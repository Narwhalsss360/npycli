from typing import Optional, Any, Literal
from enum import Enum
from npycli import Command
from json import dumps, loads
from npycli.parsing import create_enum_parser, create_literal_parser


class NumEnum(int, Enum):
    Zero = 0
    One = 1
    Two = 2


type Username = str

type DecodedJSON = Any

type UserType = Literal["admin", "standard"]


def main(
    num: NumEnum,
    username: Username,
    user_type: UserType,
    decoded_json: Optional[DecodedJSON] = None
) -> None:
    print(num)
    print(f"{user_type}:{username}")
    if decoded_json:
        print(decoded_json)


cmd: Command = Command.create(main)
if __name__ == "__main__":
    print(cmd.extended_command_help())
    cmd([
        "Zero",
        "username",
        "admin",
        dumps({pair.name: pair.value for pair in NumEnum})
    ], {
        NumEnum: create_enum_parser(NumEnum),
        DecodedJSON: loads,
        UserType: create_literal_parser(UserType)
    })

