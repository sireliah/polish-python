"""distutils.command.build_clib

Implements the Distutils 'build_clib' command, to build a C/C++ library
that jest included w the module distribution oraz needed by an extension
module."""


# XXX this module has *lots* of code ripped-off quite transparently from
# build_ext.py -- nie surprisingly really, jako the work required to build
# a static library z a collection of C source files jest nie really all
# that different z what's required to build a shared object file from
# a collection of C source files.  Nevertheless, I haven't done the
# necessary refactoring to account dla the overlap w code between the
# two modules, mainly because a number of subtle details changed w the
# cut 'n paste.  Sigh.

zaimportuj os
z distutils.core zaimportuj Command
z distutils.errors zaimportuj *
z distutils.sysconfig zaimportuj customize_compiler
z distutils zaimportuj log

def show_compilers():
    z distutils.ccompiler zaimportuj show_compilers
    show_compilers()


klasa build_clib(Command):

    description = "build C/C++ libraries used by Python extensions"

    user_options = [
        ('build-clib=', 'b',
         "directory to build C/C++ libraries to"),
        ('build-temp=', 't',
         "directory to put temporary build by-products"),
        ('debug', 'g',
         "compile przy debugging information"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
        ('compiler=', 'c',
         "specify the compiler type"),
        ]

    boolean_options = ['debug', 'force']

    help_options = [
        ('help-compiler', Nic,
         "list available compilers", show_compilers),
        ]

    def initialize_options(self):
        self.build_clib = Nic
        self.build_temp = Nic

        # List of libraries to build
        self.libraries = Nic

        # Compilation options dla all libraries
        self.include_dirs = Nic
        self.define = Nic
        self.undef = Nic
        self.debug = Nic
        self.force = 0
        self.compiler = Nic


    def finalize_options(self):
        # This might be confusing: both build-clib oraz build-temp default
        # to build-temp jako defined by the "build" command.  This jest because
        # I think that C libraries are really just temporary build
        # by-products, at least z the point of view of building Python
        # extensions -- but I want to keep my options open.
        self.set_undefined_options('build',
                                   ('build_temp', 'build_clib'),
                                   ('build_temp', 'build_temp'),
                                   ('compiler', 'compiler'),
                                   ('debug', 'debug'),
                                   ('force', 'force'))

        self.libraries = self.distribution.libraries
        jeżeli self.libraries:
            self.check_library_list(self.libraries)

        jeżeli self.include_dirs jest Nic:
            self.include_dirs = self.distribution.include_dirs albo []
        jeżeli isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        # XXX same jako dla build_ext -- what about 'self.define' oraz
        # 'self.undef' ?


    def run(self):
        jeżeli nie self.libraries:
            zwróć

        # Yech -- this jest cut 'n pasted z build_ext.py!
        z distutils.ccompiler zaimportuj new_compiler
        self.compiler = new_compiler(compiler=self.compiler,
                                     dry_run=self.dry_run,
                                     force=self.force)
        customize_compiler(self.compiler)

        jeżeli self.include_dirs jest nie Nic:
            self.compiler.set_include_dirs(self.include_dirs)
        jeżeli self.define jest nie Nic:
            # 'define' option jest a list of (name,value) tuples
            dla (name,value) w self.define:
                self.compiler.define_macro(name, value)
        jeżeli self.undef jest nie Nic:
            dla macro w self.undef:
                self.compiler.undefine_macro(macro)

        self.build_libraries(self.libraries)


    def check_library_list(self, libraries):
        """Ensure that the list of libraries jest valid.

        `library` jest presumably provided jako a command option 'libraries'.
        This method checks that it jest a list of 2-tuples, where the tuples
        are (library_name, build_info_dict).

        Raise DistutilsSetupError jeżeli the structure jest invalid anywhere;
        just returns otherwise.
        """
        jeżeli nie isinstance(libraries, list):
            podnieś DistutilsSetupError(
                  "'libraries' option must be a list of tuples")

        dla lib w libraries:
            jeżeli nie isinstance(lib, tuple) oraz len(lib) != 2:
                podnieś DistutilsSetupError(
                      "each element of 'libraries' must a 2-tuple")

            name, build_info = lib

            jeżeli nie isinstance(name, str):
                podnieś DistutilsSetupError(
                      "first element of each tuple w 'libraries' "
                      "must be a string (the library name)")

            jeżeli '/' w name albo (os.sep != '/' oraz os.sep w name):
                podnieś DistutilsSetupError("bad library name '%s': "
                       "may nie contain directory separators" % lib[0])

            jeżeli nie isinstance(build_info, dict):
                podnieś DistutilsSetupError(
                      "second element of each tuple w 'libraries' "
                      "must be a dictionary (build info)")


    def get_library_names(self):
        # Assume the library list jest valid -- 'check_library_list()' jest
        # called z 'finalize_options()', so it should be!
        jeżeli nie self.libraries:
            zwróć Nic

        lib_names = []
        dla (lib_name, build_info) w self.libraries:
            lib_names.append(lib_name)
        zwróć lib_names


    def get_source_files(self):
        self.check_library_list(self.libraries)
        filenames = []
        dla (lib_name, build_info) w self.libraries:
            sources = build_info.get('sources')
            jeżeli sources jest Nic albo nie isinstance(sources, (list, tuple)):
                podnieś DistutilsSetupError(
                       "in 'libraries' option (library '%s'), "
                       "'sources' must be present oraz must be "
                       "a list of source filenames" % lib_name)

            filenames.extend(sources)
        zwróć filenames


    def build_libraries(self, libraries):
        dla (lib_name, build_info) w libraries:
            sources = build_info.get('sources')
            jeżeli sources jest Nic albo nie isinstance(sources, (list, tuple)):
                podnieś DistutilsSetupError(
                       "in 'libraries' option (library '%s'), "
                       "'sources' must be present oraz must be "
                       "a list of source filenames" % lib_name)
            sources = list(sources)

            log.info("building '%s' library", lib_name)

            # First, compile the source code to object files w the library
            # directory.  (This should probably change to putting object
            # files w a temporary build directory.)
            macros = build_info.get('macros')
            include_dirs = build_info.get('include_dirs')
            objects = self.compiler.compile(sources,
                                            output_dir=self.build_temp,
                                            macros=macros,
                                            include_dirs=include_dirs,
                                            debug=self.debug)

            # Now "link" the object files together into a static library.
            # (On Unix at least, this isn't really linking -- it just
            # builds an archive.  Whatever.)
            self.compiler.create_static_lib(objects, lib_name,
                                            output_dir=self.build_clib,
                                            debug=self.debug)
