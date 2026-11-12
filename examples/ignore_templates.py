from asyncio import CancelledError, gather, run
from pathlib import Path
from sys import argv, exit, stderr, stdout
from typing import Annotated

from npycli.middlewares.help_cmd import use_help_command

try:
    from aiohttp import ClientError, ClientResponseError, ClientSession
except ImportError:
    print("Module aiohttp is required for this example", file=stderr)
    exit(1)

from npycli.ansi.const.sgr import (
    BOLD_OR_INCREASED_INTENSITY,
    DEFAULT_RENDITION,
    RED_DISPLAY,
)
from npycli.ansi.sequences import SGR
from npycli.asyncio import CLI, Command, command
from npycli.errors import CommandArgumentError
from npycli.parameters import AnnotationPreview, Description


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


async def ignore_templates(
    *templates: Annotated[
        str,
        AnnotationPreview("'*.gitignore'"),
        Description(
            "A variable positional count argument of the gitignore template to fetch from github's gitingnore repository. The path of the file from the root of the repository."
        ),
    ],
) -> None:
    """
    Generate an ignore template fetched from github/gitignore repository.
    """

    this_cmd: Command = command.require_async_cmd(command.cmd(ignore_templates))
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


async def main() -> int:
    cli = CLI(Path(__file__).name.replace(".py", ""))
    cmd: Command = await Command.create(ignore_templates, cli.title)
    cli.add_command(cmd)
    help_command: Command = use_help_command(
        cli, command_cls=Command, single_command_cli=cmd, print_to=stdout
    )

    if len(argv) == 1:
        await cli.exec((help_command.name,))
        return 0

    try:
        await cli.exec((cmd.name, *argv[1:]))
    except (CommandArgumentError, ClientError) as e:
        print_error(e)
        return 1
    except (KeyboardInterrupt, CancelledError):
        print("\n^C")

    return 0


if __name__ == "__main__":
    exit(run(main()))
