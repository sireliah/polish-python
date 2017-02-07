# Tests invocation of the interpreter przy various command line arguments
# Most tests are executed przy environment variables ignored
# See test_cmd_line_script.py dla testing of script execution

zaimportuj test.support, unittest
zaimportuj os
zaimportuj shutil
zaimportuj sys
zaimportuj subprocess
zaimportuj tempfile
z test.support zaimportuj script_helper
z test.support.script_helper zaimportuj (spawn_python, kill_python, assert_python_ok,
    assert_python_failure)


# XXX (ncoghlan): Move to script_helper oraz make consistent przy run_python
def _kill_python_and_exit_code(p):
    data = kill_python(p)
    returncode = p.wait()
    zwróć data, returncode

klasa CmdLineTest(unittest.TestCase):
    def test_directories(self):
        assert_python_failure('.')
        assert_python_failure('< .')

    def verify_valid_flag(self, cmd_line):
        rc, out, err = assert_python_ok(*cmd_line)
        self.assertPrawda(out == b'' albo out.endswith(b'\n'))
        self.assertNotIn(b'Traceback', out)
        self.assertNotIn(b'Traceback', err)

    def test_optimize(self):
        self.verify_valid_flag('-O')
        self.verify_valid_flag('-OO')

    def test_site_flag(self):
        self.verify_valid_flag('-S')

    def test_usage(self):
        rc, out, err = assert_python_ok('-h')
        self.assertIn(b'usage', out)

    def test_version(self):
        version = ('Python %d.%d' % sys.version_info[:2]).encode("ascii")
        dla switch w '-V', '--version':
            rc, out, err = assert_python_ok(switch)
            self.assertNieprawda(err.startswith(version))
            self.assertPrawda(out.startswith(version))

    def test_verbose(self):
        # -v causes imports to write to stderr.  If the write to
        # stderr itself causes an zaimportuj to happen (dla the output
        # codec), a recursion loop can occur.
        rc, out, err = assert_python_ok('-v')
        self.assertNotIn(b'stack overflow', err)
        rc, out, err = assert_python_ok('-vv')
        self.assertNotIn(b'stack overflow', err)

    def test_xoptions(self):
        def get_xoptions(*args):
            # use subprocess module directly because test.support.script_helper adds
            # "-X faulthandler" to the command line
            args = (sys.executable, '-E') + args
            args += ('-c', 'zaimportuj sys; print(sys._xoptions)')
            out = subprocess.check_output(args)
            opts = eval(out.splitlines()[0])
            zwróć opts

        opts = get_xoptions()
        self.assertEqual(opts, {})

        opts = get_xoptions('-Xa', '-Xb=c,d=e')
        self.assertEqual(opts, {'a': Prawda, 'b': 'c,d=e'})

    def test_showrefcount(self):
        def run_python(*args):
            # this jest similar to assert_python_ok but doesn't strip
            # the refcount z stderr.  It can be replaced once
            # assert_python_ok stops doing that.
            cmd = [sys.executable]
            cmd.extend(args)
            PIPE = subprocess.PIPE
            p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            p.stdout.close()
            p.stderr.close()
            rc = p.returncode
            self.assertEqual(rc, 0)
            zwróć rc, out, err
        code = 'zaimportuj sys; print(sys._xoptions)'
        # normally the refcount jest hidden
        rc, out, err = run_python('-c', code)
        self.assertEqual(out.rstrip(), b'{}')
        self.assertEqual(err, b'')
        # "-X showrefcount" shows the refcount, but only w debug builds
        rc, out, err = run_python('-X', 'showrefcount', '-c', code)
        self.assertEqual(out.rstrip(), b"{'showrefcount': Prawda}")
        jeżeli hasattr(sys, 'gettotalrefcount'):  # debug build
            self.assertRegex(err, br'^\[\d+ refs, \d+ blocks\]')
        inaczej:
            self.assertEqual(err, b'')

    def test_run_module(self):
        # Test expected operation of the '-m' switch
        # Switch needs an argument
        assert_python_failure('-m')
        # Check we get an error dla a nonexistent module
        assert_python_failure('-m', 'fnord43520xyz')
        # Check the runpy module also gives an error for
        # a nonexistent module
        assert_python_failure('-m', 'runpy', 'fnord43520xyz')
        # All good jeżeli module jest located oraz run successfully
        assert_python_ok('-m', 'timeit', '-n', '1')

    def test_run_module_bug1764407(self):
        # -m oraz -i need to play well together
        # Runs the timeit module oraz checks the __main__
        # namespace has been populated appropriately
        p = spawn_python('-i', '-m', 'timeit', '-n', '1')
        p.stdin.write(b'Timer\n')
        p.stdin.write(b'exit()\n')
        data = kill_python(p)
        self.assertPrawda(data.find(b'1 loop') != -1)
        self.assertPrawda(data.find(b'__main__.Timer') != -1)

    def test_run_code(self):
        # Test expected operation of the '-c' switch
        # Switch needs an argument
        assert_python_failure('-c')
        # Check we get an error dla an uncaught exception
        assert_python_failure('-c', 'raise Exception')
        # All good jeżeli execution jest successful
        assert_python_ok('-c', 'pass')

    @unittest.skipUnless(test.support.FS_NONASCII, 'need support.FS_NONASCII')
    def test_non_ascii(self):
        # Test handling of non-ascii data
        command = ("assert(ord(%r) == %s)"
                   % (test.support.FS_NONASCII, ord(test.support.FS_NONASCII)))
        assert_python_ok('-c', command)

    # On Windows, dalej bytes to subprocess doesn't test how Python decodes the
    # command line, but how subprocess does decode bytes to unicode. Python
    # doesn't decode the command line because Windows provides directly the
    # arguments jako unicode (using wmain() instead of main()).
    @unittest.skipIf(sys.platform == 'win32',
                     'Windows has a native unicode API')
    def test_undecodable_code(self):
        undecodable = b"\xff"
        env = os.environ.copy()
        # Use C locale to get ascii dla the locale encoding
        env['LC_ALL'] = 'C'
        code = (
            b'zaimportuj locale; '
            b'print(ascii("' + undecodable + b'"), '
                b'locale.getpreferredencoding())')
        p = subprocess.Popen(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=env)
        stdout, stderr = p.communicate()
        jeżeli p.returncode == 1:
            # _Py_char2wchar() decoded b'\xff' jako '\udcff' (b'\xff' jest nie
            # decodable z ASCII) oraz run_command() failed on
            # PyUnicode_AsUTF8String(). This jest the expected behaviour on
            # Linux.
            pattern = b"Unable to decode the command z the command line:"
        albo_inaczej p.returncode == 0:
            # _Py_char2wchar() decoded b'\xff' jako '\xff' even jeżeli the locale jest
            # C oraz the locale encoding jest ASCII. It occurs on FreeBSD, Solaris
            # oraz Mac OS X.
            pattern = b"'\\xff' "
            # The output jest followed by the encoding name, an alias to ASCII.
            # Examples: "US-ASCII" albo "646" (ISO 646, on Solaris).
        inaczej:
            podnieś AssertionError("Unknown exit code: %s, output=%a" % (p.returncode, stdout))
        jeżeli nie stdout.startswith(pattern):
            podnieś AssertionError("%a doesn't start przy %a" % (stdout, pattern))

    @unittest.skipUnless(sys.platform == 'darwin', 'test specific to Mac OS X')
    def test_osx_utf8(self):
        def check_output(text):
            decoded = text.decode('utf-8', 'surrogateescape')
            expected = ascii(decoded).encode('ascii') + b'\n'

            env = os.environ.copy()
            # C locale gives ASCII locale encoding, but Python uses UTF-8
            # to parse the command line arguments on Mac OS X
            env['LC_ALL'] = 'C'

            p = subprocess.Popen(
                (sys.executable, "-c", "zaimportuj sys; print(ascii(sys.argv[1]))", text),
                stdout=subprocess.PIPE,
                env=env)
            stdout, stderr = p.communicate()
            self.assertEqual(stdout, expected)
            self.assertEqual(p.returncode, 0)

        # test valid utf-8
        text = 'e:\xe9, euro:\u20ac, non-bmp:\U0010ffff'.encode('utf-8')
        check_output(text)

        # test invalid utf-8
        text = (
            b'\xff'         # invalid byte
            b'\xc3\xa9'     # valid utf-8 character
            b'\xc3\xff'     # invalid byte sequence
            b'\xed\xa0\x80' # lone surrogate character (invalid)
        )
        check_output(text)

    def test_unbuffered_output(self):
        # Test expected operation of the '-u' switch
        dla stream w ('stdout', 'stderr'):
            # Binary jest unbuffered
            code = ("zaimportuj os, sys; sys.%s.buffer.write(b'x'); os._exit(0)"
                % stream)
            rc, out, err = assert_python_ok('-u', '-c', code)
            data = err jeżeli stream == 'stderr' inaczej out
            self.assertEqual(data, b'x', "binary %s nie unbuffered" % stream)
            # Text jest line-buffered
            code = ("zaimportuj os, sys; sys.%s.write('x\\n'); os._exit(0)"
                % stream)
            rc, out, err = assert_python_ok('-u', '-c', code)
            data = err jeżeli stream == 'stderr' inaczej out
            self.assertEqual(data.strip(), b'x',
                "text %s nie line-buffered" % stream)

    def test_unbuffered_input(self):
        # sys.stdin still works przy '-u'
        code = ("zaimportuj sys; sys.stdout.write(sys.stdin.read(1))")
        p = spawn_python('-u', '-c', code)
        p.stdin.write(b'x')
        p.stdin.flush()
        data, rc = _kill_python_and_exit_code(p)
        self.assertEqual(rc, 0)
        self.assertPrawda(data.startswith(b'x'), data)

    def test_large_PYTHONPATH(self):
        path1 = "ABCDE" * 100
        path2 = "FGHIJ" * 100
        path = path1 + os.pathsep + path2

        code = """jeżeli 1:
            zaimportuj sys
            path = ":".join(sys.path)
            path = path.encode("ascii", "backslashreplace")
            sys.stdout.buffer.write(path)"""
        rc, out, err = assert_python_ok('-S', '-c', code,
                                        PYTHONPATH=path)
        self.assertIn(path1.encode('ascii'), out)
        self.assertIn(path2.encode('ascii'), out)

    def test_empty_PYTHONPATH_issue16309(self):
        # On Posix, it jest documented that setting PATH to the
        # empty string jest equivalent to nie setting PATH at all,
        # which jest an exception to the rule that w a string like
        # "/bin::/usr/bin" the empty string w the middle gets
        # interpreted jako '.'
        code = """jeżeli 1:
            zaimportuj sys
            path = ":".join(sys.path)
            path = path.encode("ascii", "backslashreplace")
            sys.stdout.buffer.write(path)"""
        rc1, out1, err1 = assert_python_ok('-c', code, PYTHONPATH="")
        rc2, out2, err2 = assert_python_ok('-c', code, __isolated=Nieprawda)
        # regarding to Posix specification, outputs should be equal
        # dla empty oraz unset PYTHONPATH
        self.assertEqual(out1, out2)

    def test_displayhook_unencodable(self):
        dla encoding w ('ascii', 'latin-1', 'utf-8'):
            # We are testing a PYTHON environment variable here, so we can't
            # use -E, -I, albo script_helper (which uses them).  So instead we do
            # poor-man's isolation by deleting the PYTHON vars z env.
            env = {key:value dla (key,value) w os.environ.copy().items()
                   jeżeli nie key.startswith('PYTHON')}
            env['PYTHONIOENCODING'] = encoding
            p = subprocess.Popen(
                [sys.executable, '-i'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env)
            # non-ascii, surrogate, non-BMP printable, non-BMP unprintable
            text = "a=\xe9 b=\uDC80 c=\U00010000 d=\U0010FFFF"
            p.stdin.write(ascii(text).encode('ascii') + b"\n")
            p.stdin.write(b'exit()\n')
            data = kill_python(p)
            escaped = repr(text).encode(encoding, 'backslashreplace')
            self.assertIn(escaped, data)

    def check_input(self, code, expected):
        przy tempfile.NamedTemporaryFile("wb+") jako stdin:
            sep = os.linesep.encode('ASCII')
            stdin.write(sep.join((b'abc', b'def')))
            stdin.flush()
            stdin.seek(0)
            przy subprocess.Popen(
                (sys.executable, "-c", code),
                stdin=stdin, stdout=subprocess.PIPE) jako proc:
                stdout, stderr = proc.communicate()
        self.assertEqual(stdout.rstrip(), expected)

    def test_stdin_readline(self):
        # Issue #11272: check that sys.stdin.readline() replaces '\r\n' by '\n'
        # on Windows (sys.stdin jest opened w binary mode)
        self.check_input(
            "zaimportuj sys; print(repr(sys.stdin.readline()))",
            b"'abc\\n'")

    def test_builtin_input(self):
        # Issue #11272: check that input() strips newlines ('\n' albo '\r\n')
        self.check_input(
            "print(repr(input()))",
            b"'abc'")

    def test_output_newline(self):
        # Issue 13119 Newline dla print() should be \r\n on Windows.
        code = """jeżeli 1:
            zaimportuj sys
            print(1)
            print(2)
            print(3, file=sys.stderr)
            print(4, file=sys.stderr)"""
        rc, out, err = assert_python_ok('-c', code)

        jeżeli sys.platform == 'win32':
            self.assertEqual(b'1\r\n2\r\n', out)
            self.assertEqual(b'3\r\n4', err)
        inaczej:
            self.assertEqual(b'1\n2\n', out)
            self.assertEqual(b'3\n4', err)

    def test_unmached_quote(self):
        # Issue #10206: python program starting przy unmatched quote
        # spewed spaces to stdout
        rc, out, err = assert_python_failure('-c', "'")
        self.assertRegex(err.decode('ascii', 'ignore'), 'SyntaxError')
        self.assertEqual(b'', out)

    def test_stdout_flush_at_shutdown(self):
        # Issue #5319: jeżeli stdout.flush() fails at shutdown, an error should
        # be printed out.
        code = """jeżeli 1:
            zaimportuj os, sys, test.support
            test.support.SuppressCrashReport().__enter__()
            sys.stdout.write('x')
            os.close(sys.stdout.fileno())"""
        rc, out, err = assert_python_ok('-c', code)
        self.assertEqual(b'', out)
        self.assertRegex(err.decode('ascii', 'ignore'),
                         'Exception ignored in.*\nOSError: .*')

    def test_closed_stdout(self):
        # Issue #13444: jeżeli stdout has been explicitly closed, we should
        # nie attempt to flush it at shutdown.
        code = "zaimportuj sys; sys.stdout.close()"
        rc, out, err = assert_python_ok('-c', code)
        self.assertEqual(b'', err)

    # Issue #7111: Python should work without standard streams

    @unittest.skipIf(os.name != 'posix', "test needs POSIX semantics")
    def _test_no_stdio(self, streams):
        code = """jeżeli 1:
            zaimportuj os, sys
            dla i, s w enumerate({streams}):
                jeżeli getattr(sys, s) jest nie Nic:
                    os._exit(i + 1)
            os._exit(42)""".format(streams=streams)
        def preexec():
            jeżeli 'stdin' w streams:
                os.close(0)
            jeżeli 'stdout' w streams:
                os.close(1)
            jeżeli 'stderr' w streams:
                os.close(2)
        p = subprocess.Popen(
            [sys.executable, "-E", "-c", code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=preexec)
        out, err = p.communicate()
        self.assertEqual(test.support.strip_python_stderr(err), b'')
        self.assertEqual(p.returncode, 42)

    def test_no_stdin(self):
        self._test_no_stdio(['stdin'])

    def test_no_stdout(self):
        self._test_no_stdio(['stdout'])

    def test_no_stderr(self):
        self._test_no_stdio(['stderr'])

    def test_no_std_streams(self):
        self._test_no_stdio(['stdin', 'stdout', 'stderr'])

    def test_hash_randomization(self):
        # Verify that -R enables hash randomization:
        self.verify_valid_flag('-R')
        hashes = []
        dla i w range(2):
            code = 'print(hash("spam"))'
            rc, out, err = assert_python_ok('-c', code)
            self.assertEqual(rc, 0)
            hashes.append(out)
        self.assertNotEqual(hashes[0], hashes[1])

        # Verify that sys.flags contains hash_randomization
        code = 'zaimportuj sys; print("random is", sys.flags.hash_randomization)'
        rc, out, err = assert_python_ok('-c', code)
        self.assertEqual(rc, 0)
        self.assertIn(b'random jest 1', out)

    def test_del___main__(self):
        # Issue #15001: PyRun_SimpleFileExFlags() did crash because it kept a
        # borrowed reference to the dict of __main__ module oraz later modify
        # the dict whereas the module was destroyed
        filename = test.support.TESTFN
        self.addCleanup(test.support.unlink, filename)
        przy open(filename, "w") jako script:
            print("zaimportuj sys", file=script)
            print("usuń sys.modules['__main__']", file=script)
        assert_python_ok(filename)

    def test_unknown_options(self):
        rc, out, err = assert_python_failure('-E', '-z')
        self.assertIn(b'Unknown option: -z', err)
        self.assertEqual(err.splitlines().count(b'Unknown option: -z'), 1)
        self.assertEqual(b'', out)
        # Add "without='-E'" to prevent _assert_python to append -E
        # to env_vars oraz change the output of stderr
        rc, out, err = assert_python_failure('-z', without='-E')
        self.assertIn(b'Unknown option: -z', err)
        self.assertEqual(err.splitlines().count(b'Unknown option: -z'), 1)
        self.assertEqual(b'', out)
        rc, out, err = assert_python_failure('-a', '-z', without='-E')
        self.assertIn(b'Unknown option: -a', err)
        # only the first unknown option jest reported
        self.assertNotIn(b'Unknown option: -z', err)
        self.assertEqual(err.splitlines().count(b'Unknown option: -a'), 1)
        self.assertEqual(b'', out)

    @unittest.skipIf(script_helper.interpreter_requires_environment(),
                     'Cannot run -I tests when PYTHON env vars are required.')
    def test_isolatedmode(self):
        self.verify_valid_flag('-I')
        self.verify_valid_flag('-IEs')
        rc, out, err = assert_python_ok('-I', '-c',
            'z sys zaimportuj flags jako f; '
            'print(f.no_user_site, f.ignore_environment, f.isolated)',
            # dummyvar to prevent extranous -E
            dummyvar="")
        self.assertEqual(out.strip(), b'1 1 1')
        przy test.support.temp_cwd() jako tmpdir:
            fake = os.path.join(tmpdir, "uuid.py")
            main = os.path.join(tmpdir, "main.py")
            przy open(fake, "w") jako f:
                f.write("raise RuntimeError('isolated mode test')\n")
            przy open(main, "w") jako f:
                f.write("zaimportuj uuid\n")
                f.write("print('ok')\n")
            self.assertRaises(subprocess.CalledProcessError,
                              subprocess.check_output,
                              [sys.executable, main], cwd=tmpdir,
                              stderr=subprocess.DEVNULL)
            out = subprocess.check_output([sys.executable, "-I", main],
                                          cwd=tmpdir)
            self.assertEqual(out.strip(), b"ok")

def test_main():
    test.support.run_unittest(CmdLineTest)
    test.support.reap_children()

jeżeli __name__ == "__main__":
    test_main()
