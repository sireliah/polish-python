"""Supporting definitions dla the Python regression tests."""

jeżeli __name__ != 'test.support':
    podnieś ImportError('support must be imported z the test package')

zaimportuj collections.abc
zaimportuj contextlib
zaimportuj errno
zaimportuj faulthandler
zaimportuj fnmatch
zaimportuj functools
zaimportuj gc
zaimportuj importlib
zaimportuj importlib.util
zaimportuj logging.handlers
zaimportuj nntplib
zaimportuj os
zaimportuj platform
zaimportuj re
zaimportuj shutil
zaimportuj socket
zaimportuj stat
zaimportuj struct
zaimportuj subprocess
zaimportuj sys
zaimportuj sysconfig
zaimportuj tempfile
zaimportuj time
zaimportuj unittest
zaimportuj urllib.error
zaimportuj warnings

spróbuj:
    zaimportuj _thread, threading
wyjąwszy ImportError:
    _thread = Nic
    threading = Nic
spróbuj:
    zaimportuj multiprocessing.process
wyjąwszy ImportError:
    multiprocessing = Nic

spróbuj:
    zaimportuj zlib
wyjąwszy ImportError:
    zlib = Nic

spróbuj:
    zaimportuj gzip
wyjąwszy ImportError:
    gzip = Nic

spróbuj:
    zaimportuj bz2
wyjąwszy ImportError:
    bz2 = Nic

spróbuj:
    zaimportuj lzma
wyjąwszy ImportError:
    lzma = Nic

spróbuj:
    zaimportuj resource
wyjąwszy ImportError:
    resource = Nic

__all__ = [
    # globals
    "PIPE_MAX_SIZE", "verbose", "max_memuse", "use_resources", "failfast",
    # exceptions
    "Error", "TestFailed", "ResourceDenied",
    # imports
    "import_module", "import_fresh_module", "CleanImport",
    # modules
    "unload", "forget",
    # io
    "record_original_stdout", "get_original_stdout", "captured_stdout",
    "captured_stdin", "captured_stderr",
    # filesystem
    "TESTFN", "SAVEDCWD", "unlink", "rmtree", "temp_cwd", "findfile",
    "create_empty_file", "can_symlink", "fs_is_case_insensitive",
    # unittest
    "is_resource_enabled", "requires", "requires_freebsd_version",
    "requires_linux_version", "requires_mac_ver", "check_syntax_error",
    "TransientResource", "time_out", "socket_peer_reset", "ioerror_peer_reset",
    "transient_internet", "BasicTestRunner", "run_unittest", "run_doctest",
    "skip_unless_symlink", "requires_gzip", "requires_bz2", "requires_lzma",
    "bigmemtest", "bigaddrspacetest", "cpython_only", "get_attribute",
    "requires_IEEE_754", "skip_unless_xattr", "requires_zlib",
    "anticipate_failure", "load_package_tests", "detect_api_mismatch",
    # sys
    "is_jython", "check_impl_detail",
    # network
    "HOST", "IPV6_ENABLED", "find_unused_port", "bind_port", "open_urlresource",
    # processes
    'temp_umask', "reap_children",
    # logging
    "TestHandler",
    # threads
    "threading_setup", "threading_cleanup", "reap_threads", "start_threads",
    # miscellaneous
    "check_warnings", "EnvironmentVarGuard", "run_with_locale", "swap_item",
    "swap_attr", "Matcher", "set_memlimit", "SuppressCrashReport", "sortdict",
    "run_with_tz",
    ]

klasa Error(Exception):
    """Base klasa dla regression test exceptions."""

klasa TestFailed(Error):
    """Test failed."""

klasa ResourceDenied(unittest.SkipTest):
    """Test skipped because it requested a disallowed resource.

    This jest podnieśd when a test calls requires() dla a resource that
    has nie be enabled.  It jest used to distinguish between expected
    oraz unexpected skips.
    """

@contextlib.contextmanager
def _ignore_deprecated_imports(ignore=Prawda):
    """Context manager to suppress package oraz module deprecation
    warnings when importing them.

    If ignore jest Nieprawda, this context manager has no effect.
    """
    jeżeli ignore:
        przy warnings.catch_warnings():
            warnings.filterwarnings("ignore", ".+ (module|package)",
                                    DeprecationWarning)
            uzyskaj
    inaczej:
        uzyskaj


def import_module(name, deprecated=Nieprawda, *, required_on=()):
    """Import oraz zwróć the module to be tested, raising SkipTest if
    it jest nie available.

    If deprecated jest Prawda, any module albo package deprecation messages
    will be suppressed. If a module jest required on a platform but optional for
    others, set required_on to an iterable of platform prefixes which will be
    compared against sys.platform.
    """
    przy _ignore_deprecated_imports(deprecated):
        spróbuj:
            zwróć importlib.import_module(name)
        wyjąwszy ImportError jako msg:
            jeżeli sys.platform.startswith(tuple(required_on)):
                podnieś
            podnieś unittest.SkipTest(str(msg))


def _save_and_remove_module(name, orig_modules):
    """Helper function to save oraz remove a module z sys.modules

    Raise ImportError jeżeli the module can't be imported.
    """
    # try to zaimportuj the module oraz podnieś an error jeżeli it can't be imported
    jeżeli name nie w sys.modules:
        __import__(name)
        usuń sys.modules[name]
    dla modname w list(sys.modules):
        jeżeli modname == name albo modname.startswith(name + '.'):
            orig_modules[modname] = sys.modules[modname]
            usuń sys.modules[modname]

def _save_and_block_module(name, orig_modules):
    """Helper function to save oraz block a module w sys.modules

    Return Prawda jeżeli the module was w sys.modules, Nieprawda otherwise.
    """
    saved = Prawda
    spróbuj:
        orig_modules[name] = sys.modules[name]
    wyjąwszy KeyError:
        saved = Nieprawda
    sys.modules[name] = Nic
    zwróć saved


def anticipate_failure(condition):
    """Decorator to mark a test that jest known to be broken w some cases

       Any use of this decorator should have a comment identifying the
       associated tracker issue.
    """
    jeżeli condition:
        zwróć unittest.expectedFailure
    zwróć lambda f: f

def load_package_tests(pkg_dir, loader, standard_tests, pattern):
    """Generic load_tests implementation dla simple test packages.

    Most packages can implement load_tests using this function jako follows:

       def load_tests(*args):
           zwróć load_package_tests(os.path.dirname(__file__), *args)
    """
    jeżeli pattern jest Nic:
        pattern = "test*"
    top_dir = os.path.dirname(              # Lib
                  os.path.dirname(              # test
                      os.path.dirname(__file__)))   # support
    package_tests = loader.discover(start_dir=pkg_dir,
                                    top_level_dir=top_dir,
                                    pattern=pattern)
    standard_tests.addTests(package_tests)
    zwróć standard_tests


def import_fresh_module(name, fresh=(), blocked=(), deprecated=Nieprawda):
    """Import oraz zwróć a module, deliberately bypassing sys.modules.

    This function imports oraz returns a fresh copy of the named Python module
    by removing the named module z sys.modules before doing the import.
    Note that unlike reload, the original module jest nie affected by
    this operation.

    *fresh* jest an iterable of additional module names that are also removed
    z the sys.modules cache before doing the import.

    *blocked* jest an iterable of module names that are replaced przy Nic
    w the module cache during the zaimportuj to ensure that attempts to import
    them podnieś ImportError.

    The named module oraz any modules named w the *fresh* oraz *blocked*
    parameters are saved before starting the zaimportuj oraz then reinserted into
    sys.modules when the fresh zaimportuj jest complete.

    Module oraz package deprecation messages are suppressed during this import
    jeżeli *deprecated* jest Prawda.

    This function will podnieś ImportError jeżeli the named module cannot be
    imported.
    """
    # NOTE: test_heapq, test_json oraz test_warnings include extra sanity checks
    # to make sure that this utility function jest working jako expected
    przy _ignore_deprecated_imports(deprecated):
        # Keep track of modules saved dla later restoration jako well
        # jako those which just need a blocking entry removed
        orig_modules = {}
        names_to_remove = []
        _save_and_remove_module(name, orig_modules)
        spróbuj:
            dla fresh_name w fresh:
                _save_and_remove_module(fresh_name, orig_modules)
            dla blocked_name w blocked:
                jeżeli nie _save_and_block_module(blocked_name, orig_modules):
                    names_to_remove.append(blocked_name)
            fresh_module = importlib.import_module(name)
        wyjąwszy ImportError:
            fresh_module = Nic
        w_końcu:
            dla orig_name, module w orig_modules.items():
                sys.modules[orig_name] = module
            dla name_to_remove w names_to_remove:
                usuń sys.modules[name_to_remove]
        zwróć fresh_module


def get_attribute(obj, name):
    """Get an attribute, raising SkipTest jeżeli AttributeError jest podnieśd."""
    spróbuj:
        attribute = getattr(obj, name)
    wyjąwszy AttributeError:
        podnieś unittest.SkipTest("object %r has no attribute %r" % (obj, name))
    inaczej:
        zwróć attribute

verbose = 1              # Flag set to 0 by regrtest.py
use_resources = Nic     # Flag set to [] by regrtest.py
max_memuse = 0           # Disable bigmem tests (they will still be run with
                         # small sizes, to make sure they work.)
real_max_memuse = 0
failfast = Nieprawda
match_tests = Nic

# _original_stdout jest meant to hold stdout at the time regrtest began.
# This may be "the real" stdout, albo IDLE's emulation of stdout, albo whatever.
# The point jest to have some flavor of stdout the user can actually see.
_original_stdout = Nic
def record_original_stdout(stdout):
    global _original_stdout
    _original_stdout = stdout

def get_original_stdout():
    zwróć _original_stdout albo sys.stdout

def unload(name):
    spróbuj:
        usuń sys.modules[name]
    wyjąwszy KeyError:
        dalej

jeżeli sys.platform.startswith("win"):
    def _waitfor(func, pathname, waitall=Nieprawda):
        # Perform the operation
        func(pathname)
        # Now setup the wait loop
        jeżeli waitall:
            dirname = pathname
        inaczej:
            dirname, name = os.path.split(pathname)
            dirname = dirname albo '.'
        # Check dla `pathname` to be removed z the filesystem.
        # The exponential backoff of the timeout amounts to a total
        # of ~1 second after which the deletion jest probably an error
        # anyway.
        # Testing on a i7@4.3GHz shows that usually only 1 iteration jest
        # required when contention occurs.
        timeout = 0.001
        dopóki timeout < 1.0:
            # Note we are only testing dla the existence of the file(s) w
            # the contents of the directory regardless of any security albo
            # access rights.  If we have made it this far, we have sufficient
            # permissions to do that much using Python's equivalent of the
            # Windows API FindFirstFile.
            # Other Windows APIs can fail albo give incorrect results when
            # dealing przy files that are pending deletion.
            L = os.listdir(dirname)
            jeżeli nie (L jeżeli waitall inaczej name w L):
                zwróć
            # Increase the timeout oraz try again
            time.sleep(timeout)
            timeout *= 2
        warnings.warn('tests may fail, delete still pending dla ' + pathname,
                      RuntimeWarning, stacklevel=4)

    def _unlink(filename):
        _waitfor(os.unlink, filename)

    def _rmdir(dirname):
        _waitfor(os.rmdir, dirname)

    def _rmtree(path):
        def _rmtree_inner(path):
            dla name w os.listdir(path):
                fullname = os.path.join(path, name)
                spróbuj:
                    mode = os.lstat(fullname).st_mode
                wyjąwszy OSError jako exc:
                    print("support.rmtree(): os.lstat(%r) failed przy %s" % (fullname, exc),
                          file=sys.__stderr__)
                    mode = 0
                jeżeli stat.S_ISDIR(mode):
                    _waitfor(_rmtree_inner, fullname, waitall=Prawda)
                    os.rmdir(fullname)
                inaczej:
                    os.unlink(fullname)
        _waitfor(_rmtree_inner, path, waitall=Prawda)
        _waitfor(os.rmdir, path)
inaczej:
    _unlink = os.unlink
    _rmdir = os.rmdir
    _rmtree = shutil.rmtree

def unlink(filename):
    spróbuj:
        _unlink(filename)
    wyjąwszy (FileNotFoundError, NotADirectoryError):
        dalej

def rmdir(dirname):
    spróbuj:
        _rmdir(dirname)
    wyjąwszy FileNotFoundError:
        dalej

def rmtree(path):
    spróbuj:
        _rmtree(path)
    wyjąwszy FileNotFoundError:
        dalej

def make_legacy_pyc(source):
    """Move a PEP 3147/488 pyc file to its legacy pyc location.

    :param source: The file system path to the source file.  The source file
        does nie need to exist, however the PEP 3147/488 pyc file must exist.
    :return: The file system path to the legacy pyc file.
    """
    pyc_file = importlib.util.cache_from_source(source)
    up_one = os.path.dirname(os.path.abspath(source))
    legacy_pyc = os.path.join(up_one, source + 'c')
    os.rename(pyc_file, legacy_pyc)
    zwróć legacy_pyc

def forget(modname):
    """'Forget' a module was ever imported.

    This removes the module z sys.modules oraz deletes any PEP 3147/488 albo
    legacy .pyc files.
    """
    unload(modname)
    dla dirname w sys.path:
        source = os.path.join(dirname, modname + '.py')
        # It doesn't matter jeżeli they exist albo not, unlink all possible
        # combinations of PEP 3147/488 oraz legacy pyc files.
        unlink(source + 'c')
        dla opt w ('', 1, 2):
            unlink(importlib.util.cache_from_source(source, optimization=opt))

# Check whether a gui jest actually available
def _is_gui_available():
    jeżeli hasattr(_is_gui_available, 'result'):
        zwróć _is_gui_available.result
    reason = Nic
    jeżeli sys.platform.startswith('win'):
        # jeżeli Python jest running jako a service (such jako the buildbot service),
        # gui interaction may be disallowed
        zaimportuj ctypes
        zaimportuj ctypes.wintypes
        UOI_FLAGS = 1
        WSF_VISIBLE = 0x0001
        klasa USEROBJECTFLAGS(ctypes.Structure):
            _fields_ = [("fInherit", ctypes.wintypes.BOOL),
                        ("fReserved", ctypes.wintypes.BOOL),
                        ("dwFlags", ctypes.wintypes.DWORD)]
        dll = ctypes.windll.user32
        h = dll.GetProcessWindowStation()
        jeżeli nie h:
            podnieś ctypes.WinError()
        uof = USEROBJECTFLAGS()
        needed = ctypes.wintypes.DWORD()
        res = dll.GetUserObjectInformationW(h,
            UOI_FLAGS,
            ctypes.byref(uof),
            ctypes.sizeof(uof),
            ctypes.byref(needed))
        jeżeli nie res:
            podnieś ctypes.WinError()
        jeżeli nie bool(uof.dwFlags & WSF_VISIBLE):
            reason = "gui nie available (WSF_VISIBLE flag nie set)"
    albo_inaczej sys.platform == 'darwin':
        # The Aqua Tk implementations on OS X can abort the process if
        # being called w an environment where a window server connection
        # cannot be made, dla instance when invoked by a buildbot albo ssh
        # process nie running under the same user id jako the current console
        # user.  To avoid that, podnieś an exception jeżeli the window manager
        # connection jest nie available.
        z ctypes zaimportuj cdll, c_int, pointer, Structure
        z ctypes.util zaimportuj find_library

        app_services = cdll.LoadLibrary(find_library("ApplicationServices"))

        jeżeli app_services.CGMainDisplayID() == 0:
            reason = "gui tests cannot run without OS X window manager"
        inaczej:
            klasa ProcessSerialNumber(Structure):
                _fields_ = [("highLongOfPSN", c_int),
                            ("lowLongOfPSN", c_int)]
            psn = ProcessSerialNumber()
            psn_p = pointer(psn)
            jeżeli (  (app_services.GetCurrentProcess(psn_p) < 0) albo
                  (app_services.SetFrontProcess(psn_p) < 0) ):
                reason = "cannot run without OS X gui process"

    # check on every platform whether tkinter can actually do anything
    jeżeli nie reason:
        spróbuj:
            z tkinter zaimportuj Tk
            root = Tk()
            root.update()
            root.destroy()
        wyjąwszy Exception jako e:
            err_string = str(e)
            jeżeli len(err_string) > 50:
                err_string = err_string[:50] + ' [...]'
            reason = 'Tk unavailable due to {}: {}'.format(type(e).__name__,
                                                           err_string)

    _is_gui_available.reason = reason
    _is_gui_available.result = nie reason

    zwróć _is_gui_available.result

def is_resource_enabled(resource):
    """Test whether a resource jest enabled.

    Known resources are set by regrtest.py.  If nie running under regrtest.py,
    all resources are assumed enabled unless use_resources has been set.
    """
    zwróć use_resources jest Nic albo resource w use_resources

def requires(resource, msg=Nic):
    """Raise ResourceDenied jeżeli the specified resource jest nie available."""
    jeżeli resource == 'gui' oraz nie _is_gui_available():
        podnieś ResourceDenied(_is_gui_available.reason)
    jeżeli nie is_resource_enabled(resource):
        jeżeli msg jest Nic:
            msg = "Use of the %r resource nie enabled" % resource
        podnieś ResourceDenied(msg)

def _requires_unix_version(sysname, min_version):
    """Decorator raising SkipTest jeżeli the OS jest `sysname` oraz the version jest less
    than `min_version`.

    For example, @_requires_unix_version('FreeBSD', (7, 2)) podnieśs SkipTest if
    the FreeBSD version jest less than 7.2.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            jeżeli platform.system() == sysname:
                version_txt = platform.release().split('-', 1)[0]
                spróbuj:
                    version = tuple(map(int, version_txt.split('.')))
                wyjąwszy ValueError:
                    dalej
                inaczej:
                    jeżeli version < min_version:
                        min_version_txt = '.'.join(map(str, min_version))
                        podnieś unittest.SkipTest(
                            "%s version %s albo higher required, nie %s"
                            % (sysname, min_version_txt, version_txt))
            zwróć func(*args, **kw)
        wrapper.min_version = min_version
        zwróć wrapper
    zwróć decorator

def requires_freebsd_version(*min_version):
    """Decorator raising SkipTest jeżeli the OS jest FreeBSD oraz the FreeBSD version jest
    less than `min_version`.

    For example, @requires_freebsd_version(7, 2) podnieśs SkipTest jeżeli the FreeBSD
    version jest less than 7.2.
    """
    zwróć _requires_unix_version('FreeBSD', min_version)

def requires_linux_version(*min_version):
    """Decorator raising SkipTest jeżeli the OS jest Linux oraz the Linux version jest
    less than `min_version`.

    For example, @requires_linux_version(2, 6, 32) podnieśs SkipTest jeżeli the Linux
    version jest less than 2.6.32.
    """
    zwróć _requires_unix_version('Linux', min_version)

def requires_mac_ver(*min_version):
    """Decorator raising SkipTest jeżeli the OS jest Mac OS X oraz the OS X
    version jeżeli less than min_version.

    For example, @requires_mac_ver(10, 5) podnieśs SkipTest jeżeli the OS X version
    jest lesser than 10.5.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            jeżeli sys.platform == 'darwin':
                version_txt = platform.mac_ver()[0]
                spróbuj:
                    version = tuple(map(int, version_txt.split('.')))
                wyjąwszy ValueError:
                    dalej
                inaczej:
                    jeżeli version < min_version:
                        min_version_txt = '.'.join(map(str, min_version))
                        podnieś unittest.SkipTest(
                            "Mac OS X %s albo higher required, nie %s"
                            % (min_version_txt, version_txt))
            zwróć func(*args, **kw)
        wrapper.min_version = min_version
        zwróć wrapper
    zwróć decorator


# Don't use "localhost", since resolving it uses the DNS under recent
# Windows versions (see issue #18792).
HOST = "127.0.0.1"
HOSTv6 = "::1"


def find_unused_port(family=socket.AF_INET, socktype=socket.SOCK_STREAM):
    """Returns an unused port that should be suitable dla binding.  This jest
    achieved by creating a temporary socket przy the same family oraz type as
    the 'sock' parameter (default jest AF_INET, SOCK_STREAM), oraz binding it to
    the specified host address (defaults to 0.0.0.0) przy the port set to 0,
    eliciting an unused ephemeral port z the OS.  The temporary socket jest
    then closed oraz deleted, oraz the ephemeral port jest returned.

    Either this method albo bind_port() should be used dla any tests where a
    server socket needs to be bound to a particular port dla the duration of
    the test.  Which one to use depends on whether the calling code jest creating
    a python socket, albo jeżeli an unused port needs to be provided w a constructor
    albo dalejed to an external program (i.e. the -accept argument to openssl's
    s_server mode).  Always prefer bind_port() over find_unused_port() where
    possible.  Hard coded ports should *NEVER* be used.  As soon jako a server
    socket jest bound to a hard coded port, the ability to run multiple instances
    of the test simultaneously on the same host jest compromised, which makes the
    test a ticking time bomb w a buildbot environment. On Unix buildbots, this
    may simply manifest jako a failed test, which can be recovered z without
    intervention w most cases, but on Windows, the entire python process can
    completely oraz utterly wedge, requiring someone to log w to the buildbot
    oraz manually kill the affected process.

    (This jest easy to reproduce on Windows, unfortunately, oraz can be traced to
    the SO_REUSEADDR socket option having different semantics on Windows versus
    Unix/Linux.  On Unix, you can't have two AF_INET SOCK_STREAM sockets bind,
    listen oraz then accept connections on identical host/ports.  An EADDRINUSE
    OSError will be podnieśd at some point (depending on the platform oraz
    the order bind oraz listen were called on each socket).

    However, on Windows, jeżeli SO_REUSEADDR jest set on the sockets, no EADDRINUSE
    will ever be podnieśd when attempting to bind two identical host/ports. When
    accept() jest called on each socket, the second caller's process will steal
    the port z the first caller, leaving them both w an awkwardly wedged
    state where they'll no longer respond to any signals albo graceful kills, oraz
    must be forcibly killed via OpenProcess()/TerminateProcess().

    The solution on Windows jest to use the SO_EXCLUSIVEADDRUSE socket option
    instead of SO_REUSEADDR, which effectively affords the same semantics as
    SO_REUSEADDR on Unix.  Given the propensity of Unix developers w the Open
    Source world compared to Windows ones, this jest a common mistake.  A quick
    look over OpenSSL's 0.9.8g source shows that they use SO_REUSEADDR when
    openssl.exe jest called przy the 's_server' option, dla example. See
    http://bugs.python.org/issue2550 dla more info.  The following site also
    has a very thorough description about the implications of both REUSEADDR
    oraz EXCLUSIVEADDRUSE on Windows:
    http://msdn2.microsoft.com/en-us/library/ms740621(VS.85).aspx)

    XXX: although this approach jest a vast improvement on previous attempts to
    elicit unused ports, it rests heavily on the assumption that the ephemeral
    port returned to us by the OS won't immediately be dished back out to some
    other process when we close oraz delete our temporary socket but before our
    calling code has a chance to bind the returned port.  We can deal przy this
    issue if/when we come across it.
    """

    tempsock = socket.socket(family, socktype)
    port = bind_port(tempsock)
    tempsock.close()
    usuń tempsock
    zwróć port

def bind_port(sock, host=HOST):
    """Bind the socket to a free port oraz zwróć the port number.  Relies on
    ephemeral ports w order to ensure we are using an unbound port.  This jest
    important jako many tests may be running simultaneously, especially w a
    buildbot environment.  This method podnieśs an exception jeżeli the sock.family
    jest AF_INET oraz sock.type jest SOCK_STREAM, *and* the socket has SO_REUSEADDR
    albo SO_REUSEPORT set on it.  Tests should *never* set these socket options
    dla TCP/IP sockets.  The only case dla setting these options jest testing
    multicasting via multiple UDP sockets.

    Additionally, jeżeli the SO_EXCLUSIVEADDRUSE socket option jest available (i.e.
    on Windows), it will be set on the socket.  This will prevent anyone inaczej
    z bind()'ing to our host/port dla the duration of the test.
    """

    jeżeli sock.family == socket.AF_INET oraz sock.type == socket.SOCK_STREAM:
        jeżeli hasattr(socket, 'SO_REUSEADDR'):
            jeżeli sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) == 1:
                podnieś TestFailed("tests should never set the SO_REUSEADDR "   \
                                 "socket option on TCP/IP sockets!")
        jeżeli hasattr(socket, 'SO_REUSEPORT'):
            spróbuj:
                jeżeli sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 1:
                    podnieś TestFailed("tests should never set the SO_REUSEPORT "   \
                                     "socket option on TCP/IP sockets!")
            wyjąwszy OSError:
                # Python's socket module was compiled using modern headers
                # thus defining SO_REUSEPORT but this process jest running
                # under an older kernel that does nie support SO_REUSEPORT.
                dalej
        jeżeli hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)

    sock.bind((host, 0))
    port = sock.getsockname()[1]
    zwróć port

def _is_ipv6_enabled():
    """Check whether IPv6 jest enabled on this host."""
    jeżeli socket.has_ipv6:
        sock = Nic
        spróbuj:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.bind((HOSTv6, 0))
            zwróć Prawda
        wyjąwszy OSError:
            dalej
        w_końcu:
            jeżeli sock:
                sock.close()
    zwróć Nieprawda

IPV6_ENABLED = _is_ipv6_enabled()

def system_must_validate_cert(f):
    """Skip the test on TLS certificate validation failures."""
    @functools.wraps(f)
    def dec(*args, **kwargs):
        spróbuj:
            f(*args, **kwargs)
        wyjąwszy IOError jako e:
            jeżeli "CERTIFICATE_VERIFY_FAILED" w str(e):
                podnieś unittest.SkipTest("system does nie contain "
                                        "necessary certificates")
            podnieś
    zwróć dec

# A constant likely larger than the underlying OS pipe buffer size, to
# make writes blocking.
# Windows limit seems to be around 512 B, oraz many Unix kernels have a
# 64 KiB pipe buffer size albo 16 * PAGE_SIZE: take a few megs to be sure.
# (see issue #17835 dla a discussion of this number).
PIPE_MAX_SIZE = 4 * 1024 * 1024 + 1

# A constant likely larger than the underlying OS socket buffer size, to make
# writes blocking.
# The socket buffer sizes can usually be tuned system-wide (e.g. through sysctl
# on Linux), albo on a per-socket basis (SO_SNDBUF/SO_RCVBUF). See issue #18643
# dla a discussion of this number).
SOCK_MAX_SIZE = 16 * 1024 * 1024 + 1

# decorator dla skipping tests on non-IEEE 754 platforms
requires_IEEE_754 = unittest.skipUnless(
    float.__getformat__("double").startswith("IEEE"),
    "test requires IEEE 754 doubles")

requires_zlib = unittest.skipUnless(zlib, 'requires zlib')

requires_gzip = unittest.skipUnless(gzip, 'requires gzip')

requires_bz2 = unittest.skipUnless(bz2, 'requires bz2')

requires_lzma = unittest.skipUnless(lzma, 'requires lzma')

is_jython = sys.platform.startswith('java')

# Filename used dla testing
jeżeli os.name == 'java':
    # Jython disallows @ w module names
    TESTFN = '$test'
inaczej:
    TESTFN = '@test'

# Disambiguate TESTFN dla parallel testing, dopóki letting it remain a valid
# module name.
TESTFN = "{}_{}_tmp".format(TESTFN, os.getpid())

# FS_NONASCII: non-ASCII character encodable by os.fsencode(),
# albo Nic jeżeli there jest no such character.
FS_NONASCII = Nic
dla character w (
    # First try printable oraz common characters to have a readable filename.
    # For each character, the encoding list are just example of encodings able
    # to encode the character (the list jest nie exhaustive).

    # U+00E6 (Latin Small Letter Ae): cp1252, iso-8859-1
    '\u00E6',
    # U+0130 (Latin Capital Letter I With Dot Above): cp1254, iso8859_3
    '\u0130',
    # U+0141 (Latin Capital Letter L With Stroke): cp1250, cp1257
    '\u0141',
    # U+03C6 (Greek Small Letter Phi): cp1253
    '\u03C6',
    # U+041A (Cyrillic Capital Letter Ka): cp1251
    '\u041A',
    # U+05D0 (Hebrew Letter Alef): Encodable to cp424
    '\u05D0',
    # U+060C (Arabic Comma): cp864, cp1006, iso8859_6, mac_arabic
    '\u060C',
    # U+062A (Arabic Letter Teh): cp720
    '\u062A',
    # U+0E01 (Thai Character Ko Kai): cp874
    '\u0E01',

    # Then try more "special" characters. "special" because they may be
    # interpreted albo displayed differently depending on the exact locale
    # encoding oraz the font.

    # U+00A0 (No-Break Space)
    '\u00A0',
    # U+20AC (Euro Sign)
    '\u20AC',
):
    spróbuj:
        os.fsdecode(os.fsencode(character))
    wyjąwszy UnicodeError:
        dalej
    inaczej:
        FS_NONASCII = character
        przerwij

# TESTFN_UNICODE jest a non-ascii filename
TESTFN_UNICODE = TESTFN + "-\xe0\xf2\u0258\u0141\u011f"
jeżeli sys.platform == 'darwin':
    # In Mac OS X's VFS API file names are, by definition, canonically
    # decomposed Unicode, encoded using UTF-8. See QA1173:
    # http://developer.apple.com/mac/library/qa/qa2001/qa1173.html
    zaimportuj unicodedata
    TESTFN_UNICODE = unicodedata.normalize('NFD', TESTFN_UNICODE)
TESTFN_ENCODING = sys.getfilesystemencoding()

# TESTFN_UNENCODABLE jest a filename (str type) that should *not* be able to be
# encoded by the filesystem encoding (in strict mode). It can be Nic jeżeli we
# cannot generate such filename.
TESTFN_UNENCODABLE = Nic
jeżeli os.name w ('nt', 'ce'):
    # skip win32s (0) albo Windows 9x/ME (1)
    jeżeli sys.getwindowsversion().platform >= 2:
        # Different kinds of characters z various languages to minimize the
        # probability that the whole name jest encodable to MBCS (issue #9819)
        TESTFN_UNENCODABLE = TESTFN + "-\u5171\u0141\u2661\u0363\uDC80"
        spróbuj:
            TESTFN_UNENCODABLE.encode(TESTFN_ENCODING)
        wyjąwszy UnicodeEncodeError:
            dalej
        inaczej:
            print('WARNING: The filename %r CAN be encoded by the filesystem encoding (%s). '
                  'Unicode filename tests may nie be effective'
                  % (TESTFN_UNENCODABLE, TESTFN_ENCODING))
            TESTFN_UNENCODABLE = Nic
# Mac OS X denies unencodable filenames (invalid utf-8)
albo_inaczej sys.platform != 'darwin':
    spróbuj:
        # ascii oraz utf-8 cannot encode the byte 0xff
        b'\xff'.decode(TESTFN_ENCODING)
    wyjąwszy UnicodeDecodeError:
        # 0xff will be encoded using the surrogate character u+DCFF
        TESTFN_UNENCODABLE = TESTFN \
            + b'-\xff'.decode(TESTFN_ENCODING, 'surrogateescape')
    inaczej:
        # File system encoding (eg. ISO-8859-* encodings) can encode
        # the byte 0xff. Skip some unicode filename tests.
        dalej

# TESTFN_UNDECODABLE jest a filename (bytes type) that should *not* be able to be
# decoded z the filesystem encoding (in strict mode). It can be Nic jeżeli we
# cannot generate such filename (ex: the latin1 encoding can decode any byte
# sequence). On UNIX, TESTFN_UNDECODABLE can be decoded by os.fsdecode() thanks
# to the surrogateescape error handler (PEP 383), but nie z the filesystem
# encoding w strict mode.
TESTFN_UNDECODABLE = Nic
dla name w (
    # b'\xff' jest nie decodable by os.fsdecode() przy code page 932. Windows
    # accepts it to create a file albo a directory, albo don't accept to enter to
    # such directory (when the bytes name jest used). So test b'\xe7' first: it jest
    # nie decodable z cp932.
    b'\xe7w\xf0',
    # undecodable z ASCII, UTF-8
    b'\xff',
    # undecodable z iso8859-3, iso8859-6, iso8859-7, cp424, iso8859-8, cp856
    # oraz cp857
    b'\xae\xd5'
    # undecodable z UTF-8 (UNIX oraz Mac OS X)
    b'\xed\xb2\x80', b'\xed\xb4\x80',
    # undecodable z shift_jis, cp869, cp874, cp932, cp1250, cp1251, cp1252,
    # cp1253, cp1254, cp1255, cp1257, cp1258
    b'\x81\x98',
):
    spróbuj:
        name.decode(TESTFN_ENCODING)
    wyjąwszy UnicodeDecodeError:
        TESTFN_UNDECODABLE = os.fsencode(TESTFN) + name
        przerwij

jeżeli FS_NONASCII:
    TESTFN_NONASCII = TESTFN + '-' + FS_NONASCII
inaczej:
    TESTFN_NONASCII = Nic

# Save the initial cwd
SAVEDCWD = os.getcwd()

@contextlib.contextmanager
def temp_dir(path=Nic, quiet=Nieprawda):
    """Return a context manager that creates a temporary directory.

    Arguments:

      path: the directory to create temporarily.  If omitted albo Nic,
        defaults to creating a temporary directory using tempfile.mkdtemp.

      quiet: jeżeli Nieprawda (the default), the context manager podnieśs an exception
        on error.  Otherwise, jeżeli the path jest specified oraz cannot be
        created, only a warning jest issued.

    """
    dir_created = Nieprawda
    jeżeli path jest Nic:
        path = tempfile.mkdtemp()
        dir_created = Prawda
        path = os.path.realpath(path)
    inaczej:
        spróbuj:
            os.mkdir(path)
            dir_created = Prawda
        wyjąwszy OSError:
            jeżeli nie quiet:
                podnieś
            warnings.warn('tests may fail, unable to create temp dir: ' + path,
                          RuntimeWarning, stacklevel=3)
    spróbuj:
        uzyskaj path
    w_końcu:
        jeżeli dir_created:
            shutil.rmtree(path)

@contextlib.contextmanager
def change_cwd(path, quiet=Nieprawda):
    """Return a context manager that changes the current working directory.

    Arguments:

      path: the directory to use jako the temporary current working directory.

      quiet: jeżeli Nieprawda (the default), the context manager podnieśs an exception
        on error.  Otherwise, it issues only a warning oraz keeps the current
        working directory the same.

    """
    saved_dir = os.getcwd()
    spróbuj:
        os.chdir(path)
    wyjąwszy OSError:
        jeżeli nie quiet:
            podnieś
        warnings.warn('tests may fail, unable to change CWD to: ' + path,
                      RuntimeWarning, stacklevel=3)
    spróbuj:
        uzyskaj os.getcwd()
    w_końcu:
        os.chdir(saved_dir)


@contextlib.contextmanager
def temp_cwd(name='tempcwd', quiet=Nieprawda):
    """
    Context manager that temporarily creates oraz changes the CWD.

    The function temporarily changes the current working directory
    after creating a temporary directory w the current directory with
    name *name*.  If *name* jest Nic, the temporary directory jest
    created using tempfile.mkdtemp.

    If *quiet* jest Nieprawda (default) oraz it jest nie possible to
    create albo change the CWD, an error jest podnieśd.  If *quiet* jest Prawda,
    only a warning jest podnieśd oraz the original CWD jest used.

    """
    przy temp_dir(path=name, quiet=quiet) jako temp_path:
        przy change_cwd(temp_path, quiet=quiet) jako cwd_dir:
            uzyskaj cwd_dir

jeżeli hasattr(os, "umask"):
    @contextlib.contextmanager
    def temp_umask(umask):
        """Context manager that temporarily sets the process umask."""
        oldmask = os.umask(umask)
        spróbuj:
            uzyskaj
        w_końcu:
            os.umask(oldmask)

# TEST_HOME_DIR refers to the top level directory of the "test" package
# that contains Python's regression test suite
TEST_SUPPORT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_HOME_DIR = os.path.dirname(TEST_SUPPORT_DIR)

# TEST_DATA_DIR jest used jako a target download location dla remote resources
TEST_DATA_DIR = os.path.join(TEST_HOME_DIR, "data")

def findfile(filename, subdir=Nic):
    """Try to find a file on sys.path albo w the test directory.  If it jest nie
    found the argument dalejed to the function jest returned (this does nie
    necessarily signal failure; could still be the legitimate path).

    Setting *subdir* indicates a relative path to use to find the file
    rather than looking directly w the path directories.
    """
    jeżeli os.path.isabs(filename):
        zwróć filename
    jeżeli subdir jest nie Nic:
        filename = os.path.join(subdir, filename)
    path = [TEST_HOME_DIR] + sys.path
    dla dn w path:
        fn = os.path.join(dn, filename)
        jeżeli os.path.exists(fn): zwróć fn
    zwróć filename

def create_empty_file(filename):
    """Create an empty file. If the file already exists, truncate it."""
    fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    os.close(fd)

def sortdict(dict):
    "Like repr(dict), but w sorted order."
    items = sorted(dict.items())
    reprpairs = ["%r: %r" % pair dla pair w items]
    withcommas = ", ".join(reprpairs)
    zwróć "{%s}" % withcommas

def make_bad_fd():
    """
    Create an invalid file descriptor by opening oraz closing a file oraz zwróć
    its fd.
    """
    file = open(TESTFN, "wb")
    spróbuj:
        zwróć file.fileno()
    w_końcu:
        file.close()
        unlink(TESTFN)

def check_syntax_error(testcase, statement):
    testcase.assertRaises(SyntaxError, compile, statement,
                          '<test string>', 'exec')

def open_urlresource(url, *args, **kw):
    zaimportuj urllib.request, urllib.parse

    check = kw.pop('check', Nic)

    filename = urllib.parse.urlparse(url)[2].split('/')[-1] # '/': it's URL!

    fn = os.path.join(TEST_DATA_DIR, filename)

    def check_valid_file(fn):
        f = open(fn, *args, **kw)
        jeżeli check jest Nic:
            zwróć f
        albo_inaczej check(f):
            f.seek(0)
            zwróć f
        f.close()

    jeżeli os.path.exists(fn):
        f = check_valid_file(fn)
        jeżeli f jest nie Nic:
            zwróć f
        unlink(fn)

    # Verify the requirement before downloading the file
    requires('urlfetch')

    jeżeli verbose:
        print('\tfetching %s ...' % url, file=get_original_stdout())
    opener = urllib.request.build_opener()
    jeżeli gzip:
        opener.addheaders.append(('Accept-Encoding', 'gzip'))
    f = opener.open(url, timeout=15)
    jeżeli gzip oraz f.headers.get('Content-Encoding') == 'gzip':
        f = gzip.GzipFile(fileobj=f)
    spróbuj:
        przy open(fn, "wb") jako out:
            s = f.read()
            dopóki s:
                out.write(s)
                s = f.read()
    w_końcu:
        f.close()

    f = check_valid_file(fn)
    jeżeli f jest nie Nic:
        zwróć f
    podnieś TestFailed('invalid resource %r' % fn)


klasa WarningsRecorder(object):
    """Convenience wrapper dla the warnings list returned on
       entry to the warnings.catch_warnings() context manager.
    """
    def __init__(self, warnings_list):
        self._warnings = warnings_list
        self._last = 0

    def __getattr__(self, attr):
        jeżeli len(self._warnings) > self._last:
            zwróć getattr(self._warnings[-1], attr)
        albo_inaczej attr w warnings.WarningMessage._WARNING_DETAILS:
            zwróć Nic
        podnieś AttributeError("%r has no attribute %r" % (self, attr))

    @property
    def warnings(self):
        zwróć self._warnings[self._last:]

    def reset(self):
        self._last = len(self._warnings)


def _filterwarnings(filters, quiet=Nieprawda):
    """Catch the warnings, then check jeżeli all the expected
    warnings have been podnieśd oraz re-raise unexpected warnings.
    If 'quiet' jest Prawda, only re-raise the unexpected warnings.
    """
    # Clear the warning registry of the calling module
    # w order to re-raise the warnings.
    frame = sys._getframe(2)
    registry = frame.f_globals.get('__warningregistry__')
    jeżeli registry:
        registry.clear()
    przy warnings.catch_warnings(record=Prawda) jako w:
        # Set filter "always" to record all warnings.  Because
        # test_warnings swap the module, we need to look up w
        # the sys.modules dictionary.
        sys.modules['warnings'].simplefilter("always")
        uzyskaj WarningsRecorder(w)
    # Filter the recorded warnings
    reraise = list(w)
    missing = []
    dla msg, cat w filters:
        seen = Nieprawda
        dla w w reraise[:]:
            warning = w.message
            # Filter out the matching messages
            jeżeli (re.match(msg, str(warning), re.I) oraz
                issubclass(warning.__class__, cat)):
                seen = Prawda
                reraise.remove(w)
        jeżeli nie seen oraz nie quiet:
            # This filter caught nothing
            missing.append((msg, cat.__name__))
    jeżeli reraise:
        podnieś AssertionError("unhandled warning %s" % reraise[0])
    jeżeli missing:
        podnieś AssertionError("filter (%r, %s) did nie catch any warning" %
                             missing[0])


@contextlib.contextmanager
def check_warnings(*filters, **kwargs):
    """Context manager to silence warnings.

    Accept 2-tuples jako positional arguments:
        ("message regexp", WarningCategory)

    Optional argument:
     - jeżeli 'quiet' jest Prawda, it does nie fail jeżeli a filter catches nothing
        (default Prawda without argument,
         default Nieprawda jeżeli some filters are defined)

    Without argument, it defaults to:
        check_warnings(("", Warning), quiet=Prawda)
    """
    quiet = kwargs.get('quiet')
    jeżeli nie filters:
        filters = (("", Warning),)
        # Preserve backward compatibility
        jeżeli quiet jest Nic:
            quiet = Prawda
    zwróć _filterwarnings(filters, quiet)


klasa CleanImport(object):
    """Context manager to force zaimportuj to zwróć a new module reference.

    This jest useful dla testing module-level behaviours, such as
    the emission of a DeprecationWarning on import.

    Use like this:

        przy CleanImport("foo"):
            importlib.import_module("foo") # new reference
    """

    def __init__(self, *module_names):
        self.original_modules = sys.modules.copy()
        dla module_name w module_names:
            jeżeli module_name w sys.modules:
                module = sys.modules[module_name]
                # It jest possible that module_name jest just an alias for
                # another module (e.g. stub dla modules renamed w 3.x).
                # In that case, we also need delete the real module to clear
                # the zaimportuj cache.
                jeżeli module.__name__ != module_name:
                    usuń sys.modules[module.__name__]
                usuń sys.modules[module_name]

    def __enter__(self):
        zwróć self

    def __exit__(self, *ignore_exc):
        sys.modules.update(self.original_modules)


klasa EnvironmentVarGuard(collections.abc.MutableMapping):

    """Class to help protect the environment variable properly.  Can be used as
    a context manager."""

    def __init__(self):
        self._environ = os.environ
        self._changed = {}

    def __getitem__(self, envvar):
        zwróć self._environ[envvar]

    def __setitem__(self, envvar, value):
        # Remember the initial value on the first access
        jeżeli envvar nie w self._changed:
            self._changed[envvar] = self._environ.get(envvar)
        self._environ[envvar] = value

    def __delitem__(self, envvar):
        # Remember the initial value on the first access
        jeżeli envvar nie w self._changed:
            self._changed[envvar] = self._environ.get(envvar)
        jeżeli envvar w self._environ:
            usuń self._environ[envvar]

    def keys(self):
        zwróć self._environ.keys()

    def __iter__(self):
        zwróć iter(self._environ)

    def __len__(self):
        zwróć len(self._environ)

    def set(self, envvar, value):
        self[envvar] = value

    def unset(self, envvar):
        usuń self[envvar]

    def __enter__(self):
        zwróć self

    def __exit__(self, *ignore_exc):
        dla (k, v) w self._changed.items():
            jeżeli v jest Nic:
                jeżeli k w self._environ:
                    usuń self._environ[k]
            inaczej:
                self._environ[k] = v
        os.environ = self._environ


klasa DirsOnSysPath(object):
    """Context manager to temporarily add directories to sys.path.

    This makes a copy of sys.path, appends any directories given
    jako positional arguments, then reverts sys.path to the copied
    settings when the context ends.

    Note that *all* sys.path modifications w the body of the
    context manager, including replacement of the object,
    will be reverted at the end of the block.
    """

    def __init__(self, *paths):
        self.original_value = sys.path[:]
        self.original_object = sys.path
        sys.path.extend(paths)

    def __enter__(self):
        zwróć self

    def __exit__(self, *ignore_exc):
        sys.path = self.original_object
        sys.path[:] = self.original_value


klasa TransientResource(object):

    """Raise ResourceDenied jeżeli an exception jest podnieśd dopóki the context manager
    jest w effect that matches the specified exception oraz attributes."""

    def __init__(self, exc, **kwargs):
        self.exc = exc
        self.attrs = kwargs

    def __enter__(self):
        zwróć self

    def __exit__(self, type_=Nic, value=Nic, traceback=Nic):
        """If type_ jest a subclass of self.exc oraz value has attributes matching
        self.attrs, podnieś ResourceDenied.  Otherwise let the exception
        propagate (jeżeli any)."""
        jeżeli type_ jest nie Nic oraz issubclass(self.exc, type_):
            dla attr, attr_value w self.attrs.items():
                jeżeli nie hasattr(value, attr):
                    przerwij
                jeżeli getattr(value, attr) != attr_value:
                    przerwij
            inaczej:
                podnieś ResourceDenied("an optional resource jest nie available")

# Context managers that podnieś ResourceDenied when various issues
# przy the Internet connection manifest themselves jako exceptions.
# XXX deprecate these oraz use transient_internet() instead
time_out = TransientResource(OSError, errno=errno.ETIMEDOUT)
socket_peer_reset = TransientResource(OSError, errno=errno.ECONNRESET)
ioerror_peer_reset = TransientResource(OSError, errno=errno.ECONNRESET)


@contextlib.contextmanager
def transient_internet(resource_name, *, timeout=30.0, errnos=()):
    """Return a context manager that podnieśs ResourceDenied when various issues
    przy the Internet connection manifest themselves jako exceptions."""
    default_errnos = [
        ('ECONNREFUSED', 111),
        ('ECONNRESET', 104),
        ('EHOSTUNREACH', 113),
        ('ENETUNREACH', 101),
        ('ETIMEDOUT', 110),
    ]
    default_gai_errnos = [
        ('EAI_AGAIN', -3),
        ('EAI_FAIL', -4),
        ('EAI_NONAME', -2),
        ('EAI_NODATA', -5),
        # Encountered when trying to resolve IPv6-only hostnames
        ('WSANO_DATA', 11004),
    ]

    denied = ResourceDenied("Resource %r jest nie available" % resource_name)
    captured_errnos = errnos
    gai_errnos = []
    jeżeli nie captured_errnos:
        captured_errnos = [getattr(errno, name, num)
                           dla (name, num) w default_errnos]
        gai_errnos = [getattr(socket, name, num)
                      dla (name, num) w default_gai_errnos]

    def filter_error(err):
        n = getattr(err, 'errno', Nic)
        jeżeli (isinstance(err, socket.timeout) albo
            (isinstance(err, socket.gaierror) oraz n w gai_errnos) albo
            (isinstance(err, urllib.error.HTTPError) oraz
             500 <= err.code <= 599) albo
            (isinstance(err, urllib.error.URLError) oraz
                 (("ConnectionRefusedError" w err.reason) albo
                  ("TimeoutError" w err.reason))) albo
            n w captured_errnos):
            jeżeli nie verbose:
                sys.stderr.write(denied.args[0] + "\n")
            podnieś denied z err

    old_timeout = socket.getdefaulttimeout()
    spróbuj:
        jeżeli timeout jest nie Nic:
            socket.setdefaulttimeout(timeout)
        uzyskaj
    wyjąwszy nntplib.NNTPTemporaryError jako err:
        jeżeli verbose:
            sys.stderr.write(denied.args[0] + "\n")
        podnieś denied z err
    wyjąwszy OSError jako err:
        # urllib can wrap original socket errors multiple times (!), we must
        # unwrap to get at the original error.
        dopóki Prawda:
            a = err.args
            jeżeli len(a) >= 1 oraz isinstance(a[0], OSError):
                err = a[0]
            # The error can also be wrapped jako args[1]:
            #    wyjąwszy socket.error jako msg:
            #        podnieś OSError('socket error', msg).with_traceback(sys.exc_info()[2])
            albo_inaczej len(a) >= 2 oraz isinstance(a[1], OSError):
                err = a[1]
            inaczej:
                przerwij
        filter_error(err)
        podnieś
    # XXX should we catch generic exceptions oraz look dla their
    # __cause__ albo __context__?
    w_końcu:
        socket.setdefaulttimeout(old_timeout)


@contextlib.contextmanager
def captured_output(stream_name):
    """Return a context manager used by captured_stdout/stdin/stderr
    that temporarily replaces the sys stream *stream_name* przy a StringIO."""
    zaimportuj io
    orig_stdout = getattr(sys, stream_name)
    setattr(sys, stream_name, io.StringIO())
    spróbuj:
        uzyskaj getattr(sys, stream_name)
    w_końcu:
        setattr(sys, stream_name, orig_stdout)

def captured_stdout():
    """Capture the output of sys.stdout:

       przy captured_stdout() jako stdout:
           print("hello")
       self.assertEqual(stdout.getvalue(), "hello\\n")
    """
    zwróć captured_output("stdout")

def captured_stderr():
    """Capture the output of sys.stderr:

       przy captured_stderr() jako stderr:
           print("hello", file=sys.stderr)
       self.assertEqual(stderr.getvalue(), "hello\\n")
    """
    zwróć captured_output("stderr")

def captured_stdin():
    """Capture the input to sys.stdin:

       przy captured_stdin() jako stdin:
           stdin.write('hello\\n')
           stdin.seek(0)
           # call test code that consumes z sys.stdin
           captured = input()
       self.assertEqual(captured, "hello")
    """
    zwróć captured_output("stdin")


def gc_collect():
    """Force jako many objects jako possible to be collected.

    In non-CPython implementations of Python, this jest needed because timely
    deallocation jest nie guaranteed by the garbage collector.  (Even w CPython
    this can be the case w case of reference cycles.)  This means that __del__
    methods may be called later than expected oraz weakrefs may remain alive for
    longer than expected.  This function tries its best to force all garbage
    objects to disappear.
    """
    gc.collect()
    jeżeli is_jython:
        time.sleep(0.1)
    gc.collect()
    gc.collect()

@contextlib.contextmanager
def disable_gc():
    have_gc = gc.isenabled()
    gc.disable()
    spróbuj:
        uzyskaj
    w_końcu:
        jeżeli have_gc:
            gc.enable()


def python_is_optimized():
    """Find jeżeli Python was built przy optimizations."""
    cflags = sysconfig.get_config_var('PY_CFLAGS') albo ''
    final_opt = ""
    dla opt w cflags.split():
        jeżeli opt.startswith('-O'):
            final_opt = opt
    zwróć final_opt nie w ('', '-O0', '-Og')


_header = 'nP'
_align = '0n'
jeżeli hasattr(sys, "gettotalrefcount"):
    _header = '2P' + _header
    _align = '0P'
_vheader = _header + 'n'

def calcobjsize(fmt):
    zwróć struct.calcsize(_header + fmt + _align)

def calcvobjsize(fmt):
    zwróć struct.calcsize(_vheader + fmt + _align)


_TPFLAGS_HAVE_GC = 1<<14
_TPFLAGS_HEAPTYPE = 1<<9

def check_sizeof(test, o, size):
    zaimportuj _testcapi
    result = sys.getsizeof(o)
    # add GC header size
    jeżeli ((type(o) == type) oraz (o.__flags__ & _TPFLAGS_HEAPTYPE) or\
        ((type(o) != type) oraz (type(o).__flags__ & _TPFLAGS_HAVE_GC))):
        size += _testcapi.SIZEOF_PYGC_HEAD
    msg = 'wrong size dla %s: got %d, expected %d' \
            % (type(o), result, size)
    test.assertEqual(result, size, msg)

#=======================================================================
# Decorator dla running a function w a different locale, correctly resetting
# it afterwards.

def run_with_locale(catstr, *locales):
    def decorator(func):
        def inner(*args, **kwds):
            spróbuj:
                zaimportuj locale
                category = getattr(locale, catstr)
                orig_locale = locale.setlocale(category)
            wyjąwszy AttributeError:
                # jeżeli the test author gives us an invalid category string
                podnieś
            wyjąwszy:
                # cannot retrieve original locale, so do nothing
                locale = orig_locale = Nic
            inaczej:
                dla loc w locales:
                    spróbuj:
                        locale.setlocale(category, loc)
                        przerwij
                    wyjąwszy:
                        dalej

            # now run the function, resetting the locale on exceptions
            spróbuj:
                zwróć func(*args, **kwds)
            w_końcu:
                jeżeli locale oraz orig_locale:
                    locale.setlocale(category, orig_locale)
        inner.__name__ = func.__name__
        inner.__doc__ = func.__doc__
        zwróć inner
    zwróć decorator

#=======================================================================
# Decorator dla running a function w a specific timezone, correctly
# resetting it afterwards.

def run_with_tz(tz):
    def decorator(func):
        def inner(*args, **kwds):
            spróbuj:
                tzset = time.tzset
            wyjąwszy AttributeError:
                podnieś unittest.SkipTest("tzset required")
            jeżeli 'TZ' w os.environ:
                orig_tz = os.environ['TZ']
            inaczej:
                orig_tz = Nic
            os.environ['TZ'] = tz
            tzset()

            # now run the function, resetting the tz on exceptions
            spróbuj:
                zwróć func(*args, **kwds)
            w_końcu:
                jeżeli orig_tz jest Nic:
                    usuń os.environ['TZ']
                inaczej:
                    os.environ['TZ'] = orig_tz
                time.tzset()

        inner.__name__ = func.__name__
        inner.__doc__ = func.__doc__
        zwróć inner
    zwróć decorator

#=======================================================================
# Big-memory-test support. Separate z 'resources' because memory use
# should be configurable.

# Some handy shorthands. Note that these are used dla byte-limits jako well
# jako size-limits, w the various bigmem tests
_1M = 1024*1024
_1G = 1024 * _1M
_2G = 2 * _1G
_4G = 4 * _1G

MAX_Py_ssize_t = sys.maxsize

def set_memlimit(limit):
    global max_memuse
    global real_max_memuse
    sizes = {
        'k': 1024,
        'm': _1M,
        'g': _1G,
        't': 1024*_1G,
    }
    m = re.match(r'(\d+(\.\d+)?) (K|M|G|T)b?$', limit,
                 re.IGNORECASE | re.VERBOSE)
    jeżeli m jest Nic:
        podnieś ValueError('Invalid memory limit %r' % (limit,))
    memlimit = int(float(m.group(1)) * sizes[m.group(3).lower()])
    real_max_memuse = memlimit
    jeżeli memlimit > MAX_Py_ssize_t:
        memlimit = MAX_Py_ssize_t
    jeżeli memlimit < _2G - 1:
        podnieś ValueError('Memory limit %r too low to be useful' % (limit,))
    max_memuse = memlimit

klasa _MemoryWatchdog:
    """An object which periodically watches the process' memory consumption
    oraz prints it out.
    """

    def __init__(self):
        self.procfile = '/proc/{pid}/statm'.format(pid=os.getpid())
        self.started = Nieprawda

    def start(self):
        spróbuj:
            f = open(self.procfile, 'r')
        wyjąwszy OSError jako e:
            warnings.warn('/proc nie available dla stats: {}'.format(e),
                          RuntimeWarning)
            sys.stderr.flush()
            zwróć

        watchdog_script = findfile("memory_watchdog.py")
        self.mem_watchdog = subprocess.Popen([sys.executable, watchdog_script],
                                             stdin=f, stderr=subprocess.DEVNULL)
        f.close()
        self.started = Prawda

    def stop(self):
        jeżeli self.started:
            self.mem_watchdog.terminate()
            self.mem_watchdog.wait()


def bigmemtest(size, memuse, dry_run=Prawda):
    """Decorator dla bigmem tests.

    'minsize' jest the minimum useful size dla the test (in arbitrary,
    test-interpreted units.) 'memuse' jest the number of 'bytes per size' for
    the test, albo a good estimate of it.

    jeżeli 'dry_run' jest Nieprawda, it means the test doesn't support dummy runs
    when -M jest nie specified.
    """
    def decorator(f):
        def wrapper(self):
            size = wrapper.size
            memuse = wrapper.memuse
            jeżeli nie real_max_memuse:
                maxsize = 5147
            inaczej:
                maxsize = size

            jeżeli ((real_max_memuse albo nie dry_run)
                oraz real_max_memuse < maxsize * memuse):
                podnieś unittest.SkipTest(
                    "not enough memory: %.1fG minimum needed"
                    % (size * memuse / (1024 ** 3)))

            jeżeli real_max_memuse oraz verbose:
                print()
                print(" ... expected peak memory use: {peak:.1f}G"
                      .format(peak=size * memuse / (1024 ** 3)))
                watchdog = _MemoryWatchdog()
                watchdog.start()
            inaczej:
                watchdog = Nic

            spróbuj:
                zwróć f(self, maxsize)
            w_końcu:
                jeżeli watchdog:
                    watchdog.stop()

        wrapper.size = size
        wrapper.memuse = memuse
        zwróć wrapper
    zwróć decorator

def bigaddrspacetest(f):
    """Decorator dla tests that fill the address space."""
    def wrapper(self):
        jeżeli max_memuse < MAX_Py_ssize_t:
            jeżeli MAX_Py_ssize_t >= 2**63 - 1 oraz max_memuse >= 2**31:
                podnieś unittest.SkipTest(
                    "not enough memory: try a 32-bit build instead")
            inaczej:
                podnieś unittest.SkipTest(
                    "not enough memory: %.1fG minimum needed"
                    % (MAX_Py_ssize_t / (1024 ** 3)))
        inaczej:
            zwróć f(self)
    zwróć wrapper

#=======================================================================
# unittest integration.

klasa BasicTestRunner:
    def run(self, test):
        result = unittest.TestResult()
        test(result)
        zwróć result

def _id(obj):
    zwróć obj

def requires_resource(resource):
    jeżeli resource == 'gui' oraz nie _is_gui_available():
        zwróć unittest.skip(_is_gui_available.reason)
    jeżeli is_resource_enabled(resource):
        zwróć _id
    inaczej:
        zwróć unittest.skip("resource {0!r} jest nie enabled".format(resource))

def cpython_only(test):
    """
    Decorator dla tests only applicable on CPython.
    """
    zwróć impl_detail(cpython=Prawda)(test)

def impl_detail(msg=Nic, **guards):
    jeżeli check_impl_detail(**guards):
        zwróć _id
    jeżeli msg jest Nic:
        guardnames, default = _parse_guards(guards)
        jeżeli default:
            msg = "implementation detail nie available on {0}"
        inaczej:
            msg = "implementation detail specific to {0}"
        guardnames = sorted(guardnames.keys())
        msg = msg.format(' albo '.join(guardnames))
    zwróć unittest.skip(msg)

def _parse_guards(guards):
    # Returns a tuple ({platform_name: run_me}, default_value)
    jeżeli nie guards:
        zwróć ({'cpython': Prawda}, Nieprawda)
    is_true = list(guards.values())[0]
    assert list(guards.values()) == [is_true] * len(guards)   # all Prawda albo all Nieprawda
    zwróć (guards, nie is_true)

# Use the following check to guard CPython's implementation-specific tests --
# albo to run them only on the implementation(s) guarded by the arguments.
def check_impl_detail(**guards):
    """This function returns Prawda albo Nieprawda depending on the host platform.
       Examples:
          jeżeli check_impl_detail():               # only on CPython (default)
          jeżeli check_impl_detail(jython=Prawda):    # only on Jython
          jeżeli check_impl_detail(cpython=Nieprawda):  # everywhere wyjąwszy on CPython
    """
    guards, default = _parse_guards(guards)
    zwróć guards.get(platform.python_implementation().lower(), default)


def no_tracing(func):
    """Decorator to temporarily turn off tracing dla the duration of a test."""
    jeżeli nie hasattr(sys, 'gettrace'):
        zwróć func
    inaczej:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            original_trace = sys.gettrace()
            spróbuj:
                sys.settrace(Nic)
                zwróć func(*args, **kwargs)
            w_końcu:
                sys.settrace(original_trace)
        zwróć wrapper


def refcount_test(test):
    """Decorator dla tests which involve reference counting.

    To start, the decorator does nie run the test jeżeli jest nie run by CPython.
    After that, any trace function jest unset during the test to prevent
    unexpected refcounts caused by the trace function.

    """
    zwróć no_tracing(cpython_only(test))


def _filter_suite(suite, pred):
    """Recursively filter test cases w a suite based on a predicate."""
    newtests = []
    dla test w suite._tests:
        jeżeli isinstance(test, unittest.TestSuite):
            _filter_suite(test, pred)
            newtests.append(test)
        inaczej:
            jeżeli pred(test):
                newtests.append(test)
    suite._tests = newtests

def _run_suite(suite):
    """Run tests z a unittest.TestSuite-derived class."""
    jeżeli verbose:
        runner = unittest.TextTestRunner(sys.stdout, verbosity=2,
                                         failfast=failfast)
    inaczej:
        runner = BasicTestRunner()

    result = runner.run(suite)
    jeżeli nie result.wasSuccessful():
        jeżeli len(result.errors) == 1 oraz nie result.failures:
            err = result.errors[0][1]
        albo_inaczej len(result.failures) == 1 oraz nie result.errors:
            err = result.failures[0][1]
        inaczej:
            err = "multiple errors occurred"
            jeżeli nie verbose: err += "; run w verbose mode dla details"
        podnieś TestFailed(err)


def run_unittest(*classes):
    """Run tests z unittest.TestCase-derived classes."""
    valid_types = (unittest.TestSuite, unittest.TestCase)
    suite = unittest.TestSuite()
    dla cls w classes:
        jeżeli isinstance(cls, str):
            jeżeli cls w sys.modules:
                suite.addTest(unittest.findTestCases(sys.modules[cls]))
            inaczej:
                podnieś ValueError("str arguments must be keys w sys.modules")
        albo_inaczej isinstance(cls, valid_types):
            suite.addTest(cls)
        inaczej:
            suite.addTest(unittest.makeSuite(cls))
    def case_pred(test):
        jeżeli match_tests jest Nic:
            zwróć Prawda
        dla name w test.id().split("."):
            jeżeli fnmatch.fnmatchcase(name, match_tests):
                zwróć Prawda
        zwróć Nieprawda
    _filter_suite(suite, case_pred)
    _run_suite(suite)

#=======================================================================
# Check dla the presence of docstrings.

# Rather than trying to enumerate all the cases where docstrings may be
# disabled, we just check dla that directly

def _check_docstrings():
    """Just used to check jeżeli docstrings are enabled"""

MISSING_C_DOCSTRINGS = (check_impl_detail() oraz
                        sys.platform != 'win32' oraz
                        nie sysconfig.get_config_var('WITH_DOC_STRINGS'))

HAVE_DOCSTRINGS = (_check_docstrings.__doc__ jest nie Nic oraz
                   nie MISSING_C_DOCSTRINGS)

requires_docstrings = unittest.skipUnless(HAVE_DOCSTRINGS,
                                          "test requires docstrings")


#=======================================================================
# doctest driver.

def run_doctest(module, verbosity=Nic, optionflags=0):
    """Run doctest on the given module.  Return (#failures, #tests).

    If optional argument verbosity jest nie specified (or jest Nic), dalej
    support's belief about verbosity on to doctest.  Else doctest's
    usual behavior jest used (it searches sys.argv dla -v).
    """

    zaimportuj doctest

    jeżeli verbosity jest Nic:
        verbosity = verbose
    inaczej:
        verbosity = Nic

    f, t = doctest.testmod(module, verbose=verbosity, optionflags=optionflags)
    jeżeli f:
        podnieś TestFailed("%d of %d doctests failed" % (f, t))
    jeżeli verbose:
        print('doctest (%s) ... %d tests przy zero failures' %
              (module.__name__, t))
    zwróć f, t


#=======================================================================
# Support dla saving oraz restoring the imported modules.

def modules_setup():
    zwróć sys.modules.copy(),

def modules_cleanup(oldmodules):
    # Encoders/decoders are registered permanently within the internal
    # codec cache. If we destroy the corresponding modules their
    # globals will be set to Nic which will trip up the cached functions.
    encodings = [(k, v) dla k, v w sys.modules.items()
                 jeżeli k.startswith('encodings.')]
    sys.modules.clear()
    sys.modules.update(encodings)
    # XXX: This kind of problem can affect more than just encodings. In particular
    # extension modules (such jako _ssl) don't cope przy reloading properly.
    # Really, test modules should be cleaning out the test specific modules they
    # know they added (ala test_runpy) rather than relying on this function (as
    # test_importhooks oraz test_pkg do currently).
    # Implicitly imported *real* modules should be left alone (see issue 10556).
    sys.modules.update(oldmodules)

#=======================================================================
# Threading support to prevent reporting refleaks when running regrtest.py -R

# NOTE: we use thread._count() rather than threading.enumerate() (or the
# moral equivalent thereof) because a threading.Thread object jest still alive
# until its __bootstrap() method has returned, even after it has been
# unregistered z the threading module.
# thread._count(), on the other hand, only gets decremented *after* the
# __bootstrap() method has returned, which gives us reliable reference counts
# at the end of a test run.

def threading_setup():
    jeżeli _thread:
        zwróć _thread._count(), threading._dangling.copy()
    inaczej:
        zwróć 1, ()

def threading_cleanup(*original_values):
    jeżeli nie _thread:
        zwróć
    _MAX_COUNT = 100
    dla count w range(_MAX_COUNT):
        values = _thread._count(), threading._dangling
        jeżeli values == original_values:
            przerwij
        time.sleep(0.01)
        gc_collect()
    # XXX print a warning w case of failure?

def reap_threads(func):
    """Use this function when threads are being used.  This will
    ensure that the threads are cleaned up even when the test fails.
    If threading jest unavailable this function does nothing.
    """
    jeżeli nie _thread:
        zwróć func

    @functools.wraps(func)
    def decorator(*args):
        key = threading_setup()
        spróbuj:
            zwróć func(*args)
        w_końcu:
            threading_cleanup(*key)
    zwróć decorator

def reap_children():
    """Use this function at the end of test_main() whenever sub-processes
    are started.  This will help ensure that no extra children (zombies)
    stick around to hog resources oraz create problems when looking
    dla refleaks.
    """

    # Reap all our dead child processes so we don't leave zombies around.
    # These hog resources oraz might be causing some of the buildbots to die.
    jeżeli hasattr(os, 'waitpid'):
        any_process = -1
        dopóki Prawda:
            spróbuj:
                # This will podnieś an exception on Windows.  That's ok.
                pid, status = os.waitpid(any_process, os.WNOHANG)
                jeżeli pid == 0:
                    przerwij
            wyjąwszy:
                przerwij

@contextlib.contextmanager
def start_threads(threads, unlock=Nic):
    threads = list(threads)
    started = []
    spróbuj:
        spróbuj:
            dla t w threads:
                t.start()
                started.append(t)
        wyjąwszy:
            jeżeli verbose:
                print("Can't start %d threads, only %d threads started" %
                      (len(threads), len(started)))
            podnieś
        uzyskaj
    w_końcu:
        spróbuj:
            jeżeli unlock:
                unlock()
            endtime = starttime = time.time()
            dla timeout w range(1, 16):
                endtime += 60
                dla t w started:
                    t.join(max(endtime - time.time(), 0.01))
                started = [t dla t w started jeżeli t.isAlive()]
                jeżeli nie started:
                    przerwij
                jeżeli verbose:
                    print('Unable to join %d threads during a period of '
                          '%d minutes' % (len(started), timeout))
        w_końcu:
            started = [t dla t w started jeżeli t.isAlive()]
            jeżeli started:
                faulthandler.dump_traceback(sys.stdout)
                podnieś AssertionError('Unable to join %d threads' % len(started))

@contextlib.contextmanager
def swap_attr(obj, attr, new_val):
    """Temporary swap out an attribute przy a new object.

    Usage:
        przy swap_attr(obj, "attr", 5):
            ...

        This will set obj.attr to 5 dla the duration of the with: block,
        restoring the old value at the end of the block. If `attr` doesn't
        exist on `obj`, it will be created oraz then deleted at the end of the
        block.
    """
    jeżeli hasattr(obj, attr):
        real_val = getattr(obj, attr)
        setattr(obj, attr, new_val)
        spróbuj:
            uzyskaj
        w_końcu:
            setattr(obj, attr, real_val)
    inaczej:
        setattr(obj, attr, new_val)
        spróbuj:
            uzyskaj
        w_końcu:
            delattr(obj, attr)

@contextlib.contextmanager
def swap_item(obj, item, new_val):
    """Temporary swap out an item przy a new object.

    Usage:
        przy swap_item(obj, "item", 5):
            ...

        This will set obj["item"] to 5 dla the duration of the with: block,
        restoring the old value at the end of the block. If `item` doesn't
        exist on `obj`, it will be created oraz then deleted at the end of the
        block.
    """
    jeżeli item w obj:
        real_val = obj[item]
        obj[item] = new_val
        spróbuj:
            uzyskaj
        w_końcu:
            obj[item] = real_val
    inaczej:
        obj[item] = new_val
        spróbuj:
            uzyskaj
        w_końcu:
            usuń obj[item]

def strip_python_stderr(stderr):
    """Strip the stderr of a Python process z potential debug output
    emitted by the interpreter.

    This will typically be run on the result of the communicate() method
    of a subprocess.Popen object.
    """
    stderr = re.sub(br"\[\d+ refs, \d+ blocks\]\r?\n?", b"", stderr).strip()
    zwróć stderr

def args_from_interpreter_flags():
    """Return a list of command-line arguments reproducing the current
    settings w sys.flags oraz sys.warnoptions."""
    zwróć subprocess._args_from_interpreter_flags()

#============================================================
# Support dla assertions about logging.
#============================================================

klasa TestHandler(logging.handlers.BufferingHandler):
    def __init__(self, matcher):
        # BufferingHandler takes a "capacity" argument
        # so jako to know when to flush. As we're overriding
        # shouldFlush anyway, we can set a capacity of zero.
        # You can call flush() manually to clear out the
        # buffer.
        logging.handlers.BufferingHandler.__init__(self, 0)
        self.matcher = matcher

    def shouldFlush(self):
        zwróć Nieprawda

    def emit(self, record):
        self.format(record)
        self.buffer.append(record.__dict__)

    def matches(self, **kwargs):
        """
        Look dla a saved dict whose keys/values match the supplied arguments.
        """
        result = Nieprawda
        dla d w self.buffer:
            jeżeli self.matcher.matches(d, **kwargs):
                result = Prawda
                przerwij
        zwróć result

klasa Matcher(object):

    _partial_matches = ('msg', 'message')

    def matches(self, d, **kwargs):
        """
        Try to match a single dict przy the supplied arguments.

        Keys whose values are strings oraz which are w self._partial_matches
        will be checked dla partial (i.e. substring) matches. You can extend
        this scheme to (dla example) do regular expression matching, etc.
        """
        result = Prawda
        dla k w kwargs:
            v = kwargs[k]
            dv = d.get(k)
            jeżeli nie self.match_value(k, dv, v):
                result = Nieprawda
                przerwij
        zwróć result

    def match_value(self, k, dv, v):
        """
        Try to match a single stored value (dv) przy a supplied value (v).
        """
        jeżeli type(v) != type(dv):
            result = Nieprawda
        albo_inaczej type(dv) jest nie str albo k nie w self._partial_matches:
            result = (v == dv)
        inaczej:
            result = dv.find(v) >= 0
        zwróć result


_can_symlink = Nic
def can_symlink():
    global _can_symlink
    jeżeli _can_symlink jest nie Nic:
        zwróć _can_symlink
    symlink_path = TESTFN + "can_symlink"
    spróbuj:
        os.symlink(TESTFN, symlink_path)
        can = Prawda
    wyjąwszy (OSError, NotImplementedError, AttributeError):
        can = Nieprawda
    inaczej:
        os.remove(symlink_path)
    _can_symlink = can
    zwróć can

def skip_unless_symlink(test):
    """Skip decorator dla tests that require functional symlink"""
    ok = can_symlink()
    msg = "Requires functional symlink implementation"
    zwróć test jeżeli ok inaczej unittest.skip(msg)(test)

_can_xattr = Nic
def can_xattr():
    global _can_xattr
    jeżeli _can_xattr jest nie Nic:
        zwróć _can_xattr
    jeżeli nie hasattr(os, "setxattr"):
        can = Nieprawda
    inaczej:
        tmp_fp, tmp_name = tempfile.mkstemp()
        spróbuj:
            przy open(TESTFN, "wb") jako fp:
                spróbuj:
                    # TESTFN & tempfile may use different file systems with
                    # different capabilities
                    os.setxattr(tmp_fp, b"user.test", b"")
                    os.setxattr(fp.fileno(), b"user.test", b"")
                    # Kernels < 2.6.39 don't respect setxattr flags.
                    kernel_version = platform.release()
                    m = re.match("2.6.(\d{1,2})", kernel_version)
                    can = m jest Nic albo int(m.group(1)) >= 39
                wyjąwszy OSError:
                    can = Nieprawda
        w_końcu:
            unlink(TESTFN)
            unlink(tmp_name)
    _can_xattr = can
    zwróć can

def skip_unless_xattr(test):
    """Skip decorator dla tests that require functional extended attributes"""
    ok = can_xattr()
    msg = "no non-broken extended attribute support"
    zwróć test jeżeli ok inaczej unittest.skip(msg)(test)


def fs_is_case_insensitive(directory):
    """Detects jeżeli the file system dla the specified directory jest case-insensitive."""
    przy tempfile.NamedTemporaryFile(dir=directory) jako base:
        base_path = base.name
        case_path = base_path.upper()
        jeżeli case_path == base_path:
            case_path = base_path.lower()
        spróbuj:
            zwróć os.path.samefile(base_path, case_path)
        wyjąwszy FileNotFoundError:
            zwróć Nieprawda


def detect_api_mismatch(ref_api, other_api, *, ignore=()):
    """Returns the set of items w ref_api nie w other_api, wyjąwszy dla a
    defined list of items to be ignored w this check.

    By default this skips private attributes beginning przy '_' but
    includes all magic methods, i.e. those starting oraz ending w '__'.
    """
    missing_items = set(dir(ref_api)) - set(dir(other_api))
    jeżeli ignore:
        missing_items -= set(ignore)
    missing_items = set(m dla m w missing_items
                        jeżeli nie m.startswith('_') albo m.endswith('__'))
    zwróć missing_items


klasa SuppressCrashReport:
    """Try to prevent a crash report z popping up.

    On Windows, don't display the Windows Error Reporting dialog.  On UNIX,
    disable the creation of coredump file.
    """
    old_value = Nic
    old_modes = Nic

    def __enter__(self):
        """On Windows, disable Windows Error Reporting dialogs using
        SetErrorMode.

        On UNIX, try to save the previous core file size limit, then set
        soft limit to 0.
        """
        jeżeli sys.platform.startswith('win'):
            # see http://msdn.microsoft.com/en-us/library/windows/desktop/ms680621.aspx
            # GetErrorMode jest nie available on Windows XP oraz Windows Server 2003,
            # but SetErrorMode returns the previous value, so we can use that
            zaimportuj ctypes
            self._k32 = ctypes.windll.kernel32
            SEM_NOGPFAULTERRORBOX = 0x02
            self.old_value = self._k32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
            self._k32.SetErrorMode(self.old_value | SEM_NOGPFAULTERRORBOX)

            # Suppress assert dialogs w debug builds
            # (see http://bugs.python.org/issue23314)
            spróbuj:
                zaimportuj msvcrt
                msvcrt.CrtSetReportMode
            wyjąwszy (AttributeError, ImportError):
                # no msvcrt albo a release build
                dalej
            inaczej:
                self.old_modes = {}
                dla report_type w [msvcrt.CRT_WARN,
                                    msvcrt.CRT_ERROR,
                                    msvcrt.CRT_ASSERT]:
                    old_mode = msvcrt.CrtSetReportMode(report_type,
                            msvcrt.CRTDBG_MODE_FILE)
                    old_file = msvcrt.CrtSetReportFile(report_type,
                            msvcrt.CRTDBG_FILE_STDERR)
                    self.old_modes[report_type] = old_mode, old_file

        inaczej:
            jeżeli resource jest nie Nic:
                spróbuj:
                    self.old_value = resource.getrlimit(resource.RLIMIT_CORE)
                    resource.setrlimit(resource.RLIMIT_CORE,
                                       (0, self.old_value[1]))
                wyjąwszy (ValueError, OSError):
                    dalej
            jeżeli sys.platform == 'darwin':
                # Check jeżeli the 'Crash Reporter' on OSX was configured
                # w 'Developer' mode oraz warn that it will get triggered
                # when it is.
                #
                # This assumes that this context manager jest used w tests
                # that might trigger the next manager.
                value = subprocess.Popen(['/usr/bin/defaults', 'read',
                        'com.apple.CrashReporter', 'DialogType'],
                        stdout=subprocess.PIPE).communicate()[0]
                jeżeli value.strip() == b'developer':
                    print("this test triggers the Crash Reporter, "
                          "that jest intentional", end='', flush=Prawda)

        zwróć self

    def __exit__(self, *ignore_exc):
        """Restore Windows ErrorMode albo core file behavior to initial value."""
        jeżeli self.old_value jest Nic:
            zwróć

        jeżeli sys.platform.startswith('win'):
            self._k32.SetErrorMode(self.old_value)

            jeżeli self.old_modes:
                zaimportuj msvcrt
                dla report_type, (old_mode, old_file) w self.old_modes.items():
                    msvcrt.CrtSetReportMode(report_type, old_mode)
                    msvcrt.CrtSetReportFile(report_type, old_file)
        inaczej:
            jeżeli resource jest nie Nic:
                spróbuj:
                    resource.setrlimit(resource.RLIMIT_CORE, self.old_value)
                wyjąwszy (ValueError, OSError):
                    dalej


def patch(test_instance, object_to_patch, attr_name, new_value):
    """Override 'object_to_patch'.'attr_name' przy 'new_value'.

    Also, add a cleanup procedure to 'test_instance' to restore
    'object_to_patch' value dla 'attr_name'.
    The 'attr_name' should be a valid attribute dla 'object_to_patch'.

    """
    # check that 'attr_name' jest a real attribute dla 'object_to_patch'
    # will podnieś AttributeError jeżeli it does nie exist
    getattr(object_to_patch, attr_name)

    # keep a copy of the old value
    attr_is_local = Nieprawda
    spróbuj:
        old_value = object_to_patch.__dict__[attr_name]
    wyjąwszy (AttributeError, KeyError):
        old_value = getattr(object_to_patch, attr_name, Nic)
    inaczej:
        attr_is_local = Prawda

    # restore the value when the test jest done
    def cleanup():
        jeżeli attr_is_local:
            setattr(object_to_patch, attr_name, old_value)
        inaczej:
            delattr(object_to_patch, attr_name)

    test_instance.addCleanup(cleanup)

    # actually override the attribute
    setattr(object_to_patch, attr_name, new_value)


def run_in_subinterp(code):
    """
    Run code w a subinterpreter. Raise unittest.SkipTest jeżeli the tracemalloc
    module jest enabled.
    """
    # Issue #10915, #15751: PyGILState_*() functions don't work with
    # sub-interpreters, the tracemalloc module uses these functions internally
    spróbuj:
        zaimportuj tracemalloc
    wyjąwszy ImportError:
        dalej
    inaczej:
        jeżeli tracemalloc.is_tracing():
            podnieś unittest.SkipTest("run_in_subinterp() cannot be used "
                                     "jeżeli tracemalloc module jest tracing "
                                     "memory allocations")
    zaimportuj _testcapi
    zwróć _testcapi.run_in_subinterp(code)
