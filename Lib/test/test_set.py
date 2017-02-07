zaimportuj unittest
z test zaimportuj support
zaimportuj gc
zaimportuj weakref
zaimportuj operator
zaimportuj copy
zaimportuj pickle
z random zaimportuj randrange, shuffle
zaimportuj sys
zaimportuj warnings
zaimportuj collections
zaimportuj collections.abc

klasa PassThru(Exception):
    dalej

def check_pass_thru():
    podnieś PassThru
    uzyskaj 1

klasa BadCmp:
    def __hash__(self):
        zwróć 1
    def __eq__(self, other):
        podnieś RuntimeError

klasa ReprWrapper:
    'Used to test self-referential repr() calls'
    def __repr__(self):
        zwróć repr(self.value)

klasa HashCountingInt(int):
    'int-like object that counts the number of times __hash__ jest called'
    def __init__(self, *args):
        self.hash_count = 0
    def __hash__(self):
        self.hash_count += 1
        zwróć int.__hash__(self)

klasa TestJointOps:
    # Tests common to both set oraz frozenset

    def setUp(self):
        self.word = word = 'simsalabim'
        self.otherword = 'madagascar'
        self.letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.s = self.thetype(word)
        self.d = dict.fromkeys(word)

    def test_new_or_init(self):
        self.assertRaises(TypeError, self.thetype, [], 2)
        self.assertRaises(TypeError, set().__init__, a=1)

    def test_uniquification(self):
        actual = sorted(self.s)
        expected = sorted(self.d)
        self.assertEqual(actual, expected)
        self.assertRaises(PassThru, self.thetype, check_pass_thru())
        self.assertRaises(TypeError, self.thetype, [[]])

    def test_len(self):
        self.assertEqual(len(self.s), len(self.d))

    def test_contains(self):
        dla c w self.letters:
            self.assertEqual(c w self.s, c w self.d)
        self.assertRaises(TypeError, self.s.__contains__, [[]])
        s = self.thetype([frozenset(self.letters)])
        self.assertIn(self.thetype(self.letters), s)

    def test_union(self):
        u = self.s.union(self.otherword)
        dla c w self.letters:
            self.assertEqual(c w u, c w self.d albo c w self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(u), self.basetype)
        self.assertRaises(PassThru, self.s.union, check_pass_thru())
        self.assertRaises(TypeError, self.s.union, [[]])
        dla C w set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').union(C('cdc')), set('abcd'))
            self.assertEqual(self.thetype('abcba').union(C('efgfe')), set('abcefg'))
            self.assertEqual(self.thetype('abcba').union(C('ccb')), set('abc'))
            self.assertEqual(self.thetype('abcba').union(C('ef')), set('abcef'))
            self.assertEqual(self.thetype('abcba').union(C('ef'), C('fg')), set('abcefg'))

        # Issue #6573
        x = self.thetype()
        self.assertEqual(x.union(set([1]), x, set([2])), self.thetype([1, 2]))

    def test_or(self):
        i = self.s.union(self.otherword)
        self.assertEqual(self.s | set(self.otherword), i)
        self.assertEqual(self.s | frozenset(self.otherword), i)
        spróbuj:
            self.s | self.otherword
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("s|t did nie screen-out general iterables")

    def test_intersection(self):
        i = self.s.intersection(self.otherword)
        dla c w self.letters:
            self.assertEqual(c w i, c w self.d oraz c w self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(i), self.basetype)
        self.assertRaises(PassThru, self.s.intersection, check_pass_thru())
        dla C w set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').intersection(C('cdc')), set('cc'))
            self.assertEqual(self.thetype('abcba').intersection(C('efgfe')), set(''))
            self.assertEqual(self.thetype('abcba').intersection(C('ccb')), set('bc'))
            self.assertEqual(self.thetype('abcba').intersection(C('ef')), set(''))
            self.assertEqual(self.thetype('abcba').intersection(C('cbcf'), C('bag')), set('b'))
        s = self.thetype('abcba')
        z = s.intersection()
        jeżeli self.thetype == frozenset():
            self.assertEqual(id(s), id(z))
        inaczej:
            self.assertNotEqual(id(s), id(z))

    def test_isdisjoint(self):
        def f(s1, s2):
            'Pure python equivalent of isdisjoint()'
            zwróć nie set(s1).intersection(s2)
        dla larg w '', 'a', 'ab', 'abc', 'ababac', 'cdc', 'cc', 'efgfe', 'ccb', 'ef':
            s1 = self.thetype(larg)
            dla rarg w '', 'a', 'ab', 'abc', 'ababac', 'cdc', 'cc', 'efgfe', 'ccb', 'ef':
                dla C w set, frozenset, dict.fromkeys, str, list, tuple:
                    s2 = C(rarg)
                    actual = s1.isdisjoint(s2)
                    expected = f(s1, s2)
                    self.assertEqual(actual, expected)
                    self.assertPrawda(actual jest Prawda albo actual jest Nieprawda)

    def test_and(self):
        i = self.s.intersection(self.otherword)
        self.assertEqual(self.s & set(self.otherword), i)
        self.assertEqual(self.s & frozenset(self.otherword), i)
        spróbuj:
            self.s & self.otherword
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("s&t did nie screen-out general iterables")

    def test_difference(self):
        i = self.s.difference(self.otherword)
        dla c w self.letters:
            self.assertEqual(c w i, c w self.d oraz c nie w self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(i), self.basetype)
        self.assertRaises(PassThru, self.s.difference, check_pass_thru())
        self.assertRaises(TypeError, self.s.difference, [[]])
        dla C w set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').difference(C('cdc')), set('ab'))
            self.assertEqual(self.thetype('abcba').difference(C('efgfe')), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(C('ccb')), set('a'))
            self.assertEqual(self.thetype('abcba').difference(C('ef')), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(C('a'), C('b')), set('c'))

    def test_sub(self):
        i = self.s.difference(self.otherword)
        self.assertEqual(self.s - set(self.otherword), i)
        self.assertEqual(self.s - frozenset(self.otherword), i)
        spróbuj:
            self.s - self.otherword
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("s-t did nie screen-out general iterables")

    def test_symmetric_difference(self):
        i = self.s.symmetric_difference(self.otherword)
        dla c w self.letters:
            self.assertEqual(c w i, (c w self.d) ^ (c w self.otherword))
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(i), self.basetype)
        self.assertRaises(PassThru, self.s.symmetric_difference, check_pass_thru())
        self.assertRaises(TypeError, self.s.symmetric_difference, [[]])
        dla C w set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('cdc')), set('abd'))
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('efgfe')), set('abcefg'))
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('ccb')), set('a'))
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('ef')), set('abcef'))

    def test_xor(self):
        i = self.s.symmetric_difference(self.otherword)
        self.assertEqual(self.s ^ set(self.otherword), i)
        self.assertEqual(self.s ^ frozenset(self.otherword), i)
        spróbuj:
            self.s ^ self.otherword
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("s^t did nie screen-out general iterables")

    def test_equality(self):
        self.assertEqual(self.s, set(self.word))
        self.assertEqual(self.s, frozenset(self.word))
        self.assertEqual(self.s == self.word, Nieprawda)
        self.assertNotEqual(self.s, set(self.otherword))
        self.assertNotEqual(self.s, frozenset(self.otherword))
        self.assertEqual(self.s != self.word, Prawda)

    def test_setOfFrozensets(self):
        t = map(frozenset, ['abcdef', 'bcd', 'bdcb', 'fed', 'fedccba'])
        s = self.thetype(t)
        self.assertEqual(len(s), 3)

    def test_sub_and_super(self):
        p, q, r = map(self.thetype, ['ab', 'abcde', 'def'])
        self.assertPrawda(p < q)
        self.assertPrawda(p <= q)
        self.assertPrawda(q <= q)
        self.assertPrawda(q > p)
        self.assertPrawda(q >= p)
        self.assertNieprawda(q < r)
        self.assertNieprawda(q <= r)
        self.assertNieprawda(q > r)
        self.assertNieprawda(q >= r)
        self.assertPrawda(set('a').issubset('abc'))
        self.assertPrawda(set('abc').issuperset('a'))
        self.assertNieprawda(set('a').issubset('cbs'))
        self.assertNieprawda(set('cbs').issuperset('a'))

    def test_pickling(self):
        dla i w range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(self.s, i)
            dup = pickle.loads(p)
            self.assertEqual(self.s, dup, "%s != %s" % (self.s, dup))
            jeżeli type(self.s) nie w (set, frozenset):
                self.s.x = 10
                p = pickle.dumps(self.s, i)
                dup = pickle.loads(p)
                self.assertEqual(self.s.x, dup.x)

    def test_iterator_pickling(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            itorg = iter(self.s)
            data = self.thetype(self.s)
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            # Set iterators unpickle jako list iterators due to the
            # undefined order of set items.
            # self.assertEqual(type(itorg), type(it))
            self.assertIsInstance(it, collections.abc.Iterator)
            self.assertEqual(self.thetype(it), data)

            it = pickle.loads(d)
            spróbuj:
                drop = next(it)
            wyjąwszy StopIteration:
                kontynuuj
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(self.thetype(it), data - self.thetype((drop,)))

    def test_deepcopy(self):
        klasa Tracer:
            def __init__(self, value):
                self.value = value
            def __hash__(self):
                zwróć self.value
            def __deepcopy__(self, memo=Nic):
                zwróć Tracer(self.value + 1)
        t = Tracer(10)
        s = self.thetype([t])
        dup = copy.deepcopy(s)
        self.assertNotEqual(id(s), id(dup))
        dla elem w dup:
            newt = elem
        self.assertNotEqual(id(t), id(newt))
        self.assertEqual(t.value + 1, newt.value)

    def test_gc(self):
        # Create a nest of cycles to exercise overall ref count check
        klasa A:
            dalej
        s = set(A() dla i w range(1000))
        dla elem w s:
            elem.cycle = s
            elem.sub = elem
            elem.set = set([elem])

    def test_subclass_with_custom_hash(self):
        # Bug #1257731
        klasa H(self.thetype):
            def __hash__(self):
                zwróć int(id(self) & 0x7fffffff)
        s=H()
        f=set()
        f.add(s)
        self.assertIn(s, f)
        f.remove(s)
        f.add(s)
        f.discard(s)

    def test_badcmp(self):
        s = self.thetype([BadCmp()])
        # Detect comparison errors during insertion oraz lookup
        self.assertRaises(RuntimeError, self.thetype, [BadCmp(), BadCmp()])
        self.assertRaises(RuntimeError, s.__contains__, BadCmp())
        # Detect errors during mutating operations
        jeżeli hasattr(s, 'add'):
            self.assertRaises(RuntimeError, s.add, BadCmp())
            self.assertRaises(RuntimeError, s.discard, BadCmp())
            self.assertRaises(RuntimeError, s.remove, BadCmp())

    def test_cyclical_repr(self):
        w = ReprWrapper()
        s = self.thetype([w])
        w.value = s
        jeżeli self.thetype == set:
            self.assertEqual(repr(s), '{set(...)}')
        inaczej:
            name = repr(s).partition('(')[0]    # strip klasa name
            self.assertEqual(repr(s), '%s({%s(...)})' % (name, name))

    def test_cyclical_print(self):
        w = ReprWrapper()
        s = self.thetype([w])
        w.value = s
        fo = open(support.TESTFN, "w")
        spróbuj:
            fo.write(str(s))
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(s))
        w_końcu:
            fo.close()
            support.unlink(support.TESTFN)

    def test_do_not_rehash_dict_keys(self):
        n = 10
        d = dict.fromkeys(map(HashCountingInt, range(n)))
        self.assertEqual(sum(elem.hash_count dla elem w d), n)
        s = self.thetype(d)
        self.assertEqual(sum(elem.hash_count dla elem w d), n)
        s.difference(d)
        self.assertEqual(sum(elem.hash_count dla elem w d), n)
        jeżeli hasattr(s, 'symmetric_difference_update'):
            s.symmetric_difference_update(d)
        self.assertEqual(sum(elem.hash_count dla elem w d), n)
        d2 = dict.fromkeys(set(d))
        self.assertEqual(sum(elem.hash_count dla elem w d), n)
        d3 = dict.fromkeys(frozenset(d))
        self.assertEqual(sum(elem.hash_count dla elem w d), n)
        d3 = dict.fromkeys(frozenset(d), 123)
        self.assertEqual(sum(elem.hash_count dla elem w d), n)
        self.assertEqual(d3, dict.fromkeys(d, 123))

    def test_container_iterator(self):
        # Bug #3680: tp_traverse was nie implemented dla set iterator object
        klasa C(object):
            dalej
        obj = C()
        ref = weakref.ref(obj)
        container = set([obj, 1])
        obj.x = iter(container)
        usuń obj, container
        gc.collect()
        self.assertPrawda(ref() jest Nic, "Cycle was nie collected")

klasa TestSet(TestJointOps, unittest.TestCase):
    thetype = set
    basetype = set

    def test_init(self):
        s = self.thetype()
        s.__init__(self.word)
        self.assertEqual(s, set(self.word))
        s.__init__(self.otherword)
        self.assertEqual(s, set(self.otherword))
        self.assertRaises(TypeError, s.__init__, s, 2);
        self.assertRaises(TypeError, s.__init__, 1);

    def test_constructor_identity(self):
        s = self.thetype(range(3))
        t = self.thetype(s)
        self.assertNotEqual(id(s), id(t))

    def test_set_literal(self):
        s = set([1,2,3])
        t = {1,2,3}
        self.assertEqual(s, t)

    def test_hash(self):
        self.assertRaises(TypeError, hash, self.s)

    def test_clear(self):
        self.s.clear()
        self.assertEqual(self.s, set())
        self.assertEqual(len(self.s), 0)

    def test_copy(self):
        dup = self.s.copy()
        self.assertEqual(self.s, dup)
        self.assertNotEqual(id(self.s), id(dup))
        self.assertEqual(type(dup), self.basetype)

    def test_add(self):
        self.s.add('Q')
        self.assertIn('Q', self.s)
        dup = self.s.copy()
        self.s.add('Q')
        self.assertEqual(self.s, dup)
        self.assertRaises(TypeError, self.s.add, [])

    def test_remove(self):
        self.s.remove('a')
        self.assertNotIn('a', self.s)
        self.assertRaises(KeyError, self.s.remove, 'Q')
        self.assertRaises(TypeError, self.s.remove, [])
        s = self.thetype([frozenset(self.word)])
        self.assertIn(self.thetype(self.word), s)
        s.remove(self.thetype(self.word))
        self.assertNotIn(self.thetype(self.word), s)
        self.assertRaises(KeyError, self.s.remove, self.thetype(self.word))

    def test_remove_keyerror_unpacking(self):
        # bug:  www.python.org/sf/1576657
        dla v1 w ['Q', (1,)]:
            spróbuj:
                self.s.remove(v1)
            wyjąwszy KeyError jako e:
                v2 = e.args[0]
                self.assertEqual(v1, v2)
            inaczej:
                self.fail()

    def test_remove_keyerror_set(self):
        key = self.thetype([3, 4])
        spróbuj:
            self.s.remove(key)
        wyjąwszy KeyError jako e:
            self.assertPrawda(e.args[0] jest key,
                         "KeyError should be {0}, nie {1}".format(key,
                                                                  e.args[0]))
        inaczej:
            self.fail()

    def test_discard(self):
        self.s.discard('a')
        self.assertNotIn('a', self.s)
        self.s.discard('Q')
        self.assertRaises(TypeError, self.s.discard, [])
        s = self.thetype([frozenset(self.word)])
        self.assertIn(self.thetype(self.word), s)
        s.discard(self.thetype(self.word))
        self.assertNotIn(self.thetype(self.word), s)
        s.discard(self.thetype(self.word))

    def test_pop(self):
        dla i w range(len(self.s)):
            elem = self.s.pop()
            self.assertNotIn(elem, self.s)
        self.assertRaises(KeyError, self.s.pop)

    def test_update(self):
        retval = self.s.update(self.otherword)
        self.assertEqual(retval, Nic)
        dla c w (self.word + self.otherword):
            self.assertIn(c, self.s)
        self.assertRaises(PassThru, self.s.update, check_pass_thru())
        self.assertRaises(TypeError, self.s.update, [[]])
        dla p, q w (('cdc', 'abcd'), ('efgfe', 'abcefg'), ('ccb', 'abc'), ('ef', 'abcef')):
            dla C w set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.update(C(p)), Nic)
                self.assertEqual(s, set(q))
        dla p w ('cdc', 'efgfe', 'ccb', 'ef', 'abcda'):
            q = 'ahi'
            dla C w set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.update(C(p), C(q)), Nic)
                self.assertEqual(s, set(s) | set(p) | set(q))

    def test_ior(self):
        self.s |= set(self.otherword)
        dla c w (self.word + self.otherword):
            self.assertIn(c, self.s)

    def test_intersection_update(self):
        retval = self.s.intersection_update(self.otherword)
        self.assertEqual(retval, Nic)
        dla c w (self.word + self.otherword):
            jeżeli c w self.otherword oraz c w self.word:
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)
        self.assertRaises(PassThru, self.s.intersection_update, check_pass_thru())
        self.assertRaises(TypeError, self.s.intersection_update, [[]])
        dla p, q w (('cdc', 'c'), ('efgfe', ''), ('ccb', 'bc'), ('ef', '')):
            dla C w set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.intersection_update(C(p)), Nic)
                self.assertEqual(s, set(q))
                ss = 'abcba'
                s = self.thetype(ss)
                t = 'cbc'
                self.assertEqual(s.intersection_update(C(p), C(t)), Nic)
                self.assertEqual(s, set('abcba')&set(p)&set(t))

    def test_iand(self):
        self.s &= set(self.otherword)
        dla c w (self.word + self.otherword):
            jeżeli c w self.otherword oraz c w self.word:
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)

    def test_difference_update(self):
        retval = self.s.difference_update(self.otherword)
        self.assertEqual(retval, Nic)
        dla c w (self.word + self.otherword):
            jeżeli c w self.word oraz c nie w self.otherword:
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)
        self.assertRaises(PassThru, self.s.difference_update, check_pass_thru())
        self.assertRaises(TypeError, self.s.difference_update, [[]])
        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])
        dla p, q w (('cdc', 'ab'), ('efgfe', 'abc'), ('ccb', 'a'), ('ef', 'abc')):
            dla C w set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.difference_update(C(p)), Nic)
                self.assertEqual(s, set(q))

                s = self.thetype('abcdefghih')
                s.difference_update()
                self.assertEqual(s, self.thetype('abcdefghih'))

                s = self.thetype('abcdefghih')
                s.difference_update(C('aba'))
                self.assertEqual(s, self.thetype('cdefghih'))

                s = self.thetype('abcdefghih')
                s.difference_update(C('cdc'), C('aba'))
                self.assertEqual(s, self.thetype('efghih'))

    def test_isub(self):
        self.s -= set(self.otherword)
        dla c w (self.word + self.otherword):
            jeżeli c w self.word oraz c nie w self.otherword:
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)

    def test_symmetric_difference_update(self):
        retval = self.s.symmetric_difference_update(self.otherword)
        self.assertEqual(retval, Nic)
        dla c w (self.word + self.otherword):
            jeżeli (c w self.word) ^ (c w self.otherword):
                self.assertIn(c, self.s)
            inaczej:
                self.assertNotIn(c, self.s)
        self.assertRaises(PassThru, self.s.symmetric_difference_update, check_pass_thru())
        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])
        dla p, q w (('cdc', 'abd'), ('efgfe', 'abcefg'), ('ccb', 'a'), ('ef', 'abcef')):
            dla C w set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.symmetric_difference_update(C(p)), Nic)
                self.assertEqual(s, set(q))

    def test_ixor(self):
        self.s ^= set(self.otherword)
        dla c w (self.word + self.otherword):
            jeżeli (c w self.word) ^ (c w self.otherword):
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
        self.assertEqual(t, self.thetype())
        t = self.s.copy()
        t ^= t
        self.assertEqual(t, self.thetype())

    def test_weakref(self):
        s = self.thetype('gallahad')
        p = weakref.proxy(s)
        self.assertEqual(str(p), str(s))
        s = Nic
        self.assertRaises(ReferenceError, str, p)

    def test_rich_compare(self):
        klasa TestRichSetCompare:
            def __gt__(self, some_set):
                self.gt_called = Prawda
                zwróć Nieprawda
            def __lt__(self, some_set):
                self.lt_called = Prawda
                zwróć Nieprawda
            def __ge__(self, some_set):
                self.ge_called = Prawda
                zwróć Nieprawda
            def __le__(self, some_set):
                self.le_called = Prawda
                zwróć Nieprawda

        # This first tries the builtin rich set comparison, which doesn't know
        # how to handle the custom object. Upon returning NotImplemented, the
        # corresponding comparison on the right object jest invoked.
        myset = {1, 2, 3}

        myobj = TestRichSetCompare()
        myset < myobj
        self.assertPrawda(myobj.gt_called)

        myobj = TestRichSetCompare()
        myset > myobj
        self.assertPrawda(myobj.lt_called)

        myobj = TestRichSetCompare()
        myset <= myobj
        self.assertPrawda(myobj.ge_called)

        myobj = TestRichSetCompare()
        myset >= myobj
        self.assertPrawda(myobj.le_called)

    @unittest.skipUnless(hasattr(set, "test_c_api"),
                         'C API test only available w a debug build')
    def test_c_api(self):
        self.assertEqual(set().test_c_api(), Prawda)

klasa SetSubclass(set):
    dalej

klasa TestSetSubclass(TestSet):
    thetype = SetSubclass
    basetype = set

klasa SetSubclassWithKeywordArgs(set):
    def __init__(self, iterable=[], newarg=Nic):
        set.__init__(self, iterable)

klasa TestSetSubclassWithKeywordArgs(TestSet):

    def test_keywords_in_subclass(self):
        'SF bug #1486663 -- this used to erroneously podnieś a TypeError'
        SetSubclassWithKeywordArgs(newarg=1)

klasa TestFrozenSet(TestJointOps, unittest.TestCase):
    thetype = frozenset
    basetype = frozenset

    def test_init(self):
        s = self.thetype(self.word)
        s.__init__(self.otherword)
        self.assertEqual(s, set(self.word))

    def test_singleton_empty_frozenset(self):
        f = frozenset()
        efs = [frozenset(), frozenset([]), frozenset(()), frozenset(''),
               frozenset(), frozenset([]), frozenset(()), frozenset(''),
               frozenset(range(0)), frozenset(frozenset()),
               frozenset(f), f]
        # All of the empty frozensets should have just one id()
        self.assertEqual(len(set(map(id, efs))), 1)

    def test_constructor_identity(self):
        s = self.thetype(range(3))
        t = self.thetype(s)
        self.assertEqual(id(s), id(t))

    def test_hash(self):
        self.assertEqual(hash(self.thetype('abcdeb')),
                         hash(self.thetype('ebecda')))

        # make sure that all permutations give the same hash value
        n = 100
        seq = [randrange(n) dla i w range(n)]
        results = set()
        dla i w range(200):
            shuffle(seq)
            results.add(hash(self.thetype(seq)))
        self.assertEqual(len(results), 1)

    def test_copy(self):
        dup = self.s.copy()
        self.assertEqual(id(self.s), id(dup))

    def test_frozen_as_dictkey(self):
        seq = list(range(10)) + list('abcdefg') + ['apple']
        key1 = self.thetype(seq)
        key2 = self.thetype(reversed(seq))
        self.assertEqual(key1, key2)
        self.assertNotEqual(id(key1), id(key2))
        d = {}
        d[key1] = 42
        self.assertEqual(d[key2], 42)

    def test_hash_caching(self):
        f = self.thetype('abcdcda')
        self.assertEqual(hash(f), hash(f))

    def test_hash_effectiveness(self):
        n = 13
        hashvalues = set()
        addhashvalue = hashvalues.add
        elemmasks = [(i+1, 1<<i) dla i w range(n)]
        dla i w range(2**n):
            addhashvalue(hash(frozenset([e dla e, m w elemmasks jeżeli m&i])))
        self.assertEqual(len(hashvalues), 2**n)

klasa FrozenSetSubclass(frozenset):
    dalej

klasa TestFrozenSetSubclass(TestFrozenSet):
    thetype = FrozenSetSubclass
    basetype = frozenset

    def test_constructor_identity(self):
        s = self.thetype(range(3))
        t = self.thetype(s)
        self.assertNotEqual(id(s), id(t))

    def test_copy(self):
        dup = self.s.copy()
        self.assertNotEqual(id(self.s), id(dup))

    def test_nested_empty_constructor(self):
        s = self.thetype()
        t = self.thetype(s)
        self.assertEqual(s, t)

    def test_singleton_empty_frozenset(self):
        Frozenset = self.thetype
        f = frozenset()
        F = Frozenset()
        efs = [Frozenset(), Frozenset([]), Frozenset(()), Frozenset(''),
               Frozenset(), Frozenset([]), Frozenset(()), Frozenset(''),
               Frozenset(range(0)), Frozenset(Frozenset()),
               Frozenset(frozenset()), f, F, Frozenset(f), Frozenset(F)]
        # All empty frozenset subclass instances should have different ids
        self.assertEqual(len(set(map(id, efs))), len(efs))

# Tests taken z test_sets.py =============================================

empty_set = set()

#==============================================================================

klasa TestBasicOps:

    def test_repr(self):
        jeżeli self.repr jest nie Nic:
            self.assertEqual(repr(self.set), self.repr)

    def check_repr_against_values(self):
        text = repr(self.set)
        self.assertPrawda(text.startswith('{'))
        self.assertPrawda(text.endswith('}'))

        result = text[1:-1].split(', ')
        result.sort()
        sorted_repr_values = [repr(value) dla value w self.values]
        sorted_repr_values.sort()
        self.assertEqual(result, sorted_repr_values)

    def test_print(self):
        spróbuj:
            fo = open(support.TESTFN, "w")
            fo.write(str(self.set))
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(self.set))
        w_końcu:
            fo.close()
            support.unlink(support.TESTFN)

    def test_length(self):
        self.assertEqual(len(self.set), self.length)

    def test_self_equality(self):
        self.assertEqual(self.set, self.set)

    def test_equivalent_equality(self):
        self.assertEqual(self.set, self.dup)

    def test_copy(self):
        self.assertEqual(self.set.copy(), self.dup)

    def test_self_union(self):
        result = self.set | self.set
        self.assertEqual(result, self.dup)

    def test_empty_union(self):
        result = self.set | empty_set
        self.assertEqual(result, self.dup)

    def test_union_empty(self):
        result = empty_set | self.set
        self.assertEqual(result, self.dup)

    def test_self_intersection(self):
        result = self.set & self.set
        self.assertEqual(result, self.dup)

    def test_empty_intersection(self):
        result = self.set & empty_set
        self.assertEqual(result, empty_set)

    def test_intersection_empty(self):
        result = empty_set & self.set
        self.assertEqual(result, empty_set)

    def test_self_isdisjoint(self):
        result = self.set.isdisjoint(self.set)
        self.assertEqual(result, nie self.set)

    def test_empty_isdisjoint(self):
        result = self.set.isdisjoint(empty_set)
        self.assertEqual(result, Prawda)

    def test_isdisjoint_empty(self):
        result = empty_set.isdisjoint(self.set)
        self.assertEqual(result, Prawda)

    def test_self_symmetric_difference(self):
        result = self.set ^ self.set
        self.assertEqual(result, empty_set)

    def test_empty_symmetric_difference(self):
        result = self.set ^ empty_set
        self.assertEqual(result, self.set)

    def test_self_difference(self):
        result = self.set - self.set
        self.assertEqual(result, empty_set)

    def test_empty_difference(self):
        result = self.set - empty_set
        self.assertEqual(result, self.dup)

    def test_empty_difference_rev(self):
        result = empty_set - self.set
        self.assertEqual(result, empty_set)

    def test_iteration(self):
        dla v w self.set:
            self.assertIn(v, self.values)
        setiter = iter(self.set)
        self.assertEqual(setiter.__length_hint__(), len(self.set))

    def test_pickling(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(self.set, proto)
            copy = pickle.loads(p)
            self.assertEqual(self.set, copy,
                             "%s != %s" % (self.set, copy))

#------------------------------------------------------------------------------

klasa TestBasicOpsEmpty(TestBasicOps, unittest.TestCase):
    def setUp(self):
        self.case   = "empty set"
        self.values = []
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 0
        self.repr   = "set()"

#------------------------------------------------------------------------------

klasa TestBasicOpsSingleton(TestBasicOps, unittest.TestCase):
    def setUp(self):
        self.case   = "unit set (number)"
        self.values = [3]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 1
        self.repr   = "{3}"

    def test_in(self):
        self.assertIn(3, self.set)

    def test_not_in(self):
        self.assertNotIn(2, self.set)

#------------------------------------------------------------------------------

klasa TestBasicOpsTuple(TestBasicOps, unittest.TestCase):
    def setUp(self):
        self.case   = "unit set (tuple)"
        self.values = [(0, "zero")]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 1
        self.repr   = "{(0, 'zero')}"

    def test_in(self):
        self.assertIn((0, "zero"), self.set)

    def test_not_in(self):
        self.assertNotIn(9, self.set)

#------------------------------------------------------------------------------

klasa TestBasicOpsTriple(TestBasicOps, unittest.TestCase):
    def setUp(self):
        self.case   = "triple set"
        self.values = [0, "zero", operator.add]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 3
        self.repr   = Nic

#------------------------------------------------------------------------------

klasa TestBasicOpsString(TestBasicOps, unittest.TestCase):
    def setUp(self):
        self.case   = "string set"
        self.values = ["a", "b", "c"]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 3

    def test_repr(self):
        self.check_repr_against_values()

#------------------------------------------------------------------------------

klasa TestBasicOpsBytes(TestBasicOps, unittest.TestCase):
    def setUp(self):
        self.case   = "bytes set"
        self.values = [b"a", b"b", b"c"]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 3

    def test_repr(self):
        self.check_repr_against_values()

#------------------------------------------------------------------------------

klasa TestBasicOpsMixedStringBytes(TestBasicOps, unittest.TestCase):
    def setUp(self):
        self._warning_filters = support.check_warnings()
        self._warning_filters.__enter__()
        warnings.simplefilter('ignore', BytesWarning)
        self.case   = "string oraz bytes set"
        self.values = ["a", "b", b"a", b"b"]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 4

    def tearDown(self):
        self._warning_filters.__exit__(Nic, Nic, Nic)

    def test_repr(self):
        self.check_repr_against_values()

#==============================================================================

def baditer():
    podnieś TypeError
    uzyskaj Prawda

def gooditer():
    uzyskaj Prawda

klasa TestExceptionPropagation(unittest.TestCase):
    """SF 628246:  Set constructor should nie trap iterator TypeErrors"""

    def test_instanceWithException(self):
        self.assertRaises(TypeError, set, baditer())

    def test_instancesWithoutException(self):
        # All of these iterables should load without exception.
        set([1,2,3])
        set((1,2,3))
        set({'one':1, 'two':2, 'three':3})
        set(range(3))
        set('abc')
        set(gooditer())

    def test_changingSizeWhileIterating(self):
        s = set([1,2,3])
        spróbuj:
            dla i w s:
                s.update([4])
        wyjąwszy RuntimeError:
            dalej
        inaczej:
            self.fail("no exception when changing size during iteration")

#==============================================================================

klasa TestSetOfSets(unittest.TestCase):
    def test_constructor(self):
        inner = frozenset([1])
        outer = set([inner])
        element = outer.pop()
        self.assertEqual(type(element), frozenset)
        outer.add(inner)        # Rebuild set of sets przy .add method
        outer.remove(inner)
        self.assertEqual(outer, set())   # Verify that remove worked
        outer.discard(inner)    # Absence of KeyError indicates working fine

#==============================================================================

klasa TestBinaryOps(unittest.TestCase):
    def setUp(self):
        self.set = set((2, 4, 6))

    def test_eq(self):              # SF bug 643115
        self.assertEqual(self.set, set({2:1,4:3,6:5}))

    def test_union_subset(self):
        result = self.set | set([2])
        self.assertEqual(result, set((2, 4, 6)))

    def test_union_superset(self):
        result = self.set | set([2, 4, 6, 8])
        self.assertEqual(result, set([2, 4, 6, 8]))

    def test_union_overlap(self):
        result = self.set | set([3, 4, 5])
        self.assertEqual(result, set([2, 3, 4, 5, 6]))

    def test_union_non_overlap(self):
        result = self.set | set([8])
        self.assertEqual(result, set([2, 4, 6, 8]))

    def test_intersection_subset(self):
        result = self.set & set((2, 4))
        self.assertEqual(result, set((2, 4)))

    def test_intersection_superset(self):
        result = self.set & set([2, 4, 6, 8])
        self.assertEqual(result, set([2, 4, 6]))

    def test_intersection_overlap(self):
        result = self.set & set([3, 4, 5])
        self.assertEqual(result, set([4]))

    def test_intersection_non_overlap(self):
        result = self.set & set([8])
        self.assertEqual(result, empty_set)

    def test_isdisjoint_subset(self):
        result = self.set.isdisjoint(set((2, 4)))
        self.assertEqual(result, Nieprawda)

    def test_isdisjoint_superset(self):
        result = self.set.isdisjoint(set([2, 4, 6, 8]))
        self.assertEqual(result, Nieprawda)

    def test_isdisjoint_overlap(self):
        result = self.set.isdisjoint(set([3, 4, 5]))
        self.assertEqual(result, Nieprawda)

    def test_isdisjoint_non_overlap(self):
        result = self.set.isdisjoint(set([8]))
        self.assertEqual(result, Prawda)

    def test_sym_difference_subset(self):
        result = self.set ^ set((2, 4))
        self.assertEqual(result, set([6]))

    def test_sym_difference_superset(self):
        result = self.set ^ set((2, 4, 6, 8))
        self.assertEqual(result, set([8]))

    def test_sym_difference_overlap(self):
        result = self.set ^ set((3, 4, 5))
        self.assertEqual(result, set([2, 3, 5, 6]))

    def test_sym_difference_non_overlap(self):
        result = self.set ^ set([8])
        self.assertEqual(result, set([2, 4, 6, 8]))

#==============================================================================

klasa TestUpdateOps(unittest.TestCase):
    def setUp(self):
        self.set = set((2, 4, 6))

    def test_union_subset(self):
        self.set |= set([2])
        self.assertEqual(self.set, set((2, 4, 6)))

    def test_union_superset(self):
        self.set |= set([2, 4, 6, 8])
        self.assertEqual(self.set, set([2, 4, 6, 8]))

    def test_union_overlap(self):
        self.set |= set([3, 4, 5])
        self.assertEqual(self.set, set([2, 3, 4, 5, 6]))

    def test_union_non_overlap(self):
        self.set |= set([8])
        self.assertEqual(self.set, set([2, 4, 6, 8]))

    def test_union_method_call(self):
        self.set.update(set([3, 4, 5]))
        self.assertEqual(self.set, set([2, 3, 4, 5, 6]))

    def test_intersection_subset(self):
        self.set &= set((2, 4))
        self.assertEqual(self.set, set((2, 4)))

    def test_intersection_superset(self):
        self.set &= set([2, 4, 6, 8])
        self.assertEqual(self.set, set([2, 4, 6]))

    def test_intersection_overlap(self):
        self.set &= set([3, 4, 5])
        self.assertEqual(self.set, set([4]))

    def test_intersection_non_overlap(self):
        self.set &= set([8])
        self.assertEqual(self.set, empty_set)

    def test_intersection_method_call(self):
        self.set.intersection_update(set([3, 4, 5]))
        self.assertEqual(self.set, set([4]))

    def test_sym_difference_subset(self):
        self.set ^= set((2, 4))
        self.assertEqual(self.set, set([6]))

    def test_sym_difference_superset(self):
        self.set ^= set((2, 4, 6, 8))
        self.assertEqual(self.set, set([8]))

    def test_sym_difference_overlap(self):
        self.set ^= set((3, 4, 5))
        self.assertEqual(self.set, set([2, 3, 5, 6]))

    def test_sym_difference_non_overlap(self):
        self.set ^= set([8])
        self.assertEqual(self.set, set([2, 4, 6, 8]))

    def test_sym_difference_method_call(self):
        self.set.symmetric_difference_update(set([3, 4, 5]))
        self.assertEqual(self.set, set([2, 3, 5, 6]))

    def test_difference_subset(self):
        self.set -= set((2, 4))
        self.assertEqual(self.set, set([6]))

    def test_difference_superset(self):
        self.set -= set((2, 4, 6, 8))
        self.assertEqual(self.set, set([]))

    def test_difference_overlap(self):
        self.set -= set((3, 4, 5))
        self.assertEqual(self.set, set([2, 6]))

    def test_difference_non_overlap(self):
        self.set -= set([8])
        self.assertEqual(self.set, set([2, 4, 6]))

    def test_difference_method_call(self):
        self.set.difference_update(set([3, 4, 5]))
        self.assertEqual(self.set, set([2, 6]))

#==============================================================================

klasa TestMutate(unittest.TestCase):
    def setUp(self):
        self.values = ["a", "b", "c"]
        self.set = set(self.values)

    def test_add_present(self):
        self.set.add("c")
        self.assertEqual(self.set, set("abc"))

    def test_add_absent(self):
        self.set.add("d")
        self.assertEqual(self.set, set("abcd"))

    def test_add_until_full(self):
        tmp = set()
        expected_len = 0
        dla v w self.values:
            tmp.add(v)
            expected_len += 1
            self.assertEqual(len(tmp), expected_len)
        self.assertEqual(tmp, self.set)

    def test_remove_present(self):
        self.set.remove("b")
        self.assertEqual(self.set, set("ac"))

    def test_remove_absent(self):
        spróbuj:
            self.set.remove("d")
            self.fail("Removing missing element should have podnieśd LookupError")
        wyjąwszy LookupError:
            dalej

    def test_remove_until_empty(self):
        expected_len = len(self.set)
        dla v w self.values:
            self.set.remove(v)
            expected_len -= 1
            self.assertEqual(len(self.set), expected_len)

    def test_discard_present(self):
        self.set.discard("c")
        self.assertEqual(self.set, set("ab"))

    def test_discard_absent(self):
        self.set.discard("d")
        self.assertEqual(self.set, set("abc"))

    def test_clear(self):
        self.set.clear()
        self.assertEqual(len(self.set), 0)

    def test_pop(self):
        popped = {}
        dopóki self.set:
            popped[self.set.pop()] = Nic
        self.assertEqual(len(popped), len(self.values))
        dla v w self.values:
            self.assertIn(v, popped)

    def test_update_empty_tuple(self):
        self.set.update(())
        self.assertEqual(self.set, set(self.values))

    def test_update_unit_tuple_overlap(self):
        self.set.update(("a",))
        self.assertEqual(self.set, set(self.values))

    def test_update_unit_tuple_non_overlap(self):
        self.set.update(("a", "z"))
        self.assertEqual(self.set, set(self.values + ["z"]))

#==============================================================================

klasa TestSubsets:

    case2method = {"<=": "issubset",
                   ">=": "issuperset",
                  }

    reverse = {"==": "==",
               "!=": "!=",
               "<":  ">",
               ">":  "<",
               "<=": ">=",
               ">=": "<=",
              }

    def test_issubset(self):
        x = self.left
        y = self.right
        dla case w "!=", "==", "<", "<=", ">", ">=":
            expected = case w self.cases
            # Test the binary infix spelling.
            result = eval("x" + case + "y", locals())
            self.assertEqual(result, expected)
            # Test the "friendly" method-name spelling, jeżeli one exists.
            jeżeli case w TestSubsets.case2method:
                method = getattr(x, TestSubsets.case2method[case])
                result = method(y)
                self.assertEqual(result, expected)

            # Now do the same dla the operands reversed.
            rcase = TestSubsets.reverse[case]
            result = eval("y" + rcase + "x", locals())
            self.assertEqual(result, expected)
            jeżeli rcase w TestSubsets.case2method:
                method = getattr(y, TestSubsets.case2method[rcase])
                result = method(x)
                self.assertEqual(result, expected)
#------------------------------------------------------------------------------

klasa TestSubsetEqualEmpty(TestSubsets, unittest.TestCase):
    left  = set()
    right = set()
    name  = "both empty"
    cases = "==", "<=", ">="

#------------------------------------------------------------------------------

klasa TestSubsetEqualNonEmpty(TestSubsets, unittest.TestCase):
    left  = set([1, 2])
    right = set([1, 2])
    name  = "equal pair"
    cases = "==", "<=", ">="

#------------------------------------------------------------------------------

klasa TestSubsetEmptyNonEmpty(TestSubsets, unittest.TestCase):
    left  = set()
    right = set([1, 2])
    name  = "one empty, one non-empty"
    cases = "!=", "<", "<="

#------------------------------------------------------------------------------

klasa TestSubsetPartial(TestSubsets, unittest.TestCase):
    left  = set([1])
    right = set([1, 2])
    name  = "one a non-empty proper subset of other"
    cases = "!=", "<", "<="

#------------------------------------------------------------------------------

klasa TestSubsetNonOverlap(TestSubsets, unittest.TestCase):
    left  = set([1])
    right = set([2])
    name  = "neither empty, neither contains"
    cases = "!="

#==============================================================================

klasa TestOnlySetsInBinaryOps:

    def test_eq_ne(self):
        # Unlike the others, this jest testing that == oraz != *are* allowed.
        self.assertEqual(self.other == self.set, Nieprawda)
        self.assertEqual(self.set == self.other, Nieprawda)
        self.assertEqual(self.other != self.set, Prawda)
        self.assertEqual(self.set != self.other, Prawda)

    def test_ge_gt_le_lt(self):
        self.assertRaises(TypeError, lambda: self.set < self.other)
        self.assertRaises(TypeError, lambda: self.set <= self.other)
        self.assertRaises(TypeError, lambda: self.set > self.other)
        self.assertRaises(TypeError, lambda: self.set >= self.other)

        self.assertRaises(TypeError, lambda: self.other < self.set)
        self.assertRaises(TypeError, lambda: self.other <= self.set)
        self.assertRaises(TypeError, lambda: self.other > self.set)
        self.assertRaises(TypeError, lambda: self.other >= self.set)

    def test_update_operator(self):
        spróbuj:
            self.set |= self.other
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("expected TypeError")

    def test_update(self):
        jeżeli self.otherIsIterable:
            self.set.update(self.other)
        inaczej:
            self.assertRaises(TypeError, self.set.update, self.other)

    def test_union(self):
        self.assertRaises(TypeError, lambda: self.set | self.other)
        self.assertRaises(TypeError, lambda: self.other | self.set)
        jeżeli self.otherIsIterable:
            self.set.union(self.other)
        inaczej:
            self.assertRaises(TypeError, self.set.union, self.other)

    def test_intersection_update_operator(self):
        spróbuj:
            self.set &= self.other
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("expected TypeError")

    def test_intersection_update(self):
        jeżeli self.otherIsIterable:
            self.set.intersection_update(self.other)
        inaczej:
            self.assertRaises(TypeError,
                              self.set.intersection_update,
                              self.other)

    def test_intersection(self):
        self.assertRaises(TypeError, lambda: self.set & self.other)
        self.assertRaises(TypeError, lambda: self.other & self.set)
        jeżeli self.otherIsIterable:
            self.set.intersection(self.other)
        inaczej:
            self.assertRaises(TypeError, self.set.intersection, self.other)

    def test_sym_difference_update_operator(self):
        spróbuj:
            self.set ^= self.other
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("expected TypeError")

    def test_sym_difference_update(self):
        jeżeli self.otherIsIterable:
            self.set.symmetric_difference_update(self.other)
        inaczej:
            self.assertRaises(TypeError,
                              self.set.symmetric_difference_update,
                              self.other)

    def test_sym_difference(self):
        self.assertRaises(TypeError, lambda: self.set ^ self.other)
        self.assertRaises(TypeError, lambda: self.other ^ self.set)
        jeżeli self.otherIsIterable:
            self.set.symmetric_difference(self.other)
        inaczej:
            self.assertRaises(TypeError, self.set.symmetric_difference, self.other)

    def test_difference_update_operator(self):
        spróbuj:
            self.set -= self.other
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("expected TypeError")

    def test_difference_update(self):
        jeżeli self.otherIsIterable:
            self.set.difference_update(self.other)
        inaczej:
            self.assertRaises(TypeError,
                              self.set.difference_update,
                              self.other)

    def test_difference(self):
        self.assertRaises(TypeError, lambda: self.set - self.other)
        self.assertRaises(TypeError, lambda: self.other - self.set)
        jeżeli self.otherIsIterable:
            self.set.difference(self.other)
        inaczej:
            self.assertRaises(TypeError, self.set.difference, self.other)

#------------------------------------------------------------------------------

klasa TestOnlySetsNumeric(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = 19
        self.otherIsIterable = Nieprawda

#------------------------------------------------------------------------------

klasa TestOnlySetsDict(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = {1:2, 3:4}
        self.otherIsIterable = Prawda

#------------------------------------------------------------------------------

klasa TestOnlySetsOperator(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = operator.add
        self.otherIsIterable = Nieprawda

#------------------------------------------------------------------------------

klasa TestOnlySetsTuple(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = (2, 4, 6)
        self.otherIsIterable = Prawda

#------------------------------------------------------------------------------

klasa TestOnlySetsString(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        self.set   = set((1, 2, 3))
        self.other = 'abc'
        self.otherIsIterable = Prawda

#------------------------------------------------------------------------------

klasa TestOnlySetsGenerator(TestOnlySetsInBinaryOps, unittest.TestCase):
    def setUp(self):
        def gen():
            dla i w range(0, 10, 2):
                uzyskaj i
        self.set   = set((1, 2, 3))
        self.other = gen()
        self.otherIsIterable = Prawda

#==============================================================================

klasa TestCopying:

    def test_copy(self):
        dup = self.set.copy()
        dup_list = sorted(dup, key=repr)
        set_list = sorted(self.set, key=repr)
        self.assertEqual(len(dup_list), len(set_list))
        dla i w range(len(dup_list)):
            self.assertPrawda(dup_list[i] jest set_list[i])

    def test_deep_copy(self):
        dup = copy.deepcopy(self.set)
        ##print type(dup), repr(dup)
        dup_list = sorted(dup, key=repr)
        set_list = sorted(self.set, key=repr)
        self.assertEqual(len(dup_list), len(set_list))
        dla i w range(len(dup_list)):
            self.assertEqual(dup_list[i], set_list[i])

#------------------------------------------------------------------------------

klasa TestCopyingEmpty(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set()

#------------------------------------------------------------------------------

klasa TestCopyingSingleton(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set(["hello"])

#------------------------------------------------------------------------------

klasa TestCopyingTriple(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set(["zero", 0, Nic])

#------------------------------------------------------------------------------

klasa TestCopyingTuple(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set([(1, 2)])

#------------------------------------------------------------------------------

klasa TestCopyingNested(TestCopying, unittest.TestCase):
    def setUp(self):
        self.set = set([((1, 2), (3, 4))])

#==============================================================================

klasa TestIdentities(unittest.TestCase):
    def setUp(self):
        self.a = set('abracadabra')
        self.b = set('alacazam')

    def test_binopsVsSubsets(self):
        a, b = self.a, self.b
        self.assertPrawda(a - b < a)
        self.assertPrawda(b - a < b)
        self.assertPrawda(a & b < a)
        self.assertPrawda(a & b < b)
        self.assertPrawda(a | b > a)
        self.assertPrawda(a | b > b)
        self.assertPrawda(a ^ b < a | b)

    def test_commutativity(self):
        a, b = self.a, self.b
        self.assertEqual(a&b, b&a)
        self.assertEqual(a|b, b|a)
        self.assertEqual(a^b, b^a)
        jeżeli a != b:
            self.assertNotEqual(a-b, b-a)

    def test_summations(self):
        # check that sums of parts equal the whole
        a, b = self.a, self.b
        self.assertEqual((a-b)|(a&b)|(b-a), a|b)
        self.assertEqual((a&b)|(a^b), a|b)
        self.assertEqual(a|(b-a), a|b)
        self.assertEqual((a-b)|b, a|b)
        self.assertEqual((a-b)|(a&b), a)
        self.assertEqual((b-a)|(a&b), b)
        self.assertEqual((a-b)|(b-a), a^b)

    def test_exclusion(self):
        # check that inverse operations show non-overlap
        a, b, zero = self.a, self.b, set()
        self.assertEqual((a-b)&b, zero)
        self.assertEqual((b-a)&a, zero)
        self.assertEqual((a&b)&(a^b), zero)

# Tests derived z test_itertools.py =======================================

def R(seqn):
    'Regular generator'
    dla i w seqn:
        uzyskaj i

klasa G:
    'Sequence using __getitem__'
    def __init__(self, seqn):
        self.seqn = seqn
    def __getitem__(self, i):
        zwróć self.seqn[i]

klasa I:
    'Sequence using iterator protocol'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        zwróć self
    def __next__(self):
        jeżeli self.i >= len(self.seqn): podnieś StopIteration
        v = self.seqn[self.i]
        self.i += 1
        zwróć v

klasa Ig:
    'Sequence using iterator protocol defined przy a generator'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        dla val w self.seqn:
            uzyskaj val

klasa X:
    'Missing __getitem__ oraz __iter__'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __next__(self):
        jeżeli self.i >= len(self.seqn): podnieś StopIteration
        v = self.seqn[self.i]
        self.i += 1
        zwróć v

klasa N:
    'Iterator missing __next__()'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        zwróć self

klasa E:
    'Test propagation of exceptions'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        zwróć self
    def __next__(self):
        3 // 0

klasa S:
    'Test immediate stop'
    def __init__(self, seqn):
        dalej
    def __iter__(self):
        zwróć self
    def __next__(self):
        podnieś StopIteration

z itertools zaimportuj chain
def L(seqn):
    'Test multiple tiers of iterators'
    zwróć chain(map(lambda x:x, R(Ig(G(seqn)))))

klasa TestVariousIteratorArgs(unittest.TestCase):

    def test_constructor(self):
        dla cons w (set, frozenset):
            dla s w ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
                dla g w (G, I, Ig, S, L, R):
                    self.assertEqual(sorted(cons(g(s)), key=repr), sorted(g(s), key=repr))
                self.assertRaises(TypeError, cons , X(s))
                self.assertRaises(TypeError, cons , N(s))
                self.assertRaises(ZeroDivisionError, cons , E(s))

    def test_inline_methods(self):
        s = set('november')
        dla data w ("123", "", range(1000), ('do', 1.2), range(2000,2200,5), 'december'):
            dla meth w (s.union, s.intersection, s.difference, s.symmetric_difference, s.isdisjoint):
                dla g w (G, I, Ig, L, R):
                    expected = meth(data)
                    actual = meth(g(data))
                    jeżeli isinstance(expected, bool):
                        self.assertEqual(actual, expected)
                    inaczej:
                        self.assertEqual(sorted(actual, key=repr), sorted(expected, key=repr))
                self.assertRaises(TypeError, meth, X(s))
                self.assertRaises(TypeError, meth, N(s))
                self.assertRaises(ZeroDivisionError, meth, E(s))

    def test_inplace_methods(self):
        dla data w ("123", "", range(1000), ('do', 1.2), range(2000,2200,5), 'december'):
            dla methname w ('update', 'intersection_update',
                             'difference_update', 'symmetric_difference_update'):
                dla g w (G, I, Ig, S, L, R):
                    s = set('january')
                    t = s.copy()
                    getattr(s, methname)(list(g(data)))
                    getattr(t, methname)(g(data))
                    self.assertEqual(sorted(s, key=repr), sorted(t, key=repr))

                self.assertRaises(TypeError, getattr(set('january'), methname), X(data))
                self.assertRaises(TypeError, getattr(set('january'), methname), N(data))
                self.assertRaises(ZeroDivisionError, getattr(set('january'), methname), E(data))

klasa bad_eq:
    def __eq__(self, other):
        jeżeli be_bad:
            set2.clear()
            podnieś ZeroDivisionError
        zwróć self jest other
    def __hash__(self):
        zwróć 0

klasa bad_dict_clear:
    def __eq__(self, other):
        jeżeli be_bad:
            dict2.clear()
        zwróć self jest other
    def __hash__(self):
        zwróć 0

klasa TestWeirdBugs(unittest.TestCase):
    def test_8420_set_merge(self):
        # This used to segfault
        global be_bad, set2, dict2
        be_bad = Nieprawda
        set1 = {bad_eq()}
        set2 = {bad_eq() dla i w range(75)}
        be_bad = Prawda
        self.assertRaises(ZeroDivisionError, set1.update, set2)

        be_bad = Nieprawda
        set1 = {bad_dict_clear()}
        dict2 = {bad_dict_clear(): Nic}
        be_bad = Prawda
        set1.symmetric_difference_update(dict2)

    def test_iter_and_mutate(self):
        # Issue #24581
        s = set(range(100))
        s.clear()
        s.update(range(100))
        si = iter(s)
        s.clear()
        a = list(range(100))
        s.update(range(100))
        list(si)

    def test_merge_and_mutate(self):
        klasa X:
            def __hash__(self):
                zwróć hash(0)
            def __eq__(self, o):
                other.clear()
                zwróć Nieprawda

        other = set()
        other = {X() dla i w range(10)}
        s = {0}
        s.update(other)

# Application tests (based on David Eppstein's graph recipes ====================================

def powerset(U):
    """Generates all subsets of a set albo sequence U."""
    U = iter(U)
    spróbuj:
        x = frozenset([next(U)])
        dla S w powerset(U):
            uzyskaj S
            uzyskaj S | x
    wyjąwszy StopIteration:
        uzyskaj frozenset()

def cube(n):
    """Graph of n-dimensional hypercube."""
    singletons = [frozenset([x]) dla x w range(n)]
    zwróć dict([(x, frozenset([x^s dla s w singletons]))
                 dla x w powerset(range(n))])

def linegraph(G):
    """Graph, the vertices of which are edges of G,
    przy two vertices being adjacent iff the corresponding
    edges share a vertex."""
    L = {}
    dla x w G:
        dla y w G[x]:
            nx = [frozenset([x,z]) dla z w G[x] jeżeli z != y]
            ny = [frozenset([y,z]) dla z w G[y] jeżeli z != x]
            L[frozenset([x,y])] = frozenset(nx+ny)
    zwróć L

def faces(G):
    'Return a set of faces w G.  Where a face jest a set of vertices on that face'
    # currently limited to triangles,squares, oraz pentagons
    f = set()
    dla v1, edges w G.items():
        dla v2 w edges:
            dla v3 w G[v2]:
                jeżeli v1 == v3:
                    kontynuuj
                jeżeli v1 w G[v3]:
                    f.add(frozenset([v1, v2, v3]))
                inaczej:
                    dla v4 w G[v3]:
                        jeżeli v4 == v2:
                            kontynuuj
                        jeżeli v1 w G[v4]:
                            f.add(frozenset([v1, v2, v3, v4]))
                        inaczej:
                            dla v5 w G[v4]:
                                jeżeli v5 == v3 albo v5 == v2:
                                    kontynuuj
                                jeżeli v1 w G[v5]:
                                    f.add(frozenset([v1, v2, v3, v4, v5]))
    zwróć f


klasa TestGraphs(unittest.TestCase):

    def test_cube(self):

        g = cube(3)                             # vert --> {v1, v2, v3}
        vertices1 = set(g)
        self.assertEqual(len(vertices1), 8)     # eight vertices
        dla edge w g.values():
            self.assertEqual(len(edge), 3)      # each vertex connects to three edges
        vertices2 = set(v dla edges w g.values() dla v w edges)
        self.assertEqual(vertices1, vertices2)  # edge vertices w original set

        cubefaces = faces(g)
        self.assertEqual(len(cubefaces), 6)     # six faces
        dla face w cubefaces:
            self.assertEqual(len(face), 4)      # each face jest a square

    def test_cuboctahedron(self):

        # http://en.wikipedia.org/wiki/Cuboctahedron
        # 8 triangular faces oraz 6 square faces
        # 12 indentical vertices each connecting a triangle oraz square

        g = cube(3)
        cuboctahedron = linegraph(g)            # V( --> {V1, V2, V3, V4}
        self.assertEqual(len(cuboctahedron), 12)# twelve vertices

        vertices = set(cuboctahedron)
        dla edges w cuboctahedron.values():
            self.assertEqual(len(edges), 4)     # each vertex connects to four other vertices
        othervertices = set(edge dla edges w cuboctahedron.values() dla edge w edges)
        self.assertEqual(vertices, othervertices)   # edge vertices w original set

        cubofaces = faces(cuboctahedron)
        facesizes = collections.defaultdict(int)
        dla face w cubofaces:
            facesizes[len(face)] += 1
        self.assertEqual(facesizes[3], 8)       # eight triangular faces
        self.assertEqual(facesizes[4], 6)       # six square faces

        dla vertex w cuboctahedron:
            edge = vertex                       # Cuboctahedron vertices are edges w Cube
            self.assertEqual(len(edge), 2)      # Two cube vertices define an edge
            dla cubevert w edge:
                self.assertIn(cubevert, g)


#==============================================================================

jeżeli __name__ == "__main__":
    unittest.main()
