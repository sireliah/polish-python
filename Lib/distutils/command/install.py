"""distutils.command.install

Implements the Distutils 'install' command."""

zaimportuj sys
zaimportuj os

z distutils zaimportuj log
z distutils.core zaimportuj Command
z distutils.debug zaimportuj DEBUG
z distutils.sysconfig zaimportuj get_config_vars
z distutils.errors zaimportuj DistutilsPlatformError
z distutils.file_util zaimportuj write_file
z distutils.util zaimportuj convert_path, subst_vars, change_root
z distutils.util zaimportuj get_platform
z distutils.errors zaimportuj DistutilsOptionError

z site zaimportuj USER_BASE
z site zaimportuj USER_SITE
HAS_USER_SITE = Prawda

WINDOWS_SCHEME = {
    'purelib': '$base/Lib/site-packages',
    'platlib': '$base/Lib/site-packages',
    'headers': '$base/Include/$dist_name',
    'scripts': '$base/Scripts',
    'data'   : '$base',
}

INSTALL_SCHEMES = {
    'unix_prefix': {
        'purelib': '$base/lib/python$py_version_short/site-packages',
        'platlib': '$platbase/lib/python$py_version_short/site-packages',
        'headers': '$base/include/python$py_version_short$abiflags/$dist_name',
        'scripts': '$base/bin',
        'data'   : '$base',
        },
    'unix_home': {
        'purelib': '$base/lib/python',
        'platlib': '$base/lib/python',
        'headers': '$base/include/python/$dist_name',
        'scripts': '$base/bin',
        'data'   : '$base',
        },
    'nt': WINDOWS_SCHEME,
    }

# user site schemes
jeżeli HAS_USER_SITE:
    INSTALL_SCHEMES['nt_user'] = {
        'purelib': '$usersite',
        'platlib': '$usersite',
        'headers': '$userbase/Python$py_version_nodot/Include/$dist_name',
        'scripts': '$userbase/Python$py_version_nodot/Scripts',
        'data'   : '$userbase',
        }

    INSTALL_SCHEMES['unix_user'] = {
        'purelib': '$usersite',
        'platlib': '$usersite',
        'headers':
            '$userbase/include/python$py_version_short$abiflags/$dist_name',
        'scripts': '$userbase/bin',
        'data'   : '$userbase',
        }

# The keys to an installation scheme; jeżeli any new types of files are to be
# installed, be sure to add an entry to every installation scheme above,
# oraz to SCHEME_KEYS here.
SCHEME_KEYS = ('purelib', 'platlib', 'headers', 'scripts', 'data')


klasa install(Command):

    description = "install everything z build directory"

    user_options = [
        # Select installation scheme oraz set base director(y|ies)
        ('prefix=', Nic,
         "installation prefix"),
        ('exec-prefix=', Nic,
         "(Unix only) prefix dla platform-specific files"),
        ('home=', Nic,
         "(Unix only) home directory to install under"),

        # Or, just set the base director(y|ies)
        ('install-base=', Nic,
         "base installation directory (instead of --prefix albo --home)"),
        ('install-platbase=', Nic,
         "base installation directory dla platform-specific files " +
         "(instead of --exec-prefix albo --home)"),
        ('root=', Nic,
         "install everything relative to this alternate root directory"),

        # Or, explicitly set the installation scheme
        ('install-purelib=', Nic,
         "installation directory dla pure Python module distributions"),
        ('install-platlib=', Nic,
         "installation directory dla non-pure module distributions"),
        ('install-lib=', Nic,
         "installation directory dla all module distributions " +
         "(overrides --install-purelib oraz --install-platlib)"),

        ('install-headers=', Nic,
         "installation directory dla C/C++ headers"),
        ('install-scripts=', Nic,
         "installation directory dla Python scripts"),
        ('install-data=', Nic,
         "installation directory dla data files"),

        # Byte-compilation options -- see install_lib.py dla details, as
        # these are duplicated z there (but only install_lib does
        # anything przy them).
        ('compile', 'c', "compile .py to .pyc [default]"),
        ('no-compile', Nic, "don't compile .py files"),
        ('optimize=', 'O',
         "also compile przy optimization: -O1 dla \"python -O\", "
         "-O2 dla \"python -OO\", oraz -O0 to disable [default: -O0]"),

        # Miscellaneous control options
        ('force', 'f',
         "force installation (overwrite any existing files)"),
        ('skip-build', Nic,
         "skip rebuilding everything (dla testing/debugging)"),

        # Where to install documentation (eventually!)
        #('doc-format=', Nic, "format of documentation to generate"),
        #('install-man=', Nic, "directory dla Unix man pages"),
        #('install-html=', Nic, "directory dla HTML documentation"),
        #('install-info=', Nic, "directory dla GNU info files"),

        ('record=', Nic,
         "filename w which to record list of installed files"),
        ]

    boolean_options = ['compile', 'force', 'skip-build']

    jeżeli HAS_USER_SITE:
        user_options.append(('user', Nic,
                             "install w user site-package '%s'" % USER_SITE))
        boolean_options.append('user')

    negative_opt = {'no-compile' : 'compile'}


    def initialize_options(self):
        """Initializes options."""
        # High-level options: these select both an installation base
        # oraz scheme.
        self.prefix = Nic
        self.exec_prefix = Nic
        self.home = Nic
        self.user = 0

        # These select only the installation base; it's up to the user to
        # specify the installation scheme (currently, that means supplying
        # the --install-{platlib,purelib,scripts,data} options).
        self.install_base = Nic
        self.install_platbase = Nic
        self.root = Nic

        # These options are the actual installation directories; jeżeli nie
        # supplied by the user, they are filled w using the installation
        # scheme implied by prefix/exec-prefix/home oraz the contents of
        # that installation scheme.
        self.install_purelib = Nic     # dla pure module distributions
        self.install_platlib = Nic     # non-pure (dists w/ extensions)
        self.install_headers = Nic     # dla C/C++ headers
        self.install_lib = Nic         # set to either purelib albo platlib
        self.install_scripts = Nic
        self.install_data = Nic
        self.install_userbase = USER_BASE
        self.install_usersite = USER_SITE

        self.compile = Nic
        self.optimize = Nic

        # These two are dla putting non-packagized distributions into their
        # own directory oraz creating a .pth file jeżeli it makes sense.
        # 'extra_path' comes z the setup file; 'install_path_file' can
        # be turned off jeżeli it makes no sense to install a .pth file.  (But
        # better to install it uselessly than to guess wrong oraz nie
        # install it when it's necessary oraz would be used!)  Currently,
        # 'install_path_file' jest always true unless some outsider meddles
        # przy it.
        self.extra_path = Nic
        self.install_path_file = 1

        # 'force' forces installation, even jeżeli target files are nie
        # out-of-date.  'skip_build' skips running the "build" command,
        # handy jeżeli you know it's nie necessary.  'warn_dir' (which jest *not*
        # a user option, it's just there so the bdist_* commands can turn
        # it off) determines whether we warn about installing to a
        # directory nie w sys.path.
        self.force = 0
        self.skip_build = 0
        self.warn_dir = 1

        # These are only here jako a conduit z the 'build' command to the
        # 'install_*' commands that do the real work.  ('build_base' isn't
        # actually used anywhere, but it might be useful w future.)  They
        # are nie user options, because jeżeli the user told the install
        # command where the build directory is, that wouldn't affect the
        # build command.
        self.build_base = Nic
        self.build_lib = Nic

        # Not defined yet because we don't know anything about
        # documentation yet.
        #self.install_man = Nic
        #self.install_html = Nic
        #self.install_info = Nic

        self.record = Nic


    # -- Option finalizing methods -------------------------------------
    # (This jest rather more involved than dla most commands,
    # because this jest where the policy dla installing third-
    # party Python modules on various platforms given a wide
    # array of user input jest decided.  Yes, it's quite complex!)

    def finalize_options(self):
        """Finalizes options."""
        # This method (and its pliant slaves, like 'finalize_unix()',
        # 'finalize_other()', oraz 'select_scheme()') jest where the default
        # installation directories dla modules, extension modules, oraz
        # anything inaczej we care to install z a Python module
        # distribution.  Thus, this code makes a pretty important policy
        # statement about how third-party stuff jest added to a Python
        # installation!  Note that the actual work of installation jest done
        # by the relatively simple 'install_*' commands; they just take
        # their orders z the installation directory options determined
        # here.

        # Check dla errors/inconsistencies w the options; first, stuff
        # that's wrong on any platform.

        jeżeli ((self.prefix albo self.exec_prefix albo self.home) oraz
            (self.install_base albo self.install_platbase)):
            podnieś DistutilsOptionError(
                   "must supply either prefix/exec-prefix/home albo " +
                   "install-base/install-platbase -- nie both")

        jeżeli self.home oraz (self.prefix albo self.exec_prefix):
            podnieś DistutilsOptionError(
                  "must supply either home albo prefix/exec-prefix -- nie both")

        jeżeli self.user oraz (self.prefix albo self.exec_prefix albo self.home albo
                self.install_base albo self.install_platbase):
            podnieś DistutilsOptionError("can't combine user przy prefix, "
                                       "exec_prefix/home, albo install_(plat)base")

        # Next, stuff that's wrong (or dubious) only on certain platforms.
        jeżeli os.name != "posix":
            jeżeli self.exec_prefix:
                self.warn("exec-prefix option ignored on this platform")
                self.exec_prefix = Nic

        # Now the interesting logic -- so interesting that we farm it out
        # to other methods.  The goal of these methods jest to set the final
        # values dla the install_{lib,scripts,data,...}  options, using as
        # input a heady brew of prefix, exec_prefix, home, install_base,
        # install_platbase, user-supplied versions of
        # install_{purelib,platlib,lib,scripts,data,...}, oraz the
        # INSTALL_SCHEME dictionary above.  Phew!

        self.dump_dirs("pre-finalize_{unix,other}")

        jeżeli os.name == 'posix':
            self.finalize_unix()
        inaczej:
            self.finalize_other()

        self.dump_dirs("post-finalize_{unix,other}()")

        # Expand configuration variables, tilde, etc. w self.install_base
        # oraz self.install_platbase -- that way, we can use $base albo
        # $platbase w the other installation directories oraz nie worry
        # about needing recursive variable expansion (shudder).

        py_version = sys.version.split()[0]
        (prefix, exec_prefix) = get_config_vars('prefix', 'exec_prefix')
        spróbuj:
            abiflags = sys.abiflags
        wyjąwszy AttributeError:
            # sys.abiflags may nie be defined on all platforms.
            abiflags = ''
        self.config_vars = {'dist_name': self.distribution.get_name(),
                            'dist_version': self.distribution.get_version(),
                            'dist_fullname': self.distribution.get_fullname(),
                            'py_version': py_version,
                            'py_version_short': py_version[0:3],
                            'py_version_nodot': py_version[0] + py_version[2],
                            'sys_prefix': prefix,
                            'prefix': prefix,
                            'sys_exec_prefix': exec_prefix,
                            'exec_prefix': exec_prefix,
                            'abiflags': abiflags,
                           }

        jeżeli HAS_USER_SITE:
            self.config_vars['userbase'] = self.install_userbase
            self.config_vars['usersite'] = self.install_usersite

        self.expand_basedirs()

        self.dump_dirs("post-expand_basedirs()")

        # Now define config vars dla the base directories so we can expand
        # everything inaczej.
        self.config_vars['base'] = self.install_base
        self.config_vars['platbase'] = self.install_platbase

        jeżeli DEBUG:
            z pprint zaimportuj pprint
            print("config vars:")
            pprint(self.config_vars)

        # Expand "~" oraz configuration variables w the installation
        # directories.
        self.expand_dirs()

        self.dump_dirs("post-expand_dirs()")

        # Create directories w the home dir:
        jeżeli self.user:
            self.create_home_path()

        # Pick the actual directory to install all modules to: either
        # install_purelib albo install_platlib, depending on whether this
        # module distribution jest pure albo not.  Of course, jeżeli the user
        # already specified install_lib, use their selection.
        jeżeli self.install_lib jest Nic:
            jeżeli self.distribution.ext_modules: # has extensions: non-pure
                self.install_lib = self.install_platlib
            inaczej:
                self.install_lib = self.install_purelib


        # Convert directories z Unix /-separated syntax to the local
        # convention.
        self.convert_paths('lib', 'purelib', 'platlib',
                           'scripts', 'data', 'headers',
                           'userbase', 'usersite')

        # Well, we're nie actually fully completely finalized yet: we still
        # have to deal przy 'extra_path', which jest the hack dla allowing
        # non-packagized module distributions (hello, Numerical Python!) to
        # get their own directories.
        self.handle_extra_path()
        self.install_libbase = self.install_lib # needed dla .pth file
        self.install_lib = os.path.join(self.install_lib, self.extra_dirs)

        # If a new root directory was supplied, make all the installation
        # dirs relative to it.
        jeżeli self.root jest nie Nic:
            self.change_roots('libbase', 'lib', 'purelib', 'platlib',
                              'scripts', 'data', 'headers')

        self.dump_dirs("after prepending root")

        # Find out the build directories, ie. where to install from.
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'),
                                   ('build_lib', 'build_lib'))

        # Punt on doc directories dla now -- after all, we're punting on
        # documentation completely!

    def dump_dirs(self, msg):
        """Dumps the list of user options."""
        jeżeli nie DEBUG:
            zwróć
        z distutils.fancy_getopt zaimportuj longopt_xlate
        log.debug(msg + ":")
        dla opt w self.user_options:
            opt_name = opt[0]
            jeżeli opt_name[-1] == "=":
                opt_name = opt_name[0:-1]
            jeżeli opt_name w self.negative_opt:
                opt_name = self.negative_opt[opt_name]
                opt_name = opt_name.translate(longopt_xlate)
                val = nie getattr(self, opt_name)
            inaczej:
                opt_name = opt_name.translate(longopt_xlate)
                val = getattr(self, opt_name)
            log.debug("  %s: %s" % (opt_name, val))

    def finalize_unix(self):
        """Finalizes options dla posix platforms."""
        jeżeli self.install_base jest nie Nic albo self.install_platbase jest nie Nic:
            jeżeli ((self.install_lib jest Nic oraz
                 self.install_purelib jest Nic oraz
                 self.install_platlib jest Nic) albo
                self.install_headers jest Nic albo
                self.install_scripts jest Nic albo
                self.install_data jest Nic):
                podnieś DistutilsOptionError(
                      "install-base albo install-platbase supplied, but "
                      "installation scheme jest incomplete")
            zwróć

        jeżeli self.user:
            jeżeli self.install_userbase jest Nic:
                podnieś DistutilsPlatformError(
                    "User base directory jest nie specified")
            self.install_base = self.install_platbase = self.install_userbase
            self.select_scheme("unix_user")
        albo_inaczej self.home jest nie Nic:
            self.install_base = self.install_platbase = self.home
            self.select_scheme("unix_home")
        inaczej:
            jeżeli self.prefix jest Nic:
                jeżeli self.exec_prefix jest nie Nic:
                    podnieś DistutilsOptionError(
                          "must nie supply exec-prefix without prefix")

                self.prefix = os.path.normpath(sys.prefix)
                self.exec_prefix = os.path.normpath(sys.exec_prefix)

            inaczej:
                jeżeli self.exec_prefix jest Nic:
                    self.exec_prefix = self.prefix

            self.install_base = self.prefix
            self.install_platbase = self.exec_prefix
            self.select_scheme("unix_prefix")

    def finalize_other(self):
        """Finalizes options dla non-posix platforms"""
        jeżeli self.user:
            jeżeli self.install_userbase jest Nic:
                podnieś DistutilsPlatformError(
                    "User base directory jest nie specified")
            self.install_base = self.install_platbase = self.install_userbase
            self.select_scheme(os.name + "_user")
        albo_inaczej self.home jest nie Nic:
            self.install_base = self.install_platbase = self.home
            self.select_scheme("unix_home")
        inaczej:
            jeżeli self.prefix jest Nic:
                self.prefix = os.path.normpath(sys.prefix)

            self.install_base = self.install_platbase = self.prefix
            spróbuj:
                self.select_scheme(os.name)
            wyjąwszy KeyError:
                podnieś DistutilsPlatformError(
                      "I don't know how to install stuff on '%s'" % os.name)

    def select_scheme(self, name):
        """Sets the install directories by applying the install schemes."""
        # it's the caller's problem jeżeli they supply a bad name!
        scheme = INSTALL_SCHEMES[name]
        dla key w SCHEME_KEYS:
            attrname = 'install_' + key
            jeżeli getattr(self, attrname) jest Nic:
                setattr(self, attrname, scheme[key])

    def _expand_attrs(self, attrs):
        dla attr w attrs:
            val = getattr(self, attr)
            jeżeli val jest nie Nic:
                jeżeli os.name == 'posix' albo os.name == 'nt':
                    val = os.path.expanduser(val)
                val = subst_vars(val, self.config_vars)
                setattr(self, attr, val)

    def expand_basedirs(self):
        """Calls `os.path.expanduser` on install_base, install_platbase oraz
        root."""
        self._expand_attrs(['install_base', 'install_platbase', 'root'])

    def expand_dirs(self):
        """Calls `os.path.expanduser` on install dirs."""
        self._expand_attrs(['install_purelib', 'install_platlib',
                            'install_lib', 'install_headers',
                            'install_scripts', 'install_data',])

    def convert_paths(self, *names):
        """Call `convert_path` over `names`."""
        dla name w names:
            attr = "install_" + name
            setattr(self, attr, convert_path(getattr(self, attr)))

    def handle_extra_path(self):
        """Set `path_file` oraz `extra_dirs` using `extra_path`."""
        jeżeli self.extra_path jest Nic:
            self.extra_path = self.distribution.extra_path

        jeżeli self.extra_path jest nie Nic:
            jeżeli isinstance(self.extra_path, str):
                self.extra_path = self.extra_path.split(',')

            jeżeli len(self.extra_path) == 1:
                path_file = extra_dirs = self.extra_path[0]
            albo_inaczej len(self.extra_path) == 2:
                path_file, extra_dirs = self.extra_path
            inaczej:
                podnieś DistutilsOptionError(
                      "'extra_path' option must be a list, tuple, albo "
                      "comma-separated string przy 1 albo 2 elements")

            # convert to local form w case Unix notation used (as it
            # should be w setup scripts)
            extra_dirs = convert_path(extra_dirs)
        inaczej:
            path_file = Nic
            extra_dirs = ''

        # XXX should we warn jeżeli path_file oraz nie extra_dirs? (in which
        # case the path file would be harmless but pointless)
        self.path_file = path_file
        self.extra_dirs = extra_dirs

    def change_roots(self, *names):
        """Change the install directories pointed by name using root."""
        dla name w names:
            attr = "install_" + name
            setattr(self, attr, change_root(self.root, getattr(self, attr)))

    def create_home_path(self):
        """Create directories under ~."""
        jeżeli nie self.user:
            zwróć
        home = convert_path(os.path.expanduser("~"))
        dla name, path w self.config_vars.items():
            jeżeli path.startswith(home) oraz nie os.path.isdir(path):
                self.debug_print("os.makedirs('%s', 0o700)" % path)
                os.makedirs(path, 0o700)

    # -- Command execution methods -------------------------------------

    def run(self):
        """Runs the command."""
        # Obviously have to build before we can install
        jeżeli nie self.skip_build:
            self.run_command('build')
            # If we built dla any other platform, we can't install.
            build_plat = self.distribution.get_command_obj('build').plat_name
            # check warn_dir - it jest a clue that the 'install' jest happening
            # internally, oraz nie to sys.path, so we don't check the platform
            # matches what we are running.
            jeżeli self.warn_dir oraz build_plat != get_platform():
                podnieś DistutilsPlatformError("Can't install when "
                                             "cross-compiling")

        # Run all sub-commands (at least those that need to be run)
        dla cmd_name w self.get_sub_commands():
            self.run_command(cmd_name)

        jeżeli self.path_file:
            self.create_path_file()

        # write list of installed files, jeżeli requested.
        jeżeli self.record:
            outputs = self.get_outputs()
            jeżeli self.root:               # strip any package prefix
                root_len = len(self.root)
                dla counter w range(len(outputs)):
                    outputs[counter] = outputs[counter][root_len:]
            self.execute(write_file,
                         (self.record, outputs),
                         "writing list of installed files to '%s'" %
                         self.record)

        sys_path = map(os.path.normpath, sys.path)
        sys_path = map(os.path.normcase, sys_path)
        install_lib = os.path.normcase(os.path.normpath(self.install_lib))
        jeżeli (self.warn_dir oraz
            nie (self.path_file oraz self.install_path_file) oraz
            install_lib nie w sys_path):
            log.debug(("modules installed to '%s', which jest nie w "
                       "Python's module search path (sys.path) -- "
                       "you'll have to change the search path yourself"),
                       self.install_lib)

    def create_path_file(self):
        """Creates the .pth file"""
        filename = os.path.join(self.install_libbase,
                                self.path_file + ".pth")
        jeżeli self.install_path_file:
            self.execute(write_file,
                         (filename, [self.extra_dirs]),
                         "creating %s" % filename)
        inaczej:
            self.warn("path file '%s' nie created" % filename)


    # -- Reporting methods ---------------------------------------------

    def get_outputs(self):
        """Assembles the outputs of all the sub-commands."""
        outputs = []
        dla cmd_name w self.get_sub_commands():
            cmd = self.get_finalized_command(cmd_name)
            # Add the contents of cmd.get_outputs(), ensuring
            # that outputs doesn't contain duplicate entries
            dla filename w cmd.get_outputs():
                jeżeli filename nie w outputs:
                    outputs.append(filename)

        jeżeli self.path_file oraz self.install_path_file:
            outputs.append(os.path.join(self.install_libbase,
                                        self.path_file + ".pth"))

        zwróć outputs

    def get_inputs(self):
        """Returns the inputs of all the sub-commands"""
        # XXX gee, this looks familiar ;-(
        inputs = []
        dla cmd_name w self.get_sub_commands():
            cmd = self.get_finalized_command(cmd_name)
            inputs.extend(cmd.get_inputs())

        zwróć inputs

    # -- Predicates dla sub-command list -------------------------------

    def has_lib(self):
        """Returns true jeżeli the current distribution has any Python
        modules to install."""
        zwróć (self.distribution.has_pure_modules() albo
                self.distribution.has_ext_modules())

    def has_headers(self):
        """Returns true jeżeli the current distribution has any headers to
        install."""
        zwróć self.distribution.has_headers()

    def has_scripts(self):
        """Returns true jeżeli the current distribution has any scripts to.
        install."""
        zwróć self.distribution.has_scripts()

    def has_data(self):
        """Returns true jeżeli the current distribution has any data to.
        install."""
        zwróć self.distribution.has_data_files()

    # 'sub_commands': a list of commands this command might have to run to
    # get its work done.  See cmd.py dla more info.
    sub_commands = [('install_lib',     has_lib),
                    ('install_headers', has_headers),
                    ('install_scripts', has_scripts),
                    ('install_data',    has_data),
                    ('install_egg_info', lambda self:Prawda),
                   ]
