"""BaseHTTPServer that implements the Python WSGI protocol (PEP 3333)

This jest both an example of how WSGI can be implemented, oraz a basis dla running
simple web applications on a local machine, such jako might be done when testing
or debugging an application.  It has nie been reviewed dla security issues,
however, oraz we strongly recommend that you use a "real" web server for
production use.

For example usage, see the 'jeżeli __name__=="__main__"' block at the end of the
module.  See also the BaseHTTPServer module docs dla other API information.
"""

z http.server zaimportuj BaseHTTPRequestHandler, HTTPServer
zaimportuj sys
zaimportuj urllib.parse
z wsgiref.handlers zaimportuj SimpleHandler
z platform zaimportuj python_implementation

__version__ = "0.2"
__all__ = ['WSGIServer', 'WSGIRequestHandler', 'demo_app', 'make_server']


server_version = "WSGIServer/" + __version__
sys_version = python_implementation() + "/" + sys.version.split()[0]
software_version = server_version + ' ' + sys_version


klasa ServerHandler(SimpleHandler):

    server_software = software_version

    def close(self):
        spróbuj:
            self.request_handler.log_request(
                self.status.split(' ',1)[0], self.bytes_sent
            )
        w_końcu:
            SimpleHandler.close(self)



klasa WSGIServer(HTTPServer):

    """BaseHTTPServer that implements the Python WSGI protocol"""

    application = Nic

    def server_bind(self):
        """Override server_bind to store the server name."""
        HTTPServer.server_bind(self)
        self.setup_environ()

    def setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST']=''
        env['CONTENT_LENGTH']=''
        env['SCRIPT_NAME'] = ''

    def get_app(self):
        zwróć self.application

    def set_app(self,application):
        self.application = application



klasa WSGIRequestHandler(BaseHTTPRequestHandler):

    server_version = "WSGIServer/" + __version__

    def get_environ(self):
        env = self.server.base_environ.copy()
        env['SERVER_PROTOCOL'] = self.request_version
        env['SERVER_SOFTWARE'] = self.server_version
        env['REQUEST_METHOD'] = self.command
        jeżeli '?' w self.path:
            path,query = self.path.split('?',1)
        inaczej:
            path,query = self.path,''

        env['PATH_INFO'] = urllib.parse.unquote_to_bytes(path).decode('iso-8859-1')
        env['QUERY_STRING'] = query

        host = self.address_string()
        jeżeli host != self.client_address[0]:
            env['REMOTE_HOST'] = host
        env['REMOTE_ADDR'] = self.client_address[0]

        jeżeli self.headers.get('content-type') jest Nic:
            env['CONTENT_TYPE'] = self.headers.get_content_type()
        inaczej:
            env['CONTENT_TYPE'] = self.headers['content-type']

        length = self.headers.get('content-length')
        jeżeli length:
            env['CONTENT_LENGTH'] = length

        dla k, v w self.headers.items():
            k=k.replace('-','_').upper(); v=v.strip()
            jeżeli k w env:
                continue                    # skip content length, type,etc.
            jeżeli 'HTTP_'+k w env:
                env['HTTP_'+k] += ','+v     # comma-separate multiple headers
            inaczej:
                env['HTTP_'+k] = v
        zwróć env

    def get_stderr(self):
        zwróć sys.stderr

    def handle(self):
        """Handle a single HTTP request"""

        self.raw_requestline = self.rfile.readline(65537)
        jeżeli len(self.raw_requestline) > 65536:
            self.requestline = ''
            self.request_version = ''
            self.command = ''
            self.send_error(414)
            zwróć

        jeżeli nie self.parse_request(): # An error code has been sent, just exit
            zwróć

        handler = ServerHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ()
        )
        handler.request_handler = self      # backpointer dla logging
        handler.run(self.server.get_app())



def demo_app(environ,start_response):
    z io zaimportuj StringIO
    stdout = StringIO()
    print("Hello world!", file=stdout)
    print(file=stdout)
    h = sorted(environ.items())
    dla k,v w h:
        print(k,'=',repr(v), file=stdout)
    start_response("200 OK", [('Content-Type','text/plain; charset=utf-8')])
    zwróć [stdout.getvalue().encode("utf-8")]


def make_server(
    host, port, app, server_class=WSGIServer, handler_class=WSGIRequestHandler
):
    """Create a new WSGI server listening on `host` oraz `port` dla `app`"""
    server = server_class((host, port), handler_class)
    server.set_app(app)
    zwróć server


jeżeli __name__ == '__main__':
    httpd = make_server('', 8000, demo_app)
    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")
    zaimportuj webbrowser
    webbrowser.open('http://localhost:8000/xyz?abc')
    httpd.handle_request()  # serve one request, then exit
    httpd.server_close()
