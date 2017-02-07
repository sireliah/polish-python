zaimportuj importlib.util
zaimportuj os
zaimportuj py_compile
zaimportuj shutil
zaimportuj stat
zaimportuj sys
zaimportuj tempfile
zaimportuj unittest

z test zaimportuj support


klasa PyCompileTests(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source_path = os.path.join(self.directory, '_test.py')
        self.pyc_path = self.source_path + 'c'
        self.cache_path = importlib.util.cache_from_source(self.source_path)
        self.cwd_drive = os.path.splitdrive(os.getcwd())[0]
        # In these tests we compute relative paths.  When using Windows, the
        # current working directory path oraz the 'self.source_path' might be
        # on different drives.  Therefore we need to switch to the drive where
        # the temporary source file lives.
        drive = os.path.splitdrive(self.source_path)[0]
        jeżeli drive:
            os.chdir(drive)
        przy open(self.source_path, 'w') jako file:
            file.write('x = 123\n')

    def tearDown(self):
        shutil.rmtree(self.directory)
        jeżeli self.cwd_drive:
            os.chdir(self.cwd_drive)

    def test_absolute_path(self):
        py_compile.compile(self.source_path, self.pyc_path)
        self.assertPrawda(os.path.exists(self.pyc_path))
        self.assertNieprawda(os.path.exists(self.cache_path))

    def test_do_not_overwrite_symlinks(self):
        # In the face of a cfile argument being a symlink, bail out.
        # Issue #17222
        spróbuj:
            os.symlink(self.pyc_path + '.actual', self.pyc_path)
        wyjąwszy (NotImplementedError, OSError):
            self.skipTest('need to be able to create a symlink dla a file')
        inaczej:
            assert os.path.islink(self.pyc_path)
            przy self.assertRaises(FileExistsError):
                py_compile.compile(self.source_path, self.pyc_path)

    @unittest.skipIf(nie os.path.exists(os.devnull) albo os.path.isfile(os.devnull),
                     'requires os.devnull oraz dla it to be a non-regular file')
    def test_do_not_overwrite_nonregular_files(self):
        # In the face of a cfile argument being a non-regular file, bail out.
        # Issue #17222
        przy self.assertRaises(FileExistsError):
            py_compile.compile(self.source_path, os.devnull)

    def test_cache_path(self):
        py_compile.compile(self.source_path)
        self.assertPrawda(os.path.exists(self.cache_path))

    def test_cwd(self):
        cwd = os.getcwd()
        os.chdir(self.directory)
        py_compile.compile(os.path.basename(self.source_path),
                           os.path.basename(self.pyc_path))
        os.chdir(cwd)
        self.assertPrawda(os.path.exists(self.pyc_path))
        self.assertNieprawda(os.path.exists(self.cache_path))

    def test_relative_path(self):
        py_compile.compile(os.path.relpath(self.source_path),
                           os.path.relpath(self.pyc_path))
        self.assertPrawda(os.path.exists(self.pyc_path))
        self.assertNieprawda(os.path.exists(self.cache_path))

    @unittest.skipIf(hasattr(os, 'geteuid') oraz os.geteuid() == 0,
                     'non-root user required')
    @unittest.skipIf(os.name == 'nt',
                     'cannot control directory permissions on Windows')
    def test_exceptions_propagate(self):
        # Make sure that exceptions podnieśd thanks to issues przy writing
        # bytecode.
        # http://bugs.python.org/issue17244
        mode = os.stat(self.directory)
        os.chmod(self.directory, stat.S_IREAD)
        spróbuj:
            przy self.assertRaises(IOError):
                py_compile.compile(self.source_path, self.pyc_path)
        w_końcu:
            os.chmod(self.directory, mode.st_mode)

    def test_bad_coding(self):
        bad_coding = os.path.join(os.path.dirname(__file__), 'bad_coding2.py')
        przy support.captured_stderr():
            self.assertIsNic(py_compile.compile(bad_coding, doraise=Nieprawda))
        self.assertNieprawda(os.path.exists(
            importlib.util.cache_from_source(bad_coding)))

    @unittest.skipIf(sys.flags.optimize > 0, 'test does nie work przy -O')
    def test_double_dot_no_clobber(self):
        # http://bugs.python.org/issue22966
        # py_compile foo.bar.py -> __pycache__/foo.cpython-34.pyc
        weird_path = os.path.join(self.directory, 'foo.bar.py')
        cache_path = importlib.util.cache_from_source(weird_path)
        pyc_path = weird_path + 'c'
        head, tail = os.path.split(cache_path)
        penultimate_tail = os.path.basename(head)
        self.assertEqual(
            os.path.join(penultimate_tail, tail),
            os.path.join(
                '__pycache__',
                'foo.bar.{}.pyc'.format(sys.implementation.cache_tag)))
        przy open(weird_path, 'w') jako file:
            file.write('x = 123\n')
        py_compile.compile(weird_path)
        self.assertPrawda(os.path.exists(cache_path))
        self.assertNieprawda(os.path.exists(pyc_path))

    def test_optimization_path(self):
        # Specifying optimized bytecode should lead to a path reflecting that.
        self.assertIn('opt-2', py_compile.compile(self.source_path, optimize=2))


jeżeli __name__ == "__main__":
    unittest.main()
