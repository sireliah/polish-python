#!/usr/bin/env python3

"""
Support Eiffel-style preconditions oraz postconditions dla functions.

An example dla Python metaclasses.
"""

zaimportuj unittest
z types zaimportuj FunctionType jako function

klasa EiffelBaseMetaClass(type):

    def __new__(meta, name, bases, dict):
        meta.convert_methods(dict)
        zwróć super(EiffelBaseMetaClass, meta).__new__(
            meta, name, bases, dict)

    @classmethod
    def convert_methods(cls, dict):
        """Replace functions w dict przy EiffelMethod wrappers.

        The dict jest modified w place.

        If a method ends w _pre albo _post, it jest removed z the dict
        regardless of whether there jest a corresponding method.
        """
        # find methods przy pre albo post conditions
        methods = []
        dla k, v w dict.items():
            jeżeli k.endswith('_pre') albo k.endswith('_post'):
                assert isinstance(v, function)
            albo_inaczej isinstance(v, function):
                methods.append(k)
        dla m w methods:
            pre = dict.get("%s_pre" % m)
            post = dict.get("%s_post" % m)
            jeżeli pre albo post:
                dict[m] = cls.make_eiffel_method(dict[m], pre, post)


klasa EiffelMetaClass1(EiffelBaseMetaClass):
    # an implementation of the "eiffel" meta klasa that uses nested functions

    @staticmethod
    def make_eiffel_method(func, pre, post):
        def method(self, *args, **kwargs):
            jeżeli pre:
                pre(self, *args, **kwargs)
            rv = func(self, *args, **kwargs)
            jeżeli post:
                post(self, rv, *args, **kwargs)
            zwróć rv

        jeżeli func.__doc__:
            method.__doc__ = func.__doc__

        zwróć method


klasa EiffelMethodWrapper:

    def __init__(self, inst, descr):
        self._inst = inst
        self._descr = descr

    def __call__(self, *args, **kwargs):
        zwróć self._descr.callmethod(self._inst, args, kwargs)


klasa EiffelDescriptor:

    def __init__(self, func, pre, post):
        self._func = func
        self._pre = pre
        self._post = post

        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, cls):
        zwróć EiffelMethodWrapper(obj, self)

    def callmethod(self, inst, args, kwargs):
        jeżeli self._pre:
            self._pre(inst, *args, **kwargs)
        x = self._func(inst, *args, **kwargs)
        jeżeli self._post:
            self._post(inst, x, *args, **kwargs)
        zwróć x


klasa EiffelMetaClass2(EiffelBaseMetaClass):
    # an implementation of the "eiffel" meta klasa that uses descriptors

    make_eiffel_method = EiffelDescriptor


klasa Tests(unittest.TestCase):

    def testEiffelMetaClass1(self):
        self._test(EiffelMetaClass1)

    def testEiffelMetaClass2(self):
        self._test(EiffelMetaClass2)

    def _test(self, metaclass):
        klasa Eiffel(metaclass=metaclass):
            dalej

        klasa Test(Eiffel):
            def m(self, arg):
                """Make it a little larger"""
                zwróć arg + 1

            def m2(self, arg):
                """Make it a little larger"""
                zwróć arg + 1

            def m2_pre(self, arg):
                assert arg > 0

            def m2_post(self, result, arg):
                assert result > arg

        klasa Sub(Test):
            def m2(self, arg):
                zwróć arg**2

            def m2_post(self, Result, arg):
                super(Sub, self).m2_post(Result, arg)
                assert Result < 100

        t = Test()
        self.assertEqual(t.m(1), 2)
        self.assertEqual(t.m2(1), 2)
        self.assertRaises(AssertionError, t.m2, 0)

        s = Sub()
        self.assertRaises(AssertionError, s.m2, 1)
        self.assertRaises(AssertionError, s.m2, 10)
        self.assertEqual(s.m2(5), 25)


jeżeli __name__ == "__main__":
    unittest.main()
