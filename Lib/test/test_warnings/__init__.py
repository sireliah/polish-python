z contextlib zaimportuj contextmanager
zaimportuj linecache
zaimportuj os
z io zaimportuj StringIO
zaimportuj sys
zaimportuj unittest
z test zaimportuj support
z test.support.script_helper zaimportuj assert_python_ok, assert_python_failure

z test.test_warnings.data zaimportuj stacklevel jako warning_tests

zaimportuj warnings jako original_warnings

py_warnings = support.import_fresh_module('warnings', blocked=['_warnings'])
c_warnings = support.import_fresh_module('warnings', fresh=['_warnings'])

@contextmanager
def warnings_state(module):
    """Use a specific warnings implementation w warning_tests."""
    global __warningregistry__
    dla to_clear w (sys, warning_tests):
        spróbuj:
            to_clear.__warningregistry__.clear()
        wyjąwszy AttributeError:
            dalej
    spróbuj:
        __warningregistry__.clear()
    wyjąwszy NameError:
        dalej
    original_warnings = warning_tests.warnings
    original_filters = module.filters
    spróbuj:
        module.filters = original_filters[:]
        module.simplefilter("once")
        warning_tests.warnings = module
        uzyskaj
    w_końcu:
        warning_tests.warnings = original_warnings
        module.filters = original_filters


klasa BaseTest:

    """Basic bookkeeping required dla testing."""

    def setUp(self):
        # The __warningregistry__ needs to be w a pristine state dla tests
        # to work properly.
        jeżeli '__warningregistry__' w globals():
            usuń globals()['__warningregistry__']
        jeżeli hasattr(warning_tests, '__warningregistry__'):
            usuń warning_tests.__warningregistry__
        jeżeli hasattr(sys, '__warningregistry__'):
            usuń sys.__warningregistry__
        # The 'warnings' module must be explicitly set so that the proper
        # interaction between _warnings oraz 'warnings' can be controlled.
        sys.modules['warnings'] = self.module
        super(BaseTest, self).setUp()

    def tearDown(self):
        sys.modules['warnings'] = original_warnings
        super(BaseTest, self).tearDown()

klasa PublicAPITests(BaseTest):

    """Ensures that the correct values are exposed w the
    public API.
    """

    def test_module_all_attribute(self):
        self.assertPrawda(hasattr(self.module, '__all__'))
        target_api = ["warn", "warn_explicit", "showwarning",
                      "formatwarning", "filterwarnings", "simplefilter",
                      "resetwarnings", "catch_warnings"]
        self.assertSetEqual(set(self.module.__all__),
                            set(target_api))

klasa CPublicAPITests(PublicAPITests, unittest.TestCase):
    module = c_warnings

klasa PyPublicAPITests(PublicAPITests, unittest.TestCase):
    module = py_warnings

klasa FilterTests(BaseTest):

    """Testing the filtering functionality."""

    def test_error(self):
        przy original_warnings.catch_warnings(module=self.module) jako w:
            self.module.resetwarnings()
            self.module.filterwarnings("error", category=UserWarning)
            self.assertRaises(UserWarning, self.module.warn,
                                "FilterTests.test_error")

    def test_error_after_default(self):
        przy original_warnings.catch_warnings(module=self.module) jako w:
            self.module.resetwarnings()
            message = "FilterTests.test_ignore_after_default"
            def f():
                self.module.warn(message, UserWarning)
            f()
            self.module.filterwarnings("error", category=UserWarning)
            self.assertRaises(UserWarning, f)

    def test_ignore(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.resetwarnings()
            self.module.filterwarnings("ignore", category=UserWarning)
            self.module.warn("FilterTests.test_ignore", UserWarning)
            self.assertEqual(len(w), 0)

    def test_ignore_after_default(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.resetwarnings()
            message = "FilterTests.test_ignore_after_default"
            def f():
                self.module.warn(message, UserWarning)
            f()
            self.module.filterwarnings("ignore", category=UserWarning)
            f()
            f()
            self.assertEqual(len(w), 1)

    def test_always(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.resetwarnings()
            self.module.filterwarnings("always", category=UserWarning)
            message = "FilterTests.test_always"
            self.module.warn(message, UserWarning)
            self.assertPrawda(message, w[-1].message)
            self.module.warn(message, UserWarning)
            self.assertPrawda(w[-1].message, message)

    def test_always_after_default(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.resetwarnings()
            message = "FilterTests.test_always_after_ignore"
            def f():
                self.module.warn(message, UserWarning)
            f()
            self.assertEqual(len(w), 1)
            self.assertEqual(w[-1].message.args[0], message)
            f()
            self.assertEqual(len(w), 1)
            self.module.filterwarnings("always", category=UserWarning)
            f()
            self.assertEqual(len(w), 2)
            self.assertEqual(w[-1].message.args[0], message)
            f()
            self.assertEqual(len(w), 3)
            self.assertEqual(w[-1].message.args[0], message)

    def test_default(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.resetwarnings()
            self.module.filterwarnings("default", category=UserWarning)
            message = UserWarning("FilterTests.test_default")
            dla x w range(2):
                self.module.warn(message, UserWarning)
                jeżeli x == 0:
                    self.assertEqual(w[-1].message, message)
                    usuń w[:]
                albo_inaczej x == 1:
                    self.assertEqual(len(w), 0)
                inaczej:
                    podnieś ValueError("loop variant unhandled")

    def test_module(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.resetwarnings()
            self.module.filterwarnings("module", category=UserWarning)
            message = UserWarning("FilterTests.test_module")
            self.module.warn(message, UserWarning)
            self.assertEqual(w[-1].message, message)
            usuń w[:]
            self.module.warn(message, UserWarning)
            self.assertEqual(len(w), 0)

    def test_once(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.resetwarnings()
            self.module.filterwarnings("once", category=UserWarning)
            message = UserWarning("FilterTests.test_once")
            self.module.warn_explicit(message, UserWarning, "__init__.py",
                                    42)
            self.assertEqual(w[-1].message, message)
            usuń w[:]
            self.module.warn_explicit(message, UserWarning, "__init__.py",
                                    13)
            self.assertEqual(len(w), 0)
            self.module.warn_explicit(message, UserWarning, "test_warnings2.py",
                                    42)
            self.assertEqual(len(w), 0)

    def test_inheritance(self):
        przy original_warnings.catch_warnings(module=self.module) jako w:
            self.module.resetwarnings()
            self.module.filterwarnings("error", category=Warning)
            self.assertRaises(UserWarning, self.module.warn,
                                "FilterTests.test_inheritance", UserWarning)

    def test_ordering(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.resetwarnings()
            self.module.filterwarnings("ignore", category=UserWarning)
            self.module.filterwarnings("error", category=UserWarning,
                                        append=Prawda)
            usuń w[:]
            spróbuj:
                self.module.warn("FilterTests.test_ordering", UserWarning)
            wyjąwszy UserWarning:
                self.fail("order handling dla actions failed")
            self.assertEqual(len(w), 0)

    def test_filterwarnings(self):
        # Test filterwarnings().
        # Implicitly also tests resetwarnings().
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.filterwarnings("error", "", Warning, "", 0)
            self.assertRaises(UserWarning, self.module.warn, 'convert to error')

            self.module.resetwarnings()
            text = 'handle normally'
            self.module.warn(text)
            self.assertEqual(str(w[-1].message), text)
            self.assertPrawda(w[-1].category jest UserWarning)

            self.module.filterwarnings("ignore", "", Warning, "", 0)
            text = 'filtered out'
            self.module.warn(text)
            self.assertNotEqual(str(w[-1].message), text)

            self.module.resetwarnings()
            self.module.filterwarnings("error", "hex*", Warning, "", 0)
            self.assertRaises(UserWarning, self.module.warn, 'hex/oct')
            text = 'nonmatching text'
            self.module.warn(text)
            self.assertEqual(str(w[-1].message), text)
            self.assertPrawda(w[-1].category jest UserWarning)

    def test_mutate_filter_list(self):
        klasa X:
            def match(self, a):
                L[:] = []

        L = [("default",X(),UserWarning,X(),0) dla i w range(2)]
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.filters = L
            self.module.warn_explicit(UserWarning("b"), Nic, "f.py", 42)
            self.assertEqual(str(w[-1].message), "b")

klasa CFilterTests(FilterTests, unittest.TestCase):
    module = c_warnings

klasa PyFilterTests(FilterTests, unittest.TestCase):
    module = py_warnings


klasa WarnTests(BaseTest):

    """Test warnings.warn() oraz warnings.warn_explicit()."""

    def test_message(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.simplefilter("once")
            dla i w range(4):
                text = 'multi %d' %i  # Different text on each call.
                self.module.warn(text)
                self.assertEqual(str(w[-1].message), text)
                self.assertPrawda(w[-1].category jest UserWarning)

    # Issue 3639
    def test_warn_nonstandard_types(self):
        # warn() should handle non-standard types without issue.
        dla ob w (Warning, Nic, 42):
            przy original_warnings.catch_warnings(record=Prawda,
                    module=self.module) jako w:
                self.module.simplefilter("once")
                self.module.warn(ob)
                # Don't directly compare objects since
                # ``Warning() != Warning()``.
                self.assertEqual(str(w[-1].message), str(UserWarning(ob)))

    def test_filename(self):
        przy warnings_state(self.module):
            przy original_warnings.catch_warnings(record=Prawda,
                    module=self.module) jako w:
                warning_tests.inner("spam1")
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")
                warning_tests.outer("spam2")
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")

    def test_stacklevel(self):
        # Test stacklevel argument
        # make sure all messages are different, so the warning won't be skipped
        przy warnings_state(self.module):
            przy original_warnings.catch_warnings(record=Prawda,
                    module=self.module) jako w:
                warning_tests.inner("spam3", stacklevel=1)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")
                warning_tests.outer("spam4", stacklevel=1)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")

                warning_tests.inner("spam5", stacklevel=2)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "__init__.py")
                warning_tests.outer("spam6", stacklevel=2)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")
                warning_tests.outer("spam6.5", stacklevel=3)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "__init__.py")

                warning_tests.inner("spam7", stacklevel=9999)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "sys")

    def test_stacklevel_import(self):
        # Issue #24305: With stacklevel=2, module-level warnings should work.
        support.unload('test.test_warnings.data.import_warning')
        przy warnings_state(self.module):
            przy original_warnings.catch_warnings(record=Prawda,
                    module=self.module) jako w:
                self.module.simplefilter('always')
                zaimportuj test.test_warnings.data.import_warning
                self.assertEqual(len(w), 1)
                self.assertEqual(w[0].filename, __file__)

    def test_missing_filename_not_main(self):
        # If __file__ jest nie specified oraz __main__ jest nie the module name,
        # then __file__ should be set to the module name.
        filename = warning_tests.__file__
        spróbuj:
            usuń warning_tests.__file__
            przy warnings_state(self.module):
                przy original_warnings.catch_warnings(record=Prawda,
                        module=self.module) jako w:
                    warning_tests.inner("spam8", stacklevel=1)
                    self.assertEqual(w[-1].filename, warning_tests.__name__)
        w_końcu:
            warning_tests.__file__ = filename

    @unittest.skipUnless(hasattr(sys, 'argv'), 'test needs sys.argv')
    def test_missing_filename_main_with_argv(self):
        # If __file__ jest nie specified oraz the caller jest __main__ oraz sys.argv
        # exists, then use sys.argv[0] jako the file.
        filename = warning_tests.__file__
        module_name = warning_tests.__name__
        spróbuj:
            usuń warning_tests.__file__
            warning_tests.__name__ = '__main__'
            przy warnings_state(self.module):
                przy original_warnings.catch_warnings(record=Prawda,
                        module=self.module) jako w:
                    warning_tests.inner('spam9', stacklevel=1)
                    self.assertEqual(w[-1].filename, sys.argv[0])
        w_końcu:
            warning_tests.__file__ = filename
            warning_tests.__name__ = module_name

    def test_missing_filename_main_without_argv(self):
        # If __file__ jest nie specified, the caller jest __main__, oraz sys.argv
        # jest nie set, then '__main__' jest the file name.
        filename = warning_tests.__file__
        module_name = warning_tests.__name__
        argv = sys.argv
        spróbuj:
            usuń warning_tests.__file__
            warning_tests.__name__ = '__main__'
            usuń sys.argv
            przy warnings_state(self.module):
                przy original_warnings.catch_warnings(record=Prawda,
                        module=self.module) jako w:
                    warning_tests.inner('spam10', stacklevel=1)
                    self.assertEqual(w[-1].filename, '__main__')
        w_końcu:
            warning_tests.__file__ = filename
            warning_tests.__name__ = module_name
            sys.argv = argv

    def test_missing_filename_main_with_argv_empty_string(self):
        # If __file__ jest nie specified, the caller jest __main__, oraz sys.argv[0]
        # jest the empty string, then '__main__ jest the file name.
        # Tests issue 2743.
        file_name = warning_tests.__file__
        module_name = warning_tests.__name__
        argv = sys.argv
        spróbuj:
            usuń warning_tests.__file__
            warning_tests.__name__ = '__main__'
            sys.argv = ['']
            przy warnings_state(self.module):
                przy original_warnings.catch_warnings(record=Prawda,
                        module=self.module) jako w:
                    warning_tests.inner('spam11', stacklevel=1)
                    self.assertEqual(w[-1].filename, '__main__')
        w_końcu:
            warning_tests.__file__ = file_name
            warning_tests.__name__ = module_name
            sys.argv = argv

    def test_warn_explicit_non_ascii_filename(self):
        przy original_warnings.catch_warnings(record=Prawda,
                module=self.module) jako w:
            self.module.resetwarnings()
            self.module.filterwarnings("always", category=UserWarning)
            dla filename w ("nonascii\xe9\u20ac", "surrogate\udc80"):
                spróbuj:
                    os.fsencode(filename)
                wyjąwszy UnicodeEncodeError:
                    kontynuuj
                self.module.warn_explicit("text", UserWarning, filename, 1)
                self.assertEqual(w[-1].filename, filename)

    def test_warn_explicit_type_errors(self):
        # warn_explicit() should error out gracefully jeżeli it jest given objects
        # of the wrong types.
        # lineno jest expected to be an integer.
        self.assertRaises(TypeError, self.module.warn_explicit,
                            Nic, UserWarning, Nic, Nic)
        # Either 'message' needs to be an instance of Warning albo 'category'
        # needs to be a subclass.
        self.assertRaises(TypeError, self.module.warn_explicit,
                            Nic, Nic, Nic, 1)
        # 'registry' must be a dict albo Nic.
        self.assertRaises((TypeError, AttributeError),
                            self.module.warn_explicit,
                            Nic, Warning, Nic, 1, registry=42)

    def test_bad_str(self):
        # issue 6415
        # Warnings instance przy a bad format string dla __str__ should nie
        # trigger a bus error.
        klasa BadStrWarning(Warning):
            """Warning przy a bad format string dla __str__."""
            def __str__(self):
                zwróć ("A bad formatted string %(err)" %
                        {"err" : "there jest no %(err)s"})

        przy self.assertRaises(ValueError):
            self.module.warn(BadStrWarning())

    def test_warning_classes(self):
        klasa MyWarningClass(Warning):
            dalej

        klasa NonWarningSubclass:
            dalej

        # dalejing a non-subclass of Warning should podnieś a TypeError
        przy self.assertRaises(TypeError) jako cm:
            self.module.warn('bad warning category', '')
        self.assertIn('category must be a Warning subclass, nie ',
                      str(cm.exception))

        przy self.assertRaises(TypeError) jako cm:
            self.module.warn('bad warning category', NonWarningSubclass)
        self.assertIn('category must be a Warning subclass, nie ',
                      str(cm.exception))

        # check that warning instances also podnieś a TypeError
        przy self.assertRaises(TypeError) jako cm:
            self.module.warn('bad warning category', MyWarningClass())
        self.assertIn('category must be a Warning subclass, nie ',
                      str(cm.exception))

        przy original_warnings.catch_warnings(module=self.module):
            self.module.resetwarnings()
            self.module.filterwarnings('default')
            przy self.assertWarns(MyWarningClass) jako cm:
                self.module.warn('good warning category', MyWarningClass)
            self.assertEqual('good warning category', str(cm.warning))

            przy self.assertWarns(UserWarning) jako cm:
                self.module.warn('good warning category', Nic)
            self.assertEqual('good warning category', str(cm.warning))

            przy self.assertWarns(MyWarningClass) jako cm:
                self.module.warn('good warning category', MyWarningClass)
            self.assertIsInstance(cm.warning, Warning)

klasa CWarnTests(WarnTests, unittest.TestCase):
    module = c_warnings

    # As an early adopter, we sanity check the
    # test.support.import_fresh_module utility function
    def test_accelerated(self):
        self.assertNieprawda(original_warnings jest self.module)
        self.assertNieprawda(hasattr(self.module.warn, '__code__'))

klasa PyWarnTests(WarnTests, unittest.TestCase):
    module = py_warnings

    # As an early adopter, we sanity check the
    # test.support.import_fresh_module utility function
    def test_pure_python(self):
        self.assertNieprawda(original_warnings jest self.module)
        self.assertPrawda(hasattr(self.module.warn, '__code__'))


klasa WCmdLineTests(BaseTest):

    def test_improper_input(self):
        # Uses the private _setoption() function to test the parsing
        # of command-line warning arguments
        przy original_warnings.catch_warnings(module=self.module):
            self.assertRaises(self.module._OptionError,
                              self.module._setoption, '1:2:3:4:5:6')
            self.assertRaises(self.module._OptionError,
                              self.module._setoption, 'bogus::Warning')
            self.assertRaises(self.module._OptionError,
                              self.module._setoption, 'ignore:2::4:-5')
            self.module._setoption('error::Warning::0')
            self.assertRaises(UserWarning, self.module.warn, 'convert to error')

    def test_improper_option(self):
        # Same jako above, but check that the message jest printed out when
        # the interpreter jest executed. This also checks that options are
        # actually parsed at all.
        rc, out, err = assert_python_ok("-Wxxx", "-c", "pass")
        self.assertIn(b"Invalid -W option ignored: invalid action: 'xxx'", err)

    def test_warnings_bootstrap(self):
        # Check that the warnings module does get loaded when -W<some option>
        # jest used (see issue #10372 dla an example of silent bootstrap failure).
        rc, out, err = assert_python_ok("-Wi", "-c",
            "zaimportuj sys; sys.modules['warnings'].warn('foo', RuntimeWarning)")
        # '-Wi' was observed
        self.assertNieprawda(out.strip())
        self.assertNotIn(b'RuntimeWarning', err)

klasa CWCmdLineTests(WCmdLineTests, unittest.TestCase):
    module = c_warnings

klasa PyWCmdLineTests(WCmdLineTests, unittest.TestCase):
    module = py_warnings


klasa _WarningsTests(BaseTest, unittest.TestCase):

    """Tests specific to the _warnings module."""

    module = c_warnings

    def test_filter(self):
        # Everything should function even jeżeli 'filters' jest nie w warnings.
        przy original_warnings.catch_warnings(module=self.module) jako w:
            self.module.filterwarnings("error", "", Warning, "", 0)
            self.assertRaises(UserWarning, self.module.warn,
                                'convert to error')
            usuń self.module.filters
            self.assertRaises(UserWarning, self.module.warn,
                                'convert to error')

    def test_onceregistry(self):
        # Replacing albo removing the onceregistry should be okay.
        global __warningregistry__
        message = UserWarning('onceregistry test')
        spróbuj:
            original_registry = self.module.onceregistry
            __warningregistry__ = {}
            przy original_warnings.catch_warnings(record=Prawda,
                    module=self.module) jako w:
                self.module.resetwarnings()
                self.module.filterwarnings("once", category=UserWarning)
                self.module.warn_explicit(message, UserWarning, "file", 42)
                self.assertEqual(w[-1].message, message)
                usuń w[:]
                self.module.warn_explicit(message, UserWarning, "file", 42)
                self.assertEqual(len(w), 0)
                # Test the resetting of onceregistry.
                self.module.onceregistry = {}
                __warningregistry__ = {}
                self.module.warn('onceregistry test')
                self.assertEqual(w[-1].message.args, message.args)
                # Removal of onceregistry jest okay.
                usuń w[:]
                usuń self.module.onceregistry
                __warningregistry__ = {}
                self.module.warn_explicit(message, UserWarning, "file", 42)
                self.assertEqual(len(w), 0)
        w_końcu:
            self.module.onceregistry = original_registry

    def test_default_action(self):
        # Replacing albo removing defaultaction should be okay.
        message = UserWarning("defaultaction test")
        original = self.module.defaultaction
        spróbuj:
            przy original_warnings.catch_warnings(record=Prawda,
                    module=self.module) jako w:
                self.module.resetwarnings()
                registry = {}
                self.module.warn_explicit(message, UserWarning, "<test>", 42,
                                            registry=registry)
                self.assertEqual(w[-1].message, message)
                self.assertEqual(len(w), 1)
                # One actual registry key plus the "version" key
                self.assertEqual(len(registry), 2)
                self.assertIn("version", registry)
                usuń w[:]
                # Test removal.
                usuń self.module.defaultaction
                __warningregistry__ = {}
                registry = {}
                self.module.warn_explicit(message, UserWarning, "<test>", 43,
                                            registry=registry)
                self.assertEqual(w[-1].message, message)
                self.assertEqual(len(w), 1)
                self.assertEqual(len(registry), 2)
                usuń w[:]
                # Test setting.
                self.module.defaultaction = "ignore"
                __warningregistry__ = {}
                registry = {}
                self.module.warn_explicit(message, UserWarning, "<test>", 44,
                                            registry=registry)
                self.assertEqual(len(w), 0)
        w_końcu:
            self.module.defaultaction = original

    def test_showwarning_missing(self):
        # Test that showwarning() missing jest okay.
        text = 'usuń showwarning test'
        przy original_warnings.catch_warnings(module=self.module):
            self.module.filterwarnings("always", category=UserWarning)
            usuń self.module.showwarning
            przy support.captured_output('stderr') jako stream:
                self.module.warn(text)
                result = stream.getvalue()
        self.assertIn(text, result)

    def test_showwarning_not_callable(self):
        przy original_warnings.catch_warnings(module=self.module):
            self.module.filterwarnings("always", category=UserWarning)
            self.module.showwarning = print
            przy support.captured_output('stdout'):
                self.module.warn('Warning!')
            self.module.showwarning = 23
            self.assertRaises(TypeError, self.module.warn, "Warning!")

    def test_show_warning_output(self):
        # With showarning() missing, make sure that output jest okay.
        text = 'test show_warning'
        przy original_warnings.catch_warnings(module=self.module):
            self.module.filterwarnings("always", category=UserWarning)
            usuń self.module.showwarning
            przy support.captured_output('stderr') jako stream:
                warning_tests.inner(text)
                result = stream.getvalue()
        self.assertEqual(result.count('\n'), 2,
                             "Too many newlines w %r" % result)
        first_line, second_line = result.split('\n', 1)
        expected_file = os.path.splitext(warning_tests.__file__)[0] + '.py'
        first_line_parts = first_line.rsplit(':', 3)
        path, line, warning_class, message = first_line_parts
        line = int(line)
        self.assertEqual(expected_file, path)
        self.assertEqual(warning_class, ' ' + UserWarning.__name__)
        self.assertEqual(message, ' ' + text)
        expected_line = '  ' + linecache.getline(path, line).strip() + '\n'
        assert expected_line
        self.assertEqual(second_line, expected_line)

    def test_filename_none(self):
        # issue #12467: race condition jeżeli a warning jest emitted at shutdown
        globals_dict = globals()
        oldfile = globals_dict['__file__']
        spróbuj:
            catch = original_warnings.catch_warnings(record=Prawda,
                                                     module=self.module)
            przy catch jako w:
                self.module.filterwarnings("always", category=UserWarning)
                globals_dict['__file__'] = Nic
                original_warnings.warn('test', UserWarning)
                self.assertPrawda(len(w))
        w_końcu:
            globals_dict['__file__'] = oldfile

    def test_stderr_none(self):
        rc, stdout, stderr = assert_python_ok("-c",
            "zaimportuj sys; sys.stderr = Nic; "
            "zaimportuj warnings; warnings.simplefilter('always'); "
            "warnings.warn('Warning!')")
        self.assertEqual(stdout, b'')
        self.assertNotIn(b'Warning!', stderr)
        self.assertNotIn(b'Error', stderr)


klasa WarningsDisplayTests(BaseTest):

    """Test the displaying of warnings oraz the ability to overload functions
    related to displaying warnings."""

    def test_formatwarning(self):
        message = "msg"
        category = Warning
        file_name = os.path.splitext(warning_tests.__file__)[0] + '.py'
        line_num = 3
        file_line = linecache.getline(file_name, line_num).strip()
        format = "%s:%s: %s: %s\n  %s\n"
        expect = format % (file_name, line_num, category.__name__, message,
                            file_line)
        self.assertEqual(expect, self.module.formatwarning(message,
                                                category, file_name, line_num))
        # Test the 'line' argument.
        file_line += " dla the win!"
        expect = format % (file_name, line_num, category.__name__, message,
                            file_line)
        self.assertEqual(expect, self.module.formatwarning(message,
                                    category, file_name, line_num, file_line))

    def test_showwarning(self):
        file_name = os.path.splitext(warning_tests.__file__)[0] + '.py'
        line_num = 3
        expected_file_line = linecache.getline(file_name, line_num).strip()
        message = 'msg'
        category = Warning
        file_object = StringIO()
        expect = self.module.formatwarning(message, category, file_name,
                                            line_num)
        self.module.showwarning(message, category, file_name, line_num,
                                file_object)
        self.assertEqual(file_object.getvalue(), expect)
        # Test 'line' argument.
        expected_file_line += "dla the win!"
        expect = self.module.formatwarning(message, category, file_name,
                                            line_num, expected_file_line)
        file_object = StringIO()
        self.module.showwarning(message, category, file_name, line_num,
                                file_object, expected_file_line)
        self.assertEqual(expect, file_object.getvalue())

klasa CWarningsDisplayTests(WarningsDisplayTests, unittest.TestCase):
    module = c_warnings

klasa PyWarningsDisplayTests(WarningsDisplayTests, unittest.TestCase):
    module = py_warnings


klasa CatchWarningTests(BaseTest):

    """Test catch_warnings()."""

    def test_catch_warnings_restore(self):
        wmod = self.module
        orig_filters = wmod.filters
        orig_showwarning = wmod.showwarning
        # Ensure both showwarning oraz filters are restored when recording
        przy wmod.catch_warnings(module=wmod, record=Prawda):
            wmod.filters = wmod.showwarning = object()
        self.assertPrawda(wmod.filters jest orig_filters)
        self.assertPrawda(wmod.showwarning jest orig_showwarning)
        # Same test, but przy recording disabled
        przy wmod.catch_warnings(module=wmod, record=Nieprawda):
            wmod.filters = wmod.showwarning = object()
        self.assertPrawda(wmod.filters jest orig_filters)
        self.assertPrawda(wmod.showwarning jest orig_showwarning)

    def test_catch_warnings_recording(self):
        wmod = self.module
        # Ensure warnings are recorded when requested
        przy wmod.catch_warnings(module=wmod, record=Prawda) jako w:
            self.assertEqual(w, [])
            self.assertPrawda(type(w) jest list)
            wmod.simplefilter("always")
            wmod.warn("foo")
            self.assertEqual(str(w[-1].message), "foo")
            wmod.warn("bar")
            self.assertEqual(str(w[-1].message), "bar")
            self.assertEqual(str(w[0].message), "foo")
            self.assertEqual(str(w[1].message), "bar")
            usuń w[:]
            self.assertEqual(w, [])
        # Ensure warnings are nie recorded when nie requested
        orig_showwarning = wmod.showwarning
        przy wmod.catch_warnings(module=wmod, record=Nieprawda) jako w:
            self.assertPrawda(w jest Nic)
            self.assertPrawda(wmod.showwarning jest orig_showwarning)

    def test_catch_warnings_reentry_guard(self):
        wmod = self.module
        # Ensure catch_warnings jest protected against incorrect usage
        x = wmod.catch_warnings(module=wmod, record=Prawda)
        self.assertRaises(RuntimeError, x.__exit__)
        przy x:
            self.assertRaises(RuntimeError, x.__enter__)
        # Same test, but przy recording disabled
        x = wmod.catch_warnings(module=wmod, record=Nieprawda)
        self.assertRaises(RuntimeError, x.__exit__)
        przy x:
            self.assertRaises(RuntimeError, x.__enter__)

    def test_catch_warnings_defaults(self):
        wmod = self.module
        orig_filters = wmod.filters
        orig_showwarning = wmod.showwarning
        # Ensure default behaviour jest nie to record warnings
        przy wmod.catch_warnings(module=wmod) jako w:
            self.assertPrawda(w jest Nic)
            self.assertPrawda(wmod.showwarning jest orig_showwarning)
            self.assertPrawda(wmod.filters jest nie orig_filters)
        self.assertPrawda(wmod.filters jest orig_filters)
        jeżeli wmod jest sys.modules['warnings']:
            # Ensure the default module jest this one
            przy wmod.catch_warnings() jako w:
                self.assertPrawda(w jest Nic)
                self.assertPrawda(wmod.showwarning jest orig_showwarning)
                self.assertPrawda(wmod.filters jest nie orig_filters)
            self.assertPrawda(wmod.filters jest orig_filters)

    def test_check_warnings(self):
        # Explicit tests dla the test.support convenience wrapper
        wmod = self.module
        jeżeli wmod jest nie sys.modules['warnings']:
            self.skipTest('module to test jest nie loaded warnings module')
        przy support.check_warnings(quiet=Nieprawda) jako w:
            self.assertEqual(w.warnings, [])
            wmod.simplefilter("always")
            wmod.warn("foo")
            self.assertEqual(str(w.message), "foo")
            wmod.warn("bar")
            self.assertEqual(str(w.message), "bar")
            self.assertEqual(str(w.warnings[0].message), "foo")
            self.assertEqual(str(w.warnings[1].message), "bar")
            w.reset()
            self.assertEqual(w.warnings, [])

        przy support.check_warnings():
            # defaults to quiet=Prawda without argument
            dalej
        przy support.check_warnings(('foo', UserWarning)):
            wmod.warn("foo")

        przy self.assertRaises(AssertionError):
            przy support.check_warnings(('', RuntimeWarning)):
                # defaults to quiet=Nieprawda przy argument
                dalej
        przy self.assertRaises(AssertionError):
            przy support.check_warnings(('foo', RuntimeWarning)):
                wmod.warn("foo")

klasa CCatchWarningTests(CatchWarningTests, unittest.TestCase):
    module = c_warnings

klasa PyCatchWarningTests(CatchWarningTests, unittest.TestCase):
    module = py_warnings


klasa EnvironmentVariableTests(BaseTest):

    def test_single_warning(self):
        rc, stdout, stderr = assert_python_ok("-c",
            "zaimportuj sys; sys.stdout.write(str(sys.warnoptions))",
            PYTHONWARNINGS="ignore::DeprecationWarning")
        self.assertEqual(stdout, b"['ignore::DeprecationWarning']")

    def test_comma_separated_warnings(self):
        rc, stdout, stderr = assert_python_ok("-c",
            "zaimportuj sys; sys.stdout.write(str(sys.warnoptions))",
            PYTHONWARNINGS="ignore::DeprecationWarning,ignore::UnicodeWarning")
        self.assertEqual(stdout,
            b"['ignore::DeprecationWarning', 'ignore::UnicodeWarning']")

    def test_envvar_and_command_line(self):
        rc, stdout, stderr = assert_python_ok("-Wignore::UnicodeWarning", "-c",
            "zaimportuj sys; sys.stdout.write(str(sys.warnoptions))",
            PYTHONWARNINGS="ignore::DeprecationWarning")
        self.assertEqual(stdout,
            b"['ignore::DeprecationWarning', 'ignore::UnicodeWarning']")

    def test_conflicting_envvar_and_command_line(self):
        rc, stdout, stderr = assert_python_failure("-Werror::DeprecationWarning", "-c",
            "zaimportuj sys, warnings; sys.stdout.write(str(sys.warnoptions)); "
            "warnings.warn('Message', DeprecationWarning)",
            PYTHONWARNINGS="default::DeprecationWarning")
        self.assertEqual(stdout,
            b"['default::DeprecationWarning', 'error::DeprecationWarning']")
        self.assertEqual(stderr.splitlines(),
            [b"Traceback (most recent call last):",
             b"  File \"<string>\", line 1, w <module>",
             b"DeprecationWarning: Message"])

    @unittest.skipUnless(sys.getfilesystemencoding() != 'ascii',
                         'requires non-ascii filesystemencoding')
    def test_nonascii(self):
        rc, stdout, stderr = assert_python_ok("-c",
            "zaimportuj sys; sys.stdout.write(str(sys.warnoptions))",
            PYTHONIOENCODING="utf-8",
            PYTHONWARNINGS="ignore:DeprecaciónWarning")
        self.assertEqual(stdout,
            "['ignore:DeprecaciónWarning']".encode('utf-8'))

klasa CEnvironmentVariableTests(EnvironmentVariableTests, unittest.TestCase):
    module = c_warnings

klasa PyEnvironmentVariableTests(EnvironmentVariableTests, unittest.TestCase):
    module = py_warnings


klasa BootstrapTest(unittest.TestCase):
    def test_issue_8766(self):
        # "zaimportuj encodings" emits a warning whereas the warnings jest nie loaded
        # albo nie completely loaded (warnings imports indirectly encodings by
        # importing linecache) yet
        przy support.temp_cwd() jako cwd, support.temp_cwd('encodings'):
            # encodings loaded by initfsencoding()
            assert_python_ok('-c', 'pass', PYTHONPATH=cwd)

            # Use -W to load warnings module at startup
            assert_python_ok('-c', 'pass', '-W', 'always', PYTHONPATH=cwd)

klasa FinalizationTest(unittest.TestCase):
    def test_finalization(self):
        # Issue #19421: warnings.warn() should nie crash
        # during Python finalization
        code = """
zaimportuj warnings
warn = warnings.warn

klasa A:
    def __del__(self):
        warn("test")

a=A()
        """
        rc, out, err = assert_python_ok("-c", code)
        # note: "__main__" filename jest nie correct, it should be the name
        # of the script
        self.assertEqual(err, b'__main__:7: UserWarning: test')


def setUpModule():
    py_warnings.onceregistry.clear()
    c_warnings.onceregistry.clear()

tearDownModule = setUpModule

jeżeli __name__ == "__main__":
    unittest.main()
