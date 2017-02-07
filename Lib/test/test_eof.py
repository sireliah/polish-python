"""test script dla a few new invalid token catches"""

zaimportuj unittest
z test zaimportuj support

klasa EOFTestCase(unittest.TestCase):
    def test_EOFC(self):
        expect = "EOL dopóki scanning string literal (<string>, line 1)"
        spróbuj:
            eval("""'this jest a test\
            """)
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(str(msg), expect)
        inaczej:
            podnieś support.TestFailed

    def test_EOFS(self):
        expect = ("EOF dopóki scanning triple-quoted string literal "
                  "(<string>, line 1)")
        spróbuj:
            eval("""'''this jest a test""")
        wyjąwszy SyntaxError jako msg:
            self.assertEqual(str(msg), expect)
        inaczej:
            podnieś support.TestFailed

jeżeli __name__ == "__main__":
    unittest.main()
