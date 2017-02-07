"""HTTP/1.1 client library

<intro stuff goes here>
<other stuff, too>

HTTPConnection goes through a number of "states", which define when a client
may legally make another request albo fetch the response dla a particular
request. This diagram details these state transitions:

    (null)
      |
      | HTTPConnection()
      v
    Idle
      |
      | putrequest()
      v
    Request-started
      |
      | ( putheader() )*  endheaders()
      v
    Request-sent
      |\_____________________________
      |                              | getresponse() podnieśs
      | response = getresponse()     | ConnectionError
      v                              v
    Unread-response                Idle
    [Response-headers-read]
      |\____________________
      |                     |
      | response.read()     | putrequest()
      v                     v
    Idle                  Req-started-unread-response
                     ______/|
                   /        |
   response.read() |        | ( putheader() )*  endheaders()
                   v        v
       Request-started    Req-sent-unread-response
                            |
                            | response.read()
                            v
                          Request-sent

This diagram presents the following rules:
  -- a second request may nie be started until {response-headers-read}
  -- a response [object] cannot be retrieved until {request-sent}
  -- there jest no differentiation between an unread response body oraz a
     partially read response body

Note: this enforcement jest applied by the HTTPConnection class. The
      HTTPResponse klasa does nie enforce this state machine, which
      implies sophisticated clients may accelerate the request/response
      pipeline. Caution should be taken, though: accelerating the states
      beyond the above pattern may imply knowledge of the server's
      connection-close behavior dla certain requests. For example, it
      jest impossible to tell whether the server will close the connection
      UNTIL the response headers have been read; this means that further
      requests cannot be placed into the pipeline until it jest known that
      the server will NOT be closing the connection.

Logical State                  __state            __response
-------------                  -------            ----------
Idle                           _CS_IDLE           Nic
Request-started                _CS_REQ_STARTED    Nic
Request-sent                   _CS_REQ_SENT       Nic
Unread-response                _CS_IDLE           <response_class>
Req-started-unread-response    _CS_REQ_STARTED    <response_class>
Req-sent-unread-response       _CS_REQ_SENT       <response_class>
"""

zaimportuj email.parser
zaimportuj email.message
zaimportuj http
zaimportuj io
zaimportuj os
zaimportuj re
zaimportuj socket
zaimportuj collections
z urllib.parse zaimportuj urlsplit

# HTTPMessage, parse_headers(), oraz the HTTP status code constants are
# intentionally omitted dla simplicity
__all__ = ["HTTPResponse", "HTTPConnection",
           "HTTPException", "NotConnected", "UnknownProtocol",
           "UnknownTransferEncoding", "UnimplementedFileMode",
           "IncompleteRead", "InvalidURL", "ImproperConnectionState",
           "CannotSendRequest", "CannotSendHeader", "ResponseNotReady",
           "BadStatusLine", "LineTooLong", "RemoteDisconnected", "error",
           "responses"]

HTTP_PORT = 80
HTTPS_PORT = 443

_UNKNOWN = 'UNKNOWN'

# connection states
_CS_IDLE = 'Idle'
_CS_REQ_STARTED = 'Request-started'
_CS_REQ_SENT = 'Request-sent'


# hack to maintain backwards compatibility
globals().update(http.HTTPStatus.__members__)

# another hack to maintain backwards compatibility
# Mapping status codes to official W3C names
responses = {v: v.phrase dla v w http.HTTPStatus.__members__.values()}

# maximal amount of data to read at one time w _safe_read
MAXAMOUNT = 1048576

# maximal line length when calling readline().
_MAXLINE = 65536
_MAXHEADERS = 100

# Header name/value ABNF (http://tools.ietf.org/html/rfc7230#section-3.2)
#
# VCHAR          = %x21-7E
# obs-text       = %x80-FF
# header-field   = field-name ":" OWS field-value OWS
# field-name     = token
# field-value    = *( field-content / obs-fold )
# field-content  = field-vchar [ 1*( SP / HTAB ) field-vchar ]
# field-vchar    = VCHAR / obs-text
#
# obs-fold       = CRLF 1*( SP / HTAB )
#                ; obsolete line folding
#                ; see Section 3.2.4

# token          = 1*tchar
#
# tchar          = "!" / "#" / "$" / "%" / "&" / "'" / "*"
#                / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~"
#                / DIGIT / ALPHA
#                ; any VCHAR, wyjąwszy delimiters
#
# VCHAR defined w http://tools.ietf.org/html/rfc5234#appendix-B.1

# the patterns dla both name oraz value are more leniant than RFC
# definitions to allow dla backwards compatibility
_is_legal_header_name = re.compile(rb'[^:\s][^:\r\n]*').fullmatch
_is_illegal_header_value = re.compile(rb'\n(?![ \t])|\r(?![ \t\n])').search

# We always set the Content-Length header dla these methods because some
# servers will otherwise respond przy a 411
_METHODS_EXPECTING_BODY = {'PATCH', 'POST', 'PUT'}


klasa HTTPMessage(email.message.Message):
    # XXX The only usage of this method jest w
    # http.server.CGIHTTPRequestHandler.  Maybe move the code there so
    # that it doesn't need to be part of the public API.  The API has
    # never been defined so this could cause backwards compatibility
    # issues.

    def getallmatchingheaders(self, name):
        """Find all header lines matching a given header name.

        Look through the list of headers oraz find all lines matching a given
        header name (and their continuation lines).  A list of the lines jest
        returned, without interpretation.  If the header does nie occur, an
        empty list jest returned.  If the header occurs multiple times, all
        occurrences are returned.  Case jest nie important w the header name.

        """
        name = name.lower() + ':'
        n = len(name)
        lst = []
        hit = 0
        dla line w self.keys():
            jeżeli line[:n].lower() == name:
                hit = 1
            albo_inaczej nie line[:1].isspace():
                hit = 0
            jeżeli hit:
                lst.append(line)
        zwróć lst

def parse_headers(fp, _class=HTTPMessage):
    """Parses only RFC2822 headers z a file pointer.

    email Parser wants to see strings rather than bytes.
    But a TextIOWrapper around self.rfile would buffer too many bytes
    z the stream, bytes which we later need to read jako bytes.
    So we read the correct bytes here, jako bytes, dla email Parser
    to parse.

    """
    headers = []
    dopóki Prawda:
        line = fp.readline(_MAXLINE + 1)
        jeżeli len(line) > _MAXLINE:
            podnieś LineTooLong("header line")
        headers.append(line)
        jeżeli len(headers) > _MAXHEADERS:
            podnieś HTTPException("got more than %d headers" % _MAXHEADERS)
        jeżeli line w (b'\r\n', b'\n', b''):
            przerwij
    hstring = b''.join(headers).decode('iso-8859-1')
    zwróć email.parser.Parser(_class=_class).parsestr(hstring)


klasa HTTPResponse(io.BufferedIOBase):

    # See RFC 2616 sec 19.6 oraz RFC 1945 sec 6 dla details.

    # The bytes z the socket object are iso-8859-1 strings.
    # See RFC 2616 sec 2.2 which notes an exception dla MIME-encoded
    # text following RFC 2047.  The basic status line parsing only
    # accepts iso-8859-1.

    def __init__(self, sock, debuglevel=0, method=Nic, url=Nic):
        # If the response includes a content-length header, we need to
        # make sure that the client doesn't read more than the
        # specified number of bytes.  If it does, it will block until
        # the server times out oraz closes the connection.  This will
        # happen jeżeli a self.fp.read() jest done (without a size) whether
        # self.fp jest buffered albo not.  So, no self.fp.read() by
        # clients unless they know what they are doing.
        self.fp = sock.makefile("rb")
        self.debuglevel = debuglevel
        self._method = method

        # The HTTPResponse object jest returned via urllib.  The clients
        # of http oraz urllib expect different attributes dla the
        # headers.  headers jest used here oraz supports urllib.  msg jest
        # provided jako a backwards compatibility layer dla http
        # clients.

        self.headers = self.msg = Nic

        # z the Status-Line of the response
        self.version = _UNKNOWN # HTTP-Version
        self.status = _UNKNOWN  # Status-Code
        self.reason = _UNKNOWN  # Reason-Phrase

        self.chunked = _UNKNOWN         # jest "chunked" being used?
        self.chunk_left = _UNKNOWN      # bytes left to read w current chunk
        self.length = _UNKNOWN          # number of bytes left w response
        self.will_close = _UNKNOWN      # conn will close at end of response

    def _read_status(self):
        line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
        jeżeli len(line) > _MAXLINE:
            podnieś LineTooLong("status line")
        jeżeli self.debuglevel > 0:
            print("reply:", repr(line))
        jeżeli nie line:
            # Presumably, the server closed the connection before
            # sending a valid response.
            podnieś RemoteDisconnected("Remote end closed connection without"
                                     " response")
        spróbuj:
            version, status, reason = line.split(Nic, 2)
        wyjąwszy ValueError:
            spróbuj:
                version, status = line.split(Nic, 1)
                reason = ""
            wyjąwszy ValueError:
                # empty version will cause next test to fail.
                version = ""
        jeżeli nie version.startswith("HTTP/"):
            self._close_conn()
            podnieś BadStatusLine(line)

        # The status code jest a three-digit number
        spróbuj:
            status = int(status)
            jeżeli status < 100 albo status > 999:
                podnieś BadStatusLine(line)
        wyjąwszy ValueError:
            podnieś BadStatusLine(line)
        zwróć version, status, reason

    def begin(self):
        jeżeli self.headers jest nie Nic:
            # we've already started reading the response
            zwróć

        # read until we get a non-100 response
        dopóki Prawda:
            version, status, reason = self._read_status()
            jeżeli status != CONTINUE:
                przerwij
            # skip the header z the 100 response
            dopóki Prawda:
                skip = self.fp.readline(_MAXLINE + 1)
                jeżeli len(skip) > _MAXLINE:
                    podnieś LineTooLong("header line")
                skip = skip.strip()
                jeżeli nie skip:
                    przerwij
                jeżeli self.debuglevel > 0:
                    print("header:", skip)

        self.code = self.status = status
        self.reason = reason.strip()
        jeżeli version w ("HTTP/1.0", "HTTP/0.9"):
            # Some servers might still zwróć "0.9", treat it jako 1.0 anyway
            self.version = 10
        albo_inaczej version.startswith("HTTP/1."):
            self.version = 11   # use HTTP/1.1 code dla HTTP/1.x where x>=1
        inaczej:
            podnieś UnknownProtocol(version)

        self.headers = self.msg = parse_headers(self.fp)

        jeżeli self.debuglevel > 0:
            dla hdr w self.headers:
                print("header:", hdr, end=" ")

        # are we using the chunked-style of transfer encoding?
        tr_enc = self.headers.get("transfer-encoding")
        jeżeli tr_enc oraz tr_enc.lower() == "chunked":
            self.chunked = Prawda
            self.chunk_left = Nic
        inaczej:
            self.chunked = Nieprawda

        # will the connection close at the end of the response?
        self.will_close = self._check_close()

        # do we have a Content-Length?
        # NOTE: RFC 2616, S4.4, #3 says we ignore this jeżeli tr_enc jest "chunked"
        self.length = Nic
        length = self.headers.get("content-length")

         # are we using the chunked-style of transfer encoding?
        tr_enc = self.headers.get("transfer-encoding")
        jeżeli length oraz nie self.chunked:
            spróbuj:
                self.length = int(length)
            wyjąwszy ValueError:
                self.length = Nic
            inaczej:
                jeżeli self.length < 0:  # ignore nonsensical negative lengths
                    self.length = Nic
        inaczej:
            self.length = Nic

        # does the body have a fixed length? (of zero)
        jeżeli (status == NO_CONTENT albo status == NOT_MODIFIED albo
            100 <= status < 200 albo      # 1xx codes
            self._method == "HEAD"):
            self.length = 0

        # jeżeli the connection remains open, oraz we aren't using chunked, oraz
        # a content-length was nie provided, then assume that the connection
        # WILL close.
        jeżeli (nie self.will_close oraz
            nie self.chunked oraz
            self.length jest Nic):
            self.will_close = Prawda

    def _check_close(self):
        conn = self.headers.get("connection")
        jeżeli self.version == 11:
            # An HTTP/1.1 proxy jest assumed to stay open unless
            # explicitly closed.
            conn = self.headers.get("connection")
            jeżeli conn oraz "close" w conn.lower():
                zwróć Prawda
            zwróć Nieprawda

        # Some HTTP/1.0 implementations have support dla persistent
        # connections, using rules different than HTTP/1.1.

        # For older HTTP, Keep-Alive indicates persistent connection.
        jeżeli self.headers.get("keep-alive"):
            zwróć Nieprawda

        # At least Akamai returns a "Connection: Keep-Alive" header,
        # which was supposed to be sent by the client.
        jeżeli conn oraz "keep-alive" w conn.lower():
            zwróć Nieprawda

        # Proxy-Connection jest a netscape hack.
        pconn = self.headers.get("proxy-connection")
        jeżeli pconn oraz "keep-alive" w pconn.lower():
            zwróć Nieprawda

        # otherwise, assume it will close
        zwróć Prawda

    def _close_conn(self):
        fp = self.fp
        self.fp = Nic
        fp.close()

    def close(self):
        spróbuj:
            super().close() # set "closed" flag
        w_końcu:
            jeżeli self.fp:
                self._close_conn()

    # These implementations are dla the benefit of io.BufferedReader.

    # XXX This klasa should probably be revised to act more like
    # the "raw stream" that BufferedReader expects.

    def flush(self):
        super().flush()
        jeżeli self.fp:
            self.fp.flush()

    def readable(self):
        zwróć Prawda

    # End of "raw stream" methods

    def isclosed(self):
        """Prawda jeżeli the connection jest closed."""
        # NOTE: it jest possible that we will nie ever call self.close(). This
        #       case occurs when will_close jest TRUE, length jest Nic, oraz we
        #       read up to the last byte, but NOT past it.
        #
        # IMPLIES: jeżeli will_close jest FALSE, then self.close() will ALWAYS be
        #          called, meaning self.isclosed() jest meaningful.
        zwróć self.fp jest Nic

    def read(self, amt=Nic):
        jeżeli self.fp jest Nic:
            zwróć b""

        jeżeli self._method == "HEAD":
            self._close_conn()
            zwróć b""

        jeżeli amt jest nie Nic:
            # Amount jest given, implement using readinto
            b = bytearray(amt)
            n = self.readinto(b)
            zwróć memoryview(b)[:n].tobytes()
        inaczej:
            # Amount jest nie given (unbounded read) so we must check self.length
            # oraz self.chunked

            jeżeli self.chunked:
                zwróć self._readall_chunked()

            jeżeli self.length jest Nic:
                s = self.fp.read()
            inaczej:
                spróbuj:
                    s = self._safe_read(self.length)
                wyjąwszy IncompleteRead:
                    self._close_conn()
                    podnieś
                self.length = 0
            self._close_conn()        # we read everything
            zwróć s

    def readinto(self, b):
        jeżeli self.fp jest Nic:
            zwróć 0

        jeżeli self._method == "HEAD":
            self._close_conn()
            zwróć 0

        jeżeli self.chunked:
            zwróć self._readinto_chunked(b)

        jeżeli self.length jest nie Nic:
            jeżeli len(b) > self.length:
                # clip the read to the "end of response"
                b = memoryview(b)[0:self.length]

        # we do nie use _safe_read() here because this may be a .will_close
        # connection, oraz the user jest reading more bytes than will be provided
        # (dla example, reading w 1k chunks)
        n = self.fp.readinto(b)
        jeżeli nie n oraz b:
            # Ideally, we would podnieś IncompleteRead jeżeli the content-length
            # wasn't satisfied, but it might przerwij compatibility.
            self._close_conn()
        albo_inaczej self.length jest nie Nic:
            self.length -= n
            jeżeli nie self.length:
                self._close_conn()
        zwróć n

    def _read_next_chunk_size(self):
        # Read the next chunk size z the file
        line = self.fp.readline(_MAXLINE + 1)
        jeżeli len(line) > _MAXLINE:
            podnieś LineTooLong("chunk size")
        i = line.find(b";")
        jeżeli i >= 0:
            line = line[:i] # strip chunk-extensions
        spróbuj:
            zwróć int(line, 16)
        wyjąwszy ValueError:
            # close the connection jako protocol synchronisation jest
            # probably lost
            self._close_conn()
            podnieś

    def _read_and_discard_trailer(self):
        # read oraz discard trailer up to the CRLF terminator
        ### note: we shouldn't have any trailers!
        dopóki Prawda:
            line = self.fp.readline(_MAXLINE + 1)
            jeżeli len(line) > _MAXLINE:
                podnieś LineTooLong("trailer line")
            jeżeli nie line:
                # a vanishingly small number of sites EOF without
                # sending the trailer
                przerwij
            jeżeli line w (b'\r\n', b'\n', b''):
                przerwij

    def _get_chunk_left(self):
        # zwróć self.chunk_left, reading a new chunk jeżeli necessary.
        # chunk_left == 0: at the end of the current chunk, need to close it
        # chunk_left == Nic: No current chunk, should read next.
        # This function returns non-zero albo Nic jeżeli the last chunk has
        # been read.
        chunk_left = self.chunk_left
        jeżeli nie chunk_left: # Can be 0 albo Nic
            jeżeli chunk_left jest nie Nic:
                # We are at the end of chunk. dicard chunk end
                self._safe_read(2)  # toss the CRLF at the end of the chunk
            spróbuj:
                chunk_left = self._read_next_chunk_size()
            wyjąwszy ValueError:
                podnieś IncompleteRead(b'')
            jeżeli chunk_left == 0:
                # last chunk: 1*("0") [ chunk-extension ] CRLF
                self._read_and_discard_trailer()
                # we read everything; close the "file"
                self._close_conn()
                chunk_left = Nic
            self.chunk_left = chunk_left
        zwróć chunk_left

    def _readall_chunked(self):
        assert self.chunked != _UNKNOWN
        value = []
        spróbuj:
            dopóki Prawda:
                chunk_left = self._get_chunk_left()
                jeżeli chunk_left jest Nic:
                    przerwij
                value.append(self._safe_read(chunk_left))
                self.chunk_left = 0
            zwróć b''.join(value)
        wyjąwszy IncompleteRead:
            podnieś IncompleteRead(b''.join(value))

    def _readinto_chunked(self, b):
        assert self.chunked != _UNKNOWN
        total_bytes = 0
        mvb = memoryview(b)
        spróbuj:
            dopóki Prawda:
                chunk_left = self._get_chunk_left()
                jeżeli chunk_left jest Nic:
                    zwróć total_bytes

                jeżeli len(mvb) <= chunk_left:
                    n = self._safe_readinto(mvb)
                    self.chunk_left = chunk_left - n
                    zwróć total_bytes + n

                temp_mvb = mvb[:chunk_left]
                n = self._safe_readinto(temp_mvb)
                mvb = mvb[n:]
                total_bytes += n
                self.chunk_left = 0

        wyjąwszy IncompleteRead:
            podnieś IncompleteRead(bytes(b[0:total_bytes]))

    def _safe_read(self, amt):
        """Read the number of bytes requested, compensating dla partial reads.

        Normally, we have a blocking socket, but a read() can be interrupted
        by a signal (resulting w a partial read).

        Note that we cannot distinguish between EOF oraz an interrupt when zero
        bytes have been read. IncompleteRead() will be podnieśd w this
        situation.

        This function should be used when <amt> bytes "should" be present for
        reading. If the bytes are truly nie available (due to EOF), then the
        IncompleteRead exception can be used to detect the problem.
        """
        s = []
        dopóki amt > 0:
            chunk = self.fp.read(min(amt, MAXAMOUNT))
            jeżeli nie chunk:
                podnieś IncompleteRead(b''.join(s), amt)
            s.append(chunk)
            amt -= len(chunk)
        zwróć b"".join(s)

    def _safe_readinto(self, b):
        """Same jako _safe_read, but dla reading into a buffer."""
        total_bytes = 0
        mvb = memoryview(b)
        dopóki total_bytes < len(b):
            jeżeli MAXAMOUNT < len(mvb):
                temp_mvb = mvb[0:MAXAMOUNT]
                n = self.fp.readinto(temp_mvb)
            inaczej:
                n = self.fp.readinto(mvb)
            jeżeli nie n:
                podnieś IncompleteRead(bytes(mvb[0:total_bytes]), len(b))
            mvb = mvb[n:]
            total_bytes += n
        zwróć total_bytes

    def read1(self, n=-1):
        """Read przy at most one underlying system call.  If at least one
        byte jest buffered, zwróć that instead.
        """
        jeżeli self.fp jest Nic albo self._method == "HEAD":
            zwróć b""
        jeżeli self.chunked:
            zwróć self._read1_chunked(n)
        spróbuj:
            result = self.fp.read1(n)
        wyjąwszy ValueError:
            jeżeli n >= 0:
                podnieś
            # some implementations, like BufferedReader, don't support -1
            # Read an arbitrarily selected largeish chunk.
            result = self.fp.read1(16*1024)
        jeżeli nie result oraz n:
            self._close_conn()
        zwróć result

    def peek(self, n=-1):
        # Having this enables IOBase.readline() to read more than one
        # byte at a time
        jeżeli self.fp jest Nic albo self._method == "HEAD":
            zwróć b""
        jeżeli self.chunked:
            zwróć self._peek_chunked(n)
        zwróć self.fp.peek(n)

    def readline(self, limit=-1):
        jeżeli self.fp jest Nic albo self._method == "HEAD":
            zwróć b""
        jeżeli self.chunked:
            # Fallback to IOBase readline which uses peek() oraz read()
            zwróć super().readline(limit)
        result = self.fp.readline(limit)
        jeżeli nie result oraz limit:
            self._close_conn()
        zwróć result

    def _read1_chunked(self, n):
        # Strictly speaking, _get_chunk_left() may cause more than one read,
        # but that jest ok, since that jest to satisfy the chunked protocol.
        chunk_left = self._get_chunk_left()
        jeżeli chunk_left jest Nic albo n == 0:
            zwróć b''
        jeżeli nie (0 <= n <= chunk_left):
            n = chunk_left # jeżeli n jest negative albo larger than chunk_left
        read = self.fp.read1(n)
        self.chunk_left -= len(read)
        jeżeli nie read:
            podnieś IncompleteRead(b"")
        zwróć read

    def _peek_chunked(self, n):
        # Strictly speaking, _get_chunk_left() may cause more than one read,
        # but that jest ok, since that jest to satisfy the chunked protocol.
        spróbuj:
            chunk_left = self._get_chunk_left()
        wyjąwszy IncompleteRead:
            zwróć b'' # peek doesn't worry about protocol
        jeżeli chunk_left jest Nic:
            zwróć b'' # eof
        # peek jest allowed to zwróć more than requested.  Just request the
        # entire chunk, oraz truncate what we get.
        zwróć self.fp.peek(chunk_left)[:chunk_left]

    def fileno(self):
        zwróć self.fp.fileno()

    def getheader(self, name, default=Nic):
        jeżeli self.headers jest Nic:
            podnieś ResponseNotReady()
        headers = self.headers.get_all(name) albo default
        jeżeli isinstance(headers, str) albo nie hasattr(headers, '__iter__'):
            zwróć headers
        inaczej:
            zwróć ', '.join(headers)

    def getheaders(self):
        """Return list of (header, value) tuples."""
        jeżeli self.headers jest Nic:
            podnieś ResponseNotReady()
        zwróć list(self.headers.items())

    # We override IOBase.__iter__ so that it doesn't check dla closed-ness

    def __iter__(self):
        zwróć self

    # For compatibility przy old-style urllib responses.

    def info(self):
        zwróć self.headers

    def geturl(self):
        zwróć self.url

    def getcode(self):
        zwróć self.status

klasa HTTPConnection:

    _http_vsn = 11
    _http_vsn_str = 'HTTP/1.1'

    response_class = HTTPResponse
    default_port = HTTP_PORT
    auto_open = 1
    debuglevel = 0

    def __init__(self, host, port=Nic, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=Nic):
        self.timeout = timeout
        self.source_address = source_address
        self.sock = Nic
        self._buffer = []
        self.__response = Nic
        self.__state = _CS_IDLE
        self._method = Nic
        self._tunnel_host = Nic
        self._tunnel_port = Nic
        self._tunnel_headers = {}

        (self.host, self.port) = self._get_hostport(host, port)

        # This jest stored jako an instance variable to allow unit
        # tests to replace it przy a suitable mockup
        self._create_connection = socket.create_connection

    def set_tunnel(self, host, port=Nic, headers=Nic):
        """Set up host oraz port dla HTTP CONNECT tunnelling.

        In a connection that uses HTTP CONNECT tunneling, the host dalejed to the
        constructor jest used jako a proxy server that relays all communication to
        the endpoint dalejed to `set_tunnel`. This done by sending an HTTP
        CONNECT request to the proxy server when the connection jest established.

        This method must be called before the HTML connection has been
        established.

        The headers argument should be a mapping of extra HTTP headers to send
        przy the CONNECT request.
        """

        jeżeli self.sock:
            podnieś RuntimeError("Can't set up tunnel dla established connection")

        self._tunnel_host, self._tunnel_port = self._get_hostport(host, port)
        jeżeli headers:
            self._tunnel_headers = headers
        inaczej:
            self._tunnel_headers.clear()

    def _get_hostport(self, host, port):
        jeżeli port jest Nic:
            i = host.rfind(':')
            j = host.rfind(']')         # ipv6 addresses have [...]
            jeżeli i > j:
                spróbuj:
                    port = int(host[i+1:])
                wyjąwszy ValueError:
                    jeżeli host[i+1:] == "": # http://foo.com:/ == http://foo.com/
                        port = self.default_port
                    inaczej:
                        podnieś InvalidURL("nonnumeric port: '%s'" % host[i+1:])
                host = host[:i]
            inaczej:
                port = self.default_port
            jeżeli host oraz host[0] == '[' oraz host[-1] == ']':
                host = host[1:-1]

        zwróć (host, port)

    def set_debuglevel(self, level):
        self.debuglevel = level

    def _tunnel(self):
        connect_str = "CONNECT %s:%d HTTP/1.0\r\n" % (self._tunnel_host,
            self._tunnel_port)
        connect_bytes = connect_str.encode("ascii")
        self.send(connect_bytes)
        dla header, value w self._tunnel_headers.items():
            header_str = "%s: %s\r\n" % (header, value)
            header_bytes = header_str.encode("latin-1")
            self.send(header_bytes)
        self.send(b'\r\n')

        response = self.response_class(self.sock, method=self._method)
        (version, code, message) = response._read_status()

        jeżeli code != http.HTTPStatus.OK:
            self.close()
            podnieś OSError("Tunnel connection failed: %d %s" % (code,
                                                               message.strip()))
        dopóki Prawda:
            line = response.fp.readline(_MAXLINE + 1)
            jeżeli len(line) > _MAXLINE:
                podnieś LineTooLong("header line")
            jeżeli nie line:
                # dla sites which EOF without sending a trailer
                przerwij
            jeżeli line w (b'\r\n', b'\n', b''):
                przerwij

            jeżeli self.debuglevel > 0:
                print('header:', line.decode())

    def connect(self):
        """Connect to the host oraz port specified w __init__."""
        self.sock = self._create_connection(
            (self.host,self.port), self.timeout, self.source_address)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        jeżeli self._tunnel_host:
            self._tunnel()

    def close(self):
        """Close the connection to the HTTP server."""
        self.__state = _CS_IDLE
        spróbuj:
            sock = self.sock
            jeżeli sock:
                self.sock = Nic
                sock.close()   # close it manually... there may be other refs
        w_końcu:
            response = self.__response
            jeżeli response:
                self.__response = Nic
                response.close()

    def send(self, data):
        """Send `data' to the server.
        ``data`` can be a string object, a bytes object, an array object, a
        file-like object that supports a .read() method, albo an iterable object.
        """

        jeżeli self.sock jest Nic:
            jeżeli self.auto_open:
                self.connect()
            inaczej:
                podnieś NotConnected()

        jeżeli self.debuglevel > 0:
            print("send:", repr(data))
        blocksize = 8192
        jeżeli hasattr(data, "read") :
            jeżeli self.debuglevel > 0:
                print("sendIng a read()able")
            encode = Nieprawda
            spróbuj:
                mode = data.mode
            wyjąwszy AttributeError:
                # io.BytesIO oraz other file-like objects don't have a `mode`
                # attribute.
                dalej
            inaczej:
                jeżeli "b" nie w mode:
                    encode = Prawda
                    jeżeli self.debuglevel > 0:
                        print("encoding file using iso-8859-1")
            dopóki 1:
                datablock = data.read(blocksize)
                jeżeli nie datablock:
                    przerwij
                jeżeli encode:
                    datablock = datablock.encode("iso-8859-1")
                self.sock.sendall(datablock)
            zwróć
        spróbuj:
            self.sock.sendall(data)
        wyjąwszy TypeError:
            jeżeli isinstance(data, collections.Iterable):
                dla d w data:
                    self.sock.sendall(d)
            inaczej:
                podnieś TypeError("data should be a bytes-like object "
                                "or an iterable, got %r" % type(data))

    def _output(self, s):
        """Add a line of output to the current request buffer.

        Assumes that the line does *not* end przy \\r\\n.
        """
        self._buffer.append(s)

    def _send_output(self, message_body=Nic):
        """Send the currently buffered request oraz clear the buffer.

        Appends an extra \\r\\n to the buffer.
        A message_body may be specified, to be appended to the request.
        """
        self._buffer.extend((b"", b""))
        msg = b"\r\n".join(self._buffer)
        usuń self._buffer[:]

        self.send(msg)
        jeżeli message_body jest nie Nic:
            self.send(message_body)

    def putrequest(self, method, url, skip_host=0, skip_accept_encoding=0):
        """Send a request to the server.

        `method' specifies an HTTP request method, e.g. 'GET'.
        `url' specifies the object being requested, e.g. '/index.html'.
        `skip_host' jeżeli Prawda does nie add automatically a 'Host:' header
        `skip_accept_encoding' jeżeli Prawda does nie add automatically an
           'Accept-Encoding:' header
        """

        # jeżeli a prior response has been completed, then forget about it.
        jeżeli self.__response oraz self.__response.isclosed():
            self.__response = Nic


        # w certain cases, we cannot issue another request on this connection.
        # this occurs when:
        #   1) we are w the process of sending a request.   (_CS_REQ_STARTED)
        #   2) a response to a previous request has signalled that it jest going
        #      to close the connection upon completion.
        #   3) the headers dla the previous response have nie been read, thus
        #      we cannot determine whether point (2) jest true.   (_CS_REQ_SENT)
        #
        # jeżeli there jest no prior response, then we can request at will.
        #
        # jeżeli point (2) jest true, then we will have dalejed the socket to the
        # response (effectively meaning, "there jest no prior response"), oraz
        # will open a new one when a new request jest made.
        #
        # Note: jeżeli a prior response exists, then we *can* start a new request.
        #       We are nie allowed to begin fetching the response to this new
        #       request, however, until that prior response jest complete.
        #
        jeżeli self.__state == _CS_IDLE:
            self.__state = _CS_REQ_STARTED
        inaczej:
            podnieś CannotSendRequest(self.__state)

        # Save the method we use, we need it later w the response phase
        self._method = method
        jeżeli nie url:
            url = '/'
        request = '%s %s %s' % (method, url, self._http_vsn_str)

        # Non-ASCII characters should have been eliminated earlier
        self._output(request.encode('ascii'))

        jeżeli self._http_vsn == 11:
            # Issue some standard headers dla better HTTP/1.1 compliance

            jeżeli nie skip_host:
                # this header jest issued *only* dla HTTP/1.1
                # connections. more specifically, this means it jest
                # only issued when the client uses the new
                # HTTPConnection() class. backwards-compat clients
                # will be using HTTP/1.0 oraz those clients may be
                # issuing this header themselves. we should NOT issue
                # it twice; some web servers (such jako Apache) barf
                # when they see two Host: headers

                # If we need a non-standard port,include it w the
                # header.  If the request jest going through a proxy,
                # but the host of the actual URL, nie the host of the
                # proxy.

                netloc = ''
                jeżeli url.startswith('http'):
                    nil, netloc, nil, nil, nil = urlsplit(url)

                jeżeli netloc:
                    spróbuj:
                        netloc_enc = netloc.encode("ascii")
                    wyjąwszy UnicodeEncodeError:
                        netloc_enc = netloc.encode("idna")
                    self.putheader('Host', netloc_enc)
                inaczej:
                    jeżeli self._tunnel_host:
                        host = self._tunnel_host
                        port = self._tunnel_port
                    inaczej:
                        host = self.host
                        port = self.port

                    spróbuj:
                        host_enc = host.encode("ascii")
                    wyjąwszy UnicodeEncodeError:
                        host_enc = host.encode("idna")

                    # As per RFC 273, IPv6 address should be wrapped przy []
                    # when used jako Host header

                    jeżeli host.find(':') >= 0:
                        host_enc = b'[' + host_enc + b']'

                    jeżeli port == self.default_port:
                        self.putheader('Host', host_enc)
                    inaczej:
                        host_enc = host_enc.decode("ascii")
                        self.putheader('Host', "%s:%s" % (host_enc, port))

            # note: we are assuming that clients will nie attempt to set these
            #       headers since *this* library must deal przy the
            #       consequences. this also means that when the supporting
            #       libraries are updated to recognize other forms, then this
            #       code should be changed (removed albo updated).

            # we only want a Content-Encoding of "identity" since we don't
            # support encodings such jako x-gzip albo x-deflate.
            jeżeli nie skip_accept_encoding:
                self.putheader('Accept-Encoding', 'identity')

            # we can accept "chunked" Transfer-Encodings, but no others
            # NOTE: no TE header implies *only* "chunked"
            #self.putheader('TE', 'chunked')

            # jeżeli TE jest supplied w the header, then it must appear w a
            # Connection header.
            #self.putheader('Connection', 'TE')

        inaczej:
            # For HTTP/1.0, the server will assume "not chunked"
            dalej

    def putheader(self, header, *values):
        """Send a request header line to the server.

        For example: h.putheader('Accept', 'text/html')
        """
        jeżeli self.__state != _CS_REQ_STARTED:
            podnieś CannotSendHeader()

        jeżeli hasattr(header, 'encode'):
            header = header.encode('ascii')

        jeżeli nie _is_legal_header_name(header):
            podnieś ValueError('Invalid header name %r' % (header,))

        values = list(values)
        dla i, one_value w enumerate(values):
            jeżeli hasattr(one_value, 'encode'):
                values[i] = one_value.encode('latin-1')
            albo_inaczej isinstance(one_value, int):
                values[i] = str(one_value).encode('ascii')

            jeżeli _is_illegal_header_value(values[i]):
                podnieś ValueError('Invalid header value %r' % (values[i],))

        value = b'\r\n\t'.join(values)
        header = header + b': ' + value
        self._output(header)

    def endheaders(self, message_body=Nic):
        """Indicate that the last header line has been sent to the server.

        This method sends the request to the server.  The optional message_body
        argument can be used to dalej a message body associated przy the
        request.  The message body will be sent w the same packet jako the
        message headers jeżeli it jest a string, otherwise it jest sent jako a separate
        packet.
        """
        jeżeli self.__state == _CS_REQ_STARTED:
            self.__state = _CS_REQ_SENT
        inaczej:
            podnieś CannotSendHeader()
        self._send_output(message_body)

    def request(self, method, url, body=Nic, headers={}):
        """Send a complete request to the server."""
        self._send_request(method, url, body, headers)

    def _set_content_length(self, body, method):
        # Set the content-length based on the body. If the body jest "empty", we
        # set Content-Length: 0 dla methods that expect a body (RFC 7230,
        # Section 3.3.2). If the body jest set dla other methods, we set the
        # header provided we can figure out what the length is.
        thelen = Nic
        method_expects_body = method.upper() w _METHODS_EXPECTING_BODY
        jeżeli body jest Nic oraz method_expects_body:
            thelen = '0'
        albo_inaczej body jest nie Nic:
            spróbuj:
                thelen = str(len(body))
            wyjąwszy TypeError:
                # If this jest a file-like object, try to
                # fstat its file descriptor
                spróbuj:
                    thelen = str(os.fstat(body.fileno()).st_size)
                wyjąwszy (AttributeError, OSError):
                    # Don't send a length jeżeli this failed
                    jeżeli self.debuglevel > 0: print("Cannot stat!!")

        jeżeli thelen jest nie Nic:
            self.putheader('Content-Length', thelen)

    def _send_request(self, method, url, body, headers):
        # Honor explicitly requested Host: oraz Accept-Encoding: headers.
        header_names = dict.fromkeys([k.lower() dla k w headers])
        skips = {}
        jeżeli 'host' w header_names:
            skips['skip_host'] = 1
        jeżeli 'accept-encoding' w header_names:
            skips['skip_accept_encoding'] = 1

        self.putrequest(method, url, **skips)

        jeżeli 'content-length' nie w header_names:
            self._set_content_length(body, method)
        dla hdr, value w headers.items():
            self.putheader(hdr, value)
        jeżeli isinstance(body, str):
            # RFC 2616 Section 3.7.1 says that text default has a
            # default charset of iso-8859-1.
            body = body.encode('iso-8859-1')
        self.endheaders(body)

    def getresponse(self):
        """Get the response z the server.

        If the HTTPConnection jest w the correct state, returns an
        instance of HTTPResponse albo of whatever object jest returned by
        klasa the response_class variable.

        If a request has nie been sent albo jeżeli a previous response has
        nie be handled, ResponseNotReady jest podnieśd.  If the HTTP
        response indicates that the connection should be closed, then
        it will be closed before the response jest returned.  When the
        connection jest closed, the underlying socket jest closed.
        """

        # jeżeli a prior response has been completed, then forget about it.
        jeżeli self.__response oraz self.__response.isclosed():
            self.__response = Nic

        # jeżeli a prior response exists, then it must be completed (otherwise, we
        # cannot read this response's header to determine the connection-close
        # behavior)
        #
        # note: jeżeli a prior response existed, but was connection-close, then the
        # socket oraz response were made independent of this HTTPConnection
        # object since a new request requires that we open a whole new
        # connection
        #
        # this means the prior response had one of two states:
        #   1) will_close: this connection was reset oraz the prior socket oraz
        #                  response operate independently
        #   2) persistent: the response was retained oraz we await its
        #                  isclosed() status to become true.
        #
        jeżeli self.__state != _CS_REQ_SENT albo self.__response:
            podnieś ResponseNotReady(self.__state)

        jeżeli self.debuglevel > 0:
            response = self.response_class(self.sock, self.debuglevel,
                                           method=self._method)
        inaczej:
            response = self.response_class(self.sock, method=self._method)

        spróbuj:
            spróbuj:
                response.begin()
            wyjąwszy ConnectionError:
                self.close()
                podnieś
            assert response.will_close != _UNKNOWN
            self.__state = _CS_IDLE

            jeżeli response.will_close:
                # this effectively dalejes the connection to the response
                self.close()
            inaczej:
                # remember this, so we can tell when it jest complete
                self.__response = response

            zwróć response
        wyjąwszy:
            response.close()
            podnieś

spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    dalej
inaczej:
    klasa HTTPSConnection(HTTPConnection):
        "This klasa allows communication via SSL."

        default_port = HTTPS_PORT

        # XXX Should key_file oraz cert_file be deprecated w favour of context?

        def __init__(self, host, port=Nic, key_file=Nic, cert_file=Nic,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     source_address=Nic, *, context=Nic,
                     check_hostname=Nic):
            super(HTTPSConnection, self).__init__(host, port, timeout,
                                                  source_address)
            self.key_file = key_file
            self.cert_file = cert_file
            jeżeli context jest Nic:
                context = ssl._create_default_https_context()
            will_verify = context.verify_mode != ssl.CERT_NONE
            jeżeli check_hostname jest Nic:
                check_hostname = context.check_hostname
            jeżeli check_hostname oraz nie will_verify:
                podnieś ValueError("check_hostname needs a SSL context przy "
                                 "either CERT_OPTIONAL albo CERT_REQUIRED")
            jeżeli key_file albo cert_file:
                context.load_cert_chain(cert_file, key_file)
            self._context = context
            self._check_hostname = check_hostname

        def connect(self):
            "Connect to a host on a given (SSL) port."

            super().connect()

            jeżeli self._tunnel_host:
                server_hostname = self._tunnel_host
            inaczej:
                server_hostname = self.host

            self.sock = self._context.wrap_socket(self.sock,
                                                  server_hostname=server_hostname)
            jeżeli nie self._context.check_hostname oraz self._check_hostname:
                spróbuj:
                    ssl.match_hostname(self.sock.getpeercert(), server_hostname)
                wyjąwszy Exception:
                    self.sock.shutdown(socket.SHUT_RDWR)
                    self.sock.close()
                    podnieś

    __all__.append("HTTPSConnection")

klasa HTTPException(Exception):
    # Subclasses that define an __init__ must call Exception.__init__
    # albo define self.args.  Otherwise, str() will fail.
    dalej

klasa NotConnected(HTTPException):
    dalej

klasa InvalidURL(HTTPException):
    dalej

klasa UnknownProtocol(HTTPException):
    def __init__(self, version):
        self.args = version,
        self.version = version

klasa UnknownTransferEncoding(HTTPException):
    dalej

klasa UnimplementedFileMode(HTTPException):
    dalej

klasa IncompleteRead(HTTPException):
    def __init__(self, partial, expected=Nic):
        self.args = partial,
        self.partial = partial
        self.expected = expected
    def __repr__(self):
        jeżeli self.expected jest nie Nic:
            e = ', %i more expected' % self.expected
        inaczej:
            e = ''
        zwróć '%s(%i bytes read%s)' % (self.__class__.__name__,
                                        len(self.partial), e)
    def __str__(self):
        zwróć repr(self)

klasa ImproperConnectionState(HTTPException):
    dalej

klasa CannotSendRequest(ImproperConnectionState):
    dalej

klasa CannotSendHeader(ImproperConnectionState):
    dalej

klasa ResponseNotReady(ImproperConnectionState):
    dalej

klasa BadStatusLine(HTTPException):
    def __init__(self, line):
        jeżeli nie line:
            line = repr(line)
        self.args = line,
        self.line = line

klasa LineTooLong(HTTPException):
    def __init__(self, line_type):
        HTTPException.__init__(self, "got more than %d bytes when reading %s"
                                     % (_MAXLINE, line_type))

klasa RemoteDisconnected(ConnectionResetError, BadStatusLine):
    def __init__(self, *pos, **kw):
        BadStatusLine.__init__(self, "")
        ConnectionResetError.__init__(self, *pos, **kw)

# dla backwards compatibility
error = HTTPException
