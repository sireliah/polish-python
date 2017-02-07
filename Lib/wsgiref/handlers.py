"""Base classes dla server/gateway implementations"""

z .util zaimportuj FileWrapper, guess_scheme, is_hop_by_hop
z .headers zaimportuj Headers

zaimportuj sys, os, time

__all__ = [
    'BaseHandler', 'SimpleHandler', 'BaseCGIHandler', 'CGIHandler',
    'IISCGIHandler', 'read_environ'
]

# Weekday oraz month names dla HTTP date/time formatting; always English!
_weekdayname = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_monthname = [Nic, # Dummy so we can use 1-based month numbers
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def format_date_time(timestamp):
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    zwróć "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        _weekdayname[wd], day, _monthname[month], year, hh, mm, ss
    )

_is_request = {
    'SCRIPT_NAME', 'PATH_INFO', 'QUERY_STRING', 'REQUEST_METHOD', 'AUTH_TYPE',
    'CONTENT_TYPE', 'CONTENT_LENGTH', 'HTTPS', 'REMOTE_USER', 'REMOTE_IDENT',
}.__contains__

def _needs_transcode(k):
    zwróć _is_request(k) albo k.startswith('HTTP_') albo k.startswith('SSL_') \
        albo (k.startswith('REDIRECT_') oraz _needs_transcode(k[9:]))

def read_environ():
    """Read environment, fixing HTTP variables"""
    enc = sys.getfilesystemencoding()
    esc = 'surrogateescape'
    spróbuj:
        ''.encode('utf-8', esc)
    wyjąwszy LookupError:
        esc = 'replace'
    environ = {}

    # Take the basic environment z native-unicode os.environ. Attempt to
    # fix up the variables that come z the HTTP request to compensate for
    # the bytes->unicode decoding step that will already have taken place.
    dla k, v w os.environ.items():
        jeżeli _needs_transcode(k):

            # On win32, the os.environ jest natively Unicode. Different servers
            # decode the request bytes using different encodings.
            jeżeli sys.platform == 'win32':
                software = os.environ.get('SERVER_SOFTWARE', '').lower()

                # On IIS, the HTTP request will be decoded jako UTF-8 jako long
                # jako the input jest a valid UTF-8 sequence. Otherwise it jest
                # decoded using the system code page (mbcs), przy no way to
                # detect this has happened. Because UTF-8 jest the more likely
                # encoding, oraz mbcs jest inherently unreliable (an mbcs string
                # that happens to be valid UTF-8 will nie be decoded jako mbcs)
                # always recreate the original bytes jako UTF-8.
                jeżeli software.startswith('microsoft-iis/'):
                    v = v.encode('utf-8').decode('iso-8859-1')

                # Apache mod_cgi writes bytes-as-unicode (as jeżeli ISO-8859-1) direct
                # to the Unicode environ. No modification needed.
                albo_inaczej software.startswith('apache/'):
                    dalej

                # Python 3's http.server.CGIHTTPRequestHandler decodes
                # using the urllib.unquote default of UTF-8, amongst other
                # issues.
                albo_inaczej (
                    software.startswith('simplehttp/')
                    oraz 'python/3' w software
                ):
                    v = v.encode('utf-8').decode('iso-8859-1')

                # For other servers, guess that they have written bytes to
                # the environ using stdio byte-oriented interfaces, ending up
                # przy the system code page.
                inaczej:
                    v = v.encode(enc, 'replace').decode('iso-8859-1')

            # Recover bytes z unicode environ, using surrogate escapes
            # where available (Python 3.1+).
            inaczej:
                v = v.encode(enc, esc).decode('iso-8859-1')

        environ[k] = v
    zwróć environ


klasa BaseHandler:
    """Manage the invocation of a WSGI application"""

    # Configuration parameters; can override per-subclass albo per-instance
    wsgi_version = (1,0)
    wsgi_multithread = Prawda
    wsgi_multiprocess = Prawda
    wsgi_run_once = Nieprawda

    origin_server = Prawda    # We are transmitting direct to client
    http_version  = "1.0"   # Version that should be used dla response
    server_software = Nic  # String name of server software, jeżeli any

    # os_environ jest used to supply configuration z the OS environment:
    # by default it's a copy of 'os.environ' jako of zaimportuj time, but you can
    # override this w e.g. your __init__ method.
    os_environ= read_environ()

    # Collaborator classes
    wsgi_file_wrapper = FileWrapper     # set to Nic to disable
    headers_class = Headers             # must be a Headers-like class

    # Error handling (also per-subclass albo per-instance)
    traceback_limit = Nic  # Print entire traceback to self.get_stderr()
    error_status = "500 Internal Server Error"
    error_headers = [('Content-Type','text/plain')]
    error_body = b"A server error occurred.  Please contact the administrator."

    # State variables (don't mess przy these)
    status = result = Nic
    headers_sent = Nieprawda
    headers = Nic
    bytes_sent = 0

    def run(self, application):
        """Invoke the application"""
        # Note to self: don't move the close()!  Asynchronous servers shouldn't
        # call close() z finish_response(), so jeżeli you close() anywhere but
        # the double-error branch here, you'll przerwij asynchronous servers by
        # prematurely closing.  Async servers must zwróć z 'run()' without
        # closing jeżeli there might still be output to iterate over.
        spróbuj:
            self.setup_environ()
            self.result = application(self.environ, self.start_response)
            self.finish_response()
        wyjąwszy:
            spróbuj:
                self.handle_error()
            wyjąwszy:
                # If we get an error handling an error, just give up already!
                self.close()
                podnieś   # ...and let the actual server figure it out.


    def setup_environ(self):
        """Set up the environment dla one request"""

        env = self.environ = self.os_environ.copy()
        self.add_cgi_vars()

        env['wsgi.input']        = self.get_stdin()
        env['wsgi.errors']       = self.get_stderr()
        env['wsgi.version']      = self.wsgi_version
        env['wsgi.run_once']     = self.wsgi_run_once
        env['wsgi.url_scheme']   = self.get_scheme()
        env['wsgi.multithread']  = self.wsgi_multithread
        env['wsgi.multiprocess'] = self.wsgi_multiprocess

        jeżeli self.wsgi_file_wrapper jest nie Nic:
            env['wsgi.file_wrapper'] = self.wsgi_file_wrapper

        jeżeli self.origin_server oraz self.server_software:
            env.setdefault('SERVER_SOFTWARE',self.server_software)


    def finish_response(self):
        """Send any iterable data, then close self oraz the iterable

        Subclasses intended dla use w asynchronous servers will
        want to redefine this method, such that it sets up callbacks
        w the event loop to iterate over the data, oraz to call
        'self.close()' once the response jest finished.
        """
        spróbuj:
            jeżeli nie self.result_is_file() albo nie self.sendfile():
                dla data w self.result:
                    self.write(data)
                self.finish_content()
        w_końcu:
            self.close()


    def get_scheme(self):
        """Return the URL scheme being used"""
        zwróć guess_scheme(self.environ)


    def set_content_length(self):
        """Compute Content-Length albo switch to chunked encoding jeżeli possible"""
        spróbuj:
            blocks = len(self.result)
        wyjąwszy (TypeError,AttributeError,NotImplementedError):
            dalej
        inaczej:
            jeżeli blocks==1:
                self.headers['Content-Length'] = str(self.bytes_sent)
                zwróć
        # XXX Try dla chunked encoding jeżeli origin server oraz client jest 1.1


    def cleanup_headers(self):
        """Make any necessary header changes albo defaults

        Subclasses can extend this to add other defaults.
        """
        jeżeli 'Content-Length' nie w self.headers:
            self.set_content_length()

    def start_response(self, status, headers,exc_info=Nic):
        """'start_response()' callable jako specified by PEP 3333"""

        jeżeli exc_info:
            spróbuj:
                jeżeli self.headers_sent:
                    # Re-raise original exception jeżeli headers sent
                    podnieś exc_info[0](exc_info[1]).with_traceback(exc_info[2])
            w_końcu:
                exc_info = Nic        # avoid dangling circular ref
        albo_inaczej self.headers jest nie Nic:
            podnieś AssertionError("Headers already set!")

        self.status = status
        self.headers = self.headers_class(headers)
        status = self._convert_string_type(status, "Status")
        assert len(status)>=4,"Status must be at least 4 characters"
        assert int(status[:3]),"Status message must begin w/3-digit code"
        assert status[3]==" ", "Status message must have a space after code"

        jeżeli __debug__:
            dla name, val w headers:
                name = self._convert_string_type(name, "Header name")
                val = self._convert_string_type(val, "Header value")
                assert nie is_hop_by_hop(name),"Hop-by-hop headers nie allowed"

        zwróć self.write

    def _convert_string_type(self, value, title):
        """Convert/check value type."""
        jeżeli type(value) jest str:
            zwróć value
        podnieś AssertionError(
            "{0} must be of type str (got {1})".format(title, repr(value))
        )

    def send_preamble(self):
        """Transmit version/status/date/server, via self._write()"""
        jeżeli self.origin_server:
            jeżeli self.client_is_modern():
                self._write(('HTTP/%s %s\r\n' % (self.http_version,self.status)).encode('iso-8859-1'))
                jeżeli 'Date' nie w self.headers:
                    self._write(
                        ('Date: %s\r\n' % format_date_time(time.time())).encode('iso-8859-1')
                    )
                jeżeli self.server_software oraz 'Server' nie w self.headers:
                    self._write(('Server: %s\r\n' % self.server_software).encode('iso-8859-1'))
        inaczej:
            self._write(('Status: %s\r\n' % self.status).encode('iso-8859-1'))

    def write(self, data):
        """'write()' callable jako specified by PEP 3333"""

        assert type(data) jest bytes, \
            "write() argument must be a bytes instance"

        jeżeli nie self.status:
            podnieś AssertionError("write() before start_response()")

        albo_inaczej nie self.headers_sent:
            # Before the first output, send the stored headers
            self.bytes_sent = len(data)    # make sure we know content-length
            self.send_headers()
        inaczej:
            self.bytes_sent += len(data)

        # XXX check Content-Length oraz truncate jeżeli too many bytes written?
        self._write(data)
        self._flush()


    def sendfile(self):
        """Platform-specific file transmission

        Override this method w subclasses to support platform-specific
        file transmission.  It jest only called jeżeli the application's
        zwróć iterable ('self.result') jest an instance of
        'self.wsgi_file_wrapper'.

        This method should zwróć a true value jeżeli it was able to actually
        transmit the wrapped file-like object using a platform-specific
        approach.  It should zwróć a false value jeżeli normal iteration
        should be used instead.  An exception can be podnieśd to indicate
        that transmission was attempted, but failed.

        NOTE: this method should call 'self.send_headers()' if
        'self.headers_sent' jest false oraz it jest going to attempt direct
        transmission of the file.
        """
        zwróć Nieprawda   # No platform-specific transmission by default


    def finish_content(self):
        """Ensure headers oraz content have both been sent"""
        jeżeli nie self.headers_sent:
            # Only zero Content-Length jeżeli nie set by the application (so
            # that HEAD requests can be satisfied properly, see #3839)
            self.headers.setdefault('Content-Length', "0")
            self.send_headers()
        inaczej:
            dalej # XXX check jeżeli content-length was too short?

    def close(self):
        """Close the iterable (jeżeli needed) oraz reset all instance vars

        Subclasses may want to also drop the client connection.
        """
        spróbuj:
            jeżeli hasattr(self.result,'close'):
                self.result.close()
        w_końcu:
            self.result = self.headers = self.status = self.environ = Nic
            self.bytes_sent = 0; self.headers_sent = Nieprawda


    def send_headers(self):
        """Transmit headers to the client, via self._write()"""
        self.cleanup_headers()
        self.headers_sent = Prawda
        jeżeli nie self.origin_server albo self.client_is_modern():
            self.send_preamble()
            self._write(bytes(self.headers))


    def result_is_file(self):
        """Prawda jeżeli 'self.result' jest an instance of 'self.wsgi_file_wrapper'"""
        wrapper = self.wsgi_file_wrapper
        zwróć wrapper jest nie Nic oraz isinstance(self.result,wrapper)


    def client_is_modern(self):
        """Prawda jeżeli client can accept status oraz headers"""
        zwróć self.environ['SERVER_PROTOCOL'].upper() != 'HTTP/0.9'


    def log_exception(self,exc_info):
        """Log the 'exc_info' tuple w the server log

        Subclasses may override to retarget the output albo change its format.
        """
        spróbuj:
            z traceback zaimportuj print_exception
            stderr = self.get_stderr()
            print_exception(
                exc_info[0], exc_info[1], exc_info[2],
                self.traceback_limit, stderr
            )
            stderr.flush()
        w_końcu:
            exc_info = Nic

    def handle_error(self):
        """Log current error, oraz send error output to client jeżeli possible"""
        self.log_exception(sys.exc_info())
        jeżeli nie self.headers_sent:
            self.result = self.error_output(self.environ, self.start_response)
            self.finish_response()
        # XXX inaczej: attempt advanced recovery techniques dla HTML albo text?

    def error_output(self, environ, start_response):
        """WSGI mini-app to create error output

        By default, this just uses the 'error_status', 'error_headers',
        oraz 'error_body' attributes to generate an output page.  It can
        be overridden w a subclass to dynamically generate diagnostics,
        choose an appropriate message dla the user's preferred language, etc.

        Note, however, that it's nie recommended z a security perspective to
        spit out diagnostics to any old user; ideally, you should have to do
        something special to enable diagnostic output, which jest why we don't
        include any here!
        """
        start_response(self.error_status,self.error_headers[:],sys.exc_info())
        zwróć [self.error_body]


    # Pure abstract methods; *must* be overridden w subclasses

    def _write(self,data):
        """Override w subclass to buffer data dla send to client

        It's okay jeżeli this method actually transmits the data; BaseHandler
        just separates write oraz flush operations dla greater efficiency
        when the underlying system actually has such a distinction.
        """
        podnieś NotImplementedError

    def _flush(self):
        """Override w subclass to force sending of recent '_write()' calls

        It's okay jeżeli this method jest a no-op (i.e., jeżeli '_write()' actually
        sends the data.
        """
        podnieś NotImplementedError

    def get_stdin(self):
        """Override w subclass to zwróć suitable 'wsgi.input'"""
        podnieś NotImplementedError

    def get_stderr(self):
        """Override w subclass to zwróć suitable 'wsgi.errors'"""
        podnieś NotImplementedError

    def add_cgi_vars(self):
        """Override w subclass to insert CGI variables w 'self.environ'"""
        podnieś NotImplementedError


klasa SimpleHandler(BaseHandler):
    """Handler that's just initialized przy streams, environment, etc.

    This handler subclass jest intended dla synchronous HTTP/1.0 origin servers,
    oraz handles sending the entire response output, given the correct inputs.

    Usage::

        handler = SimpleHandler(
            inp,out,err,env, multithread=Nieprawda, multiprocess=Prawda
        )
        handler.run(app)"""

    def __init__(self,stdin,stdout,stderr,environ,
        multithread=Prawda, multiprocess=Nieprawda
    ):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.base_env = environ
        self.wsgi_multithread = multithread
        self.wsgi_multiprocess = multiprocess

    def get_stdin(self):
        zwróć self.stdin

    def get_stderr(self):
        zwróć self.stderr

    def add_cgi_vars(self):
        self.environ.update(self.base_env)

    def _write(self,data):
        self.stdout.write(data)

    def _flush(self):
        self.stdout.flush()
        self._flush = self.stdout.flush


klasa BaseCGIHandler(SimpleHandler):

    """CGI-like systems using input/output/error streams oraz environ mapping

    Usage::

        handler = BaseCGIHandler(inp,out,err,env)
        handler.run(app)

    This handler klasa jest useful dla gateway protocols like ReadyExec oraz
    FastCGI, that have usable input/output/error streams oraz an environment
    mapping.  It's also the base klasa dla CGIHandler, which just uses
    sys.stdin, os.environ, oraz so on.

    The constructor also takes keyword arguments 'multithread' oraz
    'multiprocess' (defaulting to 'Prawda' oraz 'Nieprawda' respectively) to control
    the configuration sent to the application.  It sets 'origin_server' to
    Nieprawda (to enable CGI-like output), oraz assumes that 'wsgi.run_once' jest
    Nieprawda.
    """

    origin_server = Nieprawda


klasa CGIHandler(BaseCGIHandler):

    """CGI-based invocation via sys.stdin/stdout/stderr oraz os.environ

    Usage::

        CGIHandler().run(app)

    The difference between this klasa oraz BaseCGIHandler jest that it always
    uses 'wsgi.run_once' of 'Prawda', 'wsgi.multithread' of 'Nieprawda', oraz
    'wsgi.multiprocess' of 'Prawda'.  It does nie take any initialization
    parameters, but always uses 'sys.stdin', 'os.environ', oraz friends.

    If you need to override any of these parameters, use BaseCGIHandler
    instead.
    """

    wsgi_run_once = Prawda
    # Do nie allow os.environ to leak between requests w Google App Engine
    # oraz other multi-run CGI use cases.  This jest nie easily testable.
    # See http://bugs.python.org/issue7250
    os_environ = {}

    def __init__(self):
        BaseCGIHandler.__init__(
            self, sys.stdin.buffer, sys.stdout.buffer, sys.stderr,
            read_environ(), multithread=Nieprawda, multiprocess=Prawda
        )


klasa IISCGIHandler(BaseCGIHandler):
    """CGI-based invocation przy workaround dla IIS path bug

    This handler should be used w preference to CGIHandler when deploying on
    Microsoft IIS without having set the config allowPathInfo option (IIS>=7)
    albo metabase allowPathInfoForScriptMappings (IIS<7).
    """
    wsgi_run_once = Prawda
    os_environ = {}

    # By default, IIS gives a PATH_INFO that duplicates the SCRIPT_NAME at
    # the front, causing problems dla WSGI applications that wish to implement
    # routing. This handler strips any such duplicated path.

    # IIS can be configured to dalej the correct PATH_INFO, but this causes
    # another bug where PATH_TRANSLATED jest wrong. Luckily this variable jest
    # rarely used oraz jest nie guaranteed by WSGI. On IIS<7, though, the
    # setting can only be made on a vhost level, affecting all other script
    # mappings, many of which przerwij when exposed to the PATH_TRANSLATED bug.
    # For this reason IIS<7 jest almost never deployed przy the fix. (Even IIS7
    # rarely uses it because there jest still no UI dla it.)

    # There jest no way dla CGI code to tell whether the option was set, so a
    # separate handler klasa jest provided.
    def __init__(self):
        environ= read_environ()
        path = environ.get('PATH_INFO', '')
        script = environ.get('SCRIPT_NAME', '')
        jeżeli (path+'/').startswith(script+'/'):
            environ['PATH_INFO'] = path[len(script):]
        BaseCGIHandler.__init__(
            self, sys.stdin.buffer, sys.stdout.buffer, sys.stderr,
            environ, multithread=Nieprawda, multiprocess=Prawda
        )
