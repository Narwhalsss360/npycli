from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Self, TypeGuard, override

from npycli.parameters import CommandParameter, CommandParameterParser, Parsers

from .abc import command as abccommand
from .abc.command import (
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
        return False

    def __post_init__(self) -> None:
        super(Command, self).__post_init__()
        self._sync_callback_futures()

    def exec_with(
        self,
        entries: Sequence[str],
        parsers: Parsers | CommandParameterParser | None = None,
    ) -> Any:
        return self.sync_exec_with(entries, parsers)

    def __call__(
        self,
        args: Sequence[str] | None = None,
        parsers: Parsers | CommandParameterParser | None = None,
    ) -> Any:
        return self.sync_exec_with(args or (), parsers)


def is_sync_cmd(command: abccommand.Command) -> TypeGuard[Command]:
    return isinstance(command, Command)


def require_sync_cmd(command: abccommand.Command) -> Command:
    assert is_sync_cmd(command)
    return command


__all__ = ["Command", "cmd", "cmd_hook", "is_cmd"]


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
