"""Module/script to byte-compile all .py files to .pyc files.

When called jako a script przy arguments, this compiles the directories
given jako arguments recursively; the -l option prevents it from
recursing into directories.

Without arguments, jeżeli compiles all modules on sys.path, without
recursing into subdirectories.  (Even though it should do so for
packages -- dla now, you'll have to deal przy packages separately.)

See module py_compile dla details of the actual byte-compilation.
"""
zaimportuj os
zaimportuj sys
zaimportuj importlib.util
zaimportuj py_compile
zaimportuj struct

spróbuj:
    z concurrent.futures zaimportuj ProcessPoolExecutor
wyjąwszy ImportError:
    ProcessPoolExecutor = Nic
z functools zaimportuj partial

__all__ = ["compile_dir","compile_file","compile_path"]

def _walk_dir(dir, ddir=Nic, maxlevels=10, quiet=0):
    jeżeli nie quiet:
        print('Listing {!r}...'.format(dir))
    spróbuj:
        names = os.listdir(dir)
    wyjąwszy OSError:
        jeżeli quiet < 2:
            print("Can't list {!r}".format(dir))
        names = []
    names.sort()
    dla name w names:
        jeżeli name == '__pycache__':
            kontynuuj
        fullname = os.path.join(dir, name)
        jeżeli ddir jest nie Nic:
            dfile = os.path.join(ddir, name)
        inaczej:
            dfile = Nic
        jeżeli nie os.path.isdir(fullname):
            uzyskaj fullname
        albo_inaczej (maxlevels > 0 oraz name != os.curdir oraz name != os.pardir oraz
              os.path.isdir(fullname) oraz nie os.path.islink(fullname)):
            uzyskaj z _walk_dir(fullname, ddir=dfile,
                                 maxlevels=maxlevels - 1, quiet=quiet)

def compile_dir(dir, maxlevels=10, ddir=Nic, force=Nieprawda, rx=Nic,
                quiet=0, legacy=Nieprawda, optimize=-1, workers=1):
    """Byte-compile all modules w the given directory tree.

    Arguments (only dir jest required):

    dir:       the directory to byte-compile
    maxlevels: maximum recursion level (default 10)
    ddir:      the directory that will be prepended to the path to the
               file jako it jest compiled into each byte-code file.
    force:     jeżeli Prawda, force compilation, even jeżeli timestamps are up-to-date
    quiet:     full output przy Nieprawda albo 0, errors only przy 1,
               no output przy 2
    legacy:    jeżeli Prawda, produce legacy pyc paths instead of PEP 3147 paths
    optimize:  optimization level albo -1 dla level of the interpreter
    workers:   maximum number of parallel workers
    """
    files = _walk_dir(dir, quiet=quiet, maxlevels=maxlevels,
                      ddir=ddir)
    success = 1
    jeżeli workers jest nie Nic oraz workers != 1 oraz ProcessPoolExecutor jest nie Nic:
        jeżeli workers < 0:
            podnieś ValueError('workers must be greater albo equal to 0')

        workers = workers albo Nic
        przy ProcessPoolExecutor(max_workers=workers) jako executor:
            results = executor.map(partial(compile_file,
                                           ddir=ddir, force=force,
                                           rx=rx, quiet=quiet,
                                           legacy=legacy,
                                           optimize=optimize),
                                   files)
            success = min(results, default=1)
    inaczej:
        dla file w files:
            jeżeli nie compile_file(file, ddir, force, rx, quiet,
                                legacy, optimize):
                success = 0
    zwróć success

def compile_file(fullname, ddir=Nic, force=Nieprawda, rx=Nic, quiet=0,
                 legacy=Nieprawda, optimize=-1):
    """Byte-compile one file.

    Arguments (only fullname jest required):

    fullname:  the file to byte-compile
    ddir:      jeżeli given, the directory name compiled w to the
               byte-code file.
    force:     jeżeli Prawda, force compilation, even jeżeli timestamps are up-to-date
    quiet:     full output przy Nieprawda albo 0, errors only przy 1,
               no output przy 2
    legacy:    jeżeli Prawda, produce legacy pyc paths instead of PEP 3147 paths
    optimize:  optimization level albo -1 dla level of the interpreter
    """
    success = 1
    name = os.path.basename(fullname)
    jeżeli ddir jest nie Nic:
        dfile = os.path.join(ddir, name)
    inaczej:
        dfile = Nic
    jeżeli rx jest nie Nic:
        mo = rx.search(fullname)
        jeżeli mo:
            zwróć success
    jeżeli os.path.isfile(fullname):
        jeżeli legacy:
            cfile = fullname + 'c'
        inaczej:
            jeżeli optimize >= 0:
                opt = optimize jeżeli optimize >= 1 inaczej ''
                cfile = importlib.util.cache_from_source(
                                fullname, optimization=opt)
            inaczej:
                cfile = importlib.util.cache_from_source(fullname)
            cache_dir = os.path.dirname(cfile)
        head, tail = name[:-3], name[-3:]
        jeżeli tail == '.py':
            jeżeli nie force:
                spróbuj:
                    mtime = int(os.stat(fullname).st_mtime)
                    expect = struct.pack('<4sl', importlib.util.MAGIC_NUMBER,
                                         mtime)
                    przy open(cfile, 'rb') jako chandle:
                        actual = chandle.read(8)
                    jeżeli expect == actual:
                        zwróć success
                wyjąwszy OSError:
                    dalej
            jeżeli nie quiet:
                print('Compiling {!r}...'.format(fullname))
            spróbuj:
                ok = py_compile.compile(fullname, cfile, dfile, Prawda,
                                        optimize=optimize)
            wyjąwszy py_compile.PyCompileError jako err:
                success = 0
                jeżeli quiet >= 2:
                    zwróć success
                albo_inaczej quiet:
                    print('*** Error compiling {!r}...'.format(fullname))
                inaczej:
                    print('*** ', end='')
                # escape non-printable characters w msg
                msg = err.msg.encode(sys.stdout.encoding,
                                     errors='backslashreplace')
                msg = msg.decode(sys.stdout.encoding)
                print(msg)
            wyjąwszy (SyntaxError, UnicodeError, OSError) jako e:
                success = 0
                jeżeli quiet >= 2:
                    zwróć success
                albo_inaczej quiet:
                    print('*** Error compiling {!r}...'.format(fullname))
                inaczej:
                    print('*** ', end='')
                print(e.__class__.__name__ + ':', e)
            inaczej:
                jeżeli ok == 0:
                    success = 0
    zwróć success

def compile_path(skip_curdir=1, maxlevels=0, force=Nieprawda, quiet=0,
                 legacy=Nieprawda, optimize=-1):
    """Byte-compile all module on sys.path.

    Arguments (all optional):

    skip_curdir: jeżeli true, skip current directory (default Prawda)
    maxlevels:   max recursion level (default 0)
    force: jako dla compile_dir() (default Nieprawda)
    quiet: jako dla compile_dir() (default 0)
    legacy: jako dla compile_dir() (default Nieprawda)
    optimize: jako dla compile_dir() (default -1)
    """
    success = 1
    dla dir w sys.path:
        jeżeli (nie dir albo dir == os.curdir) oraz skip_curdir:
            jeżeli quiet < 2:
                print('Skipping current directory')
        inaczej:
            success = success oraz compile_dir(dir, maxlevels, Nic,
                                              force, quiet=quiet,
                                              legacy=legacy, optimize=optimize)
    zwróć success


def main():
    """Script main program."""
    zaimportuj argparse

    parser = argparse.ArgumentParser(
        description='Utilities to support installing Python libraries.')
    parser.add_argument('-l', action='store_const', const=0,
                        default=10, dest='maxlevels',
                        help="don't recurse into subdirectories")
    parser.add_argument('-r', type=int, dest='recursion',
                        help=('control the maximum recursion level. '
                              'jeżeli `-l` oraz `-r` options are specified, '
                              'then `-r` takes precedence.'))
    parser.add_argument('-f', action='store_true', dest='force',
                        help='force rebuild even jeżeli timestamps are up to date')
    parser.add_argument('-q', action='count', dest='quiet', default=0,
                        help='output only error messages; -qq will suppress '
                             'the error messages jako well.')
    parser.add_argument('-b', action='store_true', dest='legacy',
                        help='use legacy (pre-PEP3147) compiled file locations')
    parser.add_argument('-d', metavar='DESTDIR',  dest='ddir', default=Nic,
                        help=('directory to prepend to file paths dla use w '
                              'compile-time tracebacks oraz w runtime '
                              'tracebacks w cases where the source file jest '
                              'unavailable'))
    parser.add_argument('-x', metavar='REGEXP', dest='rx', default=Nic,
                        help=('skip files matching the regular expression; '
                              'the regexp jest searched dla w the full path '
                              'of each file considered dla compilation'))
    parser.add_argument('-i', metavar='FILE', dest='flist',
                        help=('add all the files oraz directories listed w '
                              'FILE to the list considered dla compilation; '
                              'jeżeli "-", names are read z stdin'))
    parser.add_argument('compile_dest', metavar='FILE|DIR', nargs='*',
                        help=('zero albo more file oraz directory names '
                              'to compile; jeżeli no arguments given, defaults '
                              'to the equivalent of -l sys.path'))
    parser.add_argument('-j', '--workers', default=1,
                        type=int, help='Run compileall concurrently')

    args = parser.parse_args()
    compile_dests = args.compile_dest

    jeżeli (args.ddir oraz (len(compile_dests) != 1
            albo nie os.path.isdir(compile_dests[0]))):
        parser.exit('-d destdir requires exactly one directory argument')
    jeżeli args.rx:
        zaimportuj re
        args.rx = re.compile(args.rx)


    jeżeli args.recursion jest nie Nic:
        maxlevels = args.recursion
    inaczej:
        maxlevels = args.maxlevels

    # jeżeli flist jest provided then load it
    jeżeli args.flist:
        spróbuj:
            przy (sys.stdin jeżeli args.flist=='-' inaczej open(args.flist)) jako f:
                dla line w f:
                    compile_dests.append(line.strip())
        wyjąwszy OSError:
            jeżeli args.quiet < 2:
                print("Error reading file list {}".format(args.flist))
            zwróć Nieprawda

    jeżeli args.workers jest nie Nic:
        args.workers = args.workers albo Nic

    success = Prawda
    spróbuj:
        jeżeli compile_dests:
            dla dest w compile_dests:
                jeżeli os.path.isfile(dest):
                    jeżeli nie compile_file(dest, args.ddir, args.force, args.rx,
                                        args.quiet, args.legacy):
                        success = Nieprawda
                inaczej:
                    jeżeli nie compile_dir(dest, maxlevels, args.ddir,
                                       args.force, args.rx, args.quiet,
                                       args.legacy, workers=args.workers):
                        success = Nieprawda
            zwróć success
        inaczej:
            zwróć compile_path(legacy=args.legacy, force=args.force,
                                quiet=args.quiet)
    wyjąwszy KeyboardInterrupt:
        jeżeli args.quiet < 2:
            print("\n[interrupted]")
        zwróć Nieprawda
    zwróć Prawda


jeżeli __name__ == '__main__':
    exit_status = int(nie main())
    sys.exit(exit_status)
