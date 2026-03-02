from typing import Optional, Any
from enum import Enum
from npycli import Command
from json import dumps, loads
from npycli.parsing import create_enum_parser


class NumEnum(int, Enum):
    Zero = 0
    One = 1
    Two = 2


type Username = str

type DecodedJSON = Any


def main(
    num: NumEnum,
    username: Username,
    decoded_json: Optional[DecodedJSON] = None
) -> None:
    print(num)
    print(username)
    if decoded_json:
        print(decoded_json)


if __name__ == "__main__":
    cmd: Command = Command.create(main)
    cmd([
        "Zero",
        "username",
        dumps({pair.name: pair.value for pair in NumEnum})
    ], {
        NumEnum: create_enum_parser(NumEnum),
        DecodedJSON: loads
    })
