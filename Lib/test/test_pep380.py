# -*- coding: utf-8 -*-

"""
Test suite dla PEP 380 implementation

adapted z original tests written by Greg Ewing
see <http://www.cosc.canterbury.ac.nz/greg.ewing/python/uzyskaj-from/YieldFrom-Python3.1.2-rev5.zip>
"""

zaimportuj unittest
zaimportuj io
zaimportuj sys
zaimportuj inspect
zaimportuj parser

z test.support zaimportuj captured_stderr, disable_gc, gc_collect

klasa TestPEP380Operation(unittest.TestCase):
    """
    Test semantics.
    """

    def test_delegation_of_initial_next_to_subgenerator(self):
        """
        Test delegation of initial next() call to subgenerator
        """
        trace = []
        def g1():
            trace.append("Starting g1")
            uzyskaj z g2()
            trace.append("Finishing g1")
        def g2():
            trace.append("Starting g2")
            uzyskaj 42
            trace.append("Finishing g2")
        dla x w g1():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Starting g2",
            "Yielded 42",
            "Finishing g2",
            "Finishing g1",
        ])

    def test_raising_exception_in_initial_next_call(self):
        """
        Test raising exception w initial next() call
        """
        trace = []
        def g1():
            spróbuj:
                trace.append("Starting g1")
                uzyskaj z g2()
            w_końcu:
                trace.append("Finishing g1")
        def g2():
            spróbuj:
                trace.append("Starting g2")
                podnieś ValueError("spanish inquisition occurred")
            w_końcu:
                trace.append("Finishing g2")
        spróbuj:
            dla x w g1():
                trace.append("Yielded %s" % (x,))
        wyjąwszy ValueError jako e:
            self.assertEqual(e.args[0], "spanish inquisition occurred")
        inaczej:
            self.fail("subgenerator failed to podnieś ValueError")
        self.assertEqual(trace,[
            "Starting g1",
            "Starting g2",
            "Finishing g2",
            "Finishing g1",
        ])

    def test_delegation_of_next_call_to_subgenerator(self):
        """
        Test delegation of next() call to subgenerator
        """
        trace = []
        def g1():
            trace.append("Starting g1")
            uzyskaj "g1 ham"
            uzyskaj z g2()
            uzyskaj "g1 eggs"
            trace.append("Finishing g1")
        def g2():
            trace.append("Starting g2")
            uzyskaj "g2 spam"
            uzyskaj "g2 more spam"
            trace.append("Finishing g2")
        dla x w g1():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Yielded g2 more spam",
            "Finishing g2",
            "Yielded g1 eggs",
            "Finishing g1",
        ])

    def test_raising_exception_in_delegated_next_call(self):
        """
        Test raising exception w delegated next() call
        """
        trace = []
        def g1():
            spróbuj:
                trace.append("Starting g1")
                uzyskaj "g1 ham"
                uzyskaj z g2()
                uzyskaj "g1 eggs"
            w_końcu:
                trace.append("Finishing g1")
        def g2():
            spróbuj:
                trace.append("Starting g2")
                uzyskaj "g2 spam"
                podnieś ValueError("hovercraft jest full of eels")
                uzyskaj "g2 more spam"
            w_końcu:
                trace.append("Finishing g2")
        spróbuj:
            dla x w g1():
                trace.append("Yielded %s" % (x,))
        wyjąwszy ValueError jako e:
            self.assertEqual(e.args[0], "hovercraft jest full of eels")
        inaczej:
            self.fail("subgenerator failed to podnieś ValueError")
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Finishing g2",
            "Finishing g1",
        ])

    def test_delegation_of_send(self):
        """
        Test delegation of send()
        """
        trace = []
        def g1():
            trace.append("Starting g1")
            x = uzyskaj "g1 ham"
            trace.append("g1 received %s" % (x,))
            uzyskaj z g2()
            x = uzyskaj "g1 eggs"
            trace.append("g1 received %s" % (x,))
            trace.append("Finishing g1")
        def g2():
            trace.append("Starting g2")
            x = uzyskaj "g2 spam"
            trace.append("g2 received %s" % (x,))
            x = uzyskaj "g2 more spam"
            trace.append("g2 received %s" % (x,))
            trace.append("Finishing g2")
        g = g1()
        y = next(g)
        x = 1
        spróbuj:
            dopóki 1:
                y = g.send(x)
                trace.append("Yielded %s" % (y,))
                x += 1
        wyjąwszy StopIteration:
            dalej
        self.assertEqual(trace,[
            "Starting g1",
            "g1 received 1",
            "Starting g2",
            "Yielded g2 spam",
            "g2 received 2",
            "Yielded g2 more spam",
            "g2 received 3",
            "Finishing g2",
            "Yielded g1 eggs",
            "g1 received 4",
            "Finishing g1",
        ])

    def test_handling_exception_while_delegating_send(self):
        """
        Test handling exception dopóki delegating 'send'
        """
        trace = []
        def g1():
            trace.append("Starting g1")
            x = uzyskaj "g1 ham"
            trace.append("g1 received %s" % (x,))
            uzyskaj z g2()
            x = uzyskaj "g1 eggs"
            trace.append("g1 received %s" % (x,))
            trace.append("Finishing g1")
        def g2():
            trace.append("Starting g2")
            x = uzyskaj "g2 spam"
            trace.append("g2 received %s" % (x,))
            podnieś ValueError("hovercraft jest full of eels")
            x = uzyskaj "g2 more spam"
            trace.append("g2 received %s" % (x,))
            trace.append("Finishing g2")
        def run():
            g = g1()
            y = next(g)
            x = 1
            spróbuj:
                dopóki 1:
                    y = g.send(x)
                    trace.append("Yielded %s" % (y,))
                    x += 1
            wyjąwszy StopIteration:
                trace.append("StopIteration")
        self.assertRaises(ValueError,run)
        self.assertEqual(trace,[
            "Starting g1",
            "g1 received 1",
            "Starting g2",
            "Yielded g2 spam",
            "g2 received 2",
        ])

    def test_delegating_close(self):
        """
        Test delegating 'close'
        """
        trace = []
        def g1():
            spróbuj:
                trace.append("Starting g1")
                uzyskaj "g1 ham"
                uzyskaj z g2()
                uzyskaj "g1 eggs"
            w_końcu:
                trace.append("Finishing g1")
        def g2():
            spróbuj:
                trace.append("Starting g2")
                uzyskaj "g2 spam"
                uzyskaj "g2 more spam"
            w_końcu:
                trace.append("Finishing g2")
        g = g1()
        dla i w range(2):
            x = next(g)
            trace.append("Yielded %s" % (x,))
        g.close()
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Finishing g2",
            "Finishing g1"
        ])

    def test_handing_exception_while_delegating_close(self):
        """
        Test handling exception dopóki delegating 'close'
        """
        trace = []
        def g1():
            spróbuj:
                trace.append("Starting g1")
                uzyskaj "g1 ham"
                uzyskaj z g2()
                uzyskaj "g1 eggs"
            w_końcu:
                trace.append("Finishing g1")
        def g2():
            spróbuj:
                trace.append("Starting g2")
                uzyskaj "g2 spam"
                uzyskaj "g2 more spam"
            w_końcu:
                trace.append("Finishing g2")
                podnieś ValueError("nybbles have exploded przy delight")
        spróbuj:
            g = g1()
            dla i w range(2):
                x = next(g)
                trace.append("Yielded %s" % (x,))
            g.close()
        wyjąwszy ValueError jako e:
            self.assertEqual(e.args[0], "nybbles have exploded przy delight")
            self.assertIsInstance(e.__context__, GeneratorExit)
        inaczej:
            self.fail("subgenerator failed to podnieś ValueError")
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Finishing g2",
            "Finishing g1",
        ])

    def test_delegating_throw(self):
        """
        Test delegating 'throw'
        """
        trace = []
        def g1():
            spróbuj:
                trace.append("Starting g1")
                uzyskaj "g1 ham"
                uzyskaj z g2()
                uzyskaj "g1 eggs"
            w_końcu:
                trace.append("Finishing g1")
        def g2():
            spróbuj:
                trace.append("Starting g2")
                uzyskaj "g2 spam"
                uzyskaj "g2 more spam"
            w_końcu:
                trace.append("Finishing g2")
        spróbuj:
            g = g1()
            dla i w range(2):
                x = next(g)
                trace.append("Yielded %s" % (x,))
            e = ValueError("tomato ejected")
            g.throw(e)
        wyjąwszy ValueError jako e:
            self.assertEqual(e.args[0], "tomato ejected")
        inaczej:
            self.fail("subgenerator failed to podnieś ValueError")
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Finishing g2",
            "Finishing g1",
        ])

    def test_value_attribute_of_StopIteration_exception(self):
        """
        Test 'value' attribute of StopIteration exception
        """
        trace = []
        def pex(e):
            trace.append("%s: %s" % (e.__class__.__name__, e))
            trace.append("value = %s" % (e.value,))
        e = StopIteration()
        pex(e)
        e = StopIteration("spam")
        pex(e)
        e.value = "eggs"
        pex(e)
        self.assertEqual(trace,[
            "StopIteration: ",
            "value = Nic",
            "StopIteration: spam",
            "value = spam",
            "StopIteration: spam",
            "value = eggs",
        ])


    def test_exception_value_crash(self):
        # There used to be a refcount error when the zwróć value
        # stored w the StopIteration has a refcount of 1.
        def g1():
            uzyskaj z g2()
        def g2():
            uzyskaj "g2"
            zwróć [42]
        self.assertEqual(list(g1()), ["g2"])


    def test_generator_return_value(self):
        """
        Test generator zwróć value
        """
        trace = []
        def g1():
            trace.append("Starting g1")
            uzyskaj "g1 ham"
            ret = uzyskaj z g2()
            trace.append("g2 returned %s" % (ret,))
            ret = uzyskaj z g2(42)
            trace.append("g2 returned %s" % (ret,))
            uzyskaj "g1 eggs"
            trace.append("Finishing g1")
        def g2(v = Nic):
            trace.append("Starting g2")
            uzyskaj "g2 spam"
            uzyskaj "g2 more spam"
            trace.append("Finishing g2")
            jeżeli v:
                zwróć v
        dla x w g1():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Yielded g2 more spam",
            "Finishing g2",
            "g2 returned Nic",
            "Starting g2",
            "Yielded g2 spam",
            "Yielded g2 more spam",
            "Finishing g2",
            "g2 returned 42",
            "Yielded g1 eggs",
            "Finishing g1",
        ])

    def test_delegation_of_next_to_non_generator(self):
        """
        Test delegation of next() to non-generator
        """
        trace = []
        def g():
            uzyskaj z range(3)
        dla x w g():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Yielded 0",
            "Yielded 1",
            "Yielded 2",
        ])


    def test_conversion_of_sendNic_to_next(self):
        """
        Test conversion of send(Nic) to next()
        """
        trace = []
        def g():
            uzyskaj z range(3)
        gi = g()
        dla x w range(3):
            y = gi.send(Nic)
            trace.append("Yielded: %s" % (y,))
        self.assertEqual(trace,[
            "Yielded: 0",
            "Yielded: 1",
            "Yielded: 2",
        ])

    def test_delegation_of_close_to_non_generator(self):
        """
        Test delegation of close() to non-generator
        """
        trace = []
        def g():
            spróbuj:
                trace.append("starting g")
                uzyskaj z range(3)
                trace.append("g should nie be here")
            w_końcu:
                trace.append("finishing g")
        gi = g()
        next(gi)
        przy captured_stderr() jako output:
            gi.close()
        self.assertEqual(output.getvalue(), '')
        self.assertEqual(trace,[
            "starting g",
            "finishing g",
        ])

    def test_delegating_throw_to_non_generator(self):
        """
        Test delegating 'throw' to non-generator
        """
        trace = []
        def g():
            spróbuj:
                trace.append("Starting g")
                uzyskaj z range(10)
            w_końcu:
                trace.append("Finishing g")
        spróbuj:
            gi = g()
            dla i w range(5):
                x = next(gi)
                trace.append("Yielded %s" % (x,))
            e = ValueError("tomato ejected")
            gi.throw(e)
        wyjąwszy ValueError jako e:
            self.assertEqual(e.args[0],"tomato ejected")
        inaczej:
            self.fail("subgenerator failed to podnieś ValueError")
        self.assertEqual(trace,[
            "Starting g",
            "Yielded 0",
            "Yielded 1",
            "Yielded 2",
            "Yielded 3",
            "Yielded 4",
            "Finishing g",
        ])

    def test_attempting_to_send_to_non_generator(self):
        """
        Test attempting to send to non-generator
        """
        trace = []
        def g():
            spróbuj:
                trace.append("starting g")
                uzyskaj z range(3)
                trace.append("g should nie be here")
            w_końcu:
                trace.append("finishing g")
        spróbuj:
            gi = g()
            next(gi)
            dla x w range(3):
                y = gi.send(42)
                trace.append("Should nie have uzyskajed: %s" % (y,))
        wyjąwszy AttributeError jako e:
            self.assertIn("send", e.args[0])
        inaczej:
            self.fail("was able to send into non-generator")
        self.assertEqual(trace,[
            "starting g",
            "finishing g",
        ])

    def test_broken_getattr_handling(self):
        """
        Test subiterator przy a broken getattr implementation
        """
        klasa Broken:
            def __iter__(self):
                zwróć self
            def __next__(self):
                zwróć 1
            def __getattr__(self, attr):
                1/0

        def g():
            uzyskaj z Broken()

        przy self.assertRaises(ZeroDivisionError):
            gi = g()
            self.assertEqual(next(gi), 1)
            gi.send(1)

        przy self.assertRaises(ZeroDivisionError):
            gi = g()
            self.assertEqual(next(gi), 1)
            gi.throw(AttributeError)

        przy captured_stderr() jako output:
            gi = g()
            self.assertEqual(next(gi), 1)
            gi.close()
        self.assertIn('ZeroDivisionError', output.getvalue())

    def test_exception_in_initial_next_call(self):
        """
        Test exception w initial next() call
        """
        trace = []
        def g1():
            trace.append("g1 about to uzyskaj z g2")
            uzyskaj z g2()
            trace.append("g1 should nie be here")
        def g2():
            uzyskaj 1/0
        def run():
            gi = g1()
            next(gi)
        self.assertRaises(ZeroDivisionError,run)
        self.assertEqual(trace,[
            "g1 about to uzyskaj z g2"
        ])

    def test_attempted_uzyskaj_from_loop(self):
        """
        Test attempted uzyskaj-z loop
        """
        trace = []
        def g1():
            trace.append("g1: starting")
            uzyskaj "y1"
            trace.append("g1: about to uzyskaj z g2")
            uzyskaj z g2()
            trace.append("g1 should nie be here")

        def g2():
            trace.append("g2: starting")
            uzyskaj "y2"
            trace.append("g2: about to uzyskaj z g1")
            uzyskaj z gi
            trace.append("g2 should nie be here")
        spróbuj:
            gi = g1()
            dla y w gi:
                trace.append("Yielded: %s" % (y,))
        wyjąwszy ValueError jako e:
            self.assertEqual(e.args[0],"generator already executing")
        inaczej:
            self.fail("subgenerator didn't podnieś ValueError")
        self.assertEqual(trace,[
            "g1: starting",
            "Yielded: y1",
            "g1: about to uzyskaj z g2",
            "g2: starting",
            "Yielded: y2",
            "g2: about to uzyskaj z g1",
        ])

    def test_returning_value_from_delegated_throw(self):
        """
        Test returning value z delegated 'throw'
        """
        trace = []
        def g1():
            spróbuj:
                trace.append("Starting g1")
                uzyskaj "g1 ham"
                uzyskaj z g2()
                uzyskaj "g1 eggs"
            w_końcu:
                trace.append("Finishing g1")
        def g2():
            spróbuj:
                trace.append("Starting g2")
                uzyskaj "g2 spam"
                uzyskaj "g2 more spam"
            wyjąwszy LunchError:
                trace.append("Caught LunchError w g2")
                uzyskaj "g2 lunch saved"
                uzyskaj "g2 yet more spam"
        klasa LunchError(Exception):
            dalej
        g = g1()
        dla i w range(2):
            x = next(g)
            trace.append("Yielded %s" % (x,))
        e = LunchError("tomato ejected")
        g.throw(e)
        dla x w g:
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Caught LunchError w g2",
            "Yielded g2 yet more spam",
            "Yielded g1 eggs",
            "Finishing g1",
        ])

    def test_next_and_return_with_value(self):
        """
        Test next oraz zwróć przy value
        """
        trace = []
        def f(r):
            gi = g(r)
            next(gi)
            spróbuj:
                trace.append("f resuming g")
                next(gi)
                trace.append("f SHOULD NOT BE HERE")
            wyjąwszy StopIteration jako e:
                trace.append("f caught %s" % (repr(e),))
        def g(r):
            trace.append("g starting")
            uzyskaj
            trace.append("g returning %s" % (r,))
            zwróć r
        f(Nic)
        f(42)
        self.assertEqual(trace,[
            "g starting",
            "f resuming g",
            "g returning Nic",
            "f caught StopIteration()",
            "g starting",
            "f resuming g",
            "g returning 42",
            "f caught StopIteration(42,)",
        ])

    def test_send_and_return_with_value(self):
        """
        Test send oraz zwróć przy value
        """
        trace = []
        def f(r):
            gi = g(r)
            next(gi)
            spróbuj:
                trace.append("f sending spam to g")
                gi.send("spam")
                trace.append("f SHOULD NOT BE HERE")
            wyjąwszy StopIteration jako e:
                trace.append("f caught %r" % (e,))
        def g(r):
            trace.append("g starting")
            x = uzyskaj
            trace.append("g received %s" % (x,))
            trace.append("g returning %s" % (r,))
            zwróć r
        f(Nic)
        f(42)
        self.assertEqual(trace,[
            "g starting",
            "f sending spam to g",
            "g received spam",
            "g returning Nic",
            "f caught StopIteration()",
            "g starting",
            "f sending spam to g",
            "g received spam",
            "g returning 42",
            "f caught StopIteration(42,)",
        ])

    def test_catching_exception_from_subgen_and_returning(self):
        """
        Test catching an exception thrown into a
        subgenerator oraz returning a value
        """
        trace = []
        def inner():
            spróbuj:
                uzyskaj 1
            wyjąwszy ValueError:
                trace.append("inner caught ValueError")
            zwróć 2

        def outer():
            v = uzyskaj z inner()
            trace.append("inner returned %r to outer" % v)
            uzyskaj v
        g = outer()
        trace.append(next(g))
        trace.append(g.throw(ValueError))
        self.assertEqual(trace,[
            1,
            "inner caught ValueError",
            "inner returned 2 to outer",
            2,
        ])

    def test_throwing_GeneratorExit_into_subgen_that_returns(self):
        """
        Test throwing GeneratorExit into a subgenerator that
        catches it oraz returns normally.
        """
        trace = []
        def f():
            spróbuj:
                trace.append("Enter f")
                uzyskaj
                trace.append("Exit f")
            wyjąwszy GeneratorExit:
                zwróć
        def g():
            trace.append("Enter g")
            uzyskaj z f()
            trace.append("Exit g")
        spróbuj:
            gi = g()
            next(gi)
            gi.throw(GeneratorExit)
        wyjąwszy GeneratorExit:
            dalej
        inaczej:
            self.fail("subgenerator failed to podnieś GeneratorExit")
        self.assertEqual(trace,[
            "Enter g",
            "Enter f",
        ])

    def test_throwing_GeneratorExit_into_subgenerator_that_uzyskajs(self):
        """
        Test throwing GeneratorExit into a subgenerator that
        catches it oraz uzyskajs.
        """
        trace = []
        def f():
            spróbuj:
                trace.append("Enter f")
                uzyskaj
                trace.append("Exit f")
            wyjąwszy GeneratorExit:
                uzyskaj
        def g():
            trace.append("Enter g")
            uzyskaj z f()
            trace.append("Exit g")
        spróbuj:
            gi = g()
            next(gi)
            gi.throw(GeneratorExit)
        wyjąwszy RuntimeError jako e:
            self.assertEqual(e.args[0], "generator ignored GeneratorExit")
        inaczej:
            self.fail("subgenerator failed to podnieś GeneratorExit")
        self.assertEqual(trace,[
            "Enter g",
            "Enter f",
        ])

    def test_throwing_GeneratorExit_into_subgen_that_raises(self):
        """
        Test throwing GeneratorExit into a subgenerator that
        catches it oraz podnieśs a different exception.
        """
        trace = []
        def f():
            spróbuj:
                trace.append("Enter f")
                uzyskaj
                trace.append("Exit f")
            wyjąwszy GeneratorExit:
                podnieś ValueError("Vorpal bunny encountered")
        def g():
            trace.append("Enter g")
            uzyskaj z f()
            trace.append("Exit g")
        spróbuj:
            gi = g()
            next(gi)
            gi.throw(GeneratorExit)
        wyjąwszy ValueError jako e:
            self.assertEqual(e.args[0], "Vorpal bunny encountered")
            self.assertIsInstance(e.__context__, GeneratorExit)
        inaczej:
            self.fail("subgenerator failed to podnieś ValueError")
        self.assertEqual(trace,[
            "Enter g",
            "Enter f",
        ])

    def test_uzyskaj_from_empty(self):
        def g():
            uzyskaj z ()
        self.assertRaises(StopIteration, next, g())

    def test_delegating_generators_claim_to_be_running(self):
        # Check przy basic iteration
        def one():
            uzyskaj 0
            uzyskaj z two()
            uzyskaj 3
        def two():
            uzyskaj 1
            spróbuj:
                uzyskaj z g1
            wyjąwszy ValueError:
                dalej
            uzyskaj 2
        g1 = one()
        self.assertEqual(list(g1), [0, 1, 2, 3])
        # Check przy send
        g1 = one()
        res = [next(g1)]
        spróbuj:
            dopóki Prawda:
                res.append(g1.send(42))
        wyjąwszy StopIteration:
            dalej
        self.assertEqual(res, [0, 1, 2, 3])
        # Check przy throw
        klasa MyErr(Exception):
            dalej
        def one():
            spróbuj:
                uzyskaj 0
            wyjąwszy MyErr:
                dalej
            uzyskaj z two()
            spróbuj:
                uzyskaj 3
            wyjąwszy MyErr:
                dalej
        def two():
            spróbuj:
                uzyskaj 1
            wyjąwszy MyErr:
                dalej
            spróbuj:
                uzyskaj z g1
            wyjąwszy ValueError:
                dalej
            spróbuj:
                uzyskaj 2
            wyjąwszy MyErr:
                dalej
        g1 = one()
        res = [next(g1)]
        spróbuj:
            dopóki Prawda:
                res.append(g1.throw(MyErr))
        wyjąwszy StopIteration:
            dalej
        # Check przy close
        klasa MyIt(object):
            def __iter__(self):
                zwróć self
            def __next__(self):
                zwróć 42
            def close(self_):
                self.assertPrawda(g1.gi_running)
                self.assertRaises(ValueError, next, g1)
        def one():
            uzyskaj z MyIt()
        g1 = one()
        next(g1)
        g1.close()

    def test_delegator_is_visible_to_debugger(self):
        def call_stack():
            zwróć [f[3] dla f w inspect.stack()]

        def gen():
            uzyskaj call_stack()
            uzyskaj call_stack()
            uzyskaj call_stack()

        def spam(g):
            uzyskaj z g

        def eggs(g):
            uzyskaj z g

        dla stack w spam(gen()):
            self.assertPrawda('spam' w stack)

        dla stack w spam(eggs(gen())):
            self.assertPrawda('spam' w stack oraz 'eggs' w stack)

    def test_custom_iterator_return(self):
        # See issue #15568
        klasa MyIter:
            def __iter__(self):
                zwróć self
            def __next__(self):
                podnieś StopIteration(42)
        def gen():
            nonlocal ret
            ret = uzyskaj z MyIter()
        ret = Nic
        list(gen())
        self.assertEqual(ret, 42)

    def test_close_with_cleared_frame(self):
        # See issue #17669.
        #
        # Create a stack of generators: outer() delegating to inner()
        # delegating to innermost(). The key point jest that the instance of
        # inner jest created first: this ensures that its frame appears before
        # the instance of outer w the GC linked list.
        #
        # At the gc.collect call:
        #   - frame_clear jest called on the inner_gen frame.
        #   - gen_dealloc jest called on the outer_gen generator (the only
        #     reference jest w the frame's locals).
        #   - gen_close jest called on the outer_gen generator.
        #   - gen_close_iter jest called to close the inner_gen generator, which
        #     w turn calls gen_close, oraz gen_yf.
        #
        # Previously, gen_yf would crash since inner_gen's frame had been
        # cleared (and w particular f_stacktop was NULL).

        def innermost():
            uzyskaj
        def inner():
            outer_gen = uzyskaj
            uzyskaj z innermost()
        def outer():
            inner_gen = uzyskaj
            uzyskaj z inner_gen

        przy disable_gc():
            inner_gen = inner()
            outer_gen = outer()
            outer_gen.send(Nic)
            outer_gen.send(inner_gen)
            outer_gen.send(outer_gen)

            usuń outer_gen
            usuń inner_gen
            gc_collect()

    def test_send_tuple_with_custom_generator(self):
        # See issue #21209.
        klasa MyGen:
            def __iter__(self):
                zwróć self
            def __next__(self):
                zwróć 42
            def send(self, what):
                nonlocal v
                v = what
                zwróć Nic
        def outer():
            v = uzyskaj z MyGen()
        g = outer()
        next(g)
        v = Nic
        g.send((1, 2, 3, 4))
        self.assertEqual(v, (1, 2, 3, 4))


jeżeli __name__ == '__main__':
    unittest.main()
