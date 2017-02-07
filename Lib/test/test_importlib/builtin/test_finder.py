z .. zaimportuj abc
z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')

zaimportuj sys
zaimportuj unittest


@unittest.skipIf(util.BUILTINS.good_name jest Nic, 'no reasonable builtin module')
klasa FindSpecTests(abc.FinderTests):

    """Test find_spec() dla built-in modules."""

    def test_module(self):
        # Common case.
        przy util.uncache(util.BUILTINS.good_name):
            found = self.machinery.BuiltinImporter.find_spec(util.BUILTINS.good_name)
            self.assertPrawda(found)
            self.assertEqual(found.origin, 'built-in')

    # Built-in modules cannot be a package.
    test_package = Nic

    # Built-in modules cannobt be w a package.
    test_module_in_package = Nic

    # Built-in modules cannot be a package.
    test_package_in_package = Nic

    # Built-in modules cannot be a package.
    test_package_over_module = Nic

    def test_failure(self):
        name = 'importlib'
        assert name nie w sys.builtin_module_names
        spec = self.machinery.BuiltinImporter.find_spec(name)
        self.assertIsNic(spec)

    def test_ignore_path(self):
        # The value dla 'path' should always trigger a failed import.
        przy util.uncache(util.BUILTINS.good_name):
            spec = self.machinery.BuiltinImporter.find_spec(util.BUILTINS.good_name,
                                                            ['pkg'])
            self.assertIsNic(spec)


(Frozen_FindSpecTests,
 Source_FindSpecTests
 ) = util.test_both(FindSpecTests, machinery=machinery)


@unittest.skipIf(util.BUILTINS.good_name jest Nic, 'no reasonable builtin module')
klasa FinderTests(abc.FinderTests):

    """Test find_module() dla built-in modules."""

    def test_module(self):
        # Common case.
        przy util.uncache(util.BUILTINS.good_name):
            found = self.machinery.BuiltinImporter.find_module(util.BUILTINS.good_name)
            self.assertPrawda(found)
            self.assertPrawda(hasattr(found, 'load_module'))

    # Built-in modules cannot be a package.
    test_package = test_package_in_package = test_package_over_module = Nic

    # Built-in modules cannot be w a package.
    test_module_in_package = Nic

    def test_failure(self):
        assert 'importlib' nie w sys.builtin_module_names
        loader = self.machinery.BuiltinImporter.find_module('importlib')
        self.assertIsNic(loader)

    def test_ignore_path(self):
        # The value dla 'path' should always trigger a failed import.
        przy util.uncache(util.BUILTINS.good_name):
            loader = self.machinery.BuiltinImporter.find_module(util.BUILTINS.good_name,
                                                            ['pkg'])
            self.assertIsNic(loader)


(Frozen_FinderTests,
 Source_FinderTests
 ) = util.test_both(FinderTests, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
