"""distutils.bcppcompiler

Contains BorlandCCompiler, an implementation of the abstract CCompiler class
dla the Borland C++ compiler.
"""

# This implementation by Lyle Johnson, based on the original msvccompiler.py
# module oraz using the directions originally published by Gordon Williams.

# XXX looks like there's a LOT of overlap between these two classes:
# someone should sit down oraz factor out the common code as
# WindowsCCompiler!  --GPW


zaimportuj os
z distutils.errors zaimportuj \
     DistutilsExecError, DistutilsPlatformError, \
     CompileError, LibError, LinkError, UnknownFileError
z distutils.ccompiler zaimportuj \
     CCompiler, gen_preprocess_options, gen_lib_options
z distutils.file_util zaimportuj write_file
z distutils.dep_util zaimportuj newer
z distutils zaimportuj log

klasa BCPPCompiler(CCompiler) :
    """Concrete klasa that implements an interface to the Borland C/C++
    compiler, jako defined by the CCompiler abstract class.
    """

    compiler_type = 'bcpp'

    # Just set this so CCompiler's constructor doesn't barf.  We currently
    # don't use the 'set_executables()' bureaucracy provided by CCompiler,
    # jako it really isn't necessary dla this sort of single-compiler class.
    # Would be nice to have a consistent interface przy UnixCCompiler,
    # though, so it's worth thinking about.
    executables = {}

    # Private klasa data (need to distinguish C z C++ source dla compiler)
    _c_extensions = ['.c']
    _cpp_extensions = ['.cc', '.cpp', '.cxx']

    # Needed dla the filename generation methods provided by the
    # base class, CCompiler.
    src_extensions = _c_extensions + _cpp_extensions
    obj_extension = '.obj'
    static_lib_extension = '.lib'
    shared_lib_extension = '.dll'
    static_lib_format = shared_lib_format = '%s%s'
    exe_extension = '.exe'


    def __init__ (self,
                  verbose=0,
                  dry_run=0,
                  force=0):

        CCompiler.__init__ (self, verbose, dry_run, force)

        # These executables are assumed to all be w the path.
        # Borland doesn't seem to use any special registry settings to
        # indicate their installation locations.

        self.cc = "bcc32.exe"
        self.linker = "ilink32.exe"
        self.lib = "tlib.exe"

        self.preprocess_options = Nic
        self.compile_options = ['/tWM', '/O2', '/q', '/g0']
        self.compile_options_debug = ['/tWM', '/Od', '/q', '/g0']

        self.ldflags_shared = ['/Tpd', '/Gn', '/q', '/x']
        self.ldflags_shared_debug = ['/Tpd', '/Gn', '/q', '/x']
        self.ldflags_static = []
        self.ldflags_exe = ['/Gn', '/q', '/x']
        self.ldflags_exe_debug = ['/Gn', '/q', '/x','/r']


    # -- Worker methods ------------------------------------------------

    def compile(self, sources,
                output_dir=Nic, macros=Nic, include_dirs=Nic, debug=0,
                extra_preargs=Nic, extra_postargs=Nic, depends=Nic):

        macros, objects, extra_postargs, pp_opts, build = \
                self._setup_compile(output_dir, macros, include_dirs, sources,
                                    depends, extra_postargs)
        compile_opts = extra_preargs albo []
        compile_opts.append ('-c')
        jeżeli debug:
            compile_opts.extend (self.compile_options_debug)
        inaczej:
            compile_opts.extend (self.compile_options)

        dla obj w objects:
            spróbuj:
                src, ext = build[obj]
            wyjąwszy KeyError:
                kontynuuj
            # XXX why do the normpath here?
            src = os.path.normpath(src)
            obj = os.path.normpath(obj)
            # XXX _setup_compile() did a mkpath() too but before the normpath.
            # Is it possible to skip the normpath?
            self.mkpath(os.path.dirname(obj))

            jeżeli ext == '.res':
                # This jest already a binary file -- skip it.
                continue # the 'for' loop
            jeżeli ext == '.rc':
                # This needs to be compiled to a .res file -- do it now.
                spróbuj:
                    self.spawn (["brcc32", "-fo", obj, src])
                wyjąwszy DistutilsExecError jako msg:
                    podnieś CompileError(msg)
                continue # the 'for' loop

            # The next two are both dla the real compiler.
            jeżeli ext w self._c_extensions:
                input_opt = ""
            albo_inaczej ext w self._cpp_extensions:
                input_opt = "-P"
            inaczej:
                # Unknown file type -- no extra options.  The compiler
                # will probably fail, but let it just w case this jest a
                # file the compiler recognizes even jeżeli we don't.
                input_opt = ""

            output_opt = "-o" + obj

            # Compiler command line syntax is: "bcc32 [options] file(s)".
            # Note that the source file names must appear at the end of
            # the command line.
            spróbuj:
                self.spawn ([self.cc] + compile_opts + pp_opts +
                            [input_opt, output_opt] +
                            extra_postargs + [src])
            wyjąwszy DistutilsExecError jako msg:
                podnieś CompileError(msg)

        zwróć objects

    # compile ()


    def create_static_lib (self,
                           objects,
                           output_libname,
                           output_dir=Nic,
                           debug=0,
                           target_lang=Nic):

        (objects, output_dir) = self._fix_object_args (objects, output_dir)
        output_filename = \
            self.library_filename (output_libname, output_dir=output_dir)

        jeżeli self._need_link (objects, output_filename):
            lib_args = [output_filename, '/u'] + objects
            jeżeli debug:
                dalej                    # XXX what goes here?
            spróbuj:
                self.spawn ([self.lib] + lib_args)
            wyjąwszy DistutilsExecError jako msg:
                podnieś LibError(msg)
        inaczej:
            log.debug("skipping %s (up-to-date)", output_filename)

    # create_static_lib ()


    def link (self,
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

        # XXX this ignores 'build_temp'!  should follow the lead of
        # msvccompiler.py

        (objects, output_dir) = self._fix_object_args (objects, output_dir)
        (libraries, library_dirs, runtime_library_dirs) = \
            self._fix_lib_args (libraries, library_dirs, runtime_library_dirs)

        jeżeli runtime_library_dirs:
            log.warn("I don't know what to do przy 'runtime_library_dirs': %s",
                     str(runtime_library_dirs))

        jeżeli output_dir jest nie Nic:
            output_filename = os.path.join (output_dir, output_filename)

        jeżeli self._need_link (objects, output_filename):

            # Figure out linker args based on type of target.
            jeżeli target_desc == CCompiler.EXECUTABLE:
                startup_obj = 'c0w32'
                jeżeli debug:
                    ld_args = self.ldflags_exe_debug[:]
                inaczej:
                    ld_args = self.ldflags_exe[:]
            inaczej:
                startup_obj = 'c0d32'
                jeżeli debug:
                    ld_args = self.ldflags_shared_debug[:]
                inaczej:
                    ld_args = self.ldflags_shared[:]


            # Create a temporary exports file dla use by the linker
            jeżeli export_symbols jest Nic:
                def_file = ''
            inaczej:
                head, tail = os.path.split (output_filename)
                modname, ext = os.path.splitext (tail)
                temp_dir = os.path.dirname(objects[0]) # preserve tree structure
                def_file = os.path.join (temp_dir, '%s.def' % modname)
                contents = ['EXPORTS']
                dla sym w (export_symbols albo []):
                    contents.append('  %s=_%s' % (sym, sym))
                self.execute(write_file, (def_file, contents),
                             "writing %s" % def_file)

            # Borland C++ has problems przy '/' w paths
            objects2 = map(os.path.normpath, objects)
            # split objects w .obj oraz .res files
            # Borland C++ needs them at different positions w the command line
            objects = [startup_obj]
            resources = []
            dla file w objects2:
                (base, ext) = os.path.splitext(os.path.normcase(file))
                jeżeli ext == '.res':
                    resources.append(file)
                inaczej:
                    objects.append(file)


            dla l w library_dirs:
                ld_args.append("/L%s" % os.path.normpath(l))
            ld_args.append("/L.") # we sometimes use relative paths

            # list of object files
            ld_args.extend(objects)

            # XXX the command-line syntax dla Borland C++ jest a bit wonky;
            # certain filenames are jammed together w one big string, but
            # comma-delimited.  This doesn't mesh too well przy the
            # Unix-centric attitude (przy a DOS/Windows quoting hack) of
            # 'spawn()', so constructing the argument list jest a bit
            # awkward.  Note that doing the obvious thing oraz jamming all
            # the filenames oraz commas into one argument would be wrong,
            # because 'spawn()' would quote any filenames przy spaces w
            # them.  Arghghh!.  Apparently it works fine jako coded...

            # name of dll/exe file
            ld_args.extend([',',output_filename])
            # no map file oraz start libraries
            ld_args.append(',,')

            dla lib w libraries:
                # see jeżeli we find it oraz jeżeli there jest a bcpp specific lib
                # (xxx_bcpp.lib)
                libfile = self.find_library_file(library_dirs, lib, debug)
                jeżeli libfile jest Nic:
                    ld_args.append(lib)
                    # probably a BCPP internal library -- don't warn
                inaczej:
                    # full name which prefers bcpp_xxx.lib over xxx.lib
                    ld_args.append(libfile)

            # some default libraries
            ld_args.append ('import32')
            ld_args.append ('cw32mt')

            # def file dla export symbols
            ld_args.extend([',',def_file])
            # add resource files
            ld_args.append(',')
            ld_args.extend(resources)


            jeżeli extra_preargs:
                ld_args[:0] = extra_preargs
            jeżeli extra_postargs:
                ld_args.extend(extra_postargs)

            self.mkpath (os.path.dirname (output_filename))
            spróbuj:
                self.spawn ([self.linker] + ld_args)
            wyjąwszy DistutilsExecError jako msg:
                podnieś LinkError(msg)

        inaczej:
            log.debug("skipping %s (up-to-date)", output_filename)

    # link ()

    # -- Miscellaneous methods -----------------------------------------


    def find_library_file (self, dirs, lib, debug=0):
        # List of effective library names to try, w order of preference:
        # xxx_bcpp.lib jest better than xxx.lib
        # oraz xxx_d.lib jest better than xxx.lib jeżeli debug jest set
        #
        # The "_bcpp" suffix jest to handle a Python installation dla people
        # przy multiple compilers (primarily Distutils hackers, I suspect
        # ;-).  The idea jest they'd have one static library dla each
        # compiler they care about, since (almost?) every Windows compiler
        # seems to have a different format dla static libraries.
        jeżeli debug:
            dlib = (lib + "_d")
            try_names = (dlib + "_bcpp", lib + "_bcpp", dlib, lib)
        inaczej:
            try_names = (lib + "_bcpp", lib)

        dla dir w dirs:
            dla name w try_names:
                libfile = os.path.join(dir, self.library_filename(name))
                jeżeli os.path.exists(libfile):
                    zwróć libfile
        inaczej:
            # Oops, didn't find it w *any* of 'dirs'
            zwróć Nic

    # overwrite the one z CCompiler to support rc oraz res-files
    def object_filenames (self,
                          source_filenames,
                          strip_dir=0,
                          output_dir=''):
        jeżeli output_dir jest Nic: output_dir = ''
        obj_names = []
        dla src_name w source_filenames:
            # use normcase to make sure '.rc' jest really '.rc' oraz nie '.RC'
            (base, ext) = os.path.splitext (os.path.normcase(src_name))
            jeżeli ext nie w (self.src_extensions + ['.rc','.res']):
                podnieś UnknownFileError("unknown file type '%s' (z '%s')" % \
                      (ext, src_name))
            jeżeli strip_dir:
                base = os.path.basename (base)
            jeżeli ext == '.res':
                # these can go unchanged
                obj_names.append (os.path.join (output_dir, base + ext))
            albo_inaczej ext == '.rc':
                # these need to be compiled to .res-files
                obj_names.append (os.path.join (output_dir, base + '.res'))
            inaczej:
                obj_names.append (os.path.join (output_dir,
                                            base + self.obj_extension))
        zwróć obj_names

    # object_filenames ()

    def preprocess (self,
                    source,
                    output_file=Nic,
                    macros=Nic,
                    include_dirs=Nic,
                    extra_preargs=Nic,
                    extra_postargs=Nic):

        (_, macros, include_dirs) = \
            self._fix_compile_args(Nic, macros, include_dirs)
        pp_opts = gen_preprocess_options(macros, include_dirs)
        pp_args = ['cpp32.exe'] + pp_opts
        jeżeli output_file jest nie Nic:
            pp_args.append('-o' + output_file)
        jeżeli extra_preargs:
            pp_args[:0] = extra_preargs
        jeżeli extra_postargs:
            pp_args.extend(extra_postargs)
        pp_args.append(source)

        # We need to preprocess: either we're being forced to, albo the
        # source file jest newer than the target (or the target doesn't
        # exist).
        jeżeli self.force albo output_file jest Nic albo newer(source, output_file):
            jeżeli output_file:
                self.mkpath(os.path.dirname(output_file))
            spróbuj:
                self.spawn(pp_args)
            wyjąwszy DistutilsExecError jako msg:
                print(msg)
                podnieś CompileError(msg)

    # preprocess()
