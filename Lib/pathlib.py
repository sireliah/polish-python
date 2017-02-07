zaimportuj fnmatch
zaimportuj functools
zaimportuj io
zaimportuj ntpath
zaimportuj os
zaimportuj posixpath
zaimportuj re
zaimportuj sys
z collections zaimportuj Sequence
z contextlib zaimportuj contextmanager
z errno zaimportuj EINVAL, ENOENT, ENOTDIR
z operator zaimportuj attrgetter
z stat zaimportuj S_ISDIR, S_ISLNK, S_ISREG, S_ISSOCK, S_ISBLK, S_ISCHR, S_ISFIFO
z urllib.parse zaimportuj quote_from_bytes jako urlquote_from_bytes


supports_symlinks = Prawda
jeżeli os.name == 'nt':
    zaimportuj nt
    jeżeli sys.getwindowsversion()[:2] >= (6, 0):
        z nt zaimportuj _getfinalpathname
    inaczej:
        supports_symlinks = Nieprawda
        _getfinalpathname = Nic
inaczej:
    nt = Nic


__all__ = [
    "PurePath", "PurePosixPath", "PureWindowsPath",
    "Path", "PosixPath", "WindowsPath",
    ]

#
# Internals
#

def _is_wildcard_pattern(pat):
    # Whether this pattern needs actual matching using fnmatch, albo can
    # be looked up directly jako a file.
    zwróć "*" w pat albo "?" w pat albo "[" w pat


klasa _Flavour(object):
    """A flavour implements a particular (platform-specific) set of path
    semantics."""

    def __init__(self):
        self.join = self.sep.join

    def parse_parts(self, parts):
        parsed = []
        sep = self.sep
        altsep = self.altsep
        drv = root = ''
        it = reversed(parts)
        dla part w it:
            jeżeli nie part:
                kontynuuj
            jeżeli altsep:
                part = part.replace(altsep, sep)
            drv, root, rel = self.splitroot(part)
            jeżeli sep w rel:
                dla x w reversed(rel.split(sep)):
                    jeżeli x oraz x != '.':
                        parsed.append(sys.intern(x))
            inaczej:
                jeżeli rel oraz rel != '.':
                    parsed.append(sys.intern(rel))
            jeżeli drv albo root:
                jeżeli nie drv:
                    # If no drive jest present, try to find one w the previous
                    # parts. This makes the result of parsing e.g.
                    # ("C:", "/", "a") reasonably intuitive.
                    dla part w it:
                        jeżeli nie part:
                            kontynuuj
                        jeżeli altsep:
                            part = part.replace(altsep, sep)
                        drv = self.splitroot(part)[0]
                        jeżeli drv:
                            przerwij
                przerwij
        jeżeli drv albo root:
            parsed.append(drv + root)
        parsed.reverse()
        zwróć drv, root, parsed

    def join_parsed_parts(self, drv, root, parts, drv2, root2, parts2):
        """
        Join the two paths represented by the respective
        (drive, root, parts) tuples.  Return a new (drive, root, parts) tuple.
        """
        jeżeli root2:
            jeżeli nie drv2 oraz drv:
                zwróć drv, root2, [drv + root2] + parts2[1:]
        albo_inaczej drv2:
            jeżeli drv2 == drv albo self.casefold(drv2) == self.casefold(drv):
                # Same drive => second path jest relative to the first
                zwróć drv, root, parts + parts2[1:]
        inaczej:
            # Second path jest non-anchored (common case)
            zwróć drv, root, parts + parts2
        zwróć drv2, root2, parts2


klasa _WindowsFlavour(_Flavour):
    # Reference dla Windows paths can be found at
    # http://msdn.microsoft.com/en-us/library/aa365247%28v=vs.85%29.aspx

    sep = '\\'
    altsep = '/'
    has_drv = Prawda
    pathmod = ntpath

    is_supported = (os.name == 'nt')

    drive_letters = (
        set(chr(x) dla x w range(ord('a'), ord('z') + 1)) |
        set(chr(x) dla x w range(ord('A'), ord('Z') + 1))
    )
    ext_namespace_prefix = '\\\\?\\'

    reserved_names = (
        {'CON', 'PRN', 'AUX', 'NUL'} |
        {'COM%d' % i dla i w range(1, 10)} |
        {'LPT%d' % i dla i w range(1, 10)}
        )

    # Interesting findings about extended paths:
    # - '\\?\c:\a', '//?/c:\a' oraz '//?/c:/a' are all supported
    #   but '\\?\c:/a' jest nie
    # - extended paths are always absolute; "relative" extended paths will
    #   fail.

    def splitroot(self, part, sep=sep):
        first = part[0:1]
        second = part[1:2]
        jeżeli (second == sep oraz first == sep):
            # XXX extended paths should also disable the collapsing of "."
            # components (according to MSDN docs).
            prefix, part = self._split_extended_path(part)
            first = part[0:1]
            second = part[1:2]
        inaczej:
            prefix = ''
        third = part[2:3]
        jeżeli (second == sep oraz first == sep oraz third != sep):
            # jest a UNC path:
            # vvvvvvvvvvvvvvvvvvvvv root
            # \\machine\mountpoint\directory\etc\...
            #            directory ^^^^^^^^^^^^^^
            index = part.find(sep, 2)
            jeżeli index != -1:
                index2 = part.find(sep, index + 1)
                # a UNC path can't have two slashes w a row
                # (after the initial two)
                jeżeli index2 != index + 1:
                    jeżeli index2 == -1:
                        index2 = len(part)
                    jeżeli prefix:
                        zwróć prefix + part[1:index2], sep, part[index2+1:]
                    inaczej:
                        zwróć part[:index2], sep, part[index2+1:]
        drv = root = ''
        jeżeli second == ':' oraz first w self.drive_letters:
            drv = part[:2]
            part = part[2:]
            first = third
        jeżeli first == sep:
            root = first
            part = part.lstrip(sep)
        zwróć prefix + drv, root, part

    def casefold(self, s):
        zwróć s.lower()

    def casefold_parts(self, parts):
        zwróć [p.lower() dla p w parts]

    def resolve(self, path):
        s = str(path)
        jeżeli nie s:
            zwróć os.getcwd()
        jeżeli _getfinalpathname jest nie Nic:
            zwróć self._ext_to_normal(_getfinalpathname(s))
        # Means fallback on absolute
        zwróć Nic

    def _split_extended_path(self, s, ext_prefix=ext_namespace_prefix):
        prefix = ''
        jeżeli s.startswith(ext_prefix):
            prefix = s[:4]
            s = s[4:]
            jeżeli s.startswith('UNC\\'):
                prefix += s[:3]
                s = '\\' + s[3:]
        zwróć prefix, s

    def _ext_to_normal(self, s):
        # Turn back an extended path into a normal DOS-like path
        zwróć self._split_extended_path(s)[1]

    def is_reserved(self, parts):
        # NOTE: the rules dla reserved names seem somewhat complicated
        # (e.g. r"..\NUL" jest reserved but nie r"foo\NUL").
        # We err on the side of caution oraz zwróć Prawda dla paths which are
        # nie considered reserved by Windows.
        jeżeli nie parts:
            zwróć Nieprawda
        jeżeli parts[0].startswith('\\\\'):
            # UNC paths are never reserved
            zwróć Nieprawda
        zwróć parts[-1].partition('.')[0].upper() w self.reserved_names

    def make_uri(self, path):
        # Under Windows, file URIs use the UTF-8 encoding.
        drive = path.drive
        jeżeli len(drive) == 2 oraz drive[1] == ':':
            # It's a path on a local drive => 'file:///c:/a/b'
            rest = path.as_posix()[2:].lstrip('/')
            zwróć 'file:///%s/%s' % (
                drive, urlquote_from_bytes(rest.encode('utf-8')))
        inaczej:
            # It's a path on a network drive => 'file://host/share/a/b'
            zwróć 'file:' + urlquote_from_bytes(path.as_posix().encode('utf-8'))

    def gethomedir(self, username):
        jeżeli 'HOME' w os.environ:
            userhome = os.environ['HOME']
        albo_inaczej 'USERPROFILE' w os.environ:
            userhome = os.environ['USERPROFILE']
        albo_inaczej 'HOMEPATH' w os.environ:
            spróbuj:
                drv = os.environ['HOMEDRIVE']
            wyjąwszy KeyError:
                drv = ''
            userhome = drv + os.environ['HOMEPATH']
        inaczej:
            podnieś RuntimeError("Can't determine home directory")

        jeżeli username:
            # Try to guess user home directory.  By default all users
            # directories are located w the same place oraz are named by
            # corresponding usernames.  If current user home directory points
            # to nonstandard place, this guess jest likely wrong.
            jeżeli os.environ['USERNAME'] != username:
                drv, root, parts = self.parse_parts((userhome,))
                jeżeli parts[-1] != os.environ['USERNAME']:
                    podnieś RuntimeError("Can't determine home directory "
                                       "dla %r" % username)
                parts[-1] = username
                jeżeli drv albo root:
                    userhome = drv + root + self.join(parts[1:])
                inaczej:
                    userhome = self.join(parts)
        zwróć userhome

klasa _PosixFlavour(_Flavour):
    sep = '/'
    altsep = ''
    has_drv = Nieprawda
    pathmod = posixpath

    is_supported = (os.name != 'nt')

    def splitroot(self, part, sep=sep):
        jeżeli part oraz part[0] == sep:
            stripped_part = part.lstrip(sep)
            # According to POSIX path resolution:
            # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap04.html#tag_04_11
            # "A pathname that begins przy two successive slashes may be
            # interpreted w an implementation-defined manner, although more
            # than two leading slashes shall be treated jako a single slash".
            jeżeli len(part) - len(stripped_part) == 2:
                zwróć '', sep * 2, stripped_part
            inaczej:
                zwróć '', sep, stripped_part
        inaczej:
            zwróć '', '', part

    def casefold(self, s):
        zwróć s

    def casefold_parts(self, parts):
        zwróć parts

    def resolve(self, path):
        sep = self.sep
        accessor = path._accessor
        seen = {}
        def _resolve(path, rest):
            jeżeli rest.startswith(sep):
                path = ''

            dla name w rest.split(sep):
                jeżeli nie name albo name == '.':
                    # current dir
                    kontynuuj
                jeżeli name == '..':
                    # parent dir
                    path, _, _ = path.rpartition(sep)
                    kontynuuj
                newpath = path + sep + name
                jeżeli newpath w seen:
                    # Already seen this path
                    path = seen[newpath]
                    jeżeli path jest nie Nic:
                        # use cached value
                        kontynuuj
                    # The symlink jest nie resolved, so we must have a symlink loop.
                    podnieś RuntimeError("Symlink loop z %r" % newpath)
                # Resolve the symbolic link
                spróbuj:
                    target = accessor.readlink(newpath)
                wyjąwszy OSError jako e:
                    jeżeli e.errno != EINVAL:
                        podnieś
                    # Not a symlink
                    path = newpath
                inaczej:
                    seen[newpath] = Nic # nie resolved symlink
                    path = _resolve(path, target)
                    seen[newpath] = path # resolved symlink

            zwróć path
        # NOTE: according to POSIX, getcwd() cannot contain path components
        # which are symlinks.
        base = '' jeżeli path.is_absolute() inaczej os.getcwd()
        zwróć _resolve(base, str(path)) albo sep

    def is_reserved(self, parts):
        zwróć Nieprawda

    def make_uri(self, path):
        # We represent the path using the local filesystem encoding,
        # dla portability to other applications.
        bpath = bytes(path)
        zwróć 'file://' + urlquote_from_bytes(bpath)

    def gethomedir(self, username):
        jeżeli nie username:
            spróbuj:
                zwróć os.environ['HOME']
            wyjąwszy KeyError:
                zaimportuj pwd
                zwróć pwd.getpwuid(os.getuid()).pw_dir
        inaczej:
            zaimportuj pwd
            spróbuj:
                zwróć pwd.getpwnam(username).pw_dir
            wyjąwszy KeyError:
                podnieś RuntimeError("Can't determine home directory "
                                   "dla %r" % username)


_windows_flavour = _WindowsFlavour()
_posix_flavour = _PosixFlavour()


klasa _Accessor:
    """An accessor implements a particular (system-specific albo not) way of
    accessing paths on the filesystem."""


klasa _NormalAccessor(_Accessor):

    def _wrap_strfunc(strfunc):
        @functools.wraps(strfunc)
        def wrapped(pathobj, *args):
            zwróć strfunc(str(pathobj), *args)
        zwróć staticmethod(wrapped)

    def _wrap_binary_strfunc(strfunc):
        @functools.wraps(strfunc)
        def wrapped(pathobjA, pathobjB, *args):
            zwróć strfunc(str(pathobjA), str(pathobjB), *args)
        zwróć staticmethod(wrapped)

    stat = _wrap_strfunc(os.stat)

    lstat = _wrap_strfunc(os.lstat)

    open = _wrap_strfunc(os.open)

    listdir = _wrap_strfunc(os.listdir)

    chmod = _wrap_strfunc(os.chmod)

    jeżeli hasattr(os, "lchmod"):
        lchmod = _wrap_strfunc(os.lchmod)
    inaczej:
        def lchmod(self, pathobj, mode):
            podnieś NotImplementedError("lchmod() nie available on this system")

    mkdir = _wrap_strfunc(os.mkdir)

    unlink = _wrap_strfunc(os.unlink)

    rmdir = _wrap_strfunc(os.rmdir)

    rename = _wrap_binary_strfunc(os.rename)

    replace = _wrap_binary_strfunc(os.replace)

    jeżeli nt:
        jeżeli supports_symlinks:
            symlink = _wrap_binary_strfunc(os.symlink)
        inaczej:
            def symlink(a, b, target_is_directory):
                podnieś NotImplementedError("symlink() nie available on this system")
    inaczej:
        # Under POSIX, os.symlink() takes two args
        @staticmethod
        def symlink(a, b, target_is_directory):
            zwróć os.symlink(str(a), str(b))

    utime = _wrap_strfunc(os.utime)

    # Helper dla resolve()
    def readlink(self, path):
        zwróć os.readlink(path)


_normal_accessor = _NormalAccessor()


#
# Globbing helpers
#

@contextmanager
def _cached(func):
    spróbuj:
        func.__cached__
        uzyskaj func
    wyjąwszy AttributeError:
        cache = {}
        def wrapper(*args):
            spróbuj:
                zwróć cache[args]
            wyjąwszy KeyError:
                value = cache[args] = func(*args)
                zwróć value
        wrapper.__cached__ = Prawda
        spróbuj:
            uzyskaj wrapper
        w_końcu:
            cache.clear()

def _make_selector(pattern_parts):
    pat = pattern_parts[0]
    child_parts = pattern_parts[1:]
    jeżeli pat == '**':
        cls = _RecursiveWildcardSelector
    albo_inaczej '**' w pat:
        podnieś ValueError("Invalid pattern: '**' can only be an entire path component")
    albo_inaczej _is_wildcard_pattern(pat):
        cls = _WildcardSelector
    inaczej:
        cls = _PreciseSelector
    zwróć cls(pat, child_parts)

jeżeli hasattr(functools, "lru_cache"):
    _make_selector = functools.lru_cache()(_make_selector)


klasa _Selector:
    """A selector matches a specific glob pattern part against the children
    of a given path."""

    def __init__(self, child_parts):
        self.child_parts = child_parts
        jeżeli child_parts:
            self.successor = _make_selector(child_parts)
        inaczej:
            self.successor = _TerminatingSelector()

    def select_from(self, parent_path):
        """Iterate over all child paths of `parent_path` matched by this
        selector.  This can contain parent_path itself."""
        path_cls = type(parent_path)
        is_dir = path_cls.is_dir
        exists = path_cls.exists
        listdir = parent_path._accessor.listdir
        zwróć self._select_from(parent_path, is_dir, exists, listdir)


klasa _TerminatingSelector:

    def _select_from(self, parent_path, is_dir, exists, listdir):
        uzyskaj parent_path


klasa _PreciseSelector(_Selector):

    def __init__(self, name, child_parts):
        self.name = name
        _Selector.__init__(self, child_parts)

    def _select_from(self, parent_path, is_dir, exists, listdir):
        jeżeli nie is_dir(parent_path):
            zwróć
        path = parent_path._make_child_relpath(self.name)
        jeżeli exists(path):
            dla p w self.successor._select_from(path, is_dir, exists, listdir):
                uzyskaj p


klasa _WildcardSelector(_Selector):

    def __init__(self, pat, child_parts):
        self.pat = re.compile(fnmatch.translate(pat))
        _Selector.__init__(self, child_parts)

    def _select_from(self, parent_path, is_dir, exists, listdir):
        jeżeli nie is_dir(parent_path):
            zwróć
        cf = parent_path._flavour.casefold
        dla name w listdir(parent_path):
            casefolded = cf(name)
            jeżeli self.pat.match(casefolded):
                path = parent_path._make_child_relpath(name)
                dla p w self.successor._select_from(path, is_dir, exists, listdir):
                    uzyskaj p


klasa _RecursiveWildcardSelector(_Selector):

    def __init__(self, pat, child_parts):
        _Selector.__init__(self, child_parts)

    def _iterate_directories(self, parent_path, is_dir, listdir):
        uzyskaj parent_path
        dla name w listdir(parent_path):
            path = parent_path._make_child_relpath(name)
            jeżeli is_dir(path):
                dla p w self._iterate_directories(path, is_dir, listdir):
                    uzyskaj p

    def _select_from(self, parent_path, is_dir, exists, listdir):
        jeżeli nie is_dir(parent_path):
            zwróć
        przy _cached(listdir) jako listdir:
            uzyskajed = set()
            spróbuj:
                successor_select = self.successor._select_from
                dla starting_point w self._iterate_directories(parent_path, is_dir, listdir):
                    dla p w successor_select(starting_point, is_dir, exists, listdir):
                        jeżeli p nie w uzyskajed:
                            uzyskaj p
                            uzyskajed.add(p)
            w_końcu:
                uzyskajed.clear()


#
# Public API
#

klasa _PathParents(Sequence):
    """This object provides sequence-like access to the logical ancestors
    of a path.  Don't try to construct it yourself."""
    __slots__ = ('_pathcls', '_drv', '_root', '_parts')

    def __init__(self, path):
        # We don't store the instance to avoid reference cycles
        self._pathcls = type(path)
        self._drv = path._drv
        self._root = path._root
        self._parts = path._parts

    def __len__(self):
        jeżeli self._drv albo self._root:
            zwróć len(self._parts) - 1
        inaczej:
            zwróć len(self._parts)

    def __getitem__(self, idx):
        jeżeli idx < 0 albo idx >= len(self):
            podnieś IndexError(idx)
        zwróć self._pathcls._from_parsed_parts(self._drv, self._root,
                                                self._parts[:-idx - 1])

    def __repr__(self):
        zwróć "<{}.parents>".format(self._pathcls.__name__)


klasa PurePath(object):
    """PurePath represents a filesystem path oraz offers operations which
    don't imply any actual filesystem I/O.  Depending on your system,
    instantiating a PurePath will zwróć either a PurePosixPath albo a
    PureWindowsPath object.  You can also instantiate either of these classes
    directly, regardless of your system.
    """
    __slots__ = (
        '_drv', '_root', '_parts',
        '_str', '_hash', '_pparts', '_cached_cparts',
    )

    def __new__(cls, *args):
        """Construct a PurePath z one albo several strings oraz albo existing
        PurePath objects.  The strings oraz path objects are combined so as
        to uzyskaj a canonicalized path, which jest incorporated into the
        new PurePath object.
        """
        jeżeli cls jest PurePath:
            cls = PureWindowsPath jeżeli os.name == 'nt' inaczej PurePosixPath
        zwróć cls._from_parts(args)

    def __reduce__(self):
        # Using the parts tuple helps share interned path parts
        # when pickling related paths.
        zwróć (self.__class__, tuple(self._parts))

    @classmethod
    def _parse_args(cls, args):
        # This jest useful when you don't want to create an instance, just
        # canonicalize some constructor arguments.
        parts = []
        dla a w args:
            jeżeli isinstance(a, PurePath):
                parts += a._parts
            albo_inaczej isinstance(a, str):
                # Force-cast str subclasses to str (issue #21127)
                parts.append(str(a))
            inaczej:
                podnieś TypeError(
                    "argument should be a path albo str object, nie %r"
                    % type(a))
        zwróć cls._flavour.parse_parts(parts)

    @classmethod
    def _from_parts(cls, args, init=Prawda):
        # We need to call _parse_args on the instance, so jako to get the
        # right flavour.
        self = object.__new__(cls)
        drv, root, parts = self._parse_args(args)
        self._drv = drv
        self._root = root
        self._parts = parts
        jeżeli init:
            self._init()
        zwróć self

    @classmethod
    def _from_parsed_parts(cls, drv, root, parts, init=Prawda):
        self = object.__new__(cls)
        self._drv = drv
        self._root = root
        self._parts = parts
        jeżeli init:
            self._init()
        zwróć self

    @classmethod
    def _format_parsed_parts(cls, drv, root, parts):
        jeżeli drv albo root:
            zwróć drv + root + cls._flavour.join(parts[1:])
        inaczej:
            zwróć cls._flavour.join(parts)

    def _init(self):
        # Overriden w concrete Path
        dalej

    def _make_child(self, args):
        drv, root, parts = self._parse_args(args)
        drv, root, parts = self._flavour.join_parsed_parts(
            self._drv, self._root, self._parts, drv, root, parts)
        zwróć self._from_parsed_parts(drv, root, parts)

    def __str__(self):
        """Return the string representation of the path, suitable for
        dalejing to system calls."""
        spróbuj:
            zwróć self._str
        wyjąwszy AttributeError:
            self._str = self._format_parsed_parts(self._drv, self._root,
                                                  self._parts) albo '.'
            zwróć self._str

    def as_posix(self):
        """Return the string representation of the path przy forward (/)
        slashes."""
        f = self._flavour
        zwróć str(self).replace(f.sep, '/')

    def __bytes__(self):
        """Return the bytes representation of the path.  This jest only
        recommended to use under Unix."""
        zwróć os.fsencode(str(self))

    def __repr__(self):
        zwróć "{}({!r})".format(self.__class__.__name__, self.as_posix())

    def as_uri(self):
        """Return the path jako a 'file' URI."""
        jeżeli nie self.is_absolute():
            podnieś ValueError("relative path can't be expressed jako a file URI")
        zwróć self._flavour.make_uri(self)

    @property
    def _cparts(self):
        # Cached casefolded parts, dla hashing oraz comparison
        spróbuj:
            zwróć self._cached_cparts
        wyjąwszy AttributeError:
            self._cached_cparts = self._flavour.casefold_parts(self._parts)
            zwróć self._cached_cparts

    def __eq__(self, other):
        jeżeli nie isinstance(other, PurePath):
            zwróć NotImplemented
        zwróć self._cparts == other._cparts oraz self._flavour jest other._flavour

    def __hash__(self):
        spróbuj:
            zwróć self._hash
        wyjąwszy AttributeError:
            self._hash = hash(tuple(self._cparts))
            zwróć self._hash

    def __lt__(self, other):
        jeżeli nie isinstance(other, PurePath) albo self._flavour jest nie other._flavour:
            zwróć NotImplemented
        zwróć self._cparts < other._cparts

    def __le__(self, other):
        jeżeli nie isinstance(other, PurePath) albo self._flavour jest nie other._flavour:
            zwróć NotImplemented
        zwróć self._cparts <= other._cparts

    def __gt__(self, other):
        jeżeli nie isinstance(other, PurePath) albo self._flavour jest nie other._flavour:
            zwróć NotImplemented
        zwróć self._cparts > other._cparts

    def __ge__(self, other):
        jeżeli nie isinstance(other, PurePath) albo self._flavour jest nie other._flavour:
            zwróć NotImplemented
        zwróć self._cparts >= other._cparts

    drive = property(attrgetter('_drv'),
                     doc="""The drive prefix (letter albo UNC path), jeżeli any.""")

    root = property(attrgetter('_root'),
                    doc="""The root of the path, jeżeli any.""")

    @property
    def anchor(self):
        """The concatenation of the drive oraz root, albo ''."""
        anchor = self._drv + self._root
        zwróć anchor

    @property
    def name(self):
        """The final path component, jeżeli any."""
        parts = self._parts
        jeżeli len(parts) == (1 jeżeli (self._drv albo self._root) inaczej 0):
            zwróć ''
        zwróć parts[-1]

    @property
    def suffix(self):
        """The final component's last suffix, jeżeli any."""
        name = self.name
        i = name.rfind('.')
        jeżeli 0 < i < len(name) - 1:
            zwróć name[i:]
        inaczej:
            zwróć ''

    @property
    def suffixes(self):
        """A list of the final component's suffixes, jeżeli any."""
        name = self.name
        jeżeli name.endswith('.'):
            zwróć []
        name = name.lstrip('.')
        zwróć ['.' + suffix dla suffix w name.split('.')[1:]]

    @property
    def stem(self):
        """The final path component, minus its last suffix."""
        name = self.name
        i = name.rfind('.')
        jeżeli 0 < i < len(name) - 1:
            zwróć name[:i]
        inaczej:
            zwróć name

    def with_name(self, name):
        """Return a new path przy the file name changed."""
        jeżeli nie self.name:
            podnieś ValueError("%r has an empty name" % (self,))
        drv, root, parts = self._flavour.parse_parts((name,))
        jeżeli (nie name albo name[-1] w [self._flavour.sep, self._flavour.altsep]
            albo drv albo root albo len(parts) != 1):
            podnieś ValueError("Invalid name %r" % (name))
        zwróć self._from_parsed_parts(self._drv, self._root,
                                       self._parts[:-1] + [name])

    def with_suffix(self, suffix):
        """Return a new path przy the file suffix changed (or added, jeżeli none)."""
        # XXX jeżeli suffix jest Nic, should the current suffix be removed?
        f = self._flavour
        jeżeli f.sep w suffix albo f.altsep oraz f.altsep w suffix:
            podnieś ValueError("Invalid suffix %r" % (suffix))
        jeżeli suffix oraz nie suffix.startswith('.') albo suffix == '.':
            podnieś ValueError("Invalid suffix %r" % (suffix))
        name = self.name
        jeżeli nie name:
            podnieś ValueError("%r has an empty name" % (self,))
        old_suffix = self.suffix
        jeżeli nie old_suffix:
            name = name + suffix
        inaczej:
            name = name[:-len(old_suffix)] + suffix
        zwróć self._from_parsed_parts(self._drv, self._root,
                                       self._parts[:-1] + [name])

    def relative_to(self, *other):
        """Return the relative path to another path identified by the dalejed
        arguments.  If the operation jest nie possible (because this jest nie
        a subpath of the other path), podnieś ValueError.
        """
        # For the purpose of this method, drive oraz root are considered
        # separate parts, i.e.:
        #   Path('c:/').relative_to('c:')  gives Path('/')
        #   Path('c:/').relative_to('/')   podnieś ValueError
        jeżeli nie other:
            podnieś TypeError("need at least one argument")
        parts = self._parts
        drv = self._drv
        root = self._root
        jeżeli root:
            abs_parts = [drv, root] + parts[1:]
        inaczej:
            abs_parts = parts
        to_drv, to_root, to_parts = self._parse_args(other)
        jeżeli to_root:
            to_abs_parts = [to_drv, to_root] + to_parts[1:]
        inaczej:
            to_abs_parts = to_parts
        n = len(to_abs_parts)
        cf = self._flavour.casefold_parts
        jeżeli (root albo drv) jeżeli n == 0 inaczej cf(abs_parts[:n]) != cf(to_abs_parts):
            formatted = self._format_parsed_parts(to_drv, to_root, to_parts)
            podnieś ValueError("{!r} does nie start przy {!r}"
                             .format(str(self), str(formatted)))
        zwróć self._from_parsed_parts('', root jeżeli n == 1 inaczej '',
                                       abs_parts[n:])

    @property
    def parts(self):
        """An object providing sequence-like access to the
        components w the filesystem path."""
        # We cache the tuple to avoid building a new one each time .parts
        # jest accessed.  XXX jest this necessary?
        spróbuj:
            zwróć self._pparts
        wyjąwszy AttributeError:
            self._pparts = tuple(self._parts)
            zwróć self._pparts

    def joinpath(self, *args):
        """Combine this path przy one albo several arguments, oraz zwróć a
        new path representing either a subpath (jeżeli all arguments are relative
        paths) albo a totally different path (jeżeli one of the arguments jest
        anchored).
        """
        zwróć self._make_child(args)

    def __truediv__(self, key):
        zwróć self._make_child((key,))

    def __rtruediv__(self, key):
        zwróć self._from_parts([key] + self._parts)

    @property
    def parent(self):
        """The logical parent of the path."""
        drv = self._drv
        root = self._root
        parts = self._parts
        jeżeli len(parts) == 1 oraz (drv albo root):
            zwróć self
        zwróć self._from_parsed_parts(drv, root, parts[:-1])

    @property
    def parents(self):
        """A sequence of this path's logical parents."""
        zwróć _PathParents(self)

    def is_absolute(self):
        """Prawda jeżeli the path jest absolute (has both a root and, jeżeli applicable,
        a drive)."""
        jeżeli nie self._root:
            zwróć Nieprawda
        zwróć nie self._flavour.has_drv albo bool(self._drv)

    def is_reserved(self):
        """Return Prawda jeżeli the path contains one of the special names reserved
        by the system, jeżeli any."""
        zwróć self._flavour.is_reserved(self._parts)

    def match(self, path_pattern):
        """
        Return Prawda jeżeli this path matches the given pattern.
        """
        cf = self._flavour.casefold
        path_pattern = cf(path_pattern)
        drv, root, pat_parts = self._flavour.parse_parts((path_pattern,))
        jeżeli nie pat_parts:
            podnieś ValueError("empty pattern")
        jeżeli drv oraz drv != cf(self._drv):
            zwróć Nieprawda
        jeżeli root oraz root != cf(self._root):
            zwróć Nieprawda
        parts = self._cparts
        jeżeli drv albo root:
            jeżeli len(pat_parts) != len(parts):
                zwróć Nieprawda
            pat_parts = pat_parts[1:]
        albo_inaczej len(pat_parts) > len(parts):
            zwróć Nieprawda
        dla part, pat w zip(reversed(parts), reversed(pat_parts)):
            jeżeli nie fnmatch.fnmatchcase(part, pat):
                zwróć Nieprawda
        zwróć Prawda


klasa PurePosixPath(PurePath):
    _flavour = _posix_flavour
    __slots__ = ()


klasa PureWindowsPath(PurePath):
    _flavour = _windows_flavour
    __slots__ = ()


# Filesystem-accessing classes


klasa Path(PurePath):
    __slots__ = (
        '_accessor',
        '_closed',
    )

    def __new__(cls, *args, **kwargs):
        jeżeli cls jest Path:
            cls = WindowsPath jeżeli os.name == 'nt' inaczej PosixPath
        self = cls._from_parts(args, init=Nieprawda)
        jeżeli nie self._flavour.is_supported:
            podnieś NotImplementedError("cannot instantiate %r on your system"
                                      % (cls.__name__,))
        self._init()
        zwróć self

    def _init(self,
              # Private non-constructor arguments
              template=Nic,
              ):
        self._closed = Nieprawda
        jeżeli template jest nie Nic:
            self._accessor = template._accessor
        inaczej:
            self._accessor = _normal_accessor

    def _make_child_relpath(self, part):
        # This jest an optimization used dla dir walking.  `part` must be
        # a single part relative to this path.
        parts = self._parts + [part]
        zwróć self._from_parsed_parts(self._drv, self._root, parts)

    def __enter__(self):
        jeżeli self._closed:
            self._raise_closed()
        zwróć self

    def __exit__(self, t, v, tb):
        self._closed = Prawda

    def _raise_closed(self):
        podnieś ValueError("I/O operation on closed path")

    def _opener(self, name, flags, mode=0o666):
        # A stub dla the opener argument to built-in open()
        zwróć self._accessor.open(self, flags, mode)

    def _raw_open(self, flags, mode=0o777):
        """
        Open the file pointed by this path oraz zwróć a file descriptor,
        jako os.open() does.
        """
        jeżeli self._closed:
            self._raise_closed()
        zwróć self._accessor.open(self, flags, mode)

    # Public API

    @classmethod
    def cwd(cls):
        """Return a new path pointing to the current working directory
        (as returned by os.getcwd()).
        """
        zwróć cls(os.getcwd())

    @classmethod
    def home(cls):
        """Return a new path pointing to the user's home directory (as
        returned by os.path.expanduser('~')).
        """
        zwróć cls(cls()._flavour.gethomedir(Nic))

    def samefile(self, other_path):
        """Return whether `other_file` jest the same albo nie jako this file.
        (as returned by os.path.samefile(file, other_file)).
        """
        st = self.stat()
        spróbuj:
            other_st = other_path.stat()
        wyjąwszy AttributeError:
            other_st = os.stat(other_path)
        zwróć os.path.samestat(st, other_st)

    def iterdir(self):
        """Iterate over the files w this directory.  Does nie uzyskaj any
        result dla the special paths '.' oraz '..'.
        """
        jeżeli self._closed:
            self._raise_closed()
        dla name w self._accessor.listdir(self):
            jeżeli name w {'.', '..'}:
                # Yielding a path object dla these makes little sense
                kontynuuj
            uzyskaj self._make_child_relpath(name)
            jeżeli self._closed:
                self._raise_closed()

    def glob(self, pattern):
        """Iterate over this subtree oraz uzyskaj all existing files (of any
        kind, including directories) matching the given pattern.
        """
        pattern = self._flavour.casefold(pattern)
        drv, root, pattern_parts = self._flavour.parse_parts((pattern,))
        jeżeli drv albo root:
            podnieś NotImplementedError("Non-relative patterns are unsupported")
        selector = _make_selector(tuple(pattern_parts))
        dla p w selector.select_from(self):
            uzyskaj p

    def rglob(self, pattern):
        """Recursively uzyskaj all existing files (of any kind, including
        directories) matching the given pattern, anywhere w this subtree.
        """
        pattern = self._flavour.casefold(pattern)
        drv, root, pattern_parts = self._flavour.parse_parts((pattern,))
        jeżeli drv albo root:
            podnieś NotImplementedError("Non-relative patterns are unsupported")
        selector = _make_selector(("**",) + tuple(pattern_parts))
        dla p w selector.select_from(self):
            uzyskaj p

    def absolute(self):
        """Return an absolute version of this path.  This function works
        even jeżeli the path doesn't point to anything.

        No normalization jest done, i.e. all '.' oraz '..' will be kept along.
        Use resolve() to get the canonical path to a file.
        """
        # XXX untested yet!
        jeżeli self._closed:
            self._raise_closed()
        jeżeli self.is_absolute():
            zwróć self
        # FIXME this must defer to the specific flavour (and, under Windows,
        # use nt._getfullpathname())
        obj = self._from_parts([os.getcwd()] + self._parts, init=Nieprawda)
        obj._init(template=self)
        zwróć obj

    def resolve(self):
        """
        Make the path absolute, resolving all symlinks on the way oraz also
        normalizing it (dla example turning slashes into backslashes under
        Windows).
        """
        jeżeli self._closed:
            self._raise_closed()
        s = self._flavour.resolve(self)
        jeżeli s jest Nic:
            # No symlink resolution => dla consistency, podnieś an error if
            # the path doesn't exist albo jest forbidden
            self.stat()
            s = str(self.absolute())
        # Now we have no symlinks w the path, it's safe to normalize it.
        normed = self._flavour.pathmod.normpath(s)
        obj = self._from_parts((normed,), init=Nieprawda)
        obj._init(template=self)
        zwróć obj

    def stat(self):
        """
        Return the result of the stat() system call on this path, like
        os.stat() does.
        """
        zwróć self._accessor.stat(self)

    def owner(self):
        """
        Return the login name of the file owner.
        """
        zaimportuj pwd
        zwróć pwd.getpwuid(self.stat().st_uid).pw_name

    def group(self):
        """
        Return the group name of the file gid.
        """
        zaimportuj grp
        zwróć grp.getgrgid(self.stat().st_gid).gr_name

    def open(self, mode='r', buffering=-1, encoding=Nic,
             errors=Nic, newline=Nic):
        """
        Open the file pointed by this path oraz zwróć a file object, as
        the built-in open() function does.
        """
        jeżeli self._closed:
            self._raise_closed()
        zwróć io.open(str(self), mode, buffering, encoding, errors, newline,
                       opener=self._opener)

    def read_bytes(self):
        """
        Open the file w bytes mode, read it, oraz close the file.
        """
        przy self.open(mode='rb') jako f:
            zwróć f.read()

    def read_text(self, encoding=Nic, errors=Nic):
        """
        Open the file w text mode, read it, oraz close the file.
        """
        przy self.open(mode='r', encoding=encoding, errors=errors) jako f:
            zwróć f.read()

    def write_bytes(self, data):
        """
        Open the file w bytes mode, write to it, oraz close the file.
        """
        # type-check dla the buffer interface before truncating the file
        view = memoryview(data)
        przy self.open(mode='wb') jako f:
            zwróć f.write(view)

    def write_text(self, data, encoding=Nic, errors=Nic):
        """
        Open the file w text mode, write to it, oraz close the file.
        """
        jeżeli nie isinstance(data, str):
            podnieś TypeError('data must be str, nie %s' %
                            data.__class__.__name__)
        przy self.open(mode='w', encoding=encoding, errors=errors) jako f:
            zwróć f.write(data)

    def touch(self, mode=0o666, exist_ok=Prawda):
        """
        Create this file przy the given access mode, jeżeli it doesn't exist.
        """
        jeżeli self._closed:
            self._raise_closed()
        jeżeli exist_ok:
            # First try to bump modification time
            # Implementation note: GNU touch uses the UTIME_NOW option of
            # the utimensat() / futimens() functions.
            spróbuj:
                self._accessor.utime(self, Nic)
            wyjąwszy OSError:
                # Avoid exception chaining
                dalej
            inaczej:
                zwróć
        flags = os.O_CREAT | os.O_WRONLY
        jeżeli nie exist_ok:
            flags |= os.O_EXCL
        fd = self._raw_open(flags, mode)
        os.close(fd)

    def mkdir(self, mode=0o777, parents=Nieprawda, exist_ok=Nieprawda):
        jeżeli self._closed:
            self._raise_closed()
        jeżeli nie parents:
            spróbuj:
                self._accessor.mkdir(self, mode)
            wyjąwszy FileExistsError:
                jeżeli nie exist_ok albo nie self.is_dir():
                    podnieś
        inaczej:
            spróbuj:
                self._accessor.mkdir(self, mode)
            wyjąwszy FileExistsError:
                jeżeli nie exist_ok albo nie self.is_dir():
                    podnieś
            wyjąwszy OSError jako e:
                jeżeli e.errno != ENOENT:
                    podnieś
                self.parent.mkdir(parents=Prawda)
                self._accessor.mkdir(self, mode)

    def chmod(self, mode):
        """
        Change the permissions of the path, like os.chmod().
        """
        jeżeli self._closed:
            self._raise_closed()
        self._accessor.chmod(self, mode)

    def lchmod(self, mode):
        """
        Like chmod(), wyjąwszy jeżeli the path points to a symlink, the symlink's
        permissions are changed, rather than its target's.
        """
        jeżeli self._closed:
            self._raise_closed()
        self._accessor.lchmod(self, mode)

    def unlink(self):
        """
        Remove this file albo link.
        If the path jest a directory, use rmdir() instead.
        """
        jeżeli self._closed:
            self._raise_closed()
        self._accessor.unlink(self)

    def rmdir(self):
        """
        Remove this directory.  The directory must be empty.
        """
        jeżeli self._closed:
            self._raise_closed()
        self._accessor.rmdir(self)

    def lstat(self):
        """
        Like stat(), wyjąwszy jeżeli the path points to a symlink, the symlink's
        status information jest returned, rather than its target's.
        """
        jeżeli self._closed:
            self._raise_closed()
        zwróć self._accessor.lstat(self)

    def rename(self, target):
        """
        Rename this path to the given path.
        """
        jeżeli self._closed:
            self._raise_closed()
        self._accessor.rename(self, target)

    def replace(self, target):
        """
        Rename this path to the given path, clobbering the existing
        destination jeżeli it exists.
        """
        jeżeli self._closed:
            self._raise_closed()
        self._accessor.replace(self, target)

    def symlink_to(self, target, target_is_directory=Nieprawda):
        """
        Make this path a symlink pointing to the given path.
        Note the order of arguments (self, target) jest the reverse of os.symlink's.
        """
        jeżeli self._closed:
            self._raise_closed()
        self._accessor.symlink(target, self, target_is_directory)

    # Convenience functions dla querying the stat results

    def exists(self):
        """
        Whether this path exists.
        """
        spróbuj:
            self.stat()
        wyjąwszy OSError jako e:
            jeżeli e.errno nie w (ENOENT, ENOTDIR):
                podnieś
            zwróć Nieprawda
        zwróć Prawda

    def is_dir(self):
        """
        Whether this path jest a directory.
        """
        spróbuj:
            zwróć S_ISDIR(self.stat().st_mode)
        wyjąwszy OSError jako e:
            jeżeli e.errno nie w (ENOENT, ENOTDIR):
                podnieś
            # Path doesn't exist albo jest a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            zwróć Nieprawda

    def is_file(self):
        """
        Whether this path jest a regular file (also Prawda dla symlinks pointing
        to regular files).
        """
        spróbuj:
            zwróć S_ISREG(self.stat().st_mode)
        wyjąwszy OSError jako e:
            jeżeli e.errno nie w (ENOENT, ENOTDIR):
                podnieś
            # Path doesn't exist albo jest a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            zwróć Nieprawda

    def is_symlink(self):
        """
        Whether this path jest a symbolic link.
        """
        spróbuj:
            zwróć S_ISLNK(self.lstat().st_mode)
        wyjąwszy OSError jako e:
            jeżeli e.errno nie w (ENOENT, ENOTDIR):
                podnieś
            # Path doesn't exist
            zwróć Nieprawda

    def is_block_device(self):
        """
        Whether this path jest a block device.
        """
        spróbuj:
            zwróć S_ISBLK(self.stat().st_mode)
        wyjąwszy OSError jako e:
            jeżeli e.errno nie w (ENOENT, ENOTDIR):
                podnieś
            # Path doesn't exist albo jest a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            zwróć Nieprawda

    def is_char_device(self):
        """
        Whether this path jest a character device.
        """
        spróbuj:
            zwróć S_ISCHR(self.stat().st_mode)
        wyjąwszy OSError jako e:
            jeżeli e.errno nie w (ENOENT, ENOTDIR):
                podnieś
            # Path doesn't exist albo jest a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            zwróć Nieprawda

    def is_fifo(self):
        """
        Whether this path jest a FIFO.
        """
        spróbuj:
            zwróć S_ISFIFO(self.stat().st_mode)
        wyjąwszy OSError jako e:
            jeżeli e.errno nie w (ENOENT, ENOTDIR):
                podnieś
            # Path doesn't exist albo jest a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            zwróć Nieprawda

    def is_socket(self):
        """
        Whether this path jest a socket.
        """
        spróbuj:
            zwróć S_ISSOCK(self.stat().st_mode)
        wyjąwszy OSError jako e:
            jeżeli e.errno nie w (ENOENT, ENOTDIR):
                podnieś
            # Path doesn't exist albo jest a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            zwróć Nieprawda

    def expanduser(self):
        """ Return a new path przy expanded ~ oraz ~user constructs
        (as returned by os.path.expanduser)
        """
        jeżeli (nie (self._drv albo self._root) oraz
            self._parts oraz self._parts[0][:1] == '~'):
            homedir = self._flavour.gethomedir(self._parts[0][1:])
            zwróć self._from_parts([homedir] + self._parts[1:])

        zwróć self


klasa PosixPath(Path, PurePosixPath):
    __slots__ = ()

klasa WindowsPath(Path, PureWindowsPath):
    __slots__ = ()
