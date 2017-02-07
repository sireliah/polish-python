zaimportuj unittest
zaimportuj tkinter
z test.support zaimportuj requires, run_unittest
z tkinter.test.support zaimportuj AbstractTkTest

requires('gui')

klasa TextTest(AbstractTkTest, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.text = tkinter.Text(self.root)

    def test_debug(self):
        text = self.text
        olddebug = text.debug()
        spróbuj:
            text.debug(0)
            self.assertEqual(text.debug(), 0)
            text.debug(1)
            self.assertEqual(text.debug(), 1)
        w_końcu:
            text.debug(olddebug)
            self.assertEqual(text.debug(), olddebug)

    def test_search(self):
        text = self.text

        # pattern oraz index are obligatory arguments.
        self.assertRaises(tkinter.TclError, text.search, Nic, '1.0')
        self.assertRaises(tkinter.TclError, text.search, 'a', Nic)
        self.assertRaises(tkinter.TclError, text.search, Nic, Nic)

        # Invalid text index.
        self.assertRaises(tkinter.TclError, text.search, '', 0)

        # Check jeżeli we are getting the indices jako strings -- you are likely
        # to get Tcl_Obj under Tk 8.5 jeżeli Tkinter doesn't convert it.
        text.insert('1.0', 'hi-test')
        self.assertEqual(text.search('-test', '1.0', 'end'), '1.2')
        self.assertEqual(text.search('test', '1.0', 'end'), '1.3')


tests_gui = (TextTest, )

jeżeli __name__ == "__main__":
    run_unittest(*tests_gui)
