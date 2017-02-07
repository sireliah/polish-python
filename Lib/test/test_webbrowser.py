zaimportuj webbrowser
zaimportuj unittest
zaimportuj subprocess
z unittest zaimportuj mock
z test zaimportuj support


URL = 'http://www.example.com'
CMD_NAME = 'test'


klasa PopenMock(mock.MagicMock):

    def poll(self):
        zwróć 0

    def wait(self, seconds=Nic):
        zwróć 0


klasa CommandTestMixin:

    def _test(self, meth, *, args=[URL], kw={}, options, arguments):
        """Given a web browser instance method name along przy arguments oraz
        keywords dla same (which defaults to the single argument URL), creates
        a browser instance z the klasa pointed to by self.browser, calls the
        indicated instance method przy the indicated arguments, oraz compares
        the resulting options oraz arguments dalejed to Popen by the browser
        instance against the 'options' oraz 'args' lists.  Options are compared
        w a position independent fashion, oraz the arguments are compared w
        sequence order to whatever jest left over after removing the options.

        """
        popen = PopenMock()
        support.patch(self, subprocess, 'Popen', popen)
        browser = self.browser_class(name=CMD_NAME)
        getattr(browser, meth)(*args, **kw)
        popen_args = subprocess.Popen.call_args[0][0]
        self.assertEqual(popen_args[0], CMD_NAME)
        popen_args.pop(0)
        dla option w options:
            self.assertIn(option, popen_args)
            popen_args.pop(popen_args.index(option))
        self.assertEqual(popen_args, arguments)


klasa GenericBrowserCommandTest(CommandTestMixin, unittest.TestCase):

    browser_class = webbrowser.GenericBrowser

    def test_open(self):
        self._test('open',
                   options=[],
                   arguments=[URL])


klasa BackgroundBrowserCommandTest(CommandTestMixin, unittest.TestCase):

    browser_class = webbrowser.BackgroundBrowser

    def test_open(self):
        self._test('open',
                   options=[],
                   arguments=[URL])


klasa ChromeCommandTest(CommandTestMixin, unittest.TestCase):

    browser_class = webbrowser.Chrome

    def test_open(self):
        self._test('open',
                   options=[],
                   arguments=[URL])

    def test_open_with_autoraise_false(self):
        self._test('open', kw=dict(autoraise=Nieprawda),
                   options=[],
                   arguments=[URL])

    def test_open_new(self):
        self._test('open_new',
                   options=['--new-window'],
                   arguments=[URL])

    def test_open_new_tab(self):
        self._test('open_new_tab',
                   options=[],
                   arguments=[URL])


klasa MozillaCommandTest(CommandTestMixin, unittest.TestCase):

    browser_class = webbrowser.Mozilla

    def test_open(self):
        self._test('open',
                   options=['-raise', '-remote'],
                   arguments=['openURL({})'.format(URL)])

    def test_open_with_autoraise_false(self):
        self._test('open', kw=dict(autoraise=Nieprawda),
                   options=['-noraise', '-remote'],
                   arguments=['openURL({})'.format(URL)])

    def test_open_new(self):
        self._test('open_new',
                   options=['-raise', '-remote'],
                   arguments=['openURL({},new-window)'.format(URL)])

    def test_open_new_tab(self):
        self._test('open_new_tab',
                   options=['-raise', '-remote'],
                   arguments=['openURL({},new-tab)'.format(URL)])


klasa GaleonCommandTest(CommandTestMixin, unittest.TestCase):

    browser_class = webbrowser.Galeon

    def test_open(self):
        self._test('open',
                   options=['-n'],
                   arguments=[URL])

    def test_open_with_autoraise_false(self):
        self._test('open', kw=dict(autoraise=Nieprawda),
                   options=['-noraise', '-n'],
                   arguments=[URL])

    def test_open_new(self):
        self._test('open_new',
                   options=['-w'],
                   arguments=[URL])

    def test_open_new_tab(self):
        self._test('open_new_tab',
                   options=['-w'],
                   arguments=[URL])


klasa OperaCommandTest(CommandTestMixin, unittest.TestCase):

    browser_class = webbrowser.Opera

    def test_open(self):
        self._test('open',
                   options=['-remote'],
                   arguments=['openURL({})'.format(URL)])

    def test_open_with_autoraise_false(self):
        self._test('open', kw=dict(autoraise=Nieprawda),
                   options=['-remote', '-noraise'],
                   arguments=['openURL({})'.format(URL)])

    def test_open_new(self):
        self._test('open_new',
                   options=['-remote'],
                   arguments=['openURL({},new-window)'.format(URL)])

    def test_open_new_tab(self):
        self._test('open_new_tab',
                   options=['-remote'],
                   arguments=['openURL({},new-page)'.format(URL)])


klasa ELinksCommandTest(CommandTestMixin, unittest.TestCase):

    browser_class = webbrowser.Elinks

    def test_open(self):
        self._test('open', options=['-remote'],
                           arguments=['openURL({})'.format(URL)])

    def test_open_with_autoraise_false(self):
        self._test('open',
                   options=['-remote'],
                   arguments=['openURL({})'.format(URL)])

    def test_open_new(self):
        self._test('open_new',
                   options=['-remote'],
                   arguments=['openURL({},new-window)'.format(URL)])

    def test_open_new_tab(self):
        self._test('open_new_tab',
                   options=['-remote'],
                   arguments=['openURL({},new-tab)'.format(URL)])


jeżeli __name__=='__main__':
    unittest.main()
