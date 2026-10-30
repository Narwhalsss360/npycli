from io import StringIO
from os import get_terminal_size
from pathlib import Path
from sys import argv, stdout
from time import sleep
from typing import Any, TextIO

from npycli import Command
from npycli.ansi.const.p_rm import HIDE_CURSOR
from npycli.ansi.const.p_sm import SHOW_CURSOR
from npycli.ansi.const.sgr import DEFAULT_RENDITION, SINGLY_UNDERLINED, SLOWLY_BLINKING
from npycli.ansi.parsing import strip_control_sequences
from npycli.ansi.sequences import CUU, IL, P_RM, P_SM, SGR


class InPlacePrint:
    def __init__(self, file: TextIO = stdout) -> None:
        self.last_lines: list[str] | None = None
        self._file: TextIO = file

    @staticmethod
    def wrap(string: str, columns: int) -> list[str]:
        lines: list[str] = string.split("\n")
        i: int = 0
        while i < len(lines):
            if len(strip_control_sequences(lines[i])) > columns:
                this, next = lines[i][:columns], lines[i][columns:]
                lines[i] = this
                lines.insert(i + 1, next)
            i += 1
        return lines

    @staticmethod
    def pad(lines: list[str], padding: list[int]) -> list[str]:
        if len(lines) != len(padding):
            raise ValueError("'lines' and 'padding' must be the same size.")

        padded: list[str] = lines.copy()
        for i, (padded_line, pad) in enumerate(zip(padded, padding)):
            stripped_len: int = len(strip_control_sequences(padded_line))
            if stripped_len < pad:
                padded[i] = f"{padded[i]}{' ' * (pad - stripped_len)}"

        return padded

    def print(self, *values: Any, sep: str = " ", end: str = "\n") -> bool:
        buffer: StringIO = StringIO()
        print(*values, sep=sep, end=end, file=buffer, flush=True)
        terminal_size = get_terminal_size(self._file.fileno())
        lines: list[str] = InPlacePrint.wrap(buffer.getvalue(), terminal_size.columns)
        with_clearing: list[str] = lines.copy()

        if self.last_lines is not None:
            if len(self.last_lines) > len(lines):
                clearing_line: str = " " * terminal_size.columns
                with_clearing.extend(clearing_line for _ in range(len(self.last_lines) - len(lines)))

            padding: list[int] = [len(strip_control_sequences(last_line)) for last_line in self.last_lines]
            if len(padding) < len(with_clearing):
                padding.extend(0 for _ in range(len(lines) - len(padding)))
            with_clearing = InPlacePrint.pad(with_clearing, padding)

        self.last_lines = lines
        print("\n".join(with_clearing), file=self._file)
        if len(with_clearing) >= terminal_size.lines:
            self.last_lines = None
            if len(with_clearing) > len(lines):
                CUU(len(with_clearing) - len(lines), file=self._file)
            return False

        CUU(len(with_clearing), file=self._file)
        return True

    def print_above(self, *values: Any, sep: str = " ", end: str = "") -> None:
        buffer: StringIO = StringIO()
        print(*values, sep=sep, end=end, file=buffer, flush=True)
        terminal_size = get_terminal_size(self._file.fileno())
        lines: list[str] = InPlacePrint.wrap(buffer.getvalue(), terminal_size.columns)

        if not self.last_lines:
            print("\n".join(lines), file=self._file)
            return

        IL(len(lines), file=self._file)
        print("\n".join(lines), file=self._file)

    def clear(self) -> bool:
        if self.last_lines is None:
            return True
        terminal_size = get_terminal_size(self._file.fileno())
        if len(self.last_lines) >= terminal_size.lines:
            self.last_lines = None
            return False

        clearing_line: str = " " * terminal_size.columns
        print("\n".join([clearing_line for _ in range(len(self.last_lines))]), file=self._file)
        CUU(len(self.last_lines), file=self._file)
        return True

    def done(self) -> bool:
        if self.last_lines is None:
            return True
        terminal_size = get_terminal_size(self._file.fileno())
        if len(self.last_lines) >= terminal_size.lines:
            self.last_lines = None
            return False

        print("\n" * len(self.last_lines), end="", file=self._file)
        return True

    def __call__(self, *values: Any, sep: str = " ", end: str = "\n") -> bool:
        return self.print(*values, sep=sep, end=end)


def line_count_wrapped_at(s: str, column: int) -> int:
    line_count: int = 1
    line_length: int = 0
    for c in strip_control_sequences(s):
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
        f"{SGR(SLOWLY_BLINKING)}Walking "
        f"{SGR(SINGLY_UNDERLINED)}{working_directory}{SGR(DEFAULT_RENDITION)}{SGR(SLOWLY_BLINKING)}"
        f" ...{SGR(DEFAULT_RENDITION)}"
    )

    P_RM(HIDE_CURSOR, file=stdout)
    in_place = InPlacePrint()
    try:
        for root, _, files in working_directory.walk():
            for file in files:
                if not in_place(make_tree_string(working_directory, root.joinpath(file))):
                    print(chr(0x2500) * get_terminal_size().columns)
                sleep(interval)

        if in_place.clear():
            CUU()
            print(" " * get_terminal_size().columns, end="\r")
        print("Done!")
    except KeyboardInterrupt:
        in_place.clear()
        raise
    finally:
        P_SM(SHOW_CURSOR, file=stdout)


if __name__ == "__main__":
    try:
        Command.create(main).exec_with(argv[1:])
    except KeyboardInterrupt:
        print("\n^C")
