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
                    help=help
                )
            )
            return function

        return decorator


__all__ = ["CLI", "ErrorHandler", "ReturnValueHandler"]
