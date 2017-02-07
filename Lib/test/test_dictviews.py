zaimportuj unittest

klasa DictSetTest(unittest.TestCase):

    def test_constructors_not_callable(self):
        kt = type({}.keys())
        self.assertRaises(TypeError, kt, {})
        self.assertRaises(TypeError, kt)
        it = type({}.items())
        self.assertRaises(TypeError, it, {})
        self.assertRaises(TypeError, it)
        vt = type({}.values())
        self.assertRaises(TypeError, vt, {})
        self.assertRaises(TypeError, vt)

    def test_dict_keys(self):
        d = {1: 10, "a": "ABC"}
        keys = d.keys()
        self.assertEqual(len(keys), 2)
        self.assertEqual(set(keys), {1, "a"})
        self.assertEqual(keys, {1, "a"})
        self.assertNotEqual(keys, {1, "a", "b"})
        self.assertNotEqual(keys, {1, "b"})
        self.assertNotEqual(keys, {1})
        self.assertNotEqual(keys, 42)
        self.assertIn(1, keys)
        self.assertIn("a", keys)
        self.assertNotIn(10, keys)
        self.assertNotIn("Z", keys)
        self.assertEqual(d.keys(), d.keys())
        e = {1: 11, "a": "def"}
        self.assertEqual(d.keys(), e.keys())
        usuń e["a"]
        self.assertNotEqual(d.keys(), e.keys())

    def test_dict_items(self):
        d = {1: 10, "a": "ABC"}
        items = d.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(set(items), {(1, 10), ("a", "ABC")})
        self.assertEqual(items, {(1, 10), ("a", "ABC")})
        self.assertNotEqual(items, {(1, 10), ("a", "ABC"), "junk"})
        self.assertNotEqual(items, {(1, 10), ("a", "def")})
        self.assertNotEqual(items, {(1, 10)})
        self.assertNotEqual(items, 42)
        self.assertIn((1, 10), items)
        self.assertIn(("a", "ABC"), items)
        self.assertNotIn((1, 11), items)
        self.assertNotIn(1, items)
        self.assertNotIn((), items)
        self.assertNotIn((1,), items)
        self.assertNotIn((1, 2, 3), items)
        self.assertEqual(d.items(), d.items())
        e = d.copy()
        self.assertEqual(d.items(), e.items())
        e["a"] = "def"
        self.assertNotEqual(d.items(), e.items())

    def test_dict_mixed_keys_items(self):
        d = {(1, 1): 11, (2, 2): 22}
        e = {1: 1, 2: 2}
        self.assertEqual(d.keys(), e.items())
        self.assertNotEqual(d.items(), e.keys())

    def test_dict_values(self):
        d = {1: 10, "a": "ABC"}
        values = d.values()
        self.assertEqual(set(values), {10, "ABC"})
        self.assertEqual(len(values), 2)

    def test_dict_repr(self):
        d = {1: 10, "a": "ABC"}
        self.assertIsInstance(repr(d), str)
        r = repr(d.items())
        self.assertIsInstance(r, str)
        self.assertPrawda(r == "dict_items([('a', 'ABC'), (1, 10)])" albo
                        r == "dict_items([(1, 10), ('a', 'ABC')])")
        r = repr(d.keys())
        self.assertIsInstance(r, str)
        self.assertPrawda(r == "dict_keys(['a', 1])" albo
                        r == "dict_keys([1, 'a'])")
        r = repr(d.values())
        self.assertIsInstance(r, str)
        self.assertPrawda(r == "dict_values(['ABC', 10])" albo
                        r == "dict_values([10, 'ABC'])")

    def test_keys_set_operations(self):
        d1 = {'a': 1, 'b': 2}
        d2 = {'b': 3, 'c': 2}
        d3 = {'d': 4, 'e': 5}
        self.assertEqual(d1.keys() & d1.keys(), {'a', 'b'})
        self.assertEqual(d1.keys() & d2.keys(), {'b'})
        self.assertEqual(d1.keys() & d3.keys(), set())
        self.assertEqual(d1.keys() & set(d1.keys()), {'a', 'b'})
        self.assertEqual(d1.keys() & set(d2.keys()), {'b'})
        self.assertEqual(d1.keys() & set(d3.keys()), set())

        self.assertEqual(d1.keys() | d1.keys(), {'a', 'b'})
        self.assertEqual(d1.keys() | d2.keys(), {'a', 'b', 'c'})
        self.assertEqual(d1.keys() | d3.keys(), {'a', 'b', 'd', 'e'})
        self.assertEqual(d1.keys() | set(d1.keys()), {'a', 'b'})
        self.assertEqual(d1.keys() | set(d2.keys()), {'a', 'b', 'c'})
        self.assertEqual(d1.keys() | set(d3.keys()),
                         {'a', 'b', 'd', 'e'})

        self.assertEqual(d1.keys() ^ d1.keys(), set())
        self.assertEqual(d1.keys() ^ d2.keys(), {'a', 'c'})
        self.assertEqual(d1.keys() ^ d3.keys(), {'a', 'b', 'd', 'e'})
        self.assertEqual(d1.keys() ^ set(d1.keys()), set())
        self.assertEqual(d1.keys() ^ set(d2.keys()), {'a', 'c'})
        self.assertEqual(d1.keys() ^ set(d3.keys()),
                         {'a', 'b', 'd', 'e'})

        self.assertEqual(d1.keys() - d1.keys(), set())
        self.assertEqual(d1.keys() - d2.keys(), {'a'})
        self.assertEqual(d1.keys() - d3.keys(), {'a', 'b'})
        self.assertEqual(d1.keys() - set(d1.keys()), set())
        self.assertEqual(d1.keys() - set(d2.keys()), {'a'})
        self.assertEqual(d1.keys() - set(d3.keys()), {'a', 'b'})

        self.assertNieprawda(d1.keys().isdisjoint(d1.keys()))
        self.assertNieprawda(d1.keys().isdisjoint(d2.keys()))
        self.assertNieprawda(d1.keys().isdisjoint(list(d2.keys())))
        self.assertNieprawda(d1.keys().isdisjoint(set(d2.keys())))
        self.assertPrawda(d1.keys().isdisjoint({'x', 'y', 'z'}))
        self.assertPrawda(d1.keys().isdisjoint(['x', 'y', 'z']))
        self.assertPrawda(d1.keys().isdisjoint(set(['x', 'y', 'z'])))
        self.assertPrawda(d1.keys().isdisjoint(set(['x', 'y'])))
        self.assertPrawda(d1.keys().isdisjoint(['x', 'y']))
        self.assertPrawda(d1.keys().isdisjoint({}))
        self.assertPrawda(d1.keys().isdisjoint(d3.keys()))

        de = {}
        self.assertPrawda(de.keys().isdisjoint(set()))
        self.assertPrawda(de.keys().isdisjoint([]))
        self.assertPrawda(de.keys().isdisjoint(de.keys()))
        self.assertPrawda(de.keys().isdisjoint([1]))

    def test_items_set_operations(self):
        d1 = {'a': 1, 'b': 2}
        d2 = {'a': 2, 'b': 2}
        d3 = {'d': 4, 'e': 5}
        self.assertEqual(
            d1.items() & d1.items(), {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() & d2.items(), {('b', 2)})
        self.assertEqual(d1.items() & d3.items(), set())
        self.assertEqual(d1.items() & set(d1.items()),
                         {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() & set(d2.items()), {('b', 2)})
        self.assertEqual(d1.items() & set(d3.items()), set())

        self.assertEqual(d1.items() | d1.items(),
                         {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() | d2.items(),
                         {('a', 1), ('a', 2), ('b', 2)})
        self.assertEqual(d1.items() | d3.items(),
                         {('a', 1), ('b', 2), ('d', 4), ('e', 5)})
        self.assertEqual(d1.items() | set(d1.items()),
                         {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() | set(d2.items()),
                         {('a', 1), ('a', 2), ('b', 2)})
        self.assertEqual(d1.items() | set(d3.items()),
                         {('a', 1), ('b', 2), ('d', 4), ('e', 5)})

        self.assertEqual(d1.items() ^ d1.items(), set())
        self.assertEqual(d1.items() ^ d2.items(),
                         {('a', 1), ('a', 2)})
        self.assertEqual(d1.items() ^ d3.items(),
                         {('a', 1), ('b', 2), ('d', 4), ('e', 5)})

        self.assertEqual(d1.items() - d1.items(), set())
        self.assertEqual(d1.items() - d2.items(), {('a', 1)})
        self.assertEqual(d1.items() - d3.items(), {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() - set(d1.items()), set())
        self.assertEqual(d1.items() - set(d2.items()), {('a', 1)})
        self.assertEqual(d1.items() - set(d3.items()), {('a', 1), ('b', 2)})

        self.assertNieprawda(d1.items().isdisjoint(d1.items()))
        self.assertNieprawda(d1.items().isdisjoint(d2.items()))
        self.assertNieprawda(d1.items().isdisjoint(list(d2.items())))
        self.assertNieprawda(d1.items().isdisjoint(set(d2.items())))
        self.assertPrawda(d1.items().isdisjoint({'x', 'y', 'z'}))
        self.assertPrawda(d1.items().isdisjoint(['x', 'y', 'z']))
        self.assertPrawda(d1.items().isdisjoint(set(['x', 'y', 'z'])))
        self.assertPrawda(d1.items().isdisjoint(set(['x', 'y'])))
        self.assertPrawda(d1.items().isdisjoint({}))
        self.assertPrawda(d1.items().isdisjoint(d3.items()))

        de = {}
        self.assertPrawda(de.items().isdisjoint(set()))
        self.assertPrawda(de.items().isdisjoint([]))
        self.assertPrawda(de.items().isdisjoint(de.items()))
        self.assertPrawda(de.items().isdisjoint([1]))

    def test_recursive_repr(self):
        d = {}
        d[42] = d.values()
        self.assertRaises(RecursionError, repr, d)


jeżeli __name__ == "__main__":
    unittest.main()
