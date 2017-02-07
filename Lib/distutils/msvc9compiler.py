"""distutils.msvc9compiler

Contains MSVCCompiler, an implementation of the abstract CCompiler class
dla the Microsoft Visual Studio 2008.

The module jest compatible przy VS 2005 oraz VS 2008. You can find legacy support
dla older versions of VS w distutils.msvccompiler.
"""

# Written by Perry Stoll
# hacked by Robin Becker oraz Thomas Heller to do a better job of
#   finding DevStudio (through the registry)
# ported to VS2005 oraz VS 2008 by Christian Heimes

zaimportuj os
zaimportuj subprocess
zaimportuj sys
zaimportuj re

z distutils.errors zaimportuj DistutilsExecError, DistutilsPlatformError, \
                             CompileError, LibError, LinkError
z distutils.ccompiler zaimportuj CCompiler, gen_preprocess_options, \
                                gen_lib_options
z distutils zaimportuj log
z distutils.util zaimportuj get_platform

zaimportuj winreg

RegOpenKeyEx = winreg.OpenKeyEx
RegEnumKey = winreg.EnumKey
RegEnumValue = winreg.EnumValue
RegError = winreg.error

HKEYS = (winreg.HKEY_USERS,
         winreg.HKEY_CURRENT_USER,
         winreg.HKEY_LOCAL_MACHINE,
         winreg.HKEY_CLASSES_ROOT)

NATIVE_WIN64 = (sys.platform == 'win32' oraz sys.maxsize > 2**32)
jeżeli NATIVE_WIN64:
    # Visual C++ jest a 32-bit application, so we need to look w
    # the corresponding registry branch, jeżeli we're running a
    # 64-bit Python on Win64
    VS_BASE = r"Software\Wow6432Node\Microsoft\VisualStudio\%0.1f"
    WINSDK_BASE = r"Software\Wow6432Node\Microsoft\Microsoft SDKs\Windows"
    NET_BASE = r"Software\Wow6432Node\Microsoft\.NETFramework"
inaczej:
    VS_BASE = r"Software\Microsoft\VisualStudio\%0.1f"
    WINSDK_BASE = r"Software\Microsoft\Microsoft SDKs\Windows"
    NET_BASE = r"Software\Microsoft\.NETFramework"

# A map keyed by get_platform() zwróć values to values accepted by
# 'vcvarsall.bat'.  Note a cross-compile may combine these (eg, 'x86_amd64' jest
# the param to cross-compile on x86 targetting amd64.)
PLAT_TO_VCVARS = {
    'win32' : 'x86',
    'win-amd64' : 'amd64',
    'win-ia64' : 'ia64',
}

klasa Reg:
    """Helper klasa to read values z the registry
    """

    def get_value(cls, path, key):
        dla base w HKEYS:
            d = cls.read_values(base, path)
            jeżeli d oraz key w d:
                zwróć d[key]
        podnieś KeyError(key)
    get_value = classmethod(get_value)

    def read_keys(cls, base, key):
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
    read_keys = classmethod(read_keys)

    def read_values(cls, base, key):
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
            d[cls.convert_mbcs(name)] = cls.convert_mbcs(value)
            i += 1
        zwróć d
    read_values = classmethod(read_values)

    def convert_mbcs(s):
        dec = getattr(s, "decode", Nic)
        jeżeli dec jest nie Nic:
            spróbuj:
                s = dec("mbcs")
            wyjąwszy UnicodeError:
                dalej
        zwróć s
    convert_mbcs = staticmethod(convert_mbcs)

klasa MacroExpander:

    def __init__(self, version):
        self.macros = {}
        self.vsbase = VS_BASE % version
        self.load_macros(version)

    def set_macro(self, macro, path, key):
        self.macros["$(%s)" % macro] = Reg.get_value(path, key)

    def load_macros(self, version):
        self.set_macro("VCInstallDir", self.vsbase + r"\Setup\VC", "productdir")
        self.set_macro("VSInstallDir", self.vsbase + r"\Setup\VS", "productdir")
        self.set_macro("FrameworkDir", NET_BASE, "installroot")
        spróbuj:
            jeżeli version >= 8.0:
                self.set_macro("FrameworkSDKDir", NET_BASE,
                               "sdkinstallrootv2.0")
            inaczej:
                podnieś KeyError("sdkinstallrootv2.0")
        wyjąwszy KeyError:
            podnieś DistutilsPlatformError(
            """Python was built przy Visual Studio 2008;
extensions must be built przy a compiler than can generate compatible binaries.
Visual Studio 2008 was nie found on this system. If you have Cygwin installed,
you can try compiling przy MingW32, by dalejing "-c mingw32" to setup.py.""")

        jeżeli version >= 9.0:
            self.set_macro("FrameworkVersion", self.vsbase, "clr version")
            self.set_macro("WindowsSdkDir", WINSDK_BASE, "currentinstallfolder")
        inaczej:
            p = r"Software\Microsoft\NET Framework Setup\Product"
            dla base w HKEYS:
                spróbuj:
                    h = RegOpenKeyEx(base, p)
                wyjąwszy RegError:
                    kontynuuj
                key = RegEnumKey(h, 0)
                d = Reg.get_value(base, r"%s\%s" % (p, key))
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

def removeDuplicates(variable):
    """Remove duplicate values of an environment variable.
    """
    oldList = variable.split(os.pathsep)
    newList = []
    dla i w oldList:
        jeżeli i nie w newList:
            newList.append(i)
    newVariable = os.pathsep.join(newList)
    zwróć newVariable

def find_vcvarsall(version):
    """Find the vcvarsall.bat file

    At first it tries to find the productdir of VS 2008 w the registry. If
    that fails it falls back to the VS90COMNTOOLS env var.
    """
    vsbase = VS_BASE % version
    spróbuj:
        productdir = Reg.get_value(r"%s\Setup\VC" % vsbase,
                                   "productdir")
    wyjąwszy KeyError:
        log.debug("Unable to find productdir w registry")
        productdir = Nic

    jeżeli nie productdir albo nie os.path.isdir(productdir):
        toolskey = "VS%0.f0COMNTOOLS" % version
        toolsdir = os.environ.get(toolskey, Nic)

        jeżeli toolsdir oraz os.path.isdir(toolsdir):
            productdir = os.path.join(toolsdir, os.pardir, os.pardir, "VC")
            productdir = os.path.abspath(productdir)
            jeżeli nie os.path.isdir(productdir):
                log.debug("%s jest nie a valid directory" % productdir)
                zwróć Nic
        inaczej:
            log.debug("Env var %s jest nie set albo invalid" % toolskey)
    jeżeli nie productdir:
        log.debug("No productdir found")
        zwróć Nic
    vcvarsall = os.path.join(productdir, "vcvarsall.bat")
    jeżeli os.path.isfile(vcvarsall):
        zwróć vcvarsall
    log.debug("Unable to find vcvarsall.bat")
    zwróć Nic

def query_vcvarsall(version, arch="x86"):
    """Launch vcvarsall.bat oraz read the settings z its environment
    """
    vcvarsall = find_vcvarsall(version)
    interesting = set(("include", "lib", "libpath", "path"))
    result = {}

    jeżeli vcvarsall jest Nic:
        podnieś DistutilsPlatformError("Unable to find vcvarsall.bat")
    log.debug("Calling 'vcvarsall.bat %s' (version=%s)", arch, version)
    popen = subprocess.Popen('"%s" %s & set' % (vcvarsall, arch),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    spróbuj:
        stdout, stderr = popen.communicate()
        jeżeli popen.wait() != 0:
            podnieś DistutilsPlatformError(stderr.decode("mbcs"))

        stdout = stdout.decode("mbcs")
        dla line w stdout.split("\n"):
            line = Reg.convert_mbcs(line)
            jeżeli '=' nie w line:
                kontynuuj
            line = line.strip()
            key, value = line.split('=', 1)
            key = key.lower()
            jeżeli key w interesting:
                jeżeli value.endswith(os.pathsep):
                    value = value[:-1]
                result[key] = removeDuplicates(value)

    w_końcu:
        popen.stdout.close()
        popen.stderr.close()

    jeżeli len(result) != len(interesting):
        podnieś ValueError(str(list(result.keys())))

    zwróć result

# More globals
VERSION = get_build_version()
jeżeli VERSION < 8.0:
    podnieś DistutilsPlatformError("VC %0.1f jest nie supported by this module" % VERSION)
# MACROS = MacroExpander(VERSION)

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
        self.__version = VERSION
        self.__root = r"Software\Microsoft\VisualStudio"
        # self.__macros = MACROS
        self.__paths = []
        # target platform (.plat_name jest consistent przy 'bdist')
        self.plat_name = Nic
        self.__arch = Nic # deprecated name
        self.initialized = Nieprawda

    def initialize(self, plat_name=Nic):
        # multi-init means we would need to check platform same each time...
        assert nie self.initialized, "don't init multiple times"
        jeżeli plat_name jest Nic:
            plat_name = get_platform()
        # sanity check dla platforms to prevent obscure errors later.
        ok_plats = 'win32', 'win-amd64', 'win-ia64'
        jeżeli plat_name nie w ok_plats:
            podnieś DistutilsPlatformError("--plat-name must be one of %s" %
                                         (ok_plats,))

        jeżeli "DISTUTILS_USE_SDK" w os.environ oraz "MSSdk" w os.environ oraz self.find_exe("cl.exe"):
            # Assume that the SDK set up everything alright; don't try to be
            # smarter
            self.cc = "cl.exe"
            self.linker = "link.exe"
            self.lib = "lib.exe"
            self.rc = "rc.exe"
            self.mc = "mc.exe"
        inaczej:
            # On x86, 'vcvars32.bat amd64' creates an env that doesn't work;
            # to cross compile, you use 'x86_amd64'.
            # On AMD64, 'vcvars32.bat amd64' jest a native build env; to cross
            # compile use 'x86' (ie, it runs the x86 compiler directly)
            # No idea how itanium handles this, jeżeli at all.
            jeżeli plat_name == get_platform() albo plat_name == 'win32':
                # native build albo cross-compile to win32
                plat_spec = PLAT_TO_VCVARS[plat_name]
            inaczej:
                # cross compile z win32 -> some 64bit
                plat_spec = PLAT_TO_VCVARS[get_platform()] + '_' + \
                            PLAT_TO_VCVARS[plat_name]

            vc_env = query_vcvarsall(VERSION, plat_spec)

            self.__paths = vc_env['path'].split(os.pathsep)
            os.environ['lib'] = vc_env['lib']
            os.environ['include'] = vc_env['include']

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
            #self.set_path_env_var('lib')
            #self.set_path_env_var('include')

        # extend the MSVC path przy the current path
        spróbuj:
            dla p w os.environ['path'].split(';'):
                self.__paths.append(p)
        wyjąwszy KeyError:
            dalej
        self.__paths = normalize_and_reduce_paths(self.__paths)
        os.environ['path'] = ";".join(self.__paths)

        self.preprocess_options = Nic
        jeżeli self.__arch == "x86":
            self.compile_options = [ '/nologo', '/Ox', '/MD', '/W3',
                                     '/DNDEBUG']
            self.compile_options_debug = ['/nologo', '/Od', '/MDd', '/W3',
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
            build_temp = os.path.dirname(objects[0])
            jeżeli export_symbols jest nie Nic:
                (dll_name, dll_ext) = os.path.splitext(
                    os.path.basename(output_filename))
                implib_file = os.path.join(
                    build_temp,
                    self.library_filename(dll_name))
                ld_args.append ('/IMPLIB:' + implib_file)

            self.manifest_setup_ldargs(output_filename, build_temp, ld_args)

            jeżeli extra_preargs:
                ld_args[:0] = extra_preargs
            jeżeli extra_postargs:
                ld_args.extend(extra_postargs)

            self.mkpath(os.path.dirname(output_filename))
            spróbuj:
                self.spawn([self.linker] + ld_args)
            wyjąwszy DistutilsExecError jako msg:
                podnieś LinkError(msg)

            # embed the manifest
            # XXX - this jest somewhat fragile - jeżeli mt.exe fails, distutils
            # will still consider the DLL up-to-date, but it will nie have a
            # manifest.  Maybe we should link to a temp file?  OTOH, that
            # implies a build environment error that shouldn't go undetected.
            mfinfo = self.manifest_get_embed_info(target_desc, ld_args)
            jeżeli mfinfo jest nie Nic:
                mffilename, mfid = mfinfo
                out_arg = '-outputresource:%s;%s' % (output_filename, mfid)
                spróbuj:
                    self.spawn(['mt.exe', '-nologo', '-manifest',
                                mffilename, out_arg])
                wyjąwszy DistutilsExecError jako msg:
                    podnieś LinkError(msg)
        inaczej:
            log.debug("skipping %s (up-to-date)", output_filename)

    def manifest_setup_ldargs(self, output_filename, build_temp, ld_args):
        # If we need a manifest at all, an embedded manifest jest recommended.
        # See MSDN article titled
        # "How to: Embed a Manifest Inside a C/C++ Application"
        # (currently at http://msdn2.microsoft.com/en-us/library/ms235591(VS.80).aspx)
        # Ask the linker to generate the manifest w the temp dir, so
        # we can check it, oraz possibly embed it, later.
        temp_manifest = os.path.join(
                build_temp,
                os.path.basename(output_filename) + ".manifest")
        ld_args.append('/MANIFESTFILE:' + temp_manifest)

    def manifest_get_embed_info(self, target_desc, ld_args):
        # If a manifest should be embedded, zwróć a tuple of
        # (manifest_filename, resource_id).  Returns Nic jeżeli no manifest
        # should be embedded.  See http://bugs.python.org/issue7833 dla why
        # we want to avoid any manifest dla extension modules jeżeli we can)
        dla arg w ld_args:
            jeżeli arg.startswith("/MANIFESTFILE:"):
                temp_manifest = arg.split(":", 1)[1]
                przerwij
        inaczej:
            # no /MANIFESTFILE so nothing to do.
            zwróć Nic
        jeżeli target_desc == CCompiler.EXECUTABLE:
            # by default, executables always get the manifest przy the
            # CRT referenced.
            mfid = 1
        inaczej:
            # Extension modules try oraz avoid any manifest jeżeli possible.
            mfid = 2
            temp_manifest = self._remove_visual_c_ref(temp_manifest)
        jeżeli temp_manifest jest Nic:
            zwróć Nic
        zwróć temp_manifest, mfid

    def _remove_visual_c_ref(self, manifest_file):
        spróbuj:
            # Remove references to the Visual C runtime, so they will
            # fall through to the Visual C dependency of Python.exe.
            # This way, when installed dla a restricted user (e.g.
            # runtimes are nie w WinSxS folder, but w Python's own
            # folder), the runtimes do nie need to be w every folder
            # przy .pyd's.
            # Returns either the filename of the modified manifest albo
            # Nic jeżeli no manifest should be embedded.
            manifest_f = open(manifest_file)
            spróbuj:
                manifest_buf = manifest_f.read()
            w_końcu:
                manifest_f.close()
            pattern = re.compile(
                r"""<assemblyIdentity.*?name=("|')Microsoft\."""\
                r"""VC\d{2}\.CRT("|').*?(/>|</assemblyIdentity>)""",
                re.DOTALL)
            manifest_buf = re.sub(pattern, "", manifest_buf)
            pattern = "<dependentAssembly>\s*</dependentAssembly>"
            manifest_buf = re.sub(pattern, "", manifest_buf)
            # Now see jeżeli any other assemblies are referenced - jeżeli not, we
            # don't want a manifest embedded.
            pattern = re.compile(
                r"""<assemblyIdentity.*?name=(?:"|')(.+?)(?:"|')"""
                r""".*?(?:/>|</assemblyIdentity>)""", re.DOTALL)
            jeżeli re.search(pattern, manifest_buf) jest Nic:
                zwróć Nic

            manifest_f = open(manifest_file, 'w')
            spróbuj:
                manifest_f.write(manifest_buf)
                zwróć manifest_file
            w_końcu:
                manifest_f.close()
        wyjąwszy OSError:
            dalej

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
