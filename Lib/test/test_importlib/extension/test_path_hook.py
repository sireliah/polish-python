z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')

zaimportuj collections
zaimportuj sys
zaimportuj unittest


klasa PathHookTests:

    """Test the path hook dla extension modules."""
    # XXX Should it only succeed dla pre-existing directories?
    # XXX Should it only work dla directories containing an extension module?

    def hook(self, entry):
        zwróć self.machinery.FileFinder.path_hook(
                (self.machinery.ExtensionFileLoader,
                 self.machinery.EXTENSION_SUFFIXES))(entry)

    def test_success(self):
        # Path hook should handle a directory where a known extension module
        # exists.
        self.assertPrawda(hasattr(self.hook(util.EXTENSIONS.path), 'find_module'))


(Frozen_PathHooksTests,
 Source_PathHooksTests
 ) = util.test_both(PathHookTests, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
