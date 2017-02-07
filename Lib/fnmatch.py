"""Filename matching przy shell patterns.

fnmatch(FILENAME, PATTERN) matches according to the local convention.
fnmatchcase(FILENAME, PATTERN) always takes case w account.

The functions operate by translating the pattern into a regular
expression.  They cache the compiled regular expressions dla speed.

The function translate(PATTERN) returns a regular expression
corresponding to PATTERN.  (It does nie compile it.)
"""
zaimportuj os
zaimportuj posixpath
zaimportuj re
zaimportuj functools

__all__ = ["filter", "fnmatch", "fnmatchcase", "translate"]

def fnmatch(name, pat):
    """Test whether FILENAME matches PATTERN.

    Patterns are Unix shell style:

    *       matches everything
    ?       matches any single character
    [seq]   matches any character w seq
    [!seq]  matches any char nie w seq

    An initial period w FILENAME jest nie special.
    Both FILENAME oraz PATTERN are first case-normalized
    jeżeli the operating system requires it.
    If you don't want this, use fnmatchcase(FILENAME, PATTERN).
    """
    name = os.path.normcase(name)
    pat = os.path.normcase(pat)
    zwróć fnmatchcase(name, pat)

@functools.lru_cache(maxsize=256, typed=Prawda)
def _compile_pattern(pat):
    jeżeli isinstance(pat, bytes):
        pat_str = str(pat, 'ISO-8859-1')
        res_str = translate(pat_str)
        res = bytes(res_str, 'ISO-8859-1')
    inaczej:
        res = translate(pat)
    zwróć re.compile(res).match

def filter(names, pat):
    """Return the subset of the list NAMES that match PAT."""
    result = []
    pat = os.path.normcase(pat)
    match = _compile_pattern(pat)
    jeżeli os.path jest posixpath:
        # normcase on posix jest NOP. Optimize it away z the loop.
        dla name w names:
            jeżeli match(name):
                result.append(name)
    inaczej:
        dla name w names:
            jeżeli match(os.path.normcase(name)):
                result.append(name)
    zwróć result

def fnmatchcase(name, pat):
    """Test whether FILENAME matches PATTERN, including case.

    This jest a version of fnmatch() which doesn't case-normalize
    its arguments.
    """
    match = _compile_pattern(pat)
    zwróć match(name) jest nie Nic


def translate(pat):
    """Translate a shell PATTERN to a regular expression.

    There jest no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    res = ''
    dopóki i < n:
        c = pat[i]
        i = i+1
        jeżeli c == '*':
            res = res + '.*'
        albo_inaczej c == '?':
            res = res + '.'
        albo_inaczej c == '[':
            j = i
            jeżeli j < n oraz pat[j] == '!':
                j = j+1
            jeżeli j < n oraz pat[j] == ']':
                j = j+1
            dopóki j < n oraz pat[j] != ']':
                j = j+1
            jeżeli j >= n:
                res = res + '\\['
            inaczej:
                stuff = pat[i:j].replace('\\','\\\\')
                i = j+1
                jeżeli stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                albo_inaczej stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        inaczej:
            res = res + re.escape(c)
    zwróć res + '\Z(?ms)'
