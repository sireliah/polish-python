# test_getopt.py
# David Goodger <dgoodger@bigfoot.com> 2000-08-19

z test.support zaimportuj verbose, run_doctest, EnvironmentVarGuard
zaimportuj unittest

zaimportuj getopt

sentinel = object()

klasa GetoptTests(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentVarGuard()
        jeżeli "POSIXLY_CORRECT" w self.env:
            usuń self.env["POSIXLY_CORRECT"]

    def tearDown(self):
        self.env.__exit__()
        usuń self.env

    def assertError(self, *args, **kwargs):
        self.assertRaises(getopt.GetoptError, *args, **kwargs)

    def test_short_has_arg(self):
        self.assertPrawda(getopt.short_has_arg('a', 'a:'))
        self.assertNieprawda(getopt.short_has_arg('a', 'a'))
        self.assertError(getopt.short_has_arg, 'a', 'b')

    def test_long_has_args(self):
        has_arg, option = getopt.long_has_args('abc', ['abc='])
        self.assertPrawda(has_arg)
        self.assertEqual(option, 'abc')

        has_arg, option = getopt.long_has_args('abc', ['abc'])
        self.assertNieprawda(has_arg)
        self.assertEqual(option, 'abc')

        has_arg, option = getopt.long_has_args('abc', ['abcd'])
        self.assertNieprawda(has_arg)
        self.assertEqual(option, 'abcd')

        self.assertError(getopt.long_has_args, 'abc', ['def'])
        self.assertError(getopt.long_has_args, 'abc', [])
        self.assertError(getopt.long_has_args, 'abc', ['abcd','abcde'])

    def test_do_shorts(self):
        opts, args = getopt.do_shorts([], 'a', 'a', [])
        self.assertEqual(opts, [('-a', '')])
        self.assertEqual(args, [])

        opts, args = getopt.do_shorts([], 'a1', 'a:', [])
        self.assertEqual(opts, [('-a', '1')])
        self.assertEqual(args, [])

        #opts, args = getopt.do_shorts([], 'a=1', 'a:', [])
        #self.assertEqual(opts, [('-a', '1')])
        #self.assertEqual(args, [])

        opts, args = getopt.do_shorts([], 'a', 'a:', ['1'])
        self.assertEqual(opts, [('-a', '1')])
        self.assertEqual(args, [])

        opts, args = getopt.do_shorts([], 'a', 'a:', ['1', '2'])
        self.assertEqual(opts, [('-a', '1')])
        self.assertEqual(args, ['2'])

        self.assertError(getopt.do_shorts, [], 'a1', 'a', [])
        self.assertError(getopt.do_shorts, [], 'a', 'a:', [])

    def test_do_longs(self):
        opts, args = getopt.do_longs([], 'abc', ['abc'], [])
        self.assertEqual(opts, [('--abc', '')])
        self.assertEqual(args, [])

        opts, args = getopt.do_longs([], 'abc=1', ['abc='], [])
        self.assertEqual(opts, [('--abc', '1')])
        self.assertEqual(args, [])

        opts, args = getopt.do_longs([], 'abc=1', ['abcd='], [])
        self.assertEqual(opts, [('--abcd', '1')])
        self.assertEqual(args, [])

        opts, args = getopt.do_longs([], 'abc', ['ab', 'abc', 'abcd'], [])
        self.assertEqual(opts, [('--abc', '')])
        self.assertEqual(args, [])

        # Much like the preceding, wyjąwszy przy a non-alpha character ("-") w
        # option name that precedes "="; failed w
        # http://python.org/sf/126863
        opts, args = getopt.do_longs([], 'foo=42', ['foo-bar', 'foo=',], [])
        self.assertEqual(opts, [('--foo', '42')])
        self.assertEqual(args, [])

        self.assertError(getopt.do_longs, [], 'abc=1', ['abc'], [])
        self.assertError(getopt.do_longs, [], 'abc', ['abc='], [])

    def test_getopt(self):
        # note: the empty string between '-a' oraz '--beta' jest significant:
        # it simulates an empty string option argument ('-a ""') on the
        # command line.
        cmdline = ['-a', '1', '-b', '--alpha=2', '--beta', '-a', '3', '-a',
                   '', '--beta', 'arg1', 'arg2']

        opts, args = getopt.getopt(cmdline, 'a:b', ['alpha=', 'beta'])
        self.assertEqual(opts, [('-a', '1'), ('-b', ''),
                                ('--alpha', '2'), ('--beta', ''),
                                ('-a', '3'), ('-a', ''), ('--beta', '')])
        # Note ambiguity of ('-b', '') oraz ('-a', '') above. This must be
        # accounted dla w the code that calls getopt().
        self.assertEqual(args, ['arg1', 'arg2'])

        self.assertError(getopt.getopt, cmdline, 'a:b', ['alpha', 'beta'])

    def test_gnu_getopt(self):
        # Test handling of GNU style scanning mode.
        cmdline = ['-a', 'arg1', '-b', '1', '--alpha', '--beta=2']

        # GNU style
        opts, args = getopt.gnu_getopt(cmdline, 'ab:', ['alpha', 'beta='])
        self.assertEqual(args, ['arg1'])
        self.assertEqual(opts, [('-a', ''), ('-b', '1'),
                                ('--alpha', ''), ('--beta', '2')])

        # recognize "-" jako an argument
        opts, args = getopt.gnu_getopt(['-a', '-', '-b', '-'], 'ab:', [])
        self.assertEqual(args, ['-'])
        self.assertEqual(opts, [('-a', ''), ('-b', '-')])

        # Posix style via +
        opts, args = getopt.gnu_getopt(cmdline, '+ab:', ['alpha', 'beta='])
        self.assertEqual(opts, [('-a', '')])
        self.assertEqual(args, ['arg1', '-b', '1', '--alpha', '--beta=2'])

        # Posix style via POSIXLY_CORRECT
        self.env["POSIXLY_CORRECT"] = "1"
        opts, args = getopt.gnu_getopt(cmdline, 'ab:', ['alpha', 'beta='])
        self.assertEqual(opts, [('-a', '')])
        self.assertEqual(args, ['arg1', '-b', '1', '--alpha', '--beta=2'])

    def test_libref_examples(self):
        s = """
        Examples z the Library Reference:  Doc/lib/libgetopt.tex

        An example using only Unix style options:


        >>> zaimportuj getopt
        >>> args = '-a -b -cfoo -d bar a1 a2'.split()
        >>> args
        ['-a', '-b', '-cfoo', '-d', 'bar', 'a1', 'a2']
        >>> optlist, args = getopt.getopt(args, 'abc:d:')
        >>> optlist
        [('-a', ''), ('-b', ''), ('-c', 'foo'), ('-d', 'bar')]
        >>> args
        ['a1', 'a2']

        Using long option names jest equally easy:


        >>> s = '--condition=foo --testing --output-file abc.def -x a1 a2'
        >>> args = s.split()
        >>> args
        ['--condition=foo', '--testing', '--output-file', 'abc.def', '-x', 'a1', 'a2']
        >>> optlist, args = getopt.getopt(args, 'x', [
        ...     'condition=', 'output-file=', 'testing'])
        >>> optlist
        [('--condition', 'foo'), ('--testing', ''), ('--output-file', 'abc.def'), ('-x', '')]
        >>> args
        ['a1', 'a2']
        """

        zaimportuj types
        m = types.ModuleType("libreftest", s)
        run_doctest(m, verbose)

    def test_issue4629(self):
        longopts, shortopts = getopt.getopt(['--help='], '', ['help='])
        self.assertEqual(longopts, [('--help', '')])
        longopts, shortopts = getopt.getopt(['--help=x'], '', ['help='])
        self.assertEqual(longopts, [('--help', 'x')])
        self.assertRaises(getopt.GetoptError, getopt.getopt, ['--help='], '', ['help'])

jeżeli __name__ == "__main__":
    unittest.main()
