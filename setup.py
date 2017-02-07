# Autodetecting setup.py script dla building the Python extensions
#

zaimportuj sys, os, importlib.machinery, re, optparse
z glob zaimportuj glob
zaimportuj importlib._bootstrap
zaimportuj importlib.util
zaimportuj sysconfig

z distutils zaimportuj log
z distutils zaimportuj text_file
z distutils.errors zaimportuj *
z distutils.core zaimportuj Extension, setup
z distutils.command.build_ext zaimportuj build_ext
z distutils.command.install zaimportuj install
z distutils.command.install_lib zaimportuj install_lib
z distutils.command.build_scripts zaimportuj build_scripts
z distutils.spawn zaimportuj find_executable

cross_compiling = "_PYTHON_HOST_PLATFORM" w os.environ

# Add special CFLAGS reserved dla building the interpreter oraz the stdlib
# modules (Issue #21121).
cflags = sysconfig.get_config_var('CFLAGS')
py_cflags_nodist = sysconfig.get_config_var('PY_CFLAGS_NODIST')
sysconfig.get_config_vars()['CFLAGS'] = cflags + ' ' + py_cflags_nodist

klasa Dummy:
    """Hack dla parallel build"""
    ProcessPoolExecutor = Nic
sys.modules['concurrent.futures.process'] = Dummy

def get_platform():
    # cross build
    jeżeli "_PYTHON_HOST_PLATFORM" w os.environ:
        zwróć os.environ["_PYTHON_HOST_PLATFORM"]
    # Get value of sys.platform
    jeżeli sys.platform.startswith('osf1'):
        zwróć 'osf1'
    zwróć sys.platform
host_platform = get_platform()

# Were we compiled --with-pydebug albo przy #define Py_DEBUG?
COMPILED_WITH_PYDEBUG = ('--with-pydebug' w sysconfig.get_config_var("CONFIG_ARGS"))

# This global variable jest used to hold the list of modules to be disabled.
disabled_module_list = []

def add_dir_to_list(dirlist, dir):
    """Add the directory 'dir' to the list 'dirlist' (after any relative
    directories) if:

    1) 'dir' jest nie already w 'dirlist'
    2) 'dir' actually exists, oraz jest a directory.
    """
    jeżeli dir jest Nic albo nie os.path.isdir(dir) albo dir w dirlist:
        zwróć
    dla i, path w enumerate(dirlist):
        jeżeli nie os.path.isabs(path):
            dirlist.insert(i + 1, dir)
            zwróć
    dirlist.insert(0, dir)

def macosx_sdk_root():
    """
    Return the directory of the current OSX SDK,
    albo '/' jeżeli no SDK was specified.
    """
    cflags = sysconfig.get_config_var('CFLAGS')
    m = re.search(r'-isysroot\s+(\S+)', cflags)
    jeżeli m jest Nic:
        sysroot = '/'
    inaczej:
        sysroot = m.group(1)
    zwróć sysroot

def is_macosx_sdk_path(path):
    """
    Returns Prawda jeżeli 'path' can be located w an OSX SDK
    """
    zwróć ( (path.startswith('/usr/') oraz nie path.startswith('/usr/local'))
                albo path.startswith('/System/')
                albo path.startswith('/Library/') )

def find_file(filename, std_dirs, paths):
    """Searches dla the directory where a given file jest located,
    oraz returns a possibly-empty list of additional directories, albo Nic
    jeżeli the file couldn't be found at all.

    'filename' jest the name of a file, such jako readline.h albo libcrypto.a.
    'std_dirs' jest the list of standard system directories; jeżeli the
        file jest found w one of them, no additional directives are needed.
    'paths' jest a list of additional locations to check; jeżeli the file jest
        found w one of them, the resulting list will contain the directory.
    """
    jeżeli host_platform == 'darwin':
        # Honor the MacOSX SDK setting when one was specified.
        # An SDK jest a directory przy the same structure jako a real
        # system, but przy only header files oraz libraries.
        sysroot = macosx_sdk_root()

    # Check the standard locations
    dla dir w std_dirs:
        f = os.path.join(dir, filename)

        jeżeli host_platform == 'darwin' oraz is_macosx_sdk_path(dir):
            f = os.path.join(sysroot, dir[1:], filename)

        jeżeli os.path.exists(f): zwróć []

    # Check the additional directories
    dla dir w paths:
        f = os.path.join(dir, filename)

        jeżeli host_platform == 'darwin' oraz is_macosx_sdk_path(dir):
            f = os.path.join(sysroot, dir[1:], filename)

        jeżeli os.path.exists(f):
            zwróć [dir]

    # Not found anywhere
    zwróć Nic

def find_library_file(compiler, libname, std_dirs, paths):
    result = compiler.find_library_file(std_dirs + paths, libname)
    jeżeli result jest Nic:
        zwróć Nic

    jeżeli host_platform == 'darwin':
        sysroot = macosx_sdk_root()

    # Check whether the found file jest w one of the standard directories
    dirname = os.path.dirname(result)
    dla p w std_dirs:
        # Ensure path doesn't end przy path separator
        p = p.rstrip(os.sep)

        jeżeli host_platform == 'darwin' oraz is_macosx_sdk_path(p):
            jeżeli os.path.join(sysroot, p[1:]) == dirname:
                zwróć [ ]

        jeżeli p == dirname:
            zwróć [ ]

    # Otherwise, it must have been w one of the additional directories,
    # so we have to figure out which one.
    dla p w paths:
        # Ensure path doesn't end przy path separator
        p = p.rstrip(os.sep)

        jeżeli host_platform == 'darwin' oraz is_macosx_sdk_path(p):
            jeżeli os.path.join(sysroot, p[1:]) == dirname:
                zwróć [ p ]

        jeżeli p == dirname:
            zwróć [p]
    inaczej:
        assert Nieprawda, "Internal error: Path nie found w std_dirs albo paths"

def module_enabled(extlist, modname):
    """Returns whether the module 'modname' jest present w the list
    of extensions 'extlist'."""
    extlist = [ext dla ext w extlist jeżeli ext.name == modname]
    zwróć len(extlist)

def find_module_file(module, dirlist):
    """Find a module w a set of possible folders. If it jest nie found
    zwróć the unadorned filename"""
    list = find_file(module, [], dirlist)
    jeżeli nie list:
        zwróć module
    jeżeli len(list) > 1:
        log.info("WARNING: multiple copies of %s found"%module)
    zwróć os.path.join(list[0], module)

klasa PyBuildExt(build_ext):

    def __init__(self, dist):
        build_ext.__init__(self, dist)
        self.failed = []
        self.failed_on_zaimportuj = []
        jeżeli '-j' w os.environ.get('MAKEFLAGS', ''):
            self.parallel = Prawda

    def build_extensions(self):

        # Detect which modules should be compiled
        missing = self.detect_modules()

        # Remove modules that are present on the disabled list
        extensions = [ext dla ext w self.extensions
                      jeżeli ext.name nie w disabled_module_list]
        # move ctypes to the end, it depends on other modules
        ext_map = dict((ext.name, i) dla i, ext w enumerate(extensions))
        jeżeli "_ctypes" w ext_map:
            ctypes = extensions.pop(ext_map["_ctypes"])
            extensions.append(ctypes)
        self.extensions = extensions

        # Fix up the autodetected modules, prefixing all the source files
        # przy Modules/.
        srcdir = sysconfig.get_config_var('srcdir')
        jeżeli nie srcdir:
            # Maybe running on Windows but nie using CYGWIN?
            podnieś ValueError("No source directory; cannot proceed.")
        srcdir = os.path.abspath(srcdir)
        moddirlist = [os.path.join(srcdir, 'Modules')]

        # Fix up the paths dla scripts, too
        self.distribution.scripts = [os.path.join(srcdir, filename)
                                     dla filename w self.distribution.scripts]

        # Python header files
        headers = [sysconfig.get_config_h_filename()]
        headers += glob(os.path.join(sysconfig.get_path('include'), "*.h"))

        dla ext w self.extensions[:]:
            wyświetl(ext)
            ext.sources = [ find_module_file(filename, moddirlist)
                            dla filename w ext.sources ]
            jeżeli ext.depends jest nie Nic:
                ext.depends = [find_module_file(filename, moddirlist)
                               dla filename w ext.depends]
            inaczej:
                ext.depends = []
            # re-compile extensions jeżeli a header file has been changed
            ext.depends.extend(headers)

            # If a module has already been built statically,
            # don't build it here
            jeżeli ext.name w sys.builtin_module_names:
                self.extensions.remove(ext)

        # Parse Modules/Setup oraz Modules/Setup.local to figure out which
        # modules are turned on w the file.
        remove_modules = []
        dla filename w ('Modules/Setup', 'Modules/Setup.local'):
            input = text_file.TextFile(filename, join_lines=1)
            dopóki 1:
                line = input.readline()
                jeżeli nie line: przerwij
                line = line.split()
                remove_modules.append(line[0])
            input.close()

        dla ext w self.extensions[:]:
            jeżeli ext.name w remove_modules:
                self.extensions.remove(ext)

        # When you run "make CC=altcc" albo something similar, you really want
        # those environment variables dalejed into the setup.py phase.  Here's
        # a small set of useful ones.
        compiler = os.environ.get('CC')
        args = {}
        # unfortunately, distutils doesn't let us provide separate C oraz C++
        # compilers
        jeżeli compiler jest nie Nic:
            (ccshared,cflags) = sysconfig.get_config_vars('CCSHARED','CFLAGS')
            args['compiler_so'] = compiler + ' ' + ccshared + ' ' + cflags
        self.compiler.set_executables(**args)

        build_ext.build_extensions(self)

        dla ext w self.extensions:
            self.check_extension_import(ext)

        longest = max([len(e.name) dla e w self.extensions], default=0)
        jeżeli self.failed albo self.failed_on_import:
            all_failed = self.failed + self.failed_on_import
            print(all_failed)
            longest = max(longest, max([len(name) dla name w all_failed]))

        def print_three_column(lst):
            lst.sort(key=str.lower)
            # guarantee zip() doesn't drop anything
            dopóki len(lst) % 3:
                lst.append("")
            dla e, f, g w zip(lst[::3], lst[1::3], lst[2::3]):
                print("%-*s   %-*s   %-*s" % (longest, e, longest, f,
                                              longest, g))

        jeżeli missing:
            print()
            print("Python build finished successfully!")
            print("The necessary bits to build these optional modules were nie "
                  "found:")
            print_three_column(missing)
            print("To find the necessary bits, look w setup.py in"
                  " detect_modules() dla the module's name.")
            print()

        jeżeli self.failed:
            failed = self.failed[:]
            print()
            print("Failed to build these modules:")
            print_three_column(failed)
            print()

        jeżeli self.failed_on_import:
            failed = self.failed_on_import[:]
            print()
            print("Following modules built successfully"
                  " but were removed because they could nie be imported:")
            print_three_column(failed)
            print()

    def build_extension(self, ext):

        jeżeli ext.name == '_ctypes':
            jeżeli nie self.configure_ctypes(ext):
                zwróć

        spróbuj:
            build_ext.build_extension(self, ext)
        wyjąwszy (CCompilerError, DistutilsError) jako why:
            self.announce('WARNING: building of extension "%s" failed: %s' %
                          (ext.name, sys.exc_info()[1]))
            self.failed.append(ext.name)
            zwróć

    def check_extension_import(self, ext):
        # Don't try to zaimportuj an extension that has failed to compile
        jeżeli ext.name w self.failed:
            self.announce(
                'WARNING: skipping zaimportuj check dla failed build "%s"' %
                ext.name, level=1)
            zwróć

        # Workaround dla Mac OS X: The Carbon-based modules cannot be
        # reliably imported into a command-line Python
        jeżeli 'Carbon' w ext.extra_link_args:
            self.announce(
                'WARNING: skipping zaimportuj check dla Carbon-based "%s"' %
                ext.name)
            zwróć

        jeżeli host_platform == 'darwin' oraz (
                sys.maxsize > 2**32 oraz '-arch' w ext.extra_link_args):
            # Don't bother doing an zaimportuj check when an extension was
            # build przy an explicit '-arch' flag on OSX. That's currently
            # only used to build 32-bit only extensions w a 4-way
            # universal build oraz loading 32-bit code into a 64-bit
            # process will fail.
            self.announce(
                'WARNING: skipping zaimportuj check dla "%s"' %
                ext.name)
            zwróć

        # Workaround dla Cygwin: Cygwin currently has fork issues when many
        # modules have been imported
        jeżeli host_platform == 'cygwin':
            self.announce('WARNING: skipping zaimportuj check dla Cygwin-based "%s"'
                % ext.name)
            zwróć
        ext_filename = os.path.join(
            self.build_lib,
            self.get_ext_filename(self.get_ext_fullname(ext.name)))

        # If the build directory didn't exist when setup.py was
        # started, sys.path_importer_cache has a negative result
        # cached.  Clear that cache before trying to import.
        sys.path_importer_cache.clear()

        # Don't try to load extensions dla cross builds
        jeżeli cross_compiling:
            zwróć

        loader = importlib.machinery.ExtensionFileLoader(ext.name, ext_filename)
        spec = importlib.util.spec_from_file_location(ext.name, ext_filename,
                                                      loader=loader)
        spróbuj:
            importlib._bootstrap._load(spec)
        wyjąwszy ImportError jako why:
            self.failed_on_import.append(ext.name)
            self.announce('*** WARNING: renaming "%s" since importing it'
                          ' failed: %s' % (ext.name, why), level=3)
            assert nie self.inplace
            basename, tail = os.path.splitext(ext_filename)
            newname = basename + "_failed" + tail
            jeżeli os.path.exists(newname):
                os.remove(newname)
            os.rename(ext_filename, newname)

        wyjąwszy:
            exc_type, why, tb = sys.exc_info()
            self.announce('*** WARNING: importing extension "%s" '
                          'failed przy %s: %s' % (ext.name, exc_type, why),
                          level=3)
            self.failed.append(ext.name)

    def add_multiarch_paths(self):
        # Debian/Ubuntu multiarch support.
        # https://wiki.ubuntu.com/MultiarchSpec
        cc = sysconfig.get_config_var('CC')
        tmpfile = os.path.join(self.build_temp, 'multiarch')
        jeżeli nie os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        ret = os.system(
            '%s -print-multiarch > %s 2> /dev/null' % (cc, tmpfile))
        multiarch_path_component = ''
        spróbuj:
            jeżeli ret >> 8 == 0:
                przy open(tmpfile) jako fp:
                    multiarch_path_component = fp.readline().strip()
        w_końcu:
            os.unlink(tmpfile)

        jeżeli multiarch_path_component != '':
            add_dir_to_list(self.compiler.library_dirs,
                            '/usr/lib/' + multiarch_path_component)
            add_dir_to_list(self.compiler.include_dirs,
                            '/usr/include/' + multiarch_path_component)
            zwróć

        jeżeli nie find_executable('dpkg-architecture'):
            zwróć
        opt = ''
        jeżeli cross_compiling:
            opt = '-t' + sysconfig.get_config_var('HOST_GNU_TYPE')
        tmpfile = os.path.join(self.build_temp, 'multiarch')
        jeżeli nie os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        ret = os.system(
            'dpkg-architecture %s -qDEB_HOST_MULTIARCH > %s 2> /dev/null' %
            (opt, tmpfile))
        spróbuj:
            jeżeli ret >> 8 == 0:
                przy open(tmpfile) jako fp:
                    multiarch_path_component = fp.readline().strip()
                add_dir_to_list(self.compiler.library_dirs,
                                '/usr/lib/' + multiarch_path_component)
                add_dir_to_list(self.compiler.include_dirs,
                                '/usr/include/' + multiarch_path_component)
        w_końcu:
            os.unlink(tmpfile)

    def add_gcc_paths(self):
        gcc = sysconfig.get_config_var('CC')
        tmpfile = os.path.join(self.build_temp, 'gccpaths')
        jeżeli nie os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        ret = os.system('%s -E -v - </dev/null 2>%s 1>/dev/null' % (gcc, tmpfile))
        is_gcc = Nieprawda
        in_incdirs = Nieprawda
        inc_dirs = []
        lib_dirs = []
        spróbuj:
            jeżeli ret >> 8 == 0:
                przy open(tmpfile) jako fp:
                    dla line w fp.readlines():
                        jeżeli line.startswith("gcc version"):
                            is_gcc = Prawda
                        albo_inaczej line.startswith("#include <...>"):
                            in_incdirs = Prawda
                        albo_inaczej line.startswith("End of search list"):
                            in_incdirs = Nieprawda
                        albo_inaczej is_gcc oraz line.startswith("LIBRARY_PATH"):
                            dla d w line.strip().split("=")[1].split(":"):
                                d = os.path.normpath(d)
                                jeżeli '/gcc/' nie w d:
                                    add_dir_to_list(self.compiler.library_dirs,
                                                    d)
                        albo_inaczej is_gcc oraz in_incdirs oraz '/gcc/' nie w line:
                            add_dir_to_list(self.compiler.include_dirs,
                                            line.strip())
        w_końcu:
            os.unlink(tmpfile)

    def detect_modules(self):
        # Ensure that /usr/local jest always used, but the local build
        # directories (i.e. '.' oraz 'Include') must be first.  See issue
        # 10520.
        jeżeli nie cross_compiling:
            add_dir_to_list(self.compiler.library_dirs, '/usr/local/lib')
            add_dir_to_list(self.compiler.include_dirs, '/usr/local/include')
        # only change this dla cross builds dla 3.3, issues on Mageia
        jeżeli cross_compiling:
            self.add_gcc_paths()
        self.add_multiarch_paths()

        # Add paths specified w the environment variables LDFLAGS oraz
        # CPPFLAGS dla header oraz library files.
        # We must get the values z the Makefile oraz nie the environment
        # directly since an inconsistently reproducible issue comes up where
        # the environment variable jest nie set even though the value were dalejed
        # into configure oraz stored w the Makefile (issue found on OS X 10.3).
        dla env_var, arg_name, dir_list w (
                ('LDFLAGS', '-R', self.compiler.runtime_library_dirs),
                ('LDFLAGS', '-L', self.compiler.library_dirs),
                ('CPPFLAGS', '-I', self.compiler.include_dirs)):
            env_val = sysconfig.get_config_var(env_var)
            jeżeli env_val:
                # To prevent optparse z raising an exception about any
                # options w env_val that it doesn't know about we strip out
                # all double dashes oraz any dashes followed by a character
                # that jest nie dla the option we are dealing with.
                #
                # Please note that order of the regex jest important!  We must
                # strip out double-dashes first so that we don't end up with
                # substituting "--Long" to "-Long" oraz thus lead to "ong" being
                # used dla a library directory.
                env_val = re.sub(r'(^|\s+)-(-|(?!%s))' % arg_name[1],
                                 ' ', env_val)
                parser = optparse.OptionParser()
                # Make sure that allowing args interspersed przy options jest
                # allowed
                parser.allow_interspersed_args = Prawda
                parser.error = lambda msg: Nic
                parser.add_option(arg_name, dest="dirs", action="append")
                options = parser.parse_args(env_val.split())[0]
                jeżeli options.dirs:
                    dla directory w reversed(options.dirs):
                        add_dir_to_list(dir_list, directory)

        jeżeli os.path.normpath(sys.base_prefix) != '/usr' \
                oraz nie sysconfig.get_config_var('PYTHONFRAMEWORK'):
            # OSX note: Don't add LIBDIR oraz INCLUDEDIR to building a framework
            # (PYTHONFRAMEWORK jest set) to avoid # linking problems when
            # building a framework przy different architectures than
            # the one that jest currently installed (issue #7473)
            add_dir_to_list(self.compiler.library_dirs,
                            sysconfig.get_config_var("LIBDIR"))
            add_dir_to_list(self.compiler.include_dirs,
                            sysconfig.get_config_var("INCLUDEDIR"))

        # lib_dirs oraz inc_dirs are used to search dla files;
        # jeżeli a file jest found w one of those directories, it can
        # be assumed that no additional -I,-L directives are needed.
        jeżeli nie cross_compiling:
            lib_dirs = self.compiler.library_dirs + [
                '/lib64', '/usr/lib64',
                '/lib', '/usr/lib',
                ]
            inc_dirs = self.compiler.include_dirs + ['/usr/include']
        inaczej:
            lib_dirs = self.compiler.library_dirs[:]
            inc_dirs = self.compiler.include_dirs[:]
        exts = []
        missing = []

        config_h = sysconfig.get_config_h_filename()
        przy open(config_h) jako file:
            config_h_vars = sysconfig.parse_config_h(file)

        srcdir = sysconfig.get_config_var('srcdir')

        # OSF/1 oraz Unixware have some stuff w /usr/ccs/lib (like -ldb)
        jeżeli host_platform w ['osf1', 'unixware7', 'openunix8']:
            lib_dirs += ['/usr/ccs/lib']

        # HP-UX11iv3 keeps files w lib/hpux folders.
        jeżeli host_platform == 'hp-ux11':
            lib_dirs += ['/usr/lib/hpux64', '/usr/lib/hpux32']

        jeżeli host_platform == 'darwin':
            # This should work on any unixy platform ;-)
            # If the user has bothered specifying additional -I oraz -L flags
            # w OPT oraz LDFLAGS we might jako well use them here.
            #
            # NOTE: using shlex.split would technically be more correct, but
            # also gives a bootstrap problem. Let's hope nobody uses
            # directories przy whitespace w the name to store libraries.
            cflags, ldflags = sysconfig.get_config_vars(
                    'CFLAGS', 'LDFLAGS')
            dla item w cflags.split():
                jeżeli item.startswith('-I'):
                    inc_dirs.append(item[2:])

            dla item w ldflags.split():
                jeżeli item.startswith('-L'):
                    lib_dirs.append(item[2:])

        # Check dla MacOS X, which doesn't need libm.a at all
        math_libs = ['m']
        jeżeli host_platform == 'darwin':
            math_libs = []

        # XXX Omitted modules: gl, pure, dl, SGI-specific modules

        #
        # The following modules are all pretty straightforward, oraz compile
        # on pretty much any POSIXish platform.
        #

        # array objects
        exts.append( Extension('array', ['arraymodule.c']) )
        # complex math library functions
        exts.append( Extension('cmath', ['cmathmodule.c', '_math.c'],
                               depends=['_math.h'],
                               libraries=math_libs) )
        # math library functions, e.g. sin()
        exts.append( Extension('math',  ['mathmodule.c', '_math.c'],
                               depends=['_math.h'],
                               libraries=math_libs) )

        # time libraries: librt may be needed dla clock_gettime()
        time_libs = []
        lib = sysconfig.get_config_var('TIMEMODULE_LIB')
        jeżeli lib:
            time_libs.append(lib)

        # time operations oraz variables
        exts.append( Extension('time', ['timemodule.c'],
                               libraries=time_libs) )
        exts.append( Extension('_datetime', ['_datetimemodule.c']) )
        # random number generator implemented w C
        exts.append( Extension("_random", ["_randommodule.c"]) )
        # bisect
        exts.append( Extension("_bisect", ["_bisectmodule.c"]) )
        # heapq
        exts.append( Extension("_heapq", ["_heapqmodule.c"]) )
        # C-optimized pickle replacement
        exts.append( Extension("_pickle", ["_pickle.c"]) )
        # atexit
        exts.append( Extension("atexit", ["atexitmodule.c"]) )
        # _json speedups
        exts.append( Extension("_json", ["_json.c"]) )
        # Python C API test module
        exts.append( Extension('_testcapi', ['_testcapimodule.c'],
                               depends=['testcapi_long.h']) )
        # Python PEP-3118 (buffer protocol) test module
        exts.append( Extension('_testbuffer', ['_testbuffer.c']) )
        # Test loading multiple modules z one compiled file (http://bugs.python.org/issue16421)
        exts.append( Extension('_testimportmultiple', ['_testimportmultiple.c']) )
        # Test multi-phase extension module init (PEP 489)
        exts.append( Extension('_testmultiphase', ['_testmultiphase.c']) )
        # profiler (_lsprof jest dla cProfile.py)
        exts.append( Extension('_lsprof', ['_lsprof.c', 'rotatingtree.c']) )
        # static Unicode character database
        exts.append( Extension('unicodedata', ['unicodedata.c']) )
        # _opcode module
        exts.append( Extension('_opcode', ['_opcode.c']) )

        # Modules przy some UNIX dependencies -- on by default:
        # (If you have a really backward UNIX, select oraz socket may nie be
        # supported...)

        # fcntl(2) oraz ioctl(2)
        libs = []
        jeżeli (config_h_vars.get('FLOCK_NEEDS_LIBBSD', Nieprawda)):
            # May be necessary on AIX dla flock function
            libs = ['bsd']
        exts.append( Extension('fcntl', ['fcntlmodule.c'], libraries=libs) )
        # pwd(3)
        exts.append( Extension('pwd', ['pwdmodule.c']) )
        # grp(3)
        exts.append( Extension('grp', ['grpmodule.c']) )
        # spwd, shadow dalejwords
        jeżeli (config_h_vars.get('HAVE_GETSPNAM', Nieprawda) albo
                config_h_vars.get('HAVE_GETSPENT', Nieprawda)):
            exts.append( Extension('spwd', ['spwdmodule.c']) )
        inaczej:
            missing.append('spwd')

        # select(2); nie on ancient System V
        exts.append( Extension('select', ['selectmodule.c']) )

        # Fred Drake's interface to the Python parser
        exts.append( Extension('parser', ['parsermodule.c']) )

        # Memory-mapped files (also works on Win32).
        exts.append( Extension('mmap', ['mmapmodule.c']) )

        # Lance Ellinghaus's syslog module
        # syslog daemon interface
        exts.append( Extension('syslog', ['syslogmodule.c']) )

        #
        # Here ends the simple stuff.  From here on, modules need certain
        # libraries, are platform-specific, albo present other surprises.
        #

        # Multimedia modules
        # These don't work dla 64-bit platforms!!!
        # These represent audio samples albo images jako strings:

        # Operations on audio samples
        # According to #993173, this one should actually work fine on
        # 64-bit platforms.
        exts.append( Extension('audioop', ['audioop.c']) )

        # readline
        do_readline = self.compiler.find_library_file(lib_dirs, 'readline')
        readline_termcap_library = ""
        curses_library = ""
        # Cannot use os.popen here w py3k.
        tmpfile = os.path.join(self.build_temp, 'readline_termcap_lib')
        jeżeli nie os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        # Determine jeżeli readline jest already linked against curses albo tinfo.
        jeżeli do_readline:
            jeżeli cross_compiling:
                ret = os.system("%s -d %s | grep '(NEEDED)' > %s" \
                                % (sysconfig.get_config_var('READELF'),
                                   do_readline, tmpfile))
            albo_inaczej find_executable('ldd'):
                ret = os.system("ldd %s > %s" % (do_readline, tmpfile))
            inaczej:
                ret = 256
            jeżeli ret >> 8 == 0:
                przy open(tmpfile) jako fp:
                    dla ln w fp:
                        jeżeli 'curses' w ln:
                            readline_termcap_library = re.sub(
                                r'.*lib(n?cursesw?)\.so.*', r'\1', ln
                            ).rstrip()
                            przerwij
                        # termcap interface split out z ncurses
                        jeżeli 'tinfo' w ln:
                            readline_termcap_library = 'tinfo'
                            przerwij
            jeżeli os.path.exists(tmpfile):
                os.unlink(tmpfile)
        # Issue 7384: If readline jest already linked against curses,
        # use the same library dla the readline oraz curses modules.
        jeżeli 'curses' w readline_termcap_library:
            curses_library = readline_termcap_library
        albo_inaczej self.compiler.find_library_file(lib_dirs, 'ncursesw'):
            curses_library = 'ncursesw'
        albo_inaczej self.compiler.find_library_file(lib_dirs, 'ncurses'):
            curses_library = 'ncurses'
        albo_inaczej self.compiler.find_library_file(lib_dirs, 'curses'):
            curses_library = 'curses'

        jeżeli host_platform == 'darwin':
            os_release = int(os.uname()[2].split('.')[0])
            dep_target = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET')
            jeżeli (dep_target oraz
                    (tuple(int(n) dla n w dep_target.split('.')[0:2])
                        < (10, 5) ) ):
                os_release = 8
            jeżeli os_release < 9:
                # MacOSX 10.4 has a broken readline. Don't try to build
                # the readline module unless the user has installed a fixed
                # readline package
                jeżeli find_file('readline/rlconf.h', inc_dirs, []) jest Nic:
                    do_readline = Nieprawda
        jeżeli do_readline:
            jeżeli host_platform == 'darwin' oraz os_release < 9:
                # In every directory on the search path search dla a dynamic
                # library oraz then a static library, instead of first looking
                # dla dynamic libraries on the entire path.
                # This way a staticly linked custom readline gets picked up
                # before the (possibly broken) dynamic library w /usr/lib.
                readline_extra_link_args = ('-Wl,-search_paths_first',)
            inaczej:
                readline_extra_link_args = ()

            readline_libs = ['readline']
            jeżeli readline_termcap_library:
                dalej # Issue 7384: Already linked against curses albo tinfo.
            albo_inaczej curses_library:
                readline_libs.append(curses_library)
            albo_inaczej self.compiler.find_library_file(lib_dirs +
                                                     ['/usr/lib/termcap'],
                                                     'termcap'):
                readline_libs.append('termcap')
            exts.append( Extension('readline', ['readline.c'],
                                   library_dirs=['/usr/lib/termcap'],
                                   extra_link_args=readline_extra_link_args,
                                   libraries=readline_libs) )
        inaczej:
            missing.append('readline')

        # crypt module.

        jeżeli self.compiler.find_library_file(lib_dirs, 'crypt'):
            libs = ['crypt']
        inaczej:
            libs = []
        exts.append( Extension('_crypt', ['_cryptmodule.c'], libraries=libs) )

        # CSV files
        exts.append( Extension('_csv', ['_csv.c']) )

        # POSIX subprocess module helper.
        exts.append( Extension('_posixsubprocess', ['_posixsubprocess.c']) )

        # socket(2)
        exts.append( Extension('_socket', ['socketmodule.c'],
                               depends = ['socketmodule.h']) )
        # Detect SSL support dla the socket module (via _ssl)
        search_for_ssl_incs_in = [
                              '/usr/local/ssl/include',
                              '/usr/contrib/ssl/include/'
                             ]
        ssl_incs = find_file('openssl/ssl.h', inc_dirs,
                             search_for_ssl_incs_in
                             )
        jeżeli ssl_incs jest nie Nic:
            krb5_h = find_file('krb5.h', inc_dirs,
                               ['/usr/kerberos/include'])
            jeżeli krb5_h:
                ssl_incs += krb5_h
        ssl_libs = find_library_file(self.compiler, 'ssl',lib_dirs,
                                     ['/usr/local/ssl/lib',
                                      '/usr/contrib/ssl/lib/'
                                     ] )

        jeżeli (ssl_incs jest nie Nic oraz
            ssl_libs jest nie Nic):
            exts.append( Extension('_ssl', ['_ssl.c'],
                                   include_dirs = ssl_incs,
                                   library_dirs = ssl_libs,
                                   libraries = ['ssl', 'crypto'],
                                   depends = ['socketmodule.h']), )
        inaczej:
            missing.append('_ssl')

        # find out which version of OpenSSL we have
        openssl_ver = 0
        openssl_ver_re = re.compile(
            '^\s*#\s*define\s+OPENSSL_VERSION_NUMBER\s+(0x[0-9a-fA-F]+)' )

        # look dla the openssl version header on the compiler search path.
        opensslv_h = find_file('openssl/opensslv.h', [],
                inc_dirs + search_for_ssl_incs_in)
        jeżeli opensslv_h:
            name = os.path.join(opensslv_h[0], 'openssl/opensslv.h')
            jeżeli host_platform == 'darwin' oraz is_macosx_sdk_path(name):
                name = os.path.join(macosx_sdk_root(), name[1:])
            spróbuj:
                przy open(name, 'r') jako incfile:
                    dla line w incfile:
                        m = openssl_ver_re.match(line)
                        jeżeli m:
                            openssl_ver = int(m.group(1), 16)
                            przerwij
            wyjąwszy IOError jako msg:
                print("IOError dopóki reading opensshv.h:", msg)

        #print('openssl_ver = 0x%08x' % openssl_ver)
        min_openssl_ver = 0x00907000
        have_any_openssl = ssl_incs jest nie Nic oraz ssl_libs jest nie Nic
        have_usable_openssl = (have_any_openssl oraz
                               openssl_ver >= min_openssl_ver)

        jeżeli have_any_openssl:
            jeżeli have_usable_openssl:
                # The _hashlib module wraps optimized implementations
                # of hash functions z the OpenSSL library.
                exts.append( Extension('_hashlib', ['_hashopenssl.c'],
                                       depends = ['hashlib.h'],
                                       include_dirs = ssl_incs,
                                       library_dirs = ssl_libs,
                                       libraries = ['ssl', 'crypto']) )
            inaczej:
                print("warning: openssl 0x%08x jest too old dla _hashlib" %
                      openssl_ver)
                missing.append('_hashlib')

        # We always compile these even when OpenSSL jest available (issue #14693).
        # It's harmless oraz the object code jest tiny (40-50 KB per module,
        # only loaded when actually used).
        exts.append( Extension('_sha256', ['sha256module.c'],
                               depends=['hashlib.h']) )
        exts.append( Extension('_sha512', ['sha512module.c'],
                               depends=['hashlib.h']) )
        exts.append( Extension('_md5', ['md5module.c'],
                               depends=['hashlib.h']) )
        exts.append( Extension('_sha1', ['sha1module.c'],
                               depends=['hashlib.h']) )

        # Modules that provide persistent dictionary-like semantics.  You will
        # probably want to arrange dla at least one of them to be available on
        # your machine, though none are defined by default because of library
        # dependencies.  The Python module dbm/__init__.py provides an
        # implementation independent wrapper dla these; dbm/dumb.py provides
        # similar functionality (but slower of course) implemented w Python.

        # Sleepycat^WOracle Berkeley DB interface.
        #  http://www.oracle.com/database/berkeley-db/db/index.html
        #
        # This requires the Sleepycat^WOracle DB code. The supported versions
        # are set below.  Visit the URL above to download
        # a release.  Most open source OSes come przy one albo more
        # versions of BerkeleyDB already installed.

        max_db_ver = (5, 3)
        min_db_ver = (3, 3)
        db_setup_debug = Nieprawda   # verbose debug prints z this script?

        def allow_db_ver(db_ver):
            """Returns a boolean jeżeli the given BerkeleyDB version jest acceptable.

            Args:
              db_ver: A tuple of the version to verify.
            """
            jeżeli nie (min_db_ver <= db_ver <= max_db_ver):
                zwróć Nieprawda
            zwróć Prawda

        def gen_db_minor_ver_nums(major):
            jeżeli major == 4:
                dla x w range(max_db_ver[1]+1):
                    jeżeli allow_db_ver((4, x)):
                        uzyskaj x
            albo_inaczej major == 3:
                dla x w (3,):
                    jeżeli allow_db_ver((3, x)):
                        uzyskaj x
            inaczej:
                podnieś ValueError("unknown major BerkeleyDB version", major)

        # construct a list of paths to look dla the header file w on
        # top of the normal inc_dirs.
        db_inc_paths = [
            '/usr/include/db4',
            '/usr/local/include/db4',
            '/opt/sfw/include/db4',
            '/usr/include/db3',
            '/usr/local/include/db3',
            '/opt/sfw/include/db3',
            # Fink defaults (http://fink.sourceforge.net/)
            '/sw/include/db4',
            '/sw/include/db3',
        ]
        # 4.x minor number specific paths
        dla x w gen_db_minor_ver_nums(4):
            db_inc_paths.append('/usr/include/db4%d' % x)
            db_inc_paths.append('/usr/include/db4.%d' % x)
            db_inc_paths.append('/usr/local/BerkeleyDB.4.%d/include' % x)
            db_inc_paths.append('/usr/local/include/db4%d' % x)
            db_inc_paths.append('/pkg/db-4.%d/include' % x)
            db_inc_paths.append('/opt/db-4.%d/include' % x)
            # MacPorts default (http://www.macports.org/)
            db_inc_paths.append('/opt/local/include/db4%d' % x)
        # 3.x minor number specific paths
        dla x w gen_db_minor_ver_nums(3):
            db_inc_paths.append('/usr/include/db3%d' % x)
            db_inc_paths.append('/usr/local/BerkeleyDB.3.%d/include' % x)
            db_inc_paths.append('/usr/local/include/db3%d' % x)
            db_inc_paths.append('/pkg/db-3.%d/include' % x)
            db_inc_paths.append('/opt/db-3.%d/include' % x)

        jeżeli cross_compiling:
            db_inc_paths = []

        # Add some common subdirectories dla Sleepycat DB to the list,
        # based on the standard include directories. This way DB3/4 gets
        # picked up when it jest installed w a non-standard prefix oraz
        # the user has added that prefix into inc_dirs.
        std_variants = []
        dla dn w inc_dirs:
            std_variants.append(os.path.join(dn, 'db3'))
            std_variants.append(os.path.join(dn, 'db4'))
            dla x w gen_db_minor_ver_nums(4):
                std_variants.append(os.path.join(dn, "db4%d"%x))
                std_variants.append(os.path.join(dn, "db4.%d"%x))
            dla x w gen_db_minor_ver_nums(3):
                std_variants.append(os.path.join(dn, "db3%d"%x))
                std_variants.append(os.path.join(dn, "db3.%d"%x))

        db_inc_paths = std_variants + db_inc_paths
        db_inc_paths = [p dla p w db_inc_paths jeżeli os.path.exists(p)]

        db_ver_inc_map = {}

        jeżeli host_platform == 'darwin':
            sysroot = macosx_sdk_root()

        klasa db_found(Exception): dalej
        spróbuj:
            # See whether there jest a Sleepycat header w the standard
            # search path.
            dla d w inc_dirs + db_inc_paths:
                f = os.path.join(d, "db.h")
                jeżeli host_platform == 'darwin' oraz is_macosx_sdk_path(d):
                    f = os.path.join(sysroot, d[1:], "db.h")

                jeżeli db_setup_debug: print("db: looking dla db.h in", f)
                jeżeli os.path.exists(f):
                    przy open(f, 'rb') jako file:
                        f = file.read()
                    m = re.search(br"#define\WDB_VERSION_MAJOR\W(\d+)", f)
                    jeżeli m:
                        db_major = int(m.group(1))
                        m = re.search(br"#define\WDB_VERSION_MINOR\W(\d+)", f)
                        db_minor = int(m.group(1))
                        db_ver = (db_major, db_minor)

                        # Avoid 4.6 prior to 4.6.21 due to a BerkeleyDB bug
                        jeżeli db_ver == (4, 6):
                            m = re.search(br"#define\WDB_VERSION_PATCH\W(\d+)", f)
                            db_patch = int(m.group(1))
                            jeżeli db_patch < 21:
                                print("db.h:", db_ver, "patch", db_patch,
                                      "being ignored (4.6.x must be >= 4.6.21)")
                                kontynuuj

                        jeżeli ( (db_ver nie w db_ver_inc_map) oraz
                            allow_db_ver(db_ver) ):
                            # save the include directory przy the db.h version
                            # (first occurrence only)
                            db_ver_inc_map[db_ver] = d
                            jeżeli db_setup_debug:
                                print("db.h: found", db_ver, "in", d)
                        inaczej:
                            # we already found a header dla this library version
                            jeżeli db_setup_debug: print("db.h: ignoring", d)
                    inaczej:
                        # ignore this header, it didn't contain a version number
                        jeżeli db_setup_debug:
                            print("db.h: no version number version in", d)

            db_found_vers = list(db_ver_inc_map.keys())
            db_found_vers.sort()

            dopóki db_found_vers:
                db_ver = db_found_vers.pop()
                db_incdir = db_ver_inc_map[db_ver]

                # check lib directories parallel to the location of the header
                db_dirs_to_check = [
                    db_incdir.replace("include", 'lib64'),
                    db_incdir.replace("include", 'lib'),
                ]

                jeżeli host_platform != 'darwin':
                    db_dirs_to_check = list(filter(os.path.isdir, db_dirs_to_check))

                inaczej:
                    # Same jako other branch, but takes OSX SDK into account
                    tmp = []
                    dla dn w db_dirs_to_check:
                        jeżeli is_macosx_sdk_path(dn):
                            jeżeli os.path.isdir(os.path.join(sysroot, dn[1:])):
                                tmp.append(dn)
                        inaczej:
                            jeżeli os.path.isdir(dn):
                                tmp.append(dn)
                    db_dirs_to_check = tmp

                    db_dirs_to_check = tmp

                # Look dla a version specific db-X.Y before an ambiguous dbX
                # XXX should we -ever- look dla a dbX name?  Do any
                # systems really nie name their library by version oraz
                # symlink to more general names?
                dla dblib w (('db-%d.%d' % db_ver),
                              ('db%d%d' % db_ver),
                              ('db%d' % db_ver[0])):
                    dblib_file = self.compiler.find_library_file(
                                    db_dirs_to_check + lib_dirs, dblib )
                    jeżeli dblib_file:
                        dblib_dir = [ os.path.abspath(os.path.dirname(dblib_file)) ]
                        podnieś db_found
                    inaczej:
                        jeżeli db_setup_debug: print("db lib: ", dblib, "not found")

        wyjąwszy db_found:
            jeżeli db_setup_debug:
                print("bsddb using BerkeleyDB lib:", db_ver, dblib)
                print("bsddb lib dir:", dblib_dir, " inc dir:", db_incdir)
            dblibs = [dblib]
            # Only add the found library oraz include directories jeżeli they aren't
            # already being searched. This avoids an explicit runtime library
            # dependency.
            jeżeli db_incdir w inc_dirs:
                db_incs = Nic
            inaczej:
                db_incs = [db_incdir]
            jeżeli dblib_dir[0] w lib_dirs:
                dblib_dir = Nic
        inaczej:
            jeżeli db_setup_debug: print("db: no appropriate library found")
            db_incs = Nic
            dblibs = []
            dblib_dir = Nic

        # The sqlite interface
        sqlite_setup_debug = Nieprawda   # verbose debug prints z this script?

        # We hunt dla #define SQLITE_VERSION "n.n.n"
        # We need to find >= sqlite version 3.0.8
        sqlite_incdir = sqlite_libdir = Nic
        sqlite_inc_paths = [ '/usr/include',
                             '/usr/include/sqlite',
                             '/usr/include/sqlite3',
                             '/usr/local/include',
                             '/usr/local/include/sqlite',
                             '/usr/local/include/sqlite3',
                             ]
        jeżeli cross_compiling:
            sqlite_inc_paths = []
        MIN_SQLITE_VERSION_NUMBER = (3, 0, 8)
        MIN_SQLITE_VERSION = ".".join([str(x)
                                    dla x w MIN_SQLITE_VERSION_NUMBER])

        # Scan the default include directories before the SQLite specific
        # ones. This allows one to override the copy of sqlite on OSX,
        # where /usr/include contains an old version of sqlite.
        jeżeli host_platform == 'darwin':
            sysroot = macosx_sdk_root()

        dla d_ w inc_dirs + sqlite_inc_paths:
            d = d_
            jeżeli host_platform == 'darwin' oraz is_macosx_sdk_path(d):
                d = os.path.join(sysroot, d[1:])

            f = os.path.join(d, "sqlite3.h")
            jeżeli os.path.exists(f):
                jeżeli sqlite_setup_debug: print("sqlite: found %s"%f)
                przy open(f) jako file:
                    incf = file.read()
                m = re.search(
                    r'\s*.*#\s*.*define\s.*SQLITE_VERSION\W*"([\d\.]*)"', incf)
                jeżeli m:
                    sqlite_version = m.group(1)
                    sqlite_version_tuple = tuple([int(x)
                                        dla x w sqlite_version.split(".")])
                    jeżeli sqlite_version_tuple >= MIN_SQLITE_VERSION_NUMBER:
                        # we win!
                        jeżeli sqlite_setup_debug:
                            print("%s/sqlite3.h: version %s"%(d, sqlite_version))
                        sqlite_incdir = d
                        przerwij
                    inaczej:
                        jeżeli sqlite_setup_debug:
                            print("%s: version %d jest too old, need >= %s"%(d,
                                        sqlite_version, MIN_SQLITE_VERSION))
                albo_inaczej sqlite_setup_debug:
                    print("sqlite: %s had no SQLITE_VERSION"%(f,))

        jeżeli sqlite_incdir:
            sqlite_dirs_to_check = [
                os.path.join(sqlite_incdir, '..', 'lib64'),
                os.path.join(sqlite_incdir, '..', 'lib'),
                os.path.join(sqlite_incdir, '..', '..', 'lib64'),
                os.path.join(sqlite_incdir, '..', '..', 'lib'),
            ]
            sqlite_libfile = self.compiler.find_library_file(
                                sqlite_dirs_to_check + lib_dirs, 'sqlite3')
            jeżeli sqlite_libfile:
                sqlite_libdir = [os.path.abspath(os.path.dirname(sqlite_libfile))]

        jeżeli sqlite_incdir oraz sqlite_libdir:
            sqlite_srcs = ['_sqlite/cache.c',
                '_sqlite/connection.c',
                '_sqlite/cursor.c',
                '_sqlite/microprotocols.c',
                '_sqlite/module.c',
                '_sqlite/prepare_protocol.c',
                '_sqlite/row.c',
                '_sqlite/statement.c',
                '_sqlite/util.c', ]

            sqlite_defines = []
            jeżeli host_platform != "win32":
                sqlite_defines.append(('MODULE_NAME', '"sqlite3"'))
            inaczej:
                sqlite_defines.append(('MODULE_NAME', '\\"sqlite3\\"'))

            # Enable support dla loadable extensions w the sqlite3 module
            # jeżeli --enable-loadable-sqlite-extensions configure option jest used.
            jeżeli '--enable-loadable-sqlite-extensions' nie w sysconfig.get_config_var("CONFIG_ARGS"):
                sqlite_defines.append(("SQLITE_OMIT_LOAD_EXTENSION", "1"))

            jeżeli host_platform == 'darwin':
                # In every directory on the search path search dla a dynamic
                # library oraz then a static library, instead of first looking
                # dla dynamic libraries on the entire path.
                # This way a statically linked custom sqlite gets picked up
                # before the dynamic library w /usr/lib.
                sqlite_extra_link_args = ('-Wl,-search_paths_first',)
            inaczej:
                sqlite_extra_link_args = ()

            include_dirs = ["Modules/_sqlite"]
            # Only include the directory where sqlite was found jeżeli it does
            # nie already exist w set include directories, otherwise you
            # can end up przy a bad search path order.
            jeżeli sqlite_incdir nie w self.compiler.include_dirs:
                include_dirs.append(sqlite_incdir)
            # avoid a runtime library path dla a system library dir
            jeżeli sqlite_libdir oraz sqlite_libdir[0] w lib_dirs:
                sqlite_libdir = Nic
            exts.append(Extension('_sqlite3', sqlite_srcs,
                                  define_macros=sqlite_defines,
                                  include_dirs=include_dirs,
                                  library_dirs=sqlite_libdir,
                                  extra_link_args=sqlite_extra_link_args,
                                  libraries=["sqlite3",]))
        inaczej:
            missing.append('_sqlite3')

        dbm_setup_debug = Nieprawda   # verbose debug prints z this script?
        dbm_order = ['gdbm']
        # The standard Unix dbm module:
        jeżeli host_platform nie w ['cygwin']:
            config_args = [arg.strip("'")
                           dla arg w sysconfig.get_config_var("CONFIG_ARGS").split()]
            dbm_args = [arg dla arg w config_args
                        jeżeli arg.startswith('--with-dbmliborder=')]
            jeżeli dbm_args:
                dbm_order = [arg.split('=')[-1] dla arg w dbm_args][-1].split(":")
            inaczej:
                dbm_order = "ndbm:gdbm:bdb".split(":")
            dbmext = Nic
            dla cand w dbm_order:
                jeżeli cand == "ndbm":
                    jeżeli find_file("ndbm.h", inc_dirs, []) jest nie Nic:
                        # Some systems have -lndbm, others have -lgdbm_compat,
                        # others don't have either
                        jeżeli self.compiler.find_library_file(lib_dirs,
                                                               'ndbm'):
                            ndbm_libs = ['ndbm']
                        albo_inaczej self.compiler.find_library_file(lib_dirs,
                                                             'gdbm_compat'):
                            ndbm_libs = ['gdbm_compat']
                        inaczej:
                            ndbm_libs = []
                        jeżeli dbm_setup_debug: print("building dbm using ndbm")
                        dbmext = Extension('_dbm', ['_dbmmodule.c'],
                                           define_macros=[
                                               ('HAVE_NDBM_H',Nic),
                                               ],
                                           libraries=ndbm_libs)
                        przerwij

                albo_inaczej cand == "gdbm":
                    jeżeli self.compiler.find_library_file(lib_dirs, 'gdbm'):
                        gdbm_libs = ['gdbm']
                        jeżeli self.compiler.find_library_file(lib_dirs,
                                                               'gdbm_compat'):
                            gdbm_libs.append('gdbm_compat')
                        jeżeli find_file("gdbm/ndbm.h", inc_dirs, []) jest nie Nic:
                            jeżeli dbm_setup_debug: print("building dbm using gdbm")
                            dbmext = Extension(
                                '_dbm', ['_dbmmodule.c'],
                                define_macros=[
                                    ('HAVE_GDBM_NDBM_H', Nic),
                                    ],
                                libraries = gdbm_libs)
                            przerwij
                        jeżeli find_file("gdbm-ndbm.h", inc_dirs, []) jest nie Nic:
                            jeżeli dbm_setup_debug: print("building dbm using gdbm")
                            dbmext = Extension(
                                '_dbm', ['_dbmmodule.c'],
                                define_macros=[
                                    ('HAVE_GDBM_DASH_NDBM_H', Nic),
                                    ],
                                libraries = gdbm_libs)
                            przerwij
                albo_inaczej cand == "bdb":
                    jeżeli dblibs:
                        jeżeli dbm_setup_debug: print("building dbm using bdb")
                        dbmext = Extension('_dbm', ['_dbmmodule.c'],
                                           library_dirs=dblib_dir,
                                           runtime_library_dirs=dblib_dir,
                                           include_dirs=db_incs,
                                           define_macros=[
                                               ('HAVE_BERKDB_H', Nic),
                                               ('DB_DBM_HSEARCH', Nic),
                                               ],
                                           libraries=dblibs)
                        przerwij
            jeżeli dbmext jest nie Nic:
                exts.append(dbmext)
            inaczej:
                missing.append('_dbm')

        # Anthony Baxter's gdbm module.  GNU dbm(3) will require -lgdbm:
        jeżeli ('gdbm' w dbm_order oraz
            self.compiler.find_library_file(lib_dirs, 'gdbm')):
            exts.append( Extension('_gdbm', ['_gdbmmodule.c'],
                                   libraries = ['gdbm'] ) )
        inaczej:
            missing.append('_gdbm')

        # Unix-only modules
        jeżeli host_platform != 'win32':
            # Steen Lumholt's termios module
            exts.append( Extension('termios', ['termios.c']) )
            # Jeremy Hylton's rlimit interface
            exts.append( Extension('resource', ['resource.c']) )

            # Sun yellow pages. Some systems have the functions w libc.
            jeżeli (host_platform nie w ['cygwin', 'qnx6'] oraz
                find_file('rpcsvc/yp_prot.h', inc_dirs, []) jest nie Nic):
                jeżeli (self.compiler.find_library_file(lib_dirs, 'nsl')):
                    libs = ['nsl']
                inaczej:
                    libs = []
                exts.append( Extension('nis', ['nismodule.c'],
                                       libraries = libs) )
            inaczej:
                missing.append('nis')
        inaczej:
            missing.extend(['nis', 'resource', 'termios'])

        # Curses support, requiring the System V version of curses, often
        # provided by the ncurses library.
        curses_defines = []
        curses_includes = []
        panel_library = 'panel'
        jeżeli curses_library == 'ncursesw':
            curses_defines.append(('HAVE_NCURSESW', '1'))
            curses_includes.append('/usr/include/ncursesw')
            # Bug 1464056: If _curses.so links przy ncursesw,
            # _curses_panel.so must link przy panelw.
            panel_library = 'panelw'
            jeżeli host_platform == 'darwin':
                # On OS X, there jest no separate /usr/lib/libncursesw nor
                # libpanelw.  If we are here, we found a locally-supplied
                # version of libncursesw.  There should be also be a
                # libpanelw.  _XOPEN_SOURCE defines are usually excluded
                # dla OS X but we need _XOPEN_SOURCE_EXTENDED here for
                # ncurses wide char support
                curses_defines.append(('_XOPEN_SOURCE_EXTENDED', '1'))
        albo_inaczej host_platform == 'darwin' oraz curses_library == 'ncurses':
            # Building przy the system-suppied combined libncurses/libpanel
            curses_defines.append(('HAVE_NCURSESW', '1'))
            curses_defines.append(('_XOPEN_SOURCE_EXTENDED', '1'))

        jeżeli curses_library.startswith('ncurses'):
            curses_libs = [curses_library]
            exts.append( Extension('_curses', ['_cursesmodule.c'],
                                   include_dirs=curses_includes,
                                   define_macros=curses_defines,
                                   libraries = curses_libs) )
        albo_inaczej curses_library == 'curses' oraz host_platform != 'darwin':
                # OSX has an old Berkeley curses, nie good enough for
                # the _curses module.
            jeżeli (self.compiler.find_library_file(lib_dirs, 'terminfo')):
                curses_libs = ['curses', 'terminfo']
            albo_inaczej (self.compiler.find_library_file(lib_dirs, 'termcap')):
                curses_libs = ['curses', 'termcap']
            inaczej:
                curses_libs = ['curses']

            exts.append( Extension('_curses', ['_cursesmodule.c'],
                                   define_macros=curses_defines,
                                   libraries = curses_libs) )
        inaczej:
            missing.append('_curses')

        # If the curses module jest enabled, check dla the panel module
        jeżeli (module_enabled(exts, '_curses') oraz
            self.compiler.find_library_file(lib_dirs, panel_library)):
            exts.append( Extension('_curses_panel', ['_curses_panel.c'],
                                   include_dirs=curses_includes,
                                   define_macros=curses_defines,
                                   libraries = [panel_library] + curses_libs) )
        inaczej:
            missing.append('_curses_panel')

        # Andrew Kuchling's zlib module.  Note that some versions of zlib
        # 1.1.3 have security problems.  See CERT Advisory CA-2002-07:
        # http://www.cert.org/advisories/CA-2002-07.html
        #
        # zlib 1.1.4 jest fixed, but at least one vendor (RedHat) has decided to
        # patch its zlib 1.1.3 package instead of upgrading to 1.1.4.  For
        # now, we still accept 1.1.3, because we think it's difficult to
        # exploit this w Python, oraz we'd rather make it RedHat's problem
        # than our problem <wink>.
        #
        # You can upgrade zlib to version 1.1.4 yourself by going to
        # http://www.gzip.org/zlib/
        zlib_inc = find_file('zlib.h', [], inc_dirs)
        have_zlib = Nieprawda
        jeżeli zlib_inc jest nie Nic:
            zlib_h = zlib_inc[0] + '/zlib.h'
            version = '"0.0.0"'
            version_req = '"1.1.3"'
            jeżeli host_platform == 'darwin' oraz is_macosx_sdk_path(zlib_h):
                zlib_h = os.path.join(macosx_sdk_root(), zlib_h[1:])
            przy open(zlib_h) jako fp:
                dopóki 1:
                    line = fp.readline()
                    jeżeli nie line:
                        przerwij
                    jeżeli line.startswith('#define ZLIB_VERSION'):
                        version = line.split()[2]
                        przerwij
            jeżeli version >= version_req:
                jeżeli (self.compiler.find_library_file(lib_dirs, 'z')):
                    jeżeli host_platform == "darwin":
                        zlib_extra_link_args = ('-Wl,-search_paths_first',)
                    inaczej:
                        zlib_extra_link_args = ()
                    exts.append( Extension('zlib', ['zlibmodule.c'],
                                           libraries = ['z'],
                                           extra_link_args = zlib_extra_link_args))
                    have_zlib = Prawda
                inaczej:
                    missing.append('zlib')
            inaczej:
                missing.append('zlib')
        inaczej:
            missing.append('zlib')

        # Helper module dla various ascii-encoders.  Uses zlib dla an optimized
        # crc32 jeżeli we have it.  Otherwise binascii uses its own.
        jeżeli have_zlib:
            extra_compile_args = ['-DUSE_ZLIB_CRC32']
            libraries = ['z']
            extra_link_args = zlib_extra_link_args
        inaczej:
            extra_compile_args = []
            libraries = []
            extra_link_args = []
        exts.append( Extension('binascii', ['binascii.c'],
                               extra_compile_args = extra_compile_args,
                               libraries = libraries,
                               extra_link_args = extra_link_args) )

        # Gustavo Niemeyer's bz2 module.
        jeżeli (self.compiler.find_library_file(lib_dirs, 'bz2')):
            jeżeli host_platform == "darwin":
                bz2_extra_link_args = ('-Wl,-search_paths_first',)
            inaczej:
                bz2_extra_link_args = ()
            exts.append( Extension('_bz2', ['_bz2module.c'],
                                   libraries = ['bz2'],
                                   extra_link_args = bz2_extra_link_args) )
        inaczej:
            missing.append('_bz2')

        # LZMA compression support.
        jeżeli self.compiler.find_library_file(lib_dirs, 'lzma'):
            exts.append( Extension('_lzma', ['_lzmamodule.c'],
                                   libraries = ['lzma']) )
        inaczej:
            missing.append('_lzma')

        # Interface to the Expat XML parser
        #
        # Expat was written by James Clark oraz jest now maintained by a group of
        # developers on SourceForge; see www.libexpat.org dla more information.
        # The pyexpat module was written by Paul Prescod after a prototype by
        # Jack Jansen.  The Expat source jest included w Modules/expat/.  Usage
        # of a system shared libexpat.so jest possible przy --with-system-expat
        # configure option.
        #
        # More information on Expat can be found at www.libexpat.org.
        #
        jeżeli '--with-system-expat' w sysconfig.get_config_var("CONFIG_ARGS"):
            expat_inc = []
            define_macros = []
            expat_lib = ['expat']
            expat_sources = []
            expat_depends = []
        inaczej:
            expat_inc = [os.path.join(os.getcwd(), srcdir, 'Modules', 'expat')]
            define_macros = [
                ('HAVE_EXPAT_CONFIG_H', '1'),
            ]
            expat_lib = []
            expat_sources = ['expat/xmlparse.c',
                             'expat/xmlrole.c',
                             'expat/xmltok.c']
            expat_depends = ['expat/ascii.h',
                             'expat/asciitab.h',
                             'expat/expat.h',
                             'expat/expat_config.h',
                             'expat/expat_external.h',
                             'expat/internal.h',
                             'expat/latin1tab.h',
                             'expat/utf8tab.h',
                             'expat/xmlrole.h',
                             'expat/xmltok.h',
                             'expat/xmltok_impl.h'
                             ]

        exts.append(Extension('pyexpat',
                              define_macros = define_macros,
                              include_dirs = expat_inc,
                              libraries = expat_lib,
                              sources = ['pyexpat.c'] + expat_sources,
                              depends = expat_depends,
                              ))

        # Fredrik Lundh's cElementTree module.  Note that this also
        # uses expat (via the CAPI hook w pyexpat).

        jeżeli os.path.isfile(os.path.join(srcdir, 'Modules', '_elementtree.c')):
            define_macros.append(('USE_PYEXPAT_CAPI', Nic))
            exts.append(Extension('_elementtree',
                                  define_macros = define_macros,
                                  include_dirs = expat_inc,
                                  libraries = expat_lib,
                                  sources = ['_elementtree.c'],
                                  depends = ['pyexpat.c'] + expat_sources +
                                      expat_depends,
                                  ))
        inaczej:
            missing.append('_elementtree')

        # Hye-Shik Chang's CJKCodecs modules.
        exts.append(Extension('_multibytecodec',
                              ['cjkcodecs/multibytecodec.c']))
        dla loc w ('kr', 'jp', 'cn', 'tw', 'hk', 'iso2022'):
            exts.append(Extension('_codecs_%s' % loc,
                                  ['cjkcodecs/_codecs_%s.c' % loc]))

        # Stefan Krah's _decimal module
        exts.append(self._decimal_ext())

        # Thomas Heller's _ctypes module
        self.detect_ctypes(inc_dirs, lib_dirs)

        # Richard Oudkerk's multiprocessing module
        jeżeli host_platform == 'win32':        # Windows
            macros = dict()
            libraries = ['ws2_32']

        albo_inaczej host_platform == 'darwin':     # Mac OSX
            macros = dict()
            libraries = []

        albo_inaczej host_platform == 'cygwin':     # Cygwin
            macros = dict()
            libraries = []

        albo_inaczej host_platform w ('freebsd4', 'freebsd5', 'freebsd6', 'freebsd7', 'freebsd8'):
            # FreeBSD's P1003.1b semaphore support jest very experimental
            # oraz has many known problems. (as of June 2008)
            macros = dict()
            libraries = []

        albo_inaczej host_platform.startswith('openbsd'):
            macros = dict()
            libraries = []

        albo_inaczej host_platform.startswith('netbsd'):
            macros = dict()
            libraries = []

        inaczej:                                   # Linux oraz other unices
            macros = dict()
            libraries = ['rt']

        jeżeli host_platform == 'win32':
            multiprocessing_srcs = [ '_multiprocessing/multiprocessing.c',
                                     '_multiprocessing/semaphore.c',
                                   ]

        inaczej:
            multiprocessing_srcs = [ '_multiprocessing/multiprocessing.c',
                                   ]
            jeżeli (sysconfig.get_config_var('HAVE_SEM_OPEN') oraz nie
                sysconfig.get_config_var('POSIX_SEMAPHORES_NOT_ENABLED')):
                multiprocessing_srcs.append('_multiprocessing/semaphore.c')

        jeżeli sysconfig.get_config_var('WITH_THREAD'):
            exts.append ( Extension('_multiprocessing', multiprocessing_srcs,
                                    define_macros=list(macros.items()),
                                    include_dirs=["Modules/_multiprocessing"]))
        inaczej:
            missing.append('_multiprocessing')
        # End multiprocessing

        # Platform-specific libraries
        jeżeli host_platform.startswith(('linux', 'freebsd', 'gnukfreebsd')):
            exts.append( Extension('ossaudiodev', ['ossaudiodev.c']) )
        inaczej:
            missing.append('ossaudiodev')

        jeżeli host_platform == 'darwin':
            exts.append(
                       Extension('_scproxy', ['_scproxy.c'],
                       extra_link_args=[
                           '-framework', 'SystemConfiguration',
                           '-framework', 'CoreFoundation',
                        ]))

        self.extensions.extend(exts)

        # Call the method dla detecting whether _tkinter can be compiled
        self.detect_tkinter(inc_dirs, lib_dirs)

        jeżeli '_tkinter' nie w [e.name dla e w self.extensions]:
            missing.append('_tkinter')

##         # Uncomment these lines jeżeli you want to play przy xxmodule.c
##         ext = Extension('xx', ['xxmodule.c'])
##         self.extensions.append(ext)

        jeżeli 'd' nie w sys.abiflags:
            ext = Extension('xxlimited', ['xxlimited.c'],
                            define_macros=[('Py_LIMITED_API', '0x03050000')])
            self.extensions.append(ext)

        zwróć missing

    def detect_tkinter_explicitly(self):
        # Build _tkinter using explicit locations dla Tcl/Tk.
        #
        # This jest enabled when both arguments are given to ./configure:
        #
        #     --with-tcltk-includes="-I/path/to/tclincludes \
        #                            -I/path/to/tkincludes"
        #     --with-tcltk-libs="-L/path/to/tcllibs -ltclm.n \
        #                        -L/path/to/tklibs -ltkm.n"
        #
        # These values can also be specified albo overriden via make:
        #    make TCLTK_INCLUDES="..." TCLTK_LIBS="..."
        #
        # This can be useful dla building oraz testing tkinter przy multiple
        # versions of Tcl/Tk.  Note that a build of Tk depends on a particular
        # build of Tcl so you need to specify both arguments oraz use care when
        # overriding.

        # The _TCLTK variables are created w the Makefile sharedmods target.
        tcltk_includes = os.environ.get('_TCLTK_INCLUDES')
        tcltk_libs = os.environ.get('_TCLTK_LIBS')
        jeżeli nie (tcltk_includes oraz tcltk_libs):
            # Resume default configuration search.
            zwróć 0

        extra_compile_args = tcltk_includes.split()
        extra_link_args = tcltk_libs.split()
        ext = Extension('_tkinter', ['_tkinter.c', 'tkappinit.c'],
                        define_macros=[('WITH_APPINIT', 1)],
                        extra_compile_args = extra_compile_args,
                        extra_link_args = extra_link_args,
                        )
        self.extensions.append(ext)
        zwróć 1

    def detect_tkinter_darwin(self, inc_dirs, lib_dirs):
        # The _tkinter module, using frameworks. Since frameworks are quite
        # different the UNIX search logic jest nie sharable.
        z os.path zaimportuj join, exists
        framework_dirs = [
            '/Library/Frameworks',
            '/System/Library/Frameworks/',
            join(os.getenv('HOME'), '/Library/Frameworks')
        ]

        sysroot = macosx_sdk_root()

        # Find the directory that contains the Tcl.framework oraz Tk.framework
        # bundles.
        # XXX distutils should support -F!
        dla F w framework_dirs:
            # both Tcl.framework oraz Tk.framework should be present


            dla fw w 'Tcl', 'Tk':
                jeżeli is_macosx_sdk_path(F):
                    jeżeli nie exists(join(sysroot, F[1:], fw + '.framework')):
                        przerwij
                inaczej:
                    jeżeli nie exists(join(F, fw + '.framework')):
                        przerwij
            inaczej:
                # ok, F jest now directory przy both frameworks. Continure
                # building
                przerwij
        inaczej:
            # Tk oraz Tcl frameworks nie found. Normal "unix" tkinter search
            # will now resume.
            zwróć 0

        # For 8.4a2, we must add -I options that point inside the Tcl oraz Tk
        # frameworks. In later release we should hopefully be able to dalej
        # the -F option to gcc, which specifies a framework lookup path.
        #
        include_dirs = [
            join(F, fw + '.framework', H)
            dla fw w ('Tcl', 'Tk')
            dla H w ('Headers', 'Versions/Current/PrivateHeaders')
        ]

        # For 8.4a2, the X11 headers are nie included. Rather than include a
        # complicated search, this jest a hard-coded path. It could bail out
        # jeżeli X11 libs are nie found...
        include_dirs.append('/usr/X11R6/include')
        frameworks = ['-framework', 'Tcl', '-framework', 'Tk']

        # All existing framework builds of Tcl/Tk don't support 64-bit
        # architectures.
        cflags = sysconfig.get_config_vars('CFLAGS')[0]
        archs = re.findall('-arch\s+(\w+)', cflags)

        tmpfile = os.path.join(self.build_temp, 'tk.arch')
        jeżeli nie os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # Note: cannot use os.popen albo subprocess here, that
        # requires extensions that are nie available here.
        jeżeli is_macosx_sdk_path(F):
            os.system("file %s/Tk.framework/Tk | grep 'dla architecture' > %s"%(os.path.join(sysroot, F[1:]), tmpfile))
        inaczej:
            os.system("file %s/Tk.framework/Tk | grep 'dla architecture' > %s"%(F, tmpfile))

        przy open(tmpfile) jako fp:
            detected_archs = []
            dla ln w fp:
                a = ln.split()[-1]
                jeżeli a w archs:
                    detected_archs.append(ln.split()[-1])
        os.unlink(tmpfile)

        dla a w detected_archs:
            frameworks.append('-arch')
            frameworks.append(a)

        ext = Extension('_tkinter', ['_tkinter.c', 'tkappinit.c'],
                        define_macros=[('WITH_APPINIT', 1)],
                        include_dirs = include_dirs,
                        libraries = [],
                        extra_compile_args = frameworks[2:],
                        extra_link_args = frameworks,
                        )
        self.extensions.append(ext)
        zwróć 1

    def detect_tkinter(self, inc_dirs, lib_dirs):
        # The _tkinter module.

        # Check whether --with-tcltk-includes oraz --with-tcltk-libs were
        # configured albo dalejed into the make target.  If so, use these values
        # to build tkinter oraz bypass the searches dla Tcl oraz TK w standard
        # locations.
        jeżeli self.detect_tkinter_explicitly():
            zwróć

        # Rather than complicate the code below, detecting oraz building
        # AquaTk jest a separate method. Only one Tkinter will be built on
        # Darwin - either AquaTk, jeżeli it jest found, albo X11 based Tk.
        jeżeli (host_platform == 'darwin' oraz
            self.detect_tkinter_darwin(inc_dirs, lib_dirs)):
            zwróć

        # Assume we haven't found any of the libraries albo include files
        # The versions przy dots are used on Unix, oraz the versions without
        # dots on Windows, dla detection by cygwin.
        tcllib = tklib = tcl_includes = tk_includes = Nic
        dla version w ['8.6', '86', '8.5', '85', '8.4', '84', '8.3', '83',
                        '8.2', '82', '8.1', '81', '8.0', '80']:
            tklib = self.compiler.find_library_file(lib_dirs,
                                                        'tk' + version)
            tcllib = self.compiler.find_library_file(lib_dirs,
                                                         'tcl' + version)
            jeżeli tklib oraz tcllib:
                # Exit the loop when we've found the Tcl/Tk libraries
                przerwij

        # Now check dla the header files
        jeżeli tklib oraz tcllib:
            # Check dla the include files on Debian oraz {Free,Open}BSD, where
            # they're put w /usr/include/{tcl,tk}X.Y
            dotversion = version
            jeżeli '.' nie w dotversion oraz "bsd" w host_platform.lower():
                # OpenBSD oraz FreeBSD use Tcl/Tk library names like libtcl83.a,
                # but the include subdirs are named like .../include/tcl8.3.
                dotversion = dotversion[:-1] + '.' + dotversion[-1]
            tcl_include_sub = []
            tk_include_sub = []
            dla dir w inc_dirs:
                tcl_include_sub += [dir + os.sep + "tcl" + dotversion]
                tk_include_sub += [dir + os.sep + "tk" + dotversion]
            tk_include_sub += tcl_include_sub
            tcl_includes = find_file('tcl.h', inc_dirs, tcl_include_sub)
            tk_includes = find_file('tk.h', inc_dirs, tk_include_sub)

        jeżeli (tcllib jest Nic albo tklib jest Nic albo
            tcl_includes jest Nic albo tk_includes jest Nic):
            self.announce("INFO: Can't locate Tcl/Tk libs and/or headers", 2)
            zwróć

        # OK... everything seems to be present dla Tcl/Tk.

        include_dirs = [] ; libs = [] ; defs = [] ; added_lib_dirs = []
        dla dir w tcl_includes + tk_includes:
            jeżeli dir nie w include_dirs:
                include_dirs.append(dir)

        # Check dla various platform-specific directories
        jeżeli host_platform == 'sunos5':
            include_dirs.append('/usr/openwin/include')
            added_lib_dirs.append('/usr/openwin/lib')
        albo_inaczej os.path.exists('/usr/X11R6/include'):
            include_dirs.append('/usr/X11R6/include')
            added_lib_dirs.append('/usr/X11R6/lib64')
            added_lib_dirs.append('/usr/X11R6/lib')
        albo_inaczej os.path.exists('/usr/X11R5/include'):
            include_dirs.append('/usr/X11R5/include')
            added_lib_dirs.append('/usr/X11R5/lib')
        inaczej:
            # Assume default location dla X11
            include_dirs.append('/usr/X11/include')
            added_lib_dirs.append('/usr/X11/lib')

        # If Cygwin, then verify that X jest installed before proceeding
        jeżeli host_platform == 'cygwin':
            x11_inc = find_file('X11/Xlib.h', [], include_dirs)
            jeżeli x11_inc jest Nic:
                zwróć

        # Check dla BLT extension
        jeżeli self.compiler.find_library_file(lib_dirs + added_lib_dirs,
                                               'BLT8.0'):
            defs.append( ('WITH_BLT', 1) )
            libs.append('BLT8.0')
        albo_inaczej self.compiler.find_library_file(lib_dirs + added_lib_dirs,
                                                'BLT'):
            defs.append( ('WITH_BLT', 1) )
            libs.append('BLT')

        # Add the Tcl/Tk libraries
        libs.append('tk'+ version)
        libs.append('tcl'+ version)

        jeżeli host_platform w ['aix3', 'aix4']:
            libs.append('ld')

        # Finally, link przy the X11 libraries (nie appropriate on cygwin)
        jeżeli host_platform != "cygwin":
            libs.append('X11')

        ext = Extension('_tkinter', ['_tkinter.c', 'tkappinit.c'],
                        define_macros=[('WITH_APPINIT', 1)] + defs,
                        include_dirs = include_dirs,
                        libraries = libs,
                        library_dirs = added_lib_dirs,
                        )
        self.extensions.append(ext)

        # XXX handle these, but how to detect?
        # *** Uncomment oraz edit dla PIL (TkImaging) extension only:
        #       -DWITH_PIL -I../Extensions/Imaging/libImaging  tkImaging.c \
        # *** Uncomment oraz edit dla TOGL extension only:
        #       -DWITH_TOGL togl.c \
        # *** Uncomment these dla TOGL extension only:
        #       -lGL -lGLU -lXext -lXmu \

    def configure_ctypes_darwin(self, ext):
        # Darwin (OS X) uses preconfigured files, w
        # the Modules/_ctypes/libffi_osx directory.
        srcdir = sysconfig.get_config_var('srcdir')
        ffi_srcdir = os.path.abspath(os.path.join(srcdir, 'Modules',
                                                  '_ctypes', 'libffi_osx'))
        sources = [os.path.join(ffi_srcdir, p)
                   dla p w ['ffi.c',
                             'x86/darwin64.S',
                             'x86/x86-darwin.S',
                             'x86/x86-ffi_darwin.c',
                             'x86/x86-ffi64.c',
                             'powerpc/ppc-darwin.S',
                             'powerpc/ppc-darwin_closure.S',
                             'powerpc/ppc-ffi_darwin.c',
                             'powerpc/ppc64-darwin_closure.S',
                             ]]

        # Add .S (preprocessed assembly) to C compiler source extensions.
        self.compiler.src_extensions.append('.S')

        include_dirs = [os.path.join(ffi_srcdir, 'include'),
                        os.path.join(ffi_srcdir, 'powerpc')]
        ext.include_dirs.extend(include_dirs)
        ext.sources.extend(sources)
        zwróć Prawda

    def configure_ctypes(self, ext):
        jeżeli nie self.use_system_libffi:
            jeżeli host_platform == 'darwin':
                zwróć self.configure_ctypes_darwin(ext)

            srcdir = sysconfig.get_config_var('srcdir')
            ffi_builddir = os.path.join(self.build_temp, 'libffi')
            ffi_srcdir = os.path.abspath(os.path.join(srcdir, 'Modules',
                                         '_ctypes', 'libffi'))
            ffi_configfile = os.path.join(ffi_builddir, 'fficonfig.py')

            z distutils.dep_util zaimportuj newer_group

            config_sources = [os.path.join(ffi_srcdir, fname)
                              dla fname w os.listdir(ffi_srcdir)
                              jeżeli os.path.isfile(os.path.join(ffi_srcdir, fname))]
            jeżeli self.force albo newer_group(config_sources,
                                         ffi_configfile):
                z distutils.dir_util zaimportuj mkpath
                mkpath(ffi_builddir)
                config_args = [arg dla arg w sysconfig.get_config_var("CONFIG_ARGS").split()
                               jeżeli (('--host=' w arg) albo ('--build=' w arg))]
                jeżeli nie self.verbose:
                    config_args.append("-q")

                # Pass empty CFLAGS because we'll just append the resulting
                # CFLAGS to Python's; -g albo -O2 jest to be avoided.
                cmd = "cd %s && env CFLAGS='' '%s/configure' %s" \
                      % (ffi_builddir, ffi_srcdir, " ".join(config_args))

                res = os.system(cmd)
                jeżeli res albo nie os.path.exists(ffi_configfile):
                    print("Failed to configure _ctypes module")
                    zwróć Nieprawda

            fficonfig = {}
            przy open(ffi_configfile) jako f:
                exec(f.read(), globals(), fficonfig)

            # Add .S (preprocessed assembly) to C compiler source extensions.
            self.compiler.src_extensions.append('.S')

            include_dirs = [os.path.join(ffi_builddir, 'include'),
                            ffi_builddir,
                            os.path.join(ffi_srcdir, 'src')]
            extra_compile_args = fficonfig['ffi_cflags'].split()

            ext.sources.extend(os.path.join(ffi_srcdir, f) dla f w
                               fficonfig['ffi_sources'])
            ext.include_dirs.extend(include_dirs)
            ext.extra_compile_args.extend(extra_compile_args)
        zwróć Prawda

    def detect_ctypes(self, inc_dirs, lib_dirs):
        self.use_system_libffi = Nieprawda
        include_dirs = []
        extra_compile_args = []
        extra_link_args = []
        sources = ['_ctypes/_ctypes.c',
                   '_ctypes/callbacks.c',
                   '_ctypes/callproc.c',
                   '_ctypes/stgdict.c',
                   '_ctypes/cfield.c']
        depends = ['_ctypes/ctypes.h']

        jeżeli host_platform == 'darwin':
            sources.append('_ctypes/malloc_closure.c')
            sources.append('_ctypes/darwin/dlfcn_simple.c')
            extra_compile_args.append('-DMACOSX')
            include_dirs.append('_ctypes/darwin')
# XXX Is this still needed?
##            extra_link_args.extend(['-read_only_relocs', 'warning'])

        albo_inaczej host_platform == 'sunos5':
            # XXX This shouldn't be necessary; it appears that some
            # of the assembler code jest non-PIC (i.e. it has relocations
            # when it shouldn't. The proper fix would be to rewrite
            # the assembler code to be PIC.
            # This only works przy GCC; the Sun compiler likely refuses
            # this option. If you want to compile ctypes przy the Sun
            # compiler, please research a proper solution, instead of
            # finding some -z option dla the Sun compiler.
            extra_link_args.append('-mimpure-text')

        albo_inaczej host_platform.startswith('hp-ux'):
            extra_link_args.append('-fPIC')

        ext = Extension('_ctypes',
                        include_dirs=include_dirs,
                        extra_compile_args=extra_compile_args,
                        extra_link_args=extra_link_args,
                        libraries=[],
                        sources=sources,
                        depends=depends)
        ext_test = Extension('_ctypes_test',
                             sources=['_ctypes/_ctypes_test.c'])
        self.extensions.extend([ext, ext_test])

        jeżeli nie '--with-system-ffi' w sysconfig.get_config_var("CONFIG_ARGS"):
            zwróć

        jeżeli host_platform == 'darwin':
            # OS X 10.5 comes przy libffi.dylib; the include files are
            # w /usr/include/ffi
            inc_dirs.append('/usr/include/ffi')

        ffi_inc = [sysconfig.get_config_var("LIBFFI_INCLUDEDIR")]
        jeżeli nie ffi_inc albo ffi_inc[0] == '':
            ffi_inc = find_file('ffi.h', [], inc_dirs)
        jeżeli ffi_inc jest nie Nic:
            ffi_h = ffi_inc[0] + '/ffi.h'
            przy open(ffi_h) jako fp:
                dopóki 1:
                    line = fp.readline()
                    jeżeli nie line:
                        ffi_inc = Nic
                        przerwij
                    jeżeli line.startswith('#define LIBFFI_H'):
                        przerwij
        ffi_lib = Nic
        jeżeli ffi_inc jest nie Nic:
            dla lib_name w ('ffi_convenience', 'ffi_pic', 'ffi'):
                jeżeli (self.compiler.find_library_file(lib_dirs, lib_name)):
                    ffi_lib = lib_name
                    przerwij

        jeżeli ffi_inc oraz ffi_lib:
            ext.include_dirs.extend(ffi_inc)
            ext.libraries.append(ffi_lib)
            self.use_system_libffi = Prawda

    def _decimal_ext(self):
        extra_compile_args = []
        undef_macros = []
        jeżeli '--with-system-libmpdec' w sysconfig.get_config_var("CONFIG_ARGS"):
            include_dirs = []
            libraries = [':libmpdec.so.2']
            sources = ['_decimal/_decimal.c']
            depends = ['_decimal/docstrings.h']
        inaczej:
            srcdir = sysconfig.get_config_var('srcdir')
            include_dirs = [os.path.abspath(os.path.join(srcdir,
                                                         'Modules',
                                                         '_decimal',
                                                         'libmpdec'))]
            libraries = []
            sources = [
              '_decimal/_decimal.c',
              '_decimal/libmpdec/basearith.c',
              '_decimal/libmpdec/constants.c',
              '_decimal/libmpdec/context.c',
              '_decimal/libmpdec/convolute.c',
              '_decimal/libmpdec/crt.c',
              '_decimal/libmpdec/difradix2.c',
              '_decimal/libmpdec/fnt.c',
              '_decimal/libmpdec/fourstep.c',
              '_decimal/libmpdec/io.c',
              '_decimal/libmpdec/memory.c',
              '_decimal/libmpdec/mpdecimal.c',
              '_decimal/libmpdec/numbertheory.c',
              '_decimal/libmpdec/sixstep.c',
              '_decimal/libmpdec/transpose.c',
              ]
            depends = [
              '_decimal/docstrings.h',
              '_decimal/libmpdec/basearith.h',
              '_decimal/libmpdec/bits.h',
              '_decimal/libmpdec/constants.h',
              '_decimal/libmpdec/convolute.h',
              '_decimal/libmpdec/crt.h',
              '_decimal/libmpdec/difradix2.h',
              '_decimal/libmpdec/fnt.h',
              '_decimal/libmpdec/fourstep.h',
              '_decimal/libmpdec/io.h',
              '_decimal/libmpdec/memory.h',
              '_decimal/libmpdec/mpdecimal.h',
              '_decimal/libmpdec/numbertheory.h',
              '_decimal/libmpdec/sixstep.h',
              '_decimal/libmpdec/transpose.h',
              '_decimal/libmpdec/typearith.h',
              '_decimal/libmpdec/umodarith.h',
              ]

        config = {
          'x64':     [('CONFIG_64','1'), ('ASM','1')],
          'uint128': [('CONFIG_64','1'), ('ANSI','1'), ('HAVE_UINT128_T','1')],
          'ansi64':  [('CONFIG_64','1'), ('ANSI','1')],
          'ppro':    [('CONFIG_32','1'), ('PPRO','1'), ('ASM','1')],
          'ansi32':  [('CONFIG_32','1'), ('ANSI','1')],
          'ansi-legacy': [('CONFIG_32','1'), ('ANSI','1'),
                          ('LEGACY_COMPILER','1')],
          'universal':   [('UNIVERSAL','1')]
        }

        cc = sysconfig.get_config_var('CC')
        sizeof_size_t = sysconfig.get_config_var('SIZEOF_SIZE_T')
        machine = os.environ.get('PYTHON_DECIMAL_WITH_MACHINE')

        jeżeli machine:
            # Override automatic configuration to facilitate testing.
            define_macros = config[machine]
        albo_inaczej host_platform == 'darwin':
            # Universal here means: build przy the same options Python
            # was built with.
            define_macros = config['universal']
        albo_inaczej sizeof_size_t == 8:
            jeżeli sysconfig.get_config_var('HAVE_GCC_ASM_FOR_X64'):
                define_macros = config['x64']
            albo_inaczej sysconfig.get_config_var('HAVE_GCC_UINT128_T'):
                define_macros = config['uint128']
            inaczej:
                define_macros = config['ansi64']
        albo_inaczej sizeof_size_t == 4:
            ppro = sysconfig.get_config_var('HAVE_GCC_ASM_FOR_X87')
            jeżeli ppro oraz ('gcc' w cc albo 'clang' w cc) oraz \
               nie 'sunos' w host_platform:
                # solaris: problems przy register allocation.
                # icc >= 11.0 works jako well.
                define_macros = config['ppro']
                extra_compile_args.append('-Wno-unknown-pragmas')
            inaczej:
                define_macros = config['ansi32']
        inaczej:
            podnieś DistutilsError("_decimal: unsupported architecture")

        # Workarounds dla toolchain bugs:
        jeżeli sysconfig.get_config_var('HAVE_IPA_PURE_CONST_BUG'):
            # Some versions of gcc miscompile inline asm:
            # http://gcc.gnu.org/bugzilla/show_bug.cgi?id=46491
            # http://gcc.gnu.org/ml/gcc/2010-11/msg00366.html
            extra_compile_args.append('-fno-ipa-pure-const')
        jeżeli sysconfig.get_config_var('HAVE_GLIBC_MEMMOVE_BUG'):
            # _FORTIFY_SOURCE wrappers dla memmove oraz bcopy are incorrect:
            # http://sourceware.org/ml/libc-alpha/2010-12/msg00009.html
            undef_macros.append('_FORTIFY_SOURCE')

        # Faster version without thread local contexts:
        jeżeli nie sysconfig.get_config_var('WITH_THREAD'):
            define_macros.append(('WITHOUT_THREADS', 1))

        # Increase warning level dla gcc:
        jeżeli 'gcc' w cc:
            cmd = ("echo '' | %s -Wextra -Wno-missing-field-initializers -E - "
                   "> /dev/null 2>&1" % cc)
            ret = os.system(cmd)
            jeżeli ret >> 8 == 0:
                extra_compile_args.extend(['-Wextra',
                                           '-Wno-missing-field-initializers'])

        # Uncomment dla extra functionality:
        #define_macros.append(('EXTRA_FUNCTIONALITY', 1))
        ext = Extension (
            '_decimal',
            include_dirs=include_dirs,
            libraries=libraries,
            define_macros=define_macros,
            undef_macros=undef_macros,
            extra_compile_args=extra_compile_args,
            sources=sources,
            depends=depends
        )
        zwróć ext

klasa PyBuildInstall(install):
    # Suppress the warning about installation into the lib_dynload
    # directory, which jest nie w sys.path when running Python during
    # installation:
    def initialize_options (self):
        install.initialize_options(self)
        self.warn_dir=0

    # Customize subcommands to nie install an egg-info file dla Python
    sub_commands = [('install_lib', install.has_lib),
                    ('install_headers', install.has_headers),
                    ('install_scripts', install.has_scripts),
                    ('install_data', install.has_data)]


klasa PyBuildInstallLib(install_lib):
    # Do exactly what install_lib does but make sure correct access modes get
    # set on installed directories oraz files. All installed files przy get
    # mode 644 unless they are a shared library w which case they will get
    # mode 755. All installed directories will get mode 755.

    # this jest works dla EXT_SUFFIX too, which ends przy SHLIB_SUFFIX
    shlib_suffix = sysconfig.get_config_var("SHLIB_SUFFIX")

    def install(self):
        outfiles = install_lib.install(self)
        self.set_file_modes(outfiles, 0o644, 0o755)
        self.set_dir_modes(self.install_dir, 0o755)
        zwróć outfiles

    def set_file_modes(self, files, defaultMode, sharedLibMode):
        jeżeli nie self.is_chmod_supported(): zwróć
        jeżeli nie files: zwróć

        dla filename w files:
            jeżeli os.path.islink(filename): kontynuuj
            mode = defaultMode
            jeżeli filename.endswith(self.shlib_suffix): mode = sharedLibMode
            log.info("changing mode of %s to %o", filename, mode)
            jeżeli nie self.dry_run: os.chmod(filename, mode)

    def set_dir_modes(self, dirname, mode):
        jeżeli nie self.is_chmod_supported(): zwróć
        dla dirpath, dirnames, fnames w os.walk(dirname):
            jeżeli os.path.islink(dirpath):
                kontynuuj
            log.info("changing mode of %s to %o", dirpath, mode)
            jeżeli nie self.dry_run: os.chmod(dirpath, mode)

    def is_chmod_supported(self):
        zwróć hasattr(os, 'chmod')

klasa PyBuildScripts(build_scripts):
    def copy_scripts(self):
        outfiles, updated_files = build_scripts.copy_scripts(self)
        fullversion = '-{0[0]}.{0[1]}'.format(sys.version_info)
        minoronly = '.{0[1]}'.format(sys.version_info)
        newoutfiles = []
        newupdated_files = []
        dla filename w outfiles:
            jeżeli filename.endswith(('2to3', 'pyvenv')):
                newfilename = filename + fullversion
            inaczej:
                newfilename = filename + minoronly
            log.info('renaming {} to {}'.format(filename, newfilename))
            os.rename(filename, newfilename)
            newoutfiles.append(newfilename)
            jeżeli filename w updated_files:
                newupdated_files.append(newfilename)
        zwróć newoutfiles, newupdated_files

SUMMARY = """
Python jest an interpreted, interactive, object-oriented programming
language. It jest often compared to Tcl, Perl, Scheme albo Java.

Python combines remarkable power przy very clear syntax. It has
modules, classes, exceptions, very high level dynamic data types, oraz
dynamic typing. There are interfaces to many system calls oraz
libraries, jako well jako to various windowing systems (X11, Motif, Tk,
Mac, MFC). New built-in modules are easily written w C albo C++. Python
is also usable jako an extension language dla applications that need a
programmable interface.

The Python implementation jest portable: it runs on many brands of UNIX,
on Windows, DOS, Mac, Amiga... If your favorite system isn't
listed here, it may still be supported, jeżeli there's a C compiler for
it. Ask around on comp.lang.python -- albo just try compiling Python
yourself.
"""

CLASSIFIERS = """
Development Status :: 6 - Mature
License :: OSI Approved :: Python Software Foundation License
Natural Language :: English
Programming Language :: C
Programming Language :: Python
Topic :: Software Development
"""

def main():
    # turn off warnings when deprecated modules are imported
    zaimportuj warnings
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    setup(# PyPI Metadata (PEP 301)
          name = "Python",
          version = sys.version.split()[0],
          url = "http://www.python.org/%s" % sys.version[:3],
          maintainer = "Guido van Rossum oraz the Python community",
          maintainer_email = "python-dev@python.org",
          description = "A high-level object-oriented programming language",
          long_description = SUMMARY.strip(),
          license = "PSF license",
          classifiers = [x dla x w CLASSIFIERS.split("\n") jeżeli x],
          platforms = ["Many"],

          # Build info
          cmdclass = {'build_ext': PyBuildExt,
                      'build_scripts': PyBuildScripts,
                      'install': PyBuildInstall,
                      'install_lib': PyBuildInstallLib},
          # The struct module jest defined here, because build_ext won't be
          # called unless there's at least one extension module defined.
          ext_modules=[Extension('_struct', ['_struct.c'])],

          # If you change the scripts installed here, you also need to
          # check the PyBuildScripts command above, oraz change the links
          # created by the bininstall target w Makefile.pre.in
          scripts = ["Tools/scripts/pydoc3", "Tools/scripts/idle3",
                    "Tools/scripts/2to3", "Tools/scripts/pyvenv"]
        )

# --install-platlib
jeżeli __name__ == '__main__':
    main()
