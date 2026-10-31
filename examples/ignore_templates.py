from asyncio import CancelledError, gather, run
from pathlib import Path
from sys import argv, exit, stderr
from typing import Annotated

try:
    from aiohttp import ClientError, ClientResponseError, ClientSession
except ImportError:
    print("Module aiohttp is required for this example", file=stderr)
    exit(1)

from npycli import Command, command
from npycli.ansi.const.sgr import (
    BOLD_OR_INCREASED_INTENSITY,
    DEFAULT_RENDITION,
    RED_DISPLAY,
)
from npycli.ansi.sequences import SGR
from npycli.errors import CommandArgumentError
from npycli.parameters import AnnotationPreview


def print_error(exc: Exception) -> None:
    if isinstance(exc, ClientResponseError):
        message: str = f"{exc.status} {exc.message}"
    else:
        message: str = f" {'\n\t'.join(str(arg) for arg in exc.args)}"

    print(
        SGR(BOLD_OR_INCREASED_INTENSITY, RED_DISPLAY),
        f"{exc.__class__.__name__}:",
        SGR(DEFAULT_RENDITION),
        " ",
        message,
        sep="",
        file=stderr,
    )


def build_gh_gitignore_url(template_name: str) -> str:
    return f"https://raw.githubusercontent.com/github/gitignore/refs/heads/main/{template_name}"


async def fetch_string(session: ClientSession, url: str) -> str:
    async with session.get(url, raise_for_status=True) as response:
        return await response.text()


async def main(
    *templates: Annotated[str, AnnotationPreview("'*.gitignore'")],
) -> None:
    this_cmd: Command = command.cmd(main)
    for template_name in templates:
        if not template_name.endswith(".gitignore"):
            raise CommandArgumentError(
                f"Templates must be a .gitignore file, '{template_name}' is invalid",
                this_cmd,
                command=this_cmd,
            )

    async with ClientSession() as session:
        values: tuple[str] = await gather(
            *[fetch_string(session, build_gh_gitignore_url(name)) for name in templates]
        )

    print(
        "\n\n".join(
            f"## {this_cmd}:{template_name}\n{value}"
            for template_name, value in zip(templates, values)
        )
    )


cmd: Command = Command.create(main, Path(__file__).name.replace(".py", ""))
if __name__ == "__main__":
    if len(argv) == 1:
        print(cmd)
        exit(1)

    try:
        run(cmd(argv[1:]))
    except (CommandArgumentError, ClientError) as e:
        print_error(e)
        exit(1)
    except (KeyboardInterrupt, CancelledError):
        print("\n^C")
