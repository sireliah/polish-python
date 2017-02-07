# Testing the line trace facility.

z test zaimportuj support
zaimportuj unittest
zaimportuj sys
zaimportuj difflib
zaimportuj gc

# A very basic example.  If this fails, we're w deep trouble.
def basic():
    zwróć 1

basic.events = [(0, 'call'),
                (1, 'line'),
                (1, 'return')]

# Many of the tests below are tricky because they involve dalej statements.
# If there jest implicit control flow around a dalej statement (in an except
# clause albo inaczej caluse) under what conditions do you set a line number
# following that clause?


# The entire "dopóki 0:" statement jest optimized away.  No code
# exists dla it, so the line numbers skip directly z "usuń x"
# to "x = 1".
def arigo_example():
    x = 1
    usuń x
    dopóki 0:
        dalej
    x = 1

arigo_example.events = [(0, 'call'),
                        (1, 'line'),
                        (2, 'line'),
                        (5, 'line'),
                        (5, 'return')]

# check that lines consisting of just one instruction get traced:
def one_instr_line():
    x = 1
    usuń x
    x = 1

one_instr_line.events = [(0, 'call'),
                         (1, 'line'),
                         (2, 'line'),
                         (3, 'line'),
                         (3, 'return')]

def no_pop_tops():      # 0
    x = 1               # 1
    dla a w range(2):  # 2
        jeżeli a:           # 3
            x = 1       # 4
        inaczej:           # 5
            x = 1       # 6

no_pop_tops.events = [(0, 'call'),
                      (1, 'line'),
                      (2, 'line'),
                      (3, 'line'),
                      (6, 'line'),
                      (2, 'line'),
                      (3, 'line'),
                      (4, 'line'),
                      (2, 'line'),
                      (2, 'return')]

def no_pop_blocks():
    y = 1
    dopóki nie y:
        bla
    x = 1

no_pop_blocks.events = [(0, 'call'),
                        (1, 'line'),
                        (2, 'line'),
                        (4, 'line'),
                        (4, 'return')]

def called(): # line -3
    x = 1

def call():   # line 0
    called()

call.events = [(0, 'call'),
               (1, 'line'),
               (-3, 'call'),
               (-2, 'line'),
               (-2, 'return'),
               (1, 'return')]

def podnieśs():
    podnieś Exception

def test_raise():
    spróbuj:
        podnieśs()
    wyjąwszy Exception jako exc:
        x = 1

test_raise.events = [(0, 'call'),
                     (1, 'line'),
                     (2, 'line'),
                     (-3, 'call'),
                     (-2, 'line'),
                     (-2, 'exception'),
                     (-2, 'return'),
                     (2, 'exception'),
                     (3, 'line'),
                     (4, 'line'),
                     (4, 'return')]

def _settrace_and_return(tracefunc):
    sys.settrace(tracefunc)
    sys._getframe().f_back.f_trace = tracefunc
def settrace_and_return(tracefunc):
    _settrace_and_return(tracefunc)

settrace_and_return.events = [(1, 'return')]

def _settrace_and_raise(tracefunc):
    sys.settrace(tracefunc)
    sys._getframe().f_back.f_trace = tracefunc
    podnieś RuntimeError
def settrace_and_raise(tracefunc):
    spróbuj:
        _settrace_and_raise(tracefunc)
    wyjąwszy RuntimeError jako exc:
        dalej

settrace_and_raise.events = [(2, 'exception'),
                             (3, 'line'),
                             (4, 'line'),
                             (4, 'return')]

# implicit zwróć example
# This test jest interesting because of the inaczej: dalej
# part of the code.  The code generate dla the true
# part of the jeżeli contains a jump past the inaczej branch.
# The compiler then generates an implicit "return Nic"
# Internally, the compiler visits the dalej statement
# oraz stores its line number dla use on the next instruction.
# The next instruction jest the implicit zwróć Nic.
def ireturn_example():
    a = 5
    b = 5
    jeżeli a == b:
        b = a+1
    inaczej:
        dalej

ireturn_example.events = [(0, 'call'),
                          (1, 'line'),
                          (2, 'line'),
                          (3, 'line'),
                          (4, 'line'),
                          (6, 'line'),
                          (6, 'return')]

# Tight loop przy while(1) example (SF #765624)
def tightloop_example():
    items = range(0, 3)
    spróbuj:
        i = 0
        dopóki 1:
            b = items[i]; i+=1
    wyjąwszy IndexError:
        dalej

tightloop_example.events = [(0, 'call'),
                            (1, 'line'),
                            (2, 'line'),
                            (3, 'line'),
                            (4, 'line'),
                            (5, 'line'),
                            (5, 'line'),
                            (5, 'line'),
                            (5, 'line'),
                            (5, 'exception'),
                            (6, 'line'),
                            (7, 'line'),
                            (7, 'return')]

def tighterloop_example():
    items = range(1, 4)
    spróbuj:
        i = 0
        dopóki 1: i = items[i]
    wyjąwszy IndexError:
        dalej

tighterloop_example.events = [(0, 'call'),
                            (1, 'line'),
                            (2, 'line'),
                            (3, 'line'),
                            (4, 'line'),
                            (4, 'line'),
                            (4, 'line'),
                            (4, 'line'),
                            (4, 'exception'),
                            (5, 'line'),
                            (6, 'line'),
                            (6, 'return')]

def generator_function():
    spróbuj:
        uzyskaj Prawda
        "continued"
    w_końcu:
        "finally"
def generator_example():
    # any() will leave the generator before its end
    x = any(generator_function())

    # the following lines were nie traced
    dla x w range(10):
        y = x

generator_example.events = ([(0, 'call'),
                             (2, 'line'),
                             (-6, 'call'),
                             (-5, 'line'),
                             (-4, 'line'),
                             (-4, 'return'),
                             (-4, 'call'),
                             (-4, 'exception'),
                             (-1, 'line'),
                             (-1, 'return')] +
                            [(5, 'line'), (6, 'line')] * 10 +
                            [(5, 'line'), (5, 'return')])


klasa Tracer:
    def __init__(self):
        self.events = []
    def trace(self, frame, event, arg):
        self.events.append((frame.f_lineno, event))
        zwróć self.trace
    def traceWithGenexp(self, frame, event, arg):
        (o dla o w [1])
        self.events.append((frame.f_lineno, event))
        zwróć self.trace

klasa TraceTestCase(unittest.TestCase):

    # Disable gc collection when tracing, otherwise the
    # deallocators may be traced jako well.
    def setUp(self):
        self.using_gc = gc.isenabled()
        gc.disable()
        self.addCleanup(sys.settrace, sys.gettrace())

    def tearDown(self):
        jeżeli self.using_gc:
            gc.enable()

    def compare_events(self, line_offset, events, expected_events):
        events = [(l - line_offset, e) dla (l, e) w events]
        jeżeli events != expected_events:
            self.fail(
                "events did nie match expectation:\n" +
                "\n".join(difflib.ndiff([str(x) dla x w expected_events],
                                        [str(x) dla x w events])))

    def run_and_compare(self, func, events):
        tracer = Tracer()
        sys.settrace(tracer.trace)
        func()
        sys.settrace(Nic)
        self.compare_events(func.__code__.co_firstlineno,
                            tracer.events, events)

    def run_test(self, func):
        self.run_and_compare(func, func.events)

    def run_test2(self, func):
        tracer = Tracer()
        func(tracer.trace)
        sys.settrace(Nic)
        self.compare_events(func.__code__.co_firstlineno,
                            tracer.events, func.events)

    def test_set_and_retrieve_none(self):
        sys.settrace(Nic)
        assert sys.gettrace() jest Nic

    def test_set_and_retrieve_func(self):
        def fn(*args):
            dalej

        sys.settrace(fn)
        spróbuj:
            assert sys.gettrace() jest fn
        w_końcu:
            sys.settrace(Nic)

    def test_01_basic(self):
        self.run_test(basic)
    def test_02_arigo(self):
        self.run_test(arigo_example)
    def test_03_one_instr(self):
        self.run_test(one_instr_line)
    def test_04_no_pop_blocks(self):
        self.run_test(no_pop_blocks)
    def test_05_no_pop_tops(self):
        self.run_test(no_pop_tops)
    def test_06_call(self):
        self.run_test(call)
    def test_07_raise(self):
        self.run_test(test_raise)

    def test_08_settrace_and_return(self):
        self.run_test2(settrace_and_return)
    def test_09_settrace_and_raise(self):
        self.run_test2(settrace_and_raise)
    def test_10_ireturn(self):
        self.run_test(ireturn_example)
    def test_11_tightloop(self):
        self.run_test(tightloop_example)
    def test_12_tighterloop(self):
        self.run_test(tighterloop_example)

    def test_13_genexp(self):
        self.run_test(generator_example)
        # issue1265: jeżeli the trace function contains a generator,
        # oraz jeżeli the traced function contains another generator
        # that jest nie completely exhausted, the trace stopped.
        # Worse: the 'finally' clause was nie invoked.
        tracer = Tracer()
        sys.settrace(tracer.traceWithGenexp)
        generator_example()
        sys.settrace(Nic)
        self.compare_events(generator_example.__code__.co_firstlineno,
                            tracer.events, generator_example.events)

    def test_14_onliner_if(self):
        def onliners():
            jeżeli Prawda: Nieprawda
            inaczej: Prawda
            zwróć 0
        self.run_and_compare(
            onliners,
            [(0, 'call'),
             (1, 'line'),
             (3, 'line'),
             (3, 'return')])

    def test_15_loops(self):
        # issue1750076: "while" expression jest skipped by debugger
        def for_example():
            dla x w range(2):
                dalej
        self.run_and_compare(
            for_example,
            [(0, 'call'),
             (1, 'line'),
             (2, 'line'),
             (1, 'line'),
             (2, 'line'),
             (1, 'line'),
             (1, 'return')])

        def while_example():
            # While expression should be traced on every loop
            x = 2
            dopóki x > 0:
                x -= 1
        self.run_and_compare(
            while_example,
            [(0, 'call'),
             (2, 'line'),
             (3, 'line'),
             (4, 'line'),
             (3, 'line'),
             (4, 'line'),
             (3, 'line'),
             (3, 'return')])

    def test_16_blank_lines(self):
        namespace = {}
        exec("def f():\n" + "\n" * 256 + "    dalej", namespace)
        self.run_and_compare(
            namespace["f"],
            [(0, 'call'),
             (257, 'line'),
             (257, 'return')])


klasa RaisingTraceFuncTestCase(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())

    def trace(self, frame, event, arg):
        """A trace function that podnieśs an exception w response to a
        specific trace event."""
        jeżeli event == self.raiseOnEvent:
            podnieś ValueError # just something that isn't RuntimeError
        inaczej:
            zwróć self.trace

    def f(self):
        """The function to trace; podnieśs an exception jeżeli that's the case
        we're testing, so that the 'exception' trace event fires."""
        jeżeli self.raiseOnEvent == 'exception':
            x = 0
            y = 1/x
        inaczej:
            zwróć 1

    def run_test_for_event(self, event):
        """Tests that an exception podnieśd w response to the given event jest
        handled OK."""
        self.raiseOnEvent = event
        spróbuj:
            dla i w range(sys.getrecursionlimit() + 1):
                sys.settrace(self.trace)
                spróbuj:
                    self.f()
                wyjąwszy ValueError:
                    dalej
                inaczej:
                    self.fail("exception nie podnieśd!")
        wyjąwszy RuntimeError:
            self.fail("recursion counter nie reset")

    # Test the handling of exceptions podnieśd by each kind of trace event.
    def test_call(self):
        self.run_test_for_event('call')
    def test_line(self):
        self.run_test_for_event('line')
    def test_return(self):
        self.run_test_for_event('return')
    def test_exception(self):
        self.run_test_for_event('exception')

    def test_trash_stack(self):
        def f():
            dla i w range(5):
                print(i)  # line tracing will podnieś an exception at this line

        def g(frame, why, extra):
            jeżeli (why == 'line' oraz
                frame.f_lineno == f.__code__.co_firstlineno + 2):
                podnieś RuntimeError("i am crashing")
            zwróć g

        sys.settrace(g)
        spróbuj:
            f()
        wyjąwszy RuntimeError:
            # the test jest really that this doesn't segfault:
            zaimportuj gc
            gc.collect()
        inaczej:
            self.fail("exception nie propagated")


    def test_exception_arguments(self):
        def f():
            x = 0
            # this should podnieś an error
            x.no_such_attr
        def g(frame, event, arg):
            jeżeli (event == 'exception'):
                type, exception, trace = arg
                self.assertIsInstance(exception, Exception)
            zwróć g

        existing = sys.gettrace()
        spróbuj:
            sys.settrace(g)
            spróbuj:
                f()
            wyjąwszy AttributeError:
                # this jest expected
                dalej
        w_końcu:
            sys.settrace(existing)


# 'Jump' tests: assigning to frame.f_lineno within a trace function
# moves the execution position - it's how debuggers implement a Jump
# command (aka. "Set next statement").

klasa JumpTracer:
    """Defines a trace function that jumps z one place to another,
    przy the source oraz destination lines of the jump being defined by
    the 'jump' property of the function under test."""

    def __init__(self, function):
        self.function = function
        self.jumpFrom = function.jump[0]
        self.jumpTo = function.jump[1]
        self.done = Nieprawda

    def trace(self, frame, event, arg):
        jeżeli nie self.done oraz frame.f_code == self.function.__code__:
            firstLine = frame.f_code.co_firstlineno
            jeżeli event == 'line' oraz frame.f_lineno == firstLine + self.jumpFrom:
                # Cope przy non-integer self.jumpTo (because of
                # no_jump_to_non_integers below).
                spróbuj:
                    frame.f_lineno = firstLine + self.jumpTo
                wyjąwszy TypeError:
                    frame.f_lineno = self.jumpTo
                self.done = Prawda
        zwróć self.trace

# The first set of 'jump' tests are dla things that are allowed:

def jump_simple_forwards(output):
    output.append(1)
    output.append(2)
    output.append(3)

jump_simple_forwards.jump = (1, 3)
jump_simple_forwards.output = [3]

def jump_simple_backwards(output):
    output.append(1)
    output.append(2)

jump_simple_backwards.jump = (2, 1)
jump_simple_backwards.output = [1, 1, 2]

def jump_out_of_block_forwards(output):
    dla i w 1, 2:
        output.append(2)
        dla j w [3]:  # Also tests jumping over a block
            output.append(4)
    output.append(5)

jump_out_of_block_forwards.jump = (3, 5)
jump_out_of_block_forwards.output = [2, 5]

def jump_out_of_block_backwards(output):
    output.append(1)
    dla i w [1]:
        output.append(3)
        dla j w [2]:  # Also tests jumping over a block
            output.append(5)
        output.append(6)
    output.append(7)

jump_out_of_block_backwards.jump = (6, 1)
jump_out_of_block_backwards.output = [1, 3, 5, 1, 3, 5, 6, 7]

def jump_to_codeless_line(output):
    output.append(1)
    # Jumping to this line should skip to the next one.
    output.append(3)

jump_to_codeless_line.jump = (1, 2)
jump_to_codeless_line.output = [3]

def jump_to_same_line(output):
    output.append(1)
    output.append(2)
    output.append(3)

jump_to_same_line.jump = (2, 2)
jump_to_same_line.output = [1, 2, 3]

# Tests jumping within a finally block, oraz over one.
def jump_in_nested_finally(output):
    spróbuj:
        output.append(2)
    w_końcu:
        output.append(4)
        spróbuj:
            output.append(6)
        w_końcu:
            output.append(8)
        output.append(9)

jump_in_nested_finally.jump = (4, 9)
jump_in_nested_finally.output = [2, 9]

def jump_infinite_while_loop(output):
    output.append(1)
    dopóki 1:
        output.append(2)
    output.append(3)

jump_infinite_while_loop.jump = (3, 4)
jump_infinite_while_loop.output = [1, 3]

# The second set of 'jump' tests are dla things that are nie allowed:

def no_jump_too_far_forwards(output):
    spróbuj:
        output.append(2)
        output.append(3)
    wyjąwszy ValueError jako e:
        output.append('after' w str(e))

no_jump_too_far_forwards.jump = (3, 6)
no_jump_too_far_forwards.output = [2, Prawda]

def no_jump_too_far_backwards(output):
    spróbuj:
        output.append(2)
        output.append(3)
    wyjąwszy ValueError jako e:
        output.append('before' w str(e))

no_jump_too_far_backwards.jump = (3, -1)
no_jump_too_far_backwards.output = [2, Prawda]

# Test each kind of 'except' line.
def no_jump_to_except_1(output):
    spróbuj:
        output.append(2)
    wyjąwszy:
        e = sys.exc_info()[1]
        output.append('except' w str(e))

no_jump_to_except_1.jump = (2, 3)
no_jump_to_except_1.output = [Prawda]

def no_jump_to_except_2(output):
    spróbuj:
        output.append(2)
    wyjąwszy ValueError:
        e = sys.exc_info()[1]
        output.append('except' w str(e))

no_jump_to_except_2.jump = (2, 3)
no_jump_to_except_2.output = [Prawda]

def no_jump_to_except_3(output):
    spróbuj:
        output.append(2)
    wyjąwszy ValueError jako e:
        output.append('except' w str(e))

no_jump_to_except_3.jump = (2, 3)
no_jump_to_except_3.output = [Prawda]

def no_jump_to_except_4(output):
    spróbuj:
        output.append(2)
    wyjąwszy (ValueError, RuntimeError) jako e:
        output.append('except' w str(e))

no_jump_to_except_4.jump = (2, 3)
no_jump_to_except_4.output = [Prawda]

def no_jump_forwards_into_block(output):
    spróbuj:
        output.append(2)
        dla i w 1, 2:
            output.append(4)
    wyjąwszy ValueError jako e:
        output.append('into' w str(e))

no_jump_forwards_into_block.jump = (2, 4)
no_jump_forwards_into_block.output = [Prawda]

def no_jump_backwards_into_block(output):
    spróbuj:
        dla i w 1, 2:
            output.append(3)
        output.append(4)
    wyjąwszy ValueError jako e:
        output.append('into' w str(e))

no_jump_backwards_into_block.jump = (4, 3)
no_jump_backwards_into_block.output = [3, 3, Prawda]

def no_jump_into_finally_block(output):
    spróbuj:
        spróbuj:
            output.append(3)
            x = 1
        w_końcu:
            output.append(6)
    wyjąwszy ValueError jako e:
        output.append('finally' w str(e))

no_jump_into_finally_block.jump = (4, 6)
no_jump_into_finally_block.output = [3, 6, Prawda]  # The 'finally' still runs

def no_jump_out_of_finally_block(output):
    spróbuj:
        spróbuj:
            output.append(3)
        w_końcu:
            output.append(5)
            output.append(6)
    wyjąwszy ValueError jako e:
        output.append('finally' w str(e))

no_jump_out_of_finally_block.jump = (5, 1)
no_jump_out_of_finally_block.output = [3, Prawda]

# This verifies the line-numbers-must-be-integers rule.
def no_jump_to_non_integers(output):
    spróbuj:
        output.append(2)
    wyjąwszy ValueError jako e:
        output.append('integer' w str(e))

no_jump_to_non_integers.jump = (2, "Spam")
no_jump_to_non_integers.output = [Prawda]

def jump_across_with(output):
    przy open(support.TESTFN, "wb") jako fp:
        dalej
    przy open(support.TESTFN, "wb") jako fp:
        dalej
jump_across_with.jump = (1, 3)
jump_across_with.output = []

# This verifies that you can't set f_lineno via _getframe albo similar
# trickery.
def no_jump_without_trace_function():
    spróbuj:
        previous_frame = sys._getframe().f_back
        previous_frame.f_lineno = previous_frame.f_lineno
    wyjąwszy ValueError jako e:
        # This jest the exception we wanted; make sure the error message
        # talks about trace functions.
        jeżeli 'trace' nie w str(e):
            podnieś
    inaczej:
        # Something's wrong - the expected exception wasn't podnieśd.
        podnieś RuntimeError("Trace-function-less jump failed to fail")


klasa JumpTestCase(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())
        sys.settrace(Nic)

    def compare_jump_output(self, expected, received):
        jeżeli received != expected:
            self.fail( "Outputs don't match:\n" +
                       "Expected: " + repr(expected) + "\n" +
                       "Received: " + repr(received))

    def run_test(self, func):
        tracer = JumpTracer(func)
        sys.settrace(tracer.trace)
        output = []
        func(output)
        sys.settrace(Nic)
        self.compare_jump_output(func.output, output)

    def test_01_jump_simple_forwards(self):
        self.run_test(jump_simple_forwards)
    def test_02_jump_simple_backwards(self):
        self.run_test(jump_simple_backwards)
    def test_03_jump_out_of_block_forwards(self):
        self.run_test(jump_out_of_block_forwards)
    def test_04_jump_out_of_block_backwards(self):
        self.run_test(jump_out_of_block_backwards)
    def test_05_jump_to_codeless_line(self):
        self.run_test(jump_to_codeless_line)
    def test_06_jump_to_same_line(self):
        self.run_test(jump_to_same_line)
    def test_07_jump_in_nested_finally(self):
        self.run_test(jump_in_nested_finally)
    def test_jump_infinite_while_loop(self):
        self.run_test(jump_infinite_while_loop)
    def test_08_no_jump_too_far_forwards(self):
        self.run_test(no_jump_too_far_forwards)
    def test_09_no_jump_too_far_backwards(self):
        self.run_test(no_jump_too_far_backwards)
    def test_10_no_jump_to_except_1(self):
        self.run_test(no_jump_to_except_1)
    def test_11_no_jump_to_except_2(self):
        self.run_test(no_jump_to_except_2)
    def test_12_no_jump_to_except_3(self):
        self.run_test(no_jump_to_except_3)
    def test_13_no_jump_to_except_4(self):
        self.run_test(no_jump_to_except_4)
    def test_14_no_jump_forwards_into_block(self):
        self.run_test(no_jump_forwards_into_block)
    def test_15_no_jump_backwards_into_block(self):
        self.run_test(no_jump_backwards_into_block)
    def test_16_no_jump_into_finally_block(self):
        self.run_test(no_jump_into_finally_block)
    def test_17_no_jump_out_of_finally_block(self):
        self.run_test(no_jump_out_of_finally_block)
    def test_18_no_jump_to_non_integers(self):
        self.run_test(no_jump_to_non_integers)
    def test_19_no_jump_without_trace_function(self):
        # Must set sys.settrace(Nic) w setUp(), inaczej condition jest nie
        # triggered.
        no_jump_without_trace_function()
    def test_jump_across_with(self):
        self.addCleanup(support.unlink, support.TESTFN)
        self.run_test(jump_across_with)

    def test_20_large_function(self):
        d = {}
        exec("""def f(output):        # line 0
            x = 0                     # line 1
            y = 1                     # line 2
            '''                       # line 3
            %s                        # lines 4-1004
            '''                       # line 1005
            x += 1                    # line 1006
            output.append(x)          # line 1007
            return""" % ('\n' * 1000,), d)
        f = d['f']

        f.jump = (2, 1007)
        f.output = [0]
        self.run_test(f)

    def test_jump_to_firstlineno(self):
        # This tests that PDB can jump back to the first line w a
        # file.  See issue #1689458.  It can only be triggered w a
        # function call jeżeli the function jest defined on a single line.
        code = compile("""
# Comments don't count.
output.append(2)  # firstlineno jest here.
output.append(3)
output.append(4)
""", "<fake module>", "exec")
        klasa fake_function:
            __code__ = code
            jump = (2, 0)
        tracer = JumpTracer(fake_function)
        sys.settrace(tracer.trace)
        namespace = {"output": []}
        exec(code, namespace)
        sys.settrace(Nic)
        self.compare_jump_output([2, 3, 2, 3, 4], namespace["output"])


def test_main():
    support.run_unittest(
        TraceTestCase,
        RaisingTraceFuncTestCase,
        JumpTestCase
    )

jeżeli __name__ == "__main__":
    test_main()
