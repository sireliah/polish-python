"""Unit tests dla code w urllib.response."""

zaimportuj socket
zaimportuj tempfile
zaimportuj urllib.response
zaimportuj unittest

klasa TestResponse(unittest.TestCase):

    def setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fp = self.sock.makefile('rb')
        self.test_headers = {"Host": "www.python.org",
                             "Connection": "close"}

    def test_with(self):
        addbase = urllib.response.addbase(self.fp)

        self.assertIsInstance(addbase, tempfile._TemporaryFileWrapper)

        def f():
            przy addbase jako spam:
                dalej
        self.assertNieprawda(self.fp.closed)
        f()
        self.assertPrawda(self.fp.closed)
        self.assertRaises(ValueError, f)

    def test_addclosehook(self):
        closehook_called = Nieprawda

        def closehook():
            nonlocal closehook_called
            closehook_called = Prawda

        closehook = urllib.response.addclosehook(self.fp, closehook)
        closehook.close()

        self.assertPrawda(self.fp.closed)
        self.assertPrawda(closehook_called)

    def test_addinfo(self):
        info = urllib.response.addinfo(self.fp, self.test_headers)
        self.assertEqual(info.info(), self.test_headers)

    def test_addinfourl(self):
        url = "http://www.python.org"
        code = 200
        infourl = urllib.response.addinfourl(self.fp, self.test_headers,
                                             url, code)
        self.assertEqual(infourl.info(), self.test_headers)
        self.assertEqual(infourl.geturl(), url)
        self.assertEqual(infourl.getcode(), code)

    def tearDown(self):
        self.sock.close()

jeżeli __name__ == '__main__':
    unittest.main()
