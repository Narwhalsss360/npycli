from io import StringIO
from os import get_terminal_size
from sys import stdout
from typing import Any, TextIO

from npycli.ansi.const.sgr import (
    BOLD_OR_INCREASED_INTENSITY,
    DEFAULT_RENDITION,
    RED_DISPLAY,
    WHITE_BACKGROUND,
)
from npycli.ansi.parsing import strip_control_sequences
from npycli.ansi.sequences import CUD, CUU, IL, RCP, SCCP, SGR


def print_above(
    *args: Any,
    max_columns: int,
    sep: str | None = " ",
    file: TextIO = stdout,
    current_is_empty: bool = False,
    lines_above: int = 1,
) -> None:
    """
    Print above the current line.
    """

    if lines_above == 0:
        print(*args, sep=sep)
        return

    # Use print with file=buffer so this function can be used just like regular print
    buffer: StringIO = StringIO()
    print(*args, sep=sep, end="", file=buffer, flush=True)
    output: str = buffer.getvalue()

    line_count: int = 1
    line_length: int = 0
    for c in strip_control_sequences(output):
        line_length += 1
        if line_length == max_columns or c == "\n":
            line_count += 1
            line_length = 0

    SCCP(file=file)
    if current_is_empty:
        print("\n" * lines_above, file=file, end="", flush=True)
        CUU(lines_above, file=file)

    # These ansi control commands may be supplied with arguments
    print("\n" * line_count, file=file, end="", flush=True)
    CUU(line_count + lines_above - (0 if current_is_empty else 1), file=file)
    # This one doesn't have argument, so we just repeat the command
    IL(line_count, file=file)

    # Flush, just in case current cursor position gets moved after output
    print(output, end="", file=file, flush=True)
    RCP(file=file)
    CUD(line_count, file=file)


# Prints in order
print(1)
print(2)
print(4)
print_above(
    "3\n3.5", max_columns=get_terminal_size().columns, current_is_empty=True
)  # This line will be an empty line, so current_is_empty = True
print_above(
    "2.5", max_columns=get_terminal_size().columns, current_is_empty=True, lines_above=3
)  # This line will be an empty line, so current_is_empty = True

SGR(BOLD_OR_INCREASED_INTENSITY, RED_DISPLAY, WHITE_BACKGROUND, file=stdout)
# Or
print(1)
print(2)
print(4, end="")
SGR(DEFAULT_RENDITION, file=stdout)
three = f"{SGR(BOLD_OR_INCREASED_INTENSITY, RED_DISPLAY, WHITE_BACKGROUND)}3{SGR(DEFAULT_RENDITION)}"
print_above(three, max_columns=get_terminal_size().columns)
print()
