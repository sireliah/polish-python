z importlib zaimportuj machinery
zaimportuj sys
zaimportuj types
zaimportuj unittest

z .. zaimportuj util


klasa SpecLoaderMock:

    def find_spec(self, fullname, path=Nic, target=Nic):
        zwróć machinery.ModuleSpec(fullname, self)

    def create_module(self, spec):
        zwróć Nic

    def exec_module(self, module):
        dalej


klasa SpecLoaderAttributeTests:

    def test___loader__(self):
        loader = SpecLoaderMock()
        przy util.uncache('blah'), util.import_state(meta_path=[loader]):
            module = self.__import__('blah')
        self.assertEqual(loader, module.__loader__)


(Frozen_SpecTests,
 Source_SpecTests
 ) = util.test_both(SpecLoaderAttributeTests, __import__=util.__import__)


klasa LoaderMock:

    def find_module(self, fullname, path=Nic):
        zwróć self

    def load_module(self, fullname):
        sys.modules[fullname] = self.module
        zwróć self.module


klasa LoaderAttributeTests:

    def test___loader___missing(self):
        module = types.ModuleType('blah')
        spróbuj:
            usuń module.__loader__
        wyjąwszy AttributeError:
            dalej
        loader = LoaderMock()
        loader.module = module
        przy util.uncache('blah'), util.import_state(meta_path=[loader]):
            module = self.__import__('blah')
        self.assertEqual(loader, module.__loader__)

    def test___loader___is_Nic(self):
        module = types.ModuleType('blah')
        module.__loader__ = Nic
        loader = LoaderMock()
        loader.module = module
        przy util.uncache('blah'), util.import_state(meta_path=[loader]):
            returned_module = self.__import__('blah')
        self.assertEqual(loader, module.__loader__)


(Frozen_Tests,
 Source_Tests
 ) = util.test_both(LoaderAttributeTests, __import__=util.__import__)


jeżeli __name__ == '__main__':
    unittest.main()
