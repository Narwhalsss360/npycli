from __future__ import annotations
from collections.abc import Iterable
from typing import Optional, Any, TextIO
from dataclasses import dataclass, field
from re import findall


@dataclass(frozen=True)
class ANSIControl:
    CSI = "\u001B["

    name: str
    sequence: str
    no_of_arguments: int = field(default=0)
    no_of_default_arguments: int = field(default=0)
    instance_without_args: Optional[ANSIControl] = field(default=None)

    @staticmethod
    def send(ansi_control: ANSIControl | str, repeat: int = 1, flush: bool = False, file: Optional[TextIO] = None) -> None:
        if isinstance(ansi_control, ANSIControl):
            for i in range(repeat):
                print(str(ansi_control), end="", file=file, flush=(i == repeat - 1 and flush))
        else:
            if not ansi_control.startswith(ANSIControl.CSI):
                raise ValueError(f"Sequence {ansi_control} does not start with ANSI CSI")
            for i in range(repeat):
                print(ansi_control, end="", file=file, flush=(i == repeat - 1 and flush))

    @property
    def has_args(self) -> bool:
        return self.instance_without_args is not None

    @property
    def with_no_args(self) -> ANSIControl:
        return self.instance_without_args if self.instance_without_args else self

    def with_args(self, *args: Any) -> ANSIControl:
        if self.has_args:
            return self

        if len(args) > self.no_of_arguments:
            raise ValueError(f"{ANSIControl.with_args}({self.name}) Too many arguments supplied")

        if len(args) < self.no_of_arguments - self.no_of_default_arguments:
            raise ValueError(f"{ANSIControl.with_args}({self.name}) Not enough arguments supplied")

        sequence: str = ""

        last: int = len(args) - 1
        for position, arg in enumerate(args):
            sequence += str(arg)
            if position != last:
                sequence += ";"
        sequence += self.sequence

        return ANSIControl(self.name, sequence, self.no_of_arguments, self.no_of_default_arguments, self)

    def __call__(self, *args: Any, repeat: int = 1, flush: bool = False, file: Optional[TextIO] = None) -> ANSIControl:
        if self.has_args:
            assert self.instance_without_args is not None
            replaced_args: ANSIControl = self.instance_without_args.with_args(*args)
            ANSIControl.send(replaced_args, repeat, flush, file)
            return replaced_args
        else:
            ANSIControl.send(self.with_args(*args), repeat, flush, file)
            return self

    def __str__(self) -> str:
        if not self.has_args:
            return str(self.with_args())
        return f"{ANSIControl.CSI}{self.sequence}"


def send_ansi(ansi_control: ANSIControl | str, repeat: int = 1, flush: bool = False, file: Optional[TextIO] = None) -> None:
    ANSIControl.send(ansi_control, repeat, flush, file)


__controls: dict[str, ANSIControl] = {}
__constants: dict[str, int] = {}


CURSOR_UP: ANSIControl = ANSIControl("CURSOR_UP", "A", 1, 1)
__controls["CURSOR_UP"] = CURSOR_UP

CURSOR_DOWN: ANSIControl = ANSIControl("CURSOR_DOWN", "B", 1, 1)
__controls["CURSOR_DOWN"] = CURSOR_DOWN

CURSOR_FORWARD: ANSIControl = ANSIControl("CURSOR_FORWARD", "C", 1, 1)
__controls["CURSOR_FORWARD"] = CURSOR_FORWARD

CURSOR_BACK: ANSIControl = ANSIControl("CURSOR_BACK", "D", 1, 1)
__controls["CURSOR_BACK"] = CURSOR_BACK

CURSOR_NEXT_LINE: ANSIControl = ANSIControl("CURSOR_NEXT_LINE", "E", 1, 1)
__controls["CURSOR_NEXT_LINE"] = CURSOR_NEXT_LINE

CURSOR_PREVIOUS_LINE: ANSIControl = ANSIControl("CURSOR_PREVIOUS_LINE", "F", 1, 1)
__controls["CURSOR_PREVIOUS_LINE"] = CURSOR_PREVIOUS_LINE

CURSOR_HORIZONTAL_ABSOLUTE: ANSIControl = ANSIControl("CURSOR_HORIZONTAL_ABSOLUTE", "G", 1, 1)
__controls["CURSOR_HORIZONTAL_ABSOLUTE"] = CURSOR_HORIZONTAL_ABSOLUTE

CURSOR_POSITION: ANSIControl = ANSIControl("CURSOR_POSITION", "H", 2)
__controls["CURSOR_POSITION"] = CURSOR_POSITION

ERASE_IN_DISPLAY: ANSIControl = ANSIControl("ERASE_IN_DISPLAY", "J", 1, 1)
__controls["ERASE_IN_DISPLAY"] = ERASE_IN_DISPLAY

ERASE_IN_DISPLAY_TO_END: int = 0
__constants["ERASE_IN_DISPLAY_TO_END"] = ERASE_IN_DISPLAY_TO_END

ERASE_IN_DISPLAY_TO_BEGINNING: int = 1
__constants["ERASE_IN_DISPLAY_TO_BEGINNING"] = ERASE_IN_DISPLAY_TO_BEGINNING

ERASE_IN_DISPLAY_ALL: int = 2
__constants["ERASE_IN_DISPLAY_ALL"] = ERASE_IN_DISPLAY_ALL

ERASE_IN_LINE: ANSIControl = ANSIControl("ERASE_IN_LINE", "K", 1, 1)
__controls["ERASE_IN_LINE"] = ERASE_IN_LINE

ERASE_IN_LINE_END: int = 0
__constants["ERASE_IN_LINE_END"] = ERASE_IN_LINE_END

ERASE_IN_LINE_BEGINNING: int = 1
__constants["ERASE_IN_LINE_BEGINNING"] = ERASE_IN_DISPLAY_TO_BEGINNING

ERASE_IN_LINE_ALL: int = 2
__constants["ERASE_IN_LINE_ALL"] = ERASE_IN_LINE_ALL

SCROLL_UP: ANSIControl = ANSIControl("SCROLL_UP", "T", 1, 1)
__controls["SCROLL_UP"] = SCROLL_UP

SCROLL_DOWN: ANSIControl = ANSIControl("SCROLL_DOWN", "S", 1, 1)
__controls["SCROLL_DOWN"] = SCROLL_DOWN

HORIZONTAL_VERTICAL_POSITION: ANSIControl = ANSIControl("HORIZONTAL_VERTICAL_POSITION", "f", 2)
__controls["HORIZONTAL_VERTICAL_POSITION"] = HORIZONTAL_VERTICAL_POSITION

SELECT_CHARACTER_RENDITION: ANSIControl = ANSIControl("SELECT_CHARACTER_RENDITION", "m", 3, 3)
__controls["SELECT_CHARACTER_RENDITION"] = SELECT_CHARACTER_RENDITION

AUX_PORT_ON: ANSIControl = ANSIControl("AUX_PORT_ON", "5i")
__controls["AUX_PORT_ON"] = AUX_PORT_ON

AUX_PORT_OFF: ANSIControl = ANSIControl("AUX_PORT_OFF", "4i")
__controls["AUX_PORT_OFF"] = AUX_PORT_OFF

DEVICE_STATUS_REPORT: ANSIControl = ANSIControl("DEVICE_STATUS_REPORT", "6n")
__controls["DEVICE_STATUS_REPORT"] = DEVICE_STATUS_REPORT

CURSOR_POSITION_REPORT: ANSIControl = ANSIControl("CURSOR_POSITION_REPORT", "R")
__controls["CURSOR_POSITION_REPORT"] = CURSOR_POSITION_REPORT


INSERT_NEW_LINE: ANSIControl = ANSIControl("INSERT_NEW_LINE", "L")
__controls["INSERT_NEW_LINE"] = INSERT_NEW_LINE


SAVE_CURRENT_CURSOR_POSITION: ANSIControl = ANSIControl("SAVE_CURRENT_CURSOR_POSITION", "s")
__controls["SAVE_CURRENT_CURSOR_POSITION"] = SAVE_CURRENT_CURSOR_POSITION

RESTORE_SAVED_CURSOR_POSITION: ANSIControl = ANSIControl("RESTORE_SAVED_CURSOR_POSITION", "u")
__controls["RESTORE_SAVED_CURSOR_POSITION"] = RESTORE_SAVED_CURSOR_POSITION

SHOW_CURSOR: ANSIControl = ANSIControl("SHOW_CURSOR", "?25h")
__controls["SHOW_CURSOR"] = SHOW_CURSOR

HIDE_CURSOR: ANSIControl = ANSIControl("HIDE_CURSOR", "?25l")
__controls["HIDE_CURSOR"] = HIDE_CURSOR

USE_ALTERNATE_SCREEN_BUFFER: ANSIControl = ANSIControl("USE_ALTERNATE_SCREEN_BUFFER", "?1049h")
__controls["USE_ALTENATE_SCREEN_BUFFER"] = USE_ALTERNATE_SCREEN_BUFFER

USE_MAIN_SCREEN_BUFFER: ANSIControl = ANSIControl("USE_MAIN_SCREEN_BUFFER", "?1049h")
__controls["USE_MAIN_SCREEN_BUFFER"] = USE_MAIN_SCREEN_BUFFER


DELETE_LINE: ANSIControl = ANSIControl("DELETE_LINE", "M", 1, 1)
__controls["DELETE_LINE"] = DELETE_LINE

REMOVE_LINE: ANSIControl = ANSIControl("REMOVE_LINE", "M")
__controls["REMOVE_LINE"] = REMOVE_LINE

REMOVE_CHARACTER: ANSIControl = ANSIControl("REMOVE_CHARACTER", "P")
__controls["REMOVE_CHARACTER"] = REMOVE_CHARACTER


SCR_RESET: int = 0
__constants["SCR_RESET"] = SCR_RESET


FOREGROUND_BLACK: int = 30
__constants["FOREGROUND_BLACK"] = FOREGROUND_BLACK

FOREGROUND_RED: int = 31
__constants["FOREGROUND_RED"] = FOREGROUND_RED

FOREGROUND_GREEN: int = 32
__constants["FOREGROUND_GREEN"] = FOREGROUND_GREEN

FOREGROUND_YELLOW: int = 33
__constants["FOREGROUND_YELLOW"] = FOREGROUND_YELLOW

FOREGROUND_BLUE: int = 34
__constants["FOREGROUND_BLUE"] = FOREGROUND_BLUE

FOREGROUND_MAGENTA: int = 35
__constants["FOREGROUND_MAGENTA"] = FOREGROUND_MAGENTA

FOREGROUND_CYAN: int = 36
__constants["FOREGROUND_CYAN"] = FOREGROUND_CYAN

FOREGROUND_WHITE: int = 37
__constants["FOREGROUND_WHITE"] = FOREGROUND_WHITE

FOREGROUND_DEFAULT: int = 38
__constants["FOREGROUND_DEFAULT"] = FOREGROUND_DEFAULT


BACKGROUND_BLACK: int = FOREGROUND_BLACK + 10
__constants["BACKGROUND_BLACK"] = BACKGROUND_BLACK

BACKGROUND_RED: int = FOREGROUND_RED + 10
__constants["BACKGROUND_RED"] = BACKGROUND_RED

BACKGROUND_GREEN: int = FOREGROUND_GREEN + 10
__constants["BACKGROUND_GREEN"] = BACKGROUND_GREEN

BACKGROUND_YELLOW: int = FOREGROUND_YELLOW + 10
__constants["BACKGROUND_YELLOW"] = BACKGROUND_YELLOW

BACKGROUND_BLUE: int = FOREGROUND_BLUE + 10
__constants["BACKGROUND_BLUE"] = BACKGROUND_BLUE

BACKGROUND_MAGENTA: int = FOREGROUND_MAGENTA + 10
__constants["BACKGROUND_MAGENTA"] = BACKGROUND_MAGENTA

BACKGROUND_CYAN: int = FOREGROUND_CYAN + 10
__constants["BACKGROUND_CYAN"] = BACKGROUND_CYAN

BACKGROUND_WHITE: int = FOREGROUND_WHITE + 10
__constants["BACKGROUND_WHITE"] = BACKGROUND_WHITE

BACKGROUND_DEFAULT: int = FOREGROUND_DEFAULT + 10
__constants["BACKGROUND_DEFAULT"] = BACKGROUND_DEFAULT


SET_BOLD_MODE: int = 1
__constants["SET_BOLD_MODE"] = SET_BOLD_MODE

SET_DIM_MODE: int = 2
__constants["SET_DIM_MODE"] = SET_DIM_MODE

SET_ITALIC_MODE: int = 3
__constants["SET_ITALIC_MODE"] = SET_ITALIC_MODE

SET_UNDERLINE_MODE: int = 4
__constants["SET_UNDERLINE_MODE"] = SET_UNDERLINE_MODE

SET_BLINKING_MODE: int = 5
__constants["SET_BLINKING_MODE"] = SET_BLINKING_MODE

SET_INVERSE_MODE: int = 7
__constants["SET_INVERSE_MODE"] = SET_INVERSE_MODE

SET_INVISIBLE_MODE: int = 8
__constants["SET_INVISIBLE_MODE"] = SET_INVISIBLE_MODE

SET_STRIKETHROUGH_MODE: int = 9
__constants["SET_STRIKETHROUGH_MODE"] = SET_STRIKETHROUGH_MODE


def controls() -> dict[str, ANSIControl]:
    return __controls


def constants() -> dict[str, int]:
    return __constants


def extract_asni_args(char_iter: Iterable[str], main_control_sequence: str, max_iterations: int = -1) -> tuple[str, ...]:
    args: list[str] = []
    arg_index: int = -1
    iterations: int = 0
    for c in char_iter:
        if iterations == max_iterations:
            raise StopIteration

        iterations += 1
        if len(c) != 1:
            raise ValueError("Must be a character iterartor")
        if arg_index == -1:
            args.append("")
            arg_index = 0
        if c == ";":
            args.append("")
            arg_index += 1
            continue
        args[arg_index] += c
        if args[arg_index].endswith(main_control_sequence):
            args[arg_index] = args[arg_index][0:-len(main_control_sequence)]
            break
    return tuple(args)


def extract_ansi(char_iter: Iterable[str], max_iterations: int = -1) -> tuple[Optional[ANSIControl], tuple[str, ...], int, int]:
    iterations: int = 0
    s: str = ""
    start_index: int = 0
    iterator = iter(char_iter)
    while not s.endswith(ANSIControl.CSI):
        if iterations == max_iterations:
            raise StopIteration

        try:
            c: str = next(iterator)
        except StopIteration:
            return None, (), -1, -1

        if len(c) != 1:
            raise TypeError("Must be a character iterartor")
        s += c
        start_index += 1
        iterations += 1

    end_index: int = start_index
    start_index -= len(ANSIControl.CSI)
    s = ""

    while True:
        if iterations == max_iterations:
            raise StopIteration

        try:
            c: str = next(iterator)
        except StopIteration:
            return None, (), -1, -1
        s += c
        iterations += 1

        if (control := next(filter(lambda a: s.endswith(a.sequence), controls().values()), None)) is None:
            end_index += 1
            continue

        args: tuple[str, ...] = extract_asni_args(s, control.sequence, len(s))
        return (
            ANSIControl(
                control.name,
                f"{s}{control.sequence}",
                len(args),
                control.no_of_default_arguments,
                control if args else None
            ),
            args,
            start_index,
            end_index + len(control.sequence)
        )


ANSI_CONTROL_SEQUENCE_REGEX: str = r"\x1B\[([0-?]*)[\x20-/]*([@-~])"


def strip_ansi(text: str) -> str:
    stripped: str = text
    for matched_groups in findall(ANSI_CONTROL_SEQUENCE_REGEX, text):
        stripped = stripped.replace(f"{ANSIControl.CSI}{"".join(matched_groups)}", "")
    return stripped


__all__ = [
    "ANSIControl",
    "send_ansi",
    "controls",
    "constants",
    "extract_asni_args",
    "extract_ansi",
    "strip_ansi",
    "CURSOR_UP",
    "CURSOR_DOWN",
    "CURSOR_FORWARD",
    "CURSOR_BACK",
    "CURSOR_NEXT_LINE",
    "CURSOR_PREVIOUS_LINE",
    "CURSOR_HORIZONTAL_ABSOLUTE",
    "CURSOR_POSITION",
    "ERASE_IN_DISPLAY",
    "ERASE_IN_DISPLAY_TO_END",
    "ERASE_IN_DISPLAY_TO_BEGINNING",
    "ERASE_IN_DISPLAY_ALL",
    "ERASE_IN_LINE",
    "ERASE_IN_LINE_END",
    "ERASE_IN_LINE_BEGINNING",
    "ERASE_IN_LINE_ALL",
    "SCROLL_UP",
    "SCROLL_DOWN",
    "HORIZONTAL_VERTICAL_POSITION",
    "SELECT_CHARACTER_RENDITION",
    "AUX_PORT_ON",
    "AUX_PORT_OFF",
    "DEVICE_STATUS_REPORT",
    "CURSOR_POSITION_REPORT",
    "INSERT_NEW_LINE",
    "SAVE_CURRENT_CURSOR_POSITION",
    "RESTORE_SAVED_CURSOR_POSITION",
    "SHOW_CURSOR",
    "HIDE_CURSOR",
    "USE_ALTERNATE_SCREEN_BUFFER",
    "USE_MAIN_SCREEN_BUFFER",
    "DELETE_LINE",
    "REMOVE_LINE",
    "REMOVE_CHARACTER",
    "SCR_RESET",
    "FOREGROUND_BLACK",
    "FOREGROUND_RED",
    "FOREGROUND_GREEN",
    "FOREGROUND_YELLOW",
    "FOREGROUND_BLUE",
    "FOREGROUND_MAGENTA",
    "FOREGROUND_CYAN",
    "FOREGROUND_WHITE",
    "FOREGROUND_DEFAULT",
    "BACKGROUND_BLACK",
    "BACKGROUND_RED",
    "BACKGROUND_GREEN",
    "BACKGROUND_YELLOW",
    "BACKGROUND_BLUE",
    "BACKGROUND_MAGENTA",
    "BACKGROUND_CYAN",
    "BACKGROUND_WHITE",
    "BACKGROUND_DEFAULT",
    "SET_BOLD_MODE",
    "SET_DIM_MODE",
    "SET_ITALIC_MODE",
    "SET_UNDERLINE_MODE",
    "SET_BLINKING_MODE",
    "SET_INVERSE_MODE",
    "SET_INVISIBLE_MODE",
    "SET_STRIKETHROUGH_MODE",
    "ANSI_CONTROL_SEQUENCE_REGEX",
]
