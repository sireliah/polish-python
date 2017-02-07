#
# XML-RPC CLIENT LIBRARY
# $Id$
#
# an XML-RPC client interface dla Python.
#
# the marshalling oraz response parser code can also be used to
# implement XML-RPC servers.
#
# Notes:
# this version jest designed to work przy Python 2.1 albo newer.
#
# History:
# 1999-01-14 fl  Created
# 1999-01-15 fl  Changed dateTime to use localtime
# 1999-01-16 fl  Added Binary/base64 element, default to RPC2 service
# 1999-01-19 fl  Fixed array data element (z Skip Montanaro)
# 1999-01-21 fl  Fixed dateTime constructor, etc.
# 1999-02-02 fl  Added fault handling, handle empty sequences, etc.
# 1999-02-10 fl  Fixed problem przy empty responses (z Skip Montanaro)
# 1999-06-20 fl  Speed improvements, pluggable parsers/transports (0.9.8)
# 2000-11-28 fl  Changed boolean to check the truth value of its argument
# 2001-02-24 fl  Added encoding/Unicode/SafeTransport patches
# 2001-02-26 fl  Added compare support to wrappers (0.9.9/1.0b1)
# 2001-03-28 fl  Make sure response tuple jest a singleton
# 2001-03-29 fl  Don't require empty params element (z Nicholas Riley)
# 2001-06-10 fl  Folded w _xmlrpclib accelerator support (1.0b2)
# 2001-08-20 fl  Base xmlrpclib.Error on built-in Exception (z Paul Prescod)
# 2001-09-03 fl  Allow Transport subclass to override getparser
# 2001-09-10 fl  Lazy zaimportuj of urllib, cgi, xmllib (20x zaimportuj speedup)
# 2001-10-01 fl  Remove containers z memo cache when done przy them
# 2001-10-01 fl  Use faster escape method (80% dumps speedup)
# 2001-10-02 fl  More dumps microtuning
# 2001-10-04 fl  Make sure zaimportuj expat gets a parser (z Guido van Rossum)
# 2001-10-10 sm  Allow long ints to be dalejed jako ints jeżeli they don't overflow
# 2001-10-17 sm  Test dla int oraz long overflow (allows use on 64-bit systems)
# 2001-11-12 fl  Use repr() to marshal doubles (z Paul Felix)
# 2002-03-17 fl  Avoid buffered read when possible (z James Rucker)
# 2002-04-07 fl  Added pythondoc comments
# 2002-04-16 fl  Added __str__ methods to datetime/binary wrappers
# 2002-05-15 fl  Added error constants (z Andrew Kuchling)
# 2002-06-27 fl  Merged przy Python CVS version
# 2002-10-22 fl  Added basic authentication (based on code z Phillip Eby)
# 2003-01-22 sm  Add support dla the bool type
# 2003-02-27 gvr Remove apply calls
# 2003-04-24 sm  Use cStringIO jeżeli available
# 2003-04-25 ak  Add support dla nil
# 2003-06-15 gn  Add support dla time.struct_time
# 2003-07-12 gp  Correct marshalling of Faults
# 2003-10-31 mvl Add multicall support
# 2004-08-20 mvl Bump minimum supported Python version to 2.1
# 2014-12-02 ch/doko  Add workaround dla gzip bomb vulnerability
#
# Copyright (c) 1999-2002 by Secret Labs AB.
# Copyright (c) 1999-2002 by Fredrik Lundh.
#
# info@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The XML-RPC client interface jest
#
# Copyright (c) 1999-2002 by Secret Labs AB
# Copyright (c) 1999-2002 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# oraz will comply przy the following terms oraz conditions:
#
# Permission to use, copy, modify, oraz distribute this software oraz
# its associated documentation dla any purpose oraz without fee jest
# hereby granted, provided that the above copyright notice appears w
# all copies, oraz that both that copyright notice oraz this permission
# notice appear w supporting documentation, oraz that the name of
# Secret Labs AB albo the author nie be used w advertising albo publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

"""
An XML-RPC client interface dla Python.

The marshalling oraz response parser code can also be used to
implement XML-RPC servers.

Exported exceptions:

  Error          Base klasa dla client errors
  ProtocolError  Indicates an HTTP protocol error
  ResponseError  Indicates a broken response package
  Fault          Indicates an XML-RPC fault package

Exported classes:

  ServerProxy    Represents a logical connection to an XML-RPC server

  MultiCall      Executor of boxcared xmlrpc requests
  DateTime       dateTime wrapper dla an ISO 8601 string albo time tuple albo
                 localtime integer value to generate a "dateTime.iso8601"
                 XML-RPC value
  Binary         binary data wrapper

  Marshaller     Generate an XML-RPC params chunk z a Python data structure
  Unmarshaller   Unmarshal an XML-RPC response z incoming XML event message
  Transport      Handles an HTTP transaction to an XML-RPC server
  SafeTransport  Handles an HTTPS transaction to an XML-RPC server

Exported constants:

  (none)

Exported functions:

  getparser      Create instance of the fastest available parser & attach
                 to an unmarshalling object
  dumps          Convert an argument tuple albo a Fault instance to an XML-RPC
                 request (or response, jeżeli the methodresponse option jest used).
  loads          Convert an XML-RPC packet to unmarshalled data plus a method
                 name (Nic jeżeli nie present).
"""

zaimportuj base64
zaimportuj sys
zaimportuj time
z datetime zaimportuj datetime
zaimportuj http.client
zaimportuj urllib.parse
z xml.parsers zaimportuj expat
zaimportuj errno
z io zaimportuj BytesIO
spróbuj:
    zaimportuj gzip
wyjąwszy ImportError:
    gzip = Nic #python can be built without zlib/gzip support

# --------------------------------------------------------------------
# Internal stuff

def escape(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    zwróć s.replace(">", "&gt;",)

# used w User-Agent header sent
__version__ = sys.version[:3]

# xmlrpc integer limits
MAXINT =  2**31-1
MININT = -2**31

# --------------------------------------------------------------------
# Error constants (z Dan Libby's specification at
# http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php)

# Ranges of errors
PARSE_ERROR       = -32700
SERVER_ERROR      = -32600
APPLICATION_ERROR = -32500
SYSTEM_ERROR      = -32400
TRANSPORT_ERROR   = -32300

# Specific errors
NOT_WELLFORMED_ERROR  = -32700
UNSUPPORTED_ENCODING  = -32701
INVALID_ENCODING_CHAR = -32702
INVALID_XMLRPC        = -32600
METHOD_NOT_FOUND      = -32601
INVALID_METHOD_PARAMS = -32602
INTERNAL_ERROR        = -32603

# --------------------------------------------------------------------
# Exceptions

##
# Base klasa dla all kinds of client-side errors.

klasa Error(Exception):
    """Base klasa dla client errors."""
    def __str__(self):
        zwróć repr(self)

##
# Indicates an HTTP-level protocol error.  This jest podnieśd by the HTTP
# transport layer, jeżeli the server returns an error code other than 200
# (OK).
#
# @param url The target URL.
# @param errcode The HTTP error code.
# @param errmsg The HTTP error message.
# @param headers The HTTP header dictionary.

klasa ProtocolError(Error):
    """Indicates an HTTP protocol error."""
    def __init__(self, url, errcode, errmsg, headers):
        Error.__init__(self)
        self.url = url
        self.errcode = errcode
        self.errmsg = errmsg
        self.headers = headers
    def __repr__(self):
        zwróć (
            "<%s dla %s: %s %s>" %
            (self.__class__.__name__, self.url, self.errcode, self.errmsg)
            )

##
# Indicates a broken XML-RPC response package.  This exception jest
# podnieśd by the unmarshalling layer, jeżeli the XML-RPC response jest
# malformed.

klasa ResponseError(Error):
    """Indicates a broken response package."""
    dalej

##
# Indicates an XML-RPC fault response package.  This exception jest
# podnieśd by the unmarshalling layer, jeżeli the XML-RPC response contains
# a fault string.  This exception can also be used jako a class, to
# generate a fault XML-RPC message.
#
# @param faultCode The XML-RPC fault code.
# @param faultString The XML-RPC fault string.

klasa Fault(Error):
    """Indicates an XML-RPC fault package."""
    def __init__(self, faultCode, faultString, **extra):
        Error.__init__(self)
        self.faultCode = faultCode
        self.faultString = faultString
    def __repr__(self):
        zwróć "<%s %s: %r>" % (self.__class__.__name__,
                                self.faultCode, self.faultString)

# --------------------------------------------------------------------
# Special values

##
# Backwards compatibility

boolean = Boolean = bool

##
# Wrapper dla XML-RPC DateTime values.  This converts a time value to
# the format used by XML-RPC.
# <p>
# The value can be given jako a datetime object, jako a string w the
# format "yyyymmddThh:mm:ss", jako a 9-item time tuple (as returned by
# time.localtime()), albo an integer value (as returned by time.time()).
# The wrapper uses time.localtime() to convert an integer to a time
# tuple.
#
# @param value The time, given jako a datetime object, an ISO 8601 string,
#              a time tuple, albo an integer time value.


# Issue #13305: different format codes across platforms
_day0 = datetime(1, 1, 1)
jeżeli _day0.strftime('%Y') == '0001':      # Mac OS X
    def _iso8601_format(value):
        zwróć value.strftime("%Y%m%dT%H:%M:%S")
albo_inaczej _day0.strftime('%4Y') == '0001':   # Linux
    def _iso8601_format(value):
        zwróć value.strftime("%4Y%m%dT%H:%M:%S")
inaczej:
    def _iso8601_format(value):
        zwróć value.strftime("%Y%m%dT%H:%M:%S").zfill(17)
usuń _day0


def _strftime(value):
    jeżeli isinstance(value, datetime):
        zwróć _iso8601_format(value)

    jeżeli nie isinstance(value, (tuple, time.struct_time)):
        jeżeli value == 0:
            value = time.time()
        value = time.localtime(value)

    zwróć "%04d%02d%02dT%02d:%02d:%02d" % value[:6]

klasa DateTime:
    """DateTime wrapper dla an ISO 8601 string albo time tuple albo
    localtime integer value to generate 'dateTime.iso8601' XML-RPC
    value.
    """

    def __init__(self, value=0):
        jeżeli isinstance(value, str):
            self.value = value
        inaczej:
            self.value = _strftime(value)

    def make_comparable(self, other):
        jeżeli isinstance(other, DateTime):
            s = self.value
            o = other.value
        albo_inaczej isinstance(other, datetime):
            s = self.value
            o = _iso8601_format(other)
        albo_inaczej isinstance(other, str):
            s = self.value
            o = other
        albo_inaczej hasattr(other, "timetuple"):
            s = self.timetuple()
            o = other.timetuple()
        inaczej:
            otype = (hasattr(other, "__class__")
                     oraz other.__class__.__name__
                     albo type(other))
            podnieś TypeError("Can't compare %s oraz %s" %
                            (self.__class__.__name__, otype))
        zwróć s, o

    def __lt__(self, other):
        s, o = self.make_comparable(other)
        zwróć s < o

    def __le__(self, other):
        s, o = self.make_comparable(other)
        zwróć s <= o

    def __gt__(self, other):
        s, o = self.make_comparable(other)
        zwróć s > o

    def __ge__(self, other):
        s, o = self.make_comparable(other)
        zwróć s >= o

    def __eq__(self, other):
        s, o = self.make_comparable(other)
        zwróć s == o

    def timetuple(self):
        zwróć time.strptime(self.value, "%Y%m%dT%H:%M:%S")

    ##
    # Get date/time value.
    #
    # @return Date/time value, jako an ISO 8601 string.

    def __str__(self):
        zwróć self.value

    def __repr__(self):
        zwróć "<%s %r at %#x>" % (self.__class__.__name__, self.value, id(self))

    def decode(self, data):
        self.value = str(data).strip()

    def encode(self, out):
        out.write("<value><dateTime.iso8601>")
        out.write(self.value)
        out.write("</dateTime.iso8601></value>\n")

def _datetime(data):
    # decode xml element contents into a DateTime structure.
    value = DateTime()
    value.decode(data)
    zwróć value

def _datetime_type(data):
    zwróć datetime.strptime(data, "%Y%m%dT%H:%M:%S")

##
# Wrapper dla binary data.  This can be used to transport any kind
# of binary data over XML-RPC, using BASE64 encoding.
#
# @param data An 8-bit string containing arbitrary data.

klasa Binary:
    """Wrapper dla binary data."""

    def __init__(self, data=Nic):
        jeżeli data jest Nic:
            data = b""
        inaczej:
            jeżeli nie isinstance(data, (bytes, bytearray)):
                podnieś TypeError("expected bytes albo bytearray, nie %s" %
                                data.__class__.__name__)
            data = bytes(data)  # Make a copy of the bytes!
        self.data = data

    ##
    # Get buffer contents.
    #
    # @return Buffer contents, jako an 8-bit string.

    def __str__(self):
        zwróć str(self.data, "latin-1")  # XXX encoding?!

    def __eq__(self, other):
        jeżeli isinstance(other, Binary):
            other = other.data
        zwróć self.data == other

    def decode(self, data):
        self.data = base64.decodebytes(data)

    def encode(self, out):
        out.write("<value><base64>\n")
        encoded = base64.encodebytes(self.data)
        out.write(encoded.decode('ascii'))
        out.write("</base64></value>\n")

def _binary(data):
    # decode xml element contents into a Binary structure
    value = Binary()
    value.decode(data)
    zwróć value

WRAPPERS = (DateTime, Binary)

# --------------------------------------------------------------------
# XML parsers

klasa ExpatParser:
    # fast expat parser dla Python 2.0 oraz later.
    def __init__(self, target):
        self._parser = parser = expat.ParserCreate(Nic, Nic)
        self._target = target
        parser.StartElementHandler = target.start
        parser.EndElementHandler = target.end
        parser.CharacterDataHandler = target.data
        encoding = Nic
        target.xml(encoding, Nic)

    def feed(self, data):
        self._parser.Parse(data, 0)

    def close(self):
        spróbuj:
            parser = self._parser
        wyjąwszy AttributeError:
            dalej
        inaczej:
            usuń self._target, self._parser # get rid of circular references
            parser.Parse(b"", Prawda) # end of data

# --------------------------------------------------------------------
# XML-RPC marshalling oraz unmarshalling code

##
# XML-RPC marshaller.
#
# @param encoding Default encoding dla 8-bit strings.  The default
#     value jest Nic (interpreted jako UTF-8).
# @see dumps

klasa Marshaller:
    """Generate an XML-RPC params chunk z a Python data structure.

    Create a Marshaller instance dla each set of parameters, oraz use
    the "dumps" method to convert your data (represented jako a tuple)
    to an XML-RPC params chunk.  To write a fault response, dalej a
    Fault instance instead.  You may prefer to use the "dumps" module
    function dla this purpose.
    """

    # by the way, jeżeli you don't understand what's going on w here,
    # that's perfectly ok.

    def __init__(self, encoding=Nic, allow_none=Nieprawda):
        self.memo = {}
        self.data = Nic
        self.encoding = encoding
        self.allow_none = allow_none

    dispatch = {}

    def dumps(self, values):
        out = []
        write = out.append
        dump = self.__dump
        jeżeli isinstance(values, Fault):
            # fault instance
            write("<fault>\n")
            dump({'faultCode': values.faultCode,
                  'faultString': values.faultString},
                 write)
            write("</fault>\n")
        inaczej:
            # parameter block
            # FIXME: the xml-rpc specification allows us to leave out
            # the entire <params> block jeżeli there are no parameters.
            # however, changing this may przerwij older code (including
            # old versions of xmlrpclib.py), so this jest better left as
            # jest dla now.  See @XMLRPC3 dla more information. /F
            write("<params>\n")
            dla v w values:
                write("<param>\n")
                dump(v, write)
                write("</param>\n")
            write("</params>\n")
        result = "".join(out)
        zwróć result

    def __dump(self, value, write):
        spróbuj:
            f = self.dispatch[type(value)]
        wyjąwszy KeyError:
            # check jeżeli this object can be marshalled jako a structure
            jeżeli nie hasattr(value, '__dict__'):
                podnieś TypeError("cannot marshal %s objects" % type(value))
            # check jeżeli this klasa jest a sub-class of a basic type,
            # because we don't know how to marshal these types
            # (e.g. a string sub-class)
            dla type_ w type(value).__mro__:
                jeżeli type_ w self.dispatch.keys():
                    podnieś TypeError("cannot marshal %s objects" % type(value))
            # XXX(twouters): using "_arbitrary_instance" jako key jako a quick-fix
            # dla the p3yk merge, this should probably be fixed more neatly.
            f = self.dispatch["_arbitrary_instance"]
        f(self, value, write)

    def dump_nil (self, value, write):
        jeżeli nie self.allow_none:
            podnieś TypeError("cannot marshal Nic unless allow_none jest enabled")
        write("<value><nil/></value>")
    dispatch[type(Nic)] = dump_nil

    def dump_bool(self, value, write):
        write("<value><boolean>")
        write(value oraz "1" albo "0")
        write("</boolean></value>\n")
    dispatch[bool] = dump_bool

    def dump_long(self, value, write):
        jeżeli value > MAXINT albo value < MININT:
            podnieś OverflowError("int exceeds XML-RPC limits")
        write("<value><int>")
        write(str(int(value)))
        write("</int></value>\n")
    dispatch[int] = dump_long

    # backward compatible
    dump_int = dump_long

    def dump_double(self, value, write):
        write("<value><double>")
        write(repr(value))
        write("</double></value>\n")
    dispatch[float] = dump_double

    def dump_unicode(self, value, write, escape=escape):
        write("<value><string>")
        write(escape(value))
        write("</string></value>\n")
    dispatch[str] = dump_unicode

    def dump_bytes(self, value, write):
        write("<value><base64>\n")
        encoded = base64.encodebytes(value)
        write(encoded.decode('ascii'))
        write("</base64></value>\n")
    dispatch[bytes] = dump_bytes
    dispatch[bytearray] = dump_bytes

    def dump_array(self, value, write):
        i = id(value)
        jeżeli i w self.memo:
            podnieś TypeError("cannot marshal recursive sequences")
        self.memo[i] = Nic
        dump = self.__dump
        write("<value><array><data>\n")
        dla v w value:
            dump(v, write)
        write("</data></array></value>\n")
        usuń self.memo[i]
    dispatch[tuple] = dump_array
    dispatch[list] = dump_array

    def dump_struct(self, value, write, escape=escape):
        i = id(value)
        jeżeli i w self.memo:
            podnieś TypeError("cannot marshal recursive dictionaries")
        self.memo[i] = Nic
        dump = self.__dump
        write("<value><struct>\n")
        dla k, v w value.items():
            write("<member>\n")
            jeżeli nie isinstance(k, str):
                podnieś TypeError("dictionary key must be string")
            write("<name>%s</name>\n" % escape(k))
            dump(v, write)
            write("</member>\n")
        write("</struct></value>\n")
        usuń self.memo[i]
    dispatch[dict] = dump_struct

    def dump_datetime(self, value, write):
        write("<value><dateTime.iso8601>")
        write(_strftime(value))
        write("</dateTime.iso8601></value>\n")
    dispatch[datetime] = dump_datetime

    def dump_instance(self, value, write):
        # check dla special wrappers
        jeżeli value.__class__ w WRAPPERS:
            self.write = write
            value.encode(self)
            usuń self.write
        inaczej:
            # store instance attributes jako a struct (really?)
            self.dump_struct(value.__dict__, write)
    dispatch[DateTime] = dump_instance
    dispatch[Binary] = dump_instance
    # XXX(twouters): using "_arbitrary_instance" jako key jako a quick-fix
    # dla the p3yk merge, this should probably be fixed more neatly.
    dispatch["_arbitrary_instance"] = dump_instance

##
# XML-RPC unmarshaller.
#
# @see loads

klasa Unmarshaller:
    """Unmarshal an XML-RPC response, based on incoming XML event
    messages (start, data, end).  Call close() to get the resulting
    data structure.

    Note that this reader jest fairly tolerant, oraz gladly accepts bogus
    XML-RPC data without complaining (but nie bogus XML).
    """

    # oraz again, jeżeli you don't understand what's going on w here,
    # that's perfectly ok.

    def __init__(self, use_datetime=Nieprawda, use_builtin_types=Nieprawda):
        self._type = Nic
        self._stack = []
        self._marks = []
        self._data = []
        self._methodname = Nic
        self._encoding = "utf-8"
        self.append = self._stack.append
        self._use_datetime = use_builtin_types albo use_datetime
        self._use_bytes = use_builtin_types

    def close(self):
        # zwróć response tuple oraz target method
        jeżeli self._type jest Nic albo self._marks:
            podnieś ResponseError()
        jeżeli self._type == "fault":
            podnieś Fault(**self._stack[0])
        zwróć tuple(self._stack)

    def getmethodname(self):
        zwróć self._methodname

    #
    # event handlers

    def xml(self, encoding, standalone):
        self._encoding = encoding
        # FIXME: assert standalone == 1 ???

    def start(self, tag, attrs):
        # prepare to handle this element
        jeżeli tag == "array" albo tag == "struct":
            self._marks.append(len(self._stack))
        self._data = []
        self._value = (tag == "value")

    def data(self, text):
        self._data.append(text)

    def end(self, tag):
        # call the appropriate end tag handler
        spróbuj:
            f = self.dispatch[tag]
        wyjąwszy KeyError:
            dalej # unknown tag ?
        inaczej:
            zwróć f(self, "".join(self._data))

    #
    # accelerator support

    def end_dispatch(self, tag, data):
        # dispatch data
        spróbuj:
            f = self.dispatch[tag]
        wyjąwszy KeyError:
            dalej # unknown tag ?
        inaczej:
            zwróć f(self, data)

    #
    # element decoders

    dispatch = {}

    def end_nil (self, data):
        self.append(Nic)
        self._value = 0
    dispatch["nil"] = end_nil

    def end_boolean(self, data):
        jeżeli data == "0":
            self.append(Nieprawda)
        albo_inaczej data == "1":
            self.append(Prawda)
        inaczej:
            podnieś TypeError("bad boolean value")
        self._value = 0
    dispatch["boolean"] = end_boolean

    def end_int(self, data):
        self.append(int(data))
        self._value = 0
    dispatch["i4"] = end_int
    dispatch["i8"] = end_int
    dispatch["int"] = end_int

    def end_double(self, data):
        self.append(float(data))
        self._value = 0
    dispatch["double"] = end_double

    def end_string(self, data):
        jeżeli self._encoding:
            data = data.decode(self._encoding)
        self.append(data)
        self._value = 0
    dispatch["string"] = end_string
    dispatch["name"] = end_string # struct keys are always strings

    def end_array(self, data):
        mark = self._marks.pop()
        # map arrays to Python lists
        self._stack[mark:] = [self._stack[mark:]]
        self._value = 0
    dispatch["array"] = end_array

    def end_struct(self, data):
        mark = self._marks.pop()
        # map structs to Python dictionaries
        dict = {}
        items = self._stack[mark:]
        dla i w range(0, len(items), 2):
            dict[items[i]] = items[i+1]
        self._stack[mark:] = [dict]
        self._value = 0
    dispatch["struct"] = end_struct

    def end_base64(self, data):
        value = Binary()
        value.decode(data.encode("ascii"))
        jeżeli self._use_bytes:
            value = value.data
        self.append(value)
        self._value = 0
    dispatch["base64"] = end_base64

    def end_dateTime(self, data):
        value = DateTime()
        value.decode(data)
        jeżeli self._use_datetime:
            value = _datetime_type(data)
        self.append(value)
    dispatch["dateTime.iso8601"] = end_dateTime

    def end_value(self, data):
        # jeżeli we stumble upon a value element przy no internal
        # elements, treat it jako a string element
        jeżeli self._value:
            self.end_string(data)
    dispatch["value"] = end_value

    def end_params(self, data):
        self._type = "params"
    dispatch["params"] = end_params

    def end_fault(self, data):
        self._type = "fault"
    dispatch["fault"] = end_fault

    def end_methodName(self, data):
        jeżeli self._encoding:
            data = data.decode(self._encoding)
        self._methodname = data
        self._type = "methodName" # no params
    dispatch["methodName"] = end_methodName

## Multicall support
#

klasa _MultiCallMethod:
    # some lesser magic to store calls made to a MultiCall object
    # dla batch execution
    def __init__(self, call_list, name):
        self.__call_list = call_list
        self.__name = name
    def __getattr__(self, name):
        zwróć _MultiCallMethod(self.__call_list, "%s.%s" % (self.__name, name))
    def __call__(self, *args):
        self.__call_list.append((self.__name, args))

klasa MultiCallIterator:
    """Iterates over the results of a multicall. Exceptions are
    podnieśd w response to xmlrpc faults."""

    def __init__(self, results):
        self.results = results

    def __getitem__(self, i):
        item = self.results[i]
        jeżeli type(item) == type({}):
            podnieś Fault(item['faultCode'], item['faultString'])
        albo_inaczej type(item) == type([]):
            zwróć item[0]
        inaczej:
            podnieś ValueError("unexpected type w multicall result")

klasa MultiCall:
    """server -> a object used to boxcar method calls

    server should be a ServerProxy object.

    Methods can be added to the MultiCall using normal
    method call syntax e.g.:

    multicall = MultiCall(server_proxy)
    multicall.add(2,3)
    multicall.get_address("Guido")

    To execute the multicall, call the MultiCall object e.g.:

    add_result, address = multicall()
    """

    def __init__(self, server):
        self.__server = server
        self.__call_list = []

    def __repr__(self):
        zwróć "<%s at %#x>" % (self.__class__.__name__, id(self))

    __str__ = __repr__

    def __getattr__(self, name):
        zwróć _MultiCallMethod(self.__call_list, name)

    def __call__(self):
        marshalled_list = []
        dla name, args w self.__call_list:
            marshalled_list.append({'methodName' : name, 'params' : args})

        zwróć MultiCallIterator(self.__server.system.multicall(marshalled_list))

# --------------------------------------------------------------------
# convenience functions

FastMarshaller = FastParser = FastUnmarshaller = Nic

##
# Create a parser object, oraz connect it to an unmarshalling instance.
# This function picks the fastest available XML parser.
#
# zwróć A (parser, unmarshaller) tuple.

def getparser(use_datetime=Nieprawda, use_builtin_types=Nieprawda):
    """getparser() -> parser, unmarshaller

    Create an instance of the fastest available parser, oraz attach it
    to an unmarshalling object.  Return both objects.
    """
    jeżeli FastParser oraz FastUnmarshaller:
        jeżeli use_builtin_types:
            mkdatetime = _datetime_type
            mkbytes = base64.decodebytes
        albo_inaczej use_datetime:
            mkdatetime = _datetime_type
            mkbytes = _binary
        inaczej:
            mkdatetime = _datetime
            mkbytes = _binary
        target = FastUnmarshaller(Prawda, Nieprawda, mkbytes, mkdatetime, Fault)
        parser = FastParser(target)
    inaczej:
        target = Unmarshaller(use_datetime=use_datetime, use_builtin_types=use_builtin_types)
        jeżeli FastParser:
            parser = FastParser(target)
        inaczej:
            parser = ExpatParser(target)
    zwróć parser, target

##
# Convert a Python tuple albo a Fault instance to an XML-RPC packet.
#
# @def dumps(params, **options)
# @param params A tuple albo Fault instance.
# @keyparam methodname If given, create a methodCall request for
#     this method name.
# @keyparam methodresponse If given, create a methodResponse packet.
#     If used przy a tuple, the tuple must be a singleton (that is,
#     it must contain exactly one element).
# @keyparam encoding The packet encoding.
# @return A string containing marshalled data.

def dumps(params, methodname=Nic, methodresponse=Nic, encoding=Nic,
          allow_none=Nieprawda):
    """data [,options] -> marshalled data

    Convert an argument tuple albo a Fault instance to an XML-RPC
    request (or response, jeżeli the methodresponse option jest used).

    In addition to the data object, the following options can be given
    jako keyword arguments:

        methodname: the method name dla a methodCall packet

        methodresponse: true to create a methodResponse packet.
        If this option jest used przy a tuple, the tuple must be
        a singleton (i.e. it can contain only one element).

        encoding: the packet encoding (default jest UTF-8)

    All byte strings w the data structure are assumed to use the
    packet encoding.  Unicode strings are automatically converted,
    where necessary.
    """

    assert isinstance(params, (tuple, Fault)), "argument must be tuple albo Fault instance"
    jeżeli isinstance(params, Fault):
        methodresponse = 1
    albo_inaczej methodresponse oraz isinstance(params, tuple):
        assert len(params) == 1, "response tuple must be a singleton"

    jeżeli nie encoding:
        encoding = "utf-8"

    jeżeli FastMarshaller:
        m = FastMarshaller(encoding)
    inaczej:
        m = Marshaller(encoding, allow_none)

    data = m.dumps(params)

    jeżeli encoding != "utf-8":
        xmlheader = "<?xml version='1.0' encoding='%s'?>\n" % str(encoding)
    inaczej:
        xmlheader = "<?xml version='1.0'?>\n" # utf-8 jest default

    # standard XML-RPC wrappings
    jeżeli methodname:
        # a method call
        jeżeli nie isinstance(methodname, str):
            methodname = methodname.encode(encoding)
        data = (
            xmlheader,
            "<methodCall>\n"
            "<methodName>", methodname, "</methodName>\n",
            data,
            "</methodCall>\n"
            )
    albo_inaczej methodresponse:
        # a method response, albo a fault structure
        data = (
            xmlheader,
            "<methodResponse>\n",
            data,
            "</methodResponse>\n"
            )
    inaczej:
        zwróć data # zwróć jako jest
    zwróć "".join(data)

##
# Convert an XML-RPC packet to a Python object.  If the XML-RPC packet
# represents a fault condition, this function podnieśs a Fault exception.
#
# @param data An XML-RPC packet, given jako an 8-bit string.
# @return A tuple containing the unpacked data, oraz the method name
#     (Nic jeżeli nie present).
# @see Fault

def loads(data, use_datetime=Nieprawda, use_builtin_types=Nieprawda):
    """data -> unmarshalled data, method name

    Convert an XML-RPC packet to unmarshalled data plus a method
    name (Nic jeżeli nie present).

    If the XML-RPC packet represents a fault condition, this function
    podnieśs a Fault exception.
    """
    p, u = getparser(use_datetime=use_datetime, use_builtin_types=use_builtin_types)
    p.feed(data)
    p.close()
    zwróć u.close(), u.getmethodname()

##
# Encode a string using the gzip content encoding such jako specified by the
# Content-Encoding: gzip
# w the HTTP header, jako described w RFC 1952
#
# @param data the unencoded data
# @return the encoded data

def gzip_encode(data):
    """data -> gzip encoded data

    Encode data using the gzip content encoding jako described w RFC 1952
    """
    jeżeli nie gzip:
        podnieś NotImplementedError
    f = BytesIO()
    przy gzip.GzipFile(mode="wb", fileobj=f, compresslevel=1) jako gzf:
        gzf.write(data)
    zwróć f.getvalue()

##
# Decode a string using the gzip content encoding such jako specified by the
# Content-Encoding: gzip
# w the HTTP header, jako described w RFC 1952
#
# @param data The encoded data
# @keyparam max_decode Maximum bytes to decode (20MB default), use negative
#    values dla unlimited decoding
# @return the unencoded data
# @raises ValueError jeżeli data jest nie correctly coded.
# @raises ValueError jeżeli max gzipped payload length exceeded

def gzip_decode(data, max_decode=20971520):
    """gzip encoded data -> unencoded data

    Decode data using the gzip content encoding jako described w RFC 1952
    """
    jeżeli nie gzip:
        podnieś NotImplementedError
    przy gzip.GzipFile(mode="rb", fileobj=BytesIO(data)) jako gzf:
        spróbuj:
            jeżeli max_decode < 0: # no limit
                decoded = gzf.read()
            inaczej:
                decoded = gzf.read(max_decode + 1)
        wyjąwszy OSError:
            podnieś ValueError("invalid data")
    jeżeli max_decode >= 0 oraz len(decoded) > max_decode:
        podnieś ValueError("max gzipped payload length exceeded")
    zwróć decoded

##
# Return a decoded file-like object dla the gzip encoding
# jako described w RFC 1952.
#
# @param response A stream supporting a read() method
# @return a file-like object that the decoded data can be read() from

klasa GzipDecodedResponse(gzip.GzipFile jeżeli gzip inaczej object):
    """a file-like object to decode a response encoded przy the gzip
    method, jako described w RFC 1952.
    """
    def __init__(self, response):
        #response doesn't support tell() oraz read(), required by
        #GzipFile
        jeżeli nie gzip:
            podnieś NotImplementedError
        self.io = BytesIO(response.read())
        gzip.GzipFile.__init__(self, mode="rb", fileobj=self.io)

    def close(self):
        spróbuj:
            gzip.GzipFile.close(self)
        w_końcu:
            self.io.close()


# --------------------------------------------------------------------
# request dispatcher

klasa _Method:
    # some magic to bind an XML-RPC method to an RPC server.
    # supports "nested" methods (e.g. examples.getStateName)
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
    def __getattr__(self, name):
        zwróć _Method(self.__send, "%s.%s" % (self.__name, name))
    def __call__(self, *args):
        zwróć self.__send(self.__name, args)

##
# Standard transport klasa dla XML-RPC over HTTP.
# <p>
# You can create custom transports by subclassing this method, oraz
# overriding selected methods.

klasa Transport:
    """Handles an HTTP transaction to an XML-RPC server."""

    # client identifier (may be overridden)
    user_agent = "Python-xmlrpc/%s" % __version__

    #jeżeli true, we'll request gzip encoding
    accept_gzip_encoding = Prawda

    # jeżeli positive, encode request using gzip jeżeli it exceeds this threshold
    # note that many server will get confused, so only use it jeżeli you know
    # that they can decode such a request
    encode_threshold = Nic #Nic = don't encode

    def __init__(self, use_datetime=Nieprawda, use_builtin_types=Nieprawda):
        self._use_datetime = use_datetime
        self._use_builtin_types = use_builtin_types
        self._connection = (Nic, Nic)
        self._extra_headers = []

    ##
    # Send a complete request, oraz parse the response.
    # Retry request jeżeli a cached connection has disconnected.
    #
    # @param host Target host.
    # @param handler Target PRC handler.
    # @param request_body XML-RPC request body.
    # @param verbose Debugging flag.
    # @return Parsed response.

    def request(self, host, handler, request_body, verbose=Nieprawda):
        #retry request once jeżeli cached connection has gone cold
        dla i w (0, 1):
            spróbuj:
                zwróć self.single_request(host, handler, request_body, verbose)
            wyjąwszy OSError jako e:
                jeżeli i albo e.errno nie w (errno.ECONNRESET, errno.ECONNABORTED,
                                        errno.EPIPE):
                    podnieś
            wyjąwszy http.client.RemoteDisconnected:
                jeżeli i:
                    podnieś

    def single_request(self, host, handler, request_body, verbose=Nieprawda):
        # issue XML-RPC request
        spróbuj:
            http_conn = self.send_request(host, handler, request_body, verbose)
            resp = http_conn.getresponse()
            jeżeli resp.status == 200:
                self.verbose = verbose
                zwróć self.parse_response(resp)

        wyjąwszy Fault:
            podnieś
        wyjąwszy Exception:
            #All unexpected errors leave connection w
            # a strange state, so we clear it.
            self.close()
            podnieś

        #We got an error response.
        #Discard any response data oraz podnieś exception
        jeżeli resp.getheader("content-length", ""):
            resp.read()
        podnieś ProtocolError(
            host + handler,
            resp.status, resp.reason,
            dict(resp.getheaders())
            )


    ##
    # Create parser.
    #
    # @return A 2-tuple containing a parser oraz a unmarshaller.

    def getparser(self):
        # get parser oraz unmarshaller
        zwróć getparser(use_datetime=self._use_datetime,
                         use_builtin_types=self._use_builtin_types)

    ##
    # Get authorization info z host parameter
    # Host may be a string, albo a (host, x509-dict) tuple; jeżeli a string,
    # it jest checked dla a "user:pw@host" format, oraz a "Basic
    # Authentication" header jest added jeżeli appropriate.
    #
    # @param host Host descriptor (URL albo (URL, x509 info) tuple).
    # @return A 3-tuple containing (actual host, extra headers,
    #     x509 info).  The header oraz x509 fields may be Nic.

    def get_host_info(self, host):

        x509 = {}
        jeżeli isinstance(host, tuple):
            host, x509 = host

        auth, host = urllib.parse.splituser(host)

        jeżeli auth:
            auth = urllib.parse.unquote_to_bytes(auth)
            auth = base64.encodebytes(auth).decode("utf-8")
            auth = "".join(auth.split()) # get rid of whitespace
            extra_headers = [
                ("Authorization", "Basic " + auth)
                ]
        inaczej:
            extra_headers = []

        zwróć host, extra_headers, x509

    ##
    # Connect to server.
    #
    # @param host Target host.
    # @return An HTTPConnection object

    def make_connection(self, host):
        #return an existing connection jeżeli possible.  This allows
        #HTTP/1.1 keep-alive.
        jeżeli self._connection oraz host == self._connection[0]:
            zwróć self._connection[1]
        # create a HTTP connection object z a host descriptor
        chost, self._extra_headers, x509 = self.get_host_info(host)
        self._connection = host, http.client.HTTPConnection(chost)
        zwróć self._connection[1]

    ##
    # Clear any cached connection object.
    # Used w the event of socket errors.
    #
    def close(self):
        host, connection = self._connection
        jeżeli connection:
            self._connection = (Nic, Nic)
            connection.close()

    ##
    # Send HTTP request.
    #
    # @param host Host descriptor (URL albo (URL, x509 info) tuple).
    # @param handler Targer RPC handler (a path relative to host)
    # @param request_body The XML-RPC request body
    # @param debug Enable debugging jeżeli debug jest true.
    # @return An HTTPConnection.

    def send_request(self, host, handler, request_body, debug):
        connection = self.make_connection(host)
        headers = self._extra_headers[:]
        jeżeli debug:
            connection.set_debuglevel(1)
        jeżeli self.accept_gzip_encoding oraz gzip:
            connection.putrequest("POST", handler, skip_accept_encoding=Prawda)
            headers.append(("Accept-Encoding", "gzip"))
        inaczej:
            connection.putrequest("POST", handler)
        headers.append(("Content-Type", "text/xml"))
        headers.append(("User-Agent", self.user_agent))
        self.send_headers(connection, headers)
        self.send_content(connection, request_body)
        zwróć connection

    ##
    # Send request headers.
    # This function provides a useful hook dla subclassing
    #
    # @param connection httpConnection.
    # @param headers list of key,value pairs dla HTTP headers

    def send_headers(self, connection, headers):
        dla key, val w headers:
            connection.putheader(key, val)

    ##
    # Send request body.
    # This function provides a useful hook dla subclassing
    #
    # @param connection httpConnection.
    # @param request_body XML-RPC request body.

    def send_content(self, connection, request_body):
        #optionally encode the request
        jeżeli (self.encode_threshold jest nie Nic oraz
            self.encode_threshold < len(request_body) oraz
            gzip):
            connection.putheader("Content-Encoding", "gzip")
            request_body = gzip_encode(request_body)

        connection.putheader("Content-Length", str(len(request_body)))
        connection.endheaders(request_body)

    ##
    # Parse response.
    #
    # @param file Stream.
    # @return Response tuple oraz target method.

    def parse_response(self, response):
        # read response data z httpresponse, oraz parse it
        # Check dla new http response object, otherwise it jest a file object.
        jeżeli hasattr(response, 'getheader'):
            jeżeli response.getheader("Content-Encoding", "") == "gzip":
                stream = GzipDecodedResponse(response)
            inaczej:
                stream = response
        inaczej:
            stream = response

        p, u = self.getparser()

        dopóki 1:
            data = stream.read(1024)
            jeżeli nie data:
                przerwij
            jeżeli self.verbose:
                print("body:", repr(data))
            p.feed(data)

        jeżeli stream jest nie response:
            stream.close()
        p.close()

        zwróć u.close()

##
# Standard transport klasa dla XML-RPC over HTTPS.

klasa SafeTransport(Transport):
    """Handles an HTTPS transaction to an XML-RPC server."""

    def __init__(self, use_datetime=Nieprawda, use_builtin_types=Nieprawda, *,
                 context=Nic):
        super().__init__(use_datetime=use_datetime, use_builtin_types=use_builtin_types)
        self.context = context

    # FIXME: mostly untested

    def make_connection(self, host):
        jeżeli self._connection oraz host == self._connection[0]:
            zwróć self._connection[1]

        jeżeli nie hasattr(http.client, "HTTPSConnection"):
            podnieś NotImplementedError(
            "your version of http.client doesn't support HTTPS")
        # create a HTTPS connection object z a host descriptor
        # host may be a string, albo a (host, x509-dict) tuple
        chost, self._extra_headers, x509 = self.get_host_info(host)
        self._connection = host, http.client.HTTPSConnection(chost,
            Nic, context=self.context, **(x509 albo {}))
        zwróć self._connection[1]

##
# Standard server proxy.  This klasa establishes a virtual connection
# to an XML-RPC server.
# <p>
# This klasa jest available jako ServerProxy oraz Server.  New code should
# use ServerProxy, to avoid confusion.
#
# @def ServerProxy(uri, **options)
# @param uri The connection point on the server.
# @keyparam transport A transport factory, compatible przy the
#    standard transport class.
# @keyparam encoding The default encoding used dla 8-bit strings
#    (default jest UTF-8).
# @keyparam verbose Use a true value to enable debugging output.
#    (printed to standard output).
# @see Transport

klasa ServerProxy:
    """uri [,options] -> a logical connection to an XML-RPC server

    uri jest the connection point on the server, given as
    scheme://host/target.

    The standard implementation always supports the "http" scheme.  If
    SSL socket support jest available (Python 2.0), it also supports
    "https".

    If the target part oraz the slash preceding it are both omitted,
    "/RPC2" jest assumed.

    The following options can be given jako keyword arguments:

        transport: a transport factory
        encoding: the request encoding (default jest UTF-8)

    All 8-bit strings dalejed to the server proxy are assumed to use
    the given encoding.
    """

    def __init__(self, uri, transport=Nic, encoding=Nic, verbose=Nieprawda,
                 allow_none=Nieprawda, use_datetime=Nieprawda, use_builtin_types=Nieprawda,
                 *, context=Nic):
        # establish a "logical" server connection

        # get the url
        type, uri = urllib.parse.splittype(uri)
        jeżeli type nie w ("http", "https"):
            podnieś OSError("unsupported XML-RPC protocol")
        self.__host, self.__handler = urllib.parse.splithost(uri)
        jeżeli nie self.__handler:
            self.__handler = "/RPC2"

        jeżeli transport jest Nic:
            jeżeli type == "https":
                handler = SafeTransport
                extra_kwargs = {"context": context}
            inaczej:
                handler = Transport
                extra_kwargs = {}
            transport = handler(use_datetime=use_datetime,
                                use_builtin_types=use_builtin_types,
                                **extra_kwargs)
        self.__transport = transport

        self.__encoding = encoding albo 'utf-8'
        self.__verbose = verbose
        self.__allow_none = allow_none

    def __close(self):
        self.__transport.close()

    def __request(self, methodname, params):
        # call a method on the remote server

        request = dumps(params, methodname, encoding=self.__encoding,
                        allow_none=self.__allow_none).encode(self.__encoding)

        response = self.__transport.request(
            self.__host,
            self.__handler,
            request,
            verbose=self.__verbose
            )

        jeżeli len(response) == 1:
            response = response[0]

        zwróć response

    def __repr__(self):
        zwróć (
            "<%s dla %s%s>" %
            (self.__class__.__name__, self.__host, self.__handler)
            )

    __str__ = __repr__

    def __getattr__(self, name):
        # magic method dispatcher
        zwróć _Method(self.__request, name)

    # note: to call a remote object przy an non-standard name, use
    # result getattr(server, "strange-python-name")(args)

    def __call__(self, attr):
        """A workaround to get special attributes on the ServerProxy
           without interfering przy the magic __getattr__
        """
        jeżeli attr == "close":
            zwróć self.__close
        albo_inaczej attr == "transport":
            zwróć self.__transport
        podnieś AttributeError("Attribute %r nie found" % (attr,))

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        self.__close()

# compatibility

Server = ServerProxy

# --------------------------------------------------------------------
# test code

jeżeli __name__ == "__main__":

    # simple test program (z the XML-RPC specification)

    # local server, available z Lib/xmlrpc/server.py
    server = ServerProxy("http://localhost:8000")

    spróbuj:
        print(server.currentTime.getCurrentTime())
    wyjąwszy Error jako v:
        print("ERROR", v)

    multi = MultiCall(server)
    multi.getData()
    multi.pow(2,9)
    multi.add(1,2)
    spróbuj:
        dla response w multi():
            print(response)
    wyjąwszy Error jako v:
        print("ERROR", v)
