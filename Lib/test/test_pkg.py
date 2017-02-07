# Test packages (dotted-name import)

zaimportuj sys
zaimportuj os
zaimportuj tempfile
zaimportuj textwrap
zaimportuj unittest
z test zaimportuj support


# Helpers to create oraz destroy hierarchies.

def cleanout(root):
    names = os.listdir(root)
    dla name w names:
        fullname = os.path.join(root, name)
        jeżeli os.path.isdir(fullname) oraz nie os.path.islink(fullname):
            cleanout(fullname)
        inaczej:
            os.remove(fullname)
    os.rmdir(root)

def fixdir(lst):
    jeżeli "__builtins__" w lst:
        lst.remove("__builtins__")
    jeżeli "__initializing__" w lst:
        lst.remove("__initializing__")
    zwróć lst


# XXX Things to test
#
# zaimportuj package without __init__
# zaimportuj package przy __init__
# __init__ importing submodule
# __init__ importing global module
# __init__ defining variables
# submodule importing other submodule
# submodule importing global module
# submodule zaimportuj submodule via global name
# z package zaimportuj submodule
# z package zaimportuj subpackage
# z package zaimportuj variable (defined w __init__)
# z package zaimportuj * (defined w __init__)


klasa TestPkg(unittest.TestCase):

    def setUp(self):
        self.root = Nic
        self.pkgname = Nic
        self.syspath = list(sys.path)
        self.modules_before = support.modules_setup()

    def tearDown(self):
        sys.path[:] = self.syspath
        support.modules_cleanup(*self.modules_before)
        jeżeli self.root: # Only clean jeżeli the test was actually run
            cleanout(self.root)

        # delete all modules concerning the tested hierarchy
        jeżeli self.pkgname:
            modules = [name dla name w sys.modules
                       jeżeli self.pkgname w name.split('.')]
            dla name w modules:
                usuń sys.modules[name]

    def run_code(self, code):
        exec(textwrap.dedent(code), globals(), {"self": self})

    def mkhier(self, descr):
        root = tempfile.mkdtemp()
        sys.path.insert(0, root)
        jeżeli nie os.path.isdir(root):
            os.mkdir(root)
        dla name, contents w descr:
            comps = name.split()
            fullname = root
            dla c w comps:
                fullname = os.path.join(fullname, c)
            jeżeli contents jest Nic:
                os.mkdir(fullname)
            inaczej:
                f = open(fullname, "w")
                f.write(contents)
                jeżeli contents oraz contents[-1] != '\n':
                    f.write('\n')
                f.close()
        self.root = root
        # package name jest the name of the first item
        self.pkgname = descr[0][0]

    def test_1(self):
        hier = [("t1", Nic), ("t1 __init__.py", "")]
        self.mkhier(hier)
        zaimportuj t1

    def test_2(self):
        hier = [
         ("t2", Nic),
         ("t2 __init__.py", "'doc dla t2'"),
         ("t2 sub", Nic),
         ("t2 sub __init__.py", ""),
         ("t2 sub subsub", Nic),
         ("t2 sub subsub __init__.py", "spam = 1"),
        ]
        self.mkhier(hier)

        zaimportuj t2.sub
        zaimportuj t2.sub.subsub
        self.assertEqual(t2.__name__, "t2")
        self.assertEqual(t2.sub.__name__, "t2.sub")
        self.assertEqual(t2.sub.subsub.__name__, "t2.sub.subsub")

        # This exec crap jest needed because Py3k forbids 'zaimportuj *' outside
        # of module-scope oraz __import__() jest insufficient dla what we need.
        s = """
            zaimportuj t2
            z t2 zaimportuj *
            self.assertEqual(dir(), ['self', 'sub', 't2'])
            """
        self.run_code(s)

        z t2 zaimportuj sub
        z t2.sub zaimportuj subsub
        z t2.sub.subsub zaimportuj spam
        self.assertEqual(sub.__name__, "t2.sub")
        self.assertEqual(subsub.__name__, "t2.sub.subsub")
        self.assertEqual(sub.subsub.__name__, "t2.sub.subsub")
        dla name w ['spam', 'sub', 'subsub', 't2']:
            self.assertPrawda(locals()["name"], "Failed to zaimportuj %s" % name)

        zaimportuj t2.sub
        zaimportuj t2.sub.subsub
        self.assertEqual(t2.__name__, "t2")
        self.assertEqual(t2.sub.__name__, "t2.sub")
        self.assertEqual(t2.sub.subsub.__name__, "t2.sub.subsub")

        s = """
            z t2 zaimportuj *
            self.assertPrawda(dir(), ['self', 'sub'])
            """
        self.run_code(s)

    def test_3(self):
        hier = [
                ("t3", Nic),
                ("t3 __init__.py", ""),
                ("t3 sub", Nic),
                ("t3 sub __init__.py", ""),
                ("t3 sub subsub", Nic),
                ("t3 sub subsub __init__.py", "spam = 1"),
               ]
        self.mkhier(hier)

        zaimportuj t3.sub.subsub
        self.assertEqual(t3.__name__, "t3")
        self.assertEqual(t3.sub.__name__, "t3.sub")
        self.assertEqual(t3.sub.subsub.__name__, "t3.sub.subsub")

    def test_4(self):
        hier = [
        ("t4.py", "raise RuntimeError('Shouldnt load t4.py')"),
        ("t4", Nic),
        ("t4 __init__.py", ""),
        ("t4 sub.py", "raise RuntimeError('Shouldnt load sub.py')"),
        ("t4 sub", Nic),
        ("t4 sub __init__.py", ""),
        ("t4 sub subsub.py",
         "raise RuntimeError('Shouldnt load subsub.py')"),
        ("t4 sub subsub", Nic),
        ("t4 sub subsub __init__.py", "spam = 1"),
               ]
        self.mkhier(hier)

        s = """
            z t4.sub.subsub zaimportuj *
            self.assertEqual(spam, 1)
            """
        self.run_code(s)

    def test_5(self):
        hier = [
        ("t5", Nic),
        ("t5 __init__.py", "zaimportuj t5.foo"),
        ("t5 string.py", "spam = 1"),
        ("t5 foo.py",
         "z . zaimportuj string; assert string.spam == 1"),
         ]
        self.mkhier(hier)

        zaimportuj t5
        s = """
            z t5 zaimportuj *
            self.assertEqual(dir(), ['foo', 'self', 'string', 't5'])
            """
        self.run_code(s)

        zaimportuj t5
        self.assertEqual(fixdir(dir(t5)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__path__', '__spec__',
                          'foo', 'string', 't5'])
        self.assertEqual(fixdir(dir(t5.foo)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__spec__', 'string'])
        self.assertEqual(fixdir(dir(t5.string)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__spec__', 'spam'])

    def test_6(self):
        hier = [
                ("t6", Nic),
                ("t6 __init__.py",
                 "__all__ = ['spam', 'ham', 'eggs']"),
                ("t6 spam.py", ""),
                ("t6 ham.py", ""),
                ("t6 eggs.py", ""),
               ]
        self.mkhier(hier)

        zaimportuj t6
        self.assertEqual(fixdir(dir(t6)),
                         ['__all__', '__cached__', '__doc__', '__file__',
                          '__loader__', '__name__', '__package__', '__path__',
                          '__spec__'])
        s = """
            zaimportuj t6
            z t6 zaimportuj *
            self.assertEqual(fixdir(dir(t6)),
                             ['__all__', '__cached__', '__doc__', '__file__',
                              '__loader__', '__name__', '__package__',
                              '__path__', '__spec__', 'eggs', 'ham', 'spam'])
            self.assertEqual(dir(), ['eggs', 'ham', 'self', 'spam', 't6'])
            """
        self.run_code(s)

    def test_7(self):
        hier = [
                ("t7.py", ""),
                ("t7", Nic),
                ("t7 __init__.py", ""),
                ("t7 sub.py",
                 "raise RuntimeError('Shouldnt load sub.py')"),
                ("t7 sub", Nic),
                ("t7 sub __init__.py", ""),
                ("t7 sub .py",
                 "raise RuntimeError('Shouldnt load subsub.py')"),
                ("t7 sub subsub", Nic),
                ("t7 sub subsub __init__.py",
                 "spam = 1"),
               ]
        self.mkhier(hier)


        t7, sub, subsub = Nic, Nic, Nic
        zaimportuj t7 jako tas
        self.assertEqual(fixdir(dir(tas)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__path__', '__spec__'])
        self.assertNieprawda(t7)
        z t7 zaimportuj sub jako subpar
        self.assertEqual(fixdir(dir(subpar)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__path__', '__spec__'])
        self.assertNieprawda(t7)
        self.assertNieprawda(sub)
        z t7.sub zaimportuj subsub jako subsubsub
        self.assertEqual(fixdir(dir(subsubsub)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__path__', '__spec__',
                          'spam'])
        self.assertNieprawda(t7)
        self.assertNieprawda(sub)
        self.assertNieprawda(subsub)
        z t7.sub.subsub zaimportuj spam jako ham
        self.assertEqual(ham, 1)
        self.assertNieprawda(t7)
        self.assertNieprawda(sub)
        self.assertNieprawda(subsub)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted przy -O2 oraz above")
    def test_8(self):
        hier = [
                ("t8", Nic),
                ("t8 __init__"+os.extsep+"py", "'doc dla t8'"),
               ]
        self.mkhier(hier)

        zaimportuj t8
        self.assertEqual(t8.__doc__, "doc dla t8")

jeżeli __name__ == "__main__":
    unittest.main()
