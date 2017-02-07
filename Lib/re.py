#
# Secret Labs' Regular Expression Engine
#
# re-compatible interface dla the sre matching engine
#
# Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
#
# This version of the SRE library can be redistributed under CNRI's
# Python 1.6 license.  For any other use, please contact Secret Labs
# AB (info@pythonware.com).
#
# Portions of this engine have been developed w cooperation with
# CNRI.  Hewlett-Packard provided funding dla 1.6 integration oraz
# other compatibility work.
#

r"""Support dla regular expressions (RE).

This module provides regular expression matching operations similar to
those found w Perl.  It supports both 8-bit oraz Unicode strings; both
the pattern oraz the strings being processed can contain null bytes oraz
characters outside the US ASCII range.

Regular expressions can contain both special oraz ordinary characters.
Most ordinary characters, like "A", "a", albo "0", are the simplest
regular expressions; they simply match themselves.  You can
concatenate ordinary characters, so last matches the string 'last'.

The special characters are:
    "."      Matches any character wyjąwszy a newline.
    "^"      Matches the start of the string.
    "$"      Matches the end of the string albo just before the newline at
             the end of the string.
    "*"      Matches 0 albo more (greedy) repetitions of the preceding RE.
             Greedy means that it will match jako many repetitions jako possible.
    "+"      Matches 1 albo more (greedy) repetitions of the preceding RE.
    "?"      Matches 0 albo 1 (greedy) of the preceding RE.
    *?,+?,?? Non-greedy versions of the previous three special characters.
    {m,n}    Matches z m to n repetitions of the preceding RE.
    {m,n}?   Non-greedy version of the above.
    "\\"     Either escapes special characters albo signals a special sequence.
    []       Indicates a set of characters.
             A "^" jako the first character indicates a complementing set.
    "|"      A|B, creates an RE that will match either A albo B.
    (...)    Matches the RE inside the parentheses.
             The contents can be retrieved albo matched later w the string.
    (?aiLmsux) Set the A, I, L, M, S, U, albo X flag dla the RE (see below).
    (?:...)  Non-grouping version of regular parentheses.
    (?P<name>...) The substring matched by the group jest accessible by name.
    (?P=name)     Matches the text matched earlier by the group named name.
    (?#...)  A comment; ignored.
    (?=...)  Matches jeżeli ... matches next, but doesn't consume the string.
    (?!...)  Matches jeżeli ... doesn't match next.
    (?<=...) Matches jeżeli preceded by ... (must be fixed length).
    (?<!...) Matches jeżeli nie preceded by ... (must be fixed length).
    (?(id/name)yes|no) Matches yes pattern jeżeli the group przy id/name matched,
                       the (optional) no pattern otherwise.

The special sequences consist of "\\" oraz a character z the list
below.  If the ordinary character jest nie on the list, then the
resulting RE will match the second character.
    \number  Matches the contents of the group of the same number.
    \A       Matches only at the start of the string.
    \Z       Matches only at the end of the string.
    \b       Matches the empty string, but only at the start albo end of a word.
    \B       Matches the empty string, but nie at the start albo end of a word.
    \d       Matches any decimal digit; equivalent to the set [0-9] w
             bytes patterns albo string patterns przy the ASCII flag.
             In string patterns without the ASCII flag, it will match the whole
             range of Unicode digits.
    \D       Matches any non-digit character; equivalent to [^\d].
    \s       Matches any whitespace character; equivalent to [ \t\n\r\f\v] w
             bytes patterns albo string patterns przy the ASCII flag.
             In string patterns without the ASCII flag, it will match the whole
             range of Unicode whitespace characters.
    \S       Matches any non-whitespace character; equivalent to [^\s].
    \w       Matches any alphanumeric character; equivalent to [a-zA-Z0-9_]
             w bytes patterns albo string patterns przy the ASCII flag.
             In string patterns without the ASCII flag, it will match the
             range of Unicode alphanumeric characters (letters plus digits
             plus underscore).
             With LOCALE, it will match the set [0-9_] plus characters defined
             jako letters dla the current locale.
    \W       Matches the complement of \w.
    \\       Matches a literal backslash.

This module exports the following functions:
    match     Match a regular expression pattern to the beginning of a string.
    fullmatch Match a regular expression pattern to all of a string.
    search    Search a string dla the presence of a pattern.
    sub       Substitute occurrences of a pattern found w a string.
    subn      Same jako sub, but also zwróć the number of substitutions made.
    split     Split a string by the occurrences of a pattern.
    findall   Find all occurrences of a pattern w a string.
    finditer  Return an iterator uzyskajing a match object dla each match.
    compile   Compile a pattern into a RegexObject.
    purge     Clear the regular expression cache.
    escape    Backslash all non-alphanumerics w a string.

Some of the functions w this module takes flags jako optional parameters:
    A  ASCII       For string patterns, make \w, \W, \b, \B, \d, \D
                   match the corresponding ASCII character categories
                   (rather than the whole Unicode categories, which jest the
                   default).
                   For bytes patterns, this flag jest the only available
                   behaviour oraz needn't be specified.
    I  IGNORECASE  Perform case-insensitive matching.
    L  LOCALE      Make \w, \W, \b, \B, dependent on the current locale.
    M  MULTILINE   "^" matches the beginning of lines (after a newline)
                   jako well jako the string.
                   "$" matches the end of lines (before a newline) jako well
                   jako the end of the string.
    S  DOTALL      "." matches any character at all, including the newline.
    X  VERBOSE     Ignore whitespace oraz comments dla nicer looking RE's.
    U  UNICODE     For compatibility only. Ignored dla string patterns (it
                   jest the default), oraz forbidden dla bytes patterns.

This module also defines an exception 'error'.

"""

zaimportuj sys
zaimportuj sre_compile
zaimportuj sre_parse
spróbuj:
    zaimportuj _locale
wyjąwszy ImportError:
    _locale = Nic

# public symbols
__all__ = [
    "match", "fullmatch", "search", "sub", "subn", "split",
    "findall", "finditer", "compile", "purge", "template", "escape",
    "error", "A", "I", "L", "M", "S", "X", "U",
    "ASCII", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE",
    "UNICODE",
]

__version__ = "2.2.1"

# flags
A = ASCII = sre_compile.SRE_FLAG_ASCII # assume ascii "locale"
I = IGNORECASE = sre_compile.SRE_FLAG_IGNORECASE # ignore case
L = LOCALE = sre_compile.SRE_FLAG_LOCALE # assume current 8-bit locale
U = UNICODE = sre_compile.SRE_FLAG_UNICODE # assume unicode "locale"
M = MULTILINE = sre_compile.SRE_FLAG_MULTILINE # make anchors look dla newline
S = DOTALL = sre_compile.SRE_FLAG_DOTALL # make dot match newline
X = VERBOSE = sre_compile.SRE_FLAG_VERBOSE # ignore whitespace oraz comments

# sre extensions (experimental, don't rely on these)
T = TEMPLATE = sre_compile.SRE_FLAG_TEMPLATE # disable backtracking
DEBUG = sre_compile.SRE_FLAG_DEBUG # dump pattern after compilation

# sre exception
error = sre_compile.error

# --------------------------------------------------------------------
# public interface

def match(pattern, string, flags=0):
    """Try to apply the pattern at the start of the string, returning
    a match object, albo Nic jeżeli no match was found."""
    zwróć _compile(pattern, flags).match(string)

def fullmatch(pattern, string, flags=0):
    """Try to apply the pattern to all of the string, returning
    a match object, albo Nic jeżeli no match was found."""
    zwróć _compile(pattern, flags).fullmatch(string)

def search(pattern, string, flags=0):
    """Scan through string looking dla a match to the pattern, returning
    a match object, albo Nic jeżeli no match was found."""
    zwróć _compile(pattern, flags).search(string)

def sub(pattern, repl, string, count=0, flags=0):
    """Return the string obtained by replacing the leftmost
    non-overlapping occurrences of the pattern w string by the
    replacement repl.  repl can be either a string albo a callable;
    jeżeli a string, backslash escapes w it are processed.  If it jest
    a callable, it's dalejed the match object oraz must zwróć
    a replacement string to be used."""
    zwróć _compile(pattern, flags).sub(repl, string, count)

def subn(pattern, repl, string, count=0, flags=0):
    """Return a 2-tuple containing (new_string, number).
    new_string jest the string obtained by replacing the leftmost
    non-overlapping occurrences of the pattern w the source
    string by the replacement repl.  number jest the number of
    substitutions that were made. repl can be either a string albo a
    callable; jeżeli a string, backslash escapes w it are processed.
    If it jest a callable, it's dalejed the match object oraz must
    zwróć a replacement string to be used."""
    zwróć _compile(pattern, flags).subn(repl, string, count)

def split(pattern, string, maxsplit=0, flags=0):
    """Split the source string by the occurrences of the pattern,
    returning a list containing the resulting substrings.  If
    capturing parentheses are used w pattern, then the text of all
    groups w the pattern are also returned jako part of the resulting
    list.  If maxsplit jest nonzero, at most maxsplit splits occur,
    oraz the remainder of the string jest returned jako the final element
    of the list."""
    zwróć _compile(pattern, flags).split(string, maxsplit)

def findall(pattern, string, flags=0):
    """Return a list of all non-overlapping matches w the string.

    If one albo more capturing groups are present w the pattern, zwróć
    a list of groups; this will be a list of tuples jeżeli the pattern
    has more than one group.

    Empty matches are included w the result."""
    zwróć _compile(pattern, flags).findall(string)

def finditer(pattern, string, flags=0):
    """Return an iterator over all non-overlapping matches w the
    string.  For each match, the iterator returns a match object.

    Empty matches are included w the result."""
    zwróć _compile(pattern, flags).finditer(string)

def compile(pattern, flags=0):
    "Compile a regular expression pattern, returning a pattern object."
    zwróć _compile(pattern, flags)

def purge():
    "Clear the regular expression caches"
    _cache.clear()
    _cache_repl.clear()

def template(pattern, flags=0):
    "Compile a template pattern, returning a pattern object"
    zwróć _compile(pattern, flags|T)

_alphanum_str = frozenset(
    "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890")
_alphanum_bytes = frozenset(
    b"_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890")

def escape(pattern):
    """
    Escape all the characters w pattern wyjąwszy ASCII letters, numbers oraz '_'.
    """
    jeżeli isinstance(pattern, str):
        alphanum = _alphanum_str
        s = list(pattern)
        dla i, c w enumerate(pattern):
            jeżeli c nie w alphanum:
                jeżeli c == "\000":
                    s[i] = "\\000"
                inaczej:
                    s[i] = "\\" + c
        zwróć "".join(s)
    inaczej:
        alphanum = _alphanum_bytes
        s = []
        esc = ord(b"\\")
        dla c w pattern:
            jeżeli c w alphanum:
                s.append(c)
            inaczej:
                jeżeli c == 0:
                    s.extend(b"\\000")
                inaczej:
                    s.append(esc)
                    s.append(c)
        zwróć bytes(s)

# --------------------------------------------------------------------
# internals

_cache = {}
_cache_repl = {}

_pattern_type = type(sre_compile.compile("", 0))

_MAXCACHE = 512
def _compile(pattern, flags):
    # internal: compile pattern
    spróbuj:
        p, loc = _cache[type(pattern), pattern, flags]
        jeżeli loc jest Nic albo loc == _locale.setlocale(_locale.LC_CTYPE):
            zwróć p
    wyjąwszy KeyError:
        dalej
    jeżeli isinstance(pattern, _pattern_type):
        jeżeli flags:
            podnieś ValueError(
                "cannot process flags argument przy a compiled pattern")
        zwróć pattern
    jeżeli nie sre_compile.isstring(pattern):
        podnieś TypeError("first argument must be string albo compiled pattern")
    p = sre_compile.compile(pattern, flags)
    jeżeli nie (flags & DEBUG):
        jeżeli len(_cache) >= _MAXCACHE:
            _cache.clear()
        jeżeli p.flags & LOCALE:
            jeżeli nie _locale:
                zwróć p
            loc = _locale.setlocale(_locale.LC_CTYPE)
        inaczej:
            loc = Nic
        _cache[type(pattern), pattern, flags] = p, loc
    zwróć p

def _compile_repl(repl, pattern):
    # internal: compile replacement pattern
    spróbuj:
        zwróć _cache_repl[repl, pattern]
    wyjąwszy KeyError:
        dalej
    p = sre_parse.parse_template(repl, pattern)
    jeżeli len(_cache_repl) >= _MAXCACHE:
        _cache_repl.clear()
    _cache_repl[repl, pattern] = p
    zwróć p

def _expand(pattern, match, template):
    # internal: match.expand implementation hook
    template = sre_parse.parse_template(template, pattern)
    zwróć sre_parse.expand_template(template, match)

def _subx(pattern, template):
    # internal: pattern.sub/subn implementation helper
    template = _compile_repl(template, pattern)
    jeżeli nie template[0] oraz len(template[1]) == 1:
        # literal replacement
        zwróć template[1][0]
    def filter(match, template=template):
        zwróć sre_parse.expand_template(template, match)
    zwróć filter

# register myself dla pickling

zaimportuj copyreg

def _pickle(p):
    zwróć _compile, (p.pattern, p.flags)

copyreg.pickle(_pattern_type, _pickle, _compile)

# --------------------------------------------------------------------
# experimental stuff (see python-dev discussions dla details)

klasa Scanner:
    def __init__(self, lexicon, flags=0):
        z sre_constants zaimportuj BRANCH, SUBPATTERN
        self.lexicon = lexicon
        # combine phrases into a compound pattern
        p = []
        s = sre_parse.Pattern()
        s.flags = flags
        dla phrase, action w lexicon:
            gid = s.opengroup()
            p.append(sre_parse.SubPattern(s, [
                (SUBPATTERN, (gid, sre_parse.parse(phrase, flags))),
                ]))
            s.closegroup(gid, p[-1])
        p = sre_parse.SubPattern(s, [(BRANCH, (Nic, p))])
        self.scanner = sre_compile.compile(p)
    def scan(self, string):
        result = []
        append = result.append
        match = self.scanner.scanner(string).match
        i = 0
        dopóki Prawda:
            m = match()
            jeżeli nie m:
                przerwij
            j = m.end()
            jeżeli i == j:
                przerwij
            action = self.lexicon[m.lastindex-1][1]
            jeżeli callable(action):
                self.match = m
                action = action(self, m.group())
            jeżeli action jest nie Nic:
                append(action)
            i = j
        zwróć result, string[i:]
