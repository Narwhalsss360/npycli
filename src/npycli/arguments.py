from __future__ import annotations
from typing import Callable, Any, Annotated, Optional, Union, get_origin, get_args
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


@dataclass
class CommandParameter:
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
            else:
                if isinstance(annotation, type):
                    parameter.argument_types = (annotation,)
                elif get_origin(annotation) == Union:
                    parameter.argument_types = ()
                    for arg in get_args(annotation):
                        if isinstance(arg, type):
                            parameter.argument_types = (arg,) + parameter.argument_types
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


def main() -> None:
    parameter: CommandParameter = CommandParameter.build(
        "param",
        ParameterKind.POSITIONAL_OR_KEYWORD,
        Annotated[
            Optional[int],
            Alias("p", "n", private=True),
            Description("Natural number"),
            AnnotationPreview("ℕ"),
            #          lower str            negate arg    just re-raise exception
            ParseHooks(lambda s: s.lower(), lambda n: -n, lambda s, e: e)
        ],
        0
    )
    ...


if __name__ == "__main__":
    main()
