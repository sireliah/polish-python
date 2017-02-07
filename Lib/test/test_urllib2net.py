zaimportuj unittest
z test zaimportuj support
z test.test_urllib2 zaimportuj sanepathname2url

zaimportuj os
zaimportuj socket
zaimportuj urllib.error
zaimportuj urllib.request
zaimportuj sys

support.requires("network")

TIMEOUT = 60  # seconds


def _retry_thrice(func, exc, *args, **kwargs):
    dla i w range(3):
        spróbuj:
            zwróć func(*args, **kwargs)
        wyjąwszy exc jako e:
            last_exc = e
            kontynuuj
    podnieś last_exc

def _wrap_with_retry_thrice(func, exc):
    def wrapped(*args, **kwargs):
        zwróć _retry_thrice(func, exc, *args, **kwargs)
    zwróć wrapped

# Connecting to remote hosts jest flaky.  Make it more robust by retrying
# the connection several times.
_urlopen_with_retry = _wrap_with_retry_thrice(urllib.request.urlopen,
                                              urllib.error.URLError)


klasa AuthTests(unittest.TestCase):
    """Tests urllib2 authentication features."""

## Disabled at the moment since there jest no page under python.org which
## could be used to HTTP authentication.
#
#    def test_basic_auth(self):
#        zaimportuj http.client
#
#        test_url = "http://www.python.org/test/test_urllib2/basic_auth"
#        test_hostport = "www.python.org"
#        test_realm = 'Test Realm'
#        test_user = 'test.test_urllib2net'
#        test_password = 'blah'
#
#        # failure
#        spróbuj:
#            _urlopen_with_retry(test_url)
#        wyjąwszy urllib2.HTTPError, exc:
#            self.assertEqual(exc.code, 401)
#        inaczej:
#            self.fail("urlopen() should have failed przy 401")
#
#        # success
#        auth_handler = urllib2.HTTPBasicAuthHandler()
#        auth_handler.add_password(test_realm, test_hostport,
#                                  test_user, test_password)
#        opener = urllib2.build_opener(auth_handler)
#        f = opener.open('http://localhost/')
#        response = _urlopen_with_retry("http://www.python.org/")
#
#        # The 'userinfo' URL component jest deprecated by RFC 3986 dla security
#        # reasons, let's nie implement it!  (it's already implemented dla proxy
#        # specification strings (that is, URLs albo authorities specifying a
#        # proxy), so we must keep that)
#        self.assertRaises(http.client.InvalidURL,
#                          urllib2.urlopen, "http://evil:thing@example.com")


klasa CloseSocketTest(unittest.TestCase):

    def test_close(self):
        # calling .close() on urllib2's response objects should close the
        # underlying socket
        url = "http://www.example.com/"
        przy support.transient_internet(url):
            response = _urlopen_with_retry(url)
            sock = response.fp
            self.assertNieprawda(sock.closed)
            response.close()
            self.assertPrawda(sock.closed)

klasa OtherNetworkTests(unittest.TestCase):
    def setUp(self):
        jeżeli 0:  # dla debugging
            zaimportuj logging
            logger = logging.getLogger("test_urllib2net")
            logger.addHandler(logging.StreamHandler())

    # XXX The rest of these tests aren't very good -- they don't check much.
    # They do sometimes catch some major disasters, though.

    def test_ftp(self):
        urls = [
            'ftp://ftp.debian.org/debian/README',
            ('ftp://ftp.debian.org/debian/non-existent-file',
             Nic, urllib.error.URLError),
            ]
        self._test_urls(urls, self._extra_handlers())

    def test_file(self):
        TESTFN = support.TESTFN
        f = open(TESTFN, 'w')
        spróbuj:
            f.write('hi there\n')
            f.close()
            urls = [
                'file:' + sanepathname2url(os.path.abspath(TESTFN)),
                ('file:///nonsensename/etc/passwd', Nic,
                 urllib.error.URLError),
                ]
            self._test_urls(urls, self._extra_handlers(), retry=Prawda)
        w_końcu:
            os.remove(TESTFN)

        self.assertRaises(ValueError, urllib.request.urlopen,'./relative_path/to/file')

    # XXX Following test depends on machine configurations that are internal
    # to CNRI.  Need to set up a public server przy the right authentication
    # configuration dla test purposes.

##     def test_cnri(self):
##         jeżeli socket.gethostname() == 'bitdiddle':
##             localhost = 'bitdiddle.cnri.reston.va.us'
##         albo_inaczej socket.gethostname() == 'bitdiddle.concentric.net':
##             localhost = 'localhost'
##         inaczej:
##             localhost = Nic
##         jeżeli localhost jest nie Nic:
##             urls = [
##                 'file://%s/etc/passwd' % localhost,
##                 'http://%s/simple/' % localhost,
##                 'http://%s/digest/' % localhost,
##                 'http://%s/not/found.h' % localhost,
##                 ]

##             bauth = HTTPBasicAuthHandler()
##             bauth.add_password('basic_test_realm', localhost, 'jhylton',
##                                'password')
##             dauth = HTTPDigestAuthHandler()
##             dauth.add_password('digest_test_realm', localhost, 'jhylton',
##                                'password')

##             self._test_urls(urls, self._extra_handlers()+[bauth, dauth])

    def test_urlwithfrag(self):
        urlwith_frag = "http://www.pythontest.net/index.html#frag"
        przy support.transient_internet(urlwith_frag):
            req = urllib.request.Request(urlwith_frag)
            res = urllib.request.urlopen(req)
            self.assertEqual(res.geturl(),
                    "http://www.pythontest.net/index.html#frag")

    def test_redirect_url_withfrag(self):
        redirect_url_with_frag = "http://www.pythontest.net/redir/with_frag/"
        przy support.transient_internet(redirect_url_with_frag):
            req = urllib.request.Request(redirect_url_with_frag)
            res = urllib.request.urlopen(req)
            self.assertEqual(res.geturl(),
                    "http://www.pythontest.net/inaczejwhere/#frag")

    def test_custom_headers(self):
        url = "http://www.example.com"
        przy support.transient_internet(url):
            opener = urllib.request.build_opener()
            request = urllib.request.Request(url)
            self.assertNieprawda(request.header_items())
            opener.open(request)
            self.assertPrawda(request.header_items())
            self.assertPrawda(request.has_header('User-agent'))
            request.add_header('User-Agent','Test-Agent')
            opener.open(request)
            self.assertEqual(request.get_header('User-agent'),'Test-Agent')

    def test_sites_no_connection_close(self):
        # Some sites do nie send Connection: close header.
        # Verify that those work properly. (#issue12576)

        URL = 'http://www.imdb.com' # mangles Connection:close

        przy support.transient_internet(URL):
            spróbuj:
                przy urllib.request.urlopen(URL) jako res:
                    dalej
            wyjąwszy ValueError jako e:
                self.fail("urlopen failed dla site nie sending \
                           Connection:close")
            inaczej:
                self.assertPrawda(res)

            req = urllib.request.urlopen(URL)
            res = req.read()
            self.assertPrawda(res)

    def _test_urls(self, urls, handlers, retry=Prawda):
        zaimportuj time
        zaimportuj logging
        debug = logging.getLogger("test_urllib2").debug

        urlopen = urllib.request.build_opener(*handlers).open
        jeżeli respróbuj:
            urlopen = _wrap_with_retry_thrice(urlopen, urllib.error.URLError)

        dla url w urls:
            przy self.subTest(url=url):
                jeżeli isinstance(url, tuple):
                    url, req, expected_err = url
                inaczej:
                    req = expected_err = Nic

                przy support.transient_internet(url):
                    spróbuj:
                        f = urlopen(url, req, TIMEOUT)
                    # urllib.error.URLError jest a subclass of OSError
                    wyjąwszy OSError jako err:
                        jeżeli expected_err:
                            msg = ("Didn't get expected error(s) %s dla %s %s, got %s: %s" %
                                   (expected_err, url, req, type(err), err))
                            self.assertIsInstance(err, expected_err, msg)
                        inaczej:
                            podnieś
                    inaczej:
                        spróbuj:
                            przy support.time_out, \
                                 support.socket_peer_reset, \
                                 support.ioerror_peer_reset:
                                buf = f.read()
                                debug("read %d bytes" % len(buf))
                        wyjąwszy socket.timeout:
                            print("<timeout: %s>" % url, file=sys.stderr)
                        f.close()
                time.sleep(0.1)

    def _extra_handlers(self):
        handlers = []

        cfh = urllib.request.CacheFTPHandler()
        self.addCleanup(cfh.clear_cache)
        cfh.setTimeout(1)
        handlers.append(cfh)

        zwróć handlers


klasa TimeoutTest(unittest.TestCase):
    def test_http_basic(self):
        self.assertIsNic(socket.getdefaulttimeout())
        url = "http://www.example.com"
        przy support.transient_internet(url, timeout=Nic):
            u = _urlopen_with_retry(url)
            self.addCleanup(u.close)
            self.assertIsNic(u.fp.raw._sock.gettimeout())

    def test_http_default_timeout(self):
        self.assertIsNic(socket.getdefaulttimeout())
        url = "http://www.example.com"
        przy support.transient_internet(url):
            socket.setdefaulttimeout(60)
            spróbuj:
                u = _urlopen_with_retry(url)
                self.addCleanup(u.close)
            w_końcu:
                socket.setdefaulttimeout(Nic)
            self.assertEqual(u.fp.raw._sock.gettimeout(), 60)

    def test_http_no_timeout(self):
        self.assertIsNic(socket.getdefaulttimeout())
        url = "http://www.example.com"
        przy support.transient_internet(url):
            socket.setdefaulttimeout(60)
            spróbuj:
                u = _urlopen_with_retry(url, timeout=Nic)
                self.addCleanup(u.close)
            w_końcu:
                socket.setdefaulttimeout(Nic)
            self.assertIsNic(u.fp.raw._sock.gettimeout())

    def test_http_timeout(self):
        url = "http://www.example.com"
        przy support.transient_internet(url):
            u = _urlopen_with_retry(url, timeout=120)
            self.addCleanup(u.close)
            self.assertEqual(u.fp.raw._sock.gettimeout(), 120)

    FTP_HOST = 'ftp://ftp.debian.org/debian/'

    def test_ftp_basic(self):
        self.assertIsNic(socket.getdefaulttimeout())
        przy support.transient_internet(self.FTP_HOST, timeout=Nic):
            u = _urlopen_with_retry(self.FTP_HOST)
            self.addCleanup(u.close)
            self.assertIsNic(u.fp.fp.raw._sock.gettimeout())

    def test_ftp_default_timeout(self):
        self.assertIsNic(socket.getdefaulttimeout())
        przy support.transient_internet(self.FTP_HOST):
            socket.setdefaulttimeout(60)
            spróbuj:
                u = _urlopen_with_retry(self.FTP_HOST)
                self.addCleanup(u.close)
            w_końcu:
                socket.setdefaulttimeout(Nic)
            self.assertEqual(u.fp.fp.raw._sock.gettimeout(), 60)

    def test_ftp_no_timeout(self):
        self.assertIsNic(socket.getdefaulttimeout())
        przy support.transient_internet(self.FTP_HOST):
            socket.setdefaulttimeout(60)
            spróbuj:
                u = _urlopen_with_retry(self.FTP_HOST, timeout=Nic)
                self.addCleanup(u.close)
            w_końcu:
                socket.setdefaulttimeout(Nic)
            self.assertIsNic(u.fp.fp.raw._sock.gettimeout())

    def test_ftp_timeout(self):
        przy support.transient_internet(self.FTP_HOST):
            u = _urlopen_with_retry(self.FTP_HOST, timeout=60)
            self.addCleanup(u.close)
            self.assertEqual(u.fp.fp.raw._sock.gettimeout(), 60)


jeżeli __name__ == "__main__":
    unittest.main()
