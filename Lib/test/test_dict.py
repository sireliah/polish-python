zaimportuj unittest
z test zaimportuj support

zaimportuj collections, random, string
zaimportuj collections.abc
zaimportuj gc, weakref
zaimportuj pickle


klasa DictTest(unittest.TestCase):

    def test_invalid_keyword_arguments(self):
        klasa Custom(dict):
            dalej
        dla invalid w {1 : 2}, Custom({1 : 2}):
            przy self.assertRaises(TypeError):
                dict(**invalid)
            przy self.assertRaises(TypeError):
                {}.update(**invalid)

    def test_constructor(self):
        # calling built-in types without argument must zwróć empty
        self.assertEqual(dict(), {})
        self.assertIsNot(dict(), {})

    def test_literal_constructor(self):
        # check literal constructor dla different sized dicts
        # (to exercise the BUILD_MAP oparg).
        dla n w (0, 1, 6, 256, 400):
            items = [(''.join(random.sample(string.ascii_letters, 8)), i)
                     dla i w range(n)]
            random.shuffle(items)
            formatted_items = ('{!r}: {:d}'.format(k, v) dla k, v w items)
            dictliteral = '{' + ', '.join(formatted_items) + '}'
            self.assertEqual(eval(dictliteral), dict(items))

    def test_bool(self):
        self.assertIs(nie {}, Prawda)
        self.assertPrawda({1: 2})
        self.assertIs(bool({}), Nieprawda)
        self.assertIs(bool({1: 2}), Prawda)

    def test_keys(self):
        d = {}
        self.assertEqual(set(d.keys()), set())
        d = {'a': 1, 'b': 2}
        k = d.keys()
        self.assertEqual(set(k), {'a', 'b'})
        self.assertIn('a', k)
        self.assertIn('b', k)
        self.assertIn('a', d)
        self.assertIn('b', d)
        self.assertRaises(TypeError, d.keys, Nic)
        self.assertEqual(repr(dict(a=1).keys()), "dict_keys(['a'])")

    def test_values(self):
        d = {}
        self.assertEqual(set(d.values()), set())
        d = {1:2}
        self.assertEqual(set(d.values()), {2})
        self.assertRaises(TypeError, d.values, Nic)
        self.assertEqual(repr(dict(a=1).values()), "dict_values([1])")

    def test_items(self):
        d = {}
        self.assertEqual(set(d.items()), set())

        d = {1:2}
        self.assertEqual(set(d.items()), {(1, 2)})
        self.assertRaises(TypeError, d.items, Nic)
        self.assertEqual(repr(dict(a=1).items()), "dict_items([('a', 1)])")

    def test_contains(self):
        d = {}
        self.assertNotIn('a', d)
        self.assertNieprawda('a' w d)
        self.assertPrawda('a' nie w d)
        d = {'a': 1, 'b': 2}
        self.assertIn('a', d)
        self.assertIn('b', d)
        self.assertNotIn('c', d)

        self.assertRaises(TypeError, d.__contains__)

    def test_len(self):
        d = {}
        self.assertEqual(len(d), 0)
        d = {'a': 1, 'b': 2}
        self.assertEqual(len(d), 2)

    def test_getitem(self):
        d = {'a': 1, 'b': 2}
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        d['c'] = 3
        d['a'] = 4
        self.assertEqual(d['c'], 3)
        self.assertEqual(d['a'], 4)
        usuń d['b']
        self.assertEqual(d, {'a': 4, 'c': 3})

        self.assertRaises(TypeError, d.__getitem__)

        klasa BadEq(object):
            def __eq__(self, other):
                podnieś Exc()
            def __hash__(self):
                zwróć 24

        d = {}
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        klasa Exc(Exception): dalej

        klasa BadHash(object):
            fail = Nieprawda
            def __hash__(self):
                jeżeli self.fail:
                    podnieś Exc()
                inaczej:
                    zwróć 42

        x = BadHash()
        d[x] = 42
        x.fail = Prawda
        self.assertRaises(Exc, d.__getitem__, x)

    def test_clear(self):
        d = {1:1, 2:2, 3:3}
        d.clear()
        self.assertEqual(d, {})

        self.assertRaises(TypeError, d.clear, Nic)

    def test_update(self):
        d = {}
        d.update({1:100})
        d.update({2:20})
        d.update({1:1, 2:2, 3:3})
        self.assertEqual(d, {1:1, 2:2, 3:3})

        d.update()
        self.assertEqual(d, {1:1, 2:2, 3:3})

        self.assertRaises((TypeError, AttributeError), d.update, Nic)

        klasa SimpleUserDict:
            def __init__(self):
                self.d = {1:1, 2:2, 3:3}
            def keys(self):
                zwróć self.d.keys()
            def __getitem__(self, i):
                zwróć self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        self.assertEqual(d, {1:1, 2:2, 3:3})

        klasa Exc(Exception): dalej

        d.clear()
        klasa FailingUserDict:
            def keys(self):
                podnieś Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        klasa FailingUserDict:
            def keys(self):
                klasa BogonIter:
                    def __init__(self):
                        self.i = 1
                    def __iter__(self):
                        zwróć self
                    def __next__(self):
                        jeżeli self.i:
                            self.i = 0
                            zwróć 'a'
                        podnieś Exc
                zwróć BogonIter()
            def __getitem__(self, key):
                zwróć key
        self.assertRaises(Exc, d.update, FailingUserDict())

        klasa FailingUserDict:
            def keys(self):
                klasa BogonIter:
                    def __init__(self):
                        self.i = ord('a')
                    def __iter__(self):
                        zwróć self
                    def __next__(self):
                        jeżeli self.i <= ord('z'):
                            rtn = chr(self.i)
                            self.i += 1
                            zwróć rtn
                        podnieś StopIteration
                zwróć BogonIter()
            def __getitem__(self, key):
                podnieś Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        klasa badseq(object):
            def __iter__(self):
                zwróć self
            def __next__(self):
                podnieś Exc()

        self.assertRaises(Exc, {}.update, badseq())

        self.assertRaises(ValueError, {}.update, [(1, 2, 3)])

    def test_fromkeys(self):
        self.assertEqual(dict.fromkeys('abc'), {'a':Nic, 'b':Nic, 'c':Nic})
        d = {}
        self.assertIsNot(d.fromkeys('abc'), d)
        self.assertEqual(d.fromkeys('abc'), {'a':Nic, 'b':Nic, 'c':Nic})
        self.assertEqual(d.fromkeys((4,5),0), {4:0, 5:0})
        self.assertEqual(d.fromkeys([]), {})
        def g():
            uzyskaj 1
        self.assertEqual(d.fromkeys(g()), {1:Nic})
        self.assertRaises(TypeError, {}.fromkeys, 3)
        klasa dictlike(dict): dalej
        self.assertEqual(dictlike.fromkeys('a'), {'a':Nic})
        self.assertEqual(dictlike().fromkeys('a'), {'a':Nic})
        self.assertIsInstance(dictlike.fromkeys('a'), dictlike)
        self.assertIsInstance(dictlike().fromkeys('a'), dictlike)
        klasa mydict(dict):
            def __new__(cls):
                zwróć collections.UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':Nic, 'b':Nic})
        self.assertIsInstance(ud, collections.UserDict)
        self.assertRaises(TypeError, dict.fromkeys)

        klasa Exc(Exception): dalej

        klasa baddict1(dict):
            def __init__(self):
                podnieś Exc()

        self.assertRaises(Exc, baddict1.fromkeys, [1])

        klasa BadSeq(object):
            def __iter__(self):
                zwróć self
            def __next__(self):
                podnieś Exc()

        self.assertRaises(Exc, dict.fromkeys, BadSeq())

        klasa baddict2(dict):
            def __setitem__(self, key, value):
                podnieś Exc()

        self.assertRaises(Exc, baddict2.fromkeys, [1])

        # test fast path dla dictionary inputs
        d = dict(zip(range(6), range(6)))
        self.assertEqual(dict.fromkeys(d, 0), dict(zip(range(6), [0]*6)))

        klasa baddict3(dict):
            def __new__(cls):
                zwróć d
        d = {i : i dla i w range(10)}
        res = d.copy()
        res.update(a=Nic, b=Nic, c=Nic)
        self.assertEqual(baddict3.fromkeys({"a", "b", "c"}), res)

    def test_copy(self):
        d = {1:1, 2:2, 3:3}
        self.assertEqual(d.copy(), {1:1, 2:2, 3:3})
        self.assertEqual({}.copy(), {})
        self.assertRaises(TypeError, d.copy, Nic)

    def test_get(self):
        d = {}
        self.assertIs(d.get('c'), Nic)
        self.assertEqual(d.get('c', 3), 3)
        d = {'a': 1, 'b': 2}
        self.assertIs(d.get('c'), Nic)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, Nic, Nic, Nic)

    def test_setdefault(self):
        # dict.setdefault()
        d = {}
        self.assertIs(d.setdefault('key0'), Nic)
        d.setdefault('key0', [])
        self.assertIs(d.setdefault('key0'), Nic)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)
        self.assertRaises(TypeError, d.setdefault)

        klasa Exc(Exception): dalej

        klasa BadHash(object):
            fail = Nieprawda
            def __hash__(self):
                jeżeli self.fail:
                    podnieś Exc()
                inaczej:
                    zwróć 42

        x = BadHash()
        d[x] = 42
        x.fail = Prawda
        self.assertRaises(Exc, d.setdefault, x, [])

    def test_setdefault_atomic(self):
        # Issue #13521: setdefault() calls __hash__ oraz __eq__ only once.
        klasa Hashed(object):
            def __init__(self):
                self.hash_count = 0
                self.eq_count = 0
            def __hash__(self):
                self.hash_count += 1
                zwróć 42
            def __eq__(self, other):
                self.eq_count += 1
                zwróć id(self) == id(other)
        hashed1 = Hashed()
        y = {hashed1: 5}
        hashed2 = Hashed()
        y.setdefault(hashed2, [])
        self.assertEqual(hashed1.hash_count, 1)
        self.assertEqual(hashed2.hash_count, 1)
        self.assertEqual(hashed1.eq_count + hashed2.eq_count, 1)

    def test_setitem_atomic_at_resize(self):
        klasa Hashed(object):
            def __init__(self):
                self.hash_count = 0
                self.eq_count = 0
            def __hash__(self):
                self.hash_count += 1
                zwróć 42
            def __eq__(self, other):
                self.eq_count += 1
                zwróć id(self) == id(other)
        hashed1 = Hashed()
        # 5 items
        y = {hashed1: 5, 0: 0, 1: 1, 2: 2, 3: 3}
        hashed2 = Hashed()
        # 6th item forces a resize
        y[hashed2] = []
        self.assertEqual(hashed1.hash_count, 1)
        self.assertEqual(hashed2.hash_count, 1)
        self.assertEqual(hashed1.eq_count + hashed2.eq_count, 1)

    def test_popitem(self):
        # dict.popitem()
        dla copymode w -1, +1:
            # -1: b has same structure jako a
            # +1: b jest a.copy()
            dla log2size w range(12):
                size = 2**log2size
                a = {}
                b = {}
                dla i w range(size):
                    a[repr(i)] = i
                    jeżeli copymode < 0:
                        b[repr(i)] = i
                jeżeli copymode > 0:
                    b = a.copy()
                dla i w range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assertNieprawda(copymode < 0 oraz ta != tb)
                self.assertNieprawda(a)
                self.assertNieprawda(b)

        d = {}
        self.assertRaises(KeyError, d.popitem)

    def test_pop(self):
        # Tests dla pop przy specified key
        d = {}
        k, v = 'abc', 'def'
        d[k] = v
        self.assertRaises(KeyError, d.pop, 'ghi')

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)

        self.assertRaises(TypeError, d.pop)

        klasa Exc(Exception): dalej

        klasa BadHash(object):
            fail = Nieprawda
            def __hash__(self):
                jeżeli self.fail:
                    podnieś Exc()
                inaczej:
                    zwróć 42

        x = BadHash()
        d[x] = 42
        x.fail = Prawda
        self.assertRaises(Exc, d.pop, x)

    def test_mutating_iteration(self):
        # changing dict size during iteration
        d = {}
        d[1] = 1
        przy self.assertRaises(RuntimeError):
            dla i w d:
                d[i+1] = 1

    def test_mutating_lookup(self):
        # changing dict during a lookup (issue #14417)
        klasa NastyKey:
            mutate_dict = Nic

            def __init__(self, value):
                self.value = value

            def __hash__(self):
                # hash collision!
                zwróć 1

            def __eq__(self, other):
                jeżeli NastyKey.mutate_dict:
                    mydict, key = NastyKey.mutate_dict
                    NastyKey.mutate_dict = Nic
                    usuń mydict[key]
                zwróć self.value == other.value

        key1 = NastyKey(1)
        key2 = NastyKey(2)
        d = {key1: 1}
        NastyKey.mutate_dict = (d, key1)
        d[key2] = 2
        self.assertEqual(d, {key2: 2})

    def test_repr(self):
        d = {}
        self.assertEqual(repr(d), '{}')
        d[1] = 2
        self.assertEqual(repr(d), '{1: 2}')
        d = {}
        d[1] = d
        self.assertEqual(repr(d), '{1: {...}}')

        klasa Exc(Exception): dalej

        klasa BadRepr(object):
            def __repr__(self):
                podnieś Exc()

        d = {1: BadRepr()}
        self.assertRaises(Exc, repr, d)

    def test_eq(self):
        self.assertEqual({}, {})
        self.assertEqual({1: 2}, {1: 2})

        klasa Exc(Exception): dalej

        klasa BadCmp(object):
            def __eq__(self, other):
                podnieś Exc()
            def __hash__(self):
                zwróć 1

        d1 = {BadCmp(): 1}
        d2 = {1: 1}

        przy self.assertRaises(Exc):
            d1 == d2

    def test_keys_contained(self):
        self.helper_keys_contained(lambda x: x.keys())
        self.helper_keys_contained(lambda x: x.items())

    def helper_keys_contained(self, fn):
        # Test rich comparisons against dict key views, which should behave the
        # same jako sets.
        empty = fn(dict())
        empty2 = fn(dict())
        smaller = fn({1:1, 2:2})
        larger = fn({1:1, 2:2, 3:3})
        larger2 = fn({1:1, 2:2, 3:3})
        larger3 = fn({4:1, 2:2, 3:3})

        self.assertPrawda(smaller <  larger)
        self.assertPrawda(smaller <= larger)
        self.assertPrawda(larger >  smaller)
        self.assertPrawda(larger >= smaller)

        self.assertNieprawda(smaller >= larger)
        self.assertNieprawda(smaller >  larger)
        self.assertNieprawda(larger  <= smaller)
        self.assertNieprawda(larger  <  smaller)

        self.assertNieprawda(smaller <  larger3)
        self.assertNieprawda(smaller <= larger3)
        self.assertNieprawda(larger3 >  smaller)
        self.assertNieprawda(larger3 >= smaller)

        # Inequality strictness
        self.assertPrawda(larger2 >= larger)
        self.assertPrawda(larger2 <= larger)
        self.assertNieprawda(larger2 > larger)
        self.assertNieprawda(larger2 < larger)

        self.assertPrawda(larger == larger2)
        self.assertPrawda(smaller != larger)

        # There jest an optimization on the zero-element case.
        self.assertPrawda(empty == empty2)
        self.assertNieprawda(empty != empty2)
        self.assertNieprawda(empty == smaller)
        self.assertPrawda(empty != smaller)

        # With the same size, an elementwise compare happens
        self.assertPrawda(larger != larger3)
        self.assertNieprawda(larger == larger3)

    def test_errors_in_view_containment_check(self):
        klasa C:
            def __eq__(self, other):
                podnieś RuntimeError

        d1 = {1: C()}
        d2 = {1: C()}
        przy self.assertRaises(RuntimeError):
            d1.items() == d2.items()
        przy self.assertRaises(RuntimeError):
            d1.items() != d2.items()
        przy self.assertRaises(RuntimeError):
            d1.items() <= d2.items()
        przy self.assertRaises(RuntimeError):
            d1.items() >= d2.items()

        d3 = {1: C(), 2: C()}
        przy self.assertRaises(RuntimeError):
            d2.items() < d3.items()
        przy self.assertRaises(RuntimeError):
            d3.items() > d2.items()

    def test_dictview_set_operations_on_keys(self):
        k1 = {1:1, 2:2}.keys()
        k2 = {1:1, 2:2, 3:3}.keys()
        k3 = {4:4}.keys()

        self.assertEqual(k1 - k2, set())
        self.assertEqual(k1 - k3, {1,2})
        self.assertEqual(k2 - k1, {3})
        self.assertEqual(k3 - k1, {4})
        self.assertEqual(k1 & k2, {1,2})
        self.assertEqual(k1 & k3, set())
        self.assertEqual(k1 | k2, {1,2,3})
        self.assertEqual(k1 ^ k2, {3})
        self.assertEqual(k1 ^ k3, {1,2,4})

    def test_dictview_set_operations_on_items(self):
        k1 = {1:1, 2:2}.items()
        k2 = {1:1, 2:2, 3:3}.items()
        k3 = {4:4}.items()

        self.assertEqual(k1 - k2, set())
        self.assertEqual(k1 - k3, {(1,1), (2,2)})
        self.assertEqual(k2 - k1, {(3,3)})
        self.assertEqual(k3 - k1, {(4,4)})
        self.assertEqual(k1 & k2, {(1,1), (2,2)})
        self.assertEqual(k1 & k3, set())
        self.assertEqual(k1 | k2, {(1,1), (2,2), (3,3)})
        self.assertEqual(k1 ^ k2, {(3,3)})
        self.assertEqual(k1 ^ k3, {(1,1), (2,2), (4,4)})

    def test_dictview_mixed_set_operations(self):
        # Just a few dla .keys()
        self.assertPrawda({1:1}.keys() == {1})
        self.assertPrawda({1} == {1:1}.keys())
        self.assertEqual({1:1}.keys() | {2}, {1, 2})
        self.assertEqual({2} | {1:1}.keys(), {1, 2})
        # And a few dla .items()
        self.assertPrawda({1:1}.items() == {(1,1)})
        self.assertPrawda({(1,1)} == {1:1}.items())
        self.assertEqual({1:1}.items() | {2}, {(1,1), 2})
        self.assertEqual({2} | {1:1}.items(), {(1,1), 2})

    def test_missing(self):
        # Make sure dict doesn't have a __missing__ method
        self.assertNieprawda(hasattr(dict, "__missing__"))
        self.assertNieprawda(hasattr({}, "__missing__"))
        # Test several cases:
        # (D) subclass defines __missing__ method returning a value
        # (E) subclass defines __missing__ method raising RuntimeError
        # (F) subclass sets __missing__ instance variable (no effect)
        # (G) subclass doesn't define __missing__ at a all
        klasa D(dict):
            def __missing__(self, key):
                zwróć 42
        d = D({1: 2, 3: 4})
        self.assertEqual(d[1], 2)
        self.assertEqual(d[3], 4)
        self.assertNotIn(2, d)
        self.assertNotIn(2, d.keys())
        self.assertEqual(d[2], 42)

        klasa E(dict):
            def __missing__(self, key):
                podnieś RuntimeError(key)
        e = E()
        przy self.assertRaises(RuntimeError) jako c:
            e[42]
        self.assertEqual(c.exception.args, (42,))

        klasa F(dict):
            def __init__(self):
                # An instance variable __missing__ should have no effect
                self.__missing__ = lambda key: Nic
        f = F()
        przy self.assertRaises(KeyError) jako c:
            f[42]
        self.assertEqual(c.exception.args, (42,))

        klasa G(dict):
            dalej
        g = G()
        przy self.assertRaises(KeyError) jako c:
            g[42]
        self.assertEqual(c.exception.args, (42,))

    def test_tuple_keyerror(self):
        # SF #1576657
        d = {}
        przy self.assertRaises(KeyError) jako c:
            d[(1,)]
        self.assertEqual(c.exception.args, ((1,),))

    def test_bad_key(self):
        # Dictionary lookups should fail jeżeli __eq__() podnieśs an exception.
        klasa CustomException(Exception):
            dalej

        klasa BadDictKey:
            def __hash__(self):
                zwróć hash(self.__class__)

            def __eq__(self, other):
                jeżeli isinstance(other, self.__class__):
                    podnieś CustomException
                zwróć other

        d = {}
        x1 = BadDictKey()
        x2 = BadDictKey()
        d[x1] = 1
        dla stmt w ['d[x2] = 2',
                     'z = d[x2]',
                     'x2 w d',
                     'd.get(x2)',
                     'd.setdefault(x2, 42)',
                     'd.pop(x2)',
                     'd.update({x2: 2})']:
            przy self.assertRaises(CustomException):
                exec(stmt, locals())

    def test_resize1(self):
        # Dict resizing bug, found by Jack Jansen w 2.2 CVS development.
        # This version got an assert failure w debug build, infinite loop w
        # release build.  Unfortunately, provoking this kind of stuff requires
        # a mix of inserts oraz deletes hitting exactly the right hash codes w
        # exactly the right order, oraz I can't think of a randomized approach
        # that would be *likely* to hit a failing case w reasonable time.

        d = {}
        dla i w range(5):
            d[i] = i
        dla i w range(5):
            usuń d[i]
        dla i w range(5, 9):  # i==8 was the problem
            d[i] = i

    def test_resize2(self):
        # Another dict resizing bug (SF bug #1456209).
        # This caused Segmentation faults albo Illegal instructions.

        klasa X(object):
            def __hash__(self):
                zwróć 5
            def __eq__(self, other):
                jeżeli resizing:
                    d.clear()
                zwróć Nieprawda
        d = {}
        resizing = Nieprawda
        d[X()] = 1
        d[X()] = 2
        d[X()] = 3
        d[X()] = 4
        d[X()] = 5
        # now trigger a resize
        resizing = Prawda
        d[9] = 6

    def test_empty_presized_dict_in_freelist(self):
        # Bug #3537: jeżeli an empty but presized dict przy a size larger
        # than 7 was w the freelist, it triggered an assertion failure
        przy self.assertRaises(ZeroDivisionError):
            d = {'a': 1 // 0, 'b': Nic, 'c': Nic, 'd': Nic, 'e': Nic,
                 'f': Nic, 'g': Nic, 'h': Nic}
        d = {}

    def test_container_iterator(self):
        # Bug #3680: tp_traverse was nie implemented dla dictiter oraz
        # dictview objects.
        klasa C(object):
            dalej
        views = (dict.items, dict.values, dict.keys)
        dla v w views:
            obj = C()
            ref = weakref.ref(obj)
            container = {obj: 1}
            obj.v = v(container)
            obj.x = iter(obj.v)
            usuń obj, container
            gc.collect()
            self.assertIs(ref(), Nic, "Cycle was nie collected")

    def _not_tracked(self, t):
        # Nested containers can take several collections to untrack
        gc.collect()
        gc.collect()
        self.assertNieprawda(gc.is_tracked(t), t)

    def _tracked(self, t):
        self.assertPrawda(gc.is_tracked(t), t)
        gc.collect()
        gc.collect()
        self.assertPrawda(gc.is_tracked(t), t)

    @support.cpython_only
    def test_track_literals(self):
        # Test GC-optimization of dict literals
        x, y, z, w = 1.5, "a", (1, Nic), []

        self._not_tracked({})
        self._not_tracked({x:(), y:x, z:1})
        self._not_tracked({1: "a", "b": 2})
        self._not_tracked({1: 2, (Nic, Prawda, Nieprawda, ()): int})
        self._not_tracked({1: object()})

        # Dicts przy mutable elements are always tracked, even jeżeli those
        # elements are nie tracked right now.
        self._tracked({1: []})
        self._tracked({1: ([],)})
        self._tracked({1: {}})
        self._tracked({1: set()})

    @support.cpython_only
    def test_track_dynamic(self):
        # Test GC-optimization of dynamically-created dicts
        klasa MyObject(object):
            dalej
        x, y, z, w, o = 1.5, "a", (1, object()), [], MyObject()

        d = dict()
        self._not_tracked(d)
        d[1] = "a"
        self._not_tracked(d)
        d[y] = 2
        self._not_tracked(d)
        d[z] = 3
        self._not_tracked(d)
        self._not_tracked(d.copy())
        d[4] = w
        self._tracked(d)
        self._tracked(d.copy())
        d[4] = Nic
        self._not_tracked(d)
        self._not_tracked(d.copy())

        # dd isn't tracked right now, but it may mutate oraz therefore d
        # which contains it must be tracked.
        d = dict()
        dd = dict()
        d[1] = dd
        self._not_tracked(dd)
        self._tracked(d)
        dd[1] = d
        self._tracked(dd)

        d = dict.fromkeys([x, y, z])
        self._not_tracked(d)
        dd = dict()
        dd.update(d)
        self._not_tracked(dd)
        d = dict.fromkeys([x, y, z, o])
        self._tracked(d)
        dd = dict()
        dd.update(d)
        self._tracked(dd)

        d = dict(x=x, y=y, z=z)
        self._not_tracked(d)
        d = dict(x=x, y=y, z=z, w=w)
        self._tracked(d)
        d = dict()
        d.update(x=x, y=y, z=z)
        self._not_tracked(d)
        d.update(w=w)
        self._tracked(d)

        d = dict([(x, y), (z, 1)])
        self._not_tracked(d)
        d = dict([(x, y), (z, w)])
        self._tracked(d)
        d = dict()
        d.update([(x, y), (z, 1)])
        self._not_tracked(d)
        d.update([(x, y), (z, w)])
        self._tracked(d)

    @support.cpython_only
    def test_track_subtypes(self):
        # Dict subtypes are always tracked
        klasa MyDict(dict):
            dalej
        self._tracked(MyDict())

    def test_iterator_pickling(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            data = {1:"a", 2:"b", 3:"c"}
            it = iter(data)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(sorted(it), sorted(data))

            it = pickle.loads(d)
            spróbuj:
                drop = next(it)
            wyjąwszy StopIteration:
                kontynuuj
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            usuń data[drop]
            self.assertEqual(sorted(it), sorted(data))

    def test_itemiterator_pickling(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            data = {1:"a", 2:"b", 3:"c"}
            # dictviews aren't picklable, only their iterators
            itorg = iter(data.items())
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            # note that the type of type of the unpickled iterator
            # jest nie necessarily the same jako the original.  It jest
            # merely an object supporting the iterator protocol, uzyskajing
            # the same objects jako the original one.
            # self.assertEqual(type(itorg), type(it))
            self.assertIsInstance(it, collections.abc.Iterator)
            self.assertEqual(dict(it), data)

            it = pickle.loads(d)
            drop = next(it)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            usuń data[drop[0]]
            self.assertEqual(dict(it), data)

    def test_valuesiterator_pickling(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL):
            data = {1:"a", 2:"b", 3:"c"}
            # data.values() isn't picklable, only its iterator
            it = iter(data.values())
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(sorted(list(it)), sorted(list(data.values())))

            it = pickle.loads(d)
            drop = next(it)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            values = list(it) + [drop]
            self.assertEqual(sorted(values), sorted(list(data.values())))

    def test_instance_dict_getattr_str_subclass(self):
        klasa Foo:
            def __init__(self, msg):
                self.msg = msg
        f = Foo('123')
        klasa _str(str):
            dalej
        self.assertEqual(f.msg, getattr(f, _str('msg')))
        self.assertEqual(f.msg, f.__dict__[_str('msg')])

    def test_object_set_item_single_instance_non_str_key(self):
        klasa Foo: dalej
        f = Foo()
        f.__dict__[1] = 1
        f.a = 'a'
        self.assertEqual(f.__dict__, {1:1, 'a':'a'})

    def check_reentrant_insertion(self, mutate):
        # This object will trigger mutation of the dict when replaced
        # by another value.  Note this relies on refcounting: the test
        # won't achieve its purpose on fully-GCed Python implementations.
        klasa Mutating:
            def __del__(self):
                mutate(d)

        d = {k: Mutating() dla k w 'abcdefghijklmnopqr'}
        dla k w list(d):
            d[k] = k

    def test_reentrant_insertion(self):
        # Reentrant insertion shouldn't crash (see issue #22653)
        def mutate(d):
            d['b'] = 5
        self.check_reentrant_insertion(mutate)

        def mutate(d):
            d.update(self.__dict__)
            d.clear()
        self.check_reentrant_insertion(mutate)

        def mutate(d):
            dopóki d:
                d.popitem()
        self.check_reentrant_insertion(mutate)

    def test_merge_and_mutate(self):
        klasa X:
            def __hash__(self):
                zwróć 0

            def __eq__(self, o):
                other.clear()
                zwróć Nieprawda

        l = [(i,0) dla i w range(1, 1337)]
        other = dict(l)
        other[X()] = 0
        d = {X(): 0, 1: 1}
        self.assertRaises(RuntimeError, d.update, other)

z test zaimportuj mapping_tests

klasa GeneralMappingTests(mapping_tests.BasicTestMappingProtocol):
    type2test = dict

klasa Dict(dict):
    dalej

klasa SubclassMappingTests(mapping_tests.BasicTestMappingProtocol):
    type2test = Dict

jeżeli __name__ == "__main__":
    unittest.main()
