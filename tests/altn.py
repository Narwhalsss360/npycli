from sys import stdout
from os import get_terminal_size, terminal_size
from npycli.ansi import USE_ALTERNATE_SCREEN_BUFFER, USE_MAIN_SCREEN_BUFFER, CURSOR_POSITION, SHOW_CURSOR, SAVE_CURRENT_CURSOR_POSITION, RESTORE_SAVED_CURSOR_POSITION
from time import sleep


def draw_screen(char: str, tsize: terminal_size) -> None:
    assert len(char) == 1
    CURSOR_POSITION(0, 0)
    SHOW_CURSOR()
    parity = True
    for lineno in range(tsize.lines):
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
    USE_ALTERNATE_SCREEN_BUFFER()
    for i in range(ord('A'), ord('Z') + 1):
        draw_screen(chr(i), get_terminal_size())
        sleep(0.5)
    USE_MAIN_SCREEN_BUFFER()


if __name__ == "__main__":
    main()
