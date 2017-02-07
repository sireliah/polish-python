zaimportuj unittest
zaimportuj weakref

z test.support zaimportuj check_syntax_error, cpython_only


klasa ScopeTests(unittest.TestCase):

    def testSimpleNesting(self):

        def make_adder(x):
            def adder(y):
                zwróć x + y
            zwróć adder

        inc = make_adder(1)
        plus10 = make_adder(10)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    def testExtraNesting(self):

        def make_adder2(x):
            def extra(): # check freevars dalejing through non-use scopes
                def adder(y):
                    zwróć x + y
                zwróć adder
            zwróć extra()

        inc = make_adder2(1)
        plus10 = make_adder2(10)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    def testSimpleAndRebinding(self):

        def make_adder3(x):
            def adder(y):
                zwróć x + y
            x = x + 1 # check tracking of assignment to x w defining scope
            zwróć adder

        inc = make_adder3(0)
        plus10 = make_adder3(9)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    def testNestingGlobalNoFree(self):

        def make_adder4(): # XXX add exta level of indirection
            def nest():
                def nest():
                    def adder(y):
                        zwróć global_x + y # check that plain old globals work
                    zwróć adder
                zwróć nest()
            zwróć nest()

        global_x = 1
        adder = make_adder4()
        self.assertEqual(adder(1), 2)

        global_x = 10
        self.assertEqual(adder(-2), 8)

    def testNestingThroughClass(self):

        def make_adder5(x):
            klasa Adder:
                def __call__(self, y):
                    zwróć x + y
            zwróć Adder()

        inc = make_adder5(1)
        plus10 = make_adder5(10)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    def testNestingPlusFreeRefToGlobal(self):

        def make_adder6(x):
            global global_nest_x
            def adder(y):
                zwróć global_nest_x + y
            global_nest_x = x
            zwróć adder

        inc = make_adder6(1)
        plus10 = make_adder6(10)

        self.assertEqual(inc(1), 11) # there's only one global
        self.assertEqual(plus10(-2), 8)

    def testNearestEnclosingScope(self):

        def f(x):
            def g(y):
                x = 42 # check that this masks binding w f()
                def h(z):
                    zwróć x + z
                zwróć h
            zwróć g(2)

        test_func = f(10)
        self.assertEqual(test_func(5), 47)

    def testMixedFreevarsAndCellvars(self):

        def identity(x):
            zwróć x

        def f(x, y, z):
            def g(a, b, c):
                a = a + x # 3
                def h():
                    # z * (4 + 9)
                    # 3 * 13
                    zwróć identity(z * (b + y))
                y = c + z # 9
                zwróć h
            zwróć g

        g = f(1, 2, 3)
        h = g(2, 4, 6)
        self.assertEqual(h(), 39)

    def testFreeVarInMethod(self):

        def test():
            method_and_var = "var"
            klasa Test:
                def method_and_var(self):
                    zwróć "method"
                def test(self):
                    zwróć method_and_var
                def actual_global(self):
                    zwróć str("global")
                def str(self):
                    zwróć str(self)
            zwróć Test()

        t = test()
        self.assertEqual(t.test(), "var")
        self.assertEqual(t.method_and_var(), "method")
        self.assertEqual(t.actual_global(), "global")

        method_and_var = "var"
        klasa Test:
            # this klasa jest nie nested, so the rules are different
            def method_and_var(self):
                zwróć "method"
            def test(self):
                zwróć method_and_var
            def actual_global(self):
                zwróć str("global")
            def str(self):
                zwróć str(self)

        t = Test()
        self.assertEqual(t.test(), "var")
        self.assertEqual(t.method_and_var(), "method")
        self.assertEqual(t.actual_global(), "global")

    def testCellIsKwonlyArg(self):
        # Issue 1409: Initialisation of a cell value,
        # when it comes z a keyword-only parameter
        def foo(*, a=17):
            def bar():
                zwróć a + 5
            zwróć bar() + 3

        self.assertEqual(foo(a=42), 50)
        self.assertEqual(foo(), 25)

    def testRecursion(self):

        def f(x):
            def fact(n):
                jeżeli n == 0:
                    zwróć 1
                inaczej:
                    zwróć n * fact(n - 1)
            jeżeli x >= 0:
                zwróć fact(x)
            inaczej:
                podnieś ValueError("x must be >= 0")

        self.assertEqual(f(6), 720)


    def testUnoptimizedNamespaces(self):

        check_syntax_error(self, """jeżeli 1:
            def unoptimized_clash1(strip):
                def f(s):
                    z sys zaimportuj *
                    zwróć getrefcount(s) # ambiguity: free albo local
                zwróć f
            """)

        check_syntax_error(self, """jeżeli 1:
            def unoptimized_clash2():
                z sys zaimportuj *
                def f(s):
                    zwróć getrefcount(s) # ambiguity: global albo local
                zwróć f
            """)

        check_syntax_error(self, """jeżeli 1:
            def unoptimized_clash2():
                z sys zaimportuj *
                def g():
                    def f(s):
                        zwróć getrefcount(s) # ambiguity: global albo local
                    zwróć f
            """)

        check_syntax_error(self, """jeżeli 1:
            def f():
                def g():
                    z sys zaimportuj *
                    zwróć getrefcount # global albo local?
            """)

    def testLambdas(self):

        f1 = lambda x: lambda y: x + y
        inc = f1(1)
        plus10 = f1(10)
        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(5), 15)

        f2 = lambda x: (lambda : lambda y: x + y)()
        inc = f2(1)
        plus10 = f2(10)
        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(5), 15)

        f3 = lambda x: lambda y: global_x + y
        global_x = 1
        inc = f3(Nic)
        self.assertEqual(inc(2), 3)

        f8 = lambda x, y, z: lambda a, b, c: lambda : z * (b + y)
        g = f8(1, 2, 3)
        h = g(2, 4, 6)
        self.assertEqual(h(), 18)

    def testUnboundLocal(self):

        def errorInOuter():
            print(y)
            def inner():
                zwróć y
            y = 1

        def errorInInner():
            def inner():
                zwróć y
            inner()
            y = 1

        self.assertRaises(UnboundLocalError, errorInOuter)
        self.assertRaises(NameError, errorInInner)

    def testUnboundLocal_AfterDel(self):
        # #4617: It jest now legal to delete a cell variable.
        # The following functions must obviously compile,
        # oraz give the correct error when accessing the deleted name.
        def errorInOuter():
            y = 1
            usuń y
            print(y)
            def inner():
                zwróć y

        def errorInInner():
            def inner():
                zwróć y
            y = 1
            usuń y
            inner()

        self.assertRaises(UnboundLocalError, errorInOuter)
        self.assertRaises(NameError, errorInInner)

    def testUnboundLocal_AugAssign(self):
        # test dla bug #1501934: incorrect LOAD/STORE_GLOBAL generation
        exec("""jeżeli 1:
            global_x = 1
            def f():
                global_x += 1
            spróbuj:
                f()
            wyjąwszy UnboundLocalError:
                dalej
            inaczej:
                fail('scope of global_x nie correctly determined')
            """, {'fail': self.fail})

    def testComplexDefinitions(self):

        def makeReturner(*lst):
            def returner():
                zwróć lst
            zwróć returner

        self.assertEqual(makeReturner(1,2,3)(), (1,2,3))

        def makeReturner2(**kwargs):
            def returner():
                zwróć kwargs
            zwróć returner

        self.assertEqual(makeReturner2(a=11)()['a'], 11)

    def testScopeOfGlobalStmt(self):
        # Examples posted by Samuele Pedroni to python-dev on 3/1/2001

        exec("""jeżeli 1:
            # I
            x = 7
            def f():
                x = 1
                def g():
                    global x
                    def i():
                        def h():
                            zwróć x
                        zwróć h()
                    zwróć i()
                zwróć g()
            self.assertEqual(f(), 7)
            self.assertEqual(x, 7)

            # II
            x = 7
            def f():
                x = 1
                def g():
                    x = 2
                    def i():
                        def h():
                            zwróć x
                        zwróć h()
                    zwróć i()
                zwróć g()
            self.assertEqual(f(), 2)
            self.assertEqual(x, 7)

            # III
            x = 7
            def f():
                x = 1
                def g():
                    global x
                    x = 2
                    def i():
                        def h():
                            zwróć x
                        zwróć h()
                    zwróć i()
                zwróć g()
            self.assertEqual(f(), 2)
            self.assertEqual(x, 2)

            # IV
            x = 7
            def f():
                x = 3
                def g():
                    global x
                    x = 2
                    def i():
                        def h():
                            zwróć x
                        zwróć h()
                    zwróć i()
                zwróć g()
            self.assertEqual(f(), 2)
            self.assertEqual(x, 2)

            # XXX what about global statements w klasa blocks?
            # do they affect methods?

            x = 12
            klasa Global:
                global x
                x = 13
                def set(self, val):
                    x = val
                def get(self):
                    zwróć x

            g = Global()
            self.assertEqual(g.get(), 13)
            g.set(15)
            self.assertEqual(g.get(), 13)
            """)

    def testLeaks(self):

        klasa Foo:
            count = 0

            def __init__(self):
                Foo.count += 1

            def __del__(self):
                Foo.count -= 1

        def f1():
            x = Foo()
            def f2():
                zwróć x
            f2()

        dla i w range(100):
            f1()

        self.assertEqual(Foo.count, 0)

    def testClassAndGlobal(self):

        exec("""jeżeli 1:
            def test(x):
                klasa Foo:
                    global x
                    def __call__(self, y):
                        zwróć x + y
                zwróć Foo()

            x = 0
            self.assertEqual(test(6)(2), 8)
            x = -1
            self.assertEqual(test(3)(2), 5)

            looked_up_by_load_name = Nieprawda
            klasa X:
                # Implicit globals inside classes are be looked up by LOAD_NAME, nie
                # LOAD_GLOBAL.
                locals()['looked_up_by_load_name'] = Prawda
                dalejed = looked_up_by_load_name

            self.assertPrawda(X.passed)
            """)

    def testLocalsFunction(self):

        def f(x):
            def g(y):
                def h(z):
                    zwróć y + z
                w = x + y
                y += 3
                zwróć locals()
            zwróć g

        d = f(2)(4)
        self.assertIn('h', d)
        usuń d['h']
        self.assertEqual(d, {'x': 2, 'y': 7, 'w': 6})

    def testLocalsClass(self):
        # This test verifies that calling locals() does nie pollute
        # the local namespace of the klasa przy free variables.  Old
        # versions of Python had a bug, where a free variable being
        # dalejed through a klasa namespace would be inserted into
        # locals() by locals() albo exec albo a trace function.
        #
        # The real bug lies w frame code that copies variables
        # between fast locals oraz the locals dict, e.g. when executing
        # a trace function.

        def f(x):
            klasa C:
                x = 12
                def m(self):
                    zwróć x
                locals()
            zwróć C

        self.assertEqual(f(1).x, 12)

        def f(x):
            klasa C:
                y = x
                def m(self):
                    zwróć x
                z = list(locals())
            zwróć C

        varnames = f(1).z
        self.assertNotIn("x", varnames)
        self.assertIn("y", varnames)

    @cpython_only
    def testLocalsClass_WithTrace(self):
        # Issue23728: after the trace function returns, the locals()
        # dictionary jest used to update all variables, this used to
        # include free variables. But w klasa statements, free
        # variables are nie inserted...
        zaimportuj sys
        self.addCleanup(sys.settrace, sys.gettrace())
        sys.settrace(lambda a,b,c:Nic)
        x = 12

        klasa C:
            def f(self):
                zwróć x

        self.assertEqual(x, 12) # Used to podnieś UnboundLocalError

    def testBoundAndFree(self):
        # var jest bound oraz free w class

        def f(x):
            klasa C:
                def m(self):
                    zwróć x
                a = x
            zwróć C

        inst = f(3)()
        self.assertEqual(inst.a, inst.m())

    @cpython_only
    def testInteractionWithTraceFunc(self):

        zaimportuj sys
        def tracer(a,b,c):
            zwróć tracer

        def adaptgetter(name, klass, getter):
            kind, des = getter
            jeżeli kind == 1:       # AV happens when stepping z this line to next
                jeżeli des == "":
                    des = "_%s__%s" % (klass.__name__, name)
                zwróć lambda obj: getattr(obj, des)

        klasa TestClass:
            dalej

        self.addCleanup(sys.settrace, sys.gettrace())
        sys.settrace(tracer)
        adaptgetter("foo", TestClass, (1, ""))
        sys.settrace(Nic)

        self.assertRaises(TypeError, sys.settrace)

    def testEvalExecFreeVars(self):

        def f(x):
            zwróć lambda: x + 1

        g = f(3)
        self.assertRaises(TypeError, eval, g.__code__)

        spróbuj:
            exec(g.__code__, {})
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("exec should have failed, because code contained free vars")

    def testListCompLocalVars(self):

        spróbuj:
            print(bad)
        wyjąwszy NameError:
            dalej
        inaczej:
            print("bad should nie be defined")

        def x():
            [bad dla s w 'a b' dla bad w s.split()]

        x()
        spróbuj:
            print(bad)
        wyjąwszy NameError:
            dalej

    def testEvalFreeVars(self):

        def f(x):
            def g():
                x
                eval("x + 1")
            zwróć g

        f(4)()

    def testFreeingCell(self):
        # Test what happens when a finalizer accesses
        # the cell where the object was stored.
        klasa Special:
            def __del__(self):
                nestedcell_get()

    def testNonLocalFunction(self):

        def f(x):
            def inc():
                nonlocal x
                x += 1
                zwróć x
            def dec():
                nonlocal x
                x -= 1
                zwróć x
            zwróć inc, dec

        inc, dec = f(0)
        self.assertEqual(inc(), 1)
        self.assertEqual(inc(), 2)
        self.assertEqual(dec(), 1)
        self.assertEqual(dec(), 0)

    def testNonLocalMethod(self):
        def f(x):
            klasa c:
                def inc(self):
                    nonlocal x
                    x += 1
                    zwróć x
                def dec(self):
                    nonlocal x
                    x -= 1
                    zwróć x
            zwróć c()
        c = f(0)
        self.assertEqual(c.inc(), 1)
        self.assertEqual(c.inc(), 2)
        self.assertEqual(c.dec(), 1)
        self.assertEqual(c.dec(), 0)

    def testGlobalInParallelNestedFunctions(self):
        # A symbol table bug leaked the global statement z one
        # function to other nested functions w the same block.
        # This test verifies that a global statement w the first
        # function does nie affect the second function.
        local_ns = {}
        global_ns = {}
        exec("""jeżeli 1:
            def f():
                y = 1
                def g():
                    global y
                    zwróć y
                def h():
                    zwróć y + 1
                zwróć g, h
            y = 9
            g, h = f()
            result9 = g()
            result2 = h()
            """, local_ns, global_ns)
        self.assertEqual(2, global_ns["result2"])
        self.assertEqual(9, global_ns["result9"])

    def testNonLocalClass(self):

        def f(x):
            klasa c:
                nonlocal x
                x += 1
                def get(self):
                    zwróć x
            zwróć c()

        c = f(0)
        self.assertEqual(c.get(), 1)
        self.assertNotIn("x", c.__class__.__dict__)


    def testNonLocalGenerator(self):

        def f(x):
            def g(y):
                nonlocal x
                dla i w range(y):
                    x += 1
                    uzyskaj x
            zwróć g

        g = f(0)
        self.assertEqual(list(g(5)), [1, 2, 3, 4, 5])

    def testNestedNonLocal(self):

        def f(x):
            def g():
                nonlocal x
                x -= 2
                def h():
                    nonlocal x
                    x += 4
                    zwróć x
                zwróć h
            zwróć g

        g = f(1)
        h = g()
        self.assertEqual(h(), 3)

    def testTopIsNotSignificant(self):
        # See #9997.
        def top(a):
            dalej
        def b():
            global a

    def testClassNamespaceOverridesClosure(self):
        # See #17853.
        x = 42
        klasa X:
            locals()["x"] = 43
            y = x
        self.assertEqual(X.y, 43)
        klasa X:
            locals()["x"] = 43
            usuń x
        self.assertNieprawda(hasattr(X, "x"))
        self.assertEqual(x, 42)

    @cpython_only
    def testCellLeak(self):
        # Issue 17927.
        #
        # The issue was that jeżeli self was part of a cycle involving the
        # frame of a method call, *and* the method contained a nested
        # function referencing self, thereby forcing 'self' into a
        # cell, setting self to Nic would nie be enough to przerwij the
        # frame -- the frame had another reference to the instance,
        # which could nie be cleared by the code running w the frame
        # (though it will be cleared when the frame jest collected).
        # Without the lambda, setting self to Nic jest enough to przerwij
        # the cycle.
        klasa Tester:
            def dig(self):
                jeżeli 0:
                    lambda: self
                spróbuj:
                    1/0
                wyjąwszy Exception jako exc:
                    self.exc = exc
                self = Nic  # Break the cycle
        tester = Tester()
        tester.dig()
        ref = weakref.ref(tester)
        usuń tester
        self.assertIsNic(ref())


jeżeli __name__ == '__main__':
    unittest.main()
