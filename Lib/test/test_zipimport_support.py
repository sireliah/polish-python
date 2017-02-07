# This test module covers support w various parts of the standard library
# dla working przy modules located inside zipfiles
# The tests are centralised w this fashion to make it easy to drop them
# jeżeli a platform doesn't support zipimport
zaimportuj test.support
zaimportuj os
zaimportuj os.path
zaimportuj sys
zaimportuj textwrap
zaimportuj zipfile
zaimportuj zipimport
zaimportuj doctest
zaimportuj inspect
zaimportuj linecache
zaimportuj pdb
zaimportuj unittest
z test.support.script_helper zaimportuj (spawn_python, kill_python, assert_python_ok,
                                        make_script, make_zip_script)

verbose = test.support.verbose

# Library modules covered by this test set
#  pdb (Issue 4201)
#  inspect (Issue 4223)
#  doctest (Issue 4197)

# Other test modules przy zipzaimportuj related tests
#  test_zipzaimportuj (of course!)
#  test_cmd_line_script (covers the zipzaimportuj support w runpy)

# Retrieve some helpers z other test cases
z test zaimportuj (test_doctest, sample_doctest, sample_doctest_no_doctests,
                  sample_doctest_no_docstrings)


def _run_object_doctest(obj, module):
    finder = doctest.DocTestFinder(verbose=verbose, recurse=Nieprawda)
    runner = doctest.DocTestRunner(verbose=verbose)
    # Use the object's fully qualified name jeżeli it has one
    # Otherwise, use the module's name
    spróbuj:
        name = "%s.%s" % (obj.__module__, obj.__qualname__)
    wyjąwszy AttributeError:
        name = module.__name__
    dla example w finder.find(obj, name, module):
        runner.run(example)
    f, t = runner.failures, runner.tries
    jeżeli f:
        podnieś test.support.TestFailed("%d of %d doctests failed" % (f, t))
    jeżeli verbose:
        print ('doctest (%s) ... %d tests przy zero failures' % (module.__name__, t))
    zwróć f, t



klasa ZipSupportTests(unittest.TestCase):
    # This used to use the ImportHooksBaseTestCase to restore
    # the state of the zaimportuj related information
    # w the sys module after each test. However, that restores
    # *too much* information oraz przerwijs dla the invocation
    # of test_doctest. So we do our own thing oraz leave
    # sys.modules alone.
    # We also clear the linecache oraz zipzaimportuj cache
    # just to avoid any bogus errors due to name reuse w the tests
    def setUp(self):
        linecache.clearcache()
        zipimport._zip_directory_cache.clear()
        self.path = sys.path[:]
        self.meta_path = sys.meta_path[:]
        self.path_hooks = sys.path_hooks[:]
        sys.path_importer_cache.clear()

    def tearDown(self):
        sys.path[:] = self.path
        sys.meta_path[:] = self.meta_path
        sys.path_hooks[:] = self.path_hooks
        sys.path_importer_cache.clear()

    def test_inspect_getsource_issue4223(self):
        test_src = "def foo(): dalej\n"
        przy test.support.temp_dir() jako d:
            init_name = make_script(d, '__init__', test_src)
            name_in_zip = os.path.join('zip_pkg',
                                       os.path.basename(init_name))
            zip_name, run_name = make_zip_script(d, 'test_zip',
                                                init_name, name_in_zip)
            os.remove(init_name)
            sys.path.insert(0, zip_name)
            zaimportuj zip_pkg
            spróbuj:
                self.assertEqual(inspect.getsource(zip_pkg.foo), test_src)
            w_końcu:
                usuń sys.modules["zip_pkg"]

    def test_doctest_issue4197(self):
        # To avoid having to keep two copies of the doctest module's
        # unit tests w sync, this test works by taking the source of
        # test_doctest itself, rewriting it a bit to cope przy a new
        # location, oraz then throwing it w a zip file to make sure
        # everything still works correctly
        test_src = inspect.getsource(test_doctest)
        test_src = test_src.replace(
                         "z test zaimportuj test_doctest",
                         "zaimportuj test_zipped_doctest jako test_doctest")
        test_src = test_src.replace("test.test_doctest",
                                    "test_zipped_doctest")
        test_src = test_src.replace("test.sample_doctest",
                                    "sample_zipped_doctest")
        # The sample doctest files rewritten to include w the zipped version.
        sample_sources = {}
        dla mod w [sample_doctest, sample_doctest_no_doctests,
                    sample_doctest_no_docstrings]:
            src = inspect.getsource(mod)
            src = src.replace("test.test_doctest", "test_zipped_doctest")
            # Rewrite the module name so that, dla example,
            # "test.sample_doctest" becomes "sample_zipped_doctest".
            mod_name = mod.__name__.split(".")[-1]
            mod_name = mod_name.replace("sample_", "sample_zipped_")
            sample_sources[mod_name] = src

        przy test.support.temp_dir() jako d:
            script_name = make_script(d, 'test_zipped_doctest',
                                            test_src)
            zip_name, run_name = make_zip_script(d, 'test_zip',
                                                script_name)
            z = zipfile.ZipFile(zip_name, 'a')
            dla mod_name, src w sample_sources.items():
                z.writestr(mod_name + ".py", src)
            z.close()
            jeżeli verbose:
                zip_file = zipfile.ZipFile(zip_name, 'r')
                print ('Contents of %r:' % zip_name)
                zip_file.printdir()
                zip_file.close()
            os.remove(script_name)
            sys.path.insert(0, zip_name)
            zaimportuj test_zipped_doctest
            spróbuj:
                # Some of the doc tests depend on the colocated text files
                # which aren't available to the zipped version (the doctest
                # module currently requires real filenames dla non-embedded
                # tests). So we're forced to be selective about which tests
                # to run.
                # doctest could really use some APIs which take a text
                # string albo a file object instead of a filename...
                known_good_tests = [
                    test_zipped_doctest.SampleClass,
                    test_zipped_doctest.SampleClass.NestedClass,
                    test_zipped_doctest.SampleClass.NestedClass.__init__,
                    test_zipped_doctest.SampleClass.__init__,
                    test_zipped_doctest.SampleClass.a_classmethod,
                    test_zipped_doctest.SampleClass.a_property,
                    test_zipped_doctest.SampleClass.a_staticmethod,
                    test_zipped_doctest.SampleClass.double,
                    test_zipped_doctest.SampleClass.get,
                    test_zipped_doctest.SampleNewStyleClass,
                    test_zipped_doctest.SampleNewStyleClass.__init__,
                    test_zipped_doctest.SampleNewStyleClass.double,
                    test_zipped_doctest.SampleNewStyleClass.get,
                    test_zipped_doctest.sample_func,
                    test_zipped_doctest.test_DocTest,
                    test_zipped_doctest.test_DocTestParser,
                    test_zipped_doctest.test_DocTestRunner.basics,
                    test_zipped_doctest.test_DocTestRunner.exceptions,
                    test_zipped_doctest.test_DocTestRunner.option_directives,
                    test_zipped_doctest.test_DocTestRunner.optionflags,
                    test_zipped_doctest.test_DocTestRunner.verbose_flag,
                    test_zipped_doctest.test_Example,
                    test_zipped_doctest.test_debug,
                    test_zipped_doctest.test_testsource,
                    test_zipped_doctest.test_trailing_space_in_test,
                    test_zipped_doctest.test_DocTestSuite,
                    test_zipped_doctest.test_DocTestFinder,
                ]
                # These tests are the ones which need access
                # to the data files, so we don't run them
                fail_due_to_missing_data_files = [
                    test_zipped_doctest.test_DocFileSuite,
                    test_zipped_doctest.test_testfile,
                    test_zipped_doctest.test_unittest_reportflags,
                ]

                dla obj w known_good_tests:
                    _run_object_doctest(obj, test_zipped_doctest)
            w_końcu:
                usuń sys.modules["test_zipped_doctest"]

    def test_doctest_main_issue4197(self):
        test_src = textwrap.dedent("""\
                    klasa Test:
                        ">>> 'line 2'"
                        dalej

                    zaimportuj doctest
                    doctest.testmod()
                    """)
        pattern = 'File "%s", line 2, w %s'
        przy test.support.temp_dir() jako d:
            script_name = make_script(d, 'script', test_src)
            rc, out, err = assert_python_ok(script_name)
            expected = pattern % (script_name, "__main__.Test")
            jeżeli verbose:
                print ("Expected line", expected)
                print ("Got stdout:")
                print (ascii(out))
            self.assertIn(expected.encode('utf-8'), out)
            zip_name, run_name = make_zip_script(d, "test_zip",
                                                script_name, '__main__.py')
            rc, out, err = assert_python_ok(zip_name)
            expected = pattern % (run_name, "__main__.Test")
            jeżeli verbose:
                print ("Expected line", expected)
                print ("Got stdout:")
                print (ascii(out))
            self.assertIn(expected.encode('utf-8'), out)

    def test_pdb_issue4201(self):
        test_src = textwrap.dedent("""\
                    def f():
                        dalej

                    zaimportuj pdb
                    pdb.Pdb(nosigint=Prawda).runcall(f)
                    """)
        przy test.support.temp_dir() jako d:
            script_name = make_script(d, 'script', test_src)
            p = spawn_python(script_name)
            p.stdin.write(b'l\n')
            data = kill_python(p)
            # bdb/pdb applies normcase to its filename before displaying
            self.assertIn(os.path.normcase(script_name.encode('utf-8')), data)
            zip_name, run_name = make_zip_script(d, "test_zip",
                                                script_name, '__main__.py')
            p = spawn_python(zip_name)
            p.stdin.write(b'l\n')
            data = kill_python(p)
            # bdb/pdb applies normcase to its filename before displaying
            self.assertIn(os.path.normcase(run_name.encode('utf-8')), data)


def tearDownModule():
    test.support.reap_children()

jeżeli __name__ == '__main__':
    unittest.main()
