from sys import argv, stderr
from os.path import basename
from typing import Annotated
from asyncio import CancelledError, run, gather
from aiohttp import ClientSession, ClientError, ClientResponseError
from npycli import Command, command
from npycli.parameters import AnnotationPreview
from npycli.errors import CommandArgumentError
from npycli.ansi import (
    SELECT_CHARACTER_RENDITION,
    SET_BOLD_MODE,
    FOREGROUND_RED,
    SCR_RESET,
)


def print_error(e: Exception) -> None:
    if isinstance(e, ClientResponseError):
        message: str = f"{e.code} {e.message}"
    else:
        message: str = f" {'\n\t'.join(str(arg) for arg in e.args)}"

    print(
        SELECT_CHARACTER_RENDITION.with_args(SET_BOLD_MODE, FOREGROUND_RED),
        f"{e.__class__.__name__}:",
        SELECT_CHARACTER_RENDITION.with_args(SCR_RESET),
        " ", message,
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
        values: list[str] = await gather(
            *[fetch_string(session, build_gh_gitignore_url(name)) for name in templates]
        )

    print(
        "\n\n".join(
            f"## {this_cmd}:{template_name}\n{value}"
            for template_name, value in zip(templates, values)
        )
    )


cmd: Command = Command.create(main, basename(__file__).replace(".py", ""))
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
