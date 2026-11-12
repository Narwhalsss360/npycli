import json
from math import ceil
from os.path import isfile
from types import FrameType
from typing import IO, Annotated, Any

from npycli import CLI, CLIError, EmptyEntriesError
from npycli.abc import command as abccommand
from npycli.command import Command, cmd
from npycli.errors import causes
from npycli.middlewares.help_cmd import use_help_command
from npycli.parameters import Alias

USER_ITEMS_FILE = "user-items.gitignore.json"
TAB_WIDTH: int = 4

cli = CLI("user-items")
help_cmd: Command = use_help_command(cli)


def open_user_items_file(mode: str) -> IO[Any]:
    return open(USER_ITEMS_FILE, mode, encoding="utf-8")


__items__: dict[str, str] | None = None


def items() -> dict[str, str]:
    global __items__

    if __items__ is not None:
        return __items__

    if isfile(USER_ITEMS_FILE):
        with open_user_items_file("r") as f:
            __items__ = json.loads(f.read())
    else:
        __items__ = {}

    return items()


def commit() -> dict[str, str]:
    if __items__ is None:
        raise RuntimeError(
            "Program error: __items__ should never be None when committing"
        )
    with open_user_items_file("w") as f:
        f.write(json.dumps(__items__, indent=4))
    return __items__


@cli.cmd(names=("add", "new"), help="Add a new key-value pair.")
def add_cmd(key: Annotated[str, Alias("k")], value: Annotated[str, Alias("v")]) -> str:
    if key in items():
        raise KeyError(f"Key {key} already exists.")
    items()[key] = value
    commit()
    return f"{key}:{value}"


@cli.cmd(names=("set", "change"), help="Change an the existing value of a key.")
def set_cmd(key: Annotated[str, Alias("k")], value: Annotated[str, Alias("v")]) -> str:
    if key not in items():
        raise KeyError(f"Key {key} does not exist. Use {cmd(add_cmd).name}.")
    items()[key] = value
    commit()
    return f"{key}:{value}"


@cli.cmd(
    names=("delete", "del", "remove", "rm"), help="Delete an existing key-value pair."
)
def delete_cmd(key: Annotated[str, Alias("k")]) -> str:
    value: str = items().pop(key)
    commit()
    return f"Deleted:\n{key}:{value}"


@cli.cmd(
    names=("show", "print"), help="Show a specific or all existing key-value pair(s)."
)
def show_cmd(key: Annotated[str | None, Alias("k")] = None) -> str:
    if key is None:
        longest_length: int = max(len(s) for s in items())
        tab_count: int = ceil(longest_length / TAB_WIDTH)
        result: str = ""
        for k, v in items().items():
            result += f"{k + ':': <{tab_count * TAB_WIDTH}}{v}\n"
        return result
    else:
        return f"{key}:{items()[key]}"


@cli.retvals()
def retvals(command: abccommand.Command, return_value: Any | None) -> Any | None:
    if return_value is None:
        return
    print(f"{command.name}:\n{return_value}")


@cli.errors()
def errors(command: abccommand.Command, exc: Exception) -> Any | None:
    errors_string: str = "\n".join(
        [f"{' ' * TAB_WIDTH}{e.__class__.__name__}: {e}" for e in causes(exc, True)]
    )
    print(f"{command.name} error:\n{errors_string}")
    return None


def as_prompter() -> None:
    print("Program style: as_prompter")
    while True:
        try:
            cli.prompt()
        except KeyboardInterrupt:
            print("\n^C")
            return
        except EmptyEntriesError:  # If the user entered nothing, just continue
            pass
        except (
            CLIError
        ) as err:  # Catch errors that occur between here and execution of command
            print(f"{err.__class__.__name__}: {err.args[0]}")


def as_cli_program() -> None:
    print("Program style: as_cli_program")
    from sys import argv

    try:
        cli.exec(argv[1:])
    except EmptyEntriesError:  # If the user entered nothing, just continue
        pass
    except (
        CLIError
    ) as err:  # Catch errors that occur between here and execution of command
        print(f"{err.__class__.__name__}: {err.args[0]}")


if __name__ == "__main__":
    from inspect import currentframe, getframeinfo

    print(
        f"Comment/uncomment a function below (line {getframeinfo(currentframe() or FrameType()).lineno}) to use to select the style of program.",
        end="",
    )

    # This function will use the arguments passed into `argv` as arguments.
    # as_cli_program()

    # This function will use a `while true` loop to prompt the user with text entry.
    as_prompter()
