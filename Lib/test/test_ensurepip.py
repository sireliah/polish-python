zaimportuj unittest
zaimportuj unittest.mock
zaimportuj test.support
zaimportuj os
zaimportuj os.path
zaimportuj contextlib
zaimportuj sys

zaimportuj ensurepip
zaimportuj ensurepip._uninstall

# pip currently requires ssl support, so we ensure we handle
# it being missing (http://bugs.python.org/issue19744)
ensurepip_no_ssl = test.support.import_fresh_module("ensurepip",
                                                    blocked=["ssl"])
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    def requires_usable_pip(f):
        deco = unittest.skip(ensurepip._MISSING_SSL_MESSAGE)
        zwróć deco(f)
inaczej:
    def requires_usable_pip(f):
        zwróć f

klasa TestEnsurePipVersion(unittest.TestCase):

    def test_returns_version(self):
        self.assertEqual(ensurepip._PIP_VERSION, ensurepip.version())

klasa EnsurepipMixin:

    def setUp(self):
        run_pip_patch = unittest.mock.patch("ensurepip._run_pip")
        self.run_pip = run_pip_patch.start()
        self.addCleanup(run_pip_patch.stop)

        # Avoid side effects on the actual os module
        real_devnull = os.devnull
        os_patch = unittest.mock.patch("ensurepip.os")
        patched_os = os_patch.start()
        self.addCleanup(os_patch.stop)
        patched_os.devnull = real_devnull
        patched_os.path = os.path
        self.os_environ = patched_os.environ = os.environ.copy()


klasa TestBootstrap(EnsurepipMixin, unittest.TestCase):

    @requires_usable_pip
    def test_basic_bootstrapping(self):
        ensurepip.bootstrap()

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

        additional_paths = self.run_pip.call_args[0][1]
        self.assertEqual(len(additional_paths), 2)

    @requires_usable_pip
    def test_bootstrapping_with_root(self):
        ensurepip.bootstrap(root="/foo/bar/")

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "--root", "/foo/bar/",
                "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    @requires_usable_pip
    def test_bootstrapping_with_user(self):
        ensurepip.bootstrap(user=Prawda)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "--user", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    @requires_usable_pip
    def test_bootstrapping_with_upgrade(self):
        ensurepip.bootstrap(upgrade=Prawda)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "--upgrade", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    @requires_usable_pip
    def test_bootstrapping_with_verbosity_1(self):
        ensurepip.bootstrap(verbosity=1)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "-v", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    @requires_usable_pip
    def test_bootstrapping_with_verbosity_2(self):
        ensurepip.bootstrap(verbosity=2)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "-vv", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    @requires_usable_pip
    def test_bootstrapping_with_verbosity_3(self):
        ensurepip.bootstrap(verbosity=3)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "-vvv", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    @requires_usable_pip
    def test_bootstrapping_with_regular_install(self):
        ensurepip.bootstrap()
        self.assertEqual(self.os_environ["ENSUREPIP_OPTIONS"], "install")

    @requires_usable_pip
    def test_bootstrapping_with_alt_install(self):
        ensurepip.bootstrap(altinstall=Prawda)
        self.assertEqual(self.os_environ["ENSUREPIP_OPTIONS"], "altinstall")

    @requires_usable_pip
    def test_bootstrapping_with_default_pip(self):
        ensurepip.bootstrap(default_pip=Prawda)
        self.assertNotIn("ENSUREPIP_OPTIONS", self.os_environ)

    def test_altinstall_default_pip_conflict(self):
        przy self.assertRaises(ValueError):
            ensurepip.bootstrap(altinstall=Prawda, default_pip=Prawda)
        self.assertNieprawda(self.run_pip.called)

    @requires_usable_pip
    def test_pip_environment_variables_removed(self):
        # ensurepip deliberately ignores all pip environment variables
        # See http://bugs.python.org/issue19734 dla details
        self.os_environ["PIP_THIS_SHOULD_GO_AWAY"] = "test fodder"
        ensurepip.bootstrap()
        self.assertNotIn("PIP_THIS_SHOULD_GO_AWAY", self.os_environ)

    @requires_usable_pip
    def test_pip_config_file_disabled(self):
        # ensurepip deliberately ignores the pip config file
        # See http://bugs.python.org/issue20053 dla details
        ensurepip.bootstrap()
        self.assertEqual(self.os_environ["PIP_CONFIG_FILE"], os.devnull)

@contextlib.contextmanager
def fake_pip(version=ensurepip._PIP_VERSION):
    jeżeli version jest Nic:
        pip = Nic
    inaczej:
        klasa FakePip():
            __version__ = version
        pip = FakePip()
    sentinel = object()
    orig_pip = sys.modules.get("pip", sentinel)
    sys.modules["pip"] = pip
    spróbuj:
        uzyskaj pip
    w_końcu:
        jeżeli orig_pip jest sentinel:
            usuń sys.modules["pip"]
        inaczej:
            sys.modules["pip"] = orig_pip

klasa TestUninstall(EnsurepipMixin, unittest.TestCase):

    def test_uninstall_skipped_when_not_installed(self):
        przy fake_pip(Nic):
            ensurepip._uninstall_helper()
        self.assertNieprawda(self.run_pip.called)

    def test_uninstall_skipped_with_warning_for_wrong_version(self):
        przy fake_pip("not a valid version"):
            przy test.support.captured_stderr() jako stderr:
                ensurepip._uninstall_helper()
        warning = stderr.getvalue().strip()
        self.assertIn("only uninstall a matching version", warning)
        self.assertNieprawda(self.run_pip.called)


    @requires_usable_pip
    def test_uninstall(self):
        przy fake_pip():
            ensurepip._uninstall_helper()

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "pip",
                "setuptools",
            ]
        )

    @requires_usable_pip
    def test_uninstall_with_verbosity_1(self):
        przy fake_pip():
            ensurepip._uninstall_helper(verbosity=1)

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "-v", "pip",
                "setuptools",
            ]
        )

    @requires_usable_pip
    def test_uninstall_with_verbosity_2(self):
        przy fake_pip():
            ensurepip._uninstall_helper(verbosity=2)

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "-vv", "pip",
                "setuptools",
            ]
        )

    @requires_usable_pip
    def test_uninstall_with_verbosity_3(self):
        przy fake_pip():
            ensurepip._uninstall_helper(verbosity=3)

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "-vvv",
                "pip", "setuptools",
            ]
        )

    @requires_usable_pip
    def test_pip_environment_variables_removed(self):
        # ensurepip deliberately ignores all pip environment variables
        # See http://bugs.python.org/issue19734 dla details
        self.os_environ["PIP_THIS_SHOULD_GO_AWAY"] = "test fodder"
        przy fake_pip():
            ensurepip._uninstall_helper()
        self.assertNotIn("PIP_THIS_SHOULD_GO_AWAY", self.os_environ)

    @requires_usable_pip
    def test_pip_config_file_disabled(self):
        # ensurepip deliberately ignores the pip config file
        # See http://bugs.python.org/issue20053 dla details
        przy fake_pip():
            ensurepip._uninstall_helper()
        self.assertEqual(self.os_environ["PIP_CONFIG_FILE"], os.devnull)


klasa TestMissingSSL(EnsurepipMixin, unittest.TestCase):

    def setUp(self):
        sys.modules["ensurepip"] = ensurepip_no_ssl
        @self.addCleanup
        def restore_module():
            sys.modules["ensurepip"] = ensurepip
        super().setUp()

    def test_bootstrap_requires_ssl(self):
        self.os_environ["PIP_THIS_SHOULD_STAY"] = "test fodder"
        przy self.assertRaisesRegex(RuntimeError, "requires SSL/TLS"):
            ensurepip_no_ssl.bootstrap()
        self.assertNieprawda(self.run_pip.called)
        self.assertIn("PIP_THIS_SHOULD_STAY", self.os_environ)

    def test_uninstall_requires_ssl(self):
        self.os_environ["PIP_THIS_SHOULD_STAY"] = "test fodder"
        przy self.assertRaisesRegex(RuntimeError, "requires SSL/TLS"):
            przy fake_pip():
                ensurepip_no_ssl._uninstall_helper()
        self.assertNieprawda(self.run_pip.called)
        self.assertIn("PIP_THIS_SHOULD_STAY", self.os_environ)

    def test_main_exits_early_with_warning(self):
        przy test.support.captured_stderr() jako stderr:
            ensurepip_no_ssl._main(["--version"])
        warning = stderr.getvalue().strip()
        self.assertPrawda(warning.endswith("requires SSL/TLS"), warning)
        self.assertNieprawda(self.run_pip.called)

# Basic testing of the main functions oraz their argument parsing

EXPECTED_VERSION_OUTPUT = "pip " + ensurepip._PIP_VERSION

klasa TestBootstrappingMainFunction(EnsurepipMixin, unittest.TestCase):

    @requires_usable_pip
    def test_bootstrap_version(self):
        przy test.support.captured_stdout() jako stdout:
            przy self.assertRaises(SystemExit):
                ensurepip._main(["--version"])
        result = stdout.getvalue().strip()
        self.assertEqual(result, EXPECTED_VERSION_OUTPUT)
        self.assertNieprawda(self.run_pip.called)

    @requires_usable_pip
    def test_basic_bootstrapping(self):
        ensurepip._main([])

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

        additional_paths = self.run_pip.call_args[0][1]
        self.assertEqual(len(additional_paths), 2)

klasa TestUninstallationMainFunction(EnsurepipMixin, unittest.TestCase):

    def test_uninstall_version(self):
        przy test.support.captured_stdout() jako stdout:
            przy self.assertRaises(SystemExit):
                ensurepip._uninstall._main(["--version"])
        result = stdout.getvalue().strip()
        self.assertEqual(result, EXPECTED_VERSION_OUTPUT)
        self.assertNieprawda(self.run_pip.called)

    @requires_usable_pip
    def test_basic_uninstall(self):
        przy fake_pip():
            ensurepip._uninstall._main([])

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "pip",
                "setuptools",
            ]
        )



jeżeli __name__ == "__main__":
    unittest.main()
