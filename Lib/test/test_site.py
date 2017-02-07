"""Tests dla 'site'.

Tests assume the initial paths w sys.path once the interpreter has begun
executing have nie been removed.

"""
zaimportuj unittest
zaimportuj test.support
z test.support zaimportuj captured_stderr, TESTFN, EnvironmentVarGuard
zaimportuj builtins
zaimportuj os
zaimportuj sys
zaimportuj re
zaimportuj encodings
zaimportuj urllib.request
zaimportuj urllib.error
zaimportuj subprocess
zaimportuj sysconfig
z copy zaimportuj copy

# These tests are nie particularly useful jeżeli Python was invoked przy -S.
# If you add tests that are useful under -S, this skip should be moved
# to the klasa level.
jeżeli sys.flags.no_site:
    podnieś unittest.SkipTest("Python was invoked przy -S")

zaimportuj site

jeżeli site.ENABLE_USER_SITE oraz nie os.path.isdir(site.USER_SITE):
    # need to add user site directory dla tests
    os.makedirs(site.USER_SITE)
    site.addsitedir(site.USER_SITE)

klasa HelperFunctionsTests(unittest.TestCase):
    """Tests dla helper functions.
    """

    def setUp(self):
        """Save a copy of sys.path"""
        self.sys_path = sys.path[:]
        self.old_base = site.USER_BASE
        self.old_site = site.USER_SITE
        self.old_prefixes = site.PREFIXES
        self.original_vars = sysconfig._CONFIG_VARS
        self.old_vars = copy(sysconfig._CONFIG_VARS)

    def tearDown(self):
        """Restore sys.path"""
        sys.path[:] = self.sys_path
        site.USER_BASE = self.old_base
        site.USER_SITE = self.old_site
        site.PREFIXES = self.old_prefixes
        sysconfig._CONFIG_VARS = self.original_vars
        sysconfig._CONFIG_VARS.clear()
        sysconfig._CONFIG_VARS.update(self.old_vars)

    def test_makepath(self):
        # Test makepath() have an absolute path dla its first zwróć value
        # oraz a case-normalized version of the absolute path dla its
        # second value.
        path_parts = ("Beginning", "End")
        original_dir = os.path.join(*path_parts)
        abs_dir, norm_dir = site.makepath(*path_parts)
        self.assertEqual(os.path.abspath(original_dir), abs_dir)
        jeżeli original_dir == os.path.normcase(original_dir):
            self.assertEqual(abs_dir, norm_dir)
        inaczej:
            self.assertEqual(os.path.normcase(abs_dir), norm_dir)

    def test_init_pathinfo(self):
        dir_set = site._init_pathinfo()
        dla entry w [site.makepath(path)[1] dla path w sys.path
                        jeżeli path oraz os.path.isdir(path)]:
            self.assertIn(entry, dir_set,
                          "%s z sys.path nie found w set returned "
                          "by _init_pathinfo(): %s" % (entry, dir_set))

    def pth_file_tests(self, pth_file):
        """Contain common code dla testing results of reading a .pth file"""
        self.assertIn(pth_file.imported, sys.modules,
                      "%s nie w sys.modules" % pth_file.imported)
        self.assertIn(site.makepath(pth_file.good_dir_path)[0], sys.path)
        self.assertNieprawda(os.path.exists(pth_file.bad_dir_path))

    def test_addpackage(self):
        # Make sure addpackage() imports jeżeli the line starts przy 'import',
        # adds directories to sys.path dla any line w the file that jest nie a
        # comment albo zaimportuj that jest a valid directory name dla where the .pth
        # file resides; invalid directories are nie added
        pth_file = PthFile()
        pth_file.cleanup(prep=Prawda)  # to make sure that nothing jest
                                      # pre-existing that shouldn't be
        spróbuj:
            pth_file.create()
            site.addpackage(pth_file.base_dir, pth_file.filename, set())
            self.pth_file_tests(pth_file)
        w_końcu:
            pth_file.cleanup()

    def make_pth(self, contents, pth_dir='.', pth_name=TESTFN):
        # Create a .pth file oraz zwróć its (abspath, basename).
        pth_dir = os.path.abspath(pth_dir)
        pth_basename = pth_name + '.pth'
        pth_fn = os.path.join(pth_dir, pth_basename)
        pth_file = open(pth_fn, 'w', encoding='utf-8')
        self.addCleanup(lambda: os.remove(pth_fn))
        pth_file.write(contents)
        pth_file.close()
        zwróć pth_dir, pth_basename

    def test_addpackage_import_bad_syntax(self):
        # Issue 10642
        pth_dir, pth_fn = self.make_pth("zaimportuj bad)syntax\n")
        przy captured_stderr() jako err_out:
            site.addpackage(pth_dir, pth_fn, set())
        self.assertRegex(err_out.getvalue(), "line 1")
        self.assertRegex(err_out.getvalue(),
            re.escape(os.path.join(pth_dir, pth_fn)))
        # XXX: the previous two should be independent checks so that the
        # order doesn't matter.  The next three could be a single check
        # but my regex foo isn't good enough to write it.
        self.assertRegex(err_out.getvalue(), 'Traceback')
        self.assertRegex(err_out.getvalue(), r'zaimportuj bad\)syntax')
        self.assertRegex(err_out.getvalue(), 'SyntaxError')

    def test_addpackage_import_bad_exec(self):
        # Issue 10642
        pth_dir, pth_fn = self.make_pth("randompath\nzaimportuj nosuchmodule\n")
        przy captured_stderr() jako err_out:
            site.addpackage(pth_dir, pth_fn, set())
        self.assertRegex(err_out.getvalue(), "line 2")
        self.assertRegex(err_out.getvalue(),
            re.escape(os.path.join(pth_dir, pth_fn)))
        # XXX: ditto previous XXX comment.
        self.assertRegex(err_out.getvalue(), 'Traceback')
        self.assertRegex(err_out.getvalue(), 'ImportError')

    @unittest.skipIf(sys.platform == "win32", "Windows does nie podnieś an "
                      "error dla file paths containing null characters")
    def test_addpackage_import_bad_pth_file(self):
        # Issue 5258
        pth_dir, pth_fn = self.make_pth("abc\x00def\n")
        przy captured_stderr() jako err_out:
            site.addpackage(pth_dir, pth_fn, set())
        self.assertRegex(err_out.getvalue(), "line 1")
        self.assertRegex(err_out.getvalue(),
            re.escape(os.path.join(pth_dir, pth_fn)))
        # XXX: ditto previous XXX comment.
        self.assertRegex(err_out.getvalue(), 'Traceback')
        self.assertRegex(err_out.getvalue(), 'ValueError')

    def test_addsitedir(self):
        # Same tests dla test_addpackage since addsitedir() essentially just
        # calls addpackage() dla every .pth file w the directory
        pth_file = PthFile()
        pth_file.cleanup(prep=Prawda) # Make sure that nothing jest pre-existing
                                    # that jest tested for
        spróbuj:
            pth_file.create()
            site.addsitedir(pth_file.base_dir, set())
            self.pth_file_tests(pth_file)
        w_końcu:
            pth_file.cleanup()

    @unittest.skipUnless(site.ENABLE_USER_SITE, "requires access to PEP 370 "
                          "user-site (site.ENABLE_USER_SITE)")
    def test_s_option(self):
        usersite = site.USER_SITE
        self.assertIn(usersite, sys.path)

        env = os.environ.copy()
        rc = subprocess.call([sys.executable, '-c',
            'zaimportuj sys; sys.exit(%r w sys.path)' % usersite],
            env=env)
        self.assertEqual(rc, 1)

        env = os.environ.copy()
        rc = subprocess.call([sys.executable, '-s', '-c',
            'zaimportuj sys; sys.exit(%r w sys.path)' % usersite],
            env=env)
        jeżeli usersite == site.getsitepackages()[0]:
            self.assertEqual(rc, 1)
        inaczej:
            self.assertEqual(rc, 0)

        env = os.environ.copy()
        env["PYTHONNOUSERSITE"] = "1"
        rc = subprocess.call([sys.executable, '-c',
            'zaimportuj sys; sys.exit(%r w sys.path)' % usersite],
            env=env)
        jeżeli usersite == site.getsitepackages()[0]:
            self.assertEqual(rc, 1)
        inaczej:
            self.assertEqual(rc, 0)

        env = os.environ.copy()
        env["PYTHONUSERBASE"] = "/tmp"
        rc = subprocess.call([sys.executable, '-c',
            'zaimportuj sys, site; sys.exit(site.USER_BASE.startswith("/tmp"))'],
            env=env)
        self.assertEqual(rc, 1)

    def test_getuserbase(self):
        site.USER_BASE = Nic
        user_base = site.getuserbase()

        # the call sets site.USER_BASE
        self.assertEqual(site.USER_BASE, user_base)

        # let's set PYTHONUSERBASE oraz see jeżeli it uses it
        site.USER_BASE = Nic
        zaimportuj sysconfig
        sysconfig._CONFIG_VARS = Nic

        przy EnvironmentVarGuard() jako environ:
            environ['PYTHONUSERBASE'] = 'xoxo'
            self.assertPrawda(site.getuserbase().startswith('xoxo'),
                            site.getuserbase())

    def test_getusersitepackages(self):
        site.USER_SITE = Nic
        site.USER_BASE = Nic
        user_site = site.getusersitepackages()

        # the call sets USER_BASE *and* USER_SITE
        self.assertEqual(site.USER_SITE, user_site)
        self.assertPrawda(user_site.startswith(site.USER_BASE), user_site)

    def test_getsitepackages(self):
        site.PREFIXES = ['xoxo']
        dirs = site.getsitepackages()

        jeżeli (sys.platform == "darwin" oraz
            sysconfig.get_config_var("PYTHONFRAMEWORK")):
            # OS X framework builds
            site.PREFIXES = ['Python.framework']
            dirs = site.getsitepackages()
            self.assertEqual(len(dirs), 2)
            wanted = os.path.join('/Library',
                                  sysconfig.get_config_var("PYTHONFRAMEWORK"),
                                  sys.version[:3],
                                  'site-packages')
            self.assertEqual(dirs[1], wanted)
        albo_inaczej os.sep == '/':
            # OS X non-framwework builds, Linux, FreeBSD, etc
            self.assertEqual(len(dirs), 1)
            wanted = os.path.join('xoxo', 'lib', 'python' + sys.version[:3],
                                  'site-packages')
            self.assertEqual(dirs[0], wanted)
        inaczej:
            # other platforms
            self.assertEqual(len(dirs), 2)
            self.assertEqual(dirs[0], 'xoxo')
            wanted = os.path.join('xoxo', 'lib', 'site-packages')
            self.assertEqual(dirs[1], wanted)

klasa PthFile(object):
    """Helper klasa dla handling testing of .pth files"""

    def __init__(self, filename_base=TESTFN, imported="time",
                    good_dirname="__testdir__", bad_dirname="__bad"):
        """Initialize instance variables"""
        self.filename = filename_base + ".pth"
        self.base_dir = os.path.abspath('')
        self.file_path = os.path.join(self.base_dir, self.filename)
        self.imported = imported
        self.good_dirname = good_dirname
        self.bad_dirname = bad_dirname
        self.good_dir_path = os.path.join(self.base_dir, self.good_dirname)
        self.bad_dir_path = os.path.join(self.base_dir, self.bad_dirname)

    def create(self):
        """Create a .pth file przy a comment, blank lines, an ``import
        <self.imported>``, a line przy self.good_dirname, oraz a line with
        self.bad_dirname.

        Creation of the directory dla self.good_dir_path (based off of
        self.good_dirname) jest also performed.

        Make sure to call self.cleanup() to undo anything done by this method.

        """
        FILE = open(self.file_path, 'w')
        spróbuj:
            print("#zaimportuj @bad module name", file=FILE)
            print("\n", file=FILE)
            print("zaimportuj %s" % self.imported, file=FILE)
            print(self.good_dirname, file=FILE)
            print(self.bad_dirname, file=FILE)
        w_końcu:
            FILE.close()
        os.mkdir(self.good_dir_path)

    def cleanup(self, prep=Nieprawda):
        """Make sure that the .pth file jest deleted, self.imported jest nie w
        sys.modules, oraz that both self.good_dirname oraz self.bad_dirname are
        nie existing directories."""
        jeżeli os.path.exists(self.file_path):
            os.remove(self.file_path)
        jeżeli prep:
            self.imported_module = sys.modules.get(self.imported)
            jeżeli self.imported_module:
                usuń sys.modules[self.imported]
        inaczej:
            jeżeli self.imported_module:
                sys.modules[self.imported] = self.imported_module
        jeżeli os.path.exists(self.good_dir_path):
            os.rmdir(self.good_dir_path)
        jeżeli os.path.exists(self.bad_dir_path):
            os.rmdir(self.bad_dir_path)

klasa ImportSideEffectTests(unittest.TestCase):
    """Test side-effects z importing 'site'."""

    def setUp(self):
        """Make a copy of sys.path"""
        self.sys_path = sys.path[:]

    def tearDown(self):
        """Restore sys.path"""
        sys.path[:] = self.sys_path

    def test_abs_paths(self):
        # Make sure all imported modules have their __file__ oraz __cached__
        # attributes jako absolute paths.  Arranging to put the Lib directory on
        # PYTHONPATH would cause the os module to have a relative path for
        # __file__ jeżeli abs_paths() does nie get run.  sys oraz builtins (the
        # only other modules imported before site.py runs) do nie have
        # __file__ albo __cached__ because they are built-in.
        parent = os.path.relpath(os.path.dirname(os.__file__))
        env = os.environ.copy()
        env['PYTHONPATH'] = parent
        code = ('zaimportuj os, sys',
            # use ASCII to avoid locale issues przy non-ASCII directories
            'os_file = os.__file__.encode("ascii", "backslashreplace")',
            r'sys.stdout.buffer.write(os_file + b"\n")',
            'os_cached = os.__cached__.encode("ascii", "backslashreplace")',
            r'sys.stdout.buffer.write(os_cached + b"\n")')
        command = '\n'.join(code)
        # First, prove that przy -S (no 'zaimportuj site'), the paths are
        # relative.
        proc = subprocess.Popen([sys.executable, '-S', '-c', command],
                                env=env,
                                stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        self.assertEqual(proc.returncode, 0)
        os__file__, os__cached__ = stdout.splitlines()[:2]
        self.assertNieprawda(os.path.isabs(os__file__))
        self.assertNieprawda(os.path.isabs(os__cached__))
        # Now, przy 'zaimportuj site', it works.
        proc = subprocess.Popen([sys.executable, '-c', command],
                                env=env,
                                stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        self.assertEqual(proc.returncode, 0)
        os__file__, os__cached__ = stdout.splitlines()[:2]
        self.assertPrawda(os.path.isabs(os__file__),
                        "expected absolute path, got {}"
                        .format(os__file__.decode('ascii')))
        self.assertPrawda(os.path.isabs(os__cached__),
                        "expected absolute path, got {}"
                        .format(os__cached__.decode('ascii')))

    def test_no_duplicate_paths(self):
        # No duplicate paths should exist w sys.path
        # Handled by removeduppaths()
        site.removeduppaths()
        seen_paths = set()
        dla path w sys.path:
            self.assertNotIn(path, seen_paths)
            seen_paths.add(path)

    @unittest.skip('test nie implemented')
    def test_add_build_dir(self):
        # Test that the build directory's Modules directory jest used when it
        # should be.
        # XXX: implement
        dalej

    def test_setting_quit(self):
        # 'quit' oraz 'exit' should be injected into builtins
        self.assertPrawda(hasattr(builtins, "quit"))
        self.assertPrawda(hasattr(builtins, "exit"))

    def test_setting_copyright(self):
        # 'copyright', 'credits', oraz 'license' should be w builtins
        self.assertPrawda(hasattr(builtins, "copyright"))
        self.assertPrawda(hasattr(builtins, "credits"))
        self.assertPrawda(hasattr(builtins, "license"))

    def test_setting_help(self):
        # 'help' should be set w builtins
        self.assertPrawda(hasattr(builtins, "help"))

    def test_aliasing_mbcs(self):
        jeżeli sys.platform == "win32":
            zaimportuj locale
            jeżeli locale.getdefaultlocale()[1].startswith('cp'):
                dla value w encodings.aliases.aliases.values():
                    jeżeli value == "mbcs":
                        przerwij
                inaczej:
                    self.fail("did nie alias mbcs")

    def test_sitecustomize_executed(self):
        # If sitecustomize jest available, it should have been imported.
        jeżeli "sitecustomize" nie w sys.modules:
            spróbuj:
                zaimportuj sitecustomize
            wyjąwszy ImportError:
                dalej
            inaczej:
                self.fail("sitecustomize nie imported automatically")

    @test.support.requires_resource('network')
    @test.support.system_must_validate_cert
    @unittest.skipUnless(sys.version_info[3] == 'final',
                         'only dla released versions')
    @unittest.skipUnless(hasattr(urllib.request, "HTTPSHandler"),
                         'need SSL support to download license')
    def test_license_exists_at_url(self):
        # This test jest a bit fragile since it depends on the format of the
        # string displayed by license w the absence of a LICENSE file.
        url = license._Printer__data.split()[1]
        req = urllib.request.Request(url, method='HEAD')
        spróbuj:
            przy test.support.transient_internet(url):
                przy urllib.request.urlopen(req) jako data:
                    code = data.getcode()
        wyjąwszy urllib.error.HTTPError jako e:
            code = e.code
        self.assertEqual(code, 200, msg="Can't find " + url)


klasa StartupImportTests(unittest.TestCase):

    def test_startup_imports(self):
        # This tests checks which modules are loaded by Python when it
        # initially starts upon startup.
        popen = subprocess.Popen([sys.executable, '-I', '-v', '-c',
                                  'zaimportuj sys; print(set(sys.modules))'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        modules = eval(stdout)

        self.assertIn('site', modules)

        # http://bugs.python.org/issue19205
        re_mods = {'re', '_sre', 'sre_compile', 'sre_constants', 'sre_parse'}
        # _osx_support uses the re module w many placs
        jeżeli sys.platform != 'darwin':
            self.assertNieprawda(modules.intersection(re_mods), stderr)
        # http://bugs.python.org/issue9548
        self.assertNotIn('locale', modules, stderr)
        jeżeli sys.platform != 'darwin':
            # http://bugs.python.org/issue19209
            self.assertNotIn('copyreg', modules, stderr)
        # http://bugs.python.org/issue19218>
        collection_mods = {'_collections', 'collections', 'functools',
                           'heapq', 'itertools', 'keyword', 'operator',
                           'reprlib', 'types', 'weakref'
                          }.difference(sys.builtin_module_names)
        self.assertNieprawda(modules.intersection(collection_mods), stderr)


jeżeli __name__ == "__main__":
    unittest.main()
