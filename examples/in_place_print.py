from os import get_terminal_size
from sys import stdout, stderr, argv
from time import sleep
from io import StringIO
from typing import Callable, Generator, TextIO, Any, Literal
from npycli.ansi import CURSOR_UP, DELETE_LINE, HIDE_CURSOR, INSERT_NEW_LINE, RESTORE_SAVED_CURSOR_POSITION, SAVE_CURRENT_CURSOR_POSITION, SCROLL_DOWN, CURSOR_DOWN, SELECT_CHARACTER_RENDITION, SCR_RESET, BACKGROND_RED, FOREGROND_WHITE, SET_BOLD_MODE
from npycli.parsing import create_literal_parser
from npycli import Command


def wrap_and_pad_lines(string: str, columns: int) -> str:
    lines: list[str] = string.split("\n")
    for i in range(len(lines)):
        if len(lines[i]) > columns:
            this, next = lines[i][:columns], lines[i][columns:]
            lines[i] = this
            lines.insert(i + 1, next)
        lines[i] = f"{lines[i].ljust(columns)}{"" if i == len(lines) - 1 else "\n"}"
    return "".join(lines)


type terminal_columns_type = int
type terminal_lines_type = int
type terminal_size_getter_type = Callable[[], tuple[terminal_columns_type, terminal_lines_type]]


class InPlacePrint:
    def __init__(self, terminal_size_getter: terminal_size_getter_type = get_terminal_size, file: TextIO = stdout) -> None:
        self.last_string: str | None = None
        self.terminal_size_getter: terminal_size_getter_type = terminal_size_getter
        self.file: TextIO = file

    def print(self, *values: Any, sep: str = " ", end: str = "\n", raise_on_too_short: bool = True) -> None:
        buffer: StringIO = StringIO()
        print(*values, sep=sep, end=end, file=buffer, flush=True)
        string: str = wrap_and_pad_lines(buffer.getvalue(), self.terminal_size_getter()[0])

        line_count: int = string.count('\n') + 1
        lines: int = self.terminal_size_getter()[1]
        if lines < line_count:
            if raise_on_too_short:
                raise ValueError("Not enough lines to print in place.")
            print(string, file=self.file, end="")
            self.last_string = None
            return

        if self.last_string is None:
            self.last_string = string
            if line_count > 1:
                SCROLL_DOWN(line_count - 1)
                INSERT_NEW_LINE(repeat=line_count - 1)
                CURSOR_UP(line_count - 1)
            print(string, file=self.file, end="")
            return

        repeats: int = self.last_string.count("\n") + 1
        for i in range(repeats):
            DELETE_LINE(file=self.file)
            if i != repeats - 1:
                CURSOR_UP(file=self.file)
        INSERT_NEW_LINE(repeat=line_count)
        print(string, file=self.file, end="")

        self.last_string = string

    def print_above(self, *args: Any, sep: str | None = " ") -> None:
        buffer: StringIO = StringIO()
        print(*args, sep=sep, end="", file=buffer, flush=True)
        output: str = buffer.getvalue()

        line_count: int = 1
        line_length: int = 0
        max_columns: int = self.terminal_size_getter()[0]
        for c in output:
            line_length += 1
            if line_length == max_columns or c == "\n":
                line_count += 1
                line_length = 0

        SAVE_CURRENT_CURSOR_POSITION()
        if self.last_string is None:
            print(output, flush=True, file=self.file)
            return

        last_string_line_count_offset: int = self.last_string.count("\n") if self.last_string else 0
        print("\n" * line_count, end="", file=self.file)
        CURSOR_UP(line_count + last_string_line_count_offset)
        INSERT_NEW_LINE(repeat=line_count)

        print(output, end='', flush=True, file=self.file)
        RESTORE_SAVED_CURSOR_POSITION()
        CURSOR_DOWN(line_count)

    def __call__(self, *values: Any, sep: str = " ", end: str = "\n", raise_on_too_short: bool = True) -> None:
        self.print(*values, sep=sep, end=end, raise_on_too_short=raise_on_too_short)


def bouncer(min: int, max: int, increasing: bool, max_iterations: int) -> Generator[int, Any, None]:
    assert min <= max
    i: int = 0
    n: int = min - 1 if increasing else max + 1
    while i != max_iterations:
        if increasing:
            if n == max:
                n -= 1
                increasing = False
            else:
                n += 1
        else:
            if n == min:
                n += 1
                increasing = True
            else:
                n -= 1
        yield n
        max_iterations += 1


type Direction = Literal["increasing", "decreasing"]
type BounceObject = Literal["numbers", "ball"]


def main(
    min: int = 0,
    max: int = 5,
    direction: Direction = "increasing",
    max_iterations: int = 100,
    sleep_interval: float = 0.25,
    bounce_object: BounceObject = "ball"
) -> None:
    in_place_print: InPlacePrint = InPlacePrint()
    if bounce_object == "ball":
        if min != 0:
            raise ValueError("min with ball must be 0")

    if max < min:
        raise ValueError("Must not have max < min")

    HIDE_CURSOR()
    bounces: int = -1
    bounce_message: str = f""
    for n in bouncer(min, max, direction == "increasing", max_iterations):
        if bounce_object == "numbers":
            s: str = f"{"\u2500" * len(bounce_message)}\n{"\n".join(str(i + bounces) for i in range(n))}"
        else:
            s: str = (
                f"{"\u2500" * len(bounce_message)}\n"
                f"{"\n" * (max - n)}{" " * (len(bounce_message) // 2)}*{n * "\n"}"
                f"\n{"\u2500" * len(bounce_message)}"
            )
        in_place_print(s, end="")
        if n == min:
            bounces += 1
            bounce_message: str = f"Bounce: {bounces}"
            in_place_print.print_above(bounce_message)
        sleep(sleep_interval)


if __name__ == "__main__":
    try:
        Command.create(main).exec_with(argv[1:], {
            Direction: create_literal_parser(Direction),
            BounceObject: create_literal_parser(BounceObject)
        })
    except KeyboardInterrupt:
        pass
    except ValueError as e:
        print(
            SELECT_CHARACTER_RENDITION.with_args(SET_BOLD_MODE, BACKGROND_RED, FOREGROND_WHITE),
            "ERROR",
            SELECT_CHARACTER_RENDITION.with_args(SCR_RESET),
            f": {e}",
            sep="",
            end="",
            file=stderr
        )