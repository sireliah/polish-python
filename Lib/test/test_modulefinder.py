zaimportuj os
zaimportuj errno
zaimportuj importlib.machinery
zaimportuj py_compile
zaimportuj shutil
zaimportuj unittest
zaimportuj tempfile

z test zaimportuj support

zaimportuj modulefinder

TEST_DIR = tempfile.mkdtemp()
TEST_PATH = [TEST_DIR, os.path.dirname(tempfile.__file__)]

# Each test description jest a list of 5 items:
#
# 1. a module name that will be imported by modulefinder
# 2. a list of module names that modulefinder jest required to find
# 3. a list of module names that modulefinder should complain
#    about because they are nie found
# 4. a list of module names that modulefinder should complain
#    about because they MAY be nie found
# 5. a string specifying packages to create; the format jest obvious imo.
#
# Each package will be created w TEST_DIR, oraz TEST_DIR will be
# removed after the tests again.
# Modulefinder searches w a path that contains TEST_DIR, plus
# the standard Lib directory.

maybe_test = [
    "a.module",
    ["a", "a.module", "sys",
     "b"],
    ["c"], ["b.something"],
    """\
a/__init__.py
a/module.py
                                z b zaimportuj something
                                z c zaimportuj something
b/__init__.py
                                z sys zaimportuj *
"""]

maybe_test_new = [
    "a.module",
    ["a", "a.module", "sys",
     "b", "__future__"],
    ["c"], ["b.something"],
    """\
a/__init__.py
a/module.py
                                z b zaimportuj something
                                z c zaimportuj something
b/__init__.py
                                z __future__ zaimportuj absolute_import
                                z sys zaimportuj *
"""]

package_test = [
    "a.module",
    ["a", "a.b", "a.c", "a.module", "mymodule", "sys"],
    ["blahblah", "c"], [],
    """\
mymodule.py
a/__init__.py
                                zaimportuj blahblah
                                z a zaimportuj b
                                zaimportuj c
a/module.py
                                zaimportuj sys
                                z a zaimportuj b jako x
                                z a.c zaimportuj sillyname
a/b.py
a/c.py
                                z a.module zaimportuj x
                                zaimportuj mymodule jako sillyname
                                z sys zaimportuj version_info
"""]

absolute_import_test = [
    "a.module",
    ["a", "a.module",
     "b", "b.x", "b.y", "b.z",
     "__future__", "sys", "gc"],
    ["blahblah", "z"], [],
    """\
mymodule.py
a/__init__.py
a/module.py
                                z __future__ zaimportuj absolute_import
                                zaimportuj sys # sys
                                zaimportuj blahblah # fails
                                zaimportuj gc # gc
                                zaimportuj b.x # b.x
                                z b zaimportuj y # b.y
                                z b.z zaimportuj * # b.z.*
a/gc.py
a/sys.py
                                zaimportuj mymodule
a/b/__init__.py
a/b/x.py
a/b/y.py
a/b/z.py
b/__init__.py
                                zaimportuj z
b/unused.py
b/x.py
b/y.py
b/z.py
"""]

relative_import_test = [
    "a.module",
    ["__future__",
     "a", "a.module",
     "a.b", "a.b.y", "a.b.z",
     "a.b.c", "a.b.c.moduleC",
     "a.b.c.d", "a.b.c.e",
     "a.b.x",
     "gc"],
    [], [],
    """\
mymodule.py
a/__init__.py
                                z .b zaimportuj y, z # a.b.y, a.b.z
a/module.py
                                z __future__ zaimportuj absolute_zaimportuj # __future__
                                zaimportuj gc # gc
a/gc.py
a/sys.py
a/b/__init__.py
                                z ..b zaimportuj x # a.b.x
                                #z a.b.c zaimportuj moduleC
                                z .c zaimportuj moduleC # a.b.moduleC
a/b/x.py
a/b/y.py
a/b/z.py
a/b/g.py
a/b/c/__init__.py
                                z ..c zaimportuj e # a.b.c.e
a/b/c/moduleC.py
                                z ..c zaimportuj d # a.b.c.d
a/b/c/d.py
a/b/c/e.py
a/b/c/x.py
"""]

relative_import_test_2 = [
    "a.module",
    ["a", "a.module",
     "a.sys",
     "a.b", "a.b.y", "a.b.z",
     "a.b.c", "a.b.c.d",
     "a.b.c.e",
     "a.b.c.moduleC",
     "a.b.c.f",
     "a.b.x",
     "a.another"],
    [], [],
    """\
mymodule.py
a/__init__.py
                                z . zaimportuj sys # a.sys
a/another.py
a/module.py
                                z .b zaimportuj y, z # a.b.y, a.b.z
a/gc.py
a/sys.py
a/b/__init__.py
                                z .c zaimportuj moduleC # a.b.c.moduleC
                                z .c zaimportuj d # a.b.c.d
a/b/x.py
a/b/y.py
a/b/z.py
a/b/c/__init__.py
                                z . zaimportuj e # a.b.c.e
a/b/c/moduleC.py
                                #
                                z . zaimportuj f   # a.b.c.f
                                z .. zaimportuj x  # a.b.x
                                z ... zaimportuj another # a.another
a/b/c/d.py
a/b/c/e.py
a/b/c/f.py
"""]

relative_import_test_3 = [
    "a.module",
    ["a", "a.module"],
    ["a.bar"],
    [],
    """\
a/__init__.py
                                def foo(): dalej
a/module.py
                                z . zaimportuj foo
                                z . zaimportuj bar
"""]

relative_import_test_4 = [
    "a.module",
    ["a", "a.module"],
    [],
    [],
    """\
a/__init__.py
                                def foo(): dalej
a/module.py
                                z . zaimportuj *
"""]

bytecode_test = [
    "a",
    ["a"],
    [],
    [],
    ""
]


def open_file(path):
    dirname = os.path.dirname(path)
    spróbuj:
        os.makedirs(dirname)
    wyjąwszy OSError jako e:
        jeżeli e.errno != errno.EEXIST:
            podnieś
    zwróć open(path, "w")


def create_package(source):
    ofi = Nic
    spróbuj:
        dla line w source.splitlines():
            jeżeli line.startswith(" ") albo line.startswith("\t"):
                ofi.write(line.strip() + "\n")
            inaczej:
                jeżeli ofi:
                    ofi.close()
                ofi = open_file(os.path.join(TEST_DIR, line.strip()))
    w_końcu:
        jeżeli ofi:
            ofi.close()


klasa ModuleFinderTest(unittest.TestCase):
    def _do_test(self, info, report=Nieprawda, debug=0, replace_paths=[]):
        import_this, modules, missing, maybe_missing, source = info
        create_package(source)
        spróbuj:
            mf = modulefinder.ModuleFinder(path=TEST_PATH, debug=debug,
                                           replace_paths=replace_paths)
            mf.import_hook(import_this)
            jeżeli report:
                mf.report()
##                # This wouldn't work w general when executed several times:
##                opath = sys.path[:]
##                sys.path = TEST_PATH
##                spróbuj:
##                    __import__(import_this)
##                wyjąwszy:
##                    zaimportuj traceback; traceback.print_exc()
##                sys.path = opath
##                zwróć
            modules = sorted(set(modules))
            found = sorted(mf.modules)
            # check jeżeli we found what we expected, nie more, nie less
            self.assertEqual(found, modules)

            # check dla missing oraz maybe missing modules
            bad, maybe = mf.any_missing_maybe()
            self.assertEqual(bad, missing)
            self.assertEqual(maybe, maybe_missing)
        w_końcu:
            shutil.rmtree(TEST_DIR)

    def test_package(self):
        self._do_test(package_test)

    def test_maybe(self):
        self._do_test(maybe_test)

    def test_maybe_new(self):
        self._do_test(maybe_test_new)

    def test_absolute_imports(self):
        self._do_test(absolute_import_test)

    def test_relative_imports(self):
        self._do_test(relative_import_test)

    def test_relative_imports_2(self):
        self._do_test(relative_import_test_2)

    def test_relative_imports_3(self):
        self._do_test(relative_import_test_3)

    def test_relative_imports_4(self):
        self._do_test(relative_import_test_4)

    def test_bytecode(self):
        base_path = os.path.join(TEST_DIR, 'a')
        source_path = base_path + importlib.machinery.SOURCE_SUFFIXES[0]
        bytecode_path = base_path + importlib.machinery.BYTECODE_SUFFIXES[0]
        przy open_file(source_path) jako file:
            file.write('testing_modulefinder = Prawda\n')
        py_compile.compile(source_path, cfile=bytecode_path)
        os.remove(source_path)
        self._do_test(bytecode_test)

    def test_replace_paths(self):
        old_path = os.path.join(TEST_DIR, 'a', 'module.py')
        new_path = os.path.join(TEST_DIR, 'a', 'spam.py')
        przy support.captured_stdout() jako output:
            self._do_test(maybe_test, debug=2,
                          replace_paths=[(old_path, new_path)])
        output = output.getvalue()
        expected = "co_filename %r changed to %r" % (old_path, new_path)
        self.assertIn(expected, output)


jeżeli __name__ == "__main__":
    unittest.main()
