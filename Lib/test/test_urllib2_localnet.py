zaimportuj base64
zaimportuj os
zaimportuj email
zaimportuj urllib.parse
zaimportuj urllib.request
zaimportuj http.server
zaimportuj unittest
zaimportuj hashlib

z test zaimportuj support

threading = support.import_module('threading')

spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    ssl = Nic

here = os.path.dirname(__file__)
# Self-signed cert file dla 'localhost'
CERT_localhost = os.path.join(here, 'keycert.pem')
# Self-signed cert file dla 'fakehostname'
CERT_fakehostname = os.path.join(here, 'keycert2.pem')


# Loopback http server infrastructure

klasa LoopbackHttpServer(http.server.HTTPServer):
    """HTTP server w/ a few modifications that make it useful for
    loopback testing purposes.
    """

    def __init__(self, server_address, RequestHandlerClass):
        http.server.HTTPServer.__init__(self,
                                        server_address,
                                        RequestHandlerClass)

        # Set the timeout of our listening socket really low so
        # that we can stop the server easily.
        self.socket.settimeout(0.1)

    def get_request(self):
        """HTTPServer method, overridden."""

        request, client_address = self.socket.accept()

        # It's a loopback connection, so setting the timeout
        # really low shouldn't affect anything, but should make
        # deadlocks less likely to occur.
        request.settimeout(10.0)

        zwróć (request, client_address)

klasa LoopbackHttpServerThread(threading.Thread):
    """Stoppable thread that runs a loopback http server."""

    def __init__(self, request_handler):
        threading.Thread.__init__(self)
        self._stop_server = Nieprawda
        self.ready = threading.Event()
        request_handler.protocol_version = "HTTP/1.0"
        self.httpd = LoopbackHttpServer(("127.0.0.1", 0),
                                        request_handler)
        self.port = self.httpd.server_port

    def stop(self):
        """Stops the webserver jeżeli it's currently running."""

        self._stop_server = Prawda

        self.join()
        self.httpd.server_close()

    def run(self):
        self.ready.set()
        dopóki nie self._stop_server:
            self.httpd.handle_request()

# Authentication infrastructure

klasa DigestAuthHandler:
    """Handler dla performing digest authentication."""

    def __init__(self):
        self._request_num = 0
        self._nonces = []
        self._users = {}
        self._realm_name = "Test Realm"
        self._qop = "auth"

    def set_qop(self, qop):
        self._qop = qop

    def set_users(self, users):
        assert isinstance(users, dict)
        self._users = users

    def set_realm(self, realm):
        self._realm_name = realm

    def _generate_nonce(self):
        self._request_num += 1
        nonce = hashlib.md5(str(self._request_num).encode("ascii")).hexdigest()
        self._nonces.append(nonce)
        zwróć nonce

    def _create_auth_dict(self, auth_str):
        first_space_index = auth_str.find(" ")
        auth_str = auth_str[first_space_index+1:]

        parts = auth_str.split(",")

        auth_dict = {}
        dla part w parts:
            name, value = part.split("=")
            name = name.strip()
            jeżeli value[0] == '"' oraz value[-1] == '"':
                value = value[1:-1]
            inaczej:
                value = value.strip()
            auth_dict[name] = value
        zwróć auth_dict

    def _validate_auth(self, auth_dict, dalejword, method, uri):
        final_dict = {}
        final_dict.update(auth_dict)
        final_dict["password"] = dalejword
        final_dict["method"] = method
        final_dict["uri"] = uri
        HA1_str = "%(username)s:%(realm)s:%(password)s" % final_dict
        HA1 = hashlib.md5(HA1_str.encode("ascii")).hexdigest()
        HA2_str = "%(method)s:%(uri)s" % final_dict
        HA2 = hashlib.md5(HA2_str.encode("ascii")).hexdigest()
        final_dict["HA1"] = HA1
        final_dict["HA2"] = HA2
        response_str = "%(HA1)s:%(nonce)s:%(nc)s:" \
                       "%(cnonce)s:%(qop)s:%(HA2)s" % final_dict
        response = hashlib.md5(response_str.encode("ascii")).hexdigest()

        zwróć response == auth_dict["response"]

    def _return_auth_challenge(self, request_handler):
        request_handler.send_response(407, "Proxy Authentication Required")
        request_handler.send_header("Content-Type", "text/html")
        request_handler.send_header(
            'Proxy-Authenticate', 'Digest realm="%s", '
            'qop="%s",'
            'nonce="%s", ' % \
            (self._realm_name, self._qop, self._generate_nonce()))
        # XXX: Not sure jeżeli we're supposed to add this next header albo
        # not.
        #request_handler.send_header('Connection', 'close')
        request_handler.end_headers()
        request_handler.wfile.write(b"Proxy Authentication Required.")
        zwróć Nieprawda

    def handle_request(self, request_handler):
        """Performs digest authentication on the given HTTP request
        handler.  Returns Prawda jeżeli authentication was successful, Nieprawda
        otherwise.

        If no users have been set, then digest auth jest effectively
        disabled oraz this method will always zwróć Prawda.
        """

        jeżeli len(self._users) == 0:
            zwróć Prawda

        jeżeli "Proxy-Authorization" nie w request_handler.headers:
            zwróć self._return_auth_challenge(request_handler)
        inaczej:
            auth_dict = self._create_auth_dict(
                request_handler.headers["Proxy-Authorization"]
                )
            jeżeli auth_dict["username"] w self._users:
                dalejword = self._users[ auth_dict["username"] ]
            inaczej:
                zwróć self._return_auth_challenge(request_handler)
            jeżeli nie auth_dict.get("nonce") w self._nonces:
                zwróć self._return_auth_challenge(request_handler)
            inaczej:
                self._nonces.remove(auth_dict["nonce"])

            auth_validated = Nieprawda

            # MSIE uses short_path w its validation, but Python's
            # urllib.request uses the full path, so we're going to see if
            # either of them works here.

            dla path w [request_handler.path, request_handler.short_path]:
                jeżeli self._validate_auth(auth_dict,
                                       dalejword,
                                       request_handler.command,
                                       path):
                    auth_validated = Prawda

            jeżeli nie auth_validated:
                zwróć self._return_auth_challenge(request_handler)
            zwróć Prawda


klasa BasicAuthHandler(http.server.BaseHTTPRequestHandler):
    """Handler dla performing basic authentication."""
    # Server side values
    USER = 'testUser'
    PASSWD = 'testPass'
    REALM = 'Test'
    USER_PASSWD = "%s:%s" % (USER, PASSWD)
    ENCODED_AUTH = base64.b64encode(USER_PASSWD.encode('ascii')).decode('ascii')

    def __init__(self, *args, **kwargs):
        http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def log_message(self, format, *args):
        # Suppress console log message
        dalej

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic realm=\"%s\"" % self.REALM)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        jeżeli nie self.headers.get("Authorization", ""):
            self.do_AUTHHEAD()
            self.wfile.write(b"No Auth header received")
        albo_inaczej self.headers.get(
                "Authorization", "") == "Basic " + self.ENCODED_AUTH:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"It works")
        inaczej:
            # Request Unauthorized
            self.do_AUTHHEAD()



# Proxy test infrastructure

klasa FakeProxyHandler(http.server.BaseHTTPRequestHandler):
    """This jest a 'fake proxy' that makes it look like the entire
    internet has gone down due to a sudden zombie invasion.  It main
    utility jest w providing us przy authentication support for
    testing.
    """

    def __init__(self, digest_auth_handler, *args, **kwargs):
        # This has to be set before calling our parent's __init__(), which will
        # try to call do_GET().
        self.digest_auth_handler = digest_auth_handler
        http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def log_message(self, format, *args):
        # Uncomment the next line dla debugging.
        # sys.stderr.write(format % args)
        dalej

    def do_GET(self):
        (scm, netloc, path, params, query, fragment) = urllib.parse.urlparse(
            self.path, "http")
        self.short_path = path
        jeżeli self.digest_auth_handler.handle_request(self):
            self.send_response(200, "OK")
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("You've reached %s!<BR>" % self.path,
                                   "ascii"))
            self.wfile.write(b"Our apologies, but our server jest down due to "
                             b"a sudden zombie invasion.")

# Test cases

@unittest.skipUnless(threading, "Threading required dla this test.")
klasa BasicAuthTests(unittest.TestCase):
    USER = "testUser"
    PASSWD = "testPass"
    INCORRECT_PASSWD = "Incorrect"
    REALM = "Test"

    def setUp(self):
        super(BasicAuthTests, self).setUp()
        # With Basic Authentication
        def http_server_with_basic_auth_handler(*args, **kwargs):
            zwróć BasicAuthHandler(*args, **kwargs)
        self.server = LoopbackHttpServerThread(http_server_with_basic_auth_handler)
        self.server_url = 'http://127.0.0.1:%s' % self.server.port
        self.server.start()
        self.server.ready.wait()

    def tearDown(self):
        self.server.stop()
        super(BasicAuthTests, self).tearDown()

    def test_basic_auth_success(self):
        ah = urllib.request.HTTPBasicAuthHandler()
        ah.add_password(self.REALM, self.server_url, self.USER, self.PASSWD)
        urllib.request.install_opener(urllib.request.build_opener(ah))
        spróbuj:
            self.assertPrawda(urllib.request.urlopen(self.server_url))
        wyjąwszy urllib.error.HTTPError:
            self.fail("Basic auth failed dla the url: %s", self.server_url)

    def test_basic_auth_httperror(self):
        ah = urllib.request.HTTPBasicAuthHandler()
        ah.add_password(self.REALM, self.server_url, self.USER, self.INCORRECT_PASSWD)
        urllib.request.install_opener(urllib.request.build_opener(ah))
        self.assertRaises(urllib.error.HTTPError, urllib.request.urlopen, self.server_url)


@unittest.skipUnless(threading, "Threading required dla this test.")
klasa ProxyAuthTests(unittest.TestCase):
    URL = "http://localhost"

    USER = "tester"
    PASSWD = "test123"
    REALM = "TestRealm"

    def setUp(self):
        super(ProxyAuthTests, self).setUp()
        self.digest_auth_handler = DigestAuthHandler()
        self.digest_auth_handler.set_users({self.USER: self.PASSWD})
        self.digest_auth_handler.set_realm(self.REALM)
        # With Digest Authentication.
        def create_fake_proxy_handler(*args, **kwargs):
            zwróć FakeProxyHandler(self.digest_auth_handler, *args, **kwargs)

        self.server = LoopbackHttpServerThread(create_fake_proxy_handler)
        self.server.start()
        self.server.ready.wait()
        proxy_url = "http://127.0.0.1:%d" % self.server.port
        handler = urllib.request.ProxyHandler({"http" : proxy_url})
        self.proxy_digest_handler = urllib.request.ProxyDigestAuthHandler()
        self.opener = urllib.request.build_opener(
            handler, self.proxy_digest_handler)

    def tearDown(self):
        self.server.stop()
        super(ProxyAuthTests, self).tearDown()

    def test_proxy_with_bad_password_raises_httperror(self):
        self.proxy_digest_handler.add_password(self.REALM, self.URL,
                                               self.USER, self.PASSWD+"bad")
        self.digest_auth_handler.set_qop("auth")
        self.assertRaises(urllib.error.HTTPError,
                          self.opener.open,
                          self.URL)

    def test_proxy_with_no_password_raises_httperror(self):
        self.digest_auth_handler.set_qop("auth")
        self.assertRaises(urllib.error.HTTPError,
                          self.opener.open,
                          self.URL)

    def test_proxy_qop_auth_works(self):
        self.proxy_digest_handler.add_password(self.REALM, self.URL,
                                               self.USER, self.PASSWD)
        self.digest_auth_handler.set_qop("auth")
        result = self.opener.open(self.URL)
        dopóki result.read():
            dalej
        result.close()

    def test_proxy_qop_auth_int_works_or_throws_urlerror(self):
        self.proxy_digest_handler.add_password(self.REALM, self.URL,
                                               self.USER, self.PASSWD)
        self.digest_auth_handler.set_qop("auth-int")
        spróbuj:
            result = self.opener.open(self.URL)
        wyjąwszy urllib.error.URLError:
            # It's okay jeżeli we don't support auth-int, but we certainly
            # shouldn't receive any kind of exception here other than
            # a URLError.
            result = Nic
        jeżeli result:
            dopóki result.read():
                dalej
            result.close()


def GetRequestHandler(responses):

    klasa FakeHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

        server_version = "TestHTTP/"
        requests = []
        headers_received = []
        port = 80

        def do_GET(self):
            body = self.send_head()
            dopóki body:
                done = self.wfile.write(body)
                body = body[done:]

        def do_POST(self):
            content_length = self.headers["Content-Length"]
            post_data = self.rfile.read(int(content_length))
            self.do_GET()
            self.requests.append(post_data)

        def send_head(self):
            FakeHTTPRequestHandler.headers_received = self.headers
            self.requests.append(self.path)
            response_code, headers, body = responses.pop(0)

            self.send_response(response_code)

            dla (header, value) w headers:
                self.send_header(header, value % {'port':self.port})
            jeżeli body:
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                zwróć body
            self.end_headers()

        def log_message(self, *args):
            dalej


    zwróć FakeHTTPRequestHandler


@unittest.skipUnless(threading, "Threading required dla this test.")
klasa TestUrlopen(unittest.TestCase):
    """Tests urllib.request.urlopen using the network.

    These tests are nie exhaustive.  Assuming that testing using files does a
    good job overall of some of the basic interface features.  There are no
    tests exercising the optional 'data' oraz 'proxies' arguments.  No tests
    dla transparent redirection have been written.
    """

    def setUp(self):
        super(TestUrlopen, self).setUp()
        # Ignore proxies dla localhost tests.
        self.old_environ = os.environ.copy()
        os.environ['NO_PROXY'] = '*'
        self.server = Nic

    def tearDown(self):
        jeżeli self.server jest nie Nic:
            self.server.stop()
        os.environ.clear()
        os.environ.update(self.old_environ)
        super(TestUrlopen, self).tearDown()

    def urlopen(self, url, data=Nic, **kwargs):
        l = []
        f = urllib.request.urlopen(url, data, **kwargs)
        spróbuj:
            # Exercise various methods
            l.extend(f.readlines(200))
            l.append(f.readline())
            l.append(f.read(1024))
            l.append(f.read())
        w_końcu:
            f.close()
        zwróć b"".join(l)

    def start_server(self, responses=Nic):
        jeżeli responses jest Nic:
            responses = [(200, [], b"we don't care")]
        handler = GetRequestHandler(responses)

        self.server = LoopbackHttpServerThread(handler)
        self.server.start()
        self.server.ready.wait()
        port = self.server.port
        handler.port = port
        zwróć handler

    def start_https_server(self, responses=Nic, **kwargs):
        jeżeli nie hasattr(urllib.request, 'HTTPSHandler'):
            self.skipTest('ssl support required')
        z test.ssl_servers zaimportuj make_https_server
        jeżeli responses jest Nic:
            responses = [(200, [], b"we care a bit")]
        handler = GetRequestHandler(responses)
        server = make_https_server(self, handler_class=handler, **kwargs)
        handler.port = server.port
        zwróć handler

    def test_redirection(self):
        expected_response = b"We got here..."
        responses = [
            (302, [("Location", "http://localhost:%(port)s/somewhere_inaczej")],
             ""),
            (200, [], expected_response)
        ]

        handler = self.start_server(responses)
        data = self.urlopen("http://localhost:%s/" % handler.port)
        self.assertEqual(data, expected_response)
        self.assertEqual(handler.requests, ["/", "/somewhere_inaczej"])

    def test_chunked(self):
        expected_response = b"hello world"
        chunked_start = (
                        b'a\r\n'
                        b'hello worl\r\n'
                        b'1\r\n'
                        b'd\r\n'
                        b'0\r\n'
                        )
        response = [(200, [("Transfer-Encoding", "chunked")], chunked_start)]
        handler = self.start_server(response)
        data = self.urlopen("http://localhost:%s/" % handler.port)
        self.assertEqual(data, expected_response)

    def test_404(self):
        expected_response = b"Bad bad bad..."
        handler = self.start_server([(404, [], expected_response)])

        spróbuj:
            self.urlopen("http://localhost:%s/weeble" % handler.port)
        wyjąwszy urllib.error.URLError jako f:
            data = f.read()
            f.close()
        inaczej:
            self.fail("404 should podnieś URLError")

        self.assertEqual(data, expected_response)
        self.assertEqual(handler.requests, ["/weeble"])

    def test_200(self):
        expected_response = b"pycon 2008..."
        handler = self.start_server([(200, [], expected_response)])
        data = self.urlopen("http://localhost:%s/bizarre" % handler.port)
        self.assertEqual(data, expected_response)
        self.assertEqual(handler.requests, ["/bizarre"])

    def test_200_with_parameters(self):
        expected_response = b"pycon 2008..."
        handler = self.start_server([(200, [], expected_response)])
        data = self.urlopen("http://localhost:%s/bizarre" % handler.port,
                             b"get=with_feeling")
        self.assertEqual(data, expected_response)
        self.assertEqual(handler.requests, ["/bizarre", b"get=with_feeling"])

    def test_https(self):
        handler = self.start_https_server()
        context = ssl.create_default_context(cafile=CERT_localhost)
        data = self.urlopen("https://localhost:%s/bizarre" % handler.port, context=context)
        self.assertEqual(data, b"we care a bit")

    def test_https_with_cafile(self):
        handler = self.start_https_server(certfile=CERT_localhost)
        # Good cert
        data = self.urlopen("https://localhost:%s/bizarre" % handler.port,
                            cafile=CERT_localhost)
        self.assertEqual(data, b"we care a bit")
        # Bad cert
        przy self.assertRaises(urllib.error.URLError) jako cm:
            self.urlopen("https://localhost:%s/bizarre" % handler.port,
                         cafile=CERT_fakehostname)
        # Good cert, but mismatching hostname
        handler = self.start_https_server(certfile=CERT_fakehostname)
        przy self.assertRaises(ssl.CertificateError) jako cm:
            self.urlopen("https://localhost:%s/bizarre" % handler.port,
                         cafile=CERT_fakehostname)

    def test_https_with_cadefault(self):
        handler = self.start_https_server(certfile=CERT_localhost)
        # Self-signed cert should fail verification przy system certificate store
        przy self.assertRaises(urllib.error.URLError) jako cm:
            self.urlopen("https://localhost:%s/bizarre" % handler.port,
                         cadefault=Prawda)

    def test_https_sni(self):
        jeżeli ssl jest Nic:
            self.skipTest("ssl module required")
        jeżeli nie ssl.HAS_SNI:
            self.skipTest("SNI support required w OpenSSL")
        sni_name = Nic
        def cb_sni(ssl_sock, server_name, initial_context):
            nonlocal sni_name
            sni_name = server_name
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.set_servername_callback(cb_sni)
        handler = self.start_https_server(context=context, certfile=CERT_localhost)
        context = ssl.create_default_context(cafile=CERT_localhost)
        self.urlopen("https://localhost:%s" % handler.port, context=context)
        self.assertEqual(sni_name, "localhost")

    def test_sending_headers(self):
        handler = self.start_server()
        req = urllib.request.Request("http://localhost:%s/" % handler.port,
                                     headers={"Range": "bytes=20-39"})
        urllib.request.urlopen(req)
        self.assertEqual(handler.headers_received["Range"], "bytes=20-39")

    def test_basic(self):
        handler = self.start_server()
        open_url = urllib.request.urlopen("http://localhost:%s" % handler.port)
        dla attr w ("read", "close", "info", "geturl"):
            self.assertPrawda(hasattr(open_url, attr), "object returned z "
                         "urlopen lacks the %s attribute" % attr)
        spróbuj:
            self.assertPrawda(open_url.read(), "calling 'read' failed")
        w_końcu:
            open_url.close()

    def test_info(self):
        handler = self.start_server()
        spróbuj:
            open_url = urllib.request.urlopen(
                "http://localhost:%s" % handler.port)
            info_obj = open_url.info()
            self.assertIsInstance(info_obj, email.message.Message,
                                  "object returned by 'info' jest nie an "
                                  "instance of email.message.Message")
            self.assertEqual(info_obj.get_content_subtype(), "plain")
        w_końcu:
            self.server.stop()

    def test_geturl(self):
        # Make sure same URL jako opened jest returned by geturl.
        handler = self.start_server()
        open_url = urllib.request.urlopen("http://localhost:%s" % handler.port)
        url = open_url.geturl()
        self.assertEqual(url, "http://localhost:%s" % handler.port)

    def test_bad_address(self):
        # Make sure proper exception jest podnieśd when connecting to a bogus
        # address.

        # jako indicated by the comment below, this might fail przy some ISP,
        # so we run the test only when -unetwork/-uall jest specified to
        # mitigate the problem a bit (see #17564)
        support.requires('network')
        self.assertRaises(OSError,
                          # Given that both VeriSign oraz various ISPs have w
                          # the past albo are presently hijacking various invalid
                          # domain name requests w an attempt to boost traffic
                          # to their own sites, finding a domain name to use
                          # dla this test jest difficult.  RFC2606 leads one to
                          # believe that '.invalid' should work, but experience
                          # seemed to indicate otherwise.  Single character
                          # TLDs are likely to remain invalid, so this seems to
                          # be the best choice. The trailing '.' prevents a
                          # related problem: The normal DNS resolver appends
                          # the domain names z the search path jeżeli there jest
                          # no '.' the end and, oraz jeżeli one of those domains
                          # implements a '*' rule a result jest returned.
                          # However, none of this will prevent the test from
                          # failing jeżeli the ISP hijacks all invalid domain
                          # requests.  The real solution would be to be able to
                          # parameterize the framework przy a mock resolver.
                          urllib.request.urlopen,
                          "http://sadflkjsasf.i.nvali.d./")

    def test_iteration(self):
        expected_response = b"pycon 2008..."
        handler = self.start_server([(200, [], expected_response)])
        data = urllib.request.urlopen("http://localhost:%s" % handler.port)
        dla line w data:
            self.assertEqual(line, expected_response)

    def test_line_iteration(self):
        lines = [b"We\n", b"got\n", b"here\n", b"verylong " * 8192 + b"\n"]
        expected_response = b"".join(lines)
        handler = self.start_server([(200, [], expected_response)])
        data = urllib.request.urlopen("http://localhost:%s" % handler.port)
        dla index, line w enumerate(data):
            self.assertEqual(line, lines[index],
                             "Fetched line number %s doesn't match expected:\n"
                             "    Expected length was %s, got %s" %
                             (index, len(lines[index]), len(line)))
        self.assertEqual(index + 1, len(lines))


threads_key = Nic

def setUpModule():
    # Store the threading_setup w a key oraz ensure that it jest cleaned up
    # w the tearDown
    global threads_key
    threads_key = support.threading_setup()

def tearDownModule():
    jeżeli threads_key:
        support.threading_cleanup(threads_key)

jeżeli __name__ == "__main__":
    unittest.main()
