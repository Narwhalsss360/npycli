from __future__ import annotations
from collections.abc import Iterable
from typing import Optional, Any
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ANSIControl:
    CSI = "\u001B["

    name: str
    sequence: str
    no_of_arguments: int = field(default=0)
    no_of_default_arguments: int = field(default=0)
    instance_without_args: Optional[ANSIControl] = field(default=None)

    @staticmethod
    def send(ansi_control: ANSIControl | str, repeat: int = 1) -> None:
        if isinstance(ansi_control, ANSIControl):
            for i in range(repeat):
                print(str(ansi_control), end="", flush=i == repeat - 1)
        else:
            if not ansi_control.startswith(ANSIControl.CSI):
                raise ValueError(f"Sequence {ansi_control} does not start with ANSI CSI")
            for i in range(repeat):
                print(ansi_control, end="", flush=i == repeat - 1)

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

        sequence: str= ""

        last: int = len(args) - 1
        for position, arg in enumerate(args):
            sequence += str(arg)
            if position != last:
                sequence += ";"
        sequence += self.sequence

        return ANSIControl(self.name, sequence, self.no_of_arguments, self.no_of_default_arguments, self)

    def __call__(self, *args: Any, repeat: int = 1) -> ANSIControl:
        if self.has_args:
            assert self.instance_without_args is not None
            replaced_args: ANSIControl = self.instance_without_args.with_args(*args)
            ANSIControl.send(replaced_args, repeat)
            return replaced_args
        else:
            ANSIControl.send(self.with_args(*args), repeat)
            return self

    def __str__(self) -> str:
        if not self.has_args:
            return str(self.with_args())
        return f"{ANSIControl.CSI}{self.sequence}"


def send_ansi(ansi_control: ANSIControl | str, repeat: int = 1) -> None:
    ANSIControl.send(ansi_control, repeat)


__controls: dict[str, ANSIControl] = {}
__constants: dict[str, int] = {}


__controls["CURSOR_UP"] = ANSIControl("CURSOR_UP", "A", 1, 1)
CURSOR_UP: ANSIControl = __controls["CURSOR_UP"]

__controls["CURSOR_DOWN"] = ANSIControl("CURSOR_DOWN", "B", 1, 1)
CURSOR_DOWN: ANSIControl = __controls["CURSOR_DOWN"]

__controls["CURSOR_FORWARD"] = ANSIControl("CURSOR_FORWARD", "C", 1, 1)
CURSOR_FORWARD: ANSIControl = __controls["CURSOR_FORWARD"]

__controls["CURSOR_BACK"] = ANSIControl("CURSOR_BACK", "D", 1, 1)
CURSOR_BACK: ANSIControl = __controls["CURSOR_BACK"]

__controls["CURSOR_NEXT_LINE"] = ANSIControl("CURSOR_NEXT_LINE", "E", 1, 1)
CURSOR_NEXT_LINE: ANSIControl = __controls["CURSOR_NEXT_LINE"]

__controls["CURSOR_PREVIOUS_LINE"] = ANSIControl("CURSOR_PREVIOUS_LINE", "F", 1, 1)
CURSOR_PREVIOUS_LINE: ANSIControl = __controls["CURSOR_PREVIOUS_LINE"]

__controls["CURSOR_HORIZONTAL_ABSOLUTE"] = ANSIControl("CURSOR_HORIZONTAL_ABSOLUTE", "G", 1, 1)
CURSOR_HORIZONTAL_ABSOLUTE: ANSIControl = __controls["CURSOR_HORIZONTAL_ABSOLUTE"]

__controls["CURSOR_POSITION"] = ANSIControl("CURSOR_POSITION", "H", 2)
CURSOR_POSITION: ANSIControl = __controls["CURSOR_POSITION"]

__controls["ERASE_IN_DISPLAY"] = ANSIControl("ERASE_IN_DISPLAY", "J", 1, 1)
ERASE_IN_DISPLAY: ANSIControl = __controls["ERASE_IN_DISPLAY"]

__constants["ERASE_IN_DISPLAY_TO_END"] = 0
ERASE_IN_DISPLAY_TO_END: int = __constants["ERASE_IN_DISPLAY_TO_END"]

__constants["ERASE_IN_DISPLAY_TO_BEGINNING"] = 1
ERASE_IN_DISPLAY_TO_BEGINNING: int = __constants["ERASE_IN_DISPLAY_TO_BEGINNING"]

__constants["ERASE_IN_DISPLAY_ALL"] = 2
ERASE_IN_DISPLAY_ALL: int = __constants["ERASE_IN_DISPLAY_ALL"]

__controls["ERASE_IN_LINE"] = ANSIControl("ERASE_IN_LINE", "K", 1, 1)
ERASE_IN_LINE: ANSIControl = __controls["ERASE_IN_LINE"]

__constants["ERASE_IN_LINE_END"] = 0
ERASE_IN_LINE_END: int = __constants["ERASE_IN_LINE_END"]

__constants["ERASE_IN_LINE_BEGINNING"] = 1
ERASE_IN_LINE_BEGINNING: int = __constants["ERASE_IN_LINE_BEGINNING"]

__constants["ERASE_IN_LINE_ALL"] = 2
ERASE_IN_LINE_ALL: int = __constants["ERASE_IN_LINE_ALL"]

__controls["SCROLL_UP"] = ANSIControl("SCROLL_UP", "T", 1, 1)
SCROLL_UP: ANSIControl = __controls["SCROLL_UP"]

__controls["SCROLL_DOWN"] = ANSIControl("SCROLL_DOWN", "S", 1, 1)
SCROLL_DOWN: ANSIControl = __controls["SCROLL_DOWN"]

__controls["HORIZONTAL_VERTICAL_POSITION"] = ANSIControl("HORIZONTAL_VERTICAL_POSITION", "f", 2)
HORIZONTAL_VERTICAL_POSITION: ANSIControl = __controls["HORIZONTAL_VERTICAL_POSITION"]

__controls["SELECT_CHARACTER_RENDITION"] = ANSIControl("SELECT_CHARACTER_RENDITION", "m", 3, 3)
SELECT_CHARACTER_RENDITION: ANSIControl = __controls["SELECT_CHARACTER_RENDITION"]

__controls["AUX_PORT_ON"] = ANSIControl("AUX_PORT_ON", "5i")
AUX_PORT_ON: ANSIControl = __controls["AUX_PORT_ON"]

__controls["AUX_PORT_OFF"] = ANSIControl("AUX_PORT_OFF", "4i")
AUX_PORT_OFF: ANSIControl = __controls["AUX_PORT_OFF"]

__controls["DEVICE_STATUS_REPORT"] = ANSIControl("DEVICE_STATUS_REPORT", "6n")
DEVICE_STATUS_REPORT: ANSIControl = __controls["DEVICE_STATUS_REPORT"]

__controls["CURSOR_POSITION_REPORT"] = ANSIControl("CURSOR_POSITION_REPORT", "R")
CURSOR_POSITION_REPORT: ANSIControl = __controls["CURSOR_POSITION_REPORT"]


__controls["INSERT_NEW_LINE"] = ANSIControl("INSERT_NEW_LINE", "L")
INSERT_NEW_LINE: ANSIControl = __controls["INSERT_NEW_LINE"]


__controls["SAVE_CURRENT_CURSOR_POSITION"] = ANSIControl("SAVE_CURRENT_CURSOR_POSITION", "s")
SAVE_CURRENT_CURSOR_POSITION: ANSIControl = __controls["SAVE_CURRENT_CURSOR_POSITION"]

__controls["RESTORE_SAVED_CURSOR_POSITION"] = ANSIControl("RESTORE_SAVED_CURSOR_POSITION", "u")
RESTORE_SAVED_CURSOR_POSITION: ANSIControl = __controls["RESTORE_SAVED_CURSOR_POSITION"]

__controls["SHOW_CURSOR"] = ANSIControl("SHOW_CURSOR", "?25h")
SHOW_CURSOR: ANSIControl = __controls["SHOW_CURSOR"]

__controls["HIDE_CURSOR"] = ANSIControl("HIDE_CURSOR", "?25l")
HIDE_CURSOR: ANSIControl = __controls["HIDE_CURSOR"]


__controls["REMOVE_LINE"] = ANSIControl("REMOVE_LINE", "M")
REMOVE_LINE: ANSIControl = __controls["REMOVE_LINE"]

__controls["REMOVE_CHARACTER"] = ANSIControl("REMOVE_CHARACTER", "P")
REMOVE_CHARACTER: ANSIControl = __controls["REMOVE_CHARACTER"]



__constants["SCR_RESET"] = 0
SCR_RESET: int = __constants["SCR_RESET"]



__constants["FOREGROND_BLACK"] = 30
FOREGROND_BLACK: int = __constants["FOREGROND_BLACK"]

__constants["FOREGROND_RED"] = 31
FOREGROND_RED: int = __constants["FOREGROND_RED"]

__constants["FOREGROND_GREEN"] = 32
FOREGROND_GREEN: int = __constants["FOREGROND_GREEN"]

__constants["FOREGROND_YELLOW"] = 33
FOREGROND_YELLOW: int = __constants["FOREGROND_YELLOW"]

__constants["FOREGROND_BLUE"] = 34
FOREGROND_BLUE: int = __constants["FOREGROND_BLUE"]

__constants["FOREGROND_MAGENTA"] = 35
FOREGROND_MAGENTA: int = __constants["FOREGROND_MAGENTA"]

__constants["FOREGROND_CYAN"] = 36
FOREGROND_CYAN: int = __constants["FOREGROND_CYAN"]

__constants["FOREGROND_WHITE"] = 37
FOREGROND_WHITE: int = __constants["FOREGROND_WHITE"]

__constants["FOREGROND_DEFAULT"] = 38
FOREGROND_DEFAULT: int = __constants["FOREGROND_DEFAULT"]



__constants["BACKGROND_BLACK"] = FOREGROND_BLACK + 10
BACKGROND_BLACK: int = __constants["BACKGROND_BLACK"]

__constants["BACKGROND_RED"] = FOREGROND_RED + 10
BACKGROND_RED: int = __constants["BACKGROND_RED"]

__constants["BACKGROND_GREEN"] = FOREGROND_GREEN + 10
BACKGROND_GREEN: int = __constants["BACKGROND_GREEN"]

__constants["BACKGROND_YELLOW"] = FOREGROND_YELLOW + 10
BACKGROND_YELLOW: int = __constants["BACKGROND_YELLOW"]

__constants["BACKGROND_BLUE"] = FOREGROND_BLUE + 10
BACKGROND_BLUE: int = __constants["BACKGROND_BLUE"]

__constants["BACKGROND_MAGENTA"] = FOREGROND_MAGENTA + 10
BACKGROND_MAGENTA: int = __constants["BACKGROND_MAGENTA"]

__constants["BACKGROND_CYAN"] = FOREGROND_CYAN + 10
BACKGROND_CYAN: int = __constants["BACKGROND_CYAN"]

__constants["BACKGROND_WHITE"] = FOREGROND_WHITE + 10
BACKGROND_WHITE: int = __constants["BACKGROND_WHITE"]

__constants["BACKGROND_DEFAULT"] = FOREGROND_DEFAULT + 10
BACKGROND_DEFAULT: int = __constants["BACKGROND_DEFAULT"]



__constants["SET_BOLD_MODE"] = 1
SET_BOLD_MODE: int = __constants["SET_BOLD_MODE"]

__constants["SET_DIM_MODE"] = 2
SET_DIM_MODE: int = __constants["SET_DIM_MODE"]

__constants["SET_ITALIC_MODE"] = 3
SET_ITALIC_MODE: int = __constants["SET_ITALIC_MODE"]

__constants["SET_UNDERLINE_MODE"] = 4
SET_UNDERLINE_MODE: int = __constants["SET_UNDERLINE_MODE"]

__constants["SET_BLINKING_MODE"] = 5
SET_BLINKING_MODE: int = __constants["SET_BLINKING_MODE"]

__constants["SET_INVERSE_MODE"] = 7
SET_INVERSE_MODE: int = __constants["SET_INVERSE_MODE"]

__constants["SET_INVISIBLE_MODE"] = 8
SET_INVISIBLE_MODE: int = __constants["SET_INVISIBLE_MODE"]

__constants["SET_STRIKETHROUGH_MODE"] = 9
SET_STRIKETHROUGH_MODE: int = __constants["SET_STRIKETHROUGH_MODE"]


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
            raise ValueError("Must be a character iterartor")
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
        return ANSIControl(control.name, f"{s}{control.sequence}", len(args), control.no_of_default_arguments, control), args, start_index, end_index + len(control.sequence)