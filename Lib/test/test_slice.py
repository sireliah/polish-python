# tests dla slice objects; w particular the indices method.

zaimportuj unittest
z pickle zaimportuj loads, dumps

zaimportuj itertools
zaimportuj operator
zaimportuj sys


def evaluate_slice_index(arg):
    """
    Helper function to convert a slice argument to an integer, oraz podnieś
    TypeError przy a suitable message on failure.

    """
    jeżeli hasattr(arg, '__index__'):
        zwróć operator.index(arg)
    inaczej:
        podnieś TypeError(
            "slice indices must be integers albo "
            "Nic albo have an __index__ method")

def slice_indices(slice, length):
    """
    Reference implementation dla the slice.indices method.

    """
    # Compute step oraz length jako integers.
    length = operator.index(length)
    step = 1 jeżeli slice.step jest Nic inaczej evaluate_slice_index(slice.step)

    # Raise ValueError dla negative length albo zero step.
    jeżeli length < 0:
        podnieś ValueError("length should nie be negative")
    jeżeli step == 0:
        podnieś ValueError("slice step cannot be zero")

    # Find lower oraz upper bounds dla start oraz stop.
    lower = -1 jeżeli step < 0 inaczej 0
    upper = length - 1 jeżeli step < 0 inaczej length

    # Compute start.
    jeżeli slice.start jest Nic:
        start = upper jeżeli step < 0 inaczej lower
    inaczej:
        start = evaluate_slice_index(slice.start)
        start = max(start + length, lower) jeżeli start < 0 inaczej min(start, upper)

    # Compute stop.
    jeżeli slice.stop jest Nic:
        stop = lower jeżeli step < 0 inaczej upper
    inaczej:
        stop = evaluate_slice_index(slice.stop)
        stop = max(stop + length, lower) jeżeli stop < 0 inaczej min(stop, upper)

    zwróć start, stop, step


# Class providing an __index__ method.  Used dla testing slice.indices.

klasa MyIndexable(object):
    def __init__(self, value):
        self.value = value

    def __index__(self):
        zwróć self.value


klasa SliceTest(unittest.TestCase):

    def test_constructor(self):
        self.assertRaises(TypeError, slice)
        self.assertRaises(TypeError, slice, 1, 2, 3, 4)

    def test_repr(self):
        self.assertEqual(repr(slice(1, 2, 3)), "slice(1, 2, 3)")

    def test_hash(self):
        # Verify clearing of SF bug #800796
        self.assertRaises(TypeError, hash, slice(5))
        przy self.assertRaises(TypeError):
            slice(5).__hash__()

    def test_cmp(self):
        s1 = slice(1, 2, 3)
        s2 = slice(1, 2, 3)
        s3 = slice(1, 2, 4)
        self.assertEqual(s1, s2)
        self.assertNotEqual(s1, s3)
        self.assertNotEqual(s1, Nic)
        self.assertNotEqual(s1, (1, 2, 3))
        self.assertNotEqual(s1, "")

        klasa Exc(Exception):
            dalej

        klasa BadCmp(object):
            def __eq__(self, other):
                podnieś Exc

        s1 = slice(BadCmp())
        s2 = slice(BadCmp())
        self.assertEqual(s1, s1)
        self.assertRaises(Exc, lambda: s1 == s2)

        s1 = slice(1, BadCmp())
        s2 = slice(1, BadCmp())
        self.assertEqual(s1, s1)
        self.assertRaises(Exc, lambda: s1 == s2)

        s1 = slice(1, 2, BadCmp())
        s2 = slice(1, 2, BadCmp())
        self.assertEqual(s1, s1)
        self.assertRaises(Exc, lambda: s1 == s2)

    def test_members(self):
        s = slice(1)
        self.assertEqual(s.start, Nic)
        self.assertEqual(s.stop, 1)
        self.assertEqual(s.step, Nic)

        s = slice(1, 2)
        self.assertEqual(s.start, 1)
        self.assertEqual(s.stop, 2)
        self.assertEqual(s.step, Nic)

        s = slice(1, 2, 3)
        self.assertEqual(s.start, 1)
        self.assertEqual(s.stop, 2)
        self.assertEqual(s.step, 3)

        klasa AnyClass:
            dalej

        obj = AnyClass()
        s = slice(obj)
        self.assertPrawda(s.stop jest obj)

    def check_indices(self, slice, length):
        spróbuj:
            actual = slice.indices(length)
        wyjąwszy ValueError:
            actual = "valueerror"
        spróbuj:
            expected = slice_indices(slice, length)
        wyjąwszy ValueError:
            expected = "valueerror"
        self.assertEqual(actual, expected)

        jeżeli length >= 0 oraz slice.step != 0:
            actual = range(*slice.indices(length))
            expected = range(length)[slice]
            self.assertEqual(actual, expected)

    def test_indices(self):
        self.assertEqual(slice(Nic           ).indices(10), (0, 10,  1))
        self.assertEqual(slice(Nic,  Nic,  2).indices(10), (0, 10,  2))
        self.assertEqual(slice(1,     Nic,  2).indices(10), (1, 10,  2))
        self.assertEqual(slice(Nic,  Nic, -1).indices(10), (9, -1, -1))
        self.assertEqual(slice(Nic,  Nic, -2).indices(10), (9, -1, -2))
        self.assertEqual(slice(3,     Nic, -2).indices(10), (3, -1, -2))
        # issue 3004 tests
        self.assertEqual(slice(Nic, -9).indices(10), (0, 1, 1))
        self.assertEqual(slice(Nic, -10).indices(10), (0, 0, 1))
        self.assertEqual(slice(Nic, -11).indices(10), (0, 0, 1))
        self.assertEqual(slice(Nic, -10, -1).indices(10), (9, 0, -1))
        self.assertEqual(slice(Nic, -11, -1).indices(10), (9, -1, -1))
        self.assertEqual(slice(Nic, -12, -1).indices(10), (9, -1, -1))
        self.assertEqual(slice(Nic, 9).indices(10), (0, 9, 1))
        self.assertEqual(slice(Nic, 10).indices(10), (0, 10, 1))
        self.assertEqual(slice(Nic, 11).indices(10), (0, 10, 1))
        self.assertEqual(slice(Nic, 8, -1).indices(10), (9, 8, -1))
        self.assertEqual(slice(Nic, 9, -1).indices(10), (9, 9, -1))
        self.assertEqual(slice(Nic, 10, -1).indices(10), (9, 9, -1))

        self.assertEqual(
            slice(-100,  100     ).indices(10),
            slice(Nic).indices(10)
        )
        self.assertEqual(
            slice(100,  -100,  -1).indices(10),
            slice(Nic, Nic, -1).indices(10)
        )
        self.assertEqual(slice(-100, 100, 2).indices(10), (0, 10,  2))

        self.assertEqual(list(range(10))[::sys.maxsize - 1], [0])

        # Check a variety of start, stop, step oraz length values, including
        # values exceeding sys.maxsize (see issue #14794).
        vals = [Nic, -2**100, -2**30, -53, -7, -1, 0, 1, 7, 53, 2**30, 2**100]
        lengths = [0, 1, 7, 53, 2**30, 2**100]
        dla slice_args w itertools.product(vals, repeat=3):
            s = slice(*slice_args)
            dla length w lengths:
                self.check_indices(s, length)
        self.check_indices(slice(0, 10, 1), -3)

        # Negative length should podnieś ValueError
        przy self.assertRaises(ValueError):
            slice(Nic).indices(-1)

        # Zero step should podnieś ValueError
        przy self.assertRaises(ValueError):
            slice(0, 10, 0).indices(5)

        # Using a start, stop albo step albo length that can't be interpreted jako an
        # integer should give a TypeError ...
        przy self.assertRaises(TypeError):
            slice(0.0, 10, 1).indices(5)
        przy self.assertRaises(TypeError):
            slice(0, 10.0, 1).indices(5)
        przy self.assertRaises(TypeError):
            slice(0, 10, 1.0).indices(5)
        przy self.assertRaises(TypeError):
            slice(0, 10, 1).indices(5.0)

        # ... but it should be fine to use a custom klasa that provides index.
        self.assertEqual(slice(0, 10, 1).indices(5), (0, 5, 1))
        self.assertEqual(slice(MyIndexable(0), 10, 1).indices(5), (0, 5, 1))
        self.assertEqual(slice(0, MyIndexable(10), 1).indices(5), (0, 5, 1))
        self.assertEqual(slice(0, 10, MyIndexable(1)).indices(5), (0, 5, 1))
        self.assertEqual(slice(0, 10, 1).indices(MyIndexable(5)), (0, 5, 1))

    def test_setslice_without_getslice(self):
        tmp = []
        klasa X(object):
            def __setitem__(self, i, k):
                tmp.append((i, k))

        x = X()
        x[1:2] = 42
        self.assertEqual(tmp, [(slice(1, 2), 42)])

    def test_pickle(self):
        s = slice(10, 20, 3)
        dla protocol w (0,1,2):
            t = loads(dumps(s, protocol))
            self.assertEqual(s, t)
            self.assertEqual(s.indices(15), t.indices(15))
            self.assertNotEqual(id(s), id(t))

jeżeli __name__ == "__main__":
    unittest.main()
