from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, override

from .abc import cli as abccli
from .abc.cli import ErrorHandler, ReturnValueHandler
from .command import Command


class CLI(abccli.CLI):
    @property
    @override
    def is_async(self) -> bool:
        return False

    def exec(self, entries: Sequence[str]) -> Any:
        return self.sync_exec(entries)

    def prompt(self) -> Any:
        return self.sync_prompt()

    @override
    def cmd[F: Callable[..., Any]](
        self,
        name: str | None = None,
        names: tuple[str, ...] | None = None,
        help: str | None = None,
    ) -> Callable[[F], F]:
        def decorator(function: F) -> F:
            self.add_command(
                Command.create(function=function, name=name, names=names, help=help)
            )
            return function

        return decorator


__all__ = ["CLI", "ErrorHandler", "ReturnValueHandler"]
