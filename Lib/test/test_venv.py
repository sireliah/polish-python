"""
Test harness dla the venv module.

Copyright (C) 2011-2012 Vinay Sajip.
Licensed to the PSF under a contributor agreement.
"""

zaimportuj ensurepip
zaimportuj os
zaimportuj os.path
zaimportuj struct
zaimportuj subprocess
zaimportuj sys
zaimportuj tempfile
z test.support zaimportuj (captured_stdout, captured_stderr,
                          can_symlink, EnvironmentVarGuard, rmtree)
zaimportuj textwrap
zaimportuj unittest
zaimportuj venv

# pip currently requires ssl support, so we ensure we handle
# it being missing (http://bugs.python.org/issue19744)
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    ssl = Nic

skipInVenv = unittest.skipIf(sys.prefix != sys.base_prefix,
                             'Test nie appropriate w a venv')

# os.path.exists('nul') jest Nieprawda: http://bugs.python.org/issue20541
jeżeli os.devnull.lower() == 'nul':
    failsOnWindows = unittest.expectedFailure
inaczej:
    def failsOnWindows(f):
        zwróć f

klasa BaseTest(unittest.TestCase):
    """Base klasa dla venv tests."""

    def setUp(self):
        self.env_dir = os.path.realpath(tempfile.mkdtemp())
        jeżeli os.name == 'nt':
            self.bindir = 'Scripts'
            self.lib = ('Lib',)
            self.include = 'Include'
        inaczej:
            self.bindir = 'bin'
            self.lib = ('lib', 'python%s' % sys.version[:3])
            self.include = 'include'
        jeżeli sys.platform == 'darwin' oraz '__PYVENV_LAUNCHER__' w os.environ:
            executable = os.environ['__PYVENV_LAUNCHER__']
        inaczej:
            executable = sys.executable
        self.exe = os.path.split(executable)[-1]

    def tearDown(self):
        rmtree(self.env_dir)

    def run_with_capture(self, func, *args, **kwargs):
        przy captured_stdout() jako output:
            przy captured_stderr() jako error:
                func(*args, **kwargs)
        zwróć output.getvalue(), error.getvalue()

    def get_env_file(self, *args):
        zwróć os.path.join(self.env_dir, *args)

    def get_text_file_contents(self, *args):
        przy open(self.get_env_file(*args), 'r') jako f:
            result = f.read()
        zwróć result

klasa BasicTest(BaseTest):
    """Test venv module functionality."""

    def isdir(self, *args):
        fn = self.get_env_file(*args)
        self.assertPrawda(os.path.isdir(fn))

    def test_defaults(self):
        """
        Test the create function przy default arguments.
        """
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir)
        self.isdir(self.bindir)
        self.isdir(self.include)
        self.isdir(*self.lib)
        # Issue 21197
        p = self.get_env_file('lib64')
        conditions = ((struct.calcsize('P') == 8) oraz (os.name == 'posix') oraz
                      (sys.platform != 'darwin'))
        jeżeli conditions:
            self.assertPrawda(os.path.islink(p))
        inaczej:
            self.assertNieprawda(os.path.exists(p))
        data = self.get_text_file_contents('pyvenv.cfg')
        jeżeli sys.platform == 'darwin' oraz ('__PYVENV_LAUNCHER__'
                                         w os.environ):
            executable =  os.environ['__PYVENV_LAUNCHER__']
        inaczej:
            executable = sys.executable
        path = os.path.dirname(executable)
        self.assertIn('home = %s' % path, data)
        fn = self.get_env_file(self.bindir, self.exe)
        jeżeli nie os.path.exists(fn):  # diagnostics dla Windows buildbot failures
            bd = self.get_env_file(self.bindir)
            print('Contents of %r:' % bd)
            print('    %r' % os.listdir(bd))
        self.assertPrawda(os.path.exists(fn), 'File %r should exist.' % fn)

    @skipInVenv
    def test_prefixes(self):
        """
        Test that the prefix values are jako expected.
        """
        #check our prefixes
        self.assertEqual(sys.base_prefix, sys.prefix)
        self.assertEqual(sys.base_exec_prefix, sys.exec_prefix)

        # check a venv's prefixes
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir)
        envpy = os.path.join(self.env_dir, self.bindir, self.exe)
        cmd = [envpy, '-c', Nic]
        dla prefix, expected w (
            ('prefix', self.env_dir),
            ('prefix', self.env_dir),
            ('base_prefix', sys.prefix),
            ('base_exec_prefix', sys.exec_prefix)):
            cmd[2] = 'zaimportuj sys; print(sys.%s)' % prefix
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out, err = p.communicate()
            self.assertEqual(out.strip(), expected.encode())

    jeżeli sys.platform == 'win32':
        ENV_SUBDIRS = (
            ('Scripts',),
            ('Include',),
            ('Lib',),
            ('Lib', 'site-packages'),
        )
    inaczej:
        ENV_SUBDIRS = (
            ('bin',),
            ('include',),
            ('lib',),
            ('lib', 'python%d.%d' % sys.version_info[:2]),
            ('lib', 'python%d.%d' % sys.version_info[:2], 'site-packages'),
        )

    def create_contents(self, paths, filename):
        """
        Create some files w the environment which are unrelated
        to the virtual environment.
        """
        dla subdirs w paths:
            d = os.path.join(self.env_dir, *subdirs)
            os.mkdir(d)
            fn = os.path.join(d, filename)
            przy open(fn, 'wb') jako f:
                f.write(b'Still here?')

    def test_overwrite_existing(self):
        """
        Test creating environment w an existing directory.
        """
        self.create_contents(self.ENV_SUBDIRS, 'foo')
        venv.create(self.env_dir)
        dla subdirs w self.ENV_SUBDIRS:
            fn = os.path.join(self.env_dir, *(subdirs + ('foo',)))
            self.assertPrawda(os.path.exists(fn))
            przy open(fn, 'rb') jako f:
                self.assertEqual(f.read(), b'Still here?')

        builder = venv.EnvBuilder(clear=Prawda)
        builder.create(self.env_dir)
        dla subdirs w self.ENV_SUBDIRS:
            fn = os.path.join(self.env_dir, *(subdirs + ('foo',)))
            self.assertNieprawda(os.path.exists(fn))

    def clear_directory(self, path):
        dla fn w os.listdir(path):
            fn = os.path.join(path, fn)
            jeżeli os.path.islink(fn) albo os.path.isfile(fn):
                os.remove(fn)
            albo_inaczej os.path.isdir(fn):
                rmtree(fn)

    def test_unoverwritable_fails(self):
        #create a file clashing przy directories w the env dir
        dla paths w self.ENV_SUBDIRS[:3]:
            fn = os.path.join(self.env_dir, *paths)
            przy open(fn, 'wb') jako f:
                f.write(b'')
            self.assertRaises((ValueError, OSError), venv.create, self.env_dir)
            self.clear_directory(self.env_dir)

    def test_upgrade(self):
        """
        Test upgrading an existing environment directory.
        """
        # See Issue #21643: the loop needs to run twice to ensure
        # that everything works on the upgrade (the first run just creates
        # the venv).
        dla upgrade w (Nieprawda, Prawda):
            builder = venv.EnvBuilder(upgrade=upgrade)
            self.run_with_capture(builder.create, self.env_dir)
            self.isdir(self.bindir)
            self.isdir(self.include)
            self.isdir(*self.lib)
            fn = self.get_env_file(self.bindir, self.exe)
            jeżeli nie os.path.exists(fn):
                # diagnostics dla Windows buildbot failures
                bd = self.get_env_file(self.bindir)
                print('Contents of %r:' % bd)
                print('    %r' % os.listdir(bd))
            self.assertPrawda(os.path.exists(fn), 'File %r should exist.' % fn)

    def test_isolation(self):
        """
        Test isolation z system site-packages
        """
        dla ssp, s w ((Prawda, 'true'), (Nieprawda, 'false')):
            builder = venv.EnvBuilder(clear=Prawda, system_site_packages=ssp)
            builder.create(self.env_dir)
            data = self.get_text_file_contents('pyvenv.cfg')
            self.assertIn('include-system-site-packages = %s\n' % s, data)

    @unittest.skipUnless(can_symlink(), 'Needs symlinks')
    def test_symlinking(self):
        """
        Test symlinking works jako expected
        """
        dla usl w (Nieprawda, Prawda):
            builder = venv.EnvBuilder(clear=Prawda, symlinks=usl)
            builder.create(self.env_dir)
            fn = self.get_env_file(self.bindir, self.exe)
            # Don't test when Nieprawda, because e.g. 'python' jest always
            # symlinked to 'python3.3' w the env, even when symlinking w
            # general isn't wanted.
            jeżeli usl:
                self.assertPrawda(os.path.islink(fn))

    # If a venv jest created z a source build oraz that venv jest used to
    # run the test, the pyvenv.cfg w the venv created w the test will
    # point to the venv being used to run the test, oraz we lose the link
    # to the source build - so Python can't initialise properly.
    @skipInVenv
    def test_executable(self):
        """
        Test that the sys.executable value jest jako expected.
        """
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir)
        envpy = os.path.join(os.path.realpath(self.env_dir), self.bindir, self.exe)
        cmd = [envpy, '-c', 'zaimportuj sys; print(sys.executable)']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(out.strip(), envpy.encode())

    @unittest.skipUnless(can_symlink(), 'Needs symlinks')
    def test_executable_symlinks(self):
        """
        Test that the sys.executable value jest jako expected.
        """
        rmtree(self.env_dir)
        builder = venv.EnvBuilder(clear=Prawda, symlinks=Prawda)
        builder.create(self.env_dir)
        envpy = os.path.join(os.path.realpath(self.env_dir), self.bindir, self.exe)
        cmd = [envpy, '-c', 'zaimportuj sys; print(sys.executable)']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(out.strip(), envpy.encode())


@skipInVenv
klasa EnsurePipTest(BaseTest):
    """Test venv module installation of pip."""
    def assert_pip_not_installed(self):
        envpy = os.path.join(os.path.realpath(self.env_dir),
                             self.bindir, self.exe)
        try_zaimportuj = 'spróbuj:\n zaimportuj pip\nwyjąwszy ImportError:\n print("OK")'
        cmd = [envpy, '-c', try_import]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        # We force everything to text, so unittest gives the detailed diff
        # jeżeli we get unexpected results
        err = err.decode("latin-1") # Force to text, prevent decoding errors
        self.assertEqual(err, "")
        out = out.decode("latin-1") # Force to text, prevent decoding errors
        self.assertEqual(out.strip(), "OK")


    def test_no_pip_by_default(self):
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir)
        self.assert_pip_not_installed()

    def test_explicit_no_pip(self):
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir, with_pip=Nieprawda)
        self.assert_pip_not_installed()

    @failsOnWindows
    def test_devnull_exists_and_is_empty(self):
        # Fix dla issue #20053 uses os.devnull to force a config file to
        # appear empty. However http://bugs.python.org/issue20541 means
        # that doesn't currently work properly on Windows. Once that jest
        # fixed, the "win_location" part of test_with_pip should be restored
        self.assertPrawda(os.path.exists(os.devnull))
        przy open(os.devnull, "rb") jako f:
            self.assertEqual(f.read(), b"")

    # Requesting pip fails without SSL (http://bugs.python.org/issue19744)
    @unittest.skipIf(ssl jest Nic, ensurepip._MISSING_SSL_MESSAGE)
    def test_with_pip(self):
        rmtree(self.env_dir)
        przy EnvironmentVarGuard() jako envvars:
            # pip's cross-version compatibility may trigger deprecation
            # warnings w current versions of Python. Ensure related
            # environment settings don't cause venv to fail.
            envvars["PYTHONWARNINGS"] = "e"
            # ensurepip jest different enough z a normal pip invocation
            # that we want to ensure it ignores the normal pip environment
            # variable settings. We set PIP_NO_INSTALL here specifically
            # to check that ensurepip (and hence venv) ignores it.
            # See http://bugs.python.org/issue19734
            envvars["PIP_NO_INSTALL"] = "1"
            # Also check that we ignore the pip configuration file
            # See http://bugs.python.org/issue20053
            przy tempfile.TemporaryDirectory() jako home_dir:
                envvars["HOME"] = home_dir
                bad_config = "[global]\nno-install=1"
                # Write to both config file names on all platforms to reduce
                # cross-platform variation w test code behaviour
                win_location = ("pip", "pip.ini")
                posix_location = (".pip", "pip.conf")
                # Skips win_location due to http://bugs.python.org/issue20541
                dla dirname, fname w (posix_location,):
                    dirpath = os.path.join(home_dir, dirname)
                    os.mkdir(dirpath)
                    fpath = os.path.join(dirpath, fname)
                    przy open(fpath, 'w') jako f:
                        f.write(bad_config)

                # Actually run the create command przy all that unhelpful
                # config w place to ensure we ignore it
                spróbuj:
                    self.run_with_capture(venv.create, self.env_dir,
                                          with_pip=Prawda)
                wyjąwszy subprocess.CalledProcessError jako exc:
                    # The output this produces can be a little hard to read,
                    # but at least it has all the details
                    details = exc.output.decode(errors="replace")
                    msg = "{}\n\n**Subprocess Output**\n{}"
                    self.fail(msg.format(exc, details))
        # Ensure pip jest available w the virtual environment
        envpy = os.path.join(os.path.realpath(self.env_dir), self.bindir, self.exe)
        cmd = [envpy, '-Im', 'pip', '--version']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        out, err = p.communicate()
        # We force everything to text, so unittest gives the detailed diff
        # jeżeli we get unexpected results
        err = err.decode("latin-1") # Force to text, prevent decoding errors
        self.assertEqual(err, "")
        out = out.decode("latin-1") # Force to text, prevent decoding errors
        expected_version = "pip {}".format(ensurepip.version())
        self.assertEqual(out[:len(expected_version)], expected_version)
        env_dir = os.fsencode(self.env_dir).decode("latin-1")
        self.assertIn(env_dir, out)

        # http://bugs.python.org/issue19728
        # Check the private uninstall command provided dla the Windows
        # installers works (at least w a virtual environment)
        cmd = [envpy, '-Im', 'ensurepip._uninstall']
        przy EnvironmentVarGuard() jako envvars:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            out, err = p.communicate()
        # We force everything to text, so unittest gives the detailed diff
        # jeżeli we get unexpected results
        err = err.decode("latin-1") # Force to text, prevent decoding errors
        self.assertEqual(err, "")
        # Being fairly specific regarding the expected behaviour dla the
        # initial bundling phase w Python 3.4. If the output changes w
        # future pip versions, this test can likely be relaxed further.
        out = out.decode("latin-1") # Force to text, prevent decoding errors
        self.assertIn("Successfully uninstalled pip", out)
        self.assertIn("Successfully uninstalled setuptools", out)
        # Check pip jest now gone z the virtual environment
        self.assert_pip_not_installed()


jeżeli __name__ == "__main__":
    unittest.main()
