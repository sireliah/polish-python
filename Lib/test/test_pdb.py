# A test suite dla pdb; nie very comprehensive at the moment.

zaimportuj doctest
zaimportuj pdb
zaimportuj sys
zaimportuj types
zaimportuj unittest
zaimportuj subprocess
zaimportuj textwrap

z test zaimportuj support
# This little helper klasa jest essential dla testing pdb under doctest.
z test.test_doctest zaimportuj _FakeInput


klasa PdbTestInput(object):
    """Context manager that makes testing Pdb w doctests easier."""

    def __init__(self, input):
        self.input = input

    def __enter__(self):
        self.real_stdin = sys.stdin
        sys.stdin = _FakeInput(self.input)
        self.orig_trace = sys.gettrace() jeżeli hasattr(sys, 'gettrace') inaczej Nic

    def __exit__(self, *exc):
        sys.stdin = self.real_stdin
        jeżeli self.orig_trace:
            sys.settrace(self.orig_trace)


def test_pdb_displayhook():
    """This tests the custom displayhook dla pdb.

    >>> def test_function(foo, bar):
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     dalej

    >>> przy PdbTestInput([
    ...     'foo',
    ...     'bar',
    ...     'dla i w range(5): print(i)',
    ...     'continue',
    ... ]):
    ...     test_function(1, Nic)
    > <doctest test.test_pdb.test_pdb_displayhook[0]>(3)test_function()
    -> dalej
    (Pdb) foo
    1
    (Pdb) bar
    (Pdb) dla i w range(5): print(i)
    0
    1
    2
    3
    4
    (Pdb) kontynuuj
    """


def test_pdb_basic_commands():
    """Test the basic commands of pdb.

    >>> def test_function_2(foo, bar='default'):
    ...     print(foo)
    ...     dla i w range(5):
    ...         print(i)
    ...     print(bar)
    ...     dla i w range(10):
    ...         never_executed
    ...     print('after for')
    ...     print('...')
    ...     zwróć foo.upper()

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     ret = test_function_2('baz')
    ...     print(ret)

    >>> przy PdbTestInput([  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ...     'step',       # entering the function call
    ...     'args',       # display function args
    ...     'list',       # list function source
    ...     'bt',         # display backtrace
    ...     'up',         # step up to test_function()
    ...     'down',       # step down to test_function_2() again
    ...     'next',       # stepping to print(foo)
    ...     'next',       # stepping to the dla loop
    ...     'step',       # stepping into the dla loop
    ...     'until',      # continuing until out of the dla loop
    ...     'next',       # executing the print(bar)
    ...     'jump 8',     # jump over second dla loop
    ...     'return',     # zwróć out of function
    ...     'retval',     # display zwróć value
    ...     'continue',
    ... ]):
    ...    test_function()
    > <doctest test.test_pdb.test_pdb_basic_commands[1]>(3)test_function()
    -> ret = test_function_2('baz')
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(1)test_function_2()
    -> def test_function_2(foo, bar='default'):
    (Pdb) args
    foo = 'baz'
    bar = 'default'
    (Pdb) list
      1  ->     def test_function_2(foo, bar='default'):
      2             print(foo)
      3             dla i w range(5):
      4                 print(i)
      5             print(bar)
      6             dla i w range(10):
      7                 never_executed
      8             print('after for')
      9             print('...')
     10             zwróć foo.upper()
    [EOF]
    (Pdb) bt
    ...
      <doctest test.test_pdb.test_pdb_basic_commands[2]>(18)<module>()
    -> test_function()
      <doctest test.test_pdb.test_pdb_basic_commands[1]>(3)test_function()
    -> ret = test_function_2('baz')
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(1)test_function_2()
    -> def test_function_2(foo, bar='default'):
    (Pdb) up
    > <doctest test.test_pdb.test_pdb_basic_commands[1]>(3)test_function()
    -> ret = test_function_2('baz')
    (Pdb) down
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(1)test_function_2()
    -> def test_function_2(foo, bar='default'):
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(2)test_function_2()
    -> print(foo)
    (Pdb) next
    baz
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(3)test_function_2()
    -> dla i w range(5):
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(4)test_function_2()
    -> print(i)
    (Pdb) until
    0
    1
    2
    3
    4
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(5)test_function_2()
    -> print(bar)
    (Pdb) next
    default
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(6)test_function_2()
    -> dla i w range(10):
    (Pdb) jump 8
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(8)test_function_2()
    -> print('after for')
    (Pdb) zwróć
    after for
    ...
    --Return--
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(10)test_function_2()->'BAZ'
    -> zwróć foo.upper()
    (Pdb) retval
    'BAZ'
    (Pdb) kontynuuj
    BAZ
    """


def test_pdb_breakpoint_commands():
    """Test basic commands related to przerwijpoints.

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     print(1)
    ...     print(2)
    ...     print(3)
    ...     print(4)

    First, need to clear bdb state that might be left over z previous tests.
    Otherwise, the new przerwijpoints might get assigned different numbers.

    >>> z bdb zaimportuj Breakpoint
    >>> Breakpoint.next = 1
    >>> Breakpoint.bplist = {}
    >>> Breakpoint.bpbynumber = [Nic]

    Now test the przerwijpoint commands.  NORMALIZE_WHITESPACE jest needed because
    the przerwijpoint list outputs a tab dla the "stop only" oraz "ignore next"
    lines, which we don't want to put w here.

    >>> przy PdbTestInput([  # doctest: +NORMALIZE_WHITESPACE
    ...     'break 3',
    ...     'disable 1',
    ...     'ignore 1 10',
    ...     'condition 1 1 < 2',
    ...     'break 4',
    ...     'break 4',
    ...     'break',
    ...     'clear 3',
    ...     'break',
    ...     'condition 1',
    ...     'enable 1',
    ...     'clear 1',
    ...     'commands 2',
    ...     'p "42"',
    ...     'print("42", 7*6)',     # Issue 18764 (nie about przerwijpoints)
    ...     'end',
    ...     'continue',  # will stop at przerwijpoint 2 (line 4)
    ...     'clear',     # clear all!
    ...     'y',
    ...     'tbreak 5',
    ...     'continue',  # will stop at temporary przerwijpoint
    ...     'break',     # make sure przerwijpoint jest gone
    ...     'continue',
    ... ]):
    ...    test_function()
    > <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>(3)test_function()
    -> print(1)
    (Pdb) przerwij 3
    Breakpoint 1 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:3
    (Pdb) disable 1
    Disabled przerwijpoint 1 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:3
    (Pdb) ignore 1 10
    Will ignore next 10 crossings of przerwijpoint 1.
    (Pdb) condition 1 1 < 2
    New condition set dla przerwijpoint 1.
    (Pdb) przerwij 4
    Breakpoint 2 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:4
    (Pdb) przerwij 4
    Breakpoint 3 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:4
    (Pdb) przerwij
    Num Type         Disp Enb   Where
    1   przerwijpoint   keep no    at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:3
            stop only jeżeli 1 < 2
            ignore next 10 hits
    2   przerwijpoint   keep yes   at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:4
    3   przerwijpoint   keep yes   at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:4
    (Pdb) clear 3
    Deleted przerwijpoint 3 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:4
    (Pdb) przerwij
    Num Type         Disp Enb   Where
    1   przerwijpoint   keep no    at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:3
            stop only jeżeli 1 < 2
            ignore next 10 hits
    2   przerwijpoint   keep yes   at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:4
    (Pdb) condition 1
    Breakpoint 1 jest now unconditional.
    (Pdb) enable 1
    Enabled przerwijpoint 1 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:3
    (Pdb) clear 1
    Deleted przerwijpoint 1 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:3
    (Pdb) commands 2
    (com) p "42"
    (com) print("42", 7*6)
    (com) end
    (Pdb) kontynuuj
    1
    '42'
    42 42
    > <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>(4)test_function()
    -> print(2)
    (Pdb) clear
    Clear all przerwijs? y
    Deleted przerwijpoint 2 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:4
    (Pdb) tbreak 5
    Breakpoint 4 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:5
    (Pdb) kontynuuj
    2
    Deleted przerwijpoint 4 at <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>:5
    > <doctest test.test_pdb.test_pdb_breakpoint_commands[0]>(5)test_function()
    -> print(3)
    (Pdb) przerwij
    (Pdb) kontynuuj
    3
    4
    """


def do_nothing():
    dalej

def do_something():
    print(42)

def test_list_commands():
    """Test the list oraz source commands of pdb.

    >>> def test_function_2(foo):
    ...     zaimportuj test.test_pdb
    ...     test.test_pdb.do_nothing()
    ...     'some...'
    ...     'more...'
    ...     'code...'
    ...     'to...'
    ...     'make...'
    ...     'a...'
    ...     'long...'
    ...     'listing...'
    ...     'useful...'
    ...     '...'
    ...     '...'
    ...     zwróć foo

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     ret = test_function_2('baz')

    >>> przy PdbTestInput([  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ...     'list',      # list first function
    ...     'step',      # step into second function
    ...     'list',      # list second function
    ...     'list',      # continue listing to EOF
    ...     'list 1,3',  # list specific lines
    ...     'list x',    # invalid argument
    ...     'next',      # step to import
    ...     'next',      # step over import
    ...     'step',      # step into do_nothing
    ...     'longlist',  # list all lines
    ...     'source do_something',  # list all lines of function
    ...     'source fooxxx',        # something that doesn't exit
    ...     'continue',
    ... ]):
    ...    test_function()
    > <doctest test.test_pdb.test_list_commands[1]>(3)test_function()
    -> ret = test_function_2('baz')
    (Pdb) list
      1         def test_function():
      2             zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
      3  ->         ret = test_function_2('baz')
    [EOF]
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_list_commands[0]>(1)test_function_2()
    -> def test_function_2(foo):
    (Pdb) list
      1  ->     def test_function_2(foo):
      2             zaimportuj test.test_pdb
      3             test.test_pdb.do_nothing()
      4             'some...'
      5             'more...'
      6             'code...'
      7             'to...'
      8             'make...'
      9             'a...'
     10             'long...'
     11             'listing...'
    (Pdb) list
     12             'useful...'
     13             '...'
     14             '...'
     15             zwróć foo
    [EOF]
    (Pdb) list 1,3
      1  ->     def test_function_2(foo):
      2             zaimportuj test.test_pdb
      3             test.test_pdb.do_nothing()
    (Pdb) list x
    *** ...
    (Pdb) next
    > <doctest test.test_pdb.test_list_commands[0]>(2)test_function_2()
    -> zaimportuj test.test_pdb
    (Pdb) next
    > <doctest test.test_pdb.test_list_commands[0]>(3)test_function_2()
    -> test.test_pdb.do_nothing()
    (Pdb) step
    --Call--
    > ...test_pdb.py(...)do_nothing()
    -> def do_nothing():
    (Pdb) longlist
    ...  ->     def do_nothing():
    ...             dalej
    (Pdb) source do_something
    ...         def do_something():
    ...             print(42)
    (Pdb) source fooxxx
    *** ...
    (Pdb) kontynuuj
    """


def test_post_mortem():
    """Test post mortem traceback debugging.

    >>> def test_function_2():
    ...     spróbuj:
    ...         1/0
    ...     w_końcu:
    ...         print('Exception!')

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     test_function_2()
    ...     print('Not reached.')

    >>> przy PdbTestInput([  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ...     'next',      # step over exception-raising call
    ...     'bt',        # get a backtrace
    ...     'list',      # list code of test_function()
    ...     'down',      # step into test_function_2()
    ...     'list',      # list code of test_function_2()
    ...     'continue',
    ... ]):
    ...    spróbuj:
    ...        test_function()
    ...    wyjąwszy ZeroDivisionError:
    ...        print('Correctly reraised.')
    > <doctest test.test_pdb.test_post_mortem[1]>(3)test_function()
    -> test_function_2()
    (Pdb) next
    Exception!
    ZeroDivisionError: division by zero
    > <doctest test.test_pdb.test_post_mortem[1]>(3)test_function()
    -> test_function_2()
    (Pdb) bt
    ...
      <doctest test.test_pdb.test_post_mortem[2]>(10)<module>()
    -> test_function()
    > <doctest test.test_pdb.test_post_mortem[1]>(3)test_function()
    -> test_function_2()
      <doctest test.test_pdb.test_post_mortem[0]>(3)test_function_2()
    -> 1/0
    (Pdb) list
      1         def test_function():
      2             zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
      3  ->         test_function_2()
      4             print('Not reached.')
    [EOF]
    (Pdb) down
    > <doctest test.test_pdb.test_post_mortem[0]>(3)test_function_2()
    -> 1/0
    (Pdb) list
      1         def test_function_2():
      2             spróbuj:
      3  >>             1/0
      4             w_końcu:
      5  ->             print('Exception!')
    [EOF]
    (Pdb) kontynuuj
    Correctly reraised.
    """


def test_pdb_skip_modules():
    """This illustrates the simple case of module skipping.

    >>> def skip_module():
    ...     zaimportuj string
    ...     zaimportuj pdb; pdb.Pdb(skip=['stri*'], nosigint=Prawda).set_trace()
    ...     string.capwords('FOO')

    >>> przy PdbTestInput([
    ...     'step',
    ...     'continue',
    ... ]):
    ...     skip_module()
    > <doctest test.test_pdb.test_pdb_skip_modules[0]>(4)skip_module()
    -> string.capwords('FOO')
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_skip_modules[0]>(4)skip_module()->Nic
    -> string.capwords('FOO')
    (Pdb) kontynuuj
    """


# Module dla testing skipping of module that makes a callback
mod = types.ModuleType('module_to_skip')
exec('def foo_pony(callback): x = 1; callback(); zwróć Nic', mod.__dict__)


def test_pdb_skip_modules_with_callback():
    """This illustrates skipping of modules that call into other code.

    >>> def skip_module():
    ...     def callback():
    ...         zwróć Nic
    ...     zaimportuj pdb; pdb.Pdb(skip=['module_to_skip*'], nosigint=Prawda).set_trace()
    ...     mod.foo_pony(callback)

    >>> przy PdbTestInput([
    ...     'step',
    ...     'step',
    ...     'step',
    ...     'step',
    ...     'step',
    ...     'continue',
    ... ]):
    ...     skip_module()
    ...     dalej  # provides something to "step" to
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(5)skip_module()
    -> mod.foo_pony(callback)
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(2)callback()
    -> def callback():
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(3)callback()
    -> zwróć Nic
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(3)callback()->Nic
    -> zwróć Nic
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(5)skip_module()->Nic
    -> mod.foo_pony(callback)
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[1]>(10)<module>()
    -> dalej  # provides something to "step" to
    (Pdb) kontynuuj
    """


def test_pdb_continue_in_bottomframe():
    """Test that "continue" oraz "next" work properly w bottom frame (issue #5294).

    >>> def test_function():
    ...     zaimportuj pdb, sys; inst = pdb.Pdb(nosigint=Prawda)
    ...     inst.set_trace()
    ...     inst.botframe = sys._getframe()  # hackery to get the right botframe
    ...     print(1)
    ...     print(2)
    ...     print(3)
    ...     print(4)

    >>> przy PdbTestInput([  # doctest: +ELLIPSIS
    ...     'next',
    ...     'break 7',
    ...     'continue',
    ...     'next',
    ...     'continue',
    ...     'continue',
    ... ]):
    ...    test_function()
    > <doctest test.test_pdb.test_pdb_continue_in_bottomframe[0]>(4)test_function()
    -> inst.botframe = sys._getframe()  # hackery to get the right botframe
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_continue_in_bottomframe[0]>(5)test_function()
    -> print(1)
    (Pdb) przerwij 7
    Breakpoint ... at <doctest test.test_pdb.test_pdb_continue_in_bottomframe[0]>:7
    (Pdb) kontynuuj
    1
    2
    > <doctest test.test_pdb.test_pdb_continue_in_bottomframe[0]>(7)test_function()
    -> print(3)
    (Pdb) next
    3
    > <doctest test.test_pdb.test_pdb_continue_in_bottomframe[0]>(8)test_function()
    -> print(4)
    (Pdb) kontynuuj
    4
    """


def pdb_invoke(method, arg):
    """Run pdb.method(arg)."""
    zaimportuj pdb
    getattr(pdb.Pdb(nosigint=Prawda), method)(arg)


def test_pdb_run_with_incorrect_argument():
    """Testing run oraz runeval przy incorrect first argument.

    >>> pti = PdbTestInput(['continue',])
    >>> przy pti:
    ...     pdb_invoke('run', lambda x: x)
    Traceback (most recent call last):
    TypeError: exec() arg 1 must be a string, bytes albo code object

    >>> przy pti:
    ...     pdb_invoke('runeval', lambda x: x)
    Traceback (most recent call last):
    TypeError: eval() arg 1 must be a string, bytes albo code object
    """


def test_pdb_run_with_code_object():
    """Testing run oraz runeval przy code object jako a first argument.

    >>> przy PdbTestInput(['step','x', 'continue']):  # doctest: +ELLIPSIS
    ...     pdb_invoke('run', compile('x=1', '<string>', 'exec'))
    > <string>(1)<module>()...
    (Pdb) step
    --Return--
    > <string>(1)<module>()->Nic
    (Pdb) x
    1
    (Pdb) kontynuuj

    >>> przy PdbTestInput(['x', 'continue']):
    ...     x=0
    ...     pdb_invoke('runeval', compile('x+1', '<string>', 'eval'))
    > <string>(1)<module>()->Nic
    (Pdb) x
    1
    (Pdb) kontynuuj
    """

def test_next_until_return_at_return_event():
    """Test that pdb stops after a next/until/return issued at a zwróć debug event.

    >>> def test_function_2():
    ...     x = 1
    ...     x = 2

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     test_function_2()
    ...     test_function_2()
    ...     test_function_2()
    ...     end = 1

    >>> z bdb zaimportuj Breakpoint
    >>> Breakpoint.next = 1
    >>> przy PdbTestInput(['break test_function_2',
    ...                    'continue',
    ...                    'return',
    ...                    'next',
    ...                    'continue',
    ...                    'return',
    ...                    'until',
    ...                    'continue',
    ...                    'return',
    ...                    'return',
    ...                    'continue']):
    ...     test_function()
    > <doctest test.test_pdb.test_next_until_return_at_return_event[1]>(3)test_function()
    -> test_function_2()
    (Pdb) przerwij test_function_2
    Breakpoint 1 at <doctest test.test_pdb.test_next_until_return_at_return_event[0]>:1
    (Pdb) kontynuuj
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(2)test_function_2()
    -> x = 1
    (Pdb) zwróć
    --Return--
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(3)test_function_2()->Nic
    -> x = 2
    (Pdb) next
    > <doctest test.test_pdb.test_next_until_return_at_return_event[1]>(4)test_function()
    -> test_function_2()
    (Pdb) kontynuuj
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(2)test_function_2()
    -> x = 1
    (Pdb) zwróć
    --Return--
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(3)test_function_2()->Nic
    -> x = 2
    (Pdb) until
    > <doctest test.test_pdb.test_next_until_return_at_return_event[1]>(5)test_function()
    -> test_function_2()
    (Pdb) kontynuuj
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(2)test_function_2()
    -> x = 1
    (Pdb) zwróć
    --Return--
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(3)test_function_2()->Nic
    -> x = 2
    (Pdb) zwróć
    > <doctest test.test_pdb.test_next_until_return_at_return_event[1]>(6)test_function()
    -> end = 1
    (Pdb) kontynuuj
    """

def test_pdb_next_command_for_generator():
    """Testing skip unwindng stack on uzyskaj dla generators dla "next" command

    >>> def test_gen():
    ...     uzyskaj 0
    ...     zwróć 1
    ...     uzyskaj 2

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     it = test_gen()
    ...     spróbuj:
    ...         jeżeli next(it) != 0:
    ...             podnieś AssertionError
    ...         next(it)
    ...     wyjąwszy StopIteration jako ex:
    ...         jeżeli ex.value != 1:
    ...             podnieś AssertionError
    ...     print("finished")

    >>> przy PdbTestInput(['step',
    ...                    'step',
    ...                    'step',
    ...                    'next',
    ...                    'next',
    ...                    'step',
    ...                    'step',
    ...                    'continue']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[1]>(3)test_function()
    -> it = test_gen()
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[1]>(4)test_function()
    -> spróbuj:
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[1]>(5)test_function()
    -> jeżeli next(it) != 0:
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[0]>(1)test_gen()
    -> def test_gen():
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[0]>(2)test_gen()
    -> uzyskaj 0
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[0]>(3)test_gen()
    -> zwróć 1
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[0]>(3)test_gen()->1
    -> zwróć 1
    (Pdb) step
    StopIteration: 1
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[1]>(7)test_function()
    -> next(it)
    (Pdb) kontynuuj
    finished
    """

def test_pdb_return_command_for_generator():
    """Testing no unwindng stack on uzyskaj dla generators
       dla "return" command

    >>> def test_gen():
    ...     uzyskaj 0
    ...     zwróć 1
    ...     uzyskaj 2

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     it = test_gen()
    ...     spróbuj:
    ...         jeżeli next(it) != 0:
    ...             podnieś AssertionError
    ...         next(it)
    ...     wyjąwszy StopIteration jako ex:
    ...         jeżeli ex.value != 1:
    ...             podnieś AssertionError
    ...     print("finished")

    >>> przy PdbTestInput(['step',
    ...                    'step',
    ...                    'step',
    ...                    'return',
    ...                    'step',
    ...                    'step',
    ...                    'continue']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(3)test_function()
    -> it = test_gen()
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(4)test_function()
    -> spróbuj:
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(5)test_function()
    -> jeżeli next(it) != 0:
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[0]>(1)test_gen()
    -> def test_gen():
    (Pdb) zwróć
    StopIteration: 1
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(7)test_function()
    -> next(it)
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(8)test_function()
    -> wyjąwszy StopIteration jako ex:
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(9)test_function()
    -> jeżeli ex.value != 1:
    (Pdb) kontynuuj
    finished
    """

def test_pdb_until_command_for_generator():
    """Testing no unwindng stack on uzyskaj dla generators
       dla "until" command jeżeli target przerwijpoing jest nie reached

    >>> def test_gen():
    ...     uzyskaj 0
    ...     uzyskaj 1
    ...     uzyskaj 2

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     dla i w test_gen():
    ...         print(i)
    ...     print("finished")

    >>> przy PdbTestInput(['step',
    ...                    'until 4',
    ...                    'step',
    ...                    'step',
    ...                    'continue']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[1]>(3)test_function()
    -> dla i w test_gen():
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[0]>(1)test_gen()
    -> def test_gen():
    (Pdb) until 4
    0
    1
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[0]>(4)test_gen()
    -> uzyskaj 2
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[0]>(4)test_gen()->2
    -> uzyskaj 2
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[1]>(4)test_function()
    -> print(i)
    (Pdb) kontynuuj
    2
    finished
    """

def test_pdb_next_command_in_generator_for_loop():
    """The next command on returning z a generator controled by a dla loop.

    >>> def test_gen():
    ...     uzyskaj 0
    ...     zwróć 1

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     dla i w test_gen():
    ...         print('value', i)
    ...     x = 123

    >>> przy PdbTestInput(['break test_gen',
    ...                    'continue',
    ...                    'next',
    ...                    'next',
    ...                    'next',
    ...                    'continue']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[1]>(3)test_function()
    -> dla i w test_gen():
    (Pdb) przerwij test_gen
    Breakpoint 6 at <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[0]>:1
    (Pdb) kontynuuj
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[0]>(2)test_gen()
    -> uzyskaj 0
    (Pdb) next
    value 0
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[0]>(3)test_gen()
    -> zwróć 1
    (Pdb) next
    Internal StopIteration: 1
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[1]>(3)test_function()
    -> dla i w test_gen():
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[1]>(5)test_function()
    -> x = 123
    (Pdb) kontynuuj
    """

def test_pdb_next_command_subiterator():
    """The next command w a generator przy a subiterator.

    >>> def test_subgenerator():
    ...     uzyskaj 0
    ...     zwróć 1

    >>> def test_gen():
    ...     x = uzyskaj z test_subgenerator()
    ...     zwróć x

    >>> def test_function():
    ...     zaimportuj pdb; pdb.Pdb(nosigint=Prawda).set_trace()
    ...     dla i w test_gen():
    ...         print('value', i)
    ...     x = 123

    >>> przy PdbTestInput(['step',
    ...                    'step',
    ...                    'next',
    ...                    'next',
    ...                    'next',
    ...                    'continue']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[2]>(3)test_function()
    -> dla i w test_gen():
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[1]>(1)test_gen()
    -> def test_gen():
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[1]>(2)test_gen()
    -> x = uzyskaj z test_subgenerator()
    (Pdb) next
    value 0
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[1]>(3)test_gen()
    -> zwróć x
    (Pdb) next
    Internal StopIteration: 1
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[2]>(3)test_function()
    -> dla i w test_gen():
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[2]>(5)test_function()
    -> x = 123
    (Pdb) kontynuuj
    """


klasa PdbTestCase(unittest.TestCase):

    def run_pdb(self, script, commands):
        """Run 'script' lines przy pdb oraz the pdb 'commands'."""
        filename = 'main.py'
        przy open(filename, 'w') jako f:
            f.write(textwrap.dedent(script))
        self.addCleanup(support.unlink, filename)
        self.addCleanup(support.rmtree, '__pycache__')
        cmd = [sys.executable, '-m', 'pdb', filename]
        stdout = stderr = Nic
        przy subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   ) jako proc:
            stdout, stderr = proc.communicate(str.encode(commands))
        stdout = stdout oraz bytes.decode(stdout)
        stderr = stderr oraz bytes.decode(stderr)
        zwróć stdout, stderr

    def _assert_find_function(self, file_content, func_name, expected):
        file_content = textwrap.dedent(file_content)

        przy open(support.TESTFN, 'w') jako f:
            f.write(file_content)

        expected = Nic jeżeli nie expected inaczej (
            expected[0], support.TESTFN, expected[1])
        self.assertEqual(
            expected, pdb.find_function(func_name, support.TESTFN))

    def test_find_function_empty_file(self):
        self._assert_find_function('', 'foo', Nic)

    def test_find_function_found(self):
        self._assert_find_function(
            """\
            def foo():
                dalej

            def bar():
                dalej

            def quux():
                dalej
            """,
            'bar',
            ('bar', 4),
        )

    def test_issue7964(self):
        # open the file jako binary so we can force \r\n newline
        przy open(support.TESTFN, 'wb') jako f:
            f.write(b'print("testing my pdb")\r\n')
        cmd = [sys.executable, '-m', 'pdb', support.TESTFN]
        proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            )
        self.addCleanup(proc.stdout.close)
        stdout, stderr = proc.communicate(b'quit\n')
        self.assertNotIn(b'SyntaxError', stdout,
                         "Got a syntax error running test script under PDB")

    def test_issue13183(self):
        script = """
            z bar zaimportuj bar

            def foo():
                bar()

            def nope():
                dalej

            def foobar():
                foo()
                nope()

            foobar()
        """
        commands = """
            z bar zaimportuj bar
            przerwij bar
            kontynuuj
            step
            step
            quit
        """
        bar = """
            def bar():
                dalej
        """
        przy open('bar.py', 'w') jako f:
            f.write(textwrap.dedent(bar))
        self.addCleanup(support.unlink, 'bar.py')
        stdout, stderr = self.run_pdb(script, commands)
        self.assertPrawda(
            any('main.py(5)foo()->Nic' w l dla l w stdout.splitlines()),
            'Fail to step into the caller after a return')

    def test_issue13210(self):
        # invoking "continue" on a non-main thread triggered an exception
        # inside signal.signal

        # podnieśs SkipTest jeżeli python was built without threads
        support.import_module('threading')

        przy open(support.TESTFN, 'wb') jako f:
            f.write(textwrap.dedent("""
                zaimportuj threading
                zaimportuj pdb

                def start_pdb():
                    pdb.Pdb().set_trace()
                    x = 1
                    y = 1

                t = threading.Thread(target=start_pdb)
                t.start()""").encode('ascii'))
        cmd = [sys.executable, '-u', support.TESTFN]
        proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            )
        self.addCleanup(proc.stdout.close)
        stdout, stderr = proc.communicate(b'cont\n')
        self.assertNotIn('Error', stdout.decode(),
                         "Got an error running test script under PDB")

    def tearDown(self):
        support.unlink(support.TESTFN)


def load_tests(*args):
    z test zaimportuj test_pdb
    suites = [unittest.makeSuite(PdbTestCase), doctest.DocTestSuite(test_pdb)]
    zwróć unittest.TestSuite(suites)


jeżeli __name__ == '__main__':
    unittest.main()
