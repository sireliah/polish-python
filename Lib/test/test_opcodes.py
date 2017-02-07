# Python test set -- part 2, opcodes

zaimportuj unittest

klasa OpcodeTest(unittest.TestCase):

    def test_try_inside_for_loop(self):
        n = 0
        dla i w range(10):
            n = n+i
            spróbuj: 1/0
            wyjąwszy NameError: dalej
            wyjąwszy ZeroDivisionError: dalej
            wyjąwszy TypeError: dalej
            spróbuj: dalej
            wyjąwszy: dalej
            spróbuj: dalej
            w_końcu: dalej
            n = n+i
        jeżeli n != 90:
            self.fail('try inside for')

    def test_raise_class_exceptions(self):

        klasa AClass(Exception): dalej
        klasa BClass(AClass): dalej
        klasa CClass(Exception): dalej
        klasa DClass(AClass):
            def __init__(self, ignore):
                dalej

        spróbuj: podnieś AClass()
        wyjąwszy: dalej

        spróbuj: podnieś AClass()
        wyjąwszy AClass: dalej

        spróbuj: podnieś BClass()
        wyjąwszy AClass: dalej

        spróbuj: podnieś BClass()
        wyjąwszy CClass: self.fail()
        wyjąwszy: dalej

        a = AClass()
        b = BClass()

        spróbuj:
            podnieś b
        wyjąwszy AClass jako v:
            self.assertEqual(v, b)
        inaczej:
            self.fail("no exception")

        # nie enough arguments
        ##spróbuj:  podnieś BClass, a
        ##wyjąwszy TypeError: dalej
        ##inaczej: self.fail("no exception")

        spróbuj:  podnieś DClass(a)
        wyjąwszy DClass jako v:
            self.assertIsInstance(v, DClass)
        inaczej:
            self.fail("no exception")

    def test_compare_function_objects(self):

        f = eval('lambda: Nic')
        g = eval('lambda: Nic')
        self.assertNotEqual(f, g)

        f = eval('lambda a: a')
        g = eval('lambda a: a')
        self.assertNotEqual(f, g)

        f = eval('lambda a=1: a')
        g = eval('lambda a=1: a')
        self.assertNotEqual(f, g)

        f = eval('lambda: 0')
        g = eval('lambda: 1')
        self.assertNotEqual(f, g)

        f = eval('lambda: Nic')
        g = eval('lambda a: Nic')
        self.assertNotEqual(f, g)

        f = eval('lambda a: Nic')
        g = eval('lambda b: Nic')
        self.assertNotEqual(f, g)

        f = eval('lambda a: Nic')
        g = eval('lambda a=Nic: Nic')
        self.assertNotEqual(f, g)

        f = eval('lambda a=0: Nic')
        g = eval('lambda a=1: Nic')
        self.assertNotEqual(f, g)

    def test_modulo_of_string_subclasses(self):
        klasa MyString(str):
            def __mod__(self, value):
                zwróć 42
        self.assertEqual(MyString() % 3, 42)


jeżeli __name__ == '__main__':
    unittest.main()
