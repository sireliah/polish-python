zaimportuj unittest

z test zaimportuj support

# For scope testing.
g = "Global variable"


klasa DictComprehensionTest(unittest.TestCase):

    def test_basics(self):
        expected = {0: 10, 1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17,
                    8: 18, 9: 19}
        actual = {k: k + 10 dla k w range(10)}
        self.assertEqual(actual, expected)

        expected = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}
        actual = {k: v dla k w range(10) dla v w range(10) jeżeli k == v}
        self.assertEqual(actual, expected)

    def test_scope_isolation(self):
        k = "Local Variable"

        expected = {0: Nic, 1: Nic, 2: Nic, 3: Nic, 4: Nic, 5: Nic,
                    6: Nic, 7: Nic, 8: Nic, 9: Nic}
        actual = {k: Nic dla k w range(10)}
        self.assertEqual(actual, expected)
        self.assertEqual(k, "Local Variable")

        expected = {9: 1, 18: 2, 19: 2, 27: 3, 28: 3, 29: 3, 36: 4, 37: 4,
                    38: 4, 39: 4, 45: 5, 46: 5, 47: 5, 48: 5, 49: 5, 54: 6,
                    55: 6, 56: 6, 57: 6, 58: 6, 59: 6, 63: 7, 64: 7, 65: 7,
                    66: 7, 67: 7, 68: 7, 69: 7, 72: 8, 73: 8, 74: 8, 75: 8,
                    76: 8, 77: 8, 78: 8, 79: 8, 81: 9, 82: 9, 83: 9, 84: 9,
                    85: 9, 86: 9, 87: 9, 88: 9, 89: 9}
        actual = {k: v dla v w range(10) dla k w range(v * 9, v * 10)}
        self.assertEqual(k, "Local Variable")
        self.assertEqual(actual, expected)

    def test_scope_isolation_from_global(self):
        expected = {0: Nic, 1: Nic, 2: Nic, 3: Nic, 4: Nic, 5: Nic,
                    6: Nic, 7: Nic, 8: Nic, 9: Nic}
        actual = {g: Nic dla g w range(10)}
        self.assertEqual(actual, expected)
        self.assertEqual(g, "Global variable")

        expected = {9: 1, 18: 2, 19: 2, 27: 3, 28: 3, 29: 3, 36: 4, 37: 4,
                    38: 4, 39: 4, 45: 5, 46: 5, 47: 5, 48: 5, 49: 5, 54: 6,
                    55: 6, 56: 6, 57: 6, 58: 6, 59: 6, 63: 7, 64: 7, 65: 7,
                    66: 7, 67: 7, 68: 7, 69: 7, 72: 8, 73: 8, 74: 8, 75: 8,
                    76: 8, 77: 8, 78: 8, 79: 8, 81: 9, 82: 9, 83: 9, 84: 9,
                    85: 9, 86: 9, 87: 9, 88: 9, 89: 9}
        actual = {g: v dla v w range(10) dla g w range(v * 9, v * 10)}
        self.assertEqual(g, "Global variable")
        self.assertEqual(actual, expected)

    def test_global_visibility(self):
        expected = {0: 'Global variable', 1: 'Global variable',
                    2: 'Global variable', 3: 'Global variable',
                    4: 'Global variable', 5: 'Global variable',
                    6: 'Global variable', 7: 'Global variable',
                    8: 'Global variable', 9: 'Global variable'}
        actual = {k: g dla k w range(10)}
        self.assertEqual(actual, expected)

    def test_local_visibility(self):
        v = "Local variable"
        expected = {0: 'Local variable', 1: 'Local variable',
                    2: 'Local variable', 3: 'Local variable',
                    4: 'Local variable', 5: 'Local variable',
                    6: 'Local variable', 7: 'Local variable',
                    8: 'Local variable', 9: 'Local variable'}
        actual = {k: v dla k w range(10)}
        self.assertEqual(actual, expected)
        self.assertEqual(v, "Local variable")

    def test_illegal_assignment(self):
        przy self.assertRaisesRegex(SyntaxError, "can't assign"):
            compile("{x: y dla y, x w ((1, 2), (3, 4))} = 5", "<test>",
                    "exec")

        przy self.assertRaisesRegex(SyntaxError, "can't assign"):
            compile("{x: y dla y, x w ((1, 2), (3, 4))} += 5", "<test>",
                    "exec")


jeżeli __name__ == "__main__":
    unittest.main()
