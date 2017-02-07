"""Support code dla distutils test cases."""
zaimportuj os
zaimportuj sys
zaimportuj shutil
zaimportuj tempfile
zaimportuj unittest
zaimportuj sysconfig
z copy zaimportuj deepcopy

z distutils zaimportuj log
z distutils.log zaimportuj DEBUG, INFO, WARN, ERROR, FATAL
z distutils.core zaimportuj Distribution


klasa LoggingSilencer(object):

    def setUp(self):
        super().setUp()
        self.threshold = log.set_threshold(log.FATAL)
        # catching warnings
        # when log will be replaced by logging
        # we won't need such monkey-patch anymore
        self._old_log = log.Log._log
        log.Log._log = self._log
        self.logs = []

    def tearDown(self):
        log.set_threshold(self.threshold)
        log.Log._log = self._old_log
        super().tearDown()

    def _log(self, level, msg, args):
        jeżeli level nie w (DEBUG, INFO, WARN, ERROR, FATAL):
            podnieś ValueError('%s wrong log level' % str(level))
        jeżeli nie isinstance(msg, str):
            podnieś TypeError("msg should be str, nie '%.200s'"
                            % (type(msg).__name__))
        self.logs.append((level, msg, args))

    def get_logs(self, *levels):
        def _format(msg, args):
            zwróć msg % args
        zwróć [msg % args dla level, msg, args
                w self.logs jeżeli level w levels]

    def clear_logs(self):
        self.logs = []


klasa TempdirManager(object):
    """Mix-in klasa that handles temporary directories dla test cases.

    This jest intended to be used przy unittest.TestCase.
    """

    def setUp(self):
        super().setUp()
        self.old_cwd = os.getcwd()
        self.tempdirs = []

    def tearDown(self):
        # Restore working dir, dla Solaris oraz derivatives, where rmdir()
        # on the current directory fails.
        os.chdir(self.old_cwd)
        super().tearDown()
        dopóki self.tempdirs:
            d = self.tempdirs.pop()
            shutil.rmtree(d, os.name w ('nt', 'cygwin'))

    def mkdtemp(self):
        """Create a temporary directory that will be cleaned up.

        Returns the path of the directory.
        """
        d = tempfile.mkdtemp()
        self.tempdirs.append(d)
        zwróć d

    def write_file(self, path, content='xxx'):
        """Writes a file w the given path.


        path can be a string albo a sequence.
        """
        jeżeli isinstance(path, (list, tuple)):
            path = os.path.join(*path)
        f = open(path, 'w')
        spróbuj:
            f.write(content)
        w_końcu:
            f.close()

    def create_dist(self, pkg_name='foo', **kw):
        """Will generate a test environment.

        This function creates:
         - a Distribution instance using keywords
         - a temporary directory przy a package structure

        It returns the package directory oraz the distribution
        instance.
        """
        tmp_dir = self.mkdtemp()
        pkg_dir = os.path.join(tmp_dir, pkg_name)
        os.mkdir(pkg_dir)
        dist = Distribution(attrs=kw)

        zwróć pkg_dir, dist


klasa DummyCommand:
    """Class to store options dla retrieval via set_undefined_options()."""

    def __init__(self, **kwargs):
        dla kw, val w kwargs.items():
            setattr(self, kw, val)

    def ensure_finalized(self):
        dalej


klasa EnvironGuard(object):

    def setUp(self):
        super(EnvironGuard, self).setUp()
        self.old_environ = deepcopy(os.environ)

    def tearDown(self):
        dla key, value w self.old_environ.items():
            jeżeli os.environ.get(key) != value:
                os.environ[key] = value

        dla key w tuple(os.environ.keys()):
            jeżeli key nie w self.old_environ:
                usuń os.environ[key]

        super(EnvironGuard, self).tearDown()


def copy_xxmodule_c(directory):
    """Helper dla tests that need the xxmodule.c source file.

    Example use:

        def test_compile(self):
            copy_xxmodule_c(self.tmpdir)
            self.assertIn('xxmodule.c', os.listdir(self.tmpdir))

    If the source file can be found, it will be copied to *directory*.  If not,
    the test will be skipped.  Errors during copy are nie caught.
    """
    filename = _get_xxmodule_path()
    jeżeli filename jest Nic:
        podnieś unittest.SkipTest('cannot find xxmodule.c (test must run w '
                                'the python build dir)')
    shutil.copy(filename, directory)


def _get_xxmodule_path():
    srcdir = sysconfig.get_config_var('srcdir')
    candidates = [
        # use installed copy jeżeli available
        os.path.join(os.path.dirname(__file__), 'xxmodule.c'),
        # otherwise try using copy z build directory
        os.path.join(srcdir, 'Modules', 'xxmodule.c'),
        # srcdir mysteriously can be $srcdir/Lib/distutils/tests when
        # this file jest run z its parent directory, so walk up the
        # tree to find the real srcdir
        os.path.join(srcdir, '..', '..', '..', 'Modules', 'xxmodule.c'),
    ]
    dla path w candidates:
        jeżeli os.path.exists(path):
            zwróć path


def fixup_build_ext(cmd):
    """Function needed to make build_ext tests dalej.

    When Python was built przy --enable-shared on Unix, -L. jest nie enough to
    find libpython<blah>.so, because regrtest runs w a tempdir, nie w the
    source directory where the .so lives.

    When Python was built przy w debug mode on Windows, build_ext commands
    need their debug attribute set, oraz it jest nie done automatically for
    some reason.

    This function handles both of these things.  Example use:

        cmd = build_ext(dist)
        support.fixup_build_ext(cmd)
        cmd.ensure_finalized()

    Unlike most other Unix platforms, Mac OS X embeds absolute paths
    to shared libraries into executables, so the fixup jest nie needed there.
    """
    jeżeli os.name == 'nt':
        cmd.debug = sys.executable.endswith('_d.exe')
    albo_inaczej sysconfig.get_config_var('Py_ENABLE_SHARED'):
        # To further add to the shared builds fun on Unix, we can't just add
        # library_dirs to the Extension() instance because that doesn't get
        # plumbed through to the final compiler command.
        runshared = sysconfig.get_config_var('RUNSHARED')
        jeżeli runshared jest Nic:
            cmd.library_dirs = ['.']
        inaczej:
            jeżeli sys.platform == 'darwin':
                cmd.library_dirs = []
            inaczej:
                name, equals, value = runshared.partition('=')
                cmd.library_dirs = [d dla d w value.split(os.pathsep) jeżeli d]
