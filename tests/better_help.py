from types import NoneType
from typing import Annotated

from npycli import CLI, Command, CommandDoesNotExistError, EmptyEntriesError
from npycli.kwarg_aliasing import alias_cmd_kwargs
from npycli.parameters import CommandParameter

TAB_CHARS: str = " " * 4


cli = CLI(title="user-items", prompt_marker="->", env={"user-items": {}})


def __log_out__(text: str) -> None:
    with open(f"{__name__}.log", "a+", encoding="utf-8") as log_file:
        log_file.write(text)


def user_items() -> dict[str, str]:
    return cli.env["user-items"]


@cli.cmd(name="add")
@alias_cmd_kwargs({"key": ("k",), "value": ("v",)})
def add_item(key: str, value: str) -> str:
    if key in user_items():
        return f"Key {key} already exists"
    user_items()[key] = value
    return f"Added {key}: {value}"


@cli.cmd(name="change")
def change_item(key: str, value: str) -> str:
    if key not in user_items():
        return f"Key {key} does not exist"
    old_value: str = user_items()[key]
    user_items()[key] = value
    return f"Swapped value of {key} from {old_value} for {value}"


@cli.cmd(name="show")
def show_item(key: str | None = None) -> str:
    if key is None:
        s = ""
        for k, v in user_items().items():
            s += f"{k}: {v}\n"
        return s
    if key not in user_items():
        return f"Key {key} does not exist"
    return f"{key}: {user_items()[key]}"


@cli.cmd(names=("delete", "del", "remove", "rm", "pop"))
def delete_item(key: str) -> str:
    if key not in user_items():
        return f"Key {key} does not exist"
    return f"Popped {key}: {user_items().pop(key)}"


@cli.cmd(
    name="help",
    help=(
        "<...>: Positional or Keyword\n"
        "<*...>: Variable Positional\n"
        "<**...>: Variable Keyword\n"
        "/: Positional / Keyword Only Delimiter\n"
        "<: ...>: Type\n"
        "<: = ...>: Default Value\n"
        "[...]: Boolean Flag (Keyword only, no value needed)\n"
    ),
)
def help_cmd(
    command_name: str | None = None,
    parameter_name: str | None = None,
    /,
    extended: bool = False,
) -> str:
    if extended:
        command_help, parameter_help = (
            Command.extended_command_help,
            CommandParameter.extended_parameter_help,
        )
    else:
        command_help, parameter_help = (
            Command.basic_command_help,
            CommandParameter.basic_parameter_help,
        )

    if command_name is None:
        return "\n".join(command_help(command) for command in cli.commands)

    if (command := cli.get_command(command_name)) is None:
        return f"{command_name} is not a command."

    if parameter_name is not None:
        if (
            parameter := next(
                filter(lambda p: parameter_name in p.names, command.parameters), None
            )
        ) is None:
            return f"'{parameter_name}' is not a parameter"
        return parameter_help(parameter)

    return command_help(command)


@cli.retvals()
def retvals(command: Command, retval: str) -> None:
    __log_out__(f"{command.name}:\n{retval}\n")
    print(retval)


@cli.errors()
def errors(command: Command | None, exception: Exception) -> None:
    print(
        f"Exception {exception.__class__.__name__} thrown: {exception} | {exception.args} - {f' Running command {command.name}' if command is not None else ''}"
    )


def main() -> None:
    while True:
        try:
            cli.prompt()
        except CommandDoesNotExistError as cmd_error:
            print(cmd_error.args[0])
        except EmptyEntriesError:
            ...
        except KeyboardInterrupt:
            print("\n^C")
            break


if __name__ == "__main__":
    main()
