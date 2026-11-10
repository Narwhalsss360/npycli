from __future__ import annotations

from collections.abc import Callable, Sequence
from enum import Enum
from types import UnionType
from typing import Any, ClassVar, Literal, TypeAliasType, get_args, get_origin

from npycli.errors import MissingKeywordArgumentValueError, ParsingError
from npycli.parameters import (
    CONTAINER_TYPES,
    CommandParameter,
    CommandParameterType,
    ContainerTypes,
    ParameterKind,
)

type Parsers = dict[CommandParameterType, Callable[[str], Any]]


def create_literal_parser(
    literal_type: TypeAliasType | UnionType,
) -> Callable[[str], Any]:
    if isinstance(literal_type, TypeAliasType):
        return create_literal_parser(literal_type.__value__)

    if get_origin(literal_type) != Literal:
        raise TypeError("Argument must be of origin 'Literal'")

    if not all(isinstance(t, (int, str)) for t in get_args(literal_type)):
        raise TypeError("Only supported arguments of 'Literal' are str and int.")

    def parser(s: str) -> Any:
        for literal_value in get_args(literal_type):
            if isinstance(literal_value, str):
                if s == literal_value:
                    return literal_value
            else:
                assert isinstance(literal_value, int)
                if int(s) == literal_value:
                    return literal_value
        raise ValueError(f"{s} was not one of {get_args(literal_type)!r}")

    return parser


def create_enum_parser[T](enum_type: type[T]) -> Callable[[str], T]:
    assert issubclass(enum_type, Enum)

    def parser(s: str) -> T:
        try:
            return enum_type(s)
        except ValueError:
            return enum_type[s]

    return parser


def default_pre_parse_hook(s: str) -> str:
    return s


def default_post_parse_hook(s: Any) -> Any:
    return s


def default_err_parse_hook(_: str, exc: Exception) -> Any | Exception:
    return exc


def parse_with_hooks(
    parameter: CommandParameter,
    entry: str,
    parsers: Parsers,
) -> Any:
    pre: Callable[[str], str] = default_pre_parse_hook
    post: Callable[[Any], Any] = default_post_parse_hook
    err: Callable[[str, Exception], Any | Exception] = default_err_parse_hook
    if parameter.parse_hooks:
        pre = parameter.parse_hooks.pre or pre
        post = parameter.parse_hooks.post or post
        err = parameter.parse_hooks.err or err

    parsed: Any = CommandParameter.UNPARSED
    entry = pre(entry)
    for ith_type, parameter_type in enumerate(parameter.argument_types):
        if (
            parameter_type in CONTAINER_TYPES
            and (item_types := parameter.item_types) is not None
        ):
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
            except (ParsingError, TypeError, ValueError, RuntimeError) as exc:
                if not isinstance(handled := err(entry, exc), Exception):
                    parsed = handled
                    break
                if (
                    ith_type != len(parameter.argument_types) - 1
                    or ith_inner_type != len(inner_types) - 1
                ):
                    continue

                parsing_error = ParsingError(
                    entry,
                    f"Parse resolution exhausted: {entry} as {parameter.argument_types}",
                )
                if isinstance(
                    handled := err(entry, parsing_error),
                    Exception,
                ):
                    if handled is parsing_error:
                        raise parsing_error from exc

                    if handled is exc:
                        raise
                    else:
                        raise handled

                parsed = handled
                break

        if parsed is not CommandParameter.UNPARSED:
            break

    if parsed is CommandParameter.UNPARSED:
        raise ParsingError(
            entry, f"Parse resolution exhausted: {entry} as {parameter.argument_types}"
        )

    return post(parsed)


def add_to_container_type(
    container_type: type[ContainerTypes], current: ContainerTypes | None, parsed: Any
) -> ContainerTypes:
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


class CommandParameterParser:
    DEFAULT_KEYWORD_PREFIX: ClassVar[str] = "--"
    DEFAULT_ARGUMENT_SEPARATOR: ClassVar[str] = DEFAULT_KEYWORD_PREFIX

    class Context:
        def __init__(self, parameters: Sequence[CommandParameter]) -> None:
            self.arguments: list[Any] = []
            self.keyword_arguments: dict[str, Any] = {}
            self.var_args: CommandParameter | None = next(
                filter(lambda p: p.kind == ParameterKind.VAR_POSITIONAL, parameters),
                None,
            )
            self.var_args_index: int = (
                -1 if self.var_args is None else parameters.index(self.var_args)
            )
            self.var_kwargs: CommandParameter | None = next(
                filter(lambda p: p.kind == ParameterKind.VAR_KEYWORD, parameters), None
            )
            self.keyword_parameter: CommandParameter | None = None
            self.var_kwarg: str | None = None
            self.no_keywords: bool = False

    def __init__(
        self,
        keyword_prefix: str = DEFAULT_KEYWORD_PREFIX,
        argument_separator: str = DEFAULT_ARGUMENT_SEPARATOR,
        parsers: Parsers | None = None,
    ) -> None:
        self.keyword_prefix: str = keyword_prefix
        self.argument_separator: str = argument_separator
        self.parsers: Parsers = parsers or {}

    def _next_keyword(
        self,
        context: CommandParameterParser.Context,
        parameters: Sequence[CommandParameter],
        bypass_parse: bool,
        entries: Sequence[str],
        i: int,
    ) -> None:
        entry: str = entries[i]
        if context.keyword_parameter is not None:
            assert isinstance(context.keyword_parameter, CommandParameter)
            raise MissingKeywordArgumentValueError(
                context.keyword_parameter.name,
                f"'{context.keyword_parameter.name}' is missing a value",
            )
        if context.var_kwarg is not None:
            assert context.var_kwargs is not None, (
                "'var_kwarg' may only be not None if 'var_kwargs' is not None"
            )
            if bool in context.var_kwargs.argument_types:
                context.keyword_arguments[context.var_kwarg] = True
            else:
                raise MissingKeywordArgumentValueError(
                    f"'{context.var_kwarg}' is missing a value"
                )

        keyword = entry[len(self.keyword_prefix) :]
        context.keyword_parameter = next(
            filter(lambda p: keyword in p.names, parameters), None
        )
        if context.keyword_parameter is not None:  # type: ignore
            context.keyword_parameter = context.keyword_parameter
            if context.keyword_parameter.kind == ParameterKind.POSITIONAL_ONLY:
                raise ParsingError(
                    context.keyword_parameter.name, "This argument is positional only"
                )
            elif (
                context.keyword_parameter.kind == ParameterKind.POSITIONAL_OR_KEYWORD
                and parameters.index(context.keyword_parameter) < len(context.arguments)
            ):
                raise ParsingError(
                    context.keyword_parameter.name,
                    f"'{context.keyword_parameter.name}' was already specified positionally",
                )

            if context.keyword_parameter.argument_types[0] is bool:  # Boolean flag
                context.keyword_arguments[context.keyword_parameter.private_name] = True
                context.keyword_parameter = None
        else:
            if context.var_kwargs is not None:
                if bool in context.var_kwargs.argument_types and i == len(entries) - 1:
                    context.keyword_arguments[keyword] = True
                else:
                    context.var_kwarg = keyword
            elif bypass_parse:
                context.arguments.append(entry)
            else:
                raise ParsingError(keyword, f"'{keyword}' is not a keyword parameter")

    def _next_keyword_value(
        self,
        context: CommandParameterParser.Context,
        entries: Sequence[str],
        i: int,
    ) -> None:
        assert context.keyword_parameter is not None
        assert isinstance(context.keyword_parameter, CommandParameter)

        entry: str = entries[i]
        if (container_type := context.keyword_parameter.container_type) is not None:
            context.keyword_arguments[context.keyword_parameter.private_name] = (
                add_to_container_type(
                    container_type,
                    context.keyword_arguments.get(
                        context.keyword_parameter.private_name, None
                    ),
                    parse_with_hooks(context.keyword_parameter, entry, self.parsers),
                )
            )
        elif context.keyword_parameter.kind == ParameterKind.VAR_POSITIONAL:
            if len(context.arguments) <= context.var_args_index:
                raise ParsingError(
                    entry,
                    "Cannot provide variable positional argument before positional-only and positional-or-keyword parameters.",
                )
            context.arguments.append(
                parse_with_hooks(context.keyword_parameter, entry, self.parsers)
            )
        else:
            context.keyword_arguments[context.keyword_parameter.private_name] = (
                parse_with_hooks(context.keyword_parameter, entry, self.parsers)
            )

        context.keyword_parameter = None

    def _next_var_kwarg_value(
        self,
        context: CommandParameterParser.Context,
        entries: Sequence[str],
        i: int,
    ) -> None:
        assert context.var_kwarg is not None
        assert context.var_kwargs is not None, (
            "'var_kwarg' may only be not None if 'var_kwargs' is not None"
        )

        entry: str = entries[i]
        if (container_type := context.var_kwargs.container_type) is not None:
            if context.var_kwarg not in context.keyword_arguments:
                context.keyword_arguments[context.var_kwarg] = container_type()
            context.keyword_arguments[context.var_kwarg] = add_to_container_type(
                container_type,
                context.keyword_arguments[context.var_kwarg],
                parse_with_hooks(context.var_kwargs, entry, self.parsers),
            )
        else:
            context.keyword_arguments[context.var_kwarg] = parse_with_hooks(
                context.var_kwargs, entry, self.parsers
            )
        context.var_kwarg = None

    @staticmethod
    def _validate(
        context: CommandParameterParser.Context,
        parameters: Sequence[CommandParameter],
    ) -> None:
        required_positionals: int = 0
        for i, parameter in enumerate(parameters):
            if parameter.kind == ParameterKind.POSITIONAL_ONLY:
                if parameter.default == parameter.empty and len(context.arguments) <= i:
                    raise ParsingError(
                        parameter.name,
                        f"Missing required positional '{parameter.name}'",
                    )
                continue

            if parameter.kind == ParameterKind.POSITIONAL_OR_KEYWORD:
                if parameter.default != parameter.empty:
                    continue
                if len(context.arguments) > i:
                    continue
                if parameter.private_name not in context.keyword_arguments:
                    raise ParsingError(
                        parameter.name,
                        f"Missing required keyword/positional '{parameter.name}'",
                    )
            if parameter.default != parameter.empty or parameter.kind in (
                ParameterKind.VAR_POSITIONAL,
                ParameterKind.VAR_KEYWORD,
            ):
                continue

            if parameter.private_name not in context.keyword_arguments:
                raise ParsingError(
                    parameter.name, f"Missing required keyword '{parameter.name}'"
                )

        if len(context.arguments) < required_positionals:
            raise ParsingError(
                parameters[len(context.arguments)].name,
                f"Missing required positional '{parameters[len(context.arguments)].name}'",
            )

    def parse(
        self, parameters: Sequence[CommandParameter], entries: Sequence[str]
    ) -> tuple[list[Any], dict[str, Any]]:
        context: CommandParameterParser.Context = CommandParameterParser.Context(
            parameters
        )

        for i, entry in enumerate(entries):
            within_bypass: bool = (
                context.var_args is not None
                and context.var_args.bypasses_parsing
                and i >= context.var_args_index
            )

            if entry == self.argument_separator and not within_bypass:
                context.no_keywords = True
                continue

            if not context.no_keywords and entry.startswith(self.keyword_prefix):
                self._next_keyword(context, parameters, within_bypass, entries, i)
                continue

            if context.keyword_parameter is not None:
                self._next_keyword_value(context, entries, i)
                continue

            if context.var_kwarg is not None:
                self._next_var_kwarg_value(context, entries, i)
                continue

            if within_bypass:
                context.arguments.append(entry)
                continue
            elif (
                context.var_args is not None
                and len(context.arguments) > context.var_args_index
            ):
                context.arguments.append(
                    parse_with_hooks(context.var_args, entry, self.parsers)
                )
                continue

            if len(context.arguments) >= len(parameters):
                raise ParsingError(
                    context.arguments[
                        len(parameters)
                        - (1 if len(context.arguments) == len(parameters) else 0)
                    ]
                    if context.arguments
                    else entry,
                    "Too many positional arguments",
                )

            parameter: CommandParameter = parameters[len(context.arguments)]
            if parameter.private_name in context.keyword_arguments:
                raise ParsingError(
                    entry,
                    f"Argument for {parameter.private_name} was supplied positionally and as keyword argument.",
                )

            if parameter.kind in (
                ParameterKind.KEYWORD_ONLY,
                ParameterKind.VAR_KEYWORD,
            ):
                raise ParsingError(
                    context.arguments[len(parameters)], "Too many positional arguments"
                )
            context.arguments.append(parse_with_hooks(parameter, entry, self.parsers))

        if context.keyword_parameter is not None:
            raise MissingKeywordArgumentValueError(
                context.keyword_parameter.name,
                f"'{context.keyword_parameter.name}' is missing a value",
            )
        if context.var_kwarg is not None:
            raise MissingKeywordArgumentValueError(
                context.var_kwarg, f"'{context.var_kwarg}' is missing a value"
            )

        self._validate(context, parameters)
        return context.arguments, context.keyword_arguments


def parse_parameters(
    parameters: Sequence[CommandParameter],
    entries: Sequence[str],
    keyword_prefix: str,
    argument_separator: str,
    parsers: Parsers,
) -> tuple[list[Any], dict[str, Any]]:
    return CommandParameterParser(keyword_prefix, argument_separator, parsers).parse(
        parameters, entries
    )


__all__ = [
    "CommandParameterParser",
    "add_to_container_type",
    "create_enum_parser",
    "create_literal_parser",
    "parse_parameters",
    "parse_with_hooks",
]
