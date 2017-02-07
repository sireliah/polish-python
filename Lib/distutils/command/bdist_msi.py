# Copyright (C) 2005, 2006 Martin von Löwis
# Licensed to PSF under a Contributor Agreement.
# The bdist_wininst command proper
# based on bdist_wininst
"""
Implements the bdist_msi command.
"""

zaimportuj sys, os
z distutils.core zaimportuj Command
z distutils.dir_util zaimportuj remove_tree
z distutils.sysconfig zaimportuj get_python_version
z distutils.version zaimportuj StrictVersion
z distutils.errors zaimportuj DistutilsOptionError
z distutils.util zaimportuj get_platform
z distutils zaimportuj log
zaimportuj msilib
z msilib zaimportuj schema, sequence, text
z msilib zaimportuj Directory, Feature, Dialog, add_data

klasa PyDialog(Dialog):
    """Dialog klasa przy a fixed layout: controls at the top, then a ruler,
    then a list of buttons: back, next, cancel. Optionally a bitmap at the
    left."""
    def __init__(self, *args, **kw):
        """Dialog(database, name, x, y, w, h, attributes, title, first,
        default, cancel, bitmap=true)"""
        Dialog.__init__(self, *args)
        ruler = self.h - 36
        bmwidth = 152*ruler/328
        #jeżeli kw.get("bitmap", Prawda):
        #    self.bitmap("Bitmap", 0, 0, bmwidth, ruler, "PythonWin")
        self.line("BottomLine", 0, ruler, self.w, 0)

    def title(self, title):
        "Set the title text of the dialog at the top."
        # name, x, y, w, h, flags=Visible|Enabled|Transparent|NoPrefix,
        # text, w VerdanaBold10
        self.text("Title", 15, 10, 320, 60, 0x30003,
                  r"{\VerdanaBold10}%s" % title)

    def back(self, title, next, name = "Back", active = 1):
        """Add a back button przy a given title, the tab-next button,
        its name w the Control table, possibly initially disabled.

        Return the button, so that events can be associated"""
        jeżeli active:
            flags = 3 # Visible|Enabled
        inaczej:
            flags = 1 # Visible
        zwróć self.pushbutton(name, 180, self.h-27 , 56, 17, flags, title, next)

    def cancel(self, title, next, name = "Cancel", active = 1):
        """Add a cancel button przy a given title, the tab-next button,
        its name w the Control table, possibly initially disabled.

        Return the button, so that events can be associated"""
        jeżeli active:
            flags = 3 # Visible|Enabled
        inaczej:
            flags = 1 # Visible
        zwróć self.pushbutton(name, 304, self.h-27, 56, 17, flags, title, next)

    def next(self, title, next, name = "Next", active = 1):
        """Add a Next button przy a given title, the tab-next button,
        its name w the Control table, possibly initially disabled.

        Return the button, so that events can be associated"""
        jeżeli active:
            flags = 3 # Visible|Enabled
        inaczej:
            flags = 1 # Visible
        zwróć self.pushbutton(name, 236, self.h-27, 56, 17, flags, title, next)

    def xbutton(self, name, title, next, xpos):
        """Add a button przy a given title, the tab-next button,
        its name w the Control table, giving its x position; the
        y-position jest aligned przy the other buttons.

        Return the button, so that events can be associated"""
        zwróć self.pushbutton(name, int(self.w*xpos - 28), self.h-27, 56, 17, 3, title, next)

klasa bdist_msi(Command):

    description = "create a Microsoft Installer (.msi) binary distribution"

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
                    ('skip-build', Nic,
                     "skip rebuilding everything (dla testing/debugging)"),
                    ('install-script=', Nic,
                     "basename of installation script to be run after"
                     "installation albo before deinstallation"),
                    ('pre-install-script=', Nic,
                     "Fully qualified filename of a script to be run before "
                     "any files are installed.  This script need nie be w the "
                     "distribution"),
                   ]

    boolean_options = ['keep-temp', 'no-target-compile', 'no-target-optimize',
                       'skip-build']

    all_versions = ['2.0', '2.1', '2.2', '2.3', '2.4',
                    '2.5', '2.6', '2.7', '2.8', '2.9',
                    '3.0', '3.1', '3.2', '3.3', '3.4',
                    '3.5', '3.6', '3.7', '3.8', '3.9']
    other_version = 'X'

    def initialize_options(self):
        self.bdist_dir = Nic
        self.plat_name = Nic
        self.keep_temp = 0
        self.no_target_compile = 0
        self.no_target_optimize = 0
        self.target_version = Nic
        self.dist_dir = Nic
        self.skip_build = Nic
        self.install_script = Nic
        self.pre_install_script = Nic
        self.versions = Nic

    def finalize_options(self):
        self.set_undefined_options('bdist', ('skip_build', 'skip_build'))

        jeżeli self.bdist_dir jest Nic:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'msi')

        short_version = get_python_version()
        jeżeli (nie self.target_version) oraz self.distribution.has_ext_modules():
            self.target_version = short_version

        jeżeli self.target_version:
            self.versions = [self.target_version]
            jeżeli nie self.skip_build oraz self.distribution.has_ext_modules()\
               oraz self.target_version != short_version:
                podnieś DistutilsOptionError(
                      "target version can only be %s, albo the '--skip-build'"
                      " option must be specified" % (short_version,))
        inaczej:
            self.versions = list(self.all_versions)

        self.set_undefined_options('bdist',
                                   ('dist_dir', 'dist_dir'),
                                   ('plat_name', 'plat_name'),
                                   )

        jeżeli self.pre_install_script:
            podnieś DistutilsOptionError(
                  "the pre-install-script feature jest nie yet implemented")

        jeżeli self.install_script:
            dla script w self.distribution.scripts:
                jeżeli self.install_script == os.path.basename(script):
                    przerwij
            inaczej:
                podnieś DistutilsOptionError(
                      "install_script '%s' nie found w scripts"
                      % self.install_script)
        self.install_script_key = Nic

    def run(self):
        jeżeli nie self.skip_build:
            self.run_command('build')

        install = self.reinitialize_command('install', reinit_subcommands=1)
        install.prefix = self.bdist_dir
        install.skip_build = self.skip_build
        install.warn_dir = 0

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

        log.info("installing to %s", self.bdist_dir)
        install.ensure_finalized()

        # avoid warning of 'install_lib' about installing
        # into a directory nie w sys.path
        sys.path.insert(0, os.path.join(self.bdist_dir, 'PURELIB'))

        install.run()

        usuń sys.path[0]

        self.mkpath(self.dist_dir)
        fullname = self.distribution.get_fullname()
        installer_name = self.get_installer_filename(fullname)
        installer_name = os.path.abspath(installer_name)
        jeżeli os.path.exists(installer_name): os.unlink(installer_name)

        metadata = self.distribution.metadata
        author = metadata.author
        jeżeli nie author:
            author = metadata.maintainer
        jeżeli nie author:
            author = "UNKNOWN"
        version = metadata.get_version()
        # ProductVersion must be strictly numeric
        # XXX need to deal przy prerelease versions
        sversion = "%d.%d.%d" % StrictVersion(version).version
        # Prefix ProductName przy Python x.y, so that
        # it sorts together przy the other Python packages
        # w Add-Remove-Programs (APR)
        fullname = self.distribution.get_fullname()
        jeżeli self.target_version:
            product_name = "Python %s %s" % (self.target_version, fullname)
        inaczej:
            product_name = "Python %s" % (fullname)
        self.db = msilib.init_database(installer_name, schema,
                product_name, msilib.gen_uuid(),
                sversion, author)
        msilib.add_tables(self.db, sequence)
        props = [('DistVersion', version)]
        email = metadata.author_email albo metadata.maintainer_email
        jeżeli email:
            props.append(("ARPCONTACT", email))
        jeżeli metadata.url:
            props.append(("ARPURLINFOABOUT", metadata.url))
        jeżeli props:
            add_data(self.db, 'Property', props)

        self.add_find_python()
        self.add_files()
        self.add_scripts()
        self.add_ui()
        self.db.Commit()

        jeżeli hasattr(self.distribution, 'dist_files'):
            tup = 'bdist_msi', self.target_version albo 'any', fullname
            self.distribution.dist_files.append(tup)

        jeżeli nie self.keep_temp:
            remove_tree(self.bdist_dir, dry_run=self.dry_run)

    def add_files(self):
        db = self.db
        cab = msilib.CAB("distfiles")
        rootdir = os.path.abspath(self.bdist_dir)

        root = Directory(db, cab, Nic, rootdir, "TARGETDIR", "SourceDir")
        f = Feature(db, "Python", "Python", "Everything",
                    0, 1, directory="TARGETDIR")

        items = [(f, root, '')]
        dla version w self.versions + [self.other_version]:
            target = "TARGETDIR" + version
            name = default = "Python" + version
            desc = "Everything"
            jeżeli version jest self.other_version:
                title = "Python z another location"
                level = 2
            inaczej:
                title = "Python %s z registry" % version
                level = 1
            f = Feature(db, name, title, desc, 1, level, directory=target)
            dir = Directory(db, cab, root, rootdir, target, default)
            items.append((f, dir, version))
        db.Commit()

        seen = {}
        dla feature, dir, version w items:
            todo = [dir]
            dopóki todo:
                dir = todo.pop()
                dla file w os.listdir(dir.absolute):
                    afile = os.path.join(dir.absolute, file)
                    jeżeli os.path.isdir(afile):
                        short = "%s|%s" % (dir.make_short(file), file)
                        default = file + version
                        newdir = Directory(db, cab, dir, file, default, short)
                        todo.append(newdir)
                    inaczej:
                        jeżeli nie dir.component:
                            dir.start_component(dir.logical, feature, 0)
                        jeżeli afile nie w seen:
                            key = seen[afile] = dir.add_file(file)
                            jeżeli file==self.install_script:
                                jeżeli self.install_script_key:
                                    podnieś DistutilsOptionError(
                                          "Multiple files przy name %s" % file)
                                self.install_script_key = '[#%s]' % key
                        inaczej:
                            key = seen[afile]
                            add_data(self.db, "DuplicateFile",
                                [(key + version, dir.component, key, Nic, dir.logical)])
            db.Commit()
        cab.commit(db)

    def add_find_python(self):
        """Adds code to the installer to compute the location of Python.

        Properties PYTHON.MACHINE.X.Y oraz PYTHON.USER.X.Y will be set z the
        registry dla each version of Python.

        Properties TARGETDIRX.Y will be set z PYTHON.USER.X.Y jeżeli defined,
        inaczej z PYTHON.MACHINE.X.Y.

        Properties PYTHONX.Y will be set to TARGETDIRX.Y\\python.exe"""

        start = 402
        dla ver w self.versions:
            install_path = r"SOFTWARE\Python\PythonCore\%s\InstallPath" % ver
            machine_reg = "python.machine." + ver
            user_reg = "python.user." + ver
            machine_prop = "PYTHON.MACHINE." + ver
            user_prop = "PYTHON.USER." + ver
            machine_action = "PythonFromMachine" + ver
            user_action = "PythonFromUser" + ver
            exe_action = "PythonExe" + ver
            target_dir_prop = "TARGETDIR" + ver
            exe_prop = "PYTHON" + ver
            jeżeli msilib.Win64:
                # type: msidbLocatorTypeRawValue + msidbLocatorType64bit
                Type = 2+16
            inaczej:
                Type = 2
            add_data(self.db, "RegLocator",
                    [(machine_reg, 2, install_path, Nic, Type),
                     (user_reg, 1, install_path, Nic, Type)])
            add_data(self.db, "AppSearch",
                    [(machine_prop, machine_reg),
                     (user_prop, user_reg)])
            add_data(self.db, "CustomAction",
                    [(machine_action, 51+256, target_dir_prop, "[" + machine_prop + "]"),
                     (user_action, 51+256, target_dir_prop, "[" + user_prop + "]"),
                     (exe_action, 51+256, exe_prop, "[" + target_dir_prop + "]\\python.exe"),
                    ])
            add_data(self.db, "InstallExecuteSequence",
                    [(machine_action, machine_prop, start),
                     (user_action, user_prop, start + 1),
                     (exe_action, Nic, start + 2),
                    ])
            add_data(self.db, "InstallUISequence",
                    [(machine_action, machine_prop, start),
                     (user_action, user_prop, start + 1),
                     (exe_action, Nic, start + 2),
                    ])
            add_data(self.db, "Condition",
                    [("Python" + ver, 0, "NOT TARGETDIR" + ver)])
            start += 4
            assert start < 500

    def add_scripts(self):
        jeżeli self.install_script:
            start = 6800
            dla ver w self.versions + [self.other_version]:
                install_action = "install_script." + ver
                exe_prop = "PYTHON" + ver
                add_data(self.db, "CustomAction",
                        [(install_action, 50, exe_prop, self.install_script_key)])
                add_data(self.db, "InstallExecuteSequence",
                        [(install_action, "&Python%s=3" % ver, start)])
                start += 1
        # XXX pre-install scripts are currently refused w finalize_options()
        #     but jeżeli this feature jest completed, it will also need to add
        #     entries dla each version jako the above code does
        jeżeli self.pre_install_script:
            scriptfn = os.path.join(self.bdist_dir, "preinstall.bat")
            f = open(scriptfn, "w")
            # The batch file will be executed przy [PYTHON], so that %1
            # jest the path to the Python interpreter; %0 will be the path
            # of the batch file.
            # rem ="""
            # %1 %0
            # exit
            # """
            # <actual script>
            f.write('rem ="""\n%1 %0\nexit\n"""\n')
            f.write(open(self.pre_install_script).read())
            f.close()
            add_data(self.db, "Binary",
                [("PreInstall", msilib.Binary(scriptfn))
                ])
            add_data(self.db, "CustomAction",
                [("PreInstall", 2, "PreInstall", Nic)
                ])
            add_data(self.db, "InstallExecuteSequence",
                    [("PreInstall", "NOT Installed", 450)])


    def add_ui(self):
        db = self.db
        x = y = 50
        w = 370
        h = 300
        title = "[ProductName] Setup"

        # see "Dialog Style Bits"
        modal = 3      # visible | modal
        modeless = 1   # visible
        track_disk_space = 32

        # UI customization properties
        add_data(db, "Property",
                 # See "DefaultUIFont Property"
                 [("DefaultUIFont", "DlgFont8"),
                  # See "ErrorDialog Style Bit"
                  ("ErrorDialog", "ErrorDlg"),
                  ("Progress1", "Install"),   # modified w maintenance type dlg
                  ("Progress2", "installs"),
                  ("MaintenanceForm_Action", "Repair"),
                  # possible values: ALL, JUSTME
                  ("WhichUsers", "ALL")
                 ])

        # Fonts, see "TextStyle Table"
        add_data(db, "TextStyle",
                 [("DlgFont8", "Tahoma", 9, Nic, 0),
                  ("DlgFontBold8", "Tahoma", 8, Nic, 1), #bold
                  ("VerdanaBold10", "Verdana", 10, Nic, 1),
                  ("VerdanaRed9", "Verdana", 9, 255, 0),
                 ])

        # UI Sequences, see "InstallUISequence Table", "Using a Sequence Table"
        # Numbers indicate sequence; see sequence.py dla how these action integrate
        add_data(db, "InstallUISequence",
                 [("PrepareDlg", "Not Privileged albo Windows9x albo Installed", 140),
                  ("WhichUsersDlg", "Privileged oraz nie Windows9x oraz nie Installed", 141),
                  # In the user interface, assume all-users installation jeżeli privileged.
                  ("SelectFeaturesDlg", "Not Installed", 1230),
                  # XXX no support dla resume installations yet
                  #("ResumeDlg", "Installed AND (RESUME OR Preselected)", 1240),
                  ("MaintenanceTypeDlg", "Installed AND NOT RESUME AND NOT Preselected", 1250),
                  ("ProgressDlg", Nic, 1280)])

        add_data(db, 'ActionText', text.ActionText)
        add_data(db, 'UIText', text.UIText)
        #####################################################################
        # Standard dialogs: FatalError, UserExit, ExitDialog
        fatal=PyDialog(db, "FatalError", x, y, w, h, modal, title,
                     "Finish", "Finish", "Finish")
        fatal.title("[ProductName] Installer ended prematurely")
        fatal.back("< Back", "Finish", active = 0)
        fatal.cancel("Cancel", "Back", active = 0)
        fatal.text("Description1", 15, 70, 320, 80, 0x30003,
                   "[ProductName] setup ended prematurely because of an error.  Your system has nie been modified.  To install this program at a later time, please run the installation again.")
        fatal.text("Description2", 15, 155, 320, 20, 0x30003,
                   "Click the Finish button to exit the Installer.")
        c=fatal.next("Finish", "Cancel", name="Finish")
        c.event("EndDialog", "Exit")

        user_exit=PyDialog(db, "UserExit", x, y, w, h, modal, title,
                     "Finish", "Finish", "Finish")
        user_exit.title("[ProductName] Installer was interrupted")
        user_exit.back("< Back", "Finish", active = 0)
        user_exit.cancel("Cancel", "Back", active = 0)
        user_exit.text("Description1", 15, 70, 320, 80, 0x30003,
                   "[ProductName] setup was interrupted.  Your system has nie been modified.  "
                   "To install this program at a later time, please run the installation again.")
        user_exit.text("Description2", 15, 155, 320, 20, 0x30003,
                   "Click the Finish button to exit the Installer.")
        c = user_exit.next("Finish", "Cancel", name="Finish")
        c.event("EndDialog", "Exit")

        exit_dialog = PyDialog(db, "ExitDialog", x, y, w, h, modal, title,
                             "Finish", "Finish", "Finish")
        exit_dialog.title("Completing the [ProductName] Installer")
        exit_dialog.back("< Back", "Finish", active = 0)
        exit_dialog.cancel("Cancel", "Back", active = 0)
        exit_dialog.text("Description", 15, 235, 320, 20, 0x30003,
                   "Click the Finish button to exit the Installer.")
        c = exit_dialog.next("Finish", "Cancel", name="Finish")
        c.event("EndDialog", "Return")

        #####################################################################
        # Required dialog: FilesInUse, ErrorDlg
        inuse = PyDialog(db, "FilesInUse",
                         x, y, w, h,
                         19,                # KeepModeless|Modal|Visible
                         title,
                         "Retry", "Retry", "Retry", bitmap=Nieprawda)
        inuse.text("Title", 15, 6, 200, 15, 0x30003,
                   r"{\DlgFontBold8}Files w Use")
        inuse.text("Description", 20, 23, 280, 20, 0x30003,
               "Some files that need to be updated are currently w use.")
        inuse.text("Text", 20, 55, 330, 50, 3,
                   "The following applications are using files that need to be updated by this setup. Close these applications oraz then click Retry to continue the installation albo Cancel to exit it.")
        inuse.control("List", "ListBox", 20, 107, 330, 130, 7, "FileInUseProcess",
                      Nic, Nic, Nic)
        c=inuse.back("Exit", "Ignore", name="Exit")
        c.event("EndDialog", "Exit")
        c=inuse.next("Ignore", "Retry", name="Ignore")
        c.event("EndDialog", "Ignore")
        c=inuse.cancel("Retry", "Exit", name="Retry")
        c.event("EndDialog","Retry")

        # See "Error Dialog". See "ICE20" dla the required names of the controls.
        error = Dialog(db, "ErrorDlg",
                       50, 10, 330, 101,
                       65543,       # Error|Minimize|Modal|Visible
                       title,
                       "ErrorText", Nic, Nic)
        error.text("ErrorText", 50,9,280,48,3, "")
        #error.control("ErrorIcon", "Icon", 15, 9, 24, 24, 5242881, Nic, "py.ico", Nic, Nic)
        error.pushbutton("N",120,72,81,21,3,"No",Nic).event("EndDialog","ErrorNo")
        error.pushbutton("Y",240,72,81,21,3,"Yes",Nic).event("EndDialog","ErrorYes")
        error.pushbutton("A",0,72,81,21,3,"Abort",Nic).event("EndDialog","ErrorAbort")
        error.pushbutton("C",42,72,81,21,3,"Cancel",Nic).event("EndDialog","ErrorCancel")
        error.pushbutton("I",81,72,81,21,3,"Ignore",Nic).event("EndDialog","ErrorIgnore")
        error.pushbutton("O",159,72,81,21,3,"Ok",Nic).event("EndDialog","ErrorOk")
        error.pushbutton("R",198,72,81,21,3,"Retry",Nic).event("EndDialog","ErrorRetry")

        #####################################################################
        # Global "Query Cancel" dialog
        cancel = Dialog(db, "CancelDlg", 50, 10, 260, 85, 3, title,
                        "No", "No", "No")
        cancel.text("Text", 48, 15, 194, 30, 3,
                    "Are you sure you want to cancel [ProductName] installation?")
        #cancel.control("Icon", "Icon", 15, 15, 24, 24, 5242881, Nic,
        #               "py.ico", Nic, Nic)
        c=cancel.pushbutton("Yes", 72, 57, 56, 17, 3, "Yes", "No")
        c.event("EndDialog", "Exit")

        c=cancel.pushbutton("No", 132, 57, 56, 17, 3, "No", "Yes")
        c.event("EndDialog", "Return")

        #####################################################################
        # Global "Wait dla costing" dialog
        costing = Dialog(db, "WaitForCostingDlg", 50, 10, 260, 85, modal, title,
                         "Return", "Return", "Return")
        costing.text("Text", 48, 15, 194, 30, 3,
                     "Please wait dopóki the installer finishes determining your disk space requirements.")
        c = costing.pushbutton("Return", 102, 57, 56, 17, 3, "Return", Nic)
        c.event("EndDialog", "Exit")

        #####################################################################
        # Preparation dialog: no user input wyjąwszy cancellation
        prep = PyDialog(db, "PrepareDlg", x, y, w, h, modeless, title,
                        "Cancel", "Cancel", "Cancel")
        prep.text("Description", 15, 70, 320, 40, 0x30003,
                  "Please wait dopóki the Installer prepares to guide you through the installation.")
        prep.title("Welcome to the [ProductName] Installer")
        c=prep.text("ActionText", 15, 110, 320, 20, 0x30003, "Pondering...")
        c.mapping("ActionText", "Text")
        c=prep.text("ActionData", 15, 135, 320, 30, 0x30003, Nic)
        c.mapping("ActionData", "Text")
        prep.back("Back", Nic, active=0)
        prep.next("Next", Nic, active=0)
        c=prep.cancel("Cancel", Nic)
        c.event("SpawnDialog", "CancelDlg")

        #####################################################################
        # Feature (Python directory) selection
        seldlg = PyDialog(db, "SelectFeaturesDlg", x, y, w, h, modal, title,
                        "Next", "Next", "Cancel")
        seldlg.title("Select Python Installations")

        seldlg.text("Hint", 15, 30, 300, 20, 3,
                    "Select the Python locations where %s should be installed."
                    % self.distribution.get_fullname())

        seldlg.back("< Back", Nic, active=0)
        c = seldlg.next("Next >", "Cancel")
        order = 1
        c.event("[TARGETDIR]", "[SourceDir]", ordering=order)
        dla version w self.versions + [self.other_version]:
            order += 1
            c.event("[TARGETDIR]", "[TARGETDIR%s]" % version,
                    "FEATURE_SELECTED AND &Python%s=3" % version,
                    ordering=order)
        c.event("SpawnWaitDialog", "WaitForCostingDlg", ordering=order + 1)
        c.event("EndDialog", "Return", ordering=order + 2)
        c = seldlg.cancel("Cancel", "Features")
        c.event("SpawnDialog", "CancelDlg")

        c = seldlg.control("Features", "SelectionTree", 15, 60, 300, 120, 3,
                           "FEATURE", Nic, "PathEdit", Nic)
        c.event("[FEATURE_SELECTED]", "1")
        ver = self.other_version
        install_other_cond = "FEATURE_SELECTED AND &Python%s=3" % ver
        dont_install_other_cond = "FEATURE_SELECTED AND &Python%s<>3" % ver

        c = seldlg.text("Other", 15, 200, 300, 15, 3,
                        "Provide an alternate Python location")
        c.condition("Enable", install_other_cond)
        c.condition("Show", install_other_cond)
        c.condition("Disable", dont_install_other_cond)
        c.condition("Hide", dont_install_other_cond)

        c = seldlg.control("PathEdit", "PathEdit", 15, 215, 300, 16, 1,
                           "TARGETDIR" + ver, Nic, "Next", Nic)
        c.condition("Enable", install_other_cond)
        c.condition("Show", install_other_cond)
        c.condition("Disable", dont_install_other_cond)
        c.condition("Hide", dont_install_other_cond)

        #####################################################################
        # Disk cost
        cost = PyDialog(db, "DiskCostDlg", x, y, w, h, modal, title,
                        "OK", "OK", "OK", bitmap=Nieprawda)
        cost.text("Title", 15, 6, 200, 15, 0x30003,
                  "{\DlgFontBold8}Disk Space Requirements")
        cost.text("Description", 20, 20, 280, 20, 0x30003,
                  "The disk space required dla the installation of the selected features.")
        cost.text("Text", 20, 53, 330, 60, 3,
                  "The highlighted volumes (jeżeli any) do nie have enough disk space "
              "available dla the currently selected features.  You can either "
              "remove some files z the highlighted volumes, albo choose to "
              "install less features onto local drive(s), albo select different "
              "destination drive(s).")
        cost.control("VolumeList", "VolumeCostList", 20, 100, 330, 150, 393223,
                     Nic, "{120}{70}{70}{70}{70}", Nic, Nic)
        cost.xbutton("OK", "Ok", Nic, 0.5).event("EndDialog", "Return")

        #####################################################################
        # WhichUsers Dialog. Only available on NT, oraz dla privileged users.
        # This must be run before FindRelatedProducts, because that will
        # take into account whether the previous installation was per-user
        # albo per-machine. We currently don't support going back to this
        # dialog after "Next" was selected; to support this, we would need to
        # find how to reset the ALLUSERS property, oraz how to re-run
        # FindRelatedProducts.
        # On Windows9x, the ALLUSERS property jest ignored on the command line
        # oraz w the Property table, but installer fails according to the documentation
        # jeżeli a dialog attempts to set ALLUSERS.
        whichusers = PyDialog(db, "WhichUsersDlg", x, y, w, h, modal, title,
                            "AdminInstall", "Next", "Cancel")
        whichusers.title("Select whether to install [ProductName] dla all users of this computer.")
        # A radio group przy two options: allusers, justme
        g = whichusers.radiogroup("AdminInstall", 15, 60, 260, 50, 3,
                                  "WhichUsers", "", "Next")
        g.add("ALL", 0, 5, 150, 20, "Install dla all users")
        g.add("JUSTME", 0, 25, 150, 20, "Install just dla me")

        whichusers.back("Back", Nic, active=0)

        c = whichusers.next("Next >", "Cancel")
        c.event("[ALLUSERS]", "1", 'WhichUsers="ALL"', 1)
        c.event("EndDialog", "Return", ordering = 2)

        c = whichusers.cancel("Cancel", "AdminInstall")
        c.event("SpawnDialog", "CancelDlg")

        #####################################################################
        # Installation Progress dialog (modeless)
        progress = PyDialog(db, "ProgressDlg", x, y, w, h, modeless, title,
                            "Cancel", "Cancel", "Cancel", bitmap=Nieprawda)
        progress.text("Title", 20, 15, 200, 15, 0x30003,
                      "{\DlgFontBold8}[Progress1] [ProductName]")
        progress.text("Text", 35, 65, 300, 30, 3,
                      "Please wait dopóki the Installer [Progress2] [ProductName]. "
                      "This may take several minutes.")
        progress.text("StatusLabel", 35, 100, 35, 20, 3, "Status:")

        c=progress.text("ActionText", 70, 100, w-70, 20, 3, "Pondering...")
        c.mapping("ActionText", "Text")

        #c=progress.text("ActionData", 35, 140, 300, 20, 3, Nic)
        #c.mapping("ActionData", "Text")

        c=progress.control("ProgressBar", "ProgressBar", 35, 120, 300, 10, 65537,
                           Nic, "Progress done", Nic, Nic)
        c.mapping("SetProgress", "Progress")

        progress.back("< Back", "Next", active=Nieprawda)
        progress.next("Next >", "Cancel", active=Nieprawda)
        progress.cancel("Cancel", "Back").event("SpawnDialog", "CancelDlg")

        ###################################################################
        # Maintenance type: repair/uninstall
        maint = PyDialog(db, "MaintenanceTypeDlg", x, y, w, h, modal, title,
                         "Next", "Next", "Cancel")
        maint.title("Welcome to the [ProductName] Setup Wizard")
        maint.text("BodyText", 15, 63, 330, 42, 3,
                   "Select whether you want to repair albo remove [ProductName].")
        g=maint.radiogroup("RepairRadioGroup", 15, 108, 330, 60, 3,
                            "MaintenanceForm_Action", "", "Next")
        #g.add("Change", 0, 0, 200, 17, "&Change [ProductName]")
        g.add("Repair", 0, 18, 200, 17, "&Repair [ProductName]")
        g.add("Remove", 0, 36, 200, 17, "Re&move [ProductName]")

        maint.back("< Back", Nic, active=Nieprawda)
        c=maint.next("Finish", "Cancel")
        # Change installation: Change progress dialog to "Change", then ask
        # dla feature selection
        #c.event("[Progress1]", "Change", 'MaintenanceForm_Action="Change"', 1)
        #c.event("[Progress2]", "changes", 'MaintenanceForm_Action="Change"', 2)

        # Reinstall: Change progress dialog to "Repair", then invoke reinstall
        # Also set list of reinstalled features to "ALL"
        c.event("[REINSTALL]", "ALL", 'MaintenanceForm_Action="Repair"', 5)
        c.event("[Progress1]", "Repairing", 'MaintenanceForm_Action="Repair"', 6)
        c.event("[Progress2]", "repairs", 'MaintenanceForm_Action="Repair"', 7)
        c.event("Reinstall", "ALL", 'MaintenanceForm_Action="Repair"', 8)

        # Uninstall: Change progress to "Remove", then invoke uninstall
        # Also set list of removed features to "ALL"
        c.event("[REMOVE]", "ALL", 'MaintenanceForm_Action="Remove"', 11)
        c.event("[Progress1]", "Removing", 'MaintenanceForm_Action="Remove"', 12)
        c.event("[Progress2]", "removes", 'MaintenanceForm_Action="Remove"', 13)
        c.event("Remove", "ALL", 'MaintenanceForm_Action="Remove"', 14)

        # Close dialog when maintenance action scheduled
        c.event("EndDialog", "Return", 'MaintenanceForm_Action<>"Change"', 20)
        #c.event("NewDialog", "SelectFeaturesDlg", 'MaintenanceForm_Action="Change"', 21)

        maint.cancel("Cancel", "RepairRadioGroup").event("SpawnDialog", "CancelDlg")

    def get_installer_filename(self, fullname):
        # Factored out to allow overriding w subclasses
        jeżeli self.target_version:
            base_name = "%s.%s-py%s.msi" % (fullname, self.plat_name,
                                            self.target_version)
        inaczej:
            base_name = "%s.%s.msi" % (fullname, self.plat_name)
        installer_name = os.path.join(self.dist_dir, base_name)
        zwróć installer_name
