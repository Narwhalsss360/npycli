from typing import Annotated, TextIO

from npycli.errors import CLIError
from npycli.parameters import Alias, CommandParameter, Description
from npycli.parsing import CommandParameterParser

from .. import command as sync_command
from ..abc.cli import CLI
from ..abc.command import (
    Command,
    HelpExtractor,
    ParameterExtractor,
    default_help_extractor,
    default_parameter_extractor,
)


def use_help_command[CommandType: Command](
    cli: CLI,
    name_or_names: str | tuple[str, ...] = "help",
    parameter_extractor: ParameterExtractor = default_parameter_extractor,
    help_extractor: HelpExtractor = default_help_extractor,
    kwarg_prefix: str = CommandParameterParser.DEFAULT_KEYWORD_PREFIX,
    command_cls: type[CommandType] = sync_command.Command,
    line_prefix: str = "",
    commands_joiner: str = "\n",
    print_to: TextIO | None = None,
    print_end: str = "\n",
    print_flush: bool = False,
    single_command_cli: Command | None = None,
) -> CommandType:
    command: CommandType

    def generate_help_for_help() -> str:
        nonlocal command
        return (
            "<...>: Positional or keyword parameter\n"
            "<*...>: Variable positional parameter (variable positional count)\n"
            "<**...>: Variable keyword (variable keyword-value count)\n"
            "/: Positional / Positional only delimiter (Parameters before may not be supplied by keyword-value)\n"
            "<: ...>: Type\n"
            "<: = ...>: Default value\n"
            "[...]: Boolean flag (keyword only)\n"
            f"Keyword prefix: '{cli.kwarg_prefix}'"
        )

    last_kwarg_prefix: str = kwarg_prefix

    def description_command_help(command: Command) -> str:
        return f"{command.name}:\n{command.help or command.basic_command_help()}"

    def description_parameter_help(parameter: CommandParameter) -> str:
        return parameter.description

    def generate_help_string_for(
        command: Command,
        parameter_name: str | None,
        extended: bool,
        description: bool,
        /,
    ) -> str:
        if extended:
            command_help, parameter_help = (
                Command.extended_command_help,
                CommandParameter.extended_parameter_help,
            )
        elif description:
            command_help, parameter_help = (
                description_command_help,
                description_parameter_help,
            )
        else:
            command_help, parameter_help = (
                Command.basic_command_help,
                CommandParameter.basic_parameter_help,
            )

        if parameter_name is None:
            return command_help(command)

        if (parameter := command.find_parameter(parameter_name)) is None:
            raise CLIError(
                f"'{parameter_name}' is not a parameter of the command {command.name}."
            )

        return parameter_help(parameter)

    def generated_help_function(
        _command: Annotated[
            str | None,
            Alias("command", private=True),
            Description(
                "The name of the command to get help for. Do not supply to show help for all commands."
            ),
        ] = None,
        parameter: Annotated[
            str | None,
            Description(
                "The name of the parameter of the specified command to show help for."
            ),
        ] = None,
        /,  # Avoid parameter without command.
        *,
        extended: Annotated[
            bool,
            Description(
                "Show more information about the command(s) or specificed parameter than just signature."
            ),
        ] = False,
        description: Annotated[
            bool,
            Description(
                "Show only the help description of the command. Overriden by 'extended' and ignored for a parameter."
            ),
        ] = False,
    ) -> str:
        nonlocal last_kwarg_prefix
        nonlocal command

        # In the case that CLI.kwarg_prefix gets set, it must be updated here for the help of the help function at least.
        if last_kwarg_prefix != cli.kwarg_prefix:
            object.__setattr__(command, "help", generate_help_for_help())
            last_kwarg_prefix = cli.kwarg_prefix

        output: str
        if _command is None:
            if single_command_cli is not None:
                if len(cli.commands) != 2 or single_command_cli not in cli.commands:
                    raise TypeError(
                        f"The single_command_cli paremeter for {use_help_command.__name__} requires the CLI to have a single command plus the help command."
                    )

                output = generate_help_string_for(
                    single_command_cli, parameter, extended, description
                )
            else:
                output = commands_joiner.join(
                    generate_help_string_for(__command, None, extended, description)
                    for __command in cli.commands
                )
        else:
            if (__command := cli.get_command(_command)) is None:
                raise CLIError(
                    f"The command {_command} does not exist. To list all commands, supply no arguments."
                )
            output = generate_help_string_for(
                __command, parameter, extended, description
            )

        output.replace("\n", f"{line_prefix}\n")
        if print_to:
            print(output, end=print_end, file=print_to, flush=print_flush)
        return output

    names: tuple[str, ...] = (
        name_or_names if isinstance(name_or_names, tuple) else (name_or_names,)
    )
    command = command_cls.create(
        function=generated_help_function,
        names=names,
        help=generate_help_for_help(),
        parameter_extractor=parameter_extractor,
        help_extractor=help_extractor,
        kwarg_prefix=kwarg_prefix,
    )

    cli.add_command(command)
    return command
