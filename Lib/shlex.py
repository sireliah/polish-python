"""A lexical analyzer klasa dla simple shell-like syntaxes."""

# Module oraz documentation by Eric S. Raymond, 21 Dec 1998
# Input stacking oraz error message cleanup added by ESR, March 2000
# push_source() oraz pop_source() made explicit by ESR, January 2001.
# Posix compliance, split(), string arguments, oraz
# iterator interface by Gustavo Niemeyer, April 2003.

zaimportuj os
zaimportuj re
zaimportuj sys
z collections zaimportuj deque

z io zaimportuj StringIO

__all__ = ["shlex", "split", "quote"]

klasa shlex:
    "A lexical analyzer klasa dla simple shell-like syntaxes."
    def __init__(self, instream=Nic, infile=Nic, posix=Nieprawda):
        jeżeli isinstance(instream, str):
            instream = StringIO(instream)
        jeżeli instream jest nie Nic:
            self.instream = instream
            self.infile = infile
        inaczej:
            self.instream = sys.stdin
            self.infile = Nic
        self.posix = posix
        jeżeli posix:
            self.eof = Nic
        inaczej:
            self.eof = ''
        self.commenters = '#'
        self.wordchars = ('abcdfeghijklmnopqrstuvwxyz'
                          'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
        jeżeli self.posix:
            self.wordchars += ('ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'
                               'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ')
        self.whitespace = ' \t\r\n'
        self.whitespace_split = Nieprawda
        self.quotes = '\'"'
        self.escape = '\\'
        self.escapedquotes = '"'
        self.state = ' '
        self.pushback = deque()
        self.lineno = 1
        self.debug = 0
        self.token = ''
        self.filestack = deque()
        self.source = Nic

    def push_token(self, tok):
        "Push a token onto the stack popped by the get_token method"
        jeżeli self.debug >= 1:
            print("shlex: pushing token " + repr(tok))
        self.pushback.appendleft(tok)

    def push_source(self, newstream, newfile=Nic):
        "Push an input source onto the lexer's input source stack."
        jeżeli isinstance(newstream, str):
            newstream = StringIO(newstream)
        self.filestack.appendleft((self.infile, self.instream, self.lineno))
        self.infile = newfile
        self.instream = newstream
        self.lineno = 1
        jeżeli self.debug:
            jeżeli newfile jest nie Nic:
                print('shlex: pushing to file %s' % (self.infile,))
            inaczej:
                print('shlex: pushing to stream %s' % (self.instream,))

    def pop_source(self):
        "Pop the input source stack."
        self.instream.close()
        (self.infile, self.instream, self.lineno) = self.filestack.popleft()
        jeżeli self.debug:
            print('shlex: popping to %s, line %d' \
                  % (self.instream, self.lineno))
        self.state = ' '

    def get_token(self):
        "Get a token z the input stream (or z stack jeżeli it's nonempty)"
        jeżeli self.pushback:
            tok = self.pushback.popleft()
            jeżeli self.debug >= 1:
                print("shlex: popping token " + repr(tok))
            zwróć tok
        # No pushback.  Get a token.
        raw = self.read_token()
        # Handle inclusions
        jeżeli self.source jest nie Nic:
            dopóki raw == self.source:
                spec = self.sourcehook(self.read_token())
                jeżeli spec:
                    (newfile, newstream) = spec
                    self.push_source(newstream, newfile)
                raw = self.get_token()
        # Maybe we got EOF instead?
        dopóki raw == self.eof:
            jeżeli nie self.filestack:
                zwróć self.eof
            inaczej:
                self.pop_source()
                raw = self.get_token()
        # Neither inclusion nor EOF
        jeżeli self.debug >= 1:
            jeżeli raw != self.eof:
                print("shlex: token=" + repr(raw))
            inaczej:
                print("shlex: token=EOF")
        zwróć raw

    def read_token(self):
        quoted = Nieprawda
        escapedstate = ' '
        dopóki Prawda:
            nextchar = self.instream.read(1)
            jeżeli nextchar == '\n':
                self.lineno = self.lineno + 1
            jeżeli self.debug >= 3:
                print("shlex: w state", repr(self.state), \
                      "I see character:", repr(nextchar))
            jeżeli self.state jest Nic:
                self.token = ''        # past end of file
                przerwij
            albo_inaczej self.state == ' ':
                jeżeli nie nextchar:
                    self.state = Nic  # end of file
                    przerwij
                albo_inaczej nextchar w self.whitespace:
                    jeżeli self.debug >= 2:
                        print("shlex: I see whitespace w whitespace state")
                    jeżeli self.token albo (self.posix oraz quoted):
                        przerwij   # emit current token
                    inaczej:
                        kontynuuj
                albo_inaczej nextchar w self.commenters:
                    self.instream.readline()
                    self.lineno = self.lineno + 1
                albo_inaczej self.posix oraz nextchar w self.escape:
                    escapedstate = 'a'
                    self.state = nextchar
                albo_inaczej nextchar w self.wordchars:
                    self.token = nextchar
                    self.state = 'a'
                albo_inaczej nextchar w self.quotes:
                    jeżeli nie self.posix:
                        self.token = nextchar
                    self.state = nextchar
                albo_inaczej self.whitespace_split:
                    self.token = nextchar
                    self.state = 'a'
                inaczej:
                    self.token = nextchar
                    jeżeli self.token albo (self.posix oraz quoted):
                        przerwij   # emit current token
                    inaczej:
                        kontynuuj
            albo_inaczej self.state w self.quotes:
                quoted = Prawda
                jeżeli nie nextchar:      # end of file
                    jeżeli self.debug >= 2:
                        print("shlex: I see EOF w quotes state")
                    # XXX what error should be podnieśd here?
                    podnieś ValueError("No closing quotation")
                jeżeli nextchar == self.state:
                    jeżeli nie self.posix:
                        self.token = self.token + nextchar
                        self.state = ' '
                        przerwij
                    inaczej:
                        self.state = 'a'
                albo_inaczej self.posix oraz nextchar w self.escape oraz \
                     self.state w self.escapedquotes:
                    escapedstate = self.state
                    self.state = nextchar
                inaczej:
                    self.token = self.token + nextchar
            albo_inaczej self.state w self.escape:
                jeżeli nie nextchar:      # end of file
                    jeżeli self.debug >= 2:
                        print("shlex: I see EOF w escape state")
                    # XXX what error should be podnieśd here?
                    podnieś ValueError("No escaped character")
                # In posix shells, only the quote itself albo the escape
                # character may be escaped within quotes.
                jeżeli escapedstate w self.quotes oraz \
                   nextchar != self.state oraz nextchar != escapedstate:
                    self.token = self.token + self.state
                self.token = self.token + nextchar
                self.state = escapedstate
            albo_inaczej self.state == 'a':
                jeżeli nie nextchar:
                    self.state = Nic   # end of file
                    przerwij
                albo_inaczej nextchar w self.whitespace:
                    jeżeli self.debug >= 2:
                        print("shlex: I see whitespace w word state")
                    self.state = ' '
                    jeżeli self.token albo (self.posix oraz quoted):
                        przerwij   # emit current token
                    inaczej:
                        kontynuuj
                albo_inaczej nextchar w self.commenters:
                    self.instream.readline()
                    self.lineno = self.lineno + 1
                    jeżeli self.posix:
                        self.state = ' '
                        jeżeli self.token albo (self.posix oraz quoted):
                            przerwij   # emit current token
                        inaczej:
                            kontynuuj
                albo_inaczej self.posix oraz nextchar w self.quotes:
                    self.state = nextchar
                albo_inaczej self.posix oraz nextchar w self.escape:
                    escapedstate = 'a'
                    self.state = nextchar
                albo_inaczej nextchar w self.wordchars albo nextchar w self.quotes \
                    albo self.whitespace_split:
                    self.token = self.token + nextchar
                inaczej:
                    self.pushback.appendleft(nextchar)
                    jeżeli self.debug >= 2:
                        print("shlex: I see punctuation w word state")
                    self.state = ' '
                    jeżeli self.token:
                        przerwij   # emit current token
                    inaczej:
                        kontynuuj
        result = self.token
        self.token = ''
        jeżeli self.posix oraz nie quoted oraz result == '':
            result = Nic
        jeżeli self.debug > 1:
            jeżeli result:
                print("shlex: raw token=" + repr(result))
            inaczej:
                print("shlex: raw token=EOF")
        zwróć result

    def sourcehook(self, newfile):
        "Hook called on a filename to be sourced."
        jeżeli newfile[0] == '"':
            newfile = newfile[1:-1]
        # This implements cpp-like semantics dla relative-path inclusion.
        jeżeli isinstance(self.infile, str) oraz nie os.path.isabs(newfile):
            newfile = os.path.join(os.path.dirname(self.infile), newfile)
        zwróć (newfile, open(newfile, "r"))

    def error_leader(self, infile=Nic, lineno=Nic):
        "Emit a C-compiler-like, Emacs-friendly error-message leader."
        jeżeli infile jest Nic:
            infile = self.infile
        jeżeli lineno jest Nic:
            lineno = self.lineno
        zwróć "\"%s\", line %d: " % (infile, lineno)

    def __iter__(self):
        zwróć self

    def __next__(self):
        token = self.get_token()
        jeżeli token == self.eof:
            podnieś StopIteration
        zwróć token

def split(s, comments=Nieprawda, posix=Prawda):
    lex = shlex(s, posix=posix)
    lex.whitespace_split = Prawda
    jeżeli nie comments:
        lex.commenters = ''
    zwróć list(lex)


_find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search

def quote(s):
    """Return a shell-escaped version of the string *s*."""
    jeżeli nie s:
        zwróć "''"
    jeżeli _find_unsafe(s) jest Nic:
        zwróć s

    # use single quotes, oraz put single quotes into double quotes
    # the string $'b jest then quoted jako '$'"'"'b'
    zwróć "'" + s.replace("'", "'\"'\"'") + "'"


def _print_tokens(lexer):
    dopóki 1:
        tt = lexer.get_token()
        jeżeli nie tt:
            przerwij
        print("Token: " + repr(tt))

jeżeli __name__ == '__main__':
    jeżeli len(sys.argv) == 1:
        _print_tokens(shlex())
    inaczej:
        fn = sys.argv[1]
        przy open(fn) jako f:
            _print_tokens(shlex(f, fn))
