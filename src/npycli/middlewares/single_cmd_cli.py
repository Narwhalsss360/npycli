from collections.abc import Sequence

from ..abc.cli import CLI
from ..abc.command import Command
from ..errors import MiddlewareError
from ..middleware import (
    CommandExecutionInfoMiddlewareHandler,
    CommandExecutionInfoMiddlewareResult,
    MiddlewareContext,
)


def create_single_command_cli_command_execution_info(
    allow_multiple_commands: bool = False,
    single_command: str | Command | None = None,
    strip_first_entry_if_is_name: bool = True,
) -> CommandExecutionInfoMiddlewareHandler:
    def command_execution_info(
        context: MiddlewareContext, entries: Sequence[str]
    ) -> CommandExecutionInfoMiddlewareResult:
        if (
            isinstance(context.previous_result, CommandExecutionInfoMiddlewareResult)
            and context.previous_result.command is not None
        ):
            return context.previous_result

        if not allow_multiple_commands and len(context.cli.commands) != 1:
            raise MiddlewareError(
                "Invalid use of single command cli middleware, there must be only one command in the CLI.",
                cli=context.cli,
            )

        nonlocal single_command
        if isinstance(single_command, str):
            single_command = context.cli.get_command(single_command)
            if single_command is None:
                raise MiddlewareError(
                    f"The single command by the name of {single_command} does not exist."
                )
        elif isinstance(single_command, Command):
            if single_command not in context.cli.commands:
                raise MiddlewareError(
                    f"The command {single_command} is not in the CLI.", cli=context.cli
                )
        else:
            if not context.cli.commands:
                raise MiddlewareError("There are no commands in the CLI.")
            single_command = context.cli.commands[0]

        if len(entries) == 0:
            return CommandExecutionInfoMiddlewareResult(single_command, entries)

        if strip_first_entry_if_is_name and entries[0] in single_command.names:
            entries = entries[1:]

        return CommandExecutionInfoMiddlewareResult(single_command, entries)

    return command_execution_info


def use_single_command_cli[CLIType: CLI](
    cli: CLIType,
    allow_multiple_commands: bool = False,
    single_command: str | Command | None = None,
    strip_first_entry_if_is_name: bool = True,
) -> CLIType:
    cli.middlewares.wrap_command_execution_info_middleware(
        create_single_command_cli_command_execution_info(
            allow_multiple_commands, single_command, strip_first_entry_if_is_name
        )
    )
    return cli
