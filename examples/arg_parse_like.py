import os
import time
from datetime import datetime
from pathlib import Path
from sys import argv, exit
from types import NoneType
from typing import Annotated, cast

from npycli import Command, CommandParameter, CommandParameterParser, ParameterKind
from npycli.parameters import Alias, Description


def unix_timestamp_to_datetime_parser(s: str) -> datetime:
    return datetime.fromtimestamp(float(s))


def touch() -> None:
    parameters: tuple[CommandParameter, ...] = (
        CommandParameter.build(
            "files",
            ParameterKind.VAR_POSITIONAL,
            Annotated[Path, Description("File(s) to touch")],
        ),
        CommandParameter.build(
            "no_create",
            ParameterKind.KEYWORD_ONLY,
            Annotated[
                bool,
                Alias("c", "no-create", private=True),
                Description("Do not create any files if they do not exist."),
            ],
            False,
        ),
        CommandParameter.build(
            "access_only",
            ParameterKind.KEYWORD_ONLY,
            Annotated[
                bool,
                Alias("a", private=True),
                Description("Change only the access time."),
            ],
            False,
        ),
        CommandParameter.build(
            "mod_only",
            ParameterKind.KEYWORD_ONLY,
            Annotated[
                bool,
                Alias("m", private=True),
                Description("Change only the modification time."),
            ],
            False,
        ),
        CommandParameter(
            ("t",),
            ParameterKind.KEYWORD_ONLY,
            datetime | None,
            argument_types=(datetime, NoneType),
            description="Use the specified Unix timestamp instead of current time.",
            default=None,
            _private_name="timestamp",
        ),
    )
    args, kwargs = CommandParameterParser(
        keyword_prefix="--",
        argument_separator="--",
        parsers={datetime: unix_timestamp_to_datetime_parser},
        char_keyword_prefix="-",
    ).parse(parameters, argv[1:])

    print(f"{args=}")
    print(f"{kwargs=}")
    assert all(isinstance(arg, Path) for arg in args)
    files: list[Path] = cast(list[Path], args)
    no_create: bool = kwargs.get("no_create", False)
    access_only: bool = kwargs.get("access_only", False)
    mod_only: bool = kwargs.get("mod_only", False)
    timestamp: datetime | None = kwargs.get("timestamp", None)

    target_time = timestamp.timestamp() if timestamp is not None else time.time()
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


# Equivalent to:
if __name__ == "__main__":
    touch()
    exit()

    # Equaivalent execution as a command instead:
    def touch_as_built_command_function(
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
            datetime | None,
            Alias("t", private=True),
            Description("Use specified Unix timestamp instead of current time."),
        ] = None,
    ) -> None:
        import os
        import time

        target_time = timestamp.timestamp() if timestamp is not None else time.time()
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

    Command.create(touch_as_built_command_function).exec_with(
        argv[1:], {datetime: unix_timestamp_to_datetime_parser}
    )
