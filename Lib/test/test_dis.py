# Minimal tests dla dis module

z test.support zaimportuj captured_stdout
z test.bytecode_helper zaimportuj BytecodeTestCase
zaimportuj difflib
zaimportuj unittest
zaimportuj sys
zaimportuj dis
zaimportuj io
zaimportuj re
zaimportuj types
zaimportuj contextlib

def get_tb():
    def _error():
        spróbuj:
            1 / 0
        wyjąwszy Exception jako e:
            tb = e.__traceback__
        zwróć tb

    tb = _error()
    dopóki tb.tb_next:
        tb = tb.tb_next
    zwróć tb

TRACEBACK_CODE = get_tb().tb_frame.f_code

klasa _C:
    def __init__(self, x):
        self.x = x == 1

dis_c_instance_method = """\
 %-4d         0 LOAD_FAST                1 (x)
              3 LOAD_CONST               1 (1)
              6 COMPARE_OP               2 (==)
              9 LOAD_FAST                0 (self)
             12 STORE_ATTR               0 (x)
             15 LOAD_CONST               0 (Nic)
             18 RETURN_VALUE
""" % (_C.__init__.__code__.co_firstlineno + 1,)

dis_c_instance_method_bytes = """\
          0 LOAD_FAST                1 (1)
          3 LOAD_CONST               1 (1)
          6 COMPARE_OP               2 (==)
          9 LOAD_FAST                0 (0)
         12 STORE_ATTR               0 (0)
         15 LOAD_CONST               0 (0)
         18 RETURN_VALUE
"""

def _f(a):
    print(a)
    zwróć 1

dis_f = """\
 %-4d         0 LOAD_GLOBAL              0 (print)
              3 LOAD_FAST                0 (a)
              6 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
              9 POP_TOP

 %-4d        10 LOAD_CONST               1 (1)
             13 RETURN_VALUE
""" % (_f.__code__.co_firstlineno + 1,
       _f.__code__.co_firstlineno + 2)


dis_f_co_code = """\
          0 LOAD_GLOBAL              0 (0)
          3 LOAD_FAST                0 (0)
          6 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
          9 POP_TOP
         10 LOAD_CONST               1 (1)
         13 RETURN_VALUE
"""


def bug708901():
    dla res w range(1,
                     10):
        dalej

dis_bug708901 = """\
 %-4d         0 SETUP_LOOP              23 (to 26)
              3 LOAD_GLOBAL              0 (range)
              6 LOAD_CONST               1 (1)

 %-4d         9 LOAD_CONST               2 (10)
             12 CALL_FUNCTION            2 (2 positional, 0 keyword pair)
             15 GET_ITER
        >>   16 FOR_ITER                 6 (to 25)
             19 STORE_FAST               0 (res)

 %-4d        22 JUMP_ABSOLUTE           16
        >>   25 POP_BLOCK
        >>   26 LOAD_CONST               0 (Nic)
             29 RETURN_VALUE
""" % (bug708901.__code__.co_firstlineno + 1,
       bug708901.__code__.co_firstlineno + 2,
       bug708901.__code__.co_firstlineno + 3)


def bug1333982(x=[]):
    assert 0, ([s dla s w x] +
              1)
    dalej

dis_bug1333982 = """\
%3d           0 LOAD_CONST               1 (0)
              3 POP_JUMP_IF_TRUE        35
              6 LOAD_GLOBAL              0 (AssertionError)
              9 LOAD_CONST               2 (<code object <listcomp> at 0x..., file "%s", line %d>)
             12 LOAD_CONST               3 ('bug1333982.<locals>.<listcomp>')
             15 MAKE_FUNCTION            0
             18 LOAD_FAST                0 (x)
             21 GET_ITER
             22 CALL_FUNCTION            1 (1 positional, 0 keyword pair)

%3d          25 LOAD_CONST               4 (1)
             28 BINARY_ADD
             29 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             32 RAISE_VARARGS            1

%3d     >>   35 LOAD_CONST               0 (Nic)
             38 RETURN_VALUE
""" % (bug1333982.__code__.co_firstlineno + 1,
       __file__,
       bug1333982.__code__.co_firstlineno + 1,
       bug1333982.__code__.co_firstlineno + 2,
       bug1333982.__code__.co_firstlineno + 3)

_BIG_LINENO_FORMAT = """\
%3d           0 LOAD_GLOBAL              0 (spam)
              3 POP_TOP
              4 LOAD_CONST               0 (Nic)
              7 RETURN_VALUE
"""

dis_module_expected_results = """\
Disassembly of f:
  4           0 LOAD_CONST               0 (Nic)
              3 RETURN_VALUE

Disassembly of g:
  5           0 LOAD_CONST               0 (Nic)
              3 RETURN_VALUE

"""

expr_str = "x + 1"

dis_expr_str = """\
  1           0 LOAD_NAME                0 (x)
              3 LOAD_CONST               0 (1)
              6 BINARY_ADD
              7 RETURN_VALUE
"""

simple_stmt_str = "x = x + 1"

dis_simple_stmt_str = """\
  1           0 LOAD_NAME                0 (x)
              3 LOAD_CONST               0 (1)
              6 BINARY_ADD
              7 STORE_NAME               0 (x)
             10 LOAD_CONST               1 (Nic)
             13 RETURN_VALUE
"""

compound_stmt_str = """\
x = 0
dopóki 1:
    x += 1"""
# Trailing newline has been deliberately omitted

dis_compound_stmt_str = """\
  1           0 LOAD_CONST               0 (0)
              3 STORE_NAME               0 (x)

  2           6 SETUP_LOOP              14 (to 23)

  3     >>    9 LOAD_NAME                0 (x)
             12 LOAD_CONST               1 (1)
             15 INPLACE_ADD
             16 STORE_NAME               0 (x)
             19 JUMP_ABSOLUTE            9
             22 POP_BLOCK
        >>   23 LOAD_CONST               2 (Nic)
             26 RETURN_VALUE
"""

dis_traceback = """\
 %-4d         0 SETUP_EXCEPT            12 (to 15)

 %-4d         3 LOAD_CONST               1 (1)
              6 LOAD_CONST               2 (0)
    -->       9 BINARY_TRUE_DIVIDE
             10 POP_TOP
             11 POP_BLOCK
             12 JUMP_FORWARD            46 (to 61)

 %-4d   >>   15 DUP_TOP
             16 LOAD_GLOBAL              0 (Exception)
             19 COMPARE_OP              10 (exception match)
             22 POP_JUMP_IF_FALSE       60
             25 POP_TOP
             26 STORE_FAST               0 (e)
             29 POP_TOP
             30 SETUP_FINALLY           14 (to 47)

 %-4d        33 LOAD_FAST                0 (e)
             36 LOAD_ATTR                1 (__traceback__)
             39 STORE_FAST               1 (tb)
             42 POP_BLOCK
             43 POP_EXCEPT
             44 LOAD_CONST               0 (Nic)
        >>   47 LOAD_CONST               0 (Nic)
             50 STORE_FAST               0 (e)
             53 DELETE_FAST              0 (e)
             56 END_FINALLY
             57 JUMP_FORWARD             1 (to 61)
        >>   60 END_FINALLY

 %-4d   >>   61 LOAD_FAST                1 (tb)
             64 RETURN_VALUE
""" % (TRACEBACK_CODE.co_firstlineno + 1,
       TRACEBACK_CODE.co_firstlineno + 2,
       TRACEBACK_CODE.co_firstlineno + 3,
       TRACEBACK_CODE.co_firstlineno + 4,
       TRACEBACK_CODE.co_firstlineno + 5)

def _g(x):
    uzyskaj x

klasa DisTests(unittest.TestCase):

    def get_disassembly(self, func, lasti=-1, wrapper=Prawda):
        # We want to test the default printing behaviour, nie the file arg
        output = io.StringIO()
        przy contextlib.redirect_stdout(output):
            jeżeli wrapper:
                dis.dis(func)
            inaczej:
                dis.disassemble(func, lasti)
        zwróć output.getvalue()

    def get_disassemble_as_string(self, func, lasti=-1):
        zwróć self.get_disassembly(func, lasti, Nieprawda)

    def strip_addresses(self, text):
        zwróć re.sub(r'\b0x[0-9A-Fa-f]+\b', '0x...', text)

    def do_disassembly_test(self, func, expected):
        got = self.get_disassembly(func)
        jeżeli got != expected:
            got = self.strip_addresses(got)
        self.assertEqual(got, expected)

    def test_opmap(self):
        self.assertEqual(dis.opmap["NOP"], 9)
        self.assertIn(dis.opmap["LOAD_CONST"], dis.hasconst)
        self.assertIn(dis.opmap["STORE_NAME"], dis.hasname)

    def test_opname(self):
        self.assertEqual(dis.opname[dis.opmap["LOAD_FAST"]], "LOAD_FAST")

    def test_boundaries(self):
        self.assertEqual(dis.opmap["EXTENDED_ARG"], dis.EXTENDED_ARG)
        self.assertEqual(dis.opmap["STORE_NAME"], dis.HAVE_ARGUMENT)

    def test_dis(self):
        self.do_disassembly_test(_f, dis_f)

    def test_bug_708901(self):
        self.do_disassembly_test(bug708901, dis_bug708901)

    def test_bug_1333982(self):
        # This one jest checking bytecodes generated dla an `assert` statement,
        # so fails jeżeli the tests are run przy -O.  Skip this test then.
        jeżeli nie __debug__:
            self.skipTest('need asserts, run without -O')

        self.do_disassembly_test(bug1333982, dis_bug1333982)

    def test_big_linenos(self):
        def func(count):
            namespace = {}
            func = "def foo():\n " + "".join(["\n "] * count + ["spam\n"])
            exec(func, namespace)
            zwróć namespace['foo']

        # Test all small ranges
        dla i w range(1, 300):
            expected = _BIG_LINENO_FORMAT % (i + 2)
            self.do_disassembly_test(func(i), expected)

        # Test some larger ranges too
        dla i w range(300, 5000, 10):
            expected = _BIG_LINENO_FORMAT % (i + 2)
            self.do_disassembly_test(func(i), expected)

        z test zaimportuj dis_module
        self.do_disassembly_test(dis_module, dis_module_expected_results)

    def test_disassemble_str(self):
        self.do_disassembly_test(expr_str, dis_expr_str)
        self.do_disassembly_test(simple_stmt_str, dis_simple_stmt_str)
        self.do_disassembly_test(compound_stmt_str, dis_compound_stmt_str)

    def test_disassemble_bytes(self):
        self.do_disassembly_test(_f.__code__.co_code, dis_f_co_code)

    def test_disassemble_method(self):
        self.do_disassembly_test(_C(1).__init__, dis_c_instance_method)

    def test_disassemble_method_bytes(self):
        method_bytecode = _C(1).__init__.__code__.co_code
        self.do_disassembly_test(method_bytecode, dis_c_instance_method_bytes)

    def test_disassemble_generator(self):
        gen_func_disas = self.get_disassembly(_g)  # Disassemble generator function
        gen_disas = self.get_disassembly(_g(1))  # Disassemble generator itself
        self.assertEqual(gen_disas, gen_func_disas)

    def test_dis_none(self):
        spróbuj:
            usuń sys.last_traceback
        wyjąwszy AttributeError:
            dalej
        self.assertRaises(RuntimeError, dis.dis, Nic)

    def test_dis_traceback(self):
        spróbuj:
            usuń sys.last_traceback
        wyjąwszy AttributeError:
            dalej

        spróbuj:
            1/0
        wyjąwszy Exception jako e:
            tb = e.__traceback__
            sys.last_traceback = tb

        tb_dis = self.get_disassemble_as_string(tb.tb_frame.f_code, tb.tb_lasti)
        self.do_disassembly_test(Nic, tb_dis)

    def test_dis_object(self):
        self.assertRaises(TypeError, dis.dis, object())

klasa DisWithFileTests(DisTests):

    # Run the tests again, using the file arg instead of print
    def get_disassembly(self, func, lasti=-1, wrapper=Prawda):
        output = io.StringIO()
        jeżeli wrapper:
            dis.dis(func, file=output)
        inaczej:
            dis.disassemble(func, lasti, file=output)
        zwróć output.getvalue()



code_info_code_info = """\
Name:              code_info
Filename:          (.*)
Argument count:    1
Kw-only arguments: 0
Number of locals:  1
Stack size:        3
Flags:             OPTIMIZED, NEWLOCALS, NOFREE
Constants:
   0: %r
Names:
   0: _format_code_info
   1: _get_code_object
Variable names:
   0: x""" % (('Formatted details of methods, functions, albo code.',)
              jeżeli sys.flags.optimize < 2 inaczej (Nic,))

@staticmethod
def tricky(x, y, z=Prawda, *args, c, d, e=[], **kwds):
    def f(c=c):
        print(x, y, z, c, d, e, f)
    uzyskaj x, y, z, c, d, e, f

code_info_tricky = """\
Name:              tricky
Filename:          (.*)
Argument count:    3
Kw-only arguments: 3
Number of locals:  8
Stack size:        7
Flags:             OPTIMIZED, NEWLOCALS, VARARGS, VARKEYWORDS, GENERATOR
Constants:
   0: Nic
   1: <code object f at (.*), file "(.*)", line (.*)>
   2: 'tricky.<locals>.f'
Variable names:
   0: x
   1: y
   2: z
   3: c
   4: d
   5: e
   6: args
   7: kwds
Cell variables:
   0: [edfxyz]
   1: [edfxyz]
   2: [edfxyz]
   3: [edfxyz]
   4: [edfxyz]
   5: [edfxyz]"""
# NOTE: the order of the cell variables above depends on dictionary order!

co_tricky_nested_f = tricky.__func__.__code__.co_consts[1]

code_info_tricky_nested_f = """\
Name:              f
Filename:          (.*)
Argument count:    1
Kw-only arguments: 0
Number of locals:  1
Stack size:        8
Flags:             OPTIMIZED, NEWLOCALS, NESTED
Constants:
   0: Nic
Names:
   0: print
Variable names:
   0: c
Free variables:
   0: [edfxyz]
   1: [edfxyz]
   2: [edfxyz]
   3: [edfxyz]
   4: [edfxyz]
   5: [edfxyz]"""

code_info_expr_str = """\
Name:              <module>
Filename:          <disassembly>
Argument count:    0
Kw-only arguments: 0
Number of locals:  0
Stack size:        2
Flags:             NOFREE
Constants:
   0: 1
Names:
   0: x"""

code_info_simple_stmt_str = """\
Name:              <module>
Filename:          <disassembly>
Argument count:    0
Kw-only arguments: 0
Number of locals:  0
Stack size:        2
Flags:             NOFREE
Constants:
   0: 1
   1: Nic
Names:
   0: x"""

code_info_compound_stmt_str = """\
Name:              <module>
Filename:          <disassembly>
Argument count:    0
Kw-only arguments: 0
Number of locals:  0
Stack size:        2
Flags:             NOFREE
Constants:
   0: 0
   1: 1
   2: Nic
Names:
   0: x"""


async def async_def():
    await 1
    async dla a w b: dalej
    async przy c jako d: dalej

code_info_async_def = """\
Name:              async_def
Filename:          (.*)
Argument count:    0
Kw-only arguments: 0
Number of locals:  2
Stack size:        17
Flags:             OPTIMIZED, NEWLOCALS, GENERATOR, NOFREE, COROUTINE
Constants:
   0: Nic
   1: 1"""

klasa CodeInfoTests(unittest.TestCase):
    test_pairs = [
      (dis.code_info, code_info_code_info),
      (tricky, code_info_tricky),
      (co_tricky_nested_f, code_info_tricky_nested_f),
      (expr_str, code_info_expr_str),
      (simple_stmt_str, code_info_simple_stmt_str),
      (compound_stmt_str, code_info_compound_stmt_str),
      (async_def, code_info_async_def)
    ]

    def test_code_info(self):
        self.maxDiff = 1000
        dla x, expected w self.test_pairs:
            self.assertRegex(dis.code_info(x), expected)

    def test_show_code(self):
        self.maxDiff = 1000
        dla x, expected w self.test_pairs:
            przy captured_stdout() jako output:
                dis.show_code(x)
            self.assertRegex(output.getvalue(), expected+"\n")
            output = io.StringIO()
            dis.show_code(x, file=output)
            self.assertRegex(output.getvalue(), expected)

    def test_code_info_object(self):
        self.assertRaises(TypeError, dis.code_info, object())

    def test_pretty_flags_no_flags(self):
        self.assertEqual(dis.pretty_flags(0), '0x0')


# Fodder dla instruction introspection tests
#   Editing any of these may require recalculating the expected output
def outer(a=1, b=2):
    def f(c=3, d=4):
        def inner(e=5, f=6):
            print(a, b, c, d, e, f)
        print(a, b, c, d)
        zwróć inner
    print(a, b, '', 1, [], {}, "Hello world!")
    zwróć f

def jumpy():
    # This won't actually run (but that's OK, we only disassemble it)
    dla i w range(10):
        print(i)
        jeżeli i < 4:
            kontynuuj
        jeżeli i > 6:
            przerwij
    inaczej:
        print("I can haz inaczej clause?")
    dopóki i:
        print(i)
        i -= 1
        jeżeli i > 6:
            kontynuuj
        jeżeli i < 4:
            przerwij
    inaczej:
        print("Who let lolcatz into this test suite?")
    spróbuj:
        1 / 0
    wyjąwszy ZeroDivisionError:
        print("Here we go, here we go, here we go...")
    inaczej:
        przy i jako dodgy:
            print("Never reach this")
    w_końcu:
        print("OK, now we're done")

# End fodder dla opinfo generation tests
expected_outer_line = 1
_line_offset = outer.__code__.co_firstlineno - 1
code_object_f = outer.__code__.co_consts[3]
expected_f_line = code_object_f.co_firstlineno - _line_offset
code_object_inner = code_object_f.co_consts[3]
expected_inner_line = code_object_inner.co_firstlineno - _line_offset
expected_jumpy_line = 1

# The following lines are useful to regenerate the expected results after
# either the fodder jest modified albo the bytecode generation changes
# After regeneration, update the references to code_object_f oraz
# code_object_inner before rerunning the tests

#_instructions = dis.get_instructions(outer, first_line=expected_outer_line)
#print('expected_opinfo_outer = [\n  ',
      #',\n  '.join(map(str, _instructions)), ',\n]', sep='')
#_instructions = dis.get_instructions(outer(), first_line=expected_f_line)
#print('expected_opinfo_f = [\n  ',
      #',\n  '.join(map(str, _instructions)), ',\n]', sep='')
#_instructions = dis.get_instructions(outer()(), first_line=expected_inner_line)
#print('expected_opinfo_inner = [\n  ',
      #',\n  '.join(map(str, _instructions)), ',\n]', sep='')
#_instructions = dis.get_instructions(jumpy, first_line=expected_jumpy_line)
#print('expected_opinfo_jumpy = [\n  ',
      #',\n  '.join(map(str, _instructions)), ',\n]', sep='')


Instruction = dis.Instruction
expected_opinfo_outer = [
  Instruction(opname='LOAD_CONST', opcode=100, arg=1, argval=3, argrepr='3', offset=0, starts_line=2, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=2, argval=4, argrepr='4', offset=3, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=0, argval='a', argrepr='a', offset=6, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=1, argval='b', argrepr='b', offset=9, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='BUILD_TUPLE', opcode=102, arg=2, argval=2, argrepr='', offset=12, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=3, argval=code_object_f, argrepr=repr(code_object_f), offset=15, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=4, argval='outer.<locals>.f', argrepr="'outer.<locals>.f'", offset=18, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='MAKE_CLOSURE', opcode=134, arg=2, argval=2, argrepr='', offset=21, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='STORE_FAST', opcode=125, arg=2, argval='f', argrepr='f', offset=24, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=0, argval='print', argrepr='print', offset=27, starts_line=7, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=0, argval='a', argrepr='a', offset=30, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=1, argval='b', argrepr='b', offset=33, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=5, argval='', argrepr="''", offset=36, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=6, argval=1, argrepr='1', offset=39, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='BUILD_LIST', opcode=103, arg=0, argval=0, argrepr='', offset=42, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='BUILD_MAP', opcode=105, arg=0, argval=0, argrepr='', offset=45, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=7, argval='Hello world!', argrepr="'Hello world!'", offset=48, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=7, argval=7, argrepr='7 positional, 0 keyword pair', offset=51, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=54, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=2, argval='f', argrepr='f', offset=55, starts_line=8, is_jump_target=Nieprawda),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Nic, argval=Nic, argrepr='', offset=58, starts_line=Nic, is_jump_target=Nieprawda),
]

expected_opinfo_f = [
  Instruction(opname='LOAD_CONST', opcode=100, arg=1, argval=5, argrepr='5', offset=0, starts_line=3, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=2, argval=6, argrepr='6', offset=3, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=2, argval='a', argrepr='a', offset=6, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=3, argval='b', argrepr='b', offset=9, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=0, argval='c', argrepr='c', offset=12, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=1, argval='d', argrepr='d', offset=15, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='BUILD_TUPLE', opcode=102, arg=4, argval=4, argrepr='', offset=18, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=3, argval=code_object_inner, argrepr=repr(code_object_inner), offset=21, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=4, argval='outer.<locals>.f.<locals>.inner', argrepr="'outer.<locals>.f.<locals>.inner'", offset=24, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='MAKE_CLOSURE', opcode=134, arg=2, argval=2, argrepr='', offset=27, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='STORE_FAST', opcode=125, arg=2, argval='inner', argrepr='inner', offset=30, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=0, argval='print', argrepr='print', offset=33, starts_line=5, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=2, argval='a', argrepr='a', offset=36, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=3, argval='b', argrepr='b', offset=39, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=0, argval='c', argrepr='c', offset=42, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=1, argval='d', argrepr='d', offset=45, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=4, argval=4, argrepr='4 positional, 0 keyword pair', offset=48, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=51, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=2, argval='inner', argrepr='inner', offset=52, starts_line=6, is_jump_target=Nieprawda),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Nic, argval=Nic, argrepr='', offset=55, starts_line=Nic, is_jump_target=Nieprawda),
]

expected_opinfo_inner = [
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=0, argval='print', argrepr='print', offset=0, starts_line=4, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=0, argval='a', argrepr='a', offset=3, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=1, argval='b', argrepr='b', offset=6, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=2, argval='c', argrepr='c', offset=9, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=3, argval='d', argrepr='d', offset=12, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='e', argrepr='e', offset=15, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=1, argval='f', argrepr='f', offset=18, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=6, argval=6, argrepr='6 positional, 0 keyword pair', offset=21, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=24, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=Nic, argrepr='Nic', offset=25, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Nic, argval=Nic, argrepr='', offset=28, starts_line=Nic, is_jump_target=Nieprawda),
]

expected_opinfo_jumpy = [
  Instruction(opname='SETUP_LOOP', opcode=120, arg=68, argval=71, argrepr='to 71', offset=0, starts_line=3, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=0, argval='range', argrepr='range', offset=3, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=1, argval=10, argrepr='10', offset=6, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', offset=9, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='GET_ITER', opcode=68, arg=Nic, argval=Nic, argrepr='', offset=12, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='FOR_ITER', opcode=93, arg=44, argval=60, argrepr='to 60', offset=13, starts_line=Nic, is_jump_target=Prawda),
  Instruction(opname='STORE_FAST', opcode=125, arg=0, argval='i', argrepr='i', offset=16, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=19, starts_line=4, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=22, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', offset=25, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=28, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=29, starts_line=5, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=2, argval=4, argrepr='4', offset=32, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='COMPARE_OP', opcode=107, arg=0, argval='<', argrepr='<', offset=35, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=44, argval=44, argrepr='', offset=38, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=13, argval=13, argrepr='', offset=41, starts_line=6, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=44, starts_line=7, is_jump_target=Prawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=3, argval=6, argrepr='6', offset=47, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='COMPARE_OP', opcode=107, arg=4, argval='>', argrepr='>', offset=50, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=13, argval=13, argrepr='', offset=53, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='BREAK_LOOP', opcode=80, arg=Nic, argval=Nic, argrepr='', offset=56, starts_line=8, is_jump_target=Nieprawda),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=13, argval=13, argrepr='', offset=57, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_BLOCK', opcode=87, arg=Nic, argval=Nic, argrepr='', offset=60, starts_line=Nic, is_jump_target=Prawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=61, starts_line=10, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=4, argval='I can haz inaczej clause?', argrepr="'I can haz inaczej clause?'", offset=64, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', offset=67, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=70, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='SETUP_LOOP', opcode=120, arg=68, argval=142, argrepr='to 142', offset=71, starts_line=11, is_jump_target=Prawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=74, starts_line=Nic, is_jump_target=Prawda),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=131, argval=131, argrepr='', offset=77, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=80, starts_line=12, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=83, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', offset=86, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=89, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=90, starts_line=13, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=5, argval=1, argrepr='1', offset=93, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='INPLACE_SUBTRACT', opcode=56, arg=Nic, argval=Nic, argrepr='', offset=96, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='STORE_FAST', opcode=125, arg=0, argval='i', argrepr='i', offset=97, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=100, starts_line=14, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=3, argval=6, argrepr='6', offset=103, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='COMPARE_OP', opcode=107, arg=4, argval='>', argrepr='>', offset=106, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=115, argval=115, argrepr='', offset=109, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=74, argval=74, argrepr='', offset=112, starts_line=15, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=115, starts_line=16, is_jump_target=Prawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=2, argval=4, argrepr='4', offset=118, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='COMPARE_OP', opcode=107, arg=0, argval='<', argrepr='<', offset=121, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=74, argval=74, argrepr='', offset=124, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='BREAK_LOOP', opcode=80, arg=Nic, argval=Nic, argrepr='', offset=127, starts_line=17, is_jump_target=Nieprawda),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=74, argval=74, argrepr='', offset=128, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_BLOCK', opcode=87, arg=Nic, argval=Nic, argrepr='', offset=131, starts_line=Nic, is_jump_target=Prawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=132, starts_line=19, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=6, argval='Who let lolcatz into this test suite?', argrepr="'Who let lolcatz into this test suite?'", offset=135, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', offset=138, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=141, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='SETUP_FINALLY', opcode=122, arg=73, argval=218, argrepr='to 218', offset=142, starts_line=20, is_jump_target=Prawda),
  Instruction(opname='SETUP_EXCEPT', opcode=121, arg=12, argval=160, argrepr='to 160', offset=145, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=5, argval=1, argrepr='1', offset=148, starts_line=21, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=7, argval=0, argrepr='0', offset=151, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='BINARY_TRUE_DIVIDE', opcode=27, arg=Nic, argval=Nic, argrepr='', offset=154, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=155, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_BLOCK', opcode=87, arg=Nic, argval=Nic, argrepr='', offset=156, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='JUMP_FORWARD', opcode=110, arg=28, argval=188, argrepr='to 188', offset=157, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='DUP_TOP', opcode=4, arg=Nic, argval=Nic, argrepr='', offset=160, starts_line=22, is_jump_target=Prawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=2, argval='ZeroDivisionError', argrepr='ZeroDivisionError', offset=161, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='COMPARE_OP', opcode=107, arg=10, argval='exception match', argrepr='exception match', offset=164, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=187, argval=187, argrepr='', offset=167, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=170, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=171, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=172, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=173, starts_line=23, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=8, argval='Here we go, here we go, here we go...', argrepr="'Here we go, here we go, here we go...'", offset=176, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', offset=179, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=182, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_EXCEPT', opcode=89, arg=Nic, argval=Nic, argrepr='', offset=183, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='JUMP_FORWARD', opcode=110, arg=27, argval=214, argrepr='to 214', offset=184, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='END_FINALLY', opcode=88, arg=Nic, argval=Nic, argrepr='', offset=187, starts_line=Nic, is_jump_target=Prawda),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=188, starts_line=25, is_jump_target=Prawda),
  Instruction(opname='SETUP_WITH', opcode=143, arg=17, argval=211, argrepr='to 211', offset=191, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='STORE_FAST', opcode=125, arg=1, argval='dodgy', argrepr='dodgy', offset=194, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=197, starts_line=26, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=9, argval='Never reach this', argrepr="'Never reach this'", offset=200, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', offset=203, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=206, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_BLOCK', opcode=87, arg=Nic, argval=Nic, argrepr='', offset=207, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=Nic, argrepr='Nic', offset=208, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='WITH_CLEANUP_START', opcode=81, arg=Nic, argval=Nic, argrepr='', offset=211, starts_line=Nic, is_jump_target=Prawda),
  Instruction(opname='WITH_CLEANUP_FINISH', opcode=82, arg=Nic, argval=Nic, argrepr='', offset=212, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='END_FINALLY', opcode=88, arg=Nic, argval=Nic, argrepr='', offset=213, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_BLOCK', opcode=87, arg=Nic, argval=Nic, argrepr='', offset=214, starts_line=Nic, is_jump_target=Prawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=Nic, argrepr='Nic', offset=215, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=218, starts_line=28, is_jump_target=Prawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=10, argval="OK, now we're done", argrepr='"OK, now we\'re done"', offset=221, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', offset=224, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='POP_TOP', opcode=1, arg=Nic, argval=Nic, argrepr='', offset=227, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='END_FINALLY', opcode=88, arg=Nic, argval=Nic, argrepr='', offset=228, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=Nic, argrepr='Nic', offset=229, starts_line=Nic, is_jump_target=Nieprawda),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Nic, argval=Nic, argrepr='', offset=232, starts_line=Nic, is_jump_target=Nieprawda),
]

# One last piece of inspect fodder to check the default line number handling
def simple(): dalej
expected_opinfo_simple = [
  Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=Nic, argrepr='Nic', offset=0, starts_line=simple.__code__.co_firstlineno, is_jump_target=Nieprawda),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Nic, argval=Nic, argrepr='', offset=3, starts_line=Nic, is_jump_target=Nieprawda)
]


klasa InstructionTests(BytecodeTestCase):

    def test_default_first_line(self):
        actual = dis.get_instructions(simple)
        self.assertEqual(list(actual), expected_opinfo_simple)

    def test_first_line_set_to_Nic(self):
        actual = dis.get_instructions(simple, first_line=Nic)
        self.assertEqual(list(actual), expected_opinfo_simple)

    def test_outer(self):
        actual = dis.get_instructions(outer, first_line=expected_outer_line)
        self.assertEqual(list(actual), expected_opinfo_outer)

    def test_nested(self):
        przy captured_stdout():
            f = outer()
        actual = dis.get_instructions(f, first_line=expected_f_line)
        self.assertEqual(list(actual), expected_opinfo_f)

    def test_doubly_nested(self):
        przy captured_stdout():
            inner = outer()()
        actual = dis.get_instructions(inner, first_line=expected_inner_line)
        self.assertEqual(list(actual), expected_opinfo_inner)

    def test_jumpy(self):
        actual = dis.get_instructions(jumpy, first_line=expected_jumpy_line)
        self.assertEqual(list(actual), expected_opinfo_jumpy)

# get_instructions has its own tests above, so can rely on it to validate
# the object oriented API
klasa BytecodeTests(unittest.TestCase):
    def test_instantiation(self):
        # Test przy function, method, code string oraz code object
        dla obj w [_f, _C(1).__init__, "a=1", _f.__code__]:
            przy self.subTest(obj=obj):
                b = dis.Bytecode(obj)
                self.assertIsInstance(b.codeobj, types.CodeType)

        self.assertRaises(TypeError, dis.Bytecode, object())

    def test_iteration(self):
        dla obj w [_f, _C(1).__init__, "a=1", _f.__code__]:
            przy self.subTest(obj=obj):
                via_object = list(dis.Bytecode(obj))
                via_generator = list(dis.get_instructions(obj))
                self.assertEqual(via_object, via_generator)

    def test_explicit_first_line(self):
        actual = dis.Bytecode(outer, first_line=expected_outer_line)
        self.assertEqual(list(actual), expected_opinfo_outer)

    def test_source_line_in_disassembly(self):
        # Use the line w the source code
        actual = dis.Bytecode(simple).dis()[:3]
        expected = "{:>3}".format(simple.__code__.co_firstlineno)
        self.assertEqual(actual, expected)
        # Use an explicit first line number
        actual = dis.Bytecode(simple, first_line=350).dis()[:3]
        self.assertEqual(actual, "350")

    def test_info(self):
        self.maxDiff = 1000
        dla x, expected w CodeInfoTests.test_pairs:
            b = dis.Bytecode(x)
            self.assertRegex(b.info(), expected)

    def test_disassembled(self):
        actual = dis.Bytecode(_f).dis()
        self.assertEqual(actual, dis_f)

    def test_from_traceback(self):
        tb = get_tb()
        b = dis.Bytecode.from_traceback(tb)
        dopóki tb.tb_next: tb = tb.tb_next

        self.assertEqual(b.current_offset, tb.tb_lasti)

    def test_from_traceback_dis(self):
        tb = get_tb()
        b = dis.Bytecode.from_traceback(tb)
        self.assertEqual(b.dis(), dis_traceback)

jeżeli __name__ == "__main__":
    unittest.main()
