from __future__ import annotations
from types import UnionType
from typing import Callable, Any, Annotated, Union, get_origin, get_args
from inspect import _ParameterKind, Parameter
from dataclasses import dataclass, field


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
        pre: Callable[[str], str] | None,
        post: Callable[[Any], Any] | None,
        err: Callable[[str, Exception], Any | Exception] | None = None
    ) -> None:
        self.pre: Callable[[str], str] | None = pre
        self.post: Callable[[Any], Any] | None = post
        self.err: Callable[[str, Exception], Any | Exception] | None = err

    def __repr__(self) -> str:
        return f"ParseHooks(...)"

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
    argument_types: tuple[type, ...] = field(default=DEFAULT_ARG_TYPES)
    default: Any = field(default=empty)
    default_preview: str = field(default=DEFAULT_STR)
    description: str = field(default=DEFAULT_STR)
    parse_hooks: ParseHooks | None = field(default=None)

    def __post_init__(self) -> None:
        self._custom_attributes: dict[str, Any] = {}

    @staticmethod
    def build(name: str, kind: ParameterKind, annotation: Any, default: Any = empty) -> CommandParameter:
        if isinstance(annotation, str):
            raise ValueError("'annotation' must not be the source code annotation strign.")
        DEFAULT_NAMES: tuple[str] = ("",)
        parameter: CommandParameter = CommandParameter(DEFAULT_NAMES, kind, annotation, default=default)

        def next_annotation(annotation: Any, is_metadata: bool = False) -> None:
            if is_metadata:
                if isinstance(annotation, Alias):
                    parameter.names = (() if annotation.private else (name,)) + annotation.aliases
                elif isinstance(annotation, Description):
                    parameter.description = annotation.description
                elif isinstance(annotation, AnnotationPreview):
                    parameter.annotation_preview = annotation.annotation_preview
                elif isinstance(annotation, DefaultPreview):
                    parameter.default_preview = annotation.default_preview
                elif isinstance(annotation, ParseHooks):
                    parameter.parse_hooks = annotation
                elif isinstance(annotation, CustomAttrbute):
                    parameter.add_custom_attribute(annotation.key, annotation.value, annotation.overwrite)
            else:
                if isinstance(annotation, type):
                    parameter.argument_types = (annotation,)
                elif isinstance(annotation, UnionType) or get_origin(annotation) == Union:
                    parameter.argument_types = tuple(arg for arg in get_args(annotation) if isinstance(arg, type))
                else:
                    raise TypeError(f"{annotation} is unsupported")

        if get_origin(annotation) == Annotated:
            is_metadata: bool = False
            for arg in get_args(annotation):
                next_annotation(arg, is_metadata)
                is_metadata = True
        else:
            next_annotation(annotation)

        if parameter.names is DEFAULT_NAMES:
            parameter.names = (name,)

        return parameter

    @property
    def name(self) -> str:
        return self.names[0]

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

    def add_custom_attribute(self, key: str, value: Any, overwrite: bool = False) -> None:
        if not overwrite and key in self._custom_attributes:
            raise KeyError(f"Key {key} already exists and overwrite is False")
        self._custom_attributes[key] = value

    def remove_custom_attribute(self, key: str) -> Any:
        return self._custom_attributes.pop(key)


def parse_with_hooks(parameter: CommandParameter, entry: str, parsers: dict[type, Callable[[str], Any]]) -> Any:
    pre: Callable[[str], str] = lambda s: s
    post: Callable[[Any], Any] = lambda o: o
    err: Callable[[str, Exception], Any | Exception] = lambda _, e: e
    if parameter.parse_hooks:
        pre = parameter.parse_hooks.pre or pre
        post = parameter.parse_hooks.post or post
        err = parameter.parse_hooks.err or err

    parsed: Any = CommandParameter.UNPARSED
    entry = pre(entry)
    for i, t in enumerate(parameter.argument_types):
        parser: Callable = parsers.get(t, t)
        try:
            parsed = parser(entry)
            break
        except Exception as exc:
            if not isinstance(handled := err(entry, exc), Exception):
                parsed = handled
                break
            if i != len(parameter.argument_types) - 1:
                continue

            if isinstance(
                handled := err(entry, NotImplementedError(f"Parse resolution exhausted: {entry} as {parameter.argument_types}")),
                Exception
            ):
                raise handled
            parsed = handled
            break

    return post(parsed)


def parse_parameters(
    parameters: list[CommandParameter],
    entries: list[str],
    keyword_prefix: str,
    argument_seperator: str,
    parsers: dict[type, Callable[[str], Any]]
) -> tuple[list[Any], dict[str, Any]]:
    arguments: list[Any] = []
    keyword_arguments: dict[str, Any] = {}
    var_args: CommandParameter | None = next(filter(lambda p: p.kind == ParameterKind.VAR_POSITIONAL, parameters), None)
    var_args_index: int = -1 if var_args is None else parameters.index(var_args)
    var_kwargs: CommandParameter | None = next(filter(lambda p: p.kind == ParameterKind.VAR_KEYWORD, parameters), None)

    keyword_parameter: CommandParameter | None = None
    var_kwarg: str | None = None
    no_keywords: bool = False
    for entry in entries:
        if entry == argument_seperator:
            no_keywords = True
            continue

        if not no_keywords and entry.startswith(keyword_prefix):
            if keyword_parameter is not None:
                raise NotImplementedError(f"'{keyword_parameter.name}' is missing a value")
            if var_kwarg is not None:
                raise NotImplementedError(f"'{var_kwarg}' is missing a value")

            keyword = entry[len(keyword_prefix):]
            if (keyword_parameter := next(filter(lambda p: keyword in p.names, parameters), None)) is not None:
                if keyword_parameter.kind == ParameterKind.POSITIONAL_ONLY:
                    raise NotImplementedError("This argument is positional only")
                elif keyword_parameter.kind == ParameterKind.POSITIONAL_OR_KEYWORD:
                    if parameters.index(keyword_parameter) < len(arguments):
                        raise NotImplementedError(f"'{keyword_parameter.name}' was already specified positionally")

                if keyword_parameter.argument_types[0] == bool: # Boolean flag
                    keyword_arguments[keyword_parameter.name] = True
                    keyword_parameter = None
            else:
                if var_kwargs is not None:
                    var_kwarg = keyword
                else:
                    raise NotImplementedError(f"'{keyword}' is not a keyword parameter")
            continue

        if keyword_parameter is not None:
            keyword_arguments[keyword_parameter.name] = parse_with_hooks(keyword_parameter, entry, parsers)
            keyword_parameter = None
            continue

        if var_kwarg is not None:
            assert var_kwargs is not None, "'var_kwarg' may only be not None if 'var_kwargs' is not None"
            keyword_arguments[var_kwarg] = parse_with_hooks(var_kwargs, entry, parsers)
            var_kwarg = None
            continue

        if var_args is not None and len(arguments) > var_args_index:
            arguments.append(parse_with_hooks(var_args, entry, parsers))
            continue

        if len(arguments) >= len(parameters):
            raise NotImplementedError(f"Too many positional arguments")

        parameter: CommandParameter = parameters[len(arguments)]
        if parameter.kind in (ParameterKind.KEYWORD_ONLY, ParameterKind.VAR_KEYWORD):
            raise NotImplementedError(f"Too many positional arguments")
        arguments.append(parse_with_hooks(parameter, entry, parsers))

    required_positionals: int = 0
    for i, parameter in enumerate(parameters):
        if parameter.kind == ParameterKind.POSITIONAL_ONLY:
            if parameter.default == parameter.empty and len(arguments) <= i:
                raise NotImplementedError(f"Missing required positional '{parameter.name}'")
            continue

        if parameter.kind == ParameterKind.POSITIONAL_OR_KEYWORD:
            if parameter.default != parameter.empty:
                continue
            if len(arguments) > i:
                continue
            if parameter.name not in keyword_arguments:
                raise NotImplementedError(f"Missing required keyword/positional '{parameter.name}'")
        if parameter.default != parameter.empty or parameter.kind in (ParameterKind.VAR_POSITIONAL, ParameterKind.VAR_KEYWORD):
            continue

        if parameter.name not in keyword_arguments:
            raise NotImplementedError(f"Missing required keyword '{parameter.name}'")

    if len(arguments) < required_positionals:
        raise NotImplementedError(f"Missing required positional '{parameters[len(arguments)].name}'")

    return arguments, keyword_arguments


def main() -> None:
    from pathlib import Path
    two_sum_parameters: list[CommandParameter] = [
        CommandParameter.build(
            "first",
            ParameterKind.POSITIONAL_ONLY,
            Annotated[int | float, Alias("a", "x"), Description("First number to sum.")]
        ),
        CommandParameter.build(
            "second",
            ParameterKind.POSITIONAL_OR_KEYWORD,
            Annotated[int | float, Alias("b", "y"), Description("Second number to sum.")]
        ),
        CommandParameter.build(
            "output",
            ParameterKind.KEYWORD_ONLY,
            Annotated[Path, CustomAttrbute("directory", "no")],
            default=None
        )
    ]
    parsed = parse_parameters(two_sum_parameters, ["1.2", "2"], "--", "--", {})
    del parsed


if __name__ == "__main__":
    main()
