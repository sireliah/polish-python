"""Tests dla the unparse.py script w the Tools/parser directory."""

zaimportuj unittest
zaimportuj test.support
zaimportuj io
zaimportuj os
zaimportuj random
zaimportuj tokenize
zaimportuj ast

z test.test_tools zaimportuj basepath, toolsdir, skip_if_missing

skip_if_missing()

parser_path = os.path.join(toolsdir, "parser")

przy test.support.DirsOnSysPath(parser_path):
    zaimportuj unparse

def read_pyfile(filename):
    """Read oraz zwróć the contents of a Python source file (as a
    string), taking into account the file encoding."""
    przy open(filename, "rb") jako pyfile:
        encoding = tokenize.detect_encoding(pyfile.readline)[0]
    przy open(filename, "r", encoding=encoding) jako pyfile:
        source = pyfile.read()
    zwróć source

for_inaczej = """\
def f():
    dla x w range(10):
        przerwij
    inaczej:
        y = 2
    z = 3
"""

while_inaczej = """\
def g():
    dopóki Prawda:
        przerwij
    inaczej:
        y = 2
    z = 3
"""

relative_zaimportuj = """\
z . zaimportuj fred
z .. zaimportuj barney
z .australia zaimportuj shrimp jako prawns
"""

nonlocal_ex = """\
def f():
    x = 1
    def g():
        nonlocal x
        x = 2
        y = 7
        def h():
            nonlocal x, y
"""

# also acts jako test dla 'wyjąwszy ... jako ...'
raise_z = """\
spróbuj:
    1 / 0
wyjąwszy ZeroDivisionError jako e:
    podnieś ArithmeticError z e
"""

class_decorator = """\
@f1(arg)
@f2
klasa Foo: dalej
"""

elif1 = """\
jeżeli cond1:
    suite1
albo_inaczej cond2:
    suite2
inaczej:
    suite3
"""

elif2 = """\
jeżeli cond1:
    suite1
albo_inaczej cond2:
    suite2
"""

try_except_finally = """\
spróbuj:
    suite1
wyjąwszy ex1:
    suite2
wyjąwszy ex2:
    suite3
inaczej:
    suite4
w_końcu:
    suite5
"""

with_simple = """\
przy f():
    suite1
"""

with_as = """\
przy f() jako x:
    suite1
"""

with_two_items = """\
przy f() jako x, g() jako y:
    suite1
"""

klasa ASTTestCase(unittest.TestCase):
    def assertASTEqual(self, ast1, ast2):
        self.assertEqual(ast.dump(ast1), ast.dump(ast2))

    def check_roundtrip(self, code1, filename="internal"):
        ast1 = compile(code1, filename, "exec", ast.PyCF_ONLY_AST)
        unparse_buffer = io.StringIO()
        unparse.Unparser(ast1, unparse_buffer)
        code2 = unparse_buffer.getvalue()
        ast2 = compile(code2, filename, "exec", ast.PyCF_ONLY_AST)
        self.assertASTEqual(ast1, ast2)

klasa UnparseTestCase(ASTTestCase):
    # Tests dla specific bugs found w earlier versions of unparse

    def test_del_statement(self):
        self.check_roundtrip("usuń x, y, z")

    def test_shifts(self):
        self.check_roundtrip("45 << 2")
        self.check_roundtrip("13 >> 7")

    def test_for_inaczej(self):
        self.check_roundtrip(for_inaczej)

    def test_while_inaczej(self):
        self.check_roundtrip(while_inaczej)

    def test_unary_parens(self):
        self.check_roundtrip("(-1)**7")
        self.check_roundtrip("(-1.)**8")
        self.check_roundtrip("(-1j)**6")
        self.check_roundtrip("not Prawda albo Nieprawda")
        self.check_roundtrip("Prawda albo nie Nieprawda")

    def test_integer_parens(self):
        self.check_roundtrip("3 .__abs__()")

    def test_huge_float(self):
        self.check_roundtrip("1e1000")
        self.check_roundtrip("-1e1000")
        self.check_roundtrip("1e1000j")
        self.check_roundtrip("-1e1000j")

    def test_min_int(self):
        self.check_roundtrip(str(-2**31))
        self.check_roundtrip(str(-2**63))

    def test_imaginary_literals(self):
        self.check_roundtrip("7j")
        self.check_roundtrip("-7j")
        self.check_roundtrip("0j")
        self.check_roundtrip("-0j")

    def test_lambda_parentheses(self):
        self.check_roundtrip("(lambda: int)()")

    def test_chained_comparisons(self):
        self.check_roundtrip("1 < 4 <= 5")
        self.check_roundtrip("a jest b jest c jest nie d")

    def test_function_arguments(self):
        self.check_roundtrip("def f(): dalej")
        self.check_roundtrip("def f(a): dalej")
        self.check_roundtrip("def f(b = 2): dalej")
        self.check_roundtrip("def f(a, b): dalej")
        self.check_roundtrip("def f(a, b = 2): dalej")
        self.check_roundtrip("def f(a = 5, b = 2): dalej")
        self.check_roundtrip("def f(*, a = 1, b = 2): dalej")
        self.check_roundtrip("def f(*, a = 1, b): dalej")
        self.check_roundtrip("def f(*, a, b = 2): dalej")
        self.check_roundtrip("def f(a, b = Nic, *, c, **kwds): dalej")
        self.check_roundtrip("def f(a=2, *args, c=5, d, **kwds): dalej")
        self.check_roundtrip("def f(*args, **kwargs): dalej")

    def test_relative_import(self):
        self.check_roundtrip(relative_import)

    def test_nonlocal(self):
        self.check_roundtrip(nonlocal_ex)

    def test_raise_from(self):
        self.check_roundtrip(raise_from)

    def test_bytes(self):
        self.check_roundtrip("b'123'")

    def test_annotations(self):
        self.check_roundtrip("def f(a : int): dalej")
        self.check_roundtrip("def f(a: int = 5): dalej")
        self.check_roundtrip("def f(*args: [int]): dalej")
        self.check_roundtrip("def f(**kwargs: dict): dalej")
        self.check_roundtrip("def f() -> Nic: dalej")

    def test_set_literal(self):
        self.check_roundtrip("{'a', 'b', 'c'}")

    def test_set_comprehension(self):
        self.check_roundtrip("{x dla x w range(5)}")

    def test_dict_comprehension(self):
        self.check_roundtrip("{x: x*x dla x w range(10)}")

    def test_class_decorators(self):
        self.check_roundtrip(class_decorator)

    def test_class_definition(self):
        self.check_roundtrip("class A(metaclass=type, *[], **{}): dalej")

    def test_elifs(self):
        self.check_roundtrip(elif1)
        self.check_roundtrip(elif2)

    def test_try_except_finally(self):
        self.check_roundtrip(try_except_finally)

    def test_starred_assignment(self):
        self.check_roundtrip("a, *b, c = seq")
        self.check_roundtrip("a, (*b, c) = seq")
        self.check_roundtrip("a, *b[0], c = seq")
        self.check_roundtrip("a, *(b, c) = seq")

    def test_with_simple(self):
        self.check_roundtrip(with_simple)

    def test_with_as(self):
        self.check_roundtrip(with_as)

    def test_with_two_items(self):
        self.check_roundtrip(with_two_items)


klasa DirectoryTestCase(ASTTestCase):
    """Test roundtrip behaviour on all files w Lib oraz Lib/test."""

    # test directories, relative to the root of the distribution
    test_directories = 'Lib', os.path.join('Lib', 'test')

    def test_files(self):
        # get names of files to test

        names = []
        dla d w self.test_directories:
            test_dir = os.path.join(basepath, d)
            dla n w os.listdir(test_dir):
                jeżeli n.endswith('.py') oraz nie n.startswith('bad'):
                    names.append(os.path.join(test_dir, n))

        # Test limited subset of files unless the 'cpu' resource jest specified.
        jeżeli nie test.support.is_resource_enabled("cpu"):
            names = random.sample(names, 10)

        dla filename w names:
            jeżeli test.support.verbose:
                print('Testing %s' % filename)
            source = read_pyfile(filename)
            self.check_roundtrip(source)


jeżeli __name__ == '__main__':
    unittest.main()
