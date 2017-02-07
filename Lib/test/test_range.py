# Python test set -- built-in functions

zaimportuj test.support, unittest
zaimportuj sys
zaimportuj pickle
zaimportuj itertools

# pure Python implementations (3 args only), dla comparison
def pyrange(start, stop, step):
    jeżeli (start - stop) // step < 0:
        # replace stop przy next element w the sequence of integers
        # that are congruent to start modulo step.
        stop += (start - stop) % step
        dopóki start != stop:
            uzyskaj start
            start += step

def pyrange_reversed(start, stop, step):
    stop += (start - stop) % step
    zwróć pyrange(stop - step, start - step, -step)


klasa RangeTest(unittest.TestCase):
    def assert_iterators_equal(self, xs, ys, test_id, limit=Nic):
        # check that an iterator xs matches the expected results ys,
        # up to a given limit.
        jeżeli limit jest nie Nic:
            xs = itertools.islice(xs, limit)
            ys = itertools.islice(ys, limit)
        sentinel = object()
        pairs = itertools.zip_longest(xs, ys, fillvalue=sentinel)
        dla i, (x, y) w enumerate(pairs):
            jeżeli x == y:
                kontynuuj
            albo_inaczej x == sentinel:
                self.fail('{}: iterator ended unexpectedly '
                          'at position {}; expected {}'.format(test_id, i, y))
            albo_inaczej y == sentinel:
                self.fail('{}: unexpected excess element {} at '
                          'position {}'.format(test_id, x, i))
            inaczej:
                self.fail('{}: wrong element at position {};'
                          'expected {}, got {}'.format(test_id, i, y, x))

    def test_range(self):
        self.assertEqual(list(range(3)), [0, 1, 2])
        self.assertEqual(list(range(1, 5)), [1, 2, 3, 4])
        self.assertEqual(list(range(0)), [])
        self.assertEqual(list(range(-3)), [])
        self.assertEqual(list(range(1, 10, 3)), [1, 4, 7])
        self.assertEqual(list(range(5, -5, -3)), [5, 2, -1, -4])

        a = 10
        b = 100
        c = 50

        self.assertEqual(list(range(a, a+2)), [a, a+1])
        self.assertEqual(list(range(a+2, a, -1)), [a+2, a+1])
        self.assertEqual(list(range(a+4, a, -2)), [a+4, a+2])

        seq = list(range(a, b, c))
        self.assertIn(a, seq)
        self.assertNotIn(b, seq)
        self.assertEqual(len(seq), 2)

        seq = list(range(b, a, -c))
        self.assertIn(b, seq)
        self.assertNotIn(a, seq)
        self.assertEqual(len(seq), 2)

        seq = list(range(-a, -b, -c))
        self.assertIn(-a, seq)
        self.assertNotIn(-b, seq)
        self.assertEqual(len(seq), 2)

        self.assertRaises(TypeError, range)
        self.assertRaises(TypeError, range, 1, 2, 3, 4)
        self.assertRaises(ValueError, range, 1, 2, 0)

        self.assertRaises(TypeError, range, 0.0, 2, 1)
        self.assertRaises(TypeError, range, 1, 2.0, 1)
        self.assertRaises(TypeError, range, 1, 2, 1.0)
        self.assertRaises(TypeError, range, 1e100, 1e101, 1e101)

        self.assertRaises(TypeError, range, 0, "spam")
        self.assertRaises(TypeError, range, 0, 42, "spam")

        self.assertEqual(len(range(0, sys.maxsize, sys.maxsize-1)), 2)

        r = range(-sys.maxsize, sys.maxsize, 2)
        self.assertEqual(len(r), sys.maxsize)

    def test_large_operands(self):
        x = range(10**20, 10**20+10, 3)
        self.assertEqual(len(x), 4)
        self.assertEqual(len(list(x)), 4)

        x = range(10**20+10, 10**20, 3)
        self.assertEqual(len(x), 0)
        self.assertEqual(len(list(x)), 0)

        x = range(10**20, 10**20+10, -3)
        self.assertEqual(len(x), 0)
        self.assertEqual(len(list(x)), 0)

        x = range(10**20+10, 10**20, -3)
        self.assertEqual(len(x), 4)
        self.assertEqual(len(list(x)), 4)

        # Now test range() przy longs
        self.assertEqual(list(range(-2**100)), [])
        self.assertEqual(list(range(0, -2**100)), [])
        self.assertEqual(list(range(0, 2**100, -1)), [])
        self.assertEqual(list(range(0, 2**100, -1)), [])

        a = int(10 * sys.maxsize)
        b = int(100 * sys.maxsize)
        c = int(50 * sys.maxsize)

        self.assertEqual(list(range(a, a+2)), [a, a+1])
        self.assertEqual(list(range(a+2, a, -1)), [a+2, a+1])
        self.assertEqual(list(range(a+4, a, -2)), [a+4, a+2])

        seq = list(range(a, b, c))
        self.assertIn(a, seq)
        self.assertNotIn(b, seq)
        self.assertEqual(len(seq), 2)
        self.assertEqual(seq[0], a)
        self.assertEqual(seq[-1], a+c)

        seq = list(range(b, a, -c))
        self.assertIn(b, seq)
        self.assertNotIn(a, seq)
        self.assertEqual(len(seq), 2)
        self.assertEqual(seq[0], b)
        self.assertEqual(seq[-1], b-c)

        seq = list(range(-a, -b, -c))
        self.assertIn(-a, seq)
        self.assertNotIn(-b, seq)
        self.assertEqual(len(seq), 2)
        self.assertEqual(seq[0], -a)
        self.assertEqual(seq[-1], -a-c)

    def test_large_range(self):
        # Check long ranges (len > sys.maxsize)
        # len() jest expected to fail due to limitations of the __len__ protocol
        def _range_len(x):
            spróbuj:
                length = len(x)
            wyjąwszy OverflowError:
                step = x[1] - x[0]
                length = 1 + ((x[-1] - x[0]) // step)
            zwróć length
        a = -sys.maxsize
        b = sys.maxsize
        expected_len = b - a
        x = range(a, b)
        self.assertIn(a, x)
        self.assertNotIn(b, x)
        self.assertRaises(OverflowError, len, x)
        self.assertEqual(_range_len(x), expected_len)
        self.assertEqual(x[0], a)
        idx = sys.maxsize+1
        self.assertEqual(x[idx], a+idx)
        self.assertEqual(x[idx:idx+1][0], a+idx)
        przy self.assertRaises(IndexError):
            x[-expected_len-1]
        przy self.assertRaises(IndexError):
            x[expected_len]

        a = 0
        b = 2 * sys.maxsize
        expected_len = b - a
        x = range(a, b)
        self.assertIn(a, x)
        self.assertNotIn(b, x)
        self.assertRaises(OverflowError, len, x)
        self.assertEqual(_range_len(x), expected_len)
        self.assertEqual(x[0], a)
        idx = sys.maxsize+1
        self.assertEqual(x[idx], a+idx)
        self.assertEqual(x[idx:idx+1][0], a+idx)
        przy self.assertRaises(IndexError):
            x[-expected_len-1]
        przy self.assertRaises(IndexError):
            x[expected_len]

        a = 0
        b = sys.maxsize**10
        c = 2*sys.maxsize
        expected_len = 1 + (b - a) // c
        x = range(a, b, c)
        self.assertIn(a, x)
        self.assertNotIn(b, x)
        self.assertRaises(OverflowError, len, x)
        self.assertEqual(_range_len(x), expected_len)
        self.assertEqual(x[0], a)
        idx = sys.maxsize+1
        self.assertEqual(x[idx], a+(idx*c))
        self.assertEqual(x[idx:idx+1][0], a+(idx*c))
        przy self.assertRaises(IndexError):
            x[-expected_len-1]
        przy self.assertRaises(IndexError):
            x[expected_len]

        a = sys.maxsize**10
        b = 0
        c = -2*sys.maxsize
        expected_len = 1 + (b - a) // c
        x = range(a, b, c)
        self.assertIn(a, x)
        self.assertNotIn(b, x)
        self.assertRaises(OverflowError, len, x)
        self.assertEqual(_range_len(x), expected_len)
        self.assertEqual(x[0], a)
        idx = sys.maxsize+1
        self.assertEqual(x[idx], a+(idx*c))
        self.assertEqual(x[idx:idx+1][0], a+(idx*c))
        przy self.assertRaises(IndexError):
            x[-expected_len-1]
        przy self.assertRaises(IndexError):
            x[expected_len]

    def test_invalid_invocation(self):
        self.assertRaises(TypeError, range)
        self.assertRaises(TypeError, range, 1, 2, 3, 4)
        self.assertRaises(ValueError, range, 1, 2, 0)
        a = int(10 * sys.maxsize)
        self.assertRaises(ValueError, range, a, a + 1, int(0))
        self.assertRaises(TypeError, range, 1., 1., 1.)
        self.assertRaises(TypeError, range, 1e100, 1e101, 1e101)
        self.assertRaises(TypeError, range, 0, "spam")
        self.assertRaises(TypeError, range, 0, 42, "spam")
        # Exercise various combinations of bad arguments, to check
        # refcounting logic
        self.assertRaises(TypeError, range, 0.0)
        self.assertRaises(TypeError, range, 0, 0.0)
        self.assertRaises(TypeError, range, 0.0, 0)
        self.assertRaises(TypeError, range, 0.0, 0.0)
        self.assertRaises(TypeError, range, 0, 0, 1.0)
        self.assertRaises(TypeError, range, 0, 0.0, 1)
        self.assertRaises(TypeError, range, 0, 0.0, 1.0)
        self.assertRaises(TypeError, range, 0.0, 0, 1)
        self.assertRaises(TypeError, range, 0.0, 0, 1.0)
        self.assertRaises(TypeError, range, 0.0, 0.0, 1)
        self.assertRaises(TypeError, range, 0.0, 0.0, 1.0)

    def test_index(self):
        u = range(2)
        self.assertEqual(u.index(0), 0)
        self.assertEqual(u.index(1), 1)
        self.assertRaises(ValueError, u.index, 2)

        u = range(-2, 3)
        self.assertEqual(u.count(0), 1)
        self.assertEqual(u.index(0), 2)
        self.assertRaises(TypeError, u.index)

        klasa BadExc(Exception):
            dalej

        klasa BadCmp:
            def __eq__(self, other):
                jeżeli other == 2:
                    podnieś BadExc()
                zwróć Nieprawda

        a = range(4)
        self.assertRaises(BadExc, a.index, BadCmp())

        a = range(-2, 3)
        self.assertEqual(a.index(0), 2)
        self.assertEqual(range(1, 10, 3).index(4), 1)
        self.assertEqual(range(1, -10, -3).index(-5), 2)

        self.assertEqual(range(10**20).index(1), 1)
        self.assertEqual(range(10**20).index(10**20 - 1), 10**20 - 1)

        self.assertRaises(ValueError, range(1, 2**100, 2).index, 2**87)
        self.assertEqual(range(1, 2**100, 2).index(2**87+1), 2**86)

        klasa AlwaysEqual(object):
            def __eq__(self, other):
                zwróć Prawda
        always_equal = AlwaysEqual()
        self.assertEqual(range(10).index(always_equal), 0)

    def test_user_index_method(self):
        bignum = 2*sys.maxsize
        smallnum = 42

        # User-defined klasa przy an __index__ method
        klasa I:
            def __init__(self, n):
                self.n = int(n)
            def __index__(self):
                zwróć self.n
        self.assertEqual(list(range(I(bignum), I(bignum + 1))), [bignum])
        self.assertEqual(list(range(I(smallnum), I(smallnum + 1))), [smallnum])

        # User-defined klasa przy a failing __index__ method
        klasa IX:
            def __index__(self):
                podnieś RuntimeError
        self.assertRaises(RuntimeError, range, IX())

        # User-defined klasa przy an invalid __index__ method
        klasa IN:
            def __index__(self):
                zwróć "not a number"

        self.assertRaises(TypeError, range, IN())

        # Test use of user-defined classes w slice indices.
        self.assertEqual(range(10)[:I(5)], range(5))

        przy self.assertRaises(RuntimeError):
            range(0, 10)[:IX()]

        przy self.assertRaises(TypeError):
            range(0, 10)[:IN()]

    def test_count(self):
        self.assertEqual(range(3).count(-1), 0)
        self.assertEqual(range(3).count(0), 1)
        self.assertEqual(range(3).count(1), 1)
        self.assertEqual(range(3).count(2), 1)
        self.assertEqual(range(3).count(3), 0)
        self.assertIs(type(range(3).count(-1)), int)
        self.assertIs(type(range(3).count(1)), int)
        self.assertEqual(range(10**20).count(1), 1)
        self.assertEqual(range(10**20).count(10**20), 0)
        self.assertEqual(range(3).index(1), 1)
        self.assertEqual(range(1, 2**100, 2).count(2**87), 0)
        self.assertEqual(range(1, 2**100, 2).count(2**87+1), 1)

        klasa AlwaysEqual(object):
            def __eq__(self, other):
                zwróć Prawda
        always_equal = AlwaysEqual()
        self.assertEqual(range(10).count(always_equal), 10)

        self.assertEqual(len(range(sys.maxsize, sys.maxsize+10)), 10)

    def test_repr(self):
        self.assertEqual(repr(range(1)), 'range(0, 1)')
        self.assertEqual(repr(range(1, 2)), 'range(1, 2)')
        self.assertEqual(repr(range(1, 2, 3)), 'range(1, 2, 3)')

    def test_pickling(self):
        testcases = [(13,), (0, 11), (-22, 10), (20, 3, -1),
                     (13, 21, 3), (-2, 2, 2), (2**65, 2**65+2)]
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            dla t w testcases:
                przy self.subTest(proto=proto, test=t):
                    r = range(*t)
                    self.assertEqual(list(pickle.loads(pickle.dumps(r, proto))),
                                     list(r))

    def test_iterator_pickling(self):
        testcases = [(13,), (0, 11), (-22, 10), (20, 3, -1),
                     (13, 21, 3), (-2, 2, 2), (2**65, 2**65+2)]
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            dla t w testcases:
                it = itorg = iter(range(*t))
                data = list(range(*t))

                d = pickle.dumps(it, proto)
                it = pickle.loads(d)
                self.assertEqual(type(itorg), type(it))
                self.assertEqual(list(it), data)

                it = pickle.loads(d)
                spróbuj:
                    next(it)
                wyjąwszy StopIteration:
                    kontynuuj
                d = pickle.dumps(it, proto)
                it = pickle.loads(d)
                self.assertEqual(list(it), data[1:])

    def test_exhausted_iterator_pickling(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            r = range(2**65, 2**65+2)
            i = iter(r)
            dopóki Prawda:
                r = next(i)
                jeżeli r == 2**65+1:
                    przerwij
            d = pickle.dumps(i, proto)
            i2 = pickle.loads(d)
            self.assertEqual(list(i), [])
            self.assertEqual(list(i2), [])

    def test_large_exhausted_iterator_pickling(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            r = range(20)
            i = iter(r)
            dopóki Prawda:
                r = next(i)
                jeżeli r == 19:
                    przerwij
            d = pickle.dumps(i, proto)
            i2 = pickle.loads(d)
            self.assertEqual(list(i), [])
            self.assertEqual(list(i2), [])

    def test_odd_bug(self):
        # This used to podnieś a "SystemError: NULL result without error"
        # because the range validation step was eating the exception
        # before NULL was returned.
        przy self.assertRaises(TypeError):
            range([], 1, -1)

    def test_types(self):
        # Non-integer objects *equal* to any of the range's items are supposed
        # to be contained w the range.
        self.assertIn(1.0, range(3))
        self.assertIn(Prawda, range(3))
        self.assertIn(1+0j, range(3))

        klasa C1:
            def __eq__(self, other): zwróć Prawda
        self.assertIn(C1(), range(3))

        # Objects are never coerced into other types dla comparison.
        klasa C2:
            def __int__(self): zwróć 1
            def __index__(self): zwróć 1
        self.assertNotIn(C2(), range(3))
        # ..wyjąwszy jeżeli explicitly told so.
        self.assertIn(int(C2()), range(3))

        # Check that the range.__contains__ optimization jest only
        # used dla ints, nie dla instances of subclasses of int.
        klasa C3(int):
            def __eq__(self, other): zwróć Prawda
        self.assertIn(C3(11), range(10))
        self.assertIn(C3(11), list(range(10)))

    def test_strided_limits(self):
        r = range(0, 101, 2)
        self.assertIn(0, r)
        self.assertNotIn(1, r)
        self.assertIn(2, r)
        self.assertNotIn(99, r)
        self.assertIn(100, r)
        self.assertNotIn(101, r)

        r = range(0, -20, -1)
        self.assertIn(0, r)
        self.assertIn(-1, r)
        self.assertIn(-19, r)
        self.assertNotIn(-20, r)

        r = range(0, -20, -2)
        self.assertIn(-18, r)
        self.assertNotIn(-19, r)
        self.assertNotIn(-20, r)

    def test_empty(self):
        r = range(0)
        self.assertNotIn(0, r)
        self.assertNotIn(1, r)

        r = range(0, -10)
        self.assertNotIn(0, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(1, r)

    def test_range_iterators(self):
        # exercise 'fast' iterators, that use a rangeiterobject internally.
        # see issue 7298
        limits = [base + jiggle
                  dla M w (2**32, 2**64)
                  dla base w (-M, -M//2, 0, M//2, M)
                  dla jiggle w (-2, -1, 0, 1, 2)]
        test_ranges = [(start, end, step)
                       dla start w limits
                       dla end w limits
                       dla step w (-2**63, -2**31, -2, -1, 1, 2)]

        dla start, end, step w test_ranges:
            iter1 = range(start, end, step)
            iter2 = pyrange(start, end, step)
            test_id = "range({}, {}, {})".format(start, end, step)
            # check first 100 entries
            self.assert_iterators_equal(iter1, iter2, test_id, limit=100)

            iter1 = reversed(range(start, end, step))
            iter2 = pyrange_reversed(start, end, step)
            test_id = "reversed(range({}, {}, {}))".format(start, end, step)
            self.assert_iterators_equal(iter1, iter2, test_id, limit=100)

    def test_slice(self):
        def check(start, stop, step=Nic):
            i = slice(start, stop, step)
            self.assertEqual(list(r[i]), list(r)[i])
            self.assertEqual(len(r[i]), len(list(r)[i]))
        dla r w [range(10),
                  range(0),
                  range(1, 9, 3),
                  range(8, 0, -3),
                  range(sys.maxsize+1, sys.maxsize+10),
                  ]:
            check(0, 2)
            check(0, 20)
            check(1, 2)
            check(20, 30)
            check(-30, -20)
            check(-1, 100, 2)
            check(0, -1)
            check(-1, -3, -1)

    def test_contains(self):
        r = range(10)
        self.assertIn(0, r)
        self.assertIn(1, r)
        self.assertIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)
        r = range(9, -1, -1)
        self.assertIn(0, r)
        self.assertIn(1, r)
        self.assertIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)
        r = range(0, 10, 2)
        self.assertIn(0, r)
        self.assertNotIn(1, r)
        self.assertNotIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)
        r = range(9, -1, -2)
        self.assertNotIn(0, r)
        self.assertIn(1, r)
        self.assertIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)

    def test_reverse_iteration(self):
        dla r w [range(10),
                  range(0),
                  range(1, 9, 3),
                  range(8, 0, -3),
                  range(sys.maxsize+1, sys.maxsize+10),
                  ]:
            self.assertEqual(list(reversed(r)), list(r)[::-1])

    def test_issue11845(self):
        r = range(*slice(1, 18, 2).indices(20))
        values = {Nic, 0, 1, -1, 2, -2, 5, -5, 19, -19,
                  20, -20, 21, -21, 30, -30, 99, -99}
        dla i w values:
            dla j w values:
                dla k w values - {0}:
                    r[i:j:k]

    def test_comparison(self):
        test_ranges = [range(0), range(0, -1), range(1, 1, 3),
                       range(1), range(5, 6), range(5, 6, 2),
                       range(5, 7, 2), range(2), range(0, 4, 2),
                       range(0, 5, 2), range(0, 6, 2)]
        test_tuples = list(map(tuple, test_ranges))

        # Check that equality of ranges matches equality of the corresponding
        # tuples dla each pair z the test lists above.
        ranges_eq = [a == b dla a w test_ranges dla b w test_ranges]
        tuples_eq = [a == b dla a w test_tuples dla b w test_tuples]
        self.assertEqual(ranges_eq, tuples_eq)

        # Check that != correctly gives the logical negation of ==
        ranges_ne = [a != b dla a w test_ranges dla b w test_ranges]
        self.assertEqual(ranges_ne, [not x dla x w ranges_eq])

        # Equal ranges should have equal hashes.
        dla a w test_ranges:
            dla b w test_ranges:
                jeżeli a == b:
                    self.assertEqual(hash(a), hash(b))

        # Ranges are unequal to other types (even sequence types)
        self.assertIs(range(0) == (), Nieprawda)
        self.assertIs(() == range(0), Nieprawda)
        self.assertIs(range(2) == [0, 1], Nieprawda)

        # Huge integers aren't a problem.
        self.assertEqual(range(0, 2**100 - 1, 2),
                         range(0, 2**100, 2))
        self.assertEqual(hash(range(0, 2**100 - 1, 2)),
                         hash(range(0, 2**100, 2)))
        self.assertNotEqual(range(0, 2**100, 2),
                            range(0, 2**100 + 1, 2))
        self.assertEqual(range(2**200, 2**201 - 2**99, 2**100),
                         range(2**200, 2**201, 2**100))
        self.assertEqual(hash(range(2**200, 2**201 - 2**99, 2**100)),
                         hash(range(2**200, 2**201, 2**100)))
        self.assertNotEqual(range(2**200, 2**201, 2**100),
                            range(2**200, 2**201 + 1, 2**100))

        # Order comparisons are nie implemented dla ranges.
        przy self.assertRaises(TypeError):
            range(0) < range(0)
        przy self.assertRaises(TypeError):
            range(0) > range(0)
        przy self.assertRaises(TypeError):
            range(0) <= range(0)
        przy self.assertRaises(TypeError):
            range(0) >= range(0)


    def test_attributes(self):
        # test the start, stop oraz step attributes of range objects
        self.assert_attrs(range(0), 0, 0, 1)
        self.assert_attrs(range(10), 0, 10, 1)
        self.assert_attrs(range(-10), 0, -10, 1)
        self.assert_attrs(range(0, 10, 1), 0, 10, 1)
        self.assert_attrs(range(0, 10, 3), 0, 10, 3)
        self.assert_attrs(range(10, 0, -1), 10, 0, -1)
        self.assert_attrs(range(10, 0, -3), 10, 0, -3)

    def assert_attrs(self, rangeobj, start, stop, step):
        self.assertEqual(rangeobj.start, start)
        self.assertEqual(rangeobj.stop, stop)
        self.assertEqual(rangeobj.step, step)

        przy self.assertRaises(AttributeError):
            rangeobj.start = 0
        przy self.assertRaises(AttributeError):
            rangeobj.stop = 10
        przy self.assertRaises(AttributeError):
            rangeobj.step = 1

        przy self.assertRaises(AttributeError):
            usuń rangeobj.start
        przy self.assertRaises(AttributeError):
            usuń rangeobj.stop
        przy self.assertRaises(AttributeError):
            usuń rangeobj.step

jeżeli __name__ == "__main__":
    unittest.main()
