zaimportuj unittest
z test.support zaimportuj requires
z tkinter zaimportuj Tk, Text

zaimportuj idlelib.AutoComplete jako ac
zaimportuj idlelib.AutoCompleteWindow jako acw
zaimportuj idlelib.macosxSupport jako mac
z idlelib.idle_test.mock_idle zaimportuj Func
z idlelib.idle_test.mock_tk zaimportuj Event

klasa AutoCompleteWindow:
    def complete():
        zwróć

klasa DummyEditwin:
    def __init__(self, root, text):
        self.root = root
        self.text = text
        self.indentwidth = 8
        self.tabwidth = 8
        self.context_use_ps1 = Prawda


klasa AutoCompleteTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        mac.setupApp(cls.root, Nic)
        cls.text = Text(cls.root)
        cls.editor = DummyEditwin(cls.root, cls.text)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        usuń cls.text
        usuń cls.editor
        usuń cls.root

    def setUp(self):
        self.editor.text.delete('1.0', 'end')
        self.autocomplete = ac.AutoComplete(self.editor)

    def test_init(self):
        self.assertEqual(self.autocomplete.editwin, self.editor)

    def test_make_autocomplete_window(self):
        testwin = self.autocomplete._make_autocomplete_window()
        self.assertIsInstance(testwin, acw.AutoCompleteWindow)

    def test_remove_autocomplete_window(self):
        self.autocomplete.autocompletewindow = (
            self.autocomplete._make_autocomplete_window())
        self.autocomplete._remove_autocomplete_window()
        self.assertIsNic(self.autocomplete.autocompletewindow)

    def test_force_open_completions_event(self):
        # Test that force_open_completions_event calls _open_completions
        o_cs = Func()
        self.autocomplete.open_completions = o_cs
        self.autocomplete.force_open_completions_event('event')
        self.assertEqual(o_cs.args, (Prawda, Nieprawda, Prawda))

    def test_try_open_completions_event(self):
        Equal = self.assertEqual
        autocomplete = self.autocomplete
        trycompletions = self.autocomplete.try_open_completions_event
        o_c_l = Func()
        autocomplete._open_completions_later = o_c_l

        # _open_completions_later should nie be called przy no text w editor
        trycompletions('event')
        Equal(o_c_l.args, Nic)

        # _open_completions_later should be called przy COMPLETE_ATTRIBUTES (1)
        self.text.insert('1.0', 're.')
        trycompletions('event')
        Equal(o_c_l.args, (Nieprawda, Nieprawda, Nieprawda, 1))

        # _open_completions_later should be called przy COMPLETE_FILES (2)
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', '"./Lib/')
        trycompletions('event')
        Equal(o_c_l.args, (Nieprawda, Nieprawda, Nieprawda, 2))

    def test_autocomplete_event(self):
        Equal = self.assertEqual
        autocomplete = self.autocomplete

        # Test that the autocomplete event jest ignored jeżeli user jest pressing a
        # modifier key w addition to the tab key
        ev = Event(mc_state=Prawda)
        self.assertIsNic(autocomplete.autocomplete_event(ev))
        usuń ev.mc_state

        # If autocomplete window jest open, complete() method jest called
        self.text.insert('1.0', 're.')
        # This must call autocomplete._make_autocomplete_window()
        Equal(self.autocomplete.autocomplete_event(ev), 'break')

        # If autocomplete window jest nie active albo does nie exist,
        # open_completions jest called. Return depends on its return.
        autocomplete._remove_autocomplete_window()
        o_cs = Func()  # .result = Nic
        autocomplete.open_completions = o_cs
        Equal(self.autocomplete.autocomplete_event(ev), Nic)
        Equal(o_cs.args, (Nieprawda, Prawda, Prawda))
        o_cs.result = Prawda
        Equal(self.autocomplete.autocomplete_event(ev), 'break')
        Equal(o_cs.args, (Nieprawda, Prawda, Prawda))

    def test_open_completions_later(self):
        # Test that autocomplete._delayed_completion_id jest set
        dalej

    def test_delayed_open_completions(self):
        # Test that autocomplete._delayed_completion_id set to Nic oraz that
        # open_completions only called jeżeli insertion index jest the same as
        # _delayed_completion_index
        dalej

    def test_open_completions(self):
        # Test completions of files oraz attributes jako well jako non-completion
        # of errors
        dalej

    def test_fetch_completions(self):
        # Test that fetch_completions returns 2 lists:
        # For attribute completion, a large list containing all variables, oraz
        # a small list containing non-private variables.
        # For file completion, a large list containing all files w the path,
        # oraz a small list containing files that do nie start przy '.'
        dalej

    def test_get_entity(self):
        # Test that a name jest w the namespace of sys.modules oraz
        # __main__.__dict__
        dalej


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2)
