from os import get_terminal_size
from sys import stderr, argv
from time import sleep
from io import StringIO
from typing import Callable, Generator, Any, Literal
from npycli.ansi import CURSOR_UP, HIDE_CURSOR, INSERT_NEW_LINE, SELECT_CHARACTER_RENDITION, SCR_RESET, BACKGROUND_RED, FOREGROUND_WHITE, SET_BOLD_MODE, strip_ansi, SHOW_CURSOR
from npycli.parsing import create_literal_parser
from npycli import Command
import builtins


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
    def __init__(self) -> None:
        self.last_lines: list[str] | None = None

    @staticmethod
    def wrap(string: str, columns: int) -> list[str]:
        lines: list[str] = string.split("\n")
        for i in range(len(lines)):
            if len(strip_ansi(lines[i])) > columns:
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

    def print_above(self, *values: Any, sep: str = " ", end: str = "") -> None:
        buffer: StringIO = StringIO()
        print(*values, sep=sep, end=end, file=buffer, flush=True)
        terminal_size = get_terminal_size()
        lines: list[str] = InPlacePrint.wrap(buffer.getvalue(), terminal_size.columns)

        if not self.last_lines:
            print("\n".join(lines))
            return

        INSERT_NEW_LINE(repeat=len(lines))
        print("\n".join(lines))

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

    def __call__(self, *values: Any, sep: str = " ", end: str = "\n") -> bool:
        return self.print(*values, sep=sep, end=end)


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

    bounces: int = -1
    bounce_message: str = ""
    HIDE_CURSOR()
    try:
        for n in bouncer(min, max, direction == "increasing", max_iterations):
            bounce_message_lines: list[str] = [strip_ansi(line) for line in bounce_message.splitlines()]
            separator_width: int = len("  Bounce: 1") if len(bounce_message) == 0 else builtins.max(len(line) for line in bounce_message_lines)
            if bounce_object == "numbers":
                s: str = f"{"\u2500" * separator_width}\n{"\n".join(str(i + bounces) for i in range(n))}"
            else:
                s: str = (
                    f"{"\u2500" * separator_width}\n"
                    f"{"\n" * (max - n)}{" " * (separator_width // 2)}*{n * "\n"}"
                    f"\n{"\u2500" * separator_width}"
                )
            in_place_print(s, end="")
            if n == min:
                bounces += 1
                bounce_message: str = f"Next:\n  Bounce: {bounces}"
                in_place_print.print_above(bounce_message)
            sleep(sleep_interval)
    except KeyboardInterrupt:
        in_place_print.clear()
    except Exception:
        SHOW_CURSOR()
        raise
    finally:
        SHOW_CURSOR()


if __name__ == "__main__":
    try:
        Command.create(main).exec_with(argv[1:], {
            Direction: create_literal_parser(Direction),
            BounceObject: create_literal_parser(BounceObject)
        })
    except ValueError as e:
        print(
            SELECT_CHARACTER_RENDITION.with_args(SET_BOLD_MODE, BACKGROUND_RED, FOREGROUND_WHITE),
            "ERROR",
            SELECT_CHARACTER_RENDITION.with_args(SCR_RESET),
            f": {e}",
            sep="",
            end="",
            file=stderr
        )
