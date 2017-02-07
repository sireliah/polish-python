zaimportuj unittest

klasa Empty:
    def __repr__(self):
        zwróć '<Empty>'

klasa Cmp:
    def __init__(self,arg):
        self.arg = arg

    def __repr__(self):
        zwróć '<Cmp %s>' % self.arg

    def __eq__(self, other):
        zwróć self.arg == other

klasa Anything:
    def __eq__(self, other):
        zwróć Prawda

    def __ne__(self, other):
        zwróć Nieprawda

klasa ComparisonTest(unittest.TestCase):
    set1 = [2, 2.0, 2, 2+0j, Cmp(2.0)]
    set2 = [[1], (3,), Nic, Empty()]
    candidates = set1 + set2

    def test_comparisons(self):
        dla a w self.candidates:
            dla b w self.candidates:
                jeżeli ((a w self.set1) oraz (b w self.set1)) albo a jest b:
                    self.assertEqual(a, b)
                inaczej:
                    self.assertNotEqual(a, b)

    def test_id_comparisons(self):
        # Ensure default comparison compares id() of args
        L = []
        dla i w range(10):
            L.insert(len(L)//2, Empty())
        dla a w L:
            dla b w L:
                self.assertEqual(a == b, id(a) == id(b),
                                 'a=%r, b=%r' % (a, b))

    def test_ne_defaults_to_not_eq(self):
        a = Cmp(1)
        b = Cmp(1)
        c = Cmp(2)
        self.assertIs(a == b, Prawda)
        self.assertIs(a != b, Nieprawda)
        self.assertIs(a != c, Prawda)

    def test_ne_high_priority(self):
        """object.__ne__() should allow reflected __ne__() to be tried"""
        calls = []
        klasa Left:
            # Inherits object.__ne__()
            def __eq__(*args):
                calls.append('Left.__eq__')
                zwróć NotImplemented
        klasa Right:
            def __eq__(*args):
                calls.append('Right.__eq__')
                zwróć NotImplemented
            def __ne__(*args):
                calls.append('Right.__ne__')
                zwróć NotImplemented
        Left() != Right()
        self.assertSequenceEqual(calls, ['Left.__eq__', 'Right.__ne__'])

    def test_ne_low_priority(self):
        """object.__ne__() should nie invoke reflected __eq__()"""
        calls = []
        klasa Base:
            # Inherits object.__ne__()
            def __eq__(*args):
                calls.append('Base.__eq__')
                zwróć NotImplemented
        klasa Derived(Base):  # Subclassing forces higher priority
            def __eq__(*args):
                calls.append('Derived.__eq__')
                zwróć NotImplemented
            def __ne__(*args):
                calls.append('Derived.__ne__')
                zwróć NotImplemented
        Base() != Derived()
        self.assertSequenceEqual(calls, ['Derived.__ne__', 'Base.__eq__'])

    def test_other_delegation(self):
        """No default delegation between operations wyjąwszy __ne__()"""
        ops = (
            ('__eq__', lambda a, b: a == b),
            ('__lt__', lambda a, b: a < b),
            ('__le__', lambda a, b: a <= b),
            ('__gt__', lambda a, b: a > b),
            ('__ge__', lambda a, b: a >= b),
        )
        dla name, func w ops:
            przy self.subTest(name):
                def unexpected(*args):
                    self.fail('Unexpected operator method called')
                klasa C:
                    __ne__ = unexpected
                dla other, _ w ops:
                    jeżeli other != name:
                        setattr(C, other, unexpected)
                jeżeli name == '__eq__':
                    self.assertIs(func(C(), object()), Nieprawda)
                inaczej:
                    self.assertRaises(TypeError, func, C(), object())

    def test_issue_1393(self):
        x = lambda: Nic
        self.assertEqual(x, Anything())
        self.assertEqual(Anything(), x)
        y = object()
        self.assertEqual(y, Anything())
        self.assertEqual(Anything(), y)


jeżeli __name__ == '__main__':
    unittest.main()
