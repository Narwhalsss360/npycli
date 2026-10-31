# ANSI

_NOTE:_ What is actually implemented is the ECMA-48 standard since ISO's ANSI is **really** expensive.

# Naming

Control sequences/functions constants are named according to their standard abbreviation. _Private control sequences/functions are abbreviated as initialism of their name with `P_` prefix.

# Selective Control Sequence Parameters

All standard selective parameters are constants. For example, to use green display text, use the SELECT GRAPHIC RENDITION control sequence with parameter GREEN_DISPLAY (32), where the control sequence constant is `npycli.ansi.sequences.SGR` and the selective parameter constant is `npycli.ansi.const.sgr.GREEN_DISPLAY`.

Constants for selective parameters are found in `npycli.ansi.const.<ABBREVIATION>.*` where `<ABBREVIATION>` is the abbreviation a specific control sequence.

# Basic Usage

## BitCombination and Representation

The ECMA-48 specification uses a column/row notation to specify characters known as a bit combination to be byte-size-agnostic, therefore, the `BitCombination(NamedTuple)` is used to follow the same notation. There exist helper functions:

- `is_valid_bit_combination(combo: BitCombination)`
- `to_bit_combination(combo: tuple[CellAddress, CellAddress] | BitCombination | bytes | int) -> BitCombination`
- `bit_combination_to_ord(combo: BitCombination) -> int`

and where the names of the integers in the tuple are `column` and `row`.

## Main Types

Control sequence/functions composes the `ECMA48Token` frozen dataclass which is used to represent the details of the bits/bytes.

All control sequences/functions derive from the `npycli.ansi.sequence_types.ControlFunction` frozen dataclass, where we have the following fields:

- `abbreviation: str`
- `name: str`
- `argument_count: int`
- `default_arguments: ControlSequenceParameters | None`
- `description: str`
- `init_token: ECMA48Token`

and the following properties:

- `token -> T`, where `T` is the type token for this class of control function.
- `encoding -> str` which is used to convert the bytes to a `str`. _You may set the encoding by using method_ `use_encoding(self, encoding: str) -> Self`, _which will **not** return a new instance._

and lastly, the following dunder methods:

- `__str__` for the `str` that will actually perform the control function.
- `__call__(self, *_: None, file: TextIO, end: str = "", flush: bool | None = None)` which will write the control function to the specified file. `flush` if `None` will default to `True`.
- `ControlSequence.__call__(self, *args_: None, file: TextIO, end: str = "", flush: bool | None = None)` will return a new instance of `ControlSequence` with the specified arguments and will write the control function (the new instance) to the specified file if one is specified. `flush` if `None` will default to `True`.

The `ControlSequence` class also has `arguments -> ControlSequenceParameters` property, `without_args -> ControlSequence` property and `with_args(self, args: ControlSequenceParameters)` function which will return a new instance. _Note: `ControlSequenceParameters` is a type alias of a tuple of ints of any length._

---

See [ansiexport repository; branch: py](https://github.com/Narwhalsss360/ansiexport/tree/py)