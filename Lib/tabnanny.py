#! /usr/bin/env python3

"""The Tab Nanny despises ambiguous indentation.  She knows no mercy.

tabnanny -- Detection of ambiguous indentation

For the time being this module jest intended to be called jako a script.
However it jest possible to zaimportuj it into an IDE oraz use the function
check() described below.

Warning: The API provided by this module jest likely to change w future
releases; such changes may nie be backward compatible.
"""

# Released to the public domain, by Tim Peters, 15 April 1998.

# XXX Note: this jest now a standard library module.
# XXX The API needs to undergo changes however; the current code jest too
# XXX script-like.  This will be addressed later.

__version__ = "6"

zaimportuj os
zaimportuj sys
zaimportuj getopt
zaimportuj tokenize
jeżeli nie hasattr(tokenize, 'NL'):
    podnieś ValueError("tokenize.NL doesn't exist -- tokenize module too old")

__all__ = ["check", "NannyNag", "process_tokens"]

verbose = 0
filename_only = 0

def errprint(*args):
    sep = ""
    dla arg w args:
        sys.stderr.write(sep + str(arg))
        sep = " "
    sys.stderr.write("\n")

def main():
    global verbose, filename_only
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], "qv")
    wyjąwszy getopt.error jako msg:
        errprint(msg)
        zwróć
    dla o, a w opts:
        jeżeli o == '-q':
            filename_only = filename_only + 1
        jeżeli o == '-v':
            verbose = verbose + 1
    jeżeli nie args:
        errprint("Usage:", sys.argv[0], "[-v] file_or_directory ...")
        zwróć
    dla arg w args:
        check(arg)

klasa NannyNag(Exception):
    """
    Raised by tokeneater() jeżeli detecting an ambiguous indent.
    Captured oraz handled w check().
    """
    def __init__(self, lineno, msg, line):
        self.lineno, self.msg, self.line = lineno, msg, line
    def get_lineno(self):
        zwróć self.lineno
    def get_msg(self):
        zwróć self.msg
    def get_line(self):
        zwróć self.line

def check(file):
    """check(file_or_dir)

    If file_or_dir jest a directory oraz nie a symbolic link, then recursively
    descend the directory tree named by file_or_dir, checking all .py files
    along the way. If file_or_dir jest an ordinary Python source file, it jest
    checked dla whitespace related problems. The diagnostic messages are
    written to standard output using the print statement.
    """

    jeżeli os.path.isdir(file) oraz nie os.path.islink(file):
        jeżeli verbose:
            print("%r: listing directory" % (file,))
        names = os.listdir(file)
        dla name w names:
            fullname = os.path.join(file, name)
            jeżeli (os.path.isdir(fullname) oraz
                nie os.path.islink(fullname) albo
                os.path.normcase(name[-3:]) == ".py"):
                check(fullname)
        zwróć

    spróbuj:
        f = tokenize.open(file)
    wyjąwszy OSError jako msg:
        errprint("%r: I/O Error: %s" % (file, msg))
        zwróć

    jeżeli verbose > 1:
        print("checking %r ..." % file)

    spróbuj:
        process_tokens(tokenize.generate_tokens(f.readline))

    wyjąwszy tokenize.TokenError jako msg:
        errprint("%r: Token Error: %s" % (file, msg))
        zwróć

    wyjąwszy IndentationError jako msg:
        errprint("%r: Indentation Error: %s" % (file, msg))
        zwróć

    wyjąwszy NannyNag jako nag:
        badline = nag.get_lineno()
        line = nag.get_line()
        jeżeli verbose:
            print("%r: *** Line %d: trouble w tab city! ***" % (file, badline))
            print("offending line: %r" % (line,))
            print(nag.get_msg())
        inaczej:
            jeżeli ' ' w file: file = '"' + file + '"'
            jeżeli filename_only: print(file)
            inaczej: print(file, badline, repr(line))
        zwróć

    w_końcu:
        f.close()

    jeżeli verbose:
        print("%r: Clean bill of health." % (file,))

klasa Whitespace:
    # the characters used dla space oraz tab
    S, T = ' \t'

    # members:
    #   raw
    #       the original string
    #   n
    #       the number of leading whitespace characters w raw
    #   nt
    #       the number of tabs w raw[:n]
    #   norm
    #       the normal form jako a pair (count, trailing), where:
    #       count
    #           a tuple such that raw[:n] contains count[i]
    #           instances of S * i + T
    #       trailing
    #           the number of trailing spaces w raw[:n]
    #       It's A Theorem that m.indent_level(t) ==
    #       n.indent_level(t) dla all t >= 1 iff m.norm == n.norm.
    #   is_simple
    #       true iff raw[:n] jest of the form (T*)(S*)

    def __init__(self, ws):
        self.raw  = ws
        S, T = Whitespace.S, Whitespace.T
        count = []
        b = n = nt = 0
        dla ch w self.raw:
            jeżeli ch == S:
                n = n + 1
                b = b + 1
            albo_inaczej ch == T:
                n = n + 1
                nt = nt + 1
                jeżeli b >= len(count):
                    count = count + [0] * (b - len(count) + 1)
                count[b] = count[b] + 1
                b = 0
            inaczej:
                przerwij
        self.n    = n
        self.nt   = nt
        self.norm = tuple(count), b
        self.is_simple = len(count) <= 1

    # zwróć length of longest contiguous run of spaces (whether albo nie
    # preceding a tab)
    def longest_run_of_spaces(self):
        count, trailing = self.norm
        zwróć max(len(count)-1, trailing)

    def indent_level(self, tabsize):
        # count, il = self.norm
        # dla i w range(len(count)):
        #    jeżeli count[i]:
        #        il = il + (i//tabsize + 1)*tabsize * count[i]
        # zwróć il

        # quicker:
        # il = trailing + sum (i//ts + 1)*ts*count[i] =
        # trailing + ts * sum (i//ts + 1)*count[i] =
        # trailing + ts * sum i//ts*count[i] + count[i] =
        # trailing + ts * [(sum i//ts*count[i]) + (sum count[i])] =
        # trailing + ts * [(sum i//ts*count[i]) + num_tabs]
        # oraz note that i//ts*count[i] jest 0 when i < ts

        count, trailing = self.norm
        il = 0
        dla i w range(tabsize, len(count)):
            il = il + i//tabsize * count[i]
        zwróć trailing + tabsize * (il + self.nt)

    # zwróć true iff self.indent_level(t) == other.indent_level(t)
    # dla all t >= 1
    def equal(self, other):
        zwróć self.norm == other.norm

    # zwróć a list of tuples (ts, i1, i2) such that
    # i1 == self.indent_level(ts) != other.indent_level(ts) == i2.
    # Intended to be used after nie self.equal(other) jest known, w which
    # case it will zwróć at least one witnessing tab size.
    def not_equal_witness(self, other):
        n = max(self.longest_run_of_spaces(),
                other.longest_run_of_spaces()) + 1
        a = []
        dla ts w range(1, n+1):
            jeżeli self.indent_level(ts) != other.indent_level(ts):
                a.append( (ts,
                           self.indent_level(ts),
                           other.indent_level(ts)) )
        zwróć a

    # Return Prawda iff self.indent_level(t) < other.indent_level(t)
    # dla all t >= 1.
    # The algorithm jest due to Vincent Broman.
    # Easy to prove it's correct.
    # XXXpost that.
    # Trivial to prove n jest sharp (consider T vs ST).
    # Unknown whether there's a faster general way.  I suspected so at
    # first, but no longer.
    # For the special (but common!) case where M oraz N are both of the
    # form (T*)(S*), M.less(N) iff M.len() < N.len() oraz
    # M.num_tabs() <= N.num_tabs(). Proof jest easy but kinda long-winded.
    # XXXwrite that up.
    # Note that M jest of the form (T*)(S*) iff len(M.norm[0]) <= 1.
    def less(self, other):
        jeżeli self.n >= other.n:
            zwróć Nieprawda
        jeżeli self.is_simple oraz other.is_simple:
            zwróć self.nt <= other.nt
        n = max(self.longest_run_of_spaces(),
                other.longest_run_of_spaces()) + 1
        # the self.n >= other.n test already did it dla ts=1
        dla ts w range(2, n+1):
            jeżeli self.indent_level(ts) >= other.indent_level(ts):
                zwróć Nieprawda
        zwróć Prawda

    # zwróć a list of tuples (ts, i1, i2) such that
    # i1 == self.indent_level(ts) >= other.indent_level(ts) == i2.
    # Intended to be used after nie self.less(other) jest known, w which
    # case it will zwróć at least one witnessing tab size.
    def not_less_witness(self, other):
        n = max(self.longest_run_of_spaces(),
                other.longest_run_of_spaces()) + 1
        a = []
        dla ts w range(1, n+1):
            jeżeli self.indent_level(ts) >= other.indent_level(ts):
                a.append( (ts,
                           self.indent_level(ts),
                           other.indent_level(ts)) )
        zwróć a

def format_witnesses(w):
    firsts = (str(tup[0]) dla tup w w)
    prefix = "at tab size"
    jeżeli len(w) > 1:
        prefix = prefix + "s"
    zwróć prefix + " " + ', '.join(firsts)

def process_tokens(tokens):
    INDENT = tokenize.INDENT
    DEDENT = tokenize.DEDENT
    NEWLINE = tokenize.NEWLINE
    JUNK = tokenize.COMMENT, tokenize.NL
    indents = [Whitespace("")]
    check_equal = 0

    dla (type, token, start, end, line) w tokens:
        jeżeli type == NEWLINE:
            # a program statement, albo ENDMARKER, will eventually follow,
            # after some (possibly empty) run of tokens of the form
            #     (NL | COMMENT)* (INDENT | DEDENT+)?
            # If an INDENT appears, setting check_equal jest wrong, oraz will
            # be undone when we see the INDENT.
            check_equal = 1

        albo_inaczej type == INDENT:
            check_equal = 0
            thisguy = Whitespace(token)
            jeżeli nie indents[-1].less(thisguy):
                witness = indents[-1].not_less_witness(thisguy)
                msg = "indent nie greater e.g. " + format_witnesses(witness)
                podnieś NannyNag(start[0], msg, line)
            indents.append(thisguy)

        albo_inaczej type == DEDENT:
            # there's nothing we need to check here!  what's important jest
            # that when the run of DEDENTs ends, the indentation of the
            # program statement (or ENDMARKER) that triggered the run jest
            # equal to what's left at the top of the indents stack

            # Ouch!  This assert triggers jeżeli the last line of the source
            # jest indented *and* lacks a newline -- then DEDENTs pop out
            # of thin air.
            # assert check_equal  # inaczej no earlier NEWLINE, albo an earlier INDENT
            check_equal = 1

            usuń indents[-1]

        albo_inaczej check_equal oraz type nie w JUNK:
            # this jest the first "real token" following a NEWLINE, so it
            # must be the first token of the next program statement, albo an
            # ENDMARKER; the "line" argument exposes the leading whitespace
            # dla this statement; w the case of ENDMARKER, line jest an empty
            # string, so will properly match the empty string przy which the
            # "indents" stack was seeded
            check_equal = 0
            thisguy = Whitespace(line)
            jeżeli nie indents[-1].equal(thisguy):
                witness = indents[-1].not_equal_witness(thisguy)
                msg = "indent nie equal e.g. " + format_witnesses(witness)
                podnieś NannyNag(start[0], msg, line)


jeżeli __name__ == '__main__':
    main()
