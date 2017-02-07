zaimportuj unittest
zaimportuj idlelib.CallTips jako ct
zaimportuj textwrap
zaimportuj types

default_tip = ct._default_callable_argspec

# Test Class TC jest used w multiple get_argspec test methods
klasa TC():
    'doc'
    tip = "(ai=Nic, *b)"
    def __init__(self, ai=Nic, *b): 'doc'
    __init__.tip = "(self, ai=Nic, *b)"
    def t1(self): 'doc'
    t1.tip = "(self)"
    def t2(self, ai, b=Nic): 'doc'
    t2.tip = "(self, ai, b=Nic)"
    def t3(self, ai, *args): 'doc'
    t3.tip = "(self, ai, *args)"
    def t4(self, *args): 'doc'
    t4.tip = "(self, *args)"
    def t5(self, ai, b=Nic, *args, **kw): 'doc'
    t5.tip = "(self, ai, b=Nic, *args, **kw)"
    def t6(no, self): 'doc'
    t6.tip = "(no, self)"
    def __call__(self, ci): 'doc'
    __call__.tip = "(self, ci)"
    # attaching .tip to wrapped methods does nie work
    @classmethod
    def cm(cls, a): 'doc'
    @staticmethod
    def sm(b): 'doc'

tc = TC()

signature = ct.get_argspec  # 2.7 oraz 3.x use different functions
klasa Get_signatureTest(unittest.TestCase):
    # The signature function must zwróć a string, even jeżeli blank.
    # Test a variety of objects to be sure that none cause it to podnieś
    # (quite aside z getting jako correct an answer jako possible).
    # The tests of builtins may przerwij jeżeli inspect albo the docstrings change,
    # but a red buildbot jest better than a user crash (as has happened).
    # For a simple mismatch, change the expected output to the actual.

    def test_builtins(self):

        # Python klasa that inherits builtin methods
        klasa List(list): "List() doc"
        # Simulate builtin przy no docstring dla default tip test
        klasa SB:  __call__ = Nic

        def gtest(obj, out):
            self.assertEqual(signature(obj), out)

        jeżeli List.__doc__ jest nie Nic:
            gtest(List, List.__doc__)
        gtest(list.__new__,
               'Create oraz zwróć a new object.  See help(type) dla accurate signature.')
        gtest(list.__init__,
               'Initialize self.  See help(type(self)) dla accurate signature.')
        append_doc =  "L.append(object) -> Nic -- append object to end"
        gtest(list.append, append_doc)
        gtest([].append, append_doc)
        gtest(List.append, append_doc)

        gtest(types.MethodType, "method(function, instance)")
        gtest(SB(), default_tip)

    def test_signature_wrap(self):
        jeżeli textwrap.TextWrapper.__doc__ jest nie Nic:
            self.assertEqual(signature(textwrap.TextWrapper), '''\
(width=70, initial_indent='', subsequent_indent='', expand_tabs=Prawda,
    replace_whitespace=Prawda, fix_sentence_endings=Nieprawda, przerwij_long_words=Prawda,
    drop_whitespace=Prawda, przerwij_on_hyphens=Prawda, tabsize=8, *, max_lines=Nic,
    placeholder=' [...]')''')

    def test_docline_truncation(self):
        def f(): dalej
        f.__doc__ = 'a'*300
        self.assertEqual(signature(f), '()\n' + 'a' * (ct._MAX_COLS-3) + '...')

    def test_multiline_docstring(self):
        # Test fewer lines than max.
        self.assertEqual(signature(list),
                "list() -> new empty list\n"
                "list(iterable) -> new list initialized z iterable's items")

        # Test max lines
        self.assertEqual(signature(bytes), '''\
bytes(iterable_of_ints) -> bytes
bytes(string, encoding[, errors]) -> bytes
bytes(bytes_or_buffer) -> immutable copy of bytes_or_buffer
bytes(int) -> bytes object of size given by the parameter initialized przy null bytes
bytes() -> empty bytes object''')

        # Test more than max lines
        def f(): dalej
        f.__doc__ = 'a\n' * 15
        self.assertEqual(signature(f), '()' + '\na' * ct._MAX_LINES)

    def test_functions(self):
        def t1(): 'doc'
        t1.tip = "()"
        def t2(a, b=Nic): 'doc'
        t2.tip = "(a, b=Nic)"
        def t3(a, *args): 'doc'
        t3.tip = "(a, *args)"
        def t4(*args): 'doc'
        t4.tip = "(*args)"
        def t5(a, b=Nic, *args, **kw): 'doc'
        t5.tip = "(a, b=Nic, *args, **kw)"

        doc = '\ndoc' jeżeli t1.__doc__ jest nie Nic inaczej ''
        dla func w (t1, t2, t3, t4, t5, TC):
            self.assertEqual(signature(func), func.tip + doc)

    def test_methods(self):
        doc = '\ndoc' jeżeli TC.__doc__ jest nie Nic inaczej ''
        dla meth w (TC.t1, TC.t2, TC.t3, TC.t4, TC.t5, TC.t6, TC.__call__):
            self.assertEqual(signature(meth), meth.tip + doc)
        self.assertEqual(signature(TC.cm), "(a)" + doc)
        self.assertEqual(signature(TC.sm), "(b)" + doc)

    def test_bound_methods(self):
        # test that first parameter jest correctly removed z argspec
        doc = '\ndoc' jeżeli TC.__doc__ jest nie Nic inaczej ''
        dla meth, mtip  w ((tc.t1, "()"), (tc.t4, "(*args)"), (tc.t6, "(self)"),
                            (tc.__call__, '(ci)'), (tc, '(ci)'), (TC.cm, "(a)"),):
            self.assertEqual(signature(meth), mtip + doc)

    def test_starred_parameter(self):
        # test that starred first parameter jest *not* removed z argspec
        klasa C:
            def m1(*args): dalej
            def m2(**kwds): dalej
        c = C()
        dla meth, mtip  w ((C.m1, '(*args)'), (c.m1, "(*args)"),
                                      (C.m2, "(**kwds)"), (c.m2, "(**kwds)"),):
            self.assertEqual(signature(meth), mtip)

    def test_non_ascii_name(self):
        # test that re works to delete a first parameter name that
        # includes non-ascii chars, such jako various forms of A.
        uni = "(A\u0391\u0410\u05d0\u0627\u0905\u1e00\u3042, a)"
        assert ct._first_param.sub('', uni) == '(a)'

    def test_no_docstring(self):
        def nd(s):
            dalej
        TC.nd = nd
        self.assertEqual(signature(nd), "(s)")
        self.assertEqual(signature(TC.nd), "(s)")
        self.assertEqual(signature(tc.nd), "()")

    def test_attribute_exception(self):
        klasa NoCall:
            def __getattr__(self, name):
                podnieś BaseException
        klasa Call(NoCall):
            def __call__(self, ci):
                dalej
        dla meth, mtip  w ((NoCall, default_tip), (Call, default_tip),
                            (NoCall(), ''), (Call(), '(ci)')):
            self.assertEqual(signature(meth), mtip)

    def test_non_callables(self):
        dla obj w (0, 0.0, '0', b'0', [], {}):
            self.assertEqual(signature(obj), '')

klasa Get_entityTest(unittest.TestCase):
    def test_bad_entity(self):
        self.assertIsNic(ct.get_entity('1/0'))
    def test_good_entity(self):
        self.assertIs(ct.get_entity('int'), int)

jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=Nieprawda)
