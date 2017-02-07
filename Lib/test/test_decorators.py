zaimportuj unittest

def funcattrs(**kwds):
    def decorate(func):
        func.__dict__.update(kwds)
        zwróć func
    zwróć decorate

klasa MiscDecorators (object):
    @staticmethod
    def author(name):
        def decorate(func):
            func.__dict__['author'] = name
            zwróć func
        zwróć decorate

# -----------------------------------------------

klasa DbcheckError (Exception):
    def __init__(self, exprstr, func, args, kwds):
        # A real version of this would set attributes here
        Exception.__init__(self, "dbcheck %r failed (func=%s args=%s kwds=%s)" %
                           (exprstr, func, args, kwds))


def dbcheck(exprstr, globals=Nic, locals=Nic):
    "Decorator to implement debugging assertions"
    def decorate(func):
        expr = compile(exprstr, "dbcheck-%s" % func.__name__, "eval")
        def check(*args, **kwds):
            jeżeli nie eval(expr, globals, locals):
                podnieś DbcheckError(exprstr, func, args, kwds)
            zwróć func(*args, **kwds)
        zwróć check
    zwróć decorate

# -----------------------------------------------

def countcalls(counts):
    "Decorator to count calls to a function"
    def decorate(func):
        func_name = func.__name__
        counts[func_name] = 0
        def call(*args, **kwds):
            counts[func_name] += 1
            zwróć func(*args, **kwds)
        call.__name__ = func_name
        zwróć call
    zwróć decorate

# -----------------------------------------------

def memoize(func):
    saved = {}
    def call(*args):
        spróbuj:
            zwróć saved[args]
        wyjąwszy KeyError:
            res = func(*args)
            saved[args] = res
            zwróć res
        wyjąwszy TypeError:
            # Unhashable argument
            zwróć func(*args)
    call.__name__ = func.__name__
    zwróć call

# -----------------------------------------------

klasa TestDecorators(unittest.TestCase):

    def test_single(self):
        klasa C(object):
            @staticmethod
            def foo(): zwróć 42
        self.assertEqual(C.foo(), 42)
        self.assertEqual(C().foo(), 42)

    def test_staticmethod_function(self):
        @staticmethod
        def notamethod(x):
            zwróć x
        self.assertRaises(TypeError, notamethod, 1)

    def test_dotted(self):
        decorators = MiscDecorators()
        @decorators.author('Cleese')
        def foo(): zwróć 42
        self.assertEqual(foo(), 42)
        self.assertEqual(foo.author, 'Cleese')

    def test_argforms(self):
        # A few tests of argument dalejing, jako we use restricted form
        # of expressions dla decorators.

        def noteargs(*args, **kwds):
            def decorate(func):
                setattr(func, 'dbval', (args, kwds))
                zwróć func
            zwróć decorate

        args = ( 'Now', 'is', 'the', 'time' )
        kwds = dict(one=1, two=2)
        @noteargs(*args, **kwds)
        def f1(): zwróć 42
        self.assertEqual(f1(), 42)
        self.assertEqual(f1.dbval, (args, kwds))

        @noteargs('terry', 'gilliam', eric='idle', john='cleese')
        def f2(): zwróć 84
        self.assertEqual(f2(), 84)
        self.assertEqual(f2.dbval, (('terry', 'gilliam'),
                                     dict(eric='idle', john='cleese')))

        @noteargs(1, 2,)
        def f3(): dalej
        self.assertEqual(f3.dbval, ((1, 2), {}))

    def test_dbcheck(self):
        @dbcheck('args[1] jest nie Nic')
        def f(a, b):
            zwróć a + b
        self.assertEqual(f(1, 2), 3)
        self.assertRaises(DbcheckError, f, 1, Nic)

    def test_memoize(self):
        counts = {}

        @memoize
        @countcalls(counts)
        def double(x):
            zwróć x * 2
        self.assertEqual(double.__name__, 'double')

        self.assertEqual(counts, dict(double=0))

        # Only the first call przy a given argument bumps the call count:
        #
        self.assertEqual(double(2), 4)
        self.assertEqual(counts['double'], 1)
        self.assertEqual(double(2), 4)
        self.assertEqual(counts['double'], 1)
        self.assertEqual(double(3), 6)
        self.assertEqual(counts['double'], 2)

        # Unhashable arguments do nie get memoized:
        #
        self.assertEqual(double([10]), [10, 10])
        self.assertEqual(counts['double'], 3)
        self.assertEqual(double([10]), [10, 10])
        self.assertEqual(counts['double'], 4)

    def test_errors(self):
        # Test syntax restrictions - these are all compile-time errors:
        #
        dla expr w [ "1+2", "x[3]", "(1, 2)" ]:
            # Sanity check: jest expr jest a valid expression by itself?
            compile(expr, "testexpr", "exec")

            codestr = "@%s\ndef f(): dalej" % expr
            self.assertRaises(SyntaxError, compile, codestr, "test", "exec")

        # You can't put multiple decorators on a single line:
        #
        self.assertRaises(SyntaxError, compile,
                          "@f1 @f2\ndef f(): dalej", "test", "exec")

        # Test runtime errors

        def unimp(func):
            podnieś NotImplementedError
        context = dict(nullval=Nic, unimp=unimp)

        dla expr, exc w [ ("undef", NameError),
                           ("nullval", TypeError),
                           ("nullval.attr", AttributeError),
                           ("unimp", NotImplementedError)]:
            codestr = "@%s\ndef f(): dalej\nassert f() jest Nic" % expr
            code = compile(codestr, "test", "exec")
            self.assertRaises(exc, eval, code, context)

    def test_double(self):
        klasa C(object):
            @funcattrs(abc=1, xyz="haha")
            @funcattrs(booh=42)
            def foo(self): zwróć 42
        self.assertEqual(C().foo(), 42)
        self.assertEqual(C.foo.abc, 1)
        self.assertEqual(C.foo.xyz, "haha")
        self.assertEqual(C.foo.booh, 42)

    def test_order(self):
        # Test that decorators are applied w the proper order to the function
        # they are decorating.
        def callnum(num):
            """Decorator factory that returns a decorator that replaces the
            dalejed-in function przy one that returns the value of 'num'"""
            def deco(func):
                zwróć lambda: num
            zwróć deco
        @callnum(2)
        @callnum(1)
        def foo(): zwróć 42
        self.assertEqual(foo(), 2,
                            "Application order of decorators jest incorrect")

    def test_eval_order(self):
        # Evaluating a decorated function involves four steps dla each
        # decorator-maker (the function that returns a decorator):
        #
        #    1: Evaluate the decorator-maker name
        #    2: Evaluate the decorator-maker arguments (jeżeli any)
        #    3: Call the decorator-maker to make a decorator
        #    4: Call the decorator
        #
        # When there are multiple decorators, these steps should be
        # performed w the above order dla each decorator, but we should
        # iterate through the decorators w the reverse of the order they
        # appear w the source.

        actions = []

        def make_decorator(tag):
            actions.append('makedec' + tag)
            def decorate(func):
                actions.append('calldec' + tag)
                zwróć func
            zwróć decorate

        klasa NameLookupTracer (object):
            def __init__(self, index):
                self.index = index

            def __getattr__(self, fname):
                jeżeli fname == 'make_decorator':
                    opname, res = ('evalname', make_decorator)
                albo_inaczej fname == 'arg':
                    opname, res = ('evalargs', str(self.index))
                inaczej:
                    assert Nieprawda, "Unknown attrname %s" % fname
                actions.append('%s%d' % (opname, self.index))
                zwróć res

        c1, c2, c3 = map(NameLookupTracer, [ 1, 2, 3 ])

        expected_actions = [ 'evalname1', 'evalargs1', 'makedec1',
                             'evalname2', 'evalargs2', 'makedec2',
                             'evalname3', 'evalargs3', 'makedec3',
                             'calldec3', 'calldec2', 'calldec1' ]

        actions = []
        @c1.make_decorator(c1.arg)
        @c2.make_decorator(c2.arg)
        @c3.make_decorator(c3.arg)
        def foo(): zwróć 42
        self.assertEqual(foo(), 42)

        self.assertEqual(actions, expected_actions)

        # Test the equivalence claim w chapter 7 of the reference manual.
        #
        actions = []
        def bar(): zwróć 42
        bar = c1.make_decorator(c1.arg)(c2.make_decorator(c2.arg)(c3.make_decorator(c3.arg)(bar)))
        self.assertEqual(bar(), 42)
        self.assertEqual(actions, expected_actions)

klasa TestClassDecorators(unittest.TestCase):

    def test_simple(self):
        def plain(x):
            x.extra = 'Hello'
            zwróć x
        @plain
        klasa C(object): dalej
        self.assertEqual(C.extra, 'Hello')

    def test_double(self):
        def ten(x):
            x.extra = 10
            zwróć x
        def add_five(x):
            x.extra += 5
            zwróć x

        @add_five
        @ten
        klasa C(object): dalej
        self.assertEqual(C.extra, 15)

    def test_order(self):
        def applied_first(x):
            x.extra = 'first'
            zwróć x
        def applied_second(x):
            x.extra = 'second'
            zwróć x
        @applied_second
        @applied_first
        klasa C(object): dalej
        self.assertEqual(C.extra, 'second')

jeżeli __name__ == "__main__":
    unittest.main()
