from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .cli import CLI
    from .command import Command


class ParsingError(Exception):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)


class MissingKeywordArgumentValueError(ParsingError):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)


class TooManyArgumentsError(ParsingError):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)


class CLIError(Exception):
    def __init__(self, *args: Any, cli: Optional[CLI] = None, command: Optional[Command] = None) -> None:
        super().__init__(*args)
        self.cli: Optional[CLI] = cli
        self.command: Optional[Command] = command


class EmptyEntriesError(CLIError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommandDoesNotExistError(CLIError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommandArgumentError(CLIError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
