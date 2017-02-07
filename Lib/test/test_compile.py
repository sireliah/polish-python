zaimportuj math
zaimportuj os
zaimportuj unittest
zaimportuj sys
zaimportuj _ast
zaimportuj tempfile
zaimportuj types
z test zaimportuj support
z test.support zaimportuj script_helper

klasa TestSpecifics(unittest.TestCase):

    def compile_single(self, source):
        compile(source, "<single>", "single")

    def assertInvalidSingle(self, source):
        self.assertRaises(SyntaxError, self.compile_single, source)

    def test_no_ending_newline(self):
        compile("hi", "<test>", "exec")
        compile("hi\r", "<test>", "exec")

    def test_empty(self):
        compile("", "<test>", "exec")

    def test_other_newlines(self):
        compile("\r\n", "<test>", "exec")
        compile("\r", "<test>", "exec")
        compile("hi\r\nstuff\r\ndef f():\n    dalej\r", "<test>", "exec")
        compile("this_is\rreally_old_mac\rdef f():\n    dalej", "<test>", "exec")

    def test_debug_assignment(self):
        # catch assignments to __debug__
        self.assertRaises(SyntaxError, compile, '__debug__ = 1', '?', 'single')
        zaimportuj builtins
        prev = builtins.__debug__
        setattr(builtins, '__debug__', 'sure')
        setattr(builtins, '__debug__', prev)

    def test_argument_handling(self):
        # detect duplicate positional oraz keyword arguments
        self.assertRaises(SyntaxError, eval, 'lambda a,a:0')
        self.assertRaises(SyntaxError, eval, 'lambda a,a=1:0')
        self.assertRaises(SyntaxError, eval, 'lambda a=1,a=1:0')
        self.assertRaises(SyntaxError, exec, 'def f(a, a): dalej')
        self.assertRaises(SyntaxError, exec, 'def f(a = 0, a = 1): dalej')
        self.assertRaises(SyntaxError, exec, 'def f(a): global a; a = 1')

    def test_syntax_error(self):
        self.assertRaises(SyntaxError, compile, "1+*3", "filename", "exec")

    def test_none_keyword_arg(self):
        self.assertRaises(SyntaxError, compile, "f(Nic=1)", "<string>", "exec")

    def test_duplicate_global_local(self):
        self.assertRaises(SyntaxError, exec, 'def f(a): global a; a = 1')

    def test_exec_with_general_mapping_for_locals(self):

        klasa M:
            "Test mapping interface versus possible calls z eval()."
            def __getitem__(self, key):
                jeżeli key == 'a':
                    zwróć 12
                podnieś KeyError
            def __setitem__(self, key, value):
                self.results = (key, value)
            def keys(self):
                zwróć list('xyz')

        m = M()
        g = globals()
        exec('z = a', g, m)
        self.assertEqual(m.results, ('z', 12))
        spróbuj:
            exec('z = b', g, m)
        wyjąwszy NameError:
            dalej
        inaczej:
            self.fail('Did nie detect a KeyError')
        exec('z = dir()', g, m)
        self.assertEqual(m.results, ('z', list('xyz')))
        exec('z = globals()', g, m)
        self.assertEqual(m.results, ('z', g))
        exec('z = locals()', g, m)
        self.assertEqual(m.results, ('z', m))
        self.assertRaises(TypeError, exec, 'z = b', m)

        klasa A:
            "Non-mapping"
            dalej
        m = A()
        self.assertRaises(TypeError, exec, 'z = a', g, m)

        # Verify that dict subclasses work jako well
        klasa D(dict):
            def __getitem__(self, key):
                jeżeli key == 'a':
                    zwróć 12
                zwróć dict.__getitem__(self, key)
        d = D()
        exec('z = a', g, d)
        self.assertEqual(d['z'], 12)

    def test_extended_arg(self):
        longexpr = 'x = x albo ' + '-x' * 2500
        g = {}
        code = '''
def f(x):
    %s
    %s
    %s
    %s
    %s
    %s
    %s
    %s
    %s
    %s
    # the expressions above have no effect, x == argument
    dopóki x:
        x -= 1
        # EXTENDED_ARG/JUMP_ABSOLUTE here
    zwróć x
''' % ((longexpr,)*10)
        exec(code, g)
        self.assertEqual(g['f'](5), 0)

    def test_argument_order(self):
        self.assertRaises(SyntaxError, exec, 'def f(a=1, b): dalej')

    def test_float_literals(self):
        # testing bad float literals
        self.assertRaises(SyntaxError, eval, "2e")
        self.assertRaises(SyntaxError, eval, "2.0e+")
        self.assertRaises(SyntaxError, eval, "1e-")
        self.assertRaises(SyntaxError, eval, "3-4e/21")

    def test_indentation(self):
        # testing compile() of indented block w/o trailing newline"
        s = """
jeżeli 1:
    jeżeli 2:
        dalej"""
        compile(s, "<string>", "exec")

    # This test jest probably specific to CPython oraz may nie generalize
    # to other implementations.  We are trying to ensure that when
    # the first line of code starts after 256, correct line numbers
    # w tracebacks are still produced.
    def test_leading_newlines(self):
        s256 = "".join(["\n"] * 256 + ["spam"])
        co = compile(s256, 'fn', 'exec')
        self.assertEqual(co.co_firstlineno, 257)
        self.assertEqual(co.co_lnotab, bytes())

    def test_literals_with_leading_zeroes(self):
        dla arg w ["077787", "0xj", "0x.", "0e",  "090000000000000",
                    "080000000000000", "000000000000009", "000000000000008",
                    "0b42", "0BADCAFE", "0o123456789", "0b1.1", "0o4.2",
                    "0b101j2", "0o153j2", "0b100e1", "0o777e1", "0777",
                    "000777", "000000000000007"]:
            self.assertRaises(SyntaxError, eval, arg)

        self.assertEqual(eval("0xff"), 255)
        self.assertEqual(eval("0777."), 777)
        self.assertEqual(eval("0777.0"), 777)
        self.assertEqual(eval("000000000000000000000000000000000000000000000000000777e0"), 777)
        self.assertEqual(eval("0777e1"), 7770)
        self.assertEqual(eval("0e0"), 0)
        self.assertEqual(eval("0000e-012"), 0)
        self.assertEqual(eval("09.5"), 9.5)
        self.assertEqual(eval("0777j"), 777j)
        self.assertEqual(eval("000"), 0)
        self.assertEqual(eval("00j"), 0j)
        self.assertEqual(eval("00.0"), 0)
        self.assertEqual(eval("0e3"), 0)
        self.assertEqual(eval("090000000000000."), 90000000000000.)
        self.assertEqual(eval("090000000000000.0000000000000000000000"), 90000000000000.)
        self.assertEqual(eval("090000000000000e0"), 90000000000000.)
        self.assertEqual(eval("090000000000000e-0"), 90000000000000.)
        self.assertEqual(eval("090000000000000j"), 90000000000000j)
        self.assertEqual(eval("000000000000008."), 8.)
        self.assertEqual(eval("000000000000009."), 9.)
        self.assertEqual(eval("0b101010"), 42)
        self.assertEqual(eval("-0b000000000010"), -2)
        self.assertEqual(eval("0o777"), 511)
        self.assertEqual(eval("-0o0000010"), -8)

    def test_unary_minus(self):
        # Verify treatment of unary minus on negative numbers SF bug #660455
        jeżeli sys.maxsize == 2147483647:
            # 32-bit machine
            all_one_bits = '0xffffffff'
            self.assertEqual(eval(all_one_bits), 4294967295)
            self.assertEqual(eval("-" + all_one_bits), -4294967295)
        albo_inaczej sys.maxsize == 9223372036854775807:
            # 64-bit machine
            all_one_bits = '0xffffffffffffffff'
            self.assertEqual(eval(all_one_bits), 18446744073709551615)
            self.assertEqual(eval("-" + all_one_bits), -18446744073709551615)
        inaczej:
            self.fail("How many bits *does* this machine have???")
        # Verify treatment of constant folding on -(sys.maxsize+1)
        # i.e. -2147483648 on 32 bit platforms.  Should zwróć int.
        self.assertIsInstance(eval("%s" % (-sys.maxsize - 1)), int)
        self.assertIsInstance(eval("%s" % (-sys.maxsize - 2)), int)

    jeżeli sys.maxsize == 9223372036854775807:
        def test_32_63_bit_values(self):
            a = +4294967296  # 1 << 32
            b = -4294967296  # 1 << 32
            c = +281474976710656  # 1 << 48
            d = -281474976710656  # 1 << 48
            e = +4611686018427387904  # 1 << 62
            f = -4611686018427387904  # 1 << 62
            g = +9223372036854775807  # 1 << 63 - 1
            h = -9223372036854775807  # 1 << 63 - 1

            dla variable w self.test_32_63_bit_values.__code__.co_consts:
                jeżeli variable jest nie Nic:
                    self.assertIsInstance(variable, int)

    def test_sequence_unpacking_error(self):
        # Verify sequence packing/unpacking przy "or".  SF bug #757818
        i,j = (1, -1) albo (-1, 1)
        self.assertEqual(i, 1)
        self.assertEqual(j, -1)

    def test_none_assignment(self):
        stmts = [
            'Nic = 0',
            'Nic += 0',
            '__builtins__.Nic = 0',
            'def Nic(): dalej',
            'class Nic: dalej',
            '(a, Nic) = 0, 0',
            'dla Nic w range(10): dalej',
            'def f(Nic): dalej',
            'zaimportuj Nic',
            'zaimportuj x jako Nic',
            'z x zaimportuj Nic',
            'z x zaimportuj y jako Nic'
        ]
        dla stmt w stmts:
            stmt += "\n"
            self.assertRaises(SyntaxError, compile, stmt, 'tmp', 'single')
            self.assertRaises(SyntaxError, compile, stmt, 'tmp', 'exec')

    def test_import(self):
        succeed = [
            'zaimportuj sys',
            'zaimportuj os, sys',
            'zaimportuj os jako bar',
            'zaimportuj os.path jako bar',
            'z __future__ zaimportuj nested_scopes, generators',
            'z __future__ zaimportuj (nested_scopes,\ngenerators)',
            'z __future__ zaimportuj (nested_scopes,\ngenerators,)',
            'z sys zaimportuj stdin, stderr, stdout',
            'z sys zaimportuj (stdin, stderr,\nstdout)',
            'z sys zaimportuj (stdin, stderr,\nstdout,)',
            'z sys zaimportuj (stdin\n, stderr, stdout)',
            'z sys zaimportuj (stdin\n, stderr, stdout,)',
            'z sys zaimportuj stdin jako si, stdout jako so, stderr jako se',
            'z sys zaimportuj (stdin jako si, stdout jako so, stderr jako se)',
            'z sys zaimportuj (stdin jako si, stdout jako so, stderr jako se,)',
            ]
        fail = [
            'zaimportuj (os, sys)',
            'zaimportuj (os), (sys)',
            'zaimportuj ((os), (sys))',
            'zaimportuj (sys',
            'zaimportuj sys)',
            'zaimportuj (os,)',
            'zaimportuj os As bar',
            'zaimportuj os.path a bar',
            'z sys zaimportuj stdin As stdout',
            'z sys zaimportuj stdin a stdout',
            'z (sys) zaimportuj stdin',
            'z __future__ zaimportuj (nested_scopes',
            'z __future__ zaimportuj nested_scopes)',
            'z __future__ zaimportuj nested_scopes,\ngenerators',
            'z sys zaimportuj (stdin',
            'z sys zaimportuj stdin)',
            'z sys zaimportuj stdin, stdout,\nstderr',
            'z sys zaimportuj stdin si',
            'z sys zaimportuj stdin,'
            'z sys zaimportuj (*)',
            'z sys zaimportuj (stdin,, stdout, stderr)',
            'z sys zaimportuj (stdin, stdout),',
            ]
        dla stmt w succeed:
            compile(stmt, 'tmp', 'exec')
        dla stmt w fail:
            self.assertRaises(SyntaxError, compile, stmt, 'tmp', 'exec')

    def test_for_distinct_code_objects(self):
        # SF bug 1048870
        def f():
            f1 = lambda x=1: x
            f2 = lambda x=2: x
            zwróć f1, f2
        f1, f2 = f()
        self.assertNotEqual(id(f1.__code__), id(f2.__code__))

    def test_lambda_doc(self):
        l = lambda: "foo"
        self.assertIsNic(l.__doc__)

    def test_encoding(self):
        code = b'# -*- coding: badencoding -*-\npass\n'
        self.assertRaises(SyntaxError, compile, code, 'tmp', 'exec')
        code = '# -*- coding: badencoding -*-\n"\xc2\xa4"\n'
        compile(code, 'tmp', 'exec')
        self.assertEqual(eval(code), '\xc2\xa4')
        code = '"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xc2\xa4')
        code = b'"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xa4')
        code = b'# -*- coding: latin1 -*-\n"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xc2\xa4')
        code = b'# -*- coding: utf-8 -*-\n"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xa4')
        code = b'# -*- coding: iso8859-15 -*-\n"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xc2\u20ac')
        code = '"""\\\n# -*- coding: iso8859-15 -*-\n\xc2\xa4"""\n'
        self.assertEqual(eval(code), '# -*- coding: iso8859-15 -*-\n\xc2\xa4')
        code = b'"""\\\n# -*- coding: iso8859-15 -*-\n\xc2\xa4"""\n'
        self.assertEqual(eval(code), '# -*- coding: iso8859-15 -*-\n\xa4')

    def test_subscripts(self):
        # SF bug 1448804
        # Class to make testing subscript results easy
        klasa str_map(object):
            def __init__(self):
                self.data = {}
            def __getitem__(self, key):
                zwróć self.data[str(key)]
            def __setitem__(self, key, value):
                self.data[str(key)] = value
            def __delitem__(self, key):
                usuń self.data[str(key)]
            def __contains__(self, key):
                zwróć str(key) w self.data
        d = str_map()
        # Index
        d[1] = 1
        self.assertEqual(d[1], 1)
        d[1] += 1
        self.assertEqual(d[1], 2)
        usuń d[1]
        self.assertNotIn(1, d)
        # Tuple of indices
        d[1, 1] = 1
        self.assertEqual(d[1, 1], 1)
        d[1, 1] += 1
        self.assertEqual(d[1, 1], 2)
        usuń d[1, 1]
        self.assertNotIn((1, 1), d)
        # Simple slice
        d[1:2] = 1
        self.assertEqual(d[1:2], 1)
        d[1:2] += 1
        self.assertEqual(d[1:2], 2)
        usuń d[1:2]
        self.assertNotIn(slice(1, 2), d)
        # Tuple of simple slices
        d[1:2, 1:2] = 1
        self.assertEqual(d[1:2, 1:2], 1)
        d[1:2, 1:2] += 1
        self.assertEqual(d[1:2, 1:2], 2)
        usuń d[1:2, 1:2]
        self.assertNotIn((slice(1, 2), slice(1, 2)), d)
        # Extended slice
        d[1:2:3] = 1
        self.assertEqual(d[1:2:3], 1)
        d[1:2:3] += 1
        self.assertEqual(d[1:2:3], 2)
        usuń d[1:2:3]
        self.assertNotIn(slice(1, 2, 3), d)
        # Tuple of extended slices
        d[1:2:3, 1:2:3] = 1
        self.assertEqual(d[1:2:3, 1:2:3], 1)
        d[1:2:3, 1:2:3] += 1
        self.assertEqual(d[1:2:3, 1:2:3], 2)
        usuń d[1:2:3, 1:2:3]
        self.assertNotIn((slice(1, 2, 3), slice(1, 2, 3)), d)
        # Ellipsis
        d[...] = 1
        self.assertEqual(d[...], 1)
        d[...] += 1
        self.assertEqual(d[...], 2)
        usuń d[...]
        self.assertNotIn(Ellipsis, d)
        # Tuple of Ellipses
        d[..., ...] = 1
        self.assertEqual(d[..., ...], 1)
        d[..., ...] += 1
        self.assertEqual(d[..., ...], 2)
        usuń d[..., ...]
        self.assertNotIn((Ellipsis, Ellipsis), d)

    def test_annotation_limit(self):
        # 16 bits are available dla # of annotations, but only 8 bits are
        # available dla the parameter count, hence 255
        # jest the max. Ensure the result of too many annotations jest a
        # SyntaxError.
        s = "def f(%s): dalej"
        s %= ', '.join('a%d:%d' % (i,i) dla i w range(256))
        self.assertRaises(SyntaxError, compile, s, '?', 'exec')
        # Test that the max # of annotations compiles.
        s = "def f(%s): dalej"
        s %= ', '.join('a%d:%d' % (i,i) dla i w range(255))
        compile(s, '?', 'exec')

    def test_mangling(self):
        klasa A:
            def f():
                __mangled = 1
                __not_mangled__ = 2
                zaimportuj __mangled_mod
                zaimportuj __package__.module

        self.assertIn("_A__mangled", A.f.__code__.co_varnames)
        self.assertIn("__not_mangled__", A.f.__code__.co_varnames)
        self.assertIn("_A__mangled_mod", A.f.__code__.co_varnames)
        self.assertIn("__package__", A.f.__code__.co_varnames)

    def test_compile_ast(self):
        fname = __file__
        jeżeli fname.lower().endswith('pyc'):
            fname = fname[:-1]
        przy open(fname, 'r') jako f:
            fcontents = f.read()
        sample_code = [
            ['<assign>', 'x = 5'],
            ['<ifblock>', """jeżeli Prawda:\n    dalej\n"""],
            ['<forblock>', """dla n w [1, 2, 3]:\n    print(n)\n"""],
            ['<deffunc>', """def foo():\n    dalej\nfoo()\n"""],
            [fname, fcontents],
        ]

        dla fname, code w sample_code:
            co1 = compile(code, '%s1' % fname, 'exec')
            ast = compile(code, '%s2' % fname, 'exec', _ast.PyCF_ONLY_AST)
            self.assertPrawda(type(ast) == _ast.Module)
            co2 = compile(ast, '%s3' % fname, 'exec')
            self.assertEqual(co1, co2)
            # the code object's filename comes z the second compilation step
            self.assertEqual(co2.co_filename, '%s3' % fname)

        # podnieś exception when node type doesn't match przy compile mode
        co1 = compile('print(1)', '<string>', 'exec', _ast.PyCF_ONLY_AST)
        self.assertRaises(TypeError, compile, co1, '<ast>', 'eval')

        # podnieś exception when node type jest no start node
        self.assertRaises(TypeError, compile, _ast.If(), '<ast>', 'exec')

        # podnieś exception when node has invalid children
        ast = _ast.Module()
        ast.body = [_ast.BoolOp()]
        self.assertRaises(TypeError, compile, ast, '<ast>', 'exec')

    def test_dict_evaluation_order(self):
        i = 0

        def f():
            nonlocal i
            i += 1
            zwróć i

        d = {f(): f(), f(): f()}
        self.assertEqual(d, {1: 2, 3: 4})

    @support.cpython_only
    def test_same_filename_used(self):
        s = """def f(): dalej\ndef g(): dalej"""
        c = compile(s, "myfile", "exec")
        dla obj w c.co_consts:
            jeżeli isinstance(obj, types.CodeType):
                self.assertIs(obj.co_filename, c.co_filename)

    def test_single_statement(self):
        self.compile_single("1 + 2")
        self.compile_single("\n1 + 2")
        self.compile_single("1 + 2\n")
        self.compile_single("1 + 2\n\n")
        self.compile_single("1 + 2\t\t\n")
        self.compile_single("1 + 2\t\t\n        ")
        self.compile_single("1 + 2 # one plus two")
        self.compile_single("1; 2")
        self.compile_single("zaimportuj sys; sys")
        self.compile_single("def f():\n   dalej")
        self.compile_single("dopóki Nieprawda:\n   dalej")
        self.compile_single("jeżeli x:\n   f(x)")
        self.compile_single("jeżeli x:\n   f(x)\ninaczej:\n   g(x)")
        self.compile_single("class T:\n   dalej")

    def test_bad_single_statement(self):
        self.assertInvalidSingle('1\n2')
        self.assertInvalidSingle('def f(): dalej')
        self.assertInvalidSingle('a = 13\nb = 187')
        self.assertInvalidSingle('usuń x\nusuń y')
        self.assertInvalidSingle('f()\ng()')
        self.assertInvalidSingle('f()\n# blah\nblah()')
        self.assertInvalidSingle('f()\nxy # blah\nblah()')
        self.assertInvalidSingle('x = 5 # comment\nx = 6\n')

    def test_particularly_evil_undecodable(self):
        # Issue 24022
        src = b'0000\x00\n00000000000\n\x00\n\x9e\n'
        przy tempfile.TemporaryDirectory() jako tmpd:
            fn = os.path.join(tmpd, "bad.py")
            przy open(fn, "wb") jako fp:
                fp.write(src)
            res = script_helper.run_python_until_end(fn)[0]
        self.assertIn(b"Non-UTF-8", res.err)

    @support.cpython_only
    def test_compiler_recursion_limit(self):
        # Expected limit jest sys.getrecursionlimit() * the scaling factor
        # w symtable.c (currently 3)
        # We expect to fail *at* that limit, because we use up some of
        # the stack depth limit w the test suite code
        # So we check the expected limit oraz 75% of that
        # XXX (ncoghlan): duplicating the scaling factor here jest a little
        # ugly. Perhaps it should be exposed somewhere...
        fail_depth = sys.getrecursionlimit() * 3
        success_depth = int(fail_depth * 0.75)

        def check_limit(prefix, repeated):
            expect_ok = prefix + repeated * success_depth
            self.compile_single(expect_ok)
            broken = prefix + repeated * fail_depth
            details = "Compiling ({!r} + {!r} * {})".format(
                         prefix, repeated, fail_depth)
            przy self.assertRaises(RecursionError, msg=details):
                self.compile_single(broken)

        check_limit("a", "()")
        check_limit("a", ".b")
        check_limit("a", "[0]")
        check_limit("a", "*a")


klasa TestStackSize(unittest.TestCase):
    # These tests check that the computed stack size dla a code object
    # stays within reasonable bounds (see issue #21523 dla an example
    # dysfunction).
    N = 100

    def check_stack_size(self, code):
        # To assert that the alleged stack size jest nie O(N), we
        # check that it jest smaller than log(N).
        jeżeli isinstance(code, str):
            code = compile(code, "<foo>", "single")
        max_size = math.ceil(math.log(len(code.co_code)))
        self.assertLessEqual(code.co_stacksize, max_size)

    def test_and(self):
        self.check_stack_size("x oraz " * self.N + "x")

    def test_or(self):
        self.check_stack_size("x albo " * self.N + "x")

    def test_and_or(self):
        self.check_stack_size("x oraz x albo " * self.N + "x")

    def test_chained_comparison(self):
        self.check_stack_size("x < " * self.N + "x")

    def test_if_inaczej(self):
        self.check_stack_size("x jeżeli x inaczej " * self.N + "x")

    def test_binop(self):
        self.check_stack_size("x + " * self.N + "x")

    def test_func_and(self):
        code = "def f(x):\n"
        code += "   x oraz x\n" * self.N
        self.check_stack_size(code)


jeżeli __name__ == "__main__":
    unittest.main()
