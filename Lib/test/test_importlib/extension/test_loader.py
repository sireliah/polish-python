z .. zaimportuj abc
z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')

zaimportuj os.path
zaimportuj sys
zaimportuj types
zaimportuj unittest
zaimportuj importlib.util
zaimportuj importlib


klasa LoaderTests(abc.LoaderTests):

    """Test load_module() dla extension modules."""

    def setUp(self):
        self.loader = self.machinery.ExtensionFileLoader(util.EXTENSIONS.name,
                                                         util.EXTENSIONS.file_path)

    def load_module(self, fullname):
        zwróć self.loader.load_module(fullname)

    def test_load_module_API(self):
        # Test the default argument dla load_module().
        self.loader.load_module()
        self.loader.load_module(Nic)
        przy self.assertRaises(ImportError):
            self.load_module('XXX')

    def test_equality(self):
        other = self.machinery.ExtensionFileLoader(util.EXTENSIONS.name,
                                                   util.EXTENSIONS.file_path)
        self.assertEqual(self.loader, other)

    def test_inequality(self):
        other = self.machinery.ExtensionFileLoader('_' + util.EXTENSIONS.name,
                                                   util.EXTENSIONS.file_path)
        self.assertNotEqual(self.loader, other)

    def test_module(self):
        przy util.uncache(util.EXTENSIONS.name):
            module = self.load_module(util.EXTENSIONS.name)
            dla attr, value w [('__name__', util.EXTENSIONS.name),
                                ('__file__', util.EXTENSIONS.file_path),
                                ('__package__', '')]:
                self.assertEqual(getattr(module, attr), value)
            self.assertIn(util.EXTENSIONS.name, sys.modules)
            self.assertIsInstance(module.__loader__,
                                  self.machinery.ExtensionFileLoader)

    # No extension module jako __init__ available dla testing.
    test_package = Nic

    # No extension module w a package available dla testing.
    test_lacking_parent = Nic

    def test_module_reuse(self):
        przy util.uncache(util.EXTENSIONS.name):
            module1 = self.load_module(util.EXTENSIONS.name)
            module2 = self.load_module(util.EXTENSIONS.name)
            self.assertIs(module1, module2)

    # No easy way to trigger a failure after a successful import.
    test_state_after_failure = Nic

    def test_unloadable(self):
        name = 'asdfjkl;'
        przy self.assertRaises(ImportError) jako cm:
            self.load_module(name)
        self.assertEqual(cm.exception.name, name)

    def test_is_package(self):
        self.assertNieprawda(self.loader.is_package(util.EXTENSIONS.name))
        dla suffix w self.machinery.EXTENSION_SUFFIXES:
            path = os.path.join('some', 'path', 'pkg', '__init__' + suffix)
            loader = self.machinery.ExtensionFileLoader('pkg', path)
            self.assertPrawda(loader.is_package('pkg'))

(Frozen_LoaderTests,
 Source_LoaderTests
 ) = util.test_both(LoaderTests, machinery=machinery)

klasa MultiPhaseExtensionModuleTests(abc.LoaderTests):
    """Test loading extension modules przy multi-phase initialization (PEP 489)
    """

    def setUp(self):
        self.name = '_testmultiphase'
        finder = self.machinery.FileFinder(Nic)
        self.spec = importlib.util.find_spec(self.name)
        assert self.spec
        self.loader = self.machinery.ExtensionFileLoader(
            self.name, self.spec.origin)

    # No extension module jako __init__ available dla testing.
    test_package = Nic

    # No extension module w a package available dla testing.
    test_lacking_parent = Nic

    # Handling failure on reload jest the up to the module.
    test_state_after_failure = Nic

    def test_module(self):
        '''Test loading an extension module'''
        przy util.uncache(self.name):
            module = self.load_module()
            dla attr, value w [('__name__', self.name),
                                ('__file__', self.spec.origin),
                                ('__package__', '')]:
                self.assertEqual(getattr(module, attr), value)
            przy self.assertRaises(AttributeError):
                module.__path__
            self.assertIs(module, sys.modules[self.name])
            self.assertIsInstance(module.__loader__,
                                  self.machinery.ExtensionFileLoader)

    def test_functionality(self):
        '''Test basic functionality of stuff defined w an extension module'''
        przy util.uncache(self.name):
            module = self.load_module()
            self.assertIsInstance(module, types.ModuleType)
            ex = module.Example()
            self.assertEqual(ex.demo('abcd'), 'abcd')
            self.assertEqual(ex.demo(), Nic)
            przy self.assertRaises(AttributeError):
                ex.abc
            ex.abc = 0
            self.assertEqual(ex.abc, 0)
            self.assertEqual(module.foo(9, 9), 18)
            self.assertIsInstance(module.Str(), str)
            self.assertEqual(module.Str(1) + '23', '123')
            przy self.assertRaises(module.error):
                podnieś module.error()
            self.assertEqual(module.int_const, 1969)
            self.assertEqual(module.str_const, 'something different')

    def test_reload(self):
        '''Test that reload didn't re-set the module's attributes'''
        przy util.uncache(self.name):
            module = self.load_module()
            ex_class = module.Example
            importlib.reload(module)
            self.assertIs(ex_class, module.Example)

    def test_try_registration(self):
        '''Assert that the PyState_{Find,Add,Remove}Module C API doesn't work'''
        module = self.load_module()
        przy self.subTest('PyState_FindModule'):
            self.assertEqual(module.call_state_registration_func(0), Nic)
        przy self.subTest('PyState_AddModule'):
            przy self.assertRaises(SystemError):
                module.call_state_registration_func(1)
        przy self.subTest('PyState_RemoveModule'):
            przy self.assertRaises(SystemError):
                module.call_state_registration_func(2)

    def load_module(self):
        '''Load the module z the test extension'''
        zwróć self.loader.load_module(self.name)

    def load_module_by_name(self, fullname):
        '''Load a module z the test extension by name'''
        origin = self.spec.origin
        loader = self.machinery.ExtensionFileLoader(fullname, origin)
        spec = importlib.util.spec_from_loader(fullname, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        zwróć module

    def test_load_submodule(self):
        '''Test loading a simulated submodule'''
        module = self.load_module_by_name('pkg.' + self.name)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, 'pkg.' + self.name)
        self.assertEqual(module.str_const, 'something different')

    def test_load_short_name(self):
        '''Test loading module przy a one-character name'''
        module = self.load_module_by_name('x')
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, 'x')
        self.assertEqual(module.str_const, 'something different')
        self.assertNotIn('x', sys.modules)

    def test_load_twice(self):
        '''Test that 2 loads result w 2 module objects'''
        module1 = self.load_module_by_name(self.name)
        module2 = self.load_module_by_name(self.name)
        self.assertIsNot(module1, module2)

    def test_unloadable(self):
        '''Test nonexistent module'''
        name = 'asdfjkl;'
        przy self.assertRaises(ImportError) jako cm:
            self.load_module_by_name(name)
        self.assertEqual(cm.exception.name, name)

    def test_unloadable_nonascii(self):
        '''Test behavior przy nonexistent module przy non-ASCII name'''
        name = 'fo\xf3'
        przy self.assertRaises(ImportError) jako cm:
            self.load_module_by_name(name)
        self.assertEqual(cm.exception.name, name)

    def test_nonmodule(self):
        '''Test returning a non-module object z create works'''
        name = self.name + '_nonmodule'
        mod = self.load_module_by_name(name)
        self.assertNotEqual(type(mod), type(unittest))
        self.assertEqual(mod.three, 3)

    def test_null_slots(self):
        '''Test that NULL slots aren't a problem'''
        name = self.name + '_null_slots'
        module = self.load_module_by_name(name)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, name)

    def test_bad_modules(self):
        '''Test SystemError jest podnieśd dla misbehaving extensions'''
        dla name_base w [
                'bad_slot_large',
                'bad_slot_negative',
                'create_int_with_state',
                'negative_size',
                'export_null',
                'export_uninitialized',
                'export_raise',
                'export_unreported_exception',
                'create_null',
                'create_raise',
                'create_unreported_exception',
                'nonmodule_with_exec_slots',
                'exec_err',
                'exec_raise',
                'exec_unreported_exception',
                ]:
            przy self.subTest(name_base):
                name = self.name + '_' + name_base
                przy self.assertRaises(SystemError):
                    self.load_module_by_name(name)

    def test_nonascii(self):
        '''Test that modules przy non-ASCII names can be loaded'''
        # punycode behaves slightly differently w some-ASCII oraz no-ASCII
        # cases, so test both
        cases = [
            (self.name + '_zkou\u0161ka_na\u010dten\xed', 'Czech'),
            ('\uff3f\u30a4\u30f3\u30dd\u30fc\u30c8\u30c6\u30b9\u30c8',
             'Japanese'),
            ]
        dla name, lang w cases:
            przy self.subTest(name):
                module = self.load_module_by_name(name)
                self.assertEqual(module.__name__, name)
                self.assertEqual(module.__doc__, "Module named w %s" % lang)


(Frozen_MultiPhaseExtensionModuleTests,
 Source_MultiPhaseExtensionModuleTests
 ) = util.test_both(MultiPhaseExtensionModuleTests, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
