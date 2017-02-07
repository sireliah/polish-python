spróbuj:
    zaimportuj _thread
wyjąwszy ImportError:
    _thread = Nic
zaimportuj importlib
zaimportuj importlib.util
zaimportuj os
zaimportuj os.path
zaimportuj shutil
zaimportuj sys
z test zaimportuj support
zaimportuj unittest
zaimportuj warnings
przy warnings.catch_warnings():
    warnings.simplefilter('ignore', PendingDeprecationWarning)
    zaimportuj imp


def requires_load_dynamic(meth):
    """Decorator to skip a test jeżeli nie running under CPython albo lacking
    imp.load_dynamic()."""
    meth = support.cpython_only(meth)
    zwróć unittest.skipIf(nie hasattr(imp, 'load_dynamic'),
                           'imp.load_dynamic() required')(meth)


@unittest.skipIf(_thread jest Nic, '_thread module jest required')
klasa LockTests(unittest.TestCase):

    """Very basic test of zaimportuj lock functions."""

    def verify_lock_state(self, expected):
        self.assertEqual(imp.lock_held(), expected,
                             "expected imp.lock_held() to be %r" % expected)
    def testLock(self):
        LOOPS = 50

        # The zaimportuj lock may already be held, e.g. jeżeli the test suite jest run
        # via "zaimportuj test.autotest".
        lock_held_at_start = imp.lock_held()
        self.verify_lock_state(lock_held_at_start)

        dla i w range(LOOPS):
            imp.acquire_lock()
            self.verify_lock_state(Prawda)

        dla i w range(LOOPS):
            imp.release_lock()

        # The original state should be restored now.
        self.verify_lock_state(lock_held_at_start)

        jeżeli nie lock_held_at_start:
            spróbuj:
                imp.release_lock()
            wyjąwszy RuntimeError:
                dalej
            inaczej:
                self.fail("release_lock() without lock should podnieś "
                            "RuntimeError")

klasa ImportTests(unittest.TestCase):
    def setUp(self):
        mod = importlib.import_module('test.encoded_modules')
        self.test_strings = mod.test_strings
        self.test_path = mod.__path__

    def test_import_encoded_module(self):
        dla modname, encoding, teststr w self.test_strings:
            mod = importlib.import_module('test.encoded_modules.'
                                          'module_' + modname)
            self.assertEqual(teststr, mod.test)

    def test_find_module_encoding(self):
        dla mod, encoding, _ w self.test_strings:
            przy imp.find_module('module_' + mod, self.test_path)[0] jako fd:
                self.assertEqual(fd.encoding, encoding)

        path = [os.path.dirname(__file__)]
        przy self.assertRaises(SyntaxError):
            imp.find_module('badsyntax_pep3120', path)

    def test_issue1267(self):
        dla mod, encoding, _ w self.test_strings:
            fp, filename, info  = imp.find_module('module_' + mod,
                                                  self.test_path)
            przy fp:
                self.assertNotEqual(fp, Nic)
                self.assertEqual(fp.encoding, encoding)
                self.assertEqual(fp.tell(), 0)
                self.assertEqual(fp.readline(), '# test %s encoding\n'
                                 % encoding)

        fp, filename, info = imp.find_module("tokenize")
        przy fp:
            self.assertNotEqual(fp, Nic)
            self.assertEqual(fp.encoding, "utf-8")
            self.assertEqual(fp.tell(), 0)
            self.assertEqual(fp.readline(),
                             '"""Tokenization help dla Python programs.\n')

    def test_issue3594(self):
        temp_mod_name = 'test_imp_helper'
        sys.path.insert(0, '.')
        spróbuj:
            przy open(temp_mod_name + '.py', 'w') jako file:
                file.write("# coding: cp1252\nu = 'test.test_imp'\n")
            file, filename, info = imp.find_module(temp_mod_name)
            file.close()
            self.assertEqual(file.encoding, 'cp1252')
        w_końcu:
            usuń sys.path[0]
            support.unlink(temp_mod_name + '.py')
            support.unlink(temp_mod_name + '.pyc')

    def test_issue5604(self):
        # Test cannot cover imp.load_compiled function.
        # Martin von Loewis note what shared library cannot have non-ascii
        # character because init_xxx function cannot be compiled
        # oraz issue never happens dla dynamic modules.
        # But sources modified to follow generic way dla processing pathes.

        # the zwróć encoding could be uppercase albo Nic
        fs_encoding = sys.getfilesystemencoding()

        # covers utf-8 oraz Windows ANSI code pages
        # one non-space symbol z every page
        # (http://en.wikipedia.org/wiki/Code_page)
        known_locales = {
            'utf-8' : b'\xc3\xa4',
            'cp1250' : b'\x8C',
            'cp1251' : b'\xc0',
            'cp1252' : b'\xc0',
            'cp1253' : b'\xc1',
            'cp1254' : b'\xc0',
            'cp1255' : b'\xe0',
            'cp1256' : b'\xe0',
            'cp1257' : b'\xc0',
            'cp1258' : b'\xc0',
            }

        jeżeli sys.platform == 'darwin':
            self.assertEqual(fs_encoding, 'utf-8')
            # Mac OS X uses the Normal Form D decomposition
            # http://developer.apple.com/mac/library/qa/qa2001/qa1173.html
            special_char = b'a\xcc\x88'
        inaczej:
            special_char = known_locales.get(fs_encoding)

        jeżeli nie special_char:
            self.skipTest("can't run this test przy %s jako filesystem encoding"
                          % fs_encoding)
        decoded_char = special_char.decode(fs_encoding)
        temp_mod_name = 'test_imp_helper_' + decoded_char
        test_package_name = 'test_imp_helper_package_' + decoded_char
        init_file_name = os.path.join(test_package_name, '__init__.py')
        spróbuj:
            # jeżeli the curdir jest nie w sys.path the test fails when run with
            # ./python ./Lib/test/regrtest.py test_imp
            sys.path.insert(0, os.curdir)
            przy open(temp_mod_name + '.py', 'w') jako file:
                file.write('a = 1\n')
            file, filename, info = imp.find_module(temp_mod_name)
            przy file:
                self.assertIsNotNic(file)
                self.assertPrawda(filename[:-3].endswith(temp_mod_name))
                self.assertEqual(info[0], '.py')
                self.assertEqual(info[1], 'r')
                self.assertEqual(info[2], imp.PY_SOURCE)

                mod = imp.load_module(temp_mod_name, file, filename, info)
                self.assertEqual(mod.a, 1)

            przy warnings.catch_warnings():
                warnings.simplefilter('ignore')
                mod = imp.load_source(temp_mod_name, temp_mod_name + '.py')
            self.assertEqual(mod.a, 1)

            przy warnings.catch_warnings():
                warnings.simplefilter('ignore')
                jeżeli nie sys.dont_write_bytecode:
                    mod = imp.load_compiled(
                        temp_mod_name,
                        imp.cache_from_source(temp_mod_name + '.py'))
            self.assertEqual(mod.a, 1)

            jeżeli nie os.path.exists(test_package_name):
                os.mkdir(test_package_name)
            przy open(init_file_name, 'w') jako file:
                file.write('b = 2\n')
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore')
                package = imp.load_package(test_package_name, test_package_name)
            self.assertEqual(package.b, 2)
        w_końcu:
            usuń sys.path[0]
            dla ext w ('.py', '.pyc'):
                support.unlink(temp_mod_name + ext)
                support.unlink(init_file_name + ext)
            support.rmtree(test_package_name)
            support.rmtree('__pycache__')

    def test_issue9319(self):
        path = os.path.dirname(__file__)
        self.assertRaises(SyntaxError,
                          imp.find_module, "badsyntax_pep3120", [path])

    def test_load_from_source(self):
        # Verify that the imp module can correctly load oraz find .py files
        # XXX (ncoghlan): It would be nice to use support.CleanImport
        # here, but that przerwijs because the os module registers some
        # handlers w copy_reg on import. Since CleanImport doesn't
        # revert that registration, the module jest left w a broken
        # state after reversion. Reinitialising the module contents
        # oraz just reverting os.environ to its previous state jest an OK
        # workaround
        orig_path = os.path
        orig_getenv = os.getenv
        przy support.EnvironmentVarGuard():
            x = imp.find_module("os")
            self.addCleanup(x[0].close)
            new_os = imp.load_module("os", *x)
            self.assertIs(os, new_os)
            self.assertIs(orig_path, new_os.path)
            self.assertIsNot(orig_getenv, new_os.getenv)

    @requires_load_dynamic
    def test_issue15828_load_extensions(self):
        # Issue 15828 picked up that the adapter between the old imp API
        # oraz importlib couldn't handle C extensions
        example = "_heapq"
        x = imp.find_module(example)
        file_ = x[0]
        jeżeli file_ jest nie Nic:
            self.addCleanup(file_.close)
        mod = imp.load_module(example, *x)
        self.assertEqual(mod.__name__, example)

    @requires_load_dynamic
    def test_issue16421_multiple_modules_in_one_dll(self):
        # Issue 16421: loading several modules z the same compiled file fails
        m = '_testimportmultiple'
        fileobj, pathname, description = imp.find_module(m)
        fileobj.close()
        mod0 = imp.load_dynamic(m, pathname)
        mod1 = imp.load_dynamic('_testimportmultiple_foo', pathname)
        mod2 = imp.load_dynamic('_testimportmultiple_bar', pathname)
        self.assertEqual(mod0.__name__, m)
        self.assertEqual(mod1.__name__, '_testimportmultiple_foo')
        self.assertEqual(mod2.__name__, '_testimportmultiple_bar')
        przy self.assertRaises(ImportError):
            imp.load_dynamic('nonexistent', pathname)

    @requires_load_dynamic
    def test_load_dynamic_ImportError_path(self):
        # Issue #1559549 added `name` oraz `path` attributes to ImportError
        # w order to provide better detail. Issue #10854 implemented those
        # attributes on zaimportuj failures of extensions on Windows.
        path = 'bogus file path'
        name = 'extension'
        przy self.assertRaises(ImportError) jako err:
            imp.load_dynamic(name, path)
        self.assertIn(path, err.exception.path)
        self.assertEqual(name, err.exception.name)

    @requires_load_dynamic
    def test_load_module_extension_file_is_Nic(self):
        # When loading an extension module oraz the file jest Nic, open one
        # on the behalf of imp.load_dynamic().
        # Issue #15902
        name = '_testimportmultiple'
        found = imp.find_module(name)
        jeżeli found[0] jest nie Nic:
            found[0].close()
        jeżeli found[2][2] != imp.C_EXTENSION:
            self.skipTest("found module doesn't appear to be a C extension")
        imp.load_module(name, Nic, *found[1:])

    @requires_load_dynamic
    def test_issue24748_load_module_skips_sys_modules_check(self):
        name = 'test.imp_dummy'
        spróbuj:
            usuń sys.modules[name]
        wyjąwszy KeyError:
            dalej
        spróbuj:
            module = importlib.import_module(name)
            spec = importlib.util.find_spec('_testmultiphase')
            module = imp.load_dynamic(name, spec.origin)
            self.assertEqual(module.__name__, name)
            self.assertEqual(module.__spec__.name, name)
            self.assertEqual(module.__spec__.origin, spec.origin)
            self.assertRaises(AttributeError, getattr, module, 'dummy_name')
            self.assertEqual(module.int_const, 1969)
            self.assertIs(sys.modules[name], module)
        w_końcu:
            spróbuj:
                usuń sys.modules[name]
            wyjąwszy KeyError:
                dalej

    @unittest.skipIf(sys.dont_write_bytecode,
        "test meaningful only when writing bytecode")
    def test_bug7732(self):
        przy support.temp_cwd():
            source = support.TESTFN + '.py'
            os.mkdir(source)
            self.assertRaisesRegex(ImportError, '^No module',
                imp.find_module, support.TESTFN, ["."])

    def test_multiple_calls_to_get_data(self):
        # Issue #18755: make sure multiple calls to get_data() can succeed.
        loader = imp._LoadSourceCompatibility('imp', imp.__file__,
                                              open(imp.__file__))
        loader.get_data(imp.__file__)  # File should be closed
        loader.get_data(imp.__file__)  # Will need to create a newly opened file


klasa ReloadTests(unittest.TestCase):

    """Very basic tests to make sure that imp.reload() operates just like
    reload()."""

    def test_source(self):
        # XXX (ncoghlan): It would be nice to use test.support.CleanImport
        # here, but that przerwijs because the os module registers some
        # handlers w copy_reg on import. Since CleanImport doesn't
        # revert that registration, the module jest left w a broken
        # state after reversion. Reinitialising the module contents
        # oraz just reverting os.environ to its previous state jest an OK
        # workaround
        przy support.EnvironmentVarGuard():
            zaimportuj os
            imp.reload(os)

    def test_extension(self):
        przy support.CleanImport('time'):
            zaimportuj time
            imp.reload(time)

    def test_builtin(self):
        przy support.CleanImport('marshal'):
            zaimportuj marshal
            imp.reload(marshal)

    def test_with_deleted_parent(self):
        # see #18681
        z html zaimportuj parser
        html = sys.modules.pop('html')
        def cleanup():
            sys.modules['html'] = html
        self.addCleanup(cleanup)
        przy self.assertRaisesRegex(ImportError, 'html'):
            imp.reload(parser)


klasa PEP3147Tests(unittest.TestCase):
    """Tests of PEP 3147."""

    tag = imp.get_tag()

    @unittest.skipUnless(sys.implementation.cache_tag jest nie Nic,
                         'requires sys.implementation.cache_tag nie be Nic')
    def test_cache_from_source(self):
        # Given the path to a .py file, zwróć the path to its PEP 3147
        # defined .pyc file (i.e. under __pycache__).
        path = os.path.join('foo', 'bar', 'baz', 'qux.py')
        expect = os.path.join('foo', 'bar', 'baz', '__pycache__',
                              'qux.{}.pyc'.format(self.tag))
        self.assertEqual(imp.cache_from_source(path, Prawda), expect)

    @unittest.skipUnless(sys.implementation.cache_tag jest nie Nic,
                         'requires sys.implementation.cache_tag to nie be '
                         'Nic')
    def test_source_from_cache(self):
        # Given the path to a PEP 3147 defined .pyc file, zwróć the path to
        # its source.  This tests the good path.
        path = os.path.join('foo', 'bar', 'baz', '__pycache__',
                            'qux.{}.pyc'.format(self.tag))
        expect = os.path.join('foo', 'bar', 'baz', 'qux.py')
        self.assertEqual(imp.source_from_cache(path), expect)


klasa NullImporterTests(unittest.TestCase):
    @unittest.skipIf(support.TESTFN_UNENCODABLE jest Nic,
                     "Need an undecodeable filename")
    def test_unencodeable(self):
        name = support.TESTFN_UNENCODABLE
        os.mkdir(name)
        spróbuj:
            self.assertRaises(ImportError, imp.NullImporter, name)
        w_końcu:
            os.rmdir(name)


jeżeli __name__ == "__main__":
    unittest.main()
