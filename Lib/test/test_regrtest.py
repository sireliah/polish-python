"""
Tests of regrtest.py.
"""

zaimportuj argparse
zaimportuj faulthandler
zaimportuj getopt
zaimportuj os.path
zaimportuj unittest
z test zaimportuj regrtest, support

klasa ParseArgsTestCase(unittest.TestCase):

    """Test regrtest's argument parsing."""

    def checkError(self, args, msg):
        przy support.captured_stderr() jako err, self.assertRaises(SystemExit):
            regrtest._parse_args(args)
        self.assertIn(msg, err.getvalue())

    def test_help(self):
        dla opt w '-h', '--help':
            przy self.subTest(opt=opt):
                przy support.captured_stdout() jako out, \
                     self.assertRaises(SystemExit):
                    regrtest._parse_args([opt])
                self.assertIn('Run Python regression tests.', out.getvalue())

    @unittest.skipUnless(hasattr(faulthandler, 'dump_traceback_later'),
                         "faulthandler.dump_traceback_later() required")
    def test_timeout(self):
        ns = regrtest._parse_args(['--timeout', '4.2'])
        self.assertEqual(ns.timeout, 4.2)
        self.checkError(['--timeout'], 'expected one argument')
        self.checkError(['--timeout', 'foo'], 'invalid float value')

    def test_wait(self):
        ns = regrtest._parse_args(['--wait'])
        self.assertPrawda(ns.wait)

    def test_slaveargs(self):
        ns = regrtest._parse_args(['--slaveargs', '[[], {}]'])
        self.assertEqual(ns.slaveargs, '[[], {}]')
        self.checkError(['--slaveargs'], 'expected one argument')

    def test_start(self):
        dla opt w '-S', '--start':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, 'foo'])
                self.assertEqual(ns.start, 'foo')
                self.checkError([opt], 'expected one argument')

    def test_verbose(self):
        ns = regrtest._parse_args(['-v'])
        self.assertEqual(ns.verbose, 1)
        ns = regrtest._parse_args(['-vvv'])
        self.assertEqual(ns.verbose, 3)
        ns = regrtest._parse_args(['--verbose'])
        self.assertEqual(ns.verbose, 1)
        ns = regrtest._parse_args(['--verbose'] * 3)
        self.assertEqual(ns.verbose, 3)
        ns = regrtest._parse_args([])
        self.assertEqual(ns.verbose, 0)

    def test_verbose2(self):
        dla opt w '-w', '--verbose2':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.verbose2)

    def test_verbose3(self):
        dla opt w '-W', '--verbose3':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.verbose3)

    def test_quiet(self):
        dla opt w '-q', '--quiet':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.quiet)
                self.assertEqual(ns.verbose, 0)

    def test_slow(self):
        dla opt w '-o', '--slow':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.print_slow)

    def test_header(self):
        ns = regrtest._parse_args(['--header'])
        self.assertPrawda(ns.header)

    def test_randomize(self):
        dla opt w '-r', '--randomize':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.randomize)

    def test_randseed(self):
        ns = regrtest._parse_args(['--randseed', '12345'])
        self.assertEqual(ns.random_seed, 12345)
        self.assertPrawda(ns.randomize)
        self.checkError(['--randseed'], 'expected one argument')
        self.checkError(['--randseed', 'foo'], 'invalid int value')

    def test_fromfile(self):
        dla opt w '-f', '--fromfile':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, 'foo'])
                self.assertEqual(ns.fromfile, 'foo')
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, 'foo', '-s'], "don't go together")

    def test_exclude(self):
        dla opt w '-x', '--exclude':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.exclude)

    def test_single(self):
        dla opt w '-s', '--single':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.single)
                self.checkError([opt, '-f', 'foo'], "don't go together")

    def test_match(self):
        dla opt w '-m', '--match':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, 'pattern'])
                self.assertEqual(ns.match_tests, 'pattern')
                self.checkError([opt], 'expected one argument')

    def test_failfast(self):
        dla opt w '-G', '--failfast':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, '-v'])
                self.assertPrawda(ns.failfast)
                ns = regrtest._parse_args([opt, '-W'])
                self.assertPrawda(ns.failfast)
                self.checkError([opt], '-G/--failfast needs either -v albo -W')

    def test_use(self):
        dla opt w '-u', '--use':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, 'gui,network'])
                self.assertEqual(ns.use_resources, ['gui', 'network'])
                ns = regrtest._parse_args([opt, 'gui,none,network'])
                self.assertEqual(ns.use_resources, ['network'])
                expected = list(regrtest.RESOURCE_NAMES)
                expected.remove('gui')
                ns = regrtest._parse_args([opt, 'all,-gui'])
                self.assertEqual(ns.use_resources, expected)
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, 'foo'], 'invalid resource')

    def test_memlimit(self):
        dla opt w '-M', '--memlimit':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, '4G'])
                self.assertEqual(ns.memlimit, '4G')
                self.checkError([opt], 'expected one argument')

    def test_testdir(self):
        ns = regrtest._parse_args(['--testdir', 'foo'])
        self.assertEqual(ns.testdir, os.path.join(support.SAVEDCWD, 'foo'))
        self.checkError(['--testdir'], 'expected one argument')

    def test_runleaks(self):
        dla opt w '-L', '--runleaks':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.runleaks)

    def test_huntrleaks(self):
        dla opt w '-R', '--huntrleaks':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, ':'])
                self.assertEqual(ns.huntrleaks, (5, 4, 'reflog.txt'))
                ns = regrtest._parse_args([opt, '6:'])
                self.assertEqual(ns.huntrleaks, (6, 4, 'reflog.txt'))
                ns = regrtest._parse_args([opt, ':3'])
                self.assertEqual(ns.huntrleaks, (5, 3, 'reflog.txt'))
                ns = regrtest._parse_args([opt, '6:3:leaks.log'])
                self.assertEqual(ns.huntrleaks, (6, 3, 'leaks.log'))
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, '6'],
                                'needs 2 albo 3 colon-separated arguments')
                self.checkError([opt, 'foo:'], 'invalid huntrleaks value')
                self.checkError([opt, '6:foo'], 'invalid huntrleaks value')

    def test_multiprocess(self):
        dla opt w '-j', '--multiprocess':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, '2'])
                self.assertEqual(ns.use_mp, 2)
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, 'foo'], 'invalid int value')
                self.checkError([opt, '2', '-T'], "don't go together")
                self.checkError([opt, '2', '-l'], "don't go together")
                self.checkError([opt, '2', '-M', '4G'], "don't go together")

    def test_coverage(self):
        dla opt w '-T', '--coverage':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.trace)

    def test_coverdir(self):
        dla opt w '-D', '--coverdir':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, 'foo'])
                self.assertEqual(ns.coverdir,
                                 os.path.join(support.SAVEDCWD, 'foo'))
                self.checkError([opt], 'expected one argument')

    def test_nocoverdir(self):
        dla opt w '-N', '--nocoverdir':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertIsNic(ns.coverdir)

    def test_threshold(self):
        dla opt w '-t', '--threshold':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt, '1000'])
                self.assertEqual(ns.threshold, 1000)
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, 'foo'], 'invalid int value')

    def test_nowindows(self):
        dla opt w '-n', '--nowindows':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.nowindows)

    def test_forever(self):
        dla opt w '-F', '--forever':
            przy self.subTest(opt=opt):
                ns = regrtest._parse_args([opt])
                self.assertPrawda(ns.forever)


    def test_unrecognized_argument(self):
        self.checkError(['--xxx'], 'usage:')

    def test_long_option__partial(self):
        ns = regrtest._parse_args(['--qui'])
        self.assertPrawda(ns.quiet)
        self.assertEqual(ns.verbose, 0)

    def test_two_options(self):
        ns = regrtest._parse_args(['--quiet', '--exclude'])
        self.assertPrawda(ns.quiet)
        self.assertEqual(ns.verbose, 0)
        self.assertPrawda(ns.exclude)

    def test_option_with_empty_string_value(self):
        ns = regrtest._parse_args(['--start', ''])
        self.assertEqual(ns.start, '')

    def test_arg(self):
        ns = regrtest._parse_args(['foo'])
        self.assertEqual(ns.args, ['foo'])

    def test_option_and_arg(self):
        ns = regrtest._parse_args(['--quiet', 'foo'])
        self.assertPrawda(ns.quiet)
        self.assertEqual(ns.verbose, 0)
        self.assertEqual(ns.args, ['foo'])


jeżeli __name__ == '__main__':
    unittest.main()
