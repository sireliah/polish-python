"""Tests dla distutils.pypirc.pypirc."""
zaimportuj sys
zaimportuj os
zaimportuj unittest
zaimportuj tempfile

z distutils.core zaimportuj PyPIRCCommand
z distutils.core zaimportuj Distribution
z distutils.log zaimportuj set_threshold
z distutils.log zaimportuj WARN

z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest

PYPIRC = """\
[distutils]

index-servers =
    server1
    server2

[server1]
username:me
password:secret

[server2]
username:meagain
password: secret
realm:acme
repository:http://another.pypi/
"""

PYPIRC_OLD = """\
[server-login]
username:tarek
password:secret
"""

WANTED = """\
[distutils]
index-servers =
    pypi

[pypi]
username:tarek
password:xxx
"""


klasa PyPIRCCommandTestCase(support.TempdirManager,
                            support.LoggingSilencer,
                            support.EnvironGuard,
                            unittest.TestCase):

    def setUp(self):
        """Patches the environment."""
        super(PyPIRCCommandTestCase, self).setUp()
        self.tmp_dir = self.mkdtemp()
        os.environ['HOME'] = self.tmp_dir
        self.rc = os.path.join(self.tmp_dir, '.pypirc')
        self.dist = Distribution()

        klasa command(PyPIRCCommand):
            def __init__(self, dist):
                PyPIRCCommand.__init__(self, dist)
            def initialize_options(self):
                dalej
            finalize_options = initialize_options

        self._cmd = command
        self.old_threshold = set_threshold(WARN)

    def tearDown(self):
        """Removes the patch."""
        set_threshold(self.old_threshold)
        super(PyPIRCCommandTestCase, self).tearDown()

    def test_server_registration(self):
        # This test makes sure PyPIRCCommand knows how to:
        # 1. handle several sections w .pypirc
        # 2. handle the old format

        # new format
        self.write_file(self.rc, PYPIRC)
        cmd = self._cmd(self.dist)
        config = cmd._read_pypirc()

        config = list(sorted(config.items()))
        waited = [('password', 'secret'), ('realm', 'pypi'),
                  ('repository', 'https://pypi.python.org/pypi'),
                  ('server', 'server1'), ('username', 'me')]
        self.assertEqual(config, waited)

        # old format
        self.write_file(self.rc, PYPIRC_OLD)
        config = cmd._read_pypirc()
        config = list(sorted(config.items()))
        waited = [('password', 'secret'), ('realm', 'pypi'),
                  ('repository', 'https://pypi.python.org/pypi'),
                  ('server', 'server-login'), ('username', 'tarek')]
        self.assertEqual(config, waited)

    def test_server_empty_registration(self):
        cmd = self._cmd(self.dist)
        rc = cmd._get_rc_file()
        self.assertNieprawda(os.path.exists(rc))
        cmd._store_pypirc('tarek', 'xxx')
        self.assertPrawda(os.path.exists(rc))
        f = open(rc)
        spróbuj:
            content = f.read()
            self.assertEqual(content, WANTED)
        w_końcu:
            f.close()

def test_suite():
    zwróć unittest.makeSuite(PyPIRCCommandTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
