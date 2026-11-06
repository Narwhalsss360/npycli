from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple, Protocol

from .command import Command
from .parameters import Parsers

if TYPE_CHECKING:
    from .cli import CLI


@dataclass(frozen=True)
class MiddlewareContext:
    class DoesNotExistSentinelType:
        __slots__ = ()

        def __repr__(self) -> str:
            return "<Does Not Exist Sentinel>"

        def __setattr__(self, name: str, value: Any):
            raise AttributeError("This sentinel instance is immutable.")

        def __delattr__(self, name: str):
            raise AttributeError("This sentinel instances is immutable.")

        def __copy__(self):
            return self

        def __deepcopy__(self, memo: Any):
            return self

    DNE: ClassVar[DoesNotExistSentinelType] = DoesNotExistSentinelType()

    cli: CLI
    base_result: Any = field(default=DNE)
    previous_result: Any = field(default=DNE)


class MiddlewareHandler[**P, R](Protocol):
    def __call__(
        self, context: MiddlewareContext, /, *args: P.args, **kwargs: P.kwargs
    ) -> R: ...


class CommandExecutionInfoMiddlewareResult(NamedTuple):
    command: Command | None
    arg_entries: Sequence[str]


class ExecutorMiddlewareResult(NamedTuple):
    command_executed: Command
    return_value: Any


@dataclass
class HandlerInfo[**P, R]:
    handler: MiddlewareHandler[P, R]
    context: MiddlewareContext


type PromptMiddlewareHandler = MiddlewareHandler[[str], str]

type SplitMiddlewareHandler = MiddlewareHandler[[str], Sequence[str]]

type CommandExecutionInfoMiddlewareHandler = MiddlewareHandler[
    [Sequence[str]], CommandExecutionInfoMiddlewareResult
]

type ExecutorMiddlewareHandler = MiddlewareHandler[
    [Command, Sequence[str], Parsers], ExecutorMiddlewareResult
]

type ErrorMiddlewareHandler = MiddlewareHandler[[Command, Exception], Any]

type ReturnValueMiddlewareHandler = MiddlewareHandler[[Command, Any], Any]


@dataclass
class PromptMiddlewareHandlerInfo(HandlerInfo[[str], str]):
    pass


@dataclass
class SplitMiddlewareHandlerInfo(HandlerInfo[[str], Sequence[str]]):
    pass


@dataclass
class CommandForMiddlewareHandlerInfo(
    HandlerInfo[[Sequence[str]], CommandExecutionInfoMiddlewareResult]
):
    pass


@dataclass
class ExecutorMiddlewareHandlerInfo(
    HandlerInfo[[Command, Sequence[str], Parsers], ExecutorMiddlewareResult]
):
    pass


@dataclass
class ErrorMiddlewareHandlerInfo(HandlerInfo[[Command, Exception], Any]):
    pass


@dataclass
class ReturnValueMiddlewareHandlerInfo(HandlerInfo[[Command, Any], Any]):
    pass
