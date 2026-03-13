from npycli.ansi import controls, ANSI_CONTROL_SEQUENCE_REGEX, SELECT_CHARACTER_RENDITION, SCR_RESET, BACKGROUND_BLACK, FOREGROUND_BLUE, ANSIControl, strip_ansi, SET_BOLD_MODE, BACKGROUND_WHITE
import re


for sequence in controls().values():
    with_args = sequence.with_args(*tuple(i for i in range(sequence.no_of_arguments - sequence.no_of_default_arguments)))
    print(f"{repr(str(with_args))}: {re.findall(ANSI_CONTROL_SEQUENCE_REGEX, str(with_args))}")


s = (
    f"{SELECT_CHARACTER_RENDITION.with_args(BACKGROUND_BLACK, FOREGROUND_BLUE)}"
    "A B C "
    f"{SELECT_CHARACTER_RENDITION.with_args(SCR_RESET)}"
    "regular"
)

found = re.findall(ANSI_CONTROL_SEQUENCE_REGEX, s)
print(f"{repr(s)}: {found}")

s1 = s
for matches in found:
    s1 = s1.replace(f"{ANSIControl.CSI}{"".join(matches)}", "")
print(repr(s1))

s = (
    f"{SELECT_CHARACTER_RENDITION.with_args(SET_BOLD_MODE, BACKGROUND_WHITE, FOREGROUND_BLUE)}"
    "INFO"
    f"{SELECT_CHARACTER_RENDITION(SCR_RESET)} "
    "Server info log message placeholder..."
)
s1 = strip_ansi(s)
print(repr(f"{(s, s1)=}"))
