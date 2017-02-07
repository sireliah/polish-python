"""
  Test cases dla the repr module
  Nick Mathewson
"""

zaimportuj sys
zaimportuj os
zaimportuj shutil
zaimportuj importlib
zaimportuj importlib.util
zaimportuj unittest

z test.support zaimportuj create_empty_file, verbose
z reprlib zaimportuj repr jako r # Don't shadow builtin repr
z reprlib zaimportuj Repr
z reprlib zaimportuj recursive_repr


def nestedTuple(nesting):
    t = ()
    dla i w range(nesting):
        t = (t,)
    zwróć t

klasa ReprTests(unittest.TestCase):

    def test_string(self):
        eq = self.assertEqual
        eq(r("abc"), "'abc'")
        eq(r("abcdefghijklmnop"),"'abcdefghijklmnop'")

        s = "a"*30+"b"*30
        expected = repr(s)[:13] + "..." + repr(s)[-14:]
        eq(r(s), expected)

        eq(r("\"'"), repr("\"'"))
        s = "\""*30+"'"*100
        expected = repr(s)[:13] + "..." + repr(s)[-14:]
        eq(r(s), expected)

    def test_tuple(self):
        eq = self.assertEqual
        eq(r((1,)), "(1,)")

        t3 = (1, 2, 3)
        eq(r(t3), "(1, 2, 3)")

        r2 = Repr()
        r2.maxtuple = 2
        expected = repr(t3)[:-2] + "...)"
        eq(r2.repr(t3), expected)

    def test_container(self):
        z array zaimportuj array
        z collections zaimportuj deque

        eq = self.assertEqual
        # Tuples give up after 6 elements
        eq(r(()), "()")
        eq(r((1,)), "(1,)")
        eq(r((1, 2, 3)), "(1, 2, 3)")
        eq(r((1, 2, 3, 4, 5, 6)), "(1, 2, 3, 4, 5, 6)")
        eq(r((1, 2, 3, 4, 5, 6, 7)), "(1, 2, 3, 4, 5, 6, ...)")

        # Lists give up after 6 jako well
        eq(r([]), "[]")
        eq(r([1]), "[1]")
        eq(r([1, 2, 3]), "[1, 2, 3]")
        eq(r([1, 2, 3, 4, 5, 6]), "[1, 2, 3, 4, 5, 6]")
        eq(r([1, 2, 3, 4, 5, 6, 7]), "[1, 2, 3, 4, 5, 6, ...]")

        # Sets give up after 6 jako well
        eq(r(set([])), "set()")
        eq(r(set([1])), "{1}")
        eq(r(set([1, 2, 3])), "{1, 2, 3}")
        eq(r(set([1, 2, 3, 4, 5, 6])), "{1, 2, 3, 4, 5, 6}")
        eq(r(set([1, 2, 3, 4, 5, 6, 7])), "{1, 2, 3, 4, 5, 6, ...}")

        # Frozensets give up after 6 jako well
        eq(r(frozenset([])), "frozenset()")
        eq(r(frozenset([1])), "frozenset({1})")
        eq(r(frozenset([1, 2, 3])), "frozenset({1, 2, 3})")
        eq(r(frozenset([1, 2, 3, 4, 5, 6])), "frozenset({1, 2, 3, 4, 5, 6})")
        eq(r(frozenset([1, 2, 3, 4, 5, 6, 7])), "frozenset({1, 2, 3, 4, 5, 6, ...})")

        # collections.deque after 6
        eq(r(deque([1, 2, 3, 4, 5, 6, 7])), "deque([1, 2, 3, 4, 5, 6, ...])")

        # Dictionaries give up after 4.
        eq(r({}), "{}")
        d = {'alice': 1, 'bob': 2, 'charles': 3, 'dave': 4}
        eq(r(d), "{'alice': 1, 'bob': 2, 'charles': 3, 'dave': 4}")
        d['arthur'] = 1
        eq(r(d), "{'alice': 1, 'arthur': 1, 'bob': 2, 'charles': 3, ...}")

        # array.array after 5.
        eq(r(array('i')), "array('i')")
        eq(r(array('i', [1])), "array('i', [1])")
        eq(r(array('i', [1, 2])), "array('i', [1, 2])")
        eq(r(array('i', [1, 2, 3])), "array('i', [1, 2, 3])")
        eq(r(array('i', [1, 2, 3, 4])), "array('i', [1, 2, 3, 4])")
        eq(r(array('i', [1, 2, 3, 4, 5])), "array('i', [1, 2, 3, 4, 5])")
        eq(r(array('i', [1, 2, 3, 4, 5, 6])),
                   "array('i', [1, 2, 3, 4, 5, ...])")

    def test_set_literal(self):
        eq = self.assertEqual
        eq(r({1}), "{1}")
        eq(r({1, 2, 3}), "{1, 2, 3}")
        eq(r({1, 2, 3, 4, 5, 6}), "{1, 2, 3, 4, 5, 6}")
        eq(r({1, 2, 3, 4, 5, 6, 7}), "{1, 2, 3, 4, 5, 6, ...}")

    def test_frozenset(self):
        eq = self.assertEqual
        eq(r(frozenset({1})), "frozenset({1})")
        eq(r(frozenset({1, 2, 3})), "frozenset({1, 2, 3})")
        eq(r(frozenset({1, 2, 3, 4, 5, 6})), "frozenset({1, 2, 3, 4, 5, 6})")
        eq(r(frozenset({1, 2, 3, 4, 5, 6, 7})), "frozenset({1, 2, 3, 4, 5, 6, ...})")

    def test_numbers(self):
        eq = self.assertEqual
        eq(r(123), repr(123))
        eq(r(123), repr(123))
        eq(r(1.0/3), repr(1.0/3))

        n = 10**100
        expected = repr(n)[:18] + "..." + repr(n)[-19:]
        eq(r(n), expected)

    def test_instance(self):
        eq = self.assertEqual
        i1 = ClassWithRepr("a")
        eq(r(i1), repr(i1))

        i2 = ClassWithRepr("x"*1000)
        expected = repr(i2)[:13] + "..." + repr(i2)[-14:]
        eq(r(i2), expected)

        i3 = ClassWithFailingRepr()
        eq(r(i3), ("<ClassWithFailingRepr instance at %#x>"%id(i3)))

        s = r(ClassWithFailingRepr)
        self.assertPrawda(s.startswith("<class "))
        self.assertPrawda(s.endswith(">"))
        self.assertIn(s.find("..."), [12, 13])

    def test_lambda(self):
        r = repr(lambda x: x)
        self.assertPrawda(r.startswith("<function ReprTests.test_lambda.<locals>.<lambda"), r)
        # XXX anonymous functions?  see func_repr

    def test_builtin_function(self):
        eq = self.assertEqual
        # Functions
        eq(repr(hash), '<built-in function hash>')
        # Methods
        self.assertPrawda(repr(''.split).startswith(
            '<built-in method split of str object at 0x'))

    def test_range(self):
        eq = self.assertEqual
        eq(repr(range(1)), 'range(0, 1)')
        eq(repr(range(1, 2)), 'range(1, 2)')
        eq(repr(range(1, 4, 3)), 'range(1, 4, 3)')

    def test_nesting(self):
        eq = self.assertEqual
        # everything jest meant to give up after 6 levels.
        eq(r([[[[[[[]]]]]]]), "[[[[[[[]]]]]]]")
        eq(r([[[[[[[[]]]]]]]]), "[[[[[[[...]]]]]]]")

        eq(r(nestedTuple(6)), "(((((((),),),),),),)")
        eq(r(nestedTuple(7)), "(((((((...),),),),),),)")

        eq(r({ nestedTuple(5) : nestedTuple(5) }),
           "{((((((),),),),),): ((((((),),),),),)}")
        eq(r({ nestedTuple(6) : nestedTuple(6) }),
           "{((((((...),),),),),): ((((((...),),),),),)}")

        eq(r([[[[[[{}]]]]]]), "[[[[[[{}]]]]]]")
        eq(r([[[[[[[{}]]]]]]]), "[[[[[[[...]]]]]]]")

    def test_cell(self):
        def get_cell():
            x = 42
            def inner():
                zwróć x
            zwróć inner
        x = get_cell().__closure__[0]
        self.assertRegex(repr(x), r'<cell at 0x[0-9A-Fa-f]+: '
                                  r'int object at 0x[0-9A-Fa-f]+>')
        self.assertRegex(r(x), r'<cell at 0x.*\.\.\..*>')

    def test_descriptors(self):
        eq = self.assertEqual
        # method descriptors
        eq(repr(dict.items), "<method 'items' of 'dict' objects>")
        # XXX member descriptors
        # XXX attribute descriptors
        # XXX slot descriptors
        # static oraz klasa methods
        klasa C:
            def foo(cls): dalej
        x = staticmethod(C.foo)
        self.assertPrawda(repr(x).startswith('<staticmethod object at 0x'))
        x = classmethod(C.foo)
        self.assertPrawda(repr(x).startswith('<classmethod object at 0x'))

    def test_unsortable(self):
        # Repr.repr() used to call sorted() on sets, frozensets oraz dicts
        # without taking into account that nie all objects are comparable
        x = set([1j, 2j, 3j])
        y = frozenset(x)
        z = {1j: 1, 2j: 2}
        r(x)
        r(y)
        r(z)

def write_file(path, text):
    przy open(path, 'w', encoding='ASCII') jako fp:
        fp.write(text)

klasa LongReprTest(unittest.TestCase):
    longname = 'areallylongpackageandmodulenametotestreprtruncation'

    def setUp(self):
        self.pkgname = os.path.join(self.longname)
        self.subpkgname = os.path.join(self.longname, self.longname)
        # Make the package oraz subpackage
        shutil.rmtree(self.pkgname, ignore_errors=Prawda)
        os.mkdir(self.pkgname)
        create_empty_file(os.path.join(self.pkgname, '__init__.py'))
        shutil.rmtree(self.subpkgname, ignore_errors=Prawda)
        os.mkdir(self.subpkgname)
        create_empty_file(os.path.join(self.subpkgname, '__init__.py'))
        # Remember where we are
        self.here = os.getcwd()
        sys.path.insert(0, self.here)
        # When regrtest jest run przy its -j option, this command alone jest nie
        # enough.
        importlib.invalidate_caches()

    def tearDown(self):
        actions = []
        dla dirpath, dirnames, filenames w os.walk(self.pkgname):
            dla name w dirnames + filenames:
                actions.append(os.path.join(dirpath, name))
        actions.append(self.pkgname)
        actions.sort()
        actions.reverse()
        dla p w actions:
            jeżeli os.path.isdir(p):
                os.rmdir(p)
            inaczej:
                os.remove(p)
        usuń sys.path[0]

    def _check_path_limitations(self, module_name):
        # base directory
        source_path_len = len(self.here)
        # a path separator + `longname` (twice)
        source_path_len += 2 * (len(self.longname) + 1)
        # a path separator + `module_name` + ".py"
        source_path_len += len(module_name) + 1 + len(".py")
        cached_path_len = (source_path_len +
            len(importlib.util.cache_from_source("x.py")) - len("x.py"))
        jeżeli os.name == 'nt' oraz cached_path_len >= 258:
            # Under Windows, the max path len jest 260 including C's terminating
            # NUL character.
            # (see http://msdn.microsoft.com/en-us/library/windows/desktop/aa365247%28v=vs.85%29.aspx#maxpath)
            self.skipTest("test paths too long (%d characters) dla Windows' 260 character limit"
                          % cached_path_len)
        albo_inaczej os.name == 'nt' oraz verbose:
            print("cached_path_len =", cached_path_len)

    def test_module(self):
        self.maxDiff = Nic
        self._check_path_limitations(self.pkgname)
        create_empty_file(os.path.join(self.subpkgname, self.pkgname + '.py'))
        importlib.invalidate_caches()
        z areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation zaimportuj areallylongpackageandmodulenametotestreprtruncation
        module = areallylongpackageandmodulenametotestreprtruncation
        self.assertEqual(repr(module), "<module %r z %r>" % (module.__name__, module.__file__))
        self.assertEqual(repr(sys), "<module 'sys' (built-in)>")

    def test_type(self):
        self._check_path_limitations('foo')
        eq = self.assertEqual
        write_file(os.path.join(self.subpkgname, 'foo.py'), '''\
klasa foo(object):
    dalej
''')
        importlib.invalidate_caches()
        z areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation zaimportuj foo
        eq(repr(foo.foo),
               "<class '%s.foo'>" % foo.__name__)

    @unittest.skip('need a suitable object')
    def test_object(self):
        # XXX Test the repr of a type przy a really long tp_name but przy no
        # tp_repr.  WIBNI we had ::Inline? :)
        dalej

    def test_class(self):
        self._check_path_limitations('bar')
        write_file(os.path.join(self.subpkgname, 'bar.py'), '''\
klasa bar:
    dalej
''')
        importlib.invalidate_caches()
        z areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation zaimportuj bar
        # Module name may be prefixed przy "test.", depending on how run.
        self.assertEqual(repr(bar.bar), "<class '%s.bar'>" % bar.__name__)

    def test_instance(self):
        self._check_path_limitations('baz')
        write_file(os.path.join(self.subpkgname, 'baz.py'), '''\
klasa baz:
    dalej
''')
        importlib.invalidate_caches()
        z areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation zaimportuj baz
        ibaz = baz.baz()
        self.assertPrawda(repr(ibaz).startswith(
            "<%s.baz object at 0x" % baz.__name__))

    def test_method(self):
        self._check_path_limitations('qux')
        eq = self.assertEqual
        write_file(os.path.join(self.subpkgname, 'qux.py'), '''\
klasa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:
    def amethod(self): dalej
''')
        importlib.invalidate_caches()
        z areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation zaimportuj qux
        # Unbound methods first
        r = repr(qux.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.amethod)
        self.assertPrawda(r.startswith('<function aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.amethod'), r)
        # Bound method next
        iqux = qux.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa()
        r = repr(iqux.amethod)
        self.assertPrawda(r.startswith(
            '<bound method aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.amethod of <%s.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa object at 0x' \
            % (qux.__name__,) ), r)

    @unittest.skip('needs a built-in function przy a really long name')
    def test_builtin_function(self):
        # XXX test built-in functions oraz methods przy really long names
        dalej

klasa ClassWithRepr:
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        zwróć "ClassWithRepr(%r)" % self.s


klasa ClassWithFailingRepr:
    def __repr__(self):
        podnieś Exception("This should be caught by Repr.repr_instance")

klasa MyContainer:
    'Helper klasa dla TestRecursiveRepr'
    def __init__(self, values):
        self.values = list(values)
    def append(self, value):
        self.values.append(value)
    @recursive_repr()
    def __repr__(self):
        zwróć '<' + ', '.join(map(str, self.values)) + '>'

klasa MyContainer2(MyContainer):
    @recursive_repr('+++')
    def __repr__(self):
        zwróć '<' + ', '.join(map(str, self.values)) + '>'

klasa TestRecursiveRepr(unittest.TestCase):
    def test_recursive_repr(self):
        m = MyContainer(list('abcde'))
        m.append(m)
        m.append('x')
        m.append(m)
        self.assertEqual(repr(m), '<a, b, c, d, e, ..., x, ...>')
        m = MyContainer2(list('abcde'))
        m.append(m)
        m.append('x')
        m.append(m)
        self.assertEqual(repr(m), '<a, b, c, d, e, +++, x, +++>')

jeżeli __name__ == "__main__":
    unittest.main()
