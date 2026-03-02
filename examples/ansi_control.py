from typing import Any
from io import StringIO
from os import get_terminal_size
from npycli.ansi import (
    send_ansi,
    SAVE_CURRENT_CURSOR_POSITION,
    CURSOR_DOWN,
    CURSOR_UP,
    INSERT_NEW_LINE,
    RESTORE_SAVED_CURSOR_POSITION,
    SELECT_CHARACTER_RENDITION,
    FOREGROND_RED,
    BACKGROND_WHITE,
    SET_BOLD_MODE,
    SCR_RESET
)

def print_above(*args: Any, max_columns: int, sep: str | None = " ", current_is_empty: bool = False) -> None:
    '''
    Print above the current line.
    '''

    # Use print with file=buffer so this function can be used just like regular print
    buffer: StringIO = StringIO()
    print(*args, sep=sep, end="", file=buffer, flush=True)
    output: str = buffer.getvalue()

    line_count: int = 1
    line_length: int = 0
    for c in output:
        line_length += 1
        if line_length == max_columns or c == "\n":
            line_count += 1
            line_length = 0

    send_ansi(SAVE_CURRENT_CURSOR_POSITION)
    if current_is_empty:
        print()
        send_ansi(CURSOR_UP.with_args(2))

    # These ansi control commands may be supplied with arguments
    print("\n" * line_count, end="")
    send_ansi(CURSOR_UP.with_args(line_count))
    # This one doesn't have argument, so we just repeat the command
    send_ansi(INSERT_NEW_LINE, repeat=line_count)

    # Flush, just in case current cursor position gets moved after output
    print(output, end='', flush=True)
    send_ansi(RESTORE_SAVED_CURSOR_POSITION)
    send_ansi(CURSOR_DOWN.with_args(line_count))


# Prints in order
print(1)
print(2)
print(4)
print_above(3, max_columns=get_terminal_size().columns, current_is_empty=True) #This line will be an empty line, so current_is_empty = True


SELECT_CHARACTER_RENDITION(SET_BOLD_MODE, FOREGROND_RED, BACKGROND_WHITE)
# Or
print(1)
print(2)
print(4, end='')
print_above(3, max_columns=get_terminal_size().columns)
SELECT_CHARACTER_RENDITION(SCR_RESET)
