from __future__ import annotations

from asyncio import Task, create_task
from collections.abc import Callable, Generator, Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Self, TypeGuard, override
from weakref import WeakKeyDictionary

from npycli.parameters import CommandParameter
from npycli.parsing import CommandParameterParser, Parsers

from ..abc import command as abccommand
from ..abc.command import (
    HelpExtractor,
    ParameterExtractor,
    cmd,
    cmd_hook,
    cmds,
    default_help_extractor,
    default_parameter_extractor,
    is_cmd,
)


@dataclass(frozen=True, slots=True, weakref_slot=True)
class Command(abccommand.Command):
    __async_initialization_tasks__: ClassVar[
        WeakKeyDictionary[Command, Task[Command] | None]
    ] = WeakKeyDictionary()

    @classmethod
    @override
    def create(
        cls: type[Self],
        function: Callable[..., Any],
        name: str | None = None,
        names: tuple[str, ...] | None = None,
        help: str | None = None,
        parameter_extractor: abccommand.ParameterExtractor = abccommand.default_parameter_extractor,
        help_extractor: abccommand.HelpExtractor = abccommand.default_help_extractor,
        kwarg_prefix: str = CommandParameterParser.DEFAULT_KEYWORD_PREFIX,
    ) -> Self:
        if names is None:
            if name:
                names = (name,)
            else:
                names = (function.__name__,)

        parameters: tuple[CommandParameter, ...] = parameter_extractor(function)
        return cls(
            function=function,
            parameters=parameters,
            names=names,
            help=help_extractor(help, function, parameters),
        ).with_kwarg_prefix(kwarg_prefix)

    @property
    @override
    def is_async(self) -> bool:
        return True

    def __post_init__(self) -> None:
        super(Command, self).__post_init__()
        Command.__async_initialization_tasks__[self] = None

    @property
    def _initialization_task(self) -> Task[Command]:
        if (task := Command.__async_initialization_tasks__[self]) is not None:
            return task

        async def initialization_task() -> Command:
            await self._async_callback_futures()
            return self

        Command.__async_initialization_tasks__[self] = create_task(
            initialization_task()
        )
        return self._initialization_task

    async def exec_with(
        self,
        entries: Sequence[str],
        parsers: Parsers | CommandParameterParser | None = None,
    ) -> Any:
        return await self.async_exec_with(entries, parsers)

    async def __call__(
        self,
        args: Sequence[str] | None = None,
        parsers: Parsers | CommandParameterParser | None = None,
    ) -> Any:
        return await self.async_exec_with(args or (), parsers)

    def __await__(self) -> Generator[Any, None, Command]:
        return self._initialization_task.__await__()


def is_async_cmd(command: abccommand.Command) -> TypeGuard[Command]:
    return isinstance(command, Command)


def require_async_cmd(command: abccommand.Command) -> Command:
    assert is_async_cmd(command)
    return command


__all__ = [
    "Command",
    "HelpExtractor",
    "ParameterExtractor",
    "cmd",
    "cmd_hook",
    "cmds",
    "default_help_extractor",
    "default_parameter_extractor",
    "is_cmd",
]
