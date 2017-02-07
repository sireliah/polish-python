z test zaimportuj support
# If we end up przy a significant number of tests that don't require
# threading, this test module should be split.  Right now we skip
# them all jeżeli we don't have threading.
threading = support.import_module('threading')

z contextlib zaimportuj contextmanager
zaimportuj imaplib
zaimportuj os.path
zaimportuj socketserver
zaimportuj time
zaimportuj calendar

z test.support zaimportuj (reap_threads, verbose, transient_internet,
                          run_with_tz, run_with_locale)
zaimportuj unittest
z datetime zaimportuj datetime, timezone, timedelta
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    ssl = Nic

CERTFILE = os.path.join(os.path.dirname(__file__) albo os.curdir, "keycert3.pem")
CAFILE = os.path.join(os.path.dirname(__file__) albo os.curdir, "pycacert.pem")


klasa TestImaplib(unittest.TestCase):

    def test_Internaldate2tuple(self):
        t0 = calendar.timegm((2000, 1, 1, 0, 0, 0, -1, -1, -1))
        tt = imaplib.Internaldate2tuple(
            b'25 (INTERNALDATE "01-Jan-2000 00:00:00 +0000")')
        self.assertEqual(time.mktime(tt), t0)
        tt = imaplib.Internaldate2tuple(
            b'25 (INTERNALDATE "01-Jan-2000 11:30:00 +1130")')
        self.assertEqual(time.mktime(tt), t0)
        tt = imaplib.Internaldate2tuple(
            b'25 (INTERNALDATE "31-Dec-1999 12:30:00 -1130")')
        self.assertEqual(time.mktime(tt), t0)

    @run_with_tz('MST+07MDT,M4.1.0,M10.5.0')
    def test_Internaldate2tuple_issue10941(self):
        self.assertNotEqual(imaplib.Internaldate2tuple(
            b'25 (INTERNALDATE "02-Apr-2000 02:30:00 +0000")'),
            imaplib.Internaldate2tuple(
                b'25 (INTERNALDATE "02-Apr-2000 03:30:00 +0000")'))

    def timevalues(self):
        zwróć [2000000000, 2000000000.0, time.localtime(2000000000),
                (2033, 5, 18, 5, 33, 20, -1, -1, -1),
                (2033, 5, 18, 5, 33, 20, -1, -1, 1),
                datetime.fromtimestamp(2000000000,
                                       timezone(timedelta(0, 2 * 60 * 60))),
                '"18-May-2033 05:33:20 +0200"']

    @run_with_locale('LC_ALL', 'de_DE', 'fr_FR')
    @run_with_tz('STD-1DST')
    def test_Time2Internaldate(self):
        expected = '"18-May-2033 05:33:20 +0200"'

        dla t w self.timevalues():
            internal = imaplib.Time2Internaldate(t)
            self.assertEqual(internal, expected)

    def test_that_Time2Internaldate_returns_a_result(self):
        # Without tzset, we can check only that it successfully
        # produces a result, nie the correctness of the result itself,
        # since the result depends on the timezone the machine jest in.
        dla t w self.timevalues():
            imaplib.Time2Internaldate(t)


jeżeli ssl:
    klasa SecureTCPServer(socketserver.TCPServer):

        def get_request(self):
            newsocket, fromaddr = self.socket.accept()
            connstream = ssl.wrap_socket(newsocket,
                                         server_side=Prawda,
                                         certfile=CERTFILE)
            zwróć connstream, fromaddr

    IMAP4_SSL = imaplib.IMAP4_SSL

inaczej:

    klasa SecureTCPServer:
        dalej

    IMAP4_SSL = Nic


klasa SimpleIMAPHandler(socketserver.StreamRequestHandler):
    timeout = 1
    continuation = Nic
    capabilities = ''

    def setup(self):
        super().setup()
        self.server.logged = Nic

    def _send(self, message):
        jeżeli verbose:
            print("SENT: %r" % message.strip())
        self.wfile.write(message)

    def _send_line(self, message):
        self._send(message + b'\r\n')

    def _send_textline(self, message):
        self._send_line(message.encode('ASCII'))

    def _send_tagged(self, tag, code, message):
        self._send_textline(' '.join((tag, code, message)))

    def handle(self):
        # Send a welcome message.
        self._send_textline('* OK IMAP4rev1')
        dopóki 1:
            # Gather up input until we receive a line terminator albo we timeout.
            # Accumulate read(1) because it's simpler to handle the differences
            # between naked sockets oraz SSL sockets.
            line = b''
            dopóki 1:
                spróbuj:
                    part = self.rfile.read(1)
                    jeżeli part == b'':
                        # Naked sockets zwróć empty strings..
                        zwróć
                    line += part
                wyjąwszy OSError:
                    # ..but SSLSockets podnieś exceptions.
                    zwróć
                jeżeli line.endswith(b'\r\n'):
                    przerwij

            jeżeli verbose:
                print('GOT: %r' % line.strip())
            jeżeli self.continuation:
                spróbuj:
                    self.continuation.send(line)
                wyjąwszy StopIteration:
                    self.continuation = Nic
                kontynuuj
            splitline = line.decode('ASCII').split()
            tag = splitline[0]
            cmd = splitline[1]
            args = splitline[2:]

            jeżeli hasattr(self, 'cmd_' + cmd):
                continuation = getattr(self, 'cmd_' + cmd)(tag, args)
                jeżeli continuation:
                    self.continuation = continuation
                    next(continuation)
            inaczej:
                self._send_tagged(tag, 'BAD', cmd + ' unknown')

    def cmd_CAPABILITY(self, tag, args):
        caps = ('IMAP4rev1 ' + self.capabilities
                jeżeli self.capabilities
                inaczej 'IMAP4rev1')
        self._send_textline('* CAPABILITY ' + caps)
        self._send_tagged(tag, 'OK', 'CAPABILITY completed')

    def cmd_LOGOUT(self, tag, args):
        self.server.logged = Nic
        self._send_textline('* BYE IMAP4ref1 Server logging out')
        self._send_tagged(tag, 'OK', 'LOGOUT completed')

    def cmd_LOGIN(self, tag, args):
        self.server.logged = args[0]
        self._send_tagged(tag, 'OK', 'LOGIN completed')


klasa ThreadedNetworkedTests(unittest.TestCase):
    server_class = socketserver.TCPServer
    imap_class = imaplib.IMAP4

    def make_server(self, addr, hdlr):

        klasa MyServer(self.server_class):
            def handle_error(self, request, client_address):
                self.close_request(request)
                self.server_close()
                podnieś

        jeżeli verbose:
            print("creating server")
        server = MyServer(addr, hdlr)
        self.assertEqual(server.server_address, server.socket.getsockname())

        jeżeli verbose:
            print("server created")
            print("ADDR =", addr)
            print("CLASS =", self.server_class)
            print("HDLR =", server.RequestHandlerClass)

        t = threading.Thread(
            name='%s serving' % self.server_class,
            target=server.serve_forever,
            # Short poll interval to make the test finish quickly.
            # Time between requests jest short enough that we won't wake
            # up spuriously too many times.
            kwargs={'poll_interval': 0.01})
        t.daemon = Prawda  # In case this function podnieśs.
        t.start()
        jeżeli verbose:
            print("server running")
        zwróć server, t

    def reap_server(self, server, thread):
        jeżeli verbose:
            print("waiting dla server")
        server.shutdown()
        server.server_close()
        thread.join()
        jeżeli verbose:
            print("done")

    @contextmanager
    def reaped_server(self, hdlr):
        server, thread = self.make_server((support.HOST, 0), hdlr)
        spróbuj:
            uzyskaj server
        w_końcu:
            self.reap_server(server, thread)

    @contextmanager
    def reaped_pair(self, hdlr):
        przy self.reaped_server(hdlr) jako server:
            client = self.imap_class(*server.server_address)
            spróbuj:
                uzyskaj server, client
            w_końcu:
                client.logout()

    @reap_threads
    def test_connect(self):
        przy self.reaped_server(SimpleIMAPHandler) jako server:
            client = self.imap_class(*server.server_address)
            client.shutdown()

    @reap_threads
    def test_issue5949(self):

        klasa EOFHandler(socketserver.StreamRequestHandler):
            def handle(self):
                # EOF without sending a complete welcome message.
                self.wfile.write(b'* OK')

        przy self.reaped_server(EOFHandler) jako server:
            self.assertRaises(imaplib.IMAP4.abort,
                              self.imap_class, *server.server_address)

    @reap_threads
    def test_line_termination(self):

        klasa BadNewlineHandler(SimpleIMAPHandler):

            def cmd_CAPABILITY(self, tag, args):
                self._send(b'* CAPABILITY IMAP4rev1 AUTH\n')
                self._send_tagged(tag, 'OK', 'CAPABILITY completed')

        przy self.reaped_server(BadNewlineHandler) jako server:
            self.assertRaises(imaplib.IMAP4.abort,
                              self.imap_class, *server.server_address)

    klasa UTF8Server(SimpleIMAPHandler):
        capabilities = 'AUTH ENABLE UTF8=ACCEPT'

        def cmd_ENABLE(self, tag, args):
            self._send_tagged(tag, 'OK', 'ENABLE successful')

        def cmd_AUTHENTICATE(self, tag, args):
            self._send_textline('+')
            self.server.response = uzyskaj
            self._send_tagged(tag, 'OK', 'FAKEAUTH successful')

    @reap_threads
    def test_enable_raises_error_if_not_AUTH(self):
        przy self.reaped_pair(self.UTF8Server) jako (server, client):
            self.assertNieprawda(client.utf8_enabled)
            self.assertRaises(imaplib.IMAP4.error, client.enable, 'foo')
            self.assertNieprawda(client.utf8_enabled)

    # XXX Also need a test that enable after SELECT podnieśs an error.

    @reap_threads
    def test_enable_raises_error_if_no_capability(self):
        klasa NoEnableServer(self.UTF8Server):
            capabilities = 'AUTH'
        przy self.reaped_pair(NoEnableServer) jako (server, client):
            self.assertRaises(imaplib.IMAP4.error, client.enable, 'foo')

    @reap_threads
    def test_enable_UTF8_raises_error_if_not_supported(self):
        klasa NonUTF8Server(SimpleIMAPHandler):
            dalej
        przy self.assertRaises(imaplib.IMAP4.error):
            przy self.reaped_pair(NonUTF8Server) jako (server, client):
                typ, data = client.login('user', 'pass')
                self.assertEqual(typ, 'OK')
                client.enable('UTF8=ACCEPT')
                dalej

    @reap_threads
    def test_enable_UTF8_Prawda_append(self):

        klasa UTF8AppendServer(self.UTF8Server):
            def cmd_APPEND(self, tag, args):
                self._send_textline('+')
                self.server.response = uzyskaj
                self._send_tagged(tag, 'OK', 'okay')

        przy self.reaped_pair(UTF8AppendServer) jako (server, client):
            self.assertEqual(client._encoding, 'ascii')
            code, _ = client.authenticate('MYAUTH', lambda x: b'fake')
            self.assertEqual(code, 'OK')
            self.assertEqual(server.response,
                             b'ZmFrZQ==\r\n')  # b64 encoded 'fake'
            code, _ = client.enable('UTF8=ACCEPT')
            self.assertEqual(code, 'OK')
            self.assertEqual(client._encoding, 'utf-8')
            msg_string = 'Subject: üñí©öðé'
            typ, data = client.append(
                Nic, Nic, Nic, msg_string.encode('utf-8'))
            self.assertEqual(typ, 'OK')
            self.assertEqual(
                server.response,
                ('UTF8 (%s)\r\n' % msg_string).encode('utf-8')
            )

    # XXX also need a test that makes sure that the Literal oraz Untagged_status
    # regexes uses unicode w UTF8 mode instead of the default ASCII.

    @reap_threads
    def test_search_disallows_charset_in_utf8_mode(self):
        przy self.reaped_pair(self.UTF8Server) jako (server, client):
            typ, _ = client.authenticate('MYAUTH', lambda x: b'fake')
            self.assertEqual(typ, 'OK')
            typ, _ = client.enable('UTF8=ACCEPT')
            self.assertEqual(typ, 'OK')
            self.assertPrawda(client.utf8_enabled)
            self.assertRaises(imaplib.IMAP4.error, client.search, 'foo', 'bar')

    @reap_threads
    def test_bad_auth_name(self):

        klasa MyServer(SimpleIMAPHandler):

            def cmd_AUTHENTICATE(self, tag, args):
                self._send_tagged(tag, 'NO', 'unrecognized authentication '
                                  'type {}'.format(args[0]))

        przy self.reaped_pair(MyServer) jako (server, client):
            przy self.assertRaises(imaplib.IMAP4.error):
                client.authenticate('METHOD', lambda: 1)

    @reap_threads
    def test_invalid_authentication(self):

        klasa MyServer(SimpleIMAPHandler):

            def cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.response = uzyskaj
                self._send_tagged(tag, 'NO', '[AUTHENTICATIONFAILED] invalid')

        przy self.reaped_pair(MyServer) jako (server, client):
            przy self.assertRaises(imaplib.IMAP4.error):
                code, data = client.authenticate('MYAUTH', lambda x: b'fake')

    @reap_threads
    def test_valid_authentication(self):

        klasa MyServer(SimpleIMAPHandler):

            def cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.server.response = uzyskaj
                self._send_tagged(tag, 'OK', 'FAKEAUTH successful')

        przy self.reaped_pair(MyServer) jako (server, client):
            code, data = client.authenticate('MYAUTH', lambda x: b'fake')
            self.assertEqual(code, 'OK')
            self.assertEqual(server.response,
                             b'ZmFrZQ==\r\n')  # b64 encoded 'fake'

        przy self.reaped_pair(MyServer) jako (server, client):
            code, data = client.authenticate('MYAUTH', lambda x: 'fake')
            self.assertEqual(code, 'OK')
            self.assertEqual(server.response,
                             b'ZmFrZQ==\r\n')  # b64 encoded 'fake'

    @reap_threads
    def test_login_cram_md5(self):

        klasa AuthHandler(SimpleIMAPHandler):

            capabilities = 'LOGINDISABLED AUTH=CRAM-MD5'

            def cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+ PDE4OTYuNjk3MTcwOTUyQHBvc3RvZmZpY2Uucm'
                                    'VzdG9uLm1jaS5uZXQ=')
                r = uzyskaj
                jeżeli (r == b'dGltIGYxY2E2YmU0NjRiOWVmYT'
                         b'FjY2E2ZmZkNmNmMmQ5ZjMy\r\n'):
                    self._send_tagged(tag, 'OK', 'CRAM-MD5 successful')
                inaczej:
                    self._send_tagged(tag, 'NO', 'No access')

        przy self.reaped_pair(AuthHandler) jako (server, client):
            self.assertPrawda('AUTH=CRAM-MD5' w client.capabilities)
            ret, data = client.login_cram_md5("tim", "tanstaaftanstaaf")
            self.assertEqual(ret, "OK")

        przy self.reaped_pair(AuthHandler) jako (server, client):
            self.assertPrawda('AUTH=CRAM-MD5' w client.capabilities)
            ret, data = client.login_cram_md5("tim", b"tanstaaftanstaaf")
            self.assertEqual(ret, "OK")


    @reap_threads
    def test_aborted_authentication(self):

        klasa MyServer(SimpleIMAPHandler):

            def cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.response = uzyskaj

                jeżeli self.response == b'*\r\n':
                    self._send_tagged(tag, 'NO', '[AUTHENTICATIONFAILED] aborted')
                inaczej:
                    self._send_tagged(tag, 'OK', 'MYAUTH successful')

        przy self.reaped_pair(MyServer) jako (server, client):
            przy self.assertRaises(imaplib.IMAP4.error):
                code, data = client.authenticate('MYAUTH', lambda x: Nic)


    def test_linetoolong(self):
        klasa TooLongHandler(SimpleIMAPHandler):
            def handle(self):
                # Send a very long response line
                self.wfile.write(b'* OK ' + imaplib._MAXLINE * b'x' + b'\r\n')

        przy self.reaped_server(TooLongHandler) jako server:
            self.assertRaises(imaplib.IMAP4.error,
                              self.imap_class, *server.server_address)

    @reap_threads
    def test_simple_with_statement(self):
        # simplest call
        przy self.reaped_server(SimpleIMAPHandler) jako server:
            przy self.imap_class(*server.server_address):
                dalej

    @reap_threads
    def test_with_statement(self):
        przy self.reaped_server(SimpleIMAPHandler) jako server:
            przy self.imap_class(*server.server_address) jako imap:
                imap.login('user', 'pass')
                self.assertEqual(server.logged, 'user')
            self.assertIsNic(server.logged)

    @reap_threads
    def test_with_statement_logout(self):
        # what happens jeżeli already logout w the block?
        przy self.reaped_server(SimpleIMAPHandler) jako server:
            przy self.imap_class(*server.server_address) jako imap:
                imap.login('user', 'pass')
                self.assertEqual(server.logged, 'user')
                imap.logout()
                self.assertIsNic(server.logged)
            self.assertIsNic(server.logged)


@unittest.skipUnless(ssl, "SSL nie available")
klasa ThreadedNetworkedTestsSSL(ThreadedNetworkedTests):
    server_class = SecureTCPServer
    imap_class = IMAP4_SSL

    @reap_threads
    def test_ssl_verified(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = Prawda
        ssl_context.load_verify_locations(CAFILE)

        przy self.assertRaisesRegex(
                ssl.CertificateError,
                "hostname '127.0.0.1' doesn't match 'localhost'"):
            przy self.reaped_server(SimpleIMAPHandler) jako server:
                client = self.imap_class(*server.server_address,
                                         ssl_context=ssl_context)
                client.shutdown()

        przy self.reaped_server(SimpleIMAPHandler) jako server:
            client = self.imap_class("localhost", server.server_address[1],
                                     ssl_context=ssl_context)
            client.shutdown()


@unittest.skipUnless(
    support.is_resource_enabled('network'), 'network resource disabled')
klasa RemoteIMAPTest(unittest.TestCase):
    host = 'cyrus.andrew.cmu.edu'
    port = 143
    username = 'anonymous'
    dalejword = 'pass'
    imap_class = imaplib.IMAP4

    def setUp(self):
        przy transient_internet(self.host):
            self.server = self.imap_class(self.host, self.port)

    def tearDown(self):
        jeżeli self.server jest nie Nic:
            przy transient_internet(self.host):
                self.server.logout()

    def test_logincapa(self):
        przy transient_internet(self.host):
            dla cap w self.server.capabilities:
                self.assertIsInstance(cap, str)
            self.assertIn('LOGINDISABLED', self.server.capabilities)
            self.assertIn('AUTH=ANONYMOUS', self.server.capabilities)
            rs = self.server.login(self.username, self.password)
            self.assertEqual(rs[0], 'OK')

    def test_logout(self):
        przy transient_internet(self.host):
            rs = self.server.logout()
            self.server = Nic
            self.assertEqual(rs[0], 'BYE')


@unittest.skipUnless(ssl, "SSL nie available")
@unittest.skipUnless(
    support.is_resource_enabled('network'), 'network resource disabled')
klasa RemoteIMAP_STARTTLSTest(RemoteIMAPTest):

    def setUp(self):
        super().setUp()
        przy transient_internet(self.host):
            rs = self.server.starttls()
            self.assertEqual(rs[0], 'OK')

    def test_logincapa(self):
        dla cap w self.server.capabilities:
            self.assertIsInstance(cap, str)
        self.assertNotIn('LOGINDISABLED', self.server.capabilities)


@unittest.skipUnless(ssl, "SSL nie available")
klasa RemoteIMAP_SSLTest(RemoteIMAPTest):
    port = 993
    imap_class = IMAP4_SSL

    def setUp(self):
        dalej

    def tearDown(self):
        dalej

    def create_ssl_context(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(CERTFILE)
        zwróć ssl_context

    def check_logincapa(self, server):
        spróbuj:
            dla cap w server.capabilities:
                self.assertIsInstance(cap, str)
            self.assertNotIn('LOGINDISABLED', server.capabilities)
            self.assertIn('AUTH=PLAIN', server.capabilities)
            rs = server.login(self.username, self.password)
            self.assertEqual(rs[0], 'OK')
        w_końcu:
            server.logout()

    def test_logincapa(self):
        przy transient_internet(self.host):
            _server = self.imap_class(self.host, self.port)
            self.check_logincapa(_server)

    def test_logincapa_with_client_certfile(self):
        przy transient_internet(self.host):
            _server = self.imap_class(self.host, self.port, certfile=CERTFILE)
            self.check_logincapa(_server)

    def test_logincapa_with_client_ssl_context(self):
        przy transient_internet(self.host):
            _server = self.imap_class(
                self.host, self.port, ssl_context=self.create_ssl_context())
            self.check_logincapa(_server)

    def test_logout(self):
        przy transient_internet(self.host):
            _server = self.imap_class(self.host, self.port)
            rs = _server.logout()
            self.assertEqual(rs[0], 'BYE')

    def test_ssl_context_certfile_exclusive(self):
        przy transient_internet(self.host):
            self.assertRaises(
                ValueError, self.imap_class, self.host, self.port,
                certfile=CERTFILE, ssl_context=self.create_ssl_context())

    def test_ssl_context_keyfile_exclusive(self):
        przy transient_internet(self.host):
            self.assertRaises(
                ValueError, self.imap_class, self.host, self.port,
                keyfile=CERTFILE, ssl_context=self.create_ssl_context())


jeżeli __name__ == "__main__":
    unittest.main()
