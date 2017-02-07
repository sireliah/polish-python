zaimportuj dis
zaimportuj re
zaimportuj sys
z io zaimportuj StringIO
zaimportuj unittest
z math zaimportuj copysign

z test.bytecode_helper zaimportuj BytecodeTestCase

klasa TestTranforms(BytecodeTestCase):

    def test_unot(self):
        # UNARY_NOT POP_JUMP_IF_FALSE  -->  POP_JUMP_IF_TRUE'
        def unot(x):
            jeżeli nie x == 2:
                usuń x
        self.assertNotInBytecode(unot, 'UNARY_NOT')
        self.assertNotInBytecode(unot, 'POP_JUMP_IF_FALSE')
        self.assertInBytecode(unot, 'POP_JUMP_IF_TRUE')

    def test_elim_inversion_of_is_or_in(self):
        dla line, cmp_op w (
            ('not a jest b', 'is not',),
            ('not a w b', 'not in',),
            ('not a jest nie b', 'is',),
            ('not a nie w b', 'in',),
            ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'COMPARE_OP', cmp_op)

    def test_global_as_constant(self):
        # LOAD_GLOBAL Nic/Prawda/Nieprawda  -->  LOAD_CONST Nic/Prawda/Nieprawda
        def f(x):
            Nic
            Nic
            zwróć x
        def g(x):
            Prawda
            zwróć x
        def h(x):
            Nieprawda
            zwróć x
        dla func, elem w ((f, Nic), (g, Prawda), (h, Nieprawda)):
            self.assertNotInBytecode(func, 'LOAD_GLOBAL')
            self.assertInBytecode(func, 'LOAD_CONST', elem)
        def f():
            'Adding a docstring made this test fail w Py2.5.0'
            zwróć Nic
        self.assertNotInBytecode(f, 'LOAD_GLOBAL')
        self.assertInBytecode(f, 'LOAD_CONST', Nic)

    def test_while_one(self):
        # Skip over:  LOAD_CONST trueconst  POP_JUMP_IF_FALSE xx
        def f():
            dopóki 1:
                dalej
            zwróć list
        dla elem w ('LOAD_CONST', 'POP_JUMP_IF_FALSE'):
            self.assertNotInBytecode(f, elem)
        dla elem w ('JUMP_ABSOLUTE',):
            self.assertInBytecode(f, elem)

    def test_pack_unpack(self):
        dla line, elem w (
            ('a, = a,', 'LOAD_CONST',),
            ('a, b = a, b', 'ROT_TWO',),
            ('a, b, c = a, b, c', 'ROT_THREE',),
            ):
            code = compile(line,'','single')
            self.assertInBytecode(code, elem)
            self.assertNotInBytecode(code, 'BUILD_TUPLE')
            self.assertNotInBytecode(code, 'UNPACK_TUPLE')

    def test_folding_of_tuples_of_constants(self):
        dla line, elem w (
            ('a = 1,2,3', (1, 2, 3)),
            ('("a","b","c")', ('a', 'b', 'c')),
            ('a,b,c = 1,2,3', (1, 2, 3)),
            ('(Nic, 1, Nic)', (Nic, 1, Nic)),
            ('((1, 2), 3, 4)', ((1, 2), 3, 4)),
            ):
            code = compile(line,'','single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            self.assertNotInBytecode(code, 'BUILD_TUPLE')

        # Long tuples should be folded too.
        code = compile(repr(tuple(range(10000))),'','single')
        self.assertNotInBytecode(code, 'BUILD_TUPLE')
        # One LOAD_CONST dla the tuple, one dla the Nic zwróć value
        load_consts = [instr dla instr w dis.get_instructions(code)
                              jeżeli instr.opname == 'LOAD_CONST']
        self.assertEqual(len(load_consts), 2)

        # Bug 1053819:  Tuple of constants misidentified when presented with:
        # . . . opcode_with_arg 100   unary_opcode   BUILD_TUPLE 1  . . .
        # The following would segfault upon compilation
        def crater():
            (~[
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
            ],)

    def test_folding_of_lists_of_constants(self):
        dla line, elem w (
            # in/not w constants przy BUILD_LIST should be folded to a tuple:
            ('a w [1,2,3]', (1, 2, 3)),
            ('a nie w ["a","b","c"]', ('a', 'b', 'c')),
            ('a w [Nic, 1, Nic]', (Nic, 1, Nic)),
            ('a nie w [(1, 2), 3, 4]', ((1, 2), 3, 4)),
            ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            self.assertNotInBytecode(code, 'BUILD_LIST')

    def test_folding_of_sets_of_constants(self):
        dla line, elem w (
            # in/not w constants przy BUILD_SET should be folded to a frozenset:
            ('a w {1,2,3}', frozenset({1, 2, 3})),
            ('a nie w {"a","b","c"}', frozenset({'a', 'c', 'b'})),
            ('a w {Nic, 1, Nic}', frozenset({1, Nic})),
            ('a nie w {(1, 2), 3, 4}', frozenset({(1, 2), 3, 4})),
            ('a w {1, 2, 3, 3, 2, 1}', frozenset({1, 2, 3})),
            ):
            code = compile(line, '', 'single')
            self.assertNotInBytecode(code, 'BUILD_SET')
            self.assertInBytecode(code, 'LOAD_CONST', elem)

        # Ensure that the resulting code actually works:
        def f(a):
            zwróć a w {1, 2, 3}

        def g(a):
            zwróć a nie w {1, 2, 3}

        self.assertPrawda(f(3))
        self.assertPrawda(nie f(4))

        self.assertPrawda(nie g(3))
        self.assertPrawda(g(4))


    def test_folding_of_binops_on_constants(self):
        dla line, elem w (
            ('a = 2+3+4', 9),                   # chained fold
            ('"@"*4', '@@@@'),                  # check string ops
            ('a="abc" + "def"', 'abcdef'),      # check string ops
            ('a = 3**4', 81),                   # binary power
            ('a = 3*4', 12),                    # binary multiply
            ('a = 13//4', 3),                   # binary floor divide
            ('a = 14%4', 2),                    # binary modulo
            ('a = 2+3', 5),                     # binary add
            ('a = 13-4', 9),                    # binary subtract
            ('a = (12,13)[1]', 13),             # binary subscr
            ('a = 13 << 2', 52),                # binary lshift
            ('a = 13 >> 2', 3),                 # binary rshift
            ('a = 13 & 7', 5),                  # binary oraz
            ('a = 13 ^ 7', 10),                 # binary xor
            ('a = 13 | 7', 15),                 # binary albo
            ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            dla instr w dis.get_instructions(code):
                self.assertNieprawda(instr.opname.startswith('BINARY_'))

        # Verify that unfoldables are skipped
        code = compile('a=2+"b"', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', 2)
        self.assertInBytecode(code, 'LOAD_CONST', 'b')

        # Verify that large sequences do nie result z folding
        code = compile('a="x"*1000', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', 1000)

    def test_binary_subscr_on_unicode(self):
        # valid code get optimized
        code = compile('"foo"[0]', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', 'f')
        self.assertNotInBytecode(code, 'BINARY_SUBSCR')
        code = compile('"\u0061\uffff"[1]', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', '\uffff')
        self.assertNotInBytecode(code,'BINARY_SUBSCR')

        # With PEP 393, non-BMP char get optimized
        code = compile('"\U00012345"[0]', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', '\U00012345')
        self.assertNotInBytecode(code, 'BINARY_SUBSCR')

        # invalid code doesn't get optimized
        # out of range
        code = compile('"fuu"[10]', '', 'single')
        self.assertInBytecode(code, 'BINARY_SUBSCR')

    def test_folding_of_unaryops_on_constants(self):
        dla line, elem w (
            ('-0.5', -0.5),                     # unary negative
            ('-0.0', -0.0),                     # -0.0
            ('-(1.0-1.0)', -0.0),               # -0.0 after folding
            ('-0', 0),                          # -0
            ('~-2', 1),                         # unary invert
            ('+1', 1),                          # unary positive
        ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            dla instr w dis.get_instructions(code):
                self.assertNieprawda(instr.opname.startswith('UNARY_'))

        # Check that -0.0 works after marshaling
        def negzero():
            zwróć -(1.0-1.0)

        dla instr w dis.get_instructions(code):
            self.assertNieprawda(instr.opname.startswith('UNARY_'))

        # Verify that unfoldables are skipped
        dla line, elem, opname w (
            ('-"abc"', 'abc', 'UNARY_NEGATIVE'),
            ('~"abc"', 'abc', 'UNARY_INVERT'),
        ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            self.assertInBytecode(code, opname)

    def test_elim_extra_return(self):
        # RETURN LOAD_CONST Nic RETURN  -->  RETURN
        def f(x):
            zwróć x
        self.assertNotInBytecode(f, 'LOAD_CONST', Nic)
        returns = [instr dla instr w dis.get_instructions(f)
                          jeżeli instr.opname == 'RETURN_VALUE']
        self.assertEqual(len(returns), 1)

    def test_elim_jump_to_return(self):
        # JUMP_FORWARD to RETURN -->  RETURN
        def f(cond, true_value, false_value):
            zwróć true_value jeżeli cond inaczej false_value
        self.assertNotInBytecode(f, 'JUMP_FORWARD')
        self.assertNotInBytecode(f, 'JUMP_ABSOLUTE')
        returns = [instr dla instr w dis.get_instructions(f)
                          jeżeli instr.opname == 'RETURN_VALUE']
        self.assertEqual(len(returns), 2)

    def test_elim_jump_after_return1(self):
        # Eliminate dead code: jumps immediately after returns can't be reached
        def f(cond1, cond2):
            jeżeli cond1: zwróć 1
            jeżeli cond2: zwróć 2
            dopóki 1:
                zwróć 3
            dopóki 1:
                jeżeli cond1: zwróć 4
                zwróć 5
            zwróć 6
        self.assertNotInBytecode(f, 'JUMP_FORWARD')
        self.assertNotInBytecode(f, 'JUMP_ABSOLUTE')
        returns = [instr dla instr w dis.get_instructions(f)
                          jeżeli instr.opname == 'RETURN_VALUE']
        self.assertEqual(len(returns), 6)

    def test_elim_jump_after_return2(self):
        # Eliminate dead code: jumps immediately after returns can't be reached
        def f(cond1, cond2):
            dopóki 1:
                jeżeli cond1: zwróć 4
        self.assertNotInBytecode(f, 'JUMP_FORWARD')
        # There should be one jump dla the dopóki loop.
        returns = [instr dla instr w dis.get_instructions(f)
                          jeżeli instr.opname == 'JUMP_ABSOLUTE']
        self.assertEqual(len(returns), 1)
        returns = [instr dla instr w dis.get_instructions(f)
                          jeżeli instr.opname == 'RETURN_VALUE']
        self.assertEqual(len(returns), 2)

    def test_make_function_doesnt_bail(self):
        def f():
            def g()->1+1:
                dalej
            zwróć g
        self.assertNotInBytecode(f, 'BINARY_ADD')

    def test_constant_folding(self):
        # Issue #11244: aggressive constant folding.
        exprs = [
            '3 * -5',
            '-3 * 5',
            '2 * (3 * 4)',
            '(2 * 3) * 4',
            '(-1, 2, 3)',
            '(1, -2, 3)',
            '(1, 2, -3)',
            '(1, 2, -3) * 6',
            'lambda x: x w {(3 * -5) + (-1 - 6), (1, -2, 3) * 2, Nic}',
        ]
        dla e w exprs:
            code = compile(e, '', 'single')
            dla instr w dis.get_instructions(code):
                self.assertNieprawda(instr.opname.startswith('UNARY_'))
                self.assertNieprawda(instr.opname.startswith('BINARY_'))
                self.assertNieprawda(instr.opname.startswith('BUILD_'))


klasa TestBuglets(unittest.TestCase):

    def test_bug_11510(self):
        # folded constant set optimization was commingled przy the tuple
        # unpacking optimization which would fail jeżeli the set had duplicate
        # elements so that the set length was unexpected
        def f():
            x, y = {1, 1}
            zwróć x, y
        przy self.assertRaises(ValueError):
            f()


jeżeli __name__ == "__main__":
    unittest.main()
