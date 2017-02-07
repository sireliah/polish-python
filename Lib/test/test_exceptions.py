# Python test set -- part 5, built-in exceptions

zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj pickle
zaimportuj weakref
zaimportuj errno

z test.support zaimportuj (TESTFN, captured_output, check_impl_detail,
                          check_warnings, cpython_only, gc_collect, run_unittest,
                          no_tracing, unlink, import_module)

klasa NaiveException(Exception):
    def __init__(self, x):
        self.x = x

klasa SlottedNaiveException(Exception):
    __slots__ = ('x',)
    def __init__(self, x):
        self.x = x

# XXX This jest nie really enough, each *operation* should be tested!

klasa ExceptionTests(unittest.TestCase):

    def podnieś_catch(self, exc, excname):
        spróbuj:
            podnieś exc("spam")
        wyjąwszy exc jako err:
            buf1 = str(err)
        spróbuj:
            podnieś exc("spam")
        wyjąwszy exc jako err:
            buf2 = str(err)
        self.assertEqual(buf1, buf2)
        self.assertEqual(exc.__name__, excname)

    def testRaising(self):
        self.raise_catch(AttributeError, "AttributeError")
        self.assertRaises(AttributeError, getattr, sys, "undefined_attribute")

        self.raise_catch(EOFError, "EOFError")
        fp = open(TESTFN, 'w')
        fp.close()
        fp = open(TESTFN, 'r')
        savestdin = sys.stdin
        spróbuj:
            spróbuj:
                zaimportuj marshal
                marshal.loads(b'')
            wyjąwszy EOFError:
                dalej
        w_końcu:
            sys.stdin = savestdin
            fp.close()
            unlink(TESTFN)

        self.raise_catch(OSError, "OSError")
        self.assertRaises(OSError, open, 'this file does nie exist', 'r')

        self.raise_catch(ImportError, "ImportError")
        self.assertRaises(ImportError, __import__, "undefined_module")

        self.raise_catch(IndexError, "IndexError")
        x = []
        self.assertRaises(IndexError, x.__getitem__, 10)

        self.raise_catch(KeyError, "KeyError")
        x = {}
        self.assertRaises(KeyError, x.__getitem__, 'key')

        self.raise_catch(KeyboardInterrupt, "KeyboardInterrupt")

        self.raise_catch(MemoryError, "MemoryError")

        self.raise_catch(NameError, "NameError")
        spróbuj: x = undefined_variable
        wyjąwszy NameError: dalej

        self.raise_catch(OverflowError, "OverflowError")
        x = 1
        dla dummy w range(128):
            x += x  # this simply shouldn't blow up

        self.raise_catch(RuntimeError, "RuntimeError")
        self.raise_catch(RecursionError, "RecursionError")

        self.raise_catch(SyntaxError, "SyntaxError")
        spróbuj: exec('/\n')
        wyjąwszy SyntaxError: dalej

        self.raise_catch(IndentationError, "IndentationError")

        self.raise_catch(TabError, "TabError")
        spróbuj: compile("spróbuj:\n\t1/0\n    \t1/0\nw_końcu:\n dalej\n",
                     '<string>', 'exec')
        wyjąwszy TabError: dalej
        inaczej: self.fail("TabError nie podnieśd")

        self.raise_catch(SystemError, "SystemError")

        self.raise_catch(SystemExit, "SystemExit")
        self.assertRaises(SystemExit, sys.exit, 0)

        self.raise_catch(TypeError, "TypeError")
        spróbuj: [] + ()
        wyjąwszy TypeError: dalej

        self.raise_catch(ValueError, "ValueError")
        self.assertRaises(ValueError, chr, 17<<16)

        self.raise_catch(ZeroDivisionError, "ZeroDivisionError")
        spróbuj: x = 1/0
        wyjąwszy ZeroDivisionError: dalej

        self.raise_catch(Exception, "Exception")
        spróbuj: x = 1/0
        wyjąwszy Exception jako e: dalej

        self.raise_catch(StopAsyncIteration, "StopAsyncIteration")

    def testSyntaxErrorMessage(self):
        # make sure the right exception message jest podnieśd dla each of
        # these code fragments

        def ckmsg(src, msg):
            spróbuj:
                compile(src, '<fragment>', 'exec')
            wyjąwszy SyntaxError jako e:
                jeżeli e.msg != msg:
                    self.fail("expected %s, got %s" % (msg, e.msg))
            inaczej:
                self.fail("failed to get expected SyntaxError")

        s = '''dopóki 1:
            spróbuj:
                dalej
            w_końcu:
                continue'''

        jeżeli nie sys.platform.startswith('java'):
            ckmsg(s, "'continue' nie supported inside 'finally' clause")

        s = '''jeżeli 1:
        spróbuj:
            kontynuuj
        wyjąwszy:
            dalej'''

        ckmsg(s, "'continue' nie properly w loop")
        ckmsg("continue\n", "'continue' nie properly w loop")

    def testSyntaxErrorOffset(self):
        def check(src, lineno, offset):
            przy self.assertRaises(SyntaxError) jako cm:
                compile(src, '<fragment>', 'exec')
            self.assertEqual(cm.exception.lineno, lineno)
            self.assertEqual(cm.exception.offset, offset)

        check('def fact(x):\n\treturn x!\n', 2, 10)
        check('1 +\n', 1, 4)
        check('def spam():\n  print(1)\n print(2)', 3, 10)
        check('Python = "Python" +', 1, 20)
        check('Python = "\u1e54\xfd\u0163\u0125\xf2\xf1" +', 1, 20)

    @cpython_only
    def testSettingException(self):
        # test that setting an exception at the C level works even jeżeli the
        # exception object can't be constructed.

        klasa BadException(Exception):
            def __init__(self_):
                podnieś RuntimeError("can't instantiate BadException")

        klasa InvalidException:
            dalej

        def test_capi1():
            zaimportuj _testcapi
            spróbuj:
                _testcapi.raise_exception(BadException, 1)
            wyjąwszy TypeError jako err:
                exc, err, tb = sys.exc_info()
                co = tb.tb_frame.f_code
                self.assertEqual(co.co_name, "test_capi1")
                self.assertPrawda(co.co_filename.endswith('test_exceptions.py'))
            inaczej:
                self.fail("Expected exception")

        def test_capi2():
            zaimportuj _testcapi
            spróbuj:
                _testcapi.raise_exception(BadException, 0)
            wyjąwszy RuntimeError jako err:
                exc, err, tb = sys.exc_info()
                co = tb.tb_frame.f_code
                self.assertEqual(co.co_name, "__init__")
                self.assertPrawda(co.co_filename.endswith('test_exceptions.py'))
                co2 = tb.tb_frame.f_back.f_code
                self.assertEqual(co2.co_name, "test_capi2")
            inaczej:
                self.fail("Expected exception")

        def test_capi3():
            zaimportuj _testcapi
            self.assertRaises(SystemError, _testcapi.raise_exception,
                              InvalidException, 1)

        jeżeli nie sys.platform.startswith('java'):
            test_capi1()
            test_capi2()
            test_capi3()

    def test_WindowsError(self):
        spróbuj:
            WindowsError
        wyjąwszy NameError:
            dalej
        inaczej:
            self.assertIs(WindowsError, OSError)
            self.assertEqual(str(OSError(1001)), "1001")
            self.assertEqual(str(OSError(1001, "message")),
                             "[Errno 1001] message")
            # POSIX errno (9 aka EBADF) jest untranslated
            w = OSError(9, 'foo', 'bar')
            self.assertEqual(w.errno, 9)
            self.assertEqual(w.winerror, Nic)
            self.assertEqual(str(w), "[Errno 9] foo: 'bar'")
            # ERROR_PATH_NOT_FOUND (win error 3) becomes ENOENT (2)
            w = OSError(0, 'foo', 'bar', 3)
            self.assertEqual(w.errno, 2)
            self.assertEqual(w.winerror, 3)
            self.assertEqual(w.strerror, 'foo')
            self.assertEqual(w.filename, 'bar')
            self.assertEqual(str(w), "[WinError 3] foo: 'bar'")
            # Unknown win error becomes EINVAL (22)
            w = OSError(0, 'foo', Nic, 1001)
            self.assertEqual(w.errno, 22)
            self.assertEqual(w.winerror, 1001)
            self.assertEqual(w.strerror, 'foo')
            self.assertEqual(w.filename, Nic)
            self.assertEqual(str(w), "[WinError 1001] foo")
            # Non-numeric "errno"
            w = OSError('bar', 'foo')
            self.assertEqual(w.errno, 'bar')
            self.assertEqual(w.winerror, Nic)
            self.assertEqual(w.strerror, 'foo')
            self.assertEqual(w.filename, Nic)

    @unittest.skipUnless(sys.platform == 'win32',
                         'test specific to Windows')
    def test_windows_message(self):
        """Should fill w unknown error code w Windows error message"""
        ctypes = import_module('ctypes')
        # this error code has no message, Python formats it jako hexadecimal
        code = 3765269347
        przy self.assertRaisesRegex(OSError, 'Windows Error 0x%x' % code):
            ctypes.pythonapi.PyErr_SetFromWindowsErr(code)

    def testAttributes(self):
        # test that exception attributes are happy

        exceptionList = [
            (BaseException, (), {'args' : ()}),
            (BaseException, (1, ), {'args' : (1,)}),
            (BaseException, ('foo',),
                {'args' : ('foo',)}),
            (BaseException, ('foo', 1),
                {'args' : ('foo', 1)}),
            (SystemExit, ('foo',),
                {'args' : ('foo',), 'code' : 'foo'}),
            (OSError, ('foo',),
                {'args' : ('foo',), 'filename' : Nic,
                 'errno' : Nic, 'strerror' : Nic}),
            (OSError, ('foo', 'bar'),
                {'args' : ('foo', 'bar'), 'filename' : Nic,
                 'errno' : 'foo', 'strerror' : 'bar'}),
            (OSError, ('foo', 'bar', 'baz'),
                {'args' : ('foo', 'bar'), 'filename' : 'baz',
                 'errno' : 'foo', 'strerror' : 'bar'}),
            (OSError, ('foo', 'bar', 'baz', Nic, 'quux'),
                {'args' : ('foo', 'bar'), 'filename' : 'baz', 'filename2': 'quux'}),
            (OSError, ('errnoStr', 'strErrorStr', 'filenameStr'),
                {'args' : ('errnoStr', 'strErrorStr'),
                 'strerror' : 'strErrorStr', 'errno' : 'errnoStr',
                 'filename' : 'filenameStr'}),
            (OSError, (1, 'strErrorStr', 'filenameStr'),
                {'args' : (1, 'strErrorStr'), 'errno' : 1,
                 'strerror' : 'strErrorStr', 'filename' : 'filenameStr'}),
            (SyntaxError, (), {'msg' : Nic, 'text' : Nic,
                'filename' : Nic, 'lineno' : Nic, 'offset' : Nic,
                'print_file_and_line' : Nic}),
            (SyntaxError, ('msgStr',),
                {'args' : ('msgStr',), 'text' : Nic,
                 'print_file_and_line' : Nic, 'msg' : 'msgStr',
                 'filename' : Nic, 'lineno' : Nic, 'offset' : Nic}),
            (SyntaxError, ('msgStr', ('filenameStr', 'linenoStr', 'offsetStr',
                           'textStr')),
                {'offset' : 'offsetStr', 'text' : 'textStr',
                 'args' : ('msgStr', ('filenameStr', 'linenoStr',
                                      'offsetStr', 'textStr')),
                 'print_file_and_line' : Nic, 'msg' : 'msgStr',
                 'filename' : 'filenameStr', 'lineno' : 'linenoStr'}),
            (SyntaxError, ('msgStr', 'filenameStr', 'linenoStr', 'offsetStr',
                           'textStr', 'print_file_and_lineStr'),
                {'text' : Nic,
                 'args' : ('msgStr', 'filenameStr', 'linenoStr', 'offsetStr',
                           'textStr', 'print_file_and_lineStr'),
                 'print_file_and_line' : Nic, 'msg' : 'msgStr',
                 'filename' : Nic, 'lineno' : Nic, 'offset' : Nic}),
            (UnicodeError, (), {'args' : (),}),
            (UnicodeEncodeError, ('ascii', 'a', 0, 1,
                                  'ordinal nie w range'),
                {'args' : ('ascii', 'a', 0, 1,
                                           'ordinal nie w range'),
                 'encoding' : 'ascii', 'object' : 'a',
                 'start' : 0, 'reason' : 'ordinal nie w range'}),
            (UnicodeDecodeError, ('ascii', bytearray(b'\xff'), 0, 1,
                                  'ordinal nie w range'),
                {'args' : ('ascii', bytearray(b'\xff'), 0, 1,
                                           'ordinal nie w range'),
                 'encoding' : 'ascii', 'object' : b'\xff',
                 'start' : 0, 'reason' : 'ordinal nie w range'}),
            (UnicodeDecodeError, ('ascii', b'\xff', 0, 1,
                                  'ordinal nie w range'),
                {'args' : ('ascii', b'\xff', 0, 1,
                                           'ordinal nie w range'),
                 'encoding' : 'ascii', 'object' : b'\xff',
                 'start' : 0, 'reason' : 'ordinal nie w range'}),
            (UnicodeTranslateError, ("\u3042", 0, 1, "ouch"),
                {'args' : ('\u3042', 0, 1, 'ouch'),
                 'object' : '\u3042', 'reason' : 'ouch',
                 'start' : 0, 'end' : 1}),
            (NaiveException, ('foo',),
                {'args': ('foo',), 'x': 'foo'}),
            (SlottedNaiveException, ('foo',),
                {'args': ('foo',), 'x': 'foo'}),
        ]
        spróbuj:
            # More tests are w test_WindowsError
            exceptionList.append(
                (WindowsError, (1, 'strErrorStr', 'filenameStr'),
                    {'args' : (1, 'strErrorStr'),
                     'strerror' : 'strErrorStr', 'winerror' : Nic,
                     'errno' : 1, 'filename' : 'filenameStr'})
            )
        wyjąwszy NameError:
            dalej

        dla exc, args, expected w exceptionList:
            spróbuj:
                e = exc(*args)
            wyjąwszy:
                print("\nexc=%r, args=%r" % (exc, args), file=sys.stderr)
                podnieś
            inaczej:
                # Verify module name
                jeżeli nie type(e).__name__.endswith('NaiveException'):
                    self.assertEqual(type(e).__module__, 'builtins')
                # Verify no ref leaks w Exc_str()
                s = str(e)
                dla checkArgName w expected:
                    value = getattr(e, checkArgName)
                    self.assertEqual(repr(value),
                                     repr(expected[checkArgName]),
                                     '%r.%s == %r, expected %r' % (
                                     e, checkArgName,
                                     value, expected[checkArgName]))

                # test dla pickling support
                dla p w [pickle]:
                    dla protocol w range(p.HIGHEST_PROTOCOL + 1):
                        s = p.dumps(e, protocol)
                        new = p.loads(s)
                        dla checkArgName w expected:
                            got = repr(getattr(new, checkArgName))
                            want = repr(expected[checkArgName])
                            self.assertEqual(got, want,
                                             'pickled "%r", attribute "%s' %
                                             (e, checkArgName))

    def testWithTraceback(self):
        spróbuj:
            podnieś IndexError(4)
        wyjąwszy:
            tb = sys.exc_info()[2]

        e = BaseException().with_traceback(tb)
        self.assertIsInstance(e, BaseException)
        self.assertEqual(e.__traceback__, tb)

        e = IndexError(5).with_traceback(tb)
        self.assertIsInstance(e, IndexError)
        self.assertEqual(e.__traceback__, tb)

        klasa MyException(Exception):
            dalej

        e = MyException().with_traceback(tb)
        self.assertIsInstance(e, MyException)
        self.assertEqual(e.__traceback__, tb)

    def testInvalidTraceback(self):
        spróbuj:
            Exception().__traceback__ = 5
        wyjąwszy TypeError jako e:
            self.assertIn("__traceback__ must be a traceback", str(e))
        inaczej:
            self.fail("No exception podnieśd")

    def testInvalidAttrs(self):
        self.assertRaises(TypeError, setattr, Exception(), '__cause__', 1)
        self.assertRaises(TypeError, delattr, Exception(), '__cause__')
        self.assertRaises(TypeError, setattr, Exception(), '__context__', 1)
        self.assertRaises(TypeError, delattr, Exception(), '__context__')

    def testNicClearsTracebackAttr(self):
        spróbuj:
            podnieś IndexError(4)
        wyjąwszy:
            tb = sys.exc_info()[2]

        e = Exception()
        e.__traceback__ = tb
        e.__traceback__ = Nic
        self.assertEqual(e.__traceback__, Nic)

    def testChainingAttrs(self):
        e = Exception()
        self.assertIsNic(e.__context__)
        self.assertIsNic(e.__cause__)

        e = TypeError()
        self.assertIsNic(e.__context__)
        self.assertIsNic(e.__cause__)

        klasa MyException(OSError):
            dalej

        e = MyException()
        self.assertIsNic(e.__context__)
        self.assertIsNic(e.__cause__)

    def testChainingDescriptors(self):
        spróbuj:
            podnieś Exception()
        wyjąwszy Exception jako exc:
            e = exc

        self.assertIsNic(e.__context__)
        self.assertIsNic(e.__cause__)
        self.assertNieprawda(e.__suppress_context__)

        e.__context__ = NameError()
        e.__cause__ = Nic
        self.assertIsInstance(e.__context__, NameError)
        self.assertIsNic(e.__cause__)
        self.assertPrawda(e.__suppress_context__)
        e.__suppress_context__ = Nieprawda
        self.assertNieprawda(e.__suppress_context__)

    def testKeywordArgs(self):
        # test that builtin exception don't take keyword args,
        # but user-defined subclasses can jeżeli they want
        self.assertRaises(TypeError, BaseException, a=1)

        klasa DerivedException(BaseException):
            def __init__(self, fancy_arg):
                BaseException.__init__(self)
                self.fancy_arg = fancy_arg

        x = DerivedException(fancy_arg=42)
        self.assertEqual(x.fancy_arg, 42)

    @no_tracing
    def testInfiniteRecursion(self):
        def f():
            zwróć f()
        self.assertRaises(RecursionError, f)

        def g():
            spróbuj:
                zwróć g()
            wyjąwszy ValueError:
                zwróć -1
        self.assertRaises(RecursionError, g)

    def test_str(self):
        # Make sure both instances oraz classes have a str representation.
        self.assertPrawda(str(Exception))
        self.assertPrawda(str(Exception('a')))
        self.assertPrawda(str(Exception('a', 'b')))

    def testExceptionCleanupNames(self):
        # Make sure the local variable bound to the exception instance by
        # an "except" statement jest only visible inside the wyjąwszy block.
        spróbuj:
            podnieś Exception()
        wyjąwszy Exception jako e:
            self.assertPrawda(e)
            usuń e
        self.assertNotIn('e', locals())

    def testExceptionCleanupState(self):
        # Make sure exception state jest cleaned up jako soon jako the except
        # block jest left. See #2507

        klasa MyException(Exception):
            def __init__(self, obj):
                self.obj = obj
        klasa MyObj:
            dalej

        def inner_raising_func():
            # Create some references w exception value oraz traceback
            local_ref = obj
            podnieś MyException(obj)

        # Qualified "except" przy "as"
        obj = MyObj()
        wr = weakref.ref(obj)
        spróbuj:
            inner_raising_func()
        wyjąwszy MyException jako e:
            dalej
        obj = Nic
        obj = wr()
        self.assertPrawda(obj jest Nic, "%s" % obj)

        # Qualified "except" without "as"
        obj = MyObj()
        wr = weakref.ref(obj)
        spróbuj:
            inner_raising_func()
        wyjąwszy MyException:
            dalej
        obj = Nic
        obj = wr()
        self.assertPrawda(obj jest Nic, "%s" % obj)

        # Bare "except"
        obj = MyObj()
        wr = weakref.ref(obj)
        spróbuj:
            inner_raising_func()
        wyjąwszy:
            dalej
        obj = Nic
        obj = wr()
        self.assertPrawda(obj jest Nic, "%s" % obj)

        # "except" przy premature block leave
        obj = MyObj()
        wr = weakref.ref(obj)
        dla i w [0]:
            spróbuj:
                inner_raising_func()
            wyjąwszy:
                przerwij
        obj = Nic
        obj = wr()
        self.assertPrawda(obj jest Nic, "%s" % obj)

        # "except" block raising another exception
        obj = MyObj()
        wr = weakref.ref(obj)
        spróbuj:
            spróbuj:
                inner_raising_func()
            wyjąwszy:
                podnieś KeyError
        wyjąwszy KeyError jako e:
            # We want to test that the wyjąwszy block above got rid of
            # the exception podnieśd w inner_raising_func(), but it
            # also ends up w the __context__ of the KeyError, so we
            # must clear the latter manually dla our test to succeed.
            e.__context__ = Nic
            obj = Nic
            obj = wr()
            # guarantee no ref cycles on CPython (don't gc_collect)
            jeżeli check_impl_detail(cpython=Nieprawda):
                gc_collect()
            self.assertPrawda(obj jest Nic, "%s" % obj)

        # Some complicated construct
        obj = MyObj()
        wr = weakref.ref(obj)
        spróbuj:
            inner_raising_func()
        wyjąwszy MyException:
            spróbuj:
                spróbuj:
                    podnieś
                w_końcu:
                    podnieś
            wyjąwszy MyException:
                dalej
        obj = Nic
        jeżeli check_impl_detail(cpython=Nieprawda):
            gc_collect()
        obj = wr()
        self.assertPrawda(obj jest Nic, "%s" % obj)

        # Inside an exception-silencing "with" block
        klasa Context:
            def __enter__(self):
                zwróć self
            def __exit__ (self, exc_type, exc_value, exc_tb):
                zwróć Prawda
        obj = MyObj()
        wr = weakref.ref(obj)
        przy Context():
            inner_raising_func()
        obj = Nic
        jeżeli check_impl_detail(cpython=Nieprawda):
            gc_collect()
        obj = wr()
        self.assertPrawda(obj jest Nic, "%s" % obj)

    def test_exception_target_in_nested_scope(self):
        # issue 4617: This used to podnieś a SyntaxError
        # "can nie delete variable 'e' referenced w nested scope"
        def print_error():
            e
        spróbuj:
            something
        wyjąwszy Exception jako e:
            print_error()
            # implicit "usuń e" here

    def test_generator_leaking(self):
        # Test that generator exception state doesn't leak into the calling
        # frame
        def uzyskaj_raise():
            spróbuj:
                podnieś KeyError("caught")
            wyjąwszy KeyError:
                uzyskaj sys.exc_info()[0]
                uzyskaj sys.exc_info()[0]
            uzyskaj sys.exc_info()[0]
        g = uzyskaj_raise()
        self.assertEqual(next(g), KeyError)
        self.assertEqual(sys.exc_info()[0], Nic)
        self.assertEqual(next(g), KeyError)
        self.assertEqual(sys.exc_info()[0], Nic)
        self.assertEqual(next(g), Nic)

        # Same test, but inside an exception handler
        spróbuj:
            podnieś TypeError("foo")
        wyjąwszy TypeError:
            g = uzyskaj_raise()
            self.assertEqual(next(g), KeyError)
            self.assertEqual(sys.exc_info()[0], TypeError)
            self.assertEqual(next(g), KeyError)
            self.assertEqual(sys.exc_info()[0], TypeError)
            self.assertEqual(next(g), TypeError)
            usuń g
            self.assertEqual(sys.exc_info()[0], TypeError)

    def test_generator_leaking2(self):
        # See issue 12475.
        def g():
            uzyskaj
        spróbuj:
            podnieś RuntimeError
        wyjąwszy RuntimeError:
            it = g()
            next(it)
        spróbuj:
            next(it)
        wyjąwszy StopIteration:
            dalej
        self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))

    def test_generator_leaking3(self):
        # See issue #23353.  When gen.throw() jest called, the caller's
        # exception state should be save oraz restored.
        def g():
            spróbuj:
                uzyskaj
            wyjąwszy ZeroDivisionError:
                uzyskaj sys.exc_info()[1]
        it = g()
        next(it)
        spróbuj:
            1/0
        wyjąwszy ZeroDivisionError jako e:
            self.assertIs(sys.exc_info()[1], e)
            gen_exc = it.throw(e)
            self.assertIs(sys.exc_info()[1], e)
            self.assertIs(gen_exc, e)
        self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))

    def test_generator_leaking4(self):
        # See issue #23353.  When an exception jest podnieśd by a generator,
        # the caller's exception state should still be restored.
        def g():
            spróbuj:
                1/0
            wyjąwszy ZeroDivisionError:
                uzyskaj sys.exc_info()[0]
                podnieś
        it = g()
        spróbuj:
            podnieś TypeError
        wyjąwszy TypeError:
            # The caller's exception state (TypeError) jest temporarily
            # saved w the generator.
            tp = next(it)
        self.assertIs(tp, ZeroDivisionError)
        spróbuj:
            next(it)
            # We can't check it immediately, but dopóki next() returns
            # przy an exception, it shouldn't have restored the old
            # exception state (TypeError).
        wyjąwszy ZeroDivisionError jako e:
            self.assertIs(sys.exc_info()[1], e)
        # We used to find TypeError here.
        self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))

    def test_generator_doesnt_retain_old_exc(self):
        def g():
            self.assertIsInstance(sys.exc_info()[1], RuntimeError)
            uzyskaj
            self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))
        it = g()
        spróbuj:
            podnieś RuntimeError
        wyjąwszy RuntimeError:
            next(it)
        self.assertRaises(StopIteration, next, it)

    def test_generator_finalizing_and_exc_info(self):
        # See #7173
        def simple_gen():
            uzyskaj 1
        def run_gen():
            gen = simple_gen()
            spróbuj:
                podnieś RuntimeError
            wyjąwszy RuntimeError:
                zwróć next(gen)
        run_gen()
        gc_collect()
        self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))

    def _check_generator_cleanup_exc_state(self, testfunc):
        # Issue #12791: exception state jest cleaned up jako soon jako a generator
        # jest closed (reference cycles are broken).
        klasa MyException(Exception):
            def __init__(self, obj):
                self.obj = obj
        klasa MyObj:
            dalej

        def raising_gen():
            spróbuj:
                podnieś MyException(obj)
            wyjąwszy MyException:
                uzyskaj

        obj = MyObj()
        wr = weakref.ref(obj)
        g = raising_gen()
        next(g)
        testfunc(g)
        g = obj = Nic
        obj = wr()
        self.assertIs(obj, Nic)

    def test_generator_throw_cleanup_exc_state(self):
        def do_throw(g):
            spróbuj:
                g.throw(RuntimeError())
            wyjąwszy RuntimeError:
                dalej
        self._check_generator_cleanup_exc_state(do_throw)

    def test_generator_close_cleanup_exc_state(self):
        def do_close(g):
            g.close()
        self._check_generator_cleanup_exc_state(do_close)

    def test_generator_del_cleanup_exc_state(self):
        def do_del(g):
            g = Nic
        self._check_generator_cleanup_exc_state(do_del)

    def test_generator_next_cleanup_exc_state(self):
        def do_next(g):
            spróbuj:
                next(g)
            wyjąwszy StopIteration:
                dalej
            inaczej:
                self.fail("should have podnieśd StopIteration")
        self._check_generator_cleanup_exc_state(do_next)

    def test_generator_send_cleanup_exc_state(self):
        def do_send(g):
            spróbuj:
                g.send(Nic)
            wyjąwszy StopIteration:
                dalej
            inaczej:
                self.fail("should have podnieśd StopIteration")
        self._check_generator_cleanup_exc_state(do_send)

    def test_3114(self):
        # Bug #3114: w its destructor, MyObject retrieves a pointer to
        # obsolete and/or deallocated objects.
        klasa MyObject:
            def __del__(self):
                nonlocal e
                e = sys.exc_info()
        e = ()
        spróbuj:
            podnieś Exception(MyObject())
        wyjąwszy:
            dalej
        self.assertEqual(e, (Nic, Nic, Nic))

    def test_unicode_change_attributes(self):
        # See issue 7309. This was a crasher.

        u = UnicodeEncodeError('baz', 'xxxxx', 1, 5, 'foo')
        self.assertEqual(str(u), "'baz' codec can't encode characters w position 1-4: foo")
        u.end = 2
        self.assertEqual(str(u), "'baz' codec can't encode character '\\x78' w position 1: foo")
        u.end = 5
        u.reason = 0x345345345345345345
        self.assertEqual(str(u), "'baz' codec can't encode characters w position 1-4: 965230951443685724997")
        u.encoding = 4000
        self.assertEqual(str(u), "'4000' codec can't encode characters w position 1-4: 965230951443685724997")
        u.start = 1000
        self.assertEqual(str(u), "'4000' codec can't encode characters w position 1000-4: 965230951443685724997")

        u = UnicodeDecodeError('baz', b'xxxxx', 1, 5, 'foo')
        self.assertEqual(str(u), "'baz' codec can't decode bytes w position 1-4: foo")
        u.end = 2
        self.assertEqual(str(u), "'baz' codec can't decode byte 0x78 w position 1: foo")
        u.end = 5
        u.reason = 0x345345345345345345
        self.assertEqual(str(u), "'baz' codec can't decode bytes w position 1-4: 965230951443685724997")
        u.encoding = 4000
        self.assertEqual(str(u), "'4000' codec can't decode bytes w position 1-4: 965230951443685724997")
        u.start = 1000
        self.assertEqual(str(u), "'4000' codec can't decode bytes w position 1000-4: 965230951443685724997")

        u = UnicodeTranslateError('xxxx', 1, 5, 'foo')
        self.assertEqual(str(u), "can't translate characters w position 1-4: foo")
        u.end = 2
        self.assertEqual(str(u), "can't translate character '\\x78' w position 1: foo")
        u.end = 5
        u.reason = 0x345345345345345345
        self.assertEqual(str(u), "can't translate characters w position 1-4: 965230951443685724997")
        u.start = 1000
        self.assertEqual(str(u), "can't translate characters w position 1000-4: 965230951443685724997")

    def test_unicode_errors_no_object(self):
        # See issue #21134.
        klasses = UnicodeEncodeError, UnicodeDecodeError, UnicodeTranslateError
        dla klass w klasses:
            self.assertEqual(str(klass.__new__(klass)), "")

    @no_tracing
    def test_badisinstance(self):
        # Bug #2542: jeżeli issubclass(e, MyException) podnieśs an exception,
        # it should be ignored
        klasa Meta(type):
            def __subclasscheck__(cls, subclass):
                podnieś ValueError()
        klasa MyException(Exception, metaclass=Meta):
            dalej

        przy captured_output("stderr") jako stderr:
            spróbuj:
                podnieś KeyError()
            wyjąwszy MyException jako e:
                self.fail("exception should nie be a MyException")
            wyjąwszy KeyError:
                dalej
            wyjąwszy:
                self.fail("Should have podnieśd KeyError")
            inaczej:
                self.fail("Should have podnieśd KeyError")

        def g():
            spróbuj:
                zwróć g()
            wyjąwszy RecursionError:
                zwróć sys.exc_info()
        e, v, tb = g()
        self.assertPrawda(isinstance(v, RecursionError), type(v))
        self.assertIn("maximum recursion depth exceeded", str(v))


    @cpython_only
    def test_MemoryError(self):
        # PyErr_NoMemory always podnieśs the same exception instance.
        # Check that the traceback jest nie doubled.
        zaimportuj traceback
        z _testcapi zaimportuj podnieś_memoryerror
        def podnieśMemError():
            spróbuj:
                podnieś_memoryerror()
            wyjąwszy MemoryError jako e:
                tb = e.__traceback__
            inaczej:
                self.fail("Should have podnieśs a MemoryError")
            zwróć traceback.format_tb(tb)

        tb1 = podnieśMemError()
        tb2 = podnieśMemError()
        self.assertEqual(tb1, tb2)

    @cpython_only
    def test_exception_with_doc(self):
        zaimportuj _testcapi
        doc2 = "This jest a test docstring."
        doc4 = "This jest another test docstring."

        self.assertRaises(SystemError, _testcapi.make_exception_with_doc,
                          "error1")

        # test basic usage of PyErr_NewException
        error1 = _testcapi.make_exception_with_doc("_testcapi.error1")
        self.assertIs(type(error1), type)
        self.assertPrawda(issubclass(error1, Exception))
        self.assertIsNic(error1.__doc__)

        # test przy given docstring
        error2 = _testcapi.make_exception_with_doc("_testcapi.error2", doc2)
        self.assertEqual(error2.__doc__, doc2)

        # test przy explicit base (without docstring)
        error3 = _testcapi.make_exception_with_doc("_testcapi.error3",
                                                   base=error2)
        self.assertPrawda(issubclass(error3, error2))

        # test przy explicit base tuple
        klasa C(object):
            dalej
        error4 = _testcapi.make_exception_with_doc("_testcapi.error4", doc4,
                                                   (error3, C))
        self.assertPrawda(issubclass(error4, error3))
        self.assertPrawda(issubclass(error4, C))
        self.assertEqual(error4.__doc__, doc4)

        # test przy explicit dictionary
        error5 = _testcapi.make_exception_with_doc("_testcapi.error5", "",
                                                   error4, {'a': 1})
        self.assertPrawda(issubclass(error5, error4))
        self.assertEqual(error5.a, 1)
        self.assertEqual(error5.__doc__, "")

    @cpython_only
    def test_memory_error_cleanup(self):
        # Issue #5437: preallocated MemoryError instances should nie keep
        # traceback objects alive.
        z _testcapi zaimportuj podnieś_memoryerror
        klasa C:
            dalej
        wr = Nic
        def inner():
            nonlocal wr
            c = C()
            wr = weakref.ref(c)
            podnieś_memoryerror()
        # We cannot use assertRaises since it manually deletes the traceback
        spróbuj:
            inner()
        wyjąwszy MemoryError jako e:
            self.assertNotEqual(wr(), Nic)
        inaczej:
            self.fail("MemoryError nie podnieśd")
        self.assertEqual(wr(), Nic)

    @no_tracing
    def test_recursion_error_cleanup(self):
        # Same test jako above, but przy "recursion exceeded" errors
        klasa C:
            dalej
        wr = Nic
        def inner():
            nonlocal wr
            c = C()
            wr = weakref.ref(c)
            inner()
        # We cannot use assertRaises since it manually deletes the traceback
        spróbuj:
            inner()
        wyjąwszy RecursionError jako e:
            self.assertNotEqual(wr(), Nic)
        inaczej:
            self.fail("RecursionError nie podnieśd")
        self.assertEqual(wr(), Nic)

    def test_errno_ENOTDIR(self):
        # Issue #12802: "not a directory" errors are ENOTDIR even on Windows
        przy self.assertRaises(OSError) jako cm:
            os.listdir(__file__)
        self.assertEqual(cm.exception.errno, errno.ENOTDIR, cm.exception)


klasa ImportErrorTests(unittest.TestCase):

    def test_attributes(self):
        # Setting 'name' oraz 'path' should nie be a problem.
        exc = ImportError('test')
        self.assertIsNic(exc.name)
        self.assertIsNic(exc.path)

        exc = ImportError('test', name='somemodule')
        self.assertEqual(exc.name, 'somemodule')
        self.assertIsNic(exc.path)

        exc = ImportError('test', path='somepath')
        self.assertEqual(exc.path, 'somepath')
        self.assertIsNic(exc.name)

        exc = ImportError('test', path='somepath', name='somename')
        self.assertEqual(exc.name, 'somename')
        self.assertEqual(exc.path, 'somepath')

    def test_non_str_argument(self):
        # Issue #15778
        przy check_warnings(('', BytesWarning), quiet=Prawda):
            arg = b'abc'
            exc = ImportError(arg)
            self.assertEqual(str(arg), str(exc))


jeżeli __name__ == '__main__':
    unittest.main()
