# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Python Software Foundation.
# All rights reserved.

"""Tokenization help dla Python programs.

generate_tokens(readline) jest a generator that przerwijs a stream of
text into Python tokens.  It accepts a readline-like method which jest called
repeatedly to get the next line of input (or "" dla EOF).  It generates
5-tuples przy these members:

    the token type (see token.py)
    the token (a string)
    the starting (row, column) indices of the token (a 2-tuple of ints)
    the ending (row, column) indices of the token (a 2-tuple of ints)
    the original line (string)

It jest designed to match the working of the Python tokenizer exactly, except
that it produces COMMENT tokens dla comments oraz gives type OP dla all
operators

Older entry points
    tokenize_loop(readline, tokeneater)
    tokenize(readline, tokeneater=printtoken)
are the same, wyjąwszy instead of generating tokens, tokeneater jest a callback
function to which the 5 fields described above are dalejed jako 5 arguments,
each time a new token jest found."""

__author__ = 'Ka-Ping Yee <ping@lfw.org>'
__credits__ = \
    'GvR, ESR, Tim Peters, Thomas Wouters, Fred Drake, Skip Montanaro'

zaimportuj string, re
z codecs zaimportuj BOM_UTF8, lookup
z lib2to3.pgen2.token zaimportuj *

z . zaimportuj token
__all__ = [x dla x w dir(token) jeżeli x[0] != '_'] + ["tokenize",
           "generate_tokens", "untokenize"]
usuń token

spróbuj:
    bytes
wyjąwszy NameError:
    # Support bytes type w Python <= 2.5, so 2to3 turns itself into
    # valid Python 3 code.
    bytes = str

def group(*choices): zwróć '(' + '|'.join(choices) + ')'
def any(*choices): zwróć group(*choices) + '*'
def maybe(*choices): zwróć group(*choices) + '?'

Whitespace = r'[ \f\t]*'
Comment = r'#[^\r\n]*'
Ignore = Whitespace + any(r'\\\r?\n' + Whitespace) + maybe(Comment)
Name = r'[a-zA-Z_]\w*'

Binnumber = r'0[bB][01]*'
Hexnumber = r'0[xX][\da-fA-F]*[lL]?'
Octnumber = r'0[oO]?[0-7]*[lL]?'
Decnumber = r'[1-9]\d*[lL]?'
Intnumber = group(Binnumber, Hexnumber, Octnumber, Decnumber)
Exponent = r'[eE][-+]?\d+'
Pointfloat = group(r'\d+\.\d*', r'\.\d+') + maybe(Exponent)
Expfloat = r'\d+' + Exponent
Floatnumber = group(Pointfloat, Expfloat)
Imagnumber = group(r'\d+[jJ]', Floatnumber + r'[jJ]')
Number = group(Imagnumber, Floatnumber, Intnumber)

# Tail end of ' string.
Single = r"[^'\\]*(?:\\.[^'\\]*)*'"
# Tail end of " string.
Double = r'[^"\\]*(?:\\.[^"\\]*)*"'
# Tail end of ''' string.
Single3 = r"[^'\\]*(?:(?:\\.|'(?!''))[^'\\]*)*'''"
# Tail end of """ string.
Double3 = r'[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""'
Triple = group("[ubUB]?[rR]?'''", '[ubUB]?[rR]?"""')
# Single-line ' albo " string.
String = group(r"[uU]?[rR]?'[^\n'\\]*(?:\\.[^\n'\\]*)*'",
               r'[uU]?[rR]?"[^\n"\\]*(?:\\.[^\n"\\]*)*"')

# Because of leftmost-then-longest match semantics, be sure to put the
# longest operators first (e.g., jeżeli = came before ==, == would get
# recognized jako two instances of =).
Operator = group(r"\*\*=?", r">>=?", r"<<=?", r"<>", r"!=",
                 r"//=?", r"->",
                 r"[+\-*/%&@|^=<>]=?",
                 r"~")

Bracket = '[][(){}]'
Special = group(r'\r?\n', r'[:;.,`@]')
Funny = group(Operator, Bracket, Special)

PlainToken = group(Number, Funny, String, Name)
Token = Ignore + PlainToken

# First (or only) line of ' albo " string.
ContStr = group(r"[uUbB]?[rR]?'[^\n'\\]*(?:\\.[^\n'\\]*)*" +
                group("'", r'\\\r?\n'),
                r'[uUbB]?[rR]?"[^\n"\\]*(?:\\.[^\n"\\]*)*' +
                group('"', r'\\\r?\n'))
PseudoExtras = group(r'\\\r?\n', Comment, Triple)
PseudoToken = Whitespace + group(PseudoExtras, Number, Funny, ContStr, Name)

tokenprog, pseudoprog, single3prog, double3prog = list(map(
    re.compile, (Token, PseudoToken, Single3, Double3)))
endprogs = {"'": re.compile(Single), '"': re.compile(Double),
            "'''": single3prog, '"""': double3prog,
            "r'''": single3prog, 'r"""': double3prog,
            "u'''": single3prog, 'u"""': double3prog,
            "b'''": single3prog, 'b"""': double3prog,
            "ur'''": single3prog, 'ur"""': double3prog,
            "br'''": single3prog, 'br"""': double3prog,
            "R'''": single3prog, 'R"""': double3prog,
            "U'''": single3prog, 'U"""': double3prog,
            "B'''": single3prog, 'B"""': double3prog,
            "uR'''": single3prog, 'uR"""': double3prog,
            "Ur'''": single3prog, 'Ur"""': double3prog,
            "UR'''": single3prog, 'UR"""': double3prog,
            "bR'''": single3prog, 'bR"""': double3prog,
            "Br'''": single3prog, 'Br"""': double3prog,
            "BR'''": single3prog, 'BR"""': double3prog,
            'r': Nic, 'R': Nic,
            'u': Nic, 'U': Nic,
            'b': Nic, 'B': Nic}

triple_quoted = {}
dla t w ("'''", '"""',
          "r'''", 'r"""', "R'''", 'R"""',
          "u'''", 'u"""', "U'''", 'U"""',
          "b'''", 'b"""', "B'''", 'B"""',
          "ur'''", 'ur"""', "Ur'''", 'Ur"""',
          "uR'''", 'uR"""', "UR'''", 'UR"""',
          "br'''", 'br"""', "Br'''", 'Br"""',
          "bR'''", 'bR"""', "BR'''", 'BR"""',):
    triple_quoted[t] = t
single_quoted = {}
dla t w ("'", '"',
          "r'", 'r"', "R'", 'R"',
          "u'", 'u"', "U'", 'U"',
          "b'", 'b"', "B'", 'B"',
          "ur'", 'ur"', "Ur'", 'Ur"',
          "uR'", 'uR"', "UR'", 'UR"',
          "br'", 'br"', "Br'", 'Br"',
          "bR'", 'bR"', "BR'", 'BR"', ):
    single_quoted[t] = t

tabsize = 8

klasa TokenError(Exception): dalej

klasa StopTokenizing(Exception): dalej

def printtoken(type, token, xxx_todo_changeme, xxx_todo_changeme1, line): # dla testing
    (srow, scol) = xxx_todo_changeme
    (erow, ecol) = xxx_todo_changeme1
    print("%d,%d-%d,%d:\t%s\t%s" % \
        (srow, scol, erow, ecol, tok_name[type], repr(token)))

def tokenize(readline, tokeneater=printtoken):
    """
    The tokenize() function accepts two parameters: one representing the
    input stream, oraz one providing an output mechanism dla tokenize().

    The first parameter, readline, must be a callable object which provides
    the same interface jako the readline() method of built-in file objects.
    Each call to the function should zwróć one line of input jako a string.

    The second parameter, tokeneater, must also be a callable object. It jest
    called once dla each token, przy five arguments, corresponding to the
    tuples generated by generate_tokens().
    """
    spróbuj:
        tokenize_loop(readline, tokeneater)
    wyjąwszy StopTokenizing:
        dalej

# backwards compatible interface
def tokenize_loop(readline, tokeneater):
    dla token_info w generate_tokens(readline):
        tokeneater(*token_info)

klasa Untokenizer:

    def __init__(self):
        self.tokens = []
        self.prev_row = 1
        self.prev_col = 0

    def add_whitespace(self, start):
        row, col = start
        assert row <= self.prev_row
        col_offset = col - self.prev_col
        jeżeli col_offset:
            self.tokens.append(" " * col_offset)

    def untokenize(self, iterable):
        dla t w iterable:
            jeżeli len(t) == 2:
                self.compat(t, iterable)
                przerwij
            tok_type, token, start, end, line = t
            self.add_whitespace(start)
            self.tokens.append(token)
            self.prev_row, self.prev_col = end
            jeżeli tok_type w (NEWLINE, NL):
                self.prev_row += 1
                self.prev_col = 0
        zwróć "".join(self.tokens)

    def compat(self, token, iterable):
        startline = Nieprawda
        indents = []
        toks_append = self.tokens.append
        toknum, tokval = token
        jeżeli toknum w (NAME, NUMBER):
            tokval += ' '
        jeżeli toknum w (NEWLINE, NL):
            startline = Prawda
        dla tok w iterable:
            toknum, tokval = tok[:2]

            jeżeli toknum w (NAME, NUMBER, ASYNC, AWAIT):
                tokval += ' '

            jeżeli toknum == INDENT:
                indents.append(tokval)
                kontynuuj
            albo_inaczej toknum == DEDENT:
                indents.pop()
                kontynuuj
            albo_inaczej toknum w (NEWLINE, NL):
                startline = Prawda
            albo_inaczej startline oraz indents:
                toks_append(indents[-1])
                startline = Nieprawda
            toks_append(tokval)

cookie_re = re.compile(r'^[ \t\f]*#.*coding[:=][ \t]*([-\w.]+)', re.ASCII)
blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)', re.ASCII)

def _get_normal_name(orig_enc):
    """Imitates get_normal_name w tokenizer.c."""
    # Only care about the first 12 characters.
    enc = orig_enc[:12].lower().replace("_", "-")
    jeżeli enc == "utf-8" albo enc.startswith("utf-8-"):
        zwróć "utf-8"
    jeżeli enc w ("latin-1", "iso-8859-1", "iso-latin-1") albo \
       enc.startswith(("latin-1-", "iso-8859-1-", "iso-latin-1-")):
        zwróć "iso-8859-1"
    zwróć orig_enc

def detect_encoding(readline):
    """
    The detect_encoding() function jest used to detect the encoding that should
    be used to decode a Python source file. It requires one argument, readline,
    w the same way jako the tokenize() generator.

    It will call readline a maximum of twice, oraz zwróć the encoding used
    (as a string) oraz a list of any lines (left jako bytes) it has read
    in.

    It detects the encoding z the presence of a utf-8 bom albo an encoding
    cookie jako specified w pep-0263. If both a bom oraz a cookie are present, but
    disagree, a SyntaxError will be podnieśd. If the encoding cookie jest an invalid
    charset, podnieś a SyntaxError.  Note that jeżeli a utf-8 bom jest found,
    'utf-8-sig' jest returned.

    If no encoding jest specified, then the default of 'utf-8' will be returned.
    """
    bom_found = Nieprawda
    encoding = Nic
    default = 'utf-8'
    def read_or_stop():
        spróbuj:
            zwróć readline()
        wyjąwszy StopIteration:
            zwróć bytes()

    def find_cookie(line):
        spróbuj:
            line_string = line.decode('ascii')
        wyjąwszy UnicodeDecodeError:
            zwróć Nic
        match = cookie_re.match(line_string)
        jeżeli nie match:
            zwróć Nic
        encoding = _get_normal_name(match.group(1))
        spróbuj:
            codec = lookup(encoding)
        wyjąwszy LookupError:
            # This behaviour mimics the Python interpreter
            podnieś SyntaxError("unknown encoding: " + encoding)

        jeżeli bom_found:
            jeżeli codec.name != 'utf-8':
                # This behaviour mimics the Python interpreter
                podnieś SyntaxError('encoding problem: utf-8')
            encoding += '-sig'
        zwróć encoding

    first = read_or_stop()
    jeżeli first.startswith(BOM_UTF8):
        bom_found = Prawda
        first = first[3:]
        default = 'utf-8-sig'
    jeżeli nie first:
        zwróć default, []

    encoding = find_cookie(first)
    jeżeli encoding:
        zwróć encoding, [first]
    jeżeli nie blank_re.match(first):
        zwróć default, [first]

    second = read_or_stop()
    jeżeli nie second:
        zwróć default, [first]

    encoding = find_cookie(second)
    jeżeli encoding:
        zwróć encoding, [first, second]

    zwróć default, [first, second]

def untokenize(iterable):
    """Transform tokens back into Python source code.

    Each element returned by the iterable must be a token sequence
    przy at least two elements, a token number oraz token value.  If
    only two tokens are dalejed, the resulting output jest poor.

    Round-trip invariant dla full input:
        Untokenized source will match input source exactly

    Round-trip invariant dla limited intput:
        # Output text will tokenize the back to the input
        t1 = [tok[:2] dla tok w generate_tokens(f.readline)]
        newcode = untokenize(t1)
        readline = iter(newcode.splitlines(1)).next
        t2 = [tok[:2] dla tokin generate_tokens(readline)]
        assert t1 == t2
    """
    ut = Untokenizer()
    zwróć ut.untokenize(iterable)

def generate_tokens(readline):
    """
    The generate_tokens() generator requires one argument, readline, which
    must be a callable object which provides the same interface jako the
    readline() method of built-in file objects. Each call to the function
    should zwróć one line of input jako a string.  Alternately, readline
    can be a callable function terminating przy StopIteration:
        readline = open(myfile).next    # Example of alternate readline

    The generator produces 5-tuples przy these members: the token type; the
    token string; a 2-tuple (srow, scol) of ints specifying the row oraz
    column where the token begins w the source; a 2-tuple (erow, ecol) of
    ints specifying the row oraz column where the token ends w the source;
    oraz the line on which the token was found. The line dalejed jest the
    logical line; continuation lines are included.
    """
    lnum = parenlev = continued = 0
    namechars, numchars = string.ascii_letters + '_', '0123456789'
    contstr, needcont = '', 0
    contline = Nic
    indents = [0]

    # 'stashed' oraz 'async_*' are used dla async/await parsing
    stashed = Nic
    async_def = Nieprawda
    async_def_indent = 0
    async_def_nl = Nieprawda

    dopóki 1:                                   # loop over lines w stream
        spróbuj:
            line = readline()
        wyjąwszy StopIteration:
            line = ''
        lnum = lnum + 1
        pos, max = 0, len(line)

        jeżeli contstr:                            # continued string
            jeżeli nie line:
                podnieś TokenError("EOF w multi-line string", strstart)
            endmatch = endprog.match(line)
            jeżeli endmatch:
                pos = end = endmatch.end(0)
                uzyskaj (STRING, contstr + line[:end],
                       strstart, (lnum, end), contline + line)
                contstr, needcont = '', 0
                contline = Nic
            albo_inaczej needcont oraz line[-2:] != '\\\n' oraz line[-3:] != '\\\r\n':
                uzyskaj (ERRORTOKEN, contstr + line,
                           strstart, (lnum, len(line)), contline)
                contstr = ''
                contline = Nic
                kontynuuj
            inaczej:
                contstr = contstr + line
                contline = contline + line
                kontynuuj

        albo_inaczej parenlev == 0 oraz nie continued:  # new statement
            jeżeli nie line: przerwij
            column = 0
            dopóki pos < max:                   # measure leading whitespace
                jeżeli line[pos] == ' ': column = column + 1
                albo_inaczej line[pos] == '\t': column = (column//tabsize + 1)*tabsize
                albo_inaczej line[pos] == '\f': column = 0
                inaczej: przerwij
                pos = pos + 1
            jeżeli pos == max: przerwij

            jeżeli stashed:
                uzyskaj stashed
                stashed = Nic

            jeżeli line[pos] w '#\r\n':           # skip comments albo blank lines
                jeżeli line[pos] == '#':
                    comment_token = line[pos:].rstrip('\r\n')
                    nl_pos = pos + len(comment_token)
                    uzyskaj (COMMENT, comment_token,
                           (lnum, pos), (lnum, pos + len(comment_token)), line)
                    uzyskaj (NL, line[nl_pos:],
                           (lnum, nl_pos), (lnum, len(line)), line)
                inaczej:
                    uzyskaj ((NL, COMMENT)[line[pos] == '#'], line[pos:],
                           (lnum, pos), (lnum, len(line)), line)
                kontynuuj

            jeżeli column > indents[-1]:           # count indents albo dedents
                indents.append(column)
                uzyskaj (INDENT, line[:pos], (lnum, 0), (lnum, pos), line)
            dopóki column < indents[-1]:
                jeżeli column nie w indents:
                    podnieś IndentationError(
                        "unindent does nie match any outer indentation level",
                        ("<tokenize>", lnum, pos, line))
                indents = indents[:-1]

                jeżeli async_def oraz async_def_indent >= indents[-1]:
                    async_def = Nieprawda
                    async_def_nl = Nieprawda
                    async_def_indent = 0

                uzyskaj (DEDENT, '', (lnum, pos), (lnum, pos), line)

            jeżeli async_def oraz async_def_nl oraz async_def_indent >= indents[-1]:
                async_def = Nieprawda
                async_def_nl = Nieprawda
                async_def_indent = 0

        inaczej:                                  # continued statement
            jeżeli nie line:
                podnieś TokenError("EOF w multi-line statement", (lnum, 0))
            continued = 0

        dopóki pos < max:
            pseudomatch = pseudoprog.match(line, pos)
            jeżeli pseudomatch:                                # scan dla tokens
                start, end = pseudomatch.span(1)
                spos, epos, pos = (lnum, start), (lnum, end), end
                token, initial = line[start:end], line[start]

                jeżeli initial w numchars albo \
                   (initial == '.' oraz token != '.'):      # ordinary number
                    uzyskaj (NUMBER, token, spos, epos, line)
                albo_inaczej initial w '\r\n':
                    newline = NEWLINE
                    jeżeli parenlev > 0:
                        newline = NL
                    albo_inaczej async_def:
                        async_def_nl = Prawda
                    jeżeli stashed:
                        uzyskaj stashed
                        stashed = Nic
                    uzyskaj (newline, token, spos, epos, line)

                albo_inaczej initial == '#':
                    assert nie token.endswith("\n")
                    jeżeli stashed:
                        uzyskaj stashed
                        stashed = Nic
                    uzyskaj (COMMENT, token, spos, epos, line)
                albo_inaczej token w triple_quoted:
                    endprog = endprogs[token]
                    endmatch = endprog.match(line, pos)
                    jeżeli endmatch:                           # all on one line
                        pos = endmatch.end(0)
                        token = line[start:pos]
                        jeżeli stashed:
                            uzyskaj stashed
                            stashed = Nic
                        uzyskaj (STRING, token, spos, (lnum, pos), line)
                    inaczej:
                        strstart = (lnum, start)           # multiple lines
                        contstr = line[start:]
                        contline = line
                        przerwij
                albo_inaczej initial w single_quoted albo \
                    token[:2] w single_quoted albo \
                    token[:3] w single_quoted:
                    jeżeli token[-1] == '\n':                  # continued string
                        strstart = (lnum, start)
                        endprog = (endprogs[initial] albo endprogs[token[1]] albo
                                   endprogs[token[2]])
                        contstr, needcont = line[start:], 1
                        contline = line
                        przerwij
                    inaczej:                                  # ordinary string
                        jeżeli stashed:
                            uzyskaj stashed
                            stashed = Nic
                        uzyskaj (STRING, token, spos, epos, line)
                albo_inaczej initial w namechars:                 # ordinary name
                    jeżeli token w ('async', 'await'):
                        jeżeli async_def:
                            uzyskaj (ASYNC jeżeli token == 'async' inaczej AWAIT,
                                   token, spos, epos, line)
                            kontynuuj

                    tok = (NAME, token, spos, epos, line)
                    jeżeli token == 'async' oraz nie stashed:
                        stashed = tok
                        kontynuuj

                    jeżeli token == 'def':
                        jeżeli (stashed
                                oraz stashed[0] == NAME
                                oraz stashed[1] == 'async'):

                            async_def = Prawda
                            async_def_indent = indents[-1]

                            uzyskaj (ASYNC, stashed[1],
                                   stashed[2], stashed[3],
                                   stashed[4])
                            stashed = Nic

                    jeżeli stashed:
                        uzyskaj stashed
                        stashed = Nic

                    uzyskaj tok
                albo_inaczej initial == '\\':                      # continued stmt
                    # This uzyskaj jest new; needed dla better idempotency:
                    jeżeli stashed:
                        uzyskaj stashed
                        stashed = Nic
                    uzyskaj (NL, token, spos, (lnum, pos), line)
                    continued = 1
                inaczej:
                    jeżeli initial w '([{': parenlev = parenlev + 1
                    albo_inaczej initial w ')]}': parenlev = parenlev - 1
                    jeżeli stashed:
                        uzyskaj stashed
                        stashed = Nic
                    uzyskaj (OP, token, spos, epos, line)
            inaczej:
                uzyskaj (ERRORTOKEN, line[pos],
                           (lnum, pos), (lnum, pos+1), line)
                pos = pos + 1

    jeżeli stashed:
        uzyskaj stashed
        stashed = Nic

    dla indent w indents[1:]:                 # pop remaining indent levels
        uzyskaj (DEDENT, '', (lnum, 0), (lnum, 0), '')
    uzyskaj (ENDMARKER, '', (lnum, 0), (lnum, 0), '')

jeżeli __name__ == '__main__':                     # testing
    zaimportuj sys
    jeżeli len(sys.argv) > 1: tokenize(open(sys.argv[1]).readline)
    inaczej: tokenize(sys.stdin.readline)
