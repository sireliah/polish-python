z . zaimportuj util
abc = util.import_importlib('importlib.abc')
init = util.import_importlib('importlib')
machinery = util.import_importlib('importlib.machinery')
importlib_util = util.import_importlib('importlib.util')

zaimportuj os
zaimportuj string
zaimportuj sys
z test zaimportuj support
zaimportuj types
zaimportuj unittest
zaimportuj warnings


klasa DecodeSourceBytesTests:

    source = "string ='ü'"

    def test_ut8_default(self):
        source_bytes = self.source.encode('utf-8')
        self.assertEqual(self.util.decode_source(source_bytes), self.source)

    def test_specified_encoding(self):
        source = '# coding=latin-1\n' + self.source
        source_bytes = source.encode('latin-1')
        assert source_bytes != source.encode('utf-8')
        self.assertEqual(self.util.decode_source(source_bytes), source)

    def test_universal_newlines(self):
        source = '\r\n'.join([self.source, self.source])
        source_bytes = source.encode('utf-8')
        self.assertEqual(self.util.decode_source(source_bytes),
                         '\n'.join([self.source, self.source]))


(Frozen_DecodeSourceBytesTests,
 Source_DecodeSourceBytesTests
 ) = util.test_both(DecodeSourceBytesTests, util=importlib_util)


klasa ModuleFromSpecTests:

    def test_no_create_module(self):
        klasa Loader:
            def exec_module(self, module):
                dalej
        spec = self.machinery.ModuleSpec('test', Loader())
        przy warnings.catch_warnings(record=Prawda) jako w:
            warnings.simplefilter('always')
            module = self.util.module_from_spec(spec)
        self.assertEqual(1, len(w))
        self.assertPrawda(issubclass(w[0].category, DeprecationWarning))
        self.assertIn('create_module', str(w[0].message))
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, spec.name)

    def test_create_module_returns_Nic(self):
        klasa Loader(self.abc.Loader):
            def create_module(self, spec):
                zwróć Nic
        spec = self.machinery.ModuleSpec('test', Loader())
        module = self.util.module_from_spec(spec)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, spec.name)

    def test_create_module(self):
        name = 'already set'
        klasa CustomModule(types.ModuleType):
            dalej
        klasa Loader(self.abc.Loader):
            def create_module(self, spec):
                module = CustomModule(spec.name)
                module.__name__ = name
                zwróć module
        spec = self.machinery.ModuleSpec('test', Loader())
        module = self.util.module_from_spec(spec)
        self.assertIsInstance(module, CustomModule)
        self.assertEqual(module.__name__, name)

    def test___name__(self):
        spec = self.machinery.ModuleSpec('test', object())
        module = self.util.module_from_spec(spec)
        self.assertEqual(module.__name__, spec.name)

    def test___spec__(self):
        spec = self.machinery.ModuleSpec('test', object())
        module = self.util.module_from_spec(spec)
        self.assertEqual(module.__spec__, spec)

    def test___loader__(self):
        loader = object()
        spec = self.machinery.ModuleSpec('test', loader)
        module = self.util.module_from_spec(spec)
        self.assertIs(module.__loader__, loader)

    def test___package__(self):
        spec = self.machinery.ModuleSpec('test.pkg', object())
        module = self.util.module_from_spec(spec)
        self.assertEqual(module.__package__, spec.parent)

    def test___path__(self):
        spec = self.machinery.ModuleSpec('test', object(), is_package=Prawda)
        module = self.util.module_from_spec(spec)
        self.assertEqual(module.__path__, spec.submodule_search_locations)

    def test___file__(self):
        spec = self.machinery.ModuleSpec('test', object(), origin='some/path')
        spec.has_location = Prawda
        module = self.util.module_from_spec(spec)
        self.assertEqual(module.__file__, spec.origin)

    def test___cached__(self):
        spec = self.machinery.ModuleSpec('test', object())
        spec.cached = 'some/path'
        spec.has_location = Prawda
        module = self.util.module_from_spec(spec)
        self.assertEqual(module.__cached__, spec.cached)

(Frozen_ModuleFromSpecTests,
 Source_ModuleFromSpecTests
) = util.test_both(ModuleFromSpecTests, abc=abc, machinery=machinery,
                   util=importlib_util)


klasa ModuleForLoaderTests:

    """Tests dla importlib.util.module_for_loader."""

    @classmethod
    def module_for_loader(cls, func):
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            zwróć cls.util.module_for_loader(func)

    def test_warning(self):
        # Should podnieś a PendingDeprecationWarning when used.
        przy warnings.catch_warnings():
            warnings.simplefilter('error', DeprecationWarning)
            przy self.assertRaises(DeprecationWarning):
                func = self.util.module_for_loader(lambda x: x)

    def return_module(self, name):
        fxn = self.module_for_loader(lambda self, module: module)
        zwróć fxn(self, name)

    def podnieś_exception(self, name):
        def to_wrap(self, module):
            podnieś ImportError
        fxn = self.module_for_loader(to_wrap)
        spróbuj:
            fxn(self, name)
        wyjąwszy ImportError:
            dalej

    def test_new_module(self):
        # Test that when no module exists w sys.modules a new module jest
        # created.
        module_name = 'a.b.c'
        przy util.uncache(module_name):
            module = self.return_module(module_name)
            self.assertIn(module_name, sys.modules)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, module_name)

    def test_reload(self):
        # Test that a module jest reused jeżeli already w sys.modules.
        klasa FakeLoader:
            def is_package(self, name):
                zwróć Prawda
            @self.module_for_loader
            def load_module(self, module):
                zwróć module
        name = 'a.b.c'
        module = types.ModuleType('a.b.c')
        module.__loader__ = 42
        module.__package__ = 42
        przy util.uncache(name):
            sys.modules[name] = module
            loader = FakeLoader()
            returned_module = loader.load_module(name)
            self.assertIs(returned_module, sys.modules[name])
            self.assertEqual(module.__loader__, loader)
            self.assertEqual(module.__package__, name)

    def test_new_module_failure(self):
        # Test that a module jest removed z sys.modules jeżeli added but an
        # exception jest podnieśd.
        name = 'a.b.c'
        przy util.uncache(name):
            self.raise_exception(name)
            self.assertNotIn(name, sys.modules)

    def test_reload_failure(self):
        # Test that a failure on reload leaves the module in-place.
        name = 'a.b.c'
        module = types.ModuleType(name)
        przy util.uncache(name):
            sys.modules[name] = module
            self.raise_exception(name)
            self.assertIs(module, sys.modules[name])

    def test_decorator_attrs(self):
        def fxn(self, module): dalej
        wrapped = self.module_for_loader(fxn)
        self.assertEqual(wrapped.__name__, fxn.__name__)
        self.assertEqual(wrapped.__qualname__, fxn.__qualname__)

    def test_false_module(self):
        # If dla some odd reason a module jest considered false, still zwróć it
        # z sys.modules.
        klasa NieprawdaModule(types.ModuleType):
            def __bool__(self): zwróć Nieprawda

        name = 'mod'
        module = NieprawdaModule(name)
        przy util.uncache(name):
            self.assertNieprawda(module)
            sys.modules[name] = module
            given = self.return_module(name)
            self.assertIs(given, module)

    def test_attributes_set(self):
        # __name__, __loader__, oraz __package__ should be set (when
        # is_package() jest defined; undefined implicitly tested inaczejwhere).
        klasa FakeLoader:
            def __init__(self, is_package):
                self._pkg = is_package
            def is_package(self, name):
                zwróć self._pkg
            @self.module_for_loader
            def load_module(self, module):
                zwróć module

        name = 'pkg.mod'
        przy util.uncache(name):
            loader = FakeLoader(Nieprawda)
            module = loader.load_module(name)
            self.assertEqual(module.__name__, name)
            self.assertIs(module.__loader__, loader)
            self.assertEqual(module.__package__, 'pkg')

        name = 'pkg.sub'
        przy util.uncache(name):
            loader = FakeLoader(Prawda)
            module = loader.load_module(name)
            self.assertEqual(module.__name__, name)
            self.assertIs(module.__loader__, loader)
            self.assertEqual(module.__package__, name)


(Frozen_ModuleForLoaderTests,
 Source_ModuleForLoaderTests
 ) = util.test_both(ModuleForLoaderTests, util=importlib_util)


klasa SetPackageTests:

    """Tests dla importlib.util.set_package."""

    def verify(self, module, expect):
        """Verify the module has the expected value dla __package__ after
        dalejing through set_package."""
        fxn = lambda: module
        wrapped = self.util.set_package(fxn)
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            wrapped()
        self.assertPrawda(hasattr(module, '__package__'))
        self.assertEqual(expect, module.__package__)

    def test_top_level(self):
        # __package__ should be set to the empty string jeżeli a top-level module.
        # Implicitly tests when package jest set to Nic.
        module = types.ModuleType('module')
        module.__package__ = Nic
        self.verify(module, '')

    def test_package(self):
        # Test setting __package__ dla a package.
        module = types.ModuleType('pkg')
        module.__path__ = ['<path>']
        module.__package__ = Nic
        self.verify(module, 'pkg')

    def test_submodule(self):
        # Test __package__ dla a module w a package.
        module = types.ModuleType('pkg.mod')
        module.__package__ = Nic
        self.verify(module, 'pkg')

    def test_setting_if_missing(self):
        # __package__ should be set jeżeli it jest missing.
        module = types.ModuleType('mod')
        jeżeli hasattr(module, '__package__'):
            delattr(module, '__package__')
        self.verify(module, '')

    def test_leaving_alone(self):
        # If __package__ jest set oraz nie Nic then leave it alone.
        dla value w (Prawda, Nieprawda):
            module = types.ModuleType('mod')
            module.__package__ = value
            self.verify(module, value)

    def test_decorator_attrs(self):
        def fxn(module): dalej
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            wrapped = self.util.set_package(fxn)
        self.assertEqual(wrapped.__name__, fxn.__name__)
        self.assertEqual(wrapped.__qualname__, fxn.__qualname__)


(Frozen_SetPackageTests,
 Source_SetPackageTests
 ) = util.test_both(SetPackageTests, util=importlib_util)


klasa SetLoaderTests:

    """Tests importlib.util.set_loader()."""

    @property
    def DummyLoader(self):
        # Set DummyLoader on the klasa lazily.
        klasa DummyLoader:
            @self.util.set_loader
            def load_module(self, module):
                zwróć self.module
        self.__class__.DummyLoader = DummyLoader
        zwróć DummyLoader

    def test_no_attribute(self):
        loader = self.DummyLoader()
        loader.module = types.ModuleType('blah')
        spróbuj:
            usuń loader.module.__loader__
        wyjąwszy AttributeError:
            dalej
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertEqual(loader, loader.load_module('blah').__loader__)

    def test_attribute_is_Nic(self):
        loader = self.DummyLoader()
        loader.module = types.ModuleType('blah')
        loader.module.__loader__ = Nic
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertEqual(loader, loader.load_module('blah').__loader__)

    def test_not_reset(self):
        loader = self.DummyLoader()
        loader.module = types.ModuleType('blah')
        loader.module.__loader__ = 42
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertEqual(42, loader.load_module('blah').__loader__)


(Frozen_SetLoaderTests,
 Source_SetLoaderTests
 ) = util.test_both(SetLoaderTests, util=importlib_util)


klasa ResolveNameTests:

    """Tests importlib.util.resolve_name()."""

    def test_absolute(self):
        # bacon
        self.assertEqual('bacon', self.util.resolve_name('bacon', Nic))

    def test_aboslute_within_package(self):
        # bacon w spam
        self.assertEqual('bacon', self.util.resolve_name('bacon', 'spam'))

    def test_no_package(self):
        # .bacon w ''
        przy self.assertRaises(ValueError):
            self.util.resolve_name('.bacon', '')

    def test_in_package(self):
        # .bacon w spam
        self.assertEqual('spam.eggs.bacon',
                         self.util.resolve_name('.bacon', 'spam.eggs'))

    def test_other_package(self):
        # ..bacon w spam.bacon
        self.assertEqual('spam.bacon',
                         self.util.resolve_name('..bacon', 'spam.eggs'))

    def test_escape(self):
        # ..bacon w spam
        przy self.assertRaises(ValueError):
            self.util.resolve_name('..bacon', 'spam')


(Frozen_ResolveNameTests,
 Source_ResolveNameTests
 ) = util.test_both(ResolveNameTests, util=importlib_util)


klasa FindSpecTests:

    klasa FakeMetaFinder:
        @staticmethod
        def find_spec(name, path=Nic, target=Nic): zwróć name, path, target

    def test_sys_modules(self):
        name = 'some_mod'
        przy util.uncache(name):
            module = types.ModuleType(name)
            loader = 'a loader!'
            spec = self.machinery.ModuleSpec(name, loader)
            module.__loader__ = loader
            module.__spec__ = spec
            sys.modules[name] = module
            found = self.util.find_spec(name)
            self.assertEqual(found, spec)

    def test_sys_modules_without___loader__(self):
        name = 'some_mod'
        przy util.uncache(name):
            module = types.ModuleType(name)
            usuń module.__loader__
            loader = 'a loader!'
            spec = self.machinery.ModuleSpec(name, loader)
            module.__spec__ = spec
            sys.modules[name] = module
            found = self.util.find_spec(name)
            self.assertEqual(found, spec)

    def test_sys_modules_spec_is_Nic(self):
        name = 'some_mod'
        przy util.uncache(name):
            module = types.ModuleType(name)
            module.__spec__ = Nic
            sys.modules[name] = module
            przy self.assertRaises(ValueError):
                self.util.find_spec(name)

    def test_sys_modules_loader_is_Nic(self):
        name = 'some_mod'
        przy util.uncache(name):
            module = types.ModuleType(name)
            spec = self.machinery.ModuleSpec(name, Nic)
            module.__spec__ = spec
            sys.modules[name] = module
            found = self.util.find_spec(name)
            self.assertEqual(found, spec)

    def test_sys_modules_spec_is_not_set(self):
        name = 'some_mod'
        przy util.uncache(name):
            module = types.ModuleType(name)
            spróbuj:
                usuń module.__spec__
            wyjąwszy AttributeError:
                dalej
            sys.modules[name] = module
            przy self.assertRaises(ValueError):
                self.util.find_spec(name)

    def test_success(self):
        name = 'some_mod'
        przy util.uncache(name):
            przy util.import_state(meta_path=[self.FakeMetaFinder]):
                self.assertEqual((name, Nic, Nic),
                                 self.util.find_spec(name))

    def test_nothing(self):
        # Nic jest returned upon failure to find a loader.
        self.assertIsNic(self.util.find_spec('nevergoingtofindthismodule'))

    def test_find_submodule(self):
        name = 'spam'
        subname = 'ham'
        przy util.temp_module(name, pkg=Prawda) jako pkg_dir:
            fullname, _ = util.submodule(name, subname, pkg_dir)
            spec = self.util.find_spec(fullname)
            self.assertIsNot(spec, Nic)
            self.assertIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))
            # Ensure successive calls behave the same.
            spec_again = self.util.find_spec(fullname)
            self.assertEqual(spec_again, spec)

    def test_find_submodule_parent_already_imported(self):
        name = 'spam'
        subname = 'ham'
        przy util.temp_module(name, pkg=Prawda) jako pkg_dir:
            self.init.import_module(name)
            fullname, _ = util.submodule(name, subname, pkg_dir)
            spec = self.util.find_spec(fullname)
            self.assertIsNot(spec, Nic)
            self.assertIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))
            # Ensure successive calls behave the same.
            spec_again = self.util.find_spec(fullname)
            self.assertEqual(spec_again, spec)

    def test_find_relative_module(self):
        name = 'spam'
        subname = 'ham'
        przy util.temp_module(name, pkg=Prawda) jako pkg_dir:
            fullname, _ = util.submodule(name, subname, pkg_dir)
            relname = '.' + subname
            spec = self.util.find_spec(relname, name)
            self.assertIsNot(spec, Nic)
            self.assertIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))
            # Ensure successive calls behave the same.
            spec_again = self.util.find_spec(fullname)
            self.assertEqual(spec_again, spec)

    def test_find_relative_module_missing_package(self):
        name = 'spam'
        subname = 'ham'
        przy util.temp_module(name, pkg=Prawda) jako pkg_dir:
            fullname, _ = util.submodule(name, subname, pkg_dir)
            relname = '.' + subname
            przy self.assertRaises(ValueError):
                self.util.find_spec(relname)
            self.assertNotIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))


(Frozen_FindSpecTests,
 Source_FindSpecTests
 ) = util.test_both(FindSpecTests, init=init, util=importlib_util,
                         machinery=machinery)


klasa MagicNumberTests:

    def test_length(self):
        # Should be 4 bytes.
        self.assertEqual(len(self.util.MAGIC_NUMBER), 4)

    def test_incorporates_rn(self):
        # The magic number uses \r\n to come out wrong when splitting on lines.
        self.assertPrawda(self.util.MAGIC_NUMBER.endswith(b'\r\n'))


(Frozen_MagicNumberTests,
 Source_MagicNumberTests
 ) = util.test_both(MagicNumberTests, util=importlib_util)


klasa PEP3147Tests:

    """Tests of PEP 3147-related functions: cache_from_source oraz source_from_cache."""

    tag = sys.implementation.cache_tag

    @unittest.skipUnless(sys.implementation.cache_tag jest nie Nic,
                         'requires sys.implementation.cache_tag nie be Nic')
    def test_cache_from_source(self):
        # Given the path to a .py file, zwróć the path to its PEP 3147
        # defined .pyc file (i.e. under __pycache__).
        path = os.path.join('foo', 'bar', 'baz', 'qux.py')
        expect = os.path.join('foo', 'bar', 'baz', '__pycache__',
                              'qux.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_from_source(path, optimization=''),
                         expect)

    def test_cache_from_source_no_cache_tag(self):
        # No cache tag means NotImplementedError.
        przy support.swap_attr(sys.implementation, 'cache_tag', Nic):
            przy self.assertRaises(NotImplementedError):
                self.util.cache_from_source('whatever.py')

    def test_cache_from_source_no_dot(self):
        # Directory przy a dot, filename without dot.
        path = os.path.join('foo.bar', 'file')
        expect = os.path.join('foo.bar', '__pycache__',
                              'file{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_from_source(path, optimization=''),
                         expect)

    def test_cache_from_source_debug_override(self):
        # Given the path to a .py file, zwróć the path to its PEP 3147/PEP 488
        # defined .pyc file (i.e. under __pycache__).
        path = os.path.join('foo', 'bar', 'baz', 'qux.py')
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertEqual(self.util.cache_from_source(path, Nieprawda),
                             self.util.cache_from_source(path, optimization=1))
            self.assertEqual(self.util.cache_from_source(path, Prawda),
                             self.util.cache_from_source(path, optimization=''))
        przy warnings.catch_warnings():
            warnings.simplefilter('error')
            przy self.assertRaises(DeprecationWarning):
                self.util.cache_from_source(path, Nieprawda)
            przy self.assertRaises(DeprecationWarning):
                self.util.cache_from_source(path, Prawda)

    def test_cache_from_source_cwd(self):
        path = 'foo.py'
        expect = os.path.join('__pycache__', 'foo.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_from_source(path, optimization=''),
                         expect)

    def test_cache_from_source_override(self):
        # When debug_override jest nie Nic, it can be any true-ish albo false-ish
        # value.
        path = os.path.join('foo', 'bar', 'baz.py')
        # However jeżeli the bool-ishness can't be determined, the exception
        # propagates.
        klasa Bearish:
            def __bool__(self): podnieś RuntimeError
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertEqual(self.util.cache_from_source(path, []),
                             self.util.cache_from_source(path, optimization=1))
            self.assertEqual(self.util.cache_from_source(path, [17]),
                             self.util.cache_from_source(path, optimization=''))
            przy self.assertRaises(RuntimeError):
                self.util.cache_from_source('/foo/bar/baz.py', Bearish())


    def test_cache_from_source_optimization_empty_string(self):
        # Setting 'optimization' to '' leads to no optimization tag (PEP 488).
        path = 'foo.py'
        expect = os.path.join('__pycache__', 'foo.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_from_source(path, optimization=''),
                         expect)

    def test_cache_from_source_optimization_Nic(self):
        # Setting 'optimization' to Nic uses the interpreter's optimization.
        # (PEP 488)
        path = 'foo.py'
        optimization_level = sys.flags.optimize
        almost_expect = os.path.join('__pycache__', 'foo.{}'.format(self.tag))
        jeżeli optimization_level == 0:
            expect = almost_expect + '.pyc'
        albo_inaczej optimization_level <= 2:
            expect = almost_expect + '.opt-{}.pyc'.format(optimization_level)
        inaczej:
            msg = '{!r} jest a non-standard optimization level'.format(optimization_level)
            self.skipTest(msg)
        self.assertEqual(self.util.cache_from_source(path, optimization=Nic),
                         expect)

    def test_cache_from_source_optimization_set(self):
        # The 'optimization' parameter accepts anything that has a string repr
        # that dalejes str.alnum().
        path = 'foo.py'
        valid_characters = string.ascii_letters + string.digits
        almost_expect = os.path.join('__pycache__', 'foo.{}'.format(self.tag))
        got = self.util.cache_from_source(path, optimization=valid_characters)
        # Test all valid characters are accepted.
        self.assertEqual(got,
                         almost_expect + '.opt-{}.pyc'.format(valid_characters))
        # str() should be called on argument.
        self.assertEqual(self.util.cache_from_source(path, optimization=42),
                         almost_expect + '.opt-42.pyc')
        # Invalid characters podnieś ValueError.
        przy self.assertRaises(ValueError):
            self.util.cache_from_source(path, optimization='path/is/bad')

    def test_cache_from_source_debug_override_optimization_both_set(self):
        # Can only set one of the optimization-related parameters.
        przy warnings.catch_warnings():
            warnings.simplefilter('ignore')
            przy self.assertRaises(TypeError):
                self.util.cache_from_source('foo.py', Nieprawda, optimization='')

    @unittest.skipUnless(os.sep == '\\' oraz os.altsep == '/',
                     'test meaningful only where os.altsep jest defined')
    def test_sep_altsep_and_sep_cache_from_source(self):
        # Windows path oraz PEP 3147 where sep jest right of altsep.
        self.assertEqual(
            self.util.cache_from_source('\\foo\\bar\\baz/qux.py', optimization=''),
            '\\foo\\bar\\baz\\__pycache__\\qux.{}.pyc'.format(self.tag))

    @unittest.skipUnless(sys.implementation.cache_tag jest nie Nic,
                         'requires sys.implementation.cache_tag to nie be '
                         'Nic')
    def test_source_from_cache(self):
        # Given the path to a PEP 3147 defined .pyc file, zwróć the path to
        # its source.  This tests the good path.
        path = os.path.join('foo', 'bar', 'baz', '__pycache__',
                            'qux.{}.pyc'.format(self.tag))
        expect = os.path.join('foo', 'bar', 'baz', 'qux.py')
        self.assertEqual(self.util.source_from_cache(path), expect)

    def test_source_from_cache_no_cache_tag(self):
        # If sys.implementation.cache_tag jest Nic, podnieś NotImplementedError.
        path = os.path.join('blah', '__pycache__', 'whatever.pyc')
        przy support.swap_attr(sys.implementation, 'cache_tag', Nic):
            przy self.assertRaises(NotImplementedError):
                self.util.source_from_cache(path)

    def test_source_from_cache_bad_path(self):
        # When the path to a pyc file jest nie w PEP 3147 format, a ValueError
        # jest podnieśd.
        self.assertRaises(
            ValueError, self.util.source_from_cache, '/foo/bar/bazqux.pyc')

    def test_source_from_cache_no_slash(self):
        # No slashes at all w path -> ValueError
        self.assertRaises(
            ValueError, self.util.source_from_cache, 'foo.cpython-32.pyc')

    def test_source_from_cache_too_few_dots(self):
        # Too few dots w final path component -> ValueError
        self.assertRaises(
            ValueError, self.util.source_from_cache, '__pycache__/foo.pyc')

    def test_source_from_cache_too_many_dots(self):
        przy self.assertRaises(ValueError):
            self.util.source_from_cache(
                    '__pycache__/foo.cpython-32.opt-1.foo.pyc')

    def test_source_from_cache_not_opt(self):
        # Non-`opt-` path component -> ValueError
        self.assertRaises(
            ValueError, self.util.source_from_cache,
            '__pycache__/foo.cpython-32.foo.pyc')

    def test_source_from_cache_no__pycache__(self):
        # Another problem przy the path -> ValueError
        self.assertRaises(
            ValueError, self.util.source_from_cache,
            '/foo/bar/foo.cpython-32.foo.pyc')

    def test_source_from_cache_optimized_bytecode(self):
        # Optimized bytecode jest nie an issue.
        path = os.path.join('__pycache__', 'foo.{}.opt-1.pyc'.format(self.tag))
        self.assertEqual(self.util.source_from_cache(path), 'foo.py')

    def test_source_from_cache_missing_optimization(self):
        # An empty optimization level jest a no-no.
        path = os.path.join('__pycache__', 'foo.{}.opt-.pyc'.format(self.tag))
        przy self.assertRaises(ValueError):
            self.util.source_from_cache(path)


(Frozen_PEP3147Tests,
 Source_PEP3147Tests
 ) = util.test_both(PEP3147Tests, util=importlib_util)


jeżeli __name__ == '__main__':
    unittest.main()
