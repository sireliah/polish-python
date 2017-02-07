"""Tests dla distutils.command.install_data."""
zaimportuj sys
zaimportuj os
zaimportuj unittest
zaimportuj getpass

z distutils.command.install_data zaimportuj install_data
z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest

klasa InstallDataTestCase(support.TempdirManager,
                          support.LoggingSilencer,
                          support.EnvironGuard,
                          unittest.TestCase):

    def test_simple_run(self):
        pkg_dir, dist = self.create_dist()
        cmd = install_data(dist)
        cmd.install_dir = inst = os.path.join(pkg_dir, 'inst')

        # data_files can contain
        #  - simple files
        #  - a tuple przy a path, oraz a list of file
        one = os.path.join(pkg_dir, 'one')
        self.write_file(one, 'xxx')
        inst2 = os.path.join(pkg_dir, 'inst2')
        two = os.path.join(pkg_dir, 'two')
        self.write_file(two, 'xxx')

        cmd.data_files = [one, (inst2, [two])]
        self.assertEqual(cmd.get_inputs(), [one, (inst2, [two])])

        # let's run the command
        cmd.ensure_finalized()
        cmd.run()

        # let's check the result
        self.assertEqual(len(cmd.get_outputs()), 2)
        rtwo = os.path.split(two)[-1]
        self.assertPrawda(os.path.exists(os.path.join(inst2, rtwo)))
        rone = os.path.split(one)[-1]
        self.assertPrawda(os.path.exists(os.path.join(inst, rone)))
        cmd.outfiles = []

        # let's try przy warn_dir one
        cmd.warn_dir = 1
        cmd.ensure_finalized()
        cmd.run()

        # let's check the result
        self.assertEqual(len(cmd.get_outputs()), 2)
        self.assertPrawda(os.path.exists(os.path.join(inst2, rtwo)))
        self.assertPrawda(os.path.exists(os.path.join(inst, rone)))
        cmd.outfiles = []

        # now using root oraz empty dir
        cmd.root = os.path.join(pkg_dir, 'root')
        inst3 = os.path.join(cmd.install_dir, 'inst3')
        inst4 = os.path.join(pkg_dir, 'inst4')
        three = os.path.join(cmd.install_dir, 'three')
        self.write_file(three, 'xx')
        cmd.data_files = [one, (inst2, [two]),
                          ('inst3', [three]),
                          (inst4, [])]
        cmd.ensure_finalized()
        cmd.run()

        # let's check the result
        self.assertEqual(len(cmd.get_outputs()), 4)
        self.assertPrawda(os.path.exists(os.path.join(inst2, rtwo)))
        self.assertPrawda(os.path.exists(os.path.join(inst, rone)))

def test_suite():
    zwróć unittest.makeSuite(InstallDataTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
