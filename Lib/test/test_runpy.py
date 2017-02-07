# Test the runpy module
zaimportuj unittest
zaimportuj os
zaimportuj os.path
zaimportuj sys
zaimportuj re
zaimportuj tempfile
zaimportuj importlib, importlib.machinery, importlib.util
zaimportuj py_compile
z test.support zaimportuj (
    forget, make_legacy_pyc, unload, verbose, no_tracing,
    create_empty_file, temp_dir)
z test.support.script_helper zaimportuj (
    make_pkg, make_script, make_zip_pkg, make_zip_script)


zaimportuj runpy
z runpy zaimportuj _run_code, _run_module_code, run_module, run_path
# Note: This module can't safely test _run_module_as_main jako it
# runs its tests w the current process, which would mess przy the
# real __main__ module (usually test.regrtest)
# See test_cmd_line_script dla a test that executes that code path


# Set up the test code oraz expected results
example_source = """\
# Check basic code execution
result = ['Top level assignment']
def f():
    result.append('Lower level reference')
f()
usuń f
# Check the sys module
zaimportuj sys
run_argv0 = sys.argv[0]
run_name_in_sys_modules = __name__ w sys.modules
module_in_sys_modules = (run_name_in_sys_modules oraz
                         globals() jest sys.modules[__name__].__dict__)
# Check nested operation
zaimportuj runpy
nested = runpy._run_module_code('x=1\\n', mod_name='<run>')
"""

implicit_namespace = {
    "__name__": Nic,
    "__file__": Nic,
    "__cached__": Nic,
    "__package__": Nic,
    "__doc__": Nic,
    "__spec__": Nic
}
example_namespace =  {
    "sys": sys,
    "runpy": runpy,
    "result": ["Top level assignment", "Lower level reference"],
    "run_argv0": sys.argv[0],
    "run_name_in_sys_modules": Nieprawda,
    "module_in_sys_modules": Nieprawda,
    "nested": dict(implicit_namespace,
                   x=1, __name__="<run>", __loader__=Nic),
}
example_namespace.update(implicit_namespace)

klasa CodeExecutionMixin:
    # Issue #15230 (run_path nie handling run_name correctly) highlighted a
    # problem przy the way arguments were being dalejed z higher level APIs
    # down to lower level code. This mixin makes it easier to ensure full
    # testing occurs at those upper layers jako well, nie just at the utility
    # layer

    # Figuring out the loader details w advance jest hard to do, so we skip
    # checking the full details of loader oraz loader_state
    CHECKED_SPEC_ATTRIBUTES = ["name", "parent", "origin", "cached",
                               "has_location", "submodule_search_locations"]

    def assertNamespaceMatches(self, result_ns, expected_ns):
        """Check two namespaces match.

           Ignores any unspecified interpreter created names
        """
        # Avoid side effects
        result_ns = result_ns.copy()
        expected_ns = expected_ns.copy()
        # Impls are permitted to add extra names, so filter them out
        dla k w list(result_ns):
            jeżeli k.startswith("__") oraz k.endswith("__"):
                jeżeli k nie w expected_ns:
                    result_ns.pop(k)
                jeżeli k nie w expected_ns["nested"]:
                    result_ns["nested"].pop(k)
        # Spec equality includes the loader, so we take the spec out of the
        # result namespace oraz check that separately
        result_spec = result_ns.pop("__spec__")
        expected_spec = expected_ns.pop("__spec__")
        jeżeli expected_spec jest Nic:
            self.assertIsNic(result_spec)
        inaczej:
            # If an expected loader jest set, we just check we got the right
            # type, rather than checking dla full equality
            jeżeli expected_spec.loader jest nie Nic:
                self.assertEqual(type(result_spec.loader),
                                 type(expected_spec.loader))
            dla attr w self.CHECKED_SPEC_ATTRIBUTES:
                k = "__spec__." + attr
                actual = (k, getattr(result_spec, attr))
                expected = (k, getattr(expected_spec, attr))
                self.assertEqual(actual, expected)
        # For the rest, we still don't use direct dict comparison on the
        # namespace, jako the diffs are too hard to debug jeżeli anything przerwijs
        self.assertEqual(set(result_ns), set(expected_ns))
        dla k w result_ns:
            actual = (k, result_ns[k])
            expected = (k, expected_ns[k])
            self.assertEqual(actual, expected)

    def check_code_execution(self, create_namespace, expected_namespace):
        """Check that an interface runs the example code correctly

           First argument jest a callable accepting the initial globals oraz
           using them to create the actual namespace
           Second argument jest the expected result
        """
        sentinel = object()
        expected_ns = expected_namespace.copy()
        run_name = expected_ns["__name__"]
        saved_argv0 = sys.argv[0]
        saved_mod = sys.modules.get(run_name, sentinel)
        # Check without initial globals
        result_ns = create_namespace(Nic)
        self.assertNamespaceMatches(result_ns, expected_ns)
        self.assertIs(sys.argv[0], saved_argv0)
        self.assertIs(sys.modules.get(run_name, sentinel), saved_mod)
        # And then przy initial globals
        initial_ns = {"sentinel": sentinel}
        expected_ns["sentinel"] = sentinel
        result_ns = create_namespace(initial_ns)
        self.assertIsNot(result_ns, initial_ns)
        self.assertNamespaceMatches(result_ns, expected_ns)
        self.assertIs(sys.argv[0], saved_argv0)
        self.assertIs(sys.modules.get(run_name, sentinel), saved_mod)


klasa ExecutionLayerTestCase(unittest.TestCase, CodeExecutionMixin):
    """Unit tests dla runpy._run_code oraz runpy._run_module_code"""

    def test_run_code(self):
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__loader__": Nic,
        })
        def create_ns(init_globals):
            zwróć _run_code(example_source, {}, init_globals)
        self.check_code_execution(create_ns, expected_ns)

    def test_run_module_code(self):
        mod_name = "<Nonsense>"
        mod_fname = "Some other nonsense"
        mod_loader = "Now you're just being silly"
        mod_package = '' # Treat jako a top level module
        mod_spec = importlib.machinery.ModuleSpec(mod_name,
                                                  origin=mod_fname,
                                                  loader=mod_loader)
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__name__": mod_name,
            "__file__": mod_fname,
            "__loader__": mod_loader,
            "__package__": mod_package,
            "__spec__": mod_spec,
            "run_argv0": mod_fname,
            "run_name_in_sys_modules": Prawda,
            "module_in_sys_modules": Prawda,
        })
        def create_ns(init_globals):
            zwróć _run_module_code(example_source,
                                    init_globals,
                                    mod_name,
                                    mod_spec)
        self.check_code_execution(create_ns, expected_ns)

# TODO: Use self.addCleanup to get rid of a lot of try-finally blocks
klasa RunModuleTestCase(unittest.TestCase, CodeExecutionMixin):
    """Unit tests dla runpy.run_module"""

    def expect_import_error(self, mod_name):
        spróbuj:
            run_module(mod_name)
        wyjąwszy ImportError:
            dalej
        inaczej:
            self.fail("Expected zaimportuj error dla " + mod_name)

    def test_invalid_names(self):
        # Builtin module
        self.expect_import_error("sys")
        # Non-existent modules
        self.expect_import_error("sys.imp.eric")
        self.expect_import_error("os.path.half")
        self.expect_import_error("a.bee")
        self.expect_import_error(".howard")
        self.expect_import_error("..eaten")
        # Package without __main__.py
        self.expect_import_error("multiprocessing")

    def test_library_module(self):
        self.assertEqual(run_module("runpy")["__name__"], "runpy")

    def _add_pkg_dir(self, pkg_dir, namespace=Nieprawda):
        os.mkdir(pkg_dir)
        jeżeli namespace:
            zwróć Nic
        pkg_fname = os.path.join(pkg_dir, "__init__.py")
        create_empty_file(pkg_fname)
        zwróć pkg_fname

    def _make_pkg(self, source, depth, mod_base="runpy_test",
                     *, namespace=Nieprawda, parent_namespaces=Nieprawda):
        # Enforce a couple of internal sanity checks on test cases
        jeżeli (namespace albo parent_namespaces) oraz nie depth:
            podnieś RuntimeError("Can't mark top level module jako a "
                               "namespace package")
        pkg_name = "__runpy_pkg__"
        test_fname = mod_base+os.extsep+"py"
        pkg_dir = sub_dir = os.path.realpath(tempfile.mkdtemp())
        jeżeli verbose > 1: print("  Package tree in:", sub_dir)
        sys.path.insert(0, pkg_dir)
        jeżeli verbose > 1: print("  Updated sys.path:", sys.path[0])
        jeżeli depth:
            namespace_flags = [parent_namespaces] * depth
            namespace_flags[-1] = namespace
            dla namespace_flag w namespace_flags:
                sub_dir = os.path.join(sub_dir, pkg_name)
                pkg_fname = self._add_pkg_dir(sub_dir, namespace_flag)
                jeżeli verbose > 1: print("  Next level in:", sub_dir)
                jeżeli verbose > 1: print("  Created:", pkg_fname)
        mod_fname = os.path.join(sub_dir, test_fname)
        mod_file = open(mod_fname, "w")
        mod_file.write(source)
        mod_file.close()
        jeżeli verbose > 1: print("  Created:", mod_fname)
        mod_name = (pkg_name+".")*depth + mod_base
        mod_spec = importlib.util.spec_from_file_location(mod_name,
                                                          mod_fname)
        zwróć pkg_dir, mod_fname, mod_name, mod_spec

    def _del_pkg(self, top, depth, mod_name):
        dla entry w list(sys.modules):
            jeżeli entry.startswith("__runpy_pkg__"):
                usuń sys.modules[entry]
        jeżeli verbose > 1: print("  Removed sys.modules entries")
        usuń sys.path[0]
        jeżeli verbose > 1: print("  Removed sys.path entry")
        dla root, dirs, files w os.walk(top, topdown=Nieprawda):
            dla name w files:
                spróbuj:
                    os.remove(os.path.join(root, name))
                wyjąwszy OSError jako ex:
                    jeżeli verbose > 1: print(ex) # Persist przy cleaning up
            dla name w dirs:
                fullname = os.path.join(root, name)
                spróbuj:
                    os.rmdir(fullname)
                wyjąwszy OSError jako ex:
                    jeżeli verbose > 1: print(ex) # Persist przy cleaning up
        spróbuj:
            os.rmdir(top)
            jeżeli verbose > 1: print("  Removed package tree")
        wyjąwszy OSError jako ex:
            jeżeli verbose > 1: print(ex) # Persist przy cleaning up

    def _fix_ns_for_legacy_pyc(self, ns, alter_sys):
        char_to_add = "c"
        ns["__file__"] += char_to_add
        ns["__cached__"] = ns["__file__"]
        spec = ns["__spec__"]
        new_spec = importlib.util.spec_from_file_location(spec.name,
                                                          ns["__file__"])
        ns["__spec__"] = new_spec
        jeżeli alter_sys:
            ns["run_argv0"] += char_to_add


    def _check_module(self, depth, alter_sys=Nieprawda,
                         *, namespace=Nieprawda, parent_namespaces=Nieprawda):
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg(example_source, depth,
                              namespace=namespace,
                              parent_namespaces=parent_namespaces))
        forget(mod_name)
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__name__": mod_name,
            "__file__": mod_fname,
            "__cached__": mod_spec.cached,
            "__package__": mod_name.rpartition(".")[0],
            "__spec__": mod_spec,
        })
        jeżeli alter_sys:
            expected_ns.update({
                "run_argv0": mod_fname,
                "run_name_in_sys_modules": Prawda,
                "module_in_sys_modules": Prawda,
            })
        def create_ns(init_globals):
            zwróć run_module(mod_name, init_globals, alter_sys=alter_sys)
        spróbuj:
            jeżeli verbose > 1: print("Running z source:", mod_name)
            self.check_code_execution(create_ns, expected_ns)
            importlib.invalidate_caches()
            __import__(mod_name)
            os.remove(mod_fname)
            jeżeli nie sys.dont_write_bytecode:
                make_legacy_pyc(mod_fname)
                unload(mod_name)  # In case loader caches paths
                importlib.invalidate_caches()
                jeżeli verbose > 1: print("Running z compiled:", mod_name)
                self._fix_ns_for_legacy_pyc(expected_ns, alter_sys)
                self.check_code_execution(create_ns, expected_ns)
        w_końcu:
            self._del_pkg(pkg_dir, depth, mod_name)
        jeżeli verbose > 1: print("Module executed successfully")

    def _check_package(self, depth, alter_sys=Nieprawda,
                          *, namespace=Nieprawda, parent_namespaces=Nieprawda):
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg(example_source, depth, "__main__",
                              namespace=namespace,
                              parent_namespaces=parent_namespaces))
        pkg_name = mod_name.rpartition(".")[0]
        forget(mod_name)
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__name__": mod_name,
            "__file__": mod_fname,
            "__cached__": importlib.util.cache_from_source(mod_fname),
            "__package__": pkg_name,
            "__spec__": mod_spec,
        })
        jeżeli alter_sys:
            expected_ns.update({
                "run_argv0": mod_fname,
                "run_name_in_sys_modules": Prawda,
                "module_in_sys_modules": Prawda,
            })
        def create_ns(init_globals):
            zwróć run_module(pkg_name, init_globals, alter_sys=alter_sys)
        spróbuj:
            jeżeli verbose > 1: print("Running z source:", pkg_name)
            self.check_code_execution(create_ns, expected_ns)
            importlib.invalidate_caches()
            __import__(mod_name)
            os.remove(mod_fname)
            jeżeli nie sys.dont_write_bytecode:
                make_legacy_pyc(mod_fname)
                unload(mod_name)  # In case loader caches paths
                jeżeli verbose > 1: print("Running z compiled:", pkg_name)
                importlib.invalidate_caches()
                self._fix_ns_for_legacy_pyc(expected_ns, alter_sys)
                self.check_code_execution(create_ns, expected_ns)
        w_końcu:
            self._del_pkg(pkg_dir, depth, pkg_name)
        jeżeli verbose > 1: print("Package executed successfully")

    def _add_relative_modules(self, base_dir, source, depth):
        jeżeli depth <= 1:
            podnieś ValueError("Relative module test needs depth > 1")
        pkg_name = "__runpy_pkg__"
        module_dir = base_dir
        dla i w range(depth):
            parent_dir = module_dir
            module_dir = os.path.join(module_dir, pkg_name)
        # Add sibling module
        sibling_fname = os.path.join(module_dir, "sibling.py")
        create_empty_file(sibling_fname)
        jeżeli verbose > 1: print("  Added sibling module:", sibling_fname)
        # Add nephew module
        uncle_dir = os.path.join(parent_dir, "uncle")
        self._add_pkg_dir(uncle_dir)
        jeżeli verbose > 1: print("  Added uncle package:", uncle_dir)
        cousin_dir = os.path.join(uncle_dir, "cousin")
        self._add_pkg_dir(cousin_dir)
        jeżeli verbose > 1: print("  Added cousin package:", cousin_dir)
        nephew_fname = os.path.join(cousin_dir, "nephew.py")
        create_empty_file(nephew_fname)
        jeżeli verbose > 1: print("  Added nephew module:", nephew_fname)

    def _check_relative_imports(self, depth, run_name=Nic):
        contents = r"""\
z __future__ zaimportuj absolute_import
z . zaimportuj sibling
z ..uncle.cousin zaimportuj nephew
"""
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg(contents, depth))
        jeżeli run_name jest Nic:
            expected_name = mod_name
        inaczej:
            expected_name = run_name
        spróbuj:
            self._add_relative_modules(pkg_dir, contents, depth)
            pkg_name = mod_name.rpartition('.')[0]
            jeżeli verbose > 1: print("Running z source:", mod_name)
            d1 = run_module(mod_name, run_name=run_name) # Read z source
            self.assertEqual(d1["__name__"], expected_name)
            self.assertEqual(d1["__package__"], pkg_name)
            self.assertIn("sibling", d1)
            self.assertIn("nephew", d1)
            usuń d1 # Ensure __loader__ entry doesn't keep file open
            importlib.invalidate_caches()
            __import__(mod_name)
            os.remove(mod_fname)
            jeżeli nie sys.dont_write_bytecode:
                make_legacy_pyc(mod_fname)
                unload(mod_name)  # In case the loader caches paths
                jeżeli verbose > 1: print("Running z compiled:", mod_name)
                importlib.invalidate_caches()
                d2 = run_module(mod_name, run_name=run_name) # Read z bytecode
                self.assertEqual(d2["__name__"], expected_name)
                self.assertEqual(d2["__package__"], pkg_name)
                self.assertIn("sibling", d2)
                self.assertIn("nephew", d2)
                usuń d2 # Ensure __loader__ entry doesn't keep file open
        w_końcu:
            self._del_pkg(pkg_dir, depth, mod_name)
        jeżeli verbose > 1: print("Module executed successfully")

    def test_run_module(self):
        dla depth w range(4):
            jeżeli verbose > 1: print("Testing package depth:", depth)
            self._check_module(depth)

    def test_run_module_in_namespace_package(self):
        dla depth w range(1, 4):
            jeżeli verbose > 1: print("Testing package depth:", depth)
            self._check_module(depth, namespace=Prawda, parent_namespaces=Prawda)

    def test_run_package(self):
        dla depth w range(1, 4):
            jeżeli verbose > 1: print("Testing package depth:", depth)
            self._check_package(depth)

    def test_run_package_in_namespace_package(self):
        dla depth w range(1, 4):
            jeżeli verbose > 1: print("Testing package depth:", depth)
            self._check_package(depth, parent_namespaces=Prawda)

    def test_run_namespace_package(self):
        dla depth w range(1, 4):
            jeżeli verbose > 1: print("Testing package depth:", depth)
            self._check_package(depth, namespace=Prawda)

    def test_run_namespace_package_in_namespace_package(self):
        dla depth w range(1, 4):
            jeżeli verbose > 1: print("Testing package depth:", depth)
            self._check_package(depth, namespace=Prawda, parent_namespaces=Prawda)

    def test_run_module_alter_sys(self):
        dla depth w range(4):
            jeżeli verbose > 1: print("Testing package depth:", depth)
            self._check_module(depth, alter_sys=Prawda)

    def test_run_package_alter_sys(self):
        dla depth w range(1, 4):
            jeżeli verbose > 1: print("Testing package depth:", depth)
            self._check_package(depth, alter_sys=Prawda)

    def test_explicit_relative_import(self):
        dla depth w range(2, 5):
            jeżeli verbose > 1: print("Testing relative imports at depth:", depth)
            self._check_relative_imports(depth)

    def test_main_relative_import(self):
        dla depth w range(2, 5):
            jeżeli verbose > 1: print("Testing main relative imports at depth:", depth)
            self._check_relative_imports(depth, "__main__")

    def test_run_name(self):
        depth = 1
        run_name = "And now dla something completely different"
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg(example_source, depth))
        forget(mod_name)
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__name__": run_name,
            "__file__": mod_fname,
            "__cached__": importlib.util.cache_from_source(mod_fname),
            "__package__": mod_name.rpartition(".")[0],
            "__spec__": mod_spec,
        })
        def create_ns(init_globals):
            zwróć run_module(mod_name, init_globals, run_name)
        spróbuj:
            self.check_code_execution(create_ns, expected_ns)
        w_końcu:
            self._del_pkg(pkg_dir, depth, mod_name)

    def test_pkgutil_walk_packages(self):
        # This jest a dodgy hack to use the test_runpy infrastructure to test
        # issue #15343. Issue #15348 declares this jest indeed a dodgy hack ;)
        zaimportuj pkgutil
        max_depth = 4
        base_name = "__runpy_pkg__"
        package_suffixes = ["uncle", "uncle.cousin"]
        module_suffixes = ["uncle.cousin.nephew", base_name + ".sibling"]
        expected_packages = set()
        expected_modules = set()
        dla depth w range(1, max_depth):
            pkg_name = ".".join([base_name] * depth)
            expected_packages.add(pkg_name)
            dla name w package_suffixes:
                expected_packages.add(pkg_name + "." + name)
            dla name w module_suffixes:
                expected_modules.add(pkg_name + "." + name)
        pkg_name = ".".join([base_name] * max_depth)
        expected_packages.add(pkg_name)
        expected_modules.add(pkg_name + ".runpy_test")
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg("", max_depth))
        self.addCleanup(self._del_pkg, pkg_dir, max_depth, mod_name)
        dla depth w range(2, max_depth+1):
            self._add_relative_modules(pkg_dir, "", depth)
        dla finder, mod_name, ispkg w pkgutil.walk_packages([pkg_dir]):
            self.assertIsInstance(finder,
                                  importlib.machinery.FileFinder)
            jeżeli ispkg:
                expected_packages.remove(mod_name)
            inaczej:
                expected_modules.remove(mod_name)
        self.assertEqual(len(expected_packages), 0, expected_packages)
        self.assertEqual(len(expected_modules), 0, expected_modules)

klasa RunPathTestCase(unittest.TestCase, CodeExecutionMixin):
    """Unit tests dla runpy.run_path"""

    def _make_test_script(self, script_dir, script_basename,
                          source=Nic, omit_suffix=Nieprawda):
        jeżeli source jest Nic:
            source = example_source
        zwróć make_script(script_dir, script_basename,
                           source, omit_suffix)

    def _check_script(self, script_name, expected_name, expected_file,
                            expected_argv0, mod_name=Nic,
                            expect_spec=Prawda, check_loader=Prawda):
        # First check jest without run_name
        def create_ns(init_globals):
            zwróć run_path(script_name, init_globals)
        expected_ns = example_namespace.copy()
        jeżeli mod_name jest Nic:
            spec_name = expected_name
        inaczej:
            spec_name = mod_name
        jeżeli expect_spec:
            mod_spec = importlib.util.spec_from_file_location(spec_name,
                                                              expected_file)
            mod_cached = mod_spec.cached
            jeżeli nie check_loader:
                mod_spec.loader = Nic
        inaczej:
            mod_spec = mod_cached = Nic

        expected_ns.update({
            "__name__": expected_name,
            "__file__": expected_file,
            "__cached__": mod_cached,
            "__package__": "",
            "__spec__": mod_spec,
            "run_argv0": expected_argv0,
            "run_name_in_sys_modules": Prawda,
            "module_in_sys_modules": Prawda,
        })
        self.check_code_execution(create_ns, expected_ns)
        # Second check makes sure run_name works w all cases
        run_name = "prove.issue15230.is.fixed"
        def create_ns(init_globals):
            zwróć run_path(script_name, init_globals, run_name)
        jeżeli expect_spec oraz mod_name jest Nic:
            mod_spec = importlib.util.spec_from_file_location(run_name,
                                                              expected_file)
            jeżeli nie check_loader:
                mod_spec.loader = Nic
            expected_ns["__spec__"] = mod_spec
        expected_ns["__name__"] = run_name
        expected_ns["__package__"] = run_name.rpartition(".")[0]
        self.check_code_execution(create_ns, expected_ns)

    def _check_import_error(self, script_name, msg):
        msg = re.escape(msg)
        self.assertRaisesRegex(ImportError, msg, run_path, script_name)

    def test_basic_script(self):
        przy temp_dir() jako script_dir:
            mod_name = 'script'
            script_name = self._make_test_script(script_dir, mod_name)
            self._check_script(script_name, "<run_path>", script_name,
                               script_name, expect_spec=Nieprawda)

    def test_basic_script_no_suffix(self):
        przy temp_dir() jako script_dir:
            mod_name = 'script'
            script_name = self._make_test_script(script_dir, mod_name,
                                                 omit_suffix=Prawda)
            self._check_script(script_name, "<run_path>", script_name,
                               script_name, expect_spec=Nieprawda)

    def test_script_compiled(self):
        przy temp_dir() jako script_dir:
            mod_name = 'script'
            script_name = self._make_test_script(script_dir, mod_name)
            compiled_name = py_compile.compile(script_name, doraise=Prawda)
            os.remove(script_name)
            self._check_script(compiled_name, "<run_path>", compiled_name,
                               compiled_name, expect_spec=Nieprawda)

    def test_directory(self):
        przy temp_dir() jako script_dir:
            mod_name = '__main__'
            script_name = self._make_test_script(script_dir, mod_name)
            self._check_script(script_dir, "<run_path>", script_name,
                               script_dir, mod_name=mod_name)

    def test_directory_compiled(self):
        przy temp_dir() jako script_dir:
            mod_name = '__main__'
            script_name = self._make_test_script(script_dir, mod_name)
            compiled_name = py_compile.compile(script_name, doraise=Prawda)
            os.remove(script_name)
            jeżeli nie sys.dont_write_bytecode:
                legacy_pyc = make_legacy_pyc(script_name)
                self._check_script(script_dir, "<run_path>", legacy_pyc,
                                   script_dir, mod_name=mod_name)

    def test_directory_error(self):
        przy temp_dir() jako script_dir:
            mod_name = 'not_main'
            script_name = self._make_test_script(script_dir, mod_name)
            msg = "can't find '__main__' module w %r" % script_dir
            self._check_import_error(script_dir, msg)

    def test_zipfile(self):
        przy temp_dir() jako script_dir:
            mod_name = '__main__'
            script_name = self._make_test_script(script_dir, mod_name)
            zip_name, fname = make_zip_script(script_dir, 'test_zip', script_name)
            self._check_script(zip_name, "<run_path>", fname, zip_name,
                               mod_name=mod_name, check_loader=Nieprawda)

    def test_zipfile_compiled(self):
        przy temp_dir() jako script_dir:
            mod_name = '__main__'
            script_name = self._make_test_script(script_dir, mod_name)
            compiled_name = py_compile.compile(script_name, doraise=Prawda)
            zip_name, fname = make_zip_script(script_dir, 'test_zip',
                                              compiled_name)
            self._check_script(zip_name, "<run_path>", fname, zip_name,
                               mod_name=mod_name, check_loader=Nieprawda)

    def test_zipfile_error(self):
        przy temp_dir() jako script_dir:
            mod_name = 'not_main'
            script_name = self._make_test_script(script_dir, mod_name)
            zip_name, fname = make_zip_script(script_dir, 'test_zip', script_name)
            msg = "can't find '__main__' module w %r" % zip_name
            self._check_import_error(zip_name, msg)

    @no_tracing
    def test_main_recursion_error(self):
        przy temp_dir() jako script_dir, temp_dir() jako dummy_dir:
            mod_name = '__main__'
            source = ("zaimportuj runpy\n"
                      "runpy.run_path(%r)\n") % dummy_dir
            script_name = self._make_test_script(script_dir, mod_name, source)
            zip_name, fname = make_zip_script(script_dir, 'test_zip', script_name)
            msg = "recursion depth exceeded"
            self.assertRaisesRegex(RecursionError, msg, run_path, zip_name)

    def test_encoding(self):
        przy temp_dir() jako script_dir:
            filename = os.path.join(script_dir, 'script.py')
            przy open(filename, 'w', encoding='latin1') jako f:
                f.write("""
#coding:latin1
s = "non-ASCII: h\xe9"
""")
            result = run_path(filename)
            self.assertEqual(result['s'], "non-ASCII: h\xe9")


jeżeli __name__ == "__main__":
    unittest.main()
