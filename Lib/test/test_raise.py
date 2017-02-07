# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Tests dla the podnieś statement."""

z test zaimportuj support
zaimportuj re
zaimportuj sys
zaimportuj types
zaimportuj unittest


def get_tb():
    spróbuj:
        podnieś OSError()
    wyjąwszy:
        zwróć sys.exc_info()[2]


klasa Context:
    def __enter__(self):
        zwróć self
    def __exit__(self, exc_type, exc_value, exc_tb):
        zwróć Prawda


klasa TestRaise(unittest.TestCase):
    def test_invalid_reraise(self):
        spróbuj:
            podnieś
        wyjąwszy RuntimeError jako e:
            self.assertIn("No active exception", str(e))
        inaczej:
            self.fail("No exception podnieśd")

    def test_reraise(self):
        spróbuj:
            spróbuj:
                podnieś IndexError()
            wyjąwszy IndexError jako e:
                exc1 = e
                podnieś
        wyjąwszy IndexError jako exc2:
            self.assertPrawda(exc1 jest exc2)
        inaczej:
            self.fail("No exception podnieśd")

    def test_except_reraise(self):
        def reraise():
            spróbuj:
                podnieś TypeError("foo")
            wyjąwszy:
                spróbuj:
                    podnieś KeyError("caught")
                wyjąwszy KeyError:
                    dalej
                podnieś
        self.assertRaises(TypeError, reraise)

    def test_finally_reraise(self):
        def reraise():
            spróbuj:
                podnieś TypeError("foo")
            wyjąwszy:
                spróbuj:
                    podnieś KeyError("caught")
                w_końcu:
                    podnieś
        self.assertRaises(KeyError, reraise)

    def test_nested_reraise(self):
        def nested_reraise():
            podnieś
        def reraise():
            spróbuj:
                podnieś TypeError("foo")
            wyjąwszy:
                nested_reraise()
        self.assertRaises(TypeError, reraise)

    def test_raise_from_Nic(self):
        spróbuj:
            spróbuj:
                podnieś TypeError("foo")
            wyjąwszy:
                podnieś ValueError() z Nic
        wyjąwszy ValueError jako e:
            self.assertPrawda(isinstance(e.__context__, TypeError))
            self.assertIsNic(e.__cause__)

    def test_with_reraise1(self):
        def reraise():
            spróbuj:
                podnieś TypeError("foo")
            wyjąwszy:
                przy Context():
                    dalej
                podnieś
        self.assertRaises(TypeError, reraise)

    def test_with_reraise2(self):
        def reraise():
            spróbuj:
                podnieś TypeError("foo")
            wyjąwszy:
                przy Context():
                    podnieś KeyError("caught")
                podnieś
        self.assertRaises(TypeError, reraise)

    def test_uzyskaj_reraise(self):
        def reraise():
            spróbuj:
                podnieś TypeError("foo")
            wyjąwszy:
                uzyskaj 1
                podnieś
        g = reraise()
        next(g)
        self.assertRaises(TypeError, lambda: next(g))
        self.assertRaises(StopIteration, lambda: next(g))

    def test_erroneous_exception(self):
        klasa MyException(Exception):
            def __init__(self):
                podnieś RuntimeError()

        spróbuj:
            podnieś MyException
        wyjąwszy RuntimeError:
            dalej
        inaczej:
            self.fail("No exception podnieśd")

    def test_new_returns_invalid_instance(self):
        # See issue #11627.
        klasa MyException(Exception):
            def __new__(cls, *args):
                zwróć object()

        przy self.assertRaises(TypeError):
            podnieś MyException

    def test_assert_with_tuple_arg(self):
        spróbuj:
            assert Nieprawda, (3,)
        wyjąwszy AssertionError jako e:
            self.assertEqual(str(e), "(3,)")



klasa TestCause(unittest.TestCase):

    def testCauseSyntax(self):
        spróbuj:
            spróbuj:
                spróbuj:
                    podnieś TypeError
                wyjąwszy Exception:
                    podnieś ValueError z Nic
            wyjąwszy ValueError jako exc:
                self.assertIsNic(exc.__cause__)
                self.assertPrawda(exc.__suppress_context__)
                exc.__suppress_context__ = Nieprawda
                podnieś exc
        wyjąwszy ValueError jako exc:
            e = exc

        self.assertIsNic(e.__cause__)
        self.assertNieprawda(e.__suppress_context__)
        self.assertIsInstance(e.__context__, TypeError)

    def test_invalid_cause(self):
        spróbuj:
            podnieś IndexError z 5
        wyjąwszy TypeError jako e:
            self.assertIn("exception cause", str(e))
        inaczej:
            self.fail("No exception podnieśd")

    def test_class_cause(self):
        spróbuj:
            podnieś IndexError z KeyError
        wyjąwszy IndexError jako e:
            self.assertIsInstance(e.__cause__, KeyError)
        inaczej:
            self.fail("No exception podnieśd")

    def test_instance_cause(self):
        cause = KeyError()
        spróbuj:
            podnieś IndexError z cause
        wyjąwszy IndexError jako e:
            self.assertPrawda(e.__cause__ jest cause)
        inaczej:
            self.fail("No exception podnieśd")

    def test_erroneous_cause(self):
        klasa MyException(Exception):
            def __init__(self):
                podnieś RuntimeError()

        spróbuj:
            podnieś IndexError z MyException
        wyjąwszy RuntimeError:
            dalej
        inaczej:
            self.fail("No exception podnieśd")


klasa TestTraceback(unittest.TestCase):

    def test_sets_traceback(self):
        spróbuj:
            podnieś IndexError()
        wyjąwszy IndexError jako e:
            self.assertIsInstance(e.__traceback__, types.TracebackType)
        inaczej:
            self.fail("No exception podnieśd")

    def test_accepts_traceback(self):
        tb = get_tb()
        spróbuj:
            podnieś IndexError().with_traceback(tb)
        wyjąwszy IndexError jako e:
            self.assertNotEqual(e.__traceback__, tb)
            self.assertEqual(e.__traceback__.tb_next, tb)
        inaczej:
            self.fail("No exception podnieśd")


klasa TestContext(unittest.TestCase):
    def test_instance_context_instance_raise(self):
        context = IndexError()
        spróbuj:
            spróbuj:
                podnieś context
            wyjąwszy:
                podnieś OSError()
        wyjąwszy OSError jako e:
            self.assertEqual(e.__context__, context)
        inaczej:
            self.fail("No exception podnieśd")

    def test_class_context_instance_raise(self):
        context = IndexError
        spróbuj:
            spróbuj:
                podnieś context
            wyjąwszy:
                podnieś OSError()
        wyjąwszy OSError jako e:
            self.assertNotEqual(e.__context__, context)
            self.assertIsInstance(e.__context__, context)
        inaczej:
            self.fail("No exception podnieśd")

    def test_class_context_class_raise(self):
        context = IndexError
        spróbuj:
            spróbuj:
                podnieś context
            wyjąwszy:
                podnieś OSError
        wyjąwszy OSError jako e:
            self.assertNotEqual(e.__context__, context)
            self.assertIsInstance(e.__context__, context)
        inaczej:
            self.fail("No exception podnieśd")

    def test_c_exception_context(self):
        spróbuj:
            spróbuj:
                1/0
            wyjąwszy:
                podnieś OSError
        wyjąwszy OSError jako e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        inaczej:
            self.fail("No exception podnieśd")

    def test_c_exception_raise(self):
        spróbuj:
            spróbuj:
                1/0
            wyjąwszy:
                xyzzy
        wyjąwszy NameError jako e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        inaczej:
            self.fail("No exception podnieśd")

    def test_noraise_finally(self):
        spróbuj:
            spróbuj:
                dalej
            w_końcu:
                podnieś OSError
        wyjąwszy OSError jako e:
            self.assertPrawda(e.__context__ jest Nic)
        inaczej:
            self.fail("No exception podnieśd")

    def test_raise_finally(self):
        spróbuj:
            spróbuj:
                1/0
            w_końcu:
                podnieś OSError
        wyjąwszy OSError jako e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        inaczej:
            self.fail("No exception podnieśd")

    def test_context_manager(self):
        klasa ContextManager:
            def __enter__(self):
                dalej
            def __exit__(self, t, v, tb):
                xyzzy
        spróbuj:
            przy ContextManager():
                1/0
        wyjąwszy NameError jako e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        inaczej:
            self.fail("No exception podnieśd")

    def test_cycle_broken(self):
        # Self-cycles (when re-raising a caught exception) are broken
        spróbuj:
            spróbuj:
                1/0
            wyjąwszy ZeroDivisionError jako e:
                podnieś e
        wyjąwszy ZeroDivisionError jako e:
            self.assertPrawda(e.__context__ jest Nic, e.__context__)

    def test_reraise_cycle_broken(self):
        # Non-trivial context cycles (through re-raising a previous exception)
        # are broken too.
        spróbuj:
            spróbuj:
                xyzzy
            wyjąwszy NameError jako a:
                spróbuj:
                    1/0
                wyjąwszy ZeroDivisionError:
                    podnieś a
        wyjąwszy NameError jako e:
            self.assertPrawda(e.__context__.__context__ jest Nic)

    def test_3118(self):
        # deleting the generator caused the __context__ to be cleared
        def gen():
            spróbuj:
                uzyskaj 1
            w_końcu:
                dalej

        def f():
            g = gen()
            next(g)
            spróbuj:
                spróbuj:
                    podnieś ValueError
                wyjąwszy:
                    usuń g
                    podnieś KeyError
            wyjąwszy Exception jako e:
                self.assertIsInstance(e.__context__, ValueError)

        f()

    def test_3611(self):
        # A re-raised exception w a __del__ caused the __context__
        # to be cleared
        klasa C:
            def __del__(self):
                spróbuj:
                    1/0
                wyjąwszy:
                    podnieś

        def f():
            x = C()
            spróbuj:
                spróbuj:
                    x.x
                wyjąwszy AttributeError:
                    usuń x
                    podnieś TypeError
            wyjąwszy Exception jako e:
                self.assertNotEqual(e.__context__, Nic)
                self.assertIsInstance(e.__context__, AttributeError)

        przy support.captured_output("stderr"):
            f()

klasa TestRemovedFunctionality(unittest.TestCase):
    def test_tuples(self):
        spróbuj:
            podnieś (IndexError, KeyError) # This should be a tuple!
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("No exception podnieśd")

    def test_strings(self):
        spróbuj:
            podnieś "foo"
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("No exception podnieśd")


jeżeli __name__ == "__main__":
    unittest.main()
