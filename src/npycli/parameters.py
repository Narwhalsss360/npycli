from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from inspect import Parameter, _ParameterKind  # type: ignore
from types import GenericAlias, NoneType, UnionType
from typing import (
    Annotated,
    Any,
    ClassVar,
    Literal,
    Self,
    TypeAliasType,
    Union,
    get_args,
    get_origin,
)
from weakref import WeakKeyDictionary

ParameterKind = _ParameterKind


class Alias:
    def __init__(self, *aliases: str, private: bool = False) -> None:
        self.aliases: tuple[str, ...] = aliases
        self.private: bool = private

    def __repr__(self) -> str:
        return f"Alias({self.aliases})"

    def __str__(self) -> str:
        return repr(self)


class Description:
    def __init__(self, description: str) -> None:
        self.description: str = description

    def __repr__(self) -> str:
        return f"Description({self.description})"

    def __str__(self) -> str:
        return repr(self)


class AnnotationPreview:
    def __init__(self, annotation_preview: str) -> None:
        self.annotation_preview: str = annotation_preview

    def __repr__(self) -> str:
        return f"AnnotationPreview({self.annotation_preview})"

    def __str__(self) -> str:
        return repr(self)


class DefaultPreview:
    def __init__(self, default_preview: str) -> None:
        self.default_preview = default_preview

    def __repr__(self) -> str:
        return f"DefaultPreview({self.default_preview})"

    def __str__(self) -> str:
        return repr(self)


class ParseHooks:
    def __init__(
        self,
        pre: Callable[[str], str] | None = None,
        post: Callable[[Any], Any] | None = None,
        err: Callable[[str, Exception], Any | Exception] | None = None,
    ) -> None:
        self.pre: Callable[[str], str] | None = pre
        self.post: Callable[[Any], Any] | None = post
        self.err: Callable[[str, Exception], Any | Exception] | None = err

    def __repr__(self) -> str:
        return "ParseHooks(...)"

    def __str__(self) -> str:
        return repr(self)


class CustomAttribute:
    def __init__(self, key: str, value: Any, overwrite: bool = False) -> None:
        self.key: str = key
        self.value: Any = value
        self.overwrite: bool = overwrite

    def __repr__(self) -> str:
        return f"ParseHooks({self.key}, {self.value!r}, {self.overwrite})"

    def __str__(self) -> str:
        return repr(self)


ContainerTypes = list[Any] | tuple[Any, ...]
CONTAINER_TYPES: tuple[type, ...] = list, tuple


type BypassParse = str


type CommandParameterType = type | TypeAliasType | GenericAlias


class CommandParameterAttributes:
    def __init__(self) -> None:
        self._custom_attributes: dict[str, Any] = {}

    @property
    def custom_attributes(self) -> Mapping[str, Any]:
        return self._custom_attributes

    def add_custom_attribute(
        self, key: str, value: Any, overwrite: bool = False
    ) -> Self:
        if key in self._custom_attributes and not overwrite:
            raise KeyError(
                f"Key {key} already exists for command parameter custom attribute and overwrite is False."
            )
        self._custom_attributes[key] = value
        return self

    def pop_custom_attribute(self, key: str) -> Any:
        return self._custom_attributes.pop(key)


@dataclass(frozen=True)
class CommandParameter:
    __mutable_attributes__: ClassVar[
        WeakKeyDictionary[CommandParameter, CommandParameterAttributes]
    ] = WeakKeyDictionary()

    UNPARSED = object()
    DEFAULT_ARG_TYPES = (str,)
    DEFAULT_STR = ""
    empty = Parameter.empty

    names: tuple[str, ...]
    kind: ParameterKind
    annotation: Any
    annotation_preview: str = field(default=DEFAULT_STR)
    argument_types: tuple[CommandParameterType, ...] = field(default=DEFAULT_ARG_TYPES)
    default: Any = field(default_factory=lambda: CommandParameter.empty)
    default_preview: str = field(default=DEFAULT_STR)
    description: str = field(default=DEFAULT_STR)
    parse_hooks: ParseHooks | None = field(default=None)
    container_annotation: Any | None = field(default=None)
    item_types: tuple[CommandParameterType, ...] | None = field(default=None)
    _private_name: str | None = field(default=None)

    def __post_init__(self) -> None:
        CommandParameter.__mutable_attributes__[self] = CommandParameterAttributes()
        self.validate_data()

    @staticmethod
    def build(
        name: str, kind: ParameterKind, annotation: Any, default: Any = empty
    ) -> CommandParameter:
        return CommandParameterBuilder(name, kind, annotation, default).parameter

    @property
    def name(self) -> str:
        assert self.names
        return self.names[0]

    @property
    def private_name(self) -> str:
        return self._private_name or self.names[0]

    @property
    def is_plain(self) -> bool:
        return (
            self.annotation_preview is CommandParameter.DEFAULT_STR
            and self.argument_types is CommandParameter.DEFAULT_ARG_TYPES
            and self.default_preview is CommandParameter.DEFAULT_STR
            and self.description is CommandParameter.DEFAULT_STR
            and self.parse_hooks is None
        )

    @property
    def custom_attributes(self) -> Mapping[str, Any]:
        return CommandParameter.__mutable_attributes__[self].custom_attributes

    @property
    def argument_type(self) -> CommandParameterType:
        return self.argument_types[0]

    @property
    def container_type(self) -> type[ContainerTypes] | None:
        if self.container_annotation is None:
            return None
        return get_origin(self.container_annotation)

    @property
    def bypasses_parsing(self) -> bool:
        return len(self.argument_types) == 1 and self.argument_types[0] is BypassParse

    def add_custom_attribute(
        self, key: str, value: Any, overwrite: bool = False
    ) -> Self:
        CommandParameter.__mutable_attributes__[self].add_custom_attribute(
            key, value, overwrite
        )
        return self

    @staticmethod
    def type_name(t: CommandParameterType) -> str:
        if t == NoneType:
            return str(None)
        if get_origin(t) == Literal:
            return f"Literal[{', '.join(repr(arg) for arg in get_args(t))}]"
        return t.__name__

    def annotation_preview_fallback(self) -> str:
        if self.annotation_preview:
            return self.annotation_preview
        out: str = ""
        for i, t in enumerate(self.argument_types):
            out += CommandParameter.type_name(t)
            if t in CONTAINER_TYPES:
                item_types: tuple[CommandParameterType, ...] | None = self.item_types
                assert item_types is not None
                out += f"[{
                    ' | '.join(
                        [
                            CommandParameter.type_name(item_type)
                            for item_type in item_types
                        ]
                    )
                }{', ...' if t is tuple else ''}]"
            if i != len(self.argument_types) - 1:
                out += " | "
        return out

    def default_preview_fallback(self) -> str | None:
        if self.default == self.empty:
            return None
        if self.default_preview:
            return self.default_preview
        return repr(self.default)

    def basic_parameter_help(self) -> str:
        if (
            self.default != self.empty
            and self.argument_types[0] is bool
            and self.kind
            in (ParameterKind.POSITIONAL_OR_KEYWORD, ParameterKind.KEYWORD_ONLY)
        ):
            return f"[{self.name}]"
        else:
            return (
                "<"
                f"{'*' if self.kind == ParameterKind.VAR_POSITIONAL else ''}"
                f"{'**' if self.kind == ParameterKind.VAR_KEYWORD else ''}"
                f"{self.name}: "
                f"{self.annotation_preview_fallback()}"
                f"{'' if (default := self.default_preview_fallback()) is None else f' = {default}'}"
                ">"
            )

    def extended_parameter_help(self, tab_chars: str = " " * 4) -> str:
        tabstr: str = tab_chars
        out = tabstr
        for i, name in enumerate(self.names):
            out += name
            if i != len(self.names) - 1:
                out += " "
        out += "\n"

        tabstr = tab_chars * 2
        out += f"{tabstr}Kind: {self.kind.name}\n"
        out += f"{tabstr}Annotation: {self.annotation_preview_fallback()}\n"

        out += f"{tabstr}Types:\n"
        for i, t in enumerate(self.argument_types):
            out += f"{tabstr}{tab_chars}{CommandParameter.type_name(t)}"
            if t in CONTAINER_TYPES:
                item_types: tuple[CommandParameterType, ...] | None = self.item_types
                assert item_types is not None
                out += f"[{
                    ' | '.join(
                        [
                            CommandParameter.type_name(item_type)
                            for item_type in item_types
                        ]
                    )
                }{', ...' if t is tuple else ''}]"
            if i != len(self.argument_types) - 1:
                out += "\n"

        if (default := self.default_preview_fallback()) is not None:
            out += f"\n{tabstr}Default: {default}"

        if self.parse_hooks is not None:
            out += f"\n{tabstr}Parse Hooks:"
            if self.parse_hooks.pre is not None:
                out += f"\n{tabstr}{tab_chars}Pre-Hook: {getattr(self.parse_hooks.pre, '__name__', '...')}"
            if self.parse_hooks.post is not None:
                out += f"\n{tabstr}{tab_chars}Post-Hook: {getattr(self.parse_hooks.post, '__name__', '...')}"
            if self.parse_hooks.err is not None:
                out += f"\n{tabstr}{tab_chars}Error-Hook: {getattr(self.parse_hooks.err, '__name__', '...')}"

        if self.description:
            out += f"\n{tabstr}Description: {self.description.replace(chr(0x0A), f'{chr(0x0A)}{tabstr}')}"

        return out

    def remove_custom_attribute(self, key: str) -> Any:
        return CommandParameter.__mutable_attributes__[self].pop_custom_attribute(key)

    def validate_data(self) -> None:
        assert len(self.names), "Parameters must have at least 1 name"
        assert len(self.argument_types), "Parameters must have at least 1 type"


def container_annotation_item_types(
    container_annotation: Any,
) -> tuple[CommandParameterType, ...] | None:
    if container_annotation is None:
        return None
    if not (args := get_args(container_annotation)):
        return (str,)

    if get_origin(container_annotation) is tuple:
        if len(args) != 2 or args[1] is not Ellipsis:
            raise TypeError("Ellipsis required for second generic argument of tuples")
        args = (args[0],)
    elif len(args) != 1:
        raise TypeError("Only single argument generic container types are supported")

    if isinstance(args[0], UnionType) or args[0] == Union:
        return get_args(args[0])
    return args


class CommandParameterBuilder:
    DEFAULT_STR: str = ""
    DEFAULT_NAMES: ClassVar[list[str]] = []
    DEFAULT_ARG_TYPES: ClassVar[list[CommandParameterType]] = [str]

    def __init__(
        self,
        name: str,
        kind: ParameterKind,
        annotation: Any,
        default: Any = CommandParameter.empty,
    ) -> None:
        if isinstance(annotation, str):
            raise TypeError(
                "'annotation' must not be the source code annotation string."
            )

        self._name: str = name
        self._parameter_names: list[str] = CommandParameterBuilder.DEFAULT_NAMES
        self._parameter_kind: ParameterKind = kind
        self._parameter_annotation: Any = annotation
        self._parameter_annotation_preview: str = CommandParameterBuilder.DEFAULT_STR
        self._parameter_argument_types: list[CommandParameterType] = (
            CommandParameterBuilder.DEFAULT_ARG_TYPES
        )
        self._parameter_default: Any = default
        self._parameter_default_preview: str = CommandParameterBuilder.DEFAULT_STR
        self._parameter_description: str = CommandParameterBuilder.DEFAULT_STR
        self._parameter_parse_hooks: ParseHooks | None = None
        self._parameter_container_annotation: Any | None = None
        self._parameter_item_types: list[CommandParameterType] | None = None
        self._custom_attributes: dict[str, Any] = {}
        self._private_name: str = name

        self._has_bypass: bool = False
        self._appending_mode: bool = False
        self._built_parameter: CommandParameter | None = None

        if annotation is CommandParameter.empty:
            self._parameter_names = [name]
        elif (
            isinstance(annotation, TypeAliasType)
            and get_origin(annotation.__value__) is Annotated
        ):
            args: tuple[Any, ...] = get_args(annotation.__value__)
            self._next_annotation(args[0])
            for arg in args[1:]:
                self._next_metadata_annotation(arg)
        elif get_origin(annotation) is Annotated:
            args: tuple[Any, ...] = get_args(annotation)
            self._next_annotation(args[0])
            for arg in args[1:]:
                self._next_metadata_annotation(arg)
        else:
            self._next_annotation(annotation)

    def _next_metadata_annotation(self, annotation: Any) -> None:
        if isinstance(annotation, Alias):
            if self._parameter_names is CommandParameterBuilder.DEFAULT_NAMES:
                self._parameter_names = []

            if not annotation.private:
                self._parameter_names.insert(0, self._name)
            self._parameter_names.extend(annotation.aliases)
            self._private_name = self._name
        elif isinstance(annotation, Description):
            self._parameter_description = annotation.description
        elif isinstance(annotation, AnnotationPreview):
            self._parameter_annotation_preview = annotation.annotation_preview
        elif isinstance(annotation, DefaultPreview):
            self._parameter_default_preview = annotation.default_preview
        elif isinstance(annotation, ParseHooks):
            self._parameter_parse_hooks = annotation
        elif isinstance(annotation, CustomAttribute):
            if not annotation.overwrite and annotation.key in self._custom_attributes:
                raise KeyError(
                    f"Key {annotation.key} already exists for command parameter custom attribute and overwrite is False."
                )
            self._custom_attributes[annotation.key] = annotation.value
        else:
            raise TypeError(f"{annotation} is unsupported")

    def _next_annotation(self, annotation: Any) -> None:
        if self._has_bypass:
            raise TypeError(
                f"The only self._parameter.must be {BypassParse.__name__} when it is specified"
            )

        if isinstance(annotation, type):
            if (
                not self._appending_mode
                or self._parameter_argument_types
                is CommandParameterBuilder.DEFAULT_ARG_TYPES
            ):
                self._parameter_argument_types = [annotation]
            else:
                self._parameter_argument_types = self._parameter_argument_types + [
                    annotation
                ]
            return

        if isinstance(annotation, TypeAliasType):
            self._next_type_alias(annotation)
            return

        if (origin := get_origin(annotation)) in CONTAINER_TYPES:
            if self._parameter_kind not in (
                self._parameter_kind.KEYWORD_ONLY,
                ParameterKind.VAR_KEYWORD,
            ):
                raise TypeError(
                    f"A container argument type must be either {ParameterKind.KEYWORD_ONLY} {ParameterKind.VAR_KEYWORD}"
                )
            self._parameter_argument_types = [origin]
            self._parameter_container_annotation = annotation  # pyright: ignore [reportPrivateUsage]
            self._parameter_item_types = (
                list(types)
                if (
                    types := container_annotation_item_types(
                        self._parameter_container_annotation
                    )
                )
                is not None
                else None
            )
            assert self._parameter_item_types is not None, (
                "Shall not be None of _container_annotation is not None"
            )

            if not all(
                isinstance(item_type, (type, TypeAliasType))
                for item_type in self._parameter_item_types
            ):
                raise TypeError(
                    f"{container_annotation_item_types} is not supported as item types for containers, only {CommandParameterType}."
                )
            return

        if isinstance(annotation, GenericAlias):
            self._next_generic_alias(annotation)
            return

        if isinstance(annotation, UnionType) or get_origin(annotation) == Union:
            args = get_args(annotation)
            for arg in args:
                if (
                    not isinstance(arg, (type, TypeAliasType))
                    and get_origin(arg) not in CONTAINER_TYPES
                ):
                    continue
                self._appending_mode = True
                self._next_annotation(arg)
            return

        if get_origin(annotation) == Literal:
            if (
                not self._appending_mode
                or self._parameter_argument_types
                is CommandParameterBuilder.DEFAULT_ARG_TYPES
            ):
                self._parameter_argument_types = [annotation]
            else:
                self._parameter_argument_types = self._parameter_argument_types + [
                    annotation
                ]
            return

        raise TypeError(f"{annotation} is unsupported")

    def _next_type_alias(self, annotation: TypeAliasType) -> None:
        if annotation is BypassParse:
            if self._parameter_kind != self._parameter_kind.VAR_POSITIONAL:
                raise TypeError(
                    f"{BypassParse.__name__} self._parameter.kind must be VAR_POSITIONAL"
                )
            if self._parameter_default is not CommandParameter.empty:
                raise TypeError(
                    f"{BypassParse.__name__} self._parameter.must be empty, it will always be provided."
                )
            self._has_bypass = True
            self._parameter_argument_types = [BypassParse]
            return

        if self._parameter_argument_types is CommandParameterBuilder.DEFAULT_ARG_TYPES:
            self._parameter_argument_types = [annotation]
        else:
            self._parameter_argument_types = self._parameter_argument_types + [
                annotation
            ]

        self._appending_mode = True
        self._next_annotation(annotation.__value__)

    def _next_generic_alias(self, annotation: GenericAlias) -> None:
        if self._parameter_argument_types is CommandParameterBuilder.DEFAULT_ARG_TYPES:
            self._parameter_argument_types = [annotation]
        else:
            self._parameter_argument_types = self._parameter_argument_types + [
                annotation
            ]

    @property
    def parameter(self) -> CommandParameter:
        if self._built_parameter is not None:
            return self._built_parameter

        if self._parameter_names is CommandParameterBuilder.DEFAULT_NAMES:
            self._parameter_names = [self._name]

        self._built_parameter = CommandParameter(
            names=tuple(self._parameter_names),
            kind=self._parameter_kind,
            annotation=self._parameter_annotation,
            annotation_preview=CommandParameter.DEFAULT_STR
            if self._parameter_annotation_preview is CommandParameterBuilder.DEFAULT_STR
            else self._parameter_annotation_preview,
            argument_types=CommandParameter.DEFAULT_ARG_TYPES
            if self._parameter_argument_types
            is CommandParameterBuilder.DEFAULT_ARG_TYPES
            else tuple(self._parameter_argument_types),
            default=self._parameter_default,
            default_preview=CommandParameter.DEFAULT_STR
            if self._parameter_default_preview is CommandParameterBuilder.DEFAULT_STR
            else self._parameter_default_preview,
            description=CommandParameter.DEFAULT_STR
            if self._parameter_description is CommandParameterBuilder.DEFAULT_STR
            else self._parameter_description,
            parse_hooks=self._parameter_parse_hooks,
            container_annotation=self._parameter_container_annotation,
            item_types=tuple(self._parameter_item_types)
            if self._parameter_item_types
            else (),
            _private_name=self._private_name,
        )
        for key, value in self._custom_attributes.items():
            self._built_parameter.add_custom_attribute(key, value)

        return self.parameter


__all__ = [
    "CONTAINER_TYPES",
    "Alias",
    "AnnotationPreview",
    "BypassParse",
    "CommandParameter",
    "CommandParameterBuilder",
    "CommandParameterType",
    "ContainerTypes",
    "CustomAttribute",
    "DefaultPreview",
    "Description",
    "ParameterKind",
    "ParseHooks",
]
