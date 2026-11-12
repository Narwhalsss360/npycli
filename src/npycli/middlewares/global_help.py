from collections.abc import Sequence

from npycli.errors import MiddlewareError
from npycli.middleware import (
    CommandExecutionInfoMiddlewareHandler,
    CommandExecutionInfoMiddlewareResult,
    MiddlewareContext,
)
from npycli.parameters import CommandParameter, ParameterKind

from ..abc.cli import CLI
from ..abc.command import Command


def create_global_help_flag_command_execution_info(
    help_command: str | Command = "help",
    global_help_flag: str = "help",
    help_command_max_positionals: int = 2,  # Assuming command name and parameter name
    allow_flag_obfuscation: bool = False,
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

        if isinstance(context.previous_result, CommandExecutionInfoMiddlewareResult):
            command = context.previous_result.command
            arg_entries = context.previous_result.arg_entries
        else:
            if len(entries) == 0:
                return CommandExecutionInfoMiddlewareResult(None, entries)

            command = context.cli.get_command(entries[0])
            arg_entries = entries[1:]

        if command is None:
            return CommandExecutionInfoMiddlewareResult(None, arg_entries)

        if (
            not allow_flag_obfuscation
            and (
                matching_parameter := next(
                    filter(lambda p: global_help_flag in p.names, command.parameters),
                    None,
                )
            )
            is not None
            and len(matching_parameter.names) == 1
            and matching_parameter.kind is ParameterKind.KEYWORD_ONLY
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
        help_command_boolean_prefixed_flags_names: tuple[str, ...] = tuple(
            f"{context.cli.kwarg_prefix}{name}"
            for parameter in help_command.parameters
            for name in parameter.names
        )

        global_help_parameter: CommandParameter = CommandParameter.build(
            global_help_flag, ParameterKind.KEYWORD_ONLY, bool, False
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

        help_command_arg_entries: list[str] = [command.name]
        no_keywords: bool = False
        for entry in arg_entries:
            if not no_keywords:
                if entry == context.cli.kwarg_prefix:
                    no_keywords = True
                    continue
                if entry.startswith(context.cli.kwarg_prefix):
                    if entry in help_command_boolean_prefixed_flags_names:
                        help_command_arg_entries.append(entry)
                    continue

            if len(help_command_arg_entries) == help_command_max_positionals:
                continue
            help_command_arg_entries.append(entry)

        help_command_positional_count: int
        if any(
            parameter.kind is ParameterKind.VAR_POSITIONAL
            for parameter in help_command.parameters
        ):
            help_command_positional_count = help_command_max_positionals
        else:
            help_command_positional_count = sum(
                1
                for parameter in help_command.parameters
                if parameter.kind
                in (ParameterKind.POSITIONAL_ONLY, ParameterKind.POSITIONAL_OR_KEYWORD)
            )

        help_command_positional_count = min(
            help_command_positional_count, help_command_max_positionals
        )
        return CommandExecutionInfoMiddlewareResult(
            help_command, help_command_arg_entries
        )

    return command_execution_info


def use_global_help_flag(
    cli: CLI,
    help_command: str | Command = "help",
    global_help_flag: str = "help",
    help_command_max_positionals: int = 2,  # Assuming command name and parameter name
    allow_flag_obfuscation: bool = False,
) -> CLI:
    cli.middlewares.wrap_command_execution_info_middleware(
        create_global_help_flag_command_execution_info(
            help_command,
            global_help_flag,
            help_command_max_positionals,
            allow_flag_obfuscation,
        )
    )

    if isinstance(help_command, Command):
        cli.add_command(help_command)
    return cli
