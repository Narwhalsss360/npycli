from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from collections.abc import Iterator

if TYPE_CHECKING:
    from .cli import CLI
    from .command import Command


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
    def __init__(self, *args: Any, cli: Optional[CLI] = None, command: Optional[Command] = None) -> None:
        super().__init__(*args)
        self.cli: Optional[CLI] = cli
        self.command: Optional[Command] = command


class EmptyEntriesError(CLIError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommandDoesNotExistError(CLIError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommandArgumentError(CLIError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


def causes(exception: BaseException, include_self: bool) -> Iterator[BaseException]:
    exc: BaseException | None = exception if include_self else exception.__cause__
    while exc is not None:
        yield exc
        exc = exc.__cause__


__all__ = [
    "ParsingError",
    "MissingKeywordArgumentValueError",
    "TooManyArgumentsError",
    "CLIError",
    "EmptyEntriesError",
    "CommandDoesNotExistError",
    "CommandArgumentError",
    "causes",
]
