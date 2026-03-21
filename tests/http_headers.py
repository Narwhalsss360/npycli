from sys import argv
from typing import Annotated, Optional
from npycli import Command
from npycli.parameters import Alias, Description


def http_headers(
    *,
    headers: Annotated[Optional[tuple[str, ...]], Description("Specify this keyword argument multiple times"), Alias("header", private=True)] = None
):
    for header in headers or tuple():
        print(f"{header}\\r\\n")
    print("\\r\\n")


if __name__ == "__main__":
    cmd: Command = Command(http_headers, ("http-headers",))
    cmd(argv[1:])
