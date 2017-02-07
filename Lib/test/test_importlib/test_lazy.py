zaimportuj importlib
z importlib zaimportuj abc
z importlib zaimportuj util
zaimportuj unittest

z . zaimportuj util jako test_util


klasa CollectInit:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def exec_module(self, module):
        zwróć self


klasa LazyLoaderFactoryTests(unittest.TestCase):

    def test_init(self):
        factory = util.LazyLoader.factory(CollectInit)
        # E.g. what importlib.machinery.FileFinder instantiates loaders with
        # plus keyword arguments.
        lazy_loader = factory('module name', 'module path', kw='kw')
        loader = lazy_loader.loader
        self.assertEqual(('module name', 'module path'), loader.args)
        self.assertEqual({'kw': 'kw'}, loader.kwargs)

    def test_validation(self):
        # No exec_module(), no lazy loading.
        przy self.assertRaises(TypeError):
            util.LazyLoader.factory(object)


klasa TestingImporter(abc.MetaPathFinder, abc.Loader):

    module_name = 'lazy_loader_test'
    mutated_name = 'changed'
    loaded = Nic
    source_code = 'attr = 42; __name__ = {!r}'.format(mutated_name)

    def find_spec(self, name, path, target=Nic):
        jeżeli name != self.module_name:
            zwróć Nic
        zwróć util.spec_from_loader(name, util.LazyLoader(self))

    def exec_module(self, module):
        exec(self.source_code, module.__dict__)
        self.loaded = module


klasa LazyLoaderTests(unittest.TestCase):

    def test_init(self):
        przy self.assertRaises(TypeError):
            util.LazyLoader(object)

    def new_module(self, source_code=Nic):
        loader = TestingImporter()
        jeżeli source_code jest nie Nic:
            loader.source_code = source_code
        spec = util.spec_from_loader(TestingImporter.module_name,
                                     util.LazyLoader(loader))
        module = spec.loader.create_module(spec)
        module.__spec__ = spec
        module.__loader__ = spec.loader
        spec.loader.exec_module(module)
        # Module jest now lazy.
        self.assertIsNic(loader.loaded)
        zwróć module

    def test_e2e(self):
        # End-to-end test to verify the load jest w fact lazy.
        importer = TestingImporter()
        assert importer.loaded jest Nic
        przy test_util.uncache(importer.module_name):
            przy test_util.import_state(meta_path=[importer]):
                module = importlib.import_module(importer.module_name)
        self.assertIsNic(importer.loaded)
        # Trigger load.
        self.assertEqual(module.__loader__, importer)
        self.assertIsNotNic(importer.loaded)
        self.assertEqual(module, importer.loaded)

    def test_attr_unchanged(self):
        # An attribute only mutated jako a side-effect of zaimportuj should nie be
        # changed needlessly.
        module = self.new_module()
        self.assertEqual(TestingImporter.mutated_name, module.__name__)

    def test_new_attr(self):
        # A new attribute should persist.
        module = self.new_module()
        module.new_attr = 42
        self.assertEqual(42, module.new_attr)

    def test_mutated_preexisting_attr(self):
        # Changing an attribute that already existed on the module --
        # e.g. __name__ -- should persist.
        module = self.new_module()
        module.__name__ = 'bogus'
        self.assertEqual('bogus', module.__name__)

    def test_mutated_attr(self):
        # Changing an attribute that comes into existence after an import
        # should persist.
        module = self.new_module()
        module.attr = 6
        self.assertEqual(6, module.attr)

    def test_delete_eventual_attr(self):
        # Deleting an attribute should stay deleted.
        module = self.new_module()
        usuń module.attr
        self.assertNieprawda(hasattr(module, 'attr'))

    def test_delete_preexisting_attr(self):
        module = self.new_module()
        usuń module.__name__
        self.assertNieprawda(hasattr(module, '__name__'))

    def test_module_substitution_error(self):
        source_code = 'zaimportuj sys; sys.modules[__name__] = 42'
        module = self.new_module(source_code)
        przy test_util.uncache(TestingImporter.module_name):
            przy self.assertRaises(ValueError):
                module.__name__


jeżeli __name__ == '__main__':
    unittest.main()
