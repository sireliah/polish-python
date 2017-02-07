"""Tests dla distutils.command.bdist_wininst."""
zaimportuj unittest
z test.support zaimportuj run_unittest

z distutils.command.bdist_wininst zaimportuj bdist_wininst
z distutils.tests zaimportuj support

klasa BuildWinInstTestCase(support.TempdirManager,
                           support.LoggingSilencer,
                           unittest.TestCase):

    def test_get_exe_bytes(self):

        # issue5731: command was broken on non-windows platforms
        # this test makes sure it works now dla every platform
        # let's create a command
        pkg_pth, dist = self.create_dist()
        cmd = bdist_wininst(dist)
        cmd.ensure_finalized()

        # let's run the code that finds the right wininst*.exe file
        # oraz make sure it finds it oraz returns its content
        # no matter what platform we have
        exe_file = cmd.get_exe_bytes()
        self.assertGreater(len(exe_file), 10)

def test_suite():
    zwróć unittest.makeSuite(BuildWinInstTestCase)

jeżeli __name__ == '__main__':
    run_unittest(test_suite())
