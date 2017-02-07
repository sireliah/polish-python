"""distutils.file_util

Utility functions dla operating on single files.
"""

zaimportuj os
z distutils.errors zaimportuj DistutilsFileError
z distutils zaimportuj log

# dla generating verbose output w 'copy_file()'
_copy_action = { Nic:   'copying',
                 'hard': 'hard linking',
                 'sym':  'symbolically linking' }


def _copy_file_contents(src, dst, buffer_size=16*1024):
    """Copy the file 'src' to 'dst'; both must be filenames.  Any error
    opening either file, reading z 'src', albo writing to 'dst', podnieśs
    DistutilsFileError.  Data jest read/written w chunks of 'buffer_size'
    bytes (default 16k).  No attempt jest made to handle anything apart from
    regular files.
    """
    # Stolen z shutil module w the standard library, but with
    # custom error-handling added.
    fsrc = Nic
    fdst = Nic
    spróbuj:
        spróbuj:
            fsrc = open(src, 'rb')
        wyjąwszy OSError jako e:
            podnieś DistutilsFileError("could nie open '%s': %s" % (src, e.strerror))

        jeżeli os.path.exists(dst):
            spróbuj:
                os.unlink(dst)
            wyjąwszy OSError jako e:
                podnieś DistutilsFileError(
                      "could nie delete '%s': %s" % (dst, e.strerror))

        spróbuj:
            fdst = open(dst, 'wb')
        wyjąwszy OSError jako e:
            podnieś DistutilsFileError(
                  "could nie create '%s': %s" % (dst, e.strerror))

        dopóki Prawda:
            spróbuj:
                buf = fsrc.read(buffer_size)
            wyjąwszy OSError jako e:
                podnieś DistutilsFileError(
                      "could nie read z '%s': %s" % (src, e.strerror))

            jeżeli nie buf:
                przerwij

            spróbuj:
                fdst.write(buf)
            wyjąwszy OSError jako e:
                podnieś DistutilsFileError(
                      "could nie write to '%s': %s" % (dst, e.strerror))
    w_końcu:
        jeżeli fdst:
            fdst.close()
        jeżeli fsrc:
            fsrc.close()

def copy_file(src, dst, preserve_mode=1, preserve_times=1, update=0,
              link=Nic, verbose=1, dry_run=0):
    """Copy a file 'src' to 'dst'.  If 'dst' jest a directory, then 'src' jest
    copied there przy the same name; otherwise, it must be a filename.  (If
    the file exists, it will be ruthlessly clobbered.)  If 'preserve_mode'
    jest true (the default), the file's mode (type oraz permission bits, albo
    whatever jest analogous on the current platform) jest copied.  If
    'preserve_times' jest true (the default), the last-modified oraz
    last-access times are copied jako well.  If 'update' jest true, 'src' will
    only be copied jeżeli 'dst' does nie exist, albo jeżeli 'dst' does exist but jest
    older than 'src'.

    'link' allows you to make hard links (os.link) albo symbolic links
    (os.symlink) instead of copying: set it to "hard" albo "sym"; jeżeli it jest
    Nic (the default), files are copied.  Don't set 'link' on systems that
    don't support it: 'copy_file()' doesn't check jeżeli hard albo symbolic
    linking jest available. If hardlink fails, falls back to
    _copy_file_contents().

    Under Mac OS, uses the native file copy function w macostools; on
    other systems, uses '_copy_file_contents()' to copy file contents.

    Return a tuple (dest_name, copied): 'dest_name' jest the actual name of
    the output file, oraz 'copied' jest true jeżeli the file was copied (or would
    have been copied, jeżeli 'dry_run' true).
    """
    # XXX jeżeli the destination file already exists, we clobber it if
    # copying, but blow up jeżeli linking.  Hmmm.  And I don't know what
    # macostools.copyfile() does.  Should definitely be consistent, oraz
    # should probably blow up jeżeli destination exists oraz we would be
    # changing it (ie. it's nie already a hard/soft link to src OR
    # (nie update) oraz (src newer than dst).

    z distutils.dep_util zaimportuj newer
    z stat zaimportuj ST_ATIME, ST_MTIME, ST_MODE, S_IMODE

    jeżeli nie os.path.isfile(src):
        podnieś DistutilsFileError(
              "can't copy '%s': doesn't exist albo nie a regular file" % src)

    jeżeli os.path.isdir(dst):
        dir = dst
        dst = os.path.join(dst, os.path.basename(src))
    inaczej:
        dir = os.path.dirname(dst)

    jeżeli update oraz nie newer(src, dst):
        jeżeli verbose >= 1:
            log.debug("not copying %s (output up-to-date)", src)
        zwróć (dst, 0)

    spróbuj:
        action = _copy_action[link]
    wyjąwszy KeyError:
        podnieś ValueError("invalid value '%s' dla 'link' argument" % link)

    jeżeli verbose >= 1:
        jeżeli os.path.basename(dst) == os.path.basename(src):
            log.info("%s %s -> %s", action, src, dir)
        inaczej:
            log.info("%s %s -> %s", action, src, dst)

    jeżeli dry_run:
        zwróć (dst, 1)

    # If linking (hard albo symbolic), use the appropriate system call
    # (Unix only, of course, but that's the caller's responsibility)
    albo_inaczej link == 'hard':
        jeżeli nie (os.path.exists(dst) oraz os.path.samefile(src, dst)):
            spróbuj:
                os.link(src, dst)
                zwróć (dst, 1)
            wyjąwszy OSError:
                # If hard linking fails, fall back on copying file
                # (some special filesystems don't support hard linking
                #  even under Unix, see issue #8876).
                dalej
    albo_inaczej link == 'sym':
        jeżeli nie (os.path.exists(dst) oraz os.path.samefile(src, dst)):
            os.symlink(src, dst)
            zwróć (dst, 1)

    # Otherwise (non-Mac, nie linking), copy the file contents oraz
    # (optionally) copy the times oraz mode.
    _copy_file_contents(src, dst)
    jeżeli preserve_mode albo preserve_times:
        st = os.stat(src)

        # According to David Ascher <da@ski.org>, utime() should be done
        # before chmod() (at least under NT).
        jeżeli preserve_times:
            os.utime(dst, (st[ST_ATIME], st[ST_MTIME]))
        jeżeli preserve_mode:
            os.chmod(dst, S_IMODE(st[ST_MODE]))

    zwróć (dst, 1)


# XXX I suspect this jest Unix-specific -- need porting help!
def move_file (src, dst,
               verbose=1,
               dry_run=0):

    """Move a file 'src' to 'dst'.  If 'dst' jest a directory, the file will
    be moved into it przy the same name; otherwise, 'src' jest just renamed
    to 'dst'.  Return the new full name of the file.

    Handles cross-device moves on Unix using 'copy_file()'.  What about
    other systems???
    """
    z os.path zaimportuj exists, isfile, isdir, basename, dirname
    zaimportuj errno

    jeżeli verbose >= 1:
        log.info("moving %s -> %s", src, dst)

    jeżeli dry_run:
        zwróć dst

    jeżeli nie isfile(src):
        podnieś DistutilsFileError("can't move '%s': nie a regular file" % src)

    jeżeli isdir(dst):
        dst = os.path.join(dst, basename(src))
    albo_inaczej exists(dst):
        podnieś DistutilsFileError(
              "can't move '%s': destination '%s' already exists" %
              (src, dst))

    jeżeli nie isdir(dirname(dst)):
        podnieś DistutilsFileError(
              "can't move '%s': destination '%s' nie a valid path" %
              (src, dst))

    copy_it = Nieprawda
    spróbuj:
        os.rename(src, dst)
    wyjąwszy OSError jako e:
        (num, msg) = e.args
        jeżeli num == errno.EXDEV:
            copy_it = Prawda
        inaczej:
            podnieś DistutilsFileError(
                  "couldn't move '%s' to '%s': %s" % (src, dst, msg))

    jeżeli copy_it:
        copy_file(src, dst, verbose=verbose)
        spróbuj:
            os.unlink(src)
        wyjąwszy OSError jako e:
            (num, msg) = e.args
            spróbuj:
                os.unlink(dst)
            wyjąwszy OSError:
                dalej
            podnieś DistutilsFileError(
                  "couldn't move '%s' to '%s' by copy/delete: "
                  "delete '%s' failed: %s"
                  % (src, dst, src, msg))
    zwróć dst


def write_file (filename, contents):
    """Create a file przy the specified name oraz write 'contents' (a
    sequence of strings without line terminators) to it.
    """
    f = open(filename, "w")
    spróbuj:
        dla line w contents:
            f.write(line + "\n")
    w_końcu:
        f.close()
