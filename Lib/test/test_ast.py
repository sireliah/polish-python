zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj ast
zaimportuj weakref

z test zaimportuj support

def to_tuple(t):
    jeżeli t jest Nic albo isinstance(t, (str, int, complex)):
        zwróć t
    albo_inaczej isinstance(t, list):
        zwróć [to_tuple(e) dla e w t]
    result = [t.__class__.__name__]
    jeżeli hasattr(t, 'lineno') oraz hasattr(t, 'col_offset'):
        result.append((t.lineno, t.col_offset))
    jeżeli t._fields jest Nic:
        zwróć tuple(result)
    dla f w t._fields:
        result.append(to_tuple(getattr(t, f)))
    zwróć tuple(result)


# These tests are compiled through "exec"
# There should be at least one test per statement
exec_tests = [
    # Nic
    "Nic",
    # FunctionDef
    "def f(): dalej",
    # FunctionDef przy arg
    "def f(a): dalej",
    # FunctionDef przy arg oraz default value
    "def f(a=0): dalej",
    # FunctionDef przy varargs
    "def f(*args): dalej",
    # FunctionDef przy kwargs
    "def f(**kwargs): dalej",
    # FunctionDef przy all kind of args
    "def f(a, b=1, c=Nic, d=[], e={}, *args, f=42, **kwargs): dalej",
    # ClassDef
    "class C:pass",
    # ClassDef, new style class
    "class C(object): dalej",
    # Return
    "def f():return 1",
    # Delete
    "usuń v",
    # Assign
    "v = 1",
    # AugAssign
    "v += 1",
    # For
    "dla v w v:pass",
    # While
    "dopóki v:pass",
    # If
    "jeżeli v:pass",
    # With
    "przy x jako y: dalej",
    "przy x jako y, z jako q: dalej",
    # Raise
    "raise Exception('string')",
    # TryExcept
    "spróbuj:\n  dalej\nwyjąwszy Exception:\n  dalej",
    # TryFinally
    "spróbuj:\n  dalej\nw_końcu:\n  dalej",
    # Assert
    "assert v",
    # Import
    "zaimportuj sys",
    # ImportFrom
    "z sys zaimportuj v",
    # Global
    "global v",
    # Expr
    "1",
    # Pass,
    "pass",
    # Break
    "dla v w v:break",
    # Continue
    "dla v w v:continue",
    # dla statements przy naked tuples (see http://bugs.python.org/issue6704)
    "dla a,b w c: dalej",
    "[(a,b) dla a,b w c]",
    "((a,b) dla a,b w c)",
    "((a,b) dla (a,b) w c)",
    # Multiline generator expression (test dla .lineno & .col_offset)
    """(
    (
    Aa
    ,
       Bb
    )
    for
    Aa
    ,
    Bb w Cc
    )""",
    # dictcomp
    "{a : b dla w w x dla m w p jeżeli g}",
    # dictcomp przy naked tuple
    "{a : b dla v,w w x}",
    # setcomp
    "{r dla l w x jeżeli g}",
    # setcomp przy naked tuple
    "{r dla l,m w x}",
    # AsyncFunctionDef
    "async def f():\n await something()",
    # AsyncFor
    "async def f():\n async dla e w i: 1\n inaczej: 2",
    # AsyncWith
    "async def f():\n async przy a jako b: 1",
    # PEP 448: Additional Unpacking Generalizations
    "{**{1:2}, 2:3}",
    "{*{1, 2}, 3}",
]

# These are compiled through "single"
# because of overlap przy "eval", it just tests what
# can't be tested przy "eval"
single_tests = [
    "1+2"
]

# These are compiled through "eval"
# It should test all expressions
eval_tests = [
  # Nic
  "Nic",
  # BoolOp
  "a oraz b",
  # BinOp
  "a + b",
  # UnaryOp
  "not v",
  # Lambda
  "lambda:Nic",
  # Dict
  "{ 1:2 }",
  # Empty dict
  "{}",
  # Set
  "{Nic,}",
  # Multiline dict (test dla .lineno & .col_offset)
  """{
      1
        :
          2
     }""",
  # ListComp
  "[a dla b w c jeżeli d]",
  # GeneratorExp
  "(a dla b w c jeżeli d)",
  # Yield - uzyskaj expressions can't work outside a function
  #
  # Compare
  "1 < 2 < 3",
  # Call
  "f(1,2,c=3,*d,**e)",
  # Num
  "10",
  # Str
  "'string'",
  # Attribute
  "a.b",
  # Subscript
  "a[b:c]",
  # Name
  "v",
  # List
  "[1,2,3]",
  # Empty list
  "[]",
  # Tuple
  "1,2,3",
  # Tuple
  "(1,2,3)",
  # Empty tuple
  "()",
  # Combination
  "a.b.c.d(a.b[1:2])",

]

# TODO: expr_context, slice, boolop, operator, unaryop, cmpop, comprehension
# excepthandler, arguments, keywords, alias

klasa AST_Tests(unittest.TestCase):

    def _assertPrawdaorder(self, ast_node, parent_pos):
        jeżeli nie isinstance(ast_node, ast.AST) albo ast_node._fields jest Nic:
            zwróć
        jeżeli isinstance(ast_node, (ast.expr, ast.stmt, ast.excepthandler)):
            node_pos = (ast_node.lineno, ast_node.col_offset)
            self.assertPrawda(node_pos >= parent_pos)
            parent_pos = (ast_node.lineno, ast_node.col_offset)
        dla name w ast_node._fields:
            value = getattr(ast_node, name)
            jeżeli isinstance(value, list):
                dla child w value:
                    self._assertPrawdaorder(child, parent_pos)
            albo_inaczej value jest nie Nic:
                self._assertPrawdaorder(value, parent_pos)

    def test_AST_objects(self):
        x = ast.AST()
        self.assertEqual(x._fields, ())
        x.foobar = 42
        self.assertEqual(x.foobar, 42)
        self.assertEqual(x.__dict__["foobar"], 42)

        przy self.assertRaises(AttributeError):
            x.vararg

        przy self.assertRaises(TypeError):
            # "_ast.AST constructor takes 0 positional arguments"
            ast.AST(2)

    def test_AST_garbage_collection(self):
        klasa X:
            dalej
        a = ast.AST()
        a.x = X()
        a.x.a = a
        ref = weakref.ref(a.x)
        usuń a
        support.gc_collect()
        self.assertIsNic(ref())

    def test_snippets(self):
        dla input, output, kind w ((exec_tests, exec_results, "exec"),
                                    (single_tests, single_results, "single"),
                                    (eval_tests, eval_results, "eval")):
            dla i, o w zip(input, output):
                przy self.subTest(action="parsing", input=i):
                    ast_tree = compile(i, "?", kind, ast.PyCF_ONLY_AST)
                    self.assertEqual(to_tuple(ast_tree), o)
                    self._assertPrawdaorder(ast_tree, (0, 0))
                przy self.subTest(action="compiling", input=i):
                    compile(ast_tree, "?", kind)

    def test_slice(self):
        slc = ast.parse("x[::]").body[0].value.slice
        self.assertIsNic(slc.upper)
        self.assertIsNic(slc.lower)
        self.assertIsNic(slc.step)

    def test_from_import(self):
        im = ast.parse("z . zaimportuj y").body[0]
        self.assertIsNic(im.module)

    def test_non_interned_future_from_ast(self):
        mod = ast.parse("z __future__ zaimportuj division")
        self.assertIsInstance(mod.body[0], ast.ImportFrom)
        mod.body[0].module = " __future__ ".strip()
        compile(mod, "<test>", "exec")

    def test_base_classes(self):
        self.assertPrawda(issubclass(ast.For, ast.stmt))
        self.assertPrawda(issubclass(ast.Name, ast.expr))
        self.assertPrawda(issubclass(ast.stmt, ast.AST))
        self.assertPrawda(issubclass(ast.expr, ast.AST))
        self.assertPrawda(issubclass(ast.comprehension, ast.AST))
        self.assertPrawda(issubclass(ast.Gt, ast.AST))

    def test_field_attr_existence(self):
        dla name, item w ast.__dict__.items():
            jeżeli isinstance(item, type) oraz name != 'AST' oraz name[0].isupper():
                x = item()
                jeżeli isinstance(x, ast.AST):
                    self.assertEqual(type(x._fields), tuple)

    def test_arguments(self):
        x = ast.arguments()
        self.assertEqual(x._fields, ('args', 'vararg', 'kwonlyargs',
                                      'kw_defaults', 'kwarg', 'defaults'))

        przy self.assertRaises(AttributeError):
            x.vararg

        x = ast.arguments(*range(1, 7))
        self.assertEqual(x.vararg, 2)

    def test_field_attr_writable(self):
        x = ast.Num()
        # We can assign to _fields
        x._fields = 666
        self.assertEqual(x._fields, 666)

    def test_classattrs(self):
        x = ast.Num()
        self.assertEqual(x._fields, ('n',))

        przy self.assertRaises(AttributeError):
            x.n

        x = ast.Num(42)
        self.assertEqual(x.n, 42)

        przy self.assertRaises(AttributeError):
            x.lineno

        przy self.assertRaises(AttributeError):
            x.foobar

        x = ast.Num(lineno=2)
        self.assertEqual(x.lineno, 2)

        x = ast.Num(42, lineno=0)
        self.assertEqual(x.lineno, 0)
        self.assertEqual(x._fields, ('n',))
        self.assertEqual(x.n, 42)

        self.assertRaises(TypeError, ast.Num, 1, 2)
        self.assertRaises(TypeError, ast.Num, 1, 2, lineno=0)

    def test_module(self):
        body = [ast.Num(42)]
        x = ast.Module(body)
        self.assertEqual(x.body, body)

    def test_nodeclasses(self):
        # Zero arguments constructor explicitly allowed
        x = ast.BinOp()
        self.assertEqual(x._fields, ('left', 'op', 'right'))

        # Random attribute allowed too
        x.foobarbaz = 5
        self.assertEqual(x.foobarbaz, 5)

        n1 = ast.Num(1)
        n3 = ast.Num(3)
        addop = ast.Add()
        x = ast.BinOp(n1, addop, n3)
        self.assertEqual(x.left, n1)
        self.assertEqual(x.op, addop)
        self.assertEqual(x.right, n3)

        x = ast.BinOp(1, 2, 3)
        self.assertEqual(x.left, 1)
        self.assertEqual(x.op, 2)
        self.assertEqual(x.right, 3)

        x = ast.BinOp(1, 2, 3, lineno=0)
        self.assertEqual(x.left, 1)
        self.assertEqual(x.op, 2)
        self.assertEqual(x.right, 3)
        self.assertEqual(x.lineno, 0)

        # node podnieśs exception when nie given enough arguments
        self.assertRaises(TypeError, ast.BinOp, 1, 2)
        # node podnieśs exception when given too many arguments
        self.assertRaises(TypeError, ast.BinOp, 1, 2, 3, 4)
        # node podnieśs exception when nie given enough arguments
        self.assertRaises(TypeError, ast.BinOp, 1, 2, lineno=0)
        # node podnieśs exception when given too many arguments
        self.assertRaises(TypeError, ast.BinOp, 1, 2, 3, 4, lineno=0)

        # can set attributes through kwargs too
        x = ast.BinOp(left=1, op=2, right=3, lineno=0)
        self.assertEqual(x.left, 1)
        self.assertEqual(x.op, 2)
        self.assertEqual(x.right, 3)
        self.assertEqual(x.lineno, 0)

        # Random kwargs also allowed
        x = ast.BinOp(1, 2, 3, foobarbaz=42)
        self.assertEqual(x.foobarbaz, 42)

    def test_no_fields(self):
        # this used to fail because Sub._fields was Nic
        x = ast.Sub()
        self.assertEqual(x._fields, ())

    def test_pickling(self):
        zaimportuj pickle
        mods = [pickle]
        spróbuj:
            zaimportuj cPickle
            mods.append(cPickle)
        wyjąwszy ImportError:
            dalej
        protocols = [0, 1, 2]
        dla mod w mods:
            dla protocol w protocols:
                dla ast w (compile(i, "?", "exec", 0x400) dla i w exec_tests):
                    ast2 = mod.loads(mod.dumps(ast, protocol))
                    self.assertEqual(to_tuple(ast2), to_tuple(ast))

    def test_invalid_sum(self):
        pos = dict(lineno=2, col_offset=3)
        m = ast.Module([ast.Expr(ast.expr(**pos), **pos)])
        przy self.assertRaises(TypeError) jako cm:
            compile(m, "<test>", "exec")
        self.assertIn("but got <_ast.expr", str(cm.exception))

    def test_invalid_identitifer(self):
        m = ast.Module([ast.Expr(ast.Name(42, ast.Load()))])
        ast.fix_missing_locations(m)
        przy self.assertRaises(TypeError) jako cm:
            compile(m, "<test>", "exec")
        self.assertIn("identifier must be of type str", str(cm.exception))

    def test_invalid_string(self):
        m = ast.Module([ast.Expr(ast.Str(42))])
        ast.fix_missing_locations(m)
        przy self.assertRaises(TypeError) jako cm:
            compile(m, "<test>", "exec")
        self.assertIn("string must be of type str", str(cm.exception))

    def test_empty_uzyskaj_from(self):
        # Issue 16546: uzyskaj z value jest nie optional.
        empty_uzyskaj_z = ast.parse("def f():\n uzyskaj z g()")
        empty_uzyskaj_from.body[0].body[0].value.value = Nic
        przy self.assertRaises(ValueError) jako cm:
            compile(empty_uzyskaj_from, "<test>", "exec")
        self.assertIn("field value jest required", str(cm.exception))


klasa ASTHelpers_Test(unittest.TestCase):

    def test_parse(self):
        a = ast.parse('foo(1 + 1)')
        b = compile('foo(1 + 1)', '<unknown>', 'exec', ast.PyCF_ONLY_AST)
        self.assertEqual(ast.dump(a), ast.dump(b))

    def test_parse_in_error(self):
        spróbuj:
            1/0
        wyjąwszy Exception:
            przy self.assertRaises(SyntaxError) jako e:
                ast.literal_eval(r"'\U'")
            self.assertIsNotNic(e.exception.__context__)

    def test_dump(self):
        node = ast.parse('spam(eggs, "and cheese")')
        self.assertEqual(ast.dump(node),
            "Module(body=[Expr(value=Call(func=Name(id='spam', ctx=Load()), "
            "args=[Name(id='eggs', ctx=Load()), Str(s='and cheese')], "
            "keywords=[]))])"
        )
        self.assertEqual(ast.dump(node, annotate_fields=Nieprawda),
            "Module([Expr(Call(Name('spam', Load()), [Name('eggs', Load()), "
            "Str('and cheese')], []))])"
        )
        self.assertEqual(ast.dump(node, include_attributes=Prawda),
            "Module(body=[Expr(value=Call(func=Name(id='spam', ctx=Load(), "
            "lineno=1, col_offset=0), args=[Name(id='eggs', ctx=Load(), "
            "lineno=1, col_offset=5), Str(s='and cheese', lineno=1, "
            "col_offset=11)], keywords=[], "
            "lineno=1, col_offset=0), lineno=1, col_offset=0)])"
        )

    def test_copy_location(self):
        src = ast.parse('1 + 1', mode='eval')
        src.body.right = ast.copy_location(ast.Num(2), src.body.right)
        self.assertEqual(ast.dump(src, include_attributes=Prawda),
            'Expression(body=BinOp(left=Num(n=1, lineno=1, col_offset=0), '
            'op=Add(), right=Num(n=2, lineno=1, col_offset=4), lineno=1, '
            'col_offset=0))'
        )

    def test_fix_missing_locations(self):
        src = ast.parse('write("spam")')
        src.body.append(ast.Expr(ast.Call(ast.Name('spam', ast.Load()),
                                          [ast.Str('eggs')], [])))
        self.assertEqual(src, ast.fix_missing_locations(src))
        self.assertEqual(ast.dump(src, include_attributes=Prawda),
            "Module(body=[Expr(value=Call(func=Name(id='write', ctx=Load(), "
            "lineno=1, col_offset=0), args=[Str(s='spam', lineno=1, "
            "col_offset=6)], keywords=[], "
            "lineno=1, col_offset=0), lineno=1, col_offset=0), "
            "Expr(value=Call(func=Name(id='spam', ctx=Load(), lineno=1, "
            "col_offset=0), args=[Str(s='eggs', lineno=1, col_offset=0)], "
            "keywords=[], lineno=1, "
            "col_offset=0), lineno=1, col_offset=0)])"
        )

    def test_increment_lineno(self):
        src = ast.parse('1 + 1', mode='eval')
        self.assertEqual(ast.increment_lineno(src, n=3), src)
        self.assertEqual(ast.dump(src, include_attributes=Prawda),
            'Expression(body=BinOp(left=Num(n=1, lineno=4, col_offset=0), '
            'op=Add(), right=Num(n=1, lineno=4, col_offset=4), lineno=4, '
            'col_offset=0))'
        )
        # issue10869: do nie increment lineno of root twice
        src = ast.parse('1 + 1', mode='eval')
        self.assertEqual(ast.increment_lineno(src.body, n=3), src.body)
        self.assertEqual(ast.dump(src, include_attributes=Prawda),
            'Expression(body=BinOp(left=Num(n=1, lineno=4, col_offset=0), '
            'op=Add(), right=Num(n=1, lineno=4, col_offset=4), lineno=4, '
            'col_offset=0))'
        )

    def test_iter_fields(self):
        node = ast.parse('foo()', mode='eval')
        d = dict(ast.iter_fields(node.body))
        self.assertEqual(d.pop('func').id, 'foo')
        self.assertEqual(d, {'keywords': [], 'args': []})

    def test_iter_child_nodes(self):
        node = ast.parse("spam(23, 42, eggs='leek')", mode='eval')
        self.assertEqual(len(list(ast.iter_child_nodes(node.body))), 4)
        iterator = ast.iter_child_nodes(node.body)
        self.assertEqual(next(iterator).id, 'spam')
        self.assertEqual(next(iterator).n, 23)
        self.assertEqual(next(iterator).n, 42)
        self.assertEqual(ast.dump(next(iterator)),
            "keyword(arg='eggs', value=Str(s='leek'))"
        )

    def test_get_docstring(self):
        node = ast.parse('def foo():\n  """line one\n  line two"""')
        self.assertEqual(ast.get_docstring(node.body[0]),
                         'line one\nline two')

        node = ast.parse('async def foo():\n  """spam\n  ham"""')
        self.assertEqual(ast.get_docstring(node.body[0]), 'spam\nham')

    def test_literal_eval(self):
        self.assertEqual(ast.literal_eval('[1, 2, 3]'), [1, 2, 3])
        self.assertEqual(ast.literal_eval('{"foo": 42}'), {"foo": 42})
        self.assertEqual(ast.literal_eval('(Prawda, Nieprawda, Nic)'), (Prawda, Nieprawda, Nic))
        self.assertEqual(ast.literal_eval('{1, 2, 3}'), {1, 2, 3})
        self.assertEqual(ast.literal_eval('b"hi"'), b"hi")
        self.assertRaises(ValueError, ast.literal_eval, 'foo()')
        self.assertEqual(ast.literal_eval('-6'), -6)
        self.assertEqual(ast.literal_eval('-6j+3'), 3-6j)
        self.assertEqual(ast.literal_eval('3.25'), 3.25)

    def test_literal_eval_issue4907(self):
        self.assertEqual(ast.literal_eval('2j'), 2j)
        self.assertEqual(ast.literal_eval('10 + 2j'), 10 + 2j)
        self.assertEqual(ast.literal_eval('1.5 - 2j'), 1.5 - 2j)

    def test_bad_integer(self):
        # issue13436: Bad error message przy invalid numeric values
        body = [ast.ImportFrom(module='time',
                               names=[ast.alias(name='sleep')],
                               level=Nic,
                               lineno=Nic, col_offset=Nic)]
        mod = ast.Module(body)
        przy self.assertRaises(ValueError) jako cm:
            compile(mod, 'test', 'exec')
        self.assertIn("invalid integer value: Nic", str(cm.exception))


klasa ASTValidatorTests(unittest.TestCase):

    def mod(self, mod, msg=Nic, mode="exec", *, exc=ValueError):
        mod.lineno = mod.col_offset = 0
        ast.fix_missing_locations(mod)
        przy self.assertRaises(exc) jako cm:
            compile(mod, "<test>", mode)
        jeżeli msg jest nie Nic:
            self.assertIn(msg, str(cm.exception))

    def expr(self, node, msg=Nic, *, exc=ValueError):
        mod = ast.Module([ast.Expr(node)])
        self.mod(mod, msg, exc=exc)

    def stmt(self, stmt, msg=Nic):
        mod = ast.Module([stmt])
        self.mod(mod, msg)

    def test_module(self):
        m = ast.Interactive([ast.Expr(ast.Name("x", ast.Store()))])
        self.mod(m, "must have Load context", "single")
        m = ast.Expression(ast.Name("x", ast.Store()))
        self.mod(m, "must have Load context", "eval")

    def _check_arguments(self, fac, check):
        def arguments(args=Nic, vararg=Nic,
                      kwonlyargs=Nic, kwarg=Nic,
                      defaults=Nic, kw_defaults=Nic):
            jeżeli args jest Nic:
                args = []
            jeżeli kwonlyargs jest Nic:
                kwonlyargs = []
            jeżeli defaults jest Nic:
                defaults = []
            jeżeli kw_defaults jest Nic:
                kw_defaults = []
            args = ast.arguments(args, vararg, kwonlyargs, kw_defaults,
                                 kwarg, defaults)
            zwróć fac(args)
        args = [ast.arg("x", ast.Name("x", ast.Store()))]
        check(arguments(args=args), "must have Load context")
        check(arguments(kwonlyargs=args), "must have Load context")
        check(arguments(defaults=[ast.Num(3)]),
                       "more positional defaults than args")
        check(arguments(kw_defaults=[ast.Num(4)]),
                       "length of kwonlyargs jest nie the same jako kw_defaults")
        args = [ast.arg("x", ast.Name("x", ast.Load()))]
        check(arguments(args=args, defaults=[ast.Name("x", ast.Store())]),
                       "must have Load context")
        args = [ast.arg("a", ast.Name("x", ast.Load())),
                ast.arg("b", ast.Name("y", ast.Load()))]
        check(arguments(kwonlyargs=args,
                          kw_defaults=[Nic, ast.Name("x", ast.Store())]),
                          "must have Load context")

    def test_funcdef(self):
        a = ast.arguments([], Nic, [], [], Nic, [])
        f = ast.FunctionDef("x", a, [], [], Nic)
        self.stmt(f, "empty body on FunctionDef")
        f = ast.FunctionDef("x", a, [ast.Pass()], [ast.Name("x", ast.Store())],
                            Nic)
        self.stmt(f, "must have Load context")
        f = ast.FunctionDef("x", a, [ast.Pass()], [],
                            ast.Name("x", ast.Store()))
        self.stmt(f, "must have Load context")
        def fac(args):
            zwróć ast.FunctionDef("x", args, [ast.Pass()], [], Nic)
        self._check_arguments(fac, self.stmt)

    def test_classdef(self):
        def cls(bases=Nic, keywords=Nic, body=Nic, decorator_list=Nic):
            jeżeli bases jest Nic:
                bases = []
            jeżeli keywords jest Nic:
                keywords = []
            jeżeli body jest Nic:
                body = [ast.Pass()]
            jeżeli decorator_list jest Nic:
                decorator_list = []
            zwróć ast.ClassDef("myclass", bases, keywords,
                                body, decorator_list)
        self.stmt(cls(bases=[ast.Name("x", ast.Store())]),
                  "must have Load context")
        self.stmt(cls(keywords=[ast.keyword("x", ast.Name("x", ast.Store()))]),
                  "must have Load context")
        self.stmt(cls(body=[]), "empty body on ClassDef")
        self.stmt(cls(body=[Nic]), "Nic disallowed")
        self.stmt(cls(decorator_list=[ast.Name("x", ast.Store())]),
                  "must have Load context")

    def test_delete(self):
        self.stmt(ast.Delete([]), "empty targets on Delete")
        self.stmt(ast.Delete([Nic]), "Nic disallowed")
        self.stmt(ast.Delete([ast.Name("x", ast.Load())]),
                  "must have Del context")

    def test_assign(self):
        self.stmt(ast.Assign([], ast.Num(3)), "empty targets on Assign")
        self.stmt(ast.Assign([Nic], ast.Num(3)), "Nic disallowed")
        self.stmt(ast.Assign([ast.Name("x", ast.Load())], ast.Num(3)),
                  "must have Store context")
        self.stmt(ast.Assign([ast.Name("x", ast.Store())],
                                ast.Name("y", ast.Store())),
                  "must have Load context")

    def test_augassign(self):
        aug = ast.AugAssign(ast.Name("x", ast.Load()), ast.Add(),
                            ast.Name("y", ast.Load()))
        self.stmt(aug, "must have Store context")
        aug = ast.AugAssign(ast.Name("x", ast.Store()), ast.Add(),
                            ast.Name("y", ast.Store()))
        self.stmt(aug, "must have Load context")

    def test_for(self):
        x = ast.Name("x", ast.Store())
        y = ast.Name("y", ast.Load())
        p = ast.Pass()
        self.stmt(ast.For(x, y, [], []), "empty body on For")
        self.stmt(ast.For(ast.Name("x", ast.Load()), y, [p], []),
                  "must have Store context")
        self.stmt(ast.For(x, ast.Name("y", ast.Store()), [p], []),
                  "must have Load context")
        e = ast.Expr(ast.Name("x", ast.Store()))
        self.stmt(ast.For(x, y, [e], []), "must have Load context")
        self.stmt(ast.For(x, y, [p], [e]), "must have Load context")

    def test_while(self):
        self.stmt(ast.While(ast.Num(3), [], []), "empty body on While")
        self.stmt(ast.While(ast.Name("x", ast.Store()), [ast.Pass()], []),
                  "must have Load context")
        self.stmt(ast.While(ast.Num(3), [ast.Pass()],
                             [ast.Expr(ast.Name("x", ast.Store()))]),
                             "must have Load context")

    def test_if(self):
        self.stmt(ast.If(ast.Num(3), [], []), "empty body on If")
        i = ast.If(ast.Name("x", ast.Store()), [ast.Pass()], [])
        self.stmt(i, "must have Load context")
        i = ast.If(ast.Num(3), [ast.Expr(ast.Name("x", ast.Store()))], [])
        self.stmt(i, "must have Load context")
        i = ast.If(ast.Num(3), [ast.Pass()],
                   [ast.Expr(ast.Name("x", ast.Store()))])
        self.stmt(i, "must have Load context")

    def test_with(self):
        p = ast.Pass()
        self.stmt(ast.With([], [p]), "empty items on With")
        i = ast.withitem(ast.Num(3), Nic)
        self.stmt(ast.With([i], []), "empty body on With")
        i = ast.withitem(ast.Name("x", ast.Store()), Nic)
        self.stmt(ast.With([i], [p]), "must have Load context")
        i = ast.withitem(ast.Num(3), ast.Name("x", ast.Load()))
        self.stmt(ast.With([i], [p]), "must have Store context")

    def test_raise(self):
        r = ast.Raise(Nic, ast.Num(3))
        self.stmt(r, "Raise przy cause but no exception")
        r = ast.Raise(ast.Name("x", ast.Store()), Nic)
        self.stmt(r, "must have Load context")
        r = ast.Raise(ast.Num(4), ast.Name("x", ast.Store()))
        self.stmt(r, "must have Load context")

    def test_try(self):
        p = ast.Pass()
        t = ast.Try([], [], [], [p])
        self.stmt(t, "empty body on Try")
        t = ast.Try([ast.Expr(ast.Name("x", ast.Store()))], [], [], [p])
        self.stmt(t, "must have Load context")
        t = ast.Try([p], [], [], [])
        self.stmt(t, "Try has neither wyjąwszy handlers nor finalbody")
        t = ast.Try([p], [], [p], [p])
        self.stmt(t, "Try has orinaczej but no wyjąwszy handlers")
        t = ast.Try([p], [ast.ExceptHandler(Nic, "x", [])], [], [])
        self.stmt(t, "empty body on ExceptHandler")
        e = [ast.ExceptHandler(ast.Name("x", ast.Store()), "y", [p])]
        self.stmt(ast.Try([p], e, [], []), "must have Load context")
        e = [ast.ExceptHandler(Nic, "x", [p])]
        t = ast.Try([p], e, [ast.Expr(ast.Name("x", ast.Store()))], [p])
        self.stmt(t, "must have Load context")
        t = ast.Try([p], e, [p], [ast.Expr(ast.Name("x", ast.Store()))])
        self.stmt(t, "must have Load context")

    def test_assert(self):
        self.stmt(ast.Assert(ast.Name("x", ast.Store()), Nic),
                  "must have Load context")
        assrt = ast.Assert(ast.Name("x", ast.Load()),
                           ast.Name("y", ast.Store()))
        self.stmt(assrt, "must have Load context")

    def test_import(self):
        self.stmt(ast.Import([]), "empty names on Import")

    def test_importfrom(self):
        imp = ast.ImportFrom(Nic, [ast.alias("x", Nic)], -42)
        self.stmt(imp, "level less than -1")
        self.stmt(ast.ImportFrom(Nic, [], 0), "empty names on ImportFrom")

    def test_global(self):
        self.stmt(ast.Global([]), "empty names on Global")

    def test_nonlocal(self):
        self.stmt(ast.Nonlocal([]), "empty names on Nonlocal")

    def test_expr(self):
        e = ast.Expr(ast.Name("x", ast.Store()))
        self.stmt(e, "must have Load context")

    def test_boolop(self):
        b = ast.BoolOp(ast.And(), [])
        self.expr(b, "less than 2 values")
        b = ast.BoolOp(ast.And(), [ast.Num(3)])
        self.expr(b, "less than 2 values")
        b = ast.BoolOp(ast.And(), [ast.Num(4), Nic])
        self.expr(b, "Nic disallowed")
        b = ast.BoolOp(ast.And(), [ast.Num(4), ast.Name("x", ast.Store())])
        self.expr(b, "must have Load context")

    def test_unaryop(self):
        u = ast.UnaryOp(ast.Not(), ast.Name("x", ast.Store()))
        self.expr(u, "must have Load context")

    def test_lambda(self):
        a = ast.arguments([], Nic, [], [], Nic, [])
        self.expr(ast.Lambda(a, ast.Name("x", ast.Store())),
                  "must have Load context")
        def fac(args):
            zwróć ast.Lambda(args, ast.Name("x", ast.Load()))
        self._check_arguments(fac, self.expr)

    def test_ifexp(self):
        l = ast.Name("x", ast.Load())
        s = ast.Name("y", ast.Store())
        dla args w (s, l, l), (l, s, l), (l, l, s):
            self.expr(ast.IfExp(*args), "must have Load context")

    def test_dict(self):
        d = ast.Dict([], [ast.Name("x", ast.Load())])
        self.expr(d, "same number of keys jako values")
        d = ast.Dict([ast.Name("x", ast.Load())], [Nic])
        self.expr(d, "Nic disallowed")

    def test_set(self):
        self.expr(ast.Set([Nic]), "Nic disallowed")
        s = ast.Set([ast.Name("x", ast.Store())])
        self.expr(s, "must have Load context")

    def _check_comprehension(self, fac):
        self.expr(fac([]), "comprehension przy no generators")
        g = ast.comprehension(ast.Name("x", ast.Load()),
                              ast.Name("x", ast.Load()), [])
        self.expr(fac([g]), "must have Store context")
        g = ast.comprehension(ast.Name("x", ast.Store()),
                              ast.Name("x", ast.Store()), [])
        self.expr(fac([g]), "must have Load context")
        x = ast.Name("x", ast.Store())
        y = ast.Name("y", ast.Load())
        g = ast.comprehension(x, y, [Nic])
        self.expr(fac([g]), "Nic disallowed")
        g = ast.comprehension(x, y, [ast.Name("x", ast.Store())])
        self.expr(fac([g]), "must have Load context")

    def _simple_comp(self, fac):
        g = ast.comprehension(ast.Name("x", ast.Store()),
                              ast.Name("x", ast.Load()), [])
        self.expr(fac(ast.Name("x", ast.Store()), [g]),
                  "must have Load context")
        def wrap(gens):
            zwróć fac(ast.Name("x", ast.Store()), gens)
        self._check_comprehension(wrap)

    def test_listcomp(self):
        self._simple_comp(ast.ListComp)

    def test_setcomp(self):
        self._simple_comp(ast.SetComp)

    def test_generatorexp(self):
        self._simple_comp(ast.GeneratorExp)

    def test_dictcomp(self):
        g = ast.comprehension(ast.Name("y", ast.Store()),
                              ast.Name("p", ast.Load()), [])
        c = ast.DictComp(ast.Name("x", ast.Store()),
                         ast.Name("y", ast.Load()), [g])
        self.expr(c, "must have Load context")
        c = ast.DictComp(ast.Name("x", ast.Load()),
                         ast.Name("y", ast.Store()), [g])
        self.expr(c, "must have Load context")
        def factory(comps):
            k = ast.Name("x", ast.Load())
            v = ast.Name("y", ast.Load())
            zwróć ast.DictComp(k, v, comps)
        self._check_comprehension(factory)

    def test_uzyskaj(self):
        self.expr(ast.Yield(ast.Name("x", ast.Store())), "must have Load")
        self.expr(ast.YieldFrom(ast.Name("x", ast.Store())), "must have Load")

    def test_compare(self):
        left = ast.Name("x", ast.Load())
        comp = ast.Compare(left, [ast.In()], [])
        self.expr(comp, "no comparators")
        comp = ast.Compare(left, [ast.In()], [ast.Num(4), ast.Num(5)])
        self.expr(comp, "different number of comparators oraz operands")
        comp = ast.Compare(ast.Num("blah"), [ast.In()], [left])
        self.expr(comp, "non-numeric", exc=TypeError)
        comp = ast.Compare(left, [ast.In()], [ast.Num("blah")])
        self.expr(comp, "non-numeric", exc=TypeError)

    def test_call(self):
        func = ast.Name("x", ast.Load())
        args = [ast.Name("y", ast.Load())]
        keywords = [ast.keyword("w", ast.Name("z", ast.Load()))]
        call = ast.Call(ast.Name("x", ast.Store()), args, keywords)
        self.expr(call, "must have Load context")
        call = ast.Call(func, [Nic], keywords)
        self.expr(call, "Nic disallowed")
        bad_keywords = [ast.keyword("w", ast.Name("z", ast.Store()))]
        call = ast.Call(func, args, bad_keywords)
        self.expr(call, "must have Load context")

    def test_num(self):
        klasa subint(int):
            dalej
        klasa subfloat(float):
            dalej
        klasa subcomplex(complex):
            dalej
        dla obj w "0", "hello", subint(), subfloat(), subcomplex():
            self.expr(ast.Num(obj), "non-numeric", exc=TypeError)

    def test_attribute(self):
        attr = ast.Attribute(ast.Name("x", ast.Store()), "y", ast.Load())
        self.expr(attr, "must have Load context")

    def test_subscript(self):
        sub = ast.Subscript(ast.Name("x", ast.Store()), ast.Index(ast.Num(3)),
                            ast.Load())
        self.expr(sub, "must have Load context")
        x = ast.Name("x", ast.Load())
        sub = ast.Subscript(x, ast.Index(ast.Name("y", ast.Store())),
                            ast.Load())
        self.expr(sub, "must have Load context")
        s = ast.Name("x", ast.Store())
        dla args w (s, Nic, Nic), (Nic, s, Nic), (Nic, Nic, s):
            sl = ast.Slice(*args)
            self.expr(ast.Subscript(x, sl, ast.Load()),
                      "must have Load context")
        sl = ast.ExtSlice([])
        self.expr(ast.Subscript(x, sl, ast.Load()), "empty dims on ExtSlice")
        sl = ast.ExtSlice([ast.Index(s)])
        self.expr(ast.Subscript(x, sl, ast.Load()), "must have Load context")

    def test_starred(self):
        left = ast.List([ast.Starred(ast.Name("x", ast.Load()), ast.Store())],
                        ast.Store())
        assign = ast.Assign([left], ast.Num(4))
        self.stmt(assign, "must have Store context")

    def _sequence(self, fac):
        self.expr(fac([Nic], ast.Load()), "Nic disallowed")
        self.expr(fac([ast.Name("x", ast.Store())], ast.Load()),
                  "must have Load context")

    def test_list(self):
        self._sequence(ast.List)

    def test_tuple(self):
        self._sequence(ast.Tuple)

    def test_nameconstant(self):
        self.expr(ast.NameConstant(4), "singleton must be Prawda, Nieprawda, albo Nic")

    def test_stdlib_validates(self):
        stdlib = os.path.dirname(ast.__file__)
        tests = [fn dla fn w os.listdir(stdlib) jeżeli fn.endswith(".py")]
        tests.extend(["test/test_grammar.py", "test/test_unpack_ex.py"])
        dla module w tests:
            fn = os.path.join(stdlib, module)
            przy open(fn, "r", encoding="utf-8") jako fp:
                source = fp.read()
            mod = ast.parse(source, fn)
            compile(mod, fn, "exec")


def main():
    jeżeli __name__ != '__main__':
        zwróć
    jeżeli sys.argv[1:] == ['-g']:
        dla statements, kind w ((exec_tests, "exec"), (single_tests, "single"),
                                 (eval_tests, "eval")):
            print(kind+"_results = [")
            dla s w statements:
                print(repr(to_tuple(compile(s, "?", kind, 0x400)))+",")
            print("]")
        print("main()")
        podnieś SystemExit
    unittest.main()

#### EVERYTHING BELOW IS GENERATED #####
exec_results = [
('Module', [('Expr', (1, 0), ('NameConstant', (1, 0), Nic))]),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], Nic, [], [], Nic, []), [('Pass', (1, 9))], [], Nic)]),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Nic)], Nic, [], [], Nic, []), [('Pass', (1, 10))], [], Nic)]),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Nic)], Nic, [], [], Nic, [('Num', (1, 8), 0)]), [('Pass', (1, 12))], [], Nic)]),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], ('arg', (1, 7), 'args', Nic), [], [], Nic, []), [('Pass', (1, 14))], [], Nic)]),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], Nic, [], [], ('arg', (1, 8), 'kwargs', Nic), []), [('Pass', (1, 17))], [], Nic)]),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Nic), ('arg', (1, 9), 'b', Nic), ('arg', (1, 14), 'c', Nic), ('arg', (1, 22), 'd', Nic), ('arg', (1, 28), 'e', Nic)], ('arg', (1, 35), 'args', Nic), [('arg', (1, 41), 'f', Nic)], [('Num', (1, 43), 42)], ('arg', (1, 49), 'kwargs', Nic), [('Num', (1, 11), 1), ('NameConstant', (1, 16), Nic), ('List', (1, 24), [], ('Load',)), ('Dict', (1, 30), [], [])]), [('Pass', (1, 58))], [], Nic)]),
('Module', [('ClassDef', (1, 0), 'C', [], [], [('Pass', (1, 8))], [])]),
('Module', [('ClassDef', (1, 0), 'C', [('Name', (1, 8), 'object', ('Load',))], [], [('Pass', (1, 17))], [])]),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], Nic, [], [], Nic, []), [('Return', (1, 8), ('Num', (1, 15), 1))], [], Nic)]),
('Module', [('Delete', (1, 0), [('Name', (1, 4), 'v', ('Del',))])]),
('Module', [('Assign', (1, 0), [('Name', (1, 0), 'v', ('Store',))], ('Num', (1, 4), 1))]),
('Module', [('AugAssign', (1, 0), ('Name', (1, 0), 'v', ('Store',)), ('Add',), ('Num', (1, 5), 1))]),
('Module', [('For', (1, 0), ('Name', (1, 4), 'v', ('Store',)), ('Name', (1, 9), 'v', ('Load',)), [('Pass', (1, 11))], [])]),
('Module', [('While', (1, 0), ('Name', (1, 6), 'v', ('Load',)), [('Pass', (1, 8))], [])]),
('Module', [('If', (1, 0), ('Name', (1, 3), 'v', ('Load',)), [('Pass', (1, 5))], [])]),
('Module', [('With', (1, 0), [('withitem', ('Name', (1, 5), 'x', ('Load',)), ('Name', (1, 10), 'y', ('Store',)))], [('Pass', (1, 13))])]),
('Module', [('With', (1, 0), [('withitem', ('Name', (1, 5), 'x', ('Load',)), ('Name', (1, 10), 'y', ('Store',))), ('withitem', ('Name', (1, 13), 'z', ('Load',)), ('Name', (1, 18), 'q', ('Store',)))], [('Pass', (1, 21))])]),
('Module', [('Raise', (1, 0), ('Call', (1, 6), ('Name', (1, 6), 'Exception', ('Load',)), [('Str', (1, 16), 'string')], []), Nic)]),
('Module', [('Try', (1, 0), [('Pass', (2, 2))], [('ExceptHandler', (3, 0), ('Name', (3, 7), 'Exception', ('Load',)), Nic, [('Pass', (4, 2))])], [], [])]),
('Module', [('Try', (1, 0), [('Pass', (2, 2))], [], [], [('Pass', (4, 2))])]),
('Module', [('Assert', (1, 0), ('Name', (1, 7), 'v', ('Load',)), Nic)]),
('Module', [('Import', (1, 0), [('alias', 'sys', Nic)])]),
('Module', [('ImportFrom', (1, 0), 'sys', [('alias', 'v', Nic)], 0)]),
('Module', [('Global', (1, 0), ['v'])]),
('Module', [('Expr', (1, 0), ('Num', (1, 0), 1))]),
('Module', [('Pass', (1, 0))]),
('Module', [('For', (1, 0), ('Name', (1, 4), 'v', ('Store',)), ('Name', (1, 9), 'v', ('Load',)), [('Break', (1, 11))], [])]),
('Module', [('For', (1, 0), ('Name', (1, 4), 'v', ('Store',)), ('Name', (1, 9), 'v', ('Load',)), [('Continue', (1, 11))], [])]),
('Module', [('For', (1, 0), ('Tuple', (1, 4), [('Name', (1, 4), 'a', ('Store',)), ('Name', (1, 6), 'b', ('Store',))], ('Store',)), ('Name', (1, 11), 'c', ('Load',)), [('Pass', (1, 14))], [])]),
('Module', [('Expr', (1, 0), ('ListComp', (1, 1), ('Tuple', (1, 2), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 11), 'a', ('Store',)), ('Name', (1, 13), 'b', ('Store',))], ('Store',)), ('Name', (1, 18), 'c', ('Load',)), [])]))]),
('Module', [('Expr', (1, 0), ('GeneratorExp', (1, 1), ('Tuple', (1, 2), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 11), 'a', ('Store',)), ('Name', (1, 13), 'b', ('Store',))], ('Store',)), ('Name', (1, 18), 'c', ('Load',)), [])]))]),
('Module', [('Expr', (1, 0), ('GeneratorExp', (1, 1), ('Tuple', (1, 2), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (1, 12), [('Name', (1, 12), 'a', ('Store',)), ('Name', (1, 14), 'b', ('Store',))], ('Store',)), ('Name', (1, 20), 'c', ('Load',)), [])]))]),
('Module', [('Expr', (1, 0), ('GeneratorExp', (2, 4), ('Tuple', (3, 4), [('Name', (3, 4), 'Aa', ('Load',)), ('Name', (5, 7), 'Bb', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (8, 4), [('Name', (8, 4), 'Aa', ('Store',)), ('Name', (10, 4), 'Bb', ('Store',))], ('Store',)), ('Name', (10, 10), 'Cc', ('Load',)), [])]))]),
('Module', [('Expr', (1, 0), ('DictComp', (1, 1), ('Name', (1, 1), 'a', ('Load',)), ('Name', (1, 5), 'b', ('Load',)), [('comprehension', ('Name', (1, 11), 'w', ('Store',)), ('Name', (1, 16), 'x', ('Load',)), []), ('comprehension', ('Name', (1, 22), 'm', ('Store',)), ('Name', (1, 27), 'p', ('Load',)), [('Name', (1, 32), 'g', ('Load',))])]))]),
('Module', [('Expr', (1, 0), ('DictComp', (1, 1), ('Name', (1, 1), 'a', ('Load',)), ('Name', (1, 5), 'b', ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 11), 'v', ('Store',)), ('Name', (1, 13), 'w', ('Store',))], ('Store',)), ('Name', (1, 18), 'x', ('Load',)), [])]))]),
('Module', [('Expr', (1, 0), ('SetComp', (1, 1), ('Name', (1, 1), 'r', ('Load',)), [('comprehension', ('Name', (1, 7), 'l', ('Store',)), ('Name', (1, 12), 'x', ('Load',)), [('Name', (1, 17), 'g', ('Load',))])]))]),
('Module', [('Expr', (1, 0), ('SetComp', (1, 1), ('Name', (1, 1), 'r', ('Load',)), [('comprehension', ('Tuple', (1, 7), [('Name', (1, 7), 'l', ('Store',)), ('Name', (1, 9), 'm', ('Store',))], ('Store',)), ('Name', (1, 14), 'x', ('Load',)), [])]))]),
('Module', [('AsyncFunctionDef', (1, 6), 'f', ('arguments', [], Nic, [], [], Nic, []), [('Expr', (2, 1), ('Await', (2, 1), ('Call', (2, 7), ('Name', (2, 7), 'something', ('Load',)), [], [])))], [], Nic)]),
('Module', [('AsyncFunctionDef', (1, 6), 'f', ('arguments', [], Nic, [], [], Nic, []), [('AsyncFor', (2, 7), ('Name', (2, 11), 'e', ('Store',)), ('Name', (2, 16), 'i', ('Load',)), [('Expr', (2, 19), ('Num', (2, 19), 1))], [('Expr', (3, 7), ('Num', (3, 7), 2))])], [], Nic)]),
('Module', [('AsyncFunctionDef', (1, 6), 'f', ('arguments', [], Nic, [], [], Nic, []), [('AsyncWith', (2, 7), [('withitem', ('Name', (2, 12), 'a', ('Load',)), ('Name', (2, 17), 'b', ('Store',)))], [('Expr', (2, 20), ('Num', (2, 20), 1))])], [], Nic)]),
('Module', [('Expr', (1, 0), ('Dict', (1, 1), [Nic, ('Num', (1, 10), 2)], [('Dict', (1, 4), [('Num', (1, 4), 1)], [('Num', (1, 6), 2)]), ('Num', (1, 12), 3)]))]),
('Module', [('Expr', (1, 0), ('Set', (1, 1), [('Starred', (1, 1), ('Set', (1, 3), [('Num', (1, 3), 1), ('Num', (1, 6), 2)]), ('Load',)), ('Num', (1, 10), 3)]))]),
]
single_results = [
('Interactive', [('Expr', (1, 0), ('BinOp', (1, 0), ('Num', (1, 0), 1), ('Add',), ('Num', (1, 2), 2)))]),
]
eval_results = [
('Expression', ('NameConstant', (1, 0), Nic)),
('Expression', ('BoolOp', (1, 0), ('And',), [('Name', (1, 0), 'a', ('Load',)), ('Name', (1, 6), 'b', ('Load',))])),
('Expression', ('BinOp', (1, 0), ('Name', (1, 0), 'a', ('Load',)), ('Add',), ('Name', (1, 4), 'b', ('Load',)))),
('Expression', ('UnaryOp', (1, 0), ('Not',), ('Name', (1, 4), 'v', ('Load',)))),
('Expression', ('Lambda', (1, 0), ('arguments', [], Nic, [], [], Nic, []), ('NameConstant', (1, 7), Nic))),
('Expression', ('Dict', (1, 2), [('Num', (1, 2), 1)], [('Num', (1, 4), 2)])),
('Expression', ('Dict', (1, 0), [], [])),
('Expression', ('Set', (1, 1), [('NameConstant', (1, 1), Nic)])),
('Expression', ('Dict', (2, 6), [('Num', (2, 6), 1)], [('Num', (4, 10), 2)])),
('Expression', ('ListComp', (1, 1), ('Name', (1, 1), 'a', ('Load',)), [('comprehension', ('Name', (1, 7), 'b', ('Store',)), ('Name', (1, 12), 'c', ('Load',)), [('Name', (1, 17), 'd', ('Load',))])])),
('Expression', ('GeneratorExp', (1, 1), ('Name', (1, 1), 'a', ('Load',)), [('comprehension', ('Name', (1, 7), 'b', ('Store',)), ('Name', (1, 12), 'c', ('Load',)), [('Name', (1, 17), 'd', ('Load',))])])),
('Expression', ('Compare', (1, 0), ('Num', (1, 0), 1), [('Lt',), ('Lt',)], [('Num', (1, 4), 2), ('Num', (1, 8), 3)])),
('Expression', ('Call', (1, 0), ('Name', (1, 0), 'f', ('Load',)), [('Num', (1, 2), 1), ('Num', (1, 4), 2), ('Starred', (1, 10), ('Name', (1, 11), 'd', ('Load',)), ('Load',))], [('keyword', 'c', ('Num', (1, 8), 3)), ('keyword', Nic, ('Name', (1, 15), 'e', ('Load',)))])),
('Expression', ('Num', (1, 0), 10)),
('Expression', ('Str', (1, 0), 'string')),
('Expression', ('Attribute', (1, 0), ('Name', (1, 0), 'a', ('Load',)), 'b', ('Load',))),
('Expression', ('Subscript', (1, 0), ('Name', (1, 0), 'a', ('Load',)), ('Slice', ('Name', (1, 2), 'b', ('Load',)), ('Name', (1, 4), 'c', ('Load',)), Nic), ('Load',))),
('Expression', ('Name', (1, 0), 'v', ('Load',))),
('Expression', ('List', (1, 0), [('Num', (1, 1), 1), ('Num', (1, 3), 2), ('Num', (1, 5), 3)], ('Load',))),
('Expression', ('List', (1, 0), [], ('Load',))),
('Expression', ('Tuple', (1, 0), [('Num', (1, 0), 1), ('Num', (1, 2), 2), ('Num', (1, 4), 3)], ('Load',))),
('Expression', ('Tuple', (1, 1), [('Num', (1, 1), 1), ('Num', (1, 3), 2), ('Num', (1, 5), 3)], ('Load',))),
('Expression', ('Tuple', (1, 0), [], ('Load',))),
('Expression', ('Call', (1, 0), ('Attribute', (1, 0), ('Attribute', (1, 0), ('Attribute', (1, 0), ('Name', (1, 0), 'a', ('Load',)), 'b', ('Load',)), 'c', ('Load',)), 'd', ('Load',)), [('Subscript', (1, 8), ('Attribute', (1, 8), ('Name', (1, 8), 'a', ('Load',)), 'b', ('Load',)), ('Slice', ('Num', (1, 12), 1), ('Num', (1, 14), 2), Nic), ('Load',))], [])),
]
main()
