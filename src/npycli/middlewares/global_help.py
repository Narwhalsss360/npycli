from collections.abc import Sequence
from typing import Annotated

from npycli.errors import MiddlewareError
from npycli.middleware import (
    CommandExecutionInfoMiddlewareHandler,
    CommandExecutionInfoMiddlewareResult,
    MiddlewareContext,
)
from npycli.parameters import Alias, CommandParameter, ParameterKind

from ..abc.cli import CLI
from ..abc.command import Command

GLOBAL_HELP_FLAG_BYPASS_CUSTOM_COMMAND_ATTRIBUTE: str = "global_help_flag_bypass"


def bypass_global_help_flag(command: Command) -> Command:
    return command.with_custom_attribute(
        GLOBAL_HELP_FLAG_BYPASS_CUSTOM_COMMAND_ATTRIBUTE, True
    )


def create_global_help_flag_command_execution_info(
    help_command: str | Command = "help",
    global_help_flag: str = "help",
    global_help_flag_aliases: tuple[str, ...] = ("h",),
    help_command_max_positionals: int = 2,  # Assuming command name and parameter name
    allow_flag_obfuscation: bool = False,
    bypass_for: tuple[Command, ...] = (),
) -> CommandExecutionInfoMiddlewareHandler:
    def command_execution_info(
        context: MiddlewareContext, entries: Sequence[str]
    ) -> CommandExecutionInfoMiddlewareResult:
        nonlocal help_command
        if isinstance(help_command, str):
            if (cmd := context.cli.get_command(help_command)) is None:
                raise MiddlewareError(
                    f"Cannot create global help flag command execution info for non existent help command named '{help_command}'"
                )
            help_command = cmd

        command: Command | None
        arg_entries: Sequence[str]

        def prefixed_names(names: Sequence[str]) -> tuple[str, ...]:
            result: list[str] = []
            for name in names:
                if len(name) == 1:
                    if context.cli.parser.char_keyword_prefix is not None:
                        result.append(f"{context.cli.parser.char_keyword_prefix}{name}")
                elif len(name) > 1:
                    result.append(f"{context.cli.parser.keyword_prefix}{name}")
            return tuple(result)

        all_global_help_names: tuple[str, ...] = (
            global_help_flag,
            *global_help_flag_aliases,
        )
        if isinstance(context.previous_result, CommandExecutionInfoMiddlewareResult):
            command = context.previous_result.command
            arg_entries = context.previous_result.arg_entries
        else:
            if len(entries) == 0:
                return CommandExecutionInfoMiddlewareResult(None, entries)

            if len(entries) == 1 and entries[0] in prefixed_names(
                all_global_help_names
            ):
                return CommandExecutionInfoMiddlewareResult(help_command, ())

            command = context.cli.get_command(entries[0])
            arg_entries = entries[1:]

        if command is None:
            return CommandExecutionInfoMiddlewareResult(None, arg_entries)

        if command in bypass_for or command.custom_attributes.get(
            GLOBAL_HELP_FLAG_BYPASS_CUSTOM_COMMAND_ATTRIBUTE, False
        ):
            return CommandExecutionInfoMiddlewareResult(command, arg_entries)

        active_help_names: set[str] = {
            name
            for name in all_global_help_names
            if len(name) > 1 or context.cli.parser.char_keyword_prefix is not None
        }
        if (
            not allow_flag_obfuscation
            and (
                next(
                    (
                        p
                        for p in command.parameters
                        if any(name in p.names for name in active_help_names)
                        and len(p.names) == 1
                        and p.kind is ParameterKind.KEYWORD_ONLY
                    ),
                    None,
                )
            )
            is not None
        ):
            raise MiddlewareError(
                f"Invalid use of {create_global_help_flag_command_execution_info}, global help flag obfuscates a target command parameter"
            )

        help_command_boolean_flags: tuple[CommandParameter, ...] = tuple(
            parameter
            for parameter in help_command.parameters
            if bool in parameter.argument_types
            and parameter.kind is ParameterKind.KEYWORD_ONLY
        )
        help_command_short_flag_chars: set[str] = {
            name
            for parameter in help_command_boolean_flags
            for name in parameter.names
            if len(name) == 1
        }
        help_command_long_prefixed_flags: set[str] = {
            f"{context.cli.parser.keyword_prefix}{name}"
            for parameter in help_command_boolean_flags
            for name in parameter.names
            if len(name) > 1
        }

        global_help_parameter: CommandParameter = CommandParameter.build(
            global_help_flag,
            ParameterKind.KEYWORD_ONLY,
            Annotated[bool, Alias(*global_help_flag_aliases)],
            False,
        )
        _, kwargs = context.cli.parser.parse(
            (
                CommandParameter.build("_", ParameterKind.VAR_POSITIONAL, str | bool),
                global_help_parameter,
                *help_command_boolean_flags,
                CommandParameter.build("_", ParameterKind.VAR_KEYWORD, str | bool),
            ),
            arg_entries,
        )

        if not kwargs.get(global_help_flag, False):
            return CommandExecutionInfoMiddlewareResult(command, arg_entries)
        kwargs.pop(global_help_flag)

        effective_max_positionals: int
        if any(
            parameter.kind is ParameterKind.VAR_POSITIONAL
            for parameter in help_command.parameters
        ):
            effective_max_positionals = help_command_max_positionals
        else:
            effective_max_positionals = min(
                help_command_max_positionals,
                sum(
                    1
                    for parameter in help_command.parameters
                    if parameter.kind
                    in (
                        ParameterKind.POSITIONAL_ONLY,
                        ParameterKind.POSITIONAL_OR_KEYWORD,
                    )
                ),
            )
        help_command_arg_entries: list[str] = [command.name]
        positinal_count: int = 1
        no_keywords: bool = False
        skip_next: bool = False
        char_prefix: str | None = context.cli.parser.char_keyword_prefix

        for entry in arg_entries:
            if skip_next:
                skip_next = False
                continue

            if not no_keywords:
                if entry == context.cli.parser.argument_separator:
                    no_keywords = True
                    continue

                if entry.startswith(context.cli.parser.keyword_prefix):
                    if entry in help_command_long_prefixed_flags:
                        help_command_arg_entries.append(entry)
                    else:
                        kw = entry[len(context.cli.parser.keyword_prefix) :]
                        target_param = next(
                            (
                                p
                                for p in command.parameters
                                if kw in p.names and len(kw) > 1
                            ),
                            None,
                        )
                        if (
                            target_param is not None
                            and bool not in target_param.argument_types
                        ):
                            skip_next = True
                    continue

                if (
                    char_prefix is not None
                    and len(entry) > 1
                    and entry.startswith(char_prefix)
                ):
                    chars = entry[1:]
                    for ch in chars:
                        if ch in help_command_short_flag_chars:
                            help_command_arg_entries.append(f"{char_prefix}{ch}")

                    last_ch = chars[-1]
                    target_param = next(
                        (p for p in command.parameters if last_ch in p.names),
                        None,
                    )
                    if (
                        target_param is not None
                        and bool not in target_param.argument_types
                    ):
                        skip_next = True
                    continue

            if positinal_count >= effective_max_positionals:
                continue
            positinal_count += 1
            help_command_arg_entries.append(entry)

        return CommandExecutionInfoMiddlewareResult(
            help_command, help_command_arg_entries
        )

    return command_execution_info


def use_global_help_flag(
    cli: CLI,
    help_command: str | Command = "help",
    global_help_flag: str = "help",
    global_help_flag_aliases: tuple[str, ...] = ("h",),
    help_command_max_positionals: int = 2,  # Assuming command name and parameter name
    allow_flag_obfuscation: bool = False,
    bypass_for: tuple[Command, ...] = (),
) -> CLI:
    cli.middlewares.wrap_command_execution_info_middleware(
        create_global_help_flag_command_execution_info(
            help_command,
            global_help_flag,
            global_help_flag_aliases,
            help_command_max_positionals,
            allow_flag_obfuscation,
            bypass_for,
        )
    )

    if isinstance(help_command, Command):
        cli.add_command(help_command)
    return cli
