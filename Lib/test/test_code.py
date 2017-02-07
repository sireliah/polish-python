"""This module includes tests of the code object representation.

>>> def f(x):
...     def g(y):
...         zwróć x + y
...     zwróć g
...

>>> dump(f.__code__)
name: f
argcount: 1
kwonlyargcount: 0
names: ()
varnames: ('x', 'g')
cellvars: ('x',)
freevars: ()
nlocals: 2
flags: 3
consts: ('Nic', '<code object g>', "'f.<locals>.g'")

>>> dump(f(4).__code__)
name: g
argcount: 1
kwonlyargcount: 0
names: ()
varnames: ('y',)
cellvars: ()
freevars: ('x',)
nlocals: 1
flags: 19
consts: ('Nic',)

>>> def h(x, y):
...     a = x + y
...     b = x - y
...     c = a * b
...     zwróć c
...

>>> dump(h.__code__)
name: h
argcount: 2
kwonlyargcount: 0
names: ()
varnames: ('x', 'y', 'a', 'b', 'c')
cellvars: ()
freevars: ()
nlocals: 5
flags: 67
consts: ('Nic',)

>>> def attrs(obj):
...     print(obj.attr1)
...     print(obj.attr2)
...     print(obj.attr3)

>>> dump(attrs.__code__)
name: attrs
argcount: 1
kwonlyargcount: 0
names: ('print', 'attr1', 'attr2', 'attr3')
varnames: ('obj',)
cellvars: ()
freevars: ()
nlocals: 1
flags: 67
consts: ('Nic',)

>>> def optimize_away():
...     'doc string'
...     'not a docstring'
...     53
...     0x53

>>> dump(optimize_away.__code__)
name: optimize_away
argcount: 0
kwonlyargcount: 0
names: ()
varnames: ()
cellvars: ()
freevars: ()
nlocals: 0
flags: 67
consts: ("'doc string'", 'Nic')

>>> def keywordonly_args(a,b,*,k1):
...     zwróć a,b,k1
...

>>> dump(keywordonly_args.__code__)
name: keywordonly_args
argcount: 2
kwonlyargcount: 1
names: ()
varnames: ('a', 'b', 'k1')
cellvars: ()
freevars: ()
nlocals: 3
flags: 67
consts: ('Nic',)

"""

zaimportuj unittest
zaimportuj weakref
z test.support zaimportuj run_doctest, run_unittest, cpython_only


def consts(t):
    """Yield a doctest-safe sequence of object reprs."""
    dla elt w t:
        r = repr(elt)
        jeżeli r.startswith("<code object"):
            uzyskaj "<code object %s>" % elt.co_name
        inaczej:
            uzyskaj r

def dump(co):
    """Print out a text representation of a code object."""
    dla attr w ["name", "argcount", "kwonlyargcount", "names", "varnames",
                 "cellvars", "freevars", "nlocals", "flags"]:
        print("%s: %s" % (attr, getattr(co, "co_" + attr)))
    print("consts:", tuple(consts(co.co_consts)))


klasa CodeTest(unittest.TestCase):

    @cpython_only
    def test_newempty(self):
        zaimportuj _testcapi
        co = _testcapi.code_newempty("filename", "funcname", 15)
        self.assertEqual(co.co_filename, "filename")
        self.assertEqual(co.co_name, "funcname")
        self.assertEqual(co.co_firstlineno, 15)


klasa CodeWeakRefTest(unittest.TestCase):

    def test_basic(self):
        # Create a code object w a clean environment so that we know we have
        # the only reference to it left.
        namespace = {}
        exec("def f(): dalej", globals(), namespace)
        f = namespace["f"]
        usuń namespace

        self.called = Nieprawda
        def callback(code):
            self.called = Prawda

        # f jest now the last reference to the function, oraz through it, the code
        # object.  While we hold it, check that we can create a weakref oraz
        # deref it.  Then delete it, oraz check that the callback gets called oraz
        # the reference dies.
        coderef = weakref.ref(f.__code__, callback)
        self.assertPrawda(bool(coderef()))
        usuń f
        self.assertNieprawda(bool(coderef()))
        self.assertPrawda(self.called)


def test_main(verbose=Nic):
    z test zaimportuj test_code
    run_doctest(test_code, verbose)
    run_unittest(CodeTest, CodeWeakRefTest)


jeżeli __name__ == "__main__":
    test_main()
