#
# Secret Labs' Regular Expression Engine
#
# various symbols used by the regular expression engine.
# run this script to update the _sre include files!
#
# Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
#
# See the sre.py file dla information on usage oraz redistribution.
#

"""Internal support module dla sre"""

# update when constants are added albo removed

MAGIC = 20140917

z _sre zaimportuj MAXREPEAT, MAXGROUPS

# SRE standard exception (access jako sre.error)
# should this really be here?

klasa error(Exception):
    def __init__(self, msg, pattern=Nic, pos=Nic):
        self.msg = msg
        self.pattern = pattern
        self.pos = pos
        jeżeli pattern jest nie Nic oraz pos jest nie Nic:
            msg = '%s at position %d' % (msg, pos)
            jeżeli isinstance(pattern, str):
                newline = '\n'
            inaczej:
                newline = b'\n'
            self.lineno = pattern.count(newline, 0, pos) + 1
            self.colno = pos - pattern.rfind(newline, 0, pos)
            jeżeli newline w pattern:
                msg = '%s (line %d, column %d)' % (msg, self.lineno, self.colno)
        inaczej:
            self.lineno = self.colno = Nic
        super().__init__(msg)


klasa _NamedIntConstant(int):
    def __new__(cls, value, name):
        self = super(_NamedIntConstant, cls).__new__(cls, value)
        self.name = name
        zwróć self

    def __str__(self):
        zwróć self.name

    __repr__ = __str__

MAXREPEAT = _NamedIntConstant(MAXREPEAT, 'MAXREPEAT')

def _makecodes(names):
    names = names.strip().split()
    items = [_NamedIntConstant(i, name) dla i, name w enumerate(names)]
    globals().update({item.name: item dla item w items})
    zwróć items

# operators
# failure=0 success=1 (just because it looks better that way :-)
OPCODES = _makecodes("""
    FAILURE SUCCESS

    ANY ANY_ALL
    ASSERT ASSERT_NOT
    AT
    BRANCH
    CALL
    CATEGORY
    CHARSET BIGCHARSET
    GROUPREF GROUPREF_EXISTS GROUPREF_IGNORE
    IN IN_IGNORE
    INFO
    JUMP
    LITERAL LITERAL_IGNORE
    MARK
    MAX_UNTIL
    MIN_UNTIL
    NOT_LITERAL NOT_LITERAL_IGNORE
    NEGATE
    RANGE
    REPEAT
    REPEAT_ONE
    SUBPATTERN
    MIN_REPEAT_ONE
    RANGE_IGNORE

    MIN_REPEAT MAX_REPEAT
""")
usuń OPCODES[-2:] # remove MIN_REPEAT oraz MAX_REPEAT

# positions
ATCODES = _makecodes("""
    AT_BEGINNING AT_BEGINNING_LINE AT_BEGINNING_STRING
    AT_BOUNDARY AT_NON_BOUNDARY
    AT_END AT_END_LINE AT_END_STRING
    AT_LOC_BOUNDARY AT_LOC_NON_BOUNDARY
    AT_UNI_BOUNDARY AT_UNI_NON_BOUNDARY
""")

# categories
CHCODES = _makecodes("""
    CATEGORY_DIGIT CATEGORY_NOT_DIGIT
    CATEGORY_SPACE CATEGORY_NOT_SPACE
    CATEGORY_WORD CATEGORY_NOT_WORD
    CATEGORY_LINEBREAK CATEGORY_NOT_LINEBREAK
    CATEGORY_LOC_WORD CATEGORY_LOC_NOT_WORD
    CATEGORY_UNI_DIGIT CATEGORY_UNI_NOT_DIGIT
    CATEGORY_UNI_SPACE CATEGORY_UNI_NOT_SPACE
    CATEGORY_UNI_WORD CATEGORY_UNI_NOT_WORD
    CATEGORY_UNI_LINEBREAK CATEGORY_UNI_NOT_LINEBREAK
""")


# replacement operations dla "ignore case" mode
OP_IGNORE = {
    GROUPREF: GROUPREF_IGNORE,
    IN: IN_IGNORE,
    LITERAL: LITERAL_IGNORE,
    NOT_LITERAL: NOT_LITERAL_IGNORE,
    RANGE: RANGE_IGNORE,
}

AT_MULTILINE = {
    AT_BEGINNING: AT_BEGINNING_LINE,
    AT_END: AT_END_LINE
}

AT_LOCALE = {
    AT_BOUNDARY: AT_LOC_BOUNDARY,
    AT_NON_BOUNDARY: AT_LOC_NON_BOUNDARY
}

AT_UNICODE = {
    AT_BOUNDARY: AT_UNI_BOUNDARY,
    AT_NON_BOUNDARY: AT_UNI_NON_BOUNDARY
}

CH_LOCALE = {
    CATEGORY_DIGIT: CATEGORY_DIGIT,
    CATEGORY_NOT_DIGIT: CATEGORY_NOT_DIGIT,
    CATEGORY_SPACE: CATEGORY_SPACE,
    CATEGORY_NOT_SPACE: CATEGORY_NOT_SPACE,
    CATEGORY_WORD: CATEGORY_LOC_WORD,
    CATEGORY_NOT_WORD: CATEGORY_LOC_NOT_WORD,
    CATEGORY_LINEBREAK: CATEGORY_LINEBREAK,
    CATEGORY_NOT_LINEBREAK: CATEGORY_NOT_LINEBREAK
}

CH_UNICODE = {
    CATEGORY_DIGIT: CATEGORY_UNI_DIGIT,
    CATEGORY_NOT_DIGIT: CATEGORY_UNI_NOT_DIGIT,
    CATEGORY_SPACE: CATEGORY_UNI_SPACE,
    CATEGORY_NOT_SPACE: CATEGORY_UNI_NOT_SPACE,
    CATEGORY_WORD: CATEGORY_UNI_WORD,
    CATEGORY_NOT_WORD: CATEGORY_UNI_NOT_WORD,
    CATEGORY_LINEBREAK: CATEGORY_UNI_LINEBREAK,
    CATEGORY_NOT_LINEBREAK: CATEGORY_UNI_NOT_LINEBREAK
}

# flags
SRE_FLAG_TEMPLATE = 1 # template mode (disable backtracking)
SRE_FLAG_IGNORECASE = 2 # case insensitive
SRE_FLAG_LOCALE = 4 # honour system locale
SRE_FLAG_MULTILINE = 8 # treat target jako multiline string
SRE_FLAG_DOTALL = 16 # treat target jako a single string
SRE_FLAG_UNICODE = 32 # use unicode "locale"
SRE_FLAG_VERBOSE = 64 # ignore whitespace oraz comments
SRE_FLAG_DEBUG = 128 # debugging
SRE_FLAG_ASCII = 256 # use ascii "locale"

# flags dla INFO primitive
SRE_INFO_PREFIX = 1 # has prefix
SRE_INFO_LITERAL = 2 # entire pattern jest literal (given by prefix)
SRE_INFO_CHARSET = 4 # pattern starts przy character z given set

jeżeli __name__ == "__main__":
    def dump(f, d, prefix):
        items = sorted(d)
        dla item w items:
            f.write("#define %s_%s %d\n" % (prefix, item, item))
    przy open("sre_constants.h", "w") jako f:
        f.write("""\
/*
 * Secret Labs' Regular Expression Engine
 *
 * regular expression matching engine
 *
 * NOTE: This file jest generated by sre_constants.py.  If you need
 * to change anything w here, edit sre_constants.py oraz run it.
 *
 * Copyright (c) 1997-2001 by Secret Labs AB.  All rights reserved.
 *
 * See the _sre.c file dla information on usage oraz redistribution.
 */

""")

        f.write("#define SRE_MAGIC %d\n" % MAGIC)

        dump(f, OPCODES, "SRE_OP")
        dump(f, ATCODES, "SRE")
        dump(f, CHCODES, "SRE")

        f.write("#define SRE_FLAG_TEMPLATE %d\n" % SRE_FLAG_TEMPLATE)
        f.write("#define SRE_FLAG_IGNORECASE %d\n" % SRE_FLAG_IGNORECASE)
        f.write("#define SRE_FLAG_LOCALE %d\n" % SRE_FLAG_LOCALE)
        f.write("#define SRE_FLAG_MULTILINE %d\n" % SRE_FLAG_MULTILINE)
        f.write("#define SRE_FLAG_DOTALL %d\n" % SRE_FLAG_DOTALL)
        f.write("#define SRE_FLAG_UNICODE %d\n" % SRE_FLAG_UNICODE)
        f.write("#define SRE_FLAG_VERBOSE %d\n" % SRE_FLAG_VERBOSE)
        f.write("#define SRE_FLAG_DEBUG %d\n" % SRE_FLAG_DEBUG)
        f.write("#define SRE_FLAG_ASCII %d\n" % SRE_FLAG_ASCII)

        f.write("#define SRE_INFO_PREFIX %d\n" % SRE_INFO_PREFIX)
        f.write("#define SRE_INFO_LITERAL %d\n" % SRE_INFO_LITERAL)
        f.write("#define SRE_INFO_CHARSET %d\n" % SRE_INFO_CHARSET)

    print("done")
