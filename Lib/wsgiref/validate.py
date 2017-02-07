# (c) 2005 Ian Bicking oraz contributors; written dla Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Also licenced under the Apache License, 2.0: http://opensource.org/licenses/apache2.0.php
# Licensed to PSF under a Contributor Agreement
"""
Middleware to check dla obedience to the WSGI specification.

Some of the things this checks:

* Signature of the application oraz start_response (including that
  keyword arguments are nie used).

* Environment checks:

  - Environment jest a dictionary (and nie a subclass).

  - That all the required keys are w the environment: REQUEST_METHOD,
    SERVER_NAME, SERVER_PORT, wsgi.version, wsgi.input, wsgi.errors,
    wsgi.multithread, wsgi.multiprocess, wsgi.run_once

  - That HTTP_CONTENT_TYPE oraz HTTP_CONTENT_LENGTH are nie w the
    environment (these headers should appear jako CONTENT_LENGTH oraz
    CONTENT_TYPE).

  - Warns jeżeli QUERY_STRING jest missing, jako the cgi module acts
    unpredictably w that case.

  - That CGI-style variables (that don't contain a .) have
    (non-unicode) string values

  - That wsgi.version jest a tuple

  - That wsgi.url_scheme jest 'http' albo 'https' (@@: jest this too
    restrictive?)

  - Warns jeżeli the REQUEST_METHOD jest nie known (@@: probably too
    restrictive).

  - That SCRIPT_NAME oraz PATH_INFO are empty albo start przy /

  - That at least one of SCRIPT_NAME albo PATH_INFO are set.

  - That CONTENT_LENGTH jest a positive integer.

  - That SCRIPT_NAME jest nie '/' (it should be '', oraz PATH_INFO should
    be '/').

  - That wsgi.input has the methods read, readline, readlines, oraz
    __iter__

  - That wsgi.errors has the methods flush, write, writelines

* The status jest a string, contains a space, starts przy an integer,
  oraz that integer jest w range (> 100).

* That the headers jest a list (nie a subclass, nie another kind of
  sequence).

* That the items of the headers are tuples of strings.

* That there jest no 'status' header (that jest used w CGI, but nie w
  WSGI).

* That the headers don't contain newlines albo colons, end w _ albo -, albo
  contain characters codes below 037.

* That Content-Type jest given jeżeli there jest content (CGI often has a
  default content type, but WSGI does not).

* That no Content-Type jest given when there jest no content (@@: jest this
  too restrictive?)

* That the exc_info argument to start_response jest a tuple albo Nic.

* That all calls to the writer are przy strings, oraz no other methods
  on the writer are accessed.

* That wsgi.input jest used properly:

  - .read() jest called przy zero albo one argument

  - That it returns a string

  - That readline, readlines, oraz __iter__ zwróć strings

  - That .close() jest nie called

  - No other methods are provided

* That wsgi.errors jest used properly:

  - .write() oraz .writelines() jest called przy a string

  - That .close() jest nie called, oraz no other methods are provided.

* The response iterator:

  - That it jest nie a string (it should be a list of a single string; a
    string will work, but perform horribly).

  - That .__next__() returns a string

  - That the iterator jest nie iterated over until start_response has
    been called (that can signal either a server albo application
    error).

  - That .close() jest called (doesn't podnieś exception, only prints to
    sys.stderr, because we only know it isn't called when the object
    jest garbage collected).
"""
__all__ = ['validator']


zaimportuj re
zaimportuj sys
zaimportuj warnings

header_re = re.compile(r'^[a-zA-Z][a-zA-Z0-9\-_]*$')
bad_header_value_re = re.compile(r'[\000-\037]')

klasa WSGIWarning(Warning):
    """
    Raised w response to WSGI-spec-related warnings
    """

def assert_(cond, *args):
    jeżeli nie cond:
        podnieś AssertionError(*args)

def check_string_type(value, title):
    jeżeli type (value) jest str:
        zwróć value
    podnieś AssertionError(
        "{0} must be of type str (got {1})".format(title, repr(value)))

def validator(application):

    """
    When applied between a WSGI server oraz a WSGI application, this
    middleware will check dla WSGI compliancy on a number of levels.
    This middleware does nie modify the request albo response w any
    way, but will podnieś an AssertionError jeżeli anything seems off
    (wyjąwszy dla a failure to close the application iterator, which
    will be printed to stderr -- there's no way to podnieś an exception
    at that point).
    """

    def lint_app(*args, **kw):
        assert_(len(args) == 2, "Two arguments required")
        assert_(nie kw, "No keyword arguments allowed")
        environ, start_response = args

        check_environ(environ)

        # We use this to check jeżeli the application returns without
        # calling start_response:
        start_response_started = []

        def start_response_wrapper(*args, **kw):
            assert_(len(args) == 2 albo len(args) == 3, (
                "Invalid number of arguments: %s" % (args,)))
            assert_(nie kw, "No keyword arguments allowed")
            status = args[0]
            headers = args[1]
            jeżeli len(args) == 3:
                exc_info = args[2]
            inaczej:
                exc_info = Nic

            check_status(status)
            check_headers(headers)
            check_content_type(status, headers)
            check_exc_info(exc_info)

            start_response_started.append(Nic)
            zwróć WriteWrapper(start_response(*args))

        environ['wsgi.input'] = InputWrapper(environ['wsgi.input'])
        environ['wsgi.errors'] = ErrorWrapper(environ['wsgi.errors'])

        iterator = application(environ, start_response_wrapper)
        assert_(iterator jest nie Nic oraz iterator != Nieprawda,
            "The application must zwróć an iterator, jeżeli only an empty list")

        check_iterator(iterator)

        zwróć IteratorWrapper(iterator, start_response_started)

    zwróć lint_app

klasa InputWrapper:

    def __init__(self, wsgi_input):
        self.input = wsgi_input

    def read(self, *args):
        assert_(len(args) == 1)
        v = self.input.read(*args)
        assert_(type(v) jest bytes)
        zwróć v

    def readline(self, *args):
        assert_(len(args) <= 1)
        v = self.input.readline(*args)
        assert_(type(v) jest bytes)
        zwróć v

    def readlines(self, *args):
        assert_(len(args) <= 1)
        lines = self.input.readlines(*args)
        assert_(type(lines) jest list)
        dla line w lines:
            assert_(type(line) jest bytes)
        zwróć lines

    def __iter__(self):
        dopóki 1:
            line = self.readline()
            jeżeli nie line:
                zwróć
            uzyskaj line

    def close(self):
        assert_(0, "input.close() must nie be called")

klasa ErrorWrapper:

    def __init__(self, wsgi_errors):
        self.errors = wsgi_errors

    def write(self, s):
        assert_(type(s) jest str)
        self.errors.write(s)

    def flush(self):
        self.errors.flush()

    def writelines(self, seq):
        dla line w seq:
            self.write(line)

    def close(self):
        assert_(0, "errors.close() must nie be called")

klasa WriteWrapper:

    def __init__(self, wsgi_writer):
        self.writer = wsgi_writer

    def __call__(self, s):
        assert_(type(s) jest bytes)
        self.writer(s)

klasa PartialIteratorWrapper:

    def __init__(self, wsgi_iterator):
        self.iterator = wsgi_iterator

    def __iter__(self):
        # We want to make sure __iter__ jest called
        zwróć IteratorWrapper(self.iterator, Nic)

klasa IteratorWrapper:

    def __init__(self, wsgi_iterator, check_start_response):
        self.original_iterator = wsgi_iterator
        self.iterator = iter(wsgi_iterator)
        self.closed = Nieprawda
        self.check_start_response = check_start_response

    def __iter__(self):
        zwróć self

    def __next__(self):
        assert_(nie self.closed,
            "Iterator read after closed")
        v = next(self.iterator)
        jeżeli type(v) jest nie bytes:
            assert_(Nieprawda, "Iterator uzyskajed non-bytestring (%r)" % (v,))
        jeżeli self.check_start_response jest nie Nic:
            assert_(self.check_start_response,
                "The application returns oraz we started iterating over its body, but start_response has nie yet been called")
            self.check_start_response = Nic
        zwróć v

    def close(self):
        self.closed = Prawda
        jeżeli hasattr(self.original_iterator, 'close'):
            self.original_iterator.close()

    def __del__(self):
        jeżeli nie self.closed:
            sys.stderr.write(
                "Iterator garbage collected without being closed")
        assert_(self.closed,
            "Iterator garbage collected without being closed")

def check_environ(environ):
    assert_(type(environ) jest dict,
        "Environment jest nie of the right type: %r (environment: %r)"
        % (type(environ), environ))

    dla key w ['REQUEST_METHOD', 'SERVER_NAME', 'SERVER_PORT',
                'wsgi.version', 'wsgi.input', 'wsgi.errors',
                'wsgi.multithread', 'wsgi.multiprocess',
                'wsgi.run_once']:
        assert_(key w environ,
            "Environment missing required key: %r" % (key,))

    dla key w ['HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH']:
        assert_(key nie w environ,
            "Environment should nie have the key: %s "
            "(use %s instead)" % (key, key[5:]))

    jeżeli 'QUERY_STRING' nie w environ:
        warnings.warn(
            'QUERY_STRING jest nie w the WSGI environment; the cgi '
            'module will use sys.argv when this variable jest missing, '
            'so application errors are more likely',
            WSGIWarning)

    dla key w environ.keys():
        jeżeli '.' w key:
            # Extension, we don't care about its type
            kontynuuj
        assert_(type(environ[key]) jest str,
            "Environmental variable %s jest nie a string: %r (value: %r)"
            % (key, type(environ[key]), environ[key]))

    assert_(type(environ['wsgi.version']) jest tuple,
        "wsgi.version should be a tuple (%r)" % (environ['wsgi.version'],))
    assert_(environ['wsgi.url_scheme'] w ('http', 'https'),
        "wsgi.url_scheme unknown: %r" % environ['wsgi.url_scheme'])

    check_input(environ['wsgi.input'])
    check_errors(environ['wsgi.errors'])

    # @@: these need filling out:
    jeżeli environ['REQUEST_METHOD'] nie w (
        'GET', 'HEAD', 'POST', 'OPTIONS', 'PATCH', 'PUT', 'DELETE', 'TRACE'):
        warnings.warn(
            "Unknown REQUEST_METHOD: %r" % environ['REQUEST_METHOD'],
            WSGIWarning)

    assert_(nie environ.get('SCRIPT_NAME')
            albo environ['SCRIPT_NAME'].startswith('/'),
        "SCRIPT_NAME doesn't start przy /: %r" % environ['SCRIPT_NAME'])
    assert_(nie environ.get('PATH_INFO')
            albo environ['PATH_INFO'].startswith('/'),
        "PATH_INFO doesn't start przy /: %r" % environ['PATH_INFO'])
    jeżeli environ.get('CONTENT_LENGTH'):
        assert_(int(environ['CONTENT_LENGTH']) >= 0,
            "Invalid CONTENT_LENGTH: %r" % environ['CONTENT_LENGTH'])

    jeżeli nie environ.get('SCRIPT_NAME'):
        assert_('PATH_INFO' w environ,
            "One of SCRIPT_NAME albo PATH_INFO are required (PATH_INFO "
            "should at least be '/' jeżeli SCRIPT_NAME jest empty)")
    assert_(environ.get('SCRIPT_NAME') != '/',
        "SCRIPT_NAME cannot be '/'; it should instead be '', oraz "
        "PATH_INFO should be '/'")

def check_input(wsgi_input):
    dla attr w ['read', 'readline', 'readlines', '__iter__']:
        assert_(hasattr(wsgi_input, attr),
            "wsgi.input (%r) doesn't have the attribute %s"
            % (wsgi_input, attr))

def check_errors(wsgi_errors):
    dla attr w ['flush', 'write', 'writelines']:
        assert_(hasattr(wsgi_errors, attr),
            "wsgi.errors (%r) doesn't have the attribute %s"
            % (wsgi_errors, attr))

def check_status(status):
    status = check_string_type(status, "Status")
    # Implicitly check that we can turn it into an integer:
    status_code = status.split(Nic, 1)[0]
    assert_(len(status_code) == 3,
        "Status codes must be three characters: %r" % status_code)
    status_int = int(status_code)
    assert_(status_int >= 100, "Status code jest invalid: %r" % status_int)
    jeżeli len(status) < 4 albo status[3] != ' ':
        warnings.warn(
            "The status string (%r) should be a three-digit integer "
            "followed by a single space oraz a status explanation"
            % status, WSGIWarning)

def check_headers(headers):
    assert_(type(headers) jest list,
        "Headers (%r) must be of type list: %r"
        % (headers, type(headers)))
    header_names = {}
    dla item w headers:
        assert_(type(item) jest tuple,
            "Individual headers (%r) must be of type tuple: %r"
            % (item, type(item)))
        assert_(len(item) == 2)
        name, value = item
        name = check_string_type(name, "Header name")
        value = check_string_type(value, "Header value")
        assert_(name.lower() != 'status',
            "The Status header cannot be used; it conflicts przy CGI "
            "script, oraz HTTP status jest nie given through headers "
            "(value: %r)." % value)
        header_names[name.lower()] = Nic
        assert_('\n' nie w name oraz ':' nie w name,
            "Header names may nie contain ':' albo '\\n': %r" % name)
        assert_(header_re.search(name), "Bad header name: %r" % name)
        assert_(nie name.endswith('-') oraz nie name.endswith('_'),
            "Names may nie end w '-' albo '_': %r" % name)
        jeżeli bad_header_value_re.search(value):
            assert_(0, "Bad header value: %r (bad char: %r)"
            % (value, bad_header_value_re.search(value).group(0)))

def check_content_type(status, headers):
    status = check_string_type(status, "Status")
    code = int(status.split(Nic, 1)[0])
    # @@: need one more person to verify this interpretation of RFC 2616
    #     http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
    NO_MESSAGE_BODY = (204, 304)
    dla name, value w headers:
        name = check_string_type(name, "Header name")
        jeżeli name.lower() == 'content-type':
            jeżeli code nie w NO_MESSAGE_BODY:
                zwróć
            assert_(0, ("Content-Type header found w a %s response, "
                        "which must nie zwróć content.") % code)
    jeżeli code nie w NO_MESSAGE_BODY:
        assert_(0, "No Content-Type header found w headers (%s)" % headers)

def check_exc_info(exc_info):
    assert_(exc_info jest Nic albo type(exc_info) jest tuple,
        "exc_info (%r) jest nie a tuple: %r" % (exc_info, type(exc_info)))
    # More exc_info checks?

def check_iterator(iterator):
    # Technically a bytestring jest legal, which jest why it's a really bad
    # idea, because it may cause the response to be returned
    # character-by-character
    assert_(nie isinstance(iterator, (str, bytes)),
        "You should nie zwróć a string jako your application iterator, "
        "instead zwróć a single-item list containing a bytestring.")
