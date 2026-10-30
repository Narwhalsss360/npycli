from os import get_terminal_size, terminal_size
from sys import stdout
from time import sleep

from npycli.ansi.const.p_rm import USE_MAIN_SCREEN_BUFFER
from npycli.ansi.const.p_sm import SHOW_CURSOR, USE_ALTERNATE_SCREEN_BUFFER
from npycli.ansi.sequences import CUP, P_RM, P_SM


def draw_screen(char: str, tsize: terminal_size) -> None:
    assert len(char) == 1
    CUP(0, 0, file=stdout)
    P_SM(SHOW_CURSOR, file=stdout)
    parity = True
    for _ in range(tsize.lines):
        for i in range(tsize.columns):
            if (i % 2 == 0) == parity:
                print(char, end="")
            else:
                print(" ", end="")

        print()
        parity = not parity
        if get_terminal_size() != tsize:
            draw_screen(char, get_terminal_size())
            return

    stdout.flush()


def main() -> None:
    P_SM(USE_ALTERNATE_SCREEN_BUFFER, file=stdout)
    for i in range(ord('A'), ord('Z') + 1):
        draw_screen(chr(i), get_terminal_size())
        sleep(0.5)
    P_RM(USE_MAIN_SCREEN_BUFFER, file=stdout)


if __name__ == "__main__":
    main()
