"""
Unit tests dla refactor.py.
"""

z __future__ zaimportuj with_statement

zaimportuj sys
zaimportuj os
zaimportuj codecs
zaimportuj operator
zaimportuj io
zaimportuj tempfile
zaimportuj shutil
zaimportuj unittest
zaimportuj warnings

z lib2to3 zaimportuj refactor, pygram, fixer_base
z lib2to3.pgen2 zaimportuj token

z . zaimportuj support


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXER_DIR = os.path.join(TEST_DATA_DIR, "fixers")

sys.path.append(FIXER_DIR)
spróbuj:
    _DEFAULT_FIXERS = refactor.get_fixers_from_package("myfixes")
w_końcu:
    sys.path.pop()

_2TO3_FIXERS = refactor.get_fixers_from_package("lib2to3.fixes")

klasa TestRefactoringTool(unittest.TestCase):

    def setUp(self):
        sys.path.append(FIXER_DIR)

    def tearDown(self):
        sys.path.pop()

    def check_instances(self, instances, classes):
        dla inst, cls w zip(instances, classes):
            jeżeli nie isinstance(inst, cls):
                self.fail("%s are nie instances of %s" % instances, classes)

    def rt(self, options=Nic, fixers=_DEFAULT_FIXERS, explicit=Nic):
        zwróć refactor.RefactoringTool(fixers, options, explicit)

    def test_print_function_option(self):
        rt = self.rt({"print_function" : Prawda})
        self.assertIs(rt.grammar, pygram.python_grammar_no_print_statement)
        self.assertIs(rt.driver.grammar,
                      pygram.python_grammar_no_print_statement)

    def test_write_unchanged_files_option(self):
        rt = self.rt()
        self.assertNieprawda(rt.write_unchanged_files)
        rt = self.rt({"write_unchanged_files" : Prawda})
        self.assertPrawda(rt.write_unchanged_files)

    def test_fixer_loading_helpers(self):
        contents = ["explicit", "first", "last", "parrot", "preorder"]
        non_prefixed = refactor.get_all_fix_names("myfixes")
        prefixed = refactor.get_all_fix_names("myfixes", Nieprawda)
        full_names = refactor.get_fixers_from_package("myfixes")
        self.assertEqual(prefixed, ["fix_" + name dla name w contents])
        self.assertEqual(non_prefixed, contents)
        self.assertEqual(full_names,
                         ["myfixes.fix_" + name dla name w contents])

    def test_detect_future_features(self):
        run = refactor._detect_future_features
        fs = frozenset
        empty = fs()
        self.assertEqual(run(""), empty)
        self.assertEqual(run("z __future__ zaimportuj print_function"),
                         fs(("print_function",)))
        self.assertEqual(run("z __future__ zaimportuj generators"),
                         fs(("generators",)))
        self.assertEqual(run("z __future__ zaimportuj generators, feature"),
                         fs(("generators", "feature")))
        inp = "z __future__ zaimportuj generators, print_function"
        self.assertEqual(run(inp), fs(("generators", "print_function")))
        inp ="z __future__ zaimportuj print_function, generators"
        self.assertEqual(run(inp), fs(("print_function", "generators")))
        inp = "z __future__ zaimportuj (print_function,)"
        self.assertEqual(run(inp), fs(("print_function",)))
        inp = "z __future__ zaimportuj (generators, print_function)"
        self.assertEqual(run(inp), fs(("generators", "print_function")))
        inp = "z __future__ zaimportuj (generators, nested_scopes)"
        self.assertEqual(run(inp), fs(("generators", "nested_scopes")))
        inp = """z __future__ zaimportuj generators
z __future__ zaimportuj print_function"""
        self.assertEqual(run(inp), fs(("generators", "print_function")))
        invalid = ("from",
                   "z 4",
                   "z x",
                   "z x 5",
                   "z x im",
                   "z x import",
                   "z x zaimportuj 4",
                   )
        dla inp w invalid:
            self.assertEqual(run(inp), empty)
        inp = "'docstring'\nz __future__ zaimportuj print_function"
        self.assertEqual(run(inp), fs(("print_function",)))
        inp = "'docstring'\n'somng'\nz __future__ zaimportuj print_function"
        self.assertEqual(run(inp), empty)
        inp = "# comment\nz __future__ zaimportuj print_function"
        self.assertEqual(run(inp), fs(("print_function",)))
        inp = "# comment\n'doc'\nz __future__ zaimportuj print_function"
        self.assertEqual(run(inp), fs(("print_function",)))
        inp = "class x: dalej\nz __future__ zaimportuj print_function"
        self.assertEqual(run(inp), empty)

    def test_get_headnode_dict(self):
        klasa NicFix(fixer_base.BaseFix):
            dalej

        klasa FileInputFix(fixer_base.BaseFix):
            PATTERN = "file_input< any * >"

        klasa SimpleFix(fixer_base.BaseFix):
            PATTERN = "'name'"

        no_head = NicFix({}, [])
        with_head = FileInputFix({}, [])
        simple = SimpleFix({}, [])
        d = refactor._get_headnode_dict([no_head, with_head, simple])
        top_fixes = d.pop(pygram.python_symbols.file_input)
        self.assertEqual(top_fixes, [with_head, no_head])
        name_fixes = d.pop(token.NAME)
        self.assertEqual(name_fixes, [simple, no_head])
        dla fixes w d.values():
            self.assertEqual(fixes, [no_head])

    def test_fixer_loading(self):
        z myfixes.fix_first zaimportuj FixFirst
        z myfixes.fix_last zaimportuj FixLast
        z myfixes.fix_parrot zaimportuj FixParrot
        z myfixes.fix_preorder zaimportuj FixPreorder

        rt = self.rt()
        pre, post = rt.get_fixers()

        self.check_instances(pre, [FixPreorder])
        self.check_instances(post, [FixFirst, FixParrot, FixLast])

    def test_naughty_fixers(self):
        self.assertRaises(ImportError, self.rt, fixers=["not_here"])
        self.assertRaises(refactor.FixerError, self.rt, fixers=["no_fixer_cls"])
        self.assertRaises(refactor.FixerError, self.rt, fixers=["bad_order"])

    def test_refactor_string(self):
        rt = self.rt()
        input = "def parrot(): dalej\n\n"
        tree = rt.refactor_string(input, "<test>")
        self.assertNotEqual(str(tree), input)

        input = "def f(): dalej\n\n"
        tree = rt.refactor_string(input, "<test>")
        self.assertEqual(str(tree), input)

    def test_refactor_stdin(self):

        klasa MyRT(refactor.RefactoringTool):

            def print_output(self, old_text, new_text, filename, equal):
                results.extend([old_text, new_text, filename, equal])

        results = []
        rt = MyRT(_DEFAULT_FIXERS)
        save = sys.stdin
        sys.stdin = io.StringIO("def parrot(): dalej\n\n")
        spróbuj:
            rt.refactor_stdin()
        w_końcu:
            sys.stdin = save
        expected = ["def parrot(): dalej\n\n",
                    "def cheese(): dalej\n\n",
                    "<stdin>", Nieprawda]
        self.assertEqual(results, expected)

    def check_file_refactoring(self, test_file, fixers=_2TO3_FIXERS,
                               options=Nic, mock_log_debug=Nic,
                               actually_write=Prawda):
        tmpdir = tempfile.mkdtemp(prefix="2to3-test_refactor")
        self.addCleanup(shutil.rmtree, tmpdir)
        # make a copy of the tested file that we can write to
        shutil.copy(test_file, tmpdir)
        test_file = os.path.join(tmpdir, os.path.basename(test_file))
        os.chmod(test_file, 0o644)

        def read_file():
            przy open(test_file, "rb") jako fp:
                zwróć fp.read()

        old_contents = read_file()
        rt = self.rt(fixers=fixers, options=options)
        jeżeli mock_log_debug:
            rt.log_debug = mock_log_debug

        rt.refactor_file(test_file)
        self.assertEqual(old_contents, read_file())

        jeżeli nie actually_write:
            zwróć
        rt.refactor_file(test_file, Prawda)
        new_contents = read_file()
        self.assertNotEqual(old_contents, new_contents)
        zwróć new_contents

    def test_refactor_file(self):
        test_file = os.path.join(FIXER_DIR, "parrot_example.py")
        self.check_file_refactoring(test_file, _DEFAULT_FIXERS)

    def test_refactor_file_write_unchanged_file(self):
        test_file = os.path.join(FIXER_DIR, "parrot_example.py")
        debug_messages = []
        def recording_log_debug(msg, *args):
            debug_messages.append(msg % args)
        self.check_file_refactoring(test_file, fixers=(),
                                    options={"write_unchanged_files": Prawda},
                                    mock_log_debug=recording_log_debug,
                                    actually_write=Nieprawda)
        # Testing that it logged this message when write=Nieprawda was dalejed jest
        # sufficient to see that it did nie bail early after "No changes".
        message_regex = r"Not writing changes to .*%s%s" % (
                os.sep, os.path.basename(test_file))
        dla message w debug_messages:
            jeżeli "Not writing changes" w message:
                self.assertRegex(message, message_regex)
                przerwij
        inaczej:
            self.fail("%r nie matched w %r" % (message_regex, debug_messages))

    def test_refactor_dir(self):
        def check(structure, expected):
            def mock_refactor_file(self, f, *args):
                got.append(f)
            save_func = refactor.RefactoringTool.refactor_file
            refactor.RefactoringTool.refactor_file = mock_refactor_file
            rt = self.rt()
            got = []
            dir = tempfile.mkdtemp(prefix="2to3-test_refactor")
            spróbuj:
                os.mkdir(os.path.join(dir, "a_dir"))
                dla fn w structure:
                    open(os.path.join(dir, fn), "wb").close()
                rt.refactor_dir(dir)
            w_końcu:
                refactor.RefactoringTool.refactor_file = save_func
                shutil.rmtree(dir)
            self.assertEqual(got,
                             [os.path.join(dir, path) dla path w expected])
        check([], [])
        tree = ["nothing",
                "hi.py",
                ".dumb",
                ".after.py",
                "notpy.npy",
                "sappy"]
        expected = ["hi.py"]
        check(tree, expected)
        tree = ["hi.py",
                os.path.join("a_dir", "stuff.py")]
        check(tree, tree)

    def test_file_encoding(self):
        fn = os.path.join(TEST_DATA_DIR, "different_encoding.py")
        self.check_file_refactoring(fn)

    def test_false_file_encoding(self):
        fn = os.path.join(TEST_DATA_DIR, "false_encoding.py")
        data = self.check_file_refactoring(fn)

    def test_bom(self):
        fn = os.path.join(TEST_DATA_DIR, "bom.py")
        data = self.check_file_refactoring(fn)
        self.assertPrawda(data.startswith(codecs.BOM_UTF8))

    def test_crlf_newlines(self):
        old_sep = os.linesep
        os.linesep = "\r\n"
        spróbuj:
            fn = os.path.join(TEST_DATA_DIR, "crlf.py")
            fixes = refactor.get_fixers_from_package("lib2to3.fixes")
            self.check_file_refactoring(fn, fixes)
        w_końcu:
            os.linesep = old_sep

    def test_refactor_docstring(self):
        rt = self.rt()

        doc = """
>>> example()
42
"""
        out = rt.refactor_docstring(doc, "<test>")
        self.assertEqual(out, doc)

        doc = """
>>> def parrot():
...      zwróć 43
"""
        out = rt.refactor_docstring(doc, "<test>")
        self.assertNotEqual(out, doc)

    def test_explicit(self):
        z myfixes.fix_explicit zaimportuj FixExplicit

        rt = self.rt(fixers=["myfixes.fix_explicit"])
        self.assertEqual(len(rt.post_order), 0)

        rt = self.rt(explicit=["myfixes.fix_explicit"])
        dla fix w rt.post_order:
            jeżeli isinstance(fix, FixExplicit):
                przerwij
        inaczej:
            self.fail("explicit fixer nie loaded")
