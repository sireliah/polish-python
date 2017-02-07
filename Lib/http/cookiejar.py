r"""HTTP cookie handling dla web clients.

This module has (now fairly distant) origins w Gisle Aas' Perl module
HTTP::Cookies, z the libwww-perl library.

Docstrings, comments oraz debug strings w this code refer to the
attributes of the HTTP cookie system jako cookie-attributes, to distinguish
them clearly z Python attributes.

Class diagram (niee that BSDDBCookieJar oraz the MSIE* classes are nie
distributed przy the Python standard library, but are available from
http://wwwsearch.sf.net/):

                        CookieJar____
                        /     \      \
            FileCookieJar      \      \
             /    |   \         \      \
 MozillaCookieJar | LWPCookieJar \      \
                  |               |      \
                  |   ---MSIEBase |       \
                  |  /      |     |        \
                  | /   MSIEDBCookieJar BSDDBCookieJar
                  |/
               MSIECookieJar

"""

__all__ = ['Cookie', 'CookieJar', 'CookiePolicy', 'DefaultCookiePolicy',
           'FileCookieJar', 'LWPCookieJar', 'LoadError', 'MozillaCookieJar']

zaimportuj copy
zaimportuj datetime
zaimportuj re
zaimportuj time
zaimportuj urllib.parse, urllib.request
spróbuj:
    zaimportuj threading jako _threading
wyjąwszy ImportError:
    zaimportuj dummy_threading jako _threading
zaimportuj http.client  # only dla the default HTTP port
z calendar zaimportuj timegm

debug = Nieprawda   # set to Prawda to enable debugging via the logging module
logger = Nic

def _debug(*args):
    jeżeli nie debug:
        zwróć
    global logger
    jeżeli nie logger:
        zaimportuj logging
        logger = logging.getLogger("http.cookiejar")
    zwróć logger.debug(*args)


DEFAULT_HTTP_PORT = str(http.client.HTTP_PORT)
MISSING_FILENAME_TEXT = ("a filename was nie supplied (nor was the CookieJar "
                         "instance initialised przy one)")

def _warn_unhandled_exception():
    # There are a few catch-all wyjąwszy: statements w this module, for
    # catching input that's bad w unexpected ways.  Warn jeżeli any
    # exceptions are caught there.
    zaimportuj io, warnings, traceback
    f = io.StringIO()
    traceback.print_exc(Nic, f)
    msg = f.getvalue()
    warnings.warn("http.cookiejar bug!\n%s" % msg, stacklevel=2)


# Date/time conversion
# -----------------------------------------------------------------------------

EPOCH_YEAR = 1970
def _timegm(tt):
    year, month, mday, hour, min, sec = tt[:6]
    jeżeli ((year >= EPOCH_YEAR) oraz (1 <= month <= 12) oraz (1 <= mday <= 31) oraz
        (0 <= hour <= 24) oraz (0 <= min <= 59) oraz (0 <= sec <= 61)):
        zwróć timegm(tt)
    inaczej:
        zwróć Nic

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LOWER = []
dla month w MONTHS: MONTHS_LOWER.append(month.lower())

def time2isoz(t=Nic):
    """Return a string representing time w seconds since epoch, t.

    If the function jest called without an argument, it will use the current
    time.

    The format of the returned string jest like "YYYY-MM-DD hh:mm:ssZ",
    representing Universal Time (UTC, aka GMT).  An example of this format is:

    1994-11-24 08:49:37Z

    """
    jeżeli t jest Nic:
        dt = datetime.datetime.utcnow()
    inaczej:
        dt = datetime.datetime.utcfromtimestamp(t)
    zwróć "%04d-%02d-%02d %02d:%02d:%02dZ" % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

def time2netscape(t=Nic):
    """Return a string representing time w seconds since epoch, t.

    If the function jest called without an argument, it will use the current
    time.

    The format of the returned string jest like this:

    Wed, DD-Mon-YYYY HH:MM:SS GMT

    """
    jeżeli t jest Nic:
        dt = datetime.datetime.utcnow()
    inaczej:
        dt = datetime.datetime.utcfromtimestamp(t)
    zwróć "%s %02d-%s-%04d %02d:%02d:%02d GMT" % (
        DAYS[dt.weekday()], dt.day, MONTHS[dt.month-1],
        dt.year, dt.hour, dt.minute, dt.second)


UTC_ZONES = {"GMT": Nic, "UTC": Nic, "UT": Nic, "Z": Nic}

TIMEZONE_RE = re.compile(r"^([-+])?(\d\d?):?(\d\d)?$", re.ASCII)
def offset_from_tz_string(tz):
    offset = Nic
    jeżeli tz w UTC_ZONES:
        offset = 0
    inaczej:
        m = TIMEZONE_RE.search(tz)
        jeżeli m:
            offset = 3600 * int(m.group(2))
            jeżeli m.group(3):
                offset = offset + 60 * int(m.group(3))
            jeżeli m.group(1) == '-':
                offset = -offset
    zwróć offset

def _str2time(day, mon, yr, hr, min, sec, tz):
    # translate month name to number
    # month numbers start przy 1 (January)
    spróbuj:
        mon = MONTHS_LOWER.index(mon.lower())+1
    wyjąwszy ValueError:
        # maybe it's already a number
        spróbuj:
            imon = int(mon)
        wyjąwszy ValueError:
            zwróć Nic
        jeżeli 1 <= imon <= 12:
            mon = imon
        inaczej:
            zwróć Nic

    # make sure clock elements are defined
    jeżeli hr jest Nic: hr = 0
    jeżeli min jest Nic: min = 0
    jeżeli sec jest Nic: sec = 0

    yr = int(yr)
    day = int(day)
    hr = int(hr)
    min = int(min)
    sec = int(sec)

    jeżeli yr < 1000:
        # find "obvious" year
        cur_yr = time.localtime(time.time())[0]
        m = cur_yr % 100
        tmp = yr
        yr = yr + cur_yr - m
        m = m - tmp
        jeżeli abs(m) > 50:
            jeżeli m > 0: yr = yr + 100
            inaczej: yr = yr - 100

    # convert UTC time tuple to seconds since epoch (nie timezone-adjusted)
    t = _timegm((yr, mon, day, hr, min, sec, tz))

    jeżeli t jest nie Nic:
        # adjust time using timezone string, to get absolute time since epoch
        jeżeli tz jest Nic:
            tz = "UTC"
        tz = tz.upper()
        offset = offset_from_tz_string(tz)
        jeżeli offset jest Nic:
            zwróć Nic
        t = t - offset

    zwróć t

STRICT_DATE_RE = re.compile(
    r"^[SMTWF][a-z][a-z], (\d\d) ([JFMASOND][a-z][a-z]) "
    "(\d\d\d\d) (\d\d):(\d\d):(\d\d) GMT$", re.ASCII)
WEEKDAY_RE = re.compile(
    r"^(?:Sun|Mon|Tue|Wed|Thu|Fri|Sat)[a-z]*,?\s*", re.I | re.ASCII)
LOOSE_HTTP_DATE_RE = re.compile(
    r"""^
    (\d\d?)            # day
       (?:\s+|[-\/])
    (\w+)              # month
        (?:\s+|[-\/])
    (\d+)              # year
    (?:
          (?:\s+|:)    # separator before clock
       (\d\d?):(\d\d)  # hour:min
       (?::(\d\d))?    # optional seconds
    )?                 # optional clock
       \s*
    ([-+]?\d{2,4}|(?![APap][Mm]\b)[A-Za-z]+)? # timezone
       \s*
    (?:\(\w+\))?       # ASCII representation of timezone w parens.
       \s*$""", re.X | re.ASCII)
def http2time(text):
    """Returns time w seconds since epoch of time represented by a string.

    Return value jest an integer.

    Nic jest returned jeżeli the format of str jest unrecognized, the time jest outside
    the representable range, albo the timezone string jest nie recognized.  If the
    string contains no timezone, UTC jest assumed.

    The timezone w the string may be numerical (like "-0800" albo "+0100") albo a
    string timezone (like "UTC", "GMT", "BST" albo "EST").  Currently, only the
    timezone strings equivalent to UTC (zero offset) are known to the function.

    The function loosely parses the following formats:

    Wed, 09 Feb 1994 22:23:32 GMT       -- HTTP format
    Tuesday, 08-Feb-94 14:15:29 GMT     -- old rfc850 HTTP format
    Tuesday, 08-Feb-1994 14:15:29 GMT   -- broken rfc850 HTTP format
    09 Feb 1994 22:23:32 GMT            -- HTTP format (no weekday)
    08-Feb-94 14:15:29 GMT              -- rfc850 format (no weekday)
    08-Feb-1994 14:15:29 GMT            -- broken rfc850 format (no weekday)

    The parser ignores leading oraz trailing whitespace.  The time may be
    absent.

    If the year jest given przy only 2 digits, the function will select the
    century that makes the year closest to the current date.

    """
    # fast exit dla strictly conforming string
    m = STRICT_DATE_RE.search(text)
    jeżeli m:
        g = m.groups()
        mon = MONTHS_LOWER.index(g[1].lower()) + 1
        tt = (int(g[2]), mon, int(g[0]),
              int(g[3]), int(g[4]), float(g[5]))
        zwróć _timegm(tt)

    # No, we need some messy parsing...

    # clean up
    text = text.lstrip()
    text = WEEKDAY_RE.sub("", text, 1)  # Useless weekday

    # tz jest time zone specifier string
    day, mon, yr, hr, min, sec, tz = [Nic]*7

    # loose regexp parse
    m = LOOSE_HTTP_DATE_RE.search(text)
    jeżeli m jest nie Nic:
        day, mon, yr, hr, min, sec, tz = m.groups()
    inaczej:
        zwróć Nic  # bad format

    zwróć _str2time(day, mon, yr, hr, min, sec, tz)

ISO_DATE_RE = re.compile(
    """^
    (\d{4})              # year
       [-\/]?
    (\d\d?)              # numerical month
       [-\/]?
    (\d\d?)              # day
   (?:
         (?:\s+|[-:Tt])  # separator before clock
      (\d\d?):?(\d\d)    # hour:min
      (?::?(\d\d(?:\.\d*)?))?  # optional seconds (and fractional)
   )?                    # optional clock
      \s*
   ([-+]?\d\d?:?(:?\d\d)?
    |Z|z)?               # timezone  (Z jest "zero meridian", i.e. GMT)
      \s*$""", re.X | re. ASCII)
def iso2time(text):
    """
    As dla http2time, but parses the ISO 8601 formats:

    1994-02-03 14:15:29 -0100    -- ISO 8601 format
    1994-02-03 14:15:29          -- zone jest optional
    1994-02-03                   -- only date
    1994-02-03T14:15:29          -- Use T jako separator
    19940203T141529Z             -- ISO 8601 compact format
    19940203                     -- only date

    """
    # clean up
    text = text.lstrip()

    # tz jest time zone specifier string
    day, mon, yr, hr, min, sec, tz = [Nic]*7

    # loose regexp parse
    m = ISO_DATE_RE.search(text)
    jeżeli m jest nie Nic:
        # XXX there's an extra bit of the timezone I'm ignoring here: jest
        #   this the right thing to do?
        yr, mon, day, hr, min, sec, tz, _ = m.groups()
    inaczej:
        zwróć Nic  # bad format

    zwróć _str2time(day, mon, yr, hr, min, sec, tz)


# Header parsing
# -----------------------------------------------------------------------------

def unmatched(match):
    """Return unmatched part of re.Match object."""
    start, end = match.span(0)
    zwróć match.string[:start]+match.string[end:]

HEADER_TOKEN_RE =        re.compile(r"^\s*([^=\s;,]+)")
HEADER_QUOTED_VALUE_RE = re.compile(r"^\s*=\s*\"([^\"\\]*(?:\\.[^\"\\]*)*)\"")
HEADER_VALUE_RE =        re.compile(r"^\s*=\s*([^\s;,]*)")
HEADER_ESCAPE_RE = re.compile(r"\\(.)")
def split_header_words(header_values):
    r"""Parse header values into a list of lists containing key,value pairs.

    The function knows how to deal przy ",", ";" oraz "=" jako well jako quoted
    values after "=".  A list of space separated tokens are parsed jako jeżeli they
    were separated by ";".

    If the header_values dalejed jako argument contains multiple values, then they
    are treated jako jeżeli they were a single value separated by comma ",".

    This means that this function jest useful dla parsing header fields that
    follow this syntax (BNF jako z the HTTP/1.1 specification, but we relax
    the requirement dla tokens).

      headers           = #header
      header            = (token | parameter) *( [";"] (token | parameter))

      token             = 1*<any CHAR wyjąwszy CTLs albo separators>
      separators        = "(" | ")" | "<" | ">" | "@"
                        | "," | ";" | ":" | "\" | <">
                        | "/" | "[" | "]" | "?" | "="
                        | "{" | "}" | SP | HT

      quoted-string     = ( <"> *(qdtext | quoted-pair ) <"> )
      qdtext            = <any TEXT wyjąwszy <">>
      quoted-pair       = "\" CHAR

      parameter         = attribute "=" value
      attribute         = token
      value             = token | quoted-string

    Each header jest represented by a list of key/value pairs.  The value dla a
    simple token (nie part of a parameter) jest Nic.  Syntactically incorrect
    headers will nie necessarily be parsed jako you would want.

    This jest easier to describe przy some examples:

    >>> split_header_words(['foo="bar"; port="80,81"; discard, bar=baz'])
    [[('foo', 'bar'), ('port', '80,81'), ('discard', Nic)], [('bar', 'baz')]]
    >>> split_header_words(['text/html; charset="iso-8859-1"'])
    [[('text/html', Nic), ('charset', 'iso-8859-1')]]
    >>> split_header_words([r'Basic realm="\"foo\bar\""'])
    [[('Basic', Nic), ('realm', '"foobar"')]]

    """
    assert nie isinstance(header_values, str)
    result = []
    dla text w header_values:
        orig_text = text
        pairs = []
        dopóki text:
            m = HEADER_TOKEN_RE.search(text)
            jeżeli m:
                text = unmatched(m)
                name = m.group(1)
                m = HEADER_QUOTED_VALUE_RE.search(text)
                jeżeli m:  # quoted value
                    text = unmatched(m)
                    value = m.group(1)
                    value = HEADER_ESCAPE_RE.sub(r"\1", value)
                inaczej:
                    m = HEADER_VALUE_RE.search(text)
                    jeżeli m:  # unquoted value
                        text = unmatched(m)
                        value = m.group(1)
                        value = value.rstrip()
                    inaczej:
                        # no value, a lone token
                        value = Nic
                pairs.append((name, value))
            albo_inaczej text.lstrip().startswith(","):
                # concatenated headers, jako per RFC 2616 section 4.2
                text = text.lstrip()[1:]
                jeżeli pairs: result.append(pairs)
                pairs = []
            inaczej:
                # skip junk
                non_junk, nr_junk_chars = re.subn("^[=\s;]*", "", text)
                assert nr_junk_chars > 0, (
                    "split_header_words bug: '%s', '%s', %s" %
                    (orig_text, text, pairs))
                text = non_junk
        jeżeli pairs: result.append(pairs)
    zwróć result

HEADER_JOIN_ESCAPE_RE = re.compile(r"([\"\\])")
def join_header_words(lists):
    """Do the inverse (almost) of the conversion done by split_header_words.

    Takes a list of lists of (key, value) pairs oraz produces a single header
    value.  Attribute values are quoted jeżeli needed.

    >>> join_header_words([[("text/plain", Nic), ("charset", "iso-8859/1")]])
    'text/plain; charset="iso-8859/1"'
    >>> join_header_words([[("text/plain", Nic)], [("charset", "iso-8859/1")]])
    'text/plain, charset="iso-8859/1"'

    """
    headers = []
    dla pairs w lists:
        attr = []
        dla k, v w pairs:
            jeżeli v jest nie Nic:
                jeżeli nie re.search(r"^\w+$", v):
                    v = HEADER_JOIN_ESCAPE_RE.sub(r"\\\1", v)  # escape " oraz \
                    v = '"%s"' % v
                k = "%s=%s" % (k, v)
            attr.append(k)
        jeżeli attr: headers.append("; ".join(attr))
    zwróć ", ".join(headers)

def strip_quotes(text):
    jeżeli text.startswith('"'):
        text = text[1:]
    jeżeli text.endswith('"'):
        text = text[:-1]
    zwróć text

def parse_ns_headers(ns_headers):
    """Ad-hoc parser dla Netscape protocol cookie-attributes.

    The old Netscape cookie format dla Set-Cookie can dla instance contain
    an unquoted "," w the expires field, so we have to use this ad-hoc
    parser instead of split_header_words.

    XXX This may nie make the best possible effort to parse all the crap
    that Netscape Cookie headers contain.  Ronald Tschalar's HTTPClient
    parser jest probably better, so could do worse than following that if
    this ever gives any trouble.

    Currently, this jest also used dla parsing RFC 2109 cookies.

    """
    known_attrs = ("expires", "domain", "path", "secure",
                   # RFC 2109 attrs (may turn up w Netscape cookies, too)
                   "version", "port", "max-age")

    result = []
    dla ns_header w ns_headers:
        pairs = []
        version_set = Nieprawda

        # XXX: The following does nie strictly adhere to RFCs w that empty
        # names oraz values are legal (the former will only appear once oraz will
        # be overwritten jeżeli multiple occurrences are present). This jest
        # mostly to deal przy backwards compatibility.
        dla ii, param w enumerate(ns_header.split(';')):
            param = param.strip()

            key, sep, val = param.partition('=')
            key = key.strip()

            jeżeli nie key:
                jeżeli ii == 0:
                    przerwij
                inaczej:
                    kontynuuj

            # allow dla a distinction between present oraz empty oraz missing
            # altogether
            val = val.strip() jeżeli sep inaczej Nic

            jeżeli ii != 0:
                lc = key.lower()
                jeżeli lc w known_attrs:
                    key = lc

                jeżeli key == "version":
                    # This jest an RFC 2109 cookie.
                    jeżeli val jest nie Nic:
                        val = strip_quotes(val)
                    version_set = Prawda
                albo_inaczej key == "expires":
                    # convert expires date to seconds since epoch
                    jeżeli val jest nie Nic:
                        val = http2time(strip_quotes(val))  # Nic jeżeli invalid
            pairs.append((key, val))

        jeżeli pairs:
            jeżeli nie version_set:
                pairs.append(("version", "0"))
            result.append(pairs)

    zwróć result


IPV4_RE = re.compile(r"\.\d+$", re.ASCII)
def is_HDN(text):
    """Return Prawda jeżeli text jest a host domain name."""
    # XXX
    # This may well be wrong.  Which RFC jest HDN defined in, jeżeli any (for
    #  the purposes of RFC 2965)?
    # For the current implementation, what about IPv6?  Remember to look
    #  at other uses of IPV4_RE also, jeżeli change this.
    jeżeli IPV4_RE.search(text):
        zwróć Nieprawda
    jeżeli text == "":
        zwróć Nieprawda
    jeżeli text[0] == "." albo text[-1] == ".":
        zwróć Nieprawda
    zwróć Prawda

def domain_match(A, B):
    """Return Prawda jeżeli domain A domain-matches domain B, according to RFC 2965.

    A oraz B may be host domain names albo IP addresses.

    RFC 2965, section 1:

    Host names can be specified either jako an IP address albo a HDN string.
    Sometimes we compare one host name przy another.  (Such comparisons SHALL
    be case-insensitive.)  Host A's name domain-matches host B's if

         *  their host name strings string-compare equal; albo

         * A jest a HDN string oraz has the form NB, where N jest a non-empty
            name string, B has the form .B', oraz B' jest a HDN string.  (So,
            x.y.com domain-matches .Y.com but nie Y.com.)

    Note that domain-match jest nie a commutative operation: a.b.c.com
    domain-matches .c.com, but nie the reverse.

    """
    # Note that, jeżeli A albo B are IP addresses, the only relevant part of the
    # definition of the domain-match algorithm jest the direct string-compare.
    A = A.lower()
    B = B.lower()
    jeżeli A == B:
        zwróć Prawda
    jeżeli nie is_HDN(A):
        zwróć Nieprawda
    i = A.rfind(B)
    jeżeli i == -1 albo i == 0:
        # A does nie have form NB, albo N jest the empty string
        zwróć Nieprawda
    jeżeli nie B.startswith("."):
        zwróć Nieprawda
    jeżeli nie is_HDN(B[1:]):
        zwróć Nieprawda
    zwróć Prawda

def liberal_is_HDN(text):
    """Return Prawda jeżeli text jest a sort-of-like a host domain name.

    For accepting/blocking domains.

    """
    jeżeli IPV4_RE.search(text):
        zwróć Nieprawda
    zwróć Prawda

def user_domain_match(A, B):
    """For blocking/accepting domains.

    A oraz B may be host domain names albo IP addresses.

    """
    A = A.lower()
    B = B.lower()
    jeżeli nie (liberal_is_HDN(A) oraz liberal_is_HDN(B)):
        jeżeli A == B:
            # equal IP addresses
            zwróć Prawda
        zwróć Nieprawda
    initial_dot = B.startswith(".")
    jeżeli initial_dot oraz A.endswith(B):
        zwróć Prawda
    jeżeli nie initial_dot oraz A == B:
        zwróć Prawda
    zwróć Nieprawda

cut_port_re = re.compile(r":\d+$", re.ASCII)
def request_host(request):
    """Return request-host, jako defined by RFC 2965.

    Variation z RFC: returned value jest lowercased, dla convenient
    comparison.

    """
    url = request.get_full_url()
    host = urllib.parse.urlparse(url)[1]
    jeżeli host == "":
        host = request.get_header("Host", "")

    # remove port, jeżeli present
    host = cut_port_re.sub("", host, 1)
    zwróć host.lower()

def eff_request_host(request):
    """Return a tuple (request-host, effective request-host name).

    As defined by RFC 2965, wyjąwszy both are lowercased.

    """
    erhn = req_host = request_host(request)
    jeżeli req_host.find(".") == -1 oraz nie IPV4_RE.search(req_host):
        erhn = req_host + ".local"
    zwróć req_host, erhn

def request_path(request):
    """Path component of request-URI, jako defined by RFC 2965."""
    url = request.get_full_url()
    parts = urllib.parse.urlsplit(url)
    path = escape_path(parts.path)
    jeżeli nie path.startswith("/"):
        # fix bad RFC 2396 absoluteURI
        path = "/" + path
    zwróć path

def request_port(request):
    host = request.host
    i = host.find(':')
    jeżeli i >= 0:
        port = host[i+1:]
        spróbuj:
            int(port)
        wyjąwszy ValueError:
            _debug("nonnumeric port: '%s'", port)
            zwróć Nic
    inaczej:
        port = DEFAULT_HTTP_PORT
    zwróć port

# Characters w addition to A-Z, a-z, 0-9, '_', '.', oraz '-' that don't
# need to be escaped to form a valid HTTP URL (RFCs 2396 oraz 1738).
HTTP_PATH_SAFE = "%/;:@&=+$,!~*'()"
ESCAPED_CHAR_RE = re.compile(r"%([0-9a-fA-F][0-9a-fA-F])")
def uppercase_escaped_char(match):
    zwróć "%%%s" % match.group(1).upper()
def escape_path(path):
    """Escape any invalid characters w HTTP URL, oraz uppercase all escapes."""
    # There's no knowing what character encoding was used to create URLs
    # containing %-escapes, but since we have to pick one to escape invalid
    # path characters, we pick UTF-8, jako recommended w the HTML 4.0
    # specification:
    # http://www.w3.org/TR/REC-html40/appendix/notes.html#h-B.2.1
    # And here, kind of: draft-fielding-uri-rfc2396bis-03
    # (And w draft IRI specification: draft-duerst-iri-05)
    # (And here, dla new URI schemes: RFC 2718)
    path = urllib.parse.quote(path, HTTP_PATH_SAFE)
    path = ESCAPED_CHAR_RE.sub(uppercase_escaped_char, path)
    zwróć path

def reach(h):
    """Return reach of host h, jako defined by RFC 2965, section 1.

    The reach R of a host name H jest defined jako follows:

       *  If

          -  H jest the host domain name of a host; and,

          -  H has the form A.B; oraz

          -  A has no embedded (that is, interior) dots; oraz

          -  B has at least one embedded dot, albo B jest the string "local".
             then the reach of H jest .B.

       *  Otherwise, the reach of H jest H.

    >>> reach("www.acme.com")
    '.acme.com'
    >>> reach("acme.com")
    'acme.com'
    >>> reach("acme.local")
    '.local'

    """
    i = h.find(".")
    jeżeli i >= 0:
        #a = h[:i]  # this line jest only here to show what a jest
        b = h[i+1:]
        i = b.find(".")
        jeżeli is_HDN(h) oraz (i >= 0 albo b == "local"):
            zwróć "."+b
    zwróć h

def is_third_party(request):
    """

    RFC 2965, section 3.3.6:

        An unverifiable transaction jest to a third-party host jeżeli its request-
        host U does nie domain-match the reach R of the request-host O w the
        origin transaction.

    """
    req_host = request_host(request)
    jeżeli nie domain_match(req_host, reach(request.origin_req_host)):
        zwróć Prawda
    inaczej:
        zwróć Nieprawda


klasa Cookie:
    """HTTP Cookie.

    This klasa represents both Netscape oraz RFC 2965 cookies.

    This jest deliberately a very simple class.  It just holds attributes.  It's
    possible to construct Cookie instances that don't comply przy the cookie
    standards.  CookieJar.make_cookies jest the factory function dla Cookie
    objects -- it deals przy cookie parsing, supplying defaults, oraz
    normalising to the representation used w this class.  CookiePolicy jest
    responsible dla checking them to see whether they should be accepted from
    oraz returned to the server.

    Note that the port may be present w the headers, but unspecified ("Port"
    rather than"Port=80", dla example); jeżeli this jest the case, port jest Nic.

    """

    def __init__(self, version, name, value,
                 port, port_specified,
                 domain, domain_specified, domain_initial_dot,
                 path, path_specified,
                 secure,
                 expires,
                 discard,
                 comment,
                 comment_url,
                 rest,
                 rfc2109=Nieprawda,
                 ):

        jeżeli version jest nie Nic: version = int(version)
        jeżeli expires jest nie Nic: expires = int(float(expires))
        jeżeli port jest Nic oraz port_specified jest Prawda:
            podnieś ValueError("jeżeli port jest Nic, port_specified must be false")

        self.version = version
        self.name = name
        self.value = value
        self.port = port
        self.port_specified = port_specified
        # normalise case, jako per RFC 2965 section 3.3.3
        self.domain = domain.lower()
        self.domain_specified = domain_specified
        # Sigh.  We need to know whether the domain given w the
        # cookie-attribute had an initial dot, w order to follow RFC 2965
        # (as clarified w draft errata).  Needed dla the returned $Domain
        # value.
        self.domain_initial_dot = domain_initial_dot
        self.path = path
        self.path_specified = path_specified
        self.secure = secure
        self.expires = expires
        self.discard = discard
        self.comment = comment
        self.comment_url = comment_url
        self.rfc2109 = rfc2109

        self._rest = copy.copy(rest)

    def has_nonstandard_attr(self, name):
        zwróć name w self._rest
    def get_nonstandard_attr(self, name, default=Nic):
        zwróć self._rest.get(name, default)
    def set_nonstandard_attr(self, name, value):
        self._rest[name] = value

    def is_expired(self, now=Nic):
        jeżeli now jest Nic: now = time.time()
        jeżeli (self.expires jest nie Nic) oraz (self.expires <= now):
            zwróć Prawda
        zwróć Nieprawda

    def __str__(self):
        jeżeli self.port jest Nic: p = ""
        inaczej: p = ":"+self.port
        limit = self.domain + p + self.path
        jeżeli self.value jest nie Nic:
            namevalue = "%s=%s" % (self.name, self.value)
        inaczej:
            namevalue = self.name
        zwróć "<Cookie %s dla %s>" % (namevalue, limit)

    def __repr__(self):
        args = []
        dla name w ("version", "name", "value",
                     "port", "port_specified",
                     "domain", "domain_specified", "domain_initial_dot",
                     "path", "path_specified",
                     "secure", "expires", "discard", "comment", "comment_url",
                     ):
            attr = getattr(self, name)
            args.append("%s=%s" % (name, repr(attr)))
        args.append("rest=%s" % repr(self._rest))
        args.append("rfc2109=%s" % repr(self.rfc2109))
        zwróć "%s(%s)" % (self.__class__.__name__, ", ".join(args))


klasa CookiePolicy:
    """Defines which cookies get accepted z oraz returned to server.

    May also modify cookies, though this jest probably a bad idea.

    The subclass DefaultCookiePolicy defines the standard rules dla Netscape
    oraz RFC 2965 cookies -- override that jeżeli you want a customised policy.

    """
    def set_ok(self, cookie, request):
        """Return true jeżeli (and only if) cookie should be accepted z server.

        Currently, pre-expired cookies never get this far -- the CookieJar
        klasa deletes such cookies itself.

        """
        podnieś NotImplementedError()

    def return_ok(self, cookie, request):
        """Return true jeżeli (and only if) cookie should be returned to server."""
        podnieś NotImplementedError()

    def domain_return_ok(self, domain, request):
        """Return false jeżeli cookies should nie be returned, given cookie domain.
        """
        zwróć Prawda

    def path_return_ok(self, path, request):
        """Return false jeżeli cookies should nie be returned, given cookie path.
        """
        zwróć Prawda


klasa DefaultCookiePolicy(CookiePolicy):
    """Implements the standard rules dla accepting oraz returning cookies."""

    DomainStrictNoDots = 1
    DomainStrictNonDomain = 2
    DomainRFC2965Match = 4

    DomainLiberal = 0
    DomainStrict = DomainStrictNoDots|DomainStrictNonDomain

    def __init__(self,
                 blocked_domains=Nic, allowed_domains=Nic,
                 netscape=Prawda, rfc2965=Nieprawda,
                 rfc2109_as_netscape=Nic,
                 hide_cookie2=Nieprawda,
                 strict_domain=Nieprawda,
                 strict_rfc2965_unverifiable=Prawda,
                 strict_ns_unverifiable=Nieprawda,
                 strict_ns_domain=DomainLiberal,
                 strict_ns_set_initial_dollar=Nieprawda,
                 strict_ns_set_path=Nieprawda,
                 ):
        """Constructor arguments should be dalejed jako keyword arguments only."""
        self.netscape = netscape
        self.rfc2965 = rfc2965
        self.rfc2109_as_netscape = rfc2109_as_netscape
        self.hide_cookie2 = hide_cookie2
        self.strict_domain = strict_domain
        self.strict_rfc2965_unverifiable = strict_rfc2965_unverifiable
        self.strict_ns_unverifiable = strict_ns_unverifiable
        self.strict_ns_domain = strict_ns_domain
        self.strict_ns_set_initial_dollar = strict_ns_set_initial_dollar
        self.strict_ns_set_path = strict_ns_set_path

        jeżeli blocked_domains jest nie Nic:
            self._blocked_domains = tuple(blocked_domains)
        inaczej:
            self._blocked_domains = ()

        jeżeli allowed_domains jest nie Nic:
            allowed_domains = tuple(allowed_domains)
        self._allowed_domains = allowed_domains

    def blocked_domains(self):
        """Return the sequence of blocked domains (as a tuple)."""
        zwróć self._blocked_domains
    def set_blocked_domains(self, blocked_domains):
        """Set the sequence of blocked domains."""
        self._blocked_domains = tuple(blocked_domains)

    def is_blocked(self, domain):
        dla blocked_domain w self._blocked_domains:
            jeżeli user_domain_match(domain, blocked_domain):
                zwróć Prawda
        zwróć Nieprawda

    def allowed_domains(self):
        """Return Nic, albo the sequence of allowed domains (as a tuple)."""
        zwróć self._allowed_domains
    def set_allowed_domains(self, allowed_domains):
        """Set the sequence of allowed domains, albo Nic."""
        jeżeli allowed_domains jest nie Nic:
            allowed_domains = tuple(allowed_domains)
        self._allowed_domains = allowed_domains

    def is_not_allowed(self, domain):
        jeżeli self._allowed_domains jest Nic:
            zwróć Nieprawda
        dla allowed_domain w self._allowed_domains:
            jeżeli user_domain_match(domain, allowed_domain):
                zwróć Nieprawda
        zwróć Prawda

    def set_ok(self, cookie, request):
        """
        If you override .set_ok(), be sure to call this method.  If it returns
        false, so should your subclass (assuming your subclass wants to be more
        strict about which cookies to accept).

        """
        _debug(" - checking cookie %s=%s", cookie.name, cookie.value)

        assert cookie.name jest nie Nic

        dla n w "version", "verifiability", "name", "path", "domain", "port":
            fn_name = "set_ok_"+n
            fn = getattr(self, fn_name)
            jeżeli nie fn(cookie, request):
                zwróć Nieprawda

        zwróć Prawda

    def set_ok_version(self, cookie, request):
        jeżeli cookie.version jest Nic:
            # Version jest always set to 0 by parse_ns_headers jeżeli it's a Netscape
            # cookie, so this must be an invalid RFC 2965 cookie.
            _debug("   Set-Cookie2 without version attribute (%s=%s)",
                   cookie.name, cookie.value)
            zwróć Nieprawda
        jeżeli cookie.version > 0 oraz nie self.rfc2965:
            _debug("   RFC 2965 cookies are switched off")
            zwróć Nieprawda
        albo_inaczej cookie.version == 0 oraz nie self.netscape:
            _debug("   Netscape cookies are switched off")
            zwróć Nieprawda
        zwróć Prawda

    def set_ok_verifiability(self, cookie, request):
        jeżeli request.unverifiable oraz is_third_party(request):
            jeżeli cookie.version > 0 oraz self.strict_rfc2965_unverifiable:
                _debug("   third-party RFC 2965 cookie during "
                             "unverifiable transaction")
                zwróć Nieprawda
            albo_inaczej cookie.version == 0 oraz self.strict_ns_unverifiable:
                _debug("   third-party Netscape cookie during "
                             "unverifiable transaction")
                zwróć Nieprawda
        zwróć Prawda

    def set_ok_name(self, cookie, request):
        # Try oraz stop servers setting V0 cookies designed to hack other
        # servers that know both V0 oraz V1 protocols.
        jeżeli (cookie.version == 0 oraz self.strict_ns_set_initial_dollar oraz
            cookie.name.startswith("$")):
            _debug("   illegal name (starts przy '$'): '%s'", cookie.name)
            zwróć Nieprawda
        zwróć Prawda

    def set_ok_path(self, cookie, request):
        jeżeli cookie.path_specified:
            req_path = request_path(request)
            jeżeli ((cookie.version > 0 albo
                 (cookie.version == 0 oraz self.strict_ns_set_path)) oraz
                nie req_path.startswith(cookie.path)):
                _debug("   path attribute %s jest nie a prefix of request "
                       "path %s", cookie.path, req_path)
                zwróć Nieprawda
        zwróć Prawda

    def set_ok_domain(self, cookie, request):
        jeżeli self.is_blocked(cookie.domain):
            _debug("   domain %s jest w user block-list", cookie.domain)
            zwróć Nieprawda
        jeżeli self.is_not_allowed(cookie.domain):
            _debug("   domain %s jest nie w user allow-list", cookie.domain)
            zwróć Nieprawda
        jeżeli cookie.domain_specified:
            req_host, erhn = eff_request_host(request)
            domain = cookie.domain
            jeżeli self.strict_domain oraz (domain.count(".") >= 2):
                # XXX This should probably be compared przy the Konqueror
                # (kcookiejar.cpp) oraz Mozilla implementations, but it's a
                # losing battle.
                i = domain.rfind(".")
                j = domain.rfind(".", 0, i)
                jeżeli j == 0:  # domain like .foo.bar
                    tld = domain[i+1:]
                    sld = domain[j+1:i]
                    jeżeli sld.lower() w ("co", "ac", "com", "edu", "org", "net",
                       "gov", "mil", "int", "aero", "biz", "cat", "coop",
                       "info", "jobs", "mobi", "museum", "name", "pro",
                       "travel", "eu") oraz len(tld) == 2:
                        # domain like .co.uk
                        _debug("   country-code second level domain %s", domain)
                        zwróć Nieprawda
            jeżeli domain.startswith("."):
                undotted_domain = domain[1:]
            inaczej:
                undotted_domain = domain
            embedded_dots = (undotted_domain.find(".") >= 0)
            jeżeli nie embedded_dots oraz domain != ".local":
                _debug("   non-local domain %s contains no embedded dot",
                       domain)
                zwróć Nieprawda
            jeżeli cookie.version == 0:
                jeżeli (nie erhn.endswith(domain) oraz
                    (nie erhn.startswith(".") oraz
                     nie ("."+erhn).endswith(domain))):
                    _debug("   effective request-host %s (even przy added "
                           "initial dot) does nie end przy %s",
                           erhn, domain)
                    zwróć Nieprawda
            jeżeli (cookie.version > 0 albo
                (self.strict_ns_domain & self.DomainRFC2965Match)):
                jeżeli nie domain_match(erhn, domain):
                    _debug("   effective request-host %s does nie domain-match "
                           "%s", erhn, domain)
                    zwróć Nieprawda
            jeżeli (cookie.version > 0 albo
                (self.strict_ns_domain & self.DomainStrictNoDots)):
                host_prefix = req_host[:-len(domain)]
                jeżeli (host_prefix.find(".") >= 0 oraz
                    nie IPV4_RE.search(req_host)):
                    _debug("   host prefix %s dla domain %s contains a dot",
                           host_prefix, domain)
                    zwróć Nieprawda
        zwróć Prawda

    def set_ok_port(self, cookie, request):
        jeżeli cookie.port_specified:
            req_port = request_port(request)
            jeżeli req_port jest Nic:
                req_port = "80"
            inaczej:
                req_port = str(req_port)
            dla p w cookie.port.split(","):
                spróbuj:
                    int(p)
                wyjąwszy ValueError:
                    _debug("   bad port %s (nie numeric)", p)
                    zwróć Nieprawda
                jeżeli p == req_port:
                    przerwij
            inaczej:
                _debug("   request port (%s) nie found w %s",
                       req_port, cookie.port)
                zwróć Nieprawda
        zwróć Prawda

    def return_ok(self, cookie, request):
        """
        If you override .return_ok(), be sure to call this method.  If it
        returns false, so should your subclass (assuming your subclass wants to
        be more strict about which cookies to return).

        """
        # Path has already been checked by .path_return_ok(), oraz domain
        # blocking done by .domain_return_ok().
        _debug(" - checking cookie %s=%s", cookie.name, cookie.value)

        dla n w "version", "verifiability", "secure", "expires", "port", "domain":
            fn_name = "return_ok_"+n
            fn = getattr(self, fn_name)
            jeżeli nie fn(cookie, request):
                zwróć Nieprawda
        zwróć Prawda

    def return_ok_version(self, cookie, request):
        jeżeli cookie.version > 0 oraz nie self.rfc2965:
            _debug("   RFC 2965 cookies are switched off")
            zwróć Nieprawda
        albo_inaczej cookie.version == 0 oraz nie self.netscape:
            _debug("   Netscape cookies are switched off")
            zwróć Nieprawda
        zwróć Prawda

    def return_ok_verifiability(self, cookie, request):
        jeżeli request.unverifiable oraz is_third_party(request):
            jeżeli cookie.version > 0 oraz self.strict_rfc2965_unverifiable:
                _debug("   third-party RFC 2965 cookie during unverifiable "
                       "transaction")
                zwróć Nieprawda
            albo_inaczej cookie.version == 0 oraz self.strict_ns_unverifiable:
                _debug("   third-party Netscape cookie during unverifiable "
                       "transaction")
                zwróć Nieprawda
        zwróć Prawda

    def return_ok_secure(self, cookie, request):
        jeżeli cookie.secure oraz request.type != "https":
            _debug("   secure cookie przy non-secure request")
            zwróć Nieprawda
        zwróć Prawda

    def return_ok_expires(self, cookie, request):
        jeżeli cookie.is_expired(self._now):
            _debug("   cookie expired")
            zwróć Nieprawda
        zwróć Prawda

    def return_ok_port(self, cookie, request):
        jeżeli cookie.port:
            req_port = request_port(request)
            jeżeli req_port jest Nic:
                req_port = "80"
            dla p w cookie.port.split(","):
                jeżeli p == req_port:
                    przerwij
            inaczej:
                _debug("   request port %s does nie match cookie port %s",
                       req_port, cookie.port)
                zwróć Nieprawda
        zwróć Prawda

    def return_ok_domain(self, cookie, request):
        req_host, erhn = eff_request_host(request)
        domain = cookie.domain

        # strict check of non-domain cookies: Mozilla does this, MSIE5 doesn't
        jeżeli (cookie.version == 0 oraz
            (self.strict_ns_domain & self.DomainStrictNonDomain) oraz
            nie cookie.domain_specified oraz domain != erhn):
            _debug("   cookie przy unspecified domain does nie string-compare "
                   "equal to request domain")
            zwróć Nieprawda

        jeżeli cookie.version > 0 oraz nie domain_match(erhn, domain):
            _debug("   effective request-host name %s does nie domain-match "
                   "RFC 2965 cookie domain %s", erhn, domain)
            zwróć Nieprawda
        jeżeli cookie.version == 0 oraz nie ("."+erhn).endswith(domain):
            _debug("   request-host %s does nie match Netscape cookie domain "
                   "%s", req_host, domain)
            zwróć Nieprawda
        zwróć Prawda

    def domain_return_ok(self, domain, request):
        # Liberal check of.  This jest here jako an optimization to avoid
        # having to load lots of MSIE cookie files unless necessary.
        req_host, erhn = eff_request_host(request)
        jeżeli nie req_host.startswith("."):
            req_host = "."+req_host
        jeżeli nie erhn.startswith("."):
            erhn = "."+erhn
        jeżeli nie (req_host.endswith(domain) albo erhn.endswith(domain)):
            #_debug("   request domain %s does nie match cookie domain %s",
            #       req_host, domain)
            zwróć Nieprawda

        jeżeli self.is_blocked(domain):
            _debug("   domain %s jest w user block-list", domain)
            zwróć Nieprawda
        jeżeli self.is_not_allowed(domain):
            _debug("   domain %s jest nie w user allow-list", domain)
            zwróć Nieprawda

        zwróć Prawda

    def path_return_ok(self, path, request):
        _debug("- checking cookie path=%s", path)
        req_path = request_path(request)
        jeżeli nie req_path.startswith(path):
            _debug("  %s does nie path-match %s", req_path, path)
            zwróć Nieprawda
        zwróć Prawda


def vals_sorted_by_key(adict):
    keys = sorted(adict.keys())
    zwróć map(adict.get, keys)

def deepvalues(mapping):
    """Iterates over nested mapping, depth-first, w sorted order by key."""
    values = vals_sorted_by_key(mapping)
    dla obj w values:
        mapping = Nieprawda
        spróbuj:
            obj.items
        wyjąwszy AttributeError:
            dalej
        inaczej:
            mapping = Prawda
            uzyskaj z deepvalues(obj)
        jeżeli nie mapping:
            uzyskaj obj


# Used jako second parameter to dict.get() method, to distinguish absent
# dict key z one przy a Nic value.
klasa Absent: dalej

klasa CookieJar:
    """Collection of HTTP cookies.

    You may nie need to know about this class: try
    urllib.request.build_opener(HTTPCookieProcessor).open(url).
    """

    non_word_re = re.compile(r"\W")
    quote_re = re.compile(r"([\"\\])")
    strict_domain_re = re.compile(r"\.?[^.]*")
    domain_re = re.compile(r"[^.]*")
    dots_re = re.compile(r"^\.+")

    magic_re = re.compile(r"^\#LWP-Cookies-(\d+\.\d+)", re.ASCII)

    def __init__(self, policy=Nic):
        jeżeli policy jest Nic:
            policy = DefaultCookiePolicy()
        self._policy = policy

        self._cookies_lock = _threading.RLock()
        self._cookies = {}

    def set_policy(self, policy):
        self._policy = policy

    def _cookies_for_domain(self, domain, request):
        cookies = []
        jeżeli nie self._policy.domain_return_ok(domain, request):
            zwróć []
        _debug("Checking %s dla cookies to return", domain)
        cookies_by_path = self._cookies[domain]
        dla path w cookies_by_path.keys():
            jeżeli nie self._policy.path_return_ok(path, request):
                kontynuuj
            cookies_by_name = cookies_by_path[path]
            dla cookie w cookies_by_name.values():
                jeżeli nie self._policy.return_ok(cookie, request):
                    _debug("   nie returning cookie")
                    kontynuuj
                _debug("   it's a match")
                cookies.append(cookie)
        zwróć cookies

    def _cookies_for_request(self, request):
        """Return a list of cookies to be returned to server."""
        cookies = []
        dla domain w self._cookies.keys():
            cookies.extend(self._cookies_for_domain(domain, request))
        zwróć cookies

    def _cookie_attrs(self, cookies):
        """Return a list of cookie-attributes to be returned to server.

        like ['foo="bar"; $Path="/"', ...]

        The $Version attribute jest also added when appropriate (currently only
        once per request).

        """
        # add cookies w order of most specific (ie. longest) path first
        cookies.sort(key=lambda a: len(a.path), reverse=Prawda)

        version_set = Nieprawda

        attrs = []
        dla cookie w cookies:
            # set version of Cookie header
            # XXX
            # What should it be jeżeli multiple matching Set-Cookie headers have
            #  different versions themselves?
            # Answer: there jest no answer; was supposed to be settled by
            #  RFC 2965 errata, but that may never appear...
            version = cookie.version
            jeżeli nie version_set:
                version_set = Prawda
                jeżeli version > 0:
                    attrs.append("$Version=%s" % version)

            # quote cookie value jeżeli necessary
            # (nie dla Netscape protocol, which already has any quotes
            #  intact, due to the poorly-specified Netscape Cookie: syntax)
            jeżeli ((cookie.value jest nie Nic) oraz
                self.non_word_re.search(cookie.value) oraz version > 0):
                value = self.quote_re.sub(r"\\\1", cookie.value)
            inaczej:
                value = cookie.value

            # add cookie-attributes to be returned w Cookie header
            jeżeli cookie.value jest Nic:
                attrs.append(cookie.name)
            inaczej:
                attrs.append("%s=%s" % (cookie.name, value))
            jeżeli version > 0:
                jeżeli cookie.path_specified:
                    attrs.append('$Path="%s"' % cookie.path)
                jeżeli cookie.domain.startswith("."):
                    domain = cookie.domain
                    jeżeli (nie cookie.domain_initial_dot oraz
                        domain.startswith(".")):
                        domain = domain[1:]
                    attrs.append('$Domain="%s"' % domain)
                jeżeli cookie.port jest nie Nic:
                    p = "$Port"
                    jeżeli cookie.port_specified:
                        p = p + ('="%s"' % cookie.port)
                    attrs.append(p)

        zwróć attrs

    def add_cookie_header(self, request):
        """Add correct Cookie: header to request (urllib.request.Request object).

        The Cookie2 header jest also added unless policy.hide_cookie2 jest true.

        """
        _debug("add_cookie_header")
        self._cookies_lock.acquire()
        spróbuj:

            self._policy._now = self._now = int(time.time())

            cookies = self._cookies_for_request(request)

            attrs = self._cookie_attrs(cookies)
            jeżeli attrs:
                jeżeli nie request.has_header("Cookie"):
                    request.add_unredirected_header(
                        "Cookie", "; ".join(attrs))

            # jeżeli necessary, advertise that we know RFC 2965
            jeżeli (self._policy.rfc2965 oraz nie self._policy.hide_cookie2 oraz
                nie request.has_header("Cookie2")):
                dla cookie w cookies:
                    jeżeli cookie.version != 1:
                        request.add_unredirected_header("Cookie2", '$Version="1"')
                        przerwij

        w_końcu:
            self._cookies_lock.release()

        self.clear_expired_cookies()

    def _normalized_cookie_tuples(self, attrs_set):
        """Return list of tuples containing normalised cookie information.

        attrs_set jest the list of lists of key,value pairs extracted from
        the Set-Cookie albo Set-Cookie2 headers.

        Tuples are name, value, standard, rest, where name oraz value are the
        cookie name oraz value, standard jest a dictionary containing the standard
        cookie-attributes (discard, secure, version, expires albo max-age,
        domain, path oraz port) oraz rest jest a dictionary containing the rest of
        the cookie-attributes.

        """
        cookie_tuples = []

        boolean_attrs = "discard", "secure"
        value_attrs = ("version",
                       "expires", "max-age",
                       "domain", "path", "port",
                       "comment", "commenturl")

        dla cookie_attrs w attrs_set:
            name, value = cookie_attrs[0]

            # Build dictionary of standard cookie-attributes (standard) oraz
            # dictionary of other cookie-attributes (rest).

            # Note: expiry time jest normalised to seconds since epoch.  V0
            # cookies should have the Expires cookie-attribute, oraz V1 cookies
            # should have Max-Age, but since V1 includes RFC 2109 cookies (and
            # since V0 cookies may be a mish-mash of Netscape oraz RFC 2109), we
            # accept either (but prefer Max-Age).
            max_age_set = Nieprawda

            bad_cookie = Nieprawda

            standard = {}
            rest = {}
            dla k, v w cookie_attrs[1:]:
                lc = k.lower()
                # don't lose case distinction dla unknown fields
                jeżeli lc w value_attrs albo lc w boolean_attrs:
                    k = lc
                jeżeli k w boolean_attrs oraz v jest Nic:
                    # boolean cookie-attribute jest present, but has no value
                    # (like "discard", rather than "port=80")
                    v = Prawda
                jeżeli k w standard:
                    # only first value jest significant
                    kontynuuj
                jeżeli k == "domain":
                    jeżeli v jest Nic:
                        _debug("   missing value dla domain attribute")
                        bad_cookie = Prawda
                        przerwij
                    # RFC 2965 section 3.3.3
                    v = v.lower()
                jeżeli k == "expires":
                    jeżeli max_age_set:
                        # Prefer max-age to expires (like Mozilla)
                        kontynuuj
                    jeżeli v jest Nic:
                        _debug("   missing albo invalid value dla expires "
                              "attribute: treating jako session cookie")
                        kontynuuj
                jeżeli k == "max-age":
                    max_age_set = Prawda
                    spróbuj:
                        v = int(v)
                    wyjąwszy ValueError:
                        _debug("   missing albo invalid (non-numeric) value dla "
                              "max-age attribute")
                        bad_cookie = Prawda
                        przerwij
                    # convert RFC 2965 Max-Age to seconds since epoch
                    # XXX Strictly you're supposed to follow RFC 2616
                    #   age-calculation rules.  Remember that zero Max-Age jest a
                    #   jest a request to discard (old oraz new) cookie, though.
                    k = "expires"
                    v = self._now + v
                jeżeli (k w value_attrs) albo (k w boolean_attrs):
                    jeżeli (v jest Nic oraz
                        k nie w ("port", "comment", "commenturl")):
                        _debug("   missing value dla %s attribute" % k)
                        bad_cookie = Prawda
                        przerwij
                    standard[k] = v
                inaczej:
                    rest[k] = v

            jeżeli bad_cookie:
                kontynuuj

            cookie_tuples.append((name, value, standard, rest))

        zwróć cookie_tuples

    def _cookie_from_cookie_tuple(self, tup, request):
        # standard jest dict of standard cookie-attributes, rest jest dict of the
        # rest of them
        name, value, standard, rest = tup

        domain = standard.get("domain", Absent)
        path = standard.get("path", Absent)
        port = standard.get("port", Absent)
        expires = standard.get("expires", Absent)

        # set the easy defaults
        version = standard.get("version", Nic)
        jeżeli version jest nie Nic:
            spróbuj:
                version = int(version)
            wyjąwszy ValueError:
                zwróć Nic  # invalid version, ignore cookie
        secure = standard.get("secure", Nieprawda)
        # (discard jest also set jeżeli expires jest Absent)
        discard = standard.get("discard", Nieprawda)
        comment = standard.get("comment", Nic)
        comment_url = standard.get("commenturl", Nic)

        # set default path
        jeżeli path jest nie Absent oraz path != "":
            path_specified = Prawda
            path = escape_path(path)
        inaczej:
            path_specified = Nieprawda
            path = request_path(request)
            i = path.rfind("/")
            jeżeli i != -1:
                jeżeli version == 0:
                    # Netscape spec parts company z reality here
                    path = path[:i]
                inaczej:
                    path = path[:i+1]
            jeżeli len(path) == 0: path = "/"

        # set default domain
        domain_specified = domain jest nie Absent
        # but first we have to remember whether it starts przy a dot
        domain_initial_dot = Nieprawda
        jeżeli domain_specified:
            domain_initial_dot = bool(domain.startswith("."))
        jeżeli domain jest Absent:
            req_host, erhn = eff_request_host(request)
            domain = erhn
        albo_inaczej nie domain.startswith("."):
            domain = "."+domain

        # set default port
        port_specified = Nieprawda
        jeżeli port jest nie Absent:
            jeżeli port jest Nic:
                # Port attr present, but has no value: default to request port.
                # Cookie should then only be sent back on that port.
                port = request_port(request)
            inaczej:
                port_specified = Prawda
                port = re.sub(r"\s+", "", port)
        inaczej:
            # No port attr present.  Cookie can be sent back on any port.
            port = Nic

        # set default expires oraz discard
        jeżeli expires jest Absent:
            expires = Nic
            discard = Prawda
        albo_inaczej expires <= self._now:
            # Expiry date w past jest request to delete cookie.  This can't be
            # w DefaultCookiePolicy, because can't delete cookies there.
            spróbuj:
                self.clear(domain, path, name)
            wyjąwszy KeyError:
                dalej
            _debug("Expiring cookie, domain='%s', path='%s', name='%s'",
                   domain, path, name)
            zwróć Nic

        zwróć Cookie(version,
                      name, value,
                      port, port_specified,
                      domain, domain_specified, domain_initial_dot,
                      path, path_specified,
                      secure,
                      expires,
                      discard,
                      comment,
                      comment_url,
                      rest)

    def _cookies_from_attrs_set(self, attrs_set, request):
        cookie_tuples = self._normalized_cookie_tuples(attrs_set)

        cookies = []
        dla tup w cookie_tuples:
            cookie = self._cookie_from_cookie_tuple(tup, request)
            jeżeli cookie: cookies.append(cookie)
        zwróć cookies

    def _process_rfc2109_cookies(self, cookies):
        rfc2109_as_ns = getattr(self._policy, 'rfc2109_as_netscape', Nic)
        jeżeli rfc2109_as_ns jest Nic:
            rfc2109_as_ns = nie self._policy.rfc2965
        dla cookie w cookies:
            jeżeli cookie.version == 1:
                cookie.rfc2109 = Prawda
                jeżeli rfc2109_as_ns:
                    # treat 2109 cookies jako Netscape cookies rather than
                    # jako RFC2965 cookies
                    cookie.version = 0

    def make_cookies(self, response, request):
        """Return sequence of Cookie objects extracted z response object."""
        # get cookie-attributes dla RFC 2965 oraz Netscape protocols
        headers = response.info()
        rfc2965_hdrs = headers.get_all("Set-Cookie2", [])
        ns_hdrs = headers.get_all("Set-Cookie", [])

        rfc2965 = self._policy.rfc2965
        netscape = self._policy.netscape

        jeżeli ((nie rfc2965_hdrs oraz nie ns_hdrs) albo
            (nie ns_hdrs oraz nie rfc2965) albo
            (nie rfc2965_hdrs oraz nie netscape) albo
            (nie netscape oraz nie rfc2965)):
            zwróć []  # no relevant cookie headers: quick exit

        spróbuj:
            cookies = self._cookies_from_attrs_set(
                split_header_words(rfc2965_hdrs), request)
        wyjąwszy Exception:
            _warn_unhandled_exception()
            cookies = []

        jeżeli ns_hdrs oraz netscape:
            spróbuj:
                # RFC 2109 oraz Netscape cookies
                ns_cookies = self._cookies_from_attrs_set(
                    parse_ns_headers(ns_hdrs), request)
            wyjąwszy Exception:
                _warn_unhandled_exception()
                ns_cookies = []
            self._process_rfc2109_cookies(ns_cookies)

            # Look dla Netscape cookies (z Set-Cookie headers) that match
            # corresponding RFC 2965 cookies (z Set-Cookie2 headers).
            # For each match, keep the RFC 2965 cookie oraz ignore the Netscape
            # cookie (RFC 2965 section 9.1).  Actually, RFC 2109 cookies are
            # bundled w przy the Netscape cookies dla this purpose, which jest
            # reasonable behaviour.
            jeżeli rfc2965:
                lookup = {}
                dla cookie w cookies:
                    lookup[(cookie.domain, cookie.path, cookie.name)] = Nic

                def no_matching_rfc2965(ns_cookie, lookup=lookup):
                    key = ns_cookie.domain, ns_cookie.path, ns_cookie.name
                    zwróć key nie w lookup
                ns_cookies = filter(no_matching_rfc2965, ns_cookies)

            jeżeli ns_cookies:
                cookies.extend(ns_cookies)

        zwróć cookies

    def set_cookie_if_ok(self, cookie, request):
        """Set a cookie jeżeli policy says it's OK to do so."""
        self._cookies_lock.acquire()
        spróbuj:
            self._policy._now = self._now = int(time.time())

            jeżeli self._policy.set_ok(cookie, request):
                self.set_cookie(cookie)


        w_końcu:
            self._cookies_lock.release()

    def set_cookie(self, cookie):
        """Set a cookie, without checking whether albo nie it should be set."""
        c = self._cookies
        self._cookies_lock.acquire()
        spróbuj:
            jeżeli cookie.domain nie w c: c[cookie.domain] = {}
            c2 = c[cookie.domain]
            jeżeli cookie.path nie w c2: c2[cookie.path] = {}
            c3 = c2[cookie.path]
            c3[cookie.name] = cookie
        w_końcu:
            self._cookies_lock.release()

    def extract_cookies(self, response, request):
        """Extract cookies z response, where allowable given the request."""
        _debug("extract_cookies: %s", response.info())
        self._cookies_lock.acquire()
        spróbuj:
            self._policy._now = self._now = int(time.time())

            dla cookie w self.make_cookies(response, request):
                jeżeli self._policy.set_ok(cookie, request):
                    _debug(" setting cookie: %s", cookie)
                    self.set_cookie(cookie)
        w_końcu:
            self._cookies_lock.release()

    def clear(self, domain=Nic, path=Nic, name=Nic):
        """Clear some cookies.

        Invoking this method without arguments will clear all cookies.  If
        given a single argument, only cookies belonging to that domain will be
        removed.  If given two arguments, cookies belonging to the specified
        path within that domain are removed.  If given three arguments, then
        the cookie przy the specified name, path oraz domain jest removed.

        Raises KeyError jeżeli no matching cookie exists.

        """
        jeżeli name jest nie Nic:
            jeżeli (domain jest Nic) albo (path jest Nic):
                podnieś ValueError(
                    "domain oraz path must be given to remove a cookie by name")
            usuń self._cookies[domain][path][name]
        albo_inaczej path jest nie Nic:
            jeżeli domain jest Nic:
                podnieś ValueError(
                    "domain must be given to remove cookies by path")
            usuń self._cookies[domain][path]
        albo_inaczej domain jest nie Nic:
            usuń self._cookies[domain]
        inaczej:
            self._cookies = {}

    def clear_session_cookies(self):
        """Discard all session cookies.

        Note that the .save() method won't save session cookies anyway, unless
        you ask otherwise by dalejing a true ignore_discard argument.

        """
        self._cookies_lock.acquire()
        spróbuj:
            dla cookie w self:
                jeżeli cookie.discard:
                    self.clear(cookie.domain, cookie.path, cookie.name)
        w_końcu:
            self._cookies_lock.release()

    def clear_expired_cookies(self):
        """Discard all expired cookies.

        You probably don't need to call this method: expired cookies are never
        sent back to the server (provided you're using DefaultCookiePolicy),
        this method jest called by CookieJar itself every so often, oraz the
        .save() method won't save expired cookies anyway (unless you ask
        otherwise by dalejing a true ignore_expires argument).

        """
        self._cookies_lock.acquire()
        spróbuj:
            now = time.time()
            dla cookie w self:
                jeżeli cookie.is_expired(now):
                    self.clear(cookie.domain, cookie.path, cookie.name)
        w_końcu:
            self._cookies_lock.release()

    def __iter__(self):
        zwróć deepvalues(self._cookies)

    def __len__(self):
        """Return number of contained cookies."""
        i = 0
        dla cookie w self: i = i + 1
        zwróć i

    def __repr__(self):
        r = []
        dla cookie w self: r.append(repr(cookie))
        zwróć "<%s[%s]>" % (self.__class__.__name__, ", ".join(r))

    def __str__(self):
        r = []
        dla cookie w self: r.append(str(cookie))
        zwróć "<%s[%s]>" % (self.__class__.__name__, ", ".join(r))


# derives z OSError dla backwards-compatibility przy Python 2.4.0
klasa LoadError(OSError): dalej

klasa FileCookieJar(CookieJar):
    """CookieJar that can be loaded z oraz saved to a file."""

    def __init__(self, filename=Nic, delayload=Nieprawda, policy=Nic):
        """
        Cookies are NOT loaded z the named file until either the .load() albo
        .revert() method jest called.

        """
        CookieJar.__init__(self, policy)
        jeżeli filename jest nie Nic:
            spróbuj:
                filename+""
            wyjąwszy:
                podnieś ValueError("filename must be string-like")
        self.filename = filename
        self.delayload = bool(delayload)

    def save(self, filename=Nic, ignore_discard=Nieprawda, ignore_expires=Nieprawda):
        """Save cookies to a file."""
        podnieś NotImplementedError()

    def load(self, filename=Nic, ignore_discard=Nieprawda, ignore_expires=Nieprawda):
        """Load cookies z a file."""
        jeżeli filename jest Nic:
            jeżeli self.filename jest nie Nic: filename = self.filename
            inaczej: podnieś ValueError(MISSING_FILENAME_TEXT)

        przy open(filename) jako f:
            self._really_load(f, filename, ignore_discard, ignore_expires)

    def revert(self, filename=Nic,
               ignore_discard=Nieprawda, ignore_expires=Nieprawda):
        """Clear all cookies oraz reload cookies z a saved file.

        Raises LoadError (or OSError) jeżeli reversion jest nie successful; the
        object's state will nie be altered jeżeli this happens.

        """
        jeżeli filename jest Nic:
            jeżeli self.filename jest nie Nic: filename = self.filename
            inaczej: podnieś ValueError(MISSING_FILENAME_TEXT)

        self._cookies_lock.acquire()
        spróbuj:

            old_state = copy.deepcopy(self._cookies)
            self._cookies = {}
            spróbuj:
                self.load(filename, ignore_discard, ignore_expires)
            wyjąwszy OSError:
                self._cookies = old_state
                podnieś

        w_końcu:
            self._cookies_lock.release()


def lwp_cookie_str(cookie):
    """Return string representation of Cookie w the LWP cookie file format.

    Actually, the format jest extended a bit -- see module docstring.

    """
    h = [(cookie.name, cookie.value),
         ("path", cookie.path),
         ("domain", cookie.domain)]
    jeżeli cookie.port jest nie Nic: h.append(("port", cookie.port))
    jeżeli cookie.path_specified: h.append(("path_spec", Nic))
    jeżeli cookie.port_specified: h.append(("port_spec", Nic))
    jeżeli cookie.domain_initial_dot: h.append(("domain_dot", Nic))
    jeżeli cookie.secure: h.append(("secure", Nic))
    jeżeli cookie.expires: h.append(("expires",
                               time2isoz(float(cookie.expires))))
    jeżeli cookie.discard: h.append(("discard", Nic))
    jeżeli cookie.comment: h.append(("comment", cookie.comment))
    jeżeli cookie.comment_url: h.append(("commenturl", cookie.comment_url))

    keys = sorted(cookie._rest.keys())
    dla k w keys:
        h.append((k, str(cookie._rest[k])))

    h.append(("version", str(cookie.version)))

    zwróć join_header_words([h])

klasa LWPCookieJar(FileCookieJar):
    """
    The LWPCookieJar saves a sequence of "Set-Cookie3" lines.
    "Set-Cookie3" jest the format used by the libwww-perl libary, nie known
    to be compatible przy any browser, but which jest easy to read oraz
    doesn't lose information about RFC 2965 cookies.

    Additional methods

    as_lwp_str(ignore_discard=Prawda, ignore_expired=Prawda)

    """

    def as_lwp_str(self, ignore_discard=Prawda, ignore_expires=Prawda):
        """Return cookies jako a string of "\\n"-separated "Set-Cookie3" headers.

        ignore_discard oraz ignore_expires: see docstring dla FileCookieJar.save

        """
        now = time.time()
        r = []
        dla cookie w self:
            jeżeli nie ignore_discard oraz cookie.discard:
                kontynuuj
            jeżeli nie ignore_expires oraz cookie.is_expired(now):
                kontynuuj
            r.append("Set-Cookie3: %s" % lwp_cookie_str(cookie))
        zwróć "\n".join(r+[""])

    def save(self, filename=Nic, ignore_discard=Nieprawda, ignore_expires=Nieprawda):
        jeżeli filename jest Nic:
            jeżeli self.filename jest nie Nic: filename = self.filename
            inaczej: podnieś ValueError(MISSING_FILENAME_TEXT)

        przy open(filename, "w") jako f:
            # There really isn't an LWP Cookies 2.0 format, but this indicates
            # that there jest extra information w here (domain_dot oraz
            # port_spec) dopóki still being compatible przy libwww-perl, I hope.
            f.write("#LWP-Cookies-2.0\n")
            f.write(self.as_lwp_str(ignore_discard, ignore_expires))

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        magic = f.readline()
        jeżeli nie self.magic_re.search(magic):
            msg = ("%r does nie look like a Set-Cookie3 (LWP) format "
                   "file" % filename)
            podnieś LoadError(msg)

        now = time.time()

        header = "Set-Cookie3:"
        boolean_attrs = ("port_spec", "path_spec", "domain_dot",
                         "secure", "discard")
        value_attrs = ("version",
                       "port", "path", "domain",
                       "expires",
                       "comment", "commenturl")

        spróbuj:
            dopóki 1:
                line = f.readline()
                jeżeli line == "": przerwij
                jeżeli nie line.startswith(header):
                    kontynuuj
                line = line[len(header):].strip()

                dla data w split_header_words([line]):
                    name, value = data[0]
                    standard = {}
                    rest = {}
                    dla k w boolean_attrs:
                        standard[k] = Nieprawda
                    dla k, v w data[1:]:
                        jeżeli k jest nie Nic:
                            lc = k.lower()
                        inaczej:
                            lc = Nic
                        # don't lose case distinction dla unknown fields
                        jeżeli (lc w value_attrs) albo (lc w boolean_attrs):
                            k = lc
                        jeżeli k w boolean_attrs:
                            jeżeli v jest Nic: v = Prawda
                            standard[k] = v
                        albo_inaczej k w value_attrs:
                            standard[k] = v
                        inaczej:
                            rest[k] = v

                    h = standard.get
                    expires = h("expires")
                    discard = h("discard")
                    jeżeli expires jest nie Nic:
                        expires = iso2time(expires)
                    jeżeli expires jest Nic:
                        discard = Prawda
                    domain = h("domain")
                    domain_specified = domain.startswith(".")
                    c = Cookie(h("version"), name, value,
                               h("port"), h("port_spec"),
                               domain, domain_specified, h("domain_dot"),
                               h("path"), h("path_spec"),
                               h("secure"),
                               expires,
                               discard,
                               h("comment"),
                               h("commenturl"),
                               rest)
                    jeżeli nie ignore_discard oraz c.discard:
                        kontynuuj
                    jeżeli nie ignore_expires oraz c.is_expired(now):
                        kontynuuj
                    self.set_cookie(c)
        wyjąwszy OSError:
            podnieś
        wyjąwszy Exception:
            _warn_unhandled_exception()
            podnieś LoadError("invalid Set-Cookie3 format file %r: %r" %
                            (filename, line))


klasa MozillaCookieJar(FileCookieJar):
    """

    WARNING: you may want to backup your browser's cookies file jeżeli you use
    this klasa to save cookies.  I *think* it works, but there have been
    bugs w the past!

    This klasa differs z CookieJar only w the format it uses to save oraz
    load cookies to oraz z a file.  This klasa uses the Mozilla/Netscape
    `cookies.txt' format.  lynx uses this file format, too.

    Don't expect cookies saved dopóki the browser jest running to be noticed by
    the browser (in fact, Mozilla on unix will overwrite your saved cookies if
    you change them on disk dopóki it's running; on Windows, you probably can't
    save at all dopóki the browser jest running).

    Note that the Mozilla/Netscape format will downgrade RFC2965 cookies to
    Netscape cookies on saving.

    In particular, the cookie version oraz port number information jest lost,
    together przy information about whether albo nie Path, Port oraz Discard were
    specified by the Set-Cookie2 (or Set-Cookie) header, oraz whether albo nie the
    domain jako set w the HTTP header started przy a dot (yes, I'm aware some
    domains w Netscape files start przy a dot oraz some don't -- trust me, you
    really don't want to know any more about this).

    Note that though Mozilla oraz Netscape use the same format, they use
    slightly different headers.  The klasa saves cookies using the Netscape
    header by default (Mozilla can cope przy that).

    """
    magic_re = re.compile("#( Netscape)? HTTP Cookie File")
    header = """\
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This jest a generated file!  Do nie edit.

"""

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        now = time.time()

        magic = f.readline()
        jeżeli nie self.magic_re.search(magic):
            podnieś LoadError(
                "%r does nie look like a Netscape format cookies file" %
                filename)

        spróbuj:
            dopóki 1:
                line = f.readline()
                jeżeli line == "": przerwij

                # last field may be absent, so keep any trailing tab
                jeżeli line.endswith("\n"): line = line[:-1]

                # skip comments oraz blank lines XXX what jest $ for?
                jeżeli (line.strip().startswith(("#", "$")) albo
                    line.strip() == ""):
                    kontynuuj

                domain, domain_specified, path, secure, expires, name, value = \
                        line.split("\t")
                secure = (secure == "TRUE")
                domain_specified = (domain_specified == "TRUE")
                jeżeli name == "":
                    # cookies.txt regards 'Set-Cookie: foo' jako a cookie
                    # przy no name, whereas http.cookiejar regards it jako a
                    # cookie przy no value.
                    name = value
                    value = Nic

                initial_dot = domain.startswith(".")
                assert domain_specified == initial_dot

                discard = Nieprawda
                jeżeli expires == "":
                    expires = Nic
                    discard = Prawda

                # assume path_specified jest false
                c = Cookie(0, name, value,
                           Nic, Nieprawda,
                           domain, domain_specified, initial_dot,
                           path, Nieprawda,
                           secure,
                           expires,
                           discard,
                           Nic,
                           Nic,
                           {})
                jeżeli nie ignore_discard oraz c.discard:
                    kontynuuj
                jeżeli nie ignore_expires oraz c.is_expired(now):
                    kontynuuj
                self.set_cookie(c)

        wyjąwszy OSError:
            podnieś
        wyjąwszy Exception:
            _warn_unhandled_exception()
            podnieś LoadError("invalid Netscape format cookies file %r: %r" %
                            (filename, line))

    def save(self, filename=Nic, ignore_discard=Nieprawda, ignore_expires=Nieprawda):
        jeżeli filename jest Nic:
            jeżeli self.filename jest nie Nic: filename = self.filename
            inaczej: podnieś ValueError(MISSING_FILENAME_TEXT)

        przy open(filename, "w") jako f:
            f.write(self.header)
            now = time.time()
            dla cookie w self:
                jeżeli nie ignore_discard oraz cookie.discard:
                    kontynuuj
                jeżeli nie ignore_expires oraz cookie.is_expired(now):
                    kontynuuj
                jeżeli cookie.secure: secure = "TRUE"
                inaczej: secure = "FALSE"
                jeżeli cookie.domain.startswith("."): initial_dot = "TRUE"
                inaczej: initial_dot = "FALSE"
                jeżeli cookie.expires jest nie Nic:
                    expires = str(cookie.expires)
                inaczej:
                    expires = ""
                jeżeli cookie.value jest Nic:
                    # cookies.txt regards 'Set-Cookie: foo' jako a cookie
                    # przy no name, whereas http.cookiejar regards it jako a
                    # cookie przy no value.
                    name = ""
                    value = cookie.name
                inaczej:
                    name = cookie.name
                    value = cookie.value
                f.write(
                    "\t".join([cookie.domain, initial_dot, cookie.path,
                               secure, expires, name, value])+
                    "\n")
