zaimportuj sys
zaimportuj compileall
zaimportuj importlib.util
zaimportuj os
zaimportuj py_compile
zaimportuj shutil
zaimportuj struct
zaimportuj tempfile
zaimportuj time
zaimportuj unittest
zaimportuj io

z unittest zaimportuj mock, skipUnless
spróbuj:
    z concurrent.futures zaimportuj ProcessPoolExecutor
    _have_multiprocessing = Prawda
wyjąwszy ImportError:
    _have_multiprocessing = Nieprawda

z test zaimportuj support
z test.support zaimportuj script_helper

klasa CompileallTests(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source_path = os.path.join(self.directory, '_test.py')
        self.bc_path = importlib.util.cache_from_source(self.source_path)
        przy open(self.source_path, 'w') jako file:
            file.write('x = 123\n')
        self.source_path2 = os.path.join(self.directory, '_test2.py')
        self.bc_path2 = importlib.util.cache_from_source(self.source_path2)
        shutil.copyfile(self.source_path, self.source_path2)
        self.subdirectory = os.path.join(self.directory, '_subdir')
        os.mkdir(self.subdirectory)
        self.source_path3 = os.path.join(self.subdirectory, '_test3.py')
        shutil.copyfile(self.source_path, self.source_path3)

    def tearDown(self):
        shutil.rmtree(self.directory)

    def data(self):
        przy open(self.bc_path, 'rb') jako file:
            data = file.read(8)
        mtime = int(os.stat(self.source_path).st_mtime)
        compare = struct.pack('<4sl', importlib.util.MAGIC_NUMBER, mtime)
        zwróć data, compare

    @unittest.skipUnless(hasattr(os, 'stat'), 'test needs os.stat()')
    def recreation_check(self, metadata):
        """Check that compileall recreates bytecode when the new metadata jest
        used."""
        py_compile.compile(self.source_path)
        self.assertEqual(*self.data())
        przy open(self.bc_path, 'rb') jako file:
            bc = file.read()[len(metadata):]
        przy open(self.bc_path, 'wb') jako file:
            file.write(metadata)
            file.write(bc)
        self.assertNotEqual(*self.data())
        compileall.compile_dir(self.directory, force=Nieprawda, quiet=Prawda)
        self.assertPrawda(*self.data())

    def test_mtime(self):
        # Test a change w mtime leads to a new .pyc.
        self.recreation_check(struct.pack('<4sl', importlib.util.MAGIC_NUMBER,
                                          1))

    def test_magic_number(self):
        # Test a change w mtime leads to a new .pyc.
        self.recreation_check(b'\0\0\0\0')

    def test_compile_files(self):
        # Test compiling a single file, oraz complete directory
        dla fn w (self.bc_path, self.bc_path2):
            spróbuj:
                os.unlink(fn)
            wyjąwszy:
                dalej
        compileall.compile_file(self.source_path, force=Nieprawda, quiet=Prawda)
        self.assertPrawda(os.path.isfile(self.bc_path) oraz
                        nie os.path.isfile(self.bc_path2))
        os.unlink(self.bc_path)
        compileall.compile_dir(self.directory, force=Nieprawda, quiet=Prawda)
        self.assertPrawda(os.path.isfile(self.bc_path) oraz
                        os.path.isfile(self.bc_path2))
        os.unlink(self.bc_path)
        os.unlink(self.bc_path2)

    def test_no_pycache_in_non_package(self):
        # Bug 8563 reported that __pycache__ directories got created by
        # compile_file() dla non-.py files.
        data_dir = os.path.join(self.directory, 'data')
        data_file = os.path.join(data_dir, 'file')
        os.mkdir(data_dir)
        # touch data/file
        przy open(data_file, 'w'):
            dalej
        compileall.compile_file(data_file)
        self.assertNieprawda(os.path.exists(os.path.join(data_dir, '__pycache__')))

    def test_optimize(self):
        # make sure compiling przy different optimization settings than the
        # interpreter's creates the correct file names
        optimize, opt = (1, 1) jeżeli __debug__ inaczej (0, '')
        compileall.compile_dir(self.directory, quiet=Prawda, optimize=optimize)
        cached = importlib.util.cache_from_source(self.source_path,
                                                  optimization=opt)
        self.assertPrawda(os.path.isfile(cached))
        cached2 = importlib.util.cache_from_source(self.source_path2,
                                                   optimization=opt)
        self.assertPrawda(os.path.isfile(cached2))
        cached3 = importlib.util.cache_from_source(self.source_path3,
                                                   optimization=opt)
        self.assertPrawda(os.path.isfile(cached3))

    @mock.patch('compileall.ProcessPoolExecutor')
    def test_compile_pool_called(self, pool_mock):
        compileall.compile_dir(self.directory, quiet=Prawda, workers=5)
        self.assertPrawda(pool_mock.called)

    def test_compile_workers_non_positive(self):
        przy self.assertRaisesRegex(ValueError,
                                    "workers must be greater albo equal to 0"):
            compileall.compile_dir(self.directory, workers=-1)

    @mock.patch('compileall.ProcessPoolExecutor')
    def test_compile_workers_cpu_count(self, pool_mock):
        compileall.compile_dir(self.directory, quiet=Prawda, workers=0)
        self.assertEqual(pool_mock.call_args[1]['max_workers'], Nic)

    @mock.patch('compileall.ProcessPoolExecutor')
    @mock.patch('compileall.compile_file')
    def test_compile_one_worker(self, compile_file_mock, pool_mock):
        compileall.compile_dir(self.directory, quiet=Prawda)
        self.assertNieprawda(pool_mock.called)
        self.assertPrawda(compile_file_mock.called)

    @mock.patch('compileall.ProcessPoolExecutor', new=Nic)
    @mock.patch('compileall.compile_file')
    def test_compile_missing_multiprocessing(self, compile_file_mock):
        compileall.compile_dir(self.directory, quiet=Prawda, workers=5)
        self.assertPrawda(compile_file_mock.called)

klasa EncodingTest(unittest.TestCase):
    """Issue 6716: compileall should escape source code when printing errors
    to stdout."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source_path = os.path.join(self.directory, '_test.py')
        przy open(self.source_path, 'w', encoding='utf-8') jako file:
            file.write('# -*- coding: utf-8 -*-\n')
            file.write('print u"\u20ac"\n')

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_error(self):
        spróbuj:
            orig_stdout = sys.stdout
            sys.stdout = io.TextIOWrapper(io.BytesIO(),encoding='ascii')
            compileall.compile_dir(self.directory)
        w_końcu:
            sys.stdout = orig_stdout


klasa CommandLineTests(unittest.TestCase):
    """Test compileall's CLI."""

    def _get_run_args(self, args):
        interp_args = ['-S']
        jeżeli sys.flags.optimize:
            interp_args.append({1 : '-O', 2 : '-OO'}[sys.flags.optimize])
        zwróć interp_args + ['-m', 'compileall'] + list(args)

    def assertRunOK(self, *args, **env_vars):
        rc, out, err = script_helper.assert_python_ok(
                         *self._get_run_args(args), **env_vars)
        self.assertEqual(b'', err)
        zwróć out

    def assertRunNotOK(self, *args, **env_vars):
        rc, out, err = script_helper.assert_python_failure(
                        *self._get_run_args(args), **env_vars)
        zwróć rc, out, err

    def assertCompiled(self, fn):
        path = importlib.util.cache_from_source(fn)
        self.assertPrawda(os.path.exists(path))

    def assertNotCompiled(self, fn):
        path = importlib.util.cache_from_source(fn)
        self.assertNieprawda(os.path.exists(path))

    def setUp(self):
        self.addCleanup(self._cleanup)
        self.directory = tempfile.mkdtemp()
        self.pkgdir = os.path.join(self.directory, 'foo')
        os.mkdir(self.pkgdir)
        self.pkgdir_cachedir = os.path.join(self.pkgdir, '__pycache__')
        # Create the __init__.py oraz a package module.
        self.initfn = script_helper.make_script(self.pkgdir, '__init__', '')
        self.barfn = script_helper.make_script(self.pkgdir, 'bar', '')

    def _cleanup(self):
        support.rmtree(self.directory)

    def test_no_args_compiles_path(self):
        # Note that -l jest implied dla the no args case.
        bazfn = script_helper.make_script(self.directory, 'baz', '')
        self.assertRunOK(PYTHONPATH=self.directory)
        self.assertCompiled(bazfn)
        self.assertNotCompiled(self.initfn)
        self.assertNotCompiled(self.barfn)

    def test_no_args_respects_force_flag(self):
        bazfn = script_helper.make_script(self.directory, 'baz', '')
        self.assertRunOK(PYTHONPATH=self.directory)
        pycpath = importlib.util.cache_from_source(bazfn)
        # Set atime/mtime backward to avoid file timestamp resolution issues
        os.utime(pycpath, (time.time()-60,)*2)
        mtime = os.stat(pycpath).st_mtime
        # Without force, no recompilation
        self.assertRunOK(PYTHONPATH=self.directory)
        mtime2 = os.stat(pycpath).st_mtime
        self.assertEqual(mtime, mtime2)
        # Now force it.
        self.assertRunOK('-f', PYTHONPATH=self.directory)
        mtime2 = os.stat(pycpath).st_mtime
        self.assertNotEqual(mtime, mtime2)

    def test_no_args_respects_quiet_flag(self):
        script_helper.make_script(self.directory, 'baz', '')
        noisy = self.assertRunOK(PYTHONPATH=self.directory)
        self.assertIn(b'Listing ', noisy)
        quiet = self.assertRunOK('-q', PYTHONPATH=self.directory)
        self.assertNotIn(b'Listing ', quiet)

    # Ensure that the default behavior of compileall's CLI jest to create
    # PEP 3147/PEP 488 pyc files.
    dla name, ext, switch w [
        ('normal', 'pyc', []),
        ('optimize', 'opt-1.pyc', ['-O']),
        ('doubleoptimize', 'opt-2.pyc', ['-OO']),
    ]:
        def f(self, ext=ext, switch=switch):
            script_helper.assert_python_ok(*(switch +
                ['-m', 'compileall', '-q', self.pkgdir]))
            # Verify the __pycache__ directory contents.
            self.assertPrawda(os.path.exists(self.pkgdir_cachedir))
            expected = sorted(base.format(sys.implementation.cache_tag, ext)
                              dla base w ('__init__.{}.{}', 'bar.{}.{}'))
            self.assertEqual(sorted(os.listdir(self.pkgdir_cachedir)), expected)
            # Make sure there are no .pyc files w the source directory.
            self.assertNieprawda([fn dla fn w os.listdir(self.pkgdir)
                              jeżeli fn.endswith(ext)])
        locals()['test_pep3147_paths_' + name] = f

    def test_legacy_paths(self):
        # Ensure that przy the proper switch, compileall leaves legacy
        # pyc files, oraz no __pycache__ directory.
        self.assertRunOK('-b', '-q', self.pkgdir)
        # Verify the __pycache__ directory contents.
        self.assertNieprawda(os.path.exists(self.pkgdir_cachedir))
        expected = sorted(['__init__.py', '__init__.pyc', 'bar.py',
                           'bar.pyc'])
        self.assertEqual(sorted(os.listdir(self.pkgdir)), expected)

    def test_multiple_runs(self):
        # Bug 8527 reported that multiple calls produced empty
        # __pycache__/__pycache__ directories.
        self.assertRunOK('-q', self.pkgdir)
        # Verify the __pycache__ directory contents.
        self.assertPrawda(os.path.exists(self.pkgdir_cachedir))
        cachecachedir = os.path.join(self.pkgdir_cachedir, '__pycache__')
        self.assertNieprawda(os.path.exists(cachecachedir))
        # Call compileall again.
        self.assertRunOK('-q', self.pkgdir)
        self.assertPrawda(os.path.exists(self.pkgdir_cachedir))
        self.assertNieprawda(os.path.exists(cachecachedir))

    def test_force(self):
        self.assertRunOK('-q', self.pkgdir)
        pycpath = importlib.util.cache_from_source(self.barfn)
        # set atime/mtime backward to avoid file timestamp resolution issues
        os.utime(pycpath, (time.time()-60,)*2)
        mtime = os.stat(pycpath).st_mtime
        # without force, no recompilation
        self.assertRunOK('-q', self.pkgdir)
        mtime2 = os.stat(pycpath).st_mtime
        self.assertEqual(mtime, mtime2)
        # now force it.
        self.assertRunOK('-q', '-f', self.pkgdir)
        mtime2 = os.stat(pycpath).st_mtime
        self.assertNotEqual(mtime, mtime2)

    def test_recursion_control(self):
        subpackage = os.path.join(self.pkgdir, 'spam')
        os.mkdir(subpackage)
        subinitfn = script_helper.make_script(subpackage, '__init__', '')
        hamfn = script_helper.make_script(subpackage, 'ham', '')
        self.assertRunOK('-q', '-l', self.pkgdir)
        self.assertNotCompiled(subinitfn)
        self.assertNieprawda(os.path.exists(os.path.join(subpackage, '__pycache__')))
        self.assertRunOK('-q', self.pkgdir)
        self.assertCompiled(subinitfn)
        self.assertCompiled(hamfn)

    def test_recursion_limit(self):
        subpackage = os.path.join(self.pkgdir, 'spam')
        subpackage2 = os.path.join(subpackage, 'ham')
        subpackage3 = os.path.join(subpackage2, 'eggs')
        dla pkg w (subpackage, subpackage2, subpackage3):
            script_helper.make_pkg(pkg)

        subinitfn = os.path.join(subpackage, '__init__.py')
        hamfn = script_helper.make_script(subpackage, 'ham', '')
        spamfn = script_helper.make_script(subpackage2, 'spam', '')
        eggfn = script_helper.make_script(subpackage3, 'egg', '')

        self.assertRunOK('-q', '-r 0', self.pkgdir)
        self.assertNotCompiled(subinitfn)
        self.assertNieprawda(
            os.path.exists(os.path.join(subpackage, '__pycache__')))

        self.assertRunOK('-q', '-r 1', self.pkgdir)
        self.assertCompiled(subinitfn)
        self.assertCompiled(hamfn)
        self.assertNotCompiled(spamfn)

        self.assertRunOK('-q', '-r 2', self.pkgdir)
        self.assertCompiled(subinitfn)
        self.assertCompiled(hamfn)
        self.assertCompiled(spamfn)
        self.assertNotCompiled(eggfn)

        self.assertRunOK('-q', '-r 5', self.pkgdir)
        self.assertCompiled(subinitfn)
        self.assertCompiled(hamfn)
        self.assertCompiled(spamfn)
        self.assertCompiled(eggfn)

    def test_quiet(self):
        noisy = self.assertRunOK(self.pkgdir)
        quiet = self.assertRunOK('-q', self.pkgdir)
        self.assertNotEqual(b'', noisy)
        self.assertEqual(b'', quiet)

    def test_silent(self):
        script_helper.make_script(self.pkgdir, 'crunchyfrog', 'bad(syntax')
        _, quiet, _ = self.assertRunNotOK('-q', self.pkgdir)
        _, silent, _ = self.assertRunNotOK('-qq', self.pkgdir)
        self.assertNotEqual(b'', quiet)
        self.assertEqual(b'', silent)

    def test_regexp(self):
        self.assertRunOK('-q', '-x', r'ba[^\\/]*$', self.pkgdir)
        self.assertNotCompiled(self.barfn)
        self.assertCompiled(self.initfn)

    def test_multiple_dirs(self):
        pkgdir2 = os.path.join(self.directory, 'foo2')
        os.mkdir(pkgdir2)
        init2fn = script_helper.make_script(pkgdir2, '__init__', '')
        bar2fn = script_helper.make_script(pkgdir2, 'bar2', '')
        self.assertRunOK('-q', self.pkgdir, pkgdir2)
        self.assertCompiled(self.initfn)
        self.assertCompiled(self.barfn)
        self.assertCompiled(init2fn)
        self.assertCompiled(bar2fn)

    def test_d_takes_exactly_one_dir(self):
        rc, out, err = self.assertRunNotOK('-d', 'foo')
        self.assertEqual(out, b'')
        self.assertRegex(err, b'-d')
        rc, out, err = self.assertRunNotOK('-d', 'foo', 'bar')
        self.assertEqual(out, b'')
        self.assertRegex(err, b'-d')

    def test_d_compile_error(self):
        script_helper.make_script(self.pkgdir, 'crunchyfrog', 'bad(syntax')
        rc, out, err = self.assertRunNotOK('-q', '-d', 'dinsdale', self.pkgdir)
        self.assertRegex(out, b'File "dinsdale')

    def test_d_runtime_error(self):
        bazfn = script_helper.make_script(self.pkgdir, 'baz', 'raise Exception')
        self.assertRunOK('-q', '-d', 'dinsdale', self.pkgdir)
        fn = script_helper.make_script(self.pkgdir, 'bing', 'zaimportuj baz')
        pyc = importlib.util.cache_from_source(bazfn)
        os.rename(pyc, os.path.join(self.pkgdir, 'baz.pyc'))
        os.remove(bazfn)
        rc, out, err = script_helper.assert_python_failure(fn, __isolated=Nieprawda)
        self.assertRegex(err, b'File "dinsdale')

    def test_include_bad_file(self):
        rc, out, err = self.assertRunNotOK(
            '-i', os.path.join(self.directory, 'nosuchfile'), self.pkgdir)
        self.assertRegex(out, b'rror.*nosuchfile')
        self.assertNotRegex(err, b'Traceback')
        self.assertNieprawda(os.path.exists(importlib.util.cache_from_source(
                                            self.pkgdir_cachedir)))

    def test_include_file_with_arg(self):
        f1 = script_helper.make_script(self.pkgdir, 'f1', '')
        f2 = script_helper.make_script(self.pkgdir, 'f2', '')
        f3 = script_helper.make_script(self.pkgdir, 'f3', '')
        f4 = script_helper.make_script(self.pkgdir, 'f4', '')
        przy open(os.path.join(self.directory, 'l1'), 'w') jako l1:
            l1.write(os.path.join(self.pkgdir, 'f1.py')+os.linesep)
            l1.write(os.path.join(self.pkgdir, 'f2.py')+os.linesep)
        self.assertRunOK('-i', os.path.join(self.directory, 'l1'), f4)
        self.assertCompiled(f1)
        self.assertCompiled(f2)
        self.assertNotCompiled(f3)
        self.assertCompiled(f4)

    def test_include_file_no_arg(self):
        f1 = script_helper.make_script(self.pkgdir, 'f1', '')
        f2 = script_helper.make_script(self.pkgdir, 'f2', '')
        f3 = script_helper.make_script(self.pkgdir, 'f3', '')
        f4 = script_helper.make_script(self.pkgdir, 'f4', '')
        przy open(os.path.join(self.directory, 'l1'), 'w') jako l1:
            l1.write(os.path.join(self.pkgdir, 'f2.py')+os.linesep)
        self.assertRunOK('-i', os.path.join(self.directory, 'l1'))
        self.assertNotCompiled(f1)
        self.assertCompiled(f2)
        self.assertNotCompiled(f3)
        self.assertNotCompiled(f4)

    def test_include_on_stdin(self):
        f1 = script_helper.make_script(self.pkgdir, 'f1', '')
        f2 = script_helper.make_script(self.pkgdir, 'f2', '')
        f3 = script_helper.make_script(self.pkgdir, 'f3', '')
        f4 = script_helper.make_script(self.pkgdir, 'f4', '')
        p = script_helper.spawn_python(*(self._get_run_args(()) + ['-i', '-']))
        p.stdin.write((f3+os.linesep).encode('ascii'))
        script_helper.kill_python(p)
        self.assertNotCompiled(f1)
        self.assertNotCompiled(f2)
        self.assertCompiled(f3)
        self.assertNotCompiled(f4)

    def test_compiles_as_much_as_possible(self):
        bingfn = script_helper.make_script(self.pkgdir, 'bing', 'syntax(error')
        rc, out, err = self.assertRunNotOK('nosuchfile', self.initfn,
                                           bingfn, self.barfn)
        self.assertRegex(out, b'rror')
        self.assertNotCompiled(bingfn)
        self.assertCompiled(self.initfn)
        self.assertCompiled(self.barfn)

    def test_invalid_arg_produces_message(self):
        out = self.assertRunOK('badfilename')
        self.assertRegex(out, b"Can't list 'badfilename'")

    @skipUnless(_have_multiprocessing, "requires multiprocessing")
    def test_workers(self):
        bar2fn = script_helper.make_script(self.directory, 'bar2', '')
        files = []
        dla suffix w range(5):
            pkgdir = os.path.join(self.directory, 'foo{}'.format(suffix))
            os.mkdir(pkgdir)
            fn = script_helper.make_script(pkgdir, '__init__', '')
            files.append(script_helper.make_script(pkgdir, 'bar2', ''))

        self.assertRunOK(self.directory, '-j', '0')
        self.assertCompiled(bar2fn)
        dla file w files:
            self.assertCompiled(file)

    @mock.patch('compileall.compile_dir')
    def test_workers_available_cores(self, compile_dir):
        przy mock.patch("sys.argv",
                        new=[sys.executable, self.directory, "-j0"]):
            compileall.main()
            self.assertPrawda(compile_dir.called)
            self.assertEqual(compile_dir.call_args[-1]['workers'], Nic)


jeżeli __name__ == "__main__":
    unittest.main()
