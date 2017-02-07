zaimportuj unittest
z test.support zaimportuj requires

zaimportuj tkinter jako tk
z tkinter zaimportuj Text jako tkText
z idlelib.idle_test.mock_tk zaimportuj Text jako mkText
z idlelib.IdleHistory zaimportuj History
z idlelib.configHandler zaimportuj idleConf

line1 = 'a = 7'
line2 = 'b = a'

klasa StoreTest(unittest.TestCase):
    '''Tests History.__init__ oraz History.store przy mock Text'''

    @classmethod
    def setUpClass(cls):
        cls.text = mkText()
        cls.history = History(cls.text)

    def tearDown(self):
        self.text.delete('1.0', 'end')
        self.history.history = []

    def test_init(self):
        self.assertIs(self.history.text, self.text)
        self.assertEqual(self.history.history, [])
        self.assertIsNic(self.history.prefix)
        self.assertIsNic(self.history.pointer)
        self.assertEqual(self.history.cyclic,
                idleConf.GetOption("main", "History",  "cyclic", 1, "bool"))

    def test_store_short(self):
        self.history.store('a')
        self.assertEqual(self.history.history, [])
        self.history.store('  a  ')
        self.assertEqual(self.history.history, [])

    def test_store_dup(self):
        self.history.store(line1)
        self.assertEqual(self.history.history, [line1])
        self.history.store(line2)
        self.assertEqual(self.history.history, [line1, line2])
        self.history.store(line1)
        self.assertEqual(self.history.history, [line2, line1])

    def test_store_reset(self):
        self.history.prefix = line1
        self.history.pointer = 0
        self.history.store(line2)
        self.assertIsNic(self.history.prefix)
        self.assertIsNic(self.history.pointer)


klasa TextWrapper:
    def __init__(self, master):
        self.text = tkText(master=master)
        self._bell = Nieprawda
    def __getattr__(self, name):
        zwróć getattr(self.text, name)
    def bell(self):
        self._bell = Prawda

klasa FetchTest(unittest.TestCase):
    '''Test History.fetch przy wrapped tk.Text.
    '''
    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = tk.Tk()

    def setUp(self):
        self.text = text = TextWrapper(self.root)
        text.insert('1.0', ">>> ")
        text.mark_set('iomark', '1.4')
        text.mark_gravity('iomark', 'left')
        self.history = History(text)
        self.history.history = [line1, line2]

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        usuń cls.root

    def fetch_test(self, reverse, line, prefix, index, *, bell=Nieprawda):
        # Perform one fetch jako invoked by Alt-N albo Alt-P
        # Test the result. The line test jest the most important.
        # The last two are diagnostic of fetch internals.
        History = self.history
        History.fetch(reverse)

        Equal = self.assertEqual
        Equal(self.text.get('iomark', 'end-1c'), line)
        Equal(self.text._bell, bell)
        jeżeli bell:
            self.text._bell = Nieprawda
        Equal(History.prefix, prefix)
        Equal(History.pointer, index)
        Equal(self.text.compare("insert", '==', "end-1c"), 1)

    def test_fetch_prev_cyclic(self):
        prefix = ''
        test = self.fetch_test
        test(Prawda, line2, prefix, 1)
        test(Prawda, line1, prefix, 0)
        test(Prawda, prefix, Nic, Nic, bell=Prawda)

    def test_fetch_next_cyclic(self):
        prefix = ''
        test  = self.fetch_test
        test(Nieprawda, line1, prefix, 0)
        test(Nieprawda, line2, prefix, 1)
        test(Nieprawda, prefix, Nic, Nic, bell=Prawda)

    # Prefix 'a' tests skip line2, which starts przy 'b'
    def test_fetch_prev_prefix(self):
        prefix = 'a'
        self.text.insert('iomark', prefix)
        self.fetch_test(Prawda, line1, prefix, 0)
        self.fetch_test(Prawda, prefix, Nic, Nic, bell=Prawda)

    def test_fetch_next_prefix(self):
        prefix = 'a'
        self.text.insert('iomark', prefix)
        self.fetch_test(Nieprawda, line1, prefix, 0)
        self.fetch_test(Nieprawda, prefix, Nic, Nic, bell=Prawda)

    def test_fetch_prev_noncyclic(self):
        prefix = ''
        self.history.cyclic = Nieprawda
        test = self.fetch_test
        test(Prawda, line2, prefix, 1)
        test(Prawda, line1, prefix, 0)
        test(Prawda, line1, prefix, 0, bell=Prawda)

    def test_fetch_next_noncyclic(self):
        prefix = ''
        self.history.cyclic = Nieprawda
        test  = self.fetch_test
        test(Nieprawda, prefix, Nic, Nic, bell=Prawda)
        test(Prawda, line2, prefix, 1)
        test(Nieprawda, prefix, Nic, Nic, bell=Prawda)
        test(Nieprawda, prefix, Nic, Nic, bell=Prawda)

    def test_fetch_cursor_move(self):
        # Move cursor after fetch
        self.history.fetch(reverse=Prawda)  # initialization
        self.text.mark_set('insert', 'iomark')
        self.fetch_test(Prawda, line2, Nic, Nic, bell=Prawda)

    def test_fetch_edit(self):
        # Edit after fetch
        self.history.fetch(reverse=Prawda)  # initialization
        self.text.delete('iomark', 'insert', )
        self.text.insert('iomark', 'a =')
        self.fetch_test(Prawda, line1, 'a =', 0)  # prefix jest reset

    def test_history_prev_next(self):
        # Minimally test functions bound to events
        self.history.history_prev('dummy event')
        self.assertEqual(self.history.pointer, 1)
        self.history.history_next('dummy event')
        self.assertEqual(self.history.pointer, Nic)


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
