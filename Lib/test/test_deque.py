z collections zaimportuj deque
zaimportuj unittest
z test zaimportuj support, seq_tests
zaimportuj gc
zaimportuj weakref
zaimportuj copy
zaimportuj pickle
z io zaimportuj StringIO
zaimportuj random
zaimportuj struct

BIG = 100000

def fail():
    podnieś SyntaxError
    uzyskaj 1

klasa BadCmp:
    def __eq__(self, other):
        podnieś RuntimeError

klasa MutateCmp:
    def __init__(self, deque, result):
        self.deque = deque
        self.result = result
    def __eq__(self, other):
        self.deque.clear()
        zwróć self.result

klasa TestBasic(unittest.TestCase):

    def test_basics(self):
        d = deque(range(-5125, -5000))
        d.__init__(range(200))
        dla i w range(200, 400):
            d.append(i)
        dla i w reversed(range(-200, 0)):
            d.appendleft(i)
        self.assertEqual(list(d), list(range(-200, 400)))
        self.assertEqual(len(d), 600)

        left = [d.popleft() dla i w range(250)]
        self.assertEqual(left, list(range(-200, 50)))
        self.assertEqual(list(d), list(range(50, 400)))

        right = [d.pop() dla i w range(250)]
        right.reverse()
        self.assertEqual(right, list(range(150, 400)))
        self.assertEqual(list(d), list(range(50, 150)))

    def test_maxlen(self):
        self.assertRaises(ValueError, deque, 'abc', -1)
        self.assertRaises(ValueError, deque, 'abc', -2)
        it = iter(range(10))
        d = deque(it, maxlen=3)
        self.assertEqual(list(it), [])
        self.assertEqual(repr(d), 'deque([7, 8, 9], maxlen=3)')
        self.assertEqual(list(d), [7, 8, 9])
        self.assertEqual(d, deque(range(10), 3))
        d.append(10)
        self.assertEqual(list(d), [8, 9, 10])
        d.appendleft(7)
        self.assertEqual(list(d), [7, 8, 9])
        d.extend([10, 11])
        self.assertEqual(list(d), [9, 10, 11])
        d.extendleft([8, 7])
        self.assertEqual(list(d), [7, 8, 9])
        d = deque(range(200), maxlen=10)
        d.append(d)
        support.unlink(support.TESTFN)
        fo = open(support.TESTFN, "w")
        spróbuj:
            fo.write(str(d))
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(d))
        w_końcu:
            fo.close()
            support.unlink(support.TESTFN)

        d = deque(range(10), maxlen=Nic)
        self.assertEqual(repr(d), 'deque([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])')
        fo = open(support.TESTFN, "w")
        spróbuj:
            fo.write(str(d))
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(d))
        w_końcu:
            fo.close()
            support.unlink(support.TESTFN)

    def test_maxlen_zero(self):
        it = iter(range(100))
        deque(it, maxlen=0)
        self.assertEqual(list(it), [])

        it = iter(range(100))
        d = deque(maxlen=0)
        d.extend(it)
        self.assertEqual(list(it), [])

        it = iter(range(100))
        d = deque(maxlen=0)
        d.extendleft(it)
        self.assertEqual(list(it), [])

    def test_maxlen_attribute(self):
        self.assertEqual(deque().maxlen, Nic)
        self.assertEqual(deque('abc').maxlen, Nic)
        self.assertEqual(deque('abc', maxlen=4).maxlen, 4)
        self.assertEqual(deque('abc', maxlen=2).maxlen, 2)
        self.assertEqual(deque('abc', maxlen=0).maxlen, 0)
        przy self.assertRaises(AttributeError):
            d = deque('abc')
            d.maxlen = 10

    def test_count(self):
        dla s w ('', 'abracadabra', 'simsalabim'*500+'abc'):
            s = list(s)
            d = deque(s)
            dla letter w 'abcdefghijklmnopqrstuvwxyz':
                self.assertEqual(s.count(letter), d.count(letter), (s, d, letter))
        self.assertRaises(TypeError, d.count)       # too few args
        self.assertRaises(TypeError, d.count, 1, 2) # too many args
        klasa BadCompare:
            def __eq__(self, other):
                podnieś ArithmeticError
        d = deque([1, 2, BadCompare(), 3])
        self.assertRaises(ArithmeticError, d.count, 2)
        d = deque([1, 2, 3])
        self.assertRaises(ArithmeticError, d.count, BadCompare())
        klasa MutatingCompare:
            def __eq__(self, other):
                self.d.pop()
                zwróć Prawda
        m = MutatingCompare()
        d = deque([1, 2, 3, m, 4, 5])
        m.d = d
        self.assertRaises(RuntimeError, d.count, 3)

        # test issue11004
        # block advance failed after rotation aligned elements on right side of block
        d = deque([Nic]*16)
        dla i w range(len(d)):
            d.rotate(-1)
        d.rotate(1)
        self.assertEqual(d.count(1), 0)
        self.assertEqual(d.count(Nic), 16)

    def test_comparisons(self):
        d = deque('xabc'); d.popleft()
        dla e w [d, deque('abc'), deque('ab'), deque(), list(d)]:
            self.assertEqual(d==e, type(d)==type(e) oraz list(d)==list(e))
            self.assertEqual(d!=e, not(type(d)==type(e) oraz list(d)==list(e)))

        args = map(deque, ('', 'a', 'b', 'ab', 'ba', 'abc', 'xba', 'xabc', 'cba'))
        dla x w args:
            dla y w args:
                self.assertEqual(x == y, list(x) == list(y), (x,y))
                self.assertEqual(x != y, list(x) != list(y), (x,y))
                self.assertEqual(x <  y, list(x) <  list(y), (x,y))
                self.assertEqual(x <= y, list(x) <= list(y), (x,y))
                self.assertEqual(x >  y, list(x) >  list(y), (x,y))
                self.assertEqual(x >= y, list(x) >= list(y), (x,y))

    def test_contains(self):
        n = 200

        d = deque(range(n))
        dla i w range(n):
            self.assertPrawda(i w d)
        self.assertPrawda((n+1) nie w d)

        # Test detection of mutation during iteration
        d = deque(range(n))
        d[n//2] = MutateCmp(d, Nieprawda)
        przy self.assertRaises(RuntimeError):
            n w d

        # Test detection of comparison exceptions
        d = deque(range(n))
        d[n//2] = BadCmp()
        przy self.assertRaises(RuntimeError):
            n w d

    def test_extend(self):
        d = deque('a')
        self.assertRaises(TypeError, d.extend, 1)
        d.extend('bcd')
        self.assertEqual(list(d), list('abcd'))
        d.extend(d)
        self.assertEqual(list(d), list('abcdabcd'))

    def test_add(self):
        d = deque()
        e = deque('abc')
        f = deque('def')
        self.assertEqual(d + d, deque())
        self.assertEqual(e + f, deque('abcdef'))
        self.assertEqual(e + e, deque('abcabc'))
        self.assertEqual(e + d, deque('abc'))
        self.assertEqual(d + e, deque('abc'))
        self.assertIsNot(d + d, deque())
        self.assertIsNot(e + d, deque('abc'))
        self.assertIsNot(d + e, deque('abc'))

        g = deque('abcdef', maxlen=4)
        h = deque('gh')
        self.assertEqual(g + h, deque('efgh'))

        przy self.assertRaises(TypeError):
            deque('abc') + 'def'

    def test_iadd(self):
        d = deque('a')
        d += 'bcd'
        self.assertEqual(list(d), list('abcd'))
        d += d
        self.assertEqual(list(d), list('abcdabcd'))

    def test_extendleft(self):
        d = deque('a')
        self.assertRaises(TypeError, d.extendleft, 1)
        d.extendleft('bcd')
        self.assertEqual(list(d), list(reversed('abcd')))
        d.extendleft(d)
        self.assertEqual(list(d), list('abcddcba'))
        d = deque()
        d.extendleft(range(1000))
        self.assertEqual(list(d), list(reversed(range(1000))))
        self.assertRaises(SyntaxError, d.extendleft, fail())

    def test_getitem(self):
        n = 200
        d = deque(range(n))
        l = list(range(n))
        dla i w range(n):
            d.popleft()
            l.pop(0)
            jeżeli random.random() < 0.5:
                d.append(i)
                l.append(i)
            dla j w range(1-len(l), len(l)):
                assert d[j] == l[j]

        d = deque('superman')
        self.assertEqual(d[0], 's')
        self.assertEqual(d[-1], 'n')
        d = deque()
        self.assertRaises(IndexError, d.__getitem__, 0)
        self.assertRaises(IndexError, d.__getitem__, -1)

    def test_index(self):
        dla n w 1, 2, 30, 40, 200:

            d = deque(range(n))
            dla i w range(n):
                self.assertEqual(d.index(i), i)

            przy self.assertRaises(ValueError):
                d.index(n+1)

            # Test detection of mutation during iteration
            d = deque(range(n))
            d[n//2] = MutateCmp(d, Nieprawda)
            przy self.assertRaises(RuntimeError):
                d.index(n)

            # Test detection of comparison exceptions
            d = deque(range(n))
            d[n//2] = BadCmp()
            przy self.assertRaises(RuntimeError):
                d.index(n)

        # Test start oraz stop arguments behavior matches list.index()
        elements = 'ABCDEFGHI'
        nonelement = 'Z'
        d = deque(elements * 2)
        s = list(elements * 2)
        dla start w range(-5 - len(s)*2, 5 + len(s) * 2):
            dla stop w range(-5 - len(s)*2, 5 + len(s) * 2):
                dla element w elements + 'Z':
                    spróbuj:
                        target = s.index(element, start, stop)
                    wyjąwszy ValueError:
                        przy self.assertRaises(ValueError):
                            d.index(element, start, stop)
                    inaczej:
                        self.assertEqual(d.index(element, start, stop), target)

    def test_insert_bug_24913(self):
        d = deque('A' * 3)
        przy self.assertRaises(ValueError):
            i = d.index("Hello world", 0, 4)

    def test_insert(self):
        # Test to make sure insert behaves like lists
        elements = 'ABCDEFGHI'
        dla i w range(-5 - len(elements)*2, 5 + len(elements) * 2):
            d = deque('ABCDEFGHI')
            s = list('ABCDEFGHI')
            d.insert(i, 'Z')
            s.insert(i, 'Z')
            self.assertEqual(list(d), s)

    def test_imul(self):
        dla n w (-10, -1, 0, 1, 2, 10, 1000):
            d = deque()
            d *= n
            self.assertEqual(d, deque())
            self.assertIsNic(d.maxlen)

        dla n w (-10, -1, 0, 1, 2, 10, 1000):
            d = deque('a')
            d *= n
            self.assertEqual(d, deque('a' * n))
            self.assertIsNic(d.maxlen)

        dla n w (-10, -1, 0, 1, 2, 10, 499, 500, 501, 1000):
            d = deque('a', 500)
            d *= n
            self.assertEqual(d, deque('a' * min(n, 500)))
            self.assertEqual(d.maxlen, 500)

        dla n w (-10, -1, 0, 1, 2, 10, 1000):
            d = deque('abcdef')
            d *= n
            self.assertEqual(d, deque('abcdef' * n))
            self.assertIsNic(d.maxlen)

        dla n w (-10, -1, 0, 1, 2, 10, 499, 500, 501, 1000):
            d = deque('abcdef', 500)
            d *= n
            self.assertEqual(d, deque(('abcdef' * n)[-500:]))
            self.assertEqual(d.maxlen, 500)

    def test_mul(self):
        d = deque('abc')
        self.assertEqual(d * -5, deque())
        self.assertEqual(d * 0, deque())
        self.assertEqual(d * 1, deque('abc'))
        self.assertEqual(d * 2, deque('abcabc'))
        self.assertEqual(d * 3, deque('abcabcabc'))
        self.assertIsNot(d * 1, d)

        self.assertEqual(deque() * 0, deque())
        self.assertEqual(deque() * 1, deque())
        self.assertEqual(deque() * 5, deque())

        self.assertEqual(-5 * d, deque())
        self.assertEqual(0 * d, deque())
        self.assertEqual(1 * d, deque('abc'))
        self.assertEqual(2 * d, deque('abcabc'))
        self.assertEqual(3 * d, deque('abcabcabc'))

        d = deque('abc', maxlen=5)
        self.assertEqual(d * -5, deque())
        self.assertEqual(d * 0, deque())
        self.assertEqual(d * 1, deque('abc'))
        self.assertEqual(d * 2, deque('bcabc'))
        self.assertEqual(d * 30, deque('bcabc'))

    def test_setitem(self):
        n = 200
        d = deque(range(n))
        dla i w range(n):
            d[i] = 10 * i
        self.assertEqual(list(d), [10*i dla i w range(n)])
        l = list(d)
        dla i w range(1-n, 0, -1):
            d[i] = 7*i
            l[i] = 7*i
        self.assertEqual(list(d), l)

    def test_delitem(self):
        n = 500         # O(n**2) test, don't make this too big
        d = deque(range(n))
        self.assertRaises(IndexError, d.__delitem__, -n-1)
        self.assertRaises(IndexError, d.__delitem__, n)
        dla i w range(n):
            self.assertEqual(len(d), n-i)
            j = random.randrange(-len(d), len(d))
            val = d[j]
            self.assertIn(val, d)
            usuń d[j]
            self.assertNotIn(val, d)
        self.assertEqual(len(d), 0)

    def test_reverse(self):
        n = 500         # O(n**2) test, don't make this too big
        data = [random.random() dla i w range(n)]
        dla i w range(n):
            d = deque(data[:i])
            r = d.reverse()
            self.assertEqual(list(d), list(reversed(data[:i])))
            self.assertIs(r, Nic)
            d.reverse()
            self.assertEqual(list(d), data[:i])
        self.assertRaises(TypeError, d.reverse, 1)          # Arity jest zero

    def test_rotate(self):
        s = tuple('abcde')
        n = len(s)

        d = deque(s)
        d.rotate(1)             # verify rot(1)
        self.assertEqual(''.join(d), 'eabcd')

        d = deque(s)
        d.rotate(-1)            # verify rot(-1)
        self.assertEqual(''.join(d), 'bcdea')
        d.rotate()              # check default to 1
        self.assertEqual(tuple(d), s)

        dla i w range(n*3):
            d = deque(s)
            e = deque(d)
            d.rotate(i)         # check vs. rot(1) n times
            dla j w range(i):
                e.rotate(1)
            self.assertEqual(tuple(d), tuple(e))
            d.rotate(-i)        # check that it works w reverse
            self.assertEqual(tuple(d), s)
            e.rotate(n-i)       # check that it wraps forward
            self.assertEqual(tuple(e), s)

        dla i w range(n*3):
            d = deque(s)
            e = deque(d)
            d.rotate(-i)
            dla j w range(i):
                e.rotate(-1)    # check vs. rot(-1) n times
            self.assertEqual(tuple(d), tuple(e))
            d.rotate(i)         # check that it works w reverse
            self.assertEqual(tuple(d), s)
            e.rotate(i-n)       # check that it wraps backaround
            self.assertEqual(tuple(e), s)

        d = deque(s)
        e = deque(s)
        e.rotate(BIG+17)        # verify on long series of rotates
        dr = d.rotate
        dla i w range(BIG+17):
            dr()
        self.assertEqual(tuple(d), tuple(e))

        self.assertRaises(TypeError, d.rotate, 'x')   # Wrong arg type
        self.assertRaises(TypeError, d.rotate, 1, 10) # Too many args

        d = deque()
        d.rotate()              # rotate an empty deque
        self.assertEqual(d, deque())

    def test_len(self):
        d = deque('ab')
        self.assertEqual(len(d), 2)
        d.popleft()
        self.assertEqual(len(d), 1)
        d.pop()
        self.assertEqual(len(d), 0)
        self.assertRaises(IndexError, d.pop)
        self.assertEqual(len(d), 0)
        d.append('c')
        self.assertEqual(len(d), 1)
        d.appendleft('d')
        self.assertEqual(len(d), 2)
        d.clear()
        self.assertEqual(len(d), 0)

    def test_underflow(self):
        d = deque()
        self.assertRaises(IndexError, d.pop)
        self.assertRaises(IndexError, d.popleft)

    def test_clear(self):
        d = deque(range(100))
        self.assertEqual(len(d), 100)
        d.clear()
        self.assertEqual(len(d), 0)
        self.assertEqual(list(d), [])
        d.clear()               # clear an emtpy deque
        self.assertEqual(list(d), [])

    def test_remove(self):
        d = deque('abcdefghcij')
        d.remove('c')
        self.assertEqual(d, deque('abdefghcij'))
        d.remove('c')
        self.assertEqual(d, deque('abdefghij'))
        self.assertRaises(ValueError, d.remove, 'c')
        self.assertEqual(d, deque('abdefghij'))

        # Handle comparison errors
        d = deque(['a', 'b', BadCmp(), 'c'])
        e = deque(d)
        self.assertRaises(RuntimeError, d.remove, 'c')
        dla x, y w zip(d, e):
            # verify that original order oraz values are retained.
            self.assertPrawda(x jest y)

        # Handle evil mutator
        dla match w (Prawda, Nieprawda):
            d = deque(['ab'])
            d.extend([MutateCmp(d, match), 'c'])
            self.assertRaises(IndexError, d.remove, 'c')
            self.assertEqual(d, deque())

    def test_repr(self):
        d = deque(range(200))
        e = eval(repr(d))
        self.assertEqual(list(d), list(e))
        d.append(d)
        self.assertIn('...', repr(d))

    def test_print(self):
        d = deque(range(200))
        d.append(d)
        spróbuj:
            support.unlink(support.TESTFN)
            fo = open(support.TESTFN, "w")
            print(d, file=fo, end='')
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(d))
        w_końcu:
            fo.close()
            support.unlink(support.TESTFN)

    def test_init(self):
        self.assertRaises(TypeError, deque, 'abc', 2, 3);
        self.assertRaises(TypeError, deque, 1);

    def test_hash(self):
        self.assertRaises(TypeError, hash, deque('abc'))

    def test_long_steadystate_queue_popleft(self):
        dla size w (0, 1, 2, 100, 1000):
            d = deque(range(size))
            append, pop = d.append, d.popleft
            dla i w range(size, BIG):
                append(i)
                x = pop()
                jeżeli x != i - size:
                    self.assertEqual(x, i-size)
            self.assertEqual(list(d), list(range(BIG-size, BIG)))

    def test_long_steadystate_queue_popright(self):
        dla size w (0, 1, 2, 100, 1000):
            d = deque(reversed(range(size)))
            append, pop = d.appendleft, d.pop
            dla i w range(size, BIG):
                append(i)
                x = pop()
                jeżeli x != i - size:
                    self.assertEqual(x, i-size)
            self.assertEqual(list(reversed(list(d))),
                             list(range(BIG-size, BIG)))

    def test_big_queue_popleft(self):
        dalej
        d = deque()
        append, pop = d.append, d.popleft
        dla i w range(BIG):
            append(i)
        dla i w range(BIG):
            x = pop()
            jeżeli x != i:
                self.assertEqual(x, i)

    def test_big_queue_popright(self):
        d = deque()
        append, pop = d.appendleft, d.pop
        dla i w range(BIG):
            append(i)
        dla i w range(BIG):
            x = pop()
            jeżeli x != i:
                self.assertEqual(x, i)

    def test_big_stack_right(self):
        d = deque()
        append, pop = d.append, d.pop
        dla i w range(BIG):
            append(i)
        dla i w reversed(range(BIG)):
            x = pop()
            jeżeli x != i:
                self.assertEqual(x, i)
        self.assertEqual(len(d), 0)

    def test_big_stack_left(self):
        d = deque()
        append, pop = d.appendleft, d.popleft
        dla i w range(BIG):
            append(i)
        dla i w reversed(range(BIG)):
            x = pop()
            jeżeli x != i:
                self.assertEqual(x, i)
        self.assertEqual(len(d), 0)

    def test_roundtrip_iter_init(self):
        d = deque(range(200))
        e = deque(d)
        self.assertNotEqual(id(d), id(e))
        self.assertEqual(list(d), list(e))

    def test_pickle(self):
        d = deque(range(200))
        dla i w range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(d, i)
            e = pickle.loads(s)
            self.assertNotEqual(id(d), id(e))
            self.assertEqual(list(d), list(e))

##    def test_pickle_recursive(self):
##        d = deque('abc')
##        d.append(d)
##        dla i w range(pickle.HIGHEST_PROTOCOL + 1):
##            e = pickle.loads(pickle.dumps(d, i))
##            self.assertNotEqual(id(d), id(e))
##            self.assertEqual(id(e), id(e[-1]))

    def test_iterator_pickle(self):
        data = deque(range(200))
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            it = itorg = iter(data)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(type(itorg), type(it))
            self.assertEqual(list(it), list(data))

            it = pickle.loads(d)
            next(it)
            d = pickle.dumps(it, proto)
            self.assertEqual(list(it), list(data)[1:])

    def test_deepcopy(self):
        mut = [10]
        d = deque([mut])
        e = copy.deepcopy(d)
        self.assertEqual(list(d), list(e))
        mut[0] = 11
        self.assertNotEqual(id(d), id(e))
        self.assertNotEqual(list(d), list(e))

    def test_copy(self):
        mut = [10]
        d = deque([mut])
        e = copy.copy(d)
        self.assertEqual(list(d), list(e))
        mut[0] = 11
        self.assertNotEqual(id(d), id(e))
        self.assertEqual(list(d), list(e))

    def test_copy_method(self):
        mut = [10]
        d = deque([mut])
        e = d.copy()
        self.assertEqual(list(d), list(e))
        mut[0] = 11
        self.assertNotEqual(id(d), id(e))
        self.assertEqual(list(d), list(e))

    def test_reversed(self):
        dla s w ('abcd', range(2000)):
            self.assertEqual(list(reversed(deque(s))), list(reversed(s)))

    def test_reversed_new(self):
        klass = type(reversed(deque()))
        dla s w ('abcd', range(2000)):
            self.assertEqual(list(klass(deque(s))), list(reversed(s)))

    def test_gc_doesnt_blowup(self):
        zaimportuj gc
        # This used to assert-fail w deque_traverse() under a debug
        # build, albo run wild przy a NULL pointer w a release build.
        d = deque()
        dla i w range(100):
            d.append(1)
            gc.collect()

    def test_container_iterator(self):
        # Bug #3680: tp_traverse was nie implemented dla deque iterator objects
        klasa C(object):
            dalej
        dla i w range(2):
            obj = C()
            ref = weakref.ref(obj)
            jeżeli i == 0:
                container = deque([obj, 1])
            inaczej:
                container = reversed(deque([obj, 1]))
            obj.x = iter(container)
            usuń obj, container
            gc.collect()
            self.assertPrawda(ref() jest Nic, "Cycle was nie collected")

    check_sizeof = support.check_sizeof

    @support.cpython_only
    def test_sizeof(self):
        BLOCKLEN = 64
        basesize = support.calcobjsize('2P4nlP')
        blocksize = struct.calcsize('2P%dP' % BLOCKLEN)
        self.assertEqual(object.__sizeof__(deque()), basesize)
        check = self.check_sizeof
        check(deque(), basesize + blocksize)
        check(deque('a'), basesize + blocksize)
        check(deque('a' * (BLOCKLEN - 1)), basesize + blocksize)
        check(deque('a' * BLOCKLEN), basesize + 2 * blocksize)
        check(deque('a' * (42 * BLOCKLEN)), basesize + 43 * blocksize)

klasa TestVariousIteratorArgs(unittest.TestCase):

    def test_constructor(self):
        dla s w ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            dla g w (seq_tests.Sequence, seq_tests.IterFunc,
                      seq_tests.IterGen, seq_tests.IterFuncStop,
                      seq_tests.itermulti, seq_tests.iterfunc):
                self.assertEqual(list(deque(g(s))), list(g(s)))
            self.assertRaises(TypeError, deque, seq_tests.IterNextOnly(s))
            self.assertRaises(TypeError, deque, seq_tests.IterNoNext(s))
            self.assertRaises(ZeroDivisionError, deque, seq_tests.IterGenExc(s))

    def test_iter_with_altered_data(self):
        d = deque('abcdefg')
        it = iter(d)
        d.pop()
        self.assertRaises(RuntimeError, next, it)

    def test_runtime_error_on_empty_deque(self):
        d = deque()
        it = iter(d)
        d.append(10)
        self.assertRaises(RuntimeError, next, it)

klasa Deque(deque):
    dalej

klasa DequeWithBadIter(deque):
    def __iter__(self):
        podnieś TypeError

klasa TestSubclass(unittest.TestCase):

    def test_basics(self):
        d = Deque(range(25))
        d.__init__(range(200))
        dla i w range(200, 400):
            d.append(i)
        dla i w reversed(range(-200, 0)):
            d.appendleft(i)
        self.assertEqual(list(d), list(range(-200, 400)))
        self.assertEqual(len(d), 600)

        left = [d.popleft() dla i w range(250)]
        self.assertEqual(left, list(range(-200, 50)))
        self.assertEqual(list(d), list(range(50, 400)))

        right = [d.pop() dla i w range(250)]
        right.reverse()
        self.assertEqual(right, list(range(150, 400)))
        self.assertEqual(list(d), list(range(50, 150)))

        d.clear()
        self.assertEqual(len(d), 0)

    def test_copy_pickle(self):

        d = Deque('abc')

        e = d.__copy__()
        self.assertEqual(type(d), type(e))
        self.assertEqual(list(d), list(e))

        e = Deque(d)
        self.assertEqual(type(d), type(e))
        self.assertEqual(list(d), list(e))

        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(d, proto)
            e = pickle.loads(s)
            self.assertNotEqual(id(d), id(e))
            self.assertEqual(type(d), type(e))
            self.assertEqual(list(d), list(e))

        d = Deque('abcde', maxlen=4)

        e = d.__copy__()
        self.assertEqual(type(d), type(e))
        self.assertEqual(list(d), list(e))

        e = Deque(d)
        self.assertEqual(type(d), type(e))
        self.assertEqual(list(d), list(e))

        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(d, proto)
            e = pickle.loads(s)
            self.assertNotEqual(id(d), id(e))
            self.assertEqual(type(d), type(e))
            self.assertEqual(list(d), list(e))

##    def test_pickle(self):
##        d = Deque('abc')
##        d.append(d)
##
##        e = pickle.loads(pickle.dumps(d))
##        self.assertNotEqual(id(d), id(e))
##        self.assertEqual(type(d), type(e))
##        dd = d.pop()
##        ee = e.pop()
##        self.assertEqual(id(e), id(ee))
##        self.assertEqual(d, e)
##
##        d.x = d
##        e = pickle.loads(pickle.dumps(d))
##        self.assertEqual(id(e), id(e.x))
##
##        d = DequeWithBadIter('abc')
##        self.assertRaises(TypeError, pickle.dumps, d)

    def test_weakref(self):
        d = deque('gallahad')
        p = weakref.proxy(d)
        self.assertEqual(str(p), str(d))
        d = Nic
        self.assertRaises(ReferenceError, str, p)

    def test_strange_subclass(self):
        klasa X(deque):
            def __iter__(self):
                zwróć iter([])
        d1 = X([1,2,3])
        d2 = X([4,5,6])
        d1 == d2   # nie clear jeżeli this jest supposed to be Prawda albo Nieprawda,
                   # but it used to give a SystemError


klasa SubclassWithKwargs(deque):
    def __init__(self, newarg=1):
        deque.__init__(self)

klasa TestSubclassWithKwargs(unittest.TestCase):
    def test_subclass_with_kwargs(self):
        # SF bug #1486663 -- this used to erroneously podnieś a TypeError
        SubclassWithKwargs(newarg=1)

klasa TestSequence(seq_tests.CommonTest):
    type2test = deque

    def test_getitem(self):
        # For now, bypass tests that require slicing
        dalej

    def test_getslice(self):
        # For now, bypass tests that require slicing
        dalej

    def test_subscript(self):
        # For now, bypass tests that require slicing
        dalej

#==============================================================================

libreftest = """
Example z the Library Reference:  Doc/lib/libcollections.tex

>>> z collections zaimportuj deque
>>> d = deque('ghi')                 # make a new deque przy three items
>>> dla elem w d:                   # iterate over the deque's elements
...     print(elem.upper())
G
H
I
>>> d.append('j')                    # add a new entry to the right side
>>> d.appendleft('f')                # add a new entry to the left side
>>> d                                # show the representation of the deque
deque(['f', 'g', 'h', 'i', 'j'])
>>> d.pop()                          # zwróć oraz remove the rightmost item
'j'
>>> d.popleft()                      # zwróć oraz remove the leftmost item
'f'
>>> list(d)                          # list the contents of the deque
['g', 'h', 'i']
>>> d[0]                             # peek at leftmost item
'g'
>>> d[-1]                            # peek at rightmost item
'i'
>>> list(reversed(d))                # list the contents of a deque w reverse
['i', 'h', 'g']
>>> 'h' w d                         # search the deque
Prawda
>>> d.extend('jkl')                  # add multiple elements at once
>>> d
deque(['g', 'h', 'i', 'j', 'k', 'l'])
>>> d.rotate(1)                      # right rotation
>>> d
deque(['l', 'g', 'h', 'i', 'j', 'k'])
>>> d.rotate(-1)                     # left rotation
>>> d
deque(['g', 'h', 'i', 'j', 'k', 'l'])
>>> deque(reversed(d))               # make a new deque w reverse order
deque(['l', 'k', 'j', 'i', 'h', 'g'])
>>> d.clear()                        # empty the deque
>>> d.pop()                          # cannot pop z an empty deque
Traceback (most recent call last):
  File "<pyshell#6>", line 1, w -toplevel-
    d.pop()
IndexError: pop z an empty deque

>>> d.extendleft('abc')              # extendleft() reverses the input order
>>> d
deque(['c', 'b', 'a'])



>>> def delete_nth(d, n):
...     d.rotate(-n)
...     d.popleft()
...     d.rotate(n)
...
>>> d = deque('abcdef')
>>> delete_nth(d, 2)   # remove the entry at d[2]
>>> d
deque(['a', 'b', 'd', 'e', 'f'])



>>> def roundrobin(*iterables):
...     pending = deque(iter(i) dla i w iterables)
...     dopóki pending:
...         task = pending.popleft()
...         spróbuj:
...             uzyskaj next(task)
...         wyjąwszy StopIteration:
...             kontynuuj
...         pending.append(task)
...

>>> dla value w roundrobin('abc', 'd', 'efgh'):
...     print(value)
...
a
d
e
b
f
c
g
h


>>> def maketree(iterable):
...     d = deque(iterable)
...     dopóki len(d) > 1:
...         pair = [d.popleft(), d.popleft()]
...         d.append(pair)
...     zwróć list(d)
...
>>> print(maketree('abcdefgh'))
[[[['a', 'b'], ['c', 'd']], [['e', 'f'], ['g', 'h']]]]

"""


#==============================================================================

__test__ = {'libreftest' : libreftest}

def test_main(verbose=Nic):
    zaimportuj sys
    test_classes = (
        TestBasic,
        TestVariousIteratorArgs,
        TestSubclass,
        TestSubclassWithKwargs,
        TestSequence,
    )

    support.run_unittest(*test_classes)

    # verify reference counting
    jeżeli verbose oraz hasattr(sys, "gettotalrefcount"):
        zaimportuj gc
        counts = [Nic] * 5
        dla i w range(len(counts)):
            support.run_unittest(*test_classes)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        print(counts)

    # doctests
    z test zaimportuj test_deque
    support.run_doctest(test_deque, verbose)

jeżeli __name__ == "__main__":
    test_main(verbose=Prawda)
