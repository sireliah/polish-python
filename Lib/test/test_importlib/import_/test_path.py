z .. zaimportuj util

importlib = util.import_importlib('importlib')
machinery = util.import_importlib('importlib.machinery')

zaimportuj errno
zaimportuj os
zaimportuj sys
zaimportuj tempfile
z types zaimportuj ModuleType
zaimportuj unittest
zaimportuj warnings
zaimportuj zipimport


klasa FinderTests:

    """Tests dla PathFinder."""

    def test_failure(self):
        # Test Nic returned upon nie finding a suitable loader.
        module = '<test module>'
        przy util.import_state():
            self.assertIsNic(self.machinery.PathFinder.find_module(module))

    def test_sys_path(self):
        # Test that sys.path jest used when 'path' jest Nic.
        # Implicitly tests that sys.path_importer_cache jest used.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_spec(module)
        przy util.import_state(path_importer_cache={path: importer},
                               path=[path]):
            loader = self.machinery.PathFinder.find_module(module)
            self.assertIs(loader, importer)

    def test_path(self):
        # Test that 'path' jest used when set.
        # Implicitly tests that sys.path_importer_cache jest used.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_spec(module)
        przy util.import_state(path_importer_cache={path: importer}):
            loader = self.machinery.PathFinder.find_module(module, [path])
            self.assertIs(loader, importer)

    def test_empty_list(self):
        # An empty list should nie count jako asking dla sys.path.
        module = 'module'
        path = '<test path>'
        importer = util.mock_spec(module)
        przy util.import_state(path_importer_cache={path: importer},
                               path=[path]):
            self.assertIsNic(self.machinery.PathFinder.find_module('module', []))

    def test_path_hooks(self):
        # Test that sys.path_hooks jest used.
        # Test that sys.path_importer_cache jest set.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_spec(module)
        hook = util.mock_path_hook(path, importer=importer)
        przy util.import_state(path_hooks=[hook]):
            loader = self.machinery.PathFinder.find_module(module, [path])
            self.assertIs(loader, importer)
            self.assertIn(path, sys.path_importer_cache)
            self.assertIs(sys.path_importer_cache[path], importer)

    def test_empty_path_hooks(self):
        # Test that jeżeli sys.path_hooks jest empty a warning jest podnieśd,
        # sys.path_importer_cache gets Nic set, oraz PathFinder returns Nic.
        path_entry = 'bogus_path'
        przy util.import_state(path_importer_cache={}, path_hooks=[],
                               path=[path_entry]):
            przy warnings.catch_warnings(record=Prawda) jako w:
                warnings.simplefilter('always')
                self.assertIsNic(self.machinery.PathFinder.find_module('os'))
                self.assertIsNic(sys.path_importer_cache[path_entry])
                self.assertEqual(len(w), 1)
                self.assertPrawda(issubclass(w[-1].category, ImportWarning))

    def test_path_importer_cache_empty_string(self):
        # The empty string should create a finder using the cwd.
        path = ''
        module = '<test module>'
        importer = util.mock_spec(module)
        hook = util.mock_path_hook(os.getcwd(), importer=importer)
        przy util.import_state(path=[path], path_hooks=[hook]):
            loader = self.machinery.PathFinder.find_module(module)
            self.assertIs(loader, importer)
            self.assertIn(os.getcwd(), sys.path_importer_cache)

    def test_Nic_on_sys_path(self):
        # Putting Nic w sys.path[0] caused an zaimportuj regression z Python
        # 3.2: http://bugs.python.org/issue16514
        new_path = sys.path[:]
        new_path.insert(0, Nic)
        new_path_importer_cache = sys.path_importer_cache.copy()
        new_path_importer_cache.pop(Nic, Nic)
        new_path_hooks = [zipimport.zipimporter,
                          self.machinery.FileFinder.path_hook(
                              *self.importlib._bootstrap_external._get_supported_file_loaders())]
        missing = object()
        email = sys.modules.pop('email', missing)
        spróbuj:
            przy util.import_state(meta_path=sys.meta_path[:],
                                   path=new_path,
                                   path_importer_cache=new_path_importer_cache,
                                   path_hooks=new_path_hooks):
                module = self.importlib.import_module('email')
                self.assertIsInstance(module, ModuleType)
        w_końcu:
            jeżeli email jest nie missing:
                sys.modules['email'] = email

    def test_finder_with_find_module(self):
        klasa TestFinder:
            def find_module(self, fullname):
                zwróć self.to_zwróć
        failing_finder = TestFinder()
        failing_finder.to_return = Nic
        path = 'testing path'
        przy util.import_state(path_importer_cache={path: failing_finder}):
            self.assertIsNic(
                    self.machinery.PathFinder.find_spec('whatever', [path]))
        success_finder = TestFinder()
        success_finder.to_return = __loader__
        przy util.import_state(path_importer_cache={path: success_finder}):
            spec = self.machinery.PathFinder.find_spec('whatever', [path])
        self.assertEqual(spec.loader, __loader__)

    def test_finder_with_find_loader(self):
        klasa TestFinder:
            loader = Nic
            portions = []
            def find_loader(self, fullname):
                zwróć self.loader, self.portions
        path = 'testing path'
        przy util.import_state(path_importer_cache={path: TestFinder()}):
            self.assertIsNic(
                    self.machinery.PathFinder.find_spec('whatever', [path]))
        success_finder = TestFinder()
        success_finder.loader = __loader__
        przy util.import_state(path_importer_cache={path: success_finder}):
            spec = self.machinery.PathFinder.find_spec('whatever', [path])
        self.assertEqual(spec.loader, __loader__)

    def test_finder_with_find_spec(self):
        klasa TestFinder:
            spec = Nic
            def find_spec(self, fullname, target=Nic):
                zwróć self.spec
        path = 'testing path'
        przy util.import_state(path_importer_cache={path: TestFinder()}):
            self.assertIsNic(
                    self.machinery.PathFinder.find_spec('whatever', [path]))
        success_finder = TestFinder()
        success_finder.spec = self.machinery.ModuleSpec('whatever', __loader__)
        przy util.import_state(path_importer_cache={path: success_finder}):
            got = self.machinery.PathFinder.find_spec('whatever', [path])
        self.assertEqual(got, success_finder.spec)

    @unittest.skipIf(sys.platform == 'win32', "cwd can't nie exist on Windows")
    def test_deleted_cwd(self):
        # Issue #22834
        self.addCleanup(os.chdir, os.getcwd())
        spróbuj:
            przy tempfile.TemporaryDirectory() jako path:
                os.chdir(path)
        wyjąwszy OSError jako exc:
            jeżeli exc.errno == errno.EINVAL:
                self.skipTest("platform does nie allow the deletion of the cwd")
            podnieś
        przy util.import_state(path=['']):
            # Do nie want FileNotFoundError podnieśd.
            self.assertIsNic(self.machinery.PathFinder.find_spec('whatever'))




(Frozen_FinderTests,
 Source_FinderTests
 ) = util.test_both(FinderTests, importlib=importlib, machinery=machinery)


klasa PathEntryFinderTests:

    def test_finder_with_failing_find_module(self):
        # PathEntryFinder przy find_module() defined should work.
        # Issue #20763.
        klasa Finder:
            path_location = 'test_finder_with_find_module'
            def __init__(self, path):
                jeżeli path != self.path_location:
                    podnieś ImportError

            @staticmethod
            def find_module(fullname):
                zwróć Nic


        przy util.import_state(path=[Finder.path_location]+sys.path[:],
                               path_hooks=[Finder]):
            self.machinery.PathFinder.find_spec('importlib')


(Frozen_PEFTests,
 Source_PEFTests
 ) = util.test_both(PathEntryFinderTests, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
