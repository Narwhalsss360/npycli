from sys import argv
from npycli import Command
from npycli.parameters import BypassParse


def parse_bypass(*entries: BypassParse) -> None:
    print("\n".join(entries))


if __name__ == "__main__":
    command: Command = Command.create(parse_bypass)
    print(command.extended_command_help())
    command.exec_with(argv[1:])
