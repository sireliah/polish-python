"""distutils.archive_util

Utility functions dla creating archive files (tarballs, zip files,
that sort of thing)."""

zaimportuj os
z warnings zaimportuj warn
zaimportuj sys

spróbuj:
    zaimportuj zipfile
wyjąwszy ImportError:
    zipfile = Nic


z distutils.errors zaimportuj DistutilsExecError
z distutils.spawn zaimportuj spawn
z distutils.dir_util zaimportuj mkpath
z distutils zaimportuj log

spróbuj:
    z pwd zaimportuj getpwnam
wyjąwszy ImportError:
    getpwnam = Nic

spróbuj:
    z grp zaimportuj getgrnam
wyjąwszy ImportError:
    getgrnam = Nic

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

def make_tarball(base_name, base_dir, compress="gzip", verbose=0, dry_run=0,
                 owner=Nic, group=Nic):
    """Create a (possibly compressed) tar file z all the files under
    'base_dir'.

    'compress' must be "gzip" (the default), "bzip2", "xz", "compress", albo
    Nic.  ("compress" will be deprecated w Python 3.2)

    'owner' oraz 'group' can be used to define an owner oraz a group dla the
    archive that jest being built. If nie provided, the current owner oraz group
    will be used.

    The output tar file will be named 'base_dir' +  ".tar", possibly plus
    the appropriate compression extension (".gz", ".bz2", ".xz" albo ".Z").

    Returns the output filename.
    """
    tar_compression = {'gzip': 'gz', 'bzip2': 'bz2', 'xz': 'xz', Nic: '',
                       'compress': ''}
    compress_ext = {'gzip': '.gz', 'bzip2': '.bz2', 'xz': '.xz',
                    'compress': '.Z'}

    # flags dla compression program, each element of list will be an argument
    jeżeli compress jest nie Nic oraz compress nie w compress_ext.keys():
        podnieś ValueError(
              "bad value dla 'compress': must be Nic, 'gzip', 'bzip2', "
              "'xz' albo 'compress'")

    archive_name = base_name + '.tar'
    jeżeli compress != 'compress':
        archive_name += compress_ext.get(compress, '')

    mkpath(os.path.dirname(archive_name), dry_run=dry_run)

    # creating the tarball
    zaimportuj tarfile  # late zaimportuj so Python build itself doesn't przerwij

    log.info('Creating tar archive')

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

    # compression using `compress`
    jeżeli compress == 'compress':
        warn("'compress' will be deprecated.", PendingDeprecationWarning)
        # the option varies depending on the platform
        compressed_name = archive_name + compress_ext[compress]
        jeżeli sys.platform == 'win32':
            cmd = [compress, archive_name, compressed_name]
        inaczej:
            cmd = [compress, '-f', archive_name]
        spawn(cmd, dry_run=dry_run)
        zwróć compressed_name

    zwróć archive_name

def make_zipfile(base_name, base_dir, verbose=0, dry_run=0):
    """Create a zip file z all the files under 'base_dir'.

    The output zip file will be named 'base_name' + ".zip".  Uses either the
    "zipfile" Python module (jeżeli available) albo the InfoZIP "zip" utility
    (jeżeli installed oraz found on the default search path).  If neither tool jest
    available, podnieśs DistutilsExecError.  Returns the name of the output zip
    file.
    """
    zip_filename = base_name + ".zip"
    mkpath(os.path.dirname(zip_filename), dry_run=dry_run)

    # If zipfile module jest nie available, try spawning an external
    # 'zip' command.
    jeżeli zipfile jest Nic:
        jeżeli verbose:
            zipoptions = "-r"
        inaczej:
            zipoptions = "-rq"

        spróbuj:
            spawn(["zip", zipoptions, zip_filename, base_dir],
                  dry_run=dry_run)
        wyjąwszy DistutilsExecError:
            # XXX really should distinguish between "couldn't find
            # external 'zip' command" oraz "zip failed".
            podnieś DistutilsExecError(("unable to create zip file '%s': "
                   "could neither zaimportuj the 'zipfile' module nor "
                   "find a standalone zip utility") % zip_filename)

    inaczej:
        log.info("creating '%s' oraz adding '%s' to it",
                 zip_filename, base_dir)

        jeżeli nie dry_run:
            spróbuj:
                zip = zipfile.ZipFile(zip_filename, "w",
                                      compression=zipfile.ZIP_DEFLATED)
            wyjąwszy RuntimeError:
                zip = zipfile.ZipFile(zip_filename, "w",
                                      compression=zipfile.ZIP_STORED)

            dla dirpath, dirnames, filenames w os.walk(base_dir):
                dla name w filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    jeżeli os.path.isfile(path):
                        zip.write(path, path)
                        log.info("adding '%s'" % path)
            zip.close()

    zwróć zip_filename

ARCHIVE_FORMATS = {
    'gztar': (make_tarball, [('compress', 'gzip')], "gzip'ed tar-file"),
    'bztar': (make_tarball, [('compress', 'bzip2')], "bzip2'ed tar-file"),
    'xztar': (make_tarball, [('compress', 'xz')], "xz'ed tar-file"),
    'ztar':  (make_tarball, [('compress', 'compress')], "compressed tar file"),
    'tar':   (make_tarball, [('compress', Nic)], "uncompressed tar file"),
    'zip':   (make_zipfile, [],"ZIP file")
    }

def check_archive_formats(formats):
    """Returns the first format z the 'format' list that jest unknown.

    If all formats are known, returns Nic
    """
    dla format w formats:
        jeżeli format nie w ARCHIVE_FORMATS:
            zwróć format
    zwróć Nic

def make_archive(base_name, format, root_dir=Nic, base_dir=Nic, verbose=0,
                 dry_run=0, owner=Nic, group=Nic):
    """Create an archive file (eg. zip albo tar).

    'base_name' jest the name of the file to create, minus any format-specific
    extension; 'format' jest the archive format: one of "zip", "tar", "gztar",
    "bztar", "xztar", albo "ztar".

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
        log.debug("changing into '%s'", root_dir)
        base_name = os.path.abspath(base_name)
        jeżeli nie dry_run:
            os.chdir(root_dir)

    jeżeli base_dir jest Nic:
        base_dir = os.curdir

    kwargs = {'dry_run': dry_run}

    spróbuj:
        format_info = ARCHIVE_FORMATS[format]
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
            log.debug("changing back to '%s'", save_cwd)
            os.chdir(save_cwd)

    zwróć filename
