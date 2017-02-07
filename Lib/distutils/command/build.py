"""distutils.command.build

Implements the Distutils 'build' command."""

zaimportuj sys, os
z distutils.core zaimportuj Command
z distutils.errors zaimportuj DistutilsOptionError
z distutils.util zaimportuj get_platform


def show_compilers():
    z distutils.ccompiler zaimportuj show_compilers
    show_compilers()


klasa build(Command):

    description = "build everything needed to install"

    user_options = [
        ('build-base=', 'b',
         "base directory dla build library"),
        ('build-purelib=', Nic,
         "build directory dla platform-neutral distributions"),
        ('build-platlib=', Nic,
         "build directory dla platform-specific distributions"),
        ('build-lib=', Nic,
         "build directory dla all distribution (defaults to either " +
         "build-purelib albo build-platlib"),
        ('build-scripts=', Nic,
         "build directory dla scripts"),
        ('build-temp=', 't',
         "temporary build directory"),
        ('plat-name=', 'p',
         "platform name to build for, jeżeli supported "
         "(default: %s)" % get_platform()),
        ('compiler=', 'c',
         "specify the compiler type"),
        ('parallel=', 'j',
         "number of parallel build jobs"),
        ('debug', 'g',
         "compile extensions oraz libraries przy debugging information"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
        ('executable=', 'e',
         "specify final destination interpreter path (build.py)"),
        ]

    boolean_options = ['debug', 'force']

    help_options = [
        ('help-compiler', Nic,
         "list available compilers", show_compilers),
        ]

    def initialize_options(self):
        self.build_base = 'build'
        # these are decided only after 'build_base' has its final value
        # (unless overridden by the user albo client)
        self.build_purelib = Nic
        self.build_platlib = Nic
        self.build_lib = Nic
        self.build_temp = Nic
        self.build_scripts = Nic
        self.compiler = Nic
        self.plat_name = Nic
        self.debug = Nic
        self.force = 0
        self.executable = Nic
        self.parallel = Nic

    def finalize_options(self):
        jeżeli self.plat_name jest Nic:
            self.plat_name = get_platform()
        inaczej:
            # plat-name only supported dla windows (other platforms are
            # supported via ./configure flags, jeżeli at all).  Avoid misleading
            # other platforms.
            jeżeli os.name != 'nt':
                podnieś DistutilsOptionError(
                            "--plat-name only supported on Windows (try "
                            "using './configure --help' on your platform)")

        plat_specifier = ".%s-%s" % (self.plat_name, sys.version[0:3])

        # Make it so Python 2.x oraz Python 2.x przy --with-pydebug don't
        # share the same build directories. Doing so confuses the build
        # process dla C modules
        jeżeli hasattr(sys, 'gettotalrefcount'):
            plat_specifier += '-pydebug'

        # 'build_purelib' oraz 'build_platlib' just default to 'lib' oraz
        # 'lib.<plat>' under the base build directory.  We only use one of
        # them dla a given distribution, though --
        jeżeli self.build_purelib jest Nic:
            self.build_purelib = os.path.join(self.build_base, 'lib')
        jeżeli self.build_platlib jest Nic:
            self.build_platlib = os.path.join(self.build_base,
                                              'lib' + plat_specifier)

        # 'build_lib' jest the actual directory that we will use dla this
        # particular module distribution -- jeżeli user didn't supply it, pick
        # one of 'build_purelib' albo 'build_platlib'.
        jeżeli self.build_lib jest Nic:
            jeżeli self.distribution.ext_modules:
                self.build_lib = self.build_platlib
            inaczej:
                self.build_lib = self.build_purelib

        # 'build_temp' -- temporary directory dla compiler turds,
        # "build/temp.<plat>"
        jeżeli self.build_temp jest Nic:
            self.build_temp = os.path.join(self.build_base,
                                           'temp' + plat_specifier)
        jeżeli self.build_scripts jest Nic:
            self.build_scripts = os.path.join(self.build_base,
                                              'scripts-' + sys.version[0:3])

        jeżeli self.executable jest Nic:
            self.executable = os.path.normpath(sys.executable)

        jeżeli isinstance(self.parallel, str):
            spróbuj:
                self.parallel = int(self.parallel)
            wyjąwszy ValueError:
                podnieś DistutilsOptionError("parallel should be an integer")

    def run(self):
        # Run all relevant sub-commands.  This will be some subset of:
        #  - build_py      - pure Python modules
        #  - build_clib    - standalone C libraries
        #  - build_ext     - Python extensions
        #  - build_scripts - (Python) scripts
        dla cmd_name w self.get_sub_commands():
            self.run_command(cmd_name)


    # -- Predicates dla the sub-command list ---------------------------

    def has_pure_modules(self):
        zwróć self.distribution.has_pure_modules()

    def has_c_libraries(self):
        zwróć self.distribution.has_c_libraries()

    def has_ext_modules(self):
        zwróć self.distribution.has_ext_modules()

    def has_scripts(self):
        zwróć self.distribution.has_scripts()


    sub_commands = [('build_py',      has_pure_modules),
                    ('build_clib',    has_c_libraries),
                    ('build_ext',     has_ext_modules),
                    ('build_scripts', has_scripts),
                   ]
