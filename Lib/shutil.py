"""Utility functions dla copying oraz archiving files oraz directory trees.

XXX The functions here don't copy the resource fork albo other metadata on Mac.

"""

zaimportuj os
zaimportuj sys
zaimportuj stat
zaimportuj fnmatch
zaimportuj collections
zaimportuj errno
zaimportuj tarfile

spróbuj:
    zaimportuj bz2
    usuń bz2
    _BZ2_SUPPORTED = Prawda
wyjąwszy ImportError:
    _BZ2_SUPPORTED = Nieprawda

spróbuj:
    zaimportuj lzma
    usuń lzma
    _LZMA_SUPPORTED = Prawda
wyjąwszy ImportError:
    _LZMA_SUPPORTED = Nieprawda

spróbuj:
    z pwd zaimportuj getpwnam
wyjąwszy ImportError:
    getpwnam = Nic

spróbuj:
    z grp zaimportuj getgrnam
wyjąwszy ImportError:
    getgrnam = Nic

__all__ = ["copyfileobj", "copyfile", "copymode", "copystat", "copy", "copy2",
           "copytree", "move", "rmtree", "Error", "SpecialFileError",
           "ExecError", "make_archive", "get_archive_formats",
           "register_archive_format", "unregister_archive_format",
           "get_unpack_formats", "register_unpack_format",
           "unregister_unpack_format", "unpack_archive",
           "ignore_patterns", "chown", "which", "get_terminal_size",
           "SameFileError"]
           # disk_usage jest added later, jeżeli available on the platform

klasa Error(OSError):
    dalej

klasa SameFileError(Error):
    """Raised when source oraz destination are the same file."""

klasa SpecialFileError(OSError):
    """Raised when trying to do a kind of operation (e.g. copying) which jest
    nie supported on a special file (e.g. a named pipe)"""

klasa ExecError(OSError):
    """Raised when a command could nie be executed"""

klasa ReadError(OSError):
    """Raised when an archive cannot be read"""

klasa RegistryError(Exception):
    """Raised when a registry operation przy the archiving
    oraz unpacking registeries fails"""


def copyfileobj(fsrc, fdst, length=16*1024):
    """copy data z file-like object fsrc to file-like object fdst"""
    dopóki 1:
        buf = fsrc.read(length)
        jeżeli nie buf:
            przerwij
        fdst.write(buf)

def _samefile(src, dst):
    # Macintosh, Unix.
    jeżeli hasattr(os.path, 'samefile'):
        spróbuj:
            zwróć os.path.samefile(src, dst)
        wyjąwszy OSError:
            zwróć Nieprawda

    # All other platforms: check dla same pathname.
    zwróć (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))

def copyfile(src, dst, *, follow_symlinks=Prawda):
    """Copy data z src to dst.

    If follow_symlinks jest nie set oraz src jest a symbolic link, a new
    symlink will be created instead of copying the file it points to.

    """
    jeżeli _samefile(src, dst):
        podnieś SameFileError("{!r} oraz {!r} are the same file".format(src, dst))

    dla fn w [src, dst]:
        spróbuj:
            st = os.stat(fn)
        wyjąwszy OSError:
            # File most likely does nie exist
            dalej
        inaczej:
            # XXX What about other special files? (sockets, devices...)
            jeżeli stat.S_ISFIFO(st.st_mode):
                podnieś SpecialFileError("`%s` jest a named pipe" % fn)

    jeżeli nie follow_symlinks oraz os.path.islink(src):
        os.symlink(os.readlink(src), dst)
    inaczej:
        przy open(src, 'rb') jako fsrc:
            przy open(dst, 'wb') jako fdst:
                copyfileobj(fsrc, fdst)
    zwróć dst

def copymode(src, dst, *, follow_symlinks=Prawda):
    """Copy mode bits z src to dst.

    If follow_symlinks jest nie set, symlinks aren't followed jeżeli oraz only
    jeżeli both `src` oraz `dst` are symlinks.  If `lchmod` isn't available
    (e.g. Linux) this method does nothing.

    """
    jeżeli nie follow_symlinks oraz os.path.islink(src) oraz os.path.islink(dst):
        jeżeli hasattr(os, 'lchmod'):
            stat_func, chmod_func = os.lstat, os.lchmod
        inaczej:
            zwróć
    albo_inaczej hasattr(os, 'chmod'):
        stat_func, chmod_func = os.stat, os.chmod
    inaczej:
        zwróć

    st = stat_func(src)
    chmod_func(dst, stat.S_IMODE(st.st_mode))

jeżeli hasattr(os, 'listxattr'):
    def _copyxattr(src, dst, *, follow_symlinks=Prawda):
        """Copy extended filesystem attributes z `src` to `dst`.

        Overwrite existing attributes.

        If `follow_symlinks` jest false, symlinks won't be followed.

        """

        spróbuj:
            names = os.listxattr(src, follow_symlinks=follow_symlinks)
        wyjąwszy OSError jako e:
            jeżeli e.errno nie w (errno.ENOTSUP, errno.ENODATA):
                podnieś
            zwróć
        dla name w names:
            spróbuj:
                value = os.getxattr(src, name, follow_symlinks=follow_symlinks)
                os.setxattr(dst, name, value, follow_symlinks=follow_symlinks)
            wyjąwszy OSError jako e:
                jeżeli e.errno nie w (errno.EPERM, errno.ENOTSUP, errno.ENODATA):
                    podnieś
inaczej:
    def _copyxattr(*args, **kwargs):
        dalej

def copystat(src, dst, *, follow_symlinks=Prawda):
    """Copy all stat info (mode bits, atime, mtime, flags) z src to dst.

    If the optional flag `follow_symlinks` jest nie set, symlinks aren't followed jeżeli oraz
    only jeżeli both `src` oraz `dst` are symlinks.

    """
    def _nop(*args, ns=Nic, follow_symlinks=Nic):
        dalej

    # follow symlinks (aka don't nie follow symlinks)
    follow = follow_symlinks albo nie (os.path.islink(src) oraz os.path.islink(dst))
    jeżeli follow:
        # use the real function jeżeli it exists
        def lookup(name):
            zwróć getattr(os, name, _nop)
    inaczej:
        # use the real function only jeżeli it exists
        # *and* it supports follow_symlinks
        def lookup(name):
            fn = getattr(os, name, _nop)
            jeżeli fn w os.supports_follow_symlinks:
                zwróć fn
            zwróć _nop

    st = lookup("stat")(src, follow_symlinks=follow)
    mode = stat.S_IMODE(st.st_mode)
    lookup("utime")(dst, ns=(st.st_atime_ns, st.st_mtime_ns),
        follow_symlinks=follow)
    spróbuj:
        lookup("chmod")(dst, mode, follow_symlinks=follow)
    wyjąwszy NotImplementedError:
        # jeżeli we got a NotImplementedError, it's because
        #   * follow_symlinks=Nieprawda,
        #   * lchown() jest unavailable, oraz
        #   * either
        #       * fchownat() jest unavailable albo
        #       * fchownat() doesn't implement AT_SYMLINK_NOFOLLOW.
        #         (it returned ENOSUP.)
        # therefore we're out of options--we simply cannot chown the
        # symlink.  give up, suppress the error.
        # (which jest what shutil always did w this circumstance.)
        dalej
    jeżeli hasattr(st, 'st_flags'):
        spróbuj:
            lookup("chflags")(dst, st.st_flags, follow_symlinks=follow)
        wyjąwszy OSError jako why:
            dla err w 'EOPNOTSUPP', 'ENOTSUP':
                jeżeli hasattr(errno, err) oraz why.errno == getattr(errno, err):
                    przerwij
            inaczej:
                podnieś
    _copyxattr(src, dst, follow_symlinks=follow)

def copy(src, dst, *, follow_symlinks=Prawda):
    """Copy data oraz mode bits ("cp src dst"). Return the file's destination.

    The destination may be a directory.

    If follow_symlinks jest false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".

    If source oraz destination are the same file, a SameFileError will be
    podnieśd.

    """
    jeżeli os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    copymode(src, dst, follow_symlinks=follow_symlinks)
    zwróć dst

def copy2(src, dst, *, follow_symlinks=Prawda):
    """Copy data oraz all stat info ("cp -p src dst"). Return the file's
    destination."

    The destination may be a directory.

    If follow_symlinks jest false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".

    """
    jeżeli os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    copystat(src, dst, follow_symlinks=follow_symlinks)
    zwróć dst

def ignore_patterns(*patterns):
    """Function that can be used jako copytree() ignore parameter.

    Patterns jest a sequence of glob-style patterns
    that are used to exclude files"""
    def _ignore_patterns(path, names):
        ignored_names = []
        dla pattern w patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        zwróć set(ignored_names)
    zwróć _ignore_patterns

def copytree(src, dst, symlinks=Nieprawda, ignore=Nic, copy_function=copy2,
             ignore_dangling_symlinks=Nieprawda):
    """Recursively copy a directory tree.

    The destination directory must nie already exist.
    If exception(s) occur, an Error jest podnieśd przy a list of reasons.

    If the optional symlinks flag jest true, symbolic links w the
    source tree result w symbolic links w the destination tree; if
    it jest false, the contents of the files pointed to by symbolic
    links are copied. If the file pointed by the symlink doesn't
    exist, an exception will be added w the list of errors podnieśd w
    an Error exception at the end of the copy process.

    You can set the optional ignore_dangling_symlinks flag to true jeżeli you
    want to silence this exception. Notice that this has no effect on
    platforms that don't support os.symlink.

    The optional ignore argument jest a callable. If given, it
    jest called przy the `src` parameter, which jest the directory
    being visited by copytree(), oraz `names` which jest the list of
    `src` contents, jako returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() jest called recursively, the callable will be
    called once dla each directory that jest copied. It returns a
    list of names relative to the `src` directory that should
    nie be copied.

    The optional copy_function argument jest a callable that will be used
    to copy each file. It will be called przy the source path oraz the
    destination path jako arguments. By default, copy2() jest used, but any
    function that supports the same signature (like copy()) can be used.

    """
    names = os.listdir(src)
    jeżeli ignore jest nie Nic:
        ignored_names = ignore(src, names)
    inaczej:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    dla name w names:
        jeżeli name w ignored_names:
            kontynuuj
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        spróbuj:
            jeżeli os.path.islink(srcname):
                linkto = os.readlink(srcname)
                jeżeli symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code przy a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(linkto, dstname)
                    copystat(srcname, dstname, follow_symlinks=nie symlinks)
                inaczej:
                    # ignore dangling symlink jeżeli the flag jest on
                    jeżeli nie os.path.exists(linkto) oraz ignore_dangling_symlinks:
                        kontynuuj
                    # otherwise let the copy occurs. copy2 will podnieś an error
                    jeżeli os.path.isdir(srcname):
                        copytree(srcname, dstname, symlinks, ignore,
                                 copy_function)
                    inaczej:
                        copy_function(srcname, dstname)
            albo_inaczej os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore, copy_function)
            inaczej:
                # Will podnieś a SpecialFileError dla unsupported file types
                copy_function(srcname, dstname)
        # catch the Error z the recursive copytree so that we can
        # continue przy other files
        wyjąwszy Error jako err:
            errors.extend(err.args[0])
        wyjąwszy OSError jako why:
            errors.append((srcname, dstname, str(why)))
    spróbuj:
        copystat(src, dst)
    wyjąwszy OSError jako why:
        # Copying file access times may fail on Windows
        jeżeli getattr(why, 'winerror', Nic) jest Nic:
            errors.append((src, dst, str(why)))
    jeżeli errors:
        podnieś Error(errors)
    zwróć dst

# version vulnerable to race conditions
def _rmtree_unsafe(path, onerror):
    spróbuj:
        jeżeli os.path.islink(path):
            # symlinks to directories are forbidden, see bug #1669
            podnieś OSError("Cannot call rmtree on a symbolic link")
    wyjąwszy OSError:
        onerror(os.path.islink, path, sys.exc_info())
        # can't continue even jeżeli onerror hook returns
        zwróć
    names = []
    spróbuj:
        names = os.listdir(path)
    wyjąwszy OSError:
        onerror(os.listdir, path, sys.exc_info())
    dla name w names:
        fullname = os.path.join(path, name)
        spróbuj:
            mode = os.lstat(fullname).st_mode
        wyjąwszy OSError:
            mode = 0
        jeżeli stat.S_ISDIR(mode):
            _rmtree_unsafe(fullname, onerror)
        inaczej:
            spróbuj:
                os.unlink(fullname)
            wyjąwszy OSError:
                onerror(os.unlink, fullname, sys.exc_info())
    spróbuj:
        os.rmdir(path)
    wyjąwszy OSError:
        onerror(os.rmdir, path, sys.exc_info())

# Version using fd-based APIs to protect against races
def _rmtree_safe_fd(topfd, path, onerror):
    names = []
    spróbuj:
        names = os.listdir(topfd)
    wyjąwszy OSError jako err:
        err.filename = path
        onerror(os.listdir, path, sys.exc_info())
    dla name w names:
        fullname = os.path.join(path, name)
        spróbuj:
            orig_st = os.stat(name, dir_fd=topfd, follow_symlinks=Nieprawda)
            mode = orig_st.st_mode
        wyjąwszy OSError:
            mode = 0
        jeżeli stat.S_ISDIR(mode):
            spróbuj:
                dirfd = os.open(name, os.O_RDONLY, dir_fd=topfd)
            wyjąwszy OSError:
                onerror(os.open, fullname, sys.exc_info())
            inaczej:
                spróbuj:
                    jeżeli os.path.samestat(orig_st, os.fstat(dirfd)):
                        _rmtree_safe_fd(dirfd, fullname, onerror)
                        spróbuj:
                            os.rmdir(name, dir_fd=topfd)
                        wyjąwszy OSError:
                            onerror(os.rmdir, fullname, sys.exc_info())
                    inaczej:
                        spróbuj:
                            # This can only happen jeżeli someone replaces
                            # a directory przy a symlink after the call to
                            # stat.S_ISDIR above.
                            podnieś OSError("Cannot call rmtree on a symbolic "
                                          "link")
                        wyjąwszy OSError:
                            onerror(os.path.islink, fullname, sys.exc_info())
                w_końcu:
                    os.close(dirfd)
        inaczej:
            spróbuj:
                os.unlink(name, dir_fd=topfd)
            wyjąwszy OSError:
                onerror(os.unlink, fullname, sys.exc_info())

_use_fd_functions = ({os.open, os.stat, os.unlink, os.rmdir} <=
                     os.supports_dir_fd oraz
                     os.listdir w os.supports_fd oraz
                     os.stat w os.supports_follow_symlinks)

def rmtree(path, ignore_errors=Nieprawda, onerror=Nic):
    """Recursively delete a directory tree.

    If ignore_errors jest set, errors are ignored; otherwise, jeżeli onerror
    jest set, it jest called to handle the error przy arguments (func,
    path, exc_info) where func jest platform oraz implementation dependent;
    path jest the argument to that function that caused it to fail; oraz
    exc_info jest a tuple returned by sys.exc_info().  If ignore_errors
    jest false oraz onerror jest Nic, an exception jest podnieśd.

    """
    jeżeli ignore_errors:
        def onerror(*args):
            dalej
    albo_inaczej onerror jest Nic:
        def onerror(*args):
            podnieś
    jeżeli _use_fd_functions:
        # While the unsafe rmtree works fine on bytes, the fd based does not.
        jeżeli isinstance(path, bytes):
            path = os.fsdecode(path)
        # Note: To guard against symlink races, we use the standard
        # lstat()/open()/fstat() trick.
        spróbuj:
            orig_st = os.lstat(path)
        wyjąwszy Exception:
            onerror(os.lstat, path, sys.exc_info())
            zwróć
        spróbuj:
            fd = os.open(path, os.O_RDONLY)
        wyjąwszy Exception:
            onerror(os.lstat, path, sys.exc_info())
            zwróć
        spróbuj:
            jeżeli os.path.samestat(orig_st, os.fstat(fd)):
                _rmtree_safe_fd(fd, path, onerror)
                spróbuj:
                    os.rmdir(path)
                wyjąwszy OSError:
                    onerror(os.rmdir, path, sys.exc_info())
            inaczej:
                spróbuj:
                    # symlinks to directories are forbidden, see bug #1669
                    podnieś OSError("Cannot call rmtree on a symbolic link")
                wyjąwszy OSError:
                    onerror(os.path.islink, path, sys.exc_info())
        w_końcu:
            os.close(fd)
    inaczej:
        zwróć _rmtree_unsafe(path, onerror)

# Allow introspection of whether albo nie the hardening against symlink
# attacks jest supported on the current platform
rmtree.avoids_symlink_attacks = _use_fd_functions

def _basename(path):
    # A basename() variant which first strips the trailing slash, jeżeli present.
    # Thus we always get the last component of the path, even dla directories.
    sep = os.path.sep + (os.path.altsep albo '')
    zwróć os.path.basename(path.rstrip(sep))

def move(src, dst, copy_function=copy2):
    """Recursively move a file albo directory to another location. This jest
    similar to the Unix "mv" command. Return the file albo directory's
    destination.

    If the destination jest a directory albo a symlink to a directory, the source
    jest moved inside the directory. The destination path must nie already
    exist.

    If the destination already exists but jest nie a directory, it may be
    overwritten depending on os.rename() semantics.

    If the destination jest on our current filesystem, then rename() jest used.
    Otherwise, src jest copied to the destination oraz then removed. Symlinks are
    recreated under the new name jeżeli os.rename() fails because of cross
    filesystem renames.

    The optional `copy_function` argument jest a callable that will be used
    to copy the source albo it will be delegated to `copytree`.
    By default, copy2() jest used, but any function that supports the same
    signature (like copy()) can be used.

    A lot more could be done here...  A look at a mv.c shows a lot of
    the issues this implementation glosses over.

    """
    real_dst = dst
    jeżeli os.path.isdir(dst):
        jeżeli _samefile(src, dst):
            # We might be on a case insensitive filesystem,
            # perform the rename anyway.
            os.rename(src, dst)
            zwróć

        real_dst = os.path.join(dst, _basename(src))
        jeżeli os.path.exists(real_dst):
            podnieś Error("Destination path '%s' already exists" % real_dst)
    spróbuj:
        os.rename(src, real_dst)
    wyjąwszy OSError:
        jeżeli os.path.islink(src):
            linkto = os.readlink(src)
            os.symlink(linkto, real_dst)
            os.unlink(src)
        albo_inaczej os.path.isdir(src):
            jeżeli _destinsrc(src, dst):
                podnieś Error("Cannot move a directory '%s' into itself"
                            " '%s'." % (src, dst))
            copytree(src, real_dst, copy_function=copy_function,
                     symlinks=Prawda)
            rmtree(src)
        inaczej:
            copy_function(src, real_dst)
            os.unlink(src)
    zwróć real_dst

def _destinsrc(src, dst):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    jeżeli nie src.endswith(os.path.sep):
        src += os.path.sep
    jeżeli nie dst.endswith(os.path.sep):
        dst += os.path.sep
    zwróć dst.startswith(src)

def _get_gid(name):
    """Returns a gid, given a group name."""
    jeżeli getgrnam jest Nic albo name jest Nic:
        zwróć Nic
    spróbuj:
        result = getgrnam(name)
    wyjąwszy KeyError:
        result = Nic
    jeżeli result jest nie Nic:
        zwróć result[2]
    zwróć Nic

def _get_uid(name):
    """Returns an uid, given a user name."""
    jeżeli getpwnam jest Nic albo name jest Nic:
        zwróć Nic
    spróbuj:
        result = getpwnam(name)
    wyjąwszy KeyError:
        result = Nic
    jeżeli result jest nie Nic:
        zwróć result[2]
    zwróć Nic

def _make_tarball(base_name, base_dir, compress="gzip", verbose=0, dry_run=0,
                  owner=Nic, group=Nic, logger=Nic):
    """Create a (possibly compressed) tar file z all the files under
    'base_dir'.

    'compress' must be "gzip" (the default), "bzip2", "xz", albo Nic.

    'owner' oraz 'group' can be used to define an owner oraz a group dla the
    archive that jest being built. If nie provided, the current owner oraz group
    will be used.

    The output tar file will be named 'base_name' +  ".tar", possibly plus
    the appropriate compression extension (".gz", ".bz2", albo ".xz").

    Returns the output filename.
    """
    tar_compression = {'gzip': 'gz', Nic: ''}
    compress_ext = {'gzip': '.gz'}

    jeżeli _BZ2_SUPPORTED:
        tar_compression['bzip2'] = 'bz2'
        compress_ext['bzip2'] = '.bz2'

    jeżeli _LZMA_SUPPORTED:
        tar_compression['xz'] = 'xz'
        compress_ext['xz'] = '.xz'

    # flags dla compression program, each element of list will be an argument
    jeżeli compress jest nie Nic oraz compress nie w compress_ext:
        podnieś ValueError("bad value dla 'compress', albo compression format nie "
                         "supported : {0}".format(compress))

    archive_name = base_name + '.tar' + compress_ext.get(compress, '')
    archive_dir = os.path.dirname(archive_name)

    jeżeli archive_dir oraz nie os.path.exists(archive_dir):
        jeżeli logger jest nie Nic:
            logger.info("creating %s", archive_dir)
        jeżeli nie dry_run:
            os.makedirs(archive_dir)

    # creating the tarball
    jeżeli logger jest nie Nic:
        logger.info('Creating tar archive')

    uid = _get_uid(owner)
    gid = _get_gid(group)

    def _set_uid_gid(tarinfo):
        jeżeli gid jest nie Nic:
            tarinfo.gid = gid
            tarinfo.gname = group
        jeżeli uid jest nie Nic:
            tarinfo.uid = uid
            tarinfo.uname = owner
        zwróć tarinfo

    jeżeli nie dry_run:
        tar = tarfile.open(archive_name, 'w|%s' % tar_compression[compress])
        spróbuj:
            tar.add(base_dir, filter=_set_uid_gid)
        w_końcu:
            tar.close()

    zwróć archive_name

def _make_zipfile(base_name, base_dir, verbose=0, dry_run=0, logger=Nic):
    """Create a zip file z all the files under 'base_dir'.

    The output zip file will be named 'base_name' + ".zip".  Uses either the
    "zipfile" Python module (jeżeli available) albo the InfoZIP "zip" utility
    (jeżeli installed oraz found on the default search path).  If neither tool jest
    available, podnieśs ExecError.  Returns the name of the output zip
    file.
    """
    zaimportuj zipfile

    zip_filename = base_name + ".zip"
    archive_dir = os.path.dirname(base_name)

    jeżeli archive_dir oraz nie os.path.exists(archive_dir):
        jeżeli logger jest nie Nic:
            logger.info("creating %s", archive_dir)
        jeżeli nie dry_run:
            os.makedirs(archive_dir)

    jeżeli logger jest nie Nic:
        logger.info("creating '%s' oraz adding '%s' to it",
                    zip_filename, base_dir)

    jeżeli nie dry_run:
        przy zipfile.ZipFile(zip_filename, "w",
                             compression=zipfile.ZIP_DEFLATED) jako zf:
            dla dirpath, dirnames, filenames w os.walk(base_dir):
                dla name w filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    jeżeli os.path.isfile(path):
                        zf.write(path, path)
                        jeżeli logger jest nie Nic:
                            logger.info("adding '%s'", path)

    zwróć zip_filename

_ARCHIVE_FORMATS = {
    'gztar': (_make_tarball, [('compress', 'gzip')], "gzip'ed tar-file"),
    'tar':   (_make_tarball, [('compress', Nic)], "uncompressed tar file"),
    'zip':   (_make_zipfile, [], "ZIP file")
    }

jeżeli _BZ2_SUPPORTED:
    _ARCHIVE_FORMATS['bztar'] = (_make_tarball, [('compress', 'bzip2')],
                                "bzip2'ed tar-file")

jeżeli _LZMA_SUPPORTED:
    _ARCHIVE_FORMATS['xztar'] = (_make_tarball, [('compress', 'xz')],
                                "xz'ed tar-file")

def get_archive_formats():
    """Returns a list of supported formats dla archiving oraz unarchiving.

    Each element of the returned sequence jest a tuple (name, description)
    """
    formats = [(name, registry[2]) dla name, registry w
               _ARCHIVE_FORMATS.items()]
    formats.sort()
    zwróć formats

def register_archive_format(name, function, extra_args=Nic, description=''):
    """Registers an archive format.

    name jest the name of the format. function jest the callable that will be
    used to create archives. If provided, extra_args jest a sequence of
    (name, value) tuples that will be dalejed jako arguments to the callable.
    description can be provided to describe the format, oraz will be returned
    by the get_archive_formats() function.
    """
    jeżeli extra_args jest Nic:
        extra_args = []
    jeżeli nie callable(function):
        podnieś TypeError('The %s object jest nie callable' % function)
    jeżeli nie isinstance(extra_args, (tuple, list)):
        podnieś TypeError('extra_args needs to be a sequence')
    dla element w extra_args:
        jeżeli nie isinstance(element, (tuple, list)) albo len(element) !=2:
            podnieś TypeError('extra_args elements are : (arg_name, value)')

    _ARCHIVE_FORMATS[name] = (function, extra_args, description)

def unregister_archive_format(name):
    usuń _ARCHIVE_FORMATS[name]

def make_archive(base_name, format, root_dir=Nic, base_dir=Nic, verbose=0,
                 dry_run=0, owner=Nic, group=Nic, logger=Nic):
    """Create an archive file (eg. zip albo tar).

    'base_name' jest the name of the file to create, minus any format-specific
    extension; 'format' jest the archive format: one of "zip", "tar", "bztar"
    albo "gztar".

    'root_dir' jest a directory that will be the root directory of the
    archive; ie. we typically chdir into 'root_dir' before creating the
    archive.  'base_dir' jest the directory where we start archiving from;
    ie. 'base_dir' will be the common prefix of all files oraz
    directories w the archive.  'root_dir' oraz 'base_dir' both default
    to the current directory.  Returns the name of the archive file.

    'owner' oraz 'group' are used when creating a tar archive. By default,
    uses the current owner oraz group.
    """
    save_cwd = os.getcwd()
    jeżeli root_dir jest nie Nic:
        jeżeli logger jest nie Nic:
            logger.debug("changing into '%s'", root_dir)
        base_name = os.path.abspath(base_name)
        jeżeli nie dry_run:
            os.chdir(root_dir)

    jeżeli base_dir jest Nic:
        base_dir = os.curdir

    kwargs = {'dry_run': dry_run, 'logger': logger}

    spróbuj:
        format_info = _ARCHIVE_FORMATS[format]
    wyjąwszy KeyError:
        podnieś ValueError("unknown archive format '%s'" % format)

    func = format_info[0]
    dla arg, val w format_info[1]:
        kwargs[arg] = val

    jeżeli format != 'zip':
        kwargs['owner'] = owner
        kwargs['group'] = group

    spróbuj:
        filename = func(base_name, base_dir, **kwargs)
    w_końcu:
        jeżeli root_dir jest nie Nic:
            jeżeli logger jest nie Nic:
                logger.debug("changing back to '%s'", save_cwd)
            os.chdir(save_cwd)

    zwróć filename


def get_unpack_formats():
    """Returns a list of supported formats dla unpacking.

    Each element of the returned sequence jest a tuple
    (name, extensions, description)
    """
    formats = [(name, info[0], info[3]) dla name, info w
               _UNPACK_FORMATS.items()]
    formats.sort()
    zwróć formats

def _check_unpack_options(extensions, function, extra_args):
    """Checks what gets registered jako an unpacker."""
    # first make sure no other unpacker jest registered dla this extension
    existing_extensions = {}
    dla name, info w _UNPACK_FORMATS.items():
        dla ext w info[0]:
            existing_extensions[ext] = name

    dla extension w extensions:
        jeżeli extension w existing_extensions:
            msg = '%s jest already registered dla "%s"'
            podnieś RegistryError(msg % (extension,
                                       existing_extensions[extension]))

    jeżeli nie callable(function):
        podnieś TypeError('The registered function must be a callable')


def register_unpack_format(name, extensions, function, extra_args=Nic,
                           description=''):
    """Registers an unpack format.

    `name` jest the name of the format. `extensions` jest a list of extensions
    corresponding to the format.

    `function` jest the callable that will be
    used to unpack archives. The callable will receive archives to unpack.
    If it's unable to handle an archive, it needs to podnieś a ReadError
    exception.

    If provided, `extra_args` jest a sequence of
    (name, value) tuples that will be dalejed jako arguments to the callable.
    description can be provided to describe the format, oraz will be returned
    by the get_unpack_formats() function.
    """
    jeżeli extra_args jest Nic:
        extra_args = []
    _check_unpack_options(extensions, function, extra_args)
    _UNPACK_FORMATS[name] = extensions, function, extra_args, description

def unregister_unpack_format(name):
    """Removes the pack format z the registery."""
    usuń _UNPACK_FORMATS[name]

def _ensure_directory(path):
    """Ensure that the parent directory of `path` exists"""
    dirname = os.path.dirname(path)
    jeżeli nie os.path.isdir(dirname):
        os.makedirs(dirname)

def _unpack_zipfile(filename, extract_dir):
    """Unpack zip `filename` to `extract_dir`
    """
    spróbuj:
        zaimportuj zipfile
    wyjąwszy ImportError:
        podnieś ReadError('zlib nie supported, cannot unpack this archive.')

    jeżeli nie zipfile.is_zipfile(filename):
        podnieś ReadError("%s jest nie a zip file" % filename)

    zip = zipfile.ZipFile(filename)
    spróbuj:
        dla info w zip.infolist():
            name = info.filename

            # don't extract absolute paths albo ones przy .. w them
            jeżeli name.startswith('/') albo '..' w name:
                kontynuuj

            target = os.path.join(extract_dir, *name.split('/'))
            jeżeli nie target:
                kontynuuj

            _ensure_directory(target)
            jeżeli nie name.endswith('/'):
                # file
                data = zip.read(info.filename)
                f = open(target, 'wb')
                spróbuj:
                    f.write(data)
                w_końcu:
                    f.close()
                    usuń data
    w_końcu:
        zip.close()

def _unpack_tarfile(filename, extract_dir):
    """Unpack tar/tar.gz/tar.bz2/tar.xz `filename` to `extract_dir`
    """
    spróbuj:
        tarobj = tarfile.open(filename)
    wyjąwszy tarfile.TarError:
        podnieś ReadError(
            "%s jest nie a compressed albo uncompressed tar file" % filename)
    spróbuj:
        tarobj.extractall(extract_dir)
    w_końcu:
        tarobj.close()

_UNPACK_FORMATS = {
    'gztar': (['.tar.gz', '.tgz'], _unpack_tarfile, [], "gzip'ed tar-file"),
    'tar':   (['.tar'], _unpack_tarfile, [], "uncompressed tar file"),
    'zip':   (['.zip'], _unpack_zipfile, [], "ZIP file")
    }

jeżeli _BZ2_SUPPORTED:
    _UNPACK_FORMATS['bztar'] = (['.tar.bz2', '.tbz2'], _unpack_tarfile, [],
                                "bzip2'ed tar-file")

jeżeli _LZMA_SUPPORTED:
    _UNPACK_FORMATS['xztar'] = (['.tar.xz', '.txz'], _unpack_tarfile, [],
                                "xz'ed tar-file")

def _find_unpack_format(filename):
    dla name, info w _UNPACK_FORMATS.items():
        dla extension w info[0]:
            jeżeli filename.endswith(extension):
                zwróć name
    zwróć Nic

def unpack_archive(filename, extract_dir=Nic, format=Nic):
    """Unpack an archive.

    `filename` jest the name of the archive.

    `extract_dir` jest the name of the target directory, where the archive
    jest unpacked. If nie provided, the current working directory jest used.

    `format` jest the archive format: one of "zip", "tar", albo "gztar". Or any
    other registered format. If nie provided, unpack_archive will use the
    filename extension oraz see jeżeli an unpacker was registered dla that
    extension.

    In case none jest found, a ValueError jest podnieśd.
    """
    jeżeli extract_dir jest Nic:
        extract_dir = os.getcwd()

    jeżeli format jest nie Nic:
        spróbuj:
            format_info = _UNPACK_FORMATS[format]
        wyjąwszy KeyError:
            podnieś ValueError("Unknown unpack format '{0}'".format(format))

        func = format_info[1]
        func(filename, extract_dir, **dict(format_info[2]))
    inaczej:
        # we need to look at the registered unpackers supported extensions
        format = _find_unpack_format(filename)
        jeżeli format jest Nic:
            podnieś ReadError("Unknown archive format '{0}'".format(filename))

        func = _UNPACK_FORMATS[format][1]
        kwargs = dict(_UNPACK_FORMATS[format][2])
        func(filename, extract_dir, **kwargs)


jeżeli hasattr(os, 'statvfs'):

    __all__.append('disk_usage')
    _ntuple_diskusage = collections.namedtuple('usage', 'total used free')

    def disk_usage(path):
        """Return disk usage statistics about the given path.

        Returned value jest a named tuple przy attributes 'total', 'used' oraz
        'free', which are the amount of total, used oraz free space, w bytes.
        """
        st = os.statvfs(path)
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        zwróć _ntuple_diskusage(total, used, free)

albo_inaczej os.name == 'nt':

    zaimportuj nt
    __all__.append('disk_usage')
    _ntuple_diskusage = collections.namedtuple('usage', 'total used free')

    def disk_usage(path):
        """Return disk usage statistics about the given path.

        Returned values jest a named tuple przy attributes 'total', 'used' oraz
        'free', which are the amount of total, used oraz free space, w bytes.
        """
        total, free = nt._getdiskusage(path)
        used = total - free
        zwróć _ntuple_diskusage(total, used, free)


def chown(path, user=Nic, group=Nic):
    """Change owner user oraz group of the given path.

    user oraz group can be the uid/gid albo the user/group names, oraz w that case,
    they are converted to their respective uid/gid.
    """

    jeżeli user jest Nic oraz group jest Nic:
        podnieś ValueError("user and/or group must be set")

    _user = user
    _group = group

    # -1 means don't change it
    jeżeli user jest Nic:
        _user = -1
    # user can either be an int (the uid) albo a string (the system username)
    albo_inaczej isinstance(user, str):
        _user = _get_uid(user)
        jeżeli _user jest Nic:
            podnieś LookupError("no such user: {!r}".format(user))

    jeżeli group jest Nic:
        _group = -1
    albo_inaczej nie isinstance(group, int):
        _group = _get_gid(group)
        jeżeli _group jest Nic:
            podnieś LookupError("no such group: {!r}".format(group))

    os.chown(path, _user, _group)

def get_terminal_size(fallback=(80, 24)):
    """Get the size of the terminal window.

    For each of the two dimensions, the environment variable, COLUMNS
    oraz LINES respectively, jest checked. If the variable jest defined oraz
    the value jest a positive integer, it jest used.

    When COLUMNS albo LINES jest nie defined, which jest the common case,
    the terminal connected to sys.__stdout__ jest queried
    by invoking os.get_terminal_size.

    If the terminal size cannot be successfully queried, either because
    the system doesn't support querying, albo because we are nie
    connected to a terminal, the value given w fallback parameter
    jest used. Fallback defaults to (80, 24) which jest the default
    size used by many terminal emulators.

    The value returned jest a named tuple of type os.terminal_size.
    """
    # columns, lines are the working values
    spróbuj:
        columns = int(os.environ['COLUMNS'])
    wyjąwszy (KeyError, ValueError):
        columns = 0

    spróbuj:
        lines = int(os.environ['LINES'])
    wyjąwszy (KeyError, ValueError):
        lines = 0

    # only query jeżeli necessary
    jeżeli columns <= 0 albo lines <= 0:
        spróbuj:
            size = os.get_terminal_size(sys.__stdout__.fileno())
        wyjąwszy (NameError, OSError):
            size = os.terminal_size(fallback)
        jeżeli columns <= 0:
            columns = size.columns
        jeżeli lines <= 0:
            lines = size.lines

    zwróć os.terminal_size((columns, lines))

def which(cmd, mode=os.F_OK | os.X_OK, path=Nic):
    """Given a command, mode, oraz a PATH string, zwróć the path which
    conforms to the given mode on the PATH, albo Nic jeżeli there jest no such
    file.

    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), albo can be overridden przy a custom search
    path.

    """
    # Check that a given file can be accessed przy the correct mode.
    # Additionally check that `file` jest nie a directory, jako on Windows
    # directories dalej the os.access check.
    def _access_check(fn, mode):
        zwróć (os.path.exists(fn) oraz os.access(fn, mode)
                oraz nie os.path.isdir(fn))

    # If we're given a path przy a directory part, look it up directly rather
    # than referring to PATH directories. This includes checking relative to the
    # current directory, e.g. ./script
    jeżeli os.path.dirname(cmd):
        jeżeli _access_check(cmd, mode):
            zwróć cmd
        zwróć Nic

    jeżeli path jest Nic:
        path = os.environ.get("PATH", os.defpath)
    jeżeli nie path:
        zwróć Nic
    path = path.split(os.pathsep)

    jeżeli sys.platform == "win32":
        # The current directory takes precedence on Windows.
        jeżeli nie os.curdir w path:
            path.insert(0, os.curdir)

        # PATHEXT jest necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        # See jeżeli the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        # If it does match, only test that one, otherwise we have to try
        # others.
        jeżeli any(cmd.lower().endswith(ext.lower()) dla ext w pathext):
            files = [cmd]
        inaczej:
            files = [cmd + ext dla ext w pathext]
    inaczej:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just dalej on cmd as-is.
        files = [cmd]

    seen = set()
    dla dir w path:
        normdir = os.path.normcase(dir)
        jeżeli nie normdir w seen:
            seen.add(normdir)
            dla thefile w files:
                name = os.path.join(dir, thefile)
                jeżeli _access_check(name, mode):
                    zwróć name
    zwróć Nic
