# Run the _testcapi module tests (tests dla the Python/C API):  by defn,
# these are all functions _testcapi exports whose name begins przy 'test_'.

zaimportuj os
zaimportuj pickle
zaimportuj random
zaimportuj subprocess
zaimportuj sys
zaimportuj textwrap
zaimportuj time
zaimportuj unittest
z test zaimportuj support
z test.support zaimportuj MISSING_C_DOCSTRINGS
z test.support.script_helper zaimportuj assert_python_failure
spróbuj:
    zaimportuj _posixsubprocess
wyjąwszy ImportError:
    _posixsubprocess = Nic
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic
# Skip this test jeżeli the _testcapi module isn't available.
_testcapi = support.import_module('_testcapi')

# Were we compiled --with-pydebug albo przy #define Py_DEBUG?
Py_DEBUG = hasattr(sys, 'gettotalrefcount')


def testfunction(self):
    """some doc"""
    zwróć self

klasa InstanceMethod:
    id = _testcapi.instancemethod(id)
    testfunction = _testcapi.instancemethod(testfunction)

klasa CAPITest(unittest.TestCase):

    def test_instancemethod(self):
        inst = InstanceMethod()
        self.assertEqual(id(inst), inst.id())
        self.assertPrawda(inst.testfunction() jest inst)
        self.assertEqual(inst.testfunction.__doc__, testfunction.__doc__)
        self.assertEqual(InstanceMethod.testfunction.__doc__, testfunction.__doc__)

        InstanceMethod.testfunction.attribute = "test"
        self.assertEqual(testfunction.attribute, "test")
        self.assertRaises(AttributeError, setattr, inst.testfunction, "attribute", "test")

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def test_no_FatalError_infinite_loop(self):
        przy support.SuppressCrashReport():
            p = subprocess.Popen([sys.executable, "-c",
                                  'zaimportuj _testcapi;'
                                  '_testcapi.crash_no_current_thread()'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        (out, err) = p.communicate()
        self.assertEqual(out, b'')
        # This used to cause an infinite loop.
        self.assertPrawda(err.rstrip().startswith(
                         b'Fatal Python error:'
                         b' PyThreadState_Get: no current thread'))

    def test_memoryview_from_NULL_pointer(self):
        self.assertRaises(ValueError, _testcapi.make_memoryview_from_NULL_pointer)

    def test_exc_info(self):
        podnieśd_exception = ValueError("5")
        new_exc = TypeError("TEST")
        spróbuj:
            podnieś podnieśd_exception
        wyjąwszy ValueError jako e:
            tb = e.__traceback__
            orig_sys_exc_info = sys.exc_info()
            orig_exc_info = _testcapi.set_exc_info(new_exc.__class__, new_exc, Nic)
            new_sys_exc_info = sys.exc_info()
            new_exc_info = _testcapi.set_exc_info(*orig_exc_info)
            reset_sys_exc_info = sys.exc_info()

            self.assertEqual(orig_exc_info[1], e)

            self.assertSequenceEqual(orig_exc_info, (raised_exception.__class__, podnieśd_exception, tb))
            self.assertSequenceEqual(orig_sys_exc_info, orig_exc_info)
            self.assertSequenceEqual(reset_sys_exc_info, orig_exc_info)
            self.assertSequenceEqual(new_exc_info, (new_exc.__class__, new_exc, Nic))
            self.assertSequenceEqual(new_sys_exc_info, new_exc_info)
        inaczej:
            self.assertPrawda(Nieprawda)

    @unittest.skipUnless(_posixsubprocess, '_posixsubprocess required dla this test.')
    def test_seq_bytes_to_charp_array(self):
        # Issue #15732: crash w _PySequence_BytesToCharpArray()
        klasa Z(object):
            def __len__(self):
                zwróć 1
        self.assertRaises(TypeError, _posixsubprocess.fork_exec,
                          1,Z(),3,[1, 2],5,6,7,8,9,10,11,12,13,14,15,16,17)
        # Issue #15736: overflow w _PySequence_BytesToCharpArray()
        klasa Z(object):
            def __len__(self):
                zwróć sys.maxsize
            def __getitem__(self, i):
                zwróć b'x'
        self.assertRaises(MemoryError, _posixsubprocess.fork_exec,
                          1,Z(),3,[1, 2],5,6,7,8,9,10,11,12,13,14,15,16,17)

    @unittest.skipUnless(_posixsubprocess, '_posixsubprocess required dla this test.')
    def test_subprocess_fork_exec(self):
        klasa Z(object):
            def __len__(self):
                zwróć 1

        # Issue #15738: crash w subprocess_fork_exec()
        self.assertRaises(TypeError, _posixsubprocess.fork_exec,
                          Z(),[b'1'],3,[1, 2],5,6,7,8,9,10,11,12,13,14,15,16,17)

    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information dla builtins requires docstrings")
    def test_docstring_signature_parsing(self):

        self.assertEqual(_testcapi.no_docstring.__doc__, Nic)
        self.assertEqual(_testcapi.no_docstring.__text_signature__, Nic)

        self.assertEqual(_testcapi.docstring_empty.__doc__, Nic)
        self.assertEqual(_testcapi.docstring_empty.__text_signature__, Nic)

        self.assertEqual(_testcapi.docstring_no_signature.__doc__,
            "This docstring has no signature.")
        self.assertEqual(_testcapi.docstring_no_signature.__text_signature__, Nic)

        self.assertEqual(_testcapi.docstring_with_invalid_signature.__doc__,
            "docstring_with_invalid_signature($module, /, boo)\n"
            "\n"
            "This docstring has an invalid signature."
            )
        self.assertEqual(_testcapi.docstring_with_invalid_signature.__text_signature__, Nic)

        self.assertEqual(_testcapi.docstring_with_invalid_signature2.__doc__,
            "docstring_with_invalid_signature2($module, /, boo)\n"
            "\n"
            "--\n"
            "\n"
            "This docstring also has an invalid signature."
            )
        self.assertEqual(_testcapi.docstring_with_invalid_signature2.__text_signature__, Nic)

        self.assertEqual(_testcapi.docstring_with_signature.__doc__,
            "This docstring has a valid signature.")
        self.assertEqual(_testcapi.docstring_with_signature.__text_signature__, "($module, /, sig)")

        self.assertEqual(_testcapi.docstring_with_signature_but_no_doc.__doc__, Nic)
        self.assertEqual(_testcapi.docstring_with_signature_but_no_doc.__text_signature__,
            "($module, /, sig)")

        self.assertEqual(_testcapi.docstring_with_signature_and_extra_newlines.__doc__,
            "\nThis docstring has a valid signature oraz some extra newlines.")
        self.assertEqual(_testcapi.docstring_with_signature_and_extra_newlines.__text_signature__,
            "($module, /, parameter)")

    def test_c_type_with_matrix_multiplication(self):
        M = _testcapi.matmulType
        m1 = M()
        m2 = M()
        self.assertEqual(m1 @ m2, ("matmul", m1, m2))
        self.assertEqual(m1 @ 42, ("matmul", m1, 42))
        self.assertEqual(42 @ m1, ("matmul", 42, m1))
        o = m1
        o @= m2
        self.assertEqual(o, ("imatmul", m1, m2))
        o = m1
        o @= 42
        self.assertEqual(o, ("imatmul", m1, 42))
        o = 42
        o @= m1
        self.assertEqual(o, ("matmul", 42, m1))

    def test_return_null_without_error(self):
        # Issue #23571: A function must nie zwróć NULL without setting an
        # error
        jeżeli Py_DEBUG:
            code = textwrap.dedent("""
                zaimportuj _testcapi
                z test zaimportuj support

                przy support.SuppressCrashReport():
                    _testcapi.return_null_without_error()
            """)
            rc, out, err = assert_python_failure('-c', code)
            self.assertRegex(err.replace(b'\r', b''),
                             br'Fatal Python error: a function returned NULL '
                                br'without setting an error\n'
                             br'SystemError: <built-in function '
                                 br'return_null_without_error> returned NULL '
                                 br'without setting an error\n'
                             br'\n'
                             br'Current thread.*:\n'
                             br'  File .*", line 6 w <module>')
        inaczej:
            przy self.assertRaises(SystemError) jako cm:
                _testcapi.return_null_without_error()
            self.assertRegex(str(cm.exception),
                             'return_null_without_error.* '
                             'returned NULL without setting an error')

    def test_return_result_with_error(self):
        # Issue #23571: A function must nie zwróć a result przy an error set
        jeżeli Py_DEBUG:
            code = textwrap.dedent("""
                zaimportuj _testcapi
                z test zaimportuj support

                przy support.SuppressCrashReport():
                    _testcapi.return_result_with_error()
            """)
            rc, out, err = assert_python_failure('-c', code)
            self.assertRegex(err.replace(b'\r', b''),
                             br'Fatal Python error: a function returned a '
                                br'result przy an error set\n'
                             br'ValueError\n'
                             br'\n'
                             br'During handling of the above exception, '
                                br'another exception occurred:\n'
                             br'\n'
                             br'SystemError: <built-in '
                                br'function return_result_with_error> '
                                br'returned a result przy an error set\n'
                             br'\n'
                             br'Current thread.*:\n'
                             br'  File .*, line 6 w <module>')
        inaczej:
            przy self.assertRaises(SystemError) jako cm:
                _testcapi.return_result_with_error()
            self.assertRegex(str(cm.exception),
                             'return_result_with_error.* '
                             'returned a result przy an error set')


@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa TestPendingCalls(unittest.TestCase):

    def pendingcalls_submit(self, l, n):
        def callback():
            #this function can be interrupted by thread switching so let's
            #use an atomic operation
            l.append(Nic)

        dla i w range(n):
            time.sleep(random.random()*0.02) #0.01 secs on average
            #try submitting callback until successful.
            #rely on regular interrupt to flush queue jeżeli we are
            #unsuccessful.
            dopóki Prawda:
                jeżeli _testcapi._pending_threadfunc(callback):
                    przerwij;

    def pendingcalls_wait(self, l, n, context = Nic):
        #now, stick around until l[0] has grown to 10
        count = 0;
        dopóki len(l) != n:
            #this busy loop jest where we expect to be interrupted to
            #run our callbacks.  Note that callbacks are only run on the
            #main thread
            jeżeli Nieprawda oraz support.verbose:
                print("(%i)"%(len(l),),)
            dla i w range(1000):
                a = i*i
            jeżeli context oraz nie context.event.is_set():
                kontynuuj
            count += 1
            self.assertPrawda(count < 10000,
                "timeout waiting dla %i callbacks, got %i"%(n, len(l)))
        jeżeli Nieprawda oraz support.verbose:
            print("(%i)"%(len(l),))

    def test_pendingcalls_threaded(self):

        #do every callback on a separate thread
        n = 32 #total callbacks
        threads = []
        klasa foo(object):pass
        context = foo()
        context.l = []
        context.n = 2 #submits per thread
        context.nThreads = n // context.n
        context.nFinished = 0
        context.lock = threading.Lock()
        context.event = threading.Event()

        threads = [threading.Thread(target=self.pendingcalls_thread,
                                    args=(context,))
                   dla i w range(context.nThreads)]
        przy support.start_threads(threads):
            self.pendingcalls_wait(context.l, n, context)

    def pendingcalls_thread(self, context):
        spróbuj:
            self.pendingcalls_submit(context.l, context.n)
        w_końcu:
            przy context.lock:
                context.nFinished += 1
                nFinished = context.nFinished
                jeżeli Nieprawda oraz support.verbose:
                    print("finished threads: ", nFinished)
            jeżeli nFinished == context.nThreads:
                context.event.set()

    def test_pendingcalls_non_threaded(self):
        #again, just using the main thread, likely they will all be dispatched at
        #once.  It jest ok to ask dla too many, because we loop until we find a slot.
        #the loop can be interrupted to dispatch.
        #there are only 32 dispatch slots, so we go dla twice that!
        l = []
        n = 64
        self.pendingcalls_submit(l, n)
        self.pendingcalls_wait(l, n)


klasa SubinterpreterTest(unittest.TestCase):

    def test_subinterps(self):
        zaimportuj builtins
        r, w = os.pipe()
        code = """jeżeli 1:
            zaimportuj sys, builtins, pickle
            przy open({:d}, "wb") jako f:
                pickle.dump(id(sys.modules), f)
                pickle.dump(id(builtins), f)
            """.format(w)
        przy open(r, "rb") jako f:
            ret = support.run_in_subinterp(code)
            self.assertEqual(ret, 0)
            self.assertNotEqual(pickle.load(f), id(sys.modules))
            self.assertNotEqual(pickle.load(f), id(builtins))


# Bug #6012
klasa Test6012(unittest.TestCase):
    def test(self):
        self.assertEqual(_testcapi.argparsing("Hello", "World"), 1)


klasa EmbeddingTests(unittest.TestCase):
    def setUp(self):
        basepath = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        exename = "_testembed"
        jeżeli sys.platform.startswith("win"):
            ext = ("_d" jeżeli "_d" w sys.executable inaczej "") + ".exe"
            exename += ext
            exepath = os.path.dirname(sys.executable)
        inaczej:
            exepath = os.path.join(basepath, "Programs")
        self.test_exe = exe = os.path.join(exepath, exename)
        jeżeli nie os.path.exists(exe):
            self.skipTest("%r doesn't exist" % exe)
        # This jest needed otherwise we get a fatal error:
        # "Py_Initialize: Unable to get the locale encoding
        # LookupError: no codec search functions registered: can't find encoding"
        self.oldcwd = os.getcwd()
        os.chdir(basepath)

    def tearDown(self):
        os.chdir(self.oldcwd)

    def run_embedded_interpreter(self, *args):
        """Runs a test w the embedded interpreter"""
        cmd = [self.test_exe]
        cmd.extend(args)
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=Prawda)
        (out, err) = p.communicate()
        self.assertEqual(p.returncode, 0,
                         "bad returncode %d, stderr jest %r" %
                         (p.returncode, err))
        zwróć out, err

    def test_subinterps(self):
        # This jest just a "don't crash" test
        out, err = self.run_embedded_interpreter()
        jeżeli support.verbose:
            print()
            print(out)
            print(err)

    @staticmethod
    def _get_default_pipe_encoding():
        rp, wp = os.pipe()
        spróbuj:
            przy os.fdopen(wp, 'w') jako w:
                default_pipe_encoding = w.encoding
        w_końcu:
            os.close(rp)
        zwróć default_pipe_encoding

    def test_forced_io_encoding(self):
        # Checks forced configuration of embedded interpreter IO streams
        out, err = self.run_embedded_interpreter("forced_io_encoding")
        jeżeli support.verbose:
            print()
            print(out)
            print(err)
        expected_errors = sys.__stdout__.errors
        expected_stdin_encoding = sys.__stdin__.encoding
        expected_pipe_encoding = self._get_default_pipe_encoding()
        expected_output = '\n'.join([
        "--- Use defaults ---",
        "Expected encoding: default",
        "Expected errors: default",
        "stdin: {in_encoding}:{errors}",
        "stdout: {out_encoding}:{errors}",
        "stderr: {out_encoding}:backslashreplace",
        "--- Set errors only ---",
        "Expected encoding: default",
        "Expected errors: ignore",
        "stdin: {in_encoding}:ignore",
        "stdout: {out_encoding}:ignore",
        "stderr: {out_encoding}:backslashreplace",
        "--- Set encoding only ---",
        "Expected encoding: latin-1",
        "Expected errors: default",
        "stdin: latin-1:{errors}",
        "stdout: latin-1:{errors}",
        "stderr: latin-1:backslashreplace",
        "--- Set encoding oraz errors ---",
        "Expected encoding: latin-1",
        "Expected errors: replace",
        "stdin: latin-1:replace",
        "stdout: latin-1:replace",
        "stderr: latin-1:backslashreplace"])
        expected_output = expected_output.format(
                                in_encoding=expected_stdin_encoding,
                                out_encoding=expected_pipe_encoding,
                                errors=expected_errors)
        # This jest useful jeżeli we ever trip over odd platform behaviour
        self.maxDiff = Nic
        self.assertEqual(out.strip(), expected_output)

klasa SkipitemTest(unittest.TestCase):

    def test_skipitem(self):
        """
        If this test failed, you probably added a new "format unit"
        w Python/getargs.c, but neglected to update our poor friend
        skipitem() w the same file.  (If so, shame on you!)

        With a few exceptions**, this function brute-force tests all
        printable ASCII*** characters (32 to 126 inclusive) jako format units,
        checking to see that PyArg_ParseTupleAndKeywords() zwróć consistent
        errors both when the unit jest attempted to be used oraz when it jest
        skipped.  If the format unit doesn't exist, we'll get one of two
        specific error messages (one dla used, one dla skipped); jeżeli it does
        exist we *won't* get that error--we'll get either no error albo some
        other error.  If we get the specific "does nie exist" error dla one
        test oraz nie dla the other, there's a mismatch, oraz the test fails.

           ** Some format units have special funny semantics oraz it would
              be difficult to accomodate them here.  Since these are all
              well-established oraz properly skipped w skipitem() we can
              get away przy nie testing them--this test jest really intended
              to catch *new* format units.

          *** Python C source files must be ASCII.  Therefore it's impossible
              to have non-ASCII format units.

        """
        empty_tuple = ()
        tuple_1 = (0,)
        dict_b = {'b':1}
        keywords = ["a", "b"]

        dla i w range(32, 127):
            c = chr(i)

            # skip parentheses, the error reporting jest inconsistent about them
            # skip 'e', it's always a two-character code
            # skip '|' oraz '$', they don't represent arguments anyway
            jeżeli c w '()e|$':
                kontynuuj

            # test the format unit when nie skipped
            format = c + "i"
            spróbuj:
                # (niee: the format string must be bytes!)
                _testcapi.parse_tuple_and_keywords(tuple_1, dict_b,
                    format.encode("ascii"), keywords)
                when_not_skipped = Nieprawda
            wyjąwszy TypeError jako e:
                s = "argument 1 must be impossible<bad format char>, nie int"
                when_not_skipped = (str(e) == s)
            wyjąwszy RuntimeError jako e:
                when_not_skipped = Nieprawda

            # test the format unit when skipped
            optional_format = "|" + format
            spróbuj:
                _testcapi.parse_tuple_and_keywords(empty_tuple, dict_b,
                    optional_format.encode("ascii"), keywords)
                when_skipped = Nieprawda
            wyjąwszy RuntimeError jako e:
                s = "impossible<bad format char>: '{}'".format(format)
                when_skipped = (str(e) == s)

            message = ("test_skipitem_parity: "
                "detected mismatch between convertsimple oraz skipitem "
                "dla format unit '{}' ({}), nie skipped {}, skipped {}".format(
                    c, i, when_skipped, when_not_skipped))
            self.assertIs(when_skipped, when_not_skipped, message)

    def test_parse_tuple_and_keywords(self):
        # parse_tuple_and_keywords error handling tests
        self.assertRaises(TypeError, _testcapi.parse_tuple_and_keywords,
                          (), {}, 42, [])
        self.assertRaises(ValueError, _testcapi.parse_tuple_and_keywords,
                          (), {}, b'', 42)
        self.assertRaises(ValueError, _testcapi.parse_tuple_and_keywords,
                          (), {}, b'', [''] * 42)
        self.assertRaises(ValueError, _testcapi.parse_tuple_and_keywords,
                          (), {}, b'', [42])

@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa TestThreadState(unittest.TestCase):

    @support.reap_threads
    def test_thread_state(self):
        # some extra thread-state tests driven via _testcapi
        def target():
            idents = []

            def callback():
                idents.append(threading.get_ident())

            _testcapi._test_thread_state(callback)
            a = b = callback
            time.sleep(1)
            # Check our main thread jest w the list exactly 3 times.
            self.assertEqual(idents.count(threading.get_ident()), 3,
                             "Couldn't find main thread correctly w the list")

        target()
        t = threading.Thread(target=target)
        t.start()
        t.join()

klasa Test_testcapi(unittest.TestCase):
    def test__testcapi(self):
        dla name w dir(_testcapi):
            jeżeli name.startswith('test_'):
                przy self.subTest("internal", name=name):
                    test = getattr(_testcapi, name)
                    test()

jeżeli __name__ == "__main__":
    unittest.main()
