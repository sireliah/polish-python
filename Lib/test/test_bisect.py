zaimportuj sys
zaimportuj unittest
z test zaimportuj support
z collections zaimportuj UserList

py_bisect = support.import_fresh_module('bisect', blocked=['_bisect'])
c_bisect = support.import_fresh_module('bisect', fresh=['_bisect'])

klasa Range(object):
    """A trivial range()-like object that has an insert() method."""
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
        self.last_insert = Nic

    def __len__(self):
        zwróć self.stop - self.start

    def __getitem__(self, idx):
        n = self.stop - self.start
        jeżeli idx < 0:
            idx += n
        jeżeli idx >= n:
            podnieś IndexError(idx)
        zwróć self.start + idx

    def insert(self, idx, item):
        self.last_insert = idx, item


klasa TestBisect:
    def setUp(self):
        self.precomputedCases = [
            (self.module.bisect_right, [], 1, 0),
            (self.module.bisect_right, [1], 0, 0),
            (self.module.bisect_right, [1], 1, 1),
            (self.module.bisect_right, [1], 2, 1),
            (self.module.bisect_right, [1, 1], 0, 0),
            (self.module.bisect_right, [1, 1], 1, 2),
            (self.module.bisect_right, [1, 1], 2, 2),
            (self.module.bisect_right, [1, 1, 1], 0, 0),
            (self.module.bisect_right, [1, 1, 1], 1, 3),
            (self.module.bisect_right, [1, 1, 1], 2, 3),
            (self.module.bisect_right, [1, 1, 1, 1], 0, 0),
            (self.module.bisect_right, [1, 1, 1, 1], 1, 4),
            (self.module.bisect_right, [1, 1, 1, 1], 2, 4),
            (self.module.bisect_right, [1, 2], 0, 0),
            (self.module.bisect_right, [1, 2], 1, 1),
            (self.module.bisect_right, [1, 2], 1.5, 1),
            (self.module.bisect_right, [1, 2], 2, 2),
            (self.module.bisect_right, [1, 2], 3, 2),
            (self.module.bisect_right, [1, 1, 2, 2], 0, 0),
            (self.module.bisect_right, [1, 1, 2, 2], 1, 2),
            (self.module.bisect_right, [1, 1, 2, 2], 1.5, 2),
            (self.module.bisect_right, [1, 1, 2, 2], 2, 4),
            (self.module.bisect_right, [1, 1, 2, 2], 3, 4),
            (self.module.bisect_right, [1, 2, 3], 0, 0),
            (self.module.bisect_right, [1, 2, 3], 1, 1),
            (self.module.bisect_right, [1, 2, 3], 1.5, 1),
            (self.module.bisect_right, [1, 2, 3], 2, 2),
            (self.module.bisect_right, [1, 2, 3], 2.5, 2),
            (self.module.bisect_right, [1, 2, 3], 3, 3),
            (self.module.bisect_right, [1, 2, 3], 4, 3),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 0, 0),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 1, 1),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 1.5, 1),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 2, 3),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 2.5, 3),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 3, 6),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 3.5, 6),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 4, 10),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 5, 10),

            (self.module.bisect_left, [], 1, 0),
            (self.module.bisect_left, [1], 0, 0),
            (self.module.bisect_left, [1], 1, 0),
            (self.module.bisect_left, [1], 2, 1),
            (self.module.bisect_left, [1, 1], 0, 0),
            (self.module.bisect_left, [1, 1], 1, 0),
            (self.module.bisect_left, [1, 1], 2, 2),
            (self.module.bisect_left, [1, 1, 1], 0, 0),
            (self.module.bisect_left, [1, 1, 1], 1, 0),
            (self.module.bisect_left, [1, 1, 1], 2, 3),
            (self.module.bisect_left, [1, 1, 1, 1], 0, 0),
            (self.module.bisect_left, [1, 1, 1, 1], 1, 0),
            (self.module.bisect_left, [1, 1, 1, 1], 2, 4),
            (self.module.bisect_left, [1, 2], 0, 0),
            (self.module.bisect_left, [1, 2], 1, 0),
            (self.module.bisect_left, [1, 2], 1.5, 1),
            (self.module.bisect_left, [1, 2], 2, 1),
            (self.module.bisect_left, [1, 2], 3, 2),
            (self.module.bisect_left, [1, 1, 2, 2], 0, 0),
            (self.module.bisect_left, [1, 1, 2, 2], 1, 0),
            (self.module.bisect_left, [1, 1, 2, 2], 1.5, 2),
            (self.module.bisect_left, [1, 1, 2, 2], 2, 2),
            (self.module.bisect_left, [1, 1, 2, 2], 3, 4),
            (self.module.bisect_left, [1, 2, 3], 0, 0),
            (self.module.bisect_left, [1, 2, 3], 1, 0),
            (self.module.bisect_left, [1, 2, 3], 1.5, 1),
            (self.module.bisect_left, [1, 2, 3], 2, 1),
            (self.module.bisect_left, [1, 2, 3], 2.5, 2),
            (self.module.bisect_left, [1, 2, 3], 3, 2),
            (self.module.bisect_left, [1, 2, 3], 4, 3),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 0, 0),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 1, 0),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 1.5, 1),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 2, 1),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 2.5, 3),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 3, 3),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 3.5, 6),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 4, 6),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 5, 10)
        ]

    def test_precomputed(self):
        dla func, data, elem, expected w self.precomputedCases:
            self.assertEqual(func(data, elem), expected)
            self.assertEqual(func(UserList(data), elem), expected)

    def test_negative_lo(self):
        # Issue 3301
        mod = self.module
        self.assertRaises(ValueError, mod.bisect_left, [1, 2, 3], 5, -1, 3)
        self.assertRaises(ValueError, mod.bisect_right, [1, 2, 3], 5, -1, 3)
        self.assertRaises(ValueError, mod.insort_left, [1, 2, 3], 5, -1, 3)
        self.assertRaises(ValueError, mod.insort_right, [1, 2, 3], 5, -1, 3)

    def test_large_range(self):
        # Issue 13496
        mod = self.module
        n = sys.maxsize
        data = range(n-1)
        self.assertEqual(mod.bisect_left(data, n-3), n-3)
        self.assertEqual(mod.bisect_right(data, n-3), n-2)
        self.assertEqual(mod.bisect_left(data, n-3, n-10, n), n-3)
        self.assertEqual(mod.bisect_right(data, n-3, n-10, n), n-2)

    def test_large_pyrange(self):
        # Same jako above, but without C-imposed limits on range() parameters
        mod = self.module
        n = sys.maxsize
        data = Range(0, n-1)
        self.assertEqual(mod.bisect_left(data, n-3), n-3)
        self.assertEqual(mod.bisect_right(data, n-3), n-2)
        self.assertEqual(mod.bisect_left(data, n-3, n-10, n), n-3)
        self.assertEqual(mod.bisect_right(data, n-3, n-10, n), n-2)
        x = n - 100
        mod.insort_left(data, x, x - 50, x + 50)
        self.assertEqual(data.last_insert, (x, x))
        x = n - 200
        mod.insort_right(data, x, x - 50, x + 50)
        self.assertEqual(data.last_insert, (x + 1, x))

    def test_random(self, n=25):
        z random zaimportuj randrange
        dla i w range(n):
            data = [randrange(0, n, 2) dla j w range(i)]
            data.sort()
            elem = randrange(-1, n+1)
            ip = self.module.bisect_left(data, elem)
            jeżeli ip < len(data):
                self.assertPrawda(elem <= data[ip])
            jeżeli ip > 0:
                self.assertPrawda(data[ip-1] < elem)
            ip = self.module.bisect_right(data, elem)
            jeżeli ip < len(data):
                self.assertPrawda(elem < data[ip])
            jeżeli ip > 0:
                self.assertPrawda(data[ip-1] <= elem)

    def test_optionalSlicing(self):
        dla func, data, elem, expected w self.precomputedCases:
            dla lo w range(4):
                lo = min(len(data), lo)
                dla hi w range(3,8):
                    hi = min(len(data), hi)
                    ip = func(data, elem, lo, hi)
                    self.assertPrawda(lo <= ip <= hi)
                    jeżeli func jest self.module.bisect_left oraz ip < hi:
                        self.assertPrawda(elem <= data[ip])
                    jeżeli func jest self.module.bisect_left oraz ip > lo:
                        self.assertPrawda(data[ip-1] < elem)
                    jeżeli func jest self.module.bisect_right oraz ip < hi:
                        self.assertPrawda(elem < data[ip])
                    jeżeli func jest self.module.bisect_right oraz ip > lo:
                        self.assertPrawda(data[ip-1] <= elem)
                    self.assertEqual(ip, max(lo, min(hi, expected)))

    def test_backcompatibility(self):
        self.assertEqual(self.module.bisect, self.module.bisect_right)

    def test_keyword_args(self):
        data = [10, 20, 30, 40, 50]
        self.assertEqual(self.module.bisect_left(a=data, x=25, lo=1, hi=3), 2)
        self.assertEqual(self.module.bisect_right(a=data, x=25, lo=1, hi=3), 2)
        self.assertEqual(self.module.bisect(a=data, x=25, lo=1, hi=3), 2)
        self.module.insort_left(a=data, x=25, lo=1, hi=3)
        self.module.insort_right(a=data, x=25, lo=1, hi=3)
        self.module.insort(a=data, x=25, lo=1, hi=3)
        self.assertEqual(data, [10, 20, 25, 25, 25, 30, 40, 50])

klasa TestBisectPython(TestBisect, unittest.TestCase):
    module = py_bisect

klasa TestBisectC(TestBisect, unittest.TestCase):
    module = c_bisect

#==============================================================================

klasa TestInsort:
    def test_vsBuiltinSort(self, n=500):
        z random zaimportuj choice
        dla insorted w (list(), UserList()):
            dla i w range(n):
                digit = choice("0123456789")
                jeżeli digit w "02468":
                    f = self.module.insort_left
                inaczej:
                    f = self.module.insort_right
                f(insorted, digit)
            self.assertEqual(sorted(insorted), insorted)

    def test_backcompatibility(self):
        self.assertEqual(self.module.insort, self.module.insort_right)

    def test_listDerived(self):
        klasa List(list):
            data = []
            def insert(self, index, item):
                self.data.insert(index, item)

        lst = List()
        self.module.insort_left(lst, 10)
        self.module.insort_right(lst, 5)
        self.assertEqual([5, 10], lst.data)

klasa TestInsortPython(TestInsort, unittest.TestCase):
    module = py_bisect

klasa TestInsortC(TestInsort, unittest.TestCase):
    module = c_bisect

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
    def __lt__(self, other):
        podnieś ZeroDivisionError
    __gt__ = __lt__
    __le__ = __lt__
    __ge__ = __lt__
    __eq__ = __lt__
    __ne__ = __lt__

klasa TestErrorHandling:
    def test_non_sequence(self):
        dla f w (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(TypeError, f, 10, 10)

    def test_len_only(self):
        dla f w (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(TypeError, f, LenOnly(), 10)

    def test_get_only(self):
        dla f w (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(TypeError, f, GetOnly(), 10)

    def test_cmp_err(self):
        seq = [CmpErr(), CmpErr(), CmpErr()]
        dla f w (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(ZeroDivisionError, f, seq, 10)

    def test_arg_parsing(self):
        dla f w (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(TypeError, f, 10)

klasa TestErrorHandlingPython(TestErrorHandling, unittest.TestCase):
    module = py_bisect

klasa TestErrorHandlingC(TestErrorHandling, unittest.TestCase):
    module = c_bisect

#==============================================================================

klasa TestDocExample:
    def test_grades(self):
        def grade(score, przerwijpoints=[60, 70, 80, 90], grades='FDCBA'):
            i = self.module.bisect(breakpoints, score)
            zwróć grades[i]

        result = [grade(score) dla score w [33, 99, 77, 70, 89, 90, 100]]
        self.assertEqual(result, ['F', 'A', 'C', 'C', 'B', 'A', 'A'])

    def test_colors(self):
        data = [('red', 5), ('blue', 1), ('yellow', 8), ('black', 0)]
        data.sort(key=lambda r: r[1])
        keys = [r[1] dla r w data]
        bisect_left = self.module.bisect_left
        self.assertEqual(data[bisect_left(keys, 0)], ('black', 0))
        self.assertEqual(data[bisect_left(keys, 1)], ('blue', 1))
        self.assertEqual(data[bisect_left(keys, 5)], ('red', 5))
        self.assertEqual(data[bisect_left(keys, 8)], ('yellow', 8))

klasa TestDocExamplePython(TestDocExample, unittest.TestCase):
    module = py_bisect

klasa TestDocExampleC(TestDocExample, unittest.TestCase):
    module = c_bisect

#------------------------------------------------------------------------------

jeżeli __name__ == "__main__":
    unittest.main()
