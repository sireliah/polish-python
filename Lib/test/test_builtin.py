# Python test set -- built-in functions

zaimportuj ast
zaimportuj builtins
zaimportuj collections
zaimportuj io
zaimportuj locale
zaimportuj os
zaimportuj pickle
zaimportuj platform
zaimportuj random
zaimportuj sys
zaimportuj traceback
zaimportuj types
zaimportuj unittest
zaimportuj warnings
z operator zaimportuj neg
z test.support zaimportuj TESTFN, unlink,  run_unittest, check_warnings
z test.support.script_helper zaimportuj assert_python_ok
spróbuj:
    zaimportuj pty, signal
wyjąwszy ImportError:
    pty = signal = Nic


klasa Squares:

    def __init__(self, max):
        self.max = max
        self.sofar = []

    def __len__(self): zwróć len(self.sofar)

    def __getitem__(self, i):
        jeżeli nie 0 <= i < self.max: podnieś IndexError
        n = len(self.sofar)
        dopóki n <= i:
            self.sofar.append(n*n)
            n += 1
        zwróć self.sofar[i]

klasa StrSquares:

    def __init__(self, max):
        self.max = max
        self.sofar = []

    def __len__(self):
        zwróć len(self.sofar)

    def __getitem__(self, i):
        jeżeli nie 0 <= i < self.max:
            podnieś IndexError
        n = len(self.sofar)
        dopóki n <= i:
            self.sofar.append(str(n*n))
            n += 1
        zwróć self.sofar[i]

klasa BitBucket:
    def write(self, line):
        dalej

test_conv_no_sign = [
        ('0', 0),
        ('1', 1),
        ('9', 9),
        ('10', 10),
        ('99', 99),
        ('100', 100),
        ('314', 314),
        (' 314', 314),
        ('314 ', 314),
        ('  \t\t  314  \t\t  ', 314),
        (repr(sys.maxsize), sys.maxsize),
        ('  1x', ValueError),
        ('  1  ', 1),
        ('  1\02  ', ValueError),
        ('', ValueError),
        (' ', ValueError),
        ('  \t\t  ', ValueError),
        (str(b'\u0663\u0661\u0664 ','raw-unicode-escape'), 314),
        (chr(0x200), ValueError),
]

test_conv_sign = [
        ('0', 0),
        ('1', 1),
        ('9', 9),
        ('10', 10),
        ('99', 99),
        ('100', 100),
        ('314', 314),
        (' 314', ValueError),
        ('314 ', 314),
        ('  \t\t  314  \t\t  ', ValueError),
        (repr(sys.maxsize), sys.maxsize),
        ('  1x', ValueError),
        ('  1  ', ValueError),
        ('  1\02  ', ValueError),
        ('', ValueError),
        (' ', ValueError),
        ('  \t\t  ', ValueError),
        (str(b'\u0663\u0661\u0664 ','raw-unicode-escape'), 314),
        (chr(0x200), ValueError),
]

klasa TestFailingBool:
    def __bool__(self):
        podnieś RuntimeError

klasa TestFailingIter:
    def __iter__(self):
        podnieś RuntimeError

def filter_char(arg):
    zwróć ord(arg) > ord("d")

def map_char(arg):
    zwróć chr(ord(arg)+1)

klasa BuiltinTest(unittest.TestCase):
    # Helper to check picklability
    def check_iter_pickle(self, it, seq, proto):
        itorg = it
        d = pickle.dumps(it, proto)
        it = pickle.loads(d)
        self.assertEqual(type(itorg), type(it))
        self.assertEqual(list(it), seq)

        #test the iterator after dropping one z it
        it = pickle.loads(d)
        spróbuj:
            next(it)
        wyjąwszy StopIteration:
            zwróć
        d = pickle.dumps(it, proto)
        it = pickle.loads(d)
        self.assertEqual(list(it), seq[1:])

    def test_import(self):
        __import__('sys')
        __import__('time')
        __import__('string')
        __import__(name='sys')
        __import__(name='time', level=0)
        self.assertRaises(ImportError, __import__, 'spamspam')
        self.assertRaises(TypeError, __import__, 1, 2, 3, 4)
        self.assertRaises(ValueError, __import__, '')
        self.assertRaises(TypeError, __import__, 'sys', name='sys')

    def test_abs(self):
        # int
        self.assertEqual(abs(0), 0)
        self.assertEqual(abs(1234), 1234)
        self.assertEqual(abs(-1234), 1234)
        self.assertPrawda(abs(-sys.maxsize-1) > 0)
        # float
        self.assertEqual(abs(0.0), 0.0)
        self.assertEqual(abs(3.14), 3.14)
        self.assertEqual(abs(-3.14), 3.14)
        # str
        self.assertRaises(TypeError, abs, 'a')
        # bool
        self.assertEqual(abs(Prawda), 1)
        self.assertEqual(abs(Nieprawda), 0)
        # other
        self.assertRaises(TypeError, abs)
        self.assertRaises(TypeError, abs, Nic)
        klasa AbsClass(object):
            def __abs__(self):
                zwróć -5
        self.assertEqual(abs(AbsClass()), -5)

    def test_all(self):
        self.assertEqual(all([2, 4, 6]), Prawda)
        self.assertEqual(all([2, Nic, 6]), Nieprawda)
        self.assertRaises(RuntimeError, all, [2, TestFailingBool(), 6])
        self.assertRaises(RuntimeError, all, TestFailingIter())
        self.assertRaises(TypeError, all, 10)               # Non-iterable
        self.assertRaises(TypeError, all)                   # No args
        self.assertRaises(TypeError, all, [2, 4, 6], [])    # Too many args
        self.assertEqual(all([]), Prawda)                     # Empty iterator
        self.assertEqual(all([0, TestFailingBool()]), Nieprawda)# Short-circuit
        S = [50, 60]
        self.assertEqual(all(x > 42 dla x w S), Prawda)
        S = [50, 40, 60]
        self.assertEqual(all(x > 42 dla x w S), Nieprawda)

    def test_any(self):
        self.assertEqual(any([Nic, Nic, Nic]), Nieprawda)
        self.assertEqual(any([Nic, 4, Nic]), Prawda)
        self.assertRaises(RuntimeError, any, [Nic, TestFailingBool(), 6])
        self.assertRaises(RuntimeError, any, TestFailingIter())
        self.assertRaises(TypeError, any, 10)               # Non-iterable
        self.assertRaises(TypeError, any)                   # No args
        self.assertRaises(TypeError, any, [2, 4, 6], [])    # Too many args
        self.assertEqual(any([]), Nieprawda)                    # Empty iterator
        self.assertEqual(any([1, TestFailingBool()]), Prawda) # Short-circuit
        S = [40, 60, 30]
        self.assertEqual(any(x > 42 dla x w S), Prawda)
        S = [10, 20, 30]
        self.assertEqual(any(x > 42 dla x w S), Nieprawda)

    def test_ascii(self):
        self.assertEqual(ascii(''), '\'\'')
        self.assertEqual(ascii(0), '0')
        self.assertEqual(ascii(()), '()')
        self.assertEqual(ascii([]), '[]')
        self.assertEqual(ascii({}), '{}')
        a = []
        a.append(a)
        self.assertEqual(ascii(a), '[[...]]')
        a = {}
        a[0] = a
        self.assertEqual(ascii(a), '{0: {...}}')
        # Advanced checks dla unicode strings
        def _check_uni(s):
            self.assertEqual(ascii(s), repr(s))
        _check_uni("'")
        _check_uni('"')
        _check_uni('"\'')
        _check_uni('\0')
        _check_uni('\r\n\t .')
        # Unprintable non-ASCII characters
        _check_uni('\x85')
        _check_uni('\u1fff')
        _check_uni('\U00012fff')
        # Lone surrogates
        _check_uni('\ud800')
        _check_uni('\udfff')
        # Issue #9804: surrogates should be joined even dla printable
        # wide characters (UCS-2 builds).
        self.assertEqual(ascii('\U0001d121'), "'\\U0001d121'")
        # All together
        s = "'\0\"\n\r\t abcd\x85é\U00012fff\uD800\U0001D121xxx."
        self.assertEqual(ascii(s),
            r"""'\'\x00"\n\r\t abcd\x85\xe9\U00012fff\ud800\U0001d121xxx.'""")

    def test_neg(self):
        x = -sys.maxsize-1
        self.assertPrawda(isinstance(x, int))
        self.assertEqual(-x, sys.maxsize+1)

    def test_callable(self):
        self.assertPrawda(callable(len))
        self.assertNieprawda(callable("a"))
        self.assertPrawda(callable(callable))
        self.assertPrawda(callable(lambda x, y: x + y))
        self.assertNieprawda(callable(__builtins__))
        def f(): dalej
        self.assertPrawda(callable(f))

        klasa C1:
            def meth(self): dalej
        self.assertPrawda(callable(C1))
        c = C1()
        self.assertPrawda(callable(c.meth))
        self.assertNieprawda(callable(c))

        # __call__ jest looked up on the class, nie the instance
        c.__call__ = Nic
        self.assertNieprawda(callable(c))
        c.__call__ = lambda self: 0
        self.assertNieprawda(callable(c))
        usuń c.__call__
        self.assertNieprawda(callable(c))

        klasa C2(object):
            def __call__(self): dalej
        c2 = C2()
        self.assertPrawda(callable(c2))
        c2.__call__ = Nic
        self.assertPrawda(callable(c2))
        klasa C3(C2): dalej
        c3 = C3()
        self.assertPrawda(callable(c3))

    def test_chr(self):
        self.assertEqual(chr(32), ' ')
        self.assertEqual(chr(65), 'A')
        self.assertEqual(chr(97), 'a')
        self.assertEqual(chr(0xff), '\xff')
        self.assertRaises(ValueError, chr, 1<<24)
        self.assertEqual(chr(sys.maxunicode),
                         str('\\U0010ffff'.encode("ascii"), 'unicode-escape'))
        self.assertRaises(TypeError, chr)
        self.assertEqual(chr(0x0000FFFF), "\U0000FFFF")
        self.assertEqual(chr(0x00010000), "\U00010000")
        self.assertEqual(chr(0x00010001), "\U00010001")
        self.assertEqual(chr(0x000FFFFE), "\U000FFFFE")
        self.assertEqual(chr(0x000FFFFF), "\U000FFFFF")
        self.assertEqual(chr(0x00100000), "\U00100000")
        self.assertEqual(chr(0x00100001), "\U00100001")
        self.assertEqual(chr(0x0010FFFE), "\U0010FFFE")
        self.assertEqual(chr(0x0010FFFF), "\U0010FFFF")
        self.assertRaises(ValueError, chr, -1)
        self.assertRaises(ValueError, chr, 0x00110000)
        self.assertRaises((OverflowError, ValueError), chr, 2**32)

    def test_cmp(self):
        self.assertPrawda(nie hasattr(builtins, "cmp"))

    def test_compile(self):
        compile('print(1)\n', '', 'exec')
        bom = b'\xef\xbb\xbf'
        compile(bom + b'print(1)\n', '', 'exec')
        compile(source='pass', filename='?', mode='exec')
        compile(dont_inherit=0, filename='tmp', source='0', mode='eval')
        compile('pass', '?', dont_inherit=1, mode='exec')
        compile(memoryview(b"text"), "name", "exec")
        self.assertRaises(TypeError, compile)
        self.assertRaises(ValueError, compile, 'print(42)\n', '<string>', 'badmode')
        self.assertRaises(ValueError, compile, 'print(42)\n', '<string>', 'single', 0xff)
        self.assertRaises(ValueError, compile, chr(0), 'f', 'exec')
        self.assertRaises(TypeError, compile, 'pass', '?', 'exec',
                          mode='eval', source='0', filename='tmp')
        compile('print("\xe5")\n', '', 'exec')
        self.assertRaises(ValueError, compile, chr(0), 'f', 'exec')
        self.assertRaises(ValueError, compile, str('a = 1'), 'f', 'bad')

        # test the optimize argument

        codestr = '''def f():
        """doc"""
        spróbuj:
            assert Nieprawda
        wyjąwszy AssertionError:
            zwróć (Prawda, f.__doc__)
        inaczej:
            zwróć (Nieprawda, f.__doc__)
        '''
        def f(): """doc"""
        values = [(-1, __debug__, f.__doc__),
                  (0, Prawda, 'doc'),
                  (1, Nieprawda, 'doc'),
                  (2, Nieprawda, Nic)]
        dla optval, debugval, docstring w values:
            # test both direct compilation oraz compilation via AST
            codeobjs = []
            codeobjs.append(compile(codestr, "<test>", "exec", optimize=optval))
            tree = ast.parse(codestr)
            codeobjs.append(compile(tree, "<test>", "exec", optimize=optval))
            dla code w codeobjs:
                ns = {}
                exec(code, ns)
                rv = ns['f']()
                self.assertEqual(rv, (debugval, docstring))

    def test_delattr(self):
        sys.spam = 1
        delattr(sys, 'spam')
        self.assertRaises(TypeError, delattr)

    def test_dir(self):
        # dir(wrong number of arguments)
        self.assertRaises(TypeError, dir, 42, 42)

        # dir() - local scope
        local_var = 1
        self.assertIn('local_var', dir())

        # dir(module)
        self.assertIn('exit', dir(sys))

        # dir(module_with_invalid__dict__)
        klasa Foo(types.ModuleType):
            __dict__ = 8
        f = Foo("foo")
        self.assertRaises(TypeError, dir, f)

        # dir(type)
        self.assertIn("strip", dir(str))
        self.assertNotIn("__mro__", dir(str))

        # dir(obj)
        klasa Foo(object):
            def __init__(self):
                self.x = 7
                self.y = 8
                self.z = 9
        f = Foo()
        self.assertIn("y", dir(f))

        # dir(obj_no__dict__)
        klasa Foo(object):
            __slots__ = []
        f = Foo()
        self.assertIn("__repr__", dir(f))

        # dir(obj_no__class__with__dict__)
        # (an ugly trick to cause getattr(f, "__class__") to fail)
        klasa Foo(object):
            __slots__ = ["__class__", "__dict__"]
            def __init__(self):
                self.bar = "wow"
        f = Foo()
        self.assertNotIn("__repr__", dir(f))
        self.assertIn("bar", dir(f))

        # dir(obj_using __dir__)
        klasa Foo(object):
            def __dir__(self):
                zwróć ["kan", "ga", "roo"]
        f = Foo()
        self.assertPrawda(dir(f) == ["ga", "kan", "roo"])

        # dir(obj__dir__tuple)
        klasa Foo(object):
            def __dir__(self):
                zwróć ("b", "c", "a")
        res = dir(Foo())
        self.assertIsInstance(res, list)
        self.assertPrawda(res == ["a", "b", "c"])

        # dir(obj__dir__not_sequence)
        klasa Foo(object):
            def __dir__(self):
                zwróć 7
        f = Foo()
        self.assertRaises(TypeError, dir, f)

        # dir(traceback)
        spróbuj:
            podnieś IndexError
        wyjąwszy:
            self.assertEqual(len(dir(sys.exc_info()[2])), 4)

        # test that object has a __dir__()
        self.assertEqual(sorted([].__dir__()), dir([]))

    def test_divmod(self):
        self.assertEqual(divmod(12, 7), (1, 5))
        self.assertEqual(divmod(-12, 7), (-2, 2))
        self.assertEqual(divmod(12, -7), (-2, -2))
        self.assertEqual(divmod(-12, -7), (1, -5))

        self.assertEqual(divmod(-sys.maxsize-1, -1), (sys.maxsize+1, 0))

        dla num, denom, exp_result w [ (3.25, 1.0, (3.0, 0.25)),
                                        (-3.25, 1.0, (-4.0, 0.75)),
                                        (3.25, -1.0, (-4.0, -0.75)),
                                        (-3.25, -1.0, (3.0, -0.25))]:
            result = divmod(num, denom)
            self.assertAlmostEqual(result[0], exp_result[0])
            self.assertAlmostEqual(result[1], exp_result[1])

        self.assertRaises(TypeError, divmod)

    def test_eval(self):
        self.assertEqual(eval('1+1'), 2)
        self.assertEqual(eval(' 1+1\n'), 2)
        globals = {'a': 1, 'b': 2}
        locals = {'b': 200, 'c': 300}
        self.assertEqual(eval('a', globals) , 1)
        self.assertEqual(eval('a', globals, locals), 1)
        self.assertEqual(eval('b', globals, locals), 200)
        self.assertEqual(eval('c', globals, locals), 300)
        globals = {'a': 1, 'b': 2}
        locals = {'b': 200, 'c': 300}
        bom = b'\xef\xbb\xbf'
        self.assertEqual(eval(bom + b'a', globals, locals), 1)
        self.assertEqual(eval('"\xe5"', globals), "\xe5")
        self.assertRaises(TypeError, eval)
        self.assertRaises(TypeError, eval, ())
        self.assertRaises(SyntaxError, eval, bom[:2] + b'a')

        klasa X:
            def __getitem__(self, key):
                podnieś ValueError
        self.assertRaises(ValueError, eval, "foo", {}, X())

    def test_general_eval(self):
        # Tests that general mappings can be used dla the locals argument

        klasa M:
            "Test mapping interface versus possible calls z eval()."
            def __getitem__(self, key):
                jeżeli key == 'a':
                    zwróć 12
                podnieś KeyError
            def keys(self):
                zwróć list('xyz')

        m = M()
        g = globals()
        self.assertEqual(eval('a', g, m), 12)
        self.assertRaises(NameError, eval, 'b', g, m)
        self.assertEqual(eval('dir()', g, m), list('xyz'))
        self.assertEqual(eval('globals()', g, m), g)
        self.assertEqual(eval('locals()', g, m), m)
        self.assertRaises(TypeError, eval, 'a', m)
        klasa A:
            "Non-mapping"
            dalej
        m = A()
        self.assertRaises(TypeError, eval, 'a', g, m)

        # Verify that dict subclasses work jako well
        klasa D(dict):
            def __getitem__(self, key):
                jeżeli key == 'a':
                    zwróć 12
                zwróć dict.__getitem__(self, key)
            def keys(self):
                zwróć list('xyz')

        d = D()
        self.assertEqual(eval('a', g, d), 12)
        self.assertRaises(NameError, eval, 'b', g, d)
        self.assertEqual(eval('dir()', g, d), list('xyz'))
        self.assertEqual(eval('globals()', g, d), g)
        self.assertEqual(eval('locals()', g, d), d)

        # Verify locals stores (used by list comps)
        eval('[locals() dla i w (2,3)]', g, d)
        eval('[locals() dla i w (2,3)]', g, collections.UserDict())

        klasa SpreadSheet:
            "Sample application showing nested, calculated lookups."
            _cells = {}
            def __setitem__(self, key, formula):
                self._cells[key] = formula
            def __getitem__(self, key):
                zwróć eval(self._cells[key], globals(), self)

        ss = SpreadSheet()
        ss['a1'] = '5'
        ss['a2'] = 'a1*6'
        ss['a3'] = 'a2*7'
        self.assertEqual(ss['a3'], 210)

        # Verify that dir() catches a non-list returned by eval
        # SF bug #1004669
        klasa C:
            def __getitem__(self, item):
                podnieś KeyError(item)
            def keys(self):
                zwróć 1 # used to be 'a' but that's no longer an error
        self.assertRaises(TypeError, eval, 'dir()', globals(), C())

    def test_exec(self):
        g = {}
        exec('z = 1', g)
        jeżeli '__builtins__' w g:
            usuń g['__builtins__']
        self.assertEqual(g, {'z': 1})

        exec('z = 1+1', g)
        jeżeli '__builtins__' w g:
            usuń g['__builtins__']
        self.assertEqual(g, {'z': 2})
        g = {}
        l = {}

        przy check_warnings():
            warnings.filterwarnings("ignore", "global statement",
                    module="<string>")
            exec('global a; a = 1; b = 2', g, l)
        jeżeli '__builtins__' w g:
            usuń g['__builtins__']
        jeżeli '__builtins__' w l:
            usuń l['__builtins__']
        self.assertEqual((g, l), ({'a': 1}, {'b': 2}))

    def test_exec_globals(self):
        code = compile("print('Hello World!')", "", "exec")
        # no builtin function
        self.assertRaisesRegex(NameError, "name 'print' jest nie defined",
                               exec, code, {'__builtins__': {}})
        # __builtins__ must be a mapping type
        self.assertRaises(TypeError,
                          exec, code, {'__builtins__': 123})

        # no __build_class__ function
        code = compile("class A: dalej", "", "exec")
        self.assertRaisesRegex(NameError, "__build_class__ nie found",
                               exec, code, {'__builtins__': {}})

        klasa frozendict_error(Exception):
            dalej

        klasa frozendict(dict):
            def __setitem__(self, key, value):
                podnieś frozendict_error("frozendict jest readonly")

        # read-only builtins
        jeżeli isinstance(__builtins__, types.ModuleType):
            frozen_builtins = frozendict(__builtins__.__dict__)
        inaczej:
            frozen_builtins = frozendict(__builtins__)
        code = compile("__builtins__['superglobal']=2; print(superglobal)", "test", "exec")
        self.assertRaises(frozendict_error,
                          exec, code, {'__builtins__': frozen_builtins})

        # read-only globals
        namespace = frozendict({})
        code = compile("x=1", "test", "exec")
        self.assertRaises(frozendict_error,
                          exec, code, namespace)

    def test_exec_redirected(self):
        savestdout = sys.stdout
        sys.stdout = Nic # Whatever that cannot flush()
        spróbuj:
            # Used to podnieś SystemError('error zwróć without exception set')
            exec('a')
        wyjąwszy NameError:
            dalej
        w_końcu:
            sys.stdout = savestdout

    def test_filter(self):
        self.assertEqual(list(filter(lambda c: 'a' <= c <= 'z', 'Hello World')), list('elloorld'))
        self.assertEqual(list(filter(Nic, [1, 'hello', [], [3], '', Nic, 9, 0])), [1, 'hello', [3], 9])
        self.assertEqual(list(filter(lambda x: x > 0, [1, -3, 9, 0, 2])), [1, 9, 2])
        self.assertEqual(list(filter(Nic, Squares(10))), [1, 4, 9, 16, 25, 36, 49, 64, 81])
        self.assertEqual(list(filter(lambda x: x%2, Squares(10))), [1, 9, 25, 49, 81])
        def identity(item):
            zwróć 1
        filter(identity, Squares(5))
        self.assertRaises(TypeError, filter)
        klasa BadSeq(object):
            def __getitem__(self, index):
                jeżeli index<4:
                    zwróć 42
                podnieś ValueError
        self.assertRaises(ValueError, list, filter(lambda x: x, BadSeq()))
        def badfunc():
            dalej
        self.assertRaises(TypeError, list, filter(badfunc, range(5)))

        # test bltinmodule.c::filtertuple()
        self.assertEqual(list(filter(Nic, (1, 2))), [1, 2])
        self.assertEqual(list(filter(lambda x: x>=3, (1, 2, 3, 4))), [3, 4])
        self.assertRaises(TypeError, list, filter(42, (1, 2)))

    def test_filter_pickle(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            f1 = filter(filter_char, "abcdeabcde")
            f2 = filter(filter_char, "abcdeabcde")
            self.check_iter_pickle(f1, list(f2), proto)

    def test_getattr(self):
        self.assertPrawda(getattr(sys, 'stdout') jest sys.stdout)
        self.assertRaises(TypeError, getattr, sys, 1)
        self.assertRaises(TypeError, getattr, sys, 1, "foo")
        self.assertRaises(TypeError, getattr)
        self.assertRaises(AttributeError, getattr, sys, chr(sys.maxunicode))
        # unicode surrogates are nie encodable to the default encoding (utf8)
        self.assertRaises(AttributeError, getattr, 1, "\uDAD1\uD51E")

    def test_hasattr(self):
        self.assertPrawda(hasattr(sys, 'stdout'))
        self.assertRaises(TypeError, hasattr, sys, 1)
        self.assertRaises(TypeError, hasattr)
        self.assertEqual(Nieprawda, hasattr(sys, chr(sys.maxunicode)))

        # Check that hasattr propagates all exceptions outside of
        # AttributeError.
        klasa A:
            def __getattr__(self, what):
                podnieś SystemExit
        self.assertRaises(SystemExit, hasattr, A(), "b")
        klasa B:
            def __getattr__(self, what):
                podnieś ValueError
        self.assertRaises(ValueError, hasattr, B(), "b")

    def test_hash(self):
        hash(Nic)
        self.assertEqual(hash(1), hash(1))
        self.assertEqual(hash(1), hash(1.0))
        hash('spam')
        self.assertEqual(hash('spam'), hash(b'spam'))
        hash((0,1,2,3))
        def f(): dalej
        self.assertRaises(TypeError, hash, [])
        self.assertRaises(TypeError, hash, {})
        # Bug 1536021: Allow hash to zwróć long objects
        klasa X:
            def __hash__(self):
                zwróć 2**100
        self.assertEqual(type(hash(X())), int)
        klasa Z(int):
            def __hash__(self):
                zwróć self
        self.assertEqual(hash(Z(42)), hash(42))

    def test_hex(self):
        self.assertEqual(hex(16), '0x10')
        self.assertEqual(hex(-16), '-0x10')
        self.assertRaises(TypeError, hex, {})

    def test_id(self):
        id(Nic)
        id(1)
        id(1.0)
        id('spam')
        id((0,1,2,3))
        id([0,1,2,3])
        id({'spam': 1, 'eggs': 2, 'ham': 3})

    # Test input() later, alphabetized jako jeżeli it were raw_input

    def test_iter(self):
        self.assertRaises(TypeError, iter)
        self.assertRaises(TypeError, iter, 42, 42)
        lists = [("1", "2"), ["1", "2"], "12"]
        dla l w lists:
            i = iter(l)
            self.assertEqual(next(i), '1')
            self.assertEqual(next(i), '2')
            self.assertRaises(StopIteration, next, i)

    def test_isinstance(self):
        klasa C:
            dalej
        klasa D(C):
            dalej
        klasa E:
            dalej
        c = C()
        d = D()
        e = E()
        self.assertPrawda(isinstance(c, C))
        self.assertPrawda(isinstance(d, C))
        self.assertPrawda(nie isinstance(e, C))
        self.assertPrawda(nie isinstance(c, D))
        self.assertPrawda(nie isinstance('foo', E))
        self.assertRaises(TypeError, isinstance, E, 'foo')
        self.assertRaises(TypeError, isinstance)

    def test_issubclass(self):
        klasa C:
            dalej
        klasa D(C):
            dalej
        klasa E:
            dalej
        c = C()
        d = D()
        e = E()
        self.assertPrawda(issubclass(D, C))
        self.assertPrawda(issubclass(C, C))
        self.assertPrawda(nie issubclass(C, D))
        self.assertRaises(TypeError, issubclass, 'foo', E)
        self.assertRaises(TypeError, issubclass, E, 'foo')
        self.assertRaises(TypeError, issubclass)

    def test_len(self):
        self.assertEqual(len('123'), 3)
        self.assertEqual(len(()), 0)
        self.assertEqual(len((1, 2, 3, 4)), 4)
        self.assertEqual(len([1, 2, 3, 4]), 4)
        self.assertEqual(len({}), 0)
        self.assertEqual(len({'a':1, 'b': 2}), 2)
        klasa BadSeq:
            def __len__(self):
                podnieś ValueError
        self.assertRaises(ValueError, len, BadSeq())
        klasa InvalidLen:
            def __len__(self):
                zwróć Nic
        self.assertRaises(TypeError, len, InvalidLen())
        klasa FloatLen:
            def __len__(self):
                zwróć 4.5
        self.assertRaises(TypeError, len, FloatLen())
        klasa HugeLen:
            def __len__(self):
                zwróć sys.maxsize + 1
        self.assertRaises(OverflowError, len, HugeLen())
        klasa NoLenMethod(object): dalej
        self.assertRaises(TypeError, len, NoLenMethod())

    def test_map(self):
        self.assertEqual(
            list(map(lambda x: x*x, range(1,4))),
            [1, 4, 9]
        )
        spróbuj:
            z math zaimportuj sqrt
        wyjąwszy ImportError:
            def sqrt(x):
                zwróć pow(x, 0.5)
        self.assertEqual(
            list(map(lambda x: list(map(sqrt, x)), [[16, 4], [81, 9]])),
            [[4.0, 2.0], [9.0, 3.0]]
        )
        self.assertEqual(
            list(map(lambda x, y: x+y, [1,3,2], [9,1,4])),
            [10, 4, 6]
        )

        def plus(*v):
            accu = 0
            dla i w v: accu = accu + i
            zwróć accu
        self.assertEqual(
            list(map(plus, [1, 3, 7])),
            [1, 3, 7]
        )
        self.assertEqual(
            list(map(plus, [1, 3, 7], [4, 9, 2])),
            [1+4, 3+9, 7+2]
        )
        self.assertEqual(
            list(map(plus, [1, 3, 7], [4, 9, 2], [1, 1, 0])),
            [1+4+1, 3+9+1, 7+2+0]
        )
        self.assertEqual(
            list(map(int, Squares(10))),
            [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
        )
        def Max(a, b):
            jeżeli a jest Nic:
                zwróć b
            jeżeli b jest Nic:
                zwróć a
            zwróć max(a, b)
        self.assertEqual(
            list(map(Max, Squares(3), Squares(2))),
            [0, 1]
        )
        self.assertRaises(TypeError, map)
        self.assertRaises(TypeError, map, lambda x: x, 42)
        klasa BadSeq:
            def __iter__(self):
                podnieś ValueError
                uzyskaj Nic
        self.assertRaises(ValueError, list, map(lambda x: x, BadSeq()))
        def badfunc(x):
            podnieś RuntimeError
        self.assertRaises(RuntimeError, list, map(badfunc, range(5)))

    def test_map_pickle(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            m1 = map(map_char, "Is this the real life?")
            m2 = map(map_char, "Is this the real life?")
            self.check_iter_pickle(m1, list(m2), proto)

    def test_max(self):
        self.assertEqual(max('123123'), '3')
        self.assertEqual(max(1, 2, 3), 3)
        self.assertEqual(max((1, 2, 3, 1, 2, 3)), 3)
        self.assertEqual(max([1, 2, 3, 1, 2, 3]), 3)

        self.assertEqual(max(1, 2, 3.0), 3.0)
        self.assertEqual(max(1, 2.0, 3), 3)
        self.assertEqual(max(1.0, 2, 3), 3)

        self.assertRaises(TypeError, max)
        self.assertRaises(TypeError, max, 42)
        self.assertRaises(ValueError, max, ())
        klasa BadSeq:
            def __getitem__(self, index):
                podnieś ValueError
        self.assertRaises(ValueError, max, BadSeq())

        dla stmt w (
            "max(key=int)",                 # no args
            "max(default=Nic)",
            "max(1, 2, default=Nic)",      # require container dla default
            "max(default=Nic, key=int)",
            "max(1, key=int)",              # single arg nie iterable
            "max(1, 2, keystone=int)",      # wrong keyword
            "max(1, 2, key=int, abc=int)",  # two many keywords
            "max(1, 2, key=1)",             # keyfunc jest nie callable
            ):
            spróbuj:
                exec(stmt, globals())
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail(stmt)

        self.assertEqual(max((1,), key=neg), 1)     # one elem iterable
        self.assertEqual(max((1,2), key=neg), 1)    # two elem iterable
        self.assertEqual(max(1, 2, key=neg), 1)     # two elems

        self.assertEqual(max((), default=Nic), Nic)    # zero elem iterable
        self.assertEqual(max((1,), default=Nic), 1)     # one elem iterable
        self.assertEqual(max((1,2), default=Nic), 2)    # two elem iterable

        self.assertEqual(max((), default=1, key=neg), 1)
        self.assertEqual(max((1, 2), default=3, key=neg), 1)

        data = [random.randrange(200) dla i w range(100)]
        keys = dict((elem, random.randrange(50)) dla elem w data)
        f = keys.__getitem__
        self.assertEqual(max(data, key=f),
                         sorted(reversed(data), key=f)[-1])

    def test_min(self):
        self.assertEqual(min('123123'), '1')
        self.assertEqual(min(1, 2, 3), 1)
        self.assertEqual(min((1, 2, 3, 1, 2, 3)), 1)
        self.assertEqual(min([1, 2, 3, 1, 2, 3]), 1)

        self.assertEqual(min(1, 2, 3.0), 1)
        self.assertEqual(min(1, 2.0, 3), 1)
        self.assertEqual(min(1.0, 2, 3), 1.0)

        self.assertRaises(TypeError, min)
        self.assertRaises(TypeError, min, 42)
        self.assertRaises(ValueError, min, ())
        klasa BadSeq:
            def __getitem__(self, index):
                podnieś ValueError
        self.assertRaises(ValueError, min, BadSeq())

        dla stmt w (
            "min(key=int)",                 # no args
            "min(default=Nic)",
            "min(1, 2, default=Nic)",      # require container dla default
            "min(default=Nic, key=int)",
            "min(1, key=int)",              # single arg nie iterable
            "min(1, 2, keystone=int)",      # wrong keyword
            "min(1, 2, key=int, abc=int)",  # two many keywords
            "min(1, 2, key=1)",             # keyfunc jest nie callable
            ):
            spróbuj:
                exec(stmt, globals())
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail(stmt)

        self.assertEqual(min((1,), key=neg), 1)     # one elem iterable
        self.assertEqual(min((1,2), key=neg), 2)    # two elem iterable
        self.assertEqual(min(1, 2, key=neg), 2)     # two elems

        self.assertEqual(min((), default=Nic), Nic)    # zero elem iterable
        self.assertEqual(min((1,), default=Nic), 1)     # one elem iterable
        self.assertEqual(min((1,2), default=Nic), 1)    # two elem iterable

        self.assertEqual(min((), default=1, key=neg), 1)
        self.assertEqual(min((1, 2), default=1, key=neg), 2)

        data = [random.randrange(200) dla i w range(100)]
        keys = dict((elem, random.randrange(50)) dla elem w data)
        f = keys.__getitem__
        self.assertEqual(min(data, key=f),
                         sorted(data, key=f)[0])

    def test_next(self):
        it = iter(range(2))
        self.assertEqual(next(it), 0)
        self.assertEqual(next(it), 1)
        self.assertRaises(StopIteration, next, it)
        self.assertRaises(StopIteration, next, it)
        self.assertEqual(next(it, 42), 42)

        klasa Iter(object):
            def __iter__(self):
                zwróć self
            def __next__(self):
                podnieś StopIteration

        it = iter(Iter())
        self.assertEqual(next(it, 42), 42)
        self.assertRaises(StopIteration, next, it)

        def gen():
            uzyskaj 1
            zwróć

        it = gen()
        self.assertEqual(next(it), 1)
        self.assertRaises(StopIteration, next, it)
        self.assertEqual(next(it, 42), 42)

    def test_oct(self):
        self.assertEqual(oct(100), '0o144')
        self.assertEqual(oct(-100), '-0o144')
        self.assertRaises(TypeError, oct, ())

    def write_testfile(self):
        # NB the first 4 lines are also used to test input, below
        fp = open(TESTFN, 'w')
        self.addCleanup(unlink, TESTFN)
        przy fp:
            fp.write('1+1\n')
            fp.write('The quick brown fox jumps over the lazy dog')
            fp.write('.\n')
            fp.write('Dear John\n')
            fp.write('XXX'*100)
            fp.write('YYY'*100)

    def test_open(self):
        self.write_testfile()
        fp = open(TESTFN, 'r')
        przy fp:
            self.assertEqual(fp.readline(4), '1+1\n')
            self.assertEqual(fp.readline(), 'The quick brown fox jumps over the lazy dog.\n')
            self.assertEqual(fp.readline(4), 'Dear')
            self.assertEqual(fp.readline(100), ' John\n')
            self.assertEqual(fp.read(300), 'XXX'*100)
            self.assertEqual(fp.read(1000), 'YYY'*100)

    def test_open_default_encoding(self):
        old_environ = dict(os.environ)
        spróbuj:
            # try to get a user preferred encoding different than the current
            # locale encoding to check that open() uses the current locale
            # encoding oraz nie the user preferred encoding
            dla key w ('LC_ALL', 'LANG', 'LC_CTYPE'):
                jeżeli key w os.environ:
                    usuń os.environ[key]

            self.write_testfile()
            current_locale_encoding = locale.getpreferredencoding(Nieprawda)
            fp = open(TESTFN, 'w')
            przy fp:
                self.assertEqual(fp.encoding, current_locale_encoding)
        w_końcu:
            os.environ.clear()
            os.environ.update(old_environ)

    def test_open_non_inheritable(self):
        fileobj = open(__file__)
        przy fileobj:
            self.assertNieprawda(os.get_inheritable(fileobj.fileno()))

    def test_ord(self):
        self.assertEqual(ord(' '), 32)
        self.assertEqual(ord('A'), 65)
        self.assertEqual(ord('a'), 97)
        self.assertEqual(ord('\x80'), 128)
        self.assertEqual(ord('\xff'), 255)

        self.assertEqual(ord(b' '), 32)
        self.assertEqual(ord(b'A'), 65)
        self.assertEqual(ord(b'a'), 97)
        self.assertEqual(ord(b'\x80'), 128)
        self.assertEqual(ord(b'\xff'), 255)

        self.assertEqual(ord(chr(sys.maxunicode)), sys.maxunicode)
        self.assertRaises(TypeError, ord, 42)

        self.assertEqual(ord(chr(0x10FFFF)), 0x10FFFF)
        self.assertEqual(ord("\U0000FFFF"), 0x0000FFFF)
        self.assertEqual(ord("\U00010000"), 0x00010000)
        self.assertEqual(ord("\U00010001"), 0x00010001)
        self.assertEqual(ord("\U000FFFFE"), 0x000FFFFE)
        self.assertEqual(ord("\U000FFFFF"), 0x000FFFFF)
        self.assertEqual(ord("\U00100000"), 0x00100000)
        self.assertEqual(ord("\U00100001"), 0x00100001)
        self.assertEqual(ord("\U0010FFFE"), 0x0010FFFE)
        self.assertEqual(ord("\U0010FFFF"), 0x0010FFFF)

    def test_pow(self):
        self.assertEqual(pow(0,0), 1)
        self.assertEqual(pow(0,1), 0)
        self.assertEqual(pow(1,0), 1)
        self.assertEqual(pow(1,1), 1)

        self.assertEqual(pow(2,0), 1)
        self.assertEqual(pow(2,10), 1024)
        self.assertEqual(pow(2,20), 1024*1024)
        self.assertEqual(pow(2,30), 1024*1024*1024)

        self.assertEqual(pow(-2,0), 1)
        self.assertEqual(pow(-2,1), -2)
        self.assertEqual(pow(-2,2), 4)
        self.assertEqual(pow(-2,3), -8)

        self.assertAlmostEqual(pow(0.,0), 1.)
        self.assertAlmostEqual(pow(0.,1), 0.)
        self.assertAlmostEqual(pow(1.,0), 1.)
        self.assertAlmostEqual(pow(1.,1), 1.)

        self.assertAlmostEqual(pow(2.,0), 1.)
        self.assertAlmostEqual(pow(2.,10), 1024.)
        self.assertAlmostEqual(pow(2.,20), 1024.*1024.)
        self.assertAlmostEqual(pow(2.,30), 1024.*1024.*1024.)

        self.assertAlmostEqual(pow(-2.,0), 1.)
        self.assertAlmostEqual(pow(-2.,1), -2.)
        self.assertAlmostEqual(pow(-2.,2), 4.)
        self.assertAlmostEqual(pow(-2.,3), -8.)

        dla x w 2, 2.0:
            dla y w 10, 10.0:
                dla z w 1000, 1000.0:
                    jeżeli isinstance(x, float) albo \
                       isinstance(y, float) albo \
                       isinstance(z, float):
                        self.assertRaises(TypeError, pow, x, y, z)
                    inaczej:
                        self.assertAlmostEqual(pow(x, y, z), 24.0)

        self.assertAlmostEqual(pow(-1, 0.5), 1j)
        self.assertAlmostEqual(pow(-1, 1/3), 0.5 + 0.8660254037844386j)

        self.assertRaises(ValueError, pow, -1, -2, 3)
        self.assertRaises(ValueError, pow, 1, 2, 0)

        self.assertRaises(TypeError, pow)

    def test_input(self):
        self.write_testfile()
        fp = open(TESTFN, 'r')
        savestdin = sys.stdin
        savestdout = sys.stdout # Eats the echo
        spróbuj:
            sys.stdin = fp
            sys.stdout = BitBucket()
            self.assertEqual(input(), "1+1")
            self.assertEqual(input(), 'The quick brown fox jumps over the lazy dog.')
            self.assertEqual(input('testing\n'), 'Dear John')

            # SF 1535165: don't segfault on closed stdin
            # sys.stdout must be a regular file dla triggering
            sys.stdout = savestdout
            sys.stdin.close()
            self.assertRaises(ValueError, input)

            sys.stdout = BitBucket()
            sys.stdin = io.StringIO("NULL\0")
            self.assertRaises(TypeError, input, 42, 42)
            sys.stdin = io.StringIO("    'whitespace'")
            self.assertEqual(input(), "    'whitespace'")
            sys.stdin = io.StringIO()
            self.assertRaises(EOFError, input)

            usuń sys.stdout
            self.assertRaises(RuntimeError, input, 'prompt')
            usuń sys.stdin
            self.assertRaises(RuntimeError, input, 'prompt')
        w_końcu:
            sys.stdin = savestdin
            sys.stdout = savestdout
            fp.close()

    @unittest.skipUnless(pty, "the pty oraz signal modules must be available")
    def check_input_tty(self, prompt, terminal_input, stdio_encoding=Nic):
        jeżeli nie sys.stdin.isatty() albo nie sys.stdout.isatty():
            self.skipTest("stdin oraz stdout must be ttys")
        r, w = os.pipe()
        spróbuj:
            pid, fd = pty.fork()
        wyjąwszy (OSError, AttributeError) jako e:
            os.close(r)
            os.close(w)
            self.skipTest("pty.fork() podnieśd {}".format(e))
        jeżeli pid == 0:
            # Child
            spróbuj:
                # Make sure we don't get stuck jeżeli there's a problem
                signal.alarm(2)
                os.close(r)
                # Check the error handlers are accounted for
                jeżeli stdio_encoding:
                    sys.stdin = io.TextIOWrapper(sys.stdin.detach(),
                                                 encoding=stdio_encoding,
                                                 errors='surrogateescape')
                    sys.stdout = io.TextIOWrapper(sys.stdout.detach(),
                                                  encoding=stdio_encoding,
                                                  errors='replace')
                przy open(w, "w") jako wpipe:
                    print("tty =", sys.stdin.isatty() oraz sys.stdout.isatty(), file=wpipe)
                    print(ascii(input(prompt)), file=wpipe)
            wyjąwszy:
                traceback.print_exc()
            w_końcu:
                # We don't want to zwróć to unittest...
                os._exit(0)
        # Parent
        os.close(w)
        os.write(fd, terminal_input + b"\r\n")
        # Get results z the pipe
        przy open(r, "r") jako rpipe:
            lines = []
            dopóki Prawda:
                line = rpipe.readline().strip()
                jeżeli line == "":
                    # The other end was closed => the child exited
                    przerwij
                lines.append(line)
        # Check the result was got oraz corresponds to the user's terminal input
        jeżeli len(lines) != 2:
            # Something went wrong, try to get at stderr
            przy open(fd, "r", encoding="ascii", errors="ignore") jako child_output:
                self.fail("got %d lines w pipe but expected 2, child output was:\n%s"
                          % (len(lines), child_output.read()))
        os.close(fd)
        # Check we did exercise the GNU readline path
        self.assertIn(lines[0], {'tty = Prawda', 'tty = Nieprawda'})
        jeżeli lines[0] != 'tty = Prawda':
            self.skipTest("standard IO w should have been a tty")
        input_result = eval(lines[1])   # ascii() -> eval() roundtrip
        jeżeli stdio_encoding:
            expected = terminal_input.decode(stdio_encoding, 'surrogateescape')
        inaczej:
            expected = terminal_input.decode(sys.stdin.encoding)  # what inaczej?
        self.assertEqual(input_result, expected)

    def test_input_tty(self):
        # Test input() functionality when wired to a tty (the code path
        # jest different oraz invokes GNU readline jeżeli available).
        self.check_input_tty("prompt", b"quux")

    def test_input_tty_non_ascii(self):
        # Check stdin/stdout encoding jest used when invoking GNU readline
        self.check_input_tty("prompté", b"quux\xe9", "utf-8")

    def test_input_tty_non_ascii_unicode_errors(self):
        # Check stdin/stdout error handler jest used when invoking GNU readline
        self.check_input_tty("prompté", b"quux\xe9", "ascii")

    # test_int(): see test_int.py dla tests of built-in function int().

    def test_repr(self):
        self.assertEqual(repr(''), '\'\'')
        self.assertEqual(repr(0), '0')
        self.assertEqual(repr(()), '()')
        self.assertEqual(repr([]), '[]')
        self.assertEqual(repr({}), '{}')
        a = []
        a.append(a)
        self.assertEqual(repr(a), '[[...]]')
        a = {}
        a[0] = a
        self.assertEqual(repr(a), '{0: {...}}')

    def test_round(self):
        self.assertEqual(round(0.0), 0.0)
        self.assertEqual(type(round(0.0)), int)
        self.assertEqual(round(1.0), 1.0)
        self.assertEqual(round(10.0), 10.0)
        self.assertEqual(round(1000000000.0), 1000000000.0)
        self.assertEqual(round(1e20), 1e20)

        self.assertEqual(round(-1.0), -1.0)
        self.assertEqual(round(-10.0), -10.0)
        self.assertEqual(round(-1000000000.0), -1000000000.0)
        self.assertEqual(round(-1e20), -1e20)

        self.assertEqual(round(0.1), 0.0)
        self.assertEqual(round(1.1), 1.0)
        self.assertEqual(round(10.1), 10.0)
        self.assertEqual(round(1000000000.1), 1000000000.0)

        self.assertEqual(round(-1.1), -1.0)
        self.assertEqual(round(-10.1), -10.0)
        self.assertEqual(round(-1000000000.1), -1000000000.0)

        self.assertEqual(round(0.9), 1.0)
        self.assertEqual(round(9.9), 10.0)
        self.assertEqual(round(999999999.9), 1000000000.0)

        self.assertEqual(round(-0.9), -1.0)
        self.assertEqual(round(-9.9), -10.0)
        self.assertEqual(round(-999999999.9), -1000000000.0)

        self.assertEqual(round(-8.0, -1), -10.0)
        self.assertEqual(type(round(-8.0, -1)), float)

        self.assertEqual(type(round(-8.0, 0)), float)
        self.assertEqual(type(round(-8.0, 1)), float)

        # Check even / odd rounding behaviour
        self.assertEqual(round(5.5), 6)
        self.assertEqual(round(6.5), 6)
        self.assertEqual(round(-5.5), -6)
        self.assertEqual(round(-6.5), -6)

        # Check behavior on ints
        self.assertEqual(round(0), 0)
        self.assertEqual(round(8), 8)
        self.assertEqual(round(-8), -8)
        self.assertEqual(type(round(0)), int)
        self.assertEqual(type(round(-8, -1)), int)
        self.assertEqual(type(round(-8, 0)), int)
        self.assertEqual(type(round(-8, 1)), int)

        # test new kwargs
        self.assertEqual(round(number=-8.0, ndigits=-1), -10.0)

        self.assertRaises(TypeError, round)

        # test generic rounding delegation dla reals
        klasa TestRound:
            def __round__(self):
                zwróć 23

        klasa TestNoRound:
            dalej

        self.assertEqual(round(TestRound()), 23)

        self.assertRaises(TypeError, round, 1, 2, 3)
        self.assertRaises(TypeError, round, TestNoRound())

        t = TestNoRound()
        t.__round__ = lambda *args: args
        self.assertRaises(TypeError, round, t)
        self.assertRaises(TypeError, round, t, 0)

    # Some versions of glibc dla alpha have a bug that affects
    # float -> integer rounding (floor, ceil, rint, round) for
    # values w the range [2**52, 2**53).  See:
    #
    #   http://sources.redhat.com/bugzilla/show_bug.cgi?id=5350
    #
    # We skip this test on Linux/alpha jeżeli it would fail.
    linux_alpha = (platform.system().startswith('Linux') oraz
                   platform.machine().startswith('alpha'))
    system_round_bug = round(5e15+1) != 5e15+1
    @unittest.skipIf(linux_alpha oraz system_round_bug,
                     "test will fail;  failure jest probably due to a "
                     "buggy system round function")
    def test_round_large(self):
        # Issue #1869: integral floats should remain unchanged
        self.assertEqual(round(5e15-1), 5e15-1)
        self.assertEqual(round(5e15), 5e15)
        self.assertEqual(round(5e15+1), 5e15+1)
        self.assertEqual(round(5e15+2), 5e15+2)
        self.assertEqual(round(5e15+3), 5e15+3)

    def test_setattr(self):
        setattr(sys, 'spam', 1)
        self.assertEqual(sys.spam, 1)
        self.assertRaises(TypeError, setattr, sys, 1, 'spam')
        self.assertRaises(TypeError, setattr)

    # test_str(): see test_unicode.py oraz test_bytes.py dla str() tests.

    def test_sum(self):
        self.assertEqual(sum([]), 0)
        self.assertEqual(sum(list(range(2,8))), 27)
        self.assertEqual(sum(iter(list(range(2,8)))), 27)
        self.assertEqual(sum(Squares(10)), 285)
        self.assertEqual(sum(iter(Squares(10))), 285)
        self.assertEqual(sum([[1], [2], [3]], []), [1, 2, 3])

        self.assertRaises(TypeError, sum)
        self.assertRaises(TypeError, sum, 42)
        self.assertRaises(TypeError, sum, ['a', 'b', 'c'])
        self.assertRaises(TypeError, sum, ['a', 'b', 'c'], '')
        self.assertRaises(TypeError, sum, [b'a', b'c'], b'')
        values = [bytearray(b'a'), bytearray(b'b')]
        self.assertRaises(TypeError, sum, values, bytearray(b''))
        self.assertRaises(TypeError, sum, [[1], [2], [3]])
        self.assertRaises(TypeError, sum, [{2:3}])
        self.assertRaises(TypeError, sum, [{2:3}]*2, {2:3})

        klasa BadSeq:
            def __getitem__(self, index):
                podnieś ValueError
        self.assertRaises(ValueError, sum, BadSeq())

        empty = []
        sum(([x] dla x w range(10)), empty)
        self.assertEqual(empty, [])

    def test_type(self):
        self.assertEqual(type(''),  type('123'))
        self.assertNotEqual(type(''), type(()))

    # We don't want self w vars(), so these are static methods

    @staticmethod
    def get_vars_f0():
        zwróć vars()

    @staticmethod
    def get_vars_f2():
        BuiltinTest.get_vars_f0()
        a = 1
        b = 2
        zwróć vars()

    klasa C_get_vars(object):
        def getDict(self):
            zwróć {'a':2}
        __dict__ = property(fget=getDict)

    def test_vars(self):
        self.assertEqual(set(vars()), set(dir()))
        self.assertEqual(set(vars(sys)), set(dir(sys)))
        self.assertEqual(self.get_vars_f0(), {})
        self.assertEqual(self.get_vars_f2(), {'a': 1, 'b': 2})
        self.assertRaises(TypeError, vars, 42, 42)
        self.assertRaises(TypeError, vars, 42)
        self.assertEqual(vars(self.C_get_vars()), {'a':2})

    def test_zip(self):
        a = (1, 2, 3)
        b = (4, 5, 6)
        t = [(1, 4), (2, 5), (3, 6)]
        self.assertEqual(list(zip(a, b)), t)
        b = [4, 5, 6]
        self.assertEqual(list(zip(a, b)), t)
        b = (4, 5, 6, 7)
        self.assertEqual(list(zip(a, b)), t)
        klasa I:
            def __getitem__(self, i):
                jeżeli i < 0 albo i > 2: podnieś IndexError
                zwróć i + 4
        self.assertEqual(list(zip(a, I())), t)
        self.assertEqual(list(zip()), [])
        self.assertEqual(list(zip(*[])), [])
        self.assertRaises(TypeError, zip, Nic)
        klasa G:
            dalej
        self.assertRaises(TypeError, zip, a, G())
        self.assertRaises(RuntimeError, zip, a, TestFailingIter())

        # Make sure zip doesn't try to allocate a billion elements dla the
        # result list when one of its arguments doesn't say how long it is.
        # A MemoryError jest the most likely failure mode.
        klasa SequenceWithoutALength:
            def __getitem__(self, i):
                jeżeli i == 5:
                    podnieś IndexError
                inaczej:
                    zwróć i
        self.assertEqual(
            list(zip(SequenceWithoutALength(), range(2**30))),
            list(enumerate(range(5)))
        )

        klasa BadSeq:
            def __getitem__(self, i):
                jeżeli i == 5:
                    podnieś ValueError
                inaczej:
                    zwróć i
        self.assertRaises(ValueError, list, zip(BadSeq(), BadSeq()))

    def test_zip_pickle(self):
        a = (1, 2, 3)
        b = (4, 5, 6)
        t = [(1, 4), (2, 5), (3, 6)]
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            z1 = zip(a, b)
            self.check_iter_pickle(z1, t, proto)

    def test_format(self):
        # Test the basic machinery of the format() builtin.  Don't test
        #  the specifics of the various formatters
        self.assertEqual(format(3, ''), '3')

        # Returns some classes to use dla various tests.  There's
        #  an old-style version, oraz a new-style version
        def classes_new():
            klasa A(object):
                def __init__(self, x):
                    self.x = x
                def __format__(self, format_spec):
                    zwróć str(self.x) + format_spec
            klasa DerivedFromA(A):
                dalej

            klasa Simple(object): dalej
            klasa DerivedFromSimple(Simple):
                def __init__(self, x):
                    self.x = x
                def __format__(self, format_spec):
                    zwróć str(self.x) + format_spec
            klasa DerivedFromSimple2(DerivedFromSimple): dalej
            zwróć A, DerivedFromA, DerivedFromSimple, DerivedFromSimple2

        def class_test(A, DerivedFromA, DerivedFromSimple, DerivedFromSimple2):
            self.assertEqual(format(A(3), 'spec'), '3spec')
            self.assertEqual(format(DerivedFromA(4), 'spec'), '4spec')
            self.assertEqual(format(DerivedFromSimple(5), 'abc'), '5abc')
            self.assertEqual(format(DerivedFromSimple2(10), 'abcdef'),
                             '10abcdef')

        class_test(*classes_new())

        def empty_format_spec(value):
            # test that:
            #  format(x, '') == str(x)
            #  format(x) == str(x)
            self.assertEqual(format(value, ""), str(value))
            self.assertEqual(format(value), str(value))

        # dla builtin types, format(x, "") == str(x)
        empty_format_spec(17**13)
        empty_format_spec(1.0)
        empty_format_spec(3.1415e104)
        empty_format_spec(-3.1415e104)
        empty_format_spec(3.1415e-104)
        empty_format_spec(-3.1415e-104)
        empty_format_spec(object)
        empty_format_spec(Nic)

        # TypeError because self.__format__ returns the wrong type
        klasa BadFormatResult:
            def __format__(self, format_spec):
                zwróć 1.0
        self.assertRaises(TypeError, format, BadFormatResult(), "")

        # TypeError because format_spec jest nie unicode albo str
        self.assertRaises(TypeError, format, object(), 4)
        self.assertRaises(TypeError, format, object(), object())

        # tests dla object.__format__ really belong inaczejwhere, but
        #  there's no good place to put them
        x = object().__format__('')
        self.assertPrawda(x.startswith('<object object at'))

        # first argument to object.__format__ must be string
        self.assertRaises(TypeError, object().__format__, 3)
        self.assertRaises(TypeError, object().__format__, object())
        self.assertRaises(TypeError, object().__format__, Nic)

        # --------------------------------------------------------------------
        # Issue #7994: object.__format__ przy a non-empty format string jest
        #  deprecated
        def test_deprecated_format_string(obj, fmt_str, should_raise):
            jeżeli should_raise:
                self.assertRaises(TypeError, format, obj, fmt_str)
            inaczej:
                format(obj, fmt_str)

        fmt_strs = ['', 's']

        klasa A:
            def __format__(self, fmt_str):
                zwróć format('', fmt_str)

        dla fmt_str w fmt_strs:
            test_deprecated_format_string(A(), fmt_str, Nieprawda)

        klasa B:
            dalej

        klasa C(object):
            dalej

        dla cls w [object, B, C]:
            dla fmt_str w fmt_strs:
                test_deprecated_format_string(cls(), fmt_str, len(fmt_str) != 0)
        # --------------------------------------------------------------------

        # make sure we can take a subclass of str jako a format spec
        klasa DerivedFromStr(str): dalej
        self.assertEqual(format(0, DerivedFromStr('10')), '         0')

    def test_bin(self):
        self.assertEqual(bin(0), '0b0')
        self.assertEqual(bin(1), '0b1')
        self.assertEqual(bin(-1), '-0b1')
        self.assertEqual(bin(2**65), '0b1' + '0' * 65)
        self.assertEqual(bin(2**65-1), '0b' + '1' * 65)
        self.assertEqual(bin(-(2**65)), '-0b1' + '0' * 65)
        self.assertEqual(bin(-(2**65-1)), '-0b' + '1' * 65)

    def test_bytearray_translate(self):
        x = bytearray(b"abc")
        self.assertRaises(ValueError, x.translate, b"1", 1)
        self.assertRaises(TypeError, x.translate, b"1"*256, 1)

    def test_construct_singletons(self):
        dla const w Nic, Ellipsis, NotImplemented:
            tp = type(const)
            self.assertIs(tp(), const)
            self.assertRaises(TypeError, tp, 1, 2)
            self.assertRaises(TypeError, tp, a=1, b=2)

klasa TestSorted(unittest.TestCase):

    def test_basic(self):
        data = list(range(100))
        copy = data[:]
        random.shuffle(copy)
        self.assertEqual(data, sorted(copy))
        self.assertNotEqual(data, copy)

        data.reverse()
        random.shuffle(copy)
        self.assertEqual(data, sorted(copy, key=lambda x: -x))
        self.assertNotEqual(data, copy)
        random.shuffle(copy)
        self.assertEqual(data, sorted(copy, reverse=1))
        self.assertNotEqual(data, copy)

    def test_inputtypes(self):
        s = 'abracadabra'
        types = [list, tuple, str]
        dla T w types:
            self.assertEqual(sorted(s), sorted(T(s)))

        s = ''.join(set(s))  # unique letters only
        types = [str, set, frozenset, list, tuple, dict.fromkeys]
        dla T w types:
            self.assertEqual(sorted(s), sorted(T(s)))

    def test_baddecorator(self):
        data = 'The quick Brown fox Jumped over The lazy Dog'.split()
        self.assertRaises(TypeError, sorted, data, Nic, lambda x,y: 0)


klasa ShutdownTest(unittest.TestCase):

    def test_cleanup(self):
        # Issue #19255: builtins are still available at shutdown
        code = """jeżeli 1:
            zaimportuj builtins
            zaimportuj sys

            klasa C:
                def __del__(self):
                    print("before")
                    # Check that builtins still exist
                    len(())
                    print("after")

            c = C()
            # Make this module survive until builtins oraz sys are cleaned
            builtins.here = sys.modules[__name__]
            sys.here = sys.modules[__name__]
            # Create a reference loop so that this module needs to go
            # through a GC phase.
            here = sys.modules[__name__]
            """
        # Issue #20599: Force ASCII encoding to get a codec implemented w C,
        # otherwise the codec may be unloaded before C.__del__() jest called, oraz
        # so print("before") fails because the codec cannot be used to encode
        # "before" to sys.stdout.encoding. For example, on Windows,
        # sys.stdout.encoding jest the OEM code page oraz these code pages are
        # implemented w Python
        rc, out, err = assert_python_ok("-c", code,
                                        PYTHONIOENCODING="ascii")
        self.assertEqual(["before", "after"], out.decode().splitlines())


def load_tests(loader, tests, pattern):
    z doctest zaimportuj DocTestSuite
    tests.addTest(DocTestSuite(builtins))
    zwróć tests

jeżeli __name__ == "__main__":
    unittest.main()
