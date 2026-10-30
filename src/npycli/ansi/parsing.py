from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from re import Match, findall

from .sequence_types import (
    EMPTY_PARAMETERS,
    BitCombination,
    BitCombinationSequence,
    BitMode,
    ControlByteToken,
    ControlSequence,
    ControlSequenceParameters,
    ControlSequenceToken,
    bit_combination_to_ord,
    to_bit_combination,
)
from .sequences import CONTROL_SEQUENCES

CONTROL_SEQUENCE_STRIP_REGEX: str = r"[\x1B\x9B]\[([0-?]*)[\x20-/]*([@-~])"
CONTROL_SEQUENCE_REGEX_7_BIT_MODE = (
    r"\x1B\[(\??)([\x30-\x3F]*)([\x20-\x2F]*)([\x40-\x7E])"
)
CONTROL_SEQUENCE_REGEX_8_BIT_MODE = (
    r"\x9B(\??)([\x30-\x3F]*)([\x20-\x2F]*)([\x40-\x7E])"
)
CONTROL_SEQUENCE_REGEX_PRIVATE_MARKER_BYTE_GROUP = 1
CONTROL_SEQUENCE_REGEX_PARAMETER_BYTES_GROUP = 2
CONTROL_SEQUENCE_REGEX_INTERMEDIATE_BYTES_GROUP = 3
CONTROL_SEQUENCE_REGEX_FINAL_BYTE_GROUP = 4

PARAMETER_BYTE_RANGE_LOWER_BOUND: int = bit_combination_to_ord(
    to_bit_combination((3, 0))
)
PARAMETER_BYTE_RANGE_UPPER_BOUND: int = bit_combination_to_ord(
    to_bit_combination((3, 15))
)
RESERVED_PARAMETER_BYTE_RANGE_LOWER_BOUND: int = bit_combination_to_ord(
    to_bit_combination((3, 12))
)
RESERVED_PARAMETER_BYTE_RANGE_UPPER_BOUND: int = bit_combination_to_ord(
    to_bit_combination((3, 15))
)
INTERMEDIATE_BYTE_RANGE_LOWER_BOUND: int = bit_combination_to_ord(
    to_bit_combination((2, 0))
)
INTERMEDIATE_BYTE_RANGE_UPPER_BOUND: int = bit_combination_to_ord(
    to_bit_combination((2, 15))
)
CONTROL_SEQUENCE_FINAL_BYTES: tuple[int, ...] = tuple(
    bit_combination_to_ord(cs.token.final_bit_combination) for cs in CONTROL_SEQUENCES
)


def strip_control_sequences(text: str) -> str:
    stripped: str = text
    for matched_groups in findall(CONTROL_SEQUENCE_STRIP_REGEX, text):
        stripped = stripped.replace(f"\x1b[{''.join(matched_groups)}", "")
    return stripped


def parse_match_to_control_sequence(match: Match[str]) -> ControlSequence:
    if match.re.pattern == CONTROL_SEQUENCE_REGEX_7_BIT_MODE:
        mode: BitMode = BitMode.Seven
    elif match.re.pattern == CONTROL_SEQUENCE_REGEX_8_BIT_MODE:
        mode: BitMode = BitMode.Eight
    else:
        raise ValueError("Must use one of the provided regular expression patterns.")

    private_marker: ControlByteToken | None = (
        ControlByteToken(
            to_bit_combination(
                ord(match.group(CONTROL_SEQUENCE_REGEX_PRIVATE_MARKER_BYTE_GROUP))
            )
        )
        if match.group(CONTROL_SEQUENCE_REGEX_PRIVATE_MARKER_BYTE_GROUP)
        else None
    )
    intermediate_bytes_sequence: BitCombinationSequence = tuple(
        to_bit_combination(ord(x))
        for x in match.group(CONTROL_SEQUENCE_REGEX_INTERMEDIATE_BYTES_GROUP)
    )
    final_bit_combination: BitCombination = to_bit_combination(
        ord(match.group(CONTROL_SEQUENCE_REGEX_FINAL_BYTE_GROUP))
    )

    found: ControlSequence | None = next(
        filter(
            lambda sequence: (
                sequence.token.final_bit_combination == final_bit_combination
                and sequence.token.private_marker == private_marker
                and sequence.token.intermediate_bit_combinations_sequence
                == intermediate_bytes_sequence
            ),
            CONTROL_SEQUENCES,
        ),
        None,
    )

    if found is None:
        raise ValueError(f"Could not find the control sequence for {match.group()!r}")

    arguments_string: str = match.group(CONTROL_SEQUENCE_REGEX_PARAMETER_BYTES_GROUP)
    try:
        arguments: ControlSequenceParameters = (
            tuple(int(x) for x in arguments_string.split(";"))
            if arguments_string
            else EMPTY_PARAMETERS
        )
    except ValueError:
        raise NotImplementedError("A parameter byte which is not supported exists.")

    return found.as_bit_mode(mode).with_args(arguments)


@dataclass
class ExtractionResult:
    sequence: ControlSequence
    start_index: int
    end_index: int


def extract_control_sequence(
    chr_iter: Iterable[int], max_iterations: int = -1, mode: BitMode = BitMode.Seven
) -> ExtractionResult | None:
    iterations: int = 0
    read: bytes = b""
    iterator: Iterator[int] = iter(chr_iter)
    introducer_bytes: bytes = (
        ControlSequenceToken.EIGHT_BIT_MODE_INTRODUCER
        if mode is BitMode.Eight
        else ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER
    ).bytes

    while not read.endswith(introducer_bytes):
        if iterations == max_iterations:
            raise StopIteration

        try:
            c: int = next(iterator)
        except StopIteration:
            return None

        if len(read) == len(introducer_bytes):
            read = bytes((*read[1:], *bytes((c,))))
        else:
            read += bytes((c,))
        iterations += 1

    start_index: int = iterations - len(introducer_bytes)
    end_index: int = start_index
    read = b""

    while True:
        if iterations == max_iterations:
            raise StopIteration

        try:
            c: int = next(iterator)
        except StopIteration:
            return None

        read += bytes((c,))
        if c in CONTROL_SEQUENCE_FINAL_BYTES:
            break
        end_index += 1

    intermediate_byte: int | None = next(
        filter(
            lambda x: (
                INTERMEDIATE_BYTE_RANGE_LOWER_BOUND
                <= x
                <= INTERMEDIATE_BYTE_RANGE_UPPER_BOUND
            ),
            read,
        ),
        None,
    )

    if intermediate_byte is None:

        def filter_function(cs: ControlSequence) -> bool:
            return (
                not cs.token.intermediate_bit_combinations_sequence
                and bit_combination_to_ord(cs.token.final_bit_combination) == c
            )
    else:

        def filter_function(cs: ControlSequence) -> bool:
            return (
                len(cs.token.intermediate_bit_combinations_sequence) == 1
                and bit_combination_to_ord(
                    cs.token.intermediate_bit_combinations_sequence[0]
                )
                == intermediate_byte
                and bit_combination_to_ord(cs.token.final_bit_combination) == c
            )

    if (sequence := next(filter(filter_function, CONTROL_SEQUENCES), None)) is None:
        raise LookupError(
            f"The control sequence with intermediate byte {hex(intermediate_byte) if intermediate_byte else None} and final byte of {c} was not found."
        )

    parameter_only_bytes: bytes = bytes(
        b
        for b in read
        if PARAMETER_BYTE_RANGE_LOWER_BOUND <= b <= PARAMETER_BYTE_RANGE_UPPER_BOUND
    )
    if any(
        RESERVED_PARAMETER_BYTE_RANGE_LOWER_BOUND
        <= b
        <= RESERVED_PARAMETER_BYTE_RANGE_UPPER_BOUND
        for b in parameter_only_bytes[1:]
    ):
        raise ValueError("A Parameter Byte which is reserved was used.")

    return ExtractionResult(
        sequence.with_args(
            tuple(int(bstr) for bstr in parameter_only_bytes.split(b";") if bstr)
        ),
        start_index,
        end_index,
    )


__all__ = [
    "CONTROL_SEQUENCE_FINAL_BYTES",
    "CONTROL_SEQUENCE_REGEX_7_BIT_MODE",
    "CONTROL_SEQUENCE_REGEX_8_BIT_MODE",
    "CONTROL_SEQUENCE_REGEX_FINAL_BYTE_GROUP",
    "CONTROL_SEQUENCE_REGEX_INTERMEDIATE_BYTES_GROUP",
    "CONTROL_SEQUENCE_REGEX_PARAMETER_BYTES_GROUP",
    "CONTROL_SEQUENCE_REGEX_PRIVATE_MARKER_BYTE_GROUP",
    "CONTROL_SEQUENCE_STRIP_REGEX",
    "ExtractionResult",
    "extract_control_sequence",
    "parse_match_to_control_sequence",
    "strip_control_sequences",
]
