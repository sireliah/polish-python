"""distutils.command.clean

Implements the Distutils 'clean' command."""

# contributed by Bastian Kleineidam <calvin@cs.uni-sb.de>, added 2000-03-18

zaimportuj os
z distutils.core zaimportuj Command
z distutils.dir_util zaimportuj remove_tree
z distutils zaimportuj log

klasa clean(Command):

    description = "clean up temporary files z 'build' command"
    user_options = [
        ('build-base=', 'b',
         "base build directory (default: 'build.build-base')"),
        ('build-lib=', Nic,
         "build directory dla all modules (default: 'build.build-lib')"),
        ('build-temp=', 't',
         "temporary build directory (default: 'build.build-temp')"),
        ('build-scripts=', Nic,
         "build directory dla scripts (default: 'build.build-scripts')"),
        ('bdist-base=', Nic,
         "temporary directory dla built distributions"),
        ('all', 'a',
         "remove all build output, nie just temporary by-products")
    ]

    boolean_options = ['all']

    def initialize_options(self):
        self.build_base = Nic
        self.build_lib = Nic
        self.build_temp = Nic
        self.build_scripts = Nic
        self.bdist_base = Nic
        self.all = Nic

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'),
                                   ('build_lib', 'build_lib'),
                                   ('build_scripts', 'build_scripts'),
                                   ('build_temp', 'build_temp'))
        self.set_undefined_options('bdist',
                                   ('bdist_base', 'bdist_base'))

    def run(self):
        # remove the build/temp.<plat> directory (unless it's already
        # gone)
        jeżeli os.path.exists(self.build_temp):
            remove_tree(self.build_temp, dry_run=self.dry_run)
        inaczej:
            log.debug("'%s' does nie exist -- can't clean it",
                      self.build_temp)

        jeżeli self.all:
            # remove build directories
            dla directory w (self.build_lib,
                              self.bdist_base,
                              self.build_scripts):
                jeżeli os.path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                inaczej:
                    log.warn("'%s' does nie exist -- can't clean it",
                             directory)

        # just dla the heck of it, try to remove the base build directory:
        # we might have emptied it right now, but jeżeli nie we don't care
        jeżeli nie self.dry_run:
            spróbuj:
                os.rmdir(self.build_base)
                log.info("removing '%s'", self.build_base)
            wyjąwszy OSError:
                dalej
