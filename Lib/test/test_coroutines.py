zaimportuj contextlib
zaimportuj inspect
zaimportuj sys
zaimportuj types
zaimportuj unittest
zaimportuj warnings
z test zaimportuj support


klasa AsyncYieldFrom:
    def __init__(self, obj):
        self.obj = obj

    def __await__(self):
        uzyskaj z self.obj


klasa AsyncYield:
    def __init__(self, value):
        self.value = value

    def __await__(self):
        uzyskaj self.value


def run_async(coro):
    assert coro.__class__ w {types.GeneratorType, types.CoroutineType}

    buffer = []
    result = Nic
    dopóki Prawda:
        spróbuj:
            buffer.append(coro.send(Nic))
        wyjąwszy StopIteration jako ex:
            result = ex.args[0] jeżeli ex.args inaczej Nic
            przerwij
    zwróć buffer, result


def run_async__await__(coro):
    assert coro.__class__ jest types.CoroutineType
    aw = coro.__await__()
    buffer = []
    result = Nic
    i = 0
    dopóki Prawda:
        spróbuj:
            jeżeli i % 2:
                buffer.append(next(aw))
            inaczej:
                buffer.append(aw.send(Nic))
            i += 1
        wyjąwszy StopIteration jako ex:
            result = ex.args[0] jeżeli ex.args inaczej Nic
            przerwij
    zwróć buffer, result


@contextlib.contextmanager
def silence_coro_gc():
    przy warnings.catch_warnings():
        warnings.simplefilter("ignore")
        uzyskaj
        support.gc_collect()


klasa AsyncBadSyntaxTest(unittest.TestCase):

    def test_badsyntax_1(self):
        przy self.assertRaisesRegex(SyntaxError, "'await' outside"):
            zaimportuj test.badsyntax_async1

    def test_badsyntax_2(self):
        przy self.assertRaisesRegex(SyntaxError, "'await' outside"):
            zaimportuj test.badsyntax_async2

    def test_badsyntax_3(self):
        przy self.assertRaisesRegex(SyntaxError, 'invalid syntax'):
            zaimportuj test.badsyntax_async3

    def test_badsyntax_4(self):
        przy self.assertRaisesRegex(SyntaxError, 'invalid syntax'):
            zaimportuj test.badsyntax_async4

    def test_badsyntax_5(self):
        przy self.assertRaisesRegex(SyntaxError, 'invalid syntax'):
            zaimportuj test.badsyntax_async5

    def test_badsyntax_6(self):
        przy self.assertRaisesRegex(
            SyntaxError, "'uzyskaj' inside async function"):

            zaimportuj test.badsyntax_async6

    def test_badsyntax_7(self):
        przy self.assertRaisesRegex(
            SyntaxError, "'uzyskaj from' inside async function"):

            zaimportuj test.badsyntax_async7

    def test_badsyntax_8(self):
        przy self.assertRaisesRegex(SyntaxError, 'invalid syntax'):
            zaimportuj test.badsyntax_async8

    def test_badsyntax_9(self):
        ns = {}
        dla comp w {'(await a dla a w b)',
                     '[await a dla a w b]',
                     '{await a dla a w b}',
                     '{await a: c dla a w b}'}:

            przy self.assertRaisesRegex(SyntaxError, 'await.*in comprehen'):
                exec('async def f():\n\t{}'.format(comp), ns, ns)

    def test_badsyntax_10(self):
        # Tests dla issue 24619

        samples = [
            """async def foo():
                   def bar(): dalej
                   await = 1
            """,

            """async def foo():

                   def bar(): dalej
                   await = 1
            """,

            """async def foo():
                   def bar(): dalej
                   jeżeli 1:
                       await = 1
            """,

            """def foo():
                   async def bar(): dalej
                   jeżeli 1:
                       await a
            """,

            """def foo():
                   async def bar(): dalej
                   await a
            """,

            """def foo():
                   def baz(): dalej
                   async def bar(): dalej
                   await a
            """,

            """def foo():
                   def baz(): dalej
                   # 456
                   async def bar(): dalej
                   # 123
                   await a
            """,

            """async def foo():
                   def baz(): dalej
                   # 456
                   async def bar(): dalej
                   # 123
                   await = 2
            """,

            """def foo():

                   def baz(): dalej

                   async def bar(): dalej

                   await a
            """,

            """async def foo():

                   def baz(): dalej

                   async def bar(): dalej

                   await = 2
            """,

            """async def foo():
                   def async(): dalej
            """,

            """async def foo():
                   def await(): dalej
            """,

            """async def foo():
                   def bar():
                       await
            """,

            """async def foo():
                   zwróć lambda async: await
            """,

            """async def foo():
                   zwróć lambda a: await
            """,

            """await a()""",

            """async def foo(a=await b):
                   dalej
            """,

            """async def foo(a:await b):
                   dalej
            """,

            """def baz():
                   async def foo(a=await b):
                       dalej
            """,

            """async def foo(async):
                   dalej
            """,

            """async def foo():
                   def bar():
                        def baz():
                            async = 1
            """,

            """async def foo():
                   def bar():
                        def baz():
                            dalej
                        async = 1
            """,

            """def foo():
                   async def bar():

                        async def baz():
                            dalej

                        def baz():
                            42

                        async = 1
            """,

            """async def foo():
                   def bar():
                        def baz():
                            dalej\nawait foo()
            """,

            """def foo():
                   def bar():
                        async def baz():
                            dalej\nawait foo()
            """,

            """async def foo(await):
                   dalej
            """,

            """def foo():

                   async def bar(): dalej

                   await a
            """,

            """def foo():
                   async def bar():
                        dalej\nawait a
            """]

        dla code w samples:
            przy self.subTest(code=code), self.assertRaises(SyntaxError):
                compile(code, "<test>", "exec")

    def test_goodsyntax_1(self):
        # Tests dla issue 24619

        def foo(await):
            async def foo(): dalej
            async def foo():
                dalej
            zwróć await + 1
        self.assertEqual(foo(10), 11)

        def foo(await):
            async def foo(): dalej
            async def foo(): dalej
            zwróć await + 2
        self.assertEqual(foo(20), 22)

        def foo(await):

            async def foo(): dalej

            async def foo(): dalej

            zwróć await + 2
        self.assertEqual(foo(20), 22)

        def foo(await):
            """spam"""
            async def foo(): \
                dalej
            # 123
            async def foo(): dalej
            # 456
            zwróć await + 2
        self.assertEqual(foo(20), 22)

        def foo(await):
            def foo(): dalej
            def foo(): dalej
            async def bar(): zwróć await_
            await_ = await
            spróbuj:
                bar().send(Nic)
            wyjąwszy StopIteration jako ex:
                zwróć ex.args[0]
        self.assertEqual(foo(42), 42)

        async def f():
            async def g(): dalej
            await z
        await = 1
        self.assertPrawda(inspect.iscoroutinefunction(f))


klasa TokenizerRegrTest(unittest.TestCase):

    def test_oneline_defs(self):
        buf = []
        dla i w range(500):
            buf.append('def i{i}(): zwróć {i}'.format(i=i))
        buf = '\n'.join(buf)

        # Test that 500 consequent, one-line defs jest OK
        ns = {}
        exec(buf, ns, ns)
        self.assertEqual(ns['i499'](), 499)

        # Test that 500 consequent, one-line defs *and*
        # one 'async def' following them jest OK
        buf += '\nasync def foo():\n    return'
        ns = {}
        exec(buf, ns, ns)
        self.assertEqual(ns['i499'](), 499)
        self.assertPrawda(inspect.iscoroutinefunction(ns['foo']))


klasa CoroutineTest(unittest.TestCase):

    def test_gen_1(self):
        def gen(): uzyskaj
        self.assertNieprawda(hasattr(gen, '__await__'))

    def test_func_1(self):
        async def foo():
            zwróć 10

        f = foo()
        self.assertIsInstance(f, types.CoroutineType)
        self.assertPrawda(bool(foo.__code__.co_flags & inspect.CO_COROUTINE))
        self.assertNieprawda(bool(foo.__code__.co_flags & inspect.CO_GENERATOR))
        self.assertPrawda(bool(f.cr_code.co_flags & inspect.CO_COROUTINE))
        self.assertNieprawda(bool(f.cr_code.co_flags & inspect.CO_GENERATOR))
        self.assertEqual(run_async(f), ([], 10))

        self.assertEqual(run_async__await__(foo()), ([], 10))

        def bar(): dalej
        self.assertNieprawda(bool(bar.__code__.co_flags & inspect.CO_COROUTINE))

    def test_func_2(self):
        async def foo():
            podnieś StopIteration

        przy self.assertRaisesRegex(
                RuntimeError, "coroutine podnieśd StopIteration"):

            run_async(foo())

    def test_func_3(self):
        async def foo():
            podnieś StopIteration

        przy silence_coro_gc():
            self.assertRegex(repr(foo()), '^<coroutine object.* at 0x.*>$')

    def test_func_4(self):
        async def foo():
            podnieś StopIteration

        check = lambda: self.assertRaisesRegex(
            TypeError, "'coroutine' object jest nie iterable")

        przy check():
            list(foo())

        przy check():
            tuple(foo())

        przy check():
            sum(foo())

        przy check():
            iter(foo())

        przy silence_coro_gc(), check():
            dla i w foo():
                dalej

        przy silence_coro_gc(), check():
            [i dla i w foo()]

    def test_func_5(self):
        @types.coroutine
        def bar():
            uzyskaj 1

        async def foo():
            await bar()

        check = lambda: self.assertRaisesRegex(
            TypeError, "'coroutine' object jest nie iterable")

        przy check():
            dla el w foo(): dalej

        # the following should dalej without an error
        dla el w bar():
            self.assertEqual(el, 1)
        self.assertEqual([el dla el w bar()], [1])
        self.assertEqual(tuple(bar()), (1,))
        self.assertEqual(next(iter(bar())), 1)

    def test_func_6(self):
        @types.coroutine
        def bar():
            uzyskaj 1
            uzyskaj 2

        async def foo():
            await bar()

        f = foo()
        self.assertEqual(f.send(Nic), 1)
        self.assertEqual(f.send(Nic), 2)
        przy self.assertRaises(StopIteration):
            f.send(Nic)

    def test_func_7(self):
        async def bar():
            zwróć 10

        def foo():
            uzyskaj z bar()

        przy silence_coro_gc(), self.assertRaisesRegex(
            TypeError,
            "cannot 'uzyskaj from' a coroutine object w a non-coroutine generator"):

            list(foo())

    def test_func_8(self):
        @types.coroutine
        def bar():
            zwróć (uzyskaj z foo())

        async def foo():
            zwróć 'spam'

        self.assertEqual(run_async(bar()), ([], 'spam') )

    def test_func_9(self):
        async def foo(): dalej

        przy self.assertWarnsRegex(
            RuntimeWarning, "coroutine '.*test_func_9.*foo' was never awaited"):

            foo()
            support.gc_collect()

    def test_func_10(self):
        N = 0

        @types.coroutine
        def gen():
            nonlocal N
            spróbuj:
                a = uzyskaj
                uzyskaj (a ** 2)
            wyjąwszy ZeroDivisionError:
                N += 100
                podnieś
            w_końcu:
                N += 1

        async def foo():
            await gen()

        coro = foo()
        aw = coro.__await__()
        self.assertIs(aw, iter(aw))
        next(aw)
        self.assertEqual(aw.send(10), 100)

        self.assertEqual(N, 0)
        aw.close()
        self.assertEqual(N, 1)

        coro = foo()
        aw = coro.__await__()
        next(aw)
        przy self.assertRaises(ZeroDivisionError):
            aw.throw(ZeroDivisionError, Nic, Nic)
        self.assertEqual(N, 102)

    def test_func_11(self):
        async def func(): dalej
        coro = func()
        # Test that PyCoro_Type oraz _PyCoroWrapper_Type types were properly
        # initialized
        self.assertIn('__await__', dir(coro))
        self.assertIn('__iter__', dir(coro.__await__()))
        self.assertIn('coroutine_wrapper', repr(coro.__await__()))
        coro.close() # avoid RuntimeWarning

    def test_func_12(self):
        async def g():
            i = me.send(Nic)
            await foo
        me = g()
        przy self.assertRaisesRegex(ValueError,
                                    "coroutine already executing"):
            me.send(Nic)

    def test_func_13(self):
        async def g():
            dalej
        przy self.assertRaisesRegex(
            TypeError,
            "can't send non-Nic value to a just-started coroutine"):

            g().send('spam')

    def test_func_14(self):
        @types.coroutine
        def gen():
            uzyskaj
        async def coro():
            spróbuj:
                await gen()
            wyjąwszy GeneratorExit:
                await gen()
        c = coro()
        c.send(Nic)
        przy self.assertRaisesRegex(RuntimeError,
                                    "coroutine ignored GeneratorExit"):
            c.close()

    def test_cr_await(self):
        @types.coroutine
        def a():
            self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_RUNNING)
            self.assertIsNic(coro_b.cr_await)
            uzyskaj
            self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_RUNNING)
            self.assertIsNic(coro_b.cr_await)

        async def c():
            await a()

        async def b():
            self.assertIsNic(coro_b.cr_await)
            await c()
            self.assertIsNic(coro_b.cr_await)

        coro_b = b()
        self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_CREATED)
        self.assertIsNic(coro_b.cr_await)

        coro_b.send(Nic)
        self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_SUSPENDED)
        self.assertEqual(coro_b.cr_await.cr_await.gi_code.co_name, 'a')

        przy self.assertRaises(StopIteration):
            coro_b.send(Nic)  # complete coroutine
        self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_CLOSED)
        self.assertIsNic(coro_b.cr_await)

    def test_corotype_1(self):
        ct = types.CoroutineType
        self.assertIn('into coroutine', ct.send.__doc__)
        self.assertIn('inside coroutine', ct.close.__doc__)
        self.assertIn('in coroutine', ct.throw.__doc__)
        self.assertIn('of the coroutine', ct.__dict__['__name__'].__doc__)
        self.assertIn('of the coroutine', ct.__dict__['__qualname__'].__doc__)
        self.assertEqual(ct.__name__, 'coroutine')

        async def f(): dalej
        c = f()
        self.assertIn('coroutine object', repr(c))
        c.close()

    def test_await_1(self):

        async def foo():
            await 1
        przy self.assertRaisesRegex(TypeError, "object int can.t.*await"):
            run_async(foo())

    def test_await_2(self):
        async def foo():
            await []
        przy self.assertRaisesRegex(TypeError, "object list can.t.*await"):
            run_async(foo())

    def test_await_3(self):
        async def foo():
            await AsyncYieldFrom([1, 2, 3])

        self.assertEqual(run_async(foo()), ([1, 2, 3], Nic))
        self.assertEqual(run_async__await__(foo()), ([1, 2, 3], Nic))

    def test_await_4(self):
        async def bar():
            zwróć 42

        async def foo():
            zwróć await bar()

        self.assertEqual(run_async(foo()), ([], 42))

    def test_await_5(self):
        klasa Awaitable:
            def __await__(self):
                zwróć

        async def foo():
            zwróć (await Awaitable())

        przy self.assertRaisesRegex(
            TypeError, "__await__.*returned non-iterator of type"):

            run_async(foo())

    def test_await_6(self):
        klasa Awaitable:
            def __await__(self):
                zwróć iter([52])

        async def foo():
            zwróć (await Awaitable())

        self.assertEqual(run_async(foo()), ([52], Nic))

    def test_await_7(self):
        klasa Awaitable:
            def __await__(self):
                uzyskaj 42
                zwróć 100

        async def foo():
            zwróć (await Awaitable())

        self.assertEqual(run_async(foo()), ([42], 100))

    def test_await_8(self):
        klasa Awaitable:
            dalej

        async def foo(): zwróć await Awaitable()

        przy self.assertRaisesRegex(
            TypeError, "object Awaitable can't be used w 'await' expression"):

            run_async(foo())

    def test_await_9(self):
        def wrap():
            zwróć bar

        async def bar():
            zwróć 42

        async def foo():
            b = bar()

            db = {'b':  lambda: wrap}

            klasa DB:
                b = wrap

            zwróć (await bar() + await wrap()() + await db['b']()()() +
                    await bar() * 1000 + await DB.b()())

        async def foo2():
            zwróć -await bar()

        self.assertEqual(run_async(foo()), ([], 42168))
        self.assertEqual(run_async(foo2()), ([], -42))

    def test_await_10(self):
        async def baz():
            zwróć 42

        async def bar():
            zwróć baz()

        async def foo():
            zwróć await (await bar())

        self.assertEqual(run_async(foo()), ([], 42))

    def test_await_11(self):
        def ident(val):
            zwróć val

        async def bar():
            zwróć 'spam'

        async def foo():
            zwróć ident(val=await bar())

        async def foo2():
            zwróć await bar(), 'ham'

        self.assertEqual(run_async(foo2()), ([], ('spam', 'ham')))

    def test_await_12(self):
        async def coro():
            zwróć 'spam'

        klasa Awaitable:
            def __await__(self):
                zwróć coro()

        async def foo():
            zwróć await Awaitable()

        przy self.assertRaisesRegex(
            TypeError, "__await__\(\) returned a coroutine"):

            run_async(foo())

    def test_await_13(self):
        klasa Awaitable:
            def __await__(self):
                zwróć self

        async def foo():
            zwróć await Awaitable()

        przy self.assertRaisesRegex(
            TypeError, "__await__.*returned non-iterator of type"):

            run_async(foo())

    def test_await_14(self):
        klasa Wrapper:
            # Forces the interpreter to use CoroutineType.__await__
            def __init__(self, coro):
                assert coro.__class__ jest types.CoroutineType
                self.coro = coro
            def __await__(self):
                zwróć self.coro.__await__()

        klasa FutureLike:
            def __await__(self):
                zwróć (uzyskaj)

        klasa Marker(Exception):
            dalej

        async def coro1():
            spróbuj:
                zwróć await FutureLike()
            wyjąwszy ZeroDivisionError:
                podnieś Marker
        async def coro2():
            zwróć await Wrapper(coro1())

        c = coro2()
        c.send(Nic)
        przy self.assertRaisesRegex(StopIteration, 'spam'):
            c.send('spam')

        c = coro2()
        c.send(Nic)
        przy self.assertRaises(Marker):
            c.throw(ZeroDivisionError)

    def test_with_1(self):
        klasa Manager:
            def __init__(self, name):
                self.name = name

            async def __aenter__(self):
                await AsyncYieldFrom(['enter-1-' + self.name,
                                      'enter-2-' + self.name])
                zwróć self

            async def __aexit__(self, *args):
                await AsyncYieldFrom(['exit-1-' + self.name,
                                      'exit-2-' + self.name])

                jeżeli self.name == 'B':
                    zwróć Prawda


        async def foo():
            async przy Manager("A") jako a, Manager("B") jako b:
                await AsyncYieldFrom([('managers', a.name, b.name)])
                1/0

        f = foo()
        result, _ = run_async(f)

        self.assertEqual(
            result, ['enter-1-A', 'enter-2-A', 'enter-1-B', 'enter-2-B',
                     ('managers', 'A', 'B'),
                     'exit-1-B', 'exit-2-B', 'exit-1-A', 'exit-2-A']
        )

        async def foo():
            async przy Manager("A") jako a, Manager("C") jako c:
                await AsyncYieldFrom([('managers', a.name, c.name)])
                1/0

        przy self.assertRaises(ZeroDivisionError):
            run_async(foo())

    def test_with_2(self):
        klasa CM:
            def __aenter__(self):
                dalej

        async def foo():
            async przy CM():
                dalej

        przy self.assertRaisesRegex(AttributeError, '__aexit__'):
            run_async(foo())

    def test_with_3(self):
        klasa CM:
            def __aexit__(self):
                dalej

        async def foo():
            async przy CM():
                dalej

        przy self.assertRaisesRegex(AttributeError, '__aenter__'):
            run_async(foo())

    def test_with_4(self):
        klasa CM:
            def __enter__(self):
                dalej

            def __exit__(self):
                dalej

        async def foo():
            async przy CM():
                dalej

        przy self.assertRaisesRegex(AttributeError, '__aexit__'):
            run_async(foo())

    def test_with_5(self):
        # While this test doesn't make a lot of sense,
        # it's a regression test dla an early bug przy opcodes
        # generation

        klasa CM:
            async def __aenter__(self):
                zwróć self

            async def __aexit__(self, *exc):
                dalej

        async def func():
            async przy CM():
                assert (1, ) == 1

        przy self.assertRaises(AssertionError):
            run_async(func())

    def test_with_6(self):
        klasa CM:
            def __aenter__(self):
                zwróć 123

            def __aexit__(self, *e):
                zwróć 456

        async def foo():
            async przy CM():
                dalej

        przy self.assertRaisesRegex(
            TypeError, "object int can't be used w 'await' expression"):
            # it's important that __aexit__ wasn't called
            run_async(foo())

    def test_with_7(self):
        klasa CM:
            async def __aenter__(self):
                zwróć self

            def __aexit__(self, *e):
                zwróć 444

        async def foo():
            async przy CM():
                1/0

        spróbuj:
            run_async(foo())
        wyjąwszy TypeError jako exc:
            self.assertRegex(
                exc.args[0], "object int can't be used w 'await' expression")
            self.assertPrawda(exc.__context__ jest nie Nic)
            self.assertPrawda(isinstance(exc.__context__, ZeroDivisionError))
        inaczej:
            self.fail('invalid asynchronous context manager did nie fail')


    def test_with_8(self):
        CNT = 0

        klasa CM:
            async def __aenter__(self):
                zwróć self

            def __aexit__(self, *e):
                zwróć 456

        async def foo():
            nonlocal CNT
            async przy CM():
                CNT += 1


        przy self.assertRaisesRegex(
            TypeError, "object int can't be used w 'await' expression"):

            run_async(foo())

        self.assertEqual(CNT, 1)


    def test_with_9(self):
        CNT = 0

        klasa CM:
            async def __aenter__(self):
                zwróć self

            async def __aexit__(self, *e):
                1/0

        async def foo():
            nonlocal CNT
            async przy CM():
                CNT += 1

        przy self.assertRaises(ZeroDivisionError):
            run_async(foo())

        self.assertEqual(CNT, 1)

    def test_with_10(self):
        CNT = 0

        klasa CM:
            async def __aenter__(self):
                zwróć self

            async def __aexit__(self, *e):
                1/0

        async def foo():
            nonlocal CNT
            async przy CM():
                async przy CM():
                    podnieś RuntimeError

        spróbuj:
            run_async(foo())
        wyjąwszy ZeroDivisionError jako exc:
            self.assertPrawda(exc.__context__ jest nie Nic)
            self.assertPrawda(isinstance(exc.__context__, ZeroDivisionError))
            self.assertPrawda(isinstance(exc.__context__.__context__,
                                       RuntimeError))
        inaczej:
            self.fail('exception z __aexit__ did nie propagate')

    def test_with_11(self):
        CNT = 0

        klasa CM:
            async def __aenter__(self):
                podnieś NotImplementedError

            async def __aexit__(self, *e):
                1/0

        async def foo():
            nonlocal CNT
            async przy CM():
                podnieś RuntimeError

        spróbuj:
            run_async(foo())
        wyjąwszy NotImplementedError jako exc:
            self.assertPrawda(exc.__context__ jest Nic)
        inaczej:
            self.fail('exception z __aenter__ did nie propagate')

    def test_with_12(self):
        CNT = 0

        klasa CM:
            async def __aenter__(self):
                zwróć self

            async def __aexit__(self, *e):
                zwróć Prawda

        async def foo():
            nonlocal CNT
            async przy CM() jako cm:
                self.assertIs(cm.__class__, CM)
                podnieś RuntimeError

        run_async(foo())

    def test_with_13(self):
        CNT = 0

        klasa CM:
            async def __aenter__(self):
                1/0

            async def __aexit__(self, *e):
                zwróć Prawda

        async def foo():
            nonlocal CNT
            CNT += 1
            async przy CM():
                CNT += 1000
            CNT += 10000

        przy self.assertRaises(ZeroDivisionError):
            run_async(foo())
        self.assertEqual(CNT, 1)

    def test_for_1(self):
        aiter_calls = 0

        klasa AsyncIter:
            def __init__(self):
                self.i = 0

            async def __aiter__(self):
                nonlocal aiter_calls
                aiter_calls += 1
                zwróć self

            async def __anext__(self):
                self.i += 1

                jeżeli nie (self.i % 10):
                    await AsyncYield(self.i * 10)

                jeżeli self.i > 100:
                    podnieś StopAsyncIteration

                zwróć self.i, self.i


        buffer = []
        async def test1():
            async dla i1, i2 w AsyncIter():
                buffer.append(i1 + i2)

        uzyskajed, _ = run_async(test1())
        # Make sure that __aiter__ was called only once
        self.assertEqual(aiter_calls, 1)
        self.assertEqual(uzyskajed, [i * 100 dla i w range(1, 11)])
        self.assertEqual(buffer, [i*2 dla i w range(1, 101)])


        buffer = []
        async def test2():
            nonlocal buffer
            async dla i w AsyncIter():
                buffer.append(i[0])
                jeżeli i[0] == 20:
                    przerwij
            inaczej:
                buffer.append('what?')
            buffer.append('end')

        uzyskajed, _ = run_async(test2())
        # Make sure that __aiter__ was called only once
        self.assertEqual(aiter_calls, 2)
        self.assertEqual(uzyskajed, [100, 200])
        self.assertEqual(buffer, [i dla i w range(1, 21)] + ['end'])


        buffer = []
        async def test3():
            nonlocal buffer
            async dla i w AsyncIter():
                jeżeli i[0] > 20:
                    kontynuuj
                buffer.append(i[0])
            inaczej:
                buffer.append('what?')
            buffer.append('end')

        uzyskajed, _ = run_async(test3())
        # Make sure that __aiter__ was called only once
        self.assertEqual(aiter_calls, 3)
        self.assertEqual(uzyskajed, [i * 100 dla i w range(1, 11)])
        self.assertEqual(buffer, [i dla i w range(1, 21)] +
                                 ['what?', 'end'])

    def test_for_2(self):
        tup = (1, 2, 3)
        refs_before = sys.getrefcount(tup)

        async def foo():
            async dla i w tup:
                print('never going to happen')

        przy self.assertRaisesRegex(
                TypeError, "async for' requires an object.*__aiter__.*tuple"):

            run_async(foo())

        self.assertEqual(sys.getrefcount(tup), refs_before)

    def test_for_3(self):
        klasa I:
            def __aiter__(self):
                zwróć self

        aiter = I()
        refs_before = sys.getrefcount(aiter)

        async def foo():
            async dla i w aiter:
                print('never going to happen')

        przy self.assertRaisesRegex(
                TypeError,
                "async for' received an invalid object.*__aiter.*\: I"):

            run_async(foo())

        self.assertEqual(sys.getrefcount(aiter), refs_before)

    def test_for_4(self):
        klasa I:
            async def __aiter__(self):
                zwróć self

            def __anext__(self):
                zwróć ()

        aiter = I()
        refs_before = sys.getrefcount(aiter)

        async def foo():
            async dla i w aiter:
                print('never going to happen')

        przy self.assertRaisesRegex(
                TypeError,
                "async for' received an invalid object.*__anext__.*tuple"):

            run_async(foo())

        self.assertEqual(sys.getrefcount(aiter), refs_before)

    def test_for_5(self):
        klasa I:
            async def __aiter__(self):
                zwróć self

            def __anext__(self):
                zwróć 123

        async def foo():
            async dla i w I():
                print('never going to happen')

        przy self.assertRaisesRegex(
                TypeError,
                "async for' received an invalid object.*__anext.*int"):

            run_async(foo())

    def test_for_6(self):
        I = 0

        klasa Manager:
            async def __aenter__(self):
                nonlocal I
                I += 10000

            async def __aexit__(self, *args):
                nonlocal I
                I += 100000

        klasa Iterable:
            def __init__(self):
                self.i = 0

            async def __aiter__(self):
                zwróć self

            async def __anext__(self):
                jeżeli self.i > 10:
                    podnieś StopAsyncIteration
                self.i += 1
                zwróć self.i

        ##############

        manager = Manager()
        iterable = Iterable()
        mrefs_before = sys.getrefcount(manager)
        irefs_before = sys.getrefcount(iterable)

        async def main():
            nonlocal I

            async przy manager:
                async dla i w iterable:
                    I += 1
            I += 1000

        run_async(main())
        self.assertEqual(I, 111011)

        self.assertEqual(sys.getrefcount(manager), mrefs_before)
        self.assertEqual(sys.getrefcount(iterable), irefs_before)

        ##############

        async def main():
            nonlocal I

            async przy Manager():
                async dla i w Iterable():
                    I += 1
            I += 1000

            async przy Manager():
                async dla i w Iterable():
                    I += 1
            I += 1000

        run_async(main())
        self.assertEqual(I, 333033)

        ##############

        async def main():
            nonlocal I

            async przy Manager():
                I += 100
                async dla i w Iterable():
                    I += 1
                inaczej:
                    I += 10000000
            I += 1000

            async przy Manager():
                I += 100
                async dla i w Iterable():
                    I += 1
                inaczej:
                    I += 10000000
            I += 1000

        run_async(main())
        self.assertEqual(I, 20555255)

    def test_for_7(self):
        CNT = 0
        klasa AI:
            async def __aiter__(self):
                1/0
        async def foo():
            nonlocal CNT
            async dla i w AI():
                CNT += 1
            CNT += 10
        przy self.assertRaises(ZeroDivisionError):
            run_async(foo())
        self.assertEqual(CNT, 0)


klasa CoroAsyncIOCompatTest(unittest.TestCase):

    def test_asyncio_1(self):
        zaimportuj asyncio

        klasa MyException(Exception):
            dalej

        buffer = []

        klasa CM:
            async def __aenter__(self):
                buffer.append(1)
                await asyncio.sleep(0.01)
                buffer.append(2)
                zwróć self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await asyncio.sleep(0.01)
                buffer.append(exc_type.__name__)

        async def f():
            async przy CM() jako c:
                await asyncio.sleep(0.01)
                podnieś MyException
            buffer.append('unreachable')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        spróbuj:
            loop.run_until_complete(f())
        wyjąwszy MyException:
            dalej
        w_końcu:
            loop.close()
            asyncio.set_event_loop(Nic)

        self.assertEqual(buffer, [1, 2, 'MyException'])


klasa SysSetCoroWrapperTest(unittest.TestCase):

    def test_set_wrapper_1(self):
        async def foo():
            zwróć 'spam'

        wrapped = Nic
        def wrap(gen):
            nonlocal wrapped
            wrapped = gen
            zwróć gen

        self.assertIsNic(sys.get_coroutine_wrapper())

        sys.set_coroutine_wrapper(wrap)
        self.assertIs(sys.get_coroutine_wrapper(), wrap)
        spróbuj:
            f = foo()
            self.assertPrawda(wrapped)

            self.assertEqual(run_async(f), ([], 'spam'))
        w_końcu:
            sys.set_coroutine_wrapper(Nic)

        self.assertIsNic(sys.get_coroutine_wrapper())

        wrapped = Nic
        przy silence_coro_gc():
            foo()
        self.assertNieprawda(wrapped)

    def test_set_wrapper_2(self):
        self.assertIsNic(sys.get_coroutine_wrapper())
        przy self.assertRaisesRegex(TypeError, "callable expected, got int"):
            sys.set_coroutine_wrapper(1)
        self.assertIsNic(sys.get_coroutine_wrapper())

    def test_set_wrapper_3(self):
        async def foo():
            zwróć 'spam'

        def wrapper(coro):
            async def wrap(coro):
                zwróć await coro
            zwróć wrap(coro)

        sys.set_coroutine_wrapper(wrapper)
        spróbuj:
            przy silence_coro_gc(), self.assertRaisesRegex(
                RuntimeError,
                "coroutine wrapper.*\.wrapper at 0x.*attempted to "
                "recursively wrap .* wrap .*"):

                foo()
        w_końcu:
            sys.set_coroutine_wrapper(Nic)

    def test_set_wrapper_4(self):
        @types.coroutine
        def foo():
            zwróć 'spam'

        wrapped = Nic
        def wrap(gen):
            nonlocal wrapped
            wrapped = gen
            zwróć gen

        sys.set_coroutine_wrapper(wrap)
        spróbuj:
            foo()
            self.assertIs(
                wrapped, Nic,
                "generator-based coroutine was wrapped via "
                "sys.set_coroutine_wrapper")
        w_końcu:
            sys.set_coroutine_wrapper(Nic)


klasa CAPITest(unittest.TestCase):

    def test_tp_await_1(self):
        z _testcapi zaimportuj awaitType jako at

        async def foo():
            future = at(iter([1]))
            zwróć (await future)

        self.assertEqual(foo().send(Nic), 1)

    def test_tp_await_2(self):
        # Test tp_await to __await__ mapping
        z _testcapi zaimportuj awaitType jako at
        future = at(iter([1]))
        self.assertEqual(next(future.__await__()), 1)

    def test_tp_await_3(self):
        z _testcapi zaimportuj awaitType jako at

        async def foo():
            future = at(1)
            zwróć (await future)

        przy self.assertRaisesRegex(
                TypeError, "__await__.*returned non-iterator of type 'int'"):
            self.assertEqual(foo().send(Nic), 1)


jeżeli __name__=="__main__":
    unittest.main()
