z .. zaimportuj abc
z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')

zaimportuj unittest


klasa FindSpecTests(abc.FinderTests):

    """Test finding frozen modules."""

    def find(self, name, path=Nic):
        finder = self.machinery.FrozenImporter
        zwróć finder.find_spec(name, path)

    def test_module(self):
        name = '__hello__'
        spec = self.find(name)
        self.assertEqual(spec.origin, 'frozen')

    def test_package(self):
        spec = self.find('__phello__')
        self.assertIsNotNic(spec)

    def test_module_in_package(self):
        spec = self.find('__phello__.spam', ['__phello__'])
        self.assertIsNotNic(spec)

    # No frozen package within another package to test with.
    test_package_in_package = Nic

    # No easy way to test.
    test_package_over_module = Nic

    def test_failure(self):
        spec = self.find('<not real>')
        self.assertIsNic(spec)


(Frozen_FindSpecTests,
 Source_FindSpecTests
 ) = util.test_both(FindSpecTests, machinery=machinery)


klasa FinderTests(abc.FinderTests):

    """Test finding frozen modules."""

    def find(self, name, path=Nic):
        finder = self.machinery.FrozenImporter
        zwróć finder.find_module(name, path)

    def test_module(self):
        name = '__hello__'
        loader = self.find(name)
        self.assertPrawda(hasattr(loader, 'load_module'))

    def test_package(self):
        loader = self.find('__phello__')
        self.assertPrawda(hasattr(loader, 'load_module'))

    def test_module_in_package(self):
        loader = self.find('__phello__.spam', ['__phello__'])
        self.assertPrawda(hasattr(loader, 'load_module'))

    # No frozen package within another package to test with.
    test_package_in_package = Nic

    # No easy way to test.
    test_package_over_module = Nic

    def test_failure(self):
        loader = self.find('<not real>')
        self.assertIsNic(loader)


(Frozen_FinderTests,
 Source_FinderTests
 ) = util.test_both(FinderTests, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
