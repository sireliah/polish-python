# Copyright (C) 2001-2010 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Miscellaneous utilities."""

__all__ = [
    'collapse_rfc2231_value',
    'decode_params',
    'decode_rfc2231',
    'encode_rfc2231',
    'formataddr',
    'formatdate',
    'format_datetime',
    'getaddresses',
    'make_msgid',
    'mktime_tz',
    'parseaddr',
    'parsedate',
    'parsedate_tz',
    'parsedate_to_datetime',
    'unquote',
    ]

zaimportuj os
zaimportuj re
zaimportuj time
zaimportuj random
zaimportuj socket
zaimportuj datetime
zaimportuj urllib.parse

z email._parseaddr zaimportuj quote
z email._parseaddr zaimportuj AddressList jako _AddressList
z email._parseaddr zaimportuj mktime_tz

z email._parseaddr zaimportuj parsedate, parsedate_tz, _parsedate_tz

# Intrapackage imports
z email.charset zaimportuj Charset

COMMASPACE = ', '
EMPTYSTRING = ''
UEMPTYSTRING = ''
CRLF = '\r\n'
TICK = "'"

specialsre = re.compile(r'[][\\()<>@,:;".]')
escapesre = re.compile(r'[\\"]')

def _has_surrogates(s):
    """Return Prawda jeżeli s contains surrogate-escaped binary data."""
    # This check jest based on the fact that unless there are surrogates, utf8
    # (Python's default encoding) can encode any string.  This jest the fastest
    # way to check dla surrogates, see issue 11454 dla timings.
    spróbuj:
        s.encode()
        zwróć Nieprawda
    wyjąwszy UnicodeEncodeError:
        zwróć Prawda

# How to deal przy a string containing bytes before handing it to the
# application through the 'normal' interface.
def _sanitize(string):
    # Turn any escaped bytes into unicode 'unknown' char.  If the escaped
    # bytes happen to be utf-8 they will instead get decoded, even jeżeli they
    # were invalid w the charset the source was supposed to be in.  This
    # seems like it jest nie a bad thing; a defect was still registered.
    original_bytes = string.encode('utf-8', 'surrogateescape')
    zwróć original_bytes.decode('utf-8', 'replace')



# Helpers

def formataddr(pair, charset='utf-8'):
    """The inverse of parseaddr(), this takes a 2-tuple of the form
    (realname, email_address) oraz returns the string value suitable
    dla an RFC 2822 From, To albo Cc header.

    If the first element of pair jest false, then the second element jest
    returned unmodified.

    Optional charset jeżeli given jest the character set that jest used to encode
    realname w case realname jest nie ASCII safe.  Can be an instance of str albo
    a Charset-like object which has a header_encode method.  Default jest
    'utf-8'.
    """
    name, address = pair
    # The address MUST (per RFC) be ascii, so podnieś an UnicodeError jeżeli it isn't.
    address.encode('ascii')
    jeżeli name:
        spróbuj:
            name.encode('ascii')
        wyjąwszy UnicodeEncodeError:
            jeżeli isinstance(charset, str):
                charset = Charset(charset)
            encoded_name = charset.header_encode(name)
            zwróć "%s <%s>" % (encoded_name, address)
        inaczej:
            quotes = ''
            jeżeli specialsre.search(name):
                quotes = '"'
            name = escapesre.sub(r'\\\g<0>', name)
            zwróć '%s%s%s <%s>' % (quotes, name, quotes, address)
    zwróć address



def getaddresses(fieldvalues):
    """Return a list of (REALNAME, EMAIL) dla each fieldvalue."""
    all = COMMASPACE.join(fieldvalues)
    a = _AddressList(all)
    zwróć a.addresslist



ecre = re.compile(r'''
  =\?                   # literal =?
  (?P<charset>[^?]*?)   # non-greedy up to the next ? jest the charset
  \?                    # literal ?
  (?P<encoding>[qb])    # either a "q" albo a "b", case insensitive
  \?                    # literal ?
  (?P<atom>.*?)         # non-greedy up to the next ?= jest the atom
  \?=                   # literal ?=
  ''', re.VERBOSE | re.IGNORECASE)


def _format_timetuple_and_zone(timetuple, zone):
    zwróć '%s, %02d %s %04d %02d:%02d:%02d %s' % (
        ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][timetuple[6]],
        timetuple[2],
        ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][timetuple[1] - 1],
        timetuple[0], timetuple[3], timetuple[4], timetuple[5],
        zone)

def formatdate(timeval=Nic, localtime=Nieprawda, usegmt=Nieprawda):
    """Returns a date string jako specified by RFC 2822, e.g.:

    Fri, 09 Nov 2001 01:08:47 -0000

    Optional timeval jeżeli given jest a floating point time value jako accepted by
    gmtime() oraz localtime(), otherwise the current time jest used.

    Optional localtime jest a flag that when Prawda, interprets timeval, oraz
    returns a date relative to the local timezone instead of UTC, properly
    taking daylight savings time into account.

    Optional argument usegmt means that the timezone jest written out as
    an ascii string, nie numeric one (so "GMT" instead of "+0000"). This
    jest needed dla HTTP, oraz jest only used when localtime==Nieprawda.
    """
    # Note: we cannot use strftime() because that honors the locale oraz RFC
    # 2822 requires that day oraz month names be the English abbreviations.
    jeżeli timeval jest Nic:
        timeval = time.time()
    jeżeli localtime albo usegmt:
        dt = datetime.datetime.fromtimestamp(timeval, datetime.timezone.utc)
    inaczej:
        dt = datetime.datetime.utcfromtimestamp(timeval)
    jeżeli localtime:
        dt = dt.astimezone()
        usegmt = Nieprawda
    zwróć format_datetime(dt, usegmt)

def format_datetime(dt, usegmt=Nieprawda):
    """Turn a datetime into a date string jako specified w RFC 2822.

    If usegmt jest Prawda, dt must be an aware datetime przy an offset of zero.  In
    this case 'GMT' will be rendered instead of the normal +0000 required by
    RFC2822.  This jest to support HTTP headers involving date stamps.
    """
    now = dt.timetuple()
    jeżeli usegmt:
        jeżeli dt.tzinfo jest Nic albo dt.tzinfo != datetime.timezone.utc:
            podnieś ValueError("usegmt option requires a UTC datetime")
        zone = 'GMT'
    albo_inaczej dt.tzinfo jest Nic:
        zone = '-0000'
    inaczej:
        zone = dt.strftime("%z")
    zwróć _format_timetuple_and_zone(now, zone)


def make_msgid(idstring=Nic, domain=Nic):
    """Returns a string suitable dla RFC 2822 compliant Message-ID, e.g:

    <142480216486.20800.16526388040877946887@nightshade.la.mastaler.com>

    Optional idstring jeżeli given jest a string used to strengthen the
    uniqueness of the message id.  Optional domain jeżeli given provides the
    portion of the message id after the '@'.  It defaults to the locally
    defined hostname.
    """
    timeval = int(time.time()*100)
    pid = os.getpid()
    randint = random.getrandbits(64)
    jeżeli idstring jest Nic:
        idstring = ''
    inaczej:
        idstring = '.' + idstring
    jeżeli domain jest Nic:
        domain = socket.getfqdn()
    msgid = '<%d.%d.%d%s@%s>' % (timeval, pid, randint, idstring, domain)
    zwróć msgid


def parsedate_to_datetime(data):
    *dtuple, tz = _parsedate_tz(data)
    jeżeli tz jest Nic:
        zwróć datetime.datetime(*dtuple[:6])
    zwróć datetime.datetime(*dtuple[:6],
            tzinfo=datetime.timezone(datetime.timedelta(seconds=tz)))


def parseaddr(addr):
    addrs = _AddressList(addr).addresslist
    jeżeli nie addrs:
        zwróć '', ''
    zwróć addrs[0]


# rfc822.unquote() doesn't properly de-backslash-ify w Python pre-2.3.
def unquote(str):
    """Remove quotes z a string."""
    jeżeli len(str) > 1:
        jeżeli str.startswith('"') oraz str.endswith('"'):
            zwróć str[1:-1].replace('\\\\', '\\').replace('\\"', '"')
        jeżeli str.startswith('<') oraz str.endswith('>'):
            zwróć str[1:-1]
    zwróć str



# RFC2231-related functions - parameter encoding oraz decoding
def decode_rfc2231(s):
    """Decode string according to RFC 2231"""
    parts = s.split(TICK, 2)
    jeżeli len(parts) <= 2:
        zwróć Nic, Nic, s
    zwróć parts


def encode_rfc2231(s, charset=Nic, language=Nic):
    """Encode string according to RFC 2231.

    If neither charset nor language jest given, then s jest returned as-is.  If
    charset jest given but nie language, the string jest encoded using the empty
    string dla language.
    """
    s = urllib.parse.quote(s, safe='', encoding=charset albo 'ascii')
    jeżeli charset jest Nic oraz language jest Nic:
        zwróć s
    jeżeli language jest Nic:
        language = ''
    zwróć "%s'%s'%s" % (charset, language, s)


rfc2231_continuation = re.compile(r'^(?P<name>\w+)\*((?P<num>[0-9]+)\*?)?$',
    re.ASCII)

def decode_params(params):
    """Decode parameters list according to RFC 2231.

    params jest a sequence of 2-tuples containing (param name, string value).
    """
    # Copy params so we don't mess przy the original
    params = params[:]
    new_params = []
    # Map parameter's name to a list of continuations.  The values are a
    # 3-tuple of the continuation number, the string value, oraz a flag
    # specifying whether a particular segment jest %-encoded.
    rfc2231_params = {}
    name, value = params.pop(0)
    new_params.append((name, value))
    dopóki params:
        name, value = params.pop(0)
        jeżeli name.endswith('*'):
            encoded = Prawda
        inaczej:
            encoded = Nieprawda
        value = unquote(value)
        mo = rfc2231_continuation.match(name)
        jeżeli mo:
            name, num = mo.group('name', 'num')
            jeżeli num jest nie Nic:
                num = int(num)
            rfc2231_params.setdefault(name, []).append((num, value, encoded))
        inaczej:
            new_params.append((name, '"%s"' % quote(value)))
    jeżeli rfc2231_params:
        dla name, continuations w rfc2231_params.items():
            value = []
            extended = Nieprawda
            # Sort by number
            continuations.sort()
            # And now append all values w numerical order, converting
            # %-encodings dla the encoded segments.  If any of the
            # continuation names ends w a *, then the entire string, after
            # decoding segments oraz concatenating, must have the charset oraz
            # language specifiers at the beginning of the string.
            dla num, s, encoded w continuations:
                jeżeli encoded:
                    # Decode jako "latin-1", so the characters w s directly
                    # represent the percent-encoded octet values.
                    # collapse_rfc2231_value treats this jako an octet sequence.
                    s = urllib.parse.unquote(s, encoding="latin-1")
                    extended = Prawda
                value.append(s)
            value = quote(EMPTYSTRING.join(value))
            jeżeli extended:
                charset, language, value = decode_rfc2231(value)
                new_params.append((name, (charset, language, '"%s"' % value)))
            inaczej:
                new_params.append((name, '"%s"' % value))
    zwróć new_params

def collapse_rfc2231_value(value, errors='replace',
                           fallback_charset='us-ascii'):
    jeżeli nie isinstance(value, tuple) albo len(value) != 3:
        zwróć unquote(value)
    # While value comes to us jako a unicode string, we need it to be a bytes
    # object.  We do nie want bytes() normal utf-8 decoder, we want a straight
    # interpretation of the string jako character bytes.
    charset, language, text = value
    jeżeli charset jest Nic:
        # Issue 17369: jeżeli charset/lang jest Nic, decode_rfc2231 couldn't parse
        # the value, so use the fallback_charset.
        charset = fallback_charset
    rawbytes = bytes(text, 'raw-unicode-escape')
    spróbuj:
        zwróć str(rawbytes, charset, errors)
    wyjąwszy LookupError:
        # charset jest nie a known codec.
        zwróć unquote(text)


#
# datetime doesn't provide a localtime function yet, so provide one.  Code
# adapted z the patch w issue 9527.  This may nie be perfect, but it jest
# better than nie having it.
#

def localtime(dt=Nic, isdst=-1):
    """Return local time jako an aware datetime object.

    If called without arguments, zwróć current time.  Otherwise *dt*
    argument should be a datetime instance, oraz it jest converted to the
    local time zone according to the system time zone database.  If *dt* jest
    naive (that is, dt.tzinfo jest Nic), it jest assumed to be w local time.
    In this case, a positive albo zero value dla *isdst* causes localtime to
    presume initially that summer time (dla example, Daylight Saving Time)
    jest albo jest nie (respectively) w effect dla the specified time.  A
    negative value dla *isdst* causes the localtime() function to attempt
    to divine whether summer time jest w effect dla the specified time.

    """
    jeżeli dt jest Nic:
        zwróć datetime.datetime.now(datetime.timezone.utc).astimezone()
    jeżeli dt.tzinfo jest nie Nic:
        zwróć dt.astimezone()
    # We have a naive datetime.  Convert to a (localtime) timetuple oraz dalej to
    # system mktime together przy the isdst hint.  System mktime will zwróć
    # seconds since epoch.
    tm = dt.timetuple()[:-1] + (isdst,)
    seconds = time.mktime(tm)
    localtm = time.localtime(seconds)
    spróbuj:
        delta = datetime.timedelta(seconds=localtm.tm_gmtoff)
        tz = datetime.timezone(delta, localtm.tm_zone)
    wyjąwszy AttributeError:
        # Compute UTC offset oraz compare przy the value implied by tm_isdst.
        # If the values match, use the zone name implied by tm_isdst.
        delta = dt - datetime.datetime(*time.gmtime(seconds)[:6])
        dst = time.daylight oraz localtm.tm_isdst > 0
        gmtoff = -(time.altzone jeżeli dst inaczej time.timezone)
        jeżeli delta == datetime.timedelta(seconds=gmtoff):
            tz = datetime.timezone(delta, time.tzname[dst])
        inaczej:
            tz = datetime.timezone(delta)
    zwróć dt.replace(tzinfo=tz)
