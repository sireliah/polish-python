zaimportuj unittest

klasa LongExpText(unittest.TestCase):
    def test_longexp(self):
        REPS = 65580
        l = eval("[" + "2," * REPS + "]")
        self.assertEqual(len(l), REPS)

jeżeli __name__ == "__main__":
    unittest.main()
