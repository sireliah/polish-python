"""HTTP server classes.

Note: BaseHTTPRequestHandler doesn't implement any HTTP request; see
SimpleHTTPRequestHandler dla simple implementations of GET, HEAD oraz POST,
and CGIHTTPRequestHandler dla CGI scripts.

It does, however, optionally implement HTTP/1.1 persistent connections,
as of version 0.3.

Notes on CGIHTTPRequestHandler
------------------------------

This klasa implements GET oraz POST requests to cgi-bin scripts.

If the os.fork() function jest nie present (e.g. on Windows),
subprocess.Popen() jest used jako a fallback, przy slightly altered semantics.

In all cases, the implementation jest intentionally naive -- all
requests are executed synchronously.

SECURITY WARNING: DON'T USE THIS CODE UNLESS YOU ARE INSIDE A FIREWALL
-- it may execute arbitrary Python code albo external programs.

Note that status code 200 jest sent prior to execution of a CGI script, so
scripts cannot send other status codes such jako 302 (redirect).

XXX To do:

- log requests even later (to capture byte count)
- log user-agent header oraz other interesting goodies
- send error log to separate file
"""


# See also:
#
# HTTP Working Group                                        T. Berners-Lee
# INTERNET-DRAFT                                            R. T. Fielding
# <draft-ietf-http-v10-spec-00.txt>                     H. Frystyk Niinaczejn
# Expires September 8, 1995                                  March 8, 1995
#
# URL: http://www.ics.uci.edu/pub/ietf/http/draft-ietf-http-v10-spec-00.txt
#
# oraz
#
# Network Working Group                                      R. Fielding
# Request dla Comments: 2616                                       et al
# Obsoletes: 2068                                              June 1999
# Category: Standards Track
#
# URL: http://www.faqs.org/rfcs/rfc2616.html

# Log files
# ---------
#
# Here's a quote z the NCSA httpd docs about log file format.
#
# | The logfile format jest jako follows. Each line consists of:
# |
# | host rfc931 authuser [DD/Mon/YYYY:hh:mm:ss] "request" ddd bbbb
# |
# |        host: Either the DNS name albo the IP number of the remote client
# |        rfc931: Any information returned by identd dla this person,
# |                - otherwise.
# |        authuser: If user sent a userid dla authentication, the user name,
# |                  - otherwise.
# |        DD: Day
# |        Mon: Month (calendar name)
# |        YYYY: Year
# |        hh: hour (24-hour format, the machine's timezone)
# |        mm: minutes
# |        ss: seconds
# |        request: The first line of the HTTP request jako sent by the client.
# |        ddd: the status code returned by the server, - jeżeli nie available.
# |        bbbb: the total number of bytes sent,
# |              *not including the HTTP/1.0 header*, - jeżeli nie available
# |
# | You can determine the name of the file accessed through request.
#
# (Actually, the latter jest only true jeżeli you know the server configuration
# at the time the request was made!)

__version__ = "0.6"

__all__ = [
    "HTTPServer", "BaseHTTPRequestHandler",
    "SimpleHTTPRequestHandler", "CGIHTTPRequestHandler",
]

zaimportuj html
zaimportuj http.client
zaimportuj io
zaimportuj mimetypes
zaimportuj os
zaimportuj posixpath
zaimportuj select
zaimportuj shutil
zaimportuj socket # For gethostbyaddr()
zaimportuj socketserver
zaimportuj sys
zaimportuj time
zaimportuj urllib.parse
zaimportuj copy
zaimportuj argparse

z http zaimportuj HTTPStatus


# Default error message template
DEFAULT_ERROR_MESSAGE = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: %(code)d</p>
        <p>Message: %(message)s.</p>
        <p>Error code explanation: %(code)s - %(explain)s.</p>
    </body>
</html>
"""

DEFAULT_ERROR_CONTENT_TYPE = "text/html;charset=utf-8"

def _quote_html(html):
    zwróć html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

klasa HTTPServer(socketserver.TCPServer):

    allow_reuse_address = 1    # Seems to make sense w testing environment

    def server_bind(self):
        """Override server_bind to store the server name."""
        socketserver.TCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port


klasa BaseHTTPRequestHandler(socketserver.StreamRequestHandler):

    """HTTP request handler base class.

    The following explanation of HTTP serves to guide you through the
    code jako well jako to expose any misunderstandings I may have about
    HTTP (so you don't need to read the code to figure out I'm wrong
    :-).

    HTTP (HyperText Transfer Protocol) jest an extensible protocol on
    top of a reliable stream transport (e.g. TCP/IP).  The protocol
    recognizes three parts to a request:

    1. One line identifying the request type oraz path
    2. An optional set of RFC-822-style headers
    3. An optional data part

    The headers oraz data are separated by a blank line.

    The first line of the request has the form

    <command> <path> <version>

    where <command> jest a (case-sensitive) keyword such jako GET albo POST,
    <path> jest a string containing path information dla the request,
    oraz <version> should be the string "HTTP/1.0" albo "HTTP/1.1".
    <path> jest encoded using the URL encoding scheme (using %xx to signify
    the ASCII character przy hex code xx).

    The specification specifies that lines are separated by CRLF but
    dla compatibility przy the widest range of clients recommends
    servers also handle LF.  Similarly, whitespace w the request line
    jest treated sensibly (allowing multiple spaces between components
    oraz allowing trailing whitespace).

    Similarly, dla output, lines ought to be separated by CRLF pairs
    but most clients grok LF characters just fine.

    If the first line of the request has the form

    <command> <path>

    (i.e. <version> jest left out) then this jest assumed to be an HTTP
    0.9 request; this form has no optional headers oraz data part oraz
    the reply consists of just the data.

    The reply form of the HTTP 1.x protocol again has three parts:

    1. One line giving the response code
    2. An optional set of RFC-822-style headers
    3. The data

    Again, the headers oraz data are separated by a blank line.

    The response code line has the form

    <version> <responsecode> <responsestring>

    where <version> jest the protocol version ("HTTP/1.0" albo "HTTP/1.1"),
    <responsecode> jest a 3-digit response code indicating success albo
    failure of the request, oraz <responsestring> jest an optional
    human-readable string explaining what the response code means.

    This server parses the request oraz the headers, oraz then calls a
    function specific to the request type (<command>).  Specifically,
    a request SPAM will be handled by a method do_SPAM().  If no
    such method exists the server sends an error response to the
    client.  If it exists, it jest called przy no arguments:

    do_SPAM()

    Note that the request name jest case sensitive (i.e. SPAM oraz spam
    are different requests).

    The various request details are stored w instance variables:

    - client_address jest the client IP address w the form (host,
    port);

    - command, path oraz version are the broken-down request line;

    - headers jest an instance of email.message.Message (or a derived
    class) containing the header information;

    - rfile jest a file object open dla reading positioned at the
    start of the optional input data part;

    - wfile jest a file object open dla writing.

    IT IS IMPORTANT TO ADHERE TO THE PROTOCOL FOR WRITING!

    The first thing to be written must be the response line.  Then
    follow 0 albo more header lines, then a blank line, oraz then the
    actual data (jeżeli any).  The meaning of the header lines depends on
    the command executed by the server; w most cases, when data jest
    returned, there should be at least one header line of the form

    Content-type: <type>/<subtype>

    where <type> oraz <subtype> should be registered MIME types,
    e.g. "text/html" albo "text/plain".

    """

    # The Python system version, truncated to its first component.
    sys_version = "Python/" + sys.version.split()[0]

    # The server software version.  You may want to override this.
    # The format jest multiple whitespace-separated strings,
    # where each string jest of the form name[/version].
    server_version = "BaseHTTP/" + __version__

    error_message_format = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE

    # The default request version.  This only affects responses up until
    # the point where the request line jest parsed, so it mainly decides what
    # the client gets back when sending a malformed request line.
    # Most web servers default to HTTP 0.9, i.e. don't send a status line.
    default_request_version = "HTTP/0.9"

    def parse_request(self):
        """Parse a request (internal).

        The request should be stored w self.raw_requestline; the results
        are w self.command, self.path, self.request_version oraz
        self.headers.

        Return Prawda dla success, Nieprawda dla failure; on failure, an
        error jest sent back.

        """
        self.command = Nic  # set w case of error on the first line
        self.request_version = version = self.default_request_version
        self.close_connection = Prawda
        requestline = str(self.raw_requestline, 'iso-8859-1')
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split()
        jeżeli len(words) == 3:
            command, path, version = words
            jeżeli version[:5] != 'HTTP/':
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad request version (%r)" % version)
                zwróć Nieprawda
            spróbuj:
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split(".")
                # RFC 2145 section 3.1 says there can be only one "." oraz
                #   - major oraz minor numbers MUST be treated as
                #      separate integers;
                #   - HTTP/2.4 jest a lower version than HTTP/2.13, which w
                #      turn jest lower than HTTP/12.3;
                #   - Leading zeros MUST be ignored by recipients.
                jeżeli len(version_number) != 2:
                    podnieś ValueError
                version_number = int(version_number[0]), int(version_number[1])
            wyjąwszy (ValueError, IndexError):
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad request version (%r)" % version)
                zwróć Nieprawda
            jeżeli version_number >= (1, 1) oraz self.protocol_version >= "HTTP/1.1":
                self.close_connection = Nieprawda
            jeżeli version_number >= (2, 0):
                self.send_error(
                    HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                    "Invalid HTTP Version (%s)" % base_version_number)
                zwróć Nieprawda
        albo_inaczej len(words) == 2:
            command, path = words
            self.close_connection = Prawda
            jeżeli command != 'GET':
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad HTTP/0.9 request type (%r)" % command)
                zwróć Nieprawda
        albo_inaczej nie words:
            zwróć Nieprawda
        inaczej:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                "Bad request syntax (%r)" % requestline)
            zwróć Nieprawda
        self.command, self.path, self.request_version = command, path, version

        # Examine the headers oraz look dla a Connection directive.
        spróbuj:
            self.headers = http.client.parse_headers(self.rfile,
                                                     _class=self.MessageClass)
        wyjąwszy http.client.LineTooLong:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                "Line too long")
            zwróć Nieprawda

        conntype = self.headers.get('Connection', "")
        jeżeli conntype.lower() == 'close':
            self.close_connection = Prawda
        albo_inaczej (conntype.lower() == 'keep-alive' oraz
              self.protocol_version >= "HTTP/1.1"):
            self.close_connection = Nieprawda
        # Examine the headers oraz look dla an Expect directive
        expect = self.headers.get('Expect', "")
        jeżeli (expect.lower() == "100-continue" oraz
                self.protocol_version >= "HTTP/1.1" oraz
                self.request_version >= "HTTP/1.1"):
            jeżeli nie self.handle_expect_100():
                zwróć Nieprawda
        zwróć Prawda

    def handle_expect_100(self):
        """Decide what to do przy an "Expect: 100-continue" header.

        If the client jest expecting a 100 Continue response, we must
        respond przy either a 100 Continue albo a final response before
        waiting dla the request body. The default jest to always respond
        przy a 100 Continue. You can behave differently (dla example,
        reject unauthorized requests) by overriding this method.

        This method should either zwróć Prawda (possibly after sending
        a 100 Continue response) albo send an error response oraz zwróć
        Nieprawda.

        """
        self.send_response_only(HTTPStatus.CONTINUE)
        self.end_headers()
        zwróć Prawda

    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string dla information on how to handle specific HTTP
        commands such jako GET oraz POST.

        """
        spróbuj:
            self.raw_requestline = self.rfile.readline(65537)
            jeżeli len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                zwróć
            jeżeli nie self.raw_requestline:
                self.close_connection = Prawda
                zwróć
            jeżeli nie self.parse_request():
                # An error code has been sent, just exit
                zwróć
            mname = 'do_' + self.command
            jeżeli nie hasattr(self, mname):
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    "Unsupported method (%r)" % self.command)
                zwróć
            method = getattr(self, mname)
            method()
            self.wfile.flush() #actually send the response jeżeli nie already done.
        wyjąwszy socket.timeout jako e:
            #a read albo a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = Prawda
            zwróć

    def handle(self):
        """Handle multiple requests jeżeli necessary."""
        self.close_connection = Prawda

        self.handle_one_request()
        dopóki nie self.close_connection:
            self.handle_one_request()

    def send_error(self, code, message=Nic, explain=Nic):
        """Send oraz log an error reply.

        Arguments are
        * code:    an HTTP error code
                   3 digits
        * message: a simple optional 1 line reason phrase.
                   *( HTAB / SP / VCHAR / %x80-FF )
                   defaults to short entry matching the response code
        * explain: a detailed message defaults to the long entry
                   matching the response code.

        This sends an error response (so it must be called before any
        output has been generated), logs the error, oraz finally sends
        a piece of HTML explaining the error to the user.

        """

        spróbuj:
            shortmsg, longmsg = self.responses[code]
        wyjąwszy KeyError:
            shortmsg, longmsg = '???', '???'
        jeżeli message jest Nic:
            message = shortmsg
        jeżeli explain jest Nic:
            explain = longmsg
        self.log_error("code %d, message %s", code, message)
        # using _quote_html to prevent Cross Site Scripting attacks (see bug #1100201)
        content = (self.error_message_format %
                   {'code': code, 'message': _quote_html(message), 'explain': _quote_html(explain)})
        body = content.encode('UTF-8', 'replace')
        self.send_response(code, message)
        self.send_header("Content-Type", self.error_content_type)
        self.send_header('Connection', 'close')
        self.send_header('Content-Length', int(len(body)))
        self.end_headers()

        jeżeli (self.command != 'HEAD' oraz
                code >= 200 oraz
                code nie w (
                    HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED)):
            self.wfile.write(body)

    def send_response(self, code, message=Nic):
        """Add the response header to the headers buffer oraz log the
        response code.

        Also send two standard headers przy the server software
        version oraz the current date.

        """
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())

    def send_response_only(self, code, message=Nic):
        """Send the response header only."""
        jeżeli message jest Nic:
            jeżeli code w self.responses:
                message = self.responses[code][0]
            inaczej:
                message = ''
        jeżeli self.request_version != 'HTTP/0.9':
            jeżeli nie hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(("%s %d %s\r\n" %
                    (self.protocol_version, code, message)).encode(
                        'latin-1', 'strict'))

    def send_header(self, keyword, value):
        """Send a MIME header to the headers buffer."""
        jeżeli self.request_version != 'HTTP/0.9':
            jeżeli nie hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(
                ("%s: %s\r\n" % (keyword, value)).encode('latin-1', 'strict'))

        jeżeli keyword.lower() == 'connection':
            jeżeli value.lower() == 'close':
                self.close_connection = Prawda
            albo_inaczej value.lower() == 'keep-alive':
                self.close_connection = Nieprawda

    def end_headers(self):
        """Send the blank line ending the MIME headers."""
        jeżeli self.request_version != 'HTTP/0.9':
            self._headers_buffer.append(b"\r\n")
            self.flush_headers()

    def flush_headers(self):
        jeżeli hasattr(self, '_headers_buffer'):
            self.wfile.write(b"".join(self._headers_buffer))
            self._headers_buffer = []

    def log_request(self, code='-', size='-'):
        """Log an accepted request.

        This jest called by send_response().

        """
        jeżeli isinstance(code, HTTPStatus):
            code = code.value
        self.log_message('"%s" %s %s',
                         self.requestline, str(code), str(size))

    def log_error(self, format, *args):
        """Log an error.

        This jest called when a request cannot be fulfilled.  By
        default it dalejes the message on to log_message().

        Arguments are the same jako dla log_message().

        XXX This should go to the separate error log.

        """

        self.log_message(format, *args)

    def log_message(self, format, *args):
        """Log an arbitrary message.

        This jest used by all other logging functions.  Override
        it jeżeli you have specific logging wishes.

        The first argument, FORMAT, jest a format string dla the
        message to be logged.  If the format string contains
        any % escapes requiring parameters, they should be
        specified jako subsequent arguments (it's just like
        printf!).

        The client ip oraz current date/time are prefixed to
        every message.

        """

        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

    def version_string(self):
        """Return the server software version string."""
        zwróć self.server_version + ' ' + self.sys_version

    def date_time_string(self, timestamp=Nic):
        """Return the current date oraz time formatted dla a message header."""
        jeżeli timestamp jest Nic:
            timestamp = time.time()
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
        s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
                self.weekdayname[wd],
                day, self.monthname[month], year,
                hh, mm, ss)
        zwróć s

    def log_date_time_string(self):
        """Return the current time formatted dla logging."""
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (
                day, self.monthname[month], year, hh, mm, ss)
        zwróć s

    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [Nic,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def address_string(self):
        """Return the client address."""

        zwróć self.client_address[0]

    # Essentially static klasa variables

    # The version of the HTTP protocol we support.
    # Set this to HTTP/1.1 to enable automatic keepalive
    protocol_version = "HTTP/1.0"

    # MessageClass used to parse headers
    MessageClass = http.client.HTTPMessage

    # hack to maintain backwards compatibility
    responses = {
        v: (v.phrase, v.description)
        dla v w HTTPStatus.__members__.values()
    }


klasa SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    """Simple HTTP request handler przy GET oraz HEAD commands.

    This serves files z the current directory oraz any of its
    subdirectories.  The MIME type dla files jest determined by
    calling the .guess_type() method.

    The GET oraz HEAD requests are identical wyjąwszy that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "SimpleHTTP/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        jeżeli f:
            spróbuj:
                self.copyfile(f, self.wfile)
            w_końcu:
                f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        jeżeli f:
            f.close()

    def send_head(self):
        """Common code dla GET oraz HEAD commands.

        This sends the response code oraz MIME headers.

        Return value jest either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        oraz must be closed by the caller under all circumstances), albo
        Nic, w which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = Nic
        jeżeli os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            jeżeli nie parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                zwróć Nic
            dla index w "index.html", "index.htm":
                index = os.path.join(path, index)
                jeżeli os.path.exists(index):
                    path = index
                    przerwij
            inaczej:
                zwróć self.list_directory(path)
        ctype = self.guess_type(path)
        spróbuj:
            f = open(path, 'rb')
        wyjąwszy OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File nie found")
            zwróć Nic
        spróbuj:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            zwróć f
        wyjąwszy:
            f.close()
            podnieś

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value jest either a file object, albo Nic (indicating an
        error).  In either case, the headers are sent, making the
        interface the same jako dla send_head().

        """
        spróbuj:
            list = os.listdir(path)
        wyjąwszy OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No permission to list directory")
            zwróć Nic
        list.sort(key=lambda a: a.lower())
        r = []
        spróbuj:
            displaypath = urllib.parse.unquote(self.path,
                                               errors='surrogatepass')
        wyjąwszy UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing dla %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('<hr>\n<ul>')
        dla name w list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / dla directories albo @ dla symbolic links
            jeżeli os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            jeżeli os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays przy @ oraz links przy /
            r.append('<li><a href="%s">%s</a></li>'
                    % (urllib.parse.quote(linkname,
                                          errors='surrogatepass'),
                       html.escape(displayname)))
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        zwróć f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive albo directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        spróbuj:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        wyjąwszy UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(Nic, words)
        path = os.getcwd()
        dla word w words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            jeżeli word w (os.curdir, os.pardir): kontynuuj
            path = os.path.join(path, word)
        jeżeli trailing_slash:
            path += '/'
        zwróć path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument jest a file object open dla reading
        (or anything przy a read() method) oraz the DESTINATION
        argument jest a file object open dla writing (or
        anything przy a write() method).

        The only reason dla overriding this would be to change
        the block size albo perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data jako well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument jest a PATH (a filename).

        Return value jest a string of the form type/subtype,
        usable dla a MIME Content-type header.

        The default implementation looks the file's extension
        up w the table self.extensions_map, using application/octet-stream
        jako a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        jeżeli ext w self.extensions_map:
            zwróć self.extensions_map[ext]
        ext = ext.lower()
        jeżeli ext w self.extensions_map:
            zwróć self.extensions_map[ext]
        inaczej:
            zwróć self.extensions_map['']

    jeżeli nie mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


# Utilities dla CGIHTTPRequestHandler

def _url_collapse_path(path):
    """
    Given a URL path, remove extra '/'s oraz '.' path elements oraz collapse
    any '..' references oraz returns a colllapsed path.

    Implements something akin to RFC-2396 5.2 step 6 to parse relative paths.
    The utility of this function jest limited to is_cgi method oraz helps
    preventing some security attacks.

    Returns: A tuple of (head, tail) where tail jest everything after the final /
    oraz head jest everything before it.  Head will always start przy a '/' and,
    jeżeli it contains anything inaczej, never have a trailing '/'.

    Raises: IndexError jeżeli too many '..' occur within the path.

    """
    # Similar to os.path.split(os.path.normpath(path)) but specific to URL
    # path semantics rather than local operating system semantics.
    path_parts = path.split('/')
    head_parts = []
    dla part w path_parts[:-1]:
        jeżeli part == '..':
            head_parts.pop() # IndexError jeżeli more '..' than prior parts
        albo_inaczej part oraz part != '.':
            head_parts.append( part )
    jeżeli path_parts:
        tail_part = path_parts.pop()
        jeżeli tail_part:
            jeżeli tail_part == '..':
                head_parts.pop()
                tail_part = ''
            albo_inaczej tail_part == '.':
                tail_part = ''
    inaczej:
        tail_part = ''

    splitpath = ('/' + '/'.join(head_parts), tail_part)
    collapsed_path = "/".join(splitpath)

    zwróć collapsed_path



nobody = Nic

def nobody_uid():
    """Internal routine to get nobody's uid"""
    global nobody
    jeżeli nobody:
        zwróć nobody
    spróbuj:
        zaimportuj pwd
    wyjąwszy ImportError:
        zwróć -1
    spróbuj:
        nobody = pwd.getpwnam('nobody')[2]
    wyjąwszy KeyError:
        nobody = 1 + max(x[2] dla x w pwd.getpwall())
    zwróć nobody


def executable(path):
    """Test dla executable file."""
    zwróć os.access(path, os.X_OK)


klasa CGIHTTPRequestHandler(SimpleHTTPRequestHandler):

    """Complete HTTP server przy GET, HEAD oraz POST commands.

    GET oraz HEAD also support running CGI scripts.

    The POST command jest *only* implemented dla CGI scripts.

    """

    # Determine platform specifics
    have_fork = hasattr(os, 'fork')

    # Make rfile unbuffered -- we need to read one line oraz then dalej
    # the rest to a subprocess, so we can't use buffered input.
    rbufsize = 0

    def do_POST(self):
        """Serve a POST request.

        This jest only implemented dla CGI scripts.

        """

        jeżeli self.is_cgi():
            self.run_cgi()
        inaczej:
            self.send_error(
                HTTPStatus.NOT_IMPLEMENTED,
                "Can only POST to CGI scripts")

    def send_head(self):
        """Version of send_head that support CGI scripts"""
        jeżeli self.is_cgi():
            zwróć self.run_cgi()
        inaczej:
            zwróć SimpleHTTPRequestHandler.send_head(self)

    def is_cgi(self):
        """Test whether self.path corresponds to a CGI script.

        Returns Prawda oraz updates the cgi_info attribute to the tuple
        (dir, rest) jeżeli self.path requires running a CGI script.
        Returns Nieprawda otherwise.

        If any exception jest podnieśd, the caller should assume that
        self.path was rejected jako invalid oraz act accordingly.

        The default implementation tests whether the normalized url
        path begins przy one of the strings w self.cgi_directories
        (and the next character jest a '/' albo the end of the string).

        """
        collapsed_path = _url_collapse_path(urllib.parse.unquote(self.path))
        dir_sep = collapsed_path.find('/', 1)
        head, tail = collapsed_path[:dir_sep], collapsed_path[dir_sep+1:]
        jeżeli head w self.cgi_directories:
            self.cgi_info = head, tail
            zwróć Prawda
        zwróć Nieprawda


    cgi_directories = ['/cgi-bin', '/htbin']

    def is_executable(self, path):
        """Test whether argument path jest an executable file."""
        zwróć executable(path)

    def is_python(self, path):
        """Test whether argument path jest a Python script."""
        head, tail = os.path.splitext(path)
        zwróć tail.lower() w (".py", ".pyw")

    def run_cgi(self):
        """Execute a CGI script."""
        dir, rest = self.cgi_info
        path = dir + '/' + rest
        i = path.find('/', len(dir)+1)
        dopóki i >= 0:
            nextdir = path[:i]
            nextrest = path[i+1:]

            scriptdir = self.translate_path(nextdir)
            jeżeli os.path.isdir(scriptdir):
                dir, rest = nextdir, nextrest
                i = path.find('/', len(dir)+1)
            inaczej:
                przerwij

        # find an explicit query string, jeżeli present.
        i = rest.rfind('?')
        jeżeli i >= 0:
            rest, query = rest[:i], rest[i+1:]
        inaczej:
            query = ''

        # dissect the part after the directory name into a script name &
        # a possible additional path, to be stored w PATH_INFO.
        i = rest.find('/')
        jeżeli i >= 0:
            script, rest = rest[:i], rest[i:]
        inaczej:
            script, rest = rest, ''

        scriptname = dir + '/' + script
        scriptfile = self.translate_path(scriptname)
        jeżeli nie os.path.exists(scriptfile):
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No such CGI script (%r)" % scriptname)
            zwróć
        jeżeli nie os.path.isfile(scriptfile):
            self.send_error(
                HTTPStatus.FORBIDDEN,
                "CGI script jest nie a plain file (%r)" % scriptname)
            zwróć
        ispy = self.is_python(scriptname)
        jeżeli self.have_fork albo nie ispy:
            jeżeli nie self.is_executable(scriptfile):
                self.send_error(
                    HTTPStatus.FORBIDDEN,
                    "CGI script jest nie executable (%r)" % scriptname)
                zwróć

        # Reference: http://hoohoo.ncsa.uiuc.edu/cgi/env.html
        # XXX Much of the following could be prepared ahead of time!
        env = copy.deepcopy(os.environ)
        env['SERVER_SOFTWARE'] = self.version_string()
        env['SERVER_NAME'] = self.server.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PROTOCOL'] = self.protocol_version
        env['SERVER_PORT'] = str(self.server.server_port)
        env['REQUEST_METHOD'] = self.command
        uqrest = urllib.parse.unquote(rest)
        env['PATH_INFO'] = uqrest
        env['PATH_TRANSLATED'] = self.translate_path(uqrest)
        env['SCRIPT_NAME'] = scriptname
        jeżeli query:
            env['QUERY_STRING'] = query
        env['REMOTE_ADDR'] = self.client_address[0]
        authorization = self.headers.get("authorization")
        jeżeli authorization:
            authorization = authorization.split()
            jeżeli len(authorization) == 2:
                zaimportuj base64, binascii
                env['AUTH_TYPE'] = authorization[0]
                jeżeli authorization[0].lower() == "basic":
                    spróbuj:
                        authorization = authorization[1].encode('ascii')
                        authorization = base64.decodebytes(authorization).\
                                        decode('ascii')
                    wyjąwszy (binascii.Error, UnicodeError):
                        dalej
                    inaczej:
                        authorization = authorization.split(':')
                        jeżeli len(authorization) == 2:
                            env['REMOTE_USER'] = authorization[0]
        # XXX REMOTE_IDENT
        jeżeli self.headers.get('content-type') jest Nic:
            env['CONTENT_TYPE'] = self.headers.get_content_type()
        inaczej:
            env['CONTENT_TYPE'] = self.headers['content-type']
        length = self.headers.get('content-length')
        jeżeli length:
            env['CONTENT_LENGTH'] = length
        referer = self.headers.get('referer')
        jeżeli referer:
            env['HTTP_REFERER'] = referer
        accept = []
        dla line w self.headers.getallmatchingheaders('accept'):
            jeżeli line[:1] w "\t\n\r ":
                accept.append(line.strip())
            inaczej:
                accept = accept + line[7:].split(',')
        env['HTTP_ACCEPT'] = ','.join(accept)
        ua = self.headers.get('user-agent')
        jeżeli ua:
            env['HTTP_USER_AGENT'] = ua
        co = filter(Nic, self.headers.get_all('cookie', []))
        cookie_str = ', '.join(co)
        jeżeli cookie_str:
            env['HTTP_COOKIE'] = cookie_str
        # XXX Other HTTP_* headers
        # Since we're setting the env w the parent, provide empty
        # values to override previously set values
        dla k w ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH',
                  'HTTP_USER_AGENT', 'HTTP_COOKIE', 'HTTP_REFERER'):
            env.setdefault(k, "")

        self.send_response(HTTPStatus.OK, "Script output follows")
        self.flush_headers()

        decoded_query = query.replace('+', ' ')

        jeżeli self.have_fork:
            # Unix -- fork jako we should
            args = [script]
            jeżeli '=' nie w decoded_query:
                args.append(decoded_query)
            nobody = nobody_uid()
            self.wfile.flush() # Always flush before forking
            pid = os.fork()
            jeżeli pid != 0:
                # Parent
                pid, sts = os.waitpid(pid, 0)
                # throw away additional data [see bug #427345]
                dopóki select.select([self.rfile], [], [], 0)[0]:
                    jeżeli nie self.rfile.read(1):
                        przerwij
                jeżeli sts:
                    self.log_error("CGI script exit status %#x", sts)
                zwróć
            # Child
            spróbuj:
                spróbuj:
                    os.setuid(nobody)
                wyjąwszy OSError:
                    dalej
                os.dup2(self.rfile.fileno(), 0)
                os.dup2(self.wfile.fileno(), 1)
                os.execve(scriptfile, args, env)
            wyjąwszy:
                self.server.handle_error(self.request, self.client_address)
                os._exit(127)

        inaczej:
            # Non-Unix -- use subprocess
            zaimportuj subprocess
            cmdline = [scriptfile]
            jeżeli self.is_python(scriptfile):
                interp = sys.executable
                jeżeli interp.lower().endswith("w.exe"):
                    # On Windows, use python.exe, nie pythonw.exe
                    interp = interp[:-5] + interp[-4:]
                cmdline = [interp, '-u'] + cmdline
            jeżeli '=' nie w query:
                cmdline.append(query)
            self.log_message("command: %s", subprocess.list2cmdline(cmdline))
            spróbuj:
                nbytes = int(length)
            wyjąwszy (TypeError, ValueError):
                nbytes = 0
            p = subprocess.Popen(cmdline,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env = env
                                 )
            jeżeli self.command.lower() == "post" oraz nbytes > 0:
                data = self.rfile.read(nbytes)
            inaczej:
                data = Nic
            # throw away additional data [see bug #427345]
            dopóki select.select([self.rfile._sock], [], [], 0)[0]:
                jeżeli nie self.rfile._sock.recv(1):
                    przerwij
            stdout, stderr = p.communicate(data)
            self.wfile.write(stdout)
            jeżeli stderr:
                self.log_error('%s', stderr)
            p.stderr.close()
            p.stdout.close()
            status = p.returncode
            jeżeli status:
                self.log_error("CGI script exit status %#x", status)
            inaczej:
                self.log_message("CGI script exited OK")


def test(HandlerClass=BaseHTTPRequestHandler,
         ServerClass=HTTPServer, protocol="HTTP/1.0", port=8000, bind=""):
    """Test the HTTP request handler class.

    This runs an HTTP server on port 8000 (or the first command line
    argument).

    """
    server_address = (bind, port)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")
    spróbuj:
        httpd.serve_forever()
    wyjąwszy KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        httpd.server_close()
        sys.exit(0)

jeżeli __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cgi', action='store_true',
                       help='Run jako CGI Server')
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    jeżeli args.cgi:
        handler_class = CGIHTTPRequestHandler
    inaczej:
        handler_class = SimpleHTTPRequestHandler
    test(HandlerClass=handler_class, port=args.port, bind=args.bind)
