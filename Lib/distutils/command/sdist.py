"""distutils.command.sdist

Implements the Distutils 'sdist' command (create a source distribution)."""

zaimportuj os
zaimportuj string
zaimportuj sys
z types zaimportuj *
z glob zaimportuj glob
z warnings zaimportuj warn

z distutils.core zaimportuj Command
z distutils zaimportuj dir_util, dep_util, file_util, archive_util
z distutils.text_file zaimportuj TextFile
z distutils.errors zaimportuj *
z distutils.filelist zaimportuj FileList
z distutils zaimportuj log
z distutils.util zaimportuj convert_path

def show_formats():
    """Print all possible values dla the 'formats' option (used by
    the "--help-formats" command-line option).
    """
    z distutils.fancy_getopt zaimportuj FancyGetopt
    z distutils.archive_util zaimportuj ARCHIVE_FORMATS
    formats = []
    dla format w ARCHIVE_FORMATS.keys():
        formats.append(("formats=" + format, Nic,
                        ARCHIVE_FORMATS[format][2]))
    formats.sort()
    FancyGetopt(formats).print_help(
        "List of available source distribution formats:")

klasa sdist(Command):

    description = "create a source distribution (tarball, zip file, etc.)"

    def checking_metadata(self):
        """Callable used dla the check sub-command.

        Placed here so user_options can view it"""
        zwróć self.metadata_check

    user_options = [
        ('template=', 't',
         "name of manifest template file [default: MANIFEST.in]"),
        ('manifest=', 'm',
         "name of manifest file [default: MANIFEST]"),
        ('use-defaults', Nic,
         "include the default file set w the manifest "
         "[default; disable przy --no-defaults]"),
        ('no-defaults', Nic,
         "don't include the default file set"),
        ('prune', Nic,
         "specifically exclude files/directories that should nie be "
         "distributed (build tree, RCS/CVS dirs, etc.) "
         "[default; disable przy --no-prune]"),
        ('no-prune', Nic,
         "don't automatically exclude anything"),
        ('manifest-only', 'o',
         "just regenerate the manifest oraz then stop "
         "(implies --force-manifest)"),
        ('force-manifest', 'f',
         "forcibly regenerate the manifest oraz carry on jako usual. "
         "Deprecated: now the manifest jest always regenerated."),
        ('formats=', Nic,
         "formats dla source distribution (comma-separated list)"),
        ('keep-temp', 'k',
         "keep the distribution tree around after creating " +
         "archive file(s)"),
        ('dist-dir=', 'd',
         "directory to put the source distribution archive(s) w "
         "[default: dist]"),
        ('metadata-check', Nic,
         "Ensure that all required elements of meta-data "
         "are supplied. Warn jeżeli any missing. [default]"),
        ('owner=', 'u',
         "Owner name used when creating a tar file [default: current user]"),
        ('group=', 'g',
         "Group name used when creating a tar file [default: current group]"),
        ]

    boolean_options = ['use-defaults', 'prune',
                       'manifest-only', 'force-manifest',
                       'keep-temp', 'metadata-check']

    help_options = [
        ('help-formats', Nic,
         "list available distribution formats", show_formats),
        ]

    negative_opt = {'no-defaults': 'use-defaults',
                    'no-prune': 'prune' }

    default_format = {'posix': 'gztar',
                      'nt': 'zip' }

    sub_commands = [('check', checking_metadata)]

    def initialize_options(self):
        # 'template' oraz 'manifest' are, respectively, the names of
        # the manifest template oraz manifest file.
        self.template = Nic
        self.manifest = Nic

        # 'use_defaults': jeżeli true, we will include the default file set
        # w the manifest
        self.use_defaults = 1
        self.prune = 1

        self.manifest_only = 0
        self.force_manifest = 0

        self.formats = Nic
        self.keep_temp = 0
        self.dist_dir = Nic

        self.archive_files = Nic
        self.metadata_check = 1
        self.owner = Nic
        self.group = Nic

    def finalize_options(self):
        jeżeli self.manifest jest Nic:
            self.manifest = "MANIFEST"
        jeżeli self.template jest Nic:
            self.template = "MANIFEST.in"

        self.ensure_string_list('formats')
        jeżeli self.formats jest Nic:
            spróbuj:
                self.formats = [self.default_format[os.name]]
            wyjąwszy KeyError:
                podnieś DistutilsPlatformError(
                      "don't know how to create source distributions "
                      "on platform %s" % os.name)

        bad_format = archive_util.check_archive_formats(self.formats)
        jeżeli bad_format:
            podnieś DistutilsOptionError(
                  "unknown archive format '%s'" % bad_format)

        jeżeli self.dist_dir jest Nic:
            self.dist_dir = "dist"

    def run(self):
        # 'filelist' contains the list of files that will make up the
        # manifest
        self.filelist = FileList()

        # Run sub commands
        dla cmd_name w self.get_sub_commands():
            self.run_command(cmd_name)

        # Do whatever it takes to get the list of files to process
        # (process the manifest template, read an existing manifest,
        # whatever).  File list jest accumulated w 'self.filelist'.
        self.get_file_list()

        # If user just wanted us to regenerate the manifest, stop now.
        jeżeli self.manifest_only:
            zwróć

        # Otherwise, go ahead oraz create the source distribution tarball,
        # albo zipfile, albo whatever.
        self.make_distribution()

    def check_metadata(self):
        """Deprecated API."""
        warn("distutils.command.sdist.check_metadata jest deprecated, \
              use the check command instead", PendingDeprecationWarning)
        check = self.distribution.get_command_obj('check')
        check.ensure_finalized()
        check.run()

    def get_file_list(self):
        """Figure out the list of files to include w the source
        distribution, oraz put it w 'self.filelist'.  This might involve
        reading the manifest template (and writing the manifest), albo just
        reading the manifest, albo just using the default file set -- it all
        depends on the user's options.
        """
        # new behavior when using a template:
        # the file list jest recalculated every time because
        # even jeżeli MANIFEST.in albo setup.py are nie changed
        # the user might have added some files w the tree that
        # need to be included.
        #
        #  This makes --force the default oraz only behavior przy templates.
        template_exists = os.path.isfile(self.template)
        jeżeli nie template_exists oraz self._manifest_is_not_generated():
            self.read_manifest()
            self.filelist.sort()
            self.filelist.remove_duplicates()
            zwróć

        jeżeli nie template_exists:
            self.warn(("manifest template '%s' does nie exist " +
                        "(using default file list)") %
                        self.template)
        self.filelist.findall()

        jeżeli self.use_defaults:
            self.add_defaults()

        jeżeli template_exists:
            self.read_template()

        jeżeli self.prune:
            self.prune_file_list()

        self.filelist.sort()
        self.filelist.remove_duplicates()
        self.write_manifest()

    def add_defaults(self):
        """Add all the default files to self.filelist:
          - README albo README.txt
          - setup.py
          - test/test*.py
          - all pure Python modules mentioned w setup script
          - all files pointed by package_data (build_py)
          - all files defined w data_files.
          - all files defined jako scripts.
          - all C sources listed jako part of extensions albo C libraries
            w the setup script (doesn't catch C headers!)
        Warns jeżeli (README albo README.txt) albo setup.py are missing; everything
        inaczej jest optional.
        """
        standards = [('README', 'README.txt'), self.distribution.script_name]
        dla fn w standards:
            jeżeli isinstance(fn, tuple):
                alts = fn
                got_it = Nieprawda
                dla fn w alts:
                    jeżeli os.path.exists(fn):
                        got_it = Prawda
                        self.filelist.append(fn)
                        przerwij

                jeżeli nie got_it:
                    self.warn("standard file nie found: should have one of " +
                              ', '.join(alts))
            inaczej:
                jeżeli os.path.exists(fn):
                    self.filelist.append(fn)
                inaczej:
                    self.warn("standard file '%s' nie found" % fn)

        optional = ['test/test*.py', 'setup.cfg']
        dla pattern w optional:
            files = filter(os.path.isfile, glob(pattern))
            self.filelist.extend(files)

        # build_py jest used to get:
        #  - python modules
        #  - files defined w package_data
        build_py = self.get_finalized_command('build_py')

        # getting python files
        jeżeli self.distribution.has_pure_modules():
            self.filelist.extend(build_py.get_source_files())

        # getting package_data files
        # (computed w build_py.data_files by build_py.finalize_options)
        dla pkg, src_dir, build_dir, filenames w build_py.data_files:
            dla filename w filenames:
                self.filelist.append(os.path.join(src_dir, filename))

        # getting distribution.data_files
        jeżeli self.distribution.has_data_files():
            dla item w self.distribution.data_files:
                jeżeli isinstance(item, str): # plain file
                    item = convert_path(item)
                    jeżeli os.path.isfile(item):
                        self.filelist.append(item)
                inaczej:    # a (dirname, filenames) tuple
                    dirname, filenames = item
                    dla f w filenames:
                        f = convert_path(f)
                        jeżeli os.path.isfile(f):
                            self.filelist.append(f)

        jeżeli self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            self.filelist.extend(build_ext.get_source_files())

        jeżeli self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command('build_clib')
            self.filelist.extend(build_clib.get_source_files())

        jeżeli self.distribution.has_scripts():
            build_scripts = self.get_finalized_command('build_scripts')
            self.filelist.extend(build_scripts.get_source_files())

    def read_template(self):
        """Read oraz parse manifest template file named by self.template.

        (usually "MANIFEST.in") The parsing oraz processing jest done by
        'self.filelist', which updates itself accordingly.
        """
        log.info("reading manifest template '%s'", self.template)
        template = TextFile(self.template, strip_comments=1, skip_blanks=1,
                            join_lines=1, lstrip_ws=1, rstrip_ws=1,
                            collapse_join=1)

        spróbuj:
            dopóki Prawda:
                line = template.readline()
                jeżeli line jest Nic:            # end of file
                    przerwij

                spróbuj:
                    self.filelist.process_template_line(line)
                # the call above can podnieś a DistutilsTemplateError for
                # malformed lines, albo a ValueError z the lower-level
                # convert_path function
                wyjąwszy (DistutilsTemplateError, ValueError) jako msg:
                    self.warn("%s, line %d: %s" % (template.filename,
                                                   template.current_line,
                                                   msg))
        w_końcu:
            template.close()

    def prune_file_list(self):
        """Prune off branches that might slip into the file list jako created
        by 'read_template()', but really don't belong there:
          * the build tree (typically "build")
          * the release tree itself (only an issue jeżeli we ran "sdist"
            previously przy --keep-temp, albo it aborted)
          * any RCS, CVS, .svn, .hg, .git, .bzr, _darcs directories
        """
        build = self.get_finalized_command('build')
        base_dir = self.distribution.get_fullname()

        self.filelist.exclude_pattern(Nic, prefix=build.build_base)
        self.filelist.exclude_pattern(Nic, prefix=base_dir)

        jeżeli sys.platform == 'win32':
            seps = r'/|\\'
        inaczej:
            seps = '/'

        vcs_dirs = ['RCS', 'CVS', r'\.svn', r'\.hg', r'\.git', r'\.bzr',
                    '_darcs']
        vcs_ptrn = r'(^|%s)(%s)(%s).*' % (seps, '|'.join(vcs_dirs), seps)
        self.filelist.exclude_pattern(vcs_ptrn, is_regex=1)

    def write_manifest(self):
        """Write the file list w 'self.filelist' (presumably jako filled w
        by 'add_defaults()' oraz 'read_template()') to the manifest file
        named by 'self.manifest'.
        """
        jeżeli self._manifest_is_not_generated():
            log.info("not writing to manually maintained "
                     "manifest file '%s'" % self.manifest)
            zwróć

        content = self.filelist.files[:]
        content.insert(0, '# file GENERATED by distutils, do NOT edit')
        self.execute(file_util.write_file, (self.manifest, content),
                     "writing manifest file '%s'" % self.manifest)

    def _manifest_is_not_generated(self):
        # check dla special comment used w 3.1.3 oraz higher
        jeżeli nie os.path.isfile(self.manifest):
            zwróć Nieprawda

        fp = open(self.manifest)
        spróbuj:
            first_line = fp.readline()
        w_końcu:
            fp.close()
        zwróć first_line != '# file GENERATED by distutils, do NOT edit\n'

    def read_manifest(self):
        """Read the manifest file (named by 'self.manifest') oraz use it to
        fill w 'self.filelist', the list of files to include w the source
        distribution.
        """
        log.info("reading manifest file '%s'", self.manifest)
        manifest = open(self.manifest)
        dla line w manifest:
            # ignore comments oraz blank lines
            line = line.strip()
            jeżeli line.startswith('#') albo nie line:
                kontynuuj
            self.filelist.append(line)
        manifest.close()

    def make_release_tree(self, base_dir, files):
        """Create the directory tree that will become the source
        distribution archive.  All directories implied by the filenames w
        'files' are created under 'base_dir', oraz then we hard link albo copy
        (jeżeli hard linking jest unavailable) those files into place.
        Essentially, this duplicates the developer's source tree, but w a
        directory named after the distribution, containing only the files
        to be distributed.
        """
        # Create all the directories under 'base_dir' necessary to
        # put 'files' there; the 'mkpath()' jest just so we don't die
        # jeżeli the manifest happens to be empty.
        self.mkpath(base_dir)
        dir_util.create_tree(base_dir, files, dry_run=self.dry_run)

        # And walk over the list of files, either making a hard link (if
        # os.link exists) to each one that doesn't already exist w its
        # corresponding location under 'base_dir', albo copying each file
        # that's out-of-date w 'base_dir'.  (Usually, all files will be
        # out-of-date, because by default we blow away 'base_dir' when
        # we're done making the distribution archives.)

        jeżeli hasattr(os, 'link'):        # can make hard links on this system
            link = 'hard'
            msg = "making hard links w %s..." % base_dir
        inaczej:                           # nope, have to copy
            link = Nic
            msg = "copying files to %s..." % base_dir

        jeżeli nie files:
            log.warn("no files to distribute -- empty manifest?")
        inaczej:
            log.info(msg)
        dla file w files:
            jeżeli nie os.path.isfile(file):
                log.warn("'%s' nie a regular file -- skipping" % file)
            inaczej:
                dest = os.path.join(base_dir, file)
                self.copy_file(file, dest, link=link)

        self.distribution.metadata.write_pkg_info(base_dir)

    def make_distribution(self):
        """Create the source distribution(s).  First, we create the release
        tree przy 'make_release_tree()'; then, we create all required
        archive files (according to 'self.formats') z the release tree.
        Finally, we clean up by blowing away the release tree (unless
        'self.keep_temp' jest true).  The list of archive files created jest
        stored so it can be retrieved later by 'get_archive_files()'.
        """
        # Don't warn about missing meta-data here -- should be (and is!)
        # done inaczejwhere.
        base_dir = self.distribution.get_fullname()
        base_name = os.path.join(self.dist_dir, base_dir)

        self.make_release_tree(base_dir, self.filelist.files)
        archive_files = []              # remember names of files we create
        # tar archive must be created last to avoid overwrite oraz remove
        jeżeli 'tar' w self.formats:
            self.formats.append(self.formats.pop(self.formats.index('tar')))

        dla fmt w self.formats:
            file = self.make_archive(base_name, fmt, base_dir=base_dir,
                                     owner=self.owner, group=self.group)
            archive_files.append(file)
            self.distribution.dist_files.append(('sdist', '', file))

        self.archive_files = archive_files

        jeżeli nie self.keep_temp:
            dir_util.remove_tree(base_dir, dry_run=self.dry_run)

    def get_archive_files(self):
        """Return the list of archive files created when the command
        was run, albo Nic jeżeli the command hasn't run yet.
        """
        zwróć self.archive_files
