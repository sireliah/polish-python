zaimportuj os
zaimportuj sys
zaimportuj ssl
zaimportuj pprint
zaimportuj socket
zaimportuj urllib.parse
# Rename HTTPServer to _HTTPServer so jako to avoid confusion przy HTTPSServer.
z http.server zaimportuj (HTTPServer jako _HTTPServer,
    SimpleHTTPRequestHandler, BaseHTTPRequestHandler)

z test zaimportuj support
threading = support.import_module("threading")

here = os.path.dirname(__file__)

HOST = support.HOST
CERTFILE = os.path.join(here, 'keycert.pem')

# This one's based on HTTPServer, which jest based on SocketServer

klasa HTTPSServer(_HTTPServer):

    def __init__(self, server_address, handler_class, context):
        _HTTPServer.__init__(self, server_address, handler_class)
        self.context = context

    def __str__(self):
        zwróć ('<%s %s:%s>' %
                (self.__class__.__name__,
                 self.server_name,
                 self.server_port))

    def get_request(self):
        # override this to wrap socket przy SSL
        spróbuj:
            sock, addr = self.socket.accept()
            sslconn = self.context.wrap_socket(sock, server_side=Prawda)
        wyjąwszy OSError jako e:
            # socket errors are silenced by the caller, print them here
            jeżeli support.verbose:
                sys.stderr.write("Got an error:\n%s\n" % e)
            podnieś
        zwróć sslconn, addr

klasa RootedHTTPRequestHandler(SimpleHTTPRequestHandler):
    # need to override translate_path to get a known root,
    # instead of using os.curdir, since the test could be
    # run z anywhere

    server_version = "TestHTTPS/1.0"
    root = here
    # Avoid hanging when a request gets interrupted by the client
    timeout = 5

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive albo directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = urllib.parse.urlparse(path)[2]
        path = os.path.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(Nic, words)
        path = self.root
        dla word w words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            path = os.path.join(path, word)
        zwróć path

    def log_message(self, format, *args):
        # we override this to suppress logging unless "verbose"
        jeżeli support.verbose:
            sys.stdout.write(" server (%s:%d %s):\n   [%s] %s\n" %
                             (self.server.server_address,
                              self.server.server_port,
                              self.request.cipher(),
                              self.log_date_time_string(),
                              format%args))


klasa StatsRequestHandler(BaseHTTPRequestHandler):
    """Example HTTP request handler which returns SSL statistics on GET
    requests.
    """

    server_version = "StatsHTTPS/1.0"

    def do_GET(self, send_body=Prawda):
        """Serve a GET request."""
        sock = self.rfile.raw._sock
        context = sock.context
        stats = {
            'session_cache': context.session_stats(),
            'cipher': sock.cipher(),
            'compression': sock.compression(),
            }
        body = pprint.pformat(stats)
        body = body.encode('utf-8')
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        jeżeli send_body:
            self.wfile.write(body)

    def do_HEAD(self):
        """Serve a HEAD request."""
        self.do_GET(send_body=Nieprawda)

    def log_request(self, format, *args):
        jeżeli support.verbose:
            BaseHTTPRequestHandler.log_request(self, format, *args)


klasa HTTPSServerThread(threading.Thread):

    def __init__(self, context, host=HOST, handler_class=Nic):
        self.flag = Nic
        self.server = HTTPSServer((host, 0),
                                  handler_class albo RootedHTTPRequestHandler,
                                  context)
        self.port = self.server.server_port
        threading.Thread.__init__(self)
        self.daemon = Prawda

    def __str__(self):
        zwróć "<%s %s>" % (self.__class__.__name__, self.server)

    def start(self, flag=Nic):
        self.flag = flag
        threading.Thread.start(self)

    def run(self):
        jeżeli self.flag:
            self.flag.set()
        spróbuj:
            self.server.serve_forever(0.05)
        w_końcu:
            self.server.server_close()

    def stop(self):
        self.server.shutdown()


def make_https_server(case, *, context=Nic, certfile=CERTFILE,
                      host=HOST, handler_class=Nic):
    jeżeli context jest Nic:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # We assume the certfile contains both private key oraz certificate
    context.load_cert_chain(certfile)
    server = HTTPSServerThread(context, host, handler_class)
    flag = threading.Event()
    server.start(flag)
    flag.wait()
    def cleanup():
        jeżeli support.verbose:
            sys.stdout.write('stopping HTTPS server\n')
        server.stop()
        jeżeli support.verbose:
            sys.stdout.write('joining HTTPS thread\n')
        server.join()
    case.addCleanup(cleanup)
    zwróć server


jeżeli __name__ == "__main__":
    zaimportuj argparse
    parser = argparse.ArgumentParser(
        description='Run a test HTTPS server. '
                    'By default, the current directory jest served.')
    parser.add_argument('-p', '--port', type=int, default=4433,
                        help='port to listen on (default: %(default)s)')
    parser.add_argument('-q', '--quiet', dest='verbose', default=Prawda,
                        action='store_false', help='be less verbose')
    parser.add_argument('-s', '--stats', dest='use_stats_handler', default=Nieprawda,
                        action='store_true', help='always zwróć stats page')
    parser.add_argument('--curve-name', dest='curve_name', type=str,
                        action='store',
                        help='curve name dla EC-based Diffie-Hellman')
    parser.add_argument('--ciphers', dest='ciphers', type=str,
                        help='allowed cipher list')
    parser.add_argument('--dh', dest='dh_file', type=str, action='store',
                        help='PEM file containing DH parameters')
    args = parser.parse_args()

    support.verbose = args.verbose
    jeżeli args.use_stats_handler:
        handler_class = StatsRequestHandler
    inaczej:
        handler_class = RootedHTTPRequestHandler
        handler_class.root = os.getcwd()
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(CERTFILE)
    jeżeli args.curve_name:
        context.set_ecdh_curve(args.curve_name)
    jeżeli args.dh_file:
        context.load_dh_params(args.dh_file)
    jeżeli args.ciphers:
        context.set_ciphers(args.ciphers)

    server = HTTPSServer(("", args.port), handler_class, context)
    jeżeli args.verbose:
        print("Listening on https://localhost:{0.port}".format(args))
    server.serve_forever(0.1)
