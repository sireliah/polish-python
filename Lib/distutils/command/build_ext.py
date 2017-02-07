"""distutils.command.build_ext

Implements the Distutils 'build_ext' command, dla building extension
modules (currently limited to C extensions, should accommodate C++
extensions ASAP)."""

zaimportuj contextlib
zaimportuj os
zaimportuj re
zaimportuj sys
z distutils.core zaimportuj Command
z distutils.errors zaimportuj *
z distutils.sysconfig zaimportuj customize_compiler, get_python_version
z distutils.sysconfig zaimportuj get_config_h_filename
z distutils.dep_util zaimportuj newer_group
z distutils.extension zaimportuj Extension
z distutils.util zaimportuj get_platform
z distutils zaimportuj log

z site zaimportuj USER_BASE

# An extension name jest just a dot-separated list of Python NAMEs (ie.
# the same jako a fully-qualified module name).
extension_name_re = re.compile \
    (r'^[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_][a-zA-Z_0-9]*)*$')


def show_compilers ():
    z distutils.ccompiler zaimportuj show_compilers
    show_compilers()


klasa build_ext(Command):

    description = "build C/C++ extensions (compile/link to build directory)"

    # XXX thoughts on how to deal przy complex command-line options like
    # these, i.e. how to make it so fancy_getopt can suck them off the
    # command line oraz make it look like setup.py defined the appropriate
    # lists of tuples of what-have-you.
    #   - each command needs a callback to process its command-line options
    #   - Command.__init__() needs access to its share of the whole
    #     command line (must ultimately come from
    #     Distribution.parse_command_line())
    #   - it then calls the current command class' option-parsing
    #     callback to deal przy weird options like -D, which have to
    #     parse the option text oraz churn out some custom data
    #     structure
    #   - that data structure (in this case, a list of 2-tuples)
    #     will then be present w the command object by the time
    #     we get to finalize_options() (i.e. the constructor
    #     takes care of both command-line oraz client options
    #     w between initialize_options() oraz finalize_options())

    sep_by = " (separated by '%s')" % os.pathsep
    user_options = [
        ('build-lib=', 'b',
         "directory dla compiled extension modules"),
        ('build-temp=', 't',
         "directory dla temporary files (build by-products)"),
        ('plat-name=', 'p',
         "platform name to cross-compile for, jeżeli supported "
         "(default: %s)" % get_platform()),
        ('inplace', 'i',
         "ignore build-lib oraz put compiled extensions into the source " +
         "directory alongside your pure Python modules"),
        ('include-dirs=', 'I',
         "list of directories to search dla header files" + sep_by),
        ('define=', 'D',
         "C preprocessor macros to define"),
        ('undef=', 'U',
         "C preprocessor macros to undefine"),
        ('libraries=', 'l',
         "external C libraries to link with"),
        ('library-dirs=', 'L',
         "directories to search dla external C libraries" + sep_by),
        ('rpath=', 'R',
         "directories to search dla shared C libraries at runtime"),
        ('link-objects=', 'O',
         "extra explicit link objects to include w the link"),
        ('debug', 'g',
         "compile/link przy debugging information"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
        ('compiler=', 'c',
         "specify the compiler type"),
        ('parallel=', 'j',
         "number of parallel build jobs"),
        ('swig-cpp', Nic,
         "make SWIG create C++ files (default jest C)"),
        ('swig-opts=', Nic,
         "list of SWIG command line options"),
        ('swig=', Nic,
         "path to the SWIG executable"),
        ('user', Nic,
         "add user include, library oraz rpath")
        ]

    boolean_options = ['inplace', 'debug', 'force', 'swig-cpp', 'user']

    help_options = [
        ('help-compiler', Nic,
         "list available compilers", show_compilers),
        ]

    def initialize_options(self):
        self.extensions = Nic
        self.build_lib = Nic
        self.plat_name = Nic
        self.build_temp = Nic
        self.inplace = 0
        self.package = Nic

        self.include_dirs = Nic
        self.define = Nic
        self.undef = Nic
        self.libraries = Nic
        self.library_dirs = Nic
        self.rpath = Nic
        self.link_objects = Nic
        self.debug = Nic
        self.force = Nic
        self.compiler = Nic
        self.swig = Nic
        self.swig_cpp = Nic
        self.swig_opts = Nic
        self.user = Nic
        self.parallel = Nic

    def finalize_options(self):
        z distutils zaimportuj sysconfig

        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'),
                                   ('build_temp', 'build_temp'),
                                   ('compiler', 'compiler'),
                                   ('debug', 'debug'),
                                   ('force', 'force'),
                                   ('parallel', 'parallel'),
                                   ('plat_name', 'plat_name'),
                                   )

        jeżeli self.package jest Nic:
            self.package = self.distribution.ext_package

        self.extensions = self.distribution.ext_modules

        # Make sure Python's include directories (dla Python.h, pyconfig.h,
        # etc.) are w the include search path.
        py_include = sysconfig.get_python_inc()
        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        jeżeli self.include_dirs jest Nic:
            self.include_dirs = self.distribution.include_dirs albo []
        jeżeli isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        # If w a virtualenv, add its include directory
        # Issue 16116
        jeżeli sys.exec_prefix != sys.base_exec_prefix:
            self.include_dirs.append(os.path.join(sys.exec_prefix, 'include'))

        # Put the Python "system" include dir at the end, so that
        # any local include dirs take precedence.
        self.include_dirs.append(py_include)
        jeżeli plat_py_include != py_include:
            self.include_dirs.append(plat_py_include)

        self.ensure_string_list('libraries')

        # Life jest easier jeżeli we're nie forever checking dla Nic, so
        # simplify these options to empty lists jeżeli unset
        jeżeli self.libraries jest Nic:
            self.libraries = []
        jeżeli self.library_dirs jest Nic:
            self.library_dirs = []
        albo_inaczej isinstance(self.library_dirs, str):
            self.library_dirs = self.library_dirs.split(os.pathsep)

        jeżeli self.rpath jest Nic:
            self.rpath = []
        albo_inaczej isinstance(self.rpath, str):
            self.rpath = self.rpath.split(os.pathsep)

        # dla extensions under windows use different directories
        # dla Release oraz Debug builds.
        # also Python's library directory must be appended to library_dirs
        jeżeli os.name == 'nt':
            # the 'libs' directory jest dla binary installs - we assume that
            # must be the *native* platform.  But we don't really support
            # cross-compiling via a binary install anyway, so we let it go.
            self.library_dirs.append(os.path.join(sys.exec_prefix, 'libs'))
            jeżeli sys.base_exec_prefix != sys.prefix:  # Issue 16116
                self.library_dirs.append(os.path.join(sys.base_exec_prefix, 'libs'))
            jeżeli self.debug:
                self.build_temp = os.path.join(self.build_temp, "Debug")
            inaczej:
                self.build_temp = os.path.join(self.build_temp, "Release")

            # Append the source distribution include oraz library directories,
            # this allows distutils on windows to work w the source tree
            self.include_dirs.append(os.path.dirname(get_config_h_filename()))
            _sys_home = getattr(sys, '_home', Nic)
            jeżeli _sys_home:
                self.library_dirs.append(_sys_home)

            # Use the .lib files dla the correct architecture
            jeżeli self.plat_name == 'win32':
                suffix = 'win32'
            inaczej:
                # win-amd64 albo win-ia64
                suffix = self.plat_name[4:]
            new_lib = os.path.join(sys.exec_prefix, 'PCbuild')
            jeżeli suffix:
                new_lib = os.path.join(new_lib, suffix)
            self.library_dirs.append(new_lib)

        # dla extensions under Cygwin oraz AtheOS Python's library directory must be
        # appended to library_dirs
        jeżeli sys.platform[:6] == 'cygwin' albo sys.platform[:6] == 'atheos':
            jeżeli sys.executable.startswith(os.path.join(sys.exec_prefix, "bin")):
                # building third party extensions
                self.library_dirs.append(os.path.join(sys.prefix, "lib",
                                                      "python" + get_python_version(),
                                                      "config"))
            inaczej:
                # building python standard extensions
                self.library_dirs.append('.')

        # For building extensions przy a shared Python library,
        # Python's library directory must be appended to library_dirs
        # See Issues: #1600860, #4366
        jeżeli (sysconfig.get_config_var('Py_ENABLE_SHARED')):
            jeżeli nie sysconfig.python_build:
                # building third party extensions
                self.library_dirs.append(sysconfig.get_config_var('LIBDIR'))
            inaczej:
                # building python standard extensions
                self.library_dirs.append('.')

        # The argument parsing will result w self.define being a string, but
        # it has to be a list of 2-tuples.  All the preprocessor symbols
        # specified by the 'define' option will be set to '1'.  Multiple
        # symbols can be separated przy commas.

        jeżeli self.define:
            defines = self.define.split(',')
            self.define = [(symbol, '1') dla symbol w defines]

        # The option dla macros to undefine jest also a string z the
        # option parsing, but has to be a list.  Multiple symbols can also
        # be separated przy commas here.
        jeżeli self.undef:
            self.undef = self.undef.split(',')

        jeżeli self.swig_opts jest Nic:
            self.swig_opts = []
        inaczej:
            self.swig_opts = self.swig_opts.split(' ')

        # Finally add the user include oraz library directories jeżeli requested
        jeżeli self.user:
            user_include = os.path.join(USER_BASE, "include")
            user_lib = os.path.join(USER_BASE, "lib")
            jeżeli os.path.isdir(user_include):
                self.include_dirs.append(user_include)
            jeżeli os.path.isdir(user_lib):
                self.library_dirs.append(user_lib)
                self.rpath.append(user_lib)

        jeżeli isinstance(self.parallel, str):
            spróbuj:
                self.parallel = int(self.parallel)
            wyjąwszy ValueError:
                podnieś DistutilsOptionError("parallel should be an integer")

    def run(self):
        z distutils.ccompiler zaimportuj new_compiler

        # 'self.extensions', jako supplied by setup.py, jest a list of
        # Extension instances.  See the documentation dla Extension (in
        # distutils.extension) dla details.
        #
        # For backwards compatibility przy Distutils 0.8.2 oraz earlier, we
        # also allow the 'extensions' list to be a list of tuples:
        #    (ext_name, build_info)
        # where build_info jest a dictionary containing everything that
        # Extension instances do wyjąwszy the name, przy a few things being
        # differently named.  We convert these 2-tuples to Extension
        # instances jako needed.

        jeżeli nie self.extensions:
            zwróć

        # If we were asked to build any C/C++ libraries, make sure that the
        # directory where we put them jest w the library search path for
        # linking extensions.
        jeżeli self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command('build_clib')
            self.libraries.extend(build_clib.get_library_names() albo [])
            self.library_dirs.append(build_clib.build_clib)

        # Setup the CCompiler object that we'll use to do all the
        # compiling oraz linking
        self.compiler = new_compiler(compiler=self.compiler,
                                     verbose=self.verbose,
                                     dry_run=self.dry_run,
                                     force=self.force)
        customize_compiler(self.compiler)
        # If we are cross-compiling, init the compiler now (jeżeli we are nie
        # cross-compiling, init would nie hurt, but people may rely on
        # late initialization of compiler even jeżeli they shouldn't...)
        jeżeli os.name == 'nt' oraz self.plat_name != get_platform():
            self.compiler.initialize(self.plat_name)

        # And make sure that any compile/link-related options (which might
        # come z the command-line albo z the setup script) are set w
        # that CCompiler object -- that way, they automatically apply to
        # all compiling oraz linking done here.
        jeżeli self.include_dirs jest nie Nic:
            self.compiler.set_include_dirs(self.include_dirs)
        jeżeli self.define jest nie Nic:
            # 'define' option jest a list of (name,value) tuples
            dla (name, value) w self.define:
                self.compiler.define_macro(name, value)
        jeżeli self.undef jest nie Nic:
            dla macro w self.undef:
                self.compiler.undefine_macro(macro)
        jeżeli self.libraries jest nie Nic:
            self.compiler.set_libraries(self.libraries)
        jeżeli self.library_dirs jest nie Nic:
            self.compiler.set_library_dirs(self.library_dirs)
        jeżeli self.rpath jest nie Nic:
            self.compiler.set_runtime_library_dirs(self.rpath)
        jeżeli self.link_objects jest nie Nic:
            self.compiler.set_link_objects(self.link_objects)

        # Now actually compile oraz link everything.
        self.build_extensions()

    def check_extensions_list(self, extensions):
        """Ensure that the list of extensions (presumably provided jako a
        command option 'extensions') jest valid, i.e. it jest a list of
        Extension objects.  We also support the old-style list of 2-tuples,
        where the tuples are (ext_name, build_info), which are converted to
        Extension instances here.

        Raise DistutilsSetupError jeżeli the structure jest invalid anywhere;
        just returns otherwise.
        """
        jeżeli nie isinstance(extensions, list):
            podnieś DistutilsSetupError(
                  "'ext_modules' option must be a list of Extension instances")

        dla i, ext w enumerate(extensions):
            jeżeli isinstance(ext, Extension):
                kontynuuj                # OK! (assume type-checking done
                                        # by Extension constructor)

            jeżeli nie isinstance(ext, tuple) albo len(ext) != 2:
                podnieś DistutilsSetupError(
                       "each element of 'ext_modules' option must be an "
                       "Extension instance albo 2-tuple")

            ext_name, build_info = ext

            log.warn(("old-style (ext_name, build_info) tuple found w "
                      "ext_modules dla extension '%s'"
                      "-- please convert to Extension instance" % ext_name))

            jeżeli nie (isinstance(ext_name, str) oraz
                    extension_name_re.match(ext_name)):
                podnieś DistutilsSetupError(
                       "first element of each tuple w 'ext_modules' "
                       "must be the extension name (a string)")

            jeżeli nie isinstance(build_info, dict):
                podnieś DistutilsSetupError(
                       "second element of each tuple w 'ext_modules' "
                       "must be a dictionary (build info)")

            # OK, the (ext_name, build_info) dict jest type-safe: convert it
            # to an Extension instance.
            ext = Extension(ext_name, build_info['sources'])

            # Easy stuff: one-to-one mapping z dict elements to
            # instance attributes.
            dla key w ('include_dirs', 'library_dirs', 'libraries',
                        'extra_objects', 'extra_compile_args',
                        'extra_link_args'):
                val = build_info.get(key)
                jeżeli val jest nie Nic:
                    setattr(ext, key, val)

            # Medium-easy stuff: same syntax/semantics, different names.
            ext.runtime_library_dirs = build_info.get('rpath')
            jeżeli 'def_file' w build_info:
                log.warn("'def_file' element of build info dict "
                         "no longer supported")

            # Non-trivial stuff: 'macros' split into 'define_macros'
            # oraz 'undef_macros'.
            macros = build_info.get('macros')
            jeżeli macros:
                ext.define_macros = []
                ext.undef_macros = []
                dla macro w macros:
                    jeżeli nie (isinstance(macro, tuple) oraz len(macro) w (1, 2)):
                        podnieś DistutilsSetupError(
                              "'macros' element of build info dict "
                              "must be 1- albo 2-tuple")
                    jeżeli len(macro) == 1:
                        ext.undef_macros.append(macro[0])
                    albo_inaczej len(macro) == 2:
                        ext.define_macros.append(macro)

            extensions[i] = ext

    def get_source_files(self):
        self.check_extensions_list(self.extensions)
        filenames = []

        # Wouldn't it be neat jeżeli we knew the names of header files too...
        dla ext w self.extensions:
            filenames.extend(ext.sources)
        zwróć filenames

    def get_outputs(self):
        # Sanity check the 'extensions' list -- can't assume this jest being
        # done w the same run jako a 'build_extensions()' call (in fact, we
        # can probably assume that it *isn't*!).
        self.check_extensions_list(self.extensions)

        # And build the list of output (built) filenames.  Note that this
        # ignores the 'inplace' flag, oraz assumes everything goes w the
        # "build" tree.
        outputs = []
        dla ext w self.extensions:
            outputs.append(self.get_ext_fullpath(ext.name))
        zwróć outputs

    def build_extensions(self):
        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)
        jeżeli self.parallel:
            self._build_extensions_parallel()
        inaczej:
            self._build_extensions_serial()

    def _build_extensions_parallel(self):
        workers = self.parallel
        jeżeli self.parallel jest Prawda:
            workers = os.cpu_count()  # may zwróć Nic
        spróbuj:
            z concurrent.futures zaimportuj ThreadPoolExecutor
        wyjąwszy ImportError:
            workers = Nic

        jeżeli workers jest Nic:
            self._build_extensions_serial()
            zwróć

        przy ThreadPoolExecutor(max_workers=workers) jako executor:
            futures = [executor.submit(self.build_extension, ext)
                       dla ext w self.extensions]
            dla ext, fut w zip(self.extensions, futures):
                przy self._filter_build_errors(ext):
                    fut.result()

    def _build_extensions_serial(self):
        #print(self.extensions)
        dla ext w self.extensions:
            przy self._filter_build_errors(ext):
                self.build_extension(ext)

    @contextlib.contextmanager
    def _filter_build_errors(self, ext):
        spróbuj:
            uzyskaj
        wyjąwszy (CCompilerError, DistutilsError, CompileError) jako e:
            jeżeli nie ext.optional:
                podnieś
            self.warn('building extension "%s" failed: %s' %
                      (ext.name, e))

    def build_extension(self, ext):
        sources = ext.sources
        jeżeli sources jest Nic albo nie isinstance(sources, (list, tuple)):
            podnieś DistutilsSetupError(
                  "in 'ext_modules' option (extension '%s'), "
                  "'sources' must be present oraz must be "
                  "a list of source filenames" % ext.name)
        sources = list(sources)

        ext_path = self.get_ext_fullpath(ext.name)
        depends = sources + ext.depends
        jeżeli nie (self.force albo newer_group(depends, ext_path, 'newer')):
            log.debug("skipping '%s' extension (up-to-date)", ext.name)
            zwróć
        inaczej:
            log.info("building '%s' extension", ext.name)

        # First, scan the sources dla SWIG definition files (.i), run
        # SWIG on 'em to create .c files, oraz modify the sources list
        # accordingly.
        sources = self.swig_sources(sources, ext)

        # Next, compile the source code to object files.

        # XXX nie honouring 'define_macros' albo 'undef_macros' -- the
        # CCompiler API needs to change to accommodate this, oraz I
        # want to do one thing at a time!

        # Two possible sources dla extra compiler arguments:
        #   - 'extra_compile_args' w Extension object
        #   - CFLAGS environment variable (nie particularly
        #     elegant, but people seem to expect it oraz I
        #     guess it's useful)
        # The environment variable should take precedence, oraz
        # any sensible compiler will give precedence to later
        # command line args.  Hence we combine them w order:
        extra_args = ext.extra_compile_args albo []

        macros = ext.define_macros[:]
        dla undef w ext.undef_macros:
            macros.append((undef,))

        objects = self.compiler.compile(sources,
                                         output_dir=self.build_temp,
                                         macros=macros,
                                         include_dirs=ext.include_dirs,
                                         debug=self.debug,
                                         extra_postargs=extra_args,
                                         depends=ext.depends)

        # XXX outdated variable, kept here w case third-part code
        # needs it.
        self._built_objects = objects[:]

        # Now link the object files together into a "shared object" --
        # of course, first we have to figure out all the other things
        # that go into the mix.
        jeżeli ext.extra_objects:
            objects.extend(ext.extra_objects)
        extra_args = ext.extra_link_args albo []

        # Detect target language, jeżeli nie provided
        language = ext.language albo self.compiler.detect_language(sources)

        self.compiler.link_shared_object(
            objects, ext_path,
            libraries=self.get_libraries(ext),
            library_dirs=ext.library_dirs,
            runtime_library_dirs=ext.runtime_library_dirs,
            extra_postargs=extra_args,
            export_symbols=self.get_export_symbols(ext),
            debug=self.debug,
            build_temp=self.build_temp,
            target_lang=language)

    def swig_sources(self, sources, extension):
        """Walk the list of source files w 'sources', looking dla SWIG
        interface (.i) files.  Run SWIG on all that are found, oraz
        zwróć a modified 'sources' list przy SWIG source files replaced
        by the generated C (or C++) files.
        """
        new_sources = []
        swig_sources = []
        swig_targets = {}

        # XXX this drops generated C/C++ files into the source tree, which
        # jest fine dla developers who want to distribute the generated
        # source -- but there should be an option to put SWIG output w
        # the temp dir.

        jeżeli self.swig_cpp:
            log.warn("--swig-cpp jest deprecated - use --swig-opts=-c++")

        jeżeli self.swig_cpp albo ('-c++' w self.swig_opts) albo \
           ('-c++' w extension.swig_opts):
            target_ext = '.cpp'
        inaczej:
            target_ext = '.c'

        dla source w sources:
            (base, ext) = os.path.splitext(source)
            jeżeli ext == ".i":             # SWIG interface file
                new_sources.append(base + '_wrap' + target_ext)
                swig_sources.append(source)
                swig_targets[source] = new_sources[-1]
            inaczej:
                new_sources.append(source)

        jeżeli nie swig_sources:
            zwróć new_sources

        swig = self.swig albo self.find_swig()
        swig_cmd = [swig, "-python"]
        swig_cmd.extend(self.swig_opts)
        jeżeli self.swig_cpp:
            swig_cmd.append("-c++")

        # Do nie override commandline arguments
        jeżeli nie self.swig_opts:
            dla o w extension.swig_opts:
                swig_cmd.append(o)

        dla source w swig_sources:
            target = swig_targets[source]
            log.info("swigging %s to %s", source, target)
            self.spawn(swig_cmd + ["-o", target, source])

        zwróć new_sources

    def find_swig(self):
        """Return the name of the SWIG executable.  On Unix, this jest
        just "swig" -- it should be w the PATH.  Tries a bit harder on
        Windows.
        """
        jeżeli os.name == "posix":
            zwróć "swig"
        albo_inaczej os.name == "nt":
            # Look dla SWIG w its standard installation directory on
            # Windows (or so I presume!).  If we find it there, great;
            # jeżeli not, act like Unix oraz assume it's w the PATH.
            dla vers w ("1.3", "1.2", "1.1"):
                fn = os.path.join("c:\\swig%s" % vers, "swig.exe")
                jeżeli os.path.isfile(fn):
                    zwróć fn
            inaczej:
                zwróć "swig.exe"
        inaczej:
            podnieś DistutilsPlatformError(
                  "I don't know how to find (much less run) SWIG "
                  "on platform '%s'" % os.name)

    # -- Name generators -----------------------------------------------
    # (extension names, filenames, whatever)
    def get_ext_fullpath(self, ext_name):
        """Returns the path of the filename dla a given extension.

        The file jest located w `build_lib` albo directly w the package
        (inplace option).
        """
        fullname = self.get_ext_fullname(ext_name)
        modpath = fullname.split('.')
        filename = self.get_ext_filename(modpath[-1])

        jeżeli nie self.inplace:
            # no further work needed
            # returning :
            #   build_dir/package/path/filename
            filename = os.path.join(*modpath[:-1]+[filename])
            zwróć os.path.join(self.build_lib, filename)

        # the inplace option requires to find the package directory
        # using the build_py command dla that
        package = '.'.join(modpath[0:-1])
        build_py = self.get_finalized_command('build_py')
        package_dir = os.path.abspath(build_py.get_package_dir(package))

        # returning
        #   package_dir/filename
        zwróć os.path.join(package_dir, filename)

    def get_ext_fullname(self, ext_name):
        """Returns the fullname of a given extension name.

        Adds the `package.` prefix"""
        jeżeli self.package jest Nic:
            zwróć ext_name
        inaczej:
            zwróć self.package + '.' + ext_name

    def get_ext_filename(self, ext_name):
        r"""Convert the name of an extension (eg. "foo.bar") into the name
        of the file z which it will be loaded (eg. "foo/bar.so", albo
        "foo\bar.pyd").
        """
        z distutils.sysconfig zaimportuj get_config_var
        ext_path = ext_name.split('.')
        ext_suffix = get_config_var('EXT_SUFFIX')
        zwróć os.path.join(*ext_path) + ext_suffix

    def get_export_symbols(self, ext):
        """Return the list of symbols that a shared extension has to
        export.  This either uses 'ext.export_symbols' or, jeżeli it's nie
        provided, "PyInit_" + module_name.  Only relevant on Windows, where
        the .pyd file (DLL) must export the module "PyInit_" function.
        """
        initfunc_name = "PyInit_" + ext.name.split('.')[-1]
        jeżeli initfunc_name nie w ext.export_symbols:
            ext.export_symbols.append(initfunc_name)
        zwróć ext.export_symbols

    def get_libraries(self, ext):
        """Return the list of libraries to link against when building a
        shared extension.  On most platforms, this jest just 'ext.libraries';
        on Windows, we add the Python library (eg. python20.dll).
        """
        # The python library jest always needed on Windows.  For MSVC, this
        # jest redundant, since the library jest mentioned w a pragma w
        # pyconfig.h that MSVC groks.  The other Windows compilers all seem
        # to need it mentioned explicitly, though, so that's what we do.
        # Append '_d' to the python zaimportuj library on debug builds.
        jeżeli sys.platform == "win32":
            z distutils._msvccompiler zaimportuj MSVCCompiler
            jeżeli nie isinstance(self.compiler, MSVCCompiler):
                template = "python%d%d"
                jeżeli self.debug:
                    template = template + '_d'
                pythonlib = (template %
                       (sys.hexversion >> 24, (sys.hexversion >> 16) & 0xff))
                # don't extend ext.libraries, it may be shared przy other
                # extensions, it jest a reference to the original list
                zwróć ext.libraries + [pythonlib]
            inaczej:
                zwróć ext.libraries
        albo_inaczej sys.platform[:6] == "cygwin":
            template = "python%d.%d"
            pythonlib = (template %
                   (sys.hexversion >> 24, (sys.hexversion >> 16) & 0xff))
            # don't extend ext.libraries, it may be shared przy other
            # extensions, it jest a reference to the original list
            zwróć ext.libraries + [pythonlib]
        albo_inaczej sys.platform[:6] == "atheos":
            z distutils zaimportuj sysconfig

            template = "python%d.%d"
            pythonlib = (template %
                   (sys.hexversion >> 24, (sys.hexversion >> 16) & 0xff))
            # Get SHLIBS z Makefile
            extra = []
            dla lib w sysconfig.get_config_var('SHLIBS').split():
                jeżeli lib.startswith('-l'):
                    extra.append(lib[2:])
                inaczej:
                    extra.append(lib)
            # don't extend ext.libraries, it may be shared przy other
            # extensions, it jest a reference to the original list
            zwróć ext.libraries + [pythonlib, "m"] + extra
        albo_inaczej sys.platform == 'darwin':
            # Don't use the default code below
            zwróć ext.libraries
        albo_inaczej sys.platform[:3] == 'aix':
            # Don't use the default code below
            zwróć ext.libraries
        inaczej:
            z distutils zaimportuj sysconfig
            jeżeli sysconfig.get_config_var('Py_ENABLE_SHARED'):
                pythonlib = 'python{}.{}{}'.format(
                    sys.hexversion >> 24, (sys.hexversion >> 16) & 0xff,
                    sys.abiflags)
                zwróć ext.libraries + [pythonlib]
            inaczej:
                zwróć ext.libraries
