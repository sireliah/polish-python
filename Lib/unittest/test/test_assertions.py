zaimportuj datetime
zaimportuj warnings
zaimportuj weakref
zaimportuj unittest
z itertools zaimportuj product


klasa Test_Assertions(unittest.TestCase):
    def test_AlmostEqual(self):
        self.assertAlmostEqual(1.00000001, 1.0)
        self.assertNotAlmostEqual(1.0000001, 1.0)
        self.assertRaises(self.failureException,
                          self.assertAlmostEqual, 1.0000001, 1.0)
        self.assertRaises(self.failureException,
                          self.assertNotAlmostEqual, 1.00000001, 1.0)

        self.assertAlmostEqual(1.1, 1.0, places=0)
        self.assertRaises(self.failureException,
                          self.assertAlmostEqual, 1.1, 1.0, places=1)

        self.assertAlmostEqual(0, .1+.1j, places=0)
        self.assertNotAlmostEqual(0, .1+.1j, places=1)
        self.assertRaises(self.failureException,
                          self.assertAlmostEqual, 0, .1+.1j, places=1)
        self.assertRaises(self.failureException,
                          self.assertNotAlmostEqual, 0, .1+.1j, places=0)

        self.assertAlmostEqual(float('inf'), float('inf'))
        self.assertRaises(self.failureException, self.assertNotAlmostEqual,
                          float('inf'), float('inf'))

    def test_AmostEqualWithDelta(self):
        self.assertAlmostEqual(1.1, 1.0, delta=0.5)
        self.assertAlmostEqual(1.0, 1.1, delta=0.5)
        self.assertNotAlmostEqual(1.1, 1.0, delta=0.05)
        self.assertNotAlmostEqual(1.0, 1.1, delta=0.05)

        self.assertAlmostEqual(1.0, 1.0, delta=0.5)
        self.assertRaises(self.failureException, self.assertNotAlmostEqual,
                          1.0, 1.0, delta=0.5)

        self.assertRaises(self.failureException, self.assertAlmostEqual,
                          1.1, 1.0, delta=0.05)
        self.assertRaises(self.failureException, self.assertNotAlmostEqual,
                          1.1, 1.0, delta=0.5)

        self.assertRaises(TypeError, self.assertAlmostEqual,
                          1.1, 1.0, places=2, delta=2)
        self.assertRaises(TypeError, self.assertNotAlmostEqual,
                          1.1, 1.0, places=2, delta=2)

        first = datetime.datetime.now()
        second = first + datetime.timedelta(seconds=10)
        self.assertAlmostEqual(first, second,
                               delta=datetime.timedelta(seconds=20))
        self.assertNotAlmostEqual(first, second,
                                  delta=datetime.timedelta(seconds=5))

    def test_assertRaises(self):
        def _raise(e):
            podnieś e
        self.assertRaises(KeyError, _raise, KeyError)
        self.assertRaises(KeyError, _raise, KeyError("key"))
        spróbuj:
            self.assertRaises(KeyError, lambda: Nic)
        wyjąwszy self.failureException jako e:
            self.assertIn("KeyError nie podnieśd", str(e))
        inaczej:
            self.fail("assertRaises() didn't fail")
        spróbuj:
            self.assertRaises(KeyError, _raise, ValueError)
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("assertRaises() didn't let exception dalej through")
        przy self.assertRaises(KeyError) jako cm:
            spróbuj:
                podnieś KeyError
            wyjąwszy Exception jako e:
                exc = e
                podnieś
        self.assertIs(cm.exception, exc)

        przy self.assertRaises(KeyError):
            podnieś KeyError("key")
        spróbuj:
            przy self.assertRaises(KeyError):
                dalej
        wyjąwszy self.failureException jako e:
            self.assertIn("KeyError nie podnieśd", str(e))
        inaczej:
            self.fail("assertRaises() didn't fail")
        spróbuj:
            przy self.assertRaises(KeyError):
                podnieś ValueError
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("assertRaises() didn't let exception dalej through")

    def test_assertRaises_frames_survival(self):
        # Issue #9815: assertRaises should avoid keeping local variables
        # w a traceback alive.
        klasa A:
            dalej
        wr = Nic

        klasa Foo(unittest.TestCase):

            def foo(self):
                nonlocal wr
                a = A()
                wr = weakref.ref(a)
                spróbuj:
                    podnieś IOError
                wyjąwszy IOError:
                    podnieś ValueError

            def test_functional(self):
                self.assertRaises(ValueError, self.foo)

            def test_with(self):
                przy self.assertRaises(ValueError):
                    self.foo()

        Foo("test_functional").run()
        self.assertIsNic(wr())
        Foo("test_with").run()
        self.assertIsNic(wr())

    def testAssertNotRegex(self):
        self.assertNotRegex('Ala ma kota', r'r+')
        spróbuj:
            self.assertNotRegex('Ala ma kota', r'k.t', 'Message')
        wyjąwszy self.failureException jako e:
            self.assertIn("'kot'", e.args[0])
            self.assertIn('Message', e.args[0])
        inaczej:
            self.fail('assertNotRegex should have failed.')


klasa TestLongMessage(unittest.TestCase):
    """Test that the individual asserts honour longMessage.
    This actually tests all the message behaviour for
    asserts that use longMessage."""

    def setUp(self):
        klasa TestableTestNieprawda(unittest.TestCase):
            longMessage = Nieprawda
            failureException = self.failureException

            def testTest(self):
                dalej

        klasa TestableTestPrawda(unittest.TestCase):
            longMessage = Prawda
            failureException = self.failureException

            def testTest(self):
                dalej

        self.testablePrawda = TestableTestPrawda('testTest')
        self.testableNieprawda = TestableTestNieprawda('testTest')

    def testDefault(self):
        self.assertPrawda(unittest.TestCase.longMessage)

    def test_formatMsg(self):
        self.assertEqual(self.testableNieprawda._formatMessage(Nic, "foo"), "foo")
        self.assertEqual(self.testableNieprawda._formatMessage("foo", "bar"), "foo")

        self.assertEqual(self.testablePrawda._formatMessage(Nic, "foo"), "foo")
        self.assertEqual(self.testablePrawda._formatMessage("foo", "bar"), "bar : foo")

        # This blows up jeżeli _formatMessage uses string concatenation
        self.testablePrawda._formatMessage(object(), 'foo')

    def test_formatMessage_unicode_error(self):
        one = ''.join(chr(i) dla i w range(255))
        # this used to cause a UnicodeDecodeError constructing msg
        self.testablePrawda._formatMessage(one, '\uFFFD')

    def assertMessages(self, methodName, args, errors):
        """
        Check that methodName(*args) podnieśs the correct error messages.
        errors should be a list of 4 regex that match the error when:
          1) longMessage = Nieprawda oraz no msg dalejed;
          2) longMessage = Nieprawda oraz msg dalejed;
          3) longMessage = Prawda oraz no msg dalejed;
          4) longMessage = Prawda oraz msg dalejed;
        """
        def getMethod(i):
            useTestableNieprawda  = i < 2
            jeżeli useTestableNieprawda:
                test = self.testableNieprawda
            inaczej:
                test = self.testablePrawda
            zwróć getattr(test, methodName)

        dla i, expected_regex w enumerate(errors):
            testMethod = getMethod(i)
            kwargs = {}
            withMsg = i % 2
            jeżeli withMsg:
                kwargs = {"msg": "oops"}

            przy self.assertRaisesRegex(self.failureException,
                                        expected_regex=expected_regex):
                testMethod(*args, **kwargs)

    def testAssertPrawda(self):
        self.assertMessages('assertPrawda', (Nieprawda,),
                            ["^Nieprawda jest nie true$", "^oops$", "^Nieprawda jest nie true$",
                             "^Nieprawda jest nie true : oops$"])

    def testAssertNieprawda(self):
        self.assertMessages('assertNieprawda', (Prawda,),
                            ["^Prawda jest nie false$", "^oops$", "^Prawda jest nie false$",
                             "^Prawda jest nie false : oops$"])

    def testNotEqual(self):
        self.assertMessages('assertNotEqual', (1, 1),
                            ["^1 == 1$", "^oops$", "^1 == 1$",
                             "^1 == 1 : oops$"])

    def testAlmostEqual(self):
        self.assertMessages('assertAlmostEqual', (1, 2),
                            ["^1 != 2 within 7 places$", "^oops$",
                             "^1 != 2 within 7 places$", "^1 != 2 within 7 places : oops$"])

    def testNotAlmostEqual(self):
        self.assertMessages('assertNotAlmostEqual', (1, 1),
                            ["^1 == 1 within 7 places$", "^oops$",
                             "^1 == 1 within 7 places$", "^1 == 1 within 7 places : oops$"])

    def test_baseAssertEqual(self):
        self.assertMessages('_baseAssertEqual', (1, 2),
                            ["^1 != 2$", "^oops$", "^1 != 2$", "^1 != 2 : oops$"])

    def testAssertSequenceEqual(self):
        # Error messages are multiline so nie testing on full message
        # assertTupleEqual oraz assertListEqual delegate to this method
        self.assertMessages('assertSequenceEqual', ([], [Nic]),
                            ["\+ \[Nic\]$", "^oops$", r"\+ \[Nic\]$",
                             r"\+ \[Nic\] : oops$"])

    def testAssertSetEqual(self):
        self.assertMessages('assertSetEqual', (set(), set([Nic])),
                            ["Nic$", "^oops$", "Nic$",
                             "Nic : oops$"])

    def testAssertIn(self):
        self.assertMessages('assertIn', (Nic, []),
                            ['^Nic nie found w \[\]$', "^oops$",
                             '^Nic nie found w \[\]$',
                             '^Nic nie found w \[\] : oops$'])

    def testAssertNotIn(self):
        self.assertMessages('assertNotIn', (Nic, [Nic]),
                            ['^Nic unexpectedly found w \[Nic\]$', "^oops$",
                             '^Nic unexpectedly found w \[Nic\]$',
                             '^Nic unexpectedly found w \[Nic\] : oops$'])

    def testAssertDictEqual(self):
        self.assertMessages('assertDictEqual', ({}, {'key': 'value'}),
                            [r"\+ \{'key': 'value'\}$", "^oops$",
                             "\+ \{'key': 'value'\}$",
                             "\+ \{'key': 'value'\} : oops$"])

    def testAssertDictContainsSubset(self):
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)

            self.assertMessages('assertDictContainsSubset', ({'key': 'value'}, {}),
                                ["^Missing: 'key'$", "^oops$",
                                 "^Missing: 'key'$",
                                 "^Missing: 'key' : oops$"])

    def testAssertMultiLineEqual(self):
        self.assertMessages('assertMultiLineEqual', ("", "foo"),
                            [r"\+ foo$", "^oops$",
                             r"\+ foo$",
                             r"\+ foo : oops$"])

    def testAssertLess(self):
        self.assertMessages('assertLess', (2, 1),
                            ["^2 nie less than 1$", "^oops$",
                             "^2 nie less than 1$", "^2 nie less than 1 : oops$"])

    def testAssertLessEqual(self):
        self.assertMessages('assertLessEqual', (2, 1),
                            ["^2 nie less than albo equal to 1$", "^oops$",
                             "^2 nie less than albo equal to 1$",
                             "^2 nie less than albo equal to 1 : oops$"])

    def testAssertGreater(self):
        self.assertMessages('assertGreater', (1, 2),
                            ["^1 nie greater than 2$", "^oops$",
                             "^1 nie greater than 2$",
                             "^1 nie greater than 2 : oops$"])

    def testAssertGreaterEqual(self):
        self.assertMessages('assertGreaterEqual', (1, 2),
                            ["^1 nie greater than albo equal to 2$", "^oops$",
                             "^1 nie greater than albo equal to 2$",
                             "^1 nie greater than albo equal to 2 : oops$"])

    def testAssertIsNic(self):
        self.assertMessages('assertIsNic', ('not Nic',),
                            ["^'not Nic' jest nie Nic$", "^oops$",
                             "^'not Nic' jest nie Nic$",
                             "^'not Nic' jest nie Nic : oops$"])

    def testAssertIsNotNic(self):
        self.assertMessages('assertIsNotNic', (Nic,),
                            ["^unexpectedly Nic$", "^oops$",
                             "^unexpectedly Nic$",
                             "^unexpectedly Nic : oops$"])

    def testAssertIs(self):
        self.assertMessages('assertIs', (Nic, 'foo'),
                            ["^Nic jest nie 'foo'$", "^oops$",
                             "^Nic jest nie 'foo'$",
                             "^Nic jest nie 'foo' : oops$"])

    def testAssertIsNot(self):
        self.assertMessages('assertIsNot', (Nic, Nic),
                            ["^unexpectedly identical: Nic$", "^oops$",
                             "^unexpectedly identical: Nic$",
                             "^unexpectedly identical: Nic : oops$"])


    def assertMessagesCM(self, methodName, args, func, errors):
        """
        Check that the correct error messages are podnieśd dopóki executing:
          przy method(*args):
              func()
        *errors* should be a list of 4 regex that match the error when:
          1) longMessage = Nieprawda oraz no msg dalejed;
          2) longMessage = Nieprawda oraz msg dalejed;
          3) longMessage = Prawda oraz no msg dalejed;
          4) longMessage = Prawda oraz msg dalejed;
        """
        p = product((self.testableNieprawda, self.testablePrawda),
                    ({}, {"msg": "oops"}))
        dla (cls, kwargs), err w zip(p, errors):
            method = getattr(cls, methodName)
            przy self.assertRaisesRegex(cls.failureException, err):
                przy method(*args, **kwargs) jako cm:
                    func()

    def testAssertRaises(self):
        self.assertMessagesCM('assertRaises', (TypeError,), lambda: Nic,
                              ['^TypeError nie podnieśd$', '^oops$',
                               '^TypeError nie podnieśd$',
                               '^TypeError nie podnieśd : oops$'])

    def testAssertRaisesRegex(self):
        # test error nie podnieśd
        self.assertMessagesCM('assertRaisesRegex', (TypeError, 'unused regex'),
                              lambda: Nic,
                              ['^TypeError nie podnieśd$', '^oops$',
                               '^TypeError nie podnieśd$',
                               '^TypeError nie podnieśd : oops$'])
        # test error podnieśd but przy wrong message
        def podnieś_wrong_message():
            podnieś TypeError('foo')
        self.assertMessagesCM('assertRaisesRegex', (TypeError, 'regex'),
                              podnieś_wrong_message,
                              ['^"regex" does nie match "foo"$', '^oops$',
                               '^"regex" does nie match "foo"$',
                               '^"regex" does nie match "foo" : oops$'])

    def testAssertWarns(self):
        self.assertMessagesCM('assertWarns', (UserWarning,), lambda: Nic,
                              ['^UserWarning nie triggered$', '^oops$',
                               '^UserWarning nie triggered$',
                               '^UserWarning nie triggered : oops$'])

    def testAssertWarnsRegex(self):
        # test error nie podnieśd
        self.assertMessagesCM('assertWarnsRegex', (UserWarning, 'unused regex'),
                              lambda: Nic,
                              ['^UserWarning nie triggered$', '^oops$',
                               '^UserWarning nie triggered$',
                               '^UserWarning nie triggered : oops$'])
        # test warning podnieśd but przy wrong message
        def podnieś_wrong_message():
            warnings.warn('foo')
        self.assertMessagesCM('assertWarnsRegex', (UserWarning, 'regex'),
                              podnieś_wrong_message,
                              ['^"regex" does nie match "foo"$', '^oops$',
                               '^"regex" does nie match "foo"$',
                               '^"regex" does nie match "foo" : oops$'])


jeżeli __name__ == "__main__":
    unittest.main()
