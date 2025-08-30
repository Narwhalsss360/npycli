from sys import argv
from typing import Annotated, Iterable, Iterator, cast
from npycli import Command, ParsingError, AnnotationPreview


class GenericConfigKVP:
    def __init__(self, arg: str, delimiter: str | None = None) -> None:
        if delimiter is None:
            raise TypeError("This must be a base class, where the 'delimiter' argument is specified")
        if delimiter not in arg:
            raise ParsingError(f"{GenericConfigKVP.__name__}({repr(delimiter)}): Argument does not have delimiter.")
        index = arg.index(delimiter)

        self.delimiter: str = delimiter
        self.key: str = arg[:index]
        self.value: str = arg[index + len(delimiter):]
        self.arg: str = arg

    def __iter__(self) -> Iterator[str]:
        return iter((self.key, self.value))

    def __str__(self) -> str:
        return f"{self.key}{self.delimiter}{self.value}"

    def __repr__(self) -> str:
        return repr(str(self))


class EqualsConfigKVP(GenericConfigKVP):
    DELIMITER = "="
    def __init__(self, arg: str) -> None:
        super().__init__(arg, EqualsConfigKVP.DELIMITER)


class ColonConfigKVP(GenericConfigKVP):
    DELIMITER = ":"
    def __init__(self, arg: str) -> None:
        super().__init__(arg, ColonConfigKVP.DELIMITER)


class WalrusConfigKVP(GenericConfigKVP):
    DELIMITER = ":="
    def __init__(self, arg: str) -> None:
        super().__init__(arg, WalrusConfigKVP.DELIMITER)


ConfigKVP = WalrusConfigKVP


def config_values(*args: Annotated[ConfigKVP, AnnotationPreview(f"ConfigKVP(key{ConfigKVP.DELIMITER}value)")]) -> None:
    cfg = dict(cast(Iterable[tuple[str, str]], args))
    print(cfg)


if __name__ == "__main__":
    cmd: Command = Command.create(config_values, "config-values")
    if len(argv) == 1:
        print(cmd)
        exit(1)
    cmd.exec_with(argv[1:])
