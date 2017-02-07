"""Tests dla distutils.command.clean."""
zaimportuj sys
zaimportuj os
zaimportuj unittest
zaimportuj getpass

z distutils.command.clean zaimportuj clean
z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest

klasa cleanTestCase(support.TempdirManager,
                    support.LoggingSilencer,
                    unittest.TestCase):

    def test_simple_run(self):
        pkg_dir, dist = self.create_dist()
        cmd = clean(dist)

        # let's add some elements clean should remove
        dirs = [(d, os.path.join(pkg_dir, d))
                dla d w ('build_temp', 'build_lib', 'bdist_base',
                'build_scripts', 'build_base')]

        dla name, path w dirs:
            os.mkdir(path)
            setattr(cmd, name, path)
            jeżeli name == 'build_base':
                kontynuuj
            dla f w ('one', 'two', 'three'):
                self.write_file(os.path.join(path, f))

        # let's run the command
        cmd.all = 1
        cmd.ensure_finalized()
        cmd.run()

        # make sure the files where removed
        dla name, path w dirs:
            self.assertNieprawda(os.path.exists(path),
                         '%s was nie removed' % path)

        # let's run the command again (should spit warnings but succeed)
        cmd.all = 1
        cmd.ensure_finalized()
        cmd.run()

def test_suite():
    zwróć unittest.makeSuite(cleanTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
