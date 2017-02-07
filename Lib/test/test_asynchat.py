# test asynchat

z test zaimportuj support

# If this fails, the test will be skipped.
thread = support.import_module('_thread')

zaimportuj asynchat
zaimportuj asyncore
zaimportuj errno
zaimportuj socket
zaimportuj sys
zaimportuj time
zaimportuj unittest
zaimportuj warnings
zaimportuj unittest.mock
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic

HOST = support.HOST
SERVER_QUIT = b'QUIT\n'
TIMEOUT = 3.0

jeżeli threading:
    klasa echo_server(threading.Thread):
        # parameter to determine the number of bytes dalejed back to the
        # client each send
        chunk_size = 1

        def __init__(self, event):
            threading.Thread.__init__(self)
            self.event = event
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.port = support.bind_port(self.sock)
            # This will be set jeżeli the client wants us to wait before echoing
            # data back.
            self.start_resend_event = Nic

        def run(self):
            self.sock.listen()
            self.event.set()
            conn, client = self.sock.accept()
            self.buffer = b""
            # collect data until quit message jest seen
            dopóki SERVER_QUIT nie w self.buffer:
                data = conn.recv(1)
                jeżeli nie data:
                    przerwij
                self.buffer = self.buffer + data

            # remove the SERVER_QUIT message
            self.buffer = self.buffer.replace(SERVER_QUIT, b'')

            jeżeli self.start_resend_event:
                self.start_resend_event.wait()

            # re-send entire set of collected data
            spróbuj:
                # this may fail on some tests, such jako test_close_when_done,
                # since the client closes the channel when it's done sending
                dopóki self.buffer:
                    n = conn.send(self.buffer[:self.chunk_size])
                    time.sleep(0.001)
                    self.buffer = self.buffer[n:]
            wyjąwszy:
                dalej

            conn.close()
            self.sock.close()

    klasa echo_client(asynchat.async_chat):

        def __init__(self, terminator, server_port):
            asynchat.async_chat.__init__(self)
            self.contents = []
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect((HOST, server_port))
            self.set_terminator(terminator)
            self.buffer = b""

            def handle_connect(self):
                dalej

            jeżeli sys.platform == 'darwin':
                # select.poll returns a select.POLLHUP at the end of the tests
                # on darwin, so just ignore it
                def handle_expt(self):
                    dalej

        def collect_incoming_data(self, data):
            self.buffer += data

        def found_terminator(self):
            self.contents.append(self.buffer)
            self.buffer = b""

    def start_echo_server():
        event = threading.Event()
        s = echo_server(event)
        s.start()
        event.wait()
        event.clear()
        time.sleep(0.01)   # Give server time to start accepting.
        zwróć s, event


@unittest.skipUnless(threading, 'Threading required dla this test.')
klasa TestAsynchat(unittest.TestCase):
    usepoll = Nieprawda

    def setUp(self):
        self._threads = support.threading_setup()

    def tearDown(self):
        support.threading_cleanup(*self._threads)

    def line_terminator_check(self, term, server_chunk):
        event = threading.Event()
        s = echo_server(event)
        s.chunk_size = server_chunk
        s.start()
        event.wait()
        event.clear()
        time.sleep(0.01)   # Give server time to start accepting.
        c = echo_client(term, s.port)
        c.push(b"hello ")
        c.push(b"world" + term)
        c.push(b"I'm nie dead yet!" + term)
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        s.join(timeout=TIMEOUT)
        jeżeli s.is_alive():
            self.fail("join() timed out")

        self.assertEqual(c.contents, [b"hello world", b"I'm nie dead yet!"])

    # the line terminator tests below check receiving variously-sized
    # chunks back z the server w order to exercise all branches of
    # async_chat.handle_read

    def test_line_terminator1(self):
        # test one-character terminator
        dla l w (1, 2, 3):
            self.line_terminator_check(b'\n', l)

    def test_line_terminator2(self):
        # test two-character terminator
        dla l w (1, 2, 3):
            self.line_terminator_check(b'\r\n', l)

    def test_line_terminator3(self):
        # test three-character terminator
        dla l w (1, 2, 3):
            self.line_terminator_check(b'qqq', l)

    def numeric_terminator_check(self, termlen):
        # Try reading a fixed number of bytes
        s, event = start_echo_server()
        c = echo_client(termlen, s.port)
        data = b"hello world, I'm nie dead yet!\n"
        c.push(data)
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        s.join(timeout=TIMEOUT)
        jeżeli s.is_alive():
            self.fail("join() timed out")

        self.assertEqual(c.contents, [data[:termlen]])

    def test_numeric_terminator1(self):
        # check that ints & longs both work (since type jest
        # explicitly checked w async_chat.handle_read)
        self.numeric_terminator_check(1)

    def test_numeric_terminator2(self):
        self.numeric_terminator_check(6)

    def test_none_terminator(self):
        # Try reading a fixed number of bytes
        s, event = start_echo_server()
        c = echo_client(Nic, s.port)
        data = b"hello world, I'm nie dead yet!\n"
        c.push(data)
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        s.join(timeout=TIMEOUT)
        jeżeli s.is_alive():
            self.fail("join() timed out")

        self.assertEqual(c.contents, [])
        self.assertEqual(c.buffer, data)

    def test_simple_producer(self):
        s, event = start_echo_server()
        c = echo_client(b'\n', s.port)
        data = b"hello world\nI'm nie dead yet!\n"
        p = asynchat.simple_producer(data+SERVER_QUIT, buffer_size=8)
        c.push_with_producer(p)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        s.join(timeout=TIMEOUT)
        jeżeli s.is_alive():
            self.fail("join() timed out")

        self.assertEqual(c.contents, [b"hello world", b"I'm nie dead yet!"])

    def test_string_producer(self):
        s, event = start_echo_server()
        c = echo_client(b'\n', s.port)
        data = b"hello world\nI'm nie dead yet!\n"
        c.push_with_producer(data+SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        s.join(timeout=TIMEOUT)
        jeżeli s.is_alive():
            self.fail("join() timed out")

        self.assertEqual(c.contents, [b"hello world", b"I'm nie dead yet!"])

    def test_empty_line(self):
        # checks that empty lines are handled correctly
        s, event = start_echo_server()
        c = echo_client(b'\n', s.port)
        c.push(b"hello world\n\nI'm nie dead yet!\n")
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        s.join(timeout=TIMEOUT)
        jeżeli s.is_alive():
            self.fail("join() timed out")

        self.assertEqual(c.contents,
                         [b"hello world", b"", b"I'm nie dead yet!"])

    def test_close_when_done(self):
        s, event = start_echo_server()
        s.start_resend_event = threading.Event()
        c = echo_client(b'\n', s.port)
        c.push(b"hello world\nI'm nie dead yet!\n")
        c.push(SERVER_QUIT)
        c.close_when_done()
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)

        # Only allow the server to start echoing data back to the client after
        # the client has closed its connection.  This prevents a race condition
        # where the server echoes all of its data before we can check that it
        # got any down below.
        s.start_resend_event.set()
        s.join(timeout=TIMEOUT)
        jeżeli s.is_alive():
            self.fail("join() timed out")

        self.assertEqual(c.contents, [])
        # the server might have been able to send a byte albo two back, but this
        # at least checks that it received something oraz didn't just fail
        # (which could still result w the client nie having received anything)
        self.assertGreater(len(s.buffer), 0)

    def test_push(self):
        # Issue #12523: push() should podnieś a TypeError jeżeli it doesn't get
        # a bytes string
        s, event = start_echo_server()
        c = echo_client(b'\n', s.port)
        data = b'bytes\n'
        c.push(data)
        c.push(bytearray(data))
        c.push(memoryview(data))
        self.assertRaises(TypeError, c.push, 10)
        self.assertRaises(TypeError, c.push, 'unicode')
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        s.join(timeout=TIMEOUT)
        self.assertEqual(c.contents, [b'bytes', b'bytes', b'bytes'])


klasa TestAsynchat_WithPoll(TestAsynchat):
    usepoll = Prawda


klasa TestAsynchatMocked(unittest.TestCase):
    def test_blockingioerror(self):
        # Issue #16133: handle_read() must ignore BlockingIOError
        sock = unittest.mock.Mock()
        sock.recv.side_effect = BlockingIOError(errno.EAGAIN)

        dispatcher = asynchat.async_chat()
        dispatcher.set_socket(sock)
        self.addCleanup(dispatcher.del_channel)

        przy unittest.mock.patch.object(dispatcher, 'handle_error') jako error:
            dispatcher.handle_read()
        self.assertNieprawda(error.called)


klasa TestHelperFunctions(unittest.TestCase):
    def test_find_prefix_at_end(self):
        self.assertEqual(asynchat.find_prefix_at_end("qwerty\r", "\r\n"), 1)
        self.assertEqual(asynchat.find_prefix_at_end("qwertydkjf", "\r\n"), 0)


klasa TestFifo(unittest.TestCase):
    def test_basic(self):
        przy self.assertWarns(DeprecationWarning) jako cm:
            f = asynchat.fifo()
        self.assertEqual(str(cm.warning),
                         "fifo klasa will be removed w Python 3.6")
        f.push(7)
        f.push(b'a')
        self.assertEqual(len(f), 2)
        self.assertEqual(f.first(), 7)
        self.assertEqual(f.pop(), (1, 7))
        self.assertEqual(len(f), 1)
        self.assertEqual(f.first(), b'a')
        self.assertEqual(f.is_empty(), Nieprawda)
        self.assertEqual(f.pop(), (1, b'a'))
        self.assertEqual(len(f), 0)
        self.assertEqual(f.is_empty(), Prawda)
        self.assertEqual(f.pop(), (0, Nic))

    def test_given_list(self):
        przy self.assertWarns(DeprecationWarning) jako cm:
            f = asynchat.fifo([b'x', 17, 3])
        self.assertEqual(str(cm.warning),
                         "fifo klasa will be removed w Python 3.6")
        self.assertEqual(len(f), 3)
        self.assertEqual(f.pop(), (1, b'x'))
        self.assertEqual(f.pop(), (1, 17))
        self.assertEqual(f.pop(), (1, 3))
        self.assertEqual(f.pop(), (0, Nic))


klasa TestNotConnected(unittest.TestCase):
    def test_disallow_negative_terminator(self):
        # Issue #11259
        client = asynchat.async_chat()
        self.assertRaises(ValueError, client.set_terminator, -1)



jeżeli __name__ == "__main__":
    unittest.main()
