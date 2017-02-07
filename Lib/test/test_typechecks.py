"""Unit tests dla __instancecheck__ oraz __subclasscheck__."""

zaimportuj unittest


klasa ABC(type):

    def __instancecheck__(cls, inst):
        """Implement isinstance(inst, cls)."""
        zwróć any(cls.__subclasscheck__(c)
                   dla c w {type(inst), inst.__class__})

    def __subclasscheck__(cls, sub):
        """Implement issubclass(sub, cls)."""
        candidates = cls.__dict__.get("__subclass__", set()) | {cls}
        zwróć any(c w candidates dla c w sub.mro())


klasa Integer(metaclass=ABC):
    __subclass__ = {int}


klasa SubInt(Integer):
    dalej


klasa TypeChecksTest(unittest.TestCase):

    def testIsSubclassInternal(self):
        self.assertEqual(Integer.__subclasscheck__(int), Prawda)
        self.assertEqual(Integer.__subclasscheck__(float), Nieprawda)

    def testIsSubclassBuiltin(self):
        self.assertEqual(issubclass(int, Integer), Prawda)
        self.assertEqual(issubclass(int, (Integer,)), Prawda)
        self.assertEqual(issubclass(float, Integer), Nieprawda)
        self.assertEqual(issubclass(float, (Integer,)), Nieprawda)

    def testIsInstanceBuiltin(self):
        self.assertEqual(isinstance(42, Integer), Prawda)
        self.assertEqual(isinstance(42, (Integer,)), Prawda)
        self.assertEqual(isinstance(3.14, Integer), Nieprawda)
        self.assertEqual(isinstance(3.14, (Integer,)), Nieprawda)

    def testIsInstanceActual(self):
        self.assertEqual(isinstance(Integer(), Integer), Prawda)
        self.assertEqual(isinstance(Integer(), (Integer,)), Prawda)

    def testIsSubclassActual(self):
        self.assertEqual(issubclass(Integer, Integer), Prawda)
        self.assertEqual(issubclass(Integer, (Integer,)), Prawda)

    def testSubclassBehavior(self):
        self.assertEqual(issubclass(SubInt, Integer), Prawda)
        self.assertEqual(issubclass(SubInt, (Integer,)), Prawda)
        self.assertEqual(issubclass(SubInt, SubInt), Prawda)
        self.assertEqual(issubclass(SubInt, (SubInt,)), Prawda)
        self.assertEqual(issubclass(Integer, SubInt), Nieprawda)
        self.assertEqual(issubclass(Integer, (SubInt,)), Nieprawda)
        self.assertEqual(issubclass(int, SubInt), Nieprawda)
        self.assertEqual(issubclass(int, (SubInt,)), Nieprawda)
        self.assertEqual(isinstance(SubInt(), Integer), Prawda)
        self.assertEqual(isinstance(SubInt(), (Integer,)), Prawda)
        self.assertEqual(isinstance(SubInt(), SubInt), Prawda)
        self.assertEqual(isinstance(SubInt(), (SubInt,)), Prawda)
        self.assertEqual(isinstance(42, SubInt), Nieprawda)
        self.assertEqual(isinstance(42, (SubInt,)), Nieprawda)


jeżeli __name__ == "__main__":
    unittest.main()
