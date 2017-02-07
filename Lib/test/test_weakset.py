zaimportuj unittest
z weakref zaimportuj proxy, ref, WeakSet
zaimportuj operator
zaimportuj copy
zaimportuj string
zaimportuj os
z random zaimportuj randrange, shuffle
zaimportuj sys
zaimportuj warnings
zaimportuj collections
z collections zaimportuj UserString jako ustr
zaimportuj gc
zaimportuj contextlib


klasa Foo:
    dalej

klasa RefCycle:
    def __init__(self):
        self.cycle = self


klasa TestWeakSet(unittest.TestCase):

    def setUp(self):
        # need to keep references to them
        self.items = [ustr(c) dla c w ('a', 'b', 'c')]
        self.items2 = [ustr(c) dla c w ('x', 'y', 'z')]
        self.ab_items = [ustr(c) dla c w 'ab']
        self.abcde_items = [ustr(c) dla c w 'abcde']
        self.def_items = [ustr(c) dla c w 'def']
        self.ab_weakset = WeakSet(self.ab_items)
        self.abcde_weakset = WeakSet(self.abcde_items)
        self.def_weakset = WeakSet(self.def_items)
        self.letters = [ustr(c) dla c w string.ascii_letters]
        self.s = WeakSet(self.items)
        self.d = dict.fromkeys(self.items)
        self.obj = ustr('F')
        self.fs = WeakSet([self.obj])

    def test_methods(self):
        weaksetmethods = dir(WeakSet)
        dla method w dir(set):
            jeżeli method == 'test_c_api' albo method.startswith('_'):
                kontynuuj
            self.assertIn(method, weaksetmethods,
                         "WeakSet missing method " + method)

    def test_new_or_init(self):
        self.assertRaises(TypeError, WeakSet, [], 2)

    def test_len(self):
        self.assertEqual(len(self.s), len(self.d))
        self.assertEqual(len(self.fs), 1)
        usuń self.obj
        self.assertEqual(len(self.fs), 0)

    def test_contains(self):
        dla c w self.letters:
            self.assertEqual(c w self.s, c w self.d)
        # 1 jest nie weakref'able, but that TypeError jest caught by __contains__
        self.assertNotIn(1, self.s)
        self.assertIn(self.obj, self.fs)
        usuń self.obj
        self.assertNotIn(ustr('F'), self.fs)

    def test_union(self):
        u = self.s.union(self.items2)
        dla c w self.letters:
            self.assertEqual(c w u, c w self.d albo c w self.items2)
        self.assertEqual(self.s, WeakSet(self.items))
        self.assertEqual(type(u), WeakSet)
        self.assertRaises(TypeError, self.s.union, [[]])
        dla C w set, frozenset, dict.fromkeys, list, tuple:
            x = WeakSet(self.items + self.items2)
            c = C(self.items2)
            self.assertEqual(self.s.union(c), x)
            usuń c
        self.assertEqual(len(u), len(self.items) + len(self.items2))
        self.items2.pop()
        gc.collect()
        self.assertEqual(len(u), len(self.items) + len(self.items2))

    def test_or(self):
        i = self.s.union(self.items2)
        self.assertEqual(self.s | set(self.items2), i)
        self.assertEqual(self.s | frozenset(self.items2), i)

    def test_intersection(self):
        s = WeakSet(self.letters)
        i = s.intersection(self.items2)
        dla c w self.letters:
            self.assertEqual(c w i, c w self.items2 oraz c w self.letters)
        self.assertEqual(s, WeakSet(self.letters))
        self.assertEqual(type(i), WeakSet)
        dla C w set, frozenset, dict.fromkeys, list, tuple:
            x = WeakSet([])
            self.assertEqual(i.intersection(C(self.items)), x)
        self.assertEqual(len(i), len(self.items2))
        self.items2.pop()
        gc.collect()
        self.assertEqual(len(i), len(self.items2))

    def test_isdisjoint(self):
        self.assertPrawda(self.s.isdisjoint(WeakSet(self.items2)))
        self.assertPrawda(nie self.s.isdisjoint(WeakSet(self.letters)))

    def test_and(self):
        i = self.s.intersection(self.items2)
        self.assertEqual(self.s & set(self.items2), i)
        self.assertEqual(self.s & frozenset(self.items2), i)

    def test_difference(self):
        i = self.s.difference(self.items2)
        dla c w self.letters:
            self.assertEqual(c w i, c w self.d oraz c nie w self.items2)
        self.assertEqual(self.s, WeakSet(self.items))
        self.assertEqual(type(i), WeakSet)
        self.assertRaises(TypeError, self.s.difference, [[]])

    def test_sub(self):
        i = self.s.difference(self.items2)
        self.assertEqual(self.s - set(self.items2), i)
        self.assertEqual(self.s - frozenset(self.items2), i)

    def test_symmetric_difference(self):
        i = self.s.symmetric_difference(self.items2)
        dla c w self.letters:
            self.assertEqual(c w i, (c w self.d) ^ (c w self.items2))
        self.assertEqual(self.s, WeakSet(self.items))
        self.assertEqual(type(i), WeakSet)
        self.assertRaises(TypeError, self.s.symmetric_difference, [[]])
        self.assertEqual(len(i), len(self.items) + len(self.items2))
        self.items2.pop()
        gc.collect()
        self.assertEqual(len(i), len(self.items) + len(self.items2))

    def test_xor(self):
        i = self.s.symmetric_difference(self.items2)
        self.assertEqual(self.s ^ set(self.items2), i)
        self.assertEqual(self.s ^ frozenset(self.items2), i)

    def test_sub_and_super(self):
        self.assertPrawda(self.ab_weakset <= self.abcde_weakset)
        self.assertPrawda(self.abcde_weakset <= self.abcde_weakset)
        self.assertPrawda(self.abcde_weakset >= self.ab_weakset)
        self.assertNieprawda(self.abcde_weakset <= self.def_weakset)
        self.assertNieprawda(self.abcde_weakset >= self.def_weakset)
        self.assertPrawda(set('a').issubset('abc'))
        self.assertPrawda(set('abc').issuperset('a'))
        self.assertNieprawda(set('a').issubset('cbs'))
        self.assertNieprawda(set('cbs').issuperset('a'))

    def test_lt(self):
        self.assertPrawda(self.ab_weakset < self.abcde_weakset)
        self.assertNieprawda(self.abcde_weakset < self.def_weakset)
        self.assertNieprawda(self.ab_weakset < self.ab_weakset)
        self.assertNieprawda(WeakSet() < WeakSet())

    def test_gt(self):
        self.assertPrawda(self.abcde_weakset > self.ab_weakset)
        self.assertNieprawda(self.abcde_weakset > self.def_weakset)
        self.assertNieprawda(self.ab_weakset > self.ab_weakset)
        self.assertNieprawda(WeakSet() > WeakSet())

    def test_gc(self):
        # Create a nest of cycles to exercise overall ref count check
        s = WeakSet(Foo() dla i w range(1000))
        dla elem w s:
            elem.cycle = s
            elem.sub = elem
            elem.set = WeakSet([elem])

    def test_subclass_with_custom_hash(self):
        # Bug #1257731
        klasa H(WeakSet):
            def __hash__(self):
                zwróć int(id(self) & 0x7fffffff)
        s=H()
        f=set()
        f.add(s)
        self.assertIn(s, f)
        f.remove(s)
        f.add(s)
        f.discard(s)

    def test_init(self):
        s = WeakSet()
        s.__init__(self.items)
        self.assertEqual(s, self.s)
        s.__init__(self.items2)
        self.assertEqual(s, WeakSet(self.items2))
        self.assertRaises(TypeError, s.__init__, s, 2);
        self.assertRaises(TypeError, s.__init__, 1);

    def test_constructor_identity(self):
        s = WeakSet(self.items)
        t = WeakSet(s)
        self.assertNotEqual(id(s), id(t))

    def test_hash(self):
        self.assertRaises(TypeError, hash, self.s)

    def test_clear(self):
        self.s.clear()
        self.assertEqual(self.s, WeakSet([]))
        self.assertEqual(len(self.s), 0)

    def test_copy(self):
        dup = self.s.copy()
        self.assertEqual(self.s, dup)
        self.assertNotEqual(id(self.s), id(dup))

    def test_add(self):
        x = ustr('Q')
        self.s.add(x)
        self.assertIn(x, self.s)
        dup = self.s.copy()
        self.s.add(x)
        self.assertEqual(self.s, dup)
        self.assertRaises(TypeError, self.s.add, [])
        self.fs.add(Foo())
        self.assertPrawda(len(self.fs) == 1)
        self.fs.add(self.obj)
        self.assertPrawda(len(self.fs) == 1)

    def test_remove(self):
        x = ustr('a')
        self.s.remove(x)
        self.assertNotIn(x, self.s)
        self.assertRaises(KeyError, self.s.remove, x)
        self.assertRaises(TypeError, self.s.remove, [])

    def test_discard(self):
        a, q = ustr('a'), ustr('Q')
        self.s.discard(a)
        self.assertNotIn(a, self.s)
        self.s.discard(q)
        self.assertRaises(TypeError, self.s.discard, [])

    def test_pop(self):
        dla i w range(len(self.s)):
            elem = self.s.pop()
            self.assertNotIn(elem, self.s)
        self.assertRaises(KeyError, self.s.pop)

    def test_update(self):
        retval = self.s.update(self.items2)
        self.assertEqual(retval, Nic)
        dla c w (self.items + self.items2):
            self.assertIn(c, self.s)
        self.assertRaises(TypeError, self.s.update, [[]])

    def test_update_set(self):
        self.s.update(set(self.items2))
        dla c w (self.items + self.items2):
            self.assertIn(c, self.s)

    def test_ior(self):
        self.s |= set(self.items2)
        dla c w (self.items + self.items2):
            self.assertIn(c, self.s)

    def test_intersection_update(self):
        retval = self.s.intersection_update(self.items2)
        self.assertEqual(retval, Nic)
        dla c w (self.items + self.items2):
            jeżeli c w self.items2 oraz c w self.items:
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)
        self.assertRaises(TypeError, self.s.intersection_update, [[]])

    def test_iand(self):
        self.s &= set(self.items2)
        dla c w (self.items + self.items2):
            jeżeli c w self.items2 oraz c w self.items:
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)

    def test_difference_update(self):
        retval = self.s.difference_update(self.items2)
        self.assertEqual(retval, Nic)
        dla c w (self.items + self.items2):
            jeżeli c w self.items oraz c nie w self.items2:
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)
        self.assertRaises(TypeError, self.s.difference_update, [[]])
        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])

    def test_isub(self):
        self.s -= set(self.items2)
        dla c w (self.items + self.items2):
            jeżeli c w self.items oraz c nie w self.items2:
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)

    def test_symmetric_difference_update(self):
        retval = self.s.symmetric_difference_update(self.items2)
        self.assertEqual(retval, Nic)
        dla c w (self.items + self.items2):
            jeżeli (c w self.items) ^ (c w self.items2):
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)
        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])

    def test_ixor(self):
        self.s ^= set(self.items2)
        dla c w (self.items + self.items2):
            jeżeli (c w self.items) ^ (c w self.items2):
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)

    def test_inplace_on_self(self):
        t = self.s.copy()
        t |= t
        self.assertEqual(t, self.s)
        t &= t
        self.assertEqual(t, self.s)
        t -= t
        self.assertEqual(t, WeakSet())
        t = self.s.copy()
        t ^= t
        self.assertEqual(t, WeakSet())

    def test_eq(self):
        # issue 5964
        self.assertPrawda(self.s == self.s)
        self.assertPrawda(self.s == WeakSet(self.items))
        self.assertNieprawda(self.s == set(self.items))
        self.assertNieprawda(self.s == list(self.items))
        self.assertNieprawda(self.s == tuple(self.items))
        self.assertNieprawda(self.s == WeakSet([Foo]))
        self.assertNieprawda(self.s == 1)

    def test_ne(self):
        self.assertPrawda(self.s != set(self.items))
        s1 = WeakSet()
        s2 = WeakSet()
        self.assertNieprawda(s1 != s2)

    def test_weak_destroy_while_iterating(self):
        # Issue #7105: iterators shouldn't crash when a key jest implicitly removed
        # Create new items to be sure no-one inaczej holds a reference
        items = [ustr(c) dla c w ('a', 'b', 'c')]
        s = WeakSet(items)
        it = iter(s)
        next(it)             # Trigger internal iteration
        # Destroy an item
        usuń items[-1]
        gc.collect()    # just w case
        # We have removed either the first consumed items, albo another one
        self.assertIn(len(list(it)), [len(items), len(items) - 1])
        usuń it
        # The removal has been committed
        self.assertEqual(len(s), len(items))

    def test_weak_destroy_and_mutate_while_iterating(self):
        # Issue #7105: iterators shouldn't crash when a key jest implicitly removed
        items = [ustr(c) dla c w string.ascii_letters]
        s = WeakSet(items)
        @contextlib.contextmanager
        def testcontext():
            spróbuj:
                it = iter(s)
                # Start iterator
                uzyskajed = ustr(str(next(it)))
                # Schedule an item dla removal oraz recreate it
                u = ustr(str(items.pop()))
                jeżeli uzyskajed == u:
                    # The iterator still has a reference to the removed item,
                    # advance it (issue #20006).
                    next(it)
                gc.collect()      # just w case
                uzyskaj u
            w_końcu:
                it = Nic           # should commit all removals

        przy testcontext() jako u:
            self.assertNotIn(u, s)
        przy testcontext() jako u:
            self.assertRaises(KeyError, s.remove, u)
        self.assertNotIn(u, s)
        przy testcontext() jako u:
            s.add(u)
        self.assertIn(u, s)
        t = s.copy()
        przy testcontext() jako u:
            s.update(t)
        self.assertEqual(len(s), len(t))
        przy testcontext() jako u:
            s.clear()
        self.assertEqual(len(s), 0)

    def test_len_cycles(self):
        N = 20
        items = [RefCycle() dla i w range(N)]
        s = WeakSet(items)
        usuń items
        it = iter(s)
        spróbuj:
            next(it)
        wyjąwszy StopIteration:
            dalej
        gc.collect()
        n1 = len(s)
        usuń it
        gc.collect()
        n2 = len(s)
        # one item may be kept alive inside the iterator
        self.assertIn(n1, (0, 1))
        self.assertEqual(n2, 0)

    def test_len_race(self):
        # Extended sanity checks dla len() w the face of cyclic collection
        self.addCleanup(gc.set_threshold, *gc.get_threshold())
        dla th w range(1, 100):
            N = 20
            gc.collect(0)
            gc.set_threshold(th, th, th)
            items = [RefCycle() dla i w range(N)]
            s = WeakSet(items)
            usuń items
            # All items will be collected at next garbage collection dalej
            it = iter(s)
            spróbuj:
                next(it)
            wyjąwszy StopIteration:
                dalej
            n1 = len(s)
            usuń it
            n2 = len(s)
            self.assertGreaterEqual(n1, 0)
            self.assertLessEqual(n1, N)
            self.assertGreaterEqual(n2, 0)
            self.assertLessEqual(n2, n1)


jeżeli __name__ == "__main__":
    unittest.main()
