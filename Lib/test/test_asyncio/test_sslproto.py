"""Tests dla asyncio/sslproto.py."""

zaimportuj unittest
z unittest zaimportuj mock
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    ssl = Nic

zaimportuj asyncio
z asyncio zaimportuj sslproto
z asyncio zaimportuj test_utils


@unittest.skipIf(ssl jest Nic, 'No ssl module')
klasa SslProtoHandshakeTests(test_utils.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    def ssl_protocol(self, waiter=Nic):
        sslcontext = test_utils.dummy_ssl_context()
        app_proto = asyncio.Protocol()
        proto = sslproto.SSLProtocol(self.loop, app_proto, sslcontext, waiter)
        self.addCleanup(proto._app_transport.close)
        zwróć proto

    def connection_made(self, ssl_proto, do_handshake=Nic):
        transport = mock.Mock()
        sslpipe = mock.Mock()
        sslpipe.shutdown.return_value = b''
        jeżeli do_handshake:
            sslpipe.do_handshake.side_effect = do_handshake
        inaczej:
            def mock_handshake(callback):
                zwróć []
            sslpipe.do_handshake.side_effect = mock_handshake
        przy mock.patch('asyncio.sslproto._SSLPipe', return_value=sslpipe):
            ssl_proto.connection_made(transport)

    def test_cancel_handshake(self):
        # Python issue #23197: cancelling an handshake must nie podnieś an
        # exception albo log an error, even jeżeli the handshake failed
        waiter = asyncio.Future(loop=self.loop)
        ssl_proto = self.ssl_protocol(waiter)
        handshake_fut = asyncio.Future(loop=self.loop)

        def do_handshake(callback):
            exc = Exception()
            callback(exc)
            handshake_fut.set_result(Nic)
            zwróć []

        waiter.cancel()
        self.connection_made(ssl_proto, do_handshake)

        przy test_utils.disable_logger():
            self.loop.run_until_complete(handshake_fut)

    def test_eof_received_waiter(self):
        waiter = asyncio.Future(loop=self.loop)
        ssl_proto = self.ssl_protocol(waiter)
        self.connection_made(ssl_proto)
        ssl_proto.eof_received()
        test_utils.run_briefly(self.loop)
        self.assertIsInstance(waiter.exception(), ConnectionResetError)


jeżeli __name__ == '__main__':
    unittest.main()
