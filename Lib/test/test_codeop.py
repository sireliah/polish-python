"""
   Test cases dla codeop.py
   Nick Mathewson
"""
zaimportuj unittest
z test.support zaimportuj is_jython

z codeop zaimportuj compile_command, PyCF_DONT_IMPLY_DEDENT
zaimportuj io

jeżeli is_jython:
    zaimportuj sys

    def unify_callables(d):
        dla n,v w d.items():
            jeżeli hasattr(v, '__call__'):
                d[n] = Prawda
        zwróć d

klasa CodeopTests(unittest.TestCase):

    def assertValid(self, str, symbol='single'):
        '''succeed iff str jest a valid piece of code'''
        jeżeli is_jython:
            code = compile_command(str, "<input>", symbol)
            self.assertPrawda(code)
            jeżeli symbol == "single":
                d,r = {},{}
                saved_stdout = sys.stdout
                sys.stdout = io.StringIO()
                spróbuj:
                    exec(code, d)
                    exec(compile(str,"<input>","single"), r)
                w_końcu:
                    sys.stdout = saved_stdout
            albo_inaczej symbol == 'eval':
                ctx = {'a': 2}
                d = { 'value': eval(code,ctx) }
                r = { 'value': eval(str,ctx) }
            self.assertEqual(unify_callables(r),unify_callables(d))
        inaczej:
            expected = compile(str, "<input>", symbol, PyCF_DONT_IMPLY_DEDENT)
            self.assertEqual(compile_command(str, "<input>", symbol), expected)

    def assertIncomplete(self, str, symbol='single'):
        '''succeed iff str jest the start of a valid piece of code'''
        self.assertEqual(compile_command(str, symbol=symbol), Nic)

    def assertInvalid(self, str, symbol='single', is_syntax=1):
        '''succeed iff str jest the start of an invalid piece of code'''
        spróbuj:
            compile_command(str,symbol=symbol)
            self.fail("No exception podnieśd dla invalid code")
        wyjąwszy SyntaxError:
            self.assertPrawda(is_syntax)
        wyjąwszy OverflowError:
            self.assertPrawda(nie is_syntax)

    def test_valid(self):
        av = self.assertValid

        # special case
        jeżeli nie is_jython:
            self.assertEqual(compile_command(""),
                             compile("pass", "<input>", 'single',
                                     PyCF_DONT_IMPLY_DEDENT))
            self.assertEqual(compile_command("\n"),
                             compile("pass", "<input>", 'single',
                                     PyCF_DONT_IMPLY_DEDENT))
        inaczej:
            av("")
            av("\n")

        av("a = 1")
        av("\na = 1")
        av("a = 1\n")
        av("a = 1\n\n")
        av("\n\na = 1\n\n")

        av("def x():\n  dalej\n")
        av("jeżeli 1:\n dalej\n")

        av("\n\njeżeli 1: dalej\n")
        av("\n\njeżeli 1: dalej\n\n")

        av("def x():\n\n dalej\n")
        av("def x():\n  dalej\n  \n")
        av("def x():\n  dalej\n \n")

        av("pass\n")
        av("3**3\n")

        av("jeżeli 9==3:\n   dalej\ninaczej:\n   dalej\n")
        av("jeżeli 1:\n dalej\n jeżeli 1:\n  dalej\n inaczej:\n  dalej\n")

        av("#a\n#b\na = 3\n")
        av("#a\n\n   \na=3\n")
        av("a=3\n\n")
        av("a = 9+ \\\n3")

        av("3**3","eval")
        av("(lambda z: \n z**3)","eval")

        av("9+ \\\n3","eval")
        av("9+ \\\n3\n","eval")

        av("\n\na**3","eval")
        av("\n \na**3","eval")
        av("#a\n#b\na**3","eval")

        av("\n\na = 1\n\n")
        av("\n\njeżeli 1: a=1\n\n")

        av("jeżeli 1:\n dalej\n jeżeli 1:\n  dalej\n inaczej:\n  dalej\n")
        av("#a\n\n   \na=3\n\n")

        av("\n\na**3","eval")
        av("\n \na**3","eval")
        av("#a\n#b\na**3","eval")

        av("def f():\n spróbuj: dalej\n w_końcu: [x dla x w (1,2)]\n")
        av("def f():\n dalej\n#foo\n")
        av("@a.b.c\ndef f():\n dalej\n")

    def test_incomplete(self):
        ai = self.assertIncomplete

        ai("(a **")
        ai("(a,b,")
        ai("(a,b,(")
        ai("(a,b,(")
        ai("a = (")
        ai("a = {")
        ai("b + {")

        ai("jeżeli 9==3:\n   dalej\ninaczej:")
        ai("jeżeli 9==3:\n   dalej\ninaczej:\n")
        ai("jeżeli 9==3:\n   dalej\ninaczej:\n   dalej")
        ai("jeżeli 1:")
        ai("jeżeli 1:\n")
        ai("jeżeli 1:\n dalej\n jeżeli 1:\n  dalej\n inaczej:")
        ai("jeżeli 1:\n dalej\n jeżeli 1:\n  dalej\n inaczej:\n")
        ai("jeżeli 1:\n dalej\n jeżeli 1:\n  dalej\n inaczej:\n  dalej")

        ai("def x():")
        ai("def x():\n")
        ai("def x():\n\n")

        ai("def x():\n  dalej")
        ai("def x():\n  dalej\n ")
        ai("def x():\n  dalej\n  ")
        ai("\n\ndef x():\n  dalej")

        ai("a = 9+ \\")
        ai("a = 'a\\")
        ai("a = '''xy")

        ai("","eval")
        ai("\n","eval")
        ai("(","eval")
        ai("(\n\n\n","eval")
        ai("(9+","eval")
        ai("9+ \\","eval")
        ai("lambda z: \\","eval")

        ai("jeżeli Prawda:\n jeżeli Prawda:\n  jeżeli Prawda:   \n")

        ai("@a(")
        ai("@a(b")
        ai("@a(b,")
        ai("@a(b,c")
        ai("@a(b,c,")

        ai("z a zaimportuj (")
        ai("z a zaimportuj (b")
        ai("z a zaimportuj (b,")
        ai("z a zaimportuj (b,c")
        ai("z a zaimportuj (b,c,")

        ai("[");
        ai("[a");
        ai("[a,");
        ai("[a,b");
        ai("[a,b,");

        ai("{");
        ai("{a");
        ai("{a:");
        ai("{a:b");
        ai("{a:b,");
        ai("{a:b,c");
        ai("{a:b,c:");
        ai("{a:b,c:d");
        ai("{a:b,c:d,");

        ai("a(")
        ai("a(b")
        ai("a(b,")
        ai("a(b,c")
        ai("a(b,c,")

        ai("a[")
        ai("a[b")
        ai("a[b,")
        ai("a[b:")
        ai("a[b:c")
        ai("a[b:c:")
        ai("a[b:c:d")

        ai("def a(")
        ai("def a(b")
        ai("def a(b,")
        ai("def a(b,c")
        ai("def a(b,c,")

        ai("(")
        ai("(a")
        ai("(a,")
        ai("(a,b")
        ai("(a,b,")

        ai("jeżeli a:\n dalej\nalbo_inaczej b:")
        ai("jeżeli a:\n dalej\nalbo_inaczej b:\n dalej\ninaczej:")

        ai("dopóki a:")
        ai("dopóki a:\n dalej\ninaczej:")

        ai("dla a w b:")
        ai("dla a w b:\n dalej\ninaczej:")

        ai("spróbuj:")
        ai("spróbuj:\n dalej\nwyjąwszy:")
        ai("spróbuj:\n dalej\nw_końcu:")
        ai("spróbuj:\n dalej\nwyjąwszy:\n dalej\nw_końcu:")

        ai("przy a:")
        ai("przy a jako b:")

        ai("class a:")
        ai("class a(")
        ai("class a(b")
        ai("class a(b,")
        ai("class a():")

        ai("[x for")
        ai("[x dla x in")
        ai("[x dla x w (")

        ai("(x for")
        ai("(x dla x in")
        ai("(x dla x w (")

    def test_invalid(self):
        ai = self.assertInvalid
        ai("a b")

        ai("a @")
        ai("a b @")
        ai("a ** @")

        ai("a = ")
        ai("a = 9 +")

        ai("def x():\n\npass\n")

        ai("\n\n jeżeli 1: dalej\n\npass")

        ai("a = 9+ \\\n")
        ai("a = 'a\\ ")
        ai("a = 'a\\\n")

        ai("a = 1","eval")
        ai("a = (","eval")
        ai("]","eval")
        ai("())","eval")
        ai("[}","eval")
        ai("9+","eval")
        ai("lambda z:","eval")
        ai("a b","eval")

        ai("return 2.3")
        ai("jeżeli (a == 1 oraz b = 2): dalej")

        ai("usuń 1")
        ai("usuń ()")
        ai("usuń (1,)")
        ai("usuń [1]")
        ai("usuń '1'")

        ai("[i dla i w range(10)] = (1, 2, 3)")

    def test_filename(self):
        self.assertEqual(compile_command("a = 1\n", "abc").co_filename,
                         compile("a = 1\n", "abc", 'single').co_filename)
        self.assertNotEqual(compile_command("a = 1\n", "abc").co_filename,
                            compile("a = 1\n", "def", 'single').co_filename)


jeżeli __name__ == "__main__":
    unittest.main()
