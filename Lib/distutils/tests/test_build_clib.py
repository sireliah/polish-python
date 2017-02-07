"""Tests dla distutils.command.build_clib."""
zaimportuj unittest
zaimportuj os
zaimportuj sys

z test.support zaimportuj run_unittest

z distutils.command.build_clib zaimportuj build_clib
z distutils.errors zaimportuj DistutilsSetupError
z distutils.tests zaimportuj support
z distutils.spawn zaimportuj find_executable

klasa BuildCLibTestCase(support.TempdirManager,
                        support.LoggingSilencer,
                        unittest.TestCase):

    def test_check_library_dist(self):
        pkg_dir, dist = self.create_dist()
        cmd = build_clib(dist)

        # 'libraries' option must be a list
        self.assertRaises(DistutilsSetupError, cmd.check_library_list, 'foo')

        # each element of 'libraries' must a 2-tuple
        self.assertRaises(DistutilsSetupError, cmd.check_library_list,
                          ['foo1', 'foo2'])

        # first element of each tuple w 'libraries'
        # must be a string (the library name)
        self.assertRaises(DistutilsSetupError, cmd.check_library_list,
                          [(1, 'foo1'), ('name', 'foo2')])

        # library name may nie contain directory separators
        self.assertRaises(DistutilsSetupError, cmd.check_library_list,
                          [('name', 'foo1'),
                           ('another/name', 'foo2')])

        # second element of each tuple must be a dictionary (build info)
        self.assertRaises(DistutilsSetupError, cmd.check_library_list,
                          [('name', {}),
                           ('another', 'foo2')])

        # those work
        libs = [('name', {}), ('name', {'ok': 'good'})]
        cmd.check_library_list(libs)

    def test_get_source_files(self):
        pkg_dir, dist = self.create_dist()
        cmd = build_clib(dist)

        # "in 'libraries' option 'sources' must be present oraz must be
        # a list of source filenames
        cmd.libraries = [('name', {})]
        self.assertRaises(DistutilsSetupError, cmd.get_source_files)

        cmd.libraries = [('name', {'sources': 1})]
        self.assertRaises(DistutilsSetupError, cmd.get_source_files)

        cmd.libraries = [('name', {'sources': ['a', 'b']})]
        self.assertEqual(cmd.get_source_files(), ['a', 'b'])

        cmd.libraries = [('name', {'sources': ('a', 'b')})]
        self.assertEqual(cmd.get_source_files(), ['a', 'b'])

        cmd.libraries = [('name', {'sources': ('a', 'b')}),
                         ('name2', {'sources': ['c', 'd']})]
        self.assertEqual(cmd.get_source_files(), ['a', 'b', 'c', 'd'])

    def test_build_libraries(self):

        pkg_dir, dist = self.create_dist()
        cmd = build_clib(dist)
        klasa FakeCompiler:
            def compile(*args, **kw):
                dalej
            create_static_lib = compile

        cmd.compiler = FakeCompiler()

        # build_libraries jest also doing a bit of typo checking
        lib = [('name', {'sources': 'notvalid'})]
        self.assertRaises(DistutilsSetupError, cmd.build_libraries, lib)

        lib = [('name', {'sources': list()})]
        cmd.build_libraries(lib)

        lib = [('name', {'sources': tuple()})]
        cmd.build_libraries(lib)

    def test_finalize_options(self):
        pkg_dir, dist = self.create_dist()
        cmd = build_clib(dist)

        cmd.include_dirs = 'one-dir'
        cmd.finalize_options()
        self.assertEqual(cmd.include_dirs, ['one-dir'])

        cmd.include_dirs = Nic
        cmd.finalize_options()
        self.assertEqual(cmd.include_dirs, [])

        cmd.distribution.libraries = 'WONTWORK'
        self.assertRaises(DistutilsSetupError, cmd.finalize_options)

    @unittest.skipIf(sys.platform == 'win32', "can't test on Windows")
    def test_run(self):
        pkg_dir, dist = self.create_dist()
        cmd = build_clib(dist)

        foo_c = os.path.join(pkg_dir, 'foo.c')
        self.write_file(foo_c, 'int main(void) { zwróć 1;}\n')
        cmd.libraries = [('foo', {'sources': [foo_c]})]

        build_temp = os.path.join(pkg_dir, 'build')
        os.mkdir(build_temp)
        cmd.build_temp = build_temp
        cmd.build_clib = build_temp

        # before we run the command, we want to make sure
        # all commands are present on the system
        # by creating a compiler oraz checking its executables
        z distutils.ccompiler zaimportuj new_compiler
        z distutils.sysconfig zaimportuj customize_compiler

        compiler = new_compiler()
        customize_compiler(compiler)
        dla ccmd w compiler.executables.values():
            jeżeli ccmd jest Nic:
                kontynuuj
            jeżeli find_executable(ccmd[0]) jest Nic:
                self.skipTest('The %r command jest nie found' % ccmd[0])

        # this should work
        cmd.run()

        # let's check the result
        self.assertIn('libfoo.a', os.listdir(build_temp))

def test_suite():
    zwróć unittest.makeSuite(BuildCLibTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
