from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .cli import CLI, Command
from .parameters import CommandParameterType


@dataclass(frozen=True)
class CommandAddedResult:
    middleware: Middleware
    inhibit: bool = field(default=False)


@dataclass(frozen=True)
class ReturnValueResult:
    middleware: Middleware


@dataclass(frozen=True)
class ErrorResult:
    middleware: Middleware


@dataclass(frozen=True)
class PrompterResult:
    middleware: Middleware
    prompter: Callable[[str], str] | None = field(default=None)


@dataclass(frozen=True)
class ExecutorResult:
    middleware: Middleware
    executor: (
        Callable[
            [
                Command,
                list[str],
                dict[CommandParameterType, Callable[[str], Any]] | None,
            ],
            tuple[Command, Any],
        ]
        | None
    ) = field(default=None)


class Middleware(ABC):
    def __init__(self, cli: CLI) -> None:
        self._cli: CLI | None = cli

    @classmethod
    @abstractmethod
    def on_use(cls, cli: CLI) -> Middleware:
        pass

    def _unuse(self) -> None:
        if self._cli is not None:
            self._cli._middlewares.remove(self)  # pyright: ignore[reportPrivateUsage]

    @property
    def cli(self) -> CLI:
        if self._cli is None:
            raise ValueError("This middleware is no longer in use.")
        return self._cli

    @property
    def default_command_added_result(self) -> CommandAddedResult:
        return CommandAddedResult(middleware=self)

    def command_added(
        self,
        commad: Command,
        last_result: CommandAddedResult | None = None,
        last_flagged_result: CommandAddedResult | None = None,
    ) -> CommandAddedResult:
        return self.default_command_added_result

    @property
    def default_return_value_result(self) -> ReturnValueResult:
        return ReturnValueResult(self)

    def return_value(
        self,
        command: Command,
        return_value: Any,
        last_result: ReturnValueResult | None = None,
    ) -> ReturnValueResult:
        return self.default_return_value_result

    @property
    def default_error_result(self) -> ErrorResult:
        return ErrorResult(self)

    def error(
        self, command: Command, exc: Exception, last_result: ErrorResult | None = None
    ) -> ErrorResult:
        return self.default_error_result

    @property
    def default_prompter_result(self) -> PrompterResult:
        return PrompterResult(self)

    def prompter(
        self, last_flagged_result: PrompterResult | None = None
    ) -> PrompterResult:
        return self.default_prompter_result

    @property
    def default_executor_result(self) -> ExecutorResult:
        return ExecutorResult(self)

    def executor(
        self, command: Command, last_flagged_result: ExecutorResult | None = None
    ) -> ExecutorResult:
        return self.default_executor_result


__all__ = ["CommandAddedResult", "ErrorResult", "Middleware", "ReturnValueResult"]
