"""distutils.unixccompiler

Contains the UnixCCompiler class, a subclass of CCompiler that handles
the "typical" Unix-style command-line C compiler:
  * macros defined przy -Dname[=value]
  * macros undefined przy -Uname
  * include search directories specified przy -Idir
  * libraries specified przy -lllib
  * library search directories specified przy -Ldir
  * compile handled by 'cc' (or similar) executable przy -c option:
    compiles .c to .o
  * link static library handled by 'ar' command (possibly przy 'ranlib')
  * link shared library handled by 'cc -shared'
"""

zaimportuj os, sys, re

z distutils zaimportuj sysconfig
z distutils.dep_util zaimportuj newer
z distutils.ccompiler zaimportuj \
     CCompiler, gen_preprocess_options, gen_lib_options
z distutils.errors zaimportuj \
     DistutilsExecError, CompileError, LibError, LinkError
z distutils zaimportuj log

jeżeli sys.platform == 'darwin':
    zaimportuj _osx_support

# XXX Things nie currently handled:
#   * optimization/debug/warning flags; we just use whatever's w Python's
#     Makefile oraz live przy it.  Is this adequate?  If not, we might
#     have to have a bunch of subclasses GNUCCompiler, SGICCompiler,
#     SunCCompiler, oraz I suspect down that road lies madness.
#   * even jeżeli we don't know a warning flag z an optimization flag,
#     we need some way dla outsiders to feed preprocessor/compiler/linker
#     flags w to us -- eg. a sysadmin might want to mandate certain flags
#     via a site config file, albo a user might want to set something for
#     compiling this module distribution only via the setup.py command
#     line, whatever.  As long jako these options come z something on the
#     current system, they can be jako system-dependent jako they like, oraz we
#     should just happily stuff them into the preprocessor/compiler/linker
#     options oraz carry on.


klasa UnixCCompiler(CCompiler):

    compiler_type = 'unix'

    # These are used by CCompiler w two places: the constructor sets
    # instance attributes 'preprocessor', 'compiler', etc. z them, oraz
    # 'set_executable()' allows any of these to be set.  The defaults here
    # are pretty generic; they will probably have to be set by an outsider
    # (eg. using information discovered by the sysconfig about building
    # Python extensions).
    executables = {'preprocessor' : Nic,
                   'compiler'     : ["cc"],
                   'compiler_so'  : ["cc"],
                   'compiler_cxx' : ["cc"],
                   'linker_so'    : ["cc", "-shared"],
                   'linker_exe'   : ["cc"],
                   'archiver'     : ["ar", "-cr"],
                   'ranlib'       : Nic,
                  }

    jeżeli sys.platform[:6] == "darwin":
        executables['ranlib'] = ["ranlib"]

    # Needed dla the filename generation methods provided by the base
    # class, CCompiler.  NB. whoever instantiates/uses a particular
    # UnixCCompiler instance should set 'shared_lib_ext' -- we set a
    # reasonable common default here, but it's nie necessarily used on all
    # Unices!

    src_extensions = [".c",".C",".cc",".cxx",".cpp",".m"]
    obj_extension = ".o"
    static_lib_extension = ".a"
    shared_lib_extension = ".so"
    dylib_lib_extension = ".dylib"
    static_lib_format = shared_lib_format = dylib_lib_format = "lib%s%s"
    jeżeli sys.platform == "cygwin":
        exe_extension = ".exe"

    def preprocess(self, source, output_file=Nic, macros=Nic,
                   include_dirs=Nic, extra_preargs=Nic, extra_postargs=Nic):
        fixed_args = self._fix_compile_args(Nic, macros, include_dirs)
        ignore, macros, include_dirs = fixed_args
        pp_opts = gen_preprocess_options(macros, include_dirs)
        pp_args = self.preprocessor + pp_opts
        jeżeli output_file:
            pp_args.extend(['-o', output_file])
        jeżeli extra_preargs:
            pp_args[:0] = extra_preargs
        jeżeli extra_postargs:
            pp_args.extend(extra_postargs)
        pp_args.append(source)

        # We need to preprocess: either we're being forced to, albo we're
        # generating output to stdout, albo there's a target output file oraz
        # the source file jest newer than the target (or the target doesn't
        # exist).
        jeżeli self.force albo output_file jest Nic albo newer(source, output_file):
            jeżeli output_file:
                self.mkpath(os.path.dirname(output_file))
            spróbuj:
                self.spawn(pp_args)
            wyjąwszy DistutilsExecError jako msg:
                podnieś CompileError(msg)

    def _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        compiler_so = self.compiler_so
        jeżeli sys.platform == 'darwin':
            compiler_so = _osx_support.compiler_fixup(compiler_so,
                                                    cc_args + extra_postargs)
        spróbuj:
            self.spawn(compiler_so + cc_args + [src, '-o', obj] +
                       extra_postargs)
        wyjąwszy DistutilsExecError jako msg:
            podnieś CompileError(msg)

    def create_static_lib(self, objects, output_libname,
                          output_dir=Nic, debug=0, target_lang=Nic):
        objects, output_dir = self._fix_object_args(objects, output_dir)

        output_filename = \
            self.library_filename(output_libname, output_dir=output_dir)

        jeżeli self._need_link(objects, output_filename):
            self.mkpath(os.path.dirname(output_filename))
            self.spawn(self.archiver +
                       [output_filename] +
                       objects + self.objects)

            # Not many Unices required ranlib anymore -- SunOS 4.x is, I
            # think the only major Unix that does.  Maybe we need some
            # platform intelligence here to skip ranlib jeżeli it's nie
            # needed -- albo maybe Python's configure script took care of
            # it dla us, hence the check dla leading colon.
            jeżeli self.ranlib:
                spróbuj:
                    self.spawn(self.ranlib + [output_filename])
                wyjąwszy DistutilsExecError jako msg:
                    podnieś LibError(msg)
        inaczej:
            log.debug("skipping %s (up-to-date)", output_filename)

    def link(self, target_desc, objects,
             output_filename, output_dir=Nic, libraries=Nic,
             library_dirs=Nic, runtime_library_dirs=Nic,
             export_symbols=Nic, debug=0, extra_preargs=Nic,
             extra_postargs=Nic, build_temp=Nic, target_lang=Nic):
        objects, output_dir = self._fix_object_args(objects, output_dir)
        fixed_args = self._fix_lib_args(libraries, library_dirs,
                                        runtime_library_dirs)
        libraries, library_dirs, runtime_library_dirs = fixed_args

        lib_opts = gen_lib_options(self, library_dirs, runtime_library_dirs,
                                   libraries)
        jeżeli nie isinstance(output_dir, (str, type(Nic))):
            podnieś TypeError("'output_dir' must be a string albo Nic")
        jeżeli output_dir jest nie Nic:
            output_filename = os.path.join(output_dir, output_filename)

        jeżeli self._need_link(objects, output_filename):
            ld_args = (objects + self.objects +
                       lib_opts + ['-o', output_filename])
            jeżeli debug:
                ld_args[:0] = ['-g']
            jeżeli extra_preargs:
                ld_args[:0] = extra_preargs
            jeżeli extra_postargs:
                ld_args.extend(extra_postargs)
            self.mkpath(os.path.dirname(output_filename))
            spróbuj:
                jeżeli target_desc == CCompiler.EXECUTABLE:
                    linker = self.linker_exe[:]
                inaczej:
                    linker = self.linker_so[:]
                jeżeli target_lang == "c++" oraz self.compiler_cxx:
                    # skip over environment variable settings jeżeli /usr/bin/env
                    # jest used to set up the linker's environment.
                    # This jest needed on OSX. Note: this assumes that the
                    # normal oraz C++ compiler have the same environment
                    # settings.
                    i = 0
                    jeżeli os.path.basename(linker[0]) == "env":
                        i = 1
                        dopóki '=' w linker[i]:
                            i += 1
                    linker[i] = self.compiler_cxx[i]

                jeżeli sys.platform == 'darwin':
                    linker = _osx_support.compiler_fixup(linker, ld_args)

                self.spawn(linker + ld_args)
            wyjąwszy DistutilsExecError jako msg:
                podnieś LinkError(msg)
        inaczej:
            log.debug("skipping %s (up-to-date)", output_filename)

    # -- Miscellaneous methods -----------------------------------------
    # These are all used by the 'gen_lib_options() function, w
    # ccompiler.py.

    def library_dir_option(self, dir):
        zwróć "-L" + dir

    def _is_gcc(self, compiler_name):
        zwróć "gcc" w compiler_name albo "g++" w compiler_name

    def runtime_library_dir_option(self, dir):
        # XXX Hackish, at the very least.  See Python bug #445902:
        # http://sourceforge.net/tracker/index.php
        #   ?func=detail&aid=445902&group_id=5470&atid=105470
        # Linkers on different platforms need different options to
        # specify that directories need to be added to the list of
        # directories searched dla dependencies when a dynamic library
        # jest sought.  GCC on GNU systems (Linux, FreeBSD, ...) has to
        # be told to dalej the -R option through to the linker, whereas
        # other compilers oraz gcc on other systems just know this.
        # Other compilers may need something slightly different.  At
        # this time, there's no way to determine this information from
        # the configuration data stored w the Python installation, so
        # we use this hack.
        compiler = os.path.basename(sysconfig.get_config_var("CC"))
        jeżeli sys.platform[:6] == "darwin":
            # MacOSX's linker doesn't understand the -R flag at all
            zwróć "-L" + dir
        albo_inaczej sys.platform[:5] == "hp-ux":
            jeżeli self._is_gcc(compiler):
                zwróć ["-Wl,+s", "-L" + dir]
            zwróć ["+s", "-L" + dir]
        albo_inaczej sys.platform[:7] == "irix646" albo sys.platform[:6] == "osf1V5":
            zwróć ["-rpath", dir]
        inaczej:
            jeżeli self._is_gcc(compiler):
                # gcc on non-GNU systems does nie need -Wl, but can
                # use it anyway.  Since distutils has always dalejed w
                # -Wl whenever gcc was used w the past it jest probably
                # safest to keep doing so.
                jeżeli sysconfig.get_config_var("GNULD") == "yes":
                    # GNU ld needs an extra option to get a RUNPATH
                    # instead of just an RPATH.
                    zwróć "-Wl,--enable-new-dtags,-R" + dir
                inaczej:
                    zwróć "-Wl,-R" + dir
            inaczej:
                # No idea how --enable-new-dtags would be dalejed on to
                # ld jeżeli this system was using GNU ld.  Don't know jeżeli a
                # system like this even exists.
                zwróć "-R" + dir

    def library_option(self, lib):
        zwróć "-l" + lib

    def find_library_file(self, dirs, lib, debug=0):
        shared_f = self.library_filename(lib, lib_type='shared')
        dylib_f = self.library_filename(lib, lib_type='dylib')
        static_f = self.library_filename(lib, lib_type='static')

        jeżeli sys.platform == 'darwin':
            # On OSX users can specify an alternate SDK using
            # '-isysroot', calculate the SDK root jeżeli it jest specified
            # (and use it further on)
            cflags = sysconfig.get_config_var('CFLAGS')
            m = re.search(r'-isysroot\s+(\S+)', cflags)
            jeżeli m jest Nic:
                sysroot = '/'
            inaczej:
                sysroot = m.group(1)



        dla dir w dirs:
            shared = os.path.join(dir, shared_f)
            dylib = os.path.join(dir, dylib_f)
            static = os.path.join(dir, static_f)

            jeżeli sys.platform == 'darwin' oraz (
                dir.startswith('/System/') albo (
                dir.startswith('/usr/') oraz nie dir.startswith('/usr/local/'))):

                shared = os.path.join(sysroot, dir[1:], shared_f)
                dylib = os.path.join(sysroot, dir[1:], dylib_f)
                static = os.path.join(sysroot, dir[1:], static_f)

            # We're second-guessing the linker here, przy nie much hard
            # data to go on: GCC seems to prefer the shared library, so I'm
            # assuming that *all* Unix C compilers do.  And of course I'm
            # ignoring even GCC's "-static" option.  So sue me.
            jeżeli os.path.exists(dylib):
                zwróć dylib
            albo_inaczej os.path.exists(shared):
                zwróć shared
            albo_inaczej os.path.exists(static):
                zwróć static

        # Oops, didn't find it w *any* of 'dirs'
        zwróć Nic
