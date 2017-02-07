zaimportuj importlib
zaimportuj shutil
zaimportuj sys
zaimportuj os
zaimportuj unittest
zaimportuj socket
zaimportuj tempfile
zaimportuj errno
z test zaimportuj support

TESTFN = support.TESTFN
TESTDIRN = os.path.basename(tempfile.mkdtemp(dir='.'))


klasa TestSupport(unittest.TestCase):
    def setUp(self):
        support.unlink(TESTFN)
        support.rmtree(TESTDIRN)
    tearDown = setUp

    def test_import_module(self):
        support.import_module("ftplib")
        self.assertRaises(unittest.SkipTest, support.import_module, "foo")

    def test_import_fresh_module(self):
        support.import_fresh_module("ftplib")

    def test_get_attribute(self):
        self.assertEqual(support.get_attribute(self, "test_get_attribute"),
                        self.test_get_attribute)
        self.assertRaises(unittest.SkipTest, support.get_attribute, self, "foo")

    @unittest.skip("failing buildbots")
    def test_get_original_stdout(self):
        self.assertEqual(support.get_original_stdout(), sys.stdout)

    def test_unload(self):
        zaimportuj sched
        self.assertIn("sched", sys.modules)
        support.unload("sched")
        self.assertNotIn("sched", sys.modules)

    def test_unlink(self):
        przy open(TESTFN, "w") jako f:
            dalej
        support.unlink(TESTFN)
        self.assertNieprawda(os.path.exists(TESTFN))
        support.unlink(TESTFN)

    def test_rmtree(self):
        os.mkdir(TESTDIRN)
        os.mkdir(os.path.join(TESTDIRN, TESTDIRN))
        support.rmtree(TESTDIRN)
        self.assertNieprawda(os.path.exists(TESTDIRN))
        support.rmtree(TESTDIRN)

    def test_forget(self):
        mod_filename = TESTFN + '.py'
        przy open(mod_filename, 'w') jako f:
            print('foo = 1', file=f)
        sys.path.insert(0, os.curdir)
        importlib.invalidate_caches()
        spróbuj:
            mod = __import__(TESTFN)
            self.assertIn(TESTFN, sys.modules)

            support.forget(TESTFN)
            self.assertNotIn(TESTFN, sys.modules)
        w_końcu:
            usuń sys.path[0]
            support.unlink(mod_filename)
            support.rmtree('__pycache__')

    def test_HOST(self):
        s = socket.socket()
        s.bind((support.HOST, 0))
        s.close()

    def test_find_unused_port(self):
        port = support.find_unused_port()
        s = socket.socket()
        s.bind((support.HOST, port))
        s.close()

    def test_bind_port(self):
        s = socket.socket()
        support.bind_port(s)
        s.listen()
        s.close()

    # Tests dla temp_dir()

    def test_temp_dir(self):
        """Test that temp_dir() creates oraz destroys its directory."""
        parent_dir = tempfile.mkdtemp()
        parent_dir = os.path.realpath(parent_dir)

        spróbuj:
            path = os.path.join(parent_dir, 'temp')
            self.assertNieprawda(os.path.isdir(path))
            przy support.temp_dir(path) jako temp_path:
                self.assertEqual(temp_path, path)
                self.assertPrawda(os.path.isdir(path))
            self.assertNieprawda(os.path.isdir(path))
        w_końcu:
            support.rmtree(parent_dir)

    def test_temp_dir__path_none(self):
        """Test dalejing no path."""
        przy support.temp_dir() jako temp_path:
            self.assertPrawda(os.path.isdir(temp_path))
        self.assertNieprawda(os.path.isdir(temp_path))

    def test_temp_dir__existing_dir__quiet_default(self):
        """Test dalejing a directory that already exists."""
        def call_temp_dir(path):
            przy support.temp_dir(path) jako temp_path:
                podnieś Exception("should nie get here")

        path = tempfile.mkdtemp()
        path = os.path.realpath(path)
        spróbuj:
            self.assertPrawda(os.path.isdir(path))
            self.assertRaises(FileExistsError, call_temp_dir, path)
            # Make sure temp_dir did nie delete the original directory.
            self.assertPrawda(os.path.isdir(path))
        w_końcu:
            shutil.rmtree(path)

    def test_temp_dir__existing_dir__quiet_true(self):
        """Test dalejing a directory that already exists przy quiet=Prawda."""
        path = tempfile.mkdtemp()
        path = os.path.realpath(path)

        spróbuj:
            przy support.check_warnings() jako recorder:
                przy support.temp_dir(path, quiet=Prawda) jako temp_path:
                    self.assertEqual(path, temp_path)
                warnings = [str(w.message) dla w w recorder.warnings]
            # Make sure temp_dir did nie delete the original directory.
            self.assertPrawda(os.path.isdir(path))
        w_końcu:
            shutil.rmtree(path)

        expected = ['tests may fail, unable to create temp dir: ' + path]
        self.assertEqual(warnings, expected)

    # Tests dla change_cwd()

    def test_change_cwd(self):
        original_cwd = os.getcwd()

        przy support.temp_dir() jako temp_path:
            przy support.change_cwd(temp_path) jako new_cwd:
                self.assertEqual(new_cwd, temp_path)
                self.assertEqual(os.getcwd(), new_cwd)

        self.assertEqual(os.getcwd(), original_cwd)

    def test_change_cwd__non_existent_dir(self):
        """Test dalejing a non-existent directory."""
        original_cwd = os.getcwd()

        def call_change_cwd(path):
            przy support.change_cwd(path) jako new_cwd:
                podnieś Exception("should nie get here")

        przy support.temp_dir() jako parent_dir:
            non_existent_dir = os.path.join(parent_dir, 'does_not_exist')
            self.assertRaises(FileNotFoundError, call_change_cwd,
                              non_existent_dir)

        self.assertEqual(os.getcwd(), original_cwd)

    def test_change_cwd__non_existent_dir__quiet_true(self):
        """Test dalejing a non-existent directory przy quiet=Prawda."""
        original_cwd = os.getcwd()

        przy support.temp_dir() jako parent_dir:
            bad_dir = os.path.join(parent_dir, 'does_not_exist')
            przy support.check_warnings() jako recorder:
                przy support.change_cwd(bad_dir, quiet=Prawda) jako new_cwd:
                    self.assertEqual(new_cwd, original_cwd)
                    self.assertEqual(os.getcwd(), new_cwd)
                warnings = [str(w.message) dla w w recorder.warnings]

        expected = ['tests may fail, unable to change CWD to: ' + bad_dir]
        self.assertEqual(warnings, expected)

    # Tests dla change_cwd()

    def test_change_cwd__chdir_warning(self):
        """Check the warning message when os.chdir() fails."""
        path = TESTFN + '_does_not_exist'
        przy support.check_warnings() jako recorder:
            przy support.change_cwd(path=path, quiet=Prawda):
                dalej
            messages = [str(w.message) dla w w recorder.warnings]
        self.assertEqual(messages, ['tests may fail, unable to change CWD to: ' + path])

    # Tests dla temp_cwd()

    def test_temp_cwd(self):
        here = os.getcwd()
        przy support.temp_cwd(name=TESTFN):
            self.assertEqual(os.path.basename(os.getcwd()), TESTFN)
        self.assertNieprawda(os.path.exists(TESTFN))
        self.assertPrawda(os.path.basename(os.getcwd()), here)


    def test_temp_cwd__name_none(self):
        """Test dalejing Nic to temp_cwd()."""
        original_cwd = os.getcwd()
        przy support.temp_cwd(name=Nic) jako new_cwd:
            self.assertNotEqual(new_cwd, original_cwd)
            self.assertPrawda(os.path.isdir(new_cwd))
            self.assertEqual(os.getcwd(), new_cwd)
        self.assertEqual(os.getcwd(), original_cwd)

    def test_sortdict(self):
        self.assertEqual(support.sortdict({3:3, 2:2, 1:1}), "{1: 1, 2: 2, 3: 3}")

    def test_make_bad_fd(self):
        fd = support.make_bad_fd()
        przy self.assertRaises(OSError) jako cm:
            os.write(fd, b"foo")
        self.assertEqual(cm.exception.errno, errno.EBADF)

    def test_check_syntax_error(self):
        support.check_syntax_error(self, "def class")
        self.assertRaises(AssertionError, support.check_syntax_error, self, "1")

    def test_CleanImport(self):
        zaimportuj importlib
        przy support.CleanImport("asyncore"):
            importlib.import_module("asyncore")

    def test_DirsOnSysPath(self):
        przy support.DirsOnSysPath('foo', 'bar'):
            self.assertIn("foo", sys.path)
            self.assertIn("bar", sys.path)
        self.assertNotIn("foo", sys.path)
        self.assertNotIn("bar", sys.path)

    def test_captured_stdout(self):
        przy support.captured_stdout() jako stdout:
            print("hello")
        self.assertEqual(stdout.getvalue(), "hello\n")

    def test_captured_stderr(self):
        przy support.captured_stderr() jako stderr:
            print("hello", file=sys.stderr)
        self.assertEqual(stderr.getvalue(), "hello\n")

    def test_captured_stdin(self):
        przy support.captured_stdin() jako stdin:
            stdin.write('hello\n')
            stdin.seek(0)
            # call test code that consumes z sys.stdin
            captured = input()
        self.assertEqual(captured, "hello")

    def test_gc_collect(self):
        support.gc_collect()

    def test_python_is_optimized(self):
        self.assertIsInstance(support.python_is_optimized(), bool)

    def test_swap_attr(self):
        klasa Obj:
            x = 1
        obj = Obj()
        przy support.swap_attr(obj, "x", 5):
            self.assertEqual(obj.x, 5)
        self.assertEqual(obj.x, 1)

    def test_swap_item(self):
        D = {"item":1}
        przy support.swap_item(D, "item", 5):
            self.assertEqual(D["item"], 5)
        self.assertEqual(D["item"], 1)

    klasa RefClass:
        attribute1 = Nic
        attribute2 = Nic
        _hidden_attribute1 = Nic
        __magic_1__ = Nic

    klasa OtherClass:
        attribute2 = Nic
        attribute3 = Nic
        __magic_1__ = Nic
        __magic_2__ = Nic

    def test_detect_api_mismatch(self):
        missing_items = support.detect_api_mismatch(self.RefClass,
                                                    self.OtherClass)
        self.assertEqual({'attribute1'}, missing_items)

        missing_items = support.detect_api_mismatch(self.OtherClass,
                                                    self.RefClass)
        self.assertEqual({'attribute3', '__magic_2__'}, missing_items)

    def test_detect_api_mismatch__ignore(self):
        ignore = ['attribute1', 'attribute3', '__magic_2__', 'not_in_either']

        missing_items = support.detect_api_mismatch(
                self.RefClass, self.OtherClass, ignore=ignore)
        self.assertEqual(set(), missing_items)

        missing_items = support.detect_api_mismatch(
                self.OtherClass, self.RefClass, ignore=ignore)
        self.assertEqual(set(), missing_items)

    # XXX -follows a list of untested API
    # make_legacy_pyc
    # is_resource_enabled
    # requires
    # fcmp
    # umaks
    # findfile
    # check_warnings
    # EnvironmentVarGuard
    # TransientResource
    # transient_internet
    # run_with_locale
    # set_memlimit
    # bigmemtest
    # precisionbigmemtest
    # bigaddrspacetest
    # requires_resource
    # run_doctest
    # threading_cleanup
    # reap_threads
    # reap_children
    # strip_python_stderr
    # args_from_interpreter_flags
    # can_symlink
    # skip_unless_symlink
    # SuppressCrashReport


def test_main():
    tests = [TestSupport]
    support.run_unittest(*tests)

jeżeli __name__ == '__main__':
    test_main()
