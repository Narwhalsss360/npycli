from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import gather, to_thread
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from inspect import getdoc, iscoroutinefunction, signature
from typing import Any, ClassVar, Self, get_type_hints
from weakref import ReferenceType, WeakKeyDictionary, ref

from npycli.errors import CommandArgumentError, ParsingError
from npycli.middleware import wrap_sync
from npycli.parameters import (
    CommandParameter,
    ParameterKind,
    Parsers,
    parse_parameters,
)

type ParameterExtractor = Callable[[Callable[..., Any]], tuple[CommandParameter, ...]]


def default_parameter_extractor(
    function: Callable[..., Any],
) -> tuple[CommandParameter, ...]:
    annotations: dict[str, Any] = get_type_hints(function, include_extras=True)
    return tuple(
        CommandParameter.build(
            parameter.name,
            parameter.kind,
            annotations.get(parameter.name, str),
            default=parameter.default,
        )
        for parameter in signature(function).parameters.values()
    )


type HelpExtractor = Callable[
    [str | None, Callable[..., Any], tuple[CommandParameter, ...]], str
]


def default_help_extractor(
    existing: str | None,
    function: Callable[..., Any],
    parameters: tuple[CommandParameter, ...],
) -> str:
    if existing is not None:
        return existing
    if (doc := getdoc(function)) is not None:
        return doc
    return function.__name__


class CommandAttributes:
    def __init__(self) -> None:
        self._details: list[str] = []
        self._has_invoked_callbacks: bool = False

    def add_detail(self, detail: str) -> Self:
        self._details.append(detail)
        return self

    @property
    def details(self) -> list[str]:
        return self._details

    @property
    def has_invoked_callbacks(self) -> bool:
        return self._has_invoked_callbacks

    @has_invoked_callbacks.setter
    def has_invoked_callbacks(self, value: bool) -> None:
        if self._has_invoked_callbacks and not value:
            raise ValueError("Cannot uninitialize.")
        self._has_invoked_callbacks = value


@dataclass
class CommandFunctionBindings:
    __BINDINGS_ATTR__: ClassVar[str] = "__cmd__"

    commands: list[ReferenceType[Command]] = field(
        default_factory=list[ReferenceType["Command"]]
    )
    hooks: list[Callable[[Command], None]] = field(
        default_factory=list[Callable[["Command"], None]]
    )

    def updated(self) -> Self:
        for collected in (cmd for cmd in self.commands if cmd() is None):
            self.commands.remove(collected)
        return self

    @staticmethod
    def get(function: Callable[..., Any]) -> CommandFunctionBindings | None:
        if not hasattr(function, CommandFunctionBindings.__BINDINGS_ATTR__):
            object.__setattr__(
                function,
                CommandFunctionBindings.__BINDINGS_ATTR__,
                CommandFunctionBindings(),
            )
            if not hasattr(function, CommandFunctionBindings.__BINDINGS_ATTR__):
                return None

        bindings = getattr(function, CommandFunctionBindings.__BINDINGS_ATTR__)
        assert isinstance(bindings, CommandFunctionBindings)
        return bindings.updated()


@dataclass(frozen=True)
class Command(ABC):
    __mutable_attributes__: ClassVar[WeakKeyDictionary[Command, CommandAttributes]] = (
        WeakKeyDictionary()
    )

    function: Callable[..., Any]
    parameters: tuple[CommandParameter, ...]
    names: tuple[str, ...]
    help: str | None = field(default=None)
    kwarg_prefix: str = field(default_factory=lambda: "--")

    @classmethod
    @abstractmethod
    def create(
        cls: type[Self],
        function: Callable[..., Any],
        name: str | None = None,
        names: tuple[str, ...] | None = None,
        help: str | None = None,
        kwarg_prefix: str | None = None,
        parameter_extractor: ParameterExtractor = default_parameter_extractor,
        help_extractor: HelpExtractor = default_help_extractor,
    ) -> Self:
        pass

    @property
    @abstractmethod
    def is_async(self) -> bool: ...

    @property
    def name(self) -> str:
        """
        Primary name of this `Command`
        :return: Name
        """

        return self.names[0]

    @property
    def aliases(self) -> tuple[str, ...]:
        """
        Aliases of this `Command`
        :return: Aliases
        """

        return self.names[1:]

    @property
    def details(self) -> str:
        """
        Details of this command, which include but are not limited to:
        * Name
        * Aliases
        * Arguments
        * Help string
        :return: Details
        """

        return self.basic_command_help()

    @property
    def has_invoked_callbacks(self) -> bool:
        return Command.__mutable_attributes__[self].has_invoked_callbacks

    def add_detail(self, detail: str) -> Self:
        """
        Add details to this `Command`
        :param detail: Specific detail
        :return: `None`
        """

        Command.__mutable_attributes__[self].add_detail(detail)
        return self

    def find_parameter(self, parameter_name: str) -> CommandParameter | None:
        return next(filter(lambda p: parameter_name in p.names, self.parameters), None)

    def sync_exec_with(
        self,
        entries: Sequence[str],
        parsers: Parsers | None = None,
    ) -> Any:
        """
        Execute this `Command` with specified arguments and parsers
        :param args: Arguments
        :param parsers: Custom parsers to parse arguments with.
        :return:
        """

        try:
            args, kwargs = parse_parameters(
                self.parameters,
                entries,
                self.kwarg_prefix,
                self.kwarg_prefix,
                parsers or {},
            )
            return self.function(*args, **kwargs)
        except TypeError as type_error:
            if self._is_argument_error(type_error):
                raise CommandArgumentError(
                    *type_error.args, command=self
                ) from type_error
            raise
        except ParsingError as parsing_error:
            raise CommandArgumentError(
                *parsing_error.args, command=self
            ) from parsing_error

    async def async_exec_with(
        self, entries: Sequence[str], parsers: Parsers | None = None
    ) -> Any:
        try:
            args, kwargs = parse_parameters(
                self.parameters,
                entries,
                self.kwarg_prefix,
                self.kwarg_prefix,
                parsers or {},
            )
            if iscoroutinefunction(self.function):
                return await self.function(*args, **kwargs)
            else:
                return await to_thread(self.function, *args, **kwargs)
        except TypeError as type_error:
            if self._is_argument_error(type_error):
                raise CommandArgumentError(
                    *type_error.args, command=self
                ) from type_error
            raise
        except ParsingError as parsing_error:
            raise CommandArgumentError(
                *parsing_error.args, command=self
            ) from parsing_error

    def _validate_data(self) -> None:
        if not callable(self.function):
            raise TypeError(
                f"{Command._validate_data} -> {self.function} is not callable."
            )
        if not isinstance(self.names, tuple) or not all(  # pyright: ignore[reportUnnecessaryIsInstance]
            isinstance(name, str)  # pyright: ignore[reportUnnecessaryIsInstance]
            for name in self.names
        ):
            raise TypeError(f"{Command} names must be a {tuple} of {str}.")
        if not self.names:
            raise ValueError(f"{Command} names must not be empty.")
        for name in self.names:
            for c in name:
                if c.isspace():
                    raise ValueError(
                        f"Name for {self.function} cannot contain whitespace: {name}"
                    )
        if self.help is not None and not isinstance(self.help, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"{Command} help must be a {str}.")

    def _attach_self(self) -> None:
        if (binding := CommandFunctionBindings.get(self.function)) is None:
            return
        binding.commands.append(ref(self))

    def _sync_callback_futures(self) -> None:
        if (binding := CommandFunctionBindings.get(self.function)) is None:
            return
        for callback in binding.hooks:
            callback(self)
        Command.__mutable_attributes__[self].has_invoked_callbacks = True

    async def _async_callback_futures(self) -> None:
        if (binding := CommandFunctionBindings.get(self.function)) is None:
            return
        await gather(*(wrap_sync(callback, self) for callback in binding.hooks))
        Command.__mutable_attributes__[self].has_invoked_callbacks = True

    def __post_init__(self) -> None:
        Command.__mutable_attributes__[self] = CommandAttributes()
        Command.__mutable_attributes__[self].has_invoked_callbacks = False
        self._validate_data()
        self._attach_self()

    def _is_argument_error(self, type_error: TypeError) -> bool:
        return type_error.args[0].startswith(f"{self.function.__name__}(")

    def basic_command_help(self) -> str:
        out: str = f"{self.name} "
        last_positional_only_index: int = -1
        for i, parameter in enumerate(self.parameters):
            if parameter.kind == ParameterKind.POSITIONAL_ONLY:
                last_positional_only_index = i
            else:
                break

        for i, parameter in enumerate(self.parameters):
            out += parameter.basic_parameter_help()
            if i == last_positional_only_index:
                out += " /"
            if i != len(self.parameters) - 1:
                out += " "
        return out

    def extended_command_help(self) -> str:
        out: str = ""
        for i, name in enumerate(self.names):
            out += name
            if i != len(self.names) - 1:
                out += " "
        out += "\n"

        if self.parameters:
            out += "Parameters:\n"
        for i, parameter in enumerate(self.parameters):
            out += parameter.extended_parameter_help()
            if i != len(self.parameters) - 1:
                out += "\n"

        if self.help:
            out += f"\nDesciption: {self.help}"

        for detail in Command.__mutable_attributes__[self].details:
            out += f"\n->{detail}"

        return out

    def __str__(self) -> str:
        return self.details


def is_cmd(function: Callable[..., Any]) -> bool:
    if (binding := CommandFunctionBindings.get(function)) is None:
        return False
    return len(binding.commands) > 0


def cmd(function: Callable[..., Any]) -> Command:
    if (
        binding := CommandFunctionBindings.get(function)
    ) is None or not binding.commands:
        raise ValueError(f"{function} is not a command. Use {is_cmd}.")
    command = binding.commands[-1]()
    assert command is not None, (
        "CommandFunctionBindings.get(...) should ensure all references are valid"
    )
    return command


def cmds(function: Callable[..., Any]) -> list[Command]:
    if (binding := CommandFunctionBindings.get(function)) is None:
        return []
    return [cmd for reference in binding.commands if (cmd := reference()) is not None]


def cmd_hook(function: Callable[..., Any], callback: Callable[[Command], None]) -> bool:
    if is_cmd(function):
        raise TypeError(
            f"function {function} is already not a future command, it is already a command: {cmd(function)}"
        )
    if (binding := CommandFunctionBindings.get(function)) is None:
        return False
    binding.hooks.append(callback)
    return True


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
