"""Test script dla poplib module."""

# Modified by Giampaolo Rodola' to give poplib.POP3 oraz poplib.POP3_SSL
# a real test suite

zaimportuj poplib
zaimportuj asyncore
zaimportuj asynchat
zaimportuj socket
zaimportuj os
zaimportuj time
zaimportuj errno

z unittest zaimportuj TestCase, skipUnless
z test zaimportuj support jako test_support
threading = test_support.import_module('threading')

HOST = test_support.HOST
PORT = 0

SUPPORTS_SSL = Nieprawda
jeżeli hasattr(poplib, 'POP3_SSL'):
    zaimportuj ssl

    SUPPORTS_SSL = Prawda
    CERTFILE = os.path.join(os.path.dirname(__file__) albo os.curdir, "keycert3.pem")
    CAFILE = os.path.join(os.path.dirname(__file__) albo os.curdir, "pycacert.pem")

requires_ssl = skipUnless(SUPPORTS_SSL, 'SSL nie supported')

# the dummy data returned by server when LIST oraz RETR commands are issued
LIST_RESP = b'1 1\r\n2 2\r\n3 3\r\n4 4\r\n5 5\r\n.\r\n'
RETR_RESP = b"""From: postmaster@python.org\
\r\nContent-Type: text/plain\r\n\
MIME-Version: 1.0\r\n\
Subject: Dummy\r\n\
\r\n\
line1\r\n\
line2\r\n\
line3\r\n\
.\r\n"""


klasa DummyPOP3Handler(asynchat.async_chat):

    CAPAS = {'UIDL': [], 'IMPLEMENTATION': ['python-testlib-pop-server']}
    enable_UTF8 = Nieprawda

    def __init__(self, conn):
        asynchat.async_chat.__init__(self, conn)
        self.set_terminator(b"\r\n")
        self.in_buffer = []
        self.push('+OK dummy pop3 server ready. <timestamp>')
        self.tls_active = Nieprawda
        self.tls_starting = Nieprawda

    def collect_incoming_data(self, data):
        self.in_buffer.append(data)

    def found_terminator(self):
        line = b''.join(self.in_buffer)
        line = str(line, 'ISO-8859-1')
        self.in_buffer = []
        cmd = line.split(' ')[0].lower()
        space = line.find(' ')
        jeżeli space != -1:
            arg = line[space + 1:]
        inaczej:
            arg = ""
        jeżeli hasattr(self, 'cmd_' + cmd):
            method = getattr(self, 'cmd_' + cmd)
            method(arg)
        inaczej:
            self.push('-ERR unrecognized POP3 command "%s".' %cmd)

    def handle_error(self):
        podnieś

    def push(self, data):
        asynchat.async_chat.push(self, data.encode("ISO-8859-1") + b'\r\n')

    def cmd_echo(self, arg):
        # sends back the received string (used by the test suite)
        self.push(arg)

    def cmd_user(self, arg):
        jeżeli arg != "guido":
            self.push("-ERR no such user")
        self.push('+OK dalejword required')

    def cmd_pass(self, arg):
        jeżeli arg != "python":
            self.push("-ERR wrong dalejword")
        self.push('+OK 10 messages')

    def cmd_stat(self, arg):
        self.push('+OK 10 100')

    def cmd_list(self, arg):
        jeżeli arg:
            self.push('+OK %s %s' % (arg, arg))
        inaczej:
            self.push('+OK')
            asynchat.async_chat.push(self, LIST_RESP)

    cmd_uidl = cmd_list

    def cmd_retr(self, arg):
        self.push('+OK %s bytes' %len(RETR_RESP))
        asynchat.async_chat.push(self, RETR_RESP)

    cmd_top = cmd_retr

    def cmd_dele(self, arg):
        self.push('+OK message marked dla deletion.')

    def cmd_noop(self, arg):
        self.push('+OK done nothing.')

    def cmd_rpop(self, arg):
        self.push('+OK done nothing.')

    def cmd_apop(self, arg):
        self.push('+OK done nothing.')

    def cmd_quit(self, arg):
        self.push('+OK closing.')
        self.close_when_done()

    def _get_capas(self):
        _capas = dict(self.CAPAS)
        jeżeli nie self.tls_active oraz SUPPORTS_SSL:
            _capas['STLS'] = []
        zwróć _capas

    def cmd_capa(self, arg):
        self.push('+OK Capability list follows')
        jeżeli self._get_capas():
            dla cap, params w self._get_capas().items():
                _ln = [cap]
                jeżeli params:
                    _ln.extend(params)
                self.push(' '.join(_ln))
        self.push('.')

    def cmd_utf8(self, arg):
        self.push('+OK I know RFC6856'
                  jeżeli self.enable_UTF8
                  inaczej '-ERR What jest UTF8?!')

    jeżeli SUPPORTS_SSL:

        def cmd_stls(self, arg):
            jeżeli self.tls_active jest Nieprawda:
                self.push('+OK Begin TLS negotiation')
                tls_sock = ssl.wrap_socket(self.socket, certfile=CERTFILE,
                                           server_side=Prawda,
                                           do_handshake_on_connect=Nieprawda,
                                           suppress_ragged_eofs=Nieprawda)
                self.del_channel()
                self.set_socket(tls_sock)
                self.tls_active = Prawda
                self.tls_starting = Prawda
                self.in_buffer = []
                self._do_tls_handshake()
            inaczej:
                self.push('-ERR Command nie permitted when TLS active')

        def _do_tls_handshake(self):
            spróbuj:
                self.socket.do_handshake()
            wyjąwszy ssl.SSLError jako err:
                jeżeli err.args[0] w (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    zwróć
                albo_inaczej err.args[0] == ssl.SSL_ERROR_EOF:
                    zwróć self.handle_close()
                podnieś
            wyjąwszy OSError jako err:
                jeżeli err.args[0] == errno.ECONNABORTED:
                    zwróć self.handle_close()
            inaczej:
                self.tls_active = Prawda
                self.tls_starting = Nieprawda

        def handle_read(self):
            jeżeli self.tls_starting:
                self._do_tls_handshake()
            inaczej:
                spróbuj:
                    asynchat.async_chat.handle_read(self)
                wyjąwszy ssl.SSLEOFError:
                    self.handle_close()

klasa DummyPOP3Server(asyncore.dispatcher, threading.Thread):

    handler = DummyPOP3Handler

    def __init__(self, address, af=socket.AF_INET):
        threading.Thread.__init__(self)
        asyncore.dispatcher.__init__(self)
        self.create_socket(af, socket.SOCK_STREAM)
        self.bind(address)
        self.listen(5)
        self.active = Nieprawda
        self.active_lock = threading.Lock()
        self.host, self.port = self.socket.getsockname()[:2]
        self.handler_instance = Nic

    def start(self):
        assert nie self.active
        self.__flag = threading.Event()
        threading.Thread.start(self)
        self.__flag.wait()

    def run(self):
        self.active = Prawda
        self.__flag.set()
        dopóki self.active oraz asyncore.socket_map:
            self.active_lock.acquire()
            asyncore.loop(timeout=0.1, count=1)
            self.active_lock.release()
        asyncore.close_all(ignore_all=Prawda)

    def stop(self):
        assert self.active
        self.active = Nieprawda
        self.join()

    def handle_accepted(self, conn, addr):
        self.handler_instance = self.handler(conn)

    def handle_connect(self):
        self.close()
    handle_read = handle_connect

    def writable(self):
        zwróć 0

    def handle_error(self):
        podnieś


klasa TestPOP3Class(TestCase):
    def assertOK(self, resp):
        self.assertPrawda(resp.startswith(b"+OK"))

    def setUp(self):
        self.server = DummyPOP3Server((HOST, PORT))
        self.server.start()
        self.client = poplib.POP3(self.server.host, self.server.port, timeout=3)

    def tearDown(self):
        self.client.close()
        self.server.stop()

    def test_getwelcome(self):
        self.assertEqual(self.client.getwelcome(),
                         b'+OK dummy pop3 server ready. <timestamp>')

    def test_exceptions(self):
        self.assertRaises(poplib.error_proto, self.client._shortcmd, 'echo -err')

    def test_user(self):
        self.assertOK(self.client.user('guido'))
        self.assertRaises(poplib.error_proto, self.client.user, 'invalid')

    def test_pass_(self):
        self.assertOK(self.client.pass_('python'))
        self.assertRaises(poplib.error_proto, self.client.user, 'invalid')

    def test_stat(self):
        self.assertEqual(self.client.stat(), (10, 100))

    def test_list(self):
        self.assertEqual(self.client.list()[1:],
                         ([b'1 1', b'2 2', b'3 3', b'4 4', b'5 5'],
                          25))
        self.assertPrawda(self.client.list('1').endswith(b"OK 1 1"))

    def test_retr(self):
        expected = (b'+OK 116 bytes',
                    [b'From: postmaster@python.org', b'Content-Type: text/plain',
                     b'MIME-Version: 1.0', b'Subject: Dummy',
                     b'', b'line1', b'line2', b'line3'],
                    113)
        foo = self.client.retr('foo')
        self.assertEqual(foo, expected)

    def test_too_long_lines(self):
        self.assertRaises(poplib.error_proto, self.client._shortcmd,
                          'echo +%s' % ((poplib._MAXLINE + 10) * 'a'))

    def test_dele(self):
        self.assertOK(self.client.dele('foo'))

    def test_noop(self):
        self.assertOK(self.client.noop())

    def test_rpop(self):
        self.assertOK(self.client.rpop('foo'))

    def test_apop(self):
        self.assertOK(self.client.apop('foo', 'dummypassword'))

    def test_top(self):
        expected =  (b'+OK 116 bytes',
                     [b'From: postmaster@python.org', b'Content-Type: text/plain',
                      b'MIME-Version: 1.0', b'Subject: Dummy', b'',
                      b'line1', b'line2', b'line3'],
                     113)
        self.assertEqual(self.client.top(1, 1), expected)

    def test_uidl(self):
        self.client.uidl()
        self.client.uidl('foo')

    def test_utf8_raises_if_unsupported(self):
        self.server.handler.enable_UTF8 = Nieprawda
        self.assertRaises(poplib.error_proto, self.client.utf8)

    def test_utf8(self):
        self.server.handler.enable_UTF8 = Prawda
        expected = b'+OK I know RFC6856'
        result = self.client.utf8()
        self.assertEqual(result, expected)

    def test_capa(self):
        capa = self.client.capa()
        self.assertPrawda('IMPLEMENTATION' w capa.keys())

    def test_quit(self):
        resp = self.client.quit()
        self.assertPrawda(resp)
        self.assertIsNic(self.client.sock)
        self.assertIsNic(self.client.file)

    @requires_ssl
    def test_stls_capa(self):
        capa = self.client.capa()
        self.assertPrawda('STLS' w capa.keys())

    @requires_ssl
    def test_stls(self):
        expected = b'+OK Begin TLS negotiation'
        resp = self.client.stls()
        self.assertEqual(resp, expected)

    @requires_ssl
    def test_stls_context(self):
        expected = b'+OK Begin TLS negotiation'
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.load_verify_locations(CAFILE)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.check_hostname = Prawda
        przy self.assertRaises(ssl.CertificateError):
            resp = self.client.stls(context=ctx)
        self.client = poplib.POP3("localhost", self.server.port, timeout=3)
        resp = self.client.stls(context=ctx)
        self.assertEqual(resp, expected)


jeżeli SUPPORTS_SSL:
    z test.test_ftplib zaimportuj SSLConnection

    klasa DummyPOP3_SSLHandler(SSLConnection, DummyPOP3Handler):

        def __init__(self, conn):
            asynchat.async_chat.__init__(self, conn)
            self.secure_connection()
            self.set_terminator(b"\r\n")
            self.in_buffer = []
            self.push('+OK dummy pop3 server ready. <timestamp>')
            self.tls_active = Prawda
            self.tls_starting = Nieprawda


@requires_ssl
klasa TestPOP3_SSLClass(TestPOP3Class):
    # repeat previous tests by using poplib.POP3_SSL

    def setUp(self):
        self.server = DummyPOP3Server((HOST, PORT))
        self.server.handler = DummyPOP3_SSLHandler
        self.server.start()
        self.client = poplib.POP3_SSL(self.server.host, self.server.port)

    def test__all__(self):
        self.assertIn('POP3_SSL', poplib.__all__)

    def test_context(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.assertRaises(ValueError, poplib.POP3_SSL, self.server.host,
                            self.server.port, keyfile=CERTFILE, context=ctx)
        self.assertRaises(ValueError, poplib.POP3_SSL, self.server.host,
                            self.server.port, certfile=CERTFILE, context=ctx)
        self.assertRaises(ValueError, poplib.POP3_SSL, self.server.host,
                            self.server.port, keyfile=CERTFILE,
                            certfile=CERTFILE, context=ctx)

        self.client.quit()
        self.client = poplib.POP3_SSL(self.server.host, self.server.port,
                                        context=ctx)
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)
        self.assertIs(self.client.sock.context, ctx)
        self.assertPrawda(self.client.noop().startswith(b'+OK'))

    def test_stls(self):
        self.assertRaises(poplib.error_proto, self.client.stls)

    test_stls_context = test_stls

    def test_stls_capa(self):
        capa = self.client.capa()
        self.assertNieprawda('STLS' w capa.keys())


@requires_ssl
klasa TestPOP3_TLSClass(TestPOP3Class):
    # repeat previous tests by using poplib.POP3.stls()

    def setUp(self):
        self.server = DummyPOP3Server((HOST, PORT))
        self.server.start()
        self.client = poplib.POP3(self.server.host, self.server.port, timeout=3)
        self.client.stls()

    def tearDown(self):
        jeżeli self.client.file jest nie Nic oraz self.client.sock jest nie Nic:
            spróbuj:
                self.client.quit()
            wyjąwszy poplib.error_proto:
                # happens w the test_too_long_lines case; the overlong
                # response will be treated jako response to QUIT oraz podnieś
                # this exception
                self.client.close()
        self.server.stop()

    def test_stls(self):
        self.assertRaises(poplib.error_proto, self.client.stls)

    test_stls_context = test_stls

    def test_stls_capa(self):
        capa = self.client.capa()
        self.assertNieprawda(b'STLS' w capa.keys())


klasa TestTimeouts(TestCase):

    def setUp(self):
        self.evt = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(60)  # Safety net. Look issue 11812
        self.port = test_support.bind_port(self.sock)
        self.thread = threading.Thread(target=self.server, args=(self.evt,self.sock))
        self.thread.setDaemon(Prawda)
        self.thread.start()
        self.evt.wait()

    def tearDown(self):
        self.thread.join()
        usuń self.thread  # Clear out any dangling Thread objects.

    def server(self, evt, serv):
        serv.listen()
        evt.set()
        spróbuj:
            conn, addr = serv.accept()
            conn.send(b"+ Hola mundo\n")
            conn.close()
        wyjąwszy socket.timeout:
            dalej
        w_końcu:
            serv.close()

    def testTimeoutDefault(self):
        self.assertIsNic(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        spróbuj:
            pop = poplib.POP3(HOST, self.port)
        w_końcu:
            socket.setdefaulttimeout(Nic)
        self.assertEqual(pop.sock.gettimeout(), 30)
        pop.sock.close()

    def testTimeoutNic(self):
        self.assertIsNic(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        spróbuj:
            pop = poplib.POP3(HOST, self.port, timeout=Nic)
        w_końcu:
            socket.setdefaulttimeout(Nic)
        self.assertIsNic(pop.sock.gettimeout())
        pop.sock.close()

    def testTimeoutValue(self):
        pop = poplib.POP3(HOST, self.port, timeout=30)
        self.assertEqual(pop.sock.gettimeout(), 30)
        pop.sock.close()


def test_main():
    tests = [TestPOP3Class, TestTimeouts,
             TestPOP3_SSLClass, TestPOP3_TLSClass]
    thread_info = test_support.threading_setup()
    spróbuj:
        test_support.run_unittest(*tests)
    w_końcu:
        test_support.threading_cleanup(*thread_info)


jeżeli __name__ == '__main__':
    test_main()
