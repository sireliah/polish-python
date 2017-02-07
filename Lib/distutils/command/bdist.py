"""distutils.command.bdist

Implements the Distutils 'bdist' command (create a built [binary]
distribution)."""

zaimportuj os
z distutils.core zaimportuj Command
z distutils.errors zaimportuj *
z distutils.util zaimportuj get_platform


def show_formats():
    """Print list of available formats (arguments to "--format" option).
    """
    z distutils.fancy_getopt zaimportuj FancyGetopt
    formats = []
    dla format w bdist.format_commands:
        formats.append(("formats=" + format, Nic,
                        bdist.format_command[format][1]))
    pretty_printer = FancyGetopt(formats)
    pretty_printer.print_help("List of available distribution formats:")


klasa bdist(Command):

    description = "create a built (binary) distribution"

    user_options = [('bdist-base=', 'b',
                     "temporary directory dla creating built distributions"),
                    ('plat-name=', 'p',
                     "platform name to embed w generated filenames "
                     "(default: %s)" % get_platform()),
                    ('formats=', Nic,
                     "formats dla distribution (comma-separated list)"),
                    ('dist-dir=', 'd',
                     "directory to put final built distributions w "
                     "[default: dist]"),
                    ('skip-build', Nic,
                     "skip rebuilding everything (dla testing/debugging)"),
                    ('owner=', 'u',
                     "Owner name used when creating a tar file"
                     " [default: current user]"),
                    ('group=', 'g',
                     "Group name used when creating a tar file"
                     " [default: current group]"),
                   ]

    boolean_options = ['skip-build']

    help_options = [
        ('help-formats', Nic,
         "lists available distribution formats", show_formats),
        ]

    # The following commands do nie take a format option z bdist
    no_format_option = ('bdist_rpm',)

    # This won't do w reality: will need to distinguish RPM-ish Linux,
    # Debian-ish Linux, Solaris, FreeBSD, ..., Windows, Mac OS.
    default_format = {'posix': 'gztar',
                      'nt': 'zip'}

    # Establish the preferred order (dla the --help-formats option).
    format_commands = ['rpm', 'gztar', 'bztar', 'xztar', 'ztar', 'tar',
                       'wininst', 'zip', 'msi']

    # And the real information.
    format_command = {'rpm':   ('bdist_rpm',  "RPM distribution"),
                      'gztar': ('bdist_dumb', "gzip'ed tar file"),
                      'bztar': ('bdist_dumb', "bzip2'ed tar file"),
                      'xztar': ('bdist_dumb', "xz'ed tar file"),
                      'ztar':  ('bdist_dumb', "compressed tar file"),
                      'tar':   ('bdist_dumb', "tar file"),
                      'wininst': ('bdist_wininst',
                                  "Windows executable installer"),
                      'zip':   ('bdist_dumb', "ZIP file"),
                      'msi':   ('bdist_msi',  "Microsoft Installer")
                      }


    def initialize_options(self):
        self.bdist_base = Nic
        self.plat_name = Nic
        self.formats = Nic
        self.dist_dir = Nic
        self.skip_build = 0
        self.group = Nic
        self.owner = Nic

    def finalize_options(self):
        # have to finalize 'plat_name' before 'bdist_base'
        jeżeli self.plat_name jest Nic:
            jeżeli self.skip_build:
                self.plat_name = get_platform()
            inaczej:
                self.plat_name = self.get_finalized_command('build').plat_name

        # 'bdist_base' -- parent of per-built-distribution-format
        # temporary directories (eg. we'll probably have
        # "build/bdist.<plat>/dumb", "build/bdist.<plat>/rpm", etc.)
        jeżeli self.bdist_base jest Nic:
            build_base = self.get_finalized_command('build').build_base
            self.bdist_base = os.path.join(build_base,
                                           'bdist.' + self.plat_name)

        self.ensure_string_list('formats')
        jeżeli self.formats jest Nic:
            spróbuj:
                self.formats = [self.default_format[os.name]]
            wyjąwszy KeyError:
                podnieś DistutilsPlatformError(
                      "don't know how to create built distributions "
                      "on platform %s" % os.name)

        jeżeli self.dist_dir jest Nic:
            self.dist_dir = "dist"

    def run(self):
        # Figure out which sub-commands we need to run.
        commands = []
        dla format w self.formats:
            spróbuj:
                commands.append(self.format_command[format][0])
            wyjąwszy KeyError:
                podnieś DistutilsOptionError("invalid format '%s'" % format)

        # Reinitialize oraz run each command.
        dla i w range(len(self.formats)):
            cmd_name = commands[i]
            sub_cmd = self.reinitialize_command(cmd_name)
            jeżeli cmd_name nie w self.no_format_option:
                sub_cmd.format = self.formats[i]

            # dalejing the owner oraz group names dla tar archiving
            jeżeli cmd_name == 'bdist_dumb':
                sub_cmd.owner = self.owner
                sub_cmd.group = self.group

            # If we're going to need to run this command again, tell it to
            # keep its temporary files around so subsequent runs go faster.
            jeżeli cmd_name w commands[i+1:]:
                sub_cmd.keep_temp = 1
            self.run_command(cmd_name)
