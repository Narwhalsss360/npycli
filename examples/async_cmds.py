import asyncio
from types import FunctionType
from typing import Any

import npycli
from npycli import CLIError, EmptyEntriesError
from npycli.asyncio.cli import CLI
from npycli.middlewares.help_cmd import create_help_command

cli = CLI("async program")
help_cmd = create_help_command(cli)


@cli.cmd("do-async-operation")
async def do_async_operation(sleeptime: float | None = None) -> None:
    await asyncio.sleep(sleeptime or 1)
    print("Done!")


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
