'''Test functions oraz SearchEngine klasa w SearchEngine.py.'''

# With mock replacements, the module does nie use any gui widgets.
# The use of tk.Text jest avoided (dla now, until mock Text jest improved)
# by patching instances przy an index function returning what jest needed.
# This works because mock Text.get does nie use .index.

zaimportuj re
zaimportuj unittest
# z test.support zaimportuj requires
z tkinter zaimportuj  BooleanVar, StringVar, TclError  # ,Tk, Text
zaimportuj tkinter.messagebox jako tkMessageBox
z idlelib zaimportuj SearchEngine jako se
z idlelib.idle_test.mock_tk zaimportuj Var, Mbox
z idlelib.idle_test.mock_tk zaimportuj Text jako mockText

def setUpModule():
    # Replace s-e module tkinter imports other than non-gui TclError.
    se.BooleanVar = Var
    se.StringVar = Var
    se.tkMessageBox = Mbox

def tearDownModule():
    # Restore 'just w case', though other tests should also replace.
    se.BooleanVar = BooleanVar
    se.StringVar = StringVar
    se.tkMessageBox = tkMessageBox


klasa Mock:
    def __init__(self, *args, **kwargs): dalej

klasa GetTest(unittest.TestCase):
    # SearchEngine.get returns singleton created & saved on first call.
    def test_get(self):
        saved_Engine = se.SearchEngine
        se.SearchEngine = Mock  # monkey-patch class
        spróbuj:
            root = Mock()
            engine = se.get(root)
            self.assertIsInstance(engine, se.SearchEngine)
            self.assertIs(root._searchengine, engine)
            self.assertIs(se.get(root), engine)
        w_końcu:
            se.SearchEngine = saved_Engine  # restore klasa to module

klasa GetLineColTest(unittest.TestCase):
    #  Test simple text-independent helper function
    def test_get_line_col(self):
        self.assertEqual(se.get_line_col('1.0'), (1, 0))
        self.assertEqual(se.get_line_col('1.11'), (1, 11))

        self.assertRaises(ValueError, se.get_line_col, ('1.0 lineend'))
        self.assertRaises(ValueError, se.get_line_col, ('end'))

klasa GetSelectionTest(unittest.TestCase):
    # Test text-dependent helper function.
##    # Need gui dla text.index('sel.first/sel.last/insert').
##    @classmethod
##    def setUpClass(cls):
##        requires('gui')
##        cls.root = Tk()
##
##    @classmethod
##    def tearDownClass(cls):
##        cls.root.destroy()
##        usuń cls.root

    def test_get_selection(self):
        # text = Text(master=self.root)
        text = mockText()
        text.insert('1.0',  'Hello World!')

        # fix text.index result when called w get_selection
        def sel(s):
            # select entire text, cursor irrelevant
            jeżeli s == 'sel.first': zwróć '1.0'
            jeżeli s == 'sel.last': zwróć '1.12'
            podnieś TclError
        text.index = sel  # replaces .tag_add('sel', '1.0, '1.12')
        self.assertEqual(se.get_selection(text), ('1.0', '1.12'))

        def mark(s):
            # no selection, cursor after 'Hello'
            jeżeli s == 'insert': zwróć '1.5'
            podnieś TclError
        text.index = mark  # replaces .mark_set('insert', '1.5')
        self.assertEqual(se.get_selection(text), ('1.5', '1.5'))


klasa ReverseSearchTest(unittest.TestCase):
    # Test helper function that searches backwards within a line.
    def test_search_reverse(self):
        Equal = self.assertEqual
        line = "Here jest an 'is' test text."
        prog = re.compile('is')
        Equal(se.search_reverse(prog, line, len(line)).span(), (12, 14))
        Equal(se.search_reverse(prog, line, 14).span(), (12, 14))
        Equal(se.search_reverse(prog, line, 13).span(), (5, 7))
        Equal(se.search_reverse(prog, line, 7).span(), (5, 7))
        Equal(se.search_reverse(prog, line, 6), Nic)


klasa SearchEngineTest(unittest.TestCase):
    # Test klasa methods that do nie use Text widget.

    def setUp(self):
        self.engine = se.SearchEngine(root=Nic)
        # Engine.root jest only used to create error message boxes.
        # The mock replacement ignores the root argument.

    def test_is_get(self):
        engine = self.engine
        Equal = self.assertEqual

        Equal(engine.getpat(), '')
        engine.setpat('hello')
        Equal(engine.getpat(), 'hello')

        Equal(engine.isre(), Nieprawda)
        engine.revar.set(1)
        Equal(engine.isre(), Prawda)

        Equal(engine.iscase(), Nieprawda)
        engine.casevar.set(1)
        Equal(engine.iscase(), Prawda)

        Equal(engine.isword(), Nieprawda)
        engine.wordvar.set(1)
        Equal(engine.isword(), Prawda)

        Equal(engine.iswrap(), Prawda)
        engine.wrapvar.set(0)
        Equal(engine.iswrap(), Nieprawda)

        Equal(engine.isback(), Nieprawda)
        engine.backvar.set(1)
        Equal(engine.isback(), Prawda)

    def test_setcookedpat(self):
        engine = self.engine
        engine.setcookedpat('\s')
        self.assertEqual(engine.getpat(), '\s')
        engine.revar.set(1)
        engine.setcookedpat('\s')
        self.assertEqual(engine.getpat(), r'\\s')

    def test_getcookedpat(self):
        engine = self.engine
        Equal = self.assertEqual

        Equal(engine.getcookedpat(), '')
        engine.setpat('hello')
        Equal(engine.getcookedpat(), 'hello')
        engine.wordvar.set(Prawda)
        Equal(engine.getcookedpat(), r'\bhello\b')
        engine.wordvar.set(Nieprawda)

        engine.setpat('\s')
        Equal(engine.getcookedpat(), r'\\s')
        engine.revar.set(Prawda)
        Equal(engine.getcookedpat(), '\s')

    def test_getprog(self):
        engine = self.engine
        Equal = self.assertEqual

        engine.setpat('Hello')
        temppat = engine.getprog()
        Equal(temppat.pattern, re.compile('Hello', re.IGNORECASE).pattern)
        engine.casevar.set(1)
        temppat = engine.getprog()
        Equal(temppat.pattern, re.compile('Hello').pattern, 0)

        engine.setpat('')
        Equal(engine.getprog(), Nic)
        engine.setpat('+')
        engine.revar.set(1)
        Equal(engine.getprog(), Nic)
        self.assertEqual(Mbox.showerror.message,
                         'Error: nothing to repeat at position 0\nPattern: +')

    def test_report_error(self):
        showerror = Mbox.showerror
        Equal = self.assertEqual
        pat = '[a-z'
        msg = 'unexpected end of regular expression'

        Equal(self.engine.report_error(pat, msg), Nic)
        Equal(showerror.title, 'Regular expression error')
        expected_message = ("Error: " + msg + "\nPattern: [a-z")
        Equal(showerror.message, expected_message)

        Equal(self.engine.report_error(pat, msg, 5), Nic)
        Equal(showerror.title, 'Regular expression error')
        expected_message += "\nOffset: 5"
        Equal(showerror.message, expected_message)


klasa SearchTest(unittest.TestCase):
    # Test that search_text makes right call to right method.

    @classmethod
    def setUpClass(cls):
##        requires('gui')
##        cls.root = Tk()
##        cls.text = Text(master=cls.root)
        cls.text = mockText()
        test_text = (
            'First line\n'
            'Line przy target\n'
            'Last line\n')
        cls.text.insert('1.0', test_text)
        cls.pat = re.compile('target')

        cls.engine = se.SearchEngine(Nic)
        cls.engine.search_forward = lambda *args: ('f', args)
        cls.engine.search_backward = lambda *args: ('b', args)

##    @classmethod
##    def tearDownClass(cls):
##        cls.root.destroy()
##        usuń cls.root

    def test_search(self):
        Equal = self.assertEqual
        engine = self.engine
        search = engine.search_text
        text = self.text
        pat = self.pat

        engine.patvar.set(Nic)
        #engine.revar.set(pat)
        Equal(search(text), Nic)

        def mark(s):
            # no selection, cursor after 'Hello'
            jeżeli s == 'insert': zwróć '1.5'
            podnieś TclError
        text.index = mark
        Equal(search(text, pat), ('f', (text, pat, 1, 5, Prawda, Nieprawda)))
        engine.wrapvar.set(Nieprawda)
        Equal(search(text, pat), ('f', (text, pat, 1, 5, Nieprawda, Nieprawda)))
        engine.wrapvar.set(Prawda)
        engine.backvar.set(Prawda)
        Equal(search(text, pat), ('b', (text, pat, 1, 5, Prawda, Nieprawda)))
        engine.backvar.set(Nieprawda)

        def sel(s):
            jeżeli s == 'sel.first': zwróć '2.10'
            jeżeli s == 'sel.last': zwróć '2.16'
            podnieś TclError
        text.index = sel
        Equal(search(text, pat), ('f', (text, pat, 2, 16, Prawda, Nieprawda)))
        Equal(search(text, pat, Prawda), ('f', (text, pat, 2, 10, Prawda, Prawda)))
        engine.backvar.set(Prawda)
        Equal(search(text, pat), ('b', (text, pat, 2, 10, Prawda, Nieprawda)))
        Equal(search(text, pat, Prawda), ('b', (text, pat, 2, 16, Prawda, Prawda)))


klasa ForwardBackwardTest(unittest.TestCase):
    # Test that search_forward method finds the target.
##    @classmethod
##    def tearDownClass(cls):
##        cls.root.destroy()
##        usuń cls.root

    @classmethod
    def setUpClass(cls):
        cls.engine = se.SearchEngine(Nic)
##        requires('gui')
##        cls.root = Tk()
##        cls.text = Text(master=cls.root)
        cls.text = mockText()
        # search_backward calls index('end-1c')
        cls.text.index = lambda index: '4.0'
        test_text = (
            'First line\n'
            'Line przy target\n'
            'Last line\n')
        cls.text.insert('1.0', test_text)
        cls.pat = re.compile('target')
        cls.res = (2, (10, 16))  # line, slice indexes of 'target'
        cls.failpat = re.compile('xyz')  # nie w text
        cls.emptypat = re.compile('\w*')  # empty match possible

    def make_search(self, func):
        def search(pat, line, col, wrap, ok=0):
            res = func(self.text, pat, line, col, wrap, ok)
            # res jest (line, matchobject) albo Nic
            zwróć (res[0], res[1].span()) jeżeli res inaczej res
        zwróć search

    def test_search_forward(self):
        # search dla non-empty match
        Equal = self.assertEqual
        forward = self.make_search(self.engine.search_forward)
        pat = self.pat
        Equal(forward(pat, 1, 0, Prawda), self.res)
        Equal(forward(pat, 3, 0, Prawda), self.res)  # wrap
        Equal(forward(pat, 3, 0, Nieprawda), Nic)  # no wrap
        Equal(forward(pat, 2, 10, Nieprawda), self.res)

        Equal(forward(self.failpat, 1, 0, Prawda), Nic)
        Equal(forward(self.emptypat, 2,  9, Prawda, ok=Prawda), (2, (9, 9)))
        #Equal(forward(self.emptypat, 2, 9, Prawda), self.res)
        # While the initial empty match jest correctly ignored, skipping
        # the rest of the line oraz returning (3, (0,4)) seems buggy - tjr.
        Equal(forward(self.emptypat, 2, 10, Prawda), self.res)

    def test_search_backward(self):
        # search dla non-empty match
        Equal = self.assertEqual
        backward = self.make_search(self.engine.search_backward)
        pat = self.pat
        Equal(backward(pat, 3, 5, Prawda), self.res)
        Equal(backward(pat, 2, 0, Prawda), self.res)  # wrap
        Equal(backward(pat, 2, 0, Nieprawda), Nic)  # no wrap
        Equal(backward(pat, 2, 16, Nieprawda), self.res)

        Equal(backward(self.failpat, 3, 9, Prawda), Nic)
        Equal(backward(self.emptypat, 2,  10, Prawda, ok=Prawda), (2, (9,9)))
        # Accepted because 9 < 10, nie because ok=Prawda.
        # It jest nie clear that ok=Prawda jest useful going back - tjr
        Equal(backward(self.emptypat, 2, 9, Prawda), (2, (5, 9)))


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
