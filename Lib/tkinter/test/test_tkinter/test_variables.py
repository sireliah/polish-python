zaimportuj unittest

z tkinter zaimportuj (Variable, StringVar, IntVar, DoubleVar, BooleanVar, Tcl,
                     TclError)


klasa Var(Variable):

    _default = "default"
    side_effect = Nieprawda

    def set(self, value):
        self.side_effect = Prawda
        super().set(value)


klasa TestBase(unittest.TestCase):

    def setUp(self):
        self.root = Tcl()

    def tearDown(self):
        usuń self.root


klasa TestVariable(TestBase):

    def info_exists(self, *args):
        zwróć self.root.getboolean(self.root.call("info", "exists", *args))

    def test_default(self):
        v = Variable(self.root)
        self.assertEqual("", v.get())
        self.assertRegex(str(v), r"^PY_VAR(\d+)$")

    def test_name_and_value(self):
        v = Variable(self.root, "sample string", "varname")
        self.assertEqual("sample string", v.get())
        self.assertEqual("varname", str(v))

    def test___del__(self):
        self.assertNieprawda(self.info_exists("varname"))
        v = Variable(self.root, "sample string", "varname")
        self.assertPrawda(self.info_exists("varname"))
        usuń v
        self.assertNieprawda(self.info_exists("varname"))

    def test_dont_unset_not_existing(self):
        self.assertNieprawda(self.info_exists("varname"))
        v1 = Variable(self.root, name="name")
        v2 = Variable(self.root, name="name")
        usuń v1
        self.assertNieprawda(self.info_exists("name"))
        # shouldn't podnieś exception
        usuń v2
        self.assertNieprawda(self.info_exists("name"))

    def test___eq__(self):
        # values doesn't matter, only klasa oraz name are checked
        v1 = Variable(self.root, name="abc")
        v2 = Variable(self.root, name="abc")
        self.assertEqual(v1, v2)

        v3 = Variable(self.root, name="abc")
        v4 = StringVar(self.root, name="abc")
        self.assertNotEqual(v3, v4)

    def test_invalid_name(self):
        przy self.assertRaises(TypeError):
            Variable(self.root, name=123)

    def test_null_in_name(self):
        przy self.assertRaises(ValueError):
            Variable(self.root, name='var\x00name')
        przy self.assertRaises(ValueError):
            self.root.globalsetvar('var\x00name', "value")
        przy self.assertRaises(ValueError):
            self.root.globalsetvar(b'var\x00name', "value")
        przy self.assertRaises(ValueError):
            self.root.setvar('var\x00name', "value")
        przy self.assertRaises(ValueError):
            self.root.setvar(b'var\x00name', "value")

    def test_initialize(self):
        v = Var(self.root)
        self.assertNieprawda(v.side_effect)
        v.set("value")
        self.assertPrawda(v.side_effect)


klasa TestStringVar(TestBase):

    def test_default(self):
        v = StringVar(self.root)
        self.assertEqual("", v.get())

    def test_get(self):
        v = StringVar(self.root, "abc", "name")
        self.assertEqual("abc", v.get())
        self.root.globalsetvar("name", "value")
        self.assertEqual("value", v.get())

    def test_get_null(self):
        v = StringVar(self.root, "abc\x00def", "name")
        self.assertEqual("abc\x00def", v.get())
        self.root.globalsetvar("name", "val\x00ue")
        self.assertEqual("val\x00ue", v.get())


klasa TestIntVar(TestBase):

    def test_default(self):
        v = IntVar(self.root)
        self.assertEqual(0, v.get())

    def test_get(self):
        v = IntVar(self.root, 123, "name")
        self.assertEqual(123, v.get())
        self.root.globalsetvar("name", "345")
        self.assertEqual(345, v.get())

    def test_invalid_value(self):
        v = IntVar(self.root, name="name")
        self.root.globalsetvar("name", "value")
        przy self.assertRaises((ValueError, TclError)):
            v.get()
        self.root.globalsetvar("name", "345.0")
        przy self.assertRaises((ValueError, TclError)):
            v.get()


klasa TestDoubleVar(TestBase):

    def test_default(self):
        v = DoubleVar(self.root)
        self.assertEqual(0.0, v.get())

    def test_get(self):
        v = DoubleVar(self.root, 1.23, "name")
        self.assertAlmostEqual(1.23, v.get())
        self.root.globalsetvar("name", "3.45")
        self.assertAlmostEqual(3.45, v.get())

    def test_get_from_int(self):
        v = DoubleVar(self.root, 1.23, "name")
        self.assertAlmostEqual(1.23, v.get())
        self.root.globalsetvar("name", "3.45")
        self.assertAlmostEqual(3.45, v.get())
        self.root.globalsetvar("name", "456")
        self.assertAlmostEqual(456, v.get())

    def test_invalid_value(self):
        v = DoubleVar(self.root, name="name")
        self.root.globalsetvar("name", "value")
        przy self.assertRaises((ValueError, TclError)):
            v.get()


klasa TestBooleanVar(TestBase):

    def test_default(self):
        v = BooleanVar(self.root)
        self.assertIs(v.get(), Nieprawda)

    def test_get(self):
        v = BooleanVar(self.root, Prawda, "name")
        self.assertIs(v.get(), Prawda)
        self.root.globalsetvar("name", "0")
        self.assertIs(v.get(), Nieprawda)
        self.root.globalsetvar("name", 42 jeżeli self.root.wantobjects() inaczej 1)
        self.assertIs(v.get(), Prawda)
        self.root.globalsetvar("name", 0)
        self.assertIs(v.get(), Nieprawda)
        self.root.globalsetvar("name", "on")
        self.assertIs(v.get(), Prawda)

    def test_set(self):
        true = 1 jeżeli self.root.wantobjects() inaczej "1"
        false = 0 jeżeli self.root.wantobjects() inaczej "0"
        v = BooleanVar(self.root, name="name")
        v.set(Prawda)
        self.assertEqual(self.root.globalgetvar("name"), true)
        v.set("0")
        self.assertEqual(self.root.globalgetvar("name"), false)
        v.set(42)
        self.assertEqual(self.root.globalgetvar("name"), true)
        v.set(0)
        self.assertEqual(self.root.globalgetvar("name"), false)
        v.set("on")
        self.assertEqual(self.root.globalgetvar("name"), true)

    def test_invalid_value_domain(self):
        false = 0 jeżeli self.root.wantobjects() inaczej "0"
        v = BooleanVar(self.root, name="name")
        przy self.assertRaises(TclError):
            v.set("value")
        self.assertEqual(self.root.globalgetvar("name"), false)
        self.root.globalsetvar("name", "value")
        przy self.assertRaises(ValueError):
            v.get()
        self.root.globalsetvar("name", "1.0")
        przy self.assertRaises(ValueError):
            v.get()


tests_gui = (TestVariable, TestStringVar, TestIntVar,
             TestDoubleVar, TestBooleanVar)


jeżeli __name__ == "__main__":
    z test.support zaimportuj run_unittest
    run_unittest(*tests_gui)
