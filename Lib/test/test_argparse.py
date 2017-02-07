# Author: Steven J. Bethard <steven.bethard@gmail.com>.

zaimportuj codecs
zaimportuj inspect
zaimportuj os
zaimportuj shutil
zaimportuj stat
zaimportuj sys
zaimportuj textwrap
zaimportuj tempfile
zaimportuj unittest
zaimportuj argparse

z io zaimportuj StringIO

z test zaimportuj support
z unittest zaimportuj mock
klasa StdIOBuffer(StringIO):
    dalej

klasa TestCase(unittest.TestCase):

    def setUp(self):
        # The tests assume that line wrapping occurs at 80 columns, but this
        # behaviour can be overridden by setting the COLUMNS environment
        # variable.  To ensure that this assumption jest true, unset COLUMNS.
        env = support.EnvironmentVarGuard()
        env.unset("COLUMNS")
        self.addCleanup(env.__exit__)


klasa TempDirMixin(object):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.old_dir)
        dla root, dirs, files w os.walk(self.temp_dir, topdown=Nieprawda):
            dla name w files:
                os.chmod(os.path.join(self.temp_dir, name), stat.S_IWRITE)
        shutil.rmtree(self.temp_dir, Prawda)

    def create_readonly_file(self, filename):
        file_path = os.path.join(self.temp_dir, filename)
        przy open(file_path, 'w') jako file:
            file.write(filename)
        os.chmod(file_path, stat.S_IREAD)

klasa Sig(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


klasa NS(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        sorted_items = sorted(self.__dict__.items())
        kwarg_str = ', '.join(['%s=%r' % tup dla tup w sorted_items])
        zwróć '%s(%s)' % (type(self).__name__, kwarg_str)

    def __eq__(self, other):
        zwróć vars(self) == vars(other)


klasa ArgumentParserError(Exception):

    def __init__(self, message, stdout=Nic, stderr=Nic, error_code=Nic):
        Exception.__init__(self, message, stdout, stderr)
        self.message = message
        self.stdout = stdout
        self.stderr = stderr
        self.error_code = error_code


def stderr_to_parser_error(parse_args, *args, **kwargs):
    # jeżeli this jest being called recursively oraz stderr albo stdout jest already being
    # redirected, simply call the function oraz let the enclosing function
    # catch the exception
    jeżeli isinstance(sys.stderr, StdIOBuffer) albo isinstance(sys.stdout, StdIOBuffer):
        zwróć parse_args(*args, **kwargs)

    # jeżeli this jest nie being called recursively, redirect stderr oraz
    # use it jako the ArgumentParserError message
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StdIOBuffer()
    sys.stderr = StdIOBuffer()
    spróbuj:
        spróbuj:
            result = parse_args(*args, **kwargs)
            dla key w list(vars(result)):
                jeżeli getattr(result, key) jest sys.stdout:
                    setattr(result, key, old_stdout)
                jeżeli getattr(result, key) jest sys.stderr:
                    setattr(result, key, old_stderr)
            zwróć result
        wyjąwszy SystemExit:
            code = sys.exc_info()[1].code
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
            podnieś ArgumentParserError("SystemExit", stdout, stderr, code)
    w_końcu:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


klasa ErrorRaisingArgumentParser(argparse.ArgumentParser):

    def parse_args(self, *args, **kwargs):
        parse_args = super(ErrorRaisingArgumentParser, self).parse_args
        zwróć stderr_to_parser_error(parse_args, *args, **kwargs)

    def exit(self, *args, **kwargs):
        exit = super(ErrorRaisingArgumentParser, self).exit
        zwróć stderr_to_parser_error(exit, *args, **kwargs)

    def error(self, *args, **kwargs):
        error = super(ErrorRaisingArgumentParser, self).error
        zwróć stderr_to_parser_error(error, *args, **kwargs)


klasa ParserTesterMetaclass(type):
    """Adds parser tests using the klasa attributes.

    Classes of this type should specify the following attributes:

    argument_signatures -- a list of Sig objects which specify
        the signatures of Argument objects to be created
    failures -- a list of args lists that should cause the parser
        to fail
    successes -- a list of (initial_args, options, remaining_args) tuples
        where initial_args specifies the string args to be parsed,
        options jest a dict that should match the vars() of the options
        parsed out of initial_args, oraz remaining_args should be any
        remaining unparsed arguments
    """

    def __init__(cls, name, bases, bodydict):
        jeżeli name == 'ParserTestCase':
            zwróć

        # default parser signature jest empty
        jeżeli nie hasattr(cls, 'parser_signature'):
            cls.parser_signature = Sig()
        jeżeli nie hasattr(cls, 'parser_class'):
            cls.parser_class = ErrorRaisingArgumentParser

        # ---------------------------------------
        # functions dla adding optional arguments
        # ---------------------------------------
        def no_groups(parser, argument_signatures):
            """Add all arguments directly to the parser"""
            dla sig w argument_signatures:
                parser.add_argument(*sig.args, **sig.kwargs)

        def one_group(parser, argument_signatures):
            """Add all arguments under a single group w the parser"""
            group = parser.add_argument_group('foo')
            dla sig w argument_signatures:
                group.add_argument(*sig.args, **sig.kwargs)

        def many_groups(parser, argument_signatures):
            """Add each argument w its own group to the parser"""
            dla i, sig w enumerate(argument_signatures):
                group = parser.add_argument_group('foo:%i' % i)
                group.add_argument(*sig.args, **sig.kwargs)

        # --------------------------
        # functions dla parsing args
        # --------------------------
        def listargs(parser, args):
            """Parse the args by dalejing w a list"""
            zwróć parser.parse_args(args)

        def sysargs(parser, args):
            """Parse the args by defaulting to sys.argv"""
            old_sys_argv = sys.argv
            sys.argv = [old_sys_argv[0]] + args
            spróbuj:
                zwróć parser.parse_args()
            w_końcu:
                sys.argv = old_sys_argv

        # klasa that holds the combination of one optional argument
        # addition method oraz one arg parsing method
        klasa AddTests(object):

            def __init__(self, tester_cls, add_arguments, parse_args):
                self._add_arguments = add_arguments
                self._parse_args = parse_args

                add_arguments_name = self._add_arguments.__name__
                parse_args_name = self._parse_args.__name__
                dla test_func w [self.test_failures, self.test_successes]:
                    func_name = test_func.__name__
                    names = func_name, add_arguments_name, parse_args_name
                    test_name = '_'.join(names)

                    def wrapper(self, test_func=test_func):
                        test_func(self)
                    spróbuj:
                        wrapper.__name__ = test_name
                    wyjąwszy TypeError:
                        dalej
                    setattr(tester_cls, test_name, wrapper)

            def _get_parser(self, tester):
                args = tester.parser_signature.args
                kwargs = tester.parser_signature.kwargs
                parser = tester.parser_class(*args, **kwargs)
                self._add_arguments(parser, tester.argument_signatures)
                zwróć parser

            def test_failures(self, tester):
                parser = self._get_parser(tester)
                dla args_str w tester.failures:
                    args = args_str.split()
                    przy tester.assertRaises(ArgumentParserError, msg=args):
                        parser.parse_args(args)

            def test_successes(self, tester):
                parser = self._get_parser(tester)
                dla args, expected_ns w tester.successes:
                    jeżeli isinstance(args, str):
                        args = args.split()
                    result_ns = self._parse_args(parser, args)
                    tester.assertEqual(expected_ns, result_ns)

        # add tests dla each combination of an optionals adding method
        # oraz an arg parsing method
        dla add_arguments w [no_groups, one_group, many_groups]:
            dla parse_args w [listargs, sysargs]:
                AddTests(cls, add_arguments, parse_args)

bases = TestCase,
ParserTestCase = ParserTesterMetaclass('ParserTestCase', bases, {})

# ===============
# Optionals tests
# ===============

klasa TestOptionalsSingleDash(ParserTestCase):
    """Test an Optional przy a single-dash option string"""

    argument_signatures = [Sig('-x')]
    failures = ['-x', 'a', '--foo', '-x --foo', '-x -y']
    successes = [
        ('', NS(x=Nic)),
        ('-x a', NS(x='a')),
        ('-xa', NS(x='a')),
        ('-x -1', NS(x='-1')),
        ('-x-1', NS(x='-1')),
    ]


klasa TestOptionalsSingleDashCombined(ParserTestCase):
    """Test an Optional przy a single-dash option string"""

    argument_signatures = [
        Sig('-x', action='store_true'),
        Sig('-yyy', action='store_const', const=42),
        Sig('-z'),
    ]
    failures = ['a', '--foo', '-xa', '-x --foo', '-x -z', '-z -x',
                '-yx', '-yz a', '-yyyx', '-yyyza', '-xyza']
    successes = [
        ('', NS(x=Nieprawda, yyy=Nic, z=Nic)),
        ('-x', NS(x=Prawda, yyy=Nic, z=Nic)),
        ('-za', NS(x=Nieprawda, yyy=Nic, z='a')),
        ('-z a', NS(x=Nieprawda, yyy=Nic, z='a')),
        ('-xza', NS(x=Prawda, yyy=Nic, z='a')),
        ('-xz a', NS(x=Prawda, yyy=Nic, z='a')),
        ('-x -za', NS(x=Prawda, yyy=Nic, z='a')),
        ('-x -z a', NS(x=Prawda, yyy=Nic, z='a')),
        ('-y', NS(x=Nieprawda, yyy=42, z=Nic)),
        ('-yyy', NS(x=Nieprawda, yyy=42, z=Nic)),
        ('-x -yyy -za', NS(x=Prawda, yyy=42, z='a')),
        ('-x -yyy -z a', NS(x=Prawda, yyy=42, z='a')),
    ]


klasa TestOptionalsSingleDashLong(ParserTestCase):
    """Test an Optional przy a multi-character single-dash option string"""

    argument_signatures = [Sig('-foo')]
    failures = ['-foo', 'a', '--foo', '-foo --foo', '-foo -y', '-fooa']
    successes = [
        ('', NS(foo=Nic)),
        ('-foo a', NS(foo='a')),
        ('-foo -1', NS(foo='-1')),
        ('-fo a', NS(foo='a')),
        ('-f a', NS(foo='a')),
    ]


klasa TestOptionalsSingleDashSubsetAmbiguous(ParserTestCase):
    """Test Optionals where option strings are subsets of each other"""

    argument_signatures = [Sig('-f'), Sig('-foobar'), Sig('-foorab')]
    failures = ['-f', '-foo', '-fo', '-foo b', '-foob', '-fooba', '-foora']
    successes = [
        ('', NS(f=Nic, foobar=Nic, foorab=Nic)),
        ('-f a', NS(f='a', foobar=Nic, foorab=Nic)),
        ('-fa', NS(f='a', foobar=Nic, foorab=Nic)),
        ('-foa', NS(f='oa', foobar=Nic, foorab=Nic)),
        ('-fooa', NS(f='ooa', foobar=Nic, foorab=Nic)),
        ('-foobar a', NS(f=Nic, foobar='a', foorab=Nic)),
        ('-foorab a', NS(f=Nic, foobar=Nic, foorab='a')),
    ]


klasa TestOptionalsSingleDashAmbiguous(ParserTestCase):
    """Test Optionals that partially match but are nie subsets"""

    argument_signatures = [Sig('-foobar'), Sig('-foorab')]
    failures = ['-f', '-f a', '-fa', '-foa', '-foo', '-fo', '-foo b']
    successes = [
        ('', NS(foobar=Nic, foorab=Nic)),
        ('-foob a', NS(foobar='a', foorab=Nic)),
        ('-foor a', NS(foobar=Nic, foorab='a')),
        ('-fooba a', NS(foobar='a', foorab=Nic)),
        ('-foora a', NS(foobar=Nic, foorab='a')),
        ('-foobar a', NS(foobar='a', foorab=Nic)),
        ('-foorab a', NS(foobar=Nic, foorab='a')),
    ]


klasa TestOptionalsNumeric(ParserTestCase):
    """Test an Optional przy a short opt string"""

    argument_signatures = [Sig('-1', dest='one')]
    failures = ['-1', 'a', '-1 --foo', '-1 -y', '-1 -1', '-1 -2']
    successes = [
        ('', NS(one=Nic)),
        ('-1 a', NS(one='a')),
        ('-1a', NS(one='a')),
        ('-1-2', NS(one='-2')),
    ]


klasa TestOptionalsDoubleDash(ParserTestCase):
    """Test an Optional przy a double-dash option string"""

    argument_signatures = [Sig('--foo')]
    failures = ['--foo', '-f', '-f a', 'a', '--foo -x', '--foo --bar']
    successes = [
        ('', NS(foo=Nic)),
        ('--foo a', NS(foo='a')),
        ('--foo=a', NS(foo='a')),
        ('--foo -2.5', NS(foo='-2.5')),
        ('--foo=-2.5', NS(foo='-2.5')),
    ]


klasa TestOptionalsDoubleDashPartialMatch(ParserTestCase):
    """Tests partial matching przy a double-dash option string"""

    argument_signatures = [
        Sig('--badger', action='store_true'),
        Sig('--bat'),
    ]
    failures = ['--bar', '--b', '--ba', '--b=2', '--ba=4', '--badge 5']
    successes = [
        ('', NS(badger=Nieprawda, bat=Nic)),
        ('--bat X', NS(badger=Nieprawda, bat='X')),
        ('--bad', NS(badger=Prawda, bat=Nic)),
        ('--badg', NS(badger=Prawda, bat=Nic)),
        ('--badge', NS(badger=Prawda, bat=Nic)),
        ('--badger', NS(badger=Prawda, bat=Nic)),
    ]


klasa TestOptionalsDoubleDashPrefixMatch(ParserTestCase):
    """Tests when one double-dash option string jest a prefix of another"""

    argument_signatures = [
        Sig('--badger', action='store_true'),
        Sig('--ba'),
    ]
    failures = ['--bar', '--b', '--ba', '--b=2', '--badge 5']
    successes = [
        ('', NS(badger=Nieprawda, ba=Nic)),
        ('--ba X', NS(badger=Nieprawda, ba='X')),
        ('--ba=X', NS(badger=Nieprawda, ba='X')),
        ('--bad', NS(badger=Prawda, ba=Nic)),
        ('--badg', NS(badger=Prawda, ba=Nic)),
        ('--badge', NS(badger=Prawda, ba=Nic)),
        ('--badger', NS(badger=Prawda, ba=Nic)),
    ]


klasa TestOptionalsSingleDoubleDash(ParserTestCase):
    """Test an Optional przy single- oraz double-dash option strings"""

    argument_signatures = [
        Sig('-f', action='store_true'),
        Sig('--bar'),
        Sig('-baz', action='store_const', const=42),
    ]
    failures = ['--bar', '-fbar', '-fbaz', '-bazf', '-b B', 'B']
    successes = [
        ('', NS(f=Nieprawda, bar=Nic, baz=Nic)),
        ('-f', NS(f=Prawda, bar=Nic, baz=Nic)),
        ('--ba B', NS(f=Nieprawda, bar='B', baz=Nic)),
        ('-f --bar B', NS(f=Prawda, bar='B', baz=Nic)),
        ('-f -b', NS(f=Prawda, bar=Nic, baz=42)),
        ('-ba -f', NS(f=Prawda, bar=Nic, baz=42)),
    ]


klasa TestOptionalsAlternatePrefixChars(ParserTestCase):
    """Test an Optional przy option strings przy custom prefixes"""

    parser_signature = Sig(prefix_chars='+:/', add_help=Nieprawda)
    argument_signatures = [
        Sig('+f', action='store_true'),
        Sig('::bar'),
        Sig('/baz', action='store_const', const=42),
    ]
    failures = ['--bar', '-fbar', '-b B', 'B', '-f', '--bar B', '-baz', '-h', '--help', '+h', '::help', '/help']
    successes = [
        ('', NS(f=Nieprawda, bar=Nic, baz=Nic)),
        ('+f', NS(f=Prawda, bar=Nic, baz=Nic)),
        ('::ba B', NS(f=Nieprawda, bar='B', baz=Nic)),
        ('+f ::bar B', NS(f=Prawda, bar='B', baz=Nic)),
        ('+f /b', NS(f=Prawda, bar=Nic, baz=42)),
        ('/ba +f', NS(f=Prawda, bar=Nic, baz=42)),
    ]


klasa TestOptionalsAlternatePrefixCharsAddedHelp(ParserTestCase):
    """When ``-`` nie w prefix_chars, default operators created dla help
       should use the prefix_chars w use rather than - albo --
       http://bugs.python.org/issue9444"""

    parser_signature = Sig(prefix_chars='+:/', add_help=Prawda)
    argument_signatures = [
        Sig('+f', action='store_true'),
        Sig('::bar'),
        Sig('/baz', action='store_const', const=42),
    ]
    failures = ['--bar', '-fbar', '-b B', 'B', '-f', '--bar B', '-baz']
    successes = [
        ('', NS(f=Nieprawda, bar=Nic, baz=Nic)),
        ('+f', NS(f=Prawda, bar=Nic, baz=Nic)),
        ('::ba B', NS(f=Nieprawda, bar='B', baz=Nic)),
        ('+f ::bar B', NS(f=Prawda, bar='B', baz=Nic)),
        ('+f /b', NS(f=Prawda, bar=Nic, baz=42)),
        ('/ba +f', NS(f=Prawda, bar=Nic, baz=42))
    ]


klasa TestOptionalsAlternatePrefixCharsMultipleShortArgs(ParserTestCase):
    """Verify that Optionals must be called przy their defined prefixes"""

    parser_signature = Sig(prefix_chars='+-', add_help=Nieprawda)
    argument_signatures = [
        Sig('-x', action='store_true'),
        Sig('+y', action='store_true'),
        Sig('+z', action='store_true'),
    ]
    failures = ['-w',
                '-xyz',
                '+x',
                '-y',
                '+xyz',
    ]
    successes = [
        ('', NS(x=Nieprawda, y=Nieprawda, z=Nieprawda)),
        ('-x', NS(x=Prawda, y=Nieprawda, z=Nieprawda)),
        ('+y -x', NS(x=Prawda, y=Prawda, z=Nieprawda)),
        ('+yz -x', NS(x=Prawda, y=Prawda, z=Prawda)),
    ]


klasa TestOptionalsShortLong(ParserTestCase):
    """Test a combination of single- oraz double-dash option strings"""

    argument_signatures = [
        Sig('-v', '--verbose', '-n', '--noisy', action='store_true'),
    ]
    failures = ['--x --verbose', '-N', 'a', '-v x']
    successes = [
        ('', NS(verbose=Nieprawda)),
        ('-v', NS(verbose=Prawda)),
        ('--verbose', NS(verbose=Prawda)),
        ('-n', NS(verbose=Prawda)),
        ('--noisy', NS(verbose=Prawda)),
    ]


klasa TestOptionalsDest(ParserTestCase):
    """Tests various means of setting destination"""

    argument_signatures = [Sig('--foo-bar'), Sig('--baz', dest='zabbaz')]
    failures = ['a']
    successes = [
        ('--foo-bar f', NS(foo_bar='f', zabbaz=Nic)),
        ('--baz g', NS(foo_bar=Nic, zabbaz='g')),
        ('--foo-bar h --baz i', NS(foo_bar='h', zabbaz='i')),
        ('--baz j --foo-bar k', NS(foo_bar='k', zabbaz='j')),
    ]


klasa TestOptionalsDefault(ParserTestCase):
    """Tests specifying a default dla an Optional"""

    argument_signatures = [Sig('-x'), Sig('-y', default=42)]
    failures = ['a']
    successes = [
        ('', NS(x=Nic, y=42)),
        ('-xx', NS(x='x', y=42)),
        ('-yy', NS(x=Nic, y='y')),
    ]


klasa TestOptionalsNargsDefault(ParserTestCase):
    """Tests nie specifying the number of args dla an Optional"""

    argument_signatures = [Sig('-x')]
    failures = ['a', '-x']
    successes = [
        ('', NS(x=Nic)),
        ('-x a', NS(x='a')),
    ]


klasa TestOptionalsNargs1(ParserTestCase):
    """Tests specifying the 1 arg dla an Optional"""

    argument_signatures = [Sig('-x', nargs=1)]
    failures = ['a', '-x']
    successes = [
        ('', NS(x=Nic)),
        ('-x a', NS(x=['a'])),
    ]


klasa TestOptionalsNargs3(ParserTestCase):
    """Tests specifying the 3 args dla an Optional"""

    argument_signatures = [Sig('-x', nargs=3)]
    failures = ['a', '-x', '-x a', '-x a b', 'a -x', 'a -x b']
    successes = [
        ('', NS(x=Nic)),
        ('-x a b c', NS(x=['a', 'b', 'c'])),
    ]


klasa TestOptionalsNargsOptional(ParserTestCase):
    """Tests specifying an Optional arg dla an Optional"""

    argument_signatures = [
        Sig('-w', nargs='?'),
        Sig('-x', nargs='?', const=42),
        Sig('-y', nargs='?', default='spam'),
        Sig('-z', nargs='?', type=int, const='42', default='84'),
    ]
    failures = ['2']
    successes = [
        ('', NS(w=Nic, x=Nic, y='spam', z=84)),
        ('-w', NS(w=Nic, x=Nic, y='spam', z=84)),
        ('-w 2', NS(w='2', x=Nic, y='spam', z=84)),
        ('-x', NS(w=Nic, x=42, y='spam', z=84)),
        ('-x 2', NS(w=Nic, x='2', y='spam', z=84)),
        ('-y', NS(w=Nic, x=Nic, y=Nic, z=84)),
        ('-y 2', NS(w=Nic, x=Nic, y='2', z=84)),
        ('-z', NS(w=Nic, x=Nic, y='spam', z=42)),
        ('-z 2', NS(w=Nic, x=Nic, y='spam', z=2)),
    ]


klasa TestOptionalsNargsZeroOrMore(ParserTestCase):
    """Tests specifying an args dla an Optional that accepts zero albo more"""

    argument_signatures = [
        Sig('-x', nargs='*'),
        Sig('-y', nargs='*', default='spam'),
    ]
    failures = ['a']
    successes = [
        ('', NS(x=Nic, y='spam')),
        ('-x', NS(x=[], y='spam')),
        ('-x a', NS(x=['a'], y='spam')),
        ('-x a b', NS(x=['a', 'b'], y='spam')),
        ('-y', NS(x=Nic, y=[])),
        ('-y a', NS(x=Nic, y=['a'])),
        ('-y a b', NS(x=Nic, y=['a', 'b'])),
    ]


klasa TestOptionalsNargsOneOrMore(ParserTestCase):
    """Tests specifying an args dla an Optional that accepts one albo more"""

    argument_signatures = [
        Sig('-x', nargs='+'),
        Sig('-y', nargs='+', default='spam'),
    ]
    failures = ['a', '-x', '-y', 'a -x', 'a -y b']
    successes = [
        ('', NS(x=Nic, y='spam')),
        ('-x a', NS(x=['a'], y='spam')),
        ('-x a b', NS(x=['a', 'b'], y='spam')),
        ('-y a', NS(x=Nic, y=['a'])),
        ('-y a b', NS(x=Nic, y=['a', 'b'])),
    ]


klasa TestOptionalsChoices(ParserTestCase):
    """Tests specifying the choices dla an Optional"""

    argument_signatures = [
        Sig('-f', choices='abc'),
        Sig('-g', type=int, choices=range(5))]
    failures = ['a', '-f d', '-fad', '-ga', '-g 6']
    successes = [
        ('', NS(f=Nic, g=Nic)),
        ('-f a', NS(f='a', g=Nic)),
        ('-f c', NS(f='c', g=Nic)),
        ('-g 0', NS(f=Nic, g=0)),
        ('-g 03', NS(f=Nic, g=3)),
        ('-fb -g4', NS(f='b', g=4)),
    ]


klasa TestOptionalsRequired(ParserTestCase):
    """Tests an optional action that jest required"""

    argument_signatures = [
        Sig('-x', type=int, required=Prawda),
    ]
    failures = ['a', '']
    successes = [
        ('-x 1', NS(x=1)),
        ('-x42', NS(x=42)),
    ]


klasa TestOptionalsActionStore(ParserTestCase):
    """Tests the store action dla an Optional"""

    argument_signatures = [Sig('-x', action='store')]
    failures = ['a', 'a -x']
    successes = [
        ('', NS(x=Nic)),
        ('-xfoo', NS(x='foo')),
    ]


klasa TestOptionalsActionStoreConst(ParserTestCase):
    """Tests the store_const action dla an Optional"""

    argument_signatures = [Sig('-y', action='store_const', const=object)]
    failures = ['a']
    successes = [
        ('', NS(y=Nic)),
        ('-y', NS(y=object)),
    ]


klasa TestOptionalsActionStoreNieprawda(ParserTestCase):
    """Tests the store_false action dla an Optional"""

    argument_signatures = [Sig('-z', action='store_false')]
    failures = ['a', '-za', '-z a']
    successes = [
        ('', NS(z=Prawda)),
        ('-z', NS(z=Nieprawda)),
    ]


klasa TestOptionalsActionStorePrawda(ParserTestCase):
    """Tests the store_true action dla an Optional"""

    argument_signatures = [Sig('--apple', action='store_true')]
    failures = ['a', '--apple=b', '--apple b']
    successes = [
        ('', NS(apple=Nieprawda)),
        ('--apple', NS(apple=Prawda)),
    ]


klasa TestOptionalsActionAppend(ParserTestCase):
    """Tests the append action dla an Optional"""

    argument_signatures = [Sig('--baz', action='append')]
    failures = ['a', '--baz', 'a --baz', '--baz a b']
    successes = [
        ('', NS(baz=Nic)),
        ('--baz a', NS(baz=['a'])),
        ('--baz a --baz b', NS(baz=['a', 'b'])),
    ]


klasa TestOptionalsActionAppendWithDefault(ParserTestCase):
    """Tests the append action dla an Optional"""

    argument_signatures = [Sig('--baz', action='append', default=['X'])]
    failures = ['a', '--baz', 'a --baz', '--baz a b']
    successes = [
        ('', NS(baz=['X'])),
        ('--baz a', NS(baz=['X', 'a'])),
        ('--baz a --baz b', NS(baz=['X', 'a', 'b'])),
    ]


klasa TestOptionalsActionAppendConst(ParserTestCase):
    """Tests the append_const action dla an Optional"""

    argument_signatures = [
        Sig('-b', action='append_const', const=Exception),
        Sig('-c', action='append', dest='b'),
    ]
    failures = ['a', '-c', 'a -c', '-bx', '-b x']
    successes = [
        ('', NS(b=Nic)),
        ('-b', NS(b=[Exception])),
        ('-b -cx -b -cyz', NS(b=[Exception, 'x', Exception, 'yz'])),
    ]


klasa TestOptionalsActionAppendConstWithDefault(ParserTestCase):
    """Tests the append_const action dla an Optional"""

    argument_signatures = [
        Sig('-b', action='append_const', const=Exception, default=['X']),
        Sig('-c', action='append', dest='b'),
    ]
    failures = ['a', '-c', 'a -c', '-bx', '-b x']
    successes = [
        ('', NS(b=['X'])),
        ('-b', NS(b=['X', Exception])),
        ('-b -cx -b -cyz', NS(b=['X', Exception, 'x', Exception, 'yz'])),
    ]


klasa TestOptionalsActionCount(ParserTestCase):
    """Tests the count action dla an Optional"""

    argument_signatures = [Sig('-x', action='count')]
    failures = ['a', '-x a', '-x b', '-x a -x b']
    successes = [
        ('', NS(x=Nic)),
        ('-x', NS(x=1)),
    ]


klasa TestOptionalsAllowLongAbbreviation(ParserTestCase):
    """Allow long options to be abbreviated unambiguously"""

    argument_signatures = [
        Sig('--foo'),
        Sig('--foobaz'),
        Sig('--fooble', action='store_true'),
    ]
    failures = ['--foob 5', '--foob']
    successes = [
        ('', NS(foo=Nic, foobaz=Nic, fooble=Nieprawda)),
        ('--foo 7', NS(foo='7', foobaz=Nic, fooble=Nieprawda)),
        ('--fooba a', NS(foo=Nic, foobaz='a', fooble=Nieprawda)),
        ('--foobl --foo g', NS(foo='g', foobaz=Nic, fooble=Prawda)),
    ]


klasa TestOptionalsDisallowLongAbbreviation(ParserTestCase):
    """Do nie allow abbreviations of long options at all"""

    parser_signature = Sig(allow_abbrev=Nieprawda)
    argument_signatures = [
        Sig('--foo'),
        Sig('--foodle', action='store_true'),
        Sig('--foonly'),
    ]
    failures = ['-foon 3', '--foon 3', '--food', '--food --foo 2']
    successes = [
        ('', NS(foo=Nic, foodle=Nieprawda, foonly=Nic)),
        ('--foo 3', NS(foo='3', foodle=Nieprawda, foonly=Nic)),
        ('--foonly 7 --foodle --foo 2', NS(foo='2', foodle=Prawda, foonly='7')),
    ]

# ================
# Positional tests
# ================

klasa TestPositionalsNargsNic(ParserTestCase):
    """Test a Positional that doesn't specify nargs"""

    argument_signatures = [Sig('foo')]
    failures = ['', '-x', 'a b']
    successes = [
        ('a', NS(foo='a')),
    ]


klasa TestPositionalsNargs1(ParserTestCase):
    """Test a Positional that specifies an nargs of 1"""

    argument_signatures = [Sig('foo', nargs=1)]
    failures = ['', '-x', 'a b']
    successes = [
        ('a', NS(foo=['a'])),
    ]


klasa TestPositionalsNargs2(ParserTestCase):
    """Test a Positional that specifies an nargs of 2"""

    argument_signatures = [Sig('foo', nargs=2)]
    failures = ['', 'a', '-x', 'a b c']
    successes = [
        ('a b', NS(foo=['a', 'b'])),
    ]


klasa TestPositionalsNargsZeroOrMore(ParserTestCase):
    """Test a Positional that specifies unlimited nargs"""

    argument_signatures = [Sig('foo', nargs='*')]
    failures = ['-x']
    successes = [
        ('', NS(foo=[])),
        ('a', NS(foo=['a'])),
        ('a b', NS(foo=['a', 'b'])),
    ]


klasa TestPositionalsNargsZeroOrMoreDefault(ParserTestCase):
    """Test a Positional that specifies unlimited nargs oraz a default"""

    argument_signatures = [Sig('foo', nargs='*', default='bar')]
    failures = ['-x']
    successes = [
        ('', NS(foo='bar')),
        ('a', NS(foo=['a'])),
        ('a b', NS(foo=['a', 'b'])),
    ]


klasa TestPositionalsNargsOneOrMore(ParserTestCase):
    """Test a Positional that specifies one albo more nargs"""

    argument_signatures = [Sig('foo', nargs='+')]
    failures = ['', '-x']
    successes = [
        ('a', NS(foo=['a'])),
        ('a b', NS(foo=['a', 'b'])),
    ]


klasa TestPositionalsNargsOptional(ParserTestCase):
    """Tests an Optional Positional"""

    argument_signatures = [Sig('foo', nargs='?')]
    failures = ['-x', 'a b']
    successes = [
        ('', NS(foo=Nic)),
        ('a', NS(foo='a')),
    ]


klasa TestPositionalsNargsOptionalDefault(ParserTestCase):
    """Tests an Optional Positional przy a default value"""

    argument_signatures = [Sig('foo', nargs='?', default=42)]
    failures = ['-x', 'a b']
    successes = [
        ('', NS(foo=42)),
        ('a', NS(foo='a')),
    ]


klasa TestPositionalsNargsOptionalConvertedDefault(ParserTestCase):
    """Tests an Optional Positional przy a default value
    that needs to be converted to the appropriate type.
    """

    argument_signatures = [
        Sig('foo', nargs='?', type=int, default='42'),
    ]
    failures = ['-x', 'a b', '1 2']
    successes = [
        ('', NS(foo=42)),
        ('1', NS(foo=1)),
    ]


klasa TestPositionalsNargsNicNic(ParserTestCase):
    """Test two Positionals that don't specify nargs"""

    argument_signatures = [Sig('foo'), Sig('bar')]
    failures = ['', '-x', 'a', 'a b c']
    successes = [
        ('a b', NS(foo='a', bar='b')),
    ]


klasa TestPositionalsNargsNic1(ParserTestCase):
    """Test a Positional przy no nargs followed by one przy 1"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs=1)]
    failures = ['', '--foo', 'a', 'a b c']
    successes = [
        ('a b', NS(foo='a', bar=['b'])),
    ]


klasa TestPositionalsNargs2Nic(ParserTestCase):
    """Test a Positional przy 2 nargs followed by one przy none"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar')]
    failures = ['', '--foo', 'a', 'a b', 'a b c d']
    successes = [
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


klasa TestPositionalsNargsNicZeroOrMore(ParserTestCase):
    """Test a Positional przy no nargs followed by one przy unlimited"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs='*')]
    failures = ['', '--foo']
    successes = [
        ('a', NS(foo='a', bar=[])),
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


klasa TestPositionalsNargsNicOneOrMore(ParserTestCase):
    """Test a Positional przy no nargs followed by one przy one albo more"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs='+')]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


klasa TestPositionalsNargsNicOptional(ParserTestCase):
    """Test a Positional przy no nargs followed by one przy an Optional"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs='?')]
    failures = ['', '--foo', 'a b c']
    successes = [
        ('a', NS(foo='a', bar=Nic)),
        ('a b', NS(foo='a', bar='b')),
    ]


klasa TestPositionalsNargsZeroOrMoreNic(ParserTestCase):
    """Test a Positional przy unlimited nargs followed by one przy none"""

    argument_signatures = [Sig('foo', nargs='*'), Sig('bar')]
    failures = ['', '--foo']
    successes = [
        ('a', NS(foo=[], bar='a')),
        ('a b', NS(foo=['a'], bar='b')),
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


klasa TestPositionalsNargsOneOrMoreNic(ParserTestCase):
    """Test a Positional przy one albo more nargs followed by one przy none"""

    argument_signatures = [Sig('foo', nargs='+'), Sig('bar')]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo=['a'], bar='b')),
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


klasa TestPositionalsNargsOptionalNic(ParserTestCase):
    """Test a Positional przy an Optional nargs followed by one przy none"""

    argument_signatures = [Sig('foo', nargs='?', default=42), Sig('bar')]
    failures = ['', '--foo', 'a b c']
    successes = [
        ('a', NS(foo=42, bar='a')),
        ('a b', NS(foo='a', bar='b')),
    ]


klasa TestPositionalsNargs2ZeroOrMore(ParserTestCase):
    """Test a Positional przy 2 nargs followed by one przy unlimited"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar', nargs='*')]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo=['a', 'b'], bar=[])),
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


klasa TestPositionalsNargs2OneOrMore(ParserTestCase):
    """Test a Positional przy 2 nargs followed by one przy one albo more"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar', nargs='+')]
    failures = ['', '--foo', 'a', 'a b']
    successes = [
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


klasa TestPositionalsNargs2Optional(ParserTestCase):
    """Test a Positional przy 2 nargs followed by one optional"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar', nargs='?')]
    failures = ['', '--foo', 'a', 'a b c d']
    successes = [
        ('a b', NS(foo=['a', 'b'], bar=Nic)),
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


klasa TestPositionalsNargsZeroOrMore1(ParserTestCase):
    """Test a Positional przy unlimited nargs followed by one przy 1"""

    argument_signatures = [Sig('foo', nargs='*'), Sig('bar', nargs=1)]
    failures = ['', '--foo', ]
    successes = [
        ('a', NS(foo=[], bar=['a'])),
        ('a b', NS(foo=['a'], bar=['b'])),
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


klasa TestPositionalsNargsOneOrMore1(ParserTestCase):
    """Test a Positional przy one albo more nargs followed by one przy 1"""

    argument_signatures = [Sig('foo', nargs='+'), Sig('bar', nargs=1)]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo=['a'], bar=['b'])),
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


klasa TestPositionalsNargsOptional1(ParserTestCase):
    """Test a Positional przy an Optional nargs followed by one przy 1"""

    argument_signatures = [Sig('foo', nargs='?'), Sig('bar', nargs=1)]
    failures = ['', '--foo', 'a b c']
    successes = [
        ('a', NS(foo=Nic, bar=['a'])),
        ('a b', NS(foo='a', bar=['b'])),
    ]


klasa TestPositionalsNargsNicZeroOrMore1(ParserTestCase):
    """Test three Positionals: no nargs, unlimited nargs oraz 1 nargs"""

    argument_signatures = [
        Sig('foo'),
        Sig('bar', nargs='*'),
        Sig('baz', nargs=1),
    ]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo='a', bar=[], baz=['b'])),
        ('a b c', NS(foo='a', bar=['b'], baz=['c'])),
    ]


klasa TestPositionalsNargsNicOneOrMore1(ParserTestCase):
    """Test three Positionals: no nargs, one albo more nargs oraz 1 nargs"""

    argument_signatures = [
        Sig('foo'),
        Sig('bar', nargs='+'),
        Sig('baz', nargs=1),
    ]
    failures = ['', '--foo', 'a', 'b']
    successes = [
        ('a b c', NS(foo='a', bar=['b'], baz=['c'])),
        ('a b c d', NS(foo='a', bar=['b', 'c'], baz=['d'])),
    ]


klasa TestPositionalsNargsNicOptional1(ParserTestCase):
    """Test three Positionals: no nargs, optional narg oraz 1 nargs"""

    argument_signatures = [
        Sig('foo'),
        Sig('bar', nargs='?', default=0.625),
        Sig('baz', nargs=1),
    ]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo='a', bar=0.625, baz=['b'])),
        ('a b c', NS(foo='a', bar='b', baz=['c'])),
    ]


klasa TestPositionalsNargsOptionalOptional(ParserTestCase):
    """Test two optional nargs"""

    argument_signatures = [
        Sig('foo', nargs='?'),
        Sig('bar', nargs='?', default=42),
    ]
    failures = ['--foo', 'a b c']
    successes = [
        ('', NS(foo=Nic, bar=42)),
        ('a', NS(foo='a', bar=42)),
        ('a b', NS(foo='a', bar='b')),
    ]


klasa TestPositionalsNargsOptionalZeroOrMore(ParserTestCase):
    """Test an Optional narg followed by unlimited nargs"""

    argument_signatures = [Sig('foo', nargs='?'), Sig('bar', nargs='*')]
    failures = ['--foo']
    successes = [
        ('', NS(foo=Nic, bar=[])),
        ('a', NS(foo='a', bar=[])),
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


klasa TestPositionalsNargsOptionalOneOrMore(ParserTestCase):
    """Test an Optional narg followed by one albo more nargs"""

    argument_signatures = [Sig('foo', nargs='?'), Sig('bar', nargs='+')]
    failures = ['', '--foo']
    successes = [
        ('a', NS(foo=Nic, bar=['a'])),
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


klasa TestPositionalsChoicesString(ParserTestCase):
    """Test a set of single-character choices"""

    argument_signatures = [Sig('spam', choices=set('abcdefg'))]
    failures = ['', '--foo', 'h', '42', 'ef']
    successes = [
        ('a', NS(spam='a')),
        ('g', NS(spam='g')),
    ]


klasa TestPositionalsChoicesInt(ParserTestCase):
    """Test a set of integer choices"""

    argument_signatures = [Sig('spam', type=int, choices=range(20))]
    failures = ['', '--foo', 'h', '42', 'ef']
    successes = [
        ('4', NS(spam=4)),
        ('15', NS(spam=15)),
    ]


klasa TestPositionalsActionAppend(ParserTestCase):
    """Test the 'append' action"""

    argument_signatures = [
        Sig('spam', action='append'),
        Sig('spam', action='append', nargs=2),
    ]
    failures = ['', '--foo', 'a', 'a b', 'a b c d']
    successes = [
        ('a b c', NS(spam=['a', ['b', 'c']])),
    ]

# ========================================
# Combined optionals oraz positionals tests
# ========================================

klasa TestOptionalsNumericAndPositionals(ParserTestCase):
    """Tests negative number args when numeric options are present"""

    argument_signatures = [
        Sig('x', nargs='?'),
        Sig('-4', dest='y', action='store_true'),
    ]
    failures = ['-2', '-315']
    successes = [
        ('', NS(x=Nic, y=Nieprawda)),
        ('a', NS(x='a', y=Nieprawda)),
        ('-4', NS(x=Nic, y=Prawda)),
        ('-4 a', NS(x='a', y=Prawda)),
    ]


klasa TestOptionalsAlmostNumericAndPositionals(ParserTestCase):
    """Tests negative number args when almost numeric options are present"""

    argument_signatures = [
        Sig('x', nargs='?'),
        Sig('-k4', dest='y', action='store_true'),
    ]
    failures = ['-k3']
    successes = [
        ('', NS(x=Nic, y=Nieprawda)),
        ('-2', NS(x='-2', y=Nieprawda)),
        ('a', NS(x='a', y=Nieprawda)),
        ('-k4', NS(x=Nic, y=Prawda)),
        ('-k4 a', NS(x='a', y=Prawda)),
    ]


klasa TestEmptyAndSpaceContainingArguments(ParserTestCase):

    argument_signatures = [
        Sig('x', nargs='?'),
        Sig('-y', '--yyy', dest='y'),
    ]
    failures = ['-y']
    successes = [
        ([''], NS(x='', y=Nic)),
        (['a badger'], NS(x='a badger', y=Nic)),
        (['-a badger'], NS(x='-a badger', y=Nic)),
        (['-y', ''], NS(x=Nic, y='')),
        (['-y', 'a badger'], NS(x=Nic, y='a badger')),
        (['-y', '-a badger'], NS(x=Nic, y='-a badger')),
        (['--yyy=a badger'], NS(x=Nic, y='a badger')),
        (['--yyy=-a badger'], NS(x=Nic, y='-a badger')),
    ]


klasa TestPrefixCharacterOnlyArguments(ParserTestCase):

    parser_signature = Sig(prefix_chars='-+')
    argument_signatures = [
        Sig('-', dest='x', nargs='?', const='badger'),
        Sig('+', dest='y', type=int, default=42),
        Sig('-+-', dest='z', action='store_true'),
    ]
    failures = ['-y', '+ -']
    successes = [
        ('', NS(x=Nic, y=42, z=Nieprawda)),
        ('-', NS(x='badger', y=42, z=Nieprawda)),
        ('- X', NS(x='X', y=42, z=Nieprawda)),
        ('+ -3', NS(x=Nic, y=-3, z=Nieprawda)),
        ('-+-', NS(x=Nic, y=42, z=Prawda)),
        ('- ===', NS(x='===', y=42, z=Nieprawda)),
    ]


klasa TestNargsZeroOrMore(ParserTestCase):
    """Tests specifying an args dla an Optional that accepts zero albo more"""

    argument_signatures = [Sig('-x', nargs='*'), Sig('y', nargs='*')]
    failures = []
    successes = [
        ('', NS(x=Nic, y=[])),
        ('-x', NS(x=[], y=[])),
        ('-x a', NS(x=['a'], y=[])),
        ('-x a -- b', NS(x=['a'], y=['b'])),
        ('a', NS(x=Nic, y=['a'])),
        ('a -x', NS(x=[], y=['a'])),
        ('a -x b', NS(x=['b'], y=['a'])),
    ]


klasa TestNargsRemainder(ParserTestCase):
    """Tests specifying a positional przy nargs=REMAINDER"""

    argument_signatures = [Sig('x'), Sig('y', nargs='...'), Sig('-z')]
    failures = ['', '-z', '-z Z']
    successes = [
        ('X', NS(x='X', y=[], z=Nic)),
        ('-z Z X', NS(x='X', y=[], z='Z')),
        ('X A B -z Z', NS(x='X', y=['A', 'B', '-z', 'Z'], z=Nic)),
        ('X Y --foo', NS(x='X', y=['Y', '--foo'], z=Nic)),
    ]


klasa TestOptionLike(ParserTestCase):
    """Tests options that may albo may nie be arguments"""

    argument_signatures = [
        Sig('-x', type=float),
        Sig('-3', type=float, dest='y'),
        Sig('z', nargs='*'),
    ]
    failures = ['-x', '-y2.5', '-xa', '-x -a',
                '-x -3', '-x -3.5', '-3 -3.5',
                '-x -2.5', '-x -2.5 a', '-3 -.5',
                'a x -1', '-x -1 a', '-3 -1 a']
    successes = [
        ('', NS(x=Nic, y=Nic, z=[])),
        ('-x 2.5', NS(x=2.5, y=Nic, z=[])),
        ('-x 2.5 a', NS(x=2.5, y=Nic, z=['a'])),
        ('-3.5', NS(x=Nic, y=0.5, z=[])),
        ('-3-.5', NS(x=Nic, y=-0.5, z=[])),
        ('-3 .5', NS(x=Nic, y=0.5, z=[])),
        ('a -3.5', NS(x=Nic, y=0.5, z=['a'])),
        ('a', NS(x=Nic, y=Nic, z=['a'])),
        ('a -x 1', NS(x=1.0, y=Nic, z=['a'])),
        ('-x 1 a', NS(x=1.0, y=Nic, z=['a'])),
        ('-3 1 a', NS(x=Nic, y=1.0, z=['a'])),
    ]


klasa TestDefaultSuppress(ParserTestCase):
    """Test actions przy suppressed defaults"""

    argument_signatures = [
        Sig('foo', nargs='?', default=argparse.SUPPRESS),
        Sig('bar', nargs='*', default=argparse.SUPPRESS),
        Sig('--baz', action='store_true', default=argparse.SUPPRESS),
    ]
    failures = ['-x']
    successes = [
        ('', NS()),
        ('a', NS(foo='a')),
        ('a b', NS(foo='a', bar=['b'])),
        ('--baz', NS(baz=Prawda)),
        ('a --baz', NS(foo='a', baz=Prawda)),
        ('--baz a b', NS(foo='a', bar=['b'], baz=Prawda)),
    ]


klasa TestParserDefaultSuppress(ParserTestCase):
    """Test actions przy a parser-level default of SUPPRESS"""

    parser_signature = Sig(argument_default=argparse.SUPPRESS)
    argument_signatures = [
        Sig('foo', nargs='?'),
        Sig('bar', nargs='*'),
        Sig('--baz', action='store_true'),
    ]
    failures = ['-x']
    successes = [
        ('', NS()),
        ('a', NS(foo='a')),
        ('a b', NS(foo='a', bar=['b'])),
        ('--baz', NS(baz=Prawda)),
        ('a --baz', NS(foo='a', baz=Prawda)),
        ('--baz a b', NS(foo='a', bar=['b'], baz=Prawda)),
    ]


klasa TestParserDefault42(ParserTestCase):
    """Test actions przy a parser-level default of 42"""

    parser_signature = Sig(argument_default=42)
    argument_signatures = [
        Sig('--version', action='version', version='1.0'),
        Sig('foo', nargs='?'),
        Sig('bar', nargs='*'),
        Sig('--baz', action='store_true'),
    ]
    failures = ['-x']
    successes = [
        ('', NS(foo=42, bar=42, baz=42, version=42)),
        ('a', NS(foo='a', bar=42, baz=42, version=42)),
        ('a b', NS(foo='a', bar=['b'], baz=42, version=42)),
        ('--baz', NS(foo=42, bar=42, baz=Prawda, version=42)),
        ('a --baz', NS(foo='a', bar=42, baz=Prawda, version=42)),
        ('--baz a b', NS(foo='a', bar=['b'], baz=Prawda, version=42)),
    ]


klasa TestArgumentsFromFile(TempDirMixin, ParserTestCase):
    """Test reading arguments z a file"""

    def setUp(self):
        super(TestArgumentsFromFile, self).setUp()
        file_texts = [
            ('hello', 'hello world!\n'),
            ('recursive', '-a\n'
                          'A\n'
                          '@hello'),
            ('invalid', '@no-such-path\n'),
        ]
        dla path, text w file_texts:
            file = open(path, 'w')
            file.write(text)
            file.close()

    parser_signature = Sig(fromfile_prefix_chars='@')
    argument_signatures = [
        Sig('-a'),
        Sig('x'),
        Sig('y', nargs='+'),
    ]
    failures = ['', '-b', 'X', '@invalid', '@missing']
    successes = [
        ('X Y', NS(a=Nic, x='X', y=['Y'])),
        ('X -a A Y Z', NS(a='A', x='X', y=['Y', 'Z'])),
        ('@hello X', NS(a=Nic, x='hello world!', y=['X'])),
        ('X @hello', NS(a=Nic, x='X', y=['hello world!'])),
        ('-a B @recursive Y Z', NS(a='A', x='hello world!', y=['Y', 'Z'])),
        ('X @recursive Z -a B', NS(a='B', x='X', y=['hello world!', 'Z'])),
        (["-a", "", "X", "Y"], NS(a='', x='X', y=['Y'])),
    ]


klasa TestArgumentsFromFileConverter(TempDirMixin, ParserTestCase):
    """Test reading arguments z a file"""

    def setUp(self):
        super(TestArgumentsFromFileConverter, self).setUp()
        file_texts = [
            ('hello', 'hello world!\n'),
        ]
        dla path, text w file_texts:
            file = open(path, 'w')
            file.write(text)
            file.close()

    klasa FromFileConverterArgumentParser(ErrorRaisingArgumentParser):

        def convert_arg_line_to_args(self, arg_line):
            dla arg w arg_line.split():
                jeżeli nie arg.strip():
                    kontynuuj
                uzyskaj arg
    parser_class = FromFileConverterArgumentParser
    parser_signature = Sig(fromfile_prefix_chars='@')
    argument_signatures = [
        Sig('y', nargs='+'),
    ]
    failures = []
    successes = [
        ('@hello X', NS(y=['hello', 'world!', 'X'])),
    ]


# =====================
# Type conversion tests
# =====================

klasa TestFileTypeRepr(TestCase):

    def test_r(self):
        type = argparse.FileType('r')
        self.assertEqual("FileType('r')", repr(type))

    def test_wb_1(self):
        type = argparse.FileType('wb', 1)
        self.assertEqual("FileType('wb', 1)", repr(type))

    def test_r_latin(self):
        type = argparse.FileType('r', encoding='latin_1')
        self.assertEqual("FileType('r', encoding='latin_1')", repr(type))

    def test_w_big5_ignore(self):
        type = argparse.FileType('w', encoding='big5', errors='ignore')
        self.assertEqual("FileType('w', encoding='big5', errors='ignore')",
                         repr(type))

    def test_r_1_replace(self):
        type = argparse.FileType('r', 1, errors='replace')
        self.assertEqual("FileType('r', 1, errors='replace')", repr(type))


klasa RFile(object):
    seen = {}

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        jeżeli other w self.seen:
            text = self.seen[other]
        inaczej:
            text = self.seen[other] = other.read()
            other.close()
        jeżeli nie isinstance(text, str):
            text = text.decode('ascii')
        zwróć self.name == other.name == text


klasa TestFileTypeR(TempDirMixin, ParserTestCase):
    """Test the FileType option/argument type dla reading files"""

    def setUp(self):
        super(TestFileTypeR, self).setUp()
        dla file_name w ['foo', 'bar']:
            file = open(os.path.join(self.temp_dir, file_name), 'w')
            file.write(file_name)
            file.close()
        self.create_readonly_file('readonly')

    argument_signatures = [
        Sig('-x', type=argparse.FileType()),
        Sig('spam', type=argparse.FileType('r')),
    ]
    failures = ['-x', '', 'non-existent-file.txt']
    successes = [
        ('foo', NS(x=Nic, spam=RFile('foo'))),
        ('-x foo bar', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('bar -x foo', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('-x - -', NS(x=sys.stdin, spam=sys.stdin)),
        ('readonly', NS(x=Nic, spam=RFile('readonly'))),
    ]

klasa TestFileTypeDefaults(TempDirMixin, ParserTestCase):
    """Test that a file jest nie created unless the default jest needed"""
    def setUp(self):
        super(TestFileTypeDefaults, self).setUp()
        file = open(os.path.join(self.temp_dir, 'good'), 'w')
        file.write('good')
        file.close()

    argument_signatures = [
        Sig('-c', type=argparse.FileType('r'), default='no-file.txt'),
    ]
    # should provoke no such file error
    failures = ['']
    # should nie provoke error because default file jest created
    successes = [('-c good', NS(c=RFile('good')))]


klasa TestFileTypeRB(TempDirMixin, ParserTestCase):
    """Test the FileType option/argument type dla reading files"""

    def setUp(self):
        super(TestFileTypeRB, self).setUp()
        dla file_name w ['foo', 'bar']:
            file = open(os.path.join(self.temp_dir, file_name), 'w')
            file.write(file_name)
            file.close()

    argument_signatures = [
        Sig('-x', type=argparse.FileType('rb')),
        Sig('spam', type=argparse.FileType('rb')),
    ]
    failures = ['-x', '']
    successes = [
        ('foo', NS(x=Nic, spam=RFile('foo'))),
        ('-x foo bar', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('bar -x foo', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('-x - -', NS(x=sys.stdin, spam=sys.stdin)),
    ]


klasa WFile(object):
    seen = set()

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        jeżeli other nie w self.seen:
            text = 'Check that file jest writable.'
            jeżeli 'b' w other.mode:
                text = text.encode('ascii')
            other.write(text)
            other.close()
            self.seen.add(other)
        zwróć self.name == other.name


@unittest.skipIf(hasattr(os, 'geteuid') oraz os.geteuid() == 0,
                 "non-root user required")
klasa TestFileTypeW(TempDirMixin, ParserTestCase):
    """Test the FileType option/argument type dla writing files"""

    def setUp(self):
        super(TestFileTypeW, self).setUp()
        self.create_readonly_file('readonly')

    argument_signatures = [
        Sig('-x', type=argparse.FileType('w')),
        Sig('spam', type=argparse.FileType('w')),
    ]
    failures = ['-x', '', 'readonly']
    successes = [
        ('foo', NS(x=Nic, spam=WFile('foo'))),
        ('-x foo bar', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('bar -x foo', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('-x - -', NS(x=sys.stdout, spam=sys.stdout)),
    ]


klasa TestFileTypeWB(TempDirMixin, ParserTestCase):

    argument_signatures = [
        Sig('-x', type=argparse.FileType('wb')),
        Sig('spam', type=argparse.FileType('wb')),
    ]
    failures = ['-x', '']
    successes = [
        ('foo', NS(x=Nic, spam=WFile('foo'))),
        ('-x foo bar', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('bar -x foo', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('-x - -', NS(x=sys.stdout, spam=sys.stdout)),
    ]


klasa TestFileTypeOpenArgs(TestCase):
    """Test that open (the builtin) jest correctly called"""

    def test_open_args(self):
        FT = argparse.FileType
        cases = [
            (FT('rb'), ('rb', -1, Nic, Nic)),
            (FT('w', 1), ('w', 1, Nic, Nic)),
            (FT('w', errors='replace'), ('w', -1, Nic, 'replace')),
            (FT('wb', encoding='big5'), ('wb', -1, 'big5', Nic)),
            (FT('w', 0, 'l1', 'strict'), ('w', 0, 'l1', 'strict')),
        ]
        przy mock.patch('builtins.open') jako m:
            dla type, args w cases:
                type('foo')
                m.assert_called_with('foo', *args)


klasa TestTypeCallable(ParserTestCase):
    """Test some callables jako option/argument types"""

    argument_signatures = [
        Sig('--eggs', type=complex),
        Sig('spam', type=float),
    ]
    failures = ['a', '42j', '--eggs a', '--eggs 2i']
    successes = [
        ('--eggs=42 42', NS(eggs=42, spam=42.0)),
        ('--eggs 2j -- -1.5', NS(eggs=2j, spam=-1.5)),
        ('1024.675', NS(eggs=Nic, spam=1024.675)),
    ]


klasa TestTypeUserDefined(ParserTestCase):
    """Test a user-defined option/argument type"""

    klasa MyType(TestCase):

        def __init__(self, value):
            self.value = value

        def __eq__(self, other):
            zwróć (type(self), self.value) == (type(other), other.value)

    argument_signatures = [
        Sig('-x', type=MyType),
        Sig('spam', type=MyType),
    ]
    failures = []
    successes = [
        ('a -x b', NS(x=MyType('b'), spam=MyType('a'))),
        ('-xf g', NS(x=MyType('f'), spam=MyType('g'))),
    ]


klasa TestTypeClassicClass(ParserTestCase):
    """Test a classic klasa type"""

    klasa C:

        def __init__(self, value):
            self.value = value

        def __eq__(self, other):
            zwróć (type(self), self.value) == (type(other), other.value)

    argument_signatures = [
        Sig('-x', type=C),
        Sig('spam', type=C),
    ]
    failures = []
    successes = [
        ('a -x b', NS(x=C('b'), spam=C('a'))),
        ('-xf g', NS(x=C('f'), spam=C('g'))),
    ]


klasa TestTypeRegistration(TestCase):
    """Test a user-defined type by registering it"""

    def test(self):

        def get_my_type(string):
            zwróć 'my_type{%s}' % string

        parser = argparse.ArgumentParser()
        parser.register('type', 'my_type', get_my_type)
        parser.add_argument('-x', type='my_type')
        parser.add_argument('y', type='my_type')

        self.assertEqual(parser.parse_args('1'.split()),
                         NS(x=Nic, y='my_type{1}'))
        self.assertEqual(parser.parse_args('-x 1 42'.split()),
                         NS(x='my_type{1}', y='my_type{42}'))


# ============
# Action tests
# ============

klasa TestActionUserDefined(ParserTestCase):
    """Test a user-defined option/argument action"""

    klasa OptionalAction(argparse.Action):

        def __call__(self, parser, namespace, value, option_string=Nic):
            spróbuj:
                # check destination oraz option string
                assert self.dest == 'spam', 'dest: %s' % self.dest
                assert option_string == '-s', 'flag: %s' % option_string
                # when option jest before argument, badger=2, oraz when
                # option jest after argument, badger=<whatever was set>
                expected_ns = NS(spam=0.25)
                jeżeli value w [0.125, 0.625]:
                    expected_ns.badger = 2
                albo_inaczej value w [2.0]:
                    expected_ns.badger = 84
                inaczej:
                    podnieś AssertionError('value: %s' % value)
                assert expected_ns == namespace, ('expected %s, got %s' %
                                                  (expected_ns, namespace))
            wyjąwszy AssertionError:
                e = sys.exc_info()[1]
                podnieś ArgumentParserError('opt_action failed: %s' % e)
            setattr(namespace, 'spam', value)

    klasa PositionalAction(argparse.Action):

        def __call__(self, parser, namespace, value, option_string=Nic):
            spróbuj:
                assert option_string jest Nic, ('option_string: %s' %
                                               option_string)
                # check destination
                assert self.dest == 'badger', 'dest: %s' % self.dest
                # when argument jest before option, spam=0.25, oraz when
                # option jest after argument, spam=<whatever was set>
                expected_ns = NS(badger=2)
                jeżeli value w [42, 84]:
                    expected_ns.spam = 0.25
                albo_inaczej value w [1]:
                    expected_ns.spam = 0.625
                albo_inaczej value w [2]:
                    expected_ns.spam = 0.125
                inaczej:
                    podnieś AssertionError('value: %s' % value)
                assert expected_ns == namespace, ('expected %s, got %s' %
                                                  (expected_ns, namespace))
            wyjąwszy AssertionError:
                e = sys.exc_info()[1]
                podnieś ArgumentParserError('arg_action failed: %s' % e)
            setattr(namespace, 'badger', value)

    argument_signatures = [
        Sig('-s', dest='spam', action=OptionalAction,
            type=float, default=0.25),
        Sig('badger', action=PositionalAction,
            type=int, nargs='?', default=2),
    ]
    failures = []
    successes = [
        ('-s0.125', NS(spam=0.125, badger=2)),
        ('42', NS(spam=0.25, badger=42)),
        ('-s 0.625 1', NS(spam=0.625, badger=1)),
        ('84 -s2', NS(spam=2.0, badger=84)),
    ]


klasa TestActionRegistration(TestCase):
    """Test a user-defined action supplied by registering it"""

    klasa MyAction(argparse.Action):

        def __call__(self, parser, namespace, values, option_string=Nic):
            setattr(namespace, self.dest, 'foo[%s]' % values)

    def test(self):

        parser = argparse.ArgumentParser()
        parser.register('action', 'my_action', self.MyAction)
        parser.add_argument('badger', action='my_action')

        self.assertEqual(parser.parse_args(['1']), NS(badger='foo[1]'))
        self.assertEqual(parser.parse_args(['42']), NS(badger='foo[42]'))


# ================
# Subparsers tests
# ================

klasa TestAddSubparsers(TestCase):
    """Test the add_subparsers method"""

    def assertArgumentParserError(self, *args, **kwargs):
        self.assertRaises(ArgumentParserError, *args, **kwargs)

    def _get_parser(self, subparser_help=Nieprawda, prefix_chars=Nic,
                    aliases=Nieprawda):
        # create a parser przy a subparsers argument
        jeżeli prefix_chars:
            parser = ErrorRaisingArgumentParser(
                prog='PROG', description='main description', prefix_chars=prefix_chars)
            parser.add_argument(
                prefix_chars[0] * 2 + 'foo', action='store_true', help='foo help')
        inaczej:
            parser = ErrorRaisingArgumentParser(
                prog='PROG', description='main description')
            parser.add_argument(
                '--foo', action='store_true', help='foo help')
        parser.add_argument(
            'bar', type=float, help='bar help')

        # check that only one subparsers argument can be added
        subparsers_kwargs = {}
        jeżeli aliases:
            subparsers_kwargs['metavar'] = 'COMMAND'
            subparsers_kwargs['title'] = 'commands'
        inaczej:
            subparsers_kwargs['help'] = 'command help'
        subparsers = parser.add_subparsers(**subparsers_kwargs)
        self.assertArgumentParserError(parser.add_subparsers)

        # add first sub-parser
        parser1_kwargs = dict(description='1 description')
        jeżeli subparser_help:
            parser1_kwargs['help'] = '1 help'
        jeżeli aliases:
            parser1_kwargs['aliases'] = ['1alias1', '1alias2']
        parser1 = subparsers.add_parser('1', **parser1_kwargs)
        parser1.add_argument('-w', type=int, help='w help')
        parser1.add_argument('x', choices='abc', help='x help')

        # add second sub-parser
        parser2_kwargs = dict(description='2 description')
        jeżeli subparser_help:
            parser2_kwargs['help'] = '2 help'
        parser2 = subparsers.add_parser('2', **parser2_kwargs)
        parser2.add_argument('-y', choices='123', help='y help')
        parser2.add_argument('z', type=complex, nargs='*', help='z help')

        # add third sub-parser
        parser3_kwargs = dict(description='3 description')
        jeżeli subparser_help:
            parser3_kwargs['help'] = '3 help'
        parser3 = subparsers.add_parser('3', **parser3_kwargs)
        parser3.add_argument('t', type=int, help='t help')
        parser3.add_argument('u', nargs='...', help='u help')

        # zwróć the main parser
        zwróć parser

    def setUp(self):
        super().setUp()
        self.parser = self._get_parser()
        self.command_help_parser = self._get_parser(subparser_help=Prawda)

    def test_parse_args_failures(self):
        # check some failure cases:
        dla args_str w ['', 'a', 'a a', '0.5 a', '0.5 1',
                         '0.5 1 -y', '0.5 2 -w']:
            args = args_str.split()
            self.assertArgumentParserError(self.parser.parse_args, args)

    def test_parse_args(self):
        # check some non-failure cases:
        self.assertEqual(
            self.parser.parse_args('0.5 1 b -w 7'.split()),
            NS(foo=Nieprawda, bar=0.5, w=7, x='b'),
        )
        self.assertEqual(
            self.parser.parse_args('0.25 --foo 2 -y 2 3j -- -1j'.split()),
            NS(foo=Prawda, bar=0.25, y='2', z=[3j, -1j]),
        )
        self.assertEqual(
            self.parser.parse_args('--foo 0.125 1 c'.split()),
            NS(foo=Prawda, bar=0.125, w=Nic, x='c'),
        )
        self.assertEqual(
            self.parser.parse_args('-1.5 3 11 -- a --foo 7 -- b'.split()),
            NS(foo=Nieprawda, bar=-1.5, t=11, u=['a', '--foo', '7', '--', 'b']),
        )

    def test_parse_known_args(self):
        self.assertEqual(
            self.parser.parse_known_args('0.5 1 b -w 7'.split()),
            (NS(foo=Nieprawda, bar=0.5, w=7, x='b'), []),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 -p 1 b -w 7'.split()),
            (NS(foo=Nieprawda, bar=0.5, w=7, x='b'), ['-p']),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 1 b -w 7 -p'.split()),
            (NS(foo=Nieprawda, bar=0.5, w=7, x='b'), ['-p']),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 1 b -q -rs -w 7'.split()),
            (NS(foo=Nieprawda, bar=0.5, w=7, x='b'), ['-q', '-rs']),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 -W 1 b -X Y -w 7 Z'.split()),
            (NS(foo=Nieprawda, bar=0.5, w=7, x='b'), ['-W', '-X', 'Y', 'Z']),
        )

    def test_dest(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('--foo', action='store_true')
        subparsers = parser.add_subparsers(dest='bar')
        parser1 = subparsers.add_parser('1')
        parser1.add_argument('baz')
        self.assertEqual(NS(foo=Nieprawda, bar='1', baz='2'),
                         parser.parse_args('1 2'.split()))

    def test_help(self):
        self.assertEqual(self.parser.format_usage(),
                         'usage: PROG [-h] [--foo] bar {1,2,3} ...\n')
        self.assertEqual(self.parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [--foo] bar {1,2,3} ...

            main description

            positional arguments:
              bar         bar help
              {1,2,3}     command help

            optional arguments:
              -h, --help  show this help message oraz exit
              --foo       foo help
            '''))

    def test_help_extra_prefix_chars(self):
        # Make sure - jest still used dla help jeżeli it jest a non-first prefix char
        parser = self._get_parser(prefix_chars='+:-')
        self.assertEqual(parser.format_usage(),
                         'usage: PROG [-h] [++foo] bar {1,2,3} ...\n')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [++foo] bar {1,2,3} ...

            main description

            positional arguments:
              bar         bar help
              {1,2,3}     command help

            optional arguments:
              -h, --help  show this help message oraz exit
              ++foo       foo help
            '''))


    def test_help_alternate_prefix_chars(self):
        parser = self._get_parser(prefix_chars='+:/')
        self.assertEqual(parser.format_usage(),
                         'usage: PROG [+h] [++foo] bar {1,2,3} ...\n')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [+h] [++foo] bar {1,2,3} ...

            main description

            positional arguments:
              bar         bar help
              {1,2,3}     command help

            optional arguments:
              +h, ++help  show this help message oraz exit
              ++foo       foo help
            '''))

    def test_parser_command_help(self):
        self.assertEqual(self.command_help_parser.format_usage(),
                         'usage: PROG [-h] [--foo] bar {1,2,3} ...\n')
        self.assertEqual(self.command_help_parser.format_help(),
                         textwrap.dedent('''\
            usage: PROG [-h] [--foo] bar {1,2,3} ...

            main description

            positional arguments:
              bar         bar help
              {1,2,3}     command help
                1         1 help
                2         2 help
                3         3 help

            optional arguments:
              -h, --help  show this help message oraz exit
              --foo       foo help
            '''))

    def test_subparser_title_help(self):
        parser = ErrorRaisingArgumentParser(prog='PROG',
                                            description='main description')
        parser.add_argument('--foo', action='store_true', help='foo help')
        parser.add_argument('bar', help='bar help')
        subparsers = parser.add_subparsers(title='subcommands',
                                           description='command help',
                                           help='additional text')
        parser1 = subparsers.add_parser('1')
        parser2 = subparsers.add_parser('2')
        self.assertEqual(parser.format_usage(),
                         'usage: PROG [-h] [--foo] bar {1,2} ...\n')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [--foo] bar {1,2} ...

            main description

            positional arguments:
              bar         bar help

            optional arguments:
              -h, --help  show this help message oraz exit
              --foo       foo help

            subcommands:
              command help

              {1,2}       additional text
            '''))

    def _test_subparser_help(self, args_str, expected_help):
        przy self.assertRaises(ArgumentParserError) jako cm:
            self.parser.parse_args(args_str.split())
        self.assertEqual(expected_help, cm.exception.stdout)

    def test_subparser1_help(self):
        self._test_subparser_help('5.0 1 -h', textwrap.dedent('''\
            usage: PROG bar 1 [-h] [-w W] {a,b,c}

            1 description

            positional arguments:
              {a,b,c}     x help

            optional arguments:
              -h, --help  show this help message oraz exit
              -w W        w help
            '''))

    def test_subparser2_help(self):
        self._test_subparser_help('5.0 2 -h', textwrap.dedent('''\
            usage: PROG bar 2 [-h] [-y {1,2,3}] [z [z ...]]

            2 description

            positional arguments:
              z           z help

            optional arguments:
              -h, --help  show this help message oraz exit
              -y {1,2,3}  y help
            '''))

    def test_alias_invocation(self):
        parser = self._get_parser(aliases=Prawda)
        self.assertEqual(
            parser.parse_known_args('0.5 1alias1 b'.split()),
            (NS(foo=Nieprawda, bar=0.5, w=Nic, x='b'), []),
        )
        self.assertEqual(
            parser.parse_known_args('0.5 1alias2 b'.split()),
            (NS(foo=Nieprawda, bar=0.5, w=Nic, x='b'), []),
        )

    def test_error_alias_invocation(self):
        parser = self._get_parser(aliases=Prawda)
        self.assertArgumentParserError(parser.parse_args,
                                       '0.5 1alias3 b'.split())

    def test_alias_help(self):
        parser = self._get_parser(aliases=Prawda, subparser_help=Prawda)
        self.maxDiff = Nic
        self.assertEqual(parser.format_help(), textwrap.dedent("""\
            usage: PROG [-h] [--foo] bar COMMAND ...

            main description

            positional arguments:
              bar                   bar help

            optional arguments:
              -h, --help            show this help message oraz exit
              --foo                 foo help

            commands:
              COMMAND
                1 (1alias1, 1alias2)
                                    1 help
                2                   2 help
                3                   3 help
            """))

# ============
# Groups tests
# ============

klasa TestPositionalsGroups(TestCase):
    """Tests that order of group positionals matches construction order"""

    def test_nongroup_first(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('foo')
        group = parser.add_argument_group('g')
        group.add_argument('bar')
        parser.add_argument('baz')
        expected = NS(foo='1', bar='2', baz='3')
        result = parser.parse_args('1 2 3'.split())
        self.assertEqual(expected, result)

    def test_group_first(self):
        parser = ErrorRaisingArgumentParser()
        group = parser.add_argument_group('xxx')
        group.add_argument('foo')
        parser.add_argument('bar')
        parser.add_argument('baz')
        expected = NS(foo='1', bar='2', baz='3')
        result = parser.parse_args('1 2 3'.split())
        self.assertEqual(expected, result)

    def test_interleaved_groups(self):
        parser = ErrorRaisingArgumentParser()
        group = parser.add_argument_group('xxx')
        parser.add_argument('foo')
        group.add_argument('bar')
        parser.add_argument('baz')
        group = parser.add_argument_group('yyy')
        group.add_argument('frell')
        expected = NS(foo='1', bar='2', baz='3', frell='4')
        result = parser.parse_args('1 2 3 4'.split())
        self.assertEqual(expected, result)

# ===================
# Parent parser tests
# ===================

klasa TestParentParsers(TestCase):
    """Tests that parsers can be created przy parent parsers"""

    def assertArgumentParserError(self, *args, **kwargs):
        self.assertRaises(ArgumentParserError, *args, **kwargs)

    def setUp(self):
        super().setUp()
        self.wxyz_parent = ErrorRaisingArgumentParser(add_help=Nieprawda)
        self.wxyz_parent.add_argument('--w')
        x_group = self.wxyz_parent.add_argument_group('x')
        x_group.add_argument('-y')
        self.wxyz_parent.add_argument('z')

        self.abcd_parent = ErrorRaisingArgumentParser(add_help=Nieprawda)
        self.abcd_parent.add_argument('a')
        self.abcd_parent.add_argument('-b')
        c_group = self.abcd_parent.add_argument_group('c')
        c_group.add_argument('--d')

        self.w_parent = ErrorRaisingArgumentParser(add_help=Nieprawda)
        self.w_parent.add_argument('--w')

        self.z_parent = ErrorRaisingArgumentParser(add_help=Nieprawda)
        self.z_parent.add_argument('z')

        # parents przy mutually exclusive groups
        self.ab_mutex_parent = ErrorRaisingArgumentParser(add_help=Nieprawda)
        group = self.ab_mutex_parent.add_mutually_exclusive_group()
        group.add_argument('-a', action='store_true')
        group.add_argument('-b', action='store_true')

        self.main_program = os.path.basename(sys.argv[0])

    def test_single_parent(self):
        parser = ErrorRaisingArgumentParser(parents=[self.wxyz_parent])
        self.assertEqual(parser.parse_args('-y 1 2 --w 3'.split()),
                         NS(w='3', y='1', z='2'))

    def test_single_parent_mutex(self):
        self._test_mutex_ab(self.ab_mutex_parent.parse_args)
        parser = ErrorRaisingArgumentParser(parents=[self.ab_mutex_parent])
        self._test_mutex_ab(parser.parse_args)

    def test_single_granparent_mutex(self):
        parents = [self.ab_mutex_parent]
        parser = ErrorRaisingArgumentParser(add_help=Nieprawda, parents=parents)
        parser = ErrorRaisingArgumentParser(parents=[parser])
        self._test_mutex_ab(parser.parse_args)

    def _test_mutex_ab(self, parse_args):
        self.assertEqual(parse_args([]), NS(a=Nieprawda, b=Nieprawda))
        self.assertEqual(parse_args(['-a']), NS(a=Prawda, b=Nieprawda))
        self.assertEqual(parse_args(['-b']), NS(a=Nieprawda, b=Prawda))
        self.assertArgumentParserError(parse_args, ['-a', '-b'])
        self.assertArgumentParserError(parse_args, ['-b', '-a'])
        self.assertArgumentParserError(parse_args, ['-c'])
        self.assertArgumentParserError(parse_args, ['-a', '-c'])
        self.assertArgumentParserError(parse_args, ['-b', '-c'])

    def test_multiple_parents(self):
        parents = [self.abcd_parent, self.wxyz_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        self.assertEqual(parser.parse_args('--d 1 --w 2 3 4'.split()),
                         NS(a='3', b=Nic, d='1', w='2', y=Nic, z='4'))

    def test_multiple_parents_mutex(self):
        parents = [self.ab_mutex_parent, self.wxyz_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        self.assertEqual(parser.parse_args('-a --w 2 3'.split()),
                         NS(a=Prawda, b=Nieprawda, w='2', y=Nic, z='3'))
        self.assertArgumentParserError(
            parser.parse_args, '-a --w 2 3 -b'.split())
        self.assertArgumentParserError(
            parser.parse_args, '-a -b --w 2 3'.split())

    def test_conflicting_parents(self):
        self.assertRaises(
            argparse.ArgumentError,
            argparse.ArgumentParser,
            parents=[self.w_parent, self.wxyz_parent])

    def test_conflicting_parents_mutex(self):
        self.assertRaises(
            argparse.ArgumentError,
            argparse.ArgumentParser,
            parents=[self.abcd_parent, self.ab_mutex_parent])

    def test_same_argument_name_parents(self):
        parents = [self.wxyz_parent, self.z_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        self.assertEqual(parser.parse_args('1 2'.split()),
                         NS(w=Nic, y=Nic, z='2'))

    def test_subparser_parents(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers()
        abcde_parser = subparsers.add_parser('bar', parents=[self.abcd_parent])
        abcde_parser.add_argument('e')
        self.assertEqual(parser.parse_args('bar -b 1 --d 2 3 4'.split()),
                         NS(a='3', b='1', d='2', e='4'))

    def test_subparser_parents_mutex(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers()
        parents = [self.ab_mutex_parent]
        abc_parser = subparsers.add_parser('foo', parents=parents)
        c_group = abc_parser.add_argument_group('c_group')
        c_group.add_argument('c')
        parents = [self.wxyz_parent, self.ab_mutex_parent]
        wxyzabe_parser = subparsers.add_parser('bar', parents=parents)
        wxyzabe_parser.add_argument('e')
        self.assertEqual(parser.parse_args('foo -a 4'.split()),
                         NS(a=Prawda, b=Nieprawda, c='4'))
        self.assertEqual(parser.parse_args('bar -b  --w 2 3 4'.split()),
                         NS(a=Nieprawda, b=Prawda, w='2', y=Nic, z='3', e='4'))
        self.assertArgumentParserError(
            parser.parse_args, 'foo -a -b 4'.split())
        self.assertArgumentParserError(
            parser.parse_args, 'bar -b -a 4'.split())

    def test_parent_help(self):
        parents = [self.abcd_parent, self.wxyz_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        parser_help = parser.format_help()
        progname = self.main_program
        self.assertEqual(parser_help, textwrap.dedent('''\
            usage: {}{}[-h] [-b B] [--d D] [--w W] [-y Y] a z

            positional arguments:
              a
              z

            optional arguments:
              -h, --help  show this help message oraz exit
              -b B
              --w W

            c:
              --d D

            x:
              -y Y
        '''.format(progname, ' ' jeżeli progname inaczej '' )))

    def test_groups_parents(self):
        parent = ErrorRaisingArgumentParser(add_help=Nieprawda)
        g = parent.add_argument_group(title='g', description='gd')
        g.add_argument('-w')
        g.add_argument('-x')
        m = parent.add_mutually_exclusive_group()
        m.add_argument('-y')
        m.add_argument('-z')
        parser = ErrorRaisingArgumentParser(parents=[parent])

        self.assertRaises(ArgumentParserError, parser.parse_args,
            ['-y', 'Y', '-z', 'Z'])

        parser_help = parser.format_help()
        progname = self.main_program
        self.assertEqual(parser_help, textwrap.dedent('''\
            usage: {}{}[-h] [-w W] [-x X] [-y Y | -z Z]

            optional arguments:
              -h, --help  show this help message oraz exit
              -y Y
              -z Z

            g:
              gd

              -w W
              -x X
        '''.format(progname, ' ' jeżeli progname inaczej '' )))

# ==============================
# Mutually exclusive group tests
# ==============================

klasa TestMutuallyExclusiveGroupErrors(TestCase):

    def test_invalid_add_argument_group(self):
        parser = ErrorRaisingArgumentParser()
        podnieśs = self.assertRaises
        podnieśs(TypeError, parser.add_mutually_exclusive_group, title='foo')

    def test_invalid_add_argument(self):
        parser = ErrorRaisingArgumentParser()
        group = parser.add_mutually_exclusive_group()
        add_argument = group.add_argument
        podnieśs = self.assertRaises
        podnieśs(ValueError, add_argument, '--foo', required=Prawda)
        podnieśs(ValueError, add_argument, 'bar')
        podnieśs(ValueError, add_argument, 'bar', nargs='+')
        podnieśs(ValueError, add_argument, 'bar', nargs=1)
        podnieśs(ValueError, add_argument, 'bar', nargs=argparse.PARSER)

    def test_help(self):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument('--foo', action='store_true')
        group1.add_argument('--bar', action='store_false')
        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument('--soup', action='store_true')
        group2.add_argument('--nuts', action='store_false')
        expected = '''\
            usage: PROG [-h] [--foo | --bar] [--soup | --nuts]

            optional arguments:
              -h, --help  show this help message oraz exit
              --foo
              --bar
              --soup
              --nuts
              '''
        self.assertEqual(parser.format_help(), textwrap.dedent(expected))

klasa MEMixin(object):

    def test_failures_when_not_required(self):
        parse_args = self.get_parser(required=Nieprawda).parse_args
        error = ArgumentParserError
        dla args_string w self.failures:
            self.assertRaises(error, parse_args, args_string.split())

    def test_failures_when_required(self):
        parse_args = self.get_parser(required=Prawda).parse_args
        error = ArgumentParserError
        dla args_string w self.failures + ['']:
            self.assertRaises(error, parse_args, args_string.split())

    def test_successes_when_not_required(self):
        parse_args = self.get_parser(required=Nieprawda).parse_args
        successes = self.successes + self.successes_when_not_required
        dla args_string, expected_ns w successes:
            actual_ns = parse_args(args_string.split())
            self.assertEqual(actual_ns, expected_ns)

    def test_successes_when_required(self):
        parse_args = self.get_parser(required=Prawda).parse_args
        dla args_string, expected_ns w self.successes:
            actual_ns = parse_args(args_string.split())
            self.assertEqual(actual_ns, expected_ns)

    def test_usage_when_not_required(self):
        format_usage = self.get_parser(required=Nieprawda).format_usage
        expected_usage = self.usage_when_not_required
        self.assertEqual(format_usage(), textwrap.dedent(expected_usage))

    def test_usage_when_required(self):
        format_usage = self.get_parser(required=Prawda).format_usage
        expected_usage = self.usage_when_required
        self.assertEqual(format_usage(), textwrap.dedent(expected_usage))

    def test_help_when_not_required(self):
        format_help = self.get_parser(required=Nieprawda).format_help
        help = self.usage_when_not_required + self.help
        self.assertEqual(format_help(), textwrap.dedent(help))

    def test_help_when_required(self):
        format_help = self.get_parser(required=Prawda).format_help
        help = self.usage_when_required + self.help
        self.assertEqual(format_help(), textwrap.dedent(help))


klasa TestMutuallyExclusiveSimple(MEMixin, TestCase):

    def get_parser(self, required=Nic):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('--bar', help='bar help')
        group.add_argument('--baz', nargs='?', const='Z', help='baz help')
        zwróć parser

    failures = ['--bar X --baz Y', '--bar X --baz']
    successes = [
        ('--bar X', NS(bar='X', baz=Nic)),
        ('--bar X --bar Z', NS(bar='Z', baz=Nic)),
        ('--baz Y', NS(bar=Nic, baz='Y')),
        ('--baz', NS(bar=Nic, baz='Z')),
    ]
    successes_when_not_required = [
        ('', NS(bar=Nic, baz=Nic)),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [--bar BAR | --baz [BAZ]]
        '''
    usage_when_required = '''\
        usage: PROG [-h] (--bar BAR | --baz [BAZ])
        '''
    help = '''\

        optional arguments:
          -h, --help   show this help message oraz exit
          --bar BAR    bar help
          --baz [BAZ]  baz help
        '''


klasa TestMutuallyExclusiveLong(MEMixin, TestCase):

    def get_parser(self, required=Nic):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        parser.add_argument('--abcde', help='abcde help')
        parser.add_argument('--fghij', help='fghij help')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('--klmno', help='klmno help')
        group.add_argument('--pqrst', help='pqrst help')
        zwróć parser

    failures = ['--klmno X --pqrst Y']
    successes = [
        ('--klmno X', NS(abcde=Nic, fghij=Nic, klmno='X', pqrst=Nic)),
        ('--abcde Y --klmno X',
            NS(abcde='Y', fghij=Nic, klmno='X', pqrst=Nic)),
        ('--pqrst X', NS(abcde=Nic, fghij=Nic, klmno=Nic, pqrst='X')),
        ('--pqrst X --fghij Y',
            NS(abcde=Nic, fghij='Y', klmno=Nic, pqrst='X')),
    ]
    successes_when_not_required = [
        ('', NS(abcde=Nic, fghij=Nic, klmno=Nic, pqrst=Nic)),
    ]

    usage_when_not_required = '''\
    usage: PROG [-h] [--abcde ABCDE] [--fghij FGHIJ]
                [--klmno KLMNO | --pqrst PQRST]
    '''
    usage_when_required = '''\
    usage: PROG [-h] [--abcde ABCDE] [--fghij FGHIJ]
                (--klmno KLMNO | --pqrst PQRST)
    '''
    help = '''\

    optional arguments:
      -h, --help     show this help message oraz exit
      --abcde ABCDE  abcde help
      --fghij FGHIJ  fghij help
      --klmno KLMNO  klmno help
      --pqrst PQRST  pqrst help
    '''


klasa TestMutuallyExclusiveFirstSuppressed(MEMixin, TestCase):

    def get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('-x', help=argparse.SUPPRESS)
        group.add_argument('-y', action='store_false', help='y help')
        zwróć parser

    failures = ['-x X -y']
    successes = [
        ('-x X', NS(x='X', y=Prawda)),
        ('-x X -x Y', NS(x='Y', y=Prawda)),
        ('-y', NS(x=Nic, y=Nieprawda)),
    ]
    successes_when_not_required = [
        ('', NS(x=Nic, y=Prawda)),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [-y]
        '''
    usage_when_required = '''\
        usage: PROG [-h] -y
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message oraz exit
          -y          y help
        '''


klasa TestMutuallyExclusiveManySuppressed(MEMixin, TestCase):

    def get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        add = group.add_argument
        add('--spam', action='store_true', help=argparse.SUPPRESS)
        add('--badger', action='store_false', help=argparse.SUPPRESS)
        add('--bladder', help=argparse.SUPPRESS)
        zwróć parser

    failures = [
        '--spam --badger',
        '--badger --bladder B',
        '--bladder B --spam',
    ]
    successes = [
        ('--spam', NS(spam=Prawda, badger=Prawda, bladder=Nic)),
        ('--badger', NS(spam=Nieprawda, badger=Nieprawda, bladder=Nic)),
        ('--bladder B', NS(spam=Nieprawda, badger=Prawda, bladder='B')),
        ('--spam --spam', NS(spam=Prawda, badger=Prawda, bladder=Nic)),
    ]
    successes_when_not_required = [
        ('', NS(spam=Nieprawda, badger=Prawda, bladder=Nic)),
    ]

    usage_when_required = usage_when_not_required = '''\
        usage: PROG [-h]
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message oraz exit
        '''


klasa TestMutuallyExclusiveOptionalAndPositional(MEMixin, TestCase):

    def get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('--foo', action='store_true', help='FOO')
        group.add_argument('--spam', help='SPAM')
        group.add_argument('badger', nargs='*', default='X', help='BADGER')
        zwróć parser

    failures = [
        '--foo --spam S',
        '--spam S X',
        'X --foo',
        'X Y Z --spam S',
        '--foo X Y',
    ]
    successes = [
        ('--foo', NS(foo=Prawda, spam=Nic, badger='X')),
        ('--spam S', NS(foo=Nieprawda, spam='S', badger='X')),
        ('X', NS(foo=Nieprawda, spam=Nic, badger=['X'])),
        ('X Y Z', NS(foo=Nieprawda, spam=Nic, badger=['X', 'Y', 'Z'])),
    ]
    successes_when_not_required = [
        ('', NS(foo=Nieprawda, spam=Nic, badger='X')),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [--foo | --spam SPAM | badger [badger ...]]
        '''
    usage_when_required = '''\
        usage: PROG [-h] (--foo | --spam SPAM | badger [badger ...])
        '''
    help = '''\

        positional arguments:
          badger       BADGER

        optional arguments:
          -h, --help   show this help message oraz exit
          --foo        FOO
          --spam SPAM  SPAM
        '''


klasa TestMutuallyExclusiveOptionalsMixed(MEMixin, TestCase):

    def get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        parser.add_argument('-x', action='store_true', help='x help')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('-a', action='store_true', help='a help')
        group.add_argument('-b', action='store_true', help='b help')
        parser.add_argument('-y', action='store_true', help='y help')
        group.add_argument('-c', action='store_true', help='c help')
        zwróć parser

    failures = ['-a -b', '-b -c', '-a -c', '-a -b -c']
    successes = [
        ('-a', NS(a=Prawda, b=Nieprawda, c=Nieprawda, x=Nieprawda, y=Nieprawda)),
        ('-b', NS(a=Nieprawda, b=Prawda, c=Nieprawda, x=Nieprawda, y=Nieprawda)),
        ('-c', NS(a=Nieprawda, b=Nieprawda, c=Prawda, x=Nieprawda, y=Nieprawda)),
        ('-a -x', NS(a=Prawda, b=Nieprawda, c=Nieprawda, x=Prawda, y=Nieprawda)),
        ('-y -b', NS(a=Nieprawda, b=Prawda, c=Nieprawda, x=Nieprawda, y=Prawda)),
        ('-x -y -c', NS(a=Nieprawda, b=Nieprawda, c=Prawda, x=Prawda, y=Prawda)),
    ]
    successes_when_not_required = [
        ('', NS(a=Nieprawda, b=Nieprawda, c=Nieprawda, x=Nieprawda, y=Nieprawda)),
        ('-x', NS(a=Nieprawda, b=Nieprawda, c=Nieprawda, x=Prawda, y=Nieprawda)),
        ('-y', NS(a=Nieprawda, b=Nieprawda, c=Nieprawda, x=Nieprawda, y=Prawda)),
    ]

    usage_when_required = usage_when_not_required = '''\
        usage: PROG [-h] [-x] [-a] [-b] [-y] [-c]
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message oraz exit
          -x          x help
          -a          a help
          -b          b help
          -y          y help
          -c          c help
        '''


klasa TestMutuallyExclusiveInGroup(MEMixin, TestCase):

    def get_parser(self, required=Nic):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        titled_group = parser.add_argument_group(
            title='Titled group', description='Group description')
        mutex_group = \
            titled_group.add_mutually_exclusive_group(required=required)
        mutex_group.add_argument('--bar', help='bar help')
        mutex_group.add_argument('--baz', help='baz help')
        zwróć parser

    failures = ['--bar X --baz Y', '--baz X --bar Y']
    successes = [
        ('--bar X', NS(bar='X', baz=Nic)),
        ('--baz Y', NS(bar=Nic, baz='Y')),
    ]
    successes_when_not_required = [
        ('', NS(bar=Nic, baz=Nic)),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [--bar BAR | --baz BAZ]
        '''
    usage_when_required = '''\
        usage: PROG [-h] (--bar BAR | --baz BAZ)
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message oraz exit

        Titled group:
          Group description

          --bar BAR   bar help
          --baz BAZ   baz help
        '''


klasa TestMutuallyExclusiveOptionalsAndPositionalsMixed(MEMixin, TestCase):

    def get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        parser.add_argument('x', help='x help')
        parser.add_argument('-y', action='store_true', help='y help')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('a', nargs='?', help='a help')
        group.add_argument('-b', action='store_true', help='b help')
        group.add_argument('-c', action='store_true', help='c help')
        zwróć parser

    failures = ['X A -b', '-b -c', '-c X A']
    successes = [
        ('X A', NS(a='A', b=Nieprawda, c=Nieprawda, x='X', y=Nieprawda)),
        ('X -b', NS(a=Nic, b=Prawda, c=Nieprawda, x='X', y=Nieprawda)),
        ('X -c', NS(a=Nic, b=Nieprawda, c=Prawda, x='X', y=Nieprawda)),
        ('X A -y', NS(a='A', b=Nieprawda, c=Nieprawda, x='X', y=Prawda)),
        ('X -y -b', NS(a=Nic, b=Prawda, c=Nieprawda, x='X', y=Prawda)),
    ]
    successes_when_not_required = [
        ('X', NS(a=Nic, b=Nieprawda, c=Nieprawda, x='X', y=Nieprawda)),
        ('X -y', NS(a=Nic, b=Nieprawda, c=Nieprawda, x='X', y=Prawda)),
    ]

    usage_when_required = usage_when_not_required = '''\
        usage: PROG [-h] [-y] [-b] [-c] x [a]
        '''
    help = '''\

        positional arguments:
          x           x help
          a           a help

        optional arguments:
          -h, --help  show this help message oraz exit
          -y          y help
          -b          b help
          -c          c help
        '''

# =================================================
# Mutually exclusive group w parent parser tests
# =================================================

klasa MEPBase(object):

    def get_parser(self, required=Nic):
        parent = super(MEPBase, self).get_parser(required=required)
        parser = ErrorRaisingArgumentParser(
            prog=parent.prog, add_help=Nieprawda, parents=[parent])
        zwróć parser


klasa TestMutuallyExclusiveGroupErrorsParent(
    MEPBase, TestMutuallyExclusiveGroupErrors):
    dalej


klasa TestMutuallyExclusiveSimpleParent(
    MEPBase, TestMutuallyExclusiveSimple):
    dalej


klasa TestMutuallyExclusiveLongParent(
    MEPBase, TestMutuallyExclusiveLong):
    dalej


klasa TestMutuallyExclusiveFirstSuppressedParent(
    MEPBase, TestMutuallyExclusiveFirstSuppressed):
    dalej


klasa TestMutuallyExclusiveManySuppressedParent(
    MEPBase, TestMutuallyExclusiveManySuppressed):
    dalej


klasa TestMutuallyExclusiveOptionalAndPositionalParent(
    MEPBase, TestMutuallyExclusiveOptionalAndPositional):
    dalej


klasa TestMutuallyExclusiveOptionalsMixedParent(
    MEPBase, TestMutuallyExclusiveOptionalsMixed):
    dalej


klasa TestMutuallyExclusiveOptionalsAndPositionalsMixedParent(
    MEPBase, TestMutuallyExclusiveOptionalsAndPositionalsMixed):
    dalej

# =================
# Set default tests
# =================

klasa TestSetDefaults(TestCase):

    def test_set_defaults_no_args(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(x='foo')
        parser.set_defaults(y='bar', z=1)
        self.assertEqual(NS(x='foo', y='bar', z=1),
                         parser.parse_args([]))
        self.assertEqual(NS(x='foo', y='bar', z=1),
                         parser.parse_args([], NS()))
        self.assertEqual(NS(x='baz', y='bar', z=1),
                         parser.parse_args([], NS(x='baz')))
        self.assertEqual(NS(x='baz', y='bar', z=2),
                         parser.parse_args([], NS(x='baz', z=2)))

    def test_set_defaults_with_args(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(x='foo', y='bar')
        parser.add_argument('-x', default='xfoox')
        self.assertEqual(NS(x='xfoox', y='bar'),
                         parser.parse_args([]))
        self.assertEqual(NS(x='xfoox', y='bar'),
                         parser.parse_args([], NS()))
        self.assertEqual(NS(x='baz', y='bar'),
                         parser.parse_args([], NS(x='baz')))
        self.assertEqual(NS(x='1', y='bar'),
                         parser.parse_args('-x 1'.split()))
        self.assertEqual(NS(x='1', y='bar'),
                         parser.parse_args('-x 1'.split(), NS()))
        self.assertEqual(NS(x='1', y='bar'),
                         parser.parse_args('-x 1'.split(), NS(x='baz')))

    def test_set_defaults_subparsers(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(x='foo')
        subparsers = parser.add_subparsers()
        parser_a = subparsers.add_parser('a')
        parser_a.set_defaults(y='bar')
        self.assertEqual(NS(x='foo', y='bar'),
                         parser.parse_args('a'.split()))

    def test_set_defaults_parents(self):
        parent = ErrorRaisingArgumentParser(add_help=Nieprawda)
        parent.set_defaults(x='foo')
        parser = ErrorRaisingArgumentParser(parents=[parent])
        self.assertEqual(NS(x='foo'), parser.parse_args([]))

    def test_set_defaults_on_parent_and_subparser(self):
        parser = argparse.ArgumentParser()
        xparser = parser.add_subparsers().add_parser('X')
        parser.set_defaults(foo=1)
        xparser.set_defaults(foo=2)
        self.assertEqual(NS(foo=2), parser.parse_args(['X']))

    def test_set_defaults_same_as_add_argument(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(w='W', x='X', y='Y', z='Z')
        parser.add_argument('-w')
        parser.add_argument('-x', default='XX')
        parser.add_argument('y', nargs='?')
        parser.add_argument('z', nargs='?', default='ZZ')

        # defaults set previously
        self.assertEqual(NS(w='W', x='XX', y='Y', z='ZZ'),
                         parser.parse_args([]))

        # reset defaults
        parser.set_defaults(w='WW', x='X', y='YY', z='Z')
        self.assertEqual(NS(w='WW', x='X', y='YY', z='Z'),
                         parser.parse_args([]))

    def test_set_defaults_same_as_add_argument_group(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(w='W', x='X', y='Y', z='Z')
        group = parser.add_argument_group('foo')
        group.add_argument('-w')
        group.add_argument('-x', default='XX')
        group.add_argument('y', nargs='?')
        group.add_argument('z', nargs='?', default='ZZ')


        # defaults set previously
        self.assertEqual(NS(w='W', x='XX', y='Y', z='ZZ'),
                         parser.parse_args([]))

        # reset defaults
        parser.set_defaults(w='WW', x='X', y='YY', z='Z')
        self.assertEqual(NS(w='WW', x='X', y='YY', z='Z'),
                         parser.parse_args([]))

# =================
# Get default tests
# =================

klasa TestGetDefault(TestCase):

    def test_get_default(self):
        parser = ErrorRaisingArgumentParser()
        self.assertIsNic(parser.get_default("foo"))
        self.assertIsNic(parser.get_default("bar"))

        parser.add_argument("--foo")
        self.assertIsNic(parser.get_default("foo"))
        self.assertIsNic(parser.get_default("bar"))

        parser.add_argument("--bar", type=int, default=42)
        self.assertIsNic(parser.get_default("foo"))
        self.assertEqual(42, parser.get_default("bar"))

        parser.set_defaults(foo="badger")
        self.assertEqual("badger", parser.get_default("foo"))
        self.assertEqual(42, parser.get_default("bar"))

# ==========================
# Namespace 'contains' tests
# ==========================

klasa TestNamespaceContainsSimple(TestCase):

    def test_empty(self):
        ns = argparse.Namespace()
        self.assertNotIn('', ns)
        self.assertNotIn('x', ns)

    def test_non_empty(self):
        ns = argparse.Namespace(x=1, y=2)
        self.assertNotIn('', ns)
        self.assertIn('x', ns)
        self.assertIn('y', ns)
        self.assertNotIn('xx', ns)
        self.assertNotIn('z', ns)

# =====================
# Help formatting tests
# =====================

klasa TestHelpFormattingMetaclass(type):

    def __init__(cls, name, bases, bodydict):
        jeżeli name == 'HelpTestCase':
            zwróć

        klasa AddTests(object):

            def __init__(self, test_class, func_suffix, std_name):
                self.func_suffix = func_suffix
                self.std_name = std_name

                dla test_func w [self.test_format,
                                  self.test_print,
                                  self.test_print_file]:
                    test_name = '%s_%s' % (test_func.__name__, func_suffix)

                    def test_wrapper(self, test_func=test_func):
                        test_func(self)
                    spróbuj:
                        test_wrapper.__name__ = test_name
                    wyjąwszy TypeError:
                        dalej
                    setattr(test_class, test_name, test_wrapper)

            def _get_parser(self, tester):
                parser = argparse.ArgumentParser(
                    *tester.parser_signature.args,
                    **tester.parser_signature.kwargs)
                dla argument_sig w getattr(tester, 'argument_signatures', []):
                    parser.add_argument(*argument_sig.args,
                                        **argument_sig.kwargs)
                group_sigs = getattr(tester, 'argument_group_signatures', [])
                dla group_sig, argument_sigs w group_sigs:
                    group = parser.add_argument_group(*group_sig.args,
                                                      **group_sig.kwargs)
                    dla argument_sig w argument_sigs:
                        group.add_argument(*argument_sig.args,
                                           **argument_sig.kwargs)
                subparsers_sigs = getattr(tester, 'subparsers_signatures', [])
                jeżeli subparsers_sigs:
                    subparsers = parser.add_subparsers()
                    dla subparser_sig w subparsers_sigs:
                        subparsers.add_parser(*subparser_sig.args,
                                               **subparser_sig.kwargs)
                zwróć parser

            def _test(self, tester, parser_text):
                expected_text = getattr(tester, self.func_suffix)
                expected_text = textwrap.dedent(expected_text)
                tester.assertEqual(expected_text, parser_text)

            def test_format(self, tester):
                parser = self._get_parser(tester)
                format = getattr(parser, 'format_%s' % self.func_suffix)
                self._test(tester, format())

            def test_print(self, tester):
                parser = self._get_parser(tester)
                print_ = getattr(parser, 'print_%s' % self.func_suffix)
                old_stream = getattr(sys, self.std_name)
                setattr(sys, self.std_name, StdIOBuffer())
                spróbuj:
                    print_()
                    parser_text = getattr(sys, self.std_name).getvalue()
                w_końcu:
                    setattr(sys, self.std_name, old_stream)
                self._test(tester, parser_text)

            def test_print_file(self, tester):
                parser = self._get_parser(tester)
                print_ = getattr(parser, 'print_%s' % self.func_suffix)
                sfile = StdIOBuffer()
                print_(sfile)
                parser_text = sfile.getvalue()
                self._test(tester, parser_text)

        # add tests dla {format,print}_{usage,help}
        dla func_suffix, std_name w [('usage', 'stdout'),
                                      ('help', 'stdout')]:
            AddTests(cls, func_suffix, std_name)

bases = TestCase,
HelpTestCase = TestHelpFormattingMetaclass('HelpTestCase', bases, {})


klasa TestHelpBiggerOptionals(HelpTestCase):
    """Make sure that argument help aligns when options are longer"""

    parser_signature = Sig(prog='PROG', description='DESCRIPTION',
                           epilog='EPILOG')
    argument_signatures = [
        Sig('-v', '--version', action='version', version='0.1'),
        Sig('-x', action='store_true', help='X HELP'),
        Sig('--y', help='Y HELP'),
        Sig('foo', help='FOO HELP'),
        Sig('bar', help='BAR HELP'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-v] [-x] [--y Y] foo bar
        '''
    help = usage + '''\

        DESCRIPTION

        positional arguments:
          foo            FOO HELP
          bar            BAR HELP

        optional arguments:
          -h, --help     show this help message oraz exit
          -v, --version  show program's version number oraz exit
          -x             X HELP
          --y Y          Y HELP

        EPILOG
    '''
    version = '''\
        0.1
        '''

klasa TestShortColumns(HelpTestCase):
    '''Test extremely small number of columns.

    TestCase prevents "COLUMNS" z being too small w the tests themselves,
    but we don't want any exceptions thrown w such case. Only ugly representation.
    '''
    def setUp(self):
        env = support.EnvironmentVarGuard()
        env.set("COLUMNS", '15')
        self.addCleanup(env.__exit__)

    parser_signature            = TestHelpBiggerOptionals.parser_signature
    argument_signatures         = TestHelpBiggerOptionals.argument_signatures
    argument_group_signatures   = TestHelpBiggerOptionals.argument_group_signatures
    usage = '''\
        usage: PROG
               [-h]
               [-v]
               [-x]
               [--y Y]
               foo
               bar
        '''
    help = usage + '''\

        DESCRIPTION

        positional arguments:
          foo
            FOO HELP
          bar
            BAR HELP

        optional arguments:
          -h, --help
            show this
            help
            message oraz
            exit
          -v, --version
            show
            program's
            version
            number oraz
            exit
          -x
            X HELP
          --y Y
            Y HELP

        EPILOG
    '''
    version                     = TestHelpBiggerOptionals.version


klasa TestHelpBiggerOptionalGroups(HelpTestCase):
    """Make sure that argument help aligns when options are longer"""

    parser_signature = Sig(prog='PROG', description='DESCRIPTION',
                           epilog='EPILOG')
    argument_signatures = [
        Sig('-v', '--version', action='version', version='0.1'),
        Sig('-x', action='store_true', help='X HELP'),
        Sig('--y', help='Y HELP'),
        Sig('foo', help='FOO HELP'),
        Sig('bar', help='BAR HELP'),
    ]
    argument_group_signatures = [
        (Sig('GROUP TITLE', description='GROUP DESCRIPTION'), [
            Sig('baz', help='BAZ HELP'),
            Sig('-z', nargs='+', help='Z HELP')]),
    ]
    usage = '''\
        usage: PROG [-h] [-v] [-x] [--y Y] [-z Z [Z ...]] foo bar baz
        '''
    help = usage + '''\

        DESCRIPTION

        positional arguments:
          foo            FOO HELP
          bar            BAR HELP

        optional arguments:
          -h, --help     show this help message oraz exit
          -v, --version  show program's version number oraz exit
          -x             X HELP
          --y Y          Y HELP

        GROUP TITLE:
          GROUP DESCRIPTION

          baz            BAZ HELP
          -z Z [Z ...]   Z HELP

        EPILOG
    '''
    version = '''\
        0.1
        '''


klasa TestHelpBiggerPositionals(HelpTestCase):
    """Make sure that help aligns when arguments are longer"""

    parser_signature = Sig(usage='USAGE', description='DESCRIPTION')
    argument_signatures = [
        Sig('-x', action='store_true', help='X HELP'),
        Sig('--y', help='Y HELP'),
        Sig('ekiekiekifekang', help='EKI HELP'),
        Sig('bar', help='BAR HELP'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: USAGE
        '''
    help = usage + '''\

        DESCRIPTION

        positional arguments:
          ekiekiekifekang  EKI HELP
          bar              BAR HELP

        optional arguments:
          -h, --help       show this help message oraz exit
          -x               X HELP
          --y Y            Y HELP
        '''

    version = ''


klasa TestHelpReformatting(HelpTestCase):
    """Make sure that text after short names starts on the first line"""

    parser_signature = Sig(
        prog='PROG',
        description='   oddly    formatted\n'
                    'description\n'
                    '\n'
                    'that jest so long that it should go onto multiple '
                    'lines when wrapped')
    argument_signatures = [
        Sig('-x', metavar='XX', help='oddly\n'
                                     '    formatted -x help'),
        Sig('y', metavar='yyy', help='normal y help'),
    ]
    argument_group_signatures = [
        (Sig('title', description='\n'
                                  '    oddly formatted group\n'
                                  '\n'
                                  'description'),
         [Sig('-a', action='store_true',
              help=' oddly \n'
                   'formatted    -a  help  \n'
                   '    again, so long that it should be wrapped over '
                   'multiple lines')]),
    ]
    usage = '''\
        usage: PROG [-h] [-x XX] [-a] yyy
        '''
    help = usage + '''\

        oddly formatted description that jest so long that it should go onto \
multiple
        lines when wrapped

        positional arguments:
          yyy         normal y help

        optional arguments:
          -h, --help  show this help message oraz exit
          -x XX       oddly formatted -x help

        title:
          oddly formatted group description

          -a          oddly formatted -a help again, so long that it should \
be wrapped
                      over multiple lines
        '''
    version = ''


klasa TestHelpWrappingShortNames(HelpTestCase):
    """Make sure that text after short names starts on the first line"""

    parser_signature = Sig(prog='PROG', description= 'D\nD' * 30)
    argument_signatures = [
        Sig('-x', metavar='XX', help='XHH HX' * 20),
        Sig('y', metavar='yyy', help='YH YH' * 20),
    ]
    argument_group_signatures = [
        (Sig('ALPHAS'), [
            Sig('-a', action='store_true', help='AHHH HHA' * 10)]),
    ]
    usage = '''\
        usage: PROG [-h] [-x XX] [-a] yyy
        '''
    help = usage + '''\

        D DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD \
DD DD DD
        DD DD DD DD D

        positional arguments:
          yyy         YH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH \
YHYH YHYH
                      YHYH YHYH YHYH YHYH YHYH YHYH YHYH YH

        optional arguments:
          -h, --help  show this help message oraz exit
          -x XX       XHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH \
HXXHH HXXHH
                      HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HX

        ALPHAS:
          -a          AHHH HHAAHHH HHAAHHH HHAAHHH HHAAHHH HHAAHHH HHAAHHH \
HHAAHHH
                      HHAAHHH HHAAHHH HHA
        '''
    version = ''


klasa TestHelpWrappingLongNames(HelpTestCase):
    """Make sure that text after long names starts on the next line"""

    parser_signature = Sig(usage='USAGE', description= 'D D' * 30)
    argument_signatures = [
        Sig('-v', '--version', action='version', version='V V' * 30),
        Sig('-x', metavar='X' * 25, help='XH XH' * 20),
        Sig('y', metavar='y' * 25, help='YH YH' * 20),
    ]
    argument_group_signatures = [
        (Sig('ALPHAS'), [
            Sig('-a', metavar='A' * 25, help='AH AH' * 20),
            Sig('z', metavar='z' * 25, help='ZH ZH' * 20)]),
    ]
    usage = '''\
        usage: USAGE
        '''
    help = usage + '''\

        D DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD \
DD DD DD
        DD DD DD DD D

        positional arguments:
          yyyyyyyyyyyyyyyyyyyyyyyyy
                                YH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH \
YHYH YHYH
                                YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YH

        optional arguments:
          -h, --help            show this help message oraz exit
          -v, --version         show program's version number oraz exit
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
                                XH XHXH XHXH XHXH XHXH XHXH XHXH XHXH XHXH \
XHXH XHXH
                                XHXH XHXH XHXH XHXH XHXH XHXH XHXH XHXH XHXH XH

        ALPHAS:
          -a AAAAAAAAAAAAAAAAAAAAAAAAA
                                AH AHAH AHAH AHAH AHAH AHAH AHAH AHAH AHAH \
AHAH AHAH
                                AHAH AHAH AHAH AHAH AHAH AHAH AHAH AHAH AHAH AH
          zzzzzzzzzzzzzzzzzzzzzzzzz
                                ZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH \
ZHZH ZHZH
                                ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZH
        '''
    version = '''\
        V VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV \
VV VV VV
        VV VV VV VV V
        '''


klasa TestHelpUsage(HelpTestCase):
    """Test basic usage messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-w', nargs='+', help='w'),
        Sig('-x', nargs='*', help='x'),
        Sig('a', help='a'),
        Sig('b', help='b', nargs=2),
        Sig('c', help='c', nargs='?'),
    ]
    argument_group_signatures = [
        (Sig('group'), [
            Sig('-y', nargs='?', help='y'),
            Sig('-z', nargs=3, help='z'),
            Sig('d', help='d', nargs='*'),
            Sig('e', help='e', nargs='+'),
        ])
    ]
    usage = '''\
        usage: PROG [-h] [-w W [W ...]] [-x [X [X ...]]] [-y [Y]] [-z Z Z Z]
                    a b b [c] [d [d ...]] e [e ...]
        '''
    help = usage + '''\

        positional arguments:
          a               a
          b               b
          c               c

        optional arguments:
          -h, --help      show this help message oraz exit
          -w W [W ...]    w
          -x [X [X ...]]  x

        group:
          -y [Y]          y
          -z Z Z Z        z
          d               d
          e               e
        '''
    version = ''


klasa TestHelpOnlyUserGroups(HelpTestCase):
    """Test basic usage messages"""

    parser_signature = Sig(prog='PROG', add_help=Nieprawda)
    argument_signatures = []
    argument_group_signatures = [
        (Sig('xxxx'), [
            Sig('-x', help='x'),
            Sig('a', help='a'),
        ]),
        (Sig('yyyy'), [
            Sig('b', help='b'),
            Sig('-y', help='y'),
        ]),
    ]
    usage = '''\
        usage: PROG [-x X] [-y Y] a b
        '''
    help = usage + '''\

        xxxx:
          -x X  x
          a     a

        yyyy:
          b     b
          -y Y  y
        '''
    version = ''


klasa TestHelpUsageLongProg(HelpTestCase):
    """Test usage messages where the prog jest long"""

    parser_signature = Sig(prog='P' * 60)
    argument_signatures = [
        Sig('-w', metavar='W'),
        Sig('-x', metavar='X'),
        Sig('a'),
        Sig('b'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
               [-h] [-w W] [-x X] a b
        '''
    help = usage + '''\

        positional arguments:
          a
          b

        optional arguments:
          -h, --help  show this help message oraz exit
          -w W
          -x X
        '''
    version = ''


klasa TestHelpUsageLongProgOptionsWrap(HelpTestCase):
    """Test usage messages where the prog jest long oraz the optionals wrap"""

    parser_signature = Sig(prog='P' * 60)
    argument_signatures = [
        Sig('-w', metavar='W' * 25),
        Sig('-x', metavar='X' * 25),
        Sig('-y', metavar='Y' * 25),
        Sig('-z', metavar='Z' * 25),
        Sig('a'),
        Sig('b'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
               [-h] [-w WWWWWWWWWWWWWWWWWWWWWWWWW] \
[-x XXXXXXXXXXXXXXXXXXXXXXXXX]
               [-y YYYYYYYYYYYYYYYYYYYYYYYYY] [-z ZZZZZZZZZZZZZZZZZZZZZZZZZ]
               a b
        '''
    help = usage + '''\

        positional arguments:
          a
          b

        optional arguments:
          -h, --help            show this help message oraz exit
          -w WWWWWWWWWWWWWWWWWWWWWWWWW
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


klasa TestHelpUsageLongProgPositionalsWrap(HelpTestCase):
    """Test usage messages where the prog jest long oraz the positionals wrap"""

    parser_signature = Sig(prog='P' * 60, add_help=Nieprawda)
    argument_signatures = [
        Sig('a' * 25),
        Sig('b' * 25),
        Sig('c' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
               aaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbb
               ccccccccccccccccccccccccc
        '''
    help = usage + '''\

        positional arguments:
          aaaaaaaaaaaaaaaaaaaaaaaaa
          bbbbbbbbbbbbbbbbbbbbbbbbb
          ccccccccccccccccccccccccc
        '''
    version = ''


klasa TestHelpUsageOptionalsWrap(HelpTestCase):
    """Test usage messages where the optionals wrap"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-w', metavar='W' * 25),
        Sig('-x', metavar='X' * 25),
        Sig('-y', metavar='Y' * 25),
        Sig('-z', metavar='Z' * 25),
        Sig('a'),
        Sig('b'),
        Sig('c'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-w WWWWWWWWWWWWWWWWWWWWWWWWW] \
[-x XXXXXXXXXXXXXXXXXXXXXXXXX]
                    [-y YYYYYYYYYYYYYYYYYYYYYYYYY] \
[-z ZZZZZZZZZZZZZZZZZZZZZZZZZ]
                    a b c
        '''
    help = usage + '''\

        positional arguments:
          a
          b
          c

        optional arguments:
          -h, --help            show this help message oraz exit
          -w WWWWWWWWWWWWWWWWWWWWWWWWW
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


klasa TestHelpUsagePositionalsWrap(HelpTestCase):
    """Test usage messages where the positionals wrap"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-x'),
        Sig('-y'),
        Sig('-z'),
        Sig('a' * 25),
        Sig('b' * 25),
        Sig('c' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-x X] [-y Y] [-z Z]
                    aaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbb
                    ccccccccccccccccccccccccc
        '''
    help = usage + '''\

        positional arguments:
          aaaaaaaaaaaaaaaaaaaaaaaaa
          bbbbbbbbbbbbbbbbbbbbbbbbb
          ccccccccccccccccccccccccc

        optional arguments:
          -h, --help            show this help message oraz exit
          -x X
          -y Y
          -z Z
        '''
    version = ''


klasa TestHelpUsageOptionalsPositionalsWrap(HelpTestCase):
    """Test usage messages where the optionals oraz positionals wrap"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-x', metavar='X' * 25),
        Sig('-y', metavar='Y' * 25),
        Sig('-z', metavar='Z' * 25),
        Sig('a' * 25),
        Sig('b' * 25),
        Sig('c' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-x XXXXXXXXXXXXXXXXXXXXXXXXX] \
[-y YYYYYYYYYYYYYYYYYYYYYYYYY]
                    [-z ZZZZZZZZZZZZZZZZZZZZZZZZZ]
                    aaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbb
                    ccccccccccccccccccccccccc
        '''
    help = usage + '''\

        positional arguments:
          aaaaaaaaaaaaaaaaaaaaaaaaa
          bbbbbbbbbbbbbbbbbbbbbbbbb
          ccccccccccccccccccccccccc

        optional arguments:
          -h, --help            show this help message oraz exit
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


klasa TestHelpUsageOptionalsOnlyWrap(HelpTestCase):
    """Test usage messages where there are only optionals oraz they wrap"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-x', metavar='X' * 25),
        Sig('-y', metavar='Y' * 25),
        Sig('-z', metavar='Z' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-x XXXXXXXXXXXXXXXXXXXXXXXXX] \
[-y YYYYYYYYYYYYYYYYYYYYYYYYY]
                    [-z ZZZZZZZZZZZZZZZZZZZZZZZZZ]
        '''
    help = usage + '''\

        optional arguments:
          -h, --help            show this help message oraz exit
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


klasa TestHelpUsagePositionalsOnlyWrap(HelpTestCase):
    """Test usage messages where there are only positionals oraz they wrap"""

    parser_signature = Sig(prog='PROG', add_help=Nieprawda)
    argument_signatures = [
        Sig('a' * 25),
        Sig('b' * 25),
        Sig('c' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG aaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbb
                    ccccccccccccccccccccccccc
        '''
    help = usage + '''\

        positional arguments:
          aaaaaaaaaaaaaaaaaaaaaaaaa
          bbbbbbbbbbbbbbbbbbbbbbbbb
          ccccccccccccccccccccccccc
        '''
    version = ''


klasa TestHelpVariableExpansion(HelpTestCase):
    """Test that variables are expanded properly w help messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-x', type=int,
            help='x %(prog)s %(default)s %(type)s %%'),
        Sig('-y', action='store_const', default=42, const='XXX',
            help='y %(prog)s %(default)s %(const)s'),
        Sig('--foo', choices='abc',
            help='foo %(prog)s %(default)s %(choices)s'),
        Sig('--bar', default='baz', choices=[1, 2], metavar='BBB',
            help='bar %(prog)s %(default)s %(dest)s'),
        Sig('spam', help='spam %(prog)s %(default)s'),
        Sig('badger', default=0.5, help='badger %(prog)s %(default)s'),
    ]
    argument_group_signatures = [
        (Sig('group'), [
            Sig('-a', help='a %(prog)s %(default)s'),
            Sig('-b', default=-1, help='b %(prog)s %(default)s'),
        ])
    ]
    usage = ('''\
        usage: PROG [-h] [-x X] [-y] [--foo {a,b,c}] [--bar BBB] [-a A] [-b B]
                    spam badger
        ''')
    help = usage + '''\

        positional arguments:
          spam           spam PROG Nic
          badger         badger PROG 0.5

        optional arguments:
          -h, --help     show this help message oraz exit
          -x X           x PROG Nic int %
          -y             y PROG 42 XXX
          --foo {a,b,c}  foo PROG Nic a, b, c
          --bar BBB      bar PROG baz bar

        group:
          -a A           a PROG Nic
          -b B           b PROG -1
        '''
    version = ''


klasa TestHelpVariableExpansionUsageSupplied(HelpTestCase):
    """Test that variables are expanded properly when usage= jest present"""

    parser_signature = Sig(prog='PROG', usage='%(prog)s FOO')
    argument_signatures = []
    argument_group_signatures = []
    usage = ('''\
        usage: PROG FOO
        ''')
    help = usage + '''\

        optional arguments:
          -h, --help  show this help message oraz exit
        '''
    version = ''


klasa TestHelpVariableExpansionNoArguments(HelpTestCase):
    """Test that variables are expanded properly przy no arguments"""

    parser_signature = Sig(prog='PROG', add_help=Nieprawda)
    argument_signatures = []
    argument_group_signatures = []
    usage = ('''\
        usage: PROG
        ''')
    help = usage
    version = ''


klasa TestHelpSuppressUsage(HelpTestCase):
    """Test that items can be suppressed w usage messages"""

    parser_signature = Sig(prog='PROG', usage=argparse.SUPPRESS)
    argument_signatures = [
        Sig('--foo', help='foo help'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = []
    help = '''\
        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message oraz exit
          --foo FOO   foo help
        '''
    usage = ''
    version = ''


klasa TestHelpSuppressOptional(HelpTestCase):
    """Test that optional arguments can be suppressed w help messages"""

    parser_signature = Sig(prog='PROG', add_help=Nieprawda)
    argument_signatures = [
        Sig('--foo', help=argparse.SUPPRESS),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG spam
        '''
    help = usage + '''\

        positional arguments:
          spam  spam help
        '''
    version = ''


klasa TestHelpSuppressOptionalGroup(HelpTestCase):
    """Test that optional groups can be suppressed w help messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('--foo', help='foo help'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = [
        (Sig('group'), [Sig('--bar', help=argparse.SUPPRESS)]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] spam
        '''
    help = usage + '''\

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message oraz exit
          --foo FOO   foo help
        '''
    version = ''


klasa TestHelpSuppressPositional(HelpTestCase):
    """Test that positional arguments can be suppressed w help messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('--foo', help='foo help'),
        Sig('spam', help=argparse.SUPPRESS),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [--foo FOO]
        '''
    help = usage + '''\

        optional arguments:
          -h, --help  show this help message oraz exit
          --foo FOO   foo help
        '''
    version = ''


klasa TestHelpRequiredOptional(HelpTestCase):
    """Test that required options don't look optional"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('--foo', required=Prawda, help='foo help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] --foo FOO
        '''
    help = usage + '''\

        optional arguments:
          -h, --help  show this help message oraz exit
          --foo FOO   foo help
        '''
    version = ''


klasa TestHelpAlternatePrefixChars(HelpTestCase):
    """Test that options display przy different prefix characters"""

    parser_signature = Sig(prog='PROG', prefix_chars='^;', add_help=Nieprawda)
    argument_signatures = [
        Sig('^^foo', action='store_true', help='foo help'),
        Sig(';b', ';;bar', help='bar help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [^^foo] [;b BAR]
        '''
    help = usage + '''\

        optional arguments:
          ^^foo              foo help
          ;b BAR, ;;bar BAR  bar help
        '''
    version = ''


klasa TestHelpNoHelpOptional(HelpTestCase):
    """Test that the --help argument can be suppressed help messages"""

    parser_signature = Sig(prog='PROG', add_help=Nieprawda)
    argument_signatures = [
        Sig('--foo', help='foo help'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [--foo FOO] spam
        '''
    help = usage + '''\

        positional arguments:
          spam       spam help

        optional arguments:
          --foo FOO  foo help
        '''
    version = ''


klasa TestHelpNic(HelpTestCase):
    """Test that no errors occur jeżeli no help jest specified"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('--foo'),
        Sig('spam'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [--foo FOO] spam
        '''
    help = usage + '''\

        positional arguments:
          spam

        optional arguments:
          -h, --help  show this help message oraz exit
          --foo FOO
        '''
    version = ''


klasa TestHelpTupleMetavar(HelpTestCase):
    """Test specifying metavar jako a tuple"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-w', help='w', nargs='+', metavar=('W1', 'W2')),
        Sig('-x', help='x', nargs='*', metavar=('X1', 'X2')),
        Sig('-y', help='y', nargs=3, metavar=('Y1', 'Y2', 'Y3')),
        Sig('-z', help='z', nargs='?', metavar=('Z1', )),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-w W1 [W2 ...]] [-x [X1 [X2 ...]]] [-y Y1 Y2 Y3] \
[-z [Z1]]
        '''
    help = usage + '''\

        optional arguments:
          -h, --help        show this help message oraz exit
          -w W1 [W2 ...]    w
          -x [X1 [X2 ...]]  x
          -y Y1 Y2 Y3       y
          -z [Z1]           z
        '''
    version = ''


klasa TestHelpRawText(HelpTestCase):
    """Test the RawTextHelpFormatter"""

    parser_signature = Sig(
        prog='PROG', formatter_class=argparse.RawTextHelpFormatter,
        description='Keep the formatting\n'
                    '    exactly jako it jest written\n'
                    '\n'
                    'here\n')

    argument_signatures = [
        Sig('--foo', help='    foo help should also\n'
                          'appear jako given here'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = [
        (Sig('title', description='    This text\n'
                                  '  should be indented\n'
                                  '    exactly like it jest here\n'),
         [Sig('--bar', help='bar help')]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] [--bar BAR] spam
        '''
    help = usage + '''\

        Keep the formatting
            exactly jako it jest written

        here

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message oraz exit
          --foo FOO       foo help should also
                      appear jako given here

        title:
              This text
            should be indented
              exactly like it jest here

          --bar BAR   bar help
        '''
    version = ''


klasa TestHelpRawDescription(HelpTestCase):
    """Test the RawTextHelpFormatter"""

    parser_signature = Sig(
        prog='PROG', formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Keep the formatting\n'
                    '    exactly jako it jest written\n'
                    '\n'
                    'here\n')

    argument_signatures = [
        Sig('--foo', help='  foo help should not\n'
                          '    retain this odd formatting'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = [
        (Sig('title', description='    This text\n'
                                  '  should be indented\n'
                                  '    exactly like it jest here\n'),
         [Sig('--bar', help='bar help')]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] [--bar BAR] spam
        '''
    help = usage + '''\

        Keep the formatting
            exactly jako it jest written

        here

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message oraz exit
          --foo FOO   foo help should nie retain this odd formatting

        title:
              This text
            should be indented
              exactly like it jest here

          --bar BAR   bar help
        '''
    version = ''


klasa TestHelpArgumentDefaults(HelpTestCase):
    """Test the ArgumentDefaultsHelpFormatter"""

    parser_signature = Sig(
        prog='PROG', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='description')

    argument_signatures = [
        Sig('--foo', help='foo help - oh oraz by the way, %(default)s'),
        Sig('--bar', action='store_true', help='bar help'),
        Sig('spam', help='spam help'),
        Sig('badger', nargs='?', default='wooden', help='badger help'),
    ]
    argument_group_signatures = [
        (Sig('title', description='description'),
         [Sig('--baz', type=int, default=42, help='baz help')]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] [--bar] [--baz BAZ] spam [badger]
        '''
    help = usage + '''\

        description

        positional arguments:
          spam        spam help
          badger      badger help (default: wooden)

        optional arguments:
          -h, --help  show this help message oraz exit
          --foo FOO   foo help - oh oraz by the way, Nic
          --bar       bar help (default: Nieprawda)

        title:
          description

          --baz BAZ   baz help (default: 42)
        '''
    version = ''

klasa TestHelpVersionAction(HelpTestCase):
    """Test the default help dla the version action"""

    parser_signature = Sig(prog='PROG', description='description')
    argument_signatures = [Sig('-V', '--version', action='version', version='3.6')]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-V]
        '''
    help = usage + '''\

        description

        optional arguments:
          -h, --help     show this help message oraz exit
          -V, --version  show program's version number oraz exit
        '''
    version = ''


klasa TestHelpVersionActionSuppress(HelpTestCase):
    """Test that the --version argument can be suppressed w help messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-v', '--version', action='version', version='1.0',
            help=argparse.SUPPRESS),
        Sig('--foo', help='foo help'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [--foo FOO] spam
        '''
    help = usage + '''\

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message oraz exit
          --foo FOO   foo help
        '''


klasa TestHelpSubparsersOrdering(HelpTestCase):
    """Test ordering of subcommands w help matches the code"""
    parser_signature = Sig(prog='PROG',
                           description='display some subcommands')
    argument_signatures = [Sig('-v', '--version', action='version', version='0.1')]

    subparsers_signatures = [Sig(name=name)
                             dla name w ('a', 'b', 'c', 'd', 'e')]

    usage = '''\
        usage: PROG [-h] [-v] {a,b,c,d,e} ...
        '''

    help = usage + '''\

        display some subcommands

        positional arguments:
          {a,b,c,d,e}

        optional arguments:
          -h, --help     show this help message oraz exit
          -v, --version  show program's version number oraz exit
        '''

    version = '''\
        0.1
        '''

klasa TestHelpSubparsersWithHelpOrdering(HelpTestCase):
    """Test ordering of subcommands w help matches the code"""
    parser_signature = Sig(prog='PROG',
                           description='display some subcommands')
    argument_signatures = [Sig('-v', '--version', action='version', version='0.1')]

    subcommand_data = (('a', 'a subcommand help'),
                       ('b', 'b subcommand help'),
                       ('c', 'c subcommand help'),
                       ('d', 'd subcommand help'),
                       ('e', 'e subcommand help'),
                       )

    subparsers_signatures = [Sig(name=name, help=help)
                             dla name, help w subcommand_data]

    usage = '''\
        usage: PROG [-h] [-v] {a,b,c,d,e} ...
        '''

    help = usage + '''\

        display some subcommands

        positional arguments:
          {a,b,c,d,e}
            a            a subcommand help
            b            b subcommand help
            c            c subcommand help
            d            d subcommand help
            e            e subcommand help

        optional arguments:
          -h, --help     show this help message oraz exit
          -v, --version  show program's version number oraz exit
        '''

    version = '''\
        0.1
        '''



klasa TestHelpMetavarTypeFormatter(HelpTestCase):
    """"""

    def custom_type(string):
        zwróć string

    parser_signature = Sig(prog='PROG', description='description',
                           formatter_class=argparse.MetavarTypeHelpFormatter)
    argument_signatures = [Sig('a', type=int),
                           Sig('-b', type=custom_type),
                           Sig('-c', type=float, metavar='SOME FLOAT')]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-b custom_type] [-c SOME FLOAT] int
        '''
    help = usage + '''\

        description

        positional arguments:
          int

        optional arguments:
          -h, --help      show this help message oraz exit
          -b custom_type
          -c SOME FLOAT
        '''
    version = ''


# =====================================
# Optional/Positional constructor tests
# =====================================

klasa TestInvalidArgumentConstructors(TestCase):
    """Test a bunch of invalid Argument constructors"""

    def assertTypeError(self, *args, **kwargs):
        parser = argparse.ArgumentParser()
        self.assertRaises(TypeError, parser.add_argument,
                          *args, **kwargs)

    def assertValueError(self, *args, **kwargs):
        parser = argparse.ArgumentParser()
        self.assertRaises(ValueError, parser.add_argument,
                          *args, **kwargs)

    def test_invalid_keyword_arguments(self):
        self.assertTypeError('-x', bar=Nic)
        self.assertTypeError('-y', callback='foo')
        self.assertTypeError('-y', callback_args=())
        self.assertTypeError('-y', callback_kwargs={})

    def test_missing_destination(self):
        self.assertTypeError()
        dla action w ['append', 'store']:
            self.assertTypeError(action=action)

    def test_invalid_option_strings(self):
        self.assertValueError('--')
        self.assertValueError('---')

    def test_invalid_type(self):
        self.assertValueError('--foo', type='int')
        self.assertValueError('--foo', type=(int, float))

    def test_invalid_action(self):
        self.assertValueError('-x', action='foo')
        self.assertValueError('foo', action='baz')
        self.assertValueError('--foo', action=('store', 'append'))
        parser = argparse.ArgumentParser()
        przy self.assertRaises(ValueError) jako cm:
            parser.add_argument("--foo", action="store-true")
        self.assertIn('unknown action', str(cm.exception))

    def test_multiple_dest(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(dest='foo')
        przy self.assertRaises(ValueError) jako cm:
            parser.add_argument('bar', dest='baz')
        self.assertIn('dest supplied twice dla positional argument',
                      str(cm.exception))

    def test_no_argument_actions(self):
        dla action w ['store_const', 'store_true', 'store_false',
                       'append_const', 'count']:
            dla attrs w [dict(type=int), dict(nargs='+'),
                          dict(choices='ab')]:
                self.assertTypeError('-x', action=action, **attrs)

    def test_no_argument_no_const_actions(self):
        # options przy zero arguments
        dla action w ['store_true', 'store_false', 'count']:

            # const jest always disallowed
            self.assertTypeError('-x', const='foo', action=action)

            # nargs jest always disallowed
            self.assertTypeError('-x', nargs='*', action=action)

    def test_more_than_one_argument_actions(self):
        dla action w ['store', 'append']:

            # nargs=0 jest disallowed
            self.assertValueError('-x', nargs=0, action=action)
            self.assertValueError('spam', nargs=0, action=action)

            # const jest disallowed przy non-optional arguments
            dla nargs w [1, '*', '+']:
                self.assertValueError('-x', const='foo',
                                      nargs=nargs, action=action)
                self.assertValueError('spam', const='foo',
                                      nargs=nargs, action=action)

    def test_required_const_actions(self):
        dla action w ['store_const', 'append_const']:

            # nargs jest always disallowed
            self.assertTypeError('-x', nargs='+', action=action)

    def test_parsers_action_missing_params(self):
        self.assertTypeError('command', action='parsers')
        self.assertTypeError('command', action='parsers', prog='PROG')
        self.assertTypeError('command', action='parsers',
                             parser_class=argparse.ArgumentParser)

    def test_required_positional(self):
        self.assertTypeError('foo', required=Prawda)

    def test_user_defined_action(self):

        klasa Success(Exception):
            dalej

        klasa Action(object):

            def __init__(self,
                         option_strings,
                         dest,
                         const,
                         default,
                         required=Nieprawda):
                jeżeli dest == 'spam':
                    jeżeli const jest Success:
                        jeżeli default jest Success:
                            podnieś Success()

            def __call__(self, *args, **kwargs):
                dalej

        parser = argparse.ArgumentParser()
        self.assertRaises(Success, parser.add_argument, '--spam',
                          action=Action, default=Success, const=Success)
        self.assertRaises(Success, parser.add_argument, 'spam',
                          action=Action, default=Success, const=Success)

# ================================
# Actions returned by add_argument
# ================================

klasa TestActionsReturned(TestCase):

    def test_dest(self):
        parser = argparse.ArgumentParser()
        action = parser.add_argument('--foo')
        self.assertEqual(action.dest, 'foo')
        action = parser.add_argument('-b', '--bar')
        self.assertEqual(action.dest, 'bar')
        action = parser.add_argument('-x', '-y')
        self.assertEqual(action.dest, 'x')

    def test_misc(self):
        parser = argparse.ArgumentParser()
        action = parser.add_argument('--foo', nargs='?', const=42,
                                     default=84, type=int, choices=[1, 2],
                                     help='FOO', metavar='BAR', dest='baz')
        self.assertEqual(action.nargs, '?')
        self.assertEqual(action.const, 42)
        self.assertEqual(action.default, 84)
        self.assertEqual(action.type, int)
        self.assertEqual(action.choices, [1, 2])
        self.assertEqual(action.help, 'FOO')
        self.assertEqual(action.metavar, 'BAR')
        self.assertEqual(action.dest, 'baz')


# ================================
# Argument conflict handling tests
# ================================

klasa TestConflictHandling(TestCase):

    def test_bad_type(self):
        self.assertRaises(ValueError, argparse.ArgumentParser,
                          conflict_handler='foo')

    def test_conflict_error(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-x')
        self.assertRaises(argparse.ArgumentError,
                          parser.add_argument, '-x')
        parser.add_argument('--spam')
        self.assertRaises(argparse.ArgumentError,
                          parser.add_argument, '--spam')

    def test_resolve_error(self):
        get_parser = argparse.ArgumentParser
        parser = get_parser(prog='PROG', conflict_handler='resolve')

        parser.add_argument('-x', help='OLD X')
        parser.add_argument('-x', help='NEW X')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [-x X]

            optional arguments:
              -h, --help  show this help message oraz exit
              -x X        NEW X
            '''))

        parser.add_argument('--spam', metavar='OLD_SPAM')
        parser.add_argument('--spam', metavar='NEW_SPAM')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [-x X] [--spam NEW_SPAM]

            optional arguments:
              -h, --help       show this help message oraz exit
              -x X             NEW X
              --spam NEW_SPAM
            '''))


# =============================
# Help oraz Version option tests
# =============================

klasa TestOptionalsHelpVersionActions(TestCase):
    """Test the help oraz version actions"""

    def assertPrintHelpExit(self, parser, args_str):
        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args(args_str.split())
        self.assertEqual(parser.format_help(), cm.exception.stdout)

    def assertArgumentParserError(self, parser, *args):
        self.assertRaises(ArgumentParserError, parser.parse_args, args)

    def test_version(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('-v', '--version', action='version', version='1.0')
        self.assertPrintHelpExit(parser, '-h')
        self.assertPrintHelpExit(parser, '--help')
        self.assertRaises(AttributeError, getattr, parser, 'format_version')

    def test_version_format(self):
        parser = ErrorRaisingArgumentParser(prog='PPP')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s 3.5')
        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args(['-v'])
        self.assertEqual('PPP 3.5\n', cm.exception.stdout)

    def test_version_no_help(self):
        parser = ErrorRaisingArgumentParser(add_help=Nieprawda)
        parser.add_argument('-v', '--version', action='version', version='1.0')
        self.assertArgumentParserError(parser, '-h')
        self.assertArgumentParserError(parser, '--help')
        self.assertRaises(AttributeError, getattr, parser, 'format_version')

    def test_version_action(self):
        parser = ErrorRaisingArgumentParser(prog='XXX')
        parser.add_argument('-V', action='version', version='%(prog)s 3.7')
        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args(['-V'])
        self.assertEqual('XXX 3.7\n', cm.exception.stdout)

    def test_no_help(self):
        parser = ErrorRaisingArgumentParser(add_help=Nieprawda)
        self.assertArgumentParserError(parser, '-h')
        self.assertArgumentParserError(parser, '--help')
        self.assertArgumentParserError(parser, '-v')
        self.assertArgumentParserError(parser, '--version')

    def test_alternate_help_version(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('-x', action='help')
        parser.add_argument('-y', action='version')
        self.assertPrintHelpExit(parser, '-x')
        self.assertArgumentParserError(parser, '-v')
        self.assertArgumentParserError(parser, '--version')
        self.assertRaises(AttributeError, getattr, parser, 'format_version')

    def test_help_version_extra_arguments(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('--version', action='version', version='1.0')
        parser.add_argument('-x', action='store_true')
        parser.add_argument('y')

        # try all combinations of valid prefixes oraz suffixes
        valid_prefixes = ['', '-x', 'foo', '-x bar', 'baz -x']
        valid_suffixes = valid_prefixes + ['--bad-option', 'foo bar baz']
        dla prefix w valid_prefixes:
            dla suffix w valid_suffixes:
                format = '%s %%s %s' % (prefix, suffix)
            self.assertPrintHelpExit(parser, format % '-h')
            self.assertPrintHelpExit(parser, format % '--help')
            self.assertRaises(AttributeError, getattr, parser, 'format_version')


# ======================
# str() oraz repr() tests
# ======================

klasa TestStrings(TestCase):
    """Test str()  oraz repr() on Optionals oraz Positionals"""

    def assertStringEqual(self, obj, result_string):
        dla func w [str, repr]:
            self.assertEqual(func(obj), result_string)

    def test_optional(self):
        option = argparse.Action(
            option_strings=['--foo', '-a', '-b'],
            dest='b',
            type='int',
            nargs='+',
            default=42,
            choices=[1, 2, 3],
            help='HELP',
            metavar='METAVAR')
        string = (
            "Action(option_strings=['--foo', '-a', '-b'], dest='b', "
            "nargs='+', const=Nic, default=42, type='int', "
            "choices=[1, 2, 3], help='HELP', metavar='METAVAR')")
        self.assertStringEqual(option, string)

    def test_argument(self):
        argument = argparse.Action(
            option_strings=[],
            dest='x',
            type=float,
            nargs='?',
            default=2.5,
            choices=[0.5, 1.5, 2.5],
            help='H HH H',
            metavar='MV MV MV')
        string = (
            "Action(option_strings=[], dest='x', nargs='?', "
            "const=Nic, default=2.5, type=%r, choices=[0.5, 1.5, 2.5], "
            "help='H HH H', metavar='MV MV MV')" % float)
        self.assertStringEqual(argument, string)

    def test_namespace(self):
        ns = argparse.Namespace(foo=42, bar='spam')
        string = "Namespace(bar='spam', foo=42)"
        self.assertStringEqual(ns, string)

    def test_parser(self):
        parser = argparse.ArgumentParser(prog='PROG')
        string = (
            "ArgumentParser(prog='PROG', usage=Nic, description=Nic, "
            "formatter_class=%r, conflict_handler='error', "
            "add_help=Prawda)" % argparse.HelpFormatter)
        self.assertStringEqual(parser, string)

# ===============
# Namespace tests
# ===============

klasa TestNamespace(TestCase):

    def test_constructor(self):
        ns = argparse.Namespace()
        self.assertRaises(AttributeError, getattr, ns, 'x')

        ns = argparse.Namespace(a=42, b='spam')
        self.assertEqual(ns.a, 42)
        self.assertEqual(ns.b, 'spam')

    def test_equality(self):
        ns1 = argparse.Namespace(a=1, b=2)
        ns2 = argparse.Namespace(b=2, a=1)
        ns3 = argparse.Namespace(a=1)
        ns4 = argparse.Namespace(b=2)

        self.assertEqual(ns1, ns2)
        self.assertNotEqual(ns1, ns3)
        self.assertNotEqual(ns1, ns4)
        self.assertNotEqual(ns2, ns3)
        self.assertNotEqual(ns2, ns4)
        self.assertPrawda(ns1 != ns3)
        self.assertPrawda(ns1 != ns4)
        self.assertPrawda(ns2 != ns3)
        self.assertPrawda(ns2 != ns4)

    def test_equality_returns_notimplemeted(self):
        # See issue 21481
        ns = argparse.Namespace(a=1, b=2)
        self.assertIs(ns.__eq__(Nic), NotImplemented)
        self.assertIs(ns.__ne__(Nic), NotImplemented)


# ===================
# File encoding tests
# ===================

klasa TestEncoding(TestCase):

    def _test_module_encoding(self, path):
        path, _ = os.path.splitext(path)
        path += ".py"
        przy codecs.open(path, 'r', 'utf-8') jako f:
            f.read()

    def test_argparse_module_encoding(self):
        self._test_module_encoding(argparse.__file__)

    def test_test_argparse_module_encoding(self):
        self._test_module_encoding(__file__)

# ===================
# ArgumentError tests
# ===================

klasa TestArgumentError(TestCase):

    def test_argument_error(self):
        msg = "my error here"
        error = argparse.ArgumentError(Nic, msg)
        self.assertEqual(str(error), msg)

# =======================
# ArgumentTypeError tests
# =======================

klasa TestArgumentTypeError(TestCase):

    def test_argument_type_error(self):

        def spam(string):
            podnieś argparse.ArgumentTypeError('spam!')

        parser = ErrorRaisingArgumentParser(prog='PROG', add_help=Nieprawda)
        parser.add_argument('x', type=spam)
        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args(['XXX'])
        self.assertEqual('usage: PROG x\nPROG: error: argument x: spam!\n',
                         cm.exception.stderr)

# =========================
# MessageContentError tests
# =========================

klasa TestMessageContentError(TestCase):

    def test_missing_argument_name_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos', type=str)
        parser.add_argument('-req_opt', type=int, required=Prawda)
        parser.add_argument('need_one', type=str, nargs='+')

        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')
        self.assertRegex(msg, 'need_one')
        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args(['myXargument'])
        msg = str(cm.exception)
        self.assertNotIn(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')
        self.assertRegex(msg, 'need_one')
        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args(['myXargument', '-req_opt=1'])
        msg = str(cm.exception)
        self.assertNotIn(msg, 'req_pos')
        self.assertNotIn(msg, 'req_opt')
        self.assertRegex(msg, 'need_one')

    def test_optional_optional_not_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos', type=str)
        parser.add_argument('--req_opt', type=int, required=Prawda)
        parser.add_argument('--opt_opt', type=bool, nargs='?',
                            default=Prawda)
        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')
        self.assertNotIn(msg, 'opt_opt')
        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args(['--req_opt=1'])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertNotIn(msg, 'req_opt')
        self.assertNotIn(msg, 'opt_opt')

    def test_optional_positional_not_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos')
        parser.add_argument('optional_positional', nargs='?', default='eggs')
        przy self.assertRaises(ArgumentParserError) jako cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertNotIn(msg, 'optional_positional')


# ================================================
# Check that the type function jest called only once
# ================================================

klasa TestTypeFunctionCallOnlyOnce(TestCase):

    def test_type_function_call_only_once(self):
        def spam(string_to_convert):
            self.assertEqual(string_to_convert, 'spam!')
            zwróć 'foo_converted'

        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', type=spam, default='bar')
        args = parser.parse_args('--foo spam!'.split())
        self.assertEqual(NS(foo='foo_converted'), args)

# ==================================================================
# Check semantics regarding the default argument oraz type conversion
# ==================================================================

klasa TestTypeFunctionCalledOnDefault(TestCase):

    def test_type_function_call_with_non_string_default(self):
        def spam(int_to_convert):
            self.assertEqual(int_to_convert, 0)
            zwróć 'foo_converted'

        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', type=spam, default=0)
        args = parser.parse_args([])
        # foo should *not* be converted because its default jest nie a string.
        self.assertEqual(NS(foo=0), args)

    def test_type_function_call_with_string_default(self):
        def spam(int_to_convert):
            zwróć 'foo_converted'

        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', type=spam, default='0')
        args = parser.parse_args([])
        # foo jest converted because its default jest a string.
        self.assertEqual(NS(foo='foo_converted'), args)

    def test_no_double_type_conversion_of_default(self):
        def extend(str_to_convert):
            zwróć str_to_convert + '*'

        parser = argparse.ArgumentParser()
        parser.add_argument('--test', type=extend, default='*')
        args = parser.parse_args([])
        # The test argument will be two stars, one coming z the default
        # value oraz one coming z the type conversion being called exactly
        # once.
        self.assertEqual(NS(test='**'), args)

    def test_issue_15906(self):
        # Issue #15906: When action='append', type=str, default=[] are
        # providing, the dest value was the string representation "[]" when it
        # should have been an empty list.
        parser = argparse.ArgumentParser()
        parser.add_argument('--test', dest='test', type=str,
                            default=[], action='append')
        args = parser.parse_args([])
        self.assertEqual(args.test, [])

# ======================
# parse_known_args tests
# ======================

klasa TestParseKnownArgs(TestCase):

    def test_arguments_tuple(self):
        parser = argparse.ArgumentParser()
        parser.parse_args(())

    def test_arguments_list(self):
        parser = argparse.ArgumentParser()
        parser.parse_args([])

    def test_arguments_tuple_positional(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('x')
        parser.parse_args(('x',))

    def test_arguments_list_positional(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('x')
        parser.parse_args(['x'])

    def test_optionals(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--foo')
        args, extras = parser.parse_known_args('--foo F --bar --baz'.split())
        self.assertEqual(NS(foo='F'), args)
        self.assertEqual(['--bar', '--baz'], extras)

    def test_mixed(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', nargs='?', const=1, type=int)
        parser.add_argument('--spam', action='store_false')
        parser.add_argument('badger')

        argv = ["B", "C", "--foo", "-v", "3", "4"]
        args, extras = parser.parse_known_args(argv)
        self.assertEqual(NS(v=3, spam=Prawda, badger="B"), args)
        self.assertEqual(["C", "--foo", "4"], extras)

# ==========================
# add_argument metavar tests
# ==========================

klasa TestAddArgumentMetavar(TestCase):

    EXPECTED_MESSAGE = "length of metavar tuple does nie match nargs"

    def do_test_no_exception(self, nargs, metavar):
        parser = argparse.ArgumentParser()
        parser.add_argument("--foo", nargs=nargs, metavar=metavar)

    def do_test_exception(self, nargs, metavar):
        parser = argparse.ArgumentParser()
        przy self.assertRaises(ValueError) jako cm:
            parser.add_argument("--foo", nargs=nargs, metavar=metavar)
        self.assertEqual(cm.exception.args[0], self.EXPECTED_MESSAGE)

    # Unit tests dla different values of metavar when nargs=Nic

    def test_nargs_Nic_metavar_string(self):
        self.do_test_no_exception(nargs=Nic, metavar="1")

    def test_nargs_Nic_metavar_length0(self):
        self.do_test_exception(nargs=Nic, metavar=tuple())

    def test_nargs_Nic_metavar_length1(self):
        self.do_test_no_exception(nargs=Nic, metavar=("1"))

    def test_nargs_Nic_metavar_length2(self):
        self.do_test_exception(nargs=Nic, metavar=("1", "2"))

    def test_nargs_Nic_metavar_length3(self):
        self.do_test_exception(nargs=Nic, metavar=("1", "2", "3"))

    # Unit tests dla different values of metavar when nargs=?

    def test_nargs_optional_metavar_string(self):
        self.do_test_no_exception(nargs="?", metavar="1")

    def test_nargs_optional_metavar_length0(self):
        self.do_test_exception(nargs="?", metavar=tuple())

    def test_nargs_optional_metavar_length1(self):
        self.do_test_no_exception(nargs="?", metavar=("1"))

    def test_nargs_optional_metavar_length2(self):
        self.do_test_exception(nargs="?", metavar=("1", "2"))

    def test_nargs_optional_metavar_length3(self):
        self.do_test_exception(nargs="?", metavar=("1", "2", "3"))

    # Unit tests dla different values of metavar when nargs=*

    def test_nargs_zeroormore_metavar_string(self):
        self.do_test_no_exception(nargs="*", metavar="1")

    def test_nargs_zeroormore_metavar_length0(self):
        self.do_test_exception(nargs="*", metavar=tuple())

    def test_nargs_zeroormore_metavar_length1(self):
        self.do_test_no_exception(nargs="*", metavar=("1"))

    def test_nargs_zeroormore_metavar_length2(self):
        self.do_test_no_exception(nargs="*", metavar=("1", "2"))

    def test_nargs_zeroormore_metavar_length3(self):
        self.do_test_exception(nargs="*", metavar=("1", "2", "3"))

    # Unit tests dla different values of metavar when nargs=+

    def test_nargs_oneormore_metavar_string(self):
        self.do_test_no_exception(nargs="+", metavar="1")

    def test_nargs_oneormore_metavar_length0(self):
        self.do_test_exception(nargs="+", metavar=tuple())

    def test_nargs_oneormore_metavar_length1(self):
        self.do_test_no_exception(nargs="+", metavar=("1"))

    def test_nargs_oneormore_metavar_length2(self):
        self.do_test_no_exception(nargs="+", metavar=("1", "2"))

    def test_nargs_oneormore_metavar_length3(self):
        self.do_test_exception(nargs="+", metavar=("1", "2", "3"))

    # Unit tests dla different values of metavar when nargs=...

    def test_nargs_remainder_metavar_string(self):
        self.do_test_no_exception(nargs="...", metavar="1")

    def test_nargs_remainder_metavar_length0(self):
        self.do_test_no_exception(nargs="...", metavar=tuple())

    def test_nargs_remainder_metavar_length1(self):
        self.do_test_no_exception(nargs="...", metavar=("1"))

    def test_nargs_remainder_metavar_length2(self):
        self.do_test_no_exception(nargs="...", metavar=("1", "2"))

    def test_nargs_remainder_metavar_length3(self):
        self.do_test_no_exception(nargs="...", metavar=("1", "2", "3"))

    # Unit tests dla different values of metavar when nargs=A...

    def test_nargs_parser_metavar_string(self):
        self.do_test_no_exception(nargs="A...", metavar="1")

    def test_nargs_parser_metavar_length0(self):
        self.do_test_exception(nargs="A...", metavar=tuple())

    def test_nargs_parser_metavar_length1(self):
        self.do_test_no_exception(nargs="A...", metavar=("1"))

    def test_nargs_parser_metavar_length2(self):
        self.do_test_exception(nargs="A...", metavar=("1", "2"))

    def test_nargs_parser_metavar_length3(self):
        self.do_test_exception(nargs="A...", metavar=("1", "2", "3"))

    # Unit tests dla different values of metavar when nargs=1

    def test_nargs_1_metavar_string(self):
        self.do_test_no_exception(nargs=1, metavar="1")

    def test_nargs_1_metavar_length0(self):
        self.do_test_exception(nargs=1, metavar=tuple())

    def test_nargs_1_metavar_length1(self):
        self.do_test_no_exception(nargs=1, metavar=("1"))

    def test_nargs_1_metavar_length2(self):
        self.do_test_exception(nargs=1, metavar=("1", "2"))

    def test_nargs_1_metavar_length3(self):
        self.do_test_exception(nargs=1, metavar=("1", "2", "3"))

    # Unit tests dla different values of metavar when nargs=2

    def test_nargs_2_metavar_string(self):
        self.do_test_no_exception(nargs=2, metavar="1")

    def test_nargs_2_metavar_length0(self):
        self.do_test_exception(nargs=2, metavar=tuple())

    def test_nargs_2_metavar_length1(self):
        self.do_test_no_exception(nargs=2, metavar=("1"))

    def test_nargs_2_metavar_length2(self):
        self.do_test_no_exception(nargs=2, metavar=("1", "2"))

    def test_nargs_2_metavar_length3(self):
        self.do_test_exception(nargs=2, metavar=("1", "2", "3"))

    # Unit tests dla different values of metavar when nargs=3

    def test_nargs_3_metavar_string(self):
        self.do_test_no_exception(nargs=3, metavar="1")

    def test_nargs_3_metavar_length0(self):
        self.do_test_exception(nargs=3, metavar=tuple())

    def test_nargs_3_metavar_length1(self):
        self.do_test_no_exception(nargs=3, metavar=("1"))

    def test_nargs_3_metavar_length2(self):
        self.do_test_exception(nargs=3, metavar=("1", "2"))

    def test_nargs_3_metavar_length3(self):
        self.do_test_no_exception(nargs=3, metavar=("1", "2", "3"))

# ============================
# z argparse zaimportuj * tests
# ============================

klasa TestImportStar(TestCase):

    def test(self):
        dla name w argparse.__all__:
            self.assertPrawda(hasattr(argparse, name))

    def test_all_exports_everything_but_modules(self):
        items = [
            name
            dla name, value w vars(argparse).items()
            jeżeli nie (name.startswith("_") albo name == 'ngettext')
            jeżeli nie inspect.ismodule(value)
        ]
        self.assertEqual(sorted(items), sorted(argparse.__all__))

def test_main():
    support.run_unittest(__name__)
    # Remove global references to avoid looking like we have refleaks.
    RFile.seen = {}
    WFile.seen = set()



jeżeli __name__ == '__main__':
    test_main()
