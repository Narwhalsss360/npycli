from typing import Any
from time import sleep
from os import get_terminal_size
from pathlib import Path
from sys import argv
from io import StringIO
from npycli import Command
from npycli.ansi import CURSOR_UP, SELECT_CHARACTER_RENDITION, SCR_RESET, SET_UNDERLINE_MODE, SET_BLINKING_MODE, strip_ansi, HIDE_CURSOR


class InPlacePrint:
    def __init__(self) -> None:
        self.last_lines: list[str] | None = None

    @staticmethod
    def wrap(string: str, columns: int) -> list[str]:
        lines: list[str] = string.split("\n")
        for i in range(len(lines)):
            if len(lines[i]) > columns:
                this, next = lines[i][:columns], lines[i][columns:]
                lines[i] = this
                lines.insert(i + 1, next)
        return lines

    @staticmethod
    def pad(lines: list[str], padding: list[int]) -> list[str]:
        if len(lines) != len(padding):
            raise ValueError("'lines' and 'padding' must be the same size.")
        return [line.ljust(pad) for line, pad in zip(lines, padding)]

    def print(self, *values: Any, sep: str = " ", end: str = "\n") -> bool:
        buffer: StringIO = StringIO()
        print(*values, sep=sep, end=end, file=buffer, flush=True)
        terminal_size = get_terminal_size()
        lines: list[str] = InPlacePrint.wrap(buffer.getvalue(), terminal_size.columns)
        with_clearing: list[str] = lines.copy()

        if self.last_lines is not None:
            if len(self.last_lines) > len(lines):
                clearing_line: str = " " * terminal_size.columns
                with_clearing.extend(clearing_line for _ in range(len(self.last_lines) - len(lines)))

            padding: list[int] = [len(last_line) for last_line in self.last_lines]
            if len(padding) < len(with_clearing):
                padding.extend(0 for _ in range(len(lines) - len(padding)))
            with_clearing = InPlacePrint.pad(with_clearing, padding)

        self.last_lines = lines
        print("\n".join(with_clearing))
        if len(with_clearing) >= terminal_size.lines:
            self.last_lines = None
            if len(with_clearing) > len(lines):
                CURSOR_UP(len(with_clearing) - len(lines))
            return False

        CURSOR_UP(len(with_clearing))
        return True

    def clear(self) -> bool:
        if self.last_lines is None:
            return True
        terminal_size = get_terminal_size()
        if len(self.last_lines) >= terminal_size.lines:
            self.last_lines = None
            return False

        clearing_line: str = " " * terminal_size.columns
        print("\n".join([clearing_line for _ in range(len(self.last_lines))]))
        CURSOR_UP(len(self.last_lines))
        return True

    def __call__(self, string: str) -> bool:
        return self.print(string)


def line_count_wrapped_at(s: str, column: int) -> int:
    line_count: int = 1
    line_length: int = 0
    for c in strip_ansi(s):
        line_length += 1
        if line_length == column or c == "\n":
            line_count += 1
            line_length = 0
    return line_count


def make_tree_string(working: Path, path: Path) -> str:
    nodes: list[str] = []
    node: Path = path
    while node != working:
        nodes.insert(0, node.name)
        node = node.parent

    out: str = ""
    for i, n in enumerate(nodes):
        if i == 0:
            out += n
            if len(nodes) == 1:
                break

            out += "\n"
            continue

        if i == len(nodes) - 1:
            out += chr(0x2514)
        else:
            out += chr(0x251C)

        out += chr(0x2500) * (i)
        out += " " + n

        if i != len(nodes) - 1:
            out += "\n"
    return out


def main(
    working_directory: Path | None = None,
    interval: float = 0.05
) -> None:
    working_directory = working_directory or Path(".")
    print(
        f"{SELECT_CHARACTER_RENDITION.with_args(SET_BLINKING_MODE)}Walking "
        f"{SELECT_CHARACTER_RENDITION.with_args(SET_UNDERLINE_MODE)}{str(working_directory)}{SELECT_CHARACTER_RENDITION.with_args(SCR_RESET)}{SELECT_CHARACTER_RENDITION.with_args(SET_BLINKING_MODE)}"
        f" ...{SELECT_CHARACTER_RENDITION.with_args(SCR_RESET)}"
    )

    HIDE_CURSOR()
    in_place = InPlacePrint()
    for root, _, files in working_directory.walk():
        for file in files:
            if not in_place(make_tree_string(working_directory, root.joinpath(file))):
                print(chr(0x2500) * get_terminal_size().columns)
            sleep(interval)

    if in_place.clear():
        CURSOR_UP()
        print(" " * get_terminal_size().columns, end="\r")
    print("Done!")


if __name__ == "__main__":
    try:
        Command.create(main).exec_with(argv[1:])
    except KeyboardInterrupt:
        print("\n^C")
