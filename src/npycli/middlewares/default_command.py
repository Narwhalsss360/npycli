from collections.abc import Sequence

from npycli.errors import MiddlewareError

from ..abc import CLI, Command
from ..middleware import (
    CommandExecutionInfoMiddlewareHandler,
    CommandExecutionInfoMiddlewareResult,
    MiddlewareContext,
)


def create_default_on_empty_command_execution_info(
    default_command: str | Command = "help", default_args: Sequence[str] = ()
) -> CommandExecutionInfoMiddlewareHandler:
    def command_execution_info(
        context: MiddlewareContext, entries: Sequence[str]
    ) -> CommandExecutionInfoMiddlewareResult:
        nonlocal default_command

        if (
            isinstance(context.previous_result, CommandExecutionInfoMiddlewareResult)
            and context.previous_result.command is not None
        ):
            return context.previous_result

        if len(entries) != 0:
            return CLI.MiddlewareManager.sync_default_command_execution_info(
                context, entries
            )

        if not isinstance(default_command, Command):
            if (command := context.cli.get_command(default_command)) is None:
                raise MiddlewareError(
                    f"Could not find command '{default_command}' for the default command.",
                    cli=context.cli,
                )
            default_command = command
        return CommandExecutionInfoMiddlewareResult(default_command, default_args)

    return command_execution_info


def use_default_on_empty_command_execution_info[CLIType: CLI](
    cli: CLIType, default_command: str | Command, default_args: Sequence[str] = ()
) -> CLIType:
    cli.middlewares.wrap_command_execution_info_middleware(
        create_default_on_empty_command_execution_info(default_command, default_args)
    )
    return cli
