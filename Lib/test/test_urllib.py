"""Regresssion tests dla urllib"""

zaimportuj urllib.parse
zaimportuj urllib.request
zaimportuj urllib.error
zaimportuj http.client
zaimportuj email.message
zaimportuj io
zaimportuj unittest
z unittest.mock zaimportuj patch
z test zaimportuj support
zaimportuj os
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    ssl = Nic
zaimportuj sys
zaimportuj tempfile
z nturl2path zaimportuj url2pathname, pathname2url

z base64 zaimportuj b64encode
zaimportuj collections


def hexescape(char):
    """Escape char jako RFC 2396 specifies"""
    hex_repr = hex(ord(char))[2:].upper()
    jeżeli len(hex_repr) == 1:
        hex_repr = "0%s" % hex_repr
    zwróć "%" + hex_repr

# Shortcut dla testing FancyURLopener
_urlopener = Nic


def urlopen(url, data=Nic, proxies=Nic):
    """urlopen(url [, data]) -> open file-like object"""
    global _urlopener
    jeżeli proxies jest nie Nic:
        opener = urllib.request.FancyURLopener(proxies=proxies)
    albo_inaczej nie _urlopener:
        przy support.check_warnings(
                ('FancyURLopener style of invoking requests jest deprecated.',
                DeprecationWarning)):
            opener = urllib.request.FancyURLopener()
        _urlopener = opener
    inaczej:
        opener = _urlopener
    jeżeli data jest Nic:
        zwróć opener.open(url)
    inaczej:
        zwróć opener.open(url, data)


def fakehttp(fakedata):
    klasa FakeSocket(io.BytesIO):
        io_refs = 1

        def sendall(self, data):
            FakeHTTPConnection.buf = data

        def makefile(self, *args, **kwds):
            self.io_refs += 1
            zwróć self

        def read(self, amt=Nic):
            jeżeli self.closed:
                zwróć b""
            zwróć io.BytesIO.read(self, amt)

        def readline(self, length=Nic):
            jeżeli self.closed:
                zwróć b""
            zwróć io.BytesIO.readline(self, length)

        def close(self):
            self.io_refs -= 1
            jeżeli self.io_refs == 0:
                io.BytesIO.close(self)

    klasa FakeHTTPConnection(http.client.HTTPConnection):

        # buffer to store data dla verification w urlopen tests.
        buf = Nic
        fakesock = FakeSocket(fakedata)

        def connect(self):
            self.sock = self.fakesock

    zwróć FakeHTTPConnection


klasa FakeHTTPMixin(object):
    def fakehttp(self, fakedata):
        self._connection_class = http.client.HTTPConnection
        http.client.HTTPConnection = fakehttp(fakedata)

    def unfakehttp(self):
        http.client.HTTPConnection = self._connection_class


klasa FakeFTPMixin(object):
    def fakeftp(self):
        klasa FakeFtpWrapper(object):
            def __init__(self,  user, dalejwd, host, port, dirs, timeout=Nic,
                     persistent=Prawda):
                dalej

            def retrfile(self, file, type):
                zwróć io.BytesIO(), 0

            def close(self):
                dalej

        self._ftpwrapper_class = urllib.request.ftpwrapper
        urllib.request.ftpwrapper = FakeFtpWrapper

    def unfakeftp(self):
        urllib.request.ftpwrapper = self._ftpwrapper_class


klasa urlopen_FileTests(unittest.TestCase):
    """Test urlopen() opening a temporary file.

    Try to test jako much functionality jako possible so jako to cut down on reliance
    on connecting to the Net dla testing.

    """

    def setUp(self):
        # Create a temp file to use dla testing
        self.text = bytes("test_urllib: %s\n" % self.__class__.__name__,
                          "ascii")
        f = open(support.TESTFN, 'wb')
        spróbuj:
            f.write(self.text)
        w_końcu:
            f.close()
        self.pathname = support.TESTFN
        self.returned_obj = urlopen("file:%s" % self.pathname)

    def tearDown(self):
        """Shut down the open object"""
        self.returned_obj.close()
        os.remove(support.TESTFN)

    def test_interface(self):
        # Make sure object returned by urlopen() has the specified methods
        dla attr w ("read", "readline", "readlines", "fileno",
                     "close", "info", "geturl", "getcode", "__iter__"):
            self.assertPrawda(hasattr(self.returned_obj, attr),
                         "object returned by urlopen() lacks %s attribute" %
                         attr)

    def test_read(self):
        self.assertEqual(self.text, self.returned_obj.read())

    def test_readline(self):
        self.assertEqual(self.text, self.returned_obj.readline())
        self.assertEqual(b'', self.returned_obj.readline(),
                         "calling readline() after exhausting the file did not"
                         " zwróć an empty string")

    def test_readlines(self):
        lines_list = self.returned_obj.readlines()
        self.assertEqual(len(lines_list), 1,
                         "readlines() returned the wrong number of lines")
        self.assertEqual(lines_list[0], self.text,
                         "readlines() returned improper text")

    def test_fileno(self):
        file_num = self.returned_obj.fileno()
        self.assertIsInstance(file_num, int, "fileno() did nie zwróć an int")
        self.assertEqual(os.read(file_num, len(self.text)), self.text,
                         "Reading on the file descriptor returned by fileno() "
                         "did nie zwróć the expected text")

    def test_close(self):
        # Test close() by calling it here oraz then having it be called again
        # by the tearDown() method dla the test
        self.returned_obj.close()

    def test_info(self):
        self.assertIsInstance(self.returned_obj.info(), email.message.Message)

    def test_geturl(self):
        self.assertEqual(self.returned_obj.geturl(), self.pathname)

    def test_getcode(self):
        self.assertIsNic(self.returned_obj.getcode())

    def test_iter(self):
        # Test iterator
        # Don't need to count number of iterations since test would fail the
        # instant it returned anything beyond the first line z the
        # comparison.
        # Use the iterator w the usual implicit way to test dla ticket #4608.
        dla line w self.returned_obj:
            self.assertEqual(line, self.text)

    def test_relativelocalfile(self):
        self.assertRaises(ValueError,urllib.request.urlopen,'./' + self.pathname)

klasa ProxyTests(unittest.TestCase):

    def setUp(self):
        # Records changes to env vars
        self.env = support.EnvironmentVarGuard()
        # Delete all proxy related env vars
        dla k w list(os.environ):
            jeżeli 'proxy' w k.lower():
                self.env.unset(k)

    def tearDown(self):
        # Restore all proxy related env vars
        self.env.__exit__()
        usuń self.env

    def test_getproxies_environment_keep_no_proxies(self):
        self.env.set('NO_PROXY', 'localhost')
        proxies = urllib.request.getproxies_environment()
        # getproxies_environment use lowered case truncated (no '_proxy') keys
        self.assertEqual('localhost', proxies['no'])
        # List of no_proxies przy space.
        self.env.set('NO_PROXY', 'localhost, anotherdomain.com, newdomain.com')
        self.assertPrawda(urllib.request.proxy_bypass_environment('anotherdomain.com'))

klasa urlopen_HttpTests(unittest.TestCase, FakeHTTPMixin, FakeFTPMixin):
    """Test urlopen() opening a fake http connection."""

    def check_read(self, ver):
        self.fakehttp(b"HTTP/" + ver + b" 200 OK\r\n\r\nHello!")
        spróbuj:
            fp = urlopen("http://python.org/")
            self.assertEqual(fp.readline(), b"Hello!")
            self.assertEqual(fp.readline(), b"")
            self.assertEqual(fp.geturl(), 'http://python.org/')
            self.assertEqual(fp.getcode(), 200)
        w_końcu:
            self.unfakehttp()

    def test_url_fragment(self):
        # Issue #11703: geturl() omits fragments w the original URL.
        url = 'http://docs.python.org/library/urllib.html#OK'
        self.fakehttp(b"HTTP/1.1 200 OK\r\n\r\nHello!")
        spróbuj:
            fp = urllib.request.urlopen(url)
            self.assertEqual(fp.geturl(), url)
        w_końcu:
            self.unfakehttp()

    def test_willclose(self):
        self.fakehttp(b"HTTP/1.1 200 OK\r\n\r\nHello!")
        spróbuj:
            resp = urlopen("http://www.python.org")
            self.assertPrawda(resp.fp.will_close)
        w_końcu:
            self.unfakehttp()

    def test_read_0_9(self):
        # "0.9" response accepted (but nie "simple responses" without
        # a status line)
        self.check_read(b"0.9")

    def test_read_1_0(self):
        self.check_read(b"1.0")

    def test_read_1_1(self):
        self.check_read(b"1.1")

    def test_read_bogus(self):
        # urlopen() should podnieś OSError dla many error codes.
        self.fakehttp(b'''HTTP/1.1 401 Authentication Required
Date: Wed, 02 Jan 2008 03:03:54 GMT
Server: Apache/1.3.33 (Debian GNU/Linux) mod_ssl/2.8.22 OpenSSL/0.9.7e
Connection: close
Content-Type: text/html; charset=iso-8859-1
''')
        spróbuj:
            self.assertRaises(OSError, urlopen, "http://python.org/")
        w_końcu:
            self.unfakehttp()

    def test_invalid_redirect(self):
        # urlopen() should podnieś OSError dla many error codes.
        self.fakehttp(b'''HTTP/1.1 302 Found
Date: Wed, 02 Jan 2008 03:03:54 GMT
Server: Apache/1.3.33 (Debian GNU/Linux) mod_ssl/2.8.22 OpenSSL/0.9.7e
Location: file://guidocomputer.athome.com:/python/license
Connection: close
Content-Type: text/html; charset=iso-8859-1
''')
        spróbuj:
            self.assertRaises(urllib.error.HTTPError, urlopen,
                              "http://python.org/")
        w_końcu:
            self.unfakehttp()

    def test_empty_socket(self):
        # urlopen() podnieśs OSError jeżeli the underlying socket does nie send any
        # data. (#1680230)
        self.fakehttp(b'')
        spróbuj:
            self.assertRaises(OSError, urlopen, "http://something")
        w_końcu:
            self.unfakehttp()

    def test_missing_localfile(self):
        # Test dla #10836
        przy self.assertRaises(urllib.error.URLError) jako e:
            urlopen('file://localhost/a/file/which/doesnot/exists.py')
        self.assertPrawda(e.exception.filename)
        self.assertPrawda(e.exception.reason)

    def test_file_notexists(self):
        fd, tmp_file = tempfile.mkstemp()
        tmp_fileurl = 'file://localhost/' + tmp_file.replace(os.path.sep, '/')
        spróbuj:
            self.assertPrawda(os.path.exists(tmp_file))
            przy urlopen(tmp_fileurl) jako fobj:
                self.assertPrawda(fobj)
        w_końcu:
            os.close(fd)
            os.unlink(tmp_file)
        self.assertNieprawda(os.path.exists(tmp_file))
        przy self.assertRaises(urllib.error.URLError):
            urlopen(tmp_fileurl)

    def test_ftp_nohost(self):
        test_ftp_url = 'ftp:///path'
        przy self.assertRaises(urllib.error.URLError) jako e:
            urlopen(test_ftp_url)
        self.assertNieprawda(e.exception.filename)
        self.assertPrawda(e.exception.reason)

    def test_ftp_nonexisting(self):
        przy self.assertRaises(urllib.error.URLError) jako e:
            urlopen('ftp://localhost/a/file/which/doesnot/exists.py')
        self.assertNieprawda(e.exception.filename)
        self.assertPrawda(e.exception.reason)

    @patch.object(urllib.request, 'MAXFTPCACHE', 0)
    def test_ftp_cache_pruning(self):
        self.fakeftp()
        spróbuj:
            urllib.request.ftpcache['test'] = urllib.request.ftpwrapper('user', 'pass', 'localhost', 21, [])
            urlopen('ftp://localhost')
        w_końcu:
            self.unfakeftp()


    def test_userpass_inurl(self):
        self.fakehttp(b"HTTP/1.0 200 OK\r\n\r\nHello!")
        spróbuj:
            fp = urlopen("http://user:pass@python.org/")
            self.assertEqual(fp.readline(), b"Hello!")
            self.assertEqual(fp.readline(), b"")
            self.assertEqual(fp.geturl(), 'http://user:pass@python.org/')
            self.assertEqual(fp.getcode(), 200)
        w_końcu:
            self.unfakehttp()

    def test_userpass_inurl_w_spaces(self):
        self.fakehttp(b"HTTP/1.0 200 OK\r\n\r\nHello!")
        spróbuj:
            userpass = "a b:c d"
            url = "http://{}@python.org/".format(userpass)
            fakehttp_wrapper = http.client.HTTPConnection
            authorization = ("Authorization: Basic %s\r\n" %
                             b64encode(userpass.encode("ASCII")).decode("ASCII"))
            fp = urlopen(url)
            # The authorization header must be w place
            self.assertIn(authorization, fakehttp_wrapper.buf.decode("UTF-8"))
            self.assertEqual(fp.readline(), b"Hello!")
            self.assertEqual(fp.readline(), b"")
            # the spaces are quoted w URL so no match
            self.assertNotEqual(fp.geturl(), url)
            self.assertEqual(fp.getcode(), 200)
        w_końcu:
            self.unfakehttp()

    def test_URLopener_deprecation(self):
        przy support.check_warnings(('',DeprecationWarning)):
            urllib.request.URLopener()

    @unittest.skipUnless(ssl, "ssl module required")
    def test_cafile_and_context(self):
        context = ssl.create_default_context()
        przy self.assertRaises(ValueError):
            urllib.request.urlopen(
                "https://localhost", cafile="/nonexistent/path", context=context
            )

klasa urlopen_DataTests(unittest.TestCase):
    """Test urlopen() opening a data URL."""

    def setUp(self):
        # text containing URL special- oraz unicode-characters
        self.text = "test data URLs :;,%=& \u00f6 \u00c4 "
        # 2x1 pixel RGB PNG image przy one black oraz one white pixel
        self.image = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00'
            b'\x01\x08\x02\x00\x00\x00{@\xe8\xdd\x00\x00\x00\x01sRGB\x00\xae'
            b'\xce\x1c\xe9\x00\x00\x00\x0fIDAT\x08\xd7c```\xf8\xff\xff?\x00'
            b'\x06\x01\x02\xfe\no/\x1e\x00\x00\x00\x00IEND\xaeB`\x82')

        self.text_url = (
            "data:text/plain;charset=UTF-8,test%20data%20URLs%20%3A%3B%2C%25%3"
            "D%26%20%C3%B6%20%C3%84%20")
        self.text_url_base64 = (
            "data:text/plain;charset=ISO-8859-1;base64,dGVzdCBkYXRhIFVSTHMgOjs"
            "sJT0mIPYgxCA%3D")
        # base64 encoded data URL that contains ignorable spaces,
        # such jako "\n", " ", "%0A", oraz "%20".
        self.image_url = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAABCAIAAAB7\n"
            "QOjdAAAAAXNSR0IArs4c6QAAAA9JREFUCNdj%0AYGBg%2BP//PwAGAQL%2BCm8 "
            "vHgAAAABJRU5ErkJggg%3D%3D%0A%20")

        self.text_url_resp = urllib.request.urlopen(self.text_url)
        self.text_url_base64_resp = urllib.request.urlopen(
            self.text_url_base64)
        self.image_url_resp = urllib.request.urlopen(self.image_url)

    def test_interface(self):
        # Make sure object returned by urlopen() has the specified methods
        dla attr w ("read", "readline", "readlines",
                     "close", "info", "geturl", "getcode", "__iter__"):
            self.assertPrawda(hasattr(self.text_url_resp, attr),
                         "object returned by urlopen() lacks %s attribute" %
                         attr)

    def test_info(self):
        self.assertIsInstance(self.text_url_resp.info(), email.message.Message)
        self.assertEqual(self.text_url_base64_resp.info().get_params(),
            [('text/plain', ''), ('charset', 'ISO-8859-1')])
        self.assertEqual(self.image_url_resp.info()['content-length'],
            str(len(self.image)))
        self.assertEqual(urllib.request.urlopen("data:,").info().get_params(),
            [('text/plain', ''), ('charset', 'US-ASCII')])

    def test_geturl(self):
        self.assertEqual(self.text_url_resp.geturl(), self.text_url)
        self.assertEqual(self.text_url_base64_resp.geturl(),
            self.text_url_base64)
        self.assertEqual(self.image_url_resp.geturl(), self.image_url)

    def test_read_text(self):
        self.assertEqual(self.text_url_resp.read().decode(
            dict(self.text_url_resp.info().get_params())['charset']), self.text)

    def test_read_text_base64(self):
        self.assertEqual(self.text_url_base64_resp.read().decode(
            dict(self.text_url_base64_resp.info().get_params())['charset']),
            self.text)

    def test_read_image(self):
        self.assertEqual(self.image_url_resp.read(), self.image)

    def test_missing_comma(self):
        self.assertRaises(ValueError,urllib.request.urlopen,'data:text/plain')

    def test_invalid_base64_data(self):
        # missing padding character
        self.assertRaises(ValueError,urllib.request.urlopen,'data:;base64,Cg=')

klasa urlretrieve_FileTests(unittest.TestCase):
    """Test urllib.urlretrieve() on local files"""

    def setUp(self):
        # Create a list of temporary files. Each item w the list jest a file
        # name (absolute path albo relative to the current working directory).
        # All files w this list will be deleted w the tearDown method. Note,
        # this only helps to makes sure temporary files get deleted, but it
        # does nothing about trying to close files that may still be open. It
        # jest the responsibility of the developer to properly close files even
        # when exceptional conditions occur.
        self.tempFiles = []

        # Create a temporary file.
        self.registerFileForCleanUp(support.TESTFN)
        self.text = b'testing urllib.urlretrieve'
        spróbuj:
            FILE = open(support.TESTFN, 'wb')
            FILE.write(self.text)
            FILE.close()
        w_końcu:
            spróbuj: FILE.close()
            wyjąwszy: dalej

    def tearDown(self):
        # Delete the temporary files.
        dla each w self.tempFiles:
            spróbuj: os.remove(each)
            wyjąwszy: dalej

    def constructLocalFileUrl(self, filePath):
        filePath = os.path.abspath(filePath)
        spróbuj:
            filePath.encode("utf-8")
        wyjąwszy UnicodeEncodeError:
            podnieś unittest.SkipTest("filePath jest nie encodable to utf8")
        zwróć "file://%s" % urllib.request.pathname2url(filePath)

    def createNewTempFile(self, data=b""):
        """Creates a new temporary file containing the specified data,
        registers the file dla deletion during the test fixture tear down, oraz
        returns the absolute path of the file."""

        newFd, newFilePath = tempfile.mkstemp()
        spróbuj:
            self.registerFileForCleanUp(newFilePath)
            newFile = os.fdopen(newFd, "wb")
            newFile.write(data)
            newFile.close()
        w_końcu:
            spróbuj: newFile.close()
            wyjąwszy: dalej
        zwróć newFilePath

    def registerFileForCleanUp(self, fileName):
        self.tempFiles.append(fileName)

    def test_basic(self):
        # Make sure that a local file just gets its own location returned oraz
        # a headers value jest returned.
        result = urllib.request.urlretrieve("file:%s" % support.TESTFN)
        self.assertEqual(result[0], support.TESTFN)
        self.assertIsInstance(result[1], email.message.Message,
                              "did nie get a email.message.Message instance "
                              "as second returned value")

    def test_copy(self):
        # Test that setting the filename argument works.
        second_temp = "%s.2" % support.TESTFN
        self.registerFileForCleanUp(second_temp)
        result = urllib.request.urlretrieve(self.constructLocalFileUrl(
            support.TESTFN), second_temp)
        self.assertEqual(second_temp, result[0])
        self.assertPrawda(os.path.exists(second_temp), "copy of the file was nie "
                                                  "made")
        FILE = open(second_temp, 'rb')
        spróbuj:
            text = FILE.read()
            FILE.close()
        w_końcu:
            spróbuj: FILE.close()
            wyjąwszy: dalej
        self.assertEqual(self.text, text)

    def test_reporthook(self):
        # Make sure that the reporthook works.
        def hooktester(block_count, block_read_size, file_size, count_holder=[0]):
            self.assertIsInstance(block_count, int)
            self.assertIsInstance(block_read_size, int)
            self.assertIsInstance(file_size, int)
            self.assertEqual(block_count, count_holder[0])
            count_holder[0] = count_holder[0] + 1
        second_temp = "%s.2" % support.TESTFN
        self.registerFileForCleanUp(second_temp)
        urllib.request.urlretrieve(
            self.constructLocalFileUrl(support.TESTFN),
            second_temp, hooktester)

    def test_reporthook_0_bytes(self):
        # Test on zero length file. Should call reporthook only 1 time.
        report = []
        def hooktester(block_count, block_read_size, file_size, _report=report):
            _report.append((block_count, block_read_size, file_size))
        srcFileName = self.createNewTempFile()
        urllib.request.urlretrieve(self.constructLocalFileUrl(srcFileName),
            support.TESTFN, hooktester)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0][2], 0)

    def test_reporthook_5_bytes(self):
        # Test on 5 byte file. Should call reporthook only 2 times (once when
        # the "network connection" jest established oraz once when the block jest
        # read).
        report = []
        def hooktester(block_count, block_read_size, file_size, _report=report):
            _report.append((block_count, block_read_size, file_size))
        srcFileName = self.createNewTempFile(b"x" * 5)
        urllib.request.urlretrieve(self.constructLocalFileUrl(srcFileName),
            support.TESTFN, hooktester)
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0][2], 5)
        self.assertEqual(report[1][2], 5)

    def test_reporthook_8193_bytes(self):
        # Test on 8193 byte file. Should call reporthook only 3 times (once
        # when the "network connection" jest established, once dla the next 8192
        # bytes, oraz once dla the last byte).
        report = []
        def hooktester(block_count, block_read_size, file_size, _report=report):
            _report.append((block_count, block_read_size, file_size))
        srcFileName = self.createNewTempFile(b"x" * 8193)
        urllib.request.urlretrieve(self.constructLocalFileUrl(srcFileName),
            support.TESTFN, hooktester)
        self.assertEqual(len(report), 3)
        self.assertEqual(report[0][2], 8193)
        self.assertEqual(report[0][1], 8192)
        self.assertEqual(report[1][1], 8192)
        self.assertEqual(report[2][1], 8192)


klasa urlretrieve_HttpTests(unittest.TestCase, FakeHTTPMixin):
    """Test urllib.urlretrieve() using fake http connections"""

    def test_short_content_raises_ContentTooShortError(self):
        self.fakehttp(b'''HTTP/1.1 200 OK
Date: Wed, 02 Jan 2008 03:03:54 GMT
Server: Apache/1.3.33 (Debian GNU/Linux) mod_ssl/2.8.22 OpenSSL/0.9.7e
Connection: close
Content-Length: 100
Content-Type: text/html; charset=iso-8859-1

FF
''')

        def _reporthook(par1, par2, par3):
            dalej

        przy self.assertRaises(urllib.error.ContentTooShortError):
            spróbuj:
                urllib.request.urlretrieve('http://example.com/',
                                           reporthook=_reporthook)
            w_końcu:
                self.unfakehttp()

    def test_short_content_raises_ContentTooShortError_without_reporthook(self):
        self.fakehttp(b'''HTTP/1.1 200 OK
Date: Wed, 02 Jan 2008 03:03:54 GMT
Server: Apache/1.3.33 (Debian GNU/Linux) mod_ssl/2.8.22 OpenSSL/0.9.7e
Connection: close
Content-Length: 100
Content-Type: text/html; charset=iso-8859-1

FF
''')
        przy self.assertRaises(urllib.error.ContentTooShortError):
            spróbuj:
                urllib.request.urlretrieve('http://example.com/')
            w_końcu:
                self.unfakehttp()


klasa QuotingTests(unittest.TestCase):
    """Tests dla urllib.quote() oraz urllib.quote_plus()

    According to RFC 2396 (Uniform Resource Identifiers), to escape a
    character you write it jako '%' + <2 character US-ASCII hex value>.
    The Python code of ``'%' + hex(ord(<character>))[2:]`` escapes a
    character properly. Case does nie matter on the hex letters.

    The various character sets specified are:

    Reserved characters : ";/?:@&=+$,"
        Have special meaning w URIs oraz must be escaped jeżeli nie being used for
        their special meaning
    Data characters : letters, digits, oraz "-_.!~*'()"
        Unreserved oraz do nie need to be escaped; can be, though, jeżeli desired
    Control characters : 0x00 - 0x1F, 0x7F
        Have no use w URIs so must be escaped
    space : 0x20
        Must be escaped
    Delimiters : '<>#%"'
        Must be escaped
    Unwise : "{}|\^[]`"
        Must be escaped

    """

    def test_never_quote(self):
        # Make sure quote() does nie quote letters, digits, oraz "_,.-"
        do_not_quote = '' .join(["ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                                 "abcdefghijklmnopqrstuvwxyz",
                                 "0123456789",
                                 "_.-"])
        result = urllib.parse.quote(do_not_quote)
        self.assertEqual(do_not_quote, result,
                         "using quote(): %r != %r" % (do_not_quote, result))
        result = urllib.parse.quote_plus(do_not_quote)
        self.assertEqual(do_not_quote, result,
                        "using quote_plus(): %r != %r" % (do_not_quote, result))

    def test_default_safe(self):
        # Test '/' jest default value dla 'safe' parameter
        self.assertEqual(urllib.parse.quote.__defaults__[0], '/')

    def test_safe(self):
        # Test setting 'safe' parameter does what it should do
        quote_by_default = "<>"
        result = urllib.parse.quote(quote_by_default, safe=quote_by_default)
        self.assertEqual(quote_by_default, result,
                         "using quote(): %r != %r" % (quote_by_default, result))
        result = urllib.parse.quote_plus(quote_by_default,
                                         safe=quote_by_default)
        self.assertEqual(quote_by_default, result,
                         "using quote_plus(): %r != %r" %
                         (quote_by_default, result))
        # Safe expressed jako bytes rather than str
        result = urllib.parse.quote(quote_by_default, safe=b"<>")
        self.assertEqual(quote_by_default, result,
                         "using quote(): %r != %r" % (quote_by_default, result))
        # "Safe" non-ASCII characters should have no effect
        # (Since URIs are nie allowed to have non-ASCII characters)
        result = urllib.parse.quote("a\xfcb", encoding="latin-1", safe="\xfc")
        expect = urllib.parse.quote("a\xfcb", encoding="latin-1", safe="")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" %
                         (expect, result))
        # Same jako above, but using a bytes rather than str
        result = urllib.parse.quote("a\xfcb", encoding="latin-1", safe=b"\xfc")
        expect = urllib.parse.quote("a\xfcb", encoding="latin-1", safe="")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" %
                         (expect, result))

    def test_default_quoting(self):
        # Make sure all characters that should be quoted are by default sans
        # space (separate test dla that).
        should_quote = [chr(num) dla num w range(32)] # For 0x00 - 0x1F
        should_quote.append('<>#%"{}|\^[]`')
        should_quote.append(chr(127)) # For 0x7F
        should_quote = ''.join(should_quote)
        dla char w should_quote:
            result = urllib.parse.quote(char)
            self.assertEqual(hexescape(char), result,
                             "using quote(): "
                             "%s should be escaped to %s, nie %s" %
                             (char, hexescape(char), result))
            result = urllib.parse.quote_plus(char)
            self.assertEqual(hexescape(char), result,
                             "using quote_plus(): "
                             "%s should be escapes to %s, nie %s" %
                             (char, hexescape(char), result))
        usuń should_quote
        partial_quote = "ab[]cd"
        expected = "ab%5B%5Dcd"
        result = urllib.parse.quote(partial_quote)
        self.assertEqual(expected, result,
                         "using quote(): %r != %r" % (expected, result))
        result = urllib.parse.quote_plus(partial_quote)
        self.assertEqual(expected, result,
                         "using quote_plus(): %r != %r" % (expected, result))

    def test_quoting_space(self):
        # Make sure quote() oraz quote_plus() handle spaces jako specified w
        # their unique way
        result = urllib.parse.quote(' ')
        self.assertEqual(result, hexescape(' '),
                         "using quote(): %r != %r" % (result, hexescape(' ')))
        result = urllib.parse.quote_plus(' ')
        self.assertEqual(result, '+',
                         "using quote_plus(): %r != +" % result)
        given = "a b cd e f"
        expect = given.replace(' ', hexescape(' '))
        result = urllib.parse.quote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        expect = given.replace(' ', '+')
        result = urllib.parse.quote_plus(given)
        self.assertEqual(expect, result,
                         "using quote_plus(): %r != %r" % (expect, result))

    def test_quoting_plus(self):
        self.assertEqual(urllib.parse.quote_plus('alpha+beta gamma'),
                         'alpha%2Bbeta+gamma')
        self.assertEqual(urllib.parse.quote_plus('alpha+beta gamma', '+'),
                         'alpha+beta+gamma')
        # Test przy bytes
        self.assertEqual(urllib.parse.quote_plus(b'alpha+beta gamma'),
                         'alpha%2Bbeta+gamma')
        # Test przy safe bytes
        self.assertEqual(urllib.parse.quote_plus('alpha+beta gamma', b'+'),
                         'alpha+beta+gamma')

    def test_quote_bytes(self):
        # Bytes should quote directly to percent-encoded values
        given = b"\xa2\xd8ab\xff"
        expect = "%A2%D8ab%FF"
        result = urllib.parse.quote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Encoding argument should podnieś type error on bytes input
        self.assertRaises(TypeError, urllib.parse.quote, given,
                            encoding="latin-1")
        # quote_from_bytes should work the same
        result = urllib.parse.quote_from_bytes(given)
        self.assertEqual(expect, result,
                         "using quote_from_bytes(): %r != %r"
                         % (expect, result))

    def test_quote_with_unicode(self):
        # Characters w Latin-1 range, encoded by default w UTF-8
        given = "\xa2\xd8ab\xff"
        expect = "%C2%A2%C3%98ab%C3%BF"
        result = urllib.parse.quote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters w Latin-1 range, encoded by przy Nic (default)
        result = urllib.parse.quote(given, encoding=Nic, errors=Nic)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters w Latin-1 range, encoded przy Latin-1
        given = "\xa2\xd8ab\xff"
        expect = "%A2%D8ab%FF"
        result = urllib.parse.quote(given, encoding="latin-1")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters w BMP, encoded by default w UTF-8
        given = "\u6f22\u5b57"              # "Kanji"
        expect = "%E6%BC%A2%E5%AD%97"
        result = urllib.parse.quote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters w BMP, encoded przy Latin-1
        given = "\u6f22\u5b57"
        self.assertRaises(UnicodeEncodeError, urllib.parse.quote, given,
                                    encoding="latin-1")
        # Characters w BMP, encoded przy Latin-1, przy replace error handling
        given = "\u6f22\u5b57"
        expect = "%3F%3F"                   # "??"
        result = urllib.parse.quote(given, encoding="latin-1",
                                    errors="replace")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters w BMP, Latin-1, przy xmlcharref error handling
        given = "\u6f22\u5b57"
        expect = "%26%2328450%3B%26%2323383%3B"     # "&#28450;&#23383;"
        result = urllib.parse.quote(given, encoding="latin-1",
                                    errors="xmlcharrefreplace")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))

    def test_quote_plus_with_unicode(self):
        # Encoding (latin-1) test dla quote_plus
        given = "\xa2\xd8 \xff"
        expect = "%A2%D8+%FF"
        result = urllib.parse.quote_plus(given, encoding="latin-1")
        self.assertEqual(expect, result,
                         "using quote_plus(): %r != %r" % (expect, result))
        # Errors test dla quote_plus
        given = "ab\u6f22\u5b57 cd"
        expect = "ab%3F%3F+cd"
        result = urllib.parse.quote_plus(given, encoding="latin-1",
                                         errors="replace")
        self.assertEqual(expect, result,
                         "using quote_plus(): %r != %r" % (expect, result))


klasa UnquotingTests(unittest.TestCase):
    """Tests dla unquote() oraz unquote_plus()

    See the doc string dla quoting_Tests dla details on quoting oraz such.

    """

    def test_unquoting(self):
        # Make sure unquoting of all ASCII values works
        escape_list = []
        dla num w range(128):
            given = hexescape(chr(num))
            expect = chr(num)
            result = urllib.parse.unquote(given)
            self.assertEqual(expect, result,
                             "using unquote(): %r != %r" % (expect, result))
            result = urllib.parse.unquote_plus(given)
            self.assertEqual(expect, result,
                             "using unquote_plus(): %r != %r" %
                             (expect, result))
            escape_list.append(given)
        escape_string = ''.join(escape_list)
        usuń escape_list
        result = urllib.parse.unquote(escape_string)
        self.assertEqual(result.count('%'), 1,
                         "using unquote(): nie all characters escaped: "
                         "%s" % result)
        self.assertRaises((TypeError, AttributeError), urllib.parse.unquote, Nic)
        self.assertRaises((TypeError, AttributeError), urllib.parse.unquote, ())
        przy support.check_warnings(('', BytesWarning), quiet=Prawda):
            self.assertRaises((TypeError, AttributeError), urllib.parse.unquote, b'')

    def test_unquoting_badpercent(self):
        # Test unquoting on bad percent-escapes
        given = '%xab'
        expect = given
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result, "using unquote(): %r != %r"
                         % (expect, result))
        given = '%x'
        expect = given
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result, "using unquote(): %r != %r"
                         % (expect, result))
        given = '%'
        expect = given
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result, "using unquote(): %r != %r"
                         % (expect, result))
        # unquote_to_bytes
        given = '%xab'
        expect = bytes(given, 'ascii')
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result, "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        given = '%x'
        expect = bytes(given, 'ascii')
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result, "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        given = '%'
        expect = bytes(given, 'ascii')
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result, "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        self.assertRaises((TypeError, AttributeError), urllib.parse.unquote_to_bytes, Nic)
        self.assertRaises((TypeError, AttributeError), urllib.parse.unquote_to_bytes, ())

    def test_unquoting_mixed_case(self):
        # Test unquoting on mixed-case hex digits w the percent-escapes
        given = '%Ab%eA'
        expect = b'\xab\xea'
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))

    def test_unquoting_parts(self):
        # Make sure unquoting works when have non-quoted characters
        # interspersed
        given = 'ab%sd' % hexescape('c')
        expect = "abcd"
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        result = urllib.parse.unquote_plus(given)
        self.assertEqual(expect, result,
                         "using unquote_plus(): %r != %r" % (expect, result))

    def test_unquoting_plus(self):
        # Test difference between unquote() oraz unquote_plus()
        given = "are+there+spaces..."
        expect = given
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))
        expect = given.replace('+', ' ')
        result = urllib.parse.unquote_plus(given)
        self.assertEqual(expect, result,
                         "using unquote_plus(): %r != %r" % (expect, result))

    def test_unquote_to_bytes(self):
        given = 'br%C3%BCckner_sapporo_20050930.doc'
        expect = b'br\xc3\xbcckner_sapporo_20050930.doc'
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        # Test on a string przy unescaped non-ASCII characters
        # (Technically an invalid URI; expect those characters to be UTF-8
        # encoded).
        result = urllib.parse.unquote_to_bytes("\u6f22%C3%BC")
        expect = b'\xe6\xbc\xa2\xc3\xbc'    # UTF-8 dla "\u6f22\u00fc"
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        # Test przy a bytes jako input
        given = b'%A2%D8ab%FF'
        expect = b'\xa2\xd8ab\xff'
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        # Test przy a bytes jako input, przy unescaped non-ASCII bytes
        # (Technically an invalid URI; expect those bytes to be preserved)
        given = b'%A2\xd8ab%FF'
        expect = b'\xa2\xd8ab\xff'
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))

    def test_unquote_with_unicode(self):
        # Characters w the Latin-1 range, encoded przy UTF-8
        given = 'br%C3%BCckner_sapporo_20050930.doc'
        expect = 'br\u00fcckner_sapporo_20050930.doc'
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))
        # Characters w the Latin-1 range, encoded przy Nic (default)
        result = urllib.parse.unquote(given, encoding=Nic, errors=Nic)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Characters w the Latin-1 range, encoded przy Latin-1
        result = urllib.parse.unquote('br%FCckner_sapporo_20050930.doc',
                                      encoding="latin-1")
        expect = 'br\u00fcckner_sapporo_20050930.doc'
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Characters w BMP, encoded przy UTF-8
        given = "%E6%BC%A2%E5%AD%97"
        expect = "\u6f22\u5b57"             # "Kanji"
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Decode przy UTF-8, invalid sequence
        given = "%F3%B1"
        expect = "\ufffd"                   # Replacement character
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Decode przy UTF-8, invalid sequence, replace errors
        result = urllib.parse.unquote(given, errors="replace")
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Decode przy UTF-8, invalid sequence, ignoring errors
        given = "%F3%B1"
        expect = ""
        result = urllib.parse.unquote(given, errors="ignore")
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # A mix of non-ASCII oraz percent-encoded characters, UTF-8
        result = urllib.parse.unquote("\u6f22%C3%BC")
        expect = '\u6f22\u00fc'
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # A mix of non-ASCII oraz percent-encoded characters, Latin-1
        # (Note, the string contains non-Latin-1-representable characters)
        result = urllib.parse.unquote("\u6f22%FC", encoding="latin-1")
        expect = '\u6f22\u00fc'
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

klasa urlencode_Tests(unittest.TestCase):
    """Tests dla urlencode()"""

    def help_inputtype(self, given, test_type):
        """Helper method dla testing different input types.

        'given' must lead to only the pairs:
            * 1st, 1
            * 2nd, 2
            * 3rd, 3

        Test cannot assume anything about order.  Docs make no guarantee oraz
        have possible dictionary input.

        """
        expect_somewhere = ["1st=1", "2nd=2", "3rd=3"]
        result = urllib.parse.urlencode(given)
        dla expected w expect_somewhere:
            self.assertIn(expected, result,
                         "testing %s: %s nie found w %s" %
                         (test_type, expected, result))
        self.assertEqual(result.count('&'), 2,
                         "testing %s: expected 2 '&'s; got %s" %
                         (test_type, result.count('&')))
        amp_location = result.index('&')
        on_amp_left = result[amp_location - 1]
        on_amp_right = result[amp_location + 1]
        self.assertPrawda(on_amp_left.isdigit() oraz on_amp_right.isdigit(),
                     "testing %s: '&' nie located w proper place w %s" %
                     (test_type, result))
        self.assertEqual(len(result), (5 * 3) + 2, #5 chars per thing oraz amps
                         "testing %s: "
                         "unexpected number of characters: %s != %s" %
                         (test_type, len(result), (5 * 3) + 2))

    def test_using_mapping(self):
        # Test dalejing w a mapping object jako an argument.
        self.help_inputtype({"1st":'1', "2nd":'2', "3rd":'3'},
                            "using dict jako input type")

    def test_using_sequence(self):
        # Test dalejing w a sequence of two-item sequences jako an argument.
        self.help_inputtype([('1st', '1'), ('2nd', '2'), ('3rd', '3')],
                            "using sequence of two-item tuples jako input")

    def test_quoting(self):
        # Make sure keys oraz values are quoted using quote_plus()
        given = {"&":"="}
        expect = "%s=%s" % (hexescape('&'), hexescape('='))
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)
        given = {"key name":"A bunch of pluses"}
        expect = "key+name=A+bunch+of+pluses"
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)

    def test_doseq(self):
        # Test that dalejing Prawda dla 'doseq' parameter works correctly
        given = {'sequence':['1', '2', '3']}
        expect = "sequence=%s" % urllib.parse.quote_plus(str(['1', '2', '3']))
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)
        result = urllib.parse.urlencode(given, Prawda)
        dla value w given["sequence"]:
            expect = "sequence=%s" % value
            self.assertIn(expect, result)
        self.assertEqual(result.count('&'), 2,
                         "Expected 2 '&'s, got %s" % result.count('&'))

    def test_empty_sequence(self):
        self.assertEqual("", urllib.parse.urlencode({}))
        self.assertEqual("", urllib.parse.urlencode([]))

    def test_nonstring_values(self):
        self.assertEqual("a=1", urllib.parse.urlencode({"a": 1}))
        self.assertEqual("a=Nic", urllib.parse.urlencode({"a": Nic}))

    def test_nonstring_seq_values(self):
        self.assertEqual("a=1&a=2", urllib.parse.urlencode({"a": [1, 2]}, Prawda))
        self.assertEqual("a=Nic&a=a",
                         urllib.parse.urlencode({"a": [Nic, "a"]}, Prawda))
        data = collections.OrderedDict([("a", 1), ("b", 1)])
        self.assertEqual("a=a&a=b",
                         urllib.parse.urlencode({"a": data}, Prawda))

    def test_urlencode_encoding(self):
        # ASCII encoding. Expect %3F przy errors="replace'
        given = (('\u00a0', '\u00c1'),)
        expect = '%3F=%3F'
        result = urllib.parse.urlencode(given, encoding="ASCII", errors="replace")
        self.assertEqual(expect, result)

        # Default jest UTF-8 encoding.
        given = (('\u00a0', '\u00c1'),)
        expect = '%C2%A0=%C3%81'
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)

        # Latin-1 encoding.
        given = (('\u00a0', '\u00c1'),)
        expect = '%A0=%C1'
        result = urllib.parse.urlencode(given, encoding="latin-1")
        self.assertEqual(expect, result)

    def test_urlencode_encoding_doseq(self):
        # ASCII Encoding. Expect %3F przy errors="replace'
        given = (('\u00a0', '\u00c1'),)
        expect = '%3F=%3F'
        result = urllib.parse.urlencode(given, doseq=Prawda,
                                        encoding="ASCII", errors="replace")
        self.assertEqual(expect, result)

        # ASCII Encoding. On a sequence of values.
        given = (("\u00a0", (1, "\u00c1")),)
        expect = '%3F=1&%3F=%3F'
        result = urllib.parse.urlencode(given, Prawda,
                                        encoding="ASCII", errors="replace")
        self.assertEqual(expect, result)

        # Utf-8
        given = (("\u00a0", "\u00c1"),)
        expect = '%C2%A0=%C3%81'
        result = urllib.parse.urlencode(given, Prawda)
        self.assertEqual(expect, result)

        given = (("\u00a0", (42, "\u00c1")),)
        expect = '%C2%A0=42&%C2%A0=%C3%81'
        result = urllib.parse.urlencode(given, Prawda)
        self.assertEqual(expect, result)

        # latin-1
        given = (("\u00a0", "\u00c1"),)
        expect = '%A0=%C1'
        result = urllib.parse.urlencode(given, Prawda, encoding="latin-1")
        self.assertEqual(expect, result)

        given = (("\u00a0", (42, "\u00c1")),)
        expect = '%A0=42&%A0=%C1'
        result = urllib.parse.urlencode(given, Prawda, encoding="latin-1")
        self.assertEqual(expect, result)

    def test_urlencode_bytes(self):
        given = ((b'\xa0\x24', b'\xc1\x24'),)
        expect = '%A0%24=%C1%24'
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)
        result = urllib.parse.urlencode(given, Prawda)
        self.assertEqual(expect, result)

        # Sequence of values
        given = ((b'\xa0\x24', (42, b'\xc1\x24')),)
        expect = '%A0%24=42&%A0%24=%C1%24'
        result = urllib.parse.urlencode(given, Prawda)
        self.assertEqual(expect, result)

    def test_urlencode_encoding_safe_parameter(self):

        # Send '$' (\x24) jako safe character
        # Default utf-8 encoding

        given = ((b'\xa0\x24', b'\xc1\x24'),)
        result = urllib.parse.urlencode(given, safe=":$")
        expect = '%A0$=%C1$'
        self.assertEqual(expect, result)

        given = ((b'\xa0\x24', b'\xc1\x24'),)
        result = urllib.parse.urlencode(given, doseq=Prawda, safe=":$")
        expect = '%A0$=%C1$'
        self.assertEqual(expect, result)

        # Safe parameter w sequence
        given = ((b'\xa0\x24', (b'\xc1\x24', 0xd, 42)),)
        expect = '%A0$=%C1$&%A0$=13&%A0$=42'
        result = urllib.parse.urlencode(given, Prawda, safe=":$")
        self.assertEqual(expect, result)

        # Test all above w latin-1 encoding

        given = ((b'\xa0\x24', b'\xc1\x24'),)
        result = urllib.parse.urlencode(given, safe=":$",
                                        encoding="latin-1")
        expect = '%A0$=%C1$'
        self.assertEqual(expect, result)

        given = ((b'\xa0\x24', b'\xc1\x24'),)
        expect = '%A0$=%C1$'
        result = urllib.parse.urlencode(given, doseq=Prawda, safe=":$",
                                        encoding="latin-1")

        given = ((b'\xa0\x24', (b'\xc1\x24', 0xd, 42)),)
        expect = '%A0$=%C1$&%A0$=13&%A0$=42'
        result = urllib.parse.urlencode(given, Prawda, safe=":$",
                                        encoding="latin-1")
        self.assertEqual(expect, result)

klasa Pathname_Tests(unittest.TestCase):
    """Test pathname2url() oraz url2pathname()"""

    def test_basic(self):
        # Make sure simple tests dalej
        expected_path = os.path.join("parts", "of", "a", "path")
        expected_url = "parts/of/a/path"
        result = urllib.request.pathname2url(expected_path)
        self.assertEqual(expected_url, result,
                         "pathname2url() failed; %s != %s" %
                         (result, expected_url))
        result = urllib.request.url2pathname(expected_url)
        self.assertEqual(expected_path, result,
                         "url2pathame() failed; %s != %s" %
                         (result, expected_path))

    def test_quoting(self):
        # Test automatic quoting oraz unquoting works dla pathnam2url() oraz
        # url2pathname() respectively
        given = os.path.join("needs", "quot=ing", "here")
        expect = "needs/%s/here" % urllib.parse.quote("quot=ing")
        result = urllib.request.pathname2url(given)
        self.assertEqual(expect, result,
                         "pathname2url() failed; %s != %s" %
                         (expect, result))
        expect = given
        result = urllib.request.url2pathname(result)
        self.assertEqual(expect, result,
                         "url2pathname() failed; %s != %s" %
                         (expect, result))
        given = os.path.join("make sure", "using_quote")
        expect = "%s/using_quote" % urllib.parse.quote("make sure")
        result = urllib.request.pathname2url(given)
        self.assertEqual(expect, result,
                         "pathname2url() failed; %s != %s" %
                         (expect, result))
        given = "make+sure/using_unquote"
        expect = os.path.join("make+sure", "using_unquote")
        result = urllib.request.url2pathname(given)
        self.assertEqual(expect, result,
                         "url2pathname() failed; %s != %s" %
                         (expect, result))

    @unittest.skipUnless(sys.platform == 'win32',
                         'test specific to the urllib.url2path function.')
    def test_ntpath(self):
        given = ('/C:/', '///C:/', '/C|//')
        expect = 'C:\\'
        dla url w given:
            result = urllib.request.url2pathname(url)
            self.assertEqual(expect, result,
                             'urllib.request..url2pathname() failed; %s != %s' %
                             (expect, result))
        given = '///C|/path'
        expect = 'C:\\path'
        result = urllib.request.url2pathname(given)
        self.assertEqual(expect, result,
                         'urllib.request.url2pathname() failed; %s != %s' %
                         (expect, result))

klasa Utility_Tests(unittest.TestCase):
    """Testcase to test the various utility functions w the urllib."""

    def test_thishost(self):
        """Test the urllib.request.thishost utility function returns a tuple"""
        self.assertIsInstance(urllib.request.thishost(), tuple)


klasa URLopener_Tests(unittest.TestCase):
    """Testcase to test the open method of URLopener class."""

    def test_quoted_open(self):
        klasa DummyURLopener(urllib.request.URLopener):
            def open_spam(self, url):
                zwróć url
        przy support.check_warnings(
                ('DummyURLopener style of invoking requests jest deprecated.',
                DeprecationWarning)):
            self.assertEqual(DummyURLopener().open(
                'spam://example/ /'),'//example/%20/')

            # test the safe characters are nie quoted by urlopen
            self.assertEqual(DummyURLopener().open(
                "spam://c:|windows%/:=&?~#+!$,;'@()*[]|/path/"),
                "//c:|windows%/:=&?~#+!$,;'@()*[]|/path/")

# Just commented them out.
# Can't really tell why keep failing w windows oraz sparc.
# Everywhere inaczej they work ok, but on those machines, sometimes
# fail w one of the tests, sometimes w other. I have a linux, oraz
# the tests go ok.
# If anybody has one of the problematic environments, please help!
# .   Facundo
#
# def server(evt):
#     zaimportuj socket, time
#     serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     serv.settimeout(3)
#     serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     serv.bind(("", 9093))
#     serv.listen()
#     spróbuj:
#         conn, addr = serv.accept()
#         conn.send("1 Hola mundo\n")
#         cantdata = 0
#         dopóki cantdata < 13:
#             data = conn.recv(13-cantdata)
#             cantdata += len(data)
#             time.sleep(.3)
#         conn.send("2 No more lines\n")
#         conn.close()
#     wyjąwszy socket.timeout:
#         dalej
#     w_końcu:
#         serv.close()
#         evt.set()
#
# klasa FTPWrapperTests(unittest.TestCase):
#
#     def setUp(self):
#         zaimportuj ftplib, time, threading
#         ftplib.FTP.port = 9093
#         self.evt = threading.Event()
#         threading.Thread(target=server, args=(self.evt,)).start()
#         time.sleep(.1)
#
#     def tearDown(self):
#         self.evt.wait()
#
#     def testBasic(self):
#         # connects
#         ftp = urllib.ftpwrapper("myuser", "mypass", "localhost", 9093, [])
#         ftp.close()
#
#     def testTimeoutNic(self):
#         # global default timeout jest ignored
#         zaimportuj socket
#         self.assertIsNic(socket.getdefaulttimeout())
#         socket.setdefaulttimeout(30)
#         spróbuj:
#             ftp = urllib.ftpwrapper("myuser", "mypass", "localhost", 9093, [])
#         w_końcu:
#             socket.setdefaulttimeout(Nic)
#         self.assertEqual(ftp.ftp.sock.gettimeout(), 30)
#         ftp.close()
#
#     def testTimeoutDefault(self):
#         # global default timeout jest used
#         zaimportuj socket
#         self.assertIsNic(socket.getdefaulttimeout())
#         socket.setdefaulttimeout(30)
#         spróbuj:
#             ftp = urllib.ftpwrapper("myuser", "mypass", "localhost", 9093, [])
#         w_końcu:
#             socket.setdefaulttimeout(Nic)
#         self.assertEqual(ftp.ftp.sock.gettimeout(), 30)
#         ftp.close()
#
#     def testTimeoutValue(self):
#         ftp = urllib.ftpwrapper("myuser", "mypass", "localhost", 9093, [],
#                                 timeout=30)
#         self.assertEqual(ftp.ftp.sock.gettimeout(), 30)
#         ftp.close()


klasa RequestTests(unittest.TestCase):
    """Unit tests dla urllib.request.Request."""

    def test_default_values(self):
        Request = urllib.request.Request
        request = Request("http://www.python.org")
        self.assertEqual(request.get_method(), 'GET')
        request = Request("http://www.python.org", {})
        self.assertEqual(request.get_method(), 'POST')

    def test_with_method_arg(self):
        Request = urllib.request.Request
        request = Request("http://www.python.org", method='HEAD')
        self.assertEqual(request.method, 'HEAD')
        self.assertEqual(request.get_method(), 'HEAD')
        request = Request("http://www.python.org", {}, method='HEAD')
        self.assertEqual(request.method, 'HEAD')
        self.assertEqual(request.get_method(), 'HEAD')
        request = Request("http://www.python.org", method='GET')
        self.assertEqual(request.get_method(), 'GET')
        request.method = 'HEAD'
        self.assertEqual(request.get_method(), 'HEAD')


klasa URL2PathNameTests(unittest.TestCase):

    def test_converting_drive_letter(self):
        self.assertEqual(url2pathname("///C|"), 'C:')
        self.assertEqual(url2pathname("///C:"), 'C:')
        self.assertEqual(url2pathname("///C|/"), 'C:\\')

    def test_converting_when_no_drive_letter(self):
        # cannot end a raw string w \
        self.assertEqual(url2pathname("///C/test/"), r'\\\C\test' '\\')
        self.assertEqual(url2pathname("////C/test/"), r'\\C\test' '\\')

    def test_simple_compare(self):
        self.assertEqual(url2pathname("///C|/foo/bar/spam.foo"),
                         r'C:\foo\bar\spam.foo')

    def test_non_ascii_drive_letter(self):
        self.assertRaises(IOError, url2pathname, "///\u00e8|/")

    def test_roundtrip_url2pathname(self):
        list_of_paths = ['C:',
                         r'\\\C\test\\',
                         r'C:\foo\bar\spam.foo'
                         ]
        dla path w list_of_paths:
            self.assertEqual(url2pathname(pathname2url(path)), path)

klasa PathName2URLTests(unittest.TestCase):

    def test_converting_drive_letter(self):
        self.assertEqual(pathname2url("C:"), '///C:')
        self.assertEqual(pathname2url("C:\\"), '///C:')

    def test_converting_when_no_drive_letter(self):
        self.assertEqual(pathname2url(r"\\\folder\test" "\\"),
                         '/////folder/test/')
        self.assertEqual(pathname2url(r"\\folder\test" "\\"),
                         '////folder/test/')
        self.assertEqual(pathname2url(r"\folder\test" "\\"),
                         '/folder/test/')

    def test_simple_compare(self):
        self.assertEqual(pathname2url(r'C:\foo\bar\spam.foo'),
                         "///C:/foo/bar/spam.foo" )

    def test_long_drive_letter(self):
        self.assertRaises(IOError, pathname2url, "XX:\\")

    def test_roundtrip_pathname2url(self):
        list_of_paths = ['///C:',
                         '/////folder/test/',
                         '///C:/foo/bar/spam.foo']
        dla path w list_of_paths:
            self.assertEqual(pathname2url(url2pathname(path)), path)

jeżeli __name__ == '__main__':
    unittest.main()
