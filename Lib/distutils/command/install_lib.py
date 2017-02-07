"""distutils.command.install_lib

Implements the Distutils 'install_lib' command
(install all Python modules)."""

zaimportuj os
zaimportuj importlib.util
zaimportuj sys

z distutils.core zaimportuj Command
z distutils.errors zaimportuj DistutilsOptionError


# Extension dla Python source files.
PYTHON_SOURCE_EXTENSION = ".py"

klasa install_lib(Command):

    description = "install all Python modules (extensions oraz pure Python)"

    # The byte-compilation options are a tad confusing.  Here are the
    # possible scenarios:
    #   1) no compilation at all (--no-compile --no-optimize)
    #   2) compile .pyc only (--compile --no-optimize; default)
    #   3) compile .pyc oraz "opt-1" .pyc (--compile --optimize)
    #   4) compile "opt-1" .pyc only (--no-compile --optimize)
    #   5) compile .pyc oraz "opt-2" .pyc (--compile --optimize-more)
    #   6) compile "opt-2" .pyc only (--no-compile --optimize-more)
    #
    # The UI dla this jest two options, 'compile' oraz 'optimize'.
    # 'compile' jest strictly boolean, oraz only decides whether to
    # generate .pyc files.  'optimize' jest three-way (0, 1, albo 2), oraz
    # decides both whether to generate .pyc files oraz what level of
    # optimization to use.

    user_options = [
        ('install-dir=', 'd', "directory to install to"),
        ('build-dir=','b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ('compile', 'c', "compile .py to .pyc [default]"),
        ('no-compile', Nic, "don't compile .py files"),
        ('optimize=', 'O',
         "also compile przy optimization: -O1 dla \"python -O\", "
         "-O2 dla \"python -OO\", oraz -O0 to disable [default: -O0]"),
        ('skip-build', Nic, "skip the build steps"),
        ]

    boolean_options = ['force', 'compile', 'skip-build']
    negative_opt = {'no-compile' : 'compile'}

    def initialize_options(self):
        # let the 'install' command dictate our installation directory
        self.install_dir = Nic
        self.build_dir = Nic
        self.force = 0
        self.compile = Nic
        self.optimize = Nic
        self.skip_build = Nic

    def finalize_options(self):
        # Get all the information we need to install pure Python modules
        # z the umbrella 'install' command -- build (source) directory,
        # install (target) directory, oraz whether to compile .py files.
        self.set_undefined_options('install',
                                   ('build_lib', 'build_dir'),
                                   ('install_lib', 'install_dir'),
                                   ('force', 'force'),
                                   ('compile', 'compile'),
                                   ('optimize', 'optimize'),
                                   ('skip_build', 'skip_build'),
                                  )

        jeżeli self.compile jest Nic:
            self.compile = Prawda
        jeżeli self.optimize jest Nic:
            self.optimize = Nieprawda

        jeżeli nie isinstance(self.optimize, int):
            spróbuj:
                self.optimize = int(self.optimize)
                jeżeli self.optimize nie w (0, 1, 2):
                    podnieś AssertionError
            wyjąwszy (ValueError, AssertionError):
                podnieś DistutilsOptionError("optimize must be 0, 1, albo 2")

    def run(self):
        # Make sure we have built everything we need first
        self.build()

        # Install everything: simply dump the entire contents of the build
        # directory to the installation directory (that's the beauty of
        # having a build directory!)
        outfiles = self.install()

        # (Optionally) compile .py to .pyc
        jeżeli outfiles jest nie Nic oraz self.distribution.has_pure_modules():
            self.byte_compile(outfiles)

    # -- Top-level worker functions ------------------------------------
    # (called z 'run()')

    def build(self):
        jeżeli nie self.skip_build:
            jeżeli self.distribution.has_pure_modules():
                self.run_command('build_py')
            jeżeli self.distribution.has_ext_modules():
                self.run_command('build_ext')

    def install(self):
        jeżeli os.path.isdir(self.build_dir):
            outfiles = self.copy_tree(self.build_dir, self.install_dir)
        inaczej:
            self.warn("'%s' does nie exist -- no Python modules to install" %
                      self.build_dir)
            zwróć
        zwróć outfiles

    def byte_compile(self, files):
        jeżeli sys.dont_write_bytecode:
            self.warn('byte-compiling jest disabled, skipping.')
            zwróć

        z distutils.util zaimportuj byte_compile

        # Get the "--root" directory supplied to the "install" command,
        # oraz use it jako a prefix to strip off the purported filename
        # encoded w bytecode files.  This jest far z complete, but it
        # should at least generate usable bytecode w RPM distributions.
        install_root = self.get_finalized_command('install').root

        jeżeli self.compile:
            byte_compile(files, optimize=0,
                         force=self.force, prefix=install_root,
                         dry_run=self.dry_run)
        jeżeli self.optimize > 0:
            byte_compile(files, optimize=self.optimize,
                         force=self.force, prefix=install_root,
                         verbose=self.verbose, dry_run=self.dry_run)


    # -- Utility methods -----------------------------------------------

    def _mutate_outputs(self, has_any, build_cmd, cmd_option, output_dir):
        jeżeli nie has_any:
            zwróć []

        build_cmd = self.get_finalized_command(build_cmd)
        build_files = build_cmd.get_outputs()
        build_dir = getattr(build_cmd, cmd_option)

        prefix_len = len(build_dir) + len(os.sep)
        outputs = []
        dla file w build_files:
            outputs.append(os.path.join(output_dir, file[prefix_len:]))

        zwróć outputs

    def _bytecode_filenames(self, py_filenames):
        bytecode_files = []
        dla py_file w py_filenames:
            # Since build_py handles package data installation, the
            # list of outputs can contain more than just .py files.
            # Make sure we only report bytecode dla the .py files.
            ext = os.path.splitext(os.path.normcase(py_file))[1]
            jeżeli ext != PYTHON_SOURCE_EXTENSION:
                kontynuuj
            jeżeli self.compile:
                bytecode_files.append(importlib.util.cache_from_source(
                    py_file, optimization=''))
            jeżeli self.optimize > 0:
                bytecode_files.append(importlib.util.cache_from_source(
                    py_file, optimization=self.optimize))

        zwróć bytecode_files


    # -- External interface --------------------------------------------
    # (called by outsiders)

    def get_outputs(self):
        """Return the list of files that would be installed jeżeli this command
        were actually run.  Not affected by the "dry-run" flag albo whether
        modules have actually been built yet.
        """
        pure_outputs = \
            self._mutate_outputs(self.distribution.has_pure_modules(),
                                 'build_py', 'build_lib',
                                 self.install_dir)
        jeżeli self.compile:
            bytecode_outputs = self._bytecode_filenames(pure_outputs)
        inaczej:
            bytecode_outputs = []

        ext_outputs = \
            self._mutate_outputs(self.distribution.has_ext_modules(),
                                 'build_ext', 'build_lib',
                                 self.install_dir)

        zwróć pure_outputs + bytecode_outputs + ext_outputs

    def get_inputs(self):
        """Get the list of files that are input to this command, ie. the
        files that get installed jako they are named w the build tree.
        The files w this list correspond one-to-one to the output
        filenames returned by 'get_outputs()'.
        """
        inputs = []

        jeżeli self.distribution.has_pure_modules():
            build_py = self.get_finalized_command('build_py')
            inputs.extend(build_py.get_outputs())

        jeżeli self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            inputs.extend(build_ext.get_outputs())

        zwróć inputs
