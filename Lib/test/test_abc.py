# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Unit tests dla abc.py."""

zaimportuj unittest
z test zaimportuj support

zaimportuj abc
z inspect zaimportuj isabstract


klasa TestLegacyAPI(unittest.TestCase):

    def test_abstractproperty_basics(self):
        @abc.abstractproperty
        def foo(self): dalej
        self.assertPrawda(foo.__isabstractmethod__)
        def bar(self): dalej
        self.assertNieprawda(hasattr(bar, "__isabstractmethod__"))

        klasa C(metaclass=abc.ABCMeta):
            @abc.abstractproperty
            def foo(self): zwróć 3
        self.assertRaises(TypeError, C)
        klasa D(C):
            @property
            def foo(self): zwróć super().foo
        self.assertEqual(D().foo, 3)
        self.assertNieprawda(getattr(D.foo, "__isabstractmethod__", Nieprawda))

    def test_abstractclassmethod_basics(self):
        @abc.abstractclassmethod
        def foo(cls): dalej
        self.assertPrawda(foo.__isabstractmethod__)
        @classmethod
        def bar(cls): dalej
        self.assertNieprawda(getattr(bar, "__isabstractmethod__", Nieprawda))

        klasa C(metaclass=abc.ABCMeta):
            @abc.abstractclassmethod
            def foo(cls): zwróć cls.__name__
        self.assertRaises(TypeError, C)
        klasa D(C):
            @classmethod
            def foo(cls): zwróć super().foo()
        self.assertEqual(D.foo(), 'D')
        self.assertEqual(D().foo(), 'D')

    def test_abstractstaticmethod_basics(self):
        @abc.abstractstaticmethod
        def foo(): dalej
        self.assertPrawda(foo.__isabstractmethod__)
        @staticmethod
        def bar(): dalej
        self.assertNieprawda(getattr(bar, "__isabstractmethod__", Nieprawda))

        klasa C(metaclass=abc.ABCMeta):
            @abc.abstractstaticmethod
            def foo(): zwróć 3
        self.assertRaises(TypeError, C)
        klasa D(C):
            @staticmethod
            def foo(): zwróć 4
        self.assertEqual(D.foo(), 4)
        self.assertEqual(D().foo(), 4)


klasa TestABC(unittest.TestCase):

    def test_ABC_helper(self):
        # create an ABC using the helper klasa oraz perform basic checks
        klasa C(abc.ABC):
            @classmethod
            @abc.abstractmethod
            def foo(cls): zwróć cls.__name__
        self.assertEqual(type(C), abc.ABCMeta)
        self.assertRaises(TypeError, C)
        klasa D(C):
            @classmethod
            def foo(cls): zwróć super().foo()
        self.assertEqual(D.foo(), 'D')

    def test_abstractmethod_basics(self):
        @abc.abstractmethod
        def foo(self): dalej
        self.assertPrawda(foo.__isabstractmethod__)
        def bar(self): dalej
        self.assertNieprawda(hasattr(bar, "__isabstractmethod__"))

    def test_abstractproperty_basics(self):
        @property
        @abc.abstractmethod
        def foo(self): dalej
        self.assertPrawda(foo.__isabstractmethod__)
        def bar(self): dalej
        self.assertNieprawda(getattr(bar, "__isabstractmethod__", Nieprawda))

        klasa C(metaclass=abc.ABCMeta):
            @property
            @abc.abstractmethod
            def foo(self): zwróć 3
        self.assertRaises(TypeError, C)
        klasa D(C):
            @C.foo.getter
            def foo(self): zwróć super().foo
        self.assertEqual(D().foo, 3)

    def test_abstractclassmethod_basics(self):
        @classmethod
        @abc.abstractmethod
        def foo(cls): dalej
        self.assertPrawda(foo.__isabstractmethod__)
        @classmethod
        def bar(cls): dalej
        self.assertNieprawda(getattr(bar, "__isabstractmethod__", Nieprawda))

        klasa C(metaclass=abc.ABCMeta):
            @classmethod
            @abc.abstractmethod
            def foo(cls): zwróć cls.__name__
        self.assertRaises(TypeError, C)
        klasa D(C):
            @classmethod
            def foo(cls): zwróć super().foo()
        self.assertEqual(D.foo(), 'D')
        self.assertEqual(D().foo(), 'D')

    def test_abstractstaticmethod_basics(self):
        @staticmethod
        @abc.abstractmethod
        def foo(): dalej
        self.assertPrawda(foo.__isabstractmethod__)
        @staticmethod
        def bar(): dalej
        self.assertNieprawda(getattr(bar, "__isabstractmethod__", Nieprawda))

        klasa C(metaclass=abc.ABCMeta):
            @staticmethod
            @abc.abstractmethod
            def foo(): zwróć 3
        self.assertRaises(TypeError, C)
        klasa D(C):
            @staticmethod
            def foo(): zwróć 4
        self.assertEqual(D.foo(), 4)
        self.assertEqual(D().foo(), 4)

    def test_abstractmethod_integration(self):
        dla abstractthing w [abc.abstractmethod, abc.abstractproperty,
                              abc.abstractclassmethod,
                              abc.abstractstaticmethod]:
            klasa C(metaclass=abc.ABCMeta):
                @abstractthing
                def foo(self): dalej  # abstract
                def bar(self): dalej  # concrete
            self.assertEqual(C.__abstractmethods__, {"foo"})
            self.assertRaises(TypeError, C)  # because foo jest abstract
            self.assertPrawda(isabstract(C))
            klasa D(C):
                def bar(self): dalej  # concrete override of concrete
            self.assertEqual(D.__abstractmethods__, {"foo"})
            self.assertRaises(TypeError, D)  # because foo jest still abstract
            self.assertPrawda(isabstract(D))
            klasa E(D):
                def foo(self): dalej
            self.assertEqual(E.__abstractmethods__, set())
            E()  # now foo jest concrete, too
            self.assertNieprawda(isabstract(E))
            klasa F(E):
                @abstractthing
                def bar(self): dalej  # abstract override of concrete
            self.assertEqual(F.__abstractmethods__, {"bar"})
            self.assertRaises(TypeError, F)  # because bar jest abstract now
            self.assertPrawda(isabstract(F))

    def test_descriptors_with_abstractmethod(self):
        klasa C(metaclass=abc.ABCMeta):
            @property
            @abc.abstractmethod
            def foo(self): zwróć 3
            @foo.setter
            @abc.abstractmethod
            def foo(self, val): dalej
        self.assertRaises(TypeError, C)
        klasa D(C):
            @C.foo.getter
            def foo(self): zwróć super().foo
        self.assertRaises(TypeError, D)
        klasa E(D):
            @D.foo.setter
            def foo(self, val): dalej
        self.assertEqual(E().foo, 3)
        # check that the property's __isabstractmethod__ descriptor does the
        # right thing when presented przy a value that fails truth testing:
        klasa NotBool(object):
            def __bool__(self):
                podnieś ValueError()
            __len__ = __bool__
        przy self.assertRaises(ValueError):
            klasa F(C):
                def bar(self):
                    dalej
                bar.__isabstractmethod__ = NotBool()
                foo = property(bar)


    def test_customdescriptors_with_abstractmethod(self):
        klasa Descriptor:
            def __init__(self, fget, fset=Nic):
                self._fget = fget
                self._fset = fset
            def getter(self, callable):
                zwróć Descriptor(callable, self._fget)
            def setter(self, callable):
                zwróć Descriptor(self._fget, callable)
            @property
            def __isabstractmethod__(self):
                zwróć (getattr(self._fget, '__isabstractmethod__', Nieprawda)
                        albo getattr(self._fset, '__isabstractmethod__', Nieprawda))
        klasa C(metaclass=abc.ABCMeta):
            @Descriptor
            @abc.abstractmethod
            def foo(self): zwróć 3
            @foo.setter
            @abc.abstractmethod
            def foo(self, val): dalej
        self.assertRaises(TypeError, C)
        klasa D(C):
            @C.foo.getter
            def foo(self): zwróć super().foo
        self.assertRaises(TypeError, D)
        klasa E(D):
            @D.foo.setter
            def foo(self, val): dalej
        self.assertNieprawda(E.foo.__isabstractmethod__)

    def test_metaclass_abc(self):
        # Metaclasses can be ABCs, too.
        klasa A(metaclass=abc.ABCMeta):
            @abc.abstractmethod
            def x(self):
                dalej
        self.assertEqual(A.__abstractmethods__, {"x"})
        klasa meta(type, A):
            def x(self):
                zwróć 1
        klasa C(metaclass=meta):
            dalej

    def test_registration_basics(self):
        klasa A(metaclass=abc.ABCMeta):
            dalej
        klasa B(object):
            dalej
        b = B()
        self.assertNieprawda(issubclass(B, A))
        self.assertNieprawda(issubclass(B, (A,)))
        self.assertNotIsInstance(b, A)
        self.assertNotIsInstance(b, (A,))
        B1 = A.register(B)
        self.assertPrawda(issubclass(B, A))
        self.assertPrawda(issubclass(B, (A,)))
        self.assertIsInstance(b, A)
        self.assertIsInstance(b, (A,))
        self.assertIs(B1, B)
        klasa C(B):
            dalej
        c = C()
        self.assertPrawda(issubclass(C, A))
        self.assertPrawda(issubclass(C, (A,)))
        self.assertIsInstance(c, A)
        self.assertIsInstance(c, (A,))

    def test_register_as_class_deco(self):
        klasa A(metaclass=abc.ABCMeta):
            dalej
        @A.register
        klasa B(object):
            dalej
        b = B()
        self.assertPrawda(issubclass(B, A))
        self.assertPrawda(issubclass(B, (A,)))
        self.assertIsInstance(b, A)
        self.assertIsInstance(b, (A,))
        @A.register
        klasa C(B):
            dalej
        c = C()
        self.assertPrawda(issubclass(C, A))
        self.assertPrawda(issubclass(C, (A,)))
        self.assertIsInstance(c, A)
        self.assertIsInstance(c, (A,))
        self.assertIs(C, A.register(C))

    def test_isinstance_invalidation(self):
        klasa A(metaclass=abc.ABCMeta):
            dalej
        klasa B:
            dalej
        b = B()
        self.assertNieprawda(isinstance(b, A))
        self.assertNieprawda(isinstance(b, (A,)))
        token_old = abc.get_cache_token()
        A.register(B)
        token_new = abc.get_cache_token()
        self.assertNotEqual(token_old, token_new)
        self.assertPrawda(isinstance(b, A))
        self.assertPrawda(isinstance(b, (A,)))

    def test_registration_builtins(self):
        klasa A(metaclass=abc.ABCMeta):
            dalej
        A.register(int)
        self.assertIsInstance(42, A)
        self.assertIsInstance(42, (A,))
        self.assertPrawda(issubclass(int, A))
        self.assertPrawda(issubclass(int, (A,)))
        klasa B(A):
            dalej
        B.register(str)
        klasa C(str): dalej
        self.assertIsInstance("", A)
        self.assertIsInstance("", (A,))
        self.assertPrawda(issubclass(str, A))
        self.assertPrawda(issubclass(str, (A,)))
        self.assertPrawda(issubclass(C, A))
        self.assertPrawda(issubclass(C, (A,)))

    def test_registration_edge_cases(self):
        klasa A(metaclass=abc.ABCMeta):
            dalej
        A.register(A)  # should dalej silently
        klasa A1(A):
            dalej
        self.assertRaises(RuntimeError, A1.register, A)  # cycles nie allowed
        klasa B(object):
            dalej
        A1.register(B)  # ok
        A1.register(B)  # should dalej silently
        klasa C(A):
            dalej
        A.register(C)  # should dalej silently
        self.assertRaises(RuntimeError, C.register, A)  # cycles nie allowed
        C.register(B)  # ok

    def test_register_non_class(self):
        klasa A(metaclass=abc.ABCMeta):
            dalej
        self.assertRaisesRegex(TypeError, "Can only register classes",
                               A.register, 4)

    def test_registration_transitiveness(self):
        klasa A(metaclass=abc.ABCMeta):
            dalej
        self.assertPrawda(issubclass(A, A))
        self.assertPrawda(issubclass(A, (A,)))
        klasa B(metaclass=abc.ABCMeta):
            dalej
        self.assertNieprawda(issubclass(A, B))
        self.assertNieprawda(issubclass(A, (B,)))
        self.assertNieprawda(issubclass(B, A))
        self.assertNieprawda(issubclass(B, (A,)))
        klasa C(metaclass=abc.ABCMeta):
            dalej
        A.register(B)
        klasa B1(B):
            dalej
        self.assertPrawda(issubclass(B1, A))
        self.assertPrawda(issubclass(B1, (A,)))
        klasa C1(C):
            dalej
        B1.register(C1)
        self.assertNieprawda(issubclass(C, B))
        self.assertNieprawda(issubclass(C, (B,)))
        self.assertNieprawda(issubclass(C, B1))
        self.assertNieprawda(issubclass(C, (B1,)))
        self.assertPrawda(issubclass(C1, A))
        self.assertPrawda(issubclass(C1, (A,)))
        self.assertPrawda(issubclass(C1, B))
        self.assertPrawda(issubclass(C1, (B,)))
        self.assertPrawda(issubclass(C1, B1))
        self.assertPrawda(issubclass(C1, (B1,)))
        C1.register(int)
        klasa MyInt(int):
            dalej
        self.assertPrawda(issubclass(MyInt, A))
        self.assertPrawda(issubclass(MyInt, (A,)))
        self.assertIsInstance(42, A)
        self.assertIsInstance(42, (A,))

    def test_all_new_methods_are_called(self):
        klasa A(metaclass=abc.ABCMeta):
            dalej
        klasa B(object):
            counter = 0
            def __new__(cls):
                B.counter += 1
                zwróć super().__new__(cls)
        klasa C(A, B):
            dalej
        self.assertEqual(B.counter, 0)
        C()
        self.assertEqual(B.counter, 1)


jeżeli __name__ == "__main__":
    unittest.main()
