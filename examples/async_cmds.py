import asyncio
import inspect
import shlex
from collections.abc import Callable
from typing import Optional, Any
from npycli import CLI, Command, EmptyEntriesError, CLIError


cli = CLI("async program")


@cli.cmd("do-async-operation")
async def do_async_operation(sleeptime: Optional[float] = None) -> None:
    await asyncio.sleep(sleeptime or 1)
    print("Done!")


@cli.cmd("help")
def help_cmd() -> str:
    return "\n\n".join([cmd.extended_command_help() for cmd in cli.commands])


async def cleanup():
    await asyncio.sleep(1.2)
    return "Done!"


@cli.cmd()
async def quit() -> Callable[[], None]:
    print("Quiting and cleaning up...")
    await cleanup()
    return quit


@cli.retvals()
def retvals(command: Command, return_value: Optional[Any]) -> Optional[Any]:
    print(f"{command} -> {return_value}")
    return command, return_value


async def main() -> None:
    while True:
        try:
            # Asynchronously wait for input in another thread to not block this event loop
            try:
                user_input: str = await asyncio.to_thread(input, cli.prompt_entry_marker)
            except KeyboardInterrupt:
                break

            # retvals handler ensure the return value is this tuple
            command, retval = cli.exec(shlex.split(user_input))
            assert isinstance(command, Command)

            # If the invoked command was a coroutine, await the coroutine and reprocess it in retvals handler
            if inspect.iscoroutine(retval):
                retval = retvals(command, await retval)[1]

            if retval == quit:
                return
        except asyncio.CancelledError as cancellation:
            if cancellation.__cause__ or cancellation.__context__:
                raise
            break
        except EmptyEntriesError:  # If the user entered nothing, just continue
            pass
        except CLIError as err:  # Catch errors that occur between here and execution of command
            print(f'{err.__class__.__name__}: {err.args[0]}')


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ...
