from .sequence_types import (
    EMPTY_PARAMETERS,
    EMPTY_SEQUENCE,
    BitCombination,
    C0ControlFunction,
    C1ControlFunction,
    ControlByteToken,
    ControlSequence,
    ControlSequenceToken,
    EscapeSequenceToken,
    IndependentControlFunction,
)

ACK = C0ControlFunction(
    abbreviation='ACK',
    name='ACKNOWLEDGE',
    argument_count=0,
    default_arguments=None,
    description='Transmitted by a receiver as an affirmative response to a sender.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 6)) 
)

BEL = C0ControlFunction(
    abbreviation='BEL',
    name='BELL',
    argument_count=0,
    default_arguments=None,
    description='Triggers an acoustic or attention-getting signal.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 7)) 
)

BS = C0ControlFunction(
    abbreviation='BS',
    name='BACKSPACE',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position one character position backwards along the line.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 8)) 
)

CAN = C0ControlFunction(
    abbreviation='CAN',
    name='CANCEL',
    argument_count=0,
    default_arguments=None,
    description='Indicates that the data with which it is sent is in error or is to be disregarded.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 8)) 
)

CR = C0ControlFunction(
    abbreviation='CR',
    name='CARRIAGE RETURN',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position to the first character position of the same line.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 13)) 
)

DC1 = C0ControlFunction(
    abbreviation='DC1',
    name='DEVICE CONTROL ONE',
    argument_count=0,
    default_arguments=None,
    description='A device control character primarily intended for turning on or starting an ancillary device.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 1)) 
)

DC2 = C0ControlFunction(
    abbreviation='DC2',
    name='DEVICE CONTROL TWO',
    argument_count=0,
    default_arguments=None,
    description='A device control character for starting or putting an ancillary device into a special mode.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 2)) 
)

DC3 = C0ControlFunction(
    abbreviation='DC3',
    name='DEVICE CONTROL THREE',
    argument_count=0,
    default_arguments=None,
    description='A device control character primarily intended for turning off or stopping an ancillary device.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 3)) 
)

DC4 = C0ControlFunction(
    abbreviation='DC4',
    name='DEVICE CONTROL FOUR',
    argument_count=0,
    default_arguments=None,
    description='A device control character for stopping or interrupting an ancillary device function.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 4)) 
)

DLE = C0ControlFunction(
    abbreviation='DLE',
    name='DATA LINK ESCAPE',
    argument_count=0,
    default_arguments=None,
    description='Changes the meaning of a limited number of continuously following bit combinations.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 0)) 
)

EM = C0ControlFunction(
    abbreviation='EM',
    name='END OF MEDIUM',
    argument_count=0,
    default_arguments=None,
    description='Indicates the physical end of a medium or the end of the used portion of a medium.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 9)) 
)

ENQ = C0ControlFunction(
    abbreviation='ENQ',
    name='ENQUIRY',
    argument_count=0,
    default_arguments=None,
    description='A request for a response from a remote station, often to identify itself.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 5)) 
)

EOT = C0ControlFunction(
    abbreviation='EOT',
    name='END OF TRANSMISSION',
    argument_count=0,
    default_arguments=None,
    description='Indicates the conclusion of a transmission, which may have included one or more texts.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 4)) 
)

ESC = C0ControlFunction(
    abbreviation='ESC',
    name='ESCAPE',
    argument_count=0,
    default_arguments=None,
    description='A code extension character used to provide an escape sequence for additional control functions.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 11)) 
)

ETB = C0ControlFunction(
    abbreviation='ETB',
    name='END OF TRANSMISSION BLOCK',
    argument_count=0,
    default_arguments=None,
    description='Indicates the end of a block of data where data is divided into blocks for transmission purposes.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 7)) 
)

ETX = C0ControlFunction(
    abbreviation='ETX',
    name='END OF TEXT',
    argument_count=0,
    default_arguments=None,
    description='Indicates the end of a text started by STX.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 3)) 
)

FF = C0ControlFunction(
    abbreviation='FF',
    name='FORM FEED',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position to the corresponding character position of the line at the top of the next page or form.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 12)) 
)

HT = C0ControlFunction(
    abbreviation='HT',
    name='CHARACTER TABULATION',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position to the next preset character tabulation stop.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 9)) 
)

IS1 = C0ControlFunction(
    abbreviation='IS1',
    name='INFORMATION SEPARATOR ONE',
    argument_count=0,
    default_arguments=None,
    description='Used to separate and qualify data logically; delimits a unit boundary.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 15)) 
)

IS2 = C0ControlFunction(
    abbreviation='IS2',
    name='INFORMATION SEPARATOR TWO',
    argument_count=0,
    default_arguments=None,
    description='Used to separate and qualify data logically; delimits a record boundary.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 14)) 
)

IS3 = C0ControlFunction(
    abbreviation='IS3',
    name='INFORMATION SEPARATOR THREE',
    argument_count=0,
    default_arguments=None,
    description='Used to separate and qualify data logically; delimits a group boundary.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 13)) 
)

IS4 = C0ControlFunction(
    abbreviation='IS4',
    name='INFORMATION SEPARATOR FOUR',
    argument_count=0,
    default_arguments=None,
    description='Used to separate and qualify data logically; delimits a file boundary.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 12)) 
)

LF = C0ControlFunction(
    abbreviation='LF',
    name='LINE FEED',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position to the corresponding character position of the next line.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 10)) 
)

LS0 = C0ControlFunction(
    abbreviation='LS0',
    name='LOCKING-SHIFT ZERO',
    argument_count=0,
    default_arguments=None,
    description='LS0 is used for code extension purposes. It causes the meanings of the bit combinations following it in the data stream to be changed.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 14)) 
)

LS1 = C0ControlFunction(
    abbreviation='LS1',
    name='LOCKING-SHIFT ONE',
    argument_count=0,
    default_arguments=None,
    description='LS1 is used for code extension purposes. It causes the meanings of the bit combinations following it in the data stream to be changed.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 15)) 
)

NAK = C0ControlFunction(
    abbreviation='NAK',
    name='NEGATIVE ACKNOWLEDGE',
    argument_count=0,
    default_arguments=None,
    description='Transmitted by a receiver as a negative response to a sender.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 5)) 
)

NUL = C0ControlFunction(
    abbreviation='NUL',
    name='NULL',
    argument_count=0,
    default_arguments=None,
    description='Used as a fill character for time delay or to represent an empty position.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 0)) 
)

SI = C0ControlFunction(
    abbreviation='SI',
    name='SHIFT-IN',
    argument_count=0,
    default_arguments=None,
    description='SI is used for code extension purposes. It causes the meanings of the bit combinations following it in the data stream to be changed.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 15)) 
)

SO = C0ControlFunction(
    abbreviation='SO',
    name='SHIFT-OUT',
    argument_count=0,
    default_arguments=None,
    description='SO is used for code extension purposes. It causes the meanings of the bit combinations following it in the data stream to be changed.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 14)) 
)

SOH = C0ControlFunction(
    abbreviation='SOH',
    name='START OF HEADING',
    argument_count=0,
    default_arguments=None,
    description='Indicates the beginning of a sequence of characters containing an address or routing information.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 1)) 
)

STX = C0ControlFunction(
    abbreviation='STX',
    name='START OF TEXT',
    argument_count=0,
    default_arguments=None,
    description='Indicates the beginning of a text and terminates a heading.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 2)) 
)

SUB = C0ControlFunction(
    abbreviation='SUB',
    name='SUBSTITUTE',
    argument_count=0,
    default_arguments=None,
    description='Used in place of a character that has been determined to be invalid or erroneous.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 10)) 
)

SYN = C0ControlFunction(
    abbreviation='SYN',
    name='SYNCHRONOUS IDLE',
    argument_count=0,
    default_arguments=None,
    description='Used by a synchronous transmission system in the absence of any other character to provide a signal.',
    init_token=ControlByteToken(bit_combination=BitCombination(1, 6)) 
)

VT = C0ControlFunction(
    abbreviation='VT',
    name='LINE TABULATION',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position to the corresponding character position of the next preset line tabulation stop.',
    init_token=ControlByteToken(bit_combination=BitCombination(0, 11)) 
)

APC = C1ControlFunction(
    abbreviation='APC',
    name='APPLICATION PROGRAM COMMAND',
    argument_count=0,
    default_arguments=None,
    description='Opening delimiter for a control string containing application execution directives.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 15))
)

BPH = C1ControlFunction(
    abbreviation='BPH',
    name='BREAK PERMITTED HERE',
    argument_count=0,
    default_arguments=None,
    description='Indicates a point where a line break may occur during text layout processing.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 2))
)

CCH = C1ControlFunction(
    abbreviation='CCH',
    name='CANCEL CHARACTER',
    argument_count=0,
    default_arguments=None,
    description='Indicates that the immediately preceding graphic character in the data stream is to be ignored.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 4))
)

CSI = C1ControlFunction(
    abbreviation='CSI',
    name='CONTROL SEQUENCE INTRODUCER',
    argument_count=0,
    default_arguments=None,
    description='Opening delimiter for a control sequence containing numeric or selective parameters.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 11))
)

DCS = C1ControlFunction(
    abbreviation='DCS',
    name='DEVICE CONTROL STRING',
    argument_count=0,
    default_arguments=None,
    description='Opening delimiter for a device control string terminated by ST.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 0))
)

EPA = C1ControlFunction(
    abbreviation='EPA',
    name='END OF PROTECTED AREA',
    argument_count=0,
    default_arguments=None,
    description='Indicates the end of a block of characters started by SPA.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 7))
)

ESA = C1ControlFunction(
    abbreviation='ESA',
    name='END OF SELECTED AREA',
    argument_count=0,
    default_arguments=None,
    description='Indicates the end of a block of characters started by SSA.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 7))
)

HTJ = C1ControlFunction(
    abbreviation='HTJ',
    name='CHARACTER TABULATION WITH JUSTIFICATION',
    argument_count=0,
    default_arguments=None,
    description='Advances the active position to the next tab stop and flushes the intervening text to the right.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 9))
)

HTS = C1ControlFunction(
    abbreviation='HTS',
    name='CHARACTER TABULATION SET',
    argument_count=0,
    default_arguments=None,
    description='Sets a character tabulation stop at the current active position.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 8))
)

MW = C1ControlFunction(
    abbreviation='MW',
    name='MESSAGE WAITING',
    argument_count=0,
    default_arguments=None,
    description='Triggers a visual or acoustic message indicator on a receiving terminal.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 5))
)

NBH = C1ControlFunction(
    abbreviation='NBH',
    name='NO BREAK HERE',
    argument_count=0,
    default_arguments=None,
    description='Indicates a point where a line break must not occur during text layout processing.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 3))
)

NEL = C1ControlFunction(
    abbreviation='NEL',
    name='NEXT LINE',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position to the first character position of the next line.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 5))
)

OSC = C1ControlFunction(
    abbreviation='OSC',
    name='OPERATING SYSTEM COMMAND',
    argument_count=0,
    default_arguments=None,
    description='Opening delimiter for a control string containing operating system instructions.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 13))
)

PLD = C1ControlFunction(
    abbreviation='PLD',
    name='PARTIAL LINE DOWN',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position down by an offset (typically half a line) for subscript printing.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 11))
)

PLU = C1ControlFunction(
    abbreviation='PLU',
    name='PARTIAL LINE UP',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position up by an offset (typically half a line) for superscript printing.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 12))
)

PM = C1ControlFunction(
    abbreviation='PM',
    name='PRIVACY MESSAGE',
    argument_count=0,
    default_arguments=None,
    description='Opening delimiter for a control string containing data meant for private processing.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 14))
)

PU1 = C1ControlFunction(
    abbreviation='PU1',
    name='PRIVATE USE ONE',
    argument_count=0,
    default_arguments=None,
    description='Reserved for a function determined by user application agreements.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 1))
)

PU2 = C1ControlFunction(
    abbreviation='PU2',
    name='PRIVATE USE TWO',
    argument_count=0,
    default_arguments=None,
    description='Reserved for a function determined by user application agreements.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 2))
)

RI = C1ControlFunction(
    abbreviation='RI',
    name='REVERSE LINE FEED',
    argument_count=0,
    default_arguments=None,
    description='Moves the active position to the corresponding character position of the preceding line.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 13))
)

SCI = C1ControlFunction(
    abbreviation='SCI',
    name='SINGLE GRAPHIC CHARACTER INTRODUCER',
    argument_count=0,
    default_arguments=None,
    description='Indicates that the following character is an exceptional escape graphic representation.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 10))
)

SOS = C1ControlFunction(
    abbreviation='SOS',
    name='START OF STRING',
    argument_count=0,
    default_arguments=None,
    description='Opening delimiter for a character string containing data that should not be parsed as standard controls.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 8))
)

SPA = C1ControlFunction(
    abbreviation='SPA',
    name='START OF PROTECTED AREA',
    argument_count=0,
    default_arguments=None,
    description='Indicates the beginning of a block of characters protected against erasure or modification.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 6))
)

SS2 = C1ControlFunction(
    abbreviation='SS2',
    name='SINGLE-SHIFT TWO',
    argument_count=0,
    default_arguments=None,
    description='Designates the next single character from the G2 graphic set.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 14))
)

SS3 = C1ControlFunction(
    abbreviation='SS3',
    name='SINGLE-SHIFT THREE',
    argument_count=0,
    default_arguments=None,
    description='Designates the next single character from the G3 graphic set.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 15))
)

SSA = C1ControlFunction(
    abbreviation='SSA',
    name='START OF SELECTED AREA',
    argument_count=0,
    default_arguments=None,
    description='Indicates the beginning of a block of characters intended to be selected or transmitted.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 6))
)

ST = C1ControlFunction(
    abbreviation='ST',
    name='STRING TERMINATOR',
    argument_count=0,
    default_arguments=None,
    description='Closing delimiter terminating a control string sequence started by DCS, SOS, OSC, PM, or APC.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 12))
)

STS = C1ControlFunction(
    abbreviation='STS',
    name='SET TRANSMIT STATE',
    argument_count=0,
    default_arguments=None,
    description='Establishes a condition where data communication can occur or parameters are frozen.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(5, 3))
)

VTS = C1ControlFunction(
    abbreviation='VTS',
    name='LINE TABULATION SET',
    argument_count=0,
    default_arguments=None,
    description='Sets a line tabulation stop at the line containing the current active position.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(4, 10))
)

CMD = IndependentControlFunction(
    abbreviation='CMD',
    name='CODING METHOD DELIMITER',
    argument_count=0,
    default_arguments=None,
    description='CMD is used as the delimiter of a string of data coded according to Standard ECMA-35 and to switch to a general level of control. The use of CMD is not mandatory if the higher level protocol defines means of delimiting the string, for instance, by specifying the length of the string.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(6, 4))
)

DMI = IndependentControlFunction(
    abbreviation='DMI',
    name='DISABLE MANUAL INPUT',
    argument_count=0,
    default_arguments=None,
    description="Disables the terminal's keyboard or alternative input configurations to prevent manual entries.",
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(6, 0))
)

EMI = IndependentControlFunction(
    abbreviation='EMI',
    name='ENABLE MANUAL INPUT',
    argument_count=0,
    default_arguments=None,
    description="Enables the terminal's keyboard or alternative input configurations following a DMI restriction.",
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(6, 2))
)

INT = IndependentControlFunction(
    abbreviation='INT',
    name='INTERRUPT',
    argument_count=0,
    default_arguments=None,
    description='INT is used to indicate to the receiving device that the current process is to be interrupted and an agreed procedure is to be initiated. This control function is applicable to either direction of transmission.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(6, 1))
)

LS1R = IndependentControlFunction(
    abbreviation='LS1R',
    name='LOCKING-SHIFT ONE RIGHT',
    argument_count=0,
    default_arguments=None,
    description='LS1R is used for code extension purposes. It causes the meanings of the bit combinations following it in the data stream to be changed.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(7, 14))
)

LS2 = IndependentControlFunction(
    abbreviation='LS2',
    name='LOCKING-SHIFT TWO',
    argument_count=0,
    default_arguments=None,
    description='LS2 is used for code extension purposes. It causes the meanings of the bit combinations following it in the data stream to be changed.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(6, 14))
)

LS2R = IndependentControlFunction(
    abbreviation='LS2R',
    name='LOCKING-SHIFT TWO RIGHT',
    argument_count=0,
    default_arguments=None,
    description='LS2R is used for code extension purposes. It causes the meanings of the bit combinations following it in the data stream to be changed.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(7, 13))
)

LS3 = IndependentControlFunction(
    abbreviation='LS3',
    name='LOCKING-SHIFT THREE',
    argument_count=0,
    default_arguments=None,
    description='LS3 is used for code extension purposes. It causes the meanings of the bit combinations following it in the data stream to be changed.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(6, 15))
)

LS3R = IndependentControlFunction(
    abbreviation='LS3R',
    name='LOCKING-SHIFT THREE RIGHT',
    argument_count=0,
    default_arguments=None,
    description='LS3R is used for code extension purposes. It causes the meanings of the bit combinations following it in the data stream to be changed.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(7, 12))
)

RIS = IndependentControlFunction(
    abbreviation='RIS',
    name='RESET TO INITIAL STATE',
    argument_count=0,
    default_arguments=None,
    description='Resets the terminal or processing device back to its baseline default configuration and state parameters.',
    init_token=EscapeSequenceToken(intermediate_bit_combinations=EMPTY_SEQUENCE, final_bit_combination=BitCombination(6, 3))
)

CBT = ControlSequence(
    abbreviation='CBT',
    name='CURSOR BACKWARD TABULATION',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position backward by a specified number of character tabulation stops.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 10))
)

CHA = ControlSequence(
    abbreviation='CHA',
    name='CURSOR CHARACTER ABSOLUTE',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position to a specified character position within the current line.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 7))
)

CHT = ControlSequence(
    abbreviation='CHT',
    name='CURSOR FORWARD TABULATION',
    argument_count=1,
    default_arguments=(1,),
    description='Advances the active position by a specified number of character tabulation stops.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 9))
)

CNL = ControlSequence(
    abbreviation='CNL',
    name='CURSOR NEXT LINE',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position to the first position of a specified number of lines downward.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 5))
)

CPL = ControlSequence(
    abbreviation='CPL',
    name='CURSOR PRECEDING LINE',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position to the first position of a specified number of lines upward.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 6))
)

CPR = ControlSequence(
    abbreviation='CPR',
    name='ACTIVE POSITION REPORT',
    argument_count=2,
    default_arguments=(1 ,1),
    description='Transmits the active position coordinates back to the host system as a response sequence.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 2))
)

CTC = ControlSequence(
    abbreviation='CTC',
    name='CURSOR TABULATION CONTROL',
    argument_count=-1,
    default_arguments=(0,),
    description='Sets or clears tab stops at the active position or active line. Accepts a variable list of selective parameters.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 7))
)

CUB = ControlSequence(
    abbreviation='CUB',
    name='CURSOR BACKWARD',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position backward (left) along the line by a specified number of character positions.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 4))
)

CUD = ControlSequence(
    abbreviation='CUD',
    name='CURSOR DOWN',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position downwards by a specified number of lines.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 2))
)

CUF = ControlSequence(
    abbreviation='CUF',
    name='CURSOR FORWARD',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position forward (right) along the line by a specified number of character positions.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 3))
)

CUP = ControlSequence(
    abbreviation='CUP',
    name='CURSOR POSITION',
    argument_count=2,
    default_arguments=(1 ,1),
    description='Moves the active position to a specific line and column coordinate.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 8))
)

CUU = ControlSequence(
    abbreviation='CUU',
    name='CURSOR UP',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position upwards by a specified number of lines.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 1))
)

CVT = ControlSequence(
    abbreviation='CVT',
    name='CURSOR LINE TABULATION',
    argument_count=1,
    default_arguments=(1,),
    description='Advances the active position by a specified number of line tabulation stops.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 9))
)

DA = ControlSequence(
    abbreviation='DA',
    name='DEVICE ATTRIBUTES',
    argument_count=-1,
    default_arguments=(),
    description='DAQ is used to indicate that the active presentation position in the presentation component is the first\ncharacter position of a qualified area. The last character position of the qualified area is the character\nposition in the presentation component immediately preceding the first character position of the\nfollowing qualified area.\nThe parameter value designates the type of qualified area:\n0\n unprotected and unguarded\n1\n protected and guarded\n2\n graphic character input\n3\n numeric input\n4\n alphabetic input\n5\n input aligned on the last character position of the qualified area\n6\n fill with ZEROs\n7 set a character tabulation stop at the active presentation position (the first character position of the\nqualified area) to indicate the beginning of a field\n8\n protected and unguarded\n9\n fill with SPACEs\n10 input aligned on the first character position of the qualified area\n11 the order of the character positions in the input field is reversed, i.e. the last position in each line\nbecomes the first and vice versa; input begins at the new first position.\n\nThis control function operates independently of the setting of the TABULATION STOP MODE (TSM).\nThe character tabulation stop set by parameter value 7 applies to the active line only.\nNOTE\nThe control functions for area definition (DAQ, EPA, ESA, SPA, SSA) should not be used within an SRS\nstring or an SDS string.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 3))
)

DAQ = ControlSequence(
    abbreviation='DAQ',
    name='DEFINE AREA QUALIFICATION',
    argument_count=-1,
    default_arguments=(),
    description='Defines properties of the area starting at the active position.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 15))
)

DCH = ControlSequence(
    abbreviation='DCH',
    name='DELETE CHARACTER',
    argument_count=1,
    default_arguments=(1,),
    description='Deletes one or more characters at the active position, shifting left remaining characters.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 0))
)

DECLL = ControlSequence(
    abbreviation='DECLL',
    name='SET CURSOR',
    argument_count=1,
    default_arguments=(0,),
    description='Change shape of cursor.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(7, 1))
)

DECSTBM = ControlSequence(
    abbreviation='DECSTBM',
    name='SET LINE BOUNDARIES',
    argument_count=2,
    default_arguments=(None ,None),
    description='Set the top/bottom boundaries of the scrolling margin, arguments are provided in order of top; bottom.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(7, 2))
)

DL = ControlSequence(
    abbreviation='DL',
    name='DELETE LINE',
    argument_count=1,
    default_arguments=(1,),
    description='Deletes one or more lines starting at the current line position, shifting up remaining lines.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 13))
)

DSR = ControlSequence(
    abbreviation='DSR',
    name='DEVICE STATUS REPORT',
    argument_count=1,
    default_arguments=(0,),
    description='Requests a status or state report from the device or presentation component.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 14))
)

DTA = ControlSequence(
    abbreviation='DTA',
    name='DIMENSION TEXT AREA',
    argument_count=2,
    default_arguments=(None ,None),
    description='DTA is used to establish the dimensions of the text area for subsequent pages.\nThe established dimensions remain in effect until the next occurrence of DTA in the data stream.\nPn1\n specifies the dimension in the direction perpendicular to the line orientation\nPn2\n specifies the dimension in the direction parallel to the line orientation\nThe unit in which the parameter value is expressed is that established by the parameter value of SELECT\nSIZE UNIT (SSU).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 4))
)

EA = ControlSequence(
    abbreviation='EA',
    name='ERASE IN AREA',
    argument_count=1,
    default_arguments=(0,),
    description='Erases some or all characters in the active qualified area.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 15))
)

ECH = ControlSequence(
    abbreviation='ECH',
    name='ERASE CHARACTER',
    argument_count=1,
    default_arguments=(1,),
    description='Erases a specified number of characters starting at the active position without moving the cursor.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 8))
)

ED = ControlSequence(
    abbreviation='ED',
    name='ERASE IN PAGE',
    argument_count=1,
    default_arguments=(0,),
    description='Erases some or all characters in the active display page based on parameters (0: cursor to end, 1: start to cursor, 2: complete page).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 10))
)

EF = ControlSequence(
    abbreviation='EF',
    name='ERASE IN FIELD',
    argument_count=1,
    default_arguments=(0,),
    description='Erases some or all characters in the active protected/unprotected field.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 14))
)

EL = ControlSequence(
    abbreviation='EL',
    name='ERASE IN LINE',
    argument_count=1,
    default_arguments=(0,),
    description='Erases some or all characters in the current line based on parameters (0: cursor to end, 1: start to cursor, 2: complete line).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 11))
)

FNK = ControlSequence(
    abbreviation='FNK',
    name='FUNCTION KEY',
    argument_count=1,
    default_arguments=(None,),
    description='FNK is a control function in which the parameter value identifies the function key which has been operated.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 7))
)

FNT = ControlSequence(
    abbreviation='FNT',
    name='FONT SELECTION',
    argument_count=2,
    default_arguments=(0 ,0),
    description='FNT is used to identify the character font to be selected as primary or alternative font by subsequent\noccurrences of SELECT GRAPHIC RENDITION (SGR) in the data stream. Ps1 specifies the primary or\nalternative font concerned:\n0\n primary font\n1\n first alternative font\n2\n second alternative font\n3\n third alternative font\n4\n fourth alternative font\n5\n fifth alternative font\n6\n sixth alternative font\n7\n seventh alternative font\n8\n eighth alternative font\n9\n ninth alternative font\nPs2 identifies the character font according to a register which is to be established.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 4))
)

GCC = ControlSequence(
    abbreviation='GCC',
    name='GRAPHIC CHARACTER COMBINATION',
    argument_count=1,
    default_arguments=(0,),
    description='GCC is used to indicate that two or more graphic characters are to be imaged as one single graphic\nsymbol. GCC with a parameter value of 0 indicates that the following two graphic characters are to be\nimaged as one single graphic symbol; GCC with a parameter value of 1 and GCC with a parameter value\nof 2 indicate respectively the beginning and the end of a string of graphic characters which are to be\nimaged as one single graphic symbol.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 15))
)

GSM = ControlSequence(
    abbreviation='GSM',
    name='GRAPHIC SIZE MODIFICATION',
    argument_count=2,
    default_arguments=(100 ,100),
    description='GSM is used to modify for subsequent text the height and/or the width of all primary and alternative\nfonts identified by FONT SELECTION (FNT) and established by GRAPHIC SIZE SELECTION (GSS).\nThe established values remain in effect until the next occurrence of GSM or GSS in the data steam.\nPn1\nPn2\nspecifies the height as a percentage of the height established by GSS\nspecifies the width as a percentage of the width established by GSS',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 2))
)

GSS = ControlSequence(
    abbreviation='GSS',
    name='GRAPHIC SIZE SELECTION',
    argument_count=1,
    default_arguments=(None,),
    description='GSS is used to establish for subsequent text the height and the width of all primary and alternative fonts\nidentified by FONT SELECTION (FNT). The established values remain in effect until the next\noccurrence of GSS in the data stream.\nPn specifies the height, the width is implicitly defined by the height.\nThe unit in which the parameter value is expressed is that established by the parameter value of SELECT\nSIZE UNIT (SSU).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 3))
)

HPA = ControlSequence(
    abbreviation='HPA',
    name='CHARACTER POSITION ABSOLUTE',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position to a specified horizontal coordinate without affecting the vertical position.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 0))
)

HPB = ControlSequence(
    abbreviation='HPB',
    name='CHARACTER POSITION BACKWARD',
    argument_count=1,
    default_arguments=(1,),
    description='HPB causes the active data position to be moved by n character positions in the data component in the\ndirection opposite to that of the character progression, where n equals the value of Pn.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 10))
)

HPR = ControlSequence(
    abbreviation='HPR',
    name='CHARACTER POSITION RELATIVE',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position forward by a specified number of character positions relative to its current spot.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 1))
)

HVP = ControlSequence(
    abbreviation='HVP',
    name='CHARACTER AND LINE POSITION',
    argument_count=2,
    default_arguments=(1 ,1),
    description='Moves the active position to a specific line and column coordinate (equivalent to CUP).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 6))
)

ICH = ControlSequence(
    abbreviation='ICH',
    name='INSERT CHARACTER',
    argument_count=1,
    default_arguments=(1,),
    description='Inserts one or more erased characters at the active position, shifting remaining characters right.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 0))
)

IDCS = ControlSequence(
    abbreviation='IDCS',
    name='IDENTIFY DEVICE CONTROL STRING',
    argument_count=1,
    default_arguments=(None,),
    description='IDCS is used to specify the purpose and format of the command string of subsequent DEVICE\nCONTROL STRINGs (DCS). The specified purpose and format remain in effect until the next\noccurrence of IDCS in the data stream.\nThe parameter values are\n1 reserved for use with the DIAGNOSTIC state of the STATUS REPORT TRANSFER MODE (SRTM)\n2\n reserved for Dynamically Redefinable Character Sets (DRCS) according to Standard ECMA-35.\nThe format and interpretation of the command string corresponding to these parameter values are to be\ndefined in appropriate standards. If this control function is used to identify a private command string, a\nprivate parameter value shall be used.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 15))
)

IGS = ControlSequence(
    abbreviation='IGS',
    name='IDENTIFY GRAPHIC SUBREPERTOIRE',
    argument_count=1,
    default_arguments=(None,),
    description='IGS is used to indicate that a repertoire of the graphic characters of ISO/IEC 10367 is used in the\nsubsequent text.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 13))
)

IL = ControlSequence(
    abbreviation='IL',
    name='INSERT LINE',
    argument_count=1,
    default_arguments=(1,),
    description='Inserts one or more erased lines at the current line position, shifting down remaining lines.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 12))
)

JFY = ControlSequence(
    abbreviation='JFY',
    name='JUSTIFY',
    argument_count=-1,
    default_arguments=(),
    description='JFY is used to indicate the beginning of a string of graphic characters in the presentation component that\nare to be justified according to the layout specified by the parameter values, see annex C:\n0\n no justification, end of justification of preceding text\n1\n word fill\n2\n word space\n3\n letter space\n4\n hyphenation\n5\n flush to line home position margin\n6\n centre between line home position and line limit position margins\n7\n flush to line limit position margin\n8\n Italian hyphenation\nThe end of the string to be justified is indicated by the next occurrence of JFY in the data stream.\nThe line home position is established by the parameter value of SET LINE HOME (SLH). The line limit\nposition is established by the parameter value of SET LINE LIMIT (SLL).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 6))
)

MC = ControlSequence(
    abbreviation='MC',
    name='MEDIA COPY',
    argument_count=1,
    default_arguments=(0,),
    description='MC is used either to initiate a transfer of data from or to an auxiliary input/output device or to enable or\ndisable the relay of the received data stream to an auxiliary input/output device, depending on the\nparameter value:\n0\n initiate transfer to a primary auxiliary device\n1\n initiate transfer from a primary auxiliary device\n2\n initiate transfer to a secondary auxiliary device\n3\n initiate transfer from a secondary auxiliary device\n4\n stop relay to a primary auxiliary device\n5\n start relay to a primary auxiliary device\n6\n stop relay to a secondary auxiliary device\n7\n start relay to a secondary auxiliary device\nThis control function may not be used to switch on or off an auxiliary device.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 9))
)

NP = ControlSequence(
    abbreviation='NP',
    name='NEXT PAGE',
    argument_count=1,
    default_arguments=(1,),
    description='Advances the display view forward by a specified number of pages.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 5))
)

PEC = ControlSequence(
    abbreviation='PEC',
    name='PRESENTATION EXPAND OR CONTRACT',
    argument_count=1,
    default_arguments=(0,),
    description='PEC is used to establish the spacing and the extent of the graphic characters for subsequent text. The\nspacing is specified in the line as multiples of the spacing established by the most recent occurrence of\nSET CHARACTER SPACING (SCS) or of SELECT CHARACTER SPACING (SHS) or of SPACING\nINCREMENT (SPI) in the data stream. The extent of the characters is implicitly established by these control functions. The established spacing and the extent remain in effect until the next occurrence of\nPEC, of SCS, of SHS or of SPI in the data stream. The parameter values are\n0\n normal (as specified by SCS, SHS or SPI)\n1\n expanded (multiplied by a factor not greater than 2)\n2\n condensed (multiplied by a factor not less than 0,5)',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 10))
)

PFS = ControlSequence(
    abbreviation='PFS',
    name='PAGE FORMAT SELECTION',
    argument_count=1,
    default_arguments=(0,),
    description='PFS is used to establish the available area for the imaging of pages of text based on paper size. The\npages are introduced by the subsequent occurrence of FORM FEED (FF) in the data stream.\nThe established image area remains in effect until the next occurrence of PFS in the data stream. The\nparameter values are (see also annex E):\n0\n tall basic text communication format\n1\n wide basic text communication format\n2\n tall basic A4 format\n3\n wide basic A4 format\n4\n tall North American letter format\n5\n wide North American letter format\n6\n tall extended A4 format\n7\n wide extended A4 format\n8\n tall North American legal format\n9\n wide North American legal format\n10 A4 short lines format\n11 A4 long lines format\n12 B5 short lines format\n13 B5 long lines format\n14 B4 short lines format\n15 B4 long lines format\nThe page home position is established by the parameter value of SET PAGE HOME (SPH), the page\nlimit position is established by the parameter value of SET PAGE LIMIT (SPL).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 10))
)

PP = ControlSequence(
    abbreviation='PP',
    name='PRECEDING PAGE',
    argument_count=1,
    default_arguments=(1,),
    description='Regresses the display view backward by a specified number of pages.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 6))
)

PPA = ControlSequence(
    abbreviation='PPA',
    name='PAGE POSITION ABSOLUTE',
    argument_count=1,
    default_arguments=(1,),
    description='PPA causes the active data position to be moved in the data component to the corresponding character\nposition on the n-th page, where n equals the value of Pn.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 0))
)

PPB = ControlSequence(
    abbreviation='PPB',
    name='PAGE POSITION BACKWARD',
    argument_count=1,
    default_arguments=(1,),
    description='PPB causes the active data position to be moved in the data component to the corresponding character\nposition on the n-th preceding page, where n equals the value of Pn.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 2))
)

PPR = ControlSequence(
    abbreviation='PPR',
    name='PAGE POSITION FORWARD',
    argument_count=1,
    default_arguments=(1,),
    description='PPR causes the active data position to be moved in the data component to the corresponding character\nposition on the n-th following page, where n equals the value of Pn.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 1))
)

PTX = ControlSequence(
    abbreviation='PTX',
    name='PARALLEL TEXTS',
    argument_count=1,
    default_arguments=(1,),
    description='PTX is used to delimit strings of graphic characters that are communicated one after another in the data stream but that are intended to be presented in parallel with one another, usually in adjacent lines. The parameter values are 0 end of parallel texts 1 2 3 beginning of a string of principal parallel text beginning of a string of supplementary parallel text beginning of a string of supplementary Japanese phonetic annotation 4 beginning of a string of supplementary Chinese phonetic annotation 5 end of a string of supplementary phonetic annotations PTX with a parameter value of 1 indicates the beginning of the string of principal text intended to be presented in parallel with one or more strings of supplementary text. PTX with a parameter value of 2, 3 or 4 indicates the beginning of a string of supplementary text that is intended to be presented in parallel with either a string of principal text or the immediately preceding string of supplementary text, if any; at the same time it indicates the end of the preceding string of principal text or of the immediately preceding string of supplementary text, if any. The end of a string of supplementary text is indicated by a subsequent occurrence of PTX with a parameter value other than 1. PTX with a parameter value of 0 indicates the end of the strings of text intended to be presented in parallel with one another.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 12))
)

P_RM = ControlSequence(
    abbreviation='P_RM',
    name='PRIVATE RESET MODE',
    argument_count=-1,
    default_arguments=(),
    description='The private set mode function',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=ControlByteToken(bit_combination=BitCombination(3, 15)), intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 12))
)

P_SM = ControlSequence(
    abbreviation='P_SM',
    name='PRIVATE SET MODE',
    argument_count=-1,
    default_arguments=(),
    description='The private set mode function',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=ControlByteToken(bit_combination=BitCombination(3, 15)), intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 8))
)

QUAD = ControlSequence(
    abbreviation='QUAD',
    name='QUAD',
    argument_count=-1,
    default_arguments=(),
    description='QUAD is used to indicate the end of a string of graphic characters that are to be positioned on a single\nline according to the layout specified by the parameter values, see annex C:\n0\n flush to line home position margin\n1\n flush to line home position margin and fill with leader\n2\n centre between line home position and line limit position margins\n3\n centre between line home position and line limit position margins and fill with leader\n4\n flush to line limit position margin\n5\n flush to line limit position margin and fill with leader\n6\n flush to both margins\nThe beginning of the string to be positioned is indicated by the preceding occurrence in the data stream\nof either QUAD or one of the following formator functions: FORM FEED (FF), CHARACTER AND\nLINE POSITION (HVP), LINE FEED (LF), NEXT LINE (NEL), PAGE POSITION ABSOLUTE (PPA),\nPAGE POSITION BACKWARD (PPB), PAGE POSITION FORWARD (PPR), REVERSE LINE FEED\n(RI), LINE POSITION ABSOLUTE (VPA), LINE POSITION BACKWARD (VPB), LINE POSITION\nFORWARD (VPR), or LINE TABULATION (VT).\nThe line home position is established by the parameter value of SET LINE HOME (SLH). The line limit\nposition is established by the parameter value of SET LINE LIMIT (SLL).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 8))
)

RCP = ControlSequence(
    abbreviation='RCP',
    name='RESTORE CURSOR POSITION',
    argument_count=0,
    default_arguments=None,
    description='Restores the cursor position to what was previously saved.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(7, 5))
)

REP = ControlSequence(
    abbreviation='REP',
    name='REPEAT',
    argument_count=1,
    default_arguments=(1,),
    description='REP is used to indicate that the preceding character in the data stream, if it is a graphic character\n(represented by one or more bit combinations) including SPACE, is to be repeated n times, where n\nequals the value of Pn. If the character preceding REP is a control function or part of a control function,\nthe effect of REP is not defined by this Standard.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 2))
)

RM = ControlSequence(
    abbreviation='RM',
    name='RESET MODE',
    argument_count=-1,
    default_arguments=(),
    description='RM causes the modes of the receiving device to be reset as specified by the parameter values:\n1\n GUARDED AREA TRANSFER MODE (GATM)\n2\n KEYBOARD ACTION MODE (KAM)\n3\n CONTROL REPRESENTATION MODE (CRM)\n4\n INSERTION REPLACEMENT MODE (IRM)\n5\n STATUS REPORT TRANSFER MODE (SRTM)\n6\n ERASURE MODE (ERM)\n7\n LINE EDITING MODE (VEM)\n8\n BI-DIRECTIONAL SUPPORT MODE (BDSM)\n9\n DEVICE COMPONENT SELECT MODE (DCSM)\n10 CHARACTER EDITING MODE (HEM)\n11 POSITIONING UNIT MODE (PUM) (see F.4.1 in annex F)\n12 SEND/RECEIVE MODE (SRM)\n13 FORMAT EFFECTOR ACTION MODE (FEAM)\n14 FORMAT EFFECTOR TRANSFER MODE (FETM)\n15 MULTIPLE AREA TRANSFER MODE (MATM)\n16 TRANSFER TERMINATION MODE (TTM)\n17 SELECTED AREA TRANSFER MODE (SATM)\n18 TABULATION STOP MODE (TSM)\n19 (Shall not be used; see F.5.1 in annex F)\n20 (Shall not be used; see F.5.2 in annex F)\n21 GRAPHIC RENDITION COMBINATION MODE (GRCM)\n22 ZERO DEFAULT MODE (ZDM) (see F.4.2 in annex F)',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 12))
)

SACS = ControlSequence(
    abbreviation='SACS',
    name='SET ADDITIONAL CHARACTER SEPARATION',
    argument_count=1,
    default_arguments=(0,),
    description='SACS is used to establish extra inter-character escapement for subsequent text. The established extra\nescapement remains in effect until the next occurrence of SACS or of SET REDUCED CHARACTER\nSEPARATION (SRCS) in the data stream or until it is reset to the default value by a subsequent\noccurrence of CARRIAGE RETURN/LINE FEED (CR LF) or of NEXT LINE (NEL) in the data stream,\nsee annex C.\nPn specifies the number of units by which the inter-character escapement is enlarged.\nThe unit in which the parameter value is expressed is that established by the parameter value of SELECT\nSIZE UNIT (SSU).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 12))
)

SAPV = ControlSequence(
    abbreviation='SAPV',
    name='SELECT ALTERNATIVE PRESENTATION VARIANTS',
    argument_count=-1,
    default_arguments=(),
    description='SAPV is used to specify one or more variants for the presentation of subsequent text. The parameter\nvalues are\n0 default presentation (implementation-defined); cancels the effect of any preceding occurrence of\nSAPV in the data stream\n1\n the decimal digits are presented by means of the graphic symbols used in the Latin script\n2 the decimal digits are presented by means of the graphic symbols used in the Arabic script, i.e. the\nHindi symbols\n3 when the direction of the character path is right-to-left, each of the graphic characters in the graphic\ncharacter set(s) in use which is one of a left/right-handed pair (parentheses, square brackets, curly\nbrackets, greater-than/less-than signs, etc.) is presented as "mirrored", i.e. as the other member of the\npair. For example, the coded graphic character given the name LEFT PARENTHESIS is presented as\nRIGHT PARENTHESIS, and vice versa\n4 when the direction of the character path is right-to-left, all graphic characters which represent\noperators and delimiters in mathematical formulae and which are not symmetrical about a vertical\naxis are presented as mirrored about that vertical axis\n5\n the following graphic character is presented in its isolated form\n6\n the following graphic character is presented in its initial form\n7\n the following graphic character is presented in its medial form\n8\n the following graphic character is presented in its final form\n9 where the bit combination 02/14 is intended to represent a decimal mark in a decimal number it shall\nbe presented by means of the graphic symbol FULL STOP\n10 where the bit combination 02/14 is intended to represent a decimal mark in a decimal number it shall\nbe presented by means of the graphic symbol COMMA\n11 vowels are presented above or below the preceding character\n12 vowels are presented after the preceding character\n13 contextual shape determination of Arabic scripts, including the LAM-ALEPH ligature but excluding\nall other Arabic ligatures\n14 contextual shape determination of Arabic scripts, excluding all Arabic ligatures\n15 cancels the effect of parameter values 3 and 4\n16 vowels are not presented\n17 when the string direction is right-to-left, the italicized characters are slanted to the left; when the\nstring direction is left-to-right, the italicized characters are slanted to the right\n18 contextual shape determination of Arabic scripts is not used, the graphic characters - including the\ndigits - are presented in the form they are stored (Pass-through)\n19 contextual shape determination of Arabic scripts is not used, the graphic characters- excluding the\ndigits - are presented in the form they are stored (Pass-through)\n20 the graphic symbols used to present the decimal digits are device dependent\n21 establishes the effect of parameter values 5, 6, 7, and 8 for the following graphic characters until\ncancelled\n22 cancels the effect of parameter value 21, i.e. re-establishes the effect of parameter values 5, 6, 7, and\n8 for the next single graphic character only.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 13))
)

SCCP = ControlSequence(
    abbreviation='SCCP',
    name='SAVE CURRENT CURSOR POSITION',
    argument_count=0,
    default_arguments=None,
    description='Save the current cursor position.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(7, 3))
)

SCO = ControlSequence(
    abbreviation='SCO',
    name='SELECT CHARACTER ORIENTATION',
    argument_count=1,
    default_arguments=(0,),
    description='SCO is used to establish the amount of rotation of the graphic characters following in the data stream.\nThe established value remains in effect until the next occurrence of SCO in the data stream.\nThe parameter values are\n0\n 0°\n1\n 45°\n2\n 90°\n3\n 135°\n4\n 180°\n5\n 225°\n6\n 270°\n7\n 315°\nRotation is positive, i.e. counter-clockwise and applies to the normal presentation of the graphic\ncharacters along the character path. The centre of rotation of the affected graphic characters is not\ndefined by this Standard.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 5))
)

SCP = ControlSequence(
    abbreviation='SCP',
    name='SELECT CHARACTER PATH',
    argument_count=2,
    default_arguments=(None ,None),
    description='SCP is used to select the character path, relative to the line orientation, for the active line (the line that\ncontains the active presentation position) and subsequent lines in the presentation component. It is also\nused to update the content of the active line in the presentation component and the content of the active\nline (the line that contains the active data position) in the data component. This takes effect immediately.\nPs1 specifies the character path:\n1 left-to-right (in the case of horizontal line orientation), or top-to-bottom (in the case of vertical line\norientation)\n2 right-to-left (in the case of horizontal line orientation), or bottom-to-top (in the case of vertical line\norientation)\nPs2 specifies the effect on the content of the presentation component and the content of the data\ncomponent:\n0\n undefined (implementation-dependent)',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 11))
)

SCS = ControlSequence(
    abbreviation='SCS',
    name='SET CHARACTER SPACING',
    argument_count=1,
    default_arguments=(None,),
    description='SCS is used to establish the character spacing for subsequent text. The established spacing remains in\neffect until the next occurrence of SCS, or of SELECT CHARACTER SPACING (SHS) or of SPACING\nINCREMENT (SPI) in the data stream, see annex C.\nPn specifies the character spacing.\nThe unit in which the parameter value is expressed is that established by the parameter value of SELECT\nSIZE UNIT (SSU).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 7))
)

SD = ControlSequence(
    abbreviation='SD',
    name='SCROLL DOWN',
    argument_count=1,
    default_arguments=(1,),
    description='Scrolls the contents of the display downwards by a specified number of lines.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 4))
)

SDS = ControlSequence(
    abbreviation='SDS',
    name='START DIRECTED STRING',
    argument_count=1,
    default_arguments=(0,),
    description='SDS is used to establish in the data component the beginning and the end of a string of characters as well as the direction of the string. This direction may be different from that currently established. The indicated string follows the preceding text. The established character progression is not affected. The beginning of a directed string is indicated by SDS with a parameter value not equal to 0. A directed string may contain one or more nested strings. These nested strings may be directed strings the beginnings of which are indicated by SDS with a parameter value not equal to 0, or reversed strings the beginnings of which are indicated by START REVERSED STRING (SRS) with a parameter value of 1. Every beginning of such a string invokes the next deeper level of nesting. This Standard does not define the location of the active data position within any such nested string. The end of a directed string is indicated by SDS with a parameter value of 0. Every end of such a string re-establishes the next higher level of nesting (the one in effect prior to the string just ended). The direction is re-established to that in effect prior to the string just ended. The active data position is moved to the character position following the characters of the string just ended.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 13))
)

SEE = ControlSequence(
    abbreviation='SEE',
    name='SELECT EDITING EXTENT',
    argument_count=1,
    default_arguments=(0,),
    description='Defines whether editing operations affect the character, token, field, line, or whole area.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 1))
)

SEF = ControlSequence(
    abbreviation='SEF',
    name='SHEET EJECT AND FEED',
    argument_count=2,
    default_arguments=(0 ,0),
    description='SEF causes a sheet of paper to be ejected from a printing device into a specified output stacker and\nanother sheet to be loaded into the printing device from a specified paper bin.\nParameter values of Ps1 are:\n0\n eject sheet, no new sheet loaded\n1\n eject sheet and load another from bin 1\n2\n eject sheet and load another from bin 2\n.\n.\n.\nn\n eject sheet and load another from bin n\nParameter values of Ps2 are:\n0\n eject sheet, no stacker specified\n1\n eject sheet into stacker 1\n2\n eject sheet into stacker 2\n.\n.\n.\nn\n eject sheet into stacker n\n',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 9))
)

SGR = ControlSequence(
    abbreviation='SGR',
    name='SELECT GRAPHIC RENDITION',
    argument_count=-1,
    default_arguments=(),
    description='Sets visual rendering styles for subsequent graphic characters. Defaults to 0 (Reset).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 13))
)

SHS = ControlSequence(
    abbreviation='SHS',
    name='SELECT CHARACTER SPACING',
    argument_count=1,
    default_arguments=(0,),
    description='SHS is used to establish the character spacing for subsequent text. The established spacing remains in\neffect until the next occurrence of SHS or of SET CHARACTER SPACING (SCS) or of SPACING\nINCREMENT (SPI) in the data stream. The parameter values are\n0\n 10 characters per 25,4 mm\n1\n 12 characters per 25,4 mm\n2\n 15 characters per 25,4 mm\n3\n 6 characters per 25,4 mm\n4\n 3 characters per 25,4 mm\n5\n 9 characters per 50,8 mm\n6\n 4 characters per 25,4 mm',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 11))
)

SIMD = ControlSequence(
    abbreviation='SIMD',
    name='SELECT IMPLICIT MOVEMENT DIRECTION',
    argument_count=1,
    default_arguments=(0,),
    description='SIMD is used to select the direction of implicit movement of the data position relative to the character\nprogression. The direction selected remains in effect until the next occurrence of SIMD.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 14))
)

SL = ControlSequence(
    abbreviation='SL',
    name='SCROLL LEFT',
    argument_count=1,
    default_arguments=(1,),
    description='SL causes the data in the presentation component to be moved by n character positions if the line\norientation is horizontal, or by n line positions if the line orientation is vertical, such that the data appear\nto move to the left; where n equals the value of Pn.\nThe active presentation position is not affected by this control function.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 0))
)

SLH = ControlSequence(
    abbreviation='SLH',
    name='SET LINE HOME',
    argument_count=1,
    default_arguments=(None,),
    description='If the DEVICE COMPONENT SELECT MODE is set to PRESENTATION, SLH is used to establish at\ncharacter position n in the active line (the line that contains the active presentation position) and lines of\nsubsequent text in the presentation component the position to which the active presentation position will\nbe moved by subsequent occurrences of CARRIAGE RETURN (CR), DELETE LINE (DL), INSERT\nLINE (IL) or NEXT LINE (NEL) in the data stream; where n equals the value of Pn. In the case of a\ndevice without data component, it is also the position ahead of which no implicit movement of the active\npresentation position shall occur.\nIf the DEVICE COMPONENT SELECT MODE is set to DATA, SLH is used to establish at character\nposition n in the active line (the line that contains the active data position) and lines of subsequent text\nin the data component the position to which the active data position will be moved by subsequent\noccurrences of CARRIAGE RETURN (CR), DELETE LINE (DL), INSERT LINE (IL) or NEXT LINE\n(NEL) in the data stream; where n equals the value of Pn. It is also the position ahead of which no\nimplicit movement of the active data position shall occur.\nThe established position is called the line home position and remains in effect until the next occurrence\nof SLH in the data stream.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 5))
)

SLL = ControlSequence(
    abbreviation='SLL',
    name='SET LINE LIMIT',
    argument_count=1,
    default_arguments=(None,),
    description='If the DEVICE COMPONENT SELECT MODE is set to PRESENTATION, SLL is used to establish at\ncharacter position n in the active line (the line that contains the active presentation position) and lines of\nsubsequent text in the presentation component the position to which the active presentation position will\nbe moved by subsequent occurrences of CARRIAGE RETURN (CR), or NEXT LINE (NEL) in the data\nstream if the parameter value of SELECT IMPLICIT MOVEMENT DIRECTION (SIMD) is equal to 1;\nwhere n equals the value of Pn. In the case of a device without data component, it is also the position\nbeyond which no implicit movement of the active presentation position shall occur.\nIf the DEVICE COMPONENT SELECT MODE is set to DATA, SLL is used to establish at character\nposition n in the active line (the line that contains the active data position) and lines of subsequent text\nin the data component the position beyond which no implicit movement of the active data position shall\noccur. It is also the position in the data component to which the active data position will be moved by\nsubsequent occurrences of CR or NEL in the data stream, if the parameter value of SELECT IMPLICIT\nMOVEMENT DIRECTION (SIMD) is equal to 1.\nThe established position is called the line limit position and remains in effect until the next occurrence\nof SLL in the data stream.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 6))
)

SLS = ControlSequence(
    abbreviation='SLS',
    name='SET LINE SPACING',
    argument_count=1,
    default_arguments=(None,),
    description='SLS is used to establish the line spacing for subsequent text. The established spacing remains in effect\nuntil the next occurrence of SLS or of SELECT LINE SPACING (SVS) or of SPACING INCREMENT\n(SPI) in the data stream.\nPn specifies the line spacing.\nThe unit in which the parameter value is expressed is that established by the parameter value of SELECT\nSIZE UNIT (SSU).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 8))
)

SM = ControlSequence(
    abbreviation='SM',
    name='SET MODE',
    argument_count=-1,
    default_arguments=(),
    description='SM causes the modes of the receiving device to be set as specified by the parameter values:\n1\n GUARDED AREA TRANSFER MODE (GATM)\n2\n KEYBOARD ACTION MODE (KAM)\n3\n CONTROL REPRESENTATION MODE (CRM)\n4\n INSERTION REPLACEMENT MODE (IRM)\n5\n STATUS REPORT TRANSFER MODE (SRTM)\n6\n ERASURE MODE (ERM)\n7\n LINE EDITING MODE (VEM)\n8\n BI-DIRECTIONAL SUPPORT MODE (BDSM)\n9\n DEVICE COMPONENT SELECT MODE (DCSM)\n10 CHARACTER EDITING MODE (HEM)\n11 POSITIONING UNIT MODE (PUM) (see F.4.1 in annex F)\n12 SEND/RECEIVE MODE (SRM)\n13 FORMAT EFFECTOR ACTION MODE (FEAM)\n14 FORMAT EFFECTOR TRANSFER MODE (FETM)\n15 MULTIPLE AREA TRANSFER MODE (MATM)\n16 TRANSFER TERMINATION MODE (TTM)\n17 SELECTED AREA TRANSFER MODE (SATM)\n18 TABULATION STOP MODE (TSM)\n19 (Shall not be used; see F.5.1 in annex F)\n20 (Shall not be used; see F.5.2 in annex F)\n21 GRAPHIC RENDITION COMBINATION (GRCM)\n22 ZERO DEFAULT MODE (ZDM) (see F.4.2 in annex F)',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 8))
)

SPD = ControlSequence(
    abbreviation='SPD',
    name='SELECT PRESENTATION DIRECTIONS',
    argument_count=2,
    default_arguments=(0 ,0),
    description='SPD is used to select the line orientation, the line progression, and the character path in the presentation\ncomponent. It is also used to update the content of the presentation component and the content of the\ndata component. This takes effect immediately.\nPs1 specifies the line orientation, the line progression and the character path\nPs2 specifies the effect on the content of the presentation component and the content of the data\ncomponent:',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 3))
)

SPH = ControlSequence(
    abbreviation='SPH',
    name='SET PAGE HOME',
    argument_count=1,
    default_arguments=(None,),
    description='If the DEVICE COMPONENT SELECT MODE is set to PRESENTATION, SPH is used to establish at\nline position n in the active page (the page that contains the active presentation position) and subsequent\npages in the presentation component the position to which the active presentation position will be moved\nby subsequent occurrences of FORM FEED (FF) in the data stream; where n equals the value of Pn. In\nthe case of a device without data component, it is also the position ahead of which no implicit movement\nof the active presentation position shall occur.\nIf the DEVICE COMPONENT SELECT MODE is set to DATA, SPH is used to establish at line position\nn in the active page (the page that contains the active data position) and subsequent pages in the data\ncomponent the position to which the active data position will be moved by subsequent occurrences of\nFORM FEED (FF) in the data stream; where n equals the value of Pn. It is also the position ahead of\nwhich no implicit movement of the active presentation position shall occur.\nThe established position is called the page home position and remains in effect until the next occurrence\nof SPH in the data stream.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 9))
)

SPI = ControlSequence(
    abbreviation='SPI',
    name='SPACING INCREMENT',
    argument_count=2,
    default_arguments=(None ,None),
    description='SPI is used to establish the line spacing and the character spacing for subsequent text. The established\nline spacing remains in effect until the next occurrence of SPI or of SET LINE SPACING (SLS) or of\nSELECT LINE SPACING (SVS) in the data stream. The established character spacing remains in effect\nuntil the next occurrence of SET CHARACTER SPACING (SCS) or of SELECT CHARACTER\nSPACING (SHS) in the data stream, see annex C.\nPn1 specifies the line spacing\nPn2 specifies the character spacing\nThe unit in which the parameter values are expressed is that established by the parameter value of\nSELECT SIZE UNIT (SSU).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 7))
)

SPL = ControlSequence(
    abbreviation='SPL',
    name='SET PAGE LIMIT',
    argument_count=1,
    default_arguments=(None,),
    description='If the DEVICE COMPONENT SELECT MODE is set to PRESENTATION, SPL is used to establish at\nline position n in the active page (the page that contains the active presentation position) and pages of\nsubsequent text in the presentation component the position beyond which the active presentation position\ncan normally not be moved; where n equals the value of Pn. In the case of a device without data\ncomponent, it is also the position beyond which no implicit movement of the active presentation position\nshall occur.\nIf the DEVICE COMPONENT SELECT MODE is set to DATA, SPL is used to establish at line position\nn in the active page (the page that contains the active data position) and pages of subsequent text in the\ndata component the position beyond which no implicit movement of the active data position shall occur.\nThe established position is called the page limit position and remains in effect until the next occurrence\nof SPL in the data stream.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 10))
)

SPQR = ControlSequence(
    abbreviation='SPQR',
    name='SELECT PRINT QUALITY AND RAPIDITY',
    argument_count=1,
    default_arguments=(0,),
    description='SPQR is used to select the relative print quality and the print speed for devices the output quality and\nspeed of which are inversely related. The selected values remain in effect until the next occurrence of\nSPQR in the data stream. The parameter values are\n0\n highest available print quality, low print speed\n1\n medium print quality, medium print speed\n2\n draft print quality, highest available print speed',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 8))
)

SR = ControlSequence(
    abbreviation='SR',
    name='SCROLL RIGHT',
    argument_count=1,
    default_arguments=(1,),
    description='SR causes the data in the presentation component to be moved by n character positions if the line\norientation is horizontal, or by n line positions if the line orientation is vertical, such that the data appear\nto move to the right; where n equals the value of Pn.\nThe active presentation position is not affected by this control function.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 1))
)

SRCS = ControlSequence(
    abbreviation='SRCS',
    name='SET REDUCED CHARACTER SEPARATION',
    argument_count=1,
    default_arguments=(0,),
    description='SRCS is used to establish reduced inter-character escapement for subsequent text. The established\nreduced escapement remains in effect until the next occurrence of SRCS or of SET ADDITIONAL\nCHARACTER SEPARATION (SACS) in the data stream or until it is reset to the default value by a\nsubsequent occurrence of CARRIAGE RETURN/LINE FEED (CR/LF) or of NEXT LINE (NEL) in the\ndata stream, see annex C.\nPn specifies the number of units by which the intercharacter escapement is reduced.\nThe unit in which the parameter values are expressed is that established by the parameter value of\nSELECT SIZE UNIT (SSU).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 6))
)

SRS = ControlSequence(
    abbreviation='SRS',
    name='START REVERSED STRING',
    argument_count=1,
    default_arguments=(1,),
    description='SRS is used to establish in the data component the beginning and the end of a string of characters as well as the direction of the string. This direction is opposite to that currently established. The indicated string follows the preceding text. The established character progression is not affected. The beginning of a reversed string is indicated by SRS with a parameter value of 1. A reversed string may contain one or more nested strings. These nested strings may be reversed strings the beginnings of which are indicated by SRS with a parameter value of 1, or directed strings the beginnings of which are indicated by START DIRECTED STRING (SDS) with a parameter value not equal to 0. Every beginning of such a string invokes the next deeper level of nesting. This Standard does not define the location of the active data position within any such nested string. The end of a reversed string is indicated by SRS with a parameter value of 0. Every end of such a string re-establishes the next higher level of nesting (the one in effect prior to the string just ended). The direction is re-established to that in effect prior to the string just ended. The active data position is moved to the character position following the characters of the string just ended. The parameter values are: 0 end of a reversed string; re-establish the previous direction 1 beginning of a reversed string; reverse the direction. NOTE 1 The effect of receiving a CVT, HT, SCP, SPD or VT control function within an SRS string is not defined by this Standard. NOTE 2 The control functions for area definition (DAQ, EPA, ESA, SPA, SSA) should not be used within an SRS string.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 11))
)

SSU = ControlSequence(
    abbreviation='SSU',
    name='SELECT SIZE UNIT',
    argument_count=1,
    default_arguments=(0,),
    description='SSU is used to establish the unit in which the numeric parameters of certain control functions are\nexpressed. The established unit remains in effect until the next occurrence of SSU in the data stream.\nThe parameter values are\n0\n CHARACTER - The dimensions of this unit are device-dependent\n1\n MILLIMETRE\n2\n COMPUTER DECIPOINT - 0,035 28 mm (1/720 of 25,4 mm)\n3\n DECIDIDOT - 0,037 59 mm (10/266 mm)\n4\n MIL - 0,025 4 mm (1/1 000 of 25,4 mm)\n5\n BASIC MEASURING UNIT (BMU) - 0,021 17 mm (1/1 200 of 25,4 mm)\n6\n MICROMETRE - 0,001 mm\n7\n PIXEL - The smallest increment that can be specified in a device\n8\n DECIPOINT - 0,035 14 mm (35/996 mm)',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 9))
)

SSW = ControlSequence(
    abbreviation='SSW',
    name='SET SPACE WIDTH',
    argument_count=1,
    default_arguments=(None,),
    description='SSW is used to establish for subsequent text the character escapement associated with the character\nSPACE. The established escapement remains in effect until the next occurrence of SSW in the data\nstream or until it is reset to the default value by a subsequent occurrence of CARRIAGE RETURN/LINE\nFEED (CR/LF), CARRIAGE RETURN/FORM FEED (CR/FF), or of NEXT LINE (NEL) in the data\nstream, see annex C.\nPn specifies the escapement.\nThe unit in which the parameter value is expressed is that established by the parameter value of SELECT\nSIZE UNIT (SSU).\nThe default character escapement of SPACE is specified by the most recent occurrence of SET\nCHARACTER SPACING (SCS) or of SELECT CHARACTER SPACING (SHS) or of SELECT\nSPACING INCREMENT (SPI) in the data stream if the current font has constant spacing, or is specified\nby the nominal width of the character SPACE in the current font if that font has proportional spacing.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 11))
)

STAB = ControlSequence(
    abbreviation='STAB',
    name='SELECTIVE TABULATION',
    argument_count=1,
    default_arguments=(None,),
    description='STAB causes subsequent text in the presentation component to be aligned according to the position and\nthe properties of a tabulation stop which is selected from a list according to the value of the parameter\nPs.\nThe use of this control function and means of specifying a list of tabulation stops to be referenced by the\ncontrol function are specified in other standards, for example ISO 8613-6.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 14))
)

SU = ControlSequence(
    abbreviation='SU',
    name='SCROLL UP',
    argument_count=1,
    default_arguments=(1,),
    description='Scrolls the contents of the display upwards by a specified number of lines.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(5, 3))
)

SVS = ControlSequence(
    abbreviation='SVS',
    name='SELECT LINE SPACING',
    argument_count=1,
    default_arguments=(0,),
    description='SVS is used to establish the line spacing for subsequent text. The established spacing remains in effect\nuntil the next occurrence of SVS or of SET LINE SPACING (SLS) or of SPACING INCREMENT (SPI)\nin the data stream. The parameter values are:\n0\n 6 lines per 25,4 mm\n1\n 4 lines per 25,4 mm\n2\n 3 lines per 25,4 mm\n3\n 12 lines per 25,4 mm\n4\n 8 lines per 25,4 mm\n5\n 6 lines per 30,0 mm\n6\n 4 lines per 30,0 mm\n7\n 3 lines per 30,0 mm\n8\n 12 lines per 30,0 mm\n9\n 2 lines per 25,4 mm',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 12))
)

TAC = ControlSequence(
    abbreviation='TAC',
    name='TABULATION ALIGNED CENTRED',
    argument_count=1,
    default_arguments=(None,),
    description='TAC causes a character tabulation stop calling for centring to be set at character position n in the active\nline (the line that contains the active presentation position) and lines of subsequent text in the\npresentation component, where n equals the value of Pn. TAC causes the replacement of any tabulation\nstop previously set at that character position, but does not affect other tabulation stops.\nA text string centred upon a tabulation stop set by TAC will be positioned so that the (trailing edge of\nthe) first graphic character and the (leading edge of the) last graphic character are at approximately equal\ndistances from the tabulation stop.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 2))
)

TALE = ControlSequence(
    abbreviation='TALE',
    name='TABULATION ALIGNED LEADING EDGE',
    argument_count=1,
    default_arguments=(None,),
    description='TALE causes a character tabulation stop calling for leading edge alignment to be set at character\nposition n in the active line (the line that contains the active presentation position) and lines of\nsubsequent text in the presentation component, where n equals the value of Pn. TALE causes the\nreplacement of any tabulation stop previously set at that character position, but does not affect other\ntabulation stops.\nA text string aligned with a tabulation stop set by TALE will be positioned so that the (leading edge of\nthe) last graphic character of the string is placed at the tabulation stop.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 1))
)

TATE = ControlSequence(
    abbreviation='TATE',
    name='TABULATION ALIGNED TRAILING EDGE',
    argument_count=1,
    default_arguments=(None,),
    description='TATE causes a character tabulation stop calling for trailing edge alignment to be set at character\nposition n in the active line (the line that contains the active presentation position) and lines of\nsubsequent text in the presentation component, where n equals the value of Pn. TATE causes the\nreplacement of any tabulation stop previously set at that character position, but does not affect other\ntabulation stops. A text string aligned with a tabulation stop set by TATE will be positioned so that the (trailing edge of\nthe) first graphic character of the string is placed at the tabulation stop.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 0))
)

TBC = ControlSequence(
    abbreviation='TBC',
    name='TABULATION CLEAR',
    argument_count=1,
    default_arguments=(0,),
    description='TBC causes one or more tabulation stops in the presentation component to be cleared, depending on the\nparameter value:\n0\n the character tabulation stop at the active presentation position is cleared\n1\n the line tabulation stop at the active line is cleared\n2\n all character tabulation stops in the active line are cleared\n3\n all character tabulation stops are cleared\n4\n all line tabulation stops are cleared\n5\n all tabulation stops are cleared\nIn the case of parameter value 0 or 2 the number of lines affected depends on the setting of the\nTABULATION STOP MODE (TSM)',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 7))
)

TCC = ControlSequence(
    abbreviation='TCC',
    name='TABULATION CENTRED ON CHARACTER',
    argument_count=2,
    default_arguments=(None ,32),
    description='TCC causes a character tabulation stop calling for alignment of a target graphic character to be set at\ncharacter position n in the active line (the line that contains the active presentation position) and lines of\nsubsequent text in the presentation component, where n equals the value of Pn1, and the target character\nabout which centring is to be performed is specified by Pn2. TCC causes the replacement of any\ntabulation stop previously set at that character position, but does not affect other tabulation stops.\nThe positioning of a text string aligned with a tabulation stop set by TCC will be determined by the first\noccurrence in the string of the target graphic character; that character will be centred upon the tabulation\nstop. If the target character does not occur within the string, then the trailing edge of the first character\nof the string will be positioned at the tabulation stop.\nThe value of Pn2 indicates the code table position (binary value) of the target character in the currently\ninvoked code. For a 7-bit code, the permissible range of values is 32 to 127; for an 8-bit code, the\npermissible range of values is 32 to 127 and 160 to 255.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 3))
)

TSR = ControlSequence(
    abbreviation='TSR',
    name='TABULATION STOP REMOVE',
    argument_count=1,
    default_arguments=(None,),
    description='TSR causes any character tabulation stop at character position n in the active line (the line that contains\nthe active presentation position) and lines of subsequent text in the presentation component to be\ncleared, but does not affect other tabulation stops. n equals the value of Pn.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 4))
)

TSS = ControlSequence(
    abbreviation='TSS',
    name='THIN SPACE SPECIFICATION',
    argument_count=1,
    default_arguments=(None,),
    description='TSS is used to establish the width of a thin space for subsequent text. The established width remains in\neffect until the next occurrence of TSS in the data stream, see annex C.\nPn specifies the width of the thin space.\nThe unit in which the parameter value is expressed is that established by the parameter value of SELECT\nSIZE UNIT (SSU).',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=(BitCombination(2, 0),), arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(4, 5))
)

VPA = ControlSequence(
    abbreviation='VPA',
    name='LINE POSITION ABSOLUTE',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position to a specified vertical line number without affecting the horizontal coordinate.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 4))
)

VPB = ControlSequence(
    abbreviation='VPB',
    name='LINE POSITION BACKWARD',
    argument_count=1,
    default_arguments=(1,),
    description='VPB causes the active data position to be moved by n line positions in the data component in a direction\nopposite to that of the line progression, where n equals the value of Pn.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 11))
)

VPR = ControlSequence(
    abbreviation='VPR',
    name='LINE POSITION RELATIVE',
    argument_count=1,
    default_arguments=(1,),
    description='Moves the active position downward by a specified number of lines relative to its current spot.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(6, 5))
)

WNDMAN = ControlSequence(
    abbreviation='WNDMAN',
    name='WINDOW MANIPULATION',
    argument_count=-1,
    default_arguments=(),
    description='XTERM: Manipulate the window using the window manager.',
    init_token=ControlSequenceToken(ControlSequenceToken.SEVEN_BIT_MODE_INTRODUCER, private_marker=None, intermediate_bit_combinations_sequence=EMPTY_SEQUENCE, arguments=EMPTY_PARAMETERS, final_bit_combination=BitCombination(7, 4))
)

C0 = frozenset({
    ACK,
    BEL,
    BS,
    CAN,
    CR,
    DC1,
    DC2,
    DC3,
    DC4,
    DLE,
    EM,
    ENQ,
    EOT,
    ESC,
    ETB,
    ETX,
    FF,
    HT,
    IS1,
    IS2,
    IS3,
    IS4,
    LF,
    LS0,
    LS1,
    NAK,
    NUL,
    SI,
    SO,
    SOH,
    STX,
    SUB,
    SYN,
    VT
})

C1 = frozenset({
    APC,
    BPH,
    CCH,
    CSI,
    DCS,
    EPA,
    ESA,
    HTJ,
    HTS,
    MW,
    NBH,
    NEL,
    OSC,
    PLD,
    PLU,
    PM,
    PU1,
    PU2,
    RI,
    SCI,
    SOS,
    SPA,
    SS2,
    SS3,
    SSA,
    ST,
    STS,
    VTS
})

FS = frozenset({
    CMD,
    DMI,
    EMI,
    INT,
    LS1R,
    LS2,
    LS2R,
    LS3,
    LS3R,
    RIS
})

CONTROL_SEQUENCES = frozenset({
    CBT,
    CHA,
    CHT,
    CNL,
    CPL,
    CPR,
    CTC,
    CUB,
    CUD,
    CUF,
    CUP,
    CUU,
    CVT,
    DA,
    DAQ,
    DCH,
    DECLL,
    DECSTBM,
    DL,
    DSR,
    DTA,
    EA,
    ECH,
    ED,
    EF,
    EL,
    FNK,
    FNT,
    GCC,
    GSM,
    GSS,
    HPA,
    HPB,
    HPR,
    HVP,
    ICH,
    IDCS,
    IGS,
    IL,
    JFY,
    MC,
    NP,
    PEC,
    PFS,
    PP,
    PPA,
    PPB,
    PPR,
    PTX,
    P_RM,
    P_SM,
    QUAD,
    RCP,
    REP,
    RM,
    SACS,
    SAPV,
    SCCP,
    SCO,
    SCP,
    SCS,
    SD,
    SDS,
    SEE,
    SEF,
    SGR,
    SHS,
    SIMD,
    SL,
    SLH,
    SLL,
    SLS,
    SM,
    SPD,
    SPH,
    SPI,
    SPL,
    SPQR,
    SR,
    SRCS,
    SRS,
    SSU,
    SSW,
    STAB,
    SU,
    SVS,
    TAC,
    TALE,
    TATE,
    TBC,
    TCC,
    TSR,
    TSS,
    VPA,
    VPB,
    VPR,
    WNDMAN
})

SETS = frozenset({
    C0,
    C1,
    FS,
    CONTROL_SEQUENCES
})

__all__ = [
    'ACK',
    'BEL',
    'BS',
    'CAN',
    'CR',
    'DC1',
    'DC2',
    'DC3',
    'DC4',
    'DLE',
    'EM',
    'ENQ',
    'EOT',
    'ESC',
    'ETB',
    'ETX',
    'FF',
    'HT',
    'IS1',
    'IS2',
    'IS3',
    'IS4',
    'LF',
    'LS0',
    'LS1',
    'NAK',
    'NUL',
    'SI',
    'SO',
    'SOH',
    'STX',
    'SUB',
    'SYN',
    'VT',
    'APC',
    'BPH',
    'CCH',
    'CSI',
    'DCS',
    'EPA',
    'ESA',
    'HTJ',
    'HTS',
    'MW',
    'NBH',
    'NEL',
    'OSC',
    'PLD',
    'PLU',
    'PM',
    'PU1',
    'PU2',
    'RI',
    'SCI',
    'SOS',
    'SPA',
    'SS2',
    'SS3',
    'SSA',
    'ST',
    'STS',
    'VTS',
    'CMD',
    'DMI',
    'EMI',
    'INT',
    'LS1R',
    'LS2',
    'LS2R',
    'LS3',
    'LS3R',
    'RIS',
    'CBT',
    'CHA',
    'CHT',
    'CNL',
    'CPL',
    'CPR',
    'CTC',
    'CUB',
    'CUD',
    'CUF',
    'CUP',
    'CUU',
    'CVT',
    'DA',
    'DAQ',
    'DCH',
    'DECLL',
    'DECSTBM',
    'DL',
    'DSR',
    'DTA',
    'EA',
    'ECH',
    'ED',
    'EF',
    'EL',
    'FNK',
    'FNT',
    'GCC',
    'GSM',
    'GSS',
    'HPA',
    'HPB',
    'HPR',
    'HVP',
    'ICH',
    'IDCS',
    'IGS',
    'IL',
    'JFY',
    'MC',
    'NP',
    'PEC',
    'PFS',
    'PP',
    'PPA',
    'PPB',
    'PPR',
    'PTX',
    'P_RM',
    'P_SM',
    'QUAD',
    'RCP',
    'REP',
    'RM',
    'SACS',
    'SAPV',
    'SCCP',
    'SCO',
    'SCP',
    'SCS',
    'SD',
    'SDS',
    'SEE',
    'SEF',
    'SGR',
    'SHS',
    'SIMD',
    'SL',
    'SLH',
    'SLL',
    'SLS',
    'SM',
    'SPD',
    'SPH',
    'SPI',
    'SPL',
    'SPQR',
    'SR',
    'SRCS',
    'SRS',
    'SSU',
    'SSW',
    'STAB',
    'SU',
    'SVS',
    'TAC',
    'TALE',
    'TATE',
    'TBC',
    'TCC',
    'TSR',
    'TSS',
    'VPA',
    'VPB',
    'VPR',
    'WNDMAN',
    'C0',
    'C1',
    'FS',
    'CONTROL_SEQUENCES',
    'SETS'
]