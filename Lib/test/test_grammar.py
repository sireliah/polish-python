# Python test set -- part 1, grammar.
# This just tests whether the parser accepts them all.

z test.support zaimportuj check_syntax_error
zaimportuj inspect
zaimportuj unittest
zaimportuj sys
# testing zaimportuj *
z sys zaimportuj *


klasa TokenTests(unittest.TestCase):

    def test_backslash(self):
        # Backslash means line continuation:
        x = 1 \
        + 1
        self.assertEqual(x, 2, 'backslash dla line continuation')

        # Backslash does nie means continuation w comments :\
        x = 0
        self.assertEqual(x, 0, 'backslash ending comment')

    def test_plain_integers(self):
        self.assertEqual(type(000), type(0))
        self.assertEqual(0xff, 255)
        self.assertEqual(0o377, 255)
        self.assertEqual(2147483647, 0o17777777777)
        self.assertEqual(0b1001, 9)
        # "0x" jest nie a valid literal
        self.assertRaises(SyntaxError, eval, "0x")
        z sys zaimportuj maxsize
        jeżeli maxsize == 2147483647:
            self.assertEqual(-2147483647-1, -0o20000000000)
            # XXX -2147483648
            self.assertPrawda(0o37777777777 > 0)
            self.assertPrawda(0xffffffff > 0)
            self.assertPrawda(0b1111111111111111111111111111111 > 0)
            dla s w ('2147483648', '0o40000000000', '0x100000000',
                      '0b10000000000000000000000000000000'):
                spróbuj:
                    x = eval(s)
                wyjąwszy OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        albo_inaczej maxsize == 9223372036854775807:
            self.assertEqual(-9223372036854775807-1, -0o1000000000000000000000)
            self.assertPrawda(0o1777777777777777777777 > 0)
            self.assertPrawda(0xffffffffffffffff > 0)
            self.assertPrawda(0b11111111111111111111111111111111111111111111111111111111111111 > 0)
            dla s w '9223372036854775808', '0o2000000000000000000000', \
                     '0x10000000000000000', \
                     '0b100000000000000000000000000000000000000000000000000000000000000':
                spróbuj:
                    x = eval(s)
                wyjąwszy OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        inaczej:
            self.fail('Weird maxsize value %r' % maxsize)

    def test_long_integers(self):
        x = 0
        x = 0xffffffffffffffff
        x = 0Xffffffffffffffff
        x = 0o77777777777777777
        x = 0O77777777777777777
        x = 123456789012345678901234567890
        x = 0b100000000000000000000000000000000000000000000000000000000000000000000
        x = 0B111111111111111111111111111111111111111111111111111111111111111111111

    def test_floats(self):
        x = 3.14
        x = 314.
        x = 0.314
        # XXX x = 000.314
        x = .314
        x = 3e14
        x = 3E14
        x = 3e-14
        x = 3e+14
        x = 3.e14
        x = .3e14
        x = 3.1e4

    def test_float_exponent_tokenization(self):
        # See issue 21642.
        self.assertEqual(1 jeżeli 1inaczej 0, 1)
        self.assertEqual(1 jeżeli 0inaczej 0, 0)
        self.assertRaises(SyntaxError, eval, "0 jeżeli 1Else 0")

    def test_string_literals(self):
        x = ''; y = ""; self.assertPrawda(len(x) == 0 oraz x == y)
        x = '\''; y = "'"; self.assertPrawda(len(x) == 1 oraz x == y oraz ord(x) == 39)
        x = '"'; y = "\""; self.assertPrawda(len(x) == 1 oraz x == y oraz ord(x) == 34)
        x = "doesn't \"shrink\" does it"
        y = 'doesn\'t "shrink" does it'
        self.assertPrawda(len(x) == 24 oraz x == y)
        x = "does \"shrink\" doesn't it"
        y = 'does "shrink" doesn\'t it'
        self.assertPrawda(len(x) == 24 oraz x == y)
        x = """
The "quick"
brown fox
jumps over
the 'lazy' dog.
"""
        y = '\nThe "quick"\nbrown fox\njumps over\nthe \'lazy\' dog.\n'
        self.assertEqual(x, y)
        y = '''
The "quick"
brown fox
jumps over
the 'lazy' dog.
'''
        self.assertEqual(x, y)
        y = "\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the 'lazy' dog.\n\
"
        self.assertEqual(x, y)
        y = '\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the \'lazy\' dog.\n\
'
        self.assertEqual(x, y)

    def test_ellipsis(self):
        x = ...
        self.assertPrawda(x jest Ellipsis)
        self.assertRaises(SyntaxError, eval, ".. .")

    def test_eof_error(self):
        samples = ("def foo(", "\ndef foo(", "def foo(\n")
        dla s w samples:
            przy self.assertRaises(SyntaxError) jako cm:
                compile(s, "<test>", "exec")
            self.assertIn("unexpected EOF", str(cm.exception))

klasa GrammarTests(unittest.TestCase):

    # single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
    # XXX can't test w a script -- this rule jest only used when interactive

    # file_input: (NEWLINE | stmt)* ENDMARKER
    # Being tested jako this very moment this very module

    # expr_input: testlist NEWLINE
    # XXX Hard to test -- used only w calls to input()

    def test_eval_input(self):
        # testlist ENDMARKER
        x = eval('1, 0 albo 1')

    def test_funcdef(self):
        ### [decorators] 'def' NAME parameters ['->' test] ':' suite
        ### decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
        ### decorators: decorator+
        ### parameters: '(' [typedargslist] ')'
        ### typedargslist: ((tfpdef ['=' test] ',')*
        ###                ('*' [tfpdef] (',' tfpdef ['=' test])* [',' '**' tfpdef] | '**' tfpdef)
        ###                | tfpdef ['=' test] (',' tfpdef ['=' test])* [','])
        ### tfpdef: NAME [':' test]
        ### varargslist: ((vfpdef ['=' test] ',')*
        ###              ('*' [vfpdef] (',' vfpdef ['=' test])*  [',' '**' vfpdef] | '**' vfpdef)
        ###              | vfpdef ['=' test] (',' vfpdef ['=' test])* [','])
        ### vfpdef: NAME
        def f1(): dalej
        f1()
        f1(*())
        f1(*(), **{})
        def f2(one_argument): dalej
        def f3(two, arguments): dalej
        self.assertEqual(f2.__code__.co_varnames, ('one_argument',))
        self.assertEqual(f3.__code__.co_varnames, ('two', 'arguments'))
        def a1(one_arg,): dalej
        def a2(two, args,): dalej
        def v0(*rest): dalej
        def v1(a, *rest): dalej
        def v2(a, b, *rest): dalej

        f1()
        f2(1)
        f2(1,)
        f3(1, 2)
        f3(1, 2,)
        v0()
        v0(1)
        v0(1,)
        v0(1,2)
        v0(1,2,3,4,5,6,7,8,9,0)
        v1(1)
        v1(1,)
        v1(1,2)
        v1(1,2,3)
        v1(1,2,3,4,5,6,7,8,9,0)
        v2(1,2)
        v2(1,2,3)
        v2(1,2,3,4)
        v2(1,2,3,4,5,6,7,8,9,0)

        def d01(a=1): dalej
        d01()
        d01(1)
        d01(*(1,))
        d01(*[] albo [2])
        d01(*() albo (), *{} oraz (), **() albo {})
        d01(**{'a':2})
        d01(**{'a':2} albo {})
        def d11(a, b=1): dalej
        d11(1)
        d11(1, 2)
        d11(1, **{'b':2})
        def d21(a, b, c=1): dalej
        d21(1, 2)
        d21(1, 2, 3)
        d21(*(1, 2, 3))
        d21(1, *(2, 3))
        d21(1, 2, *(3,))
        d21(1, 2, **{'c':3})
        def d02(a=1, b=2): dalej
        d02()
        d02(1)
        d02(1, 2)
        d02(*(1, 2))
        d02(1, *(2,))
        d02(1, **{'b':2})
        d02(**{'a': 1, 'b': 2})
        def d12(a, b=1, c=2): dalej
        d12(1)
        d12(1, 2)
        d12(1, 2, 3)
        def d22(a, b, c=1, d=2): dalej
        d22(1, 2)
        d22(1, 2, 3)
        d22(1, 2, 3, 4)
        def d01v(a=1, *rest): dalej
        d01v()
        d01v(1)
        d01v(1, 2)
        d01v(*(1, 2, 3, 4))
        d01v(*(1,))
        d01v(**{'a':2})
        def d11v(a, b=1, *rest): dalej
        d11v(1)
        d11v(1, 2)
        d11v(1, 2, 3)
        def d21v(a, b, c=1, *rest): dalej
        d21v(1, 2)
        d21v(1, 2, 3)
        d21v(1, 2, 3, 4)
        d21v(*(1, 2, 3, 4))
        d21v(1, 2, **{'c': 3})
        def d02v(a=1, b=2, *rest): dalej
        d02v()
        d02v(1)
        d02v(1, 2)
        d02v(1, 2, 3)
        d02v(1, *(2, 3, 4))
        d02v(**{'a': 1, 'b': 2})
        def d12v(a, b=1, c=2, *rest): dalej
        d12v(1)
        d12v(1, 2)
        d12v(1, 2, 3)
        d12v(1, 2, 3, 4)
        d12v(*(1, 2, 3, 4))
        d12v(1, 2, *(3, 4, 5))
        d12v(1, *(2,), **{'c': 3})
        def d22v(a, b, c=1, d=2, *rest): dalej
        d22v(1, 2)
        d22v(1, 2, 3)
        d22v(1, 2, 3, 4)
        d22v(1, 2, 3, 4, 5)
        d22v(*(1, 2, 3, 4))
        d22v(1, 2, *(3, 4, 5))
        d22v(1, *(2, 3), **{'d': 4})

        # keyword argument type tests
        spróbuj:
            str('x', **{b'foo':1 })
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail('Bytes should nie work jako keyword argument names')
        # keyword only argument tests
        def pos0key1(*, key): zwróć key
        pos0key1(key=100)
        def pos2key2(p1, p2, *, k1, k2=100): zwróć p1,p2,k1,k2
        pos2key2(1, 2, k1=100)
        pos2key2(1, 2, k1=100, k2=200)
        pos2key2(1, 2, k2=100, k1=200)
        def pos2key2dict(p1, p2, *, k1=100, k2, **kwarg): zwróć p1,p2,k1,k2,kwarg
        pos2key2dict(1,2,k2=100,tokwarg1=100,tokwarg2=200)
        pos2key2dict(1,2,tokwarg1=100,tokwarg2=200, k2=100)

        # keyword arguments after *arglist
        def f(*args, **kwargs):
            zwróć args, kwargs
        self.assertEqual(f(1, x=2, *[3, 4], y=5), ((1, 3, 4),
                                                    {'x':2, 'y':5}))
        self.assertEqual(f(1, *(2,3), 4), ((1, 2, 3, 4), {}))
        self.assertRaises(SyntaxError, eval, "f(1, x=2, *(3,4), x=5)")
        self.assertEqual(f(**{'eggs':'scrambled', 'spam':'fried'}),
                         ((), {'eggs':'scrambled', 'spam':'fried'}))
        self.assertEqual(f(spam='fried', **{'eggs':'scrambled'}),
                         ((), {'eggs':'scrambled', 'spam':'fried'}))

        # argument annotation tests
        def f(x) -> list: dalej
        self.assertEqual(f.__annotations__, {'return': list})
        def f(x: int): dalej
        self.assertEqual(f.__annotations__, {'x': int})
        def f(*x: str): dalej
        self.assertEqual(f.__annotations__, {'x': str})
        def f(**x: float): dalej
        self.assertEqual(f.__annotations__, {'x': float})
        def f(x, y: 1+2): dalej
        self.assertEqual(f.__annotations__, {'y': 3})
        def f(a, b: 1, c: 2, d): dalej
        self.assertEqual(f.__annotations__, {'b': 1, 'c': 2})
        def f(a, b: 1, c: 2, d, e: 3 = 4, f=5, *g: 6): dalej
        self.assertEqual(f.__annotations__,
                         {'b': 1, 'c': 2, 'e': 3, 'g': 6})
        def f(a, b: 1, c: 2, d, e: 3 = 4, f=5, *g: 6, h: 7, i=8, j: 9 = 10,
              **k: 11) -> 12: dalej
        self.assertEqual(f.__annotations__,
                         {'b': 1, 'c': 2, 'e': 3, 'g': 6, 'h': 7, 'j': 9,
                          'k': 11, 'return': 12})
        # Check dla issue #20625 -- annotations mangling
        klasa Spam:
            def f(self, *, __kw: 1):
                dalej
        klasa Ham(Spam): dalej
        self.assertEqual(Spam.f.__annotations__, {'_Spam__kw': 1})
        self.assertEqual(Ham.f.__annotations__, {'_Spam__kw': 1})
        # Check dla SF Bug #1697248 - mixing decorators oraz a zwróć annotation
        def null(x): zwróć x
        @null
        def f(x) -> list: dalej
        self.assertEqual(f.__annotations__, {'return': list})

        # test MAKE_CLOSURE przy a variety of oparg's
        closure = 1
        def f(): zwróć closure
        def f(x=1): zwróć closure
        def f(*, k=1): zwróć closure
        def f() -> int: zwróć closure

        # Check ast errors w *args oraz *kwargs
        check_syntax_error(self, "f(*g(1=2))")
        check_syntax_error(self, "f(**g(1=2))")

    def test_lambdef(self):
        ### lambdef: 'lambda' [varargslist] ':' test
        l1 = lambda : 0
        self.assertEqual(l1(), 0)
        l2 = lambda : a[d] # XXX just testing the expression
        l3 = lambda : [2 < x dla x w [-1, 3, 0]]
        self.assertEqual(l3(), [0, 1, 0])
        l4 = lambda x = lambda y = lambda z=1 : z : y() : x()
        self.assertEqual(l4(), 1)
        l5 = lambda x, y, z=2: x + y + z
        self.assertEqual(l5(1, 2), 5)
        self.assertEqual(l5(1, 2, 3), 6)
        check_syntax_error(self, "lambda x: x = 2")
        check_syntax_error(self, "lambda (Nic,): Nic")
        l6 = lambda x, y, *, k=20: x+y+k
        self.assertEqual(l6(1,2), 1+2+20)
        self.assertEqual(l6(1,2,k=10), 1+2+10)


    ### stmt: simple_stmt | compound_stmt
    # Tested below

    def test_simple_stmt(self):
        ### simple_stmt: small_stmt (';' small_stmt)* [';']
        x = 1; dalej; usuń x
        def foo():
            # verify statements that end przy semi-colons
            x = 1; dalej; usuń x;
        foo()

    ### small_stmt: expr_stmt | dalej_stmt | del_stmt | flow_stmt | import_stmt | global_stmt | access_stmt
    # Tested below

    def test_expr_stmt(self):
        # (exprlist '=')* exprlist
        1
        1, 2, 3
        x = 1
        x = 1, 2, 3
        x = y = z = 1, 2, 3
        x, y, z = 1, 2, 3
        abc = a, b, c = x, y, z = xyz = 1, 2, (3, 4)

        check_syntax_error(self, "x + 1 = 1")
        check_syntax_error(self, "a + 1 = b + 2")

    # Check the heuristic dla print & exec covers significant cases
    # As well jako placing some limits on false positives
    def test_former_statements_refer_to_builtins(self):
        keywords = "print", "exec"
        # Cases where we want the custom error
        cases = [
            "{} foo",
            "{} {{1:foo}}",
            "jeżeli 1: {} foo",
            "jeżeli 1: {} {{1:foo}}",
            "jeżeli 1:\n    {} foo",
            "jeżeli 1:\n    {} {{1:foo}}",
        ]
        dla keyword w keywords:
            custom_msg = "call to '{}'".format(keyword)
            dla case w cases:
                source = case.format(keyword)
                przy self.subTest(source=source):
                    przy self.assertRaisesRegex(SyntaxError, custom_msg):
                        exec(source)
                source = source.replace("foo", "(foo.)")
                przy self.subTest(source=source):
                    przy self.assertRaisesRegex(SyntaxError, "invalid syntax"):
                        exec(source)

    def test_del_stmt(self):
        # 'del' exprlist
        abc = [1,2,3]
        x, y, z = abc
        xyz = x, y, z

        usuń abc
        usuń x, y, (z, xyz)

    def test_pass_stmt(self):
        # 'pass'
        dalej

    # flow_stmt: przerwij_stmt | continue_stmt | return_stmt | podnieś_stmt
    # Tested below

    def test_break_stmt(self):
        # 'break'
        dopóki 1: przerwij

    def test_continue_stmt(self):
        # 'continue'
        i = 1
        dopóki i: i = 0; kontynuuj

        msg = ""
        dopóki nie msg:
            msg = "ok"
            spróbuj:
                kontynuuj
                msg = "continue failed to continue inside try"
            wyjąwszy:
                msg = "continue inside try called wyjąwszy block"
        jeżeli msg != "ok":
            self.fail(msg)

        msg = ""
        dopóki nie msg:
            msg = "finally block nie called"
            spróbuj:
                kontynuuj
            w_końcu:
                msg = "ok"
        jeżeli msg != "ok":
            self.fail(msg)

    def test_break_continue_loop(self):
        # This test warrants an explanation. It jest a test specifically dla SF bugs
        # #463359 oraz #462937. The bug jest that a 'break' statement executed albo
        # exception podnieśd inside a try/wyjąwszy inside a loop, *after* a kontynuuj
        # statement has been executed w that loop, will cause the wrong number of
        # arguments to be popped off the stack oraz the instruction pointer reset to
        # a very small number (usually 0.) Because of this, the following test
        # *must* written jako a function, oraz the tracking vars *must* be function
        # arguments przy default values. Otherwise, the test will loop oraz loop.

        def test_inner(extra_burning_oil = 1, count=0):
            big_hippo = 2
            dopóki big_hippo:
                count += 1
                spróbuj:
                    jeżeli extra_burning_oil oraz big_hippo == 1:
                        extra_burning_oil -= 1
                        przerwij
                    big_hippo -= 1
                    kontynuuj
                wyjąwszy:
                    podnieś
            jeżeli count > 2 albo big_hippo != 1:
                self.fail("continue then przerwij w try/wyjąwszy w loop broken!")
        test_inner()

    def test_return(self):
        # 'return' [testlist]
        def g1(): zwróć
        def g2(): zwróć 1
        g1()
        x = g2()
        check_syntax_error(self, "class foo:return 1")

    def test_uzyskaj(self):
        # Allowed jako standalone statement
        def g(): uzyskaj 1
        def g(): uzyskaj z ()
        # Allowed jako RHS of assignment
        def g(): x = uzyskaj 1
        def g(): x = uzyskaj z ()
        # Ordinary uzyskaj accepts implicit tuples
        def g(): uzyskaj 1, 1
        def g(): x = uzyskaj 1, 1
        # 'uzyskaj from' does nie
        check_syntax_error(self, "def g(): uzyskaj z (), 1")
        check_syntax_error(self, "def g(): x = uzyskaj z (), 1")
        # Requires parentheses jako subexpression
        def g(): 1, (uzyskaj 1)
        def g(): 1, (uzyskaj z ())
        check_syntax_error(self, "def g(): 1, uzyskaj 1")
        check_syntax_error(self, "def g(): 1, uzyskaj z ()")
        # Requires parentheses jako call argument
        def g(): f((uzyskaj 1))
        def g(): f((uzyskaj 1), 1)
        def g(): f((uzyskaj z ()))
        def g(): f((uzyskaj z ()), 1)
        check_syntax_error(self, "def g(): f(uzyskaj 1)")
        check_syntax_error(self, "def g(): f(uzyskaj 1, 1)")
        check_syntax_error(self, "def g(): f(uzyskaj z ())")
        check_syntax_error(self, "def g(): f(uzyskaj z (), 1)")
        # Not allowed at top level
        check_syntax_error(self, "uzyskaj")
        check_syntax_error(self, "uzyskaj from")
        # Not allowed at klasa scope
        check_syntax_error(self, "class foo:uzyskaj 1")
        check_syntax_error(self, "class foo:uzyskaj z ()")
        # Check annotation refleak on SyntaxError
        check_syntax_error(self, "def g(a:(uzyskaj)): dalej")

    def test_raise(self):
        # 'raise' test [',' test]
        spróbuj: podnieś RuntimeError('just testing')
        wyjąwszy RuntimeError: dalej
        spróbuj: podnieś KeyboardInterrupt
        wyjąwszy KeyboardInterrupt: dalej

    def test_import(self):
        # 'import' dotted_as_names
        zaimportuj sys
        zaimportuj time, sys
        # 'from' dotted_name 'import' ('*' | '(' import_as_names ')' | import_as_names)
        z time zaimportuj time
        z time zaimportuj (time)
        # nie testable inside a function, but already done at top of the module
        # z sys zaimportuj *
        z sys zaimportuj path, argv
        z sys zaimportuj (path, argv)
        z sys zaimportuj (path, argv,)

    def test_global(self):
        # 'global' NAME (',' NAME)*
        global a
        global a, b
        global one, two, three, four, five, six, seven, eight, nine, ten

    def test_nonlocal(self):
        # 'nonlocal' NAME (',' NAME)*
        x = 0
        y = 0
        def f():
            nonlocal x
            nonlocal x, y

    def test_assert(self):
        # assertPrawdastmt: 'assert' test [',' test]
        assert 1
        assert 1, 1
        assert lambda x:x
        assert 1, lambda x:x+1

        spróbuj:
            assert Prawda
        wyjąwszy AssertionError jako e:
            self.fail("'assert Prawda' should nie have podnieśd an AssertionError")

        spróbuj:
            assert Prawda, 'this should always dalej'
        wyjąwszy AssertionError jako e:
            self.fail("'assert Prawda, msg' should nie have "
                      "raised an AssertionError")

    # these tests fail jeżeli python jest run przy -O, so check __debug__
    @unittest.skipUnless(__debug__, "Won't work jeżeli __debug__ jest Nieprawda")
    def testAssert2(self):
        spróbuj:
            assert 0, "msg"
        wyjąwszy AssertionError jako e:
            self.assertEqual(e.args[0], "msg")
        inaczej:
            self.fail("AssertionError nie podnieśd by assert 0")

        spróbuj:
            assert Nieprawda
        wyjąwszy AssertionError jako e:
            self.assertEqual(len(e.args), 0)
        inaczej:
            self.fail("AssertionError nie podnieśd by 'assert Nieprawda'")


    ### compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funcdef | classdef
    # Tested below

    def test_if(self):
        # 'if' test ':' suite ('elif' test ':' suite)* ['inaczej' ':' suite]
        jeżeli 1: dalej
        jeżeli 1: dalej
        inaczej: dalej
        jeżeli 0: dalej
        albo_inaczej 0: dalej
        jeżeli 0: dalej
        albo_inaczej 0: dalej
        albo_inaczej 0: dalej
        albo_inaczej 0: dalej
        inaczej: dalej

    def test_while(self):
        # 'while' test ':' suite ['inaczej' ':' suite]
        dopóki 0: dalej
        dopóki 0: dalej
        inaczej: dalej

        # Issue1920: "dopóki 0" jest optimized away,
        # ensure that the "inaczej" clause jest still present.
        x = 0
        dopóki 0:
            x = 1
        inaczej:
            x = 2
        self.assertEqual(x, 2)

    def test_for(self):
        # 'for' exprlist 'in' exprlist ':' suite ['inaczej' ':' suite]
        dla i w 1, 2, 3: dalej
        dla i, j, k w (): dalej
        inaczej: dalej
        klasa Squares:
            def __init__(self, max):
                self.max = max
                self.sofar = []
            def __len__(self): zwróć len(self.sofar)
            def __getitem__(self, i):
                jeżeli nie 0 <= i < self.max: podnieś IndexError
                n = len(self.sofar)
                dopóki n <= i:
                    self.sofar.append(n*n)
                    n = n+1
                zwróć self.sofar[i]
        n = 0
        dla x w Squares(10): n = n+x
        jeżeli n != 285:
            self.fail('dla over growing sequence')

        result = []
        dla x, w [(1,), (2,), (3,)]:
            result.append(x)
        self.assertEqual(result, [1, 2, 3])

    def test_try(self):
        ### try_stmt: 'try' ':' suite (except_clause ':' suite)+ ['inaczej' ':' suite]
        ###         | 'try' ':' suite 'finally' ':' suite
        ### except_clause: 'except' [expr ['as' expr]]
        spróbuj:
            1/0
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            dalej
        spróbuj: 1/0
        wyjąwszy EOFError: dalej
        wyjąwszy TypeError jako msg: dalej
        wyjąwszy RuntimeError jako msg: dalej
        wyjąwszy: dalej
        inaczej: dalej
        spróbuj: 1/0
        wyjąwszy (EOFError, TypeError, ZeroDivisionError): dalej
        spróbuj: 1/0
        wyjąwszy (EOFError, TypeError, ZeroDivisionError) jako msg: dalej
        spróbuj: dalej
        w_końcu: dalej

    def test_suite(self):
        # simple_stmt | NEWLINE INDENT NEWLINE* (stmt NEWLINE*)+ DEDENT
        jeżeli 1: dalej
        jeżeli 1:
            dalej
        jeżeli 1:
            #
            #
            #
            dalej
            dalej
            #
            dalej
            #

    def test_test(self):
        ### and_test ('or' and_test)*
        ### and_test: not_test ('and' not_test)*
        ### not_test: 'not' not_test | comparison
        jeżeli nie 1: dalej
        jeżeli 1 oraz 1: dalej
        jeżeli 1 albo 1: dalej
        jeżeli nie not nie 1: dalej
        jeżeli nie 1 oraz 1 oraz 1: dalej
        jeżeli 1 oraz 1 albo 1 oraz 1 oraz 1 albo nie 1 oraz 1: dalej

    def test_comparison(self):
        ### comparison: expr (comp_op expr)*
        ### comp_op: '<'|'>'|'=='|'>='|'<='|'!='|'in'|'not' 'in'|'is'|'is' 'not'
        jeżeli 1: dalej
        x = (1 == 1)
        jeżeli 1 == 1: dalej
        jeżeli 1 != 1: dalej
        jeżeli 1 < 1: dalej
        jeżeli 1 > 1: dalej
        jeżeli 1 <= 1: dalej
        jeżeli 1 >= 1: dalej
        jeżeli 1 jest 1: dalej
        jeżeli 1 jest nie 1: dalej
        jeżeli 1 w (): dalej
        jeżeli 1 nie w (): dalej
        jeżeli 1 < 1 > 1 == 1 >= 1 <= 1 != 1 w 1 nie w 1 jest 1 jest nie 1: dalej

    def test_binary_mask_ops(self):
        x = 1 & 1
        x = 1 ^ 1
        x = 1 | 1

    def test_shift_ops(self):
        x = 1 << 1
        x = 1 >> 1
        x = 1 << 1 >> 1

    def test_additive_ops(self):
        x = 1
        x = 1 + 1
        x = 1 - 1 - 1
        x = 1 - 1 + 1 - 1 + 1

    def test_multiplicative_ops(self):
        x = 1 * 1
        x = 1 / 1
        x = 1 % 1
        x = 1 / 1 * 1 % 1

    def test_unary_ops(self):
        x = +1
        x = -1
        x = ~1
        x = ~1 ^ 1 & 1 | 1 & 1 ^ -1
        x = -1*1/1 + 1*1 - ---1*1

    def test_selectors(self):
        ### trailer: '(' [testlist] ')' | '[' subscript ']' | '.' NAME
        ### subscript: expr | [expr] ':' [expr]

        zaimportuj sys, time
        c = sys.path[0]
        x = time.time()
        x = sys.modules['time'].time()
        a = '01234'
        c = a[0]
        c = a[-1]
        s = a[0:5]
        s = a[:5]
        s = a[0:]
        s = a[:]
        s = a[-5:]
        s = a[:-1]
        s = a[-4:-3]
        # A rough test of SF bug 1333982.  http://python.org/sf/1333982
        # The testing here jest fairly incomplete.
        # Test cases should include: commas przy 1 oraz 2 colons
        d = {}
        d[1] = 1
        d[1,] = 2
        d[1,2] = 3
        d[1,2,3] = 4
        L = list(d)
        L.sort(key=lambda x: x jeżeli isinstance(x, tuple) inaczej ())
        self.assertEqual(str(L), '[1, (1,), (1, 2), (1, 2, 3)]')

    def test_atoms(self):
        ### atom: '(' [testlist] ')' | '[' [testlist] ']' | '{' [dictsetmaker] '}' | NAME | NUMBER | STRING
        ### dictsetmaker: (test ':' test (',' test ':' test)* [',']) | (test (',' test)* [','])

        x = (1)
        x = (1 albo 2 albo 3)
        x = (1 albo 2 albo 3, 2, 3)

        x = []
        x = [1]
        x = [1 albo 2 albo 3]
        x = [1 albo 2 albo 3, 2, 3]
        x = []

        x = {}
        x = {'one': 1}
        x = {'one': 1,}
        x = {'one' albo 'two': 1 albo 2}
        x = {'one': 1, 'two': 2}
        x = {'one': 1, 'two': 2,}
        x = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}

        x = {'one'}
        x = {'one', 1,}
        x = {'one', 'two', 'three'}
        x = {2, 3, 4,}

        x = x
        x = 'x'
        x = 123

    ### exprlist: expr (',' expr)* [',']
    ### testlist: test (',' test)* [',']
    # These have been exercised enough above

    def test_classdef(self):
        # 'class' NAME ['(' [testlist] ')'] ':' suite
        klasa B: dalej
        klasa B2(): dalej
        klasa C1(B): dalej
        klasa C2(B): dalej
        klasa D(C1, C2, B): dalej
        klasa C:
            def meth1(self): dalej
            def meth2(self, arg): dalej
            def meth3(self, a1, a2): dalej

        # decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
        # decorators: decorator+
        # decorated: decorators (classdef | funcdef)
        def class_decorator(x): zwróć x
        @class_decorator
        klasa G: dalej

    def test_dictcomps(self):
        # dictorsetmaker: ( (test ':' test (comp_dla |
        #                                   (',' test ':' test)* [','])) |
        #                   (test (comp_dla | (',' test)* [','])) )
        nums = [1, 2, 3]
        self.assertEqual({i:i+1 dla i w nums}, {1: 2, 2: 3, 3: 4})

    def test_listcomps(self):
        # list comprehension tests
        nums = [1, 2, 3, 4, 5]
        strs = ["Apple", "Banana", "Coconut"]
        spcs = ["  Apple", " Banana ", "Coco  nut  "]

        self.assertEqual([s.strip() dla s w spcs], ['Apple', 'Banana', 'Coco  nut'])
        self.assertEqual([3 * x dla x w nums], [3, 6, 9, 12, 15])
        self.assertEqual([x dla x w nums jeżeli x > 2], [3, 4, 5])
        self.assertEqual([(i, s) dla i w nums dla s w strs],
                         [(1, 'Apple'), (1, 'Banana'), (1, 'Coconut'),
                          (2, 'Apple'), (2, 'Banana'), (2, 'Coconut'),
                          (3, 'Apple'), (3, 'Banana'), (3, 'Coconut'),
                          (4, 'Apple'), (4, 'Banana'), (4, 'Coconut'),
                          (5, 'Apple'), (5, 'Banana'), (5, 'Coconut')])
        self.assertEqual([(i, s) dla i w nums dla s w [f dla f w strs jeżeli "n" w f]],
                         [(1, 'Banana'), (1, 'Coconut'), (2, 'Banana'), (2, 'Coconut'),
                          (3, 'Banana'), (3, 'Coconut'), (4, 'Banana'), (4, 'Coconut'),
                          (5, 'Banana'), (5, 'Coconut')])
        self.assertEqual([(lambda a:[a**i dla i w range(a+1)])(j) dla j w range(5)],
                         [[1], [1, 1], [1, 2, 4], [1, 3, 9, 27], [1, 4, 16, 64, 256]])

        def test_in_func(l):
            zwróć [0 < x < 3 dla x w l jeżeli x > 2]

        self.assertEqual(test_in_func(nums), [Nieprawda, Nieprawda, Nieprawda])

        def test_nested_front():
            self.assertEqual([[y dla y w [x, x + 1]] dla x w [1,3,5]],
                             [[1, 2], [3, 4], [5, 6]])

        test_nested_front()

        check_syntax_error(self, "[i, s dla i w nums dla s w strs]")
        check_syntax_error(self, "[x jeżeli y]")

        suppliers = [
          (1, "Boeing"),
          (2, "Ford"),
          (3, "Macdonalds")
        ]

        parts = [
          (10, "Airliner"),
          (20, "Engine"),
          (30, "Cheeseburger")
        ]

        suppart = [
          (1, 10), (1, 20), (2, 20), (3, 30)
        ]

        x = [
          (sname, pname)
            dla (sno, sname) w suppliers
              dla (pno, pname) w parts
                dla (sp_sno, sp_pno) w suppart
                  jeżeli sno == sp_sno oraz pno == sp_pno
        ]

        self.assertEqual(x, [('Boeing', 'Airliner'), ('Boeing', 'Engine'), ('Ford', 'Engine'),
                             ('Macdonalds', 'Cheeseburger')])

    def test_genexps(self):
        # generator expression tests
        g = ([x dla x w range(10)] dla x w range(1))
        self.assertEqual(next(g), [x dla x w range(10)])
        spróbuj:
            next(g)
            self.fail('should produce StopIteration exception')
        wyjąwszy StopIteration:
            dalej

        a = 1
        spróbuj:
            g = (a dla d w a)
            next(g)
            self.fail('should produce TypeError')
        wyjąwszy TypeError:
            dalej

        self.assertEqual(list((x, y) dla x w 'abcd' dla y w 'abcd'), [(x, y) dla x w 'abcd' dla y w 'abcd'])
        self.assertEqual(list((x, y) dla x w 'ab' dla y w 'xy'), [(x, y) dla x w 'ab' dla y w 'xy'])

        a = [x dla x w range(10)]
        b = (x dla x w (y dla y w a))
        self.assertEqual(sum(b), sum([x dla x w range(10)]))

        self.assertEqual(sum(x**2 dla x w range(10)), sum([x**2 dla x w range(10)]))
        self.assertEqual(sum(x*x dla x w range(10) jeżeli x%2), sum([x*x dla x w range(10) jeżeli x%2]))
        self.assertEqual(sum(x dla x w (y dla y w range(10))), sum([x dla x w range(10)]))
        self.assertEqual(sum(x dla x w (y dla y w (z dla z w range(10)))), sum([x dla x w range(10)]))
        self.assertEqual(sum(x dla x w [y dla y w (z dla z w range(10))]), sum([x dla x w range(10)]))
        self.assertEqual(sum(x dla x w (y dla y w (z dla z w range(10) jeżeli Prawda)) jeżeli Prawda), sum([x dla x w range(10)]))
        self.assertEqual(sum(x dla x w (y dla y w (z dla z w range(10) jeżeli Prawda) jeżeli Nieprawda) jeżeli Prawda), 0)
        check_syntax_error(self, "foo(x dla x w range(10), 100)")
        check_syntax_error(self, "foo(100, x dla x w range(10))")

    def test_comprehension_specials(self):
        # test dla outmost iterable precomputation
        x = 10; g = (i dla i w range(x)); x = 5
        self.assertEqual(len(list(g)), 10)

        # This should hold, since we're only precomputing outmost iterable.
        x = 10; t = Nieprawda; g = ((i,j) dla i w range(x) jeżeli t dla j w range(x))
        x = 5; t = Prawda;
        self.assertEqual([(i,j) dla i w range(10) dla j w range(5)], list(g))

        # Grammar allows multiple adjacent 'if's w listcomps oraz genexps,
        # even though it's silly. Make sure it works (ifinaczej broke this.)
        self.assertEqual([ x dla x w range(10) jeżeli x % 2 jeżeli x % 3 ], [1, 5, 7])
        self.assertEqual(list(x dla x w range(10) jeżeli x % 2 jeżeli x % 3), [1, 5, 7])

        # verify unpacking single element tuples w listcomp/genexp.
        self.assertEqual([x dla x, w [(4,), (5,), (6,)]], [4, 5, 6])
        self.assertEqual(list(x dla x, w [(7,), (8,), (9,)]), [7, 8, 9])

    def test_with_statement(self):
        klasa manager(object):
            def __enter__(self):
                zwróć (1, 2)
            def __exit__(self, *args):
                dalej

        przy manager():
            dalej
        przy manager() jako x:
            dalej
        przy manager() jako (x, y):
            dalej
        przy manager(), manager():
            dalej
        przy manager() jako x, manager() jako y:
            dalej
        przy manager() jako x, manager():
            dalej

    def test_if_inaczej_expr(self):
        # Test ifinaczej expressions w various cases
        def _checkeval(msg, ret):
            "helper to check that evaluation of expressions jest done correctly"
            print(x)
            zwróć ret

        # the next line jest nie allowed anymore
        #self.assertEqual([ x() dla x w lambda: Prawda, lambda: Nieprawda jeżeli x() ], [Prawda])
        self.assertEqual([ x() dla x w (lambda: Prawda, lambda: Nieprawda) jeżeli x() ], [Prawda])
        self.assertEqual([ x(Nieprawda) dla x w (lambda x: Nieprawda jeżeli x inaczej Prawda, lambda x: Prawda jeżeli x inaczej Nieprawda) jeżeli x(Nieprawda) ], [Prawda])
        self.assertEqual((5 jeżeli 1 inaczej _checkeval("check 1", 0)), 5)
        self.assertEqual((_checkeval("check 2", 0) jeżeli 0 inaczej 5), 5)
        self.assertEqual((5 oraz 6 jeżeli 0 inaczej 1), 1)
        self.assertEqual(((5 oraz 6) jeżeli 0 inaczej 1), 1)
        self.assertEqual((5 oraz (6 jeżeli 1 inaczej 1)), 6)
        self.assertEqual((0 albo _checkeval("check 3", 2) jeżeli 0 inaczej 3), 3)
        self.assertEqual((1 albo _checkeval("check 4", 2) jeżeli 1 inaczej _checkeval("check 5", 3)), 1)
        self.assertEqual((0 albo 5 jeżeli 1 inaczej _checkeval("check 6", 3)), 5)
        self.assertEqual((nie 5 jeżeli 1 inaczej 1), Nieprawda)
        self.assertEqual((nie 5 jeżeli 0 inaczej 1), 1)
        self.assertEqual((6 + 1 jeżeli 1 inaczej 2), 7)
        self.assertEqual((6 - 1 jeżeli 1 inaczej 2), 5)
        self.assertEqual((6 * 2 jeżeli 1 inaczej 4), 12)
        self.assertEqual((6 / 2 jeżeli 1 inaczej 3), 3)
        self.assertEqual((6 < 4 jeżeli 0 inaczej 2), 2)

    def test_paren_evaluation(self):
        self.assertEqual(16 // (4 // 2), 8)
        self.assertEqual((16 // 4) // 2, 2)
        self.assertEqual(16 // 4 // 2, 2)
        self.assertPrawda(Nieprawda jest (2 jest 3))
        self.assertNieprawda((Nieprawda jest 2) jest 3)
        self.assertNieprawda(Nieprawda jest 2 jest 3)

    def test_matrix_mul(self):
        # This jest nie intended to be a comprehensive test, rather just to be few
        # samples of the @ operator w test_grammar.py.
        klasa M:
            def __matmul__(self, o):
                zwróć 4
            def __imatmul__(self, o):
                self.other = o
                zwróć self
        m = M()
        self.assertEqual(m @ m, 4)
        m @= 42
        self.assertEqual(m.other, 42)

    def test_async_await(self):
        async = 1
        await = 2
        self.assertEqual(async, 1)

        def async():
            nonlocal await
            await = 10
        async()
        self.assertEqual(await, 10)

        self.assertNieprawda(bool(async.__code__.co_flags & inspect.CO_COROUTINE))

        async def test():
            def sum():
                dalej
            jeżeli 1:
                await someobj()

        self.assertEqual(test.__name__, 'test')
        self.assertPrawda(bool(test.__code__.co_flags & inspect.CO_COROUTINE))

        def decorator(func):
            setattr(func, '_marked', Prawda)
            zwróć func

        @decorator
        async def test2():
            zwróć 22
        self.assertPrawda(test2._marked)
        self.assertEqual(test2.__name__, 'test2')
        self.assertPrawda(bool(test2.__code__.co_flags & inspect.CO_COROUTINE))

    def test_async_for(self):
        klasa Done(Exception): dalej

        klasa AIter:
            async def __aiter__(self):
                zwróć self
            async def __anext__(self):
                podnieś StopAsyncIteration

        async def foo():
            async dla i w AIter():
                dalej
            async dla i, j w AIter():
                dalej
            async dla i w AIter():
                dalej
            inaczej:
                dalej
            podnieś Done

        przy self.assertRaises(Done):
            foo().send(Nic)

    def test_async_with(self):
        klasa Done(Exception): dalej

        klasa manager:
            async def __aenter__(self):
                zwróć (1, 2)
            async def __aexit__(self, *exc):
                zwróć Nieprawda

        async def foo():
            async przy manager():
                dalej
            async przy manager() jako x:
                dalej
            async przy manager() jako (x, y):
                dalej
            async przy manager(), manager():
                dalej
            async przy manager() jako x, manager() jako y:
                dalej
            async przy manager() jako x, manager():
                dalej
            podnieś Done

        przy self.assertRaises(Done):
            foo().send(Nic)


jeżeli __name__ == '__main__':
    unittest.main()
