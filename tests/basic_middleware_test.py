import asyncio
import time
from collections.abc import Sequence
from shlex import shlex
from types import FunctionType
from typing import Any, Literal, cast

import npycli
from npycli.asyncio import CLI
from npycli.errors import CLIError, EmptyEntriesError, MiddlewareError, ParsingError
from npycli.middleware import (
    CommandExecutionInfoMiddlewareHandler,
    CommandExecutionInfoMiddlewareResult,
    MiddlewareContext,
)
from npycli.parameters import CommandParameter, ParameterKind
from npycli.parsing import create_literal_parser, parse_parameters

cli = CLI("async program")


class UserError(CLIError):
    pass


type ErrorLevel = Literal["low", "high"]
cli.parsers[ErrorLevel] = create_literal_parser(ErrorLevel)


@cli.cmd("do-async-operation")
async def do_async_operation(
    sleeptime: float | None = None, error_level: ErrorLevel = "low"
) -> str:
    sleeptime = sleeptime if sleeptime is not None else 1
    if sleeptime < 0:
        args: tuple[Any, ...] = ("Parameter sleeptime must be positive",)
        if error_level == "low":
            raise UserError(*args)
        else:
            assert error_level == "high"
            raise ValueError(*args)

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
            npycli.abc.Command.extended_command_help,
            CommandParameter.extended_parameter_help,
        )
    else:
        command_help, parameter_help = (
            npycli.abc.Command.basic_command_help,
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


@cli.middlewares.register.prompt()
async def timed_async_prompter(context: MiddlewareContext, prompt: str) -> str:
    """
    Will simply time the amount of time elapsed from prompt to input.
    """

    start_time: float = time.time()
    result = await CLI.MiddlewareManager.async_default_prompter(context, prompt)
    elapsed: float = time.time() - start_time
    print(f"TIME WAITING FOR INPUT: {elapsed=}")
    return result


@cli.middlewares.register.split()
def splitter(_: MiddlewareContext, user_input: str) -> Sequence[str]:
    """
    The lexical splitter for the CLI.
    """

    lexer: shlex = shlex(user_input, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    lexer.wordchars += "?&|"
    return list(lexer)


def create_global_help_command_execution_info_middleware(
    global_help_flag_name: str = "help",
    help_command_name: str = "help",
    help_command_max_positionals: int = 2,
) -> CommandExecutionInfoMiddlewareHandler:
    """
    Curry function that creates a command execution info middleware handler for switch execution to the help command in case of a gloval help flag
    """

    def global_help_command_execution_info(
        context: MiddlewareContext, entries: Sequence[str]
    ) -> CommandExecutionInfoMiddlewareResult:
        if isinstance(context.previous_result, CommandExecutionInfoMiddlewareResult):
            command: npycli.abc.command.Command | None = context.previous_result.command
            arg_entries: Sequence[str] = context.previous_result.arg_entries
        else:
            if len(entries) == 0:
                return CommandExecutionInfoMiddlewareResult(None, entries)

            command: npycli.abc.command.Command | None = context.cli.get_command(
                entries[0]
            )
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


def format_cli_error(cli_error: CLIError) -> str:
    return f"{type(cli_error).__name__}{f' of {cli.title}' if cli_error.cli is not None else ''}{f', executing command {cli_error.command.name}' if cli_error.command is not None else ''}: {'\n'.join(cli_error.args)}"


def format_parsing_error(parsing_error: ParsingError) -> str:
    return f"{type(parsing_error).__name__} of '{parsing_error.what}': {'\n'.join(parsing_error.args)}"


@cli.middlewares.register.error(wrapping=False)
def error_handler(
    context: MiddlewareContext, command: npycli.abc.Command, error: Exception
) -> Any:
    """
    Handles CLIErrors, if not all causes were ParsingErrors or CLIError, then just raise the exception up the frame stack.
    In the case all all CLI/Parsing errors, return None back to the callsite
    """

    if isinstance(error, (asyncio.CancelledError, KeyboardInterrupt, MiddlewareError)):
        return cli.RAISE

    if not isinstance(error, CLIError):
        return cli.RAISE

    causes: tuple[BaseException, ...] = tuple(npycli.errors.causes(error, False))
    if not all(isinstance(exc, (CLIError, ParsingError)) for exc in causes):
        return cli.RAISE
    causes = cast(tuple[CLIError | ParsingError, ...], causes)

    error.cli = error.cli or context.cli
    error.command = error.command or command
    print(f"ERROR: {format_cli_error(error)}")
    for cause in causes:
        if isinstance(cause, CLIError):
            cause.cli = cause.cli or context.cli
            print(f"  CAUSE: {format_cli_error(cause)}")
        else:
            print(f"  CAUSE: {format_parsing_error(cause)}")

    return None


@cli.middlewares.register.return_value(wrapping=False)
def return_value_handler(
    _: MiddlewareContext, command: npycli.abc.Command, return_value: Any
) -> Any:
    """
    Print return value of command that were executed successfully and return back to callsite of exec/prompt.
    """

    print(f"{command.name} ->\n  {str(return_value).replace('\n', '  \n')}")
    return return_value


async def main() -> None:
    cli.middlewares.wrap_command_execution_info_middleware(
        create_global_help_command_execution_info_middleware()
    )
    while True:
        try:
            return_value: Any = await cli.prompt()
            if return_value is quit:
                break
        except KeyboardInterrupt:  # Assumed to not be handled by middlware
            break
        except (
            asyncio.CancelledError
        ) as cancellation:  # Assumed to not be handled by middlware
            if cancellation.__cause__ or cancellation.__context__:
                raise
            break
        except EmptyEntriesError:  # Never handled by middlewares
            pass


if __name__ == "__main__":
    asyncio.run(main())
