z __future__ zaimportuj nested_scopes    # Backward compat dla 2.1
z unittest zaimportuj TestCase
z wsgiref.util zaimportuj setup_testing_defaults
z wsgiref.headers zaimportuj Headers
z wsgiref.handlers zaimportuj BaseHandler, BaseCGIHandler
z wsgiref zaimportuj util
z wsgiref.validate zaimportuj validator
z wsgiref.simple_server zaimportuj WSGIServer, WSGIRequestHandler, demo_app
z wsgiref.simple_server zaimportuj make_server
z io zaimportuj StringIO, BytesIO, BufferedReader
z socketserver zaimportuj BaseServer
z platform zaimportuj python_implementation

zaimportuj os
zaimportuj re
zaimportuj sys

z test zaimportuj support

klasa MockServer(WSGIServer):
    """Non-socket HTTP server"""

    def __init__(self, server_address, RequestHandlerClass):
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.server_bind()

    def server_bind(self):
        host, port = self.server_address
        self.server_name = host
        self.server_port = port
        self.setup_environ()


klasa MockHandler(WSGIRequestHandler):
    """Non-socket HTTP handler"""
    def setup(self):
        self.connection = self.request
        self.rfile, self.wfile = self.connection

    def finish(self):
        dalej


def hello_app(environ,start_response):
    start_response("200 OK", [
        ('Content-Type','text/plain'),
        ('Date','Mon, 05 Jun 2006 18:49:54 GMT')
    ])
    zwróć [b"Hello, world!"]


def header_app(environ, start_response):
    start_response("200 OK", [
        ('Content-Type', 'text/plain'),
        ('Date', 'Mon, 05 Jun 2006 18:49:54 GMT')
    ])
    zwróć [';'.join([
        environ['HTTP_X_TEST_HEADER'], environ['QUERY_STRING'],
        environ['PATH_INFO']
    ]).encode('iso-8859-1')]


def run_amock(app=hello_app, data=b"GET / HTTP/1.0\n\n"):
    server = make_server("", 80, app, MockServer, MockHandler)
    inp = BufferedReader(BytesIO(data))
    out = BytesIO()
    olderr = sys.stderr
    err = sys.stderr = StringIO()

    spróbuj:
        server.finish_request((inp, out), ("127.0.0.1",8888))
    w_końcu:
        sys.stderr = olderr

    zwróć out.getvalue(), err.getvalue()

def compare_generic_iter(make_it,match):
    """Utility to compare a generic 2.1/2.2+ iterator przy an iterable

    If running under Python 2.2+, this tests the iterator using iter()/next(),
    jako well jako __getitem__.  'make_it' must be a function returning a fresh
    iterator to be tested (since this may test the iterator twice)."""

    it = make_it()
    n = 0
    dla item w match:
        jeżeli nie it[n]==item: podnieś AssertionError
        n+=1
    spróbuj:
        it[n]
    wyjąwszy IndexError:
        dalej
    inaczej:
        podnieś AssertionError("Too many items z __getitem__",it)

    spróbuj:
        iter, StopIteration
    wyjąwszy NameError:
        dalej
    inaczej:
        # Only test iter mode under 2.2+
        it = make_it()
        jeżeli nie iter(it) jest it: podnieś AssertionError
        dla item w match:
            jeżeli nie next(it) == item: podnieś AssertionError
        spróbuj:
            next(it)
        wyjąwszy StopIteration:
            dalej
        inaczej:
            podnieś AssertionError("Too many items z .__next__()", it)


klasa IntegrationTests(TestCase):

    def check_hello(self, out, has_length=Prawda):
        pyver = (python_implementation() + "/" +
                sys.version.split()[0])
        self.assertEqual(out,
            ("HTTP/1.0 200 OK\r\n"
            "Server: WSGIServer/0.2 " + pyver +"\r\n"
            "Content-Type: text/plain\r\n"
            "Date: Mon, 05 Jun 2006 18:49:54 GMT\r\n" +
            (has_length oraz  "Content-Length: 13\r\n" albo "") +
            "\r\n"
            "Hello, world!").encode("iso-8859-1")
        )

    def test_plain_hello(self):
        out, err = run_amock()
        self.check_hello(out)

    def test_environ(self):
        request = (
            b"GET /p%61th/?query=test HTTP/1.0\n"
            b"X-Test-Header: Python test \n"
            b"X-Test-Header: Python test 2\n"
            b"Content-Length: 0\n\n"
        )
        out, err = run_amock(header_app, request)
        self.assertEqual(
            out.splitlines()[-1],
            b"Python test,Python test 2;query=test;/path/"
        )

    def test_request_length(self):
        out, err = run_amock(data=b"GET " + (b"x" * 65537) + b" HTTP/1.0\n\n")
        self.assertEqual(out.splitlines()[0],
                         b"HTTP/1.0 414 Request-URI Too Long")

    def test_validated_hello(self):
        out, err = run_amock(validator(hello_app))
        # the middleware doesn't support len(), so content-length isn't there
        self.check_hello(out, has_length=Nieprawda)

    def test_simple_validation_error(self):
        def bad_app(environ,start_response):
            start_response("200 OK", ('Content-Type','text/plain'))
            zwróć ["Hello, world!"]
        out, err = run_amock(validator(bad_app))
        self.assertPrawda(out.endswith(
            b"A server error occurred.  Please contact the administrator."
        ))
        self.assertEqual(
            err.splitlines()[-2],
            "AssertionError: Headers (('Content-Type', 'text/plain')) must"
            " be of type list: <class 'tuple'>"
        )

    def test_wsgi_input(self):
        def bad_app(e,s):
            e["wsgi.input"].read()
            s("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
            zwróć [b"data"]
        out, err = run_amock(validator(bad_app))
        self.assertPrawda(out.endswith(
            b"A server error occurred.  Please contact the administrator."
        ))
        self.assertEqual(
            err.splitlines()[-2], "AssertionError"
        )

    def test_bytes_validation(self):
        def app(e, s):
            s("200 OK", [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Date", "Wed, 24 Dec 2008 13:29:32 GMT"),
                ])
            zwróć [b"data"]
        out, err = run_amock(validator(app))
        self.assertPrawda(err.endswith('"GET / HTTP/1.0" 200 4\n'))
        ver = sys.version.split()[0].encode('ascii')
        py  = python_implementation().encode('ascii')
        pyver = py + b"/" + ver
        self.assertEqual(
                b"HTTP/1.0 200 OK\r\n"
                b"Server: WSGIServer/0.2 "+ pyver + b"\r\n"
                b"Content-Type: text/plain; charset=utf-8\r\n"
                b"Date: Wed, 24 Dec 2008 13:29:32 GMT\r\n"
                b"\r\n"
                b"data",
                out)


klasa UtilityTests(TestCase):

    def checkShift(self,sn_in,pi_in,part,sn_out,pi_out):
        env = {'SCRIPT_NAME':sn_in,'PATH_INFO':pi_in}
        util.setup_testing_defaults(env)
        self.assertEqual(util.shift_path_info(env),part)
        self.assertEqual(env['PATH_INFO'],pi_out)
        self.assertEqual(env['SCRIPT_NAME'],sn_out)
        zwróć env

    def checkDefault(self, key, value, alt=Nic):
        # Check defaulting when empty
        env = {}
        util.setup_testing_defaults(env)
        jeżeli isinstance(value, StringIO):
            self.assertIsInstance(env[key], StringIO)
        albo_inaczej isinstance(value,BytesIO):
            self.assertIsInstance(env[key],BytesIO)
        inaczej:
            self.assertEqual(env[key], value)

        # Check existing value
        env = {key:alt}
        util.setup_testing_defaults(env)
        self.assertIs(env[key], alt)

    def checkCrossDefault(self,key,value,**kw):
        util.setup_testing_defaults(kw)
        self.assertEqual(kw[key],value)

    def checkAppURI(self,uri,**kw):
        util.setup_testing_defaults(kw)
        self.assertEqual(util.application_uri(kw),uri)

    def checkReqURI(self,uri,query=1,**kw):
        util.setup_testing_defaults(kw)
        self.assertEqual(util.request_uri(kw,query),uri)

    def checkFW(self,text,size,match):

        def make_it(text=text,size=size):
            zwróć util.FileWrapper(StringIO(text),size)

        compare_generic_iter(make_it,match)

        it = make_it()
        self.assertNieprawda(it.filelike.closed)

        dla item w it:
            dalej

        self.assertNieprawda(it.filelike.closed)

        it.close()
        self.assertPrawda(it.filelike.closed)

    def testSimpleShifts(self):
        self.checkShift('','/', '', '/', '')
        self.checkShift('','/x', 'x', '/x', '')
        self.checkShift('/','', Nic, '/', '')
        self.checkShift('/a','/x/y', 'x', '/a/x', '/y')
        self.checkShift('/a','/x/',  'x', '/a/x', '/')

    def testNormalizedShifts(self):
        self.checkShift('/a/b', '/../y', '..', '/a', '/y')
        self.checkShift('', '/../y', '..', '', '/y')
        self.checkShift('/a/b', '//y', 'y', '/a/b/y', '')
        self.checkShift('/a/b', '//y/', 'y', '/a/b/y', '/')
        self.checkShift('/a/b', '/./y', 'y', '/a/b/y', '')
        self.checkShift('/a/b', '/./y/', 'y', '/a/b/y', '/')
        self.checkShift('/a/b', '///./..//y/.//', '..', '/a', '/y/')
        self.checkShift('/a/b', '///', '', '/a/b/', '')
        self.checkShift('/a/b', '/.//', '', '/a/b/', '')
        self.checkShift('/a/b', '/x//', 'x', '/a/b/x', '/')
        self.checkShift('/a/b', '/.', Nic, '/a/b', '')

    def testDefaults(self):
        dla key, value w [
            ('SERVER_NAME','127.0.0.1'),
            ('SERVER_PORT', '80'),
            ('SERVER_PROTOCOL','HTTP/1.0'),
            ('HTTP_HOST','127.0.0.1'),
            ('REQUEST_METHOD','GET'),
            ('SCRIPT_NAME',''),
            ('PATH_INFO','/'),
            ('wsgi.version', (1,0)),
            ('wsgi.run_once', 0),
            ('wsgi.multithread', 0),
            ('wsgi.multiprocess', 0),
            ('wsgi.input', BytesIO()),
            ('wsgi.errors', StringIO()),
            ('wsgi.url_scheme','http'),
        ]:
            self.checkDefault(key,value)

    def testCrossDefaults(self):
        self.checkCrossDefault('HTTP_HOST',"foo.bar",SERVER_NAME="foo.bar")
        self.checkCrossDefault('wsgi.url_scheme',"https",HTTPS="on")
        self.checkCrossDefault('wsgi.url_scheme',"https",HTTPS="1")
        self.checkCrossDefault('wsgi.url_scheme',"https",HTTPS="yes")
        self.checkCrossDefault('wsgi.url_scheme',"http",HTTPS="foo")
        self.checkCrossDefault('SERVER_PORT',"80",HTTPS="foo")
        self.checkCrossDefault('SERVER_PORT',"443",HTTPS="on")

    def testGuessScheme(self):
        self.assertEqual(util.guess_scheme({}), "http")
        self.assertEqual(util.guess_scheme({'HTTPS':"foo"}), "http")
        self.assertEqual(util.guess_scheme({'HTTPS':"on"}), "https")
        self.assertEqual(util.guess_scheme({'HTTPS':"yes"}), "https")
        self.assertEqual(util.guess_scheme({'HTTPS':"1"}), "https")

    def testAppURIs(self):
        self.checkAppURI("http://127.0.0.1/")
        self.checkAppURI("http://127.0.0.1/spam", SCRIPT_NAME="/spam")
        self.checkAppURI("http://127.0.0.1/sp%E4m", SCRIPT_NAME="/sp\xe4m")
        self.checkAppURI("http://spam.example.com:2071/",
            HTTP_HOST="spam.example.com:2071", SERVER_PORT="2071")
        self.checkAppURI("http://spam.example.com/",
            SERVER_NAME="spam.example.com")
        self.checkAppURI("http://127.0.0.1/",
            HTTP_HOST="127.0.0.1", SERVER_NAME="spam.example.com")
        self.checkAppURI("https://127.0.0.1/", HTTPS="on")
        self.checkAppURI("http://127.0.0.1:8000/", SERVER_PORT="8000",
            HTTP_HOST=Nic)

    def testReqURIs(self):
        self.checkReqURI("http://127.0.0.1/")
        self.checkReqURI("http://127.0.0.1/spam", SCRIPT_NAME="/spam")
        self.checkReqURI("http://127.0.0.1/sp%E4m", SCRIPT_NAME="/sp\xe4m")
        self.checkReqURI("http://127.0.0.1/spammity/spam",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam")
        self.checkReqURI("http://127.0.0.1/spammity/sp%E4m",
            SCRIPT_NAME="/spammity", PATH_INFO="/sp\xe4m")
        self.checkReqURI("http://127.0.0.1/spammity/spam;ham",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam;ham")
        self.checkReqURI("http://127.0.0.1/spammity/spam;cookie=1234,5678",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam;cookie=1234,5678")
        self.checkReqURI("http://127.0.0.1/spammity/spam?say=ni",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam",QUERY_STRING="say=ni")
        self.checkReqURI("http://127.0.0.1/spammity/spam?s%E4y=ni",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam",QUERY_STRING="s%E4y=ni")
        self.checkReqURI("http://127.0.0.1/spammity/spam", 0,
            SCRIPT_NAME="/spammity", PATH_INFO="/spam",QUERY_STRING="say=ni")

    def testFileWrapper(self):
        self.checkFW("xyz"*50, 120, ["xyz"*40,"xyz"*10])

    def testHopByHop(self):
        dla hop w (
            "Connection Keep-Alive Proxy-Authenticate Proxy-Authorization "
            "TE Trailers Transfer-Encoding Upgrade"
        ).split():
            dla alt w hop, hop.title(), hop.upper(), hop.lower():
                self.assertPrawda(util.is_hop_by_hop(alt))

        # Not comprehensive, just a few random header names
        dla hop w (
            "Accept Cache-Control Date Pragma Trailer Via Warning"
        ).split():
            dla alt w hop, hop.title(), hop.upper(), hop.lower():
                self.assertNieprawda(util.is_hop_by_hop(alt))

klasa HeaderTests(TestCase):

    def testMappingInterface(self):
        test = [('x','y')]
        self.assertEqual(len(Headers()), 0)
        self.assertEqual(len(Headers([])),0)
        self.assertEqual(len(Headers(test[:])),1)
        self.assertEqual(Headers(test[:]).keys(), ['x'])
        self.assertEqual(Headers(test[:]).values(), ['y'])
        self.assertEqual(Headers(test[:]).items(), test)
        self.assertIsNot(Headers(test).items(), test)  # must be copy!

        h = Headers()
        usuń h['foo']   # should nie podnieś an error

        h['Foo'] = 'bar'
        dla m w h.__contains__, h.get, h.get_all, h.__getitem__:
            self.assertPrawda(m('foo'))
            self.assertPrawda(m('Foo'))
            self.assertPrawda(m('FOO'))
            self.assertNieprawda(m('bar'))

        self.assertEqual(h['foo'],'bar')
        h['foo'] = 'baz'
        self.assertEqual(h['FOO'],'baz')
        self.assertEqual(h.get_all('foo'),['baz'])

        self.assertEqual(h.get("foo","whee"), "baz")
        self.assertEqual(h.get("zoo","whee"), "whee")
        self.assertEqual(h.setdefault("foo","whee"), "baz")
        self.assertEqual(h.setdefault("zoo","whee"), "whee")
        self.assertEqual(h["foo"],"baz")
        self.assertEqual(h["zoo"],"whee")

    def testRequireList(self):
        self.assertRaises(TypeError, Headers, "foo")

    def testExtras(self):
        h = Headers()
        self.assertEqual(str(h),'\r\n')

        h.add_header('foo','bar',baz="spam")
        self.assertEqual(h['foo'], 'bar; baz="spam"')
        self.assertEqual(str(h),'foo: bar; baz="spam"\r\n\r\n')

        h.add_header('Foo','bar',cheese=Nic)
        self.assertEqual(h.get_all('foo'),
            ['bar; baz="spam"', 'bar; cheese'])

        self.assertEqual(str(h),
            'foo: bar; baz="spam"\r\n'
            'Foo: bar; cheese\r\n'
            '\r\n'
        )

klasa ErrorHandler(BaseCGIHandler):
    """Simple handler subclass dla testing BaseHandler"""

    # BaseHandler records the OS environment at zaimportuj time, but envvars
    # might have been changed later by other tests, which trips up
    # HandlerTests.testEnviron().
    os_environ = dict(os.environ.items())

    def __init__(self,**kw):
        setup_testing_defaults(kw)
        BaseCGIHandler.__init__(
            self, BytesIO(), BytesIO(), StringIO(), kw,
            multithread=Prawda, multiprocess=Prawda
        )

klasa TestHandler(ErrorHandler):
    """Simple handler subclass dla testing BaseHandler, w/error dalejthru"""

    def handle_error(self):
        podnieś   # dla testing, we want to see what's happening


klasa HandlerTests(TestCase):

    def checkEnvironAttrs(self, handler):
        env = handler.environ
        dla attr w [
            'version','multithread','multiprocess','run_once','file_wrapper'
        ]:
            jeżeli attr=='file_wrapper' oraz handler.wsgi_file_wrapper jest Nic:
                kontynuuj
            self.assertEqual(getattr(handler,'wsgi_'+attr),env['wsgi.'+attr])

    def checkOSEnviron(self,handler):
        empty = {}; setup_testing_defaults(empty)
        env = handler.environ
        z os zaimportuj environ
        dla k,v w environ.items():
            jeżeli k nie w empty:
                self.assertEqual(env[k],v)
        dla k,v w empty.items():
            self.assertIn(k, env)

    def testEnviron(self):
        h = TestHandler(X="Y")
        h.setup_environ()
        self.checkEnvironAttrs(h)
        self.checkOSEnviron(h)
        self.assertEqual(h.environ["X"],"Y")

    def testCGIEnviron(self):
        h = BaseCGIHandler(Nic,Nic,Nic,{})
        h.setup_environ()
        dla key w 'wsgi.url_scheme', 'wsgi.input', 'wsgi.errors':
            self.assertIn(key, h.environ)

    def testScheme(self):
        h=TestHandler(HTTPS="on"); h.setup_environ()
        self.assertEqual(h.environ['wsgi.url_scheme'],'https')
        h=TestHandler(); h.setup_environ()
        self.assertEqual(h.environ['wsgi.url_scheme'],'http')

    def testAbstractMethods(self):
        h = BaseHandler()
        dla name w [
            '_flush','get_stdin','get_stderr','add_cgi_vars'
        ]:
            self.assertRaises(NotImplementedError, getattr(h,name))
        self.assertRaises(NotImplementedError, h._write, "test")

    def testContentLength(self):
        # Demo one reason iteration jest better than write()...  ;)

        def trivial_app1(e,s):
            s('200 OK',[])
            zwróć [e['wsgi.url_scheme'].encode('iso-8859-1')]

        def trivial_app2(e,s):
            s('200 OK',[])(e['wsgi.url_scheme'].encode('iso-8859-1'))
            zwróć []

        def trivial_app3(e,s):
            s('200 OK',[])
            zwróć ['\u0442\u0435\u0441\u0442'.encode("utf-8")]

        def trivial_app4(e,s):
            # Simulate a response to a HEAD request
            s('200 OK',[('Content-Length', '12345')])
            zwróć []

        h = TestHandler()
        h.run(trivial_app1)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: 200 OK\r\n"
            "Content-Length: 4\r\n"
            "\r\n"
            "http").encode("iso-8859-1"))

        h = TestHandler()
        h.run(trivial_app2)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: 200 OK\r\n"
            "\r\n"
            "http").encode("iso-8859-1"))

        h = TestHandler()
        h.run(trivial_app3)
        self.assertEqual(h.stdout.getvalue(),
            b'Status: 200 OK\r\n'
            b'Content-Length: 8\r\n'
            b'\r\n'
            b'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82')

        h = TestHandler()
        h.run(trivial_app4)
        self.assertEqual(h.stdout.getvalue(),
            b'Status: 200 OK\r\n'
            b'Content-Length: 12345\r\n'
            b'\r\n')

    def testBasicErrorOutput(self):

        def non_error_app(e,s):
            s('200 OK',[])
            zwróć []

        def error_app(e,s):
            podnieś AssertionError("This should be caught by handler")

        h = ErrorHandler()
        h.run(non_error_app)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: 200 OK\r\n"
            "Content-Length: 0\r\n"
            "\r\n").encode("iso-8859-1"))
        self.assertEqual(h.stderr.getvalue(),"")

        h = ErrorHandler()
        h.run(error_app)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: %s\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: %d\r\n"
            "\r\n" % (h.error_status,len(h.error_body))).encode('iso-8859-1')
            + h.error_body)

        self.assertIn("AssertionError", h.stderr.getvalue())

    def testErrorAfterOutput(self):
        MSG = b"Some output has been sent"
        def error_app(e,s):
            s("200 OK",[])(MSG)
            podnieś AssertionError("This should be caught by handler")

        h = ErrorHandler()
        h.run(error_app)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: 200 OK\r\n"
            "\r\n".encode("iso-8859-1")+MSG))
        self.assertIn("AssertionError", h.stderr.getvalue())

    def testHeaderFormats(self):

        def non_error_app(e,s):
            s('200 OK',[])
            zwróć []

        stdpat = (
            r"HTTP/%s 200 OK\r\n"
            r"Date: \w{3}, [ 0123]\d \w{3} \d{4} \d\d:\d\d:\d\d GMT\r\n"
            r"%s" r"Content-Length: 0\r\n" r"\r\n"
        )
        shortpat = (
            "Status: 200 OK\r\n" "Content-Length: 0\r\n" "\r\n"
        ).encode("iso-8859-1")

        dla ssw w "FooBar/1.0", Nic:
            sw = ssw oraz "Server: %s\r\n" % ssw albo ""

            dla version w "1.0", "1.1":
                dla proto w "HTTP/0.9", "HTTP/1.0", "HTTP/1.1":

                    h = TestHandler(SERVER_PROTOCOL=proto)
                    h.origin_server = Nieprawda
                    h.http_version = version
                    h.server_software = ssw
                    h.run(non_error_app)
                    self.assertEqual(shortpat,h.stdout.getvalue())

                    h = TestHandler(SERVER_PROTOCOL=proto)
                    h.origin_server = Prawda
                    h.http_version = version
                    h.server_software = ssw
                    h.run(non_error_app)
                    jeżeli proto=="HTTP/0.9":
                        self.assertEqual(h.stdout.getvalue(),b"")
                    inaczej:
                        self.assertPrawda(
                            re.match((stdpat%(version,sw)).encode("iso-8859-1"),
                                h.stdout.getvalue()),
                            ((stdpat%(version,sw)).encode("iso-8859-1"),
                                h.stdout.getvalue())
                        )

    def testBytesData(self):
        def app(e, s):
            s("200 OK", [
                ("Content-Type", "text/plain; charset=utf-8"),
                ])
            zwróć [b"data"]

        h = TestHandler()
        h.run(app)
        self.assertEqual(b"Status: 200 OK\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"Content-Length: 4\r\n"
            b"\r\n"
            b"data",
            h.stdout.getvalue())

    def testCloseOnError(self):
        side_effects = {'close_called': Nieprawda}
        MSG = b"Some output has been sent"
        def error_app(e,s):
            s("200 OK",[])(MSG)
            klasa CrashyIterable(object):
                def __iter__(self):
                    dopóki Prawda:
                        uzyskaj b'blah'
                        podnieś AssertionError("This should be caught by handler")
                def close(self):
                    side_effects['close_called'] = Prawda
            zwróć CrashyIterable()

        h = ErrorHandler()
        h.run(error_app)
        self.assertEqual(side_effects['close_called'], Prawda)


jeżeli __name__ == "__main__":
    unittest.main()
