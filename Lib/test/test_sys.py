zaimportuj unittest, test.support
z test.support.script_helper zaimportuj assert_python_ok, assert_python_failure
zaimportuj sys, io, os
zaimportuj struct
zaimportuj subprocess
zaimportuj textwrap
zaimportuj warnings
zaimportuj operator
zaimportuj codecs
zaimportuj gc
zaimportuj sysconfig
zaimportuj platform

# count the number of test runs, used to create unique
# strings to intern w test_intern()
numruns = 0

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

klasa SysModuleTest(unittest.TestCase):

    def setUp(self):
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        self.orig_displayhook = sys.displayhook

    def tearDown(self):
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr
        sys.displayhook = self.orig_displayhook
        test.support.reap_children()

    def test_original_displayhook(self):
        zaimportuj builtins
        out = io.StringIO()
        sys.stdout = out

        dh = sys.__displayhook__

        self.assertRaises(TypeError, dh)
        jeżeli hasattr(builtins, "_"):
            usuń builtins._

        dh(Nic)
        self.assertEqual(out.getvalue(), "")
        self.assertPrawda(nie hasattr(builtins, "_"))
        dh(42)
        self.assertEqual(out.getvalue(), "42\n")
        self.assertEqual(builtins._, 42)

        usuń sys.stdout
        self.assertRaises(RuntimeError, dh, 42)

    def test_lost_displayhook(self):
        usuń sys.displayhook
        code = compile("42", "<string>", "single")
        self.assertRaises(RuntimeError, eval, code)

    def test_custom_displayhook(self):
        def baddisplayhook(obj):
            podnieś ValueError
        sys.displayhook = baddisplayhook
        code = compile("42", "<string>", "single")
        self.assertRaises(ValueError, eval, code)

    def test_original_excepthook(self):
        err = io.StringIO()
        sys.stderr = err

        eh = sys.__excepthook__

        self.assertRaises(TypeError, eh)
        spróbuj:
            podnieś ValueError(42)
        wyjąwszy ValueError jako exc:
            eh(*sys.exc_info())

        self.assertPrawda(err.getvalue().endswith("ValueError: 42\n"))

    def test_excepthook(self):
        przy test.support.captured_output("stderr") jako stderr:
            sys.excepthook(1, '1', 1)
        self.assertPrawda("TypeError: print_exception(): Exception expected dla " \
                         "value, str found" w stderr.getvalue())

    # FIXME: testing the code dla a lost albo replaced excepthook w
    # Python/pythonrun.c::PyErr_PrintEx() jest tricky.

    def test_exit(self):
        # call przy two arguments
        self.assertRaises(TypeError, sys.exit, 42, 42)

        # call without argument
        przy self.assertRaises(SystemExit) jako cm:
            sys.exit()
        self.assertIsNic(cm.exception.code)

        rc, out, err = assert_python_ok('-c', 'zaimportuj sys; sys.exit()')
        self.assertEqual(rc, 0)
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

        # call przy integer argument
        przy self.assertRaises(SystemExit) jako cm:
            sys.exit(42)
        self.assertEqual(cm.exception.code, 42)

        # call przy tuple argument przy one entry
        # entry will be unpacked
        przy self.assertRaises(SystemExit) jako cm:
            sys.exit((42,))
        self.assertEqual(cm.exception.code, 42)

        # call przy string argument
        przy self.assertRaises(SystemExit) jako cm:
            sys.exit("exit")
        self.assertEqual(cm.exception.code, "exit")

        # call przy tuple argument przy two entries
        przy self.assertRaises(SystemExit) jako cm:
            sys.exit((17, 23))
        self.assertEqual(cm.exception.code, (17, 23))

        # test that the exit machinery handles SystemExits properly
        rc, out, err = assert_python_failure('-c', 'raise SystemExit(47)')
        self.assertEqual(rc, 47)
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

        def check_exit_message(code, expected, **env_vars):
            rc, out, err = assert_python_failure('-c', code, **env_vars)
            self.assertEqual(rc, 1)
            self.assertEqual(out, b'')
            self.assertPrawda(err.startswith(expected),
                "%s doesn't start przy %s" % (ascii(err), ascii(expected)))

        # test that stderr buffer jest flushed before the exit message jest written
        # into stderr
        check_exit_message(
            r'zaimportuj sys; sys.stderr.write("unflushed,"); sys.exit("message")',
            b"unflushed,message")

        # test that the exit message jest written przy backslashreplace error
        # handler to stderr
        check_exit_message(
            r'zaimportuj sys; sys.exit("surrogates:\uDCFF")',
            b"surrogates:\\udcff")

        # test that the unicode message jest encoded to the stderr encoding
        # instead of the default encoding (utf8)
        check_exit_message(
            r'zaimportuj sys; sys.exit("h\xe9")',
            b"h\xe9", PYTHONIOENCODING='latin-1')

    def test_getdefaultencoding(self):
        self.assertRaises(TypeError, sys.getdefaultencoding, 42)
        # can't check more than the type, jako the user might have changed it
        self.assertIsInstance(sys.getdefaultencoding(), str)

    # testing sys.settrace() jest done w test_sys_settrace.py
    # testing sys.setprofile() jest done w test_sys_setprofile.py

    def test_setcheckinterval(self):
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertRaises(TypeError, sys.setcheckinterval)
            orig = sys.getcheckinterval()
            dla n w 0, 100, 120, orig: # orig last to restore starting state
                sys.setcheckinterval(n)
                self.assertEqual(sys.getcheckinterval(), n)

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    def test_switchinterval(self):
        self.assertRaises(TypeError, sys.setswitchinterval)
        self.assertRaises(TypeError, sys.setswitchinterval, "a")
        self.assertRaises(ValueError, sys.setswitchinterval, -1.0)
        self.assertRaises(ValueError, sys.setswitchinterval, 0.0)
        orig = sys.getswitchinterval()
        # sanity check
        self.assertPrawda(orig < 0.5, orig)
        spróbuj:
            dla n w 0.00001, 0.05, 3.0, orig:
                sys.setswitchinterval(n)
                self.assertAlmostEqual(sys.getswitchinterval(), n)
        w_końcu:
            sys.setswitchinterval(orig)

    def test_recursionlimit(self):
        self.assertRaises(TypeError, sys.getrecursionlimit, 42)
        oldlimit = sys.getrecursionlimit()
        self.assertRaises(TypeError, sys.setrecursionlimit)
        self.assertRaises(ValueError, sys.setrecursionlimit, -42)
        sys.setrecursionlimit(10000)
        self.assertEqual(sys.getrecursionlimit(), 10000)
        sys.setrecursionlimit(oldlimit)

    @unittest.skipIf(hasattr(sys, 'gettrace') oraz sys.gettrace(),
                     'fatal error jeżeli run przy a trace function')
    def test_recursionlimit_recovery(self):
        # NOTE: this test jest slightly fragile w that it depends on the current
        # recursion count when executing the test being low enough so jako to
        # trigger the recursion recovery detection w the _Py_MakeEndRecCheck
        # macro (see ceval.h).
        oldlimit = sys.getrecursionlimit()
        def f():
            f()
        spróbuj:
            dla i w (50, 1000):
                # Issue #5392: stack overflow after hitting recursion limit twice
                sys.setrecursionlimit(i)
                self.assertRaises(RecursionError, f)
                self.assertRaises(RecursionError, f)
        w_końcu:
            sys.setrecursionlimit(oldlimit)

    def test_recursionlimit_fatalerror(self):
        # A fatal error occurs jeżeli a second recursion limit jest hit when recovering
        # z a first one.
        code = textwrap.dedent("""
            zaimportuj sys

            def f():
                spróbuj:
                    f()
                wyjąwszy RecursionError:
                    f()

            sys.setrecursionlimit(%d)
            f()""")
        przy test.support.SuppressCrashReport():
            dla i w (50, 1000):
                sub = subprocess.Popen([sys.executable, '-c', code % i],
                    stderr=subprocess.PIPE)
                err = sub.communicate()[1]
                self.assertPrawda(sub.returncode, sub.returncode)
                self.assertIn(
                    b"Fatal Python error: Cannot recover z stack overflow",
                    err)

    def test_getwindowsversion(self):
        # Raise SkipTest jeżeli sys doesn't have getwindowsversion attribute
        test.support.get_attribute(sys, "getwindowsversion")
        v = sys.getwindowsversion()
        self.assertEqual(len(v), 5)
        self.assertIsInstance(v[0], int)
        self.assertIsInstance(v[1], int)
        self.assertIsInstance(v[2], int)
        self.assertIsInstance(v[3], int)
        self.assertIsInstance(v[4], str)
        self.assertRaises(IndexError, operator.getitem, v, 5)
        self.assertIsInstance(v.major, int)
        self.assertIsInstance(v.minor, int)
        self.assertIsInstance(v.build, int)
        self.assertIsInstance(v.platform, int)
        self.assertIsInstance(v.service_pack, str)
        self.assertIsInstance(v.service_pack_minor, int)
        self.assertIsInstance(v.service_pack_major, int)
        self.assertIsInstance(v.suite_mask, int)
        self.assertIsInstance(v.product_type, int)
        self.assertEqual(v[0], v.major)
        self.assertEqual(v[1], v.minor)
        self.assertEqual(v[2], v.build)
        self.assertEqual(v[3], v.platform)
        self.assertEqual(v[4], v.service_pack)

        # This jest how platform.py calls it. Make sure tuple
        #  still has 5 elements
        maj, min, buildno, plat, csd = sys.getwindowsversion()

    def test_call_tracing(self):
        self.assertRaises(TypeError, sys.call_tracing, type, 2)

    @unittest.skipUnless(hasattr(sys, "setdlopenflags"),
                         'test needs sys.setdlopenflags()')
    def test_dlopenflags(self):
        self.assertPrawda(hasattr(sys, "getdlopenflags"))
        self.assertRaises(TypeError, sys.getdlopenflags, 42)
        oldflags = sys.getdlopenflags()
        self.assertRaises(TypeError, sys.setdlopenflags)
        sys.setdlopenflags(oldflags+1)
        self.assertEqual(sys.getdlopenflags(), oldflags+1)
        sys.setdlopenflags(oldflags)

    @test.support.refcount_test
    def test_refcount(self):
        # n here must be a global w order dla this test to dalej while
        # tracing przy a python function.  Tracing calls PyFrame_FastToLocals
        # which will add a copy of any locals to the frame object, causing
        # the reference count to increase by 2 instead of 1.
        global n
        self.assertRaises(TypeError, sys.getrefcount)
        c = sys.getrefcount(Nic)
        n = Nic
        self.assertEqual(sys.getrefcount(Nic), c+1)
        usuń n
        self.assertEqual(sys.getrefcount(Nic), c)
        jeżeli hasattr(sys, "gettotalrefcount"):
            self.assertIsInstance(sys.gettotalrefcount(), int)

    def test_getframe(self):
        self.assertRaises(TypeError, sys._getframe, 42, 42)
        self.assertRaises(ValueError, sys._getframe, 2000000000)
        self.assertPrawda(
            SysModuleTest.test_getframe.__code__ \
            jest sys._getframe().f_code
        )

    # sys._current_frames() jest a CPython-only gimmick.
    def test_current_frames(self):
        have_threads = Prawda
        spróbuj:
            zaimportuj _thread
        wyjąwszy ImportError:
            have_threads = Nieprawda

        jeżeli have_threads:
            self.current_frames_with_threads()
        inaczej:
            self.current_frames_without_threads()

    # Test sys._current_frames() w a WITH_THREADS build.
    @test.support.reap_threads
    def current_frames_with_threads(self):
        zaimportuj threading
        zaimportuj traceback

        # Spawn a thread that blocks at a known place.  Then the main
        # thread does sys._current_frames(), oraz verifies that the frames
        # returned make sense.
        entered_g = threading.Event()
        leave_g = threading.Event()
        thread_info = []  # the thread's id

        def f123():
            g456()

        def g456():
            thread_info.append(threading.get_ident())
            entered_g.set()
            leave_g.wait()

        t = threading.Thread(target=f123)
        t.start()
        entered_g.wait()

        # At this point, t has finished its entered_g.set(), although it's
        # impossible to guess whether it's still on that line albo has moved on
        # to its leave_g.wait().
        self.assertEqual(len(thread_info), 1)
        thread_id = thread_info[0]

        d = sys._current_frames()

        main_id = threading.get_ident()
        self.assertIn(main_id, d)
        self.assertIn(thread_id, d)

        # Verify that the captured main-thread frame jest _this_ frame.
        frame = d.pop(main_id)
        self.assertPrawda(frame jest sys._getframe())

        # Verify that the captured thread frame jest blocked w g456, called
        # z f123.  This jest a litte tricky, since various bits of
        # threading.py are also w the thread's call stack.
        frame = d.pop(thread_id)
        stack = traceback.extract_stack(frame)
        dla i, (filename, lineno, funcname, sourceline) w enumerate(stack):
            jeżeli funcname == "f123":
                przerwij
        inaczej:
            self.fail("didn't find f123() on thread's call stack")

        self.assertEqual(sourceline, "g456()")

        # And the next record must be dla g456().
        filename, lineno, funcname, sourceline = stack[i+1]
        self.assertEqual(funcname, "g456")
        self.assertIn(sourceline, ["leave_g.wait()", "entered_g.set()"])

        # Reap the spawned thread.
        leave_g.set()
        t.join()

    # Test sys._current_frames() when thread support doesn't exist.
    def current_frames_without_threads(self):
        # Not much happens here:  there jest only one thread, przy artificial
        # "thread id" 0.
        d = sys._current_frames()
        self.assertEqual(len(d), 1)
        self.assertIn(0, d)
        self.assertPrawda(d[0] jest sys._getframe())

    def test_attributes(self):
        self.assertIsInstance(sys.api_version, int)
        self.assertIsInstance(sys.argv, list)
        self.assertIn(sys.byteorder, ("little", "big"))
        self.assertIsInstance(sys.builtin_module_names, tuple)
        self.assertIsInstance(sys.copyright, str)
        self.assertIsInstance(sys.exec_prefix, str)
        self.assertIsInstance(sys.base_exec_prefix, str)
        self.assertIsInstance(sys.executable, str)
        self.assertEqual(len(sys.float_info), 11)
        self.assertEqual(sys.float_info.radix, 2)
        self.assertEqual(len(sys.int_info), 2)
        self.assertPrawda(sys.int_info.bits_per_digit % 5 == 0)
        self.assertPrawda(sys.int_info.sizeof_digit >= 1)
        self.assertEqual(type(sys.int_info.bits_per_digit), int)
        self.assertEqual(type(sys.int_info.sizeof_digit), int)
        self.assertIsInstance(sys.hexversion, int)

        self.assertEqual(len(sys.hash_info), 9)
        self.assertLess(sys.hash_info.modulus, 2**sys.hash_info.width)
        # sys.hash_info.modulus should be a prime; we do a quick
        # probable primality test (doesn't exclude the possibility of
        # a Carmichael number)
        dla x w range(1, 100):
            self.assertEqual(
                pow(x, sys.hash_info.modulus-1, sys.hash_info.modulus),
                1,
                "sys.hash_info.modulus {} jest a non-prime".format(
                    sys.hash_info.modulus)
                )
        self.assertIsInstance(sys.hash_info.inf, int)
        self.assertIsInstance(sys.hash_info.nan, int)
        self.assertIsInstance(sys.hash_info.imag, int)
        algo = sysconfig.get_config_var("Py_HASH_ALGORITHM")
        jeżeli sys.hash_info.algorithm w {"fnv", "siphash24"}:
            self.assertIn(sys.hash_info.hash_bits, {32, 64})
            self.assertIn(sys.hash_info.seed_bits, {32, 64, 128})

            jeżeli algo == 1:
                self.assertEqual(sys.hash_info.algorithm, "siphash24")
            albo_inaczej algo == 2:
                self.assertEqual(sys.hash_info.algorithm, "fnv")
            inaczej:
                self.assertIn(sys.hash_info.algorithm, {"fnv", "siphash24"})
        inaczej:
            # PY_HASH_EXTERNAL
            self.assertEqual(algo, 0)
        self.assertGreaterEqual(sys.hash_info.cutoff, 0)
        self.assertLess(sys.hash_info.cutoff, 8)

        self.assertIsInstance(sys.maxsize, int)
        self.assertIsInstance(sys.maxunicode, int)
        self.assertEqual(sys.maxunicode, 0x10FFFF)
        self.assertIsInstance(sys.platform, str)
        self.assertIsInstance(sys.prefix, str)
        self.assertIsInstance(sys.base_prefix, str)
        self.assertIsInstance(sys.version, str)
        vi = sys.version_info
        self.assertIsInstance(vi[:], tuple)
        self.assertEqual(len(vi), 5)
        self.assertIsInstance(vi[0], int)
        self.assertIsInstance(vi[1], int)
        self.assertIsInstance(vi[2], int)
        self.assertIn(vi[3], ("alpha", "beta", "candidate", "final"))
        self.assertIsInstance(vi[4], int)
        self.assertIsInstance(vi.major, int)
        self.assertIsInstance(vi.minor, int)
        self.assertIsInstance(vi.micro, int)
        self.assertIn(vi.releaselevel, ("alpha", "beta", "candidate", "final"))
        self.assertIsInstance(vi.serial, int)
        self.assertEqual(vi[0], vi.major)
        self.assertEqual(vi[1], vi.minor)
        self.assertEqual(vi[2], vi.micro)
        self.assertEqual(vi[3], vi.releaselevel)
        self.assertEqual(vi[4], vi.serial)
        self.assertPrawda(vi > (1,0,0))
        self.assertIsInstance(sys.float_repr_style, str)
        self.assertIn(sys.float_repr_style, ('short', 'legacy'))
        jeżeli nie sys.platform.startswith('win'):
            self.assertIsInstance(sys.abiflags, str)

    @unittest.skipUnless(hasattr(sys, 'thread_info'),
                         'Threading required dla this test.')
    def test_thread_info(self):
        info = sys.thread_info
        self.assertEqual(len(info), 3)
        self.assertIn(info.name, ('nt', 'pthread', 'solaris', Nic))
        self.assertIn(info.lock, ('semaphore', 'mutex+cond', Nic))

    def test_43581(self):
        # Can't use sys.stdout, jako this jest a StringIO object when
        # the test runs under regrtest.
        self.assertEqual(sys.__stdout__.encoding, sys.__stderr__.encoding)

    def test_intern(self):
        global numruns
        numruns += 1
        self.assertRaises(TypeError, sys.intern)
        s = "never interned before" + str(numruns)
        self.assertPrawda(sys.intern(s) jest s)
        s2 = s.swapcase().swapcase()
        self.assertPrawda(sys.intern(s2) jest s)

        # Subclasses of string can't be interned, because they
        # provide too much opportunity dla insane things to happen.
        # We don't want them w the interned dict oraz jeżeli they aren't
        # actually interned, we don't want to create the appearance
        # that they are by allowing intern() to succeed.
        klasa S(str):
            def __hash__(self):
                zwróć 123

        self.assertRaises(TypeError, sys.intern, S("abc"))

    def test_sys_flags(self):
        self.assertPrawda(sys.flags)
        attrs = ("debug",
                 "inspect", "interactive", "optimize", "dont_write_bytecode",
                 "no_user_site", "no_site", "ignore_environment", "verbose",
                 "bytes_warning", "quiet", "hash_randomization", "isolated")
        dla attr w attrs:
            self.assertPrawda(hasattr(sys.flags, attr), attr)
            self.assertEqual(type(getattr(sys.flags, attr)), int, attr)
        self.assertPrawda(repr(sys.flags))
        self.assertEqual(len(sys.flags), len(attrs))

    def assert_raise_on_new_sys_type(self, sys_attr):
        # Users are intentionally prevented z creating new instances of
        # sys.flags, sys.version_info, oraz sys.getwindowsversion.
        attr_type = type(sys_attr)
        przy self.assertRaises(TypeError):
            attr_type()
        przy self.assertRaises(TypeError):
            attr_type.__new__(attr_type)

    def test_sys_flags_no_instantiation(self):
        self.assert_raise_on_new_sys_type(sys.flags)

    def test_sys_version_info_no_instantiation(self):
        self.assert_raise_on_new_sys_type(sys.version_info)

    def test_sys_getwindowsversion_no_instantiation(self):
        # Skip jeżeli nie being run on Windows.
        test.support.get_attribute(sys, "getwindowsversion")
        self.assert_raise_on_new_sys_type(sys.getwindowsversion())

    @test.support.cpython_only
    def test_clear_type_cache(self):
        sys._clear_type_cache()

    def test_ioencoding(self):
        env = dict(os.environ)

        # Test character: cent sign, encoded jako 0x4A (ASCII J) w CP424,
        # nie representable w ASCII.

        env["PYTHONIOENCODING"] = "cp424"
        p = subprocess.Popen([sys.executable, "-c", 'print(chr(0xa2))'],
                             stdout = subprocess.PIPE, env=env)
        out = p.communicate()[0].strip()
        expected = ("\xa2" + os.linesep).encode("cp424")
        self.assertEqual(out, expected)

        env["PYTHONIOENCODING"] = "ascii:replace"
        p = subprocess.Popen([sys.executable, "-c", 'print(chr(0xa2))'],
                             stdout = subprocess.PIPE, env=env)
        out = p.communicate()[0].strip()
        self.assertEqual(out, b'?')

        env["PYTHONIOENCODING"] = "ascii"
        p = subprocess.Popen([sys.executable, "-c", 'print(chr(0xa2))'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        self.assertEqual(out, b'')
        self.assertIn(b'UnicodeEncodeError:', err)
        self.assertIn(rb"'\xa2'", err)

        env["PYTHONIOENCODING"] = "ascii:"
        p = subprocess.Popen([sys.executable, "-c", 'print(chr(0xa2))'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        self.assertEqual(out, b'')
        self.assertIn(b'UnicodeEncodeError:', err)
        self.assertIn(rb"'\xa2'", err)

        env["PYTHONIOENCODING"] = ":surrogateescape"
        p = subprocess.Popen([sys.executable, "-c", 'print(chr(0xdcbd))'],
                             stdout=subprocess.PIPE, env=env)
        out = p.communicate()[0].strip()
        self.assertEqual(out, b'\xbd')

    @unittest.skipUnless(test.support.FS_NONASCII,
                         'requires OS support of non-ASCII encodings')
    def test_ioencoding_nonascii(self):
        env = dict(os.environ)

        env["PYTHONIOENCODING"] = ""
        p = subprocess.Popen([sys.executable, "-c",
                                'print(%a)' % test.support.FS_NONASCII],
                                stdout=subprocess.PIPE, env=env)
        out = p.communicate()[0].strip()
        self.assertEqual(out, os.fsencode(test.support.FS_NONASCII))

    @unittest.skipIf(sys.base_prefix != sys.prefix,
                     'Test jest nie venv-compatible')
    def test_executable(self):
        # sys.executable should be absolute
        self.assertEqual(os.path.abspath(sys.executable), sys.executable)

        # Issue #7774: Ensure that sys.executable jest an empty string jeżeli argv[0]
        # has been set to an non existent program name oraz Python jest unable to
        # retrieve the real program name

        # For a normal installation, it should work without 'cwd'
        # argument. For test runs w the build directory, see #7774.
        python_dir = os.path.dirname(os.path.realpath(sys.executable))
        p = subprocess.Popen(
            ["nonexistent", "-c",
             'zaimportuj sys; print(sys.executable.encode("ascii", "backslashreplace"))'],
            executable=sys.executable, stdout=subprocess.PIPE, cwd=python_dir)
        stdout = p.communicate()[0]
        executable = stdout.strip().decode("ASCII")
        p.wait()
        self.assertIn(executable, ["b''", repr(sys.executable.encode("ascii", "backslashreplace"))])

    def check_fsencoding(self, fs_encoding, expected=Nic):
        self.assertIsNotNic(fs_encoding)
        codecs.lookup(fs_encoding)
        jeżeli expected:
            self.assertEqual(fs_encoding, expected)

    def test_getfilesystemencoding(self):
        fs_encoding = sys.getfilesystemencoding()
        jeżeli sys.platform == 'darwin':
            expected = 'utf-8'
        albo_inaczej sys.platform == 'win32':
            expected = 'mbcs'
        inaczej:
            expected = Nic
        self.check_fsencoding(fs_encoding, expected)

    def c_locale_get_error_handler(self, isolated=Nieprawda, encoding=Nic):
        # Force the POSIX locale
        env = os.environ.copy()
        env["LC_ALL"] = "C"
        code = '\n'.join((
            'zaimportuj sys',
            'def dump(name):',
            '    std = getattr(sys, name)',
            '    print("%s: %s" % (name, std.errors))',
            'dump("stdin")',
            'dump("stdout")',
            'dump("stderr")',
        ))
        args = [sys.executable, "-c", code]
        jeżeli isolated:
            args.append("-I")
        albo_inaczej encoding:
            env['PYTHONIOENCODING'] = encoding
        p = subprocess.Popen(args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              env=env,
                              universal_newlines=Prawda)
        stdout, stderr = p.communicate()
        zwróć stdout

    def test_c_locale_surrogateescape(self):
        out = self.c_locale_get_error_handler(isolated=Prawda)
        self.assertEqual(out,
                         'stdin: surrogateescape\n'
                         'stdout: surrogateescape\n'
                         'stderr: backslashreplace\n')

        # replace the default error handler
        out = self.c_locale_get_error_handler(encoding=':strict')
        self.assertEqual(out,
                         'stdin: strict\n'
                         'stdout: strict\n'
                         'stderr: backslashreplace\n')

        # force the encoding
        out = self.c_locale_get_error_handler(encoding='iso8859-1')
        self.assertEqual(out,
                         'stdin: surrogateescape\n'
                         'stdout: surrogateescape\n'
                         'stderr: backslashreplace\n')

    def test_implementation(self):
        # This test applies to all implementations equally.

        levels = {'alpha': 0xA, 'beta': 0xB, 'candidate': 0xC, 'final': 0xF}

        self.assertPrawda(hasattr(sys.implementation, 'name'))
        self.assertPrawda(hasattr(sys.implementation, 'version'))
        self.assertPrawda(hasattr(sys.implementation, 'hexversion'))
        self.assertPrawda(hasattr(sys.implementation, 'cache_tag'))

        version = sys.implementation.version
        self.assertEqual(version[:2], (version.major, version.minor))

        hexversion = (version.major << 24 | version.minor << 16 |
                      version.micro << 8 | levels[version.releaselevel] << 4 |
                      version.serial << 0)
        self.assertEqual(sys.implementation.hexversion, hexversion)

        # PEP 421 requires that .name be lower case.
        self.assertEqual(sys.implementation.name,
                         sys.implementation.name.lower())

    @test.support.cpython_only
    def test_debugmallocstats(self):
        # Test sys._debugmallocstats()
        z test.support.script_helper zaimportuj assert_python_ok
        args = ['-c', 'zaimportuj sys; sys._debugmallocstats()']
        ret, out, err = assert_python_ok(*args)
        self.assertIn(b"free PyDictObjects", err)

        # The function has no parameter
        self.assertRaises(TypeError, sys._debugmallocstats, Prawda)

    @unittest.skipUnless(hasattr(sys, "getallocatedblocks"),
                         "sys.getallocatedblocks unavailable on this build")
    def test_getallocatedblocks(self):
        # Some sanity checks
        with_pymalloc = sysconfig.get_config_var('WITH_PYMALLOC')
        a = sys.getallocatedblocks()
        self.assertIs(type(a), int)
        jeżeli with_pymalloc:
            self.assertGreater(a, 0)
        inaczej:
            # When WITH_PYMALLOC isn't available, we don't know anything
            # about the underlying implementation: the function might
            # zwróć 0 albo something greater.
            self.assertGreaterEqual(a, 0)
        spróbuj:
            # While we could imagine a Python session where the number of
            # multiple buffer objects would exceed the sharing of references,
            # it jest unlikely to happen w a normal test run.
            self.assertLess(a, sys.gettotalrefcount())
        wyjąwszy AttributeError:
            # gettotalrefcount() nie available
            dalej
        gc.collect()
        b = sys.getallocatedblocks()
        self.assertLessEqual(b, a)
        gc.collect()
        c = sys.getallocatedblocks()
        self.assertIn(c, range(b - 50, b + 50))

    def test_is_finalizing(self):
        self.assertIs(sys.is_finalizing(), Nieprawda)
        # Don't use the atexit module because _Py_Finalizing jest only set
        # after calling atexit callbacks
        code = """jeżeli 1:
            zaimportuj sys

            klasa AtExit:
                is_finalizing = sys.is_finalizing
                print = print

                def __del__(self):
                    self.print(self.is_finalizing(), flush=Prawda)

            # Keep a reference w the __main__ module namespace, so the
            # AtExit destructor will be called at Python exit
            ref = AtExit()
        """
        rc, stdout, stderr = assert_python_ok('-c', code)
        self.assertEqual(stdout.rstrip(), b'Prawda')


@test.support.cpython_only
klasa SizeofTest(unittest.TestCase):

    def setUp(self):
        self.P = struct.calcsize('P')
        self.longdigit = sys.int_info.sizeof_digit
        zaimportuj _testcapi
        self.gc_headsize = _testcapi.SIZEOF_PYGC_HEAD
        self.file = open(test.support.TESTFN, 'wb')

    def tearDown(self):
        self.file.close()
        test.support.unlink(test.support.TESTFN)

    check_sizeof = test.support.check_sizeof

    def test_gc_head_size(self):
        # Check that the gc header size jest added to objects tracked by the gc.
        vsize = test.support.calcvobjsize
        gc_header_size = self.gc_headsize
        # bool objects are nie gc tracked
        self.assertEqual(sys.getsizeof(Prawda), vsize('') + self.longdigit)
        # but lists are
        self.assertEqual(sys.getsizeof([]), vsize('Pn') + gc_header_size)

    def test_errors(self):
        klasa BadSizeof:
            def __sizeof__(self):
                podnieś ValueError
        self.assertRaises(ValueError, sys.getsizeof, BadSizeof())

        klasa InvalidSizeof:
            def __sizeof__(self):
                zwróć Nic
        self.assertRaises(TypeError, sys.getsizeof, InvalidSizeof())
        sentinel = ["sentinel"]
        self.assertIs(sys.getsizeof(InvalidSizeof(), sentinel), sentinel)

        klasa FloatSizeof:
            def __sizeof__(self):
                zwróć 4.5
        self.assertRaises(TypeError, sys.getsizeof, FloatSizeof())
        self.assertIs(sys.getsizeof(FloatSizeof(), sentinel), sentinel)

        klasa OverflowSizeof(int):
            def __sizeof__(self):
                zwróć int(self)
        self.assertEqual(sys.getsizeof(OverflowSizeof(sys.maxsize)),
                         sys.maxsize + self.gc_headsize)
        przy self.assertRaises(OverflowError):
            sys.getsizeof(OverflowSizeof(sys.maxsize + 1))
        przy self.assertRaises(ValueError):
            sys.getsizeof(OverflowSizeof(-1))
        przy self.assertRaises((ValueError, OverflowError)):
            sys.getsizeof(OverflowSizeof(-sys.maxsize - 1))

    def test_default(self):
        size = test.support.calcvobjsize
        self.assertEqual(sys.getsizeof(Prawda), size('') + self.longdigit)
        self.assertEqual(sys.getsizeof(Prawda, -1), size('') + self.longdigit)

    def test_objecttypes(self):
        # check all types defined w Objects/
        size = test.support.calcobjsize
        vsize = test.support.calcvobjsize
        check = self.check_sizeof
        # bool
        check(Prawda, vsize('') + self.longdigit)
        # buffer
        # XXX
        # builtin_function_or_method
        check(len, size('4P')) # XXX check layout
        # bytearray
        samples = [b'', b'u'*100000]
        dla sample w samples:
            x = bytearray(sample)
            check(x, vsize('n2Pi') + x.__alloc__())
        # bytearray_iterator
        check(iter(bytearray()), size('nP'))
        # bytes
        check(b'', vsize('n') + 1)
        check(b'x' * 10, vsize('n') + 11)
        # cell
        def get_cell():
            x = 42
            def inner():
                zwróć x
            zwróć inner
        check(get_cell().__closure__[0], size('P'))
        # code
        check(get_cell().__code__, size('5i9Pi3P'))
        check(get_cell.__code__, size('5i9Pi3P'))
        def get_cell2(x):
            def inner():
                zwróć x
            zwróć inner
        check(get_cell2.__code__, size('5i9Pi3P') + 1)
        # complex
        check(complex(0,1), size('2d'))
        # method_descriptor (descriptor object)
        check(str.lower, size('3PP'))
        # classmethod_descriptor (descriptor object)
        # XXX
        # member_descriptor (descriptor object)
        zaimportuj datetime
        check(datetime.timedelta.days, size('3PP'))
        # getset_descriptor (descriptor object)
        zaimportuj collections
        check(collections.defaultdict.default_factory, size('3PP'))
        # wrapper_descriptor (descriptor object)
        check(int.__add__, size('3P2P'))
        # method-wrapper (descriptor object)
        check({}.__iter__, size('2P'))
        # dict
        check({}, size('n2P' + '2nPn' + 8*'n2P'))
        longdict = {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8}
        check(longdict, size('n2P' + '2nPn') + 16*struct.calcsize('n2P'))
        # dictionary-keyiterator
        check({}.keys(), size('P'))
        # dictionary-valueiterator
        check({}.values(), size('P'))
        # dictionary-itemiterator
        check({}.items(), size('P'))
        # dictionary iterator
        check(iter({}), size('P2nPn'))
        # dictproxy
        klasa C(object): dalej
        check(C.__dict__, size('P'))
        # BaseException
        check(BaseException(), size('5Pb'))
        # UnicodeEncodeError
        check(UnicodeEncodeError("", "", 0, 0, ""), size('5Pb 2P2nP'))
        # UnicodeDecodeError
        check(UnicodeDecodeError("", b"", 0, 0, ""), size('5Pb 2P2nP'))
        # UnicodeTranslateError
        check(UnicodeTranslateError("", 0, 1, ""), size('5Pb 2P2nP'))
        # ellipses
        check(Ellipsis, size(''))
        # EncodingMap
        zaimportuj codecs, encodings.iso8859_3
        x = codecs.charmap_build(encodings.iso8859_3.decoding_table)
        check(x, size('32B2iB'))
        # enumerate
        check(enumerate([]), size('n3P'))
        # reverse
        check(reversed(''), size('nP'))
        # float
        check(float(0), size('d'))
        # sys.floatinfo
        check(sys.float_info, vsize('') + self.P * len(sys.float_info))
        # frame
        zaimportuj inspect
        CO_MAXBLOCKS = 20
        x = inspect.currentframe()
        ncells = len(x.f_code.co_cellvars)
        nfrees = len(x.f_code.co_freevars)
        extras = x.f_code.co_stacksize + x.f_code.co_nlocals +\
                  ncells + nfrees - 1
        check(x, vsize('12P3ic' + CO_MAXBLOCKS*'3i' + 'P' + extras*'P'))
        # function
        def func(): dalej
        check(func, size('12P'))
        klasa c():
            @staticmethod
            def foo():
                dalej
            @classmethod
            def bar(cls):
                dalej
            # staticmethod
            check(foo, size('PP'))
            # classmethod
            check(bar, size('PP'))
        # generator
        def get_gen(): uzyskaj 1
        check(get_gen(), size('Pb2PPP'))
        # iterator
        check(iter('abc'), size('lP'))
        # callable-iterator
        zaimportuj re
        check(re.finditer('',''), size('2P'))
        # list
        samples = [[], [1,2,3], ['1', '2', '3']]
        dla sample w samples:
            check(sample, vsize('Pn') + len(sample)*self.P)
        # sortwrapper (list)
        # XXX
        # cmpwrapper (list)
        # XXX
        # listiterator (list)
        check(iter([]), size('lP'))
        # listreverseiterator (list)
        check(reversed([]), size('nP'))
        # int
        check(0, vsize(''))
        check(1, vsize('') + self.longdigit)
        check(-1, vsize('') + self.longdigit)
        PyLong_BASE = 2**sys.int_info.bits_per_digit
        check(int(PyLong_BASE), vsize('') + 2*self.longdigit)
        check(int(PyLong_BASE**2-1), vsize('') + 2*self.longdigit)
        check(int(PyLong_BASE**2), vsize('') + 3*self.longdigit)
        # module
        check(unittest, size('PnPPP'))
        # Nic
        check(Nic, size(''))
        # NotImplementedType
        check(NotImplemented, size(''))
        # object
        check(object(), size(''))
        # property (descriptor object)
        klasa C(object):
            def getx(self): zwróć self.__x
            def setx(self, value): self.__x = value
            def delx(self): usuń self.__x
            x = property(getx, setx, delx, "")
            check(x, size('4Pi'))
        # PyCapsule
        # XXX
        # rangeiterator
        check(iter(range(1)), size('4l'))
        # reverse
        check(reversed(''), size('nP'))
        # range
        check(range(1), size('4P'))
        check(range(66000), size('4P'))
        # set
        # frozenset
        PySet_MINSIZE = 8
        samples = [[], range(10), range(50)]
        s = size('3nP' + PySet_MINSIZE*'nP' + '2nP')
        dla sample w samples:
            minused = len(sample)
            jeżeli minused == 0: tmp = 1
            # the computation of minused jest actually a bit more complicated
            # but this suffices dla the sizeof test
            minused = minused*2
            newsize = PySet_MINSIZE
            dopóki newsize <= minused:
                newsize = newsize << 1
            jeżeli newsize <= 8:
                check(set(sample), s)
                check(frozenset(sample), s)
            inaczej:
                check(set(sample), s + newsize*struct.calcsize('nP'))
                check(frozenset(sample), s + newsize*struct.calcsize('nP'))
        # setiterator
        check(iter(set()), size('P3n'))
        # slice
        check(slice(0), size('3P'))
        # super
        check(super(int), size('3P'))
        # tuple
        check((), vsize(''))
        check((1,2,3), vsize('') + 3*self.P)
        # type
        # static type: PyTypeObject
        s = vsize('P2n15Pl4Pn9Pn11PIP')
        check(int, s)
        # (PyTypeObject + PyAsyncMethods + PyNumberMethods + PyMappingMethods +
        #  PySequenceMethods + PyBufferProcs + 4P)
        s = vsize('P2n17Pl4Pn9Pn11PIP') + struct.calcsize('34P 3P 3P 10P 2P 4P')
        # Separate block dla PyDictKeysObject przy 4 entries
        s += struct.calcsize("2nPn") + 4*struct.calcsize("n2P")
        # class
        klasa newstyleclass(object): dalej
        check(newstyleclass, s)
        # dict przy shared keys
        check(newstyleclass().__dict__, size('n2P' + '2nPn'))
        # unicode
        # each tuple contains a string oraz its expected character size
        # don't put any static strings here, jako they may contain
        # wchar_t albo UTF-8 representations
        samples = ['1'*100, '\xff'*50,
                   '\u0100'*40, '\uffff'*100,
                   '\U00010000'*30, '\U0010ffff'*100]
        asciifields = "nnbP"
        compactfields = asciifields + "nPn"
        unicodefields = compactfields + "P"
        dla s w samples:
            maxchar = ord(max(s))
            jeżeli maxchar < 128:
                L = size(asciifields) + len(s) + 1
            albo_inaczej maxchar < 256:
                L = size(compactfields) + len(s) + 1
            albo_inaczej maxchar < 65536:
                L = size(compactfields) + 2*(len(s) + 1)
            inaczej:
                L = size(compactfields) + 4*(len(s) + 1)
            check(s, L)
        # verify that the UTF-8 size jest accounted for
        s = chr(0x4000)   # 4 bytes canonical representation
        check(s, size(compactfields) + 4)
        # compile() will trigger the generation of the UTF-8
        # representation jako a side effect
        compile(s, "<stdin>", "eval")
        check(s, size(compactfields) + 4 + 4)
        # TODO: add check that forces the presence of wchar_t representation
        # TODO: add check that forces layout of unicodefields
        # weakref
        zaimportuj weakref
        check(weakref.ref(int), size('2Pn2P'))
        # weakproxy
        # XXX
        # weakcallableproxy
        check(weakref.proxy(int), size('2Pn2P'))

    def test_pythontypes(self):
        # check all types defined w Python/
        size = test.support.calcobjsize
        vsize = test.support.calcvobjsize
        check = self.check_sizeof
        # _ast.AST
        zaimportuj _ast
        check(_ast.AST(), size('P'))
        spróbuj:
            podnieś TypeError
        wyjąwszy TypeError:
            tb = sys.exc_info()[2]
            # traceback
            jeżeli tb jest nie Nic:
                check(tb, size('2P2i'))
        # symtable entry
        # XXX
        # sys.flags
        check(sys.flags, vsize('') + self.P * len(sys.flags))


def test_main():
    test.support.run_unittest(SysModuleTest, SizeofTest)

jeżeli __name__ == "__main__":
    test_main()
