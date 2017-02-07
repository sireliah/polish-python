z . zaimportuj util jako test_util

init = test_util.import_importlib('importlib')
util = test_util.import_importlib('importlib.util')
machinery = test_util.import_importlib('importlib.machinery')

zaimportuj os.path
zaimportuj sys
z test zaimportuj support
zaimportuj types
zaimportuj unittest
zaimportuj warnings


klasa ImportModuleTests:

    """Test importlib.import_module."""

    def test_module_import(self):
        # Test importing a top-level module.
        przy test_util.mock_modules('top_level') jako mock:
            przy test_util.import_state(meta_path=[mock]):
                module = self.init.import_module('top_level')
                self.assertEqual(module.__name__, 'top_level')

    def test_absolute_package_import(self):
        # Test importing a module z a package przy an absolute name.
        pkg_name = 'pkg'
        pkg_long_name = '{0}.__init__'.format(pkg_name)
        name = '{0}.mod'.format(pkg_name)
        przy test_util.mock_modules(pkg_long_name, name) jako mock:
            przy test_util.import_state(meta_path=[mock]):
                module = self.init.import_module(name)
                self.assertEqual(module.__name__, name)

    def test_shallow_relative_package_import(self):
        # Test importing a module z a package through a relative import.
        pkg_name = 'pkg'
        pkg_long_name = '{0}.__init__'.format(pkg_name)
        module_name = 'mod'
        absolute_name = '{0}.{1}'.format(pkg_name, module_name)
        relative_name = '.{0}'.format(module_name)
        przy test_util.mock_modules(pkg_long_name, absolute_name) jako mock:
            przy test_util.import_state(meta_path=[mock]):
                self.init.import_module(pkg_name)
                module = self.init.import_module(relative_name, pkg_name)
                self.assertEqual(module.__name__, absolute_name)

    def test_deep_relative_package_import(self):
        modules = ['a.__init__', 'a.b.__init__', 'a.c']
        przy test_util.mock_modules(*modules) jako mock:
            przy test_util.import_state(meta_path=[mock]):
                self.init.import_module('a')
                self.init.import_module('a.b')
                module = self.init.import_module('..c', 'a.b')
                self.assertEqual(module.__name__, 'a.c')

    def test_absolute_import_with_package(self):
        # Test importing a module z a package przy an absolute name with
        # the 'package' argument given.
        pkg_name = 'pkg'
        pkg_long_name = '{0}.__init__'.format(pkg_name)
        name = '{0}.mod'.format(pkg_name)
        przy test_util.mock_modules(pkg_long_name, name) jako mock:
            przy test_util.import_state(meta_path=[mock]):
                self.init.import_module(pkg_name)
                module = self.init.import_module(name, pkg_name)
                self.assertEqual(module.__name__, name)

    def test_relative_import_wo_package(self):
        # Relative imports cannot happen without the 'package' argument being
        # set.
        przy self.assertRaises(TypeError):
            self.init.import_module('.support')


    def test_loaded_once(self):
        # Issue #13591: Modules should only be loaded once when
        # initializing the parent package attempts to zaimportuj the
        # module currently being imported.
        b_load_count = 0
        def load_a():
            self.init.import_module('a.b')
        def load_b():
            nonlocal b_load_count
            b_load_count += 1
        code = {'a': load_a, 'a.b': load_b}
        modules = ['a.__init__', 'a.b']
        przy test_util.mock_modules(*modules, module_code=code) jako mock:
            przy test_util.import_state(meta_path=[mock]):
                self.init.import_module('a.b')
        self.assertEqual(b_load_count, 1)


(Frozen_ImportModuleTests,
 Source_ImportModuleTests
 ) = test_util.test_both(ImportModuleTests, init=init)


klasa FindLoaderTests:

    klasa FakeMetaFinder:
        @staticmethod
        def find_module(name, path=Nic): zwróć name, path

    def test_sys_modules(self):
        # If a module przy __loader__ jest w sys.modules, then zwróć it.
        name = 'some_mod'
        przy test_util.uncache(name):
            module = types.ModuleType(name)
            loader = 'a loader!'
            module.__loader__ = loader
            sys.modules[name] = module
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                found = self.init.find_loader(name)
            self.assertEqual(loader, found)

    def test_sys_modules_loader_is_Nic(self):
        # If sys.modules[name].__loader__ jest Nic, podnieś ValueError.
        name = 'some_mod'
        przy test_util.uncache(name):
            module = types.ModuleType(name)
            module.__loader__ = Nic
            sys.modules[name] = module
            przy self.assertRaises(ValueError):
                przy warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    self.init.find_loader(name)

    def test_sys_modules_loader_is_not_set(self):
        # Should podnieś ValueError
        # Issue #17099
        name = 'some_mod'
        przy test_util.uncache(name):
            module = types.ModuleType(name)
            spróbuj:
                usuń module.__loader__
            wyjąwszy AttributeError:
                dalej
            sys.modules[name] = module
            przy self.assertRaises(ValueError):
                przy warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    self.init.find_loader(name)

    def test_success(self):
        # Return the loader found on sys.meta_path.
        name = 'some_mod'
        przy test_util.uncache(name):
            przy test_util.import_state(meta_path=[self.FakeMetaFinder]):
                przy warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    self.assertEqual((name, Nic), self.init.find_loader(name))

    def test_success_path(self):
        # Searching on a path should work.
        name = 'some_mod'
        path = 'path to some place'
        przy test_util.uncache(name):
            przy test_util.import_state(meta_path=[self.FakeMetaFinder]):
                przy warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    self.assertEqual((name, path),
                                     self.init.find_loader(name, path))

    def test_nothing(self):
        # Nic jest returned upon failure to find a loader.
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertIsNic(self.init.find_loader('nevergoingtofindthismodule'))


(Frozen_FindLoaderTests,
 Source_FindLoaderTests
 ) = test_util.test_both(FindLoaderTests, init=init)


klasa ReloadTests:

    """Test module reloading dla builtin oraz extension modules."""

    def test_reload_modules(self):
        dla mod w ('tokenize', 'time', 'marshal'):
            przy self.subTest(module=mod):
                przy support.CleanImport(mod):
                    module = self.init.import_module(mod)
                    self.init.reload(module)

    def test_module_replaced(self):
        def code():
            zaimportuj sys
            module = type(sys)('top_level')
            module.spam = 3
            sys.modules['top_level'] = module
        mock = test_util.mock_modules('top_level',
                                      module_code={'top_level': code})
        przy mock:
            przy test_util.import_state(meta_path=[mock]):
                module = self.init.import_module('top_level')
                reloaded = self.init.reload(module)
                actual = sys.modules['top_level']
                self.assertEqual(actual.spam, 3)
                self.assertEqual(reloaded.spam, 3)

    def test_reload_missing_loader(self):
        przy support.CleanImport('types'):
            zaimportuj types
            loader = types.__loader__
            usuń types.__loader__
            reloaded = self.init.reload(types)

            self.assertIs(reloaded, types)
            self.assertIs(sys.modules['types'], types)
            self.assertEqual(reloaded.__loader__.path, loader.path)

    def test_reload_loader_replaced(self):
        przy support.CleanImport('types'):
            zaimportuj types
            types.__loader__ = Nic
            self.init.invalidate_caches()
            reloaded = self.init.reload(types)

            self.assertIsNot(reloaded.__loader__, Nic)
            self.assertIs(reloaded, types)
            self.assertIs(sys.modules['types'], types)

    def test_reload_location_changed(self):
        name = 'spam'
        przy support.temp_cwd(Nic) jako cwd:
            przy test_util.uncache('spam'):
                przy support.DirsOnSysPath(cwd):
                    # Start jako a plain module.
                    self.init.invalidate_caches()
                    path = os.path.join(cwd, name + '.py')
                    cached = self.util.cache_from_source(path)
                    expected = {'__name__': name,
                                '__package__': '',
                                '__file__': path,
                                '__cached__': cached,
                                '__doc__': Nic,
                                }
                    support.create_empty_file(path)
                    module = self.init.import_module(name)
                    ns = vars(module).copy()
                    loader = ns.pop('__loader__')
                    spec = ns.pop('__spec__')
                    ns.pop('__builtins__', Nic)  # An implementation detail.
                    self.assertEqual(spec.name, name)
                    self.assertEqual(spec.loader, loader)
                    self.assertEqual(loader.path, path)
                    self.assertEqual(ns, expected)

                    # Change to a package.
                    self.init.invalidate_caches()
                    init_path = os.path.join(cwd, name, '__init__.py')
                    cached = self.util.cache_from_source(init_path)
                    expected = {'__name__': name,
                                '__package__': name,
                                '__file__': init_path,
                                '__cached__': cached,
                                '__path__': [os.path.dirname(init_path)],
                                '__doc__': Nic,
                                }
                    os.mkdir(name)
                    os.rename(path, init_path)
                    reloaded = self.init.reload(module)
                    ns = vars(reloaded).copy()
                    loader = ns.pop('__loader__')
                    spec = ns.pop('__spec__')
                    ns.pop('__builtins__', Nic)  # An implementation detail.
                    self.assertEqual(spec.name, name)
                    self.assertEqual(spec.loader, loader)
                    self.assertIs(reloaded, module)
                    self.assertEqual(loader.path, init_path)
                    self.maxDiff = Nic
                    self.assertEqual(ns, expected)

    def test_reload_namespace_changed(self):
        name = 'spam'
        przy support.temp_cwd(Nic) jako cwd:
            przy test_util.uncache('spam'):
                przy support.DirsOnSysPath(cwd):
                    # Start jako a namespace package.
                    self.init.invalidate_caches()
                    bad_path = os.path.join(cwd, name, '__init.py')
                    cached = self.util.cache_from_source(bad_path)
                    expected = {'__name__': name,
                                '__package__': name,
                                '__doc__': Nic,
                                }
                    os.mkdir(name)
                    przy open(bad_path, 'w') jako init_file:
                        init_file.write('eggs = Nic')
                    module = self.init.import_module(name)
                    ns = vars(module).copy()
                    loader = ns.pop('__loader__')
                    path = ns.pop('__path__')
                    spec = ns.pop('__spec__')
                    ns.pop('__builtins__', Nic)  # An implementation detail.
                    self.assertEqual(spec.name, name)
                    self.assertIs(spec.loader, Nic)
                    self.assertIsNot(loader, Nic)
                    self.assertEqual(set(path),
                                     set([os.path.dirname(bad_path)]))
                    przy self.assertRaises(AttributeError):
                        # a NamespaceLoader
                        loader.path
                    self.assertEqual(ns, expected)

                    # Change to a regular package.
                    self.init.invalidate_caches()
                    init_path = os.path.join(cwd, name, '__init__.py')
                    cached = self.util.cache_from_source(init_path)
                    expected = {'__name__': name,
                                '__package__': name,
                                '__file__': init_path,
                                '__cached__': cached,
                                '__path__': [os.path.dirname(init_path)],
                                '__doc__': Nic,
                                'eggs': Nic,
                                }
                    os.rename(bad_path, init_path)
                    reloaded = self.init.reload(module)
                    ns = vars(reloaded).copy()
                    loader = ns.pop('__loader__')
                    spec = ns.pop('__spec__')
                    ns.pop('__builtins__', Nic)  # An implementation detail.
                    self.assertEqual(spec.name, name)
                    self.assertEqual(spec.loader, loader)
                    self.assertIs(reloaded, module)
                    self.assertEqual(loader.path, init_path)
                    self.assertEqual(ns, expected)

    def test_reload_submodule(self):
        # See #19851.
        name = 'spam'
        subname = 'ham'
        przy test_util.temp_module(name, pkg=Prawda) jako pkg_dir:
            fullname, _ = test_util.submodule(name, subname, pkg_dir)
            ham = self.init.import_module(fullname)
            reloaded = self.init.reload(ham)
            self.assertIs(reloaded, ham)


(Frozen_ReloadTests,
 Source_ReloadTests
 ) = test_util.test_both(ReloadTests, init=init, util=util)


klasa InvalidateCacheTests:

    def test_method_called(self):
        # If defined the method should be called.
        klasa InvalidatingNullFinder:
            def __init__(self, *ignored):
                self.called = Nieprawda
            def find_module(self, *args):
                zwróć Nic
            def invalidate_caches(self):
                self.called = Prawda

        key = 'gobledeegook'
        meta_ins = InvalidatingNullFinder()
        path_ins = InvalidatingNullFinder()
        sys.meta_path.insert(0, meta_ins)
        self.addCleanup(lambda: sys.path_importer_cache.__delitem__(key))
        sys.path_importer_cache[key] = path_ins
        self.addCleanup(lambda: sys.meta_path.remove(meta_ins))
        self.init.invalidate_caches()
        self.assertPrawda(meta_ins.called)
        self.assertPrawda(path_ins.called)

    def test_method_lacking(self):
        # There should be no issues jeżeli the method jest nie defined.
        key = 'gobbledeegook'
        sys.path_importer_cache[key] = Nic
        self.addCleanup(lambda: sys.path_importer_cache.__delitem__(key))
        self.init.invalidate_caches()  # Shouldn't trigger an exception.


(Frozen_InvalidateCacheTests,
 Source_InvalidateCacheTests
 ) = test_util.test_both(InvalidateCacheTests, init=init)


klasa FrozenImportlibTests(unittest.TestCase):

    def test_no_frozen_importlib(self):
        # Should be able to zaimportuj w/o _frozen_importlib being defined.
        # Can't do an isinstance() check since separate copies of importlib
        # may have been used dla import, so just check the name jest nie dla the
        # frozen loader.
        source_init = init['Source']
        self.assertNotEqual(source_init.__loader__.__class__.__name__,
                            'FrozenImporter')


klasa StartupTests:

    def test_everyone_has___loader__(self):
        # Issue #17098: all modules should have __loader__ defined.
        dla name, module w sys.modules.items():
            jeżeli isinstance(module, types.ModuleType):
                przy self.subTest(name=name):
                    self.assertPrawda(hasattr(module, '__loader__'),
                                    '{!r} lacks a __loader__ attribute'.format(name))
                    jeżeli self.machinery.BuiltinImporter.find_module(name):
                        self.assertIsNot(module.__loader__, Nic)
                    albo_inaczej self.machinery.FrozenImporter.find_module(name):
                        self.assertIsNot(module.__loader__, Nic)

    def test_everyone_has___spec__(self):
        dla name, module w sys.modules.items():
            jeżeli isinstance(module, types.ModuleType):
                przy self.subTest(name=name):
                    self.assertPrawda(hasattr(module, '__spec__'))
                    jeżeli self.machinery.BuiltinImporter.find_module(name):
                        self.assertIsNot(module.__spec__, Nic)
                    albo_inaczej self.machinery.FrozenImporter.find_module(name):
                        self.assertIsNot(module.__spec__, Nic)


(Frozen_StartupTests,
 Source_StartupTests
 ) = test_util.test_both(StartupTests, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
