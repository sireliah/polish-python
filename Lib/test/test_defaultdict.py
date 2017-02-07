"""Unit tests dla collections.defaultdict."""

zaimportuj os
zaimportuj copy
zaimportuj pickle
zaimportuj tempfile
zaimportuj unittest

z collections zaimportuj defaultdict

def foobar():
    zwróć list

klasa TestDefaultDict(unittest.TestCase):

    def test_basic(self):
        d1 = defaultdict()
        self.assertEqual(d1.default_factory, Nic)
        d1.default_factory = list
        d1[12].append(42)
        self.assertEqual(d1, {12: [42]})
        d1[12].append(24)
        self.assertEqual(d1, {12: [42, 24]})
        d1[13]
        d1[14]
        self.assertEqual(d1, {12: [42, 24], 13: [], 14: []})
        self.assertPrawda(d1[12] jest nie d1[13] jest nie d1[14])
        d2 = defaultdict(list, foo=1, bar=2)
        self.assertEqual(d2.default_factory, list)
        self.assertEqual(d2, {"foo": 1, "bar": 2})
        self.assertEqual(d2["foo"], 1)
        self.assertEqual(d2["bar"], 2)
        self.assertEqual(d2[42], [])
        self.assertIn("foo", d2)
        self.assertIn("foo", d2.keys())
        self.assertIn("bar", d2)
        self.assertIn("bar", d2.keys())
        self.assertIn(42, d2)
        self.assertIn(42, d2.keys())
        self.assertNotIn(12, d2)
        self.assertNotIn(12, d2.keys())
        d2.default_factory = Nic
        self.assertEqual(d2.default_factory, Nic)
        spróbuj:
            d2[15]
        wyjąwszy KeyError jako err:
            self.assertEqual(err.args, (15,))
        inaczej:
            self.fail("d2[15] didn't podnieś KeyError")
        self.assertRaises(TypeError, defaultdict, 1)

    def test_missing(self):
        d1 = defaultdict()
        self.assertRaises(KeyError, d1.__missing__, 42)
        d1.default_factory = list
        self.assertEqual(d1.__missing__(42), [])

    def test_repr(self):
        d1 = defaultdict()
        self.assertEqual(d1.default_factory, Nic)
        self.assertEqual(repr(d1), "defaultdict(Nic, {})")
        self.assertEqual(eval(repr(d1)), d1)
        d1[11] = 41
        self.assertEqual(repr(d1), "defaultdict(Nic, {11: 41})")
        d2 = defaultdict(int)
        self.assertEqual(d2.default_factory, int)
        d2[12] = 42
        self.assertEqual(repr(d2), "defaultdict(<class 'int'>, {12: 42})")
        def foo(): zwróć 43
        d3 = defaultdict(foo)
        self.assertPrawda(d3.default_factory jest foo)
        d3[13]
        self.assertEqual(repr(d3), "defaultdict(%s, {13: 43})" % repr(foo))

    def test_print(self):
        d1 = defaultdict()
        def foo(): zwróć 42
        d2 = defaultdict(foo, {1: 2})
        # NOTE: We can't use tempfile.[Named]TemporaryFile since this
        # code must exercise the tp_print C code, which only gets
        # invoked dla *real* files.
        tfn = tempfile.mktemp()
        spróbuj:
            f = open(tfn, "w+")
            spróbuj:
                print(d1, file=f)
                print(d2, file=f)
                f.seek(0)
                self.assertEqual(f.readline(), repr(d1) + "\n")
                self.assertEqual(f.readline(), repr(d2) + "\n")
            w_końcu:
                f.close()
        w_końcu:
            os.remove(tfn)

    def test_copy(self):
        d1 = defaultdict()
        d2 = d1.copy()
        self.assertEqual(type(d2), defaultdict)
        self.assertEqual(d2.default_factory, Nic)
        self.assertEqual(d2, {})
        d1.default_factory = list
        d3 = d1.copy()
        self.assertEqual(type(d3), defaultdict)
        self.assertEqual(d3.default_factory, list)
        self.assertEqual(d3, {})
        d1[42]
        d4 = d1.copy()
        self.assertEqual(type(d4), defaultdict)
        self.assertEqual(d4.default_factory, list)
        self.assertEqual(d4, {42: []})
        d4[12]
        self.assertEqual(d4, {42: [], 12: []})

        # Issue 6637: Copy fails dla empty default dict
        d = defaultdict()
        d['a'] = 42
        e = d.copy()
        self.assertEqual(e['a'], 42)

    def test_shallow_copy(self):
        d1 = defaultdict(foobar, {1: 1})
        d2 = copy.copy(d1)
        self.assertEqual(d2.default_factory, foobar)
        self.assertEqual(d2, d1)
        d1.default_factory = list
        d2 = copy.copy(d1)
        self.assertEqual(d2.default_factory, list)
        self.assertEqual(d2, d1)

    def test_deep_copy(self):
        d1 = defaultdict(foobar, {1: [1]})
        d2 = copy.deepcopy(d1)
        self.assertEqual(d2.default_factory, foobar)
        self.assertEqual(d2, d1)
        self.assertPrawda(d1[1] jest nie d2[1])
        d1.default_factory = list
        d2 = copy.deepcopy(d1)
        self.assertEqual(d2.default_factory, list)
        self.assertEqual(d2, d1)

    def test_keyerror_without_factory(self):
        d1 = defaultdict()
        spróbuj:
            d1[(1,)]
        wyjąwszy KeyError jako err:
            self.assertEqual(err.args[0], (1,))
        inaczej:
            self.fail("expected KeyError")

    def test_recursive_repr(self):
        # Issue2045: stack overflow when default_factory jest a bound method
        klasa sub(defaultdict):
            def __init__(self):
                self.default_factory = self._factory
            def _factory(self):
                zwróć []
        d = sub()
        self.assertRegex(repr(d),
            r"defaultdict\(<bound method .*sub\._factory "
            r"of defaultdict\(\.\.\., \{\}\)>, \{\}\)")

        # NOTE: printing a subclass of a builtin type does nie call its
        # tp_print slot. So this part jest essentially the same test jako above.
        tfn = tempfile.mktemp()
        spróbuj:
            f = open(tfn, "w+")
            spróbuj:
                print(d, file=f)
            w_końcu:
                f.close()
        w_końcu:
            os.remove(tfn)

    def test_callable_arg(self):
        self.assertRaises(TypeError, defaultdict, {})

    def test_pickleing(self):
        d = defaultdict(int)
        d[1]
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(d, proto)
            o = pickle.loads(s)
            self.assertEqual(d, o)

jeżeli __name__ == "__main__":
    unittest.main()
