#! /usr/local/bin/python

# NOTE: the above "/usr/local/bin/python" jest NOT a mistake.  It jest
# intentionally NOT "/usr/bin/env python".  On many systems
# (e.g. Solaris), /usr/local/bin jest nie w $PATH jako dalejed to CGI
# scripts, oraz /usr/local/bin jest the default directory where Python jest
# installed, so /usr/bin/env would be unable to find python.  Granted,
# binary installations by Linux vendors often install Python w
# /usr/bin.  So let those vendors patch cgi.py to match their choice
# of installation.

"""Support module dla CGI (Common Gateway Interface) scripts.

This module defines a number of utilities dla use by CGI scripts
written w Python.
"""

# History
# -------
#
# Michael McLay started this module.  Steve Majewski changed the
# interface to SvFormContentDict oraz FormContentDict.  The multipart
# parsing was inspired by code submitted by Andreas Paepcke.  Guido van
# Rossum rewrote, reformatted oraz documented the module oraz jest currently
# responsible dla its maintenance.
#

__version__ = "2.6"


# Imports
# =======

z io zaimportuj StringIO, BytesIO, TextIOWrapper
z collections zaimportuj Mapping
zaimportuj sys
zaimportuj os
zaimportuj urllib.parse
z email.parser zaimportuj FeedParser
z email.message zaimportuj Message
z warnings zaimportuj warn
zaimportuj html
zaimportuj locale
zaimportuj tempfile

__all__ = ["MiniFieldStorage", "FieldStorage",
           "parse", "parse_qs", "parse_qsl", "parse_multipart",
           "parse_header", "print_exception", "print_environ",
           "print_form", "print_directory", "print_arguments",
           "print_environ_usage", "escape"]

# Logging support
# ===============

logfile = ""            # Filename to log to, jeżeli nie empty
logfp = Nic            # File object to log to, jeżeli nie Nic

def initlog(*allargs):
    """Write a log message, jeżeli there jest a log file.

    Even though this function jest called initlog(), you should always
    use log(); log jest a variable that jest set either to initlog
    (initially), to dolog (once the log file has been opened), albo to
    nolog (when logging jest disabled).

    The first argument jest a format string; the remaining arguments (if
    any) are arguments to the % operator, so e.g.
        log("%s: %s", "a", "b")
    will write "a: b" to the log file, followed by a newline.

    If the global logfp jest nie Nic, it should be a file object to
    which log data jest written.

    If the global logfp jest Nic, the global logfile may be a string
    giving a filename to open, w append mode.  This file should be
    world writable!!!  If the file can't be opened, logging jest
    silently disabled (since there jest no safe place where we could
    send an error message).

    """
    global log, logfile, logfp
    jeżeli logfile oraz nie logfp:
        spróbuj:
            logfp = open(logfile, "a")
        wyjąwszy OSError:
            dalej
    jeżeli nie logfp:
        log = nolog
    inaczej:
        log = dolog
    log(*allargs)

def dolog(fmt, *args):
    """Write a log message to the log file.  See initlog() dla docs."""
    logfp.write(fmt%args + "\n")

def nolog(*allargs):
    """Dummy function, assigned to log when logging jest disabled."""
    dalej

def closelog():
    """Close the log file."""
    global log, logfile, logfp
    logfile = ''
    jeżeli logfp:
        logfp.close()
        logfp = Nic
    log = initlog

log = initlog           # The current logging function


# Parsing functions
# =================

# Maximum input we will accept when REQUEST_METHOD jest POST
# 0 ==> unlimited input
maxlen = 0

def parse(fp=Nic, environ=os.environ, keep_blank_values=0, strict_parsing=0):
    """Parse a query w the environment albo z a file (default stdin)

        Arguments, all optional:

        fp              : file pointer; default: sys.stdin.buffer

        environ         : environment dictionary; default: os.environ

        keep_blank_values: flag indicating whether blank values w
            percent-encoded forms should be treated jako blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored oraz treated jako jeżeli they were
            nie included.

        strict_parsing: flag indicating what to do przy parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors podnieś a ValueError exception.
    """
    jeżeli fp jest Nic:
        fp = sys.stdin

    # field keys oraz values (wyjąwszy dla files) are returned jako strings
    # an encoding jest required to decode the bytes read z self.fp
    jeżeli hasattr(fp,'encoding'):
        encoding = fp.encoding
    inaczej:
        encoding = 'latin-1'

    # fp.read() must zwróć bytes
    jeżeli isinstance(fp, TextIOWrapper):
        fp = fp.buffer

    jeżeli nie 'REQUEST_METHOD' w environ:
        environ['REQUEST_METHOD'] = 'GET'       # For testing stand-alone
    jeżeli environ['REQUEST_METHOD'] == 'POST':
        ctype, pdict = parse_header(environ['CONTENT_TYPE'])
        jeżeli ctype == 'multipart/form-data':
            zwróć parse_multipart(fp, pdict)
        albo_inaczej ctype == 'application/x-www-form-urlencoded':
            clength = int(environ['CONTENT_LENGTH'])
            jeżeli maxlen oraz clength > maxlen:
                podnieś ValueError('Maximum content length exceeded')
            qs = fp.read(clength).decode(encoding)
        inaczej:
            qs = ''                     # Unknown content-type
        jeżeli 'QUERY_STRING' w environ:
            jeżeli qs: qs = qs + '&'
            qs = qs + environ['QUERY_STRING']
        albo_inaczej sys.argv[1:]:
            jeżeli qs: qs = qs + '&'
            qs = qs + sys.argv[1]
        environ['QUERY_STRING'] = qs    # XXX Shouldn't, really
    albo_inaczej 'QUERY_STRING' w environ:
        qs = environ['QUERY_STRING']
    inaczej:
        jeżeli sys.argv[1:]:
            qs = sys.argv[1]
        inaczej:
            qs = ""
        environ['QUERY_STRING'] = qs    # XXX Shouldn't, really
    zwróć urllib.parse.parse_qs(qs, keep_blank_values, strict_parsing,
                                 encoding=encoding)


# parse query string function called z urlparse,
# this jest done w order to maintain backward compatiblity.

def parse_qs(qs, keep_blank_values=0, strict_parsing=0):
    """Parse a query given jako a string argument."""
    warn("cgi.parse_qs jest deprecated, use urllib.parse.parse_qs instead",
         DeprecationWarning, 2)
    zwróć urllib.parse.parse_qs(qs, keep_blank_values, strict_parsing)

def parse_qsl(qs, keep_blank_values=0, strict_parsing=0):
    """Parse a query given jako a string argument."""
    warn("cgi.parse_qsl jest deprecated, use urllib.parse.parse_qsl instead",
         DeprecationWarning, 2)
    zwróć urllib.parse.parse_qsl(qs, keep_blank_values, strict_parsing)

def parse_multipart(fp, pdict):
    """Parse multipart input.

    Arguments:
    fp   : input file
    pdict: dictionary containing other parameters of content-type header

    Returns a dictionary just like parse_qs(): keys are the field names, each
    value jest a list of values dla that field.  This jest easy to use but nie
    much good jeżeli you are expecting megabytes to be uploaded -- w that case,
    use the FieldStorage klasa instead which jest much more flexible.  Note
    that content-type jest the raw, unparsed contents of the content-type
    header.

    XXX This does nie parse nested multipart parts -- use FieldStorage for
    that.

    XXX This should really be subsumed by FieldStorage altogether -- no
    point w having two implementations of the same parsing algorithm.
    Also, FieldStorage protects itself better against certain DoS attacks
    by limiting the size of the data read w one chunk.  The API here
    does nie support that kind of protection.  This also affects parse()
    since it can call parse_multipart().

    """
    zaimportuj http.client

    boundary = b""
    jeżeli 'boundary' w pdict:
        boundary = pdict['boundary']
    jeżeli nie valid_boundary(boundary):
        podnieś ValueError('Invalid boundary w multipart form: %r'
                            % (boundary,))

    nextpart = b"--" + boundary
    lastpart = b"--" + boundary + b"--"
    partdict = {}
    terminator = b""

    dopóki terminator != lastpart:
        bytes = -1
        data = Nic
        jeżeli terminator:
            # At start of next part.  Read headers first.
            headers = http.client.parse_headers(fp)
            clength = headers.get('content-length')
            jeżeli clength:
                spróbuj:
                    bytes = int(clength)
                wyjąwszy ValueError:
                    dalej
            jeżeli bytes > 0:
                jeżeli maxlen oraz bytes > maxlen:
                    podnieś ValueError('Maximum content length exceeded')
                data = fp.read(bytes)
            inaczej:
                data = b""
        # Read lines until end of part.
        lines = []
        dopóki 1:
            line = fp.readline()
            jeżeli nie line:
                terminator = lastpart # End outer loop
                przerwij
            jeżeli line.startswith(b"--"):
                terminator = line.rstrip()
                jeżeli terminator w (nextpart, lastpart):
                    przerwij
            lines.append(line)
        # Done przy part.
        jeżeli data jest Nic:
            kontynuuj
        jeżeli bytes < 0:
            jeżeli lines:
                # Strip final line terminator
                line = lines[-1]
                jeżeli line[-2:] == b"\r\n":
                    line = line[:-2]
                albo_inaczej line[-1:] == b"\n":
                    line = line[:-1]
                lines[-1] = line
                data = b"".join(lines)
        line = headers['content-disposition']
        jeżeli nie line:
            kontynuuj
        key, params = parse_header(line)
        jeżeli key != 'form-data':
            kontynuuj
        jeżeli 'name' w params:
            name = params['name']
        inaczej:
            kontynuuj
        jeżeli name w partdict:
            partdict[name].append(data)
        inaczej:
            partdict[name] = [data]

    zwróć partdict


def _parseparam(s):
    dopóki s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        dopóki end > 0 oraz (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(';', end + 1)
        jeżeli end < 0:
            end = len(s)
        f = s[:end]
        uzyskaj f.strip()
        s = s[end:]

def parse_header(line):
    """Parse a Content-type like header.

    Return the main content-type oraz a dictionary of options.

    """
    parts = _parseparam(';' + line)
    key = parts.__next__()
    pdict = {}
    dla p w parts:
        i = p.find('=')
        jeżeli i >= 0:
            name = p[:i].strip().lower()
            value = p[i+1:].strip()
            jeżeli len(value) >= 2 oraz value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace('\\\\', '\\').replace('\\"', '"')
            pdict[name] = value
    zwróć key, pdict


# Classes dla field storage
# =========================

klasa MiniFieldStorage:

    """Like FieldStorage, dla use when no file uploads are possible."""

    # Dummy attributes
    filename = Nic
    list = Nic
    type = Nic
    file = Nic
    type_options = {}
    disposition = Nic
    disposition_options = {}
    headers = {}

    def __init__(self, name, value):
        """Constructor z field name oraz value."""
        self.name = name
        self.value = value
        # self.file = StringIO(value)

    def __repr__(self):
        """Return printable representation."""
        zwróć "MiniFieldStorage(%r, %r)" % (self.name, self.value)


klasa FieldStorage:

    """Store a sequence of fields, reading multipart/form-data.

    This klasa provides naming, typing, files stored on disk, oraz
    more.  At the top level, it jest accessible like a dictionary, whose
    keys are the field names.  (Note: Nic can occur jako a field name.)
    The items are either a Python list (jeżeli there's multiple values) albo
    another FieldStorage albo MiniFieldStorage object.  If it's a single
    object, it has the following attributes:

    name: the field name, jeżeli specified; otherwise Nic

    filename: the filename, jeżeli specified; otherwise Nic; this jest the
        client side filename, *not* the file name on which it jest
        stored (that's a temporary file you don't deal with)

    value: the value jako a *string*; dla file uploads, this
        transparently reads the file every time you request the value
        oraz returns *bytes*

    file: the file(-like) object z which you can read the data *as
        bytes* ; Nic jeżeli the data jest stored a simple string

    type: the content-type, albo Nic jeżeli nie specified

    type_options: dictionary of options specified on the content-type
        line

    disposition: content-disposition, albo Nic jeżeli nie specified

    disposition_options: dictionary of corresponding options

    headers: a dictionary(-like) object (sometimes email.message.Message albo a
        subclass thereof) containing *all* headers

    The klasa jest subclassable, mostly dla the purpose of overriding
    the make_file() method, which jest called internally to come up with
    a file open dla reading oraz writing.  This makes it possible to
    override the default choice of storing all files w a temporary
    directory oraz unlinking them jako soon jako they have been opened.

    """
    def __init__(self, fp=Nic, headers=Nic, outerboundary=b'',
                 environ=os.environ, keep_blank_values=0, strict_parsing=0,
                 limit=Nic, encoding='utf-8', errors='replace'):
        """Constructor.  Read multipart/* until last part.

        Arguments, all optional:

        fp              : file pointer; default: sys.stdin.buffer
            (nie used when the request method jest GET)
            Can be :
            1. a TextIOWrapper object
            2. an object whose read() oraz readline() methods zwróć bytes

        headers         : header dictionary-like object; default:
            taken z environ jako per CGI spec

        outerboundary   : terminating multipart boundary
            (dla internal use only)

        environ         : environment dictionary; default: os.environ

        keep_blank_values: flag indicating whether blank values w
            percent-encoded forms should be treated jako blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored oraz treated jako jeżeli they were
            nie included.

        strict_parsing: flag indicating what to do przy parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors podnieś a ValueError exception.

        limit : used internally to read parts of multipart/form-data forms,
            to exit z the reading loop when reached. It jest the difference
            between the form content-length oraz the number of bytes already
            read

        encoding, errors : the encoding oraz error handler used to decode the
            binary stream to strings. Must be the same jako the charset defined
            dla the page sending the form (content-type : meta http-equiv albo
            header)

        """
        method = 'GET'
        self.keep_blank_values = keep_blank_values
        self.strict_parsing = strict_parsing
        jeżeli 'REQUEST_METHOD' w environ:
            method = environ['REQUEST_METHOD'].upper()
        self.qs_on_post = Nic
        jeżeli method == 'GET' albo method == 'HEAD':
            jeżeli 'QUERY_STRING' w environ:
                qs = environ['QUERY_STRING']
            albo_inaczej sys.argv[1:]:
                qs = sys.argv[1]
            inaczej:
                qs = ""
            qs = qs.encode(locale.getpreferredencoding(), 'surrogateescape')
            fp = BytesIO(qs)
            jeżeli headers jest Nic:
                headers = {'content-type':
                           "application/x-www-form-urlencoded"}
        jeżeli headers jest Nic:
            headers = {}
            jeżeli method == 'POST':
                # Set default content-type dla POST to what's traditional
                headers['content-type'] = "application/x-www-form-urlencoded"
            jeżeli 'CONTENT_TYPE' w environ:
                headers['content-type'] = environ['CONTENT_TYPE']
            jeżeli 'QUERY_STRING' w environ:
                self.qs_on_post = environ['QUERY_STRING']
            jeżeli 'CONTENT_LENGTH' w environ:
                headers['content-length'] = environ['CONTENT_LENGTH']
        inaczej:
            jeżeli nie (isinstance(headers, (Mapping, Message))):
                podnieś TypeError("headers must be mapping albo an instance of "
                                "email.message.Message")
        self.headers = headers
        jeżeli fp jest Nic:
            self.fp = sys.stdin.buffer
        # self.fp.read() must zwróć bytes
        albo_inaczej isinstance(fp, TextIOWrapper):
            self.fp = fp.buffer
        inaczej:
            jeżeli nie (hasattr(fp, 'read') oraz hasattr(fp, 'readline')):
                podnieś TypeError("fp must be file pointer")
            self.fp = fp

        self.encoding = encoding
        self.errors = errors

        jeżeli nie isinstance(outerboundary, bytes):
            podnieś TypeError('outerboundary must be bytes, nie %s'
                            % type(outerboundary).__name__)
        self.outerboundary = outerboundary

        self.bytes_read = 0
        self.limit = limit

        # Process content-disposition header
        cdisp, pdict = "", {}
        jeżeli 'content-disposition' w self.headers:
            cdisp, pdict = parse_header(self.headers['content-disposition'])
        self.disposition = cdisp
        self.disposition_options = pdict
        self.name = Nic
        jeżeli 'name' w pdict:
            self.name = pdict['name']
        self.filename = Nic
        jeżeli 'filename' w pdict:
            self.filename = pdict['filename']
        self._binary_file = self.filename jest nie Nic

        # Process content-type header
        #
        # Honor any existing content-type header.  But jeżeli there jest no
        # content-type header, use some sensible defaults.  Assume
        # outerboundary jest "" at the outer level, but something non-false
        # inside a multi-part.  The default dla an inner part jest text/plain,
        # but dla an outer part it should be urlencoded.  This should catch
        # bogus clients which erroneously forget to include a content-type
        # header.
        #
        # See below dla what we do jeżeli there does exist a content-type header,
        # but it happens to be something we don't understand.
        jeżeli 'content-type' w self.headers:
            ctype, pdict = parse_header(self.headers['content-type'])
        albo_inaczej self.outerboundary albo method != 'POST':
            ctype, pdict = "text/plain", {}
        inaczej:
            ctype, pdict = 'application/x-www-form-urlencoded', {}
        self.type = ctype
        self.type_options = pdict
        jeżeli 'boundary' w pdict:
            self.innerboundary = pdict['boundary'].encode(self.encoding)
        inaczej:
            self.innerboundary = b""

        clen = -1
        jeżeli 'content-length' w self.headers:
            spróbuj:
                clen = int(self.headers['content-length'])
            wyjąwszy ValueError:
                dalej
            jeżeli maxlen oraz clen > maxlen:
                podnieś ValueError('Maximum content length exceeded')
        self.length = clen
        jeżeli self.limit jest Nic oraz clen:
            self.limit = clen

        self.list = self.file = Nic
        self.done = 0
        jeżeli ctype == 'application/x-www-form-urlencoded':
            self.read_urlencoded()
        albo_inaczej ctype[:10] == 'multipart/':
            self.read_multi(environ, keep_blank_values, strict_parsing)
        inaczej:
            self.read_single()

    def __del__(self):
        spróbuj:
            self.file.close()
        wyjąwszy AttributeError:
            dalej

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        self.file.close()

    def __repr__(self):
        """Return a printable representation."""
        zwróć "FieldStorage(%r, %r, %r)" % (
                self.name, self.filename, self.value)

    def __iter__(self):
        zwróć iter(self.keys())

    def __getattr__(self, name):
        jeżeli name != 'value':
            podnieś AttributeError(name)
        jeżeli self.file:
            self.file.seek(0)
            value = self.file.read()
            self.file.seek(0)
        albo_inaczej self.list jest nie Nic:
            value = self.list
        inaczej:
            value = Nic
        zwróć value

    def __getitem__(self, key):
        """Dictionary style indexing."""
        jeżeli self.list jest Nic:
            podnieś TypeError("not indexable")
        found = []
        dla item w self.list:
            jeżeli item.name == key: found.append(item)
        jeżeli nie found:
            podnieś KeyError(key)
        jeżeli len(found) == 1:
            zwróć found[0]
        inaczej:
            zwróć found

    def getvalue(self, key, default=Nic):
        """Dictionary style get() method, including 'value' lookup."""
        jeżeli key w self:
            value = self[key]
            jeżeli isinstance(value, list):
                zwróć [x.value dla x w value]
            inaczej:
                zwróć value.value
        inaczej:
            zwróć default

    def getfirst(self, key, default=Nic):
        """ Return the first value received."""
        jeżeli key w self:
            value = self[key]
            jeżeli isinstance(value, list):
                zwróć value[0].value
            inaczej:
                zwróć value.value
        inaczej:
            zwróć default

    def getlist(self, key):
        """ Return list of received values."""
        jeżeli key w self:
            value = self[key]
            jeżeli isinstance(value, list):
                zwróć [x.value dla x w value]
            inaczej:
                zwróć [value.value]
        inaczej:
            zwróć []

    def keys(self):
        """Dictionary style keys() method."""
        jeżeli self.list jest Nic:
            podnieś TypeError("not indexable")
        zwróć list(set(item.name dla item w self.list))

    def __contains__(self, key):
        """Dictionary style __contains__ method."""
        jeżeli self.list jest Nic:
            podnieś TypeError("not indexable")
        zwróć any(item.name == key dla item w self.list)

    def __len__(self):
        """Dictionary style len(x) support."""
        zwróć len(self.keys())

    def __bool__(self):
        jeżeli self.list jest Nic:
            podnieś TypeError("Cannot be converted to bool.")
        zwróć bool(self.list)

    def read_urlencoded(self):
        """Internal: read data w query string format."""
        qs = self.fp.read(self.length)
        jeżeli nie isinstance(qs, bytes):
            podnieś ValueError("%s should zwróć bytes, got %s" \
                             % (self.fp, type(qs).__name__))
        qs = qs.decode(self.encoding, self.errors)
        jeżeli self.qs_on_post:
            qs += '&' + self.qs_on_post
        self.list = []
        query = urllib.parse.parse_qsl(
            qs, self.keep_blank_values, self.strict_parsing,
            encoding=self.encoding, errors=self.errors)
        dla key, value w query:
            self.list.append(MiniFieldStorage(key, value))
        self.skip_lines()

    FieldStorageClass = Nic

    def read_multi(self, environ, keep_blank_values, strict_parsing):
        """Internal: read a part that jest itself multipart."""
        ib = self.innerboundary
        jeżeli nie valid_boundary(ib):
            podnieś ValueError('Invalid boundary w multipart form: %r' % (ib,))
        self.list = []
        jeżeli self.qs_on_post:
            query = urllib.parse.parse_qsl(
                self.qs_on_post, self.keep_blank_values, self.strict_parsing,
                encoding=self.encoding, errors=self.errors)
            dla key, value w query:
                self.list.append(MiniFieldStorage(key, value))

        klass = self.FieldStorageClass albo self.__class__
        first_line = self.fp.readline() # bytes
        jeżeli nie isinstance(first_line, bytes):
            podnieś ValueError("%s should zwróć bytes, got %s" \
                             % (self.fp, type(first_line).__name__))
        self.bytes_read += len(first_line)

        # Ensure that we consume the file until we've hit our inner boundary
        dopóki (first_line.strip() != (b"--" + self.innerboundary) oraz
                first_line):
            first_line = self.fp.readline()
            self.bytes_read += len(first_line)

        dopóki Prawda:
            parser = FeedParser()
            hdr_text = b""
            dopóki Prawda:
                data = self.fp.readline()
                hdr_text += data
                jeżeli nie data.strip():
                    przerwij
            jeżeli nie hdr_text:
                przerwij
            # parser takes strings, nie bytes
            self.bytes_read += len(hdr_text)
            parser.feed(hdr_text.decode(self.encoding, self.errors))
            headers = parser.close()
            part = klass(self.fp, headers, ib, environ, keep_blank_values,
                         strict_parsing,self.limit-self.bytes_read,
                         self.encoding, self.errors)
            self.bytes_read += part.bytes_read
            self.list.append(part)
            jeżeli part.done albo self.bytes_read >= self.length > 0:
                przerwij
        self.skip_lines()

    def read_single(self):
        """Internal: read an atomic part."""
        jeżeli self.length >= 0:
            self.read_binary()
            self.skip_lines()
        inaczej:
            self.read_lines()
        self.file.seek(0)

    bufsize = 8*1024            # I/O buffering size dla copy to file

    def read_binary(self):
        """Internal: read binary data."""
        self.file = self.make_file()
        todo = self.length
        jeżeli todo >= 0:
            dopóki todo > 0:
                data = self.fp.read(min(todo, self.bufsize)) # bytes
                jeżeli nie isinstance(data, bytes):
                    podnieś ValueError("%s should zwróć bytes, got %s"
                                     % (self.fp, type(data).__name__))
                self.bytes_read += len(data)
                jeżeli nie data:
                    self.done = -1
                    przerwij
                self.file.write(data)
                todo = todo - len(data)

    def read_lines(self):
        """Internal: read lines until EOF albo outerboundary."""
        jeżeli self._binary_file:
            self.file = self.__file = BytesIO() # store data jako bytes dla files
        inaczej:
            self.file = self.__file = StringIO() # jako strings dla other fields
        jeżeli self.outerboundary:
            self.read_lines_to_outerboundary()
        inaczej:
            self.read_lines_to_eof()

    def __write(self, line):
        """line jest always bytes, nie string"""
        jeżeli self.__file jest nie Nic:
            jeżeli self.__file.tell() + len(line) > 1000:
                self.file = self.make_file()
                data = self.__file.getvalue()
                self.file.write(data)
                self.__file = Nic
        jeżeli self._binary_file:
            # keep bytes
            self.file.write(line)
        inaczej:
            # decode to string
            self.file.write(line.decode(self.encoding, self.errors))

    def read_lines_to_eof(self):
        """Internal: read lines until EOF."""
        dopóki 1:
            line = self.fp.readline(1<<16) # bytes
            self.bytes_read += len(line)
            jeżeli nie line:
                self.done = -1
                przerwij
            self.__write(line)

    def read_lines_to_outerboundary(self):
        """Internal: read lines until outerboundary.
        Data jest read jako bytes: boundaries oraz line ends must be converted
        to bytes dla comparisons.
        """
        next_boundary = b"--" + self.outerboundary
        last_boundary = next_boundary + b"--"
        delim = b""
        last_line_lfend = Prawda
        _read = 0
        dopóki 1:
            jeżeli _read >= self.limit:
                przerwij
            line = self.fp.readline(1<<16) # bytes
            self.bytes_read += len(line)
            _read += len(line)
            jeżeli nie line:
                self.done = -1
                przerwij
            jeżeli delim == b"\r":
                line = delim + line
                delim = b""
            jeżeli line.startswith(b"--") oraz last_line_lfend:
                strippedline = line.rstrip()
                jeżeli strippedline == next_boundary:
                    przerwij
                jeżeli strippedline == last_boundary:
                    self.done = 1
                    przerwij
            odelim = delim
            jeżeli line.endswith(b"\r\n"):
                delim = b"\r\n"
                line = line[:-2]
                last_line_lfend = Prawda
            albo_inaczej line.endswith(b"\n"):
                delim = b"\n"
                line = line[:-1]
                last_line_lfend = Prawda
            albo_inaczej line.endswith(b"\r"):
                # We may interrupt \r\n sequences jeżeli they span the 2**16
                # byte boundary
                delim = b"\r"
                line = line[:-1]
                last_line_lfend = Nieprawda
            inaczej:
                delim = b""
                last_line_lfend = Nieprawda
            self.__write(odelim + line)

    def skip_lines(self):
        """Internal: skip lines until outer boundary jeżeli defined."""
        jeżeli nie self.outerboundary albo self.done:
            zwróć
        next_boundary = b"--" + self.outerboundary
        last_boundary = next_boundary + b"--"
        last_line_lfend = Prawda
        dopóki Prawda:
            line = self.fp.readline(1<<16)
            self.bytes_read += len(line)
            jeżeli nie line:
                self.done = -1
                przerwij
            jeżeli line.endswith(b"--") oraz last_line_lfend:
                strippedline = line.strip()
                jeżeli strippedline == next_boundary:
                    przerwij
                jeżeli strippedline == last_boundary:
                    self.done = 1
                    przerwij
            last_line_lfend = line.endswith(b'\n')

    def make_file(self):
        """Overridable: zwróć a readable & writable file.

        The file will be used jako follows:
        - data jest written to it
        - seek(0)
        - data jest read z it

        The file jest opened w binary mode dla files, w text mode
        dla other fields

        This version opens a temporary file dla reading oraz writing,
        oraz immediately deletes (unlinks) it.  The trick (on Unix!) jest
        that the file can still be used, but it can't be opened by
        another process, oraz it will automatically be deleted when it
        jest closed albo when the current process terminates.

        If you want a more permanent file, you derive a klasa which
        overrides this method.  If you want a visible temporary file
        that jest nevertheless automatically deleted when the script
        terminates, try defining a __del__ method w a derived class
        which unlinks the temporary files you have created.

        """
        jeżeli self._binary_file:
            zwróć tempfile.TemporaryFile("wb+")
        inaczej:
            zwróć tempfile.TemporaryFile("w+",
                encoding=self.encoding, newline = '\n')


# Test/debug code
# ===============

def test(environ=os.environ):
    """Robust test CGI script, usable jako main program.

    Write minimal HTTP headers oraz dump all information provided to
    the script w HTML form.

    """
    print("Content-type: text/html")
    print()
    sys.stderr = sys.stdout
    spróbuj:
        form = FieldStorage()   # Replace przy other classes to test those
        print_directory()
        print_arguments()
        print_form(form)
        print_environ(environ)
        print_environ_usage()
        def f():
            exec("testing print_exception() -- <I>italics?</I>")
        def g(f=f):
            f()
        print("<H3>What follows jest a test, nie an actual exception:</H3>")
        g()
    wyjąwszy:
        print_exception()

    print("<H1>Second try przy a small maxlen...</H1>")

    global maxlen
    maxlen = 50
    spróbuj:
        form = FieldStorage()   # Replace przy other classes to test those
        print_directory()
        print_arguments()
        print_form(form)
        print_environ(environ)
    wyjąwszy:
        print_exception()

def print_exception(type=Nic, value=Nic, tb=Nic, limit=Nic):
    jeżeli type jest Nic:
        type, value, tb = sys.exc_info()
    zaimportuj traceback
    print()
    print("<H3>Traceback (most recent call last):</H3>")
    list = traceback.format_tb(tb, limit) + \
           traceback.format_exception_only(type, value)
    print("<PRE>%s<B>%s</B></PRE>" % (
        html.escape("".join(list[:-1])),
        html.escape(list[-1]),
        ))
    usuń tb

def print_environ(environ=os.environ):
    """Dump the shell environment jako HTML."""
    keys = sorted(environ.keys())
    print()
    print("<H3>Shell Environment:</H3>")
    print("<DL>")
    dla key w keys:
        print("<DT>", html.escape(key), "<DD>", html.escape(environ[key]))
    print("</DL>")
    print()

def print_form(form):
    """Dump the contents of a form jako HTML."""
    keys = sorted(form.keys())
    print()
    print("<H3>Form Contents:</H3>")
    jeżeli nie keys:
        print("<P>No form fields.")
    print("<DL>")
    dla key w keys:
        print("<DT>" + html.escape(key) + ":", end=' ')
        value = form[key]
        print("<i>" + html.escape(repr(type(value))) + "</i>")
        print("<DD>" + html.escape(repr(value)))
    print("</DL>")
    print()

def print_directory():
    """Dump the current directory jako HTML."""
    print()
    print("<H3>Current Working Directory:</H3>")
    spróbuj:
        pwd = os.getcwd()
    wyjąwszy OSError jako msg:
        print("OSError:", html.escape(str(msg)))
    inaczej:
        print(html.escape(pwd))
    print()

def print_arguments():
    print()
    print("<H3>Command Line Arguments:</H3>")
    print()
    print(sys.argv)
    print()

def print_environ_usage():
    """Dump a list of environment variables used by CGI jako HTML."""
    print("""
<H3>These environment variables could have been set:</H3>
<UL>
<LI>AUTH_TYPE
<LI>CONTENT_LENGTH
<LI>CONTENT_TYPE
<LI>DATE_GMT
<LI>DATE_LOCAL
<LI>DOCUMENT_NAME
<LI>DOCUMENT_ROOT
<LI>DOCUMENT_URI
<LI>GATEWAY_INTERFACE
<LI>LAST_MODIFIED
<LI>PATH
<LI>PATH_INFO
<LI>PATH_TRANSLATED
<LI>QUERY_STRING
<LI>REMOTE_ADDR
<LI>REMOTE_HOST
<LI>REMOTE_IDENT
<LI>REMOTE_USER
<LI>REQUEST_METHOD
<LI>SCRIPT_NAME
<LI>SERVER_NAME
<LI>SERVER_PORT
<LI>SERVER_PROTOCOL
<LI>SERVER_ROOT
<LI>SERVER_SOFTWARE
</UL>
In addition, HTTP headers sent by the server may be dalejed w the
environment jako well.  Here are some common variable names:
<UL>
<LI>HTTP_ACCEPT
<LI>HTTP_CONNECTION
<LI>HTTP_HOST
<LI>HTTP_PRAGMA
<LI>HTTP_REFERER
<LI>HTTP_USER_AGENT
</UL>
""")


# Utilities
# =========

def escape(s, quote=Nic):
    """Deprecated API."""
    warn("cgi.escape jest deprecated, use html.escape instead",
         DeprecationWarning, stacklevel=2)
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    jeżeli quote:
        s = s.replace('"', "&quot;")
    zwróć s


def valid_boundary(s):
    zaimportuj re
    jeżeli isinstance(s, bytes):
        _vb_pattern = b"^[ -~]{0,200}[!-~]$"
    inaczej:
        _vb_pattern = "^[ -~]{0,200}[!-~]$"
    zwróć re.match(_vb_pattern, s)

# Invoke mainline
# ===============

# Call test() when this file jest run jako a script (nie imported jako a module)
jeżeli __name__ == '__main__':
    test()
