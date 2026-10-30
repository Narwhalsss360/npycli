from pathlib import Path
from sys import argv

from npycli import Command


def main(**kwargs: tuple[int | str, ...]) -> None:
    print(kwargs)
    for key, inner_values in kwargs.items():
        print(f"{key}:")
        for value in inner_values:
            print(f"  {value!r}")


DEFAULT_ARGS: list[str] = ["--a", "a.value", "--a", "1", "--b", "b.value1", "--b", "b.value2"]
cmd: Command = Command.create(main, Path(__file__).name, help=f"Go ahead, enter many of the same key, some default that are always entered are {DEFAULT_ARGS}")
if __name__ == "__main__":
    cmd([*argv[1:], *DEFAULT_ARGS])
