""" Test suite dla the code w fixer_util """

# Testing imports
z . zaimportuj support

# Python imports
zaimportuj os.path

# Local imports
z lib2to3.pytree zaimportuj Node, Leaf
z lib2to3 zaimportuj fixer_util
z lib2to3.fixer_util zaimportuj Attr, Name, Call, Comma
z lib2to3.pgen2 zaimportuj token

def parse(code, strip_levels=0):
    # The topmost node jest file_input, which we don't care about.
    # The next-topmost node jest a *_stmt node, which we also don't care about
    tree = support.parse_string(code)
    dla i w range(strip_levels):
        tree = tree.children[0]
    tree.parent = Nic
    zwróć tree

klasa MacroTestCase(support.TestCase):
    def assertStr(self, node, string):
        jeżeli isinstance(node, (tuple, list)):
            node = Node(fixer_util.syms.simple_stmt, node)
        self.assertEqual(str(node), string)


klasa Test_is_tuple(support.TestCase):
    def is_tuple(self, string):
        zwróć fixer_util.is_tuple(parse(string, strip_levels=2))

    def test_valid(self):
        self.assertPrawda(self.is_tuple("(a, b)"))
        self.assertPrawda(self.is_tuple("(a, (b, c))"))
        self.assertPrawda(self.is_tuple("((a, (b, c)),)"))
        self.assertPrawda(self.is_tuple("(a,)"))
        self.assertPrawda(self.is_tuple("()"))

    def test_invalid(self):
        self.assertNieprawda(self.is_tuple("(a)"))
        self.assertNieprawda(self.is_tuple("('foo') % (b, c)"))


klasa Test_is_list(support.TestCase):
    def is_list(self, string):
        zwróć fixer_util.is_list(parse(string, strip_levels=2))

    def test_valid(self):
        self.assertPrawda(self.is_list("[]"))
        self.assertPrawda(self.is_list("[a]"))
        self.assertPrawda(self.is_list("[a, b]"))
        self.assertPrawda(self.is_list("[a, [b, c]]"))
        self.assertPrawda(self.is_list("[[a, [b, c]],]"))

    def test_invalid(self):
        self.assertNieprawda(self.is_list("[]+[]"))


klasa Test_Attr(MacroTestCase):
    def test(self):
        call = parse("foo()", strip_levels=2)

        self.assertStr(Attr(Name("a"), Name("b")), "a.b")
        self.assertStr(Attr(call, Name("b")), "foo().b")

    def test_returns(self):
        attr = Attr(Name("a"), Name("b"))
        self.assertEqual(type(attr), list)


klasa Test_Name(MacroTestCase):
    def test(self):
        self.assertStr(Name("a"), "a")
        self.assertStr(Name("foo.foo().bar"), "foo.foo().bar")
        self.assertStr(Name("a", prefix="b"), "ba")


klasa Test_Call(MacroTestCase):
    def _Call(self, name, args=Nic, prefix=Nic):
        """Help the next test"""
        children = []
        jeżeli isinstance(args, list):
            dla arg w args:
                children.append(arg)
                children.append(Comma())
            children.pop()
        zwróć Call(Name(name), children, prefix)

    def test(self):
        kids = [Nic,
                [Leaf(token.NUMBER, 1), Leaf(token.NUMBER, 2),
                 Leaf(token.NUMBER, 3)],
                [Leaf(token.NUMBER, 1), Leaf(token.NUMBER, 3),
                 Leaf(token.NUMBER, 2), Leaf(token.NUMBER, 4)],
                [Leaf(token.STRING, "b"), Leaf(token.STRING, "j", prefix=" ")]
                ]
        self.assertStr(self._Call("A"), "A()")
        self.assertStr(self._Call("b", kids[1]), "b(1,2,3)")
        self.assertStr(self._Call("a.b().c", kids[2]), "a.b().c(1,3,2,4)")
        self.assertStr(self._Call("d", kids[3], prefix=" "), " d(b, j)")


klasa Test_does_tree_import(support.TestCase):
    def _find_bind_rec(self, name, node):
        # Search a tree dla a binding -- used to find the starting
        # point dla these tests.
        c = fixer_util.find_binding(name, node)
        jeżeli c: zwróć c
        dla child w node.children:
            c = self._find_bind_rec(name, child)
            jeżeli c: zwróć c

    def does_tree_import(self, package, name, string):
        node = parse(string)
        # Find the binding of start -- that's what we'll go from
        node = self._find_bind_rec('start', node)
        zwróć fixer_util.does_tree_import(package, name, node)

    def try_with(self, string):
        failing_tests = (("a", "a", "z a zaimportuj b"),
                         ("a.d", "a", "z a.d zaimportuj b"),
                         ("d.a", "a", "z d.a zaimportuj b"),
                         (Nic, "a", "zaimportuj b"),
                         (Nic, "a", "zaimportuj b, c, d"))
        dla package, name, import_ w failing_tests:
            n = self.does_tree_import(package, name, import_ + "\n" + string)
            self.assertNieprawda(n)
            n = self.does_tree_import(package, name, string + "\n" + import_)
            self.assertNieprawda(n)

        dalejing_tests = (("a", "a", "z a zaimportuj a"),
                         ("x", "a", "z x zaimportuj a"),
                         ("x", "a", "z x zaimportuj b, c, a, d"),
                         ("x.b", "a", "z x.b zaimportuj a"),
                         ("x.b", "a", "z x.b zaimportuj b, c, a, d"),
                         (Nic, "a", "zaimportuj a"),
                         (Nic, "a", "zaimportuj b, c, a, d"))
        dla package, name, import_ w dalejing_tests:
            n = self.does_tree_import(package, name, import_ + "\n" + string)
            self.assertPrawda(n)
            n = self.does_tree_import(package, name, string + "\n" + import_)
            self.assertPrawda(n)

    def test_in_function(self):
        self.try_with("def foo():\n\tbar.baz()\n\tstart=3")

klasa Test_find_binding(support.TestCase):
    def find_binding(self, name, string, package=Nic):
        zwróć fixer_util.find_binding(name, parse(string), package)

    def test_simple_assignment(self):
        self.assertPrawda(self.find_binding("a", "a = b"))
        self.assertPrawda(self.find_binding("a", "a = [b, c, d]"))
        self.assertPrawda(self.find_binding("a", "a = foo()"))
        self.assertPrawda(self.find_binding("a", "a = foo().foo.foo[6][foo]"))
        self.assertNieprawda(self.find_binding("a", "foo = a"))
        self.assertNieprawda(self.find_binding("a", "foo = (a, b, c)"))

    def test_tuple_assignment(self):
        self.assertPrawda(self.find_binding("a", "(a,) = b"))
        self.assertPrawda(self.find_binding("a", "(a, b, c) = [b, c, d]"))
        self.assertPrawda(self.find_binding("a", "(c, (d, a), b) = foo()"))
        self.assertPrawda(self.find_binding("a", "(a, b) = foo().foo[6][foo]"))
        self.assertNieprawda(self.find_binding("a", "(foo, b) = (b, a)"))
        self.assertNieprawda(self.find_binding("a", "(foo, (b, c)) = (a, b, c)"))

    def test_list_assignment(self):
        self.assertPrawda(self.find_binding("a", "[a] = b"))
        self.assertPrawda(self.find_binding("a", "[a, b, c] = [b, c, d]"))
        self.assertPrawda(self.find_binding("a", "[c, [d, a], b] = foo()"))
        self.assertPrawda(self.find_binding("a", "[a, b] = foo().foo[a][foo]"))
        self.assertNieprawda(self.find_binding("a", "[foo, b] = (b, a)"))
        self.assertNieprawda(self.find_binding("a", "[foo, [b, c]] = (a, b, c)"))

    def test_invalid_assignments(self):
        self.assertNieprawda(self.find_binding("a", "foo.a = 5"))
        self.assertNieprawda(self.find_binding("a", "foo[a] = 5"))
        self.assertNieprawda(self.find_binding("a", "foo(a) = 5"))
        self.assertNieprawda(self.find_binding("a", "foo(a, b) = 5"))

    def test_simple_import(self):
        self.assertPrawda(self.find_binding("a", "zaimportuj a"))
        self.assertPrawda(self.find_binding("a", "zaimportuj b, c, a, d"))
        self.assertNieprawda(self.find_binding("a", "zaimportuj b"))
        self.assertNieprawda(self.find_binding("a", "zaimportuj b, c, d"))

    def test_from_import(self):
        self.assertPrawda(self.find_binding("a", "z x zaimportuj a"))
        self.assertPrawda(self.find_binding("a", "z a zaimportuj a"))
        self.assertPrawda(self.find_binding("a", "z x zaimportuj b, c, a, d"))
        self.assertPrawda(self.find_binding("a", "z x.b zaimportuj a"))
        self.assertPrawda(self.find_binding("a", "z x.b zaimportuj b, c, a, d"))
        self.assertNieprawda(self.find_binding("a", "z a zaimportuj b"))
        self.assertNieprawda(self.find_binding("a", "z a.d zaimportuj b"))
        self.assertNieprawda(self.find_binding("a", "z d.a zaimportuj b"))

    def test_import_as(self):
        self.assertPrawda(self.find_binding("a", "zaimportuj b jako a"))
        self.assertPrawda(self.find_binding("a", "zaimportuj b jako a, c, a jako f, d"))
        self.assertNieprawda(self.find_binding("a", "zaimportuj a jako f"))
        self.assertNieprawda(self.find_binding("a", "zaimportuj b, c jako f, d jako e"))

    def test_from_import_as(self):
        self.assertPrawda(self.find_binding("a", "z x zaimportuj b jako a"))
        self.assertPrawda(self.find_binding("a", "z x zaimportuj g jako a, d jako b"))
        self.assertPrawda(self.find_binding("a", "z x.b zaimportuj t jako a"))
        self.assertPrawda(self.find_binding("a", "z x.b zaimportuj g jako a, d"))
        self.assertNieprawda(self.find_binding("a", "z a zaimportuj b jako t"))
        self.assertNieprawda(self.find_binding("a", "z a.d zaimportuj b jako t"))
        self.assertNieprawda(self.find_binding("a", "z d.a zaimportuj b jako t"))

    def test_simple_import_with_package(self):
        self.assertPrawda(self.find_binding("b", "zaimportuj b"))
        self.assertPrawda(self.find_binding("b", "zaimportuj b, c, d"))
        self.assertNieprawda(self.find_binding("b", "zaimportuj b", "b"))
        self.assertNieprawda(self.find_binding("b", "zaimportuj b, c, d", "c"))

    def test_from_import_with_package(self):
        self.assertPrawda(self.find_binding("a", "z x zaimportuj a", "x"))
        self.assertPrawda(self.find_binding("a", "z a zaimportuj a", "a"))
        self.assertPrawda(self.find_binding("a", "z x zaimportuj *", "x"))
        self.assertPrawda(self.find_binding("a", "z x zaimportuj b, c, a, d", "x"))
        self.assertPrawda(self.find_binding("a", "z x.b zaimportuj a", "x.b"))
        self.assertPrawda(self.find_binding("a", "z x.b zaimportuj *", "x.b"))
        self.assertPrawda(self.find_binding("a", "z x.b zaimportuj b, c, a, d", "x.b"))
        self.assertNieprawda(self.find_binding("a", "z a zaimportuj b", "a"))
        self.assertNieprawda(self.find_binding("a", "z a.d zaimportuj b", "a.d"))
        self.assertNieprawda(self.find_binding("a", "z d.a zaimportuj b", "a.d"))
        self.assertNieprawda(self.find_binding("a", "z x.y zaimportuj *", "a.b"))

    def test_import_as_with_package(self):
        self.assertNieprawda(self.find_binding("a", "zaimportuj b.c jako a", "b.c"))
        self.assertNieprawda(self.find_binding("a", "zaimportuj a jako f", "f"))
        self.assertNieprawda(self.find_binding("a", "zaimportuj a jako f", "a"))

    def test_from_import_as_with_package(self):
        # Because it would take a lot of special-case code w the fixers
        # to deal przy z foo zaimportuj bar jako baz, we'll simply always
        # fail jeżeli there jest an "z ... zaimportuj ... jako ..."
        self.assertNieprawda(self.find_binding("a", "z x zaimportuj b jako a", "x"))
        self.assertNieprawda(self.find_binding("a", "z x zaimportuj g jako a, d jako b", "x"))
        self.assertNieprawda(self.find_binding("a", "z x.b zaimportuj t jako a", "x.b"))
        self.assertNieprawda(self.find_binding("a", "z x.b zaimportuj g jako a, d", "x.b"))
        self.assertNieprawda(self.find_binding("a", "z a zaimportuj b jako t", "a"))
        self.assertNieprawda(self.find_binding("a", "z a zaimportuj b jako t", "b"))
        self.assertNieprawda(self.find_binding("a", "z a zaimportuj b jako t", "t"))

    def test_function_def(self):
        self.assertPrawda(self.find_binding("a", "def a(): dalej"))
        self.assertPrawda(self.find_binding("a", "def a(b, c, d): dalej"))
        self.assertPrawda(self.find_binding("a", "def a(): b = 7"))
        self.assertNieprawda(self.find_binding("a", "def d(b, (c, a), e): dalej"))
        self.assertNieprawda(self.find_binding("a", "def d(a=7): dalej"))
        self.assertNieprawda(self.find_binding("a", "def d(a): dalej"))
        self.assertNieprawda(self.find_binding("a", "def d(): a = 7"))

        s = """
            def d():
                def a():
                    dalej"""
        self.assertNieprawda(self.find_binding("a", s))

    def test_class_def(self):
        self.assertPrawda(self.find_binding("a", "class a: dalej"))
        self.assertPrawda(self.find_binding("a", "class a(): dalej"))
        self.assertPrawda(self.find_binding("a", "class a(b): dalej"))
        self.assertPrawda(self.find_binding("a", "class a(b, c=8): dalej"))
        self.assertNieprawda(self.find_binding("a", "class d: dalej"))
        self.assertNieprawda(self.find_binding("a", "class d(a): dalej"))
        self.assertNieprawda(self.find_binding("a", "class d(b, a=7): dalej"))
        self.assertNieprawda(self.find_binding("a", "class d(b, *a): dalej"))
        self.assertNieprawda(self.find_binding("a", "class d(b, **a): dalej"))
        self.assertNieprawda(self.find_binding("a", "class d: a = 7"))

        s = """
            klasa d():
                klasa a():
                    dalej"""
        self.assertNieprawda(self.find_binding("a", s))

    def test_for(self):
        self.assertPrawda(self.find_binding("a", "dla a w r: dalej"))
        self.assertPrawda(self.find_binding("a", "dla a, b w r: dalej"))
        self.assertPrawda(self.find_binding("a", "dla (a, b) w r: dalej"))
        self.assertPrawda(self.find_binding("a", "dla c, (a,) w r: dalej"))
        self.assertPrawda(self.find_binding("a", "dla c, (a, b) w r: dalej"))
        self.assertPrawda(self.find_binding("a", "dla c w r: a = c"))
        self.assertNieprawda(self.find_binding("a", "dla c w a: dalej"))

    def test_for_nested(self):
        s = """
            dla b w r:
                dla a w b:
                    dalej"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            dla b w r:
                dla a, c w b:
                    dalej"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            dla b w r:
                dla (a, c) w b:
                    dalej"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            dla b w r:
                dla (a,) w b:
                    dalej"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            dla b w r:
                dla c, (a, d) w b:
                    dalej"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            dla b w r:
                dla c w b:
                    a = 7"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            dla b w r:
                dla c w b:
                    d = a"""
        self.assertNieprawda(self.find_binding("a", s))

        s = """
            dla b w r:
                dla c w a:
                    d = 7"""
        self.assertNieprawda(self.find_binding("a", s))

    def test_if(self):
        self.assertPrawda(self.find_binding("a", "jeżeli b w r: a = c"))
        self.assertNieprawda(self.find_binding("a", "jeżeli a w r: d = e"))

    def test_if_nested(self):
        s = """
            jeżeli b w r:
                jeżeli c w d:
                    a = c"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            jeżeli b w r:
                jeżeli c w d:
                    c = a"""
        self.assertNieprawda(self.find_binding("a", s))

    def test_while(self):
        self.assertPrawda(self.find_binding("a", "dopóki b w r: a = c"))
        self.assertNieprawda(self.find_binding("a", "dopóki a w r: d = e"))

    def test_while_nested(self):
        s = """
            dopóki b w r:
                dopóki c w d:
                    a = c"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            dopóki b w r:
                dopóki c w d:
                    c = a"""
        self.assertNieprawda(self.find_binding("a", s))

    def test_try_except(self):
        s = """
            spróbuj:
                a = 6
            wyjąwszy:
                b = 8"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            wyjąwszy:
                a = 6"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            wyjąwszy KeyError:
                dalej
            wyjąwszy:
                a = 6"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            wyjąwszy:
                b = 6"""
        self.assertNieprawda(self.find_binding("a", s))

    def test_try_except_nested(self):
        s = """
            spróbuj:
                spróbuj:
                    a = 6
                wyjąwszy:
                    dalej
            wyjąwszy:
                b = 8"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            wyjąwszy:
                spróbuj:
                    a = 6
                wyjąwszy:
                    dalej"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            wyjąwszy:
                spróbuj:
                    dalej
                wyjąwszy:
                    a = 6"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                spróbuj:
                    b = 8
                wyjąwszy KeyError:
                    dalej
                wyjąwszy:
                    a = 6
            wyjąwszy:
                dalej"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                dalej
            wyjąwszy:
                spróbuj:
                    b = 8
                wyjąwszy KeyError:
                    dalej
                wyjąwszy:
                    a = 6"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            wyjąwszy:
                b = 6"""
        self.assertNieprawda(self.find_binding("a", s))

        s = """
            spróbuj:
                spróbuj:
                    b = 8
                wyjąwszy:
                    c = d
            wyjąwszy:
                spróbuj:
                    b = 6
                wyjąwszy:
                    t = 8
                wyjąwszy:
                    o = y"""
        self.assertNieprawda(self.find_binding("a", s))

    def test_try_except_finally(self):
        s = """
            spróbuj:
                c = 6
            wyjąwszy:
                b = 8
            w_końcu:
                a = 9"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            w_końcu:
                a = 6"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            w_końcu:
                b = 6"""
        self.assertNieprawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            wyjąwszy:
                b = 9
            w_końcu:
                b = 6"""
        self.assertNieprawda(self.find_binding("a", s))

    def test_try_except_finally_nested(self):
        s = """
            spróbuj:
                c = 6
            wyjąwszy:
                b = 8
            w_końcu:
                spróbuj:
                    a = 9
                wyjąwszy:
                    b = 9
                w_końcu:
                    c = 9"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            w_końcu:
                spróbuj:
                    dalej
                w_końcu:
                    a = 6"""
        self.assertPrawda(self.find_binding("a", s))

        s = """
            spróbuj:
                b = 8
            w_końcu:
                spróbuj:
                    b = 6
                w_końcu:
                    b = 7"""
        self.assertNieprawda(self.find_binding("a", s))

klasa Test_touch_import(support.TestCase):

    def test_after_docstring(self):
        node = parse('"""foo"""\nbar()')
        fixer_util.touch_import(Nic, "foo", node)
        self.assertEqual(str(node), '"""foo"""\nzaimportuj foo\nbar()\n\n')

    def test_after_imports(self):
        node = parse('"""foo"""\nzaimportuj bar\nbar()')
        fixer_util.touch_import(Nic, "foo", node)
        self.assertEqual(str(node), '"""foo"""\nzaimportuj bar\nzaimportuj foo\nbar()\n\n')

    def test_beginning(self):
        node = parse('bar()')
        fixer_util.touch_import(Nic, "foo", node)
        self.assertEqual(str(node), 'zaimportuj foo\nbar()\n\n')

    def test_from_import(self):
        node = parse('bar()')
        fixer_util.touch_import("html", "escape", node)
        self.assertEqual(str(node), 'z html zaimportuj escape\nbar()\n\n')

    def test_name_import(self):
        node = parse('bar()')
        fixer_util.touch_import(Nic, "cgi", node)
        self.assertEqual(str(node), 'zaimportuj cgi\nbar()\n\n')

klasa Test_find_indentation(support.TestCase):

    def test_nothing(self):
        fi = fixer_util.find_indentation
        node = parse("node()")
        self.assertEqual(fi(node), "")
        node = parse("")
        self.assertEqual(fi(node), "")

    def test_simple(self):
        fi = fixer_util.find_indentation
        node = parse("def f():\n    x()")
        self.assertEqual(fi(node), "")
        self.assertEqual(fi(node.children[0].children[4].children[2]), "    ")
        node = parse("def f():\n    x()\n    y()")
        self.assertEqual(fi(node.children[0].children[4].children[4]), "    ")
