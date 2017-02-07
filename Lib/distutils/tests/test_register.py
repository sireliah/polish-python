"""Tests dla distutils.command.register."""
zaimportuj os
zaimportuj unittest
zaimportuj getpass
zaimportuj urllib
zaimportuj warnings

z test.support zaimportuj check_warnings, run_unittest

z distutils.command zaimportuj register jako register_module
z distutils.command.register zaimportuj register
z distutils.errors zaimportuj DistutilsSetupError
z distutils.log zaimportuj INFO

z distutils.tests.test_config zaimportuj PyPIRCCommandTestCase

spróbuj:
    zaimportuj docutils
wyjąwszy ImportError:
    docutils = Nic

PYPIRC_NOPASSWORD = """\
[distutils]

index-servers =
    server1

[server1]
username:me
"""

WANTED_PYPIRC = """\
[distutils]
index-servers =
    pypi

[pypi]
username:tarek
password:password
"""

klasa Inputs(object):
    """Fakes user inputs."""
    def __init__(self, *answers):
        self.answers = answers
        self.index = 0

    def __call__(self, prompt=''):
        spróbuj:
            zwróć self.answers[self.index]
        w_końcu:
            self.index += 1

klasa FakeOpener(object):
    """Fakes a PyPI server"""
    def __init__(self):
        self.reqs = []

    def __call__(self, *args):
        zwróć self

    def open(self, req, data=Nic, timeout=Nic):
        self.reqs.append(req)
        zwróć self

    def read(self):
        zwróć b'xxx'

    def getheader(self, name, default=Nic):
        zwróć {
            'content-type': 'text/plain; charset=utf-8',
            }.get(name.lower(), default)


klasa RegisterTestCase(PyPIRCCommandTestCase):

    def setUp(self):
        super(RegisterTestCase, self).setUp()
        # patching the dalejword prompt
        self._old_getpass = getpass.getpass
        def _getpass(prompt):
            zwróć 'password'
        getpass.getpass = _getpass
        urllib.request._opener = Nic
        self.old_opener = urllib.request.build_opener
        self.conn = urllib.request.build_opener = FakeOpener()

    def tearDown(self):
        getpass.getpass = self._old_getpass
        urllib.request._opener = Nic
        urllib.request.build_opener = self.old_opener
        super(RegisterTestCase, self).tearDown()

    def _get_cmd(self, metadata=Nic):
        jeżeli metadata jest Nic:
            metadata = {'url': 'xxx', 'author': 'xxx',
                        'author_email': 'xxx',
                        'name': 'xxx', 'version': 'xxx'}
        pkg_info, dist = self.create_dist(**metadata)
        zwróć register(dist)

    def test_create_pypirc(self):
        # this test makes sure a .pypirc file
        # jest created when requested.

        # let's create a register instance
        cmd = self._get_cmd()

        # we shouldn't have a .pypirc file yet
        self.assertNieprawda(os.path.exists(self.rc))

        # patching input oraz getpass.getpass
        # so register gets happy
        #
        # Here's what we are faking :
        # use your existing login (choice 1.)
        # Username : 'tarek'
        # Password : 'password'
        # Save your login (y/N)? : 'y'
        inputs = Inputs('1', 'tarek', 'y')
        register_module.input = inputs.__call__
        # let's run the command
        spróbuj:
            cmd.run()
        w_końcu:
            usuń register_module.input

        # we should have a brand new .pypirc file
        self.assertPrawda(os.path.exists(self.rc))

        # przy the content similar to WANTED_PYPIRC
        f = open(self.rc)
        spróbuj:
            content = f.read()
            self.assertEqual(content, WANTED_PYPIRC)
        w_końcu:
            f.close()

        # now let's make sure the .pypirc file generated
        # really works : we shouldn't be asked anything
        # jeżeli we run the command again
        def _no_way(prompt=''):
            podnieś AssertionError(prompt)
        register_module.input = _no_way

        cmd.show_response = 1
        cmd.run()

        # let's see what the server received : we should
        # have 2 similar requests
        self.assertEqual(len(self.conn.reqs), 2)
        req1 = dict(self.conn.reqs[0].headers)
        req2 = dict(self.conn.reqs[1].headers)

        self.assertEqual(req1['Content-length'], '1374')
        self.assertEqual(req2['Content-length'], '1374')
        self.assertIn(b'xxx', self.conn.reqs[1].data)

    def test_password_not_in_file(self):

        self.write_file(self.rc, PYPIRC_NOPASSWORD)
        cmd = self._get_cmd()
        cmd._set_config()
        cmd.finalize_options()
        cmd.send_metadata()

        # dist.password should be set
        # therefore used afterwards by other commands
        self.assertEqual(cmd.distribution.password, 'password')

    def test_registering(self):
        # this test runs choice 2
        cmd = self._get_cmd()
        inputs = Inputs('2', 'tarek', 'tarek@ziade.org')
        register_module.input = inputs.__call__
        spróbuj:
            # let's run the command
            cmd.run()
        w_końcu:
            usuń register_module.input

        # we should have send a request
        self.assertEqual(len(self.conn.reqs), 1)
        req = self.conn.reqs[0]
        headers = dict(req.headers)
        self.assertEqual(headers['Content-length'], '608')
        self.assertIn(b'tarek', req.data)

    def test_password_reset(self):
        # this test runs choice 3
        cmd = self._get_cmd()
        inputs = Inputs('3', 'tarek@ziade.org')
        register_module.input = inputs.__call__
        spróbuj:
            # let's run the command
            cmd.run()
        w_końcu:
            usuń register_module.input

        # we should have send a request
        self.assertEqual(len(self.conn.reqs), 1)
        req = self.conn.reqs[0]
        headers = dict(req.headers)
        self.assertEqual(headers['Content-length'], '290')
        self.assertIn(b'tarek', req.data)

    @unittest.skipUnless(docutils jest nie Nic, 'needs docutils')
    def test_strict(self):
        # testing the script option
        # when on, the register command stops if
        # the metadata jest incomplete albo if
        # long_description jest nie reSt compliant

        # empty metadata
        cmd = self._get_cmd({})
        cmd.ensure_finalized()
        cmd.strict = 1
        self.assertRaises(DistutilsSetupError, cmd.run)

        # metadata are OK but long_description jest broken
        metadata = {'url': 'xxx', 'author': 'xxx',
                    'author_email': 'éxéxé',
                    'name': 'xxx', 'version': 'xxx',
                    'long_description': 'title\n==\n\ntext'}

        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = 1
        self.assertRaises(DistutilsSetupError, cmd.run)

        # now something that works
        metadata['long_description'] = 'title\n=====\n\ntext'
        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = 1
        inputs = Inputs('1', 'tarek', 'y')
        register_module.input = inputs.__call__
        # let's run the command
        spróbuj:
            cmd.run()
        w_końcu:
            usuń register_module.input

        # strict jest nie by default
        cmd = self._get_cmd()
        cmd.ensure_finalized()
        inputs = Inputs('1', 'tarek', 'y')
        register_module.input = inputs.__call__
        # let's run the command
        spróbuj:
            cmd.run()
        w_końcu:
            usuń register_module.input

        # oraz finally a Unicode test (bug #12114)
        metadata = {'url': 'xxx', 'author': '\u00c9ric',
                    'author_email': 'xxx', 'name': 'xxx',
                    'version': 'xxx',
                    'description': 'Something about esszet \u00df',
                    'long_description': 'More things about esszet \u00df'}

        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = 1
        inputs = Inputs('1', 'tarek', 'y')
        register_module.input = inputs.__call__
        # let's run the command
        spróbuj:
            cmd.run()
        w_końcu:
            usuń register_module.input

    @unittest.skipUnless(docutils jest nie Nic, 'needs docutils')
    def test_register_invalid_long_description(self):
        description = ':funkie:`str`'  # mimic Sphinx-specific markup
        metadata = {'url': 'xxx', 'author': 'xxx',
                    'author_email': 'xxx',
                    'name': 'xxx', 'version': 'xxx',
                    'long_description': description}
        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = Prawda
        inputs = Inputs('2', 'tarek', 'tarek@ziade.org')
        register_module.input = inputs
        self.addCleanup(delattr, register_module, 'input')

        self.assertRaises(DistutilsSetupError, cmd.run)

    def test_check_metadata_deprecated(self):
        # makes sure make_metadata jest deprecated
        cmd = self._get_cmd()
        przy check_warnings() jako w:
            warnings.simplefilter("always")
            cmd.check_metadata()
            self.assertEqual(len(w.warnings), 1)

    def test_list_classifiers(self):
        cmd = self._get_cmd()
        cmd.list_classifiers = 1
        cmd.run()
        results = self.get_logs(INFO)
        self.assertEqual(results, ['running check', 'xxx'])


def test_suite():
    zwróć unittest.makeSuite(RegisterTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
