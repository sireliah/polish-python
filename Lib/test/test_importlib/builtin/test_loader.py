z .. zaimportuj abc
z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')

zaimportuj sys
zaimportuj types
zaimportuj unittest

@unittest.skipIf(util.BUILTINS.good_name jest Nic, 'no reasonable builtin module')
klasa LoaderTests(abc.LoaderTests):

    """Test load_module() dla built-in modules."""

    def setUp(self):
        self.verification = {'__name__': 'errno', '__package__': '',
                             '__loader__': self.machinery.BuiltinImporter}

    def verify(self, module):
        """Verify that the module matches against what it should have."""
        self.assertIsInstance(module, types.ModuleType)
        dla attr, value w self.verification.items():
            self.assertEqual(getattr(module, attr), value)
        self.assertIn(module.__name__, sys.modules)

    def load_module(self, name):
        zwróć self.machinery.BuiltinImporter.load_module(name)

    def test_module(self):
        # Common case.
        przy util.uncache(util.BUILTINS.good_name):
            module = self.load_module(util.BUILTINS.good_name)
            self.verify(module)

    # Built-in modules cannot be a package.
    test_package = test_lacking_parent = Nic

    # No way to force an zaimportuj failure.
    test_state_after_failure = Nic

    def test_module_reuse(self):
        # Test that the same module jest used w a reload.
        przy util.uncache(util.BUILTINS.good_name):
            module1 = self.load_module(util.BUILTINS.good_name)
            module2 = self.load_module(util.BUILTINS.good_name)
            self.assertIs(module1, module2)

    def test_unloadable(self):
        name = 'dssdsdfff'
        assert name nie w sys.builtin_module_names
        przy self.assertRaises(ImportError) jako cm:
            self.load_module(name)
        self.assertEqual(cm.exception.name, name)

    def test_already_imported(self):
        # Using the name of a module already imported but nie a built-in should
        # still fail.
        module_name = 'builtin_reload_test'
        assert module_name nie w sys.builtin_module_names
        przy util.uncache(module_name):
            module = types.ModuleType(module_name)
            sys.modules[module_name] = module
        przy self.assertRaises(ImportError) jako cm:
            self.load_module(module_name)
        self.assertEqual(cm.exception.name, module_name)


(Frozen_LoaderTests,
 Source_LoaderTests
 ) = util.test_both(LoaderTests, machinery=machinery)


@unittest.skipIf(util.BUILTINS.good_name jest Nic, 'no reasonable builtin module')
klasa InspectLoaderTests:

    """Tests dla InspectLoader methods dla BuiltinImporter."""

    def test_get_code(self):
        # There jest no code object.
        result = self.machinery.BuiltinImporter.get_code(util.BUILTINS.good_name)
        self.assertIsNic(result)

    def test_get_source(self):
        # There jest no source.
        result = self.machinery.BuiltinImporter.get_source(util.BUILTINS.good_name)
        self.assertIsNic(result)

    def test_is_package(self):
        # Cannot be a package.
        result = self.machinery.BuiltinImporter.is_package(util.BUILTINS.good_name)
        self.assertNieprawda(result)

    @unittest.skipIf(util.BUILTINS.bad_name jest Nic, 'all modules are built in')
    def test_not_builtin(self):
        # Modules nie built-in should podnieś ImportError.
        dla meth_name w ('get_code', 'get_source', 'is_package'):
            method = getattr(self.machinery.BuiltinImporter, meth_name)
        przy self.assertRaises(ImportError) jako cm:
            method(util.BUILTINS.bad_name)


(Frozen_InspectLoaderTests,
 Source_InspectLoaderTests
 ) = util.test_both(InspectLoaderTests, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
