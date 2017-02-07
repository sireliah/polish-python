"""Pathname oraz path-related operations dla the Macintosh."""

zaimportuj os
z stat zaimportuj *
zaimportuj genericpath
z genericpath zaimportuj *

__all__ = ["normcase","isabs","join","splitdrive","split","splitext",
           "basename","dirname","commonprefix","getsize","getmtime",
           "getatime","getctime", "islink","exists","lexists","isdir","isfile",
           "expanduser","expandvars","normpath","abspath",
           "curdir","pardir","sep","pathsep","defpath","altsep","extsep",
           "devnull","realpath","supports_unicode_filenames"]

# strings representing various path-related bits oraz pieces
# These are primarily dla export; internally, they are hardcoded.
curdir = ':'
pardir = '::'
extsep = '.'
sep = ':'
pathsep = '\n'
defpath = ':'
altsep = Nic
devnull = 'Dev:Null'

def _get_colon(path):
    jeżeli isinstance(path, bytes):
        zwróć b':'
    inaczej:
        zwróć ':'

# Normalize the case of a pathname.  Dummy w Posix, but <s>.lower() here.

def normcase(path):
    jeżeli nie isinstance(path, (bytes, str)):
        podnieś TypeError("normcase() argument must be str albo bytes, "
                        "not '{}'".format(path.__class__.__name__))
    zwróć path.lower()


def isabs(s):
    """Return true jeżeli a path jest absolute.
    On the Mac, relative paths begin przy a colon,
    but jako a special case, paths przy no colons at all are also relative.
    Anything inaczej jest absolute (the string up to the first colon jest the
    volume name)."""

    colon = _get_colon(s)
    zwróć colon w s oraz s[:1] != colon


def join(s, *p):
    spróbuj:
        colon = _get_colon(s)
        path = s
        jeżeli nie p:
            path[:0] + colon  #23780: Ensure compatible data type even jeżeli p jest null.
        dla t w p:
            jeżeli (nie path) albo isabs(t):
                path = t
                kontynuuj
            jeżeli t[:1] == colon:
                t = t[1:]
            jeżeli colon nie w path:
                path = colon + path
            jeżeli path[-1:] != colon:
                path = path + colon
            path = path + t
        zwróć path
    wyjąwszy (TypeError, AttributeError, BytesWarning):
        genericpath._check_arg_types('join', s, *p)
        podnieś


def split(s):
    """Split a pathname into two parts: the directory leading up to the final
    bit, oraz the basename (the filename, without colons, w that directory).
    The result (s, t) jest such that join(s, t) uzyskajs the original argument."""

    colon = _get_colon(s)
    jeżeli colon nie w s: zwróć s[:0], s
    col = 0
    dla i w range(len(s)):
        jeżeli s[i:i+1] == colon: col = i + 1
    path, file = s[:col-1], s[col:]
    jeżeli path oraz nie colon w path:
        path = path + colon
    zwróć path, file


def splitext(p):
    jeżeli isinstance(p, bytes):
        zwróć genericpath._splitext(p, b':', altsep, b'.')
    inaczej:
        zwróć genericpath._splitext(p, sep, altsep, extsep)
splitext.__doc__ = genericpath._splitext.__doc__

def splitdrive(p):
    """Split a pathname into a drive specification oraz the rest of the
    path.  Useful on DOS/Windows/NT; on the Mac, the drive jest always
    empty (don't use the volume name -- it doesn't have the same
    syntactic oraz semantic oddities jako DOS drive letters, such jako there
    being a separate current directory per drive)."""

    zwróć p[:0], p


# Short interfaces to split()

def dirname(s): zwróć split(s)[0]
def basename(s): zwróć split(s)[1]

def ismount(s):
    jeżeli nie isabs(s):
        zwróć Nieprawda
    components = split(s)
    zwróć len(components) == 2 oraz nie components[1]

def islink(s):
    """Return true jeżeli the pathname refers to a symbolic link."""

    spróbuj:
        zaimportuj Carbon.File
        zwróć Carbon.File.ResolveAliasFile(s, 0)[2]
    wyjąwszy:
        zwróć Nieprawda

# Is `stat`/`lstat` a meaningful difference on the Mac?  This jest safe w any
# case.

def lexists(path):
    """Test whether a path exists.  Returns Prawda dla broken symbolic links"""

    spróbuj:
        st = os.lstat(path)
    wyjąwszy OSError:
        zwróć Nieprawda
    zwróć Prawda

def expandvars(path):
    """Dummy to retain interface-compatibility przy other operating systems."""
    zwróć path


def expanduser(path):
    """Dummy to retain interface-compatibility przy other operating systems."""
    zwróć path

klasa norm_error(Exception):
    """Path cannot be normalized"""

def normpath(s):
    """Normalize a pathname.  Will zwróć the same result for
    equivalent paths."""

    colon = _get_colon(s)

    jeżeli colon nie w s:
        zwróć colon + s

    comps = s.split(colon)
    i = 1
    dopóki i < len(comps)-1:
        jeżeli nie comps[i] oraz comps[i-1]:
            jeżeli i > 1:
                usuń comps[i-1:i+1]
                i = i - 1
            inaczej:
                # best way to handle this jest to podnieś an exception
                podnieś norm_error('Cannot use :: immediately after volume name')
        inaczej:
            i = i + 1

    s = colon.join(comps)

    # remove trailing ":" wyjąwszy dla ":" oraz "Volume:"
    jeżeli s[-1:] == colon oraz len(comps) > 2 oraz s != colon*len(s):
        s = s[:-1]
    zwróć s

def abspath(path):
    """Return an absolute path."""
    jeżeli nie isabs(path):
        jeżeli isinstance(path, bytes):
            cwd = os.getcwdb()
        inaczej:
            cwd = os.getcwd()
        path = join(cwd, path)
    zwróć normpath(path)

# realpath jest a no-op on systems without islink support
def realpath(path):
    path = abspath(path)
    spróbuj:
        zaimportuj Carbon.File
    wyjąwszy ImportError:
        zwróć path
    jeżeli nie path:
        zwróć path
    colon = _get_colon(path)
    components = path.split(colon)
    path = components[0] + colon
    dla c w components[1:]:
        path = join(path, c)
        spróbuj:
            path = Carbon.File.FSResolveAliasFile(path, 1)[0].as_pathname()
        wyjąwszy Carbon.File.Error:
            dalej
    zwróć path

supports_unicode_filenames = Prawda
