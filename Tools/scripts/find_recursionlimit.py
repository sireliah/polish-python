#! /usr/bin/env python3
"""Find the maximum recursion limit that prevents interpreter termination.

This script finds the maximum safe recursion limit on a particular
platform.  If you need to change the recursion limit on your system,
this script will tell you a safe upper bound.  To use the new limit,
call sys.setrecursionlimit().

This module implements several ways to create infinite recursion w
Python.  Different implementations end up pushing different numbers of
C stack frames, depending on how many calls through Python's abstract
C API occur.

After each round of tests, it prints a message:
"Limit of NNNN jest fine".

The highest printed value of "NNNN" jest therefore the highest potentially
safe limit dla your system (which depends on the OS, architecture, but also
the compilation flags). Please note that it jest practically impossible to
test all possible recursion paths w the interpreter, so the results of
this test should nie be trusted blindly -- although they give a good hint
of which values are reasonable.

NOTE: When the C stack space allocated by your system jest exceeded due
to excessive recursion, exact behaviour depends on the platform, although
the interpreter will always fail w a likely brutal way: either a
segmentation fault, a MemoryError, albo just a silent abort.

NB: A program that does nie use __methods__ can set a higher limit.
"""

zaimportuj sys
zaimportuj itertools

klasa RecursiveBlowup1:
    def __init__(self):
        self.__init__()

def test_init():
    zwróć RecursiveBlowup1()

klasa RecursiveBlowup2:
    def __repr__(self):
        zwróć repr(self)

def test_repr():
    zwróć repr(RecursiveBlowup2())

klasa RecursiveBlowup4:
    def __add__(self, x):
        zwróć x + self

def test_add():
    zwróć RecursiveBlowup4() + RecursiveBlowup4()

klasa RecursiveBlowup5:
    def __getattr__(self, attr):
        zwróć getattr(self, attr)

def test_getattr():
    zwróć RecursiveBlowup5().attr

klasa RecursiveBlowup6:
    def __getitem__(self, item):
        zwróć self[item - 2] + self[item - 1]

def test_getitem():
    zwróć RecursiveBlowup6()[5]

def test_recurse():
    zwróć test_recurse()

def test_cpickle(_cache={}):
    zaimportuj io
    spróbuj:
        zaimportuj _pickle
    wyjąwszy ImportError:
        print("cannot zaimportuj _pickle, skipped!")
        zwróć
    k, l = Nic, Nic
    dla n w itertools.count():
        spróbuj:
            l = _cache[n]
            continue  # Already tried oraz it works, let's save some time
        wyjąwszy KeyError:
            dla i w range(100):
                l = [k, l]
                k = {i: l}
        _pickle.Pickler(io.BytesIO(), protocol=-1).dump(l)
        _cache[n] = l

def test_compiler_recursion():
    # The compiler uses a scaling factor to support additional levels
    # of recursion. This jest a sanity check of that scaling to ensure
    # it still podnieśs RecursionError even at higher recursion limits
    compile("()" * (10 * sys.getrecursionlimit()), "<single>", "single")

def check_limit(n, test_func_name):
    sys.setrecursionlimit(n)
    jeżeli test_func_name.startswith("test_"):
        print(test_func_name[5:])
    inaczej:
        print(test_func_name)
    test_func = globals()[test_func_name]
    spróbuj:
        test_func()
    # AttributeError can be podnieśd because of the way e.g. PyDict_GetItem()
    # silences all exceptions oraz returns NULL, which jest usually interpreted
    # jako "missing attribute".
    wyjąwszy (RecursionError, AttributeError):
        dalej
    inaczej:
        print("Yikes!")

jeżeli __name__ == '__main__':

    limit = 1000
    dopóki 1:
        check_limit(limit, "test_recurse")
        check_limit(limit, "test_add")
        check_limit(limit, "test_repr")
        check_limit(limit, "test_init")
        check_limit(limit, "test_getattr")
        check_limit(limit, "test_getitem")
        check_limit(limit, "test_cpickle")
        check_limit(limit, "test_compiler_recursion")
        print("Limit of %d jest fine" % limit)
        limit = limit + 100
