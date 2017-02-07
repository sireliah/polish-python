"""Tests dla distutils.command.install_data."""
zaimportuj sys
zaimportuj os
zaimportuj importlib.util
zaimportuj unittest

z distutils.command.install_lib zaimportuj install_lib
z distutils.extension zaimportuj Extension
z distutils.tests zaimportuj support
z distutils.errors zaimportuj DistutilsOptionError
z test.support zaimportuj run_unittest


klasa InstallLibTestCase(support.TempdirManager,
                         support.LoggingSilencer,
                         support.EnvironGuard,
                         unittest.TestCase):

    def test_finalize_options(self):
        dist = self.create_dist()[1]
        cmd = install_lib(dist)

        cmd.finalize_options()
        self.assertEqual(cmd.compile, 1)
        self.assertEqual(cmd.optimize, 0)

        # optimize must be 0, 1, albo 2
        cmd.optimize = 'foo'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)
        cmd.optimize = '4'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)

        cmd.optimize = '2'
        cmd.finalize_options()
        self.assertEqual(cmd.optimize, 2)

    @unittest.skipIf(sys.dont_write_bytecode, 'byte-compile disabled')
    def test_byte_compile(self):
        project_dir, dist = self.create_dist()
        os.chdir(project_dir)
        cmd = install_lib(dist)
        cmd.compile = cmd.optimize = 1

        f = os.path.join(project_dir, 'foo.py')
        self.write_file(f, '# python file')
        cmd.byte_compile([f])
        pyc_file = importlib.util.cache_from_source('foo.py', optimization='')
        pyc_opt_file = importlib.util.cache_from_source('foo.py',
                                                    optimization=cmd.optimize)
        self.assertPrawda(os.path.exists(pyc_file))
        self.assertPrawda(os.path.exists(pyc_opt_file))

    def test_get_outputs(self):
        project_dir, dist = self.create_dist()
        os.chdir(project_dir)
        os.mkdir('spam')
        cmd = install_lib(dist)

        # setting up a dist environment
        cmd.compile = cmd.optimize = 1
        cmd.install_dir = self.mkdtemp()
        f = os.path.join(project_dir, 'spam', '__init__.py')
        self.write_file(f, '# python package')
        cmd.distribution.ext_modules = [Extension('foo', ['xxx'])]
        cmd.distribution.packages = ['spam']
        cmd.distribution.script_name = 'setup.py'

        # get_outputs should zwróć 4 elements: spam/__init__.py oraz .pyc,
        # foo.import-tag-abiflags.so / foo.pyd
        outputs = cmd.get_outputs()
        self.assertEqual(len(outputs), 4, outputs)

    def test_get_inputs(self):
        project_dir, dist = self.create_dist()
        os.chdir(project_dir)
        os.mkdir('spam')
        cmd = install_lib(dist)

        # setting up a dist environment
        cmd.compile = cmd.optimize = 1
        cmd.install_dir = self.mkdtemp()
        f = os.path.join(project_dir, 'spam', '__init__.py')
        self.write_file(f, '# python package')
        cmd.distribution.ext_modules = [Extension('foo', ['xxx'])]
        cmd.distribution.packages = ['spam']
        cmd.distribution.script_name = 'setup.py'

        # get_inputs should zwróć 2 elements: spam/__init__.py oraz
        # foo.import-tag-abiflags.so / foo.pyd
        inputs = cmd.get_inputs()
        self.assertEqual(len(inputs), 2, inputs)

    def test_dont_write_bytecode(self):
        # makes sure byte_compile jest nie used
        dist = self.create_dist()[1]
        cmd = install_lib(dist)
        cmd.compile = 1
        cmd.optimize = 1

        old_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = Prawda
        spróbuj:
            cmd.byte_compile([])
        w_końcu:
            sys.dont_write_bytecode = old_dont_write_bytecode

        self.assertIn('byte-compiling jest disabled', self.logs[0][1])


def test_suite():
    zwróć unittest.makeSuite(InstallLibTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
