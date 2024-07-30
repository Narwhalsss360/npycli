import builtins
from typing import Optional, Any, Callable, get_args
from itertools import zip_longest
from .errors import MissingKeywordArgumentValueError, TooManyArgumentsError


def type_from_annotation(annotation: str) -> type | None:
    args = get_args(annotation)
    if args:
        annotation = args[0]

    if isinstance(annotation, type):
        return annotation

    try:
        return getattr(builtins, annotation)
    except AttributeError:
        try:
            t = globals()[annotation]
        except KeyError:
            return None
        return t if isinstance(t, type) else None


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
                  keyword_types: dict[str, type], var_args_parser: Optional[type] = None,
                  parsers: Optional[dict[type, Callable[[str], Any]]] = None) -> tuple[list[Any], dict[str, Any]]:
    parsers = parsers or {}
    args: list[Any] = []
    kwargs: dict[str, Any] = {}

    for arg_type, arg in zip_longest(positional_types, positionals):
        # Did not enter all positionals, but they may be optional so stop.
        if arg is None:
            break
        # Args are now variable args
        if arg_type is None:
            if var_args_parser is None:
                raise TooManyArgumentsError(
                    f'Entered {len(positionals)} positionals, but max is {len(positional_types)}.')
            args.append(var_args_parser(arg))
            continue
        args.append(parsers[arg_type](arg) if arg_type in parsers else arg_type(arg))

    for kwarg, arg in keywords.items():
        arg_type: type = keyword_types.get(kwarg, str)
        kwargs[kwarg] = parsers[arg_type](arg) if arg_type in parsers else arg_type(arg)

    return args, kwargs
