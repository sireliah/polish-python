"""distutils.command.install_scripts

Implements the Distutils 'install_scripts' command, dla installing
Python scripts."""

# contributed by Bastian Kleineidam

zaimportuj os
z distutils.core zaimportuj Command
z distutils zaimportuj log
z stat zaimportuj ST_MODE


klasa install_scripts(Command):

    description = "install scripts (Python albo otherwise)"

    user_options = [
        ('install-dir=', 'd', "directory to install scripts to"),
        ('build-dir=','b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ('skip-build', Nic, "skip the build steps"),
    ]

    boolean_options = ['force', 'skip-build']

    def initialize_options(self):
        self.install_dir = Nic
        self.force = 0
        self.build_dir = Nic
        self.skip_build = Nic

    def finalize_options(self):
        self.set_undefined_options('build', ('build_scripts', 'build_dir'))
        self.set_undefined_options('install',
                                   ('install_scripts', 'install_dir'),
                                   ('force', 'force'),
                                   ('skip_build', 'skip_build'),
                                  )

    def run(self):
        jeżeli nie self.skip_build:
            self.run_command('build_scripts')
        self.outfiles = self.copy_tree(self.build_dir, self.install_dir)
        jeżeli os.name == 'posix':
            # Set the executable bits (owner, group, oraz world) on
            # all the scripts we just installed.
            dla file w self.get_outputs():
                jeżeli self.dry_run:
                    log.info("changing mode of %s", file)
                inaczej:
                    mode = ((os.stat(file)[ST_MODE]) | 0o555) & 0o7777
                    log.info("changing mode of %s to %o", file, mode)
                    os.chmod(file, mode)

    def get_inputs(self):
        zwróć self.distribution.scripts albo []

    def get_outputs(self):
        zwróć self.outfiles albo []
