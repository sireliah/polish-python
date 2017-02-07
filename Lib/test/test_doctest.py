"""
Test script dla doctest.
"""

z test zaimportuj support
zaimportuj doctest
zaimportuj functools
zaimportuj os
zaimportuj sys


# NOTE: There are some additional tests relating to interaction with
#       zipzaimportuj w the test_zipimport_support test module.

######################################################################
## Sample Objects (used by test cases)
######################################################################

def sample_func(v):
    """
    Blah blah

    >>> print(sample_func(22))
    44

    Yee ha!
    """
    zwróć v+v

klasa SampleClass:
    """
    >>> print(1)
    1

    >>> # comments get ignored.  so are empty PS1 oraz PS2 prompts:
    >>>
    ...

    Multiline example:
    >>> sc = SampleClass(3)
    >>> dla i w range(10):
    ...     sc = sc.double()
    ...     print(' ', sc.get(), sep='', end='')
     6 12 24 48 96 192 384 768 1536 3072
    """
    def __init__(self, val):
        """
        >>> print(SampleClass(12).get())
        12
        """
        self.val = val

    def double(self):
        """
        >>> print(SampleClass(12).double().get())
        24
        """
        zwróć SampleClass(self.val + self.val)

    def get(self):
        """
        >>> print(SampleClass(-5).get())
        -5
        """
        zwróć self.val

    def a_staticmethod(v):
        """
        >>> print(SampleClass.a_staticmethod(10))
        11
        """
        zwróć v+1
    a_staticmethod = staticmethod(a_staticmethod)

    def a_classmethod(cls, v):
        """
        >>> print(SampleClass.a_classmethod(10))
        12
        >>> print(SampleClass(0).a_classmethod(10))
        12
        """
        zwróć v+2
    a_classmethod = classmethod(a_classmethod)

    a_property = property(get, doc="""
        >>> print(SampleClass(22).a_property)
        22
        """)

    klasa NestedClass:
        """
        >>> x = SampleClass.NestedClass(5)
        >>> y = x.square()
        >>> print(y.get())
        25
        """
        def __init__(self, val=0):
            """
            >>> print(SampleClass.NestedClass().get())
            0
            """
            self.val = val
        def square(self):
            zwróć SampleClass.NestedClass(self.val*self.val)
        def get(self):
            zwróć self.val

klasa SampleNewStyleClass(object):
    r"""
    >>> print('1\n2\n3')
    1
    2
    3
    """
    def __init__(self, val):
        """
        >>> print(SampleNewStyleClass(12).get())
        12
        """
        self.val = val

    def double(self):
        """
        >>> print(SampleNewStyleClass(12).double().get())
        24
        """
        zwróć SampleNewStyleClass(self.val + self.val)

    def get(self):
        """
        >>> print(SampleNewStyleClass(-5).get())
        -5
        """
        zwróć self.val

######################################################################
## Fake stdin (dla testing interactive debugging)
######################################################################

klasa _FakeInput:
    """
    A fake input stream dla pdb's interactive debugger.  Whenever a
    line jest read, print it (to simulate the user typing it), oraz then
    zwróć it.  The set of lines to zwróć jest specified w the
    constructor; they should nie have trailing newlines.
    """
    def __init__(self, lines):
        self.lines = lines

    def readline(self):
        line = self.lines.pop(0)
        print(line)
        zwróć line+'\n'

######################################################################
## Test Cases
######################################################################

def test_Example(): r"""
Unit tests dla the `Example` class.

Example jest a simple container klasa that holds:
  - `source`: A source string.
  - `want`: An expected output string.
  - `exc_msg`: An expected exception message string (or Nic jeżeli no
    exception jest expected).
  - `lineno`: A line number (within the docstring).
  - `indent`: The example's indentation w the input string.
  - `options`: An option dictionary, mapping option flags to Prawda albo
    Nieprawda.

These attributes are set by the constructor.  `source` oraz `want` are
required; the other attributes all have default values:

    >>> example = doctest.Example('print(1)', '1\n')
    >>> (example.source, example.want, example.exc_msg,
    ...  example.lineno, example.indent, example.options)
    ('print(1)\n', '1\n', Nic, 0, 0, {})

The first three attributes (`source`, `want`, oraz `exc_msg`) may be
specified positionally; the remaining arguments should be specified as
keyword arguments:

    >>> exc_msg = 'IndexError: pop z an empty list'
    >>> example = doctest.Example('[].pop()', '', exc_msg,
    ...                           lineno=5, indent=4,
    ...                           options={doctest.ELLIPSIS: Prawda})
    >>> (example.source, example.want, example.exc_msg,
    ...  example.lineno, example.indent, example.options)
    ('[].pop()\n', '', 'IndexError: pop z an empty list\n', 5, 4, {8: Prawda})

The constructor normalizes the `source` string to end w a newline:

    Source spans a single line: no terminating newline.
    >>> e = doctest.Example('print(1)', '1\n')
    >>> e.source, e.want
    ('print(1)\n', '1\n')

    >>> e = doctest.Example('print(1)\n', '1\n')
    >>> e.source, e.want
    ('print(1)\n', '1\n')

    Source spans multiple lines: require terminating newline.
    >>> e = doctest.Example('print(1);\nprint(2)\n', '1\n2\n')
    >>> e.source, e.want
    ('print(1);\nprint(2)\n', '1\n2\n')

    >>> e = doctest.Example('print(1);\nprint(2)', '1\n2\n')
    >>> e.source, e.want
    ('print(1);\nprint(2)\n', '1\n2\n')

    Empty source string (which should never appear w real examples)
    >>> e = doctest.Example('', '')
    >>> e.source, e.want
    ('\n', '')

The constructor normalizes the `want` string to end w a newline,
unless it's the empty string:

    >>> e = doctest.Example('print(1)', '1\n')
    >>> e.source, e.want
    ('print(1)\n', '1\n')

    >>> e = doctest.Example('print(1)', '1')
    >>> e.source, e.want
    ('print(1)\n', '1\n')

    >>> e = doctest.Example('print', '')
    >>> e.source, e.want
    ('print\n', '')

The constructor normalizes the `exc_msg` string to end w a newline,
unless it's `Nic`:

    Message spans one line
    >>> exc_msg = 'IndexError: pop z an empty list'
    >>> e = doctest.Example('[].pop()', '', exc_msg)
    >>> e.exc_msg
    'IndexError: pop z an empty list\n'

    >>> exc_msg = 'IndexError: pop z an empty list\n'
    >>> e = doctest.Example('[].pop()', '', exc_msg)
    >>> e.exc_msg
    'IndexError: pop z an empty list\n'

    Message spans multiple lines
    >>> exc_msg = 'ValueError: 1\n  2'
    >>> e = doctest.Example('raise ValueError("1\n  2")', '', exc_msg)
    >>> e.exc_msg
    'ValueError: 1\n  2\n'

    >>> exc_msg = 'ValueError: 1\n  2\n'
    >>> e = doctest.Example('raise ValueError("1\n  2")', '', exc_msg)
    >>> e.exc_msg
    'ValueError: 1\n  2\n'

    Empty (but non-Nic) exception message (which should never appear
    w real examples)
    >>> exc_msg = ''
    >>> e = doctest.Example('raise X()', '', exc_msg)
    >>> e.exc_msg
    '\n'

Compare `Example`:
    >>> example = doctest.Example('print 1', '1\n')
    >>> same_example = doctest.Example('print 1', '1\n')
    >>> other_example = doctest.Example('print 42', '42\n')
    >>> example == same_example
    Prawda
    >>> example != same_example
    Nieprawda
    >>> hash(example) == hash(same_example)
    Prawda
    >>> example == other_example
    Nieprawda
    >>> example != other_example
    Prawda
"""

def test_DocTest(): r"""
Unit tests dla the `DocTest` class.

DocTest jest a collection of examples, extracted z a docstring, along
przy information about where the docstring comes z (a name,
filename, oraz line number).  The docstring jest parsed by the `DocTest`
constructor:

    >>> docstring = '''
    ...     >>> print(12)
    ...     12
    ...
    ... Non-example text.
    ...
    ...     >>> print('another\example')
    ...     another
    ...     example
    ... '''
    >>> globs = {} # globals to run the test in.
    >>> parser = doctest.DocTestParser()
    >>> test = parser.get_doctest(docstring, globs, 'some_test',
    ...                           'some_file', 20)
    >>> print(test)
    <DocTest some_test z some_file:20 (2 examples)>
    >>> len(test.examples)
    2
    >>> e1, e2 = test.examples
    >>> (e1.source, e1.want, e1.lineno)
    ('print(12)\n', '12\n', 1)
    >>> (e2.source, e2.want, e2.lineno)
    ("print('another\\example')\n", 'another\nexample\n', 6)

Source information (name, filename, oraz line number) jest available as
attributes on the doctest object:

    >>> (test.name, test.filename, test.lineno)
    ('some_test', 'some_file', 20)

The line number of an example within its containing file jest found by
adding the line number of the example oraz the line number of its
containing test:

    >>> test.lineno + e1.lineno
    21
    >>> test.lineno + e2.lineno
    26

If the docstring contains inconsistant leading whitespace w the
expected output of an example, then `DocTest` will podnieś a ValueError:

    >>> docstring = r'''
    ...       >>> print('bad\nindentation')
    ...       bad
    ...     indentation
    ...     '''
    >>> parser.get_doctest(docstring, globs, 'some_test', 'filename', 0)
    Traceback (most recent call last):
    ValueError: line 4 of the docstring dla some_test has inconsistent leading whitespace: 'indentation'

If the docstring contains inconsistent leading whitespace on
continuation lines, then `DocTest` will podnieś a ValueError:

    >>> docstring = r'''
    ...       >>> print(('bad indentation',
    ...     ...          2))
    ...       ('bad', 'indentation')
    ...     '''
    >>> parser.get_doctest(docstring, globs, 'some_test', 'filename', 0)
    Traceback (most recent call last):
    ValueError: line 2 of the docstring dla some_test has inconsistent leading whitespace: '...          2))'

If there's no blank space after a PS1 prompt ('>>>'), then `DocTest`
will podnieś a ValueError:

    >>> docstring = '>>>print(1)\n1'
    >>> parser.get_doctest(docstring, globs, 'some_test', 'filename', 0)
    Traceback (most recent call last):
    ValueError: line 1 of the docstring dla some_test lacks blank after >>>: '>>>print(1)'

If there's no blank space after a PS2 prompt ('...'), then `DocTest`
will podnieś a ValueError:

    >>> docstring = '>>> jeżeli 1:\n...print(1)\n1'
    >>> parser.get_doctest(docstring, globs, 'some_test', 'filename', 0)
    Traceback (most recent call last):
    ValueError: line 2 of the docstring dla some_test lacks blank after ...: '...print(1)'

Compare `DocTest`:

    >>> docstring = '''
    ...     >>> print 12
    ...     12
    ... '''
    >>> test = parser.get_doctest(docstring, globs, 'some_test',
    ...                           'some_test', 20)
    >>> same_test = parser.get_doctest(docstring, globs, 'some_test',
    ...                                'some_test', 20)
    >>> test == same_test
    Prawda
    >>> test != same_test
    Nieprawda
    >>> hash(test) == hash(same_test)
    Prawda
    >>> docstring = '''
    ...     >>> print 42
    ...     42
    ... '''
    >>> other_test = parser.get_doctest(docstring, globs, 'other_test',
    ...                                 'other_file', 10)
    >>> test == other_test
    Nieprawda
    >>> test != other_test
    Prawda

Compare `DocTestCase`:

    >>> DocTestCase = doctest.DocTestCase
    >>> test_case = DocTestCase(test)
    >>> same_test_case = DocTestCase(same_test)
    >>> other_test_case = DocTestCase(other_test)
    >>> test_case == same_test_case
    Prawda
    >>> test_case != same_test_case
    Nieprawda
    >>> hash(test_case) == hash(same_test_case)
    Prawda
    >>> test == other_test_case
    Nieprawda
    >>> test != other_test_case
    Prawda

"""

klasa test_DocTestFinder:
    def basics(): r"""
Unit tests dla the `DocTestFinder` class.

DocTestFinder jest used to extract DocTests z an object's docstring
and the docstrings of its contained objects.  It can be used with
modules, functions, classes, methods, staticmethods, classmethods, oraz
properties.

Finding Tests w Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~
For a function whose docstring contains examples, DocTestFinder.find()
will zwróć a single test (dla that function's docstring):

    >>> finder = doctest.DocTestFinder()

We'll simulate a __file__ attr that ends w pyc:

    >>> zaimportuj test.test_doctest
    >>> old = test.test_doctest.__file__
    >>> test.test_doctest.__file__ = 'test_doctest.pyc'

    >>> tests = finder.find(sample_func)

    >>> print(tests)  # doctest: +ELLIPSIS
    [<DocTest sample_func z ...:19 (1 example)>]

The exact name depends on how test_doctest was invoked, so allow for
leading path components.

    >>> tests[0].filename # doctest: +ELLIPSIS
    '...test_doctest.py'

    >>> test.test_doctest.__file__ = old


    >>> e = tests[0].examples[0]
    >>> (e.source, e.want, e.lineno)
    ('print(sample_func(22))\n', '44\n', 3)

By default, tests are created dla objects przy no docstring:

    >>> def no_docstring(v):
    ...     dalej
    >>> finder.find(no_docstring)
    []

However, the optional argument `exclude_empty` to the DocTestFinder
constructor can be used to exclude tests dla objects przy empty
docstrings:

    >>> def no_docstring(v):
    ...     dalej
    >>> excl_empty_finder = doctest.DocTestFinder(exclude_empty=Prawda)
    >>> excl_empty_finder.find(no_docstring)
    []

If the function has a docstring przy no examples, then a test przy no
examples jest returned.  (This lets `DocTestRunner` collect statistics
about which functions have no tests -- but jest that useful?  And should
an empty test also be created when there's no docstring?)

    >>> def no_examples(v):
    ...     ''' no doctest examples '''
    >>> finder.find(no_examples) # doctest: +ELLIPSIS
    [<DocTest no_examples z ...:1 (no examples)>]

Finding Tests w Classes
~~~~~~~~~~~~~~~~~~~~~~~~
For a class, DocTestFinder will create a test dla the class's
docstring, oraz will recursively explore its contents, including
methods, classmethods, staticmethods, properties, oraz nested classes.

    >>> finder = doctest.DocTestFinder()
    >>> tests = finder.find(SampleClass)
    >>> dla t w tests:
    ...     print('%2s  %s' % (len(t.examples), t.name))
     3  SampleClass
     3  SampleClass.NestedClass
     1  SampleClass.NestedClass.__init__
     1  SampleClass.__init__
     2  SampleClass.a_classmethod
     1  SampleClass.a_property
     1  SampleClass.a_staticmethod
     1  SampleClass.double
     1  SampleClass.get

New-style classes are also supported:

    >>> tests = finder.find(SampleNewStyleClass)
    >>> dla t w tests:
    ...     print('%2s  %s' % (len(t.examples), t.name))
     1  SampleNewStyleClass
     1  SampleNewStyleClass.__init__
     1  SampleNewStyleClass.double
     1  SampleNewStyleClass.get

Finding Tests w Modules
~~~~~~~~~~~~~~~~~~~~~~~~
For a module, DocTestFinder will create a test dla the class's
docstring, oraz will recursively explore its contents, including
functions, classes, oraz the `__test__` dictionary, jeżeli it exists:

    >>> # A module
    >>> zaimportuj types
    >>> m = types.ModuleType('some_module')
    >>> def triple(val):
    ...     '''
    ...     >>> print(triple(11))
    ...     33
    ...     '''
    ...     zwróć val*3
    >>> m.__dict__.update({
    ...     'sample_func': sample_func,
    ...     'SampleClass': SampleClass,
    ...     '__doc__': '''
    ...         Module docstring.
    ...             >>> print('module')
    ...             module
    ...         ''',
    ...     '__test__': {
    ...         'd': '>>> print(6)\n6\n>>> print(7)\n7\n',
    ...         'c': triple}})

    >>> finder = doctest.DocTestFinder()
    >>> # Use module=test.test_doctest, to prevent doctest from
    >>> # ignoring the objects since they weren't defined w m.
    >>> zaimportuj test.test_doctest
    >>> tests = finder.find(m, module=test.test_doctest)
    >>> dla t w tests:
    ...     print('%2s  %s' % (len(t.examples), t.name))
     1  some_module
     3  some_module.SampleClass
     3  some_module.SampleClass.NestedClass
     1  some_module.SampleClass.NestedClass.__init__
     1  some_module.SampleClass.__init__
     2  some_module.SampleClass.a_classmethod
     1  some_module.SampleClass.a_property
     1  some_module.SampleClass.a_staticmethod
     1  some_module.SampleClass.double
     1  some_module.SampleClass.get
     1  some_module.__test__.c
     2  some_module.__test__.d
     1  some_module.sample_func

Duplicate Removal
~~~~~~~~~~~~~~~~~
If a single object jest listed twice (under different names), then tests
will only be generated dla it once:

    >>> z test zaimportuj doctest_aliases
    >>> assert doctest_aliases.TwoNames.f
    >>> assert doctest_aliases.TwoNames.g
    >>> tests = excl_empty_finder.find(doctest_aliases)
    >>> print(len(tests))
    2
    >>> print(tests[0].name)
    test.doctest_aliases.TwoNames

    TwoNames.f oraz TwoNames.g are bound to the same object.
    We can't guess which will be found w doctest's traversal of
    TwoNames.__dict__ first, so we have to allow dla either.

    >>> tests[1].name.split('.')[-1] w ['f', 'g']
    Prawda

Empty Tests
~~~~~~~~~~~
By default, an object przy no doctests doesn't create any tests:

    >>> tests = doctest.DocTestFinder().find(SampleClass)
    >>> dla t w tests:
    ...     print('%2s  %s' % (len(t.examples), t.name))
     3  SampleClass
     3  SampleClass.NestedClass
     1  SampleClass.NestedClass.__init__
     1  SampleClass.__init__
     2  SampleClass.a_classmethod
     1  SampleClass.a_property
     1  SampleClass.a_staticmethod
     1  SampleClass.double
     1  SampleClass.get

By default, that excluded objects przy no doctests.  exclude_empty=Nieprawda
tells it to include (empty) tests dla objects przy no doctests.  This feature
is really to support backward compatibility w what doctest.master.summarize()
displays.

    >>> tests = doctest.DocTestFinder(exclude_empty=Nieprawda).find(SampleClass)
    >>> dla t w tests:
    ...     print('%2s  %s' % (len(t.examples), t.name))
     3  SampleClass
     3  SampleClass.NestedClass
     1  SampleClass.NestedClass.__init__
     0  SampleClass.NestedClass.get
     0  SampleClass.NestedClass.square
     1  SampleClass.__init__
     2  SampleClass.a_classmethod
     1  SampleClass.a_property
     1  SampleClass.a_staticmethod
     1  SampleClass.double
     1  SampleClass.get

Turning off Recursion
~~~~~~~~~~~~~~~~~~~~~
DocTestFinder can be told nie to look dla tests w contained objects
using the `recurse` flag:

    >>> tests = doctest.DocTestFinder(recurse=Nieprawda).find(SampleClass)
    >>> dla t w tests:
    ...     print('%2s  %s' % (len(t.examples), t.name))
     3  SampleClass

Line numbers
~~~~~~~~~~~~
DocTestFinder finds the line number of each example:

    >>> def f(x):
    ...     '''
    ...     >>> x = 12
    ...
    ...     some text
    ...
    ...     >>> # examples are nie created dla comments & bare prompts.
    ...     >>>
    ...     ...
    ...
    ...     >>> dla x w range(10):
    ...     ...     print(x, end=' ')
    ...     0 1 2 3 4 5 6 7 8 9
    ...     >>> x//2
    ...     6
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> [e.lineno dla e w test.examples]
    [1, 9, 12]
"""

    jeżeli int.__doc__: # simple check dla --without-doc-strings, skip jeżeli lacking
        def non_Python_modules(): r"""

Finding Doctests w Modules Not Written w Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DocTestFinder can also find doctests w most modules nie written w Python.
We'll use builtins jako an example, since it almost certainly isn't written w
plain ol' Python oraz jest guaranteed to be available.

    >>> zaimportuj builtins
    >>> tests = doctest.DocTestFinder().find(builtins)
    >>> 790 < len(tests) < 810 # approximate number of objects przy docstrings
    Prawda
    >>> real_tests = [t dla t w tests jeżeli len(t.examples) > 0]
    >>> len(real_tests) # objects that actually have doctests
    8
    >>> dla t w real_tests:
    ...     print('{}  {}'.format(len(t.examples), t.name))
    ...
    1  builtins.bin
    3  builtins.float.as_integer_ratio
    2  builtins.float.fromhex
    2  builtins.float.hex
    1  builtins.hex
    1  builtins.int
    2  builtins.int.bit_length
    1  builtins.oct

Note here that 'bin', 'oct', oraz 'hex' are functions; 'float.as_integer_ratio',
'float.hex', oraz 'int.bit_length' are methods; 'float.fromhex' jest a classmethod,
and 'int' jest a type.
"""

def test_DocTestParser(): r"""
Unit tests dla the `DocTestParser` class.

DocTestParser jest used to parse docstrings containing doctest examples.

The `parse` method divides a docstring into examples oraz intervening
text:

    >>> s = '''
    ...     >>> x, y = 2, 3  # no output expected
    ...     >>> jeżeli 1:
    ...     ...     print(x)
    ...     ...     print(y)
    ...     2
    ...     3
    ...
    ...     Some text.
    ...     >>> x+y
    ...     5
    ...     '''
    >>> parser = doctest.DocTestParser()
    >>> dla piece w parser.parse(s):
    ...     jeżeli isinstance(piece, doctest.Example):
    ...         print('Example:', (piece.source, piece.want, piece.lineno))
    ...     inaczej:
    ...         print('   Text:', repr(piece))
       Text: '\n'
    Example: ('x, y = 2, 3  # no output expected\n', '', 1)
       Text: ''
    Example: ('jeżeli 1:\n    print(x)\n    print(y)\n', '2\n3\n', 2)
       Text: '\nSome text.\n'
    Example: ('x+y\n', '5\n', 9)
       Text: ''

The `get_examples` method returns just the examples:

    >>> dla piece w parser.get_examples(s):
    ...     print((piece.source, piece.want, piece.lineno))
    ('x, y = 2, 3  # no output expected\n', '', 1)
    ('jeżeli 1:\n    print(x)\n    print(y)\n', '2\n3\n', 2)
    ('x+y\n', '5\n', 9)

The `get_doctest` method creates a Test z the examples, along przy the
given arguments:

    >>> test = parser.get_doctest(s, {}, 'name', 'filename', lineno=5)
    >>> (test.name, test.filename, test.lineno)
    ('name', 'filename', 5)
    >>> dla piece w test.examples:
    ...     print((piece.source, piece.want, piece.lineno))
    ('x, y = 2, 3  # no output expected\n', '', 1)
    ('jeżeli 1:\n    print(x)\n    print(y)\n', '2\n3\n', 2)
    ('x+y\n', '5\n', 9)
"""

klasa test_DocTestRunner:
    def basics(): r"""
Unit tests dla the `DocTestRunner` class.

DocTestRunner jest used to run DocTest test cases, oraz to accumulate
statistics.  Here's a simple DocTest case we can use:

    >>> def f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> print(x)
    ...     12
    ...     >>> x//2
    ...     6
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]

The main DocTestRunner interface jest the `run` method, which runs a
given DocTest case w a given namespace (globs).  It returns a tuple
`(f,t)`, where `f` jest the number of failed tests oraz `t` jest the number
of tried tests.

    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=3)

If any example produces incorrect output, then the test runner reports
the failure oraz proceeds to the next example:

    >>> def f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> print(x)
    ...     14
    ...     >>> x//2
    ...     6
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Prawda).run(test)
    ... # doctest: +ELLIPSIS
    Trying:
        x = 12
    Expecting nothing
    ok
    Trying:
        print(x)
    Expecting:
        14
    **********************************************************************
    File ..., line 4, w f
    Failed example:
        print(x)
    Expected:
        14
    Got:
        12
    Trying:
        x//2
    Expecting:
        6
    ok
    TestResults(failed=1, attempted=3)
"""
    def verbose_flag(): r"""
The `verbose` flag makes the test runner generate more detailed
output:

    >>> def f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> print(x)
    ...     12
    ...     >>> x//2
    ...     6
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]

    >>> doctest.DocTestRunner(verbose=Prawda).run(test)
    Trying:
        x = 12
    Expecting nothing
    ok
    Trying:
        print(x)
    Expecting:
        12
    ok
    Trying:
        x//2
    Expecting:
        6
    ok
    TestResults(failed=0, attempted=3)

If the `verbose` flag jest unspecified, then the output will be verbose
iff `-v` appears w sys.argv:

    >>> # Save the real sys.argv list.
    >>> old_argv = sys.argv

    >>> # If -v does nie appear w sys.argv, then output isn't verbose.
    >>> sys.argv = ['test']
    >>> doctest.DocTestRunner().run(test)
    TestResults(failed=0, attempted=3)

    >>> # If -v does appear w sys.argv, then output jest verbose.
    >>> sys.argv = ['test', '-v']
    >>> doctest.DocTestRunner().run(test)
    Trying:
        x = 12
    Expecting nothing
    ok
    Trying:
        print(x)
    Expecting:
        12
    ok
    Trying:
        x//2
    Expecting:
        6
    ok
    TestResults(failed=0, attempted=3)

    >>> # Restore sys.argv
    >>> sys.argv = old_argv

In the remaining examples, the test runner's verbosity will be
explicitly set, to ensure that the test behavior jest consistent.
    """
    def exceptions(): r"""
Tests of `DocTestRunner`'s exception handling.

An expected exception jest specified przy a traceback message.  The
lines between the first line oraz the type/value may be omitted albo
replaced przy any other string:

    >>> def f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> print(x//0)
    ...     Traceback (most recent call last):
    ...     ZeroDivisionError: integer division albo modulo by zero
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=2)

An example may nie generate output before it podnieśs an exception; if
it does, then the traceback message will nie be recognized as
signaling an expected exception, so the example will be reported jako an
unexpected exception:

    >>> def f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> print('pre-exception output', x//0)
    ...     pre-exception output
    ...     Traceback (most recent call last):
    ...     ZeroDivisionError: integer division albo modulo by zero
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 4, w f
    Failed example:
        print('pre-exception output', x//0)
    Exception podnieśd:
        ...
        ZeroDivisionError: integer division albo modulo by zero
    TestResults(failed=1, attempted=2)

Exception messages may contain newlines:

    >>> def f(x):
    ...     r'''
    ...     >>> podnieś ValueError('multi\nline\nmessage')
    ...     Traceback (most recent call last):
    ...     ValueError: multi
    ...     line
    ...     message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=1)

If an exception jest expected, but an exception przy the wrong type albo
message jest podnieśd, then it jest reported jako a failure:

    >>> def f(x):
    ...     r'''
    ...     >>> podnieś ValueError('message')
    ...     Traceback (most recent call last):
    ...     ValueError: wrong message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, w f
    Failed example:
        podnieś ValueError('message')
    Expected:
        Traceback (most recent call last):
        ValueError: wrong message
    Got:
        Traceback (most recent call last):
        ...
        ValueError: message
    TestResults(failed=1, attempted=1)

However, IGNORE_EXCEPTION_DETAIL can be used to allow a mismatch w the
detail:

    >>> def f(x):
    ...     r'''
    ...     >>> podnieś ValueError('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     ValueError: wrong message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=1)

IGNORE_EXCEPTION_DETAIL also ignores difference w exception formatting
between Python versions. For example, w Python 2.x, the module path of
the exception jest nie w the output, but this will fail under Python 3:

    >>> def f(x):
    ...     r'''
    ...     >>> z http.client zaimportuj HTTPException
    ...     >>> podnieś HTTPException('message')
    ...     Traceback (most recent call last):
    ...     HTTPException: message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 4, w f
    Failed example:
        podnieś HTTPException('message')
    Expected:
        Traceback (most recent call last):
        HTTPException: message
    Got:
        Traceback (most recent call last):
        ...
        http.client.HTTPException: message
    TestResults(failed=1, attempted=2)

But w Python 3 the module path jest included, oraz therefore a test must look
like the following test to succeed w Python 3. But that test will fail under
Python 2.

    >>> def f(x):
    ...     r'''
    ...     >>> z http.client zaimportuj HTTPException
    ...     >>> podnieś HTTPException('message')
    ...     Traceback (most recent call last):
    ...     http.client.HTTPException: message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=2)

However, przy IGNORE_EXCEPTION_DETAIL, the module name of the exception
(or its unexpected absence) will be ignored:

    >>> def f(x):
    ...     r'''
    ...     >>> z http.client zaimportuj HTTPException
    ...     >>> podnieś HTTPException('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     HTTPException: message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=2)

The module path will be completely ignored, so two different module paths will
still dalej jeżeli IGNORE_EXCEPTION_DETAIL jest given. This jest intentional, so it can
be used when exceptions have changed module.

    >>> def f(x):
    ...     r'''
    ...     >>> z http.client zaimportuj HTTPException
    ...     >>> podnieś HTTPException('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     foo.bar.HTTPException: message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=2)

But IGNORE_EXCEPTION_DETAIL does nie allow a mismatch w the exception type:

    >>> def f(x):
    ...     r'''
    ...     >>> podnieś ValueError('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     TypeError: wrong type
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, w f
    Failed example:
        podnieś ValueError('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    Expected:
        Traceback (most recent call last):
        TypeError: wrong type
    Got:
        Traceback (most recent call last):
        ...
        ValueError: message
    TestResults(failed=1, attempted=1)

If the exception does nie have a message, you can still use
IGNORE_EXCEPTION_DETAIL to normalize the modules between Python 2 oraz 3:

    >>> def f(x):
    ...     r'''
    ...     >>> z http.client zaimportuj HTTPException
    ...     >>> podnieś HTTPException() #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     foo.bar.HTTPException
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=2)

Note that a trailing colon doesn't matter either:

    >>> def f(x):
    ...     r'''
    ...     >>> z http.client zaimportuj HTTPException
    ...     >>> podnieś HTTPException() #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     foo.bar.HTTPException:
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=2)

If an exception jest podnieśd but nie expected, then it jest reported jako an
unexpected exception:

    >>> def f(x):
    ...     r'''
    ...     >>> 1//0
    ...     0
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, w f
    Failed example:
        1//0
    Exception podnieśd:
        Traceback (most recent call last):
        ...
        ZeroDivisionError: integer division albo modulo by zero
    TestResults(failed=1, attempted=1)
"""
    def displayhook(): r"""
Test that changing sys.displayhook doesn't matter dla doctest.

    >>> zaimportuj sys
    >>> orig_displayhook = sys.displayhook
    >>> def my_displayhook(x):
    ...     print('hi!')
    >>> sys.displayhook = my_displayhook
    >>> def f():
    ...     '''
    ...     >>> 3
    ...     3
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> r = doctest.DocTestRunner(verbose=Nieprawda).run(test)
    >>> post_displayhook = sys.displayhook

    We need to restore sys.displayhook now, so that we'll be able to test
    results.

    >>> sys.displayhook = orig_displayhook

    Ok, now we can check that everything jest ok.

    >>> r
    TestResults(failed=0, attempted=1)
    >>> post_displayhook jest my_displayhook
    Prawda
"""
    def optionflags(): r"""
Tests of `DocTestRunner`'s option flag handling.

Several option flags can be used to customize the behavior of the test
runner.  These are defined jako module constants w doctest, oraz dalejed
to the DocTestRunner constructor (multiple constants should be ORed
together).

The DONT_ACCEPT_TRUE_FOR_1 flag disables matches between Prawda/Nieprawda
and 1/0:

    >>> def f(x):
    ...     '>>> Prawda\n1\n'

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.DONT_ACCEPT_TRUE_FOR_1
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, w f
    Failed example:
        Prawda
    Expected:
        1
    Got:
        Prawda
    TestResults(failed=1, attempted=1)

The DONT_ACCEPT_BLANKLINE flag disables the match between blank lines
and the '<BLANKLINE>' marker:

    >>> def f(x):
    ...     '>>> print("a\\n\\nb")\na\n<BLANKLINE>\nb\n'

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.DONT_ACCEPT_BLANKLINE
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, w f
    Failed example:
        print("a\n\nb")
    Expected:
        a
        <BLANKLINE>
        b
    Got:
        a
    <BLANKLINE>
        b
    TestResults(failed=1, attempted=1)

The NORMALIZE_WHITESPACE flag causes all sequences of whitespace to be
treated jako equal:

    >>> def f(x):
    ...     '>>> print(1, 2, 3)\n  1   2\n 3'

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, w f
    Failed example:
        print(1, 2, 3)
    Expected:
          1   2
         3
    Got:
        1 2 3
    TestResults(failed=1, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.NORMALIZE_WHITESPACE
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    TestResults(failed=0, attempted=1)

    An example z the docs:
    >>> print(list(range(20))) #doctest: +NORMALIZE_WHITESPACE
    [0,   1,  2,  3,  4,  5,  6,  7,  8,  9,
    10,  11, 12, 13, 14, 15, 16, 17, 18, 19]

The ELLIPSIS flag causes ellipsis marker ("...") w the expected
output to match any substring w the actual output:

    >>> def f(x):
    ...     '>>> print(list(range(15)))\n[0, 1, 2, ..., 14]\n'

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, w f
    Failed example:
        print(list(range(15)))
    Expected:
        [0, 1, 2, ..., 14]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    TestResults(failed=1, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.ELLIPSIS
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    TestResults(failed=0, attempted=1)

    ... also matches nothing:

    >>> jeżeli 1:
    ...     dla i w range(100):
    ...         print(i**2, end=' ') #doctest: +ELLIPSIS
    ...     print('!')
    0 1...4...9 16 ... 36 49 64 ... 9801 !

    ... can be surprising; e.g., this test dalejes:

    >>> jeżeli 1:  #doctest: +ELLIPSIS
    ...     dla i w range(20):
    ...         print(i, end=' ')
    ...     print(20)
    0 1 2 ...1...2...0

    Examples z the docs:

    >>> print(list(range(20))) # doctest:+ELLIPSIS
    [0, 1, ..., 18, 19]

    >>> print(list(range(20))) # doctest: +ELLIPSIS
    ...                 # doctest: +NORMALIZE_WHITESPACE
    [0,    1, ...,   18,    19]

The SKIP flag causes an example to be skipped entirely.  I.e., the
example jest nie run.  It can be useful w contexts where doctest
examples serve jako both documentation oraz test cases, oraz an example
should be included dla documentation purposes, but should nie be
checked (e.g., because its output jest random, albo depends on resources
which would be unavailable.)  The SKIP flag can also be used for
'commenting out' broken examples.

    >>> zaimportuj unavailable_resource           # doctest: +SKIP
    >>> unavailable_resource.do_something()   # doctest: +SKIP
    >>> unavailable_resource.blow_up()        # doctest: +SKIP
    Traceback (most recent call last):
        ...
    UncheckedBlowUpError:  Nobody checks me.

    >>> zaimportuj random
    >>> print(random.random()) # doctest: +SKIP
    0.721216923889

The REPORT_UDIFF flag causes failures that involve multi-line expected
and actual outputs to be displayed using a unified diff:

    >>> def f(x):
    ...     r'''
    ...     >>> print('\n'.join('abcdefg'))
    ...     a
    ...     B
    ...     c
    ...     d
    ...     f
    ...     g
    ...     h
    ...     '''

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, w f
    Failed example:
        print('\n'.join('abcdefg'))
    Expected:
        a
        B
        c
        d
        f
        g
        h
    Got:
        a
        b
        c
        d
        e
        f
        g
    TestResults(failed=1, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_UDIFF
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, w f
    Failed example:
        print('\n'.join('abcdefg'))
    Differences (unified diff przy -expected +actual):
        @@ -1,7 +1,7 @@
         a
        -B
        +b
         c
         d
        +e
         f
         g
        -h
    TestResults(failed=1, attempted=1)

The REPORT_CDIFF flag causes failures that involve multi-line expected
and actual outputs to be displayed using a context diff:

    >>> # Reuse f() z the REPORT_UDIFF example, above.
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_CDIFF
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, w f
    Failed example:
        print('\n'.join('abcdefg'))
    Differences (context diff przy expected followed by actual):
        ***************
        *** 1,7 ****
          a
        ! B
          c
          d
          f
          g
        - h
        --- 1,7 ----
          a
        ! b
          c
          d
        + e
          f
          g
    TestResults(failed=1, attempted=1)


The REPORT_NDIFF flag causes failures to use the difflib.Differ algorithm
used by the popular ndiff.py utility.  This does intraline difference
marking, jako well jako interline differences.

    >>> def f(x):
    ...     r'''
    ...     >>> print("a b  c d e f g h i   j k l m")
    ...     a b c d e f g h i j k 1 m
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_NDIFF
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, w f
    Failed example:
        print("a b  c d e f g h i   j k l m")
    Differences (ndiff przy -expected +actual):
        - a b c d e f g h i j k 1 m
        ?                       ^
        + a b  c d e f g h i   j k l m
        ?     +              ++    ^
    TestResults(failed=1, attempted=1)

The REPORT_ONLY_FIRST_FAILURE suppresses result output after the first
failing example:

    >>> def f(x):
    ...     r'''
    ...     >>> print(1) # first success
    ...     1
    ...     >>> print(2) # first failure
    ...     200
    ...     >>> print(3) # second failure
    ...     300
    ...     >>> print(4) # second success
    ...     4
    ...     >>> print(5) # third failure
    ...     500
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_ONLY_FIRST_FAILURE
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, w f
    Failed example:
        print(2) # first failure
    Expected:
        200
    Got:
        2
    TestResults(failed=3, attempted=5)

However, output z `report_start` jest nie suppressed:

    >>> doctest.DocTestRunner(verbose=Prawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    Trying:
        print(1) # first success
    Expecting:
        1
    ok
    Trying:
        print(2) # first failure
    Expecting:
        200
    **********************************************************************
    File ..., line 5, w f
    Failed example:
        print(2) # first failure
    Expected:
        200
    Got:
        2
    TestResults(failed=3, attempted=5)

The FAIL_FAST flag causes the runner to exit after the first failing example,
so subsequent examples are nie even attempted:

    >>> flags = doctest.FAIL_FAST
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, w f
    Failed example:
        print(2) # first failure
    Expected:
        200
    Got:
        2
    TestResults(failed=1, attempted=2)

Specifying both FAIL_FAST oraz REPORT_ONLY_FIRST_FAILURE jest equivalent to
FAIL_FAST only:

    >>> flags = doctest.FAIL_FAST | doctest.REPORT_ONLY_FIRST_FAILURE
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, w f
    Failed example:
        print(2) # first failure
    Expected:
        200
    Got:
        2
    TestResults(failed=1, attempted=2)

For the purposes of both REPORT_ONLY_FIRST_FAILURE oraz FAIL_FAST, unexpected
exceptions count jako failures:

    >>> def f(x):
    ...     r'''
    ...     >>> print(1) # first success
    ...     1
    ...     >>> podnieś ValueError(2) # first failure
    ...     200
    ...     >>> print(3) # second failure
    ...     300
    ...     >>> print(4) # second success
    ...     4
    ...     >>> print(5) # third failure
    ...     500
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_ONLY_FIRST_FAILURE
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, w f
    Failed example:
        podnieś ValueError(2) # first failure
    Exception podnieśd:
        ...
        ValueError: 2
    TestResults(failed=3, attempted=5)
    >>> flags = doctest.FAIL_FAST
    >>> doctest.DocTestRunner(verbose=Nieprawda, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, w f
    Failed example:
        podnieś ValueError(2) # first failure
    Exception podnieśd:
        ...
        ValueError: 2
    TestResults(failed=1, attempted=2)

New option flags can also be registered, via register_optionflag().  Here
we reach into doctest's internals a bit.

    >>> unlikely = "UNLIKELY_OPTION_NAME"
    >>> unlikely w doctest.OPTIONFLAGS_BY_NAME
    Nieprawda
    >>> new_flag_value = doctest.register_optionflag(unlikely)
    >>> unlikely w doctest.OPTIONFLAGS_BY_NAME
    Prawda

Before 2.4.4/2.5, registering a name more than once erroneously created
more than one flag value.  Here we verify that's fixed:

    >>> redundant_flag_value = doctest.register_optionflag(unlikely)
    >>> redundant_flag_value == new_flag_value
    Prawda

Clean up.
    >>> usuń doctest.OPTIONFLAGS_BY_NAME[unlikely]

    """

    def option_directives(): r"""
Tests of `DocTestRunner`'s option directive mechanism.

Option directives can be used to turn option flags on albo off dla a
single example.  To turn an option on dla an example, follow that
example przy a comment of the form ``# doctest: +OPTION``:

    >>> def f(x): r'''
    ...     >>> print(list(range(10)))      # should fail: no ellipsis
    ...     [0, 1, ..., 9]
    ...
    ...     >>> print(list(range(10)))      # doctest: +ELLIPSIS
    ...     [0, 1, ..., 9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, w f
    Failed example:
        print(list(range(10)))      # should fail: no ellipsis
    Expected:
        [0, 1, ..., 9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

To turn an option off dla an example, follow that example przy a
comment of the form ``# doctest: -OPTION``:

    >>> def f(x): r'''
    ...     >>> print(list(range(10)))
    ...     [0, 1, ..., 9]
    ...
    ...     >>> # should fail: no ellipsis
    ...     >>> print(list(range(10)))      # doctest: -ELLIPSIS
    ...     [0, 1, ..., 9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda,
    ...                       optionflags=doctest.ELLIPSIS).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 6, w f
    Failed example:
        print(list(range(10)))      # doctest: -ELLIPSIS
    Expected:
        [0, 1, ..., 9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

Option directives affect only the example that they appear with; they
do nie change the options dla surrounding examples:

    >>> def f(x): r'''
    ...     >>> print(list(range(10)))      # Should fail: no ellipsis
    ...     [0, 1, ..., 9]
    ...
    ...     >>> print(list(range(10)))      # doctest: +ELLIPSIS
    ...     [0, 1, ..., 9]
    ...
    ...     >>> print(list(range(10)))      # Should fail: no ellipsis
    ...     [0, 1, ..., 9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, w f
    Failed example:
        print(list(range(10)))      # Should fail: no ellipsis
    Expected:
        [0, 1, ..., 9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    **********************************************************************
    File ..., line 8, w f
    Failed example:
        print(list(range(10)))      # Should fail: no ellipsis
    Expected:
        [0, 1, ..., 9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=2, attempted=3)

Multiple options may be modified by a single option directive.  They
may be separated by whitespace, commas, albo both:

    >>> def f(x): r'''
    ...     >>> print(list(range(10)))      # Should fail
    ...     [0, 1,  ...,   9]
    ...     >>> print(list(range(10)))      # Should succeed
    ...     ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ...     [0, 1,  ...,   9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, w f
    Failed example:
        print(list(range(10)))      # Should fail
    Expected:
        [0, 1,  ...,   9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

    >>> def f(x): r'''
    ...     >>> print(list(range(10)))      # Should fail
    ...     [0, 1,  ...,   9]
    ...     >>> print(list(range(10)))      # Should succeed
    ...     ... # doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
    ...     [0, 1,  ...,   9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, w f
    Failed example:
        print(list(range(10)))      # Should fail
    Expected:
        [0, 1,  ...,   9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

    >>> def f(x): r'''
    ...     >>> print(list(range(10)))      # Should fail
    ...     [0, 1,  ...,   9]
    ...     >>> print(list(range(10)))      # Should succeed
    ...     ... # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ...     [0, 1,  ...,   9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, w f
    Failed example:
        print(list(range(10)))      # Should fail
    Expected:
        [0, 1,  ...,   9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

The option directive may be put on the line following the source, as
long jako a continuation prompt jest used:

    >>> def f(x): r'''
    ...     >>> print(list(range(10)))
    ...     ... # doctest: +ELLIPSIS
    ...     [0, 1, ..., 9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=1)

For examples przy multi-line source, the option directive may appear
at the end of any line:

    >>> def f(x): r'''
    ...     >>> dla x w range(10): # doctest: +ELLIPSIS
    ...     ...     print(' ', x, end='', sep='')
    ...      0 1 2 ... 9
    ...
    ...     >>> dla x w range(10):
    ...     ...     print(' ', x, end='', sep='') # doctest: +ELLIPSIS
    ...      0 1 2 ... 9
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=2)

If more than one line of an example przy multi-line source has an
option directive, then they are combined:

    >>> def f(x): r'''
    ...     Should fail (option directive nie on the last line):
    ...         >>> dla x w range(10): # doctest: +ELLIPSIS
    ...         ...     print(x, end=' ') # doctest: +NORMALIZE_WHITESPACE
    ...         0  1    2...9
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Nieprawda).run(test)
    TestResults(failed=0, attempted=1)

It jest an error to have a comment of the form ``# doctest:`` that jest
*not* followed by words of the form ``+OPTION`` albo ``-OPTION``, where
``OPTION`` jest an option that has been registered with
`register_option`:

    >>> # Error: Option nie registered
    >>> s = '>>> print(12)  #doctest: +BADOPTION'
    >>> test = doctest.DocTestParser().get_doctest(s, {}, 's', 's.py', 0)
    Traceback (most recent call last):
    ValueError: line 1 of the doctest dla s has an invalid option: '+BADOPTION'

    >>> # Error: No + albo - prefix
    >>> s = '>>> print(12)  #doctest: ELLIPSIS'
    >>> test = doctest.DocTestParser().get_doctest(s, {}, 's', 's.py', 0)
    Traceback (most recent call last):
    ValueError: line 1 of the doctest dla s has an invalid option: 'ELLIPSIS'

It jest an error to use an option directive on a line that contains no
source:

    >>> s = '>>> # doctest: +ELLIPSIS'
    >>> test = doctest.DocTestParser().get_doctest(s, {}, 's', 's.py', 0)
    Traceback (most recent call last):
    ValueError: line 0 of the doctest dla s has an option directive on a line przy no example: '# doctest: +ELLIPSIS'
"""

def test_testsource(): r"""
Unit tests dla `testsource()`.

The testsource() function takes a module oraz a name, finds the (first)
test przy that name w that module, oraz converts it to a script. The
example code jest converted to regular Python code.  The surrounding
words oraz expected output are converted to comments:

    >>> zaimportuj test.test_doctest
    >>> name = 'test.test_doctest.sample_func'
    >>> print(doctest.testsource(test.test_doctest, name))
    # Blah blah
    #
    print(sample_func(22))
    # Expected:
    ## 44
    #
    # Yee ha!
    <BLANKLINE>

    >>> name = 'test.test_doctest.SampleNewStyleClass'
    >>> print(doctest.testsource(test.test_doctest, name))
    print('1\n2\n3')
    # Expected:
    ## 1
    ## 2
    ## 3
    <BLANKLINE>

    >>> name = 'test.test_doctest.SampleClass.a_classmethod'
    >>> print(doctest.testsource(test.test_doctest, name))
    print(SampleClass.a_classmethod(10))
    # Expected:
    ## 12
    print(SampleClass(0).a_classmethod(10))
    # Expected:
    ## 12
    <BLANKLINE>
"""

def test_debug(): r"""

Create a docstring that we want to debug:

    >>> s = '''
    ...     >>> x = 12
    ...     >>> print(x)
    ...     12
    ...     '''

Create some fake stdin input, to feed to the debugger:

    >>> real_stdin = sys.stdin
    >>> sys.stdin = _FakeInput(['next', 'print(x)', 'continue'])

Run the debugger on the docstring, oraz then restore sys.stdin.

    >>> spróbuj: doctest.debug_src(s)
    ... w_końcu: sys.stdin = real_stdin
    > <string>(1)<module>()
    (Pdb) next
    12
    --Return--
    > <string>(1)<module>()->Nic
    (Pdb) print(x)
    12
    (Pdb) kontynuuj

"""

jeżeli nie hasattr(sys, 'gettrace') albo nie sys.gettrace():
    def test_pdb_set_trace():
        """Using pdb.set_trace z a doctest.

        You can use pdb.set_trace z a doctest.  To do so, you must
        retrieve the set_trace function z the pdb module at the time
        you use it.  The doctest module changes sys.stdout so that it can
        capture program output.  It also temporarily replaces pdb.set_trace
        przy a version that restores stdout.  This jest necessary dla you to
        see debugger output.

          >>> doc = '''
          ... >>> x = 42
          ... >>> podnieś Exception('clé')
          ... Traceback (most recent call last):
          ... Exception: clé
          ... >>> zaimportuj pdb; pdb.set_trace()
          ... '''
          >>> parser = doctest.DocTestParser()
          >>> test = parser.get_doctest(doc, {}, "foo-bar@baz", "foo-bar@baz.py", 0)
          >>> runner = doctest.DocTestRunner(verbose=Nieprawda)

        To demonstrate this, we'll create a fake standard input that
        captures our debugger input:

          >>> zaimportuj tempfile
          >>> real_stdin = sys.stdin
          >>> sys.stdin = _FakeInput([
          ...    'print(x)',  # print data defined by the example
          ...    'continue', # stop debugging
          ...    ''])

          >>> spróbuj: runner.run(test)
          ... w_końcu: sys.stdin = real_stdin
          --Return--
          > <doctest foo-bar@baz[2]>(1)<module>()->Nic
          -> zaimportuj pdb; pdb.set_trace()
          (Pdb) print(x)
          42
          (Pdb) kontynuuj
          TestResults(failed=0, attempted=3)

          You can also put pdb.set_trace w a function called z a test:

          >>> def calls_set_trace():
          ...    y=2
          ...    zaimportuj pdb; pdb.set_trace()

          >>> doc = '''
          ... >>> x=1
          ... >>> calls_set_trace()
          ... '''
          >>> test = parser.get_doctest(doc, globals(), "foo-bar@baz", "foo-bar@baz.py", 0)
          >>> real_stdin = sys.stdin
          >>> sys.stdin = _FakeInput([
          ...    'print(y)',  # print data defined w the function
          ...    'up',       # out of function
          ...    'print(x)',  # print data defined by the example
          ...    'continue', # stop debugging
          ...    ''])

          >>> spróbuj:
          ...     runner.run(test)
          ... w_końcu:
          ...     sys.stdin = real_stdin
          --Return--
          > <doctest test.test_doctest.test_pdb_set_trace[8]>(3)calls_set_trace()->Nic
          -> zaimportuj pdb; pdb.set_trace()
          (Pdb) print(y)
          2
          (Pdb) up
          > <doctest foo-bar@baz[1]>(1)<module>()
          -> calls_set_trace()
          (Pdb) print(x)
          1
          (Pdb) kontynuuj
          TestResults(failed=0, attempted=2)

        During interactive debugging, source code jest shown, even for
        doctest examples:

          >>> doc = '''
          ... >>> def f(x):
          ... ...     g(x*2)
          ... >>> def g(x):
          ... ...     print(x+3)
          ... ...     zaimportuj pdb; pdb.set_trace()
          ... >>> f(3)
          ... '''
          >>> test = parser.get_doctest(doc, globals(), "foo-bar@baz", "foo-bar@baz.py", 0)
          >>> real_stdin = sys.stdin
          >>> sys.stdin = _FakeInput([
          ...    'list',     # list source z example 2
          ...    'next',     # zwróć z g()
          ...    'list',     # list source z example 1
          ...    'next',     # zwróć z f()
          ...    'list',     # list source z example 3
          ...    'continue', # stop debugging
          ...    ''])
          >>> spróbuj: runner.run(test)
          ... w_końcu: sys.stdin = real_stdin
          ... # doctest: +NORMALIZE_WHITESPACE
          --Return--
          > <doctest foo-bar@baz[1]>(3)g()->Nic
          -> zaimportuj pdb; pdb.set_trace()
          (Pdb) list
            1     def g(x):
            2         print(x+3)
            3  ->     zaimportuj pdb; pdb.set_trace()
          [EOF]
          (Pdb) next
          --Return--
          > <doctest foo-bar@baz[0]>(2)f()->Nic
          -> g(x*2)
          (Pdb) list
            1     def f(x):
            2  ->     g(x*2)
          [EOF]
          (Pdb) next
          --Return--
          > <doctest foo-bar@baz[2]>(1)<module>()->Nic
          -> f(3)
          (Pdb) list
            1  -> f(3)
          [EOF]
          (Pdb) kontynuuj
          **********************************************************************
          File "foo-bar@baz.py", line 7, w foo-bar@baz
          Failed example:
              f(3)
          Expected nothing
          Got:
              9
          TestResults(failed=1, attempted=3)
          """

    def test_pdb_set_trace_nested():
        """This illustrates more-demanding use of set_trace przy nested functions.

        >>> klasa C(object):
        ...     def calls_set_trace(self):
        ...         y = 1
        ...         zaimportuj pdb; pdb.set_trace()
        ...         self.f1()
        ...         y = 2
        ...     def f1(self):
        ...         x = 1
        ...         self.f2()
        ...         x = 2
        ...     def f2(self):
        ...         z = 1
        ...         z = 2

        >>> calls_set_trace = C().calls_set_trace

        >>> doc = '''
        ... >>> a = 1
        ... >>> calls_set_trace()
        ... '''
        >>> parser = doctest.DocTestParser()
        >>> runner = doctest.DocTestRunner(verbose=Nieprawda)
        >>> test = parser.get_doctest(doc, globals(), "foo-bar@baz", "foo-bar@baz.py", 0)
        >>> real_stdin = sys.stdin
        >>> sys.stdin = _FakeInput([
        ...    'print(y)',  # print data defined w the function
        ...    'step', 'step', 'step', 'step', 'step', 'step', 'print(z)',
        ...    'up', 'print(x)',
        ...    'up', 'print(y)',
        ...    'up', 'print(foo)',
        ...    'continue', # stop debugging
        ...    ''])

        >>> spróbuj:
        ...     runner.run(test)
        ... w_końcu:
        ...     sys.stdin = real_stdin
        ... # doctest: +REPORT_NDIFF
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(5)calls_set_trace()
        -> self.f1()
        (Pdb) print(y)
        1
        (Pdb) step
        --Call--
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(7)f1()
        -> def f1(self):
        (Pdb) step
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(8)f1()
        -> x = 1
        (Pdb) step
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(9)f1()
        -> self.f2()
        (Pdb) step
        --Call--
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(11)f2()
        -> def f2(self):
        (Pdb) step
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(12)f2()
        -> z = 1
        (Pdb) step
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(13)f2()
        -> z = 2
        (Pdb) print(z)
        1
        (Pdb) up
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(9)f1()
        -> self.f2()
        (Pdb) print(x)
        1
        (Pdb) up
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(5)calls_set_trace()
        -> self.f1()
        (Pdb) print(y)
        1
        (Pdb) up
        > <doctest foo-bar@baz[1]>(1)<module>()
        -> calls_set_trace()
        (Pdb) print(foo)
        *** NameError: name 'foo' jest nie defined
        (Pdb) kontynuuj
        TestResults(failed=0, attempted=2)
    """

def test_DocTestSuite():
    """DocTestSuite creates a unittest test suite z a doctest.

       We create a Suite by providing a module.  A module can be provided
       by dalejing a module object:

         >>> zaimportuj unittest
         >>> zaimportuj test.sample_doctest
         >>> suite = doctest.DocTestSuite(test.sample_doctest)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=4>

       We can also supply the module by name:

         >>> suite = doctest.DocTestSuite('test.sample_doctest')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=4>

       The module need nie contain any doctest examples:

         >>> suite = doctest.DocTestSuite('test.sample_doctest_no_doctests')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=0 errors=0 failures=0>

       The module need nie contain any docstrings either:

         >>> suite = doctest.DocTestSuite('test.sample_doctest_no_docstrings')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=0 errors=0 failures=0>

       We can use the current module:

         >>> suite = test.sample_doctest.test_suite()
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=4>

       We can also provide a DocTestFinder:

         >>> finder = doctest.DocTestFinder()
         >>> suite = doctest.DocTestSuite('test.sample_doctest',
         ...                          test_finder=finder)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=4>

       The DocTestFinder need nie zwróć any tests:

         >>> finder = doctest.DocTestFinder()
         >>> suite = doctest.DocTestSuite('test.sample_doctest_no_docstrings',
         ...                          test_finder=finder)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=0 errors=0 failures=0>

       We can supply global variables.  If we dalej globs, they will be
       used instead of the module globals.  Here we'll dalej an empty
       globals, triggering an extra error:

         >>> suite = doctest.DocTestSuite('test.sample_doctest', globs={})
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=5>

       Alternatively, we can provide extra globals.  Here we'll make an
       error go away by providing an extra global variable:

         >>> suite = doctest.DocTestSuite('test.sample_doctest',
         ...                              extraglobs={'y': 1})
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=3>

       You can dalej option flags.  Here we'll cause an extra error
       by disabling the blank-line feature:

         >>> suite = doctest.DocTestSuite('test.sample_doctest',
         ...                      optionflags=doctest.DONT_ACCEPT_BLANKLINE)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=5>

       You can supply setUp oraz tearDown functions:

         >>> def setUp(t):
         ...     zaimportuj test.test_doctest
         ...     test.test_doctest.sillySetup = Prawda

         >>> def tearDown(t):
         ...     zaimportuj test.test_doctest
         ...     usuń test.test_doctest.sillySetup

       Here, we installed a silly variable that the test expects:

         >>> suite = doctest.DocTestSuite('test.sample_doctest',
         ...      setUp=setUp, tearDown=tearDown)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=3>

       But the tearDown restores sanity:

         >>> zaimportuj test.test_doctest
         >>> test.test_doctest.sillySetup
         Traceback (most recent call last):
         ...
         AttributeError: module 'test.test_doctest' has no attribute 'sillySetup'

       The setUp oraz tearDown functions are dalejed test objects. Here
       we'll use the setUp function to supply the missing variable y:

         >>> def setUp(test):
         ...     test.globs['y'] = 1

         >>> suite = doctest.DocTestSuite('test.sample_doctest', setUp=setUp)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=3>

       Here, we didn't need to use a tearDown function because we
       modified the test globals, which are a copy of the
       sample_doctest module dictionary.  The test globals are
       automatically cleared dla us after a test.
       """

def test_DocFileSuite():
    """We can test tests found w text files using a DocFileSuite.

       We create a suite by providing the names of one albo more text
       files that include examples:

         >>> zaimportuj unittest
         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=2>

       The test files are looked dla w the directory containing the
       calling module.  A package keyword argument can be provided to
       specify a different relative location.

         >>> zaimportuj unittest
         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                              package='test')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=2>

       Support dla using a package's __loader__.get_data() jest also
       provided.

         >>> zaimportuj unittest, pkgutil, test
         >>> added_loader = Nieprawda
         >>> jeżeli nie hasattr(test, '__loader__'):
         ...     test.__loader__ = pkgutil.get_loader(test)
         ...     added_loader = Prawda
         >>> spróbuj:
         ...     suite = doctest.DocFileSuite('test_doctest.txt',
         ...                                  'test_doctest2.txt',
         ...                                  'test_doctest4.txt',
         ...                                  package='test')
         ...     suite.run(unittest.TestResult())
         ... w_końcu:
         ...     jeżeli added_loader:
         ...         usuń test.__loader__
         <unittest.result.TestResult run=3 errors=0 failures=2>

       '/' should be used jako a path separator.  It will be converted
       to a native separator at run time:

         >>> suite = doctest.DocFileSuite('../test/test_doctest.txt')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=1 errors=0 failures=1>

       If DocFileSuite jest used z an interactive session, then files
       are resolved relative to the directory of sys.argv[0]:

         >>> zaimportuj types, os.path, test.test_doctest
         >>> save_argv = sys.argv
         >>> sys.argv = [test.test_doctest.__file__]
         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              package=types.ModuleType('__main__'))
         >>> sys.argv = save_argv

       By setting `module_relative=Nieprawda`, os-specific paths may be
       used (including absolute paths oraz paths relative to the
       working directory):

         >>> # Get the absolute path of the test package.
         >>> test_doctest_path = os.path.abspath(test.test_doctest.__file__)
         >>> test_pkg_path = os.path.split(test_doctest_path)[0]

         >>> # Use it to find the absolute path of test_doctest.txt.
         >>> test_file = os.path.join(test_pkg_path, 'test_doctest.txt')

         >>> suite = doctest.DocFileSuite(test_file, module_relative=Nieprawda)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=1 errors=0 failures=1>

       It jest an error to specify `package` when `module_relative=Nieprawda`:

         >>> suite = doctest.DocFileSuite(test_file, module_relative=Nieprawda,
         ...                              package='test')
         Traceback (most recent call last):
         ValueError: Package may only be specified dla module-relative paths.

       You can specify initial global variables:

         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                              globs={'favorite_color': 'blue'})
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=1>

       In this case, we supplied a missing favorite color. You can
       provide doctest options:

         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                         optionflags=doctest.DONT_ACCEPT_BLANKLINE,
         ...                              globs={'favorite_color': 'blue'})
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=2>

       And, you can provide setUp oraz tearDown functions:

         >>> def setUp(t):
         ...     zaimportuj test.test_doctest
         ...     test.test_doctest.sillySetup = Prawda

         >>> def tearDown(t):
         ...     zaimportuj test.test_doctest
         ...     usuń test.test_doctest.sillySetup

       Here, we installed a silly variable that the test expects:

         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                              setUp=setUp, tearDown=tearDown)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=1>

       But the tearDown restores sanity:

         >>> zaimportuj test.test_doctest
         >>> test.test_doctest.sillySetup
         Traceback (most recent call last):
         ...
         AttributeError: module 'test.test_doctest' has no attribute 'sillySetup'

       The setUp oraz tearDown functions are dalejed test objects.
       Here, we'll use a setUp function to set the favorite color w
       test_doctest.txt:

         >>> def setUp(test):
         ...     test.globs['favorite_color'] = 'blue'

         >>> suite = doctest.DocFileSuite('test_doctest.txt', setUp=setUp)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=1 errors=0 failures=0>

       Here, we didn't need to use a tearDown function because we
       modified the test globals.  The test globals are
       automatically cleared dla us after a test.

       Tests w a file run using `DocFileSuite` can also access the
       `__file__` global, which jest set to the name of the file
       containing the tests:

         >>> suite = doctest.DocFileSuite('test_doctest3.txt')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=1 errors=0 failures=0>

       If the tests contain non-ASCII characters, we have to specify which
       encoding the file jest encoded with. We do so by using the `encoding`
       parameter:

         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                              encoding='utf-8')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=2>

       """

def test_trailing_space_in_test():
    """
    Trailing spaces w expected output are significant:

      >>> x, y = 'foo', ''
      >>> print(x, y)
      foo \n
    """

klasa Wrapper:
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)

@Wrapper
def test_look_in_unwrapped():
    """
    Docstrings w wrapped functions must be detected jako well.

    >>> 'one other test'
    'one other test'
    """

def test_unittest_reportflags():
    """Default unittest reporting flags can be set to control reporting

    Here, we'll set the REPORT_ONLY_FIRST_FAILURE option so we see
    only the first failure of each test.  First, we'll look at the
    output without the flag.  The file test_doctest.txt file has two
    tests. They both fail jeżeli blank lines are disabled:

      >>> suite = doctest.DocFileSuite('test_doctest.txt',
      ...                          optionflags=doctest.DONT_ACCEPT_BLANKLINE)
      >>> zaimportuj unittest
      >>> result = suite.run(unittest.TestResult())
      >>> print(result.failures[0][1]) # doctest: +ELLIPSIS
      Traceback ...
      Failed example:
          favorite_color
      ...
      Failed example:
          jeżeli 1:
      ...

    Note that we see both failures displayed.

      >>> old = doctest.set_unittest_reportflags(
      ...    doctest.REPORT_ONLY_FIRST_FAILURE)

    Now, when we run the test:

      >>> result = suite.run(unittest.TestResult())
      >>> print(result.failures[0][1]) # doctest: +ELLIPSIS
      Traceback ...
      Failed example:
          favorite_color
      Exception podnieśd:
          ...
          NameError: name 'favorite_color' jest nie defined
      <BLANKLINE>
      <BLANKLINE>

    We get only the first failure.

    If we give any reporting options when we set up the tests,
    however:

      >>> suite = doctest.DocFileSuite('test_doctest.txt',
      ...     optionflags=doctest.DONT_ACCEPT_BLANKLINE | doctest.REPORT_NDIFF)

    Then the default eporting options are ignored:

      >>> result = suite.run(unittest.TestResult())
      >>> print(result.failures[0][1]) # doctest: +ELLIPSIS
      Traceback ...
      Failed example:
          favorite_color
      ...
      Failed example:
          jeżeli 1:
             print('a')
             print()
             print('b')
      Differences (ndiff przy -expected +actual):
            a
          - <BLANKLINE>
          +
            b
      <BLANKLINE>
      <BLANKLINE>


    Test runners can restore the formatting flags after they run:

      >>> ignored = doctest.set_unittest_reportflags(old)

    """

def test_testfile(): r"""
Tests dla the `testfile()` function.  This function runs all the
doctest examples w a given file.  In its simple invokation, it jest
called przy the name of a file, which jest taken to be relative to the
calling module.  The zwróć value jest (#failures, #tests).

We don't want `-v` w sys.argv dla these tests.

    >>> save_argv = sys.argv
    >>> jeżeli '-v' w sys.argv:
    ...     sys.argv = [arg dla arg w save_argv jeżeli arg != '-v']


    >>> doctest.testfile('test_doctest.txt') # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 6, w test_doctest.txt
    Failed example:
        favorite_color
    Exception podnieśd:
        ...
        NameError: name 'favorite_color' jest nie defined
    **********************************************************************
    1 items had failures:
       1 of   2 w test_doctest.txt
    ***Test Failed*** 1 failures.
    TestResults(failed=1, attempted=2)
    >>> doctest.master = Nic  # Reset master.

(Note: we'll be clearing doctest.master after each call to
`doctest.testfile`, to suppress warnings about multiple tests przy the
same name.)

Globals may be specified przy the `globs` oraz `extraglobs` parameters:

    >>> globs = {'favorite_color': 'blue'}
    >>> doctest.testfile('test_doctest.txt', globs=globs)
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Nic  # Reset master.

    >>> extraglobs = {'favorite_color': 'red'}
    >>> doctest.testfile('test_doctest.txt', globs=globs,
    ...                  extraglobs=extraglobs) # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 6, w test_doctest.txt
    Failed example:
        favorite_color
    Expected:
        'blue'
    Got:
        'red'
    **********************************************************************
    1 items had failures:
       1 of   2 w test_doctest.txt
    ***Test Failed*** 1 failures.
    TestResults(failed=1, attempted=2)
    >>> doctest.master = Nic  # Reset master.

The file may be made relative to a given module albo package, using the
optional `module_relative` parameter:

    >>> doctest.testfile('test_doctest.txt', globs=globs,
    ...                  module_relative='test')
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Nic  # Reset master.

Verbosity can be increased przy the optional `verbose` parameter:

    >>> doctest.testfile('test_doctest.txt', globs=globs, verbose=Prawda)
    Trying:
        favorite_color
    Expecting:
        'blue'
    ok
    Trying:
        jeżeli 1:
           print('a')
           print()
           print('b')
    Expecting:
        a
        <BLANKLINE>
        b
    ok
    1 items dalejed all tests:
       2 tests w test_doctest.txt
    2 tests w 1 items.
    2 dalejed oraz 0 failed.
    Test dalejed.
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Nic  # Reset master.

The name of the test may be specified przy the optional `name`
parameter:

    >>> doctest.testfile('test_doctest.txt', name='newname')
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 6, w newname
    ...
    TestResults(failed=1, attempted=2)
    >>> doctest.master = Nic  # Reset master.

The summary report may be suppressed przy the optional `report`
parameter:

    >>> doctest.testfile('test_doctest.txt', report=Nieprawda)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 6, w test_doctest.txt
    Failed example:
        favorite_color
    Exception podnieśd:
        ...
        NameError: name 'favorite_color' jest nie defined
    TestResults(failed=1, attempted=2)
    >>> doctest.master = Nic  # Reset master.

The optional keyword argument `raise_on_error` can be used to podnieś an
exception on the first error (which may be useful dla postmortem
debugging):

    >>> doctest.testfile('test_doctest.txt', podnieś_on_error=Prawda)
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    doctest.UnexpectedException: ...
    >>> doctest.master = Nic  # Reset master.

If the tests contain non-ASCII characters, the tests might fail, since
it's unknown which encoding jest used. The encoding can be specified
using the optional keyword argument `encoding`:

    >>> doctest.testfile('test_doctest4.txt', encoding='latin-1') # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 7, w test_doctest4.txt
    Failed example:
        '...'
    Expected:
        'f\xf6\xf6'
    Got:
        'f\xc3\xb6\xc3\xb6'
    **********************************************************************
    ...
    **********************************************************************
    1 items had failures:
       2 of   2 w test_doctest4.txt
    ***Test Failed*** 2 failures.
    TestResults(failed=2, attempted=2)
    >>> doctest.master = Nic  # Reset master.

    >>> doctest.testfile('test_doctest4.txt', encoding='utf-8')
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Nic  # Reset master.

Test the verbose output:

    >>> doctest.testfile('test_doctest4.txt', encoding='utf-8', verbose=Prawda)
    Trying:
        'föö'
    Expecting:
        'f\xf6\xf6'
    ok
    Trying:
        'bąr'
    Expecting:
        'b\u0105r'
    ok
    1 items dalejed all tests:
       2 tests w test_doctest4.txt
    2 tests w 1 items.
    2 dalejed oraz 0 failed.
    Test dalejed.
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Nic  # Reset master.
    >>> sys.argv = save_argv
"""

def test_lineendings(): r"""
*nix systems use \n line endings, dopóki Windows systems use \r\n.  Python
handles this using universal newline mode dla reading files.  Let's make
sure doctest does so (issue 8473) by creating temporary test files using each
of the two line disciplines.  One of the two will be the "wrong" one dla the
platform the test jest run on.

Windows line endings first:

    >>> zaimportuj tempfile, os
    >>> fn = tempfile.mktemp()
    >>> przy open(fn, 'wb') jako f:
    ...    f.write(b'Test:\r\n\r\n  >>> x = 1 + 1\r\n\r\nDone.\r\n')
    35
    >>> doctest.testfile(fn, Nieprawda)
    TestResults(failed=0, attempted=1)
    >>> os.remove(fn)

And now *nix line endings:

    >>> fn = tempfile.mktemp()
    >>> przy open(fn, 'wb') jako f:
    ...     f.write(b'Test:\n\n  >>> x = 1 + 1\n\nDone.\n')
    30
    >>> doctest.testfile(fn, Nieprawda)
    TestResults(failed=0, attempted=1)
    >>> os.remove(fn)

"""

def test_testmod(): r"""
Tests dla the testmod function.  More might be useful, but dla now we're just
testing the case podnieśd by Issue 6195, where trying to doctest a C module would
fail przy a UnicodeDecodeError because doctest tried to read the "source" lines
out of the binary module.

    >>> zaimportuj unicodedata
    >>> doctest.testmod(unicodedata, verbose=Nieprawda)
    TestResults(failed=0, attempted=0)
"""

spróbuj:
    os.fsencode("foo-bär@baz.py")
wyjąwszy UnicodeEncodeError:
    # Skip the test: the filesystem encoding jest unable to encode the filename
    dalej
inaczej:
    def test_unicode(): """
Check doctest przy a non-ascii filename:

    >>> doc = '''
    ... >>> podnieś Exception('clé')
    ... '''
    ...
    >>> parser = doctest.DocTestParser()
    >>> test = parser.get_doctest(doc, {}, "foo-bär@baz", "foo-bär@baz.py", 0)
    >>> test
    <DocTest foo-bär@baz z foo-bär@baz.py:0 (1 example)>
    >>> runner = doctest.DocTestRunner(verbose=Nieprawda)
    >>> runner.run(test) # doctest: +ELLIPSIS
    **********************************************************************
    File "foo-bär@baz.py", line 2, w foo-bär@baz
    Failed example:
        podnieś Exception('clé')
    Exception podnieśd:
        Traceback (most recent call last):
          File ...
            compileflags, 1), test.globs)
          File "<doctest foo-bär@baz[0]>", line 1, w <module>
            podnieś Exception('clé')
        Exception: clé
    TestResults(failed=1, attempted=1)
    """

def test_CLI(): r"""
The doctest module can be used to run doctests against an arbitrary file.
These tests test this CLI functionality.

We'll use the support module's script_helpers dla this, oraz write a test files
to a temp dir to run the command against.  Due to a current limitation w
script_helpers, though, we need a little utility function to turn the returned
output into something we can doctest against:

    >>> def normalize(s):
    ...     zwróć '\n'.join(s.decode().splitlines())

Note: we also dalej TERM='' to all the assert_python calls to avoid a bug
in the readline library that jest triggered w these tests because we are
running them w a new python process.  See:

  http://lists.gnu.org/archive/html/bug-readline/2013-06/msg00000.html

With those preliminaries out of the way, we'll start przy a file przy two
simple tests oraz no errors.  We'll run both the unadorned doctest command, oraz
the verbose version, oraz then check the output:

    >>> z test.support zaimportuj script_helper, temp_dir
    >>> przy temp_dir() jako tmpdir:
    ...     fn = os.path.join(tmpdir, 'myfile.doc')
    ...     przy open(fn, 'w') jako f:
    ...         _ = f.write('This jest a very simple test file.\n')
    ...         _ = f.write('   >>> 1 + 1\n')
    ...         _ = f.write('   2\n')
    ...         _ = f.write('   >>> "a"\n')
    ...         _ = f.write("   'a'\n")
    ...         _ = f.write('\n')
    ...         _ = f.write('And that jest it.\n')
    ...     rc1, out1, err1 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', fn, TERM='')
    ...     rc2, out2, err2 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', '-v', fn, TERM='')

With no arguments oraz dalejing tests, we should get no output:

    >>> rc1, out1, err1
    (0, b'', b'')

With the verbose flag, we should see the test output, but no error output:

    >>> rc2, err2
    (0, b'')
    >>> print(normalize(out2))
    Trying:
        1 + 1
    Expecting:
        2
    ok
    Trying:
        "a"
    Expecting:
        'a'
    ok
    1 items dalejed all tests:
       2 tests w myfile.doc
    2 tests w 1 items.
    2 dalejed oraz 0 failed.
    Test dalejed.

Now we'll write a couple files, one przy three tests, the other a python module
przy two tests, both of the files having "errors" w the tests that can be made
non-errors by applying the appropriate doctest options to the run (ELLIPSIS w
the first file, NORMALIZE_WHITESPACE w the second).  This combination will
allow to thoroughly test the -f oraz -o flags, jako well jako the doctest command's
ability to process more than one file on the command line and, since the second
file ends w '.py', its handling of python module files (as opposed to straight
text files).

    >>> z test.support zaimportuj script_helper, temp_dir
    >>> przy temp_dir() jako tmpdir:
    ...     fn = os.path.join(tmpdir, 'myfile.doc')
    ...     przy open(fn, 'w') jako f:
    ...         _ = f.write('This jest another simple test file.\n')
    ...         _ = f.write('   >>> 1 + 1\n')
    ...         _ = f.write('   2\n')
    ...         _ = f.write('   >>> "abcdef"\n')
    ...         _ = f.write("   'a...f'\n")
    ...         _ = f.write('   >>> "ajkml"\n')
    ...         _ = f.write("   'a...l'\n")
    ...         _ = f.write('\n')
    ...         _ = f.write('And that jest it.\n')
    ...     fn2 = os.path.join(tmpdir, 'myfile2.py')
    ...     przy open(fn2, 'w') jako f:
    ...         _ = f.write('def test_func():\n')
    ...         _ = f.write('   \"\"\"\n')
    ...         _ = f.write('   This jest simple python test function.\n')
    ...         _ = f.write('       >>> 1 + 1\n')
    ...         _ = f.write('       2\n')
    ...         _ = f.write('       >>> "abc   def"\n')
    ...         _ = f.write("       'abc def'\n")
    ...         _ = f.write("\n")
    ...         _ = f.write('   \"\"\"\n')
    ...     zaimportuj shutil
    ...     rc1, out1, err1 = script_helper.assert_python_failure(
    ...             '-m', 'doctest', fn, fn2, TERM='')
    ...     rc2, out2, err2 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', '-o', 'ELLIPSIS', fn, TERM='')
    ...     rc3, out3, err3 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', '-o', 'ELLIPSIS',
    ...             '-o', 'NORMALIZE_WHITESPACE', fn, fn2, TERM='')
    ...     rc4, out4, err4 = script_helper.assert_python_failure(
    ...             '-m', 'doctest', '-f', fn, fn2, TERM='')
    ...     rc5, out5, err5 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', '-v', '-o', 'ELLIPSIS',
    ...             '-o', 'NORMALIZE_WHITESPACE', fn, fn2, TERM='')

Our first test run will show the errors z the first file (doctest stops jeżeli a
file has errors).  Note that doctest test-run error output appears on stdout,
not stderr:

    >>> rc1, err1
    (1, b'')
    >>> print(normalize(out1))                # doctest: +ELLIPSIS
    **********************************************************************
    File "...myfile.doc", line 4, w myfile.doc
    Failed example:
        "abcdef"
    Expected:
        'a...f'
    Got:
        'abcdef'
    **********************************************************************
    File "...myfile.doc", line 6, w myfile.doc
    Failed example:
        "ajkml"
    Expected:
        'a...l'
    Got:
        'ajkml'
    **********************************************************************
    1 items had failures:
       2 of   3 w myfile.doc
    ***Test Failed*** 2 failures.

With -o ELLIPSIS specified, the second run, against just the first file, should
produce no errors, oraz przy -o NORMALIZE_WHITESPACE also specified, neither
should the third, which ran against both files:

    >>> rc2, out2, err2
    (0, b'', b'')
    >>> rc3, out3, err3
    (0, b'', b'')

The fourth run uses FAIL_FAST, so we should see only one error:

    >>> rc4, err4
    (1, b'')
    >>> print(normalize(out4))                # doctest: +ELLIPSIS
    **********************************************************************
    File "...myfile.doc", line 4, w myfile.doc
    Failed example:
        "abcdef"
    Expected:
        'a...f'
    Got:
        'abcdef'
    **********************************************************************
    1 items had failures:
       1 of   2 w myfile.doc
    ***Test Failed*** 1 failures.

The fifth test uses verbose przy the two options, so we should get verbose
success output dla the tests w both files:

    >>> rc5, err5
    (0, b'')
    >>> print(normalize(out5))
    Trying:
        1 + 1
    Expecting:
        2
    ok
    Trying:
        "abcdef"
    Expecting:
        'a...f'
    ok
    Trying:
        "ajkml"
    Expecting:
        'a...l'
    ok
    1 items dalejed all tests:
       3 tests w myfile.doc
    3 tests w 1 items.
    3 dalejed oraz 0 failed.
    Test dalejed.
    Trying:
        1 + 1
    Expecting:
        2
    ok
    Trying:
        "abc   def"
    Expecting:
        'abc def'
    ok
    1 items had no tests:
        myfile2
    1 items dalejed all tests:
       2 tests w myfile2.test_func
    2 tests w 2 items.
    2 dalejed oraz 0 failed.
    Test dalejed.

We should also check some typical error cases.

Invalid file name:

    >>> rc, out, err = script_helper.assert_python_failure(
    ...         '-m', 'doctest', 'nosuchfile', TERM='')
    >>> rc, out
    (1, b'')
    >>> print(normalize(err))                    # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    FileNotFoundError: [Errno ...] No such file albo directory: 'nosuchfile'

Invalid doctest option:

    >>> rc, out, err = script_helper.assert_python_failure(
    ...         '-m', 'doctest', '-o', 'nosuchoption', TERM='')
    >>> rc, out
    (2, b'')
    >>> print(normalize(err))                    # doctest: +ELLIPSIS
    usage...invalid...nosuchoption...

"""

######################################################################
## Main
######################################################################

def test_main():
    # Check the doctest cases w doctest itself:
    ret = support.run_doctest(doctest, verbosity=Prawda)
    # Check the doctest cases defined here:
    z test zaimportuj test_doctest
    support.run_doctest(test_doctest, verbosity=Prawda)

zaimportuj sys, re, io

def test_coverage(coverdir):
    trace = support.import_module('trace')
    tracer = trace.Trace(ignoredirs=[sys.base_prefix, sys.base_exec_prefix,],
                         trace=0, count=1)
    tracer.run('test_main()')
    r = tracer.results()
    print('Writing coverage results...')
    r.write_results(show_missing=Prawda, summary=Prawda,
                    coverdir=coverdir)

jeżeli __name__ == '__main__':
    jeżeli '-c' w sys.argv:
        test_coverage('/tmp/doctest.cover')
    inaczej:
        test_main()
