"""Test script dla ftplib module."""

# Modified by Giampaolo Rodola' to test FTP class, IPv6 oraz TLS
# environment

zaimportuj ftplib
zaimportuj asyncore
zaimportuj asynchat
zaimportuj socket
zaimportuj io
zaimportuj errno
zaimportuj os
zaimportuj time
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    ssl = Nic

z unittest zaimportuj TestCase, skipUnless
z test zaimportuj support
z test.support zaimportuj HOST, HOSTv6
threading = support.import_module('threading')

TIMEOUT = 3
# the dummy data returned by server over the data channel when
# RETR, LIST, NLST, MLSD commands are issued
RETR_DATA = 'abcde12345\r\n' * 1000
LIST_DATA = 'foo\r\nbar\r\n'
NLST_DATA = 'foo\r\nbar\r\n'
MLSD_DATA = ("type=cdir;perm=el;unique==keVO1+ZF4; test\r\n"
             "type=pdir;perm=e;unique==keVO1+d?3; ..\r\n"
             "type=OS.unix=slink:/foobar;perm=;unique==keVO1+4G4; foobar\r\n"
             "type=OS.unix=chr-13/29;perm=;unique==keVO1+5G4; device\r\n"
             "type=OS.unix=blk-11/108;perm=;unique==keVO1+6G4; block\r\n"
             "type=file;perm=awr;unique==keVO1+8G4; writable\r\n"
             "type=dir;perm=cpmel;unique==keVO1+7G4; promiscuous\r\n"
             "type=dir;perm=;unique==keVO1+1t2; no-exec\r\n"
             "type=file;perm=r;unique==keVO1+EG4; two words\r\n"
             "type=file;perm=r;unique==keVO1+IH4;  leading space\r\n"
             "type=file;perm=r;unique==keVO1+1G4; file1\r\n"
             "type=dir;perm=cpmel;unique==keVO1+7G4; incoming\r\n"
             "type=file;perm=r;unique==keVO1+1G4; file2\r\n"
             "type=file;perm=r;unique==keVO1+1G4; file3\r\n"
             "type=file;perm=r;unique==keVO1+1G4; file4\r\n")


klasa DummyDTPHandler(asynchat.async_chat):
    dtp_conn_closed = Nieprawda

    def __init__(self, conn, baseclass):
        asynchat.async_chat.__init__(self, conn)
        self.baseclass = baseclass
        self.baseclass.last_received_data = ''

    def handle_read(self):
        self.baseclass.last_received_data += self.recv(1024).decode('ascii')

    def handle_close(self):
        # XXX: this method can be called many times w a row dla a single
        # connection, including w clear-text (non-TLS) mode.
        # (behaviour witnessed przy test_data_connection)
        jeżeli nie self.dtp_conn_closed:
            self.baseclass.push('226 transfer complete')
            self.close()
            self.dtp_conn_closed = Prawda

    def push(self, what):
        jeżeli self.baseclass.next_data jest nie Nic:
            what = self.baseclass.next_data
            self.baseclass.next_data = Nic
        jeżeli nie what:
            zwróć self.close_when_done()
        super(DummyDTPHandler, self).push(what.encode('ascii'))

    def handle_error(self):
        podnieś Exception


klasa DummyFTPHandler(asynchat.async_chat):

    dtp_handler = DummyDTPHandler

    def __init__(self, conn):
        asynchat.async_chat.__init__(self, conn)
        # tells the socket to handle urgent data inline (ABOR command)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_OOBINLINE, 1)
        self.set_terminator(b"\r\n")
        self.in_buffer = []
        self.dtp = Nic
        self.last_received_cmd = Nic
        self.last_received_data = ''
        self.next_response = ''
        self.next_data = Nic
        self.rest = Nic
        self.next_retr_data = RETR_DATA
        self.push('220 welcome')

    def collect_incoming_data(self, data):
        self.in_buffer.append(data)

    def found_terminator(self):
        line = b''.join(self.in_buffer).decode('ascii')
        self.in_buffer = []
        jeżeli self.next_response:
            self.push(self.next_response)
            self.next_response = ''
        cmd = line.split(' ')[0].lower()
        self.last_received_cmd = cmd
        space = line.find(' ')
        jeżeli space != -1:
            arg = line[space + 1:]
        inaczej:
            arg = ""
        jeżeli hasattr(self, 'cmd_' + cmd):
            method = getattr(self, 'cmd_' + cmd)
            method(arg)
        inaczej:
            self.push('550 command "%s" nie understood.' %cmd)

    def handle_error(self):
        podnieś Exception

    def push(self, data):
        asynchat.async_chat.push(self, data.encode('ascii') + b'\r\n')

    def cmd_port(self, arg):
        addr = list(map(int, arg.split(',')))
        ip = '%d.%d.%d.%d' %tuple(addr[:4])
        port = (addr[4] * 256) + addr[5]
        s = socket.create_connection((ip, port), timeout=TIMEOUT)
        self.dtp = self.dtp_handler(s, baseclass=self)
        self.push('200 active data connection established')

    def cmd_pasv(self, arg):
        przy socket.socket() jako sock:
            sock.bind((self.socket.getsockname()[0], 0))
            sock.listen()
            sock.settimeout(TIMEOUT)
            ip, port = sock.getsockname()[:2]
            ip = ip.replace('.', ','); p1 = port / 256; p2 = port % 256
            self.push('227 entering dalejive mode (%s,%d,%d)' %(ip, p1, p2))
            conn, addr = sock.accept()
            self.dtp = self.dtp_handler(conn, baseclass=self)

    def cmd_eprt(self, arg):
        af, ip, port = arg.split(arg[0])[1:-1]
        port = int(port)
        s = socket.create_connection((ip, port), timeout=TIMEOUT)
        self.dtp = self.dtp_handler(s, baseclass=self)
        self.push('200 active data connection established')

    def cmd_epsv(self, arg):
        przy socket.socket(socket.AF_INET6) jako sock:
            sock.bind((self.socket.getsockname()[0], 0))
            sock.listen()
            sock.settimeout(TIMEOUT)
            port = sock.getsockname()[1]
            self.push('229 entering extended dalejive mode (|||%d|)' %port)
            conn, addr = sock.accept()
            self.dtp = self.dtp_handler(conn, baseclass=self)

    def cmd_echo(self, arg):
        # sends back the received string (used by the test suite)
        self.push(arg)

    def cmd_noop(self, arg):
        self.push('200 noop ok')

    def cmd_user(self, arg):
        self.push('331 username ok')

    def cmd_pass(self, arg):
        self.push('230 dalejword ok')

    def cmd_acct(self, arg):
        self.push('230 acct ok')

    def cmd_rnfr(self, arg):
        self.push('350 rnfr ok')

    def cmd_rnto(self, arg):
        self.push('250 rnto ok')

    def cmd_dele(self, arg):
        self.push('250 dele ok')

    def cmd_cwd(self, arg):
        self.push('250 cwd ok')

    def cmd_size(self, arg):
        self.push('250 1000')

    def cmd_mkd(self, arg):
        self.push('257 "%s"' %arg)

    def cmd_rmd(self, arg):
        self.push('250 rmd ok')

    def cmd_pwd(self, arg):
        self.push('257 "pwd ok"')

    def cmd_type(self, arg):
        self.push('200 type ok')

    def cmd_quit(self, arg):
        self.push('221 quit ok')
        self.close()

    def cmd_abor(self, arg):
        self.push('226 abor ok')

    def cmd_stor(self, arg):
        self.push('125 stor ok')

    def cmd_rest(self, arg):
        self.rest = arg
        self.push('350 rest ok')

    def cmd_retr(self, arg):
        self.push('125 retr ok')
        jeżeli self.rest jest nie Nic:
            offset = int(self.rest)
        inaczej:
            offset = 0
        self.dtp.push(self.next_retr_data[offset:])
        self.dtp.close_when_done()
        self.rest = Nic

    def cmd_list(self, arg):
        self.push('125 list ok')
        self.dtp.push(LIST_DATA)
        self.dtp.close_when_done()

    def cmd_nlst(self, arg):
        self.push('125 nlst ok')
        self.dtp.push(NLST_DATA)
        self.dtp.close_when_done()

    def cmd_opts(self, arg):
        self.push('200 opts ok')

    def cmd_mlsd(self, arg):
        self.push('125 mlsd ok')
        self.dtp.push(MLSD_DATA)
        self.dtp.close_when_done()

    def cmd_setlongretr(self, arg):
        # For testing. Next RETR will zwróć long line.
        self.next_retr_data = 'x' * int(arg)
        self.push('125 setlongretr ok')


klasa DummyFTPServer(asyncore.dispatcher, threading.Thread):

    handler = DummyFTPHandler

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
        podnieś Exception


jeżeli ssl jest nie Nic:

    CERTFILE = os.path.join(os.path.dirname(__file__), "keycert3.pem")
    CAFILE = os.path.join(os.path.dirname(__file__), "pycacert.pem")

    klasa SSLConnection(asyncore.dispatcher):
        """An asyncore.dispatcher subclass supporting TLS/SSL."""

        _ssl_accepting = Nieprawda
        _ssl_closing = Nieprawda

        def secure_connection(self):
            socket = ssl.wrap_socket(self.socket, suppress_ragged_eofs=Nieprawda,
                                     certfile=CERTFILE, server_side=Prawda,
                                     do_handshake_on_connect=Nieprawda,
                                     ssl_version=ssl.PROTOCOL_SSLv23)
            self.del_channel()
            self.set_socket(socket)
            self._ssl_accepting = Prawda

        def _do_ssl_handshake(self):
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
                self._ssl_accepting = Nieprawda

        def _do_ssl_shutdown(self):
            self._ssl_closing = Prawda
            spróbuj:
                self.socket = self.socket.unwrap()
            wyjąwszy ssl.SSLError jako err:
                jeżeli err.args[0] w (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    zwróć
            wyjąwszy OSError jako err:
                # Any "socket error" corresponds to a SSL_ERROR_SYSCALL zwróć
                # z OpenSSL's SSL_shutdown(), corresponding to a
                # closed socket condition. See also:
                # http://www.mail-archive.com/openssl-users@openssl.org/msg60710.html
                dalej
            self._ssl_closing = Nieprawda
            jeżeli getattr(self, '_ccc', Nieprawda) jest Nieprawda:
                super(SSLConnection, self).close()
            inaczej:
                dalej

        def handle_read_event(self):
            jeżeli self._ssl_accepting:
                self._do_ssl_handshake()
            albo_inaczej self._ssl_closing:
                self._do_ssl_shutdown()
            inaczej:
                super(SSLConnection, self).handle_read_event()

        def handle_write_event(self):
            jeżeli self._ssl_accepting:
                self._do_ssl_handshake()
            albo_inaczej self._ssl_closing:
                self._do_ssl_shutdown()
            inaczej:
                super(SSLConnection, self).handle_write_event()

        def send(self, data):
            spróbuj:
                zwróć super(SSLConnection, self).send(data)
            wyjąwszy ssl.SSLError jako err:
                jeżeli err.args[0] w (ssl.SSL_ERROR_EOF, ssl.SSL_ERROR_ZERO_RETURN,
                                   ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    zwróć 0
                podnieś

        def recv(self, buffer_size):
            spróbuj:
                zwróć super(SSLConnection, self).recv(buffer_size)
            wyjąwszy ssl.SSLError jako err:
                jeżeli err.args[0] w (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    zwróć b''
                jeżeli err.args[0] w (ssl.SSL_ERROR_EOF, ssl.SSL_ERROR_ZERO_RETURN):
                    self.handle_close()
                    zwróć b''
                podnieś

        def handle_error(self):
            podnieś Exception

        def close(self):
            jeżeli (isinstance(self.socket, ssl.SSLSocket) oraz
                self.socket._sslobj jest nie Nic):
                self._do_ssl_shutdown()
            inaczej:
                super(SSLConnection, self).close()


    klasa DummyTLS_DTPHandler(SSLConnection, DummyDTPHandler):
        """A DummyDTPHandler subclass supporting TLS/SSL."""

        def __init__(self, conn, baseclass):
            DummyDTPHandler.__init__(self, conn, baseclass)
            jeżeli self.baseclass.secure_data_channel:
                self.secure_connection()


    klasa DummyTLS_FTPHandler(SSLConnection, DummyFTPHandler):
        """A DummyFTPHandler subclass supporting TLS/SSL."""

        dtp_handler = DummyTLS_DTPHandler

        def __init__(self, conn):
            DummyFTPHandler.__init__(self, conn)
            self.secure_data_channel = Nieprawda
            self._ccc = Nieprawda

        def cmd_auth(self, line):
            """Set up secure control channel."""
            self.push('234 AUTH TLS successful')
            self.secure_connection()

        def cmd_ccc(self, line):
            self.push('220 Reverting back to clear-text')
            self._ccc = Prawda
            self._do_ssl_shutdown()

        def cmd_pbsz(self, line):
            """Negotiate size of buffer dla secure data transfer.
            For TLS/SSL the only valid value dla the parameter jest '0'.
            Any other value jest accepted but ignored.
            """
            self.push('200 PBSZ=0 successful.')

        def cmd_prot(self, line):
            """Setup un/secure data channel."""
            arg = line.upper()
            jeżeli arg == 'C':
                self.push('200 Protection set to Clear')
                self.secure_data_channel = Nieprawda
            albo_inaczej arg == 'P':
                self.push('200 Protection set to Private')
                self.secure_data_channel = Prawda
            inaczej:
                self.push("502 Unrecognized PROT type (use C albo P).")


    klasa DummyTLS_FTPServer(DummyFTPServer):
        handler = DummyTLS_FTPHandler


klasa TestFTPClass(TestCase):

    def setUp(self):
        self.server = DummyFTPServer((HOST, 0))
        self.server.start()
        self.client = ftplib.FTP(timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)

    def tearDown(self):
        self.client.close()
        self.server.stop()

    def check_data(self, received, expected):
        self.assertEqual(len(received), len(expected))
        self.assertEqual(received, expected)

    def test_getwelcome(self):
        self.assertEqual(self.client.getwelcome(), '220 welcome')

    def test_sanitize(self):
        self.assertEqual(self.client.sanitize('foo'), repr('foo'))
        self.assertEqual(self.client.sanitize('pass 12345'), repr('pass *****'))
        self.assertEqual(self.client.sanitize('PASS 12345'), repr('PASS *****'))

    def test_exceptions(self):
        self.assertRaises(ftplib.error_temp, self.client.sendcmd, 'echo 400')
        self.assertRaises(ftplib.error_temp, self.client.sendcmd, 'echo 499')
        self.assertRaises(ftplib.error_perm, self.client.sendcmd, 'echo 500')
        self.assertRaises(ftplib.error_perm, self.client.sendcmd, 'echo 599')
        self.assertRaises(ftplib.error_proto, self.client.sendcmd, 'echo 999')

    def test_all_errors(self):
        exceptions = (ftplib.error_reply, ftplib.error_temp, ftplib.error_perm,
                      ftplib.error_proto, ftplib.Error, OSError, EOFError)
        dla x w exceptions:
            spróbuj:
                podnieś x('exception nie included w all_errors set')
            wyjąwszy ftplib.all_errors:
                dalej

    def test_set_pasv(self):
        # dalejive mode jest supposed to be enabled by default
        self.assertPrawda(self.client.passiveserver)
        self.client.set_pasv(Prawda)
        self.assertPrawda(self.client.passiveserver)
        self.client.set_pasv(Nieprawda)
        self.assertNieprawda(self.client.passiveserver)

    def test_voidcmd(self):
        self.client.voidcmd('echo 200')
        self.client.voidcmd('echo 299')
        self.assertRaises(ftplib.error_reply, self.client.voidcmd, 'echo 199')
        self.assertRaises(ftplib.error_reply, self.client.voidcmd, 'echo 300')

    def test_login(self):
        self.client.login()

    def test_acct(self):
        self.client.acct('passwd')

    def test_rename(self):
        self.client.rename('a', 'b')
        self.server.handler_instance.next_response = '200'
        self.assertRaises(ftplib.error_reply, self.client.rename, 'a', 'b')

    def test_delete(self):
        self.client.delete('foo')
        self.server.handler_instance.next_response = '199'
        self.assertRaises(ftplib.error_reply, self.client.delete, 'foo')

    def test_size(self):
        self.client.size('foo')

    def test_mkd(self):
        dir = self.client.mkd('/foo')
        self.assertEqual(dir, '/foo')

    def test_rmd(self):
        self.client.rmd('foo')

    def test_cwd(self):
        dir = self.client.cwd('/foo')
        self.assertEqual(dir, '250 cwd ok')

    def test_pwd(self):
        dir = self.client.pwd()
        self.assertEqual(dir, 'pwd ok')

    def test_quit(self):
        self.assertEqual(self.client.quit(), '221 quit ok')
        # Ensure the connection gets closed; sock attribute should be Nic
        self.assertEqual(self.client.sock, Nic)

    def test_abort(self):
        self.client.abort()

    def test_retrbinary(self):
        def callback(data):
            received.append(data.decode('ascii'))
        received = []
        self.client.retrbinary('retr', callback)
        self.check_data(''.join(received), RETR_DATA)

    def test_retrbinary_rest(self):
        def callback(data):
            received.append(data.decode('ascii'))
        dla rest w (0, 10, 20):
            received = []
            self.client.retrbinary('retr', callback, rest=rest)
            self.check_data(''.join(received), RETR_DATA[rest:])

    def test_retrlines(self):
        received = []
        self.client.retrlines('retr', received.append)
        self.check_data(''.join(received), RETR_DATA.replace('\r\n', ''))

    def test_storbinary(self):
        f = io.BytesIO(RETR_DATA.encode('ascii'))
        self.client.storbinary('stor', f)
        self.check_data(self.server.handler_instance.last_received_data, RETR_DATA)
        # test new callback arg
        flag = []
        f.seek(0)
        self.client.storbinary('stor', f, callback=lambda x: flag.append(Nic))
        self.assertPrawda(flag)

    def test_storbinary_rest(self):
        f = io.BytesIO(RETR_DATA.replace('\r\n', '\n').encode('ascii'))
        dla r w (30, '30'):
            f.seek(0)
            self.client.storbinary('stor', f, rest=r)
            self.assertEqual(self.server.handler_instance.rest, str(r))

    def test_storlines(self):
        f = io.BytesIO(RETR_DATA.replace('\r\n', '\n').encode('ascii'))
        self.client.storlines('stor', f)
        self.check_data(self.server.handler_instance.last_received_data, RETR_DATA)
        # test new callback arg
        flag = []
        f.seek(0)
        self.client.storlines('stor foo', f, callback=lambda x: flag.append(Nic))
        self.assertPrawda(flag)

        f = io.StringIO(RETR_DATA.replace('\r\n', '\n'))
        # storlines() expects a binary file, nie a text file
        przy support.check_warnings(('', BytesWarning), quiet=Prawda):
            self.assertRaises(TypeError, self.client.storlines, 'stor foo', f)

    def test_nlst(self):
        self.client.nlst()
        self.assertEqual(self.client.nlst(), NLST_DATA.split('\r\n')[:-1])

    def test_dir(self):
        l = []
        self.client.dir(lambda x: l.append(x))
        self.assertEqual(''.join(l), LIST_DATA.replace('\r\n', ''))

    def test_mlsd(self):
        list(self.client.mlsd())
        list(self.client.mlsd(path='/'))
        list(self.client.mlsd(path='/', facts=['size', 'type']))

        ls = list(self.client.mlsd())
        dla name, facts w ls:
            self.assertIsInstance(name, str)
            self.assertIsInstance(facts, dict)
            self.assertPrawda(name)
            self.assertIn('type', facts)
            self.assertIn('perm', facts)
            self.assertIn('unique', facts)

        def set_data(data):
            self.server.handler_instance.next_data = data

        def test_entry(line, type=Nic, perm=Nic, unique=Nic, name=Nic):
            type = 'type' jeżeli type jest Nic inaczej type
            perm = 'perm' jeżeli perm jest Nic inaczej perm
            unique = 'unique' jeżeli unique jest Nic inaczej unique
            name = 'name' jeżeli name jest Nic inaczej name
            set_data(line)
            _name, facts = next(self.client.mlsd())
            self.assertEqual(_name, name)
            self.assertEqual(facts['type'], type)
            self.assertEqual(facts['perm'], perm)
            self.assertEqual(facts['unique'], unique)

        # plain
        test_entry('type=type;perm=perm;unique=unique; name\r\n')
        # "=" w fact value
        test_entry('type=ty=pe;perm=perm;unique=unique; name\r\n', type="ty=pe")
        test_entry('type==type;perm=perm;unique=unique; name\r\n', type="=type")
        test_entry('type=t=y=pe;perm=perm;unique=unique; name\r\n', type="t=y=pe")
        test_entry('type=====;perm=perm;unique=unique; name\r\n', type="====")
        # spaces w name
        test_entry('type=type;perm=perm;unique=unique; na me\r\n', name="na me")
        test_entry('type=type;perm=perm;unique=unique; name \r\n', name="name ")
        test_entry('type=type;perm=perm;unique=unique;  name\r\n', name=" name")
        test_entry('type=type;perm=perm;unique=unique; n am  e\r\n', name="n am  e")
        # ";" w name
        test_entry('type=type;perm=perm;unique=unique; na;me\r\n', name="na;me")
        test_entry('type=type;perm=perm;unique=unique; ;name\r\n', name=";name")
        test_entry('type=type;perm=perm;unique=unique; ;name;\r\n', name=";name;")
        test_entry('type=type;perm=perm;unique=unique; ;;;;\r\n', name=";;;;")
        # case sensitiveness
        set_data('Type=type;TyPe=perm;UNIQUE=unique; name\r\n')
        _name, facts = next(self.client.mlsd())
        dla x w facts:
            self.assertPrawda(x.islower())
        # no data (directory empty)
        set_data('')
        self.assertRaises(StopIteration, next, self.client.mlsd())
        set_data('')
        dla x w self.client.mlsd():
            self.fail("unexpected data %s" % x)

    def test_makeport(self):
        przy self.client.makeport():
            # IPv4 jest w use, just make sure send_eprt has nie been used
            self.assertEqual(self.server.handler_instance.last_received_cmd,
                                'port')

    def test_makepasv(self):
        host, port = self.client.makepasv()
        conn = socket.create_connection((host, port), timeout=TIMEOUT)
        conn.close()
        # IPv4 jest w use, just make sure send_epsv has nie been used
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'pasv')

    def test_with_statement(self):
        self.client.quit()

        def is_client_connected():
            jeżeli self.client.sock jest Nic:
                zwróć Nieprawda
            spróbuj:
                self.client.sendcmd('noop')
            wyjąwszy (OSError, EOFError):
                zwróć Nieprawda
            zwróć Prawda

        # base test
        przy ftplib.FTP(timeout=TIMEOUT) jako self.client:
            self.client.connect(self.server.host, self.server.port)
            self.client.sendcmd('noop')
            self.assertPrawda(is_client_connected())
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'quit')
        self.assertNieprawda(is_client_connected())

        # QUIT sent inside the przy block
        przy ftplib.FTP(timeout=TIMEOUT) jako self.client:
            self.client.connect(self.server.host, self.server.port)
            self.client.sendcmd('noop')
            self.client.quit()
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'quit')
        self.assertNieprawda(is_client_connected())

        # force a wrong response code to be sent on QUIT: error_perm
        # jest expected oraz the connection jest supposed to be closed
        spróbuj:
            przy ftplib.FTP(timeout=TIMEOUT) jako self.client:
                self.client.connect(self.server.host, self.server.port)
                self.client.sendcmd('noop')
                self.server.handler_instance.next_response = '550 error on quit'
        wyjąwszy ftplib.error_perm jako err:
            self.assertEqual(str(err), '550 error on quit')
        inaczej:
            self.fail('Exception nie podnieśd')
        # needed to give the threaded server some time to set the attribute
        # which otherwise would still be == 'noop'
        time.sleep(0.1)
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'quit')
        self.assertNieprawda(is_client_connected())

    def test_source_address(self):
        self.client.quit()
        port = support.find_unused_port()
        spróbuj:
            self.client.connect(self.server.host, self.server.port,
                                source_address=(HOST, port))
            self.assertEqual(self.client.sock.getsockname()[1], port)
            self.client.quit()
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.EADDRINUSE:
                self.skipTest("couldn't bind to port %d" % port)
            podnieś

    def test_source_address_passive_connection(self):
        port = support.find_unused_port()
        self.client.source_address = (HOST, port)
        spróbuj:
            przy self.client.transfercmd('list') jako sock:
                self.assertEqual(sock.getsockname()[1], port)
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.EADDRINUSE:
                self.skipTest("couldn't bind to port %d" % port)
            podnieś

    def test_parse257(self):
        self.assertEqual(ftplib.parse257('257 "/foo/bar"'), '/foo/bar')
        self.assertEqual(ftplib.parse257('257 "/foo/bar" created'), '/foo/bar')
        self.assertEqual(ftplib.parse257('257 ""'), '')
        self.assertEqual(ftplib.parse257('257 "" created'), '')
        self.assertRaises(ftplib.error_reply, ftplib.parse257, '250 "/foo/bar"')
        # The 257 response jest supposed to include the directory
        # name oraz w case it contains embedded double-quotes
        # they must be doubled (see RFC-959, chapter 7, appendix 2).
        self.assertEqual(ftplib.parse257('257 "/foo/b""ar"'), '/foo/b"ar')
        self.assertEqual(ftplib.parse257('257 "/foo/b""ar" created'), '/foo/b"ar')

    def test_line_too_long(self):
        self.assertRaises(ftplib.Error, self.client.sendcmd,
                          'x' * self.client.maxline * 2)

    def test_retrlines_too_long(self):
        self.client.sendcmd('SETLONGRETR %d' % (self.client.maxline * 2))
        received = []
        self.assertRaises(ftplib.Error,
                          self.client.retrlines, 'retr', received.append)

    def test_storlines_too_long(self):
        f = io.BytesIO(b'x' * self.client.maxline * 2)
        self.assertRaises(ftplib.Error, self.client.storlines, 'stor', f)


@skipUnless(support.IPV6_ENABLED, "IPv6 nie enabled")
klasa TestIPv6Environment(TestCase):

    def setUp(self):
        self.server = DummyFTPServer((HOSTv6, 0), af=socket.AF_INET6)
        self.server.start()
        self.client = ftplib.FTP(timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)

    def tearDown(self):
        self.client.close()
        self.server.stop()

    def test_af(self):
        self.assertEqual(self.client.af, socket.AF_INET6)

    def test_makeport(self):
        przy self.client.makeport():
            self.assertEqual(self.server.handler_instance.last_received_cmd,
                                'eprt')

    def test_makepasv(self):
        host, port = self.client.makepasv()
        conn = socket.create_connection((host, port), timeout=TIMEOUT)
        conn.close()
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'epsv')

    def test_transfer(self):
        def retr():
            def callback(data):
                received.append(data.decode('ascii'))
            received = []
            self.client.retrbinary('retr', callback)
            self.assertEqual(len(''.join(received)), len(RETR_DATA))
            self.assertEqual(''.join(received), RETR_DATA)
        self.client.set_pasv(Prawda)
        retr()
        self.client.set_pasv(Nieprawda)
        retr()


@skipUnless(ssl, "SSL nie available")
klasa TestTLS_FTPClassMixin(TestFTPClass):
    """Repeat TestFTPClass tests starting the TLS layer dla both control
    oraz data connections first.
    """

    def setUp(self):
        self.server = DummyTLS_FTPServer((HOST, 0))
        self.server.start()
        self.client = ftplib.FTP_TLS(timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)
        # enable TLS
        self.client.auth()
        self.client.prot_p()


@skipUnless(ssl, "SSL nie available")
klasa TestTLS_FTPClass(TestCase):
    """Specific TLS_FTP klasa tests."""

    def setUp(self):
        self.server = DummyTLS_FTPServer((HOST, 0))
        self.server.start()
        self.client = ftplib.FTP_TLS(timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)

    def tearDown(self):
        self.client.close()
        self.server.stop()

    def test_control_connection(self):
        self.assertNotIsInstance(self.client.sock, ssl.SSLSocket)
        self.client.auth()
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)

    def test_data_connection(self):
        # clear text
        przy self.client.transfercmd('list') jako sock:
            self.assertNotIsInstance(sock, ssl.SSLSocket)
        self.assertEqual(self.client.voidresp(), "226 transfer complete")

        # secured, after PROT P
        self.client.prot_p()
        przy self.client.transfercmd('list') jako sock:
            self.assertIsInstance(sock, ssl.SSLSocket)
        self.assertEqual(self.client.voidresp(), "226 transfer complete")

        # PROT C jest issued, the connection must be w cleartext again
        self.client.prot_c()
        przy self.client.transfercmd('list') jako sock:
            self.assertNotIsInstance(sock, ssl.SSLSocket)
        self.assertEqual(self.client.voidresp(), "226 transfer complete")

    def test_login(self):
        # login() jest supposed to implicitly secure the control connection
        self.assertNotIsInstance(self.client.sock, ssl.SSLSocket)
        self.client.login()
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)
        # make sure that AUTH TLS doesn't get issued again
        self.client.login()

    def test_auth_issued_twice(self):
        self.client.auth()
        self.assertRaises(ValueError, self.client.auth)

    def test_auth_ssl(self):
        spróbuj:
            self.client.ssl_version = ssl.PROTOCOL_SSLv23
            self.client.auth()
            self.assertRaises(ValueError, self.client.auth)
        w_końcu:
            self.client.ssl_version = ssl.PROTOCOL_TLSv1

    def test_context(self):
        self.client.quit()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.assertRaises(ValueError, ftplib.FTP_TLS, keyfile=CERTFILE,
                          context=ctx)
        self.assertRaises(ValueError, ftplib.FTP_TLS, certfile=CERTFILE,
                          context=ctx)
        self.assertRaises(ValueError, ftplib.FTP_TLS, certfile=CERTFILE,
                          keyfile=CERTFILE, context=ctx)

        self.client = ftplib.FTP_TLS(context=ctx, timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)
        self.assertNotIsInstance(self.client.sock, ssl.SSLSocket)
        self.client.auth()
        self.assertIs(self.client.sock.context, ctx)
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)

        self.client.prot_p()
        przy self.client.transfercmd('list') jako sock:
            self.assertIs(sock.context, ctx)
            self.assertIsInstance(sock, ssl.SSLSocket)

    def test_ccc(self):
        self.assertRaises(ValueError, self.client.ccc)
        self.client.login(secure=Prawda)
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)
        self.client.ccc()
        self.assertRaises(ValueError, self.client.sock.unwrap)

    def test_check_hostname(self):
        self.client.quit()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.check_hostname = Prawda
        ctx.load_verify_locations(CAFILE)
        self.client = ftplib.FTP_TLS(context=ctx, timeout=TIMEOUT)

        # 127.0.0.1 doesn't match SAN
        self.client.connect(self.server.host, self.server.port)
        przy self.assertRaises(ssl.CertificateError):
            self.client.auth()
        # exception quits connection

        self.client.connect(self.server.host, self.server.port)
        self.client.prot_p()
        przy self.assertRaises(ssl.CertificateError):
            przy self.client.transfercmd("list") jako sock:
                dalej
        self.client.quit()

        self.client.connect("localhost", self.server.port)
        self.client.auth()
        self.client.quit()

        self.client.connect("localhost", self.server.port)
        self.client.prot_p()
        przy self.client.transfercmd("list") jako sock:
            dalej


klasa TestTimeouts(TestCase):

    def setUp(self):
        self.evt = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(20)
        self.port = support.bind_port(self.sock)
        self.server_thread = threading.Thread(target=self.server)
        self.server_thread.start()
        # Wait dla the server to be ready.
        self.evt.wait()
        self.evt.clear()
        self.old_port = ftplib.FTP.port
        ftplib.FTP.port = self.port

    def tearDown(self):
        ftplib.FTP.port = self.old_port
        self.server_thread.join()

    def server(self):
        # This method sets the evt 3 times:
        #  1) when the connection jest ready to be accepted.
        #  2) when it jest safe dla the caller to close the connection
        #  3) when we have closed the socket
        self.sock.listen()
        # (1) Signal the caller that we are ready to accept the connection.
        self.evt.set()
        spróbuj:
            conn, addr = self.sock.accept()
        wyjąwszy socket.timeout:
            dalej
        inaczej:
            conn.sendall(b"1 Hola mundo\n")
            conn.shutdown(socket.SHUT_WR)
            # (2) Signal the caller that it jest safe to close the socket.
            self.evt.set()
            conn.close()
        w_końcu:
            self.sock.close()

    def testTimeoutDefault(self):
        # default -- use global socket timeout
        self.assertIsNic(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        spróbuj:
            ftp = ftplib.FTP(HOST)
        w_końcu:
            socket.setdefaulttimeout(Nic)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()

    def testTimeoutNic(self):
        # no timeout -- do nie use global socket timeout
        self.assertIsNic(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        spróbuj:
            ftp = ftplib.FTP(HOST, timeout=Nic)
        w_końcu:
            socket.setdefaulttimeout(Nic)
        self.assertIsNic(ftp.sock.gettimeout())
        self.evt.wait()
        ftp.close()

    def testTimeoutValue(self):
        # a value
        ftp = ftplib.FTP(HOST, timeout=30)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()

    def testTimeoutConnect(self):
        ftp = ftplib.FTP()
        ftp.connect(HOST, timeout=30)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()

    def testTimeoutDifferentOrder(self):
        ftp = ftplib.FTP(timeout=30)
        ftp.connect(HOST)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()

    def testTimeoutDirectAccess(self):
        ftp = ftplib.FTP()
        ftp.timeout = 30
        ftp.connect(HOST)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()


def test_main():
    tests = [TestFTPClass, TestTimeouts,
             TestIPv6Environment,
             TestTLS_FTPClassMixin, TestTLS_FTPClass]

    thread_info = support.threading_setup()
    spróbuj:
        support.run_unittest(*tests)
    w_końcu:
        support.threading_cleanup(*thread_info)


jeżeli __name__ == '__main__':
    test_main()
