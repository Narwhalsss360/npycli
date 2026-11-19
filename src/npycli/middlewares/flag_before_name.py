from collections.abc import Sequence

from ..abc.cli import CLI
from ..abc.command import Command
from ..middleware import CommandExecutionInfoMiddlewareResult, MiddlewareContext


def flag_before_name_command_execution_info(
    context: MiddlewareContext, entries: Sequence[str]
) -> CommandExecutionInfoMiddlewareResult:
    if (
        isinstance(context.previous_result, CommandExecutionInfoMiddlewareResult)
        and context.previous_result.command is not None
    ):
        return context.previous_result

    if len(entries) == 0:
        return CommandExecutionInfoMiddlewareResult(None, ())

    command: Command | None = context.cli.get_command(entries[0])
    name_index: int = 0
    had_argument_separator: bool = False
    for i, entry in enumerate(entries):
        if (
            not had_argument_separator
            and entry == context.cli.parser.argument_separator
        ):
            had_argument_separator = True
            continue

        if had_argument_separator:
            name_index: int = i
            command = context.cli.get_command(entry)
            break

        if (command := context.cli.get_command(entry)) is not None:
            name_index = i
            break

        if entry.startswith(context.cli.parser.keyword_prefix):
            continue

        if context.cli.parser.char_keyword_prefix is not None and entry.startswith(
            context.cli.parser.char_keyword_prefix
        ):
            continue

    if command is None:
        return CommandExecutionInfoMiddlewareResult(None, entries)

    return CommandExecutionInfoMiddlewareResult(
        command, (*entries[:name_index], *entries[name_index + 1 :])
    )


def use_flag_before_name_command_execution_info[CLIType: CLI](cli: CLIType) -> CLIType:
    cli.middlewares.wrap_command_execution_info_middleware(
        flag_before_name_command_execution_info
    )
    return cli
