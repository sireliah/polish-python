"""Unit tests dla the przy statement specified w PEP 343."""


__author__ = "Mike Bland"
__email__ = "mbland at acm dot org"

zaimportuj sys
zaimportuj unittest
z collections zaimportuj deque
z contextlib zaimportuj _GeneratorContextManager, contextmanager


klasa MockContextManager(_GeneratorContextManager):
    def __init__(self, *args):
        super().__init__(*args)
        self.enter_called = Nieprawda
        self.exit_called = Nieprawda
        self.exit_args = Nic

    def __enter__(self):
        self.enter_called = Prawda
        zwróć _GeneratorContextManager.__enter__(self)

    def __exit__(self, type, value, traceback):
        self.exit_called = Prawda
        self.exit_args = (type, value, traceback)
        zwróć _GeneratorContextManager.__exit__(self, type,
                                                 value, traceback)


def mock_contextmanager(func):
    def helper(*args, **kwds):
        zwróć MockContextManager(func, args, kwds)
    zwróć helper


klasa MockResource(object):
    def __init__(self):
        self.uzyskajed = Nieprawda
        self.stopped = Nieprawda


@mock_contextmanager
def mock_contextmanager_generator():
    mock = MockResource()
    spróbuj:
        mock.uzyskajed = Prawda
        uzyskaj mock
    w_końcu:
        mock.stopped = Prawda


klasa Nested(object):

    def __init__(self, *managers):
        self.managers = managers
        self.entered = Nic

    def __enter__(self):
        jeżeli self.entered jest nie Nic:
            podnieś RuntimeError("Context jest nie reentrant")
        self.entered = deque()
        vars = []
        spróbuj:
            dla mgr w self.managers:
                vars.append(mgr.__enter__())
                self.entered.appendleft(mgr)
        wyjąwszy:
            jeżeli nie self.__exit__(*sys.exc_info()):
                podnieś
        zwróć vars

    def __exit__(self, *exc_info):
        # Behave like nested przy statements
        # first in, last out
        # New exceptions override old ones
        ex = exc_info
        dla mgr w self.entered:
            spróbuj:
                jeżeli mgr.__exit__(*ex):
                    ex = (Nic, Nic, Nic)
            wyjąwszy:
                ex = sys.exc_info()
        self.entered = Nic
        jeżeli ex jest nie exc_info:
            podnieś ex[0](ex[1]).with_traceback(ex[2])


klasa MockNested(Nested):
    def __init__(self, *managers):
        Nested.__init__(self, *managers)
        self.enter_called = Nieprawda
        self.exit_called = Nieprawda
        self.exit_args = Nic

    def __enter__(self):
        self.enter_called = Prawda
        zwróć Nested.__enter__(self)

    def __exit__(self, *exc_info):
        self.exit_called = Prawda
        self.exit_args = exc_info
        zwróć Nested.__exit__(self, *exc_info)


klasa FailureTestCase(unittest.TestCase):
    def testNameError(self):
        def fooNotDeclared():
            przy foo: dalej
        self.assertRaises(NameError, fooNotDeclared)

    def testEnterAttributeError(self):
        klasa LacksEnter(object):
            def __exit__(self, type, value, traceback):
                dalej

        def fooLacksEnter():
            foo = LacksEnter()
            przy foo: dalej
        self.assertRaises(AttributeError, fooLacksEnter)

    def testExitAttributeError(self):
        klasa LacksExit(object):
            def __enter__(self):
                dalej

        def fooLacksExit():
            foo = LacksExit()
            przy foo: dalej
        self.assertRaises(AttributeError, fooLacksExit)

    def assertRaisesSyntaxError(self, codestr):
        def shouldRaiseSyntaxError(s):
            compile(s, '', 'single')
        self.assertRaises(SyntaxError, shouldRaiseSyntaxError, codestr)

    def testAssignmentToNicError(self):
        self.assertRaisesSyntaxError('przy mock jako Nic:\n  dalej')
        self.assertRaisesSyntaxError(
            'przy mock jako (Nic):\n'
            '  dalej')

    def testAssignmentToEmptyTupleError(self):
        self.assertRaisesSyntaxError(
            'przy mock jako ():\n'
            '  dalej')

    def testAssignmentToTupleOnlyContainingNicError(self):
        self.assertRaisesSyntaxError('przy mock jako Nic,:\n  dalej')
        self.assertRaisesSyntaxError(
            'przy mock jako (Nic,):\n'
            '  dalej')

    def testAssignmentToTupleContainingNicError(self):
        self.assertRaisesSyntaxError(
            'przy mock jako (foo, Nic, bar):\n'
            '  dalej')

    def testEnterThrows(self):
        klasa EnterThrows(object):
            def __enter__(self):
                podnieś RuntimeError("Enter threw")
            def __exit__(self, *args):
                dalej

        def shouldThrow():
            ct = EnterThrows()
            self.foo = Nic
            przy ct jako self.foo:
                dalej
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertEqual(self.foo, Nic)

    def testExitThrows(self):
        klasa ExitThrows(object):
            def __enter__(self):
                zwróć
            def __exit__(self, *args):
                podnieś RuntimeError(42)
        def shouldThrow():
            przy ExitThrows():
                dalej
        self.assertRaises(RuntimeError, shouldThrow)

klasa ContextmanagerAssertionMixin(object):

    def setUp(self):
        self.TEST_EXCEPTION = RuntimeError("test exception")

    def assertInWithManagerInvariants(self, mock_manager):
        self.assertPrawda(mock_manager.enter_called)
        self.assertNieprawda(mock_manager.exit_called)
        self.assertEqual(mock_manager.exit_args, Nic)

    def assertAfterWithManagerInvariants(self, mock_manager, exit_args):
        self.assertPrawda(mock_manager.enter_called)
        self.assertPrawda(mock_manager.exit_called)
        self.assertEqual(mock_manager.exit_args, exit_args)

    def assertAfterWithManagerInvariantsNoError(self, mock_manager):
        self.assertAfterWithManagerInvariants(mock_manager,
            (Nic, Nic, Nic))

    def assertInWithGeneratorInvariants(self, mock_generator):
        self.assertPrawda(mock_generator.uzyskajed)
        self.assertNieprawda(mock_generator.stopped)

    def assertAfterWithGeneratorInvariantsNoError(self, mock_generator):
        self.assertPrawda(mock_generator.uzyskajed)
        self.assertPrawda(mock_generator.stopped)

    def podnieśTestException(self):
        podnieś self.TEST_EXCEPTION

    def assertAfterWithManagerInvariantsWithError(self, mock_manager,
                                                  exc_type=Nic):
        self.assertPrawda(mock_manager.enter_called)
        self.assertPrawda(mock_manager.exit_called)
        jeżeli exc_type jest Nic:
            self.assertEqual(mock_manager.exit_args[1], self.TEST_EXCEPTION)
            exc_type = type(self.TEST_EXCEPTION)
        self.assertEqual(mock_manager.exit_args[0], exc_type)
        # Test the __exit__ arguments. Issue #7853
        self.assertIsInstance(mock_manager.exit_args[1], exc_type)
        self.assertIsNot(mock_manager.exit_args[2], Nic)

    def assertAfterWithGeneratorInvariantsWithError(self, mock_generator):
        self.assertPrawda(mock_generator.uzyskajed)
        self.assertPrawda(mock_generator.stopped)


klasa NicxceptionalTestCase(unittest.TestCase, ContextmanagerAssertionMixin):
    def testInlineGeneratorSyntax(self):
        przy mock_contextmanager_generator():
            dalej

    def testUnboundGenerator(self):
        mock = mock_contextmanager_generator()
        przy mock:
            dalej
        self.assertAfterWithManagerInvariantsNoError(mock)

    def testInlineGeneratorBoundSyntax(self):
        przy mock_contextmanager_generator() jako foo:
            self.assertInWithGeneratorInvariants(foo)
        # FIXME: In the future, we'll try to keep the bound names z leaking
        self.assertAfterWithGeneratorInvariantsNoError(foo)

    def testInlineGeneratorBoundToExistingVariable(self):
        foo = Nic
        przy mock_contextmanager_generator() jako foo:
            self.assertInWithGeneratorInvariants(foo)
        self.assertAfterWithGeneratorInvariantsNoError(foo)

    def testInlineGeneratorBoundToDottedVariable(self):
        przy mock_contextmanager_generator() jako self.foo:
            self.assertInWithGeneratorInvariants(self.foo)
        self.assertAfterWithGeneratorInvariantsNoError(self.foo)

    def testBoundGenerator(self):
        mock = mock_contextmanager_generator()
        przy mock jako foo:
            self.assertInWithGeneratorInvariants(foo)
            self.assertInWithManagerInvariants(mock)
        self.assertAfterWithGeneratorInvariantsNoError(foo)
        self.assertAfterWithManagerInvariantsNoError(mock)

    def testNestedSingleStatements(self):
        mock_a = mock_contextmanager_generator()
        przy mock_a jako foo:
            mock_b = mock_contextmanager_generator()
            przy mock_b jako bar:
                self.assertInWithManagerInvariants(mock_a)
                self.assertInWithManagerInvariants(mock_b)
                self.assertInWithGeneratorInvariants(foo)
                self.assertInWithGeneratorInvariants(bar)
            self.assertAfterWithManagerInvariantsNoError(mock_b)
            self.assertAfterWithGeneratorInvariantsNoError(bar)
            self.assertInWithManagerInvariants(mock_a)
            self.assertInWithGeneratorInvariants(foo)
        self.assertAfterWithManagerInvariantsNoError(mock_a)
        self.assertAfterWithGeneratorInvariantsNoError(foo)


klasa NestedNicxceptionalTestCase(unittest.TestCase,
    ContextmanagerAssertionMixin):
    def testSingleArgInlineGeneratorSyntax(self):
        przy Nested(mock_contextmanager_generator()):
            dalej

    def testSingleArgBoundToNonTuple(self):
        m = mock_contextmanager_generator()
        # This will bind all the arguments to nested() into a single list
        # assigned to foo.
        przy Nested(m) jako foo:
            self.assertInWithManagerInvariants(m)
        self.assertAfterWithManagerInvariantsNoError(m)

    def testSingleArgBoundToSingleElementParenthesizedList(self):
        m = mock_contextmanager_generator()
        # This will bind all the arguments to nested() into a single list
        # assigned to foo.
        przy Nested(m) jako (foo):
            self.assertInWithManagerInvariants(m)
        self.assertAfterWithManagerInvariantsNoError(m)

    def testSingleArgBoundToMultipleElementTupleError(self):
        def shouldThrowValueError():
            przy Nested(mock_contextmanager_generator()) jako (foo, bar):
                dalej
        self.assertRaises(ValueError, shouldThrowValueError)

    def testSingleArgUnbound(self):
        mock_contextmanager = mock_contextmanager_generator()
        mock_nested = MockNested(mock_contextmanager)
        przy mock_nested:
            self.assertInWithManagerInvariants(mock_contextmanager)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithManagerInvariantsNoError(mock_contextmanager)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)

    def testMultipleArgUnbound(self):
        m = mock_contextmanager_generator()
        n = mock_contextmanager_generator()
        o = mock_contextmanager_generator()
        mock_nested = MockNested(m, n, o)
        przy mock_nested:
            self.assertInWithManagerInvariants(m)
            self.assertInWithManagerInvariants(n)
            self.assertInWithManagerInvariants(o)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithManagerInvariantsNoError(m)
        self.assertAfterWithManagerInvariantsNoError(n)
        self.assertAfterWithManagerInvariantsNoError(o)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)

    def testMultipleArgBound(self):
        mock_nested = MockNested(mock_contextmanager_generator(),
            mock_contextmanager_generator(), mock_contextmanager_generator())
        przy mock_nested jako (m, n, o):
            self.assertInWithGeneratorInvariants(m)
            self.assertInWithGeneratorInvariants(n)
            self.assertInWithGeneratorInvariants(o)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithGeneratorInvariantsNoError(m)
        self.assertAfterWithGeneratorInvariantsNoError(n)
        self.assertAfterWithGeneratorInvariantsNoError(o)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)


klasa ExceptionalTestCase(ContextmanagerAssertionMixin, unittest.TestCase):
    def testSingleResource(self):
        cm = mock_contextmanager_generator()
        def shouldThrow():
            przy cm jako self.resource:
                self.assertInWithManagerInvariants(cm)
                self.assertInWithGeneratorInvariants(self.resource)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource)

    def testExceptionNormalized(self):
        cm = mock_contextmanager_generator()
        def shouldThrow():
            przy cm jako self.resource:
                # Note this relies on the fact that 1 // 0 produces an exception
                # that jest nie normalized immediately.
                1 // 0
        self.assertRaises(ZeroDivisionError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm, ZeroDivisionError)

    def testNestedSingleStatements(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        def shouldThrow():
            przy mock_a jako self.foo:
                przy mock_b jako self.bar:
                    self.assertInWithManagerInvariants(mock_a)
                    self.assertInWithManagerInvariants(mock_b)
                    self.assertInWithGeneratorInvariants(self.foo)
                    self.assertInWithGeneratorInvariants(self.bar)
                    self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithManagerInvariantsWithError(mock_b)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)
        self.assertAfterWithGeneratorInvariantsWithError(self.bar)

    def testMultipleResourcesInSingleStatement(self):
        cm_a = mock_contextmanager_generator()
        cm_b = mock_contextmanager_generator()
        mock_nested = MockNested(cm_a, cm_b)
        def shouldThrow():
            przy mock_nested jako (self.resource_a, self.resource_b):
                self.assertInWithManagerInvariants(cm_a)
                self.assertInWithManagerInvariants(cm_b)
                self.assertInWithManagerInvariants(mock_nested)
                self.assertInWithGeneratorInvariants(self.resource_a)
                self.assertInWithGeneratorInvariants(self.resource_b)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm_a)
        self.assertAfterWithManagerInvariantsWithError(cm_b)
        self.assertAfterWithManagerInvariantsWithError(mock_nested)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource_a)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource_b)

    def testNestedExceptionBeforeInnerStatement(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        self.bar = Nic
        def shouldThrow():
            przy mock_a jako self.foo:
                self.assertInWithManagerInvariants(mock_a)
                self.assertInWithGeneratorInvariants(self.foo)
                self.raiseTestException()
                przy mock_b jako self.bar:
                    dalej
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)

        # The inner statement stuff should never have been touched
        self.assertEqual(self.bar, Nic)
        self.assertNieprawda(mock_b.enter_called)
        self.assertNieprawda(mock_b.exit_called)
        self.assertEqual(mock_b.exit_args, Nic)

    def testNestedExceptionAfterInnerStatement(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        def shouldThrow():
            przy mock_a jako self.foo:
                przy mock_b jako self.bar:
                    self.assertInWithManagerInvariants(mock_a)
                    self.assertInWithManagerInvariants(mock_b)
                    self.assertInWithGeneratorInvariants(self.foo)
                    self.assertInWithGeneratorInvariants(self.bar)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithManagerInvariantsNoError(mock_b)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)
        self.assertAfterWithGeneratorInvariantsNoError(self.bar)

    def testRaisedStopIteration1(self):
        # From bug 1462485
        @contextmanager
        def cm():
            uzyskaj

        def shouldThrow():
            przy cm():
                podnieś StopIteration("z with")

        przy self.assertWarnsRegex(PendingDeprecationWarning, "StopIteration"):
            self.assertRaises(StopIteration, shouldThrow)

    def testRaisedStopIteration2(self):
        # From bug 1462485
        klasa cm(object):
            def __enter__(self):
                dalej
            def __exit__(self, type, value, traceback):
                dalej

        def shouldThrow():
            przy cm():
                podnieś StopIteration("z with")

        self.assertRaises(StopIteration, shouldThrow)

    def testRaisedStopIteration3(self):
        # Another variant where the exception hasn't been instantiated
        # From bug 1705170
        @contextmanager
        def cm():
            uzyskaj

        def shouldThrow():
            przy cm():
                podnieś next(iter([]))

        przy self.assertWarnsRegex(PendingDeprecationWarning, "StopIteration"):
            self.assertRaises(StopIteration, shouldThrow)

    def testRaisedGeneratorExit1(self):
        # From bug 1462485
        @contextmanager
        def cm():
            uzyskaj

        def shouldThrow():
            przy cm():
                podnieś GeneratorExit("z with")

        self.assertRaises(GeneratorExit, shouldThrow)

    def testRaisedGeneratorExit2(self):
        # From bug 1462485
        klasa cm (object):
            def __enter__(self):
                dalej
            def __exit__(self, type, value, traceback):
                dalej

        def shouldThrow():
            przy cm():
                podnieś GeneratorExit("z with")

        self.assertRaises(GeneratorExit, shouldThrow)

    def testErrorsInBool(self):
        # issue4589: __exit__ zwróć code may podnieś an exception
        # when looking at its truth value.

        klasa cm(object):
            def __init__(self, bool_conversion):
                klasa Bool:
                    def __bool__(self):
                        zwróć bool_conversion()
                self.exit_result = Bool()
            def __enter__(self):
                zwróć 3
            def __exit__(self, a, b, c):
                zwróć self.exit_result

        def trueAsBool():
            przy cm(lambda: Prawda):
                self.fail("Should NOT see this")
        trueAsBool()

        def falseAsBool():
            przy cm(lambda: Nieprawda):
                self.fail("Should podnieś")
        self.assertRaises(AssertionError, falseAsBool)

        def failAsBool():
            przy cm(lambda: 1//0):
                self.fail("Should NOT see this")
        self.assertRaises(ZeroDivisionError, failAsBool)


klasa NonLocalFlowControlTestCase(unittest.TestCase):

    def testWithBreak(self):
        counter = 0
        dopóki Prawda:
            counter += 1
            przy mock_contextmanager_generator():
                counter += 10
                przerwij
            counter += 100 # Not reached
        self.assertEqual(counter, 11)

    def testWithContinue(self):
        counter = 0
        dopóki Prawda:
            counter += 1
            jeżeli counter > 2:
                przerwij
            przy mock_contextmanager_generator():
                counter += 10
                kontynuuj
            counter += 100 # Not reached
        self.assertEqual(counter, 12)

    def testWithReturn(self):
        def foo():
            counter = 0
            dopóki Prawda:
                counter += 1
                przy mock_contextmanager_generator():
                    counter += 10
                    zwróć counter
                counter += 100 # Not reached
        self.assertEqual(foo(), 11)

    def testWithYield(self):
        def gen():
            przy mock_contextmanager_generator():
                uzyskaj 12
                uzyskaj 13
        x = list(gen())
        self.assertEqual(x, [12, 13])

    def testWithRaise(self):
        counter = 0
        spróbuj:
            counter += 1
            przy mock_contextmanager_generator():
                counter += 10
                podnieś RuntimeError
            counter += 100 # Not reached
        wyjąwszy RuntimeError:
            self.assertEqual(counter, 11)
        inaczej:
            self.fail("Didn't podnieś RuntimeError")


klasa AssignmentTargetTestCase(unittest.TestCase):

    def testSingleComplexTarget(self):
        targets = {1: [0, 1, 2]}
        przy mock_contextmanager_generator() jako targets[1][0]:
            self.assertEqual(list(targets.keys()), [1])
            self.assertEqual(targets[1][0].__class__, MockResource)
        przy mock_contextmanager_generator() jako list(targets.values())[0][1]:
            self.assertEqual(list(targets.keys()), [1])
            self.assertEqual(targets[1][1].__class__, MockResource)
        przy mock_contextmanager_generator() jako targets[2]:
            keys = list(targets.keys())
            keys.sort()
            self.assertEqual(keys, [1, 2])
        klasa C: dalej
        blah = C()
        przy mock_contextmanager_generator() jako blah.foo:
            self.assertEqual(hasattr(blah, "foo"), Prawda)

    def testMultipleComplexTargets(self):
        klasa C:
            def __enter__(self): zwróć 1, 2, 3
            def __exit__(self, t, v, tb): dalej
        targets = {1: [0, 1, 2]}
        przy C() jako (targets[1][0], targets[1][1], targets[1][2]):
            self.assertEqual(targets, {1: [1, 2, 3]})
        przy C() jako (list(targets.values())[0][2], list(targets.values())[0][1], list(targets.values())[0][0]):
            self.assertEqual(targets, {1: [3, 2, 1]})
        przy C() jako (targets[1], targets[2], targets[3]):
            self.assertEqual(targets, {1: 1, 2: 2, 3: 3})
        klasa B: dalej
        blah = B()
        przy C() jako (blah.one, blah.two, blah.three):
            self.assertEqual(blah.one, 1)
            self.assertEqual(blah.two, 2)
            self.assertEqual(blah.three, 3)


klasa ExitSwallowsExceptionTestCase(unittest.TestCase):

    def testExitPrawdaSwallowsException(self):
        klasa AfricanSwallow:
            def __enter__(self): dalej
            def __exit__(self, t, v, tb): zwróć Prawda
        spróbuj:
            przy AfricanSwallow():
                1/0
        wyjąwszy ZeroDivisionError:
            self.fail("ZeroDivisionError should have been swallowed")

    def testExitNieprawdaDoesntSwallowException(self):
        klasa EuropeanSwallow:
            def __enter__(self): dalej
            def __exit__(self, t, v, tb): zwróć Nieprawda
        spróbuj:
            przy EuropeanSwallow():
                1/0
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            self.fail("ZeroDivisionError should have been podnieśd")


klasa NestedWith(unittest.TestCase):

    klasa Dummy(object):
        def __init__(self, value=Nic, gobble=Nieprawda):
            jeżeli value jest Nic:
                value = self
            self.value = value
            self.gobble = gobble
            self.enter_called = Nieprawda
            self.exit_called = Nieprawda

        def __enter__(self):
            self.enter_called = Prawda
            zwróć self.value

        def __exit__(self, *exc_info):
            self.exit_called = Prawda
            self.exc_info = exc_info
            jeżeli self.gobble:
                zwróć Prawda

    klasa InitRaises(object):
        def __init__(self): podnieś RuntimeError()

    klasa EnterRaises(object):
        def __enter__(self): podnieś RuntimeError()
        def __exit__(self, *exc_info): dalej

    klasa ExitRaises(object):
        def __enter__(self): dalej
        def __exit__(self, *exc_info): podnieś RuntimeError()

    def testNoExceptions(self):
        przy self.Dummy() jako a, self.Dummy() jako b:
            self.assertPrawda(a.enter_called)
            self.assertPrawda(b.enter_called)
        self.assertPrawda(a.exit_called)
        self.assertPrawda(b.exit_called)

    def testExceptionInExprList(self):
        spróbuj:
            przy self.Dummy() jako a, self.InitRaises():
                dalej
        wyjąwszy:
            dalej
        self.assertPrawda(a.enter_called)
        self.assertPrawda(a.exit_called)

    def testExceptionInEnter(self):
        spróbuj:
            przy self.Dummy() jako a, self.EnterRaises():
                self.fail('body of bad przy executed')
        wyjąwszy RuntimeError:
            dalej
        inaczej:
            self.fail('RuntimeError nie reraised')
        self.assertPrawda(a.enter_called)
        self.assertPrawda(a.exit_called)

    def testExceptionInExit(self):
        body_executed = Nieprawda
        przy self.Dummy(gobble=Prawda) jako a, self.ExitRaises():
            body_executed = Prawda
        self.assertPrawda(a.enter_called)
        self.assertPrawda(a.exit_called)
        self.assertPrawda(body_executed)
        self.assertNotEqual(a.exc_info[0], Nic)

    def testEnterReturnsTuple(self):
        przy self.Dummy(value=(1,2)) jako (a1, a2), \
             self.Dummy(value=(10, 20)) jako (b1, b2):
            self.assertEqual(1, a1)
            self.assertEqual(2, a2)
            self.assertEqual(10, b1)
            self.assertEqual(20, b2)

jeżeli __name__ == '__main__':
    unittest.main()
