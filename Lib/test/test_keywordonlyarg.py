"""Unit tests dla the keyword only argument specified w PEP 3102."""

__author__ = "Jiwon Seo"
__email__ = "seojiwon at gmail dot com"

zaimportuj unittest

def posonly_sum(pos_arg1, *arg, **kwarg):
    zwróć pos_arg1 + sum(arg) + sum(kwarg.values())
def keywordonly_sum(*, k1=0, k2):
    zwróć k1 + k2
def keywordonly_nodefaults_sum(*, k1, k2):
    zwróć k1 + k2
def keywordonly_and_kwarg_sum(*, k1, k2, **kwarg):
    zwróć k1 + k2 + sum(kwarg.values())
def mixedargs_sum(a, b=0, *arg, k1, k2=0):
    zwróć a + b + k1 + k2 + sum(arg)
def mixedargs_sum2(a, b=0, *arg, k1, k2=0, **kwargs):
    zwróć a + b + k1 + k2 + sum(arg) + sum(kwargs.values())

def sortnum(*nums, reverse=Nieprawda):
    zwróć sorted(list(nums), reverse=reverse)

def sortwords(*words, reverse=Nieprawda, **kwargs):
    zwróć sorted(list(words), reverse=reverse)

klasa Foo:
    def __init__(self, *, k1, k2=0):
        self.k1 = k1
        self.k2 = k2
    def set(self, p1, *, k1, k2):
        self.k1 = k1
        self.k2 = k2
    def sum(self):
        zwróć self.k1 + self.k2

klasa KeywordOnlyArgTestCase(unittest.TestCase):
    def assertRaisesSyntaxError(self, codestr):
        def shouldRaiseSyntaxError(s):
            compile(s, "<test>", "single")
        self.assertRaises(SyntaxError, shouldRaiseSyntaxError, codestr)

    def testSyntaxErrorForFunctionDefinition(self):
        self.assertRaisesSyntaxError("def f(p, *):\n  dalej\n")
        self.assertRaisesSyntaxError("def f(p1, *, p1=100):\n  dalej\n")
        self.assertRaisesSyntaxError("def f(p1, *k1, k1=100):\n  dalej\n")
        self.assertRaisesSyntaxError("def f(p1, *, k1, k1=100):\n  dalej\n")
        self.assertRaisesSyntaxError("def f(p1, *, **k1):\n  dalej\n")
        self.assertRaisesSyntaxError("def f(p1, *, k1, **k1):\n  dalej\n")
        self.assertRaisesSyntaxError("def f(p1, *, Nic, **k1):\n  dalej\n")
        self.assertRaisesSyntaxError("def f(p, *, (k1, k2), **kw):\n  dalej\n")

    def testSyntaxForManyArguments(self):
        fundef = "def f("
        dla i w range(255):
            fundef += "i%d, "%i
        fundef += "*, key=100):\n dalej\n"
        self.assertRaisesSyntaxError(fundef)

        fundef2 = "def foo(i,*,"
        dla i w range(255):
            fundef2 += "i%d, "%i
        fundef2 += "lastarg):\n  dalej\n"
        self.assertRaisesSyntaxError(fundef2)

        # exactly 255 arguments, should compile ok
        fundef3 = "def f(i,*,"
        dla i w range(253):
            fundef3 += "i%d, "%i
        fundef3 += "lastarg):\n  dalej\n"
        compile(fundef3, "<test>", "single")

    def testTooManyPositionalErrorMessage(self):
        def f(a, b=Nic, *, c=Nic):
            dalej
        przy self.assertRaises(TypeError) jako exc:
            f(1, 2, 3)
        expected = "f() takes z 1 to 2 positional arguments but 3 were given"
        self.assertEqual(str(exc.exception), expected)

    def testSyntaxErrorForFunctionCall(self):
        self.assertRaisesSyntaxError("f(p, k=1, p2)")
        self.assertRaisesSyntaxError("f(p, k1=50, *(1,2), k1=100)")

    def testRaiseErrorFuncallWithUnexpectedKeywordArgument(self):
        self.assertRaises(TypeError, keywordonly_sum, ())
        self.assertRaises(TypeError, keywordonly_nodefaults_sum, ())
        self.assertRaises(TypeError, Foo, ())
        spróbuj:
            keywordonly_sum(k2=100, non_existing_arg=200)
            self.fail("should podnieś TypeError")
        wyjąwszy TypeError:
            dalej
        spróbuj:
            keywordonly_nodefaults_sum(k2=2)
            self.fail("should podnieś TypeError")
        wyjąwszy TypeError:
            dalej

    def testFunctionCall(self):
        self.assertEqual(1, posonly_sum(1))
        self.assertEqual(1+2, posonly_sum(1,**{"2":2}))
        self.assertEqual(1+2+3, posonly_sum(1,*(2,3)))
        self.assertEqual(1+2+3+4, posonly_sum(1,*(2,3),**{"4":4}))

        self.assertEqual(1, keywordonly_sum(k2=1))
        self.assertEqual(1+2, keywordonly_sum(k1=1, k2=2))

        self.assertEqual(1+2, keywordonly_and_kwarg_sum(k1=1, k2=2))
        self.assertEqual(1+2+3, keywordonly_and_kwarg_sum(k1=1, k2=2, k3=3))
        self.assertEqual(1+2+3+4,
                         keywordonly_and_kwarg_sum(k1=1, k2=2,
                                                    **{"a":3,"b":4}))

        self.assertEqual(1+2, mixedargs_sum(1, k1=2))
        self.assertEqual(1+2+3, mixedargs_sum(1, 2, k1=3))
        self.assertEqual(1+2+3+4, mixedargs_sum(1, 2, k1=3, k2=4))
        self.assertEqual(1+2+3+4+5, mixedargs_sum(1, 2, 3, k1=4, k2=5))

        self.assertEqual(1+2, mixedargs_sum2(1, k1=2))
        self.assertEqual(1+2+3, mixedargs_sum2(1, 2, k1=3))
        self.assertEqual(1+2+3+4, mixedargs_sum2(1, 2, k1=3, k2=4))
        self.assertEqual(1+2+3+4+5, mixedargs_sum2(1, 2, 3, k1=4, k2=5))
        self.assertEqual(1+2+3+4+5+6,
                         mixedargs_sum2(1, 2, 3, k1=4, k2=5, k3=6))
        self.assertEqual(1+2+3+4+5+6,
                         mixedargs_sum2(1, 2, 3, k1=4, **{'k2':5, 'k3':6}))

        self.assertEqual(1, Foo(k1=1).sum())
        self.assertEqual(1+2, Foo(k1=1,k2=2).sum())

        self.assertEqual([1,2,3], sortnum(3,2,1))
        self.assertEqual([3,2,1], sortnum(1,2,3, reverse=Prawda))

        self.assertEqual(['a','b','c'], sortwords('a','c','b'))
        self.assertEqual(['c','b','a'], sortwords('a','c','b', reverse=Prawda))
        self.assertEqual(['c','b','a'],
                         sortwords('a','c','b', reverse=Prawda, ignore='ignore'))

    def testKwDefaults(self):
        def foo(p1,p2=0, *, k1, k2=0):
            zwróć p1 + p2 + k1 + k2

        self.assertEqual(2, foo.__code__.co_kwonlyargcount)
        self.assertEqual({"k2":0}, foo.__kwdefaults__)
        foo.__kwdefaults__ = {"k1":0}
        spróbuj:
            foo(1,k1=10)
            self.fail("__kwdefaults__ jest nie properly changed")
        wyjąwszy TypeError:
            dalej

    def test_kwonly_methods(self):
        klasa Example:
            def f(self, *, k1=1, k2=2):
                zwróć k1, k2

        self.assertEqual(Example().f(k1=1, k2=2), (1, 2))
        self.assertEqual(Example.f(Example(), k1=1, k2=2), (1, 2))
        self.assertRaises(TypeError, Example.f, k1=1, k2=2)

    def test_issue13343(self):
        # The Python compiler must scan all symbols of a function to
        # determine their scope: global, local, cell...
        # This was nie done dla the default values of keyword
        # arguments w a lambda definition, oraz the following line
        # used to fail przy a SystemError.
        lambda *, k1=unittest: Nic

    def test_mangling(self):
        klasa X:
            def f(self, *, __a=42):
                zwróć __a
        self.assertEqual(X().f(), 42)

    def test_default_evaluation_order(self):
        # See issue 16967
        a = 42
        przy self.assertRaises(NameError) jako err:
            def f(v=a, x=b, *, y=c, z=d):
                dalej
        self.assertEqual(str(err.exception), "name 'b' jest nie defined")
        przy self.assertRaises(NameError) jako err:
            f = lambda v=a, x=b, *, y=c, z=d: Nic
        self.assertEqual(str(err.exception), "name 'b' jest nie defined")


jeżeli __name__ == "__main__":
    unittest.main()
