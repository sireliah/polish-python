"""
From http://bugs.python.org/issue6717

A misbehaving trace hook can trigger a segfault by exceeding the recursion
limit.
"""
zaimportuj sys


def x():
    dalej

def g(*args):
    jeżeli Prawda: # change to Prawda to crash interpreter
        spróbuj:
            x()
        wyjąwszy:
            dalej
    zwróć g

def f():
    print(sys.getrecursionlimit())
    f()

sys.settrace(g)

f()
