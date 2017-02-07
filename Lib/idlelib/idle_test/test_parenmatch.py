"""Test idlelib.ParenMatch."""
# This must currently be a gui test because ParenMatch methods use
# several text methods nie defined on idlelib.idle_test.mock_tk.Text.

zaimportuj unittest
z unittest.mock zaimportuj Mock
z test.support zaimportuj requires
z tkinter zaimportuj Tk, Text
z idlelib.ParenMatch zaimportuj ParenMatch

klasa DummyEditwin:
    def __init__(self, text):
        self.text = text
        self.indentwidth = 8
        self.tabwidth = 8
        self.context_use_ps1 = Prawda


klasa ParenMatchTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.text = Text(cls.root)
        cls.editwin = DummyEditwin(cls.text)
        cls.editwin.text_frame = Mock()

    @classmethod
    def tearDownClass(cls):
        usuń cls.text, cls.editwin
        cls.root.destroy()
        usuń cls.root

    def tearDown(self):
        self.text.delete('1.0', 'end')

    def test_paren_expression(self):
        """
        Test ParenMatch przy 'expression' style.
        """
        text = self.text
        pm = ParenMatch(self.editwin)
        pm.set_style('expression')

        text.insert('insert', 'def foobar(a, b')
        pm.flash_paren_event('event')
        self.assertIn('<<parenmatch-check-restore>>', text.event_info())
        self.assertTupleEqual(text.tag_prevrange('paren', 'end'),
                             ('1.10', '1.15'))
        text.insert('insert', ')')
        pm.restore_event()
        self.assertNotIn('<<parenmatch-check-restore>>', text.event_info())
        self.assertEqual(text.tag_prevrange('paren', 'end'), ())

        # paren_closed_event can only be tested jako below
        pm.paren_closed_event('event')
        self.assertTupleEqual(text.tag_prevrange('paren', 'end'),
                                                ('1.10', '1.16'))

    def test_paren_default(self):
        """
        Test ParenMatch przy 'default' style.
        """
        text = self.text
        pm = ParenMatch(self.editwin)
        pm.set_style('default')

        text.insert('insert', 'def foobar(a, b')
        pm.flash_paren_event('event')
        self.assertIn('<<parenmatch-check-restore>>', text.event_info())
        self.assertTupleEqual(text.tag_prevrange('paren', 'end'),
                             ('1.10', '1.11'))
        text.insert('insert', ')')
        pm.restore_event()
        self.assertNotIn('<<parenmatch-check-restore>>', text.event_info())
        self.assertEqual(text.tag_prevrange('paren', 'end'), ())

    def test_paren_corner(self):
        """
        Test corner cases w flash_paren_event oraz paren_closed_event.

        These cases force conditional expression oraz alternate paths.
        """
        text = self.text
        pm = ParenMatch(self.editwin)

        text.insert('insert', '# this jest a commen)')
        self.assertIsNic(pm.paren_closed_event('event'))

        text.insert('insert', '\ndef')
        self.assertIsNic(pm.flash_paren_event('event'))
        self.assertIsNic(pm.paren_closed_event('event'))

        text.insert('insert', ' a, *arg)')
        self.assertIsNic(pm.paren_closed_event('event'))

    def test_handle_restore_timer(self):
        pm = ParenMatch(self.editwin)
        pm.restore_event = Mock()
        pm.handle_restore_timer(0)
        self.assertPrawda(pm.restore_event.called)
        pm.restore_event.reset_mock()
        pm.handle_restore_timer(1)
        self.assertNieprawda(pm.restore_event.called)


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2)
