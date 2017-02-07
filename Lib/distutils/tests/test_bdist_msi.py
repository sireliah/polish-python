"""Tests dla distutils.command.bdist_msi."""
zaimportuj sys
zaimportuj unittest
z test.support zaimportuj run_unittest
z distutils.tests zaimportuj support


@unittest.skipUnless(sys.platform == 'win32', 'these tests require Windows')
klasa BDistMSITestCase(support.TempdirManager,
                       support.LoggingSilencer,
                       unittest.TestCase):

    def test_minimal(self):
        # minimal test XXX need more tests
        z distutils.command.bdist_msi zaimportuj bdist_msi
        project_dir, dist = self.create_dist()
        cmd = bdist_msi(dist)
        cmd.ensure_finalized()


def test_suite():
    zwróć unittest.makeSuite(BDistMSITestCase)

jeżeli __name__ == '__main__':
    run_unittest(test_suite())
