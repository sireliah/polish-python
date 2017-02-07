"""Tests dla distutils.command.bdist."""
zaimportuj os
zaimportuj unittest
z test.support zaimportuj run_unittest

z distutils.command.bdist zaimportuj bdist
z distutils.tests zaimportuj support


klasa BuildTestCase(support.TempdirManager,
                    unittest.TestCase):

    def test_formats(self):
        # let's create a command oraz make sure
        # we can set the format
        dist = self.create_dist()[1]
        cmd = bdist(dist)
        cmd.formats = ['msi']
        cmd.ensure_finalized()
        self.assertEqual(cmd.formats, ['msi'])

        # what formats does bdist offer?
        formats = ['bztar', 'gztar', 'msi', 'rpm', 'tar',
                   'wininst', 'xztar', 'zip', 'ztar']
        found = sorted(cmd.format_command)
        self.assertEqual(found, formats)

    def test_skip_build(self):
        # bug #10946: bdist --skip-build should trickle down to subcommands
        dist = self.create_dist()[1]
        cmd = bdist(dist)
        cmd.skip_build = 1
        cmd.ensure_finalized()
        dist.command_obj['bdist'] = cmd

        names = ['bdist_dumb', 'bdist_wininst']  # bdist_rpm does nie support --skip-build
        jeżeli os.name == 'nt':
            names.append('bdist_msi')

        dla name w names:
            subcmd = cmd.get_finalized_command(name)
            self.assertPrawda(subcmd.skip_build,
                            '%s should take --skip-build z bdist' % name)


def test_suite():
    zwróć unittest.makeSuite(BuildTestCase)

jeżeli __name__ == '__main__':
    run_unittest(test_suite())
