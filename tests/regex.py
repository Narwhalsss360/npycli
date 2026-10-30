import re

from npycli.ansi.parsing import (
    CONTROL_SEQUENCE_REGEX_7_BIT_MODE,
    CONTROL_SEQUENCE_REGEX_FINAL_BYTE_GROUP,
    CONTROL_SEQUENCE_REGEX_INTERMEDIATE_BYTES_GROUP,
    CONTROL_SEQUENCE_REGEX_PARAMETER_BYTES_GROUP,
    CONTROL_SEQUENCE_REGEX_PRIVATE_MARKER_BYTE_GROUP,
    parse_match_to_control_sequence,
)
from npycli.ansi.sequence_types import bit_combination_to_ord, to_bit_combination
from npycli.ansi.sequences import CONTROL_SEQUENCES

whole: str = ""


for i, seq in enumerate(CONTROL_SEQUENCES):
    num_params = min(seq.argument_count if seq.argument_count != -1 else 5, i % 5)
    args = tuple(range(num_params))
    sequence = seq(*args)
    seq_str = str(sequence)
    whole += seq_str
    match = re.match(CONTROL_SEQUENCE_REGEX_7_BIT_MODE, seq_str)
    assert match is not None
    assert match.group(CONTROL_SEQUENCE_REGEX_PARAMETER_BYTES_GROUP) == ";".join(
        str(x) for x in args
    )
    assert match.group(CONTROL_SEQUENCE_REGEX_INTERMEDIATE_BYTES_GROUP) == bytes(
        bit_combination_to_ord(combo)
        for combo in sequence.token.intermediate_bit_combinations_sequence
    ).decode("utf-8")
    assert (
        to_bit_combination(ord(match.group(CONTROL_SEQUENCE_REGEX_FINAL_BYTE_GROUP)))
        == sequence.token.final_bit_combination
    )
    assert sequence.token.private_marker is None or match.group(
        CONTROL_SEQUENCE_REGEX_PRIVATE_MARKER_BYTE_GROUP
    ) == bytes(
        (bit_combination_to_ord(sequence.token.private_marker.bit_combination),)
    ).decode("utf-8")
    parsed = parse_match_to_control_sequence(match)
    assert sequence == parsed


for match in re.finditer(CONTROL_SEQUENCE_REGEX_7_BIT_MODE, whole):
    print(parse_match_to_control_sequence(match).abbreviation)
