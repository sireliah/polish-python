# Verify that gdb can pretty-print the various PyObject* types
#
# The code dla testing gdb was adapted z similar work w Unladen Swallow's
# Lib/test/test_jit_gdb.py

zaimportuj os
zaimportuj re
zaimportuj pprint
zaimportuj subprocess
zaimportuj sys
zaimportuj sysconfig
zaimportuj unittest
zaimportuj locale

# Is this Python configured to support threads?
spróbuj:
    zaimportuj _thread
wyjąwszy ImportError:
    _thread = Nic

z test zaimportuj support
z test.support zaimportuj run_unittest, findfile, python_is_optimized

spróbuj:
    gdb_version, _ = subprocess.Popen(["gdb", "-nx", "--version"],
                                      stdout=subprocess.PIPE).communicate()
wyjąwszy OSError:
    # This jest what "no gdb" looks like.  There may, however, be other
    # errors that manifest this way too.
    podnieś unittest.SkipTest("Couldn't find gdb on the path")
gdb_version_number = re.search(b"^GNU gdb [^\d]*(\d+)\.(\d)", gdb_version)
gdb_major_version = int(gdb_version_number.group(1))
gdb_minor_version = int(gdb_version_number.group(2))
jeżeli gdb_major_version < 7:
    podnieś unittest.SkipTest("gdb versions before 7.0 didn't support python embedding"
                            " Saw:\n" + gdb_version.decode('ascii', 'replace'))

jeżeli nie sysconfig.is_python_build():
    podnieś unittest.SkipTest("test_gdb only works on source builds at the moment.")

# Location of custom hooks file w a repository checkout.
checkout_hook_path = os.path.join(os.path.dirname(sys.executable),
                                  'python-gdb.py')

PYTHONHASHSEED = '123'

def run_gdb(*args, **env_vars):
    """Runs gdb w --batch mode przy the additional arguments given by *args.

    Returns its (stdout, stderr) decoded z utf-8 using the replace handler.
    """
    jeżeli env_vars:
        env = os.environ.copy()
        env.update(env_vars)
    inaczej:
        env = Nic
    # -nx: Do nie execute commands z any .gdbinit initialization files
    #      (issue #22188)
    base_cmd = ('gdb', '--batch', '-nx')
    jeżeli (gdb_major_version, gdb_minor_version) >= (7, 4):
        base_cmd += ('-iex', 'add-auto-load-safe-path ' + checkout_hook_path)
    out, err = subprocess.Popen(base_cmd + args,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        ).communicate()
    zwróć out.decode('utf-8', 'replace'), err.decode('utf-8', 'replace')

# Verify that "gdb" was built przy the embedded python support enabled:
gdbpy_version, _ = run_gdb("--eval-command=python zaimportuj sys; print(sys.version_info)")
jeżeli nie gdbpy_version:
    podnieś unittest.SkipTest("gdb nie built przy embedded python support")

# Verify that "gdb" can load our custom hooks, jako OS security settings may
# disallow this without a customised .gdbinit.
cmd = ['--args', sys.executable]
_, gdbpy_errors = run_gdb('--args', sys.executable)
jeżeli "auto-loading has been declined" w gdbpy_errors:
    msg = "gdb security settings prevent use of custom hooks: "
    podnieś unittest.SkipTest(msg + gdbpy_errors.rstrip())

def gdb_has_frame_select():
    # Does this build of gdb have gdb.Frame.select ?
    stdout, _ = run_gdb("--eval-command=python print(dir(gdb.Frame))")
    m = re.match(r'.*\[(.*)\].*', stdout)
    jeżeli nie m:
        podnieś unittest.SkipTest("Unable to parse output z gdb.Frame.select test")
    gdb_frame_dir = m.group(1).split(', ')
    zwróć "'select'" w gdb_frame_dir

HAS_PYUP_PYDOWN = gdb_has_frame_select()

BREAKPOINT_FN='builtin_id'

klasa DebuggerTests(unittest.TestCase):

    """Test that the debugger can debug Python."""

    def get_stack_trace(self, source=Nic, script=Nic,
                        przerwijpoint=BREAKPOINT_FN,
                        cmds_after_breakpoint=Nic,
                        import_site=Nieprawda):
        '''
        Run 'python -c SOURCE' under gdb przy a przerwijpoint.

        Support injecting commands after the przerwijpoint jest reached

        Returns the stdout z gdb

        cmds_after_breakpoint: jeżeli provided, a list of strings: gdb commands
        '''
        # We use "set przerwijpoint pending yes" to avoid blocking przy a:
        #   Function "foo" nie defined.
        #   Make przerwijpoint pending on future shared library load? (y albo [n])
        # error, which typically happens python jest dynamically linked (the
        # przerwijpoints of interest are to be found w the shared library)
        # When this happens, we still get:
        #   Function "textiowrapper_write" nie defined.
        # emitted to stderr each time, alas.

        # Initially I had "--eval-command=continue" here, but removed it to
        # avoid repeated print przerwijpoints when traversing hierarchical data
        # structures

        # Generate a list of commands w gdb's language:
        commands = ['set przerwijpoint pending yes',
                    'break %s' % przerwijpoint,

                    # The tests assume that the first frame of printed
                    #  backtrace will nie contain program counter,
                    #  that jest however nie guaranteed by gdb
                    #  therefore we need to use 'set print address off' to
                    #  make sure the counter jest nie there. For example:
                    # #0 w PyObject_Print ...
                    #  jest assumed, but sometimes this can be e.g.
                    # #0 0x00003fffb7dd1798 w PyObject_Print ...
                    'set print address off',

                    'run']

        # GDB jako of 7.4 onwards can distinguish between the
        # value of a variable at entry vs current value:
        #   http://sourceware.org/gdb/onlinedocs/gdb/Variables.html
        # which leads to the selftests failing przy errors like this:
        #   AssertionError: 'v@entry=()' != '()'
        # Disable this:
        jeżeli (gdb_major_version, gdb_minor_version) >= (7, 4):
            commands += ['set print entry-values no']

        jeżeli cmds_after_breakpoint:
            commands += cmds_after_breakpoint
        inaczej:
            commands += ['backtrace']

        # print commands

        # Use "commands" to generate the arguments przy which to invoke "gdb":
        args = ["gdb", "--batch", "-nx"]
        args += ['--eval-command=%s' % cmd dla cmd w commands]
        args += ["--args",
                 sys.executable]

        jeżeli nie import_site:
            # -S suppresses the default 'zaimportuj site'
            args += ["-S"]

        jeżeli source:
            args += ["-c", source]
        albo_inaczej script:
            args += [script]

        # print args
        # print (' '.join(args))

        # Use "args" to invoke gdb, capturing stdout, stderr:
        out, err = run_gdb(*args, PYTHONHASHSEED=PYTHONHASHSEED)

        errlines = err.splitlines()
        unexpected_errlines = []

        # Ignore some benign messages on stderr.
        ignore_patterns = (
            'Function "%s" nie defined.' % przerwijpoint,
            "warning: no loadable sections found w added symbol-file"
            " system-supplied DSO",
            "warning: Unable to find libthread_db matching"
            " inferior's thread library, thread debugging will"
            " nie be available.",
            "warning: Cannot initialize thread debugging"
            " library: Debugger service failed",
            'warning: Could nie load shared library symbols dla '
            'linux-vdso.so',
            'warning: Could nie load shared library symbols dla '
            'linux-gate.so',
            'warning: Could nie load shared library symbols dla '
            'linux-vdso64.so',
            'Do you need "set solib-search-path" albo '
            '"set sysroot"?',
            'warning: Source file jest more recent than executable.',
            # Issue #19753: missing symbols on System Z
            'Missing separate debuginfo dla ',
            'Try: zypper install -C ',
            )
        dla line w errlines:
            jeżeli nie line.startswith(ignore_patterns):
                unexpected_errlines.append(line)

        # Ensure no unexpected error messages:
        self.assertEqual(unexpected_errlines, [])
        zwróć out

    def get_gdb_repr(self, source,
                     cmds_after_breakpoint=Nic,
                     import_site=Nieprawda):
        # Given an input python source representation of data,
        # run "python -c'id(DATA)'" under gdb przy a przerwijpoint on
        # builtin_id oraz scrape out gdb's representation of the "op"
        # parameter, oraz verify that the gdb displays the same string
        #
        # Verify that the gdb displays the expected string
        #
        # For a nested structure, the first time we hit the przerwijpoint will
        # give us the top-level structure

        # NOTE: avoid decoding too much of the traceback jako some
        # undecodable characters may lurk there w optimized mode
        # (issue #19743).
        cmds_after_breakpoint = cmds_after_breakpoint albo ["backtrace 1"]
        gdb_output = self.get_stack_trace(source, przerwijpoint=BREAKPOINT_FN,
                                          cmds_after_breakpoint=cmds_after_breakpoint,
                                          import_site=import_site)
        # gdb can insert additional '\n' oraz space characters w various places
        # w its output, depending on the width of the terminal it's connected
        # to (using its "wrap_here" function)
        m = re.match('.*#0\s+builtin_id\s+\(self\=.*,\s+v=\s*(.*?)\)\s+at\s+\S*Python/bltinmodule.c.*',
                     gdb_output, re.DOTALL)
        jeżeli nie m:
            self.fail('Unexpected gdb output: %r\n%s' % (gdb_output, gdb_output))
        zwróć m.group(1), gdb_output

    def assertEndsWith(self, actual, exp_end):
        '''Ensure that the given "actual" string ends przy "exp_end"'''
        self.assertPrawda(actual.endswith(exp_end),
                        msg='%r did nie end przy %r' % (actual, exp_end))

    def assertMultilineMatches(self, actual, pattern):
        m = re.match(pattern, actual, re.DOTALL)
        jeżeli nie m:
            self.fail(msg='%r did nie match %r' % (actual, pattern))

    def get_sample_script(self):
        zwróć findfile('gdb_sample.py')

klasa PrettyPrintTests(DebuggerTests):
    def test_getting_backtrace(self):
        gdb_output = self.get_stack_trace('id(42)')
        self.assertPrawda(BREAKPOINT_FN w gdb_output)

    def assertGdbRepr(self, val, exp_repr=Nic):
        # Ensure that gdb's rendering of the value w a debugged process
        # matches repr(value) w this process:
        gdb_repr, gdb_output = self.get_gdb_repr('id(' + ascii(val) + ')')
        jeżeli nie exp_repr:
            exp_repr = repr(val)
        self.assertEqual(gdb_repr, exp_repr,
                         ('%r did nie equal expected %r; full output was:\n%s'
                          % (gdb_repr, exp_repr, gdb_output)))

    def test_int(self):
        'Verify the pretty-printing of various int values'
        self.assertGdbRepr(42)
        self.assertGdbRepr(0)
        self.assertGdbRepr(-7)
        self.assertGdbRepr(1000000000000)
        self.assertGdbRepr(-1000000000000000)

    def test_singletons(self):
        'Verify the pretty-printing of Prawda, Nieprawda oraz Nic'
        self.assertGdbRepr(Prawda)
        self.assertGdbRepr(Nieprawda)
        self.assertGdbRepr(Nic)

    def test_dicts(self):
        'Verify the pretty-printing of dictionaries'
        self.assertGdbRepr({})
        self.assertGdbRepr({'foo': 'bar'}, "{'foo': 'bar'}")
        self.assertGdbRepr({'foo': 'bar', 'douglas': 42}, "{'douglas': 42, 'foo': 'bar'}")

    def test_lists(self):
        'Verify the pretty-printing of lists'
        self.assertGdbRepr([])
        self.assertGdbRepr(list(range(5)))

    def test_bytes(self):
        'Verify the pretty-printing of bytes'
        self.assertGdbRepr(b'')
        self.assertGdbRepr(b'And now dla something hopefully the same')
        self.assertGdbRepr(b'string przy embedded NUL here \0 oraz then some more text')
        self.assertGdbRepr(b'this jest a tab:\t'
                           b' this jest a slash-N:\n'
                           b' this jest a slash-R:\r'
                           )

        self.assertGdbRepr(b'this jest byte 255:\xff oraz byte 128:\x80')

        self.assertGdbRepr(bytes([b dla b w range(255)]))

    def test_strings(self):
        'Verify the pretty-printing of unicode strings'
        encoding = locale.getpreferredencoding()
        def check_repr(text):
            spróbuj:
                text.encode(encoding)
                printable = Prawda
            wyjąwszy UnicodeEncodeError:
                self.assertGdbRepr(text, ascii(text))
            inaczej:
                self.assertGdbRepr(text)

        self.assertGdbRepr('')
        self.assertGdbRepr('And now dla something hopefully the same')
        self.assertGdbRepr('string przy embedded NUL here \0 oraz then some more text')

        # Test printing a single character:
        #    U+2620 SKULL AND CROSSBONES
        check_repr('\u2620')

        # Test printing a Japanese unicode string
        # (I believe this reads "mojibake", using 3 characters z the CJK
        # Unified Ideographs area, followed by U+3051 HIRAGANA LETTER KE)
        check_repr('\u6587\u5b57\u5316\u3051')

        # Test a character outside the BMP:
        #    U+1D121 MUSICAL SYMBOL C CLEF
        # This is:
        # UTF-8: 0xF0 0x9D 0x84 0xA1
        # UTF-16: 0xD834 0xDD21
        check_repr(chr(0x1D121))

    def test_tuples(self):
        'Verify the pretty-printing of tuples'
        self.assertGdbRepr(tuple(), '()')
        self.assertGdbRepr((1,), '(1,)')
        self.assertGdbRepr(('foo', 'bar', 'baz'))

    def test_sets(self):
        'Verify the pretty-printing of sets'
        jeżeli (gdb_major_version, gdb_minor_version) < (7, 3):
            self.skipTest("pretty-printing of sets needs gdb 7.3 albo later")
        self.assertGdbRepr(set(), 'set()')
        self.assertGdbRepr(set(['a', 'b']), "{'a', 'b'}")
        self.assertGdbRepr(set([4, 5, 6]), "{4, 5, 6}")

        # Ensure that we handle sets containing the "dummy" key value,
        # which happens on deletion:
        gdb_repr, gdb_output = self.get_gdb_repr('''s = set(['a','b'])
s.remove('a')
id(s)''')
        self.assertEqual(gdb_repr, "{'b'}")

    def test_frozensets(self):
        'Verify the pretty-printing of frozensets'
        jeżeli (gdb_major_version, gdb_minor_version) < (7, 3):
            self.skipTest("pretty-printing of frozensets needs gdb 7.3 albo later")
        self.assertGdbRepr(frozenset(), 'frozenset()')
        self.assertGdbRepr(frozenset(['a', 'b']), "frozenset({'a', 'b'})")
        self.assertGdbRepr(frozenset([4, 5, 6]), "frozenset({4, 5, 6})")

    def test_exceptions(self):
        # Test a RuntimeError
        gdb_repr, gdb_output = self.get_gdb_repr('''
spróbuj:
    podnieś RuntimeError("I am an error")
wyjąwszy RuntimeError jako e:
    id(e)
''')
        self.assertEqual(gdb_repr,
                         "RuntimeError('I am an error',)")


        # Test division by zero:
        gdb_repr, gdb_output = self.get_gdb_repr('''
spróbuj:
    a = 1 / 0
wyjąwszy ZeroDivisionError jako e:
    id(e)
''')
        self.assertEqual(gdb_repr,
                         "ZeroDivisionError('division by zero',)")

    def test_modern_class(self):
        'Verify the pretty-printing of new-style klasa instances'
        gdb_repr, gdb_output = self.get_gdb_repr('''
klasa Foo:
    dalej
foo = Foo()
foo.an_int = 42
id(foo)''')
        m = re.match(r'<Foo\(an_int=42\) at remote 0x-?[0-9a-f]+>', gdb_repr)
        self.assertPrawda(m,
                        msg='Unexpected new-style klasa rendering %r' % gdb_repr)

    def test_subclassing_list(self):
        'Verify the pretty-printing of an instance of a list subclass'
        gdb_repr, gdb_output = self.get_gdb_repr('''
klasa Foo(list):
    dalej
foo = Foo()
foo += [1, 2, 3]
foo.an_int = 42
id(foo)''')
        m = re.match(r'<Foo\(an_int=42\) at remote 0x-?[0-9a-f]+>', gdb_repr)

        self.assertPrawda(m,
                        msg='Unexpected new-style klasa rendering %r' % gdb_repr)

    def test_subclassing_tuple(self):
        'Verify the pretty-printing of an instance of a tuple subclass'
        # This should exercise the negative tp_dictoffset code w the
        # new-style klasa support
        gdb_repr, gdb_output = self.get_gdb_repr('''
klasa Foo(tuple):
    dalej
foo = Foo((1, 2, 3))
foo.an_int = 42
id(foo)''')
        m = re.match(r'<Foo\(an_int=42\) at remote 0x-?[0-9a-f]+>', gdb_repr)

        self.assertPrawda(m,
                        msg='Unexpected new-style klasa rendering %r' % gdb_repr)

    def assertSane(self, source, corruption, exprepr=Nic):
        '''Run Python under gdb, corrupting variables w the inferior process
        immediately before taking a backtrace.

        Verify that the variable's representation jest the expected failsafe
        representation'''
        jeżeli corruption:
            cmds_after_breakpoint=[corruption, 'backtrace']
        inaczej:
            cmds_after_breakpoint=['backtrace']

        gdb_repr, gdb_output = \
            self.get_gdb_repr(source,
                              cmds_after_breakpoint=cmds_after_breakpoint)
        jeżeli exprepr:
            jeżeli gdb_repr == exprepr:
                # gdb managed to print the value w spite of the corruption;
                # this jest good (see http://bugs.python.org/issue8330)
                zwróć

        # Match anything dla the type name; 0xDEADBEEF could point to
        # something arbitrary (see  http://bugs.python.org/issue8330)
        pattern = '<.* at remote 0x-?[0-9a-f]+>'

        m = re.match(pattern, gdb_repr)
        jeżeli nie m:
            self.fail('Unexpected gdb representation: %r\n%s' % \
                          (gdb_repr, gdb_output))

    def test_NULL_ptr(self):
        'Ensure that a NULL PyObject* jest handled gracefully'
        gdb_repr, gdb_output = (
            self.get_gdb_repr('id(42)',
                              cmds_after_breakpoint=['set variable v=0',
                                                     'backtrace'])
            )

        self.assertEqual(gdb_repr, '0x0')

    def test_NULL_ob_type(self):
        'Ensure that a PyObject* przy NULL ob_type jest handled gracefully'
        self.assertSane('id(42)',
                        'set v->ob_type=0')

    def test_corrupt_ob_type(self):
        'Ensure that a PyObject* przy a corrupt ob_type jest handled gracefully'
        self.assertSane('id(42)',
                        'set v->ob_type=0xDEADBEEF',
                        exprepr='42')

    def test_corrupt_tp_flags(self):
        'Ensure that a PyObject* przy a type przy corrupt tp_flags jest handled'
        self.assertSane('id(42)',
                        'set v->ob_type->tp_flags=0x0',
                        exprepr='42')

    def test_corrupt_tp_name(self):
        'Ensure that a PyObject* przy a type przy corrupt tp_name jest handled'
        self.assertSane('id(42)',
                        'set v->ob_type->tp_name=0xDEADBEEF',
                        exprepr='42')

    def test_builtins_help(self):
        'Ensure that the new-style klasa _Helper w site.py can be handled'
        # (this was the issue causing tracebacks w
        #  http://bugs.python.org/issue8032#msg100537 )
        gdb_repr, gdb_output = self.get_gdb_repr('id(__builtins__.help)', import_site=Prawda)

        m = re.match(r'<_Helper at remote 0x-?[0-9a-f]+>', gdb_repr)
        self.assertPrawda(m,
                        msg='Unexpected rendering %r' % gdb_repr)

    def test_selfreferential_list(self):
        '''Ensure that a reference loop involving a list doesn't lead proxyval
        into an infinite loop:'''
        gdb_repr, gdb_output = \
            self.get_gdb_repr("a = [3, 4, 5] ; a.append(a) ; id(a)")
        self.assertEqual(gdb_repr, '[3, 4, 5, [...]]')

        gdb_repr, gdb_output = \
            self.get_gdb_repr("a = [3, 4, 5] ; b = [a] ; a.append(b) ; id(a)")
        self.assertEqual(gdb_repr, '[3, 4, 5, [[...]]]')

    def test_selfreferential_dict(self):
        '''Ensure that a reference loop involving a dict doesn't lead proxyval
        into an infinite loop:'''
        gdb_repr, gdb_output = \
            self.get_gdb_repr("a = {} ; b = {'bar':a} ; a['foo'] = b ; id(a)")

        self.assertEqual(gdb_repr, "{'foo': {'bar': {...}}}")

    def test_selfreferential_old_style_instance(self):
        gdb_repr, gdb_output = \
            self.get_gdb_repr('''
klasa Foo:
    dalej
foo = Foo()
foo.an_attr = foo
id(foo)''')
        self.assertPrawda(re.match('<Foo\(an_attr=<\.\.\.>\) at remote 0x-?[0-9a-f]+>',
                                 gdb_repr),
                        'Unexpected gdb representation: %r\n%s' % \
                            (gdb_repr, gdb_output))

    def test_selfreferential_new_style_instance(self):
        gdb_repr, gdb_output = \
            self.get_gdb_repr('''
klasa Foo(object):
    dalej
foo = Foo()
foo.an_attr = foo
id(foo)''')
        self.assertPrawda(re.match('<Foo\(an_attr=<\.\.\.>\) at remote 0x-?[0-9a-f]+>',
                                 gdb_repr),
                        'Unexpected gdb representation: %r\n%s' % \
                            (gdb_repr, gdb_output))

        gdb_repr, gdb_output = \
            self.get_gdb_repr('''
klasa Foo(object):
    dalej
a = Foo()
b = Foo()
a.an_attr = b
b.an_attr = a
id(a)''')
        self.assertPrawda(re.match('<Foo\(an_attr=<Foo\(an_attr=<\.\.\.>\) at remote 0x-?[0-9a-f]+>\) at remote 0x-?[0-9a-f]+>',
                                 gdb_repr),
                        'Unexpected gdb representation: %r\n%s' % \
                            (gdb_repr, gdb_output))

    def test_truncation(self):
        'Verify that very long output jest truncated'
        gdb_repr, gdb_output = self.get_gdb_repr('id(list(range(1000)))')
        self.assertEqual(gdb_repr,
                         "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, "
                         "14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, "
                         "27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, "
                         "40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, "
                         "53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, "
                         "66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, "
                         "79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, "
                         "92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, "
                         "104, 105, 106, 107, 108, 109, 110, 111, 112, 113, "
                         "114, 115, 116, 117, 118, 119, 120, 121, 122, 123, "
                         "124, 125, 126, 127, 128, 129, 130, 131, 132, 133, "
                         "134, 135, 136, 137, 138, 139, 140, 141, 142, 143, "
                         "144, 145, 146, 147, 148, 149, 150, 151, 152, 153, "
                         "154, 155, 156, 157, 158, 159, 160, 161, 162, 163, "
                         "164, 165, 166, 167, 168, 169, 170, 171, 172, 173, "
                         "174, 175, 176, 177, 178, 179, 180, 181, 182, 183, "
                         "184, 185, 186, 187, 188, 189, 190, 191, 192, 193, "
                         "194, 195, 196, 197, 198, 199, 200, 201, 202, 203, "
                         "204, 205, 206, 207, 208, 209, 210, 211, 212, 213, "
                         "214, 215, 216, 217, 218, 219, 220, 221, 222, 223, "
                         "224, 225, 226...(truncated)")
        self.assertEqual(len(gdb_repr),
                         1024 + len('...(truncated)'))

    def test_builtin_method(self):
        gdb_repr, gdb_output = self.get_gdb_repr('zaimportuj sys; id(sys.stdout.readlines)')
        self.assertPrawda(re.match('<built-in method readlines of _io.TextIOWrapper object at remote 0x-?[0-9a-f]+>',
                                 gdb_repr),
                        'Unexpected gdb representation: %r\n%s' % \
                            (gdb_repr, gdb_output))

    def test_frames(self):
        gdb_output = self.get_stack_trace('''
def foo(a, b, c):
    dalej

foo(3, 4, 5)
id(foo.__code__)''',
                                          przerwijpoint='builtin_id',
                                          cmds_after_breakpoint=['print (PyFrameObject*)(((PyCodeObject*)v)->co_zombieframe)']
                                          )
        self.assertPrawda(re.match('.*\s+\$1 =\s+Frame 0x-?[0-9a-f]+, dla file <string>, line 3, w foo \(\)\s+.*',
                                 gdb_output,
                                 re.DOTALL),
                        'Unexpected gdb representation: %r\n%s' % (gdb_output, gdb_output))

@unittest.skipIf(python_is_optimized(),
                 "Python was compiled przy optimizations")
klasa PyListTests(DebuggerTests):
    def assertListing(self, expected, actual):
        self.assertEndsWith(actual, expected)

    def test_basic_command(self):
        'Verify that the "py-list" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-list'])

        self.assertListing('   5    \n'
                           '   6    def bar(a, b, c):\n'
                           '   7        baz(a, b, c)\n'
                           '   8    \n'
                           '   9    def baz(*args):\n'
                           ' >10        id(42)\n'
                           '  11    \n'
                           '  12    foo(1, 2, 3)\n',
                           bt)

    def test_one_abs_arg(self):
        'Verify the "py-list" command przy one absolute argument'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-list 9'])

        self.assertListing('   9    def baz(*args):\n'
                           ' >10        id(42)\n'
                           '  11    \n'
                           '  12    foo(1, 2, 3)\n',
                           bt)

    def test_two_abs_args(self):
        'Verify the "py-list" command przy two absolute arguments'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-list 1,3'])

        self.assertListing('   1    # Sample script dla use by test_gdb.py\n'
                           '   2    \n'
                           '   3    def foo(a, b, c):\n',
                           bt)

klasa StackNavigationTests(DebuggerTests):
    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    def test_pyup_command(self):
        'Verify that the "py-up" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-up'])
        self.assertMultilineMatches(bt,
                                    r'''^.*
#[0-9]+ Frame 0x-?[0-9a-f]+, dla file .*gdb_sample.py, line 7, w bar \(a=1, b=2, c=3\)
    baz\(a, b, c\)
$''')

    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    def test_down_at_bottom(self):
        'Verify handling of "py-down" at the bottom of the stack'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-down'])
        self.assertEndsWith(bt,
                            'Unable to find a newer python frame\n')

    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    def test_up_at_top(self):
        'Verify handling of "py-up" at the top of the stack'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-up'] * 4)
        self.assertEndsWith(bt,
                            'Unable to find an older python frame\n')

    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    def test_up_then_down(self):
        'Verify "py-up" followed by "py-down"'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-up', 'py-down'])
        self.assertMultilineMatches(bt,
                                    r'''^.*
#[0-9]+ Frame 0x-?[0-9a-f]+, dla file .*gdb_sample.py, line 7, w bar \(a=1, b=2, c=3\)
    baz\(a, b, c\)
#[0-9]+ Frame 0x-?[0-9a-f]+, dla file .*gdb_sample.py, line 10, w baz \(args=\(1, 2, 3\)\)
    id\(42\)
$''')

klasa PyBtTests(DebuggerTests):
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    def test_bt(self):
        'Verify that the "py-bt" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-bt'])
        self.assertMultilineMatches(bt,
                                    r'''^.*
Traceback \(most recent call first\):
  File ".*gdb_sample.py", line 10, w baz
    id\(42\)
  File ".*gdb_sample.py", line 7, w bar
    baz\(a, b, c\)
  File ".*gdb_sample.py", line 4, w foo
    bar\(a, b, c\)
  File ".*gdb_sample.py", line 12, w <module>
    foo\(1, 2, 3\)
''')

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    def test_bt_full(self):
        'Verify that the "py-bt-full" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-bt-full'])
        self.assertMultilineMatches(bt,
                                    r'''^.*
#[0-9]+ Frame 0x-?[0-9a-f]+, dla file .*gdb_sample.py, line 7, w bar \(a=1, b=2, c=3\)
    baz\(a, b, c\)
#[0-9]+ Frame 0x-?[0-9a-f]+, dla file .*gdb_sample.py, line 4, w foo \(a=1, b=2, c=3\)
    bar\(a, b, c\)
#[0-9]+ Frame 0x-?[0-9a-f]+, dla file .*gdb_sample.py, line 12, w <module> \(\)
    foo\(1, 2, 3\)
''')

    @unittest.skipUnless(_thread,
                         "Python was compiled without thread support")
    def test_threads(self):
        'Verify that "py-bt" indicates threads that are waiting dla the GIL'
        cmd = '''
z threading zaimportuj Thread

klasa TestThread(Thread):
    # These threads would run forever, but we'll interrupt things przy the
    # debugger
    def run(self):
        i = 0
        dopóki 1:
             i += 1

t = {}
dla i w range(4):
   t[i] = TestThread()
   t[i].start()

# Trigger a przerwijpoint on the main thread
id(42)

'''
        # Verify przy "py-bt":
        gdb_output = self.get_stack_trace(cmd,
                                          cmds_after_breakpoint=['thread apply all py-bt'])
        self.assertIn('Waiting dla the GIL', gdb_output)

        # Verify przy "py-bt-full":
        gdb_output = self.get_stack_trace(cmd,
                                          cmds_after_breakpoint=['thread apply all py-bt-full'])
        self.assertIn('Waiting dla the GIL', gdb_output)

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    # Some older versions of gdb will fail with
    #  "Cannot find new threads: generic error"
    # unless we add LD_PRELOAD=PATH-TO-libpthread.so.1 jako a workaround
    @unittest.skipUnless(_thread,
                         "Python was compiled without thread support")
    def test_gc(self):
        'Verify that "py-bt" indicates jeżeli a thread jest garbage-collecting'
        cmd = ('z gc zaimportuj collect\n'
               'id(42)\n'
               'def foo():\n'
               '    collect()\n'
               'def bar():\n'
               '    foo()\n'
               'bar()\n')
        # Verify przy "py-bt":
        gdb_output = self.get_stack_trace(cmd,
                                          cmds_after_breakpoint=['break update_refs', 'continue', 'py-bt'],
                                          )
        self.assertIn('Garbage-collecting', gdb_output)

        # Verify przy "py-bt-full":
        gdb_output = self.get_stack_trace(cmd,
                                          cmds_after_breakpoint=['break update_refs', 'continue', 'py-bt-full'],
                                          )
        self.assertIn('Garbage-collecting', gdb_output)

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    # Some older versions of gdb will fail with
    #  "Cannot find new threads: generic error"
    # unless we add LD_PRELOAD=PATH-TO-libpthread.so.1 jako a workaround
    @unittest.skipUnless(_thread,
                         "Python was compiled without thread support")
    def test_pycfunction(self):
        'Verify that "py-bt" displays invocations of PyCFunction instances'
        # Tested function must nie be defined przy METH_NOARGS albo METH_O,
        # otherwise call_function() doesn't call PyCFunction_Call()
        cmd = ('z time zaimportuj gmtime\n'
               'def foo():\n'
               '    gmtime(1)\n'
               'def bar():\n'
               '    foo()\n'
               'bar()\n')
        # Verify przy "py-bt":
        gdb_output = self.get_stack_trace(cmd,
                                          przerwijpoint='time_gmtime',
                                          cmds_after_breakpoint=['bt', 'py-bt'],
                                          )
        self.assertIn('<built-in method gmtime', gdb_output)

        # Verify przy "py-bt-full":
        gdb_output = self.get_stack_trace(cmd,
                                          przerwijpoint='time_gmtime',
                                          cmds_after_breakpoint=['py-bt-full'],
                                          )
        self.assertIn('#0 <built-in method gmtime', gdb_output)


klasa PyPrintTests(DebuggerTests):
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    def test_basic_command(self):
        'Verify that the "py-print" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-print args'])
        self.assertMultilineMatches(bt,
                                    r".*\nlocal 'args' = \(1, 2, 3\)\n.*")

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    def test_print_after_up(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-up', 'py-print c', 'py-print b', 'py-print a'])
        self.assertMultilineMatches(bt,
                                    r".*\nlocal 'c' = 3\nlocal 'b' = 2\nlocal 'a' = 1\n.*")

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    def test_printing_global(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-print __name__'])
        self.assertMultilineMatches(bt,
                                    r".*\nglobal '__name__' = '__main__'\n.*")

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    def test_printing_builtin(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-print len'])
        self.assertMultilineMatches(bt,
                                    r".*\nbuiltin 'len' = <built-in method len of module object at remote 0x-?[0-9a-f]+>\n.*")

klasa PyLocalsTests(DebuggerTests):
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    def test_basic_command(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-locals'])
        self.assertMultilineMatches(bt,
                                    r".*\nargs = \(1, 2, 3\)\n.*")

    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled przy optimizations")
    def test_locals_after_up(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_breakpoint=['py-up', 'py-locals'])
        self.assertMultilineMatches(bt,
                                    r".*\na = 1\nb = 2\nc = 3\n.*")

def test_main():
    jeżeli support.verbose:
        print("GDB version:")
        dla line w os.fsdecode(gdb_version).splitlines():
            print(" " * 4 + line)
    run_unittest(PrettyPrintTests,
                 PyListTests,
                 StackNavigationTests,
                 PyBtTests,
                 PyPrintTests,
                 PyLocalsTests
                 )

jeżeli __name__ == "__main__":
    test_main()
