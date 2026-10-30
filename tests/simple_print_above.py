# NOTE: On windows, this will only work if the input line is on the bottom of the terminal because of windows' line
# buffering and even then, only single lines. Seems like manual character buffering is the only solution for windows.

from __future__ import (
    annotations,  # Required for proper type annotation of multiprocessing.Queue
)

from asyncio import CancelledError, Task, create_task, run, sleep, to_thread
from io import StringIO
from multiprocessing import Process, Queue
from os import get_terminal_size, kill, name, system
from signal import SIGINT
from sys import stdout
from typing import Any, TextIO

from npycli.ansi.const.p_sm import SHOW_CURSOR
from npycli.ansi.const.sgr import (
    BOLD_OR_INCREASED_INTENSITY,
    DEFAULT_RENDITION,
    RED_DISPLAY,
)
from npycli.ansi.parsing import strip_control_sequences
from npycli.ansi.sequences import CUD, CUU, IL, P_SM, RCP, SCCP, SGR


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
    for c in strip_control_sequences(output):
        line_length += 1
        if line_length == max_columns or c == "\n":
            line_count += 1
            line_length = 0

    SCCP(file=file)
    if current_is_empty:
        print("\n" * lines_above, file=file, end="", flush=True)
        CUU(lines_above, file=file)

    # These ansi control commands may be supplied with arguments
    print("\n" * line_count, file=file, end="", flush=True)
    CUU(line_count + lines_above - (0 if current_is_empty else 1), file=file)
    IL(line_count, file=file)

    # Flush, just in case current cursor position gets moved after output
    print(output, end='', file=file, flush=True)
    RCP(file=file)
    CUD(line_count, file=file)


PRINT_ABOVE_INTERVAL: float = 1


async def main() -> None:
    await to_thread(system, "cls" if name == "nt" else "clear")
    input_prompt: str = (
        f"{SGR(BOLD_OR_INCREASED_INTENSITY)}"
        "Enter your input:"
        f"{SGR(DEFAULT_RENDITION)}"
        "\n>"
    )
    input_task: Task[str] = create_task(input_async(input_prompt))
    i: int = 0
    P_SM(SHOW_CURSOR, file=stdout)
    while True:
        sleep_task: Task[None] = create_task(sleep(0.4))
        def canceller(input_task: Task[str], sleep_task: Task[None] = sleep_task) -> None:
            sleep_task.cancel()
        input_task.add_done_callback(canceller)
        try:
            await sleep_task
        except CancelledError:
            if not input_task.done():
                input_task.cancel()
            break
        print_above(f"Printed Above\n{SGR(BOLD_OR_INCREASED_INTENSITY, RED_DISPLAY)}Iteration: {i}{SGR(DEFAULT_RENDITION)}", max_columns=get_terminal_size().columns)
        i += 1

    if input_task.done():
        print(input_task.result())


if __name__ == "__main__":
    run(main())
