"""Tokenization help dla Python programs.

tokenize(readline) jest a generator that przerwijs a stream of bytes into
Python tokens.  It decodes the bytes according to PEP-0263 for
determining source file encoding.

It accepts a readline-like method which jest called repeatedly to get the
next line of input (or b"" dla EOF).  It generates 5-tuples przy these
members:

    the token type (see token.py)
    the token (a string)
    the starting (row, column) indices of the token (a 2-tuple of ints)
    the ending (row, column) indices of the token (a 2-tuple of ints)
    the original line (string)

It jest designed to match the working of the Python tokenizer exactly, except
that it produces COMMENT tokens dla comments oraz gives type OP dla all
operators.  Additionally, all token lists start przy an ENCODING token
which tells you which encoding was used to decode the bytes stream.
"""

__author__ = 'Ka-Ping Yee <ping@lfw.org>'
__credits__ = ('GvR, ESR, Tim Peters, Thomas Wouters, Fred Drake, '
               'Skip Montanaro, Raymond Hettinger, Trent Nelson, '
               'Michael Foord')
z builtins zaimportuj open jako _builtin_open
z codecs zaimportuj lookup, BOM_UTF8
zaimportuj collections
z io zaimportuj TextIOWrapper
z itertools zaimportuj chain
zaimportuj re
zaimportuj sys
z token zaimportuj *

cookie_re = re.compile(r'^[ \t\f]*#.*coding[:=][ \t]*([-\w.]+)', re.ASCII)
blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)', re.ASCII)

zaimportuj token
__all__ = token.__all__ + ["COMMENT", "tokenize", "detect_encoding",
                           "NL", "untokenize", "ENCODING", "TokenInfo"]
usuń token

COMMENT = N_TOKENS
tok_name[COMMENT] = 'COMMENT'
NL = N_TOKENS + 1
tok_name[NL] = 'NL'
ENCODING = N_TOKENS + 2
tok_name[ENCODING] = 'ENCODING'
N_TOKENS += 3
EXACT_TOKEN_TYPES = {
    '(':   LPAR,
    ')':   RPAR,
    '[':   LSQB,
    ']':   RSQB,
    ':':   COLON,
    ',':   COMMA,
    ';':   SEMI,
    '+':   PLUS,
    '-':   MINUS,
    '*':   STAR,
    '/':   SLASH,
    '|':   VBAR,
    '&':   AMPER,
    '<':   LESS,
    '>':   GREATER,
    '=':   EQUAL,
    '.':   DOT,
    '%':   PERCENT,
    '{':   LBRACE,
    '}':   RBRACE,
    '==':  EQEQUAL,
    '!=':  NOTEQUAL,
    '<=':  LESSEQUAL,
    '>=':  GREATEREQUAL,
    '~':   TILDE,
    '^':   CIRCUMFLEX,
    '<<':  LEFTSHIFT,
    '>>':  RIGHTSHIFT,
    '**':  DOUBLESTAR,
    '+=':  PLUSEQUAL,
    '-=':  MINEQUAL,
    '*=':  STAREQUAL,
    '/=':  SLASHEQUAL,
    '%=':  PERCENTEQUAL,
    '&=':  AMPEREQUAL,
    '|=':  VBAREQUAL,
    '^=': CIRCUMFLEXEQUAL,
    '<<=': LEFTSHIFTEQUAL,
    '>>=': RIGHTSHIFTEQUAL,
    '**=': DOUBLESTAREQUAL,
    '//':  DOUBLESLASH,
    '//=': DOUBLESLASHEQUAL,
    '@':   AT,
    '@=':  ATEQUAL,
}

klasa TokenInfo(collections.namedtuple('TokenInfo', 'type string start end line')):
    def __repr__(self):
        annotated_type = '%d (%s)' % (self.type, tok_name[self.type])
        zwróć ('TokenInfo(type=%s, string=%r, start=%r, end=%r, line=%r)' %
                self._replace(type=annotated_type))

    @property
    def exact_type(self):
        jeżeli self.type == OP oraz self.string w EXACT_TOKEN_TYPES:
            zwróć EXACT_TOKEN_TYPES[self.string]
        inaczej:
            zwróć self.type

def group(*choices): zwróć '(' + '|'.join(choices) + ')'
def any(*choices): zwróć group(*choices) + '*'
def maybe(*choices): zwróć group(*choices) + '?'

# Note: we use unicode matching dla names ("\w") but ascii matching for
# number literals.
Whitespace = r'[ \f\t]*'
Comment = r'#[^\r\n]*'
Ignore = Whitespace + any(r'\\\r?\n' + Whitespace) + maybe(Comment)
Name = r'\w+'

Hexnumber = r'0[xX][0-9a-fA-F]+'
Binnumber = r'0[bB][01]+'
Octnumber = r'0[oO][0-7]+'
Decnumber = r'(?:0+|[1-9][0-9]*)'
Intnumber = group(Hexnumber, Binnumber, Octnumber, Decnumber)
Exponent = r'[eE][-+]?[0-9]+'
Pointfloat = group(r'[0-9]+\.[0-9]*', r'\.[0-9]+') + maybe(Exponent)
Expfloat = r'[0-9]+' + Exponent
Floatnumber = group(Pointfloat, Expfloat)
Imagnumber = group(r'[0-9]+[jJ]', Floatnumber + r'[jJ]')
Number = group(Imagnumber, Floatnumber, Intnumber)

StringPrefix = r'(?:[bB][rR]?|[rR][bB]?|[uU])?'

# Tail end of ' string.
Single = r"[^'\\]*(?:\\.[^'\\]*)*'"
# Tail end of " string.
Double = r'[^"\\]*(?:\\.[^"\\]*)*"'
# Tail end of ''' string.
Single3 = r"[^'\\]*(?:(?:\\.|'(?!''))[^'\\]*)*'''"
# Tail end of """ string.
Double3 = r'[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""'
Triple = group(StringPrefix + "'''", StringPrefix + '"""')
# Single-line ' albo " string.
String = group(StringPrefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'",
               StringPrefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"')

# Because of leftmost-then-longest match semantics, be sure to put the
# longest operators first (e.g., jeżeli = came before ==, == would get
# recognized jako two instances of =).
Operator = group(r"\*\*=?", r">>=?", r"<<=?", r"!=",
                 r"//=?", r"->",
                 r"[+\-*/%&@|^=<>]=?",
                 r"~")

Bracket = '[][(){}]'
Special = group(r'\r?\n', r'\.\.\.', r'[:;.,@]')
Funny = group(Operator, Bracket, Special)

PlainToken = group(Number, Funny, String, Name)
Token = Ignore + PlainToken

# First (or only) line of ' albo " string.
ContStr = group(StringPrefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*" +
                group("'", r'\\\r?\n'),
                StringPrefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*' +
                group('"', r'\\\r?\n'))
PseudoExtras = group(r'\\\r?\n|\Z', Comment, Triple)
PseudoToken = Whitespace + group(PseudoExtras, Number, Funny, ContStr, Name)

def _compile(expr):
    zwróć re.compile(expr, re.UNICODE)

endpats = {"'": Single, '"': Double,
           "'''": Single3, '"""': Double3,
           "r'''": Single3, 'r"""': Double3,
           "b'''": Single3, 'b"""': Double3,
           "R'''": Single3, 'R"""': Double3,
           "B'''": Single3, 'B"""': Double3,
           "br'''": Single3, 'br"""': Double3,
           "bR'''": Single3, 'bR"""': Double3,
           "Br'''": Single3, 'Br"""': Double3,
           "BR'''": Single3, 'BR"""': Double3,
           "rb'''": Single3, 'rb"""': Double3,
           "Rb'''": Single3, 'Rb"""': Double3,
           "rB'''": Single3, 'rB"""': Double3,
           "RB'''": Single3, 'RB"""': Double3,
           "u'''": Single3, 'u"""': Double3,
           "U'''": Single3, 'U"""': Double3,
           'r': Nic, 'R': Nic, 'b': Nic, 'B': Nic,
           'u': Nic, 'U': Nic}

triple_quoted = {}
dla t w ("'''", '"""',
          "r'''", 'r"""', "R'''", 'R"""',
          "b'''", 'b"""', "B'''", 'B"""',
          "br'''", 'br"""', "Br'''", 'Br"""',
          "bR'''", 'bR"""', "BR'''", 'BR"""',
          "rb'''", 'rb"""', "rB'''", 'rB"""',
          "Rb'''", 'Rb"""', "RB'''", 'RB"""',
          "u'''", 'u"""', "U'''", 'U"""',
          ):
    triple_quoted[t] = t
single_quoted = {}
dla t w ("'", '"',
          "r'", 'r"', "R'", 'R"',
          "b'", 'b"', "B'", 'B"',
          "br'", 'br"', "Br'", 'Br"',
          "bR'", 'bR"', "BR'", 'BR"' ,
          "rb'", 'rb"', "rB'", 'rB"',
          "Rb'", 'Rb"', "RB'", 'RB"' ,
          "u'", 'u"', "U'", 'U"',
          ):
    single_quoted[t] = t

tabsize = 8

klasa TokenError(Exception): dalej

klasa StopTokenizing(Exception): dalej


klasa Untokenizer:

    def __init__(self):
        self.tokens = []
        self.prev_row = 1
        self.prev_col = 0
        self.encoding = Nic

    def add_whitespace(self, start):
        row, col = start
        jeżeli row < self.prev_row albo row == self.prev_row oraz col < self.prev_col:
            podnieś ValueError("start ({},{}) precedes previous end ({},{})"
                             .format(row, col, self.prev_row, self.prev_col))
        row_offset = row - self.prev_row
        jeżeli row_offset:
            self.tokens.append("\\\n" * row_offset)
            self.prev_col = 0
        col_offset = col - self.prev_col
        jeżeli col_offset:
            self.tokens.append(" " * col_offset)

    def untokenize(self, iterable):
        it = iter(iterable)
        indents = []
        startline = Nieprawda
        dla t w it:
            jeżeli len(t) == 2:
                self.compat(t, it)
                przerwij
            tok_type, token, start, end, line = t
            jeżeli tok_type == ENCODING:
                self.encoding = token
                kontynuuj
            jeżeli tok_type == ENDMARKER:
                przerwij
            jeżeli tok_type == INDENT:
                indents.append(token)
                kontynuuj
            albo_inaczej tok_type == DEDENT:
                indents.pop()
                self.prev_row, self.prev_col = end
                kontynuuj
            albo_inaczej tok_type w (NEWLINE, NL):
                startline = Prawda
            albo_inaczej startline oraz indents:
                indent = indents[-1]
                jeżeli start[1] >= len(indent):
                    self.tokens.append(indent)
                    self.prev_col = len(indent)
                startline = Nieprawda
            self.add_whitespace(start)
            self.tokens.append(token)
            self.prev_row, self.prev_col = end
            jeżeli tok_type w (NEWLINE, NL):
                self.prev_row += 1
                self.prev_col = 0
        zwróć "".join(self.tokens)

    def compat(self, token, iterable):
        indents = []
        toks_append = self.tokens.append
        startline = token[0] w (NEWLINE, NL)
        prevstring = Nieprawda

        dla tok w chain([token], iterable):
            toknum, tokval = tok[:2]
            jeżeli toknum == ENCODING:
                self.encoding = tokval
                kontynuuj

            jeżeli toknum w (NAME, NUMBER, ASYNC, AWAIT):
                tokval += ' '

            # Insert a space between two consecutive strings
            jeżeli toknum == STRING:
                jeżeli prevstring:
                    tokval = ' ' + tokval
                prevstring = Prawda
            inaczej:
                prevstring = Nieprawda

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


def untokenize(iterable):
    """Transform tokens back into Python source code.
    It returns a bytes object, encoded using the ENCODING
    token, which jest the first token sequence output by tokenize.

    Each element returned by the iterable must be a token sequence
    przy at least two elements, a token number oraz token value.  If
    only two tokens are dalejed, the resulting output jest poor.

    Round-trip invariant dla full input:
        Untokenized source will match input source exactly

    Round-trip invariant dla limited intput:
        # Output bytes will tokenize the back to the input
        t1 = [tok[:2] dla tok w tokenize(f.readline)]
        newcode = untokenize(t1)
        readline = BytesIO(newcode).readline
        t2 = [tok[:2] dla tok w tokenize(readline)]
        assert t1 == t2
    """
    ut = Untokenizer()
    out = ut.untokenize(iterable)
    jeżeli ut.encoding jest nie Nic:
        out = out.encode(ut.encoding)
    zwróć out


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
    be used to decode a Python source file.  It requires one argument, readline,
    w the same way jako the tokenize() generator.

    It will call readline a maximum of twice, oraz zwróć the encoding used
    (as a string) oraz a list of any lines (left jako bytes) it has read in.

    It detects the encoding z the presence of a utf-8 bom albo an encoding
    cookie jako specified w pep-0263.  If both a bom oraz a cookie are present,
    but disagree, a SyntaxError will be podnieśd.  If the encoding cookie jest an
    invalid charset, podnieś a SyntaxError.  Note that jeżeli a utf-8 bom jest found,
    'utf-8-sig' jest returned.

    If no encoding jest specified, then the default of 'utf-8' will be returned.
    """
    spróbuj:
        filename = readline.__self__.name
    wyjąwszy AttributeError:
        filename = Nic
    bom_found = Nieprawda
    encoding = Nic
    default = 'utf-8'
    def read_or_stop():
        spróbuj:
            zwróć readline()
        wyjąwszy StopIteration:
            zwróć b''

    def find_cookie(line):
        spróbuj:
            # Decode jako UTF-8. Either the line jest an encoding declaration,
            # w which case it should be pure ASCII, albo it must be UTF-8
            # per default encoding.
            line_string = line.decode('utf-8')
        wyjąwszy UnicodeDecodeError:
            msg = "invalid albo missing encoding declaration"
            jeżeli filename jest nie Nic:
                msg = '{} dla {!r}'.format(msg, filename)
            podnieś SyntaxError(msg)

        match = cookie_re.match(line_string)
        jeżeli nie match:
            zwróć Nic
        encoding = _get_normal_name(match.group(1))
        spróbuj:
            codec = lookup(encoding)
        wyjąwszy LookupError:
            # This behaviour mimics the Python interpreter
            jeżeli filename jest Nic:
                msg = "unknown encoding: " + encoding
            inaczej:
                msg = "unknown encoding dla {!r}: {}".format(filename,
                        encoding)
            podnieś SyntaxError(msg)

        jeżeli bom_found:
            jeżeli encoding != 'utf-8':
                # This behaviour mimics the Python interpreter
                jeżeli filename jest Nic:
                    msg = 'encoding problem: utf-8'
                inaczej:
                    msg = 'encoding problem dla {!r}: utf-8'.format(filename)
                podnieś SyntaxError(msg)
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


def open(filename):
    """Open a file w read only mode using the encoding detected by
    detect_encoding().
    """
    buffer = _builtin_open(filename, 'rb')
    spróbuj:
        encoding, lines = detect_encoding(buffer.readline)
        buffer.seek(0)
        text = TextIOWrapper(buffer, encoding, line_buffering=Prawda)
        text.mode = 'r'
        zwróć text
    wyjąwszy:
        buffer.close()
        podnieś


def tokenize(readline):
    """
    The tokenize() generator requires one argment, readline, which
    must be a callable object which provides the same interface jako the
    readline() method of built-in file objects.  Each call to the function
    should zwróć one line of input jako bytes.  Alternately, readline
    can be a callable function terminating przy StopIteration:
        readline = open(myfile, 'rb').__next__  # Example of alternate readline

    The generator produces 5-tuples przy these members: the token type; the
    token string; a 2-tuple (srow, scol) of ints specifying the row oraz
    column where the token begins w the source; a 2-tuple (erow, ecol) of
    ints specifying the row oraz column where the token ends w the source;
    oraz the line on which the token was found.  The line dalejed jest the
    logical line; continuation lines are included.

    The first token sequence will always be an ENCODING token
    which tells you which encoding was used to decode the bytes stream.
    """
    # This zaimportuj jest here to avoid problems when the itertools module jest nie
    # built yet oraz tokenize jest imported.
    z itertools zaimportuj chain, repeat
    encoding, consumed = detect_encoding(readline)
    rl_gen = iter(readline, b"")
    empty = repeat(b"")
    zwróć _tokenize(chain(consumed, rl_gen, empty).__next__, encoding)


def _tokenize(readline, encoding):
    lnum = parenlev = continued = 0
    numchars = '0123456789'
    contstr, needcont = '', 0
    contline = Nic
    indents = [0]

    # 'stashed' oraz 'async_*' are used dla async/await parsing
    stashed = Nic
    async_def = Nieprawda
    async_def_indent = 0
    async_def_nl = Nieprawda

    jeżeli encoding jest nie Nic:
        jeżeli encoding == "utf-8-sig":
            # BOM will already have been stripped.
            encoding = "utf-8"
        uzyskaj TokenInfo(ENCODING, encoding, (0, 0), (0, 0), '')
    dopóki Prawda:             # loop over lines w stream
        spróbuj:
            line = readline()
        wyjąwszy StopIteration:
            line = b''

        jeżeli encoding jest nie Nic:
            line = line.decode(encoding)
        lnum += 1
        pos, max = 0, len(line)

        jeżeli contstr:                            # continued string
            jeżeli nie line:
                podnieś TokenError("EOF w multi-line string", strstart)
            endmatch = endprog.match(line)
            jeżeli endmatch:
                pos = end = endmatch.end(0)
                uzyskaj TokenInfo(STRING, contstr + line[:end],
                       strstart, (lnum, end), contline + line)
                contstr, needcont = '', 0
                contline = Nic
            albo_inaczej needcont oraz line[-2:] != '\\\n' oraz line[-3:] != '\\\r\n':
                uzyskaj TokenInfo(ERRORTOKEN, contstr + line,
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
                jeżeli line[pos] == ' ':
                    column += 1
                albo_inaczej line[pos] == '\t':
                    column = (column//tabsize + 1)*tabsize
                albo_inaczej line[pos] == '\f':
                    column = 0
                inaczej:
                    przerwij
                pos += 1
            jeżeli pos == max:
                przerwij

            jeżeli line[pos] w '#\r\n':           # skip comments albo blank lines
                jeżeli line[pos] == '#':
                    comment_token = line[pos:].rstrip('\r\n')
                    nl_pos = pos + len(comment_token)
                    uzyskaj TokenInfo(COMMENT, comment_token,
                           (lnum, pos), (lnum, pos + len(comment_token)), line)
                    uzyskaj TokenInfo(NL, line[nl_pos:],
                           (lnum, nl_pos), (lnum, len(line)), line)
                inaczej:
                    uzyskaj TokenInfo((NL, COMMENT)[line[pos] == '#'], line[pos:],
                           (lnum, pos), (lnum, len(line)), line)
                kontynuuj

            jeżeli column > indents[-1]:           # count indents albo dedents
                indents.append(column)
                uzyskaj TokenInfo(INDENT, line[:pos], (lnum, 0), (lnum, pos), line)
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

                uzyskaj TokenInfo(DEDENT, '', (lnum, pos), (lnum, pos), line)

            jeżeli async_def oraz async_def_nl oraz async_def_indent >= indents[-1]:
                async_def = Nieprawda
                async_def_nl = Nieprawda
                async_def_indent = 0

        inaczej:                                  # continued statement
            jeżeli nie line:
                podnieś TokenError("EOF w multi-line statement", (lnum, 0))
            continued = 0

        dopóki pos < max:
            pseudomatch = _compile(PseudoToken).match(line, pos)
            jeżeli pseudomatch:                                # scan dla tokens
                start, end = pseudomatch.span(1)
                spos, epos, pos = (lnum, start), (lnum, end), end
                jeżeli start == end:
                    kontynuuj
                token, initial = line[start:end], line[start]

                jeżeli (initial w numchars albo                  # ordinary number
                    (initial == '.' oraz token != '.' oraz token != '...')):
                    uzyskaj TokenInfo(NUMBER, token, spos, epos, line)
                albo_inaczej initial w '\r\n':
                    jeżeli stashed:
                        uzyskaj stashed
                        stashed = Nic
                    jeżeli parenlev > 0:
                        uzyskaj TokenInfo(NL, token, spos, epos, line)
                    inaczej:
                        uzyskaj TokenInfo(NEWLINE, token, spos, epos, line)
                        jeżeli async_def:
                            async_def_nl = Prawda

                albo_inaczej initial == '#':
                    assert nie token.endswith("\n")
                    jeżeli stashed:
                        uzyskaj stashed
                        stashed = Nic
                    uzyskaj TokenInfo(COMMENT, token, spos, epos, line)
                albo_inaczej token w triple_quoted:
                    endprog = _compile(endpats[token])
                    endmatch = endprog.match(line, pos)
                    jeżeli endmatch:                           # all on one line
                        pos = endmatch.end(0)
                        token = line[start:pos]
                        uzyskaj TokenInfo(STRING, token, spos, (lnum, pos), line)
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
                        endprog = _compile(endpats[initial] albo
                                           endpats[token[1]] albo
                                           endpats[token[2]])
                        contstr, needcont = line[start:], 1
                        contline = line
                        przerwij
                    inaczej:                                  # ordinary string
                        uzyskaj TokenInfo(STRING, token, spos, epos, line)
                albo_inaczej initial.isidentifier():               # ordinary name
                    jeżeli token w ('async', 'await'):
                        jeżeli async_def:
                            uzyskaj TokenInfo(
                                ASYNC jeżeli token == 'async' inaczej AWAIT,
                                token, spos, epos, line)
                            kontynuuj

                    tok = TokenInfo(NAME, token, spos, epos, line)
                    jeżeli token == 'async' oraz nie stashed:
                        stashed = tok
                        kontynuuj

                    jeżeli token == 'def':
                        jeżeli (stashed
                                oraz stashed.type == NAME
                                oraz stashed.string == 'async'):

                            async_def = Prawda
                            async_def_indent = indents[-1]

                            uzyskaj TokenInfo(ASYNC, stashed.string,
                                            stashed.start, stashed.end,
                                            stashed.line)
                            stashed = Nic

                    jeżeli stashed:
                        uzyskaj stashed
                        stashed = Nic

                    uzyskaj tok
                albo_inaczej initial == '\\':                      # continued stmt
                    continued = 1
                inaczej:
                    jeżeli initial w '([{':
                        parenlev += 1
                    albo_inaczej initial w ')]}':
                        parenlev -= 1
                    jeżeli stashed:
                        uzyskaj stashed
                        stashed = Nic
                    uzyskaj TokenInfo(OP, token, spos, epos, line)
            inaczej:
                uzyskaj TokenInfo(ERRORTOKEN, line[pos],
                           (lnum, pos), (lnum, pos+1), line)
                pos += 1

    jeżeli stashed:
        uzyskaj stashed
        stashed = Nic

    dla indent w indents[1:]:                 # pop remaining indent levels
        uzyskaj TokenInfo(DEDENT, '', (lnum, 0), (lnum, 0), '')
    uzyskaj TokenInfo(ENDMARKER, '', (lnum, 0), (lnum, 0), '')


# An undocumented, backwards compatible, API dla all the places w the standard
# library that expect to be able to use tokenize przy strings
def generate_tokens(readline):
    zwróć _tokenize(readline, Nic)

def main():
    zaimportuj argparse

    # Helper error handling routines
    def perror(message):
        print(message, file=sys.stderr)

    def error(message, filename=Nic, location=Nic):
        jeżeli location:
            args = (filename,) + location + (message,)
            perror("%s:%d:%d: error: %s" % args)
        albo_inaczej filename:
            perror("%s: error: %s" % (filename, message))
        inaczej:
            perror("error: %s" % message)
        sys.exit(1)

    # Parse the arguments oraz options
    parser = argparse.ArgumentParser(prog='python -m tokenize')
    parser.add_argument(dest='filename', nargs='?',
                        metavar='filename.py',
                        help='the file to tokenize; defaults to stdin')
    parser.add_argument('-e', '--exact', dest='exact', action='store_true',
                        help='display token names using the exact type')
    args = parser.parse_args()

    spróbuj:
        # Tokenize the input
        jeżeli args.filename:
            filename = args.filename
            przy _builtin_open(filename, 'rb') jako f:
                tokens = list(tokenize(f.readline))
        inaczej:
            filename = "<stdin>"
            tokens = _tokenize(sys.stdin.readline, Nic)

        # Output the tokenization
        dla token w tokens:
            token_type = token.type
            jeżeli args.exact:
                token_type = token.exact_type
            token_range = "%d,%d-%d,%d:" % (token.start + token.end)
            print("%-20s%-15s%-15r" %
                  (token_range, tok_name[token_type], token.string))
    wyjąwszy IndentationError jako err:
        line, column = err.args[1][1:3]
        error(err.args[0], filename, (line, column))
    wyjąwszy TokenError jako err:
        line, column = err.args[1]
        error(err.args[0], filename, (line, column))
    wyjąwszy SyntaxError jako err:
        error(err, filename)
    wyjąwszy OSError jako err:
        error(err)
    wyjąwszy KeyboardInterrupt:
        print("interrupted\n")
    wyjąwszy Exception jako err:
        perror("unexpected error: %s" % err)
        podnieś

jeżeli __name__ == "__main__":
    main()
