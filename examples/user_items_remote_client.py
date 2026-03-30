from sys import argv, stdout, stderr
from dataclasses import asdict
from asyncio import AbstractEventLoop, get_event_loop, run
from json import loads, dumps
from socket import socket, AddressFamily, SocketKind, IPPROTO_TCP
from user_items_remote_server import REMOTE_PORT, NEWLINE_DELIMITER, Output, OutputDirection, UserInput, RemoteInitialization, UserInputRequest, recv_line


async def main() -> int:
    loop: AbstractEventLoop = get_event_loop()
    with socket(AddressFamily.AF_INET, SocketKind.SOCK_STREAM, IPPROTO_TCP) as client:
        client.setblocking(False)
        await loop.sock_connect(client, ("127.0.0.1", REMOTE_PORT))

        client.send(dumps(asdict(RemoteInitialization(
            stdout_isatty=stdout.isatty(),
            stderr_isatty=stderr.isatty()
        ))).encode() + NEWLINE_DELIMITER)

        try:
            user_input_request_json: str = (await recv_line(client)).decode()
        except EOFError:
            print("Disconnected", file=stderr)
            return 1

        try:
            user_input_request: UserInputRequest = UserInputRequest(**loads(user_input_request_json))
        except TypeError as e:
            print(e, file=stderr)
            return 1

        print(f"{user_input_request.prompt}{" ".join([f"'{arg}'" for arg in argv[1:]])}\n")
        user_input: UserInput = UserInput(args=argv[1:])
        client.send(dumps(asdict(user_input)).encode() + NEWLINE_DELIMITER)

        try:
            output_json: str = (await recv_line(client)).decode()
        except EOFError:
            print("Disconnected", file=stderr)
            return 1

        try:
            output: Output = Output(**loads(output_json))
        except TypeError as e:
            print(e, file=stderr)
            return 1

        print(output.output, file=stdout if output.direction == OutputDirection.stdout else stderr)

    return 0


if __name__ == "__main__":
    exit(run(main()))
