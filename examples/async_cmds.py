import asyncio
from types import FunctionType
from typing import Any

import npycli
from npycli import CLIError, EmptyEntriesError
from npycli.asyncio.cli import CLI
from npycli.parameters import CommandParameter

cli = CLI("async program")


@cli.cmd("do-async-operation")
async def do_async_operation(sleeptime: float | None = None) -> None:
    await asyncio.sleep(sleeptime or 1)
    print("Done!")


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
        f"Keyword prefix: '{cli.kwarg_prefix}'"
    ),
)
def help_cmd(
    command_name: str | None = None,
    parameter_name: str | None = None,
    /,
    *,
    extended: bool = False,
) -> str:
    if extended:
        command_help, parameter_help = (
            npycli.abc.command.Command.extended_command_help,
            CommandParameter.extended_parameter_help,
        )
    else:
        command_help, parameter_help = (
            npycli.abc.command.Command.basic_command_help,
            CommandParameter.basic_parameter_help,
        )

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
        if (
            parameter := next(
                filter(lambda p: parameter_name in p.names, command.parameters), None
            )
        ) is None:
            return f"'{parameter_name}' is not a parameter"
        return parameter_help(parameter)

    return command_help(command)


async def cleanup():
    await asyncio.sleep(1.2)
    return "Done!"


@cli.cmd()
async def quit() -> FunctionType:
    print("Quiting and cleaning up...")
    await cleanup()
    return quit


@cli.retvals()
async def retvals(command: npycli.abc.Command, return_value: Any | None) -> Any | None:
    print(f"{command} ->\n{return_value}")
    return return_value


async def main() -> None:
    await cli
    while True:
        try:
            return_value: Any = await cli.prompt()
            if return_value is quit:
                break
        except KeyboardInterrupt:
            break
        except asyncio.CancelledError as cancellation:
            if cancellation.__cause__ or cancellation.__context__:
                raise
            break
        except EmptyEntriesError:
            continue
        except CLIError as err:
            print(f"{err.__class__.__name__}: {err.args[0]}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
