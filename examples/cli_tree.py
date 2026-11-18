from pathlib import Path
from sys import argv, exit
from typing import Annotated, Any, cast

import npycli
from npycli import CLI, Command
from npycli.abc.command import cmd
from npycli.errors import CLIError, EmptyEntriesError, ParsingError, causes
from npycli.middleware import MiddlewareContext
from npycli.middlewares.cli_error_printer import (
    full_cli_error_string,
    use_cli_error_printer,
)
from npycli.middlewares.default_command import (
    use_default_on_empty_command_execution_info,
)
from npycli.middlewares.global_help import bypass_global_help_flag, use_global_help_flag
from npycli.middlewares.help_cmd import create_help_command
from npycli.middlewares.sub_clis import get_sub_clis, use_sub_cli_coalesce_command
from npycli.parameters import Alias, BypassParse, Description


def use_common_middlewares(cli: CLI, preamble: str = "", line_prefix: str = "") -> CLI:
    use_default_on_empty_command_execution_info(
        use_cli_error_printer(
            use_global_help_flag(
                cli,
                create_help_command(
                    cli, preamble, long_form_default=True, line_prefix=line_prefix
                ),
            ),
            raise_on=(EmptyEntriesError,),
            cli_error_return_value=lambda context, command, error: error,
        ),
        "help",
    )
    return cli


def construct_sub_cli_a() -> CLI:
    cli_a: CLI = CLI("fileio")

    @cli_a.cmd()
    def echo(*entries: BypassParse) -> str:
        """Echo arguments"""
        return " ".join(entries)

    @cli_a.cmd()
    def echo_string(s: str) -> str:
        """Echo a single argument"""
        return s

    @cli_a.cmd()
    def touch(
        *files: Annotated[Path, Description("File(s) to touch")],
        no_create: Annotated[
            bool,
            Alias("c", "no-create", private=True),
            Description("Do not create any files if they do not exist."),
        ] = False,
        access_only: Annotated[
            bool, Alias("a", private=True), Description("Change only the access time.")
        ] = False,
        mod_only: Annotated[
            bool,
            Alias("m", private=True),
            Description("Change only the modification time."),
        ] = False,
        timestamp: Annotated[
            float | None,
            Alias("t", private=True),
            Description("Use specified Unix timestamp instead of current time."),
        ] = None,
    ) -> None:
        import os
        import time

        target_time = timestamp if timestamp is not None else time.time()
        for file in files:
            if not file.exists():
                if no_create:
                    continue
                file.touch()

            if access_only or mod_only or timestamp is not None:
                stat = file.stat()
                atime = target_time if (access_only or not mod_only) else stat.st_atime
                mtime = target_time if (mod_only or not access_only) else stat.st_mtime
                os.utime(file, (atime, mtime))
            else:
                file.touch()

    return use_common_middlewares(cli_a, "Sub CLI A")


def construct_sub_cli_b() -> CLI:
    cli_b: CLI = CLI("internet")

    @cli_b.cmd()
    def publicip() -> str:
        """
        Get public ip address.
        From ipify.org
        """

        try:
            import requests
        except ImportError:
            raise RuntimeError("A dependency of this command is the 'requests' module")

        response: requests.Response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise TypeError("Unexpected response from server.")
        data = cast(dict[Any, Any], data)
        if not isinstance(ip := data.get("ip", None), str):
            raise TypeError("Unexpected response from server.")
        return ip

    try:
        import apod_manager

        use_sub_cli_coalesce_command(cli_b, apod_manager.cli.cli, "apod")
    except ImportError:

        @cli_b.cmd()
        def apod(apidate: str | None = None) -> str:
            """
            Get NASA's Astronomy Picture of the Day.
            Date Format: YYMMDD.
            Default: Today's date
            """

            import json
            from datetime import datetime

            apidate = apidate or datetime.now().astimezone().strftime("%y%m%d")
            try:
                import requests
            except ImportError:
                raise RuntimeError(
                    "A dependency of this command is the 'requests' module"
                )

            response: requests.Response = requests.get(
                f"https://science.nasa.gov/wp-json/wp/v2/apod-basic/{apidate}"
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)

    import ignore_templates_requests

    use_sub_cli_coalesce_command(cli_b, ignore_templates_requests.cli, "ignore")

    # ignore_templates_requests prints to stdout, so that things don't get shown twice, make all return values None
    @ignore_templates_requests.cli.middlewares.register.return_value()
    def return_value(
        context: MiddlewareContext, command: npycli.abc.Command, return_value: Any
    ) -> Any:
        return None

    return use_common_middlewares(cli_b, "Sub CLI B")


def main(*args: BypassParse, prompter: bool = False) -> int:
    main_cli: CLI = CLI("main-cli")

    @main_cli.cmd()
    def total(*nums: int) -> int:
        """Take the sum of the given integers"""
        return sum(nums)

    @main_cli.cmd()
    def prod(*nums: int) -> int:
        """Take the product of the given integers"""
        import math

        return math.prod(nums)

    @main_cli.cmd(names=("process", "!"))
    def process(*args: BypassParse) -> Any:
        """Invoke a shell subprocess."""
        from subprocess import CompletedProcess, run

        completed: CompletedProcess[bytes] = run(args, shell=True, check=False)
        if completed.returncode != 0:
            return completed
        return None

    bypass_global_help_flag(cmd(process))

    @main_cli.cmd()
    def subclis() -> str:
        """Show the sub-clis"""

        return "\n".join(cli.title for cli in get_sub_clis(main_cli))

    import user_items

    use_sub_cli_coalesce_command(main_cli, construct_sub_cli_a())
    use_sub_cli_coalesce_command(main_cli, construct_sub_cli_b())
    use_sub_cli_coalesce_command(main_cli, user_items.cli)
    use_common_middlewares(main_cli, "The main CLI", " > ")

    once = main_cli.prompt if prompter else lambda: main_cli.exec(args)
    code: int = 0
    while True:
        try:
            if (retval := once()) is not None:
                print(retval)
        except KeyboardInterrupt:
            print("\n^C")
            code = 0
            break
        except EmptyEntriesError:
            pass
        except CLIError as err:
            print(
                full_cli_error_string(
                    main_cli,
                    err,
                    tuple(
                        cause
                        for cause in causes(err, False)
                        if isinstance(cause, (CLIError, ParsingError))
                    ),
                    ansi=True,
                )
            )
            code = 1

        if not prompter:
            break

    return code


if __name__ == "__main__":
    exit(Command.create(main, Path(__file__).with_suffix("").stem).exec_with(argv[1:]))
