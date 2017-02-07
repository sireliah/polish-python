#
# Secret Labs' Regular Expression Engine
#
# convert re-style regular expression to sre pattern
#
# Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
#
# See the sre.py file dla information on usage oraz redistribution.
#

"""Internal support module dla sre"""

# XXX: show string offset oraz offending character dla all errors

z sre_constants zaimportuj *

SPECIAL_CHARS = ".\\[{()*+?^$|"
REPEAT_CHARS = "*+?{"

DIGITS = frozenset("0123456789")

OCTDIGITS = frozenset("01234567")
HEXDIGITS = frozenset("0123456789abcdefABCDEF")
ASCIILETTERS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

WHITESPACE = frozenset(" \t\n\r\v\f")

_REPEATCODES = frozenset({MIN_REPEAT, MAX_REPEAT})
_UNITCODES = frozenset({ANY, RANGE, IN, LITERAL, NOT_LITERAL, CATEGORY})

ESCAPES = {
    r"\a": (LITERAL, ord("\a")),
    r"\b": (LITERAL, ord("\b")),
    r"\f": (LITERAL, ord("\f")),
    r"\n": (LITERAL, ord("\n")),
    r"\r": (LITERAL, ord("\r")),
    r"\t": (LITERAL, ord("\t")),
    r"\v": (LITERAL, ord("\v")),
    r"\\": (LITERAL, ord("\\"))
}

CATEGORIES = {
    r"\A": (AT, AT_BEGINNING_STRING), # start of string
    r"\b": (AT, AT_BOUNDARY),
    r"\B": (AT, AT_NON_BOUNDARY),
    r"\d": (IN, [(CATEGORY, CATEGORY_DIGIT)]),
    r"\D": (IN, [(CATEGORY, CATEGORY_NOT_DIGIT)]),
    r"\s": (IN, [(CATEGORY, CATEGORY_SPACE)]),
    r"\S": (IN, [(CATEGORY, CATEGORY_NOT_SPACE)]),
    r"\w": (IN, [(CATEGORY, CATEGORY_WORD)]),
    r"\W": (IN, [(CATEGORY, CATEGORY_NOT_WORD)]),
    r"\Z": (AT, AT_END_STRING), # end of string
}

FLAGS = {
    # standard flags
    "i": SRE_FLAG_IGNORECASE,
    "L": SRE_FLAG_LOCALE,
    "m": SRE_FLAG_MULTILINE,
    "s": SRE_FLAG_DOTALL,
    "x": SRE_FLAG_VERBOSE,
    # extensions
    "a": SRE_FLAG_ASCII,
    "t": SRE_FLAG_TEMPLATE,
    "u": SRE_FLAG_UNICODE,
}

klasa Pattern:
    # master pattern object.  keeps track of global attributes
    def __init__(self):
        self.flags = 0
        self.groupdict = {}
        self.subpatterns = [Nic]  # group 0
        self.lookbehindgroups = Nic
    @property
    def groups(self):
        zwróć len(self.subpatterns)
    def opengroup(self, name=Nic):
        gid = self.groups
        self.subpatterns.append(Nic)
        jeżeli self.groups > MAXGROUPS:
            podnieś error("too many groups")
        jeżeli name jest nie Nic:
            ogid = self.groupdict.get(name, Nic)
            jeżeli ogid jest nie Nic:
                podnieś error("redefinition of group name %r jako group %d; "
                            "was group %d" % (name, gid,  ogid))
            self.groupdict[name] = gid
        zwróć gid
    def closegroup(self, gid, p):
        self.subpatterns[gid] = p
    def checkgroup(self, gid):
        zwróć gid < self.groups oraz self.subpatterns[gid] jest nie Nic

    def checklookbehindgroup(self, gid, source):
        jeżeli self.lookbehindgroups jest nie Nic:
            jeżeli nie self.checkgroup(gid):
                podnieś source.error('cannot refer to an open group')
            jeżeli gid >= self.lookbehindgroups:
                podnieś source.error('cannot refer to group defined w the same '
                                   'lookbehind subpattern')

klasa SubPattern:
    # a subpattern, w intermediate form
    def __init__(self, pattern, data=Nic):
        self.pattern = pattern
        jeżeli data jest Nic:
            data = []
        self.data = data
        self.width = Nic
    def dump(self, level=0):
        nl = Prawda
        seqtypes = (tuple, list)
        dla op, av w self.data:
            print(level*"  " + str(op), end='')
            jeżeli op jest IN:
                # member sublanguage
                print()
                dla op, a w av:
                    print((level+1)*"  " + str(op), a)
            albo_inaczej op jest BRANCH:
                print()
                dla i, a w enumerate(av[1]):
                    jeżeli i:
                        print(level*"  " + "OR")
                    a.dump(level+1)
            albo_inaczej op jest GROUPREF_EXISTS:
                condgroup, item_yes, item_no = av
                print('', condgroup)
                item_yes.dump(level+1)
                jeżeli item_no:
                    print(level*"  " + "ELSE")
                    item_no.dump(level+1)
            albo_inaczej isinstance(av, seqtypes):
                nl = Nieprawda
                dla a w av:
                    jeżeli isinstance(a, SubPattern):
                        jeżeli nie nl:
                            print()
                        a.dump(level+1)
                        nl = Prawda
                    inaczej:
                        jeżeli nie nl:
                            print(' ', end='')
                        print(a, end='')
                        nl = Nieprawda
                jeżeli nie nl:
                    print()
            inaczej:
                print('', av)
    def __repr__(self):
        zwróć repr(self.data)
    def __len__(self):
        zwróć len(self.data)
    def __delitem__(self, index):
        usuń self.data[index]
    def __getitem__(self, index):
        jeżeli isinstance(index, slice):
            zwróć SubPattern(self.pattern, self.data[index])
        zwróć self.data[index]
    def __setitem__(self, index, code):
        self.data[index] = code
    def insert(self, index, code):
        self.data.insert(index, code)
    def append(self, code):
        self.data.append(code)
    def getwidth(self):
        # determine the width (min, max) dla this subpattern
        jeżeli self.width jest nie Nic:
            zwróć self.width
        lo = hi = 0
        dla op, av w self.data:
            jeżeli op jest BRANCH:
                i = MAXREPEAT - 1
                j = 0
                dla av w av[1]:
                    l, h = av.getwidth()
                    i = min(i, l)
                    j = max(j, h)
                lo = lo + i
                hi = hi + j
            albo_inaczej op jest CALL:
                i, j = av.getwidth()
                lo = lo + i
                hi = hi + j
            albo_inaczej op jest SUBPATTERN:
                i, j = av[1].getwidth()
                lo = lo + i
                hi = hi + j
            albo_inaczej op w _REPEATCODES:
                i, j = av[2].getwidth()
                lo = lo + i * av[0]
                hi = hi + j * av[1]
            albo_inaczej op w _UNITCODES:
                lo = lo + 1
                hi = hi + 1
            albo_inaczej op jest GROUPREF:
                i, j = self.pattern.subpatterns[av].getwidth()
                lo = lo + i
                hi = hi + j
            albo_inaczej op jest GROUPREF_EXISTS:
                i, j = av[1].getwidth()
                jeżeli av[2] jest nie Nic:
                    l, h = av[2].getwidth()
                    i = min(i, l)
                    j = max(j, h)
                inaczej:
                    i = 0
                lo = lo + i
                hi = hi + j
            albo_inaczej op jest SUCCESS:
                przerwij
        self.width = min(lo, MAXREPEAT - 1), min(hi, MAXREPEAT)
        zwróć self.width

klasa Tokenizer:
    def __init__(self, string):
        self.istext = isinstance(string, str)
        self.string = string
        jeżeli nie self.istext:
            string = str(string, 'latin1')
        self.decoded_string = string
        self.index = 0
        self.next = Nic
        self.__next()
    def __next(self):
        index = self.index
        spróbuj:
            char = self.decoded_string[index]
        wyjąwszy IndexError:
            self.next = Nic
            zwróć
        jeżeli char == "\\":
            index += 1
            spróbuj:
                char += self.decoded_string[index]
            wyjąwszy IndexError:
                podnieś error("bad escape (end of pattern)",
                            self.string, len(self.string) - 1) z Nic
        self.index = index + 1
        self.next = char
    def match(self, char):
        jeżeli char == self.next:
            self.__next()
            zwróć Prawda
        zwróć Nieprawda
    def get(self):
        this = self.next
        self.__next()
        zwróć this
    def getwhile(self, n, charset):
        result = ''
        dla _ w range(n):
            c = self.next
            jeżeli c nie w charset:
                przerwij
            result += c
            self.__next()
        zwróć result
    def getuntil(self, terminator):
        result = ''
        dopóki Prawda:
            c = self.next
            self.__next()
            jeżeli c jest Nic:
                jeżeli nie result:
                    podnieś self.error("missing group name")
                podnieś self.error("missing %s, unterminated name" % terminator,
                                 len(result))
            jeżeli c == terminator:
                jeżeli nie result:
                    podnieś self.error("missing group name", 1)
                przerwij
            result += c
        zwróć result
    def tell(self):
        zwróć self.index - len(self.next albo '')
    def seek(self, index):
        self.index = index
        self.__next()

    def error(self, msg, offset=0):
        zwróć error(msg, self.string, self.tell() - offset)

# The following three functions are nie used w this module anymore, but we keep
# them here (przy DeprecationWarnings) dla backwards compatibility.

def isident(char):
    zaimportuj warnings
    warnings.warn('sre_parse.isident() will be removed w 3.5',
                  DeprecationWarning, stacklevel=2)
    zwróć "a" <= char <= "z" albo "A" <= char <= "Z" albo char == "_"

def isdigit(char):
    zaimportuj warnings
    warnings.warn('sre_parse.isdigit() will be removed w 3.5',
                  DeprecationWarning, stacklevel=2)
    zwróć "0" <= char <= "9"

def isname(name):
    zaimportuj warnings
    warnings.warn('sre_parse.isname() will be removed w 3.5',
                  DeprecationWarning, stacklevel=2)
    # check that group name jest a valid string
    jeżeli nie isident(name[0]):
        zwróć Nieprawda
    dla char w name[1:]:
        jeżeli nie isident(char) oraz nie isdigit(char):
            zwróć Nieprawda
    zwróć Prawda

def _class_escape(source, escape):
    # handle escape code inside character class
    code = ESCAPES.get(escape)
    jeżeli code:
        zwróć code
    code = CATEGORIES.get(escape)
    jeżeli code oraz code[0] jest IN:
        zwróć code
    spróbuj:
        c = escape[1:2]
        jeżeli c == "x":
            # hexadecimal escape (exactly two digits)
            escape += source.getwhile(2, HEXDIGITS)
            jeżeli len(escape) != 4:
                podnieś source.error("incomplete escape %s" % escape, len(escape))
            zwróć LITERAL, int(escape[2:], 16)
        albo_inaczej c == "u" oraz source.istext:
            # unicode escape (exactly four digits)
            escape += source.getwhile(4, HEXDIGITS)
            jeżeli len(escape) != 6:
                podnieś source.error("incomplete escape %s" % escape, len(escape))
            zwróć LITERAL, int(escape[2:], 16)
        albo_inaczej c == "U" oraz source.istext:
            # unicode escape (exactly eight digits)
            escape += source.getwhile(8, HEXDIGITS)
            jeżeli len(escape) != 10:
                podnieś source.error("incomplete escape %s" % escape, len(escape))
            c = int(escape[2:], 16)
            chr(c) # podnieś ValueError dla invalid code
            zwróć LITERAL, c
        albo_inaczej c w OCTDIGITS:
            # octal escape (up to three digits)
            escape += source.getwhile(2, OCTDIGITS)
            c = int(escape[1:], 8)
            jeżeli c > 0o377:
                podnieś source.error('octal escape value %s outside of '
                                   'range 0-0o377' % escape, len(escape))
            zwróć LITERAL, c
        albo_inaczej c w DIGITS:
            podnieś ValueError
        jeżeli len(escape) == 2:
            jeżeli c w ASCIILETTERS:
                zaimportuj warnings
                warnings.warn('bad escape %s' % escape,
                              DeprecationWarning, stacklevel=8)
            zwróć LITERAL, ord(escape[1])
    wyjąwszy ValueError:
        dalej
    podnieś source.error("bad escape %s" % escape, len(escape))

def _escape(source, escape, state):
    # handle escape code w expression
    code = CATEGORIES.get(escape)
    jeżeli code:
        zwróć code
    code = ESCAPES.get(escape)
    jeżeli code:
        zwróć code
    spróbuj:
        c = escape[1:2]
        jeżeli c == "x":
            # hexadecimal escape
            escape += source.getwhile(2, HEXDIGITS)
            jeżeli len(escape) != 4:
                podnieś source.error("incomplete escape %s" % escape, len(escape))
            zwróć LITERAL, int(escape[2:], 16)
        albo_inaczej c == "u" oraz source.istext:
            # unicode escape (exactly four digits)
            escape += source.getwhile(4, HEXDIGITS)
            jeżeli len(escape) != 6:
                podnieś source.error("incomplete escape %s" % escape, len(escape))
            zwróć LITERAL, int(escape[2:], 16)
        albo_inaczej c == "U" oraz source.istext:
            # unicode escape (exactly eight digits)
            escape += source.getwhile(8, HEXDIGITS)
            jeżeli len(escape) != 10:
                podnieś source.error("incomplete escape %s" % escape, len(escape))
            c = int(escape[2:], 16)
            chr(c) # podnieś ValueError dla invalid code
            zwróć LITERAL, c
        albo_inaczej c == "0":
            # octal escape
            escape += source.getwhile(2, OCTDIGITS)
            zwróć LITERAL, int(escape[1:], 8)
        albo_inaczej c w DIGITS:
            # octal escape *or* decimal group reference (sigh)
            jeżeli source.next w DIGITS:
                escape += source.get()
                jeżeli (escape[1] w OCTDIGITS oraz escape[2] w OCTDIGITS oraz
                    source.next w OCTDIGITS):
                    # got three octal digits; this jest an octal escape
                    escape += source.get()
                    c = int(escape[1:], 8)
                    jeżeli c > 0o377:
                        podnieś source.error('octal escape value %s outside of '
                                           'range 0-0o377' % escape,
                                           len(escape))
                    zwróć LITERAL, c
            # nie an octal escape, so this jest a group reference
            group = int(escape[1:])
            jeżeli group < state.groups:
                jeżeli nie state.checkgroup(group):
                    podnieś source.error("cannot refer to an open group",
                                       len(escape))
                state.checklookbehindgroup(group, source)
                zwróć GROUPREF, group
            podnieś source.error("invalid group reference", len(escape))
        jeżeli len(escape) == 2:
            jeżeli c w ASCIILETTERS:
                zaimportuj warnings
                warnings.warn('bad escape %s' % escape,
                              DeprecationWarning, stacklevel=8)
            zwróć LITERAL, ord(escape[1])
    wyjąwszy ValueError:
        dalej
    podnieś source.error("bad escape %s" % escape, len(escape))

def _parse_sub(source, state, nested=Prawda):
    # parse an alternation: a|b|c

    items = []
    itemsappend = items.append
    sourcematch = source.match
    start = source.tell()
    dopóki Prawda:
        itemsappend(_parse(source, state))
        jeżeli nie sourcematch("|"):
            przerwij

    jeżeli len(items) == 1:
        zwróć items[0]

    subpattern = SubPattern(state)
    subpatternappend = subpattern.append

    # check jeżeli all items share a common prefix
    dopóki Prawda:
        prefix = Nic
        dla item w items:
            jeżeli nie item:
                przerwij
            jeżeli prefix jest Nic:
                prefix = item[0]
            albo_inaczej item[0] != prefix:
                przerwij
        inaczej:
            # all subitems start przy a common "prefix".
            # move it out of the branch
            dla item w items:
                usuń item[0]
            subpatternappend(prefix)
            continue # check next one
        przerwij

    # check jeżeli the branch can be replaced by a character set
    dla item w items:
        jeżeli len(item) != 1 albo item[0][0] jest nie LITERAL:
            przerwij
    inaczej:
        # we can store this jako a character set instead of a
        # branch (the compiler may optimize this even more)
        subpatternappend((IN, [item[0] dla item w items]))
        zwróć subpattern

    subpattern.append((BRANCH, (Nic, items)))
    zwróć subpattern

def _parse_sub_cond(source, state, condgroup):
    item_yes = _parse(source, state)
    jeżeli source.match("|"):
        item_no = _parse(source, state)
        jeżeli source.next == "|":
            podnieś source.error("conditional backref przy more than two branches")
    inaczej:
        item_no = Nic
    subpattern = SubPattern(state)
    subpattern.append((GROUPREF_EXISTS, (condgroup, item_yes, item_no)))
    zwróć subpattern

def _parse(source, state):
    # parse a simple pattern
    subpattern = SubPattern(state)

    # precompute constants into local variables
    subpatternappend = subpattern.append
    sourceget = source.get
    sourcematch = source.match
    _len = len
    _ord = ord
    verbose = state.flags & SRE_FLAG_VERBOSE

    dopóki Prawda:

        this = source.next
        jeżeli this jest Nic:
            przerwij # end of pattern
        jeżeli this w "|)":
            przerwij # end of subpattern
        sourceget()

        jeżeli verbose:
            # skip whitespace oraz comments
            jeżeli this w WHITESPACE:
                kontynuuj
            jeżeli this == "#":
                dopóki Prawda:
                    this = sourceget()
                    jeżeli this jest Nic albo this == "\n":
                        przerwij
                kontynuuj

        jeżeli this[0] == "\\":
            code = _escape(source, this, state)
            subpatternappend(code)

        albo_inaczej this nie w SPECIAL_CHARS:
            subpatternappend((LITERAL, _ord(this)))

        albo_inaczej this == "[":
            here = source.tell() - 1
            # character set
            set = []
            setappend = set.append
##          jeżeli sourcematch(":"):
##              dalej # handle character classes
            jeżeli sourcematch("^"):
                setappend((NEGATE, Nic))
            # check remaining characters
            start = set[:]
            dopóki Prawda:
                this = sourceget()
                jeżeli this jest Nic:
                    podnieś source.error("unterminated character set",
                                       source.tell() - here)
                jeżeli this == "]" oraz set != start:
                    przerwij
                albo_inaczej this[0] == "\\":
                    code1 = _class_escape(source, this)
                inaczej:
                    code1 = LITERAL, _ord(this)
                jeżeli sourcematch("-"):
                    # potential range
                    that = sourceget()
                    jeżeli that jest Nic:
                        podnieś source.error("unterminated character set",
                                           source.tell() - here)
                    jeżeli that == "]":
                        jeżeli code1[0] jest IN:
                            code1 = code1[1][0]
                        setappend(code1)
                        setappend((LITERAL, _ord("-")))
                        przerwij
                    jeżeli that[0] == "\\":
                        code2 = _class_escape(source, that)
                    inaczej:
                        code2 = LITERAL, _ord(that)
                    jeżeli code1[0] != LITERAL albo code2[0] != LITERAL:
                        msg = "bad character range %s-%s" % (this, that)
                        podnieś source.error(msg, len(this) + 1 + len(that))
                    lo = code1[1]
                    hi = code2[1]
                    jeżeli hi < lo:
                        msg = "bad character range %s-%s" % (this, that)
                        podnieś source.error(msg, len(this) + 1 + len(that))
                    setappend((RANGE, (lo, hi)))
                inaczej:
                    jeżeli code1[0] jest IN:
                        code1 = code1[1][0]
                    setappend(code1)

            # XXX: <fl> should move set optimization to compiler!
            jeżeli _len(set)==1 oraz set[0][0] jest LITERAL:
                subpatternappend(set[0]) # optimization
            albo_inaczej _len(set)==2 oraz set[0][0] jest NEGATE oraz set[1][0] jest LITERAL:
                subpatternappend((NOT_LITERAL, set[1][1])) # optimization
            inaczej:
                # XXX: <fl> should add charmap optimization here
                subpatternappend((IN, set))

        albo_inaczej this w REPEAT_CHARS:
            # repeat previous item
            here = source.tell()
            jeżeli this == "?":
                min, max = 0, 1
            albo_inaczej this == "*":
                min, max = 0, MAXREPEAT

            albo_inaczej this == "+":
                min, max = 1, MAXREPEAT
            albo_inaczej this == "{":
                jeżeli source.next == "}":
                    subpatternappend((LITERAL, _ord(this)))
                    kontynuuj
                min, max = 0, MAXREPEAT
                lo = hi = ""
                dopóki source.next w DIGITS:
                    lo += sourceget()
                jeżeli sourcematch(","):
                    dopóki source.next w DIGITS:
                        hi += sourceget()
                inaczej:
                    hi = lo
                jeżeli nie sourcematch("}"):
                    subpatternappend((LITERAL, _ord(this)))
                    source.seek(here)
                    kontynuuj
                jeżeli lo:
                    min = int(lo)
                    jeżeli min >= MAXREPEAT:
                        podnieś OverflowError("the repetition number jest too large")
                jeżeli hi:
                    max = int(hi)
                    jeżeli max >= MAXREPEAT:
                        podnieś OverflowError("the repetition number jest too large")
                    jeżeli max < min:
                        podnieś source.error("min repeat greater than max repeat",
                                           source.tell() - here)
            inaczej:
                podnieś AssertionError("unsupported quantifier %r" % (char,))
            # figure out which item to repeat
            jeżeli subpattern:
                item = subpattern[-1:]
            inaczej:
                item = Nic
            jeżeli nie item albo (_len(item) == 1 oraz item[0][0] jest AT):
                podnieś source.error("nothing to repeat",
                                   source.tell() - here + len(this))
            jeżeli item[0][0] w _REPEATCODES:
                podnieś source.error("multiple repeat",
                                   source.tell() - here + len(this))
            jeżeli sourcematch("?"):
                subpattern[-1] = (MIN_REPEAT, (min, max, item))
            inaczej:
                subpattern[-1] = (MAX_REPEAT, (min, max, item))

        albo_inaczej this == ".":
            subpatternappend((ANY, Nic))

        albo_inaczej this == "(":
            start = source.tell() - 1
            group = Prawda
            name = Nic
            condgroup = Nic
            jeżeli sourcematch("?"):
                # options
                char = sourceget()
                jeżeli char jest Nic:
                    podnieś source.error("unexpected end of pattern")
                jeżeli char == "P":
                    # python extensions
                    jeżeli sourcematch("<"):
                        # named group: skip forward to end of name
                        name = source.getuntil(">")
                        jeżeli nie name.isidentifier():
                            msg = "bad character w group name %r" % name
                            podnieś source.error(msg, len(name) + 1)
                    albo_inaczej sourcematch("="):
                        # named backreference
                        name = source.getuntil(")")
                        jeżeli nie name.isidentifier():
                            msg = "bad character w group name %r" % name
                            podnieś source.error(msg, len(name) + 1)
                        gid = state.groupdict.get(name)
                        jeżeli gid jest Nic:
                            msg = "unknown group name %r" % name
                            podnieś source.error(msg, len(name) + 1)
                        jeżeli nie state.checkgroup(gid):
                            podnieś source.error("cannot refer to an open group",
                                               len(name) + 1)
                        state.checklookbehindgroup(gid, source)
                        subpatternappend((GROUPREF, gid))
                        kontynuuj
                    inaczej:
                        char = sourceget()
                        jeżeli char jest Nic:
                            podnieś source.error("unexpected end of pattern")
                        podnieś source.error("unknown extension ?P" + char,
                                           len(char) + 2)
                albo_inaczej char == ":":
                    # non-capturing group
                    group = Nic
                albo_inaczej char == "#":
                    # comment
                    dopóki Prawda:
                        jeżeli source.next jest Nic:
                            podnieś source.error("missing ), unterminated comment",
                                               source.tell() - start)
                        jeżeli sourceget() == ")":
                            przerwij
                    kontynuuj
                albo_inaczej char w "=!<":
                    # lookahead assertions
                    dir = 1
                    jeżeli char == "<":
                        char = sourceget()
                        jeżeli char jest Nic:
                            podnieś source.error("unexpected end of pattern")
                        jeżeli char nie w "=!":
                            podnieś source.error("unknown extension ?<" + char,
                                               len(char) + 2)
                        dir = -1 # lookbehind
                        lookbehindgroups = state.lookbehindgroups
                        jeżeli lookbehindgroups jest Nic:
                            state.lookbehindgroups = state.groups
                    p = _parse_sub(source, state)
                    jeżeli dir < 0:
                        jeżeli lookbehindgroups jest Nic:
                            state.lookbehindgroups = Nic
                    jeżeli nie sourcematch(")"):
                        podnieś source.error("missing ), unterminated subpattern",
                                           source.tell() - start)
                    jeżeli char == "=":
                        subpatternappend((ASSERT, (dir, p)))
                    inaczej:
                        subpatternappend((ASSERT_NOT, (dir, p)))
                    kontynuuj
                albo_inaczej char == "(":
                    # conditional backreference group
                    condname = source.getuntil(")")
                    group = Nic
                    jeżeli condname.isidentifier():
                        condgroup = state.groupdict.get(condname)
                        jeżeli condgroup jest Nic:
                            msg = "unknown group name %r" % condname
                            podnieś source.error(msg, len(condname) + 1)
                    inaczej:
                        spróbuj:
                            condgroup = int(condname)
                            jeżeli condgroup < 0:
                                podnieś ValueError
                        wyjąwszy ValueError:
                            msg = "bad character w group name %r" % condname
                            podnieś source.error(msg, len(condname) + 1) z Nic
                        jeżeli nie condgroup:
                            podnieś source.error("bad group number",
                                               len(condname) + 1)
                        jeżeli condgroup >= MAXGROUPS:
                            podnieś source.error("invalid group reference",
                                               len(condname) + 1)
                    state.checklookbehindgroup(condgroup, source)
                albo_inaczej char w FLAGS:
                    # flags
                    dopóki Prawda:
                        state.flags |= FLAGS[char]
                        char = sourceget()
                        jeżeli char jest Nic:
                            podnieś source.error("missing )")
                        jeżeli char == ")":
                            przerwij
                        jeżeli char nie w FLAGS:
                            podnieś source.error("unknown flag", len(char))
                    verbose = state.flags & SRE_FLAG_VERBOSE
                    kontynuuj
                inaczej:
                    podnieś source.error("unknown extension ?" + char,
                                       len(char) + 1)

            # parse group contents
            jeżeli group jest nie Nic:
                spróbuj:
                    group = state.opengroup(name)
                wyjąwszy error jako err:
                    podnieś source.error(err.msg, len(name) + 1) z Nic
            jeżeli condgroup:
                p = _parse_sub_cond(source, state, condgroup)
            inaczej:
                p = _parse_sub(source, state)
            jeżeli nie source.match(")"):
                podnieś source.error("missing ), unterminated subpattern",
                                   source.tell() - start)
            jeżeli group jest nie Nic:
                state.closegroup(group, p)
            subpatternappend((SUBPATTERN, (group, p)))

        albo_inaczej this == "^":
            subpatternappend((AT, AT_BEGINNING))

        albo_inaczej this == "$":
            subpattern.append((AT, AT_END))

        inaczej:
            podnieś AssertionError("unsupported special character %r" % (char,))

    zwróć subpattern

def fix_flags(src, flags):
    # Check oraz fix flags according to the type of pattern (str albo bytes)
    jeżeli isinstance(src, str):
        jeżeli flags & SRE_FLAG_LOCALE:
            zaimportuj warnings
            warnings.warn("LOCALE flag przy a str pattern jest deprecated. "
                          "Will be an error w 3.6",
                          DeprecationWarning, stacklevel=6)
        jeżeli nie flags & SRE_FLAG_ASCII:
            flags |= SRE_FLAG_UNICODE
        albo_inaczej flags & SRE_FLAG_UNICODE:
            podnieś ValueError("ASCII oraz UNICODE flags are incompatible")
    inaczej:
        jeżeli flags & SRE_FLAG_UNICODE:
            podnieś ValueError("cannot use UNICODE flag przy a bytes pattern")
        jeżeli flags & SRE_FLAG_LOCALE oraz flags & SRE_FLAG_ASCII:
            zaimportuj warnings
            warnings.warn("ASCII oraz LOCALE flags are incompatible. "
                          "Will be an error w 3.6",
                          DeprecationWarning, stacklevel=6)
    zwróć flags

def parse(str, flags=0, pattern=Nic):
    # parse 're' pattern into list of (opcode, argument) tuples

    source = Tokenizer(str)

    jeżeli pattern jest Nic:
        pattern = Pattern()
    pattern.flags = flags
    pattern.str = str

    p = _parse_sub(source, pattern, 0)
    p.pattern.flags = fix_flags(str, p.pattern.flags)

    jeżeli source.next jest nie Nic:
        assert source.next == ")"
        podnieś source.error("unbalanced parenthesis")

    jeżeli flags & SRE_FLAG_DEBUG:
        p.dump()

    jeżeli nie (flags & SRE_FLAG_VERBOSE) oraz p.pattern.flags & SRE_FLAG_VERBOSE:
        # the VERBOSE flag was switched on inside the pattern.  to be
        # on the safe side, we'll parse the whole thing again...
        zwróć parse(str, p.pattern.flags)

    zwróć p

def parse_template(source, pattern):
    # parse 're' replacement string into list of literals oraz
    # group references
    s = Tokenizer(source)
    sget = s.get
    groups = []
    literals = []
    literal = []
    lappend = literal.append
    def addgroup(index):
        jeżeli literal:
            literals.append(''.join(literal))
            usuń literal[:]
        groups.append((len(literals), index))
        literals.append(Nic)
    groupindex = pattern.groupindex
    dopóki Prawda:
        this = sget()
        jeżeli this jest Nic:
            przerwij # end of replacement string
        jeżeli this[0] == "\\":
            # group
            c = this[1]
            jeżeli c == "g":
                name = ""
                jeżeli nie s.match("<"):
                    podnieś s.error("missing <")
                name = s.getuntil(">")
                jeżeli name.isidentifier():
                    spróbuj:
                        index = groupindex[name]
                    wyjąwszy KeyError:
                        podnieś IndexError("unknown group name %r" % name)
                inaczej:
                    spróbuj:
                        index = int(name)
                        jeżeli index < 0:
                            podnieś ValueError
                    wyjąwszy ValueError:
                        podnieś s.error("bad character w group name %r" % name,
                                      len(name) + 1) z Nic
                    jeżeli index >= MAXGROUPS:
                        podnieś s.error("invalid group reference",
                                      len(name) + 1)
                addgroup(index)
            albo_inaczej c == "0":
                jeżeli s.next w OCTDIGITS:
                    this += sget()
                    jeżeli s.next w OCTDIGITS:
                        this += sget()
                lappend(chr(int(this[1:], 8) & 0xff))
            albo_inaczej c w DIGITS:
                isoctal = Nieprawda
                jeżeli s.next w DIGITS:
                    this += sget()
                    jeżeli (c w OCTDIGITS oraz this[2] w OCTDIGITS oraz
                        s.next w OCTDIGITS):
                        this += sget()
                        isoctal = Prawda
                        c = int(this[1:], 8)
                        jeżeli c > 0o377:
                            podnieś s.error('octal escape value %s outside of '
                                          'range 0-0o377' % this, len(this))
                        lappend(chr(c))
                jeżeli nie isoctal:
                    addgroup(int(this[1:]))
            inaczej:
                spróbuj:
                    this = chr(ESCAPES[this][1])
                wyjąwszy KeyError:
                    jeżeli c w ASCIILETTERS:
                        zaimportuj warnings
                        warnings.warn('bad escape %s' % this,
                                      DeprecationWarning, stacklevel=4)
                lappend(this)
        inaczej:
            lappend(this)
    jeżeli literal:
        literals.append(''.join(literal))
    jeżeli nie isinstance(source, str):
        # The tokenizer implicitly decodes bytes objects jako latin-1, we must
        # therefore re-encode the final representation.
        literals = [Nic jeżeli s jest Nic inaczej s.encode('latin-1') dla s w literals]
    zwróć groups, literals

def expand_template(template, match):
    g = match.group
    empty = match.string[:0]
    groups, literals = template
    literals = literals[:]
    spróbuj:
        dla index, group w groups:
            literals[index] = g(group) albo empty
    wyjąwszy IndexError:
        podnieś error("invalid group reference")
    zwróć empty.join(literals)
