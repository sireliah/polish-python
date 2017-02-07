zaimportuj parser
zaimportuj unittest
zaimportuj sys
zaimportuj operator
zaimportuj struct
z test zaimportuj support
z test.support.script_helper zaimportuj assert_python_failure

#
#  First, we test that we can generate trees z valid source fragments,
#  oraz that these valid trees are indeed allowed by the tree-loading side
#  of the parser module.
#

klasa RoundtripLegalSyntaxTestCase(unittest.TestCase):

    def roundtrip(self, f, s):
        st1 = f(s)
        t = st1.totuple()
        spróbuj:
            st2 = parser.sequence2st(t)
        wyjąwszy parser.ParserError jako why:
            self.fail("could nie roundtrip %r: %s" % (s, why))

        self.assertEqual(t, st2.totuple(),
                         "could nie re-generate syntax tree")

    def check_expr(self, s):
        self.roundtrip(parser.expr, s)

    def test_flags_passed(self):
        # The unicode literals flags has to be dalejed z the paser to AST
        # generation.
        suite = parser.suite("z __future__ zaimportuj unicode_literals; x = ''")
        code = suite.compile()
        scope = {}
        exec(code, {}, scope)
        self.assertIsInstance(scope["x"], str)

    def check_suite(self, s):
        self.roundtrip(parser.suite, s)

    def test_uzyskaj_statement(self):
        self.check_suite("def f(): uzyskaj 1")
        self.check_suite("def f(): uzyskaj")
        self.check_suite("def f(): x += uzyskaj")
        self.check_suite("def f(): x = uzyskaj 1")
        self.check_suite("def f(): x = y = uzyskaj 1")
        self.check_suite("def f(): x = uzyskaj")
        self.check_suite("def f(): x = y = uzyskaj")
        self.check_suite("def f(): 1 + (uzyskaj)*2")
        self.check_suite("def f(): (uzyskaj 1)*2")
        self.check_suite("def f(): return; uzyskaj 1")
        self.check_suite("def f(): uzyskaj 1; return")
        self.check_suite("def f(): uzyskaj z 1")
        self.check_suite("def f(): x = uzyskaj z 1")
        self.check_suite("def f(): f((uzyskaj z 1))")
        self.check_suite("def f(): uzyskaj 1; zwróć 1")
        self.check_suite("def f():\n"
                         "    dla x w range(30):\n"
                         "        uzyskaj x\n")
        self.check_suite("def f():\n"
                         "    jeżeli (uzyskaj):\n"
                         "        uzyskaj x\n")

    def test_await_statement(self):
        self.check_suite("async def f():\n await smth()")
        self.check_suite("async def f():\n foo = await smth()")
        self.check_suite("async def f():\n foo, bar = await smth()")
        self.check_suite("async def f():\n (await smth())")
        self.check_suite("async def f():\n foo((await smth()))")
        self.check_suite("async def f():\n await foo(); zwróć 42")

    def test_async_with_statement(self):
        self.check_suite("async def f():\n async przy 1: dalej")
        self.check_suite("async def f():\n async przy a jako b, c jako d: dalej")

    def test_async_for_statement(self):
        self.check_suite("async def f():\n async dla i w (): dalej")
        self.check_suite("async def f():\n async dla i, b w (): dalej")

    def test_nonlocal_statement(self):
        self.check_suite("def f():\n"
                         "    x = 0\n"
                         "    def g():\n"
                         "        nonlocal x\n")
        self.check_suite("def f():\n"
                         "    x = y = 0\n"
                         "    def g():\n"
                         "        nonlocal x, y\n")

    def test_expressions(self):
        self.check_expr("foo(1)")
        self.check_expr("[1, 2, 3]")
        self.check_expr("[x**3 dla x w range(20)]")
        self.check_expr("[x**3 dla x w range(20) jeżeli x % 3]")
        self.check_expr("[x**3 dla x w range(20) jeżeli x % 2 jeżeli x % 3]")
        self.check_expr("list(x**3 dla x w range(20))")
        self.check_expr("list(x**3 dla x w range(20) jeżeli x % 3)")
        self.check_expr("list(x**3 dla x w range(20) jeżeli x % 2 jeżeli x % 3)")
        self.check_expr("foo(*args)")
        self.check_expr("foo(*args, **kw)")
        self.check_expr("foo(**kw)")
        self.check_expr("foo(key=value)")
        self.check_expr("foo(key=value, *args)")
        self.check_expr("foo(key=value, *args, **kw)")
        self.check_expr("foo(key=value, **kw)")
        self.check_expr("foo(a, b, c, *args)")
        self.check_expr("foo(a, b, c, *args, **kw)")
        self.check_expr("foo(a, b, c, **kw)")
        self.check_expr("foo(a, *args, keyword=23)")
        self.check_expr("foo + bar")
        self.check_expr("foo - bar")
        self.check_expr("foo * bar")
        self.check_expr("foo / bar")
        self.check_expr("foo // bar")
        self.check_expr("lambda: 0")
        self.check_expr("lambda x: 0")
        self.check_expr("lambda *y: 0")
        self.check_expr("lambda *y, **z: 0")
        self.check_expr("lambda **z: 0")
        self.check_expr("lambda x, y: 0")
        self.check_expr("lambda foo=bar: 0")
        self.check_expr("lambda foo=bar, spaz=nifty+spit: 0")
        self.check_expr("lambda foo=bar, **z: 0")
        self.check_expr("lambda foo=bar, blaz=blat+2, **z: 0")
        self.check_expr("lambda foo=bar, blaz=blat+2, *y, **z: 0")
        self.check_expr("lambda x, *y, **z: 0")
        self.check_expr("(x dla x w range(10))")
        self.check_expr("foo(x dla x w range(10))")
        self.check_expr("...")
        self.check_expr("a[...]")

    def test_simple_expression(self):
        # expr_stmt
        self.check_suite("a")

    def test_simple_assignments(self):
        self.check_suite("a = b")
        self.check_suite("a = b = c = d = e")

    def test_simple_augmented_assignments(self):
        self.check_suite("a += b")
        self.check_suite("a -= b")
        self.check_suite("a *= b")
        self.check_suite("a /= b")
        self.check_suite("a //= b")
        self.check_suite("a %= b")
        self.check_suite("a &= b")
        self.check_suite("a |= b")
        self.check_suite("a ^= b")
        self.check_suite("a <<= b")
        self.check_suite("a >>= b")
        self.check_suite("a **= b")

    def test_function_defs(self):
        self.check_suite("def f(): dalej")
        self.check_suite("def f(*args): dalej")
        self.check_suite("def f(*args, **kw): dalej")
        self.check_suite("def f(**kw): dalej")
        self.check_suite("def f(foo=bar): dalej")
        self.check_suite("def f(foo=bar, *args): dalej")
        self.check_suite("def f(foo=bar, *args, **kw): dalej")
        self.check_suite("def f(foo=bar, **kw): dalej")

        self.check_suite("def f(a, b): dalej")
        self.check_suite("def f(a, b, *args): dalej")
        self.check_suite("def f(a, b, *args, **kw): dalej")
        self.check_suite("def f(a, b, **kw): dalej")
        self.check_suite("def f(a, b, foo=bar): dalej")
        self.check_suite("def f(a, b, foo=bar, *args): dalej")
        self.check_suite("def f(a, b, foo=bar, *args, **kw): dalej")
        self.check_suite("def f(a, b, foo=bar, **kw): dalej")

        self.check_suite("@staticmethod\n"
                         "def f(): dalej")
        self.check_suite("@staticmethod\n"
                         "@funcattrs(x, y)\n"
                         "def f(): dalej")
        self.check_suite("@funcattrs()\n"
                         "def f(): dalej")

        # keyword-only arguments
        self.check_suite("def f(*, a): dalej")
        self.check_suite("def f(*, a = 5): dalej")
        self.check_suite("def f(*, a = 5, b): dalej")
        self.check_suite("def f(*, a, b = 5): dalej")
        self.check_suite("def f(*, a, b = 5, **kwds): dalej")
        self.check_suite("def f(*args, a): dalej")
        self.check_suite("def f(*args, a = 5): dalej")
        self.check_suite("def f(*args, a = 5, b): dalej")
        self.check_suite("def f(*args, a, b = 5): dalej")
        self.check_suite("def f(*args, a, b = 5, **kwds): dalej")

        # function annotations
        self.check_suite("def f(a: int): dalej")
        self.check_suite("def f(a: int = 5): dalej")
        self.check_suite("def f(*args: list): dalej")
        self.check_suite("def f(**kwds: dict): dalej")
        self.check_suite("def f(*, a: int): dalej")
        self.check_suite("def f(*, a: int = 5): dalej")
        self.check_suite("def f() -> int: dalej")

    def test_class_defs(self):
        self.check_suite("class foo():pass")
        self.check_suite("class foo(object):pass")
        self.check_suite("@class_decorator\n"
                         "class foo():pass")
        self.check_suite("@class_decorator(arg)\n"
                         "class foo():pass")
        self.check_suite("@decorator1\n"
                         "@decorator2\n"
                         "class foo():pass")

    def test_import_from_statement(self):
        self.check_suite("z sys.path zaimportuj *")
        self.check_suite("z sys.path zaimportuj dirname")
        self.check_suite("z sys.path zaimportuj (dirname)")
        self.check_suite("z sys.path zaimportuj (dirname,)")
        self.check_suite("z sys.path zaimportuj dirname jako my_dirname")
        self.check_suite("z sys.path zaimportuj (dirname jako my_dirname)")
        self.check_suite("z sys.path zaimportuj (dirname jako my_dirname,)")
        self.check_suite("z sys.path zaimportuj dirname, basename")
        self.check_suite("z sys.path zaimportuj (dirname, basename)")
        self.check_suite("z sys.path zaimportuj (dirname, basename,)")
        self.check_suite(
            "z sys.path zaimportuj dirname jako my_dirname, basename")
        self.check_suite(
            "z sys.path zaimportuj (dirname jako my_dirname, basename)")
        self.check_suite(
            "z sys.path zaimportuj (dirname jako my_dirname, basename,)")
        self.check_suite(
            "z sys.path zaimportuj dirname, basename jako my_basename")
        self.check_suite(
            "z sys.path zaimportuj (dirname, basename jako my_basename)")
        self.check_suite(
            "z sys.path zaimportuj (dirname, basename jako my_basename,)")
        self.check_suite("z .bogus zaimportuj x")

    def test_basic_import_statement(self):
        self.check_suite("zaimportuj sys")
        self.check_suite("zaimportuj sys jako system")
        self.check_suite("zaimportuj sys, math")
        self.check_suite("zaimportuj sys jako system, math")
        self.check_suite("zaimportuj sys, math jako my_math")

    def test_relative_imports(self):
        self.check_suite("z . zaimportuj name")
        self.check_suite("z .. zaimportuj name")
        # check all the way up to '....', since '...' jest tokenized
        # differently z '.' (it's an ellipsis token).
        self.check_suite("z ... zaimportuj name")
        self.check_suite("z .... zaimportuj name")
        self.check_suite("z .pkg zaimportuj name")
        self.check_suite("z ..pkg zaimportuj name")
        self.check_suite("z ...pkg zaimportuj name")
        self.check_suite("z ....pkg zaimportuj name")

    def test_pep263(self):
        self.check_suite("# -*- coding: iso-8859-1 -*-\n"
                         "pass\n")

    def test_assert(self):
        self.check_suite("assert alo < ahi oraz blo < bhi\n")

    def test_with(self):
        self.check_suite("przy open('x'): dalej\n")
        self.check_suite("przy open('x') jako f: dalej\n")
        self.check_suite("przy open('x') jako f, open('y') jako g: dalej\n")

    def test_try_stmt(self):
        self.check_suite("spróbuj: dalej\nwyjąwszy: dalej\n")
        self.check_suite("spróbuj: dalej\nw_końcu: dalej\n")
        self.check_suite("spróbuj: dalej\nwyjąwszy A: dalej\nw_końcu: dalej\n")
        self.check_suite("spróbuj: dalej\nwyjąwszy A: dalej\nwyjąwszy: dalej\n"
                         "w_końcu: dalej\n")
        self.check_suite("spróbuj: dalej\nwyjąwszy: dalej\ninaczej: dalej\n")
        self.check_suite("spróbuj: dalej\nwyjąwszy: dalej\ninaczej: dalej\n"
                         "w_końcu: dalej\n")

    def test_position(self):
        # An absolutely minimal test of position information.  Better
        # tests would be a big project.
        code = "def f(x):\n    zwróć x + 1"
        st1 = parser.suite(code)
        st2 = st1.totuple(line_info=1, col_info=1)

        def walk(tree):
            node_type = tree[0]
            next = tree[1]
            jeżeli isinstance(next, tuple):
                dla elt w tree[1:]:
                    dla x w walk(elt):
                        uzyskaj x
            inaczej:
                uzyskaj tree

        terminals = list(walk(st2))
        self.assertEqual([
            (1, 'def', 1, 0),
            (1, 'f', 1, 4),
            (7, '(', 1, 5),
            (1, 'x', 1, 6),
            (8, ')', 1, 7),
            (11, ':', 1, 8),
            (4, '', 1, 9),
            (5, '', 2, -1),
            (1, 'return', 2, 4),
            (1, 'x', 2, 11),
            (14, '+', 2, 13),
            (2, '1', 2, 15),
            (4, '', 2, 16),
            (6, '', 2, -1),
            (4, '', 2, -1),
            (0, '', 2, -1)],
                         terminals)

    def test_extended_unpacking(self):
        self.check_suite("*a = y")
        self.check_suite("x, *b, = m")
        self.check_suite("[*a, *b] = y")
        self.check_suite("dla [*x, b] w x: dalej")

    def test_raise_statement(self):
        self.check_suite("raise\n")
        self.check_suite("raise e\n")
        self.check_suite("spróbuj:\n"
                         "    suite\n"
                         "wyjąwszy Exception jako e:\n"
                         "    podnieś ValueError z e\n")

    def test_list_displays(self):
        self.check_expr('[]')
        self.check_expr('[*{2}, 3, *[4]]')

    def test_set_displays(self):
        self.check_expr('{*{2}, 3, *[4]}')
        self.check_expr('{2}')
        self.check_expr('{2,}')
        self.check_expr('{2, 3}')
        self.check_expr('{2, 3,}')

    def test_dict_displays(self):
        self.check_expr('{}')
        self.check_expr('{a:b}')
        self.check_expr('{a:b,}')
        self.check_expr('{a:b, c:d}')
        self.check_expr('{a:b, c:d,}')
        self.check_expr('{**{}}')
        self.check_expr('{**{}, 3:4, **{5:6, 7:8}}')

    def test_argument_unpacking(self):
        self.check_expr("f(*a, **b)")
        self.check_expr('f(a, *b, *c, *d)')
        self.check_expr('f(**a, **b)')
        self.check_expr('f(2, *a, *b, **b, **c, **d)')
        self.check_expr("f(*b, *() albo () oraz (), **{} oraz {}, **() albo {})")

    def test_set_comprehensions(self):
        self.check_expr('{x dla x w seq}')
        self.check_expr('{f(x) dla x w seq}')
        self.check_expr('{f(x) dla x w seq jeżeli condition(x)}')

    def test_dict_comprehensions(self):
        self.check_expr('{x:x dla x w seq}')
        self.check_expr('{x**2:x[3] dla x w seq jeżeli condition(x)}')
        self.check_expr('{x:x dla x w seq1 dla y w seq2 jeżeli condition(x, y)}')


#
#  Second, we take *invalid* trees oraz make sure we get ParserError
#  rejections dla them.
#

klasa IllegalSyntaxTestCase(unittest.TestCase):

    def check_bad_tree(self, tree, label):
        spróbuj:
            parser.sequence2st(tree)
        wyjąwszy parser.ParserError:
            dalej
        inaczej:
            self.fail("did nie detect invalid tree dla %r" % label)

    def test_junk(self):
        # nie even remotely valid:
        self.check_bad_tree((1, 2, 3), "<junk>")

    def test_illegal_uzyskaj_1(self):
        # Illegal uzyskaj statement: def f(): zwróć 1; uzyskaj 1
        tree = \
        (257,
         (264,
          (285,
           (259,
            (1, 'def'),
            (1, 'f'),
            (260, (7, '('), (8, ')')),
            (11, ':'),
            (291,
             (4, ''),
             (5, ''),
             (264,
              (265,
               (266,
                (272,
                 (275,
                  (1, 'return'),
                  (313,
                   (292,
                    (293,
                     (294,
                      (295,
                       (297,
                        (298,
                         (299,
                          (300,
                           (301,
                            (302, (303, (304, (305, (2, '1')))))))))))))))))),
               (264,
                (265,
                 (266,
                  (272,
                   (276,
                    (1, 'uzyskaj'),
                    (313,
                     (292,
                      (293,
                       (294,
                        (295,
                         (297,
                          (298,
                           (299,
                            (300,
                             (301,
                              (302,
                               (303, (304, (305, (2, '1')))))))))))))))))),
                 (4, ''))),
               (6, ''))))),
           (4, ''),
           (0, ''))))
        self.check_bad_tree(tree, "def f():\n  zwróć 1\n  uzyskaj 1")

    def test_illegal_uzyskaj_2(self):
        # Illegal zwróć w generator: def f(): zwróć 1; uzyskaj 1
        tree = \
        (257,
         (264,
          (265,
           (266,
            (278,
             (1, 'from'),
             (281, (1, '__future__')),
             (1, 'import'),
             (279, (1, 'generators')))),
           (4, ''))),
         (264,
          (285,
           (259,
            (1, 'def'),
            (1, 'f'),
            (260, (7, '('), (8, ')')),
            (11, ':'),
            (291,
             (4, ''),
             (5, ''),
             (264,
              (265,
               (266,
                (272,
                 (275,
                  (1, 'return'),
                  (313,
                   (292,
                    (293,
                     (294,
                      (295,
                       (297,
                        (298,
                         (299,
                          (300,
                           (301,
                            (302, (303, (304, (305, (2, '1')))))))))))))))))),
               (264,
                (265,
                 (266,
                  (272,
                   (276,
                    (1, 'uzyskaj'),
                    (313,
                     (292,
                      (293,
                       (294,
                        (295,
                         (297,
                          (298,
                           (299,
                            (300,
                             (301,
                              (302,
                               (303, (304, (305, (2, '1')))))))))))))))))),
                 (4, ''))),
               (6, ''))))),
           (4, ''),
           (0, ''))))
        self.check_bad_tree(tree, "def f():\n  zwróć 1\n  uzyskaj 1")

    def test_a_comma_comma_c(self):
        # Illegal input: a,,c
        tree = \
        (258,
         (311,
          (290,
           (291,
            (292,
             (293,
              (295,
               (296,
                (297,
                 (298, (299, (300, (301, (302, (303, (1, 'a')))))))))))))),
          (12, ','),
          (12, ','),
          (290,
           (291,
            (292,
             (293,
              (295,
               (296,
                (297,
                 (298, (299, (300, (301, (302, (303, (1, 'c'))))))))))))))),
         (4, ''),
         (0, ''))
        self.check_bad_tree(tree, "a,,c")

    def test_illegal_operator(self):
        # Illegal input: a $= b
        tree = \
        (257,
         (264,
          (265,
           (266,
            (267,
             (312,
              (291,
               (292,
                (293,
                 (294,
                  (296,
                   (297,
                    (298,
                     (299,
                      (300, (301, (302, (303, (304, (1, 'a'))))))))))))))),
             (268, (37, '$=')),
             (312,
              (291,
               (292,
                (293,
                 (294,
                  (296,
                   (297,
                    (298,
                     (299,
                      (300, (301, (302, (303, (304, (1, 'b'))))))))))))))))),
           (4, ''))),
         (0, ''))
        self.check_bad_tree(tree, "a $= b")

    def test_malformed_global(self):
        #doesn't have global keyword w ast
        tree = (257,
                (264,
                 (265,
                  (266,
                   (282, (1, 'foo'))), (4, ''))),
                (4, ''),
                (0, ''))
        self.check_bad_tree(tree, "malformed global ast")

    def test_missing_import_source(self):
        # z zaimportuj fred
        tree = \
            (257,
             (268,
              (269,
               (270,
                (282,
                 (284, (1, 'from'), (1, 'import'),
                  (287, (285, (1, 'fred')))))),
               (4, ''))),
             (4, ''), (0, ''))
        self.check_bad_tree(tree, "z zaimportuj fred")


klasa CompileTestCase(unittest.TestCase):

    # These tests are very minimal. :-(

    def test_compile_expr(self):
        st = parser.expr('2 + 3')
        code = parser.compilest(st)
        self.assertEqual(eval(code), 5)

    def test_compile_suite(self):
        st = parser.suite('x = 2; y = x + 3')
        code = parser.compilest(st)
        globs = {}
        exec(code, globs)
        self.assertEqual(globs['y'], 5)

    def test_compile_error(self):
        st = parser.suite('1 = 3 + 4')
        self.assertRaises(SyntaxError, parser.compilest, st)

    def test_compile_badunicode(self):
        st = parser.suite('a = "\\U12345678"')
        self.assertRaises(SyntaxError, parser.compilest, st)
        st = parser.suite('a = "\\u1"')
        self.assertRaises(SyntaxError, parser.compilest, st)

    def test_issue_9011(self):
        # Issue 9011: compilation of an unary minus expression changed
        # the meaning of the ST, so that a second compilation produced
        # incorrect results.
        st = parser.expr('-3')
        code1 = parser.compilest(st)
        self.assertEqual(eval(code1), -3)
        code2 = parser.compilest(st)
        self.assertEqual(eval(code2), -3)

klasa ParserStackLimitTestCase(unittest.TestCase):
    """try to push the parser to/over its limits.
    see http://bugs.python.org/issue1881 dla a discussion
    """
    def _nested_expression(self, level):
        zwróć "["*level+"]"*level

    def test_deeply_nested_list(self):
        # XXX used to be 99 levels w 2.x
        e = self._nested_expression(93)
        st = parser.expr(e)
        st.compile()

    def test_trigger_memory_error(self):
        e = self._nested_expression(100)
        rc, out, err = assert_python_failure('-c', e)
        # parsing the expression will result w an error message
        # followed by a MemoryError (see #11963)
        self.assertIn(b's_push: parser stack overflow', err)
        self.assertIn(b'MemoryError', err)

klasa STObjectTestCase(unittest.TestCase):
    """Test operations on ST objects themselves"""

    def test_comparisons(self):
        # ST objects should support order oraz equality comparisons
        st1 = parser.expr('2 + 3')
        st2 = parser.suite('x = 2; y = x + 3')
        st3 = parser.expr('list(x**3 dla x w range(20))')
        st1_copy = parser.expr('2 + 3')
        st2_copy = parser.suite('x = 2; y = x + 3')
        st3_copy = parser.expr('list(x**3 dla x w range(20))')

        # exercise fast path dla object identity
        self.assertEqual(st1 == st1, Prawda)
        self.assertEqual(st2 == st2, Prawda)
        self.assertEqual(st3 == st3, Prawda)
        # slow path equality
        self.assertEqual(st1, st1_copy)
        self.assertEqual(st2, st2_copy)
        self.assertEqual(st3, st3_copy)
        self.assertEqual(st1 == st2, Nieprawda)
        self.assertEqual(st1 == st3, Nieprawda)
        self.assertEqual(st2 == st3, Nieprawda)
        self.assertEqual(st1 != st1, Nieprawda)
        self.assertEqual(st2 != st2, Nieprawda)
        self.assertEqual(st3 != st3, Nieprawda)
        self.assertEqual(st1 != st1_copy, Nieprawda)
        self.assertEqual(st2 != st2_copy, Nieprawda)
        self.assertEqual(st3 != st3_copy, Nieprawda)
        self.assertEqual(st2 != st1, Prawda)
        self.assertEqual(st1 != st3, Prawda)
        self.assertEqual(st3 != st2, Prawda)
        # we don't particularly care what the ordering is;  just that
        # it's usable oraz self-consistent
        self.assertEqual(st1 < st2, nie (st2 <= st1))
        self.assertEqual(st1 < st3, nie (st3 <= st1))
        self.assertEqual(st2 < st3, nie (st3 <= st2))
        self.assertEqual(st1 < st2, st2 > st1)
        self.assertEqual(st1 < st3, st3 > st1)
        self.assertEqual(st2 < st3, st3 > st2)
        self.assertEqual(st1 <= st2, st2 >= st1)
        self.assertEqual(st3 <= st1, st1 >= st3)
        self.assertEqual(st2 <= st3, st3 >= st2)
        # transitivity
        bottom = min(st1, st2, st3)
        top = max(st1, st2, st3)
        mid = sorted([st1, st2, st3])[1]
        self.assertPrawda(bottom < mid)
        self.assertPrawda(bottom < top)
        self.assertPrawda(mid < top)
        self.assertPrawda(bottom <= mid)
        self.assertPrawda(bottom <= top)
        self.assertPrawda(mid <= top)
        self.assertPrawda(bottom <= bottom)
        self.assertPrawda(mid <= mid)
        self.assertPrawda(top <= top)
        # interaction przy other types
        self.assertEqual(st1 == 1588.602459, Nieprawda)
        self.assertEqual('spanish armada' != st2, Prawda)
        self.assertRaises(TypeError, operator.ge, st3, Nic)
        self.assertRaises(TypeError, operator.le, Nieprawda, st1)
        self.assertRaises(TypeError, operator.lt, st1, 1815)
        self.assertRaises(TypeError, operator.gt, b'waterloo', st2)

    check_sizeof = support.check_sizeof

    @support.cpython_only
    def test_sizeof(self):
        def XXXROUNDUP(n):
            jeżeli n <= 1:
                zwróć n
            jeżeli n <= 128:
                zwróć (n + 3) & ~3
            zwróć 1 << (n - 1).bit_length()

        basesize = support.calcobjsize('Pii')
        nodesize = struct.calcsize('hP3iP0h')
        def sizeofchildren(node):
            jeżeli node jest Nic:
                zwróć 0
            res = 0
            hasstr = len(node) > 1 oraz isinstance(node[-1], str)
            jeżeli hasstr:
                res += len(node[-1]) + 1
            children = node[1:-1] jeżeli hasstr inaczej node[1:]
            jeżeli children:
                res += XXXROUNDUP(len(children)) * nodesize
                dla child w children:
                    res += sizeofchildren(child)
            zwróć res

        def check_st_sizeof(st):
            self.check_sizeof(st, basesize + nodesize +
                                  sizeofchildren(st.totuple()))

        check_st_sizeof(parser.expr('2 + 3'))
        check_st_sizeof(parser.expr('2 + 3 + 4'))
        check_st_sizeof(parser.suite('x = 2 + 3'))
        check_st_sizeof(parser.suite(''))
        check_st_sizeof(parser.suite('# -*- coding: utf-8 -*-'))
        check_st_sizeof(parser.expr('[' + '2,' * 1000 + ']'))


    # XXX tests dla pickling oraz unpickling of ST objects should go here

klasa OtherParserCase(unittest.TestCase):

    def test_two_args_to_expr(self):
        # See bug #12264
        przy self.assertRaises(TypeError):
            parser.expr("a", "b")

jeżeli __name__ == "__main__":
    unittest.main()
