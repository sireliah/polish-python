# Module 'ntpath' -- common operations on WinNT/Win95 pathnames
"""Common pathname manipulations, WindowsNT/95 version.

Instead of importing this module directly, zaimportuj os oraz refer to this
module jako os.path.
"""

zaimportuj os
zaimportuj sys
zaimportuj stat
zaimportuj genericpath
z genericpath zaimportuj *

__all__ = ["normcase","isabs","join","splitdrive","split","splitext",
           "basename","dirname","commonprefix","getsize","getmtime",
           "getatime","getctime", "islink","exists","lexists","isdir","isfile",
           "ismount", "expanduser","expandvars","normpath","abspath",
           "splitunc","curdir","pardir","sep","pathsep","defpath","altsep",
           "extsep","devnull","realpath","supports_unicode_filenames","relpath",
           "samefile", "sameopenfile", "samestat", "commonpath"]

# strings representing various path-related bits oraz pieces
# These are primarily dla export; internally, they are hardcoded.
curdir = '.'
pardir = '..'
extsep = '.'
sep = '\\'
pathsep = ';'
altsep = '/'
defpath = '.;C:\\bin'
jeżeli 'ce' w sys.builtin_module_names:
    defpath = '\\Windows'
devnull = 'nul'

def _get_bothseps(path):
    jeżeli isinstance(path, bytes):
        zwróć b'\\/'
    inaczej:
        zwróć '\\/'

# Normalize the case of a pathname oraz map slashes to backslashes.
# Other normalizations (such jako optimizing '../' away) are nie done
# (this jest done by normpath).

def normcase(s):
    """Normalize case of pathname.

    Makes all characters lowercase oraz all slashes into backslashes."""
    spróbuj:
        jeżeli isinstance(s, bytes):
            zwróć s.replace(b'/', b'\\').lower()
        inaczej:
            zwróć s.replace('/', '\\').lower()
    wyjąwszy (TypeError, AttributeError):
        jeżeli nie isinstance(s, (bytes, str)):
            podnieś TypeError("normcase() argument must be str albo bytes, "
                            "not %r" % s.__class__.__name__) z Nic
        podnieś


# Return whether a path jest absolute.
# Trivial w Posix, harder on Windows.
# For Windows it jest absolute jeżeli it starts przy a slash albo backslash (current
# volume), albo jeżeli a pathname after the volume-letter-and-colon albo UNC-resource
# starts przy a slash albo backslash.

def isabs(s):
    """Test whether a path jest absolute"""
    s = splitdrive(s)[1]
    zwróć len(s) > 0 oraz s[0] w _get_bothseps(s)


# Join two (or more) paths.
def join(path, *paths):
    jeżeli isinstance(path, bytes):
        sep = b'\\'
        seps = b'\\/'
        colon = b':'
    inaczej:
        sep = '\\'
        seps = '\\/'
        colon = ':'
    spróbuj:
        jeżeli nie paths:
            path[:0] + sep  #23780: Ensure compatible data type even jeżeli p jest null.
        result_drive, result_path = splitdrive(path)
        dla p w paths:
            p_drive, p_path = splitdrive(p)
            jeżeli p_path oraz p_path[0] w seps:
                # Second path jest absolute
                jeżeli p_drive albo nie result_drive:
                    result_drive = p_drive
                result_path = p_path
                kontynuuj
            albo_inaczej p_drive oraz p_drive != result_drive:
                jeżeli p_drive.lower() != result_drive.lower():
                    # Different drives => ignore the first path entirely
                    result_drive = p_drive
                    result_path = p_path
                    kontynuuj
                # Same drive w different case
                result_drive = p_drive
            # Second path jest relative to the first
            jeżeli result_path oraz result_path[-1] nie w seps:
                result_path = result_path + sep
            result_path = result_path + p_path
        ## add separator between UNC oraz non-absolute path
        jeżeli (result_path oraz result_path[0] nie w seps oraz
            result_drive oraz result_drive[-1:] != colon):
            zwróć result_drive + sep + result_path
        zwróć result_drive + result_path
    wyjąwszy (TypeError, AttributeError, BytesWarning):
        genericpath._check_arg_types('join', path, *paths)
        podnieś


# Split a path w a drive specification (a drive letter followed by a
# colon) oraz the path specification.
# It jest always true that drivespec + pathspec == p
def splitdrive(p):
    """Split a pathname into drive/UNC sharepoint oraz relative path specifiers.
    Returns a 2-tuple (drive_or_unc, path); either part may be empty.

    If you assign
        result = splitdrive(p)
    It jest always true that:
        result[0] + result[1] == p

    If the path contained a drive letter, drive_or_unc will contain everything
    up to oraz including the colon.  e.g. splitdrive("c:/dir") returns ("c:", "/dir")

    If the path contained a UNC path, the drive_or_unc will contain the host name
    oraz share up to but nie including the fourth directory separator character.
    e.g. splitdrive("//host/computer/dir") returns ("//host/computer", "/dir")

    Paths cannot contain both a drive letter oraz a UNC path.

    """
    jeżeli len(p) >= 2:
        jeżeli isinstance(p, bytes):
            sep = b'\\'
            altsep = b'/'
            colon = b':'
        inaczej:
            sep = '\\'
            altsep = '/'
            colon = ':'
        normp = p.replace(altsep, sep)
        jeżeli (normp[0:2] == sep*2) oraz (normp[2:3] != sep):
            # jest a UNC path:
            # vvvvvvvvvvvvvvvvvvvv drive letter albo UNC path
            # \\machine\mountpoint\directory\etc\...
            #           directory ^^^^^^^^^^^^^^^
            index = normp.find(sep, 2)
            jeżeli index == -1:
                zwróć p[:0], p
            index2 = normp.find(sep, index + 1)
            # a UNC path can't have two slashes w a row
            # (after the initial two)
            jeżeli index2 == index + 1:
                zwróć p[:0], p
            jeżeli index2 == -1:
                index2 = len(p)
            zwróć p[:index2], p[index2:]
        jeżeli normp[1:2] == colon:
            zwróć p[:2], p[2:]
    zwróć p[:0], p


# Parse UNC paths
def splitunc(p):
    """Deprecated since Python 3.1.  Please use splitdrive() instead;
    it now handles UNC paths.

    Split a pathname into UNC mount point oraz relative path specifiers.

    Return a 2-tuple (unc, rest); either part may be empty.
    If unc jest nie empty, it has the form '//host/mount' (or similar
    using backslashes).  unc+rest jest always the input path.
    Paths containing drive letters never have an UNC part.
    """
    zaimportuj warnings
    warnings.warn("ntpath.splitunc jest deprecated, use ntpath.splitdrive instead",
                  DeprecationWarning, 2)
    drive, path = splitdrive(p)
    jeżeli len(drive) == 2:
         # Drive letter present
        zwróć p[:0], p
    zwróć drive, path


# Split a path w head (everything up to the last '/') oraz tail (the
# rest).  After the trailing '/' jest stripped, the invariant
# join(head, tail) == p holds.
# The resulting head won't end w '/' unless it jest the root.

def split(p):
    """Split a pathname.

    Return tuple (head, tail) where tail jest everything after the final slash.
    Either part may be empty."""

    seps = _get_bothseps(p)
    d, p = splitdrive(p)
    # set i to index beyond p's last slash
    i = len(p)
    dopóki i oraz p[i-1] nie w seps:
        i -= 1
    head, tail = p[:i], p[i:]  # now tail has no slashes
    # remove trailing slashes z head, unless it's all slashes
    head = head.rstrip(seps) albo head
    zwróć d + head, tail


# Split a path w root oraz extension.
# The extension jest everything starting at the last dot w the last
# pathname component; the root jest everything before that.
# It jest always true that root + ext == p.

def splitext(p):
    jeżeli isinstance(p, bytes):
        zwróć genericpath._splitext(p, b'\\', b'/', b'.')
    inaczej:
        zwróć genericpath._splitext(p, '\\', '/', '.')
splitext.__doc__ = genericpath._splitext.__doc__


# Return the tail (basename) part of a path.

def basename(p):
    """Returns the final component of a pathname"""
    zwróć split(p)[1]


# Return the head (dirname) part of a path.

def dirname(p):
    """Returns the directory component of a pathname"""
    zwróć split(p)[0]

# Is a path a symbolic link?
# This will always zwróć false on systems where os.lstat doesn't exist.

def islink(path):
    """Test whether a path jest a symbolic link.
    This will always zwróć false dla Windows prior to 6.0.
    """
    spróbuj:
        st = os.lstat(path)
    wyjąwszy (OSError, AttributeError):
        zwróć Nieprawda
    zwróć stat.S_ISLNK(st.st_mode)

# Being true dla dangling symbolic links jest also useful.

def lexists(path):
    """Test whether a path exists.  Returns Prawda dla broken symbolic links"""
    spróbuj:
        st = os.lstat(path)
    wyjąwszy OSError:
        zwróć Nieprawda
    zwróć Prawda

# Is a path a mount point?
# Any drive letter root (eg c:\)
# Any share UNC (eg \\server\share)
# Any volume mounted on a filesystem folder
#
# No one method detects all three situations. Historically we've lexically
# detected drive letter roots oraz share UNCs. The canonical approach to
# detecting mounted volumes (querying the reparse tag) fails dla the most
# common case: drive letter roots. The alternative which uses GetVolumePathName
# fails jeżeli the drive letter jest the result of a SUBST.
spróbuj:
    z nt zaimportuj _getvolumepathname
wyjąwszy ImportError:
    _getvolumepathname = Nic
def ismount(path):
    """Test whether a path jest a mount point (a drive root, the root of a
    share, albo a mounted volume)"""
    seps = _get_bothseps(path)
    path = abspath(path)
    root, rest = splitdrive(path)
    jeżeli root oraz root[0] w seps:
        zwróć (nie rest) albo (rest w seps)
    jeżeli rest w seps:
        zwróć Prawda

    jeżeli _getvolumepathname:
        zwróć path.rstrip(seps) == _getvolumepathname(path).rstrip(seps)
    inaczej:
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
    """Expand ~ oraz ~user constructs.

    If user albo $HOME jest unknown, do nothing."""
    jeżeli isinstance(path, bytes):
        tilde = b'~'
    inaczej:
        tilde = '~'
    jeżeli nie path.startswith(tilde):
        zwróć path
    i, n = 1, len(path)
    dopóki i < n oraz path[i] nie w _get_bothseps(path):
        i += 1

    jeżeli 'HOME' w os.environ:
        userhome = os.environ['HOME']
    albo_inaczej 'USERPROFILE' w os.environ:
        userhome = os.environ['USERPROFILE']
    albo_inaczej nie 'HOMEPATH' w os.environ:
        zwróć path
    inaczej:
        spróbuj:
            drive = os.environ['HOMEDRIVE']
        wyjąwszy KeyError:
            drive = ''
        userhome = join(drive, os.environ['HOMEPATH'])

    jeżeli isinstance(path, bytes):
        userhome = os.fsencode(userhome)

    jeżeli i != 1: #~user
        userhome = join(dirname(userhome), path[1:i])

    zwróć userhome + path[i:]


# Expand paths containing shell variable substitutions.
# The following rules apply:
#       - no expansion within single quotes
#       - '$$' jest translated into '$'
#       - '%%' jest translated into '%' jeżeli '%%' are nie seen w %var1%%var2%
#       - ${varname} jest accepted.
#       - $varname jest accepted.
#       - %varname% jest accepted.
#       - varnames can be made out of letters, digits oraz the characters '_-'
#         (though jest nie verified w the ${varname} oraz %varname% cases)
# XXX With COMMAND.COM you can use any characters w a variable name,
# XXX wyjąwszy '^|<>='.

def expandvars(path):
    """Expand shell variables of the forms $var, ${var} oraz %var%.

    Unknown variables are left unchanged."""
    jeżeli isinstance(path, bytes):
        jeżeli b'$' nie w path oraz b'%' nie w path:
            zwróć path
        zaimportuj string
        varchars = bytes(string.ascii_letters + string.digits + '_-', 'ascii')
        quote = b'\''
        percent = b'%'
        brace = b'{'
        rbrace = b'}'
        dollar = b'$'
        environ = getattr(os, 'environb', Nic)
    inaczej:
        jeżeli '$' nie w path oraz '%' nie w path:
            zwróć path
        zaimportuj string
        varchars = string.ascii_letters + string.digits + '_-'
        quote = '\''
        percent = '%'
        brace = '{'
        rbrace = '}'
        dollar = '$'
        environ = os.environ
    res = path[:0]
    index = 0
    pathlen = len(path)
    dopóki index < pathlen:
        c = path[index:index+1]
        jeżeli c == quote:   # no expansion within single quotes
            path = path[index + 1:]
            pathlen = len(path)
            spróbuj:
                index = path.index(c)
                res += c + path[:index + 1]
            wyjąwszy ValueError:
                res += c + path
                index = pathlen - 1
        albo_inaczej c == percent:  # variable albo '%'
            jeżeli path[index + 1:index + 2] == percent:
                res += c
                index += 1
            inaczej:
                path = path[index+1:]
                pathlen = len(path)
                spróbuj:
                    index = path.index(percent)
                wyjąwszy ValueError:
                    res += percent + path
                    index = pathlen - 1
                inaczej:
                    var = path[:index]
                    spróbuj:
                        jeżeli environ jest Nic:
                            value = os.fsencode(os.environ[os.fsdecode(var)])
                        inaczej:
                            value = environ[var]
                    wyjąwszy KeyError:
                        value = percent + var + percent
                    res += value
        albo_inaczej c == dollar:  # variable albo '$$'
            jeżeli path[index + 1:index + 2] == dollar:
                res += c
                index += 1
            albo_inaczej path[index + 1:index + 2] == brace:
                path = path[index+2:]
                pathlen = len(path)
                spróbuj:
                    index = path.index(rbrace)
                wyjąwszy ValueError:
                    res += dollar + brace + path
                    index = pathlen - 1
                inaczej:
                    var = path[:index]
                    spróbuj:
                        jeżeli environ jest Nic:
                            value = os.fsencode(os.environ[os.fsdecode(var)])
                        inaczej:
                            value = environ[var]
                    wyjąwszy KeyError:
                        value = dollar + brace + var + rbrace
                    res += value
            inaczej:
                var = path[:0]
                index += 1
                c = path[index:index + 1]
                dopóki c oraz c w varchars:
                    var += c
                    index += 1
                    c = path[index:index + 1]
                spróbuj:
                    jeżeli environ jest Nic:
                        value = os.fsencode(os.environ[os.fsdecode(var)])
                    inaczej:
                        value = environ[var]
                wyjąwszy KeyError:
                    value = dollar + var
                res += value
                jeżeli c:
                    index -= 1
        inaczej:
            res += c
        index += 1
    zwróć res


# Normalize a path, e.g. A//B, A/./B oraz A/foo/../B all become A\B.
# Previously, this function also truncated pathnames to 8+3 format,
# but jako this module jest called "ntpath", that's obviously wrong!

def normpath(path):
    """Normalize path, eliminating double slashes, etc."""
    jeżeli isinstance(path, bytes):
        sep = b'\\'
        altsep = b'/'
        curdir = b'.'
        pardir = b'..'
        special_prefixes = (b'\\\\.\\', b'\\\\?\\')
    inaczej:
        sep = '\\'
        altsep = '/'
        curdir = '.'
        pardir = '..'
        special_prefixes = ('\\\\.\\', '\\\\?\\')
    jeżeli path.startswith(special_prefixes):
        # w the case of paths przy these prefixes:
        # \\.\ -> device names
        # \\?\ -> literal paths
        # do nie do any normalization, but zwróć the path unchanged
        zwróć path
    path = path.replace(altsep, sep)
    prefix, path = splitdrive(path)

    # collapse initial backslashes
    jeżeli path.startswith(sep):
        prefix += sep
        path = path.lstrip(sep)

    comps = path.split(sep)
    i = 0
    dopóki i < len(comps):
        jeżeli nie comps[i] albo comps[i] == curdir:
            usuń comps[i]
        albo_inaczej comps[i] == pardir:
            jeżeli i > 0 oraz comps[i-1] != pardir:
                usuń comps[i-1:i+1]
                i -= 1
            albo_inaczej i == 0 oraz prefix.endswith(sep):
                usuń comps[i]
            inaczej:
                i += 1
        inaczej:
            i += 1
    # If the path jest now empty, substitute '.'
    jeżeli nie prefix oraz nie comps:
        comps.append(curdir)
    zwróć prefix + sep.join(comps)


# Return an absolute path.
spróbuj:
    z nt zaimportuj _getfullpathname

wyjąwszy ImportError: # nie running on Windows - mock up something sensible
    def abspath(path):
        """Return the absolute version of a path."""
        jeżeli nie isabs(path):
            jeżeli isinstance(path, bytes):
                cwd = os.getcwdb()
            inaczej:
                cwd = os.getcwd()
            path = join(cwd, path)
        zwróć normpath(path)

inaczej:  # use native Windows method on Windows
    def abspath(path):
        """Return the absolute version of a path."""

        jeżeli path: # Empty path must zwróć current working directory.
            spróbuj:
                path = _getfullpathname(path)
            wyjąwszy OSError:
                dalej # Bad path - zwróć unchanged.
        albo_inaczej isinstance(path, bytes):
            path = os.getcwdb()
        inaczej:
            path = os.getcwd()
        zwróć normpath(path)

# realpath jest a no-op on systems without islink support
realpath = abspath
# Win9x family oraz earlier have no Unicode filename support.
supports_unicode_filenames = (hasattr(sys, "getwindowsversion") oraz
                              sys.getwindowsversion()[3] >= 2)

def relpath(path, start=Nic):
    """Return a relative version of a path"""
    jeżeli isinstance(path, bytes):
        sep = b'\\'
        curdir = b'.'
        pardir = b'..'
    inaczej:
        sep = '\\'
        curdir = '.'
        pardir = '..'

    jeżeli start jest Nic:
        start = curdir

    jeżeli nie path:
        podnieś ValueError("no path specified")

    spróbuj:
        start_abs = abspath(normpath(start))
        path_abs = abspath(normpath(path))
        start_drive, start_rest = splitdrive(start_abs)
        path_drive, path_rest = splitdrive(path_abs)
        jeżeli normcase(start_drive) != normcase(path_drive):
            podnieś ValueError("path jest on mount %r, start on mount %r" % (
                path_drive, start_drive))

        start_list = [x dla x w start_rest.split(sep) jeżeli x]
        path_list = [x dla x w path_rest.split(sep) jeżeli x]
        # Work out how much of the filepath jest shared by start oraz path.
        i = 0
        dla e1, e2 w zip(start_list, path_list):
            jeżeli normcase(e1) != normcase(e2):
                przerwij
            i += 1

        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        jeżeli nie rel_list:
            zwróć curdir
        zwróć join(*rel_list)
    wyjąwszy (TypeError, ValueError, AttributeError, BytesWarning, DeprecationWarning):
        genericpath._check_arg_types('relpath', path, start)
        podnieś


# Return the longest common sub-path of the sequence of paths given jako input.
# The function jest case-insensitive oraz 'separator-insensitive', i.e. jeżeli the
# only difference between two paths jest the use of '\' versus '/' jako separator,
# they are deemed to be equal.
#
# However, the returned path will have the standard '\' separator (even jeżeli the
# given paths had the alternative '/' separator) oraz will have the case of the
# first path given w the sequence. Additionally, any trailing separator jest
# stripped z the returned path.

def commonpath(paths):
    """Given a sequence of path names, returns the longest common sub-path."""

    jeżeli nie paths:
        podnieś ValueError('commonpath() arg jest an empty sequence')

    jeżeli isinstance(paths[0], bytes):
        sep = b'\\'
        altsep = b'/'
        curdir = b'.'
    inaczej:
        sep = '\\'
        altsep = '/'
        curdir = '.'

    spróbuj:
        drivesplits = [splitdrive(p.replace(altsep, sep).lower()) dla p w paths]
        split_paths = [p.split(sep) dla d, p w drivesplits]

        spróbuj:
            isabs, = set(p[:1] == sep dla d, p w drivesplits)
        wyjąwszy ValueError:
            podnieś ValueError("Can't mix absolute oraz relative paths") z Nic

        # Check that all drive letters albo UNC paths match. The check jest made only
        # now otherwise type errors dla mixing strings oraz bytes would nie be
        # caught.
        jeżeli len(set(d dla d, p w drivesplits)) != 1:
            podnieś ValueError("Paths don't have the same drive")

        drive, path = splitdrive(paths[0].replace(altsep, sep))
        common = path.split(sep)
        common = [c dla c w common jeżeli c oraz c != curdir]

        split_paths = [[c dla c w s jeżeli c oraz c != curdir] dla s w split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        dla i, c w enumerate(s1):
            jeżeli c != s2[i]:
                common = common[:i]
                przerwij
        inaczej:
            common = common[:len(s1)]

        prefix = drive + sep jeżeli isabs inaczej drive
        zwróć prefix + sep.join(common)
    wyjąwszy (TypeError, AttributeError):
        genericpath._check_arg_types('commonpath', *paths)
        podnieś


# determine jeżeli two files are w fact the same file
spróbuj:
    # GetFinalPathNameByHandle jest available starting przy Windows 6.0.
    # Windows XP oraz non-Windows OS'es will mock _getfinalpathname.
    jeżeli sys.getwindowsversion()[:2] >= (6, 0):
        z nt zaimportuj _getfinalpathname
    inaczej:
        podnieś ImportError
wyjąwszy (AttributeError, ImportError):
    # On Windows XP oraz earlier, two files are the same jeżeli their absolute
    # pathnames are the same.
    # Non-Windows operating systems fake this method przy an XP
    # approximation.
    def _getfinalpathname(f):
        zwróć normcase(abspath(f))


spróbuj:
    # The genericpath.isdir implementation uses os.stat oraz checks the mode
    # attribute to tell whether albo nie the path jest a directory.
    # This jest overkill on Windows - just dalej the path to GetFileAttributes
    # oraz check the attribute z there.
    z nt zaimportuj _isdir jako isdir
wyjąwszy ImportError:
    # Use genericpath.isdir jako imported above.
    dalej
