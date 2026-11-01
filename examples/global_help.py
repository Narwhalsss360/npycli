from shlex import split
from sys import argv
from typing import Any

from npycli.cli import CLI
from npycli.command import Command
from npycli.errors import CLIError, EmptyEntriesError
from npycli.parameters import BypassParse, ParameterKind


def create_global_help_command(cli: CLI, help_cmd_name: str = "help") -> Command:
    if (help_cmd := cli.get_command(help_cmd_name)) is None:
        raise RuntimeError(
            f"The command named '{help_cmd_name}' must exist in the CLI prior to creation."
        )

    help_num_positionals: int = sum(
        1
        for parameter in help_cmd.parameters
        if parameter.kind
        in (
            ParameterKind.POSITIONAL_ONLY,
            ParameterKind.POSITIONAL_ONLY,
            ParameterKind.VAR_POSITIONAL,
        )
    )

    def global_help_hook(*entries: BypassParse, help: bool = False) -> Any:
        if help:
            return cli.exec(
                [
                    "help",
                    *(
                        entry
                        for entry in entries[: max(help_num_positionals, len(entries))]
                        if not entry.startswith(cli.kwarg_prefix)
                    ),
                ]
            )
        return cli.exec(list(entries))

    return Command.create(
        global_help_hook,
        "global_help_hook",
        help="A function that bypasses parsing except for help bool flag to see help for any command.",
        kwarg_prefix=cli.kwarg_prefix,
    )


from user_items import (
    cli,
)  # This uses the cli of another example, since this is meant to "middleware" to a CLI.


def program_style_switch(*entries: BypassParse, prompter: bool = False) -> Any:
    command = create_global_help_command(cli)

    try:
        if prompter:
            if len(entries) > 1:
                command.exec_with(list(entries))

            while True:
                command.exec_with(split(input(f"{cli.title}{cli.prompt_marker}")))
        else:
            command.exec_with(list(entries))
    except KeyboardInterrupt:
        print("\n^C")
        return
    except EmptyEntriesError:
        pass
    except CLIError as err:
        print(f"{err.__class__.__name__}: {err.args[0]}")


def main() -> None:
    entry_command = Command.create(
        program_style_switch,
        "program_style_switch",
        help=f"Switches from prompter style/cli style where, as prompter, this process doesn't end as soon as the command is finished, and as cli it does. Just pass the {cli.kwarg_prefix}prompter flag, else CLI by default.",
        kwarg_prefix=cli.kwarg_prefix,
    )

    if len(argv) == 1:
        print(entry_command.extended_command_help())
        return

    entry_command.exec_with(argv[1:])


if __name__ == "__main__":
    main()
