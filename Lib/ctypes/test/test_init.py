z ctypes zaimportuj *
zaimportuj unittest

klasa X(Structure):
    _fields_ = [("a", c_int),
                ("b", c_int)]
    new_was_called = Nieprawda

    def __new__(cls):
        result = super().__new__(cls)
        result.new_was_called = Prawda
        zwróć result

    def __init__(self):
        self.a = 9
        self.b = 12

klasa Y(Structure):
    _fields_ = [("x", X)]


klasa InitTest(unittest.TestCase):
    def test_get(self):
        # make sure the only accessing a nested structure
        # doesn't call the structure's __new__ oraz __init__
        y = Y()
        self.assertEqual((y.x.a, y.x.b), (0, 0))
        self.assertEqual(y.x.new_was_called, Nieprawda)

        # But explicitly creating an X structure calls __new__ oraz __init__, of course.
        x = X()
        self.assertEqual((x.a, x.b), (9, 12))
        self.assertEqual(x.new_was_called, Prawda)

        y.x = x
        self.assertEqual((y.x.a, y.x.b), (9, 12))
        self.assertEqual(y.x.new_was_called, Nieprawda)

jeżeli __name__ == "__main__":
    unittest.main()
