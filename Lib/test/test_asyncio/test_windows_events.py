zaimportuj os
zaimportuj sys
zaimportuj unittest
z unittest zaimportuj mock

jeżeli sys.platform != 'win32':
    podnieś unittest.SkipTest('Windows only')

zaimportuj _winapi

zaimportuj asyncio
z asyncio zaimportuj _overlapped
z asyncio zaimportuj test_utils
z asyncio zaimportuj windows_events


klasa UpperProto(asyncio.Protocol):
    def __init__(self):
        self.buf = []

    def connection_made(self, trans):
        self.trans = trans

    def data_received(self, data):
        self.buf.append(data)
        jeżeli b'\n' w data:
            self.trans.write(b''.join(self.buf).upper())
            self.trans.close()


klasa ProactorTests(test_utils.TestCase):

    def setUp(self):
        self.loop = asyncio.ProactorEventLoop()
        self.set_event_loop(self.loop)

    def test_close(self):
        a, b = self.loop._socketpair()
        trans = self.loop._make_socket_transport(a, asyncio.Protocol())
        f = asyncio.ensure_future(self.loop.sock_recv(b, 100))
        trans.close()
        self.loop.run_until_complete(f)
        self.assertEqual(f.result(), b'')
        b.close()

    def test_double_bind(self):
        ADDRESS = r'\\.\pipe\test_double_bind-%s' % os.getpid()
        server1 = windows_events.PipeServer(ADDRESS)
        przy self.assertRaises(PermissionError):
            windows_events.PipeServer(ADDRESS)
        server1.close()

    def test_pipe(self):
        res = self.loop.run_until_complete(self._test_pipe())
        self.assertEqual(res, 'done')

    def _test_pipe(self):
        ADDRESS = r'\\.\pipe\_test_pipe-%s' % os.getpid()

        przy self.assertRaises(FileNotFoundError):
            uzyskaj z self.loop.create_pipe_connection(
                asyncio.Protocol, ADDRESS)

        [server] = uzyskaj z self.loop.start_serving_pipe(
            UpperProto, ADDRESS)
        self.assertIsInstance(server, windows_events.PipeServer)

        clients = []
        dla i w range(5):
            stream_reader = asyncio.StreamReader(loop=self.loop)
            protocol = asyncio.StreamReaderProtocol(stream_reader,
                                                    loop=self.loop)
            trans, proto = uzyskaj z self.loop.create_pipe_connection(
                lambda: protocol, ADDRESS)
            self.assertIsInstance(trans, asyncio.Transport)
            self.assertEqual(protocol, proto)
            clients.append((stream_reader, trans))

        dla i, (r, w) w enumerate(clients):
            w.write('lower-{}\n'.format(i).encode())

        dla i, (r, w) w enumerate(clients):
            response = uzyskaj z r.readline()
            self.assertEqual(response, 'LOWER-{}\n'.format(i).encode())
            w.close()

        server.close()

        przy self.assertRaises(FileNotFoundError):
            uzyskaj z self.loop.create_pipe_connection(
                asyncio.Protocol, ADDRESS)

        zwróć 'done'

    def test_connect_pipe_cancel(self):
        exc = OSError()
        exc.winerror = _overlapped.ERROR_PIPE_BUSY
        przy mock.patch.object(_overlapped, 'ConnectPipe', side_effect=exc) jako connect:
            coro = self.loop._proactor.connect_pipe('pipe_address')
            task = self.loop.create_task(coro)

            # check that it's possible to cancel connect_pipe()
            task.cancel()
            przy self.assertRaises(asyncio.CancelledError):
                self.loop.run_until_complete(task)

    def test_wait_for_handle(self):
        event = _overlapped.CreateEvent(Nic, Prawda, Nieprawda, Nic)
        self.addCleanup(_winapi.CloseHandle, event)

        # Wait dla unset event przy 0.5s timeout;
        # result should be Nieprawda at timeout
        fut = self.loop._proactor.wait_for_handle(event, 0.5)
        start = self.loop.time()
        done = self.loop.run_until_complete(fut)
        elapsed = self.loop.time() - start

        self.assertEqual(done, Nieprawda)
        self.assertNieprawda(fut.result())
        self.assertPrawda(0.48 < elapsed < 0.9, elapsed)

        _overlapped.SetEvent(event)

        # Wait dla set event;
        # result should be Prawda immediately
        fut = self.loop._proactor.wait_for_handle(event, 10)
        start = self.loop.time()
        done = self.loop.run_until_complete(fut)
        elapsed = self.loop.time() - start

        self.assertEqual(done, Prawda)
        self.assertPrawda(fut.result())
        self.assertPrawda(0 <= elapsed < 0.3, elapsed)

        # asyncio issue #195: cancelling a done _WaitHandleFuture
        # must nie crash
        fut.cancel()

    def test_wait_for_handle_cancel(self):
        event = _overlapped.CreateEvent(Nic, Prawda, Nieprawda, Nic)
        self.addCleanup(_winapi.CloseHandle, event)

        # Wait dla unset event przy a cancelled future;
        # CancelledError should be podnieśd immediately
        fut = self.loop._proactor.wait_for_handle(event, 10)
        fut.cancel()
        start = self.loop.time()
        przy self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(fut)
        elapsed = self.loop.time() - start
        self.assertPrawda(0 <= elapsed < 0.1, elapsed)

        # asyncio issue #195: cancelling a _WaitHandleFuture twice
        # must nie crash
        fut = self.loop._proactor.wait_for_handle(event)
        fut.cancel()
        fut.cancel()


jeżeli __name__ == '__main__':
    unittest.main()
