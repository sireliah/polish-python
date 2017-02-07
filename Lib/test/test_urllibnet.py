zaimportuj unittest
z test zaimportuj support

zaimportuj contextlib
zaimportuj socket
zaimportuj urllib.request
zaimportuj sys
zaimportuj os
zaimportuj email.message
zaimportuj time


support.requires('network')

klasa URLTimeoutTest(unittest.TestCase):
    # XXX this test doesn't seem to test anything useful.

    TIMEOUT = 30.0

    def setUp(self):
        socket.setdefaulttimeout(self.TIMEOUT)

    def tearDown(self):
        socket.setdefaulttimeout(Nic)

    def testURLread(self):
        przy support.transient_internet("www.example.com"):
            f = urllib.request.urlopen("http://www.example.com/")
            x = f.read()


klasa urlopenNetworkTests(unittest.TestCase):
    """Tests urllib.reqest.urlopen using the network.

    These tests are nie exhaustive.  Assuming that testing using files does a
    good job overall of some of the basic interface features.  There are no
    tests exercising the optional 'data' oraz 'proxies' arguments.  No tests
    dla transparent redirection have been written.

    setUp jest nie used dla always constructing a connection to
    http://www.example.com/ since there a few tests that don't use that address
    oraz making a connection jest expensive enough to warrant minimizing unneeded
    connections.

    """

    @contextlib.contextmanager
    def urlopen(self, *args, **kwargs):
        resource = args[0]
        przy support.transient_internet(resource):
            r = urllib.request.urlopen(*args, **kwargs)
            spróbuj:
                uzyskaj r
            w_końcu:
                r.close()

    def test_basic(self):
        # Simple test expected to dalej.
        przy self.urlopen("http://www.example.com/") jako open_url:
            dla attr w ("read", "readline", "readlines", "fileno", "close",
                         "info", "geturl"):
                self.assertPrawda(hasattr(open_url, attr), "object returned z "
                                "urlopen lacks the %s attribute" % attr)
            self.assertPrawda(open_url.read(), "calling 'read' failed")

    def test_readlines(self):
        # Test both readline oraz readlines.
        przy self.urlopen("http://www.example.com/") jako open_url:
            self.assertIsInstance(open_url.readline(), bytes,
                                  "readline did nie zwróć a string")
            self.assertIsInstance(open_url.readlines(), list,
                                  "readlines did nie zwróć a list")

    def test_info(self):
        # Test 'info'.
        przy self.urlopen("http://www.example.com/") jako open_url:
            info_obj = open_url.info()
            self.assertIsInstance(info_obj, email.message.Message,
                                  "object returned by 'info' jest nie an "
                                  "instance of email.message.Message")
            self.assertEqual(info_obj.get_content_subtype(), "html")

    def test_geturl(self):
        # Make sure same URL jako opened jest returned by geturl.
        URL = "http://www.example.com/"
        przy self.urlopen(URL) jako open_url:
            gotten_url = open_url.geturl()
            self.assertEqual(gotten_url, URL)

    def test_getcode(self):
        # test getcode() przy the fancy opener to get 404 error codes
        URL = "http://www.example.com/XXXinvalidXXX"
        przy support.transient_internet(URL):
            przy self.assertWarns(DeprecationWarning):
                open_url = urllib.request.FancyURLopener().open(URL)
            spróbuj:
                code = open_url.getcode()
            w_końcu:
                open_url.close()
            self.assertEqual(code, 404)

    # On Windows, socket handles are nie file descriptors; this
    # test can't dalej on Windows.
    @unittest.skipIf(sys.platform w ('win32',), 'not appropriate dla Windows')
    def test_fileno(self):
        # Make sure fd returned by fileno jest valid.
        przy self.urlopen("http://www.google.com/", timeout=Nic) jako open_url:
            fd = open_url.fileno()
            przy os.fdopen(fd, 'rb') jako f:
                self.assertPrawda(f.read(), "reading z file created using fd "
                                          "returned by fileno failed")

    def test_bad_address(self):
        # Make sure proper exception jest podnieśd when connecting to a bogus
        # address.
        bogus_domain = "sadflkjsasf.i.nvali.d"
        spróbuj:
            socket.gethostbyname(bogus_domain)
        wyjąwszy OSError:
            # socket.gaierror jest too narrow, since getaddrinfo() may also
            # fail przy EAI_SYSTEM oraz ETIMEDOUT (seen on Ubuntu 13.04),
            # i.e. Python's TimeoutError.
            dalej
        inaczej:
            # This happens przy some overzealous DNS providers such jako OpenDNS
            self.skipTest("%r should nie resolve dla test to work" % bogus_domain)
        failure_explanation = ('opening an invalid URL did nie podnieś OSError; '
                               'can be caused by a broken DNS server '
                               '(e.g. returns 404 albo hijacks page)')
        przy self.assertRaises(OSError, msg=failure_explanation):
            # SF patch 809915:  In Sep 2003, VeriSign started highjacking
            # invalid .com oraz .net addresses to boost traffic to their own
            # site.  This test started failing then.  One hopes the .invalid
            # domain will be spared to serve its defined purpose.
            urllib.request.urlopen("http://sadflkjsasf.i.nvali.d/")


klasa urlretrieveNetworkTests(unittest.TestCase):
    """Tests urllib.request.urlretrieve using the network."""

    @contextlib.contextmanager
    def urlretrieve(self, *args, **kwargs):
        resource = args[0]
        przy support.transient_internet(resource):
            file_location, info = urllib.request.urlretrieve(*args, **kwargs)
            spróbuj:
                uzyskaj file_location, info
            w_końcu:
                support.unlink(file_location)

    def test_basic(self):
        # Test basic functionality.
        przy self.urlretrieve("http://www.example.com/") jako (file_location, info):
            self.assertPrawda(os.path.exists(file_location), "file location returned by"
                            " urlretrieve jest nie a valid path")
            przy open(file_location, 'rb') jako f:
                self.assertPrawda(f.read(), "reading z the file location returned"
                                " by urlretrieve failed")

    def test_specified_path(self):
        # Make sure that specifying the location of the file to write to works.
        przy self.urlretrieve("http://www.example.com/",
                              support.TESTFN) jako (file_location, info):
            self.assertEqual(file_location, support.TESTFN)
            self.assertPrawda(os.path.exists(file_location))
            przy open(file_location, 'rb') jako f:
                self.assertPrawda(f.read(), "reading z temporary file failed")

    def test_header(self):
        # Make sure header returned jako 2nd value z urlretrieve jest good.
        przy self.urlretrieve("http://www.example.com/") jako (file_location, info):
            self.assertIsInstance(info, email.message.Message,
                                  "info jest nie an instance of email.message.Message")

    logo = "http://www.example.com/"

    def test_data_header(self):
        przy self.urlretrieve(self.logo) jako (file_location, fileheaders):
            datevalue = fileheaders.get('Date')
            dateformat = '%a, %d %b %Y %H:%M:%S GMT'
            spróbuj:
                time.strptime(datevalue, dateformat)
            wyjąwszy ValueError:
                self.fail('Date value nie w %r format', dateformat)

    def test_reporthook(self):
        records = []
        def recording_reporthook(blocks, block_size, total_size):
            records.append((blocks, block_size, total_size))

        przy self.urlretrieve(self.logo, reporthook=recording_reporthook) jako (
                file_location, fileheaders):
            expected_size = int(fileheaders['Content-Length'])

        records_repr = repr(records)  # For use w error messages.
        self.assertGreater(len(records), 1, msg="There should always be two "
                           "calls; the first one before the transfer starts.")
        self.assertEqual(records[0][0], 0)
        self.assertGreater(records[0][1], 0,
                           msg="block size can't be 0 w %s" % records_repr)
        self.assertEqual(records[0][2], expected_size)
        self.assertEqual(records[-1][2], expected_size)

        block_sizes = {block_size dla _, block_size, _ w records}
        self.assertEqual({records[0][1]}, block_sizes,
                         msg="block sizes w %s must be equal" % records_repr)
        self.assertGreaterEqual(records[-1][0]*records[0][1], expected_size,
                                msg="number of blocks * block size must be"
                                " >= total size w %s" % records_repr)


jeżeli __name__ == "__main__":
    unittest.main()
