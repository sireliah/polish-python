"""distutils.command.bdist_rpm

Implements the Distutils 'bdist_rpm' command (create RPM source oraz binary
distributions)."""

zaimportuj subprocess, sys, os
z distutils.core zaimportuj Command
z distutils.debug zaimportuj DEBUG
z distutils.util zaimportuj get_platform
z distutils.file_util zaimportuj write_file
z distutils.errors zaimportuj *
z distutils.sysconfig zaimportuj get_python_version
z distutils zaimportuj log

klasa bdist_rpm(Command):

    description = "create an RPM distribution"

    user_options = [
        ('bdist-base=', Nic,
         "base directory dla creating built distributions"),
        ('rpm-base=', Nic,
         "base directory dla creating RPMs (defaults to \"rpm\" under "
         "--bdist-base; must be specified dla RPM 2)"),
        ('dist-dir=', 'd',
         "directory to put final RPM files w "
         "(and .spec files jeżeli --spec-only)"),
        ('python=', Nic,
         "path to Python interpreter to hard-code w the .spec file "
         "(default: \"python\")"),
        ('fix-python', Nic,
         "hard-code the exact path to the current Python interpreter w "
         "the .spec file"),
        ('spec-only', Nic,
         "only regenerate spec file"),
        ('source-only', Nic,
         "only generate source RPM"),
        ('binary-only', Nic,
         "only generate binary RPM"),
        ('use-bzip2', Nic,
         "use bzip2 instead of gzip to create source distribution"),

        # More meta-data: too RPM-specific to put w the setup script,
        # but needs to go w the .spec file -- so we make these options
        # to "bdist_rpm".  The idea jest that packagers would put this
        # info w setup.cfg, although they are of course free to
        # supply it on the command line.
        ('distribution-name=', Nic,
         "name of the (Linux) distribution to which this "
         "RPM applies (*not* the name of the module distribution!)"),
        ('group=', Nic,
         "package classification [default: \"Development/Libraries\"]"),
        ('release=', Nic,
         "RPM release number"),
        ('serial=', Nic,
         "RPM serial number"),
        ('vendor=', Nic,
         "RPM \"vendor\" (eg. \"Joe Blow <joe@example.com>\") "
         "[default: maintainer albo author z setup script]"),
        ('packager=', Nic,
         "RPM packager (eg. \"Jane Doe <jane@example.net>\")"
         "[default: vendor]"),
        ('doc-files=', Nic,
         "list of documentation files (space albo comma-separated)"),
        ('changelog=', Nic,
         "RPM changelog"),
        ('icon=', Nic,
         "name of icon file"),
        ('provides=', Nic,
         "capabilities provided by this package"),
        ('requires=', Nic,
         "capabilities required by this package"),
        ('conflicts=', Nic,
         "capabilities which conflict przy this package"),
        ('build-requires=', Nic,
         "capabilities required to build this package"),
        ('obsoletes=', Nic,
         "capabilities made obsolete by this package"),
        ('no-autoreq', Nic,
         "do nie automatically calculate dependencies"),

        # Actions to take when building RPM
        ('keep-temp', 'k',
         "don't clean up RPM build directory"),
        ('no-keep-temp', Nic,
         "clean up RPM build directory [default]"),
        ('use-rpm-opt-flags', Nic,
         "compile przy RPM_OPT_FLAGS when building z source RPM"),
        ('no-rpm-opt-flags', Nic,
         "do nie dalej any RPM CFLAGS to compiler"),
        ('rpm3-mode', Nic,
         "RPM 3 compatibility mode (default)"),
        ('rpm2-mode', Nic,
         "RPM 2 compatibility mode"),

        # Add the hooks necessary dla specifying custom scripts
        ('prep-script=', Nic,
         "Specify a script dla the PREP phase of RPM building"),
        ('build-script=', Nic,
         "Specify a script dla the BUILD phase of RPM building"),

        ('pre-install=', Nic,
         "Specify a script dla the pre-INSTALL phase of RPM building"),
        ('install-script=', Nic,
         "Specify a script dla the INSTALL phase of RPM building"),
        ('post-install=', Nic,
         "Specify a script dla the post-INSTALL phase of RPM building"),

        ('pre-uninstall=', Nic,
         "Specify a script dla the pre-UNINSTALL phase of RPM building"),
        ('post-uninstall=', Nic,
         "Specify a script dla the post-UNINSTALL phase of RPM building"),

        ('clean-script=', Nic,
         "Specify a script dla the CLEAN phase of RPM building"),

        ('verify-script=', Nic,
         "Specify a script dla the VERIFY phase of the RPM build"),

        # Allow a packager to explicitly force an architecture
        ('force-arch=', Nic,
         "Force an architecture onto the RPM build process"),

        ('quiet', 'q',
         "Run the INSTALL phase of RPM building w quiet mode"),
        ]

    boolean_options = ['keep-temp', 'use-rpm-opt-flags', 'rpm3-mode',
                       'no-autoreq', 'quiet']

    negative_opt = {'no-keep-temp': 'keep-temp',
                    'no-rpm-opt-flags': 'use-rpm-opt-flags',
                    'rpm2-mode': 'rpm3-mode'}


    def initialize_options(self):
        self.bdist_base = Nic
        self.rpm_base = Nic
        self.dist_dir = Nic
        self.python = Nic
        self.fix_python = Nic
        self.spec_only = Nic
        self.binary_only = Nic
        self.source_only = Nic
        self.use_bzip2 = Nic

        self.distribution_name = Nic
        self.group = Nic
        self.release = Nic
        self.serial = Nic
        self.vendor = Nic
        self.packager = Nic
        self.doc_files = Nic
        self.changelog = Nic
        self.icon = Nic

        self.prep_script = Nic
        self.build_script = Nic
        self.install_script = Nic
        self.clean_script = Nic
        self.verify_script = Nic
        self.pre_install = Nic
        self.post_install = Nic
        self.pre_uninstall = Nic
        self.post_uninstall = Nic
        self.prep = Nic
        self.provides = Nic
        self.requires = Nic
        self.conflicts = Nic
        self.build_requires = Nic
        self.obsoletes = Nic

        self.keep_temp = 0
        self.use_rpm_opt_flags = 1
        self.rpm3_mode = 1
        self.no_autoreq = 0

        self.force_arch = Nic
        self.quiet = 0

    def finalize_options(self):
        self.set_undefined_options('bdist', ('bdist_base', 'bdist_base'))
        jeżeli self.rpm_base jest Nic:
            jeżeli nie self.rpm3_mode:
                podnieś DistutilsOptionError(
                      "you must specify --rpm-base w RPM 2 mode")
            self.rpm_base = os.path.join(self.bdist_base, "rpm")

        jeżeli self.python jest Nic:
            jeżeli self.fix_python:
                self.python = sys.executable
            inaczej:
                self.python = "python3"
        albo_inaczej self.fix_python:
            podnieś DistutilsOptionError(
                  "--python oraz --fix-python are mutually exclusive options")

        jeżeli os.name != 'posix':
            podnieś DistutilsPlatformError("don't know how to create RPM "
                   "distributions on platform %s" % os.name)
        jeżeli self.binary_only oraz self.source_only:
            podnieś DistutilsOptionError(
                  "cannot supply both '--source-only' oraz '--binary-only'")

        # don't dalej CFLAGS to pure python distributions
        jeżeli nie self.distribution.has_ext_modules():
            self.use_rpm_opt_flags = 0

        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))
        self.finalize_package_data()

    def finalize_package_data(self):
        self.ensure_string('group', "Development/Libraries")
        self.ensure_string('vendor',
                           "%s <%s>" % (self.distribution.get_contact(),
                                        self.distribution.get_contact_email()))
        self.ensure_string('packager')
        self.ensure_string_list('doc_files')
        jeżeli isinstance(self.doc_files, list):
            dla readme w ('README', 'README.txt'):
                jeżeli os.path.exists(readme) oraz readme nie w self.doc_files:
                    self.doc_files.append(readme)

        self.ensure_string('release', "1")
        self.ensure_string('serial')   # should it be an int?

        self.ensure_string('distribution_name')

        self.ensure_string('changelog')
          # Format changelog correctly
        self.changelog = self._format_changelog(self.changelog)

        self.ensure_filename('icon')

        self.ensure_filename('prep_script')
        self.ensure_filename('build_script')
        self.ensure_filename('install_script')
        self.ensure_filename('clean_script')
        self.ensure_filename('verify_script')
        self.ensure_filename('pre_install')
        self.ensure_filename('post_install')
        self.ensure_filename('pre_uninstall')
        self.ensure_filename('post_uninstall')

        # XXX don't forget we punted on summaries oraz descriptions -- they
        # should be handled here eventually!

        # Now *this* jest some meta-data that belongs w the setup script...
        self.ensure_string_list('provides')
        self.ensure_string_list('requires')
        self.ensure_string_list('conflicts')
        self.ensure_string_list('build_requires')
        self.ensure_string_list('obsoletes')

        self.ensure_string('force_arch')

    def run(self):
        jeżeli DEBUG:
            print("before _get_package_data():")
            print("vendor =", self.vendor)
            print("packager =", self.packager)
            print("doc_files =", self.doc_files)
            print("changelog =", self.changelog)

        # make directories
        jeżeli self.spec_only:
            spec_dir = self.dist_dir
            self.mkpath(spec_dir)
        inaczej:
            rpm_dir = {}
            dla d w ('SOURCES', 'SPECS', 'BUILD', 'RPMS', 'SRPMS'):
                rpm_dir[d] = os.path.join(self.rpm_base, d)
                self.mkpath(rpm_dir[d])
            spec_dir = rpm_dir['SPECS']

        # Spec file goes into 'dist_dir' jeżeli '--spec-only specified',
        # build/rpm.<plat> otherwise.
        spec_path = os.path.join(spec_dir,
                                 "%s.spec" % self.distribution.get_name())
        self.execute(write_file,
                     (spec_path,
                      self._make_spec_file()),
                     "writing '%s'" % spec_path)

        jeżeli self.spec_only: # stop jeżeli requested
            zwróć

        # Make a source distribution oraz copy to SOURCES directory with
        # optional icon.
        saved_dist_files = self.distribution.dist_files[:]
        sdist = self.reinitialize_command('sdist')
        jeżeli self.use_bzip2:
            sdist.formats = ['bztar']
        inaczej:
            sdist.formats = ['gztar']
        self.run_command('sdist')
        self.distribution.dist_files = saved_dist_files

        source = sdist.get_archive_files()[0]
        source_dir = rpm_dir['SOURCES']
        self.copy_file(source, source_dir)

        jeżeli self.icon:
            jeżeli os.path.exists(self.icon):
                self.copy_file(self.icon, source_dir)
            inaczej:
                podnieś DistutilsFileError(
                      "icon file '%s' does nie exist" % self.icon)

        # build package
        log.info("building RPMs")
        rpm_cmd = ['rpm']
        jeżeli os.path.exists('/usr/bin/rpmbuild') albo \
           os.path.exists('/bin/rpmbuild'):
            rpm_cmd = ['rpmbuild']

        jeżeli self.source_only: # what kind of RPMs?
            rpm_cmd.append('-bs')
        albo_inaczej self.binary_only:
            rpm_cmd.append('-bb')
        inaczej:
            rpm_cmd.append('-ba')
        rpm_cmd.extend(['--define', '__python %s' % self.python])
        jeżeli self.rpm3_mode:
            rpm_cmd.extend(['--define',
                             '_topdir %s' % os.path.abspath(self.rpm_base)])
        jeżeli nie self.keep_temp:
            rpm_cmd.append('--clean')

        jeżeli self.quiet:
            rpm_cmd.append('--quiet')

        rpm_cmd.append(spec_path)
        # Determine the binary rpm names that should be built out of this spec
        # file
        # Note that some of these may nie be really built (jeżeli the file
        # list jest empty)
        nvr_string = "%{name}-%{version}-%{release}"
        src_rpm = nvr_string + ".src.rpm"
        non_src_rpm = "%{arch}/" + nvr_string + ".%{arch}.rpm"
        q_cmd = r"rpm -q --qf '%s %s\n' --specfile '%s'" % (
            src_rpm, non_src_rpm, spec_path)

        out = os.popen(q_cmd)
        spróbuj:
            binary_rpms = []
            source_rpm = Nic
            dopóki Prawda:
                line = out.readline()
                jeżeli nie line:
                    przerwij
                l = line.strip().split()
                assert(len(l) == 2)
                binary_rpms.append(l[1])
                # The source rpm jest named after the first entry w the spec file
                jeżeli source_rpm jest Nic:
                    source_rpm = l[0]

            status = out.close()
            jeżeli status:
                podnieś DistutilsExecError("Failed to execute: %s" % repr(q_cmd))

        w_końcu:
            out.close()

        self.spawn(rpm_cmd)

        jeżeli nie self.dry_run:
            jeżeli self.distribution.has_ext_modules():
                pyversion = get_python_version()
            inaczej:
                pyversion = 'any'

            jeżeli nie self.binary_only:
                srpm = os.path.join(rpm_dir['SRPMS'], source_rpm)
                assert(os.path.exists(srpm))
                self.move_file(srpm, self.dist_dir)
                filename = os.path.join(self.dist_dir, source_rpm)
                self.distribution.dist_files.append(
                    ('bdist_rpm', pyversion, filename))

            jeżeli nie self.source_only:
                dla rpm w binary_rpms:
                    rpm = os.path.join(rpm_dir['RPMS'], rpm)
                    jeżeli os.path.exists(rpm):
                        self.move_file(rpm, self.dist_dir)
                        filename = os.path.join(self.dist_dir,
                                                os.path.basename(rpm))
                        self.distribution.dist_files.append(
                            ('bdist_rpm', pyversion, filename))

    def _dist_path(self, path):
        zwróć os.path.join(self.dist_dir, os.path.basename(path))

    def _make_spec_file(self):
        """Generate the text of an RPM spec file oraz zwróć it jako a
        list of strings (one per line).
        """
        # definitions oraz headers
        spec_file = [
            '%define name ' + self.distribution.get_name(),
            '%define version ' + self.distribution.get_version().replace('-','_'),
            '%define unmangled_version ' + self.distribution.get_version(),
            '%define release ' + self.release.replace('-','_'),
            '',
            'Summary: ' + self.distribution.get_description(),
            ]

        # Workaround dla #14443 which affects some RPM based systems such as
        # RHEL6 (and probably derivatives)
        vendor_hook = subprocess.getoutput('rpm --eval %{__os_install_post}')
        # Generate a potential replacement value dla __os_install_post (whilst
        # normalizing the whitespace to simplify the test dla whether the
        # invocation of brp-python-bytecompile dalejes w __python):
        vendor_hook = '\n'.join(['  %s \\' % line.strip()
                                 dla line w vendor_hook.splitlines()])
        problem = "brp-python-bytecompile \\\n"
        fixed = "brp-python-bytecompile %{__python} \\\n"
        fixed_hook = vendor_hook.replace(problem, fixed)
        jeżeli fixed_hook != vendor_hook:
            spec_file.append('# Workaround dla http://bugs.python.org/issue14443')
            spec_file.append('%define __os_install_post ' + fixed_hook + '\n')

        # put locale summaries into spec file
        # XXX nie supported dla now (hard to put a dictionary
        # w a config file -- arg!)
        #dla locale w self.summaries.keys():
        #    spec_file.append('Summary(%s): %s' % (locale,
        #                                          self.summaries[locale]))

        spec_file.extend([
            'Name: %{name}',
            'Version: %{version}',
            'Release: %{release}',])

        # XXX yuck! this filename jest available z the "sdist" command,
        # but only after it has run: oraz we create the spec file before
        # running "sdist", w case of --spec-only.
        jeżeli self.use_bzip2:
            spec_file.append('Source0: %{name}-%{unmangled_version}.tar.bz2')
        inaczej:
            spec_file.append('Source0: %{name}-%{unmangled_version}.tar.gz')

        spec_file.extend([
            'License: ' + self.distribution.get_license(),
            'Group: ' + self.group,
            'BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot',
            'Prefix: %{_prefix}', ])

        jeżeli nie self.force_arch:
            # noarch jeżeli no extension modules
            jeżeli nie self.distribution.has_ext_modules():
                spec_file.append('BuildArch: noarch')
        inaczej:
            spec_file.append( 'BuildArch: %s' % self.force_arch )

        dla field w ('Vendor',
                      'Packager',
                      'Provides',
                      'Requires',
                      'Conflicts',
                      'Obsoletes',
                      ):
            val = getattr(self, field.lower())
            jeżeli isinstance(val, list):
                spec_file.append('%s: %s' % (field, ' '.join(val)))
            albo_inaczej val jest nie Nic:
                spec_file.append('%s: %s' % (field, val))


        jeżeli self.distribution.get_url() != 'UNKNOWN':
            spec_file.append('Url: ' + self.distribution.get_url())

        jeżeli self.distribution_name:
            spec_file.append('Distribution: ' + self.distribution_name)

        jeżeli self.build_requires:
            spec_file.append('BuildRequires: ' +
                             ' '.join(self.build_requires))

        jeżeli self.icon:
            spec_file.append('Icon: ' + os.path.basename(self.icon))

        jeżeli self.no_autoreq:
            spec_file.append('AutoReq: 0')

        spec_file.extend([
            '',
            '%description',
            self.distribution.get_long_description()
            ])

        # put locale descriptions into spec file
        # XXX again, suppressed because config file syntax doesn't
        # easily support this ;-(
        #dla locale w self.descriptions.keys():
        #    spec_file.extend([
        #        '',
        #        '%description -l ' + locale,
        #        self.descriptions[locale],
        #        ])

        # rpm scripts
        # figure out default build script
        def_setup_call = "%s %s" % (self.python,os.path.basename(sys.argv[0]))
        def_build = "%s build" % def_setup_call
        jeżeli self.use_rpm_opt_flags:
            def_build = 'env CFLAGS="$RPM_OPT_FLAGS" ' + def_build

        # insert contents of files

        # XXX this jest kind of misleading: user-supplied options are files
        # that we open oraz interpolate into the spec file, but the defaults
        # are just text that we drop w as-is.  Hmmm.

        install_cmd = ('%s install -O1 --root=$RPM_BUILD_ROOT '
                       '--record=INSTALLED_FILES') % def_setup_call

        script_options = [
            ('prep', 'prep_script', "%setup -n %{name}-%{unmangled_version}"),
            ('build', 'build_script', def_build),
            ('install', 'install_script', install_cmd),
            ('clean', 'clean_script', "rm -rf $RPM_BUILD_ROOT"),
            ('verifyscript', 'verify_script', Nic),
            ('pre', 'pre_install', Nic),
            ('post', 'post_install', Nic),
            ('preun', 'pre_uninstall', Nic),
            ('postun', 'post_uninstall', Nic),
        ]

        dla (rpm_opt, attr, default) w script_options:
            # Insert contents of file referred to, jeżeli no file jest referred to
            # use 'default' jako contents of script
            val = getattr(self, attr)
            jeżeli val albo default:
                spec_file.extend([
                    '',
                    '%' + rpm_opt,])
                jeżeli val:
                    spec_file.extend(open(val, 'r').read().split('\n'))
                inaczej:
                    spec_file.append(default)


        # files section
        spec_file.extend([
            '',
            '%files -f INSTALLED_FILES',
            '%defattr(-,root,root)',
            ])

        jeżeli self.doc_files:
            spec_file.append('%doc ' + ' '.join(self.doc_files))

        jeżeli self.changelog:
            spec_file.extend([
                '',
                '%changelog',])
            spec_file.extend(self.changelog)

        zwróć spec_file

    def _format_changelog(self, changelog):
        """Format the changelog correctly oraz convert it to a list of strings
        """
        jeżeli nie changelog:
            zwróć changelog
        new_changelog = []
        dla line w changelog.strip().split('\n'):
            line = line.strip()
            jeżeli line[0] == '*':
                new_changelog.extend(['', line])
            albo_inaczej line[0] == '-':
                new_changelog.append(line)
            inaczej:
                new_changelog.append('  ' + line)

        # strip trailing newline inserted by first changelog entry
        jeżeli nie new_changelog[0]:
            usuń new_changelog[0]

        zwróć new_changelog
