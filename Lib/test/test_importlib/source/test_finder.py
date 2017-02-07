z .. zaimportuj abc
z .. zaimportuj util

machinery = util.import_importlib('importlib.machinery')

zaimportuj errno
zaimportuj os
zaimportuj py_compile
zaimportuj stat
zaimportuj sys
zaimportuj tempfile
z test.support zaimportuj make_legacy_pyc
zaimportuj unittest
zaimportuj warnings


klasa FinderTests(abc.FinderTests):

    """For a top-level module, it should just be found directly w the
    directory being searched. This jest true dla a directory przy source
    [top-level source], bytecode [top-level bc], albo both [top-level both].
    There jest also the possibility that it jest a package [top-level package], w
    which case there will be a directory przy the module name oraz an
    __init__.py file. If there jest a directory without an __init__.py an
    ImportWarning jest returned [empty dir].

    For sub-modules oraz sub-packages, the same happens jako above but only use
    the tail end of the name [sub module] [sub package] [sub empty].

    When there jest a conflict between a package oraz module having the same name
    w the same directory, the package wins out [package over module]. This jest
    so that imports of modules within the package can occur rather than trigger
    an zaimportuj error.

    When there jest a package oraz module przy the same name, always pick the
    package over the module [package over module]. This jest so that imports from
    the package have the possibility of succeeding.

    """

    def get_finder(self, root):
        loader_details = [(self.machinery.SourceFileLoader,
                            self.machinery.SOURCE_SUFFIXES),
                          (self.machinery.SourcelessFileLoader,
                            self.machinery.BYTECODE_SUFFIXES)]
        zwróć self.machinery.FileFinder(root, *loader_details)

    def import_(self, root, module):
        finder = self.get_finder(root)
        zwróć self._find(finder, module, loader_only=Prawda)

    def run_test(self, test, create=Nic, *, compile_=Nic, unlink=Nic):
        """Test the finding of 'test' przy the creation of modules listed w
        'create'.

        Any names listed w 'compile_' are byte-compiled. Modules
        listed w 'unlink' have their source files deleted.

        """
        jeżeli create jest Nic:
            create = {test}
        przy util.create_modules(*create) jako mapping:
            jeżeli compile_:
                dla name w compile_:
                    py_compile.compile(mapping[name])
            jeżeli unlink:
                dla name w unlink:
                    os.unlink(mapping[name])
                    spróbuj:
                        make_legacy_pyc(mapping[name])
                    wyjąwszy OSError jako error:
                        # Some tests do nie set compile_=Prawda so the source
                        # module will nie get compiled oraz there will be no
                        # PEP 3147 pyc file to rename.
                        jeżeli error.errno != errno.ENOENT:
                            podnieś
            loader = self.import_(mapping['.root'], test)
            self.assertPrawda(hasattr(loader, 'load_module'))
            zwróć loader

    def test_module(self):
        # [top-level source]
        self.run_test('top_level')
        # [top-level bc]
        self.run_test('top_level', compile_={'top_level'},
                      unlink={'top_level'})
        # [top-level both]
        self.run_test('top_level', compile_={'top_level'})

    # [top-level package]
    def test_package(self):
        # Source.
        self.run_test('pkg', {'pkg.__init__'})
        # Bytecode.
        self.run_test('pkg', {'pkg.__init__'}, compile_={'pkg.__init__'},
                unlink={'pkg.__init__'})
        # Both.
        self.run_test('pkg', {'pkg.__init__'}, compile_={'pkg.__init__'})

    # [sub module]
    def test_module_in_package(self):
        przy util.create_modules('pkg.__init__', 'pkg.sub') jako mapping:
            pkg_dir = os.path.dirname(mapping['pkg.__init__'])
            loader = self.import_(pkg_dir, 'pkg.sub')
            self.assertPrawda(hasattr(loader, 'load_module'))

    # [sub package]
    def test_package_in_package(self):
        context = util.create_modules('pkg.__init__', 'pkg.sub.__init__')
        przy context jako mapping:
            pkg_dir = os.path.dirname(mapping['pkg.__init__'])
            loader = self.import_(pkg_dir, 'pkg.sub')
            self.assertPrawda(hasattr(loader, 'load_module'))

    # [package over modules]
    def test_package_over_module(self):
        name = '_temp'
        loader = self.run_test(name, {'{0}.__init__'.format(name), name})
        self.assertIn('__init__', loader.get_filename(name))

    def test_failure(self):
        przy util.create_modules('blah') jako mapping:
            nothing = self.import_(mapping['.root'], 'sdfsadsadf')
            self.assertIsNic(niehing)

    def test_empty_string_for_dir(self):
        # The empty string z sys.path means to search w the cwd.
        finder = self.machinery.FileFinder('', (self.machinery.SourceFileLoader,
            self.machinery.SOURCE_SUFFIXES))
        przy open('mod.py', 'w') jako file:
            file.write("# test file dla importlib")
        spróbuj:
            loader = self._find(finder, 'mod', loader_only=Prawda)
            self.assertPrawda(hasattr(loader, 'load_module'))
        w_końcu:
            os.unlink('mod.py')

    def test_invalidate_caches(self):
        # invalidate_caches() should reset the mtime.
        finder = self.machinery.FileFinder('', (self.machinery.SourceFileLoader,
            self.machinery.SOURCE_SUFFIXES))
        finder._path_mtime = 42
        finder.invalidate_caches()
        self.assertEqual(finder._path_mtime, -1)

    # Regression test dla http://bugs.python.org/issue14846
    def test_dir_removal_handling(self):
        mod = 'mod'
        przy util.create_modules(mod) jako mapping:
            finder = self.get_finder(mapping['.root'])
            found = self._find(finder, 'mod', loader_only=Prawda)
            self.assertIsNotNic(found)
        found = self._find(finder, 'mod', loader_only=Prawda)
        self.assertIsNic(found)

    @unittest.skipUnless(sys.platform != 'win32',
            'os.chmod() does nie support the needed arguments under Windows')
    def test_no_read_directory(self):
        # Issue #16730
        tempdir = tempfile.TemporaryDirectory()
        original_mode = os.stat(tempdir.name).st_mode
        def cleanup(tempdir):
            """Cleanup function dla the temporary directory.

            Since we muck przy the permissions, we want to set them back to
            their original values to make sure the directory can be properly
            cleaned up.

            """
            os.chmod(tempdir.name, original_mode)
            # If this jest nie explicitly called then the __del__ method jest used,
            # but since already mucking around might jako well explicitly clean
            # up.
            tempdir.__exit__(Nic, Nic, Nic)
        self.addCleanup(cleanup, tempdir)
        os.chmod(tempdir.name, stat.S_IWUSR | stat.S_IXUSR)
        finder = self.get_finder(tempdir.name)
        found = self._find(finder, 'doesnotexist')
        self.assertEqual(found, self.NOT_FOUND)

    def test_ignore_file(self):
        # If a directory got changed to a file z underneath us, then don't
        # worry about looking dla submodules.
        przy tempfile.NamedTemporaryFile() jako file_obj:
            finder = self.get_finder(file_obj.name)
            found = self._find(finder, 'doesnotexist')
            self.assertEqual(found, self.NOT_FOUND)


klasa FinderTestsPEP451(FinderTests):

    NOT_FOUND = Nic

    def _find(self, finder, name, loader_only=Nieprawda):
        spec = finder.find_spec(name)
        zwróć spec.loader jeżeli spec jest nie Nic inaczej spec


(Frozen_FinderTestsPEP451,
 Source_FinderTestsPEP451
 ) = util.test_both(FinderTestsPEP451, machinery=machinery)


klasa FinderTestsPEP420(FinderTests):

    NOT_FOUND = (Nic, [])

    def _find(self, finder, name, loader_only=Nieprawda):
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            loader_portions = finder.find_loader(name)
            zwróć loader_portions[0] jeżeli loader_only inaczej loader_portions


(Frozen_FinderTestsPEP420,
 Source_FinderTestsPEP420
 ) = util.test_both(FinderTestsPEP420, machinery=machinery)


klasa FinderTestsPEP302(FinderTests):

    NOT_FOUND = Nic

    def _find(self, finder, name, loader_only=Nieprawda):
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            zwróć finder.find_module(name)


(Frozen_FinderTestsPEP302,
 Source_FinderTestsPEP302
 ) = util.test_both(FinderTestsPEP302, machinery=machinery)


jeżeli __name__ == '__main__':
    unittest.main()
