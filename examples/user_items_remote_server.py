from dataclasses import asdict, dataclass
from typing import Any
from json import dumps, loads
from sys import stderr
from asyncio import AbstractEventLoop, CancelledError, get_event_loop, run, wait_for
from socket import socket, AddressFamily, SocketKind, IPPROTO_TCP
from enum import Enum
from user_items import cli, EmptyEntriesError, CLIError, Command


REMOTE_PORT: int = 43781
STOP_SERVER_SENTINEL: object = object()
NEWLINE_DELIMITER: bytes = b'\n'


@dataclass
class RemoteInitialization:
    stdout_isatty: bool
    stderr_isatty: bool


@dataclass
class UserInputRequest:
    prompt: str


@dataclass
class UserInput:
    args: list[str]


class OutputDirection(str, Enum):
    stdout = "stdout"
    stderr = "stderr"


@dataclass
class Output:
    direction: OutputDirection
    output: str


@cli.cmd()
def stop_server() -> Any:
    return STOP_SERVER_SENTINEL


async def recv_line(sock: socket) -> bytearray:
    received: bytearray = bytearray()
    loop: AbstractEventLoop = get_event_loop()

    while True:
        b: bytes = await loop.sock_recv(sock, 1)
        if not b:
            raise EOFError()

        if b[0] == ord('\n'):
            break
        received.append(b[0])

    return received


STEP_TIMEOUT: float = 3


async def remote_cli_server() -> None:
    cli.env["retvals cmd and retval"] = True
    loop: AbstractEventLoop = get_event_loop()
    with socket(AddressFamily.AF_INET, SocketKind.SOCK_STREAM, IPPROTO_TCP) as listener:
        listener.setblocking(False)
        listener.bind(("127.0.0.1", REMOTE_PORT))
        listener.listen(1)

        while True:
            client, client_addr = await loop.sock_accept(listener)
            print(f"[INFO] {client_addr=} connected.")

            try:
                initialization_json: str = (await wait_for(recv_line(client), timeout=STEP_TIMEOUT)).decode()
            except EOFError:
                print("[INFO] Disconnected", file=stderr)
                client.close()
                continue
            except TimeoutError:
                print("Timed our waiting for initialization", file=stderr)
                continue

            try:
                initialization: RemoteInitialization = RemoteInitialization(**loads(initialization_json))
            except TypeError as e:
                print(e, file=stderr)
                client.close()
                continue
            print(">", initialization)

            response: Any = UserInputRequest(prompt=cli.prompt_entry_marker)
            client.send(dumps(asdict(response)).encode() + NEWLINE_DELIMITER)
            print("<", response)

            try:
                user_input_json: str = (await wait_for(recv_line(client), timeout=STEP_TIMEOUT)).decode()
            except EOFError:
                print("[INFO] Disconnected", file=stderr)
                client.close()
                continue
            except TimeoutError:
                print("Timed our waiting for user input", file=stderr)
                continue

            try:
                user_input: UserInput = UserInput(**loads(user_input_json))
            except TypeError as e:
                print(e, file=stderr)
                client.close()
                continue

            return_value: Any = None
            try:
                retval_unsafe: Any = cli.exec(user_input.args)
                assert isinstance(retval_unsafe, tuple)
                assert len(retval_unsafe) == 2
                assert isinstance(retval_unsafe[0], Command)
                command: Command = retval_unsafe[0]
                return_value = retval_unsafe[1]
                response = Output(
                    OutputDirection.stdout,
                    f"{command.name}:\n{return_value}"
                )
                client.send(dumps(asdict(response)).encode() + NEWLINE_DELIMITER)
                print("<", response)
            except CancelledError:
                print("\n^C", file=stderr)
                return
            except EmptyEntriesError as err:
                response = Output(
                    OutputDirection.stderr,
                    f"{err.__class__.__name__}: {err.args[0]}"
                )
                print("<", response, file=stderr)
                client.send(dumps(asdict(response)).encode() + NEWLINE_DELIMITER)

            except CLIError as err:
                response = Output(
                    OutputDirection.stderr,
                    f"{err.__class__.__name__}: {err.args[0]}"
                )
                print("<", response, file=stderr)
                client.send(dumps(asdict(response)).encode() + NEWLINE_DELIMITER)
            finally:
                client.close()
                if return_value is STOP_SERVER_SENTINEL:
                    break


if __name__ == "__main__":
    try:
        run(remote_cli_server())
    except (KeyboardInterrupt, CancelledError):
        print("\n^C", file=stderr)

