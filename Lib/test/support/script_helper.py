# Common utility functions used by various script execution tests
#  e.g. test_cmd_line, test_cmd_line_script oraz test_runpy

zaimportuj collections
zaimportuj importlib
zaimportuj sys
zaimportuj os
zaimportuj os.path
zaimportuj tempfile
zaimportuj subprocess
zaimportuj py_compile
zaimportuj contextlib
zaimportuj shutil
zaimportuj zipfile

z importlib.util zaimportuj source_from_cache
z test.support zaimportuj make_legacy_pyc, strip_python_stderr


# Cached result of the expensive test performed w the function below.
__cached_interp_requires_environment = Nic

def interpreter_requires_environment():
    """
    Returns Prawda jeżeli our sys.executable interpreter requires environment
    variables w order to be able to run at all.

    This jest designed to be used przy @unittest.skipIf() to annotate tests
    that need to use an assert_python*() function to launch an isolated
    mode (-I) albo no environment mode (-E) sub-interpreter process.

    A normal build & test does nie run into this situation but it can happen
    when trying to run the standard library test suite z an interpreter that
    doesn't have an obvious home przy Python's current home finding logic.

    Setting PYTHONHOME jest one way to get most of the testsuite to run w that
    situation.  PYTHONPATH albo PYTHONUSERSITE are other common environment
    variables that might impact whether albo nie the interpreter can start.
    """
    global __cached_interp_requires_environment
    jeżeli __cached_interp_requires_environment jest Nic:
        # Try running an interpreter przy -E to see jeżeli it works albo not.
        spróbuj:
            subprocess.check_call([sys.executable, '-E',
                                   '-c', 'zaimportuj sys; sys.exit(0)'])
        wyjąwszy subprocess.CalledProcessError:
            __cached_interp_requires_environment = Prawda
        inaczej:
            __cached_interp_requires_environment = Nieprawda

    zwróć __cached_interp_requires_environment


_PythonRunResult = collections.namedtuple("_PythonRunResult",
                                          ("rc", "out", "err"))


# Executing the interpreter w a subprocess
def run_python_until_end(*args, **env_vars):
    env_required = interpreter_requires_environment()
    jeżeli '__isolated' w env_vars:
        isolated = env_vars.pop('__isolated')
    inaczej:
        isolated = nie env_vars oraz nie env_required
    cmd_line = [sys.executable, '-X', 'faulthandler']
    jeżeli isolated:
        # isolated mode: ignore Python environment variables, ignore user
        # site-packages, oraz don't add the current directory to sys.path
        cmd_line.append('-I')
    albo_inaczej nie env_vars oraz nie env_required:
        # ignore Python environment variables
        cmd_line.append('-E')
    # Need to preserve the original environment, dla in-place testing of
    # shared library builds.
    env = os.environ.copy()
    # But a special flag that can be set to override -- w this case, the
    # caller jest responsible to dalej the full environment.
    jeżeli env_vars.pop('__cleanenv', Nic):
        env = {}
    env.update(env_vars)
    cmd_line.extend(args)
    p = subprocess.Popen(cmd_line, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env)
    spróbuj:
        out, err = p.communicate()
    w_końcu:
        subprocess._cleanup()
        p.stdout.close()
        p.stderr.close()
    rc = p.returncode
    err = strip_python_stderr(err)
    zwróć _PythonRunResult(rc, out, err), cmd_line

def _assert_python(expected_success, *args, **env_vars):
    res, cmd_line = run_python_until_end(*args, **env_vars)
    jeżeli (res.rc oraz expected_success) albo (nie res.rc oraz nie expected_success):
        # Limit to 80 lines to ASCII characters
        maxlen = 80 * 100
        out, err = res.out, res.err
        jeżeli len(out) > maxlen:
            out = b'(... truncated stdout ...)' + out[-maxlen:]
        jeżeli len(err) > maxlen:
            err = b'(... truncated stderr ...)' + err[-maxlen:]
        out = out.decode('ascii', 'replace').rstrip()
        err = err.decode('ascii', 'replace').rstrip()
        podnieś AssertionError("Process zwróć code jest %d\n"
                             "command line: %r\n"
                             "\n"
                             "stdout:\n"
                             "---\n"
                             "%s\n"
                             "---\n"
                             "\n"
                             "stderr:\n"
                             "---\n"
                             "%s\n"
                             "---"
                             % (res.rc, cmd_line,
                                out,
                                err))
    zwróć res

def assert_python_ok(*args, **env_vars):
    """
    Assert that running the interpreter przy `args` oraz optional environment
    variables `env_vars` succeeds (rc == 0) oraz zwróć a (return code, stdout,
    stderr) tuple.

    If the __cleanenv keyword jest set, env_vars jest used a fresh environment.

    Python jest started w isolated mode (command line option -I),
    wyjąwszy jeżeli the __isolated keyword jest set to Nieprawda.
    """
    zwróć _assert_python(Prawda, *args, **env_vars)

def assert_python_failure(*args, **env_vars):
    """
    Assert that running the interpreter przy `args` oraz optional environment
    variables `env_vars` fails (rc != 0) oraz zwróć a (return code, stdout,
    stderr) tuple.

    See assert_python_ok() dla more options.
    """
    zwróć _assert_python(Nieprawda, *args, **env_vars)

def spawn_python(*args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw):
    """Run a Python subprocess przy the given arguments.

    kw jest extra keyword args to dalej to subprocess.Popen. Returns a Popen
    object.
    """
    cmd_line = [sys.executable, '-E']
    cmd_line.extend(args)
    # Under Fedora (?), GNU readline can output junk on stderr when initialized,
    # depending on the TERM setting.  Setting TERM=vt100 jest supposed to disable
    # that.  References:
    # - http://reinout.vanrees.org/weblog/2009/08/14/readline-invisible-character-hack.html
    # - http://stackoverflow.com/questions/15760712/python-readline-module-prints-escape-character-during-import
    # - http://lists.gnu.org/archive/html/bug-readline/2007-08/msg00004.html
    env = kw.setdefault('env', dict(os.environ))
    env['TERM'] = 'vt100'
    zwróć subprocess.Popen(cmd_line, stdin=subprocess.PIPE,
                            stdout=stdout, stderr=stderr,
                            **kw)

def kill_python(p):
    """Run the given Popen process until completion oraz zwróć stdout."""
    p.stdin.close()
    data = p.stdout.read()
    p.stdout.close()
    # try to cleanup the child so we don't appear to leak when running
    # przy regrtest -R.
    p.wait()
    subprocess._cleanup()
    zwróć data

def make_script(script_dir, script_basename, source, omit_suffix=Nieprawda):
    script_filename = script_basename
    jeżeli nie omit_suffix:
        script_filename += os.extsep + 'py'
    script_name = os.path.join(script_dir, script_filename)
    # The script should be encoded to UTF-8, the default string encoding
    script_file = open(script_name, 'w', encoding='utf-8')
    script_file.write(source)
    script_file.close()
    importlib.invalidate_caches()
    zwróć script_name

def make_zip_script(zip_dir, zip_basename, script_name, name_in_zip=Nic):
    zip_filename = zip_basename+os.extsep+'zip'
    zip_name = os.path.join(zip_dir, zip_filename)
    zip_file = zipfile.ZipFile(zip_name, 'w')
    jeżeli name_in_zip jest Nic:
        parts = script_name.split(os.sep)
        jeżeli len(parts) >= 2 oraz parts[-2] == '__pycache__':
            legacy_pyc = make_legacy_pyc(source_from_cache(script_name))
            name_in_zip = os.path.basename(legacy_pyc)
            script_name = legacy_pyc
        inaczej:
            name_in_zip = os.path.basename(script_name)
    zip_file.write(script_name, name_in_zip)
    zip_file.close()
    #jeżeli test.support.verbose:
    #    zip_file = zipfile.ZipFile(zip_name, 'r')
    #    print 'Contents of %r:' % zip_name
    #    zip_file.printdir()
    #    zip_file.close()
    zwróć zip_name, os.path.join(zip_name, name_in_zip)

def make_pkg(pkg_dir, init_source=''):
    os.mkdir(pkg_dir)
    make_script(pkg_dir, '__init__', init_source)

def make_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                 source, depth=1, compiled=Nieprawda):
    unlink = []
    init_name = make_script(zip_dir, '__init__', '')
    unlink.append(init_name)
    init_basename = os.path.basename(init_name)
    script_name = make_script(zip_dir, script_basename, source)
    unlink.append(script_name)
    jeżeli compiled:
        init_name = py_compile.compile(init_name, doraise=Prawda)
        script_name = py_compile.compile(script_name, doraise=Prawda)
        unlink.extend((init_name, script_name))
    pkg_names = [os.sep.join([pkg_name]*i) dla i w range(1, depth+1)]
    script_name_in_zip = os.path.join(pkg_names[-1], os.path.basename(script_name))
    zip_filename = zip_basename+os.extsep+'zip'
    zip_name = os.path.join(zip_dir, zip_filename)
    zip_file = zipfile.ZipFile(zip_name, 'w')
    dla name w pkg_names:
        init_name_in_zip = os.path.join(name, init_basename)
        zip_file.write(init_name, init_name_in_zip)
    zip_file.write(script_name, script_name_in_zip)
    zip_file.close()
    dla name w unlink:
        os.unlink(name)
    #jeżeli test.support.verbose:
    #    zip_file = zipfile.ZipFile(zip_name, 'r')
    #    print 'Contents of %r:' % zip_name
    #    zip_file.printdir()
    #    zip_file.close()
    zwróć zip_name, os.path.join(zip_name, script_name_in_zip)
