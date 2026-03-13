from typing import Any, TextIO
from sys import stdout
from io import StringIO
from os import get_terminal_size
from npycli.ansi import (
    send_ansi,
    strip_ansi,
    SAVE_CURRENT_CURSOR_POSITION,
    CURSOR_DOWN,
    CURSOR_UP,
    INSERT_NEW_LINE,
    RESTORE_SAVED_CURSOR_POSITION,
    SELECT_CHARACTER_RENDITION,
    FOREGROUND_RED,
    BACKGROUND_WHITE,
    SET_BOLD_MODE,
    SCR_RESET
)


def print_above(*args: Any, max_columns: int, sep: str | None = " ", file: TextIO = stdout, current_is_empty: bool = False, lines_above: int = 1) -> None:
    '''
    Print above the current line.
    '''

    if lines_above == 0:
        print(*args, sep=sep)
        return

    # Use print with file=buffer so this function can be used just like regular print
    buffer: StringIO = StringIO()
    print(*args, sep=sep, end="", file=buffer, flush=True)
    output: str = buffer.getvalue()

    line_count: int = 1
    line_length: int = 0
    for c in strip_ansi(output):
        line_length += 1
        if line_length == max_columns or c == "\n":
            line_count += 1
            line_length = 0

    send_ansi(SAVE_CURRENT_CURSOR_POSITION, flush=True)
    if current_is_empty:
        print("\n" * lines_above, file=file, end="", flush=True)
        send_ansi(CURSOR_UP.with_args(lines_above), file=file, flush=True)

    # These ansi control commands may be supplied with arguments
    print("\n" * line_count, file=file, end="", flush=True)
    send_ansi(CURSOR_UP.with_args(line_count + lines_above - (0 if current_is_empty else 1)), file=file, flush=True)
    # This one doesn't have argument, so we just repeat the command
    send_ansi(INSERT_NEW_LINE, repeat=line_count, file=file, flush=True)

    # Flush, just in case current cursor position gets moved after output
    print(output, end='', file=file, flush=True)
    send_ansi(RESTORE_SAVED_CURSOR_POSITION, file=file, flush=True)
    send_ansi(CURSOR_DOWN.with_args(line_count), file=file, flush=True)


# Prints in order
print(1)
print(2)
print(4)
print_above(f"3\n3.5", max_columns=get_terminal_size().columns, current_is_empty=True) # This line will be an empty line, so current_is_empty = True
print_above(f"2.5", max_columns=get_terminal_size().columns, current_is_empty=True, lines_above=3) # This line will be an empty line, so current_is_empty = True

SELECT_CHARACTER_RENDITION(SET_BOLD_MODE, FOREGROUND_RED, BACKGROUND_WHITE)
# Or
print(1)
print(2)
print(4, end='')
SELECT_CHARACTER_RENDITION(SCR_RESET)
three = f"{SELECT_CHARACTER_RENDITION.with_args(SET_BOLD_MODE, FOREGROUND_RED, BACKGROUND_WHITE)}3{SELECT_CHARACTER_RENDITION(SCR_RESET)}"
print_above(three, max_columns=get_terminal_size().columns)
print()
