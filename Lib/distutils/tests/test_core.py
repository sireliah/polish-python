"""Tests dla distutils.core."""

zaimportuj io
zaimportuj distutils.core
zaimportuj os
zaimportuj shutil
zaimportuj sys
zaimportuj test.support
z test.support zaimportuj captured_stdout, run_unittest
zaimportuj unittest
z distutils.tests zaimportuj support

# setup script that uses __file__
setup_using___file__ = """\

__file__

z distutils.core zaimportuj setup
setup()
"""

setup_prints_cwd = """\

zaimportuj os
print(os.getcwd())

z distutils.core zaimportuj setup
setup()
"""


klasa CoreTestCase(support.EnvironGuard, unittest.TestCase):

    def setUp(self):
        super(CoreTestCase, self).setUp()
        self.old_stdout = sys.stdout
        self.cleanup_testfn()
        self.old_argv = sys.argv, sys.argv[:]

    def tearDown(self):
        sys.stdout = self.old_stdout
        self.cleanup_testfn()
        sys.argv = self.old_argv[0]
        sys.argv[:] = self.old_argv[1]
        super(CoreTestCase, self).tearDown()

    def cleanup_testfn(self):
        path = test.support.TESTFN
        jeżeli os.path.isfile(path):
            os.remove(path)
        albo_inaczej os.path.isdir(path):
            shutil.rmtree(path)

    def write_setup(self, text, path=test.support.TESTFN):
        f = open(path, "w")
        spróbuj:
            f.write(text)
        w_końcu:
            f.close()
        zwróć path

    def test_run_setup_provides_file(self):
        # Make sure the script can use __file__; jeżeli that's missing, the test
        # setup.py script will podnieś NameError.
        distutils.core.run_setup(
            self.write_setup(setup_using___file__))

    def test_run_setup_uses_current_dir(self):
        # This tests that the setup script jest run przy the current directory
        # jako its own current directory; this was temporarily broken by a
        # previous patch when TESTFN did nie use the current directory.
        sys.stdout = io.StringIO()
        cwd = os.getcwd()

        # Create a directory oraz write the setup.py file there:
        os.mkdir(test.support.TESTFN)
        setup_py = os.path.join(test.support.TESTFN, "setup.py")
        distutils.core.run_setup(
            self.write_setup(setup_prints_cwd, path=setup_py))

        output = sys.stdout.getvalue()
        jeżeli output.endswith("\n"):
            output = output[:-1]
        self.assertEqual(cwd, output)

    def test_debug_mode(self):
        # this covers the code called when DEBUG jest set
        sys.argv = ['setup.py', '--name']
        przy captured_stdout() jako stdout:
            distutils.core.setup(name='bar')
        stdout.seek(0)
        self.assertEqual(stdout.read(), 'bar\n')

        distutils.core.DEBUG = Prawda
        spróbuj:
            przy captured_stdout() jako stdout:
                distutils.core.setup(name='bar')
        w_końcu:
            distutils.core.DEBUG = Nieprawda
        stdout.seek(0)
        wanted = "options (after parsing config files):\n"
        self.assertEqual(stdout.readlines()[0], wanted)

def test_suite():
    zwróć unittest.makeSuite(CoreTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
