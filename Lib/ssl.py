# Wrapper module dla _ssl, providing some additional facilities
# implemented w Python.  Written by Bill Janssen.

"""This module provides some more Pythonic support dla SSL.

Object types:

  SSLSocket -- subtype of socket.socket which does SSL over the socket

Exceptions:

  SSLError -- exception podnieśd dla I/O errors

Functions:

  cert_time_to_seconds -- convert time string used dla certificate
                          notBefore oraz notAfter functions to integer
                          seconds past the Epoch (the time values
                          returned z time.time())

  fetch_server_certificate (HOST, PORT) -- fetch the certificate provided
                          by the server running on HOST at port PORT.  No
                          validation of the certificate jest performed.

Integer constants:

SSL_ERROR_ZERO_RETURN
SSL_ERROR_WANT_READ
SSL_ERROR_WANT_WRITE
SSL_ERROR_WANT_X509_LOOKUP
SSL_ERROR_SYSCALL
SSL_ERROR_SSL
SSL_ERROR_WANT_CONNECT

SSL_ERROR_EOF
SSL_ERROR_INVALID_ERROR_CODE

The following group define certificate requirements that one side jest
allowing/requiring z the other side:

CERT_NONE - no certificates z the other side are required (or will
            be looked at jeżeli provided)
CERT_OPTIONAL - certificates are nie required, but jeżeli provided will be
                validated, oraz jeżeli validation fails, the connection will
                also fail
CERT_REQUIRED - certificates are required, oraz will be validated, oraz
                jeżeli validation fails, the connection will also fail

The following constants identify various SSL protocol variants:

PROTOCOL_SSLv2
PROTOCOL_SSLv3
PROTOCOL_SSLv23
PROTOCOL_TLSv1
PROTOCOL_TLSv1_1
PROTOCOL_TLSv1_2

The following constants identify various SSL alert message descriptions jako per
http://www.iana.org/assignments/tls-parameters/tls-parameters.xml#tls-parameters-6

ALERT_DESCRIPTION_CLOSE_NOTIFY
ALERT_DESCRIPTION_UNEXPECTED_MESSAGE
ALERT_DESCRIPTION_BAD_RECORD_MAC
ALERT_DESCRIPTION_RECORD_OVERFLOW
ALERT_DESCRIPTION_DECOMPRESSION_FAILURE
ALERT_DESCRIPTION_HANDSHAKE_FAILURE
ALERT_DESCRIPTION_BAD_CERTIFICATE
ALERT_DESCRIPTION_UNSUPPORTED_CERTIFICATE
ALERT_DESCRIPTION_CERTIFICATE_REVOKED
ALERT_DESCRIPTION_CERTIFICATE_EXPIRED
ALERT_DESCRIPTION_CERTIFICATE_UNKNOWN
ALERT_DESCRIPTION_ILLEGAL_PARAMETER
ALERT_DESCRIPTION_UNKNOWN_CA
ALERT_DESCRIPTION_ACCESS_DENIED
ALERT_DESCRIPTION_DECODE_ERROR
ALERT_DESCRIPTION_DECRYPT_ERROR
ALERT_DESCRIPTION_PROTOCOL_VERSION
ALERT_DESCRIPTION_INSUFFICIENT_SECURITY
ALERT_DESCRIPTION_INTERNAL_ERROR
ALERT_DESCRIPTION_USER_CANCELLED
ALERT_DESCRIPTION_NO_RENEGOTIATION
ALERT_DESCRIPTION_UNSUPPORTED_EXTENSION
ALERT_DESCRIPTION_CERTIFICATE_UNOBTAINABLE
ALERT_DESCRIPTION_UNRECOGNIZED_NAME
ALERT_DESCRIPTION_BAD_CERTIFICATE_STATUS_RESPONSE
ALERT_DESCRIPTION_BAD_CERTIFICATE_HASH_VALUE
ALERT_DESCRIPTION_UNKNOWN_PSK_IDENTITY
"""

zaimportuj ipaddress
zaimportuj textwrap
zaimportuj re
zaimportuj sys
zaimportuj os
z collections zaimportuj namedtuple
z enum zaimportuj Enum jako _Enum, IntEnum jako _IntEnum

zaimportuj _ssl             # jeżeli we can't zaimportuj it, let the error propagate

z _ssl zaimportuj OPENSSL_VERSION_NUMBER, OPENSSL_VERSION_INFO, OPENSSL_VERSION
z _ssl zaimportuj _SSLContext, MemoryBIO
z _ssl zaimportuj (
    SSLError, SSLZeroReturnError, SSLWantReadError, SSLWantWriteError,
    SSLSyscallError, SSLEOFError,
    )
z _ssl zaimportuj CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED
z _ssl zaimportuj txt2obj jako _txt2obj, nid2obj jako _nid2obj
z _ssl zaimportuj RAND_status, RAND_add, RAND_bytes, RAND_pseudo_bytes
spróbuj:
    z _ssl zaimportuj RAND_egd
wyjąwszy ImportError:
    # LibreSSL does nie provide RAND_egd
    dalej

def _import_symbols(prefix):
    dla n w dir(_ssl):
        jeżeli n.startswith(prefix):
            globals()[n] = getattr(_ssl, n)

_import_symbols('OP_')
_import_symbols('ALERT_DESCRIPTION_')
_import_symbols('SSL_ERROR_')
_import_symbols('VERIFY_')

z _ssl zaimportuj HAS_SNI, HAS_ECDH, HAS_NPN, HAS_ALPN

z _ssl zaimportuj _OPENSSL_API_VERSION

_IntEnum._convert(
        '_SSLMethod', __name__,
        lambda name: name.startswith('PROTOCOL_'),
        source=_ssl)

_PROTOCOL_NAMES = {value: name dla name, value w _SSLMethod.__members__.items()}

spróbuj:
    _SSLv2_IF_EXISTS = PROTOCOL_SSLv2
wyjąwszy NameError:
    _SSLv2_IF_EXISTS = Nic

jeżeli sys.platform == "win32":
    z _ssl zaimportuj enum_certificates, enum_crls

z socket zaimportuj socket, AF_INET, SOCK_STREAM, create_connection
z socket zaimportuj SOL_SOCKET, SO_TYPE
zaimportuj base64        # dla DER-to-PEM translation
zaimportuj errno


socket_error = OSError  # keep that public name w module namespace

jeżeli _ssl.HAS_TLS_UNIQUE:
    CHANNEL_BINDING_TYPES = ['tls-unique']
inaczej:
    CHANNEL_BINDING_TYPES = []

# Disable weak albo insecure ciphers by default
# (OpenSSL's default setting jest 'DEFAULT:!aNULL:!eNULL')
# Enable a better set of ciphers by default
# This list has been explicitly chosen to:
#   * Prefer cipher suites that offer perfect forward secrecy (DHE/ECDHE)
#   * Prefer ECDHE over DHE dla better performance
#   * Prefer any AES-GCM over any AES-CBC dla better performance oraz security
#   * Then Use HIGH cipher suites jako a fallback
#   * Then Use 3DES jako fallback which jest secure but slow
#   * Disable NULL authentication, NULL encryption, oraz MD5 MACs dla security
#     reasons
_DEFAULT_CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5'
)

# Restricted oraz more secure ciphers dla the server side
# This list has been explicitly chosen to:
#   * Prefer cipher suites that offer perfect forward secrecy (DHE/ECDHE)
#   * Prefer ECDHE over DHE dla better performance
#   * Prefer any AES-GCM over any AES-CBC dla better performance oraz security
#   * Then Use HIGH cipher suites jako a fallback
#   * Then Use 3DES jako fallback which jest secure but slow
#   * Disable NULL authentication, NULL encryption, MD5 MACs, DSS, oraz RC4 for
#     security reasons
_RESTRICTED_SERVER_CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5:!DSS:!RC4'
)


klasa CertificateError(ValueError):
    dalej


def _dnsname_match(dn, hostname, max_wildcards=1):
    """Matching according to RFC 6125, section 6.4.3

    http://tools.ietf.org/html/rfc6125#section-6.4.3
    """
    pats = []
    jeżeli nie dn:
        zwróć Nieprawda

    leftmost, *remainder = dn.split(r'.')

    wildcards = leftmost.count('*')
    jeżeli wildcards > max_wildcards:
        # Issue #17980: avoid denials of service by refusing more
        # than one wildcard per fragment.  A survey of established
        # policy among SSL implementations showed it to be a
        # reasonable choice.
        podnieś CertificateError(
            "too many wildcards w certificate DNS name: " + repr(dn))

    # speed up common case w/o wildcards
    jeżeli nie wildcards:
        zwróć dn.lower() == hostname.lower()

    # RFC 6125, section 6.4.3, subitem 1.
    # The client SHOULD NOT attempt to match a presented identifier w which
    # the wildcard character comprises a label other than the left-most label.
    jeżeli leftmost == '*':
        # When '*' jest a fragment by itself, it matches a non-empty dotless
        # fragment.
        pats.append('[^.]+')
    albo_inaczej leftmost.startswith('xn--') albo hostname.startswith('xn--'):
        # RFC 6125, section 6.4.3, subitem 3.
        # The client SHOULD NOT attempt to match a presented identifier
        # where the wildcard character jest embedded within an A-label albo
        # U-label of an internationalized domain name.
        pats.append(re.escape(leftmost))
    inaczej:
        # Otherwise, '*' matches any dotless string, e.g. www*
        pats.append(re.escape(leftmost).replace(r'\*', '[^.]*'))

    # add the remaining fragments, ignore any wildcards
    dla frag w remainder:
        pats.append(re.escape(frag))

    pat = re.compile(r'\A' + r'\.'.join(pats) + r'\Z', re.IGNORECASE)
    zwróć pat.match(hostname)


def _ipaddress_match(ipname, host_ip):
    """Exact matching of IP addresses.

    RFC 6125 explicitly doesn't define an algorithm dla this
    (section 1.7.2 - "Out of Scope").
    """
    # OpenSSL may add a trailing newline to a subjectAltName's IP address
    ip = ipaddress.ip_address(ipname.rstrip())
    zwróć ip == host_ip


def match_hostname(cert, hostname):
    """Verify that *cert* (in decoded format jako returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 oraz RFC 6125
    rules are followed, but IP addresses are nie accepted dla *hostname*.

    CertificateError jest podnieśd on failure. On success, the function
    returns nothing.
    """
    jeżeli nie cert:
        podnieś ValueError("empty albo no certificate, match_hostname needs a "
                         "SSL socket albo SSL context przy either "
                         "CERT_OPTIONAL albo CERT_REQUIRED")
    spróbuj:
        host_ip = ipaddress.ip_address(hostname)
    wyjąwszy ValueError:
        # Not an IP address (common case)
        host_ip = Nic
    dnsnames = []
    san = cert.get('subjectAltName', ())
    dla key, value w san:
        jeżeli key == 'DNS':
            jeżeli host_ip jest Nic oraz _dnsname_match(value, hostname):
                zwróć
            dnsnames.append(value)
        albo_inaczej key == 'IP Address':
            jeżeli host_ip jest nie Nic oraz _ipaddress_match(value, host_ip):
                zwróć
            dnsnames.append(value)
    jeżeli nie dnsnames:
        # The subject jest only checked when there jest no dNSName entry
        # w subjectAltName
        dla sub w cert.get('subject', ()):
            dla key, value w sub:
                # XXX according to RFC 2818, the most specific Common Name
                # must be used.
                jeżeli key == 'commonName':
                    jeżeli _dnsname_match(value, hostname):
                        zwróć
                    dnsnames.append(value)
    jeżeli len(dnsnames) > 1:
        podnieś CertificateError("hostname %r "
            "doesn't match either of %s"
            % (hostname, ', '.join(map(repr, dnsnames))))
    albo_inaczej len(dnsnames) == 1:
        podnieś CertificateError("hostname %r "
            "doesn't match %r"
            % (hostname, dnsnames[0]))
    inaczej:
        podnieś CertificateError("no appropriate commonName albo "
            "subjectAltName fields were found")


DefaultVerifyPaths = namedtuple("DefaultVerifyPaths",
    "cafile capath openssl_cafile_env openssl_cafile openssl_capath_env "
    "openssl_capath")

def get_default_verify_paths():
    """Return paths to default cafile oraz capath.
    """
    parts = _ssl.get_default_verify_paths()

    # environment vars shadow paths
    cafile = os.environ.get(parts[0], parts[1])
    capath = os.environ.get(parts[2], parts[3])

    zwróć DefaultVerifyPaths(cafile jeżeli os.path.isfile(cafile) inaczej Nic,
                              capath jeżeli os.path.isdir(capath) inaczej Nic,
                              *parts)


klasa _ASN1Object(namedtuple("_ASN1Object", "nid shortname longname oid")):
    """ASN.1 object identifier lookup
    """
    __slots__ = ()

    def __new__(cls, oid):
        zwróć super().__new__(cls, *_txt2obj(oid, name=Nieprawda))

    @classmethod
    def fromnid(cls, nid):
        """Create _ASN1Object z OpenSSL numeric ID
        """
        zwróć super().__new__(cls, *_nid2obj(nid))

    @classmethod
    def fromname(cls, name):
        """Create _ASN1Object z short name, long name albo OID
        """
        zwróć super().__new__(cls, *_txt2obj(name, name=Prawda))


klasa Purpose(_ASN1Object, _Enum):
    """SSLContext purpose flags przy X509v3 Extended Key Usage objects
    """
    SERVER_AUTH = '1.3.6.1.5.5.7.3.1'
    CLIENT_AUTH = '1.3.6.1.5.5.7.3.2'


klasa SSLContext(_SSLContext):
    """An SSLContext holds various SSL-related configuration options oraz
    data, such jako certificates oraz possibly a private key."""

    __slots__ = ('protocol', '__weakref__')
    _windows_cert_stores = ("CA", "ROOT")

    def __new__(cls, protocol, *args, **kwargs):
        self = _SSLContext.__new__(cls, protocol)
        jeżeli protocol != _SSLv2_IF_EXISTS:
            self.set_ciphers(_DEFAULT_CIPHERS)
        zwróć self

    def __init__(self, protocol):
        self.protocol = protocol

    def wrap_socket(self, sock, server_side=Nieprawda,
                    do_handshake_on_connect=Prawda,
                    suppress_ragged_eofs=Prawda,
                    server_hostname=Nic):
        zwróć SSLSocket(sock=sock, server_side=server_side,
                         do_handshake_on_connect=do_handshake_on_connect,
                         suppress_ragged_eofs=suppress_ragged_eofs,
                         server_hostname=server_hostname,
                         _context=self)

    def wrap_bio(self, incoming, outgoing, server_side=Nieprawda,
                 server_hostname=Nic):
        sslobj = self._wrap_bio(incoming, outgoing, server_side=server_side,
                                server_hostname=server_hostname)
        zwróć SSLObject(sslobj)

    def set_npn_protocols(self, npn_protocols):
        protos = bytearray()
        dla protocol w npn_protocols:
            b = bytes(protocol, 'ascii')
            jeżeli len(b) == 0 albo len(b) > 255:
                podnieś SSLError('NPN protocols must be 1 to 255 w length')
            protos.append(len(b))
            protos.extend(b)

        self._set_npn_protocols(protos)

    def set_alpn_protocols(self, alpn_protocols):
        protos = bytearray()
        dla protocol w alpn_protocols:
            b = bytes(protocol, 'ascii')
            jeżeli len(b) == 0 albo len(b) > 255:
                podnieś SSLError('ALPN protocols must be 1 to 255 w length')
            protos.append(len(b))
            protos.extend(b)

        self._set_alpn_protocols(protos)

    def _load_windows_store_certs(self, storename, purpose):
        certs = bytearray()
        dla cert, encoding, trust w enum_certificates(storename):
            # CA certs are never PKCS#7 encoded
            jeżeli encoding == "x509_asn":
                jeżeli trust jest Prawda albo purpose.oid w trust:
                    certs.extend(cert)
        self.load_verify_locations(cadata=certs)
        zwróć certs

    def load_default_certs(self, purpose=Purpose.SERVER_AUTH):
        jeżeli nie isinstance(purpose, _ASN1Object):
            podnieś TypeError(purpose)
        jeżeli sys.platform == "win32":
            dla storename w self._windows_cert_stores:
                self._load_windows_store_certs(storename, purpose)
        self.set_default_verify_paths()


def create_default_context(purpose=Purpose.SERVER_AUTH, *, cafile=Nic,
                           capath=Nic, cadata=Nic):
    """Create a SSLContext object przy default settings.

    NOTE: The protocol oraz settings may change anytime without prior
          deprecation. The values represent a fair balance between maximum
          compatibility oraz security.
    """
    jeżeli nie isinstance(purpose, _ASN1Object):
        podnieś TypeError(purpose)

    context = SSLContext(PROTOCOL_SSLv23)

    # SSLv2 considered harmful.
    context.options |= OP_NO_SSLv2

    # SSLv3 has problematic security oraz jest only required dla really old
    # clients such jako IE6 on Windows XP
    context.options |= OP_NO_SSLv3

    # disable compression to prevent CRIME attacks (OpenSSL 1.0+)
    context.options |= getattr(_ssl, "OP_NO_COMPRESSION", 0)

    jeżeli purpose == Purpose.SERVER_AUTH:
        # verify certs oraz host name w client mode
        context.verify_mode = CERT_REQUIRED
        context.check_hostname = Prawda
    albo_inaczej purpose == Purpose.CLIENT_AUTH:
        # Prefer the server's ciphers by default so that we get stronger
        # encryption
        context.options |= getattr(_ssl, "OP_CIPHER_SERVER_PREFERENCE", 0)

        # Use single use keys w order to improve forward secrecy
        context.options |= getattr(_ssl, "OP_SINGLE_DH_USE", 0)
        context.options |= getattr(_ssl, "OP_SINGLE_ECDH_USE", 0)

        # disallow ciphers przy known vulnerabilities
        context.set_ciphers(_RESTRICTED_SERVER_CIPHERS)

    jeżeli cafile albo capath albo cadata:
        context.load_verify_locations(cafile, capath, cadata)
    albo_inaczej context.verify_mode != CERT_NONE:
        # no explicit cafile, capath albo cadata but the verify mode jest
        # CERT_OPTIONAL albo CERT_REQUIRED. Let's try to load default system
        # root CA certificates dla the given purpose. This may fail silently.
        context.load_default_certs(purpose)
    zwróć context

def _create_unverified_context(protocol=PROTOCOL_SSLv23, *, cert_reqs=Nic,
                           check_hostname=Nieprawda, purpose=Purpose.SERVER_AUTH,
                           certfile=Nic, keyfile=Nic,
                           cafile=Nic, capath=Nic, cadata=Nic):
    """Create a SSLContext object dla Python stdlib modules

    All Python stdlib modules shall use this function to create SSLContext
    objects w order to keep common settings w one place. The configuration
    jest less restrict than create_default_context()'s to increase backward
    compatibility.
    """
    jeżeli nie isinstance(purpose, _ASN1Object):
        podnieś TypeError(purpose)

    context = SSLContext(protocol)
    # SSLv2 considered harmful.
    context.options |= OP_NO_SSLv2
    # SSLv3 has problematic security oraz jest only required dla really old
    # clients such jako IE6 on Windows XP
    context.options |= OP_NO_SSLv3

    jeżeli cert_reqs jest nie Nic:
        context.verify_mode = cert_reqs
    context.check_hostname = check_hostname

    jeżeli keyfile oraz nie certfile:
        podnieś ValueError("certfile must be specified")
    jeżeli certfile albo keyfile:
        context.load_cert_chain(certfile, keyfile)

    # load CA root certs
    jeżeli cafile albo capath albo cadata:
        context.load_verify_locations(cafile, capath, cadata)
    albo_inaczej context.verify_mode != CERT_NONE:
        # no explicit cafile, capath albo cadata but the verify mode jest
        # CERT_OPTIONAL albo CERT_REQUIRED. Let's try to load default system
        # root CA certificates dla the given purpose. This may fail silently.
        context.load_default_certs(purpose)

    zwróć context

# Used by http.client jeżeli no context jest explicitly dalejed.
_create_default_https_context = create_default_context


# Backwards compatibility alias, even though it's nie a public name.
_create_stdlib_context = _create_unverified_context


klasa SSLObject:
    """This klasa implements an interface on top of a low-level SSL object as
    implemented by OpenSSL. This object captures the state of an SSL connection
    but does nie provide any network IO itself. IO needs to be performed
    through separate "BIO" objects which are OpenSSL's IO abstraction layer.

    This klasa does nie have a public constructor. Instances are returned by
    ``SSLContext.wrap_bio``. This klasa jest typically used by framework authors
    that want to implement asynchronous IO dla SSL through memory buffers.

    When compared to ``SSLSocket``, this object lacks the following features:

     * Any form of network IO incluging methods such jako ``recv`` oraz ``send``.
     * The ``do_handshake_on_connect`` oraz ``suppress_ragged_eofs`` machinery.
    """

    def __init__(self, sslobj, owner=Nic):
        self._sslobj = sslobj
        # Note: _sslobj takes a weak reference to owner
        self._sslobj.owner = owner albo self

    @property
    def context(self):
        """The SSLContext that jest currently w use."""
        zwróć self._sslobj.context

    @context.setter
    def context(self, ctx):
        self._sslobj.context = ctx

    @property
    def server_side(self):
        """Whether this jest a server-side socket."""
        zwróć self._sslobj.server_side

    @property
    def server_hostname(self):
        """The currently set server hostname (dla SNI), albo ``Nic`` jeżeli no
        server hostame jest set."""
        zwróć self._sslobj.server_hostname

    def read(self, len=0, buffer=Nic):
        """Read up to 'len' bytes z the SSL object oraz zwróć them.

        If 'buffer' jest provided, read into this buffer oraz zwróć the number of
        bytes read.
        """
        jeżeli buffer jest nie Nic:
            v = self._sslobj.read(len, buffer)
        inaczej:
            v = self._sslobj.read(len albo 1024)
        zwróć v

    def write(self, data):
        """Write 'data' to the SSL object oraz zwróć the number of bytes
        written.

        The 'data' argument must support the buffer interface.
        """
        zwróć self._sslobj.write(data)

    def getpeercert(self, binary_form=Nieprawda):
        """Returns a formatted version of the data w the certificate provided
        by the other end of the SSL channel.

        Return Nic jeżeli no certificate was provided, {} jeżeli a certificate was
        provided, but nie validated.
        """
        zwróć self._sslobj.peer_certificate(binary_form)

    def selected_npn_protocol(self):
        """Return the currently selected NPN protocol jako a string, albo ``Nic``
        jeżeli a next protocol was nie negotiated albo jeżeli NPN jest nie supported by one
        of the peers."""
        jeżeli _ssl.HAS_NPN:
            zwróć self._sslobj.selected_npn_protocol()

    def selected_alpn_protocol(self):
        """Return the currently selected ALPN protocol jako a string, albo ``Nic``
        jeżeli a next protocol was nie negotiated albo jeżeli ALPN jest nie supported by one
        of the peers."""
        jeżeli _ssl.HAS_ALPN:
            zwróć self._sslobj.selected_alpn_protocol()

    def cipher(self):
        """Return the currently selected cipher jako a 3-tuple ``(name,
        ssl_version, secret_bits)``."""
        zwróć self._sslobj.cipher()

    def shared_ciphers(self):
        """Return a list of ciphers shared by the client during the handshake albo
        Nic jeżeli this jest nie a valid server connection.
        """
        zwróć self._sslobj.shared_ciphers()

    def compression(self):
        """Return the current compression algorithm w use, albo ``Nic`` if
        compression was nie negotiated albo nie supported by one of the peers."""
        zwróć self._sslobj.compression()

    def pending(self):
        """Return the number of bytes that can be read immediately."""
        zwróć self._sslobj.pending()

    def do_handshake(self):
        """Start the SSL/TLS handshake."""
        self._sslobj.do_handshake()
        jeżeli self.context.check_hostname:
            jeżeli nie self.server_hostname:
                podnieś ValueError("check_hostname needs server_hostname "
                                 "argument")
            match_hostname(self.getpeercert(), self.server_hostname)

    def unwrap(self):
        """Start the SSL shutdown handshake."""
        zwróć self._sslobj.shutdown()

    def get_channel_binding(self, cb_type="tls-unique"):
        """Get channel binding data dla current connection.  Raise ValueError
        jeżeli the requested `cb_type` jest nie supported.  Return bytes of the data
        albo Nic jeżeli the data jest nie available (e.g. before the handshake)."""
        jeżeli cb_type nie w CHANNEL_BINDING_TYPES:
            podnieś ValueError("Unsupported channel binding type")
        jeżeli cb_type != "tls-unique":
            podnieś NotImplementedError(
                            "{0} channel binding type nie implemented"
                            .format(cb_type))
        zwróć self._sslobj.tls_unique_cb()

    def version(self):
        """Return a string identifying the protocol version used by the
        current SSL channel. """
        zwróć self._sslobj.version()


klasa SSLSocket(socket):
    """This klasa implements a subtype of socket.socket that wraps
    the underlying OS socket w an SSL context when necessary, oraz
    provides read oraz write methods over that channel."""

    def __init__(self, sock=Nic, keyfile=Nic, certfile=Nic,
                 server_side=Nieprawda, cert_reqs=CERT_NONE,
                 ssl_version=PROTOCOL_SSLv23, ca_certs=Nic,
                 do_handshake_on_connect=Prawda,
                 family=AF_INET, type=SOCK_STREAM, proto=0, fileno=Nic,
                 suppress_ragged_eofs=Prawda, npn_protocols=Nic, ciphers=Nic,
                 server_hostname=Nic,
                 _context=Nic):

        jeżeli _context:
            self._context = _context
        inaczej:
            jeżeli server_side oraz nie certfile:
                podnieś ValueError("certfile must be specified dla server-side "
                                 "operations")
            jeżeli keyfile oraz nie certfile:
                podnieś ValueError("certfile must be specified")
            jeżeli certfile oraz nie keyfile:
                keyfile = certfile
            self._context = SSLContext(ssl_version)
            self._context.verify_mode = cert_reqs
            jeżeli ca_certs:
                self._context.load_verify_locations(ca_certs)
            jeżeli certfile:
                self._context.load_cert_chain(certfile, keyfile)
            jeżeli npn_protocols:
                self._context.set_npn_protocols(npn_protocols)
            jeżeli ciphers:
                self._context.set_ciphers(ciphers)
            self.keyfile = keyfile
            self.certfile = certfile
            self.cert_reqs = cert_reqs
            self.ssl_version = ssl_version
            self.ca_certs = ca_certs
            self.ciphers = ciphers
        # Can't use sock.type jako other flags (such jako SOCK_NONBLOCK) get
        # mixed in.
        jeżeli sock.getsockopt(SOL_SOCKET, SO_TYPE) != SOCK_STREAM:
            podnieś NotImplementedError("only stream sockets are supported")
        jeżeli server_side oraz server_hostname:
            podnieś ValueError("server_hostname can only be specified "
                             "in client mode")
        jeżeli self._context.check_hostname oraz nie server_hostname:
            podnieś ValueError("check_hostname requires server_hostname")
        self.server_side = server_side
        self.server_hostname = server_hostname
        self.do_handshake_on_connect = do_handshake_on_connect
        self.suppress_ragged_eofs = suppress_ragged_eofs
        jeżeli sock jest nie Nic:
            socket.__init__(self,
                            family=sock.family,
                            type=sock.type,
                            proto=sock.proto,
                            fileno=sock.fileno())
            self.settimeout(sock.gettimeout())
            sock.detach()
        albo_inaczej fileno jest nie Nic:
            socket.__init__(self, fileno=fileno)
        inaczej:
            socket.__init__(self, family=family, type=type, proto=proto)

        # See jeżeli we are connected
        spróbuj:
            self.getpeername()
        wyjąwszy OSError jako e:
            jeżeli e.errno != errno.ENOTCONN:
                podnieś
            connected = Nieprawda
        inaczej:
            connected = Prawda

        self._closed = Nieprawda
        self._sslobj = Nic
        self._connected = connected
        jeżeli connected:
            # create the SSL object
            spróbuj:
                sslobj = self._context._wrap_socket(self, server_side,
                                                    server_hostname)
                self._sslobj = SSLObject(sslobj, owner=self)
                jeżeli do_handshake_on_connect:
                    timeout = self.gettimeout()
                    jeżeli timeout == 0.0:
                        # non-blocking
                        podnieś ValueError("do_handshake_on_connect should nie be specified dla non-blocking sockets")
                    self.do_handshake()

            wyjąwszy (OSError, ValueError):
                self.close()
                podnieś

    @property
    def context(self):
        zwróć self._context

    @context.setter
    def context(self, ctx):
        self._context = ctx
        self._sslobj.context = ctx

    def dup(self):
        podnieś NotImplemented("Can't dup() %s instances" %
                             self.__class__.__name__)

    def _checkClosed(self, msg=Nic):
        # podnieś an exception here jeżeli you wish to check dla spurious closes
        dalej

    def _check_connected(self):
        jeżeli nie self._connected:
            # getpeername() will podnieś ENOTCONN jeżeli the socket jest really
            # nie connected; note that we can be connected even without
            # _connected being set, e.g. jeżeli connect() first returned
            # EAGAIN.
            self.getpeername()

    def read(self, len=0, buffer=Nic):
        """Read up to LEN bytes oraz zwróć them.
        Return zero-length string on EOF."""

        self._checkClosed()
        jeżeli nie self._sslobj:
            podnieś ValueError("Read on closed albo unwrapped SSL socket.")
        spróbuj:
            zwróć self._sslobj.read(len, buffer)
        wyjąwszy SSLError jako x:
            jeżeli x.args[0] == SSL_ERROR_EOF oraz self.suppress_ragged_eofs:
                jeżeli buffer jest nie Nic:
                    zwróć 0
                inaczej:
                    zwróć b''
            inaczej:
                podnieś

    def write(self, data):
        """Write DATA to the underlying SSL channel.  Returns
        number of bytes of DATA actually transmitted."""

        self._checkClosed()
        jeżeli nie self._sslobj:
            podnieś ValueError("Write on closed albo unwrapped SSL socket.")
        zwróć self._sslobj.write(data)

    def getpeercert(self, binary_form=Nieprawda):
        """Returns a formatted version of the data w the
        certificate provided by the other end of the SSL channel.
        Return Nic jeżeli no certificate was provided, {} jeżeli a
        certificate was provided, but nie validated."""

        self._checkClosed()
        self._check_connected()
        zwróć self._sslobj.getpeercert(binary_form)

    def selected_npn_protocol(self):
        self._checkClosed()
        jeżeli nie self._sslobj albo nie _ssl.HAS_NPN:
            zwróć Nic
        inaczej:
            zwróć self._sslobj.selected_npn_protocol()

    def selected_alpn_protocol(self):
        self._checkClosed()
        jeżeli nie self._sslobj albo nie _ssl.HAS_ALPN:
            zwróć Nic
        inaczej:
            zwróć self._sslobj.selected_alpn_protocol()

    def cipher(self):
        self._checkClosed()
        jeżeli nie self._sslobj:
            zwróć Nic
        inaczej:
            zwróć self._sslobj.cipher()

    def shared_ciphers(self):
        self._checkClosed()
        jeżeli nie self._sslobj:
            zwróć Nic
        zwróć self._sslobj.shared_ciphers()

    def compression(self):
        self._checkClosed()
        jeżeli nie self._sslobj:
            zwróć Nic
        inaczej:
            zwróć self._sslobj.compression()

    def send(self, data, flags=0):
        self._checkClosed()
        jeżeli self._sslobj:
            jeżeli flags != 0:
                podnieś ValueError(
                    "non-zero flags nie allowed w calls to send() on %s" %
                    self.__class__)
            zwróć self._sslobj.write(data)
        inaczej:
            zwróć socket.send(self, data, flags)

    def sendto(self, data, flags_or_addr, addr=Nic):
        self._checkClosed()
        jeżeli self._sslobj:
            podnieś ValueError("sendto nie allowed on instances of %s" %
                             self.__class__)
        albo_inaczej addr jest Nic:
            zwróć socket.sendto(self, data, flags_or_addr)
        inaczej:
            zwróć socket.sendto(self, data, flags_or_addr, addr)

    def sendmsg(self, *args, **kwargs):
        # Ensure programs don't send data unencrypted jeżeli they try to
        # use this method.
        podnieś NotImplementedError("sendmsg nie allowed on instances of %s" %
                                  self.__class__)

    def sendall(self, data, flags=0):
        self._checkClosed()
        jeżeli self._sslobj:
            jeżeli flags != 0:
                podnieś ValueError(
                    "non-zero flags nie allowed w calls to sendall() on %s" %
                    self.__class__)
            amount = len(data)
            count = 0
            dopóki (count < amount):
                v = self.send(data[count:])
                count += v
            zwróć amount
        inaczej:
            zwróć socket.sendall(self, data, flags)

    def sendfile(self, file, offset=0, count=Nic):
        """Send a file, possibly by using os.sendfile() jeżeli this jest a
        clear-text socket.  Return the total number of bytes sent.
        """
        jeżeli self._sslobj jest Nic:
            # os.sendfile() works przy plain sockets only
            zwróć super().sendfile(file, offset, count)
        inaczej:
            zwróć self._sendfile_use_send(file, offset, count)

    def recv(self, buflen=1024, flags=0):
        self._checkClosed()
        jeżeli self._sslobj:
            jeżeli flags != 0:
                podnieś ValueError(
                    "non-zero flags nie allowed w calls to recv() on %s" %
                    self.__class__)
            zwróć self.read(buflen)
        inaczej:
            zwróć socket.recv(self, buflen, flags)

    def recv_into(self, buffer, nbytes=Nic, flags=0):
        self._checkClosed()
        jeżeli buffer oraz (nbytes jest Nic):
            nbytes = len(buffer)
        albo_inaczej nbytes jest Nic:
            nbytes = 1024
        jeżeli self._sslobj:
            jeżeli flags != 0:
                podnieś ValueError(
                  "non-zero flags nie allowed w calls to recv_into() on %s" %
                  self.__class__)
            zwróć self.read(nbytes, buffer)
        inaczej:
            zwróć socket.recv_into(self, buffer, nbytes, flags)

    def recvfrom(self, buflen=1024, flags=0):
        self._checkClosed()
        jeżeli self._sslobj:
            podnieś ValueError("recvz nie allowed on instances of %s" %
                             self.__class__)
        inaczej:
            zwróć socket.recvfrom(self, buflen, flags)

    def recvfrom_into(self, buffer, nbytes=Nic, flags=0):
        self._checkClosed()
        jeżeli self._sslobj:
            podnieś ValueError("recvfrom_into nie allowed on instances of %s" %
                             self.__class__)
        inaczej:
            zwróć socket.recvfrom_into(self, buffer, nbytes, flags)

    def recvmsg(self, *args, **kwargs):
        podnieś NotImplementedError("recvmsg nie allowed on instances of %s" %
                                  self.__class__)

    def recvmsg_into(self, *args, **kwargs):
        podnieś NotImplementedError("recvmsg_into nie allowed on instances of "
                                  "%s" % self.__class__)

    def pending(self):
        self._checkClosed()
        jeżeli self._sslobj:
            zwróć self._sslobj.pending()
        inaczej:
            zwróć 0

    def shutdown(self, how):
        self._checkClosed()
        self._sslobj = Nic
        socket.shutdown(self, how)

    def unwrap(self):
        jeżeli self._sslobj:
            s = self._sslobj.unwrap()
            self._sslobj = Nic
            zwróć s
        inaczej:
            podnieś ValueError("No SSL wrapper around " + str(self))

    def _real_close(self):
        self._sslobj = Nic
        socket._real_close(self)

    def do_handshake(self, block=Nieprawda):
        """Perform a TLS/SSL handshake."""
        self._check_connected()
        timeout = self.gettimeout()
        spróbuj:
            jeżeli timeout == 0.0 oraz block:
                self.settimeout(Nic)
            self._sslobj.do_handshake()
        w_końcu:
            self.settimeout(timeout)

    def _real_connect(self, addr, connect_ex):
        jeżeli self.server_side:
            podnieś ValueError("can't connect w server-side mode")
        # Here we assume that the socket jest client-side, oraz nie
        # connected at the time of the call.  We connect it, then wrap it.
        jeżeli self._connected:
            podnieś ValueError("attempt to connect already-connected SSLSocket!")
        sslobj = self.context._wrap_socket(self, Nieprawda, self.server_hostname)
        self._sslobj = SSLObject(sslobj, owner=self)
        spróbuj:
            jeżeli connect_ex:
                rc = socket.connect_ex(self, addr)
            inaczej:
                rc = Nic
                socket.connect(self, addr)
            jeżeli nie rc:
                self._connected = Prawda
                jeżeli self.do_handshake_on_connect:
                    self.do_handshake()
            zwróć rc
        wyjąwszy (OSError, ValueError):
            self._sslobj = Nic
            podnieś

    def connect(self, addr):
        """Connects to remote ADDR, oraz then wraps the connection w
        an SSL channel."""
        self._real_connect(addr, Nieprawda)

    def connect_ex(self, addr):
        """Connects to remote ADDR, oraz then wraps the connection w
        an SSL channel."""
        zwróć self._real_connect(addr, Prawda)

    def accept(self):
        """Accepts a new connection z a remote client, oraz returns
        a tuple containing that new connection wrapped przy a server-side
        SSL channel, oraz the address of the remote client."""

        newsock, addr = socket.accept(self)
        newsock = self.context.wrap_socket(newsock,
                    do_handshake_on_connect=self.do_handshake_on_connect,
                    suppress_ragged_eofs=self.suppress_ragged_eofs,
                    server_side=Prawda)
        zwróć newsock, addr

    def get_channel_binding(self, cb_type="tls-unique"):
        """Get channel binding data dla current connection.  Raise ValueError
        jeżeli the requested `cb_type` jest nie supported.  Return bytes of the data
        albo Nic jeżeli the data jest nie available (e.g. before the handshake).
        """
        jeżeli self._sslobj jest Nic:
            zwróć Nic
        zwróć self._sslobj.get_channel_binding(cb_type)

    def version(self):
        """
        Return a string identifying the protocol version used by the
        current SSL channel, albo Nic jeżeli there jest no established channel.
        """
        jeżeli self._sslobj jest Nic:
            zwróć Nic
        zwróć self._sslobj.version()


def wrap_socket(sock, keyfile=Nic, certfile=Nic,
                server_side=Nieprawda, cert_reqs=CERT_NONE,
                ssl_version=PROTOCOL_SSLv23, ca_certs=Nic,
                do_handshake_on_connect=Prawda,
                suppress_ragged_eofs=Prawda,
                ciphers=Nic):

    zwróć SSLSocket(sock=sock, keyfile=keyfile, certfile=certfile,
                     server_side=server_side, cert_reqs=cert_reqs,
                     ssl_version=ssl_version, ca_certs=ca_certs,
                     do_handshake_on_connect=do_handshake_on_connect,
                     suppress_ragged_eofs=suppress_ragged_eofs,
                     ciphers=ciphers)

# some utility functions

def cert_time_to_seconds(cert_time):
    """Return the time w seconds since the Epoch, given the timestring
    representing the "notBefore" albo "notAfter" date z a certificate
    w ``"%b %d %H:%M:%S %Y %Z"`` strptime format (C locale).

    "notBefore" albo "notAfter" dates must use UTC (RFC 5280).

    Month jest one of: Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
    UTC should be specified jako GMT (see ASN1_TIME_print())
    """
    z time zaimportuj strptime
    z calendar zaimportuj timegm

    months = (
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    )
    time_format = ' %d %H:%M:%S %Y GMT' # NOTE: no month, fixed GMT
    spróbuj:
        month_number = months.index(cert_time[:3].title()) + 1
    wyjąwszy ValueError:
        podnieś ValueError('time data %r does nie match '
                         'format "%%b%s"' % (cert_time, time_format))
    inaczej:
        # found valid month
        tt = strptime(cert_time[3:], time_format)
        # zwróć an integer, the previous mktime()-based implementation
        # returned a float (fractional seconds are always zero here).
        zwróć timegm((tt[0], month_number) + tt[2:6])

PEM_HEADER = "-----BEGIN CERTIFICATE-----"
PEM_FOOTER = "-----END CERTIFICATE-----"

def DER_cert_to_PEM_cert(der_cert_bytes):
    """Takes a certificate w binary DER format oraz returns the
    PEM version of it jako a string."""

    f = str(base64.standard_b64encode(der_cert_bytes), 'ASCII', 'strict')
    zwróć (PEM_HEADER + '\n' +
            textwrap.fill(f, 64) + '\n' +
            PEM_FOOTER + '\n')

def PEM_cert_to_DER_cert(pem_cert_string):
    """Takes a certificate w ASCII PEM format oraz returns the
    DER-encoded version of it jako a byte sequence"""

    jeżeli nie pem_cert_string.startswith(PEM_HEADER):
        podnieś ValueError("Invalid PEM encoding; must start przy %s"
                         % PEM_HEADER)
    jeżeli nie pem_cert_string.strip().endswith(PEM_FOOTER):
        podnieś ValueError("Invalid PEM encoding; must end przy %s"
                         % PEM_FOOTER)
    d = pem_cert_string.strip()[len(PEM_HEADER):-len(PEM_FOOTER)]
    zwróć base64.decodebytes(d.encode('ASCII', 'strict'))

def get_server_certificate(addr, ssl_version=PROTOCOL_SSLv23, ca_certs=Nic):
    """Retrieve the certificate z the server at the specified address,
    oraz zwróć it jako a PEM-encoded string.
    If 'ca_certs' jest specified, validate the server cert against it.
    If 'ssl_version' jest specified, use it w the connection attempt."""

    host, port = addr
    jeżeli ca_certs jest nie Nic:
        cert_reqs = CERT_REQUIRED
    inaczej:
        cert_reqs = CERT_NONE
    context = _create_stdlib_context(ssl_version,
                                     cert_reqs=cert_reqs,
                                     cafile=ca_certs)
    przy  create_connection(addr) jako sock:
        przy context.wrap_socket(sock) jako sslsock:
            dercert = sslsock.getpeercert(Prawda)
    zwróć DER_cert_to_PEM_cert(dercert)

def get_protocol_name(protocol_code):
    zwróć _PROTOCOL_NAMES.get(protocol_code, '<unknown>')
