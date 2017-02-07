"""Unittests dla the various HTTPServer modules.

Written by Cody A.W. Somerville <cody-somerville@ubuntu.com>,
Josip Dzolonga, oraz Michael Otteneder dla the 2007/08 GHOP contest.
"""

z http.server zaimportuj BaseHTTPRequestHandler, HTTPServer, \
     SimpleHTTPRequestHandler, CGIHTTPRequestHandler
z http zaimportuj server, HTTPStatus

zaimportuj os
zaimportuj sys
zaimportuj re
zaimportuj base64
zaimportuj shutil
zaimportuj urllib.parse
zaimportuj html
zaimportuj http.client
zaimportuj tempfile
z io zaimportuj BytesIO

zaimportuj unittest
z test zaimportuj support
threading = support.import_module('threading')

klasa NoLogRequestHandler:
    def log_message(self, *args):
        # don't write log messages to stderr
        dalej

    def read(self, n=Nic):
        zwróć ''


klasa TestServerThread(threading.Thread):
    def __init__(self, test_object, request_handler):
        threading.Thread.__init__(self)
        self.request_handler = request_handler
        self.test_object = test_object

    def run(self):
        self.server = HTTPServer(('localhost', 0), self.request_handler)
        self.test_object.HOST, self.test_object.PORT = self.server.socket.getsockname()
        self.test_object.server_started.set()
        self.test_object = Nic
        spróbuj:
            self.server.serve_forever(0.05)
        w_końcu:
            self.server.server_close()

    def stop(self):
        self.server.shutdown()


klasa BaseTestCase(unittest.TestCase):
    def setUp(self):
        self._threads = support.threading_setup()
        os.environ = support.EnvironmentVarGuard()
        self.server_started = threading.Event()
        self.thread = TestServerThread(self, self.request_handler)
        self.thread.start()
        self.server_started.wait()

    def tearDown(self):
        self.thread.stop()
        self.thread = Nic
        os.environ.__exit__()
        support.threading_cleanup(*self._threads)

    def request(self, uri, method='GET', body=Nic, headers={}):
        self.connection = http.client.HTTPConnection(self.HOST, self.PORT)
        self.connection.request(method, uri, body, headers)
        zwróć self.connection.getresponse()


klasa BaseHTTPServerTestCase(BaseTestCase):
    klasa request_handler(NoLogRequestHandler, BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'
        default_request_version = 'HTTP/1.1'

        def do_TEST(self):
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Connection', 'close')
            self.end_headers()

        def do_KEEP(self):
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()

        def do_KEYERROR(self):
            self.send_error(999)

        def do_NOTFOUND(self):
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_EXPLAINERROR(self):
            self.send_error(999, "Short Message",
                            "This jest a long \n explaination")

        def do_CUSTOM(self):
            self.send_response(999)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Connection', 'close')
            self.end_headers()

        def do_LATINONEHEADER(self):
            self.send_response(999)
            self.send_header('X-Special', 'Dängerous Mind')
            self.send_header('Connection', 'close')
            self.end_headers()
            body = self.headers['x-special-incoming'].encode('utf-8')
            self.wfile.write(body)

    def setUp(self):
        BaseTestCase.setUp(self)
        self.con = http.client.HTTPConnection(self.HOST, self.PORT)
        self.con.connect()

    def test_command(self):
        self.con.request('GET', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    def test_request_line_trimming(self):
        self.con._http_vsn_str = 'HTTP/1.1\n'
        self.con.putrequest('XYZBOGUS', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    def test_version_bogus(self):
        self.con._http_vsn_str = 'FUBAR'
        self.con.putrequest('GET', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.BAD_REQUEST)

    def test_version_digits(self):
        self.con._http_vsn_str = 'HTTP/9.9.9'
        self.con.putrequest('GET', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.BAD_REQUEST)

    def test_version_none_get(self):
        self.con._http_vsn_str = ''
        self.con.putrequest('GET', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    def test_version_none(self):
        # Test that a valid method jest rejected when nie HTTP/1.x
        self.con._http_vsn_str = ''
        self.con.putrequest('CUSTOM', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.BAD_REQUEST)

    def test_version_invalid(self):
        self.con._http_vsn = 99
        self.con._http_vsn_str = 'HTTP/9.9'
        self.con.putrequest('GET', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.HTTP_VERSION_NOT_SUPPORTED)

    def test_send_blank(self):
        self.con._http_vsn_str = ''
        self.con.putrequest('', '')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.BAD_REQUEST)

    def test_header_close(self):
        self.con.putrequest('GET', '/')
        self.con.putheader('Connection', 'close')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    def test_head_keep_alive(self):
        self.con._http_vsn_str = 'HTTP/1.1'
        self.con.putrequest('GET', '/')
        self.con.putheader('Connection', 'keep-alive')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    def test_handler(self):
        self.con.request('TEST', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NO_CONTENT)

    def test_return_header_keep_alive(self):
        self.con.request('KEEP', '/')
        res = self.con.getresponse()
        self.assertEqual(res.getheader('Connection'), 'keep-alive')
        self.con.request('TEST', '/')
        self.addCleanup(self.con.close)

    def test_internal_key_error(self):
        self.con.request('KEYERROR', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, 999)

    def test_return_custom_status(self):
        self.con.request('CUSTOM', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, 999)

    def test_return_explain_error(self):
        self.con.request('EXPLAINERROR', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, 999)
        self.assertPrawda(int(res.getheader('Content-Length')))

    def test_latin1_header(self):
        self.con.request('LATINONEHEADER', '/', headers={
            'X-Special-Incoming':       'Ärger mit Unicode'
        })
        res = self.con.getresponse()
        self.assertEqual(res.getheader('X-Special'), 'Dängerous Mind')
        self.assertEqual(res.read(), 'Ärger mit Unicode'.encode('utf-8'))

    def test_error_content_length(self):
        # Issue #16088: standard error responses should have a content-length
        self.con.request('NOTFOUND', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_FOUND)

        data = res.read()
        self.assertEqual(int(res.getheader('Content-Length')), len(data))


klasa RequestHandlerLoggingTestCase(BaseTestCase):
    klasa request_handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'
        default_request_version = 'HTTP/1.1'

        def do_GET(self):
            self.send_response(HTTPStatus.OK)
            self.end_headers()

        def do_ERROR(self):
            self.send_error(HTTPStatus.NOT_FOUND, 'File nie found')

    def test_get(self):
        self.con = http.client.HTTPConnection(self.HOST, self.PORT)
        self.con.connect()

        przy support.captured_stderr() jako err:
            self.con.request('GET', '/')
            self.con.getresponse()

        self.assertPrawda(
            err.getvalue().endswith('"GET / HTTP/1.1" 200 -\n'))

    def test_err(self):
        self.con = http.client.HTTPConnection(self.HOST, self.PORT)
        self.con.connect()

        przy support.captured_stderr() jako err:
            self.con.request('ERROR', '/')
            self.con.getresponse()

        lines = err.getvalue().split('\n')
        self.assertPrawda(lines[0].endswith('code 404, message File nie found'))
        self.assertPrawda(lines[1].endswith('"ERROR / HTTP/1.1" 404 -'))


klasa SimpleHTTPServerTestCase(BaseTestCase):
    klasa request_handler(NoLogRequestHandler, SimpleHTTPRequestHandler):
        dalej

    def setUp(self):
        BaseTestCase.setUp(self)
        self.cwd = os.getcwd()
        basetempdir = tempfile.gettempdir()
        os.chdir(basetempdir)
        self.data = b'We are the knights who say Ni!'
        self.tempdir = tempfile.mkdtemp(dir=basetempdir)
        self.tempdir_name = os.path.basename(self.tempdir)
        przy open(os.path.join(self.tempdir, 'test'), 'wb') jako temp:
            temp.write(self.data)

    def tearDown(self):
        spróbuj:
            os.chdir(self.cwd)
            spróbuj:
                shutil.rmtree(self.tempdir)
            wyjąwszy:
                dalej
        w_końcu:
            BaseTestCase.tearDown(self)

    def check_status_and_reason(self, response, status, data=Nic):
        def close_conn():
            """Don't close reader yet so we can check jeżeli there was leftover
            buffered input"""
            nonlocal reader
            reader = response.fp
            response.fp = Nic
        reader = Nic
        response._close_conn = close_conn

        body = response.read()
        self.assertPrawda(response)
        self.assertEqual(response.status, status)
        self.assertIsNotNic(response.reason)
        jeżeli data:
            self.assertEqual(data, body)
        # Ensure the server has nie set up a persistent connection, oraz has
        # nie sent any extra data
        self.assertEqual(response.version, 10)
        self.assertEqual(response.msg.get("Connection", "close"), "close")
        self.assertEqual(reader.read(30), b'', 'Connection should be closed')

        reader.close()
        zwróć body

    @support.requires_mac_ver(10, 5)
    @unittest.skipUnless(support.TESTFN_UNDECODABLE,
                         'need support.TESTFN_UNDECODABLE')
    def test_undecodable_filename(self):
        enc = sys.getfilesystemencoding()
        filename = os.fsdecode(support.TESTFN_UNDECODABLE) + '.txt'
        przy open(os.path.join(self.tempdir, filename), 'wb') jako f:
            f.write(support.TESTFN_UNDECODABLE)
        response = self.request(self.tempdir_name + '/')
        jeżeli sys.platform == 'darwin':
            # On Mac OS the HFS+ filesystem replaces bytes that aren't valid
            # UTF-8 into a percent-encoded value.
            dla name w os.listdir(self.tempdir):
                jeżeli name != 'test': # Ignore a filename created w setUp().
                    filename = name
                    przerwij
        body = self.check_status_and_reason(response, HTTPStatus.OK)
        quotedname = urllib.parse.quote(filename, errors='surrogatepass')
        self.assertIn(('href="%s"' % quotedname)
                      .encode(enc, 'surrogateescape'), body)
        self.assertIn(('>%s<' % html.escape(filename))
                      .encode(enc, 'surrogateescape'), body)
        response = self.request(self.tempdir_name + '/' + quotedname)
        self.check_status_and_reason(response, HTTPStatus.OK,
                                     data=support.TESTFN_UNDECODABLE)

    def test_get(self):
        #constructs the path relative to the root directory of the HTTPServer
        response = self.request(self.tempdir_name + '/test')
        self.check_status_and_reason(response, HTTPStatus.OK, data=self.data)
        # check dla trailing "/" which should zwróć 404. See Issue17324
        response = self.request(self.tempdir_name + '/test/')
        self.check_status_and_reason(response, HTTPStatus.NOT_FOUND)
        response = self.request(self.tempdir_name + '/')
        self.check_status_and_reason(response, HTTPStatus.OK)
        response = self.request(self.tempdir_name)
        self.check_status_and_reason(response, HTTPStatus.MOVED_PERMANENTLY)
        response = self.request(self.tempdir_name + '/?hi=2')
        self.check_status_and_reason(response, HTTPStatus.OK)
        response = self.request(self.tempdir_name + '?hi=1')
        self.check_status_and_reason(response, HTTPStatus.MOVED_PERMANENTLY)
        self.assertEqual(response.getheader("Location"),
                         self.tempdir_name + "/?hi=1")
        response = self.request('/ThisDoesNotExist')
        self.check_status_and_reason(response, HTTPStatus.NOT_FOUND)
        response = self.request('/' + 'ThisDoesNotExist' + '/')
        self.check_status_and_reason(response, HTTPStatus.NOT_FOUND)

        data = b"Dummy index file\r\n"
        przy open(os.path.join(self.tempdir_name, 'index.html'), 'wb') jako f:
            f.write(data)
        response = self.request('/' + self.tempdir_name + '/')
        self.check_status_and_reason(response, HTTPStatus.OK, data)

        # chmod() doesn't work jako expected on Windows, oraz filesystem
        # permissions are ignored by root on Unix.
        jeżeli os.name == 'posix' oraz os.geteuid() != 0:
            os.chmod(self.tempdir, 0)
            spróbuj:
                response = self.request(self.tempdir_name + '/')
                self.check_status_and_reason(response, HTTPStatus.NOT_FOUND)
            w_końcu:
                os.chmod(self.tempdir, 0o755)

    def test_head(self):
        response = self.request(
            self.tempdir_name + '/test', method='HEAD')
        self.check_status_and_reason(response, HTTPStatus.OK)
        self.assertEqual(response.getheader('content-length'),
                         str(len(self.data)))
        self.assertEqual(response.getheader('content-type'),
                         'application/octet-stream')

    def test_invalid_requests(self):
        response = self.request('/', method='FOO')
        self.check_status_and_reason(response, HTTPStatus.NOT_IMPLEMENTED)
        # requests must be case sensitive,so this should fail too
        response = self.request('/', method='custom')
        self.check_status_and_reason(response, HTTPStatus.NOT_IMPLEMENTED)
        response = self.request('/', method='GETs')
        self.check_status_and_reason(response, HTTPStatus.NOT_IMPLEMENTED)


cgi_file1 = """\
#!%s

print("Content-type: text/html")
print()
print("Hello World")
"""

cgi_file2 = """\
#!%s
zaimportuj cgi

print("Content-type: text/html")
print()

form = cgi.FieldStorage()
print("%%s, %%s, %%s" %% (form.getfirst("spam"), form.getfirst("eggs"),
                          form.getfirst("bacon")))
"""


@unittest.skipIf(hasattr(os, 'geteuid') oraz os.geteuid() == 0,
        "This test can't be run reliably jako root (issue #13308).")
klasa CGIHTTPServerTestCase(BaseTestCase):
    klasa request_handler(NoLogRequestHandler, CGIHTTPRequestHandler):
        dalej

    linesep = os.linesep.encode('ascii')

    def setUp(self):
        BaseTestCase.setUp(self)
        self.cwd = os.getcwd()
        self.parent_dir = tempfile.mkdtemp()
        self.cgi_dir = os.path.join(self.parent_dir, 'cgi-bin')
        self.cgi_child_dir = os.path.join(self.cgi_dir, 'child-dir')
        os.mkdir(self.cgi_dir)
        os.mkdir(self.cgi_child_dir)
        self.nocgi_path = Nic
        self.file1_path = Nic
        self.file2_path = Nic
        self.file3_path = Nic

        # The shebang line should be pure ASCII: use symlink jeżeli possible.
        # See issue #7668.
        jeżeli support.can_symlink():
            self.pythonexe = os.path.join(self.parent_dir, 'python')
            os.symlink(sys.executable, self.pythonexe)
        inaczej:
            self.pythonexe = sys.executable

        spróbuj:
            # The python executable path jest written jako the first line of the
            # CGI Python script. The encoding cookie cannot be used, oraz so the
            # path should be encodable to the default script encoding (utf-8)
            self.pythonexe.encode('utf-8')
        wyjąwszy UnicodeEncodeError:
            self.tearDown()
            self.skipTest("Python executable path jest nie encodable to utf-8")

        self.nocgi_path = os.path.join(self.parent_dir, 'nocgi.py')
        przy open(self.nocgi_path, 'w') jako fp:
            fp.write(cgi_file1 % self.pythonexe)
        os.chmod(self.nocgi_path, 0o777)

        self.file1_path = os.path.join(self.cgi_dir, 'file1.py')
        przy open(self.file1_path, 'w', encoding='utf-8') jako file1:
            file1.write(cgi_file1 % self.pythonexe)
        os.chmod(self.file1_path, 0o777)

        self.file2_path = os.path.join(self.cgi_dir, 'file2.py')
        przy open(self.file2_path, 'w', encoding='utf-8') jako file2:
            file2.write(cgi_file2 % self.pythonexe)
        os.chmod(self.file2_path, 0o777)

        self.file3_path = os.path.join(self.cgi_child_dir, 'file3.py')
        przy open(self.file3_path, 'w', encoding='utf-8') jako file3:
            file3.write(cgi_file1 % self.pythonexe)
        os.chmod(self.file3_path, 0o777)

        os.chdir(self.parent_dir)

    def tearDown(self):
        spróbuj:
            os.chdir(self.cwd)
            jeżeli self.pythonexe != sys.executable:
                os.remove(self.pythonexe)
            jeżeli self.nocgi_path:
                os.remove(self.nocgi_path)
            jeżeli self.file1_path:
                os.remove(self.file1_path)
            jeżeli self.file2_path:
                os.remove(self.file2_path)
            jeżeli self.file3_path:
                os.remove(self.file3_path)
            os.rmdir(self.cgi_child_dir)
            os.rmdir(self.cgi_dir)
            os.rmdir(self.parent_dir)
        w_końcu:
            BaseTestCase.tearDown(self)

    def test_url_collapse_path(self):
        # verify tail jest the last portion oraz head jest the rest on proper urls
        test_vectors = {
            '': '//',
            '..': IndexError,
            '/.//..': IndexError,
            '/': '//',
            '//': '//',
            '/\\': '//\\',
            '/.//': '//',
            'cgi-bin/file1.py': '/cgi-bin/file1.py',
            '/cgi-bin/file1.py': '/cgi-bin/file1.py',
            'a': '//a',
            '/a': '//a',
            '//a': '//a',
            './a': '//a',
            './C:/': '/C:/',
            '/a/b': '/a/b',
            '/a/b/': '/a/b/',
            '/a/b/.': '/a/b/',
            '/a/b/c/..': '/a/b/',
            '/a/b/c/../d': '/a/b/d',
            '/a/b/c/../d/e/../f': '/a/b/d/f',
            '/a/b/c/../d/e/../../f': '/a/b/f',
            '/a/b/c/../d/e/.././././..//f': '/a/b/f',
            '../a/b/c/../d/e/.././././..//f': IndexError,
            '/a/b/c/../d/e/../../../f': '/a/f',
            '/a/b/c/../d/e/../../../../f': '//f',
            '/a/b/c/../d/e/../../../../../f': IndexError,
            '/a/b/c/../d/e/../../../../f/..': '//',
            '/a/b/c/../d/e/../../../../f/../.': '//',
        }
        dla path, expected w test_vectors.items():
            jeżeli isinstance(expected, type) oraz issubclass(expected, Exception):
                self.assertRaises(expected,
                                  server._url_collapse_path, path)
            inaczej:
                actual = server._url_collapse_path(path)
                self.assertEqual(expected, actual,
                                 msg='path = %r\nGot:    %r\nWanted: %r' %
                                 (path, actual, expected))

    def test_headers_and_content(self):
        res = self.request('/cgi-bin/file1.py')
        self.assertEqual(
            (res.read(), res.getheader('Content-type'), res.status),
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK))

    def test_issue19435(self):
        res = self.request('///////////nocgi.py/../cgi-bin/nothere.sh')
        self.assertEqual(res.status, HTTPStatus.NOT_FOUND)

    def test_post(self):
        params = urllib.parse.urlencode(
            {'spam' : 1, 'eggs' : 'python', 'bacon' : 123456})
        headers = {'Content-type' : 'application/x-www-form-urlencoded'}
        res = self.request('/cgi-bin/file2.py', 'POST', params, headers)

        self.assertEqual(res.read(), b'1, python, 123456' + self.linesep)

    def test_invaliduri(self):
        res = self.request('/cgi-bin/invalid')
        res.read()
        self.assertEqual(res.status, HTTPStatus.NOT_FOUND)

    def test_authorization(self):
        headers = {b'Authorization' : b'Basic ' +
                   base64.b64encode(b'username:pass')}
        res = self.request('/cgi-bin/file1.py', 'GET', headers=headers)
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))

    def test_no_leading_slash(self):
        # http://bugs.python.org/issue2254
        res = self.request('cgi-bin/file1.py')
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))

    def test_os_environ_is_not_altered(self):
        signature = "Test CGI Server"
        os.environ['SERVER_SOFTWARE'] = signature
        res = self.request('/cgi-bin/file1.py')
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))
        self.assertEqual(os.environ['SERVER_SOFTWARE'], signature)

    def test_urlquote_decoding_in_cgi_check(self):
        res = self.request('/cgi-bin%2ffile1.py')
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))

    def test_nested_cgi_path_issue21323(self):
        res = self.request('/cgi-bin/child-dir/file3.py')
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))


klasa SocketlessRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self):
        self.get_called = Nieprawda
        self.protocol_version = "HTTP/1.1"

    def do_GET(self):
        self.get_called = Prawda
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body>Data</body></html>\r\n')

    def log_message(self, format, *args):
        dalej

klasa RejectingSocketlessRequestHandler(SocketlessRequestHandler):
    def handle_expect_100(self):
        self.send_error(HTTPStatus.EXPECTATION_FAILED)
        zwróć Nieprawda


klasa AuditableBytesIO:

    def __init__(self):
        self.datas = []

    def write(self, data):
        self.datas.append(data)

    def getData(self):
        zwróć b''.join(self.datas)

    @property
    def numWrites(self):
        zwróć len(self.datas)


klasa BaseHTTPRequestHandlerTestCase(unittest.TestCase):
    """Test the functionality of the BaseHTTPServer.

       Test the support dla the Expect 100-continue header.
       """

    HTTPResponseMatch = re.compile(b'HTTP/1.[0-9]+ 200 OK')

    def setUp (self):
        self.handler = SocketlessRequestHandler()

    def send_typical_request(self, message):
        input = BytesIO(message)
        output = BytesIO()
        self.handler.rfile = input
        self.handler.wfile = output
        self.handler.handle_one_request()
        output.seek(0)
        zwróć output.readlines()

    def verify_get_called(self):
        self.assertPrawda(self.handler.get_called)

    def verify_expected_headers(self, headers):
        dla fieldName w b'Server: ', b'Date: ', b'Content-Type: ':
            self.assertEqual(sum(h.startswith(fieldName) dla h w headers), 1)

    def verify_http_server_response(self, response):
        match = self.HTTPResponseMatch.search(response)
        self.assertIsNotNic(match)

    def test_http_1_1(self):
        result = self.send_typical_request(b'GET / HTTP/1.1\r\n\r\n')
        self.verify_http_server_response(result[0])
        self.verify_expected_headers(result[1:-1])
        self.verify_get_called()
        self.assertEqual(result[-1], b'<html><body>Data</body></html>\r\n')
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.1')
        self.assertEqual(self.handler.command, 'GET')
        self.assertEqual(self.handler.path, '/')
        self.assertEqual(self.handler.request_version, 'HTTP/1.1')
        self.assertSequenceEqual(self.handler.headers.items(), ())

    def test_http_1_0(self):
        result = self.send_typical_request(b'GET / HTTP/1.0\r\n\r\n')
        self.verify_http_server_response(result[0])
        self.verify_expected_headers(result[1:-1])
        self.verify_get_called()
        self.assertEqual(result[-1], b'<html><body>Data</body></html>\r\n')
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.0')
        self.assertEqual(self.handler.command, 'GET')
        self.assertEqual(self.handler.path, '/')
        self.assertEqual(self.handler.request_version, 'HTTP/1.0')
        self.assertSequenceEqual(self.handler.headers.items(), ())

    def test_http_0_9(self):
        result = self.send_typical_request(b'GET / HTTP/0.9\r\n\r\n')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], b'<html><body>Data</body></html>\r\n')
        self.verify_get_called()

    def test_with_continue_1_0(self):
        result = self.send_typical_request(b'GET / HTTP/1.0\r\nExpect: 100-continue\r\n\r\n')
        self.verify_http_server_response(result[0])
        self.verify_expected_headers(result[1:-1])
        self.verify_get_called()
        self.assertEqual(result[-1], b'<html><body>Data</body></html>\r\n')
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.0')
        self.assertEqual(self.handler.command, 'GET')
        self.assertEqual(self.handler.path, '/')
        self.assertEqual(self.handler.request_version, 'HTTP/1.0')
        headers = (("Expect", "100-continue"),)
        self.assertSequenceEqual(self.handler.headers.items(), headers)

    def test_with_continue_1_1(self):
        result = self.send_typical_request(b'GET / HTTP/1.1\r\nExpect: 100-continue\r\n\r\n')
        self.assertEqual(result[0], b'HTTP/1.1 100 Continue\r\n')
        self.assertEqual(result[1], b'\r\n')
        self.assertEqual(result[2], b'HTTP/1.1 200 OK\r\n')
        self.verify_expected_headers(result[2:-1])
        self.verify_get_called()
        self.assertEqual(result[-1], b'<html><body>Data</body></html>\r\n')
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.1')
        self.assertEqual(self.handler.command, 'GET')
        self.assertEqual(self.handler.path, '/')
        self.assertEqual(self.handler.request_version, 'HTTP/1.1')
        headers = (("Expect", "100-continue"),)
        self.assertSequenceEqual(self.handler.headers.items(), headers)

    def test_header_buffering_of_send_error(self):

        input = BytesIO(b'GET / HTTP/1.1\r\n\r\n')
        output = AuditableBytesIO()
        handler = SocketlessRequestHandler()
        handler.rfile = input
        handler.wfile = output
        handler.request_version = 'HTTP/1.1'
        handler.requestline = ''
        handler.command = Nic

        handler.send_error(418)
        self.assertEqual(output.numWrites, 2)

    def test_header_buffering_of_send_response_only(self):

        input = BytesIO(b'GET / HTTP/1.1\r\n\r\n')
        output = AuditableBytesIO()
        handler = SocketlessRequestHandler()
        handler.rfile = input
        handler.wfile = output
        handler.request_version = 'HTTP/1.1'

        handler.send_response_only(418)
        self.assertEqual(output.numWrites, 0)
        handler.end_headers()
        self.assertEqual(output.numWrites, 1)

    def test_header_buffering_of_send_header(self):

        input = BytesIO(b'GET / HTTP/1.1\r\n\r\n')
        output = AuditableBytesIO()
        handler = SocketlessRequestHandler()
        handler.rfile = input
        handler.wfile = output
        handler.request_version = 'HTTP/1.1'

        handler.send_header('Foo', 'foo')
        handler.send_header('bar', 'bar')
        self.assertEqual(output.numWrites, 0)
        handler.end_headers()
        self.assertEqual(output.getData(), b'Foo: foo\r\nbar: bar\r\n\r\n')
        self.assertEqual(output.numWrites, 1)

    def test_header_unbuffered_when_continue(self):

        def _readAndReseek(f):
            pos = f.tell()
            f.seek(0)
            data = f.read()
            f.seek(pos)
            zwróć data

        input = BytesIO(b'GET / HTTP/1.1\r\nExpect: 100-continue\r\n\r\n')
        output = BytesIO()
        self.handler.rfile = input
        self.handler.wfile = output
        self.handler.request_version = 'HTTP/1.1'

        self.handler.handle_one_request()
        self.assertNotEqual(_readAndReseek(output), b'')
        result = _readAndReseek(output).split(b'\r\n')
        self.assertEqual(result[0], b'HTTP/1.1 100 Continue')
        self.assertEqual(result[1], b'')
        self.assertEqual(result[2], b'HTTP/1.1 200 OK')

    def test_with_continue_rejected(self):
        usual_handler = self.handler        # Save to avoid przerwijing any subsequent tests.
        self.handler = RejectingSocketlessRequestHandler()
        result = self.send_typical_request(b'GET / HTTP/1.1\r\nExpect: 100-continue\r\n\r\n')
        self.assertEqual(result[0], b'HTTP/1.1 417 Expectation Failed\r\n')
        self.verify_expected_headers(result[1:-1])
        # The expect handler should short circuit the usual get method by
        # returning false here, so get_called should be false
        self.assertNieprawda(self.handler.get_called)
        self.assertEqual(sum(r == b'Connection: close\r\n' dla r w result[1:-1]), 1)
        self.handler = usual_handler        # Restore to avoid przerwijing any subsequent tests.

    def test_request_length(self):
        # Issue #10714: huge request lines are discarded, to avoid Denial
        # of Service attacks.
        result = self.send_typical_request(b'GET ' + b'x' * 65537)
        self.assertEqual(result[0], b'HTTP/1.1 414 Request-URI Too Long\r\n')
        self.assertNieprawda(self.handler.get_called)
        self.assertIsInstance(self.handler.requestline, str)

    def test_header_length(self):
        # Issue #6791: same dla headers
        result = self.send_typical_request(
            b'GET / HTTP/1.1\r\nX-Foo: bar' + b'r' * 65537 + b'\r\n\r\n')
        self.assertEqual(result[0], b'HTTP/1.1 400 Line too long\r\n')
        self.assertNieprawda(self.handler.get_called)
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.1')

    def test_close_connection(self):
        # handle_one_request() should be repeatedly called until
        # it sets close_connection
        def handle_one_request():
            self.handler.close_connection = next(close_values)
        self.handler.handle_one_request = handle_one_request

        close_values = iter((Prawda,))
        self.handler.handle()
        self.assertRaises(StopIteration, next, close_values)

        close_values = iter((Nieprawda, Nieprawda, Prawda))
        self.handler.handle()
        self.assertRaises(StopIteration, next, close_values)

klasa SimpleHTTPRequestHandlerTestCase(unittest.TestCase):
    """ Test url parsing """
    def setUp(self):
        self.translated = os.getcwd()
        self.translated = os.path.join(self.translated, 'filename')
        self.handler = SocketlessRequestHandler()

    def test_query_arguments(self):
        path = self.handler.translate_path('/filename')
        self.assertEqual(path, self.translated)
        path = self.handler.translate_path('/filename?foo=bar')
        self.assertEqual(path, self.translated)
        path = self.handler.translate_path('/filename?a=b&spam=eggs#zot')
        self.assertEqual(path, self.translated)

    def test_start_with_double_slash(self):
        path = self.handler.translate_path('//filename')
        self.assertEqual(path, self.translated)
        path = self.handler.translate_path('//filename?foo=bar')
        self.assertEqual(path, self.translated)


klasa MiscTestCase(unittest.TestCase):
    def test_all(self):
        expected = []
        blacklist = {'executable', 'nobody_uid', 'test'}
        dla name w dir(server):
            jeżeli name.startswith('_') albo name w blacklist:
                kontynuuj
            module_object = getattr(server, name)
            jeżeli getattr(module_object, '__module__', Nic) == 'http.server':
                expected.append(name)
        self.assertCountEqual(server.__all__, expected)


def test_main(verbose=Nic):
    cwd = os.getcwd()
    spróbuj:
        support.run_unittest(
            RequestHandlerLoggingTestCase,
            BaseHTTPRequestHandlerTestCase,
            BaseHTTPServerTestCase,
            SimpleHTTPServerTestCase,
            CGIHTTPServerTestCase,
            SimpleHTTPRequestHandlerTestCase,
            MiscTestCase,
        )
    w_końcu:
        os.chdir(cwd)

jeżeli __name__ == '__main__':
    test_main()
