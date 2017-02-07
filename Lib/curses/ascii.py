"""Constants oraz membership tests dla ASCII characters"""

NUL     = 0x00  # ^@
SOH     = 0x01  # ^A
STX     = 0x02  # ^B
ETX     = 0x03  # ^C
EOT     = 0x04  # ^D
ENQ     = 0x05  # ^E
ACK     = 0x06  # ^F
BEL     = 0x07  # ^G
BS      = 0x08  # ^H
TAB     = 0x09  # ^I
HT      = 0x09  # ^I
LF      = 0x0a  # ^J
NL      = 0x0a  # ^J
VT      = 0x0b  # ^K
FF      = 0x0c  # ^L
CR      = 0x0d  # ^M
SO      = 0x0e  # ^N
SI      = 0x0f  # ^O
DLE     = 0x10  # ^P
DC1     = 0x11  # ^Q
DC2     = 0x12  # ^R
DC3     = 0x13  # ^S
DC4     = 0x14  # ^T
NAK     = 0x15  # ^U
SYN     = 0x16  # ^V
ETB     = 0x17  # ^W
CAN     = 0x18  # ^X
EM      = 0x19  # ^Y
SUB     = 0x1a  # ^Z
ESC     = 0x1b  # ^[
FS      = 0x1c  # ^\
GS      = 0x1d  # ^]
RS      = 0x1e  # ^^
US      = 0x1f  # ^_
SP      = 0x20  # space
DEL     = 0x7f  # delete

controlnames = [
"NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
"BS",  "HT",  "LF",  "VT",  "FF",  "CR",  "SO",  "SI",
"DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
"CAN", "EM",  "SUB", "ESC", "FS",  "GS",  "RS",  "US",
"SP"
]

def _ctoi(c):
    jeżeli type(c) == type(""):
        zwróć ord(c)
    inaczej:
        zwróć c

def isalnum(c): zwróć isalpha(c) albo isdigit(c)
def isalpha(c): zwróć isupper(c) albo islower(c)
def isascii(c): zwróć _ctoi(c) <= 127          # ?
def isblank(c): zwróć _ctoi(c) w (8,32)
def iscntrl(c): zwróć _ctoi(c) <= 31
def isdigit(c): zwróć _ctoi(c) >= 48 oraz _ctoi(c) <= 57
def isgraph(c): zwróć _ctoi(c) >= 33 oraz _ctoi(c) <= 126
def islower(c): zwróć _ctoi(c) >= 97 oraz _ctoi(c) <= 122
def isprint(c): zwróć _ctoi(c) >= 32 oraz _ctoi(c) <= 126
def ispunct(c): zwróć _ctoi(c) != 32 oraz nie isalnum(c)
def isspace(c): zwróć _ctoi(c) w (9, 10, 11, 12, 13, 32)
def isupper(c): zwróć _ctoi(c) >= 65 oraz _ctoi(c) <= 90
def isxdigit(c): zwróć isdigit(c) albo \
    (_ctoi(c) >= 65 oraz _ctoi(c) <= 70) albo (_ctoi(c) >= 97 oraz _ctoi(c) <= 102)
def isctrl(c): zwróć _ctoi(c) < 32
def ismeta(c): zwróć _ctoi(c) > 127

def ascii(c):
    jeżeli type(c) == type(""):
        zwróć chr(_ctoi(c) & 0x7f)
    inaczej:
        zwróć _ctoi(c) & 0x7f

def ctrl(c):
    jeżeli type(c) == type(""):
        zwróć chr(_ctoi(c) & 0x1f)
    inaczej:
        zwróć _ctoi(c) & 0x1f

def alt(c):
    jeżeli type(c) == type(""):
        zwróć chr(_ctoi(c) | 0x80)
    inaczej:
        zwróć _ctoi(c) | 0x80

def unctrl(c):
    bits = _ctoi(c)
    jeżeli bits == 0x7f:
        rep = "^?"
    albo_inaczej isprint(bits & 0x7f):
        rep = chr(bits & 0x7f)
    inaczej:
        rep = "^" + chr(((bits & 0x7f) | 0x20) + 0x20)
    jeżeli bits & 0x80:
        zwróć "!" + rep
    zwróć rep
