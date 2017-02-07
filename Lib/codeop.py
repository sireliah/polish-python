r"""Utilities to compile possibly incomplete Python source code.

This module provides two interfaces, broadly similar to the builtin
function compile(), which take program text, a filename oraz a 'mode'
and:

- Return code object jeżeli the command jest complete oraz valid
- Return Nic jeżeli the command jest incomplete
- Raise SyntaxError, ValueError albo OverflowError jeżeli the command jest a
  syntax error (OverflowError oraz ValueError can be produced by
  malformed literals).

Approach:

First, check jeżeli the source consists entirely of blank lines oraz
comments; jeżeli so, replace it przy 'pass', because the built-in
parser doesn't always do the right thing dla these.

Compile three times: jako is, przy \n, oraz przy \n\n appended.  If it
compiles jako is, it's complete.  If it compiles przy one \n appended,
we expect more.  If it doesn't compile either way, we compare the
error we get when compiling przy \n albo \n\n appended.  If the errors
are the same, the code jest broken.  But jeżeli the errors are different, we
expect more.  Not intuitive; nie even guaranteed to hold w future
releases; but this matches the compiler's behavior z Python 1.4
through 2.2, at least.

Caveat:

It jest possible (but nie likely) that the parser stops parsing przy a
successful outcome before reaching the end of the source; w this
case, trailing symbols may be ignored instead of causing an error.
For example, a backslash followed by two newlines may be followed by
arbitrary garbage.  This will be fixed once the API dla the parser jest
better.

The two interfaces are:

compile_command(source, filename, symbol):

    Compiles a single command w the manner described above.

CommandCompiler():

    Instances of this klasa have __call__ methods identical w
    signature to compile_command; the difference jest that jeżeli the
    instance compiles program text containing a __future__ statement,
    the instance 'remembers' oraz compiles all subsequent program texts
    przy the statement w force.

The module also provides another class:

Compile():

    Instances of this klasa act like the built-in function compile,
    but przy 'memory' w the sense described above.
"""

zaimportuj __future__

_features = [getattr(__future__, fname)
             dla fname w __future__.all_feature_names]

__all__ = ["compile_command", "Compile", "CommandCompiler"]

PyCF_DONT_IMPLY_DEDENT = 0x200          # Matches pythonrun.h

def _maybe_compile(compiler, source, filename, symbol):
    # Check dla source consisting of only blank lines oraz comments
    dla line w source.split("\n"):
        line = line.strip()
        jeżeli line oraz line[0] != '#':
            przerwij               # Leave it alone
    inaczej:
        jeżeli symbol != "eval":
            source = "pass"     # Replace it przy a 'pass' statement

    err = err1 = err2 = Nic
    code = code1 = code2 = Nic

    spróbuj:
        code = compiler(source, filename, symbol)
    wyjąwszy SyntaxError jako err:
        dalej

    spróbuj:
        code1 = compiler(source + "\n", filename, symbol)
    wyjąwszy SyntaxError jako e:
        err1 = e

    spróbuj:
        code2 = compiler(source + "\n\n", filename, symbol)
    wyjąwszy SyntaxError jako e:
        err2 = e

    jeżeli code:
        zwróć code
    jeżeli nie code1 oraz repr(err1) == repr(err2):
        podnieś err1

def _compile(source, filename, symbol):
    zwróć compile(source, filename, symbol, PyCF_DONT_IMPLY_DEDENT)

def compile_command(source, filename="<input>", symbol="single"):
    r"""Compile a command oraz determine whether it jest incomplete.

    Arguments:

    source -- the source string; may contain \n characters
    filename -- optional filename z which source was read; default
                "<input>"
    symbol -- optional grammar start symbol; "single" (default) albo "eval"

    Return value / exceptions podnieśd:

    - Return a code object jeżeli the command jest complete oraz valid
    - Return Nic jeżeli the command jest incomplete
    - Raise SyntaxError, ValueError albo OverflowError jeżeli the command jest a
      syntax error (OverflowError oraz ValueError can be produced by
      malformed literals).
    """
    zwróć _maybe_compile(_compile, source, filename, symbol)

klasa Compile:
    """Instances of this klasa behave much like the built-in compile
    function, but jeżeli one jest used to compile text containing a future
    statement, it "remembers" oraz compiles all subsequent program texts
    przy the statement w force."""
    def __init__(self):
        self.flags = PyCF_DONT_IMPLY_DEDENT

    def __call__(self, source, filename, symbol):
        codeob = compile(source, filename, symbol, self.flags, 1)
        dla feature w _features:
            jeżeli codeob.co_flags & feature.compiler_flag:
                self.flags |= feature.compiler_flag
        zwróć codeob

klasa CommandCompiler:
    """Instances of this klasa have __call__ methods identical w
    signature to compile_command; the difference jest that jeżeli the
    instance compiles program text containing a __future__ statement,
    the instance 'remembers' oraz compiles all subsequent program texts
    przy the statement w force."""

    def __init__(self,):
        self.compiler = Compile()

    def __call__(self, source, filename="<input>", symbol="single"):
        r"""Compile a command oraz determine whether it jest incomplete.

        Arguments:

        source -- the source string; may contain \n characters
        filename -- optional filename z which source was read;
                    default "<input>"
        symbol -- optional grammar start symbol; "single" (default) albo
                  "eval"

        Return value / exceptions podnieśd:

        - Return a code object jeżeli the command jest complete oraz valid
        - Return Nic jeżeli the command jest incomplete
        - Raise SyntaxError, ValueError albo OverflowError jeżeli the command jest a
          syntax error (OverflowError oraz ValueError can be produced by
          malformed literals).
        """
        zwróć _maybe_compile(self.compiler, source, filename, symbol)
