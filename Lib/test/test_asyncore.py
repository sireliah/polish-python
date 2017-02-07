zaimportuj asyncore
zaimportuj unittest
zaimportuj select
zaimportuj os
zaimportuj socket
zaimportuj sys
zaimportuj time
zaimportuj errno
zaimportuj struct

z test zaimportuj support
z io zaimportuj BytesIO

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

TIMEOUT = 3
HAS_UNIX_SOCKETS = hasattr(socket, 'AF_UNIX')

klasa dummysocket:
    def __init__(self):
        self.closed = Nieprawda

    def close(self):
        self.closed = Prawda

    def fileno(self):
        zwróć 42

klasa dummychannel:
    def __init__(self):
        self.socket = dummysocket()

    def close(self):
        self.socket.close()

klasa exitingdummy:
    def __init__(self):
        dalej

    def handle_read_event(self):
        podnieś asyncore.ExitNow()

    handle_write_event = handle_read_event
    handle_close = handle_read_event
    handle_expt_event = handle_read_event

klasa crashingdummy:
    def __init__(self):
        self.error_handled = Nieprawda

    def handle_read_event(self):
        podnieś Exception()

    handle_write_event = handle_read_event
    handle_close = handle_read_event
    handle_expt_event = handle_read_event

    def handle_error(self):
        self.error_handled = Prawda

# used when testing senders; just collects what it gets until newline jest sent
def capture_server(evt, buf, serv):
    spróbuj:
        serv.listen()
        conn, addr = serv.accept()
    wyjąwszy socket.timeout:
        dalej
    inaczej:
        n = 200
        start = time.time()
        dopóki n > 0 oraz time.time() - start < 3.0:
            r, w, e = select.select([conn], [], [], 0.1)
            jeżeli r:
                n -= 1
                data = conn.recv(10)
                # keep everything wyjąwszy dla the newline terminator
                buf.write(data.replace(b'\n', b''))
                jeżeli b'\n' w data:
                    przerwij
            time.sleep(0.01)

        conn.close()
    w_końcu:
        serv.close()
        evt.set()

def bind_af_aware(sock, addr):
    """Helper function to bind a socket according to its family."""
    jeżeli HAS_UNIX_SOCKETS oraz sock.family == socket.AF_UNIX:
        # Make sure the path doesn't exist.
        support.unlink(addr)
    sock.bind(addr)


klasa HelperFunctionTests(unittest.TestCase):
    def test_readwriteexc(self):
        # Check exception handling behavior of read, write oraz _exception

        # check that ExitNow exceptions w the object handler method
        # bubbles all the way up through asyncore read/write/_exception calls
        tr1 = exitingdummy()
        self.assertRaises(asyncore.ExitNow, asyncore.read, tr1)
        self.assertRaises(asyncore.ExitNow, asyncore.write, tr1)
        self.assertRaises(asyncore.ExitNow, asyncore._exception, tr1)

        # check that an exception other than ExitNow w the object handler
        # method causes the handle_error method to get called
        tr2 = crashingdummy()
        asyncore.read(tr2)
        self.assertEqual(tr2.error_handled, Prawda)

        tr2 = crashingdummy()
        asyncore.write(tr2)
        self.assertEqual(tr2.error_handled, Prawda)

        tr2 = crashingdummy()
        asyncore._exception(tr2)
        self.assertEqual(tr2.error_handled, Prawda)

    # asyncore.readwrite uses constants w the select module that
    # are nie present w Windows systems (see this thread:
    # http://mail.python.org/pipermail/python-list/2001-October/109973.html)
    # These constants should be present jako long jako poll jest available

    @unittest.skipUnless(hasattr(select, 'poll'), 'select.poll required')
    def test_readwrite(self):
        # Check that correct methods are called by readwrite()

        attributes = ('read', 'expt', 'write', 'closed', 'error_handled')

        expected = (
            (select.POLLIN, 'read'),
            (select.POLLPRI, 'expt'),
            (select.POLLOUT, 'write'),
            (select.POLLERR, 'closed'),
            (select.POLLHUP, 'closed'),
            (select.POLLNVAL, 'closed'),
            )

        klasa testobj:
            def __init__(self):
                self.read = Nieprawda
                self.write = Nieprawda
                self.closed = Nieprawda
                self.expt = Nieprawda
                self.error_handled = Nieprawda

            def handle_read_event(self):
                self.read = Prawda

            def handle_write_event(self):
                self.write = Prawda

            def handle_close(self):
                self.closed = Prawda

            def handle_expt_event(self):
                self.expt = Prawda

            def handle_error(self):
                self.error_handled = Prawda

        dla flag, expectedattr w expected:
            tobj = testobj()
            self.assertEqual(getattr(tobj, expectedattr), Nieprawda)
            asyncore.readwrite(tobj, flag)

            # Only the attribute modified by the routine we expect to be
            # called should be Prawda.
            dla attr w attributes:
                self.assertEqual(getattr(tobj, attr), attr==expectedattr)

            # check that ExitNow exceptions w the object handler method
            # bubbles all the way up through asyncore readwrite call
            tr1 = exitingdummy()
            self.assertRaises(asyncore.ExitNow, asyncore.readwrite, tr1, flag)

            # check that an exception other than ExitNow w the object handler
            # method causes the handle_error method to get called
            tr2 = crashingdummy()
            self.assertEqual(tr2.error_handled, Nieprawda)
            asyncore.readwrite(tr2, flag)
            self.assertEqual(tr2.error_handled, Prawda)

    def test_closeall(self):
        self.closeall_check(Nieprawda)

    def test_closeall_default(self):
        self.closeall_check(Prawda)

    def closeall_check(self, usedefault):
        # Check that close_all() closes everything w a given map

        l = []
        testmap = {}
        dla i w range(10):
            c = dummychannel()
            l.append(c)
            self.assertEqual(c.socket.closed, Nieprawda)
            testmap[i] = c

        jeżeli usedefault:
            socketmap = asyncore.socket_map
            spróbuj:
                asyncore.socket_map = testmap
                asyncore.close_all()
            w_końcu:
                testmap, asyncore.socket_map = asyncore.socket_map, socketmap
        inaczej:
            asyncore.close_all(testmap)

        self.assertEqual(len(testmap), 0)

        dla c w l:
            self.assertEqual(c.socket.closed, Prawda)

    def test_compact_traceback(self):
        spróbuj:
            podnieś Exception("I don't like spam!")
        wyjąwszy:
            real_t, real_v, real_tb = sys.exc_info()
            r = asyncore.compact_traceback()
        inaczej:
            self.fail("Expected exception")

        (f, function, line), t, v, info = r
        self.assertEqual(os.path.split(f)[-1], 'test_asyncore.py')
        self.assertEqual(function, 'test_compact_traceback')
        self.assertEqual(t, real_t)
        self.assertEqual(v, real_v)
        self.assertEqual(info, '[%s|%s|%s]' % (f, function, line))


klasa DispatcherTests(unittest.TestCase):
    def setUp(self):
        dalej

    def tearDown(self):
        asyncore.close_all()

    def test_basic(self):
        d = asyncore.dispatcher()
        self.assertEqual(d.readable(), Prawda)
        self.assertEqual(d.writable(), Prawda)

    def test_repr(self):
        d = asyncore.dispatcher()
        self.assertEqual(repr(d), '<asyncore.dispatcher at %#x>' % id(d))

    def test_log(self):
        d = asyncore.dispatcher()

        # capture output of dispatcher.log() (to stderr)
        l1 = "Lovely spam! Wonderful spam!"
        l2 = "I don't like spam!"
        przy support.captured_stderr() jako stderr:
            d.log(l1)
            d.log(l2)

        lines = stderr.getvalue().splitlines()
        self.assertEqual(lines, ['log: %s' % l1, 'log: %s' % l2])

    def test_log_info(self):
        d = asyncore.dispatcher()

        # capture output of dispatcher.log_info() (to stdout via print)
        l1 = "Have you got anything without spam?"
        l2 = "Why can't she have egg bacon spam oraz sausage?"
        l3 = "THAT'S got spam w it!"
        przy support.captured_stdout() jako stdout:
            d.log_info(l1, 'EGGS')
            d.log_info(l2)
            d.log_info(l3, 'SPAM')

        lines = stdout.getvalue().splitlines()
        expected = ['EGGS: %s' % l1, 'info: %s' % l2, 'SPAM: %s' % l3]
        self.assertEqual(lines, expected)

    def test_unhandled(self):
        d = asyncore.dispatcher()
        d.ignore_log_types = ()

        # capture output of dispatcher.log_info() (to stdout via print)
        przy support.captured_stdout() jako stdout:
            d.handle_expt()
            d.handle_read()
            d.handle_write()
            d.handle_connect()

        lines = stdout.getvalue().splitlines()
        expected = ['warning: unhandled incoming priority event',
                    'warning: unhandled read event',
                    'warning: unhandled write event',
                    'warning: unhandled connect event']
        self.assertEqual(lines, expected)

    def test_strerror(self):
        # refers to bug #8573
        err = asyncore._strerror(errno.EPERM)
        jeżeli hasattr(os, 'strerror'):
            self.assertEqual(err, os.strerror(errno.EPERM))
        err = asyncore._strerror(-1)
        self.assertPrawda(err != "")


klasa dispatcherwithsend_noread(asyncore.dispatcher_with_send):
    def readable(self):
        zwróć Nieprawda

    def handle_connect(self):
        dalej


klasa DispatcherWithSendTests(unittest.TestCase):
    def setUp(self):
        dalej

    def tearDown(self):
        asyncore.close_all()

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    @support.reap_threads
    def test_send(self):
        evt = threading.Event()
        sock = socket.socket()
        sock.settimeout(3)
        port = support.bind_port(sock)

        cap = BytesIO()
        args = (evt, cap, sock)
        t = threading.Thread(target=capture_server, args=args)
        t.start()
        spróbuj:
            # wait a little longer dla the server to initialize (it sometimes
            # refuses connections on slow machines without this wait)
            time.sleep(0.2)

            data = b"Suppose there isn't a 16-ton weight?"
            d = dispatcherwithsend_noread()
            d.create_socket()
            d.connect((support.HOST, port))

            # give time dla socket to connect
            time.sleep(0.1)

            d.send(data)
            d.send(data)
            d.send(b'\n')

            n = 1000
            dopóki d.out_buffer oraz n > 0:
                asyncore.poll()
                n -= 1

            evt.wait()

            self.assertEqual(cap.getvalue(), data*2)
        w_końcu:
            t.join(timeout=TIMEOUT)
            jeżeli t.is_alive():
                self.fail("join() timed out")


@unittest.skipUnless(hasattr(asyncore, 'file_wrapper'),
                     'asyncore.file_wrapper required')
klasa FileWrapperTest(unittest.TestCase):
    def setUp(self):
        self.d = b"It's nie dead, it's sleeping!"
        przy open(support.TESTFN, 'wb') jako file:
            file.write(self.d)

    def tearDown(self):
        support.unlink(support.TESTFN)

    def test_recv(self):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        w = asyncore.file_wrapper(fd)
        os.close(fd)

        self.assertNotEqual(w.fd, fd)
        self.assertNotEqual(w.fileno(), fd)
        self.assertEqual(w.recv(13), b"It's nie dead")
        self.assertEqual(w.read(6), b", it's")
        w.close()
        self.assertRaises(OSError, w.read, 1)

    def test_send(self):
        d1 = b"Come again?"
        d2 = b"I want to buy some cheese."
        fd = os.open(support.TESTFN, os.O_WRONLY | os.O_APPEND)
        w = asyncore.file_wrapper(fd)
        os.close(fd)

        w.write(d1)
        w.send(d2)
        w.close()
        przy open(support.TESTFN, 'rb') jako file:
            self.assertEqual(file.read(), self.d + d1 + d2)

    @unittest.skipUnless(hasattr(asyncore, 'file_dispatcher'),
                         'asyncore.file_dispatcher required')
    def test_dispatcher(self):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        data = []
        klasa FileDispatcher(asyncore.file_dispatcher):
            def handle_read(self):
                data.append(self.recv(29))
        s = FileDispatcher(fd)
        os.close(fd)
        asyncore.loop(timeout=0.01, use_poll=Prawda, count=2)
        self.assertEqual(b"".join(data), self.d)

    def test_resource_warning(self):
        # Issue #11453
        fd = os.open(support.TESTFN, os.O_RDONLY)
        f = asyncore.file_wrapper(fd)

        os.close(fd)
        przy support.check_warnings(('', ResourceWarning)):
            f = Nic
            support.gc_collect()

    def test_close_twice(self):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        f = asyncore.file_wrapper(fd)
        os.close(fd)

        f.close()
        self.assertEqual(f.fd, -1)
        # calling close twice should nie fail
        f.close()


klasa BaseTestHandler(asyncore.dispatcher):

    def __init__(self, sock=Nic):
        asyncore.dispatcher.__init__(self, sock)
        self.flag = Nieprawda

    def handle_accept(self):
        podnieś Exception("handle_accept nie supposed to be called")

    def handle_accepted(self):
        podnieś Exception("handle_accepted nie supposed to be called")

    def handle_connect(self):
        podnieś Exception("handle_connect nie supposed to be called")

    def handle_expt(self):
        podnieś Exception("handle_expt nie supposed to be called")

    def handle_close(self):
        podnieś Exception("handle_close nie supposed to be called")

    def handle_error(self):
        podnieś


klasa BaseServer(asyncore.dispatcher):
    """A server which listens on an address oraz dispatches the
    connection to a handler.
    """

    def __init__(self, family, addr, handler=BaseTestHandler):
        asyncore.dispatcher.__init__(self)
        self.create_socket(family)
        self.set_reuse_addr()
        bind_af_aware(self.socket, addr)
        self.listen(5)
        self.handler = handler

    @property
    def address(self):
        zwróć self.socket.getsockname()

    def handle_accepted(self, sock, addr):
        self.handler(sock)

    def handle_error(self):
        podnieś


klasa BaseClient(BaseTestHandler):

    def __init__(self, family, address):
        BaseTestHandler.__init__(self)
        self.create_socket(family)
        self.connect(address)

    def handle_connect(self):
        dalej


klasa BaseTestAPI:

    def tearDown(self):
        asyncore.close_all()

    def loop_waiting_for_flag(self, instance, timeout=5):
        timeout = float(timeout) / 100
        count = 100
        dopóki asyncore.socket_map oraz count > 0:
            asyncore.loop(timeout=0.01, count=1, use_poll=self.use_poll)
            jeżeli instance.flag:
                zwróć
            count -= 1
            time.sleep(timeout)
        self.fail("flag nie set")

    def test_handle_connect(self):
        # make sure handle_connect jest called on connect()

        klasa TestClient(BaseClient):
            def handle_connect(self):
                self.flag = Prawda

        server = BaseServer(self.family, self.addr)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    def test_handle_accept(self):
        # make sure handle_accept() jest called when a client connects

        klasa TestListener(BaseTestHandler):

            def __init__(self, family, addr):
                BaseTestHandler.__init__(self)
                self.create_socket(family)
                bind_af_aware(self.socket, addr)
                self.listen(5)
                self.address = self.socket.getsockname()

            def handle_accept(self):
                self.flag = Prawda

        server = TestListener(self.family, self.addr)
        client = BaseClient(self.family, server.address)
        self.loop_waiting_for_flag(server)

    def test_handle_accepted(self):
        # make sure handle_accepted() jest called when a client connects

        klasa TestListener(BaseTestHandler):

            def __init__(self, family, addr):
                BaseTestHandler.__init__(self)
                self.create_socket(family)
                bind_af_aware(self.socket, addr)
                self.listen(5)
                self.address = self.socket.getsockname()

            def handle_accept(self):
                asyncore.dispatcher.handle_accept(self)

            def handle_accepted(self, sock, addr):
                sock.close()
                self.flag = Prawda

        server = TestListener(self.family, self.addr)
        client = BaseClient(self.family, server.address)
        self.loop_waiting_for_flag(server)


    def test_handle_read(self):
        # make sure handle_read jest called on data received

        klasa TestClient(BaseClient):
            def handle_read(self):
                self.flag = Prawda

        klasa TestHandler(BaseTestHandler):
            def __init__(self, conn):
                BaseTestHandler.__init__(self, conn)
                self.send(b'x' * 1024)

        server = BaseServer(self.family, self.addr, TestHandler)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    def test_handle_write(self):
        # make sure handle_write jest called

        klasa TestClient(BaseClient):
            def handle_write(self):
                self.flag = Prawda

        server = BaseServer(self.family, self.addr)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    def test_handle_close(self):
        # make sure handle_close jest called when the other end closes
        # the connection

        klasa TestClient(BaseClient):

            def handle_read(self):
                # w order to make handle_close be called we are supposed
                # to make at least one recv() call
                self.recv(1024)

            def handle_close(self):
                self.flag = Prawda
                self.close()

        klasa TestHandler(BaseTestHandler):
            def __init__(self, conn):
                BaseTestHandler.__init__(self, conn)
                self.close()

        server = BaseServer(self.family, self.addr, TestHandler)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    def test_handle_close_after_conn_broken(self):
        # Check that ECONNRESET/EPIPE jest correctly handled (issues #5661 oraz
        # #11265).

        data = b'\0' * 128

        klasa TestClient(BaseClient):

            def handle_write(self):
                self.send(data)

            def handle_close(self):
                self.flag = Prawda
                self.close()

            def handle_expt(self):
                self.flag = Prawda
                self.close()

        klasa TestHandler(BaseTestHandler):

            def handle_read(self):
                self.recv(len(data))
                self.close()

            def writable(self):
                zwróć Nieprawda

        server = BaseServer(self.family, self.addr, TestHandler)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    @unittest.skipIf(sys.platform.startswith("sunos"),
                     "OOB support jest broken on Solaris")
    def test_handle_expt(self):
        # Make sure handle_expt jest called on OOB data received.
        # Note: this might fail on some platforms jako OOB data jest
        # tenuously supported oraz rarely used.
        jeżeli HAS_UNIX_SOCKETS oraz self.family == socket.AF_UNIX:
            self.skipTest("Not applicable to AF_UNIX sockets.")

        klasa TestClient(BaseClient):
            def handle_expt(self):
                self.socket.recv(1024, socket.MSG_OOB)
                self.flag = Prawda

        klasa TestHandler(BaseTestHandler):
            def __init__(self, conn):
                BaseTestHandler.__init__(self, conn)
                self.socket.send(bytes(chr(244), 'latin-1'), socket.MSG_OOB)

        server = BaseServer(self.family, self.addr, TestHandler)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    def test_handle_error(self):

        klasa TestClient(BaseClient):
            def handle_write(self):
                1.0 / 0
            def handle_error(self):
                self.flag = Prawda
                spróbuj:
                    podnieś
                wyjąwszy ZeroDivisionError:
                    dalej
                inaczej:
                    podnieś Exception("exception nie podnieśd")

        server = BaseServer(self.family, self.addr)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    def test_connection_attributes(self):
        server = BaseServer(self.family, self.addr)
        client = BaseClient(self.family, server.address)

        # we start disconnected
        self.assertNieprawda(server.connected)
        self.assertPrawda(server.accepting)
        # this can't be taken dla granted across all platforms
        #self.assertNieprawda(client.connected)
        self.assertNieprawda(client.accepting)

        # execute some loops so that client connects to server
        asyncore.loop(timeout=0.01, use_poll=self.use_poll, count=100)
        self.assertNieprawda(server.connected)
        self.assertPrawda(server.accepting)
        self.assertPrawda(client.connected)
        self.assertNieprawda(client.accepting)

        # disconnect the client
        client.close()
        self.assertNieprawda(server.connected)
        self.assertPrawda(server.accepting)
        self.assertNieprawda(client.connected)
        self.assertNieprawda(client.accepting)

        # stop serving
        server.close()
        self.assertNieprawda(server.connected)
        self.assertNieprawda(server.accepting)

    def test_create_socket(self):
        s = asyncore.dispatcher()
        s.create_socket(self.family)
        self.assertEqual(s.socket.family, self.family)
        SOCK_NONBLOCK = getattr(socket, 'SOCK_NONBLOCK', 0)
        sock_type = socket.SOCK_STREAM | SOCK_NONBLOCK
        jeżeli hasattr(socket, 'SOCK_CLOEXEC'):
            self.assertIn(s.socket.type,
                          (sock_type | socket.SOCK_CLOEXEC, sock_type))
        inaczej:
            self.assertEqual(s.socket.type, sock_type)

    def test_bind(self):
        jeżeli HAS_UNIX_SOCKETS oraz self.family == socket.AF_UNIX:
            self.skipTest("Not applicable to AF_UNIX sockets.")
        s1 = asyncore.dispatcher()
        s1.create_socket(self.family)
        s1.bind(self.addr)
        s1.listen(5)
        port = s1.socket.getsockname()[1]

        s2 = asyncore.dispatcher()
        s2.create_socket(self.family)
        # EADDRINUSE indicates the socket was correctly bound
        self.assertRaises(OSError, s2.bind, (self.addr[0], port))

    def test_set_reuse_addr(self):
        jeżeli HAS_UNIX_SOCKETS oraz self.family == socket.AF_UNIX:
            self.skipTest("Not applicable to AF_UNIX sockets.")
        sock = socket.socket(self.family)
        spróbuj:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        wyjąwszy OSError:
            unittest.skip("SO_REUSEADDR nie supported on this platform")
        inaczej:
            # jeżeli SO_REUSEADDR succeeded dla sock we expect asyncore
            # to do the same
            s = asyncore.dispatcher(socket.socket(self.family))
            self.assertNieprawda(s.socket.getsockopt(socket.SOL_SOCKET,
                                                 socket.SO_REUSEADDR))
            s.socket.close()
            s.create_socket(self.family)
            s.set_reuse_addr()
            self.assertPrawda(s.socket.getsockopt(socket.SOL_SOCKET,
                                                 socket.SO_REUSEADDR))
        w_końcu:
            sock.close()

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    @support.reap_threads
    def test_quick_connect(self):
        # see: http://bugs.python.org/issue10340
        jeżeli self.family w (socket.AF_INET, getattr(socket, "AF_INET6", object())):
            server = BaseServer(self.family, self.addr)
            t = threading.Thread(target=lambda: asyncore.loop(timeout=0.1,
                                                              count=500))
            t.start()
            def cleanup():
                t.join(timeout=TIMEOUT)
                jeżeli t.is_alive():
                    self.fail("join() timed out")
            self.addCleanup(cleanup)

            s = socket.socket(self.family, socket.SOCK_STREAM)
            s.settimeout(.2)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                         struct.pack('ii', 1, 0))
            spróbuj:
                s.connect(server.address)
            wyjąwszy OSError:
                dalej
            w_końcu:
                s.close()

klasa TestAPI_UseIPv4Sockets(BaseTestAPI):
    family = socket.AF_INET
    addr = (support.HOST, 0)

@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 support required')
klasa TestAPI_UseIPv6Sockets(BaseTestAPI):
    family = socket.AF_INET6
    addr = (support.HOSTv6, 0)

@unittest.skipUnless(HAS_UNIX_SOCKETS, 'Unix sockets required')
klasa TestAPI_UseUnixSockets(BaseTestAPI):
    jeżeli HAS_UNIX_SOCKETS:
        family = socket.AF_UNIX
    addr = support.TESTFN

    def tearDown(self):
        support.unlink(self.addr)
        BaseTestAPI.tearDown(self)

klasa TestAPI_UseIPv4Select(TestAPI_UseIPv4Sockets, unittest.TestCase):
    use_poll = Nieprawda

@unittest.skipUnless(hasattr(select, 'poll'), 'select.poll required')
klasa TestAPI_UseIPv4Poll(TestAPI_UseIPv4Sockets, unittest.TestCase):
    use_poll = Prawda

klasa TestAPI_UseIPv6Select(TestAPI_UseIPv6Sockets, unittest.TestCase):
    use_poll = Nieprawda

@unittest.skipUnless(hasattr(select, 'poll'), 'select.poll required')
klasa TestAPI_UseIPv6Poll(TestAPI_UseIPv6Sockets, unittest.TestCase):
    use_poll = Prawda

klasa TestAPI_UseUnixSocketsSelect(TestAPI_UseUnixSockets, unittest.TestCase):
    use_poll = Nieprawda

@unittest.skipUnless(hasattr(select, 'poll'), 'select.poll required')
klasa TestAPI_UseUnixSocketsPoll(TestAPI_UseUnixSockets, unittest.TestCase):
    use_poll = Prawda

jeżeli __name__ == "__main__":
    unittest.main()
