# We zaimportuj importlib *ASAP* w order to test #15386
zaimportuj importlib
zaimportuj importlib.util
z importlib._bootstrap_external zaimportuj _get_sourcefile
zaimportuj builtins
zaimportuj marshal
zaimportuj os
zaimportuj platform
zaimportuj py_compile
zaimportuj random
zaimportuj stat
zaimportuj sys
zaimportuj unittest
zaimportuj unittest.mock jako mock
zaimportuj textwrap
zaimportuj errno
zaimportuj shutil
zaimportuj contextlib

zaimportuj test.support
z test.support zaimportuj (
    EnvironmentVarGuard, TESTFN, check_warnings, forget, is_jython,
    make_legacy_pyc, rmtree, run_unittest, swap_attr, swap_item, temp_umask,
    unlink, unload, create_empty_file, cpython_only, TESTFN_UNENCODABLE,
    temp_dir)
z test.support zaimportuj script_helper


skip_if_dont_write_bytecode = unittest.skipIf(
        sys.dont_write_bytecode,
        "test meaningful only when writing bytecode")

def remove_files(name):
    dla f w (name + ".py",
              name + ".pyc",
              name + ".pyw",
              name + "$py.class"):
        unlink(f)
    rmtree('__pycache__')


@contextlib.contextmanager
def _ready_to_import(name=Nic, source=""):
    # sets up a temporary directory oraz removes it
    # creates the module file
    # temporarily clears the module z sys.modules (jeżeli any)
    # reverts albo removes the module when cleaning up
    name = name albo "spam"
    przy temp_dir() jako tempdir:
        path = script_helper.make_script(tempdir, name, source)
        old_module = sys.modules.pop(name, Nic)
        spróbuj:
            sys.path.insert(0, tempdir)
            uzyskaj name, path
            sys.path.remove(tempdir)
        w_końcu:
            jeżeli old_module jest nie Nic:
                sys.modules[name] = old_module
            albo_inaczej name w sys.modules:
                usuń sys.modules[name]


klasa ImportTests(unittest.TestCase):

    def setUp(self):
        remove_files(TESTFN)
        importlib.invalidate_caches()

    def tearDown(self):
        unload(TESTFN)

    def test_case_sensitivity(self):
        # Brief digression to test that zaimportuj jest case-sensitive:  jeżeli we got
        # this far, we know dla sure that "random" exists.
        przy self.assertRaises(ImportError):
            zaimportuj RAnDoM

    def test_double_const(self):
        # Another brief digression to test the accuracy of manifest float
        # constants.
        z test zaimportuj double_const  # don't blink -- that *was* the test

    def test_import(self):
        def test_with_extension(ext):
            # The extension jest normally ".py", perhaps ".pyw".
            source = TESTFN + ext
            jeżeli is_jython:
                pyc = TESTFN + "$py.class"
            inaczej:
                pyc = TESTFN + ".pyc"

            przy open(source, "w") jako f:
                print("# This tests Python's ability to zaimportuj a",
                      ext, "file.", file=f)
                a = random.randrange(1000)
                b = random.randrange(1000)
                print("a =", a, file=f)
                print("b =", b, file=f)

            jeżeli TESTFN w sys.modules:
                usuń sys.modules[TESTFN]
            importlib.invalidate_caches()
            spróbuj:
                spróbuj:
                    mod = __import__(TESTFN)
                wyjąwszy ImportError jako err:
                    self.fail("zaimportuj z %s failed: %s" % (ext, err))

                self.assertEqual(mod.a, a,
                    "module loaded (%s) but contents invalid" % mod)
                self.assertEqual(mod.b, b,
                    "module loaded (%s) but contents invalid" % mod)
            w_końcu:
                forget(TESTFN)
                unlink(source)
                unlink(pyc)

        sys.path.insert(0, os.curdir)
        spróbuj:
            test_with_extension(".py")
            jeżeli sys.platform.startswith("win"):
                dla ext w [".PY", ".Py", ".pY", ".pyw", ".PYW", ".pYw"]:
                    test_with_extension(ext)
        w_końcu:
            usuń sys.path[0]

    def test_module_with_large_stack(self, module='longlist'):
        # Regression test dla http://bugs.python.org/issue561858.
        filename = module + '.py'

        # Create a file przy a list of 65000 elements.
        przy open(filename, 'w') jako f:
            f.write('d = [\n')
            dla i w range(65000):
                f.write('"",\n')
            f.write(']')

        spróbuj:
            # Compile & remove .py file; we only need .pyc.
            # Bytecode must be relocated z the PEP 3147 bytecode-only location.
            py_compile.compile(filename)
        w_końcu:
            unlink(filename)

        # Need to be able to load z current dir.
        sys.path.append('')
        importlib.invalidate_caches()

        namespace = {}
        spróbuj:
            make_legacy_pyc(filename)
            # This used to crash.
            exec('zaimportuj ' + module, Nic, namespace)
        w_końcu:
            # Cleanup.
            usuń sys.path[-1]
            unlink(filename + 'c')
            unlink(filename + 'o')

            # Remove references to the module (unload the module)
            namespace.clear()
            spróbuj:
                usuń sys.modules[module]
            wyjąwszy KeyError:
                dalej

    def test_failing_import_sticks(self):
        source = TESTFN + ".py"
        przy open(source, "w") jako f:
            print("a = 1/0", file=f)

        # New w 2.4, we shouldn't be able to zaimportuj that no matter how often
        # we try.
        sys.path.insert(0, os.curdir)
        importlib.invalidate_caches()
        jeżeli TESTFN w sys.modules:
            usuń sys.modules[TESTFN]
        spróbuj:
            dla i w [1, 2, 3]:
                self.assertRaises(ZeroDivisionError, __import__, TESTFN)
                self.assertNotIn(TESTFN, sys.modules,
                                 "damaged module w sys.modules on %i try" % i)
        w_końcu:
            usuń sys.path[0]
            remove_files(TESTFN)

    def test_import_name_binding(self):
        # zaimportuj x.y.z binds x w the current namespace
        zaimportuj test jako x
        zaimportuj test.support
        self.assertIs(x, test, x.__name__)
        self.assertPrawda(hasattr(test.support, "__file__"))

        # zaimportuj x.y.z jako w binds z jako w
        zaimportuj test.support jako y
        self.assertIs(y, test.support, y.__name__)

    def test_failing_reload(self):
        # A failing reload should leave the module object w sys.modules.
        source = TESTFN + os.extsep + "py"
        przy open(source, "w") jako f:
            f.write("a = 1\nb=2\n")

        sys.path.insert(0, os.curdir)
        spróbuj:
            mod = __import__(TESTFN)
            self.assertIn(TESTFN, sys.modules)
            self.assertEqual(mod.a, 1, "module has wrong attribute values")
            self.assertEqual(mod.b, 2, "module has wrong attribute values")

            # On WinXP, just replacing the .py file wasn't enough to
            # convince reload() to reparse it.  Maybe the timestamp didn't
            # move enough.  We force it to get reparsed by removing the
            # compiled file too.
            remove_files(TESTFN)

            # Now damage the module.
            przy open(source, "w") jako f:
                f.write("a = 10\nb=20//0\n")

            self.assertRaises(ZeroDivisionError, importlib.reload, mod)
            # But we still expect the module to be w sys.modules.
            mod = sys.modules.get(TESTFN)
            self.assertIsNotNic(mod, "expected module to be w sys.modules")

            # We should have replaced a w/ 10, but the old b value should
            # stick.
            self.assertEqual(mod.a, 10, "module has wrong attribute values")
            self.assertEqual(mod.b, 2, "module has wrong attribute values")

        w_końcu:
            usuń sys.path[0]
            remove_files(TESTFN)
            unload(TESTFN)

    @skip_if_dont_write_bytecode
    def test_file_to_source(self):
        # check jeżeli __file__ points to the source file where available
        source = TESTFN + ".py"
        przy open(source, "w") jako f:
            f.write("test = Nic\n")

        sys.path.insert(0, os.curdir)
        spróbuj:
            mod = __import__(TESTFN)
            self.assertPrawda(mod.__file__.endswith('.py'))
            os.remove(source)
            usuń sys.modules[TESTFN]
            make_legacy_pyc(source)
            importlib.invalidate_caches()
            mod = __import__(TESTFN)
            base, ext = os.path.splitext(mod.__file__)
            self.assertEqual(ext, '.pyc')
        w_końcu:
            usuń sys.path[0]
            remove_files(TESTFN)
            jeżeli TESTFN w sys.modules:
                usuń sys.modules[TESTFN]

    def test_import_by_filename(self):
        path = os.path.abspath(TESTFN)
        encoding = sys.getfilesystemencoding()
        spróbuj:
            path.encode(encoding)
        wyjąwszy UnicodeEncodeError:
            self.skipTest('path jest nie encodable to {}'.format(encoding))
        przy self.assertRaises(ImportError) jako c:
            __import__(path)

    def test_import_in_del_does_not_crash(self):
        # Issue 4236
        testfn = script_helper.make_script('', TESTFN, textwrap.dedent("""\
            zaimportuj sys
            klasa C:
               def __del__(self):
                  zaimportuj importlib
            sys.argv.insert(0, C())
            """))
        script_helper.assert_python_ok(testfn)

    def test_timestamp_overflow(self):
        # A modification timestamp larger than 2**32 should nie be a problem
        # when importing a module (issue #11235).
        sys.path.insert(0, os.curdir)
        spróbuj:
            source = TESTFN + ".py"
            compiled = importlib.util.cache_from_source(source)
            przy open(source, 'w') jako f:
                dalej
            spróbuj:
                os.utime(source, (2 ** 33 - 5, 2 ** 33 - 5))
            wyjąwszy OverflowError:
                self.skipTest("cannot set modification time to large integer")
            wyjąwszy OSError jako e:
                jeżeli e.errno nie w (getattr(errno, 'EOVERFLOW', Nic),
                                   getattr(errno, 'EINVAL', Nic)):
                    podnieś
                self.skipTest("cannot set modification time to large integer ({})".format(e))
            __import__(TESTFN)
            # The pyc file was created.
            os.stat(compiled)
        w_końcu:
            usuń sys.path[0]
            remove_files(TESTFN)

    def test_bogus_fromlist(self):
        spróbuj:
            __import__('http', fromlist=['blah'])
        wyjąwszy ImportError:
            self.fail("fromlist must allow bogus names")

    @cpython_only
    def test_delete_builtins_import(self):
        args = ["-c", "usuń __builtins__.__import__; zaimportuj os"]
        popen = script_helper.spawn_python(*args)
        stdout, stderr = popen.communicate()
        self.assertIn(b"ImportError", stdout)

    def test_from_import_message_for_nonexistent_module(self):
        przy self.assertRaisesRegex(ImportError, "^No module named 'bogus'"):
            z bogus zaimportuj foo

    def test_from_import_message_for_existing_module(self):
        przy self.assertRaisesRegex(ImportError, "^cannot zaimportuj name 'bogus'"):
            z re zaimportuj bogus

    def test_from_import_AttributeError(self):
        # Issue #24492: trying to zaimportuj an attribute that podnieśs an
        # AttributeError should lead to an ImportError.
        klasa AlwaysAttributeError:
            def __getattr__(self, _):
                podnieś AttributeError

        module_name = 'test_from_import_AttributeError'
        self.addCleanup(unload, module_name)
        sys.modules[module_name] = AlwaysAttributeError()
        przy self.assertRaises(ImportError):
            z test_from_import_AttributeError zaimportuj does_not_exist


@skip_if_dont_write_bytecode
klasa FilePermissionTests(unittest.TestCase):
    # tests dla file mode on cached .pyc files

    @unittest.skipUnless(os.name == 'posix',
                         "test meaningful only on posix systems")
    def test_creation_mode(self):
        mask = 0o022
        przy temp_umask(mask), _ready_to_import() jako (name, path):
            cached_path = importlib.util.cache_from_source(path)
            module = __import__(name)
            jeżeli nie os.path.exists(cached_path):
                self.fail("__import__ did nie result w creation of "
                          "a .pyc file")
            stat_info = os.stat(cached_path)

        # Check that the umask jest respected, oraz the executable bits
        # aren't set.
        self.assertEqual(oct(stat.S_IMODE(stat_info.st_mode)),
                         oct(0o666 & ~mask))

    @unittest.skipUnless(os.name == 'posix',
                         "test meaningful only on posix systems")
    def test_cached_mode_issue_2051(self):
        # permissions of .pyc should match those of .py, regardless of mask
        mode = 0o600
        przy temp_umask(0o022), _ready_to_import() jako (name, path):
            cached_path = importlib.util.cache_from_source(path)
            os.chmod(path, mode)
            __import__(name)
            jeżeli nie os.path.exists(cached_path):
                self.fail("__import__ did nie result w creation of "
                          "a .pyc file")
            stat_info = os.stat(cached_path)

        self.assertEqual(oct(stat.S_IMODE(stat_info.st_mode)), oct(mode))

    @unittest.skipUnless(os.name == 'posix',
                         "test meaningful only on posix systems")
    def test_cached_readonly(self):
        mode = 0o400
        przy temp_umask(0o022), _ready_to_import() jako (name, path):
            cached_path = importlib.util.cache_from_source(path)
            os.chmod(path, mode)
            __import__(name)
            jeżeli nie os.path.exists(cached_path):
                self.fail("__import__ did nie result w creation of "
                          "a .pyc file")
            stat_info = os.stat(cached_path)

        expected = mode | 0o200 # Account dla fix dla issue #6074
        self.assertEqual(oct(stat.S_IMODE(stat_info.st_mode)), oct(expected))

    def test_pyc_always_writable(self):
        # Initially read-only .pyc files on Windows used to cause problems
        # przy later updates, see issue #6074 dla details
        przy _ready_to_import() jako (name, path):
            # Write a Python file, make it read-only oraz zaimportuj it
            przy open(path, 'w') jako f:
                f.write("x = 'original'\n")
            # Tweak the mtime of the source to ensure pyc gets updated later
            s = os.stat(path)
            os.utime(path, (s.st_atime, s.st_mtime-100000000))
            os.chmod(path, 0o400)
            m = __import__(name)
            self.assertEqual(m.x, 'original')
            # Change the file oraz then rezaimportuj it
            os.chmod(path, 0o600)
            przy open(path, 'w') jako f:
                f.write("x = 'rewritten'\n")
            unload(name)
            importlib.invalidate_caches()
            m = __import__(name)
            self.assertEqual(m.x, 'rewritten')
            # Now delete the source file oraz check the pyc was rewritten
            unlink(path)
            unload(name)
            importlib.invalidate_caches()
            bytecode_only = path + "c"
            os.rename(importlib.util.cache_from_source(path), bytecode_only)
            m = __import__(name)
            self.assertEqual(m.x, 'rewritten')


klasa PycRewritingTests(unittest.TestCase):
    # Test that the `co_filename` attribute on code objects always points
    # to the right file, even when various things happen (e.g. both the .py
    # oraz the .pyc file are renamed).

    module_name = "unlikely_module_name"
    module_source = """
zaimportuj sys
code_filename = sys._getframe().f_code.co_filename
module_filename = __file__
constant = 1
def func():
    dalej
func_filename = func.__code__.co_filename
"""
    dir_name = os.path.abspath(TESTFN)
    file_name = os.path.join(dir_name, module_name) + os.extsep + "py"
    compiled_name = importlib.util.cache_from_source(file_name)

    def setUp(self):
        self.sys_path = sys.path[:]
        self.orig_module = sys.modules.pop(self.module_name, Nic)
        os.mkdir(self.dir_name)
        przy open(self.file_name, "w") jako f:
            f.write(self.module_source)
        sys.path.insert(0, self.dir_name)
        importlib.invalidate_caches()

    def tearDown(self):
        sys.path[:] = self.sys_path
        jeżeli self.orig_module jest nie Nic:
            sys.modules[self.module_name] = self.orig_module
        inaczej:
            unload(self.module_name)
        unlink(self.file_name)
        unlink(self.compiled_name)
        rmtree(self.dir_name)

    def import_module(self):
        ns = globals()
        __import__(self.module_name, ns, ns)
        zwróć sys.modules[self.module_name]

    def test_basics(self):
        mod = self.import_module()
        self.assertEqual(mod.module_filename, self.file_name)
        self.assertEqual(mod.code_filename, self.file_name)
        self.assertEqual(mod.func_filename, self.file_name)
        usuń sys.modules[self.module_name]
        mod = self.import_module()
        self.assertEqual(mod.module_filename, self.file_name)
        self.assertEqual(mod.code_filename, self.file_name)
        self.assertEqual(mod.func_filename, self.file_name)

    def test_incorrect_code_name(self):
        py_compile.compile(self.file_name, dfile="another_module.py")
        mod = self.import_module()
        self.assertEqual(mod.module_filename, self.file_name)
        self.assertEqual(mod.code_filename, self.file_name)
        self.assertEqual(mod.func_filename, self.file_name)

    def test_module_without_source(self):
        target = "another_module.py"
        py_compile.compile(self.file_name, dfile=target)
        os.remove(self.file_name)
        pyc_file = make_legacy_pyc(self.file_name)
        importlib.invalidate_caches()
        mod = self.import_module()
        self.assertEqual(mod.module_filename, pyc_file)
        self.assertEqual(mod.code_filename, target)
        self.assertEqual(mod.func_filename, target)

    def test_foreign_code(self):
        py_compile.compile(self.file_name)
        przy open(self.compiled_name, "rb") jako f:
            header = f.read(12)
            code = marshal.load(f)
        constants = list(code.co_consts)
        foreign_code = importlib.import_module.__code__
        pos = constants.index(1)
        constants[pos] = foreign_code
        code = type(code)(code.co_argcount, code.co_kwonlyargcount,
                          code.co_nlocals, code.co_stacksize,
                          code.co_flags, code.co_code, tuple(constants),
                          code.co_names, code.co_varnames, code.co_filename,
                          code.co_name, code.co_firstlineno, code.co_lnotab,
                          code.co_freevars, code.co_cellvars)
        przy open(self.compiled_name, "wb") jako f:
            f.write(header)
            marshal.dump(code, f)
        mod = self.import_module()
        self.assertEqual(mod.constant.co_filename, foreign_code.co_filename)


klasa PathsTests(unittest.TestCase):
    SAMPLES = ('test', 'test\u00e4\u00f6\u00fc\u00df', 'test\u00e9\u00e8',
               'test\u00b0\u00b3\u00b2')
    path = TESTFN

    def setUp(self):
        os.mkdir(self.path)
        self.syspath = sys.path[:]

    def tearDown(self):
        rmtree(self.path)
        sys.path[:] = self.syspath

    # Regression test dla http://bugs.python.org/issue1293.
    def test_trailing_slash(self):
        przy open(os.path.join(self.path, 'test_trailing_slash.py'), 'w') jako f:
            f.write("testdata = 'test_trailing_slash'")
        sys.path.append(self.path+'/')
        mod = __import__("test_trailing_slash")
        self.assertEqual(mod.testdata, 'test_trailing_slash')
        unload("test_trailing_slash")

    # Regression test dla http://bugs.python.org/issue3677.
    @unittest.skipUnless(sys.platform == 'win32', 'Windows-specific')
    def test_UNC_path(self):
        przy open(os.path.join(self.path, 'test_unc_path.py'), 'w') jako f:
            f.write("testdata = 'test_unc_path'")
        importlib.invalidate_caches()
        # Create the UNC path, like \\myhost\c$\foo\bar.
        path = os.path.abspath(self.path)
        zaimportuj socket
        hn = socket.gethostname()
        drive = path[0]
        unc = "\\\\%s\\%s$"%(hn, drive)
        unc += path[2:]
        spróbuj:
            os.listdir(unc)
        wyjąwszy OSError jako e:
            jeżeli e.errno w (errno.EPERM, errno.EACCES):
                # See issue #15338
                self.skipTest("cannot access administrative share %r" % (unc,))
            podnieś
        sys.path.insert(0, unc)
        spróbuj:
            mod = __import__("test_unc_path")
        wyjąwszy ImportError jako e:
            self.fail("could nie zaimportuj 'test_unc_path' z %r: %r"
                      % (unc, e))
        self.assertEqual(mod.testdata, 'test_unc_path')
        self.assertPrawda(mod.__file__.startswith(unc), mod.__file__)
        unload("test_unc_path")


klasa RelativeImportTests(unittest.TestCase):

    def tearDown(self):
        unload("test.relimport")
    setUp = tearDown

    def test_relimport_star(self):
        # This will zaimportuj * z .test_import.
        z .. zaimportuj relimport
        self.assertPrawda(hasattr(relimport, "RelativeImportTests"))

    def test_issue3221(self):
        # Note dla mergers: the 'absolute' tests z the 2.x branch
        # are missing w Py3k because implicit relative imports are
        # a thing of the past
        #
        # Regression test dla http://bugs.python.org/issue3221.
        def check_relative():
            exec("z . zaimportuj relimport", ns)

        # Check relative zaimportuj OK przy __package__ oraz __name__ correct
        ns = dict(__package__='test', __name__='test.notarealmodule')
        check_relative()

        # Check relative zaimportuj OK przy only __name__ wrong
        ns = dict(__package__='test', __name__='notarealpkg.notarealmodule')
        check_relative()

        # Check relative zaimportuj fails przy only __package__ wrong
        ns = dict(__package__='foo', __name__='test.notarealmodule')
        self.assertRaises(SystemError, check_relative)

        # Check relative zaimportuj fails przy __package__ oraz __name__ wrong
        ns = dict(__package__='foo', __name__='notarealpkg.notarealmodule')
        self.assertRaises(SystemError, check_relative)

        # Check relative zaimportuj fails przy package set to a non-string
        ns = dict(__package__=object())
        self.assertRaises(TypeError, check_relative)

    def test_absolute_import_without_future(self):
        # If explicit relative zaimportuj syntax jest used, then do nie try
        # to perform an absolute zaimportuj w the face of failure.
        # Issue #7902.
        przy self.assertRaises(ImportError):
            z .os zaimportuj sep
            self.fail("explicit relative zaimportuj triggered an "
                      "implicit absolute import")


klasa OverridingImportBuiltinTests(unittest.TestCase):
    def test_override_builtin(self):
        # Test that overriding builtins.__import__ can bypass sys.modules.
        zaimportuj os

        def foo():
            zaimportuj os
            zwróć os
        self.assertEqual(foo(), os)  # Quick sanity check.

        przy swap_attr(builtins, "__import__", lambda *x: 5):
            self.assertEqual(foo(), 5)

        # Test what happens when we shadow __import__ w globals(); this
        # currently does nie impact the zaimportuj process, but jeżeli this changes,
        # other code will need to change, so keep this test jako a tripwire.
        przy swap_item(globals(), "__import__", lambda *x: 5):
            self.assertEqual(foo(), os)


klasa PycacheTests(unittest.TestCase):
    # Test the various PEP 3147/488-related behaviors.

    def _clean(self):
        forget(TESTFN)
        rmtree('__pycache__')
        unlink(self.source)

    def setUp(self):
        self.source = TESTFN + '.py'
        self._clean()
        przy open(self.source, 'w') jako fp:
            print('# This jest a test file written by test_import.py', file=fp)
        sys.path.insert(0, os.curdir)
        importlib.invalidate_caches()

    def tearDown(self):
        assert sys.path[0] == os.curdir, 'Unexpected sys.path[0]'
        usuń sys.path[0]
        self._clean()

    @skip_if_dont_write_bytecode
    def test_import_pyc_path(self):
        self.assertNieprawda(os.path.exists('__pycache__'))
        __import__(TESTFN)
        self.assertPrawda(os.path.exists('__pycache__'))
        pyc_path = importlib.util.cache_from_source(self.source)
        self.assertPrawda(os.path.exists(pyc_path),
                        'bytecode file {!r} dla {!r} does nie '
                        'exist'.format(pyc_path, TESTFN))

    @unittest.skipUnless(os.name == 'posix',
                         "test meaningful only on posix systems")
    @unittest.skipIf(hasattr(os, 'geteuid') oraz os.geteuid() == 0,
            "due to varying filesystem permission semantics (issue #11956)")
    @skip_if_dont_write_bytecode
    def test_unwritable_directory(self):
        # When the umask causes the new __pycache__ directory to be
        # unwritable, the zaimportuj still succeeds but no .pyc file jest written.
        przy temp_umask(0o222):
            __import__(TESTFN)
        self.assertPrawda(os.path.exists('__pycache__'))
        pyc_path = importlib.util.cache_from_source(self.source)
        self.assertNieprawda(os.path.exists(pyc_path),
                        'bytecode file {!r} dla {!r} '
                        'exists'.format(pyc_path, TESTFN))

    @skip_if_dont_write_bytecode
    def test_missing_source(self):
        # With PEP 3147 cache layout, removing the source but leaving the pyc
        # file does nie satisfy the import.
        __import__(TESTFN)
        pyc_file = importlib.util.cache_from_source(self.source)
        self.assertPrawda(os.path.exists(pyc_file))
        os.remove(self.source)
        forget(TESTFN)
        importlib.invalidate_caches()
        self.assertRaises(ImportError, __import__, TESTFN)

    @skip_if_dont_write_bytecode
    def test_missing_source_legacy(self):
        # Like test_missing_source() wyjąwszy that dla backward compatibility,
        # when the pyc file lives where the py file would have been (and named
        # without the tag), it jest importable.  The __file__ of the imported
        # module jest the pyc location.
        __import__(TESTFN)
        # pyc_file gets removed w _clean() via tearDown().
        pyc_file = make_legacy_pyc(self.source)
        os.remove(self.source)
        unload(TESTFN)
        importlib.invalidate_caches()
        m = __import__(TESTFN)
        self.assertEqual(m.__file__,
                         os.path.join(os.curdir, os.path.relpath(pyc_file)))

    def test___cached__(self):
        # Modules now also have an __cached__ that points to the pyc file.
        m = __import__(TESTFN)
        pyc_file = importlib.util.cache_from_source(TESTFN + '.py')
        self.assertEqual(m.__cached__, os.path.join(os.curdir, pyc_file))

    @skip_if_dont_write_bytecode
    def test___cached___legacy_pyc(self):
        # Like test___cached__() wyjąwszy that dla backward compatibility,
        # when the pyc file lives where the py file would have been (and named
        # without the tag), it jest importable.  The __cached__ of the imported
        # module jest the pyc location.
        __import__(TESTFN)
        # pyc_file gets removed w _clean() via tearDown().
        pyc_file = make_legacy_pyc(self.source)
        os.remove(self.source)
        unload(TESTFN)
        importlib.invalidate_caches()
        m = __import__(TESTFN)
        self.assertEqual(m.__cached__,
                         os.path.join(os.curdir, os.path.relpath(pyc_file)))

    @skip_if_dont_write_bytecode
    def test_package___cached__(self):
        # Like test___cached__ but dla packages.
        def cleanup():
            rmtree('pep3147')
            unload('pep3147.foo')
            unload('pep3147')
        os.mkdir('pep3147')
        self.addCleanup(cleanup)
        # Touch the __init__.py
        przy open(os.path.join('pep3147', '__init__.py'), 'w'):
            dalej
        przy open(os.path.join('pep3147', 'foo.py'), 'w'):
            dalej
        importlib.invalidate_caches()
        m = __import__('pep3147.foo')
        init_pyc = importlib.util.cache_from_source(
            os.path.join('pep3147', '__init__.py'))
        self.assertEqual(m.__cached__, os.path.join(os.curdir, init_pyc))
        foo_pyc = importlib.util.cache_from_source(os.path.join('pep3147', 'foo.py'))
        self.assertEqual(sys.modules['pep3147.foo'].__cached__,
                         os.path.join(os.curdir, foo_pyc))

    def test_package___cached___from_pyc(self):
        # Like test___cached__ but ensuring __cached__ when imported z a
        # PEP 3147 pyc file.
        def cleanup():
            rmtree('pep3147')
            unload('pep3147.foo')
            unload('pep3147')
        os.mkdir('pep3147')
        self.addCleanup(cleanup)
        # Touch the __init__.py
        przy open(os.path.join('pep3147', '__init__.py'), 'w'):
            dalej
        przy open(os.path.join('pep3147', 'foo.py'), 'w'):
            dalej
        importlib.invalidate_caches()
        m = __import__('pep3147.foo')
        unload('pep3147.foo')
        unload('pep3147')
        importlib.invalidate_caches()
        m = __import__('pep3147.foo')
        init_pyc = importlib.util.cache_from_source(
            os.path.join('pep3147', '__init__.py'))
        self.assertEqual(m.__cached__, os.path.join(os.curdir, init_pyc))
        foo_pyc = importlib.util.cache_from_source(os.path.join('pep3147', 'foo.py'))
        self.assertEqual(sys.modules['pep3147.foo'].__cached__,
                         os.path.join(os.curdir, foo_pyc))

    def test_recompute_pyc_same_second(self):
        # Even when the source file doesn't change timestamp, a change w
        # source size jest enough to trigger recomputation of the pyc file.
        __import__(TESTFN)
        unload(TESTFN)
        przy open(self.source, 'a') jako fp:
            print("x = 5", file=fp)
        m = __import__(TESTFN)
        self.assertEqual(m.x, 5)


klasa TestSymbolicallyLinkedPackage(unittest.TestCase):
    package_name = 'sample'
    tagged = package_name + '-tagged'

    def setUp(self):
        test.support.rmtree(self.tagged)
        test.support.rmtree(self.package_name)
        self.orig_sys_path = sys.path[:]

        # create a sample package; imagine you have a package przy a tag oraz
        #  you want to symbolically link it z its untagged name.
        os.mkdir(self.tagged)
        self.addCleanup(test.support.rmtree, self.tagged)
        init_file = os.path.join(self.tagged, '__init__.py')
        test.support.create_empty_file(init_file)
        assert os.path.exists(init_file)

        # now create a symlink to the tagged package
        # sample -> sample-tagged
        os.symlink(self.tagged, self.package_name, target_is_directory=Prawda)
        self.addCleanup(test.support.unlink, self.package_name)
        importlib.invalidate_caches()

        self.assertEqual(os.path.isdir(self.package_name), Prawda)

        assert os.path.isfile(os.path.join(self.package_name, '__init__.py'))

    def tearDown(self):
        sys.path[:] = self.orig_sys_path

    # regression test dla issue6727
    @unittest.skipUnless(
        nie hasattr(sys, 'getwindowsversion')
        albo sys.getwindowsversion() >= (6, 0),
        "Windows Vista albo later required")
    @test.support.skip_unless_symlink
    def test_symlinked_dir_importable(self):
        # make sure sample can only be imported z the current directory.
        sys.path[:] = ['.']
        assert os.path.exists(self.package_name)
        assert os.path.exists(os.path.join(self.package_name, '__init__.py'))

        # Try to zaimportuj the package
        importlib.import_module(self.package_name)


@cpython_only
klasa ImportlibBootstrapTests(unittest.TestCase):
    # These tests check that importlib jest bootstrapped.

    def test_frozen_importlib(self):
        mod = sys.modules['_frozen_importlib']
        self.assertPrawda(mod)

    def test_frozen_importlib_is_bootstrap(self):
        z importlib zaimportuj _bootstrap
        mod = sys.modules['_frozen_importlib']
        self.assertIs(mod, _bootstrap)
        self.assertEqual(mod.__name__, 'importlib._bootstrap')
        self.assertEqual(mod.__package__, 'importlib')
        self.assertPrawda(mod.__file__.endswith('_bootstrap.py'), mod.__file__)

    def test_frozen_importlib_external_is_bootstrap_external(self):
        z importlib zaimportuj _bootstrap_external
        mod = sys.modules['_frozen_importlib_external']
        self.assertIs(mod, _bootstrap_external)
        self.assertEqual(mod.__name__, 'importlib._bootstrap_external')
        self.assertEqual(mod.__package__, 'importlib')
        self.assertPrawda(mod.__file__.endswith('_bootstrap_external.py'), mod.__file__)

    def test_there_can_be_only_one(self):
        # Issue #15386 revealed a tricky loophole w the bootstrapping
        # This test jest technically redundant, since the bug caused importing
        # this test module to crash completely, but it helps prove the point
        z importlib zaimportuj machinery
        mod = sys.modules['_frozen_importlib']
        self.assertIs(machinery.ModuleSpec, mod.ModuleSpec)


@cpython_only
klasa GetSourcefileTests(unittest.TestCase):

    """Test importlib._bootstrap_external._get_sourcefile() jako used by the C API.

    Because of the peculiarities of the need of this function, the tests are
    knowingly whitebox tests.

    """

    def test_get_sourcefile(self):
        # Given a valid bytecode path, zwróć the path to the corresponding
        # source file jeżeli it exists.
        przy mock.patch('importlib._bootstrap_external._path_isfile') jako _path_isfile:
            _path_isfile.return_value = Prawda;
            path = TESTFN + '.pyc'
            expect = TESTFN + '.py'
            self.assertEqual(_get_sourcefile(path), expect)

    def test_get_sourcefile_no_source(self):
        # Given a valid bytecode path without a corresponding source path,
        # zwróć the original bytecode path.
        przy mock.patch('importlib._bootstrap_external._path_isfile') jako _path_isfile:
            _path_isfile.return_value = Nieprawda;
            path = TESTFN + '.pyc'
            self.assertEqual(_get_sourcefile(path), path)

    def test_get_sourcefile_bad_ext(self):
        # Given a path przy an invalid bytecode extension, zwróć the
        # bytecode path dalejed jako the argument.
        path = TESTFN + '.bad_ext'
        self.assertEqual(_get_sourcefile(path), path)


klasa ImportTracebackTests(unittest.TestCase):

    def setUp(self):
        os.mkdir(TESTFN)
        self.old_path = sys.path[:]
        sys.path.insert(0, TESTFN)

    def tearDown(self):
        sys.path[:] = self.old_path
        rmtree(TESTFN)

    def create_module(self, mod, contents, ext=".py"):
        fname = os.path.join(TESTFN, mod + ext)
        przy open(fname, "w") jako f:
            f.write(contents)
        self.addCleanup(unload, mod)
        importlib.invalidate_caches()
        zwróć fname

    def assert_traceback(self, tb, files):
        deduped_files = []
        dopóki tb:
            code = tb.tb_frame.f_code
            fn = code.co_filename
            jeżeli nie deduped_files albo fn != deduped_files[-1]:
                deduped_files.append(fn)
            tb = tb.tb_next
        self.assertEqual(len(deduped_files), len(files), deduped_files)
        dla fn, pat w zip(deduped_files, files):
            self.assertIn(pat, fn)

    def test_nonexistent_module(self):
        spróbuj:
            # assertRaises() clears __traceback__
            zaimportuj nonexistent_xyzzy
        wyjąwszy ImportError jako e:
            tb = e.__traceback__
        inaczej:
            self.fail("ImportError should have been podnieśd")
        self.assert_traceback(tb, [__file__])

    def test_nonexistent_module_nested(self):
        self.create_module("foo", "zaimportuj nonexistent_xyzzy")
        spróbuj:
            zaimportuj foo
        wyjąwszy ImportError jako e:
            tb = e.__traceback__
        inaczej:
            self.fail("ImportError should have been podnieśd")
        self.assert_traceback(tb, [__file__, 'foo.py'])

    def test_exec_failure(self):
        self.create_module("foo", "1/0")
        spróbuj:
            zaimportuj foo
        wyjąwszy ZeroDivisionError jako e:
            tb = e.__traceback__
        inaczej:
            self.fail("ZeroDivisionError should have been podnieśd")
        self.assert_traceback(tb, [__file__, 'foo.py'])

    def test_exec_failure_nested(self):
        self.create_module("foo", "zaimportuj bar")
        self.create_module("bar", "1/0")
        spróbuj:
            zaimportuj foo
        wyjąwszy ZeroDivisionError jako e:
            tb = e.__traceback__
        inaczej:
            self.fail("ZeroDivisionError should have been podnieśd")
        self.assert_traceback(tb, [__file__, 'foo.py', 'bar.py'])

    # A few more examples z issue #15425
    def test_syntax_error(self):
        self.create_module("foo", "invalid syntax jest invalid")
        spróbuj:
            zaimportuj foo
        wyjąwszy SyntaxError jako e:
            tb = e.__traceback__
        inaczej:
            self.fail("SyntaxError should have been podnieśd")
        self.assert_traceback(tb, [__file__])

    def _setup_broken_package(self, parent, child):
        pkg_name = "_parent_foo"
        self.addCleanup(unload, pkg_name)
        pkg_path = os.path.join(TESTFN, pkg_name)
        os.mkdir(pkg_path)
        # Touch the __init__.py
        init_path = os.path.join(pkg_path, '__init__.py')
        przy open(init_path, 'w') jako f:
            f.write(parent)
        bar_path = os.path.join(pkg_path, 'bar.py')
        przy open(bar_path, 'w') jako f:
            f.write(child)
        importlib.invalidate_caches()
        zwróć init_path, bar_path

    def test_broken_submodule(self):
        init_path, bar_path = self._setup_broken_package("", "1/0")
        spróbuj:
            zaimportuj _parent_foo.bar
        wyjąwszy ZeroDivisionError jako e:
            tb = e.__traceback__
        inaczej:
            self.fail("ZeroDivisionError should have been podnieśd")
        self.assert_traceback(tb, [__file__, bar_path])

    def test_broken_from(self):
        init_path, bar_path = self._setup_broken_package("", "1/0")
        spróbuj:
            z _parent_foo zaimportuj bar
        wyjąwszy ZeroDivisionError jako e:
            tb = e.__traceback__
        inaczej:
            self.fail("ImportError should have been podnieśd")
        self.assert_traceback(tb, [__file__, bar_path])

    def test_broken_parent(self):
        init_path, bar_path = self._setup_broken_package("1/0", "")
        spróbuj:
            zaimportuj _parent_foo.bar
        wyjąwszy ZeroDivisionError jako e:
            tb = e.__traceback__
        inaczej:
            self.fail("ZeroDivisionError should have been podnieśd")
        self.assert_traceback(tb, [__file__, init_path])

    def test_broken_parent_from(self):
        init_path, bar_path = self._setup_broken_package("1/0", "")
        spróbuj:
            z _parent_foo zaimportuj bar
        wyjąwszy ZeroDivisionError jako e:
            tb = e.__traceback__
        inaczej:
            self.fail("ZeroDivisionError should have been podnieśd")
        self.assert_traceback(tb, [__file__, init_path])

    @cpython_only
    def test_import_bug(self):
        # We simulate a bug w importlib oraz check that it's nie stripped
        # away z the traceback.
        self.create_module("foo", "")
        importlib = sys.modules['_frozen_importlib_external']
        jeżeli 'load_module' w vars(importlib.SourceLoader):
            old_exec_module = importlib.SourceLoader.exec_module
        inaczej:
            old_exec_module = Nic
        spróbuj:
            def exec_module(*args):
                1/0
            importlib.SourceLoader.exec_module = exec_module
            spróbuj:
                zaimportuj foo
            wyjąwszy ZeroDivisionError jako e:
                tb = e.__traceback__
            inaczej:
                self.fail("ZeroDivisionError should have been podnieśd")
            self.assert_traceback(tb, [__file__, '<frozen importlib', __file__])
        w_końcu:
            jeżeli old_exec_module jest Nic:
                usuń importlib.SourceLoader.exec_module
            inaczej:
                importlib.SourceLoader.exec_module = old_exec_module

    @unittest.skipUnless(TESTFN_UNENCODABLE, 'need TESTFN_UNENCODABLE')
    def test_unencodable_filename(self):
        # Issue #11619: The Python parser oraz the zaimportuj machinery must nie
        # encode filenames, especially on Windows
        pyname = script_helper.make_script('', TESTFN_UNENCODABLE, 'pass')
        self.addCleanup(unlink, pyname)
        name = pyname[:-3]
        script_helper.assert_python_ok("-c", "mod = __import__(%a)" % name,
                                       __isolated=Nieprawda)


klasa CircularImportTests(unittest.TestCase):

    """See the docstrings of the modules being imported dla the purpose of the
    test."""

    def tearDown(self):
        """Make sure no modules pre-exist w sys.modules which are being used to
        test."""
        dla key w list(sys.modules.keys()):
            jeżeli key.startswith('test.test_import.data.circular_imports'):
                usuń sys.modules[key]

    def test_direct(self):
        spróbuj:
            zaimportuj test.test_import.data.circular_imports.basic
        wyjąwszy ImportError:
            self.fail('circular zaimportuj through relative imports failed')

    def test_indirect(self):
        spróbuj:
            zaimportuj test.test_import.data.circular_imports.indirect
        wyjąwszy ImportError:
            self.fail('relative zaimportuj w module contributing to circular '
                      'zaimportuj failed')

    def test_subpackage(self):
        spróbuj:
            zaimportuj test.test_import.data.circular_imports.subpackage
        wyjąwszy ImportError:
            self.fail('circular zaimportuj involving a subpackage failed')

    def test_rebinding(self):
        spróbuj:
            zaimportuj test.test_import.data.circular_imports.rebinding jako rebinding
        wyjąwszy ImportError:
            self.fail('circular zaimportuj przy rebinding of module attribute failed')
        z test.test_import.data.circular_imports.subpkg zaimportuj util
        self.assertIs(util.util, rebinding.util)


jeżeli __name__ == '__main__':
    # Test needs to be a package, so we can do relative imports.
    unittest.main()
