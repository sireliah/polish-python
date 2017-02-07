"""Tests dla selector_events.py"""

zaimportuj errno
zaimportuj socket
zaimportuj unittest
z unittest zaimportuj mock
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    ssl = Nic

zaimportuj asyncio
z asyncio zaimportuj selectors
z asyncio zaimportuj test_utils
z asyncio.selector_events zaimportuj BaseSelectorEventLoop
z asyncio.selector_events zaimportuj _SelectorTransport
z asyncio.selector_events zaimportuj _SelectorSslTransport
z asyncio.selector_events zaimportuj _SelectorSocketTransport
z asyncio.selector_events zaimportuj _SelectorDatagramTransport


MOCK_ANY = mock.ANY


klasa TestBaseSelectorEventLoop(BaseSelectorEventLoop):

    def close(self):
        # Don't call the close() method of the parent class, because the
        # selector jest mocked
        self._closed = Prawda

    def _make_self_pipe(self):
        self._ssock = mock.Mock()
        self._csock = mock.Mock()
        self._internal_fds += 1


def list_to_buffer(l=()):
    zwróć bytearray().join(l)


def close_transport(transport):
    # Don't call transport.close() because the event loop oraz the selector
    # are mocked
    jeżeli transport._sock jest Nic:
        zwróć
    transport._sock.close()
    transport._sock = Nic


klasa BaseSelectorEventLoopTests(test_utils.TestCase):

    def setUp(self):
        self.selector = mock.Mock()
        self.selector.select.return_value = []
        self.loop = TestBaseSelectorEventLoop(self.selector)
        self.set_event_loop(self.loop)

    def test_make_socket_transport(self):
        m = mock.Mock()
        self.loop.add_reader = mock.Mock()
        self.loop.add_reader._is_coroutine = Nieprawda
        transport = self.loop._make_socket_transport(m, asyncio.Protocol())
        self.assertIsInstance(transport, _SelectorSocketTransport)

        # Calling repr() must nie fail when the event loop jest closed
        self.loop.close()
        repr(transport)

        close_transport(transport)

    @unittest.skipIf(ssl jest Nic, 'No ssl module')
    def test_make_ssl_transport(self):
        m = mock.Mock()
        self.loop.add_reader = mock.Mock()
        self.loop.add_reader._is_coroutine = Nieprawda
        self.loop.add_writer = mock.Mock()
        self.loop.remove_reader = mock.Mock()
        self.loop.remove_writer = mock.Mock()
        waiter = asyncio.Future(loop=self.loop)
        przy test_utils.disable_logger():
            transport = self.loop._make_ssl_transport(
                m, asyncio.Protocol(), m, waiter)
            # execute the handshake dopóki the logger jest disabled
            # to ignore SSL handshake failure
            test_utils.run_briefly(self.loop)

        # Sanity check
        class_name = transport.__class__.__name__
        self.assertIn("ssl", class_name.lower())
        self.assertIn("transport", class_name.lower())

        transport.close()
        # execute pending callbacks to close the socket transport
        test_utils.run_briefly(self.loop)

    @mock.patch('asyncio.selector_events.ssl', Nic)
    @mock.patch('asyncio.sslproto.ssl', Nic)
    def test_make_ssl_transport_without_ssl_error(self):
        m = mock.Mock()
        self.loop.add_reader = mock.Mock()
        self.loop.add_writer = mock.Mock()
        self.loop.remove_reader = mock.Mock()
        self.loop.remove_writer = mock.Mock()
        przy self.assertRaises(RuntimeError):
            self.loop._make_ssl_transport(m, m, m, m)

    def test_close(self):
        klasa EventLoop(BaseSelectorEventLoop):
            def _make_self_pipe(self):
                self._ssock = mock.Mock()
                self._csock = mock.Mock()
                self._internal_fds += 1

        self.loop = EventLoop(self.selector)
        self.set_event_loop(self.loop)

        ssock = self.loop._ssock
        ssock.fileno.return_value = 7
        csock = self.loop._csock
        csock.fileno.return_value = 1
        remove_reader = self.loop.remove_reader = mock.Mock()

        self.loop._selector.close()
        self.loop._selector = selector = mock.Mock()
        self.assertNieprawda(self.loop.is_closed())

        self.loop.close()
        self.assertPrawda(self.loop.is_closed())
        self.assertIsNic(self.loop._selector)
        self.assertIsNic(self.loop._csock)
        self.assertIsNic(self.loop._ssock)
        selector.close.assert_called_with()
        ssock.close.assert_called_with()
        csock.close.assert_called_with()
        remove_reader.assert_called_with(7)

        # it should be possible to call close() more than once
        self.loop.close()
        self.loop.close()

        # operation blocked when the loop jest closed
        f = asyncio.Future(loop=self.loop)
        self.assertRaises(RuntimeError, self.loop.run_forever)
        self.assertRaises(RuntimeError, self.loop.run_until_complete, f)
        fd = 0
        def callback():
            dalej
        self.assertRaises(RuntimeError, self.loop.add_reader, fd, callback)
        self.assertRaises(RuntimeError, self.loop.add_writer, fd, callback)

    def test_close_no_selector(self):
        self.loop.remove_reader = mock.Mock()
        self.loop._selector.close()
        self.loop._selector = Nic
        self.loop.close()
        self.assertIsNic(self.loop._selector)

    def test_socketpair(self):
        self.assertRaises(NotImplementedError, self.loop._socketpair)

    def test_read_from_self_tryagain(self):
        self.loop._ssock.recv.side_effect = BlockingIOError
        self.assertIsNic(self.loop._read_from_self())

    def test_read_from_self_exception(self):
        self.loop._ssock.recv.side_effect = OSError
        self.assertRaises(OSError, self.loop._read_from_self)

    def test_write_to_self_tryagain(self):
        self.loop._csock.send.side_effect = BlockingIOError
        przy test_utils.disable_logger():
            self.assertIsNic(self.loop._write_to_self())

    def test_write_to_self_exception(self):
        # _write_to_self() swallows OSError
        self.loop._csock.send.side_effect = RuntimeError()
        self.assertRaises(RuntimeError, self.loop._write_to_self)

    def test_sock_recv(self):
        sock = test_utils.mock_nonblocking_socket()
        self.loop._sock_recv = mock.Mock()

        f = self.loop.sock_recv(sock, 1024)
        self.assertIsInstance(f, asyncio.Future)
        self.loop._sock_recv.assert_called_with(f, Nieprawda, sock, 1024)

    def test__sock_recv_canceled_fut(self):
        sock = mock.Mock()

        f = asyncio.Future(loop=self.loop)
        f.cancel()

        self.loop._sock_recv(f, Nieprawda, sock, 1024)
        self.assertNieprawda(sock.recv.called)

    def test__sock_recv_unregister(self):
        sock = mock.Mock()
        sock.fileno.return_value = 10

        f = asyncio.Future(loop=self.loop)
        f.cancel()

        self.loop.remove_reader = mock.Mock()
        self.loop._sock_recv(f, Prawda, sock, 1024)
        self.assertEqual((10,), self.loop.remove_reader.call_args[0])

    def test__sock_recv_tryagain(self):
        f = asyncio.Future(loop=self.loop)
        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.recv.side_effect = BlockingIOError

        self.loop.add_reader = mock.Mock()
        self.loop._sock_recv(f, Nieprawda, sock, 1024)
        self.assertEqual((10, self.loop._sock_recv, f, Prawda, sock, 1024),
                         self.loop.add_reader.call_args[0])

    def test__sock_recv_exception(self):
        f = asyncio.Future(loop=self.loop)
        sock = mock.Mock()
        sock.fileno.return_value = 10
        err = sock.recv.side_effect = OSError()

        self.loop._sock_recv(f, Nieprawda, sock, 1024)
        self.assertIs(err, f.exception())

    def test_sock_sendall(self):
        sock = test_utils.mock_nonblocking_socket()
        self.loop._sock_sendall = mock.Mock()

        f = self.loop.sock_sendall(sock, b'data')
        self.assertIsInstance(f, asyncio.Future)
        self.assertEqual(
            (f, Nieprawda, sock, b'data'),
            self.loop._sock_sendall.call_args[0])

    def test_sock_sendall_nodata(self):
        sock = test_utils.mock_nonblocking_socket()
        self.loop._sock_sendall = mock.Mock()

        f = self.loop.sock_sendall(sock, b'')
        self.assertIsInstance(f, asyncio.Future)
        self.assertPrawda(f.done())
        self.assertIsNic(f.result())
        self.assertNieprawda(self.loop._sock_sendall.called)

    def test__sock_sendall_canceled_fut(self):
        sock = mock.Mock()

        f = asyncio.Future(loop=self.loop)
        f.cancel()

        self.loop._sock_sendall(f, Nieprawda, sock, b'data')
        self.assertNieprawda(sock.send.called)

    def test__sock_sendall_unregister(self):
        sock = mock.Mock()
        sock.fileno.return_value = 10

        f = asyncio.Future(loop=self.loop)
        f.cancel()

        self.loop.remove_writer = mock.Mock()
        self.loop._sock_sendall(f, Prawda, sock, b'data')
        self.assertEqual((10,), self.loop.remove_writer.call_args[0])

    def test__sock_sendall_tryagain(self):
        f = asyncio.Future(loop=self.loop)
        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.send.side_effect = BlockingIOError

        self.loop.add_writer = mock.Mock()
        self.loop._sock_sendall(f, Nieprawda, sock, b'data')
        self.assertEqual(
            (10, self.loop._sock_sendall, f, Prawda, sock, b'data'),
            self.loop.add_writer.call_args[0])

    def test__sock_sendall_interrupted(self):
        f = asyncio.Future(loop=self.loop)
        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.send.side_effect = InterruptedError

        self.loop.add_writer = mock.Mock()
        self.loop._sock_sendall(f, Nieprawda, sock, b'data')
        self.assertEqual(
            (10, self.loop._sock_sendall, f, Prawda, sock, b'data'),
            self.loop.add_writer.call_args[0])

    def test__sock_sendall_exception(self):
        f = asyncio.Future(loop=self.loop)
        sock = mock.Mock()
        sock.fileno.return_value = 10
        err = sock.send.side_effect = OSError()

        self.loop._sock_sendall(f, Nieprawda, sock, b'data')
        self.assertIs(f.exception(), err)

    def test__sock_sendall(self):
        sock = mock.Mock()

        f = asyncio.Future(loop=self.loop)
        sock.fileno.return_value = 10
        sock.send.return_value = 4

        self.loop._sock_sendall(f, Nieprawda, sock, b'data')
        self.assertPrawda(f.done())
        self.assertIsNic(f.result())

    def test__sock_sendall_partial(self):
        sock = mock.Mock()

        f = asyncio.Future(loop=self.loop)
        sock.fileno.return_value = 10
        sock.send.return_value = 2

        self.loop.add_writer = mock.Mock()
        self.loop._sock_sendall(f, Nieprawda, sock, b'data')
        self.assertNieprawda(f.done())
        self.assertEqual(
            (10, self.loop._sock_sendall, f, Prawda, sock, b'ta'),
            self.loop.add_writer.call_args[0])

    def test__sock_sendall_none(self):
        sock = mock.Mock()

        f = asyncio.Future(loop=self.loop)
        sock.fileno.return_value = 10
        sock.send.return_value = 0

        self.loop.add_writer = mock.Mock()
        self.loop._sock_sendall(f, Nieprawda, sock, b'data')
        self.assertNieprawda(f.done())
        self.assertEqual(
            (10, self.loop._sock_sendall, f, Prawda, sock, b'data'),
            self.loop.add_writer.call_args[0])

    def test_sock_connect(self):
        sock = test_utils.mock_nonblocking_socket()
        self.loop._sock_connect = mock.Mock()

        f = self.loop.sock_connect(sock, ('127.0.0.1', 8080))
        self.assertIsInstance(f, asyncio.Future)
        self.assertEqual(
            (f, sock, ('127.0.0.1', 8080)),
            self.loop._sock_connect.call_args[0])

    def test_sock_connect_timeout(self):
        # asyncio issue #205: sock_connect() must unregister the socket on
        # timeout error

        # prepare mocks
        self.loop.add_writer = mock.Mock()
        self.loop.remove_writer = mock.Mock()
        sock = test_utils.mock_nonblocking_socket()
        sock.connect.side_effect = BlockingIOError

        # first call to sock_connect() registers the socket
        fut = self.loop.sock_connect(sock, ('127.0.0.1', 80))
        self.assertPrawda(sock.connect.called)
        self.assertPrawda(self.loop.add_writer.called)
        self.assertEqual(len(fut._callbacks), 1)

        # on timeout, the socket must be unregistered
        sock.connect.reset_mock()
        fut.set_exception(asyncio.TimeoutError)
        przy self.assertRaises(asyncio.TimeoutError):
            self.loop.run_until_complete(fut)
        self.assertPrawda(self.loop.remove_writer.called)

    def test__sock_connect(self):
        f = asyncio.Future(loop=self.loop)

        sock = mock.Mock()
        sock.fileno.return_value = 10

        self.loop._sock_connect(f, sock, ('127.0.0.1', 8080))
        self.assertPrawda(f.done())
        self.assertIsNic(f.result())
        self.assertPrawda(sock.connect.called)

    def test__sock_connect_cb_cancelled_fut(self):
        sock = mock.Mock()
        self.loop.remove_writer = mock.Mock()

        f = asyncio.Future(loop=self.loop)
        f.cancel()

        self.loop._sock_connect_cb(f, sock, ('127.0.0.1', 8080))
        self.assertNieprawda(sock.getsockopt.called)

    def test__sock_connect_writer(self):
        # check that the fd jest registered oraz then unregistered
        self.loop._process_events = mock.Mock()
        self.loop.add_writer = mock.Mock()
        self.loop.remove_writer = mock.Mock()

        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.connect.side_effect = BlockingIOError
        sock.getsockopt.return_value = 0
        address = ('127.0.0.1', 8080)

        f = asyncio.Future(loop=self.loop)
        self.loop._sock_connect(f, sock, address)
        self.assertPrawda(self.loop.add_writer.called)
        self.assertEqual(10, self.loop.add_writer.call_args[0][0])

        self.loop._sock_connect_cb(f, sock, address)
        # need to run the event loop to execute _sock_connect_done() callback
        self.loop.run_until_complete(f)
        self.assertEqual((10,), self.loop.remove_writer.call_args[0])

    def test__sock_connect_cb_tryagain(self):
        f = asyncio.Future(loop=self.loop)
        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.getsockopt.return_value = errno.EAGAIN

        # check that the exception jest handled
        self.loop._sock_connect_cb(f, sock, ('127.0.0.1', 8080))

    def test__sock_connect_cb_exception(self):
        f = asyncio.Future(loop=self.loop)
        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.getsockopt.return_value = errno.ENOTCONN

        self.loop.remove_writer = mock.Mock()
        self.loop._sock_connect_cb(f, sock, ('127.0.0.1', 8080))
        self.assertIsInstance(f.exception(), OSError)

    def test_sock_accept(self):
        sock = test_utils.mock_nonblocking_socket()
        self.loop._sock_accept = mock.Mock()

        f = self.loop.sock_accept(sock)
        self.assertIsInstance(f, asyncio.Future)
        self.assertEqual(
            (f, Nieprawda, sock), self.loop._sock_accept.call_args[0])

    def test__sock_accept(self):
        f = asyncio.Future(loop=self.loop)

        conn = mock.Mock()

        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.accept.return_value = conn, ('127.0.0.1', 1000)

        self.loop._sock_accept(f, Nieprawda, sock)
        self.assertPrawda(f.done())
        self.assertEqual((conn, ('127.0.0.1', 1000)), f.result())
        self.assertEqual((Nieprawda,), conn.setblocking.call_args[0])

    def test__sock_accept_canceled_fut(self):
        sock = mock.Mock()

        f = asyncio.Future(loop=self.loop)
        f.cancel()

        self.loop._sock_accept(f, Nieprawda, sock)
        self.assertNieprawda(sock.accept.called)

    def test__sock_accept_unregister(self):
        sock = mock.Mock()
        sock.fileno.return_value = 10

        f = asyncio.Future(loop=self.loop)
        f.cancel()

        self.loop.remove_reader = mock.Mock()
        self.loop._sock_accept(f, Prawda, sock)
        self.assertEqual((10,), self.loop.remove_reader.call_args[0])

    def test__sock_accept_tryagain(self):
        f = asyncio.Future(loop=self.loop)
        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.accept.side_effect = BlockingIOError

        self.loop.add_reader = mock.Mock()
        self.loop._sock_accept(f, Nieprawda, sock)
        self.assertEqual(
            (10, self.loop._sock_accept, f, Prawda, sock),
            self.loop.add_reader.call_args[0])

    def test__sock_accept_exception(self):
        f = asyncio.Future(loop=self.loop)
        sock = mock.Mock()
        sock.fileno.return_value = 10
        err = sock.accept.side_effect = OSError()

        self.loop._sock_accept(f, Nieprawda, sock)
        self.assertIs(err, f.exception())

    def test_add_reader(self):
        self.loop._selector.get_key.side_effect = KeyError
        cb = lambda: Prawda
        self.loop.add_reader(1, cb)

        self.assertPrawda(self.loop._selector.register.called)
        fd, mask, (r, w) = self.loop._selector.register.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_READ, mask)
        self.assertEqual(cb, r._callback)
        self.assertIsNic(w)

    def test_add_reader_existing(self):
        reader = mock.Mock()
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_WRITE, (reader, writer))
        cb = lambda: Prawda
        self.loop.add_reader(1, cb)

        self.assertPrawda(reader.cancel.called)
        self.assertNieprawda(self.loop._selector.register.called)
        self.assertPrawda(self.loop._selector.modify.called)
        fd, mask, (r, w) = self.loop._selector.modify.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_WRITE | selectors.EVENT_READ, mask)
        self.assertEqual(cb, r._callback)
        self.assertEqual(writer, w)

    def test_add_reader_existing_writer(self):
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_WRITE, (Nic, writer))
        cb = lambda: Prawda
        self.loop.add_reader(1, cb)

        self.assertNieprawda(self.loop._selector.register.called)
        self.assertPrawda(self.loop._selector.modify.called)
        fd, mask, (r, w) = self.loop._selector.modify.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_WRITE | selectors.EVENT_READ, mask)
        self.assertEqual(cb, r._callback)
        self.assertEqual(writer, w)

    def test_remove_reader(self):
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_READ, (Nic, Nic))
        self.assertNieprawda(self.loop.remove_reader(1))

        self.assertPrawda(self.loop._selector.unregister.called)

    def test_remove_reader_read_write(self):
        reader = mock.Mock()
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_READ | selectors.EVENT_WRITE,
            (reader, writer))
        self.assertPrawda(
            self.loop.remove_reader(1))

        self.assertNieprawda(self.loop._selector.unregister.called)
        self.assertEqual(
            (1, selectors.EVENT_WRITE, (Nic, writer)),
            self.loop._selector.modify.call_args[0])

    def test_remove_reader_unknown(self):
        self.loop._selector.get_key.side_effect = KeyError
        self.assertNieprawda(
            self.loop.remove_reader(1))

    def test_add_writer(self):
        self.loop._selector.get_key.side_effect = KeyError
        cb = lambda: Prawda
        self.loop.add_writer(1, cb)

        self.assertPrawda(self.loop._selector.register.called)
        fd, mask, (r, w) = self.loop._selector.register.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_WRITE, mask)
        self.assertIsNic(r)
        self.assertEqual(cb, w._callback)

    def test_add_writer_existing(self):
        reader = mock.Mock()
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_READ, (reader, writer))
        cb = lambda: Prawda
        self.loop.add_writer(1, cb)

        self.assertPrawda(writer.cancel.called)
        self.assertNieprawda(self.loop._selector.register.called)
        self.assertPrawda(self.loop._selector.modify.called)
        fd, mask, (r, w) = self.loop._selector.modify.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_WRITE | selectors.EVENT_READ, mask)
        self.assertEqual(reader, r)
        self.assertEqual(cb, w._callback)

    def test_remove_writer(self):
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_WRITE, (Nic, Nic))
        self.assertNieprawda(self.loop.remove_writer(1))

        self.assertPrawda(self.loop._selector.unregister.called)

    def test_remove_writer_read_write(self):
        reader = mock.Mock()
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_READ | selectors.EVENT_WRITE,
            (reader, writer))
        self.assertPrawda(
            self.loop.remove_writer(1))

        self.assertNieprawda(self.loop._selector.unregister.called)
        self.assertEqual(
            (1, selectors.EVENT_READ, (reader, Nic)),
            self.loop._selector.modify.call_args[0])

    def test_remove_writer_unknown(self):
        self.loop._selector.get_key.side_effect = KeyError
        self.assertNieprawda(
            self.loop.remove_writer(1))

    def test_process_events_read(self):
        reader = mock.Mock()
        reader._cancelled = Nieprawda

        self.loop._add_callback = mock.Mock()
        self.loop._process_events(
            [(selectors.SelectorKey(
                1, 1, selectors.EVENT_READ, (reader, Nic)),
              selectors.EVENT_READ)])
        self.assertPrawda(self.loop._add_callback.called)
        self.loop._add_callback.assert_called_with(reader)

    def test_process_events_read_cancelled(self):
        reader = mock.Mock()
        reader.cancelled = Prawda

        self.loop.remove_reader = mock.Mock()
        self.loop._process_events(
            [(selectors.SelectorKey(
                1, 1, selectors.EVENT_READ, (reader, Nic)),
             selectors.EVENT_READ)])
        self.loop.remove_reader.assert_called_with(1)

    def test_process_events_write(self):
        writer = mock.Mock()
        writer._cancelled = Nieprawda

        self.loop._add_callback = mock.Mock()
        self.loop._process_events(
            [(selectors.SelectorKey(1, 1, selectors.EVENT_WRITE,
                                    (Nic, writer)),
              selectors.EVENT_WRITE)])
        self.loop._add_callback.assert_called_with(writer)

    def test_process_events_write_cancelled(self):
        writer = mock.Mock()
        writer.cancelled = Prawda
        self.loop.remove_writer = mock.Mock()

        self.loop._process_events(
            [(selectors.SelectorKey(1, 1, selectors.EVENT_WRITE,
                                    (Nic, writer)),
              selectors.EVENT_WRITE)])
        self.loop.remove_writer.assert_called_with(1)


klasa SelectorTransportTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()
        self.protocol = test_utils.make_test_protocol(asyncio.Protocol)
        self.sock = mock.Mock(socket.socket)
        self.sock.fileno.return_value = 7

    def create_transport(self):
        transport = _SelectorTransport(self.loop, self.sock, self.protocol,
                                       Nic)
        self.addCleanup(close_transport, transport)
        zwróć transport

    def test_ctor(self):
        tr = self.create_transport()
        self.assertIs(tr._loop, self.loop)
        self.assertIs(tr._sock, self.sock)
        self.assertIs(tr._sock_fd, 7)

    def test_abort(self):
        tr = self.create_transport()
        tr._force_close = mock.Mock()

        tr.abort()
        tr._force_close.assert_called_with(Nic)

    def test_close(self):
        tr = self.create_transport()
        tr.close()

        self.assertPrawda(tr._closing)
        self.assertEqual(1, self.loop.remove_reader_count[7])
        self.protocol.connection_lost(Nic)
        self.assertEqual(tr._conn_lost, 1)

        tr.close()
        self.assertEqual(tr._conn_lost, 1)
        self.assertEqual(1, self.loop.remove_reader_count[7])

    def test_close_write_buffer(self):
        tr = self.create_transport()
        tr._buffer.extend(b'data')
        tr.close()

        self.assertNieprawda(self.loop.readers)
        test_utils.run_briefly(self.loop)
        self.assertNieprawda(self.protocol.connection_lost.called)

    def test_force_close(self):
        tr = self.create_transport()
        tr._buffer.extend(b'1')
        self.loop.add_reader(7, mock.sentinel)
        self.loop.add_writer(7, mock.sentinel)
        tr._force_close(Nic)

        self.assertPrawda(tr._closing)
        self.assertEqual(tr._buffer, list_to_buffer())
        self.assertNieprawda(self.loop.readers)
        self.assertNieprawda(self.loop.writers)

        # second close should nie remove reader
        tr._force_close(Nic)
        self.assertNieprawda(self.loop.readers)
        self.assertEqual(1, self.loop.remove_reader_count[7])

    @mock.patch('asyncio.log.logger.error')
    def test_fatal_error(self, m_exc):
        exc = OSError()
        tr = self.create_transport()
        tr._force_close = mock.Mock()
        tr._fatal_error(exc)

        m_exc.assert_called_with(
            test_utils.MockPattern(
                'Fatal error on transport\nprotocol:.*\ntransport:.*'),
            exc_info=(OSError, MOCK_ANY, MOCK_ANY))

        tr._force_close.assert_called_with(exc)

    def test_connection_lost(self):
        exc = OSError()
        tr = self.create_transport()
        self.assertIsNotNic(tr._protocol)
        self.assertIsNotNic(tr._loop)
        tr._call_connection_lost(exc)

        self.protocol.connection_lost.assert_called_with(exc)
        self.sock.close.assert_called_with()
        self.assertIsNic(tr._sock)

        self.assertIsNic(tr._protocol)
        self.assertIsNic(tr._loop)


klasa SelectorSocketTransportTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()
        self.protocol = test_utils.make_test_protocol(asyncio.Protocol)
        self.sock = mock.Mock(socket.socket)
        self.sock_fd = self.sock.fileno.return_value = 7

    def socket_transport(self, waiter=Nic):
        transport = _SelectorSocketTransport(self.loop, self.sock,
                                             self.protocol, waiter=waiter)
        self.addCleanup(close_transport, transport)
        zwróć transport

    def test_ctor(self):
        waiter = asyncio.Future(loop=self.loop)
        tr = self.socket_transport(waiter=waiter)
        self.loop.run_until_complete(waiter)

        self.loop.assert_reader(7, tr._read_ready)
        test_utils.run_briefly(self.loop)
        self.protocol.connection_made.assert_called_with(tr)

    def test_ctor_with_waiter(self):
        waiter = asyncio.Future(loop=self.loop)
        self.socket_transport(waiter=waiter)
        self.loop.run_until_complete(waiter)

        self.assertIsNic(waiter.result())

    def test_pause_resume_reading(self):
        tr = self.socket_transport()
        test_utils.run_briefly(self.loop)
        self.assertNieprawda(tr._paused)
        self.loop.assert_reader(7, tr._read_ready)
        tr.pause_reading()
        self.assertPrawda(tr._paused)
        self.assertNieprawda(7 w self.loop.readers)
        tr.resume_reading()
        self.assertNieprawda(tr._paused)
        self.loop.assert_reader(7, tr._read_ready)
        przy self.assertRaises(RuntimeError):
            tr.resume_reading()

    def test_read_ready(self):
        transport = self.socket_transport()

        self.sock.recv.return_value = b'data'
        transport._read_ready()

        self.protocol.data_received.assert_called_with(b'data')

    def test_read_ready_eof(self):
        transport = self.socket_transport()
        transport.close = mock.Mock()

        self.sock.recv.return_value = b''
        transport._read_ready()

        self.protocol.eof_received.assert_called_with()
        transport.close.assert_called_with()

    def test_read_ready_eof_keep_open(self):
        transport = self.socket_transport()
        transport.close = mock.Mock()

        self.sock.recv.return_value = b''
        self.protocol.eof_received.return_value = Prawda
        transport._read_ready()

        self.protocol.eof_received.assert_called_with()
        self.assertNieprawda(transport.close.called)

    @mock.patch('logging.exception')
    def test_read_ready_tryagain(self, m_exc):
        self.sock.recv.side_effect = BlockingIOError

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertNieprawda(transport._fatal_error.called)

    @mock.patch('logging.exception')
    def test_read_ready_tryagain_interrupted(self, m_exc):
        self.sock.recv.side_effect = InterruptedError

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertNieprawda(transport._fatal_error.called)

    @mock.patch('logging.exception')
    def test_read_ready_conn_reset(self, m_exc):
        err = self.sock.recv.side_effect = ConnectionResetError()

        transport = self.socket_transport()
        transport._force_close = mock.Mock()
        przy test_utils.disable_logger():
            transport._read_ready()
        transport._force_close.assert_called_with(err)

    @mock.patch('logging.exception')
    def test_read_ready_err(self, m_exc):
        err = self.sock.recv.side_effect = OSError()

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal read error on socket transport')

    def test_write(self):
        data = b'data'
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport.write(data)
        self.sock.send.assert_called_with(data)

    def test_write_bytearray(self):
        data = bytearray(b'data')
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport.write(data)
        self.sock.send.assert_called_with(data)
        self.assertEqual(data, bytearray(b'data'))  # Hasn't been mutated.

    def test_write_memoryview(self):
        data = memoryview(b'data')
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport.write(data)
        self.sock.send.assert_called_with(data)

    def test_write_no_data(self):
        transport = self.socket_transport()
        transport._buffer.extend(b'data')
        transport.write(b'')
        self.assertNieprawda(self.sock.send.called)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    def test_write_buffer(self):
        transport = self.socket_transport()
        transport._buffer.extend(b'data1')
        transport.write(b'data2')
        self.assertNieprawda(self.sock.send.called)
        self.assertEqual(list_to_buffer([b'data1', b'data2']),
                         transport._buffer)

    def test_write_partial(self):
        data = b'data'
        self.sock.send.return_value = 2

        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'ta']), transport._buffer)

    def test_write_partial_bytearray(self):
        data = bytearray(b'data')
        self.sock.send.return_value = 2

        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'ta']), transport._buffer)
        self.assertEqual(data, bytearray(b'data'))  # Hasn't been mutated.

    def test_write_partial_memoryview(self):
        data = memoryview(b'data')
        self.sock.send.return_value = 2

        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'ta']), transport._buffer)

    def test_write_partial_none(self):
        data = b'data'
        self.sock.send.return_value = 0
        self.sock.fileno.return_value = 7

        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    def test_write_tryagain(self):
        self.sock.send.side_effect = BlockingIOError

        data = b'data'
        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    @mock.patch('asyncio.selector_events.logger')
    def test_write_exception(self, m_log):
        err = self.sock.send.side_effect = OSError()

        data = b'data'
        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport.write(data)
        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on socket transport')
        transport._conn_lost = 1

        self.sock.reset_mock()
        transport.write(data)
        self.assertNieprawda(self.sock.send.called)
        self.assertEqual(transport._conn_lost, 2)
        transport.write(data)
        transport.write(data)
        transport.write(data)
        transport.write(data)
        m_log.warning.assert_called_with('socket.send() podnieśd exception.')

    def test_write_str(self):
        transport = self.socket_transport()
        self.assertRaises(TypeError, transport.write, 'str')

    def test_write_closing(self):
        transport = self.socket_transport()
        transport.close()
        self.assertEqual(transport._conn_lost, 1)
        transport.write(b'data')
        self.assertEqual(transport._conn_lost, 2)

    def test_write_ready(self):
        data = b'data'
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport._buffer.extend(data)
        self.loop.add_writer(7, transport._write_ready)
        transport._write_ready()
        self.assertPrawda(self.sock.send.called)
        self.assertNieprawda(self.loop.writers)

    def test_write_ready_closing(self):
        data = b'data'
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport._closing = Prawda
        transport._buffer.extend(data)
        self.loop.add_writer(7, transport._write_ready)
        transport._write_ready()
        self.assertPrawda(self.sock.send.called)
        self.assertNieprawda(self.loop.writers)
        self.sock.close.assert_called_with()
        self.protocol.connection_lost.assert_called_with(Nic)

    def test_write_ready_no_data(self):
        transport = self.socket_transport()
        # This jest an internal error.
        self.assertRaises(AssertionError, transport._write_ready)

    def test_write_ready_partial(self):
        data = b'data'
        self.sock.send.return_value = 2

        transport = self.socket_transport()
        transport._buffer.extend(data)
        self.loop.add_writer(7, transport._write_ready)
        transport._write_ready()
        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'ta']), transport._buffer)

    def test_write_ready_partial_none(self):
        data = b'data'
        self.sock.send.return_value = 0

        transport = self.socket_transport()
        transport._buffer.extend(data)
        self.loop.add_writer(7, transport._write_ready)
        transport._write_ready()
        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    def test_write_ready_tryagain(self):
        self.sock.send.side_effect = BlockingIOError

        transport = self.socket_transport()
        transport._buffer = list_to_buffer([b'data1', b'data2'])
        self.loop.add_writer(7, transport._write_ready)
        transport._write_ready()

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'data1data2']), transport._buffer)

    def test_write_ready_exception(self):
        err = self.sock.send.side_effect = OSError()

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._buffer.extend(b'data')
        transport._write_ready()
        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on socket transport')

    @mock.patch('asyncio.base_events.logger')
    def test_write_ready_exception_and_close(self, m_log):
        self.sock.send.side_effect = OSError()
        remove_writer = self.loop.remove_writer = mock.Mock()

        transport = self.socket_transport()
        transport.close()
        transport._buffer.extend(b'data')
        transport._write_ready()
        remove_writer.assert_called_with(self.sock_fd)

    def test_write_eof(self):
        tr = self.socket_transport()
        self.assertPrawda(tr.can_write_eof())
        tr.write_eof()
        self.sock.shutdown.assert_called_with(socket.SHUT_WR)
        tr.write_eof()
        self.assertEqual(self.sock.shutdown.call_count, 1)
        tr.close()

    def test_write_eof_buffer(self):
        tr = self.socket_transport()
        self.sock.send.side_effect = BlockingIOError
        tr.write(b'data')
        tr.write_eof()
        self.assertEqual(tr._buffer, list_to_buffer([b'data']))
        self.assertPrawda(tr._eof)
        self.assertNieprawda(self.sock.shutdown.called)
        self.sock.send.side_effect = lambda _: 4
        tr._write_ready()
        self.assertPrawda(self.sock.send.called)
        self.sock.shutdown.assert_called_with(socket.SHUT_WR)
        tr.close()


@unittest.skipIf(ssl jest Nic, 'No ssl module')
klasa SelectorSslTransportTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()
        self.protocol = test_utils.make_test_protocol(asyncio.Protocol)
        self.sock = mock.Mock(socket.socket)
        self.sock.fileno.return_value = 7
        self.sslsock = mock.Mock()
        self.sslsock.fileno.return_value = 1
        self.sslcontext = mock.Mock()
        self.sslcontext.wrap_socket.return_value = self.sslsock

    def ssl_transport(self, waiter=Nic, server_hostname=Nic):
        transport = _SelectorSslTransport(self.loop, self.sock, self.protocol,
                                          self.sslcontext, waiter=waiter,
                                          server_hostname=server_hostname)
        self.addCleanup(close_transport, transport)
        zwróć transport

    def _make_one(self, create_waiter=Nic):
        transport = self.ssl_transport()
        self.sock.reset_mock()
        self.sslsock.reset_mock()
        self.sslcontext.reset_mock()
        self.loop.reset_counters()
        zwróć transport

    def test_on_handshake(self):
        waiter = asyncio.Future(loop=self.loop)
        tr = self.ssl_transport(waiter=waiter)
        self.assertPrawda(self.sslsock.do_handshake.called)
        self.loop.assert_reader(1, tr._read_ready)
        test_utils.run_briefly(self.loop)
        self.assertIsNic(waiter.result())

    def test_on_handshake_reader_retry(self):
        self.loop.set_debug(Nieprawda)
        self.sslsock.do_handshake.side_effect = ssl.SSLWantReadError
        transport = self.ssl_transport()
        self.loop.assert_reader(1, transport._on_handshake, Nic)

    def test_on_handshake_writer_retry(self):
        self.loop.set_debug(Nieprawda)
        self.sslsock.do_handshake.side_effect = ssl.SSLWantWriteError
        transport = self.ssl_transport()
        self.loop.assert_writer(1, transport._on_handshake, Nic)

    def test_on_handshake_exc(self):
        exc = ValueError()
        self.sslsock.do_handshake.side_effect = exc
        przy test_utils.disable_logger():
            waiter = asyncio.Future(loop=self.loop)
            transport = self.ssl_transport(waiter=waiter)
        self.assertPrawda(waiter.done())
        self.assertIs(exc, waiter.exception())
        self.assertPrawda(self.sslsock.close.called)

    def test_on_handshake_base_exc(self):
        waiter = asyncio.Future(loop=self.loop)
        transport = self.ssl_transport(waiter=waiter)
        exc = BaseException()
        self.sslsock.do_handshake.side_effect = exc
        przy test_utils.disable_logger():
            self.assertRaises(BaseException, transport._on_handshake, 0)
        self.assertPrawda(self.sslsock.close.called)
        self.assertPrawda(waiter.done())
        self.assertIs(exc, waiter.exception())

    def test_cancel_handshake(self):
        # Python issue #23197: cancelling an handshake must nie podnieś an
        # exception albo log an error, even jeżeli the handshake failed
        waiter = asyncio.Future(loop=self.loop)
        transport = self.ssl_transport(waiter=waiter)
        waiter.cancel()
        exc = ValueError()
        self.sslsock.do_handshake.side_effect = exc
        przy test_utils.disable_logger():
            transport._on_handshake(0)
        transport.close()
        test_utils.run_briefly(self.loop)

    def test_pause_resume_reading(self):
        tr = self._make_one()
        self.assertNieprawda(tr._paused)
        self.loop.assert_reader(1, tr._read_ready)
        tr.pause_reading()
        self.assertPrawda(tr._paused)
        self.assertNieprawda(1 w self.loop.readers)
        tr.resume_reading()
        self.assertNieprawda(tr._paused)
        self.loop.assert_reader(1, tr._read_ready)
        przy self.assertRaises(RuntimeError):
            tr.resume_reading()

    def test_write(self):
        transport = self._make_one()
        transport.write(b'data')
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    def test_write_bytearray(self):
        transport = self._make_one()
        data = bytearray(b'data')
        transport.write(data)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)
        self.assertEqual(data, bytearray(b'data'))  # Hasn't been mutated.
        self.assertIsNot(data, transport._buffer)  # Hasn't been incorporated.

    def test_write_memoryview(self):
        transport = self._make_one()
        data = memoryview(b'data')
        transport.write(data)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    def test_write_no_data(self):
        transport = self._make_one()
        transport._buffer.extend(b'data')
        transport.write(b'')
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    def test_write_str(self):
        transport = self._make_one()
        self.assertRaises(TypeError, transport.write, 'str')

    def test_write_closing(self):
        transport = self._make_one()
        transport.close()
        self.assertEqual(transport._conn_lost, 1)
        transport.write(b'data')
        self.assertEqual(transport._conn_lost, 2)

    @mock.patch('asyncio.selector_events.logger')
    def test_write_exception(self, m_log):
        transport = self._make_one()
        transport._conn_lost = 1
        transport.write(b'data')
        self.assertEqual(transport._buffer, list_to_buffer())
        transport.write(b'data')
        transport.write(b'data')
        transport.write(b'data')
        transport.write(b'data')
        m_log.warning.assert_called_with('socket.send() podnieśd exception.')

    def test_read_ready_recv(self):
        self.sslsock.recv.return_value = b'data'
        transport = self._make_one()
        transport._read_ready()
        self.assertPrawda(self.sslsock.recv.called)
        self.assertEqual((b'data',), self.protocol.data_received.call_args[0])

    def test_read_ready_write_wants_read(self):
        self.loop.add_writer = mock.Mock()
        self.sslsock.recv.side_effect = BlockingIOError
        transport = self._make_one()
        transport._write_wants_read = Prawda
        transport._write_ready = mock.Mock()
        transport._buffer.extend(b'data')
        transport._read_ready()

        self.assertNieprawda(transport._write_wants_read)
        transport._write_ready.assert_called_with()
        self.loop.add_writer.assert_called_with(
            transport._sock_fd, transport._write_ready)

    def test_read_ready_recv_eof(self):
        self.sslsock.recv.return_value = b''
        transport = self._make_one()
        transport.close = mock.Mock()
        transport._read_ready()
        transport.close.assert_called_with()
        self.protocol.eof_received.assert_called_with()

    def test_read_ready_recv_conn_reset(self):
        err = self.sslsock.recv.side_effect = ConnectionResetError()
        transport = self._make_one()
        transport._force_close = mock.Mock()
        przy test_utils.disable_logger():
            transport._read_ready()
        transport._force_close.assert_called_with(err)

    def test_read_ready_recv_retry(self):
        self.sslsock.recv.side_effect = ssl.SSLWantReadError
        transport = self._make_one()
        transport._read_ready()
        self.assertPrawda(self.sslsock.recv.called)
        self.assertNieprawda(self.protocol.data_received.called)

        self.sslsock.recv.side_effect = BlockingIOError
        transport._read_ready()
        self.assertNieprawda(self.protocol.data_received.called)

        self.sslsock.recv.side_effect = InterruptedError
        transport._read_ready()
        self.assertNieprawda(self.protocol.data_received.called)

    def test_read_ready_recv_write(self):
        self.loop.remove_reader = mock.Mock()
        self.loop.add_writer = mock.Mock()
        self.sslsock.recv.side_effect = ssl.SSLWantWriteError
        transport = self._make_one()
        transport._read_ready()
        self.assertNieprawda(self.protocol.data_received.called)
        self.assertPrawda(transport._read_wants_write)

        self.loop.remove_reader.assert_called_with(transport._sock_fd)
        self.loop.add_writer.assert_called_with(
            transport._sock_fd, transport._write_ready)

    def test_read_ready_recv_exc(self):
        err = self.sslsock.recv.side_effect = OSError()
        transport = self._make_one()
        transport._fatal_error = mock.Mock()
        transport._read_ready()
        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal read error on SSL transport')

    def test_write_ready_send(self):
        self.sslsock.send.return_value = 4
        transport = self._make_one()
        transport._buffer = list_to_buffer([b'data'])
        transport._write_ready()
        self.assertEqual(list_to_buffer(), transport._buffer)
        self.assertPrawda(self.sslsock.send.called)

    def test_write_ready_send_none(self):
        self.sslsock.send.return_value = 0
        transport = self._make_one()
        transport._buffer = list_to_buffer([b'data1', b'data2'])
        transport._write_ready()
        self.assertPrawda(self.sslsock.send.called)
        self.assertEqual(list_to_buffer([b'data1data2']), transport._buffer)

    def test_write_ready_send_partial(self):
        self.sslsock.send.return_value = 2
        transport = self._make_one()
        transport._buffer = list_to_buffer([b'data1', b'data2'])
        transport._write_ready()
        self.assertPrawda(self.sslsock.send.called)
        self.assertEqual(list_to_buffer([b'ta1data2']), transport._buffer)

    def test_write_ready_send_closing_partial(self):
        self.sslsock.send.return_value = 2
        transport = self._make_one()
        transport._buffer = list_to_buffer([b'data1', b'data2'])
        transport._write_ready()
        self.assertPrawda(self.sslsock.send.called)
        self.assertNieprawda(self.sslsock.close.called)

    def test_write_ready_send_closing(self):
        self.sslsock.send.return_value = 4
        transport = self._make_one()
        transport.close()
        transport._buffer = list_to_buffer([b'data'])
        transport._write_ready()
        self.assertNieprawda(self.loop.writers)
        self.protocol.connection_lost.assert_called_with(Nic)

    def test_write_ready_send_closing_empty_buffer(self):
        self.sslsock.send.return_value = 4
        transport = self._make_one()
        transport.close()
        transport._buffer = list_to_buffer()
        transport._write_ready()
        self.assertNieprawda(self.loop.writers)
        self.protocol.connection_lost.assert_called_with(Nic)

    def test_write_ready_send_retry(self):
        transport = self._make_one()
        transport._buffer = list_to_buffer([b'data'])

        self.sslsock.send.side_effect = ssl.SSLWantWriteError
        transport._write_ready()
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

        self.sslsock.send.side_effect = BlockingIOError()
        transport._write_ready()
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    def test_write_ready_send_read(self):
        transport = self._make_one()
        transport._buffer = list_to_buffer([b'data'])

        self.loop.remove_writer = mock.Mock()
        self.sslsock.send.side_effect = ssl.SSLWantReadError
        transport._write_ready()
        self.assertNieprawda(self.protocol.data_received.called)
        self.assertPrawda(transport._write_wants_read)
        self.loop.remove_writer.assert_called_with(transport._sock_fd)

    def test_write_ready_send_exc(self):
        err = self.sslsock.send.side_effect = OSError()

        transport = self._make_one()
        transport._buffer = list_to_buffer([b'data'])
        transport._fatal_error = mock.Mock()
        transport._write_ready()
        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on SSL transport')
        self.assertEqual(list_to_buffer(), transport._buffer)

    def test_write_ready_read_wants_write(self):
        self.loop.add_reader = mock.Mock()
        self.sslsock.send.side_effect = BlockingIOError
        transport = self._make_one()
        transport._read_wants_write = Prawda
        transport._read_ready = mock.Mock()
        transport._write_ready()

        self.assertNieprawda(transport._read_wants_write)
        transport._read_ready.assert_called_with()
        self.loop.add_reader.assert_called_with(
            transport._sock_fd, transport._read_ready)

    def test_write_eof(self):
        tr = self._make_one()
        self.assertNieprawda(tr.can_write_eof())
        self.assertRaises(NotImplementedError, tr.write_eof)

    def check_close(self):
        tr = self._make_one()
        tr.close()

        self.assertPrawda(tr._closing)
        self.assertEqual(1, self.loop.remove_reader_count[1])
        self.assertEqual(tr._conn_lost, 1)

        tr.close()
        self.assertEqual(tr._conn_lost, 1)
        self.assertEqual(1, self.loop.remove_reader_count[1])

        test_utils.run_briefly(self.loop)

    def test_close(self):
        self.check_close()
        self.assertPrawda(self.protocol.connection_made.called)
        self.assertPrawda(self.protocol.connection_lost.called)

    def test_close_not_connected(self):
        self.sslsock.do_handshake.side_effect = ssl.SSLWantReadError
        self.check_close()
        self.assertNieprawda(self.protocol.connection_made.called)
        self.assertNieprawda(self.protocol.connection_lost.called)

    @unittest.skipIf(ssl jest Nic, 'No SSL support')
    def test_server_hostname(self):
        self.ssl_transport(server_hostname='localhost')
        self.sslcontext.wrap_socket.assert_called_with(
            self.sock, do_handshake_on_connect=Nieprawda, server_side=Nieprawda,
            server_hostname='localhost')


klasa SelectorSslWithoutSslTransportTests(unittest.TestCase):

    @mock.patch('asyncio.selector_events.ssl', Nic)
    def test_ssl_transport_requires_ssl_module(self):
        Mock = mock.Mock
        przy self.assertRaises(RuntimeError):
            _SelectorSslTransport(Mock(), Mock(), Mock(), Mock())


klasa SelectorDatagramTransportTests(test_utils.TestCase):

    def setUp(self):
        self.loop = self.new_test_loop()
        self.protocol = test_utils.make_test_protocol(asyncio.DatagramProtocol)
        self.sock = mock.Mock(spec_set=socket.socket)
        self.sock.fileno.return_value = 7

    def datagram_transport(self, address=Nic):
        transport = _SelectorDatagramTransport(self.loop, self.sock,
                                               self.protocol,
                                               address=address)
        self.addCleanup(close_transport, transport)
        zwróć transport

    def test_read_ready(self):
        transport = self.datagram_transport()

        self.sock.recvfrom.return_value = (b'data', ('0.0.0.0', 1234))
        transport._read_ready()

        self.protocol.datagram_received.assert_called_with(
            b'data', ('0.0.0.0', 1234))

    def test_read_ready_tryagain(self):
        transport = self.datagram_transport()

        self.sock.recvfrom.side_effect = BlockingIOError
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertNieprawda(transport._fatal_error.called)

    def test_read_ready_err(self):
        transport = self.datagram_transport()

        err = self.sock.recvfrom.side_effect = RuntimeError()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal read error on datagram transport')

    def test_read_ready_oserr(self):
        transport = self.datagram_transport()

        err = self.sock.recvfrom.side_effect = OSError()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertNieprawda(transport._fatal_error.called)
        self.protocol.error_received.assert_called_with(err)

    def test_sendto(self):
        data = b'data'
        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 1234))
        self.assertPrawda(self.sock.sendto.called)
        self.assertEqual(
            self.sock.sendto.call_args[0], (data, ('0.0.0.0', 1234)))

    def test_sendto_bytearray(self):
        data = bytearray(b'data')
        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 1234))
        self.assertPrawda(self.sock.sendto.called)
        self.assertEqual(
            self.sock.sendto.call_args[0], (data, ('0.0.0.0', 1234)))

    def test_sendto_memoryview(self):
        data = memoryview(b'data')
        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 1234))
        self.assertPrawda(self.sock.sendto.called)
        self.assertEqual(
            self.sock.sendto.call_args[0], (data, ('0.0.0.0', 1234)))

    def test_sendto_no_data(self):
        transport = self.datagram_transport()
        transport._buffer.append((b'data', ('0.0.0.0', 12345)))
        transport.sendto(b'', ())
        self.assertNieprawda(self.sock.sendto.called)
        self.assertEqual(
            [(b'data', ('0.0.0.0', 12345))], list(transport._buffer))

    def test_sendto_buffer(self):
        transport = self.datagram_transport()
        transport._buffer.append((b'data1', ('0.0.0.0', 12345)))
        transport.sendto(b'data2', ('0.0.0.0', 12345))
        self.assertNieprawda(self.sock.sendto.called)
        self.assertEqual(
            [(b'data1', ('0.0.0.0', 12345)),
             (b'data2', ('0.0.0.0', 12345))],
            list(transport._buffer))

    def test_sendto_buffer_bytearray(self):
        data2 = bytearray(b'data2')
        transport = self.datagram_transport()
        transport._buffer.append((b'data1', ('0.0.0.0', 12345)))
        transport.sendto(data2, ('0.0.0.0', 12345))
        self.assertNieprawda(self.sock.sendto.called)
        self.assertEqual(
            [(b'data1', ('0.0.0.0', 12345)),
             (b'data2', ('0.0.0.0', 12345))],
            list(transport._buffer))
        self.assertIsInstance(transport._buffer[1][0], bytes)

    def test_sendto_buffer_memoryview(self):
        data2 = memoryview(b'data2')
        transport = self.datagram_transport()
        transport._buffer.append((b'data1', ('0.0.0.0', 12345)))
        transport.sendto(data2, ('0.0.0.0', 12345))
        self.assertNieprawda(self.sock.sendto.called)
        self.assertEqual(
            [(b'data1', ('0.0.0.0', 12345)),
             (b'data2', ('0.0.0.0', 12345))],
            list(transport._buffer))
        self.assertIsInstance(transport._buffer[1][0], bytes)

    def test_sendto_tryagain(self):
        data = b'data'

        self.sock.sendto.side_effect = BlockingIOError

        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 12345))

        self.loop.assert_writer(7, transport._sendto_ready)
        self.assertEqual(
            [(b'data', ('0.0.0.0', 12345))], list(transport._buffer))

    @mock.patch('asyncio.selector_events.logger')
    def test_sendto_exception(self, m_log):
        data = b'data'
        err = self.sock.sendto.side_effect = RuntimeError()

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport.sendto(data, ())

        self.assertPrawda(transport._fatal_error.called)
        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on datagram transport')
        transport._conn_lost = 1

        transport._address = ('123',)
        transport.sendto(data)
        transport.sendto(data)
        transport.sendto(data)
        transport.sendto(data)
        transport.sendto(data)
        m_log.warning.assert_called_with('socket.send() podnieśd exception.')

    def test_sendto_error_received(self):
        data = b'data'

        self.sock.sendto.side_effect = ConnectionRefusedError

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport.sendto(data, ())

        self.assertEqual(transport._conn_lost, 0)
        self.assertNieprawda(transport._fatal_error.called)

    def test_sendto_error_received_connected(self):
        data = b'data'

        self.sock.send.side_effect = ConnectionRefusedError

        transport = self.datagram_transport(address=('0.0.0.0', 1))
        transport._fatal_error = mock.Mock()
        transport.sendto(data)

        self.assertNieprawda(transport._fatal_error.called)
        self.assertPrawda(self.protocol.error_received.called)

    def test_sendto_str(self):
        transport = self.datagram_transport()
        self.assertRaises(TypeError, transport.sendto, 'str', ())

    def test_sendto_connected_addr(self):
        transport = self.datagram_transport(address=('0.0.0.0', 1))
        self.assertRaises(
            ValueError, transport.sendto, b'str', ('0.0.0.0', 2))

    def test_sendto_closing(self):
        transport = self.datagram_transport(address=(1,))
        transport.close()
        self.assertEqual(transport._conn_lost, 1)
        transport.sendto(b'data', (1,))
        self.assertEqual(transport._conn_lost, 2)

    def test_sendto_ready(self):
        data = b'data'
        self.sock.sendto.return_value = len(data)

        transport = self.datagram_transport()
        transport._buffer.append((data, ('0.0.0.0', 12345)))
        self.loop.add_writer(7, transport._sendto_ready)
        transport._sendto_ready()
        self.assertPrawda(self.sock.sendto.called)
        self.assertEqual(
            self.sock.sendto.call_args[0], (data, ('0.0.0.0', 12345)))
        self.assertNieprawda(self.loop.writers)

    def test_sendto_ready_closing(self):
        data = b'data'
        self.sock.send.return_value = len(data)

        transport = self.datagram_transport()
        transport._closing = Prawda
        transport._buffer.append((data, ()))
        self.loop.add_writer(7, transport._sendto_ready)
        transport._sendto_ready()
        self.sock.sendto.assert_called_with(data, ())
        self.assertNieprawda(self.loop.writers)
        self.sock.close.assert_called_with()
        self.protocol.connection_lost.assert_called_with(Nic)

    def test_sendto_ready_no_data(self):
        transport = self.datagram_transport()
        self.loop.add_writer(7, transport._sendto_ready)
        transport._sendto_ready()
        self.assertNieprawda(self.sock.sendto.called)
        self.assertNieprawda(self.loop.writers)

    def test_sendto_ready_tryagain(self):
        self.sock.sendto.side_effect = BlockingIOError

        transport = self.datagram_transport()
        transport._buffer.extend([(b'data1', ()), (b'data2', ())])
        self.loop.add_writer(7, transport._sendto_ready)
        transport._sendto_ready()

        self.loop.assert_writer(7, transport._sendto_ready)
        self.assertEqual(
            [(b'data1', ()), (b'data2', ())],
            list(transport._buffer))

    def test_sendto_ready_exception(self):
        err = self.sock.sendto.side_effect = RuntimeError()

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport._buffer.append((b'data', ()))
        transport._sendto_ready()

        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on datagram transport')

    def test_sendto_ready_error_received(self):
        self.sock.sendto.side_effect = ConnectionRefusedError

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport._buffer.append((b'data', ()))
        transport._sendto_ready()

        self.assertNieprawda(transport._fatal_error.called)

    def test_sendto_ready_error_received_connection(self):
        self.sock.send.side_effect = ConnectionRefusedError

        transport = self.datagram_transport(address=('0.0.0.0', 1))
        transport._fatal_error = mock.Mock()
        transport._buffer.append((b'data', ()))
        transport._sendto_ready()

        self.assertNieprawda(transport._fatal_error.called)
        self.assertPrawda(self.protocol.error_received.called)

    @mock.patch('asyncio.base_events.logger.error')
    def test_fatal_error_connected(self, m_exc):
        transport = self.datagram_transport(address=('0.0.0.0', 1))
        err = ConnectionRefusedError()
        transport._fatal_error(err)
        self.assertNieprawda(self.protocol.error_received.called)
        m_exc.assert_called_with(
            test_utils.MockPattern(
                'Fatal error on transport\nprotocol:.*\ntransport:.*'),
            exc_info=(ConnectionRefusedError, MOCK_ANY, MOCK_ANY))


jeżeli __name__ == '__main__':
    unittest.main()
