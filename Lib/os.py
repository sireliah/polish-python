r"""OS routines dla NT albo Posix depending on what system we're on.

This exports:
  - all functions z posix, nt albo ce, e.g. unlink, stat, etc.
  - os.path jest either posixpath albo ntpath
  - os.name jest either 'posix', 'nt' albo 'ce'.
  - os.curdir jest a string representing the current directory ('.' albo ':')
  - os.pardir jest a string representing the parent directory ('..' albo '::')
  - os.sep jest the (or a most common) pathname separator ('/' albo ':' albo '\\')
  - os.extsep jest the extension separator (always '.')
  - os.altsep jest the alternate pathname separator (Nic albo '/')
  - os.pathsep jest the component separator used w $PATH etc
  - os.linesep jest the line separator w text files ('\r' albo '\n' albo '\r\n')
  - os.defpath jest the default search path dla executables
  - os.devnull jest the file path of the null device ('/dev/null', etc.)

Programs that zaimportuj oraz use 'os' stand a better chance of being
portable between different platforms.  Of course, they must then
only use functions that are defined by all platforms (e.g., unlink
and opendir), oraz leave all pathname manipulation to os.path
(e.g., split oraz join).
"""

#'

zaimportuj sys, errno
zaimportuj stat jako st

_names = sys.builtin_module_names

# Note:  more names are added to __all__ later.
__all__ = ["altsep", "curdir", "pardir", "sep", "pathsep", "linesep",
           "defpath", "name", "path", "devnull", "SEEK_SET", "SEEK_CUR",
           "SEEK_END", "fsencode", "fsdecode", "get_exec_path", "fdopen",
           "popen", "extsep"]

def _exists(name):
    zwróć name w globals()

def _get_exports_list(module):
    spróbuj:
        zwróć list(module.__all__)
    wyjąwszy AttributeError:
        zwróć [n dla n w dir(module) jeżeli n[0] != '_']

# Any new dependencies of the os module and/or changes w path separator
# requires updating importlib jako well.
jeżeli 'posix' w _names:
    name = 'posix'
    linesep = '\n'
    z posix zaimportuj *
    spróbuj:
        z posix zaimportuj _exit
        __all__.append('_exit')
    wyjąwszy ImportError:
        dalej
    zaimportuj posixpath jako path

    spróbuj:
        z posix zaimportuj _have_functions
    wyjąwszy ImportError:
        dalej

    zaimportuj posix
    __all__.extend(_get_exports_list(posix))
    usuń posix

albo_inaczej 'nt' w _names:
    name = 'nt'
    linesep = '\r\n'
    z nt zaimportuj *
    spróbuj:
        z nt zaimportuj _exit
        __all__.append('_exit')
    wyjąwszy ImportError:
        dalej
    zaimportuj ntpath jako path

    zaimportuj nt
    __all__.extend(_get_exports_list(nt))
    usuń nt

    spróbuj:
        z nt zaimportuj _have_functions
    wyjąwszy ImportError:
        dalej

albo_inaczej 'ce' w _names:
    name = 'ce'
    linesep = '\r\n'
    z ce zaimportuj *
    spróbuj:
        z ce zaimportuj _exit
        __all__.append('_exit')
    wyjąwszy ImportError:
        dalej
    # We can use the standard Windows path.
    zaimportuj ntpath jako path

    zaimportuj ce
    __all__.extend(_get_exports_list(ce))
    usuń ce

    spróbuj:
        z ce zaimportuj _have_functions
    wyjąwszy ImportError:
        dalej

inaczej:
    podnieś ImportError('no os specific module found')

sys.modules['os.path'] = path
z os.path zaimportuj (curdir, pardir, sep, pathsep, defpath, extsep, altsep,
    devnull)

usuń _names


jeżeli _exists("_have_functions"):
    _globals = globals()
    def _add(str, fn):
        jeżeli (fn w _globals) oraz (str w _have_functions):
            _set.add(_globals[fn])

    _set = set()
    _add("HAVE_FACCESSAT",  "access")
    _add("HAVE_FCHMODAT",   "chmod")
    _add("HAVE_FCHOWNAT",   "chown")
    _add("HAVE_FSTATAT",    "stat")
    _add("HAVE_FUTIMESAT",  "utime")
    _add("HAVE_LINKAT",     "link")
    _add("HAVE_MKDIRAT",    "mkdir")
    _add("HAVE_MKFIFOAT",   "mkfifo")
    _add("HAVE_MKNODAT",    "mknod")
    _add("HAVE_OPENAT",     "open")
    _add("HAVE_READLINKAT", "readlink")
    _add("HAVE_RENAMEAT",   "rename")
    _add("HAVE_SYMLINKAT",  "symlink")
    _add("HAVE_UNLINKAT",   "unlink")
    _add("HAVE_UNLINKAT",   "rmdir")
    _add("HAVE_UTIMENSAT",  "utime")
    supports_dir_fd = _set

    _set = set()
    _add("HAVE_FACCESSAT",  "access")
    supports_effective_ids = _set

    _set = set()
    _add("HAVE_FCHDIR",     "chdir")
    _add("HAVE_FCHMOD",     "chmod")
    _add("HAVE_FCHOWN",     "chown")
    _add("HAVE_FDOPENDIR",  "listdir")
    _add("HAVE_FEXECVE",    "execve")
    _set.add(stat) # fstat always works
    _add("HAVE_FTRUNCATE",  "truncate")
    _add("HAVE_FUTIMENS",   "utime")
    _add("HAVE_FUTIMES",    "utime")
    _add("HAVE_FPATHCONF",  "pathconf")
    jeżeli _exists("statvfs") oraz _exists("fstatvfs"): # mac os x10.3
        _add("HAVE_FSTATVFS", "statvfs")
    supports_fd = _set

    _set = set()
    _add("HAVE_FACCESSAT",  "access")
    # Some platforms don't support lchmod().  Often the function exists
    # anyway, jako a stub that always returns ENOSUP albo perhaps EOPNOTSUPP.
    # (No, I don't know why that's a good design.)  ./configure will detect
    # this oraz reject it--so HAVE_LCHMOD still won't be defined on such
    # platforms.  This jest Very Helpful.
    #
    # However, sometimes platforms without a working lchmod() *do* have
    # fchmodat().  (Examples: Linux kernel 3.2 przy glibc 2.15,
    # OpenIndiana 3.x.)  And fchmodat() has a flag that theoretically makes
    # it behave like lchmod().  So w theory it would be a suitable
    # replacement dla lchmod().  But when lchmod() doesn't work, fchmodat()'s
    # flag doesn't work *either*.  Sadly ./configure isn't sophisticated
    # enough to detect this condition--it only determines whether albo nie
    # fchmodat() minimally works.
    #
    # Therefore we simply ignore fchmodat() when deciding whether albo nie
    # os.chmod supports follow_symlinks.  Just checking lchmod() jest
    # sufficient.  After all--jeżeli you have a working fchmodat(), your
    # lchmod() almost certainly works too.
    #
    # _add("HAVE_FCHMODAT",   "chmod")
    _add("HAVE_FCHOWNAT",   "chown")
    _add("HAVE_FSTATAT",    "stat")
    _add("HAVE_LCHFLAGS",   "chflags")
    _add("HAVE_LCHMOD",     "chmod")
    jeżeli _exists("lchown"): # mac os x10.3
        _add("HAVE_LCHOWN", "chown")
    _add("HAVE_LINKAT",     "link")
    _add("HAVE_LUTIMES",    "utime")
    _add("HAVE_LSTAT",      "stat")
    _add("HAVE_FSTATAT",    "stat")
    _add("HAVE_UTIMENSAT",  "utime")
    _add("MS_WINDOWS",      "stat")
    supports_follow_symlinks = _set

    usuń _set
    usuń _have_functions
    usuń _globals
    usuń _add


# Python uses fixed values dla the SEEK_ constants; they are mapped
# to native constants jeżeli necessary w posixmodule.c
# Other possible SEEK values are directly imported z posixmodule.c
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

# Super directory utilities.
# (Inspired by Eric Raymond; the doc strings are mostly his)

def makedirs(name, mode=0o777, exist_ok=Nieprawda):
    """makedirs(name [, mode=0o777][, exist_ok=Nieprawda])

    Super-mkdir; create a leaf directory oraz all intermediate ones.  Works like
    mkdir, wyjąwszy that any intermediate path segment (nie just the rightmost)
    will be created jeżeli it does nie exist. If the target directory already
    exists, podnieś an OSError jeżeli exist_ok jest Nieprawda. Otherwise no exception jest
    podnieśd.  This jest recursive.

    """
    head, tail = path.split(name)
    jeżeli nie tail:
        head, tail = path.split(head)
    jeżeli head oraz tail oraz nie path.exists(head):
        spróbuj:
            makedirs(head, mode, exist_ok)
        wyjąwszy FileExistsError:
            # be happy jeżeli someone already created the path
            dalej
        cdir = curdir
        jeżeli isinstance(tail, bytes):
            cdir = bytes(curdir, 'ASCII')
        jeżeli tail == cdir:           # xxx/newdir/. exists jeżeli xxx/newdir exists
            zwróć
    spróbuj:
        mkdir(name, mode)
    wyjąwszy OSError jako e:
        jeżeli nie exist_ok albo e.errno != errno.EEXIST albo nie path.isdir(name):
            podnieś

def removedirs(name):
    """removedirs(name)

    Super-rmdir; remove a leaf directory oraz all empty intermediate
    ones.  Works like rmdir wyjąwszy that, jeżeli the leaf directory jest
    successfully removed, directories corresponding to rightmost path
    segments will be pruned away until either the whole path jest
    consumed albo an error occurs.  Errors during this latter phase are
    ignored -- they generally mean that a directory was nie empty.

    """
    rmdir(name)
    head, tail = path.split(name)
    jeżeli nie tail:
        head, tail = path.split(head)
    dopóki head oraz tail:
        spróbuj:
            rmdir(head)
        wyjąwszy OSError:
            przerwij
        head, tail = path.split(head)

def renames(old, new):
    """renames(old, new)

    Super-rename; create directories jako necessary oraz delete any left
    empty.  Works like rename, wyjąwszy creation of any intermediate
    directories needed to make the new pathname good jest attempted
    first.  After the rename, directories corresponding to rightmost
    path segments of the old name will be pruned until either the
    whole path jest consumed albo a nonempty directory jest found.

    Note: this function can fail przy the new directory structure made
    jeżeli you lack permissions needed to unlink the leaf directory albo
    file.

    """
    head, tail = path.split(new)
    jeżeli head oraz tail oraz nie path.exists(head):
        makedirs(head)
    rename(old, new)
    head, tail = path.split(old)
    jeżeli head oraz tail:
        spróbuj:
            removedirs(head)
        wyjąwszy OSError:
            dalej

__all__.extend(["makedirs", "removedirs", "renames"])

def walk(top, topdown=Prawda, onerror=Nic, followlinks=Nieprawda):
    """Directory tree generator.

    For each directory w the directory tree rooted at top (including top
    itself, but excluding '.' oraz '..'), uzyskajs a 3-tuple

        dirpath, dirnames, filenames

    dirpath jest a string, the path to the directory.  dirnames jest a list of
    the names of the subdirectories w dirpath (excluding '.' oraz '..').
    filenames jest a list of the names of the non-directory files w dirpath.
    Note that the names w the lists are just names, przy no path components.
    To get a full path (which begins przy top) to a file albo directory w
    dirpath, do os.path.join(dirpath, name).

    If optional arg 'topdown' jest true albo nie specified, the triple dla a
    directory jest generated before the triples dla any of its subdirectories
    (directories are generated top down).  If topdown jest false, the triple
    dla a directory jest generated after the triples dla all of its
    subdirectories (directories are generated bottom up).

    When topdown jest true, the caller can modify the dirnames list in-place
    (e.g., via usuń albo slice assignment), oraz walk will only recurse into the
    subdirectories whose names remain w dirnames; this can be used to prune the
    search, albo to impose a specific order of visiting.  Modifying dirnames when
    topdown jest false jest ineffective, since the directories w dirnames have
    already been generated by the time dirnames itself jest generated. No matter
    the value of topdown, the list of subdirectories jest retrieved before the
    tuples dla the directory oraz its subdirectories are generated.

    By default errors z the os.scandir() call are ignored.  If
    optional arg 'onerror' jest specified, it should be a function; it
    will be called przy one argument, an OSError instance.  It can
    report the error to continue przy the walk, albo podnieś the exception
    to abort the walk.  Note that the filename jest available jako the
    filename attribute of the exception object.

    By default, os.walk does nie follow symbolic links to subdirectories on
    systems that support them.  In order to get this functionality, set the
    optional argument 'followlinks' to true.

    Caution:  jeżeli you dalej a relative pathname dla top, don't change the
    current working directory between resumptions of walk.  walk never
    changes the current directory, oraz assumes that the client doesn't
    either.

    Example:

    zaimportuj os
    z os.path zaimportuj join, getsize
    dla root, dirs, files w os.walk('python/Lib/email'):
        print(root, "consumes", end="")
        print(sum([getsize(join(root, name)) dla name w files]), end="")
        print("bytes in", len(files), "non-directory files")
        jeżeli 'CVS' w dirs:
            dirs.remove('CVS')  # don't visit CVS directories

    """

    dirs = []
    nondirs = []

    # We may nie have read permission dla top, w which case we can't
    # get a list of the files the directory contains.  os.walk
    # always suppressed the exception then, rather than blow up dla a
    # minor reason when (say) a thousand readable directories are still
    # left to visit.  That logic jest copied here.
    spróbuj:
        # Note that scandir jest global w this module due
        # to earlier import-*.
        scandir_it = scandir(top)
    wyjąwszy OSError jako error:
        jeżeli onerror jest nie Nic:
            onerror(error)
        zwróć

    dopóki Prawda:
        spróbuj:
            spróbuj:
                entry = next(scandir_it)
            wyjąwszy StopIteration:
                przerwij
        wyjąwszy OSError jako error:
            jeżeli onerror jest nie Nic:
                onerror(error)
            zwróć

        spróbuj:
            is_dir = entry.is_dir()
        wyjąwszy OSError:
            # If is_dir() podnieśs an OSError, consider that the entry jest nie
            # a directory, same behaviour than os.path.isdir().
            is_dir = Nieprawda

        jeżeli is_dir:
            dirs.append(entry.name)
        inaczej:
            nondirs.append(entry.name)

        jeżeli nie topdown oraz is_dir:
            # Bottom-up: recurse into sub-directory, but exclude symlinks to
            # directories jeżeli followlinks jest Nieprawda
            jeżeli followlinks:
                walk_into = Prawda
            inaczej:
                spróbuj:
                    is_symlink = entry.is_symlink()
                wyjąwszy OSError:
                    # If is_symlink() podnieśs an OSError, consider that the
                    # entry jest nie a symbolic link, same behaviour than
                    # os.path.islink().
                    is_symlink = Nieprawda
                walk_into = nie is_symlink

            jeżeli walk_into:
                uzyskaj z walk(entry.path, topdown, onerror, followlinks)

    # Yield before recursion jeżeli going top down
    jeżeli topdown:
        uzyskaj top, dirs, nondirs

        # Recurse into sub-directories
        islink, join = path.islink, path.join
        dla name w dirs:
            new_path = join(top, name)
            # Issue #23605: os.path.islink() jest used instead of caching
            # entry.is_symlink() result during the loop on os.scandir() because
            # the caller can replace the directory entry during the "uzyskaj"
            # above.
            jeżeli followlinks albo nie islink(new_path):
                uzyskaj z walk(new_path, topdown, onerror, followlinks)
    inaczej:
        # Yield after recursion jeżeli going bottom up
        uzyskaj top, dirs, nondirs

__all__.append("walk")

jeżeli {open, stat} <= supports_dir_fd oraz {listdir, stat} <= supports_fd:

    def fwalk(top=".", topdown=Prawda, onerror=Nic, *, follow_symlinks=Nieprawda, dir_fd=Nic):
        """Directory tree generator.

        This behaves exactly like walk(), wyjąwszy that it uzyskajs a 4-tuple

            dirpath, dirnames, filenames, dirfd

        `dirpath`, `dirnames` oraz `filenames` are identical to walk() output,
        oraz `dirfd` jest a file descriptor referring to the directory `dirpath`.

        The advantage of fwalk() over walk() jest that it's safe against symlink
        races (when follow_symlinks jest Nieprawda).

        If dir_fd jest nie Nic, it should be a file descriptor open to a directory,
          oraz top should be relative; top will then be relative to that directory.
          (dir_fd jest always supported dla fwalk.)

        Caution:
        Since fwalk() uzyskajs file descriptors, those are only valid until the
        next iteration step, so you should dup() them jeżeli you want to keep them
        dla a longer period.

        Example:

        zaimportuj os
        dla root, dirs, files, rootfd w os.fwalk('python/Lib/email'):
            print(root, "consumes", end="")
            print(sum([os.stat(name, dir_fd=rootfd).st_size dla name w files]),
                  end="")
            print("bytes in", len(files), "non-directory files")
            jeżeli 'CVS' w dirs:
                dirs.remove('CVS')  # don't visit CVS directories
        """
        # Note: To guard against symlink races, we use the standard
        # lstat()/open()/fstat() trick.
        orig_st = stat(top, follow_symlinks=Nieprawda, dir_fd=dir_fd)
        topfd = open(top, O_RDONLY, dir_fd=dir_fd)
        spróbuj:
            jeżeli (follow_symlinks albo (st.S_ISDIR(orig_st.st_mode) oraz
                                    path.samestat(orig_st, stat(topfd)))):
                uzyskaj z _fwalk(topfd, top, topdown, onerror, follow_symlinks)
        w_końcu:
            close(topfd)

    def _fwalk(topfd, toppath, topdown, onerror, follow_symlinks):
        # Note: This uses O(depth of the directory tree) file descriptors: if
        # necessary, it can be adapted to only require O(1) FDs, see issue
        # #13734.

        names = listdir(topfd)
        dirs, nondirs = [], []
        dla name w names:
            spróbuj:
                # Here, we don't use AT_SYMLINK_NOFOLLOW to be consistent with
                # walk() which reports symlinks to directories jako directories.
                # We do however check dla symlinks before recursing into
                # a subdirectory.
                jeżeli st.S_ISDIR(stat(name, dir_fd=topfd).st_mode):
                    dirs.append(name)
                inaczej:
                    nondirs.append(name)
            wyjąwszy FileNotFoundError:
                spróbuj:
                    # Add dangling symlinks, ignore disappeared files
                    jeżeli st.S_ISLNK(stat(name, dir_fd=topfd, follow_symlinks=Nieprawda)
                                .st_mode):
                        nondirs.append(name)
                wyjąwszy FileNotFoundError:
                    kontynuuj

        jeżeli topdown:
            uzyskaj toppath, dirs, nondirs, topfd

        dla name w dirs:
            spróbuj:
                orig_st = stat(name, dir_fd=topfd, follow_symlinks=follow_symlinks)
                dirfd = open(name, O_RDONLY, dir_fd=topfd)
            wyjąwszy OSError jako err:
                jeżeli onerror jest nie Nic:
                    onerror(err)
                zwróć
            spróbuj:
                jeżeli follow_symlinks albo path.samestat(orig_st, stat(dirfd)):
                    dirpath = path.join(toppath, name)
                    uzyskaj z _fwalk(dirfd, dirpath, topdown, onerror, follow_symlinks)
            w_końcu:
                close(dirfd)

        jeżeli nie topdown:
            uzyskaj toppath, dirs, nondirs, topfd

    __all__.append("fwalk")

# Make sure os.environ exists, at least
spróbuj:
    environ
wyjąwszy NameError:
    environ = {}

def execl(file, *args):
    """execl(file, *args)

    Execute the executable file przy argument list args, replacing the
    current process. """
    execv(file, args)

def execle(file, *args):
    """execle(file, *args, env)

    Execute the executable file przy argument list args oraz
    environment env, replacing the current process. """
    env = args[-1]
    execve(file, args[:-1], env)

def execlp(file, *args):
    """execlp(file, *args)

    Execute the executable file (which jest searched dla along $PATH)
    przy argument list args, replacing the current process. """
    execvp(file, args)

def execlpe(file, *args):
    """execlpe(file, *args, env)

    Execute the executable file (which jest searched dla along $PATH)
    przy argument list args oraz environment env, replacing the current
    process. """
    env = args[-1]
    execvpe(file, args[:-1], env)

def execvp(file, args):
    """execvp(file, args)

    Execute the executable file (which jest searched dla along $PATH)
    przy argument list args, replacing the current process.
    args may be a list albo tuple of strings. """
    _execvpe(file, args)

def execvpe(file, args, env):
    """execvpe(file, args, env)

    Execute the executable file (which jest searched dla along $PATH)
    przy argument list args oraz environment env , replacing the
    current process.
    args may be a list albo tuple of strings. """
    _execvpe(file, args, env)

__all__.extend(["execl","execle","execlp","execlpe","execvp","execvpe"])

def _execvpe(file, args, env=Nic):
    jeżeli env jest nie Nic:
        exec_func = execve
        argrest = (args, env)
    inaczej:
        exec_func = execv
        argrest = (args,)
        env = environ

    head, tail = path.split(file)
    jeżeli head:
        exec_func(file, *argrest)
        zwróć
    last_exc = saved_exc = Nic
    saved_tb = Nic
    path_list = get_exec_path(env)
    jeżeli name != 'nt':
        file = fsencode(file)
        path_list = map(fsencode, path_list)
    dla dir w path_list:
        fullname = path.join(dir, file)
        spróbuj:
            exec_func(fullname, *argrest)
        wyjąwszy OSError jako e:
            last_exc = e
            tb = sys.exc_info()[2]
            jeżeli (e.errno != errno.ENOENT oraz e.errno != errno.ENOTDIR
                oraz saved_exc jest Nic):
                saved_exc = e
                saved_tb = tb
    jeżeli saved_exc:
        podnieś saved_exc.with_traceback(saved_tb)
    podnieś last_exc.with_traceback(tb)


def get_exec_path(env=Nic):
    """Returns the sequence of directories that will be searched dla the
    named executable (similar to a shell) when launching a process.

    *env* must be an environment variable dict albo Nic.  If *env* jest Nic,
    os.environ will be used.
    """
    # Use a local zaimportuj instead of a global zaimportuj to limit the number of
    # modules loaded at startup: the os module jest always loaded at startup by
    # Python. It may also avoid a bootstrap issue.
    zaimportuj warnings

    jeżeli env jest Nic:
        env = environ

    # {b'PATH': ...}.get('PATH') oraz {'PATH': ...}.get(b'PATH') emit a
    # BytesWarning when using python -b albo python -bb: ignore the warning
    przy warnings.catch_warnings():
        warnings.simplefilter("ignore", BytesWarning)

        spróbuj:
            path_list = env.get('PATH')
        wyjąwszy TypeError:
            path_list = Nic

        jeżeli supports_bytes_environ:
            spróbuj:
                path_listb = env[b'PATH']
            wyjąwszy (KeyError, TypeError):
                dalej
            inaczej:
                jeżeli path_list jest nie Nic:
                    podnieś ValueError(
                        "env cannot contain 'PATH' oraz b'PATH' keys")
                path_list = path_listb

            jeżeli path_list jest nie Nic oraz isinstance(path_list, bytes):
                path_list = fsdecode(path_list)

    jeżeli path_list jest Nic:
        path_list = defpath
    zwróć path_list.split(pathsep)


# Change environ to automatically call putenv(), unsetenv jeżeli they exist.
z _collections_abc zaimportuj MutableMapping

klasa _Environ(MutableMapping):
    def __init__(self, data, encodekey, decodekey, encodevalue, decodevalue, putenv, unsetenv):
        self.encodekey = encodekey
        self.decodekey = decodekey
        self.encodevalue = encodevalue
        self.decodevalue = decodevalue
        self.putenv = putenv
        self.unsetenv = unsetenv
        self._data = data

    def __getitem__(self, key):
        spróbuj:
            value = self._data[self.encodekey(key)]
        wyjąwszy KeyError:
            # podnieś KeyError przy the original key value
            podnieś KeyError(key) z Nic
        zwróć self.decodevalue(value)

    def __setitem__(self, key, value):
        key = self.encodekey(key)
        value = self.encodevalue(value)
        self.putenv(key, value)
        self._data[key] = value

    def __delitem__(self, key):
        encodedkey = self.encodekey(key)
        self.unsetenv(encodedkey)
        spróbuj:
            usuń self._data[encodedkey]
        wyjąwszy KeyError:
            # podnieś KeyError przy the original key value
            podnieś KeyError(key) z Nic

    def __iter__(self):
        dla key w self._data:
            uzyskaj self.decodekey(key)

    def __len__(self):
        zwróć len(self._data)

    def __repr__(self):
        zwróć 'environ({{{}}})'.format(', '.join(
            ('{!r}: {!r}'.format(self.decodekey(key), self.decodevalue(value))
            dla key, value w self._data.items())))

    def copy(self):
        zwróć dict(self)

    def setdefault(self, key, value):
        jeżeli key nie w self:
            self[key] = value
        zwróć self[key]

spróbuj:
    _putenv = putenv
wyjąwszy NameError:
    _putenv = lambda key, value: Nic
inaczej:
    jeżeli "putenv" nie w __all__:
        __all__.append("putenv")

spróbuj:
    _unsetenv = unsetenv
wyjąwszy NameError:
    _unsetenv = lambda key: _putenv(key, "")
inaczej:
    jeżeli "unsetenv" nie w __all__:
        __all__.append("unsetenv")

def _createenviron():
    jeżeli name == 'nt':
        # Where Env Var Names Must Be UPPERCASE
        def check_str(value):
            jeżeli nie isinstance(value, str):
                podnieś TypeError("str expected, nie %s" % type(value).__name__)
            zwróć value
        encode = check_str
        decode = str
        def encodekey(key):
            zwróć encode(key).upper()
        data = {}
        dla key, value w environ.items():
            data[encodekey(key)] = value
    inaczej:
        # Where Env Var Names Can Be Mixed Case
        encoding = sys.getfilesystemencoding()
        def encode(value):
            jeżeli nie isinstance(value, str):
                podnieś TypeError("str expected, nie %s" % type(value).__name__)
            zwróć value.encode(encoding, 'surrogateescape')
        def decode(value):
            zwróć value.decode(encoding, 'surrogateescape')
        encodekey = encode
        data = environ
    zwróć _Environ(data,
        encodekey, decode,
        encode, decode,
        _putenv, _unsetenv)

# unicode environ
environ = _createenviron()
usuń _createenviron


def getenv(key, default=Nic):
    """Get an environment variable, zwróć Nic jeżeli it doesn't exist.
    The optional second argument can specify an alternate default.
    key, default oraz the result are str."""
    zwróć environ.get(key, default)

supports_bytes_environ = (name != 'nt')
__all__.extend(("getenv", "supports_bytes_environ"))

jeżeli supports_bytes_environ:
    def _check_bytes(value):
        jeżeli nie isinstance(value, bytes):
            podnieś TypeError("bytes expected, nie %s" % type(value).__name__)
        zwróć value

    # bytes environ
    environb = _Environ(environ._data,
        _check_bytes, bytes,
        _check_bytes, bytes,
        _putenv, _unsetenv)
    usuń _check_bytes

    def getenvb(key, default=Nic):
        """Get an environment variable, zwróć Nic jeżeli it doesn't exist.
        The optional second argument can specify an alternate default.
        key, default oraz the result are bytes."""
        zwróć environb.get(key, default)

    __all__.extend(("environb", "getenvb"))

def _fscodec():
    encoding = sys.getfilesystemencoding()
    jeżeli encoding == 'mbcs':
        errors = 'strict'
    inaczej:
        errors = 'surrogateescape'

    def fsencode(filename):
        """
        Encode filename to the filesystem encoding przy 'surrogateescape' error
        handler, zwróć bytes unchanged. On Windows, use 'strict' error handler if
        the file system encoding jest 'mbcs' (which jest the default encoding).
        """
        jeżeli isinstance(filename, bytes):
            zwróć filename
        albo_inaczej isinstance(filename, str):
            zwróć filename.encode(encoding, errors)
        inaczej:
            podnieś TypeError("expect bytes albo str, nie %s" % type(filename).__name__)

    def fsdecode(filename):
        """
        Decode filename z the filesystem encoding przy 'surrogateescape' error
        handler, zwróć str unchanged. On Windows, use 'strict' error handler if
        the file system encoding jest 'mbcs' (which jest the default encoding).
        """
        jeżeli isinstance(filename, str):
            zwróć filename
        albo_inaczej isinstance(filename, bytes):
            zwróć filename.decode(encoding, errors)
        inaczej:
            podnieś TypeError("expect bytes albo str, nie %s" % type(filename).__name__)

    zwróć fsencode, fsdecode

fsencode, fsdecode = _fscodec()
usuń _fscodec

# Supply spawn*() (probably only dla Unix)
jeżeli _exists("fork") oraz nie _exists("spawnv") oraz _exists("execv"):

    P_WAIT = 0
    P_NOWAIT = P_NOWAITO = 1

    __all__.extend(["P_WAIT", "P_NOWAIT", "P_NOWAITO"])

    # XXX Should we support P_DETACH?  I suppose it could fork()**2
    # oraz close the std I/O streams.  Also, P_OVERLAY jest the same
    # jako execv*()?

    def _spawnvef(mode, file, args, env, func):
        # Internal helper; func jest the exec*() function to use
        pid = fork()
        jeżeli nie pid:
            # Child
            spróbuj:
                jeżeli env jest Nic:
                    func(file, args)
                inaczej:
                    func(file, args, env)
            wyjąwszy:
                _exit(127)
        inaczej:
            # Parent
            jeżeli mode == P_NOWAIT:
                zwróć pid # Caller jest responsible dla waiting!
            dopóki 1:
                wpid, sts = waitpid(pid, 0)
                jeżeli WIFSTOPPED(sts):
                    kontynuuj
                albo_inaczej WIFSIGNALED(sts):
                    zwróć -WTERMSIG(sts)
                albo_inaczej WIFEXITED(sts):
                    zwróć WEXITSTATUS(sts)
                inaczej:
                    podnieś OSError("Not stopped, signaled albo exited???")

    def spawnv(mode, file, args):
        """spawnv(mode, file, args) -> integer

Execute file przy arguments z args w a subprocess.
If mode == P_NOWAIT zwróć the pid of the process.
If mode == P_WAIT zwróć the process's exit code jeżeli it exits normally;
otherwise zwróć -SIG, where SIG jest the signal that killed it. """
        zwróć _spawnvef(mode, file, args, Nic, execv)

    def spawnve(mode, file, args, env):
        """spawnve(mode, file, args, env) -> integer

Execute file przy arguments z args w a subprocess przy the
specified environment.
If mode == P_NOWAIT zwróć the pid of the process.
If mode == P_WAIT zwróć the process's exit code jeżeli it exits normally;
otherwise zwróć -SIG, where SIG jest the signal that killed it. """
        zwróć _spawnvef(mode, file, args, env, execve)

    # Note: spawnvp[e] is't currently supported on Windows

    def spawnvp(mode, file, args):
        """spawnvp(mode, file, args) -> integer

Execute file (which jest looked dla along $PATH) przy arguments from
args w a subprocess.
If mode == P_NOWAIT zwróć the pid of the process.
If mode == P_WAIT zwróć the process's exit code jeżeli it exits normally;
otherwise zwróć -SIG, where SIG jest the signal that killed it. """
        zwróć _spawnvef(mode, file, args, Nic, execvp)

    def spawnvpe(mode, file, args, env):
        """spawnvpe(mode, file, args, env) -> integer

Execute file (which jest looked dla along $PATH) przy arguments from
args w a subprocess przy the supplied environment.
If mode == P_NOWAIT zwróć the pid of the process.
If mode == P_WAIT zwróć the process's exit code jeżeli it exits normally;
otherwise zwróć -SIG, where SIG jest the signal that killed it. """
        zwróć _spawnvef(mode, file, args, env, execvpe)


    __all__.extend(["spawnv", "spawnve", "spawnvp", "spawnvpe"])


jeżeli _exists("spawnv"):
    # These aren't supplied by the basic Windows code
    # but can be easily implemented w Python

    def spawnl(mode, file, *args):
        """spawnl(mode, file, *args) -> integer

Execute file przy arguments z args w a subprocess.
If mode == P_NOWAIT zwróć the pid of the process.
If mode == P_WAIT zwróć the process's exit code jeżeli it exits normally;
otherwise zwróć -SIG, where SIG jest the signal that killed it. """
        zwróć spawnv(mode, file, args)

    def spawnle(mode, file, *args):
        """spawnle(mode, file, *args, env) -> integer

Execute file przy arguments z args w a subprocess przy the
supplied environment.
If mode == P_NOWAIT zwróć the pid of the process.
If mode == P_WAIT zwróć the process's exit code jeżeli it exits normally;
otherwise zwróć -SIG, where SIG jest the signal that killed it. """
        env = args[-1]
        zwróć spawnve(mode, file, args[:-1], env)


    __all__.extend(["spawnl", "spawnle"])


jeżeli _exists("spawnvp"):
    # At the moment, Windows doesn't implement spawnvp[e],
    # so it won't have spawnlp[e] either.
    def spawnlp(mode, file, *args):
        """spawnlp(mode, file, *args) -> integer

Execute file (which jest looked dla along $PATH) przy arguments from
args w a subprocess przy the supplied environment.
If mode == P_NOWAIT zwróć the pid of the process.
If mode == P_WAIT zwróć the process's exit code jeżeli it exits normally;
otherwise zwróć -SIG, where SIG jest the signal that killed it. """
        zwróć spawnvp(mode, file, args)

    def spawnlpe(mode, file, *args):
        """spawnlpe(mode, file, *args, env) -> integer

Execute file (which jest looked dla along $PATH) przy arguments from
args w a subprocess przy the supplied environment.
If mode == P_NOWAIT zwróć the pid of the process.
If mode == P_WAIT zwróć the process's exit code jeżeli it exits normally;
otherwise zwróć -SIG, where SIG jest the signal that killed it. """
        env = args[-1]
        zwróć spawnvpe(mode, file, args[:-1], env)


    __all__.extend(["spawnlp", "spawnlpe"])


# Supply os.popen()
def popen(cmd, mode="r", buffering=-1):
    jeżeli nie isinstance(cmd, str):
        podnieś TypeError("invalid cmd type (%s, expected string)" % type(cmd))
    jeżeli mode nie w ("r", "w"):
        podnieś ValueError("invalid mode %r" % mode)
    jeżeli buffering == 0 albo buffering jest Nic:
        podnieś ValueError("popen() does nie support unbuffered streams")
    zaimportuj subprocess, io
    jeżeli mode == "r":
        proc = subprocess.Popen(cmd,
                                shell=Prawda,
                                stdout=subprocess.PIPE,
                                bufsize=buffering)
        zwróć _wrap_close(io.TextIOWrapper(proc.stdout), proc)
    inaczej:
        proc = subprocess.Popen(cmd,
                                shell=Prawda,
                                stdin=subprocess.PIPE,
                                bufsize=buffering)
        zwróć _wrap_close(io.TextIOWrapper(proc.stdin), proc)

# Helper dla popen() -- a proxy dla a file whose close waits dla the process
klasa _wrap_close:
    def __init__(self, stream, proc):
        self._stream = stream
        self._proc = proc
    def close(self):
        self._stream.close()
        returncode = self._proc.wait()
        jeżeli returncode == 0:
            zwróć Nic
        jeżeli name == 'nt':
            zwróć returncode
        inaczej:
            zwróć returncode << 8  # Shift left to match old behavior
    def __enter__(self):
        zwróć self
    def __exit__(self, *args):
        self.close()
    def __getattr__(self, name):
        zwróć getattr(self._stream, name)
    def __iter__(self):
        zwróć iter(self._stream)

# Supply os.fdopen()
def fdopen(fd, *args, **kwargs):
    jeżeli nie isinstance(fd, int):
        podnieś TypeError("invalid fd type (%s, expected integer)" % type(fd))
    zaimportuj io
    zwróć io.open(fd, *args, **kwargs)
