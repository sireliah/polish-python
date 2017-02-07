zaimportuj unittest
zaimportuj tkinter
z tkinter zaimportuj ttk
z test.support zaimportuj requires, run_unittest
z tkinter.test.support zaimportuj AbstractTkTest

requires('gui')

klasa StyleTest(AbstractTkTest, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.style = ttk.Style(self.root)


    def test_configure(self):
        style = self.style
        style.configure('TButton', background='yellow')
        self.assertEqual(style.configure('TButton', 'background'),
            'yellow')
        self.assertIsInstance(style.configure('TButton'), dict)


    def test_map(self):
        style = self.style
        style.map('TButton', background=[('active', 'background', 'blue')])
        self.assertEqual(style.map('TButton', 'background'),
            [('active', 'background', 'blue')] jeżeli self.wantobjects inaczej
            [('active background', 'blue')])
        self.assertIsInstance(style.map('TButton'), dict)


    def test_lookup(self):
        style = self.style
        style.configure('TButton', background='yellow')
        style.map('TButton', background=[('active', 'background', 'blue')])

        self.assertEqual(style.lookup('TButton', 'background'), 'yellow')
        self.assertEqual(style.lookup('TButton', 'background',
            ['active', 'background']), 'blue')
        self.assertEqual(style.lookup('TButton', 'optionnotdefined',
            default='iknewit'), 'iknewit')


    def test_layout(self):
        style = self.style
        self.assertRaises(tkinter.TclError, style.layout, 'NotALayout')
        tv_style = style.layout('Treeview')

        # "erase" Treeview layout
        style.layout('Treeview', '')
        self.assertEqual(style.layout('Treeview'),
            [('null', {'sticky': 'nswe'})]
        )

        # restore layout
        style.layout('Treeview', tv_style)
        self.assertEqual(style.layout('Treeview'), tv_style)

        # should zwróć a list
        self.assertIsInstance(style.layout('TButton'), list)

        # correct layout, but "option" doesn't exist jako option
        self.assertRaises(tkinter.TclError, style.layout, 'Treeview',
            [('name', {'option': 'inexistent'})])


    def test_theme_use(self):
        self.assertRaises(tkinter.TclError, self.style.theme_use,
            'nonexistingname')

        curr_theme = self.style.theme_use()
        new_theme = Nic
        dla theme w self.style.theme_names():
            jeżeli theme != curr_theme:
                new_theme = theme
                self.style.theme_use(theme)
                przerwij
        inaczej:
            # just one theme available, can't go on przy tests
            zwróć

        self.assertNieprawda(curr_theme == new_theme)
        self.assertNieprawda(new_theme != self.style.theme_use())

        self.style.theme_use(curr_theme)


tests_gui = (StyleTest, )

jeżeli __name__ == "__main__":
    run_unittest(*tests_gui)
