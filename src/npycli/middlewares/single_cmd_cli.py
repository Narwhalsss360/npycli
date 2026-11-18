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
    """Create a command execution info middleware handler for CLIs which are meant to execute only a single command.
    allow_multiple_commands is an option in the case that other middlewares add extra commands, which are meant to be executed in other ways, like, a wrapped command execution info.
    In the case that multiple commands is True, and single_command is None, the defult_command is whichever is first in the list of commands of the CLI.
    """

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
    """Use the single command cli middleware."""

    cli.middlewares.wrap_command_execution_info_middleware(
        create_single_command_cli_command_execution_info(
            allow_multiple_commands, single_command, strip_first_entry_if_is_name
        )
    )
    return cli


__all__ = ["create_single_command_cli_command_execution_info", "use_single_command_cli"]
