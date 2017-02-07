# Test the support dla SSL oraz sockets

zaimportuj sys
zaimportuj unittest
z test zaimportuj support
zaimportuj socket
zaimportuj select
zaimportuj time
zaimportuj datetime
zaimportuj gc
zaimportuj os
zaimportuj errno
zaimportuj pprint
zaimportuj tempfile
zaimportuj urllib.request
zaimportuj traceback
zaimportuj asyncore
zaimportuj weakref
zaimportuj platform
zaimportuj functools

ssl = support.import_module("ssl")

PROTOCOLS = sorted(ssl._PROTOCOL_NAMES)
HOST = support.HOST

def data_file(*name):
    zwróć os.path.join(os.path.dirname(__file__), *name)

# The custom key oraz certificate files used w test_ssl are generated
# using Lib/test/make_ssl_certs.py.
# Other certificates are simply fetched z the Internet servers they
# are meant to authenticate.

CERTFILE = data_file("keycert.pem")
BYTES_CERTFILE = os.fsencode(CERTFILE)
ONLYCERT = data_file("ssl_cert.pem")
ONLYKEY = data_file("ssl_key.pem")
BYTES_ONLYCERT = os.fsencode(ONLYCERT)
BYTES_ONLYKEY = os.fsencode(ONLYKEY)
CERTFILE_PROTECTED = data_file("keycert.passwd.pem")
ONLYKEY_PROTECTED = data_file("ssl_key.passwd.pem")
KEY_PASSWORD = "somepass"
CAPATH = data_file("capath")
BYTES_CAPATH = os.fsencode(CAPATH)
CAFILE_NEURONIO = data_file("capath", "4e1295a3.0")
CAFILE_CACERT = data_file("capath", "5ed36f99.0")


# empty CRL
CRLFILE = data_file("revocation.crl")

# Two keys oraz certs signed by the same CA (dla SNI tests)
SIGNED_CERTFILE = data_file("keycert3.pem")
SIGNED_CERTFILE2 = data_file("keycert4.pem")
SIGNING_CA = data_file("pycacert.pem")

SVN_PYTHON_ORG_ROOT_CERT = data_file("https_svn_python_org_root.pem")

EMPTYCERT = data_file("nullcert.pem")
BADCERT = data_file("badcert.pem")
WRONGCERT = data_file("XXXnonexisting.pem")
BADKEY = data_file("badkey.pem")
NOKIACERT = data_file("nokia.pem")
NULLBYTECERT = data_file("nullbytecert.pem")

DHFILE = data_file("dh1024.pem")
BYTES_DHFILE = os.fsencode(DHFILE)


def handle_error(prefix):
    exc_format = ' '.join(traceback.format_exception(*sys.exc_info()))
    jeżeli support.verbose:
        sys.stdout.write(prefix + exc_format)

def can_clear_options():
    # 0.9.8m albo higher
    zwróć ssl._OPENSSL_API_VERSION >= (0, 9, 8, 13, 15)

def no_sslv2_implies_sslv3_hello():
    # 0.9.7h albo higher
    zwróć ssl.OPENSSL_VERSION_INFO >= (0, 9, 7, 8, 15)

def have_verify_flags():
    # 0.9.8 albo higher
    zwróć ssl.OPENSSL_VERSION_INFO >= (0, 9, 8, 0, 15)

def utc_offset(): #NOTE: ignore issues like #1647654
    # local time = utc time + utc offset
    jeżeli time.daylight oraz time.localtime().tm_isdst > 0:
        zwróć -time.altzone  # seconds
    zwróć -time.timezone

def asn1time(cert_time):
    # Some versions of OpenSSL ignore seconds, see #18207
    # 0.9.8.i
    jeżeli ssl._OPENSSL_API_VERSION == (0, 9, 8, 9, 15):
        fmt = "%b %d %H:%M:%S %Y GMT"
        dt = datetime.datetime.strptime(cert_time, fmt)
        dt = dt.replace(second=0)
        cert_time = dt.strftime(fmt)
        # %d adds leading zero but ASN1_TIME_print() uses leading space
        jeżeli cert_time[4] == "0":
            cert_time = cert_time[:4] + " " + cert_time[5:]

    zwróć cert_time

# Issue #9415: Ubuntu hijacks their OpenSSL oraz forcefully disables SSLv2
def skip_if_broken_ubuntu_ssl(func):
    jeżeli hasattr(ssl, 'PROTOCOL_SSLv2'):
        @functools.wraps(func)
        def f(*args, **kwargs):
            spróbuj:
                ssl.SSLContext(ssl.PROTOCOL_SSLv2)
            wyjąwszy ssl.SSLError:
                jeżeli (ssl.OPENSSL_VERSION_INFO == (0, 9, 8, 15, 15) oraz
                    platform.linux_distribution() == ('debian', 'squeeze/sid', '')):
                    podnieś unittest.SkipTest("Patched Ubuntu OpenSSL przerwijs behaviour")
            zwróć func(*args, **kwargs)
        zwróć f
    inaczej:
        zwróć func

needs_sni = unittest.skipUnless(ssl.HAS_SNI, "SNI support needed dla this test")


klasa BasicSocketTests(unittest.TestCase):

    def test_constants(self):
        ssl.CERT_NONE
        ssl.CERT_OPTIONAL
        ssl.CERT_REQUIRED
        ssl.OP_CIPHER_SERVER_PREFERENCE
        ssl.OP_SINGLE_DH_USE
        jeżeli ssl.HAS_ECDH:
            ssl.OP_SINGLE_ECDH_USE
        jeżeli ssl.OPENSSL_VERSION_INFO >= (1, 0):
            ssl.OP_NO_COMPRESSION
        self.assertIn(ssl.HAS_SNI, {Prawda, Nieprawda})
        self.assertIn(ssl.HAS_ECDH, {Prawda, Nieprawda})

    def test_str_for_enums(self):
        # Make sure that the PROTOCOL_* constants have enum-like string
        # reprs.
        proto = ssl.PROTOCOL_SSLv23
        self.assertEqual(str(proto), '_SSLMethod.PROTOCOL_SSLv23')
        ctx = ssl.SSLContext(proto)
        self.assertIs(ctx.protocol, proto)

    def test_random(self):
        v = ssl.RAND_status()
        jeżeli support.verbose:
            sys.stdout.write("\n RAND_status jest %d (%s)\n"
                             % (v, (v oraz "sufficient randomness") albo
                                "insufficient randomness"))

        data, is_cryptographic = ssl.RAND_pseudo_bytes(16)
        self.assertEqual(len(data), 16)
        self.assertEqual(is_cryptographic, v == 1)
        jeżeli v:
            data = ssl.RAND_bytes(16)
            self.assertEqual(len(data), 16)
        inaczej:
            self.assertRaises(ssl.SSLError, ssl.RAND_bytes, 16)

        # negative num jest invalid
        self.assertRaises(ValueError, ssl.RAND_bytes, -5)
        self.assertRaises(ValueError, ssl.RAND_pseudo_bytes, -5)

        jeżeli hasattr(ssl, 'RAND_egd'):
            self.assertRaises(TypeError, ssl.RAND_egd, 1)
            self.assertRaises(TypeError, ssl.RAND_egd, 'foo', 1)
        ssl.RAND_add("this jest a random string", 75.0)
        ssl.RAND_add(b"this jest a random bytes object", 75.0)
        ssl.RAND_add(bytearray(b"this jest a random bytearray object"), 75.0)

    @unittest.skipUnless(os.name == 'posix', 'requires posix')
    def test_random_fork(self):
        status = ssl.RAND_status()
        jeżeli nie status:
            self.fail("OpenSSL's PRNG has insufficient randomness")

        rfd, wfd = os.pipe()
        pid = os.fork()
        jeżeli pid == 0:
            spróbuj:
                os.close(rfd)
                child_random = ssl.RAND_pseudo_bytes(16)[0]
                self.assertEqual(len(child_random), 16)
                os.write(wfd, child_random)
                os.close(wfd)
            wyjąwszy BaseException:
                os._exit(1)
            inaczej:
                os._exit(0)
        inaczej:
            os.close(wfd)
            self.addCleanup(os.close, rfd)
            _, status = os.waitpid(pid, 0)
            self.assertEqual(status, 0)

            child_random = os.read(rfd, 16)
            self.assertEqual(len(child_random), 16)
            parent_random = ssl.RAND_pseudo_bytes(16)[0]
            self.assertEqual(len(parent_random), 16)

            self.assertNotEqual(child_random, parent_random)

    def test_parse_cert(self):
        # note that this uses an 'unofficial' function w _ssl.c,
        # provided solely dla this test, to exercise the certificate
        # parsing code
        p = ssl._ssl._test_decode_cert(CERTFILE)
        jeżeli support.verbose:
            sys.stdout.write("\n" + pprint.pformat(p) + "\n")
        self.assertEqual(p['issuer'],
                         ((('countryName', 'XY'),),
                          (('localityName', 'Castle Anthrax'),),
                          (('organizationName', 'Python Software Foundation'),),
                          (('commonName', 'localhost'),))
                        )
        # Note the next three asserts will fail jeżeli the keys are regenerated
        self.assertEqual(p['notAfter'], asn1time('Oct  5 23:01:56 2020 GMT'))
        self.assertEqual(p['notBefore'], asn1time('Oct  8 23:01:56 2010 GMT'))
        self.assertEqual(p['serialNumber'], 'D7C7381919AFC24E')
        self.assertEqual(p['subject'],
                         ((('countryName', 'XY'),),
                          (('localityName', 'Castle Anthrax'),),
                          (('organizationName', 'Python Software Foundation'),),
                          (('commonName', 'localhost'),))
                        )
        self.assertEqual(p['subjectAltName'], (('DNS', 'localhost'),))
        # Issue #13034: the subjectAltName w some certificates
        # (nieably projects.developer.nokia.com:443) wasn't parsed
        p = ssl._ssl._test_decode_cert(NOKIACERT)
        jeżeli support.verbose:
            sys.stdout.write("\n" + pprint.pformat(p) + "\n")
        self.assertEqual(p['subjectAltName'],
                         (('DNS', 'projects.developer.nokia.com'),
                          ('DNS', 'projects.forum.nokia.com'))
                        )
        # extra OCSP oraz AIA fields
        self.assertEqual(p['OCSP'], ('http://ocsp.verisign.com',))
        self.assertEqual(p['caIssuers'],
                         ('http://SVRIntl-G3-aia.verisign.com/SVRIntlG3.cer',))
        self.assertEqual(p['crlDistributionPoints'],
                         ('http://SVRIntl-G3-crl.verisign.com/SVRIntlG3.crl',))

    def test_parse_cert_CVE_2013_4238(self):
        p = ssl._ssl._test_decode_cert(NULLBYTECERT)
        jeżeli support.verbose:
            sys.stdout.write("\n" + pprint.pformat(p) + "\n")
        subject = ((('countryName', 'US'),),
                   (('stateOrProvinceName', 'Oregon'),),
                   (('localityName', 'Beaverton'),),
                   (('organizationName', 'Python Software Foundation'),),
                   (('organizationalUnitName', 'Python Core Development'),),
                   (('commonName', 'null.python.org\x00example.org'),),
                   (('emailAddress', 'python-dev@python.org'),))
        self.assertEqual(p['subject'], subject)
        self.assertEqual(p['issuer'], subject)
        jeżeli ssl._OPENSSL_API_VERSION >= (0, 9, 8):
            san = (('DNS', 'altnull.python.org\x00example.com'),
                   ('email', 'null@python.org\x00user@example.org'),
                   ('URI', 'http://null.python.org\x00http://example.org'),
                   ('IP Address', '192.0.2.1'),
                   ('IP Address', '2001:DB8:0:0:0:0:0:1\n'))
        inaczej:
            # OpenSSL 0.9.7 doesn't support IPv6 addresses w subjectAltName
            san = (('DNS', 'altnull.python.org\x00example.com'),
                   ('email', 'null@python.org\x00user@example.org'),
                   ('URI', 'http://null.python.org\x00http://example.org'),
                   ('IP Address', '192.0.2.1'),
                   ('IP Address', '<invalid>'))

        self.assertEqual(p['subjectAltName'], san)

    def test_DER_to_PEM(self):
        przy open(SVN_PYTHON_ORG_ROOT_CERT, 'r') jako f:
            pem = f.read()
        d1 = ssl.PEM_cert_to_DER_cert(pem)
        p2 = ssl.DER_cert_to_PEM_cert(d1)
        d2 = ssl.PEM_cert_to_DER_cert(p2)
        self.assertEqual(d1, d2)
        jeżeli nie p2.startswith(ssl.PEM_HEADER + '\n'):
            self.fail("DER-to-PEM didn't include correct header:\n%r\n" % p2)
        jeżeli nie p2.endswith('\n' + ssl.PEM_FOOTER + '\n'):
            self.fail("DER-to-PEM didn't include correct footer:\n%r\n" % p2)

    def test_openssl_version(self):
        n = ssl.OPENSSL_VERSION_NUMBER
        t = ssl.OPENSSL_VERSION_INFO
        s = ssl.OPENSSL_VERSION
        self.assertIsInstance(n, int)
        self.assertIsInstance(t, tuple)
        self.assertIsInstance(s, str)
        # Some sanity checks follow
        # >= 0.9
        self.assertGreaterEqual(n, 0x900000)
        # < 3.0
        self.assertLess(n, 0x30000000)
        major, minor, fix, patch, status = t
        self.assertGreaterEqual(major, 0)
        self.assertLess(major, 3)
        self.assertGreaterEqual(minor, 0)
        self.assertLess(minor, 256)
        self.assertGreaterEqual(fix, 0)
        self.assertLess(fix, 256)
        self.assertGreaterEqual(patch, 0)
        self.assertLessEqual(patch, 63)
        self.assertGreaterEqual(status, 0)
        self.assertLessEqual(status, 15)
        # Version string jako returned by {Open,Libre}SSL, the format might change
        jeżeli "LibreSSL" w s:
            self.assertPrawda(s.startswith("LibreSSL {:d}.{:d}".format(major, minor)),
                            (s, t, hex(n)))
        inaczej:
            self.assertPrawda(s.startswith("OpenSSL {:d}.{:d}.{:d}".format(major, minor, fix)),
                            (s, t, hex(n)))

    @support.cpython_only
    def test_refcycle(self):
        # Issue #7943: an SSL object doesn't create reference cycles with
        # itself.
        s = socket.socket(socket.AF_INET)
        ss = ssl.wrap_socket(s)
        wr = weakref.ref(ss)
        przy support.check_warnings(("", ResourceWarning)):
            usuń ss
            self.assertEqual(wr(), Nic)

    def test_wrapped_unconnected(self):
        # Methods on an unconnected SSLSocket propagate the original
        # OSError podnieś by the underlying socket object.
        s = socket.socket(socket.AF_INET)
        przy ssl.wrap_socket(s) jako ss:
            self.assertRaises(OSError, ss.recv, 1)
            self.assertRaises(OSError, ss.recv_into, bytearray(b'x'))
            self.assertRaises(OSError, ss.recvfrom, 1)
            self.assertRaises(OSError, ss.recvfrom_into, bytearray(b'x'), 1)
            self.assertRaises(OSError, ss.send, b'x')
            self.assertRaises(OSError, ss.sendto, b'x', ('0.0.0.0', 0))

    def test_timeout(self):
        # Issue #8524: when creating an SSL socket, the timeout of the
        # original socket should be retained.
        dla timeout w (Nic, 0.0, 5.0):
            s = socket.socket(socket.AF_INET)
            s.settimeout(timeout)
            przy ssl.wrap_socket(s) jako ss:
                self.assertEqual(timeout, ss.gettimeout())

    def test_errors(self):
        sock = socket.socket()
        self.assertRaisesRegex(ValueError,
                        "certfile must be specified",
                        ssl.wrap_socket, sock, keyfile=CERTFILE)
        self.assertRaisesRegex(ValueError,
                        "certfile must be specified dla server-side operations",
                        ssl.wrap_socket, sock, server_side=Prawda)
        self.assertRaisesRegex(ValueError,
                        "certfile must be specified dla server-side operations",
                        ssl.wrap_socket, sock, server_side=Prawda, certfile="")
        przy ssl.wrap_socket(sock, server_side=Prawda, certfile=CERTFILE) jako s:
            self.assertRaisesRegex(ValueError, "can't connect w server-side mode",
                                    s.connect, (HOST, 8080))
        przy self.assertRaises(OSError) jako cm:
            przy socket.socket() jako sock:
                ssl.wrap_socket(sock, certfile=WRONGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        przy self.assertRaises(OSError) jako cm:
            przy socket.socket() jako sock:
                ssl.wrap_socket(sock, certfile=CERTFILE, keyfile=WRONGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        przy self.assertRaises(OSError) jako cm:
            przy socket.socket() jako sock:
                ssl.wrap_socket(sock, certfile=WRONGCERT, keyfile=WRONGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)

    def test_match_hostname(self):
        def ok(cert, hostname):
            ssl.match_hostname(cert, hostname)
        def fail(cert, hostname):
            self.assertRaises(ssl.CertificateError,
                              ssl.match_hostname, cert, hostname)

        # -- Hostname matching --

        cert = {'subject': ((('commonName', 'example.com'),),)}
        ok(cert, 'example.com')
        ok(cert, 'ExAmple.cOm')
        fail(cert, 'www.example.com')
        fail(cert, '.example.com')
        fail(cert, 'example.org')
        fail(cert, 'exampleXcom')

        cert = {'subject': ((('commonName', '*.a.com'),),)}
        ok(cert, 'foo.a.com')
        fail(cert, 'bar.foo.a.com')
        fail(cert, 'a.com')
        fail(cert, 'Xa.com')
        fail(cert, '.a.com')

        # only match one left-most wildcard
        cert = {'subject': ((('commonName', 'f*.com'),),)}
        ok(cert, 'foo.com')
        ok(cert, 'f.com')
        fail(cert, 'bar.com')
        fail(cert, 'foo.a.com')
        fail(cert, 'bar.foo.com')

        # NULL bytes are bad, CVE-2013-4073
        cert = {'subject': ((('commonName',
                              'null.python.org\x00example.org'),),)}
        ok(cert, 'null.python.org\x00example.org') # albo podnieś an error?
        fail(cert, 'example.org')
        fail(cert, 'null.python.org')

        # error cases przy wildcards
        cert = {'subject': ((('commonName', '*.*.a.com'),),)}
        fail(cert, 'bar.foo.a.com')
        fail(cert, 'a.com')
        fail(cert, 'Xa.com')
        fail(cert, '.a.com')

        cert = {'subject': ((('commonName', 'a.*.com'),),)}
        fail(cert, 'a.foo.com')
        fail(cert, 'a..com')
        fail(cert, 'a.com')

        # wildcard doesn't match IDNA prefix 'xn--'
        idna = 'püthon.python.org'.encode("idna").decode("ascii")
        cert = {'subject': ((('commonName', idna),),)}
        ok(cert, idna)
        cert = {'subject': ((('commonName', 'x*.python.org'),),)}
        fail(cert, idna)
        cert = {'subject': ((('commonName', 'xn--p*.python.org'),),)}
        fail(cert, idna)

        # wildcard w first fragment oraz  IDNA A-labels w sequent fragments
        # are supported.
        idna = 'www*.pythön.org'.encode("idna").decode("ascii")
        cert = {'subject': ((('commonName', idna),),)}
        ok(cert, 'www.pythön.org'.encode("idna").decode("ascii"))
        ok(cert, 'www1.pythön.org'.encode("idna").decode("ascii"))
        fail(cert, 'ftp.pythön.org'.encode("idna").decode("ascii"))
        fail(cert, 'pythön.org'.encode("idna").decode("ascii"))

        # Slightly fake real-world example
        cert = {'notAfter': 'Jun 26 21:41:46 2011 GMT',
                'subject': ((('commonName', 'linuxfrz.org'),),),
                'subjectAltName': (('DNS', 'linuxfr.org'),
                                   ('DNS', 'linuxfr.com'),
                                   ('othername', '<unsupported>'))}
        ok(cert, 'linuxfr.org')
        ok(cert, 'linuxfr.com')
        # Not a "DNS" entry
        fail(cert, '<unsupported>')
        # When there jest a subjectAltName, commonName isn't used
        fail(cert, 'linuxfrz.org')

        # A pristine real-world example
        cert = {'notAfter': 'Dec 18 23:59:59 2011 GMT',
                'subject': ((('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'Mountain View'),),
                            (('organizationName', 'Google Inc'),),
                            (('commonName', 'mail.google.com'),))}
        ok(cert, 'mail.google.com')
        fail(cert, 'gmail.com')
        # Only commonName jest considered
        fail(cert, 'California')

        # -- IPv4 matching --
        cert = {'subject': ((('commonName', 'example.com'),),),
                'subjectAltName': (('DNS', 'example.com'),
                                   ('IP Address', '10.11.12.13'),
                                   ('IP Address', '14.15.16.17'))}
        ok(cert, '10.11.12.13')
        ok(cert, '14.15.16.17')
        fail(cert, '14.15.16.18')
        fail(cert, 'example.net')

        # -- IPv6 matching --
        cert = {'subject': ((('commonName', 'example.com'),),),
                'subjectAltName': (('DNS', 'example.com'),
                                   ('IP Address', '2001:0:0:0:0:0:0:CAFE\n'),
                                   ('IP Address', '2003:0:0:0:0:0:0:BABA\n'))}
        ok(cert, '2001::cafe')
        ok(cert, '2003::baba')
        fail(cert, '2003::bebe')
        fail(cert, 'example.net')

        # -- Miscellaneous --

        # Neither commonName nor subjectAltName
        cert = {'notAfter': 'Dec 18 23:59:59 2011 GMT',
                'subject': ((('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'Mountain View'),),
                            (('organizationName', 'Google Inc'),))}
        fail(cert, 'mail.google.com')

        # No DNS entry w subjectAltName but a commonName
        cert = {'notAfter': 'Dec 18 23:59:59 2099 GMT',
                'subject': ((('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'Mountain View'),),
                            (('commonName', 'mail.google.com'),)),
                'subjectAltName': (('othername', 'blabla'), )}
        ok(cert, 'mail.google.com')

        # No DNS entry subjectAltName oraz no commonName
        cert = {'notAfter': 'Dec 18 23:59:59 2099 GMT',
                'subject': ((('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'Mountain View'),),
                            (('organizationName', 'Google Inc'),)),
                'subjectAltName': (('othername', 'blabla'),)}
        fail(cert, 'google.com')

        # Empty cert / no cert
        self.assertRaises(ValueError, ssl.match_hostname, Nic, 'example.com')
        self.assertRaises(ValueError, ssl.match_hostname, {}, 'example.com')

        # Issue #17980: avoid denials of service by refusing more than one
        # wildcard per fragment.
        cert = {'subject': ((('commonName', 'a*b.com'),),)}
        ok(cert, 'axxb.com')
        cert = {'subject': ((('commonName', 'a*b.co*'),),)}
        fail(cert, 'axxb.com')
        cert = {'subject': ((('commonName', 'a*b*.com'),),)}
        przy self.assertRaises(ssl.CertificateError) jako cm:
            ssl.match_hostname(cert, 'axxbxxc.com')
        self.assertIn("too many wildcards", str(cm.exception))

    def test_server_side(self):
        # server_hostname doesn't work dla server sockets
        ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        przy socket.socket() jako sock:
            self.assertRaises(ValueError, ctx.wrap_socket, sock, Prawda,
                              server_hostname="some.hostname")

    def test_unknown_channel_binding(self):
        # should podnieś ValueError dla unknown type
        s = socket.socket(socket.AF_INET)
        s.bind(('127.0.0.1', 0))
        s.listen()
        c = socket.socket(socket.AF_INET)
        c.connect(s.getsockname())
        przy ssl.wrap_socket(c, do_handshake_on_connect=Nieprawda) jako ss:
            przy self.assertRaises(ValueError):
                ss.get_channel_binding("unknown-type")
        s.close()

    @unittest.skipUnless("tls-unique" w ssl.CHANNEL_BINDING_TYPES,
                         "'tls-unique' channel binding nie available")
    def test_tls_unique_channel_binding(self):
        # unconnected should zwróć Nic dla known type
        s = socket.socket(socket.AF_INET)
        przy ssl.wrap_socket(s) jako ss:
            self.assertIsNic(ss.get_channel_binding("tls-unique"))
        # the same dla server-side
        s = socket.socket(socket.AF_INET)
        przy ssl.wrap_socket(s, server_side=Prawda, certfile=CERTFILE) jako ss:
            self.assertIsNic(ss.get_channel_binding("tls-unique"))

    def test_dealloc_warn(self):
        ss = ssl.wrap_socket(socket.socket(socket.AF_INET))
        r = repr(ss)
        przy self.assertWarns(ResourceWarning) jako cm:
            ss = Nic
            support.gc_collect()
        self.assertIn(r, str(cm.warning.args[0]))

    def test_get_default_verify_paths(self):
        paths = ssl.get_default_verify_paths()
        self.assertEqual(len(paths), 6)
        self.assertIsInstance(paths, ssl.DefaultVerifyPaths)

        przy support.EnvironmentVarGuard() jako env:
            env["SSL_CERT_DIR"] = CAPATH
            env["SSL_CERT_FILE"] = CERTFILE
            paths = ssl.get_default_verify_paths()
            self.assertEqual(paths.cafile, CERTFILE)
            self.assertEqual(paths.capath, CAPATH)

    @unittest.skipUnless(sys.platform == "win32", "Windows specific")
    def test_enum_certificates(self):
        self.assertPrawda(ssl.enum_certificates("CA"))
        self.assertPrawda(ssl.enum_certificates("ROOT"))

        self.assertRaises(TypeError, ssl.enum_certificates)
        self.assertRaises(WindowsError, ssl.enum_certificates, "")

        trust_oids = set()
        dla storename w ("CA", "ROOT"):
            store = ssl.enum_certificates(storename)
            self.assertIsInstance(store, list)
            dla element w store:
                self.assertIsInstance(element, tuple)
                self.assertEqual(len(element), 3)
                cert, enc, trust = element
                self.assertIsInstance(cert, bytes)
                self.assertIn(enc, {"x509_asn", "pkcs_7_asn"})
                self.assertIsInstance(trust, (set, bool))
                jeżeli isinstance(trust, set):
                    trust_oids.update(trust)

        serverAuth = "1.3.6.1.5.5.7.3.1"
        self.assertIn(serverAuth, trust_oids)

    @unittest.skipUnless(sys.platform == "win32", "Windows specific")
    def test_enum_crls(self):
        self.assertPrawda(ssl.enum_crls("CA"))
        self.assertRaises(TypeError, ssl.enum_crls)
        self.assertRaises(WindowsError, ssl.enum_crls, "")

        crls = ssl.enum_crls("CA")
        self.assertIsInstance(crls, list)
        dla element w crls:
            self.assertIsInstance(element, tuple)
            self.assertEqual(len(element), 2)
            self.assertIsInstance(element[0], bytes)
            self.assertIn(element[1], {"x509_asn", "pkcs_7_asn"})


    def test_asn1object(self):
        expected = (129, 'serverAuth', 'TLS Web Server Authentication',
                    '1.3.6.1.5.5.7.3.1')

        val = ssl._ASN1Object('1.3.6.1.5.5.7.3.1')
        self.assertEqual(val, expected)
        self.assertEqual(val.nid, 129)
        self.assertEqual(val.shortname, 'serverAuth')
        self.assertEqual(val.longname, 'TLS Web Server Authentication')
        self.assertEqual(val.oid, '1.3.6.1.5.5.7.3.1')
        self.assertIsInstance(val, ssl._ASN1Object)
        self.assertRaises(ValueError, ssl._ASN1Object, 'serverAuth')

        val = ssl._ASN1Object.fromnid(129)
        self.assertEqual(val, expected)
        self.assertIsInstance(val, ssl._ASN1Object)
        self.assertRaises(ValueError, ssl._ASN1Object.fromnid, -1)
        przy self.assertRaisesRegex(ValueError, "unknown NID 100000"):
            ssl._ASN1Object.fromnid(100000)
        dla i w range(1000):
            spróbuj:
                obj = ssl._ASN1Object.fromnid(i)
            wyjąwszy ValueError:
                dalej
            inaczej:
                self.assertIsInstance(obj.nid, int)
                self.assertIsInstance(obj.shortname, str)
                self.assertIsInstance(obj.longname, str)
                self.assertIsInstance(obj.oid, (str, type(Nic)))

        val = ssl._ASN1Object.fromname('TLS Web Server Authentication')
        self.assertEqual(val, expected)
        self.assertIsInstance(val, ssl._ASN1Object)
        self.assertEqual(ssl._ASN1Object.fromname('serverAuth'), expected)
        self.assertEqual(ssl._ASN1Object.fromname('1.3.6.1.5.5.7.3.1'),
                         expected)
        przy self.assertRaisesRegex(ValueError, "unknown object 'serverauth'"):
            ssl._ASN1Object.fromname('serverauth')

    def test_purpose_enum(self):
        val = ssl._ASN1Object('1.3.6.1.5.5.7.3.1')
        self.assertIsInstance(ssl.Purpose.SERVER_AUTH, ssl._ASN1Object)
        self.assertEqual(ssl.Purpose.SERVER_AUTH, val)
        self.assertEqual(ssl.Purpose.SERVER_AUTH.nid, 129)
        self.assertEqual(ssl.Purpose.SERVER_AUTH.shortname, 'serverAuth')
        self.assertEqual(ssl.Purpose.SERVER_AUTH.oid,
                              '1.3.6.1.5.5.7.3.1')

        val = ssl._ASN1Object('1.3.6.1.5.5.7.3.2')
        self.assertIsInstance(ssl.Purpose.CLIENT_AUTH, ssl._ASN1Object)
        self.assertEqual(ssl.Purpose.CLIENT_AUTH, val)
        self.assertEqual(ssl.Purpose.CLIENT_AUTH.nid, 130)
        self.assertEqual(ssl.Purpose.CLIENT_AUTH.shortname, 'clientAuth')
        self.assertEqual(ssl.Purpose.CLIENT_AUTH.oid,
                              '1.3.6.1.5.5.7.3.2')

    def test_unsupported_dtls(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(s.close)
        przy self.assertRaises(NotImplementedError) jako cx:
            ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)
        self.assertEqual(str(cx.exception), "only stream sockets are supported")
        ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        przy self.assertRaises(NotImplementedError) jako cx:
            ctx.wrap_socket(s)
        self.assertEqual(str(cx.exception), "only stream sockets are supported")

    def cert_time_ok(self, timestring, timestamp):
        self.assertEqual(ssl.cert_time_to_seconds(timestring), timestamp)

    def cert_time_fail(self, timestring):
        przy self.assertRaises(ValueError):
            ssl.cert_time_to_seconds(timestring)

    @unittest.skipUnless(utc_offset(),
                         'local time needs to be different z UTC')
    def test_cert_time_to_seconds_timezone(self):
        # Issue #19940: ssl.cert_time_to_seconds() returns wrong
        #               results jeżeli local timezone jest nie UTC
        self.cert_time_ok("May  9 00:00:00 2007 GMT", 1178668800.0)
        self.cert_time_ok("Jan  5 09:34:43 2018 GMT", 1515144883.0)

    def test_cert_time_to_seconds(self):
        timestring = "Jan  5 09:34:43 2018 GMT"
        ts = 1515144883.0
        self.cert_time_ok(timestring, ts)
        # accept keyword parameter, assert its name
        self.assertEqual(ssl.cert_time_to_seconds(cert_time=timestring), ts)
        # accept both %e oraz %d (space albo zero generated by strftime)
        self.cert_time_ok("Jan 05 09:34:43 2018 GMT", ts)
        # case-insensitive
        self.cert_time_ok("JaN  5 09:34:43 2018 GmT", ts)
        self.cert_time_fail("Jan  5 09:34 2018 GMT")     # no seconds
        self.cert_time_fail("Jan  5 09:34:43 2018")      # no GMT
        self.cert_time_fail("Jan  5 09:34:43 2018 UTC")  # nie GMT timezone
        self.cert_time_fail("Jan 35 09:34:43 2018 GMT")  # invalid day
        self.cert_time_fail("Jon  5 09:34:43 2018 GMT")  # invalid month
        self.cert_time_fail("Jan  5 24:00:00 2018 GMT")  # invalid hour
        self.cert_time_fail("Jan  5 09:60:43 2018 GMT")  # invalid minute

        newyear_ts = 1230768000.0
        # leap seconds
        self.cert_time_ok("Dec 31 23:59:60 2008 GMT", newyear_ts)
        # same timestamp
        self.cert_time_ok("Jan  1 00:00:00 2009 GMT", newyear_ts)

        self.cert_time_ok("Jan  5 09:34:59 2018 GMT", 1515144899)
        #  allow 60th second (even jeżeli it jest nie a leap second)
        self.cert_time_ok("Jan  5 09:34:60 2018 GMT", 1515144900)
        #  allow 2nd leap second dla compatibility przy time.strptime()
        self.cert_time_ok("Jan  5 09:34:61 2018 GMT", 1515144901)
        self.cert_time_fail("Jan  5 09:34:62 2018 GMT")  # invalid seconds

        # no special treatement dla the special value:
        #   99991231235959Z (rfc 5280)
        self.cert_time_ok("Dec 31 23:59:59 9999 GMT", 253402300799.0)

    @support.run_with_locale('LC_ALL', '')
    def test_cert_time_to_seconds_locale(self):
        # `cert_time_to_seconds()` should be locale independent

        def local_february_name():
            zwróć time.strftime('%b', (1, 2, 3, 4, 5, 6, 0, 0, 0))

        jeżeli local_february_name().lower() == 'feb':
            self.skipTest("locale-specific month name needs to be "
                          "different z C locale")

        # locale-independent
        self.cert_time_ok("Feb  9 00:00:00 2007 GMT", 1170979200.0)
        self.cert_time_fail(local_february_name() + "  9 00:00:00 2007 GMT")


klasa ContextTests(unittest.TestCase):

    @skip_if_broken_ubuntu_ssl
    def test_constructor(self):
        dla protocol w PROTOCOLS:
            ssl.SSLContext(protocol)
        self.assertRaises(TypeError, ssl.SSLContext)
        self.assertRaises(ValueError, ssl.SSLContext, -1)
        self.assertRaises(ValueError, ssl.SSLContext, 42)

    @skip_if_broken_ubuntu_ssl
    def test_protocol(self):
        dla proto w PROTOCOLS:
            ctx = ssl.SSLContext(proto)
            self.assertEqual(ctx.protocol, proto)

    def test_ciphers(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.set_ciphers("ALL")
        ctx.set_ciphers("DEFAULT")
        przy self.assertRaisesRegex(ssl.SSLError, "No cipher can be selected"):
            ctx.set_ciphers("^$:,;?*'dorothyx")

    @skip_if_broken_ubuntu_ssl
    def test_options(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        # OP_ALL | OP_NO_SSLv2 jest the default value
        self.assertEqual(ssl.OP_ALL | ssl.OP_NO_SSLv2,
                         ctx.options)
        ctx.options |= ssl.OP_NO_SSLv3
        self.assertEqual(ssl.OP_ALL | ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3,
                         ctx.options)
        jeżeli can_clear_options():
            ctx.options = (ctx.options & ~ssl.OP_NO_SSLv2) | ssl.OP_NO_TLSv1
            self.assertEqual(ssl.OP_ALL | ssl.OP_NO_TLSv1 | ssl.OP_NO_SSLv3,
                             ctx.options)
            ctx.options = 0
            self.assertEqual(0, ctx.options)
        inaczej:
            przy self.assertRaises(ValueError):
                ctx.options = 0

    def test_verify_mode(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        # Default value
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        ctx.verify_mode = ssl.CERT_OPTIONAL
        self.assertEqual(ctx.verify_mode, ssl.CERT_OPTIONAL)
        ctx.verify_mode = ssl.CERT_REQUIRED
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        ctx.verify_mode = ssl.CERT_NONE
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        przy self.assertRaises(TypeError):
            ctx.verify_mode = Nic
        przy self.assertRaises(ValueError):
            ctx.verify_mode = 42

    @unittest.skipUnless(have_verify_flags(),
                         "verify_flags need OpenSSL > 0.9.8")
    def test_verify_flags(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        # default value
        tf = getattr(ssl, "VERIFY_X509_TRUSTED_FIRST", 0)
        self.assertEqual(ctx.verify_flags, ssl.VERIFY_DEFAULT | tf)
        ctx.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF
        self.assertEqual(ctx.verify_flags, ssl.VERIFY_CRL_CHECK_LEAF)
        ctx.verify_flags = ssl.VERIFY_CRL_CHECK_CHAIN
        self.assertEqual(ctx.verify_flags, ssl.VERIFY_CRL_CHECK_CHAIN)
        ctx.verify_flags = ssl.VERIFY_DEFAULT
        self.assertEqual(ctx.verify_flags, ssl.VERIFY_DEFAULT)
        # supports any value
        ctx.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF | ssl.VERIFY_X509_STRICT
        self.assertEqual(ctx.verify_flags,
                         ssl.VERIFY_CRL_CHECK_LEAF | ssl.VERIFY_X509_STRICT)
        przy self.assertRaises(TypeError):
            ctx.verify_flags = Nic

    def test_load_cert_chain(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        # Combined key oraz cert w a single file
        ctx.load_cert_chain(CERTFILE, keyfile=Nic)
        ctx.load_cert_chain(CERTFILE, keyfile=CERTFILE)
        self.assertRaises(TypeError, ctx.load_cert_chain, keyfile=CERTFILE)
        przy self.assertRaises(OSError) jako cm:
            ctx.load_cert_chain(WRONGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        przy self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(BADCERT)
        przy self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(EMPTYCERT)
        # Separate key oraz cert
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.load_cert_chain(ONLYCERT, ONLYKEY)
        ctx.load_cert_chain(certfile=ONLYCERT, keyfile=ONLYKEY)
        ctx.load_cert_chain(certfile=BYTES_ONLYCERT, keyfile=BYTES_ONLYKEY)
        przy self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(ONLYCERT)
        przy self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(ONLYKEY)
        przy self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(certfile=ONLYKEY, keyfile=ONLYCERT)
        # Mismatching key oraz cert
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        przy self.assertRaisesRegex(ssl.SSLError, "key values mismatch"):
            ctx.load_cert_chain(SVN_PYTHON_ORG_ROOT_CERT, ONLYKEY)
        # Password protected key oraz cert
        ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=KEY_PASSWORD)
        ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=KEY_PASSWORD.encode())
        ctx.load_cert_chain(CERTFILE_PROTECTED,
                            dalejword=bytearray(KEY_PASSWORD.encode()))
        ctx.load_cert_chain(ONLYCERT, ONLYKEY_PROTECTED, KEY_PASSWORD)
        ctx.load_cert_chain(ONLYCERT, ONLYKEY_PROTECTED, KEY_PASSWORD.encode())
        ctx.load_cert_chain(ONLYCERT, ONLYKEY_PROTECTED,
                            bytearray(KEY_PASSWORD.encode()))
        przy self.assertRaisesRegex(TypeError, "should be a string"):
            ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=Prawda)
        przy self.assertRaises(ssl.SSLError):
            ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword="badpass")
        przy self.assertRaisesRegex(ValueError, "cannot be longer"):
            # openssl has a fixed limit on the dalejword buffer.
            # PEM_BUFSIZE jest generally set to 1kb.
            # Return a string larger than this.
            ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=b'a' * 102400)
        # Password callback
        def getpass_unicode():
            zwróć KEY_PASSWORD
        def getpass_bytes():
            zwróć KEY_PASSWORD.encode()
        def getpass_bytearray():
            zwróć bytearray(KEY_PASSWORD.encode())
        def getpass_badpass():
            zwróć "badpass"
        def getpass_huge():
            zwróć b'a' * (1024 * 1024)
        def getpass_bad_type():
            zwróć 9
        def getpass_exception():
            podnieś Exception('getpass error')
        klasa GetPassCallable:
            def __call__(self):
                zwróć KEY_PASSWORD
            def getpass(self):
                zwróć KEY_PASSWORD
        ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=getpass_unicode)
        ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=getpass_bytes)
        ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=getpass_bytearray)
        ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=GetPassCallable())
        ctx.load_cert_chain(CERTFILE_PROTECTED,
                            dalejword=GetPassCallable().getpass)
        przy self.assertRaises(ssl.SSLError):
            ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=getpass_badpass)
        przy self.assertRaisesRegex(ValueError, "cannot be longer"):
            ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=getpass_huge)
        przy self.assertRaisesRegex(TypeError, "must zwróć a string"):
            ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=getpass_bad_type)
        przy self.assertRaisesRegex(Exception, "getpass error"):
            ctx.load_cert_chain(CERTFILE_PROTECTED, dalejword=getpass_exception)
        # Make sure the dalejword function isn't called jeżeli it isn't needed
        ctx.load_cert_chain(CERTFILE, dalejword=getpass_exception)

    def test_load_verify_locations(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.load_verify_locations(CERTFILE)
        ctx.load_verify_locations(cafile=CERTFILE, capath=Nic)
        ctx.load_verify_locations(BYTES_CERTFILE)
        ctx.load_verify_locations(cafile=BYTES_CERTFILE, capath=Nic)
        self.assertRaises(TypeError, ctx.load_verify_locations)
        self.assertRaises(TypeError, ctx.load_verify_locations, Nic, Nic, Nic)
        przy self.assertRaises(OSError) jako cm:
            ctx.load_verify_locations(WRONGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        przy self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_verify_locations(BADCERT)
        ctx.load_verify_locations(CERTFILE, CAPATH)
        ctx.load_verify_locations(CERTFILE, capath=BYTES_CAPATH)

        # Issue #10989: crash jeżeli the second argument type jest invalid
        self.assertRaises(TypeError, ctx.load_verify_locations, Nic, Prawda)

    def test_load_verify_cadata(self):
        # test cadata
        przy open(CAFILE_CACERT) jako f:
            cacert_pem = f.read()
        cacert_der = ssl.PEM_cert_to_DER_cert(cacert_pem)
        przy open(CAFILE_NEURONIO) jako f:
            neuronio_pem = f.read()
        neuronio_der = ssl.PEM_cert_to_DER_cert(neuronio_pem)

        # test PEM
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 0)
        ctx.load_verify_locations(cadata=cacert_pem)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 1)
        ctx.load_verify_locations(cadata=neuronio_pem)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)
        # cert already w hash table
        ctx.load_verify_locations(cadata=neuronio_pem)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # combined
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        combined = "\n".join((cacert_pem, neuronio_pem))
        ctx.load_verify_locations(cadata=combined)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # przy junk around the certs
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        combined = ["head", cacert_pem, "other", neuronio_pem, "again",
                    neuronio_pem, "tail"]
        ctx.load_verify_locations(cadata="\n".join(combined))
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # test DER
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.load_verify_locations(cadata=cacert_der)
        ctx.load_verify_locations(cadata=neuronio_der)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)
        # cert already w hash table
        ctx.load_verify_locations(cadata=cacert_der)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # combined
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        combined = b"".join((cacert_der, neuronio_der))
        ctx.load_verify_locations(cadata=combined)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # error cases
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.assertRaises(TypeError, ctx.load_verify_locations, cadata=object)

        przy self.assertRaisesRegex(ssl.SSLError, "no start line"):
            ctx.load_verify_locations(cadata="broken")
        przy self.assertRaisesRegex(ssl.SSLError, "not enough data"):
            ctx.load_verify_locations(cadata=b"broken")


    def test_load_dh_params(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.load_dh_params(DHFILE)
        jeżeli os.name != 'nt':
            ctx.load_dh_params(BYTES_DHFILE)
        self.assertRaises(TypeError, ctx.load_dh_params)
        self.assertRaises(TypeError, ctx.load_dh_params, Nic)
        przy self.assertRaises(FileNotFoundError) jako cm:
            ctx.load_dh_params(WRONGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        przy self.assertRaises(ssl.SSLError) jako cm:
            ctx.load_dh_params(CERTFILE)

    @skip_if_broken_ubuntu_ssl
    def test_session_stats(self):
        dla proto w PROTOCOLS:
            ctx = ssl.SSLContext(proto)
            self.assertEqual(ctx.session_stats(), {
                'number': 0,
                'connect': 0,
                'connect_good': 0,
                'connect_renegotiate': 0,
                'accept': 0,
                'accept_good': 0,
                'accept_renegotiate': 0,
                'hits': 0,
                'misses': 0,
                'timeouts': 0,
                'cache_full': 0,
            })

    def test_set_default_verify_paths(self):
        # There's nie much we can do to test that it acts jako expected,
        # so just check it doesn't crash albo podnieś an exception.
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.set_default_verify_paths()

    @unittest.skipUnless(ssl.HAS_ECDH, "ECDH disabled on this OpenSSL build")
    def test_set_ecdh_curve(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.set_ecdh_curve("prime256v1")
        ctx.set_ecdh_curve(b"prime256v1")
        self.assertRaises(TypeError, ctx.set_ecdh_curve)
        self.assertRaises(TypeError, ctx.set_ecdh_curve, Nic)
        self.assertRaises(ValueError, ctx.set_ecdh_curve, "foo")
        self.assertRaises(ValueError, ctx.set_ecdh_curve, b"foo")

    @needs_sni
    def test_sni_callback(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

        # set_servername_callback expects a callable, albo Nic
        self.assertRaises(TypeError, ctx.set_servername_callback)
        self.assertRaises(TypeError, ctx.set_servername_callback, 4)
        self.assertRaises(TypeError, ctx.set_servername_callback, "")
        self.assertRaises(TypeError, ctx.set_servername_callback, ctx)

        def dummycallback(sock, servername, ctx):
            dalej
        ctx.set_servername_callback(Nic)
        ctx.set_servername_callback(dummycallback)

    @needs_sni
    def test_sni_callback_refcycle(self):
        # Reference cycles through the servername callback are detected
        # oraz cleared.
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        def dummycallback(sock, servername, ctx, cycle=ctx):
            dalej
        ctx.set_servername_callback(dummycallback)
        wr = weakref.ref(ctx)
        usuń ctx, dummycallback
        gc.collect()
        self.assertIs(wr(), Nic)

    def test_cert_store_stats(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.assertEqual(ctx.cert_store_stats(),
            {'x509_ca': 0, 'crl': 0, 'x509': 0})
        ctx.load_cert_chain(CERTFILE)
        self.assertEqual(ctx.cert_store_stats(),
            {'x509_ca': 0, 'crl': 0, 'x509': 0})
        ctx.load_verify_locations(CERTFILE)
        self.assertEqual(ctx.cert_store_stats(),
            {'x509_ca': 0, 'crl': 0, 'x509': 1})
        ctx.load_verify_locations(SVN_PYTHON_ORG_ROOT_CERT)
        self.assertEqual(ctx.cert_store_stats(),
            {'x509_ca': 1, 'crl': 0, 'x509': 2})

    def test_get_ca_certs(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.assertEqual(ctx.get_ca_certs(), [])
        # CERTFILE jest nie flagged jako X509v3 Basic Constraints: CA:TRUE
        ctx.load_verify_locations(CERTFILE)
        self.assertEqual(ctx.get_ca_certs(), [])
        # but SVN_PYTHON_ORG_ROOT_CERT jest a CA cert
        ctx.load_verify_locations(SVN_PYTHON_ORG_ROOT_CERT)
        self.assertEqual(ctx.get_ca_certs(),
            [{'issuer': ((('organizationName', 'Root CA'),),
                         (('organizationalUnitName', 'http://www.cacert.org'),),
                         (('commonName', 'CA Cert Signing Authority'),),
                         (('emailAddress', 'support@cacert.org'),)),
              'notAfter': asn1time('Mar 29 12:29:49 2033 GMT'),
              'notBefore': asn1time('Mar 30 12:29:49 2003 GMT'),
              'serialNumber': '00',
              'crlDistributionPoints': ('https://www.cacert.org/revoke.crl',),
              'subject': ((('organizationName', 'Root CA'),),
                          (('organizationalUnitName', 'http://www.cacert.org'),),
                          (('commonName', 'CA Cert Signing Authority'),),
                          (('emailAddress', 'support@cacert.org'),)),
              'version': 3}])

        przy open(SVN_PYTHON_ORG_ROOT_CERT) jako f:
            pem = f.read()
        der = ssl.PEM_cert_to_DER_cert(pem)
        self.assertEqual(ctx.get_ca_certs(Prawda), [der])

    def test_load_default_certs(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.load_default_certs()

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.load_default_certs(ssl.Purpose.SERVER_AUTH)
        ctx.load_default_certs()

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.load_default_certs(ssl.Purpose.CLIENT_AUTH)

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.assertRaises(TypeError, ctx.load_default_certs, Nic)
        self.assertRaises(TypeError, ctx.load_default_certs, 'SERVER_AUTH')

    @unittest.skipIf(sys.platform == "win32", "not-Windows specific")
    def test_load_default_certs_env(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        przy support.EnvironmentVarGuard() jako env:
            env["SSL_CERT_DIR"] = CAPATH
            env["SSL_CERT_FILE"] = CERTFILE
            ctx.load_default_certs()
            self.assertEqual(ctx.cert_store_stats(), {"crl": 0, "x509": 1, "x509_ca": 0})

    @unittest.skipUnless(sys.platform == "win32", "Windows specific")
    def test_load_default_certs_env_windows(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx.load_default_certs()
        stats = ctx.cert_store_stats()

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        przy support.EnvironmentVarGuard() jako env:
            env["SSL_CERT_DIR"] = CAPATH
            env["SSL_CERT_FILE"] = CERTFILE
            ctx.load_default_certs()
            stats["x509"] += 1
            self.assertEqual(ctx.cert_store_stats(), stats)

    def test_create_default_context(self):
        ctx = ssl.create_default_context()
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_SSLv23)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertPrawda(ctx.check_hostname)
        self.assertEqual(ctx.options & ssl.OP_NO_SSLv2, ssl.OP_NO_SSLv2)
        self.assertEqual(
            ctx.options & getattr(ssl, "OP_NO_COMPRESSION", 0),
            getattr(ssl, "OP_NO_COMPRESSION", 0),
        )

        przy open(SIGNING_CA) jako f:
            cadata = f.read()
        ctx = ssl.create_default_context(cafile=SIGNING_CA, capath=CAPATH,
                                         cadata=cadata)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_SSLv23)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertEqual(ctx.options & ssl.OP_NO_SSLv2, ssl.OP_NO_SSLv2)
        self.assertEqual(
            ctx.options & getattr(ssl, "OP_NO_COMPRESSION", 0),
            getattr(ssl, "OP_NO_COMPRESSION", 0),
        )

        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_SSLv23)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        self.assertEqual(ctx.options & ssl.OP_NO_SSLv2, ssl.OP_NO_SSLv2)
        self.assertEqual(
            ctx.options & getattr(ssl, "OP_NO_COMPRESSION", 0),
            getattr(ssl, "OP_NO_COMPRESSION", 0),
        )
        self.assertEqual(
            ctx.options & getattr(ssl, "OP_SINGLE_DH_USE", 0),
            getattr(ssl, "OP_SINGLE_DH_USE", 0),
        )
        self.assertEqual(
            ctx.options & getattr(ssl, "OP_SINGLE_ECDH_USE", 0),
            getattr(ssl, "OP_SINGLE_ECDH_USE", 0),
        )

    def test__create_stdlib_context(self):
        ctx = ssl._create_stdlib_context()
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_SSLv23)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        self.assertNieprawda(ctx.check_hostname)
        self.assertEqual(ctx.options & ssl.OP_NO_SSLv2, ssl.OP_NO_SSLv2)

        ctx = ssl._create_stdlib_context(ssl.PROTOCOL_TLSv1)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLSv1)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        self.assertEqual(ctx.options & ssl.OP_NO_SSLv2, ssl.OP_NO_SSLv2)

        ctx = ssl._create_stdlib_context(ssl.PROTOCOL_TLSv1,
                                         cert_reqs=ssl.CERT_REQUIRED,
                                         check_hostname=Prawda)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLSv1)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertPrawda(ctx.check_hostname)
        self.assertEqual(ctx.options & ssl.OP_NO_SSLv2, ssl.OP_NO_SSLv2)

        ctx = ssl._create_stdlib_context(purpose=ssl.Purpose.CLIENT_AUTH)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_SSLv23)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        self.assertEqual(ctx.options & ssl.OP_NO_SSLv2, ssl.OP_NO_SSLv2)

    def test_check_hostname(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.assertNieprawda(ctx.check_hostname)

        # Requires CERT_REQUIRED albo CERT_OPTIONAL
        przy self.assertRaises(ValueError):
            ctx.check_hostname = Prawda
        ctx.verify_mode = ssl.CERT_REQUIRED
        self.assertNieprawda(ctx.check_hostname)
        ctx.check_hostname = Prawda
        self.assertPrawda(ctx.check_hostname)

        ctx.verify_mode = ssl.CERT_OPTIONAL
        ctx.check_hostname = Prawda
        self.assertPrawda(ctx.check_hostname)

        # Cannot set CERT_NONE przy check_hostname enabled
        przy self.assertRaises(ValueError):
            ctx.verify_mode = ssl.CERT_NONE
        ctx.check_hostname = Nieprawda
        self.assertNieprawda(ctx.check_hostname)


klasa SSLErrorTests(unittest.TestCase):

    def test_str(self):
        # The str() of a SSLError doesn't include the errno
        e = ssl.SSLError(1, "foo")
        self.assertEqual(str(e), "foo")
        self.assertEqual(e.errno, 1)
        # Same dla a subclass
        e = ssl.SSLZeroReturnError(1, "foo")
        self.assertEqual(str(e), "foo")
        self.assertEqual(e.errno, 1)

    def test_lib_reason(self):
        # Test the library oraz reason attributes
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        przy self.assertRaises(ssl.SSLError) jako cm:
            ctx.load_dh_params(CERTFILE)
        self.assertEqual(cm.exception.library, 'PEM')
        self.assertEqual(cm.exception.reason, 'NO_START_LINE')
        s = str(cm.exception)
        self.assertPrawda(s.startswith("[PEM: NO_START_LINE] no start line"), s)

    def test_subclass(self):
        # Check that the appropriate SSLError subclass jest podnieśd
        # (this only tests one of them)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        przy socket.socket() jako s:
            s.bind(("127.0.0.1", 0))
            s.listen()
            c = socket.socket()
            c.connect(s.getsockname())
            c.setblocking(Nieprawda)
            przy ctx.wrap_socket(c, Nieprawda, do_handshake_on_connect=Nieprawda) jako c:
                przy self.assertRaises(ssl.SSLWantReadError) jako cm:
                    c.do_handshake()
                s = str(cm.exception)
                self.assertPrawda(s.startswith("The operation did nie complete (read)"), s)
                # For compatibility
                self.assertEqual(cm.exception.errno, ssl.SSL_ERROR_WANT_READ)


klasa MemoryBIOTests(unittest.TestCase):

    def test_read_write(self):
        bio = ssl.MemoryBIO()
        bio.write(b'foo')
        self.assertEqual(bio.read(), b'foo')
        self.assertEqual(bio.read(), b'')
        bio.write(b'foo')
        bio.write(b'bar')
        self.assertEqual(bio.read(), b'foobar')
        self.assertEqual(bio.read(), b'')
        bio.write(b'baz')
        self.assertEqual(bio.read(2), b'ba')
        self.assertEqual(bio.read(1), b'z')
        self.assertEqual(bio.read(1), b'')

    def test_eof(self):
        bio = ssl.MemoryBIO()
        self.assertNieprawda(bio.eof)
        self.assertEqual(bio.read(), b'')
        self.assertNieprawda(bio.eof)
        bio.write(b'foo')
        self.assertNieprawda(bio.eof)
        bio.write_eof()
        self.assertNieprawda(bio.eof)
        self.assertEqual(bio.read(2), b'fo')
        self.assertNieprawda(bio.eof)
        self.assertEqual(bio.read(1), b'o')
        self.assertPrawda(bio.eof)
        self.assertEqual(bio.read(), b'')
        self.assertPrawda(bio.eof)

    def test_pending(self):
        bio = ssl.MemoryBIO()
        self.assertEqual(bio.pending, 0)
        bio.write(b'foo')
        self.assertEqual(bio.pending, 3)
        dla i w range(3):
            bio.read(1)
            self.assertEqual(bio.pending, 3-i-1)
        dla i w range(3):
            bio.write(b'x')
            self.assertEqual(bio.pending, i+1)
        bio.read()
        self.assertEqual(bio.pending, 0)

    def test_buffer_types(self):
        bio = ssl.MemoryBIO()
        bio.write(b'foo')
        self.assertEqual(bio.read(), b'foo')
        bio.write(bytearray(b'bar'))
        self.assertEqual(bio.read(), b'bar')
        bio.write(memoryview(b'baz'))
        self.assertEqual(bio.read(), b'baz')

    def test_error_types(self):
        bio = ssl.MemoryBIO()
        self.assertRaises(TypeError, bio.write, 'foo')
        self.assertRaises(TypeError, bio.write, Nic)
        self.assertRaises(TypeError, bio.write, Prawda)
        self.assertRaises(TypeError, bio.write, 1)


klasa NetworkedTests(unittest.TestCase):

    def test_connect(self):
        przy support.transient_internet("svn.python.org"):
            s = ssl.wrap_socket(socket.socket(socket.AF_INET),
                                cert_reqs=ssl.CERT_NONE)
            spróbuj:
                s.connect(("svn.python.org", 443))
                self.assertEqual({}, s.getpeercert())
            w_końcu:
                s.close()

            # this should fail because we have no verification certs
            s = ssl.wrap_socket(socket.socket(socket.AF_INET),
                                cert_reqs=ssl.CERT_REQUIRED)
            self.assertRaisesRegex(ssl.SSLError, "certificate verify failed",
                                   s.connect, ("svn.python.org", 443))
            s.close()

            # this should succeed because we specify the root cert
            s = ssl.wrap_socket(socket.socket(socket.AF_INET),
                                cert_reqs=ssl.CERT_REQUIRED,
                                ca_certs=SVN_PYTHON_ORG_ROOT_CERT)
            spróbuj:
                s.connect(("svn.python.org", 443))
                self.assertPrawda(s.getpeercert())
            w_końcu:
                s.close()

    def test_connect_ex(self):
        # Issue #11326: check connect_ex() implementation
        przy support.transient_internet("svn.python.org"):
            s = ssl.wrap_socket(socket.socket(socket.AF_INET),
                                cert_reqs=ssl.CERT_REQUIRED,
                                ca_certs=SVN_PYTHON_ORG_ROOT_CERT)
            spróbuj:
                self.assertEqual(0, s.connect_ex(("svn.python.org", 443)))
                self.assertPrawda(s.getpeercert())
            w_końcu:
                s.close()

    def test_non_blocking_connect_ex(self):
        # Issue #11326: non-blocking connect_ex() should allow handshake
        # to proceed after the socket gets ready.
        przy support.transient_internet("svn.python.org"):
            s = ssl.wrap_socket(socket.socket(socket.AF_INET),
                                cert_reqs=ssl.CERT_REQUIRED,
                                ca_certs=SVN_PYTHON_ORG_ROOT_CERT,
                                do_handshake_on_connect=Nieprawda)
            spróbuj:
                s.setblocking(Nieprawda)
                rc = s.connect_ex(('svn.python.org', 443))
                # EWOULDBLOCK under Windows, EINPROGRESS inaczejwhere
                self.assertIn(rc, (0, errno.EINPROGRESS, errno.EWOULDBLOCK))
                # Wait dla connect to finish
                select.select([], [s], [], 5.0)
                # Non-blocking handshake
                dopóki Prawda:
                    spróbuj:
                        s.do_handshake()
                        przerwij
                    wyjąwszy ssl.SSLWantReadError:
                        select.select([s], [], [], 5.0)
                    wyjąwszy ssl.SSLWantWriteError:
                        select.select([], [s], [], 5.0)
                # SSL established
                self.assertPrawda(s.getpeercert())
            w_końcu:
                s.close()

    def test_timeout_connect_ex(self):
        # Issue #12065: on a timeout, connect_ex() should zwróć the original
        # errno (mimicking the behaviour of non-SSL sockets).
        przy support.transient_internet("svn.python.org"):
            s = ssl.wrap_socket(socket.socket(socket.AF_INET),
                                cert_reqs=ssl.CERT_REQUIRED,
                                ca_certs=SVN_PYTHON_ORG_ROOT_CERT,
                                do_handshake_on_connect=Nieprawda)
            spróbuj:
                s.settimeout(0.0000001)
                rc = s.connect_ex(('svn.python.org', 443))
                jeżeli rc == 0:
                    self.skipTest("svn.python.org responded too quickly")
                self.assertIn(rc, (errno.EAGAIN, errno.EWOULDBLOCK))
            w_końcu:
                s.close()

    def test_connect_ex_error(self):
        przy support.transient_internet("svn.python.org"):
            s = ssl.wrap_socket(socket.socket(socket.AF_INET),
                                cert_reqs=ssl.CERT_REQUIRED,
                                ca_certs=SVN_PYTHON_ORG_ROOT_CERT)
            spróbuj:
                rc = s.connect_ex(("svn.python.org", 444))
                # Issue #19919: Windows machines albo VMs hosted on Windows
                # machines sometimes zwróć EWOULDBLOCK.
                self.assertIn(rc, (errno.ECONNREFUSED, errno.EWOULDBLOCK))
            w_końcu:
                s.close()

    def test_connect_with_context(self):
        przy support.transient_internet("svn.python.org"):
            # Same jako test_connect, but przy a separately created context
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            s = ctx.wrap_socket(socket.socket(socket.AF_INET))
            s.connect(("svn.python.org", 443))
            spróbuj:
                self.assertEqual({}, s.getpeercert())
            w_końcu:
                s.close()
            # Same przy a server hostname
            s = ctx.wrap_socket(socket.socket(socket.AF_INET),
                                server_hostname="svn.python.org")
            s.connect(("svn.python.org", 443))
            s.close()
            # This should fail because we have no verification certs
            ctx.verify_mode = ssl.CERT_REQUIRED
            s = ctx.wrap_socket(socket.socket(socket.AF_INET))
            self.assertRaisesRegex(ssl.SSLError, "certificate verify failed",
                                    s.connect, ("svn.python.org", 443))
            s.close()
            # This should succeed because we specify the root cert
            ctx.load_verify_locations(SVN_PYTHON_ORG_ROOT_CERT)
            s = ctx.wrap_socket(socket.socket(socket.AF_INET))
            s.connect(("svn.python.org", 443))
            spróbuj:
                cert = s.getpeercert()
                self.assertPrawda(cert)
            w_końcu:
                s.close()

    def test_connect_capath(self):
        # Verify server certificates using the `capath` argument
        # NOTE: the subject hashing algorithm has been changed between
        # OpenSSL 0.9.8n oraz 1.0.0, jako a result the capath directory must
        # contain both versions of each certificate (same content, different
        # filename) dla this test to be portable across OpenSSL releases.
        przy support.transient_internet("svn.python.org"):
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(capath=CAPATH)
            s = ctx.wrap_socket(socket.socket(socket.AF_INET))
            s.connect(("svn.python.org", 443))
            spróbuj:
                cert = s.getpeercert()
                self.assertPrawda(cert)
            w_końcu:
                s.close()
            # Same przy a bytes `capath` argument
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(capath=BYTES_CAPATH)
            s = ctx.wrap_socket(socket.socket(socket.AF_INET))
            s.connect(("svn.python.org", 443))
            spróbuj:
                cert = s.getpeercert()
                self.assertPrawda(cert)
            w_końcu:
                s.close()

    def test_connect_cadata(self):
        przy open(CAFILE_CACERT) jako f:
            pem = f.read()
        der = ssl.PEM_cert_to_DER_cert(pem)
        przy support.transient_internet("svn.python.org"):
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(cadata=pem)
            przy ctx.wrap_socket(socket.socket(socket.AF_INET)) jako s:
                s.connect(("svn.python.org", 443))
                cert = s.getpeercert()
                self.assertPrawda(cert)

            # same przy DER
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(cadata=der)
            przy ctx.wrap_socket(socket.socket(socket.AF_INET)) jako s:
                s.connect(("svn.python.org", 443))
                cert = s.getpeercert()
                self.assertPrawda(cert)

    @unittest.skipIf(os.name == "nt", "Can't use a socket jako a file under Windows")
    def test_makefile_close(self):
        # Issue #5238: creating a file-like object przy makefile() shouldn't
        # delay closing the underlying "real socket" (here tested przy its
        # file descriptor, hence skipping the test under Windows).
        przy support.transient_internet("svn.python.org"):
            ss = ssl.wrap_socket(socket.socket(socket.AF_INET))
            ss.connect(("svn.python.org", 443))
            fd = ss.fileno()
            f = ss.makefile()
            f.close()
            # The fd jest still open
            os.read(fd, 0)
            # Closing the SSL socket should close the fd too
            ss.close()
            gc.collect()
            przy self.assertRaises(OSError) jako e:
                os.read(fd, 0)
            self.assertEqual(e.exception.errno, errno.EBADF)

    def test_non_blocking_handshake(self):
        przy support.transient_internet("svn.python.org"):
            s = socket.socket(socket.AF_INET)
            s.connect(("svn.python.org", 443))
            s.setblocking(Nieprawda)
            s = ssl.wrap_socket(s,
                                cert_reqs=ssl.CERT_NONE,
                                do_handshake_on_connect=Nieprawda)
            count = 0
            dopóki Prawda:
                spróbuj:
                    count += 1
                    s.do_handshake()
                    przerwij
                wyjąwszy ssl.SSLWantReadError:
                    select.select([s], [], [])
                wyjąwszy ssl.SSLWantWriteError:
                    select.select([], [s], [])
            s.close()
            jeżeli support.verbose:
                sys.stdout.write("\nNeeded %d calls to do_handshake() to establish session.\n" % count)

    def test_get_server_certificate(self):
        def _test_get_server_certificate(host, port, cert=Nic):
            przy support.transient_internet(host):
                pem = ssl.get_server_certificate((host, port))
                jeżeli nie pem:
                    self.fail("No server certificate on %s:%s!" % (host, port))

                spróbuj:
                    pem = ssl.get_server_certificate((host, port),
                                                     ca_certs=CERTFILE)
                wyjąwszy ssl.SSLError jako x:
                    #should fail
                    jeżeli support.verbose:
                        sys.stdout.write("%s\n" % x)
                inaczej:
                    self.fail("Got server certificate %s dla %s:%s!" % (pem, host, port))

                pem = ssl.get_server_certificate((host, port),
                                                 ca_certs=cert)
                jeżeli nie pem:
                    self.fail("No server certificate on %s:%s!" % (host, port))
                jeżeli support.verbose:
                    sys.stdout.write("\nVerified certificate dla %s:%s is\n%s\n" % (host, port ,pem))

        _test_get_server_certificate('svn.python.org', 443, SVN_PYTHON_ORG_ROOT_CERT)
        jeżeli support.IPV6_ENABLED:
            _test_get_server_certificate('ipv6.google.com', 443)

    def test_ciphers(self):
        remote = ("svn.python.org", 443)
        przy support.transient_internet(remote[0]):
            przy ssl.wrap_socket(socket.socket(socket.AF_INET),
                                 cert_reqs=ssl.CERT_NONE, ciphers="ALL") jako s:
                s.connect(remote)
            przy ssl.wrap_socket(socket.socket(socket.AF_INET),
                                 cert_reqs=ssl.CERT_NONE, ciphers="DEFAULT") jako s:
                s.connect(remote)
            # Error checking can happen at instantiation albo when connecting
            przy self.assertRaisesRegex(ssl.SSLError, "No cipher can be selected"):
                przy socket.socket(socket.AF_INET) jako sock:
                    s = ssl.wrap_socket(sock,
                                        cert_reqs=ssl.CERT_NONE, ciphers="^$:,;?*'dorothyx")
                    s.connect(remote)

    def test_algorithms(self):
        # Issue #8484: all algorithms should be available when verifying a
        # certificate.
        # SHA256 was added w OpenSSL 0.9.8
        jeżeli ssl.OPENSSL_VERSION_INFO < (0, 9, 8, 0, 15):
            self.skipTest("SHA256 nie available on %r" % ssl.OPENSSL_VERSION)
        # sha256.tbs-internet.com needs SNI to use the correct certificate
        jeżeli nie ssl.HAS_SNI:
            self.skipTest("SNI needed dla this test")
        # https://sha2.hboeck.de/ was used until 2011-01-08 (no route to host)
        remote = ("sha256.tbs-internet.com", 443)
        sha256_cert = os.path.join(os.path.dirname(__file__), "sha256.pem")
        przy support.transient_internet("sha256.tbs-internet.com"):
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(sha256_cert)
            s = ctx.wrap_socket(socket.socket(socket.AF_INET),
                                server_hostname="sha256.tbs-internet.com")
            spróbuj:
                s.connect(remote)
                jeżeli support.verbose:
                    sys.stdout.write("\nCipher przy %r jest %r\n" %
                                     (remote, s.cipher()))
                    sys.stdout.write("Certificate is:\n%s\n" %
                                     pprint.pformat(s.getpeercert()))
            w_końcu:
                s.close()

    def test_get_ca_certs_capath(self):
        # capath certs are loaded on request
        przy support.transient_internet("svn.python.org"):
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(capath=CAPATH)
            self.assertEqual(ctx.get_ca_certs(), [])
            s = ctx.wrap_socket(socket.socket(socket.AF_INET))
            s.connect(("svn.python.org", 443))
            spróbuj:
                cert = s.getpeercert()
                self.assertPrawda(cert)
            w_końcu:
                s.close()
            self.assertEqual(len(ctx.get_ca_certs()), 1)

    @needs_sni
    def test_context_setget(self):
        # Check that the context of a connected socket can be replaced.
        przy support.transient_internet("svn.python.org"):
            ctx1 = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            ctx2 = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            s = socket.socket(socket.AF_INET)
            przy ctx1.wrap_socket(s) jako ss:
                ss.connect(("svn.python.org", 443))
                self.assertIs(ss.context, ctx1)
                self.assertIs(ss._sslobj.context, ctx1)
                ss.context = ctx2
                self.assertIs(ss.context, ctx2)
                self.assertIs(ss._sslobj.context, ctx2)


klasa NetworkedBIOTests(unittest.TestCase):

    def ssl_io_loop(self, sock, incoming, outgoing, func, *args, **kwargs):
        # A simple IO loop. Call func(*args) depending on the error we get
        # (WANT_READ albo WANT_WRITE) move data between the socket oraz the BIOs.
        timeout = kwargs.get('timeout', 10)
        count = 0
        dopóki Prawda:
            errno = Nic
            count += 1
            spróbuj:
                ret = func(*args)
            wyjąwszy ssl.SSLError jako e:
                # Note that we get a spurious -1/SSL_ERROR_SYSCALL for
                # non-blocking IO. The SSL_shutdown manpage hints at this.
                # It *should* be safe to just ignore SYS_ERROR_SYSCALL because
                # przy a Memory BIO there's no syscalls (dla IO at least).
                jeżeli e.errno nie w (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE,
                                   ssl.SSL_ERROR_SYSCALL):
                    podnieś
                errno = e.errno
            # Get any data z the outgoing BIO irrespective of any error, oraz
            # send it to the socket.
            buf = outgoing.read()
            sock.sendall(buf)
            # If there's no error, we're done. For WANT_READ, we need to get
            # data z the socket oraz put it w the incoming BIO.
            jeżeli errno jest Nic:
                przerwij
            albo_inaczej errno == ssl.SSL_ERROR_WANT_READ:
                buf = sock.recv(32768)
                jeżeli buf:
                    incoming.write(buf)
                inaczej:
                    incoming.write_eof()
        jeżeli support.verbose:
            sys.stdout.write("Needed %d calls to complete %s().\n"
                             % (count, func.__name__))
        zwróć ret

    def test_handshake(self):
        przy support.transient_internet("svn.python.org"):
            sock = socket.socket(socket.AF_INET)
            sock.connect(("svn.python.org", 443))
            incoming = ssl.MemoryBIO()
            outgoing = ssl.MemoryBIO()
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(SVN_PYTHON_ORG_ROOT_CERT)
            ctx.check_hostname = Prawda
            sslobj = ctx.wrap_bio(incoming, outgoing, Nieprawda, 'svn.python.org')
            self.assertIs(sslobj._sslobj.owner, sslobj)
            self.assertIsNic(sslobj.cipher())
            self.assertIsNic(sslobj.shared_ciphers())
            self.assertRaises(ValueError, sslobj.getpeercert)
            jeżeli 'tls-unique' w ssl.CHANNEL_BINDING_TYPES:
                self.assertIsNic(sslobj.get_channel_binding('tls-unique'))
            self.ssl_io_loop(sock, incoming, outgoing, sslobj.do_handshake)
            self.assertPrawda(sslobj.cipher())
            self.assertIsNic(sslobj.shared_ciphers())
            self.assertPrawda(sslobj.getpeercert())
            jeżeli 'tls-unique' w ssl.CHANNEL_BINDING_TYPES:
                self.assertPrawda(sslobj.get_channel_binding('tls-unique'))
            self.ssl_io_loop(sock, incoming, outgoing, sslobj.unwrap)
            self.assertRaises(ssl.SSLError, sslobj.write, b'foo')
            sock.close()

    def test_read_write_data(self):
        przy support.transient_internet("svn.python.org"):
            sock = socket.socket(socket.AF_INET)
            sock.connect(("svn.python.org", 443))
            incoming = ssl.MemoryBIO()
            outgoing = ssl.MemoryBIO()
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.verify_mode = ssl.CERT_NONE
            sslobj = ctx.wrap_bio(incoming, outgoing, Nieprawda)
            self.ssl_io_loop(sock, incoming, outgoing, sslobj.do_handshake)
            req = b'GET / HTTP/1.0\r\n\r\n'
            self.ssl_io_loop(sock, incoming, outgoing, sslobj.write, req)
            buf = self.ssl_io_loop(sock, incoming, outgoing, sslobj.read, 1024)
            self.assertEqual(buf[:5], b'HTTP/')
            self.ssl_io_loop(sock, incoming, outgoing, sslobj.unwrap)
            sock.close()


spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    _have_threads = Nieprawda
inaczej:
    _have_threads = Prawda

    z test.ssl_servers zaimportuj make_https_server

    klasa ThreadedEchoServer(threading.Thread):

        klasa ConnectionHandler(threading.Thread):

            """A mildly complicated class, because we want it to work both
            przy oraz without the SSL wrapper around the socket connection, so
            that we can test the STARTTLS functionality."""

            def __init__(self, server, connsock, addr):
                self.server = server
                self.running = Nieprawda
                self.sock = connsock
                self.addr = addr
                self.sock.setblocking(1)
                self.sslconn = Nic
                threading.Thread.__init__(self)
                self.daemon = Prawda

            def wrap_conn(self):
                spróbuj:
                    self.sslconn = self.server.context.wrap_socket(
                        self.sock, server_side=Prawda)
                    self.server.selected_npn_protocols.append(self.sslconn.selected_npn_protocol())
                    self.server.selected_alpn_protocols.append(self.sslconn.selected_alpn_protocol())
                wyjąwszy (ssl.SSLError, ConnectionResetError) jako e:
                    # We treat ConnectionResetError jako though it were an
                    # SSLError - OpenSSL on Ubuntu abruptly closes the
                    # connection when asked to use an unsupported protocol.
                    #
                    # XXX Various errors can have happened here, dla example
                    # a mismatching protocol version, an invalid certificate,
                    # albo a low-level bug. This should be made more discriminating.
                    self.server.conn_errors.append(e)
                    jeżeli self.server.chatty:
                        handle_error("\n server:  bad connection attempt z " + repr(self.addr) + ":\n")
                    self.running = Nieprawda
                    self.server.stop()
                    self.close()
                    zwróć Nieprawda
                inaczej:
                    self.server.shared_ciphers.append(self.sslconn.shared_ciphers())
                    jeżeli self.server.context.verify_mode == ssl.CERT_REQUIRED:
                        cert = self.sslconn.getpeercert()
                        jeżeli support.verbose oraz self.server.chatty:
                            sys.stdout.write(" client cert jest " + pprint.pformat(cert) + "\n")
                        cert_binary = self.sslconn.getpeercert(Prawda)
                        jeżeli support.verbose oraz self.server.chatty:
                            sys.stdout.write(" cert binary jest " + str(len(cert_binary)) + " bytes\n")
                    cipher = self.sslconn.cipher()
                    jeżeli support.verbose oraz self.server.chatty:
                        sys.stdout.write(" server: connection cipher jest now " + str(cipher) + "\n")
                        sys.stdout.write(" server: selected protocol jest now "
                                + str(self.sslconn.selected_npn_protocol()) + "\n")
                    zwróć Prawda

            def read(self):
                jeżeli self.sslconn:
                    zwróć self.sslconn.read()
                inaczej:
                    zwróć self.sock.recv(1024)

            def write(self, bytes):
                jeżeli self.sslconn:
                    zwróć self.sslconn.write(bytes)
                inaczej:
                    zwróć self.sock.send(bytes)

            def close(self):
                jeżeli self.sslconn:
                    self.sslconn.close()
                inaczej:
                    self.sock.close()

            def run(self):
                self.running = Prawda
                jeżeli nie self.server.starttls_server:
                    jeżeli nie self.wrap_conn():
                        zwróć
                dopóki self.running:
                    spróbuj:
                        msg = self.read()
                        stripped = msg.strip()
                        jeżeli nie stripped:
                            # eof, so quit this handler
                            self.running = Nieprawda
                            self.close()
                        albo_inaczej stripped == b'over':
                            jeżeli support.verbose oraz self.server.connectionchatty:
                                sys.stdout.write(" server: client closed connection\n")
                            self.close()
                            zwróć
                        albo_inaczej (self.server.starttls_server oraz
                              stripped == b'STARTTLS'):
                            jeżeli support.verbose oraz self.server.connectionchatty:
                                sys.stdout.write(" server: read STARTTLS z client, sending OK...\n")
                            self.write(b"OK\n")
                            jeżeli nie self.wrap_conn():
                                zwróć
                        albo_inaczej (self.server.starttls_server oraz self.sslconn
                              oraz stripped == b'ENDTLS'):
                            jeżeli support.verbose oraz self.server.connectionchatty:
                                sys.stdout.write(" server: read ENDTLS z client, sending OK...\n")
                            self.write(b"OK\n")
                            self.sock = self.sslconn.unwrap()
                            self.sslconn = Nic
                            jeżeli support.verbose oraz self.server.connectionchatty:
                                sys.stdout.write(" server: connection jest now unencrypted...\n")
                        albo_inaczej stripped == b'CB tls-unique':
                            jeżeli support.verbose oraz self.server.connectionchatty:
                                sys.stdout.write(" server: read CB tls-unique z client, sending our CB data...\n")
                            data = self.sslconn.get_channel_binding("tls-unique")
                            self.write(repr(data).encode("us-ascii") + b"\n")
                        inaczej:
                            jeżeli (support.verbose oraz
                                self.server.connectionchatty):
                                ctype = (self.sslconn oraz "encrypted") albo "unencrypted"
                                sys.stdout.write(" server: read %r (%s), sending back %r (%s)...\n"
                                                 % (msg, ctype, msg.lower(), ctype))
                            self.write(msg.lower())
                    wyjąwszy OSError:
                        jeżeli self.server.chatty:
                            handle_error("Test server failure:\n")
                        self.close()
                        self.running = Nieprawda
                        # normally, we'd just stop here, but dla the test
                        # harness, we want to stop the server
                        self.server.stop()

        def __init__(self, certificate=Nic, ssl_version=Nic,
                     certreqs=Nic, cacerts=Nic,
                     chatty=Prawda, connectionchatty=Nieprawda, starttls_server=Nieprawda,
                     npn_protocols=Nic, alpn_protocols=Nic,
                     ciphers=Nic, context=Nic):
            jeżeli context:
                self.context = context
            inaczej:
                self.context = ssl.SSLContext(ssl_version
                                              jeżeli ssl_version jest nie Nic
                                              inaczej ssl.PROTOCOL_TLSv1)
                self.context.verify_mode = (certreqs jeżeli certreqs jest nie Nic
                                            inaczej ssl.CERT_NONE)
                jeżeli cacerts:
                    self.context.load_verify_locations(cacerts)
                jeżeli certificate:
                    self.context.load_cert_chain(certificate)
                jeżeli npn_protocols:
                    self.context.set_npn_protocols(npn_protocols)
                jeżeli alpn_protocols:
                    self.context.set_alpn_protocols(alpn_protocols)
                jeżeli ciphers:
                    self.context.set_ciphers(ciphers)
            self.chatty = chatty
            self.connectionchatty = connectionchatty
            self.starttls_server = starttls_server
            self.sock = socket.socket()
            self.port = support.bind_port(self.sock)
            self.flag = Nic
            self.active = Nieprawda
            self.selected_npn_protocols = []
            self.selected_alpn_protocols = []
            self.shared_ciphers = []
            self.conn_errors = []
            threading.Thread.__init__(self)
            self.daemon = Prawda

        def __enter__(self):
            self.start(threading.Event())
            self.flag.wait()
            zwróć self

        def __exit__(self, *args):
            self.stop()
            self.join()

        def start(self, flag=Nic):
            self.flag = flag
            threading.Thread.start(self)

        def run(self):
            self.sock.settimeout(0.05)
            self.sock.listen()
            self.active = Prawda
            jeżeli self.flag:
                # signal an event
                self.flag.set()
            dopóki self.active:
                spróbuj:
                    newconn, connaddr = self.sock.accept()
                    jeżeli support.verbose oraz self.chatty:
                        sys.stdout.write(' server:  new connection z '
                                         + repr(connaddr) + '\n')
                    handler = self.ConnectionHandler(self, newconn, connaddr)
                    handler.start()
                    handler.join()
                wyjąwszy socket.timeout:
                    dalej
                wyjąwszy KeyboardInterrupt:
                    self.stop()
            self.sock.close()

        def stop(self):
            self.active = Nieprawda

    klasa AsyncoreEchoServer(threading.Thread):

        # this one's based on asyncore.dispatcher

        klasa EchoServer (asyncore.dispatcher):

            klasa ConnectionHandler (asyncore.dispatcher_with_send):

                def __init__(self, conn, certfile):
                    self.socket = ssl.wrap_socket(conn, server_side=Prawda,
                                                  certfile=certfile,
                                                  do_handshake_on_connect=Nieprawda)
                    asyncore.dispatcher_with_send.__init__(self, self.socket)
                    self._ssl_accepting = Prawda
                    self._do_ssl_handshake()

                def readable(self):
                    jeżeli isinstance(self.socket, ssl.SSLSocket):
                        dopóki self.socket.pending() > 0:
                            self.handle_read_event()
                    zwróć Prawda

                def _do_ssl_handshake(self):
                    spróbuj:
                        self.socket.do_handshake()
                    wyjąwszy (ssl.SSLWantReadError, ssl.SSLWantWriteError):
                        zwróć
                    wyjąwszy ssl.SSLEOFError:
                        zwróć self.handle_close()
                    wyjąwszy ssl.SSLError:
                        podnieś
                    wyjąwszy OSError jako err:
                        jeżeli err.args[0] == errno.ECONNABORTED:
                            zwróć self.handle_close()
                    inaczej:
                        self._ssl_accepting = Nieprawda

                def handle_read(self):
                    jeżeli self._ssl_accepting:
                        self._do_ssl_handshake()
                    inaczej:
                        data = self.recv(1024)
                        jeżeli support.verbose:
                            sys.stdout.write(" server:  read %s z client\n" % repr(data))
                        jeżeli nie data:
                            self.close()
                        inaczej:
                            self.send(data.lower())

                def handle_close(self):
                    self.close()
                    jeżeli support.verbose:
                        sys.stdout.write(" server:  closed connection %s\n" % self.socket)

                def handle_error(self):
                    podnieś

            def __init__(self, certfile):
                self.certfile = certfile
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.port = support.bind_port(sock, '')
                asyncore.dispatcher.__init__(self, sock)
                self.listen(5)

            def handle_accepted(self, sock_obj, addr):
                jeżeli support.verbose:
                    sys.stdout.write(" server:  new connection z %s:%s\n" %addr)
                self.ConnectionHandler(sock_obj, self.certfile)

            def handle_error(self):
                podnieś

        def __init__(self, certfile):
            self.flag = Nic
            self.active = Nieprawda
            self.server = self.EchoServer(certfile)
            self.port = self.server.port
            threading.Thread.__init__(self)
            self.daemon = Prawda

        def __str__(self):
            zwróć "<%s %s>" % (self.__class__.__name__, self.server)

        def __enter__(self):
            self.start(threading.Event())
            self.flag.wait()
            zwróć self

        def __exit__(self, *args):
            jeżeli support.verbose:
                sys.stdout.write(" cleanup: stopping server.\n")
            self.stop()
            jeżeli support.verbose:
                sys.stdout.write(" cleanup: joining server thread.\n")
            self.join()
            jeżeli support.verbose:
                sys.stdout.write(" cleanup: successfully joined.\n")

        def start (self, flag=Nic):
            self.flag = flag
            threading.Thread.start(self)

        def run(self):
            self.active = Prawda
            jeżeli self.flag:
                self.flag.set()
            dopóki self.active:
                spróbuj:
                    asyncore.loop(1)
                wyjąwszy:
                    dalej

        def stop(self):
            self.active = Nieprawda
            self.server.close()

    def bad_cert_test(certfile):
        """
        Launch a server przy CERT_REQUIRED, oraz check that trying to
        connect to it przy the given client certificate fails.
        """
        server = ThreadedEchoServer(CERTFILE,
                                    certreqs=ssl.CERT_REQUIRED,
                                    cacerts=CERTFILE, chatty=Nieprawda,
                                    connectionchatty=Nieprawda)
        przy server:
            spróbuj:
                przy socket.socket() jako sock:
                    s = ssl.wrap_socket(sock,
                                        certfile=certfile,
                                        ssl_version=ssl.PROTOCOL_TLSv1)
                    s.connect((HOST, server.port))
            wyjąwszy ssl.SSLError jako x:
                jeżeli support.verbose:
                    sys.stdout.write("\nSSLError jest %s\n" % x.args[1])
            wyjąwszy OSError jako x:
                jeżeli support.verbose:
                    sys.stdout.write("\nOSError jest %s\n" % x.args[1])
            wyjąwszy OSError jako x:
                jeżeli x.errno != errno.ENOENT:
                    podnieś
                jeżeli support.verbose:
                    sys.stdout.write("\OSError jest %s\n" % str(x))
            inaczej:
                podnieś AssertionError("Use of invalid cert should have failed!")

    def server_params_test(client_context, server_context, indata=b"FOO\n",
                           chatty=Prawda, connectionchatty=Nieprawda, sni_name=Nic):
        """
        Launch a server, connect a client to it oraz try various reads
        oraz writes.
        """
        stats = {}
        server = ThreadedEchoServer(context=server_context,
                                    chatty=chatty,
                                    connectionchatty=Nieprawda)
        przy server:
            przy client_context.wrap_socket(socket.socket(),
                    server_hostname=sni_name) jako s:
                s.connect((HOST, server.port))
                dla arg w [indata, bytearray(indata), memoryview(indata)]:
                    jeżeli connectionchatty:
                        jeżeli support.verbose:
                            sys.stdout.write(
                                " client:  sending %r...\n" % indata)
                    s.write(arg)
                    outdata = s.read()
                    jeżeli connectionchatty:
                        jeżeli support.verbose:
                            sys.stdout.write(" client:  read %r\n" % outdata)
                    jeżeli outdata != indata.lower():
                        podnieś AssertionError(
                            "bad data <<%r>> (%d) received; expected <<%r>> (%d)\n"
                            % (outdata[:20], len(outdata),
                               indata[:20].lower(), len(indata)))
                s.write(b"over\n")
                jeżeli connectionchatty:
                    jeżeli support.verbose:
                        sys.stdout.write(" client:  closing connection.\n")
                stats.update({
                    'compression': s.compression(),
                    'cipher': s.cipher(),
                    'peercert': s.getpeercert(),
                    'client_alpn_protocol': s.selected_alpn_protocol(),
                    'client_npn_protocol': s.selected_npn_protocol(),
                    'version': s.version(),
                })
                s.close()
            stats['server_alpn_protocols'] = server.selected_alpn_protocols
            stats['server_npn_protocols'] = server.selected_npn_protocols
            stats['server_shared_ciphers'] = server.shared_ciphers
        zwróć stats

    def try_protocol_combo(server_protocol, client_protocol, expect_success,
                           certsreqs=Nic, server_options=0, client_options=0):
        """
        Try to SSL-connect using *client_protocol* to *server_protocol*.
        If *expect_success* jest true, assert that the connection succeeds,
        jeżeli it's false, assert that the connection fails.
        Also, jeżeli *expect_success* jest a string, assert that it jest the protocol
        version actually used by the connection.
        """
        jeżeli certsreqs jest Nic:
            certsreqs = ssl.CERT_NONE
        certtype = {
            ssl.CERT_NONE: "CERT_NONE",
            ssl.CERT_OPTIONAL: "CERT_OPTIONAL",
            ssl.CERT_REQUIRED: "CERT_REQUIRED",
        }[certsreqs]
        jeżeli support.verbose:
            formatstr = (expect_success oraz " %s->%s %s\n") albo " {%s->%s} %s\n"
            sys.stdout.write(formatstr %
                             (ssl.get_protocol_name(client_protocol),
                              ssl.get_protocol_name(server_protocol),
                              certtype))
        client_context = ssl.SSLContext(client_protocol)
        client_context.options |= client_options
        server_context = ssl.SSLContext(server_protocol)
        server_context.options |= server_options

        # NOTE: we must enable "ALL" ciphers on the client, otherwise an
        # SSLv23 client will send an SSLv3 hello (rather than SSLv2)
        # starting z OpenSSL 1.0.0 (see issue #8322).
        jeżeli client_context.protocol == ssl.PROTOCOL_SSLv23:
            client_context.set_ciphers("ALL")

        dla ctx w (client_context, server_context):
            ctx.verify_mode = certsreqs
            ctx.load_cert_chain(CERTFILE)
            ctx.load_verify_locations(CERTFILE)
        spróbuj:
            stats = server_params_test(client_context, server_context,
                                       chatty=Nieprawda, connectionchatty=Nieprawda)
        # Protocol mismatch can result w either an SSLError, albo a
        # "Connection reset by peer" error.
        wyjąwszy ssl.SSLError:
            jeżeli expect_success:
                podnieś
        wyjąwszy OSError jako e:
            jeżeli expect_success albo e.errno != errno.ECONNRESET:
                podnieś
        inaczej:
            jeżeli nie expect_success:
                podnieś AssertionError(
                    "Client protocol %s succeeded przy server protocol %s!"
                    % (ssl.get_protocol_name(client_protocol),
                       ssl.get_protocol_name(server_protocol)))
            albo_inaczej (expect_success jest nie Prawda
                  oraz expect_success != stats['version']):
                podnieś AssertionError("version mismatch: expected %r, got %r"
                                     % (expect_success, stats['version']))


    klasa ThreadedTests(unittest.TestCase):

        @skip_if_broken_ubuntu_ssl
        def test_echo(self):
            """Basic test of an SSL client connecting to a server"""
            jeżeli support.verbose:
                sys.stdout.write("\n")
            dla protocol w PROTOCOLS:
                przy self.subTest(protocol=ssl._PROTOCOL_NAMES[protocol]):
                    context = ssl.SSLContext(protocol)
                    context.load_cert_chain(CERTFILE)
                    server_params_test(context, context,
                                       chatty=Prawda, connectionchatty=Prawda)

        def test_getpeercert(self):
            jeżeli support.verbose:
                sys.stdout.write("\n")
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(CERTFILE)
            context.load_cert_chain(CERTFILE)
            server = ThreadedEchoServer(context=context, chatty=Nieprawda)
            przy server:
                s = context.wrap_socket(socket.socket(),
                                        do_handshake_on_connect=Nieprawda)
                s.connect((HOST, server.port))
                # getpeercert() podnieś ValueError dopóki the handshake isn't
                # done.
                przy self.assertRaises(ValueError):
                    s.getpeercert()
                s.do_handshake()
                cert = s.getpeercert()
                self.assertPrawda(cert, "Can't get peer certificate.")
                cipher = s.cipher()
                jeżeli support.verbose:
                    sys.stdout.write(pprint.pformat(cert) + '\n')
                    sys.stdout.write("Connection cipher jest " + str(cipher) + '.\n')
                jeżeli 'subject' nie w cert:
                    self.fail("No subject field w certificate: %s." %
                              pprint.pformat(cert))
                jeżeli ((('organizationName', 'Python Software Foundation'),)
                    nie w cert['subject']):
                    self.fail(
                        "Missing albo invalid 'organizationName' field w certificate subject; "
                        "should be 'Python Software Foundation'.")
                self.assertIn('notBefore', cert)
                self.assertIn('notAfter', cert)
                before = ssl.cert_time_to_seconds(cert['notBefore'])
                after = ssl.cert_time_to_seconds(cert['notAfter'])
                self.assertLess(before, after)
                s.close()

        @unittest.skipUnless(have_verify_flags(),
                            "verify_flags need OpenSSL > 0.9.8")
        def test_crl_check(self):
            jeżeli support.verbose:
                sys.stdout.write("\n")

            server_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            server_context.load_cert_chain(SIGNED_CERTFILE)

            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(SIGNING_CA)
            tf = getattr(ssl, "VERIFY_X509_TRUSTED_FIRST", 0)
            self.assertEqual(context.verify_flags, ssl.VERIFY_DEFAULT | tf)

            # VERIFY_DEFAULT should dalej
            server = ThreadedEchoServer(context=server_context, chatty=Prawda)
            przy server:
                przy context.wrap_socket(socket.socket()) jako s:
                    s.connect((HOST, server.port))
                    cert = s.getpeercert()
                    self.assertPrawda(cert, "Can't get peer certificate.")

            # VERIFY_CRL_CHECK_LEAF without a loaded CRL file fails
            context.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF

            server = ThreadedEchoServer(context=server_context, chatty=Prawda)
            przy server:
                przy context.wrap_socket(socket.socket()) jako s:
                    przy self.assertRaisesRegex(ssl.SSLError,
                                                "certificate verify failed"):
                        s.connect((HOST, server.port))

            # now load a CRL file. The CRL file jest signed by the CA.
            context.load_verify_locations(CRLFILE)

            server = ThreadedEchoServer(context=server_context, chatty=Prawda)
            przy server:
                przy context.wrap_socket(socket.socket()) jako s:
                    s.connect((HOST, server.port))
                    cert = s.getpeercert()
                    self.assertPrawda(cert, "Can't get peer certificate.")

        def test_check_hostname(self):
            jeżeli support.verbose:
                sys.stdout.write("\n")

            server_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            server_context.load_cert_chain(SIGNED_CERTFILE)

            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = Prawda
            context.load_verify_locations(SIGNING_CA)

            # correct hostname should verify
            server = ThreadedEchoServer(context=server_context, chatty=Prawda)
            przy server:
                przy context.wrap_socket(socket.socket(),
                                         server_hostname="localhost") jako s:
                    s.connect((HOST, server.port))
                    cert = s.getpeercert()
                    self.assertPrawda(cert, "Can't get peer certificate.")

            # incorrect hostname should podnieś an exception
            server = ThreadedEchoServer(context=server_context, chatty=Prawda)
            przy server:
                przy context.wrap_socket(socket.socket(),
                                         server_hostname="invalid") jako s:
                    przy self.assertRaisesRegex(ssl.CertificateError,
                                                "hostname 'invalid' doesn't match 'localhost'"):
                        s.connect((HOST, server.port))

            # missing server_hostname arg should cause an exception, too
            server = ThreadedEchoServer(context=server_context, chatty=Prawda)
            przy server:
                przy socket.socket() jako s:
                    przy self.assertRaisesRegex(ValueError,
                                                "check_hostname requires server_hostname"):
                        context.wrap_socket(s)

        def test_empty_cert(self):
            """Connecting przy an empty cert file"""
            bad_cert_test(os.path.join(os.path.dirname(__file__) albo os.curdir,
                                      "nullcert.pem"))
        def test_malformed_cert(self):
            """Connecting przy a badly formatted certificate (syntax error)"""
            bad_cert_test(os.path.join(os.path.dirname(__file__) albo os.curdir,
                                       "badcert.pem"))
        def test_nonexisting_cert(self):
            """Connecting przy a non-existing cert file"""
            bad_cert_test(os.path.join(os.path.dirname(__file__) albo os.curdir,
                                       "wrongcert.pem"))
        def test_malformed_key(self):
            """Connecting przy a badly formatted key (syntax error)"""
            bad_cert_test(os.path.join(os.path.dirname(__file__) albo os.curdir,
                                       "badkey.pem"))

        def test_rude_shutdown(self):
            """A brutal shutdown of an SSL server should podnieś an OSError
            w the client when attempting handshake.
            """
            listener_ready = threading.Event()
            listener_gone = threading.Event()

            s = socket.socket()
            port = support.bind_port(s, HOST)

            # `listener` runs w a thread.  It sits w an accept() until
            # the main thread connects.  Then it rudely closes the socket,
            # oraz sets Event `listener_gone` to let the main thread know
            # the socket jest gone.
            def listener():
                s.listen()
                listener_ready.set()
                newsock, addr = s.accept()
                newsock.close()
                s.close()
                listener_gone.set()

            def connector():
                listener_ready.wait()
                przy socket.socket() jako c:
                    c.connect((HOST, port))
                    listener_gone.wait()
                    spróbuj:
                        ssl_sock = ssl.wrap_socket(c)
                    wyjąwszy OSError:
                        dalej
                    inaczej:
                        self.fail('connecting to closed SSL socket should have failed')

            t = threading.Thread(target=listener)
            t.start()
            spróbuj:
                connector()
            w_końcu:
                t.join()

        @skip_if_broken_ubuntu_ssl
        @unittest.skipUnless(hasattr(ssl, 'PROTOCOL_SSLv2'),
                             "OpenSSL jest compiled without SSLv2 support")
        def test_protocol_sslv2(self):
            """Connecting to an SSLv2 server przy various client options"""
            jeżeli support.verbose:
                sys.stdout.write("\n")
            try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv2, Prawda)
            try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv2, Prawda, ssl.CERT_OPTIONAL)
            try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv2, Prawda, ssl.CERT_REQUIRED)
            try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv23, Nieprawda)
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv3'):
                try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv3, Nieprawda)
            try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_TLSv1, Nieprawda)
            # SSLv23 client przy specific SSL options
            jeżeli no_sslv2_implies_sslv3_hello():
                # No SSLv2 => client will use an SSLv3 hello on recent OpenSSLs
                try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv23, Nieprawda,
                                   client_options=ssl.OP_NO_SSLv2)
            try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv23, Nieprawda,
                               client_options=ssl.OP_NO_SSLv3)
            try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv23, Nieprawda,
                               client_options=ssl.OP_NO_TLSv1)

        @skip_if_broken_ubuntu_ssl
        def test_protocol_sslv23(self):
            """Connecting to an SSLv23 server przy various client options"""
            jeżeli support.verbose:
                sys.stdout.write("\n")
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv2'):
                spróbuj:
                    try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv2, Prawda)
                wyjąwszy OSError jako x:
                    # this fails on some older versions of OpenSSL (0.9.7l, dla instance)
                    jeżeli support.verbose:
                        sys.stdout.write(
                            " SSL2 client to SSL23 server test unexpectedly failed:\n %s\n"
                            % str(x))
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv3'):
                try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv3, 'SSLv3')
            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv23, Prawda)
            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_TLSv1, 'TLSv1')

            jeżeli hasattr(ssl, 'PROTOCOL_SSLv3'):
                try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv3, 'SSLv3', ssl.CERT_OPTIONAL)
            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv23, Prawda, ssl.CERT_OPTIONAL)
            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_TLSv1, 'TLSv1', ssl.CERT_OPTIONAL)

            jeżeli hasattr(ssl, 'PROTOCOL_SSLv3'):
                try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv3, 'SSLv3', ssl.CERT_REQUIRED)
            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv23, Prawda, ssl.CERT_REQUIRED)
            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_TLSv1, 'TLSv1', ssl.CERT_REQUIRED)

            # Server przy specific SSL options
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv3'):
                try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv3, Nieprawda,
                               server_options=ssl.OP_NO_SSLv3)
            # Will choose TLSv1
            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv23, Prawda,
                               server_options=ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3)
            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_TLSv1, Nieprawda,
                               server_options=ssl.OP_NO_TLSv1)


        @skip_if_broken_ubuntu_ssl
        @unittest.skipUnless(hasattr(ssl, 'PROTOCOL_SSLv3'),
                             "OpenSSL jest compiled without SSLv3 support")
        def test_protocol_sslv3(self):
            """Connecting to an SSLv3 server przy various client options"""
            jeżeli support.verbose:
                sys.stdout.write("\n")
            try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv3, 'SSLv3')
            try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv3, 'SSLv3', ssl.CERT_OPTIONAL)
            try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv3, 'SSLv3', ssl.CERT_REQUIRED)
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv2'):
                try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv2, Nieprawda)
            try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv23, Nieprawda,
                               client_options=ssl.OP_NO_SSLv3)
            try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_TLSv1, Nieprawda)
            jeżeli no_sslv2_implies_sslv3_hello():
                # No SSLv2 => client will use an SSLv3 hello on recent OpenSSLs
                try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv23, 'SSLv3',
                                   client_options=ssl.OP_NO_SSLv2)

        @skip_if_broken_ubuntu_ssl
        def test_protocol_tlsv1(self):
            """Connecting to a TLSv1 server przy various client options"""
            jeżeli support.verbose:
                sys.stdout.write("\n")
            try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1, 'TLSv1')
            try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1, 'TLSv1', ssl.CERT_OPTIONAL)
            try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1, 'TLSv1', ssl.CERT_REQUIRED)
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv2'):
                try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_SSLv2, Nieprawda)
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv3'):
                try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_SSLv3, Nieprawda)
            try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_SSLv23, Nieprawda,
                               client_options=ssl.OP_NO_TLSv1)

        @skip_if_broken_ubuntu_ssl
        @unittest.skipUnless(hasattr(ssl, "PROTOCOL_TLSv1_1"),
                             "TLS version 1.1 nie supported.")
        def test_protocol_tlsv1_1(self):
            """Connecting to a TLSv1.1 server przy various client options.
               Testing against older TLS versions."""
            jeżeli support.verbose:
                sys.stdout.write("\n")
            try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_TLSv1_1, 'TLSv1.1')
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv2'):
                try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_SSLv2, Nieprawda)
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv3'):
                try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_SSLv3, Nieprawda)
            try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_SSLv23, Nieprawda,
                               client_options=ssl.OP_NO_TLSv1_1)

            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_TLSv1_1, 'TLSv1.1')
            try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_TLSv1, Nieprawda)
            try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_1, Nieprawda)


        @skip_if_broken_ubuntu_ssl
        @unittest.skipUnless(hasattr(ssl, "PROTOCOL_TLSv1_2"),
                             "TLS version 1.2 nie supported.")
        def test_protocol_tlsv1_2(self):
            """Connecting to a TLSv1.2 server przy various client options.
               Testing against older TLS versions."""
            jeżeli support.verbose:
                sys.stdout.write("\n")
            try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_TLSv1_2, 'TLSv1.2',
                               server_options=ssl.OP_NO_SSLv3|ssl.OP_NO_SSLv2,
                               client_options=ssl.OP_NO_SSLv3|ssl.OP_NO_SSLv2,)
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv2'):
                try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_SSLv2, Nieprawda)
            jeżeli hasattr(ssl, 'PROTOCOL_SSLv3'):
                try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_SSLv3, Nieprawda)
            try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_SSLv23, Nieprawda,
                               client_options=ssl.OP_NO_TLSv1_2)

            try_protocol_combo(ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_TLSv1_2, 'TLSv1.2')
            try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_TLSv1, Nieprawda)
            try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_2, Nieprawda)
            try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_TLSv1_1, Nieprawda)
            try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_TLSv1_2, Nieprawda)

        def test_starttls(self):
            """Switching z clear text to encrypted oraz back again."""
            msgs = (b"msg 1", b"MSG 2", b"STARTTLS", b"MSG 3", b"msg 4", b"ENDTLS", b"msg 5", b"msg 6")

            server = ThreadedEchoServer(CERTFILE,
                                        ssl_version=ssl.PROTOCOL_TLSv1,
                                        starttls_server=Prawda,
                                        chatty=Prawda,
                                        connectionchatty=Prawda)
            wrapped = Nieprawda
            przy server:
                s = socket.socket()
                s.setblocking(1)
                s.connect((HOST, server.port))
                jeżeli support.verbose:
                    sys.stdout.write("\n")
                dla indata w msgs:
                    jeżeli support.verbose:
                        sys.stdout.write(
                            " client:  sending %r...\n" % indata)
                    jeżeli wrapped:
                        conn.write(indata)
                        outdata = conn.read()
                    inaczej:
                        s.send(indata)
                        outdata = s.recv(1024)
                    msg = outdata.strip().lower()
                    jeżeli indata == b"STARTTLS" oraz msg.startswith(b"ok"):
                        # STARTTLS ok, switch to secure mode
                        jeżeli support.verbose:
                            sys.stdout.write(
                                " client:  read %r z server, starting TLS...\n"
                                % msg)
                        conn = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
                        wrapped = Prawda
                    albo_inaczej indata == b"ENDTLS" oraz msg.startswith(b"ok"):
                        # ENDTLS ok, switch back to clear text
                        jeżeli support.verbose:
                            sys.stdout.write(
                                " client:  read %r z server, ending TLS...\n"
                                % msg)
                        s = conn.unwrap()
                        wrapped = Nieprawda
                    inaczej:
                        jeżeli support.verbose:
                            sys.stdout.write(
                                " client:  read %r z server\n" % msg)
                jeżeli support.verbose:
                    sys.stdout.write(" client:  closing connection.\n")
                jeżeli wrapped:
                    conn.write(b"over\n")
                inaczej:
                    s.send(b"over\n")
                jeżeli wrapped:
                    conn.close()
                inaczej:
                    s.close()

        def test_socketserver(self):
            """Using a SocketServer to create oraz manage SSL connections."""
            server = make_https_server(self, certfile=CERTFILE)
            # try to connect
            jeżeli support.verbose:
                sys.stdout.write('\n')
            przy open(CERTFILE, 'rb') jako f:
                d1 = f.read()
            d2 = ''
            # now fetch the same data z the HTTPS server
            url = 'https://localhost:%d/%s' % (
                server.port, os.path.split(CERTFILE)[1])
            context = ssl.create_default_context(cafile=CERTFILE)
            f = urllib.request.urlopen(url, context=context)
            spróbuj:
                dlen = f.info().get("content-length")
                jeżeli dlen oraz (int(dlen) > 0):
                    d2 = f.read(int(dlen))
                    jeżeli support.verbose:
                        sys.stdout.write(
                            " client: read %d bytes z remote server '%s'\n"
                            % (len(d2), server))
            w_końcu:
                f.close()
            self.assertEqual(d1, d2)

        def test_asyncore_server(self):
            """Check the example asyncore integration."""
            indata = "TEST MESSAGE of mixed case\n"

            jeżeli support.verbose:
                sys.stdout.write("\n")

            indata = b"FOO\n"
            server = AsyncoreEchoServer(CERTFILE)
            przy server:
                s = ssl.wrap_socket(socket.socket())
                s.connect(('127.0.0.1', server.port))
                jeżeli support.verbose:
                    sys.stdout.write(
                        " client:  sending %r...\n" % indata)
                s.write(indata)
                outdata = s.read()
                jeżeli support.verbose:
                    sys.stdout.write(" client:  read %r\n" % outdata)
                jeżeli outdata != indata.lower():
                    self.fail(
                        "bad data <<%r>> (%d) received; expected <<%r>> (%d)\n"
                        % (outdata[:20], len(outdata),
                           indata[:20].lower(), len(indata)))
                s.write(b"over\n")
                jeżeli support.verbose:
                    sys.stdout.write(" client:  closing connection.\n")
                s.close()
                jeżeli support.verbose:
                    sys.stdout.write(" client:  connection closed.\n")

        def test_recv_send(self):
            """Test recv(), send() oraz friends."""
            jeżeli support.verbose:
                sys.stdout.write("\n")

            server = ThreadedEchoServer(CERTFILE,
                                        certreqs=ssl.CERT_NONE,
                                        ssl_version=ssl.PROTOCOL_TLSv1,
                                        cacerts=CERTFILE,
                                        chatty=Prawda,
                                        connectionchatty=Nieprawda)
            przy server:
                s = ssl.wrap_socket(socket.socket(),
                                    server_side=Nieprawda,
                                    certfile=CERTFILE,
                                    ca_certs=CERTFILE,
                                    cert_reqs=ssl.CERT_NONE,
                                    ssl_version=ssl.PROTOCOL_TLSv1)
                s.connect((HOST, server.port))
                # helper methods dla standardising recv* method signatures
                def _recv_into():
                    b = bytearray(b"\0"*100)
                    count = s.recv_into(b)
                    zwróć b[:count]

                def _recvfrom_into():
                    b = bytearray(b"\0"*100)
                    count, addr = s.recvfrom_into(b)
                    zwróć b[:count]

                # (name, method, whether to expect success, *args)
                send_methods = [
                    ('send', s.send, Prawda, []),
                    ('sendto', s.sendto, Nieprawda, ["some.address"]),
                    ('sendall', s.sendall, Prawda, []),
                ]
                recv_methods = [
                    ('recv', s.recv, Prawda, []),
                    ('recvfrom', s.recvfrom, Nieprawda, ["some.address"]),
                    ('recv_into', _recv_into, Prawda, []),
                    ('recvfrom_into', _recvfrom_into, Nieprawda, []),
                ]
                data_prefix = "PREFIX_"

                dla meth_name, send_meth, expect_success, args w send_methods:
                    indata = (data_prefix + meth_name).encode('ascii')
                    spróbuj:
                        send_meth(indata, *args)
                        outdata = s.read()
                        jeżeli outdata != indata.lower():
                            self.fail(
                                "While sending przy <<{name:s}>> bad data "
                                "<<{outdata:r}>> ({nout:d}) received; "
                                "expected <<{indata:r}>> ({nin:d})\n".format(
                                    name=meth_name, outdata=outdata[:20],
                                    nout=len(outdata),
                                    indata=indata[:20], nin=len(indata)
                                )
                            )
                    wyjąwszy ValueError jako e:
                        jeżeli expect_success:
                            self.fail(
                                "Failed to send przy method <<{name:s}>>; "
                                "expected to succeed.\n".format(name=meth_name)
                            )
                        jeżeli nie str(e).startswith(meth_name):
                            self.fail(
                                "Method <<{name:s}>> failed przy unexpected "
                                "exception message: {exp:s}\n".format(
                                    name=meth_name, exp=e
                                )
                            )

                dla meth_name, recv_meth, expect_success, args w recv_methods:
                    indata = (data_prefix + meth_name).encode('ascii')
                    spróbuj:
                        s.send(indata)
                        outdata = recv_meth(*args)
                        jeżeli outdata != indata.lower():
                            self.fail(
                                "While receiving przy <<{name:s}>> bad data "
                                "<<{outdata:r}>> ({nout:d}) received; "
                                "expected <<{indata:r}>> ({nin:d})\n".format(
                                    name=meth_name, outdata=outdata[:20],
                                    nout=len(outdata),
                                    indata=indata[:20], nin=len(indata)
                                )
                            )
                    wyjąwszy ValueError jako e:
                        jeżeli expect_success:
                            self.fail(
                                "Failed to receive przy method <<{name:s}>>; "
                                "expected to succeed.\n".format(name=meth_name)
                            )
                        jeżeli nie str(e).startswith(meth_name):
                            self.fail(
                                "Method <<{name:s}>> failed przy unexpected "
                                "exception message: {exp:s}\n".format(
                                    name=meth_name, exp=e
                                )
                            )
                        # consume data
                        s.read()

                # Make sure sendmsg et al are disallowed to avoid
                # inadvertent disclosure of data and/or corruption
                # of the encrypted data stream
                self.assertRaises(NotImplementedError, s.sendmsg, [b"data"])
                self.assertRaises(NotImplementedError, s.recvmsg, 100)
                self.assertRaises(NotImplementedError,
                                  s.recvmsg_into, bytearray(100))

                s.write(b"over\n")
                s.close()

        def test_nonblocking_send(self):
            server = ThreadedEchoServer(CERTFILE,
                                        certreqs=ssl.CERT_NONE,
                                        ssl_version=ssl.PROTOCOL_TLSv1,
                                        cacerts=CERTFILE,
                                        chatty=Prawda,
                                        connectionchatty=Nieprawda)
            przy server:
                s = ssl.wrap_socket(socket.socket(),
                                    server_side=Nieprawda,
                                    certfile=CERTFILE,
                                    ca_certs=CERTFILE,
                                    cert_reqs=ssl.CERT_NONE,
                                    ssl_version=ssl.PROTOCOL_TLSv1)
                s.connect((HOST, server.port))
                s.setblocking(Nieprawda)

                # If we keep sending data, at some point the buffers
                # will be full oraz the call will block
                buf = bytearray(8192)
                def fill_buffer():
                    dopóki Prawda:
                        s.send(buf)
                self.assertRaises((ssl.SSLWantWriteError,
                                   ssl.SSLWantReadError), fill_buffer)

                # Now read all the output oraz discard it
                s.setblocking(Prawda)
                s.close()

        def test_handshake_timeout(self):
            # Issue #5103: SSL handshake must respect the socket timeout
            server = socket.socket(socket.AF_INET)
            host = "127.0.0.1"
            port = support.bind_port(server)
            started = threading.Event()
            finish = Nieprawda

            def serve():
                server.listen()
                started.set()
                conns = []
                dopóki nie finish:
                    r, w, e = select.select([server], [], [], 0.1)
                    jeżeli server w r:
                        # Let the socket hang around rather than having
                        # it closed by garbage collection.
                        conns.append(server.accept()[0])
                dla sock w conns:
                    sock.close()

            t = threading.Thread(target=serve)
            t.start()
            started.wait()

            spróbuj:
                spróbuj:
                    c = socket.socket(socket.AF_INET)
                    c.settimeout(0.2)
                    c.connect((host, port))
                    # Will attempt handshake oraz time out
                    self.assertRaisesRegex(socket.timeout, "timed out",
                                           ssl.wrap_socket, c)
                w_końcu:
                    c.close()
                spróbuj:
                    c = socket.socket(socket.AF_INET)
                    c = ssl.wrap_socket(c)
                    c.settimeout(0.2)
                    # Will attempt handshake oraz time out
                    self.assertRaisesRegex(socket.timeout, "timed out",
                                           c.connect, (host, port))
                w_końcu:
                    c.close()
            w_końcu:
                finish = Prawda
                t.join()
                server.close()

        def test_server_accept(self):
            # Issue #16357: accept() on a SSLSocket created through
            # SSLContext.wrap_socket().
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(CERTFILE)
            context.load_cert_chain(CERTFILE)
            server = socket.socket(socket.AF_INET)
            host = "127.0.0.1"
            port = support.bind_port(server)
            server = context.wrap_socket(server, server_side=Prawda)

            evt = threading.Event()
            remote = Nic
            peer = Nic
            def serve():
                nonlocal remote, peer
                server.listen()
                # Block on the accept oraz wait on the connection to close.
                evt.set()
                remote, peer = server.accept()
                remote.recv(1)

            t = threading.Thread(target=serve)
            t.start()
            # Client wait until server setup oraz perform a connect.
            evt.wait()
            client = context.wrap_socket(socket.socket())
            client.connect((host, port))
            client_addr = client.getsockname()
            client.close()
            t.join()
            remote.close()
            server.close()
            # Sanity checks.
            self.assertIsInstance(remote, ssl.SSLSocket)
            self.assertEqual(peer, client_addr)

        def test_getpeercert_enotconn(self):
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            przy context.wrap_socket(socket.socket()) jako sock:
                przy self.assertRaises(OSError) jako cm:
                    sock.getpeercert()
                self.assertEqual(cm.exception.errno, errno.ENOTCONN)

        def test_do_handshake_enotconn(self):
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            przy context.wrap_socket(socket.socket()) jako sock:
                przy self.assertRaises(OSError) jako cm:
                    sock.do_handshake()
                self.assertEqual(cm.exception.errno, errno.ENOTCONN)

        def test_default_ciphers(self):
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            spróbuj:
                # Force a set of weak ciphers on our client context
                context.set_ciphers("DES")
            wyjąwszy ssl.SSLError:
                self.skipTest("no DES cipher available")
            przy ThreadedEchoServer(CERTFILE,
                                    ssl_version=ssl.PROTOCOL_SSLv23,
                                    chatty=Nieprawda) jako server:
                przy context.wrap_socket(socket.socket()) jako s:
                    przy self.assertRaises(OSError):
                        s.connect((HOST, server.port))
            self.assertIn("no shared cipher", str(server.conn_errors[0]))

        def test_version_basic(self):
            """
            Basic tests dla SSLSocket.version().
            More tests are done w the test_protocol_*() methods.
            """
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            przy ThreadedEchoServer(CERTFILE,
                                    ssl_version=ssl.PROTOCOL_TLSv1,
                                    chatty=Nieprawda) jako server:
                przy context.wrap_socket(socket.socket()) jako s:
                    self.assertIs(s.version(), Nic)
                    s.connect((HOST, server.port))
                    self.assertEqual(s.version(), "TLSv1")
                self.assertIs(s.version(), Nic)

        @unittest.skipUnless(ssl.HAS_ECDH, "test requires ECDH-enabled OpenSSL")
        def test_default_ecdh_curve(self):
            # Issue #21015: elliptic curve-based Diffie Hellman key exchange
            # should be enabled by default on SSL contexts.
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.load_cert_chain(CERTFILE)
            # Prior to OpenSSL 1.0.0, ECDH ciphers have to be enabled
            # explicitly using the 'ECCdraft' cipher alias.  Otherwise,
            # our default cipher list should prefer ECDH-based ciphers
            # automatically.
            jeżeli ssl.OPENSSL_VERSION_INFO < (1, 0, 0):
                context.set_ciphers("ECCdraft:ECDH")
            przy ThreadedEchoServer(context=context) jako server:
                przy context.wrap_socket(socket.socket()) jako s:
                    s.connect((HOST, server.port))
                    self.assertIn("ECDH", s.cipher()[0])

        @unittest.skipUnless("tls-unique" w ssl.CHANNEL_BINDING_TYPES,
                             "'tls-unique' channel binding nie available")
        def test_tls_unique_channel_binding(self):
            """Test tls-unique channel binding."""
            jeżeli support.verbose:
                sys.stdout.write("\n")

            server = ThreadedEchoServer(CERTFILE,
                                        certreqs=ssl.CERT_NONE,
                                        ssl_version=ssl.PROTOCOL_TLSv1,
                                        cacerts=CERTFILE,
                                        chatty=Prawda,
                                        connectionchatty=Nieprawda)
            przy server:
                s = ssl.wrap_socket(socket.socket(),
                                    server_side=Nieprawda,
                                    certfile=CERTFILE,
                                    ca_certs=CERTFILE,
                                    cert_reqs=ssl.CERT_NONE,
                                    ssl_version=ssl.PROTOCOL_TLSv1)
                s.connect((HOST, server.port))
                # get the data
                cb_data = s.get_channel_binding("tls-unique")
                jeżeli support.verbose:
                    sys.stdout.write(" got channel binding data: {0!r}\n"
                                     .format(cb_data))

                # check jeżeli it jest sane
                self.assertIsNotNic(cb_data)
                self.assertEqual(len(cb_data), 12) # Prawda dla TLSv1

                # oraz compare przy the peers version
                s.write(b"CB tls-unique\n")
                peer_data_repr = s.read().strip()
                self.assertEqual(peer_data_repr,
                                 repr(cb_data).encode("us-ascii"))
                s.close()

                # now, again
                s = ssl.wrap_socket(socket.socket(),
                                    server_side=Nieprawda,
                                    certfile=CERTFILE,
                                    ca_certs=CERTFILE,
                                    cert_reqs=ssl.CERT_NONE,
                                    ssl_version=ssl.PROTOCOL_TLSv1)
                s.connect((HOST, server.port))
                new_cb_data = s.get_channel_binding("tls-unique")
                jeżeli support.verbose:
                    sys.stdout.write(" got another channel binding data: {0!r}\n"
                                     .format(new_cb_data))
                # jest it really unique
                self.assertNotEqual(cb_data, new_cb_data)
                self.assertIsNotNic(cb_data)
                self.assertEqual(len(cb_data), 12) # Prawda dla TLSv1
                s.write(b"CB tls-unique\n")
                peer_data_repr = s.read().strip()
                self.assertEqual(peer_data_repr,
                                 repr(new_cb_data).encode("us-ascii"))
                s.close()

        def test_compression(self):
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.load_cert_chain(CERTFILE)
            stats = server_params_test(context, context,
                                       chatty=Prawda, connectionchatty=Prawda)
            jeżeli support.verbose:
                sys.stdout.write(" got compression: {!r}\n".format(stats['compression']))
            self.assertIn(stats['compression'], { Nic, 'ZLIB', 'RLE' })

        @unittest.skipUnless(hasattr(ssl, 'OP_NO_COMPRESSION'),
                             "ssl.OP_NO_COMPRESSION needed dla this test")
        def test_compression_disabled(self):
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.load_cert_chain(CERTFILE)
            context.options |= ssl.OP_NO_COMPRESSION
            stats = server_params_test(context, context,
                                       chatty=Prawda, connectionchatty=Prawda)
            self.assertIs(stats['compression'], Nic)

        def test_dh_params(self):
            # Check we can get a connection przy ephemeral Diffie-Hellman
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.load_cert_chain(CERTFILE)
            context.load_dh_params(DHFILE)
            context.set_ciphers("kEDH")
            stats = server_params_test(context, context,
                                       chatty=Prawda, connectionchatty=Prawda)
            cipher = stats["cipher"][0]
            parts = cipher.split("-")
            jeżeli "ADH" nie w parts oraz "EDH" nie w parts oraz "DHE" nie w parts:
                self.fail("Non-DH cipher: " + cipher[0])

        def test_selected_alpn_protocol(self):
            # selected_alpn_protocol() jest Nic unless ALPN jest used.
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.load_cert_chain(CERTFILE)
            stats = server_params_test(context, context,
                                       chatty=Prawda, connectionchatty=Prawda)
            self.assertIs(stats['client_alpn_protocol'], Nic)

        @unittest.skipUnless(ssl.HAS_ALPN, "ALPN support required")
        def test_selected_alpn_protocol_if_server_uses_alpn(self):
            # selected_alpn_protocol() jest Nic unless ALPN jest used by the client.
            client_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            client_context.load_verify_locations(CERTFILE)
            server_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            server_context.load_cert_chain(CERTFILE)
            server_context.set_alpn_protocols(['foo', 'bar'])
            stats = server_params_test(client_context, server_context,
                                       chatty=Prawda, connectionchatty=Prawda)
            self.assertIs(stats['client_alpn_protocol'], Nic)

        @unittest.skipUnless(ssl.HAS_ALPN, "ALPN support needed dla this test")
        def test_alpn_protocols(self):
            server_protocols = ['foo', 'bar', 'milkshake']
            protocol_tests = [
                (['foo', 'bar'], 'foo'),
                (['bar', 'foo'], 'foo'),
                (['milkshake'], 'milkshake'),
                (['http/3.0', 'http/4.0'], Nic)
            ]
            dla client_protocols, expected w protocol_tests:
                server_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                server_context.load_cert_chain(CERTFILE)
                server_context.set_alpn_protocols(server_protocols)
                client_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                client_context.load_cert_chain(CERTFILE)
                client_context.set_alpn_protocols(client_protocols)
                stats = server_params_test(client_context, server_context,
                                           chatty=Prawda, connectionchatty=Prawda)

                msg = "failed trying %s (s) oraz %s (c).\n" \
                      "was expecting %s, but got %%s z the %%s" \
                          % (str(server_protocols), str(client_protocols),
                             str(expected))
                client_result = stats['client_alpn_protocol']
                self.assertEqual(client_result, expected, msg % (client_result, "client"))
                server_result = stats['server_alpn_protocols'][-1] \
                    jeżeli len(stats['server_alpn_protocols']) inaczej 'nothing'
                self.assertEqual(server_result, expected, msg % (server_result, "server"))

        def test_selected_npn_protocol(self):
            # selected_npn_protocol() jest Nic unless NPN jest used
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.load_cert_chain(CERTFILE)
            stats = server_params_test(context, context,
                                       chatty=Prawda, connectionchatty=Prawda)
            self.assertIs(stats['client_npn_protocol'], Nic)

        @unittest.skipUnless(ssl.HAS_NPN, "NPN support needed dla this test")
        def test_npn_protocols(self):
            server_protocols = ['http/1.1', 'spdy/2']
            protocol_tests = [
                (['http/1.1', 'spdy/2'], 'http/1.1'),
                (['spdy/2', 'http/1.1'], 'http/1.1'),
                (['spdy/2', 'test'], 'spdy/2'),
                (['abc', 'def'], 'abc')
            ]
            dla client_protocols, expected w protocol_tests:
                server_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                server_context.load_cert_chain(CERTFILE)
                server_context.set_npn_protocols(server_protocols)
                client_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                client_context.load_cert_chain(CERTFILE)
                client_context.set_npn_protocols(client_protocols)
                stats = server_params_test(client_context, server_context,
                                           chatty=Prawda, connectionchatty=Prawda)

                msg = "failed trying %s (s) oraz %s (c).\n" \
                      "was expecting %s, but got %%s z the %%s" \
                          % (str(server_protocols), str(client_protocols),
                             str(expected))
                client_result = stats['client_npn_protocol']
                self.assertEqual(client_result, expected, msg % (client_result, "client"))
                server_result = stats['server_npn_protocols'][-1] \
                    jeżeli len(stats['server_npn_protocols']) inaczej 'nothing'
                self.assertEqual(server_result, expected, msg % (server_result, "server"))

        def sni_contexts(self):
            server_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            server_context.load_cert_chain(SIGNED_CERTFILE)
            other_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            other_context.load_cert_chain(SIGNED_CERTFILE2)
            client_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            client_context.verify_mode = ssl.CERT_REQUIRED
            client_context.load_verify_locations(SIGNING_CA)
            zwróć server_context, other_context, client_context

        def check_common_name(self, stats, name):
            cert = stats['peercert']
            self.assertIn((('commonName', name),), cert['subject'])

        @needs_sni
        def test_sni_callback(self):
            calls = []
            server_context, other_context, client_context = self.sni_contexts()

            def servername_cb(ssl_sock, server_name, initial_context):
                calls.append((server_name, initial_context))
                jeżeli server_name jest nie Nic:
                    ssl_sock.context = other_context
            server_context.set_servername_callback(servername_cb)

            stats = server_params_test(client_context, server_context,
                                       chatty=Prawda,
                                       sni_name='supermessage')
            # The hostname was fetched properly, oraz the certificate was
            # changed dla the connection.
            self.assertEqual(calls, [("supermessage", server_context)])
            # CERTFILE4 was selected
            self.check_common_name(stats, 'fakehostname')

            calls = []
            # The callback jest called przy server_name=Nic
            stats = server_params_test(client_context, server_context,
                                       chatty=Prawda,
                                       sni_name=Nic)
            self.assertEqual(calls, [(Nic, server_context)])
            self.check_common_name(stats, 'localhost')

            # Check disabling the callback
            calls = []
            server_context.set_servername_callback(Nic)

            stats = server_params_test(client_context, server_context,
                                       chatty=Prawda,
                                       sni_name='notfunny')
            # Certificate didn't change
            self.check_common_name(stats, 'localhost')
            self.assertEqual(calls, [])

        @needs_sni
        def test_sni_callback_alert(self):
            # Returning a TLS alert jest reflected to the connecting client
            server_context, other_context, client_context = self.sni_contexts()

            def cb_returning_alert(ssl_sock, server_name, initial_context):
                zwróć ssl.ALERT_DESCRIPTION_ACCESS_DENIED
            server_context.set_servername_callback(cb_returning_alert)

            przy self.assertRaises(ssl.SSLError) jako cm:
                stats = server_params_test(client_context, server_context,
                                           chatty=Nieprawda,
                                           sni_name='supermessage')
            self.assertEqual(cm.exception.reason, 'TLSV1_ALERT_ACCESS_DENIED')

        @needs_sni
        def test_sni_callback_raising(self):
            # Raising fails the connection przy a TLS handshake failure alert.
            server_context, other_context, client_context = self.sni_contexts()

            def cb_raising(ssl_sock, server_name, initial_context):
                1/0
            server_context.set_servername_callback(cb_raising)

            przy self.assertRaises(ssl.SSLError) jako cm, \
                 support.captured_stderr() jako stderr:
                stats = server_params_test(client_context, server_context,
                                           chatty=Nieprawda,
                                           sni_name='supermessage')
            self.assertEqual(cm.exception.reason, 'SSLV3_ALERT_HANDSHAKE_FAILURE')
            self.assertIn("ZeroDivisionError", stderr.getvalue())

        @needs_sni
        def test_sni_callback_wrong_return_type(self):
            # Returning the wrong zwróć type terminates the TLS connection
            # przy an internal error alert.
            server_context, other_context, client_context = self.sni_contexts()

            def cb_wrong_return_type(ssl_sock, server_name, initial_context):
                zwróć "foo"
            server_context.set_servername_callback(cb_wrong_return_type)

            przy self.assertRaises(ssl.SSLError) jako cm, \
                 support.captured_stderr() jako stderr:
                stats = server_params_test(client_context, server_context,
                                           chatty=Nieprawda,
                                           sni_name='supermessage')
            self.assertEqual(cm.exception.reason, 'TLSV1_ALERT_INTERNAL_ERROR')
            self.assertIn("TypeError", stderr.getvalue())

        def test_shared_ciphers(self):
            server_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            server_context.load_cert_chain(SIGNED_CERTFILE)
            client_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            client_context.verify_mode = ssl.CERT_REQUIRED
            client_context.load_verify_locations(SIGNING_CA)
            client_context.set_ciphers("RC4")
            server_context.set_ciphers("AES:RC4")
            stats = server_params_test(client_context, server_context)
            ciphers = stats['server_shared_ciphers'][0]
            self.assertGreater(len(ciphers), 0)
            dla name, tls_version, bits w ciphers:
                self.assertIn("RC4", name.split("-"))

        def test_read_write_after_close_raises_valuerror(self):
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(CERTFILE)
            context.load_cert_chain(CERTFILE)
            server = ThreadedEchoServer(context=context, chatty=Nieprawda)

            przy server:
                s = context.wrap_socket(socket.socket())
                s.connect((HOST, server.port))
                s.close()

                self.assertRaises(ValueError, s.read, 1024)
                self.assertRaises(ValueError, s.write, b'hello')

        def test_sendfile(self):
            TEST_DATA = b"x" * 512
            przy open(support.TESTFN, 'wb') jako f:
                f.write(TEST_DATA)
            self.addCleanup(support.unlink, support.TESTFN)
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(CERTFILE)
            context.load_cert_chain(CERTFILE)
            server = ThreadedEchoServer(context=context, chatty=Nieprawda)
            przy server:
                przy context.wrap_socket(socket.socket()) jako s:
                    s.connect((HOST, server.port))
                    przy open(support.TESTFN, 'rb') jako file:
                        s.sendfile(file)
                        self.assertEqual(s.recv(1024), TEST_DATA)


def test_main(verbose=Nieprawda):
    jeżeli support.verbose:
        zaimportuj warnings
        plats = {
            'Linux': platform.linux_distribution,
            'Mac': platform.mac_ver,
            'Windows': platform.win32_ver,
        }
        przy warnings.catch_warnings():
            warnings.filterwarnings(
                'ignore',
                'dist\(\) oraz linux_distribution\(\) '
                'functions are deprecated .*',
                PendingDeprecationWarning,
            )
            dla name, func w plats.items():
                plat = func()
                jeżeli plat oraz plat[0]:
                    plat = '%s %r' % (name, plat)
                    przerwij
            inaczej:
                plat = repr(platform.platform())
        print("test_ssl: testing przy %r %r" %
            (ssl.OPENSSL_VERSION, ssl.OPENSSL_VERSION_INFO))
        print("          under %s" % plat)
        print("          HAS_SNI = %r" % ssl.HAS_SNI)
        print("          OP_ALL = 0x%8x" % ssl.OP_ALL)
        spróbuj:
            print("          OP_NO_TLSv1_1 = 0x%8x" % ssl.OP_NO_TLSv1_1)
        wyjąwszy AttributeError:
            dalej

    dla filename w [
        CERTFILE, SVN_PYTHON_ORG_ROOT_CERT, BYTES_CERTFILE,
        ONLYCERT, ONLYKEY, BYTES_ONLYCERT, BYTES_ONLYKEY,
        SIGNED_CERTFILE, SIGNED_CERTFILE2, SIGNING_CA,
        BADCERT, BADKEY, EMPTYCERT]:
        jeżeli nie os.path.exists(filename):
            podnieś support.TestFailed("Can't read certificate file %r" % filename)

    tests = [ContextTests, BasicSocketTests, SSLErrorTests, MemoryBIOTests]

    jeżeli support.is_resource_enabled('network'):
        tests.append(NetworkedTests)
        tests.append(NetworkedBIOTests)

    jeżeli _have_threads:
        thread_info = support.threading_setup()
        jeżeli thread_info:
            tests.append(ThreadedTests)

    spróbuj:
        support.run_unittest(*tests)
    w_końcu:
        jeżeli _have_threads:
            support.threading_cleanup(*thread_info)

jeżeli __name__ == "__main__":
    test_main()
