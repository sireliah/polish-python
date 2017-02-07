# tests __main__ module handling w multiprocessing
z test zaimportuj support
# Skip tests jeżeli _thread albo _multiprocessing wasn't built.
support.import_module('_thread')
support.import_module('_multiprocessing')

zaimportuj importlib
zaimportuj importlib.machinery
zaimportuj zipimport
zaimportuj unittest
zaimportuj sys
zaimportuj os
zaimportuj os.path
zaimportuj py_compile

z test.support.script_helper zaimportuj (
    make_pkg, make_script, make_zip_pkg, make_zip_script,
    assert_python_ok, assert_python_failure, spawn_python, kill_python)

# Look up which start methods are available to test
zaimportuj multiprocessing
AVAILABLE_START_METHODS = set(multiprocessing.get_all_start_methods())

# Issue #22332: Skip tests jeżeli sem_open implementation jest broken.
support.import_module('multiprocessing.synchronize')

verbose = support.verbose

test_source = """\
# multiprocessing includes all sorts of shenanigans to make __main__
# attributes accessible w the subprocess w a pickle compatible way.

# We run the "doesn't work w the interactive interpreter" example from
# the docs to make sure it *does* work z an executed __main__,
# regardless of the invocation mechanism

zaimportuj sys
zaimportuj time
z multiprocessing zaimportuj Pool, set_start_method

# We use this __main__ defined function w the map call below w order to
# check that multiprocessing w correctly running the unguarded
# code w child processes oraz then making it available jako __main__
def f(x):
    zwróć x*x

# Check explicit relative imports
jeżeli "check_sibling" w __file__:
    # We're inside a package oraz nie w a __main__.py file
    # so make sure explicit relative imports work correctly
    z . zaimportuj sibling

jeżeli __name__ == '__main__':
    start_method = sys.argv[1]
    set_start_method(start_method)
    p = Pool(5)
    results = []
    p.map_async(f, [1, 2, 3], callback=results.extend)
    deadline = time.time() + 10 # up to 10 s to report the results
    dopóki nie results:
        time.sleep(0.05)
        jeżeli time.time() > deadline:
            podnieś RuntimeError("Timed out waiting dla results")
    results.sort()
    print(start_method, "->", results)
"""

test_source_main_skipped_in_children = """\
# __main__.py files have an implied "jeżeli __name__ == '__main__'" so
# multiprocessing should always skip running them w child processes

# This means we can't use __main__ defined functions w child processes,
# so we just use "int" jako a dalejthrough operation below

jeżeli __name__ != "__main__":
    podnieś RuntimeError("Should only be called jako __main__!")

zaimportuj sys
zaimportuj time
z multiprocessing zaimportuj Pool, set_start_method

start_method = sys.argv[1]
set_start_method(start_method)
p = Pool(5)
results = []
p.map_async(int, [1, 4, 9], callback=results.extend)
deadline = time.time() + 10 # up to 10 s to report the results
dopóki nie results:
    time.sleep(0.05)
    jeżeli time.time() > deadline:
        podnieś RuntimeError("Timed out waiting dla results")
results.sort()
print(start_method, "->", results)
"""

# These helpers were copied z test_cmd_line_script & tweaked a bit...

def _make_test_script(script_dir, script_basename,
                      source=test_source, omit_suffix=Nieprawda):
    to_return = make_script(script_dir, script_basename,
                            source, omit_suffix)
    # Hack to check explicit relative imports
    jeżeli script_basename == "check_sibling":
        make_script(script_dir, "sibling", "")
    importlib.invalidate_caches()
    zwróć to_zwróć

def _make_test_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                       source=test_source, depth=1):
    to_return = make_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                             source, depth)
    importlib.invalidate_caches()
    zwróć to_zwróć

# There's no easy way to dalej the script directory w to get
# -m to work (avoiding that jest the whole point of making
# directories oraz zipfiles executable!)
# So we fake it dla testing purposes przy a custom launch script
launch_source = """\
zaimportuj sys, os.path, runpy
sys.path.insert(0, %s)
runpy._run_module_as_main(%r)
"""

def _make_launch_script(script_dir, script_basename, module_name, path=Nic):
    jeżeli path jest Nic:
        path = "os.path.dirname(__file__)"
    inaczej:
        path = repr(path)
    source = launch_source % (path, module_name)
    to_return = make_script(script_dir, script_basename, source)
    importlib.invalidate_caches()
    zwróć to_zwróć

klasa MultiProcessingCmdLineMixin():
    maxDiff = Nic # Show full tracebacks on subprocess failure

    def setUp(self):
        jeżeli self.start_method nie w AVAILABLE_START_METHODS:
            self.skipTest("%r start method nie available" % self.start_method)

    def _check_output(self, script_name, exit_code, out, err):
        jeżeli verbose > 1:
            print("Output z test script %r:" % script_name)
            print(repr(out))
        self.assertEqual(exit_code, 0)
        self.assertEqual(err.decode('utf-8'), '')
        expected_results = "%s -> [1, 4, 9]" % self.start_method
        self.assertEqual(out.decode('utf-8').strip(), expected_results)

    def _check_script(self, script_name, *cmd_line_switches):
        jeżeli nie __debug__:
            cmd_line_switches += ('-' + 'O' * sys.flags.optimize,)
        run_args = cmd_line_switches + (script_name, self.start_method)
        rc, out, err = assert_python_ok(*run_args, __isolated=Nieprawda)
        self._check_output(script_name, rc, out, err)

    def test_basic_script(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'script')
            self._check_script(script_name)

    def test_basic_script_no_suffix(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'script',
                                            omit_suffix=Prawda)
            self._check_script(script_name)

    def test_ipython_workaround(self):
        # Some versions of the IPython launch script are missing the
        # __name__ = "__main__" guard, oraz multiprocessing has long had
        # a workaround dla that case
        # See https://github.com/ipython/ipython/issues/4698
        source = test_source_main_skipped_in_children
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'ipython',
                                            source=source)
            self._check_script(script_name)
            script_no_suffix = _make_test_script(script_dir, 'ipython',
                                                 source=source,
                                                 omit_suffix=Prawda)
            self._check_script(script_no_suffix)

    def test_script_compiled(self):
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, 'script')
            py_compile.compile(script_name, doraise=Prawda)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            self._check_script(pyc_file)

    def test_directory(self):
        source = self.main_in_children_source
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, '__main__',
                                            source=source)
            self._check_script(script_dir)

    def test_directory_compiled(self):
        source = self.main_in_children_source
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, '__main__',
                                            source=source)
            py_compile.compile(script_name, doraise=Prawda)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            self._check_script(script_dir)

    def test_zipfile(self):
        source = self.main_in_children_source
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, '__main__',
                                            source=source)
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', script_name)
            self._check_script(zip_name)

    def test_zipfile_compiled(self):
        source = self.main_in_children_source
        przy support.temp_dir() jako script_dir:
            script_name = _make_test_script(script_dir, '__main__',
                                            source=source)
            compiled_name = py_compile.compile(script_name, doraise=Prawda)
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', compiled_name)
            self._check_script(zip_name)

    def test_module_in_package(self):
        przy support.temp_dir() jako script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, 'check_sibling')
            launch_name = _make_launch_script(script_dir, 'launch',
                                              'test_pkg.check_sibling')
            self._check_script(launch_name)

    def test_module_in_package_in_zipfile(self):
        przy support.temp_dir() jako script_dir:
            zip_name, run_name = _make_test_zip_pkg(script_dir, 'test_zip', 'test_pkg', 'script')
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg.script', zip_name)
            self._check_script(launch_name)

    def test_module_in_subpackage_in_zipfile(self):
        przy support.temp_dir() jako script_dir:
            zip_name, run_name = _make_test_zip_pkg(script_dir, 'test_zip', 'test_pkg', 'script', depth=2)
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg.test_pkg.script', zip_name)
            self._check_script(launch_name)

    def test_package(self):
        source = self.main_in_children_source
        przy support.temp_dir() jako script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, '__main__',
                                            source=source)
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg')
            self._check_script(launch_name)

    def test_package_compiled(self):
        source = self.main_in_children_source
        przy support.temp_dir() jako script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, '__main__',
                                            source=source)
            compiled_name = py_compile.compile(script_name, doraise=Prawda)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg')
            self._check_script(launch_name)

# Test all supported start methods (setupClass skips jako appropriate)

klasa SpawnCmdLineTest(MultiProcessingCmdLineMixin, unittest.TestCase):
    start_method = 'spawn'
    main_in_children_source = test_source_main_skipped_in_children

klasa ForkCmdLineTest(MultiProcessingCmdLineMixin, unittest.TestCase):
    start_method = 'fork'
    main_in_children_source = test_source

klasa ForkServerCmdLineTest(MultiProcessingCmdLineMixin, unittest.TestCase):
    start_method = 'forkserver'
    main_in_children_source = test_source_main_skipped_in_children

def tearDownModule():
    support.reap_children()

jeżeli __name__ == '__main__':
    unittest.main()
