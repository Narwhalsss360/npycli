from npycli.command import Command


def echo(o):
    print(o)


Command.create(echo).exec_with(["a"])