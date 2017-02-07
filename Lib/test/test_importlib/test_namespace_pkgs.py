zaimportuj contextlib
zaimportuj importlib.abc
zaimportuj importlib.machinery
zaimportuj os
zaimportuj sys
zaimportuj types
zaimportuj unittest

z test.test_importlib zaimportuj util
z test.support zaimportuj run_unittest

# needed tests:
#
# need to test when nested, so that the top-level path isn't sys.path
# need to test dynamic path detection, both at top-level oraz nested
# przy dynamic path, check when a loader jest returned on path reload (that is,
#  trying to switch z a namespace package to a regular package)


@contextlib.contextmanager
def sys_modules_context():
    """
    Make sure sys.modules jest the same object oraz has the same content
    when exiting the context jako when entering.

    Similar to importlib.test.util.uncache, but doesn't require explicit
    names.
    """
    sys_modules_saved = sys.modules
    sys_modules_copy = sys.modules.copy()
    spróbuj:
        uzyskaj
    w_końcu:
        sys.modules = sys_modules_saved
        sys.modules.clear()
        sys.modules.update(sys_modules_copy)


@contextlib.contextmanager
def namespace_tree_context(**kwargs):
    """
    Save zaimportuj state oraz sys.modules cache oraz restore it on exit.
    Typical usage:

    >>> przy namespace_tree_context(path=['/tmp/xxyy/portion1',
    ...         '/tmp/xxyy/portion2']):
    ...     dalej
    """
    # use default meta_path oraz path_hooks unless specified otherwise
    kwargs.setdefault('meta_path', sys.meta_path)
    kwargs.setdefault('path_hooks', sys.path_hooks)
    import_context = util.import_state(**kwargs)
    przy import_context, sys_modules_context():
        uzyskaj

klasa NamespacePackageTest(unittest.TestCase):
    """
    Subclasses should define self.root oraz self.paths (under that root)
    to be added to sys.path.
    """
    root = os.path.join(os.path.dirname(__file__), 'namespace_pkgs')

    def setUp(self):
        self.resolved_paths = [
            os.path.join(self.root, path) dla path w self.paths
        ]
        self.ctx = namespace_tree_context(path=self.resolved_paths)
        self.ctx.__enter__()

    def tearDown(self):
        # TODO: will we ever want to dalej exc_info to __exit__?
        self.ctx.__exit__(Nic, Nic, Nic)

klasa SingleNamespacePackage(NamespacePackageTest):
    paths = ['portion1']

    def test_simple_package(self):
        zaimportuj foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')

    def test_cant_import_other(self):
        przy self.assertRaises(ImportError):
            zaimportuj foo.two

    def test_module_repr(self):
        zaimportuj foo.one
        self.assertEqual(repr(foo), "<module 'foo' (namespace)>")


klasa DynamicPatheNamespacePackage(NamespacePackageTest):
    paths = ['portion1']

    def test_dynamic_path(self):
        # Make sure only 'foo.one' can be imported
        zaimportuj foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')

        przy self.assertRaises(ImportError):
            zaimportuj foo.two

        # Now modify sys.path
        sys.path.append(os.path.join(self.root, 'portion2'))

        # And make sure foo.two jest now importable
        zaimportuj foo.two
        self.assertEqual(foo.two.attr, 'portion2 foo two')


klasa CombinedNamespacePackages(NamespacePackageTest):
    paths = ['both_portions']

    def test_imports(self):
        zaimportuj foo.one
        zaimportuj foo.two
        self.assertEqual(foo.one.attr, 'both_portions foo one')
        self.assertEqual(foo.two.attr, 'both_portions foo two')


klasa SeparatedNamespacePackages(NamespacePackageTest):
    paths = ['portion1', 'portion2']

    def test_imports(self):
        zaimportuj foo.one
        zaimportuj foo.two
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'portion2 foo two')


klasa SeparatedOverlappingNamespacePackages(NamespacePackageTest):
    paths = ['portion1', 'both_portions']

    def test_first_path_wins(self):
        zaimportuj foo.one
        zaimportuj foo.two
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'both_portions foo two')

    def test_first_path_wins_again(self):
        sys.path.reverse()
        zaimportuj foo.one
        zaimportuj foo.two
        self.assertEqual(foo.one.attr, 'both_portions foo one')
        self.assertEqual(foo.two.attr, 'both_portions foo two')

    def test_first_path_wins_importing_second_first(self):
        zaimportuj foo.two
        zaimportuj foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'both_portions foo two')


klasa SingleZipNamespacePackage(NamespacePackageTest):
    paths = ['top_level_portion1.zip']

    def test_simple_package(self):
        zaimportuj foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')

    def test_cant_import_other(self):
        przy self.assertRaises(ImportError):
            zaimportuj foo.two


klasa SeparatedZipNamespacePackages(NamespacePackageTest):
    paths = ['top_level_portion1.zip', 'portion2']

    def test_imports(self):
        zaimportuj foo.one
        zaimportuj foo.two
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'portion2 foo two')
        self.assertIn('top_level_portion1.zip', foo.one.__file__)
        self.assertNotIn('.zip', foo.two.__file__)


klasa SingleNestedZipNamespacePackage(NamespacePackageTest):
    paths = ['nested_portion1.zip/nested_portion1']

    def test_simple_package(self):
        zaimportuj foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')

    def test_cant_import_other(self):
        przy self.assertRaises(ImportError):
            zaimportuj foo.two


klasa SeparatedNestedZipNamespacePackages(NamespacePackageTest):
    paths = ['nested_portion1.zip/nested_portion1', 'portion2']

    def test_imports(self):
        zaimportuj foo.one
        zaimportuj foo.two
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'portion2 foo two')
        fn = os.path.join('nested_portion1.zip', 'nested_portion1')
        self.assertIn(fn, foo.one.__file__)
        self.assertNotIn('.zip', foo.two.__file__)


klasa LegacySupport(NamespacePackageTest):
    paths = ['not_a_namespace_pkg', 'portion1', 'portion2', 'both_portions']

    def test_non_namespace_package_takes_precedence(self):
        zaimportuj foo.one
        przy self.assertRaises(ImportError):
            zaimportuj foo.two
        self.assertIn('__init__', foo.__file__)
        self.assertNotIn('namespace', str(foo.__loader__).lower())


klasa DynamicPathCalculation(NamespacePackageTest):
    paths = ['project1', 'project2']

    def test_project3_fails(self):
        zaimportuj parent.child.one
        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)
        zaimportuj parent.child.two
        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)

        self.assertEqual(parent.child.one.attr, 'parent child one')
        self.assertEqual(parent.child.two.attr, 'parent child two')

        przy self.assertRaises(ImportError):
            zaimportuj parent.child.three

        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)

    def test_project3_succeeds(self):
        zaimportuj parent.child.one
        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)
        zaimportuj parent.child.two
        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)

        self.assertEqual(parent.child.one.attr, 'parent child one')
        self.assertEqual(parent.child.two.attr, 'parent child two')

        przy self.assertRaises(ImportError):
            zaimportuj parent.child.three

        # now add project3
        sys.path.append(os.path.join(self.root, 'project3'))
        zaimportuj parent.child.three

        # the paths dynamically get longer, to include the new directories
        self.assertEqual(len(parent.__path__), 3)
        self.assertEqual(len(parent.child.__path__), 3)

        self.assertEqual(parent.child.three.attr, 'parent child three')


klasa ZipWithMissingDirectory(NamespacePackageTest):
    paths = ['missing_directory.zip']

    @unittest.expectedFailure
    def test_missing_directory(self):
        # This will fail because missing_directory.zip contains:
        #   Length      Date    Time    Name
        # ---------  ---------- -----   ----
        #        29  2012-05-03 18:13   foo/one.py
        #         0  2012-05-03 20:57   bar/
        #        38  2012-05-03 20:57   bar/two.py
        # ---------                     -------
        #        67                     3 files

        # Because there jest no 'foo/', the zipimporter currently doesn't
        #  know that foo jest a namespace package

        zaimportuj foo.one

    def test_present_directory(self):
        # This succeeds because there jest a "bar/" w the zip file
        zaimportuj bar.two
        self.assertEqual(bar.two.attr, 'missing_directory foo two')


klasa ModuleAndNamespacePackageInSameDir(NamespacePackageTest):
    paths = ['module_and_namespace_package']

    def test_module_before_namespace_package(self):
        # Make sure we find the module w preference to the
        #  namespace package.
        zaimportuj a_test
        self.assertEqual(a_test.attr, 'in module')


jeżeli __name__ == "__main__":
    unittest.main()
