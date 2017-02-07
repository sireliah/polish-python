"""Tests dla distutils.dir_util."""
zaimportuj unittest
zaimportuj os
zaimportuj stat
zaimportuj sys
z unittest.mock zaimportuj patch

z distutils zaimportuj dir_util, errors
z distutils.dir_util zaimportuj (mkpath, remove_tree, create_tree, copy_tree,
                                ensure_relative)

z distutils zaimportuj log
z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest


klasa DirUtilTestCase(support.TempdirManager, unittest.TestCase):

    def _log(self, msg, *args):
        jeżeli len(args) > 0:
            self._logs.append(msg % args)
        inaczej:
            self._logs.append(msg)

    def setUp(self):
        super(DirUtilTestCase, self).setUp()
        self._logs = []
        tmp_dir = self.mkdtemp()
        self.root_target = os.path.join(tmp_dir, 'deep')
        self.target = os.path.join(self.root_target, 'here')
        self.target2 = os.path.join(tmp_dir, 'deep2')
        self.old_log = log.info
        log.info = self._log

    def tearDown(self):
        log.info = self.old_log
        super(DirUtilTestCase, self).tearDown()

    def test_mkpath_remove_tree_verbosity(self):

        mkpath(self.target, verbose=0)
        wanted = []
        self.assertEqual(self._logs, wanted)
        remove_tree(self.root_target, verbose=0)

        mkpath(self.target, verbose=1)
        wanted = ['creating %s' % self.root_target,
                  'creating %s' % self.target]
        self.assertEqual(self._logs, wanted)
        self._logs = []

        remove_tree(self.root_target, verbose=1)
        wanted = ["removing '%s' (and everything under it)" % self.root_target]
        self.assertEqual(self._logs, wanted)

    @unittest.skipIf(sys.platform.startswith('win'),
        "This test jest only appropriate dla POSIX-like systems.")
    def test_mkpath_with_custom_mode(self):
        # Get oraz set the current umask value dla testing mode bits.
        umask = os.umask(0o002)
        os.umask(umask)
        mkpath(self.target, 0o700)
        self.assertEqual(
            stat.S_IMODE(os.stat(self.target).st_mode), 0o700 & ~umask)
        mkpath(self.target2, 0o555)
        self.assertEqual(
            stat.S_IMODE(os.stat(self.target2).st_mode), 0o555 & ~umask)

    def test_create_tree_verbosity(self):

        create_tree(self.root_target, ['one', 'two', 'three'], verbose=0)
        self.assertEqual(self._logs, [])
        remove_tree(self.root_target, verbose=0)

        wanted = ['creating %s' % self.root_target]
        create_tree(self.root_target, ['one', 'two', 'three'], verbose=1)
        self.assertEqual(self._logs, wanted)

        remove_tree(self.root_target, verbose=0)

    def test_copy_tree_verbosity(self):

        mkpath(self.target, verbose=0)

        copy_tree(self.target, self.target2, verbose=0)
        self.assertEqual(self._logs, [])

        remove_tree(self.root_target, verbose=0)

        mkpath(self.target, verbose=0)
        a_file = os.path.join(self.target, 'ok.txt')
        przy open(a_file, 'w') jako f:
            f.write('some content')

        wanted = ['copying %s -> %s' % (a_file, self.target2)]
        copy_tree(self.target, self.target2, verbose=1)
        self.assertEqual(self._logs, wanted)

        remove_tree(self.root_target, verbose=0)
        remove_tree(self.target2, verbose=0)

    def test_copy_tree_skips_nfs_temp_files(self):
        mkpath(self.target, verbose=0)

        a_file = os.path.join(self.target, 'ok.txt')
        nfs_file = os.path.join(self.target, '.nfs123abc')
        dla f w a_file, nfs_file:
            przy open(f, 'w') jako fh:
                fh.write('some content')

        copy_tree(self.target, self.target2)
        self.assertEqual(os.listdir(self.target2), ['ok.txt'])

        remove_tree(self.root_target, verbose=0)
        remove_tree(self.target2, verbose=0)

    def test_ensure_relative(self):
        jeżeli os.sep == '/':
            self.assertEqual(ensure_relative('/home/foo'), 'home/foo')
            self.assertEqual(ensure_relative('some/path'), 'some/path')
        inaczej:   # \\
            self.assertEqual(ensure_relative('c:\\home\\foo'), 'c:home\\foo')
            self.assertEqual(ensure_relative('home\\foo'), 'home\\foo')

    def test_copy_tree_exception_in_listdir(self):
        """
        An exception w listdir should podnieś a DistutilsFileError
        """
        przy patch("os.listdir", side_effect=OSError()), \
             self.assertRaises(errors.DistutilsFileError):
            src = self.tempdirs[-1]
            dir_util.copy_tree(src, Nic)


def test_suite():
    zwróć unittest.makeSuite(DirUtilTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
