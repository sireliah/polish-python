# Test various flavors of legal oraz illegal future statements

zaimportuj unittest
z test zaimportuj support
zaimportuj re

rx = re.compile('\((\S+).py, line (\d+)')

def get_error_location(msg):
    mo = rx.search(str(msg))
    zwróć mo.group(1, 2)

klasa FutureTest(unittest.TestCase):

    def test_future1(self):
        przy support.CleanImport('future_test1'):
            z test zaimportuj future_test1
            self.assertEqual(future_test1.result, 6)

    def test_future2(self):
        przy support.CleanImport('future_test2'):
            z test zaimportuj future_test2
            self.assertEqual(future_test2.result, 6)

    def test_future3(self):
        przy support.CleanImport('test_future3'):
            z test zaimportuj test_future3

    def test_badfuture3(self):
        spróbuj:
            z test zaimportuj badsyntax_future3
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(get_error_location(msg), ("badsyntax_future3", '3'))
        inaczej:
            self.fail("expected exception didn't occur")

    def test_badfuture4(self):
        spróbuj:
            z test zaimportuj badsyntax_future4
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(get_error_location(msg), ("badsyntax_future4", '3'))
        inaczej:
            self.fail("expected exception didn't occur")

    def test_badfuture5(self):
        spróbuj:
            z test zaimportuj badsyntax_future5
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(get_error_location(msg), ("badsyntax_future5", '4'))
        inaczej:
            self.fail("expected exception didn't occur")

    def test_badfuture6(self):
        spróbuj:
            z test zaimportuj badsyntax_future6
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(get_error_location(msg), ("badsyntax_future6", '3'))
        inaczej:
            self.fail("expected exception didn't occur")

    def test_badfuture7(self):
        spróbuj:
            z test zaimportuj badsyntax_future7
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(get_error_location(msg), ("badsyntax_future7", '3'))
        inaczej:
            self.fail("expected exception didn't occur")

    def test_badfuture8(self):
        spróbuj:
            z test zaimportuj badsyntax_future8
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(get_error_location(msg), ("badsyntax_future8", '3'))
        inaczej:
            self.fail("expected exception didn't occur")

    def test_badfuture9(self):
        spróbuj:
            z test zaimportuj badsyntax_future9
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(get_error_location(msg), ("badsyntax_future9", '3'))
        inaczej:
            self.fail("expected exception didn't occur")

    def test_badfuture10(self):
        spróbuj:
            z test zaimportuj badsyntax_future10
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(get_error_location(msg), ("badsyntax_future10", '3'))
        inaczej:
            self.fail("expected exception didn't occur")

    def test_parserhack(self):
        # test that the parser.c::future_hack function works jako expected
        # Note: although this test must dalej, it's nie testing the original
        #       bug jako of 2.6 since the przy statement jest nie optional oraz
        #       the parser hack disabled. If a new keyword jest introduced w
        #       2.6, change this to refer to the new future import.
        spróbuj:
            exec("z __future__ zaimportuj print_function; print 0")
        wyjąwszy SyntaxError:
            dalej
        inaczej:
            self.fail("syntax error didn't occur")

        spróbuj:
            exec("z __future__ zaimportuj (print_function); print 0")
        wyjąwszy SyntaxError:
            dalej
        inaczej:
            self.fail("syntax error didn't occur")

    def test_multiple_features(self):
        przy support.CleanImport("test.test_future5"):
            z test zaimportuj test_future5

    def test_unicode_literals_exec(self):
        scope = {}
        exec("z __future__ zaimportuj unicode_literals; x = ''", {}, scope)
        self.assertIsInstance(scope["x"], str)



jeżeli __name__ == "__main__":
    unittest.main()
