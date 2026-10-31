from npycli.command import Command


def echo(o):  # type: ignore
    print(o)  # type: ignore


Command.create(echo).exec_with(["a"])  # type: ignore
