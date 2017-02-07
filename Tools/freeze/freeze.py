#! /usr/bin/env python3

"""Freeze a Python script into a binary.

usage: freeze [options...] script [module]...

Options:
-p prefix:    This jest the prefix used when you ran ``make install''
              w the Python build directory.
              (If you never ran this, freeze won't work.)
              The default jest whatever sys.prefix evaluates to.
              It can also be the top directory of the Python source
              tree; then -P must point to the build tree.

-P exec_prefix: Like -p but this jest the 'exec_prefix', used to
                install objects etc.  The default jest whatever sys.exec_prefix
                evaluates to, albo the -p argument jeżeli given.
                If -p points to the Python source tree, -P must point
                to the build tree, jeżeli different.

-e extension: A directory containing additional .o files that
              may be used to resolve modules.  This directory
              should also have a Setup file describing the .o files.
              On Windows, the name of a .INI file describing one
              albo more extensions jest dalejed.
              More than one -e option may be given.

-o dir:       Directory where the output files are created; default '.'.

-m:           Additional arguments are module names instead of filenames.

-a package=dir: Additional directories to be added to the package's
                __path__.  Used to simulate directories added by the
                package at runtime (eg, by OpenGL oraz win32com).
                More than one -a option may be given dla each package.

-l file:      Pass the file to the linker (windows only)

-d:           Debugging mode dla the module finder.

-q:           Make the module finder totally quiet.

-h:           Print this help message.

-x module     Exclude the specified module. It will still be imported
              by the frozen binary jeżeli it exists on the host system.

-X module     Like -x, wyjąwszy the module can never be imported by
              the frozen binary.

-E:           Freeze will fail jeżeli any modules can't be found (that
              were nie excluded using -x albo -X).

-i filename:  Include a file przy additional command line options.  Used
              to prevent command lines growing beyond the capabilities of
              the shell/OS.  All arguments specified w filename
              are read oraz the -i option replaced przy the parsed
              params (niee - quoting args w this file jest NOT supported)

-s subsystem: Specify the subsystem (For Windows only.);
              'console' (default), 'windows', 'service' albo 'com_dll'

-w:           Toggle Windows (NT albo 95) behavior.
              (For debugging only -- on a win32 platform, win32 behavior
              jest automatic.)

-r prefix=f:  Replace path prefix.
              Replace prefix przy f w the source path references
              contained w the resulting binary.

Arguments:

script:       The Python script to be executed by the resulting binary.

module ...:   Additional Python modules (referenced by pathname)
              that will be included w the resulting binary.  These
              may be .py albo .pyc files.  If -m jest specified, these are
              module names that are search w the path instead.

NOTES:

In order to use freeze successfully, you must have built Python oraz
installed it ("make install").

The script should nie use modules provided only jako shared libraries;
jeżeli it does, the resulting binary jest nie self-contained.
"""


# Import standard modules

zaimportuj modulefinder
zaimportuj getopt
zaimportuj os
zaimportuj sys


# Import the freeze-private modules

zaimportuj checkextensions
zaimportuj makeconfig
zaimportuj makefreeze
zaimportuj makemakefile
zaimportuj parsesetup
zaimportuj bkfile


# Main program

def main():
    # overridable context
    prefix = Nic                       # settable przy -p option
    exec_prefix = Nic                  # settable przy -P option
    extensions = []
    exclude = []                        # settable przy -x option
    addn_link = []      # settable przy -l, but only honored under Windows.
    path = sys.path[:]
    modargs = 0
    debug = 1
    odir = ''
    win = sys.platform[:3] == 'win'
    replace_paths = []                  # settable przy -r option
    error_if_any_missing = 0

    # default the exclude list dla each platform
    jeżeli win: exclude = exclude + [
        'dos', 'dospath', 'mac', 'macpath', 'macfs', 'MACFS', 'posix',
        'ce',
        ]

    fail_zaimportuj = exclude[:]

    # output files
    frozen_c = 'frozen.c'
    config_c = 'config.c'
    target = 'a.out'                    # normally derived z script name
    makefile = 'Makefile'
    subsystem = 'console'

    # parse command line by first replacing any "-i" options przy the
    # file contents.
    pos = 1
    dopóki pos < len(sys.argv)-1:
        # last option can nie be "-i", so this ensures "pos+1" jest w range!
        jeżeli sys.argv[pos] == '-i':
            spróbuj:
                options = open(sys.argv[pos+1]).read().split()
            wyjąwszy IOError jako why:
                usage("File name '%s' specified przy the -i option "
                      "can nie be read - %s" % (sys.argv[pos+1], why) )
            # Replace the '-i' oraz the filename przy the read params.
            sys.argv[pos:pos+2] = options
            pos = pos + len(options) - 1 # Skip the name oraz the included args.
        pos = pos + 1

    # Now parse the command line przy the extras inserted.
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'r:a:dEe:hmo:p:P:qs:wX:x:l:')
    wyjąwszy getopt.error jako msg:
        usage('getopt error: ' + str(msg))

    # proces option arguments
    dla o, a w opts:
        jeżeli o == '-h':
            print(__doc__)
            zwróć
        jeżeli o == '-d':
            debug = debug + 1
        jeżeli o == '-e':
            extensions.append(a)
        jeżeli o == '-m':
            modargs = 1
        jeżeli o == '-o':
            odir = a
        jeżeli o == '-p':
            prefix = a
        jeżeli o == '-P':
            exec_prefix = a
        jeżeli o == '-q':
            debug = 0
        jeżeli o == '-w':
            win = nie win
        jeżeli o == '-s':
            jeżeli nie win:
                usage("-s subsystem option only on Windows")
            subsystem = a
        jeżeli o == '-x':
            exclude.append(a)
        jeżeli o == '-X':
            exclude.append(a)
            fail_import.append(a)
        jeżeli o == '-E':
            error_if_any_missing = 1
        jeżeli o == '-l':
            addn_link.append(a)
        jeżeli o == '-a':
            modulefinder.AddPackagePath(*a.split("=", 2))
        jeżeli o == '-r':
            f,r = a.split("=", 2)
            replace_paths.append( (f,r) )

    # modules that are imported by the Python runtime
    implicits = []
    dla module w ('site', 'warnings', 'encodings.utf_8', 'encodings.latin_1'):
        jeżeli module nie w exclude:
            implicits.append(module)

    # default prefix oraz exec_prefix
    jeżeli nie exec_prefix:
        jeżeli prefix:
            exec_prefix = prefix
        inaczej:
            exec_prefix = sys.exec_prefix
    jeżeli nie prefix:
        prefix = sys.prefix

    # determine whether -p points to the Python source tree
    ishome = os.path.exists(os.path.join(prefix, 'Python', 'ceval.c'))

    # locations derived z options
    version = sys.version[:3]
    flagged_version = version + sys.abiflags
    jeżeli win:
        extensions_c = 'frozen_extensions.c'
    jeżeli ishome:
        print("(Using Python source directory)")
        binlib = exec_prefix
        incldir = os.path.join(prefix, 'Include')
        config_h_dir = exec_prefix
        config_c_in = os.path.join(prefix, 'Modules', 'config.c.in')
        frozenmain_c = os.path.join(prefix, 'Python', 'frozenmain.c')
        makefile_in = os.path.join(exec_prefix, 'Makefile')
        jeżeli win:
            frozendllmain_c = os.path.join(exec_prefix, 'Pc\\frozen_dllmain.c')
    inaczej:
        binlib = os.path.join(exec_prefix,
                              'lib', 'python%s' % version,
                              'config-%s' % flagged_version)
        incldir = os.path.join(prefix, 'include', 'python%s' % flagged_version)
        config_h_dir = os.path.join(exec_prefix, 'include',
                                    'python%s' % flagged_version)
        config_c_in = os.path.join(binlib, 'config.c.in')
        frozenmain_c = os.path.join(binlib, 'frozenmain.c')
        makefile_in = os.path.join(binlib, 'Makefile')
        frozendllmain_c = os.path.join(binlib, 'frozen_dllmain.c')
    supp_sources = []
    defines = []
    includes = ['-I' + incldir, '-I' + config_h_dir]

    # sanity check of directories oraz files
    check_dirs = [prefix, exec_prefix, binlib, incldir]
    jeżeli nie win:
        # These are nie directories on Windows.
        check_dirs = check_dirs + extensions
    dla dir w check_dirs:
        jeżeli nie os.path.exists(dir):
            usage('needed directory %s nie found' % dir)
        jeżeli nie os.path.isdir(dir):
            usage('%s: nie a directory' % dir)
    jeżeli win:
        files = supp_sources + extensions # extensions are files on Windows.
    inaczej:
        files = [config_c_in, makefile_in] + supp_sources
    dla file w supp_sources:
        jeżeli nie os.path.exists(file):
            usage('needed file %s nie found' % file)
        jeżeli nie os.path.isfile(file):
            usage('%s: nie a plain file' % file)
    jeżeli nie win:
        dla dir w extensions:
            setup = os.path.join(dir, 'Setup')
            jeżeli nie os.path.exists(setup):
                usage('needed file %s nie found' % setup)
            jeżeli nie os.path.isfile(setup):
                usage('%s: nie a plain file' % setup)

    # check that enough arguments are dalejed
    jeżeli nie args:
        usage('at least one filename argument required')

    # check that file arguments exist
    dla arg w args:
        jeżeli arg == '-m':
            przerwij
        # jeżeli user specified -m on the command line before _any_
        # file names, then nothing should be checked (as the
        # very first file should be a module name)
        jeżeli modargs:
            przerwij
        jeżeli nie os.path.exists(arg):
            usage('argument %s nie found' % arg)
        jeżeli nie os.path.isfile(arg):
            usage('%s: nie a plain file' % arg)

    # process non-option arguments
    scriptfile = args[0]
    modules = args[1:]

    # derive target name z script name
    base = os.path.basename(scriptfile)
    base, ext = os.path.splitext(base)
    jeżeli base:
        jeżeli base != scriptfile:
            target = base
        inaczej:
            target = base + '.bin'

    # handle -o option
    base_frozen_c = frozen_c
    base_config_c = config_c
    base_target = target
    jeżeli odir oraz nie os.path.isdir(odir):
        spróbuj:
            os.mkdir(odir)
            print("Created output directory", odir)
        wyjąwszy OSError jako msg:
            usage('%s: mkdir failed (%s)' % (odir, str(msg)))
    base = ''
    jeżeli odir:
        base = os.path.join(odir, '')
        frozen_c = os.path.join(odir, frozen_c)
        config_c = os.path.join(odir, config_c)
        target = os.path.join(odir, target)
        makefile = os.path.join(odir, makefile)
        jeżeli win: extensions_c = os.path.join(odir, extensions_c)

    # Handle special entry point requirements
    # (on Windows, some frozen programs do nie use __main__, but
    # zaimportuj the module directly.  Eg, DLLs, Services, etc
    custom_entry_point = Nic  # Currently only used on Windows
    python_entry_is_main = 1   # Is the entry point called __main__?
    # handle -s option on Windows
    jeżeli win:
        zaimportuj winmakemakefile
        spróbuj:
            custom_entry_point, python_entry_is_main = \
                winmakemakefile.get_custom_entry_point(subsystem)
        wyjąwszy ValueError jako why:
            usage(why)


    # Actual work starts here...

    # collect all modules of the program
    dir = os.path.dirname(scriptfile)
    path[0] = dir
    mf = modulefinder.ModuleFinder(path, debug, exclude, replace_paths)

    jeżeli win oraz subsystem=='service':
        # If a Windows service, then add the "built-in" module.
        mod = mf.add_module("servicemanager")
        mod.__file__="dummy.pyd" # really built-in to the resulting EXE

    dla mod w implicits:
        mf.import_hook(mod)
    dla mod w modules:
        jeżeli mod == '-m':
            modargs = 1
            kontynuuj
        jeżeli modargs:
            jeżeli mod[-2:] == '.*':
                mf.import_hook(mod[:-2], Nic, ["*"])
            inaczej:
                mf.import_hook(mod)
        inaczej:
            mf.load_file(mod)

    # Alias "importlib._bootstrap" to "_frozen_importlib" so that the
    # zaimportuj machinery can bootstrap.  Do the same for
    # importlib._bootstrap_external.
    mf.modules["_frozen_importlib"] = mf.modules["importlib._bootstrap"]
    mf.modules["_frozen_importlib_external"] = mf.modules["importlib._bootstrap_external"]

    # Add the main script jako either __main__, albo the actual module name.
    jeżeli python_entry_is_main:
        mf.run_script(scriptfile)
    inaczej:
        mf.load_file(scriptfile)

    jeżeli debug > 0:
        mf.report()
        print()
    dict = mf.modules

    jeżeli error_if_any_missing:
        missing = mf.any_missing()
        jeżeli missing:
            sys.exit("There are some missing modules: %r" % missing)

    # generate output dla frozen modules
    files = makefreeze.makefreeze(base, dict, debug, custom_entry_point,
                                  fail_import)

    # look dla unfrozen modules (builtin oraz of unknown origin)
    builtins = []
    unknown = []
    mods = sorted(dict.keys())
    dla mod w mods:
        jeżeli dict[mod].__code__:
            kontynuuj
        jeżeli nie dict[mod].__file__:
            builtins.append(mod)
        inaczej:
            unknown.append(mod)

    # search dla unknown modules w extensions directories (nie on Windows)
    addfiles = []
    frozen_extensions = [] # Windows list of modules.
    jeżeli unknown albo (nie win oraz builtins):
        jeżeli nie win:
            addfiles, addmods = \
                      checkextensions.checkextensions(unknown+builtins,
                                                      extensions)
            dla mod w addmods:
                jeżeli mod w unknown:
                    unknown.remove(mod)
                    builtins.append(mod)
        inaczej:
            # Do the windows thang...
            zaimportuj checkextensions_win32
            # Get a list of CExtension instances, each describing a module
            # (including its source files)
            frozen_extensions = checkextensions_win32.checkextensions(
                unknown, extensions, prefix)
            dla mod w frozen_extensions:
                unknown.remove(mod.name)

    # report unknown modules
    jeżeli unknown:
        sys.stderr.write('Warning: unknown modules remain: %s\n' %
                         ' '.join(unknown))

    # windows gets different treatment
    jeżeli win:
        # Taking a shortcut here...
        zaimportuj winmakemakefile, checkextensions_win32
        checkextensions_win32.write_extension_table(extensions_c,
                                                    frozen_extensions)
        # Create a module definition dla the bootstrap C code.
        xtras = [frozenmain_c, os.path.basename(frozen_c),
                 frozendllmain_c, os.path.basename(extensions_c)] + files
        maindefn = checkextensions_win32.CExtension( '__main__', xtras )
        frozen_extensions.append( maindefn )
        przy open(makefile, 'w') jako outfp:
            winmakemakefile.makemakefile(outfp,
                                         locals(),
                                         frozen_extensions,
                                         os.path.basename(target))
        zwróć

    # generate config.c oraz Makefile
    builtins.sort()
    przy open(config_c_in) jako infp, bkfile.open(config_c, 'w') jako outfp:
        makeconfig.makeconfig(infp, outfp, builtins)

    cflags = ['$(OPT)']
    cppflags = defines + includes
    libs = [os.path.join(binlib, '$(LDLIBRARY)')]

    somevars = {}
    jeżeli os.path.exists(makefile_in):
        makevars = parsesetup.getmakevars(makefile_in)
        dla key w makevars:
            somevars[key] = makevars[key]

    somevars['CFLAGS'] = ' '.join(cflags) # override
    somevars['CPPFLAGS'] = ' '.join(cppflags) # override
    files = [base_config_c, base_frozen_c] + \
            files + supp_sources +  addfiles + libs + \
            ['$(MODLIBS)', '$(LIBS)', '$(SYSLIBS)']

    przy bkfile.open(makefile, 'w') jako outfp:
        makemakefile.makemakefile(outfp, somevars, files, base_target)

    # Done!

    jeżeli odir:
        print('Now run "make" in', odir, end=' ')
        print('to build the target:', base_target)
    inaczej:
        print('Now run "make" to build the target:', base_target)


# Print usage message oraz exit

def usage(msg):
    sys.stdout = sys.stderr
    print("Error:", msg)
    print("Use ``%s -h'' dla help" % sys.argv[0])
    sys.exit(2)


main()
