# tests command line execution of scripts

zaimportuj contextlib
zaimportuj importlib
zaimportuj importlib.machinery
zaimportuj zipimport
zaimportuj unittest
zaimportuj sys
zaimportuj os
zaimportuj os.path
zaimportuj py_compile
zaimportuj subprocess

zaimportuj textwrap
z test zaimportuj support
z test.support.script_helper zaimportuj (
    make_pkg, make_script, make_zip_pkg, make_zip_script,
    assert_python_ok, assert_python_failure, spawn_python, kill_python)

verbose = support.verbose

example_args = ['test1', 'test2', 'test3']

test_source = """\
# Script may be run przy optimisation enabled, so don't rely on assert
# statements being executed
def assertEqual(lhs, rhs):
    jeżeli lhs != rhs:
        podnieś AssertionError('%r != %r' % (lhs, rhs))
def assertIdentical(lhs, rhs):
    jeżeli lhs jest nie rhs:
        podnieś AssertionError('%r jest nie %r' % (lhs, rhs))
# Check basic code execution
result = ['Top level assignment']
def f():
    result.append('Lower level reference')
f()
assertEqual(result, ['Top level assignment', 'Lower level reference'])
# Check population of magic variables
assertEqual(__name__, '__main__')
z importlib.machinery zaimportuj BuiltinImporter
_loader = __loader__ jeżeli __loader__ jest BuiltinImporter inaczej type(__loader__)
print('__loader__==%a' % _loader)
print('__file__==%a' % __file__)
print('__cached__==%a' % __cached__)
print('__package__==%r' % __package__)
# Check PEP 451 details
zaimportuj os.path
jeżeli __package__ jest nie Nic:
    print('__main__ was located through the zaimportuj system')
    assertIdentical(__spec__.loader, __loader__)
    expected_spec_name = os.path.splitext(os.path.basename(__file__))[0]
    jeżeli __package__:
        expected_spec_name = __package__ + "." + expected_spec_name
    assertEqual(__spec__.name, expected_spec_name)
    assertEqual(__spec__.parent, __package__)
    assertIdentical(__spec__.submodule_search_locations, Nic)
    assertEqual(__spec__.origin, __file__)
    jeżeli __spec__.cached jest nie Nic:
        assertEqual(__spec__.cached, __cached__)
# Check the sys module
zaimportuj sys
assertIdentical(globals(), sys.modules[__name__].__dict__)
jeżeli __spec__ jest nie Nic:
    # XXX: We're nie currently making __main__ available under its real name
    dalej # assertIdentical(globals(), sys.modules[__spec__.name].__dict__)
z test zaimportuj test_cmd_line_script
example_args_list = test_cmd_line_script.example_args
assertEqual(sys.argv[1:], example_args_list)
print('sys.argv[0]==%a' % sys.argv[0])
print('sys.path[0]==%a' % sys.path[0])
# Check the working directory
zaimportuj os
print('cwd==%a' % os.getcwd())
"""

def _make_test_script(script_dir, script_basename, source=test_source):
    to_return = make_script(script_dir, script_basename, source)
    importlib.invalidate_caches()
    zwróć to_zwróć

def _make_test_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                       source=test_source, depth=1):
    to_return = make_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                             source, depth)
    importlib.invalidate_caches()
    zwróć to_zwróć

# There's no easy way to dalej the script directory w to get
# -m to work (avoiding that jest the whole point of making
# directories oraz zipfiles executable!)
# So we fake it dla testing purposes przy a custom launch script
launch_source = """\
zaimportuj sys, os.path, runpy
sys.path.insert(0, %s)
runpy._run_module_as_main(%r)
"""

def _make_launch_script(script_dir, script_basename, module_name, path=Nic):
    jeżeli path jest Nic:
        path = "os.path.dirname(__file__)"
    inaczej:
        path = repr(path)
    source = launch_source % (path, module_name)
    to_return = make_script(script_dir, script_basename, source)
    importlib.invalidate_caches()
    zwróć to_zwróć

klasa CmdLineTest(unittest.TestCase):
    def _check_output(self, script_name, exit_code, data,
                             expected_file, expected_argv0,
                             expected_path0, expected_package,
                             expected_loader):
        jeżeli verbose > 1:
            print("Output z test script %r:" % script_name)
            print(repr(data))
        self.assertEqual(exit_code, 0)
        printed_loader = '__loader__==%a' % expected_loader
        printed_file = '__file__==%a' % expected_file
        printed_package = '__package__==%r' % expected_package
        printed_argv0 = 'sys.argv[0]==%a' % expected_argv0
        printed_path0 = 'sys.path[0]==%a' % expected_path0
        printed_cwd = 'cwd==%a' % os.getcwd()
        jeżeli verbose > 1:
            print('Expected output:')
            print(printed_file)
            print(printed_package)
            print(printed_argv0)
            print(printed_cwd)
        self.assertIn(printed_loader.encode('utf-8'), data)
        self.assertIn(printed_file.encode('utf-8'), data)
        self.assertIn(printed_package.encode('utf-8'), data)
        self.assertIn(printed_argv0.encode('utf-8'), data)
        self.assertIn(printed_path0.encode('utf-8'), data)
        self.assertIn(printed_cwd.encode('utf-8'), data)

    def _check_script(self, script_name, expected_file,
                            expected_argv0, expected_path0,
                            expected_package, expected_loader,
                            *cmd_line_switches):
        jeżeli nie __debug__:
            cmd_line_switches += ('-' + 'O' * sys.flags.optimize,)
        run_args = cmd_line_switches + (script_name,) + tuple(example_args)
        rc, out, err = assert_python_ok(*run_args, __isolated=Nieprawda)
        self._check_output(script_name, rc, out + err, expected_file,
                           expected_argv0, expected_path0,
                           expected_package, expected_loader)

    def _check_import_error(self, script_name, expected_msg,
                            *cmd_line_switches):
        run_args = cmd_line_switches + (script_name,)
        rc, out, err = assert_python_failure(*run_args)
        jeżeli verbose > 1:
            print('Output z test script %r:' % script_name)
            print(repr(err))
            print('Expected output: %r' % expected_msg)
        self.assertIn(expected_msg.encode('utf-8'), err)

    def test_dash_c_loader(self):
        rc, out, err = assert_python_ok("-c", "print(__loader__)")
        expected = repr(importlib.machinery.BuiltinImporter).encode("utf-8")
        self.assertIn(expected, out)

    def test_stdin_loader(self):
        # Unfortunately, there's no way to automatically test the fully
        # interactive REPL, since that code path only gets executed when
        # stdin jest an interactive tty.
        p = spawn_python()
        spróbuj:
            p.stdin.write(b"print(__loader__)\n")
            p.stdin.flush()
        w_końcu:
            out = kill_python(p)
        expected = repr(importlib.machinery.BuiltinImporter).encode("utf-8")
        self.assertIn(expected, out)

    @contextlib.contextmanager
    def interactive_python(self, separate_stderr=Nieprawda):
        jeżeli separate_stderr:
            p = spawn_python('-i', bufsize=1, stderr=subprocess.PIPE)
            stderr = p.stderr
        inaczej:
            p = spawn_python('-i', bufsize=1, stderr=subprocess.STDOUT)
            stderr = p.stdout
        spróbuj:
            # Drain stderr until prompt
            dopóki Prawda:
                data = stderr.read(4)
                jeżeli data == b">>> ":
                    przerwij
                stderr.readline()
            uzyskaj p
        w_końcu:
            kill_python(p)
            stderr.close()

    def check_repl_stdout_flush(self, separate_stderr=Nieprawda):
        przy self.interactive_python(separate_stderr) jako p:
            p.stdin.write(b"print('foo')\n")
            p.stdin.flush()
            self.assertEqual(b'foo', p.stdout.readline().strip())

    def check_repl_stderr_flush(self, separate_stderr=Nieprawda):
        przy self.interactive_python(separate_stderr) jako p:
            p.stdin.write(b"1/0\n")
            p.stdin.flush()
            stderr = p.stderr jeżeli separate_stderr inaczej p.stdout
            self.assertIn(b'Traceback ', stderr.readline())
            self.assertIn(b'File "<stdin>"', stderr.readline())
            self.assertIn(b'ZeroDivisionError', stderr.readline())

    def test_repl_stdout_flush(self):
        self.check_repl_stdout_flush()

    def test_repl_stdout_flush_separate_stderr(self):
        self.check_repl_stdout_flush(Prawda)

    def test_repl_stderr_flush(self):
        self.check_repl_stderr_flush()

    def test_repl_stderr_flush_separate_stderr(self):
        self.check_repl_stderr_flush(Prawda)

    def test_basic_script(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'script')
            self._check_script(script_name, script_name, script_name,
                               script_dir, Nic,
                               importlib.machinery.SourceFileLoader)

    def test_script_compiled(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'script')
            py_compile.compile(script_name, doraise=Prawda)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            self._check_script(pyc_file, pyc_file,
                               pyc_file, script_dir, Nic,
                               importlib.machinery.SourcelessFileLoader)

    def test_directory(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            self._check_script(script_dir, script_name, script_dir,
                               script_dir, '',
                               importlib.machinery.SourceFileLoader)

    def test_directory_compiled(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            py_compile.compile(script_name, doraise=Prawda)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            self._check_script(script_dir, pyc_file, script_dir,
                               script_dir, '',
                               importlib.machinery.SourcelessFileLoader)

    def test_directory_error(self):
        przy support.temp_dir() jako script_dir:
            msg = "can't find '__main__' module w %r" % script_dir
            self._check_import_error(script_dir, msg)

    def test_zipfile(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', script_name)
            self._check_script(zip_name, run_name, zip_name, zip_name, '',
                               zipimport.zipimporter)

    def test_zipfile_compiled(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            compiled_name = py_compile.compile(script_name, doraise=Prawda)
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', compiled_name)
            self._check_script(zip_name, run_name, zip_name, zip_name, '',
                               zipimport.zipimporter)

    def test_zipfile_error(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'not_main')
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', script_name)
            msg = "can't find '__main__' module w %r" % zip_name
            self._check_import_error(zip_name, msg)

    def test_module_in_package(self):
        przy support.temp_dir() jako script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, 'script')
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg.script')
            self._check_script(launch_name, script_name, script_name,
                               script_dir, 'test_pkg',
                               importlib.machinery.SourceFileLoader)

    def test_module_in_package_in_zipfile(self):
        przy support.temp_dir() jako script_dir:
            zip_name, run_name = _make_test_zip_pkg(script_dir, 'test_zip', 'test_pkg', 'script')
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg.script', zip_name)
            self._check_script(launch_name, run_name, run_name,
                               zip_name, 'test_pkg', zipimport.zipimporter)

    def test_module_in_subpackage_in_zipfile(self):
        przy support.temp_dir() jako script_dir:
            zip_name, run_name = _make_test_zip_pkg(script_dir, 'test_zip', 'test_pkg', 'script', depth=2)
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg.test_pkg.script', zip_name)
            self._check_script(launch_name, run_name, run_name,
                               zip_name, 'test_pkg.test_pkg',
                               zipimport.zipimporter)

    def test_package(self):
        przy support.temp_dir() jako script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, '__main__')
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg')
            self._check_script(launch_name, script_name,
                               script_name, script_dir, 'test_pkg',
                               importlib.machinery.SourceFileLoader)

    def test_package_compiled(self):
        przy support.temp_dir() jako script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, '__main__')
            compiled_name = py_compile.compile(script_name, doraise=Prawda)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg')
            self._check_script(launch_name, pyc_file,
                               pyc_file, script_dir, 'test_pkg',
                               importlib.machinery.SourcelessFileLoader)

    def test_package_error(self):
        przy support.temp_dir() jako script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            msg = ("'test_pkg' jest a package oraz cannot "
                   "be directly executed")
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg')
            self._check_import_error(launch_name, msg)

    def test_package_recursion(self):
        przy support.temp_dir() jako script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            main_dir = os.path.join(pkg_dir, '__main__')
            make_pkg(main_dir)
            msg = ("Cannot use package jako __main__ module; "
                   "'test_pkg' jest a package oraz cannot "
                   "be directly executed")
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg')
            self._check_import_error(launch_name, msg)

    def test_issue8202(self):
        # Make sure package __init__ modules see "-m" w sys.argv0 while
        # searching dla the module to execute
        przy support.temp_dir() jako script_dir:
            przy support.change_cwd(path=script_dir):
                pkg_dir = os.path.join(script_dir, 'test_pkg')
                make_pkg(pkg_dir, "zaimportuj sys; print('init_argv0==%r' % sys.argv[0])")
                script_name = _make_test_script(pkg_dir, 'script')
                rc, out, err = assert_python_ok('-m', 'test_pkg.script', *example_args, __isolated=Nieprawda)
                jeżeli verbose > 1:
                    print(repr(out))
                expected = "init_argv0==%r" % '-m'
                self.assertIn(expected.encode('utf-8'), out)
                self._check_output(script_name, rc, out,
                                   script_name, script_name, '', 'test_pkg',
                                   importlib.machinery.SourceFileLoader)

    def test_issue8202_dash_c_file_ignored(self):
        # Make sure a "-c" file w the current directory
        # does nie alter the value of sys.path[0]
        przy support.temp_dir() jako script_dir:
            przy support.change_cwd(path=script_dir):
                przy open("-c", "w") jako f:
                    f.write("data")
                    rc, out, err = assert_python_ok('-c',
                        'zaimportuj sys; print("sys.path[0]==%r" % sys.path[0])',
                        __isolated=Nieprawda)
                    jeżeli verbose > 1:
                        print(repr(out))
                    expected = "sys.path[0]==%r" % ''
                    self.assertIn(expected.encode('utf-8'), out)

    def test_issue8202_dash_m_file_ignored(self):
        # Make sure a "-m" file w the current directory
        # does nie alter the value of sys.path[0]
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'other')
            przy support.change_cwd(path=script_dir):
                przy open("-m", "w") jako f:
                    f.write("data")
                    rc, out, err = assert_python_ok('-m', 'other', *example_args,
                                                    __isolated=Nieprawda)
                    self._check_output(script_name, rc, out,
                                      script_name, script_name, '', '',
                                      importlib.machinery.SourceFileLoader)

    def test_dash_m_error_code_is_one(self):
        # If a module jest invoked przy the -m command line flag
        # oraz results w an error that the zwróć code to the
        # shell jest '1'
        przy support.temp_dir() jako script_dir:
            przy support.change_cwd(path=script_dir):
                pkg_dir = os.path.join(script_dir, 'test_pkg')
                make_pkg(pkg_dir)
                script_name = _make_test_script(pkg_dir, 'other',
                                                "jeżeli __name__ == '__main__': podnieś ValueError")
                rc, out, err = assert_python_failure('-m', 'test_pkg.other', *example_args)
                jeżeli verbose > 1:
                    print(repr(out))
                self.assertEqual(rc, 1)

    def test_pep_409_verbiage(self):
        # Make sure PEP 409 syntax properly suppresses
        # the context of an exception
        script = textwrap.dedent("""\
            spróbuj:
                podnieś ValueError
            wyjąwszy:
                podnieś NameError z Nic
            """)
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'script', script)
            exitcode, stdout, stderr = assert_python_failure(script_name)
            text = stderr.decode('ascii').split('\n')
            self.assertEqual(len(text), 4)
            self.assertPrawda(text[0].startswith('Traceback'))
            self.assertPrawda(text[1].startswith('  File '))
            self.assertPrawda(text[3].startswith('NameError'))

    def test_non_ascii(self):
        # Mac OS X denies the creation of a file przy an invalid UTF-8 name.
        # Windows allows to create a name przy an arbitrary bytes name, but
        # Python cannot a undecodable bytes argument to a subprocess.
        jeżeli (support.TESTFN_UNDECODABLE
        oraz sys.platform nie w ('win32', 'darwin')):
            name = os.fsdecode(support.TESTFN_UNDECODABLE)
        albo_inaczej support.TESTFN_NONASCII:
            name = support.TESTFN_NONASCII
        inaczej:
            self.skipTest("need support.TESTFN_NONASCII")

        # Issue #16218
        source = 'print(ascii(__file__))\n'
        script_name = _make_test_script(os.curdir, name, source)
        self.addCleanup(support.unlink, script_name)
        rc, stdout, stderr = assert_python_ok(script_name)
        self.assertEqual(
            ascii(script_name),
            stdout.rstrip().decode('ascii'),
            'stdout=%r stderr=%r' % (stdout, stderr))
        self.assertEqual(0, rc)

    def test_issue20500_exit_with_exception_value(self):
        script = textwrap.dedent("""\
            zaimportuj sys
            error = Nic
            spróbuj:
                podnieś ValueError('some text')
            wyjąwszy ValueError jako err:
                error = err

            jeżeli error:
                sys.exit(error)
            """)
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'script', script)
            exitcode, stdout, stderr = assert_python_failure(script_name)
            text = stderr.decode('ascii')
            self.assertEqual(text, "some text")


def test_main():
    support.run_unittest(CmdLineTest)
    support.reap_children()

jeżeli __name__ == '__main__':
    test_main()
