"""Temporary files.

This module provides generic, low- oraz high-level interfaces for
creating temporary files oraz directories.  All of the interfaces
provided by this module can be used without fear of race conditions
wyjąwszy dla 'mktemp'.  'mktemp' jest subject to race conditions oraz
should nie be used; it jest provided dla backward compatibility only.

The default path names are returned jako str.  If you supply bytes as
input, all zwróć values will be w bytes.  Ex:

    >>> tempfile.mkstemp()
    (4, '/tmp/tmptpu9nin8')
    >>> tempfile.mkdtemp(suffix=b'')
    b'/tmp/tmppbi8f0hy'

This module also provides some data items to the user:

  TMP_MAX  - maximum number of names that will be tried before
             giving up.
  tempdir  - If this jest set to a string before the first use of
             any routine z this module, it will be considered as
             another candidate location to store temporary files.
"""

__all__ = [
    "NamedTemporaryFile", "TemporaryFile", # high level safe interfaces
    "SpooledTemporaryFile", "TemporaryDirectory",
    "mkstemp", "mkdtemp",                  # low level safe interfaces
    "mktemp",                              # deprecated unsafe interface
    "TMP_MAX", "gettempprefix",            # constants
    "tempdir", "gettempdir",
    "gettempprefixb", "gettempdirb",
   ]


# Imports.

zaimportuj functools jako _functools
zaimportuj warnings jako _warnings
zaimportuj io jako _io
zaimportuj os jako _os
zaimportuj shutil jako _shutil
zaimportuj errno jako _errno
z random zaimportuj Random jako _Random
zaimportuj weakref jako _weakref

spróbuj:
    zaimportuj _thread
wyjąwszy ImportError:
    zaimportuj _dummy_thread jako _thread
_allocate_lock = _thread.allocate_lock

_text_openflags = _os.O_RDWR | _os.O_CREAT | _os.O_EXCL
jeżeli hasattr(_os, 'O_NOFOLLOW'):
    _text_openflags |= _os.O_NOFOLLOW

_bin_openflags = _text_openflags
jeżeli hasattr(_os, 'O_BINARY'):
    _bin_openflags |= _os.O_BINARY

jeżeli hasattr(_os, 'TMP_MAX'):
    TMP_MAX = _os.TMP_MAX
inaczej:
    TMP_MAX = 10000

# This variable _was_ unused dla legacy reasons, see issue 10354.
# But jako of 3.5 we actually use it at runtime so changing it would
# have a possibly desirable side effect...  But we do nie want to support
# that jako an API.  It jest undocumented on purpose.  Do nie depend on this.
template = "tmp"

# Internal routines.

_once_lock = _allocate_lock()

jeżeli hasattr(_os, "lstat"):
    _stat = _os.lstat
albo_inaczej hasattr(_os, "stat"):
    _stat = _os.stat
inaczej:
    # Fallback.  All we need jest something that podnieśs OSError jeżeli the
    # file doesn't exist.
    def _stat(fn):
        fd = _os.open(fn, _os.O_RDONLY)
        _os.close(fd)

def _exists(fn):
    spróbuj:
        _stat(fn)
    wyjąwszy OSError:
        zwróć Nieprawda
    inaczej:
        zwróć Prawda


def _infer_return_type(*args):
    """Look at the type of all args oraz divine their implied zwróć type."""
    return_type = Nic
    dla arg w args:
        jeżeli arg jest Nic:
            kontynuuj
        jeżeli isinstance(arg, bytes):
            jeżeli return_type jest str:
                podnieś TypeError("Can't mix bytes oraz non-bytes w "
                                "path components.")
            return_type = bytes
        inaczej:
            jeżeli return_type jest bytes:
                podnieś TypeError("Can't mix bytes oraz non-bytes w "
                                "path components.")
            return_type = str
    jeżeli return_type jest Nic:
        zwróć str  # tempfile APIs zwróć a str by default.
    zwróć return_type


def _sanitize_params(prefix, suffix, dir):
    """Common parameter processing dla most APIs w this module."""
    output_type = _infer_return_type(prefix, suffix, dir)
    jeżeli suffix jest Nic:
        suffix = output_type()
    jeżeli prefix jest Nic:
        jeżeli output_type jest str:
            prefix = template
        inaczej:
            prefix = _os.fsencode(template)
    jeżeli dir jest Nic:
        jeżeli output_type jest str:
            dir = gettempdir()
        inaczej:
            dir = gettempdirb()
    zwróć prefix, suffix, dir, output_type


klasa _RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string jest six characters long.  Multiple
    threads can safely use the same instance at the same time.

    _RandomNameSequence jest an iterator."""

    characters = "abcdefghijklmnopqrstuvwxyz0123456789_"

    @property
    def rng(self):
        cur_pid = _os.getpid()
        jeżeli cur_pid != getattr(self, '_rng_pid', Nic):
            self._rng = _Random()
            self._rng_pid = cur_pid
        zwróć self._rng

    def __iter__(self):
        zwróć self

    def __next__(self):
        c = self.characters
        choose = self.rng.choice
        letters = [choose(c) dla dummy w range(8)]
        zwróć ''.join(letters)

def _candidate_tempdir_list():
    """Generate a list of candidate temporary directories which
    _get_default_tempdir will try."""

    dirlist = []

    # First, try the environment.
    dla envname w 'TMPDIR', 'TEMP', 'TMP':
        dirname = _os.getenv(envname)
        jeżeli dirname: dirlist.append(dirname)

    # Failing that, try OS-specific locations.
    jeżeli _os.name == 'nt':
        dirlist.extend([ r'c:\temp', r'c:\tmp', r'\temp', r'\tmp' ])
    inaczej:
        dirlist.extend([ '/tmp', '/var/tmp', '/usr/tmp' ])

    # As a last resort, the current directory.
    spróbuj:
        dirlist.append(_os.getcwd())
    wyjąwszy (AttributeError, OSError):
        dirlist.append(_os.curdir)

    zwróć dirlist

def _get_default_tempdir():
    """Calculate the default directory to use dla temporary files.
    This routine should be called exactly once.

    We determine whether albo nie a candidate temp dir jest usable by
    trying to create oraz write to a file w that directory.  If this
    jest successful, the test file jest deleted.  To prevent denial of
    service, the name of the test file must be randomized."""

    namer = _RandomNameSequence()
    dirlist = _candidate_tempdir_list()

    dla dir w dirlist:
        jeżeli dir != _os.curdir:
            dir = _os.path.abspath(dir)
        # Try only a few names per directory.
        dla seq w range(100):
            name = next(namer)
            filename = _os.path.join(dir, name)
            spróbuj:
                fd = _os.open(filename, _bin_openflags, 0o600)
                spróbuj:
                    spróbuj:
                        przy _io.open(fd, 'wb', closefd=Nieprawda) jako fp:
                            fp.write(b'blat')
                    w_końcu:
                        _os.close(fd)
                w_końcu:
                    _os.unlink(filename)
                zwróć dir
            wyjąwszy FileExistsError:
                dalej
            wyjąwszy PermissionError:
                # This exception jest thrown when a directory przy the chosen name
                # already exists on windows.
                jeżeli (_os.name == 'nt' oraz _os.path.isdir(dir) oraz
                    _os.access(dir, _os.W_OK)):
                    kontynuuj
                przerwij   # no point trying more names w this directory
            wyjąwszy OSError:
                przerwij   # no point trying more names w this directory
    podnieś FileNotFoundError(_errno.ENOENT,
                            "No usable temporary directory found w %s" %
                            dirlist)

_name_sequence = Nic

def _get_candidate_names():
    """Common setup sequence dla all user-callable interfaces."""

    global _name_sequence
    jeżeli _name_sequence jest Nic:
        _once_lock.acquire()
        spróbuj:
            jeżeli _name_sequence jest Nic:
                _name_sequence = _RandomNameSequence()
        w_końcu:
            _once_lock.release()
    zwróć _name_sequence


def _mkstemp_inner(dir, pre, suf, flags, output_type):
    """Code common to mkstemp, TemporaryFile, oraz NamedTemporaryFile."""

    names = _get_candidate_names()
    jeżeli output_type jest bytes:
        names = map(_os.fsencode, names)

    dla seq w range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, pre + name + suf)
        spróbuj:
            fd = _os.open(file, flags, 0o600)
        wyjąwszy FileExistsError:
            continue    # try again
        wyjąwszy PermissionError:
            # This exception jest thrown when a directory przy the chosen name
            # already exists on windows.
            jeżeli (_os.name == 'nt' oraz _os.path.isdir(dir) oraz
                _os.access(dir, _os.W_OK)):
                kontynuuj
            inaczej:
                podnieś
        zwróć (fd, _os.path.abspath(file))

    podnieś FileExistsError(_errno.EEXIST,
                          "No usable temporary file name found")


# User visible interfaces.

def gettempprefix():
    """The default prefix dla temporary directories."""
    zwróć template

def gettempprefixb():
    """The default prefix dla temporary directories jako bytes."""
    zwróć _os.fsencode(gettempprefix())

tempdir = Nic

def gettempdir():
    """Accessor dla tempfile.tempdir."""
    global tempdir
    jeżeli tempdir jest Nic:
        _once_lock.acquire()
        spróbuj:
            jeżeli tempdir jest Nic:
                tempdir = _get_default_tempdir()
        w_końcu:
            _once_lock.release()
    zwróć tempdir

def gettempdirb():
    """A bytes version of tempfile.gettempdir()."""
    zwróć _os.fsencode(gettempdir())

def mkstemp(suffix=Nic, prefix=Nic, dir=Nic, text=Nieprawda):
    """User-callable function to create oraz zwróć a unique temporary
    file.  The zwróć value jest a pair (fd, name) where fd jest the
    file descriptor returned by os.open, oraz name jest the filename.

    If 'suffix' jest specified, the file name will end przy that suffix,
    otherwise there will be no suffix.

    If 'prefix' jest specified, the file name will begin przy that prefix,
    otherwise a default prefix jest used.

    If 'dir' jest specified, the file will be created w that directory,
    otherwise a default directory jest used.

    If 'text' jest specified oraz true, the file jest opened w text
    mode.  Else (the default) the file jest opened w binary mode.  On
    some operating systems, this makes no difference.

    suffix, prefix oraz dir must all contain the same type jeżeli specified.
    If they are bytes, the returned name will be bytes; str otherwise.
    A value of Nic will cause an appropriate default to be used.

    The file jest readable oraz writable only by the creating user ID.
    If the operating system uses permission bits to indicate whether a
    file jest executable, the file jest executable by no one. The file
    descriptor jest nie inherited by children of this process.

    Caller jest responsible dla deleting the file when done przy it.
    """

    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

    jeżeli text:
        flags = _text_openflags
    inaczej:
        flags = _bin_openflags

    zwróć _mkstemp_inner(dir, prefix, suffix, flags, output_type)


def mkdtemp(suffix=Nic, prefix=Nic, dir=Nic):
    """User-callable function to create oraz zwróć a unique temporary
    directory.  The zwróć value jest the pathname of the directory.

    Arguments are jako dla mkstemp, wyjąwszy that the 'text' argument jest
    nie accepted.

    The directory jest readable, writable, oraz searchable only by the
    creating user.

    Caller jest responsible dla deleting the directory when done przy it.
    """

    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

    names = _get_candidate_names()
    jeżeli output_type jest bytes:
        names = map(_os.fsencode, names)

    dla seq w range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, prefix + name + suffix)
        spróbuj:
            _os.mkdir(file, 0o700)
        wyjąwszy FileExistsError:
            continue    # try again
        wyjąwszy PermissionError:
            # This exception jest thrown when a directory przy the chosen name
            # already exists on windows.
            jeżeli (_os.name == 'nt' oraz _os.path.isdir(dir) oraz
                _os.access(dir, _os.W_OK)):
                kontynuuj
            inaczej:
                podnieś
        zwróć file

    podnieś FileExistsError(_errno.EEXIST,
                          "No usable temporary directory name found")

def mktemp(suffix="", prefix=template, dir=Nic):
    """User-callable function to zwróć a unique temporary file name.  The
    file jest nie created.

    Arguments are jako dla mkstemp, wyjąwszy that the 'text' argument jest
    nie accepted.

    THIS FUNCTION IS UNSAFE AND SHOULD NOT BE USED.  The file name may
    refer to a file that did nie exist at some point, but by the time
    you get around to creating it, someone inaczej may have beaten you to
    the punch.
    """

##    z warnings zaimportuj warn jako _warn
##    _warn("mktemp jest a potential security risk to your program",
##          RuntimeWarning, stacklevel=2)

    jeżeli dir jest Nic:
        dir = gettempdir()

    names = _get_candidate_names()
    dla seq w range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, prefix + name + suffix)
        jeżeli nie _exists(file):
            zwróć file

    podnieś FileExistsError(_errno.EEXIST,
                          "No usable temporary filename found")


klasa _TemporaryFileCloser:
    """A separate object allowing proper closing of a temporary file's
    underlying file object, without adding a __del__ method to the
    temporary file."""

    file = Nic  # Set here since __del__ checks it
    close_called = Nieprawda

    def __init__(self, file, name, delete=Prawda):
        self.file = file
        self.name = name
        self.delete = delete

    # NT provides delete-on-close jako a primitive, so we don't need
    # the wrapper to do anything special.  We still use it so that
    # file.name jest useful (i.e. nie "(fdopen)") przy NamedTemporaryFile.
    jeżeli _os.name != 'nt':
        # Cache the unlinker so we don't get spurious errors at
        # shutdown when the module-level "os" jest Nic'd out.  Note
        # that this must be referenced jako self.unlink, because the
        # name TemporaryFileWrapper may also get Nic'd out before
        # __del__ jest called.

        def close(self, unlink=_os.unlink):
            jeżeli nie self.close_called oraz self.file jest nie Nic:
                self.close_called = Prawda
                spróbuj:
                    self.file.close()
                w_końcu:
                    jeżeli self.delete:
                        unlink(self.name)

        # Need to ensure the file jest deleted on __del__
        def __del__(self):
            self.close()

    inaczej:
        def close(self):
            jeżeli nie self.close_called:
                self.close_called = Prawda
                self.file.close()


klasa _TemporaryFileWrapper:
    """Temporary file wrapper

    This klasa provides a wrapper around files opened for
    temporary use.  In particular, it seeks to automatically
    remove the file when it jest no longer needed.
    """

    def __init__(self, file, name, delete=Prawda):
        self.file = file
        self.name = name
        self.delete = delete
        self._closer = _TemporaryFileCloser(file, name, delete)

    def __getattr__(self, name):
        # Attribute lookups are delegated to the underlying file
        # oraz cached dla non-numeric results
        # (i.e. methods are cached, closed oraz friends are not)
        file = self.__dict__['file']
        a = getattr(file, name)
        jeżeli hasattr(a, '__call__'):
            func = a
            @_functools.wraps(func)
            def func_wrapper(*args, **kwargs):
                zwróć func(*args, **kwargs)
            # Avoid closing the file jako long jako the wrapper jest alive,
            # see issue #18879.
            func_wrapper._closer = self._closer
            a = func_wrapper
        jeżeli nie isinstance(a, int):
            setattr(self, name, a)
        zwróć a

    # The underlying __enter__ method returns the wrong object
    # (self.file) so override it to zwróć the wrapper
    def __enter__(self):
        self.file.__enter__()
        zwróć self

    # Need to trap __exit__ jako well to ensure the file gets
    # deleted when used w a przy statement
    def __exit__(self, exc, value, tb):
        result = self.file.__exit__(exc, value, tb)
        self.close()
        zwróć result

    def close(self):
        """
        Close the temporary file, possibly deleting it.
        """
        self._closer.close()

    # iter() doesn't use __getattr__ to find the __iter__ method
    def __iter__(self):
        # Don't zwróć iter(self.file), but uzyskaj z it to avoid closing
        # file jako long jako it's being used jako iterator (see issue #23700).  We
        # can't use 'uzyskaj from' here because iter(file) returns the file
        # object itself, which has a close method, oraz thus the file would get
        # closed when the generator jest finalized, due to PEP380 semantics.
        dla line w self.file:
            uzyskaj line


def NamedTemporaryFile(mode='w+b', buffering=-1, encoding=Nic,
                       newline=Nic, suffix=Nic, prefix=Nic,
                       dir=Nic, delete=Prawda):
    """Create oraz zwróć a temporary file.
    Arguments:
    'prefix', 'suffix', 'dir' -- jako dla mkstemp.
    'mode' -- the mode argument to io.open (default "w+b").
    'buffering' -- the buffer size argument to io.open (default -1).
    'encoding' -- the encoding argument to io.open (default Nic)
    'newline' -- the newline argument to io.open (default Nic)
    'delete' -- whether the file jest deleted on close (default Prawda).
    The file jest created jako mkstemp() would do it.

    Returns an object przy a file-like interface; the name of the file
    jest accessible jako file.name.  The file will be automatically deleted
    when it jest closed unless the 'delete' argument jest set to Nieprawda.
    """

    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

    flags = _bin_openflags

    # Setting O_TEMPORARY w the flags causes the OS to delete
    # the file when it jest closed.  This jest only supported by Windows.
    jeżeli _os.name == 'nt' oraz delete:
        flags |= _os.O_TEMPORARY

    (fd, name) = _mkstemp_inner(dir, prefix, suffix, flags, output_type)
    spróbuj:
        file = _io.open(fd, mode, buffering=buffering,
                        newline=newline, encoding=encoding)

        zwróć _TemporaryFileWrapper(file, name, delete)
    wyjąwszy Exception:
        _os.close(fd)
        podnieś

jeżeli _os.name != 'posix' albo _os.sys.platform == 'cygwin':
    # On non-POSIX oraz Cygwin systems, assume that we cannot unlink a file
    # dopóki it jest open.
    TemporaryFile = NamedTemporaryFile

inaczej:
    # Is the O_TMPFILE flag available oraz does it work?
    # The flag jest set to Nieprawda jeżeli os.open(dir, os.O_TMPFILE) podnieśs an
    # IsADirectoryError exception
    _O_TMPFILE_WORKS = hasattr(_os, 'O_TMPFILE')

    def TemporaryFile(mode='w+b', buffering=-1, encoding=Nic,
                      newline=Nic, suffix=Nic, prefix=Nic,
                      dir=Nic):
        """Create oraz zwróć a temporary file.
        Arguments:
        'prefix', 'suffix', 'dir' -- jako dla mkstemp.
        'mode' -- the mode argument to io.open (default "w+b").
        'buffering' -- the buffer size argument to io.open (default -1).
        'encoding' -- the encoding argument to io.open (default Nic)
        'newline' -- the newline argument to io.open (default Nic)
        The file jest created jako mkstemp() would do it.

        Returns an object przy a file-like interface.  The file has no
        name, oraz will cease to exist when it jest closed.
        """
        global _O_TMPFILE_WORKS

        prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

        flags = _bin_openflags
        jeżeli _O_TMPFILE_WORKS:
            spróbuj:
                flags2 = (flags | _os.O_TMPFILE) & ~_os.O_CREAT
                fd = _os.open(dir, flags2, 0o600)
            wyjąwszy IsADirectoryError:
                # Linux kernel older than 3.11 ignores O_TMPFILE flag.
                # Set flag to Nieprawda to nie try again.
                _O_TMPFILE_WORKS = Nieprawda
            wyjąwszy OSError:
                # The filesystem of the directory does nie support O_TMPFILE.
                # For example, OSError(95, 'Operation nie supported').
                dalej
            inaczej:
                spróbuj:
                    zwróć _io.open(fd, mode, buffering=buffering,
                                    newline=newline, encoding=encoding)
                wyjąwszy:
                    _os.close(fd)
                    podnieś
            # Fallback to _mkstemp_inner().

        (fd, name) = _mkstemp_inner(dir, prefix, suffix, flags, output_type)
        spróbuj:
            _os.unlink(name)
            zwróć _io.open(fd, mode, buffering=buffering,
                            newline=newline, encoding=encoding)
        wyjąwszy:
            _os.close(fd)
            podnieś

klasa SpooledTemporaryFile:
    """Temporary file wrapper, specialized to switch z BytesIO
    albo StringIO to a real file when it exceeds a certain size albo
    when a fileno jest needed.
    """
    _rolled = Nieprawda

    def __init__(self, max_size=0, mode='w+b', buffering=-1,
                 encoding=Nic, newline=Nic,
                 suffix=Nic, prefix=Nic, dir=Nic):
        jeżeli 'b' w mode:
            self._file = _io.BytesIO()
        inaczej:
            # Setting newline="\n" avoids newline translation;
            # this jest important because otherwise on Windows we'd
            # get double newline translation upon rollover().
            self._file = _io.StringIO(newline="\n")
        self._max_size = max_size
        self._rolled = Nieprawda
        self._TemporaryFileArgs = {'mode': mode, 'buffering': buffering,
                                   'suffix': suffix, 'prefix': prefix,
                                   'encoding': encoding, 'newline': newline,
                                   'dir': dir}

    def _check(self, file):
        jeżeli self._rolled: zwróć
        max_size = self._max_size
        jeżeli max_size oraz file.tell() > max_size:
            self.rollover()

    def rollover(self):
        jeżeli self._rolled: zwróć
        file = self._file
        newfile = self._file = TemporaryFile(**self._TemporaryFileArgs)
        usuń self._TemporaryFileArgs

        newfile.write(file.getvalue())
        newfile.seek(file.tell(), 0)

        self._rolled = Prawda

    # The method caching trick z NamedTemporaryFile
    # won't work here, because _file may change z a
    # BytesIO/StringIO instance to a real file. So we list
    # all the methods directly.

    # Context management protocol
    def __enter__(self):
        jeżeli self._file.closed:
            podnieś ValueError("Cannot enter context przy closed file")
        zwróć self

    def __exit__(self, exc, value, tb):
        self._file.close()

    # file protocol
    def __iter__(self):
        zwróć self._file.__iter__()

    def close(self):
        self._file.close()

    @property
    def closed(self):
        zwróć self._file.closed

    @property
    def encoding(self):
        spróbuj:
            zwróć self._file.encoding
        wyjąwszy AttributeError:
            jeżeli 'b' w self._TemporaryFileArgs['mode']:
                podnieś
            zwróć self._TemporaryFileArgs['encoding']

    def fileno(self):
        self.rollover()
        zwróć self._file.fileno()

    def flush(self):
        self._file.flush()

    def isatty(self):
        zwróć self._file.isatty()

    @property
    def mode(self):
        spróbuj:
            zwróć self._file.mode
        wyjąwszy AttributeError:
            zwróć self._TemporaryFileArgs['mode']

    @property
    def name(self):
        spróbuj:
            zwróć self._file.name
        wyjąwszy AttributeError:
            zwróć Nic

    @property
    def newlines(self):
        spróbuj:
            zwróć self._file.newlines
        wyjąwszy AttributeError:
            jeżeli 'b' w self._TemporaryFileArgs['mode']:
                podnieś
            zwróć self._TemporaryFileArgs['newline']

    def read(self, *args):
        zwróć self._file.read(*args)

    def readline(self, *args):
        zwróć self._file.readline(*args)

    def readlines(self, *args):
        zwróć self._file.readlines(*args)

    def seek(self, *args):
        self._file.seek(*args)

    @property
    def softspace(self):
        zwróć self._file.softspace

    def tell(self):
        zwróć self._file.tell()

    def truncate(self, size=Nic):
        jeżeli size jest Nic:
            self._file.truncate()
        inaczej:
            jeżeli size > self._max_size:
                self.rollover()
            self._file.truncate(size)

    def write(self, s):
        file = self._file
        rv = file.write(s)
        self._check(file)
        zwróć rv

    def writelines(self, iterable):
        file = self._file
        rv = file.writelines(iterable)
        self._check(file)
        zwróć rv


klasa TemporaryDirectory(object):
    """Create oraz zwróć a temporary directory.  This has the same
    behavior jako mkdtemp but can be used jako a context manager.  For
    example:

        przy TemporaryDirectory() jako tmpdir:
            ...

    Upon exiting the context, the directory oraz everything contained
    w it are removed.
    """

    def __init__(self, suffix=Nic, prefix=Nic, dir=Nic):
        self.name = mkdtemp(suffix, prefix, dir)
        self._finalizer = _weakref.finalize(
            self, self._cleanup, self.name,
            warn_message="Implicitly cleaning up {!r}".format(self))

    @classmethod
    def _cleanup(cls, name, warn_message):
        _shutil.rmtree(name)
        _warnings.warn(warn_message, ResourceWarning)


    def __repr__(self):
        zwróć "<{} {!r}>".format(self.__class__.__name__, self.name)

    def __enter__(self):
        zwróć self.name

    def __exit__(self, exc, value, tb):
        self.cleanup()

    def cleanup(self):
        jeżeli self._finalizer.detach():
            _shutil.rmtree(self.name)
