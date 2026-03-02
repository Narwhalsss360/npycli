from collections.abc import Callable
from typing import Any
from functools import wraps
from .command import Command, cmd_hook

ALIASES_ATTR = '__kwarg_aliases__'


def attach_kwarg_aliases(func: Callable[..., Any], aliases: dict[str, tuple[str, ...]]) -> Callable[..., Any]:
    setattr(func, ALIASES_ATTR, aliases)
    return func


def get_kwarg_aliases(func: Callable[..., Any]) -> dict[str, tuple[str, ...]]:
    if hasattr(func, ALIASES_ATTR):
        return getattr(func, ALIASES_ATTR)
    return {}


def parse_kwarg_aliases(kwargs: dict[str, Any], aliases: dict[str, tuple[str, ...]]) -> dict[str, Any]:
    parsed_kwargs: dict[str, str] = {}
    for kwarg, value in kwargs.items():
        for original_kwarg, original_kwarg_aliases in aliases.items():
            if kwarg in original_kwarg_aliases or original_kwarg == kwarg:
                parsed_kwargs[original_kwarg] = value
                break
    return parsed_kwargs


def alias_kwargs(aliases: dict[str, tuple[str, ...]]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        attach_kwarg_aliases(func, aliases)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **parse_kwarg_aliases(kwargs, aliases))

        return wrapper

    return decorator


def alias_cmd_kwargs(aliases: dict[str, tuple[str, ...]]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def add_detail(command: Command) -> None:
            for kwarg, kwarg_aliases in aliases.items():
                command.add_detail(f'{kwarg}<->{kwarg_aliases}')
                parameter = next(filter(lambda p: p.name == kwarg, command.parameters), None)
                assert parameter is not None, f"{kwarg} is not a parameter, cannot alias."
                parameter.names = parameter.names + kwarg_aliases

        cmd_hook(func, add_detail)
        attach_kwarg_aliases(func, aliases)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **parse_kwarg_aliases(kwargs, aliases))

        return wrapper

    return decorator
