"""Test that the semantics relating to the 'fromlist' argument are correct."""
z .. zaimportuj util
zaimportuj unittest


klasa ReturnValue:

    """The use of fromlist influences what zaimportuj returns.

    If direct ``zaimportuj ...`` statement jest used, the root module albo package jest
    returned [zaimportuj return]. But jeżeli fromlist jest set, then the specified module
    jest actually returned (whether it jest a relative zaimportuj albo not)
    [z return].

    """

    def test_return_from_import(self):
        # [zaimportuj return]
        przy util.mock_spec('pkg.__init__', 'pkg.module') jako importer:
            przy util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.module')
                self.assertEqual(module.__name__, 'pkg')

    def test_return_from_from_import(self):
        # [z return]
        przy util.mock_modules('pkg.__init__', 'pkg.module')as importer:
            przy util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.module', fromlist=['attr'])
                self.assertEqual(module.__name__, 'pkg.module')


(Frozen_ReturnValue,
 Source_ReturnValue
 ) = util.test_both(ReturnValue, __import__=util.__import__)


klasa HandlingFromlist:

    """Using fromlist triggers different actions based on what jest being asked
    of it.

    If fromlist specifies an object on a module, nothing special happens
    [object case]. This jest even true jeżeli the object does nie exist [bad object].

    If a package jest being imported, then what jest listed w fromlist may be
    treated jako a module to be imported [module]. And this extends to what jest
    contained w __all__ when '*' jest imported [using *]. And '*' does nie need
    to be the only name w the fromlist [using * przy others].

    """

    def test_object(self):
        # [object case]
        przy util.mock_modules('module') jako importer:
            przy util.import_state(meta_path=[importer]):
                module = self.__import__('module', fromlist=['attr'])
                self.assertEqual(module.__name__, 'module')

    def test_nonexistent_object(self):
        # [bad object]
        przy util.mock_modules('module') jako importer:
            przy util.import_state(meta_path=[importer]):
                module = self.__import__('module', fromlist=['non_existent'])
                self.assertEqual(module.__name__, 'module')
                self.assertNieprawda(hasattr(module, 'non_existent'))

    def test_module_from_package(self):
        # [module]
        przy util.mock_modules('pkg.__init__', 'pkg.module') jako importer:
            przy util.import_state(meta_path=[importer]):
                module = self.__import__('pkg', fromlist=['module'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertPrawda(hasattr(module, 'module'))
                self.assertEqual(module.module.__name__, 'pkg.module')

    def test_module_from_package_triggers_ImportError(self):
        # If a submodule causes an ImportError because it tries to import
        # a module which doesn't exist, that should let the ImportError
        # propagate.
        def module_code():
            zaimportuj i_do_not_exist
        przy util.mock_modules('pkg.__init__', 'pkg.mod',
                               module_code={'pkg.mod': module_code}) jako importer:
            przy util.import_state(meta_path=[importer]):
                przy self.assertRaises(ImportError) jako exc:
                    self.__import__('pkg', fromlist=['mod'])
                self.assertEqual('i_do_not_exist', exc.exception.name)

    def test_empty_string(self):
        przy util.mock_modules('pkg.__init__', 'pkg.mod') jako importer:
            przy util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.mod', fromlist=[''])
                self.assertEqual(module.__name__, 'pkg.mod')

    def basic_star_test(self, fromlist=['*']):
        # [using *]
        przy util.mock_modules('pkg.__init__', 'pkg.module') jako mock:
            przy util.import_state(meta_path=[mock]):
                mock['pkg'].__all__ = ['module']
                module = self.__import__('pkg', fromlist=fromlist)
                self.assertEqual(module.__name__, 'pkg')
                self.assertPrawda(hasattr(module, 'module'))
                self.assertEqual(module.module.__name__, 'pkg.module')

    def test_using_star(self):
        # [using *]
        self.basic_star_test()

    def test_fromlist_as_tuple(self):
        self.basic_star_test(('*',))

    def test_star_with_others(self):
        # [using * przy others]
        context = util.mock_modules('pkg.__init__', 'pkg.module1', 'pkg.module2')
        przy context jako mock:
            przy util.import_state(meta_path=[mock]):
                mock['pkg'].__all__ = ['module1']
                module = self.__import__('pkg', fromlist=['module2', '*'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertPrawda(hasattr(module, 'module1'))
                self.assertPrawda(hasattr(module, 'module2'))
                self.assertEqual(module.module1.__name__, 'pkg.module1')
                self.assertEqual(module.module2.__name__, 'pkg.module2')


(Frozen_FromList,
 Source_FromList
 ) = util.test_both(HandlingFromlist, __import__=util.__import__)


jeżeli __name__ == '__main__':
    unittest.main()
