import builtins
from collections.abc import Callable
from types import UnionType
from typing import Optional, Any, get_args, Type, TypeAliasType, get_origin, Literal
from itertools import zip_longest
from enum import Enum
from .errors import MissingKeywordArgumentValueError, ParsingError, TooManyArgumentsError


def type_from_annotation(annotation: str) -> type:
    args = get_args(annotation)
    if args:
        annotation = args[0]

    if isinstance(annotation, type):
        return annotation

    try:
        return getattr(builtins, annotation)
    except AttributeError:
        if (t := globals().get(annotation)):
            return t
    raise TypeError(f"Type {annotation} not found.")


def extract_positionals_keywords(args: list[str], kwarg_prefix: Optional[str] = None) -> \
        tuple[list[str], dict[str, str]]:
    kwarg_prefix = kwarg_prefix or '--'
    positionals: list[str] = []
    keywords: dict[str, str] = {}

    kwarg: Optional[str] = None
    for arg in args:
        if kwarg is not None:
            keywords[kwarg] = arg
            kwarg = None
            continue
        elif arg.startswith(kwarg_prefix):
            kwarg = arg[len(kwarg_prefix):]
            continue
        else:
            positionals.append(arg)

    if kwarg is not None:
        raise MissingKeywordArgumentValueError(f'Keyword missing value. Usage: {kwarg_prefix}{kwarg}.')

    return positionals, keywords


def parse_args_as(positionals: list[str], keywords: dict[str, str], positional_types: list[type],
                  keyword_types: dict[str, type], var_args_index: Optional[int] = None,
                  var_args_parser: Optional[type | Callable[[str], Any]] = None,
                  parsers: Optional[dict[type, Callable[[str], Any]]] = None) -> tuple[list[Any], dict[str, Any]]:
    parsers = parsers or {}
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    if var_args_index is None:
        var_args_index = len(positionals)
        assert var_args_index is not None

    for index, (arg_type, arg) in enumerate(zip_longest(positional_types, positionals)):
        # Did not enter all positionals, but they may be optional so stop.
        if arg is None:
            break

        # Args are now variable args
        if arg_type is None or var_args_index <= index:  # pyright: ignore[reportUnnecessaryComparison]
            if var_args_parser is None:
                raise TooManyArgumentsError(
                    f'Entered {len(positionals)} positionals, but max is {len(positional_types)}.')
            try:
                args.append(var_args_parser(arg))
            except ParsingError as parsing_error:
                raise parsing_error
            except Exception as exc:
                raise ParsingError(f"An error ({repr(exc)}) occurred parsing '{arg}' as {arg_type}.") from exc
            continue

        try:
            args.append(parsers[arg_type](arg) if arg_type in parsers else arg_type(arg))
        except ParsingError as parsing_error:
            raise parsing_error
        except Exception as exc:
            raise ParsingError(f"An error ({repr(exc)}) occurred parsing '{arg}' as {arg_type}.") from exc

    for kwarg, arg in keywords.items():
        arg_type: type = keyword_types.get(kwarg, str)
        try:
            kwargs[kwarg] = parsers[arg_type](arg) if arg_type in parsers else arg_type(arg)
        except ParsingError as parsing_error:
            raise parsing_error
        except Exception as exc:
            raise ParsingError(f"An error ({repr(exc)}) occurred parsing '{arg}' as {arg_type}.") from exc

    return args, kwargs


def create_literal_parser(literal_type: TypeAliasType | UnionType) -> Callable[[str], Any]:
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
        raise ValueError(f"{s} was not one of {repr(get_args(literal_type))}")
    return parser


def create_enum_parser[T](enum_type: Type[T]) -> Callable[[str], T]:
    assert issubclass(enum_type, Enum)

    def parser(s: str) -> T:
        try:
            return enum_type(s)
        except ValueError:
            return enum_type[s]

    return parser


__all__ = [
    "type_from_annotation",
    "extract_positionals_keywords",
    "parse_args_as",
    "create_literal_parser",
]
