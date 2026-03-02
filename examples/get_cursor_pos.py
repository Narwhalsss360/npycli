import os
from re import match
from npycli.ansi import ANSIControl, DEVICE_STATUS_REPORT, extract_ansi


DEVICE_STATUS_REPORT_RE = r"\x1b\[[0-9]+;[0-9]+R"


def extract_position_from_report(report: str) -> tuple[int, int]:
    if not match(DEVICE_STATUS_REPORT_RE, report):
        raise ValueError(f"Did not get device status report: {repr(report)}")

    return int(report[report.index('[') + 1:report.index(';')]), int(report[report.index(';') + 1:-1])


def posix_main() -> None:
    assert os.name != "nt"
    import termios
    import sys
    import select
    import tty

    def flush_keypress() -> None:
        initial_flags = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())
        while select.select([sys.stdin], [], [], 0.0)[0]:
            sys.stdin.buffer.read(1)
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, initial_flags)

    # Flush awau anything entered before this main function
    flush_keypress()

    ANSIControl.send(DEVICE_STATUS_REPORT)
    # Send ANSI right after flush, so it's the first thing

    initial_flags = termios.tcgetattr(sys.stdin.fileno())
    flags = list(initial_flags)
    flags[3] &= ~termios.ICANON
    flags[3] &= ~termios.ECHO
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, flags)

    report: str = ""

    while True:
        c = sys.stdin.buffer.read(1).decode()
        report += c
        if c == "R":
            break
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, initial_flags)

    print(extract_position_from_report(report))


def win_main() -> None:
    assert os.name == "nt"
    import msvcrt
    def flush_keypress() -> None:
        while True:
            if not msvcrt.kbhit():
                break

            c = msvcrt.getch()
            if c[0] == 0xe0:
                c = msvcrt.getch()
            break

    def getch_generator(max_iterations: int = -1):
        iterations: int = 0
        while True:
            if iterations == max_iterations:
                raise StopIteration
            yield msvcrt.getch().decode()
            iterations += 1

    flush_keypress()
    ANSIControl.send(DEVICE_STATUS_REPORT)
    control, args, start_index, end_index = extract_ansi(getch_generator(16))
    if control is None:
        print("Error reading response!")
        return

    print(f"Read control sequence {repr(control)}:")
    print(f"\t{tuple(int(arg) for arg in args)}")
    print(f"\tLength: {end_index - start_index}")


if __name__ == "__main__":
    if os.name == "nt":
        win_main()
    else:
        posix_main()
