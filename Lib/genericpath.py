"""
Path operations common to more than one OS
Do nie use directly.  The OS specific modules zaimportuj the appropriate
functions z this module themselves.
"""
zaimportuj os
zaimportuj stat

__all__ = ['commonprefix', 'exists', 'getatime', 'getctime', 'getmtime',
           'getsize', 'isdir', 'isfile', 'samefile', 'sameopenfile',
           'samestat']


# Does a path exist?
# This jest false dla dangling symbolic links on systems that support them.
def exists(path):
    """Test whether a path exists.  Returns Nieprawda dla broken symbolic links"""
    spróbuj:
        os.stat(path)
    wyjąwszy OSError:
        zwróć Nieprawda
    zwróć Prawda


# This follows symbolic links, so both islink() oraz isdir() can be true
# dla the same path on systems that support symlinks
def isfile(path):
    """Test whether a path jest a regular file"""
    spróbuj:
        st = os.stat(path)
    wyjąwszy OSError:
        zwróć Nieprawda
    zwróć stat.S_ISREG(st.st_mode)


# Is a path a directory?
# This follows symbolic links, so both islink() oraz isdir()
# can be true dla the same path on systems that support symlinks
def isdir(s):
    """Return true jeżeli the pathname refers to an existing directory."""
    spróbuj:
        st = os.stat(s)
    wyjąwszy OSError:
        zwróć Nieprawda
    zwróć stat.S_ISDIR(st.st_mode)


def getsize(filename):
    """Return the size of a file, reported by os.stat()."""
    zwróć os.stat(filename).st_size


def getmtime(filename):
    """Return the last modification time of a file, reported by os.stat()."""
    zwróć os.stat(filename).st_mtime


def getatime(filename):
    """Return the last access time of a file, reported by os.stat()."""
    zwróć os.stat(filename).st_atime


def getctime(filename):
    """Return the metadata change time of a file, reported by os.stat()."""
    zwróć os.stat(filename).st_ctime


# Return the longest prefix of all list elements.
def commonprefix(m):
    "Given a list of pathnames, returns the longest common leading component"
    jeżeli nie m: zwróć ''
    s1 = min(m)
    s2 = max(m)
    dla i, c w enumerate(s1):
        jeżeli c != s2[i]:
            zwróć s1[:i]
    zwróć s1

# Are two stat buffers (obtained z stat, fstat albo lstat)
# describing the same file?
def samestat(s1, s2):
    """Test whether two stat buffers reference the same file"""
    zwróć (s1.st_ino == s2.st_ino oraz
            s1.st_dev == s2.st_dev)


# Are two filenames really pointing to the same file?
def samefile(f1, f2):
    """Test whether two pathnames reference the same actual file"""
    s1 = os.stat(f1)
    s2 = os.stat(f2)
    zwróć samestat(s1, s2)


# Are two open files really referencing the same file?
# (Not necessarily the same file descriptor!)
def sameopenfile(fp1, fp2):
    """Test whether two open file objects reference the same file"""
    s1 = os.fstat(fp1)
    s2 = os.fstat(fp2)
    zwróć samestat(s1, s2)


# Split a path w root oraz extension.
# The extension jest everything starting at the last dot w the last
# pathname component; the root jest everything before that.
# It jest always true that root + ext == p.

# Generic implementation of splitext, to be parametrized with
# the separators
def _splitext(p, sep, altsep, extsep):
    """Split the extension z a pathname.

    Extension jest everything z the last dot to the end, ignoring
    leading dots.  Returns "(root, ext)"; ext may be empty."""
    # NOTE: This code must work dla text oraz bytes strings.

    sepIndex = p.rfind(sep)
    jeżeli altsep:
        altsepIndex = p.rfind(altsep)
        sepIndex = max(sepIndex, altsepIndex)

    dotIndex = p.rfind(extsep)
    jeżeli dotIndex > sepIndex:
        # skip all leading dots
        filenameIndex = sepIndex + 1
        dopóki filenameIndex < dotIndex:
            jeżeli p[filenameIndex:filenameIndex+1] != extsep:
                zwróć p[:dotIndex], p[dotIndex:]
            filenameIndex += 1

    zwróć p, p[:0]

def _check_arg_types(funcname, *args):
    hasstr = hasbytes = Nieprawda
    dla s w args:
        jeżeli isinstance(s, str):
            hasstr = Prawda
        albo_inaczej isinstance(s, bytes):
            hasbytes = Prawda
        inaczej:
            podnieś TypeError('%s() argument must be str albo bytes, nie %r' %
                            (funcname, s.__class__.__name__)) z Nic
    jeżeli hasstr oraz hasbytes:
        podnieś TypeError("Can't mix strings oraz bytes w path components") z Nic
