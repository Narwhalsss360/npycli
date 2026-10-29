from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any, NamedTuple, Self, TextIO, cast, override

type CellAddress = int


INVALID_CELL_ADDRESS: CellAddress = -1
MAX_CELL_COLUMN: CellAddress = 8
MAX_CELL_ROW: CellAddress = 15


class BitCombination(NamedTuple):
    column: CellAddress
    row: CellAddress


def is_valid_bit_combination(combo: BitCombination):
    return 0 <= combo.column <= MAX_CELL_COLUMN and 0 <= combo.row <= MAX_CELL_ROW


def require_valid_bit_combination(combo: BitCombination, name: str | None = None):
    if not is_valid_bit_combination(combo):
        if name is None:
            raise ValueError("The bit combination was invalid")
        raise ValueError(f"The bit combination {name} was invalid")


def to_bit_combination(combo: tuple[CellAddress, CellAddress] | BitCombination | bytes | int) -> BitCombination:
    if isinstance(combo, BitCombination):
        require_valid_bit_combination(combo)
        return combo

    if isinstance(combo, tuple):
        return BitCombination(*combo)

    if isinstance(combo, bytes):
        if len(combo) != 1:
            raise ValueError("Can only convert 1 byte to a bit combination")
        return BitCombination((combo[0] >> 4) & 0b1111, combo[0] & 0b1111)

    return BitCombination((combo >> 4) & 0b1111, combo & 0b1111)


def bit_combination_to_ord(combo: BitCombination) -> int:
    return (combo.column << 4) | combo.row


def _set_on_frozen(obj: object, name: str, value: Any) -> None:
    object.__setattr__(obj, name, value)


def _get_from_frozen[T](obj: object, attr_type: type[T], name: str) -> T:
    return cast(T, getattr(obj, name))


type BitCombinationSequence = tuple[BitCombination, ...]


EMPTY_SEQUENCE: BitCombinationSequence = ()


def to_bit_combination_sequence(
        bit_combos: Iterable[int | bytes | BitCombination | tuple[CellAddress, CellAddress]]) -> BitCombinationSequence:
    return tuple(to_bit_combination(combo) for combo in bit_combos)


class BitMode(Enum):
    Seven = 7
    Eight = 8


DEFAULT_ENCODING: str = "utf-8"


@dataclass(frozen=True)
class ECMA48Token(ABC):
    def __post_init__(self) -> None:
        self.use_encoding(DEFAULT_ENCODING)

    @property
    @abstractmethod
    def bytes(self) -> bytes:
        pass

    @property
    def encoding(self) -> str:
        return _get_from_frozen(self, str, "_encoding")

    def use_encoding(self, encoding: str) -> Self:
        _set_on_frozen(self, "_encoding", encoding)
        return self

    @property
    def str(self) -> str:
        return self.bytes.decode(self.encoding)

    def __str__(self) -> str:
        return self.str


@dataclass(frozen=True)
class ControlByteToken(ECMA48Token):
    bit_combination: BitCombination

    @property
    @override
    def bytes(self) -> bytes:
        return bytes((bit_combination_to_ord(self.bit_combination),))


ESCAPE_BIT_COMBINATION: BitCombination = BitCombination(1, 11)


@dataclass(frozen=True)
class EscapeSequenceToken(ECMA48Token):
    intermediate_bit_combinations: BitCombinationSequence
    final_bit_combination: BitCombination

    @property
    @override
    def bytes(self) -> bytes:
        return bytes((
            bit_combination_to_ord(ESCAPE_BIT_COMBINATION),
            *(bit_combination_to_ord(combo) for combo in self.intermediate_bit_combinations),
            bit_combination_to_ord(self.final_bit_combination)
        ))


type ControlSequenceParameter = int | None

type ControlSequenceParameters = tuple[ControlSequenceParameter, ...]

EMPTY_PARAMETERS: ControlSequenceParameters = ()


@dataclass(frozen=True)
class ControlSequenceToken(ECMA48Token):
    SEVEN_BIT_MODE_INTRODUCER = EscapeSequenceToken(EMPTY_SEQUENCE, to_bit_combination((5, 11)))
    EIGHT_BIT_MODE_INTRODUCER = ControlByteToken(to_bit_combination((9, 11)))

    introducer: ControlByteToken | EscapeSequenceToken
    private_marker: ControlByteToken | None
    intermediate_bit_combinations_sequence: BitCombinationSequence
    arguments: ControlSequenceParameters
    final_bit_combination: BitCombination

    def __post_init__(self) -> None:
        super().__post_init__()
        if isinstance(self.introducer, EscapeSequenceToken):
            if self.introducer.intermediate_bit_combinations:
                raise ValueError("The control sequence introducer must not have any intermediate bit combinations")
            if self.introducer.final_bit_combination != to_bit_combination((5, 11)):
                raise ValueError(
                    "The control sequence introducer in 7-bit mode must have an introducer final byte of 05/11")
        elif self.introducer.bit_combination != to_bit_combination((9, 11)):
            raise ValueError("The control sequence introducer in 8-bit mode must have an introducer control byte of 09/11")

    @property
    @override
    def bytes(self) -> bytes:
        private_marker: tuple[()] | tuple[int] = (bit_combination_to_ord(
            self.private_marker.bit_combination),) if self.private_marker else ()

        return bytes((
            *self.introducer.bytes,
            *private_marker,
            *';'.join(str(x) if x is not None else "" for x in self.arguments).encode('utf-8'),
            *(bit_combination_to_ord(combo) for combo in self.intermediate_bit_combinations_sequence),
            bit_combination_to_ord(self.final_bit_combination)
        ))

    @property
    def bit_mode(self) -> BitMode:
        return BitMode.Seven if isinstance(self.introducer, EscapeSequenceToken) else BitMode.Eight

    def as_bit_mode(self, mode: BitMode) -> ControlSequenceToken:
        if mode == self.bit_mode:
            return self

        if mode is BitMode.Seven:
            return ControlSequenceToken(
                ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER,
                private_marker=self.private_marker,
                intermediate_bit_combinations_sequence=self.intermediate_bit_combinations_sequence,
                arguments=self.arguments,
                final_bit_combination=self.final_bit_combination
            )
        else:
            return ControlSequenceToken(
                ControlSequenceToken.EIGHT_BIT_MODE_INTRODUCER,
                private_marker=self.private_marker,
                intermediate_bit_combinations_sequence=self.intermediate_bit_combinations_sequence,
                arguments=self.arguments,
                final_bit_combination=self.final_bit_combination
            )

    @property
    def without_args(self) -> ControlSequenceToken:
        return ControlSequenceToken(
            introducer=self.introducer,
            private_marker=self.private_marker,
            intermediate_bit_combinations_sequence=self.intermediate_bit_combinations_sequence,
            arguments=EMPTY_PARAMETERS,
            final_bit_combination=self.final_bit_combination,
        )

    def with_args(self, args: ControlSequenceParameters) -> ControlSequenceToken:
        return ControlSequenceToken(
            introducer=self.introducer,
            private_marker=self.private_marker,
            intermediate_bit_combinations_sequence=self.intermediate_bit_combinations_sequence,
            arguments=args,
            final_bit_combination=self.final_bit_combination,
        )


@dataclass(frozen=True)
class ControlFunction[T: ECMA48Token](ABC):
    abbreviation: str
    name: str
    argument_count: int
    default_arguments: ControlSequenceParameters | None
    description: str
    init_token: ECMA48Token

    def __post_init__(self) -> None:
        pass

    def _require_init_token_subclass_instance(self, subclass: type | tuple[type, ...], required_by: type) -> None:
        if not isinstance(self.init_token, subclass):
            raise TypeError(f"{required_by} requires init_token to be of type {subclass}")

    @property
    def token(self) -> T:
        return cast(T, self.init_token)

    @property
    def encoding(self) -> str:
        return self.token.encoding

    def use_encoding(self, encoding: str) -> Self:
        self.token.use_encoding(encoding)
        return self

    def __str__(self) -> str:
        return str(self.token)

    def __call__(self, *_: None, file: TextIO, end: str = '', flush: bool | None = None) -> Self:
        flush = True if flush is None else flush
        print(str(self), end=end, file=file, flush=flush)
        return self


@dataclass(frozen=True)
class C0ControlFunction(ControlFunction[ControlByteToken]):
    def __post_init__(self) -> None:
        super().__post_init__()
        self._require_init_token_subclass_instance(ControlByteToken, C0ControlFunction)


@dataclass(frozen=True)
class C1ControlFunction(ControlFunction[ControlByteToken | EscapeSequenceToken]):
    def __post_init__(self) -> None:
        super().__post_init__()
        self._require_init_token_subclass_instance((ControlByteToken, EscapeSequenceToken), C1ControlFunction)

    @property
    def bit_mode(self) -> BitMode:
        return BitMode.Seven if isinstance(self.token, EscapeSequenceToken) else BitMode.Eight

    def as_bit_mode(self, mode: BitMode) -> C1ControlFunction:
        if mode == self.bit_mode:
            return self

        if mode is BitMode.Seven:
            assert self.bit_mode is BitMode.Eight
            assert isinstance(self.init_token, ControlByteToken)
            return C1ControlFunction(
                abbreviation=self.abbreviation,
                name=self.name,
                argument_count=self.argument_count,
                default_arguments=self.default_arguments,
                description=self.description,
                init_token=EscapeSequenceToken(EMPTY_SEQUENCE, BitCombination(
                    self.init_token.bit_combination.column - 4,
                    self.init_token.bit_combination.row
                )),
            )
        else:
            assert self.bit_mode is BitMode.Seven
            assert isinstance(self.init_token, EscapeSequenceToken)
            return C1ControlFunction(
                abbreviation=self.abbreviation,
                name=self.name,
                argument_count=self.argument_count,
                default_arguments=self.default_arguments,
                description=self.description,
                init_token=ControlByteToken(BitCombination(
                    self.init_token.final_bit_combination.column + 4,
                    self.init_token.final_bit_combination.row
                )),
            )


@dataclass(frozen=True)
class ControlSequence(ControlFunction[ControlSequenceToken]):
    def __post_init__(self) -> None:
        super().__post_init__()
        self._require_init_token_subclass_instance(ControlSequenceToken, ControlSequence)

    @property
    def bit_mode(self) -> BitMode:
        return self.token.bit_mode

    def as_bit_mode(self, mode: BitMode) -> ControlSequence:
        if mode == self.bit_mode:
            return self

        return ControlSequence(
            abbreviation=self.abbreviation,
            name=self.name,
            argument_count=self.argument_count,
            default_arguments=self.default_arguments,
            description=self.description,
            init_token=self.token.as_bit_mode(mode),
        )

    @property
    def without_args(self) -> ControlSequence | None:
        return ControlSequence(
            abbreviation=self.abbreviation,
            name=self.name,
            argument_count=self.argument_count,
            default_arguments=self.default_arguments,
            description=self.description,
            init_token=self.token.without_args
        )

    def with_args(self, args: ControlSequenceParameters) -> ControlSequence:
        return ControlSequence(
            abbreviation=self.abbreviation,
            name=self.name,
            argument_count=self.argument_count,
            default_arguments=self.default_arguments,
            description=self.description,
            init_token=self.token.with_args(args)
        )

    @override
    def __call__(self, *args: ControlSequenceParameter, file: TextIO | None = None, end: str = '', flush: bool | None = None) -> ControlSequence:
        with_args: ControlSequence = self.with_args(args)
        if file is not None:
            super(ControlSequence, with_args).__call__(file=file, end=end, flush=flush)
        return with_args


@dataclass(frozen=True)
class IndependentControlFunction(ControlFunction[EscapeSequenceToken]):
    def __post_init__(self) -> None:
        super().__post_init__()
        self._require_init_token_subclass_instance(EscapeSequenceToken, IndependentControlFunction)


__all__ = [
    "DEFAULT_ENCODING",
    "EMPTY_PARAMETERS",
    "EMPTY_SEQUENCE",
    "ESCAPE_BIT_COMBINATION",
    "INVALID_CELL_ADDRESS",
    "MAX_CELL_COLUMN",
    "MAX_CELL_ROW",
    "BitCombination",
    "BitCombinationSequence",
    "BitMode",
    "C0ControlFunction",
    "C1ControlFunction",
    "CellAddress",
    "ControlByteToken",
    "ControlFunction",
    "ControlSequence",
    "ControlSequenceParameter",
    "ControlSequenceParameters",
    "ControlSequenceToken",
    "ECMA48Token",
    "EscapeSequenceToken",
    "IndependentControlFunction",
    "bit_combination_to_ord",
    "is_valid_bit_combination",
    "require_valid_bit_combination",
    "to_bit_combination",
    "to_bit_combination_sequence"
]
