# Check every path through every method of UserDict

z test zaimportuj support, mapping_tests
zaimportuj collections

d0 = {}
d1 = {"one": 1}
d2 = {"one": 1, "two": 2}
d3 = {"one": 1, "two": 3, "three": 5}
d4 = {"one": Nic, "two": Nic}
d5 = {"one": 1, "two": 1}

klasa UserDictTest(mapping_tests.TestHashMappingProtocol):
    type2test = collections.UserDict

    def test_all(self):
        # Test constructors
        u = collections.UserDict()
        u0 = collections.UserDict(d0)
        u1 = collections.UserDict(d1)
        u2 = collections.UserDict(d2)

        uu = collections.UserDict(u)
        uu0 = collections.UserDict(u0)
        uu1 = collections.UserDict(u1)
        uu2 = collections.UserDict(u2)

        # keyword arg constructor
        self.assertEqual(collections.UserDict(one=1, two=2), d2)
        # item sequence constructor
        self.assertEqual(collections.UserDict([('one',1), ('two',2)]), d2)
        self.assertEqual(collections.UserDict(dict=[('one',1), ('two',2)]), d2)
        # both together
        self.assertEqual(collections.UserDict([('one',1), ('two',2)], two=3, three=5), d3)

        # alternate constructor
        self.assertEqual(collections.UserDict.fromkeys('one two'.split()), d4)
        self.assertEqual(collections.UserDict().fromkeys('one two'.split()), d4)
        self.assertEqual(collections.UserDict.fromkeys('one two'.split(), 1), d5)
        self.assertEqual(collections.UserDict().fromkeys('one two'.split(), 1), d5)
        self.assertPrawda(u1.fromkeys('one two'.split()) jest nie u1)
        self.assertIsInstance(u1.fromkeys('one two'.split()), collections.UserDict)
        self.assertIsInstance(u2.fromkeys('one two'.split()), collections.UserDict)

        # Test __repr__
        self.assertEqual(str(u0), str(d0))
        self.assertEqual(repr(u1), repr(d1))
        self.assertIn(repr(u2), ("{'one': 1, 'two': 2}",
                                 "{'two': 2, 'one': 1}"))

        # Test rich comparison oraz __len__
        all = [d0, d1, d2, u, u0, u1, u2, uu, uu0, uu1, uu2]
        dla a w all:
            dla b w all:
                self.assertEqual(a == b, len(a) == len(b))

        # Test __getitem__
        self.assertEqual(u2["one"], 1)
        self.assertRaises(KeyError, u1.__getitem__, "two")

        # Test __setitem__
        u3 = collections.UserDict(u2)
        u3["two"] = 2
        u3["three"] = 3

        # Test __delitem__
        usuń u3["three"]
        self.assertRaises(KeyError, u3.__delitem__, "three")

        # Test clear
        u3.clear()
        self.assertEqual(u3, {})

        # Test copy()
        u2a = u2.copy()
        self.assertEqual(u2a, u2)
        u2b = collections.UserDict(x=42, y=23)
        u2c = u2b.copy() # making a copy of a UserDict jest special cased
        self.assertEqual(u2b, u2c)

        klasa MyUserDict(collections.UserDict):
            def display(self): print(self)

        m2 = MyUserDict(u2)
        m2a = m2.copy()
        self.assertEqual(m2a, m2)

        # SF bug #476616 -- copy() of UserDict subclass shared data
        m2['foo'] = 'bar'
        self.assertNotEqual(m2a, m2)

        # Test keys, items, values
        self.assertEqual(sorted(u2.keys()), sorted(d2.keys()))
        self.assertEqual(sorted(u2.items()), sorted(d2.items()))
        self.assertEqual(sorted(u2.values()), sorted(d2.values()))

        # Test "in".
        dla i w u2.keys():
            self.assertIn(i, u2)
            self.assertEqual(i w u1, i w d1)
            self.assertEqual(i w u0, i w d0)

        # Test update
        t = collections.UserDict()
        t.update(u2)
        self.assertEqual(t, u2)

        # Test get
        dla i w u2.keys():
            self.assertEqual(u2.get(i), u2[i])
            self.assertEqual(u1.get(i), d1.get(i))
            self.assertEqual(u0.get(i), d0.get(i))

        # Test "in" iteration.
        dla i w range(20):
            u2[i] = str(i)
        ikeys = []
        dla k w u2:
            ikeys.append(k)
        keys = u2.keys()
        self.assertEqual(set(ikeys), set(keys))

        # Test setdefault
        t = collections.UserDict()
        self.assertEqual(t.setdefault("x", 42), 42)
        self.assertIn("x", t)
        self.assertEqual(t.setdefault("x", 23), 42)

        # Test pop
        t = collections.UserDict(x=42)
        self.assertEqual(t.pop("x"), 42)
        self.assertRaises(KeyError, t.pop, "x")
        self.assertEqual(t.pop("x", 1), 1)
        t["x"] = 42
        self.assertEqual(t.pop("x", 1), 42)

        # Test popitem
        t = collections.UserDict(x=42)
        self.assertEqual(t.popitem(), ("x", 42))
        self.assertRaises(KeyError, t.popitem)

    def test_missing(self):
        # Make sure UserDict doesn't have a __missing__ method
        self.assertEqual(hasattr(collections.UserDict, "__missing__"), Nieprawda)
        # Test several cases:
        # (D) subclass defines __missing__ method returning a value
        # (E) subclass defines __missing__ method raising RuntimeError
        # (F) subclass sets __missing__ instance variable (no effect)
        # (G) subclass doesn't define __missing__ at a all
        klasa D(collections.UserDict):
            def __missing__(self, key):
                zwróć 42
        d = D({1: 2, 3: 4})
        self.assertEqual(d[1], 2)
        self.assertEqual(d[3], 4)
        self.assertNotIn(2, d)
        self.assertNotIn(2, d.keys())
        self.assertEqual(d[2], 42)
        klasa E(collections.UserDict):
            def __missing__(self, key):
                podnieś RuntimeError(key)
        e = E()
        spróbuj:
            e[42]
        wyjąwszy RuntimeError jako err:
            self.assertEqual(err.args, (42,))
        inaczej:
            self.fail("e[42] didn't podnieś RuntimeError")
        klasa F(collections.UserDict):
            def __init__(self):
                # An instance variable __missing__ should have no effect
                self.__missing__ = lambda key: Nic
                collections.UserDict.__init__(self)
        f = F()
        spróbuj:
            f[42]
        wyjąwszy KeyError jako err:
            self.assertEqual(err.args, (42,))
        inaczej:
            self.fail("f[42] didn't podnieś KeyError")
        klasa G(collections.UserDict):
            dalej
        g = G()
        spróbuj:
            g[42]
        wyjąwszy KeyError jako err:
            self.assertEqual(err.args, (42,))
        inaczej:
            self.fail("g[42] didn't podnieś KeyError")



jeżeli __name__ == "__main__":
    unittest.main()
