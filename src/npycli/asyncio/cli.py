from __future__ import annotations

from asyncio import gather
from collections.abc import Callable, Generator, Sequence
from typing import Any, override

from ..abc import cli as abccli
from ..abc.cli import ErrorHandler, ReturnValueHandler
from .command import Command


class CLI(abccli.CLI):
    @property
    @override
    def is_async(self) -> bool:
        return True

    def cmd[**P, R](
        self,
        name: str | None = None,
        names: tuple[str, ...] | None = None,
        help: str | None = None,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(function: Callable[P, R]) -> Callable[P, R]:
            self.add_command(
                Command.create(
                    function=function,
                    name=name,
                    names=names,
                    help=help,
                    kwarg_prefix=self.kwarg_prefix,
                )
            )
            return function

        return decorator

    async def exec(self, entries: Sequence[str]) -> Any:
        return await self.async_exec(entries)

    async def prompt(self) -> Any:
        return await self.async_prompt()

    @override
    def __await__(self) -> Generator[Any, None, CLI]:
        if self.has_invoked_callbacks:

            def completed() -> Generator[Any, None, CLI]:
                if False:
                    yield
                return self

            return completed()

        async def wrapper() -> CLI:
            await gather(*(cmd for cmd in self._commands if isinstance(cmd, Command)))
            return self

        return wrapper().__await__()


__all__ = ["CLI", "ErrorHandler", "ReturnValueHandler"]
