zaimportuj unittest
z test.support zaimportuj script_helper
z test zaimportuj support
zaimportuj subprocess
zaimportuj sys
zaimportuj signal
zaimportuj io
zaimportuj locale
zaimportuj os
zaimportuj errno
zaimportuj tempfile
zaimportuj time
zaimportuj re
zaimportuj selectors
zaimportuj sysconfig
zaimportuj warnings
zaimportuj select
zaimportuj shutil
zaimportuj gc
zaimportuj textwrap

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

mswindows = (sys.platform == "win32")

#
# Depends on the following external programs: Python
#

jeżeli mswindows:
    SETBINARY = ('zaimportuj msvcrt; msvcrt.setmode(sys.stdout.fileno(), '
                                                'os.O_BINARY);')
inaczej:
    SETBINARY = ''


spróbuj:
    mkstemp = tempfile.mkstemp
wyjąwszy AttributeError:
    # tempfile.mkstemp jest nie available
    def mkstemp():
        """Replacement dla mkstemp, calling mktemp."""
        fname = tempfile.mktemp()
        zwróć os.open(fname, os.O_RDWR|os.O_CREAT), fname


klasa BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Try to minimize the number of children we have so this test
        # doesn't crash on some buildbots (Alphas w particular).
        support.reap_children()

    def tearDown(self):
        dla inst w subprocess._active:
            inst.wait()
        subprocess._cleanup()
        self.assertNieprawda(subprocess._active, "subprocess._active nie empty")

    def assertStderrEqual(self, stderr, expected, msg=Nic):
        # In a debug build, stuff like "[6580 refs]" jest printed to stderr at
        # shutdown time.  That frustrates tests trying to check stderr produced
        # z a spawned Python process.
        actual = support.strip_python_stderr(stderr)
        # strip_python_stderr also strips whitespace, so we do too.
        expected = expected.strip()
        self.assertEqual(actual, expected, msg)


klasa PopenTestException(Exception):
    dalej


klasa PopenExecuteChildRaises(subprocess.Popen):
    """Popen subclass dla testing cleanup of subprocess.PIPE filehandles when
    _execute_child fails.
    """
    def _execute_child(self, *args, **kwargs):
        podnieś PopenTestException("Forced Exception dla Test")


klasa ProcessTestCase(BaseTestCase):

    def test_io_buffered_by_default(self):
        p = subprocess.Popen([sys.executable, "-c", "zaimportuj sys; sys.exit(0)"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        spróbuj:
            self.assertIsInstance(p.stdin, io.BufferedIOBase)
            self.assertIsInstance(p.stdout, io.BufferedIOBase)
            self.assertIsInstance(p.stderr, io.BufferedIOBase)
        w_końcu:
            p.stdin.close()
            p.stdout.close()
            p.stderr.close()
            p.wait()

    def test_io_unbuffered_works(self):
        p = subprocess.Popen([sys.executable, "-c", "zaimportuj sys; sys.exit(0)"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, bufsize=0)
        spróbuj:
            self.assertIsInstance(p.stdin, io.RawIOBase)
            self.assertIsInstance(p.stdout, io.RawIOBase)
            self.assertIsInstance(p.stderr, io.RawIOBase)
        w_końcu:
            p.stdin.close()
            p.stdout.close()
            p.stderr.close()
            p.wait()

    def test_call_seq(self):
        # call() function przy sequence argument
        rc = subprocess.call([sys.executable, "-c",
                              "zaimportuj sys; sys.exit(47)"])
        self.assertEqual(rc, 47)

    def test_call_timeout(self):
        # call() function przy timeout argument; we want to test that the child
        # process gets killed when the timeout expires.  If the child isn't
        # killed, this call will deadlock since subprocess.call waits dla the
        # child.
        self.assertRaises(subprocess.TimeoutExpired, subprocess.call,
                          [sys.executable, "-c", "dopóki Prawda: dalej"],
                          timeout=0.1)

    def test_check_call_zero(self):
        # check_call() function przy zero zwróć code
        rc = subprocess.check_call([sys.executable, "-c",
                                    "zaimportuj sys; sys.exit(0)"])
        self.assertEqual(rc, 0)

    def test_check_call_nonzero(self):
        # check_call() function przy non-zero zwróć code
        przy self.assertRaises(subprocess.CalledProcessError) jako c:
            subprocess.check_call([sys.executable, "-c",
                                   "zaimportuj sys; sys.exit(47)"])
        self.assertEqual(c.exception.returncode, 47)

    def test_check_output(self):
        # check_output() function przy zero zwróć code
        output = subprocess.check_output(
                [sys.executable, "-c", "print('BDFL')"])
        self.assertIn(b'BDFL', output)

    def test_check_output_nonzero(self):
        # check_call() function przy non-zero zwróć code
        przy self.assertRaises(subprocess.CalledProcessError) jako c:
            subprocess.check_output(
                    [sys.executable, "-c", "zaimportuj sys; sys.exit(5)"])
        self.assertEqual(c.exception.returncode, 5)

    def test_check_output_stderr(self):
        # check_output() function stderr redirected to stdout
        output = subprocess.check_output(
                [sys.executable, "-c", "zaimportuj sys; sys.stderr.write('BDFL')"],
                stderr=subprocess.STDOUT)
        self.assertIn(b'BDFL', output)

    def test_check_output_stdin_arg(self):
        # check_output() can be called przy stdin set to a file
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b'pear')
        tf.seek(0)
        output = subprocess.check_output(
                [sys.executable, "-c",
                 "zaimportuj sys; sys.stdout.write(sys.stdin.read().upper())"],
                stdin=tf)
        self.assertIn(b'PEAR', output)

    def test_check_output_input_arg(self):
        # check_output() can be called przy input set to a string
        output = subprocess.check_output(
                [sys.executable, "-c",
                 "zaimportuj sys; sys.stdout.write(sys.stdin.read().upper())"],
                input=b'pear')
        self.assertIn(b'PEAR', output)

    def test_check_output_stdout_arg(self):
        # check_output() refuses to accept 'stdout' argument
        przy self.assertRaises(ValueError) jako c:
            output = subprocess.check_output(
                    [sys.executable, "-c", "print('will nie be run')"],
                    stdout=sys.stdout)
            self.fail("Expected ValueError when stdout arg supplied.")
        self.assertIn('stdout', c.exception.args[0])

    def test_check_output_stdin_with_input_arg(self):
        # check_output() refuses to accept 'stdin' przy 'input'
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b'pear')
        tf.seek(0)
        przy self.assertRaises(ValueError) jako c:
            output = subprocess.check_output(
                    [sys.executable, "-c", "print('will nie be run')"],
                    stdin=tf, input=b'hare')
            self.fail("Expected ValueError when stdin oraz input args supplied.")
        self.assertIn('stdin', c.exception.args[0])
        self.assertIn('input', c.exception.args[0])

    def test_check_output_timeout(self):
        # check_output() function przy timeout arg
        przy self.assertRaises(subprocess.TimeoutExpired) jako c:
            output = subprocess.check_output(
                    [sys.executable, "-c",
                     "zaimportuj sys, time\n"
                     "sys.stdout.write('BDFL')\n"
                     "sys.stdout.flush()\n"
                     "time.sleep(3600)"],
                    # Some heavily loaded buildbots (sparc Debian 3.x) require
                    # this much time to start oraz print.
                    timeout=3)
            self.fail("Expected TimeoutExpired.")
        self.assertEqual(c.exception.output, b'BDFL')

    def test_call_kwargs(self):
        # call() function przy keyword args
        newenv = os.environ.copy()
        newenv["FRUIT"] = "banana"
        rc = subprocess.call([sys.executable, "-c",
                              'zaimportuj sys, os;'
                              'sys.exit(os.getenv("FRUIT")=="banana")'],
                             env=newenv)
        self.assertEqual(rc, 1)

    def test_invalid_args(self):
        # Popen() called przy invalid arguments should podnieś TypeError
        # but Popen.__del__ should nie complain (issue #12085)
        przy support.captured_stderr() jako s:
            self.assertRaises(TypeError, subprocess.Popen, invalid_arg_name=1)
            argcount = subprocess.Popen.__init__.__code__.co_argcount
            too_many_args = [0] * (argcount + 1)
            self.assertRaises(TypeError, subprocess.Popen, *too_many_args)
        self.assertEqual(s.getvalue(), '')

    def test_stdin_none(self):
        # .stdin jest Nic when nie redirected
        p = subprocess.Popen([sys.executable, "-c", 'print("banana")'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        p.wait()
        self.assertEqual(p.stdin, Nic)

    def test_stdout_none(self):
        # .stdout jest Nic when nie redirected, oraz the child's stdout will
        # be inherited z the parent.  In order to test this we run a
        # subprocess w a subprocess:
        # this_test
        #   \-- subprocess created by this test (parent)
        #          \-- subprocess created by the parent subprocess (child)
        # The parent doesn't specify stdout, so the child will use the
        # parent's stdout.  This test checks that the message printed by the
        # child goes to the parent stdout.  The parent also checks that the
        # child's stdout jest Nic.  See #11963.
        code = ('zaimportuj sys; z subprocess zaimportuj Popen, PIPE;'
                'p = Popen([sys.executable, "-c", "print(\'test_stdout_none\')"],'
                '          stdin=PIPE, stderr=PIPE);'
                'p.wait(); assert p.stdout jest Nic;')
        p = subprocess.Popen([sys.executable, "-c", code],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0, err)
        self.assertEqual(out.rstrip(), b'test_stdout_none')

    def test_stderr_none(self):
        # .stderr jest Nic when nie redirected
        p = subprocess.Popen([sys.executable, "-c", 'print("banana")'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stdin.close)
        p.wait()
        self.assertEqual(p.stderr, Nic)

    def _assert_python(self, pre_args, **kwargs):
        # We include sys.exit() to prevent the test runner z hanging
        # whenever python jest found.
        args = pre_args + ["zaimportuj sys; sys.exit(47)"]
        p = subprocess.Popen(args, **kwargs)
        p.wait()
        self.assertEqual(47, p.returncode)

    def test_executable(self):
        # Check that the executable argument works.
        #
        # On Unix (non-Mac oraz non-Windows), Python looks at args[0] to
        # determine where its standard library is, so we need the directory
        # of args[0] to be valid dla the Popen() call to Python to succeed.
        # See also issue #16170 oraz issue #7774.
        doesnotexist = os.path.join(os.path.dirname(sys.executable),
                                    "doesnotexist")
        self._assert_python([doesnotexist, "-c"], executable=sys.executable)

    def test_executable_takes_precedence(self):
        # Check that the executable argument takes precedence over args[0].
        #
        # Verify first that the call succeeds without the executable arg.
        pre_args = [sys.executable, "-c"]
        self._assert_python(pre_args)
        self.assertRaises(FileNotFoundError, self._assert_python, pre_args,
                          executable="doesnotexist")

    @unittest.skipIf(mswindows, "executable argument replaces shell")
    def test_executable_replaces_shell(self):
        # Check that the executable argument replaces the default shell
        # when shell=Prawda.
        self._assert_python([], executable=sys.executable, shell=Prawda)

    # For use w the test_cwd* tests below.
    def _normalize_cwd(self, cwd):
        # Normalize an expected cwd (dla Tru64 support).
        # We can't use os.path.realpath since it doesn't expand Tru64 {memb}
        # strings.  See bug #1063571.
        original_cwd = os.getcwd()
        os.chdir(cwd)
        cwd = os.getcwd()
        os.chdir(original_cwd)
        zwróć cwd

    # For use w the test_cwd* tests below.
    def _split_python_path(self):
        # Return normalized (python_dir, python_base).
        python_path = os.path.realpath(sys.executable)
        zwróć os.path.split(python_path)

    # For use w the test_cwd* tests below.
    def _assert_cwd(self, expected_cwd, python_arg, **kwargs):
        # Invoke Python via Popen, oraz assert that (1) the call succeeds,
        # oraz that (2) the current working directory of the child process
        # matches *expected_cwd*.
        p = subprocess.Popen([python_arg, "-c",
                              "zaimportuj os, sys; "
                              "sys.stdout.write(os.getcwd()); "
                              "sys.exit(47)"],
                              stdout=subprocess.PIPE,
                              **kwargs)
        self.addCleanup(p.stdout.close)
        p.wait()
        self.assertEqual(47, p.returncode)
        normcase = os.path.normcase
        self.assertEqual(normcase(expected_cwd),
                         normcase(p.stdout.read().decode("utf-8")))

    def test_cwd(self):
        # Check that cwd changes the cwd dla the child process.
        temp_dir = tempfile.gettempdir()
        temp_dir = self._normalize_cwd(temp_dir)
        self._assert_cwd(temp_dir, sys.executable, cwd=temp_dir)

    @unittest.skipIf(mswindows, "pending resolution of issue #15533")
    def test_cwd_with_relative_arg(self):
        # Check that Popen looks dla args[0] relative to cwd jeżeli args[0]
        # jest relative.
        python_dir, python_base = self._split_python_path()
        rel_python = os.path.join(os.curdir, python_base)
        przy support.temp_cwd() jako wrong_dir:
            # Before calling przy the correct cwd, confirm that the call fails
            # without cwd oraz przy the wrong cwd.
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [rel_python])
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [rel_python], cwd=wrong_dir)
            python_dir = self._normalize_cwd(python_dir)
            self._assert_cwd(python_dir, rel_python, cwd=python_dir)

    @unittest.skipIf(mswindows, "pending resolution of issue #15533")
    def test_cwd_with_relative_executable(self):
        # Check that Popen looks dla executable relative to cwd jeżeli executable
        # jest relative (and that executable takes precedence over args[0]).
        python_dir, python_base = self._split_python_path()
        rel_python = os.path.join(os.curdir, python_base)
        doesntexist = "somethingyoudonthave"
        przy support.temp_cwd() jako wrong_dir:
            # Before calling przy the correct cwd, confirm that the call fails
            # without cwd oraz przy the wrong cwd.
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [doesntexist], executable=rel_python)
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [doesntexist], executable=rel_python,
                              cwd=wrong_dir)
            python_dir = self._normalize_cwd(python_dir)
            self._assert_cwd(python_dir, doesntexist, executable=rel_python,
                             cwd=python_dir)

    def test_cwd_with_absolute_arg(self):
        # Check that Popen can find the executable when the cwd jest wrong
        # jeżeli args[0] jest an absolute path.
        python_dir, python_base = self._split_python_path()
        abs_python = os.path.join(python_dir, python_base)
        rel_python = os.path.join(os.curdir, python_base)
        przy support.temp_dir() jako wrong_dir:
            # Before calling przy an absolute path, confirm that using a
            # relative path fails.
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [rel_python], cwd=wrong_dir)
            wrong_dir = self._normalize_cwd(wrong_dir)
            self._assert_cwd(wrong_dir, abs_python, cwd=wrong_dir)

    @unittest.skipIf(sys.base_prefix != sys.prefix,
                     'Test jest nie venv-compatible')
    def test_executable_with_cwd(self):
        python_dir, python_base = self._split_python_path()
        python_dir = self._normalize_cwd(python_dir)
        self._assert_cwd(python_dir, "somethingyoudonthave",
                         executable=sys.executable, cwd=python_dir)

    @unittest.skipIf(sys.base_prefix != sys.prefix,
                     'Test jest nie venv-compatible')
    @unittest.skipIf(sysconfig.is_python_build(),
                     "need an installed Python. See #7774")
    def test_executable_without_cwd(self):
        # For a normal installation, it should work without 'cwd'
        # argument.  For test runs w the build directory, see #7774.
        self._assert_cwd(os.getcwd(), "somethingyoudonthave",
                         executable=sys.executable)

    def test_stdin_pipe(self):
        # stdin redirection
        p = subprocess.Popen([sys.executable, "-c",
                         'zaimportuj sys; sys.exit(sys.stdin.read() == "pear")'],
                        stdin=subprocess.PIPE)
        p.stdin.write(b"pear")
        p.stdin.close()
        p.wait()
        self.assertEqual(p.returncode, 1)

    def test_stdin_filedes(self):
        # stdin jest set to open file descriptor
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        d = tf.fileno()
        os.write(d, b"pear")
        os.lseek(d, 0, 0)
        p = subprocess.Popen([sys.executable, "-c",
                         'zaimportuj sys; sys.exit(sys.stdin.read() == "pear")'],
                         stdin=d)
        p.wait()
        self.assertEqual(p.returncode, 1)

    def test_stdin_fileobj(self):
        # stdin jest set to open file object
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b"pear")
        tf.seek(0)
        p = subprocess.Popen([sys.executable, "-c",
                         'zaimportuj sys; sys.exit(sys.stdin.read() == "pear")'],
                         stdin=tf)
        p.wait()
        self.assertEqual(p.returncode, 1)

    def test_stdout_pipe(self):
        # stdout redirection
        p = subprocess.Popen([sys.executable, "-c",
                          'zaimportuj sys; sys.stdout.write("orange")'],
                         stdout=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.assertEqual(p.stdout.read(), b"orange")

    def test_stdout_filedes(self):
        # stdout jest set to open file descriptor
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        d = tf.fileno()
        p = subprocess.Popen([sys.executable, "-c",
                          'zaimportuj sys; sys.stdout.write("orange")'],
                         stdout=d)
        p.wait()
        os.lseek(d, 0, 0)
        self.assertEqual(os.read(d, 1024), b"orange")

    def test_stdout_fileobj(self):
        # stdout jest set to open file object
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        p = subprocess.Popen([sys.executable, "-c",
                          'zaimportuj sys; sys.stdout.write("orange")'],
                         stdout=tf)
        p.wait()
        tf.seek(0)
        self.assertEqual(tf.read(), b"orange")

    def test_stderr_pipe(self):
        # stderr redirection
        p = subprocess.Popen([sys.executable, "-c",
                          'zaimportuj sys; sys.stderr.write("strawberry")'],
                         stderr=subprocess.PIPE)
        self.addCleanup(p.stderr.close)
        self.assertStderrEqual(p.stderr.read(), b"strawberry")

    def test_stderr_filedes(self):
        # stderr jest set to open file descriptor
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        d = tf.fileno()
        p = subprocess.Popen([sys.executable, "-c",
                          'zaimportuj sys; sys.stderr.write("strawberry")'],
                         stderr=d)
        p.wait()
        os.lseek(d, 0, 0)
        self.assertStderrEqual(os.read(d, 1024), b"strawberry")

    def test_stderr_fileobj(self):
        # stderr jest set to open file object
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        p = subprocess.Popen([sys.executable, "-c",
                          'zaimportuj sys; sys.stderr.write("strawberry")'],
                         stderr=tf)
        p.wait()
        tf.seek(0)
        self.assertStderrEqual(tf.read(), b"strawberry")

    def test_stdout_stderr_pipe(self):
        # capture stdout oraz stderr to the same pipe
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys;'
                              'sys.stdout.write("apple");'
                              'sys.stdout.flush();'
                              'sys.stderr.write("orange")'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        self.addCleanup(p.stdout.close)
        self.assertStderrEqual(p.stdout.read(), b"appleorange")

    def test_stdout_stderr_file(self):
        # capture stdout oraz stderr to the same open file
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys;'
                              'sys.stdout.write("apple");'
                              'sys.stdout.flush();'
                              'sys.stderr.write("orange")'],
                             stdout=tf,
                             stderr=tf)
        p.wait()
        tf.seek(0)
        self.assertStderrEqual(tf.read(), b"appleorange")

    def test_stdout_filedes_of_stdout(self):
        # stdout jest set to 1 (#1531862).
        # To avoid printing the text on stdout, we do something similar to
        # test_stdout_none (see above).  The parent subprocess calls the child
        # subprocess dalejing stdout=1, oraz this test uses stdout=PIPE w
        # order to capture oraz check the output of the parent. See #11963.
        code = ('zaimportuj sys, subprocess; '
                'rc = subprocess.call([sys.executable, "-c", '
                '    "zaimportuj os, sys; sys.exit(os.write(sys.stdout.fileno(), '
                     'b\'test przy stdout=1\'))"], stdout=1); '
                'assert rc == 18')
        p = subprocess.Popen([sys.executable, "-c", code],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0, err)
        self.assertEqual(out.rstrip(), b'test przy stdout=1')

    def test_stdout_devnull(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'dla i w range(10240):'
                              'print("x" * 1024)'],
                              stdout=subprocess.DEVNULL)
        p.wait()
        self.assertEqual(p.stdout, Nic)

    def test_stderr_devnull(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys\n'
                              'dla i w range(10240):'
                              'sys.stderr.write("x" * 1024)'],
                              stderr=subprocess.DEVNULL)
        p.wait()
        self.assertEqual(p.stderr, Nic)

    def test_stdin_devnull(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys;'
                              'sys.stdin.read(1)'],
                              stdin=subprocess.DEVNULL)
        p.wait()
        self.assertEqual(p.stdin, Nic)

    def test_env(self):
        newenv = os.environ.copy()
        newenv["FRUIT"] = "orange"
        przy subprocess.Popen([sys.executable, "-c",
                               'zaimportuj sys,os;'
                               'sys.stdout.write(os.getenv("FRUIT"))'],
                              stdout=subprocess.PIPE,
                              env=newenv) jako p:
            stdout, stderr = p.communicate()
            self.assertEqual(stdout, b"orange")

    # Windows requires at least the SYSTEMROOT environment variable to start
    # Python
    @unittest.skipIf(sys.platform == 'win32',
                     'cannot test an empty env on Windows')
    @unittest.skipIf(sysconfig.get_config_var('Py_ENABLE_SHARED') jest nie Nic,
                     'the python library cannot be loaded '
                     'przy an empty environment')
    def test_empty_env(self):
        przy subprocess.Popen([sys.executable, "-c",
                               'zaimportuj os; '
                               'print(list(os.environ.keys()))'],
                              stdout=subprocess.PIPE,
                              env={}) jako p:
            stdout, stderr = p.communicate()
            self.assertIn(stdout.strip(),
                (b"[]",
                 # Mac OS X adds __CF_USER_TEXT_ENCODING variable to an empty
                 # environment
                 b"['__CF_USER_TEXT_ENCODING']"))

    def test_communicate_stdin(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys;'
                              'sys.exit(sys.stdin.read() == "pear")'],
                             stdin=subprocess.PIPE)
        p.communicate(b"pear")
        self.assertEqual(p.returncode, 1)

    def test_communicate_stdout(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys; sys.stdout.write("pineapple")'],
                             stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, b"pineapple")
        self.assertEqual(stderr, Nic)

    def test_communicate_stderr(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys; sys.stderr.write("pineapple")'],
                             stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, Nic)
        self.assertStderrEqual(stderr, b"pineapple")

    def test_communicate(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os;'
                              'sys.stderr.write("pineapple");'
                              'sys.stdout.write(sys.stdin.read())'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        (stdout, stderr) = p.communicate(b"banana")
        self.assertEqual(stdout, b"banana")
        self.assertStderrEqual(stderr, b"pineapple")

    def test_communicate_timeout(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os,time;'
                              'sys.stderr.write("pineapple\\n");'
                              'time.sleep(1);'
                              'sys.stderr.write("pear\\n");'
                              'sys.stdout.write(sys.stdin.read())'],
                             universal_newlines=Prawda,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.assertRaises(subprocess.TimeoutExpired, p.communicate, "banana",
                          timeout=0.3)
        # Make sure we can keep waiting dla it, oraz that we get the whole output
        # after it completes.
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, "banana")
        self.assertStderrEqual(stderr.encode(), b"pineapple\npear\n")

    def test_communicate_timeout_large_ouput(self):
        # Test an expiring timeout dopóki the child jest outputting lots of data.
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os,time;'
                              'sys.stdout.write("a" * (64 * 1024));'
                              'time.sleep(0.2);'
                              'sys.stdout.write("a" * (64 * 1024));'
                              'time.sleep(0.2);'
                              'sys.stdout.write("a" * (64 * 1024));'
                              'time.sleep(0.2);'
                              'sys.stdout.write("a" * (64 * 1024));'],
                             stdout=subprocess.PIPE)
        self.assertRaises(subprocess.TimeoutExpired, p.communicate, timeout=0.4)
        (stdout, _) = p.communicate()
        self.assertEqual(len(stdout), 4 * 64 * 1024)

    # Test dla the fd leak reported w http://bugs.python.org/issue2791.
    def test_communicate_pipe_fd_leak(self):
        dla stdin_pipe w (Nieprawda, Prawda):
            dla stdout_pipe w (Nieprawda, Prawda):
                dla stderr_pipe w (Nieprawda, Prawda):
                    options = {}
                    jeżeli stdin_pipe:
                        options['stdin'] = subprocess.PIPE
                    jeżeli stdout_pipe:
                        options['stdout'] = subprocess.PIPE
                    jeżeli stderr_pipe:
                        options['stderr'] = subprocess.PIPE
                    jeżeli nie options:
                        kontynuuj
                    p = subprocess.Popen((sys.executable, "-c", "pass"), **options)
                    p.communicate()
                    jeżeli p.stdin jest nie Nic:
                        self.assertPrawda(p.stdin.closed)
                    jeżeli p.stdout jest nie Nic:
                        self.assertPrawda(p.stdout.closed)
                    jeżeli p.stderr jest nie Nic:
                        self.assertPrawda(p.stderr.closed)

    def test_communicate_returns(self):
        # communicate() should zwróć Nic jeżeli no redirection jest active
        p = subprocess.Popen([sys.executable, "-c",
                              "zaimportuj sys; sys.exit(47)"])
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, Nic)
        self.assertEqual(stderr, Nic)

    def test_communicate_pipe_buf(self):
        # communicate() przy writes larger than pipe_buf
        # This test will probably deadlock rather than fail, if
        # communicate() does nie work properly.
        x, y = os.pipe()
        os.close(x)
        os.close(y)
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os;'
                              'sys.stdout.write(sys.stdin.read(47));'
                              'sys.stderr.write("x" * %d);'
                              'sys.stdout.write(sys.stdin.read())' %
                              support.PIPE_MAX_SIZE],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        string_to_write = b"a" * support.PIPE_MAX_SIZE
        (stdout, stderr) = p.communicate(string_to_write)
        self.assertEqual(stdout, string_to_write)

    def test_writes_before_communicate(self):
        # stdin.write before communicate()
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os;'
                              'sys.stdout.write(sys.stdin.read())'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        p.stdin.write(b"banana")
        (stdout, stderr) = p.communicate(b"split")
        self.assertEqual(stdout, b"bananasplit")
        self.assertStderrEqual(stderr, b"")

    def test_universal_newlines(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os;' + SETBINARY +
                              'buf = sys.stdout.buffer;'
                              'buf.write(sys.stdin.readline().encode());'
                              'buf.flush();'
                              'buf.write(b"line2\\n");'
                              'buf.flush();'
                              'buf.write(sys.stdin.read().encode());'
                              'buf.flush();'
                              'buf.write(b"line4\\n");'
                              'buf.flush();'
                              'buf.write(b"line5\\r\\n");'
                              'buf.flush();'
                              'buf.write(b"line6\\r");'
                              'buf.flush();'
                              'buf.write(b"\\nline7");'
                              'buf.flush();'
                              'buf.write(b"\\nline8");'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=1)
        p.stdin.write("line1\n")
        p.stdin.flush()
        self.assertEqual(p.stdout.readline(), "line1\n")
        p.stdin.write("line3\n")
        p.stdin.close()
        self.addCleanup(p.stdout.close)
        self.assertEqual(p.stdout.readline(),
                         "line2\n")
        self.assertEqual(p.stdout.read(6),
                         "line3\n")
        self.assertEqual(p.stdout.read(),
                         "line4\nline5\nline6\nline7\nline8")

    def test_universal_newlines_communicate(self):
        # universal newlines through communicate()
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os;' + SETBINARY +
                              'buf = sys.stdout.buffer;'
                              'buf.write(b"line2\\n");'
                              'buf.flush();'
                              'buf.write(b"line4\\n");'
                              'buf.flush();'
                              'buf.write(b"line5\\r\\n");'
                              'buf.flush();'
                              'buf.write(b"line6\\r");'
                              'buf.flush();'
                              'buf.write(b"\\nline7");'
                              'buf.flush();'
                              'buf.write(b"\\nline8");'],
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=1)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout,
                         "line2\nline4\nline5\nline6\nline7\nline8")

    def test_universal_newlines_communicate_stdin(self):
        # universal newlines through communicate(), przy only stdin
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os;' + SETBINARY + textwrap.dedent('''
                               s = sys.stdin.readline()
                               assert s == "line1\\n", repr(s)
                               s = sys.stdin.read()
                               assert s == "line3\\n", repr(s)
                              ''')],
                             stdin=subprocess.PIPE,
                             universal_newlines=1)
        (stdout, stderr) = p.communicate("line1\nline3\n")
        self.assertEqual(p.returncode, 0)

    def test_universal_newlines_communicate_input_none(self):
        # Test communicate(input=Nic) przy universal newlines.
        #
        # We set stdout to PIPE because, jako of this writing, a different
        # code path jest tested when the number of pipes jest zero albo one.
        p = subprocess.Popen([sys.executable, "-c", "pass"],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=Prawda)
        p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_universal_newlines_communicate_stdin_stdout_stderr(self):
        # universal newlines through communicate(), przy stdin, stdout, stderr
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os;' + SETBINARY + textwrap.dedent('''
                               s = sys.stdin.buffer.readline()
                               sys.stdout.buffer.write(s)
                               sys.stdout.buffer.write(b"line2\\r")
                               sys.stderr.buffer.write(b"eline2\\n")
                               s = sys.stdin.buffer.read()
                               sys.stdout.buffer.write(s)
                               sys.stdout.buffer.write(b"line4\\n")
                               sys.stdout.buffer.write(b"line5\\r\\n")
                               sys.stderr.buffer.write(b"eline6\\r")
                               sys.stderr.buffer.write(b"eline7\\r\\nz")
                              ''')],
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=Prawda)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        (stdout, stderr) = p.communicate("line1\nline3\n")
        self.assertEqual(p.returncode, 0)
        self.assertEqual("line1\nline2\nline3\nline4\nline5\n", stdout)
        # Python debug build push something like "[42442 refs]\n"
        # to stderr at exit of subprocess.
        # Don't use assertStderrEqual because it strips CR oraz LF z output.
        self.assertPrawda(stderr.startswith("eline2\neline6\neline7\n"))

    def test_universal_newlines_communicate_encodings(self):
        # Check that universal newlines mode works dla various encodings,
        # w particular dla encodings w the UTF-16 oraz UTF-32 families.
        # See issue #15595.
        #
        # UTF-16 oraz UTF-32-BE are sufficient to check both przy BOM oraz
        # without, oraz UTF-16 oraz UTF-32.
        zaimportuj _bootlocale
        dla encoding w ['utf-16', 'utf-32-be']:
            old_getpreferredencoding = _bootlocale.getpreferredencoding
            # Indirectly via io.TextIOWrapper, Popen() defaults to
            # locale.getpreferredencoding(Nieprawda) oraz earlier w Python 3.2 to
            # locale.getpreferredencoding().
            def getpreferredencoding(do_setlocale=Prawda):
                zwróć encoding
            code = ("zaimportuj sys; "
                    r"sys.stdout.buffer.write('1\r\n2\r3\n4'.encode('%s'))" %
                    encoding)
            args = [sys.executable, '-c', code]
            spróbuj:
                _bootlocale.getpreferredencoding = getpreferredencoding
                # We set stdin to be non-Nic because, jako of this writing,
                # a different code path jest used when the number of pipes jest
                # zero albo one.
                popen = subprocess.Popen(args, universal_newlines=Prawda,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE)
                stdout, stderr = popen.communicate(input='')
            w_końcu:
                _bootlocale.getpreferredencoding = old_getpreferredencoding
            self.assertEqual(stdout, '1\n2\n3\n4')

    def test_no_leaking(self):
        # Make sure we leak no resources
        jeżeli nie mswindows:
            max_handles = 1026 # too much dla most UNIX systems
        inaczej:
            max_handles = 2050 # too much dla (at least some) Windows setups
        handles = []
        tmpdir = tempfile.mkdtemp()
        spróbuj:
            dla i w range(max_handles):
                spróbuj:
                    tmpfile = os.path.join(tmpdir, support.TESTFN)
                    handles.append(os.open(tmpfile, os.O_WRONLY|os.O_CREAT))
                wyjąwszy OSError jako e:
                    jeżeli e.errno != errno.EMFILE:
                        podnieś
                    przerwij
            inaczej:
                self.skipTest("failed to reach the file descriptor limit "
                    "(tried %d)" % max_handles)
            # Close a couple of them (should be enough dla a subprocess)
            dla i w range(10):
                os.close(handles.pop())
            # Loop creating some subprocesses. If one of them leaks some fds,
            # the next loop iteration will fail by reaching the max fd limit.
            dla i w range(15):
                p = subprocess.Popen([sys.executable, "-c",
                                      "zaimportuj sys;"
                                      "sys.stdout.write(sys.stdin.read())"],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                data = p.communicate(b"lime")[0]
                self.assertEqual(data, b"lime")
        w_końcu:
            dla h w handles:
                os.close(h)
            shutil.rmtree(tmpdir)

    def test_list2cmdline(self):
        self.assertEqual(subprocess.list2cmdline(['a b c', 'd', 'e']),
                         '"a b c" d e')
        self.assertEqual(subprocess.list2cmdline(['ab"c', '\\', 'd']),
                         'ab\\"c \\ d')
        self.assertEqual(subprocess.list2cmdline(['ab"c', ' \\', 'd']),
                         'ab\\"c " \\\\" d')
        self.assertEqual(subprocess.list2cmdline(['a\\\\\\b', 'de fg', 'h']),
                         'a\\\\\\b "de fg" h')
        self.assertEqual(subprocess.list2cmdline(['a\\"b', 'c', 'd']),
                         'a\\\\\\"b c d')
        self.assertEqual(subprocess.list2cmdline(['a\\\\b c', 'd', 'e']),
                         '"a\\\\b c" d e')
        self.assertEqual(subprocess.list2cmdline(['a\\\\b\\ c', 'd', 'e']),
                         '"a\\\\b\\ c" d e')
        self.assertEqual(subprocess.list2cmdline(['ab', '']),
                         'ab ""')

    def test_poll(self):
        p = subprocess.Popen([sys.executable, "-c",
                              "zaimportuj os; os.read(0, 1)"],
                             stdin=subprocess.PIPE)
        self.addCleanup(p.stdin.close)
        self.assertIsNic(p.poll())
        os.write(p.stdin.fileno(), b'A')
        p.wait()
        # Subsequent invocations should just zwróć the returncode
        self.assertEqual(p.poll(), 0)

    def test_wait(self):
        p = subprocess.Popen([sys.executable, "-c", "pass"])
        self.assertEqual(p.wait(), 0)
        # Subsequent invocations should just zwróć the returncode
        self.assertEqual(p.wait(), 0)

    def test_wait_timeout(self):
        p = subprocess.Popen([sys.executable,
                              "-c", "zaimportuj time; time.sleep(0.3)"])
        przy self.assertRaises(subprocess.TimeoutExpired) jako c:
            p.wait(timeout=0.0001)
        self.assertIn("0.0001", str(c.exception))  # For coverage of __str__.
        # Some heavily loaded buildbots (sparc Debian 3.x) require this much
        # time to start.
        self.assertEqual(p.wait(timeout=3), 0)

    def test_invalid_bufsize(self):
        # an invalid type of the bufsize argument should podnieś
        # TypeError.
        przy self.assertRaises(TypeError):
            subprocess.Popen([sys.executable, "-c", "pass"], "orange")

    def test_bufsize_is_none(self):
        # bufsize=Nic should be the same jako bufsize=0.
        p = subprocess.Popen([sys.executable, "-c", "pass"], Nic)
        self.assertEqual(p.wait(), 0)
        # Again przy keyword arg
        p = subprocess.Popen([sys.executable, "-c", "pass"], bufsize=Nic)
        self.assertEqual(p.wait(), 0)

    def _test_bufsize_equal_one(self, line, expected, universal_newlines):
        # subprocess may deadlock przy bufsize=1, see issue #21332
        przy subprocess.Popen([sys.executable, "-c", "zaimportuj sys;"
                               "sys.stdout.write(sys.stdin.readline());"
                               "sys.stdout.flush()"],
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL,
                              bufsize=1,
                              universal_newlines=universal_newlines) jako p:
            p.stdin.write(line) # expect that it flushes the line w text mode
            os.close(p.stdin.fileno()) # close it without flushing the buffer
            read_line = p.stdout.readline()
            spróbuj:
                p.stdin.close()
            wyjąwszy OSError:
                dalej
            p.stdin = Nic
        self.assertEqual(p.returncode, 0)
        self.assertEqual(read_line, expected)

    def test_bufsize_equal_one_text_mode(self):
        # line jest flushed w text mode przy bufsize=1.
        # we should get the full line w zwróć
        line = "line\n"
        self._test_bufsize_equal_one(line, line, universal_newlines=Prawda)

    def test_bufsize_equal_one_binary_mode(self):
        # line jest nie flushed w binary mode przy bufsize=1.
        # we should get empty response
        line = b'line' + os.linesep.encode() # assume ascii-based locale
        self._test_bufsize_equal_one(line, b'', universal_newlines=Nieprawda)

    def test_leaking_fds_on_error(self):
        # see bug #5179: Popen leaks file descriptors to PIPEs if
        # the child fails to execute; this will eventually exhaust
        # the maximum number of open fds. 1024 seems a very common
        # value dla that limit, but Windows has 2048, so we loop
        # 1024 times (each call leaked two fds).
        dla i w range(1024):
            przy self.assertRaises(OSError) jako c:
                subprocess.Popen(['nonexisting_i_hope'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            # ignore errors that indicate the command was nie found
            jeżeli c.exception.errno nie w (errno.ENOENT, errno.EACCES):
                podnieś c.exception

    @unittest.skipIf(threading jest Nic, "threading required")
    def test_double_close_on_error(self):
        # Issue #18851
        fds = []
        def open_fds():
            dla i w range(20):
                fds.extend(os.pipe())
                time.sleep(0.001)
        t = threading.Thread(target=open_fds)
        t.start()
        spróbuj:
            przy self.assertRaises(EnvironmentError):
                subprocess.Popen(['nonexisting_i_hope'],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        w_końcu:
            t.join()
            exc = Nic
            dla fd w fds:
                # If a double close occurred, some of those fds will
                # already have been closed by mistake, oraz os.close()
                # here will podnieś.
                spróbuj:
                    os.close(fd)
                wyjąwszy OSError jako e:
                    exc = e
            jeżeli exc jest nie Nic:
                podnieś exc

    @unittest.skipIf(threading jest Nic, "threading required")
    def test_threadsafe_wait(self):
        """Issue21291: Popen.wait() needs to be threadsafe dla returncode."""
        proc = subprocess.Popen([sys.executable, '-c',
                                 'zaimportuj time; time.sleep(12)'])
        self.assertEqual(proc.returncode, Nic)
        results = []

        def kill_proc_timer_thread():
            results.append(('thread-start-poll-result', proc.poll()))
            # terminate it z the thread oraz wait dla the result.
            proc.kill()
            proc.wait()
            results.append(('thread-after-kill-and-wait', proc.returncode))
            # this wait should be a no-op given the above.
            proc.wait()
            results.append(('thread-after-second-wait', proc.returncode))

        # This jest a timing sensitive test, the failure mode jest
        # triggered when both the main thread oraz this thread are w
        # the wait() call at once.  The delay here jest to allow the
        # main thread to most likely be blocked w its wait() call.
        t = threading.Timer(0.2, kill_proc_timer_thread)
        t.start()

        jeżeli mswindows:
            expected_errorcode = 1
        inaczej:
            # Should be -9 because of the proc.kill() z the thread.
            expected_errorcode = -9

        # Wait dla the process to finish; the thread should kill it
        # long before it finishes on its own.  Supplying a timeout
        # triggers a different code path dla better coverage.
        proc.wait(timeout=20)
        self.assertEqual(proc.returncode, expected_errorcode,
                         msg="unexpected result w wait z main thread")

        # This should be a no-op przy no change w returncode.
        proc.wait()
        self.assertEqual(proc.returncode, expected_errorcode,
                         msg="unexpected result w second main wait.")

        t.join()
        # Ensure that all of the thread results are jako expected.
        # When a race condition occurs w wait(), the returncode could
        # be set by the wrong thread that doesn't actually have it
        # leading to an incorrect value.
        self.assertEqual([('thread-start-poll-result', Nic),
                          ('thread-after-kill-and-wait', expected_errorcode),
                          ('thread-after-second-wait', expected_errorcode)],
                         results)

    def test_issue8780(self):
        # Ensure that stdout jest inherited z the parent
        # jeżeli stdout=PIPE jest nie used
        code = ';'.join((
            'zaimportuj subprocess, sys',
            'retcode = subprocess.call('
                "[sys.executable, '-c', 'print(\"Hello World!\")'])",
            'assert retcode == 0'))
        output = subprocess.check_output([sys.executable, '-c', code])
        self.assertPrawda(output.startswith(b'Hello World!'), ascii(output))

    def test_handles_closed_on_exception(self):
        # If CreateProcess exits przy an error, ensure the
        # duplicate output handles are released
        ifhandle, ifname = mkstemp()
        ofhandle, ofname = mkstemp()
        efhandle, efname = mkstemp()
        spróbuj:
            subprocess.Popen (["*"], stdin=ifhandle, stdout=ofhandle,
              stderr=efhandle)
        wyjąwszy OSError:
            os.close(ifhandle)
            os.remove(ifname)
            os.close(ofhandle)
            os.remove(ofname)
            os.close(efhandle)
            os.remove(efname)
        self.assertNieprawda(os.path.exists(ifname))
        self.assertNieprawda(os.path.exists(ofname))
        self.assertNieprawda(os.path.exists(efname))

    def test_communicate_epipe(self):
        # Issue 10963: communicate() should hide EPIPE
        p = subprocess.Popen([sys.executable, "-c", 'pass'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        p.communicate(b"x" * 2**20)

    def test_communicate_epipe_only_stdin(self):
        # Issue 10963: communicate() should hide EPIPE
        p = subprocess.Popen([sys.executable, "-c", 'pass'],
                             stdin=subprocess.PIPE)
        self.addCleanup(p.stdin.close)
        p.wait()
        p.communicate(b"x" * 2**20)

    @unittest.skipUnless(hasattr(signal, 'SIGUSR1'),
                         "Requires signal.SIGUSR1")
    @unittest.skipUnless(hasattr(os, 'kill'),
                         "Requires os.kill")
    @unittest.skipUnless(hasattr(os, 'getppid'),
                         "Requires os.getppid")
    def test_communicate_eintr(self):
        # Issue #12493: communicate() should handle EINTR
        def handler(signum, frame):
            dalej
        old_handler = signal.signal(signal.SIGUSR1, handler)
        self.addCleanup(signal.signal, signal.SIGUSR1, old_handler)

        args = [sys.executable, "-c",
                'zaimportuj os, signal;'
                'os.kill(os.getppid(), signal.SIGUSR1)']
        dla stream w ('stdout', 'stderr'):
            kw = {stream: subprocess.PIPE}
            przy subprocess.Popen(args, **kw) jako process:
                # communicate() will be interrupted by SIGUSR1
                process.communicate()


    # This test jest Linux-ish specific dla simplicity to at least have
    # some coverage.  It jest nie a platform specific bug.
    @unittest.skipUnless(os.path.isdir('/proc/%d/fd' % os.getpid()),
                         "Linux specific")
    def test_failed_child_execute_fd_leak(self):
        """Test dla the fork() failure fd leak reported w issue16327."""
        fd_directory = '/proc/%d/fd' % os.getpid()
        fds_before_popen = os.listdir(fd_directory)
        przy self.assertRaises(PopenTestException):
            PopenExecuteChildRaises(
                    [sys.executable, '-c', 'pass'], stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # NOTE: This test doesn't verify that the real _execute_child
        # does nie close the file descriptors itself on the way out
        # during an exception.  Code inspection has confirmed that.

        fds_after_exception = os.listdir(fd_directory)
        self.assertEqual(fds_before_popen, fds_after_exception)


klasa RunFuncTestCase(BaseTestCase):
    def run_python(self, code, **kwargs):
        """Run Python code w a subprocess using subprocess.run"""
        argv = [sys.executable, "-c", code]
        zwróć subprocess.run(argv, **kwargs)

    def test_returncode(self):
        # call() function przy sequence argument
        cp = self.run_python("zaimportuj sys; sys.exit(47)")
        self.assertEqual(cp.returncode, 47)
        przy self.assertRaises(subprocess.CalledProcessError):
            cp.check_returncode()

    def test_check(self):
        przy self.assertRaises(subprocess.CalledProcessError) jako c:
            self.run_python("zaimportuj sys; sys.exit(47)", check=Prawda)
        self.assertEqual(c.exception.returncode, 47)

    def test_check_zero(self):
        # check_returncode shouldn't podnieś when returncode jest zero
        cp = self.run_python("zaimportuj sys; sys.exit(0)", check=Prawda)
        self.assertEqual(cp.returncode, 0)

    def test_timeout(self):
        # run() function przy timeout argument; we want to test that the child
        # process gets killed when the timeout expires.  If the child isn't
        # killed, this call will deadlock since subprocess.run waits dla the
        # child.
        przy self.assertRaises(subprocess.TimeoutExpired):
            self.run_python("dopóki Prawda: dalej", timeout=0.0001)

    def test_capture_stdout(self):
        # capture stdout przy zero zwróć code
        cp = self.run_python("print('BDFL')", stdout=subprocess.PIPE)
        self.assertIn(b'BDFL', cp.stdout)

    def test_capture_stderr(self):
        cp = self.run_python("zaimportuj sys; sys.stderr.write('BDFL')",
                             stderr=subprocess.PIPE)
        self.assertIn(b'BDFL', cp.stderr)

    def test_check_output_stdin_arg(self):
        # run() can be called przy stdin set to a file
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b'pear')
        tf.seek(0)
        cp = self.run_python(
                 "zaimportuj sys; sys.stdout.write(sys.stdin.read().upper())",
                stdin=tf, stdout=subprocess.PIPE)
        self.assertIn(b'PEAR', cp.stdout)

    def test_check_output_input_arg(self):
        # check_output() can be called przy input set to a string
        cp = self.run_python(
                "zaimportuj sys; sys.stdout.write(sys.stdin.read().upper())",
                input=b'pear', stdout=subprocess.PIPE)
        self.assertIn(b'PEAR', cp.stdout)

    def test_check_output_stdin_with_input_arg(self):
        # run() refuses to accept 'stdin' przy 'input'
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b'pear')
        tf.seek(0)
        przy self.assertRaises(ValueError,
              msg="Expected ValueError when stdin oraz input args supplied.") jako c:
            output = self.run_python("print('will nie be run')",
                                     stdin=tf, input=b'hare')
        self.assertIn('stdin', c.exception.args[0])
        self.assertIn('input', c.exception.args[0])

    def test_check_output_timeout(self):
        przy self.assertRaises(subprocess.TimeoutExpired) jako c:
            cp = self.run_python((
                     "zaimportuj sys, time\n"
                     "sys.stdout.write('BDFL')\n"
                     "sys.stdout.flush()\n"
                     "time.sleep(3600)"),
                    # Some heavily loaded buildbots (sparc Debian 3.x) require
                    # this much time to start oraz print.
                    timeout=3, stdout=subprocess.PIPE)
        self.assertEqual(c.exception.output, b'BDFL')
        # output jest aliased to stdout
        self.assertEqual(c.exception.stdout, b'BDFL')

    def test_run_kwargs(self):
        newenv = os.environ.copy()
        newenv["FRUIT"] = "banana"
        cp = self.run_python(('zaimportuj sys, os;'
                      'sys.exit(33 jeżeli os.getenv("FRUIT")=="banana" inaczej 31)'),
                             env=newenv)
        self.assertEqual(cp.returncode, 33)


@unittest.skipIf(mswindows, "POSIX specific tests")
klasa POSIXProcessTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._nonexistent_dir = "/_this/pa.th/does/not/exist"

    def _get_chdir_exception(self):
        spróbuj:
            os.chdir(self._nonexistent_dir)
        wyjąwszy OSError jako e:
            # This avoids hard coding the errno value albo the OS perror()
            # string oraz instead capture the exception that we want to see
            # below dla comparison.
            desired_exception = e
            desired_exception.strerror += ': ' + repr(self._nonexistent_dir)
        inaczej:
            self.fail("chdir to nonexistant directory %s succeeded." %
                      self._nonexistent_dir)
        zwróć desired_exception

    def test_exception_cwd(self):
        """Test error w the child podnieśd w the parent dla a bad cwd."""
        desired_exception = self._get_chdir_exception()
        spróbuj:
            p = subprocess.Popen([sys.executable, "-c", ""],
                                 cwd=self._nonexistent_dir)
        wyjąwszy OSError jako e:
            # Test that the child process chdir failure actually makes
            # it up to the parent process jako the correct exception.
            self.assertEqual(desired_exception.errno, e.errno)
            self.assertEqual(desired_exception.strerror, e.strerror)
        inaczej:
            self.fail("Expected OSError: %s" % desired_exception)

    def test_exception_bad_executable(self):
        """Test error w the child podnieśd w the parent dla a bad executable."""
        desired_exception = self._get_chdir_exception()
        spróbuj:
            p = subprocess.Popen([sys.executable, "-c", ""],
                                 executable=self._nonexistent_dir)
        wyjąwszy OSError jako e:
            # Test that the child process exec failure actually makes
            # it up to the parent process jako the correct exception.
            self.assertEqual(desired_exception.errno, e.errno)
            self.assertEqual(desired_exception.strerror, e.strerror)
        inaczej:
            self.fail("Expected OSError: %s" % desired_exception)

    def test_exception_bad_args_0(self):
        """Test error w the child podnieśd w the parent dla a bad args[0]."""
        desired_exception = self._get_chdir_exception()
        spróbuj:
            p = subprocess.Popen([self._nonexistent_dir, "-c", ""])
        wyjąwszy OSError jako e:
            # Test that the child process exec failure actually makes
            # it up to the parent process jako the correct exception.
            self.assertEqual(desired_exception.errno, e.errno)
            self.assertEqual(desired_exception.strerror, e.strerror)
        inaczej:
            self.fail("Expected OSError: %s" % desired_exception)

    def test_restore_signals(self):
        # Code coverage dla both values of restore_signals to make sure it
        # at least does nie blow up.
        # A test dla behavior would be complex.  Contributions welcome.
        subprocess.call([sys.executable, "-c", ""], restore_signals=Prawda)
        subprocess.call([sys.executable, "-c", ""], restore_signals=Nieprawda)

    def test_start_new_session(self):
        # For code coverage of calling setsid().  We don't care jeżeli we get an
        # EPERM error z it depending on the test execution environment, that
        # still indicates that it was called.
        spróbuj:
            output = subprocess.check_output(
                    [sys.executable, "-c",
                     "zaimportuj os; print(os.getpgid(os.getpid()))"],
                    start_new_session=Prawda)
        wyjąwszy OSError jako e:
            jeżeli e.errno != errno.EPERM:
                podnieś
        inaczej:
            parent_pgid = os.getpgid(os.getpid())
            child_pgid = int(output)
            self.assertNotEqual(parent_pgid, child_pgid)

    def test_run_abort(self):
        # returncode handles signal termination
        przy support.SuppressCrashReport():
            p = subprocess.Popen([sys.executable, "-c",
                                  'zaimportuj os; os.abort()'])
            p.wait()
        self.assertEqual(-p.returncode, signal.SIGABRT)

    def test_preexec(self):
        # DISCLAIMER: Setting environment variables jest *not* a good use
        # of a preexec_fn.  This jest merely a test.
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys,os;'
                              'sys.stdout.write(os.getenv("FRUIT"))'],
                             stdout=subprocess.PIPE,
                             preexec_fn=lambda: os.putenv("FRUIT", "apple"))
        self.addCleanup(p.stdout.close)
        self.assertEqual(p.stdout.read(), b"apple")

    def test_preexec_exception(self):
        def podnieś_it():
            podnieś ValueError("What jeżeli two swallows carried a coconut?")
        spróbuj:
            p = subprocess.Popen([sys.executable, "-c", ""],
                                 preexec_fn=raise_it)
        wyjąwszy subprocess.SubprocessError jako e:
            self.assertPrawda(
                    subprocess._posixsubprocess,
                    "Expected a ValueError z the preexec_fn")
        wyjąwszy ValueError jako e:
            self.assertIn("coconut", e.args[0])
        inaczej:
            self.fail("Exception podnieśd by preexec_fn did nie make it "
                      "to the parent process.")

    klasa _TestExecuteChildPopen(subprocess.Popen):
        """Used to test behavior at the end of _execute_child."""
        def __init__(self, testcase, *args, **kwargs):
            self._testcase = testcase
            subprocess.Popen.__init__(self, *args, **kwargs)

        def _execute_child(self, *args, **kwargs):
            spróbuj:
                subprocess.Popen._execute_child(self, *args, **kwargs)
            w_końcu:
                # Open a bunch of file descriptors oraz verify that
                # none of them are the same jako the ones the Popen
                # instance jest using dla stdin/stdout/stderr.
                devzero_fds = [os.open("/dev/zero", os.O_RDONLY)
                               dla _ w range(8)]
                spróbuj:
                    dla fd w devzero_fds:
                        self._testcase.assertNotIn(
                                fd, (self.stdin.fileno(), self.stdout.fileno(),
                                     self.stderr.fileno()),
                                msg="At least one fd was closed early.")
                w_końcu:
                    dla fd w devzero_fds:
                        os.close(fd)

    @unittest.skipIf(nie os.path.exists("/dev/zero"), "/dev/zero required.")
    def test_preexec_errpipe_does_not_double_close_pipes(self):
        """Issue16140: Don't double close pipes on preexec error."""

        def podnieś_it():
            podnieś subprocess.SubprocessError(
                    "force the _execute_child() errpipe_data path.")

        przy self.assertRaises(subprocess.SubprocessError):
            self._TestExecuteChildPopen(
                        self, [sys.executable, "-c", "pass"],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, preexec_fn=raise_it)

    def test_preexec_gc_module_failure(self):
        # This tests the code that disables garbage collection jeżeli the child
        # process will execute any Python.
        def podnieś_runtime_error():
            podnieś RuntimeError("this shouldn't escape")
        enabled = gc.isenabled()
        orig_gc_disable = gc.disable
        orig_gc_isenabled = gc.isenabled
        spróbuj:
            gc.disable()
            self.assertNieprawda(gc.isenabled())
            subprocess.call([sys.executable, '-c', ''],
                            preexec_fn=lambda: Nic)
            self.assertNieprawda(gc.isenabled(),
                             "Popen enabled gc when it shouldn't.")

            gc.enable()
            self.assertPrawda(gc.isenabled())
            subprocess.call([sys.executable, '-c', ''],
                            preexec_fn=lambda: Nic)
            self.assertPrawda(gc.isenabled(), "Popen left gc disabled.")

            gc.disable = podnieś_runtime_error
            self.assertRaises(RuntimeError, subprocess.Popen,
                              [sys.executable, '-c', ''],
                              preexec_fn=lambda: Nic)

            usuń gc.isenabled  # force an AttributeError
            self.assertRaises(AttributeError, subprocess.Popen,
                              [sys.executable, '-c', ''],
                              preexec_fn=lambda: Nic)
        w_końcu:
            gc.disable = orig_gc_disable
            gc.isenabled = orig_gc_isenabled
            jeżeli nie enabled:
                gc.disable()

    def test_args_string(self):
        # args jest a string
        fd, fname = mkstemp()
        # reopen w text mode
        przy open(fd, "w", errors="surrogateescape") jako fobj:
            fobj.write("#!/bin/sh\n")
            fobj.write("exec '%s' -c 'zaimportuj sys; sys.exit(47)'\n" %
                       sys.executable)
        os.chmod(fname, 0o700)
        p = subprocess.Popen(fname)
        p.wait()
        os.remove(fname)
        self.assertEqual(p.returncode, 47)

    def test_invalid_args(self):
        # invalid arguments should podnieś ValueError
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "zaimportuj sys; sys.exit(47)"],
                          startupinfo=47)
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "zaimportuj sys; sys.exit(47)"],
                          creationflags=47)

    def test_shell_sequence(self):
        # Run command through the shell (sequence)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "apple"
        p = subprocess.Popen(["echo $FRUIT"], shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        self.addCleanup(p.stdout.close)
        self.assertEqual(p.stdout.read().strip(b" \t\r\n\f"), b"apple")

    def test_shell_string(self):
        # Run command through the shell (string)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "apple"
        p = subprocess.Popen("echo $FRUIT", shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        self.addCleanup(p.stdout.close)
        self.assertEqual(p.stdout.read().strip(b" \t\r\n\f"), b"apple")

    def test_call_string(self):
        # call() function przy string argument on UNIX
        fd, fname = mkstemp()
        # reopen w text mode
        przy open(fd, "w", errors="surrogateescape") jako fobj:
            fobj.write("#!/bin/sh\n")
            fobj.write("exec '%s' -c 'zaimportuj sys; sys.exit(47)'\n" %
                       sys.executable)
        os.chmod(fname, 0o700)
        rc = subprocess.call(fname)
        os.remove(fname)
        self.assertEqual(rc, 47)

    def test_specific_shell(self):
        # Issue #9265: Incorrect name dalejed jako arg[0].
        shells = []
        dla prefix w ['/bin', '/usr/bin/', '/usr/local/bin']:
            dla name w ['bash', 'ksh']:
                sh = os.path.join(prefix, name)
                jeżeli os.path.isfile(sh):
                    shells.append(sh)
        jeżeli nie shells: # Will probably work dla any shell but csh.
            self.skipTest("bash albo ksh required dla this test")
        sh = '/bin/sh'
        jeżeli os.path.isfile(sh) oraz nie os.path.islink(sh):
            # Test will fail jeżeli /bin/sh jest a symlink to csh.
            shells.append(sh)
        dla sh w shells:
            p = subprocess.Popen("echo $0", executable=sh, shell=Prawda,
                                 stdout=subprocess.PIPE)
            self.addCleanup(p.stdout.close)
            self.assertEqual(p.stdout.read().strip(), bytes(sh, 'ascii'))

    def _kill_process(self, method, *args):
        # Do nie inherit file handles z the parent.
        # It should fix failures on some platforms.
        # Also set the SIGINT handler to the default to make sure it's nie
        # being ignored (some tests rely on that.)
        old_handler = signal.signal(signal.SIGINT, signal.default_int_handler)
        spróbuj:
            p = subprocess.Popen([sys.executable, "-c", """jeżeli 1:
                                 zaimportuj sys, time
                                 sys.stdout.write('x\\n')
                                 sys.stdout.flush()
                                 time.sleep(30)
                                 """],
                                 close_fds=Prawda,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        w_końcu:
            signal.signal(signal.SIGINT, old_handler)
        # Wait dla the interpreter to be completely initialized before
        # sending any signal.
        p.stdout.read(1)
        getattr(p, method)(*args)
        zwróć p

    @unittest.skipIf(sys.platform.startswith(('netbsd', 'openbsd')),
                     "Due to known OS bug (issue #16762)")
    def _kill_dead_process(self, method, *args):
        # Do nie inherit file handles z the parent.
        # It should fix failures on some platforms.
        p = subprocess.Popen([sys.executable, "-c", """jeżeli 1:
                             zaimportuj sys, time
                             sys.stdout.write('x\\n')
                             sys.stdout.flush()
                             """],
                             close_fds=Prawda,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        # Wait dla the interpreter to be completely initialized before
        # sending any signal.
        p.stdout.read(1)
        # The process should end after this
        time.sleep(1)
        # This shouldn't podnieś even though the child jest now dead
        getattr(p, method)(*args)
        p.communicate()

    def test_send_signal(self):
        p = self._kill_process('send_signal', signal.SIGINT)
        _, stderr = p.communicate()
        self.assertIn(b'KeyboardInterrupt', stderr)
        self.assertNotEqual(p.wait(), 0)

    def test_kill(self):
        p = self._kill_process('kill')
        _, stderr = p.communicate()
        self.assertStderrEqual(stderr, b'')
        self.assertEqual(p.wait(), -signal.SIGKILL)

    def test_terminate(self):
        p = self._kill_process('terminate')
        _, stderr = p.communicate()
        self.assertStderrEqual(stderr, b'')
        self.assertEqual(p.wait(), -signal.SIGTERM)

    def test_send_signal_dead(self):
        # Sending a signal to a dead process
        self._kill_dead_process('send_signal', signal.SIGINT)

    def test_kill_dead(self):
        # Killing a dead process
        self._kill_dead_process('kill')

    def test_terminate_dead(self):
        # Terminating a dead process
        self._kill_dead_process('terminate')

    def _save_fds(self, save_fds):
        fds = []
        dla fd w save_fds:
            inheritable = os.get_inheritable(fd)
            saved = os.dup(fd)
            fds.append((fd, saved, inheritable))
        zwróć fds

    def _restore_fds(self, fds):
        dla fd, saved, inheritable w fds:
            os.dup2(saved, fd, inheritable=inheritable)
            os.close(saved)

    def check_close_std_fds(self, fds):
        # Issue #9905: test that subprocess pipes still work properly with
        # some standard fds closed
        stdin = 0
        saved_fds = self._save_fds(fds)
        dla fd, saved, inheritable w saved_fds:
            jeżeli fd == 0:
                stdin = saved
                przerwij
        spróbuj:
            dla fd w fds:
                os.close(fd)
            out, err = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys;'
                              'sys.stdout.write("apple");'
                              'sys.stdout.flush();'
                              'sys.stderr.write("orange")'],
                       stdin=stdin,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE).communicate()
            err = support.strip_python_stderr(err)
            self.assertEqual((out, err), (b'apple', b'orange'))
        w_końcu:
            self._restore_fds(saved_fds)

    def test_close_fd_0(self):
        self.check_close_std_fds([0])

    def test_close_fd_1(self):
        self.check_close_std_fds([1])

    def test_close_fd_2(self):
        self.check_close_std_fds([2])

    def test_close_fds_0_1(self):
        self.check_close_std_fds([0, 1])

    def test_close_fds_0_2(self):
        self.check_close_std_fds([0, 2])

    def test_close_fds_1_2(self):
        self.check_close_std_fds([1, 2])

    def test_close_fds_0_1_2(self):
        # Issue #10806: test that subprocess pipes still work properly with
        # all standard fds closed.
        self.check_close_std_fds([0, 1, 2])

    def test_small_errpipe_write_fd(self):
        """Issue #15798: Popen should work when stdio fds are available."""
        new_stdin = os.dup(0)
        new_stdout = os.dup(1)
        spróbuj:
            os.close(0)
            os.close(1)

            # Side test: jeżeli errpipe_write fails to have its CLOEXEC
            # flag set this should cause the parent to think the exec
            # failed.  Extremely unlikely: everyone supports CLOEXEC.
            subprocess.Popen([
                    sys.executable, "-c",
                    "print('AssertionError:0:CLOEXEC failure.')"]).wait()
        w_końcu:
            # Restore original stdin oraz stdout
            os.dup2(new_stdin, 0)
            os.dup2(new_stdout, 1)
            os.close(new_stdin)
            os.close(new_stdout)

    def test_remapping_std_fds(self):
        # open up some temporary files
        temps = [mkstemp() dla i w range(3)]
        spróbuj:
            temp_fds = [fd dla fd, fname w temps]

            # unlink the files -- we won't need to reopen them
            dla fd, fname w temps:
                os.unlink(fname)

            # write some data to what will become stdin, oraz rewind
            os.write(temp_fds[1], b"STDIN")
            os.lseek(temp_fds[1], 0, 0)

            # move the standard file descriptors out of the way
            saved_fds = self._save_fds(range(3))
            spróbuj:
                # duplicate the file objects over the standard fd's
                dla fd, temp_fd w enumerate(temp_fds):
                    os.dup2(temp_fd, fd)

                # now use those files w the "wrong" order, so that subprocess
                # has to rearrange them w the child
                p = subprocess.Popen([sys.executable, "-c",
                    'zaimportuj sys; got = sys.stdin.read();'
                    'sys.stdout.write("got %s"%got); sys.stderr.write("err")'],
                    stdin=temp_fds[1],
                    stdout=temp_fds[2],
                    stderr=temp_fds[0])
                p.wait()
            w_końcu:
                self._restore_fds(saved_fds)

            dla fd w temp_fds:
                os.lseek(fd, 0, 0)

            out = os.read(temp_fds[2], 1024)
            err = support.strip_python_stderr(os.read(temp_fds[0], 1024))
            self.assertEqual(out, b"got STDIN")
            self.assertEqual(err, b"err")

        w_końcu:
            dla fd w temp_fds:
                os.close(fd)

    def check_swap_fds(self, stdin_no, stdout_no, stderr_no):
        # open up some temporary files
        temps = [mkstemp() dla i w range(3)]
        temp_fds = [fd dla fd, fname w temps]
        spróbuj:
            # unlink the files -- we won't need to reopen them
            dla fd, fname w temps:
                os.unlink(fname)

            # save a copy of the standard file descriptors
            saved_fds = self._save_fds(range(3))
            spróbuj:
                # duplicate the temp files over the standard fd's 0, 1, 2
                dla fd, temp_fd w enumerate(temp_fds):
                    os.dup2(temp_fd, fd)

                # write some data to what will become stdin, oraz rewind
                os.write(stdin_no, b"STDIN")
                os.lseek(stdin_no, 0, 0)

                # now use those files w the given order, so that subprocess
                # has to rearrange them w the child
                p = subprocess.Popen([sys.executable, "-c",
                    'zaimportuj sys; got = sys.stdin.read();'
                    'sys.stdout.write("got %s"%got); sys.stderr.write("err")'],
                    stdin=stdin_no,
                    stdout=stdout_no,
                    stderr=stderr_no)
                p.wait()

                dla fd w temp_fds:
                    os.lseek(fd, 0, 0)

                out = os.read(stdout_no, 1024)
                err = support.strip_python_stderr(os.read(stderr_no, 1024))
            w_końcu:
                self._restore_fds(saved_fds)

            self.assertEqual(out, b"got STDIN")
            self.assertEqual(err, b"err")

        w_końcu:
            dla fd w temp_fds:
                os.close(fd)

    # When duping fds, jeżeli there arises a situation where one of the fds jest
    # either 0, 1 albo 2, it jest possible that it jest overwritten (#12607).
    # This tests all combinations of this.
    def test_swap_fds(self):
        self.check_swap_fds(0, 1, 2)
        self.check_swap_fds(0, 2, 1)
        self.check_swap_fds(1, 0, 2)
        self.check_swap_fds(1, 2, 0)
        self.check_swap_fds(2, 0, 1)
        self.check_swap_fds(2, 1, 0)

    def test_surrogates_error_message(self):
        def prepare():
            podnieś ValueError("surrogate:\uDCff")

        spróbuj:
            subprocess.call(
                [sys.executable, "-c", "pass"],
                preexec_fn=prepare)
        wyjąwszy ValueError jako err:
            # Pure Python implementations keeps the message
            self.assertIsNic(subprocess._posixsubprocess)
            self.assertEqual(str(err), "surrogate:\uDCff")
        wyjąwszy subprocess.SubprocessError jako err:
            # _posixsubprocess uses a default message
            self.assertIsNotNic(subprocess._posixsubprocess)
            self.assertEqual(str(err), "Exception occurred w preexec_fn.")
        inaczej:
            self.fail("Expected ValueError albo subprocess.SubprocessError")

    def test_undecodable_env(self):
        dla key, value w (('test', 'abc\uDCFF'), ('test\uDCFF', '42')):
            encoded_value = value.encode("ascii", "surrogateescape")

            # test str przy surrogates
            script = "zaimportuj os; print(ascii(os.getenv(%s)))" % repr(key)
            env = os.environ.copy()
            env[key] = value
            # Use C locale to get ASCII dla the locale encoding to force
            # surrogate-escaping of \xFF w the child process; otherwise it can
            # be decoded as-is jeżeli the default locale jest latin-1.
            env['LC_ALL'] = 'C'
            jeżeli sys.platform.startswith("aix"):
                # On AIX, the C locale uses the Latin1 encoding
                decoded_value = encoded_value.decode("latin1", "surrogateescape")
            inaczej:
                # On other UNIXes, the C locale uses the ASCII encoding
                decoded_value = value
            stdout = subprocess.check_output(
                [sys.executable, "-c", script],
                env=env)
            stdout = stdout.rstrip(b'\n\r')
            self.assertEqual(stdout.decode('ascii'), ascii(decoded_value))

            # test bytes
            key = key.encode("ascii", "surrogateescape")
            script = "zaimportuj os; print(ascii(os.getenvb(%s)))" % repr(key)
            env = os.environ.copy()
            env[key] = encoded_value
            stdout = subprocess.check_output(
                [sys.executable, "-c", script],
                env=env)
            stdout = stdout.rstrip(b'\n\r')
            self.assertEqual(stdout.decode('ascii'), ascii(encoded_value))

    def test_bytes_program(self):
        abs_program = os.fsencode(sys.executable)
        path, program = os.path.split(sys.executable)
        program = os.fsencode(program)

        # absolute bytes path
        exitcode = subprocess.call([abs_program, "-c", "pass"])
        self.assertEqual(exitcode, 0)

        # absolute bytes path jako a string
        cmd = b"'" + abs_program + b"' -c dalej"
        exitcode = subprocess.call(cmd, shell=Prawda)
        self.assertEqual(exitcode, 0)

        # bytes program, unicode PATH
        env = os.environ.copy()
        env["PATH"] = path
        exitcode = subprocess.call([program, "-c", "pass"], env=env)
        self.assertEqual(exitcode, 0)

        # bytes program, bytes PATH
        envb = os.environb.copy()
        envb[b"PATH"] = os.fsencode(path)
        exitcode = subprocess.call([program, "-c", "pass"], env=envb)
        self.assertEqual(exitcode, 0)

    def test_pipe_cloexec(self):
        sleeper = support.findfile("input_reader.py", subdir="subprocessdata")
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        p1 = subprocess.Popen([sys.executable, sleeper],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, close_fds=Nieprawda)

        self.addCleanup(p1.communicate, b'')

        p2 = subprocess.Popen([sys.executable, fd_status],
                              stdout=subprocess.PIPE, close_fds=Nieprawda)

        output, error = p2.communicate()
        result_fds = set(map(int, output.split(b',')))
        unwanted_fds = set([p1.stdin.fileno(), p1.stdout.fileno(),
                            p1.stderr.fileno()])

        self.assertNieprawda(result_fds & unwanted_fds,
                         "Expected no fds z %r to be open w child, "
                         "found %r" %
                              (unwanted_fds, result_fds & unwanted_fds))

    def test_pipe_cloexec_real_tools(self):
        qcat = support.findfile("qcat.py", subdir="subprocessdata")
        qgrep = support.findfile("qgrep.py", subdir="subprocessdata")

        subdata = b'zxcvbn'
        data = subdata * 4 + b'\n'

        p1 = subprocess.Popen([sys.executable, qcat],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              close_fds=Nieprawda)

        p2 = subprocess.Popen([sys.executable, qgrep, subdata],
                              stdin=p1.stdout, stdout=subprocess.PIPE,
                              close_fds=Nieprawda)

        self.addCleanup(p1.wait)
        self.addCleanup(p2.wait)
        def kill_p1():
            spróbuj:
                p1.terminate()
            wyjąwszy ProcessLookupError:
                dalej
        def kill_p2():
            spróbuj:
                p2.terminate()
            wyjąwszy ProcessLookupError:
                dalej
        self.addCleanup(kill_p1)
        self.addCleanup(kill_p2)

        p1.stdin.write(data)
        p1.stdin.close()

        readfiles, ignored1, ignored2 = select.select([p2.stdout], [], [], 10)

        self.assertPrawda(readfiles, "The child hung")
        self.assertEqual(p2.stdout.read(), data)

        p1.stdout.close()
        p2.stdout.close()

    def test_close_fds(self):
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        fds = os.pipe()
        self.addCleanup(os.close, fds[0])
        self.addCleanup(os.close, fds[1])

        open_fds = set(fds)
        # add a bunch more fds
        dla _ w range(9):
            fd = os.open(os.devnull, os.O_RDONLY)
            self.addCleanup(os.close, fd)
            open_fds.add(fd)

        dla fd w open_fds:
            os.set_inheritable(fd, Prawda)

        p = subprocess.Popen([sys.executable, fd_status],
                             stdout=subprocess.PIPE, close_fds=Nieprawda)
        output, ignored = p.communicate()
        remaining_fds = set(map(int, output.split(b',')))

        self.assertEqual(remaining_fds & open_fds, open_fds,
                         "Some fds were closed")

        p = subprocess.Popen([sys.executable, fd_status],
                             stdout=subprocess.PIPE, close_fds=Prawda)
        output, ignored = p.communicate()
        remaining_fds = set(map(int, output.split(b',')))

        self.assertNieprawda(remaining_fds & open_fds,
                         "Some fds were left open")
        self.assertIn(1, remaining_fds, "Subprocess failed")

        # Keep some of the fd's we opened open w the subprocess.
        # This tests _posixsubprocess.c's proper handling of fds_to_keep.
        fds_to_keep = set(open_fds.pop() dla _ w range(8))
        p = subprocess.Popen([sys.executable, fd_status],
                             stdout=subprocess.PIPE, close_fds=Prawda,
                             dalej_fds=())
        output, ignored = p.communicate()
        remaining_fds = set(map(int, output.split(b',')))

        self.assertNieprawda(remaining_fds & fds_to_keep & open_fds,
                         "Some fds nie w dalej_fds were left open")
        self.assertIn(1, remaining_fds, "Subprocess failed")


    @unittest.skipIf(sys.platform.startswith("freebsd") oraz
                     os.stat("/dev").st_dev == os.stat("/dev/fd").st_dev,
                     "Requires fdescfs mounted on /dev/fd on FreeBSD.")
    def test_close_fds_when_max_fd_is_lowered(self):
        """Confirm that issue21618 jest fixed (may fail under valgrind)."""
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        # This launches the meat of the test w a child process to
        # avoid messing przy the larger unittest processes maximum
        # number of file descriptors.
        #  This process launches:
        #  +--> Process that lowers its RLIMIT_NOFILE aftr setting up
        #    a bunch of high open fds above the new lower rlimit.
        #    Those are reported via stdout before launching a new
        #    process przy close_fds=Nieprawda to run the actual test:
        #    +--> The TEST: This one launches a fd_status.py
        #      subprocess przy close_fds=Prawda so we can find out if
        #      any of the fds above the lowered rlimit are still open.
        p = subprocess.Popen([sys.executable, '-c', textwrap.dedent(
        '''
        zaimportuj os, resource, subprocess, sys, textwrap
        open_fds = set()
        # Add a bunch more fds to dalej down.
        dla _ w range(40):
            fd = os.open(os.devnull, os.O_RDONLY)
            open_fds.add(fd)

        # Leave a two pairs of low ones available dla use by the
        # internal child error pipe oraz the stdout pipe.
        # We also leave 10 more open jako some Python buildbots run into
        # "too many open files" errors during the test jeżeli we do not.
        dla fd w sorted(open_fds)[:14]:
            os.close(fd)
            open_fds.remove(fd)

        dla fd w open_fds:
            #self.addCleanup(os.close, fd)
            os.set_inheritable(fd, Prawda)

        max_fd_open = max(open_fds)

        # Communicate the open_fds to the parent unittest.TestCase process.
        print(','.join(map(str, sorted(open_fds))))
        sys.stdout.flush()

        rlim_cur, rlim_max = resource.getrlimit(resource.RLIMIT_NOFILE)
        spróbuj:
            # 29 jest lower than the highest fds we are leaving open.
            resource.setrlimit(resource.RLIMIT_NOFILE, (29, rlim_max))
            # Launch a new Python interpreter przy our low fd rlim_cur that
            # inherits open fds above that limit.  It then uses subprocess
            # przy close_fds=Prawda to get a report of open fds w the child.
            # An explicit list of fds to check jest dalejed to fd_status.py as
            # letting fd_status rely on its default logic would miss the
            # fds above rlim_cur jako it normally only checks up to that limit.
            subprocess.Popen(
                [sys.executable, '-c',
                 textwrap.dedent("""
                     zaimportuj subprocess, sys
                     subprocess.Popen([sys.executable, %r] +
                                      [str(x) dla x w range({max_fd})],
                                      close_fds=Prawda).wait()
                     """.format(max_fd=max_fd_open+1))],
                close_fds=Nieprawda).wait()
        w_końcu:
            resource.setrlimit(resource.RLIMIT_NOFILE, (rlim_cur, rlim_max))
        ''' % fd_status)], stdout=subprocess.PIPE)

        output, unused_stderr = p.communicate()
        output_lines = output.splitlines()
        self.assertEqual(len(output_lines), 2,
                         msg="expected exactly two lines of output:\n%r" % output)
        opened_fds = set(map(int, output_lines[0].strip().split(b',')))
        remaining_fds = set(map(int, output_lines[1].strip().split(b',')))

        self.assertNieprawda(remaining_fds & opened_fds,
                         msg="Some fds were left open.")


    # Mac OS X Tiger (10.4) has a kernel bug: sometimes, the file
    # descriptor of a pipe closed w the parent process jest valid w the
    # child process according to fstat(), but the mode of the file
    # descriptor jest invalid, oraz read albo write podnieś an error.
    @support.requires_mac_ver(10, 5)
    def test_pass_fds(self):
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        open_fds = set()

        dla x w range(5):
            fds = os.pipe()
            self.addCleanup(os.close, fds[0])
            self.addCleanup(os.close, fds[1])
            os.set_inheritable(fds[0], Prawda)
            os.set_inheritable(fds[1], Prawda)
            open_fds.update(fds)

        dla fd w open_fds:
            p = subprocess.Popen([sys.executable, fd_status],
                                 stdout=subprocess.PIPE, close_fds=Prawda,
                                 dalej_fds=(fd, ))
            output, ignored = p.communicate()

            remaining_fds = set(map(int, output.split(b',')))
            to_be_closed = open_fds - {fd}

            self.assertIn(fd, remaining_fds, "fd to be dalejed nie dalejed")
            self.assertNieprawda(remaining_fds & to_be_closed,
                             "fd to be closed dalejed")

            # dalej_fds overrides close_fds przy a warning.
            przy self.assertWarns(RuntimeWarning) jako context:
                self.assertNieprawda(subprocess.call(
                        [sys.executable, "-c", "zaimportuj sys; sys.exit(0)"],
                        close_fds=Nieprawda, dalej_fds=(fd, )))
            self.assertIn('overriding close_fds', str(context.warning))

    def test_pass_fds_inheritable(self):
        script = support.findfile("fd_status.py", subdir="subprocessdata")

        inheritable, non_inheritable = os.pipe()
        self.addCleanup(os.close, inheritable)
        self.addCleanup(os.close, non_inheritable)
        os.set_inheritable(inheritable, Prawda)
        os.set_inheritable(non_inheritable, Nieprawda)
        dalej_fds = (inheritable, non_inheritable)
        args = [sys.executable, script]
        args += list(map(str, dalej_fds))

        p = subprocess.Popen(args,
                             stdout=subprocess.PIPE, close_fds=Prawda,
                             dalej_fds=pass_fds)
        output, ignored = p.communicate()
        fds = set(map(int, output.split(b',')))

        # the inheritable file descriptor must be inherited, so its inheritable
        # flag must be set w the child process after fork() oraz before exec()
        self.assertEqual(fds, set(pass_fds), "output=%a" % output)

        # inheritable flag must nie be changed w the parent process
        self.assertEqual(os.get_inheritable(inheritable), Prawda)
        self.assertEqual(os.get_inheritable(non_inheritable), Nieprawda)

    def test_stdout_stdin_are_single_inout_fd(self):
        przy io.open(os.devnull, "r+") jako inout:
            p = subprocess.Popen([sys.executable, "-c", "zaimportuj sys; sys.exit(0)"],
                                 stdout=inout, stdin=inout)
            p.wait()

    def test_stdout_stderr_are_single_inout_fd(self):
        przy io.open(os.devnull, "r+") jako inout:
            p = subprocess.Popen([sys.executable, "-c", "zaimportuj sys; sys.exit(0)"],
                                 stdout=inout, stderr=inout)
            p.wait()

    def test_stderr_stdin_are_single_inout_fd(self):
        przy io.open(os.devnull, "r+") jako inout:
            p = subprocess.Popen([sys.executable, "-c", "zaimportuj sys; sys.exit(0)"],
                                 stderr=inout, stdin=inout)
            p.wait()

    def test_wait_when_sigchild_ignored(self):
        # NOTE: sigchild_ignore.py may nie be an effective test on all OSes.
        sigchild_ignore = support.findfile("sigchild_ignore.py",
                                           subdir="subprocessdata")
        p = subprocess.Popen([sys.executable, sigchild_ignore],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        self.assertEqual(0, p.returncode, "sigchild_ignore.py exited"
                         " non-zero przy this error:\n%s" %
                         stderr.decode('utf-8'))

    def test_select_unbuffered(self):
        # Issue #11459: bufsize=0 should really set the pipes as
        # unbuffered (and therefore let select() work properly).
        select = support.import_module("select")
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys;'
                              'sys.stdout.write("apple")'],
                             stdout=subprocess.PIPE,
                             bufsize=0)
        f = p.stdout
        self.addCleanup(f.close)
        spróbuj:
            self.assertEqual(f.read(4), b"appl")
            self.assertIn(f, select.select([f], [], [], 0.0)[0])
        w_końcu:
            p.wait()

    def test_zombie_fast_process_del(self):
        # Issue #12650: on Unix, jeżeli Popen.__del__() was called before the
        # process exited, it wouldn't be added to subprocess._active, oraz would
        # remain a zombie.
        # spawn a Popen, oraz delete its reference before it exits
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj sys, time;'
                              'time.sleep(0.2)'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        ident = id(p)
        pid = p.pid
        usuń p
        # check that p jest w the active processes list
        self.assertIn(ident, [id(o) dla o w subprocess._active])

    def test_leak_fast_process_del_killed(self):
        # Issue #12650: on Unix, jeżeli Popen.__del__() was called before the
        # process exited, oraz the process got killed by a signal, it would never
        # be removed z subprocess._active, which triggered a FD oraz memory
        # leak.
        # spawn a Popen, delete its reference oraz kill it
        p = subprocess.Popen([sys.executable, "-c",
                              'zaimportuj time;'
                              'time.sleep(3)'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        ident = id(p)
        pid = p.pid
        usuń p
        os.kill(pid, signal.SIGKILL)
        # check that p jest w the active processes list
        self.assertIn(ident, [id(o) dla o w subprocess._active])

        # let some time dla the process to exit, oraz create a new Popen: this
        # should trigger the wait() of p
        time.sleep(0.2)
        przy self.assertRaises(OSError) jako c:
            przy subprocess.Popen(['nonexisting_i_hope'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) jako proc:
                dalej
        # p should have been wait()ed on, oraz removed z the _active list
        self.assertRaises(OSError, os.waitpid, pid, 0)
        self.assertNotIn(ident, [id(o) dla o w subprocess._active])

    def test_close_fds_after_preexec(self):
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        # this FD jest used jako dup2() target by preexec_fn, oraz should be closed
        # w the child process
        fd = os.dup(1)
        self.addCleanup(os.close, fd)

        p = subprocess.Popen([sys.executable, fd_status],
                             stdout=subprocess.PIPE, close_fds=Prawda,
                             preexec_fn=lambda: os.dup2(1, fd))
        output, ignored = p.communicate()

        remaining_fds = set(map(int, output.split(b',')))

        self.assertNotIn(fd, remaining_fds)

    @support.cpython_only
    def test_fork_exec(self):
        # Issue #22290: fork_exec() must nie crash on memory allocation failure
        # albo other errors
        zaimportuj _posixsubprocess
        gc_enabled = gc.isenabled()
        spróbuj:
            # Use a preexec function oraz enable the garbage collector
            # to force fork_exec() to re-enable the garbage collector
            # on error.
            func = lambda: Nic
            gc.enable()

            executable_list = "exec"   # error: must be a sequence

            dla args, exe_list, cwd, env_list w (
                (123,      [b"exe"], Nic, [b"env"]),
                ([b"arg"], 123,      Nic, [b"env"]),
                ([b"arg"], [b"exe"], 123,  [b"env"]),
                ([b"arg"], [b"exe"], Nic, 123),
            ):
                przy self.assertRaises(TypeError):
                    _posixsubprocess.fork_exec(
                        args, exe_list,
                        Prawda, [], cwd, env_list,
                        -1, -1, -1, -1,
                        1, 2, 3, 4,
                        Prawda, Prawda, func)
        w_końcu:
            jeżeli nie gc_enabled:
                gc.disable()



@unittest.skipUnless(mswindows, "Windows specific tests")
klasa Win32ProcessTestCase(BaseTestCase):

    def test_startupinfo(self):
        # startupinfo argument
        # We uses hardcoded constants, because we do nie want to
        # depend on win32all.
        STARTF_USESHOWWINDOW = 1
        SW_MAXIMIZE = 3
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = SW_MAXIMIZE
        # Since Python jest a console process, it won't be affected
        # by wShowWindow, but the argument should be silently
        # ignored
        subprocess.call([sys.executable, "-c", "zaimportuj sys; sys.exit(0)"],
                        startupinfo=startupinfo)

    def test_creationflags(self):
        # creationflags argument
        CREATE_NEW_CONSOLE = 16
        sys.stderr.write("    a DOS box should flash briefly ...\n")
        subprocess.call(sys.executable +
                        ' -c "zaimportuj time; time.sleep(0.25)"',
                        creationflags=CREATE_NEW_CONSOLE)

    def test_invalid_args(self):
        # invalid arguments should podnieś ValueError
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "zaimportuj sys; sys.exit(47)"],
                          preexec_fn=lambda: 1)
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "zaimportuj sys; sys.exit(47)"],
                          stdout=subprocess.PIPE,
                          close_fds=Prawda)

    def test_close_fds(self):
        # close file descriptors
        rc = subprocess.call([sys.executable, "-c",
                              "zaimportuj sys; sys.exit(47)"],
                              close_fds=Prawda)
        self.assertEqual(rc, 47)

    def test_shell_sequence(self):
        # Run command through the shell (sequence)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "physalis"
        p = subprocess.Popen(["set"], shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        self.addCleanup(p.stdout.close)
        self.assertIn(b"physalis", p.stdout.read())

    def test_shell_string(self):
        # Run command through the shell (string)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "physalis"
        p = subprocess.Popen("set", shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        self.addCleanup(p.stdout.close)
        self.assertIn(b"physalis", p.stdout.read())

    def test_call_string(self):
        # call() function przy string argument on Windows
        rc = subprocess.call(sys.executable +
                             ' -c "zaimportuj sys; sys.exit(47)"')
        self.assertEqual(rc, 47)

    def _kill_process(self, method, *args):
        # Some win32 buildbot podnieśs EOFError jeżeli stdin jest inherited
        p = subprocess.Popen([sys.executable, "-c", """jeżeli 1:
                             zaimportuj sys, time
                             sys.stdout.write('x\\n')
                             sys.stdout.flush()
                             time.sleep(30)
                             """],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        # Wait dla the interpreter to be completely initialized before
        # sending any signal.
        p.stdout.read(1)
        getattr(p, method)(*args)
        _, stderr = p.communicate()
        self.assertStderrEqual(stderr, b'')
        returncode = p.wait()
        self.assertNotEqual(returncode, 0)

    def _kill_dead_process(self, method, *args):
        p = subprocess.Popen([sys.executable, "-c", """jeżeli 1:
                             zaimportuj sys, time
                             sys.stdout.write('x\\n')
                             sys.stdout.flush()
                             sys.exit(42)
                             """],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        # Wait dla the interpreter to be completely initialized before
        # sending any signal.
        p.stdout.read(1)
        # The process should end after this
        time.sleep(1)
        # This shouldn't podnieś even though the child jest now dead
        getattr(p, method)(*args)
        _, stderr = p.communicate()
        self.assertStderrEqual(stderr, b'')
        rc = p.wait()
        self.assertEqual(rc, 42)

    def test_send_signal(self):
        self._kill_process('send_signal', signal.SIGTERM)

    def test_kill(self):
        self._kill_process('kill')

    def test_terminate(self):
        self._kill_process('terminate')

    def test_send_signal_dead(self):
        self._kill_dead_process('send_signal', signal.SIGTERM)

    def test_kill_dead(self):
        self._kill_dead_process('kill')

    def test_terminate_dead(self):
        self._kill_dead_process('terminate')

klasa CommandTests(unittest.TestCase):
    def test_getoutput(self):
        self.assertEqual(subprocess.getoutput('echo xyzzy'), 'xyzzy')
        self.assertEqual(subprocess.getstatusoutput('echo xyzzy'),
                         (0, 'xyzzy'))

        # we use mkdtemp w the next line to create an empty directory
        # under our exclusive control; z that, we can invent a pathname
        # that we _know_ won't exist.  This jest guaranteed to fail.
        dir = Nic
        spróbuj:
            dir = tempfile.mkdtemp()
            name = os.path.join(dir, "foo")
            status, output = subprocess.getstatusoutput(
                ("type " jeżeli mswindows inaczej "cat ") + name)
            self.assertNotEqual(status, 0)
        w_końcu:
            jeżeli dir jest nie Nic:
                os.rmdir(dir)


@unittest.skipUnless(hasattr(selectors, 'PollSelector'),
                     "Test needs selectors.PollSelector")
klasa ProcessTestCaseNoPoll(ProcessTestCase):
    def setUp(self):
        self.orig_selector = subprocess._PopenSelector
        subprocess._PopenSelector = selectors.SelectSelector
        ProcessTestCase.setUp(self)

    def tearDown(self):
        subprocess._PopenSelector = self.orig_selector
        ProcessTestCase.tearDown(self)

    def test__all__(self):
        """Ensure that __all__ jest populated properly."""
        intentionally_excluded = set(("list2cmdline",))
        exported = set(subprocess.__all__)
        possible_exports = set()
        zaimportuj types
        dla name, value w subprocess.__dict__.items():
            jeżeli name.startswith('_'):
                kontynuuj
            jeżeli isinstance(value, (types.ModuleType,)):
                kontynuuj
            possible_exports.add(name)
        self.assertEqual(exported, possible_exports - intentionally_excluded)



@unittest.skipUnless(mswindows, "Windows-specific tests")
klasa CommandsWithSpaces (BaseTestCase):

    def setUp(self):
        super().setUp()
        f, fname = mkstemp(".py", "te st")
        self.fname = fname.lower ()
        os.write(f, b"zaimportuj sys;"
                    b"sys.stdout.write('%d %s' % (len(sys.argv), [a.lower () dla a w sys.argv]))"
        )
        os.close(f)

    def tearDown(self):
        os.remove(self.fname)
        super().tearDown()

    def with_spaces(self, *args, **kwargs):
        kwargs['stdout'] = subprocess.PIPE
        p = subprocess.Popen(*args, **kwargs)
        self.addCleanup(p.stdout.close)
        self.assertEqual(
          p.stdout.read ().decode("mbcs"),
          "2 [%r, 'ab cd']" % self.fname
        )

    def test_shell_string_with_spaces(self):
        # call() function przy string argument przy spaces on Windows
        self.with_spaces('"%s" "%s" "%s"' % (sys.executable, self.fname,
                                             "ab cd"), shell=1)

    def test_shell_sequence_with_spaces(self):
        # call() function przy sequence argument przy spaces on Windows
        self.with_spaces([sys.executable, self.fname, "ab cd"], shell=1)

    def test_noshell_string_with_spaces(self):
        # call() function przy string argument przy spaces on Windows
        self.with_spaces('"%s" "%s" "%s"' % (sys.executable, self.fname,
                             "ab cd"))

    def test_noshell_sequence_with_spaces(self):
        # call() function przy sequence argument przy spaces on Windows
        self.with_spaces([sys.executable, self.fname, "ab cd"])


klasa ContextManagerTests(BaseTestCase):

    def test_pipe(self):
        przy subprocess.Popen([sys.executable, "-c",
                               "zaimportuj sys;"
                               "sys.stdout.write('stdout');"
                               "sys.stderr.write('stderr');"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) jako proc:
            self.assertEqual(proc.stdout.read(), b"stdout")
            self.assertStderrEqual(proc.stderr.read(), b"stderr")

        self.assertPrawda(proc.stdout.closed)
        self.assertPrawda(proc.stderr.closed)

    def test_returncode(self):
        przy subprocess.Popen([sys.executable, "-c",
                               "zaimportuj sys; sys.exit(100)"]) jako proc:
            dalej
        # __exit__ calls wait(), so the returncode should be set
        self.assertEqual(proc.returncode, 100)

    def test_communicate_stdin(self):
        przy subprocess.Popen([sys.executable, "-c",
                              "zaimportuj sys;"
                              "sys.exit(sys.stdin.read() == 'context')"],
                             stdin=subprocess.PIPE) jako proc:
            proc.communicate(b"context")
            self.assertEqual(proc.returncode, 1)

    def test_invalid_args(self):
        przy self.assertRaises(FileNotFoundError) jako c:
            przy subprocess.Popen(['nonexisting_i_hope'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) jako proc:
                dalej

    def test_broken_pipe_cleanup(self):
        """Broken pipe error should nie prevent wait() (Issue 21619)"""
        proc = subprocess.Popen([sys.executable, '-c', 'pass'],
                                stdin=subprocess.PIPE,
                                bufsize=support.PIPE_MAX_SIZE*2)
        proc = proc.__enter__()
        # Prepare to send enough data to overflow any OS pipe buffering oraz
        # guarantee a broken pipe error. Data jest held w BufferedWriter
        # buffer until closed.
        proc.stdin.write(b'x' * support.PIPE_MAX_SIZE)
        self.assertIsNic(proc.returncode)
        # EPIPE expected under POSIX; EINVAL under Windows
        self.assertRaises(OSError, proc.__exit__, Nic, Nic, Nic)
        self.assertEqual(proc.returncode, 0)
        self.assertPrawda(proc.stdin.closed)


def test_main():
    unit_tests = (ProcessTestCase,
                  POSIXProcessTestCase,
                  Win32ProcessTestCase,
                  CommandTests,
                  ProcessTestCaseNoPoll,
                  CommandsWithSpaces,
                  ContextManagerTests,
                  RunFuncTestCase,
                  )

    support.run_unittest(*unit_tests)
    support.reap_children()

jeżeli __name__ == "__main__":
    unittest.main()
