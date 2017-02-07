"""Utilities shared by tests."""

zaimportuj collections
zaimportuj contextlib
zaimportuj io
zaimportuj logging
zaimportuj os
zaimportuj re
zaimportuj socket
zaimportuj socketserver
zaimportuj sys
zaimportuj tempfile
zaimportuj threading
zaimportuj time
zaimportuj unittest
z unittest zaimportuj mock

z http.server zaimportuj HTTPServer
z wsgiref.simple_server zaimportuj WSGIRequestHandler, WSGIServer

spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:  # pragma: no cover
    ssl = Nic

z . zaimportuj base_events
z . zaimportuj events
z . zaimportuj futures
z . zaimportuj selectors
z . zaimportuj tasks
z .coroutines zaimportuj coroutine
z .log zaimportuj logger


jeżeli sys.platform == 'win32':  # pragma: no cover
    z .windows_utils zaimportuj socketpair
inaczej:
    z socket zaimportuj socketpair  # pragma: no cover


def dummy_ssl_context():
    jeżeli ssl jest Nic:
        zwróć Nic
    inaczej:
        zwróć ssl.SSLContext(ssl.PROTOCOL_SSLv23)


def run_briefly(loop):
    @coroutine
    def once():
        dalej
    gen = once()
    t = loop.create_task(gen)
    # Don't log a warning jeżeli the task jest nie done after run_until_complete().
    # It occurs jeżeli the loop jest stopped albo jeżeli a task podnieśs a BaseException.
    t._log_destroy_pending = Nieprawda
    spróbuj:
        loop.run_until_complete(t)
    w_końcu:
        gen.close()


def run_until(loop, pred, timeout=30):
    deadline = time.time() + timeout
    dopóki nie pred():
        jeżeli timeout jest nie Nic:
            timeout = deadline - time.time()
            jeżeli timeout <= 0:
                podnieś futures.TimeoutError()
        loop.run_until_complete(tasks.sleep(0.001, loop=loop))


def run_once(loop):
    """loop.stop() schedules _raise_stop_error()
    oraz run_forever() runs until _raise_stop_error() callback.
    this wont work jeżeli test waits dla some IO events, because
    _raise_stop_error() runs before any of io events callbacks.
    """
    loop.stop()
    loop.run_forever()


klasa SilentWSGIRequestHandler(WSGIRequestHandler):

    def get_stderr(self):
        zwróć io.StringIO()

    def log_message(self, format, *args):
        dalej


klasa SilentWSGIServer(WSGIServer):

    request_timeout = 2

    def get_request(self):
        request, client_addr = super().get_request()
        request.settimeout(self.request_timeout)
        zwróć request, client_addr

    def handle_error(self, request, client_address):
        dalej


klasa SSLWSGIServerMixin:

    def finish_request(self, request, client_address):
        # The relative location of our test directory (which
        # contains the ssl key oraz certificate files) differs
        # between the stdlib oraz stand-alone asyncio.
        # Prefer our own jeżeli we can find it.
        here = os.path.join(os.path.dirname(__file__), '..', 'tests')
        jeżeli nie os.path.isdir(here):
            here = os.path.join(os.path.dirname(os.__file__),
                                'test', 'test_asyncio')
        keyfile = os.path.join(here, 'ssl_key.pem')
        certfile = os.path.join(here, 'ssl_cert.pem')
        ssock = ssl.wrap_socket(request,
                                keyfile=keyfile,
                                certfile=certfile,
                                server_side=Prawda)
        spróbuj:
            self.RequestHandlerClass(ssock, client_address, self)
            ssock.close()
        wyjąwszy OSError:
            # maybe socket has been closed by peer
            dalej


klasa SSLWSGIServer(SSLWSGIServerMixin, SilentWSGIServer):
    dalej


def _run_test_server(*, address, use_ssl=Nieprawda, server_cls, server_ssl_cls):

    def app(environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        zwróć [b'Test message']

    # Run the test WSGI server w a separate thread w order nie to
    # interfere przy event handling w the main thread
    server_class = server_ssl_cls jeżeli use_ssl inaczej server_cls
    httpd = server_class(address, SilentWSGIRequestHandler)
    httpd.set_app(app)
    httpd.address = httpd.server_address
    server_thread = threading.Thread(
        target=lambda: httpd.serve_forever(poll_interval=0.05))
    server_thread.start()
    spróbuj:
        uzyskaj httpd
    w_końcu:
        httpd.shutdown()
        httpd.server_close()
        server_thread.join()


jeżeli hasattr(socket, 'AF_UNIX'):

    klasa UnixHTTPServer(socketserver.UnixStreamServer, HTTPServer):

        def server_bind(self):
            socketserver.UnixStreamServer.server_bind(self)
            self.server_name = '127.0.0.1'
            self.server_port = 80


    klasa UnixWSGIServer(UnixHTTPServer, WSGIServer):

        request_timeout = 2

        def server_bind(self):
            UnixHTTPServer.server_bind(self)
            self.setup_environ()

        def get_request(self):
            request, client_addr = super().get_request()
            request.settimeout(self.request_timeout)
            # Code w the stdlib expects that get_request
            # will zwróć a socket oraz a tuple (host, port).
            # However, this isn't true dla UNIX sockets,
            # jako the second zwróć value will be a path;
            # hence we zwróć some fake data sufficient
            # to get the tests going
            zwróć request, ('127.0.0.1', '')


    klasa SilentUnixWSGIServer(UnixWSGIServer):

        def handle_error(self, request, client_address):
            dalej


    klasa UnixSSLWSGIServer(SSLWSGIServerMixin, SilentUnixWSGIServer):
        dalej


    def gen_unix_socket_path():
        przy tempfile.NamedTemporaryFile() jako file:
            zwróć file.name


    @contextlib.contextmanager
    def unix_socket_path():
        path = gen_unix_socket_path()
        spróbuj:
            uzyskaj path
        w_końcu:
            spróbuj:
                os.unlink(path)
            wyjąwszy OSError:
                dalej


    @contextlib.contextmanager
    def run_test_unix_server(*, use_ssl=Nieprawda):
        przy unix_socket_path() jako path:
            uzyskaj z _run_test_server(address=path, use_ssl=use_ssl,
                                        server_cls=SilentUnixWSGIServer,
                                        server_ssl_cls=UnixSSLWSGIServer)


@contextlib.contextmanager
def run_test_server(*, host='127.0.0.1', port=0, use_ssl=Nieprawda):
    uzyskaj z _run_test_server(address=(host, port), use_ssl=use_ssl,
                                server_cls=SilentWSGIServer,
                                server_ssl_cls=SSLWSGIServer)


def make_test_protocol(base):
    dct = {}
    dla name w dir(base):
        jeżeli name.startswith('__') oraz name.endswith('__'):
            # skip magic names
            kontynuuj
        dct[name] = MockCallback(return_value=Nic)
    zwróć type('TestProtocol', (base,) + base.__bases__, dct)()


klasa TestSelector(selectors.BaseSelector):

    def __init__(self):
        self.keys = {}

    def register(self, fileobj, events, data=Nic):
        key = selectors.SelectorKey(fileobj, 0, events, data)
        self.keys[fileobj] = key
        zwróć key

    def unregister(self, fileobj):
        zwróć self.keys.pop(fileobj)

    def select(self, timeout):
        zwróć []

    def get_map(self):
        zwróć self.keys


klasa TestLoop(base_events.BaseEventLoop):
    """Loop dla unittests.

    It manages self time directly.
    If something scheduled to be executed later then
    on next loop iteration after all ready handlers done
    generator dalejed to __init__ jest calling.

    Generator should be like this:

        def gen():
            ...
            when = uzyskaj ...
            ... = uzyskaj time_advance

    Value returned by uzyskaj jest absolute time of next scheduled handler.
    Value dalejed to uzyskaj jest time advance to move loop's time forward.
    """

    def __init__(self, gen=Nic):
        super().__init__()

        jeżeli gen jest Nic:
            def gen():
                uzyskaj
            self._check_on_close = Nieprawda
        inaczej:
            self._check_on_close = Prawda

        self._gen = gen()
        next(self._gen)
        self._time = 0
        self._clock_resolution = 1e-9
        self._timers = []
        self._selector = TestSelector()

        self.readers = {}
        self.writers = {}
        self.reset_counters()

    def time(self):
        zwróć self._time

    def advance_time(self, advance):
        """Move test time forward."""
        jeżeli advance:
            self._time += advance

    def close(self):
        super().close()
        jeżeli self._check_on_close:
            spróbuj:
                self._gen.send(0)
            wyjąwszy StopIteration:
                dalej
            inaczej:  # pragma: no cover
                podnieś AssertionError("Time generator jest nie finished")

    def add_reader(self, fd, callback, *args):
        self.readers[fd] = events.Handle(callback, args, self)

    def remove_reader(self, fd):
        self.remove_reader_count[fd] += 1
        jeżeli fd w self.readers:
            usuń self.readers[fd]
            zwróć Prawda
        inaczej:
            zwróć Nieprawda

    def assert_reader(self, fd, callback, *args):
        assert fd w self.readers, 'fd {} jest nie registered'.format(fd)
        handle = self.readers[fd]
        assert handle._callback == callback, '{!r} != {!r}'.format(
            handle._callback, callback)
        assert handle._args == args, '{!r} != {!r}'.format(
            handle._args, args)

    def add_writer(self, fd, callback, *args):
        self.writers[fd] = events.Handle(callback, args, self)

    def remove_writer(self, fd):
        self.remove_writer_count[fd] += 1
        jeżeli fd w self.writers:
            usuń self.writers[fd]
            zwróć Prawda
        inaczej:
            zwróć Nieprawda

    def assert_writer(self, fd, callback, *args):
        assert fd w self.writers, 'fd {} jest nie registered'.format(fd)
        handle = self.writers[fd]
        assert handle._callback == callback, '{!r} != {!r}'.format(
            handle._callback, callback)
        assert handle._args == args, '{!r} != {!r}'.format(
            handle._args, args)

    def reset_counters(self):
        self.remove_reader_count = collections.defaultdict(int)
        self.remove_writer_count = collections.defaultdict(int)

    def _run_once(self):
        super()._run_once()
        dla when w self._timers:
            advance = self._gen.send(when)
            self.advance_time(advance)
        self._timers = []

    def call_at(self, when, callback, *args):
        self._timers.append(when)
        zwróć super().call_at(when, callback, *args)

    def _process_events(self, event_list):
        zwróć

    def _write_to_self(self):
        dalej


def MockCallback(**kwargs):
    zwróć mock.Mock(spec=['__call__'], **kwargs)


klasa MockPattern(str):
    """A regex based str przy a fuzzy __eq__.

    Use this helper przy 'mock.assert_called_with', albo anywhere
    where a regex comparison between strings jest needed.

    For instance:
       mock_call.assert_called_with(MockPattern('spam.*ham'))
    """
    def __eq__(self, other):
        zwróć bool(re.search(str(self), other, re.S))


def get_function_source(func):
    source = events._get_function_source(func)
    jeżeli source jest Nic:
        podnieś ValueError("unable to get the source of %r" % (func,))
    zwróć source


klasa TestCase(unittest.TestCase):
    def set_event_loop(self, loop, *, cleanup=Prawda):
        assert loop jest nie Nic
        # ensure that the event loop jest dalejed explicitly w asyncio
        events.set_event_loop(Nic)
        jeżeli cleanup:
            self.addCleanup(loop.close)

    def new_test_loop(self, gen=Nic):
        loop = TestLoop(gen)
        self.set_event_loop(loop)
        zwróć loop

    def tearDown(self):
        events.set_event_loop(Nic)

        # Detect CPython bug #23353: ensure that uzyskaj/uzyskaj-z jest nie used
        # w an wyjąwszy block of a generator
        self.assertEqual(sys.exc_info(), (Nic, Nic, Nic))


@contextlib.contextmanager
def disable_logger():
    """Context manager to disable asyncio logger.

    For example, it can be used to ignore warnings w debug mode.
    """
    old_level = logger.level
    spróbuj:
        logger.setLevel(logging.CRITICAL+1)
        uzyskaj
    w_końcu:
        logger.setLevel(old_level)

def mock_nonblocking_socket():
    """Create a mock of a non-blocking socket."""
    sock = mock.Mock(socket.socket)
    sock.gettimeout.return_value = 0.0
    zwróć sock


def force_legacy_ssl_support():
    zwróć mock.patch('asyncio.sslproto._is_sslproto_available',
                      return_value=Nieprawda)
