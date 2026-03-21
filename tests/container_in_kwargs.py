from sys import argv
from pathlib import Path
from npycli import Command


def main(**kwargs: list[str]) -> None:
    print(kwargs)
    for key, inner_values in kwargs.items():
        print(f"{key}:")
        for value in inner_values:
            print(f"  {value}")


DEFAULT_ARGS: list[str] = ["--a", "a.value", "--b", "b.value1", "--b", "b.value2"]
cmd: Command = Command.create(main, Path(__file__).name, help=f"Go ahead, enter many of the same key, some default that are always entered are {DEFAULT_ARGS}")
if __name__ == "__main__":
    cmd([*argv[1:], *DEFAULT_ARGS])
