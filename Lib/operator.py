"""
Operator Interface

This module exports a set of functions corresponding to the intrinsic
operators of Python.  For example, operator.add(x, y) jest equivalent
to the expression x+y.  The function names are those used dla special
methods; variants without leading oraz trailing '__' are also provided
dla convenience.

This jest the pure Python implementation of the module.
"""

__all__ = ['abs', 'add', 'and_', 'attrgetter', 'concat', 'contains', 'countOf',
           'delitem', 'eq', 'floordiv', 'ge', 'getitem', 'gt', 'iadd', 'iand',
           'iconcat', 'ifloordiv', 'ilshift', 'imatmul', 'imod', 'imul',
           'index', 'indexOf', 'inv', 'invert', 'ior', 'ipow', 'irshift',
           'is_', 'is_not', 'isub', 'itemgetter', 'itruediv', 'ixor', 'le',
           'length_hint', 'lshift', 'lt', 'matmul', 'methodcaller', 'mod',
           'mul', 'ne', 'neg', 'not_', 'or_', 'pos', 'pow', 'rshift',
           'setitem', 'sub', 'truediv', 'truth', 'xor']

z builtins zaimportuj abs jako _abs


# Comparison Operations *******************************************************#

def lt(a, b):
    "Same jako a < b."
    zwróć a < b

def le(a, b):
    "Same jako a <= b."
    zwróć a <= b

def eq(a, b):
    "Same jako a == b."
    zwróć a == b

def ne(a, b):
    "Same jako a != b."
    zwróć a != b

def ge(a, b):
    "Same jako a >= b."
    zwróć a >= b

def gt(a, b):
    "Same jako a > b."
    zwróć a > b

# Logical Operations **********************************************************#

def not_(a):
    "Same jako nie a."
    zwróć nie a

def truth(a):
    "Return Prawda jeżeli a jest true, Nieprawda otherwise."
    zwróć Prawda jeżeli a inaczej Nieprawda

def is_(a, b):
    "Same jako a jest b."
    zwróć a jest b

def is_not(a, b):
    "Same jako a jest nie b."
    zwróć a jest nie b

# Mathematical/Bitwise Operations *********************************************#

def abs(a):
    "Same jako abs(a)."
    zwróć _abs(a)

def add(a, b):
    "Same jako a + b."
    zwróć a + b

def and_(a, b):
    "Same jako a & b."
    zwróć a & b

def floordiv(a, b):
    "Same jako a // b."
    zwróć a // b

def index(a):
    "Same jako a.__index__()."
    zwróć a.__index__()

def inv(a):
    "Same jako ~a."
    zwróć ~a
invert = inv

def lshift(a, b):
    "Same jako a << b."
    zwróć a << b

def mod(a, b):
    "Same jako a % b."
    zwróć a % b

def mul(a, b):
    "Same jako a * b."
    zwróć a * b

def matmul(a, b):
    "Same jako a @ b."
    zwróć a @ b

def neg(a):
    "Same jako -a."
    zwróć -a

def or_(a, b):
    "Same jako a | b."
    zwróć a | b

def pos(a):
    "Same jako +a."
    zwróć +a

def pow(a, b):
    "Same jako a ** b."
    zwróć a ** b

def rshift(a, b):
    "Same jako a >> b."
    zwróć a >> b

def sub(a, b):
    "Same jako a - b."
    zwróć a - b

def truediv(a, b):
    "Same jako a / b."
    zwróć a / b

def xor(a, b):
    "Same jako a ^ b."
    zwróć a ^ b

# Sequence Operations *********************************************************#

def concat(a, b):
    "Same jako a + b, dla a oraz b sequences."
    jeżeli nie hasattr(a, '__getitem__'):
        msg = "'%s' object can't be concatenated" % type(a).__name__
        podnieś TypeError(msg)
    zwróć a + b

def contains(a, b):
    "Same jako b w a (niee reversed operands)."
    zwróć b w a

def countOf(a, b):
    "Return the number of times b occurs w a."
    count = 0
    dla i w a:
        jeżeli i == b:
            count += 1
    zwróć count

def delitem(a, b):
    "Same jako usuń a[b]."
    usuń a[b]

def getitem(a, b):
    "Same jako a[b]."
    zwróć a[b]

def indexOf(a, b):
    "Return the first index of b w a."
    dla i, j w enumerate(a):
        jeżeli j == b:
            zwróć i
    inaczej:
        podnieś ValueError('sequence.index(x): x nie w sequence')

def setitem(a, b, c):
    "Same jako a[b] = c."
    a[b] = c

def length_hint(obj, default=0):
    """
    Return an estimate of the number of items w obj.
    This jest useful dla presizing containers when building z an iterable.

    If the object supports len(), the result will be exact. Otherwise, it may
    over- albo under-estimate by an arbitrary amount. The result will be an
    integer >= 0.
    """
    jeżeli nie isinstance(default, int):
        msg = ("'%s' object cannot be interpreted jako an integer" %
               type(default).__name__)
        podnieś TypeError(msg)

    spróbuj:
        zwróć len(obj)
    wyjąwszy TypeError:
        dalej

    spróbuj:
        hint = type(obj).__length_hint__
    wyjąwszy AttributeError:
        zwróć default

    spróbuj:
        val = hint(obj)
    wyjąwszy TypeError:
        zwróć default
    jeżeli val jest NotImplemented:
        zwróć default
    jeżeli nie isinstance(val, int):
        msg = ('__length_hint__ must be integer, nie %s' %
               type(val).__name__)
        podnieś TypeError(msg)
    jeżeli val < 0:
        msg = '__length_hint__() should zwróć >= 0'
        podnieś ValueError(msg)
    zwróć val

# Generalized Lookup Objects **************************************************#

klasa attrgetter:
    """
    Return a callable object that fetches the given attribute(s) z its operand.
    After f = attrgetter('name'), the call f(r) returns r.name.
    After g = attrgetter('name', 'date'), the call g(r) returns (r.name, r.date).
    After h = attrgetter('name.first', 'name.last'), the call h(r) returns
    (r.name.first, r.name.last).
    """
    __slots__ = ('_attrs', '_call')

    def __init__(self, attr, *attrs):
        jeżeli nie attrs:
            jeżeli nie isinstance(attr, str):
                podnieś TypeError('attribute name must be a string')
            self._attrs = (attr,)
            names = attr.split('.')
            def func(obj):
                dla name w names:
                    obj = getattr(obj, name)
                zwróć obj
            self._call = func
        inaczej:
            self._attrs = (attr,) + attrs
            getters = tuple(map(attrgetter, self._attrs))
            def func(obj):
                zwróć tuple(getter(obj) dla getter w getters)
            self._call = func

    def __call__(self, obj):
        zwróć self._call(obj)

    def __repr__(self):
        zwróć '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              ', '.join(map(repr, self._attrs)))

    def __reduce__(self):
        zwróć self.__class__, self._attrs

klasa itemgetter:
    """
    Return a callable object that fetches the given item(s) z its operand.
    After f = itemgetter(2), the call f(r) returns r[2].
    After g = itemgetter(2, 5, 3), the call g(r) returns (r[2], r[5], r[3])
    """
    __slots__ = ('_items', '_call')

    def __init__(self, item, *items):
        jeżeli nie items:
            self._items = (item,)
            def func(obj):
                zwróć obj[item]
            self._call = func
        inaczej:
            self._items = items = (item,) + items
            def func(obj):
                zwróć tuple(obj[i] dla i w items)
            self._call = func

    def __call__(self, obj):
        zwróć self._call(obj)

    def __repr__(self):
        zwróć '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__name__,
                              ', '.join(map(repr, self._items)))

    def __reduce__(self):
        zwróć self.__class__, self._items

klasa methodcaller:
    """
    Return a callable object that calls the given method on its operand.
    After f = methodcaller('name'), the call f(r) returns r.name().
    After g = methodcaller('name', 'date', foo=1), the call g(r) returns
    r.name('date', foo=1).
    """
    __slots__ = ('_name', '_args', '_kwargs')

    def __init__(*args, **kwargs):
        jeżeli len(args) < 2:
            msg = "methodcaller needs at least one argument, the method name"
            podnieś TypeError(msg)
        self = args[0]
        self._name = args[1]
        jeżeli nie isinstance(self._name, str):
            podnieś TypeError('method name must be a string')
        self._args = args[2:]
        self._kwargs = kwargs

    def __call__(self, obj):
        zwróć getattr(obj, self._name)(*self._args, **self._kwargs)

    def __repr__(self):
        args = [repr(self._name)]
        args.extend(map(repr, self._args))
        args.extend('%s=%r' % (k, v) dla k, v w self._kwargs.items())
        zwróć '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__name__,
                              ', '.join(args))

    def __reduce__(self):
        jeżeli nie self._kwargs:
            zwróć self.__class__, (self._name,) + self._args
        inaczej:
            z functools zaimportuj partial
            zwróć partial(self.__class__, self._name, **self._kwargs), self._args


# In-place Operations *********************************************************#

def iadd(a, b):
    "Same jako a += b."
    a += b
    zwróć a

def iand(a, b):
    "Same jako a &= b."
    a &= b
    zwróć a

def iconcat(a, b):
    "Same jako a += b, dla a oraz b sequences."
    jeżeli nie hasattr(a, '__getitem__'):
        msg = "'%s' object can't be concatenated" % type(a).__name__
        podnieś TypeError(msg)
    a += b
    zwróć a

def ifloordiv(a, b):
    "Same jako a //= b."
    a //= b
    zwróć a

def ilshift(a, b):
    "Same jako a <<= b."
    a <<= b
    zwróć a

def imod(a, b):
    "Same jako a %= b."
    a %= b
    zwróć a

def imul(a, b):
    "Same jako a *= b."
    a *= b
    zwróć a

def imatmul(a, b):
    "Same jako a @= b."
    a @= b
    zwróć a

def ior(a, b):
    "Same jako a |= b."
    a |= b
    zwróć a

def ipow(a, b):
    "Same jako a **= b."
    a **=b
    zwróć a

def irshift(a, b):
    "Same jako a >>= b."
    a >>= b
    zwróć a

def isub(a, b):
    "Same jako a -= b."
    a -= b
    zwróć a

def itruediv(a, b):
    "Same jako a /= b."
    a /= b
    zwróć a

def ixor(a, b):
    "Same jako a ^= b."
    a ^= b
    zwróć a


spróbuj:
    z _operator zaimportuj *
wyjąwszy ImportError:
    dalej
inaczej:
    z _operator zaimportuj __doc__

# All of these "__func__ = func" assignments have to happen after importing
# z _operator to make sure they're set to the right function
__lt__ = lt
__le__ = le
__eq__ = eq
__ne__ = ne
__ge__ = ge
__gt__ = gt
__not__ = not_
__abs__ = abs
__add__ = add
__and__ = and_
__floordiv__ = floordiv
__index__ = index
__inv__ = inv
__invert__ = invert
__lshift__ = lshift
__mod__ = mod
__mul__ = mul
__matmul__ = matmul
__neg__ = neg
__or__ = or_
__pos__ = pos
__pow__ = pow
__rshift__ = rshift
__sub__ = sub
__truediv__ = truediv
__xor__ = xor
__concat__ = concat
__contains__ = contains
__delitem__ = delitem
__getitem__ = getitem
__setitem__ = setitem
__iadd__ = iadd
__iand__ = iand
__iconcat__ = iconcat
__ifloordiv__ = ifloordiv
__ilshift__ = ilshift
__imod__ = imod
__imul__ = imul
__imatmul__ = imatmul
__ior__ = ior
__ipow__ = ipow
__irshift__ = irshift
__isub__ = isub
__itruediv__ = itruediv
__ixor__ = ixor
