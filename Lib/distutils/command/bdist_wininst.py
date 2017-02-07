"""distutils.command.bdist_wininst

Implements the Distutils 'bdist_wininst' command: create a windows installer
exe-program."""

zaimportuj sys, os
z distutils.core zaimportuj Command
z distutils.util zaimportuj get_platform
z distutils.dir_util zaimportuj create_tree, remove_tree
z distutils.errors zaimportuj *
z distutils.sysconfig zaimportuj get_python_version
z distutils zaimportuj log

klasa bdist_wininst(Command):

    description = "create an executable installer dla MS Windows"

    user_options = [('bdist-dir=', Nic,
                     "temporary directory dla creating the distribution"),
                    ('plat-name=', 'p',
                     "platform name to embed w generated filenames "
                     "(default: %s)" % get_platform()),
                    ('keep-temp', 'k',
                     "keep the pseudo-installation tree around after " +
                     "creating the distribution archive"),
                    ('target-version=', Nic,
                     "require a specific python version" +
                     " on the target system"),
                    ('no-target-compile', 'c',
                     "do nie compile .py to .pyc on the target system"),
                    ('no-target-optimize', 'o',
                     "do nie compile .py to .pyo (optimized)"
                     "on the target system"),
                    ('dist-dir=', 'd',
                     "directory to put final built distributions in"),
                    ('bitmap=', 'b',
                     "bitmap to use dla the installer instead of python-powered logo"),
                    ('title=', 't',
                     "title to display on the installer background instead of default"),
                    ('skip-build', Nic,
                     "skip rebuilding everything (dla testing/debugging)"),
                    ('install-script=', Nic,
                     "basename of installation script to be run after"
                     "installation albo before deinstallation"),
                    ('pre-install-script=', Nic,
                     "Fully qualified filename of a script to be run before "
                     "any files are installed.  This script need nie be w the "
                     "distribution"),
                    ('user-access-control=', Nic,
                     "specify Vista's UAC handling - 'none'/default=no "
                     "handling, 'auto'=use UAC jeżeli target Python installed dla "
                     "all users, 'force'=always use UAC"),
                   ]

    boolean_options = ['keep-temp', 'no-target-compile', 'no-target-optimize',
                       'skip-build']

    def initialize_options(self):
        self.bdist_dir = Nic
        self.plat_name = Nic
        self.keep_temp = 0
        self.no_target_compile = 0
        self.no_target_optimize = 0
        self.target_version = Nic
        self.dist_dir = Nic
        self.bitmap = Nic
        self.title = Nic
        self.skip_build = Nic
        self.install_script = Nic
        self.pre_install_script = Nic
        self.user_access_control = Nic


    def finalize_options(self):
        self.set_undefined_options('bdist', ('skip_build', 'skip_build'))

        jeżeli self.bdist_dir jest Nic:
            jeżeli self.skip_build oraz self.plat_name:
                # If build jest skipped oraz plat_name jest overridden, bdist will
                # nie see the correct 'plat_name' - so set that up manually.
                bdist = self.distribution.get_command_obj('bdist')
                bdist.plat_name = self.plat_name
                # next the command will be initialized using that name
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'wininst')

        jeżeli nie self.target_version:
            self.target_version = ""

        jeżeli nie self.skip_build oraz self.distribution.has_ext_modules():
            short_version = get_python_version()
            jeżeli self.target_version oraz self.target_version != short_version:
                podnieś DistutilsOptionError(
                      "target version can only be %s, albo the '--skip-build'" \
                      " option must be specified" % (short_version,))
            self.target_version = short_version

        self.set_undefined_options('bdist',
                                   ('dist_dir', 'dist_dir'),
                                   ('plat_name', 'plat_name'),
                                  )

        jeżeli self.install_script:
            dla script w self.distribution.scripts:
                jeżeli self.install_script == os.path.basename(script):
                    przerwij
            inaczej:
                podnieś DistutilsOptionError(
                      "install_script '%s' nie found w scripts"
                      % self.install_script)

    def run(self):
        jeżeli (sys.platform != "win32" oraz
            (self.distribution.has_ext_modules() albo
             self.distribution.has_c_libraries())):
            podnieś DistutilsPlatformError \
                  ("distribution contains extensions and/or C libraries; "
                   "must be compiled on a Windows 32 platform")

        jeżeli nie self.skip_build:
            self.run_command('build')

        install = self.reinitialize_command('install', reinit_subcommands=1)
        install.root = self.bdist_dir
        install.skip_build = self.skip_build
        install.warn_dir = 0
        install.plat_name = self.plat_name

        install_lib = self.reinitialize_command('install_lib')
        # we do nie want to include pyc albo pyo files
        install_lib.compile = 0
        install_lib.optimize = 0

        jeżeli self.distribution.has_ext_modules():
            # If we are building an installer dla a Python version other
            # than the one we are currently running, then we need to ensure
            # our build_lib reflects the other Python version rather than ours.
            # Note that dla target_version!=sys.version, we must have skipped the
            # build step, so there jest no issue przy enforcing the build of this
            # version.
            target_version = self.target_version
            jeżeli nie target_version:
                assert self.skip_build, "Should have already checked this"
                target_version = sys.version[0:3]
            plat_specifier = ".%s-%s" % (self.plat_name, target_version)
            build = self.get_finalized_command('build')
            build.build_lib = os.path.join(build.build_base,
                                           'lib' + plat_specifier)

        # Use a custom scheme dla the zip-file, because we have to decide
        # at installation time which scheme to use.
        dla key w ('purelib', 'platlib', 'headers', 'scripts', 'data'):
            value = key.upper()
            jeżeli key == 'headers':
                value = value + '/Include/$dist_name'
            setattr(install,
                    'install_' + key,
                    value)

        log.info("installing to %s", self.bdist_dir)
        install.ensure_finalized()

        # avoid warning of 'install_lib' about installing
        # into a directory nie w sys.path
        sys.path.insert(0, os.path.join(self.bdist_dir, 'PURELIB'))

        install.run()

        usuń sys.path[0]

        # And make an archive relative to the root of the
        # pseudo-installation tree.
        z tempfile zaimportuj mktemp
        archive_basename = mktemp()
        fullname = self.distribution.get_fullname()
        arcname = self.make_archive(archive_basename, "zip",
                                    root_dir=self.bdist_dir)
        # create an exe containing the zip-file
        self.create_exe(arcname, fullname, self.bitmap)
        jeżeli self.distribution.has_ext_modules():
            pyversion = get_python_version()
        inaczej:
            pyversion = 'any'
        self.distribution.dist_files.append(('bdist_wininst', pyversion,
                                             self.get_installer_filename(fullname)))
        # remove the zip-file again
        log.debug("removing temporary file '%s'", arcname)
        os.remove(arcname)

        jeżeli nie self.keep_temp:
            remove_tree(self.bdist_dir, dry_run=self.dry_run)

    def get_inidata(self):
        # Return data describing the installation.
        lines = []
        metadata = self.distribution.metadata

        # Write the [metadata] section.
        lines.append("[metadata]")

        # 'info' will be displayed w the installer's dialog box,
        # describing the items to be installed.
        info = (metadata.long_description albo '') + '\n'

        # Escape newline characters
        def escape(s):
            zwróć s.replace("\n", "\\n")

        dla name w ["author", "author_email", "description", "maintainer",
                     "maintainer_email", "name", "url", "version"]:
            data = getattr(metadata, name, "")
            jeżeli data:
                info = info + ("\n    %s: %s" % \
                               (name.capitalize(), escape(data)))
                lines.append("%s=%s" % (name, escape(data)))

        # The [setup] section contains entries controlling
        # the installer runtime.
        lines.append("\n[Setup]")
        jeżeli self.install_script:
            lines.append("install_script=%s" % self.install_script)
        lines.append("info=%s" % escape(info))
        lines.append("target_compile=%d" % (nie self.no_target_compile))
        lines.append("target_optimize=%d" % (nie self.no_target_optimize))
        jeżeli self.target_version:
            lines.append("target_version=%s" % self.target_version)
        jeżeli self.user_access_control:
            lines.append("user_access_control=%s" % self.user_access_control)

        title = self.title albo self.distribution.get_fullname()
        lines.append("title=%s" % escape(title))
        zaimportuj time
        zaimportuj distutils
        build_info = "Built %s przy distutils-%s" % \
                     (time.ctime(time.time()), distutils.__version__)
        lines.append("build_info=%s" % build_info)
        zwróć "\n".join(lines)

    def create_exe(self, arcname, fullname, bitmap=Nic):
        zaimportuj struct

        self.mkpath(self.dist_dir)

        cfgdata = self.get_inidata()

        installer_name = self.get_installer_filename(fullname)
        self.announce("creating %s" % installer_name)

        jeżeli bitmap:
            bitmapdata = open(bitmap, "rb").read()
            bitmaplen = len(bitmapdata)
        inaczej:
            bitmaplen = 0

        file = open(installer_name, "wb")
        file.write(self.get_exe_bytes())
        jeżeli bitmap:
            file.write(bitmapdata)

        # Convert cfgdata z unicode to ascii, mbcs encoded
        jeżeli isinstance(cfgdata, str):
            cfgdata = cfgdata.encode("mbcs")

        # Append the pre-install script
        cfgdata = cfgdata + b"\0"
        jeżeli self.pre_install_script:
            # We need to normalize newlines, so we open w text mode oraz
            # convert back to bytes. "latin-1" simply avoids any possible
            # failures.
            przy open(self.pre_install_script, "r",
                encoding="latin-1") jako script:
                script_data = script.read().encode("latin-1")
            cfgdata = cfgdata + script_data + b"\n\0"
        inaczej:
            # empty pre-install script
            cfgdata = cfgdata + b"\0"
        file.write(cfgdata)

        # The 'magic number' 0x1234567B jest used to make sure that the
        # binary layout of 'cfgdata' jest what the wininst.exe binary
        # expects.  If the layout changes, increment that number, make
        # the corresponding changes to the wininst.exe sources, oraz
        # recompile them.
        header = struct.pack("<iii",
                             0x1234567B,       # tag
                             len(cfgdata),     # length
                             bitmaplen,        # number of bytes w bitmap
                             )
        file.write(header)
        file.write(open(arcname, "rb").read())

    def get_installer_filename(self, fullname):
        # Factored out to allow overriding w subclasses
        jeżeli self.target_version:
            # jeżeli we create an installer dla a specific python version,
            # it's better to include this w the name
            installer_name = os.path.join(self.dist_dir,
                                          "%s.%s-py%s.exe" %
                                           (fullname, self.plat_name, self.target_version))
        inaczej:
            installer_name = os.path.join(self.dist_dir,
                                          "%s.%s.exe" % (fullname, self.plat_name))
        zwróć installer_name

    def get_exe_bytes(self):
        # If a target-version other than the current version has been
        # specified, then using the MSVC version z *this* build jest no good.
        # Without actually finding oraz executing the target version oraz parsing
        # its sys.version, we just hard-code our knowledge of old versions.
        # NOTE: Possible alternative jest to allow "--target-version" to
        # specify a Python executable rather than a simple version string.
        # We can then execute this program to obtain any info we need, such
        # jako the real sys.version string dla the build.
        cur_version = get_python_version()

        # If the target version jest *later* than us, then we assume they
        # use what we use
        # string compares seem wrong, but are what sysconfig.py itself uses
        jeżeli self.target_version oraz self.target_version < cur_version:
            jeżeli self.target_version < "2.4":
                bv = 6.0
            albo_inaczej self.target_version == "2.4":
                bv = 7.1
            albo_inaczej self.target_version == "2.5":
                bv = 8.0
            albo_inaczej self.target_version <= "3.2":
                bv = 9.0
            albo_inaczej self.target_version <= "3.4":
                bv = 10.0
            inaczej:
                bv = 14.0
        inaczej:
            # dla current version - use authoritative check.
            spróbuj:
                z msvcrt zaimportuj CRT_ASSEMBLY_VERSION
            wyjąwszy ImportError:
                # cross-building, so assume the latest version
                bv = 14.0
            inaczej:
                bv = float('.'.join(CRT_ASSEMBLY_VERSION.split('.', 2)[:2]))


        # wininst-x.y.exe jest w the same directory jako this file
        directory = os.path.dirname(__file__)
        # we must use a wininst-x.y.exe built przy the same C compiler
        # used dla python.  XXX What about mingw, borland, oraz so on?

        # jeżeli plat_name starts przy "win" but jest nie "win32"
        # we want to strip "win" oraz leave the rest (e.g. -amd64)
        # dla all other cases, we don't want any suffix
        jeżeli self.plat_name != 'win32' oraz self.plat_name[:3] == 'win':
            sfix = self.plat_name[3:]
        inaczej:
            sfix = ''

        filename = os.path.join(directory, "wininst-%.1f%s.exe" % (bv, sfix))
        f = open(filename, "rb")
        spróbuj:
            zwróć f.read()
        w_końcu:
            f.close()
