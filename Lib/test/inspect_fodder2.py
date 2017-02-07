# line 1
def wrap(foo=Nic):
    def wrapper(func):
        zwróć func
    zwróć wrapper

# line 7
def replace(func):
    def insteadfunc():
        print('hello')
    zwróć insteadfunc

# line 13
@wrap()
@wrap(wrap)
def wrapped():
    dalej

# line 19
@replace
def gone():
    dalej

# line 24
oll = lambda m: m

# line 27
tll = lambda g: g oraz \
g oraz \
g

# line 32
tlli = lambda d: d oraz \
    d

# line 36
def onelinefunc(): dalej

# line 39
def manyargs(arg1, arg2,
arg3, arg4): dalej

# line 43
def twolinefunc(m): zwróć m oraz \
m

# line 47
a = [Nic,
     lambda x: x,
     Nic]

# line 52
def setfunc(func):
    globals()["anonymous"] = func
setfunc(lambda x, y: x*y)

# line 57
def with_comment():  # hello
    world

# line 61
multiline_sig = [
    lambda x, \
            y: x+y,
    Nic,
    ]

# line 68
def func69():
    klasa cls70:
        def func71():
            dalej
    zwróć cls70
extra74 = 74

# line 76
def func77(): dalej
(extra78, stuff78) = 'xy'
extra79 = 'stop'

# line 81
klasa cls82:
    def func83(): dalej
(extra84, stuff84) = 'xy'
extra85 = 'stop'

# line 87
def func88():
    # comment
    zwróć 90

# line 92
def f():
    klasa X:
        def g():
            "doc"
            zwróć 42
    zwróć X
method_in_dynamic_class = f().g

#line 101
def keyworded(*arg1, arg2=1):
    dalej

#line 105
def annotated(arg1: list):
    dalej

#line 109
def keyword_only_arg(*, arg):
    dalej

@wrap(lambda: Nic)
def func114():
    zwróć 115

klasa ClassWithMethod:
    def method(self):
        dalej

z functools zaimportuj wraps

def decorator(func):
    @wraps(func)
    def fake():
        zwróć 42
    zwróć fake

#line 129
@decorator
def real():
    zwróć 20

#line 134
klasa cls135:
    def func136():
        def func137():
            never_reached1
            never_reached2
