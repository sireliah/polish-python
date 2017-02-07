zaimportuj contextlib
zaimportuj inspect
zaimportuj io
zaimportuj marshal
zaimportuj os
zaimportuj sys
z test zaimportuj support
zaimportuj types
zaimportuj unittest
z unittest zaimportuj mock
zaimportuj warnings

z . zaimportuj util jako test_util

init = test_util.import_importlib('importlib')
abc = test_util.import_importlib('importlib.abc')
machinery = test_util.import_importlib('importlib.machinery')
util = test_util.import_importlib('importlib.util')


##### Inheritance ##############################################################
klasa InheritanceTests:

    """Test that the specified klasa jest a subclass/superclass of the expected
    classes."""

    subclasses = []
    superclasses = []

    def setUp(self):
        self.superclasses = [getattr(self.abc, class_name)
                             dla class_name w self.superclass_names]
        jeżeli hasattr(self, 'subclass_names'):
            # Because test.support.import_fresh_module() creates a new
            # importlib._bootstrap per module, inheritance checks fail when
            # checking across module boundaries (i.e. the _bootstrap w abc jest
            # nie the same jako the one w machinery). That means stealing one of
            # the modules z the other to make sure the same instance jest used.
            machinery = self.abc.machinery
            self.subclasses = [getattr(machinery, class_name)
                               dla class_name w self.subclass_names]
        assert self.subclasses albo self.superclasses, self.__class__
        self.__test = getattr(self.abc, self._NAME)

    def test_subclasses(self):
        # Test that the expected subclasses inherit.
        dla subclass w self.subclasses:
            self.assertPrawda(issubclass(subclass, self.__test),
                "{0} jest nie a subclass of {1}".format(subclass, self.__test))

    def test_superclasses(self):
        # Test that the klasa inherits z the expected superclasses.
        dla superclass w self.superclasses:
            self.assertPrawda(issubclass(self.__test, superclass),
               "{0} jest nie a superclass of {1}".format(superclass, self.__test))


klasa MetaPathFinder(InheritanceTests):
    superclass_names = ['Finder']
    subclass_names = ['BuiltinImporter', 'FrozenImporter', 'PathFinder',
                      'WindowsRegistryFinder']


(Frozen_MetaPathFinderInheritanceTests,
 Source_MetaPathFinderInheritanceTests
 ) = test_util.test_both(MetaPathFinder, abc=abc)


klasa PathEntryFinder(InheritanceTests):
    superclass_names = ['Finder']
    subclass_names = ['FileFinder']


(Frozen_PathEntryFinderInheritanceTests,
 Source_PathEntryFinderInheritanceTests
 ) = test_util.test_both(PathEntryFinder, abc=abc)


klasa ResourceLoader(InheritanceTests):
    superclass_names = ['Loader']


(Frozen_ResourceLoaderInheritanceTests,
 Source_ResourceLoaderInheritanceTests
 ) = test_util.test_both(ResourceLoader, abc=abc)


klasa InspectLoader(InheritanceTests):
    superclass_names = ['Loader']
    subclass_names = ['BuiltinImporter', 'FrozenImporter', 'ExtensionFileLoader']


(Frozen_InspectLoaderInheritanceTests,
 Source_InspectLoaderInheritanceTests
 ) = test_util.test_both(InspectLoader, abc=abc)


klasa ExecutionLoader(InheritanceTests):
    superclass_names = ['InspectLoader']
    subclass_names = ['ExtensionFileLoader']


(Frozen_ExecutionLoaderInheritanceTests,
 Source_ExecutionLoaderInheritanceTests
 ) = test_util.test_both(ExecutionLoader, abc=abc)


klasa FileLoader(InheritanceTests):
    superclass_names = ['ResourceLoader', 'ExecutionLoader']
    subclass_names = ['SourceFileLoader', 'SourcelessFileLoader']


(Frozen_FileLoaderInheritanceTests,
 Source_FileLoaderInheritanceTests
 ) = test_util.test_both(FileLoader, abc=abc)


klasa SourceLoader(InheritanceTests):
    superclass_names = ['ResourceLoader', 'ExecutionLoader']
    subclass_names = ['SourceFileLoader']


(Frozen_SourceLoaderInheritanceTests,
 Source_SourceLoaderInheritanceTests
 ) = test_util.test_both(SourceLoader, abc=abc)


##### Default zwróć values ####################################################

def make_abc_subclasses(base_class, name=Nic, inst=Nieprawda, **kwargs):
    jeżeli name jest Nic:
        name = base_class.__name__
    base = {kind: getattr(splitabc, name)
            dla kind, splitabc w abc.items()}
    zwróć {cls._KIND: cls() jeżeli inst inaczej cls
            dla cls w test_util.split_frozen(base_class, base, **kwargs)}


klasa ABCTestHarness:

    @property
    def ins(self):
        # Lazily set ins on the class.
        cls = self.SPLIT[self._KIND]
        ins = cls()
        self.__class__.ins = ins
        zwróć ins


klasa MetaPathFinder:

    def find_module(self, fullname, path):
        zwróć super().find_module(fullname, path)


klasa MetaPathFinderDefaultsTests(ABCTestHarness):

    SPLIT = make_abc_subclasses(MetaPathFinder)

    def test_find_module(self):
        # Default should zwróć Nic.
        self.assertIsNic(self.ins.find_module('something', Nic))

    def test_invalidate_caches(self):
        # Calling the method jest a no-op.
        self.ins.invalidate_caches()


(Frozen_MPFDefaultTests,
 Source_MPFDefaultTests
 ) = test_util.test_both(MetaPathFinderDefaultsTests)


klasa PathEntryFinder:

    def find_loader(self, fullname):
        zwróć super().find_loader(fullname)


klasa PathEntryFinderDefaultsTests(ABCTestHarness):

    SPLIT = make_abc_subclasses(PathEntryFinder)

    def test_find_loader(self):
        self.assertEqual((Nic, []), self.ins.find_loader('something'))

    def find_module(self):
        self.assertEqual(Nic, self.ins.find_module('something'))

    def test_invalidate_caches(self):
        # Should be a no-op.
        self.ins.invalidate_caches()


(Frozen_PEFDefaultTests,
 Source_PEFDefaultTests
 ) = test_util.test_both(PathEntryFinderDefaultsTests)


klasa Loader:

    def load_module(self, fullname):
        zwróć super().load_module(fullname)


klasa LoaderDefaultsTests(ABCTestHarness):

    SPLIT = make_abc_subclasses(Loader)

    def test_load_module(self):
        przy self.assertRaises(ImportError):
            self.ins.load_module('something')

    def test_module_repr(self):
        mod = types.ModuleType('blah')
        przy self.assertRaises(NotImplementedError):
            self.ins.module_repr(mod)
        original_repr = repr(mod)
        mod.__loader__ = self.ins
        # Should still zwróć a proper repr.
        self.assertPrawda(repr(mod))


(Frozen_LDefaultTests,
 SourceLDefaultTests
 ) = test_util.test_both(LoaderDefaultsTests)


klasa ResourceLoader(Loader):

    def get_data(self, path):
        zwróć super().get_data(path)


klasa ResourceLoaderDefaultsTests(ABCTestHarness):

    SPLIT = make_abc_subclasses(ResourceLoader)

    def test_get_data(self):
        przy self.assertRaises(IOError):
            self.ins.get_data('/some/path')


(Frozen_RLDefaultTests,
 Source_RLDefaultTests
 ) = test_util.test_both(ResourceLoaderDefaultsTests)


klasa InspectLoader(Loader):

    def is_package(self, fullname):
        zwróć super().is_package(fullname)

    def get_source(self, fullname):
        zwróć super().get_source(fullname)


SPLIT_IL = make_abc_subclasses(InspectLoader)


klasa InspectLoaderDefaultsTests(ABCTestHarness):

    SPLIT = SPLIT_IL

    def test_is_package(self):
        przy self.assertRaises(ImportError):
            self.ins.is_package('blah')

    def test_get_source(self):
        przy self.assertRaises(ImportError):
            self.ins.get_source('blah')


(Frozen_ILDefaultTests,
 Source_ILDefaultTests
 ) = test_util.test_both(InspectLoaderDefaultsTests)


klasa ExecutionLoader(InspectLoader):

    def get_filename(self, fullname):
        zwróć super().get_filename(fullname)


SPLIT_EL = make_abc_subclasses(ExecutionLoader)


klasa ExecutionLoaderDefaultsTests(ABCTestHarness):

    SPLIT = SPLIT_EL

    def test_get_filename(self):
        przy self.assertRaises(ImportError):
            self.ins.get_filename('blah')


(Frozen_ELDefaultTests,
 Source_ELDefaultsTests
 ) = test_util.test_both(InspectLoaderDefaultsTests)


##### MetaPathFinder concrete methods ##########################################
klasa MetaPathFinderFindModuleTests:

    @classmethod
    def finder(cls, spec):
        klasa MetaPathSpecFinder(cls.abc.MetaPathFinder):

            def find_spec(self, fullname, path, target=Nic):
                self.called_dla = fullname, path
                zwróć spec

        zwróć MetaPathSpecFinder()

    def test_no_spec(self):
        finder = self.finder(Nic)
        path = ['a', 'b', 'c']
        name = 'blah'
        found = finder.find_module(name, path)
        self.assertIsNic(found)
        self.assertEqual(name, finder.called_for[0])
        self.assertEqual(path, finder.called_for[1])

    def test_spec(self):
        loader = object()
        spec = self.util.spec_from_loader('blah', loader)
        finder = self.finder(spec)
        found = finder.find_module('blah', Nic)
        self.assertIs(found, spec.loader)


(Frozen_MPFFindModuleTests,
 Source_MPFFindModuleTests
 ) = test_util.test_both(MetaPathFinderFindModuleTests, abc=abc, util=util)


##### PathEntryFinder concrete methods #########################################
klasa PathEntryFinderFindLoaderTests:

    @classmethod
    def finder(cls, spec):
        klasa PathEntrySpecFinder(cls.abc.PathEntryFinder):

            def find_spec(self, fullname, target=Nic):
                self.called_dla = fullname
                zwróć spec

        zwróć PathEntrySpecFinder()

    def test_no_spec(self):
        finder = self.finder(Nic)
        name = 'blah'
        found = finder.find_loader(name)
        self.assertIsNic(found[0])
        self.assertEqual([], found[1])
        self.assertEqual(name, finder.called_for)

    def test_spec_with_loader(self):
        loader = object()
        spec = self.util.spec_from_loader('blah', loader)
        finder = self.finder(spec)
        found = finder.find_loader('blah')
        self.assertIs(found[0], spec.loader)

    def test_spec_with_portions(self):
        spec = self.machinery.ModuleSpec('blah', Nic)
        paths = ['a', 'b', 'c']
        spec.submodule_search_locations = paths
        finder = self.finder(spec)
        found = finder.find_loader('blah')
        self.assertIsNic(found[0])
        self.assertEqual(paths, found[1])


(Frozen_PEFFindLoaderTests,
 Source_PEFFindLoaderTests
 ) = test_util.test_both(PathEntryFinderFindLoaderTests, abc=abc, util=util,
                         machinery=machinery)


##### Loader concrete methods ##################################################
klasa LoaderLoadModuleTests:

    def loader(self):
        klasa SpecLoader(self.abc.Loader):
            found = Nic
            def exec_module(self, module):
                self.found = module

            def is_package(self, fullname):
                """Force some non-default module state to be set."""
                zwróć Prawda

        zwróć SpecLoader()

    def test_fresh(self):
        loader = self.loader()
        name = 'blah'
        przy test_util.uncache(name):
            loader.load_module(name)
            module = loader.found
            self.assertIs(sys.modules[name], module)
        self.assertEqual(loader, module.__loader__)
        self.assertEqual(loader, module.__spec__.loader)
        self.assertEqual(name, module.__name__)
        self.assertEqual(name, module.__spec__.name)
        self.assertIsNotNic(module.__path__)
        self.assertIsNotNic(module.__path__,
                             module.__spec__.submodule_search_locations)

    def test_reload(self):
        name = 'blah'
        loader = self.loader()
        module = types.ModuleType(name)
        module.__spec__ = self.util.spec_from_loader(name, loader)
        module.__loader__ = loader
        przy test_util.uncache(name):
            sys.modules[name] = module
            loader.load_module(name)
            found = loader.found
            self.assertIs(found, sys.modules[name])
            self.assertIs(module, sys.modules[name])


(Frozen_LoaderLoadModuleTests,
 Source_LoaderLoadModuleTests
 ) = test_util.test_both(LoaderLoadModuleTests, abc=abc, util=util)


##### InspectLoader concrete methods ###########################################
klasa InspectLoaderSourceToCodeTests:

    def source_to_module(self, data, path=Nic):
        """Help przy source_to_code() tests."""
        module = types.ModuleType('blah')
        loader = self.InspectLoaderSubclass()
        jeżeli path jest Nic:
            code = loader.source_to_code(data)
        inaczej:
            code = loader.source_to_code(data, path)
        exec(code, module.__dict__)
        zwróć module

    def test_source_to_code_source(self):
        # Since compile() can handle strings, so should source_to_code().
        source = 'attr = 42'
        module = self.source_to_module(source)
        self.assertPrawda(hasattr(module, 'attr'))
        self.assertEqual(module.attr, 42)

    def test_source_to_code_bytes(self):
        # Since compile() can handle bytes, so should source_to_code().
        source = b'attr = 42'
        module = self.source_to_module(source)
        self.assertPrawda(hasattr(module, 'attr'))
        self.assertEqual(module.attr, 42)

    def test_source_to_code_path(self):
        # Specifying a path should set it dla the code object.
        path = 'path/to/somewhere'
        loader = self.InspectLoaderSubclass()
        code = loader.source_to_code('', path)
        self.assertEqual(code.co_filename, path)

    def test_source_to_code_no_path(self):
        # Not setting a path should still work oraz be set to <string> since that
        # jest a pre-existing practice jako a default to compile().
        loader = self.InspectLoaderSubclass()
        code = loader.source_to_code('')
        self.assertEqual(code.co_filename, '<string>')


(Frozen_ILSourceToCodeTests,
 Source_ILSourceToCodeTests
 ) = test_util.test_both(InspectLoaderSourceToCodeTests,
                         InspectLoaderSubclass=SPLIT_IL)


klasa InspectLoaderGetCodeTests:

    def test_get_code(self):
        # Test success.
        module = types.ModuleType('blah')
        przy mock.patch.object(self.InspectLoaderSubclass, 'get_source') jako mocked:
            mocked.return_value = 'attr = 42'
            loader = self.InspectLoaderSubclass()
            code = loader.get_code('blah')
        exec(code, module.__dict__)
        self.assertEqual(module.attr, 42)

    def test_get_code_source_is_Nic(self):
        # If get_source() jest Nic then this should be Nic.
        przy mock.patch.object(self.InspectLoaderSubclass, 'get_source') jako mocked:
            mocked.return_value = Nic
            loader = self.InspectLoaderSubclass()
            code = loader.get_code('blah')
        self.assertIsNic(code)

    def test_get_code_source_not_found(self):
        # If there jest no source then there jest no code object.
        loader = self.InspectLoaderSubclass()
        przy self.assertRaises(ImportError):
            loader.get_code('blah')


(Frozen_ILGetCodeTests,
 Source_ILGetCodeTests
 ) = test_util.test_both(InspectLoaderGetCodeTests,
                         InspectLoaderSubclass=SPLIT_IL)


klasa InspectLoaderLoadModuleTests:

    """Test InspectLoader.load_module()."""

    module_name = 'blah'

    def setUp(self):
        support.unload(self.module_name)
        self.addCleanup(support.unload, self.module_name)

    def mock_get_code(self):
        zwróć mock.patch.object(self.InspectLoaderSubclass, 'get_code')

    def test_get_code_ImportError(self):
        # If get_code() podnieśs ImportError, it should propagate.
        przy self.mock_get_code() jako mocked_get_code:
            mocked_get_code.side_effect = ImportError
            przy self.assertRaises(ImportError):
                loader = self.InspectLoaderSubclass()
                przy warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    loader.load_module(self.module_name)

    def test_get_code_Nic(self):
        # If get_code() returns Nic, podnieś ImportError.
        przy self.mock_get_code() jako mocked_get_code:
            mocked_get_code.return_value = Nic
            przy self.assertRaises(ImportError):
                loader = self.InspectLoaderSubclass()
                loader.load_module(self.module_name)

    def test_module_returned(self):
        # The loaded module should be returned.
        code = compile('attr = 42', '<string>', 'exec')
        przy self.mock_get_code() jako mocked_get_code:
            mocked_get_code.return_value = code
            loader = self.InspectLoaderSubclass()
            module = loader.load_module(self.module_name)
            self.assertEqual(module, sys.modules[self.module_name])


(Frozen_ILLoadModuleTests,
 Source_ILLoadModuleTests
 ) = test_util.test_both(InspectLoaderLoadModuleTests,
                         InspectLoaderSubclass=SPLIT_IL)


##### ExecutionLoader concrete methods #########################################
klasa ExecutionLoaderGetCodeTests:

    def mock_methods(self, *, get_source=Nieprawda, get_filename=Nieprawda):
        source_mock_context, filename_mock_context = Nic, Nic
        jeżeli get_source:
            source_mock_context = mock.patch.object(self.ExecutionLoaderSubclass,
                                                    'get_source')
        jeżeli get_filename:
            filename_mock_context = mock.patch.object(self.ExecutionLoaderSubclass,
                                                      'get_filename')
        zwróć source_mock_context, filename_mock_context

    def test_get_code(self):
        path = 'blah.py'
        source_mock_context, filename_mock_context = self.mock_methods(
                get_source=Prawda, get_filename=Prawda)
        przy source_mock_context jako source_mock, filename_mock_context jako name_mock:
            source_mock.return_value = 'attr = 42'
            name_mock.return_value = path
            loader = self.ExecutionLoaderSubclass()
            code = loader.get_code('blah')
        self.assertEqual(code.co_filename, path)
        module = types.ModuleType('blah')
        exec(code, module.__dict__)
        self.assertEqual(module.attr, 42)

    def test_get_code_source_is_Nic(self):
        # If get_source() jest Nic then this should be Nic.
        source_mock_context, _ = self.mock_methods(get_source=Prawda)
        przy source_mock_context jako mocked:
            mocked.return_value = Nic
            loader = self.ExecutionLoaderSubclass()
            code = loader.get_code('blah')
        self.assertIsNic(code)

    def test_get_code_source_not_found(self):
        # If there jest no source then there jest no code object.
        loader = self.ExecutionLoaderSubclass()
        przy self.assertRaises(ImportError):
            loader.get_code('blah')

    def test_get_code_no_path(self):
        # If get_filename() podnieśs ImportError then simply skip setting the path
        # on the code object.
        source_mock_context, filename_mock_context = self.mock_methods(
                get_source=Prawda, get_filename=Prawda)
        przy source_mock_context jako source_mock, filename_mock_context jako name_mock:
            source_mock.return_value = 'attr = 42'
            name_mock.side_effect = ImportError
            loader = self.ExecutionLoaderSubclass()
            code = loader.get_code('blah')
        self.assertEqual(code.co_filename, '<string>')
        module = types.ModuleType('blah')
        exec(code, module.__dict__)
        self.assertEqual(module.attr, 42)


(Frozen_ELGetCodeTests,
 Source_ELGetCodeTests
 ) = test_util.test_both(ExecutionLoaderGetCodeTests,
                         ExecutionLoaderSubclass=SPLIT_EL)


##### SourceLoader concrete methods ############################################
klasa SourceOnlyLoader:

    # Globals that should be defined dla all modules.
    source = (b"_ = '::'.join([__name__, __file__, __cached__, __package__, "
              b"repr(__loader__)])")

    def __init__(self, path):
        self.path = path

    def get_data(self, path):
        jeżeli path != self.path:
            podnieś IOError
        zwróć self.source

    def get_filename(self, fullname):
        zwróć self.path

    def module_repr(self, module):
        zwróć '<module>'


SPLIT_SOL = make_abc_subclasses(SourceOnlyLoader, 'SourceLoader')


klasa SourceLoader(SourceOnlyLoader):

    source_mtime = 1

    def __init__(self, path, magic=Nic):
        super().__init__(path)
        self.bytecode_path = self.util.cache_from_source(self.path)
        self.source_size = len(self.source)
        jeżeli magic jest Nic:
            magic = self.util.MAGIC_NUMBER
        data = bytearray(magic)
        data.extend(self.init._w_long(self.source_mtime))
        data.extend(self.init._w_long(self.source_size))
        code_object = compile(self.source, self.path, 'exec',
                                dont_inherit=Prawda)
        data.extend(marshal.dumps(code_object))
        self.bytecode = bytes(data)
        self.written = {}

    def get_data(self, path):
        jeżeli path == self.path:
            zwróć super().get_data(path)
        albo_inaczej path == self.bytecode_path:
            zwróć self.bytecode
        inaczej:
            podnieś OSError

    def path_stats(self, path):
        jeżeli path != self.path:
            podnieś IOError
        zwróć {'mtime': self.source_mtime, 'size': self.source_size}

    def set_data(self, path, data):
        self.written[path] = bytes(data)
        zwróć path == self.bytecode_path


SPLIT_SL = make_abc_subclasses(SourceLoader, util=util, init=init)


klasa SourceLoaderTestHarness:

    def setUp(self, *, is_package=Prawda, **kwargs):
        self.package = 'pkg'
        jeżeli is_package:
            self.path = os.path.join(self.package, '__init__.py')
            self.name = self.package
        inaczej:
            module_name = 'mod'
            self.path = os.path.join(self.package, '.'.join(['mod', 'py']))
            self.name = '.'.join([self.package, module_name])
        self.cached = self.util.cache_from_source(self.path)
        self.loader = self.loader_mock(self.path, **kwargs)

    def verify_module(self, module):
        self.assertEqual(module.__name__, self.name)
        self.assertEqual(module.__file__, self.path)
        self.assertEqual(module.__cached__, self.cached)
        self.assertEqual(module.__package__, self.package)
        self.assertEqual(module.__loader__, self.loader)
        values = module._.split('::')
        self.assertEqual(values[0], self.name)
        self.assertEqual(values[1], self.path)
        self.assertEqual(values[2], self.cached)
        self.assertEqual(values[3], self.package)
        self.assertEqual(values[4], repr(self.loader))

    def verify_code(self, code_object):
        module = types.ModuleType(self.name)
        module.__file__ = self.path
        module.__cached__ = self.cached
        module.__package__ = self.package
        module.__loader__ = self.loader
        module.__path__ = []
        exec(code_object, module.__dict__)
        self.verify_module(module)


klasa SourceOnlyLoaderTests(SourceLoaderTestHarness):

    """Test importlib.abc.SourceLoader dla source-only loading.

    Reload testing jest subsumed by the tests for
    importlib.util.module_for_loader.

    """

    def test_get_source(self):
        # Verify the source code jest returned jako a string.
        # If an OSError jest podnieśd by get_data then podnieś ImportError.
        expected_source = self.loader.source.decode('utf-8')
        self.assertEqual(self.loader.get_source(self.name), expected_source)
        def podnieś_OSError(path):
            podnieś OSError
        self.loader.get_data = podnieś_OSError
        przy self.assertRaises(ImportError) jako cm:
            self.loader.get_source(self.name)
        self.assertEqual(cm.exception.name, self.name)

    def test_is_package(self):
        # Properly detect when loading a package.
        self.setUp(is_package=Nieprawda)
        self.assertNieprawda(self.loader.is_package(self.name))
        self.setUp(is_package=Prawda)
        self.assertPrawda(self.loader.is_package(self.name))
        self.assertNieprawda(self.loader.is_package(self.name + '.__init__'))

    def test_get_code(self):
        # Verify the code object jest created.
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object)

    def test_source_to_code(self):
        # Verify the compiled code object.
        code = self.loader.source_to_code(self.loader.source, self.path)
        self.verify_code(code)

    def test_load_module(self):
        # Loading a module should set __name__, __loader__, __package__,
        # __path__ (dla packages), __file__, oraz __cached__.
        # The module should also be put into sys.modules.
        przy test_util.uncache(self.name):
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.loader.load_module(self.name)
            self.verify_module(module)
            self.assertEqual(module.__path__, [os.path.dirname(self.path)])
            self.assertIn(self.name, sys.modules)

    def test_package_settings(self):
        # __package__ needs to be set, dopóki __path__ jest set on jeżeli the module
        # jest a package.
        # Testing the values dla a package are covered by test_load_module.
        self.setUp(is_package=Nieprawda)
        przy test_util.uncache(self.name):
            przy warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.loader.load_module(self.name)
            self.verify_module(module)
            self.assertNieprawda(hasattr(module, '__path__'))

    def test_get_source_encoding(self):
        # Source jest considered encoded w UTF-8 by default unless otherwise
        # specified by an encoding line.
        source = "_ = 'ü'"
        self.loader.source = source.encode('utf-8')
        returned_source = self.loader.get_source(self.name)
        self.assertEqual(returned_source, source)
        source = "# coding: latin-1\n_ = ü"
        self.loader.source = source.encode('latin-1')
        returned_source = self.loader.get_source(self.name)
        self.assertEqual(returned_source, source)


(Frozen_SourceOnlyLoaderTests,
 Source_SourceOnlyLoaderTests
 ) = test_util.test_both(SourceOnlyLoaderTests, util=util,
                         loader_mock=SPLIT_SOL)


@unittest.skipIf(sys.dont_write_bytecode, "sys.dont_write_bytecode jest true")
klasa SourceLoaderBytecodeTests(SourceLoaderTestHarness):

    """Test importlib.abc.SourceLoader's use of bytecode.

    Source-only testing handled by SourceOnlyLoaderTests.

    """

    def verify_code(self, code_object, *, bytecode_written=Nieprawda):
        super().verify_code(code_object)
        jeżeli bytecode_written:
            self.assertIn(self.cached, self.loader.written)
            data = bytearray(self.util.MAGIC_NUMBER)
            data.extend(self.init._w_long(self.loader.source_mtime))
            data.extend(self.init._w_long(self.loader.source_size))
            data.extend(marshal.dumps(code_object))
            self.assertEqual(self.loader.written[self.cached], bytes(data))

    def test_code_with_everything(self):
        # When everything should work.
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object)

    def test_no_bytecode(self):
        # If no bytecode exists then move on to the source.
        self.loader.bytecode_path = "<does nie exist>"
        # Sanity check
        przy self.assertRaises(OSError):
            bytecode_path = self.util.cache_from_source(self.path)
            self.loader.get_data(bytecode_path)
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object, bytecode_written=Prawda)

    def test_code_bad_timestamp(self):
        # Bytecode jest only used when the timestamp matches the source EXACTLY.
        dla source_mtime w (0, 2):
            assert source_mtime != self.loader.source_mtime
            original = self.loader.source_mtime
            self.loader.source_mtime = source_mtime
            # If bytecode jest used then EOFError would be podnieśd by marshal.
            self.loader.bytecode = self.loader.bytecode[8:]
            code_object = self.loader.get_code(self.name)
            self.verify_code(code_object, bytecode_written=Prawda)
            self.loader.source_mtime = original

    def test_code_bad_magic(self):
        # Skip over bytecode przy a bad magic number.
        self.setUp(magic=b'0000')
        # If bytecode jest used then EOFError would be podnieśd by marshal.
        self.loader.bytecode = self.loader.bytecode[8:]
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object, bytecode_written=Prawda)

    def test_dont_write_bytecode(self):
        # Bytecode jest nie written jeżeli sys.dont_write_bytecode jest true.
        # Can assume it jest false already thanks to the skipIf klasa decorator.
        spróbuj:
            sys.dont_write_bytecode = Prawda
            self.loader.bytecode_path = "<does nie exist>"
            code_object = self.loader.get_code(self.name)
            self.assertNotIn(self.cached, self.loader.written)
        w_końcu:
            sys.dont_write_bytecode = Nieprawda

    def test_no_set_data(self):
        # If set_data jest nie defined, one can still read bytecode.
        self.setUp(magic=b'0000')
        original_set_data = self.loader.__class__.mro()[1].set_data
        spróbuj:
            usuń self.loader.__class__.mro()[1].set_data
            code_object = self.loader.get_code(self.name)
            self.verify_code(code_object)
        w_końcu:
            self.loader.__class__.mro()[1].set_data = original_set_data

    def test_set_data_raises_exceptions(self):
        # Raising NotImplementedError albo OSError jest okay dla set_data.
        def podnieś_exception(exc):
            def closure(*args, **kwargs):
                podnieś exc
            zwróć closure

        self.setUp(magic=b'0000')
        self.loader.set_data = podnieś_exception(NotImplementedError)
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object)


(Frozen_SLBytecodeTests,
 SourceSLBytecodeTests
 ) = test_util.test_both(SourceLoaderBytecodeTests, init=init, util=util,
                         loader_mock=SPLIT_SL)


klasa SourceLoaderGetSourceTests:

    """Tests dla importlib.abc.SourceLoader.get_source()."""

    def test_default_encoding(self):
        # Should have no problems przy UTF-8 text.
        name = 'mod'
        mock = self.SourceOnlyLoaderMock('mod.file')
        source = 'x = "ü"'
        mock.source = source.encode('utf-8')
        returned_source = mock.get_source(name)
        self.assertEqual(returned_source, source)

    def test_decoded_source(self):
        # Decoding should work.
        name = 'mod'
        mock = self.SourceOnlyLoaderMock("mod.file")
        source = "# coding: Latin-1\nx='ü'"
        assert source.encode('latin-1') != source.encode('utf-8')
        mock.source = source.encode('latin-1')
        returned_source = mock.get_source(name)
        self.assertEqual(returned_source, source)

    def test_universal_newlines(self):
        # PEP 302 says universal newlines should be used.
        name = 'mod'
        mock = self.SourceOnlyLoaderMock('mod.file')
        source = "x = 42\r\ny = -13\r\n"
        mock.source = source.encode('utf-8')
        expect = io.IncrementalNewlineDecoder(Nic, Prawda).decode(source)
        self.assertEqual(mock.get_source(name), expect)


(Frozen_SourceOnlyLoaderGetSourceTests,
 Source_SourceOnlyLoaderGetSourceTests
 ) = test_util.test_both(SourceLoaderGetSourceTests,
                         SourceOnlyLoaderMock=SPLIT_SOL)


jeżeli __name__ == '__main__':
    unittest.main()
