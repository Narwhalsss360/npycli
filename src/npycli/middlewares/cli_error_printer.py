import asyncio
from collections.abc import Callable
from io import StringIO
from sys import stderr
from typing import Any, TextIO, cast

import npycli
from npycli.abc import CLI, Command
from npycli.ansi.const.sgr import (
    DEFAULT_RENDITION,
    RED_DISPLAY,
    SLOWLY_BLINKING,
    YELLOW_DISPLAY,
)
from npycli.ansi.sequence_types import ControlSequence
from npycli.ansi.sequences import SGR
from npycli.errors import CLIError, MiddlewareError, ParsingError
from npycli.middleware import ErrorMiddlewareHandler, MiddlewareContext


def default_format_cli_error(cli: CLI, cli_error: CLIError, ansi: bool) -> str:
    return f"{type(cli_error).__name__}{f' of {cli.title}' if cli_error.cli is not None else ''}{f', executing command {cli_error.command.name}' if cli_error.command is not None else ''}: {'\n'.join(cli_error.args)}"


def default_format_parsing_error(
    cli: CLI, parsing_error: ParsingError, ansi: bool
) -> str:
    return f"{type(parsing_error).__name__} of '{parsing_error.what}': {'\n'.join(parsing_error.args)}"


def default_cli_error_return_value(
    context: MiddlewareContext, command: Command, error: CLIError
) -> Any:
    return None


def full_cli_error_string(
    cli: CLI,
    error: CLIError,
    causes: tuple[CLIError | ParsingError, ...],
    indent_str: str = "  ",
    error_prefix: str = "ERROR: ",
    cause_prefix: str = "CAUSE: ",
    format_cli_error: Callable[[CLI, CLIError, bool], str] = default_format_cli_error,
    format_parsing_error: Callable[
        [CLI, ParsingError, bool], str
    ] = default_format_parsing_error,
    ansi: bool = True,
) -> str:
    if ansi:

        def ansi_guard(sequence: ControlSequence) -> str:
            return str(sequence)
    else:

        def ansi_guard(sequence: ControlSequence) -> str:
            return ""

    text: StringIO = StringIO()

    print(
        f"{SGR(DEFAULT_RENDITION)}{ansi_guard(SGR(RED_DISPLAY, SLOWLY_BLINKING))}{error_prefix}{ansi_guard(SGR(DEFAULT_RENDITION))}{format_cli_error(cli, error, ansi)}",
        file=text,
    )
    for cause in causes:
        if isinstance(cause, CLIError):
            cause.cli = cause.cli or cli
            print(
                f"{indent_str}{ansi_guard(SGR(YELLOW_DISPLAY, SLOWLY_BLINKING))}{cause_prefix}{ansi_guard(SGR(DEFAULT_RENDITION))}{format_cli_error(cli, cause, ansi)}",
                file=text,
            )
        else:
            print(
                f"{indent_str}{ansi_guard(SGR(YELLOW_DISPLAY, SLOWLY_BLINKING))}{cause_prefix}{ansi_guard(SGR(DEFAULT_RENDITION))}{format_parsing_error(cli, cause, ansi)}",
                file=text,
            )

    return text.getvalue().rstrip("\n")


def create_cli_error_printer(
    file: TextIO = stderr,
    error_prefix: str = "ERROR: ",
    cause_prefix: str = "CAUSE: ",
    indent_str: str = "  ",
    ansi: bool = True,
    format_cli_error: Callable[[CLI, CLIError, bool], str] = default_format_cli_error,
    format_parsing_error: Callable[
        [CLI, ParsingError, bool], str
    ] = default_format_parsing_error,
    cli_error_return_value: Callable[
        [MiddlewareContext, Command, CLIError], Any
    ] = default_cli_error_return_value,
) -> ErrorMiddlewareHandler:
    def cli_error_printer_error_handler(
        context: MiddlewareContext, command: npycli.abc.Command, error: Exception
    ) -> Any:
        """
        Handles CLIErrors, if not all causes were ParsingErrors or CLIError, then just raise the exception up the frame stack.
        In the case all all CLI/Parsing errors, return None back to the callsite
        """

        if context.previous_result is not context.DNE:
            return context.previous_result

        if isinstance(
            error, (asyncio.CancelledError, KeyboardInterrupt, MiddlewareError)
        ):
            return context.cli.RAISE

        if not isinstance(error, CLIError):
            return context.cli.RAISE

        causes: tuple[BaseException, ...] = tuple(npycli.errors.causes(error, False))
        if not all(isinstance(exc, (CLIError, ParsingError)) for exc in causes):
            return context.cli.RAISE
        causes = cast(tuple[CLIError | ParsingError, ...], causes)

        error.cli = error.cli or context.cli
        error.command = error.command or command
        print(
            full_cli_error_string(
                cli=error.cli or context.cli,
                error=error,
                causes=causes,
                indent_str=indent_str,
                error_prefix=error_prefix,
                cause_prefix=cause_prefix,
                format_cli_error=format_cli_error,
                format_parsing_error=format_parsing_error,
                ansi=ansi,
            ),
            file=file,
        )
        return cli_error_return_value(context, command, error)

    return cli_error_printer_error_handler


def use_cli_error_printer(
    cli: CLI,
    file: TextIO = stderr,
    error_prefix: str = "ERROR: ",
    cause_prefix: str = "CAUSE: ",
    indent_str: str = "  ",
    ansi: bool = True,
    format_cli_error: Callable[[CLI, CLIError, bool], str] = default_format_cli_error,
    format_parsing_error: Callable[
        [CLI, ParsingError, bool], str
    ] = default_format_parsing_error,
    cli_error_return_value: Callable[
        [MiddlewareContext, Command, CLIError], Any
    ] = default_cli_error_return_value,
) -> CLI:
    cli.middlewares.wrap_error_middleware(
        create_cli_error_printer(
            file,
            error_prefix,
            cause_prefix,
            indent_str,
            ansi,
            format_cli_error,
            format_parsing_error,
            cli_error_return_value,
        )
    )
    return cli
