from sys import argv
from npycli import Command
from npycli.parameters import BypassParse


def parse_bypass(*entries: BypassParse) -> None:
    """Just give me the (string) args!"""

    print("entries:")
    print("\n".join(entries))


def parse_bypass_with_positionals(name: str, age: int, *entries: BypassParse) -> None:
    """First give me some positionals, then just the (string) args!"""

    print(f"{name=}")
    print(f"{age=}")
    print("entries:")
    print("\n".join(entries))


def parse_bypass_with_positionals_and_kwargs(name: str, age: int, *entries: BypassParse, upper: bool = False, key: str = "value") -> None:
    """First give me some positionals, maybe some bool flags and some keyword arguments, but the rest, just (string) args."""

    name = name.upper() if upper else name
    print(f"{name=}")
    print(f"{age=}")
    print(f"{upper=}")
    print(f"{key=}")
    print("entries:")
    print("\n".join(entries))


def parse_bypass_with_positionals_and_kwargs_and_var_kwargs(name: str, age: int, *entries: BypassParse, upper: bool = False, key: str = "value", **kwargs: str) -> None:
    """First give me some positionals, maybe some bool flags and some keyword arguments, and all of the parsed keywords,
    but the rest (basically just positionals), just the (string) args."""

    name = name.upper() if upper else name
    print(f"{name=}")
    print(f"{age=}")
    print(f"{upper=}")
    print(f"{key=}")
    print("entries:")
    print("\n".join(entries))
    print(f"{kwargs=}")


if __name__ == "__main__":
    for f in (
        parse_bypass,
        parse_bypass_with_positionals,
        parse_bypass_with_positionals_and_kwargs,
        parse_bypass_with_positionals_and_kwargs_and_var_kwargs
    ):
        command: Command = Command.create(f)
        print(command.extended_command_help())
        command.exec_with(argv[1:])
        print("")
