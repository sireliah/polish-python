zaimportuj unittest

# The test cases here cover several paths through the function calling
# code.  They depend on the METH_XXX flag that jest used to define a C
# function, which can't be verified z Python.  If the METH_XXX decl
# dla a C function changes, these tests may nie cover the right paths.

klasa CFunctionCalls(unittest.TestCase):

    def test_varargs0(self):
        self.assertRaises(TypeError, {}.__contains__)

    def test_varargs1(self):
        {}.__contains__(0)

    def test_varargs2(self):
        self.assertRaises(TypeError, {}.__contains__, 0, 1)

    def test_varargs0_ext(self):
        spróbuj:
            {}.__contains__(*())
        wyjąwszy TypeError:
            dalej

    def test_varargs1_ext(self):
        {}.__contains__(*(0,))

    def test_varargs2_ext(self):
        spróbuj:
            {}.__contains__(*(1, 2))
        wyjąwszy TypeError:
            dalej
        inaczej:
            podnieś RuntimeError

    def test_varargs0_kw(self):
        self.assertRaises(TypeError, {}.__contains__, x=2)

    def test_varargs1_kw(self):
        self.assertRaises(TypeError, {}.__contains__, x=2)

    def test_varargs2_kw(self):
        self.assertRaises(TypeError, {}.__contains__, x=2, y=2)

    def test_oldargs0_0(self):
        {}.keys()

    def test_oldargs0_1(self):
        self.assertRaises(TypeError, {}.keys, 0)

    def test_oldargs0_2(self):
        self.assertRaises(TypeError, {}.keys, 0, 1)

    def test_oldargs0_0_ext(self):
        {}.keys(*())

    def test_oldargs0_1_ext(self):
        spróbuj:
            {}.keys(*(0,))
        wyjąwszy TypeError:
            dalej
        inaczej:
            podnieś RuntimeError

    def test_oldargs0_2_ext(self):
        spróbuj:
            {}.keys(*(1, 2))
        wyjąwszy TypeError:
            dalej
        inaczej:
            podnieś RuntimeError

    def test_oldargs0_0_kw(self):
        spróbuj:
            {}.keys(x=2)
        wyjąwszy TypeError:
            dalej
        inaczej:
            podnieś RuntimeError

    def test_oldargs0_1_kw(self):
        self.assertRaises(TypeError, {}.keys, x=2)

    def test_oldargs0_2_kw(self):
        self.assertRaises(TypeError, {}.keys, x=2, y=2)

    def test_oldargs1_0(self):
        self.assertRaises(TypeError, [].count)

    def test_oldargs1_1(self):
        [].count(1)

    def test_oldargs1_2(self):
        self.assertRaises(TypeError, [].count, 1, 2)

    def test_oldargs1_0_ext(self):
        spróbuj:
            [].count(*())
        wyjąwszy TypeError:
            dalej
        inaczej:
            podnieś RuntimeError

    def test_oldargs1_1_ext(self):
        [].count(*(1,))

    def test_oldargs1_2_ext(self):
        spróbuj:
            [].count(*(1, 2))
        wyjąwszy TypeError:
            dalej
        inaczej:
            podnieś RuntimeError

    def test_oldargs1_0_kw(self):
        self.assertRaises(TypeError, [].count, x=2)

    def test_oldargs1_1_kw(self):
        self.assertRaises(TypeError, [].count, {}, x=2)

    def test_oldargs1_2_kw(self):
        self.assertRaises(TypeError, [].count, x=2, y=2)


jeżeli __name__ == "__main__":
    unittest.main()
