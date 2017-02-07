"""Unit tests dla contextlib.py, oraz other context managers."""

zaimportuj io
zaimportuj sys
zaimportuj tempfile
zaimportuj unittest
z contextlib zaimportuj *  # Tests __all__
z test zaimportuj support
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic


klasa ContextManagerTestCase(unittest.TestCase):

    def test_contextmanager_plain(self):
        state = []
        @contextmanager
        def woohoo():
            state.append(1)
            uzyskaj 42
            state.append(999)
        przy woohoo() jako x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
        self.assertEqual(state, [1, 42, 999])

    def test_contextmanager_finally(self):
        state = []
        @contextmanager
        def woohoo():
            state.append(1)
            spróbuj:
                uzyskaj 42
            w_końcu:
                state.append(999)
        przy self.assertRaises(ZeroDivisionError):
            przy woohoo() jako x:
                self.assertEqual(state, [1])
                self.assertEqual(x, 42)
                state.append(x)
                podnieś ZeroDivisionError()
        self.assertEqual(state, [1, 42, 999])

    def test_contextmanager_no_reraise(self):
        @contextmanager
        def whee():
            uzyskaj
        ctx = whee()
        ctx.__enter__()
        # Calling __exit__ should nie result w an exception
        self.assertNieprawda(ctx.__exit__(TypeError, TypeError("foo"), Nic))

    def test_contextmanager_trap_uzyskaj_after_throw(self):
        @contextmanager
        def whoo():
            spróbuj:
                uzyskaj
            wyjąwszy:
                uzyskaj
        ctx = whoo()
        ctx.__enter__()
        self.assertRaises(
            RuntimeError, ctx.__exit__, TypeError, TypeError("foo"), Nic
        )

    def test_contextmanager_except(self):
        state = []
        @contextmanager
        def woohoo():
            state.append(1)
            spróbuj:
                uzyskaj 42
            wyjąwszy ZeroDivisionError jako e:
                state.append(e.args[0])
                self.assertEqual(state, [1, 42, 999])
        przy woohoo() jako x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
            podnieś ZeroDivisionError(999)
        self.assertEqual(state, [1, 42, 999])

    def test_contextmanager_except_stopiter(self):
        stop_exc = StopIteration('spam')
        @contextmanager
        def woohoo():
            uzyskaj
        spróbuj:
            przy self.assertWarnsRegex(PendingDeprecationWarning,
                                       "StopIteration"):
                przy woohoo():
                    podnieś stop_exc
        wyjąwszy Exception jako ex:
            self.assertIs(ex, stop_exc)
        inaczej:
            self.fail('StopIteration was suppressed')

    def test_contextmanager_except_pep479(self):
        code = """\
z __future__ zaimportuj generator_stop
z contextlib zaimportuj contextmanager
@contextmanager
def woohoo():
    uzyskaj
"""
        locals = {}
        exec(code, locals, locals)
        woohoo = locals['woohoo']

        stop_exc = StopIteration('spam')
        spróbuj:
            przy woohoo():
                podnieś stop_exc
        wyjąwszy Exception jako ex:
            self.assertIs(ex, stop_exc)
        inaczej:
            self.fail('StopIteration was suppressed')

    def _create_contextmanager_attribs(self):
        def attribs(**kw):
            def decorate(func):
                dla k,v w kw.items():
                    setattr(func,k,v)
                zwróć func
            zwróć decorate
        @contextmanager
        @attribs(foo='bar')
        def baz(spam):
            """Whee!"""
        zwróć baz

    def test_contextmanager_attribs(self):
        baz = self._create_contextmanager_attribs()
        self.assertEqual(baz.__name__,'baz')
        self.assertEqual(baz.foo, 'bar')

    @support.requires_docstrings
    def test_contextmanager_doc_attrib(self):
        baz = self._create_contextmanager_attribs()
        self.assertEqual(baz.__doc__, "Whee!")

    @support.requires_docstrings
    def test_instance_docstring_given_cm_docstring(self):
        baz = self._create_contextmanager_attribs()(Nic)
        self.assertEqual(baz.__doc__, "Whee!")

    def test_keywords(self):
        # Ensure no keyword arguments are inhibited
        @contextmanager
        def woohoo(self, func, args, kwds):
            uzyskaj (self, func, args, kwds)
        przy woohoo(self=11, func=22, args=33, kwds=44) jako target:
            self.assertEqual(target, (11, 22, 33, 44))


klasa ClosingTestCase(unittest.TestCase):

    @support.requires_docstrings
    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = closing.__doc__
        obj = closing(Nic)
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_closing(self):
        state = []
        klasa C:
            def close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        przy closing(x) jako y:
            self.assertEqual(x, y)
        self.assertEqual(state, [1])

    def test_closing_error(self):
        state = []
        klasa C:
            def close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        przy self.assertRaises(ZeroDivisionError):
            przy closing(x) jako y:
                self.assertEqual(x, y)
                1 / 0
        self.assertEqual(state, [1])

klasa FileContextTestCase(unittest.TestCase):

    def testWithOpen(self):
        tfn = tempfile.mktemp()
        spróbuj:
            f = Nic
            przy open(tfn, "w") jako f:
                self.assertNieprawda(f.closed)
                f.write("Booh\n")
            self.assertPrawda(f.closed)
            f = Nic
            przy self.assertRaises(ZeroDivisionError):
                przy open(tfn, "r") jako f:
                    self.assertNieprawda(f.closed)
                    self.assertEqual(f.read(), "Booh\n")
                    1 / 0
            self.assertPrawda(f.closed)
        w_końcu:
            support.unlink(tfn)

@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa LockContextTestCase(unittest.TestCase):

    def boilerPlate(self, lock, locked):
        self.assertNieprawda(locked())
        przy lock:
            self.assertPrawda(locked())
        self.assertNieprawda(locked())
        przy self.assertRaises(ZeroDivisionError):
            przy lock:
                self.assertPrawda(locked())
                1 / 0
        self.assertNieprawda(locked())

    def testWithLock(self):
        lock = threading.Lock()
        self.boilerPlate(lock, lock.locked)

    def testWithRLock(self):
        lock = threading.RLock()
        self.boilerPlate(lock, lock._is_owned)

    def testWithCondition(self):
        lock = threading.Condition()
        def locked():
            zwróć lock._is_owned()
        self.boilerPlate(lock, locked)

    def testWithSemaphore(self):
        lock = threading.Semaphore()
        def locked():
            jeżeli lock.acquire(Nieprawda):
                lock.release()
                zwróć Nieprawda
            inaczej:
                zwróć Prawda
        self.boilerPlate(lock, locked)

    def testWithBoundedSemaphore(self):
        lock = threading.BoundedSemaphore()
        def locked():
            jeżeli lock.acquire(Nieprawda):
                lock.release()
                zwróć Nieprawda
            inaczej:
                zwróć Prawda
        self.boilerPlate(lock, locked)


klasa mycontext(ContextDecorator):
    """Example decoration-compatible context manager dla testing"""
    started = Nieprawda
    exc = Nic
    catch = Nieprawda

    def __enter__(self):
        self.started = Prawda
        zwróć self

    def __exit__(self, *exc):
        self.exc = exc
        zwróć self.catch


klasa TestContextDecorator(unittest.TestCase):

    @support.requires_docstrings
    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = mycontext.__doc__
        obj = mycontext()
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_contextdecorator(self):
        context = mycontext()
        przy context jako result:
            self.assertIs(result, context)
            self.assertPrawda(context.started)

        self.assertEqual(context.exc, (Nic, Nic, Nic))


    def test_contextdecorator_with_exception(self):
        context = mycontext()

        przy self.assertRaisesRegex(NameError, 'foo'):
            przy context:
                podnieś NameError('foo')
        self.assertIsNotNic(context.exc)
        self.assertIs(context.exc[0], NameError)

        context = mycontext()
        context.catch = Prawda
        przy context:
            podnieś NameError('foo')
        self.assertIsNotNic(context.exc)
        self.assertIs(context.exc[0], NameError)


    def test_decorator(self):
        context = mycontext()

        @context
        def test():
            self.assertIsNic(context.exc)
            self.assertPrawda(context.started)
        test()
        self.assertEqual(context.exc, (Nic, Nic, Nic))


    def test_decorator_with_exception(self):
        context = mycontext()

        @context
        def test():
            self.assertIsNic(context.exc)
            self.assertPrawda(context.started)
            podnieś NameError('foo')

        przy self.assertRaisesRegex(NameError, 'foo'):
            test()
        self.assertIsNotNic(context.exc)
        self.assertIs(context.exc[0], NameError)


    def test_decorating_method(self):
        context = mycontext()

        klasa Test(object):

            @context
            def method(self, a, b, c=Nic):
                self.a = a
                self.b = b
                self.c = c

        # these tests are dla argument dalejing when used jako a decorator
        test = Test()
        test.method(1, 2)
        self.assertEqual(test.a, 1)
        self.assertEqual(test.b, 2)
        self.assertEqual(test.c, Nic)

        test = Test()
        test.method('a', 'b', 'c')
        self.assertEqual(test.a, 'a')
        self.assertEqual(test.b, 'b')
        self.assertEqual(test.c, 'c')

        test = Test()
        test.method(a=1, b=2)
        self.assertEqual(test.a, 1)
        self.assertEqual(test.b, 2)


    def test_typo_enter(self):
        klasa mycontext(ContextDecorator):
            def __unter__(self):
                dalej
            def __exit__(self, *exc):
                dalej

        przy self.assertRaises(AttributeError):
            przy mycontext():
                dalej


    def test_typo_exit(self):
        klasa mycontext(ContextDecorator):
            def __enter__(self):
                dalej
            def __uxit__(self, *exc):
                dalej

        przy self.assertRaises(AttributeError):
            przy mycontext():
                dalej


    def test_contextdecorator_as_mixin(self):
        klasa somecontext(object):
            started = Nieprawda
            exc = Nic

            def __enter__(self):
                self.started = Prawda
                zwróć self

            def __exit__(self, *exc):
                self.exc = exc

        klasa mycontext(somecontext, ContextDecorator):
            dalej

        context = mycontext()
        @context
        def test():
            self.assertIsNic(context.exc)
            self.assertPrawda(context.started)
        test()
        self.assertEqual(context.exc, (Nic, Nic, Nic))


    def test_contextmanager_as_decorator(self):
        @contextmanager
        def woohoo(y):
            state.append(y)
            uzyskaj
            state.append(999)

        state = []
        @woohoo(1)
        def test(x):
            self.assertEqual(state, [1])
            state.append(x)
        test('something')
        self.assertEqual(state, [1, 'something', 999])

        # Issue #11647: Ensure the decorated function jest 'reusable'
        state = []
        test('something inaczej')
        self.assertEqual(state, [1, 'something inaczej', 999])


klasa TestExitStack(unittest.TestCase):

    @support.requires_docstrings
    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = ExitStack.__doc__
        obj = ExitStack()
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_no_resources(self):
        przy ExitStack():
            dalej

    def test_callback(self):
        expected = [
            ((), {}),
            ((1,), {}),
            ((1,2), {}),
            ((), dict(example=1)),
            ((1,), dict(example=1)),
            ((1,2), dict(example=1)),
        ]
        result = []
        def _exit(*args, **kwds):
            """Test metadata propagation"""
            result.append((args, kwds))
        przy ExitStack() jako stack:
            dla args, kwds w reversed(expected):
                jeżeli args oraz kwds:
                    f = stack.callback(_exit, *args, **kwds)
                albo_inaczej args:
                    f = stack.callback(_exit, *args)
                albo_inaczej kwds:
                    f = stack.callback(_exit, **kwds)
                inaczej:
                    f = stack.callback(_exit)
                self.assertIs(f, _exit)
            dla wrapper w stack._exit_callbacks:
                self.assertIs(wrapper.__wrapped__, _exit)
                self.assertNotEqual(wrapper.__name__, _exit.__name__)
                self.assertIsNic(wrapper.__doc__, _exit.__doc__)
        self.assertEqual(result, expected)

    def test_push(self):
        exc_raised = ZeroDivisionError
        def _expect_exc(exc_type, exc, exc_tb):
            self.assertIs(exc_type, exc_raised)
        def _suppress_exc(*exc_details):
            zwróć Prawda
        def _expect_ok(exc_type, exc, exc_tb):
            self.assertIsNic(exc_type)
            self.assertIsNic(exc)
            self.assertIsNic(exc_tb)
        klasa ExitCM(object):
            def __init__(self, check_exc):
                self.check_exc = check_exc
            def __enter__(self):
                self.fail("Should nie be called!")
            def __exit__(self, *exc_details):
                self.check_exc(*exc_details)
        przy ExitStack() jako stack:
            stack.push(_expect_ok)
            self.assertIs(stack._exit_callbacks[-1], _expect_ok)
            cm = ExitCM(_expect_ok)
            stack.push(cm)
            self.assertIs(stack._exit_callbacks[-1].__self__, cm)
            stack.push(_suppress_exc)
            self.assertIs(stack._exit_callbacks[-1], _suppress_exc)
            cm = ExitCM(_expect_exc)
            stack.push(cm)
            self.assertIs(stack._exit_callbacks[-1].__self__, cm)
            stack.push(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1], _expect_exc)
            stack.push(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1], _expect_exc)
            1/0

    def test_enter_context(self):
        klasa TestCM(object):
            def __enter__(self):
                result.append(1)
            def __exit__(self, *exc_details):
                result.append(3)

        result = []
        cm = TestCM()
        przy ExitStack() jako stack:
            @stack.callback  # Registered first => cleaned up last
            def _exit():
                result.append(4)
            self.assertIsNotNic(_exit)
            stack.enter_context(cm)
            self.assertIs(stack._exit_callbacks[-1].__self__, cm)
            result.append(2)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_close(self):
        result = []
        przy ExitStack() jako stack:
            @stack.callback
            def _exit():
                result.append(1)
            self.assertIsNotNic(_exit)
            stack.close()
            result.append(2)
        self.assertEqual(result, [1, 2])

    def test_pop_all(self):
        result = []
        przy ExitStack() jako stack:
            @stack.callback
            def _exit():
                result.append(3)
            self.assertIsNotNic(_exit)
            new_stack = stack.pop_all()
            result.append(1)
        result.append(2)
        new_stack.close()
        self.assertEqual(result, [1, 2, 3])

    def test_exit_raise(self):
        przy self.assertRaises(ZeroDivisionError):
            przy ExitStack() jako stack:
                stack.push(lambda *exc: Nieprawda)
                1/0

    def test_exit_suppress(self):
        przy ExitStack() jako stack:
            stack.push(lambda *exc: Prawda)
            1/0

    def test_exit_exception_chaining_reference(self):
        # Sanity check to make sure that ExitStack chaining matches
        # actual nested przy statements
        klasa RaiseExc:
            def __init__(self, exc):
                self.exc = exc
            def __enter__(self):
                zwróć self
            def __exit__(self, *exc_details):
                podnieś self.exc

        klasa RaiseExcWithContext:
            def __init__(self, outer, inner):
                self.outer = outer
                self.inner = inner
            def __enter__(self):
                zwróć self
            def __exit__(self, *exc_details):
                spróbuj:
                    podnieś self.inner
                wyjąwszy:
                    podnieś self.outer

        klasa SuppressExc:
            def __enter__(self):
                zwróć self
            def __exit__(self, *exc_details):
                type(self).saved_details = exc_details
                zwróć Prawda

        spróbuj:
            przy RaiseExc(IndexError):
                przy RaiseExcWithContext(KeyError, AttributeError):
                    przy SuppressExc():
                        przy RaiseExc(ValueError):
                            1 / 0
        wyjąwszy IndexError jako exc:
            self.assertIsInstance(exc.__context__, KeyError)
            self.assertIsInstance(exc.__context__.__context__, AttributeError)
            # Inner exceptions were suppressed
            self.assertIsNic(exc.__context__.__context__.__context__)
        inaczej:
            self.fail("Expected IndexError, but no exception was podnieśd")
        # Check the inner exceptions
        inner_exc = SuppressExc.saved_details[1]
        self.assertIsInstance(inner_exc, ValueError)
        self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)

    def test_exit_exception_chaining(self):
        # Ensure exception chaining matches the reference behaviour
        def podnieś_exc(exc):
            podnieś exc

        saved_details = Nic
        def suppress_exc(*exc_details):
            nonlocal saved_details
            saved_details = exc_details
            zwróć Prawda

        spróbuj:
            przy ExitStack() jako stack:
                stack.callback(raise_exc, IndexError)
                stack.callback(raise_exc, KeyError)
                stack.callback(raise_exc, AttributeError)
                stack.push(suppress_exc)
                stack.callback(raise_exc, ValueError)
                1 / 0
        wyjąwszy IndexError jako exc:
            self.assertIsInstance(exc.__context__, KeyError)
            self.assertIsInstance(exc.__context__.__context__, AttributeError)
            # Inner exceptions were suppressed
            self.assertIsNic(exc.__context__.__context__.__context__)
        inaczej:
            self.fail("Expected IndexError, but no exception was podnieśd")
        # Check the inner exceptions
        inner_exc = saved_details[1]
        self.assertIsInstance(inner_exc, ValueError)
        self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)

    def test_exit_exception_non_suppressing(self):
        # http://bugs.python.org/issue19092
        def podnieś_exc(exc):
            podnieś exc

        def suppress_exc(*exc_details):
            zwróć Prawda

        spróbuj:
            przy ExitStack() jako stack:
                stack.callback(lambda: Nic)
                stack.callback(raise_exc, IndexError)
        wyjąwszy Exception jako exc:
            self.assertIsInstance(exc, IndexError)
        inaczej:
            self.fail("Expected IndexError, but no exception was podnieśd")

        spróbuj:
            przy ExitStack() jako stack:
                stack.callback(raise_exc, KeyError)
                stack.push(suppress_exc)
                stack.callback(raise_exc, IndexError)
        wyjąwszy Exception jako exc:
            self.assertIsInstance(exc, KeyError)
        inaczej:
            self.fail("Expected KeyError, but no exception was podnieśd")

    def test_exit_exception_with_correct_context(self):
        # http://bugs.python.org/issue20317
        @contextmanager
        def gets_the_context_right(exc):
            spróbuj:
                uzyskaj
            w_końcu:
                podnieś exc

        exc1 = Exception(1)
        exc2 = Exception(2)
        exc3 = Exception(3)
        exc4 = Exception(4)

        # The contextmanager already fixes the context, so prior to the
        # fix, ExitStack would try to fix it *again* oraz get into an
        # infinite self-referential loop
        spróbuj:
            przy ExitStack() jako stack:
                stack.enter_context(gets_the_context_right(exc4))
                stack.enter_context(gets_the_context_right(exc3))
                stack.enter_context(gets_the_context_right(exc2))
                podnieś exc1
        wyjąwszy Exception jako exc:
            self.assertIs(exc, exc4)
            self.assertIs(exc.__context__, exc3)
            self.assertIs(exc.__context__.__context__, exc2)
            self.assertIs(exc.__context__.__context__.__context__, exc1)
            self.assertIsNic(
                       exc.__context__.__context__.__context__.__context__)

    def test_exit_exception_with_existing_context(self):
        # Addresses a lack of test coverage discovered after checking w a
        # fix dla issue 20317 that still contained debugging code.
        def podnieś_nested(inner_exc, outer_exc):
            spróbuj:
                podnieś inner_exc
            w_końcu:
                podnieś outer_exc
        exc1 = Exception(1)
        exc2 = Exception(2)
        exc3 = Exception(3)
        exc4 = Exception(4)
        exc5 = Exception(5)
        spróbuj:
            przy ExitStack() jako stack:
                stack.callback(raise_nested, exc4, exc5)
                stack.callback(raise_nested, exc2, exc3)
                podnieś exc1
        wyjąwszy Exception jako exc:
            self.assertIs(exc, exc5)
            self.assertIs(exc.__context__, exc4)
            self.assertIs(exc.__context__.__context__, exc3)
            self.assertIs(exc.__context__.__context__.__context__, exc2)
            self.assertIs(
                 exc.__context__.__context__.__context__.__context__, exc1)
            self.assertIsNic(
                exc.__context__.__context__.__context__.__context__.__context__)



    def test_body_exception_suppress(self):
        def suppress_exc(*exc_details):
            zwróć Prawda
        spróbuj:
            przy ExitStack() jako stack:
                stack.push(suppress_exc)
                1/0
        wyjąwszy IndexError jako exc:
            self.fail("Expected no exception, got IndexError")

    def test_exit_exception_chaining_suppress(self):
        przy ExitStack() jako stack:
            stack.push(lambda *exc: Prawda)
            stack.push(lambda *exc: 1/0)
            stack.push(lambda *exc: {}[1])

    def test_excessive_nesting(self):
        # The original implementation would die przy RecursionError here
        przy ExitStack() jako stack:
            dla i w range(10000):
                stack.callback(int)

    def test_instance_bypass(self):
        klasa Example(object): dalej
        cm = Example()
        cm.__exit__ = object()
        stack = ExitStack()
        self.assertRaises(AttributeError, stack.enter_context, cm)
        stack.push(cm)
        self.assertIs(stack._exit_callbacks[-1], cm)


klasa TestRedirectStream:

    redirect_stream = Nic
    orig_stream = Nic

    @support.requires_docstrings
    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = self.redirect_stream.__doc__
        obj = self.redirect_stream(Nic)
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_no_redirect_in_init(self):
        orig_stdout = getattr(sys, self.orig_stream)
        self.redirect_stream(Nic)
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)

    def test_redirect_to_string_io(self):
        f = io.StringIO()
        msg = "Consider an API like help(), which prints directly to stdout"
        orig_stdout = getattr(sys, self.orig_stream)
        przy self.redirect_stream(f):
            print(msg, file=getattr(sys, self.orig_stream))
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)
        s = f.getvalue().strip()
        self.assertEqual(s, msg)

    def test_enter_result_is_target(self):
        f = io.StringIO()
        przy self.redirect_stream(f) jako enter_result:
            self.assertIs(enter_result, f)

    def test_cm_is_reusable(self):
        f = io.StringIO()
        write_to_f = self.redirect_stream(f)
        orig_stdout = getattr(sys, self.orig_stream)
        przy write_to_f:
            print("Hello", end=" ", file=getattr(sys, self.orig_stream))
        przy write_to_f:
            print("World!", file=getattr(sys, self.orig_stream))
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)
        s = f.getvalue()
        self.assertEqual(s, "Hello World!\n")

    def test_cm_is_reentrant(self):
        f = io.StringIO()
        write_to_f = self.redirect_stream(f)
        orig_stdout = getattr(sys, self.orig_stream)
        przy write_to_f:
            print("Hello", end=" ", file=getattr(sys, self.orig_stream))
            przy write_to_f:
                print("World!", file=getattr(sys, self.orig_stream))
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)
        s = f.getvalue()
        self.assertEqual(s, "Hello World!\n")


klasa TestRedirectStdout(TestRedirectStream, unittest.TestCase):

    redirect_stream = redirect_stdout
    orig_stream = "stdout"


klasa TestRedirectStderr(TestRedirectStream, unittest.TestCase):

    redirect_stream = redirect_stderr
    orig_stream = "stderr"


klasa TestSuppress(unittest.TestCase):

    @support.requires_docstrings
    def test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = suppress.__doc__
        obj = suppress()
        self.assertEqual(obj.__doc__, cm_docstring)

    def test_no_result_from_enter(self):
        przy suppress(ValueError) jako enter_result:
            self.assertIsNic(enter_result)

    def test_no_exception(self):
        przy suppress(ValueError):
            self.assertEqual(pow(2, 5), 32)

    def test_exact_exception(self):
        przy suppress(TypeError):
            len(5)

    def test_exception_hierarchy(self):
        przy suppress(LookupError):
            'Hello'[50]

    def test_other_exception(self):
        przy self.assertRaises(ZeroDivisionError):
            przy suppress(TypeError):
                1/0

    def test_no_args(self):
        przy self.assertRaises(ZeroDivisionError):
            przy suppress():
                1/0

    def test_multiple_exception_args(self):
        przy suppress(ZeroDivisionError, TypeError):
            1/0
        przy suppress(ZeroDivisionError, TypeError):
            len(5)

    def test_cm_is_reentrant(self):
        ignore_exceptions = suppress(Exception)
        przy ignore_exceptions:
            dalej
        przy ignore_exceptions:
            len(5)
        przy ignore_exceptions:
            1/0
            przy ignore_exceptions: # Check nested usage
                len(5)

jeżeli __name__ == "__main__":
    unittest.main()
