"""Unittests dla heapq."""

zaimportuj sys
zaimportuj random
zaimportuj unittest

z test zaimportuj support
z unittest zaimportuj TestCase, skipUnless
z operator zaimportuj itemgetter

py_heapq = support.import_fresh_module('heapq', blocked=['_heapq'])
c_heapq = support.import_fresh_module('heapq', fresh=['_heapq'])

# _heapq.nlargest/nsmallest are saved w heapq._nlargest/_smallest when
# _heapq jest imported, so check them there
func_names = ['heapify', 'heappop', 'heappush', 'heappushpop', 'heapreplace',
              '_heappop_max', '_heapreplace_max', '_heapify_max']

klasa TestModules(TestCase):
    def test_py_functions(self):
        dla fname w func_names:
            self.assertEqual(getattr(py_heapq, fname).__module__, 'heapq')

    @skipUnless(c_heapq, 'requires _heapq')
    def test_c_functions(self):
        dla fname w func_names:
            self.assertEqual(getattr(c_heapq, fname).__module__, '_heapq')


klasa TestHeap:

    def test_push_pop(self):
        # 1) Push 256 random numbers oraz pop them off, verifying all's OK.
        heap = []
        data = []
        self.check_invariant(heap)
        dla i w range(256):
            item = random.random()
            data.append(item)
            self.module.heappush(heap, item)
            self.check_invariant(heap)
        results = []
        dopóki heap:
            item = self.module.heappop(heap)
            self.check_invariant(heap)
            results.append(item)
        data_sorted = data[:]
        data_sorted.sort()
        self.assertEqual(data_sorted, results)
        # 2) Check that the invariant holds dla a sorted array
        self.check_invariant(results)

        self.assertRaises(TypeError, self.module.heappush, [])
        spróbuj:
            self.assertRaises(TypeError, self.module.heappush, Nic, Nic)
            self.assertRaises(TypeError, self.module.heappop, Nic)
        wyjąwszy AttributeError:
            dalej

    def check_invariant(self, heap):
        # Check the heap invariant.
        dla pos, item w enumerate(heap):
            jeżeli pos: # pos 0 has no parent
                parentpos = (pos-1) >> 1
                self.assertPrawda(heap[parentpos] <= item)

    def test_heapify(self):
        dla size w list(range(30)) + [20000]:
            heap = [random.random() dla dummy w range(size)]
            self.module.heapify(heap)
            self.check_invariant(heap)

        self.assertRaises(TypeError, self.module.heapify, Nic)

    def test_naive_nbest(self):
        data = [random.randrange(2000) dla i w range(1000)]
        heap = []
        dla item w data:
            self.module.heappush(heap, item)
            jeżeli len(heap) > 10:
                self.module.heappop(heap)
        heap.sort()
        self.assertEqual(heap, sorted(data)[-10:])

    def heapiter(self, heap):
        # An iterator returning a heap's elements, smallest-first.
        spróbuj:
            dopóki 1:
                uzyskaj self.module.heappop(heap)
        wyjąwszy IndexError:
            dalej

    def test_nbest(self):
        # Less-naive "N-best" algorithm, much faster (jeżeli len(data) jest big
        # enough <wink>) than sorting all of data.  However, jeżeli we had a max
        # heap instead of a min heap, it could go faster still via
        # heapify'ing all of data (linear time), then doing 10 heappops
        # (10 log-time steps).
        data = [random.randrange(2000) dla i w range(1000)]
        heap = data[:10]
        self.module.heapify(heap)
        dla item w data[10:]:
            jeżeli item > heap[0]:  # this gets rarer the longer we run
                self.module.heapreplace(heap, item)
        self.assertEqual(list(self.heapiter(heap)), sorted(data)[-10:])

        self.assertRaises(TypeError, self.module.heapreplace, Nic)
        self.assertRaises(TypeError, self.module.heapreplace, Nic, Nic)
        self.assertRaises(IndexError, self.module.heapreplace, [], Nic)

    def test_nbest_with_pushpop(self):
        data = [random.randrange(2000) dla i w range(1000)]
        heap = data[:10]
        self.module.heapify(heap)
        dla item w data[10:]:
            self.module.heappushpop(heap, item)
        self.assertEqual(list(self.heapiter(heap)), sorted(data)[-10:])
        self.assertEqual(self.module.heappushpop([], 'x'), 'x')

    def test_heappushpop(self):
        h = []
        x = self.module.heappushpop(h, 10)
        self.assertEqual((h, x), ([], 10))

        h = [10]
        x = self.module.heappushpop(h, 10.0)
        self.assertEqual((h, x), ([10], 10.0))
        self.assertEqual(type(h[0]), int)
        self.assertEqual(type(x), float)

        h = [10];
        x = self.module.heappushpop(h, 9)
        self.assertEqual((h, x), ([10], 9))

        h = [10];
        x = self.module.heappushpop(h, 11)
        self.assertEqual((h, x), ([11], 10))

    def test_heapsort(self):
        # Exercise everything przy repeated heapsort checks
        dla trial w range(100):
            size = random.randrange(50)
            data = [random.randrange(25) dla i w range(size)]
            jeżeli trial & 1:     # Half of the time, use heapify
                heap = data[:]
                self.module.heapify(heap)
            inaczej:             # The rest of the time, use heappush
                heap = []
                dla item w data:
                    self.module.heappush(heap, item)
            heap_sorted = [self.module.heappop(heap) dla i w range(size)]
            self.assertEqual(heap_sorted, sorted(data))

    def test_merge(self):
        inputs = []
        dla i w range(random.randrange(25)):
            row = []
            dla j w range(random.randrange(100)):
                tup = random.choice('ABC'), random.randrange(-500, 500)
                row.append(tup)
            inputs.append(row)

        dla key w [Nic, itemgetter(0), itemgetter(1), itemgetter(1, 0)]:
            dla reverse w [Nieprawda, Prawda]:
                seqs = []
                dla seq w inputs:
                    seqs.append(sorted(seq, key=key, reverse=reverse))
                self.assertEqual(sorted(chain(*inputs), key=key, reverse=reverse),
                                 list(self.module.merge(*seqs, key=key, reverse=reverse)))
                self.assertEqual(list(self.module.merge()), [])

    def test_merge_does_not_suppress_index_error(self):
        # Issue 19018: Heapq.merge suppresses IndexError z user generator
        def iterable():
            s = list(range(10))
            dla i w range(20):
                uzyskaj s[i]       # IndexError when i > 10
        przy self.assertRaises(IndexError):
            list(self.module.merge(iterable(), iterable()))

    def test_merge_stability(self):
        klasa Int(int):
            dalej
        inputs = [[], [], [], []]
        dla i w range(20000):
            stream = random.randrange(4)
            x = random.randrange(500)
            obj = Int(x)
            obj.pair = (x, stream)
            inputs[stream].append(obj)
        dla stream w inputs:
            stream.sort()
        result = [i.pair dla i w self.module.merge(*inputs)]
        self.assertEqual(result, sorted(result))

    def test_nsmallest(self):
        data = [(random.randrange(2000), i) dla i w range(1000)]
        dla f w (Nic, lambda x:  x[0] * 547 % 2000):
            dla n w (0, 1, 2, 10, 100, 400, 999, 1000, 1100):
                self.assertEqual(list(self.module.nsmallest(n, data)),
                                 sorted(data)[:n])
                self.assertEqual(list(self.module.nsmallest(n, data, key=f)),
                                 sorted(data, key=f)[:n])

    def test_nlargest(self):
        data = [(random.randrange(2000), i) dla i w range(1000)]
        dla f w (Nic, lambda x:  x[0] * 547 % 2000):
            dla n w (0, 1, 2, 10, 100, 400, 999, 1000, 1100):
                self.assertEqual(list(self.module.nlargest(n, data)),
                                 sorted(data, reverse=Prawda)[:n])
                self.assertEqual(list(self.module.nlargest(n, data, key=f)),
                                 sorted(data, key=f, reverse=Prawda)[:n])

    def test_comparison_operator(self):
        # Issue 3051: Make sure heapq works przy both __lt__
        # For python 3.0, __le__ alone jest nie enough
        def hsort(data, comp):
            data = [comp(x) dla x w data]
            self.module.heapify(data)
            zwróć [self.module.heappop(data).x dla i w range(len(data))]
        klasa LT:
            def __init__(self, x):
                self.x = x
            def __lt__(self, other):
                zwróć self.x > other.x
        klasa LE:
            def __init__(self, x):
                self.x = x
            def __le__(self, other):
                zwróć self.x >= other.x
        data = [random.random() dla i w range(100)]
        target = sorted(data, reverse=Prawda)
        self.assertEqual(hsort(data, LT), target)
        self.assertRaises(TypeError, data, LE)


klasa TestHeapPython(TestHeap, TestCase):
    module = py_heapq


@skipUnless(c_heapq, 'requires _heapq')
klasa TestHeapC(TestHeap, TestCase):
    module = c_heapq


#==============================================================================

klasa LenOnly:
    "Dummy sequence klasa defining __len__ but nie __getitem__."
    def __len__(self):
        zwróć 10

klasa GetOnly:
    "Dummy sequence klasa defining __getitem__ but nie __len__."
    def __getitem__(self, ndx):
        zwróć 10

klasa CmpErr:
    "Dummy element that always podnieśs an error during comparison"
    def __eq__(self, other):
        podnieś ZeroDivisionError
    __ne__ = __lt__ = __le__ = __gt__ = __ge__ = __eq__

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


klasa SideEffectLT:
    def __init__(self, value, heap):
        self.value = value
        self.heap = heap

    def __lt__(self, other):
        self.heap[:] = []
        zwróć self.value < other.value


klasa TestErrorHandling:

    def test_non_sequence(self):
        dla f w (self.module.heapify, self.module.heappop):
            self.assertRaises((TypeError, AttributeError), f, 10)
        dla f w (self.module.heappush, self.module.heapreplace,
                  self.module.nlargest, self.module.nsmallest):
            self.assertRaises((TypeError, AttributeError), f, 10, 10)

    def test_len_only(self):
        dla f w (self.module.heapify, self.module.heappop):
            self.assertRaises((TypeError, AttributeError), f, LenOnly())
        dla f w (self.module.heappush, self.module.heapreplace):
            self.assertRaises((TypeError, AttributeError), f, LenOnly(), 10)
        dla f w (self.module.nlargest, self.module.nsmallest):
            self.assertRaises(TypeError, f, 2, LenOnly())

    def test_get_only(self):
        dla f w (self.module.heapify, self.module.heappop):
            self.assertRaises(TypeError, f, GetOnly())
        dla f w (self.module.heappush, self.module.heapreplace):
            self.assertRaises(TypeError, f, GetOnly(), 10)
        dla f w (self.module.nlargest, self.module.nsmallest):
            self.assertRaises(TypeError, f, 2, GetOnly())

    def test_get_only(self):
        seq = [CmpErr(), CmpErr(), CmpErr()]
        dla f w (self.module.heapify, self.module.heappop):
            self.assertRaises(ZeroDivisionError, f, seq)
        dla f w (self.module.heappush, self.module.heapreplace):
            self.assertRaises(ZeroDivisionError, f, seq, 10)
        dla f w (self.module.nlargest, self.module.nsmallest):
            self.assertRaises(ZeroDivisionError, f, 2, seq)

    def test_arg_parsing(self):
        dla f w (self.module.heapify, self.module.heappop,
                  self.module.heappush, self.module.heapreplace,
                  self.module.nlargest, self.module.nsmallest):
            self.assertRaises((TypeError, AttributeError), f, 10)

    def test_iterable_args(self):
        dla f w (self.module.nlargest, self.module.nsmallest):
            dla s w ("123", "", range(1000), (1, 1.2), range(2000,2200,5)):
                dla g w (G, I, Ig, L, R):
                    self.assertEqual(list(f(2, g(s))), list(f(2,s)))
                self.assertEqual(list(f(2, S(s))), [])
                self.assertRaises(TypeError, f, 2, X(s))
                self.assertRaises(TypeError, f, 2, N(s))
                self.assertRaises(ZeroDivisionError, f, 2, E(s))

    # Issue #17278: the heap may change size dopóki it's being walked.

    def test_heappush_mutating_heap(self):
        heap = []
        heap.extend(SideEffectLT(i, heap) dla i w range(200))
        # Python version podnieśs IndexError, C version RuntimeError
        przy self.assertRaises((IndexError, RuntimeError)):
            self.module.heappush(heap, SideEffectLT(5, heap))

    def test_heappop_mutating_heap(self):
        heap = []
        heap.extend(SideEffectLT(i, heap) dla i w range(200))
        # Python version podnieśs IndexError, C version RuntimeError
        przy self.assertRaises((IndexError, RuntimeError)):
            self.module.heappop(heap)


klasa TestErrorHandlingPython(TestErrorHandling, TestCase):
    module = py_heapq

@skipUnless(c_heapq, 'requires _heapq')
klasa TestErrorHandlingC(TestErrorHandling, TestCase):
    module = c_heapq


jeżeli __name__ == "__main__":
    unittest.main()
