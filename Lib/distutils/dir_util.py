"""distutils.dir_util

Utility functions dla manipulating directories oraz directory trees."""

zaimportuj os
zaimportuj errno
z distutils.errors zaimportuj DistutilsFileError, DistutilsInternalError
z distutils zaimportuj log

# cache dla by mkpath() -- w addition to cheapening redundant calls,
# eliminates redundant "creating /foo/bar/baz" messages w dry-run mode
_path_created = {}

# I don't use os.makedirs because a) it's new to Python 1.5.2, oraz
# b) it blows up jeżeli the directory already exists (I want to silently
# succeed w that case).
def mkpath(name, mode=0o777, verbose=1, dry_run=0):
    """Create a directory oraz any missing ancestor directories.

    If the directory already exists (or jeżeli 'name' jest the empty string, which
    means the current directory, which of course exists), then do nothing.
    Raise DistutilsFileError jeżeli unable to create some directory along the way
    (eg. some sub-path exists, but jest a file rather than a directory).
    If 'verbose' jest true, print a one-line summary of each mkdir to stdout.
    Return the list of directories actually created.
    """

    global _path_created

    # Detect a common bug -- name jest Nic
    jeżeli nie isinstance(name, str):
        podnieś DistutilsInternalError(
              "mkpath: 'name' must be a string (got %r)" % (name,))

    # XXX what's the better way to handle verbosity? print jako we create
    # each directory w the path (the current behaviour), albo only announce
    # the creation of the whole path? (quite easy to do the latter since
    # we're nie using a recursive algorithm)

    name = os.path.normpath(name)
    created_dirs = []
    jeżeli os.path.isdir(name) albo name == '':
        zwróć created_dirs
    jeżeli _path_created.get(os.path.abspath(name)):
        zwróć created_dirs

    (head, tail) = os.path.split(name)
    tails = [tail]                      # stack of lone dirs to create

    dopóki head oraz tail oraz nie os.path.isdir(head):
        (head, tail) = os.path.split(head)
        tails.insert(0, tail)          # push next higher dir onto stack

    # now 'head' contains the deepest directory that already exists
    # (that is, the child of 'head' w 'name' jest the highest directory
    # that does *not* exist)
    dla d w tails:
        #print "head = %s, d = %s: " % (head, d),
        head = os.path.join(head, d)
        abs_head = os.path.abspath(head)

        jeżeli _path_created.get(abs_head):
            kontynuuj

        jeżeli verbose >= 1:
            log.info("creating %s", head)

        jeżeli nie dry_run:
            spróbuj:
                os.mkdir(head, mode)
            wyjąwszy OSError jako exc:
                jeżeli nie (exc.errno == errno.EEXIST oraz os.path.isdir(head)):
                    podnieś DistutilsFileError(
                          "could nie create '%s': %s" % (head, exc.args[-1]))
            created_dirs.append(head)

        _path_created[abs_head] = 1
    zwróć created_dirs

def create_tree(base_dir, files, mode=0o777, verbose=1, dry_run=0):
    """Create all the empty directories under 'base_dir' needed to put 'files'
    there.

    'base_dir' jest just the name of a directory which doesn't necessarily
    exist yet; 'files' jest a list of filenames to be interpreted relative to
    'base_dir'.  'base_dir' + the directory portion of every file w 'files'
    will be created jeżeli it doesn't already exist.  'mode', 'verbose' oraz
    'dry_run' flags are jako dla 'mkpath()'.
    """
    # First get the list of directories to create
    need_dir = set()
    dla file w files:
        need_dir.add(os.path.join(base_dir, os.path.dirname(file)))

    # Now create them
    dla dir w sorted(need_dir):
        mkpath(dir, mode, verbose=verbose, dry_run=dry_run)

def copy_tree(src, dst, preserve_mode=1, preserve_times=1,
              preserve_symlinks=0, update=0, verbose=1, dry_run=0):
    """Copy an entire directory tree 'src' to a new location 'dst'.

    Both 'src' oraz 'dst' must be directory names.  If 'src' jest nie a
    directory, podnieś DistutilsFileError.  If 'dst' does nie exist, it jest
    created przy 'mkpath()'.  The end result of the copy jest that every
    file w 'src' jest copied to 'dst', oraz directories under 'src' are
    recursively copied to 'dst'.  Return the list of files that were
    copied albo might have been copied, using their output name.  The
    zwróć value jest unaffected by 'update' albo 'dry_run': it jest simply
    the list of all files under 'src', przy the names changed to be
    under 'dst'.

    'preserve_mode' oraz 'preserve_times' are the same jako for
    'copy_file'; note that they only apply to regular files, nie to
    directories.  If 'preserve_symlinks' jest true, symlinks will be
    copied jako symlinks (on platforms that support them!); otherwise
    (the default), the destination of the symlink will be copied.
    'update' oraz 'verbose' are the same jako dla 'copy_file'.
    """
    z distutils.file_util zaimportuj copy_file

    jeżeli nie dry_run oraz nie os.path.isdir(src):
        podnieś DistutilsFileError(
              "cannot copy tree '%s': nie a directory" % src)
    spróbuj:
        names = os.listdir(src)
    wyjąwszy OSError jako e:
        jeżeli dry_run:
            names = []
        inaczej:
            podnieś DistutilsFileError(
                  "error listing files w '%s': %s" % (src, e.strerror))

    jeżeli nie dry_run:
        mkpath(dst, verbose=verbose)

    outputs = []

    dla n w names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        jeżeli n.startswith('.nfs'):
            # skip NFS rename files
            kontynuuj

        jeżeli preserve_symlinks oraz os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            jeżeli verbose >= 1:
                log.info("linking %s -> %s", dst_name, link_dest)
            jeżeli nie dry_run:
                os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        albo_inaczej os.path.isdir(src_name):
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode,
                          preserve_times, preserve_symlinks, update,
                          verbose=verbose, dry_run=dry_run))
        inaczej:
            copy_file(src_name, dst_name, preserve_mode,
                      preserve_times, update, verbose=verbose,
                      dry_run=dry_run)
            outputs.append(dst_name)

    zwróć outputs

def _build_cmdtuple(path, cmdtuples):
    """Helper dla remove_tree()."""
    dla f w os.listdir(path):
        real_f = os.path.join(path,f)
        jeżeli os.path.isdir(real_f) oraz nie os.path.islink(real_f):
            _build_cmdtuple(real_f, cmdtuples)
        inaczej:
            cmdtuples.append((os.remove, real_f))
    cmdtuples.append((os.rmdir, path))

def remove_tree(directory, verbose=1, dry_run=0):
    """Recursively remove an entire directory tree.

    Any errors are ignored (apart z being reported to stdout jeżeli 'verbose'
    jest true).
    """
    global _path_created

    jeżeli verbose >= 1:
        log.info("removing '%s' (and everything under it)", directory)
    jeżeli dry_run:
        zwróć
    cmdtuples = []
    _build_cmdtuple(directory, cmdtuples)
    dla cmd w cmdtuples:
        spróbuj:
            cmd[0](cmd[1])
            # remove dir z cache jeżeli it's already there
            abspath = os.path.abspath(cmd[1])
            jeżeli abspath w _path_created:
                usuń _path_created[abspath]
        wyjąwszy OSError jako exc:
            log.warn("error removing %s: %s", directory, exc)

def ensure_relative(path):
    """Take the full path 'path', oraz make it a relative path.

    This jest useful to make 'path' the second argument to os.path.join().
    """
    drive, path = os.path.splitdrive(path)
    jeżeli path[0:1] == os.sep:
        path = drive + path[1:]
    zwróć path
