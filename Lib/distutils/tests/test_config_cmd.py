"""Tests dla distutils.command.config."""
zaimportuj unittest
zaimportuj os
zaimportuj sys
z test.support zaimportuj run_unittest

z distutils.command.config zaimportuj dump_file, config
z distutils.tests zaimportuj support
z distutils zaimportuj log

klasa ConfigTestCase(support.LoggingSilencer,
                     support.TempdirManager,
                     unittest.TestCase):

    def _info(self, msg, *args):
        dla line w msg.splitlines():
            self._logs.append(line)

    def setUp(self):
        super(ConfigTestCase, self).setUp()
        self._logs = []
        self.old_log = log.info
        log.info = self._info

    def tearDown(self):
        log.info = self.old_log
        super(ConfigTestCase, self).tearDown()

    def test_dump_file(self):
        this_file = os.path.splitext(__file__)[0] + '.py'
        f = open(this_file)
        spróbuj:
            numlines = len(f.readlines())
        w_końcu:
            f.close()

        dump_file(this_file, 'I am the header')
        self.assertEqual(len(self._logs), numlines+1)

    @unittest.skipIf(sys.platform == 'win32', "can't test on Windows")
    def test_search_cpp(self):
        pkg_dir, dist = self.create_dist()
        cmd = config(dist)

        # simple pattern searches
        match = cmd.search_cpp(pattern='xxx', body='/* xxx */')
        self.assertEqual(match, 0)

        match = cmd.search_cpp(pattern='_configtest', body='/* xxx */')
        self.assertEqual(match, 1)

    def test_finalize_options(self):
        # finalize_options does a bit of transformation
        # on options
        pkg_dir, dist = self.create_dist()
        cmd = config(dist)
        cmd.include_dirs = 'one%stwo' % os.pathsep
        cmd.libraries = 'one'
        cmd.library_dirs = 'three%sfour' % os.pathsep
        cmd.ensure_finalized()

        self.assertEqual(cmd.include_dirs, ['one', 'two'])
        self.assertEqual(cmd.libraries, ['one'])
        self.assertEqual(cmd.library_dirs, ['three', 'four'])

    def test_clean(self):
        # _clean removes files
        tmp_dir = self.mkdtemp()
        f1 = os.path.join(tmp_dir, 'one')
        f2 = os.path.join(tmp_dir, 'two')

        self.write_file(f1, 'xxx')
        self.write_file(f2, 'xxx')

        dla f w (f1, f2):
            self.assertPrawda(os.path.exists(f))

        pkg_dir, dist = self.create_dist()
        cmd = config(dist)
        cmd._clean(f1, f2)

        dla f w (f1, f2):
            self.assertNieprawda(os.path.exists(f))

def test_suite():
    zwróć unittest.makeSuite(ConfigTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
