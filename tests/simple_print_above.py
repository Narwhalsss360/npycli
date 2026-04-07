# NOTE: On windows, this will only work if the input line is on the bottom of the terminal because of windows' line
# buffering and even then, only single lines. Seems like manual character buffering is the only solution for windows.

from __future__ import annotations  # Required for proper type annotation of multiprocessing.Queue
from typing import Any, TextIO
from io import StringIO
from sys import stdout
from os import system, name, get_terminal_size
from asyncio import run, to_thread, create_task, Task, sleep, CancelledError
from multiprocessing import Process, Queue
from os import kill
from signal import SIGINT

from npycli.ansi import SCR_RESET, SELECT_CHARACTER_RENDITION, SET_BOLD_MODE, send_ansi, SAVE_CURRENT_CURSOR_POSITION, CURSOR_DOWN, CURSOR_UP, INSERT_NEW_LINE, RESTORE_SAVED_CURSOR_POSITION, SHOW_CURSOR, strip_ansi, FOREGROUND_RED


def input_async_process_target(queue: Queue[str]) -> None:
    with open(0, "r") as stdin:
        try:
            queue.put(stdin.readline().rsplit("\n", 1)[0])
        except KeyboardInterrupt:
            return


async def input_async(prompt: object = None) -> str:
    user_input_queue: Queue[str] = Queue(1)

    proc: Process = Process(target=input_async_process_target, args=(user_input_queue,), name="server:input", daemon=True)
    print(prompt, end="", flush=True)
    proc.start()
    assert proc.pid is not None

    try:
        join_task: Task[None] = create_task(to_thread(proc.join))
        while user_input_queue.empty() and not join_task.done():
            await sleep(0.02)
    except CancelledError:
        kill(proc.pid, SIGINT)
        raise

    if user_input_queue.empty():
        raise EOFError

    return user_input_queue.get()


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


PRINT_ABOVE_INTERVAL: float = 1


async def main() -> None:
    system("cls" if name == "nt" else "clear")
    input_prompt: str = (
        f"{SELECT_CHARACTER_RENDITION.with_args(SET_BOLD_MODE)}"
        "Enter your input:"
        f"{SELECT_CHARACTER_RENDITION.with_args(SCR_RESET)}"
        "\n>"
    )
    input_task: Task[str] = create_task(input_async(input_prompt))
    i: int = 0
    SHOW_CURSOR()
    while True:
        sleep_task: Task[None] = create_task(sleep(0.4))
        input_task.add_done_callback(lambda _: sleep_task.cancel())
        try:
            await sleep_task
        except CancelledError:
            if not input_task.done():
                input_task.cancel()
            break
        print_above(f"Printed Above\n{SELECT_CHARACTER_RENDITION.with_args(SET_BOLD_MODE, FOREGROUND_RED)}Iteration: {i}{SELECT_CHARACTER_RENDITION.with_args(SCR_RESET)}", max_columns=get_terminal_size().columns)
        i += 1

    if input_task.done():
        print(input_task.result())


if __name__ == "__main__":
    run(main())
