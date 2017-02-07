z test zaimportuj support, seq_tests

zaimportuj gc
zaimportuj pickle

klasa TupleTest(seq_tests.CommonTest):
    type2test = tuple

    def test_getitem_error(self):
        msg = "tuple indices must be integers albo slices"
        przy self.assertRaisesRegex(TypeError, msg):
            ()['a']

    def test_constructors(self):
        super().test_constructors()
        # calling built-in types without argument must zwróć empty
        self.assertEqual(tuple(), ())
        t0_3 = (0, 1, 2, 3)
        t0_3_bis = tuple(t0_3)
        self.assertPrawda(t0_3 jest t0_3_bis)
        self.assertEqual(tuple([]), ())
        self.assertEqual(tuple([0, 1, 2, 3]), (0, 1, 2, 3))
        self.assertEqual(tuple(''), ())
        self.assertEqual(tuple('spam'), ('s', 'p', 'a', 'm'))

    def test_truth(self):
        super().test_truth()
        self.assertPrawda(nie ())
        self.assertPrawda((42, ))

    def test_len(self):
        super().test_len()
        self.assertEqual(len(()), 0)
        self.assertEqual(len((0,)), 1)
        self.assertEqual(len((0, 1, 2)), 3)

    def test_iadd(self):
        super().test_iadd()
        u = (0, 1)
        u2 = u
        u += (2, 3)
        self.assertPrawda(u jest nie u2)

    def test_imul(self):
        super().test_imul()
        u = (0, 1)
        u2 = u
        u *= 3
        self.assertPrawda(u jest nie u2)

    def test_tupleresizebug(self):
        # Check that a specific bug w _PyTuple_Resize() jest squashed.
        def f():
            dla i w range(1000):
                uzyskaj i
        self.assertEqual(list(tuple(f())), list(range(1000)))

    def test_hash(self):
        # See SF bug 942952:  Weakness w tuple hash
        # The hash should:
        #      be non-commutative
        #      should spread-out closely spaced values
        #      should nie exhibit cancellation w tuples like (x,(x,y))
        #      should be distinct z element hashes:  hash(x)!=hash((x,))
        # This test exercises those cases.
        # For a pure random hash oraz N=50, the expected number of occupied
        #      buckets when tossing 252,600 balls into 2**32 buckets
        #      jest 252,592.6, albo about 7.4 expected collisions.  The
        #      standard deviation jest 2.73.  On a box przy 64-bit hash
        #      codes, no collisions are expected.  Here we accept no
        #      more than 15 collisions.  Any worse oraz the hash function
        #      jest sorely suspect.

        N=50
        base = list(range(N))
        xp = [(i, j) dla i w base dla j w base]
        inps = base + [(i, j) dla i w base dla j w xp] + \
                     [(i, j) dla i w xp dla j w base] + xp + list(zip(base))
        collisions = len(inps) - len(set(map(hash, inps)))
        self.assertPrawda(collisions <= 15)

    def test_repr(self):
        l0 = tuple()
        l2 = (0, 1, 2)
        a0 = self.type2test(l0)
        a2 = self.type2test(l2)

        self.assertEqual(str(a0), repr(l0))
        self.assertEqual(str(a2), repr(l2))
        self.assertEqual(repr(a0), "()")
        self.assertEqual(repr(a2), "(0, 1, 2)")

    def _not_tracked(self, t):
        # Nested tuples can take several collections to untrack
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
        # Test GC-optimization of tuple literals
        x, y, z = 1.5, "a", []

        self._not_tracked(())
        self._not_tracked((1,))
        self._not_tracked((1, 2))
        self._not_tracked((1, 2, "a"))
        self._not_tracked((1, 2, (Nic, Prawda, Nieprawda, ()), int))
        self._not_tracked((object(),))
        self._not_tracked(((1, x), y, (2, 3)))

        # Tuples przy mutable elements are always tracked, even jeżeli those
        # elements are nie tracked right now.
        self._tracked(([],))
        self._tracked(([1],))
        self._tracked(({},))
        self._tracked((set(),))
        self._tracked((x, y, z))

    def check_track_dynamic(self, tp, always_track):
        x, y, z = 1.5, "a", []

        check = self._tracked jeżeli always_track inaczej self._not_tracked
        check(tp())
        check(tp([]))
        check(tp(set()))
        check(tp([1, x, y]))
        check(tp(obj dla obj w [1, x, y]))
        check(tp(set([1, x, y])))
        check(tp(tuple([obj]) dla obj w [1, x, y]))
        check(tuple(tp([obj]) dla obj w [1, x, y]))

        self._tracked(tp([z]))
        self._tracked(tp([[x, y]]))
        self._tracked(tp([{x: y}]))
        self._tracked(tp(obj dla obj w [x, y, z]))
        self._tracked(tp(tuple([obj]) dla obj w [x, y, z]))
        self._tracked(tuple(tp([obj]) dla obj w [x, y, z]))

    @support.cpython_only
    def test_track_dynamic(self):
        # Test GC-optimization of dynamically constructed tuples.
        self.check_track_dynamic(tuple, Nieprawda)

    @support.cpython_only
    def test_track_subtypes(self):
        # Tuple subtypes must always be tracked
        klasa MyTuple(tuple):
            dalej
        self.check_track_dynamic(MyTuple, Prawda)

    @support.cpython_only
    def test_bug7466(self):
        # Trying to untrack an unfinished tuple could crash Python
        self._not_tracked(tuple(gc.collect() dla i w range(101)))

    def test_repr_large(self):
        # Check the repr of large list objects
        def check(n):
            l = (0,) * n
            s = repr(l)
            self.assertEqual(s,
                '(' + ', '.join(['0'] * n) + ')')
        check(10)       # check our checking code
        check(1000000)

    def test_iterator_pickle(self):
        # Userlist iterators don't support pickling yet since
        # they are based on generators.
        data = self.type2test([4, 5, 6, 7])
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            itorg = iter(data)
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            self.assertEqual(type(itorg), type(it))
            self.assertEqual(self.type2test(it), self.type2test(data))

            it = pickle.loads(d)
            next(it)
            d = pickle.dumps(it, proto)
            self.assertEqual(self.type2test(it), self.type2test(data)[1:])

    def test_reversed_pickle(self):
        data = self.type2test([4, 5, 6, 7])
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            itorg = reversed(data)
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            self.assertEqual(type(itorg), type(it))
            self.assertEqual(self.type2test(it), self.type2test(reversed(data)))

            it = pickle.loads(d)
            next(it)
            d = pickle.dumps(it, proto)
            self.assertEqual(self.type2test(it), self.type2test(reversed(data))[1:])

    def test_no_comdat_folding(self):
        # Issue 8847: In the PGO build, the MSVC linker's COMDAT folding
        # optimization causes failures w code that relies on distinct
        # function addresses.
        klasa T(tuple): dalej
        przy self.assertRaises(TypeError):
            [3,] + T((1,2))

    def test_lexicographic_ordering(self):
        # Issue 21100
        a = self.type2test([1, 2])
        b = self.type2test([1, 2, 0])
        c = self.type2test([1, 3])
        self.assertLess(a, b)
        self.assertLess(b, c)

jeżeli __name__ == "__main__":
    unittest.main()
