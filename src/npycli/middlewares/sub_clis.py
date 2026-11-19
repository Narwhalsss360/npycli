from __future__ import annotations

from inspect import iscoroutinefunction
from typing import Annotated, Any, cast

from .. import command as synccommand
from ..abc.cli import CLI
from ..abc.command import Command, default_help_extractor, default_parameter_extractor
from ..asyncio import command as asynccommand
from ..errors import CLIError, MiddlewareError, causes
from ..parameters import AnnotationPreview, BypassParse, Description

COALESCE_SUB_CLI_CUSTOM_COMMAND_ATTRIBUTE: str = "coalesce-sub-cli"


class SubCLIError(CLIError):
    """An error occurred during invocation of a sub CLI."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @staticmethod
    def replaced(cli_error: CLIError) -> SubCLIError:
        sub_cli_error: SubCLIError = SubCLIError(*cli_error.args)
        sub_cli_error.__dict__.update(cli_error.__dict__)
        if hasattr(cli_error, "__notes__"):
            sub_cli_error.__notes__ = list(cli_error.__notes__)
        sub_cli_error.__cause__ = cli_error.__cause__
        sub_cli_error.__context__ = cli_error.__context__
        sub_cli_error.__suppress_context__ = cli_error.__suppress_context__
        return sub_cli_error.with_traceback(cli_error.__traceback__)


def _set_sub_cli(command: Command, sub_cli: CLI) -> None:
    command.custom_attributes[COALESCE_SUB_CLI_CUSTOM_COMMAND_ATTRIBUTE] = sub_cli


def get_sub_cli(command: Command) -> CLI | None:
    return command.custom_attributes.get(
        COALESCE_SUB_CLI_CUSTOM_COMMAND_ATTRIBUTE, None
    )


def get_sub_clis(cli: CLI) -> list[CLI]:
    return [
        sub_cli
        for command in cli.commands
        if (sub_cli := get_sub_cli(command)) is not None
    ]


class UseSubCLIHelpCommand:
    def __init__(self, command_name: str = "help") -> None:
        self.command_name: str = command_name


def create_sub_cli_coalesce_command(
    cli: CLI,
    sub_cli: CLI,
    name_or_names: str | tuple[str, ...] = (),
    help: str | None = None,
    preamble: str | None = None,
    annotation_preview: str = "",
    description: str = "",
    coalesce_cli_error_args: bool = False,
) -> Command:
    """Create a Command that proxies exection to another CLI."""

    max_annotation_preview_length: int = 80

    if not annotation_preview:
        annotation_preview = " ".join(command.name for command in sub_cli.commands)
        if len(annotation_preview) > max_annotation_preview_length:
            annotation_preview = (
                f"{annotation_preview[: max_annotation_preview_length - 3]}..."
            )

    if not description:
        description = f"Invoke the sub-cli {sub_cli.title}."

    if not cli.is_async and sub_cli.is_async:
        raise MiddlewareError(
            f"A synchronous CLI ({cli.title}) cannot wrap an asynchronous CLI ({sub_cli.title})",
            cli=cli,
        )
    name_or_names = (
        name_or_names if isinstance(name_or_names, tuple) else (name_or_names,)
    ) or (sub_cli.title,)

    def fill_cli_error_for_sub_cli(args: tuple[str, ...], cli_error: CLIError) -> None:
        base_cli_error: CLIError = cast(
            CLIError,
            next(
                filter(
                    lambda exc: isinstance(exc, CLIError),
                    reversed(list(causes(cli_error, True))),
                )
            ),
        )
        cli_error.cli = cli_error.cli or sub_cli
        cli_error.args = (
            f"Invoking sub-cli {sub_cli.title}, the following error occured{f' in {base_cli_error.cli.title}' if base_cli_error.cli is not None else ''}: {base_cli_error.args[0]}",
            *(cli_error.args if coalesce_cli_error_args else ()),
        )

    def sync_coalesce(
        *args: Annotated[
            BypassParse, AnnotationPreview(annotation_preview), Description(description)
        ],
    ) -> Any:
        _ = (annotation_preview, description)
        try:
            return sub_cli.sync_exec(args)
        except CLIError as cli_error:
            if type(cli_error) is CLIError:
                replaced = SubCLIError.replaced(cli_error)
                raise replaced from None
            else:
                fill_cli_error_for_sub_cli(args, cli_error=cli_error)
                raise SubCLIError(
                    f"The following type of error occurred in the sub-cli: {type(cli_error).__name__}: {cli_error.args[0] if cli_error.args else '...'}"
                ) from cli_error

    async def async_coalesce(
        *args: Annotated[
            BypassParse, AnnotationPreview(annotation_preview), Description(description)
        ],
    ) -> Any:
        _ = (annotation_preview, description)
        try:
            return await sub_cli.async_exec(args)
        except CLIError as cli_error:
            if type(cli_error) is CLIError:
                replaced = SubCLIError.replaced(cli_error)
                raise replaced from None
            else:
                fill_cli_error_for_sub_cli(args, cli_error=cli_error)
                raise SubCLIError(
                    f"The following type of error occurred in the sub-cli: {type(cli_error).__name__}: {cli_error.args[0] if cli_error.args else '...'}"
                ) from cli_error

    sync_coalesce.__annotations__["args"] = Annotated[
        BypassParse, AnnotationPreview(annotation_preview), Description(description)
    ]
    async_coalesce.__annotations__["args"] = Annotated[
        BypassParse, AnnotationPreview(annotation_preview), Description(description)
    ]

    CommandType = asynccommand.Command if sub_cli.is_async else synccommand.Command

    if isinstance(help, UseSubCLIHelpCommand):
        if (
            (help_command := sub_cli.get_command("help")) is not None
            and not iscoroutinefunction(help_command.function)
            and all(
                parameter.default is not parameter.empty
                for parameter in help_command.parameters
            )
            and (inner_help_result := help_command.function()) is not None
        ):
            help = str(inner_help_result)
        else:
            raise MiddlewareError(
                f"The help function {help.command_name} is not invokable.",
                cli=cli,
                command=help_command,
            )
    elif help is None:
        from .help_cmd import create_help_command

        help = str(create_help_command(sub_cli, preamble=preamble or "").function())
    else:
        if preamble is not None:
            raise MiddlewareError(
                "The preamble is to be used only when help is None to auto-generate help."
            )

    command: Command = CommandType.create(
        async_coalesce if sub_cli.is_async else sync_coalesce,
        names=name_or_names,
        help=help,
        parameter_extractor=default_parameter_extractor,
        help_extractor=default_help_extractor,
        parser=cli.parser,
    )
    _set_sub_cli(command, sub_cli)

    from .global_help import bypass_global_help_flag

    bypass_global_help_flag(command)
    return command


def use_sub_cli_coalesce_command[CLIType: CLI](
    cli: CLIType,
    sub_cli: CLI,
    name_or_names: str | tuple[str, ...] = (),
    help: str | UseSubCLIHelpCommand | None = None,
    preamble: str | None = None,
    annotation_preview: str = "",
    description: str = "",
    coalesce_cli_error_args: bool = False,
) -> CLIType:
    cli.add_command(
        create_sub_cli_coalesce_command(
            cli,
            sub_cli,
            name_or_names,
            help,
            preamble,
            annotation_preview,
            description,
            coalesce_cli_error_args,
        )
    )
    return cli


__all__ = [
    "create_sub_cli_coalesce_command",
    "get_sub_cli",
    "get_sub_clis",
    "use_sub_cli_coalesce_command",
]
