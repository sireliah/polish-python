z . zaimportuj util jako test_util

init = test_util.import_importlib('importlib')
machinery = test_util.import_importlib('importlib.machinery')
util = test_util.import_importlib('importlib.util')

zaimportuj os.path
z test.support zaimportuj CleanImport
zaimportuj unittest
zaimportuj sys
zaimportuj warnings



klasa TestLoader:

    def __init__(self, path=Nic, is_package=Nic):
        self.path = path
        self.package = is_package

    def __repr__(self):
        zwróć '<TestLoader object>'

    def __getattr__(self, name):
        jeżeli name == 'get_filename' oraz self.path jest nie Nic:
            zwróć self._get_filename
        jeżeli name == 'is_package':
            zwróć self._is_package
        podnieś AttributeError(name)

    def _get_filename(self, name):
        zwróć self.path

    def _is_package(self, name):
        zwróć self.package

    def create_module(self, spec):
        zwróć Nic


klasa NewLoader(TestLoader):

    EGGS = 1

    def exec_module(self, module):
        module.eggs = self.EGGS


klasa LegacyLoader(TestLoader):

    HAM = -1

    przy warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)

        frozen_util = util['Frozen']

        @frozen_util.module_for_loader
        def load_module(self, module):
            module.ham = self.HAM
            zwróć module


klasa ModuleSpecTests:

    def setUp(self):
        self.name = 'spam'
        self.path = 'spam.py'
        self.cached = self.util.cache_from_source(self.path)
        self.loader = TestLoader()
        self.spec = self.machinery.ModuleSpec(self.name, self.loader)
        self.loc_spec = self.machinery.ModuleSpec(self.name, self.loader,
                                                  origin=self.path)
        self.loc_spec._set_fileattr = Prawda

    def test_default(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_default_no_loader(self):
        spec = self.machinery.ModuleSpec(self.name, Nic)

        self.assertEqual(spec.name, self.name)
        self.assertIs(spec.loader, Nic)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_default_is_package_false(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader,
                                         is_package=Nieprawda)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_default_is_package_true(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader,
                                         is_package=Prawda)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertEqual(spec.submodule_search_locations, [])
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_has_location_setter(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader,
                                         origin='somewhere')
        self.assertNieprawda(spec.has_location)
        spec.has_location = Prawda
        self.assertPrawda(spec.has_location)

    def test_equality(self):
        other = type(sys.implementation)(name=self.name,
                                         loader=self.loader,
                                         origin=Nic,
                                         submodule_search_locations=Nic,
                                         has_location=Nieprawda,
                                         cached=Nic,
                                         )

        self.assertPrawda(self.spec == other)

    def test_equality_location(self):
        other = type(sys.implementation)(name=self.name,
                                         loader=self.loader,
                                         origin=self.path,
                                         submodule_search_locations=Nic,
                                         has_location=Prawda,
                                         cached=self.cached,
                                         )

        self.assertEqual(self.loc_spec, other)

    def test_inequality(self):
        other = type(sys.implementation)(name='ham',
                                         loader=self.loader,
                                         origin=Nic,
                                         submodule_search_locations=Nic,
                                         has_location=Nieprawda,
                                         cached=Nic,
                                         )

        self.assertNotEqual(self.spec, other)

    def test_inequality_incomplete(self):
        other = type(sys.implementation)(name=self.name,
                                         loader=self.loader,
                                         )

        self.assertNotEqual(self.spec, other)

    def test_package(self):
        spec = self.machinery.ModuleSpec('spam.eggs', self.loader)

        self.assertEqual(spec.parent, 'spam')

    def test_package_is_package(self):
        spec = self.machinery.ModuleSpec('spam.eggs', self.loader,
                                         is_package=Prawda)

        self.assertEqual(spec.parent, 'spam.eggs')

    # cached

    def test_cached_set(self):
        before = self.spec.cached
        self.spec.cached = 'there'
        after = self.spec.cached

        self.assertIs(before, Nic)
        self.assertEqual(after, 'there')

    def test_cached_no_origin(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader)

        self.assertIs(spec.cached, Nic)

    def test_cached_with_origin_not_location(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader,
                                         origin=self.path)

        self.assertIs(spec.cached, Nic)

    def test_cached_source(self):
        expected = self.util.cache_from_source(self.path)

        self.assertEqual(self.loc_spec.cached, expected)

    def test_cached_source_unknown_suffix(self):
        self.loc_spec.origin = 'spam.spamspamspam'

        self.assertIs(self.loc_spec.cached, Nic)

    def test_cached_source_missing_cache_tag(self):
        original = sys.implementation.cache_tag
        sys.implementation.cache_tag = Nic
        spróbuj:
            cached = self.loc_spec.cached
        w_końcu:
            sys.implementation.cache_tag = original

        self.assertIs(cached, Nic)

    def test_cached_sourceless(self):
        self.loc_spec.origin = 'spam.pyc'

        self.assertEqual(self.loc_spec.cached, 'spam.pyc')


(Frozen_ModuleSpecTests,
 Source_ModuleSpecTests
 ) = test_util.test_both(ModuleSpecTests, util=util, machinery=machinery)


klasa ModuleSpecMethodsTests:

    @property
    def bootstrap(self):
        zwróć self.init._bootstrap

    def setUp(self):
        self.name = 'spam'
        self.path = 'spam.py'
        self.cached = self.util.cache_from_source(self.path)
        self.loader = TestLoader()
        self.spec = self.machinery.ModuleSpec(self.name, self.loader)
        self.loc_spec = self.machinery.ModuleSpec(self.name, self.loader,
                                                  origin=self.path)
        self.loc_spec._set_fileattr = Prawda

    # exec()

    def test_exec(self):
        self.spec.loader = NewLoader()
        module = self.util.module_from_spec(self.spec)
        sys.modules[self.name] = module
        self.assertNieprawda(hasattr(module, 'eggs'))
        self.bootstrap._exec(self.spec, module)

        self.assertEqual(module.eggs, 1)

    # load()

    def test_load(self):
        self.spec.loader = NewLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            installed = sys.modules[self.spec.name]

        self.assertEqual(loaded.eggs, 1)
        self.assertIs(loaded, installed)

    def test_load_replaced(self):
        replacement = object()
        klasa ReplacingLoader(TestLoader):
            def exec_module(self, module):
                sys.modules[module.__name__] = replacement
        self.spec.loader = ReplacingLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            installed = sys.modules[self.spec.name]

        self.assertIs(loaded, replacement)
        self.assertIs(installed, replacement)

    def test_load_failed(self):
        klasa FailedLoader(TestLoader):
            def exec_module(self, module):
                podnieś RuntimeError
        self.spec.loader = FailedLoader()
        przy CleanImport(self.spec.name):
            przy self.assertRaises(RuntimeError):
                loaded = self.bootstrap._load(self.spec)
            self.assertNotIn(self.spec.name, sys.modules)

    def test_load_failed_removed(self):
        klasa FailedLoader(TestLoader):
            def exec_module(self, module):
                usuń sys.modules[module.__name__]
                podnieś RuntimeError
        self.spec.loader = FailedLoader()
        przy CleanImport(self.spec.name):
            przy self.assertRaises(RuntimeError):
                loaded = self.bootstrap._load(self.spec)
            self.assertNotIn(self.spec.name, sys.modules)

    def test_load_legacy(self):
        self.spec.loader = LegacyLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)

        self.assertEqual(loaded.ham, -1)

    def test_load_legacy_attributes(self):
        self.spec.loader = LegacyLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)

        self.assertIs(loaded.__loader__, self.spec.loader)
        self.assertEqual(loaded.__package__, self.spec.parent)
        self.assertIs(loaded.__spec__, self.spec)

    def test_load_legacy_attributes_immutable(self):
        module = object()
        klasa ImmutableLoader(TestLoader):
            def load_module(self, name):
                sys.modules[name] = module
                zwróć module
        self.spec.loader = ImmutableLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)

            self.assertIs(sys.modules[self.spec.name], module)

    # reload()

    def test_reload(self):
        self.spec.loader = NewLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            reloaded = self.bootstrap._exec(self.spec, loaded)
            installed = sys.modules[self.spec.name]

        self.assertEqual(loaded.eggs, 1)
        self.assertIs(reloaded, loaded)
        self.assertIs(installed, loaded)

    def test_reload_modified(self):
        self.spec.loader = NewLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            loaded.eggs = 2
            reloaded = self.bootstrap._exec(self.spec, loaded)

        self.assertEqual(loaded.eggs, 1)
        self.assertIs(reloaded, loaded)

    def test_reload_extra_attributes(self):
        self.spec.loader = NewLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            loaded.available = Nieprawda
            reloaded = self.bootstrap._exec(self.spec, loaded)

        self.assertNieprawda(loaded.available)
        self.assertIs(reloaded, loaded)

    def test_reload_init_module_attrs(self):
        self.spec.loader = NewLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            loaded.__name__ = 'ham'
            usuń loaded.__loader__
            usuń loaded.__package__
            usuń loaded.__spec__
            self.bootstrap._exec(self.spec, loaded)

        self.assertEqual(loaded.__name__, self.spec.name)
        self.assertIs(loaded.__loader__, self.spec.loader)
        self.assertEqual(loaded.__package__, self.spec.parent)
        self.assertIs(loaded.__spec__, self.spec)
        self.assertNieprawda(hasattr(loaded, '__path__'))
        self.assertNieprawda(hasattr(loaded, '__file__'))
        self.assertNieprawda(hasattr(loaded, '__cached__'))

    def test_reload_legacy(self):
        self.spec.loader = LegacyLoader()
        przy CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            reloaded = self.bootstrap._exec(self.spec, loaded)
            installed = sys.modules[self.spec.name]

        self.assertEqual(loaded.ham, -1)
        self.assertIs(reloaded, loaded)
        self.assertIs(installed, loaded)


(Frozen_ModuleSpecMethodsTests,
 Source_ModuleSpecMethodsTests
 ) = test_util.test_both(ModuleSpecMethodsTests, init=init, util=util,
                         machinery=machinery)


klasa ModuleReprTests:

    @property
    def bootstrap(self):
        zwróć self.init._bootstrap

    def setUp(self):
        self.module = type(os)('spam')
        self.spec = self.machinery.ModuleSpec('spam', TestLoader())

    def test_module___loader___module_repr(self):
        klasa Loader:
            def module_repr(self, module):
                zwróć '<delicious {}>'.format(module.__name__)
        self.module.__loader__ = Loader()
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<delicious spam>')

    def test_module___loader___module_repr_bad(self):
        klasa Loader(TestLoader):
            def module_repr(self, module):
                podnieś Exception
        self.module.__loader__ = Loader()
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} (<TestLoader object>)>'.format('spam'))

    def test_module___spec__(self):
        origin = 'in a hole, w the ground'
        self.spec.origin = origin
        self.module.__spec__ = self.spec
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<module {!r} ({})>'.format('spam', origin))

    def test_module___spec___location(self):
        location = 'in_a_galaxy_far_far_away.py'
        self.spec.origin = location
        self.spec._set_fileattr = Prawda
        self.module.__spec__ = self.spec
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} z {!r}>'.format('spam', location))

    def test_module___spec___no_origin(self):
        self.spec.loader = TestLoader()
        self.module.__spec__ = self.spec
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} (<TestLoader object>)>'.format('spam'))

    def test_module___spec___no_origin_no_loader(self):
        self.spec.loader = Nic
        self.module.__spec__ = self.spec
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<module {!r}>'.format('spam'))

    def test_module_no_name(self):
        usuń self.module.__name__
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<module {!r}>'.format('?'))

    def test_module_with_file(self):
        filename = 'e/i/e/i/o/spam.py'
        self.module.__file__ = filename
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} z {!r}>'.format('spam', filename))

    def test_module_no_file(self):
        self.module.__loader__ = TestLoader()
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} (<TestLoader object>)>'.format('spam'))

    def test_module_no_file_no_loader(self):
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<module {!r}>'.format('spam'))


(Frozen_ModuleReprTests,
 Source_ModuleReprTests
 ) = test_util.test_both(ModuleReprTests, init=init, util=util,
                         machinery=machinery)


klasa FactoryTests:

    def setUp(self):
        self.name = 'spam'
        self.path = 'spam.py'
        self.cached = self.util.cache_from_source(self.path)
        self.loader = TestLoader()
        self.fileloader = TestLoader(self.path)
        self.pkgloader = TestLoader(self.path, Prawda)

    # spec_from_loader()

    def test_spec_from_loader_default(self):
        spec = self.util.spec_from_loader(self.name, self.loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_spec_from_loader_default_with_bad_is_package(self):
        klasa Loader:
            def is_package(self, name):
                podnieś ImportError
        loader = Loader()
        spec = self.util.spec_from_loader(self.name, loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_spec_from_loader_origin(self):
        origin = 'somewhere over the rainbow'
        spec = self.util.spec_from_loader(self.name, self.loader,
                                          origin=origin)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, origin)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_spec_from_loader_is_package_false(self):
        spec = self.util.spec_from_loader(self.name, self.loader,
                                          is_package=Nieprawda)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_spec_from_loader_is_package_true(self):
        spec = self.util.spec_from_loader(self.name, self.loader,
                                          is_package=Prawda)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertEqual(spec.submodule_search_locations, [])
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_spec_from_loader_origin_and_is_package(self):
        origin = 'where the streets have no name'
        spec = self.util.spec_from_loader(self.name, self.loader,
                                          origin=origin, is_package=Prawda)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, origin)
        self.assertIs(spec.loader_state, Nic)
        self.assertEqual(spec.submodule_search_locations, [])
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_spec_from_loader_is_package_with_loader_false(self):
        loader = TestLoader(is_package=Nieprawda)
        spec = self.util.spec_from_loader(self.name, loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_spec_from_loader_is_package_with_loader_true(self):
        loader = TestLoader(is_package=Prawda)
        spec = self.util.spec_from_loader(self.name, loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertIs(spec.origin, Nic)
        self.assertIs(spec.loader_state, Nic)
        self.assertEqual(spec.submodule_search_locations, [])
        self.assertIs(spec.cached, Nic)
        self.assertNieprawda(spec.has_location)

    def test_spec_from_loader_default_with_file_loader(self):
        spec = self.util.spec_from_loader(self.name, self.fileloader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_loader_is_package_false_with_fileloader(self):
        spec = self.util.spec_from_loader(self.name, self.fileloader,
                                          is_package=Nieprawda)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_loader_is_package_true_with_fileloader(self):
        spec = self.util.spec_from_loader(self.name, self.fileloader,
                                          is_package=Prawda)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertEqual(spec.submodule_search_locations, [''])
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    # spec_from_file_location()

    def test_spec_from_file_location_default(self):
        spec = self.util.spec_from_file_location(self.name, self.path)

        self.assertEqual(spec.name, self.name)
        # Need to use a circuitous route to get at importlib.machinery to make
        # sure the same klasa object jest used w the isinstance() check as
        # would have been used to create the loader.
        self.assertIsInstance(spec.loader,
                              self.util.abc.machinery.SourceFileLoader)
        self.assertEqual(spec.loader.name, self.name)
        self.assertEqual(spec.loader.path, self.path)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_default_without_location(self):
        spec = self.util.spec_from_file_location(self.name)

        self.assertIs(spec, Nic)

    def test_spec_from_file_location_default_bad_suffix(self):
        spec = self.util.spec_from_file_location(self.name, 'spam.eggs')

        self.assertIs(spec, Nic)

    def test_spec_from_file_location_loader_no_location(self):
        spec = self.util.spec_from_file_location(self.name,
                                                 loader=self.fileloader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_loader_no_location_no_get_filename(self):
        spec = self.util.spec_from_file_location(self.name,
                                                 loader=self.loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertEqual(spec.origin, '<unknown>')
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_loader_no_location_bad_get_filename(self):
        klasa Loader:
            def get_filename(self, name):
                podnieś ImportError
        loader = Loader()
        spec = self.util.spec_from_file_location(self.name, loader=loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertEqual(spec.origin, '<unknown>')
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertIs(spec.cached, Nic)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_smsl_none(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.fileloader,
                                       submodule_search_locations=Nic)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_smsl_empty(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.fileloader,
                                       submodule_search_locations=[])

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertEqual(spec.submodule_search_locations, [''])
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_smsl_not_empty(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.fileloader,
                                       submodule_search_locations=['eggs'])

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertEqual(spec.submodule_search_locations, ['eggs'])
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_smsl_default(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.pkgloader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.pkgloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertEqual(spec.submodule_search_locations, [''])
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_smsl_default_not_package(self):
        klasa Loader:
            def is_package(self, name):
                zwróć Nieprawda
        loader = Loader()
        spec = self.util.spec_from_file_location(self.name, self.path,
                                                 loader=loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_smsl_default_no_is_package(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.fileloader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)

    def test_spec_from_file_location_smsl_default_bad_is_package(self):
        klasa Loader:
            def is_package(self, name):
                podnieś ImportError
        loader = Loader()
        spec = self.util.spec_from_file_location(self.name, self.path,
                                                 loader=loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Nic)
        self.assertIs(spec.submodule_search_locations, Nic)
        self.assertEqual(spec.cached, self.cached)
        self.assertPrawda(spec.has_location)


(Frozen_FactoryTests,
 Source_FactoryTests
 ) = test_util.test_both(FactoryTests, util=util, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
