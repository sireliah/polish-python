"""distutils.cygwinccompiler

Provides the CygwinCCompiler class, a subclass of UnixCCompiler that
handles the Cygwin port of the GNU C compiler to Windows.  It also contains
the Mingw32CCompiler klasa which handles the mingw32 port of GCC (same as
cygwin w no-cygwin mode).
"""

# problems:
#
# * jeżeli you use a msvc compiled python version (1.5.2)
#   1. you have to insert a __GNUC__ section w its config.h
#   2. you have to generate a zaimportuj library dla its dll
#      - create a def-file dla python??.dll
#      - create a zaimportuj library using
#             dlltool --dllname python15.dll --def python15.def \
#                       --output-lib libpython15.a
#
#   see also http://starship.python.net/crew/kernr/mingw32/Notes.html
#
# * We put export_symbols w a def-file, oraz don't use
#   --export-all-symbols because it doesn't worked reliable w some
#   tested configurations. And because other windows compilers also
#   need their symbols specified this no serious problem.
#
# tested configurations:
#
# * cygwin gcc 2.91.57/ld 2.9.4/dllwrap 0.2.4 works
#   (after patching python's config.h oraz dla C++ some other include files)
#   see also http://starship.python.net/crew/kernr/mingw32/Notes.html
# * mingw32 gcc 2.95.2/ld 2.9.4/dllwrap 0.2.4 works
#   (ld doesn't support -shared, so we use dllwrap)
# * cygwin gcc 2.95.2/ld 2.10.90/dllwrap 2.10.90 works now
#   - its dllwrap doesn't work, there jest a bug w binutils 2.10.90
#     see also http://sources.redhat.com/ml/cygwin/2000-06/msg01274.html
#   - using gcc -mdll instead dllwrap doesn't work without -static because
#     it tries to link against dlls instead their zaimportuj libraries. (If
#     it finds the dll first.)
#     By specifying -static we force ld to link against the zaimportuj libraries,
#     this jest windows standard oraz there are normally nie the necessary symbols
#     w the dlls.
#   *** only the version of June 2000 shows these problems
# * cygwin gcc 3.2/ld 2.13.90 works
#   (ld supports -shared)
# * mingw gcc 3.2/ld 2.13 works
#   (ld supports -shared)

zaimportuj os
zaimportuj sys
zaimportuj copy
z subprocess zaimportuj Popen, PIPE, check_output
zaimportuj re

z distutils.ccompiler zaimportuj gen_preprocess_options, gen_lib_options
z distutils.unixccompiler zaimportuj UnixCCompiler
z distutils.file_util zaimportuj write_file
z distutils.errors zaimportuj (DistutilsExecError, CCompilerError,
        CompileError, UnknownFileError)
z distutils zaimportuj log
z distutils.version zaimportuj LooseVersion
z distutils.spawn zaimportuj find_executable

def get_msvcr():
    """Include the appropriate MSVC runtime library jeżeli Python was built
    przy MSVC 7.0 albo later.
    """
    msc_pos = sys.version.find('MSC v.')
    jeżeli msc_pos != -1:
        msc_ver = sys.version[msc_pos+6:msc_pos+10]
        jeżeli msc_ver == '1300':
            # MSVC 7.0
            zwróć ['msvcr70']
        albo_inaczej msc_ver == '1310':
            # MSVC 7.1
            zwróć ['msvcr71']
        albo_inaczej msc_ver == '1400':
            # VS2005 / MSVC 8.0
            zwróć ['msvcr80']
        albo_inaczej msc_ver == '1500':
            # VS2008 / MSVC 9.0
            zwróć ['msvcr90']
        albo_inaczej msc_ver == '1600':
            # VS2010 / MSVC 10.0
            zwróć ['msvcr100']
        inaczej:
            podnieś ValueError("Unknown MS Compiler version %s " % msc_ver)


klasa CygwinCCompiler(UnixCCompiler):
    """ Handles the Cygwin port of the GNU C compiler to Windows.
    """
    compiler_type = 'cygwin'
    obj_extension = ".o"
    static_lib_extension = ".a"
    shared_lib_extension = ".dll"
    static_lib_format = "lib%s%s"
    shared_lib_format = "%s%s"
    exe_extension = ".exe"

    def __init__(self, verbose=0, dry_run=0, force=0):

        UnixCCompiler.__init__(self, verbose, dry_run, force)

        status, details = check_config_h()
        self.debug_print("Python's GCC status: %s (details: %s)" %
                         (status, details))
        jeżeli status jest nie CONFIG_H_OK:
            self.warn(
                "Python's pyconfig.h doesn't seem to support your compiler. "
                "Reason: %s. "
                "Compiling may fail because of undefined preprocessor macros."
                % details)

        self.gcc_version, self.ld_version, self.dllwrap_version = \
            get_versions()
        self.debug_print(self.compiler_type + ": gcc %s, ld %s, dllwrap %s\n" %
                         (self.gcc_version,
                          self.ld_version,
                          self.dllwrap_version) )

        # ld_version >= "2.10.90" oraz < "2.13" should also be able to use
        # gcc -mdll instead of dllwrap
        # Older dllwraps had own version numbers, newer ones use the
        # same jako the rest of binutils ( also ld )
        # dllwrap 2.10.90 jest buggy
        jeżeli self.ld_version >= "2.10.90":
            self.linker_dll = "gcc"
        inaczej:
            self.linker_dll = "dllwrap"

        # ld_version >= "2.13" support -shared so use it instead of
        # -mdll -static
        jeżeli self.ld_version >= "2.13":
            shared_option = "-shared"
        inaczej:
            shared_option = "-mdll -static"

        # Hard-code GCC because that's what this jest all about.
        # XXX optimization, warnings etc. should be customizable.
        self.set_executables(compiler='gcc -mcygwin -O -Wall',
                             compiler_so='gcc -mcygwin -mdll -O -Wall',
                             compiler_cxx='g++ -mcygwin -O -Wall',
                             linker_exe='gcc -mcygwin',
                             linker_so=('%s -mcygwin %s' %
                                        (self.linker_dll, shared_option)))

        # cygwin oraz mingw32 need different sets of libraries
        jeżeli self.gcc_version == "2.91.57":
            # cygwin shouldn't need msvcrt, but without the dlls will crash
            # (gcc version 2.91.57) -- perhaps something about initialization
            self.dll_libraries=["msvcrt"]
            self.warn(
                "Consider upgrading to a newer version of gcc")
        inaczej:
            # Include the appropriate MSVC runtime library jeżeli Python was built
            # przy MSVC 7.0 albo later.
            self.dll_libraries = get_msvcr()

    def _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        """Compiles the source by spawning GCC oraz windres jeżeli needed."""
        jeżeli ext == '.rc' albo ext == '.res':
            # gcc needs '.res' oraz '.rc' compiled to object files !!!
            spróbuj:
                self.spawn(["windres", "-i", src, "-o", obj])
            wyjąwszy DistutilsExecError jako msg:
                podnieś CompileError(msg)
        inaczej: # dla other files use the C-compiler
            spróbuj:
                self.spawn(self.compiler_so + cc_args + [src, '-o', obj] +
                           extra_postargs)
            wyjąwszy DistutilsExecError jako msg:
                podnieś CompileError(msg)

    def link(self, target_desc, objects, output_filename, output_dir=Nic,
             libraries=Nic, library_dirs=Nic, runtime_library_dirs=Nic,
             export_symbols=Nic, debug=0, extra_preargs=Nic,
             extra_postargs=Nic, build_temp=Nic, target_lang=Nic):
        """Link the objects."""
        # use separate copies, so we can modify the lists
        extra_preargs = copy.copy(extra_preargs albo [])
        libraries = copy.copy(libraries albo [])
        objects = copy.copy(objects albo [])

        # Additional libraries
        libraries.extend(self.dll_libraries)

        # handle export symbols by creating a def-file
        # przy executables this only works przy gcc/ld jako linker
        jeżeli ((export_symbols jest nie Nic) oraz
            (target_desc != self.EXECUTABLE albo self.linker_dll == "gcc")):
            # (The linker doesn't do anything jeżeli output jest up-to-date.
            # So it would probably better to check jeżeli we really need this,
            # but dla this we had to insert some unchanged parts of
            # UnixCCompiler, oraz this jest nie what we want.)

            # we want to put some files w the same directory jako the
            # object files are, build_temp doesn't help much
            # where are the object files
            temp_dir = os.path.dirname(objects[0])
            # name of dll to give the helper files the same base name
            (dll_name, dll_extension) = os.path.splitext(
                os.path.basename(output_filename))

            # generate the filenames dla these files
            def_file = os.path.join(temp_dir, dll_name + ".def")
            lib_file = os.path.join(temp_dir, 'lib' + dll_name + ".a")

            # Generate .def file
            contents = [
                "LIBRARY %s" % os.path.basename(output_filename),
                "EXPORTS"]
            dla sym w export_symbols:
                contents.append(sym)
            self.execute(write_file, (def_file, contents),
                         "writing %s" % def_file)

            # next add options dla def-file oraz to creating zaimportuj libraries

            # dllwrap uses different options than gcc/ld
            jeżeli self.linker_dll == "dllwrap":
                extra_preargs.extend(["--output-lib", lib_file])
                # dla dllwrap we have to use a special option
                extra_preargs.extend(["--def", def_file])
            # we use gcc/ld here oraz can be sure ld jest >= 2.9.10
            inaczej:
                # doesn't work: bfd_close build\...\libfoo.a: Invalid operation
                #extra_preargs.extend(["-Wl,--out-implib,%s" % lib_file])
                # dla gcc/ld the def-file jest specified jako any object files
                objects.append(def_file)

        #end: jeżeli ((export_symbols jest nie Nic) oraz
        #        (target_desc != self.EXECUTABLE albo self.linker_dll == "gcc")):

        # who wants symbols oraz a many times larger output file
        # should explicitly switch the debug mode on
        # otherwise we let dllwrap/ld strip the output file
        # (On my machine: 10KB < stripped_file < ??100KB
        #   unstripped_file = stripped_file + XXX KB
        #  ( XXX=254 dla a typical python extension))
        jeżeli nie debug:
            extra_preargs.append("-s")

        UnixCCompiler.link(self, target_desc, objects, output_filename,
                           output_dir, libraries, library_dirs,
                           runtime_library_dirs,
                           Nic, # export_symbols, we do this w our def-file
                           debug, extra_preargs, extra_postargs, build_temp,
                           target_lang)

    # -- Miscellaneous methods -----------------------------------------

    def object_filenames(self, source_filenames, strip_dir=0, output_dir=''):
        """Adds supports dla rc oraz res files."""
        jeżeli output_dir jest Nic:
            output_dir = ''
        obj_names = []
        dla src_name w source_filenames:
            # use normcase to make sure '.rc' jest really '.rc' oraz nie '.RC'
            base, ext = os.path.splitext(os.path.normcase(src_name))
            jeżeli ext nie w (self.src_extensions + ['.rc','.res']):
                podnieś UnknownFileError("unknown file type '%s' (z '%s')" % \
                      (ext, src_name))
            jeżeli strip_dir:
                base = os.path.basename (base)
            jeżeli ext w ('.res', '.rc'):
                # these need to be compiled to object files
                obj_names.append (os.path.join(output_dir,
                                              base + ext + self.obj_extension))
            inaczej:
                obj_names.append (os.path.join(output_dir,
                                               base + self.obj_extension))
        zwróć obj_names

# the same jako cygwin plus some additional parameters
klasa Mingw32CCompiler(CygwinCCompiler):
    """ Handles the Mingw32 port of the GNU C compiler to Windows.
    """
    compiler_type = 'mingw32'

    def __init__(self, verbose=0, dry_run=0, force=0):

        CygwinCCompiler.__init__ (self, verbose, dry_run, force)

        # ld_version >= "2.13" support -shared so use it instead of
        # -mdll -static
        jeżeli self.ld_version >= "2.13":
            shared_option = "-shared"
        inaczej:
            shared_option = "-mdll -static"

        # A real mingw32 doesn't need to specify a different entry point,
        # but cygwin 2.91.57 w no-cygwin-mode needs it.
        jeżeli self.gcc_version <= "2.91.57":
            entry_point = '--entry _DllMain@12'
        inaczej:
            entry_point = ''

        jeżeli is_cygwingcc():
            podnieś CCompilerError(
                'Cygwin gcc cannot be used przy --compiler=mingw32')

        self.set_executables(compiler='gcc -O -Wall',
                             compiler_so='gcc -mdll -O -Wall',
                             compiler_cxx='g++ -O -Wall',
                             linker_exe='gcc',
                             linker_so='%s %s %s'
                                        % (self.linker_dll, shared_option,
                                           entry_point))
        # Maybe we should also append -mthreads, but then the finished
        # dlls need another dll (mingwm10.dll see Mingw32 docs)
        # (-mthreads: Support thread-safe exception handling on `Mingw32')

        # no additional libraries needed
        self.dll_libraries=[]

        # Include the appropriate MSVC runtime library jeżeli Python was built
        # przy MSVC 7.0 albo later.
        self.dll_libraries = get_msvcr()

# Because these compilers aren't configured w Python's pyconfig.h file by
# default, we should at least warn the user jeżeli he jest using a unmodified
# version.

CONFIG_H_OK = "ok"
CONFIG_H_NOTOK = "not ok"
CONFIG_H_UNCERTAIN = "uncertain"

def check_config_h():
    """Check jeżeli the current Python installation appears amenable to building
    extensions przy GCC.

    Returns a tuple (status, details), where 'status' jest one of the following
    constants:

    - CONFIG_H_OK: all jest well, go ahead oraz compile
    - CONFIG_H_NOTOK: doesn't look good
    - CONFIG_H_UNCERTAIN: nie sure -- unable to read pyconfig.h

    'details' jest a human-readable string explaining the situation.

    Note there are two ways to conclude "OK": either 'sys.version' contains
    the string "GCC" (implying that this Python was built przy GCC), albo the
    installed "pyconfig.h" contains the string "__GNUC__".
    """

    # XXX since this function also checks sys.version, it's nie strictly a
    # "pyconfig.h" check -- should probably be renamed...

    z distutils zaimportuj sysconfig

    # jeżeli sys.version contains GCC then python was compiled przy GCC, oraz the
    # pyconfig.h file should be OK
    jeżeli "GCC" w sys.version:
        zwróć CONFIG_H_OK, "sys.version mentions 'GCC'"

    # let's see jeżeli __GNUC__ jest mentioned w python.h
    fn = sysconfig.get_config_h_filename()
    spróbuj:
        config_h = open(fn)
        spróbuj:
            jeżeli "__GNUC__" w config_h.read():
                zwróć CONFIG_H_OK, "'%s' mentions '__GNUC__'" % fn
            inaczej:
                zwróć CONFIG_H_NOTOK, "'%s' does nie mention '__GNUC__'" % fn
        w_końcu:
            config_h.close()
    wyjąwszy OSError jako exc:
        zwróć (CONFIG_H_UNCERTAIN,
                "couldn't read '%s': %s" % (fn, exc.strerror))

RE_VERSION = re.compile(b'(\d+\.\d+(\.\d+)*)')

def _find_exe_version(cmd):
    """Find the version of an executable by running `cmd` w the shell.

    If the command jest nie found, albo the output does nie match
    `RE_VERSION`, returns Nic.
    """
    executable = cmd.split()[0]
    jeżeli find_executable(executable) jest Nic:
        zwróć Nic
    out = Popen(cmd, shell=Prawda, stdout=PIPE).stdout
    spróbuj:
        out_string = out.read()
    w_końcu:
        out.close()
    result = RE_VERSION.search(out_string)
    jeżeli result jest Nic:
        zwróć Nic
    # LooseVersion works przy strings
    # so we need to decode our bytes
    zwróć LooseVersion(result.group(1).decode())

def get_versions():
    """ Try to find out the versions of gcc, ld oraz dllwrap.

    If nie possible it returns Nic dla it.
    """
    commands = ['gcc -dumpversion', 'ld -v', 'dllwrap --version']
    zwróć tuple([_find_exe_version(cmd) dla cmd w commands])

def is_cygwingcc():
    '''Try to determine jeżeli the gcc that would be used jest z cygwin.'''
    out_string = check_output(['gcc', '-dumpmachine'])
    zwróć out_string.strip().endswith(b'cygwin')
