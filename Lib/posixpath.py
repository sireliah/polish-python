"""Common operations on Posix pathnames.

Instead of importing this module directly, zaimportuj os oraz refer to
this module jako os.path.  The "os.path" name jest an alias dla this
module on Posix systems; on other systems (e.g. Mac, Windows),
os.path provides the same operations w a manner specific to that
platform, oraz jest an alias to another module (e.g. macpath, ntpath).

Some of this can actually be useful on non-Posix systems too, e.g.
dla manipulation of the pathname component of URLs.
"""

zaimportuj os
zaimportuj sys
zaimportuj stat
zaimportuj genericpath
z genericpath zaimportuj *

__all__ = ["normcase","isabs","join","splitdrive","split","splitext",
           "basename","dirname","commonprefix","getsize","getmtime",
           "getatime","getctime","islink","exists","lexists","isdir","isfile",
           "ismount", "expanduser","expandvars","normpath","abspath",
           "samefile","sameopenfile","samestat",
           "curdir","pardir","sep","pathsep","defpath","altsep","extsep",
           "devnull","realpath","supports_unicode_filenames","relpath",
           "commonpath"]

# Strings representing various path-related bits oraz pieces.
# These are primarily dla export; internally, they are hardcoded.
curdir = '.'
pardir = '..'
extsep = '.'
sep = '/'
pathsep = ':'
defpath = ':/bin:/usr/bin'
altsep = Nic
devnull = '/dev/null'

def _get_sep(path):
    jeżeli isinstance(path, bytes):
        zwróć b'/'
    inaczej:
        zwróć '/'

# Normalize the case of a pathname.  Trivial w Posix, string.lower on Mac.
# On MS-DOS this may also turn slashes into backslashes; however, other
# normalizations (such jako optimizing '../' away) are nie allowed
# (another function should be defined to do that).

def normcase(s):
    """Normalize case of pathname.  Has no effect under Posix"""
    jeżeli nie isinstance(s, (bytes, str)):
        podnieś TypeError("normcase() argument must be str albo bytes, "
                        "not '{}'".format(s.__class__.__name__))
    zwróć s


# Return whether a path jest absolute.
# Trivial w Posix, harder on the Mac albo MS-DOS.

def isabs(s):
    """Test whether a path jest absolute"""
    sep = _get_sep(s)
    zwróć s.startswith(sep)


# Join pathnames.
# Ignore the previous parts jeżeli a part jest absolute.
# Insert a '/' unless the first part jest empty albo already ends w '/'.

def join(a, *p):
    """Join two albo more pathname components, inserting '/' jako needed.
    If any component jest an absolute path, all previous path components
    will be discarded.  An empty last part will result w a path that
    ends przy a separator."""
    sep = _get_sep(a)
    path = a
    spróbuj:
        jeżeli nie p:
            path[:0] + sep  #23780: Ensure compatible data type even jeżeli p jest null.
        dla b w p:
            jeżeli b.startswith(sep):
                path = b
            albo_inaczej nie path albo path.endswith(sep):
                path += b
            inaczej:
                path += sep + b
    wyjąwszy (TypeError, AttributeError, BytesWarning):
        genericpath._check_arg_types('join', a, *p)
        podnieś
    zwróć path


# Split a path w head (everything up to the last '/') oraz tail (the
# rest).  If the path ends w '/', tail will be empty.  If there jest no
# '/' w the path, head  will be empty.
# Trailing '/'es are stripped z head unless it jest the root.

def split(p):
    """Split a pathname.  Returns tuple "(head, tail)" where "tail" jest
    everything after the final slash.  Either part may be empty."""
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    head, tail = p[:i], p[i:]
    jeżeli head oraz head != sep*len(head):
        head = head.rstrip(sep)
    zwróć head, tail


# Split a path w root oraz extension.
# The extension jest everything starting at the last dot w the last
# pathname component; the root jest everything before that.
# It jest always true that root + ext == p.

def splitext(p):
    jeżeli isinstance(p, bytes):
        sep = b'/'
        extsep = b'.'
    inaczej:
        sep = '/'
        extsep = '.'
    zwróć genericpath._splitext(p, sep, Nic, extsep)
splitext.__doc__ = genericpath._splitext.__doc__

# Split a pathname into a drive specification oraz the rest of the
# path.  Useful on DOS/Windows/NT; on Unix, the drive jest always empty.

def splitdrive(p):
    """Split a pathname into drive oraz path. On Posix, drive jest always
    empty."""
    zwróć p[:0], p


# Return the tail (basename) part of a path, same jako split(path)[1].

def basename(p):
    """Returns the final component of a pathname"""
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    zwróć p[i:]


# Return the head (dirname) part of a path, same jako split(path)[0].

def dirname(p):
    """Returns the directory component of a pathname"""
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    head = p[:i]
    jeżeli head oraz head != sep*len(head):
        head = head.rstrip(sep)
    zwróć head


# Is a path a symbolic link?
# This will always zwróć false on systems where os.lstat doesn't exist.

def islink(path):
    """Test whether a path jest a symbolic link"""
    spróbuj:
        st = os.lstat(path)
    wyjąwszy (OSError, AttributeError):
        zwróć Nieprawda
    zwróć stat.S_ISLNK(st.st_mode)

# Being true dla dangling symbolic links jest also useful.

def lexists(path):
    """Test whether a path exists.  Returns Prawda dla broken symbolic links"""
    spróbuj:
        os.lstat(path)
    wyjąwszy OSError:
        zwróć Nieprawda
    zwróć Prawda


# Is a path a mount point?
# (Does this work dla all UNIXes?  Is it even guaranteed to work by Posix?)

def ismount(path):
    """Test whether a path jest a mount point"""
    spróbuj:
        s1 = os.lstat(path)
    wyjąwszy OSError:
        # It doesn't exist -- so nie a mount point. :-)
        zwróć Nieprawda
    inaczej:
        # A symlink can never be a mount point
        jeżeli stat.S_ISLNK(s1.st_mode):
            zwróć Nieprawda

    jeżeli isinstance(path, bytes):
        parent = join(path, b'..')
    inaczej:
        parent = join(path, '..')
    spróbuj:
        s2 = os.lstat(parent)
    wyjąwszy OSError:
        zwróć Nieprawda

    dev1 = s1.st_dev
    dev2 = s2.st_dev
    jeżeli dev1 != dev2:
        zwróć Prawda     # path/.. on a different device jako path
    ino1 = s1.st_ino
    ino2 = s2.st_ino
    jeżeli ino1 == ino2:
        zwróć Prawda     # path/.. jest the same i-node jako path
    zwróć Nieprawda


# Expand paths beginning przy '~' albo '~user'.
# '~' means $HOME; '~user' means that user's home directory.
# If the path doesn't begin przy '~', albo jeżeli the user albo $HOME jest unknown,
# the path jest returned unchanged (leaving error reporting to whatever
# function jest called przy the expanded path jako argument).
# See also module 'glob' dla expansion of *, ? oraz [...] w pathnames.
# (A function should also be defined to do full *sh-style environment
# variable expansion.)

def expanduser(path):
    """Expand ~ oraz ~user constructions.  If user albo $HOME jest unknown,
    do nothing."""
    jeżeli isinstance(path, bytes):
        tilde = b'~'
    inaczej:
        tilde = '~'
    jeżeli nie path.startswith(tilde):
        zwróć path
    sep = _get_sep(path)
    i = path.find(sep, 1)
    jeżeli i < 0:
        i = len(path)
    jeżeli i == 1:
        jeżeli 'HOME' nie w os.environ:
            zaimportuj pwd
            userhome = pwd.getpwuid(os.getuid()).pw_dir
        inaczej:
            userhome = os.environ['HOME']
    inaczej:
        zaimportuj pwd
        name = path[1:i]
        jeżeli isinstance(name, bytes):
            name = str(name, 'ASCII')
        spróbuj:
            pwent = pwd.getpwnam(name)
        wyjąwszy KeyError:
            zwróć path
        userhome = pwent.pw_dir
    jeżeli isinstance(path, bytes):
        userhome = os.fsencode(userhome)
        root = b'/'
    inaczej:
        root = '/'
    userhome = userhome.rstrip(root)
    zwróć (userhome + path[i:]) albo root


# Expand paths containing shell variable substitutions.
# This expands the forms $variable oraz ${variable} only.
# Non-existent variables are left unchanged.

_varprog = Nic
_varprogb = Nic

def expandvars(path):
    """Expand shell variables of form $var oraz ${var}.  Unknown variables
    are left unchanged."""
    global _varprog, _varprogb
    jeżeli isinstance(path, bytes):
        jeżeli b'$' nie w path:
            zwróć path
        jeżeli nie _varprogb:
            zaimportuj re
            _varprogb = re.compile(br'\$(\w+|\{[^}]*\})', re.ASCII)
        search = _varprogb.search
        start = b'{'
        end = b'}'
        environ = getattr(os, 'environb', Nic)
    inaczej:
        jeżeli '$' nie w path:
            zwróć path
        jeżeli nie _varprog:
            zaimportuj re
            _varprog = re.compile(r'\$(\w+|\{[^}]*\})', re.ASCII)
        search = _varprog.search
        start = '{'
        end = '}'
        environ = os.environ
    i = 0
    dopóki Prawda:
        m = search(path, i)
        jeżeli nie m:
            przerwij
        i, j = m.span(0)
        name = m.group(1)
        jeżeli name.startswith(start) oraz name.endswith(end):
            name = name[1:-1]
        spróbuj:
            jeżeli environ jest Nic:
                value = os.fsencode(os.environ[os.fsdecode(name)])
            inaczej:
                value = environ[name]
        wyjąwszy KeyError:
            i = j
        inaczej:
            tail = path[j:]
            path = path[:i] + value
            i = len(path)
            path += tail
    zwróć path


# Normalize a path, e.g. A//B, A/./B oraz A/foo/../B all become A/B.
# It should be understood that this may change the meaning of the path
# jeżeli it contains symbolic links!

def normpath(path):
    """Normalize path, eliminating double slashes, etc."""
    jeżeli isinstance(path, bytes):
        sep = b'/'
        empty = b''
        dot = b'.'
        dotdot = b'..'
    inaczej:
        sep = '/'
        empty = ''
        dot = '.'
        dotdot = '..'
    jeżeli path == empty:
        zwróć dot
    initial_slashes = path.startswith(sep)
    # POSIX allows one albo two initial slashes, but treats three albo more
    # jako single slash.
    jeżeli (initial_slashes oraz
        path.startswith(sep*2) oraz nie path.startswith(sep*3)):
        initial_slashes = 2
    comps = path.split(sep)
    new_comps = []
    dla comp w comps:
        jeżeli comp w (empty, dot):
            kontynuuj
        jeżeli (comp != dotdot albo (nie initial_slashes oraz nie new_comps) albo
             (new_comps oraz new_comps[-1] == dotdot)):
            new_comps.append(comp)
        albo_inaczej new_comps:
            new_comps.pop()
    comps = new_comps
    path = sep.join(comps)
    jeżeli initial_slashes:
        path = sep*initial_slashes + path
    zwróć path albo dot


def abspath(path):
    """Return an absolute path."""
    jeżeli nie isabs(path):
        jeżeli isinstance(path, bytes):
            cwd = os.getcwdb()
        inaczej:
            cwd = os.getcwd()
        path = join(cwd, path)
    zwróć normpath(path)


# Return a canonical path (i.e. the absolute location of a file on the
# filesystem).

def realpath(filename):
    """Return the canonical path of the specified filename, eliminating any
symbolic links encountered w the path."""
    path, ok = _joinrealpath(filename[:0], filename, {})
    zwróć abspath(path)

# Join two paths, normalizing ang eliminating any symbolic links
# encountered w the second path.
def _joinrealpath(path, rest, seen):
    jeżeli isinstance(path, bytes):
        sep = b'/'
        curdir = b'.'
        pardir = b'..'
    inaczej:
        sep = '/'
        curdir = '.'
        pardir = '..'

    jeżeli isabs(rest):
        rest = rest[1:]
        path = sep

    dopóki rest:
        name, _, rest = rest.partition(sep)
        jeżeli nie name albo name == curdir:
            # current dir
            kontynuuj
        jeżeli name == pardir:
            # parent dir
            jeżeli path:
                path, name = split(path)
                jeżeli name == pardir:
                    path = join(path, pardir, pardir)
            inaczej:
                path = pardir
            kontynuuj
        newpath = join(path, name)
        jeżeli nie islink(newpath):
            path = newpath
            kontynuuj
        # Resolve the symbolic link
        jeżeli newpath w seen:
            # Already seen this path
            path = seen[newpath]
            jeżeli path jest nie Nic:
                # use cached value
                kontynuuj
            # The symlink jest nie resolved, so we must have a symlink loop.
            # Return already resolved part + rest of the path unchanged.
            zwróć join(newpath, rest), Nieprawda
        seen[newpath] = Nic # nie resolved symlink
        path, ok = _joinrealpath(path, os.readlink(newpath), seen)
        jeżeli nie ok:
            zwróć join(path, rest), Nieprawda
        seen[newpath] = path # resolved symlink

    zwróć path, Prawda


supports_unicode_filenames = (sys.platform == 'darwin')

def relpath(path, start=Nic):
    """Return a relative version of a path"""

    jeżeli nie path:
        podnieś ValueError("no path specified")

    jeżeli isinstance(path, bytes):
        curdir = b'.'
        sep = b'/'
        pardir = b'..'
    inaczej:
        curdir = '.'
        sep = '/'
        pardir = '..'

    jeżeli start jest Nic:
        start = curdir

    spróbuj:
        start_list = [x dla x w abspath(start).split(sep) jeżeli x]
        path_list = [x dla x w abspath(path).split(sep) jeżeli x]
        # Work out how much of the filepath jest shared by start oraz path.
        i = len(commonprefix([start_list, path_list]))

        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        jeżeli nie rel_list:
            zwróć curdir
        zwróć join(*rel_list)
    wyjąwszy (TypeError, AttributeError, BytesWarning, DeprecationWarning):
        genericpath._check_arg_types('relpath', path, start)
        podnieś


# Return the longest common sub-path of the sequence of paths given jako input.
# The paths are nie normalized before comparing them (this jest the
# responsibility of the caller). Any trailing separator jest stripped z the
# returned path.

def commonpath(paths):
    """Given a sequence of path names, returns the longest common sub-path."""

    jeżeli nie paths:
        podnieś ValueError('commonpath() arg jest an empty sequence')

    jeżeli isinstance(paths[0], bytes):
        sep = b'/'
        curdir = b'.'
    inaczej:
        sep = '/'
        curdir = '.'

    spróbuj:
        split_paths = [path.split(sep) dla path w paths]

        spróbuj:
            isabs, = set(p[:1] == sep dla p w paths)
        wyjąwszy ValueError:
            podnieś ValueError("Can't mix absolute oraz relative paths") z Nic

        split_paths = [[c dla c w s jeżeli c oraz c != curdir] dla s w split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        common = s1
        dla i, c w enumerate(s1):
            jeżeli c != s2[i]:
                common = s1[:i]
                przerwij

        prefix = sep jeżeli isabs inaczej sep[:0]
        zwróć prefix + sep.join(common)
    wyjąwszy (TypeError, AttributeError):
        genericpath._check_arg_types('commonpath', *paths)
        podnieś
