from types import NoneType
from typing import Annotated, Optional
from npycli import CLI, Command, EmptyEntriesError, CommandDoesNotExistError
from npycli.kwarg_aliasing import alias_cmd_kwargs
from npycli.parameters import CommandParameter, Description


TAB_CHARS: str = " " * 4


cli = CLI(title='user-items', prompt_marker='->', env={'user-items': {}})


def __log_out__(text: str) -> None:
    with open(f'{__name__}.log', 'a+', encoding='utf-8') as log_file:
        log_file.write(text)


def user_items() -> dict[str, str]:
    return cli.env['user-items']


@cli.cmd(name='add')
@alias_cmd_kwargs({'key': ('k',), 'value': ('v',)})
def add_item(key: str, value: str) -> str:
    if key in user_items():
        return f'Key {key} already exists'
    user_items()[key] = value
    return f'Added {key}: {value}'


@cli.cmd(name='change')
def change_item(key: str, value: str) -> str:
    if key not in user_items():
        return f'Key {key} does not exist'
    old_value: str = user_items()[key]
    user_items()[key] = value
    return f'Swapped value of {key} from {old_value} for {value}'


@cli.cmd(name='show')
def show_item(key: Optional[str] = None) -> str:
    if key is None:
        s = ''
        for k, v in user_items().items():
            s += f'{k}: {v}\n'
        return s
    if key not in user_items():
        return f'Key {key} does not exist'
    return f'{key}: {user_items()[key]}'


@cli.cmd(names=('delete', 'del', 'remove', 'rm', 'pop'))
def delete_item(key: str) -> str:
    if key not in user_items():
        return f'Key {key} does not exist'
    return f'Popped {key}: {user_items().pop(key)}'


@cli.cmd(name='help')
def show_help(
    command_name: str | None = None,
    parameter_name: Annotated[str | None, Description("Show help of a specific command parameter")] = None,
    /,
    extended: bool = False
) -> str:
    if command_name is None:
        names: list[str] = []
        longest_name_length: int = 0
        descriptions: list[str] = []
        for command in cli.commands:
            if len(command.name) > longest_name_length:
                longest_name_length = len(command.name)
            names.append(command.name)
            descriptions.append(command.details or "")

        name_fmt = f"<{longest_name_length + 2}"

        help_str = ''
        for name, description in zip(names, descriptions):
            help_str += f"{format(name, name_fmt)}| {description}\n"
        help_str += "Send KeyboardInterrupt (SIGINT), CTRL+C to exit"
        return help_str

    if (command := cli.get_command(command_name)) is None:
        return f"'{command_name}' is not a command."

    out: str = ""
    for i, name in enumerate(command.names):
        out += name
        if i != len(command.names) - 1:
            out += " "
    out += "\n"

    def parameter_details(parameter: CommandParameter) -> str:
        out: str = ""
        for i, name in enumerate(parameter.names):
            out += name
            if i == len(parameter.names) - 1:
                out += " ->"
            out += " "

        for i, t in enumerate(parameter.argument_types):
            out += str(None) if t == NoneType else t.__name__
            if i != len(parameter.argument_types) - 1:
                out += " "

        out += f"\nKind: {parameter.kind.name}\n"
        if parameter.default_preview:
            out += f"Default: {parameter.default_preview}"
        elif parameter.default != parameter.empty:
            out += f"Default: {repr(parameter.default)}"

        if parameter.description:
            out += f"\n{parameter.description}"
        return out

    if parameter_name is None:
        if extended:
            for i, parameter in enumerate(command.parameters):
                out += parameter_details(parameter).replace("\n", f"\n{TAB_CHARS}")
                if i != len(command.parameters) - 1:
                    out += "\n"

        else:
            for i, parameter in enumerate(command.parameters):
                out += f"{TAB_CHARS}{parameter.name}: {"".join(f"{str(None) if t == NoneType else t.__name__} " for t in parameter.argument_types)} {parameter.description}"
                if i != len(command.parameters) - 1:
                    out += "\n"
        return out

    if (parameter := next(filter(lambda p: parameter_name in p.names, command.parameters), None)) is None:
        return f"'{parameter_name}' is not a parameter of '{command_name}'"

    return f"{out}{parameter_details(parameter)}"


@cli.retvals()
def retvals(command: Command, retval: str) -> None:
    __log_out__(f'{command.name}:\n{retval}\n')
    print(retval)


@cli.errors()
def errors(command: Optional[Command], exception: Exception) -> None:
    print(
        f'Exception {exception.__class__.__name__} thrown: {exception} | {exception.args} - {f" Running command {command.name}" if command is not None else ""}')


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


if __name__ == '__main__':
    main()

