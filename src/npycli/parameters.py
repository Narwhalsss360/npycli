from __future__ import annotations
from types import NoneType, UnionType
from collections.abc import Callable
from typing import Any, Annotated, Type, Union, TypeAliasType, get_origin, get_args, Literal
from inspect import _ParameterKind, Parameter  # type: ignore
from dataclasses import dataclass, field
from .errors import ParsingError, MissingKeywordArgumentValueError


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
        err: Callable[[str, Exception], Any | Exception] | None = None
    ) -> None:
        self.pre: Callable[[str], str] | None = pre
        self.post: Callable[[Any], Any] | None = post
        self.err: Callable[[str, Exception], Any | Exception] | None = err

    def __repr__(self) -> str:
        return "ParseHooks(...)"

    def __str__(self) -> str:
        return repr(self)


class CustomAttrbute:
    def __init__(self, key: str, value: Any, overwrite: bool = False) -> None:
        self.key: str = key
        self.value: Any = value
        self.overwrite: bool = overwrite

    def __repr__(self) -> str:
        return f"ParseHooks({self.key}, {repr(self.value)}, {self.overwrite})"

    def __str__(self) -> str:
        return repr(self)


ContainerTypes = (list[Any] | tuple[Any, ...])
CONTAINER_TYPES: tuple[type, ...] = list, tuple


type BypassParse = str


type CommandParameterType = type | TypeAliasType


@dataclass
class CommandParameter:
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

    def __post_init__(self) -> None:
        self._custom_attributes: dict[str, Any] = {}
        self._container_annotation: Any | None = None
        self._private_name: str | None = None
        self._validate_data()

    @staticmethod
    def build(name: str, kind: ParameterKind, annotation: Any, default: Any = empty) -> CommandParameter:
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
            self.annotation_preview is CommandParameter.DEFAULT_STR and
            self.argument_types is CommandParameter.DEFAULT_ARG_TYPES and
            self.default_preview is CommandParameter.DEFAULT_STR and
            self.description is CommandParameter.DEFAULT_STR and
            self.parse_hooks is None
        )

    @property
    def custom_attributes(self) -> dict[str, Any]:
        return self._custom_attributes

    @property
    def argument_type(self) -> CommandParameterType:
        return self.argument_types[0]

    @property
    def container_type(self) -> Type[ContainerTypes] | None:
        if self._container_annotation is None:
            return None
        return get_origin(self._container_annotation)

    @property
    def item_types(self) -> tuple[CommandParameterType, ...] | None:
        if self._container_annotation is None:
            return None
        if (args := get_args(self._container_annotation)) is None:
            return (str, )

        if get_origin(self._container_annotation) is tuple:
            if len(args) != 2 or args[1] is not Ellipsis:
                raise TypeError("Ellipsis required for second generic argument of tuples")
            args = (args[0],)
        elif len(args) != 1:
            raise TypeError("Only single argument generic container types are supported")

        if isinstance(args[0], UnionType) or args[0] == Union:
            return get_args(args[0])
        return args

    @property
    def bypasses_parsing(self) -> bool:
        return len(self.argument_types) == 1 and self.argument_types[0] is BypassParse

    def add_custom_attribute(self, key: str, value: Any, overwrite: bool = False) -> None:
        if not overwrite and key in self._custom_attributes:
            raise KeyError(f"Key {key} already exists and overwrite is False")
        self._custom_attributes[key] = value

    @staticmethod
    def type_name(t: CommandParameterType) -> str:
        if t == NoneType:
            return str(None)
        if get_origin(t) == Literal:
            return f"Literal[{", ".join(repr(arg) for arg in get_args(t))}]"
        return t.__name__

    def annotation_preview_fallback(self) -> str:
        if self.annotation_preview:
            return self.annotation_preview
        out: str = ""
        for i, t in enumerate(self.argument_types):
            out += CommandParameter.type_name(t)
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
            self.default != self.empty and
            self.argument_types[0] is bool and
            self.kind in (ParameterKind.POSITIONAL_OR_KEYWORD, ParameterKind.KEYWORD_ONLY)
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
        return self._custom_attributes.pop(key)

    def _validate_data(self) -> None:
        assert len(self.names), "Parameters must have at least 1 name"
        assert len(self.argument_types), "Parameters must have at least 1 type"


class CommandParameterBuilder:
    DEFAULT_NAMES: tuple[str] = ("",)

    def __init__(self, name: str, kind: ParameterKind, annotation: Any, default: Any = CommandParameter.empty) -> None:
        if isinstance(annotation, str):
            raise ValueError("'annotation' must not be the source code annotation string.")

        self._name: str = name
        self._kind: ParameterKind = kind
        self._default: Any = default
        self._parameter: CommandParameter = CommandParameter(CommandParameterBuilder.DEFAULT_NAMES, kind, annotation, default=default)
        self._has_bypass: bool = False
        self._appending_mode: bool = False
        self._built: bool = False

        if isinstance(annotation, TypeAliasType) and get_origin(annotation.__value__) is Annotated:
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
            self._parameter.names = (() if annotation.private else (self._name,)) + annotation.aliases
            self._parameter._private_name = self._name
        elif isinstance(annotation, Description):
            self._parameter.description = annotation.description
        elif isinstance(annotation, AnnotationPreview):
            self._parameter.annotation_preview = annotation.annotation_preview
        elif isinstance(annotation, DefaultPreview):
            self._parameter.default_preview = annotation.default_preview
        elif isinstance(annotation, ParseHooks):
            self._parameter.parse_hooks = annotation
        elif isinstance(annotation, CustomAttrbute):
            self._parameter.add_custom_attribute(annotation.key, annotation.value, annotation.overwrite)
        else:
            raise TypeError(f"{annotation} is unsupported")

    def _next_annotation(self, annotation: Any) -> None:
        if self._has_bypass:
            raise TypeError(f"The only self._parameter.must be {BypassParse.__name__} when it is specified")

        if isinstance(annotation, type):
            if not self._appending_mode or self._parameter.argument_types is CommandParameter.DEFAULT_ARG_TYPES:
                self._parameter.argument_types = (annotation,)
            else:
                self._parameter.argument_types = self._parameter.argument_types + (annotation,)
            return

        if isinstance(annotation, TypeAliasType):
            self._next_type_alias(annotation)
            return

        if (origin := get_origin(annotation)) in CONTAINER_TYPES:
            if self._kind not in (self._parameter.kind.KEYWORD_ONLY, ParameterKind.VAR_KEYWORD):
                raise TypeError(f"A container argument type must be either {ParameterKind.KEYWORD_ONLY} {ParameterKind.VAR_KEYWORD}")
            self._parameter.argument_types = (origin,)
            self._parameter._container_annotation = annotation
            item_types: tuple[CommandParameterType, ...] | None = self._parameter.item_types
            assert item_types is not None, "Shall not be None of _container_annotation is not None"

            if not all(isinstance(item_type, (type, TypeAliasType)) for item_type in item_types):
                raise TypeError(f"{item_types} is not supported as item types for containers, only {CommandParameterType}.")
            return

        if isinstance(annotation, UnionType) or get_origin(annotation) == Union:
            args = get_args(annotation)
            for arg in args:
                if not isinstance(arg, (type, TypeAliasType)) and get_origin(arg) not in CONTAINER_TYPES:
                    continue
                self._appending_mode = True
                self._next_annotation(arg)
            return

        if get_origin(annotation) == Literal:
            if not self._appending_mode or self._parameter.argument_types is CommandParameter.DEFAULT_ARG_TYPES:
                self._parameter.argument_types = (annotation,)
            else:
                self._parameter.argument_types = self._parameter.argument_types + (annotation,)
            return

        raise TypeError(f"{annotation} is unsupported")

    def _next_type_alias(self, annotation: TypeAliasType) -> None:
        if annotation is BypassParse:
            if self._kind != self._parameter.kind.VAR_POSITIONAL:
                raise TypeError(f"{BypassParse.__name__} self._parameter.kind must be VAR_POSITIONAL")
            if self._default is not self._parameter.empty:
                raise TypeError(f"{BypassParse.__name__} self._parameter.must be empty, it will always be provided.")
            self._has_bypass = True
            self._parameter.argument_types = (BypassParse,)
            return

        if self._parameter.argument_types is CommandParameter.DEFAULT_ARG_TYPES:
            self._parameter.argument_types = (annotation,)
        else:
            self._parameter.argument_types = self._parameter.argument_types + (annotation,)

        self._appending_mode = True
        self._next_annotation(annotation.__value__)

    @property
    def parameter(self) -> CommandParameter:
        if self._built:
            return self._parameter

        self._built = True
        if self._parameter.names is CommandParameterBuilder.DEFAULT_NAMES:
            self._parameter.names = (self._name,)

        self._parameter._validate_data()
        return self._parameter


def parse_with_hooks(parameter: CommandParameter, entry: str, parsers: dict[CommandParameterType, Callable[[str], Any]]) -> Any:
    pre: Callable[[str], str] = lambda s: s
    post: Callable[[Any], Any] = lambda o: o
    err: Callable[[str, Exception], Any | Exception] = lambda _, e: e
    if parameter.parse_hooks:
        pre = parameter.parse_hooks.pre or pre
        post = parameter.parse_hooks.post or post
        err = parameter.parse_hooks.err or err

    parsed: Any = CommandParameter.UNPARSED
    entry = pre(entry)
    for ith_type, parameter_type in enumerate(parameter.argument_types):
        if parameter_type in CONTAINER_TYPES and (item_types := parameter.item_types) is not None:
            inner_types: tuple[CommandParameterType, ...] = item_types
        else:
            inner_types: tuple[CommandParameterType, ...] = (parameter_type,)

        for ith_inner_type, inner_type in enumerate(inner_types):
            if isinstance(inner_type, type):
                parser: Callable[..., Any] = parsers.get(inner_type, inner_type)
            elif inner_type in parsers:
                parser: Callable[..., Any] = parsers[inner_type]
            else:
                continue

            try:
                parsed = parser(entry)
                break
            except Exception as exc:
                if not isinstance(handled := err(entry, exc), Exception):
                    parsed = handled
                    break
                if ith_type != len(parameter.argument_types) - 1 or ith_inner_type != len(inner_types) - 1:
                    continue

                if isinstance(
                    handled := err(entry, ParsingError(entry, f"Parse resolution exhausted: {entry} as {parameter.argument_types}")),
                    Exception
                ):
                    raise handled
                parsed = handled
                break

        if parsed is not CommandParameter.UNPARSED:
            break

    if parsed is CommandParameter.UNPARSED:
        raise ParsingError(entry, f"Parse resolution exhausted: {entry} as {parameter.argument_types}")

    return post(parsed)


def add_to_container_type(container_type: Type[ContainerTypes], current: ContainerTypes | None, parsed: Any) -> ContainerTypes:
    if container_type is list:
        if current is None:
            return [parsed]
        assert isinstance(current, list)
        current.append(parsed)
        return current
    elif container_type is tuple:
        if current is None:
            return (parsed,)
        assert isinstance(current, tuple)
        return current + (parsed,)
    else:
        raise ValueError(f"'container_type' must be of either {CONTAINER_TYPES}")


def parse_parameters(
    parameters: list[CommandParameter],
    entries: list[str],
    keyword_prefix: str,
    argument_seperator: str,
    parsers: dict[CommandParameterType, Callable[[str], Any]]
) -> tuple[list[Any], dict[str, Any]]:
    arguments: list[Any] = []
    keyword_arguments: dict[str, Any] = {}
    var_args: CommandParameter | None = next(filter(lambda p: p.kind == ParameterKind.VAR_POSITIONAL, parameters), None)
    var_args_index: int = -1 if var_args is None else parameters.index(var_args)
    var_kwargs: CommandParameter | None = next(filter(lambda p: p.kind == ParameterKind.VAR_KEYWORD, parameters), None)

    if len(parameters) == 1 and parameters[0].bypasses_parsing:
        return entries, {}

    keyword_parameter: CommandParameter | None = None
    var_kwarg: str | None = None
    no_keywords: bool = False
    for i, entry in enumerate(entries):
        if entry == argument_seperator:
            no_keywords = True
            continue

        if not no_keywords and entry.startswith(keyword_prefix):
            if keyword_parameter is not None:
                assert isinstance(keyword_parameter, CommandParameter)
                raise MissingKeywordArgumentValueError(keyword_parameter.name, f"'{keyword_parameter.name}' is missing a value")
            if var_kwarg is not None:
                assert var_kwargs is not None, "'var_kwarg' may only be not None if 'var_kwargs' is not None"
                if bool in var_kwargs.argument_types:
                    keyword_arguments[var_kwarg] = True
                else:
                    raise MissingKeywordArgumentValueError(f"'{var_kwarg}' is missing a value")

            keyword = entry[len(keyword_prefix):]
            if (keyword_parameter := next(filter(lambda p: keyword in p.names, parameters), None)) is not None:  # type: ignore
                if keyword_parameter.kind == ParameterKind.POSITIONAL_ONLY:
                    raise ParsingError(keyword_parameter.name, "This argument is positional only")
                elif keyword_parameter.kind == ParameterKind.POSITIONAL_OR_KEYWORD:
                    if parameters.index(keyword_parameter) < len(arguments):
                        raise ParsingError(keyword_parameter.name, f"'{keyword_parameter.name}' was already specified positionally")

                if keyword_parameter.argument_types[0] is bool:  # Boolean flag
                    keyword_arguments[keyword_parameter.private_name] = True
                    keyword_parameter = None
            else:
                if var_kwargs is not None:
                    if bool in var_kwargs.argument_types and i == len(entries) - 1:
                        keyword_arguments[keyword] = True
                    else:
                        var_kwarg = keyword
                else:
                    raise ParsingError(keyword, f"'{keyword}' is not a keyword parameter")
            continue

        if keyword_parameter is not None:
            assert isinstance(keyword_parameter, CommandParameter)
            if (container_type := keyword_parameter.container_type) is not None:
                keyword_arguments[keyword_parameter.private_name] = add_to_container_type(
                    container_type,
                    keyword_arguments.get(keyword_parameter.private_name, None),
                    parse_with_hooks(keyword_parameter, entry, parsers)
                )
                keyword_parameter = None
            else:
                keyword_arguments[keyword_parameter.private_name] = parse_with_hooks(keyword_parameter, entry, parsers)
                keyword_parameter = None
            continue

        if var_kwarg is not None:
            assert var_kwargs is not None, "'var_kwarg' may only be not None if 'var_kwargs' is not None"
            if (container_type := var_kwargs.container_type) is not None:
                if var_kwarg not in keyword_arguments:
                    keyword_arguments[var_kwarg] = container_type()
                keyword_arguments[var_kwarg] = add_to_container_type(
                    container_type,
                    keyword_arguments[var_kwarg],
                    parse_with_hooks(var_kwargs, entry, parsers)
                )
            else:
                keyword_arguments[var_kwarg] = parse_with_hooks(var_kwargs, entry, parsers)
            var_kwarg = None
            continue

        if var_args is not None and len(arguments) > var_args_index:
            arguments.append(parse_with_hooks(var_args, entry, parsers))
            continue

        if len(arguments) >= len(parameters):
            raise ParsingError(arguments[len(parameters) - (1 if len(arguments) == len(parameters) else 0)], "Too many positional arguments")

        parameter: CommandParameter = parameters[len(arguments)]
        if parameter.kind in (ParameterKind.KEYWORD_ONLY, ParameterKind.VAR_KEYWORD):
            raise ParsingError(arguments[len(parameters)], "Too many positional arguments")
        arguments.append(parse_with_hooks(parameter, entry, parsers))

    if keyword_parameter is not None:
        raise MissingKeywordArgumentValueError(keyword_parameter.name, f"'{keyword_parameter.name}' is missing a value")
    if var_kwarg is not None:
        raise MissingKeywordArgumentValueError(var_kwarg, f"'{var_kwarg}' is missing a value")

    required_positionals: int = 0
    for i, parameter in enumerate(parameters):
        if parameter.kind == ParameterKind.POSITIONAL_ONLY:
            if parameter.default == parameter.empty and len(arguments) <= i:
                raise ParsingError(parameter.name, f"Missing required positional '{parameter.name}'")
            continue

        if parameter.kind == ParameterKind.POSITIONAL_OR_KEYWORD:
            if parameter.default != parameter.empty:
                continue
            if len(arguments) > i:
                continue
            if parameter.private_name not in keyword_arguments:
                raise ParsingError(parameter.name, f"Missing required keyword/positional '{parameter.name}'")
        if parameter.default != parameter.empty or parameter.kind in (ParameterKind.VAR_POSITIONAL, ParameterKind.VAR_KEYWORD):
            continue

        if parameter.private_name not in keyword_arguments:
            raise ParsingError(parameter.name, f"Missing required keyword '{parameter.name}'")

    if len(arguments) < required_positionals:
        raise ParsingError(parameters[len(arguments)].name, f"Missing required positional '{parameters[len(arguments)].name}'")

    return arguments, keyword_arguments


__all__ = [
    "Parameter",
    "ParsingError",
    "MissingKeywordArgumentValueError",
    "Alias",
    "Description",
    "AnnotationPreview",
    "DefaultPreview",
    "ParseHooks",
    "CustomAttrbute",
    "CommandParameter",
    "CommandParameterBuilder",
    "parse_with_hooks",
    "add_to_container_type",
    "parse_parameters",
]
