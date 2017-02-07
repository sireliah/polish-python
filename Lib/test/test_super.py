"""Unit tests dla new super() implementation."""

zaimportuj sys
zaimportuj unittest


klasa A:
    def f(self):
        zwróć 'A'
    @classmethod
    def cm(cls):
        zwróć (cls, 'A')

klasa B(A):
    def f(self):
        zwróć super().f() + 'B'
    @classmethod
    def cm(cls):
        zwróć (cls, super().cm(), 'B')

klasa C(A):
    def f(self):
        zwróć super().f() + 'C'
    @classmethod
    def cm(cls):
        zwróć (cls, super().cm(), 'C')

klasa D(C, B):
    def f(self):
        zwróć super().f() + 'D'
    def cm(cls):
        zwróć (cls, super().cm(), 'D')

klasa E(D):
    dalej

klasa F(E):
    f = E.f

klasa G(A):
    dalej


klasa TestSuper(unittest.TestCase):

    def tearDown(self):
        # This fixes the damage that test_various___class___pathologies does.
        nonlocal __class__
        __class__ = TestSuper

    def test_basics_working(self):
        self.assertEqual(D().f(), 'ABCD')

    def test_class_getattr_working(self):
        self.assertEqual(D.f(D()), 'ABCD')

    def test_subclass_no_override_working(self):
        self.assertEqual(E().f(), 'ABCD')
        self.assertEqual(E.f(E()), 'ABCD')

    def test_unbound_method_transfer_working(self):
        self.assertEqual(F().f(), 'ABCD')
        self.assertEqual(F.f(F()), 'ABCD')

    def test_class_methods_still_working(self):
        self.assertEqual(A.cm(), (A, 'A'))
        self.assertEqual(A().cm(), (A, 'A'))
        self.assertEqual(G.cm(), (G, 'A'))
        self.assertEqual(G().cm(), (G, 'A'))

    def test_super_in_class_methods_working(self):
        d = D()
        self.assertEqual(d.cm(), (d, (D, (D, (D, 'A'), 'B'), 'C'), 'D'))
        e = E()
        self.assertEqual(e.cm(), (e, (E, (E, (E, 'A'), 'B'), 'C'), 'D'))

    def test_super_with_closure(self):
        # Issue4360: super() did nie work w a function that
        # contains a closure
        klasa E(A):
            def f(self):
                def nested():
                    self
                zwróć super().f() + 'E'

        self.assertEqual(E().f(), 'AE')

    def test_various___class___pathologies(self):
        # See issue #12370
        klasa X(A):
            def f(self):
                zwróć super().f()
            __class__ = 413
        x = X()
        self.assertEqual(x.f(), 'A')
        self.assertEqual(x.__class__, 413)
        klasa X:
            x = __class__
            def f():
                __class__
        self.assertIs(X.x, type(self))
        przy self.assertRaises(NameError) jako e:
            exec("""class X:
                __class__
                def f():
                    __class__""", globals(), {})
        self.assertIs(type(e.exception), NameError) # Not UnboundLocalError
        klasa X:
            global __class__
            __class__ = 42
            def f():
                __class__
        self.assertEqual(globals()["__class__"], 42)
        usuń globals()["__class__"]
        self.assertNotIn("__class__", X.__dict__)
        klasa X:
            nonlocal __class__
            __class__ = 42
            def f():
                __class__
        self.assertEqual(__class__, 42)

    def test___class___instancemethod(self):
        # See issue #14857
        klasa X:
            def f(self):
                zwróć __class__
        self.assertIs(X().f(), X)

    def test___class___classmethod(self):
        # See issue #14857
        klasa X:
            @classmethod
            def f(cls):
                zwróć __class__
        self.assertIs(X.f(), X)

    def test___class___staticmethod(self):
        # See issue #14857
        klasa X:
            @staticmethod
            def f():
                zwróć __class__
        self.assertIs(X.f(), X)

    def test_obscure_super_errors(self):
        def f():
            super()
        self.assertRaises(RuntimeError, f)
        def f(x):
            usuń x
            super()
        self.assertRaises(RuntimeError, f, Nic)
        klasa X:
            def f(x):
                nonlocal __class__
                usuń __class__
                super()
        self.assertRaises(RuntimeError, X().f)

    def test_cell_as_self(self):
        klasa X:
            def meth(self):
                super()

        def f():
            k = X()
            def g():
                zwróć k
            zwróć g
        c = f().__closure__[0]
        self.assertRaises(TypeError, X.meth, c)


jeżeli __name__ == "__main__":
    unittest.main()
