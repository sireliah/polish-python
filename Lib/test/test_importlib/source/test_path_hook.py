z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')

zaimportuj unittest


klasa PathHookTest:

    """Test the path hook dla source."""

    def path_hook(self):
        zwróć self.machinery.FileFinder.path_hook((self.machinery.SourceFileLoader,
            self.machinery.SOURCE_SUFFIXES))

    def test_success(self):
        przy util.create_modules('dummy') jako mapping:
            self.assertPrawda(hasattr(self.path_hook()(mapping['.root']),
                                 'find_module'))

    def test_empty_string(self):
        # The empty string represents the cwd.
        self.assertPrawda(hasattr(self.path_hook()(''), 'find_module'))


(Frozen_PathHookTest,
 Source_PathHooktest
 ) = util.test_both(PathHookTest, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
