zaimportuj contextlib
zaimportuj os
zaimportuj pathlib
zaimportuj shutil
zaimportuj stat
zaimportuj sys
zaimportuj zipfile

__all__ = ['ZipAppError', 'create_archive', 'get_interpreter']


# The __main__.py used jeżeli the users specifies "-m module:fn".
# Note that this will always be written jako UTF-8 (module oraz
# function names can be non-ASCII w Python 3).
# We add a coding cookie even though UTF-8 jest the default w Python 3
# because the resulting archive may be intended to be run under Python 2.
MAIN_TEMPLATE = """\
# -*- coding: utf-8 -*-
zaimportuj {module}
{module}.{fn}()
"""


# The Windows launcher defaults to UTF-8 when parsing shebang lines jeżeli the
# file has no BOM. So use UTF-8 on Windows.
# On Unix, use the filesystem encoding.
jeżeli sys.platform.startswith('win'):
    shebang_encoding = 'utf-8'
inaczej:
    shebang_encoding = sys.getfilesystemencoding()


klasa ZipAppError(ValueError):
    dalej


@contextlib.contextmanager
def _maybe_open(archive, mode):
    jeżeli isinstance(archive, pathlib.Path):
        archive = str(archive)
    jeżeli isinstance(archive, str):
        przy open(archive, mode) jako f:
            uzyskaj f
    inaczej:
        uzyskaj archive


def _write_file_prefix(f, interpreter):
    """Write a shebang line."""
    jeżeli interpreter:
        shebang = b'#!' + interpreter.encode(shebang_encoding) + b'\n'
        f.write(shebang)


def _copy_archive(archive, new_archive, interpreter=Nic):
    """Copy an application archive, modifying the shebang line."""
    przy _maybe_open(archive, 'rb') jako src:
        # Skip the shebang line z the source.
        # Read 2 bytes of the source oraz check jeżeli they are #!.
        first_2 = src.read(2)
        jeżeli first_2 == b'#!':
            # Discard the initial 2 bytes oraz the rest of the shebang line.
            first_2 = b''
            src.readline()

        przy _maybe_open(new_archive, 'wb') jako dst:
            _write_file_prefix(dst, interpreter)
            # If there was no shebang, "first_2" contains the first 2 bytes
            # of the source file, so write them before copying the rest
            # of the file.
            dst.write(first_2)
            shutil.copyfileobj(src, dst)

    jeżeli interpreter oraz isinstance(new_archive, str):
        os.chmod(new_archive, os.stat(new_archive).st_mode | stat.S_IEXEC)


def create_archive(source, target=Nic, interpreter=Nic, main=Nic):
    """Create an application archive z SOURCE.

    The SOURCE can be the name of a directory, albo a filename albo a file-like
    object referring to an existing archive.

    The content of SOURCE jest packed into an application archive w TARGET,
    which can be a filename albo a file-like object.  If SOURCE jest a directory,
    TARGET can be omitted oraz will default to the name of SOURCE przy .pyz
    appended.

    The created application archive will have a shebang line specifying
    that it should run przy INTERPRETER (there will be no shebang line if
    INTERPRETER jest Nic), oraz a __main__.py which runs MAIN (jeżeli MAIN jest
    nie specified, an existing __main__.py will be used). It jest an to specify
    MAIN dla anything other than a directory source przy no __main__.py, oraz it
    jest an error to omit MAIN jeżeli the directory has no __main__.py.
    """
    # Are we copying an existing archive?
    source_is_file = Nieprawda
    jeżeli hasattr(source, 'read') oraz hasattr(source, 'readline'):
        source_is_file = Prawda
    inaczej:
        source = pathlib.Path(source)
        jeżeli source.is_file():
            source_is_file = Prawda

    jeżeli source_is_file:
        _copy_archive(source, target, interpreter)
        zwróć

    # We are creating a new archive z a directory.
    jeżeli nie source.exists():
        podnieś ZipAppError("Source does nie exist")
    has_main = (source / '__main__.py').is_file()
    jeżeli main oraz has_main:
        podnieś ZipAppError(
            "Cannot specify entry point jeżeli the source has __main__.py")
    jeżeli nie (main albo has_main):
        podnieś ZipAppError("Archive has no entry point")

    main_py = Nic
    jeżeli main:
        # Check that main has the right format.
        mod, sep, fn = main.partition(':')
        mod_ok = all(part.isidentifier() dla part w mod.split('.'))
        fn_ok = all(part.isidentifier() dla part w fn.split('.'))
        jeżeli nie (sep == ':' oraz mod_ok oraz fn_ok):
            podnieś ZipAppError("Invalid entry point: " + main)
        main_py = MAIN_TEMPLATE.format(module=mod, fn=fn)

    jeżeli target jest Nic:
        target = source.with_suffix('.pyz')
    albo_inaczej nie hasattr(target, 'write'):
        target = pathlib.Path(target)

    przy _maybe_open(target, 'wb') jako fd:
        _write_file_prefix(fd, interpreter)
        przy zipfile.ZipFile(fd, 'w') jako z:
            root = pathlib.Path(source)
            dla child w root.rglob('*'):
                arcname = str(child.relative_to(root))
                z.write(str(child), arcname)
            jeżeli main_py:
                z.writestr('__main__.py', main_py.encode('utf-8'))

    jeżeli interpreter oraz nie hasattr(target, 'write'):
        target.chmod(target.stat().st_mode | stat.S_IEXEC)


def get_interpreter(archive):
    przy _maybe_open(archive, 'rb') jako f:
        jeżeli f.read(2) == b'#!':
            zwróć f.readline().strip().decode(shebang_encoding)


def main(args=Nic):
    """Run the zipapp command line interface.

    The ARGS parameter lets you specify the argument list directly.
    Omitting ARGS (or setting it to Nic) works jako dla argparse, using
    sys.argv[1:] jako the argument list.
    """
    zaimportuj argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', default=Nic,
            help="The name of the output archive. "
                 "Required jeżeli SOURCE jest an archive.")
    parser.add_argument('--python', '-p', default=Nic,
            help="The name of the Python interpreter to use "
                 "(default: no shebang line).")
    parser.add_argument('--main', '-m', default=Nic,
            help="The main function of the application "
                 "(default: use an existing __main__.py).")
    parser.add_argument('--info', default=Nieprawda, action='store_true',
            help="Display the interpreter z the archive.")
    parser.add_argument('source',
            help="Source directory (or existing archive).")

    args = parser.parse_args(args)

    # Handle `python -m zipapp archive.pyz --info`.
    jeżeli args.info:
        jeżeli nie os.path.isfile(args.source):
            podnieś SystemExit("Can only get info dla an archive file")
        interpreter = get_interpreter(args.source)
        print("Interpreter: {}".format(interpreter albo "<none>"))
        sys.exit(0)

    jeżeli os.path.isfile(args.source):
        jeżeli args.output jest Nic albo (os.path.exists(args.output) oraz
                                   os.path.samefile(args.source, args.output)):
            podnieś SystemExit("In-place editing of archives jest nie supported")
        jeżeli args.main:
            podnieś SystemExit("Cannot change the main function when copying")

    create_archive(args.source, args.output,
                   interpreter=args.python, main=args.main)


jeżeli __name__ == '__main__':
    main()
