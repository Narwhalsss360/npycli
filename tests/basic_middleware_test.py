import asyncio
import inspect
from collections.abc import Sequence
from shlex import shlex
from types import FunctionType
from typing import Any, cast

from npycli import CLI, CLIError, Command, EmptyEntriesError
from npycli.errors import MiddlewareError
from npycli.middleware import (
    CommandExecutionInfoMiddlewareHandler,
    CommandExecutionInfoMiddlewareResult,
    ExecutorMiddlewareResult,
    MiddlewareContext,
)
from npycli.parameters import CommandParameter, ParameterKind, Parsers, parse_parameters

cli = CLI("async program")


@cli.cmd("do-async-operation")
async def do_async_operation(sleeptime: float | None = None) -> str:
    sleeptime = sleeptime if sleeptime is not None else 1
    await asyncio.sleep(sleeptime)
    print("Done!")
    return f"Performed async opreation for {sleeptime} seconds"


@cli.cmd(
    name="help",
    help=(
        "<...>: Positional or Keyword\n"
        "<*...>: Variable Positional\n"
        "<**...>: Variable Keyword\n"
        "/: Positional / Keyword Only Delimiter\n"
        "<: ...>: Type\n"
        "<: = ...>: Default Value\n"
        "[...]: Boolean Flag (Keyword only, no value needed)\n"
    ),
)
def help_cmd(
    command_name: str | None = None,
    parameter_name: str | None = None,
    /,
    *,
    extended: bool = False,
) -> str:
    if extended:
        command_help, parameter_help = (
            Command.extended_command_help,
            CommandParameter.extended_parameter_help,
        )
    else:
        command_help, parameter_help = (
            Command.basic_command_help,
            CommandParameter.basic_parameter_help,
        )

    if command_name is None:
        out: str = ""
        for i, command in enumerate(cli.commands):
            out += f"{command_help(command)}"
            if i != len(cli.commands) - 1:
                out += "\n"
        return out

    if (command := cli.get_command(command_name)) is None:
        return f"{command_name} is not a command."

    if parameter_name is not None:
        if (
            parameter := next(
                filter(lambda p: parameter_name in p.names, command.parameters), None
            )
        ) is None:
            return f"'{parameter_name}' is not a parameter"
        return parameter_help(parameter)

    return command_help(command)


async def cleanup():
    await asyncio.sleep(1.2)
    return "Done!"


@cli.cmd()
async def quit() -> FunctionType:
    print("Quiting and cleaning up...")
    await cleanup()
    return quit


@cli.middlewares.register.executor(wrapping=False)
def async_task_executor(
    context: MiddlewareContext,
    command: Command,
    entries: Sequence[str],
    parsers: Parsers,
) -> ExecutorMiddlewareResult:
    if inspect.iscoroutinefunction(command.function):
        coro: Any = command.exec_with(entries, parsers)
        assert inspect.iscoroutine(coro)
        return ExecutorMiddlewareResult(
            command, asyncio.get_event_loop().create_task(coro)
        )
    else:
        return ExecutorMiddlewareResult(
            command,
            asyncio.get_event_loop().create_task(
                asyncio.to_thread(command.exec_with, entries, parsers)
            ),
        )


def async_task_executor_result(result: Any) -> asyncio.Task[Any]:
    assert isinstance(result, asyncio.Task)
    return cast(asyncio.Task[Any], result)


@cli.retvals()
def retvals(command: Command, retval: Any) -> Any:
    if isinstance(retval, asyncio.Task):
        retval = async_task_executor_result(retval)

        async def awaited() -> Any:
            return retvals(command, await retval)

        return asyncio.get_event_loop().create_task(awaited())

    print(f"{command.name} ->\n{retval}")
    return retval


@cli.middlewares.register.split()
def splitter(_: MiddlewareContext, user_input: str) -> Sequence[str]:
    lexer: shlex = shlex(user_input, posix=True)
    lexer.wordchars += "&?|"
    return list(lexer)


def create_global_help_command_execution_info_middleare(
    global_help_flag_name: str = "help",
    help_command_name: str = "help",
    help_command_max_positionals: int = 2,
) -> CommandExecutionInfoMiddlewareHandler:
    def global_help_command_execution_info(
        context: MiddlewareContext, entries: Sequence[str]
    ) -> CommandExecutionInfoMiddlewareResult:
        if isinstance(context.previous_result, CommandExecutionInfoMiddlewareResult):
            command: Command | None = context.previous_result.command
            arg_entries: Sequence[str] = context.previous_result.arg_entries
        else:
            if len(entries) == 0:
                return CommandExecutionInfoMiddlewareResult(None, entries)

            command: Command | None = context.cli.get_command(entries[0])
            arg_entries: Sequence[str] = entries[1:]

        if command is None:
            return CommandExecutionInfoMiddlewareResult(command, arg_entries)

        if (help_command := context.cli.get_command(help_command_name)) is None:
            return CommandExecutionInfoMiddlewareResult(command, arg_entries)

        if (
            (
                matching_parameter := next(
                    filter(
                        lambda p: global_help_flag_name in p.names, command.parameters
                    ),
                    None,
                )
            )
            is not None
            and len(matching_parameter.names) == 1
            and matching_parameter.kind is ParameterKind.KEYWORD_ONLY
        ):
            raise MiddlewareError(
                f"Invalid use of {global_help_command_execution_info}, global help flag obfuscates a target command parameter"
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
            global_help_flag_name, ParameterKind.KEYWORD_ONLY, bool, False
        )
        _, kwargs = parse_parameters(
            (
                CommandParameter.build("_", ParameterKind.VAR_POSITIONAL, str | bool),
                global_help_parameter,
                *help_command_boolean_flags,
                CommandParameter.build("_", ParameterKind.VAR_KEYWORD, str | bool),
            ),
            arg_entries,
            context.cli.kwarg_prefix,
            context.cli.kwarg_prefix,
            {},
        )

        if not kwargs.get(global_help_flag_name, False):
            return CommandExecutionInfoMiddlewareResult(command, arg_entries)
        kwargs.pop(global_help_flag_name)

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

    return global_help_command_execution_info


async def main() -> None:
    cli.middlewares.wrap_command_execution_info_middleware(
        create_global_help_command_execution_info_middleare()
    )
    while True:
        try:
            # Asynchronously wait for input in another thread to not block this event loop
            try:
                user_input: str = await asyncio.to_thread(
                    input, cli.prompt_entry_marker
                )
            except KeyboardInterrupt:
                break

            if (
                await async_task_executor_result(
                    cli.exec(cli.middlewares.split(user_input))
                )
            ) is quit:
                break
        except asyncio.CancelledError as cancellation:
            if cancellation.__cause__ or cancellation.__context__:
                raise
            break
        except EmptyEntriesError:  # If the user entered nothing, just continue
            pass
        except (
            CLIError
        ) as err:  # Catch errors that occur between here and execution of command
            print(f"{err.__class__.__name__}: {err.args[0]}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ...
