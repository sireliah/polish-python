# Test properties of bool promised by PEP 285

zaimportuj unittest
z test zaimportuj support

zaimportuj os

klasa BoolTest(unittest.TestCase):

    def test_subclass(self):
        spróbuj:
            klasa C(bool):
                dalej
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("bool should nie be subclassable")

        self.assertRaises(TypeError, int.__new__, bool, 0)

    def test_print(self):
        spróbuj:
            fo = open(support.TESTFN, "w")
            print(Nieprawda, Prawda, file=fo)
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), 'Nieprawda Prawda\n')
        w_końcu:
            fo.close()
            os.remove(support.TESTFN)

    def test_repr(self):
        self.assertEqual(repr(Nieprawda), 'Nieprawda')
        self.assertEqual(repr(Prawda), 'Prawda')
        self.assertEqual(eval(repr(Nieprawda)), Nieprawda)
        self.assertEqual(eval(repr(Prawda)), Prawda)

    def test_str(self):
        self.assertEqual(str(Nieprawda), 'Nieprawda')
        self.assertEqual(str(Prawda), 'Prawda')

    def test_int(self):
        self.assertEqual(int(Nieprawda), 0)
        self.assertIsNot(int(Nieprawda), Nieprawda)
        self.assertEqual(int(Prawda), 1)
        self.assertIsNot(int(Prawda), Prawda)

    def test_float(self):
        self.assertEqual(float(Nieprawda), 0.0)
        self.assertIsNot(float(Nieprawda), Nieprawda)
        self.assertEqual(float(Prawda), 1.0)
        self.assertIsNot(float(Prawda), Prawda)

    def test_math(self):
        self.assertEqual(+Nieprawda, 0)
        self.assertIsNot(+Nieprawda, Nieprawda)
        self.assertEqual(-Nieprawda, 0)
        self.assertIsNot(-Nieprawda, Nieprawda)
        self.assertEqual(abs(Nieprawda), 0)
        self.assertIsNot(abs(Nieprawda), Nieprawda)
        self.assertEqual(+Prawda, 1)
        self.assertIsNot(+Prawda, Prawda)
        self.assertEqual(-Prawda, -1)
        self.assertEqual(abs(Prawda), 1)
        self.assertIsNot(abs(Prawda), Prawda)
        self.assertEqual(~Nieprawda, -1)
        self.assertEqual(~Prawda, -2)

        self.assertEqual(Nieprawda+2, 2)
        self.assertEqual(Prawda+2, 3)
        self.assertEqual(2+Nieprawda, 2)
        self.assertEqual(2+Prawda, 3)

        self.assertEqual(Nieprawda+Nieprawda, 0)
        self.assertIsNot(Nieprawda+Nieprawda, Nieprawda)
        self.assertEqual(Nieprawda+Prawda, 1)
        self.assertIsNot(Nieprawda+Prawda, Prawda)
        self.assertEqual(Prawda+Nieprawda, 1)
        self.assertIsNot(Prawda+Nieprawda, Prawda)
        self.assertEqual(Prawda+Prawda, 2)

        self.assertEqual(Prawda-Prawda, 0)
        self.assertIsNot(Prawda-Prawda, Nieprawda)
        self.assertEqual(Nieprawda-Nieprawda, 0)
        self.assertIsNot(Nieprawda-Nieprawda, Nieprawda)
        self.assertEqual(Prawda-Nieprawda, 1)
        self.assertIsNot(Prawda-Nieprawda, Prawda)
        self.assertEqual(Nieprawda-Prawda, -1)

        self.assertEqual(Prawda*1, 1)
        self.assertEqual(Nieprawda*1, 0)
        self.assertIsNot(Nieprawda*1, Nieprawda)

        self.assertEqual(Prawda/1, 1)
        self.assertIsNot(Prawda/1, Prawda)
        self.assertEqual(Nieprawda/1, 0)
        self.assertIsNot(Nieprawda/1, Nieprawda)

        dla b w Nieprawda, Prawda:
            dla i w 0, 1, 2:
                self.assertEqual(b**i, int(b)**i)
                self.assertIsNot(b**i, bool(int(b)**i))

        dla a w Nieprawda, Prawda:
            dla b w Nieprawda, Prawda:
                self.assertIs(a&b, bool(int(a)&int(b)))
                self.assertIs(a|b, bool(int(a)|int(b)))
                self.assertIs(a^b, bool(int(a)^int(b)))
                self.assertEqual(a&int(b), int(a)&int(b))
                self.assertIsNot(a&int(b), bool(int(a)&int(b)))
                self.assertEqual(a|int(b), int(a)|int(b))
                self.assertIsNot(a|int(b), bool(int(a)|int(b)))
                self.assertEqual(a^int(b), int(a)^int(b))
                self.assertIsNot(a^int(b), bool(int(a)^int(b)))
                self.assertEqual(int(a)&b, int(a)&int(b))
                self.assertIsNot(int(a)&b, bool(int(a)&int(b)))
                self.assertEqual(int(a)|b, int(a)|int(b))
                self.assertIsNot(int(a)|b, bool(int(a)|int(b)))
                self.assertEqual(int(a)^b, int(a)^int(b))
                self.assertIsNot(int(a)^b, bool(int(a)^int(b)))

        self.assertIs(1==1, Prawda)
        self.assertIs(1==0, Nieprawda)
        self.assertIs(0<1, Prawda)
        self.assertIs(1<0, Nieprawda)
        self.assertIs(0<=0, Prawda)
        self.assertIs(1<=0, Nieprawda)
        self.assertIs(1>0, Prawda)
        self.assertIs(1>1, Nieprawda)
        self.assertIs(1>=1, Prawda)
        self.assertIs(0>=1, Nieprawda)
        self.assertIs(0!=1, Prawda)
        self.assertIs(0!=0, Nieprawda)

        x = [1]
        self.assertIs(x jest x, Prawda)
        self.assertIs(x jest nie x, Nieprawda)

        self.assertIs(1 w x, Prawda)
        self.assertIs(0 w x, Nieprawda)
        self.assertIs(1 nie w x, Nieprawda)
        self.assertIs(0 nie w x, Prawda)

        x = {1: 2}
        self.assertIs(x jest x, Prawda)
        self.assertIs(x jest nie x, Nieprawda)

        self.assertIs(1 w x, Prawda)
        self.assertIs(0 w x, Nieprawda)
        self.assertIs(1 nie w x, Nieprawda)
        self.assertIs(0 nie w x, Prawda)

        self.assertIs(nie Prawda, Nieprawda)
        self.assertIs(nie Nieprawda, Prawda)

    def test_convert(self):
        self.assertRaises(TypeError, bool, 42, 42)
        self.assertIs(bool(10), Prawda)
        self.assertIs(bool(1), Prawda)
        self.assertIs(bool(-1), Prawda)
        self.assertIs(bool(0), Nieprawda)
        self.assertIs(bool("hello"), Prawda)
        self.assertIs(bool(""), Nieprawda)
        self.assertIs(bool(), Nieprawda)

    def test_format(self):
        self.assertEqual("%d" % Nieprawda, "0")
        self.assertEqual("%d" % Prawda, "1")
        self.assertEqual("%x" % Nieprawda, "0")
        self.assertEqual("%x" % Prawda, "1")

    def test_hasattr(self):
        self.assertIs(hasattr([], "append"), Prawda)
        self.assertIs(hasattr([], "wobble"), Nieprawda)

    def test_callable(self):
        self.assertIs(callable(len), Prawda)
        self.assertIs(callable(1), Nieprawda)

    def test_isinstance(self):
        self.assertIs(isinstance(Prawda, bool), Prawda)
        self.assertIs(isinstance(Nieprawda, bool), Prawda)
        self.assertIs(isinstance(Prawda, int), Prawda)
        self.assertIs(isinstance(Nieprawda, int), Prawda)
        self.assertIs(isinstance(1, bool), Nieprawda)
        self.assertIs(isinstance(0, bool), Nieprawda)

    def test_issubclass(self):
        self.assertIs(issubclass(bool, int), Prawda)
        self.assertIs(issubclass(int, bool), Nieprawda)

    def test_contains(self):
        self.assertIs(1 w {}, Nieprawda)
        self.assertIs(1 w {1:1}, Prawda)

    def test_string(self):
        self.assertIs("xyz".endswith("z"), Prawda)
        self.assertIs("xyz".endswith("x"), Nieprawda)
        self.assertIs("xyz0123".isalnum(), Prawda)
        self.assertIs("@#$%".isalnum(), Nieprawda)
        self.assertIs("xyz".isalpha(), Prawda)
        self.assertIs("@#$%".isalpha(), Nieprawda)
        self.assertIs("0123".isdigit(), Prawda)
        self.assertIs("xyz".isdigit(), Nieprawda)
        self.assertIs("xyz".islower(), Prawda)
        self.assertIs("XYZ".islower(), Nieprawda)
        self.assertIs("0123".isdecimal(), Prawda)
        self.assertIs("xyz".isdecimal(), Nieprawda)
        self.assertIs("0123".isnumeric(), Prawda)
        self.assertIs("xyz".isnumeric(), Nieprawda)
        self.assertIs(" ".isspace(), Prawda)
        self.assertIs("\xa0".isspace(), Prawda)
        self.assertIs("\u3000".isspace(), Prawda)
        self.assertIs("XYZ".isspace(), Nieprawda)
        self.assertIs("X".istitle(), Prawda)
        self.assertIs("x".istitle(), Nieprawda)
        self.assertIs("XYZ".isupper(), Prawda)
        self.assertIs("xyz".isupper(), Nieprawda)
        self.assertIs("xyz".startswith("x"), Prawda)
        self.assertIs("xyz".startswith("z"), Nieprawda)

    def test_boolean(self):
        self.assertEqual(Prawda & 1, 1)
        self.assertNotIsInstance(Prawda & 1, bool)
        self.assertIs(Prawda & Prawda, Prawda)

        self.assertEqual(Prawda | 1, 1)
        self.assertNotIsInstance(Prawda | 1, bool)
        self.assertIs(Prawda | Prawda, Prawda)

        self.assertEqual(Prawda ^ 1, 0)
        self.assertNotIsInstance(Prawda ^ 1, bool)
        self.assertIs(Prawda ^ Prawda, Nieprawda)

    def test_fileclosed(self):
        spróbuj:
            f = open(support.TESTFN, "w")
            self.assertIs(f.closed, Nieprawda)
            f.close()
            self.assertIs(f.closed, Prawda)
        w_końcu:
            os.remove(support.TESTFN)

    def test_types(self):
        # types are always true.
        dla t w [bool, complex, dict, float, int, list, object,
                  set, str, tuple, type]:
            self.assertIs(bool(t), Prawda)

    def test_operator(self):
        zaimportuj operator
        self.assertIs(operator.truth(0), Nieprawda)
        self.assertIs(operator.truth(1), Prawda)
        self.assertIs(operator.not_(1), Nieprawda)
        self.assertIs(operator.not_(0), Prawda)
        self.assertIs(operator.contains([], 1), Nieprawda)
        self.assertIs(operator.contains([1], 1), Prawda)
        self.assertIs(operator.lt(0, 0), Nieprawda)
        self.assertIs(operator.lt(0, 1), Prawda)
        self.assertIs(operator.is_(Prawda, Prawda), Prawda)
        self.assertIs(operator.is_(Prawda, Nieprawda), Nieprawda)
        self.assertIs(operator.is_not(Prawda, Prawda), Nieprawda)
        self.assertIs(operator.is_not(Prawda, Nieprawda), Prawda)

    def test_marshal(self):
        zaimportuj marshal
        self.assertIs(marshal.loads(marshal.dumps(Prawda)), Prawda)
        self.assertIs(marshal.loads(marshal.dumps(Nieprawda)), Nieprawda)

    def test_pickle(self):
        zaimportuj pickle
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            self.assertIs(pickle.loads(pickle.dumps(Prawda, proto)), Prawda)
            self.assertIs(pickle.loads(pickle.dumps(Nieprawda, proto)), Nieprawda)

    def test_picklevalues(self):
        # Test dla specific backwards-compatible pickle values
        zaimportuj pickle
        self.assertEqual(pickle.dumps(Prawda, protocol=0), b"I01\n.")
        self.assertEqual(pickle.dumps(Nieprawda, protocol=0), b"I00\n.")
        self.assertEqual(pickle.dumps(Prawda, protocol=1), b"I01\n.")
        self.assertEqual(pickle.dumps(Nieprawda, protocol=1), b"I00\n.")
        self.assertEqual(pickle.dumps(Prawda, protocol=2), b'\x80\x02\x88.')
        self.assertEqual(pickle.dumps(Nieprawda, protocol=2), b'\x80\x02\x89.')

    def test_convert_to_bool(self):
        # Verify that TypeError occurs when bad things are returned
        # z __bool__().  This isn't really a bool test, but
        # it's related.
        check = lambda o: self.assertRaises(TypeError, bool, o)
        klasa Foo(object):
            def __bool__(self):
                zwróć self
        check(Foo())

        klasa Bar(object):
            def __bool__(self):
                zwróć "Yes"
        check(Bar())

        klasa Baz(int):
            def __bool__(self):
                zwróć self
        check(Baz())

        # __bool__() must zwróć a bool nie an int
        klasa Spam(int):
            def __bool__(self):
                zwróć 1
        check(Spam())

        klasa Eggs:
            def __len__(self):
                zwróć -1
        self.assertRaises(ValueError, bool, Eggs())

    def test_sane_len(self):
        # this test just tests our assumptions about __len__
        # this will start failing jeżeli __len__ changes assertions
        dla badval w ['illegal', -1, 1 << 32]:
            klasa A:
                def __len__(self):
                    zwróć badval
            spróbuj:
                bool(A())
            wyjąwszy (Exception) jako e_bool:
                spróbuj:
                    len(A())
                wyjąwszy (Exception) jako e_len:
                    self.assertEqual(str(e_bool), str(e_len))

    def test_real_and_imag(self):
        self.assertEqual(Prawda.real, 1)
        self.assertEqual(Prawda.imag, 0)
        self.assertIs(type(Prawda.real), int)
        self.assertIs(type(Prawda.imag), int)
        self.assertEqual(Nieprawda.real, 0)
        self.assertEqual(Nieprawda.imag, 0)
        self.assertIs(type(Nieprawda.real), int)
        self.assertIs(type(Nieprawda.imag), int)

def test_main():
    support.run_unittest(BoolTest)

jeżeli __name__ == "__main__":
    test_main()
