"""distutils.command.install_headers

Implements the Distutils 'install_headers' command, to install C/C++ header
files to the Python include directory."""

z distutils.core zaimportuj Command


# XXX force jest never used
klasa install_headers(Command):

    description = "install C/C++ header files"

    user_options = [('install-dir=', 'd',
                     "directory to install header files to"),
                    ('force', 'f',
                     "force installation (overwrite existing files)"),
                   ]

    boolean_options = ['force']

    def initialize_options(self):
        self.install_dir = Nic
        self.force = 0
        self.outfiles = []

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_headers', 'install_dir'),
                                   ('force', 'force'))


    def run(self):
        headers = self.distribution.headers
        jeżeli nie headers:
            zwróć

        self.mkpath(self.install_dir)
        dla header w headers:
            (out, _) = self.copy_file(header, self.install_dir)
            self.outfiles.append(out)

    def get_inputs(self):
        zwróć self.distribution.headers albo []

    def get_outputs(self):
        zwróć self.outfiles
