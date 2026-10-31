from sys import argv
from typing import Annotated

from npycli import Command
from npycli.parameters import Alias, Description


def http_headers(
    *,
    headers: Annotated[
        tuple[str, ...] | None,
        Description("Specify this keyword argument multiple times"),
        Alias("header", private=True),
    ] = None,
):
    for header in headers or ():
        print(f"{header}\\r\\n")
    print("\\r\\n")


if __name__ == "__main__":
    cmd: Command = Command(http_headers, ("http-headers",))
    if len(argv) == 1:
        print(cmd.extended_command_help())
    else:
        cmd(argv[1:])
