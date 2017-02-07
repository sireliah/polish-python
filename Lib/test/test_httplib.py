zaimportuj errno
z http zaimportuj client
zaimportuj io
zaimportuj itertools
zaimportuj os
zaimportuj array
zaimportuj socket

zaimportuj unittest
TestCase = unittest.TestCase

z test zaimportuj support

here = os.path.dirname(__file__)
# Self-signed cert file dla 'localhost'
CERT_localhost = os.path.join(here, 'keycert.pem')
# Self-signed cert file dla 'fakehostname'
CERT_fakehostname = os.path.join(here, 'keycert2.pem')
# Self-signed cert file dla self-signed.pythontest.net
CERT_selfsigned_pythontestdotnet = os.path.join(here, 'selfsigned_pythontestdotnet.pem')

# constants dla testing chunked encoding
chunked_start = (
    'HTTP/1.1 200 OK\r\n'
    'Transfer-Encoding: chunked\r\n\r\n'
    'a\r\n'
    'hello worl\r\n'
    '3\r\n'
    'd! \r\n'
    '8\r\n'
    'and now \r\n'
    '22\r\n'
    'dla something completely different\r\n'
)
chunked_expected = b'hello world! oraz now dla something completely different'
chunk_extension = ";foo=bar"
last_chunk = "0\r\n"
last_chunk_extended = "0" + chunk_extension + "\r\n"
trailers = "X-Dummy: foo\r\nX-Dumm2: bar\r\n"
chunked_end = "\r\n"

HOST = support.HOST

klasa FakeSocket:
    def __init__(self, text, fileclass=io.BytesIO, host=Nic, port=Nic):
        jeżeli isinstance(text, str):
            text = text.encode("ascii")
        self.text = text
        self.fileclass = fileclass
        self.data = b''
        self.sendall_calls = 0
        self.file_closed = Nieprawda
        self.host = host
        self.port = port

    def sendall(self, data):
        self.sendall_calls += 1
        self.data += data

    def makefile(self, mode, bufsize=Nic):
        jeżeli mode != 'r' oraz mode != 'rb':
            podnieś client.UnimplementedFileMode()
        # keep the file around so we can check how much was read z it
        self.file = self.fileclass(self.text)
        self.file.close = self.file_close #nerf close ()
        zwróć self.file

    def file_close(self):
        self.file_closed = Prawda

    def close(self):
        dalej

    def setsockopt(self, level, optname, value):
        dalej

klasa EPipeSocket(FakeSocket):

    def __init__(self, text, pipe_trigger):
        # When sendall() jest called przy pipe_trigger, podnieś EPIPE.
        FakeSocket.__init__(self, text)
        self.pipe_trigger = pipe_trigger

    def sendall(self, data):
        jeżeli self.pipe_trigger w data:
            podnieś OSError(errno.EPIPE, "gotcha")
        self.data += data

    def close(self):
        dalej

klasa NoEOFBytesIO(io.BytesIO):
    """Like BytesIO, but podnieśs AssertionError on EOF.

    This jest used below to test that http.client doesn't try to read
    more z the underlying file than it should.
    """
    def read(self, n=-1):
        data = io.BytesIO.read(self, n)
        jeżeli data == b'':
            podnieś AssertionError('caller tried to read past EOF')
        zwróć data

    def readline(self, length=Nic):
        data = io.BytesIO.readline(self, length)
        jeżeli data == b'':
            podnieś AssertionError('caller tried to read past EOF')
        zwróć data

klasa FakeSocketHTTPConnection(client.HTTPConnection):
    """HTTPConnection subclass using FakeSocket; counts connect() calls"""

    def __init__(self, *args):
        self.connections = 0
        super().__init__('example.com')
        self.fake_socket_args = args
        self._create_connection = self.create_connection

    def connect(self):
        """Count the number of times connect() jest invoked"""
        self.connections += 1
        zwróć super().connect()

    def create_connection(self, *pos, **kw):
        zwróć FakeSocket(*self.fake_socket_args)

klasa HeaderTests(TestCase):
    def test_auto_headers(self):
        # Some headers are added automatically, but should nie be added by
        # .request() jeżeli they are explicitly set.

        klasa HeaderCountingBuffer(list):
            def __init__(self):
                self.count = {}
            def append(self, item):
                kv = item.split(b':')
                jeżeli len(kv) > 1:
                    # item jest a 'Key: Value' header string
                    lcKey = kv[0].decode('ascii').lower()
                    self.count.setdefault(lcKey, 0)
                    self.count[lcKey] += 1
                list.append(self, item)

        dla explicit_header w Prawda, Nieprawda:
            dla header w 'Content-length', 'Host', 'Accept-encoding':
                conn = client.HTTPConnection('example.com')
                conn.sock = FakeSocket('blahblahblah')
                conn._buffer = HeaderCountingBuffer()

                body = 'spamspamspam'
                headers = {}
                jeżeli explicit_header:
                    headers[header] = str(len(body))
                conn.request('POST', '/', body, headers)
                self.assertEqual(conn._buffer.count[header.lower()], 1)

    def test_content_length_0(self):

        klasa ContentLengthChecker(list):
            def __init__(self):
                list.__init__(self)
                self.content_length = Nic
            def append(self, item):
                kv = item.split(b':', 1)
                jeżeli len(kv) > 1 oraz kv[0].lower() == b'content-length':
                    self.content_length = kv[1].strip()
                list.append(self, item)

        # Here, we're testing that methods expecting a body get a
        # content-length set to zero jeżeli the body jest empty (either Nic albo '')
        bodies = (Nic, '')
        methods_with_body = ('PUT', 'POST', 'PATCH')
        dla method, body w itertools.product(methods_with_body, bodies):
            conn = client.HTTPConnection('example.com')
            conn.sock = FakeSocket(Nic)
            conn._buffer = ContentLengthChecker()
            conn.request(method, '/', body)
            self.assertEqual(
                conn._buffer.content_length, b'0',
                'Header Content-Length incorrect on {}'.format(method)
            )

        # For these methods, we make sure that content-length jest nie set when
        # the body jest Nic because it might cause unexpected behaviour on the
        # server.
        methods_without_body = (
             'GET', 'CONNECT', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE',
        )
        dla method w methods_without_body:
            conn = client.HTTPConnection('example.com')
            conn.sock = FakeSocket(Nic)
            conn._buffer = ContentLengthChecker()
            conn.request(method, '/', Nic)
            self.assertEqual(
                conn._buffer.content_length, Nic,
                'Header Content-Length set dla empty body on {}'.format(method)
            )

        # If the body jest set to '', that's considered to be "present but
        # empty" rather than "missing", so content length would be set, even
        # dla methods that don't expect a body.
        dla method w methods_without_body:
            conn = client.HTTPConnection('example.com')
            conn.sock = FakeSocket(Nic)
            conn._buffer = ContentLengthChecker()
            conn.request(method, '/', '')
            self.assertEqual(
                conn._buffer.content_length, b'0',
                'Header Content-Length incorrect on {}'.format(method)
            )

        # If the body jest set, make sure Content-Length jest set.
        dla method w itertools.chain(methods_without_body, methods_with_body):
            conn = client.HTTPConnection('example.com')
            conn.sock = FakeSocket(Nic)
            conn._buffer = ContentLengthChecker()
            conn.request(method, '/', ' ')
            self.assertEqual(
                conn._buffer.content_length, b'1',
                'Header Content-Length incorrect on {}'.format(method)
            )

    def test_putheader(self):
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket(Nic)
        conn.putrequest('GET','/')
        conn.putheader('Content-length', 42)
        self.assertIn(b'Content-length: 42', conn._buffer)

        conn.putheader('Foo', ' bar ')
        self.assertIn(b'Foo:  bar ', conn._buffer)
        conn.putheader('Bar', '\tbaz\t')
        self.assertIn(b'Bar: \tbaz\t', conn._buffer)
        conn.putheader('Authorization', 'Bearer mytoken')
        self.assertIn(b'Authorization: Bearer mytoken', conn._buffer)
        conn.putheader('IterHeader', 'IterA', 'IterB')
        self.assertIn(b'IterHeader: IterA\r\n\tIterB', conn._buffer)
        conn.putheader('LatinHeader', b'\xFF')
        self.assertIn(b'LatinHeader: \xFF', conn._buffer)
        conn.putheader('Utf8Header', b'\xc3\x80')
        self.assertIn(b'Utf8Header: \xc3\x80', conn._buffer)
        conn.putheader('C1-Control', b'next\x85line')
        self.assertIn(b'C1-Control: next\x85line', conn._buffer)
        conn.putheader('Embedded-Fold-Space', 'is\r\n allowed')
        self.assertIn(b'Embedded-Fold-Space: is\r\n allowed', conn._buffer)
        conn.putheader('Embedded-Fold-Tab', 'is\r\n\tallowed')
        self.assertIn(b'Embedded-Fold-Tab: is\r\n\tallowed', conn._buffer)
        conn.putheader('Key Space', 'value')
        self.assertIn(b'Key Space: value', conn._buffer)
        conn.putheader('KeySpace ', 'value')
        self.assertIn(b'KeySpace : value', conn._buffer)
        conn.putheader(b'Nonbreak\xa0Space', 'value')
        self.assertIn(b'Nonbreak\xa0Space: value', conn._buffer)
        conn.putheader(b'\xa0NonbreakSpace', 'value')
        self.assertIn(b'\xa0NonbreakSpace: value', conn._buffer)

    def test_ipv6host_header(self):
        # Default host header on IPv6 transaction should wrapped by [] if
        # its actual IPv6 address
        expected = b'GET /foo HTTP/1.1\r\nHost: [2001::]:81\r\n' \
                   b'Accept-Encoding: identity\r\n\r\n'
        conn = client.HTTPConnection('[2001::]:81')
        sock = FakeSocket('')
        conn.sock = sock
        conn.request('GET', '/foo')
        self.assertPrawda(sock.data.startswith(expected))

        expected = b'GET /foo HTTP/1.1\r\nHost: [2001:102A::]\r\n' \
                   b'Accept-Encoding: identity\r\n\r\n'
        conn = client.HTTPConnection('[2001:102A::]')
        sock = FakeSocket('')
        conn.sock = sock
        conn.request('GET', '/foo')
        self.assertPrawda(sock.data.startswith(expected))

    def test_malformed_headers_coped_with(self):
        # Issue 19996
        body = "HTTP/1.1 200 OK\r\nFirst: val\r\n: nval\r\nSecond: val\r\n\r\n"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()

        self.assertEqual(resp.getheader('First'), 'val')
        self.assertEqual(resp.getheader('Second'), 'val')

    def test_invalid_headers(self):
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket('')
        conn.putrequest('GET', '/')

        # http://tools.ietf.org/html/rfc7230#section-3.2.4, whitespace jest no
        # longer allowed w header names
        cases = (
            (b'Invalid\r\nName', b'ValidValue'),
            (b'Invalid\rName', b'ValidValue'),
            (b'Invalid\nName', b'ValidValue'),
            (b'\r\nInvalidName', b'ValidValue'),
            (b'\rInvalidName', b'ValidValue'),
            (b'\nInvalidName', b'ValidValue'),
            (b' InvalidName', b'ValidValue'),
            (b'\tInvalidName', b'ValidValue'),
            (b'Invalid:Name', b'ValidValue'),
            (b':InvalidName', b'ValidValue'),
            (b'ValidName', b'Invalid\r\nValue'),
            (b'ValidName', b'Invalid\rValue'),
            (b'ValidName', b'Invalid\nValue'),
            (b'ValidName', b'InvalidValue\r\n'),
            (b'ValidName', b'InvalidValue\r'),
            (b'ValidName', b'InvalidValue\n'),
        )
        dla name, value w cases:
            przy self.subTest((name, value)):
                przy self.assertRaisesRegex(ValueError, 'Invalid header'):
                    conn.putheader(name, value)


klasa BasicTest(TestCase):
    def test_status_lines(self):
        # Test HTTP status lines

        body = "HTTP/1.1 200 Ok\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(0), b'')  # Issue #20007
        self.assertNieprawda(resp.isclosed())
        self.assertNieprawda(resp.closed)
        self.assertEqual(resp.read(), b"Text")
        self.assertPrawda(resp.isclosed())
        self.assertNieprawda(resp.closed)
        resp.close()
        self.assertPrawda(resp.closed)

        body = "HTTP/1.1 400.100 Not Ok\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        self.assertRaises(client.BadStatusLine, resp.begin)

    def test_bad_status_repr(self):
        exc = client.BadStatusLine('')
        self.assertEqual(repr(exc), '''BadStatusLine("\'\'",)''')

    def test_partial_reads(self):
        # jeżeli we have a length, the system knows when to close itself
        # same behaviour than when we read the whole thing przy read()
        body = "HTTP/1.1 200 Ok\r\nContent-Length: 4\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(2), b'Te')
        self.assertNieprawda(resp.isclosed())
        self.assertEqual(resp.read(2), b'xt')
        self.assertPrawda(resp.isclosed())
        self.assertNieprawda(resp.closed)
        resp.close()
        self.assertPrawda(resp.closed)

    def test_partial_readintos(self):
        # jeżeli we have a length, the system knows when to close itself
        # same behaviour than when we read the whole thing przy read()
        body = "HTTP/1.1 200 Ok\r\nContent-Length: 4\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        b = bytearray(2)
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'Te')
        self.assertNieprawda(resp.isclosed())
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'xt')
        self.assertPrawda(resp.isclosed())
        self.assertNieprawda(resp.closed)
        resp.close()
        self.assertPrawda(resp.closed)

    def test_partial_reads_no_content_length(self):
        # when no length jest present, the socket should be gracefully closed when
        # all data was read
        body = "HTTP/1.1 200 Ok\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(2), b'Te')
        self.assertNieprawda(resp.isclosed())
        self.assertEqual(resp.read(2), b'xt')
        self.assertEqual(resp.read(1), b'')
        self.assertPrawda(resp.isclosed())
        self.assertNieprawda(resp.closed)
        resp.close()
        self.assertPrawda(resp.closed)

    def test_partial_readintos_no_content_length(self):
        # when no length jest present, the socket should be gracefully closed when
        # all data was read
        body = "HTTP/1.1 200 Ok\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        b = bytearray(2)
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'Te')
        self.assertNieprawda(resp.isclosed())
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'xt')
        n = resp.readinto(b)
        self.assertEqual(n, 0)
        self.assertPrawda(resp.isclosed())

    def test_partial_reads_incomplete_body(self):
        # jeżeli the server shuts down the connection before the whole
        # content-length jest delivered, the socket jest gracefully closed
        body = "HTTP/1.1 200 Ok\r\nContent-Length: 10\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(2), b'Te')
        self.assertNieprawda(resp.isclosed())
        self.assertEqual(resp.read(2), b'xt')
        self.assertEqual(resp.read(1), b'')
        self.assertPrawda(resp.isclosed())

    def test_partial_readintos_incomplete_body(self):
        # jeżeli the server shuts down the connection before the whole
        # content-length jest delivered, the socket jest gracefully closed
        body = "HTTP/1.1 200 Ok\r\nContent-Length: 10\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        b = bytearray(2)
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'Te')
        self.assertNieprawda(resp.isclosed())
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'xt')
        n = resp.readinto(b)
        self.assertEqual(n, 0)
        self.assertPrawda(resp.isclosed())
        self.assertNieprawda(resp.closed)
        resp.close()
        self.assertPrawda(resp.closed)

    def test_host_port(self):
        # Check invalid host_port

        dla hp w ("www.python.org:abc", "user:password@www.python.org"):
            self.assertRaises(client.InvalidURL, client.HTTPConnection, hp)

        dla hp, h, p w (("[fe80::207:e9ff:fe9b]:8000",
                          "fe80::207:e9ff:fe9b", 8000),
                         ("www.python.org:80", "www.python.org", 80),
                         ("www.python.org:", "www.python.org", 80),
                         ("www.python.org", "www.python.org", 80),
                         ("[fe80::207:e9ff:fe9b]", "fe80::207:e9ff:fe9b", 80),
                         ("[fe80::207:e9ff:fe9b]:", "fe80::207:e9ff:fe9b", 80)):
            c = client.HTTPConnection(hp)
            self.assertEqual(h, c.host)
            self.assertEqual(p, c.port)

    def test_response_headers(self):
        # test response przy multiple message headers przy the same field name.
        text = ('HTTP/1.1 200 OK\r\n'
                'Set-Cookie: Customer="WILE_E_COYOTE"; '
                'Version="1"; Path="/acme"\r\n'
                'Set-Cookie: Part_Number="Rocket_Launcher_0001"; Version="1";'
                ' Path="/acme"\r\n'
                '\r\n'
                'No body\r\n')
        hdr = ('Customer="WILE_E_COYOTE"; Version="1"; Path="/acme"'
               ', '
               'Part_Number="Rocket_Launcher_0001"; Version="1"; Path="/acme"')
        s = FakeSocket(text)
        r = client.HTTPResponse(s)
        r.begin()
        cookies = r.getheader("Set-Cookie")
        self.assertEqual(cookies, hdr)

    def test_read_head(self):
        # Test that the library doesn't attempt to read any data
        # z a HEAD request.  (Tickles SF bug #622042.)
        sock = FakeSocket(
            'HTTP/1.1 200 OK\r\n'
            'Content-Length: 14432\r\n'
            '\r\n',
            NoEOFBytesIO)
        resp = client.HTTPResponse(sock, method="HEAD")
        resp.begin()
        jeżeli resp.read():
            self.fail("Did nie expect response z HEAD request")

    def test_readinto_head(self):
        # Test that the library doesn't attempt to read any data
        # z a HEAD request.  (Tickles SF bug #622042.)
        sock = FakeSocket(
            'HTTP/1.1 200 OK\r\n'
            'Content-Length: 14432\r\n'
            '\r\n',
            NoEOFBytesIO)
        resp = client.HTTPResponse(sock, method="HEAD")
        resp.begin()
        b = bytearray(5)
        jeżeli resp.readinto(b) != 0:
            self.fail("Did nie expect response z HEAD request")
        self.assertEqual(bytes(b), b'\x00'*5)

    def test_too_many_headers(self):
        headers = '\r\n'.join('Header%d: foo' % i
                              dla i w range(client._MAXHEADERS + 1)) + '\r\n'
        text = ('HTTP/1.1 200 OK\r\n' + headers)
        s = FakeSocket(text)
        r = client.HTTPResponse(s)
        self.assertRaisesRegex(client.HTTPException,
                               r"got more than \d+ headers", r.begin)

    def test_send_file(self):
        expected = (b'GET /foo HTTP/1.1\r\nHost: example.com\r\n'
                    b'Accept-Encoding: identity\r\nContent-Length:')

        przy open(__file__, 'rb') jako body:
            conn = client.HTTPConnection('example.com')
            sock = FakeSocket(body)
            conn.sock = sock
            conn.request('GET', '/foo', body)
            self.assertPrawda(sock.data.startswith(expected), '%r != %r' %
                    (sock.data[:len(expected)], expected))

    def test_send(self):
        expected = b'this jest a test this jest only a test'
        conn = client.HTTPConnection('example.com')
        sock = FakeSocket(Nic)
        conn.sock = sock
        conn.send(expected)
        self.assertEqual(expected, sock.data)
        sock.data = b''
        conn.send(array.array('b', expected))
        self.assertEqual(expected, sock.data)
        sock.data = b''
        conn.send(io.BytesIO(expected))
        self.assertEqual(expected, sock.data)

    def test_send_updating_file(self):
        def data():
            uzyskaj 'data'
            uzyskaj Nic
            uzyskaj 'data_two'

        klasa UpdatingFile():
            mode = 'r'
            d = data()
            def read(self, blocksize=-1):
                zwróć self.d.__next__()

        expected = b'data'

        conn = client.HTTPConnection('example.com')
        sock = FakeSocket("")
        conn.sock = sock
        conn.send(UpdatingFile())
        self.assertEqual(sock.data, expected)


    def test_send_iter(self):
        expected = b'GET /foo HTTP/1.1\r\nHost: example.com\r\n' \
                   b'Accept-Encoding: identity\r\nContent-Length: 11\r\n' \
                   b'\r\nonetwothree'

        def body():
            uzyskaj b"one"
            uzyskaj b"two"
            uzyskaj b"three"

        conn = client.HTTPConnection('example.com')
        sock = FakeSocket("")
        conn.sock = sock
        conn.request('GET', '/foo', body(), {'Content-Length': '11'})
        self.assertEqual(sock.data, expected)

    def test_send_type_error(self):
        # See: Issue #12676
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket('')
        przy self.assertRaises(TypeError):
            conn.request('POST', 'test', conn)

    def test_chunked(self):
        expected = chunked_expected
        sock = FakeSocket(chunked_start + last_chunk + chunked_end)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        resp.close()

        # Various read sizes
        dla n w range(1, 12):
            sock = FakeSocket(chunked_start + last_chunk + chunked_end)
            resp = client.HTTPResponse(sock, method="GET")
            resp.begin()
            self.assertEqual(resp.read(n) + resp.read(n) + resp.read(), expected)
            resp.close()

        dla x w ('', 'foo\r\n'):
            sock = FakeSocket(chunked_start + x)
            resp = client.HTTPResponse(sock, method="GET")
            resp.begin()
            spróbuj:
                resp.read()
            wyjąwszy client.IncompleteRead jako i:
                self.assertEqual(i.partial, expected)
                expected_message = 'IncompleteRead(%d bytes read)' % len(expected)
                self.assertEqual(repr(i), expected_message)
                self.assertEqual(str(i), expected_message)
            inaczej:
                self.fail('IncompleteRead expected')
            w_końcu:
                resp.close()

    def test_readinto_chunked(self):

        expected = chunked_expected
        nexpected = len(expected)
        b = bytearray(128)

        sock = FakeSocket(chunked_start + last_chunk + chunked_end)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        n = resp.readinto(b)
        self.assertEqual(b[:nexpected], expected)
        self.assertEqual(n, nexpected)
        resp.close()

        # Various read sizes
        dla n w range(1, 12):
            sock = FakeSocket(chunked_start + last_chunk + chunked_end)
            resp = client.HTTPResponse(sock, method="GET")
            resp.begin()
            m = memoryview(b)
            i = resp.readinto(m[0:n])
            i += resp.readinto(m[i:n + i])
            i += resp.readinto(m[i:])
            self.assertEqual(b[:nexpected], expected)
            self.assertEqual(i, nexpected)
            resp.close()

        dla x w ('', 'foo\r\n'):
            sock = FakeSocket(chunked_start + x)
            resp = client.HTTPResponse(sock, method="GET")
            resp.begin()
            spróbuj:
                n = resp.readinto(b)
            wyjąwszy client.IncompleteRead jako i:
                self.assertEqual(i.partial, expected)
                expected_message = 'IncompleteRead(%d bytes read)' % len(expected)
                self.assertEqual(repr(i), expected_message)
                self.assertEqual(str(i), expected_message)
            inaczej:
                self.fail('IncompleteRead expected')
            w_końcu:
                resp.close()

    def test_chunked_head(self):
        chunked_start = (
            'HTTP/1.1 200 OK\r\n'
            'Transfer-Encoding: chunked\r\n\r\n'
            'a\r\n'
            'hello world\r\n'
            '1\r\n'
            'd\r\n'
        )
        sock = FakeSocket(chunked_start + last_chunk + chunked_end)
        resp = client.HTTPResponse(sock, method="HEAD")
        resp.begin()
        self.assertEqual(resp.read(), b'')
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.reason, 'OK')
        self.assertPrawda(resp.isclosed())
        self.assertNieprawda(resp.closed)
        resp.close()
        self.assertPrawda(resp.closed)

    def test_readinto_chunked_head(self):
        chunked_start = (
            'HTTP/1.1 200 OK\r\n'
            'Transfer-Encoding: chunked\r\n\r\n'
            'a\r\n'
            'hello world\r\n'
            '1\r\n'
            'd\r\n'
        )
        sock = FakeSocket(chunked_start + last_chunk + chunked_end)
        resp = client.HTTPResponse(sock, method="HEAD")
        resp.begin()
        b = bytearray(5)
        n = resp.readinto(b)
        self.assertEqual(n, 0)
        self.assertEqual(bytes(b), b'\x00'*5)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.reason, 'OK')
        self.assertPrawda(resp.isclosed())
        self.assertNieprawda(resp.closed)
        resp.close()
        self.assertPrawda(resp.closed)

    def test_negative_content_length(self):
        sock = FakeSocket(
            'HTTP/1.1 200 OK\r\nContent-Length: -1\r\n\r\nHello\r\n')
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), b'Hello\r\n')
        self.assertPrawda(resp.isclosed())

    def test_incomplete_read(self):
        sock = FakeSocket('HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\nHello\r\n')
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        spróbuj:
            resp.read()
        wyjąwszy client.IncompleteRead jako i:
            self.assertEqual(i.partial, b'Hello\r\n')
            self.assertEqual(repr(i),
                             "IncompleteRead(7 bytes read, 3 more expected)")
            self.assertEqual(str(i),
                             "IncompleteRead(7 bytes read, 3 more expected)")
            self.assertPrawda(resp.isclosed())
        inaczej:
            self.fail('IncompleteRead expected')

    def test_epipe(self):
        sock = EPipeSocket(
            "HTTP/1.0 401 Authorization Required\r\n"
            "Content-type: text/html\r\n"
            "WWW-Authenticate: Basic realm=\"example\"\r\n",
            b"Content-Length")
        conn = client.HTTPConnection("example.com")
        conn.sock = sock
        self.assertRaises(OSError,
                          lambda: conn.request("PUT", "/url", "body"))
        resp = conn.getresponse()
        self.assertEqual(401, resp.status)
        self.assertEqual("Basic realm=\"example\"",
                         resp.getheader("www-authenticate"))

    # Test lines overflowing the max line size (_MAXLINE w http.client)

    def test_overflowing_status_line(self):
        body = "HTTP/1.1 200 Ok" + "k" * 65536 + "\r\n"
        resp = client.HTTPResponse(FakeSocket(body))
        self.assertRaises((client.LineTooLong, client.BadStatusLine), resp.begin)

    def test_overflowing_header_line(self):
        body = (
            'HTTP/1.1 200 OK\r\n'
            'X-Foo: bar' + 'r' * 65536 + '\r\n\r\n'
        )
        resp = client.HTTPResponse(FakeSocket(body))
        self.assertRaises(client.LineTooLong, resp.begin)

    def test_overflowing_chunked_line(self):
        body = (
            'HTTP/1.1 200 OK\r\n'
            'Transfer-Encoding: chunked\r\n\r\n'
            + '0' * 65536 + 'a\r\n'
            'hello world\r\n'
            '0\r\n'
            '\r\n'
        )
        resp = client.HTTPResponse(FakeSocket(body))
        resp.begin()
        self.assertRaises(client.LineTooLong, resp.read)

    def test_early_eof(self):
        # Test httpresponse przy no \r\n termination,
        body = "HTTP/1.1 200 Ok"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(), b'')
        self.assertPrawda(resp.isclosed())
        self.assertNieprawda(resp.closed)
        resp.close()
        self.assertPrawda(resp.closed)

    def test_error_leak(self):
        # Test that the socket jest nie leaked jeżeli getresponse() fails
        conn = client.HTTPConnection('example.com')
        response = Nic
        klasa Response(client.HTTPResponse):
            def __init__(self, *pos, **kw):
                nonlocal response
                response = self  # Avoid garbage collector closing the socket
                client.HTTPResponse.__init__(self, *pos, **kw)
        conn.response_class = Response
        conn.sock = FakeSocket('Invalid status line')
        conn.request('GET', '/')
        self.assertRaises(client.BadStatusLine, conn.getresponse)
        self.assertPrawda(response.closed)
        self.assertPrawda(conn.sock.file_closed)

    def test_chunked_extension(self):
        extra = '3;foo=bar\r\n' + 'abc\r\n'
        expected = chunked_expected + b'abc'

        sock = FakeSocket(chunked_start + extra + last_chunk_extended + chunked_end)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        resp.close()

    def test_chunked_missing_end(self):
        """some servers may serve up a short chunked encoding stream"""
        expected = chunked_expected
        sock = FakeSocket(chunked_start + last_chunk)  #no terminating crlf
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        resp.close()

    def test_chunked_trailers(self):
        """See that trailers are read oraz ignored"""
        expected = chunked_expected
        sock = FakeSocket(chunked_start + last_chunk + trailers + chunked_end)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        # we should have reached the end of the file
        self.assertEqual(sock.file.read(100), b"") #we read to the end
        resp.close()

    def test_chunked_sync(self):
        """Check that we don't read past the end of the chunked-encoding stream"""
        expected = chunked_expected
        extradata = "extradata"
        sock = FakeSocket(chunked_start + last_chunk + trailers + chunked_end + extradata)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        # the file should now have our extradata ready to be read
        self.assertEqual(sock.file.read(100), extradata.encode("ascii")) #we read to the end
        resp.close()

    def test_content_length_sync(self):
        """Check that we don't read past the end of the Content-Length stream"""
        extradata = "extradata"
        expected = b"Hello123\r\n"
        sock = FakeSocket('HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\nHello123\r\n' + extradata)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        # the file should now have our extradata ready to be read
        self.assertEqual(sock.file.read(100), extradata.encode("ascii")) #we read to the end
        resp.close()

klasa ExtendedReadTest(TestCase):
    """
    Test peek(), read1(), readline()
    """
    lines = (
        'HTTP/1.1 200 OK\r\n'
        '\r\n'
        'hello world!\n'
        'and now \n'
        'dla something completely different\n'
        'foo'
        )
    lines_expected = lines[lines.find('hello'):].encode("ascii")
    lines_chunked = (
        'HTTP/1.1 200 OK\r\n'
        'Transfer-Encoding: chunked\r\n\r\n'
        'a\r\n'
        'hello worl\r\n'
        '3\r\n'
        'd!\n\r\n'
        '9\r\n'
        'and now \n\r\n'
        '23\r\n'
        'dla something completely different\n\r\n'
        '3\r\n'
        'foo\r\n'
        '0\r\n' # terminating chunk
        '\r\n'  # end of trailers
    )

    def setUp(self):
        sock = FakeSocket(self.lines)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        resp.fp = io.BufferedReader(resp.fp)
        self.resp = resp



    def test_peek(self):
        resp = self.resp
        # patch up the buffered peek so that it returns nie too much stuff
        oldpeek = resp.fp.peek
        def mypeek(n=-1):
            p = oldpeek(n)
            jeżeli n >= 0:
                zwróć p[:n]
            zwróć p[:10]
        resp.fp.peek = mypeek

        all = []
        dopóki Prawda:
            # try a short peek
            p = resp.peek(3)
            jeżeli p:
                self.assertGreater(len(p), 0)
                # then unbounded peek
                p2 = resp.peek()
                self.assertGreaterEqual(len(p2), len(p))
                self.assertPrawda(p2.startswith(p))
                next = resp.read(len(p2))
                self.assertEqual(next, p2)
            inaczej:
                next = resp.read()
                self.assertNieprawda(next)
            all.append(next)
            jeżeli nie next:
                przerwij
        self.assertEqual(b"".join(all), self.lines_expected)

    def test_readline(self):
        resp = self.resp
        self._verify_readline(self.resp.readline, self.lines_expected)

    def _verify_readline(self, readline, expected):
        all = []
        dopóki Prawda:
            # short readlines
            line = readline(5)
            jeżeli line oraz line != b"foo":
                jeżeli len(line) < 5:
                    self.assertPrawda(line.endswith(b"\n"))
            all.append(line)
            jeżeli nie line:
                przerwij
        self.assertEqual(b"".join(all), expected)

    def test_read1(self):
        resp = self.resp
        def r():
            res = resp.read1(4)
            self.assertLessEqual(len(res), 4)
            zwróć res
        readliner = Readliner(r)
        self._verify_readline(readliner.readline, self.lines_expected)

    def test_read1_unbounded(self):
        resp = self.resp
        all = []
        dopóki Prawda:
            data = resp.read1()
            jeżeli nie data:
                przerwij
            all.append(data)
        self.assertEqual(b"".join(all), self.lines_expected)

    def test_read1_bounded(self):
        resp = self.resp
        all = []
        dopóki Prawda:
            data = resp.read1(10)
            jeżeli nie data:
                przerwij
            self.assertLessEqual(len(data), 10)
            all.append(data)
        self.assertEqual(b"".join(all), self.lines_expected)

    def test_read1_0(self):
        self.assertEqual(self.resp.read1(0), b"")

    def test_peek_0(self):
        p = self.resp.peek(0)
        self.assertLessEqual(0, len(p))

klasa ExtendedReadTestChunked(ExtendedReadTest):
    """
    Test peek(), read1(), readline() w chunked mode
    """
    lines = (
        'HTTP/1.1 200 OK\r\n'
        'Transfer-Encoding: chunked\r\n\r\n'
        'a\r\n'
        'hello worl\r\n'
        '3\r\n'
        'd!\n\r\n'
        '9\r\n'
        'and now \n\r\n'
        '23\r\n'
        'dla something completely different\n\r\n'
        '3\r\n'
        'foo\r\n'
        '0\r\n' # terminating chunk
        '\r\n'  # end of trailers
    )


klasa Readliner:
    """
    a simple readline klasa that uses an arbitrary read function oraz buffering
    """
    def __init__(self, readfunc):
        self.readfunc = readfunc
        self.remainder = b""

    def readline(self, limit):
        data = []
        datalen = 0
        read = self.remainder
        spróbuj:
            dopóki Prawda:
                idx = read.find(b'\n')
                jeżeli idx != -1:
                    przerwij
                jeżeli datalen + len(read) >= limit:
                    idx = limit - datalen - 1
                # read more data
                data.append(read)
                read = self.readfunc()
                jeżeli nie read:
                    idx = 0 #eof condition
                    przerwij
            idx += 1
            data.append(read[:idx])
            self.remainder = read[idx:]
            zwróć b"".join(data)
        wyjąwszy:
            self.remainder = b"".join(data)
            podnieś


klasa OfflineTest(TestCase):
    def test_all(self):
        # Documented objects defined w the module should be w __all__
        expected = {"responses"}  # White-list documented dict() object
        # HTTPMessage, parse_headers(), oraz the HTTP status code constants are
        # intentionally omitted dla simplicity
        blacklist = {"HTTPMessage", "parse_headers"}
        dla name w dir(client):
            jeżeli name w blacklist:
                kontynuuj
            module_object = getattr(client, name)
            jeżeli getattr(module_object, "__module__", Nic) == "http.client":
                expected.add(name)
        self.assertCountEqual(client.__all__, expected)

    def test_responses(self):
        self.assertEqual(client.responses[client.NOT_FOUND], "Not Found")

    def test_client_constants(self):
        # Make sure we don't przerwij backward compatibility przy 3.4
        expected = [
            'CONTINUE',
            'SWITCHING_PROTOCOLS',
            'PROCESSING',
            'OK',
            'CREATED',
            'ACCEPTED',
            'NON_AUTHORITATIVE_INFORMATION',
            'NO_CONTENT',
            'RESET_CONTENT',
            'PARTIAL_CONTENT',
            'MULTI_STATUS',
            'IM_USED',
            'MULTIPLE_CHOICES',
            'MOVED_PERMANENTLY',
            'FOUND',
            'SEE_OTHER',
            'NOT_MODIFIED',
            'USE_PROXY',
            'TEMPORARY_REDIRECT',
            'BAD_REQUEST',
            'UNAUTHORIZED',
            'PAYMENT_REQUIRED',
            'FORBIDDEN',
            'NOT_FOUND',
            'METHOD_NOT_ALLOWED',
            'NOT_ACCEPTABLE',
            'PROXY_AUTHENTICATION_REQUIRED',
            'REQUEST_TIMEOUT',
            'CONFLICT',
            'GONE',
            'LENGTH_REQUIRED',
            'PRECONDITION_FAILED',
            'REQUEST_ENTITY_TOO_LARGE',
            'REQUEST_URI_TOO_LONG',
            'UNSUPPORTED_MEDIA_TYPE',
            'REQUESTED_RANGE_NOT_SATISFIABLE',
            'EXPECTATION_FAILED',
            'UNPROCESSABLE_ENTITY',
            'LOCKED',
            'FAILED_DEPENDENCY',
            'UPGRADE_REQUIRED',
            'PRECONDITION_REQUIRED',
            'TOO_MANY_REQUESTS',
            'REQUEST_HEADER_FIELDS_TOO_LARGE',
            'INTERNAL_SERVER_ERROR',
            'NOT_IMPLEMENTED',
            'BAD_GATEWAY',
            'SERVICE_UNAVAILABLE',
            'GATEWAY_TIMEOUT',
            'HTTP_VERSION_NOT_SUPPORTED',
            'INSUFFICIENT_STORAGE',
            'NOT_EXTENDED',
            'NETWORK_AUTHENTICATION_REQUIRED',
        ]
        dla const w expected:
            przy self.subTest(constant=const):
                self.assertPrawda(hasattr(client, const))


klasa SourceAddressTest(TestCase):
    def setUp(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = support.bind_port(self.serv)
        self.source_port = support.find_unused_port()
        self.serv.listen()
        self.conn = Nic

    def tearDown(self):
        jeżeli self.conn:
            self.conn.close()
            self.conn = Nic
        self.serv.close()
        self.serv = Nic

    def testHTTPConnectionSourceAddress(self):
        self.conn = client.HTTPConnection(HOST, self.port,
                source_address=('', self.source_port))
        self.conn.connect()
        self.assertEqual(self.conn.sock.getsockname()[1], self.source_port)

    @unittest.skipIf(nie hasattr(client, 'HTTPSConnection'),
                     'http.client.HTTPSConnection nie defined')
    def testHTTPSConnectionSourceAddress(self):
        self.conn = client.HTTPSConnection(HOST, self.port,
                source_address=('', self.source_port))
        # We don't test anything here other the constructor nie barfing as
        # this code doesn't deal przy setting up an active running SSL server
        # dla an ssl_wrapped connect() to actually zwróć from.


klasa TimeoutTest(TestCase):
    PORT = Nic

    def setUp(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TimeoutTest.PORT = support.bind_port(self.serv)
        self.serv.listen()

    def tearDown(self):
        self.serv.close()
        self.serv = Nic

    def testTimeoutAttribute(self):
        # This will prove that the timeout gets through HTTPConnection
        # oraz into the socket.

        # default -- use global socket timeout
        self.assertIsNic(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        spróbuj:
            httpConn = client.HTTPConnection(HOST, TimeoutTest.PORT)
            httpConn.connect()
        w_końcu:
            socket.setdefaulttimeout(Nic)
        self.assertEqual(httpConn.sock.gettimeout(), 30)
        httpConn.close()

        # no timeout -- do nie use global socket default
        self.assertIsNic(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        spróbuj:
            httpConn = client.HTTPConnection(HOST, TimeoutTest.PORT,
                                              timeout=Nic)
            httpConn.connect()
        w_końcu:
            socket.setdefaulttimeout(Nic)
        self.assertEqual(httpConn.sock.gettimeout(), Nic)
        httpConn.close()

        # a value
        httpConn = client.HTTPConnection(HOST, TimeoutTest.PORT, timeout=30)
        httpConn.connect()
        self.assertEqual(httpConn.sock.gettimeout(), 30)
        httpConn.close()


klasa PersistenceTest(TestCase):

    def test_reuse_reconnect(self):
        # Should reuse albo reconnect depending on header z server
        tests = (
            ('1.0', '', Nieprawda),
            ('1.0', 'Connection: keep-alive\r\n', Prawda),
            ('1.1', '', Prawda),
            ('1.1', 'Connection: close\r\n', Nieprawda),
            ('1.0', 'Connection: keep-ALIVE\r\n', Prawda),
            ('1.1', 'Connection: cloSE\r\n', Nieprawda),
        )
        dla version, header, reuse w tests:
            przy self.subTest(version=version, header=header):
                msg = (
                    'HTTP/{} 200 OK\r\n'
                    '{}'
                    'Content-Length: 12\r\n'
                    '\r\n'
                    'Dummy body\r\n'
                ).format(version, header)
                conn = FakeSocketHTTPConnection(msg)
                self.assertIsNic(conn.sock)
                conn.request('GET', '/open-connection')
                przy conn.getresponse() jako response:
                    self.assertEqual(conn.sock jest Nic, nie reuse)
                    response.read()
                self.assertEqual(conn.sock jest Nic, nie reuse)
                self.assertEqual(conn.connections, 1)
                conn.request('GET', '/subsequent-request')
                self.assertEqual(conn.connections, 1 jeżeli reuse inaczej 2)

    def test_disconnected(self):

        def make_reset_reader(text):
            """Return BufferedReader that podnieśs ECONNRESET at EOF"""
            stream = io.BytesIO(text)
            def readinto(buffer):
                size = io.BytesIO.readinto(stream, buffer)
                jeżeli size == 0:
                    podnieś ConnectionResetError()
                zwróć size
            stream.readinto = readinto
            zwróć io.BufferedReader(stream)

        tests = (
            (io.BytesIO, client.RemoteDisconnected),
            (make_reset_reader, ConnectionResetError),
        )
        dla stream_factory, exception w tests:
            przy self.subTest(exception=exception):
                conn = FakeSocketHTTPConnection(b'', stream_factory)
                conn.request('GET', '/eof-response')
                self.assertRaises(exception, conn.getresponse)
                self.assertIsNic(conn.sock)
                # HTTPConnection.connect() should be automatically invoked
                conn.request('GET', '/reconnect')
                self.assertEqual(conn.connections, 2)

    def test_100_close(self):
        conn = FakeSocketHTTPConnection(
            b'HTTP/1.1 100 Continue\r\n'
            b'\r\n'
            # Missing final response
        )
        conn.request('GET', '/', headers={'Expect': '100-continue'})
        self.assertRaises(client.RemoteDisconnected, conn.getresponse)
        self.assertIsNic(conn.sock)
        conn.request('GET', '/reconnect')
        self.assertEqual(conn.connections, 2)


klasa HTTPSTest(TestCase):

    def setUp(self):
        jeżeli nie hasattr(client, 'HTTPSConnection'):
            self.skipTest('ssl support required')

    def make_server(self, certfile):
        z test.ssl_servers zaimportuj make_https_server
        zwróć make_https_server(self, certfile=certfile)

    def test_attributes(self):
        # simple test to check it's storing the timeout
        h = client.HTTPSConnection(HOST, TimeoutTest.PORT, timeout=30)
        self.assertEqual(h.timeout, 30)

    def test_networked(self):
        # Default settings: requires a valid cert z a trusted CA
        zaimportuj ssl
        support.requires('network')
        przy support.transient_internet('self-signed.pythontest.net'):
            h = client.HTTPSConnection('self-signed.pythontest.net', 443)
            przy self.assertRaises(ssl.SSLError) jako exc_info:
                h.request('GET', '/')
            self.assertEqual(exc_info.exception.reason, 'CERTIFICATE_VERIFY_FAILED')

    def test_networked_noverification(self):
        # Switch off cert verification
        zaimportuj ssl
        support.requires('network')
        przy support.transient_internet('self-signed.pythontest.net'):
            context = ssl._create_unverified_context()
            h = client.HTTPSConnection('self-signed.pythontest.net', 443,
                                       context=context)
            h.request('GET', '/')
            resp = h.getresponse()
            h.close()
            self.assertIn('nginx', resp.getheader('server'))

    @support.system_must_validate_cert
    def test_networked_trusted_by_default_cert(self):
        # Default settings: requires a valid cert z a trusted CA
        support.requires('network')
        przy support.transient_internet('www.python.org'):
            h = client.HTTPSConnection('www.python.org', 443)
            h.request('GET', '/')
            resp = h.getresponse()
            content_type = resp.getheader('content-type')
            h.close()
            self.assertIn('text/html', content_type)

    def test_networked_good_cert(self):
        # We feed the server's cert jako a validating cert
        zaimportuj ssl
        support.requires('network')
        przy support.transient_internet('self-signed.pythontest.net'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(CERT_selfsigned_pythontestdotnet)
            h = client.HTTPSConnection('self-signed.pythontest.net', 443, context=context)
            h.request('GET', '/')
            resp = h.getresponse()
            server_string = resp.getheader('server')
            h.close()
            self.assertIn('nginx', server_string)

    def test_networked_bad_cert(self):
        # We feed a "CA" cert that jest unrelated to the server's cert
        zaimportuj ssl
        support.requires('network')
        przy support.transient_internet('self-signed.pythontest.net'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(CERT_localhost)
            h = client.HTTPSConnection('self-signed.pythontest.net', 443, context=context)
            przy self.assertRaises(ssl.SSLError) jako exc_info:
                h.request('GET', '/')
            self.assertEqual(exc_info.exception.reason, 'CERTIFICATE_VERIFY_FAILED')

    def test_local_unknown_cert(self):
        # The custom cert isn't known to the default trust bundle
        zaimportuj ssl
        server = self.make_server(CERT_localhost)
        h = client.HTTPSConnection('localhost', server.port)
        przy self.assertRaises(ssl.SSLError) jako exc_info:
            h.request('GET', '/')
        self.assertEqual(exc_info.exception.reason, 'CERTIFICATE_VERIFY_FAILED')

    def test_local_good_hostname(self):
        # The (valid) cert validates the HTTP hostname
        zaimportuj ssl
        server = self.make_server(CERT_localhost)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(CERT_localhost)
        h = client.HTTPSConnection('localhost', server.port, context=context)
        h.request('GET', '/nonexistent')
        resp = h.getresponse()
        self.assertEqual(resp.status, 404)

    def test_local_bad_hostname(self):
        # The (valid) cert doesn't validate the HTTP hostname
        zaimportuj ssl
        server = self.make_server(CERT_fakehostname)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = Prawda
        context.load_verify_locations(CERT_fakehostname)
        h = client.HTTPSConnection('localhost', server.port, context=context)
        przy self.assertRaises(ssl.CertificateError):
            h.request('GET', '/')
        # Same przy explicit check_hostname=Prawda
        h = client.HTTPSConnection('localhost', server.port, context=context,
                                   check_hostname=Prawda)
        przy self.assertRaises(ssl.CertificateError):
            h.request('GET', '/')
        # With check_hostname=Nieprawda, the mismatching jest ignored
        context.check_hostname = Nieprawda
        h = client.HTTPSConnection('localhost', server.port, context=context,
                                   check_hostname=Nieprawda)
        h.request('GET', '/nonexistent')
        resp = h.getresponse()
        self.assertEqual(resp.status, 404)
        # The context's check_hostname setting jest used jeżeli one isn't dalejed to
        # HTTPSConnection.
        context.check_hostname = Nieprawda
        h = client.HTTPSConnection('localhost', server.port, context=context)
        h.request('GET', '/nonexistent')
        self.assertEqual(h.getresponse().status, 404)
        # Passing check_hostname to HTTPSConnection should override the
        # context's setting.
        h = client.HTTPSConnection('localhost', server.port, context=context,
                                   check_hostname=Prawda)
        przy self.assertRaises(ssl.CertificateError):
            h.request('GET', '/')

    @unittest.skipIf(nie hasattr(client, 'HTTPSConnection'),
                     'http.client.HTTPSConnection nie available')
    def test_host_port(self):
        # Check invalid host_port

        dla hp w ("www.python.org:abc", "user:password@www.python.org"):
            self.assertRaises(client.InvalidURL, client.HTTPSConnection, hp)

        dla hp, h, p w (("[fe80::207:e9ff:fe9b]:8000",
                          "fe80::207:e9ff:fe9b", 8000),
                         ("www.python.org:443", "www.python.org", 443),
                         ("www.python.org:", "www.python.org", 443),
                         ("www.python.org", "www.python.org", 443),
                         ("[fe80::207:e9ff:fe9b]", "fe80::207:e9ff:fe9b", 443),
                         ("[fe80::207:e9ff:fe9b]:", "fe80::207:e9ff:fe9b",
                             443)):
            c = client.HTTPSConnection(hp)
            self.assertEqual(h, c.host)
            self.assertEqual(p, c.port)


klasa RequestBodyTest(TestCase):
    """Test cases where a request includes a message body."""

    def setUp(self):
        self.conn = client.HTTPConnection('example.com')
        self.conn.sock = self.sock = FakeSocket("")
        self.conn.sock = self.sock

    def get_headers_and_fp(self):
        f = io.BytesIO(self.sock.data)
        f.readline()  # read the request line
        message = client.parse_headers(f)
        zwróć message, f

    def test_manual_content_length(self):
        # Set an incorrect content-length so that we can verify that
        # it will nie be over-ridden by the library.
        self.conn.request("PUT", "/url", "body",
                          {"Content-Length": "42"})
        message, f = self.get_headers_and_fp()
        self.assertEqual("42", message.get("content-length"))
        self.assertEqual(4, len(f.read()))

    def test_ascii_body(self):
        self.conn.request("PUT", "/url", "body")
        message, f = self.get_headers_and_fp()
        self.assertEqual("text/plain", message.get_content_type())
        self.assertIsNic(message.get_charset())
        self.assertEqual("4", message.get("content-length"))
        self.assertEqual(b'body', f.read())

    def test_latin1_body(self):
        self.conn.request("PUT", "/url", "body\xc1")
        message, f = self.get_headers_and_fp()
        self.assertEqual("text/plain", message.get_content_type())
        self.assertIsNic(message.get_charset())
        self.assertEqual("5", message.get("content-length"))
        self.assertEqual(b'body\xc1', f.read())

    def test_bytes_body(self):
        self.conn.request("PUT", "/url", b"body\xc1")
        message, f = self.get_headers_and_fp()
        self.assertEqual("text/plain", message.get_content_type())
        self.assertIsNic(message.get_charset())
        self.assertEqual("5", message.get("content-length"))
        self.assertEqual(b'body\xc1', f.read())

    def test_file_body(self):
        self.addCleanup(support.unlink, support.TESTFN)
        przy open(support.TESTFN, "w") jako f:
            f.write("body")
        przy open(support.TESTFN) jako f:
            self.conn.request("PUT", "/url", f)
            message, f = self.get_headers_and_fp()
            self.assertEqual("text/plain", message.get_content_type())
            self.assertIsNic(message.get_charset())
            self.assertEqual("4", message.get("content-length"))
            self.assertEqual(b'body', f.read())

    def test_binary_file_body(self):
        self.addCleanup(support.unlink, support.TESTFN)
        przy open(support.TESTFN, "wb") jako f:
            f.write(b"body\xc1")
        przy open(support.TESTFN, "rb") jako f:
            self.conn.request("PUT", "/url", f)
            message, f = self.get_headers_and_fp()
            self.assertEqual("text/plain", message.get_content_type())
            self.assertIsNic(message.get_charset())
            self.assertEqual("5", message.get("content-length"))
            self.assertEqual(b'body\xc1', f.read())


klasa HTTPResponseTest(TestCase):

    def setUp(self):
        body = "HTTP/1.1 200 Ok\r\nMy-Header: first-value\r\nMy-Header: \
                second-value\r\n\r\nText"
        sock = FakeSocket(body)
        self.resp = client.HTTPResponse(sock)
        self.resp.begin()

    def test_getting_header(self):
        header = self.resp.getheader('My-Header')
        self.assertEqual(header, 'first-value, second-value')

        header = self.resp.getheader('My-Header', 'some default')
        self.assertEqual(header, 'first-value, second-value')

    def test_getting_nonexistent_header_with_string_default(self):
        header = self.resp.getheader('No-Such-Header', 'default-value')
        self.assertEqual(header, 'default-value')

    def test_getting_nonexistent_header_with_iterable_default(self):
        header = self.resp.getheader('No-Such-Header', ['default', 'values'])
        self.assertEqual(header, 'default, values')

        header = self.resp.getheader('No-Such-Header', ('default', 'values'))
        self.assertEqual(header, 'default, values')

    def test_getting_nonexistent_header_without_default(self):
        header = self.resp.getheader('No-Such-Header')
        self.assertEqual(header, Nic)

    def test_getting_header_defaultint(self):
        header = self.resp.getheader('No-Such-Header',default=42)
        self.assertEqual(header, 42)

klasa TunnelTests(TestCase):
    def setUp(self):
        response_text = (
            'HTTP/1.0 200 OK\r\n\r\n' # Reply to CONNECT
            'HTTP/1.1 200 OK\r\n' # Reply to HEAD
            'Content-Length: 42\r\n\r\n'
        )
        self.host = 'proxy.com'
        self.conn = client.HTTPConnection(self.host)
        self.conn._create_connection = self._create_connection(response_text)

    def tearDown(self):
        self.conn.close()

    def _create_connection(self, response_text):
        def create_connection(address, timeout=Nic, source_address=Nic):
            zwróć FakeSocket(response_text, host=address[0], port=address[1])
        zwróć create_connection

    def test_set_tunnel_host_port_headers(self):
        tunnel_host = 'destination.com'
        tunnel_port = 8888
        tunnel_headers = {'User-Agent': 'Mozilla/5.0 (compatible, MSIE 11)'}
        self.conn.set_tunnel(tunnel_host, port=tunnel_port,
                             headers=tunnel_headers)
        self.conn.request('HEAD', '/', '')
        self.assertEqual(self.conn.sock.host, self.host)
        self.assertEqual(self.conn.sock.port, client.HTTP_PORT)
        self.assertEqual(self.conn._tunnel_host, tunnel_host)
        self.assertEqual(self.conn._tunnel_port, tunnel_port)
        self.assertEqual(self.conn._tunnel_headers, tunnel_headers)

    def test_disallow_set_tunnel_after_connect(self):
        # Once connected, we shouldn't be able to tunnel anymore
        self.conn.connect()
        self.assertRaises(RuntimeError, self.conn.set_tunnel,
                          'destination.com')

    def test_connect_with_tunnel(self):
        self.conn.set_tunnel('destination.com')
        self.conn.request('HEAD', '/', '')
        self.assertEqual(self.conn.sock.host, self.host)
        self.assertEqual(self.conn.sock.port, client.HTTP_PORT)
        self.assertIn(b'CONNECT destination.com', self.conn.sock.data)
        # issue22095
        self.assertNotIn(b'Host: destination.com:Nic', self.conn.sock.data)
        self.assertIn(b'Host: destination.com', self.conn.sock.data)

        # This test should be removed when CONNECT gets the HTTP/1.1 blessing
        self.assertNotIn(b'Host: proxy.com', self.conn.sock.data)

    def test_connect_put_request(self):
        self.conn.set_tunnel('destination.com')
        self.conn.request('PUT', '/', '')
        self.assertEqual(self.conn.sock.host, self.host)
        self.assertEqual(self.conn.sock.port, client.HTTP_PORT)
        self.assertIn(b'CONNECT destination.com', self.conn.sock.data)
        self.assertIn(b'Host: destination.com', self.conn.sock.data)

    def test_tunnel_debuglog(self):
        expected_header = 'X-Dummy: 1'
        response_text = 'HTTP/1.0 200 OK\r\n{}\r\n\r\n'.format(expected_header)

        self.conn.set_debuglevel(1)
        self.conn._create_connection = self._create_connection(response_text)
        self.conn.set_tunnel('destination.com')

        przy support.captured_stdout() jako output:
            self.conn.request('PUT', '/', '')
        lines = output.getvalue().splitlines()
        self.assertIn('header: {}'.format(expected_header), lines)


@support.reap_threads
def test_main(verbose=Nic):
    support.run_unittest(HeaderTests, OfflineTest, BasicTest, TimeoutTest,
                         PersistenceTest,
                         HTTPSTest, RequestBodyTest, SourceAddressTest,
                         HTTPResponseTest, ExtendedReadTest,
                         ExtendedReadTestChunked, TunnelTests)

jeżeli __name__ == '__main__':
    test_main()
