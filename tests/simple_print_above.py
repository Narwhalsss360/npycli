from typing import Any
from io import StringIO
from os import system, name, get_terminal_size
from asyncio import run, to_thread, create_task, Task, sleep, CancelledError
from npycli.ansi import send_ansi, SAVE_CURRENT_CURSOR_POSITION, CURSOR_DOWN, CURSOR_UP, INSERT_NEW_LINE, RESTORE_SAVED_CURSOR_POSITION


def print_above(*args: Any, max_columns: int, current_is_empty: bool = False, **kwargs: Any) -> None:
    '''
    Print above the current line.
    '''

    # Use print with file=buffer so this function can be used just like regular print
    buffer: StringIO = StringIO()
    print(*args, **kwargs, flush=True, file=buffer, end="")
    output: str = buffer.getvalue()

    line_count: int = 1
    line_length: int = 0
    for c in output:
        line_length += 1
        if line_length == max_columns or c == "\n":
            line_count += 1
            line_length = 0

    send_ansi(SAVE_CURRENT_CURSOR_POSITION)
    if current_is_empty:
        print()
        send_ansi(CURSOR_UP.with_args(2))

    # These ansi control commands may be supplied with arguments
    print("\n" * line_count, end="")
    send_ansi(CURSOR_UP.with_args(line_count))
    # This one doesn't have argument, so we just repeat the command
    send_ansi(INSERT_NEW_LINE, repeat=line_count)

    # Flush, just in case current cursor position gets moved after output
    print(output, end='', flush=True)
    send_ansi(RESTORE_SAVED_CURSOR_POSITION)
    send_ansi(CURSOR_DOWN.with_args(line_count))


PRINT_ABOVE_INTERVAL: float = 1


async def main() -> None:
    system("cls" if name == "nt" else "clear")
    input_task: Task[str] = create_task(to_thread(input, ">"))
    i: int = 0
    while True:
        sleep_task: Task[None] = create_task(sleep(1))
        input_task.add_done_callback(lambda _: sleep_task.cancel())
        try:
            await sleep_task
        except CancelledError:
            if not input_task.done():
                input_task.cancel()
            break
        print_above(f"Printed Above\nIteration: {i}", max_columns=get_terminal_size().columns)
        i += 1

    if input_task.done():
        print(input_task.result())


if __name__ == "__main__":
    run(main())
