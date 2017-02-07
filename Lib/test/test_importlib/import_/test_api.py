z .. zaimportuj util

z importlib zaimportuj machinery
zaimportuj sys
zaimportuj types
zaimportuj unittest

PKG_NAME = 'fine'
SUBMOD_NAME = 'fine.bogus'


klasa BadSpecFinderLoader:
    @classmethod
    def find_spec(cls, fullname, path=Nic, target=Nic):
        jeżeli fullname == SUBMOD_NAME:
            spec = machinery.ModuleSpec(fullname, cls)
            zwróć spec

    @staticmethod
    def create_module(spec):
        zwróć Nic

    @staticmethod
    def exec_module(module):
        jeżeli module.__name__ == SUBMOD_NAME:
            podnieś ImportError('I cannot be loaded!')


klasa BadLoaderFinder:
    @classmethod
    def find_module(cls, fullname, path):
        jeżeli fullname == SUBMOD_NAME:
            zwróć cls

    @classmethod
    def load_module(cls, fullname):
        jeżeli fullname == SUBMOD_NAME:
            podnieś ImportError('I cannot be loaded!')


klasa APITest:

    """Test API-specific details dla __import__ (e.g. raising the right
    exception when dalejing w an int dla the module name)."""

    def test_name_requires_rparition(self):
        # Raise TypeError jeżeli a non-string jest dalejed w dla the module name.
        przy self.assertRaises(TypeError):
            self.__import__(42)

    def test_negative_level(self):
        # Raise ValueError when a negative level jest specified.
        # PEP 328 did away przy sys.module Nic entries oraz the ambiguity of
        # absolute/relative imports.
        przy self.assertRaises(ValueError):
            self.__import__('os', globals(), level=-1)

    def test_nonexistent_fromlist_entry(self):
        # If something w fromlist doesn't exist, that's okay.
        # issue15715
        mod = types.ModuleType(PKG_NAME)
        mod.__path__ = ['XXX']
        przy util.import_state(meta_path=[self.bad_finder_loader]):
            przy util.uncache(PKG_NAME):
                sys.modules[PKG_NAME] = mod
                self.__import__(PKG_NAME, fromlist=['not here'])

    def test_fromlist_load_error_propagates(self):
        # If something w fromlist triggers an exception nie related to nie
        # existing, let that exception propagate.
        # issue15316
        mod = types.ModuleType(PKG_NAME)
        mod.__path__ = ['XXX']
        przy util.import_state(meta_path=[self.bad_finder_loader]):
            przy util.uncache(PKG_NAME):
                sys.modules[PKG_NAME] = mod
                przy self.assertRaises(ImportError):
                    self.__import__(PKG_NAME,
                                    fromlist=[SUBMOD_NAME.rpartition('.')[-1]])


klasa OldAPITests(APITest):
    bad_finder_loader = BadLoaderFinder


(Frozen_OldAPITests,
 Source_OldAPITests
 ) = util.test_both(OldAPITests, __import__=util.__import__)


klasa SpecAPITests(APITest):
    bad_finder_loader = BadSpecFinderLoader


(Frozen_SpecAPITests,
 Source_SpecAPITests
 ) = util.test_both(SpecAPITests, __import__=util.__import__)


jeżeli __name__ == '__main__':
    unittest.main()
