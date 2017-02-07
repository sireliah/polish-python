"""Test relative imports (PEP 328)."""
z .. zaimportuj util
zaimportuj sys
zaimportuj unittest

klasa RelativeImports:

    """PEP 328 introduced relative imports. This allows dla imports to occur
    z within a package without having to specify the actual package name.

    A simple example jest to zaimportuj another module within the same package
    [module z module]::

      # From pkg.mod1 przy pkg.mod2 being a module.
      z . zaimportuj mod2

    This also works dla getting an attribute z a module that jest specified
    w a relative fashion [attr z module]::

      # From pkg.mod1.
      z .mod2 zaimportuj attr

    But this jest w no way restricted to working between modules; it works
    z [package to module],::

      # From pkg, importing pkg.module which jest a module.
      z . zaimportuj module

    [module to package],::

      # Pull attr z pkg, called z pkg.module which jest a module.
      z . zaimportuj attr

    oraz [package to package]::

      # From pkg.subpkg1 (both pkg.subpkg[1,2] are packages).
      z .. zaimportuj subpkg2

    The number of dots used jest w no way restricted [deep import]::

      # Import pkg.attr z pkg.pkg1.pkg2.pkg3.pkg4.pkg5.
      z ...... zaimportuj attr

    To prevent someone z accessing code that jest outside of a package, one
    cannot reach the location containing the root package itself::

      # From pkg.__init__ [too high z package]
      z .. zaimportuj top_level

      # From pkg.module [too high z module]
      z .. zaimportuj top_level

     Relative imports are the only type of zaimportuj that allow dla an empty
     module name dla an zaimportuj [empty name].

    """

    def relative_import_test(self, create, globals_, callback):
        """Abstract out boilerplace dla setting up dla an zaimportuj test."""
        uncache_names = []
        dla name w create:
            jeżeli nie name.endswith('.__init__'):
                uncache_names.append(name)
            inaczej:
                uncache_names.append(name[:-len('.__init__')])
        przy util.mock_spec(*create) jako importer:
            przy util.import_state(meta_path=[importer]):
                dla global_ w globals_:
                    przy util.uncache(*uncache_names):
                        callback(global_)


    def test_module_from_module(self):
        # [module z module]
        create = 'pkg.__init__', 'pkg.mod2'
        globals_ = {'__package__': 'pkg'}, {'__name__': 'pkg.mod1'}
        def callback(global_):
            self.__import__('pkg')  # For __import__().
            module = self.__import__('', global_, fromlist=['mod2'], level=1)
            self.assertEqual(module.__name__, 'pkg')
            self.assertPrawda(hasattr(module, 'mod2'))
            self.assertEqual(module.mod2.attr, 'pkg.mod2')
        self.relative_import_test(create, globals_, callback)

    def test_attr_from_module(self):
        # [attr z module]
        create = 'pkg.__init__', 'pkg.mod2'
        globals_ = {'__package__': 'pkg'}, {'__name__': 'pkg.mod1'}
        def callback(global_):
            self.__import__('pkg')  # For __import__().
            module = self.__import__('mod2', global_, fromlist=['attr'],
                                            level=1)
            self.assertEqual(module.__name__, 'pkg.mod2')
            self.assertEqual(module.attr, 'pkg.mod2')
        self.relative_import_test(create, globals_, callback)

    def test_package_to_module(self):
        # [package to module]
        create = 'pkg.__init__', 'pkg.module'
        globals_ = ({'__package__': 'pkg'},
                    {'__name__': 'pkg', '__path__': ['blah']})
        def callback(global_):
            self.__import__('pkg')  # For __import__().
            module = self.__import__('', global_, fromlist=['module'],
                             level=1)
            self.assertEqual(module.__name__, 'pkg')
            self.assertPrawda(hasattr(module, 'module'))
            self.assertEqual(module.module.attr, 'pkg.module')
        self.relative_import_test(create, globals_, callback)

    def test_module_to_package(self):
        # [module to package]
        create = 'pkg.__init__', 'pkg.module'
        globals_ = {'__package__': 'pkg'}, {'__name__': 'pkg.module'}
        def callback(global_):
            self.__import__('pkg')  # For __import__().
            module = self.__import__('', global_, fromlist=['attr'], level=1)
            self.assertEqual(module.__name__, 'pkg')
        self.relative_import_test(create, globals_, callback)

    def test_package_to_package(self):
        # [package to package]
        create = ('pkg.__init__', 'pkg.subpkg1.__init__',
                    'pkg.subpkg2.__init__')
        globals_ =  ({'__package__': 'pkg.subpkg1'},
                     {'__name__': 'pkg.subpkg1', '__path__': ['blah']})
        def callback(global_):
            module = self.__import__('', global_, fromlist=['subpkg2'],
                                            level=2)
            self.assertEqual(module.__name__, 'pkg')
            self.assertPrawda(hasattr(module, 'subpkg2'))
            self.assertEqual(module.subpkg2.attr, 'pkg.subpkg2.__init__')

    def test_deep_import(self):
        # [deep import]
        create = ['pkg.__init__']
        dla count w range(1,6):
            create.append('{0}.pkg{1}.__init__'.format(
                            create[-1][:-len('.__init__')], count))
        globals_ = ({'__package__': 'pkg.pkg1.pkg2.pkg3.pkg4.pkg5'},
                    {'__name__': 'pkg.pkg1.pkg2.pkg3.pkg4.pkg5',
                        '__path__': ['blah']})
        def callback(global_):
            self.__import__(globals_[0]['__package__'])
            module = self.__import__('', global_, fromlist=['attr'], level=6)
            self.assertEqual(module.__name__, 'pkg')
        self.relative_import_test(create, globals_, callback)

    def test_too_high_from_package(self):
        # [too high z package]
        create = ['top_level', 'pkg.__init__']
        globals_ = ({'__package__': 'pkg'},
                    {'__name__': 'pkg', '__path__': ['blah']})
        def callback(global_):
            self.__import__('pkg')
            przy self.assertRaises(ValueError):
                self.__import__('', global_, fromlist=['top_level'],
                                    level=2)
        self.relative_import_test(create, globals_, callback)

    def test_too_high_from_module(self):
        # [too high z module]
        create = ['top_level', 'pkg.__init__', 'pkg.module']
        globals_ = {'__package__': 'pkg'}, {'__name__': 'pkg.module'}
        def callback(global_):
            self.__import__('pkg')
            przy self.assertRaises(ValueError):
                self.__import__('', global_, fromlist=['top_level'],
                                    level=2)
        self.relative_import_test(create, globals_, callback)

    def test_empty_name_w_level_0(self):
        # [empty name]
        przy self.assertRaises(ValueError):
            self.__import__('')

    def test_import_from_different_package(self):
        # Test importing z a different package than the caller.
        # w pkg.subpkg1.mod
        # z ..subpkg2 zaimportuj mod
        create = ['__runpy_pkg__.__init__',
                    '__runpy_pkg__.__runpy_pkg__.__init__',
                    '__runpy_pkg__.uncle.__init__',
                    '__runpy_pkg__.uncle.cousin.__init__',
                    '__runpy_pkg__.uncle.cousin.nephew']
        globals_ = {'__package__': '__runpy_pkg__.__runpy_pkg__'}
        def callback(global_):
            self.__import__('__runpy_pkg__.__runpy_pkg__')
            module = self.__import__('uncle.cousin', globals_, {},
                                    fromlist=['nephew'],
                                level=2)
            self.assertEqual(module.__name__, '__runpy_pkg__.uncle.cousin')
        self.relative_import_test(create, globals_, callback)

    def test_import_relative_import_no_fromlist(self):
        # Import a relative module w/ no fromlist.
        create = ['crash.__init__', 'crash.mod']
        globals_ = [{'__package__': 'crash', '__name__': 'crash'}]
        def callback(global_):
            self.__import__('crash')
            mod = self.__import__('mod', global_, {}, [], 1)
            self.assertEqual(mod.__name__, 'crash.mod')
        self.relative_import_test(create, globals_, callback)

    def test_relative_import_no_globals(self):
        # No globals dla a relative zaimportuj jest an error.
        przy self.assertRaises(KeyError):
            self.__import__('sys', level=1)


(Frozen_RelativeImports,
 Source_RelativeImports
 ) = util.test_both(RelativeImports, __import__=util.__import__)


jeżeli __name__ == '__main__':
    unittest.main()
