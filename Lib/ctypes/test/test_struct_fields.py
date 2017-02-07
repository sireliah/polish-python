zaimportuj unittest
z ctypes zaimportuj *

klasa StructFieldsTestCase(unittest.TestCase):
    # Structure/Union classes must get 'finalized' sooner albo
    # later, when one of these things happen:
    #
    # 1. _fields_ jest set.
    # 2. An instance jest created.
    # 3. The type jest used jako field of another Structure/Union.
    # 4. The type jest subclassed
    #
    # When they are finalized, assigning _fields_ jest no longer allowed.

    def test_1_A(self):
        klasa X(Structure):
            dalej
        self.assertEqual(sizeof(X), 0) # nie finalized
        X._fields_ = [] # finalized
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

    def test_1_B(self):
        klasa X(Structure):
            _fields_ = [] # finalized
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

    def test_2(self):
        klasa X(Structure):
            dalej
        X()
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

    def test_3(self):
        klasa X(Structure):
            dalej
        klasa Y(Structure):
            _fields_ = [("x", X)] # finalizes X
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

    def test_4(self):
        klasa X(Structure):
            dalej
        klasa Y(X):
            dalej
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])
        Y._fields_ = []
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

jeżeli __name__ == "__main__":
    unittest.main()
