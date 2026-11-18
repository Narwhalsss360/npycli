from inspect import iscoroutinefunction
from typing import Annotated, Any

from .. import command as synccommand
from ..abc.cli import CLI
from ..abc.command import Command, default_help_extractor, default_parameter_extractor
from ..asyncio import command as asynccommand
from ..errors import MiddlewareError
from ..parameters import AnnotationPreview, BypassParse, Description

COALESCE_SUB_CLI_CUSTOM_COMMAND_ATTRIBUTE: str = "coalesce-sub-cli"


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


def create_sub_cli_coalesce_command(
    cli: CLI,
    sub_cli: CLI,
    name_or_names: str | tuple[str, ...] = (),
    help: str | None = None,
    preamble: str | None = None,
    annotation_preview: str = "",
    description: str = "",
) -> Command:
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

    def sync_coalesce(
        *args: Annotated[
            BypassParse, AnnotationPreview(annotation_preview), Description(description)
        ],
    ) -> Any:
        return sub_cli.sync_exec(args)

    async def async_coalesce(
        *args: Annotated[
            BypassParse, AnnotationPreview(annotation_preview), Description(description)
        ],
    ) -> Any:
        return await sub_cli.async_exec(args)

    CommandType = asynccommand.Command if sub_cli.is_async else synccommand.Command

    if help is None:
        from .help_cmd import create_help_command

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
            help = create_help_command(sub_cli, preamble=preamble or "").function()
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
    help: str | None = None,
    preamble: str | None = None,
    annotation_preview: str = "",
    description: str = "",
) -> CLIType:
    cli.add_command(
        create_sub_cli_coalesce_command(
            cli, sub_cli, name_or_names, help, preamble, annotation_preview, description
        )
    )
    return cli


__all__ = [
    "create_sub_cli_coalesce_command",
    "get_sub_cli",
    "get_sub_clis",
    "use_sub_cli_coalesce_command",
]
