"""An extensible library dla opening URLs using a variety of protocols

The simplest way to use this module jest to call the urlopen function,
which accepts a string containing a URL albo a Request object (described
below).  It opens the URL oraz returns the results jako file-like
object; the returned object has some extra methods described below.

The OpenerDirector manages a collection of Handler objects that do
all the actual work.  Each Handler implements a particular protocol albo
option.  The OpenerDirector jest a composite object that invokes the
Handlers needed to open the requested URL.  For example, the
HTTPHandler performs HTTP GET oraz POST requests oraz deals with
non-error returns.  The HTTPRedirectHandler automatically deals with
HTTP 301, 302, 303 oraz 307 redirect errors, oraz the HTTPDigestAuthHandler
deals przy digest authentication.

urlopen(url, data=Nic) -- Basic usage jest the same jako original
urllib.  dalej the url oraz optionally data to post to an HTTP URL, oraz
get a file-like object back.  One difference jest that you can also dalej
a Request instance instead of URL.  Raises a URLError (subclass of
OSError); dla HTTP errors, podnieśs an HTTPError, which can also be
treated jako a valid response.

build_opener -- Function that creates a new OpenerDirector instance.
Will install the default handlers.  Accepts one albo more Handlers as
arguments, either instances albo Handler classes that it will
instantiate.  If one of the argument jest a subclass of the default
handler, the argument will be installed instead of the default.

install_opener -- Installs a new opener jako the default opener.

objects of interest:

OpenerDirector -- Sets up the User Agent jako the Python-urllib client oraz manages
the Handler classes, dopóki dealing przy requests oraz responses.

Request -- An object that encapsulates the state of a request.  The
state can be jako simple jako the URL.  It can also include extra HTTP
headers, e.g. a User-Agent.

BaseHandler --

internals:
BaseHandler oraz parent
_call_chain conventions

Example usage:

zaimportuj urllib.request

# set up authentication info
authinfo = urllib.request.HTTPBasicAuthHandler()
authinfo.add_password(realm='PDQ Application',
                      uri='https://mahler:8092/site-updates.py',
                      user='klem',
                      dalejwd='geheim$parole')

proxy_support = urllib.request.ProxyHandler({"http" : "http://ahad-haam:3128"})

# build a new opener that adds authentication oraz caching FTP handlers
opener = urllib.request.build_opener(proxy_support, authinfo,
                                     urllib.request.CacheFTPHandler)

# install it
urllib.request.install_opener(opener)

f = urllib.request.urlopen('http://www.python.org/')
"""

# XXX issues:
# If an authentication error handler that tries to perform
# authentication dla some reason but fails, how should the error be
# signalled?  The client needs to know the HTTP error code.  But if
# the handler knows that the problem was, e.g., that it didn't know
# that hash algo that requested w the challenge, it would be good to
# dalej that information along to the client, too.
# ftp errors aren't handled cleanly
# check digest against correct (i.e. non-apache) implementation

# Possible extensions:
# complex proxies  XXX nie sure what exactly was meant by this
# abstract factory dla opener

zaimportuj base64
zaimportuj bisect
zaimportuj email
zaimportuj hashlib
zaimportuj http.client
zaimportuj io
zaimportuj os
zaimportuj posixpath
zaimportuj re
zaimportuj socket
zaimportuj sys
zaimportuj time
zaimportuj collections
zaimportuj tempfile
zaimportuj contextlib
zaimportuj warnings


z urllib.error zaimportuj URLError, HTTPError, ContentTooShortError
z urllib.parse zaimportuj (
    urlparse, urlsplit, urljoin, unwrap, quote, unquote,
    splittype, splithost, splitport, splituser, splitpasswd,
    splitattr, splitquery, splitvalue, splittag, to_bytes,
    unquote_to_bytes, urlunparse)
z urllib.response zaimportuj addinfourl, addclosehook

# check dla SSL
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    _have_ssl = Nieprawda
inaczej:
    _have_ssl = Prawda

__all__ = [
    # Classes
    'Request', 'OpenerDirector', 'BaseHandler', 'HTTPDefaultErrorHandler',
    'HTTPRedirectHandler', 'HTTPCookieProcessor', 'ProxyHandler',
    'HTTPPasswordMgr', 'HTTPPasswordMgrWithDefaultRealm',
    'HTTPPasswordMgrWithPriorAuth', 'AbstractBasicAuthHandler',
    'HTTPBasicAuthHandler', 'ProxyBasicAuthHandler', 'AbstractDigestAuthHandler',
    'HTTPDigestAuthHandler', 'ProxyDigestAuthHandler', 'HTTPHandler',
    'FileHandler', 'FTPHandler', 'CacheFTPHandler', 'DataHandler',
    'UnknownHandler', 'HTTPErrorProcessor',
    # Functions
    'urlopen', 'install_opener', 'build_opener',
    'pathname2url', 'url2pathname', 'getproxies',
    # Legacy interface
    'urlretrieve', 'urlcleanup', 'URLopener', 'FancyURLopener',
]

# used w User-Agent header sent
__version__ = sys.version[:3]

_opener = Nic
def urlopen(url, data=Nic, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
            *, cafile=Nic, capath=Nic, cadefault=Nieprawda, context=Nic):
    global _opener
    jeżeli cafile albo capath albo cadefault:
        jeżeli context jest nie Nic:
            podnieś ValueError(
                "You can't dalej both context oraz any of cafile, capath, oraz "
                "cadefault"
            )
        jeżeli nie _have_ssl:
            podnieś ValueError('SSL support nie available')
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                             cafile=cafile,
                                             capath=capath)
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    albo_inaczej context:
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    albo_inaczej _opener jest Nic:
        _opener = opener = build_opener()
    inaczej:
        opener = _opener
    zwróć opener.open(url, data, timeout)

def install_opener(opener):
    global _opener
    _opener = opener

_url_tempfiles = []
def urlretrieve(url, filename=Nic, reporthook=Nic, data=Nic):
    """
    Retrieve a URL into a temporary location on disk.

    Requires a URL argument. If a filename jest dalejed, it jest used as
    the temporary file location. The reporthook argument should be
    a callable that accepts a block number, a read size, oraz the
    total file size of the URL target. The data argument should be
    valid URL encoded data.

    If a filename jest dalejed oraz the URL points to a local resource,
    the result jest a copy z local file to new file.

    Returns a tuple containing the path to the newly created
    data file jako well jako the resulting HTTPMessage object.
    """
    url_type, path = splittype(url)

    przy contextlib.closing(urlopen(url, data)) jako fp:
        headers = fp.info()

        # Just zwróć the local path oraz the "headers" dla file://
        # URLs. No sense w performing a copy unless requested.
        jeżeli url_type == "file" oraz nie filename:
            zwróć os.path.normpath(path), headers

        # Handle temporary file setup.
        jeżeli filename:
            tfp = open(filename, 'wb')
        inaczej:
            tfp = tempfile.NamedTemporaryFile(delete=Nieprawda)
            filename = tfp.name
            _url_tempfiles.append(filename)

        przy tfp:
            result = filename, headers
            bs = 1024*8
            size = -1
            read = 0
            blocknum = 0
            jeżeli "content-length" w headers:
                size = int(headers["Content-Length"])

            jeżeli reporthook:
                reporthook(blocknum, bs, size)

            dopóki Prawda:
                block = fp.read(bs)
                jeżeli nie block:
                    przerwij
                read += len(block)
                tfp.write(block)
                blocknum += 1
                jeżeli reporthook:
                    reporthook(blocknum, bs, size)

    jeżeli size >= 0 oraz read < size:
        podnieś ContentTooShortError(
            "retrieval incomplete: got only %i out of %i bytes"
            % (read, size), result)

    zwróć result

def urlcleanup():
    """Clean up temporary files z urlretrieve calls."""
    dla temp_file w _url_tempfiles:
        spróbuj:
            os.unlink(temp_file)
        wyjąwszy OSError:
            dalej

    usuń _url_tempfiles[:]
    global _opener
    jeżeli _opener:
        _opener = Nic

# copied z cookielib.py
_cut_port_re = re.compile(r":\d+$", re.ASCII)
def request_host(request):
    """Return request-host, jako defined by RFC 2965.

    Variation z RFC: returned value jest lowercased, dla convenient
    comparison.

    """
    url = request.full_url
    host = urlparse(url)[1]
    jeżeli host == "":
        host = request.get_header("Host", "")

    # remove port, jeżeli present
    host = _cut_port_re.sub("", host, 1)
    zwróć host.lower()

klasa Request:

    def __init__(self, url, data=Nic, headers={},
                 origin_req_host=Nic, unverifiable=Nieprawda,
                 method=Nic):
        self.full_url = url
        self.headers = {}
        self.unredirected_hdrs = {}
        self._data = Nic
        self.data = data
        self._tunnel_host = Nic
        dla key, value w headers.items():
            self.add_header(key, value)
        jeżeli origin_req_host jest Nic:
            origin_req_host = request_host(self)
        self.origin_req_host = origin_req_host
        self.unverifiable = unverifiable
        jeżeli method:
            self.method = method

    @property
    def full_url(self):
        jeżeli self.fragment:
            zwróć '{}#{}'.format(self._full_url, self.fragment)
        zwróć self._full_url

    @full_url.setter
    def full_url(self, url):
        # unwrap('<URL:type://host/path>') --> 'type://host/path'
        self._full_url = unwrap(url)
        self._full_url, self.fragment = splittag(self._full_url)
        self._parse()

    @full_url.deleter
    def full_url(self):
        self._full_url = Nic
        self.fragment = Nic
        self.selector = ''

    @property
    def data(self):
        zwróć self._data

    @data.setter
    def data(self, data):
        jeżeli data != self._data:
            self._data = data
            # issue 16464
            # jeżeli we change data we need to remove content-length header
            # (cause it's most probably calculated dla previous value)
            jeżeli self.has_header("Content-length"):
                self.remove_header("Content-length")

    @data.deleter
    def data(self):
        self.data = Nic

    def _parse(self):
        self.type, rest = splittype(self._full_url)
        jeżeli self.type jest Nic:
            podnieś ValueError("unknown url type: %r" % self.full_url)
        self.host, self.selector = splithost(rest)
        jeżeli self.host:
            self.host = unquote(self.host)

    def get_method(self):
        """Return a string indicating the HTTP request method."""
        default_method = "POST" jeżeli self.data jest nie Nic inaczej "GET"
        zwróć getattr(self, 'method', default_method)

    def get_full_url(self):
        zwróć self.full_url

    def set_proxy(self, host, type):
        jeżeli self.type == 'https' oraz nie self._tunnel_host:
            self._tunnel_host = self.host
        inaczej:
            self.type= type
            self.selector = self.full_url
        self.host = host

    def has_proxy(self):
        zwróć self.selector == self.full_url

    def add_header(self, key, val):
        # useful dla something like authentication
        self.headers[key.capitalize()] = val

    def add_unredirected_header(self, key, val):
        # will nie be added to a redirected request
        self.unredirected_hdrs[key.capitalize()] = val

    def has_header(self, header_name):
        zwróć (header_name w self.headers albo
                header_name w self.unredirected_hdrs)

    def get_header(self, header_name, default=Nic):
        zwróć self.headers.get(
            header_name,
            self.unredirected_hdrs.get(header_name, default))

    def remove_header(self, header_name):
        self.headers.pop(header_name, Nic)
        self.unredirected_hdrs.pop(header_name, Nic)

    def header_items(self):
        hdrs = self.unredirected_hdrs.copy()
        hdrs.update(self.headers)
        zwróć list(hdrs.items())

klasa OpenerDirector:
    def __init__(self):
        client_version = "Python-urllib/%s" % __version__
        self.addheaders = [('User-agent', client_version)]
        # self.handlers jest retained only dla backward compatibility
        self.handlers = []
        # manage the individual handlers
        self.handle_open = {}
        self.handle_error = {}
        self.process_response = {}
        self.process_request = {}

    def add_handler(self, handler):
        jeżeli nie hasattr(handler, "add_parent"):
            podnieś TypeError("expected BaseHandler instance, got %r" %
                            type(handler))

        added = Nieprawda
        dla meth w dir(handler):
            jeżeli meth w ["redirect_request", "do_open", "proxy_open"]:
                # oops, coincidental match
                kontynuuj

            i = meth.find("_")
            protocol = meth[:i]
            condition = meth[i+1:]

            jeżeli condition.startswith("error"):
                j = condition.find("_") + i + 1
                kind = meth[j+1:]
                spróbuj:
                    kind = int(kind)
                wyjąwszy ValueError:
                    dalej
                lookup = self.handle_error.get(protocol, {})
                self.handle_error[protocol] = lookup
            albo_inaczej condition == "open":
                kind = protocol
                lookup = self.handle_open
            albo_inaczej condition == "response":
                kind = protocol
                lookup = self.process_response
            albo_inaczej condition == "request":
                kind = protocol
                lookup = self.process_request
            inaczej:
                kontynuuj

            handlers = lookup.setdefault(kind, [])
            jeżeli handlers:
                bisect.insort(handlers, handler)
            inaczej:
                handlers.append(handler)
            added = Prawda

        jeżeli added:
            bisect.insort(self.handlers, handler)
            handler.add_parent(self)

    def close(self):
        # Only exists dla backwards compatibility.
        dalej

    def _call_chain(self, chain, kind, meth_name, *args):
        # Handlers podnieś an exception jeżeli no one inaczej should try to handle
        # the request, albo zwróć Nic jeżeli they can't but another handler
        # could.  Otherwise, they zwróć the response.
        handlers = chain.get(kind, ())
        dla handler w handlers:
            func = getattr(handler, meth_name)
            result = func(*args)
            jeżeli result jest nie Nic:
                zwróć result

    def open(self, fullurl, data=Nic, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        # accept a URL albo a Request object
        jeżeli isinstance(fullurl, str):
            req = Request(fullurl, data)
        inaczej:
            req = fullurl
            jeżeli data jest nie Nic:
                req.data = data

        req.timeout = timeout
        protocol = req.type

        # pre-process request
        meth_name = protocol+"_request"
        dla processor w self.process_request.get(protocol, []):
            meth = getattr(processor, meth_name)
            req = meth(req)

        response = self._open(req, data)

        # post-process response
        meth_name = protocol+"_response"
        dla processor w self.process_response.get(protocol, []):
            meth = getattr(processor, meth_name)
            response = meth(req, response)

        zwróć response

    def _open(self, req, data=Nic):
        result = self._call_chain(self.handle_open, 'default',
                                  'default_open', req)
        jeżeli result:
            zwróć result

        protocol = req.type
        result = self._call_chain(self.handle_open, protocol, protocol +
                                  '_open', req)
        jeżeli result:
            zwróć result

        zwróć self._call_chain(self.handle_open, 'unknown',
                                'unknown_open', req)

    def error(self, proto, *args):
        jeżeli proto w ('http', 'https'):
            # XXX http[s] protocols are special-cased
            dict = self.handle_error['http'] # https jest nie different than http
            proto = args[2]  # YUCK!
            meth_name = 'http_error_%s' % proto
            http_err = 1
            orig_args = args
        inaczej:
            dict = self.handle_error
            meth_name = proto + '_error'
            http_err = 0
        args = (dict, proto, meth_name) + args
        result = self._call_chain(*args)
        jeżeli result:
            zwróć result

        jeżeli http_err:
            args = (dict, 'default', 'http_error_default') + orig_args
            zwróć self._call_chain(*args)

# XXX probably also want an abstract factory that knows when it makes
# sense to skip a superclass w favor of a subclass oraz when it might
# make sense to include both

def build_opener(*handlers):
    """Create an opener object z a list of handlers.

    The opener will use several default handlers, including support
    dla HTTP, FTP oraz when applicable HTTPS.

    If any of the handlers dalejed jako arguments are subclasses of the
    default handlers, the default handlers will nie be used.
    """
    opener = OpenerDirector()
    default_classes = [ProxyHandler, UnknownHandler, HTTPHandler,
                       HTTPDefaultErrorHandler, HTTPRedirectHandler,
                       FTPHandler, FileHandler, HTTPErrorProcessor,
                       DataHandler]
    jeżeli hasattr(http.client, "HTTPSConnection"):
        default_classes.append(HTTPSHandler)
    skip = set()
    dla klass w default_classes:
        dla check w handlers:
            jeżeli isinstance(check, type):
                jeżeli issubclass(check, klass):
                    skip.add(klass)
            albo_inaczej isinstance(check, klass):
                skip.add(klass)
    dla klass w skip:
        default_classes.remove(klass)

    dla klass w default_classes:
        opener.add_handler(klass())

    dla h w handlers:
        jeżeli isinstance(h, type):
            h = h()
        opener.add_handler(h)
    zwróć opener

klasa BaseHandler:
    handler_order = 500

    def add_parent(self, parent):
        self.parent = parent

    def close(self):
        # Only exists dla backwards compatibility
        dalej

    def __lt__(self, other):
        jeżeli nie hasattr(other, "handler_order"):
            # Try to preserve the old behavior of having custom classes
            # inserted after default ones (works only dla custom user
            # classes which are nie aware of handler_order).
            zwróć Prawda
        zwróć self.handler_order < other.handler_order


klasa HTTPErrorProcessor(BaseHandler):
    """Process HTTP error responses."""
    handler_order = 1000  # after all other processing

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, oraz accepted.
        jeżeli nie (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)

        zwróć response

    https_response = http_response

klasa HTTPDefaultErrorHandler(BaseHandler):
    def http_error_default(self, req, fp, code, msg, hdrs):
        podnieś HTTPError(req.full_url, code, msg, hdrs, fp)

klasa HTTPRedirectHandler(BaseHandler):
    # maximum number of redirections to any single URL
    # this jest needed because of the state that cookies introduce
    max_repeats = 4
    # maximum total number of redirections (regardless of URL) before
    # assuming we're w a loop
    max_redirections = 10

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Return a Request albo Nic w response to a redirect.

        This jest called by the http_error_30x methods when a
        redirection response jest received.  If a redirection should
        take place, zwróć a new Request to allow http_error_30x to
        perform the redirect.  Otherwise, podnieś HTTPError jeżeli no-one
        inaczej should try to handle this url.  Return Nic jeżeli you can't
        but another Handler might.
        """
        m = req.get_method()
        jeżeli (nie (code w (301, 302, 303, 307) oraz m w ("GET", "HEAD")
            albo code w (301, 302, 303) oraz m == "POST")):
            podnieś HTTPError(req.full_url, code, msg, headers, fp)

        # Strictly (according to RFC 2616), 301 albo 302 w response to
        # a POST MUST NOT cause a redirection without confirmation
        # z the user (of urllib.request, w this case).  In practice,
        # essentially all clients do redirect w this case, so we do
        # the same.
        # be conciliant przy URIs containing a space
        newurl = newurl.replace(' ', '%20')
        CONTENT_HEADERS = ("content-length", "content-type")
        newheaders = dict((k, v) dla k, v w req.headers.items()
                          jeżeli k.lower() nie w CONTENT_HEADERS)
        zwróć Request(newurl,
                       headers=newheaders,
                       origin_req_host=req.origin_req_host,
                       unverifiable=Prawda)

    # Implementation note: To avoid the server sending us into an
    # infinite loop, the request object needs to track what URLs we
    # have already seen.  Do this by adding a handler-specific
    # attribute to the Request object.
    def http_error_302(self, req, fp, code, msg, headers):
        # Some servers (incorrectly) zwróć multiple Location headers
        # (so probably same goes dla URI).  Use first header.
        jeżeli "location" w headers:
            newurl = headers["location"]
        albo_inaczej "uri" w headers:
            newurl = headers["uri"]
        inaczej:
            zwróć

        # fix a possible malformed URL
        urlparts = urlparse(newurl)

        # For security reasons we don't allow redirection to anything other
        # than http, https albo ftp.

        jeżeli urlparts.scheme nie w ('http', 'https', 'ftp', ''):
            podnieś HTTPError(
                newurl, code,
                "%s - Redirection to url '%s' jest nie allowed" % (msg, newurl),
                headers, fp)

        jeżeli nie urlparts.path:
            urlparts = list(urlparts)
            urlparts[2] = "/"
        newurl = urlunparse(urlparts)

        newurl = urljoin(req.full_url, newurl)

        # XXX Probably want to forget about the state of the current
        # request, although that might interact poorly przy other
        # handlers that also use handler-specific request attributes
        new = self.redirect_request(req, fp, code, msg, headers, newurl)
        jeżeli new jest Nic:
            zwróć

        # loop detection
        # .redirect_dict has a key url jeżeli url was previously visited.
        jeżeli hasattr(req, 'redirect_dict'):
            visited = new.redirect_dict = req.redirect_dict
            jeżeli (visited.get(newurl, 0) >= self.max_repeats albo
                len(visited) >= self.max_redirections):
                podnieś HTTPError(req.full_url, code,
                                self.inf_msg + msg, headers, fp)
        inaczej:
            visited = new.redirect_dict = req.redirect_dict = {}
        visited[newurl] = visited.get(newurl, 0) + 1

        # Don't close the fp until we are sure that we won't use it
        # przy HTTPError.
        fp.read()
        fp.close()

        zwróć self.parent.open(new, timeout=req.timeout)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

    inf_msg = "The HTTP server returned a redirect error that would " \
              "lead to an infinite loop.\n" \
              "The last 30x error message was:\n"


def _parse_proxy(proxy):
    """Return (scheme, user, dalejword, host/port) given a URL albo an authority.

    If a URL jest supplied, it must have an authority (host:port) component.
    According to RFC 3986, having an authority component means the URL must
    have two slashes after the scheme.
    """
    scheme, r_scheme = splittype(proxy)
    jeżeli nie r_scheme.startswith("/"):
        # authority
        scheme = Nic
        authority = proxy
    inaczej:
        # URL
        jeżeli nie r_scheme.startswith("//"):
            podnieś ValueError("proxy URL przy no authority: %r" % proxy)
        # We have an authority, so dla RFC 3986-compliant URLs (by ss 3.
        # oraz 3.3.), path jest empty albo starts przy '/'
        end = r_scheme.find("/", 2)
        jeżeli end == -1:
            end = Nic
        authority = r_scheme[2:end]
    userinfo, hostport = splituser(authority)
    jeżeli userinfo jest nie Nic:
        user, dalejword = splitpasswd(userinfo)
    inaczej:
        user = dalejword = Nic
    zwróć scheme, user, dalejword, hostport

klasa ProxyHandler(BaseHandler):
    # Proxies must be w front
    handler_order = 100

    def __init__(self, proxies=Nic):
        jeżeli proxies jest Nic:
            proxies = getproxies()
        assert hasattr(proxies, 'keys'), "proxies must be a mapping"
        self.proxies = proxies
        dla type, url w proxies.items():
            setattr(self, '%s_open' % type,
                    lambda r, proxy=url, type=type, meth=self.proxy_open:
                        meth(r, proxy, type))

    def proxy_open(self, req, proxy, type):
        orig_type = req.type
        proxy_type, user, dalejword, hostport = _parse_proxy(proxy)
        jeżeli proxy_type jest Nic:
            proxy_type = orig_type

        jeżeli req.host oraz proxy_bypass(req.host):
            zwróć Nic

        jeżeli user oraz dalejword:
            user_pass = '%s:%s' % (unquote(user),
                                   unquote(password))
            creds = base64.b64encode(user_pass.encode()).decode("ascii")
            req.add_header('Proxy-authorization', 'Basic ' + creds)
        hostport = unquote(hostport)
        req.set_proxy(hostport, proxy_type)
        jeżeli orig_type == proxy_type albo orig_type == 'https':
            # let other handlers take care of it
            zwróć Nic
        inaczej:
            # need to start over, because the other handlers don't
            # grok the proxy's URL type
            # e.g. jeżeli we have a constructor arg proxies like so:
            # {'http': 'ftp://proxy.example.com'}, we may end up turning
            # a request dla http://acme.example.com/a into one for
            # ftp://proxy.example.com/a
            zwróć self.parent.open(req, timeout=req.timeout)

klasa HTTPPasswordMgr:

    def __init__(self):
        self.passwd = {}

    def add_password(self, realm, uri, user, dalejwd):
        # uri could be a single URI albo a sequence
        jeżeli isinstance(uri, str):
            uri = [uri]
        jeżeli realm nie w self.passwd:
            self.passwd[realm] = {}
        dla default_port w Prawda, Nieprawda:
            reduced_uri = tuple(
                [self.reduce_uri(u, default_port) dla u w uri])
            self.passwd[realm][reduced_uri] = (user, dalejwd)

    def find_user_password(self, realm, authuri):
        domains = self.passwd.get(realm, {})
        dla default_port w Prawda, Nieprawda:
            reduced_authuri = self.reduce_uri(authuri, default_port)
            dla uris, authinfo w domains.items():
                dla uri w uris:
                    jeżeli self.is_suburi(uri, reduced_authuri):
                        zwróć authinfo
        zwróć Nic, Nic

    def reduce_uri(self, uri, default_port=Prawda):
        """Accept authority albo URI oraz extract only the authority oraz path."""
        # note HTTP URLs do nie have a userinfo component
        parts = urlsplit(uri)
        jeżeli parts[1]:
            # URI
            scheme = parts[0]
            authority = parts[1]
            path = parts[2] albo '/'
        inaczej:
            # host albo host:port
            scheme = Nic
            authority = uri
            path = '/'
        host, port = splitport(authority)
        jeżeli default_port oraz port jest Nic oraz scheme jest nie Nic:
            dport = {"http": 80,
                     "https": 443,
                     }.get(scheme)
            jeżeli dport jest nie Nic:
                authority = "%s:%d" % (host, dport)
        zwróć authority, path

    def is_suburi(self, base, test):
        """Check jeżeli test jest below base w a URI tree

        Both args must be URIs w reduced form.
        """
        jeżeli base == test:
            zwróć Prawda
        jeżeli base[0] != test[0]:
            zwróć Nieprawda
        common = posixpath.commonprefix((base[1], test[1]))
        jeżeli len(common) == len(base[1]):
            zwróć Prawda
        zwróć Nieprawda


klasa HTTPPasswordMgrWithDefaultRealm(HTTPPasswordMgr):

    def find_user_password(self, realm, authuri):
        user, dalejword = HTTPPasswordMgr.find_user_password(self, realm,
                                                            authuri)
        jeżeli user jest nie Nic:
            zwróć user, dalejword
        zwróć HTTPPasswordMgr.find_user_password(self, Nic, authuri)


klasa HTTPPasswordMgrWithPriorAuth(HTTPPasswordMgrWithDefaultRealm):

    def __init__(self, *args, **kwargs):
        self.authenticated = {}
        super().__init__(*args, **kwargs)

    def add_password(self, realm, uri, user, dalejwd, is_authenticated=Nieprawda):
        self.update_authenticated(uri, is_authenticated)
        # Add a default dla prior auth requests
        jeżeli realm jest nie Nic:
            super().add_password(Nic, uri, user, dalejwd)
        super().add_password(realm, uri, user, dalejwd)

    def update_authenticated(self, uri, is_authenticated=Nieprawda):
        # uri could be a single URI albo a sequence
        jeżeli isinstance(uri, str):
            uri = [uri]

        dla default_port w Prawda, Nieprawda:
            dla u w uri:
                reduced_uri = self.reduce_uri(u, default_port)
                self.authenticated[reduced_uri] = is_authenticated

    def is_authenticated(self, authuri):
        dla default_port w Prawda, Nieprawda:
            reduced_authuri = self.reduce_uri(authuri, default_port)
            dla uri w self.authenticated:
                jeżeli self.is_suburi(uri, reduced_authuri):
                    zwróć self.authenticated[uri]


klasa AbstractBasicAuthHandler:

    # XXX this allows dla multiple auth-schemes, but will stupidly pick
    # the last one przy a realm specified.

    # allow dla double- oraz single-quoted realm values
    # (single quotes are a violation of the RFC, but appear w the wild)
    rx = re.compile('(?:.*,)*[ \t]*([^ \t]+)[ \t]+'
                    'realm=(["\']?)([^"\']*)\\2', re.I)

    # XXX could pre-emptively send auth info already accepted (RFC 2617,
    # end of section 2, oraz section 1.2 immediately after "credentials"
    # production).

    def __init__(self, dalejword_mgr=Nic):
        jeżeli dalejword_mgr jest Nic:
            dalejword_mgr = HTTPPasswordMgr()
        self.passwd = dalejword_mgr
        self.add_password = self.passwd.add_password

    def http_error_auth_reqed(self, authreq, host, req, headers):
        # host may be an authority (without userinfo) albo a URL przy an
        # authority
        # XXX could be multiple headers
        authreq = headers.get(authreq, Nic)

        jeżeli authreq:
            scheme = authreq.split()[0]
            jeżeli scheme.lower() != 'basic':
                podnieś ValueError("AbstractBasicAuthHandler does not"
                                 " support the following scheme: '%s'" %
                                 scheme)
            inaczej:
                mo = AbstractBasicAuthHandler.rx.search(authreq)
                jeżeli mo:
                    scheme, quote, realm = mo.groups()
                    jeżeli quote nie w ['"',"'"]:
                        warnings.warn("Basic Auth Realm was unquoted",
                                      UserWarning, 2)
                    jeżeli scheme.lower() == 'basic':
                        zwróć self.retry_http_basic_auth(host, req, realm)

    def retry_http_basic_auth(self, host, req, realm):
        user, pw = self.passwd.find_user_password(realm, host)
        jeżeli pw jest nie Nic:
            raw = "%s:%s" % (user, pw)
            auth = "Basic " + base64.b64encode(raw.encode()).decode("ascii")
            jeżeli req.get_header(self.auth_header, Nic) == auth:
                zwróć Nic
            req.add_unredirected_header(self.auth_header, auth)
            zwróć self.parent.open(req, timeout=req.timeout)
        inaczej:
            zwróć Nic

    def http_request(self, req):
        jeżeli (nie hasattr(self.passwd, 'is_authenticated') albo
           nie self.passwd.is_authenticated(req.full_url)):
            zwróć req

        jeżeli nie req.has_header('Authorization'):
            user, dalejwd = self.passwd.find_user_password(Nic, req.full_url)
            credentials = '{0}:{1}'.format(user, dalejwd).encode()
            auth_str = base64.standard_b64encode(credentials).decode()
            req.add_unredirected_header('Authorization',
                                        'Basic {}'.format(auth_str.strip()))
        zwróć req

    def http_response(self, req, response):
        jeżeli hasattr(self.passwd, 'is_authenticated'):
            jeżeli 200 <= response.code < 300:
                self.passwd.update_authenticated(req.full_url, Prawda)
            inaczej:
                self.passwd.update_authenticated(req.full_url, Nieprawda)
        zwróć response

    https_request = http_request
    https_response = http_response



klasa HTTPBasicAuthHandler(AbstractBasicAuthHandler, BaseHandler):

    auth_header = 'Authorization'

    def http_error_401(self, req, fp, code, msg, headers):
        url = req.full_url
        response = self.http_error_auth_reqed('www-authenticate',
                                          url, req, headers)
        zwróć response


klasa ProxyBasicAuthHandler(AbstractBasicAuthHandler, BaseHandler):

    auth_header = 'Proxy-authorization'

    def http_error_407(self, req, fp, code, msg, headers):
        # http_error_auth_reqed requires that there jest no userinfo component w
        # authority.  Assume there isn't one, since urllib.request does nie (and
        # should not, RFC 3986 s. 3.2.1) support requests dla URLs containing
        # userinfo.
        authority = req.host
        response = self.http_error_auth_reqed('proxy-authenticate',
                                          authority, req, headers)
        zwróć response


# Return n random bytes.
_randombytes = os.urandom


klasa AbstractDigestAuthHandler:
    # Digest authentication jest specified w RFC 2617.

    # XXX The client does nie inspect the Authentication-Info header
    # w a successful response.

    # XXX It should be possible to test this implementation against
    # a mock server that just generates a static set of challenges.

    # XXX qop="auth-int" supports jest shaky

    def __init__(self, dalejwd=Nic):
        jeżeli dalejwd jest Nic:
            dalejwd = HTTPPasswordMgr()
        self.passwd = dalejwd
        self.add_password = self.passwd.add_password
        self.retried = 0
        self.nonce_count = 0
        self.last_nonce = Nic

    def reset_retry_count(self):
        self.retried = 0

    def http_error_auth_reqed(self, auth_header, host, req, headers):
        authreq = headers.get(auth_header, Nic)
        jeżeli self.retried > 5:
            # Don't fail endlessly - jeżeli we failed once, we'll probably
            # fail a second time. Hm. Unless the Password Manager jest
            # prompting dla the information. Crap. This isn't great
            # but it's better than the current 'repeat until recursion
            # depth exceeded' approach <wink>
            podnieś HTTPError(req.full_url, 401, "digest auth failed",
                            headers, Nic)
        inaczej:
            self.retried += 1
        jeżeli authreq:
            scheme = authreq.split()[0]
            jeżeli scheme.lower() == 'digest':
                zwróć self.retry_http_digest_auth(req, authreq)
            albo_inaczej scheme.lower() != 'basic':
                podnieś ValueError("AbstractDigestAuthHandler does nie support"
                                 " the following scheme: '%s'" % scheme)

    def retry_http_digest_auth(self, req, auth):
        token, challenge = auth.split(' ', 1)
        chal = parse_keqv_list(filter(Nic, parse_http_list(challenge)))
        auth = self.get_authorization(req, chal)
        jeżeli auth:
            auth_val = 'Digest %s' % auth
            jeżeli req.headers.get(self.auth_header, Nic) == auth_val:
                zwróć Nic
            req.add_unredirected_header(self.auth_header, auth_val)
            resp = self.parent.open(req, timeout=req.timeout)
            zwróć resp

    def get_cnonce(self, nonce):
        # The cnonce-value jest an opaque
        # quoted string value provided by the client oraz used by both client
        # oraz server to avoid chosen plaintext attacks, to provide mutual
        # authentication, oraz to provide some message integrity protection.
        # This isn't a fabulous effort, but it's probably Good Enough.
        s = "%s:%s:%s:" % (self.nonce_count, nonce, time.ctime())
        b = s.encode("ascii") + _randombytes(8)
        dig = hashlib.sha1(b).hexdigest()
        zwróć dig[:16]

    def get_authorization(self, req, chal):
        spróbuj:
            realm = chal['realm']
            nonce = chal['nonce']
            qop = chal.get('qop')
            algorithm = chal.get('algorithm', 'MD5')
            # mod_digest doesn't send an opaque, even though it isn't
            # supposed to be optional
            opaque = chal.get('opaque', Nic)
        wyjąwszy KeyError:
            zwróć Nic

        H, KD = self.get_algorithm_impls(algorithm)
        jeżeli H jest Nic:
            zwróć Nic

        user, pw = self.passwd.find_user_password(realm, req.full_url)
        jeżeli user jest Nic:
            zwróć Nic

        # XXX nie implemented yet
        jeżeli req.data jest nie Nic:
            entdig = self.get_entity_digest(req.data, chal)
        inaczej:
            entdig = Nic

        A1 = "%s:%s:%s" % (user, realm, pw)
        A2 = "%s:%s" % (req.get_method(),
                        # XXX selector: what about proxies oraz full urls
                        req.selector)
        jeżeli qop == 'auth':
            jeżeli nonce == self.last_nonce:
                self.nonce_count += 1
            inaczej:
                self.nonce_count = 1
                self.last_nonce = nonce
            ncvalue = '%08x' % self.nonce_count
            cnonce = self.get_cnonce(nonce)
            noncebit = "%s:%s:%s:%s:%s" % (nonce, ncvalue, cnonce, qop, H(A2))
            respdig = KD(H(A1), noncebit)
        albo_inaczej qop jest Nic:
            respdig = KD(H(A1), "%s:%s" % (nonce, H(A2)))
        inaczej:
            # XXX handle auth-int.
            podnieś URLError("qop '%s' jest nie supported." % qop)

        # XXX should the partial digests be encoded too?

        base = 'username="%s", realm="%s", nonce="%s", uri="%s", ' \
               'response="%s"' % (user, realm, nonce, req.selector,
                                  respdig)
        jeżeli opaque:
            base += ', opaque="%s"' % opaque
        jeżeli entdig:
            base += ', digest="%s"' % entdig
        base += ', algorithm="%s"' % algorithm
        jeżeli qop:
            base += ', qop=auth, nc=%s, cnonce="%s"' % (ncvalue, cnonce)
        zwróć base

    def get_algorithm_impls(self, algorithm):
        # lambdas assume digest modules are imported at the top level
        jeżeli algorithm == 'MD5':
            H = lambda x: hashlib.md5(x.encode("ascii")).hexdigest()
        albo_inaczej algorithm == 'SHA':
            H = lambda x: hashlib.sha1(x.encode("ascii")).hexdigest()
        # XXX MD5-sess
        KD = lambda s, d: H("%s:%s" % (s, d))
        zwróć H, KD

    def get_entity_digest(self, data, chal):
        # XXX nie implemented yet
        zwróć Nic


klasa HTTPDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):
    """An authentication protocol defined by RFC 2069

    Digest authentication improves on basic authentication because it
    does nie transmit dalejwords w the clear.
    """

    auth_header = 'Authorization'
    handler_order = 490  # before Basic auth

    def http_error_401(self, req, fp, code, msg, headers):
        host = urlparse(req.full_url)[1]
        retry = self.http_error_auth_reqed('www-authenticate',
                                           host, req, headers)
        self.reset_retry_count()
        zwróć retry


klasa ProxyDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):

    auth_header = 'Proxy-Authorization'
    handler_order = 490  # before Basic auth

    def http_error_407(self, req, fp, code, msg, headers):
        host = req.host
        retry = self.http_error_auth_reqed('proxy-authenticate',
                                           host, req, headers)
        self.reset_retry_count()
        zwróć retry

klasa AbstractHTTPHandler(BaseHandler):

    def __init__(self, debuglevel=0):
        self._debuglevel = debuglevel

    def set_http_debuglevel(self, level):
        self._debuglevel = level

    def do_request_(self, request):
        host = request.host
        jeżeli nie host:
            podnieś URLError('no host given')

        jeżeli request.data jest nie Nic:  # POST
            data = request.data
            jeżeli isinstance(data, str):
                msg = "POST data should be bytes albo an iterable of bytes. " \
                      "It cannot be of type str."
                podnieś TypeError(msg)
            jeżeli nie request.has_header('Content-type'):
                request.add_unredirected_header(
                    'Content-type',
                    'application/x-www-form-urlencoded')
            jeżeli nie request.has_header('Content-length'):
                spróbuj:
                    mv = memoryview(data)
                wyjąwszy TypeError:
                    jeżeli isinstance(data, collections.Iterable):
                        podnieś ValueError("Content-Length should be specified "
                                "dla iterable data of type %r %r" % (type(data),
                                data))
                inaczej:
                    request.add_unredirected_header(
                            'Content-length', '%d' % (len(mv) * mv.itemsize))

        sel_host = host
        jeżeli request.has_proxy():
            scheme, sel = splittype(request.selector)
            sel_host, sel_path = splithost(sel)
        jeżeli nie request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)
        dla name, value w self.parent.addheaders:
            name = name.capitalize()
            jeżeli nie request.has_header(name):
                request.add_unredirected_header(name, value)

        zwróć request

    def do_open(self, http_class, req, **http_conn_args):
        """Return an HTTPResponse object dla the request, using http_class.

        http_class must implement the HTTPConnection API z http.client.
        """
        host = req.host
        jeżeli nie host:
            podnieś URLError('no host given')

        # will parse host:port
        h = http_class(host, timeout=req.timeout, **http_conn_args)

        headers = dict(req.unredirected_hdrs)
        headers.update(dict((k, v) dla k, v w req.headers.items()
                            jeżeli k nie w headers))

        # TODO(jhylton): Should this be redesigned to handle
        # persistent connections?

        # We want to make an HTTP/1.1 request, but the addinfourl
        # klasa isn't prepared to deal przy a persistent connection.
        # It will try to read all remaining data z the socket,
        # which will block dopóki the server waits dla the next request.
        # So make sure the connection gets closed after the (only)
        # request.
        headers["Connection"] = "close"
        headers = dict((name.title(), val) dla name, val w headers.items())

        jeżeli req._tunnel_host:
            tunnel_headers = {}
            proxy_auth_hdr = "Proxy-Authorization"
            jeżeli proxy_auth_hdr w headers:
                tunnel_headers[proxy_auth_hdr] = headers[proxy_auth_hdr]
                # Proxy-Authorization should nie be sent to origin
                # server.
                usuń headers[proxy_auth_hdr]
            h.set_tunnel(req._tunnel_host, headers=tunnel_headers)

        spróbuj:
            spróbuj:
                h.request(req.get_method(), req.selector, req.data, headers)
            wyjąwszy OSError jako err: # timeout error
                podnieś URLError(err)
            r = h.getresponse()
        wyjąwszy:
            h.close()
            podnieś

        # If the server does nie send us a 'Connection: close' header,
        # HTTPConnection assumes the socket should be left open. Manually
        # mark the socket to be closed when this response object goes away.
        jeżeli h.sock:
            h.sock.close()
            h.sock = Nic

        r.url = req.get_full_url()
        # This line replaces the .msg attribute of the HTTPResponse
        # przy .headers, because urllib clients expect the response to
        # have the reason w .msg.  It would be good to mark this
        # attribute jest deprecated oraz get then to use info() albo
        # .headers.
        r.msg = r.reason
        zwróć r


klasa HTTPHandler(AbstractHTTPHandler):

    def http_open(self, req):
        zwróć self.do_open(http.client.HTTPConnection, req)

    http_request = AbstractHTTPHandler.do_request_

jeżeli hasattr(http.client, 'HTTPSConnection'):

    klasa HTTPSHandler(AbstractHTTPHandler):

        def __init__(self, debuglevel=0, context=Nic, check_hostname=Nic):
            AbstractHTTPHandler.__init__(self, debuglevel)
            self._context = context
            self._check_hostname = check_hostname

        def https_open(self, req):
            zwróć self.do_open(http.client.HTTPSConnection, req,
                context=self._context, check_hostname=self._check_hostname)

        https_request = AbstractHTTPHandler.do_request_

    __all__.append('HTTPSHandler')

klasa HTTPCookieProcessor(BaseHandler):
    def __init__(self, cookiejar=Nic):
        zaimportuj http.cookiejar
        jeżeli cookiejar jest Nic:
            cookiejar = http.cookiejar.CookieJar()
        self.cookiejar = cookiejar

    def http_request(self, request):
        self.cookiejar.add_cookie_header(request)
        zwróć request

    def http_response(self, request, response):
        self.cookiejar.extract_cookies(response, request)
        zwróć response

    https_request = http_request
    https_response = http_response

klasa UnknownHandler(BaseHandler):
    def unknown_open(self, req):
        type = req.type
        podnieś URLError('unknown url type: %s' % type)

def parse_keqv_list(l):
    """Parse list of key=value strings where keys are nie duplicated."""
    parsed = {}
    dla elt w l:
        k, v = elt.split('=', 1)
        jeżeli v[0] == '"' oraz v[-1] == '"':
            v = v[1:-1]
        parsed[k] = v
    zwróć parsed

def parse_http_list(s):
    """Parse lists jako described by RFC 2068 Section 2.

    In particular, parse comma-separated lists where the elements of
    the list may include quoted-strings.  A quoted-string could
    contain a comma.  A non-quoted string could have quotes w the
    middle.  Neither commas nor quotes count jeżeli they are escaped.
    Only double-quotes count, nie single-quotes.
    """
    res = []
    part = ''

    escape = quote = Nieprawda
    dla cur w s:
        jeżeli escape:
            part += cur
            escape = Nieprawda
            kontynuuj
        jeżeli quote:
            jeżeli cur == '\\':
                escape = Prawda
                kontynuuj
            albo_inaczej cur == '"':
                quote = Nieprawda
            part += cur
            kontynuuj

        jeżeli cur == ',':
            res.append(part)
            part = ''
            kontynuuj

        jeżeli cur == '"':
            quote = Prawda

        part += cur

    # append last part
    jeżeli part:
        res.append(part)

    zwróć [part.strip() dla part w res]

klasa FileHandler(BaseHandler):
    # Use local file albo FTP depending on form of URL
    def file_open(self, req):
        url = req.selector
        jeżeli url[:2] == '//' oraz url[2:3] != '/' oraz (req.host oraz
                req.host != 'localhost'):
            jeżeli nie req.host w self.get_names():
                podnieś URLError("file:// scheme jest supported only on localhost")
        inaczej:
            zwróć self.open_local_file(req)

    # names dla the localhost
    names = Nic
    def get_names(self):
        jeżeli FileHandler.names jest Nic:
            spróbuj:
                FileHandler.names = tuple(
                    socket.gethostbyname_ex('localhost')[2] +
                    socket.gethostbyname_ex(socket.gethostname())[2])
            wyjąwszy socket.gaierror:
                FileHandler.names = (socket.gethostbyname('localhost'),)
        zwróć FileHandler.names

    # nie entirely sure what the rules are here
    def open_local_file(self, req):
        zaimportuj email.utils
        zaimportuj mimetypes
        host = req.host
        filename = req.selector
        localfile = url2pathname(filename)
        spróbuj:
            stats = os.stat(localfile)
            size = stats.st_size
            modified = email.utils.formatdate(stats.st_mtime, usegmt=Prawda)
            mtype = mimetypes.guess_type(filename)[0]
            headers = email.message_from_string(
                'Content-type: %s\nContent-length: %d\nLast-modified: %s\n' %
                (mtype albo 'text/plain', size, modified))
            jeżeli host:
                host, port = splitport(host)
            jeżeli nie host albo \
                (nie port oraz _safe_gethostbyname(host) w self.get_names()):
                jeżeli host:
                    origurl = 'file://' + host + filename
                inaczej:
                    origurl = 'file://' + filename
                zwróć addinfourl(open(localfile, 'rb'), headers, origurl)
        wyjąwszy OSError jako exp:
            # users shouldn't expect OSErrors coming z urlopen()
            podnieś URLError(exp)
        podnieś URLError('file nie on local host')

def _safe_gethostbyname(host):
    spróbuj:
        zwróć socket.gethostbyname(host)
    wyjąwszy socket.gaierror:
        zwróć Nic

klasa FTPHandler(BaseHandler):
    def ftp_open(self, req):
        zaimportuj ftplib
        zaimportuj mimetypes
        host = req.host
        jeżeli nie host:
            podnieś URLError('ftp error: no host given')
        host, port = splitport(host)
        jeżeli port jest Nic:
            port = ftplib.FTP_PORT
        inaczej:
            port = int(port)

        # username/password handling
        user, host = splituser(host)
        jeżeli user:
            user, dalejwd = splitpasswd(user)
        inaczej:
            dalejwd = Nic
        host = unquote(host)
        user = user albo ''
        dalejwd = dalejwd albo ''

        spróbuj:
            host = socket.gethostbyname(host)
        wyjąwszy OSError jako msg:
            podnieś URLError(msg)
        path, attrs = splitattr(req.selector)
        dirs = path.split('/')
        dirs = list(map(unquote, dirs))
        dirs, file = dirs[:-1], dirs[-1]
        jeżeli dirs oraz nie dirs[0]:
            dirs = dirs[1:]
        spróbuj:
            fw = self.connect_ftp(user, dalejwd, host, port, dirs, req.timeout)
            type = file oraz 'I' albo 'D'
            dla attr w attrs:
                attr, value = splitvalue(attr)
                jeżeli attr.lower() == 'type' oraz \
                   value w ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()
            fp, retrlen = fw.retrfile(file, type)
            headers = ""
            mtype = mimetypes.guess_type(req.full_url)[0]
            jeżeli mtype:
                headers += "Content-type: %s\n" % mtype
            jeżeli retrlen jest nie Nic oraz retrlen >= 0:
                headers += "Content-length: %d\n" % retrlen
            headers = email.message_from_string(headers)
            zwróć addinfourl(fp, headers, req.full_url)
        wyjąwszy ftplib.all_errors jako exp:
            exc = URLError('ftp error: %r' % exp)
            podnieś exc.with_traceback(sys.exc_info()[2])

    def connect_ftp(self, user, dalejwd, host, port, dirs, timeout):
        zwróć ftpwrapper(user, dalejwd, host, port, dirs, timeout,
                          persistent=Nieprawda)

klasa CacheFTPHandler(FTPHandler):
    # XXX would be nice to have pluggable cache strategies
    # XXX this stuff jest definitely nie thread safe
    def __init__(self):
        self.cache = {}
        self.timeout = {}
        self.soonest = 0
        self.delay = 60
        self.max_conns = 16

    def setTimeout(self, t):
        self.delay = t

    def setMaxConns(self, m):
        self.max_conns = m

    def connect_ftp(self, user, dalejwd, host, port, dirs, timeout):
        key = user, host, port, '/'.join(dirs), timeout
        jeżeli key w self.cache:
            self.timeout[key] = time.time() + self.delay
        inaczej:
            self.cache[key] = ftpwrapper(user, dalejwd, host, port,
                                         dirs, timeout)
            self.timeout[key] = time.time() + self.delay
        self.check_cache()
        zwróć self.cache[key]

    def check_cache(self):
        # first check dla old ones
        t = time.time()
        jeżeli self.soonest <= t:
            dla k, v w list(self.timeout.items()):
                jeżeli v < t:
                    self.cache[k].close()
                    usuń self.cache[k]
                    usuń self.timeout[k]
        self.soonest = min(list(self.timeout.values()))

        # then check the size
        jeżeli len(self.cache) == self.max_conns:
            dla k, v w list(self.timeout.items()):
                jeżeli v == self.soonest:
                    usuń self.cache[k]
                    usuń self.timeout[k]
                    przerwij
            self.soonest = min(list(self.timeout.values()))

    def clear_cache(self):
        dla conn w self.cache.values():
            conn.close()
        self.cache.clear()
        self.timeout.clear()

klasa DataHandler(BaseHandler):
    def data_open(self, req):
        # data URLs jako specified w RFC 2397.
        #
        # ignores POSTed data
        #
        # syntax:
        # dataurl   := "data:" [ mediatype ] [ ";base64" ] "," data
        # mediatype := [ type "/" subtype ] *( ";" parameter )
        # data      := *urlchar
        # parameter := attribute "=" value
        url = req.full_url

        scheme, data = url.split(":",1)
        mediatype, data = data.split(",",1)

        # even base64 encoded data URLs might be quoted so unquote w any case:
        data = unquote_to_bytes(data)
        jeżeli mediatype.endswith(";base64"):
            data = base64.decodebytes(data)
            mediatype = mediatype[:-7]

        jeżeli nie mediatype:
            mediatype = "text/plain;charset=US-ASCII"

        headers = email.message_from_string("Content-type: %s\nContent-length: %d\n" %
            (mediatype, len(data)))

        zwróć addinfourl(io.BytesIO(data), headers, url)


# Code move z the old urllib module

MAXFTPCACHE = 10        # Trim the ftp cache beyond this size

# Helper dla non-unix systems
jeżeli os.name == 'nt':
    z nturl2path zaimportuj url2pathname, pathname2url
inaczej:
    def url2pathname(pathname):
        """OS-specific conversion z a relative URL of the 'file' scheme
        to a file system path; nie recommended dla general use."""
        zwróć unquote(pathname)

    def pathname2url(pathname):
        """OS-specific conversion z a file system path to a relative URL
        of the 'file' scheme; nie recommended dla general use."""
        zwróć quote(pathname)

# This really consists of two pieces:
# (1) a klasa which handles opening of all sorts of URLs
#     (plus assorted utilities etc.)
# (2) a set of functions dla parsing URLs
# XXX Should these be separated out into different modules?


ftpcache = {}
klasa URLopener:
    """Class to open URLs.
    This jest a klasa rather than just a subroutine because we may need
    more than one set of global protocol-specific options.
    Note -- this jest a base klasa dla those who don't want the
    automatic handling of errors type 302 (relocated) oraz 401
    (authorization needed)."""

    __tempfiles = Nic

    version = "Python-urllib/%s" % __version__

    # Constructor
    def __init__(self, proxies=Nic, **x509):
        msg = "%(class)s style of invoking requests jest deprecated. " \
              "Use newer urlopen functions/methods" % {'class': self.__class__.__name__}
        warnings.warn(msg, DeprecationWarning, stacklevel=3)
        jeżeli proxies jest Nic:
            proxies = getproxies()
        assert hasattr(proxies, 'keys'), "proxies must be a mapping"
        self.proxies = proxies
        self.key_file = x509.get('key_file')
        self.cert_file = x509.get('cert_file')
        self.addheaders = [('User-Agent', self.version)]
        self.__tempfiles = []
        self.__unlink = os.unlink # See cleanup()
        self.tempcache = Nic
        # Undocumented feature: jeżeli you assign {} to tempcache,
        # it jest used to cache files retrieved with
        # self.retrieve().  This jest nie enabled by default
        # since it does nie work dla changing documents (and I
        # haven't got the logic to check expiration headers
        # yet).
        self.ftpcache = ftpcache
        # Undocumented feature: you can use a different
        # ftp cache by assigning to the .ftpcache member;
        # w case you want logically independent URL openers
        # XXX This jest nie threadsafe.  Bah.

    def __del__(self):
        self.close()

    def close(self):
        self.cleanup()

    def cleanup(self):
        # This code sometimes runs when the rest of this module
        # has already been deleted, so it can't use any globals
        # albo zaimportuj anything.
        jeżeli self.__tempfiles:
            dla file w self.__tempfiles:
                spróbuj:
                    self.__unlink(file)
                wyjąwszy OSError:
                    dalej
            usuń self.__tempfiles[:]
        jeżeli self.tempcache:
            self.tempcache.clear()

    def addheader(self, *args):
        """Add a header to be used by the HTTP interface only
        e.g. u.addheader('Accept', 'sound/basic')"""
        self.addheaders.append(args)

    # External interface
    def open(self, fullurl, data=Nic):
        """Use URLopener().open(file) instead of open(file, 'r')."""
        fullurl = unwrap(to_bytes(fullurl))
        fullurl = quote(fullurl, safe="%/:=&?~#+!$,;'@()*[]|")
        jeżeli self.tempcache oraz fullurl w self.tempcache:
            filename, headers = self.tempcache[fullurl]
            fp = open(filename, 'rb')
            zwróć addinfourl(fp, headers, fullurl)
        urltype, url = splittype(fullurl)
        jeżeli nie urltype:
            urltype = 'file'
        jeżeli urltype w self.proxies:
            proxy = self.proxies[urltype]
            urltype, proxyhost = splittype(proxy)
            host, selector = splithost(proxyhost)
            url = (host, fullurl) # Signal special case to open_*()
        inaczej:
            proxy = Nic
        name = 'open_' + urltype
        self.type = urltype
        name = name.replace('-', '_')
        jeżeli nie hasattr(self, name):
            jeżeli proxy:
                zwróć self.open_unknown_proxy(proxy, fullurl, data)
            inaczej:
                zwróć self.open_unknown(fullurl, data)
        spróbuj:
            jeżeli data jest Nic:
                zwróć getattr(self, name)(url)
            inaczej:
                zwróć getattr(self, name)(url, data)
        wyjąwszy (HTTPError, URLError):
            podnieś
        wyjąwszy OSError jako msg:
            podnieś OSError('socket error', msg).with_traceback(sys.exc_info()[2])

    def open_unknown(self, fullurl, data=Nic):
        """Overridable interface to open unknown URL type."""
        type, url = splittype(fullurl)
        podnieś OSError('url error', 'unknown url type', type)

    def open_unknown_proxy(self, proxy, fullurl, data=Nic):
        """Overridable interface to open unknown URL type."""
        type, url = splittype(fullurl)
        podnieś OSError('url error', 'invalid proxy dla %s' % type, proxy)

    # External interface
    def retrieve(self, url, filename=Nic, reporthook=Nic, data=Nic):
        """retrieve(url) returns (filename, headers) dla a local object
        albo (tempfilename, headers) dla a remote object."""
        url = unwrap(to_bytes(url))
        jeżeli self.tempcache oraz url w self.tempcache:
            zwróć self.tempcache[url]
        type, url1 = splittype(url)
        jeżeli filename jest Nic oraz (nie type albo type == 'file'):
            spróbuj:
                fp = self.open_local_file(url1)
                hdrs = fp.info()
                fp.close()
                zwróć url2pathname(splithost(url1)[1]), hdrs
            wyjąwszy OSError jako msg:
                dalej
        fp = self.open(url, data)
        spróbuj:
            headers = fp.info()
            jeżeli filename:
                tfp = open(filename, 'wb')
            inaczej:
                zaimportuj tempfile
                garbage, path = splittype(url)
                garbage, path = splithost(path albo "")
                path, garbage = splitquery(path albo "")
                path, garbage = splitattr(path albo "")
                suffix = os.path.splitext(path)[1]
                (fd, filename) = tempfile.mkstemp(suffix)
                self.__tempfiles.append(filename)
                tfp = os.fdopen(fd, 'wb')
            spróbuj:
                result = filename, headers
                jeżeli self.tempcache jest nie Nic:
                    self.tempcache[url] = result
                bs = 1024*8
                size = -1
                read = 0
                blocknum = 0
                jeżeli "content-length" w headers:
                    size = int(headers["Content-Length"])
                jeżeli reporthook:
                    reporthook(blocknum, bs, size)
                dopóki 1:
                    block = fp.read(bs)
                    jeżeli nie block:
                        przerwij
                    read += len(block)
                    tfp.write(block)
                    blocknum += 1
                    jeżeli reporthook:
                        reporthook(blocknum, bs, size)
            w_końcu:
                tfp.close()
        w_końcu:
            fp.close()

        # podnieś exception jeżeli actual size does nie match content-length header
        jeżeli size >= 0 oraz read < size:
            podnieś ContentTooShortError(
                "retrieval incomplete: got only %i out of %i bytes"
                % (read, size), result)

        zwróć result

    # Each method named open_<type> knows how to open that type of URL

    def _open_generic_http(self, connection_factory, url, data):
        """Make an HTTP connection using connection_class.

        This jest an internal method that should be called from
        open_http() albo open_https().

        Arguments:
        - connection_factory should take a host name oraz zwróć an
          HTTPConnection instance.
        - url jest the url to retrieval albo a host, relative-path pair.
        - data jest payload dla a POST request albo Nic.
        """

        user_passwd = Nic
        proxy_passwd= Nic
        jeżeli isinstance(url, str):
            host, selector = splithost(url)
            jeżeli host:
                user_passwd, host = splituser(host)
                host = unquote(host)
            realhost = host
        inaczej:
            host, selector = url
            # check whether the proxy contains authorization information
            proxy_passwd, host = splituser(host)
            # now we proceed przy the url we want to obtain
            urltype, rest = splittype(selector)
            url = rest
            user_passwd = Nic
            jeżeli urltype.lower() != 'http':
                realhost = Nic
            inaczej:
                realhost, rest = splithost(rest)
                jeżeli realhost:
                    user_passwd, realhost = splituser(realhost)
                jeżeli user_passwd:
                    selector = "%s://%s%s" % (urltype, realhost, rest)
                jeżeli proxy_bypass(realhost):
                    host = realhost

        jeżeli nie host: podnieś OSError('http error', 'no host given')

        jeżeli proxy_passwd:
            proxy_passwd = unquote(proxy_passwd)
            proxy_auth = base64.b64encode(proxy_passwd.encode()).decode('ascii')
        inaczej:
            proxy_auth = Nic

        jeżeli user_passwd:
            user_passwd = unquote(user_passwd)
            auth = base64.b64encode(user_passwd.encode()).decode('ascii')
        inaczej:
            auth = Nic
        http_conn = connection_factory(host)
        headers = {}
        jeżeli proxy_auth:
            headers["Proxy-Authorization"] = "Basic %s" % proxy_auth
        jeżeli auth:
            headers["Authorization"] =  "Basic %s" % auth
        jeżeli realhost:
            headers["Host"] = realhost

        # Add Connection:close jako we don't support persistent connections yet.
        # This helps w closing the socket oraz avoiding ResourceWarning

        headers["Connection"] = "close"

        dla header, value w self.addheaders:
            headers[header] = value

        jeżeli data jest nie Nic:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            http_conn.request("POST", selector, data, headers)
        inaczej:
            http_conn.request("GET", selector, headers=headers)

        spróbuj:
            response = http_conn.getresponse()
        wyjąwszy http.client.BadStatusLine:
            # something went wrong przy the HTTP status line
            podnieś URLError("http protocol error: bad status line")

        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, oraz accepted.
        jeżeli 200 <= response.status < 300:
            zwróć addinfourl(response, response.msg, "http:" + url,
                              response.status)
        inaczej:
            zwróć self.http_error(
                url, response.fp,
                response.status, response.reason, response.msg, data)

    def open_http(self, url, data=Nic):
        """Use HTTP protocol."""
        zwróć self._open_generic_http(http.client.HTTPConnection, url, data)

    def http_error(self, url, fp, errcode, errmsg, headers, data=Nic):
        """Handle http errors.

        Derived klasa can override this, albo provide specific handlers
        named http_error_DDD where DDD jest the 3-digit error code."""
        # First check jeżeli there's a specific handler dla this error
        name = 'http_error_%d' % errcode
        jeżeli hasattr(self, name):
            method = getattr(self, name)
            jeżeli data jest Nic:
                result = method(url, fp, errcode, errmsg, headers)
            inaczej:
                result = method(url, fp, errcode, errmsg, headers, data)
            jeżeli result: zwróć result
        zwróć self.http_error_default(url, fp, errcode, errmsg, headers)

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        """Default error handler: close the connection oraz podnieś OSError."""
        fp.close()
        podnieś HTTPError(url, errcode, errmsg, headers, Nic)

    jeżeli _have_ssl:
        def _https_connection(self, host):
            zwróć http.client.HTTPSConnection(host,
                                           key_file=self.key_file,
                                           cert_file=self.cert_file)

        def open_https(self, url, data=Nic):
            """Use HTTPS protocol."""
            zwróć self._open_generic_http(self._https_connection, url, data)

    def open_file(self, url):
        """Use local file albo FTP depending on form of URL."""
        jeżeli nie isinstance(url, str):
            podnieś URLError('file error: proxy support dla file protocol currently nie implemented')
        jeżeli url[:2] == '//' oraz url[2:3] != '/' oraz url[2:12].lower() != 'localhost/':
            podnieś ValueError("file:// scheme jest supported only on localhost")
        inaczej:
            zwróć self.open_local_file(url)

    def open_local_file(self, url):
        """Use local file."""
        zaimportuj email.utils
        zaimportuj mimetypes
        host, file = splithost(url)
        localname = url2pathname(file)
        spróbuj:
            stats = os.stat(localname)
        wyjąwszy OSError jako e:
            podnieś URLError(e.strerror, e.filename)
        size = stats.st_size
        modified = email.utils.formatdate(stats.st_mtime, usegmt=Prawda)
        mtype = mimetypes.guess_type(url)[0]
        headers = email.message_from_string(
            'Content-Type: %s\nContent-Length: %d\nLast-modified: %s\n' %
            (mtype albo 'text/plain', size, modified))
        jeżeli nie host:
            urlfile = file
            jeżeli file[:1] == '/':
                urlfile = 'file://' + file
            zwróć addinfourl(open(localname, 'rb'), headers, urlfile)
        host, port = splitport(host)
        jeżeli (nie port
           oraz socket.gethostbyname(host) w ((localhost(),) + thishost())):
            urlfile = file
            jeżeli file[:1] == '/':
                urlfile = 'file://' + file
            albo_inaczej file[:2] == './':
                podnieś ValueError("local file url may start przy / albo file:. Unknown url of type: %s" % url)
            zwróć addinfourl(open(localname, 'rb'), headers, urlfile)
        podnieś URLError('local file error: nie on local host')

    def open_ftp(self, url):
        """Use FTP protocol."""
        jeżeli nie isinstance(url, str):
            podnieś URLError('ftp error: proxy support dla ftp protocol currently nie implemented')
        zaimportuj mimetypes
        host, path = splithost(url)
        jeżeli nie host: podnieś URLError('ftp error: no host given')
        host, port = splitport(host)
        user, host = splituser(host)
        jeżeli user: user, dalejwd = splitpasswd(user)
        inaczej: dalejwd = Nic
        host = unquote(host)
        user = unquote(user albo '')
        dalejwd = unquote(passwd albo '')
        host = socket.gethostbyname(host)
        jeżeli nie port:
            zaimportuj ftplib
            port = ftplib.FTP_PORT
        inaczej:
            port = int(port)
        path, attrs = splitattr(path)
        path = unquote(path)
        dirs = path.split('/')
        dirs, file = dirs[:-1], dirs[-1]
        jeżeli dirs oraz nie dirs[0]: dirs = dirs[1:]
        jeżeli dirs oraz nie dirs[0]: dirs[0] = '/'
        key = user, host, port, '/'.join(dirs)
        # XXX thread unsafe!
        jeżeli len(self.ftpcache) > MAXFTPCACHE:
            # Prune the cache, rather arbitrarily
            dla k w list(self.ftpcache):
                jeżeli k != key:
                    v = self.ftpcache[k]
                    usuń self.ftpcache[k]
                    v.close()
        spróbuj:
            jeżeli key nie w self.ftpcache:
                self.ftpcache[key] = \
                    ftpwrapper(user, dalejwd, host, port, dirs)
            jeżeli nie file: type = 'D'
            inaczej: type = 'I'
            dla attr w attrs:
                attr, value = splitvalue(attr)
                jeżeli attr.lower() == 'type' oraz \
                   value w ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()
            (fp, retrlen) = self.ftpcache[key].retrfile(file, type)
            mtype = mimetypes.guess_type("ftp:" + url)[0]
            headers = ""
            jeżeli mtype:
                headers += "Content-Type: %s\n" % mtype
            jeżeli retrlen jest nie Nic oraz retrlen >= 0:
                headers += "Content-Length: %d\n" % retrlen
            headers = email.message_from_string(headers)
            zwróć addinfourl(fp, headers, "ftp:" + url)
        wyjąwszy ftperrors() jako exp:
            podnieś URLError('ftp error %r' % exp).with_traceback(sys.exc_info()[2])

    def open_data(self, url, data=Nic):
        """Use "data" URL."""
        jeżeli nie isinstance(url, str):
            podnieś URLError('data error: proxy support dla data protocol currently nie implemented')
        # ignore POSTed data
        #
        # syntax of data URLs:
        # dataurl   := "data:" [ mediatype ] [ ";base64" ] "," data
        # mediatype := [ type "/" subtype ] *( ";" parameter )
        # data      := *urlchar
        # parameter := attribute "=" value
        spróbuj:
            [type, data] = url.split(',', 1)
        wyjąwszy ValueError:
            podnieś OSError('data error', 'bad data URL')
        jeżeli nie type:
            type = 'text/plain;charset=US-ASCII'
        semi = type.rfind(';')
        jeżeli semi >= 0 oraz '=' nie w type[semi:]:
            encoding = type[semi+1:]
            type = type[:semi]
        inaczej:
            encoding = ''
        msg = []
        msg.append('Date: %s'%time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                                            time.gmtime(time.time())))
        msg.append('Content-type: %s' % type)
        jeżeli encoding == 'base64':
            # XXX jest this encoding/decoding ok?
            data = base64.decodebytes(data.encode('ascii')).decode('latin-1')
        inaczej:
            data = unquote(data)
        msg.append('Content-Length: %d' % len(data))
        msg.append('')
        msg.append(data)
        msg = '\n'.join(msg)
        headers = email.message_from_string(msg)
        f = io.StringIO(msg)
        #f.fileno = Nic     # needed dla addinfourl
        zwróć addinfourl(f, headers, url)


klasa FancyURLopener(URLopener):
    """Derived klasa przy handlers dla errors we can handle (perhaps)."""

    def __init__(self, *args, **kwargs):
        URLopener.__init__(self, *args, **kwargs)
        self.auth_cache = {}
        self.tries = 0
        self.maxtries = 10

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        """Default error handling -- don't podnieś an exception."""
        zwróć addinfourl(fp, headers, "http:" + url, errcode)

    def http_error_302(self, url, fp, errcode, errmsg, headers, data=Nic):
        """Error 302 -- relocated (temporarily)."""
        self.tries += 1
        jeżeli self.maxtries oraz self.tries >= self.maxtries:
            jeżeli hasattr(self, "http_error_500"):
                meth = self.http_error_500
            inaczej:
                meth = self.http_error_default
            self.tries = 0
            zwróć meth(url, fp, 500,
                        "Internal Server Error: Redirect Recursion", headers)
        result = self.redirect_internal(url, fp, errcode, errmsg, headers,
                                        data)
        self.tries = 0
        zwróć result

    def redirect_internal(self, url, fp, errcode, errmsg, headers, data):
        jeżeli 'location' w headers:
            newurl = headers['location']
        albo_inaczej 'uri' w headers:
            newurl = headers['uri']
        inaczej:
            zwróć
        fp.close()

        # In case the server sent a relative URL, join przy original:
        newurl = urljoin(self.type + ":" + url, newurl)

        urlparts = urlparse(newurl)

        # For security reasons, we don't allow redirection to anything other
        # than http, https oraz ftp.

        # We are using newer HTTPError przy older redirect_internal method
        # This older method will get deprecated w 3.3

        jeżeli urlparts.scheme nie w ('http', 'https', 'ftp', ''):
            podnieś HTTPError(newurl, errcode,
                            errmsg +
                            " Redirection to url '%s' jest nie allowed." % newurl,
                            headers, fp)

        zwróć self.open(newurl)

    def http_error_301(self, url, fp, errcode, errmsg, headers, data=Nic):
        """Error 301 -- also relocated (permanently)."""
        zwróć self.http_error_302(url, fp, errcode, errmsg, headers, data)

    def http_error_303(self, url, fp, errcode, errmsg, headers, data=Nic):
        """Error 303 -- also relocated (essentially identical to 302)."""
        zwróć self.http_error_302(url, fp, errcode, errmsg, headers, data)

    def http_error_307(self, url, fp, errcode, errmsg, headers, data=Nic):
        """Error 307 -- relocated, but turn POST into error."""
        jeżeli data jest Nic:
            zwróć self.http_error_302(url, fp, errcode, errmsg, headers, data)
        inaczej:
            zwróć self.http_error_default(url, fp, errcode, errmsg, headers)

    def http_error_401(self, url, fp, errcode, errmsg, headers, data=Nic,
            retry=Nieprawda):
        """Error 401 -- authentication required.
        This function supports Basic authentication only."""
        jeżeli 'www-authenticate' nie w headers:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        stuff = headers['www-authenticate']
        match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
        jeżeli nie match:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        scheme, realm = match.groups()
        jeżeli scheme.lower() != 'basic':
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        jeżeli nie respróbuj:
            URLopener.http_error_default(self, url, fp, errcode, errmsg,
                    headers)
        name = 'retry_' + self.type + '_basic_auth'
        jeżeli data jest Nic:
            zwróć getattr(self,name)(url, realm)
        inaczej:
            zwróć getattr(self,name)(url, realm, data)

    def http_error_407(self, url, fp, errcode, errmsg, headers, data=Nic,
            retry=Nieprawda):
        """Error 407 -- proxy authentication required.
        This function supports Basic authentication only."""
        jeżeli 'proxy-authenticate' nie w headers:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        stuff = headers['proxy-authenticate']
        match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
        jeżeli nie match:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        scheme, realm = match.groups()
        jeżeli scheme.lower() != 'basic':
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        jeżeli nie respróbuj:
            URLopener.http_error_default(self, url, fp, errcode, errmsg,
                    headers)
        name = 'retry_proxy_' + self.type + '_basic_auth'
        jeżeli data jest Nic:
            zwróć getattr(self,name)(url, realm)
        inaczej:
            zwróć getattr(self,name)(url, realm, data)

    def retry_proxy_http_basic_auth(self, url, realm, data=Nic):
        host, selector = splithost(url)
        newurl = 'http://' + host + selector
        proxy = self.proxies['http']
        urltype, proxyhost = splittype(proxy)
        proxyhost, proxyselector = splithost(proxyhost)
        i = proxyhost.find('@') + 1
        proxyhost = proxyhost[i:]
        user, dalejwd = self.get_user_passwd(proxyhost, realm, i)
        jeżeli nie (user albo dalejwd): zwróć Nic
        proxyhost = "%s:%s@%s" % (quote(user, safe=''),
                                  quote(passwd, safe=''), proxyhost)
        self.proxies['http'] = 'http://' + proxyhost + proxyselector
        jeżeli data jest Nic:
            zwróć self.open(newurl)
        inaczej:
            zwróć self.open(newurl, data)

    def retry_proxy_https_basic_auth(self, url, realm, data=Nic):
        host, selector = splithost(url)
        newurl = 'https://' + host + selector
        proxy = self.proxies['https']
        urltype, proxyhost = splittype(proxy)
        proxyhost, proxyselector = splithost(proxyhost)
        i = proxyhost.find('@') + 1
        proxyhost = proxyhost[i:]
        user, dalejwd = self.get_user_passwd(proxyhost, realm, i)
        jeżeli nie (user albo dalejwd): zwróć Nic
        proxyhost = "%s:%s@%s" % (quote(user, safe=''),
                                  quote(passwd, safe=''), proxyhost)
        self.proxies['https'] = 'https://' + proxyhost + proxyselector
        jeżeli data jest Nic:
            zwróć self.open(newurl)
        inaczej:
            zwróć self.open(newurl, data)

    def retry_http_basic_auth(self, url, realm, data=Nic):
        host, selector = splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, dalejwd = self.get_user_passwd(host, realm, i)
        jeżeli nie (user albo dalejwd): zwróć Nic
        host = "%s:%s@%s" % (quote(user, safe=''),
                             quote(passwd, safe=''), host)
        newurl = 'http://' + host + selector
        jeżeli data jest Nic:
            zwróć self.open(newurl)
        inaczej:
            zwróć self.open(newurl, data)

    def retry_https_basic_auth(self, url, realm, data=Nic):
        host, selector = splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, dalejwd = self.get_user_passwd(host, realm, i)
        jeżeli nie (user albo dalejwd): zwróć Nic
        host = "%s:%s@%s" % (quote(user, safe=''),
                             quote(passwd, safe=''), host)
        newurl = 'https://' + host + selector
        jeżeli data jest Nic:
            zwróć self.open(newurl)
        inaczej:
            zwróć self.open(newurl, data)

    def get_user_passwd(self, host, realm, clear_cache=0):
        key = realm + '@' + host.lower()
        jeżeli key w self.auth_cache:
            jeżeli clear_cache:
                usuń self.auth_cache[key]
            inaczej:
                zwróć self.auth_cache[key]
        user, dalejwd = self.prompt_user_passwd(host, realm)
        jeżeli user albo dalejwd: self.auth_cache[key] = (user, dalejwd)
        zwróć user, dalejwd

    def prompt_user_passwd(self, host, realm):
        """Override this w a GUI environment!"""
        zaimportuj getpass
        spróbuj:
            user = input("Enter username dla %s at %s: " % (realm, host))
            dalejwd = getpass.getpass("Enter dalejword dla %s w %s at %s: " %
                (user, realm, host))
            zwróć user, dalejwd
        wyjąwszy KeyboardInterrupt:
            print()
            zwróć Nic, Nic


# Utility functions

_localhost = Nic
def localhost():
    """Return the IP address of the magic hostname 'localhost'."""
    global _localhost
    jeżeli _localhost jest Nic:
        _localhost = socket.gethostbyname('localhost')
    zwróć _localhost

_thishost = Nic
def thishost():
    """Return the IP addresses of the current host."""
    global _thishost
    jeżeli _thishost jest Nic:
        spróbuj:
            _thishost = tuple(socket.gethostbyname_ex(socket.gethostname())[2])
        wyjąwszy socket.gaierror:
            _thishost = tuple(socket.gethostbyname_ex('localhost')[2])
    zwróć _thishost

_ftperrors = Nic
def ftperrors():
    """Return the set of errors podnieśd by the FTP class."""
    global _ftperrors
    jeżeli _ftperrors jest Nic:
        zaimportuj ftplib
        _ftperrors = ftplib.all_errors
    zwróć _ftperrors

_noheaders = Nic
def noheaders():
    """Return an empty email Message object."""
    global _noheaders
    jeżeli _noheaders jest Nic:
        _noheaders = email.message_from_string("")
    zwróć _noheaders


# Utility classes

klasa ftpwrapper:
    """Class used by open_ftp() dla cache of open FTP connections."""

    def __init__(self, user, dalejwd, host, port, dirs, timeout=Nic,
                 persistent=Prawda):
        self.user = user
        self.passwd = dalejwd
        self.host = host
        self.port = port
        self.dirs = dirs
        self.timeout = timeout
        self.refcount = 0
        self.keepalive = persistent
        spróbuj:
            self.init()
        wyjąwszy:
            self.close()
            podnieś

    def init(self):
        zaimportuj ftplib
        self.busy = 0
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, self.port, self.timeout)
        self.ftp.login(self.user, self.passwd)
        _target = '/'.join(self.dirs)
        self.ftp.cwd(_target)

    def retrfile(self, file, type):
        zaimportuj ftplib
        self.endtransfer()
        jeżeli type w ('d', 'D'): cmd = 'TYPE A'; isdir = 1
        inaczej: cmd = 'TYPE ' + type; isdir = 0
        spróbuj:
            self.ftp.voidcmd(cmd)
        wyjąwszy ftplib.all_errors:
            self.init()
            self.ftp.voidcmd(cmd)
        conn = Nic
        jeżeli file oraz nie isdir:
            # Try to retrieve jako a file
            spróbuj:
                cmd = 'RETR ' + file
                conn, retrlen = self.ftp.ntransfercmd(cmd)
            wyjąwszy ftplib.error_perm jako reason:
                jeżeli str(reason)[:3] != '550':
                    podnieś URLError('ftp error: %r' % reason).with_traceback(
                        sys.exc_info()[2])
        jeżeli nie conn:
            # Set transfer mode to ASCII!
            self.ftp.voidcmd('TYPE A')
            # Try a directory listing. Verify that directory exists.
            jeżeli file:
                pwd = self.ftp.pwd()
                spróbuj:
                    spróbuj:
                        self.ftp.cwd(file)
                    wyjąwszy ftplib.error_perm jako reason:
                        podnieś URLError('ftp error: %r' % reason) z reason
                w_końcu:
                    self.ftp.cwd(pwd)
                cmd = 'LIST ' + file
            inaczej:
                cmd = 'LIST'
            conn, retrlen = self.ftp.ntransfercmd(cmd)
        self.busy = 1

        ftpobj = addclosehook(conn.makefile('rb'), self.file_close)
        self.refcount += 1
        conn.close()
        # Pass back both a suitably decorated object oraz a retrieval length
        zwróć (ftpobj, retrlen)

    def endtransfer(self):
        self.busy = 0

    def close(self):
        self.keepalive = Nieprawda
        jeżeli self.refcount <= 0:
            self.real_close()

    def file_close(self):
        self.endtransfer()
        self.refcount -= 1
        jeżeli self.refcount <= 0 oraz nie self.keepalive:
            self.real_close()

    def real_close(self):
        self.endtransfer()
        spróbuj:
            self.ftp.close()
        wyjąwszy ftperrors():
            dalej

# Proxy handling
def getproxies_environment():
    """Return a dictionary of scheme -> proxy server URL mappings.

    Scan the environment dla variables named <scheme>_proxy;
    this seems to be the standard convention.  If you need a
    different way, you can dalej a proxies dictionary to the
    [Fancy]URLopener constructor.

    """
    proxies = {}
    dla name, value w os.environ.items():
        name = name.lower()
        jeżeli value oraz name[-6:] == '_proxy':
            proxies[name[:-6]] = value
    zwróć proxies

def proxy_bypass_environment(host):
    """Test jeżeli proxies should nie be used dla a particular host.

    Checks the environment dla a variable named no_proxy, which should
    be a list of DNS suffixes separated by commas, albo '*' dla all hosts.
    """
    no_proxy = os.environ.get('no_proxy', '') albo os.environ.get('NO_PROXY', '')
    # '*' jest special case dla always bypass
    jeżeli no_proxy == '*':
        zwróć 1
    # strip port off host
    hostonly, port = splitport(host)
    # check jeżeli the host ends przy any of the DNS suffixes
    no_proxy_list = [proxy.strip() dla proxy w no_proxy.split(',')]
    dla name w no_proxy_list:
        jeżeli name oraz (hostonly.endswith(name) albo host.endswith(name)):
            zwróć 1
    # otherwise, don't bypass
    zwróć 0


# This code tests an OSX specific data structure but jest testable on all
# platforms
def _proxy_bypass_macosx_sysconf(host, proxy_settings):
    """
    Return Prawda iff this host shouldn't be accessed using a proxy

    This function uses the MacOSX framework SystemConfiguration
    to fetch the proxy information.

    proxy_settings come z _scproxy._get_proxy_settings albo get mocked ie:
    { 'exclude_simple': bool,
      'exceptions': ['foo.bar', '*.bar.com', '127.0.0.1', '10.1', '10.0/16']
    }
    """
    z fnmatch zaimportuj fnmatch

    hostonly, port = splitport(host)

    def ip2num(ipAddr):
        parts = ipAddr.split('.')
        parts = list(map(int, parts))
        jeżeli len(parts) != 4:
            parts = (parts + [0, 0, 0, 0])[:4]
        zwróć (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

    # Check dla simple host names:
    jeżeli '.' nie w host:
        jeżeli proxy_settings['exclude_simple']:
            zwróć Prawda

    hostIP = Nic

    dla value w proxy_settings.get('exceptions', ()):
        # Items w the list are strings like these: *.local, 169.254/16
        jeżeli nie value: kontynuuj

        m = re.match(r"(\d+(?:\.\d+)*)(/\d+)?", value)
        jeżeli m jest nie Nic:
            jeżeli hostIP jest Nic:
                spróbuj:
                    hostIP = socket.gethostbyname(hostonly)
                    hostIP = ip2num(hostIP)
                wyjąwszy OSError:
                    kontynuuj

            base = ip2num(m.group(1))
            mask = m.group(2)
            jeżeli mask jest Nic:
                mask = 8 * (m.group(1).count('.') + 1)
            inaczej:
                mask = int(mask[1:])
            mask = 32 - mask

            jeżeli (hostIP >> mask) == (base >> mask):
                zwróć Prawda

        albo_inaczej fnmatch(host, value):
            zwróć Prawda

    zwróć Nieprawda


jeżeli sys.platform == 'darwin':
    z _scproxy zaimportuj _get_proxy_settings, _get_proxies

    def proxy_bypass_macosx_sysconf(host):
        proxy_settings = _get_proxy_settings()
        zwróć _proxy_bypass_macosx_sysconf(host, proxy_settings)

    def getproxies_macosx_sysconf():
        """Return a dictionary of scheme -> proxy server URL mappings.

        This function uses the MacOSX framework SystemConfiguration
        to fetch the proxy information.
        """
        zwróć _get_proxies()



    def proxy_bypass(host):
        jeżeli getproxies_environment():
            zwróć proxy_bypass_environment(host)
        inaczej:
            zwróć proxy_bypass_macosx_sysconf(host)

    def getproxies():
        zwróć getproxies_environment() albo getproxies_macosx_sysconf()


albo_inaczej os.name == 'nt':
    def getproxies_registry():
        """Return a dictionary of scheme -> proxy server URL mappings.

        Win32 uses the registry to store proxies.

        """
        proxies = {}
        spróbuj:
            zaimportuj winreg
        wyjąwszy ImportError:
            # Std module, so should be around - but you never know!
            zwróć proxies
        spróbuj:
            internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
            proxyEnable = winreg.QueryValueEx(internetSettings,
                                               'ProxyEnable')[0]
            jeżeli proxyEnable:
                # Returned jako Unicode but problems jeżeli nie converted to ASCII
                proxyServer = str(winreg.QueryValueEx(internetSettings,
                                                       'ProxyServer')[0])
                jeżeli '=' w proxyServer:
                    # Per-protocol settings
                    dla p w proxyServer.split(';'):
                        protocol, address = p.split('=', 1)
                        # See jeżeli address has a type:// prefix
                        jeżeli nie re.match('^([^/:]+)://', address):
                            address = '%s://%s' % (protocol, address)
                        proxies[protocol] = address
                inaczej:
                    # Use one setting dla all protocols
                    jeżeli proxyServer[:5] == 'http:':
                        proxies['http'] = proxyServer
                    inaczej:
                        proxies['http'] = 'http://%s' % proxyServer
                        proxies['https'] = 'https://%s' % proxyServer
                        proxies['ftp'] = 'ftp://%s' % proxyServer
            internetSettings.Close()
        wyjąwszy (OSError, ValueError, TypeError):
            # Either registry key nie found etc, albo the value w an
            # unexpected format.
            # proxies already set up to be empty so nothing to do
            dalej
        zwróć proxies

    def getproxies():
        """Return a dictionary of scheme -> proxy server URL mappings.

        Returns settings gathered z the environment, jeżeli specified,
        albo the registry.

        """
        zwróć getproxies_environment() albo getproxies_registry()

    def proxy_bypass_registry(host):
        spróbuj:
            zaimportuj winreg
        wyjąwszy ImportError:
            # Std modules, so should be around - but you never know!
            zwróć 0
        spróbuj:
            internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
            proxyEnable = winreg.QueryValueEx(internetSettings,
                                               'ProxyEnable')[0]
            proxyOverride = str(winreg.QueryValueEx(internetSettings,
                                                     'ProxyOverride')[0])
            # ^^^^ Returned jako Unicode but problems jeżeli nie converted to ASCII
        wyjąwszy OSError:
            zwróć 0
        jeżeli nie proxyEnable albo nie proxyOverride:
            zwróć 0
        # try to make a host list z name oraz IP address.
        rawHost, port = splitport(host)
        host = [rawHost]
        spróbuj:
            addr = socket.gethostbyname(rawHost)
            jeżeli addr != rawHost:
                host.append(addr)
        wyjąwszy OSError:
            dalej
        spróbuj:
            fqdn = socket.getfqdn(rawHost)
            jeżeli fqdn != rawHost:
                host.append(fqdn)
        wyjąwszy OSError:
            dalej
        # make a check value list z the registry enspróbuj: replace the
        # '<local>' string by the localhost entry oraz the corresponding
        # canonical entry.
        proxyOverride = proxyOverride.split(';')
        # now check jeżeli we match one of the registry values.
        dla test w proxyOverride:
            jeżeli test == '<local>':
                jeżeli '.' nie w rawHost:
                    zwróć 1
            test = test.replace(".", r"\.")     # mask dots
            test = test.replace("*", r".*")     # change glob sequence
            test = test.replace("?", r".")      # change glob char
            dla val w host:
                jeżeli re.match(test, val, re.I):
                    zwróć 1
        zwróć 0

    def proxy_bypass(host):
        """Return a dictionary of scheme -> proxy server URL mappings.

        Returns settings gathered z the environment, jeżeli specified,
        albo the registry.

        """
        jeżeli getproxies_environment():
            zwróć proxy_bypass_environment(host)
        inaczej:
            zwróć proxy_bypass_registry(host)

inaczej:
    # By default use environment variables
    getproxies = getproxies_environment
    proxy_bypass = proxy_bypass_environment
