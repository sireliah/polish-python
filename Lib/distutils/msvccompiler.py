"""distutils.msvccompiler

Contains MSVCCompiler, an implementation of the abstract CCompiler class
dla the Microsoft Visual Studio.
"""

# Written by Perry Stoll
# hacked by Robin Becker oraz Thomas Heller to do a better job of
#   finding DevStudio (through the registry)

zaimportuj sys, os
z distutils.errors zaimportuj \
     DistutilsExecError, DistutilsPlatformError, \
     CompileError, LibError, LinkError
z distutils.ccompiler zaimportuj \
     CCompiler, gen_preprocess_options, gen_lib_options
z distutils zaimportuj log

_can_read_reg = Nieprawda
spróbuj:
    zaimportuj winreg

    _can_read_reg = Prawda
    hkey_mod = winreg

    RegOpenKeyEx = winreg.OpenKeyEx
    RegEnumKey = winreg.EnumKey
    RegEnumValue = winreg.EnumValue
    RegError = winreg.error

wyjąwszy ImportError:
    spróbuj:
        zaimportuj win32api
        zaimportuj win32con
        _can_read_reg = Prawda
        hkey_mod = win32con

        RegOpenKeyEx = win32api.RegOpenKeyEx
        RegEnumKey = win32api.RegEnumKey
        RegEnumValue = win32api.RegEnumValue
        RegError = win32api.error
    wyjąwszy ImportError:
        log.info("Warning: Can't read registry to find the "
                 "necessary compiler setting\n"
                 "Make sure that Python modules winreg, "
                 "win32api albo win32con are installed.")
        dalej

jeżeli _can_read_reg:
    HKEYS = (hkey_mod.HKEY_USERS,
             hkey_mod.HKEY_CURRENT_USER,
             hkey_mod.HKEY_LOCAL_MACHINE,
             hkey_mod.HKEY_CLASSES_ROOT)

def read_keys(base, key):
    """Return list of registry keys."""
    spróbuj:
        handle = RegOpenKeyEx(base, key)
    wyjąwszy RegError:
        zwróć Nic
    L = []
    i = 0
    dopóki Prawda:
        spróbuj:
            k = RegEnumKey(handle, i)
        wyjąwszy RegError:
            przerwij
        L.append(k)
        i += 1
    zwróć L

def read_values(base, key):
    """Return dict of registry keys oraz values.

    All names are converted to lowercase.
    """
    spróbuj:
        handle = RegOpenKeyEx(base, key)
    wyjąwszy RegError:
        zwróć Nic
    d = {}
    i = 0
    dopóki Prawda:
        spróbuj:
            name, value, type = RegEnumValue(handle, i)
        wyjąwszy RegError:
            przerwij
        name = name.lower()
        d[convert_mbcs(name)] = convert_mbcs(value)
        i += 1
    zwróć d

def convert_mbcs(s):
    dec = getattr(s, "decode", Nic)
    jeżeli dec jest nie Nic:
        spróbuj:
            s = dec("mbcs")
        wyjąwszy UnicodeError:
            dalej
    zwróć s

klasa MacroExpander:
    def __init__(self, version):
        self.macros = {}
        self.load_macros(version)

    def set_macro(self, macro, path, key):
        dla base w HKEYS:
            d = read_values(base, path)
            jeżeli d:
                self.macros["$(%s)" % macro] = d[key]
                przerwij

    def load_macros(self, version):
        vsbase = r"Software\Microsoft\VisualStudio\%0.1f" % version
        self.set_macro("VCInstallDir", vsbase + r"\Setup\VC", "productdir")
        self.set_macro("VSInstallDir", vsbase + r"\Setup\VS", "productdir")
        net = r"Software\Microsoft\.NETFramework"
        self.set_macro("FrameworkDir", net, "installroot")
        spróbuj:
            jeżeli version > 7.0:
                self.set_macro("FrameworkSDKDir", net, "sdkinstallrootv1.1")
            inaczej:
                self.set_macro("FrameworkSDKDir", net, "sdkinstallroot")
        wyjąwszy KeyError jako exc: #
            podnieś DistutilsPlatformError(
            """Python was built przy Visual Studio 2003;
extensions must be built przy a compiler than can generate compatible binaries.
Visual Studio 2003 was nie found on this system. If you have Cygwin installed,
you can try compiling przy MingW32, by dalejing "-c mingw32" to setup.py.""")

        p = r"Software\Microsoft\NET Framework Setup\Product"
        dla base w HKEYS:
            spróbuj:
                h = RegOpenKeyEx(base, p)
            wyjąwszy RegError:
                kontynuuj
            key = RegEnumKey(h, 0)
            d = read_values(base, r"%s\%s" % (p, key))
            self.macros["$(FrameworkVersion)"] = d["version"]

    def sub(self, s):
        dla k, v w self.macros.items():
            s = s.replace(k, v)
        zwróć s

def get_build_version():
    """Return the version of MSVC that was used to build Python.

    For Python 2.3 oraz up, the version number jest included w
    sys.version.  For earlier versions, assume the compiler jest MSVC 6.
    """
    prefix = "MSC v."
    i = sys.version.find(prefix)
    jeżeli i == -1:
        zwróć 6
    i = i + len(prefix)
    s, rest = sys.version[i:].split(" ", 1)
    majorVersion = int(s[:-2]) - 6
    jeżeli majorVersion >= 13:
        # v13 was skipped oraz should be v14
        majorVersion += 1
    minorVersion = int(s[2:3]) / 10.0
    # I don't think paths are affected by minor version w version 6
    jeżeli majorVersion == 6:
        minorVersion = 0
    jeżeli majorVersion >= 6:
        zwróć majorVersion + minorVersion
    # inaczej we don't know what version of the compiler this jest
    zwróć Nic

def get_build_architecture():
    """Return the processor architecture.

    Possible results are "Intel", "Itanium", albo "AMD64".
    """

    prefix = " bit ("
    i = sys.version.find(prefix)
    jeżeli i == -1:
        zwróć "Intel"
    j = sys.version.find(")", i)
    zwróć sys.version[i+len(prefix):j]

def normalize_and_reduce_paths(paths):
    """Return a list of normalized paths przy duplicates removed.

    The current order of paths jest maintained.
    """
    # Paths are normalized so things like:  /a oraz /a/ aren't both preserved.
    reduced_paths = []
    dla p w paths:
        np = os.path.normpath(p)
        # XXX(nnorwitz): O(n**2), jeżeli reduced_paths gets long perhaps use a set.
        jeżeli np nie w reduced_paths:
            reduced_paths.append(np)
    zwróć reduced_paths


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
        self.__version = get_build_version()
        self.__arch = get_build_architecture()
        jeżeli self.__arch == "Intel":
            # x86
            jeżeli self.__version >= 7:
                self.__root = r"Software\Microsoft\VisualStudio"
                self.__macros = MacroExpander(self.__version)
            inaczej:
                self.__root = r"Software\Microsoft\Devstudio"
            self.__product = "Visual Studio version %s" % self.__version
        inaczej:
            # Win64. Assume this was built przy the platform SDK
            self.__product = "Microsoft SDK compiler %s" % (self.__version + 6)

        self.initialized = Nieprawda

    def initialize(self):
        self.__paths = []
        jeżeli "DISTUTILS_USE_SDK" w os.environ oraz "MSSdk" w os.environ oraz self.find_exe("cl.exe"):
            # Assume that the SDK set up everything alright; don't try to be
            # smarter
            self.cc = "cl.exe"
            self.linker = "link.exe"
            self.lib = "lib.exe"
            self.rc = "rc.exe"
            self.mc = "mc.exe"
        inaczej:
            self.__paths = self.get_msvc_paths("path")

            jeżeli len(self.__paths) == 0:
                podnieś DistutilsPlatformError("Python was built przy %s, "
                       "and extensions need to be built przy the same "
                       "version of the compiler, but it isn't installed."
                       % self.__product)

            self.cc = self.find_exe("cl.exe")
            self.linker = self.find_exe("link.exe")
            self.lib = self.find_exe("lib.exe")
            self.rc = self.find_exe("rc.exe")   # resource compiler
            self.mc = self.find_exe("mc.exe")   # message compiler
            self.set_path_env_var('lib')
            self.set_path_env_var('include')

        # extend the MSVC path przy the current path
        spróbuj:
            dla p w os.environ['path'].split(';'):
                self.__paths.append(p)
        wyjąwszy KeyError:
            dalej
        self.__paths = normalize_and_reduce_paths(self.__paths)
        os.environ['path'] = ";".join(self.__paths)

        self.preprocess_options = Nic
        jeżeli self.__arch == "Intel":
            self.compile_options = [ '/nologo', '/Ox', '/MD', '/W3', '/GX' ,
                                     '/DNDEBUG']
            self.compile_options_debug = ['/nologo', '/Od', '/MDd', '/W3', '/GX',
                                          '/Z7', '/D_DEBUG']
        inaczej:
            # Win64
            self.compile_options = [ '/nologo', '/Ox', '/MD', '/W3', '/GS-' ,
                                     '/DNDEBUG']
            self.compile_options_debug = ['/nologo', '/Od', '/MDd', '/W3', '/GS-',
                                          '/Z7', '/D_DEBUG']

        self.ldflags_shared = ['/DLL', '/nologo', '/INCREMENTAL:NO']
        jeżeli self.__version >= 7:
            self.ldflags_shared_debug = [
                '/DLL', '/nologo', '/INCREMENTAL:no', '/DEBUG'
                ]
        inaczej:
            self.ldflags_shared_debug = [
                '/DLL', '/nologo', '/INCREMENTAL:no', '/pdb:Nic', '/DEBUG'
                ]
        self.ldflags_static = [ '/nologo']

        self.initialized = Prawda

    # -- Worker methods ------------------------------------------------

    def object_filenames(self,
                         source_filenames,
                         strip_dir=0,
                         output_dir=''):
        # Copied z ccompiler.py, extended to zwróć .res jako 'object'-file
        # dla .rc input file
        jeżeli output_dir jest Nic: output_dir = ''
        obj_names = []
        dla src_name w source_filenames:
            (base, ext) = os.path.splitext (src_name)
            base = os.path.splitdrive(base)[1] # Chop off the drive
            base = base[os.path.isabs(base):]  # If abs, chop off leading /
            jeżeli ext nie w self.src_extensions:
                # Better to podnieś an exception instead of silently continuing
                # oraz later complain about sources oraz targets having
                # different lengths
                podnieś CompileError ("Don't know how to compile %s" % src_name)
            jeżeli strip_dir:
                base = os.path.basename (base)
            jeżeli ext w self._rc_extensions:
                obj_names.append (os.path.join (output_dir,
                                                base + self.res_extension))
            albo_inaczej ext w self._mc_extensions:
                obj_names.append (os.path.join (output_dir,
                                                base + self.res_extension))
            inaczej:
                obj_names.append (os.path.join (output_dir,
                                                base + self.obj_extension))
        zwróć obj_names


    def compile(self, sources,
                output_dir=Nic, macros=Nic, include_dirs=Nic, debug=0,
                extra_preargs=Nic, extra_postargs=Nic, depends=Nic):

        jeżeli nie self.initialized:
            self.initialize()
        compile_info = self._setup_compile(output_dir, macros, include_dirs,
                                           sources, depends, extra_postargs)
        macros, objects, extra_postargs, pp_opts, build = compile_info

        compile_opts = extra_preargs albo []
        compile_opts.append ('/c')
        jeżeli debug:
            compile_opts.extend(self.compile_options_debug)
        inaczej:
            compile_opts.extend(self.compile_options)

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
            albo_inaczej ext w self._rc_extensions:
                # compile .RC to .RES file
                input_opt = src
                output_opt = "/fo" + obj
                spróbuj:
                    self.spawn([self.rc] + pp_opts +
                               [output_opt] + [input_opt])
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
                    self.spawn([self.mc] +
                               ['-h', h_dir, '-r', rc_dir] + [src])
                    base, _ = os.path.splitext (os.path.basename (src))
                    rc_file = os.path.join (rc_dir, base + '.rc')
                    # then compile .RC to .RES file
                    self.spawn([self.rc] +
                               ["/fo" + obj] + [rc_file])

                wyjąwszy DistutilsExecError jako msg:
                    podnieś CompileError(msg)
                kontynuuj
            inaczej:
                # how to handle this file?
                podnieś CompileError("Don't know how to compile %s to %s"
                                   % (src, obj))

            output_opt = "/Fo" + obj
            spróbuj:
                self.spawn([self.cc] + compile_opts + pp_opts +
                           [input_opt, output_opt] +
                           extra_postargs)
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
        (objects, output_dir) = self._fix_object_args(objects, output_dir)
        output_filename = self.library_filename(output_libname,
                                                output_dir=output_dir)

        jeżeli self._need_link(objects, output_filename):
            lib_args = objects + ['/OUT:' + output_filename]
            jeżeli debug:
                dalej # XXX what goes here?
            spróbuj:
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
        (objects, output_dir) = self._fix_object_args(objects, output_dir)
        fixed_args = self._fix_lib_args(libraries, library_dirs,
                                        runtime_library_dirs)
        (libraries, library_dirs, runtime_library_dirs) = fixed_args

        jeżeli runtime_library_dirs:
            self.warn ("I don't know what to do przy 'runtime_library_dirs': "
                       + str (runtime_library_dirs))

        lib_opts = gen_lib_options(self,
                                   library_dirs, runtime_library_dirs,
                                   libraries)
        jeżeli output_dir jest nie Nic:
            output_filename = os.path.join(output_dir, output_filename)

        jeżeli self._need_link(objects, output_filename):
            jeżeli target_desc == CCompiler.EXECUTABLE:
                jeżeli debug:
                    ldflags = self.ldflags_shared_debug[1:]
                inaczej:
                    ldflags = self.ldflags_shared[1:]
            inaczej:
                jeżeli debug:
                    ldflags = self.ldflags_shared_debug
                inaczej:
                    ldflags = self.ldflags_shared

            export_opts = []
            dla sym w (export_symbols albo []):
                export_opts.append("/EXPORT:" + sym)

            ld_args = (ldflags + lib_opts + export_opts +
                       objects + ['/OUT:' + output_filename])

            # The MSVC linker generates .lib oraz .exp files, which cannot be
            # suppressed by any linker switches. The .lib files may even be
            # needed! Make sure they are generated w the temporary build
            # directory. Since they have different names dla debug oraz release
            # builds, they can go into the same directory.
            jeżeli export_symbols jest nie Nic:
                (dll_name, dll_ext) = os.path.splitext(
                    os.path.basename(output_filename))
                implib_file = os.path.join(
                    os.path.dirname(objects[0]),
                    self.library_filename(dll_name))
                ld_args.append ('/IMPLIB:' + implib_file)

            jeżeli extra_preargs:
                ld_args[:0] = extra_preargs
            jeżeli extra_postargs:
                ld_args.extend(extra_postargs)

            self.mkpath(os.path.dirname(output_filename))
            spróbuj:
                self.spawn([self.linker] + ld_args)
            wyjąwszy DistutilsExecError jako msg:
                podnieś LinkError(msg)

        inaczej:
            log.debug("skipping %s (up-to-date)", output_filename)


    # -- Miscellaneous methods -----------------------------------------
    # These are all used by the 'gen_lib_options() function, w
    # ccompiler.py.

    def library_dir_option(self, dir):
        zwróć "/LIBPATH:" + dir

    def runtime_library_dir_option(self, dir):
        podnieś DistutilsPlatformError(
              "don't know how to set runtime library search path dla MSVC++")

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
                libfile = os.path.join(dir, self.library_filename (name))
                jeżeli os.path.exists(libfile):
                    zwróć libfile
        inaczej:
            # Oops, didn't find it w *any* of 'dirs'
            zwróć Nic

    # Helper methods dla using the MSVC registry settings

    def find_exe(self, exe):
        """Return path to an MSVC executable program.

        Tries to find the program w several places: first, one of the
        MSVC program search paths z the registry; next, the directories
        w the PATH environment variable.  If any of those work, zwróć an
        absolute path that jest known to exist.  If none of them work, just
        zwróć the original program name, 'exe'.
        """
        dla p w self.__paths:
            fn = os.path.join(os.path.abspath(p), exe)
            jeżeli os.path.isfile(fn):
                zwróć fn

        # didn't find it; try existing path
        dla p w os.environ['Path'].split(';'):
            fn = os.path.join(os.path.abspath(p),exe)
            jeżeli os.path.isfile(fn):
                zwróć fn

        zwróć exe

    def get_msvc_paths(self, path, platform='x86'):
        """Get a list of devstudio directories (include, lib albo path).

        Return a list of strings.  The list will be empty jeżeli unable to
        access the registry albo appropriate registry keys nie found.
        """
        jeżeli nie _can_read_reg:
            zwróć []

        path = path + " dirs"
        jeżeli self.__version >= 7:
            key = (r"%s\%0.1f\VC\VC_OBJECTS_PLATFORM_INFO\Win32\Directories"
                   % (self.__root, self.__version))
        inaczej:
            key = (r"%s\6.0\Build System\Components\Platforms"
                   r"\Win32 (%s)\Directories" % (self.__root, platform))

        dla base w HKEYS:
            d = read_values(base, key)
            jeżeli d:
                jeżeli self.__version >= 7:
                    zwróć self.__macros.sub(d[path]).split(";")
                inaczej:
                    zwróć d[path].split(";")
        # MSVC 6 seems to create the registry entries we need only when
        # the GUI jest run.
        jeżeli self.__version == 6:
            dla base w HKEYS:
                jeżeli read_values(base, r"%s\6.0" % self.__root) jest nie Nic:
                    self.warn("It seems you have Visual Studio 6 installed, "
                        "but the expected registry settings are nie present.\n"
                        "You must at least run the Visual Studio GUI once "
                        "so that these entries are created.")
                    przerwij
        zwróć []

    def set_path_env_var(self, name):
        """Set environment variable 'name' to an MSVC path type value.

        This jest equivalent to a SET command prior to execution of spawned
        commands.
        """

        jeżeli name == "lib":
            p = self.get_msvc_paths("library")
        inaczej:
            p = self.get_msvc_paths(name)
        jeżeli p:
            os.environ[name] = ';'.join(p)


jeżeli get_build_version() >= 8.0:
    log.debug("Importing new compiler z distutils.msvc9compiler")
    OldMSVCCompiler = MSVCCompiler
    z distutils.msvc9compiler zaimportuj MSVCCompiler
    # get_build_architecture nie really relevant now we support cross-compile
    z distutils.msvc9compiler zaimportuj MacroExpander
