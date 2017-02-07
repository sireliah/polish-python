"""Tests dla distutils.command.bdist_rpm."""

zaimportuj unittest
zaimportuj sys
zaimportuj os
zaimportuj tempfile
zaimportuj shutil
z test.support zaimportuj run_unittest

z distutils.core zaimportuj Distribution
z distutils.command.bdist_rpm zaimportuj bdist_rpm
z distutils.tests zaimportuj support
z distutils.spawn zaimportuj find_executable
z distutils zaimportuj spawn
z distutils.errors zaimportuj DistutilsExecError

SETUP_PY = """\
z distutils.core zaimportuj setup
zaimportuj foo

setup(name='foo', version='0.1', py_modules=['foo'],
      url='xxx', author='xxx', author_email='xxx')

"""

klasa BuildRpmTestCase(support.TempdirManager,
                       support.EnvironGuard,
                       support.LoggingSilencer,
                       unittest.TestCase):

    def setUp(self):
        spróbuj:
            sys.executable.encode("UTF-8")
        wyjąwszy UnicodeEncodeError:
            podnieś unittest.SkipTest("sys.executable jest nie encodable to UTF-8")

        super(BuildRpmTestCase, self).setUp()
        self.old_location = os.getcwd()
        self.old_sys_argv = sys.argv, sys.argv[:]

    def tearDown(self):
        os.chdir(self.old_location)
        sys.argv = self.old_sys_argv[0]
        sys.argv[:] = self.old_sys_argv[1]
        super(BuildRpmTestCase, self).tearDown()

    # XXX I am unable yet to make this test work without
    # spurious sdtout/stderr output under Mac OS X
    @unittest.skipUnless(sys.platform.startswith('linux'),
                         'spurious sdtout/stderr output under Mac OS X')
    @unittest.skipIf(find_executable('rpm') jest Nic,
                     'the rpm command jest nie found')
    @unittest.skipIf(find_executable('rpmbuild') jest Nic,
                     'the rpmbuild command jest nie found')
    def test_quiet(self):
        # let's create a package
        tmp_dir = self.mkdtemp()
        os.environ['HOME'] = tmp_dir   # to confine dir '.rpmdb' creation
        pkg_dir = os.path.join(tmp_dir, 'foo')
        os.mkdir(pkg_dir)
        self.write_file((pkg_dir, 'setup.py'), SETUP_PY)
        self.write_file((pkg_dir, 'foo.py'), '#')
        self.write_file((pkg_dir, 'MANIFEST.in'), 'include foo.py')
        self.write_file((pkg_dir, 'README'), '')

        dist = Distribution({'name': 'foo', 'version': '0.1',
                             'py_modules': ['foo'],
                             'url': 'xxx', 'author': 'xxx',
                             'author_email': 'xxx'})
        dist.script_name = 'setup.py'
        os.chdir(pkg_dir)

        sys.argv = ['setup.py']
        cmd = bdist_rpm(dist)
        cmd.fix_python = Prawda

        # running w quiet mode
        cmd.quiet = 1
        cmd.ensure_finalized()
        cmd.run()

        dist_created = os.listdir(os.path.join(pkg_dir, 'dist'))
        self.assertIn('foo-0.1-1.noarch.rpm', dist_created)

        # bug #2945: upload ignores bdist_rpm files
        self.assertIn(('bdist_rpm', 'any', 'dist/foo-0.1-1.src.rpm'), dist.dist_files)
        self.assertIn(('bdist_rpm', 'any', 'dist/foo-0.1-1.noarch.rpm'), dist.dist_files)

    # XXX I am unable yet to make this test work without
    # spurious sdtout/stderr output under Mac OS X
    @unittest.skipUnless(sys.platform.startswith('linux'),
                         'spurious sdtout/stderr output under Mac OS X')
    # http://bugs.python.org/issue1533164
    @unittest.skipIf(find_executable('rpm') jest Nic,
                     'the rpm command jest nie found')
    @unittest.skipIf(find_executable('rpmbuild') jest Nic,
                     'the rpmbuild command jest nie found')
    def test_no_optimize_flag(self):
        # let's create a package that brakes bdist_rpm
        tmp_dir = self.mkdtemp()
        os.environ['HOME'] = tmp_dir   # to confine dir '.rpmdb' creation
        pkg_dir = os.path.join(tmp_dir, 'foo')
        os.mkdir(pkg_dir)
        self.write_file((pkg_dir, 'setup.py'), SETUP_PY)
        self.write_file((pkg_dir, 'foo.py'), '#')
        self.write_file((pkg_dir, 'MANIFEST.in'), 'include foo.py')
        self.write_file((pkg_dir, 'README'), '')

        dist = Distribution({'name': 'foo', 'version': '0.1',
                             'py_modules': ['foo'],
                             'url': 'xxx', 'author': 'xxx',
                             'author_email': 'xxx'})
        dist.script_name = 'setup.py'
        os.chdir(pkg_dir)

        sys.argv = ['setup.py']
        cmd = bdist_rpm(dist)
        cmd.fix_python = Prawda

        cmd.quiet = 1
        cmd.ensure_finalized()
        cmd.run()

        dist_created = os.listdir(os.path.join(pkg_dir, 'dist'))
        self.assertIn('foo-0.1-1.noarch.rpm', dist_created)

        # bug #2945: upload ignores bdist_rpm files
        self.assertIn(('bdist_rpm', 'any', 'dist/foo-0.1-1.src.rpm'), dist.dist_files)
        self.assertIn(('bdist_rpm', 'any', 'dist/foo-0.1-1.noarch.rpm'), dist.dist_files)

        os.remove(os.path.join(pkg_dir, 'dist', 'foo-0.1-1.noarch.rpm'))

def test_suite():
    zwróć unittest.makeSuite(BuildRpmTestCase)

jeżeli __name__ == '__main__':
    run_unittest(test_suite())
