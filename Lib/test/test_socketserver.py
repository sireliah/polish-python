"""
Test suite dla socketserver.
"""

zaimportuj contextlib
zaimportuj os
zaimportuj select
zaimportuj signal
zaimportuj socket
zaimportuj select
zaimportuj errno
zaimportuj tempfile
zaimportuj unittest
zaimportuj socketserver

zaimportuj test.support
z test.support zaimportuj reap_children, reap_threads, verbose
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

test.support.requires("network")

TEST_STR = b"hello world\n"
HOST = test.support.HOST

HAVE_UNIX_SOCKETS = hasattr(socket, "AF_UNIX")
requires_unix_sockets = unittest.skipUnless(HAVE_UNIX_SOCKETS,
                                            'requires Unix sockets')
HAVE_FORKING = hasattr(os, "fork")
requires_forking = unittest.skipUnless(HAVE_FORKING, 'requires forking')

def signal_alarm(n):
    """Call signal.alarm when it exists (i.e. nie on Windows)."""
    jeżeli hasattr(signal, 'alarm'):
        signal.alarm(n)

# Remember real select() to avoid interferences przy mocking
_real_select = select.select

def receive(sock, n, timeout=20):
    r, w, x = _real_select([sock], [], [], timeout)
    jeżeli sock w r:
        zwróć sock.recv(n)
    inaczej:
        podnieś RuntimeError("timed out on %r" % (sock,))

jeżeli HAVE_UNIX_SOCKETS:
    klasa ForkingUnixStreamServer(socketserver.ForkingMixIn,
                                  socketserver.UnixStreamServer):
        dalej

    klasa ForkingUnixDatagramServer(socketserver.ForkingMixIn,
                                    socketserver.UnixDatagramServer):
        dalej


@contextlib.contextmanager
def simple_subprocess(testcase):
    pid = os.fork()
    jeżeli pid == 0:
        # Don't podnieś an exception; it would be caught by the test harness.
        os._exit(72)
    uzyskaj Nic
    pid2, status = os.waitpid(pid, 0)
    testcase.assertEqual(pid2, pid)
    testcase.assertEqual(72 << 8, status)


@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa SocketServerTest(unittest.TestCase):
    """Test all socket servers."""

    def setUp(self):
        signal_alarm(60)  # Kill deadlocks after 60 seconds.
        self.port_seed = 0
        self.test_files = []

    def tearDown(self):
        signal_alarm(0)  # Didn't deadlock.
        reap_children()

        dla fn w self.test_files:
            spróbuj:
                os.remove(fn)
            wyjąwszy OSError:
                dalej
        self.test_files[:] = []

    def pickaddr(self, proto):
        jeżeli proto == socket.AF_INET:
            zwróć (HOST, 0)
        inaczej:
            # XXX: We need a way to tell AF_UNIX to pick its own name
            # like AF_INET provides port==0.
            dir = Nic
            fn = tempfile.mktemp(prefix='unix_socket.', dir=dir)
            self.test_files.append(fn)
            zwróć fn

    def make_server(self, addr, svrcls, hdlrbase):
        klasa MyServer(svrcls):
            def handle_error(self, request, client_address):
                self.close_request(request)
                self.server_close()
                podnieś

        klasa MyHandler(hdlrbase):
            def handle(self):
                line = self.rfile.readline()
                self.wfile.write(line)

        jeżeli verbose: print("creating server")
        server = MyServer(addr, MyHandler)
        self.assertEqual(server.server_address, server.socket.getsockname())
        zwróć server

    @reap_threads
    def run_server(self, svrcls, hdlrbase, testfunc):
        server = self.make_server(self.pickaddr(svrcls.address_family),
                                  svrcls, hdlrbase)
        # We had the OS pick a port, so pull the real address out of
        # the server.
        addr = server.server_address
        jeżeli verbose:
            print("ADDR =", addr)
            print("CLASS =", svrcls)

        t = threading.Thread(
            name='%s serving' % svrcls,
            target=server.serve_forever,
            # Short poll interval to make the test finish quickly.
            # Time between requests jest short enough that we won't wake
            # up spuriously too many times.
            kwargs={'poll_interval':0.01})
        t.daemon = Prawda  # In case this function podnieśs.
        t.start()
        jeżeli verbose: print("server running")
        dla i w range(3):
            jeżeli verbose: print("test client", i)
            testfunc(svrcls.address_family, addr)
        jeżeli verbose: print("waiting dla server")
        server.shutdown()
        t.join()
        server.server_close()
        self.assertEqual(-1, server.socket.fileno())
        jeżeli verbose: print("done")

    def stream_examine(self, proto, addr):
        s = socket.socket(proto, socket.SOCK_STREAM)
        s.connect(addr)
        s.sendall(TEST_STR)
        buf = data = receive(s, 100)
        dopóki data oraz b'\n' nie w buf:
            data = receive(s, 100)
            buf += data
        self.assertEqual(buf, TEST_STR)
        s.close()

    def dgram_examine(self, proto, addr):
        s = socket.socket(proto, socket.SOCK_DGRAM)
        s.sendto(TEST_STR, addr)
        buf = data = receive(s, 100)
        dopóki data oraz b'\n' nie w buf:
            data = receive(s, 100)
            buf += data
        self.assertEqual(buf, TEST_STR)
        s.close()

    def test_TCPServer(self):
        self.run_server(socketserver.TCPServer,
                        socketserver.StreamRequestHandler,
                        self.stream_examine)

    def test_ThreadingTCPServer(self):
        self.run_server(socketserver.ThreadingTCPServer,
                        socketserver.StreamRequestHandler,
                        self.stream_examine)

    @requires_forking
    def test_ForkingTCPServer(self):
        przy simple_subprocess(self):
            self.run_server(socketserver.ForkingTCPServer,
                            socketserver.StreamRequestHandler,
                            self.stream_examine)

    @requires_unix_sockets
    def test_UnixStreamServer(self):
        self.run_server(socketserver.UnixStreamServer,
                        socketserver.StreamRequestHandler,
                        self.stream_examine)

    @requires_unix_sockets
    def test_ThreadingUnixStreamServer(self):
        self.run_server(socketserver.ThreadingUnixStreamServer,
                        socketserver.StreamRequestHandler,
                        self.stream_examine)

    @requires_unix_sockets
    @requires_forking
    def test_ForkingUnixStreamServer(self):
        przy simple_subprocess(self):
            self.run_server(ForkingUnixStreamServer,
                            socketserver.StreamRequestHandler,
                            self.stream_examine)

    def test_UDPServer(self):
        self.run_server(socketserver.UDPServer,
                        socketserver.DatagramRequestHandler,
                        self.dgram_examine)

    def test_ThreadingUDPServer(self):
        self.run_server(socketserver.ThreadingUDPServer,
                        socketserver.DatagramRequestHandler,
                        self.dgram_examine)

    @requires_forking
    def test_ForkingUDPServer(self):
        przy simple_subprocess(self):
            self.run_server(socketserver.ForkingUDPServer,
                            socketserver.DatagramRequestHandler,
                            self.dgram_examine)

    # Alas, on Linux (at least) recvfrom() doesn't zwróć a meaningful
    # client address so this cannot work:

    # @requires_unix_sockets
    # def test_UnixDatagramServer(self):
    #     self.run_server(socketserver.UnixDatagramServer,
    #                     socketserver.DatagramRequestHandler,
    #                     self.dgram_examine)
    #
    # @requires_unix_sockets
    # def test_ThreadingUnixDatagramServer(self):
    #     self.run_server(socketserver.ThreadingUnixDatagramServer,
    #                     socketserver.DatagramRequestHandler,
    #                     self.dgram_examine)
    #
    # @requires_unix_sockets
    # @requires_forking
    # def test_ForkingUnixDatagramServer(self):
    #     self.run_server(socketserver.ForkingUnixDatagramServer,
    #                     socketserver.DatagramRequestHandler,
    #                     self.dgram_examine)

    @reap_threads
    def test_shutdown(self):
        # Issue #2302: shutdown() should always succeed w making an
        # other thread leave serve_forever().
        klasa MyServer(socketserver.TCPServer):
            dalej

        klasa MyHandler(socketserver.StreamRequestHandler):
            dalej

        threads = []
        dla i w range(20):
            s = MyServer((HOST, 0), MyHandler)
            t = threading.Thread(
                name='MyServer serving',
                target=s.serve_forever,
                kwargs={'poll_interval':0.01})
            t.daemon = Prawda  # In case this function podnieśs.
            threads.append((t, s))
        dla t, s w threads:
            t.start()
            s.shutdown()
        dla t, s w threads:
            t.join()
            s.server_close()

    def test_tcpserver_bind_leak(self):
        # Issue #22435: the server socket wouldn't be closed jeżeli bind()/listen()
        # failed.
        # Create many servers dla which bind() will fail, to see jeżeli this result
        # w FD exhaustion.
        dla i w range(1024):
            przy self.assertRaises(OverflowError):
                socketserver.TCPServer((HOST, -1),
                                       socketserver.StreamRequestHandler)


klasa MiscTestCase(unittest.TestCase):

    def test_all(self):
        # objects defined w the module should be w __all__
        expected = []
        dla name w dir(socketserver):
            jeżeli nie name.startswith('_'):
                mod_object = getattr(socketserver, name)
                jeżeli getattr(mod_object, '__module__', Nic) == 'socketserver':
                    expected.append(name)
        self.assertCountEqual(socketserver.__all__, expected)


jeżeli __name__ == "__main__":
    unittest.main()
