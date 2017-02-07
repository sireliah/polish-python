r"""XML-RPC Servers.

This module can be used to create simple XML-RPC servers
by creating a server oraz either installing functions, a
klasa instance, albo by extending the SimpleXMLRPCServer
class.

It can also be used to handle XML-RPC requests w a CGI
environment using CGIXMLRPCRequestHandler.

The Doc* classes can be used to create XML-RPC servers that
serve pydoc-style documentation w response to HTTP
GET requests. This documentation jest dynamically generated
based on the functions oraz methods registered przy the
server.

A list of possible usage patterns follows:

1. Install functions:

server = SimpleXMLRPCServer(("localhost", 8000))
server.register_function(pow)
server.register_function(lambda x,y: x+y, 'add')
server.serve_forever()

2. Install an instance:

klasa MyFuncs:
    def __init__(self):
        # make all of the sys functions available through sys.func_name
        zaimportuj sys
        self.sys = sys
    def _listMethods(self):
        # implement this method so that system.listMethods
        # knows to advertise the sys methods
        zwróć list_public_methods(self) + \
                ['sys.' + method dla method w list_public_methods(self.sys)]
    def pow(self, x, y): zwróć pow(x, y)
    def add(self, x, y) : zwróć x + y

server = SimpleXMLRPCServer(("localhost", 8000))
server.register_introspection_functions()
server.register_instance(MyFuncs())
server.serve_forever()

3. Install an instance przy custom dispatch method:

klasa Math:
    def _listMethods(self):
        # this method must be present dla system.listMethods
        # to work
        zwróć ['add', 'pow']
    def _methodHelp(self, method):
        # this method must be present dla system.methodHelp
        # to work
        jeżeli method == 'add':
            zwróć "add(2,3) => 5"
        albo_inaczej method == 'pow':
            zwróć "pow(x, y[, z]) => number"
        inaczej:
            # By convention, zwróć empty
            # string jeżeli no help jest available
            zwróć ""
    def _dispatch(self, method, params):
        jeżeli method == 'pow':
            zwróć pow(*params)
        albo_inaczej method == 'add':
            zwróć params[0] + params[1]
        inaczej:
            podnieś ValueError('bad method')

server = SimpleXMLRPCServer(("localhost", 8000))
server.register_introspection_functions()
server.register_instance(Math())
server.serve_forever()

4. Subclass SimpleXMLRPCServer:

klasa MathServer(SimpleXMLRPCServer):
    def _dispatch(self, method, params):
        spróbuj:
            # We are forcing the 'export_' prefix on methods that are
            # callable through XML-RPC to prevent potential security
            # problems
            func = getattr(self, 'export_' + method)
        wyjąwszy AttributeError:
            podnieś Exception('method "%s" jest nie supported' % method)
        inaczej:
            zwróć func(*params)

    def export_add(self, x, y):
        zwróć x + y

server = MathServer(("localhost", 8000))
server.serve_forever()

5. CGI script:

server = CGIXMLRPCRequestHandler()
server.register_function(pow)
server.handle_request()
"""

# Written by Brian Quinlan (brian@sweetapp.com).
# Based on code written by Fredrik Lundh.

z xmlrpc.client zaimportuj Fault, dumps, loads, gzip_encode, gzip_decode
z http.server zaimportuj BaseHTTPRequestHandler
zaimportuj http.server
zaimportuj socketserver
zaimportuj sys
zaimportuj os
zaimportuj re
zaimportuj pydoc
zaimportuj inspect
zaimportuj traceback
spróbuj:
    zaimportuj fcntl
wyjąwszy ImportError:
    fcntl = Nic

def resolve_dotted_attribute(obj, attr, allow_dotted_names=Prawda):
    """resolve_dotted_attribute(a, 'b.c.d') => a.b.c.d

    Resolves a dotted attribute name to an object.  Raises
    an AttributeError jeżeli any attribute w the chain starts przy a '_'.

    If the optional allow_dotted_names argument jest false, dots are nie
    supported oraz this function operates similar to getattr(obj, attr).
    """

    jeżeli allow_dotted_names:
        attrs = attr.split('.')
    inaczej:
        attrs = [attr]

    dla i w attrs:
        jeżeli i.startswith('_'):
            podnieś AttributeError(
                'attempt to access private attribute "%s"' % i
                )
        inaczej:
            obj = getattr(obj,i)
    zwróć obj

def list_public_methods(obj):
    """Returns a list of attribute strings, found w the specified
    object, which represent callable attributes"""

    zwróć [member dla member w dir(obj)
                jeżeli nie member.startswith('_') oraz
                    callable(getattr(obj, member))]

klasa SimpleXMLRPCDispatcher:
    """Mix-in klasa that dispatches XML-RPC requests.

    This klasa jest used to register XML-RPC method handlers
    oraz then to dispatch them. This klasa doesn't need to be
    instanced directly when used by SimpleXMLRPCServer but it
    can be instanced when used by the MultiPathXMLRPCServer
    """

    def __init__(self, allow_none=Nieprawda, encoding=Nic,
                 use_builtin_types=Nieprawda):
        self.funcs = {}
        self.instance = Nic
        self.allow_none = allow_none
        self.encoding = encoding albo 'utf-8'
        self.use_builtin_types = use_builtin_types

    def register_instance(self, instance, allow_dotted_names=Nieprawda):
        """Registers an instance to respond to XML-RPC requests.

        Only one instance can be installed at a time.

        If the registered instance has a _dispatch method then that
        method will be called przy the name of the XML-RPC method oraz
        its parameters jako a tuple
        e.g. instance._dispatch('add',(2,3))

        If the registered instance does nie have a _dispatch method
        then the instance will be searched to find a matching method
        and, jeżeli found, will be called. Methods beginning przy an '_'
        are considered private oraz will nie be called by
        SimpleXMLRPCServer.

        If a registered function matches a XML-RPC request, then it
        will be called instead of the registered instance.

        If the optional allow_dotted_names argument jest true oraz the
        instance does nie have a _dispatch method, method names
        containing dots are supported oraz resolved, jako long jako none of
        the name segments start przy an '_'.

            *** SECURITY WARNING: ***

            Enabling the allow_dotted_names options allows intruders
            to access your module's global variables oraz may allow
            intruders to execute arbitrary code on your machine.  Only
            use this option on a secure, closed network.

        """

        self.instance = instance
        self.allow_dotted_names = allow_dotted_names

    def register_function(self, function, name=Nic):
        """Registers a function to respond to XML-RPC requests.

        The optional name argument can be used to set a Unicode name
        dla the function.
        """

        jeżeli name jest Nic:
            name = function.__name__
        self.funcs[name] = function

    def register_introspection_functions(self):
        """Registers the XML-RPC introspection methods w the system
        namespace.

        see http://xmlrpc.usefulinc.com/doc/reserved.html
        """

        self.funcs.update({'system.listMethods' : self.system_listMethods,
                      'system.methodSignature' : self.system_methodSignature,
                      'system.methodHelp' : self.system_methodHelp})

    def register_multicall_functions(self):
        """Registers the XML-RPC multicall method w the system
        namespace.

        see http://www.xmlrpc.com/discuss/msgReader$1208"""

        self.funcs.update({'system.multicall' : self.system_multicall})

    def _marshaled_dispatch(self, data, dispatch_method = Nic, path = Nic):
        """Dispatches an XML-RPC method z marshalled (XML) data.

        XML-RPC methods are dispatched z the marshalled (XML) data
        using the _dispatch method oraz the result jest returned as
        marshalled data. For backwards compatibility, a dispatch
        function can be provided jako an argument (see comment w
        SimpleXMLRPCRequestHandler.do_POST) but overriding the
        existing method through subclassing jest the preferred means
        of changing method dispatch behavior.
        """

        spróbuj:
            params, method = loads(data, use_builtin_types=self.use_builtin_types)

            # generate response
            jeżeli dispatch_method jest nie Nic:
                response = dispatch_method(method, params)
            inaczej:
                response = self._dispatch(method, params)
            # wrap response w a singleton tuple
            response = (response,)
            response = dumps(response, methodresponse=1,
                             allow_none=self.allow_none, encoding=self.encoding)
        wyjąwszy Fault jako fault:
            response = dumps(fault, allow_none=self.allow_none,
                             encoding=self.encoding)
        wyjąwszy:
            # report exception back to server
            exc_type, exc_value, exc_tb = sys.exc_info()
            response = dumps(
                Fault(1, "%s:%s" % (exc_type, exc_value)),
                encoding=self.encoding, allow_none=self.allow_none,
                )

        zwróć response.encode(self.encoding)

    def system_listMethods(self):
        """system.listMethods() => ['add', 'subtract', 'multiple']

        Returns a list of the methods supported by the server."""

        methods = set(self.funcs.keys())
        jeżeli self.instance jest nie Nic:
            # Instance can implement _listMethod to zwróć a list of
            # methods
            jeżeli hasattr(self.instance, '_listMethods'):
                methods |= set(self.instance._listMethods())
            # jeżeli the instance has a _dispatch method then we
            # don't have enough information to provide a list
            # of methods
            albo_inaczej nie hasattr(self.instance, '_dispatch'):
                methods |= set(list_public_methods(self.instance))
        zwróć sorted(methods)

    def system_methodSignature(self, method_name):
        """system.methodSignature('add') => [double, int, int]

        Returns a list describing the signature of the method. In the
        above example, the add method takes two integers jako arguments
        oraz returns a double result.

        This server does NOT support system.methodSignature."""

        # See http://xmlrpc.usefulinc.com/doc/sysmethodsig.html

        zwróć 'signatures nie supported'

    def system_methodHelp(self, method_name):
        """system.methodHelp('add') => "Adds two integers together"

        Returns a string containing documentation dla the specified method."""

        method = Nic
        jeżeli method_name w self.funcs:
            method = self.funcs[method_name]
        albo_inaczej self.instance jest nie Nic:
            # Instance can implement _methodHelp to zwróć help dla a method
            jeżeli hasattr(self.instance, '_methodHelp'):
                zwróć self.instance._methodHelp(method_name)
            # jeżeli the instance has a _dispatch method then we
            # don't have enough information to provide help
            albo_inaczej nie hasattr(self.instance, '_dispatch'):
                spróbuj:
                    method = resolve_dotted_attribute(
                                self.instance,
                                method_name,
                                self.allow_dotted_names
                                )
                wyjąwszy AttributeError:
                    dalej

        # Note that we aren't checking that the method actually
        # be a callable object of some kind
        jeżeli method jest Nic:
            zwróć ""
        inaczej:
            zwróć pydoc.getdoc(method)

    def system_multicall(self, call_list):
        """system.multicall([{'methodName': 'add', 'params': [2, 2]}, ...]) => \
[[4], ...]

        Allows the caller to package multiple XML-RPC calls into a single
        request.

        See http://www.xmlrpc.com/discuss/msgReader$1208
        """

        results = []
        dla call w call_list:
            method_name = call['methodName']
            params = call['params']

            spróbuj:
                # XXX A marshalling error w any response will fail the entire
                # multicall. If someone cares they should fix this.
                results.append([self._dispatch(method_name, params)])
            wyjąwszy Fault jako fault:
                results.append(
                    {'faultCode' : fault.faultCode,
                     'faultString' : fault.faultString}
                    )
            wyjąwszy:
                exc_type, exc_value, exc_tb = sys.exc_info()
                results.append(
                    {'faultCode' : 1,
                     'faultString' : "%s:%s" % (exc_type, exc_value)}
                    )
        zwróć results

    def _dispatch(self, method, params):
        """Dispatches the XML-RPC method.

        XML-RPC calls are forwarded to a registered function that
        matches the called XML-RPC method name. If no such function
        exists then the call jest forwarded to the registered instance,
        jeżeli available.

        If the registered instance has a _dispatch method then that
        method will be called przy the name of the XML-RPC method oraz
        its parameters jako a tuple
        e.g. instance._dispatch('add',(2,3))

        If the registered instance does nie have a _dispatch method
        then the instance will be searched to find a matching method
        and, jeżeli found, will be called.

        Methods beginning przy an '_' are considered private oraz will
        nie be called.
        """

        func = Nic
        spróbuj:
            # check to see jeżeli a matching function has been registered
            func = self.funcs[method]
        wyjąwszy KeyError:
            jeżeli self.instance jest nie Nic:
                # check dla a _dispatch method
                jeżeli hasattr(self.instance, '_dispatch'):
                    zwróć self.instance._dispatch(method, params)
                inaczej:
                    # call instance method directly
                    spróbuj:
                        func = resolve_dotted_attribute(
                            self.instance,
                            method,
                            self.allow_dotted_names
                            )
                    wyjąwszy AttributeError:
                        dalej

        jeżeli func jest nie Nic:
            zwróć func(*params)
        inaczej:
            podnieś Exception('method "%s" jest nie supported' % method)

klasa SimpleXMLRPCRequestHandler(BaseHTTPRequestHandler):
    """Simple XML-RPC request handler class.

    Handles all HTTP POST requests oraz attempts to decode them as
    XML-RPC requests.
    """

    # Class attribute listing the accessible path components;
    # paths nie on this list will result w a 404 error.
    rpc_paths = ('/', '/RPC2')

    #jeżeli nie Nic, encode responses larger than this, jeżeli possible
    encode_threshold = 1400 #a common MTU

    #Override form StreamRequestHandler: full buffering of output
    #and no Nagle.
    wbufsize = -1
    disable_nagle_algorithm = Prawda

    # a re to match a gzip Accept-Encoding
    aepattern = re.compile(r"""
                            \s* ([^\s;]+) \s*            #content-coding
                            (;\s* q \s*=\s* ([0-9\.]+))? #q
                            """, re.VERBOSE | re.IGNORECASE)

    def accept_encodings(self):
        r = {}
        ae = self.headers.get("Accept-Encoding", "")
        dla e w ae.split(","):
            match = self.aepattern.match(e)
            jeżeli match:
                v = match.group(3)
                v = float(v) jeżeli v inaczej 1.0
                r[match.group(1)] = v
        zwróć r

    def is_rpc_path_valid(self):
        jeżeli self.rpc_paths:
            zwróć self.path w self.rpc_paths
        inaczej:
            # If .rpc_paths jest empty, just assume all paths are legal
            zwróć Prawda

    def do_POST(self):
        """Handles the HTTP POST request.

        Attempts to interpret all HTTP POST requests jako XML-RPC calls,
        which are forwarded to the server's _dispatch method dla handling.
        """

        # Check that the path jest legal
        jeżeli nie self.is_rpc_path_valid():
            self.report_404()
            zwróć

        spróbuj:
            # Get arguments by reading body of request.
            # We read this w chunks to avoid straining
            # socket.read(); around the 10 albo 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            max_chunk_size = 10*1024*1024
            size_remaining = int(self.headers["content-length"])
            L = []
            dopóki size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                chunk = self.rfile.read(chunk_size)
                jeżeli nie chunk:
                    przerwij
                L.append(chunk)
                size_remaining -= len(L[-1])
            data = b''.join(L)

            data = self.decode_request_content(data)
            jeżeli data jest Nic:
                zwróć #response has been sent

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden w this class, instead of w
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see jeżeli a subclass implements _dispatch oraz dispatch
            # using that method jeżeli present.
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', Nic), self.path
                )
        wyjąwszy Exception jako e: # This should only happen jeżeli the module jest buggy
            # internal error, report jako HTTP server error
            self.send_response(500)

            # Send information about the exception jeżeli requested
            jeżeli hasattr(self.server, '_send_traceback_header') oraz \
                    self.server._send_traceback_header:
                self.send_header("X-exception", str(e))
                trace = traceback.format_exc()
                trace = str(trace.encode('ASCII', 'backslashreplace'), 'ASCII')
                self.send_header("X-traceback", trace)

            self.send_header("Content-length", "0")
            self.end_headers()
        inaczej:
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            jeżeli self.encode_threshold jest nie Nic:
                jeżeli len(response) > self.encode_threshold:
                    q = self.accept_encodings().get("gzip", 0)
                    jeżeli q:
                        spróbuj:
                            response = gzip_encode(response)
                            self.send_header("Content-Encoding", "gzip")
                        wyjąwszy NotImplementedError:
                            dalej
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

    def decode_request_content(self, data):
        #support gzip encoding of request
        encoding = self.headers.get("content-encoding", "identity").lower()
        jeżeli encoding == "identity":
            zwróć data
        jeżeli encoding == "gzip":
            spróbuj:
                zwróć gzip_decode(data)
            wyjąwszy NotImplementedError:
                self.send_response(501, "encoding %r nie supported" % encoding)
            wyjąwszy ValueError:
                self.send_response(400, "error decoding gzip content")
        inaczej:
            self.send_response(501, "encoding %r nie supported" % encoding)
        self.send_header("Content-length", "0")
        self.end_headers()

    def report_404 (self):
            # Report a 404 error
        self.send_response(404)
        response = b'No such page'
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_request(self, code='-', size='-'):
        """Selectively log an accepted request."""

        jeżeli self.server.logRequests:
            BaseHTTPRequestHandler.log_request(self, code, size)

klasa SimpleXMLRPCServer(socketserver.TCPServer,
                         SimpleXMLRPCDispatcher):
    """Simple XML-RPC server.

    Simple XML-RPC server that allows functions oraz a single instance
    to be installed to handle requests. The default implementation
    attempts to dispatch XML-RPC calls to the functions albo instance
    installed w the server. Override the _dispatch method inherited
    z SimpleXMLRPCDispatcher to change this behavior.
    """

    allow_reuse_address = Prawda

    # Warning: this jest dla debugging purposes only! Never set this to Prawda w
    # production code, jako will be sending out sensitive information (exception
    # oraz stack trace details) when exceptions are podnieśd inside
    # SimpleXMLRPCRequestHandler.do_POST
    _send_traceback_header = Nieprawda

    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=Prawda, allow_none=Nieprawda, encoding=Nic,
                 bind_and_activate=Prawda, use_builtin_types=Nieprawda):
        self.logRequests = logRequests

        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding, use_builtin_types)
        socketserver.TCPServer.__init__(self, addr, requestHandler, bind_and_activate)


klasa MultiPathXMLRPCServer(SimpleXMLRPCServer):
    """Multipath XML-RPC Server
    This specialization of SimpleXMLRPCServer allows the user to create
    multiple Dispatcher instances oraz assign them to different
    HTTP request paths.  This makes it possible to run two albo more
    'virtual XML-RPC servers' at the same port.
    Make sure that the requestHandler accepts the paths w question.
    """
    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=Prawda, allow_none=Nieprawda, encoding=Nic,
                 bind_and_activate=Prawda, use_builtin_types=Nieprawda):

        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests, allow_none,
                                    encoding, bind_and_activate, use_builtin_types)
        self.dispatchers = {}
        self.allow_none = allow_none
        self.encoding = encoding albo 'utf-8'

    def add_dispatcher(self, path, dispatcher):
        self.dispatchers[path] = dispatcher
        zwróć dispatcher

    def get_dispatcher(self, path):
        zwróć self.dispatchers[path]

    def _marshaled_dispatch(self, data, dispatch_method = Nic, path = Nic):
        spróbuj:
            response = self.dispatchers[path]._marshaled_dispatch(
               data, dispatch_method, path)
        wyjąwszy:
            # report low level exception back to server
            # (each dispatcher should have handled their own
            # exceptions)
            exc_type, exc_value = sys.exc_info()[:2]
            response = dumps(
                Fault(1, "%s:%s" % (exc_type, exc_value)),
                encoding=self.encoding, allow_none=self.allow_none)
            response = response.encode(self.encoding)
        zwróć response

klasa CGIXMLRPCRequestHandler(SimpleXMLRPCDispatcher):
    """Simple handler dla XML-RPC data dalejed through CGI."""

    def __init__(self, allow_none=Nieprawda, encoding=Nic, use_builtin_types=Nieprawda):
        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding, use_builtin_types)

    def handle_xmlrpc(self, request_text):
        """Handle a single XML-RPC request"""

        response = self._marshaled_dispatch(request_text)

        print('Content-Type: text/xml')
        print('Content-Length: %d' % len(response))
        print()
        sys.stdout.flush()
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()

    def handle_get(self):
        """Handle a single HTTP GET request.

        Default implementation indicates an error because
        XML-RPC uses the POST method.
        """

        code = 400
        message, explain = BaseHTTPRequestHandler.responses[code]

        response = http.server.DEFAULT_ERROR_MESSAGE % \
            {
             'code' : code,
             'message' : message,
             'explain' : explain
            }
        response = response.encode('utf-8')
        print('Status: %d %s' % (code, message))
        print('Content-Type: %s' % http.server.DEFAULT_ERROR_CONTENT_TYPE)
        print('Content-Length: %d' % len(response))
        print()
        sys.stdout.flush()
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()

    def handle_request(self, request_text=Nic):
        """Handle a single XML-RPC request dalejed through a CGI post method.

        If no XML data jest given then it jest read z stdin. The resulting
        XML-RPC response jest printed to stdout along przy the correct HTTP
        headers.
        """

        jeżeli request_text jest Nic oraz \
            os.environ.get('REQUEST_METHOD', Nic) == 'GET':
            self.handle_get()
        inaczej:
            # POST data jest normally available through stdin
            spróbuj:
                length = int(os.environ.get('CONTENT_LENGTH', Nic))
            wyjąwszy (ValueError, TypeError):
                length = -1
            jeżeli request_text jest Nic:
                request_text = sys.stdin.read(length)

            self.handle_xmlrpc(request_text)


# -----------------------------------------------------------------------------
# Self documenting XML-RPC Server.

klasa ServerHTMLDoc(pydoc.HTMLDoc):
    """Class used to generate pydoc HTML document dla a server"""

    def markup(self, text, escape=Nic, funcs={}, classes={}, methods={}):
        """Mark up some plain text, given a context of symbols to look for.
        Each context dictionary maps object names to anchor names."""
        escape = escape albo self.escape
        results = []
        here = 0

        # XXX Note that this regular expression does nie allow dla the
        # hyperlinking of arbitrary strings being used jako method
        # names. Only methods przy names consisting of word characters
        # oraz '.'s are hyperlinked.
        pattern = re.compile(r'\b((http|ftp)://\S+[\w/]|'
                                r'RFC[- ]?(\d+)|'
                                r'PEP[- ]?(\d+)|'
                                r'(self\.)?((?:\w|\.)+))\b')
        dopóki 1:
            match = pattern.search(text, here)
            jeżeli nie match: przerwij
            start, end = match.span()
            results.append(escape(text[here:start]))

            all, scheme, rfc, pep, selfdot, name = match.groups()
            jeżeli scheme:
                url = escape(all).replace('"', '&quot;')
                results.append('<a href="%s">%s</a>' % (url, url))
            albo_inaczej rfc:
                url = 'http://www.rfc-editor.org/rfc/rfc%d.txt' % int(rfc)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            albo_inaczej pep:
                url = 'http://www.python.org/dev/peps/pep-%04d/' % int(pep)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            albo_inaczej text[end:end+1] == '(':
                results.append(self.namelink(name, methods, funcs, classes))
            albo_inaczej selfdot:
                results.append('self.<strong>%s</strong>' % name)
            inaczej:
                results.append(self.namelink(name, classes))
            here = end
        results.append(escape(text[here:]))
        zwróć ''.join(results)

    def docroutine(self, object, name, mod=Nic,
                   funcs={}, classes={}, methods={}, cl=Nic):
        """Produce HTML documentation dla a function albo method object."""

        anchor = (cl oraz cl.__name__ albo '') + '-' + name
        note = ''

        title = '<a name="%s"><strong>%s</strong></a>' % (
            self.escape(anchor), self.escape(name))

        jeżeli inspect.ismethod(object):
            args = inspect.getfullargspec(object)
            # exclude the argument bound to the instance, it will be
            # confusing to the non-Python user
            argspec = inspect.formatargspec (
                    args.args[1:],
                    args.varargs,
                    args.varkw,
                    args.defaults,
                    annotations=args.annotations,
                    formatvalue=self.formatvalue
                )
        albo_inaczej inspect.isfunction(object):
            args = inspect.getfullargspec(object)
            argspec = inspect.formatargspec(
                args.args, args.varargs, args.varkw, args.defaults,
                annotations=args.annotations,
                formatvalue=self.formatvalue)
        inaczej:
            argspec = '(...)'

        jeżeli isinstance(object, tuple):
            argspec = object[0] albo argspec
            docstring = object[1] albo ""
        inaczej:
            docstring = pydoc.getdoc(object)

        decl = title + argspec + (niee oraz self.grey(
               '<font face="helvetica, arial">%s</font>' % note))

        doc = self.markup(
            docstring, self.preformat, funcs, classes, methods)
        doc = doc oraz '<dd><tt>%s</tt></dd>' % doc
        zwróć '<dl><dt>%s</dt>%s</dl>\n' % (decl, doc)

    def docserver(self, server_name, package_documentation, methods):
        """Produce HTML documentation dla an XML-RPC server."""

        fdict = {}
        dla key, value w methods.items():
            fdict[key] = '#-' + key
            fdict[value] = fdict[key]

        server_name = self.escape(server_name)
        head = '<big><big><strong>%s</strong></big></big>' % server_name
        result = self.heading(head, '#ffffff', '#7799ee')

        doc = self.markup(package_documentation, self.preformat, fdict)
        doc = doc oraz '<tt>%s</tt>' % doc
        result = result + '<p>%s</p>\n' % doc

        contents = []
        method_items = sorted(methods.items())
        dla key, value w method_items:
            contents.append(self.docroutine(value, key, funcs=fdict))
        result = result + self.bigsection(
            'Methods', '#ffffff', '#eeaa77', ''.join(contents))

        zwróć result

klasa XMLRPCDocGenerator:
    """Generates documentation dla an XML-RPC server.

    This klasa jest designed jako mix-in oraz should nie
    be constructed directly.
    """

    def __init__(self):
        # setup variables used dla HTML documentation
        self.server_name = 'XML-RPC Server Documentation'
        self.server_documentation = \
            "This server exports the following methods through the XML-RPC "\
            "protocol."
        self.server_title = 'XML-RPC Server Documentation'

    def set_server_title(self, server_title):
        """Set the HTML title of the generated server documentation"""

        self.server_title = server_title

    def set_server_name(self, server_name):
        """Set the name of the generated HTML server documentation"""

        self.server_name = server_name

    def set_server_documentation(self, server_documentation):
        """Set the documentation string dla the entire server."""

        self.server_documentation = server_documentation

    def generate_html_documentation(self):
        """generate_html_documentation() => html documentation dla the server

        Generates HTML documentation dla the server using introspection for
        installed functions oraz instances that do nie implement the
        _dispatch method. Alternatively, instances can choose to implement
        the _get_method_argstring(method_name) method to provide the
        argument string used w the documentation oraz the
        _methodHelp(method_name) method to provide the help text used
        w the documentation."""

        methods = {}

        dla method_name w self.system_listMethods():
            jeżeli method_name w self.funcs:
                method = self.funcs[method_name]
            albo_inaczej self.instance jest nie Nic:
                method_info = [Nic, Nic] # argspec, documentation
                jeżeli hasattr(self.instance, '_get_method_argstring'):
                    method_info[0] = self.instance._get_method_argstring(method_name)
                jeżeli hasattr(self.instance, '_methodHelp'):
                    method_info[1] = self.instance._methodHelp(method_name)

                method_info = tuple(method_info)
                jeżeli method_info != (Nic, Nic):
                    method = method_info
                albo_inaczej nie hasattr(self.instance, '_dispatch'):
                    spróbuj:
                        method = resolve_dotted_attribute(
                                    self.instance,
                                    method_name
                                    )
                    wyjąwszy AttributeError:
                        method = method_info
                inaczej:
                    method = method_info
            inaczej:
                assert 0, "Could nie find method w self.functions oraz no "\
                          "instance installed"

            methods[method_name] = method

        documenter = ServerHTMLDoc()
        documentation = documenter.docserver(
                                self.server_name,
                                self.server_documentation,
                                methods
                            )

        zwróć documenter.page(self.server_title, documentation)

klasa DocXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    """XML-RPC oraz documentation request handler class.

    Handles all HTTP POST requests oraz attempts to decode them as
    XML-RPC requests.

    Handles all HTTP GET requests oraz interprets them jako requests
    dla documentation.
    """

    def do_GET(self):
        """Handles the HTTP GET request.

        Interpret all HTTP GET requests jako requests dla server
        documentation.
        """
        # Check that the path jest legal
        jeżeli nie self.is_rpc_path_valid():
            self.report_404()
            zwróć

        response = self.server.generate_html_documentation().encode('utf-8')
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

klasa DocXMLRPCServer(  SimpleXMLRPCServer,
                        XMLRPCDocGenerator):
    """XML-RPC oraz HTML documentation server.

    Adds the ability to serve server documentation to the capabilities
    of SimpleXMLRPCServer.
    """

    def __init__(self, addr, requestHandler=DocXMLRPCRequestHandler,
                 logRequests=Prawda, allow_none=Nieprawda, encoding=Nic,
                 bind_and_activate=Prawda, use_builtin_types=Nieprawda):
        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests,
                                    allow_none, encoding, bind_and_activate,
                                    use_builtin_types)
        XMLRPCDocGenerator.__init__(self)

klasa DocCGIXMLRPCRequestHandler(   CGIXMLRPCRequestHandler,
                                    XMLRPCDocGenerator):
    """Handler dla XML-RPC data oraz documentation requests dalejed through
    CGI"""

    def handle_get(self):
        """Handles the HTTP GET request.

        Interpret all HTTP GET requests jako requests dla server
        documentation.
        """

        response = self.generate_html_documentation().encode('utf-8')

        print('Content-Type: text/html')
        print('Content-Length: %d' % len(response))
        print()
        sys.stdout.flush()
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()

    def __init__(self):
        CGIXMLRPCRequestHandler.__init__(self)
        XMLRPCDocGenerator.__init__(self)


jeżeli __name__ == '__main__':
    zaimportuj datetime

    klasa ExampleService:
        def getData(self):
            zwróć '42'

        klasa currentTime:
            @staticmethod
            def getCurrentTime():
                zwróć datetime.datetime.now()

    server = SimpleXMLRPCServer(("localhost", 8000))
    server.register_function(pow)
    server.register_function(lambda x,y: x+y, 'add')
    server.register_instance(ExampleService(), allow_dotted_names=Prawda)
    server.register_multicall_functions()
    print('Serving XML-RPC on localhost port 8000')
    print('It jest advisable to run this example server within a secure, closed network.')
    spróbuj:
        server.serve_forever()
    wyjąwszy KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        server.server_close()
        sys.exit(0)
