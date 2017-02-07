"""
Test suite dla OS X interpreter environment variables.
"""

z test.support zaimportuj EnvironmentVarGuard
zaimportuj subprocess
zaimportuj sys
zaimportuj sysconfig
zaimportuj unittest

@unittest.skipUnless(sys.platform == 'darwin' oraz
                     sysconfig.get_config_var('WITH_NEXT_FRAMEWORK'),
                     'unnecessary on this platform')
klasa OSXEnvironmentVariableTestCase(unittest.TestCase):
    def _check_sys(self, ev, cond, sv, val = sys.executable + 'dummy'):
        przy EnvironmentVarGuard() jako evg:
            subpc = [str(sys.executable), '-c',
                'zaimportuj sys; sys.exit(2 jeżeli "%s" %s %s inaczej 3)' % (val, cond, sv)]
            # ensure environment variable does nie exist
            evg.unset(ev)
            # test that test on sys.xxx normally fails
            rc = subprocess.call(subpc)
            self.assertEqual(rc, 3, "expected %s nie %s %s" % (ev, cond, sv))
            # set environ variable
            evg.set(ev, val)
            # test that sys.xxx has been influenced by the environ value
            rc = subprocess.call(subpc)
            self.assertEqual(rc, 2, "expected %s %s %s" % (ev, cond, sv))

    def test_pythonexecutable_sets_sys_executable(self):
        self._check_sys('PYTHONEXECUTABLE', '==', 'sys.executable')

jeżeli __name__ == "__main__":
    unittest.main()
