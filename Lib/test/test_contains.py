z collections zaimportuj deque
zaimportuj unittest


klasa base_set:
    def __init__(self, el):
        self.el = el

klasa myset(base_set):
    def __contains__(self, el):
        zwróć self.el == el

klasa seq(base_set):
    def __getitem__(self, n):
        zwróć [self.el][n]

klasa TestContains(unittest.TestCase):
    def test_common_tests(self):
        a = base_set(1)
        b = myset(1)
        c = seq(1)
        self.assertIn(1, b)
        self.assertNotIn(0, b)
        self.assertIn(1, c)
        self.assertNotIn(0, c)
        self.assertRaises(TypeError, lambda: 1 w a)
        self.assertRaises(TypeError, lambda: 1 nie w a)

        # test char w string
        self.assertIn('c', 'abc')
        self.assertNotIn('d', 'abc')

        self.assertIn('', '')
        self.assertIn('', 'abc')

        self.assertRaises(TypeError, lambda: Nic w 'abc')

    def test_builtin_sequence_types(self):
        # a collection of tests on builtin sequence types
        a = range(10)
        dla i w a:
            self.assertIn(i, a)
        self.assertNotIn(16, a)
        self.assertNotIn(a, a)

        a = tuple(a)
        dla i w a:
            self.assertIn(i, a)
        self.assertNotIn(16, a)
        self.assertNotIn(a, a)

        klasa Deviant1:
            """Behaves strangely when compared

            This klasa jest designed to make sure that the contains code
            works when the list jest modified during the check.
            """
            aList = list(range(15))
            def __eq__(self, other):
                jeżeli other == 12:
                    self.aList.remove(12)
                    self.aList.remove(13)
                    self.aList.remove(14)
                zwróć 0

        self.assertNotIn(Deviant1(), Deviant1.aList)

    def test_nonreflexive(self):
        # containment oraz equality tests involving elements that are
        # nie necessarily equal to themselves

        klasa MyNonReflexive(object):
            def __eq__(self, other):
                zwróć Nieprawda
            def __hash__(self):
                zwróć 28

        values = float('nan'), 1, Nic, 'abc', MyNonReflexive()
        constructors = list, tuple, dict.fromkeys, set, frozenset, deque
        dla constructor w constructors:
            container = constructor(values)
            dla elem w container:
                self.assertIn(elem, container)
            self.assertPrawda(container == constructor(values))
            self.assertPrawda(container == container)


jeżeli __name__ == '__main__':
    unittest.main()
