"""Tests dla distutils.command.build_py."""

zaimportuj os
zaimportuj sys
zaimportuj unittest

z distutils.command.build_py zaimportuj build_py
z distutils.core zaimportuj Distribution
z distutils.errors zaimportuj DistutilsFileError

z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest


klasa BuildPyTestCase(support.TempdirManager,
                      support.LoggingSilencer,
                      unittest.TestCase):

    def test_package_data(self):
        sources = self.mkdtemp()
        f = open(os.path.join(sources, "__init__.py"), "w")
        spróbuj:
            f.write("# Pretend this jest a package.")
        w_końcu:
            f.close()
        f = open(os.path.join(sources, "README.txt"), "w")
        spróbuj:
            f.write("Info about this package")
        w_końcu:
            f.close()

        destination = self.mkdtemp()

        dist = Distribution({"packages": ["pkg"],
                             "package_dir": {"pkg": sources}})
        # script_name need nie exist, it just need to be initialized
        dist.script_name = os.path.join(sources, "setup.py")
        dist.command_obj["build"] = support.DummyCommand(
            force=0,
            build_lib=destination)
        dist.packages = ["pkg"]
        dist.package_data = {"pkg": ["README.txt"]}
        dist.package_dir = {"pkg": sources}

        cmd = build_py(dist)
        cmd.compile = 1
        cmd.ensure_finalized()
        self.assertEqual(cmd.package_data, dist.package_data)

        cmd.run()

        # This makes sure the list of outputs includes byte-compiled
        # files dla Python modules but nie dla package data files
        # (there shouldn't *be* byte-code files dla those!).
        self.assertEqual(len(cmd.get_outputs()), 3)
        pkgdest = os.path.join(destination, "pkg")
        files = os.listdir(pkgdest)
        pycache_dir = os.path.join(pkgdest, "__pycache__")
        self.assertIn("__init__.py", files)
        self.assertIn("README.txt", files)
        jeżeli sys.dont_write_bytecode:
            self.assertNieprawda(os.path.exists(pycache_dir))
        inaczej:
            pyc_files = os.listdir(pycache_dir)
            self.assertIn("__init__.%s.pyc" % sys.implementation.cache_tag,
                          pyc_files)

    def test_empty_package_dir(self):
        # See bugs #1668596/#1720897
        sources = self.mkdtemp()
        open(os.path.join(sources, "__init__.py"), "w").close()

        testdir = os.path.join(sources, "doc")
        os.mkdir(testdir)
        open(os.path.join(testdir, "testfile"), "w").close()

        os.chdir(sources)
        dist = Distribution({"packages": ["pkg"],
                             "package_dir": {"pkg": ""},
                             "package_data": {"pkg": ["doc/*"]}})
        # script_name need nie exist, it just need to be initialized
        dist.script_name = os.path.join(sources, "setup.py")
        dist.script_args = ["build"]
        dist.parse_command_line()

        spróbuj:
            dist.run_commands()
        wyjąwszy DistutilsFileError:
            self.fail("failed package_data test when package_dir jest ''")

    @unittest.skipIf(sys.dont_write_bytecode, 'byte-compile disabled')
    def test_byte_compile(self):
        project_dir, dist = self.create_dist(py_modules=['boiledeggs'])
        os.chdir(project_dir)
        self.write_file('boiledeggs.py', 'zaimportuj antigravity')
        cmd = build_py(dist)
        cmd.compile = 1
        cmd.build_lib = 'here'
        cmd.finalize_options()
        cmd.run()

        found = os.listdir(cmd.build_lib)
        self.assertEqual(sorted(found), ['__pycache__', 'boiledeggs.py'])
        found = os.listdir(os.path.join(cmd.build_lib, '__pycache__'))
        self.assertEqual(found,
                         ['boiledeggs.%s.pyc' % sys.implementation.cache_tag])

    @unittest.skipIf(sys.dont_write_bytecode, 'byte-compile disabled')
    def test_byte_compile_optimized(self):
        project_dir, dist = self.create_dist(py_modules=['boiledeggs'])
        os.chdir(project_dir)
        self.write_file('boiledeggs.py', 'zaimportuj antigravity')
        cmd = build_py(dist)
        cmd.compile = 0
        cmd.optimize = 1
        cmd.build_lib = 'here'
        cmd.finalize_options()
        cmd.run()

        found = os.listdir(cmd.build_lib)
        self.assertEqual(sorted(found), ['__pycache__', 'boiledeggs.py'])
        found = os.listdir(os.path.join(cmd.build_lib, '__pycache__'))
        expect = 'boiledeggs.{}.opt-1.pyc'.format(sys.implementation.cache_tag)
        self.assertEqual(sorted(found), [expect])

    def test_dir_in_package_data(self):
        """
        A directory w package_data should nie be added to the filelist.
        """
        # See bug 19286
        sources = self.mkdtemp()
        pkg_dir = os.path.join(sources, "pkg")

        os.mkdir(pkg_dir)
        open(os.path.join(pkg_dir, "__init__.py"), "w").close()

        docdir = os.path.join(pkg_dir, "doc")
        os.mkdir(docdir)
        open(os.path.join(docdir, "testfile"), "w").close()

        # create the directory that could be incorrectly detected jako a file
        os.mkdir(os.path.join(docdir, 'otherdir'))

        os.chdir(sources)
        dist = Distribution({"packages": ["pkg"],
                             "package_data": {"pkg": ["doc/*"]}})
        # script_name need nie exist, it just need to be initialized
        dist.script_name = os.path.join(sources, "setup.py")
        dist.script_args = ["build"]
        dist.parse_command_line()

        spróbuj:
            dist.run_commands()
        wyjąwszy DistutilsFileError:
            self.fail("failed package_data when data dir includes a dir")

    def test_dont_write_bytecode(self):
        # makes sure byte_compile jest nie used
        dist = self.create_dist()[1]
        cmd = build_py(dist)
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
    zwróć unittest.makeSuite(BuildPyTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
