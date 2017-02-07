"""Tests dla window_utils"""

zaimportuj socket
zaimportuj sys
zaimportuj unittest
zaimportuj warnings
z unittest zaimportuj mock

jeżeli sys.platform != 'win32':
    podnieś unittest.SkipTest('Windows only')

zaimportuj _winapi

z asyncio zaimportuj _overlapped
z asyncio zaimportuj windows_utils
spróbuj:
    z test zaimportuj support
wyjąwszy ImportError:
    z asyncio zaimportuj test_support jako support


klasa WinsocketpairTests(unittest.TestCase):

    def check_winsocketpair(self, ssock, csock):
        csock.send(b'xxx')
        self.assertEqual(b'xxx', ssock.recv(1024))
        csock.close()
        ssock.close()

    def test_winsocketpair(self):
        ssock, csock = windows_utils.socketpair()
        self.check_winsocketpair(ssock, csock)

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 nie supported albo enabled')
    def test_winsocketpair_ipv6(self):
        ssock, csock = windows_utils.socketpair(family=socket.AF_INET6)
        self.check_winsocketpair(ssock, csock)

    @unittest.skipIf(hasattr(socket, 'socketpair'),
                     'socket.socketpair jest available')
    @mock.patch('asyncio.windows_utils.socket')
    def test_winsocketpair_exc(self, m_socket):
        m_socket.AF_INET = socket.AF_INET
        m_socket.SOCK_STREAM = socket.SOCK_STREAM
        m_socket.socket.return_value.getsockname.return_value = ('', 12345)
        m_socket.socket.return_value.accept.return_value = object(), object()
        m_socket.socket.return_value.connect.side_effect = OSError()

        self.assertRaises(OSError, windows_utils.socketpair)

    def test_winsocketpair_invalid_args(self):
        self.assertRaises(ValueError,
                          windows_utils.socketpair, family=socket.AF_UNSPEC)
        self.assertRaises(ValueError,
                          windows_utils.socketpair, type=socket.SOCK_DGRAM)
        self.assertRaises(ValueError,
                          windows_utils.socketpair, proto=1)

    @unittest.skipIf(hasattr(socket, 'socketpair'),
                     'socket.socketpair jest available')
    @mock.patch('asyncio.windows_utils.socket')
    def test_winsocketpair_close(self, m_socket):
        m_socket.AF_INET = socket.AF_INET
        m_socket.SOCK_STREAM = socket.SOCK_STREAM
        sock = mock.Mock()
        m_socket.socket.return_value = sock
        sock.bind.side_effect = OSError
        self.assertRaises(OSError, windows_utils.socketpair)
        self.assertPrawda(sock.close.called)


klasa PipeTests(unittest.TestCase):

    def test_pipe_overlapped(self):
        h1, h2 = windows_utils.pipe(overlapped=(Prawda, Prawda))
        spróbuj:
            ov1 = _overlapped.Overlapped()
            self.assertNieprawda(ov1.pending)
            self.assertEqual(ov1.error, 0)

            ov1.ReadFile(h1, 100)
            self.assertPrawda(ov1.pending)
            self.assertEqual(ov1.error, _winapi.ERROR_IO_PENDING)
            ERROR_IO_INCOMPLETE = 996
            spróbuj:
                ov1.getresult()
            wyjąwszy OSError jako e:
                self.assertEqual(e.winerror, ERROR_IO_INCOMPLETE)
            inaczej:
                podnieś RuntimeError('expected ERROR_IO_INCOMPLETE')

            ov2 = _overlapped.Overlapped()
            self.assertNieprawda(ov2.pending)
            self.assertEqual(ov2.error, 0)

            ov2.WriteFile(h2, b"hello")
            self.assertIn(ov2.error, {0, _winapi.ERROR_IO_PENDING})

            res = _winapi.WaitForMultipleObjects([ov2.event], Nieprawda, 100)
            self.assertEqual(res, _winapi.WAIT_OBJECT_0)

            self.assertNieprawda(ov1.pending)
            self.assertEqual(ov1.error, ERROR_IO_INCOMPLETE)
            self.assertNieprawda(ov2.pending)
            self.assertIn(ov2.error, {0, _winapi.ERROR_IO_PENDING})
            self.assertEqual(ov1.getresult(), b"hello")
        w_końcu:
            _winapi.CloseHandle(h1)
            _winapi.CloseHandle(h2)

    def test_pipe_handle(self):
        h, _ = windows_utils.pipe(overlapped=(Prawda, Prawda))
        _winapi.CloseHandle(_)
        p = windows_utils.PipeHandle(h)
        self.assertEqual(p.fileno(), h)
        self.assertEqual(p.handle, h)

        # check garbage collection of p closes handle
        przy warnings.catch_warnings():
            warnings.filterwarnings("ignore", "",  ResourceWarning)
            usuń p
            support.gc_collect()
        spróbuj:
            _winapi.CloseHandle(h)
        wyjąwszy OSError jako e:
            self.assertEqual(e.winerror, 6)     # ERROR_INVALID_HANDLE
        inaczej:
            podnieś RuntimeError('expected ERROR_INVALID_HANDLE')


klasa PopenTests(unittest.TestCase):

    def test_popen(self):
        command = r"""jeżeli 1:
            zaimportuj sys
            s = sys.stdin.readline()
            sys.stdout.write(s.upper())
            sys.stderr.write('stderr')
            """
        msg = b"blah\n"

        p = windows_utils.Popen([sys.executable, '-c', command],
                                stdin=windows_utils.PIPE,
                                stdout=windows_utils.PIPE,
                                stderr=windows_utils.PIPE)

        dla f w [p.stdin, p.stdout, p.stderr]:
            self.assertIsInstance(f, windows_utils.PipeHandle)

        ovin = _overlapped.Overlapped()
        ovout = _overlapped.Overlapped()
        overr = _overlapped.Overlapped()

        ovin.WriteFile(p.stdin.handle, msg)
        ovout.ReadFile(p.stdout.handle, 100)
        overr.ReadFile(p.stderr.handle, 100)

        events = [ovin.event, ovout.event, overr.event]
        # Super-long timeout dla slow buildbots.
        res = _winapi.WaitForMultipleObjects(events, Prawda, 10000)
        self.assertEqual(res, _winapi.WAIT_OBJECT_0)
        self.assertNieprawda(ovout.pending)
        self.assertNieprawda(overr.pending)
        self.assertNieprawda(ovin.pending)

        self.assertEqual(ovin.getresult(), len(msg))
        out = ovout.getresult().rstrip()
        err = overr.getresult().rstrip()

        self.assertGreater(len(out), 0)
        self.assertGreater(len(err), 0)
        # allow dla partial reads...
        self.assertPrawda(msg.upper().rstrip().startswith(out))
        self.assertPrawda(b"stderr".startswith(err))

        # The context manager calls wait() oraz closes resources
        przy p:
            dalej


jeżeli __name__ == '__main__':
    unittest.main()
