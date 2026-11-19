from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .abc.cli import CLI
    from .abc.command import Command


class ParsingError(Exception):
    """Whether an error occurred during CommandParameter parsing."""

    def __init__(
        self, what: str, *args: Any, last_exception: Exception | None = None
    ) -> None:
        self.what: str = what
        self.last_exception: Exception | None = last_exception
        super().__init__(*args)


class MissingKeywordArgumentValueError(ParsingError):
    """Whether a keyword argument key was specified with no value during CommandParameter parsing."""

    def __init__(self, keyword: str, *args: Any) -> None:
        self.keyword: str = keyword
        super().__init__(keyword, *args)


class TooManyArgumentsError(ParsingError):
    """Whether more arguments than possible were entered during CommandParameter parsing."""

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)


class CLIError(Exception):
    """An error that has occurred in the attempt to execute a Command of a CLI."""

    def __init__(
        self, *args: Any, cli: CLI | None = None, command: Command | None = None
    ) -> None:
        super().__init__(*args)
        self.cli: CLI | None = cli
        self.command: Command | None = command


class EmptyEntriesError(CLIError):
    """Nothing was entered into the CLI."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommandDoesNotExistError(CLIError):
    """A command could not be found attempting a CLI execution."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommandArgumentError(CLIError):
    """An error occurred relating to the argument of a Command."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class MiddlewareError(CLIError):
    """An error occurred during execution of a MiddlewareHandler."""

    def __init__(
        self, *args: Any, cli: CLI | None = None, command: Command | None = None
    ) -> None:
        super().__init__(*args, cli=cli, command=command)


def causes(exception: BaseException, include_self: bool) -> Iterator[BaseException]:
    """Get all causes of an exception."""

    exc: BaseException | None = exception if include_self else exception.__cause__
    while exc is not None:
        yield exc
        exc = exc.__cause__


__all__ = [
    "CLIError",
    "CommandArgumentError",
    "CommandDoesNotExistError",
    "EmptyEntriesError",
    "MiddlewareError",
    "MissingKeywordArgumentValueError",
    "ParsingError",
    "TooManyArgumentsError",
    "causes",
]
