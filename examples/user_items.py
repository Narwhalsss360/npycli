from types import FrameType, NoneType
from typing import Optional, Any, IO
from os.path import isfile
from math import ceil
import json
from npycli import CLI, Command, CLIError, EmptyEntriesError
from npycli.command import cmd
from npycli.errors import CommandDoesNotExistError
from npycli.kwarg_aliasing import alias_cmd_kwargs
from npycli.parameters import CommandParameter, ParameterKind


USER_ITEMS_FILE = 'user-items.gitignore.json'
TAB_WIDTH: int = 4

cli = CLI('user-items')


def open_user_items_file(mode: str) -> IO:
    return open(USER_ITEMS_FILE, mode, encoding='utf-8')


__items__: Optional[dict[str, str]] = None


def items() -> dict[str, str]:
    global __items__

    if __items__ is not None:
        return __items__

    if isfile(USER_ITEMS_FILE):
        with open_user_items_file('r') as f:
            __items__ = json.loads(f.read())
    else:
        __items__ = {}

    return items()


def commit() -> dict[str, str]:
    if __items__ is None:
        raise RuntimeError('Program error: __items__ should never be None when committing')
    with open_user_items_file('w') as f:
        f.write(json.dumps(__items__, indent=4))
    return __items__


@cli.cmd(names=('add', 'new'), help='Add a new key-value pair.')
@alias_cmd_kwargs({'key': ('k',), 'value': ('v',)})
def add_cmd(key: str, value: str) -> str:
    if key in items():
        raise KeyError(f'Key {key} already exists.')
    items()[key] = value
    commit()
    return f'{key}:{value}'


@cli.cmd(names=('set', 'change'), help='Change an the existing value of a key.')
@alias_cmd_kwargs({'key': ('k',), 'value': ('v',)})
def set_cmd(key: str, value: str) -> str:
    if key not in items():
        raise KeyError(f'Key {key} does not exist. Use {cmd(add_cmd).name}.')
    items()[key] = value
    commit()
    return f'{key}:{value}'


@cli.cmd(names=('delete', 'del', 'remove', 'rm'), help='Delete an existing key-value pair.')
@alias_cmd_kwargs({'key': ('k',)})
def delete_cmd(key: str) -> str:
    value: str = items().pop(key)
    commit()
    return f'Deleted:\n{key}:{value}'


@cli.cmd(names=('show', 'print'), help='Show a specific or all existing key-value pair(s).')
@alias_cmd_kwargs({'key': ('k',)})
def show_cmd(key: Optional[str] = None) -> str:
    if key is None:
        longest_length: int = max(len(s) for s in items().keys())
        tab_count: int = ceil(longest_length / TAB_WIDTH)
        result: str = ''
        for k, v in items().items():
            result += f'{k: <{tab_count * TAB_WIDTH}}:{v}\n'
        return result
    else:
        return f'{key}:{items()[key]}'


@cli.cmd(name='help', help='Show help for a command or all commands.')
def help_cmd(
    command_name: Optional[str] = None,
    parameter_name: Optional[str] = None,
    /,
    extended: bool = False
) -> str:
    def type_name(t: type) -> str:
        if t == NoneType:
            return str(None)
        return t.__name__

    def annotation_preview(parameter: CommandParameter) -> str:
        if parameter.annotation_preview:
            return parameter.annotation_preview
        out: str = ""
        for i, t in enumerate(parameter.argument_types):
            out += type_name(t)
            if i != len(parameter.argument_types) - 1:
                out += " | "
        return out

    def default_preview(parameter: CommandParameter) -> str | None:
        if parameter.default == parameter.empty:
            return None
        if parameter.default_preview:
            return parameter.default_preview
        return repr(parameter.default)

    def basic_parameter_help(parameter: CommandParameter) -> str:
        if (
            parameter.default != parameter.empty and
            parameter.argument_types[0] == bool and
            parameter.kind in (ParameterKind.POSITIONAL_OR_KEYWORD, ParameterKind.KEYWORD_ONLY)
        ):
            return (
                "["
                    f"{parameter.name}: "
                    f"{annotation_preview(parameter)} = {default_preview(parameter)}"
                "]"
            )
        else:
            return (
                "<"
                f"{"*" if parameter.kind == ParameterKind.VAR_POSITIONAL else ""}"
                f"{"**" if parameter.kind == ParameterKind.VAR_KEYWORD else ""}"
                f"{parameter.name}: "
                f"{annotation_preview(parameter)}"
                f"{"" if (default := default_preview(parameter)) is None else f" = {default}"}"
                ">"
            )

    def extended_parameter_help(parameter: CommandParameter) -> str:
        tabstr = " " * TAB_WIDTH
        out = tabstr
        for i, name in enumerate(parameter.names):
            out += name
            if i != len(parameter.names) - 1:
                out += " "
        out += "\n"

        tabstr = " " * TAB_WIDTH * 2
        out += f"{tabstr}Kind: {parameter.kind.name}\n"
        out += f"{tabstr}Annotation: {annotation_preview(parameter)}\n"

        out += f"{tabstr}Types:\n"
        for i, t in enumerate(parameter.argument_types):
            out += f"{tabstr}{" " * TAB_WIDTH}{type_name(t)}"
            if i != len(parameter.argument_types) - 1:
                out += "\n"

        if (default := default_preview(parameter)) is not None:
            out += f"\n{tabstr}Default: {default}"

        if parameter.parse_hooks is not None:
            out += f"\n{tabstr}Parse Hooks:"
            if parameter.parse_hooks.pre is not None:
                out += f"{tabstr}{" " * TAB_WIDTH}Pre-Hook: {getattr(parameter.parse_hooks.pre, "__name__", "...")}"
            if parameter.parse_hooks.post is not None:
                out += f"{tabstr}{" " * TAB_WIDTH}Post-Hook: {getattr(parameter.parse_hooks.post, "__name__", "...")}"
            if parameter.parse_hooks.err is not None:
                out += f"{tabstr}{" " * TAB_WIDTH}Error-Hook: {getattr(parameter.parse_hooks.err, "__name__", "...")}"

        if parameter.description:
            out += f"{tabstr}Description: {parameter.description.replace("\n", f"\n{tabstr}")}"

        return out

    def basic_command_help(command: Command) -> str:
        out: str = f"{command.name} "
        last_positional_only_index: int = -1
        for i, parameter in enumerate(command.parameters):
            if parameter.kind == ParameterKind.POSITIONAL_ONLY:
                last_positional_only_index = i
            else:
                break

        for i, parameter in enumerate(command.parameters):
            out += basic_parameter_help(parameter)
            if i == last_positional_only_index:
                out += " /"
            if i != len(command.parameters) - 1:
                out += " "
        return out

    def extended_command_help(command: Command) -> str:
        out: str = ""
        for i, name in enumerate(command.names):
            out += name
            if i != len(command.names) - 1:
                out += " "
        out += "\n"

        out += "Parameters:\n"
        for i, parameter in enumerate(command.parameters):
            out += extended_parameter_help(parameter)
            if i != len(command.parameters) - 1:
                out += "\n"

        return out

    command_help, parameter_help = (extended_command_help, extended_parameter_help) if extended else (basic_command_help, basic_parameter_help)

    if command_name is None:
        out: str = ""
        for i, command in enumerate(cli.commands):
            out += f"{command_help(command)}"
            if i != len(cli.commands) - 1:
                out += "\n"
        return out

    if (command := cli.get_command(command_name)) is None:
        return f"{command_name} is not a command."

    if parameter_name is not None:
        if (parameter := next(filter(lambda p: parameter_name in p.names, command.parameters)), None) is None:
            return f"'{parameter_name}' is not a parameter"
        return parameter_help(parameter)
    return command_help(command)


@cli.retvals()
def retvals(command: Command, return_value: Optional[Any]) -> None:
    if return_value is None:
        return
    print(f'{command.name}:\n{return_value}')


@cli.errors()
def errors(command: Command, exc: Exception) -> None:
    print(f'{command.name} error: {exc}')


def as_prompter() -> None:
    print('Program style: as_prompter')
    while True:
        try:
            cli.prompt()
        except KeyboardInterrupt:
            print("\n^C")
            return
        except EmptyEntriesError:  # If the user entered nothing, just continue
            pass
        except CLIError as err:  # Catch errors that occur between here and execution of command
            print(f'{err.__class__.__name__}: {err.args[0]}')


def as_cli_program() -> None:
    print('Program style: as_cli_program')
    from sys import argv
    try:
        cli.exec(argv[1:])
    except EmptyEntriesError:  # If the user entered nothing, just continue
        pass
    except CLIError as err:  # Catch errors that occur between here and execution of command
        print(f'{err.__class__.__name__}: {err.args[0]}')


if __name__ == '__main__':
    from inspect import currentframe, getframeinfo

    print(
        f'Comment/uncomment a function below (line {getframeinfo(currentframe() or FrameType()).lineno}) to use to select the style of program.',
        end='')

    # This function will use the arguments passed into `argv` as arguments.
    # as_cli_program()

    # This function will use a `while true` loop to prompt the user with text entry.
    as_prompter()
