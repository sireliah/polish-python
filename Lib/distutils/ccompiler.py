"""distutils.ccompiler

Contains CCompiler, an abstract base klasa that defines the interface
dla the Distutils compiler abstraction model."""

zaimportuj sys, os, re
z distutils.errors zaimportuj *
z distutils.spawn zaimportuj spawn
z distutils.file_util zaimportuj move_file
z distutils.dir_util zaimportuj mkpath
z distutils.dep_util zaimportuj newer_pairwise, newer_group
z distutils.util zaimportuj split_quoted, execute
z distutils zaimportuj log

klasa CCompiler:
    """Abstract base klasa to define the interface that must be implemented
    by real compiler classes.  Also has some utility methods used by
    several compiler classes.

    The basic idea behind a compiler abstraction klasa jest that each
    instance can be used dla all the compile/link steps w building a
    single project.  Thus, attributes common to all of those compile oraz
    link steps -- include directories, macros to define, libraries to link
    against, etc. -- are attributes of the compiler instance.  To allow for
    variability w how individual files are treated, most of those
    attributes may be varied on a per-compilation albo per-link basis.
    """

    # 'compiler_type' jest a klasa attribute that identifies this class.  It
    # keeps code that wants to know what kind of compiler it's dealing with
    # z having to zaimportuj all possible compiler classes just to do an
    # 'isinstance'.  In concrete CCompiler subclasses, 'compiler_type'
    # should really, really be one of the keys of the 'compiler_class'
    # dictionary (see below -- used by the 'new_compiler()' factory
    # function) -- authors of new compiler interface classes are
    # responsible dla updating 'compiler_class'!
    compiler_type = Nic

    # XXX things nie handled by this compiler abstraction model:
    #   * client can't provide additional options dla a compiler,
    #     e.g. warning, optimization, debugging flags.  Perhaps this
    #     should be the domain of concrete compiler abstraction classes
    #     (UnixCCompiler, MSVCCompiler, etc.) -- albo perhaps the base
    #     klasa should have methods dla the common ones.
    #   * can't completely override the include albo library searchg
    #     path, ie. no "cc -I -Idir1 -Idir2" albo "cc -L -Ldir1 -Ldir2".
    #     I'm nie sure how widely supported this jest even by Unix
    #     compilers, much less on other platforms.  And I'm even less
    #     sure how useful it is; maybe dla cross-compiling, but
    #     support dla that jest a ways off.  (And anyways, cross
    #     compilers probably have a dedicated binary przy the
    #     right paths compiled in.  I hope.)
    #   * can't do really freaky things przy the library list/library
    #     dirs, e.g. "-Ldir1 -lfoo -Ldir2 -lfoo" to link against
    #     different versions of libfoo.a w different locations.  I
    #     think this jest useless without the ability to null out the
    #     library search path anyways.


    # Subclasses that rely on the standard filename generation methods
    # implemented below should override these; see the comment near
    # those methods ('object_filenames()' et. al.) dla details:
    src_extensions = Nic               # list of strings
    obj_extension = Nic                # string
    static_lib_extension = Nic
    shared_lib_extension = Nic         # string
    static_lib_format = Nic            # format string
    shared_lib_format = Nic            # prob. same jako static_lib_format
    exe_extension = Nic                # string

    # Default language settings. language_map jest used to detect a source
    # file albo Extension target language, checking source filenames.
    # language_order jest used to detect the language precedence, when deciding
    # what language to use when mixing source types. For example, jeżeli some
    # extension has two files przy ".c" extension, oraz one przy ".cpp", it
    # jest still linked jako c++.
    language_map = {".c"   : "c",
                    ".cc"  : "c++",
                    ".cpp" : "c++",
                    ".cxx" : "c++",
                    ".m"   : "objc",
                   }
    language_order = ["c++", "objc", "c"]

    def __init__(self, verbose=0, dry_run=0, force=0):
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose

        # 'output_dir': a common output directory dla object, library,
        # shared object, oraz shared library files
        self.output_dir = Nic

        # 'macros': a list of macro definitions (or undefinitions).  A
        # macro definition jest a 2-tuple (name, value), where the value jest
        # either a string albo Nic (no explicit value).  A macro
        # undefinition jest a 1-tuple (name,).
        self.macros = []

        # 'include_dirs': a list of directories to search dla include files
        self.include_dirs = []

        # 'libraries': a list of libraries to include w any link
        # (library names, nie filenames: eg. "foo" nie "libfoo.a")
        self.libraries = []

        # 'library_dirs': a list of directories to search dla libraries
        self.library_dirs = []

        # 'runtime_library_dirs': a list of directories to search for
        # shared libraries/objects at runtime
        self.runtime_library_dirs = []

        # 'objects': a list of object files (or similar, such jako explicitly
        # named library files) to include on any link
        self.objects = []

        dla key w self.executables.keys():
            self.set_executable(key, self.executables[key])

    def set_executables(self, **kwargs):
        """Define the executables (and options dla them) that will be run
        to perform the various stages of compilation.  The exact set of
        executables that may be specified here depends on the compiler
        klasa (via the 'executables' klasa attribute), but most will have:
          compiler      the C/C++ compiler
          linker_so     linker used to create shared objects oraz libraries
          linker_exe    linker used to create binary executables
          archiver      static library creator

        On platforms przy a command-line (Unix, DOS/Windows), each of these
        jest a string that will be split into executable name oraz (optional)
        list of arguments.  (Splitting the string jest done similarly to how
        Unix shells operate: words are delimited by spaces, but quotes oraz
        backslashes can override this.  See
        'distutils.util.split_quoted()'.)
        """

        # Note that some CCompiler implementation classes will define class
        # attributes 'cpp', 'cc', etc. przy hard-coded executable names;
        # this jest appropriate when a compiler klasa jest dla exactly one
        # compiler/OS combination (eg. MSVCCompiler).  Other compiler
        # classes (UnixCCompiler, w particular) are driven by information
        # discovered at run-time, since there are many different ways to do
        # basically the same things przy Unix C compilers.

        dla key w kwargs:
            jeżeli key nie w self.executables:
                podnieś ValueError("unknown executable '%s' dla klasa %s" %
                      (key, self.__class__.__name__))
            self.set_executable(key, kwargs[key])

    def set_executable(self, key, value):
        jeżeli isinstance(value, str):
            setattr(self, key, split_quoted(value))
        inaczej:
            setattr(self, key, value)

    def _find_macro(self, name):
        i = 0
        dla defn w self.macros:
            jeżeli defn[0] == name:
                zwróć i
            i += 1
        zwróć Nic

    def _check_macro_definitions(self, definitions):
        """Ensures that every element of 'definitions' jest a valid macro
        definition, ie. either (name,value) 2-tuple albo a (name,) tuple.  Do
        nothing jeżeli all definitions are OK, podnieś TypeError otherwise.
        """
        dla defn w definitions:
            jeżeli nie (isinstance(defn, tuple) oraz
                    (len(defn) w (1, 2) oraz
                      (isinstance (defn[1], str) albo defn[1] jest Nic)) oraz
                    isinstance (defn[0], str)):
                podnieś TypeError(("invalid macro definition '%s': " % defn) + \
                      "must be tuple (string,), (string, string), albo " + \
                      "(string, Nic)")


    # -- Bookkeeping methods -------------------------------------------

    def define_macro(self, name, value=Nic):
        """Define a preprocessor macro dla all compilations driven by this
        compiler object.  The optional parameter 'value' should be a
        string; jeżeli it jest nie supplied, then the macro will be defined
        without an explicit value oraz the exact outcome depends on the
        compiler used (XXX true? does ANSI say anything about this?)
        """
        # Delete z the list of macro definitions/undefinitions if
        # already there (so that this one will take precedence).
        i = self._find_macro (name)
        jeżeli i jest nie Nic:
            usuń self.macros[i]

        self.macros.append((name, value))

    def undefine_macro(self, name):
        """Undefine a preprocessor macro dla all compilations driven by
        this compiler object.  If the same macro jest defined by
        'define_macro()' oraz undefined by 'undefine_macro()' the last call
        takes precedence (including multiple redefinitions albo
        undefinitions).  If the macro jest redefined/undefined on a
        per-compilation basis (ie. w the call to 'compile()'), then that
        takes precedence.
        """
        # Delete z the list of macro definitions/undefinitions if
        # already there (so that this one will take precedence).
        i = self._find_macro (name)
        jeżeli i jest nie Nic:
            usuń self.macros[i]

        undefn = (name,)
        self.macros.append(undefn)

    def add_include_dir(self, dir):
        """Add 'dir' to the list of directories that will be searched for
        header files.  The compiler jest instructed to search directories w
        the order w which they are supplied by successive calls to
        'add_include_dir()'.
        """
        self.include_dirs.append(dir)

    def set_include_dirs(self, dirs):
        """Set the list of directories that will be searched to 'dirs' (a
        list of strings).  Overrides any preceding calls to
        'add_include_dir()'; subsequence calls to 'add_include_dir()' add
        to the list dalejed to 'set_include_dirs()'.  This does nie affect
        any list of standard include directories that the compiler may
        search by default.
        """
        self.include_dirs = dirs[:]

    def add_library(self, libname):
        """Add 'libname' to the list of libraries that will be included w
        all links driven by this compiler object.  Note that 'libname'
        should *not* be the name of a file containing a library, but the
        name of the library itself: the actual filename will be inferred by
        the linker, the compiler, albo the compiler klasa (depending on the
        platform).

        The linker will be instructed to link against libraries w the
        order they were supplied to 'add_library()' and/or
        'set_libraries()'.  It jest perfectly valid to duplicate library
        names; the linker will be instructed to link against libraries as
        many times jako they are mentioned.
        """
        self.libraries.append(libname)

    def set_libraries(self, libnames):
        """Set the list of libraries to be included w all links driven by
        this compiler object to 'libnames' (a list of strings).  This does
        nie affect any standard system libraries that the linker may
        include by default.
        """
        self.libraries = libnames[:]

    def add_library_dir(self, dir):
        """Add 'dir' to the list of directories that will be searched for
        libraries specified to 'add_library()' oraz 'set_libraries()'.  The
        linker will be instructed to search dla libraries w the order they
        are supplied to 'add_library_dir()' and/or 'set_library_dirs()'.
        """
        self.library_dirs.append(dir)

    def set_library_dirs(self, dirs):
        """Set the list of library search directories to 'dirs' (a list of
        strings).  This does nie affect any standard library search path
        that the linker may search by default.
        """
        self.library_dirs = dirs[:]

    def add_runtime_library_dir(self, dir):
        """Add 'dir' to the list of directories that will be searched for
        shared libraries at runtime.
        """
        self.runtime_library_dirs.append(dir)

    def set_runtime_library_dirs(self, dirs):
        """Set the list of directories to search dla shared libraries at
        runtime to 'dirs' (a list of strings).  This does nie affect any
        standard search path that the runtime linker may search by
        default.
        """
        self.runtime_library_dirs = dirs[:]

    def add_link_object(self, object):
        """Add 'object' to the list of object files (or analogues, such as
        explicitly named library files albo the output of "resource
        compilers") to be included w every link driven by this compiler
        object.
        """
        self.objects.append(object)

    def set_link_objects(self, objects):
        """Set the list of object files (or analogues) to be included w
        every link to 'objects'.  This does nie affect any standard object
        files that the linker may include by default (such jako system
        libraries).
        """
        self.objects = objects[:]


    # -- Private utility methods --------------------------------------
    # (here dla the convenience of subclasses)

    # Helper method to prep compiler w subclass compile() methods

    def _setup_compile(self, outdir, macros, incdirs, sources, depends,
                       extra):
        """Process arguments oraz decide which source files to compile."""
        jeżeli outdir jest Nic:
            outdir = self.output_dir
        albo_inaczej nie isinstance(outdir, str):
            podnieś TypeError("'output_dir' must be a string albo Nic")

        jeżeli macros jest Nic:
            macros = self.macros
        albo_inaczej isinstance(macros, list):
            macros = macros + (self.macros albo [])
        inaczej:
            podnieś TypeError("'macros' (jeżeli supplied) must be a list of tuples")

        jeżeli incdirs jest Nic:
            incdirs = self.include_dirs
        albo_inaczej isinstance(incdirs, (list, tuple)):
            incdirs = list(incdirs) + (self.include_dirs albo [])
        inaczej:
            podnieś TypeError(
                  "'include_dirs' (jeżeli supplied) must be a list of strings")

        jeżeli extra jest Nic:
            extra = []

        # Get the list of expected output (object) files
        objects = self.object_filenames(sources, strip_dir=0,
                                        output_dir=outdir)
        assert len(objects) == len(sources)

        pp_opts = gen_preprocess_options(macros, incdirs)

        build = {}
        dla i w range(len(sources)):
            src = sources[i]
            obj = objects[i]
            ext = os.path.splitext(src)[1]
            self.mkpath(os.path.dirname(obj))
            build[obj] = (src, ext)

        zwróć macros, objects, extra, pp_opts, build

    def _get_cc_args(self, pp_opts, debug, before):
        # works dla unixccompiler, cygwinccompiler
        cc_args = pp_opts + ['-c']
        jeżeli debug:
            cc_args[:0] = ['-g']
        jeżeli before:
            cc_args[:0] = before
        zwróć cc_args

    def _fix_compile_args(self, output_dir, macros, include_dirs):
        """Typecheck oraz fix-up some of the arguments to the 'compile()'
        method, oraz zwróć fixed-up values.  Specifically: jeżeli 'output_dir'
        jest Nic, replaces it przy 'self.output_dir'; ensures that 'macros'
        jest a list, oraz augments it przy 'self.macros'; ensures that
        'include_dirs' jest a list, oraz augments it przy 'self.include_dirs'.
        Guarantees that the returned values are of the correct type,
        i.e. dla 'output_dir' either string albo Nic, oraz dla 'macros' oraz
        'include_dirs' either list albo Nic.
        """
        jeżeli output_dir jest Nic:
            output_dir = self.output_dir
        albo_inaczej nie isinstance(output_dir, str):
            podnieś TypeError("'output_dir' must be a string albo Nic")

        jeżeli macros jest Nic:
            macros = self.macros
        albo_inaczej isinstance(macros, list):
            macros = macros + (self.macros albo [])
        inaczej:
            podnieś TypeError("'macros' (jeżeli supplied) must be a list of tuples")

        jeżeli include_dirs jest Nic:
            include_dirs = self.include_dirs
        albo_inaczej isinstance(include_dirs, (list, tuple)):
            include_dirs = list(include_dirs) + (self.include_dirs albo [])
        inaczej:
            podnieś TypeError(
                  "'include_dirs' (jeżeli supplied) must be a list of strings")

        zwróć output_dir, macros, include_dirs

    def _prep_compile(self, sources, output_dir, depends=Nic):
        """Decide which souce files must be recompiled.

        Determine the list of object files corresponding to 'sources',
        oraz figure out which ones really need to be recompiled.
        Return a list of all object files oraz a dictionary telling
        which source files can be skipped.
        """
        # Get the list of expected output (object) files
        objects = self.object_filenames(sources, output_dir=output_dir)
        assert len(objects) == len(sources)

        # Return an empty dict dla the "which source files can be skipped"
        # zwróć value to preserve API compatibility.
        zwróć objects, {}

    def _fix_object_args(self, objects, output_dir):
        """Typecheck oraz fix up some arguments supplied to various methods.
        Specifically: ensure that 'objects' jest a list; jeżeli output_dir jest
        Nic, replace przy self.output_dir.  Return fixed versions of
        'objects' oraz 'output_dir'.
        """
        jeżeli nie isinstance(objects, (list, tuple)):
            podnieś TypeError("'objects' must be a list albo tuple of strings")
        objects = list(objects)

        jeżeli output_dir jest Nic:
            output_dir = self.output_dir
        albo_inaczej nie isinstance(output_dir, str):
            podnieś TypeError("'output_dir' must be a string albo Nic")

        zwróć (objects, output_dir)

    def _fix_lib_args(self, libraries, library_dirs, runtime_library_dirs):
        """Typecheck oraz fix up some of the arguments supplied to the
        'link_*' methods.  Specifically: ensure that all arguments are
        lists, oraz augment them przy their permanent versions
        (eg. 'self.libraries' augments 'libraries').  Return a tuple with
        fixed versions of all arguments.
        """
        jeżeli libraries jest Nic:
            libraries = self.libraries
        albo_inaczej isinstance(libraries, (list, tuple)):
            libraries = list (libraries) + (self.libraries albo [])
        inaczej:
            podnieś TypeError(
                  "'libraries' (jeżeli supplied) must be a list of strings")

        jeżeli library_dirs jest Nic:
            library_dirs = self.library_dirs
        albo_inaczej isinstance(library_dirs, (list, tuple)):
            library_dirs = list (library_dirs) + (self.library_dirs albo [])
        inaczej:
            podnieś TypeError(
                  "'library_dirs' (jeżeli supplied) must be a list of strings")

        jeżeli runtime_library_dirs jest Nic:
            runtime_library_dirs = self.runtime_library_dirs
        albo_inaczej isinstance(runtime_library_dirs, (list, tuple)):
            runtime_library_dirs = (list(runtime_library_dirs) +
                                    (self.runtime_library_dirs albo []))
        inaczej:
            podnieś TypeError("'runtime_library_dirs' (jeżeli supplied) "
                            "must be a list of strings")

        zwróć (libraries, library_dirs, runtime_library_dirs)

    def _need_link(self, objects, output_file):
        """Return true jeżeli we need to relink the files listed w 'objects'
        to recreate 'output_file'.
        """
        jeżeli self.force:
            zwróć Prawda
        inaczej:
            jeżeli self.dry_run:
                newer = newer_group (objects, output_file, missing='newer')
            inaczej:
                newer = newer_group (objects, output_file)
            zwróć newer

    def detect_language(self, sources):
        """Detect the language of a given file, albo list of files. Uses
        language_map, oraz language_order to do the job.
        """
        jeżeli nie isinstance(sources, list):
            sources = [sources]
        lang = Nic
        index = len(self.language_order)
        dla source w sources:
            base, ext = os.path.splitext(source)
            extlang = self.language_map.get(ext)
            spróbuj:
                extindex = self.language_order.index(extlang)
                jeżeli extindex < index:
                    lang = extlang
                    index = extindex
            wyjąwszy ValueError:
                dalej
        zwróć lang


    # -- Worker methods ------------------------------------------------
    # (must be implemented by subclasses)

    def preprocess(self, source, output_file=Nic, macros=Nic,
                   include_dirs=Nic, extra_preargs=Nic, extra_postargs=Nic):
        """Preprocess a single C/C++ source file, named w 'source'.
        Output will be written to file named 'output_file', albo stdout if
        'output_file' nie supplied.  'macros' jest a list of macro
        definitions jako dla 'compile()', which will augment the macros set
        przy 'define_macro()' oraz 'undefine_macro()'.  'include_dirs' jest a
        list of directory names that will be added to the default list.

        Raises PreprocessError on failure.
        """
        dalej

    def compile(self, sources, output_dir=Nic, macros=Nic,
                include_dirs=Nic, debug=0, extra_preargs=Nic,
                extra_postargs=Nic, depends=Nic):
        """Compile one albo more source files.

        'sources' must be a list of filenames, most likely C/C++
        files, but w reality anything that can be handled by a
        particular compiler oraz compiler klasa (eg. MSVCCompiler can
        handle resource files w 'sources').  Return a list of object
        filenames, one per source filename w 'sources'.  Depending on
        the implementation, nie all source files will necessarily be
        compiled, but all corresponding object filenames will be
        returned.

        If 'output_dir' jest given, object files will be put under it, while
        retaining their original path component.  That is, "foo/bar.c"
        normally compiles to "foo/bar.o" (dla a Unix implementation); if
        'output_dir' jest "build", then it would compile to
        "build/foo/bar.o".

        'macros', jeżeli given, must be a list of macro definitions.  A macro
        definition jest either a (name, value) 2-tuple albo a (name,) 1-tuple.
        The former defines a macro; jeżeli the value jest Nic, the macro jest
        defined without an explicit value.  The 1-tuple case undefines a
        macro.  Later definitions/redefinitions/ undefinitions take
        precedence.

        'include_dirs', jeżeli given, must be a list of strings, the
        directories to add to the default include file search path dla this
        compilation only.

        'debug' jest a boolean; jeżeli true, the compiler will be instructed to
        output debug symbols w (or alongside) the object file(s).

        'extra_preargs' oraz 'extra_postargs' are implementation- dependent.
        On platforms that have the notion of a command-line (e.g. Unix,
        DOS/Windows), they are most likely lists of strings: extra
        command-line arguments to prepand/append to the compiler command
        line.  On other platforms, consult the implementation class
        documentation.  In any event, they are intended jako an escape hatch
        dla those occasions when the abstract compiler framework doesn't
        cut the mustard.

        'depends', jeżeli given, jest a list of filenames that all targets
        depend on.  If a source file jest older than any file w
        depends, then the source file will be recompiled.  This
        supports dependency tracking, but only at a coarse
        granularity.

        Raises CompileError on failure.
        """
        # A concrete compiler klasa can either override this method
        # entirely albo implement _compile().
        macros, objects, extra_postargs, pp_opts, build = \
                self._setup_compile(output_dir, macros, include_dirs, sources,
                                    depends, extra_postargs)
        cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)

        dla obj w objects:
            spróbuj:
                src, ext = build[obj]
            wyjąwszy KeyError:
                kontynuuj
            self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)

        # Return *all* object filenames, nie just the ones we just built.
        zwróć objects

    def _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        """Compile 'src' to product 'obj'."""
        # A concrete compiler klasa that does nie override compile()
        # should implement _compile().
        dalej

    def create_static_lib(self, objects, output_libname, output_dir=Nic,
                          debug=0, target_lang=Nic):
        """Link a bunch of stuff together to create a static library file.
        The "bunch of stuff" consists of the list of object files supplied
        jako 'objects', the extra object files supplied to
        'add_link_object()' and/or 'set_link_objects()', the libraries
        supplied to 'add_library()' and/or 'set_libraries()', oraz the
        libraries supplied jako 'libraries' (jeżeli any).

        'output_libname' should be a library name, nie a filename; the
        filename will be inferred z the library name.  'output_dir' jest
        the directory where the library file will be put.

        'debug' jest a boolean; jeżeli true, debugging information will be
        included w the library (niee that on most platforms, it jest the
        compile step where this matters: the 'debug' flag jest included here
        just dla consistency).

        'target_lang' jest the target language dla which the given objects
        are being compiled. This allows specific linkage time treatment of
        certain languages.

        Raises LibError on failure.
        """
        dalej


    # values dla target_desc parameter w link()
    SHARED_OBJECT = "shared_object"
    SHARED_LIBRARY = "shared_library"
    EXECUTABLE = "executable"

    def link(self,
             target_desc,
             objects,
             output_filename,
             output_dir=Nic,
             libraries=Nic,
             library_dirs=Nic,
             runtime_library_dirs=Nic,
             export_symbols=Nic,
             debug=0,
             extra_preargs=Nic,
             extra_postargs=Nic,
             build_temp=Nic,
             target_lang=Nic):
        """Link a bunch of stuff together to create an executable albo
        shared library file.

        The "bunch of stuff" consists of the list of object files supplied
        jako 'objects'.  'output_filename' should be a filename.  If
        'output_dir' jest supplied, 'output_filename' jest relative to it
        (i.e. 'output_filename' can provide directory components if
        needed).

        'libraries' jest a list of libraries to link against.  These are
        library names, nie filenames, since they're translated into
        filenames w a platform-specific way (eg. "foo" becomes "libfoo.a"
        on Unix oraz "foo.lib" on DOS/Windows).  However, they can include a
        directory component, which means the linker will look w that
        specific directory rather than searching all the normal locations.

        'library_dirs', jeżeli supplied, should be a list of directories to
        search dla libraries that were specified jako bare library names
        (ie. no directory component).  These are on top of the system
        default oraz those supplied to 'add_library_dir()' and/or
        'set_library_dirs()'.  'runtime_library_dirs' jest a list of
        directories that will be embedded into the shared library oraz used
        to search dla other shared libraries that *it* depends on at
        run-time.  (This may only be relevant on Unix.)

        'export_symbols' jest a list of symbols that the shared library will
        export.  (This appears to be relevant only on Windows.)

        'debug' jest jako dla 'compile()' oraz 'create_static_lib()', przy the
        slight distinction that it actually matters on most platforms (as
        opposed to 'create_static_lib()', which includes a 'debug' flag
        mostly dla form's sake).

        'extra_preargs' oraz 'extra_postargs' are jako dla 'compile()' (except
        of course that they supply command-line arguments dla the
        particular linker being used).

        'target_lang' jest the target language dla which the given objects
        are being compiled. This allows specific linkage time treatment of
        certain languages.

        Raises LinkError on failure.
        """
        podnieś NotImplementedError


    # Old 'link_*()' methods, rewritten to use the new 'link()' method.

    def link_shared_lib(self,
                        objects,
                        output_libname,
                        output_dir=Nic,
                        libraries=Nic,
                        library_dirs=Nic,
                        runtime_library_dirs=Nic,
                        export_symbols=Nic,
                        debug=0,
                        extra_preargs=Nic,
                        extra_postargs=Nic,
                        build_temp=Nic,
                        target_lang=Nic):
        self.link(CCompiler.SHARED_LIBRARY, objects,
                  self.library_filename(output_libname, lib_type='shared'),
                  output_dir,
                  libraries, library_dirs, runtime_library_dirs,
                  export_symbols, debug,
                  extra_preargs, extra_postargs, build_temp, target_lang)


    def link_shared_object(self,
                           objects,
                           output_filename,
                           output_dir=Nic,
                           libraries=Nic,
                           library_dirs=Nic,
                           runtime_library_dirs=Nic,
                           export_symbols=Nic,
                           debug=0,
                           extra_preargs=Nic,
                           extra_postargs=Nic,
                           build_temp=Nic,
                           target_lang=Nic):
        self.link(CCompiler.SHARED_OBJECT, objects,
                  output_filename, output_dir,
                  libraries, library_dirs, runtime_library_dirs,
                  export_symbols, debug,
                  extra_preargs, extra_postargs, build_temp, target_lang)


    def link_executable(self,
                        objects,
                        output_progname,
                        output_dir=Nic,
                        libraries=Nic,
                        library_dirs=Nic,
                        runtime_library_dirs=Nic,
                        debug=0,
                        extra_preargs=Nic,
                        extra_postargs=Nic,
                        target_lang=Nic):
        self.link(CCompiler.EXECUTABLE, objects,
                  self.executable_filename(output_progname), output_dir,
                  libraries, library_dirs, runtime_library_dirs, Nic,
                  debug, extra_preargs, extra_postargs, Nic, target_lang)


    # -- Miscellaneous methods -----------------------------------------
    # These are all used by the 'gen_lib_options() function; there jest
    # no appropriate default implementation so subclasses should
    # implement all of these.

    def library_dir_option(self, dir):
        """Return the compiler option to add 'dir' to the list of
        directories searched dla libraries.
        """
        podnieś NotImplementedError

    def runtime_library_dir_option(self, dir):
        """Return the compiler option to add 'dir' to the list of
        directories searched dla runtime libraries.
        """
        podnieś NotImplementedError

    def library_option(self, lib):
        """Return the compiler option to add 'dir' to the list of libraries
        linked into the shared library albo executable.
        """
        podnieś NotImplementedError

    def has_function(self, funcname, includes=Nic, include_dirs=Nic,
                     libraries=Nic, library_dirs=Nic):
        """Return a boolean indicating whether funcname jest supported on
        the current platform.  The optional arguments can be used to
        augment the compilation environment.
        """
        # this can't be included at module scope because it tries to
        # zaimportuj math which might nie be available at that point - maybe
        # the necessary logic should just be inlined?
        zaimportuj tempfile
        jeżeli includes jest Nic:
            includes = []
        jeżeli include_dirs jest Nic:
            include_dirs = []
        jeżeli libraries jest Nic:
            libraries = []
        jeżeli library_dirs jest Nic:
            library_dirs = []
        fd, fname = tempfile.mkstemp(".c", funcname, text=Prawda)
        f = os.fdopen(fd, "w")
        spróbuj:
            dla incl w includes:
                f.write("""#include "%s"\n""" % incl)
            f.write("""\
main (int argc, char **argv) {
    %s();
}
""" % funcname)
        w_końcu:
            f.close()
        spróbuj:
            objects = self.compile([fname], include_dirs=include_dirs)
        wyjąwszy CompileError:
            zwróć Nieprawda

        spróbuj:
            self.link_executable(objects, "a.out",
                                 libraries=libraries,
                                 library_dirs=library_dirs)
        wyjąwszy (LinkError, TypeError):
            zwróć Nieprawda
        zwróć Prawda

    def find_library_file (self, dirs, lib, debug=0):
        """Search the specified list of directories dla a static albo shared
        library file 'lib' oraz zwróć the full path to that file.  If
        'debug' true, look dla a debugging version (jeżeli that makes sense on
        the current platform).  Return Nic jeżeli 'lib' wasn't found w any of
        the specified directories.
        """
        podnieś NotImplementedError

    # -- Filename generation methods -----------------------------------

    # The default implementation of the filename generating methods are
    # prejudiced towards the Unix/DOS/Windows view of the world:
    #   * object files are named by replacing the source file extension
    #     (eg. .c/.cpp -> .o/.obj)
    #   * library files (shared albo static) are named by plugging the
    #     library name oraz extension into a format string, eg.
    #     "lib%s.%s" % (lib_name, ".a") dla Unix static libraries
    #   * executables are named by appending an extension (possibly
    #     empty) to the program name: eg. progname + ".exe" for
    #     Windows
    #
    # To reduce redundant code, these methods expect to find
    # several attributes w the current object (presumably defined
    # jako klasa attributes):
    #   * src_extensions -
    #     list of C/C++ source file extensions, eg. ['.c', '.cpp']
    #   * obj_extension -
    #     object file extension, eg. '.o' albo '.obj'
    #   * static_lib_extension -
    #     extension dla static library files, eg. '.a' albo '.lib'
    #   * shared_lib_extension -
    #     extension dla shared library/object files, eg. '.so', '.dll'
    #   * static_lib_format -
    #     format string dla generating static library filenames,
    #     eg. 'lib%s.%s' albo '%s.%s'
    #   * shared_lib_format
    #     format string dla generating shared library filenames
    #     (probably same jako static_lib_format, since the extension
    #     jest one of the intended parameters to the format string)
    #   * exe_extension -
    #     extension dla executable files, eg. '' albo '.exe'

    def object_filenames(self, source_filenames, strip_dir=0, output_dir=''):
        jeżeli output_dir jest Nic:
            output_dir = ''
        obj_names = []
        dla src_name w source_filenames:
            base, ext = os.path.splitext(src_name)
            base = os.path.splitdrive(base)[1] # Chop off the drive
            base = base[os.path.isabs(base):]  # If abs, chop off leading /
            jeżeli ext nie w self.src_extensions:
                podnieś UnknownFileError(
                      "unknown file type '%s' (z '%s')" % (ext, src_name))
            jeżeli strip_dir:
                base = os.path.basename(base)
            obj_names.append(os.path.join(output_dir,
                                          base + self.obj_extension))
        zwróć obj_names

    def shared_object_filename(self, basename, strip_dir=0, output_dir=''):
        assert output_dir jest nie Nic
        jeżeli strip_dir:
            basename = os.path.basename(basename)
        zwróć os.path.join(output_dir, basename + self.shared_lib_extension)

    def executable_filename(self, basename, strip_dir=0, output_dir=''):
        assert output_dir jest nie Nic
        jeżeli strip_dir:
            basename = os.path.basename(basename)
        zwróć os.path.join(output_dir, basename + (self.exe_extension albo ''))

    def library_filename(self, libname, lib_type='static',     # albo 'shared'
                         strip_dir=0, output_dir=''):
        assert output_dir jest nie Nic
        jeżeli lib_type nie w ("static", "shared", "dylib"):
            podnieś ValueError(
                  "'lib_type' must be \"static\", \"shared\" albo \"dylib\"")
        fmt = getattr(self, lib_type + "_lib_format")
        ext = getattr(self, lib_type + "_lib_extension")

        dir, base = os.path.split(libname)
        filename = fmt % (base, ext)
        jeżeli strip_dir:
            dir = ''

        zwróć os.path.join(output_dir, dir, filename)


    # -- Utility methods -----------------------------------------------

    def announce(self, msg, level=1):
        log.debug(msg)

    def debug_print(self, msg):
        z distutils.debug zaimportuj DEBUG
        jeżeli DEBUG:
            print(msg)

    def warn(self, msg):
        sys.stderr.write("warning: %s\n" % msg)

    def execute(self, func, args, msg=Nic, level=1):
        execute(func, args, msg, self.dry_run)

    def spawn(self, cmd):
        spawn(cmd, dry_run=self.dry_run)

    def move_file(self, src, dst):
        zwróć move_file(src, dst, dry_run=self.dry_run)

    def mkpath (self, name, mode=0o777):
        mkpath(name, mode, dry_run=self.dry_run)


# Map a sys.platform/os.name ('posix', 'nt') to the default compiler
# type dla that platform. Keys are interpreted jako re match
# patterns. Order jest important; platform mappings are preferred over
# OS names.
_default_compilers = (

    # Platform string mappings

    # on a cygwin built python we can use gcc like an ordinary UNIXish
    # compiler
    ('cygwin.*', 'unix'),

    # OS name mappings
    ('posix', 'unix'),
    ('nt', 'msvc'),

    )

def get_default_compiler(osname=Nic, platform=Nic):
    """Determine the default compiler to use dla the given platform.

       osname should be one of the standard Python OS names (i.e. the
       ones returned by os.name) oraz platform the common value
       returned by sys.platform dla the platform w question.

       The default values are os.name oraz sys.platform w case the
       parameters are nie given.
    """
    jeżeli osname jest Nic:
        osname = os.name
    jeżeli platform jest Nic:
        platform = sys.platform
    dla pattern, compiler w _default_compilers:
        jeżeli re.match(pattern, platform) jest nie Nic albo \
           re.match(pattern, osname) jest nie Nic:
            zwróć compiler
    # Default to Unix compiler
    zwróć 'unix'

# Map compiler types to (module_name, class_name) pairs -- ie. where to
# find the code that implements an interface to this compiler.  (The module
# jest assumed to be w the 'distutils' package.)
compiler_class = { 'unix':    ('unixccompiler', 'UnixCCompiler',
                               "standard UNIX-style compiler"),
                   'msvc':    ('_msvccompiler', 'MSVCCompiler',
                               "Microsoft Visual C++"),
                   'cygwin':  ('cygwinccompiler', 'CygwinCCompiler',
                               "Cygwin port of GNU C Compiler dla Win32"),
                   'mingw32': ('cygwinccompiler', 'Mingw32CCompiler',
                               "Mingw32 port of GNU C Compiler dla Win32"),
                   'bcpp':    ('bcppcompiler', 'BCPPCompiler',
                               "Borland C++ Compiler"),
                 }

def show_compilers():
    """Print list of available compilers (used by the "--help-compiler"
    options to "build", "build_ext", "build_clib").
    """
    # XXX this "knows" that the compiler option it's describing jest
    # "--compiler", which just happens to be the case dla the three
    # commands that use it.
    z distutils.fancy_getopt zaimportuj FancyGetopt
    compilers = []
    dla compiler w compiler_class.keys():
        compilers.append(("compiler="+compiler, Nic,
                          compiler_class[compiler][2]))
    compilers.sort()
    pretty_printer = FancyGetopt(compilers)
    pretty_printer.print_help("List of available compilers:")


def new_compiler(plat=Nic, compiler=Nic, verbose=0, dry_run=0, force=0):
    """Generate an instance of some CCompiler subclass dla the supplied
    platform/compiler combination.  'plat' defaults to 'os.name'
    (eg. 'posix', 'nt'), oraz 'compiler' defaults to the default compiler
    dla that platform.  Currently only 'posix' oraz 'nt' are supported, oraz
    the default compilers are "traditional Unix interface" (UnixCCompiler
    class) oraz Visual C++ (MSVCCompiler class).  Note that it's perfectly
    possible to ask dla a Unix compiler object under Windows, oraz a
    Microsoft compiler object under Unix -- jeżeli you supply a value for
    'compiler', 'plat' jest ignored.
    """
    jeżeli plat jest Nic:
        plat = os.name

    spróbuj:
        jeżeli compiler jest Nic:
            compiler = get_default_compiler(plat)

        (module_name, class_name, long_description) = compiler_class[compiler]
    wyjąwszy KeyError:
        msg = "don't know how to compile C/C++ code on platform '%s'" % plat
        jeżeli compiler jest nie Nic:
            msg = msg + " przy '%s' compiler" % compiler
        podnieś DistutilsPlatformError(msg)

    spróbuj:
        module_name = "distutils." + module_name
        __import__ (module_name)
        module = sys.modules[module_name]
        klass = vars(module)[class_name]
    wyjąwszy ImportError:
        podnieś DistutilsModuleError(
              "can't compile C/C++ code: unable to load module '%s'" % \
              module_name)
    wyjąwszy KeyError:
        podnieś DistutilsModuleError(
               "can't compile C/C++ code: unable to find klasa '%s' "
               "in module '%s'" % (class_name, module_name))

    # XXX The Nic jest necessary to preserve backwards compatibility
    # przy classes that expect verbose to be the first positional
    # argument.
    zwróć klass(Nic, dry_run, force)


def gen_preprocess_options(macros, include_dirs):
    """Generate C pre-processor options (-D, -U, -I) jako used by at least
    two types of compilers: the typical Unix compiler oraz Visual C++.
    'macros' jest the usual thing, a list of 1- albo 2-tuples, where (name,)
    means undefine (-U) macro 'name', oraz (name,value) means define (-D)
    macro 'name' to 'value'.  'include_dirs' jest just a list of directory
    names to be added to the header file search path (-I).  Returns a list
    of command-line options suitable dla either Unix compilers albo Visual
    C++.
    """
    # XXX it would be nice (mainly aesthetic, oraz so we don't generate
    # stupid-looking command lines) to go over 'macros' oraz eliminate
    # redundant definitions/undefinitions (ie. ensure that only the
    # latest mention of a particular macro winds up on the command
    # line).  I don't think it's essential, though, since most (all?)
    # Unix C compilers only pay attention to the latest -D albo -U
    # mention of a macro on their command line.  Similar situation for
    # 'include_dirs'.  I'm punting on both dla now.  Anyways, weeding out
    # redundancies like this should probably be the province of
    # CCompiler, since the data structures used are inherited z it
    # oraz therefore common to all CCompiler classes.
    pp_opts = []
    dla macro w macros:
        jeżeli nie (isinstance(macro, tuple) oraz 1 <= len(macro) <= 2):
            podnieś TypeError(
                  "bad macro definition '%s': "
                  "each element of 'macros' list must be a 1- albo 2-tuple"
                  % macro)

        jeżeli len(macro) == 1:        # undefine this macro
            pp_opts.append("-U%s" % macro[0])
        albo_inaczej len(macro) == 2:
            jeżeli macro[1] jest Nic:    # define przy no explicit value
                pp_opts.append("-D%s" % macro[0])
            inaczej:
                # XXX *don't* need to be clever about quoting the
                # macro value here, because we're going to avoid the
                # shell at all costs when we spawn the command!
                pp_opts.append("-D%s=%s" % macro)

    dla dir w include_dirs:
        pp_opts.append("-I%s" % dir)
    zwróć pp_opts


def gen_lib_options (compiler, library_dirs, runtime_library_dirs, libraries):
    """Generate linker options dla searching library directories oraz
    linking przy specific libraries.  'libraries' oraz 'library_dirs' are,
    respectively, lists of library names (nie filenames!) oraz search
    directories.  Returns a list of command-line options suitable dla use
    przy some compiler (depending on the two format strings dalejed in).
    """
    lib_opts = []

    dla dir w library_dirs:
        lib_opts.append(compiler.library_dir_option(dir))

    dla dir w runtime_library_dirs:
        opt = compiler.runtime_library_dir_option(dir)
        jeżeli isinstance(opt, list):
            lib_opts = lib_opts + opt
        inaczej:
            lib_opts.append(opt)

    # XXX it's important that we *not* remove redundant library mentions!
    # sometimes you really do have to say "-lfoo -lbar -lfoo" w order to
    # resolve all symbols.  I just hope we never have to say "-lfoo obj.o
    # -lbar" to get things to work -- that's certainly a possibility, but a
    # pretty nasty way to arrange your C code.

    dla lib w libraries:
        (lib_dir, lib_name) = os.path.split(lib)
        jeżeli lib_dir:
            lib_file = compiler.find_library_file([lib_dir], lib_name)
            jeżeli lib_file:
                lib_opts.append(lib_file)
            inaczej:
                compiler.warn("no library file corresponding to "
                              "'%s' found (skipping)" % lib)
        inaczej:
            lib_opts.append(compiler.library_option (lib))
    zwróć lib_opts
