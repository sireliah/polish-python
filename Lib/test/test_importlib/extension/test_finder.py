z .. zaimportuj abc
z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')

zaimportuj unittest
zaimportuj warnings

# XXX find_spec tests

klasa FinderTests(abc.FinderTests):

    """Test the finder dla extension modules."""

    def find_module(self, fullname):
        importer = self.machinery.FileFinder(util.EXTENSIONS.path,
                                            (self.machinery.ExtensionFileLoader,
                                             self.machinery.EXTENSION_SUFFIXES))
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            zwróć importer.find_module(fullname)

    def test_module(self):
        self.assertPrawda(self.find_module(util.EXTENSIONS.name))

    # No extension module jako an __init__ available dla testing.
    test_package = test_package_in_package = Nic

    # No extension module w a package available dla testing.
    test_module_in_package = Nic

    # Extension modules cannot be an __init__ dla a package.
    test_package_over_module = Nic

    def test_failure(self):
        self.assertIsNic(self.find_module('asdfjkl;'))


(Frozen_FinderTests,
 Source_FinderTests
 ) = util.test_both(FinderTests, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
