from collections.abc import Callable
from sys import argv

from npycli import Command


def product(nums: tuple[float]) -> float:
    p = 1
    for n in nums:
        p *= n
    return p


ops: dict[str, Callable[..., float]] = {
    '+': sum,
    '*': product
}


def math_op(a: float, *nums: float, op: str | None = '+') -> None:
    if op not in ops:
        print(f'Only {ops.keys()} is supported.')
        return
    print(ops[op]((a,) + nums))


if __name__ == '__main__':
    Command.create(math_op, 'op', help='Perform math operation.')(argv[1:])
