z .. zaimportuj util
zaimportuj sys
zaimportuj unittest
zaimportuj importlib
z test zaimportuj support


klasa ParentModuleTests:

    """Importing a submodule should zaimportuj the parent modules."""

    def test_import_parent(self):
        przy util.mock_spec('pkg.__init__', 'pkg.module') jako mock:
            przy util.import_state(meta_path=[mock]):
                module = self.__import__('pkg.module')
                self.assertIn('pkg', sys.modules)

    def test_bad_parent(self):
        przy util.mock_spec('pkg.module') jako mock:
            przy util.import_state(meta_path=[mock]):
                przy self.assertRaises(ImportError) jako cm:
                    self.__import__('pkg.module')
                self.assertEqual(cm.exception.name, 'pkg')

    def test_raising_parent_after_importing_child(self):
        def __init__():
            zaimportuj pkg.module
            1/0
        mock = util.mock_spec('pkg.__init__', 'pkg.module',
                                 module_code={'pkg': __init__})
        przy mock:
            przy util.import_state(meta_path=[mock]):
                przy self.assertRaises(ZeroDivisionError):
                    self.__import__('pkg')
                self.assertNotIn('pkg', sys.modules)
                self.assertIn('pkg.module', sys.modules)
                przy self.assertRaises(ZeroDivisionError):
                    self.__import__('pkg.module')
                self.assertNotIn('pkg', sys.modules)
                self.assertIn('pkg.module', sys.modules)

    def test_raising_parent_after_relative_importing_child(self):
        def __init__():
            z . zaimportuj module
            1/0
        mock = util.mock_spec('pkg.__init__', 'pkg.module',
                                 module_code={'pkg': __init__})
        przy mock:
            przy util.import_state(meta_path=[mock]):
                przy self.assertRaises((ZeroDivisionError, ImportError)):
                    # This podnieśs ImportError on the "z . zaimportuj module"
                    # line, nie sure why.
                    self.__import__('pkg')
                self.assertNotIn('pkg', sys.modules)
                przy self.assertRaises((ZeroDivisionError, ImportError)):
                    self.__import__('pkg.module')
                self.assertNotIn('pkg', sys.modules)
                # XXX Nieprawda
                #self.assertIn('pkg.module', sys.modules)

    def test_raising_parent_after_double_relative_importing_child(self):
        def __init__():
            z ..subpkg zaimportuj module
            1/0
        mock = util.mock_spec('pkg.__init__', 'pkg.subpkg.__init__',
                                 'pkg.subpkg.module',
                                 module_code={'pkg.subpkg': __init__})
        przy mock:
            przy util.import_state(meta_path=[mock]):
                przy self.assertRaises((ZeroDivisionError, ImportError)):
                    # This podnieśs ImportError on the "z ..subpkg zaimportuj module"
                    # line, nie sure why.
                    self.__import__('pkg.subpkg')
                self.assertNotIn('pkg.subpkg', sys.modules)
                przy self.assertRaises((ZeroDivisionError, ImportError)):
                    self.__import__('pkg.subpkg.module')
                self.assertNotIn('pkg.subpkg', sys.modules)
                # XXX Nieprawda
                #self.assertIn('pkg.subpkg.module', sys.modules)

    def test_module_not_package(self):
        # Try to zaimportuj a submodule z a non-package should podnieś ImportError.
        assert nie hasattr(sys, '__path__')
        przy self.assertRaises(ImportError) jako cm:
            self.__import__('sys.no_submodules_here')
        self.assertEqual(cm.exception.name, 'sys.no_submodules_here')

    def test_module_not_package_but_side_effects(self):
        # If a module injects something into sys.modules jako a side-effect, then
        # pick up on that fact.
        name = 'mod'
        subname = name + '.b'
        def module_injection():
            sys.modules[subname] = 'total bunk'
        mock_spec = util.mock_spec('mod',
                                         module_code={'mod': module_injection})
        przy mock_spec jako mock:
            przy util.import_state(meta_path=[mock]):
                spróbuj:
                    submodule = self.__import__(subname)
                w_końcu:
                    support.unload(subname)


(Frozen_ParentTests,
 Source_ParentTests
 ) = util.test_both(ParentModuleTests, __import__=util.__import__)


jeżeli __name__ == '__main__':
    unittest.main()
