import os
import time
from re import match
from sys import stdout

from npycli.ansi.const.dsr import (
    A_REPORT_OF_THE_ACTIVE_PRESENTATION_POSITION_OR_OF_THE_ACTIVE_DATA_POSITION_IN_THE_FORM_OF_ACTIVE_POSITION_REPORT_IS_REQUESTED,
)
from npycli.ansi.parsing import extract_control_sequence
from npycli.ansi.sequences import DSR

DEVICE_STATUS_REPORT_RE = r"\x1b\[[0-9]+;[0-9]+R"
ACTIVE_POSITION_REPORT_REQUEST = A_REPORT_OF_THE_ACTIVE_PRESENTATION_POSITION_OR_OF_THE_ACTIVE_DATA_POSITION_IN_THE_FORM_OF_ACTIVE_POSITION_REPORT_IS_REQUESTED


def extract_position_from_report(report: str) -> tuple[int, int]:
    if not match(DEVICE_STATUS_REPORT_RE, report):
        raise ValueError(f"Did not get device status report: {report!r}")

    return int(report[report.index("[") + 1 : report.index(";")]), int(
        report[report.index(";") + 1 : -1]
    )


def posix_main() -> None:
    assert os.name != "nt"
    import select
    import sys
    import termios
    import tty

    def flush_keypress() -> None:
        initial_flags = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())
        while select.select([sys.stdin], [], [], 0.0)[0]:
            sys.stdin.buffer.read(1)
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, initial_flags)

    # Flush away anything entered before this main function
    flush_keypress()

    DSR(6, file=stdout)
    # Send ANSI right after flush, so it's the first thing

    initial_flags = termios.tcgetattr(sys.stdin.fileno())
    flags = list(initial_flags)
    flags[3] &= ~termios.ICANON
    flags[3] &= ~termios.ECHO
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, flags)

    report: str = ""

    i = 0
    while True:
        c = sys.stdin.buffer.read(1).decode()
        report += c
        if c == "R":
            break
        i += 1
        if i == 16:
            print("Error reading response!")
            return
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, initial_flags)

    print(extract_position_from_report(report))


def win_main() -> None:
    assert os.name == "nt"
    import ctypes
    import msvcrt
    from ctypes import wintypes

    kernel32 = ctypes.windll.kernel32
    STD_INPUT_HANDLE = -10
    hStdin = kernel32.GetStdHandle(STD_INPUT_HANDLE)

    old_mode = wintypes.DWORD()
    kernel32.GetConsoleMode(hStdin, ctypes.byref(old_mode))

    ENABLE_LINE_INPUT = 0x0002
    ENABLE_ECHO_INPUT = 0x0004
    ENABLE_PROCESSED_INPUT = 0x0001
    ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
    RAW_INPUT_MODE = (
        old_mode.value
        & ~(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_PROCESSED_INPUT)
    ) | ENABLE_VIRTUAL_TERMINAL_INPUT
    kernel32.SetConsoleMode(hStdin, RAW_INPUT_MODE)

    def flush_keypress() -> None:
        kernel32.FlushConsoleInputBuffer(hStdin)

    def win_read_stream_generator(timeout_seconds: float = 0.5):
        start_time = time.time()
        num_events = wintypes.DWORD()
        has_started = False

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                return

            if (
                kernel32.GetNumberOfConsoleInputEvents(hStdin, ctypes.byref(num_events))
                and num_events.value > 0
            ):
                char = msvcrt.getwch()
                if char:
                    if not has_started:
                        has_started = True
                    yield ord(char)
                    start_time = time.time()
                    timeout_seconds = 0.1
            else:
                time.sleep(0.001)

    try:
        flush_keypress()
        DSR(ACTIVE_POSITION_REPORT_REQUEST, file=stdout)

        result = extract_control_sequence(win_read_stream_generator(10), 16)
        if result is None:
            print("Error reading response!")
            return

        print(
            f"Read control sequence {result.sequence.name} ({result.sequence.abbreviation}):"
        )
        print(f"\tArguments: {result.sequence.token.arguments}")
        print(f"\tLength: {result.end_index - result.start_index}")
    finally:
        kernel32.SetConsoleMode(hStdin, old_mode)


if __name__ == "__main__":
    if os.name == "nt":
        win_main()
    else:
        posix_main()
