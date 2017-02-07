"""Test suite dla 2to3's parser oraz grammar files.

This jest the place to add tests dla changes to 2to3's grammar, such jako those
merging the grammars dla Python 2 oraz 3. In addition to specific tests for
parts of the grammar we've changed, we also make sure we can parse the
test_grammar.py files z both Python 2 oraz Python 3.
"""

z __future__ zaimportuj with_statement

# Testing imports
z . zaimportuj support
z .support zaimportuj driver, test_dir
z test.support zaimportuj verbose

# Python imports
zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj warnings
zaimportuj subprocess

# Local imports
z lib2to3.pgen2 zaimportuj tokenize
z ..pgen2.parse zaimportuj ParseError
z lib2to3.pygram zaimportuj python_symbols jako syms


klasa TestDriver(support.TestCase):

    def test_formfeed(self):
        s = """print 1\n\x0Cprint 2\n"""
        t = driver.parse_string(s)
        self.assertEqual(t.children[0].children[0].type, syms.print_stmt)
        self.assertEqual(t.children[1].children[0].type, syms.print_stmt)


klasa GrammarTest(support.TestCase):
    def validate(self, code):
        support.parse_string(code)

    def invalid_syntax(self, code):
        spróbuj:
            self.validate(code)
        wyjąwszy ParseError:
            dalej
        inaczej:
            podnieś AssertionError("Syntax shouldn't have been valid")


klasa TestMatrixMultiplication(GrammarTest):
    def test_matrix_multiplication_operator(self):
        self.validate("a @ b")
        self.validate("a @= b")


klasa TestYieldFrom(GrammarTest):
    def test_uzyskaj_from(self):
        self.validate("uzyskaj z x")
        self.validate("(uzyskaj z x) + y")
        self.invalid_syntax("uzyskaj from")


klasa TestAsyncAwait(GrammarTest):
    def test_await_expr(self):
        self.validate("""async def foo():
                             await x
                      """)

        self.validate("""async def foo():

            def foo(): dalej

            def foo(): dalej

            await x
        """)

        self.validate("""async def foo(): zwróć await a""")

        self.validate("""def foo():
            def foo(): dalej
            async def foo(): await x
        """)

        self.invalid_syntax("await x")
        self.invalid_syntax("""def foo():
                                   await x""")

        self.invalid_syntax("""def foo():
            def foo(): dalej
            async def foo(): dalej
            await x
        """)

    def test_async_var(self):
        self.validate("""async = 1""")
        self.validate("""await = 1""")
        self.validate("""def async(): dalej""")

    def test_async_with(self):
        self.validate("""async def foo():
                             async dla a w b: dalej""")

        self.invalid_syntax("""def foo():
                                   async dla a w b: dalej""")

    def test_async_for(self):
        self.validate("""async def foo():
                             async przy a: dalej""")

        self.invalid_syntax("""def foo():
                                   async przy a: dalej""")


klasa TestRaiseChanges(GrammarTest):
    def test_2x_style_1(self):
        self.validate("raise")

    def test_2x_style_2(self):
        self.validate("raise E, V")

    def test_2x_style_3(self):
        self.validate("raise E, V, T")

    def test_2x_style_invalid_1(self):
        self.invalid_syntax("raise E, V, T, Z")

    def test_3x_style(self):
        self.validate("raise E1 z E2")

    def test_3x_style_invalid_1(self):
        self.invalid_syntax("raise E, V z E1")

    def test_3x_style_invalid_2(self):
        self.invalid_syntax("raise E z E1, E2")

    def test_3x_style_invalid_3(self):
        self.invalid_syntax("raise z E1, E2")

    def test_3x_style_invalid_4(self):
        self.invalid_syntax("raise E from")


# Adapted z Python 3's Lib/test/test_grammar.py:GrammarTests.testFuncdef
klasa TestFunctionAnnotations(GrammarTest):
    def test_1(self):
        self.validate("""def f(x) -> list: dalej""")

    def test_2(self):
        self.validate("""def f(x:int): dalej""")

    def test_3(self):
        self.validate("""def f(*x:str): dalej""")

    def test_4(self):
        self.validate("""def f(**x:float): dalej""")

    def test_5(self):
        self.validate("""def f(x, y:1+2): dalej""")

    def test_6(self):
        self.validate("""def f(a, (b:1, c:2, d)): dalej""")

    def test_7(self):
        self.validate("""def f(a, (b:1, c:2, d), e:3=4, f=5, *g:6): dalej""")

    def test_8(self):
        s = """def f(a, (b:1, c:2, d), e:3=4, f=5,
                        *g:6, h:7, i=8, j:9=10, **k:11) -> 12: dalej"""
        self.validate(s)


klasa TestExcept(GrammarTest):
    def test_new(self):
        s = """
            spróbuj:
                x
            wyjąwszy E jako N:
                y"""
        self.validate(s)

    def test_old(self):
        s = """
            spróbuj:
                x
            wyjąwszy E, N:
                y"""
        self.validate(s)


# Adapted z Python 3's Lib/test/test_grammar.py:GrammarTests.testAtoms
klasa TestSetLiteral(GrammarTest):
    def test_1(self):
        self.validate("""x = {'one'}""")

    def test_2(self):
        self.validate("""x = {'one', 1,}""")

    def test_3(self):
        self.validate("""x = {'one', 'two', 'three'}""")

    def test_4(self):
        self.validate("""x = {2, 3, 4,}""")


klasa TestNumericLiterals(GrammarTest):
    def test_new_octal_notation(self):
        self.validate("""0o7777777777777""")
        self.invalid_syntax("""0o7324528887""")

    def test_new_binary_notation(self):
        self.validate("""0b101010""")
        self.invalid_syntax("""0b0101021""")


klasa TestClassDef(GrammarTest):
    def test_new_syntax(self):
        self.validate("class B(t=7): dalej")
        self.validate("class B(t, *args): dalej")
        self.validate("class B(t, **kwargs): dalej")
        self.validate("class B(t, *args, **kwargs): dalej")
        self.validate("class B(t, y=9, *args, **kwargs): dalej")


klasa TestParserIdempotency(support.TestCase):

    """A cut-down version of pytree_idempotency.py."""

    # Issue 13125
    @unittest.expectedFailure
    def test_all_project_files(self):
        dla filepath w support.all_project_files():
            przy open(filepath, "rb") jako fp:
                encoding = tokenize.detect_encoding(fp.readline)[0]
            self.assertIsNotNic(encoding,
                                 "can't detect encoding dla %s" % filepath)
            przy open(filepath, "r", encoding=encoding) jako fp:
                source = fp.read()
            spróbuj:
                tree = driver.parse_string(source)
            wyjąwszy ParseError jako err:
                jeżeli verbose > 0:
                    warnings.warn('ParseError on file %s (%s)' % (filepath, err))
                kontynuuj
            new = str(tree)
            x = diff(filepath, new)
            jeżeli x:
                self.fail("Idempotency failed: %s" % filepath)

    def test_extended_unpacking(self):
        driver.parse_string("a, *b, c = x\n")
        driver.parse_string("[*a, b] = x\n")
        driver.parse_string("(z, *y, w) = m\n")
        driver.parse_string("dla *z, m w d: dalej\n")


klasa TestLiterals(GrammarTest):

    def validate(self, s):
        driver.parse_string(support.dedent(s) + "\n\n")

    def test_multiline_bytes_literals(self):
        s = """
            md5test(b"\xaa" * 80,
                    (b"Test Using Larger Than Block-Size Key "
                     b"and Larger Than One Block-Size Data"),
                    "6f630fad67cda0ee1fb1f562db3aa53e")
            """
        self.validate(s)

    def test_multiline_bytes_tripquote_literals(self):
        s = '''
            b"""
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN">
            """
            '''
        self.validate(s)

    def test_multiline_str_literals(self):
        s = """
            md5test("\xaa" * 80,
                    ("Test Using Larger Than Block-Size Key "
                     "and Larger Than One Block-Size Data"),
                    "6f630fad67cda0ee1fb1f562db3aa53e")
            """
        self.validate(s)


def diff(fn, result):
    spróbuj:
        przy open('@', 'w') jako f:
            f.write(str(result))
        fn = fn.replace('"', '\\"')
        zwróć subprocess.call(['diff', '-u', fn, '@'], stdout=(subprocess.DEVNULL jeżeli verbose < 1 inaczej Nic))
    w_końcu:
        spróbuj:
            os.remove("@")
        wyjąwszy OSError:
            dalej
