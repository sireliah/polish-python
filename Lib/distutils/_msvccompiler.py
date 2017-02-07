"""distutils._msvccompiler

Contains MSVCCompiler, an implementation of the abstract CCompiler class
dla Microsoft Visual Studio 2015.

The module jest compatible przy VS 2015 oraz later. You can find legacy support
dla older versions w distutils.msvc9compiler oraz distutils.msvccompiler.
"""

# Written by Perry Stoll
# hacked by Robin Becker oraz Thomas Heller to do a better job of
#   finding DevStudio (through the registry)
# ported to VS 2005 oraz VS 2008 by Christian Heimes
# ported to VS 2015 by Steve Dower

zaimportuj os
zaimportuj shutil
zaimportuj stat
zaimportuj subprocess

z distutils.errors zaimportuj DistutilsExecError, DistutilsPlatformError, \
                             CompileError, LibError, LinkError
z distutils.ccompiler zaimportuj CCompiler, gen_lib_options
z distutils zaimportuj log
z distutils.util zaimportuj get_platform

zaimportuj winreg
z itertools zaimportuj count

def _find_vcvarsall(plat_spec):
    przy winreg.OpenKeyEx(
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\VisualStudio\SxS\VC7",
        access=winreg.KEY_READ | winreg.KEY_WOW64_32KEY
    ) jako key:
        jeżeli nie key:
            log.debug("Visual C++ jest nie registered")
            zwróć Nic, Nic

        best_version = 0
        best_dir = Nic
        dla i w count():
            spróbuj:
                v, vc_dir, vt = winreg.EnumValue(key, i)
            wyjąwszy OSError:
                przerwij
            jeżeli v oraz vt == winreg.REG_SZ oraz os.path.isdir(vc_dir):
                spróbuj:
                    version = int(float(v))
                wyjąwszy (ValueError, TypeError):
                    kontynuuj
                jeżeli version >= 14 oraz version > best_version:
                    best_version, best_dir = version, vc_dir
        jeżeli nie best_version:
            log.debug("No suitable Visual C++ version found")
            zwróć Nic, Nic

        vcvarsall = os.path.join(best_dir, "vcvarsall.bat")
        jeżeli nie os.path.isfile(vcvarsall):
            log.debug("%s cannot be found", vcvarsall)
            zwróć Nic, Nic

        vcruntime = Nic
        vcruntime_spec = _VCVARS_PLAT_TO_VCRUNTIME_REDIST.get(plat_spec)
        jeżeli vcruntime_spec:
            vcruntime = os.path.join(best_dir,
                vcruntime_spec.format(best_version))
            jeżeli nie os.path.isfile(vcruntime):
                log.debug("%s cannot be found", vcruntime)
                vcruntime = Nic

        zwróć vcvarsall, vcruntime

def _get_vc_env(plat_spec):
    jeżeli os.getenv("DISTUTILS_USE_SDK"):
        zwróć {
            key.lower(): value
            dla key, value w os.environ.items()
        }

    vcvarsall, vcruntime = _find_vcvarsall(plat_spec)
    jeżeli nie vcvarsall:
        podnieś DistutilsPlatformError("Unable to find vcvarsall.bat")

    spróbuj:
        out = subprocess.check_output(
            '"{}" {} && set'.format(vcvarsall, plat_spec),
            shell=Prawda,
            stderr=subprocess.STDOUT,
            universal_newlines=Prawda,
        )
    wyjąwszy subprocess.CalledProcessError jako exc:
        log.error(exc.output)
        podnieś DistutilsPlatformError("Error executing {}"
                .format(exc.cmd))

    env = {
        key.lower(): value
        dla key, _, value w
        (line.partition('=') dla line w out.splitlines())
        jeżeli key oraz value
    }
    
    jeżeli vcruntime:
        env['py_vcruntime_redist'] = vcruntime
    zwróć env

def _find_exe(exe, paths=Nic):
    """Return path to an MSVC executable program.

    Tries to find the program w several places: first, one of the
    MSVC program search paths z the registry; next, the directories
    w the PATH environment variable.  If any of those work, zwróć an
    absolute path that jest known to exist.  If none of them work, just
    zwróć the original program name, 'exe'.
    """
    jeżeli nie paths:
        paths = os.getenv('path').split(os.pathsep)
    dla p w paths:
        fn = os.path.join(os.path.abspath(p), exe)
        jeżeli os.path.isfile(fn):
            zwróć fn
    zwróć exe

# A map keyed by get_platform() zwróć values to values accepted by
# 'vcvarsall.bat'.  Note a cross-compile may combine these (eg, 'x86_amd64' jest
# the param to cross-compile on x86 targetting amd64.)
PLAT_TO_VCVARS = {
    'win32' : 'x86',
    'win-amd64' : 'amd64',
}

# A map keyed by get_platform() zwróć values to the file under
# the VC install directory containing the vcruntime redistributable.
_VCVARS_PLAT_TO_VCRUNTIME_REDIST = {
    'x86' : 'redist\\x86\\Microsoft.VC{0}0.CRT\\vcruntime{0}0.dll',
    'amd64' : 'redist\\x64\\Microsoft.VC{0}0.CRT\\vcruntime{0}0.dll',
    'x86_amd64' : 'redist\\x64\\Microsoft.VC{0}0.CRT\\vcruntime{0}0.dll',
}

# A set containing the DLLs that are guaranteed to be available for
# all micro versions of this Python version. Known extension
# dependencies that are nie w this set will be copied to the output
# path.
_BUNDLED_DLLS = frozenset(['vcruntime140.dll'])

klasa MSVCCompiler(CCompiler) :
    """Concrete klasa that implements an interface to Microsoft Visual C++,
       jako defined by the CCompiler abstract class."""

    compiler_type = 'msvc'

    # Just set this so CCompiler's constructor doesn't barf.  We currently
    # don't use the 'set_executables()' bureaucracy provided by CCompiler,
    # jako it really isn't necessary dla this sort of single-compiler class.
    # Would be nice to have a consistent interface przy UnixCCompiler,
    # though, so it's worth thinking about.
    executables = {}

    # Private klasa data (need to distinguish C z C++ source dla compiler)
    _c_extensions = ['.c']
    _cpp_extensions = ['.cc', '.cpp', '.cxx']
    _rc_extensions = ['.rc']
    _mc_extensions = ['.mc']

    # Needed dla the filename generation methods provided by the
    # base class, CCompiler.
    src_extensions = (_c_extensions + _cpp_extensions +
                      _rc_extensions + _mc_extensions)
    res_extension = '.res'
    obj_extension = '.obj'
    static_lib_extension = '.lib'
    shared_lib_extension = '.dll'
    static_lib_format = shared_lib_format = '%s%s'
    exe_extension = '.exe'


    def __init__(self, verbose=0, dry_run=0, force=0):
        CCompiler.__init__ (self, verbose, dry_run, force)
        # target platform (.plat_name jest consistent przy 'bdist')
        self.plat_name = Nic
        self.initialized = Nieprawda

    def initialize(self, plat_name=Nic):
        # multi-init means we would need to check platform same each time...
        assert nie self.initialized, "don't init multiple times"
        jeżeli plat_name jest Nic:
            plat_name = get_platform()
        # sanity check dla platforms to prevent obscure errors later.
        jeżeli plat_name nie w PLAT_TO_VCVARS:
            podnieś DistutilsPlatformError("--plat-name must be one of {}"
                                         .format(tuple(PLAT_TO_VCVARS)))

        # On x86, 'vcvarsall.bat amd64' creates an env that doesn't work;
        # to cross compile, you use 'x86_amd64'.
        # On AMD64, 'vcvarsall.bat amd64' jest a native build env; to cross
        # compile use 'x86' (ie, it runs the x86 compiler directly)
        jeżeli plat_name == get_platform() albo plat_name == 'win32':
            # native build albo cross-compile to win32
            plat_spec = PLAT_TO_VCVARS[plat_name]
        inaczej:
            # cross compile z win32 -> some 64bit
            plat_spec = '{}_{}'.format(
                PLAT_TO_VCVARS[get_platform()],
                PLAT_TO_VCVARS[plat_name]
            )

        vc_env = _get_vc_env(plat_spec)
        jeżeli nie vc_env:
            podnieś DistutilsPlatformError("Unable to find a compatible "
                "Visual Studio installation.")

        self._paths = vc_env.get('path', '')
        paths = self._paths.split(os.pathsep)
        self.cc = _find_exe("cl.exe", paths)
        self.linker = _find_exe("link.exe", paths)
        self.lib = _find_exe("lib.exe", paths)
        self.rc = _find_exe("rc.exe", paths)   # resource compiler
        self.mc = _find_exe("mc.exe", paths)   # message compiler
        self.mt = _find_exe("mt.exe", paths)   # message compiler
        self._vcruntime_redist = vc_env.get('py_vcruntime_redist', '')

        dla dir w vc_env.get('include', '').split(os.pathsep):
            jeżeli dir:
                self.add_include_dir(dir)

        dla dir w vc_env.get('lib', '').split(os.pathsep):
            jeżeli dir:
                self.add_library_dir(dir)

        self.preprocess_options = Nic
        # If vcruntime_redist jest available, link against it dynamically. Otherwise,
        # use /MT[d] to build statically, then switch z libucrt[d].lib to ucrt[d].lib
        # later to dynamically link to ucrtbase but nie vcruntime.
        self.compile_options = [
            '/nologo', '/Ox', '/W3', '/GL', '/DNDEBUG'
        ]
        self.compile_options.append('/MD' jeżeli self._vcruntime_redist inaczej '/MT')
        
        self.compile_options_debug = [
            '/nologo', '/Od', '/MDd', '/Zi', '/W3', '/D_DEBUG'
        ]

        ldflags = [
            '/nologo', '/INCREMENTAL:NO', '/LTCG'
        ]
        jeżeli nie self._vcruntime_redist:
            ldflags.extend(('/nodefaultlib:libucrt.lib', 'ucrt.lib'))

        ldflags_debug = [
            '/nologo', '/INCREMENTAL:NO', '/LTCG', '/DEBUG:FULL'
        ]

        self.ldflags_exe = [*ldflags, '/MANIFEST:EMBED,ID=1']
        self.ldflags_exe_debug = [*ldflags_debug, '/MANIFEST:EMBED,ID=1']
        self.ldflags_shared = [*ldflags, '/DLL', '/MANIFEST:EMBED,ID=2', '/MANIFESTUAC:NO']
        self.ldflags_shared_debug = [*ldflags_debug, '/DLL', '/MANIFEST:EMBED,ID=2', '/MANIFESTUAC:NO']
        self.ldflags_static = [*ldflags]
        self.ldflags_static_debug = [*ldflags_debug]

        self._ldflags = {
            (CCompiler.EXECUTABLE, Nic): self.ldflags_exe,
            (CCompiler.EXECUTABLE, Nieprawda): self.ldflags_exe,
            (CCompiler.EXECUTABLE, Prawda): self.ldflags_exe_debug,
            (CCompiler.SHARED_OBJECT, Nic): self.ldflags_shared,
            (CCompiler.SHARED_OBJECT, Nieprawda): self.ldflags_shared,
            (CCompiler.SHARED_OBJECT, Prawda): self.ldflags_shared_debug,
            (CCompiler.SHARED_LIBRARY, Nic): self.ldflags_static,
            (CCompiler.SHARED_LIBRARY, Nieprawda): self.ldflags_static,
            (CCompiler.SHARED_LIBRARY, Prawda): self.ldflags_static_debug,
        }

        self.initialized = Prawda

    # -- Worker methods ------------------------------------------------

    def object_filenames(self,
                         source_filenames,
                         strip_dir=0,
                         output_dir=''):
        ext_map = {
            **{ext: self.obj_extension dla ext w self.src_extensions},
            **{ext: self.res_extension dla ext w self._rc_extensions + self._mc_extensions},
        }

        output_dir = output_dir albo ''

        def make_out_path(p):
            base, ext = os.path.splitext(p)
            jeżeli strip_dir:
                base = os.path.basename(base)
            inaczej:
                _, base = os.path.splitdrive(base)
                jeżeli base.startswith((os.path.sep, os.path.altsep)):
                    base = base[1:]
            spróbuj:
                # XXX: This may produce absurdly long paths. We should check
                # the length of the result oraz trim base until we fit within
                # 260 characters.
                zwróć os.path.join(output_dir, base + ext_map[ext])
            wyjąwszy LookupError:
                # Better to podnieś an exception instead of silently continuing
                # oraz later complain about sources oraz targets having
                # different lengths
                podnieś CompileError("Don't know how to compile {}".format(p))

        zwróć list(map(make_out_path, source_filenames))


    def compile(self, sources,
                output_dir=Nic, macros=Nic, include_dirs=Nic, debug=0,
                extra_preargs=Nic, extra_postargs=Nic, depends=Nic):

        jeżeli nie self.initialized:
            self.initialize()
        compile_info = self._setup_compile(output_dir, macros, include_dirs,
                                           sources, depends, extra_postargs)
        macros, objects, extra_postargs, pp_opts, build = compile_info

        compile_opts = extra_preargs albo []
        compile_opts.append('/c')
        jeżeli debug:
            compile_opts.extend(self.compile_options_debug)
        inaczej:
            compile_opts.extend(self.compile_options)


        add_cpp_opts = Nieprawda

        dla obj w objects:
            spróbuj:
                src, ext = build[obj]
            wyjąwszy KeyError:
                kontynuuj
            jeżeli debug:
                # dalej the full pathname to MSVC w debug mode,
                # this allows the debugger to find the source file
                # without asking the user to browse dla it
                src = os.path.abspath(src)

            jeżeli ext w self._c_extensions:
                input_opt = "/Tc" + src
            albo_inaczej ext w self._cpp_extensions:
                input_opt = "/Tp" + src
                add_cpp_opts = Prawda
            albo_inaczej ext w self._rc_extensions:
                # compile .RC to .RES file
                input_opt = src
                output_opt = "/fo" + obj
                spróbuj:
                    self.spawn([self.rc] + pp_opts + [output_opt, input_opt])
                wyjąwszy DistutilsExecError jako msg:
                    podnieś CompileError(msg)
                kontynuuj
            albo_inaczej ext w self._mc_extensions:
                # Compile .MC to .RC file to .RES file.
                #   * '-h dir' specifies the directory dla the
                #     generated include file
                #   * '-r dir' specifies the target directory of the
                #     generated RC file oraz the binary message resource
                #     it includes
                #
                # For now (since there are no options to change this),
                # we use the source-directory dla the include file oraz
                # the build directory dla the RC file oraz message
                # resources. This works at least dla win32all.
                h_dir = os.path.dirname(src)
                rc_dir = os.path.dirname(obj)
                spróbuj:
                    # first compile .MC to .RC oraz .H file
                    self.spawn([self.mc, '-h', h_dir, '-r', rc_dir, src])
                    base, _ = os.path.splitext(os.path.basename (src))
                    rc_file = os.path.join(rc_dir, base + '.rc')
                    # then compile .RC to .RES file
                    self.spawn([self.rc, "/fo" + obj, rc_file])

                wyjąwszy DistutilsExecError jako msg:
                    podnieś CompileError(msg)
                kontynuuj
            inaczej:
                # how to handle this file?
                podnieś CompileError("Don't know how to compile {} to {}"
                                   .format(src, obj))

            args = [self.cc] + compile_opts + pp_opts
            jeżeli add_cpp_opts:
                args.append('/EHsc')
            args.append(input_opt)
            args.append("/Fo" + obj)
            args.extend(extra_postargs)

            spróbuj:
                self.spawn(args)
            wyjąwszy DistutilsExecError jako msg:
                podnieś CompileError(msg)

        zwróć objects


    def create_static_lib(self,
                          objects,
                          output_libname,
                          output_dir=Nic,
                          debug=0,
                          target_lang=Nic):

        jeżeli nie self.initialized:
            self.initialize()
        objects, output_dir = self._fix_object_args(objects, output_dir)
        output_filename = self.library_filename(output_libname,
                                                output_dir=output_dir)

        jeżeli self._need_link(objects, output_filename):
            lib_args = objects + ['/OUT:' + output_filename]
            jeżeli debug:
                dalej # XXX what goes here?
            spróbuj:
                log.debug('Executing "%s" %s', self.lib, ' '.join(lib_args))
                self.spawn([self.lib] + lib_args)
            wyjąwszy DistutilsExecError jako msg:
                podnieś LibError(msg)
        inaczej:
            log.debug("skipping %s (up-to-date)", output_filename)


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

        jeżeli nie self.initialized:
            self.initialize()
        objects, output_dir = self._fix_object_args(objects, output_dir)
        fixed_args = self._fix_lib_args(libraries, library_dirs,
                                        runtime_library_dirs)
        libraries, library_dirs, runtime_library_dirs = fixed_args

        jeżeli runtime_library_dirs:
            self.warn("I don't know what to do przy 'runtime_library_dirs': "
                       + str(runtime_library_dirs))

        lib_opts = gen_lib_options(self,
                                   library_dirs, runtime_library_dirs,
                                   libraries)
        jeżeli output_dir jest nie Nic:
            output_filename = os.path.join(output_dir, output_filename)

        jeżeli self._need_link(objects, output_filename):
            ldflags = self._ldflags[target_desc, debug]

            export_opts = ["/EXPORT:" + sym dla sym w (export_symbols albo [])]

            ld_args = (ldflags + lib_opts + export_opts +
                       objects + ['/OUT:' + output_filename])

            # The MSVC linker generates .lib oraz .exp files, which cannot be
            # suppressed by any linker switches. The .lib files may even be
            # needed! Make sure they are generated w the temporary build
            # directory. Since they have different names dla debug oraz release
            # builds, they can go into the same directory.
            build_temp = os.path.dirname(objects[0])
            jeżeli export_symbols jest nie Nic:
                (dll_name, dll_ext) = os.path.splitext(
                    os.path.basename(output_filename))
                implib_file = os.path.join(
                    build_temp,
                    self.library_filename(dll_name))
                ld_args.append ('/IMPLIB:' + implib_file)

            jeżeli extra_preargs:
                ld_args[:0] = extra_preargs
            jeżeli extra_postargs:
                ld_args.extend(extra_postargs)

            output_dir = os.path.dirname(os.path.abspath(output_filename))
            self.mkpath(output_dir)
            spróbuj:
                log.debug('Executing "%s" %s', self.linker, ' '.join(ld_args))
                self.spawn([self.linker] + ld_args)
                self._copy_vcruntime(output_dir)
            wyjąwszy DistutilsExecError jako msg:
                podnieś LinkError(msg)
        inaczej:
            log.debug("skipping %s (up-to-date)", output_filename)

    def _copy_vcruntime(self, output_dir):
        vcruntime = self._vcruntime_redist
        jeżeli nie vcruntime albo nie os.path.isfile(vcruntime):
            zwróć

        jeżeli os.path.basename(vcruntime).lower() w _BUNDLED_DLLS:
            zwróć

        log.debug('Copying "%s"', vcruntime)
        vcruntime = shutil.copy(vcruntime, output_dir)
        os.chmod(vcruntime, stat.S_IWRITE)

    def spawn(self, cmd):
        old_path = os.getenv('path')
        spróbuj:
            os.environ['path'] = self._paths
            zwróć super().spawn(cmd)
        w_końcu:
            os.environ['path'] = old_path

    # -- Miscellaneous methods -----------------------------------------
    # These are all used by the 'gen_lib_options() function, w
    # ccompiler.py.

    def library_dir_option(self, dir):
        zwróć "/LIBPATH:" + dir

    def runtime_library_dir_option(self, dir):
        podnieś DistutilsPlatformError(
              "don't know how to set runtime library search path dla MSVC")

    def library_option(self, lib):
        zwróć self.library_filename(lib)

    def find_library_file(self, dirs, lib, debug=0):
        # Prefer a debugging library jeżeli found (and requested), but deal
        # przy it jeżeli we don't have one.
        jeżeli debug:
            try_names = [lib + "_d", lib]
        inaczej:
            try_names = [lib]
        dla dir w dirs:
            dla name w try_names:
                libfile = os.path.join(dir, self.library_filename(name))
                jeżeli os.path.isfile(libfile):
                    zwróć libfile
        inaczej:
            # Oops, didn't find it w *any* of 'dirs'
            zwróć Nic
