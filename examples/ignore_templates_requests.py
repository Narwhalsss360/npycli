from pathlib import Path
from sys import argv, exit, stderr, stdout
from typing import Annotated

from npycli.abc.command import cmd
from npycli.middlewares.global_help import use_global_help_flag
from npycli.middlewares.help_cmd import create_help_command
from npycli.middlewares.single_cmd_cli import use_single_command_cli

try:
    import requests
except ImportError:
    print("Module requests is required for this example", file=stderr)
    exit(1)

from npycli import CLI, Command, command
from npycli.ansi.const.sgr import (
    BOLD_OR_INCREASED_INTENSITY,
    DEFAULT_RENDITION,
    RED_DISPLAY,
)
from npycli.ansi.sequences import SGR
from npycli.errors import CommandArgumentError
from npycli.parameters import AnnotationPreview, Description

cli = CLI(Path(__file__).with_suffix("").stem)


def print_error(exc: Exception) -> None:
    print(
        SGR(BOLD_OR_INCREASED_INTENSITY, RED_DISPLAY),
        f"{exc.__class__.__name__}:",
        SGR(DEFAULT_RENDITION),
        " ",
        f" {'\n\t'.join(str(arg) for arg in exc.args)}",
        sep="",
        file=stderr,
    )


def build_gh_gitignore_url(template_name: str) -> str:
    return f"https://raw.githubusercontent.com/github/gitignore/refs/heads/main/{template_name}"


@cli.cmd("ignore")
def ignore_templates(
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

    this_cmd: Command = command.require_sync_cmd(command.cmd(ignore_templates))
    for template_name in templates:
        if not template_name.endswith(".gitignore"):
            raise CommandArgumentError(
                f"Templates must be a .gitignore file, '{template_name}' is invalid",
                this_cmd,
                command=this_cmd,
            )

    values: list[str] = [
        requests.get(build_gh_gitignore_url(name)).text for name in templates
    ]

    print(
        "\n\n".join(
            f"## {this_cmd}:{template_name}\n{value}"
            for template_name, value in zip(templates, values)
        )
    )


help_command_name: str = "help"
use_global_help_flag(
    cli,
    create_help_command(
        cli,
        cmd(ignore_templates).help or "",
        help_command_name,
        print_to=stdout,
        single_command_cli=cmd(ignore_templates),
    ),
)
use_single_command_cli(
    cli, allow_multiple_commands=True, single_command=cmd(ignore_templates)
)


def main() -> int:
    try:
        cli.exec(argv[1:])
    except CommandArgumentError as e:
        print_error(e)
        return 1
    except KeyboardInterrupt:
        print("\n^C")

    return 0


if __name__ == "__main__":
    exit(main())
