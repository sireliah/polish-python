# This contains most of the executable examples z Guido's descr
# tutorial, once at
#
#     http://www.python.org/2.2/descrintro.html
#
# A few examples left implicit w the writeup were fleshed out, a few were
# skipped due to lack of interest (e.g., faking super() by hand isn't
# of much interest anymore), oraz a few were fiddled to make the output
# deterministic.

z test.support zaimportuj sortdict
zaimportuj pprint

klasa defaultdict(dict):
    def __init__(self, default=Nic):
        dict.__init__(self)
        self.default = default

    def __getitem__(self, key):
        spróbuj:
            zwróć dict.__getitem__(self, key)
        wyjąwszy KeyError:
            zwróć self.default

    def get(self, key, *args):
        jeżeli nie args:
            args = (self.default,)
        zwróć dict.get(self, key, *args)

    def merge(self, other):
        dla key w other:
            jeżeli key nie w self:
                self[key] = other[key]

test_1 = """

Here's the new type at work:

    >>> print(defaultdict)              # show our type
    <class 'test.test_descrtut.defaultdict'>
    >>> print(type(defaultdict))        # its metatype
    <class 'type'>
    >>> a = defaultdict(default=0.0)    # create an instance
    >>> print(a)                        # show the instance
    {}
    >>> print(type(a))                  # show its type
    <class 'test.test_descrtut.defaultdict'>
    >>> print(a.__class__)              # show its class
    <class 'test.test_descrtut.defaultdict'>
    >>> print(type(a) jest a.__class__)   # its type jest its class
    Prawda
    >>> a[1] = 3.25                     # modify the instance
    >>> print(a)                        # show the new value
    {1: 3.25}
    >>> print(a[1])                     # show the new item
    3.25
    >>> print(a[0])                     # a non-existent item
    0.0
    >>> a.merge({1:100, 2:200})         # use a dict method
    >>> print(sortdict(a))              # show the result
    {1: 3.25, 2: 200}
    >>>

We can also use the new type w contexts where classic only allows "real"
dictionaries, such jako the locals/globals dictionaries dla the exec
statement albo the built-in function eval():

    >>> print(sorted(a.keys()))
    [1, 2]
    >>> a['print'] = print              # need the print function here
    >>> exec("x = 3; print(x)", a)
    3
    >>> print(sorted(a.keys(), key=lambda x: (str(type(x)), x)))
    [1, 2, '__builtins__', 'print', 'x']
    >>> print(a['x'])
    3
    >>>

Now I'll show that defaultdict instances have dynamic instance variables,
just like classic classes:

    >>> a.default = -1
    >>> print(a["noway"])
    -1
    >>> a.default = -1000
    >>> print(a["noway"])
    -1000
    >>> 'default' w dir(a)
    Prawda
    >>> a.x1 = 100
    >>> a.x2 = 200
    >>> print(a.x1)
    100
    >>> d = dir(a)
    >>> 'default' w d oraz 'x1' w d oraz 'x2' w d
    Prawda
    >>> print(sortdict(a.__dict__))
    {'default': -1000, 'x1': 100, 'x2': 200}
    >>>
"""

klasa defaultdict2(dict):
    __slots__ = ['default']

    def __init__(self, default=Nic):
        dict.__init__(self)
        self.default = default

    def __getitem__(self, key):
        spróbuj:
            zwróć dict.__getitem__(self, key)
        wyjąwszy KeyError:
            zwróć self.default

    def get(self, key, *args):
        jeżeli nie args:
            args = (self.default,)
        zwróć dict.get(self, key, *args)

    def merge(self, other):
        dla key w other:
            jeżeli key nie w self:
                self[key] = other[key]

test_2 = """

The __slots__ declaration takes a list of instance variables, oraz reserves
space dla exactly these w the instance. When __slots__ jest used, other
instance variables cannot be assigned to:

    >>> a = defaultdict2(default=0.0)
    >>> a[1]
    0.0
    >>> a.default = -1
    >>> a[1]
    -1
    >>> a.x1 = 1
    Traceback (most recent call last):
      File "<stdin>", line 1, w ?
    AttributeError: 'defaultdict2' object has no attribute 'x1'
    >>>

"""

test_3 = """

Introspecting instances of built-in types

For instance of built-in types, x.__class__ jest now the same jako type(x):

    >>> type([])
    <class 'list'>
    >>> [].__class__
    <class 'list'>
    >>> list
    <class 'list'>
    >>> isinstance([], list)
    Prawda
    >>> isinstance([], dict)
    Nieprawda
    >>> isinstance([], object)
    Prawda
    >>>

You can get the information z the list type:

    >>> pprint.pprint(dir(list))    # like list.__dict__.keys(), but sorted
    ['__add__',
     '__class__',
     '__contains__',
     '__delattr__',
     '__delitem__',
     '__dir__',
     '__doc__',
     '__eq__',
     '__format__',
     '__ge__',
     '__getattribute__',
     '__getitem__',
     '__gt__',
     '__hash__',
     '__iadd__',
     '__imul__',
     '__init__',
     '__iter__',
     '__le__',
     '__len__',
     '__lt__',
     '__mul__',
     '__ne__',
     '__new__',
     '__reduce__',
     '__reduce_ex__',
     '__repr__',
     '__reversed__',
     '__rmul__',
     '__setattr__',
     '__setitem__',
     '__sizeof__',
     '__str__',
     '__subclasshook__',
     'append',
     'clear',
     'copy',
     'count',
     'extend',
     'index',
     'insert',
     'pop',
     'remove',
     'reverse',
     'sort']

The new introspection API gives more information than the old one:  w
addition to the regular methods, it also shows the methods that are
normally invoked through special notations, e.g. __iadd__ (+=), __len__
(len), __ne__ (!=). You can invoke any method z this list directly:

    >>> a = ['tic', 'tac']
    >>> list.__len__(a)          # same jako len(a)
    2
    >>> a.__len__()              # ditto
    2
    >>> list.append(a, 'toe')    # same jako a.append('toe')
    >>> a
    ['tic', 'tac', 'toe']
    >>>

This jest just like it jest dla user-defined classes.
"""

test_4 = """

Static methods oraz klasa methods

The new introspection API makes it possible to add static methods oraz class
methods. Static methods are easy to describe: they behave pretty much like
static methods w C++ albo Java. Here's an example:

    >>> klasa C:
    ...
    ...     @staticmethod
    ...     def foo(x, y):
    ...         print("staticmethod", x, y)

    >>> C.foo(1, 2)
    staticmethod 1 2
    >>> c = C()
    >>> c.foo(1, 2)
    staticmethod 1 2

Class methods use a similar pattern to declare methods that receive an
implicit first argument that jest the *class* dla which they are invoked.

    >>> klasa C:
    ...     @classmethod
    ...     def foo(cls, y):
    ...         print("classmethod", cls, y)

    >>> C.foo(1)
    classmethod <class 'test.test_descrtut.C'> 1
    >>> c = C()
    >>> c.foo(1)
    classmethod <class 'test.test_descrtut.C'> 1

    >>> klasa D(C):
    ...     dalej

    >>> D.foo(1)
    classmethod <class 'test.test_descrtut.D'> 1
    >>> d = D()
    >>> d.foo(1)
    classmethod <class 'test.test_descrtut.D'> 1

This prints "classmethod __main__.D 1" both times; w other words, the
klasa dalejed jako the first argument of foo() jest the klasa involved w the
call, nie the klasa involved w the definition of foo().

But notice this:

    >>> klasa E(C):
    ...     @classmethod
    ...     def foo(cls, y): # override C.foo
    ...         print("E.foo() called")
    ...         C.foo(y)

    >>> E.foo(1)
    E.foo() called
    classmethod <class 'test.test_descrtut.C'> 1
    >>> e = E()
    >>> e.foo(1)
    E.foo() called
    classmethod <class 'test.test_descrtut.C'> 1

In this example, the call to C.foo() z E.foo() will see klasa C jako its
first argument, nie klasa E. This jest to be expected, since the call
specifies the klasa C. But it stresses the difference between these class
methods oraz methods defined w metaclasses (where an upcall to a metamethod
would dalej the target klasa jako an explicit first argument).
"""

test_5 = """

Attributes defined by get/set methods


    >>> klasa property(object):
    ...
    ...     def __init__(self, get, set=Nic):
    ...         self.__get = get
    ...         self.__set = set
    ...
    ...     def __get__(self, inst, type=Nic):
    ...         zwróć self.__get(inst)
    ...
    ...     def __set__(self, inst, value):
    ...         jeżeli self.__set jest Nic:
    ...             podnieś AttributeError("this attribute jest read-only")
    ...         zwróć self.__set(inst, value)

Now let's define a klasa przy an attribute x defined by a pair of methods,
getx() oraz setx():

    >>> klasa C(object):
    ...
    ...     def __init__(self):
    ...         self.__x = 0
    ...
    ...     def getx(self):
    ...         zwróć self.__x
    ...
    ...     def setx(self, x):
    ...         jeżeli x < 0: x = 0
    ...         self.__x = x
    ...
    ...     x = property(getx, setx)

Here's a small demonstration:

    >>> a = C()
    >>> a.x = 10
    >>> print(a.x)
    10
    >>> a.x = -10
    >>> print(a.x)
    0
    >>>

Hmm -- property jest builtin now, so let's try it that way too.

    >>> usuń property  # unmask the builtin
    >>> property
    <class 'property'>

    >>> klasa C(object):
    ...     def __init__(self):
    ...         self.__x = 0
    ...     def getx(self):
    ...         zwróć self.__x
    ...     def setx(self, x):
    ...         jeżeli x < 0: x = 0
    ...         self.__x = x
    ...     x = property(getx, setx)


    >>> a = C()
    >>> a.x = 10
    >>> print(a.x)
    10
    >>> a.x = -10
    >>> print(a.x)
    0
    >>>
"""

test_6 = """

Method resolution order

This example jest implicit w the writeup.

>>> klasa A:    # implicit new-style class
...     def save(self):
...         print("called A.save()")
>>> klasa B(A):
...     dalej
>>> klasa C(A):
...     def save(self):
...         print("called C.save()")
>>> klasa D(B, C):
...     dalej

>>> D().save()
called C.save()

>>> klasa A(object):  # explicit new-style class
...     def save(self):
...         print("called A.save()")
>>> klasa B(A):
...     dalej
>>> klasa C(A):
...     def save(self):
...         print("called C.save()")
>>> klasa D(B, C):
...     dalej

>>> D().save()
called C.save()
"""

klasa A(object):
    def m(self):
        zwróć "A"

klasa B(A):
    def m(self):
        zwróć "B" + super(B, self).m()

klasa C(A):
    def m(self):
        zwróć "C" + super(C, self).m()

klasa D(C, B):
    def m(self):
        zwróć "D" + super(D, self).m()


test_7 = """

Cooperative methods oraz "super"

>>> print(D().m()) # "DCBA"
DCBA
"""

test_8 = """

Backwards incompatibilities

>>> klasa A:
...     def foo(self):
...         print("called A.foo()")

>>> klasa B(A):
...     dalej

>>> klasa C(A):
...     def foo(self):
...         B.foo(self)

>>> C().foo()
called A.foo()

>>> klasa C(A):
...     def foo(self):
...         A.foo(self)
>>> C().foo()
called A.foo()
"""

__test__ = {"tut1": test_1,
            "tut2": test_2,
            "tut3": test_3,
            "tut4": test_4,
            "tut5": test_5,
            "tut6": test_6,
            "tut7": test_7,
            "tut8": test_8}

# Magic test name that regrtest.py invokes *after* importing this module.
# This worms around a bootstrap problem.
# Note that doctest oraz regrtest both look w sys.argv dla a "-v" argument,
# so this works jako expected w both ways of running regrtest.
def test_main(verbose=Nic):
    # Obscure:  zaimportuj this module jako test.test_descrtut instead of as
    # plain test_descrtut because the name of this module works its way
    # into the doctest examples, oraz unless the full test.test_descrtut
    # business jest used the name can change depending on how the test jest
    # invoked.
    z test zaimportuj support, test_descrtut
    support.run_doctest(test_descrtut, verbose)

# This part isn't needed dla regrtest, but dla running the test directly.
jeżeli __name__ == "__main__":
    test_main(1)
