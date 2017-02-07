z .. zaimportuj abc
z .. zaimportuj util

importlib = util.import_importlib('importlib')
importlib_abc = util.import_importlib('importlib.abc')
machinery = util.import_importlib('importlib.machinery')
importlib_util = util.import_importlib('importlib.util')

zaimportuj errno
zaimportuj marshal
zaimportuj os
zaimportuj py_compile
zaimportuj shutil
zaimportuj stat
zaimportuj sys
zaimportuj types
zaimportuj unittest
zaimportuj warnings

z test.support zaimportuj make_legacy_pyc, unload


klasa SimpleTest(abc.LoaderTests):

    """Should have no issue importing a source module [basic]. And jeżeli there jest
    a syntax error, it should podnieś a SyntaxError [syntax error].

    """

    def setUp(self):
        self.name = 'spam'
        self.filepath = os.path.join('ham', self.name + '.py')
        self.loader = self.machinery.SourceFileLoader(self.name, self.filepath)

    def test_load_module_API(self):
        klasa Tester(self.abc.FileLoader):
            def get_source(self, _): zwróć 'attr = 42'
            def is_package(self, _): zwróć Nieprawda

        loader = Tester('blah', 'blah.py')
        self.addCleanup(unload, 'blah')
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            module = loader.load_module()  # Should nie podnieś an exception.

    def test_get_filename_API(self):
        # If fullname jest nie set then assume self.path jest desired.
        klasa Tester(self.abc.FileLoader):
            def get_code(self, _): dalej
            def get_source(self, _): dalej
            def is_package(self, _): dalej
            def module_repr(self, _): dalej

        path = 'some_path'
        name = 'some_name'
        loader = Tester(name, path)
        self.assertEqual(path, loader.get_filename(name))
        self.assertEqual(path, loader.get_filename())
        self.assertEqual(path, loader.get_filename(Nic))
        przy self.assertRaises(ImportError):
            loader.get_filename(name + 'XXX')

    def test_equality(self):
        other = self.machinery.SourceFileLoader(self.name, self.filepath)
        self.assertEqual(self.loader, other)

    def test_inequality(self):
        other = self.machinery.SourceFileLoader('_' + self.name, self.filepath)
        self.assertNotEqual(self.loader, other)

    # [basic]
    def test_module(self):
        przy util.create_modules('_temp') jako mapping:
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_temp')
            self.assertIn('_temp', sys.modules)
            check = {'__name__': '_temp', '__file__': mapping['_temp'],
                     '__package__': ''}
            dla attr, value w check.items():
                self.assertEqual(getattr(module, attr), value)

    def test_package(self):
        przy util.create_modules('_pkg.__init__') jako mapping:
            loader = self.machinery.SourceFileLoader('_pkg',
                                                 mapping['_pkg.__init__'])
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_pkg')
            self.assertIn('_pkg', sys.modules)
            check = {'__name__': '_pkg', '__file__': mapping['_pkg.__init__'],
                     '__path__': [os.path.dirname(mapping['_pkg.__init__'])],
                     '__package__': '_pkg'}
            dla attr, value w check.items():
                self.assertEqual(getattr(module, attr), value)


    def test_lacking_parent(self):
        przy util.create_modules('_pkg.__init__', '_pkg.mod')as mapping:
            loader = self.machinery.SourceFileLoader('_pkg.mod',
                                                    mapping['_pkg.mod'])
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_pkg.mod')
            self.assertIn('_pkg.mod', sys.modules)
            check = {'__name__': '_pkg.mod', '__file__': mapping['_pkg.mod'],
                     '__package__': '_pkg'}
            dla attr, value w check.items():
                self.assertEqual(getattr(module, attr), value)

    def fake_mtime(self, fxn):
        """Fake mtime to always be higher than expected."""
        zwróć lambda name: fxn(name) + 1

    def test_module_reuse(self):
        przy util.create_modules('_temp') jako mapping:
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_temp')
            module_id = id(module)
            module_dict_id = id(module.__dict__)
            przy open(mapping['_temp'], 'w') jako file:
                file.write("testing_var = 42\n")
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_temp')
            self.assertIn('testing_var', module.__dict__,
                         "'testing_var' nie w "
                            "{0}".format(list(module.__dict__.keys())))
            self.assertEqual(module, sys.modules['_temp'])
            self.assertEqual(id(module), module_id)
            self.assertEqual(id(module.__dict__), module_dict_id)

    def test_state_after_failure(self):
        # A failed reload should leave the original module intact.
        attributes = ('__file__', '__path__', '__package__')
        value = '<test>'
        name = '_temp'
        przy util.create_modules(name) jako mapping:
            orig_module = types.ModuleType(name)
            dla attr w attributes:
                setattr(orig_module, attr, value)
            przy open(mapping[name], 'w') jako file:
                file.write('+++ bad syntax +++')
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            przy self.assertRaises(SyntaxError):
                loader.exec_module(orig_module)
            dla attr w attributes:
                self.assertEqual(getattr(orig_module, attr), value)
            przy self.assertRaises(SyntaxError):
                przy warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    loader.load_module(name)
            dla attr w attributes:
                self.assertEqual(getattr(orig_module, attr), value)

    # [syntax error]
    def test_bad_syntax(self):
        przy util.create_modules('_temp') jako mapping:
            przy open(mapping['_temp'], 'w') jako file:
                file.write('=')
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            przy self.assertRaises(SyntaxError):
                przy warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    loader.load_module('_temp')
            self.assertNotIn('_temp', sys.modules)

    def test_file_from_empty_string_dir(self):
        # Loading a module found z an empty string entry on sys.path should
        # nie only work, but keep all attributes relative.
        file_path = '_temp.py'
        przy open(file_path, 'w') jako file:
            file.write("# test file dla importlib")
        spróbuj:
            przy util.uncache('_temp'):
                loader = self.machinery.SourceFileLoader('_temp', file_path)
                przy warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    mod = loader.load_module('_temp')
                self.assertEqual(file_path, mod.__file__)
                self.assertEqual(self.util.cache_from_source(file_path),
                                 mod.__cached__)
        w_końcu:
            os.unlink(file_path)
            pycache = os.path.dirname(self.util.cache_from_source(file_path))
            jeżeli os.path.exists(pycache):
                shutil.rmtree(pycache)

    @util.writes_bytecode_files
    def test_timestamp_overflow(self):
        # When a modification timestamp jest larger than 2**32, it should be
        # truncated rather than podnieś an OverflowError.
        przy util.create_modules('_temp') jako mapping:
            source = mapping['_temp']
            compiled = self.util.cache_from_source(source)
            przy open(source, 'w') jako f:
                f.write("x = 5")
            spróbuj:
                os.utime(source, (2 ** 33 - 5, 2 ** 33 - 5))
            wyjąwszy OverflowError:
                self.skipTest("cannot set modification time to large integer")
            wyjąwszy OSError jako e:
                jeżeli e.errno != getattr(errno, 'EOVERFLOW', Nic):
                    podnieś
                self.skipTest("cannot set modification time to large integer ({})".format(e))
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            # PEP 451
            module = types.ModuleType('_temp')
            module.__spec__ = self.util.spec_from_loader('_temp', loader)
            loader.exec_module(module)
            self.assertEqual(module.x, 5)
            self.assertPrawda(os.path.exists(compiled))
            os.unlink(compiled)
            # PEP 302
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                mod = loader.load_module('_temp') # XXX
            # Sanity checks.
            self.assertEqual(mod.__cached__, compiled)
            self.assertEqual(mod.x, 5)
            # The pyc file was created.
            self.assertPrawda(os.path.exists(compiled))

    def test_unloadable(self):
        loader = self.machinery.SourceFileLoader('good name', {})
        module = types.ModuleType('bad name')
        module.__spec__ = self.machinery.ModuleSpec('bad name', loader)
        przy self.assertRaises(ImportError):
            loader.exec_module(module)
        przy self.assertRaises(ImportError):
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                loader.load_module('bad name')


(Frozen_SimpleTest,
 Source_SimpleTest
 ) = util.test_both(SimpleTest, importlib=importlib, machinery=machinery,
                    abc=importlib_abc, util=importlib_util)


klasa BadBytecodeTest:

    def import_(self, file, module_name):
        loader = self.loader(module_name, file)
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            # XXX Change to use exec_module().
            module = loader.load_module(module_name)
        self.assertIn(module_name, sys.modules)

    def manipulate_bytecode(self, name, mapping, manipulator, *,
                            del_source=Nieprawda):
        """Manipulate the bytecode of a module by dalejing it into a callable
        that returns what to use jako the new bytecode."""
        spróbuj:
            usuń sys.modules['_temp']
        wyjąwszy KeyError:
            dalej
        py_compile.compile(mapping[name])
        jeżeli nie del_source:
            bytecode_path = self.util.cache_from_source(mapping[name])
        inaczej:
            os.unlink(mapping[name])
            bytecode_path = make_legacy_pyc(mapping[name])
        jeżeli manipulator:
            przy open(bytecode_path, 'rb') jako file:
                bc = file.read()
                new_bc = manipulator(bc)
            przy open(bytecode_path, 'wb') jako file:
                jeżeli new_bc jest nie Nic:
                    file.write(new_bc)
        zwróć bytecode_path

    def _test_empty_file(self, test, *, del_source=Nieprawda):
        przy util.create_modules('_temp') jako mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: b'',
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    @util.writes_bytecode_files
    def _test_partial_magic(self, test, *, del_source=Nieprawda):
        # When their are less than 4 bytes to a .pyc, regenerate it if
        # possible, inaczej podnieś ImportError.
        przy util.create_modules('_temp') jako mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:3],
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    def _test_magic_only(self, test, *, del_source=Nieprawda):
        przy util.create_modules('_temp') jako mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:4],
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    def _test_partial_timestamp(self, test, *, del_source=Nieprawda):
        przy util.create_modules('_temp') jako mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:7],
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    def _test_partial_size(self, test, *, del_source=Nieprawda):
        przy util.create_modules('_temp') jako mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:11],
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    def _test_no_marshal(self, *, del_source=Nieprawda):
        przy util.create_modules('_temp') jako mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:12],
                                                del_source=del_source)
            file_path = mapping['_temp'] jeżeli nie del_source inaczej bc_path
            przy self.assertRaises(EOFError):
                self.import_(file_path, '_temp')

    def _test_non_code_marshal(self, *, del_source=Nieprawda):
        przy util.create_modules('_temp') jako mapping:
            bytecode_path = self.manipulate_bytecode('_temp', mapping,
                                    lambda bc: bc[:12] + marshal.dumps(b'abcd'),
                                    del_source=del_source)
            file_path = mapping['_temp'] jeżeli nie del_source inaczej bytecode_path
            przy self.assertRaises(ImportError) jako cm:
                self.import_(file_path, '_temp')
            self.assertEqual(cm.exception.name, '_temp')
            self.assertEqual(cm.exception.path, bytecode_path)

    def _test_bad_marshal(self, *, del_source=Nieprawda):
        przy util.create_modules('_temp') jako mapping:
            bytecode_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:12] + b'<test>',
                                                del_source=del_source)
            file_path = mapping['_temp'] jeżeli nie del_source inaczej bytecode_path
            przy self.assertRaises(EOFError):
                self.import_(file_path, '_temp')

    def _test_bad_magic(self, test, *, del_source=Nieprawda):
        przy util.create_modules('_temp') jako mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                    lambda bc: b'\x00\x00\x00\x00' + bc[4:])
            test('_temp', mapping, bc_path)


klasa BadBytecodeTestPEP451(BadBytecodeTest):

    def import_(self, file, module_name):
        loader = self.loader(module_name, file)
        module = types.ModuleType(module_name)
        module.__spec__ = self.util.spec_from_loader(module_name, loader)
        loader.exec_module(module)


klasa BadBytecodeTestPEP302(BadBytecodeTest):

    def import_(self, file, module_name):
        loader = self.loader(module_name, file)
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            module = loader.load_module(module_name)
        self.assertIn(module_name, sys.modules)


klasa SourceLoaderBadBytecodeTest:

    @classmethod
    def setUpClass(cls):
        cls.loader = cls.machinery.SourceFileLoader

    @util.writes_bytecode_files
    def test_empty_file(self):
        # When a .pyc jest empty, regenerate it jeżeli possible, inaczej podnieś
        # ImportError.
        def test(name, mapping, bytecode_path):
            self.import_(mapping[name], name)
            przy open(bytecode_path, 'rb') jako file:
                self.assertGreater(len(file.read()), 12)

        self._test_empty_file(test)

    def test_partial_magic(self):
        def test(name, mapping, bytecode_path):
            self.import_(mapping[name], name)
            przy open(bytecode_path, 'rb') jako file:
                self.assertGreater(len(file.read()), 12)

        self._test_partial_magic(test)

    @util.writes_bytecode_files
    def test_magic_only(self):
        # When there jest only the magic number, regenerate the .pyc jeżeli possible,
        # inaczej podnieś EOFError.
        def test(name, mapping, bytecode_path):
            self.import_(mapping[name], name)
            przy open(bytecode_path, 'rb') jako file:
                self.assertGreater(len(file.read()), 12)

        self._test_magic_only(test)

    @util.writes_bytecode_files
    def test_bad_magic(self):
        # When the magic number jest different, the bytecode should be
        # regenerated.
        def test(name, mapping, bytecode_path):
            self.import_(mapping[name], name)
            przy open(bytecode_path, 'rb') jako bytecode_file:
                self.assertEqual(bytecode_file.read(4),
                                 self.util.MAGIC_NUMBER)

        self._test_bad_magic(test)

    @util.writes_bytecode_files
    def test_partial_timestamp(self):
        # When the timestamp jest partial, regenerate the .pyc, inaczej
        # podnieś EOFError.
        def test(name, mapping, bc_path):
            self.import_(mapping[name], name)
            przy open(bc_path, 'rb') jako file:
                self.assertGreater(len(file.read()), 12)

        self._test_partial_timestamp(test)

    @util.writes_bytecode_files
    def test_partial_size(self):
        # When the size jest partial, regenerate the .pyc, inaczej
        # podnieś EOFError.
        def test(name, mapping, bc_path):
            self.import_(mapping[name], name)
            przy open(bc_path, 'rb') jako file:
                self.assertGreater(len(file.read()), 12)

        self._test_partial_size(test)

    @util.writes_bytecode_files
    def test_no_marshal(self):
        # When there jest only the magic number oraz timestamp, podnieś EOFError.
        self._test_no_marshal()

    @util.writes_bytecode_files
    def test_non_code_marshal(self):
        self._test_non_code_marshal()
        # XXX ImportError when sourceless

    # [bad marshal]
    @util.writes_bytecode_files
    def test_bad_marshal(self):
        # Bad marshal data should podnieś a ValueError.
        self._test_bad_marshal()

    # [bad timestamp]
    @util.writes_bytecode_files
    def test_old_timestamp(self):
        # When the timestamp jest older than the source, bytecode should be
        # regenerated.
        zeros = b'\x00\x00\x00\x00'
        przy util.create_modules('_temp') jako mapping:
            py_compile.compile(mapping['_temp'])
            bytecode_path = self.util.cache_from_source(mapping['_temp'])
            przy open(bytecode_path, 'r+b') jako bytecode_file:
                bytecode_file.seek(4)
                bytecode_file.write(zeros)
            self.import_(mapping['_temp'], '_temp')
            source_mtime = os.path.getmtime(mapping['_temp'])
            source_timestamp = self.importlib._w_long(source_mtime)
            przy open(bytecode_path, 'rb') jako bytecode_file:
                bytecode_file.seek(4)
                self.assertEqual(bytecode_file.read(4), source_timestamp)

    # [bytecode read-only]
    @util.writes_bytecode_files
    def test_read_only_bytecode(self):
        # When bytecode jest read-only but should be rewritten, fail silently.
        przy util.create_modules('_temp') jako mapping:
            # Create bytecode that will need to be re-created.
            py_compile.compile(mapping['_temp'])
            bytecode_path = self.util.cache_from_source(mapping['_temp'])
            przy open(bytecode_path, 'r+b') jako bytecode_file:
                bytecode_file.seek(0)
                bytecode_file.write(b'\x00\x00\x00\x00')
            # Make the bytecode read-only.
            os.chmod(bytecode_path,
                        stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            spróbuj:
                # Should nie podnieś OSError!
                self.import_(mapping['_temp'], '_temp')
            w_końcu:
                # Make writable dla eventual clean-up.
                os.chmod(bytecode_path, stat.S_IWUSR)


klasa SourceLoaderBadBytecodeTestPEP451(
        SourceLoaderBadBytecodeTest, BadBytecodeTestPEP451):
    dalej


(Frozen_SourceBadBytecodePEP451,
 Source_SourceBadBytecodePEP451
 ) = util.test_both(SourceLoaderBadBytecodeTestPEP451, importlib=importlib,
                    machinery=machinery, abc=importlib_abc,
                    util=importlib_util)


klasa SourceLoaderBadBytecodeTestPEP302(
        SourceLoaderBadBytecodeTest, BadBytecodeTestPEP302):
    dalej


(Frozen_SourceBadBytecodePEP302,
 Source_SourceBadBytecodePEP302
 ) = util.test_both(SourceLoaderBadBytecodeTestPEP302, importlib=importlib,
                    machinery=machinery, abc=importlib_abc,
                    util=importlib_util)


klasa SourcelessLoaderBadBytecodeTest:

    @classmethod
    def setUpClass(cls):
        cls.loader = cls.machinery.SourcelessFileLoader

    def test_empty_file(self):
        def test(name, mapping, bytecode_path):
            przy self.assertRaises(ImportError) jako cm:
                self.import_(bytecode_path, name)
            self.assertEqual(cm.exception.name, name)
            self.assertEqual(cm.exception.path, bytecode_path)

        self._test_empty_file(test, del_source=Prawda)

    def test_partial_magic(self):
        def test(name, mapping, bytecode_path):
            przy self.assertRaises(ImportError) jako cm:
                self.import_(bytecode_path, name)
            self.assertEqual(cm.exception.name, name)
            self.assertEqual(cm.exception.path, bytecode_path)
        self._test_partial_magic(test, del_source=Prawda)

    def test_magic_only(self):
        def test(name, mapping, bytecode_path):
            przy self.assertRaises(EOFError):
                self.import_(bytecode_path, name)

        self._test_magic_only(test, del_source=Prawda)

    def test_bad_magic(self):
        def test(name, mapping, bytecode_path):
            przy self.assertRaises(ImportError) jako cm:
                self.import_(bytecode_path, name)
            self.assertEqual(cm.exception.name, name)
            self.assertEqual(cm.exception.path, bytecode_path)

        self._test_bad_magic(test, del_source=Prawda)

    def test_partial_timestamp(self):
        def test(name, mapping, bytecode_path):
            przy self.assertRaises(EOFError):
                self.import_(bytecode_path, name)

        self._test_partial_timestamp(test, del_source=Prawda)

    def test_partial_size(self):
        def test(name, mapping, bytecode_path):
            przy self.assertRaises(EOFError):
                self.import_(bytecode_path, name)

        self._test_partial_size(test, del_source=Prawda)

    def test_no_marshal(self):
        self._test_no_marshal(del_source=Prawda)

    def test_non_code_marshal(self):
        self._test_non_code_marshal(del_source=Prawda)


klasa SourcelessLoaderBadBytecodeTestPEP451(SourcelessLoaderBadBytecodeTest,
        BadBytecodeTestPEP451):
    dalej


(Frozen_SourcelessBadBytecodePEP451,
 Source_SourcelessBadBytecodePEP451
 ) = util.test_both(SourcelessLoaderBadBytecodeTestPEP451, importlib=importlib,
                    machinery=machinery, abc=importlib_abc,
                    util=importlib_util)


klasa SourcelessLoaderBadBytecodeTestPEP302(SourcelessLoaderBadBytecodeTest,
        BadBytecodeTestPEP302):
    dalej


(Frozen_SourcelessBadBytecodePEP302,
 Source_SourcelessBadBytecodePEP302
 ) = util.test_both(SourcelessLoaderBadBytecodeTestPEP302, importlib=importlib,
                    machinery=machinery, abc=importlib_abc,
                    util=importlib_util)


jeżeli __name__ == '__main__':
    unittest.main()
