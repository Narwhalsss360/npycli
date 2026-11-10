from __future__ import annotations

from asyncio import to_thread
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple, Protocol, TypeGuard, cast

from .parsing import CommandParameterParser, Parsers

if TYPE_CHECKING:
    from .abc.cli import CLI
    from .abc.command import Command


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


type OptionallyAwaitable[T] = T | Awaitable[T]

type PromptMiddlewareHandler = MiddlewareHandler[[str], OptionallyAwaitable[str]]

type SplitMiddlewareHandler = MiddlewareHandler[
    [str], OptionallyAwaitable[Sequence[str]]
]

type CommandExecutionInfoMiddlewareHandler = MiddlewareHandler[
    [Sequence[str]], OptionallyAwaitable[CommandExecutionInfoMiddlewareResult]
]

type ExecutorMiddlewareHandler = MiddlewareHandler[
    [Command, Sequence[str], Parsers | CommandParameterParser],
    OptionallyAwaitable[ExecutorMiddlewareResult],
]

type ErrorMiddlewareHandler = MiddlewareHandler[
    [Command, Exception], OptionallyAwaitable[Any]
]

type ReturnValueMiddlewareHandler = MiddlewareHandler[
    [Command, Any], OptionallyAwaitable[Any]
]


async def wrap_sync[**P, T](
    function: Callable[P, OptionallyAwaitable[T]], *args: P.args, **kwargs: P.kwargs
) -> T:
    if iscoroutinefunction(function):
        return await function(*args, **kwargs)
    return cast(T, await to_thread(function, *args, **kwargs))


def is_sync_function[**P, T](
    function: Callable[P, OptionallyAwaitable[T]],
) -> TypeGuard[Callable[P, T]]:
    return not iscoroutinefunction(function)


def sync[**P, T](
    function: Callable[P, OptionallyAwaitable[T]], *args: P.args, **kwargs: P.kwargs
) -> T:
    assert is_sync_function(function)
    return function(*args, **kwargs)


@dataclass
class PromptMiddlewareHandlerInfo(HandlerInfo[[str], OptionallyAwaitable[str]]):
    pass


@dataclass
class SplitMiddlewareHandlerInfo(
    HandlerInfo[[str], OptionallyAwaitable[Sequence[str]]]
):
    pass


@dataclass
class CommandExecutionInfoHandlerInfo(
    HandlerInfo[
        [Sequence[str]], OptionallyAwaitable[CommandExecutionInfoMiddlewareResult]
    ]
):
    pass


@dataclass
class ExecutorMiddlewareHandlerInfo(
    HandlerInfo[
        ["Command", Sequence[str], Parsers | CommandParameterParser],
        OptionallyAwaitable[ExecutorMiddlewareResult],
    ]
):
    pass


@dataclass
class ErrorMiddlewareHandlerInfo(
    HandlerInfo[["Command", Exception], OptionallyAwaitable[Any]]
):
    pass


@dataclass
class ReturnValueMiddlewareHandlerInfo(
    HandlerInfo[["Command", Any], OptionallyAwaitable[Any]]
):
    pass
