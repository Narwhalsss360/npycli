from types import FrameType
from typing import Optional, Any, IO
from os.path import isfile
from math import ceil
import json
from npycli import CLI, Command, CLIError, EmptyEntriesError
from npycli.command import cmd
from npycli.kwarg_aliasing import alias_cmd_kwargs
from npycli.parameters import CommandParameter


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


@cli.cmd(
    name='help',
    help=(
        "<...>: Positional or Keyword\n"
        "<*...>: Variable Positional\n"
        "<**...>: Variable Keyword\n"
        "/: Positional / Keyword Only Delimiter\n"
        "<: ...>: Type\n"
        "<: = ...>: Default Value\n"
        "[...]: Boolean Flag (Keyword only, no value needed)\n"
    )
)
def help_cmd(
    command_name: Optional[str] = None,
    parameter_name: Optional[str] = None,
    /,
    extended: bool = False
) -> str:
    if extended:
        command_help, parameter_help = Command.extended_command_help, CommandParameter.extended_parameter_help
    else:
        command_help, parameter_help = Command.basic_command_help, CommandParameter.basic_parameter_help

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
def retvals(command: Command, return_value: Optional[Any]) -> Optional[Any]:
    if return_value is None:
        return
    print(f'{command.name}:\n{return_value}')


@cli.errors()
def errors(command: Command, exc: Exception) -> Optional[Any]:
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
