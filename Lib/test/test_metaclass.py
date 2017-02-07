doctests = """

Basic klasa construction.

    >>> klasa C:
    ...     def meth(self): print("Hello")
    ...
    >>> C.__class__ jest type
    Prawda
    >>> a = C()
    >>> a.__class__ jest C
    Prawda
    >>> a.meth()
    Hello
    >>>

Use *args notation dla the bases.

    >>> klasa A: dalej
    >>> klasa B: dalej
    >>> bases = (A, B)
    >>> klasa C(*bases): dalej
    >>> C.__bases__ == bases
    Prawda
    >>>

Use a trivial metaclass.

    >>> klasa M(type):
    ...     dalej
    ...
    >>> klasa C(metaclass=M):
    ...    def meth(self): print("Hello")
    ...
    >>> C.__class__ jest M
    Prawda
    >>> a = C()
    >>> a.__class__ jest C
    Prawda
    >>> a.meth()
    Hello
    >>>

Use **kwds notation dla the metaclass keyword.

    >>> kwds = {'metaclass': M}
    >>> klasa C(**kwds): dalej
    ...
    >>> C.__class__ jest M
    Prawda
    >>> a = C()
    >>> a.__class__ jest C
    Prawda
    >>>

Use a metaclass przy a __prepare__ static method.

    >>> klasa M(type):
    ...    @staticmethod
    ...    def __prepare__(*args, **kwds):
    ...        print("Prepare called:", args, kwds)
    ...        zwróć dict()
    ...    def __new__(cls, name, bases, namespace, **kwds):
    ...        print("New called:", kwds)
    ...        zwróć type.__new__(cls, name, bases, namespace)
    ...    def __init__(cls, *args, **kwds):
    ...        dalej
    ...
    >>> klasa C(metaclass=M):
    ...     def meth(self): print("Hello")
    ...
    Prepare called: ('C', ()) {}
    New called: {}
    >>>

Also dalej another keyword.

    >>> klasa C(object, metaclass=M, other="haha"):
    ...     dalej
    ...
    Prepare called: ('C', (<class 'object'>,)) {'other': 'haha'}
    New called: {'other': 'haha'}
    >>> C.__class__ jest M
    Prawda
    >>> C.__bases__ == (object,)
    Prawda
    >>> a = C()
    >>> a.__class__ jest C
    Prawda
    >>>

Check that build_class doesn't mutate the kwds dict.

    >>> kwds = {'metaclass': type}
    >>> klasa C(**kwds): dalej
    ...
    >>> kwds == {'metaclass': type}
    Prawda
    >>>

Use various combinations of explicit keywords oraz **kwds.

    >>> bases = (object,)
    >>> kwds = {'metaclass': M, 'other': 'haha'}
    >>> klasa C(*bases, **kwds): dalej
    ...
    Prepare called: ('C', (<class 'object'>,)) {'other': 'haha'}
    New called: {'other': 'haha'}
    >>> C.__class__ jest M
    Prawda
    >>> C.__bases__ == (object,)
    Prawda
    >>> klasa B: dalej
    >>> kwds = {'other': 'haha'}
    >>> klasa C(B, metaclass=M, *bases, **kwds): dalej
    ...
    Prepare called: ('C', (<class 'test.test_metaclass.B'>, <class 'object'>)) {'other': 'haha'}
    New called: {'other': 'haha'}
    >>> C.__class__ jest M
    Prawda
    >>> C.__bases__ == (B, object)
    Prawda
    >>>

Check dla duplicate keywords.

    >>> klasa C(metaclass=type, metaclass=type): dalej
    ...
    Traceback (most recent call last):
    [...]
    SyntaxError: keyword argument repeated
    >>>

Another way.

    >>> kwds = {'metaclass': type}
    >>> klasa C(metaclass=type, **kwds): dalej
    ...
    Traceback (most recent call last):
    [...]
    TypeError: __build_class__() got multiple values dla keyword argument 'metaclass'
    >>>

Use a __prepare__ method that returns an instrumented dict.

    >>> klasa LoggingDict(dict):
    ...     def __setitem__(self, key, value):
    ...         print("d[%r] = %r" % (key, value))
    ...         dict.__setitem__(self, key, value)
    ...
    >>> klasa Meta(type):
    ...    @staticmethod
    ...    def __prepare__(name, bases):
    ...        zwróć LoggingDict()
    ...
    >>> klasa C(metaclass=Meta):
    ...     foo = 2+2
    ...     foo = 42
    ...     bar = 123
    ...
    d['__module__'] = 'test.test_metaclass'
    d['__qualname__'] = 'C'
    d['foo'] = 4
    d['foo'] = 42
    d['bar'] = 123
    >>>

Use a metaclass that doesn't derive z type.

    >>> def meta(name, bases, namespace, **kwds):
    ...     print("meta:", name, bases)
    ...     print("ns:", sorted(namespace.items()))
    ...     print("kw:", sorted(kwds.items()))
    ...     zwróć namespace
    ...
    >>> klasa C(metaclass=meta):
    ...     a = 42
    ...     b = 24
    ...
    meta: C ()
    ns: [('__module__', 'test.test_metaclass'), ('__qualname__', 'C'), ('a', 42), ('b', 24)]
    kw: []
    >>> type(C) jest dict
    Prawda
    >>> print(sorted(C.items()))
    [('__module__', 'test.test_metaclass'), ('__qualname__', 'C'), ('a', 42), ('b', 24)]
    >>>

And again, przy a __prepare__ attribute.

    >>> def prepare(name, bases, **kwds):
    ...     print("prepare:", name, bases, sorted(kwds.items()))
    ...     zwróć LoggingDict()
    ...
    >>> meta.__prepare__ = prepare
    >>> klasa C(metaclass=meta, other="booh"):
    ...    a = 1
    ...    a = 2
    ...    b = 3
    ...
    prepare: C () [('other', 'booh')]
    d['__module__'] = 'test.test_metaclass'
    d['__qualname__'] = 'C'
    d['a'] = 1
    d['a'] = 2
    d['b'] = 3
    meta: C ()
    ns: [('__module__', 'test.test_metaclass'), ('__qualname__', 'C'), ('a', 2), ('b', 3)]
    kw: [('other', 'booh')]
    >>>

The default metaclass must define a __prepare__() method.

    >>> type.__prepare__()
    {}
    >>>

Make sure it works przy subclassing.

    >>> klasa M(type):
    ...     @classmethod
    ...     def __prepare__(cls, *args, **kwds):
    ...         d = super().__prepare__(*args, **kwds)
    ...         d["hello"] = 42
    ...         zwróć d
    ...
    >>> klasa C(metaclass=M):
    ...     print(hello)
    ...
    42
    >>> print(C.hello)
    42
    >>>

Test failures w looking up the __prepare__ method work.
    >>> klasa ObscureException(Exception):
    ...     dalej
    >>> klasa FailDescr:
    ...     def __get__(self, instance, owner):
    ...        podnieś ObscureException
    >>> klasa Meta(type):
    ...     __prepare__ = FailDescr()
    >>> klasa X(metaclass=Meta):
    ...     dalej
    Traceback (most recent call last):
    [...]
    test.test_metaclass.ObscureException

"""

zaimportuj sys

# Trace function introduces __locals__ which causes various tests to fail.
jeżeli hasattr(sys, 'gettrace') oraz sys.gettrace():
    __test__ = {}
inaczej:
    __test__ = {'doctests' : doctests}

def test_main(verbose=Nieprawda):
    z test zaimportuj support
    z test zaimportuj test_metaclass
    support.run_doctest(test_metaclass, verbose)

jeżeli __name__ == "__main__":
    test_main(verbose=Prawda)
