from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cli import CLI
    from .command import Command
    from .middleware import Middleware


class ParsingError(Exception):
    def __init__(self, what: str, *args: Any) -> None:
        self.what: str = what
        super().__init__(*args)


class MissingKeywordArgumentValueError(ParsingError):
    def __init__(self, keyword: str, *args: Any) -> None:
        self.keyword: str = keyword
        super().__init__(keyword, *args)


class TooManyArgumentsError(ParsingError):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)


class CLIError(Exception):
    def __init__(
        self, *args: Any, cli: CLI | None = None, command: Command | None = None
    ) -> None:
        super().__init__(*args)
        self.cli: CLI | None = cli
        self.command: Command | None = command


class EmptyEntriesError(CLIError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommandDoesNotExistError(CLIError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommandArgumentError(CLIError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class MiddlewareError(CLIError):
    def __init__(self, *args: Any, middleware: Middleware | None):
        super().__init__(*args)
        self.middleware: Middleware | None = middleware


def causes(exception: BaseException, include_self: bool) -> Iterator[BaseException]:
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
