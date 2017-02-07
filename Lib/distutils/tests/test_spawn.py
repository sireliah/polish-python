"""Tests dla distutils.spawn."""
zaimportuj unittest
zaimportuj os
zaimportuj time
z test.support zaimportuj captured_stdout, run_unittest

z distutils.spawn zaimportuj _nt_quote_args
z distutils.spawn zaimportuj spawn, find_executable
z distutils.errors zaimportuj DistutilsExecError
z distutils.tests zaimportuj support

klasa SpawnTestCase(support.TempdirManager,
                    support.LoggingSilencer,
                    unittest.TestCase):

    def test_nt_quote_args(self):

        dla (args, wanted) w ((['przy space', 'nospace'],
                                ['"przy space"', 'nospace']),
                               (['nochange', 'nospace'],
                                ['nochange', 'nospace'])):
            res = _nt_quote_args(args)
            self.assertEqual(res, wanted)


    @unittest.skipUnless(os.name w ('nt', 'posix'),
                         'Runs only under posix albo nt')
    def test_spawn(self):
        tmpdir = self.mkdtemp()

        # creating something executable
        # through the shell that returns 1
        jeżeli os.name == 'posix':
            exe = os.path.join(tmpdir, 'foo.sh')
            self.write_file(exe, '#!/bin/sh\nexit 1')
        inaczej:
            exe = os.path.join(tmpdir, 'foo.bat')
            self.write_file(exe, 'exit 1')

        os.chmod(exe, 0o777)
        self.assertRaises(DistutilsExecError, spawn, [exe])

        # now something that works
        jeżeli os.name == 'posix':
            exe = os.path.join(tmpdir, 'foo.sh')
            self.write_file(exe, '#!/bin/sh\nexit 0')
        inaczej:
            exe = os.path.join(tmpdir, 'foo.bat')
            self.write_file(exe, 'exit 0')

        os.chmod(exe, 0o777)
        spawn([exe])  # should work without any error

def test_suite():
    zwróć unittest.makeSuite(SpawnTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
