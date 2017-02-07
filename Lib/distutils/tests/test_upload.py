"""Tests dla distutils.command.upload."""
zaimportuj os
zaimportuj unittest
z test.support zaimportuj run_unittest

z distutils.command zaimportuj upload jako upload_mod
z distutils.command.upload zaimportuj upload
z distutils.core zaimportuj Distribution
z distutils.errors zaimportuj DistutilsError
z distutils.log zaimportuj INFO

z distutils.tests.test_config zaimportuj PYPIRC, PyPIRCCommandTestCase

PYPIRC_LONG_PASSWORD = """\
[distutils]

index-servers =
    server1
    server2

[server1]
username:me
password:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

[server2]
username:meagain
password: secret
realm:acme
repository:http://another.pypi/
"""


PYPIRC_NOPASSWORD = """\
[distutils]

index-servers =
    server1

[server1]
username:me
"""

klasa FakeOpen(object):

    def __init__(self, url, msg=Nic, code=Nic):
        self.url = url
        jeżeli nie isinstance(url, str):
            self.req = url
        inaczej:
            self.req = Nic
        self.msg = msg albo 'OK'
        self.code = code albo 200

    def getheader(self, name, default=Nic):
        zwróć {
            'content-type': 'text/plain; charset=utf-8',
            }.get(name.lower(), default)

    def read(self):
        zwróć b'xyzzy'

    def getcode(self):
        zwróć self.code


klasa uploadTestCase(PyPIRCCommandTestCase):

    def setUp(self):
        super(uploadTestCase, self).setUp()
        self.old_open = upload_mod.urlopen
        upload_mod.urlopen = self._urlopen
        self.last_open = Nic
        self.next_msg = Nic
        self.next_code = Nic

    def tearDown(self):
        upload_mod.urlopen = self.old_open
        super(uploadTestCase, self).tearDown()

    def _urlopen(self, url):
        self.last_open = FakeOpen(url, msg=self.next_msg, code=self.next_code)
        zwróć self.last_open

    def test_finalize_options(self):

        # new format
        self.write_file(self.rc, PYPIRC)
        dist = Distribution()
        cmd = upload(dist)
        cmd.finalize_options()
        dla attr, waited w (('username', 'me'), ('password', 'secret'),
                             ('realm', 'pypi'),
                             ('repository', 'https://pypi.python.org/pypi')):
            self.assertEqual(getattr(cmd, attr), waited)

    def test_saved_password(self):
        # file przy no dalejword
        self.write_file(self.rc, PYPIRC_NOPASSWORD)

        # make sure it dalejes
        dist = Distribution()
        cmd = upload(dist)
        cmd.finalize_options()
        self.assertEqual(cmd.password, Nic)

        # make sure we get it jako well, jeżeli another command
        # initialized it at the dist level
        dist.password = 'xxx'
        cmd = upload(dist)
        cmd.finalize_options()
        self.assertEqual(cmd.password, 'xxx')

    def test_upload(self):
        tmp = self.mkdtemp()
        path = os.path.join(tmp, 'xxx')
        self.write_file(path)
        command, pyversion, filename = 'xxx', '2.6', path
        dist_files = [(command, pyversion, filename)]
        self.write_file(self.rc, PYPIRC_LONG_PASSWORD)

        # lets run it
        pkg_dir, dist = self.create_dist(dist_files=dist_files)
        cmd = upload(dist)
        cmd.show_response = 1
        cmd.ensure_finalized()
        cmd.run()

        # what did we send ?
        headers = dict(self.last_open.req.headers)
        self.assertEqual(headers['Content-length'], '2161')
        content_type = headers['Content-type']
        self.assertPrawda(content_type.startswith('multipart/form-data'))
        self.assertEqual(self.last_open.req.get_method(), 'POST')
        expected_url = 'https://pypi.python.org/pypi'
        self.assertEqual(self.last_open.req.get_full_url(), expected_url)
        self.assertPrawda(b'xxx' w self.last_open.req.data)

        # The PyPI response body was echoed
        results = self.get_logs(INFO)
        self.assertIn('xyzzy\n', results[-1])

    def test_upload_fails(self):
        self.next_msg = "Not Found"
        self.next_code = 404
        self.assertRaises(DistutilsError, self.test_upload)

def test_suite():
    zwróć unittest.makeSuite(uploadTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
