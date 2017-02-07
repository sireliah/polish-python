"""Tests dla distutils.command.install."""

zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj site

z test.support zaimportuj captured_stdout, run_unittest

z distutils zaimportuj sysconfig
z distutils.command.install zaimportuj install
z distutils.command zaimportuj install jako install_module
z distutils.command.build_ext zaimportuj build_ext
z distutils.command.install zaimportuj INSTALL_SCHEMES
z distutils.core zaimportuj Distribution
z distutils.errors zaimportuj DistutilsOptionError
z distutils.extension zaimportuj Extension

z distutils.tests zaimportuj support


def _make_ext_name(modname):
    zwróć modname + sysconfig.get_config_var('EXT_SUFFIX')


klasa InstallTestCase(support.TempdirManager,
                      support.EnvironGuard,
                      support.LoggingSilencer,
                      unittest.TestCase):

    def test_home_installation_scheme(self):
        # This ensure two things:
        # - that --home generates the desired set of directory names
        # - test --home jest supported on all platforms
        builddir = self.mkdtemp()
        destination = os.path.join(builddir, "installation")

        dist = Distribution({"name": "foopkg"})
        # script_name need nie exist, it just need to be initialized
        dist.script_name = os.path.join(builddir, "setup.py")
        dist.command_obj["build"] = support.DummyCommand(
            build_base=builddir,
            build_lib=os.path.join(builddir, "lib"),
            )

        cmd = install(dist)
        cmd.home = destination
        cmd.ensure_finalized()

        self.assertEqual(cmd.install_base, destination)
        self.assertEqual(cmd.install_platbase, destination)

        def check_path(got, expected):
            got = os.path.normpath(got)
            expected = os.path.normpath(expected)
            self.assertEqual(got, expected)

        libdir = os.path.join(destination, "lib", "python")
        check_path(cmd.install_lib, libdir)
        check_path(cmd.install_platlib, libdir)
        check_path(cmd.install_purelib, libdir)
        check_path(cmd.install_headers,
                   os.path.join(destination, "include", "python", "foopkg"))
        check_path(cmd.install_scripts, os.path.join(destination, "bin"))
        check_path(cmd.install_data, destination)

    def test_user_site(self):
        # test install przy --user
        # preparing the environment dla the test
        self.old_user_base = site.USER_BASE
        self.old_user_site = site.USER_SITE
        self.tmpdir = self.mkdtemp()
        self.user_base = os.path.join(self.tmpdir, 'B')
        self.user_site = os.path.join(self.tmpdir, 'S')
        site.USER_BASE = self.user_base
        site.USER_SITE = self.user_site
        install_module.USER_BASE = self.user_base
        install_module.USER_SITE = self.user_site

        def _expanduser(path):
            zwróć self.tmpdir
        self.old_expand = os.path.expanduser
        os.path.expanduser = _expanduser

        def cleanup():
            site.USER_BASE = self.old_user_base
            site.USER_SITE = self.old_user_site
            install_module.USER_BASE = self.old_user_base
            install_module.USER_SITE = self.old_user_site
            os.path.expanduser = self.old_expand

        self.addCleanup(cleanup)

        dla key w ('nt_user', 'unix_user'):
            self.assertIn(key, INSTALL_SCHEMES)

        dist = Distribution({'name': 'xx'})
        cmd = install(dist)

        # making sure the user option jest there
        options = [name dla name, short, lable w
                   cmd.user_options]
        self.assertIn('user', options)

        # setting a value
        cmd.user = 1

        # user base oraz site shouldn't be created yet
        self.assertNieprawda(os.path.exists(self.user_base))
        self.assertNieprawda(os.path.exists(self.user_site))

        # let's run finalize
        cmd.ensure_finalized()

        # now they should
        self.assertPrawda(os.path.exists(self.user_base))
        self.assertPrawda(os.path.exists(self.user_site))

        self.assertIn('userbase', cmd.config_vars)
        self.assertIn('usersite', cmd.config_vars)

    def test_handle_extra_path(self):
        dist = Distribution({'name': 'xx', 'extra_path': 'path,dirs'})
        cmd = install(dist)

        # two elements
        cmd.handle_extra_path()
        self.assertEqual(cmd.extra_path, ['path', 'dirs'])
        self.assertEqual(cmd.extra_dirs, 'dirs')
        self.assertEqual(cmd.path_file, 'path')

        # one element
        cmd.extra_path = ['path']
        cmd.handle_extra_path()
        self.assertEqual(cmd.extra_path, ['path'])
        self.assertEqual(cmd.extra_dirs, 'path')
        self.assertEqual(cmd.path_file, 'path')

        # none
        dist.extra_path = cmd.extra_path = Nic
        cmd.handle_extra_path()
        self.assertEqual(cmd.extra_path, Nic)
        self.assertEqual(cmd.extra_dirs, '')
        self.assertEqual(cmd.path_file, Nic)

        # three elements (no way !)
        cmd.extra_path = 'path,dirs,again'
        self.assertRaises(DistutilsOptionError, cmd.handle_extra_path)

    def test_finalize_options(self):
        dist = Distribution({'name': 'xx'})
        cmd = install(dist)

        # must supply either prefix/exec-prefix/home albo
        # install-base/install-platbase -- nie both
        cmd.prefix = 'prefix'
        cmd.install_base = 'base'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)

        # must supply either home albo prefix/exec-prefix -- nie both
        cmd.install_base = Nic
        cmd.home = 'home'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)

        # can't combine user przy prefix/exec_prefix/home albo
        # install_(plat)base
        cmd.prefix = Nic
        cmd.user = 'user'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)

    def test_record(self):
        install_dir = self.mkdtemp()
        project_dir, dist = self.create_dist(py_modules=['hello'],
                                             scripts=['sayhi'])
        os.chdir(project_dir)
        self.write_file('hello.py', "def main(): print('o hai')")
        self.write_file('sayhi', 'z hello zaimportuj main; main()')

        cmd = install(dist)
        dist.command_obj['install'] = cmd
        cmd.root = install_dir
        cmd.record = os.path.join(project_dir, 'filelist')
        cmd.ensure_finalized()
        cmd.run()

        f = open(cmd.record)
        spróbuj:
            content = f.read()
        w_końcu:
            f.close()

        found = [os.path.basename(line) dla line w content.splitlines()]
        expected = ['hello.py', 'hello.%s.pyc' % sys.implementation.cache_tag,
                    'sayhi',
                    'UNKNOWN-0.0.0-py%s.%s.egg-info' % sys.version_info[:2]]
        self.assertEqual(found, expected)

    def test_record_extensions(self):
        install_dir = self.mkdtemp()
        project_dir, dist = self.create_dist(ext_modules=[
            Extension('xx', ['xxmodule.c'])])
        os.chdir(project_dir)
        support.copy_xxmodule_c(project_dir)

        buildextcmd = build_ext(dist)
        support.fixup_build_ext(buildextcmd)
        buildextcmd.ensure_finalized()

        cmd = install(dist)
        dist.command_obj['install'] = cmd
        dist.command_obj['build_ext'] = buildextcmd
        cmd.root = install_dir
        cmd.record = os.path.join(project_dir, 'filelist')
        cmd.ensure_finalized()
        cmd.run()

        f = open(cmd.record)
        spróbuj:
            content = f.read()
        w_końcu:
            f.close()

        found = [os.path.basename(line) dla line w content.splitlines()]
        expected = [_make_ext_name('xx'),
                    'UNKNOWN-0.0.0-py%s.%s.egg-info' % sys.version_info[:2]]
        self.assertEqual(found, expected)

    def test_debug_mode(self):
        # this covers the code called when DEBUG jest set
        old_logs_len = len(self.logs)
        install_module.DEBUG = Prawda
        spróbuj:
            przy captured_stdout():
                self.test_record()
        w_końcu:
            install_module.DEBUG = Nieprawda
        self.assertGreater(len(self.logs), old_logs_len)


def test_suite():
    zwróć unittest.makeSuite(InstallTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
