"""
Test the API of the symtable module.
"""
zaimportuj symtable
zaimportuj unittest



TEST_CODE = """
zaimportuj sys

glob = 42

klasa Mine:
    instance_var = 24
    def a_method(p1, p2):
        dalej

def spam(a, b, *var, **kw):
    global bar
    bar = 47
    x = 23
    glob
    def internal():
        zwróć x
    zwróć internal

def foo():
    dalej

def namespace_test(): dalej
def namespace_test(): dalej
"""


def find_block(block, name):
    dla ch w block.get_children():
        jeżeli ch.get_name() == name:
            zwróć ch


klasa SymtableTest(unittest.TestCase):

    top = symtable.symtable(TEST_CODE, "?", "exec")
    # These correspond to scopes w TEST_CODE
    Mine = find_block(top, "Mine")
    a_method = find_block(Mine, "a_method")
    spam = find_block(top, "spam")
    internal = find_block(spam, "internal")
    foo = find_block(top, "foo")

    def test_type(self):
        self.assertEqual(self.top.get_type(), "module")
        self.assertEqual(self.Mine.get_type(), "class")
        self.assertEqual(self.a_method.get_type(), "function")
        self.assertEqual(self.spam.get_type(), "function")
        self.assertEqual(self.internal.get_type(), "function")

    def test_optimized(self):
        self.assertNieprawda(self.top.is_optimized())
        self.assertNieprawda(self.top.has_exec())

        self.assertPrawda(self.spam.is_optimized())

    def test_nested(self):
        self.assertNieprawda(self.top.is_nested())
        self.assertNieprawda(self.Mine.is_nested())
        self.assertNieprawda(self.spam.is_nested())
        self.assertPrawda(self.internal.is_nested())

    def test_children(self):
        self.assertPrawda(self.top.has_children())
        self.assertPrawda(self.Mine.has_children())
        self.assertNieprawda(self.foo.has_children())

    def test_lineno(self):
        self.assertEqual(self.top.get_lineno(), 0)
        self.assertEqual(self.spam.get_lineno(), 11)

    def test_function_info(self):
        func = self.spam
        self.assertEqual(sorted(func.get_parameters()), ["a", "b", "kw", "var"])
        expected = ["a", "b", "internal", "kw", "var", "x"]
        self.assertEqual(sorted(func.get_locals()), expected)
        self.assertEqual(sorted(func.get_globals()), ["bar", "glob"])
        self.assertEqual(self.internal.get_frees(), ("x",))

    def test_globals(self):
        self.assertPrawda(self.spam.lookup("glob").is_global())
        self.assertNieprawda(self.spam.lookup("glob").is_declared_global())
        self.assertPrawda(self.spam.lookup("bar").is_global())
        self.assertPrawda(self.spam.lookup("bar").is_declared_global())
        self.assertNieprawda(self.internal.lookup("x").is_global())
        self.assertNieprawda(self.Mine.lookup("instance_var").is_global())

    def test_local(self):
        self.assertPrawda(self.spam.lookup("x").is_local())
        self.assertNieprawda(self.internal.lookup("x").is_local())

    def test_referenced(self):
        self.assertPrawda(self.internal.lookup("x").is_referenced())
        self.assertPrawda(self.spam.lookup("internal").is_referenced())
        self.assertNieprawda(self.spam.lookup("x").is_referenced())

    def test_parameters(self):
        dla sym w ("a", "var", "kw"):
            self.assertPrawda(self.spam.lookup(sym).is_parameter())
        self.assertNieprawda(self.spam.lookup("x").is_parameter())

    def test_symbol_lookup(self):
        self.assertEqual(len(self.top.get_identifiers()),
                         len(self.top.get_symbols()))

        self.assertRaises(KeyError, self.top.lookup, "not_here")

    def test_namespaces(self):
        self.assertPrawda(self.top.lookup("Mine").is_namespace())
        self.assertPrawda(self.Mine.lookup("a_method").is_namespace())
        self.assertPrawda(self.top.lookup("spam").is_namespace())
        self.assertPrawda(self.spam.lookup("internal").is_namespace())
        self.assertPrawda(self.top.lookup("namespace_test").is_namespace())
        self.assertNieprawda(self.spam.lookup("x").is_namespace())

        self.assertPrawda(self.top.lookup("spam").get_namespace() jest self.spam)
        ns_test = self.top.lookup("namespace_test")
        self.assertEqual(len(ns_test.get_namespaces()), 2)
        self.assertRaises(ValueError, ns_test.get_namespace)

    def test_assigned(self):
        self.assertPrawda(self.spam.lookup("x").is_assigned())
        self.assertPrawda(self.spam.lookup("bar").is_assigned())
        self.assertPrawda(self.top.lookup("spam").is_assigned())
        self.assertPrawda(self.Mine.lookup("a_method").is_assigned())
        self.assertNieprawda(self.internal.lookup("x").is_assigned())

    def test_imported(self):
        self.assertPrawda(self.top.lookup("sys").is_imported())

    def test_name(self):
        self.assertEqual(self.top.get_name(), "top")
        self.assertEqual(self.spam.get_name(), "spam")
        self.assertEqual(self.spam.lookup("x").get_name(), "x")
        self.assertEqual(self.Mine.get_name(), "Mine")

    def test_class_info(self):
        self.assertEqual(self.Mine.get_methods(), ('a_method',))

    def test_filename_correct(self):
        ### Bug tickler: SyntaxError file name correct whether error podnieśd
        ### dopóki parsing albo building symbol table.
        def checkfilename(brokencode):
            spróbuj:
                symtable.symtable(brokencode, "spam", "exec")
            wyjąwszy SyntaxError jako e:
                self.assertEqual(e.filename, "spam")
            inaczej:
                self.fail("no SyntaxError dla %r" % (brokencode,))
        checkfilename("def f(x): foo)(")  # parse-time
        checkfilename("def f(x): global x")  # symtable-build-time

    def test_eval(self):
        symbols = symtable.symtable("42", "?", "eval")

    def test_single(self):
        symbols = symtable.symtable("42", "?", "single")

    def test_exec(self):
        symbols = symtable.symtable("def f(x): zwróć x", "?", "exec")


jeżeli __name__ == '__main__':
    unittest.main()
