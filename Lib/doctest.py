# Module doctest.
# Released to the public domain 16-Jan-2001, by Tim Peters (tim@python.org).
# Major enhancements oraz refactoring by:
#     Jim Fulton
#     Edward Loper

# Provided as-is; use at your own risk; no warranty; no promises; enjoy!

r"""Module doctest -- a framework dla running examples w docstrings.

In simplest use, end each module M to be tested with:

def _test():
    zaimportuj doctest
    doctest.testmod()

jeżeli __name__ == "__main__":
    _test()

Then running the module jako a script will cause the examples w the
docstrings to get executed oraz verified:

python M.py

This won't display anything unless an example fails, w which case the
failing example(s) oraz the cause(s) of the failure(s) are printed to stdout
(why nie stderr? because stderr jest a lame hack <0.2 wink>), oraz the final
line of output jest "Test failed.".

Run it przy the -v switch instead:

python M.py -v

and a detailed report of all examples tried jest printed to stdout, along
przy assorted summaries at the end.

You can force verbose mode by dalejing "verbose=Prawda" to testmod, albo prohibit
it by dalejing "verbose=Nieprawda".  In either of those cases, sys.argv jest nie
examined by testmod.

There are a variety of other ways to run doctests, including integration
przy the unittest framework, oraz support dla running non-Python text
files containing doctests.  There are also many ways to override parts
of doctest's default behaviors.  See the Library Reference Manual for
details.
"""

__docformat__ = 'reStructuredText en'

__all__ = [
    # 0, Option Flags
    'register_optionflag',
    'DONT_ACCEPT_TRUE_FOR_1',
    'DONT_ACCEPT_BLANKLINE',
    'NORMALIZE_WHITESPACE',
    'ELLIPSIS',
    'SKIP',
    'IGNORE_EXCEPTION_DETAIL',
    'COMPARISON_FLAGS',
    'REPORT_UDIFF',
    'REPORT_CDIFF',
    'REPORT_NDIFF',
    'REPORT_ONLY_FIRST_FAILURE',
    'REPORTING_FLAGS',
    'FAIL_FAST',
    # 1. Utility Functions
    # 2. Example & DocTest
    'Example',
    'DocTest',
    # 3. Doctest Parser
    'DocTestParser',
    # 4. Doctest Finder
    'DocTestFinder',
    # 5. Doctest Runner
    'DocTestRunner',
    'OutputChecker',
    'DocTestFailure',
    'UnexpectedException',
    'DebugRunner',
    # 6. Test Functions
    'testmod',
    'testfile',
    'run_docstring_examples',
    # 7. Unittest Support
    'DocTestSuite',
    'DocFileSuite',
    'set_unittest_reportflags',
    # 8. Debugging Support
    'script_from_examples',
    'testsource',
    'debug_src',
    'debug',
]

zaimportuj __future__
zaimportuj argparse
zaimportuj difflib
zaimportuj inspect
zaimportuj linecache
zaimportuj os
zaimportuj pdb
zaimportuj re
zaimportuj sys
zaimportuj traceback
zaimportuj unittest
z io zaimportuj StringIO
z collections zaimportuj namedtuple

TestResults = namedtuple('TestResults', 'failed attempted')

# There are 4 basic classes:
#  - Example: a <source, want> pair, plus an intra-docstring line number.
#  - DocTest: a collection of examples, parsed z a docstring, plus
#    info about where the docstring came z (name, filename, lineno).
#  - DocTestFinder: extracts DocTests z a given object's docstring oraz
#    its contained objects' docstrings.
#  - DocTestRunner: runs DocTest cases, oraz accumulates statistics.
#
# So the basic picture is:
#
#                             list of:
# +------+                   +---------+                   +-------+
# |object| --DocTestFinder-> | DocTest | --DocTestRunner-> |results|
# +------+                   +---------+                   +-------+
#                            | Example |
#                            |   ...   |
#                            | Example |
#                            +---------+

# Option constants.

OPTIONFLAGS_BY_NAME = {}
def register_optionflag(name):
    # Create a new flag unless `name` jest already known.
    zwróć OPTIONFLAGS_BY_NAME.setdefault(name, 1 << len(OPTIONFLAGS_BY_NAME))

DONT_ACCEPT_TRUE_FOR_1 = register_optionflag('DONT_ACCEPT_TRUE_FOR_1')
DONT_ACCEPT_BLANKLINE = register_optionflag('DONT_ACCEPT_BLANKLINE')
NORMALIZE_WHITESPACE = register_optionflag('NORMALIZE_WHITESPACE')
ELLIPSIS = register_optionflag('ELLIPSIS')
SKIP = register_optionflag('SKIP')
IGNORE_EXCEPTION_DETAIL = register_optionflag('IGNORE_EXCEPTION_DETAIL')

COMPARISON_FLAGS = (DONT_ACCEPT_TRUE_FOR_1 |
                    DONT_ACCEPT_BLANKLINE |
                    NORMALIZE_WHITESPACE |
                    ELLIPSIS |
                    SKIP |
                    IGNORE_EXCEPTION_DETAIL)

REPORT_UDIFF = register_optionflag('REPORT_UDIFF')
REPORT_CDIFF = register_optionflag('REPORT_CDIFF')
REPORT_NDIFF = register_optionflag('REPORT_NDIFF')
REPORT_ONLY_FIRST_FAILURE = register_optionflag('REPORT_ONLY_FIRST_FAILURE')
FAIL_FAST = register_optionflag('FAIL_FAST')

REPORTING_FLAGS = (REPORT_UDIFF |
                   REPORT_CDIFF |
                   REPORT_NDIFF |
                   REPORT_ONLY_FIRST_FAILURE |
                   FAIL_FAST)

# Special string markers dla use w `want` strings:
BLANKLINE_MARKER = '<BLANKLINE>'
ELLIPSIS_MARKER = '...'

######################################################################
## Table of Contents
######################################################################
#  1. Utility Functions
#  2. Example & DocTest -- store test cases
#  3. DocTest Parser -- extracts examples z strings
#  4. DocTest Finder -- extracts test cases z objects
#  5. DocTest Runner -- runs test cases
#  6. Test Functions -- convenient wrappers dla testing
#  7. Unittest Support
#  8. Debugging Support
#  9. Example Usage

######################################################################
## 1. Utility Functions
######################################################################

def _extract_future_flags(globs):
    """
    Return the compiler-flags associated przy the future features that
    have been imported into the given namespace (globs).
    """
    flags = 0
    dla fname w __future__.all_feature_names:
        feature = globs.get(fname, Nic)
        jeżeli feature jest getattr(__future__, fname):
            flags |= feature.compiler_flag
    zwróć flags

def _normalize_module(module, depth=2):
    """
    Return the module specified by `module`.  In particular:
      - If `module` jest a module, then zwróć module.
      - If `module` jest a string, then zaimportuj oraz zwróć the
        module przy that name.
      - If `module` jest Nic, then zwróć the calling module.
        The calling module jest assumed to be the module of
        the stack frame at the given depth w the call stack.
    """
    jeżeli inspect.ismodule(module):
        zwróć module
    albo_inaczej isinstance(module, str):
        zwróć __import__(module, globals(), locals(), ["*"])
    albo_inaczej module jest Nic:
        zwróć sys.modules[sys._getframe(depth).f_globals['__name__']]
    inaczej:
        podnieś TypeError("Expected a module, string, albo Nic")

def _load_testfile(filename, package, module_relative, encoding):
    jeżeli module_relative:
        package = _normalize_module(package, 3)
        filename = _module_relative_path(package, filename)
        jeżeli getattr(package, '__loader__', Nic) jest nie Nic:
            jeżeli hasattr(package.__loader__, 'get_data'):
                file_contents = package.__loader__.get_data(filename)
                file_contents = file_contents.decode(encoding)
                # get_data() opens files jako 'rb', so one must do the equivalent
                # conversion jako universal newlines would do.
                zwróć file_contents.replace(os.linesep, '\n'), filename
    przy open(filename, encoding=encoding) jako f:
        zwróć f.read(), filename

def _indent(s, indent=4):
    """
    Add the given number of space characters to the beginning of
    every non-blank line w `s`, oraz zwróć the result.
    """
    # This regexp matches the start of non-blank lines:
    zwróć re.sub('(?m)^(?!$)', indent*' ', s)

def _exception_traceback(exc_info):
    """
    Return a string containing a traceback message dla the given
    exc_info tuple (as returned by sys.exc_info()).
    """
    # Get a traceback message.
    excout = StringIO()
    exc_type, exc_val, exc_tb = exc_info
    traceback.print_exception(exc_type, exc_val, exc_tb, file=excout)
    zwróć excout.getvalue()

# Override some StringIO methods.
klasa _SpoofOut(StringIO):
    def getvalue(self):
        result = StringIO.getvalue(self)
        # If anything at all was written, make sure there's a trailing
        # newline.  There's no way dla the expected output to indicate
        # that a trailing newline jest missing.
        jeżeli result oraz nie result.endswith("\n"):
            result += "\n"
        zwróć result

    def truncate(self, size=Nic):
        self.seek(size)
        StringIO.truncate(self)

# Worst-case linear-time ellipsis matching.
def _ellipsis_match(want, got):
    """
    Essentially the only subtle case:
    >>> _ellipsis_match('aa...aa', 'aaa')
    Nieprawda
    """
    jeżeli ELLIPSIS_MARKER nie w want:
        zwróć want == got

    # Find "the real" strings.
    ws = want.split(ELLIPSIS_MARKER)
    assert len(ws) >= 2

    # Deal przy exact matches possibly needed at one albo both ends.
    startpos, endpos = 0, len(got)
    w = ws[0]
    jeżeli w:   # starts przy exact match
        jeżeli got.startswith(w):
            startpos = len(w)
            usuń ws[0]
        inaczej:
            zwróć Nieprawda
    w = ws[-1]
    jeżeli w:   # ends przy exact match
        jeżeli got.endswith(w):
            endpos -= len(w)
            usuń ws[-1]
        inaczej:
            zwróć Nieprawda

    jeżeli startpos > endpos:
        # Exact end matches required more characters than we have, jako w
        # _ellipsis_match('aa...aa', 'aaa')
        zwróć Nieprawda

    # For the rest, we only need to find the leftmost non-overlapping
    # match dla each piece.  If there's no overall match that way alone,
    # there's no overall match period.
    dla w w ws:
        # w may be '' at times, jeżeli there are consecutive ellipses, albo
        # due to an ellipsis at the start albo end of `want`.  That's OK.
        # Search dla an empty string succeeds, oraz doesn't change startpos.
        startpos = got.find(w, startpos, endpos)
        jeżeli startpos < 0:
            zwróć Nieprawda
        startpos += len(w)

    zwróć Prawda

def _comment_line(line):
    "Return a commented form of the given line"
    line = line.rstrip()
    jeżeli line:
        zwróć '# '+line
    inaczej:
        zwróć '#'

def _strip_exception_details(msg):
    # Support dla IGNORE_EXCEPTION_DETAIL.
    # Get rid of everything wyjąwszy the exception name; w particular, drop
    # the possibly dotted module path (jeżeli any) oraz the exception message (if
    # any).  We assume that a colon jest never part of a dotted name, albo of an
    # exception name.
    # E.g., given
    #    "foo.bar.MyError: la di da"
    # zwróć "MyError"
    # Or dla "abc.def" albo "abc.def:\n" zwróć "def".

    start, end = 0, len(msg)
    # The exception name must appear on the first line.
    i = msg.find("\n")
    jeżeli i >= 0:
        end = i
    # retain up to the first colon (jeżeli any)
    i = msg.find(':', 0, end)
    jeżeli i >= 0:
        end = i
    # retain just the exception name
    i = msg.rfind('.', 0, end)
    jeżeli i >= 0:
        start = i+1
    zwróć msg[start: end]

klasa _OutputRedirectingPdb(pdb.Pdb):
    """
    A specialized version of the python debugger that redirects stdout
    to a given stream when interacting przy the user.  Stdout jest *not*
    redirected when traced code jest executed.
    """
    def __init__(self, out):
        self.__out = out
        self.__debugger_used = Nieprawda
        # do nie play signal games w the pdb
        pdb.Pdb.__init__(self, stdout=out, nosigint=Prawda)
        # still use input() to get user input
        self.use_rawinput = 1

    def set_trace(self, frame=Nic):
        self.__debugger_used = Prawda
        jeżeli frame jest Nic:
            frame = sys._getframe().f_back
        pdb.Pdb.set_trace(self, frame)

    def set_continue(self):
        # Calling set_continue unconditionally would przerwij unit test
        # coverage reporting, jako Bdb.set_continue calls sys.settrace(Nic).
        jeżeli self.__debugger_used:
            pdb.Pdb.set_continue(self)

    def trace_dispatch(self, *args):
        # Redirect stdout to the given stream.
        save_stdout = sys.stdout
        sys.stdout = self.__out
        # Call Pdb's trace dispatch method.
        spróbuj:
            zwróć pdb.Pdb.trace_dispatch(self, *args)
        w_końcu:
            sys.stdout = save_stdout

# [XX] Normalize przy respect to os.path.pardir?
def _module_relative_path(module, path):
    jeżeli nie inspect.ismodule(module):
        podnieś TypeError('Expected a module: %r' % module)
    jeżeli path.startswith('/'):
        podnieś ValueError('Module-relative files may nie have absolute paths')

    # Find the base directory dla the path.
    jeżeli hasattr(module, '__file__'):
        # A normal module/package
        basedir = os.path.split(module.__file__)[0]
    albo_inaczej module.__name__ == '__main__':
        # An interactive session.
        jeżeli len(sys.argv)>0 oraz sys.argv[0] != '':
            basedir = os.path.split(sys.argv[0])[0]
        inaczej:
            basedir = os.curdir
    inaczej:
        # A module w/o __file__ (this includes builtins)
        podnieś ValueError("Can't resolve paths relative to the module " +
                         module + " (it has no __file__)")

    # Combine the base directory oraz the path.
    zwróć os.path.join(basedir, *(path.split('/')))

######################################################################
## 2. Example & DocTest
######################################################################
## - An "example" jest a <source, want> pair, where "source" jest a
##   fragment of source code, oraz "want" jest the expected output for
##   "source."  The Example klasa also includes information about
##   where the example was extracted from.
##
## - A "doctest" jest a collection of examples, typically extracted from
##   a string (such jako an object's docstring).  The DocTest klasa also
##   includes information about where the string was extracted from.

klasa Example:
    """
    A single doctest example, consisting of source code oraz expected
    output.  `Example` defines the following attributes:

      - source: A single Python statement, always ending przy a newline.
        The constructor adds a newline jeżeli needed.

      - want: The expected output z running the source code (either
        z stdout, albo a traceback w case of exception).  `want` ends
        przy a newline unless it's empty, w which case it's an empty
        string.  The constructor adds a newline jeżeli needed.

      - exc_msg: The exception message generated by the example, if
        the example jest expected to generate an exception; albo `Nic` if
        it jest nie expected to generate an exception.  This exception
        message jest compared against the zwróć value of
        `traceback.format_exception_only()`.  `exc_msg` ends przy a
        newline unless it's `Nic`.  The constructor adds a newline
        jeżeli needed.

      - lineno: The line number within the DocTest string containing
        this Example where the Example begins.  This line number jest
        zero-based, przy respect to the beginning of the DocTest.

      - indent: The example's indentation w the DocTest string.
        I.e., the number of space characters that precede the
        example's first prompt.

      - options: A dictionary mapping z option flags to Prawda albo
        Nieprawda, which jest used to override default options dla this
        example.  Any option flags nie contained w this dictionary
        are left at their default value (as specified by the
        DocTestRunner's optionflags).  By default, no options are set.
    """
    def __init__(self, source, want, exc_msg=Nic, lineno=0, indent=0,
                 options=Nic):
        # Normalize inputs.
        jeżeli nie source.endswith('\n'):
            source += '\n'
        jeżeli want oraz nie want.endswith('\n'):
            want += '\n'
        jeżeli exc_msg jest nie Nic oraz nie exc_msg.endswith('\n'):
            exc_msg += '\n'
        # Store properties.
        self.source = source
        self.want = want
        self.lineno = lineno
        self.indent = indent
        jeżeli options jest Nic: options = {}
        self.options = options
        self.exc_msg = exc_msg

    def __eq__(self, other):
        jeżeli type(self) jest nie type(other):
            zwróć NotImplemented

        zwróć self.source == other.source oraz \
               self.want == other.want oraz \
               self.lineno == other.lineno oraz \
               self.indent == other.indent oraz \
               self.options == other.options oraz \
               self.exc_msg == other.exc_msg

    def __hash__(self):
        zwróć hash((self.source, self.want, self.lineno, self.indent,
                     self.exc_msg))

klasa DocTest:
    """
    A collection of doctest examples that should be run w a single
    namespace.  Each `DocTest` defines the following attributes:

      - examples: the list of examples.

      - globs: The namespace (aka globals) that the examples should
        be run in.

      - name: A name identifying the DocTest (typically, the name of
        the object whose docstring this DocTest was extracted from).

      - filename: The name of the file that this DocTest was extracted
        from, albo `Nic` jeżeli the filename jest unknown.

      - lineno: The line number within filename where this DocTest
        begins, albo `Nic` jeżeli the line number jest unavailable.  This
        line number jest zero-based, przy respect to the beginning of
        the file.

      - docstring: The string that the examples were extracted from,
        albo `Nic` jeżeli the string jest unavailable.
    """
    def __init__(self, examples, globs, name, filename, lineno, docstring):
        """
        Create a new DocTest containing the given examples.  The
        DocTest's globals are initialized przy a copy of `globs`.
        """
        assert nie isinstance(examples, str), \
               "DocTest no longer accepts str; use DocTestParser instead"
        self.examples = examples
        self.docstring = docstring
        self.globs = globs.copy()
        self.name = name
        self.filename = filename
        self.lineno = lineno

    def __repr__(self):
        jeżeli len(self.examples) == 0:
            examples = 'no examples'
        albo_inaczej len(self.examples) == 1:
            examples = '1 example'
        inaczej:
            examples = '%d examples' % len(self.examples)
        zwróć ('<%s %s z %s:%s (%s)>' %
                (self.__class__.__name__,
                 self.name, self.filename, self.lineno, examples))

    def __eq__(self, other):
        jeżeli type(self) jest nie type(other):
            zwróć NotImplemented

        zwróć self.examples == other.examples oraz \
               self.docstring == other.docstring oraz \
               self.globs == other.globs oraz \
               self.name == other.name oraz \
               self.filename == other.filename oraz \
               self.lineno == other.lineno

    def __hash__(self):
        zwróć hash((self.docstring, self.name, self.filename, self.lineno))

    # This lets us sort tests by name:
    def __lt__(self, other):
        jeżeli nie isinstance(other, DocTest):
            zwróć NotImplemented
        zwróć ((self.name, self.filename, self.lineno, id(self))
                <
                (other.name, other.filename, other.lineno, id(other)))

######################################################################
## 3. DocTestParser
######################################################################

klasa DocTestParser:
    """
    A klasa used to parse strings containing doctest examples.
    """
    # This regular expression jest used to find doctest examples w a
    # string.  It defines three groups: `source` jest the source code
    # (including leading indentation oraz prompts); `indent` jest the
    # indentation of the first (PS1) line of the source code; oraz
    # `want` jest the expected output (including leading indentation).
    _EXAMPLE_RE = re.compile(r'''
        # Source consists of a PS1 line followed by zero albo more PS2 lines.
        (?P<source>
            (?:^(?P<indent> [ ]*) >>>    .*)    # PS1 line
            (?:\n           [ ]*  \.\.\. .*)*)  # PS2 lines
        \n?
        # Want consists of any non-blank lines that do nie start przy PS1.
        (?P<want> (?:(?![ ]*$)    # Not a blank line
                     (?![ ]*>>>)  # Not a line starting przy PS1
                     .+$\n?       # But any other line
                  )*)
        ''', re.MULTILINE | re.VERBOSE)

    # A regular expression dla handling `want` strings that contain
    # expected exceptions.  It divides `want` into three pieces:
    #    - the traceback header line (`hdr`)
    #    - the traceback stack (`stack`)
    #    - the exception message (`msg`), jako generated by
    #      traceback.format_exception_only()
    # `msg` may have multiple lines.  We assume/require that the
    # exception message jest the first non-indented line starting przy a word
    # character following the traceback header line.
    _EXCEPTION_RE = re.compile(r"""
        # Grab the traceback header.  Different versions of Python have
        # said different things on the first traceback line.
        ^(?P<hdr> Traceback\ \(
            (?: most\ recent\ call\ last
            |   innermost\ last
            ) \) :
        )
        \s* $                # toss trailing whitespace on the header.
        (?P<stack> .*?)      # don't blink: absorb stuff until...
        ^ (?P<msg> \w+ .*)   #     a line *starts* przy alphanum.
        """, re.VERBOSE | re.MULTILINE | re.DOTALL)

    # A callable returning a true value iff its argument jest a blank line
    # albo contains a single comment.
    _IS_BLANK_OR_COMMENT = re.compile(r'^[ ]*(#.*)?$').match

    def parse(self, string, name='<string>'):
        """
        Divide the given string into examples oraz intervening text,
        oraz zwróć them jako a list of alternating Examples oraz strings.
        Line numbers dla the Examples are 0-based.  The optional
        argument `name` jest a name identifying this string, oraz jest only
        used dla error messages.
        """
        string = string.expandtabs()
        # If all lines begin przy the same indentation, then strip it.
        min_indent = self._min_indent(string)
        jeżeli min_indent > 0:
            string = '\n'.join([l[min_indent:] dla l w string.split('\n')])

        output = []
        charno, lineno = 0, 0
        # Find all doctest examples w the string:
        dla m w self._EXAMPLE_RE.finditer(string):
            # Add the pre-example text to `output`.
            output.append(string[charno:m.start()])
            # Update lineno (lines before this example)
            lineno += string.count('\n', charno, m.start())
            # Extract info z the regexp match.
            (source, options, want, exc_msg) = \
                     self._parse_example(m, name, lineno)
            # Create an Example, oraz add it to the list.
            jeżeli nie self._IS_BLANK_OR_COMMENT(source):
                output.append( Example(source, want, exc_msg,
                                    lineno=lineno,
                                    indent=min_indent+len(m.group('indent')),
                                    options=options) )
            # Update lineno (lines inside this example)
            lineno += string.count('\n', m.start(), m.end())
            # Update charno.
            charno = m.end()
        # Add any remaining post-example text to `output`.
        output.append(string[charno:])
        zwróć output

    def get_doctest(self, string, globs, name, filename, lineno):
        """
        Extract all doctest examples z the given string, oraz
        collect them into a `DocTest` object.

        `globs`, `name`, `filename`, oraz `lineno` are attributes for
        the new `DocTest` object.  See the documentation dla `DocTest`
        dla more information.
        """
        zwróć DocTest(self.get_examples(string, name), globs,
                       name, filename, lineno, string)

    def get_examples(self, string, name='<string>'):
        """
        Extract all doctest examples z the given string, oraz zwróć
        them jako a list of `Example` objects.  Line numbers are
        0-based, because it's most common w doctests that nothing
        interesting appears on the same line jako opening triple-quote,
        oraz so the first interesting line jest called \"line 1\" then.

        The optional argument `name` jest a name identifying this
        string, oraz jest only used dla error messages.
        """
        zwróć [x dla x w self.parse(string, name)
                jeżeli isinstance(x, Example)]

    def _parse_example(self, m, name, lineno):
        """
        Given a regular expression match z `_EXAMPLE_RE` (`m`),
        zwróć a pair `(source, want)`, where `source` jest the matched
        example's source code (przy prompts oraz indentation stripped);
        oraz `want` jest the example's expected output (przy indentation
        stripped).

        `name` jest the string's name, oraz `lineno` jest the line number
        where the example starts; both are used dla error messages.
        """
        # Get the example's indentation level.
        indent = len(m.group('indent'))

        # Divide source into lines; check that they're properly
        # indented; oraz then strip their indentation & prompts.
        source_lines = m.group('source').split('\n')
        self._check_prompt_blank(source_lines, indent, name, lineno)
        self._check_prefix(source_lines[1:], ' '*indent + '.', name, lineno)
        source = '\n'.join([sl[indent+4:] dla sl w source_lines])

        # Divide want into lines; check that it's properly indented; oraz
        # then strip the indentation.  Spaces before the last newline should
        # be preserved, so plain rstrip() isn't good enough.
        want = m.group('want')
        want_lines = want.split('\n')
        jeżeli len(want_lines) > 1 oraz re.match(r' *$', want_lines[-1]):
            usuń want_lines[-1]  # forget final newline & spaces after it
        self._check_prefix(want_lines, ' '*indent, name,
                           lineno + len(source_lines))
        want = '\n'.join([wl[indent:] dla wl w want_lines])

        # If `want` contains a traceback message, then extract it.
        m = self._EXCEPTION_RE.match(want)
        jeżeli m:
            exc_msg = m.group('msg')
        inaczej:
            exc_msg = Nic

        # Extract options z the source.
        options = self._find_options(source, name, lineno)

        zwróć source, options, want, exc_msg

    # This regular expression looks dla option directives w the
    # source code of an example.  Option directives are comments
    # starting przy "doctest:".  Warning: this may give false
    # positives dla string-literals that contain the string
    # "#doctest:".  Eliminating these false positives would require
    # actually parsing the string; but we limit them by ignoring any
    # line containing "#doctest:" that jest *followed* by a quote mark.
    _OPTION_DIRECTIVE_RE = re.compile(r'#\s*doctest:\s*([^\n\'"]*)$',
                                      re.MULTILINE)

    def _find_options(self, source, name, lineno):
        """
        Return a dictionary containing option overrides extracted from
        option directives w the given source string.

        `name` jest the string's name, oraz `lineno` jest the line number
        where the example starts; both are used dla error messages.
        """
        options = {}
        # (niee: przy the current regexp, this will match at most once:)
        dla m w self._OPTION_DIRECTIVE_RE.finditer(source):
            option_strings = m.group(1).replace(',', ' ').split()
            dla option w option_strings:
                jeżeli (option[0] nie w '+-' albo
                    option[1:] nie w OPTIONFLAGS_BY_NAME):
                    podnieś ValueError('line %r of the doctest dla %s '
                                     'has an invalid option: %r' %
                                     (lineno+1, name, option))
                flag = OPTIONFLAGS_BY_NAME[option[1:]]
                options[flag] = (option[0] == '+')
        jeżeli options oraz self._IS_BLANK_OR_COMMENT(source):
            podnieś ValueError('line %r of the doctest dla %s has an option '
                             'directive on a line przy no example: %r' %
                             (lineno, name, source))
        zwróć options

    # This regular expression finds the indentation of every non-blank
    # line w a string.
    _INDENT_RE = re.compile('^([ ]*)(?=\S)', re.MULTILINE)

    def _min_indent(self, s):
        "Return the minimum indentation of any non-blank line w `s`"
        indents = [len(indent) dla indent w self._INDENT_RE.findall(s)]
        jeżeli len(indents) > 0:
            zwróć min(indents)
        inaczej:
            zwróć 0

    def _check_prompt_blank(self, lines, indent, name, lineno):
        """
        Given the lines of a source string (including prompts oraz
        leading indentation), check to make sure that every prompt jest
        followed by a space character.  If any line jest nie followed by
        a space character, then podnieś ValueError.
        """
        dla i, line w enumerate(lines):
            jeżeli len(line) >= indent+4 oraz line[indent+3] != ' ':
                podnieś ValueError('line %r of the docstring dla %s '
                                 'lacks blank after %s: %r' %
                                 (lineno+i+1, name,
                                  line[indent:indent+3], line))

    def _check_prefix(self, lines, prefix, name, lineno):
        """
        Check that every line w the given list starts przy the given
        prefix; jeżeli any line does not, then podnieś a ValueError.
        """
        dla i, line w enumerate(lines):
            jeżeli line oraz nie line.startswith(prefix):
                podnieś ValueError('line %r of the docstring dla %s has '
                                 'inconsistent leading whitespace: %r' %
                                 (lineno+i+1, name, line))


######################################################################
## 4. DocTest Finder
######################################################################

klasa DocTestFinder:
    """
    A klasa used to extract the DocTests that are relevant to a given
    object, z its docstring oraz the docstrings of its contained
    objects.  Doctests can currently be extracted z the following
    object types: modules, functions, classes, methods, staticmethods,
    classmethods, oraz properties.
    """

    def __init__(self, verbose=Nieprawda, parser=DocTestParser(),
                 recurse=Prawda, exclude_empty=Prawda):
        """
        Create a new doctest finder.

        The optional argument `parser` specifies a klasa albo
        function that should be used to create new DocTest objects (or
        objects that implement the same interface jako DocTest).  The
        signature dla this factory function should match the signature
        of the DocTest constructor.

        If the optional argument `recurse` jest false, then `find` will
        only examine the given object, oraz nie any contained objects.

        If the optional argument `exclude_empty` jest false, then `find`
        will include tests dla objects przy empty docstrings.
        """
        self._parser = parser
        self._verbose = verbose
        self._recurse = recurse
        self._exclude_empty = exclude_empty

    def find(self, obj, name=Nic, module=Nic, globs=Nic, extraglobs=Nic):
        """
        Return a list of the DocTests that are defined by the given
        object's docstring, albo by any of its contained objects'
        docstrings.

        The optional parameter `module` jest the module that contains
        the given object.  If the module jest nie specified albo jest Nic, then
        the test finder will attempt to automatically determine the
        correct module.  The object's module jest used:

            - As a default namespace, jeżeli `globs` jest nie specified.
            - To prevent the DocTestFinder z extracting DocTests
              z objects that are imported z other modules.
            - To find the name of the file containing the object.
            - To help find the line number of the object within its
              file.

        Contained objects whose module does nie match `module` are ignored.

        If `module` jest Nieprawda, no attempt to find the module will be made.
        This jest obscure, of use mostly w tests:  jeżeli `module` jest Nieprawda, albo
        jest Nic but cannot be found automatically, then all objects are
        considered to belong to the (non-existent) module, so all contained
        objects will (recursively) be searched dla doctests.

        The globals dla each DocTest jest formed by combining `globs`
        oraz `extraglobs` (bindings w `extraglobs` override bindings
        w `globs`).  A new copy of the globals dictionary jest created
        dla each DocTest.  If `globs` jest nie specified, then it
        defaults to the module's `__dict__`, jeżeli specified, albo {}
        otherwise.  If `extraglobs` jest nie specified, then it defaults
        to {}.

        """
        # If name was nie specified, then extract it z the object.
        jeżeli name jest Nic:
            name = getattr(obj, '__name__', Nic)
            jeżeli name jest Nic:
                podnieś ValueError("DocTestFinder.find: name must be given "
                        "when obj.__name__ doesn't exist: %r" %
                                 (type(obj),))

        # Find the module that contains the given object (jeżeli obj jest
        # a module, then module=obj.).  Note: this may fail, w which
        # case module will be Nic.
        jeżeli module jest Nieprawda:
            module = Nic
        albo_inaczej module jest Nic:
            module = inspect.getmodule(obj)

        # Read the module's source code.  This jest used by
        # DocTestFinder._find_lineno to find the line number dla a
        # given object's docstring.
        spróbuj:
            file = inspect.getsourcefile(obj)
        wyjąwszy TypeError:
            source_lines = Nic
        inaczej:
            jeżeli nie file:
                # Check to see jeżeli it's one of our special internal "files"
                # (see __patched_linecache_getlines).
                file = inspect.getfile(obj)
                jeżeli nie file[0]+file[-2:] == '<]>': file = Nic
            jeżeli file jest Nic:
                source_lines = Nic
            inaczej:
                jeżeli module jest nie Nic:
                    # Supply the module globals w case the module was
                    # originally loaded via a PEP 302 loader oraz
                    # file jest nie a valid filesystem path
                    source_lines = linecache.getlines(file, module.__dict__)
                inaczej:
                    # No access to a loader, so assume it's a normal
                    # filesystem path
                    source_lines = linecache.getlines(file)
                jeżeli nie source_lines:
                    source_lines = Nic

        # Initialize globals, oraz merge w extraglobs.
        jeżeli globs jest Nic:
            jeżeli module jest Nic:
                globs = {}
            inaczej:
                globs = module.__dict__.copy()
        inaczej:
            globs = globs.copy()
        jeżeli extraglobs jest nie Nic:
            globs.update(extraglobs)
        jeżeli '__name__' nie w globs:
            globs['__name__'] = '__main__'  # provide a default module name

        # Recursively explore `obj`, extracting DocTests.
        tests = []
        self._find(tests, obj, name, module, source_lines, globs, {})
        # Sort the tests by alpha order of names, dla consistency w
        # verbose-mode output.  This was a feature of doctest w Pythons
        # <= 2.3 that got lost by accident w 2.4.  It was repaired w
        # 2.4.4 oraz 2.5.
        tests.sort()
        zwróć tests

    def _from_module(self, module, object):
        """
        Return true jeżeli the given object jest defined w the given
        module.
        """
        jeżeli module jest Nic:
            zwróć Prawda
        albo_inaczej inspect.getmodule(object) jest nie Nic:
            zwróć module jest inspect.getmodule(object)
        albo_inaczej inspect.isfunction(object):
            zwróć module.__dict__ jest object.__globals__
        albo_inaczej inspect.ismethoddescriptor(object):
            jeżeli hasattr(object, '__objclass__'):
                obj_mod = object.__objclass__.__module__
            albo_inaczej hasattr(object, '__module__'):
                obj_mod = object.__module__
            inaczej:
                zwróć Prawda # [XX] no easy way to tell otherwise
            zwróć module.__name__ == obj_mod
        albo_inaczej inspect.isclass(object):
            zwróć module.__name__ == object.__module__
        albo_inaczej hasattr(object, '__module__'):
            zwróć module.__name__ == object.__module__
        albo_inaczej isinstance(object, property):
            zwróć Prawda # [XX] no way nie be sure.
        inaczej:
            podnieś ValueError("object must be a klasa albo function")

    def _find(self, tests, obj, name, module, source_lines, globs, seen):
        """
        Find tests dla the given object oraz any contained objects, oraz
        add them to `tests`.
        """
        jeżeli self._verbose:
            print('Finding tests w %s' % name)

        # If we've already processed this object, then ignore it.
        jeżeli id(obj) w seen:
            zwróć
        seen[id(obj)] = 1

        # Find a test dla this object, oraz add it to the list of tests.
        test = self._get_test(obj, name, module, globs, source_lines)
        jeżeli test jest nie Nic:
            tests.append(test)

        # Look dla tests w a module's contained objects.
        jeżeli inspect.ismodule(obj) oraz self._recurse:
            dla valname, val w obj.__dict__.items():
                valname = '%s.%s' % (name, valname)
                # Recurse to functions & classes.
                jeżeli ((inspect.isroutine(inspect.unwrap(val))
                     albo inspect.isclass(val)) oraz
                    self._from_module(module, val)):
                    self._find(tests, val, valname, module, source_lines,
                               globs, seen)

        # Look dla tests w a module's __test__ dictionary.
        jeżeli inspect.ismodule(obj) oraz self._recurse:
            dla valname, val w getattr(obj, '__test__', {}).items():
                jeżeli nie isinstance(valname, str):
                    podnieś ValueError("DocTestFinder.find: __test__ keys "
                                     "must be strings: %r" %
                                     (type(valname),))
                jeżeli nie (inspect.isroutine(val) albo inspect.isclass(val) albo
                        inspect.ismodule(val) albo isinstance(val, str)):
                    podnieś ValueError("DocTestFinder.find: __test__ values "
                                     "must be strings, functions, methods, "
                                     "classes, albo modules: %r" %
                                     (type(val),))
                valname = '%s.__test__.%s' % (name, valname)
                self._find(tests, val, valname, module, source_lines,
                           globs, seen)

        # Look dla tests w a class's contained objects.
        jeżeli inspect.isclass(obj) oraz self._recurse:
            dla valname, val w obj.__dict__.items():
                # Special handling dla staticmethod/classmethod.
                jeżeli isinstance(val, staticmethod):
                    val = getattr(obj, valname)
                jeżeli isinstance(val, classmethod):
                    val = getattr(obj, valname).__func__

                # Recurse to methods, properties, oraz nested classes.
                jeżeli ((inspect.isroutine(val) albo inspect.isclass(val) albo
                      isinstance(val, property)) oraz
                      self._from_module(module, val)):
                    valname = '%s.%s' % (name, valname)
                    self._find(tests, val, valname, module, source_lines,
                               globs, seen)

    def _get_test(self, obj, name, module, globs, source_lines):
        """
        Return a DocTest dla the given object, jeżeli it defines a docstring;
        otherwise, zwróć Nic.
        """
        # Extract the object's docstring.  If it doesn't have one,
        # then zwróć Nic (no test dla this object).
        jeżeli isinstance(obj, str):
            docstring = obj
        inaczej:
            spróbuj:
                jeżeli obj.__doc__ jest Nic:
                    docstring = ''
                inaczej:
                    docstring = obj.__doc__
                    jeżeli nie isinstance(docstring, str):
                        docstring = str(docstring)
            wyjąwszy (TypeError, AttributeError):
                docstring = ''

        # Find the docstring's location w the file.
        lineno = self._find_lineno(obj, source_lines)

        # Don't bother jeżeli the docstring jest empty.
        jeżeli self._exclude_empty oraz nie docstring:
            zwróć Nic

        # Return a DocTest dla this object.
        jeżeli module jest Nic:
            filename = Nic
        inaczej:
            filename = getattr(module, '__file__', module.__name__)
            jeżeli filename[-4:] == ".pyc":
                filename = filename[:-1]
        zwróć self._parser.get_doctest(docstring, globs, name,
                                        filename, lineno)

    def _find_lineno(self, obj, source_lines):
        """
        Return a line number of the given object's docstring.  Note:
        this method assumes that the object has a docstring.
        """
        lineno = Nic

        # Find the line number dla modules.
        jeżeli inspect.ismodule(obj):
            lineno = 0

        # Find the line number dla classes.
        # Note: this could be fooled jeżeli a klasa jest defined multiple
        # times w a single file.
        jeżeli inspect.isclass(obj):
            jeżeli source_lines jest Nic:
                zwróć Nic
            pat = re.compile(r'^\s*class\s*%s\b' %
                             getattr(obj, '__name__', '-'))
            dla i, line w enumerate(source_lines):
                jeżeli pat.match(line):
                    lineno = i
                    przerwij

        # Find the line number dla functions & methods.
        jeżeli inspect.ismethod(obj): obj = obj.__func__
        jeżeli inspect.isfunction(obj): obj = obj.__code__
        jeżeli inspect.istraceback(obj): obj = obj.tb_frame
        jeżeli inspect.isframe(obj): obj = obj.f_code
        jeżeli inspect.iscode(obj):
            lineno = getattr(obj, 'co_firstlineno', Nic)-1

        # Find the line number where the docstring starts.  Assume
        # that it's the first line that begins przy a quote mark.
        # Note: this could be fooled by a multiline function
        # signature, where a continuation line begins przy a quote
        # mark.
        jeżeli lineno jest nie Nic:
            jeżeli source_lines jest Nic:
                zwróć lineno+1
            pat = re.compile('(^|.*:)\s*\w*("|\')')
            dla lineno w range(lineno, len(source_lines)):
                jeżeli pat.match(source_lines[lineno]):
                    zwróć lineno

        # We couldn't find the line number.
        zwróć Nic

######################################################################
## 5. DocTest Runner
######################################################################

klasa DocTestRunner:
    """
    A klasa used to run DocTest test cases, oraz accumulate statistics.
    The `run` method jest used to process a single DocTest case.  It
    returns a tuple `(f, t)`, where `t` jest the number of test cases
    tried, oraz `f` jest the number of test cases that failed.

        >>> tests = DocTestFinder().find(_TestClass)
        >>> runner = DocTestRunner(verbose=Nieprawda)
        >>> tests.sort(key = lambda test: test.name)
        >>> dla test w tests:
        ...     print(test.name, '->', runner.run(test))
        _TestClass -> TestResults(failed=0, attempted=2)
        _TestClass.__init__ -> TestResults(failed=0, attempted=2)
        _TestClass.get -> TestResults(failed=0, attempted=2)
        _TestClass.square -> TestResults(failed=0, attempted=1)

    The `summarize` method prints a summary of all the test cases that
    have been run by the runner, oraz returns an aggregated `(f, t)`
    tuple:

        >>> runner.summarize(verbose=1)
        4 items dalejed all tests:
           2 tests w _TestClass
           2 tests w _TestClass.__init__
           2 tests w _TestClass.get
           1 tests w _TestClass.square
        7 tests w 4 items.
        7 dalejed oraz 0 failed.
        Test dalejed.
        TestResults(failed=0, attempted=7)

    The aggregated number of tried examples oraz failed examples jest
    also available via the `tries` oraz `failures` attributes:

        >>> runner.tries
        7
        >>> runner.failures
        0

    The comparison between expected outputs oraz actual outputs jest done
    by an `OutputChecker`.  This comparison may be customized przy a
    number of option flags; see the documentation dla `testmod` for
    more information.  If the option flags are insufficient, then the
    comparison may also be customized by dalejing a subclass of
    `OutputChecker` to the constructor.

    The test runner's display output can be controlled w two ways.
    First, an output function (`out) can be dalejed to
    `TestRunner.run`; this function will be called przy strings that
    should be displayed.  It defaults to `sys.stdout.write`.  If
    capturing the output jest nie sufficient, then the display output
    can be also customized by subclassing DocTestRunner, oraz
    overriding the methods `report_start`, `report_success`,
    `report_unexpected_exception`, oraz `report_failure`.
    """
    # This divider string jest used to separate failure messages, oraz to
    # separate sections of the summary.
    DIVIDER = "*" * 70

    def __init__(self, checker=Nic, verbose=Nic, optionflags=0):
        """
        Create a new test runner.

        Optional keyword arg `checker` jest the `OutputChecker` that
        should be used to compare the expected outputs oraz actual
        outputs of doctest examples.

        Optional keyword arg 'verbose' prints lots of stuff jeżeli true,
        only failures jeżeli false; by default, it's true iff '-v' jest w
        sys.argv.

        Optional argument `optionflags` can be used to control how the
        test runner compares expected output to actual output, oraz how
        it displays failures.  See the documentation dla `testmod` for
        more information.
        """
        self._checker = checker albo OutputChecker()
        jeżeli verbose jest Nic:
            verbose = '-v' w sys.argv
        self._verbose = verbose
        self.optionflags = optionflags
        self.original_optionflags = optionflags

        # Keep track of the examples we've run.
        self.tries = 0
        self.failures = 0
        self._name2ft = {}

        # Create a fake output target dla capturing doctest output.
        self._fakeout = _SpoofOut()

    #/////////////////////////////////////////////////////////////////
    # Reporting methods
    #/////////////////////////////////////////////////////////////////

    def report_start(self, out, test, example):
        """
        Report that the test runner jest about to process the given
        example.  (Only displays a message jeżeli verbose=Prawda)
        """
        jeżeli self._verbose:
            jeżeli example.want:
                out('Trying:\n' + _indent(example.source) +
                    'Expecting:\n' + _indent(example.want))
            inaczej:
                out('Trying:\n' + _indent(example.source) +
                    'Expecting nothing\n')

    def report_success(self, out, test, example, got):
        """
        Report that the given example ran successfully.  (Only
        displays a message jeżeli verbose=Prawda)
        """
        jeżeli self._verbose:
            out("ok\n")

    def report_failure(self, out, test, example, got):
        """
        Report that the given example failed.
        """
        out(self._failure_header(test, example) +
            self._checker.output_difference(example, got, self.optionflags))

    def report_unexpected_exception(self, out, test, example, exc_info):
        """
        Report that the given example podnieśd an unexpected exception.
        """
        out(self._failure_header(test, example) +
            'Exception podnieśd:\n' + _indent(_exception_traceback(exc_info)))

    def _failure_header(self, test, example):
        out = [self.DIVIDER]
        jeżeli test.filename:
            jeżeli test.lineno jest nie Nic oraz example.lineno jest nie Nic:
                lineno = test.lineno + example.lineno + 1
            inaczej:
                lineno = '?'
            out.append('File "%s", line %s, w %s' %
                       (test.filename, lineno, test.name))
        inaczej:
            out.append('Line %s, w %s' % (example.lineno+1, test.name))
        out.append('Failed example:')
        source = example.source
        out.append(_indent(source))
        zwróć '\n'.join(out)

    #/////////////////////////////////////////////////////////////////
    # DocTest Running
    #/////////////////////////////////////////////////////////////////

    def __run(self, test, compileflags, out):
        """
        Run the examples w `test`.  Write the outcome of each example
        przy one of the `DocTestRunner.report_*` methods, using the
        writer function `out`.  `compileflags` jest the set of compiler
        flags that should be used to execute examples.  Return a tuple
        `(f, t)`, where `t` jest the number of examples tried, oraz `f`
        jest the number of examples that failed.  The examples are run
        w the namespace `test.globs`.
        """
        # Keep track of the number of failures oraz tries.
        failures = tries = 0

        # Save the option flags (since option directives can be used
        # to modify them).
        original_optionflags = self.optionflags

        SUCCESS, FAILURE, BOOM = range(3) # `outcome` state

        check = self._checker.check_output

        # Process each example.
        dla examplenum, example w enumerate(test.examples):

            # If REPORT_ONLY_FIRST_FAILURE jest set, then suppress
            # reporting after the first failure.
            quiet = (self.optionflags & REPORT_ONLY_FIRST_FAILURE oraz
                     failures > 0)

            # Merge w the example's options.
            self.optionflags = original_optionflags
            jeżeli example.options:
                dla (optionflag, val) w example.options.items():
                    jeżeli val:
                        self.optionflags |= optionflag
                    inaczej:
                        self.optionflags &= ~optionflag

            # If 'SKIP' jest set, then skip this example.
            jeżeli self.optionflags & SKIP:
                kontynuuj

            # Record that we started this example.
            tries += 1
            jeżeli nie quiet:
                self.report_start(out, test, example)

            # Use a special filename dla compile(), so we can retrieve
            # the source code during interactive debugging (see
            # __patched_linecache_getlines).
            filename = '<doctest %s[%d]>' % (test.name, examplenum)

            # Run the example w the given context (globs), oraz record
            # any exception that gets podnieśd.  (But don't intercept
            # keyboard interrupts.)
            spróbuj:
                # Don't blink!  This jest where the user's code gets run.
                exec(compile(example.source, filename, "single",
                             compileflags, 1), test.globs)
                self.debugger.set_continue() # ==== Example Finished ====
                exception = Nic
            wyjąwszy KeyboardInterrupt:
                podnieś
            wyjąwszy:
                exception = sys.exc_info()
                self.debugger.set_continue() # ==== Example Finished ====

            got = self._fakeout.getvalue()  # the actual output
            self._fakeout.truncate(0)
            outcome = FAILURE   # guilty until proved innocent albo insane

            # If the example executed without raising any exceptions,
            # verify its output.
            jeżeli exception jest Nic:
                jeżeli check(example.want, got, self.optionflags):
                    outcome = SUCCESS

            # The example podnieśd an exception:  check jeżeli it was expected.
            inaczej:
                exc_msg = traceback.format_exception_only(*exception[:2])[-1]
                jeżeli nie quiet:
                    got += _exception_traceback(exception)

                # If `example.exc_msg` jest Nic, then we weren't expecting
                # an exception.
                jeżeli example.exc_msg jest Nic:
                    outcome = BOOM

                # We expected an exception:  see whether it matches.
                albo_inaczej check(example.exc_msg, exc_msg, self.optionflags):
                    outcome = SUCCESS

                # Another chance jeżeli they didn't care about the detail.
                albo_inaczej self.optionflags & IGNORE_EXCEPTION_DETAIL:
                    jeżeli check(_strip_exception_details(example.exc_msg),
                             _strip_exception_details(exc_msg),
                             self.optionflags):
                        outcome = SUCCESS

            # Report the outcome.
            jeżeli outcome jest SUCCESS:
                jeżeli nie quiet:
                    self.report_success(out, test, example, got)
            albo_inaczej outcome jest FAILURE:
                jeżeli nie quiet:
                    self.report_failure(out, test, example, got)
                failures += 1
            albo_inaczej outcome jest BOOM:
                jeżeli nie quiet:
                    self.report_unexpected_exception(out, test, example,
                                                     exception)
                failures += 1
            inaczej:
                assert Nieprawda, ("unknown outcome", outcome)

            jeżeli failures oraz self.optionflags & FAIL_FAST:
                przerwij

        # Restore the option flags (in case they were modified)
        self.optionflags = original_optionflags

        # Record oraz zwróć the number of failures oraz tries.
        self.__record_outcome(test, failures, tries)
        zwróć TestResults(failures, tries)

    def __record_outcome(self, test, f, t):
        """
        Record the fact that the given DocTest (`test`) generated `f`
        failures out of `t` tried examples.
        """
        f2, t2 = self._name2ft.get(test.name, (0,0))
        self._name2ft[test.name] = (f+f2, t+t2)
        self.failures += f
        self.tries += t

    __LINECACHE_FILENAME_RE = re.compile(r'<doctest '
                                         r'(?P<name>.+)'
                                         r'\[(?P<examplenum>\d+)\]>$')
    def __patched_linecache_getlines(self, filename, module_globals=Nic):
        m = self.__LINECACHE_FILENAME_RE.match(filename)
        jeżeli m oraz m.group('name') == self.test.name:
            example = self.test.examples[int(m.group('examplenum'))]
            zwróć example.source.splitlines(keepends=Prawda)
        inaczej:
            zwróć self.save_linecache_getlines(filename, module_globals)

    def run(self, test, compileflags=Nic, out=Nic, clear_globs=Prawda):
        """
        Run the examples w `test`, oraz display the results using the
        writer function `out`.

        The examples are run w the namespace `test.globs`.  If
        `clear_globs` jest true (the default), then this namespace will
        be cleared after the test runs, to help przy garbage
        collection.  If you would like to examine the namespace after
        the test completes, then use `clear_globs=Nieprawda`.

        `compileflags` gives the set of flags that should be used by
        the Python compiler when running the examples.  If nie
        specified, then it will default to the set of future-import
        flags that apply to `globs`.

        The output of each example jest checked using
        `DocTestRunner.check_output`, oraz the results are formatted by
        the `DocTestRunner.report_*` methods.
        """
        self.test = test

        jeżeli compileflags jest Nic:
            compileflags = _extract_future_flags(test.globs)

        save_stdout = sys.stdout
        jeżeli out jest Nic:
            encoding = save_stdout.encoding
            jeżeli encoding jest Nic albo encoding.lower() == 'utf-8':
                out = save_stdout.write
            inaczej:
                # Use backslashreplace error handling on write
                def out(s):
                    s = str(s.encode(encoding, 'backslashreplace'), encoding)
                    save_stdout.write(s)
        sys.stdout = self._fakeout

        # Patch pdb.set_trace to restore sys.stdout during interactive
        # debugging (so it's nie still redirected to self._fakeout).
        # Note that the interactive output will go to *our*
        # save_stdout, even jeżeli that's nie the real sys.stdout; this
        # allows us to write test cases dla the set_trace behavior.
        save_trace = sys.gettrace()
        save_set_trace = pdb.set_trace
        self.debugger = _OutputRedirectingPdb(save_stdout)
        self.debugger.reset()
        pdb.set_trace = self.debugger.set_trace

        # Patch linecache.getlines, so we can see the example's source
        # when we're inside the debugger.
        self.save_linecache_getlines = linecache.getlines
        linecache.getlines = self.__patched_linecache_getlines

        # Make sure sys.displayhook just prints the value to stdout
        save_displayhook = sys.displayhook
        sys.displayhook = sys.__displayhook__

        spróbuj:
            zwróć self.__run(test, compileflags, out)
        w_końcu:
            sys.stdout = save_stdout
            pdb.set_trace = save_set_trace
            sys.settrace(save_trace)
            linecache.getlines = self.save_linecache_getlines
            sys.displayhook = save_displayhook
            jeżeli clear_globs:
                test.globs.clear()
                zaimportuj builtins
                builtins._ = Nic

    #/////////////////////////////////////////////////////////////////
    # Summarization
    #/////////////////////////////////////////////////////////////////
    def summarize(self, verbose=Nic):
        """
        Print a summary of all the test cases that have been run by
        this DocTestRunner, oraz zwróć a tuple `(f, t)`, where `f` jest
        the total number of failed examples, oraz `t` jest the total
        number of tried examples.

        The optional `verbose` argument controls how detailed the
        summary is.  If the verbosity jest nie specified, then the
        DocTestRunner's verbosity jest used.
        """
        jeżeli verbose jest Nic:
            verbose = self._verbose
        notests = []
        dalejed = []
        failed = []
        totalt = totalf = 0
        dla x w self._name2ft.items():
            name, (f, t) = x
            assert f <= t
            totalt += t
            totalf += f
            jeżeli t == 0:
                notests.append(name)
            albo_inaczej f == 0:
                dalejed.append( (name, t) )
            inaczej:
                failed.append(x)
        jeżeli verbose:
            jeżeli notests:
                print(len(nieests), "items had no tests:")
                notests.sort()
                dla thing w notests:
                    print("   ", thing)
            jeżeli dalejed:
                print(len(passed), "items dalejed all tests:")
                dalejed.sort()
                dla thing, count w dalejed:
                    print(" %3d tests w %s" % (count, thing))
        jeżeli failed:
            print(self.DIVIDER)
            print(len(failed), "items had failures:")
            failed.sort()
            dla thing, (f, t) w failed:
                print(" %3d of %3d w %s" % (f, t, thing))
        jeżeli verbose:
            print(totalt, "tests in", len(self._name2ft), "items.")
            print(totalt - totalf, "passed and", totalf, "failed.")
        jeżeli totalf:
            print("***Test Failed***", totalf, "failures.")
        albo_inaczej verbose:
            print("Test dalejed.")
        zwróć TestResults(totalf, totalt)

    #/////////////////////////////////////////////////////////////////
    # Backward compatibility cruft to maintain doctest.master.
    #/////////////////////////////////////////////////////////////////
    def merge(self, other):
        d = self._name2ft
        dla name, (f, t) w other._name2ft.items():
            jeżeli name w d:
                # Don't print here by default, since doing
                #     so przerwijs some of the buildbots
                #print("*** DocTestRunner.merge: '" + name + "' w both" \
                #    " testers; summing outcomes.")
                f2, t2 = d[name]
                f = f + f2
                t = t + t2
            d[name] = f, t

klasa OutputChecker:
    """
    A klasa used to check the whether the actual output z a doctest
    example matches the expected output.  `OutputChecker` defines two
    methods: `check_output`, which compares a given pair of outputs,
    oraz returns true jeżeli they match; oraz `output_difference`, which
    returns a string describing the differences between two outputs.
    """
    def _toAscii(self, s):
        """
        Convert string to hex-escaped ASCII string.
        """
        zwróć str(s.encode('ASCII', 'backslashreplace'), "ASCII")

    def check_output(self, want, got, optionflags):
        """
        Return Prawda iff the actual output z an example (`got`)
        matches the expected output (`want`).  These strings are
        always considered to match jeżeli they are identical; but
        depending on what option flags the test runner jest using,
        several non-exact match types are also possible.  See the
        documentation dla `TestRunner` dla more information about
        option flags.
        """

        # If `want` contains hex-escaped character such jako "\u1234",
        # then `want` jest a string of six characters(e.g. [\,u,1,2,3,4]).
        # On the other hand, `got` could be an another sequence of
        # characters such jako [\u1234], so `want` oraz `got` should
        # be folded to hex-escaped ASCII string to compare.
        got = self._toAscii(got)
        want = self._toAscii(want)

        # Handle the common case first, dla efficiency:
        # jeżeli they're string-identical, always zwróć true.
        jeżeli got == want:
            zwróć Prawda

        # The values Prawda oraz Nieprawda replaced 1 oraz 0 jako the zwróć
        # value dla boolean comparisons w Python 2.3.
        jeżeli nie (optionflags & DONT_ACCEPT_TRUE_FOR_1):
            jeżeli (got,want) == ("Prawda\n", "1\n"):
                zwróć Prawda
            jeżeli (got,want) == ("Nieprawda\n", "0\n"):
                zwróć Prawda

        # <BLANKLINE> can be used jako a special sequence to signify a
        # blank line, unless the DONT_ACCEPT_BLANKLINE flag jest used.
        jeżeli nie (optionflags & DONT_ACCEPT_BLANKLINE):
            # Replace <BLANKLINE> w want przy a blank line.
            want = re.sub('(?m)^%s\s*?$' % re.escape(BLANKLINE_MARKER),
                          '', want)
            # If a line w got contains only spaces, then remove the
            # spaces.
            got = re.sub('(?m)^\s*?$', '', got)
            jeżeli got == want:
                zwróć Prawda

        # This flag causes doctest to ignore any differences w the
        # contents of whitespace strings.  Note that this can be used
        # w conjunction przy the ELLIPSIS flag.
        jeżeli optionflags & NORMALIZE_WHITESPACE:
            got = ' '.join(got.split())
            want = ' '.join(want.split())
            jeżeli got == want:
                zwróć Prawda

        # The ELLIPSIS flag says to let the sequence "..." w `want`
        # match any substring w `got`.
        jeżeli optionflags & ELLIPSIS:
            jeżeli _ellipsis_match(want, got):
                zwróć Prawda

        # We didn't find any match; zwróć false.
        zwróć Nieprawda

    # Should we do a fancy diff?
    def _do_a_fancy_diff(self, want, got, optionflags):
        # Not unless they asked dla a fancy diff.
        jeżeli nie optionflags & (REPORT_UDIFF |
                              REPORT_CDIFF |
                              REPORT_NDIFF):
            zwróć Nieprawda

        # If expected output uses ellipsis, a meaningful fancy diff jest
        # too hard ... albo maybe not.  In two real-life failures Tim saw,
        # a diff was a major help anyway, so this jest commented out.
        # [todo] _ellipsis_match() knows which pieces do oraz don't match,
        # oraz could be the basis dla a kick-ass diff w this case.
        ##jeżeli optionflags & ELLIPSIS oraz ELLIPSIS_MARKER w want:
        ##    zwróć Nieprawda

        # ndiff does intraline difference marking, so can be useful even
        # dla 1-line differences.
        jeżeli optionflags & REPORT_NDIFF:
            zwróć Prawda

        # The other diff types need at least a few lines to be helpful.
        zwróć want.count('\n') > 2 oraz got.count('\n') > 2

    def output_difference(self, example, got, optionflags):
        """
        Return a string describing the differences between the
        expected output dla a given example (`example`) oraz the actual
        output (`got`).  `optionflags` jest the set of option flags used
        to compare `want` oraz `got`.
        """
        want = example.want
        # If <BLANKLINE>s are being used, then replace blank lines
        # przy <BLANKLINE> w the actual output string.
        jeżeli nie (optionflags & DONT_ACCEPT_BLANKLINE):
            got = re.sub('(?m)^[ ]*(?=\n)', BLANKLINE_MARKER, got)

        # Check jeżeli we should use diff.
        jeżeli self._do_a_fancy_diff(want, got, optionflags):
            # Split want & got into lines.
            want_lines = want.splitlines(keepends=Prawda)
            got_lines = got.splitlines(keepends=Prawda)
            # Use difflib to find their differences.
            jeżeli optionflags & REPORT_UDIFF:
                diff = difflib.unified_diff(want_lines, got_lines, n=2)
                diff = list(diff)[2:] # strip the diff header
                kind = 'unified diff przy -expected +actual'
            albo_inaczej optionflags & REPORT_CDIFF:
                diff = difflib.context_diff(want_lines, got_lines, n=2)
                diff = list(diff)[2:] # strip the diff header
                kind = 'context diff przy expected followed by actual'
            albo_inaczej optionflags & REPORT_NDIFF:
                engine = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
                diff = list(engine.compare(want_lines, got_lines))
                kind = 'ndiff przy -expected +actual'
            inaczej:
                assert 0, 'Bad diff option'
            # Remove trailing whitespace on diff output.
            diff = [line.rstrip() + '\n' dla line w diff]
            zwróć 'Differences (%s):\n' % kind + _indent(''.join(diff))

        # If we're nie using diff, then simply list the expected
        # output followed by the actual output.
        jeżeli want oraz got:
            zwróć 'Expected:\n%sGot:\n%s' % (_indent(want), _indent(got))
        albo_inaczej want:
            zwróć 'Expected:\n%sGot nothing\n' % _indent(want)
        albo_inaczej got:
            zwróć 'Expected nothing\nGot:\n%s' % _indent(got)
        inaczej:
            zwróć 'Expected nothing\nGot nothing\n'

klasa DocTestFailure(Exception):
    """A DocTest example has failed w debugging mode.

    The exception instance has variables:

    - test: the DocTest object being run

    - example: the Example object that failed

    - got: the actual output
    """
    def __init__(self, test, example, got):
        self.test = test
        self.example = example
        self.got = got

    def __str__(self):
        zwróć str(self.test)

klasa UnexpectedException(Exception):
    """A DocTest example has encountered an unexpected exception

    The exception instance has variables:

    - test: the DocTest object being run

    - example: the Example object that failed

    - exc_info: the exception info
    """
    def __init__(self, test, example, exc_info):
        self.test = test
        self.example = example
        self.exc_info = exc_info

    def __str__(self):
        zwróć str(self.test)

klasa DebugRunner(DocTestRunner):
    r"""Run doc tests but podnieś an exception jako soon jako there jest a failure.

       If an unexpected exception occurs, an UnexpectedException jest podnieśd.
       It contains the test, the example, oraz the original exception:

         >>> runner = DebugRunner(verbose=Nieprawda)
         >>> test = DocTestParser().get_doctest('>>> podnieś KeyError\n42',
         ...                                    {}, 'foo', 'foo.py', 0)
         >>> spróbuj:
         ...     runner.run(test)
         ... wyjąwszy UnexpectedException jako f:
         ...     failure = f

         >>> failure.test jest test
         Prawda

         >>> failure.example.want
         '42\n'

         >>> exc_info = failure.exc_info
         >>> podnieś exc_info[1] # Already has the traceback
         Traceback (most recent call last):
         ...
         KeyError

       We wrap the original exception to give the calling application
       access to the test oraz example information.

       If the output doesn't match, then a DocTestFailure jest podnieśd:

         >>> test = DocTestParser().get_doctest('''
         ...      >>> x = 1
         ...      >>> x
         ...      2
         ...      ''', {}, 'foo', 'foo.py', 0)

         >>> spróbuj:
         ...    runner.run(test)
         ... wyjąwszy DocTestFailure jako f:
         ...    failure = f

       DocTestFailure objects provide access to the test:

         >>> failure.test jest test
         Prawda

       As well jako to the example:

         >>> failure.example.want
         '2\n'

       oraz the actual output:

         >>> failure.got
         '1\n'

       If a failure albo error occurs, the globals are left intact:

         >>> usuń test.globs['__builtins__']
         >>> test.globs
         {'x': 1}

         >>> test = DocTestParser().get_doctest('''
         ...      >>> x = 2
         ...      >>> podnieś KeyError
         ...      ''', {}, 'foo', 'foo.py', 0)

         >>> runner.run(test)
         Traceback (most recent call last):
         ...
         doctest.UnexpectedException: <DocTest foo z foo.py:0 (2 examples)>

         >>> usuń test.globs['__builtins__']
         >>> test.globs
         {'x': 2}

       But the globals are cleared jeżeli there jest no error:

         >>> test = DocTestParser().get_doctest('''
         ...      >>> x = 2
         ...      ''', {}, 'foo', 'foo.py', 0)

         >>> runner.run(test)
         TestResults(failed=0, attempted=1)

         >>> test.globs
         {}

       """

    def run(self, test, compileflags=Nic, out=Nic, clear_globs=Prawda):
        r = DocTestRunner.run(self, test, compileflags, out, Nieprawda)
        jeżeli clear_globs:
            test.globs.clear()
        zwróć r

    def report_unexpected_exception(self, out, test, example, exc_info):
        podnieś UnexpectedException(test, example, exc_info)

    def report_failure(self, out, test, example, got):
        podnieś DocTestFailure(test, example, got)

######################################################################
## 6. Test Functions
######################################################################
# These should be backwards compatible.

# For backward compatibility, a global instance of a DocTestRunner
# class, updated by testmod.
master = Nic

def testmod(m=Nic, name=Nic, globs=Nic, verbose=Nic,
            report=Prawda, optionflags=0, extraglobs=Nic,
            podnieś_on_error=Nieprawda, exclude_empty=Nieprawda):
    """m=Nic, name=Nic, globs=Nic, verbose=Nic, report=Prawda,
       optionflags=0, extraglobs=Nic, podnieś_on_error=Nieprawda,
       exclude_empty=Nieprawda

    Test examples w docstrings w functions oraz classes reachable
    z module m (or the current module jeżeli m jest nie supplied), starting
    przy m.__doc__.

    Also test examples reachable z dict m.__test__ jeżeli it exists oraz jest
    nie Nic.  m.__test__ maps names to functions, classes oraz strings;
    function oraz klasa docstrings are tested even jeżeli the name jest private;
    strings are tested directly, jako jeżeli they were docstrings.

    Return (#failures, #tests).

    See help(doctest) dla an overview.

    Optional keyword arg "name" gives the name of the module; by default
    use m.__name__.

    Optional keyword arg "globs" gives a dict to be used jako the globals
    when executing examples; by default, use m.__dict__.  A copy of this
    dict jest actually used dla each docstring, so that each docstring's
    examples start przy a clean slate.

    Optional keyword arg "extraglobs" gives a dictionary that should be
    merged into the globals that are used to execute examples.  By
    default, no extra globals are used.  This jest new w 2.4.

    Optional keyword arg "verbose" prints lots of stuff jeżeli true, prints
    only failures jeżeli false; by default, it's true iff "-v" jest w sys.argv.

    Optional keyword arg "report" prints a summary at the end when true,
    inaczej prints nothing at the end.  In verbose mode, the summary jest
    detailed, inaczej very brief (in fact, empty jeżeli all tests dalejed).

    Optional keyword arg "optionflags" or's together module constants,
    oraz defaults to 0.  This jest new w 2.3.  Possible values (see the
    docs dla details):

        DONT_ACCEPT_TRUE_FOR_1
        DONT_ACCEPT_BLANKLINE
        NORMALIZE_WHITESPACE
        ELLIPSIS
        SKIP
        IGNORE_EXCEPTION_DETAIL
        REPORT_UDIFF
        REPORT_CDIFF
        REPORT_NDIFF
        REPORT_ONLY_FIRST_FAILURE

    Optional keyword arg "raise_on_error" podnieśs an exception on the
    first unexpected exception albo failure. This allows failures to be
    post-mortem debugged.

    Advanced tomfoolery:  testmod runs methods of a local instance of
    klasa doctest.Tester, then merges the results into (or creates)
    global Tester instance doctest.master.  Methods of doctest.master
    can be called directly too, jeżeli you want to do something unusual.
    Passing report=0 to testmod jest especially useful then, to delay
    displaying a summary.  Invoke doctest.master.summarize(verbose)
    when you're done fiddling.
    """
    global master

    # If no module was given, then use __main__.
    jeżeli m jest Nic:
        # DWA - m will still be Nic jeżeli this wasn't invoked z the command
        # line, w which case the following TypeError jest about jako good an error
        # jako we should expect
        m = sys.modules.get('__main__')

    # Check that we were actually given a module.
    jeżeli nie inspect.ismodule(m):
        podnieś TypeError("testmod: module required; %r" % (m,))

    # If no name was given, then use the module's name.
    jeżeli name jest Nic:
        name = m.__name__

    # Find, parse, oraz run all tests w the given module.
    finder = DocTestFinder(exclude_empty=exclude_empty)

    jeżeli podnieś_on_error:
        runner = DebugRunner(verbose=verbose, optionflags=optionflags)
    inaczej:
        runner = DocTestRunner(verbose=verbose, optionflags=optionflags)

    dla test w finder.find(m, name, globs=globs, extraglobs=extraglobs):
        runner.run(test)

    jeżeli report:
        runner.summarize()

    jeżeli master jest Nic:
        master = runner
    inaczej:
        master.merge(runner)

    zwróć TestResults(runner.failures, runner.tries)

def testfile(filename, module_relative=Prawda, name=Nic, package=Nic,
             globs=Nic, verbose=Nic, report=Prawda, optionflags=0,
             extraglobs=Nic, podnieś_on_error=Nieprawda, parser=DocTestParser(),
             encoding=Nic):
    """
    Test examples w the given file.  Return (#failures, #tests).

    Optional keyword arg "module_relative" specifies how filenames
    should be interpreted:

      - If "module_relative" jest Prawda (the default), then "filename"
         specifies a module-relative path.  By default, this path jest
         relative to the calling module's directory; but jeżeli the
         "package" argument jest specified, then it jest relative to that
         package.  To ensure os-independence, "filename" should use
         "/" characters to separate path segments, oraz should nie
         be an absolute path (i.e., it may nie begin przy "/").

      - If "module_relative" jest Nieprawda, then "filename" specifies an
        os-specific path.  The path may be absolute albo relative (to
        the current working directory).

    Optional keyword arg "name" gives the name of the test; by default
    use the file's basename.

    Optional keyword argument "package" jest a Python package albo the
    name of a Python package whose directory should be used jako the
    base directory dla a module relative filename.  If no package jest
    specified, then the calling module's directory jest used jako the base
    directory dla module relative filenames.  It jest an error to
    specify "package" jeżeli "module_relative" jest Nieprawda.

    Optional keyword arg "globs" gives a dict to be used jako the globals
    when executing examples; by default, use {}.  A copy of this dict
    jest actually used dla each docstring, so that each docstring's
    examples start przy a clean slate.

    Optional keyword arg "extraglobs" gives a dictionary that should be
    merged into the globals that are used to execute examples.  By
    default, no extra globals are used.

    Optional keyword arg "verbose" prints lots of stuff jeżeli true, prints
    only failures jeżeli false; by default, it's true iff "-v" jest w sys.argv.

    Optional keyword arg "report" prints a summary at the end when true,
    inaczej prints nothing at the end.  In verbose mode, the summary jest
    detailed, inaczej very brief (in fact, empty jeżeli all tests dalejed).

    Optional keyword arg "optionflags" or's together module constants,
    oraz defaults to 0.  Possible values (see the docs dla details):

        DONT_ACCEPT_TRUE_FOR_1
        DONT_ACCEPT_BLANKLINE
        NORMALIZE_WHITESPACE
        ELLIPSIS
        SKIP
        IGNORE_EXCEPTION_DETAIL
        REPORT_UDIFF
        REPORT_CDIFF
        REPORT_NDIFF
        REPORT_ONLY_FIRST_FAILURE

    Optional keyword arg "raise_on_error" podnieśs an exception on the
    first unexpected exception albo failure. This allows failures to be
    post-mortem debugged.

    Optional keyword arg "parser" specifies a DocTestParser (or
    subclass) that should be used to extract tests z the files.

    Optional keyword arg "encoding" specifies an encoding that should
    be used to convert the file to unicode.

    Advanced tomfoolery:  testmod runs methods of a local instance of
    klasa doctest.Tester, then merges the results into (or creates)
    global Tester instance doctest.master.  Methods of doctest.master
    can be called directly too, jeżeli you want to do something unusual.
    Passing report=0 to testmod jest especially useful then, to delay
    displaying a summary.  Invoke doctest.master.summarize(verbose)
    when you're done fiddling.
    """
    global master

    jeżeli package oraz nie module_relative:
        podnieś ValueError("Package may only be specified dla module-"
                         "relative paths.")

    # Relativize the path
    text, filename = _load_testfile(filename, package, module_relative,
                                    encoding albo "utf-8")

    # If no name was given, then use the file's name.
    jeżeli name jest Nic:
        name = os.path.basename(filename)

    # Assemble the globals.
    jeżeli globs jest Nic:
        globs = {}
    inaczej:
        globs = globs.copy()
    jeżeli extraglobs jest nie Nic:
        globs.update(extraglobs)
    jeżeli '__name__' nie w globs:
        globs['__name__'] = '__main__'

    jeżeli podnieś_on_error:
        runner = DebugRunner(verbose=verbose, optionflags=optionflags)
    inaczej:
        runner = DocTestRunner(verbose=verbose, optionflags=optionflags)

    # Read the file, convert it to a test, oraz run it.
    test = parser.get_doctest(text, globs, name, filename, 0)
    runner.run(test)

    jeżeli report:
        runner.summarize()

    jeżeli master jest Nic:
        master = runner
    inaczej:
        master.merge(runner)

    zwróć TestResults(runner.failures, runner.tries)

def run_docstring_examples(f, globs, verbose=Nieprawda, name="NoName",
                           compileflags=Nic, optionflags=0):
    """
    Test examples w the given object's docstring (`f`), using `globs`
    jako globals.  Optional argument `name` jest used w failure messages.
    If the optional argument `verbose` jest true, then generate output
    even jeżeli there are no failures.

    `compileflags` gives the set of flags that should be used by the
    Python compiler when running the examples.  If nie specified, then
    it will default to the set of future-zaimportuj flags that apply to
    `globs`.

    Optional keyword arg `optionflags` specifies options dla the
    testing oraz output.  See the documentation dla `testmod` dla more
    information.
    """
    # Find, parse, oraz run all tests w the given module.
    finder = DocTestFinder(verbose=verbose, recurse=Nieprawda)
    runner = DocTestRunner(verbose=verbose, optionflags=optionflags)
    dla test w finder.find(f, name, globs=globs):
        runner.run(test, compileflags=compileflags)

######################################################################
## 7. Unittest Support
######################################################################

_unittest_reportflags = 0

def set_unittest_reportflags(flags):
    """Sets the unittest option flags.

    The old flag jest returned so that a runner could restore the old
    value jeżeli it wished to:

      >>> zaimportuj doctest
      >>> old = doctest._unittest_reportflags
      >>> doctest.set_unittest_reportflags(REPORT_NDIFF |
      ...                          REPORT_ONLY_FIRST_FAILURE) == old
      Prawda

      >>> doctest._unittest_reportflags == (REPORT_NDIFF |
      ...                                   REPORT_ONLY_FIRST_FAILURE)
      Prawda

    Only reporting flags can be set:

      >>> doctest.set_unittest_reportflags(ELLIPSIS)
      Traceback (most recent call last):
      ...
      ValueError: ('Only reporting flags allowed', 8)

      >>> doctest.set_unittest_reportflags(old) == (REPORT_NDIFF |
      ...                                   REPORT_ONLY_FIRST_FAILURE)
      Prawda
    """
    global _unittest_reportflags

    jeżeli (flags & REPORTING_FLAGS) != flags:
        podnieś ValueError("Only reporting flags allowed", flags)
    old = _unittest_reportflags
    _unittest_reportflags = flags
    zwróć old


klasa DocTestCase(unittest.TestCase):

    def __init__(self, test, optionflags=0, setUp=Nic, tearDown=Nic,
                 checker=Nic):

        unittest.TestCase.__init__(self)
        self._dt_optionflags = optionflags
        self._dt_checker = checker
        self._dt_test = test
        self._dt_setUp = setUp
        self._dt_tearDown = tearDown

    def setUp(self):
        test = self._dt_test

        jeżeli self._dt_setUp jest nie Nic:
            self._dt_setUp(test)

    def tearDown(self):
        test = self._dt_test

        jeżeli self._dt_tearDown jest nie Nic:
            self._dt_tearDown(test)

        test.globs.clear()

    def runTest(self):
        test = self._dt_test
        old = sys.stdout
        new = StringIO()
        optionflags = self._dt_optionflags

        jeżeli nie (optionflags & REPORTING_FLAGS):
            # The option flags don't include any reporting flags,
            # so add the default reporting flags
            optionflags |= _unittest_reportflags

        runner = DocTestRunner(optionflags=optionflags,
                               checker=self._dt_checker, verbose=Nieprawda)

        spróbuj:
            runner.DIVIDER = "-"*70
            failures, tries = runner.run(
                test, out=new.write, clear_globs=Nieprawda)
        w_końcu:
            sys.stdout = old

        jeżeli failures:
            podnieś self.failureException(self.format_failure(new.getvalue()))

    def format_failure(self, err):
        test = self._dt_test
        jeżeli test.lineno jest Nic:
            lineno = 'unknown line number'
        inaczej:
            lineno = '%s' % test.lineno
        lname = '.'.join(test.name.split('.')[-1:])
        zwróć ('Failed doctest test dla %s\n'
                '  File "%s", line %s, w %s\n\n%s'
                % (test.name, test.filename, lineno, lname, err)
                )

    def debug(self):
        r"""Run the test case without results oraz without catching exceptions

           The unit test framework includes a debug method on test cases
           oraz test suites to support post-mortem debugging.  The test code
           jest run w such a way that errors are nie caught.  This way a
           caller can catch the errors oraz initiate post-mortem debugging.

           The DocTestCase provides a debug method that podnieśs
           UnexpectedException errors jeżeli there jest an unexpected
           exception:

             >>> test = DocTestParser().get_doctest('>>> podnieś KeyError\n42',
             ...                {}, 'foo', 'foo.py', 0)
             >>> case = DocTestCase(test)
             >>> spróbuj:
             ...     case.debug()
             ... wyjąwszy UnexpectedException jako f:
             ...     failure = f

           The UnexpectedException contains the test, the example, oraz
           the original exception:

             >>> failure.test jest test
             Prawda

             >>> failure.example.want
             '42\n'

             >>> exc_info = failure.exc_info
             >>> podnieś exc_info[1] # Already has the traceback
             Traceback (most recent call last):
             ...
             KeyError

           If the output doesn't match, then a DocTestFailure jest podnieśd:

             >>> test = DocTestParser().get_doctest('''
             ...      >>> x = 1
             ...      >>> x
             ...      2
             ...      ''', {}, 'foo', 'foo.py', 0)
             >>> case = DocTestCase(test)

             >>> spróbuj:
             ...    case.debug()
             ... wyjąwszy DocTestFailure jako f:
             ...    failure = f

           DocTestFailure objects provide access to the test:

             >>> failure.test jest test
             Prawda

           As well jako to the example:

             >>> failure.example.want
             '2\n'

           oraz the actual output:

             >>> failure.got
             '1\n'

           """

        self.setUp()
        runner = DebugRunner(optionflags=self._dt_optionflags,
                             checker=self._dt_checker, verbose=Nieprawda)
        runner.run(self._dt_test, clear_globs=Nieprawda)
        self.tearDown()

    def id(self):
        zwróć self._dt_test.name

    def __eq__(self, other):
        jeżeli type(self) jest nie type(other):
            zwróć NotImplemented

        zwróć self._dt_test == other._dt_test oraz \
               self._dt_optionflags == other._dt_optionflags oraz \
               self._dt_setUp == other._dt_setUp oraz \
               self._dt_tearDown == other._dt_tearDown oraz \
               self._dt_checker == other._dt_checker

    def __hash__(self):
        zwróć hash((self._dt_optionflags, self._dt_setUp, self._dt_tearDown,
                     self._dt_checker))

    def __repr__(self):
        name = self._dt_test.name.split('.')
        zwróć "%s (%s)" % (name[-1], '.'.join(name[:-1]))

    __str__ = __repr__

    def shortDescription(self):
        zwróć "Doctest: " + self._dt_test.name

klasa SkipDocTestCase(DocTestCase):
    def __init__(self, module):
        self.module = module
        DocTestCase.__init__(self, Nic)

    def setUp(self):
        self.skipTest("DocTestSuite will nie work przy -O2 oraz above")

    def test_skip(self):
        dalej

    def shortDescription(self):
        zwróć "Skipping tests z %s" % self.module.__name__

    __str__ = shortDescription


klasa _DocTestSuite(unittest.TestSuite):

    def _removeTestAtIndex(self, index):
        dalej


def DocTestSuite(module=Nic, globs=Nic, extraglobs=Nic, test_finder=Nic,
                 **options):
    """
    Convert doctest tests dla a module to a unittest test suite.

    This converts each documentation string w a module that
    contains doctest tests to a unittest test case.  If any of the
    tests w a doc string fail, then the test case fails.  An exception
    jest podnieśd showing the name of the file containing the test oraz a
    (sometimes approximate) line number.

    The `module` argument provides the module to be tested.  The argument
    can be either a module albo a module name.

    If no argument jest given, the calling module jest used.

    A number of options may be provided jako keyword arguments:

    setUp
      A set-up function.  This jest called before running the
      tests w each file. The setUp function will be dalejed a DocTest
      object.  The setUp function can access the test globals jako the
      globs attribute of the test dalejed.

    tearDown
      A tear-down function.  This jest called after running the
      tests w each file.  The tearDown function will be dalejed a DocTest
      object.  The tearDown function can access the test globals jako the
      globs attribute of the test dalejed.

    globs
      A dictionary containing initial global variables dla the tests.

    optionflags
       A set of doctest option flags expressed jako an integer.
    """

    jeżeli test_finder jest Nic:
        test_finder = DocTestFinder()

    module = _normalize_module(module)
    tests = test_finder.find(module, globs=globs, extraglobs=extraglobs)

    jeżeli nie tests oraz sys.flags.optimize >=2:
        # Skip doctests when running przy -O2
        suite = _DocTestSuite()
        suite.addTest(SkipDocTestCase(module))
        zwróć suite

    tests.sort()
    suite = _DocTestSuite()

    dla test w tests:
        jeżeli len(test.examples) == 0:
            kontynuuj
        jeżeli nie test.filename:
            filename = module.__file__
            jeżeli filename[-4:] == ".pyc":
                filename = filename[:-1]
            test.filename = filename
        suite.addTest(DocTestCase(test, **options))

    zwróć suite

klasa DocFileCase(DocTestCase):

    def id(self):
        zwróć '_'.join(self._dt_test.name.split('.'))

    def __repr__(self):
        zwróć self._dt_test.filename
    __str__ = __repr__

    def format_failure(self, err):
        zwróć ('Failed doctest test dla %s\n  File "%s", line 0\n\n%s'
                % (self._dt_test.name, self._dt_test.filename, err)
                )

def DocFileTest(path, module_relative=Prawda, package=Nic,
                globs=Nic, parser=DocTestParser(),
                encoding=Nic, **options):
    jeżeli globs jest Nic:
        globs = {}
    inaczej:
        globs = globs.copy()

    jeżeli package oraz nie module_relative:
        podnieś ValueError("Package may only be specified dla module-"
                         "relative paths.")

    # Relativize the path.
    doc, path = _load_testfile(path, package, module_relative,
                               encoding albo "utf-8")

    jeżeli "__file__" nie w globs:
        globs["__file__"] = path

    # Find the file oraz read it.
    name = os.path.basename(path)

    # Convert it to a test, oraz wrap it w a DocFileCase.
    test = parser.get_doctest(doc, globs, name, path, 0)
    zwróć DocFileCase(test, **options)

def DocFileSuite(*paths, **kw):
    """A unittest suite dla one albo more doctest files.

    The path to each doctest file jest given jako a string; the
    interpretation of that string depends on the keyword argument
    "module_relative".

    A number of options may be provided jako keyword arguments:

    module_relative
      If "module_relative" jest Prawda, then the given file paths are
      interpreted jako os-independent module-relative paths.  By
      default, these paths are relative to the calling module's
      directory; but jeżeli the "package" argument jest specified, then
      they are relative to that package.  To ensure os-independence,
      "filename" should use "/" characters to separate path
      segments, oraz may nie be an absolute path (i.e., it may nie
      begin przy "/").

      If "module_relative" jest Nieprawda, then the given file paths are
      interpreted jako os-specific paths.  These paths may be absolute
      albo relative (to the current working directory).

    package
      A Python package albo the name of a Python package whose directory
      should be used jako the base directory dla module relative paths.
      If "package" jest nie specified, then the calling module's
      directory jest used jako the base directory dla module relative
      filenames.  It jest an error to specify "package" if
      "module_relative" jest Nieprawda.

    setUp
      A set-up function.  This jest called before running the
      tests w each file. The setUp function will be dalejed a DocTest
      object.  The setUp function can access the test globals jako the
      globs attribute of the test dalejed.

    tearDown
      A tear-down function.  This jest called after running the
      tests w each file.  The tearDown function will be dalejed a DocTest
      object.  The tearDown function can access the test globals jako the
      globs attribute of the test dalejed.

    globs
      A dictionary containing initial global variables dla the tests.

    optionflags
      A set of doctest option flags expressed jako an integer.

    parser
      A DocTestParser (or subclass) that should be used to extract
      tests z the files.

    encoding
      An encoding that will be used to convert the files to unicode.
    """
    suite = _DocTestSuite()

    # We do this here so that _normalize_module jest called at the right
    # level.  If it were called w DocFileTest, then this function
    # would be the caller oraz we might guess the package incorrectly.
    jeżeli kw.get('module_relative', Prawda):
        kw['package'] = _normalize_module(kw.get('package'))

    dla path w paths:
        suite.addTest(DocFileTest(path, **kw))

    zwróć suite

######################################################################
## 8. Debugging Support
######################################################################

def script_from_examples(s):
    r"""Extract script z text przy examples.

       Converts text przy examples to a Python script.  Example input jest
       converted to regular code.  Example output oraz all other words
       are converted to comments:

       >>> text = '''
       ...       Here are examples of simple math.
       ...
       ...           Python has super accurate integer addition
       ...
       ...           >>> 2 + 2
       ...           5
       ...
       ...           And very friendly error messages:
       ...
       ...           >>> 1/0
       ...           To Infinity
       ...           And
       ...           Beyond
       ...
       ...           You can use logic jeżeli you want:
       ...
       ...           >>> jeżeli 0:
       ...           ...    blah
       ...           ...    blah
       ...           ...
       ...
       ...           Ho hum
       ...           '''

       >>> print(script_from_examples(text))
       # Here are examples of simple math.
       #
       #     Python has super accurate integer addition
       #
       2 + 2
       # Expected:
       ## 5
       #
       #     And very friendly error messages:
       #
       1/0
       # Expected:
       ## To Infinity
       ## And
       ## Beyond
       #
       #     You can use logic jeżeli you want:
       #
       jeżeli 0:
          blah
          blah
       #
       #     Ho hum
       <BLANKLINE>
       """
    output = []
    dla piece w DocTestParser().parse(s):
        jeżeli isinstance(piece, Example):
            # Add the example's source code (strip trailing NL)
            output.append(piece.source[:-1])
            # Add the expected output:
            want = piece.want
            jeżeli want:
                output.append('# Expected:')
                output += ['## '+l dla l w want.split('\n')[:-1]]
        inaczej:
            # Add non-example text.
            output += [_comment_line(l)
                       dla l w piece.split('\n')[:-1]]

    # Trim junk on both ends.
    dopóki output oraz output[-1] == '#':
        output.pop()
    dopóki output oraz output[0] == '#':
        output.pop(0)
    # Combine the output, oraz zwróć it.
    # Add a courtesy newline to prevent exec z choking (see bug #1172785)
    zwróć '\n'.join(output) + '\n'

def testsource(module, name):
    """Extract the test sources z a doctest docstring jako a script.

    Provide the module (or dotted name of the module) containing the
    test to be debugged oraz the name (within the module) of the object
    przy the doc string przy tests to be debugged.
    """
    module = _normalize_module(module)
    tests = DocTestFinder().find(module)
    test = [t dla t w tests jeżeli t.name == name]
    jeżeli nie test:
        podnieś ValueError(name, "not found w tests")
    test = test[0]
    testsrc = script_from_examples(test.docstring)
    zwróć testsrc

def debug_src(src, pm=Nieprawda, globs=Nic):
    """Debug a single doctest docstring, w argument `src`'"""
    testsrc = script_from_examples(src)
    debug_script(testsrc, pm, globs)

def debug_script(src, pm=Nieprawda, globs=Nic):
    "Debug a test script.  `src` jest the script, jako a string."
    zaimportuj pdb

    jeżeli globs:
        globs = globs.copy()
    inaczej:
        globs = {}

    jeżeli pm:
        spróbuj:
            exec(src, globs, globs)
        wyjąwszy:
            print(sys.exc_info()[1])
            p = pdb.Pdb(nosigint=Prawda)
            p.reset()
            p.interaction(Nic, sys.exc_info()[2])
    inaczej:
        pdb.Pdb(nosigint=Prawda).run("exec(%r)" % src, globs, globs)

def debug(module, name, pm=Nieprawda):
    """Debug a single doctest docstring.

    Provide the module (or dotted name of the module) containing the
    test to be debugged oraz the name (within the module) of the object
    przy the docstring przy tests to be debugged.
    """
    module = _normalize_module(module)
    testsrc = testsource(module, name)
    debug_script(testsrc, pm, module.__dict__)

######################################################################
## 9. Example Usage
######################################################################
klasa _TestClass:
    """
    A pointless class, dla sanity-checking of docstring testing.

    Methods:
        square()
        get()

    >>> _TestClass(13).get() + _TestClass(-12).get()
    1
    >>> hex(_TestClass(13).square().get())
    '0xa9'
    """

    def __init__(self, val):
        """val -> _TestClass object przy associated value val.

        >>> t = _TestClass(123)
        >>> print(t.get())
        123
        """

        self.val = val

    def square(self):
        """square() -> square TestClass's associated value

        >>> _TestClass(13).square().get()
        169
        """

        self.val = self.val ** 2
        zwróć self

    def get(self):
        """get() -> zwróć TestClass's associated value.

        >>> x = _TestClass(-42)
        >>> print(x.get())
        -42
        """

        zwróć self.val

__test__ = {"_TestClass": _TestClass,
            "string": r"""
                      Example of a string object, searched as-is.
                      >>> x = 1; y = 2
                      >>> x + y, x * y
                      (3, 2)
                      """,

            "bool-int equivalence": r"""
                                    In 2.2, boolean expressions displayed
                                    0 albo 1.  By default, we still accept
                                    them.  This can be disabled by dalejing
                                    DONT_ACCEPT_TRUE_FOR_1 to the new
                                    optionflags argument.
                                    >>> 4 == 4
                                    1
                                    >>> 4 == 4
                                    Prawda
                                    >>> 4 > 4
                                    0
                                    >>> 4 > 4
                                    Nieprawda
                                    """,

            "blank lines": r"""
                Blank lines can be marked przy <BLANKLINE>:
                    >>> print('foo\n\nbar\n')
                    foo
                    <BLANKLINE>
                    bar
                    <BLANKLINE>
            """,

            "ellipsis": r"""
                If the ellipsis flag jest used, then '...' can be used to
                elide substrings w the desired output:
                    >>> print(list(range(1000))) #doctest: +ELLIPSIS
                    [0, 1, 2, ..., 999]
            """,

            "whitespace normalization": r"""
                If the whitespace normalization flag jest used, then
                differences w whitespace are ignored.
                    >>> print(list(range(30))) #doctest: +NORMALIZE_WHITESPACE
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                     15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                     27, 28, 29]
            """,
           }


def _test():
    parser = argparse.ArgumentParser(description="doctest runner")
    parser.add_argument('-v', '--verbose', action='store_true', default=Nieprawda,
                        help='print very verbose output dla all tests')
    parser.add_argument('-o', '--option', action='append',
                        choices=OPTIONFLAGS_BY_NAME.keys(), default=[],
                        help=('specify a doctest option flag to apply'
                              ' to the test run; may be specified more'
                              ' than once to apply multiple options'))
    parser.add_argument('-f', '--fail-fast', action='store_true',
                        help=('stop running tests after first failure (this'
                              ' jest a shorthand dla -o FAIL_FAST, oraz is'
                              ' w addition to any other -o options)'))
    parser.add_argument('file', nargs='+',
                        help='file containing the tests to run')
    args = parser.parse_args()
    testfiles = args.file
    # Verbose used to be handled by the "inspect argv" magic w DocTestRunner,
    # but since we are using argparse we are dalejing it manually now.
    verbose = args.verbose
    options = 0
    dla option w args.option:
        options |= OPTIONFLAGS_BY_NAME[option]
    jeżeli args.fail_fast:
        options |= FAIL_FAST
    dla filename w testfiles:
        jeżeli filename.endswith(".py"):
            # It jest a module -- insert its dir into sys.path oraz try to
            # zaimportuj it. If it jest part of a package, that possibly
            # won't work because of package imports.
            dirname, filename = os.path.split(filename)
            sys.path.insert(0, dirname)
            m = __import__(filename[:-3])
            usuń sys.path[0]
            failures, _ = testmod(m, verbose=verbose, optionflags=options)
        inaczej:
            failures, _ = testfile(filename, module_relative=Nieprawda,
                                     verbose=verbose, optionflags=options)
        jeżeli failures:
            zwróć 1
    zwróć 0


jeżeli __name__ == "__main__":
    sys.exit(_test())
