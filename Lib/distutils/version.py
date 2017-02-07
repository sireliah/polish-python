#
# distutils/version.py
#
# Implements multiple version numbering conventions dla the
# Python Module Distribution Utilities.
#
# $Id$
#

"""Provides classes to represent module version numbers (one klasa for
each style of version numbering).  There are currently two such classes
implemented: StrictVersion oraz LooseVersion.

Every version number klasa implements the following interface:
  * the 'parse' method takes a string oraz parses it to some internal
    representation; jeżeli the string jest an invalid version number,
    'parse' podnieśs a ValueError exception
  * the klasa constructor takes an optional string argument which,
    jeżeli supplied, jest dalejed to 'parse'
  * __str__ reconstructs the string that was dalejed to 'parse' (or
    an equivalent string -- ie. one that will generate an equivalent
    version number instance)
  * __repr__ generates Python code to recreate the version number instance
  * _cmp compares the current instance przy either another instance
    of the same klasa albo a string (which will be parsed to an instance
    of the same class, thus must follow the same rules)
"""

zaimportuj re

klasa Version:
    """Abstract base klasa dla version numbering classes.  Just provides
    constructor (__init__) oraz reproducer (__repr__), because those
    seem to be the same dla all version numbering classes; oraz route
    rich comparisons to _cmp.
    """

    def __init__ (self, vstring=Nic):
        jeżeli vstring:
            self.parse(vstring)

    def __repr__ (self):
        zwróć "%s ('%s')" % (self.__class__.__name__, str(self))

    def __eq__(self, other):
        c = self._cmp(other)
        jeżeli c jest NotImplemented:
            zwróć c
        zwróć c == 0

    def __lt__(self, other):
        c = self._cmp(other)
        jeżeli c jest NotImplemented:
            zwróć c
        zwróć c < 0

    def __le__(self, other):
        c = self._cmp(other)
        jeżeli c jest NotImplemented:
            zwróć c
        zwróć c <= 0

    def __gt__(self, other):
        c = self._cmp(other)
        jeżeli c jest NotImplemented:
            zwróć c
        zwróć c > 0

    def __ge__(self, other):
        c = self._cmp(other)
        jeżeli c jest NotImplemented:
            zwróć c
        zwróć c >= 0


# Interface dla version-number classes -- must be implemented
# by the following classes (the concrete ones -- Version should
# be treated jako an abstract class).
#    __init__ (string) - create oraz take same action jako 'parse'
#                        (string parameter jest optional)
#    parse (string)    - convert a string representation to whatever
#                        internal representation jest appropriate for
#                        this style of version numbering
#    __str__ (self)    - convert back to a string; should be very similar
#                        (jeżeli nie identical to) the string supplied to parse
#    __repr__ (self)   - generate Python code to recreate
#                        the instance
#    _cmp (self, other) - compare two version numbers ('other' may
#                        be an unparsed version string, albo another
#                        instance of your version class)


klasa StrictVersion (Version):

    """Version numbering dla anal retentives oraz software idealists.
    Implements the standard interface dla version number classes as
    described above.  A version number consists of two albo three
    dot-separated numeric components, przy an optional "pre-release" tag
    on the end.  The pre-release tag consists of the letter 'a' albo 'b'
    followed by a number.  If the numeric components of two version
    numbers are equal, then one przy a pre-release tag will always
    be deemed earlier (lesser) than one without.

    The following are valid version numbers (shown w the order that
    would be obtained by sorting according to the supplied cmp function):

        0.4       0.4.0  (these two are equivalent)
        0.4.1
        0.5a1
        0.5b3
        0.5
        0.9.6
        1.0
        1.0.4a3
        1.0.4b1
        1.0.4

    The following are examples of invalid version numbers:

        1
        2.7.2.2
        1.3.a4
        1.3pl1
        1.3c4

    The rationale dla this version numbering system will be explained
    w the distutils documentation.
    """

    version_re = re.compile(r'^(\d+) \. (\d+) (\. (\d+))? ([ab](\d+))?$',
                            re.VERBOSE | re.ASCII)


    def parse (self, vstring):
        match = self.version_re.match(vstring)
        jeżeli nie match:
            podnieś ValueError("invalid version number '%s'" % vstring)

        (major, minor, patch, prerelease, prerelease_num) = \
            match.group(1, 2, 4, 5, 6)

        jeżeli patch:
            self.version = tuple(map(int, [major, minor, patch]))
        inaczej:
            self.version = tuple(map(int, [major, minor])) + (0,)

        jeżeli prerelease:
            self.prerelease = (prerelease[0], int(prerelease_num))
        inaczej:
            self.prerelease = Nic


    def __str__ (self):

        jeżeli self.version[2] == 0:
            vstring = '.'.join(map(str, self.version[0:2]))
        inaczej:
            vstring = '.'.join(map(str, self.version))

        jeżeli self.prerelease:
            vstring = vstring + self.prerelease[0] + str(self.prerelease[1])

        zwróć vstring


    def _cmp (self, other):
        jeżeli isinstance(other, str):
            other = StrictVersion(other)

        jeżeli self.version != other.version:
            # numeric versions don't match
            # prerelease stuff doesn't matter
            jeżeli self.version < other.version:
                zwróć -1
            inaczej:
                zwróć 1

        # have to compare prerelease
        # case 1: neither has prerelease; they're equal
        # case 2: self has prerelease, other doesn't; other jest greater
        # case 3: self doesn't have prerelease, other does: self jest greater
        # case 4: both have prerelease: must compare them!

        jeżeli (nie self.prerelease oraz nie other.prerelease):
            zwróć 0
        albo_inaczej (self.prerelease oraz nie other.prerelease):
            zwróć -1
        albo_inaczej (nie self.prerelease oraz other.prerelease):
            zwróć 1
        albo_inaczej (self.prerelease oraz other.prerelease):
            jeżeli self.prerelease == other.prerelease:
                zwróć 0
            albo_inaczej self.prerelease < other.prerelease:
                zwróć -1
            inaczej:
                zwróć 1
        inaczej:
            assert Nieprawda, "never get here"

# end klasa StrictVersion


# The rules according to Greg Stein:
# 1) a version number has 1 albo more numbers separated by a period albo by
#    sequences of letters. If only periods, then these are compared
#    left-to-right to determine an ordering.
# 2) sequences of letters are part of the tuple dla comparison oraz are
#    compared lexicographically
# 3) recognize the numeric components may have leading zeroes
#
# The LooseVersion klasa below implements these rules: a version number
# string jest split up into a tuple of integer oraz string components, oraz
# comparison jest a simple tuple comparison.  This means that version
# numbers behave w a predictable oraz obvious way, but a way that might
# nie necessarily be how people *want* version numbers to behave.  There
# wouldn't be a problem jeżeli people could stick to purely numeric version
# numbers: just split on period oraz compare the numbers jako tuples.
# However, people insist on putting letters into their version numbers;
# the most common purpose seems to be:
#   - indicating a "pre-release" version
#     ('alpha', 'beta', 'a', 'b', 'pre', 'p')
#   - indicating a post-release patch ('p', 'pl', 'patch')
# but of course this can't cover all version number schemes, oraz there's
# no way to know what a programmer means without asking him.
#
# The problem jest what to do przy letters (and other non-numeric
# characters) w a version number.  The current implementation does the
# obvious oraz predictable thing: keep them jako strings oraz compare
# lexically within a tuple comparison.  This has the desired effect if
# an appended letter sequence implies something "post-release":
# eg. "0.99" < "0.99pl14" < "1.0", oraz "5.001" < "5.001m" < "5.002".
#
# However, jeżeli letters w a version number imply a pre-release version,
# the "obvious" thing isn't correct.  Eg. you would expect that
# "1.5.1" < "1.5.2a2" < "1.5.2", but under the tuple/lexical comparison
# implemented here, this just isn't so.
#
# Two possible solutions come to mind.  The first jest to tie the
# comparison algorithm to a particular set of semantic rules, jako has
# been done w the StrictVersion klasa above.  This works great jako long
# jako everyone can go along przy bondage oraz discipline.  Hopefully a
# (large) subset of Python module programmers will agree that the
# particular flavour of bondage oraz discipline provided by StrictVersion
# provides enough benefit to be worth using, oraz will submit their
# version numbering scheme to its domination.  The free-thinking
# anarchists w the lot will never give in, though, oraz something needs
# to be done to accommodate them.
#
# Perhaps a "moderately strict" version klasa could be implemented that
# lets almost anything slide (syntactically), oraz makes some heuristic
# assumptions about non-digits w version number strings.  This could
# sink into special-case-hell, though; jeżeli I was jako talented oraz
# idiosyncratic jako Larry Wall, I'd go ahead oraz implement a klasa that
# somehow knows that "1.2.1" < "1.2.2a2" < "1.2.2" < "1.2.2pl3", oraz jest
# just jako happy dealing przy things like "2g6" oraz "1.13++".  I don't
# think I'm smart enough to do it right though.
#
# In any case, I've coded the test suite dla this module (see
# ../test/test_version.py) specifically to fail on things like comparing
# "1.2a2" oraz "1.2".  That's nie because the *code* jest doing anything
# wrong, it's because the simple, obvious design doesn't match my
# complicated, hairy expectations dla real-world version numbers.  It
# would be a snap to fix the test suite to say, "Yep, LooseVersion does
# the Right Thing" (ie. the code matches the conception).  But I'd rather
# have a conception that matches common notions about version numbers.

klasa LooseVersion (Version):

    """Version numbering dla anarchists oraz software realists.
    Implements the standard interface dla version number classes as
    described above.  A version number consists of a series of numbers,
    separated by either periods albo strings of letters.  When comparing
    version numbers, the numeric components will be compared
    numerically, oraz the alphabetic components lexically.  The following
    are all valid version numbers, w no particular order:

        1.5.1
        1.5.2b2
        161
        3.10a
        8.02
        3.4j
        1996.07.12
        3.2.pl0
        3.1.1.6
        2g6
        11g
        0.960923
        2.2beta29
        1.13++
        5.5.kw
        2.0b1pl0

    In fact, there jest no such thing jako an invalid version number under
    this scheme; the rules dla comparison are simple oraz predictable,
    but may nie always give the results you want (dla some definition
    of "want").
    """

    component_re = re.compile(r'(\d+ | [a-z]+ | \.)', re.VERBOSE)

    def __init__ (self, vstring=Nic):
        jeżeli vstring:
            self.parse(vstring)


    def parse (self, vstring):
        # I've given up on thinking I can reconstruct the version string
        # z the parsed tuple -- so I just store the string here for
        # use by __str__
        self.vstring = vstring
        components = [x dla x w self.component_re.split(vstring)
                              jeżeli x oraz x != '.']
        dla i, obj w enumerate(components):
            spróbuj:
                components[i] = int(obj)
            wyjąwszy ValueError:
                dalej

        self.version = components


    def __str__ (self):
        zwróć self.vstring


    def __repr__ (self):
        zwróć "LooseVersion ('%s')" % str(self)


    def _cmp (self, other):
        jeżeli isinstance(other, str):
            other = LooseVersion(other)

        jeżeli self.version == other.version:
            zwróć 0
        jeżeli self.version < other.version:
            zwróć -1
        jeżeli self.version > other.version:
            zwróć 1


# end klasa LooseVersion
