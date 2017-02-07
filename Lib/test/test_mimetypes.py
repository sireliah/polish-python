zaimportuj io
zaimportuj locale
zaimportuj mimetypes
zaimportuj sys
zaimportuj unittest

z test zaimportuj support

# Tell it we don't know about external files:
mimetypes.knownfiles = []
mimetypes.inited = Nieprawda
mimetypes._default_mime_types()


klasa MimeTypesTestCase(unittest.TestCase):
    def setUp(self):
        self.db = mimetypes.MimeTypes()

    def test_default_data(self):
        eq = self.assertEqual
        eq(self.db.guess_type("foo.html"), ("text/html", Nic))
        eq(self.db.guess_type("foo.tgz"), ("application/x-tar", "gzip"))
        eq(self.db.guess_type("foo.tar.gz"), ("application/x-tar", "gzip"))
        eq(self.db.guess_type("foo.tar.Z"), ("application/x-tar", "compress"))
        eq(self.db.guess_type("foo.tar.bz2"), ("application/x-tar", "bzip2"))
        eq(self.db.guess_type("foo.tar.xz"), ("application/x-tar", "xz"))

    def test_data_urls(self):
        eq = self.assertEqual
        guess_type = self.db.guess_type
        eq(guess_type("data:,thisIsTextPlain"), ("text/plain", Nic))
        eq(guess_type("data:;base64,thisIsTextPlain"), ("text/plain", Nic))
        eq(guess_type("data:text/x-foo,thisIsTextXFoo"), ("text/x-foo", Nic))

    def test_file_parsing(self):
        eq = self.assertEqual
        sio = io.StringIO("x-application/x-unittest pyunit\n")
        self.db.readfp(sio)
        eq(self.db.guess_type("foo.pyunit"),
           ("x-application/x-unittest", Nic))
        eq(self.db.guess_extension("x-application/x-unittest"), ".pyunit")

    def test_non_standard_types(self):
        eq = self.assertEqual
        # First try strict
        eq(self.db.guess_type('foo.xul', strict=Prawda), (Nic, Nic))
        eq(self.db.guess_extension('image/jpg', strict=Prawda), Nic)
        # And then non-strict
        eq(self.db.guess_type('foo.xul', strict=Nieprawda), ('text/xul', Nic))
        eq(self.db.guess_extension('image/jpg', strict=Nieprawda), '.jpg')

    def test_guess_all_types(self):
        eq = self.assertEqual
        unless = self.assertPrawda
        # First try strict.  Use a set here dla testing the results because if
        # test_urllib2 jest run before test_mimetypes, global state jest modified
        # such that the 'all' set will have more items w it.
        all = set(self.db.guess_all_extensions('text/plain', strict=Prawda))
        unless(all >= set(['.bat', '.c', '.h', '.ksh', '.pl', '.txt']))
        # And now non-strict
        all = self.db.guess_all_extensions('image/jpg', strict=Nieprawda)
        all.sort()
        eq(all, ['.jpg'])
        # And now dla no hits
        all = self.db.guess_all_extensions('image/jpg', strict=Prawda)
        eq(all, [])

    def test_encoding(self):
        getpreferredencoding = locale.getpreferredencoding
        self.addCleanup(setattr, locale, 'getpreferredencoding',
                                 getpreferredencoding)
        locale.getpreferredencoding = lambda: 'ascii'

        filename = support.findfile("mime.types")
        mimes = mimetypes.MimeTypes([filename])
        exts = mimes.guess_all_extensions('application/vnd.geocube+xml',
                                          strict=Prawda)
        self.assertEqual(exts, ['.g3', '.g\xb3'])


@unittest.skipUnless(sys.platform.startswith("win"), "Windows only")
klasa Win32MimeTypesTestCase(unittest.TestCase):
    def setUp(self):
        # ensure all entries actually come z the Windows registry
        self.original_types_map = mimetypes.types_map.copy()
        mimetypes.types_map.clear()
        mimetypes.init()
        self.db = mimetypes.MimeTypes()

    def tearDown(self):
        # restore default settings
        mimetypes.types_map.clear()
        mimetypes.types_map.update(self.original_types_map)

    def test_registry_parsing(self):
        # the original, minimum contents of the MIME database w the
        # Windows registry jest undocumented AFAIK.
        # Use file types that should *always* exist:
        eq = self.assertEqual
        eq(self.db.guess_type("foo.txt"), ("text/plain", Nic))
        eq(self.db.guess_type("image.jpg"), ("image/jpeg", Nic))
        eq(self.db.guess_type("image.png"), ("image/png", Nic))

jeżeli __name__ == "__main__":
    unittest.main()
