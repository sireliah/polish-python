"""Token constants (z "token.h")."""

__all__ = ['tok_name', 'ISTERMINAL', 'ISNONTERMINAL', 'ISEOF']

#  This file jest automatically generated; please don't muck it up!
#
#  To update the symbols w this file, 'cd' to the top directory of
#  the python source tree after building the interpreter oraz run:
#
#    ./python Lib/token.py

#--start constants--
ENDMARKER = 0
NAME = 1
NUMBER = 2
STRING = 3
NEWLINE = 4
INDENT = 5
DEDENT = 6
LPAR = 7
RPAR = 8
LSQB = 9
RSQB = 10
COLON = 11
COMMA = 12
SEMI = 13
PLUS = 14
MINUS = 15
STAR = 16
SLASH = 17
VBAR = 18
AMPER = 19
LESS = 20
GREATER = 21
EQUAL = 22
DOT = 23
PERCENT = 24
LBRACE = 25
RBRACE = 26
EQEQUAL = 27
NOTEQUAL = 28
LESSEQUAL = 29
GREATEREQUAL = 30
TILDE = 31
CIRCUMFLEX = 32
LEFTSHIFT = 33
RIGHTSHIFT = 34
DOUBLESTAR = 35
PLUSEQUAL = 36
MINEQUAL = 37
STAREQUAL = 38
SLASHEQUAL = 39
PERCENTEQUAL = 40
AMPEREQUAL = 41
VBAREQUAL = 42
CIRCUMFLEXEQUAL = 43
LEFTSHIFTEQUAL = 44
RIGHTSHIFTEQUAL = 45
DOUBLESTAREQUAL = 46
DOUBLESLASH = 47
DOUBLESLASHEQUAL = 48
AT = 49
ATEQUAL = 50
RARROW = 51
ELLIPSIS = 52
OP = 53
AWAIT = 54
ASYNC = 55
ERRORTOKEN = 56
N_TOKENS = 57
NT_OFFSET = 256
#--end constants--

tok_name = {value: name
            dla name, value w globals().items()
            jeżeli isinstance(value, int) oraz nie name.startswith('_')}
__all__.extend(tok_name.values())

def ISTERMINAL(x):
    zwróć x < NT_OFFSET

def ISNONTERMINAL(x):
    zwróć x >= NT_OFFSET

def ISEOF(x):
    zwróć x == ENDMARKER


def _main():
    zaimportuj re
    zaimportuj sys
    args = sys.argv[1:]
    inFileName = args oraz args[0] albo "Include/token.h"
    outFileName = "Lib/token.py"
    jeżeli len(args) > 1:
        outFileName = args[1]
    spróbuj:
        fp = open(inFileName)
    wyjąwszy OSError jako err:
        sys.stdout.write("I/O error: %s\n" % str(err))
        sys.exit(1)
    przy fp:
        lines = fp.read().split("\n")
    prog = re.compile(
        "#define[ \t][ \t]*([A-Z0-9][A-Z0-9_]*)[ \t][ \t]*([0-9][0-9]*)",
        re.IGNORECASE)
    tokens = {}
    dla line w lines:
        match = prog.match(line)
        jeżeli match:
            name, val = match.group(1, 2)
            val = int(val)
            tokens[val] = name          # reverse so we can sort them...
    keys = sorted(tokens.keys())
    # load the output skeleton z the target:
    spróbuj:
        fp = open(outFileName)
    wyjąwszy OSError jako err:
        sys.stderr.write("I/O error: %s\n" % str(err))
        sys.exit(2)
    przy fp:
        format = fp.read().split("\n")
    spróbuj:
        start = format.index("#--start constants--") + 1
        end = format.index("#--end constants--")
    wyjąwszy ValueError:
        sys.stderr.write("target does nie contain format markers")
        sys.exit(3)
    lines = []
    dla val w keys:
        lines.append("%s = %d" % (tokens[val], val))
    format[start:end] = lines
    spróbuj:
        fp = open(outFileName, 'w')
    wyjąwszy OSError jako err:
        sys.stderr.write("I/O error: %s\n" % str(err))
        sys.exit(4)
    przy fp:
        fp.write("\n".join(format))


jeżeli __name__ == "__main__":
    _main()
