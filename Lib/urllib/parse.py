"""Parse (absolute oraz relative) URLs.

urlparse module jest based upon the following RFC specifications.

RFC 3986 (STD66): "Uniform Resource Identifiers" by T. Berners-Lee, R. Fielding
and L.  Masinter, January 2005.

RFC 2732 : "Format dla Literal IPv6 Addresses w URL's by R.Hinden, B.Carpenter
and L.Masinter, December 1999.

RFC 2396:  "Uniform Resource Identifiers (URI)": Generic Syntax by T.
Berners-Lee, R. Fielding, oraz L. Masinter, August 1998.

RFC 2368: "The mailto URL scheme", by P.Hoffman , L Masinter, J. Zawinski, July 1998.

RFC 1808: "Relative Uniform Resource Locators", by R. Fielding, UC Irvine, June
1995.

RFC 1738: "Uniform Resource Locators (URL)" by T. Berners-Lee, L. Masinter, M.
McCahill, December 1994

RFC 3986 jest considered the current standard oraz any future changes to
urlparse module should conform przy it.  The urlparse module jest
currently nie entirely compliant przy this RFC due to defacto
scenarios dla parsing, oraz dla backward compatibility purposes, some
parsing quirks z older RFCs are retained. The testcases w
test_urlparse.py provides a good indicator of parsing behavior.
"""

zaimportuj re
zaimportuj sys
zaimportuj collections

__all__ = ["urlparse", "urlunparse", "urljoin", "urldefrag",
           "urlsplit", "urlunsplit", "urlencode", "parse_qs",
           "parse_qsl", "quote", "quote_plus", "quote_from_bytes",
           "unquote", "unquote_plus", "unquote_to_bytes",
           "DefragResult", "ParseResult", "SplitResult",
           "DefragResultBytes", "ParseResultBytes", "SplitResultBytes"]

# A classification of schemes ('' means apply by default)
uses_relative = ['ftp', 'http', 'gopher', 'nntp', 'imap',
                 'wais', 'file', 'https', 'shttp', 'mms',
                 'prospero', 'rtsp', 'rtspu', '', 'sftp',
                 'svn', 'svn+ssh']
uses_netloc = ['ftp', 'http', 'gopher', 'nntp', 'telnet',
               'imap', 'wais', 'file', 'mms', 'https', 'shttp',
               'snews', 'prospero', 'rtsp', 'rtspu', 'rsync', '',
               'svn', 'svn+ssh', 'sftp', 'nfs', 'git', 'git+ssh']
uses_params = ['ftp', 'hdl', 'prospero', 'http', 'imap',
               'https', 'shttp', 'rtsp', 'rtspu', 'sip', 'sips',
               'mms', '', 'sftp', 'tel']

# These are nie actually used anymore, but should stay dla backwards
# compatibility.  (They are undocumented, but have a public-looking name.)
non_hierarchical = ['gopher', 'hdl', 'mailto', 'news',
                    'telnet', 'wais', 'imap', 'snews', 'sip', 'sips']
uses_query = ['http', 'wais', 'imap', 'https', 'shttp', 'mms',
              'gopher', 'rtsp', 'rtspu', 'sip', 'sips', '']
uses_fragment = ['ftp', 'hdl', 'http', 'gopher', 'news',
                 'nntp', 'wais', 'https', 'shttp', 'snews',
                 'file', 'prospero', '']

# Characters valid w scheme names
scheme_chars = ('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '+-.')

# XXX: Consider replacing przy functools.lru_cache
MAX_CACHE_SIZE = 20
_parse_cache = {}

def clear_cache():
    """Clear the parse cache oraz the quoters cache."""
    _parse_cache.clear()
    _safe_quoters.clear()


# Helpers dla bytes handling
# For 3.2, we deliberately require applications that
# handle improperly quoted URLs to do their own
# decoding oraz encoding. If valid use cases are
# presented, we may relax this by using latin-1
# decoding internally dla 3.3
_implicit_encoding = 'ascii'
_implicit_errors = 'strict'

def _noop(obj):
    zwróć obj

def _encode_result(obj, encoding=_implicit_encoding,
                        errors=_implicit_errors):
    zwróć obj.encode(encoding, errors)

def _decode_args(args, encoding=_implicit_encoding,
                       errors=_implicit_errors):
    zwróć tuple(x.decode(encoding, errors) jeżeli x inaczej '' dla x w args)

def _coerce_args(*args):
    # Invokes decode jeżeli necessary to create str args
    # oraz returns the coerced inputs along with
    # an appropriate result coercion function
    #   - noop dla str inputs
    #   - encoding function otherwise
    str_input = isinstance(args[0], str)
    dla arg w args[1:]:
        # We special-case the empty string to support the
        # "scheme=''" default argument to some functions
        jeżeli arg oraz isinstance(arg, str) != str_input:
            podnieś TypeError("Cannot mix str oraz non-str arguments")
    jeżeli str_input:
        zwróć args + (_noop,)
    zwróć _decode_args(args) + (_encode_result,)

# Result objects are more helpful than simple tuples
klasa _ResultMixinStr(object):
    """Standard approach to encoding parsed results z str to bytes"""
    __slots__ = ()

    def encode(self, encoding='ascii', errors='strict'):
        zwróć self._encoded_counterpart(*(x.encode(encoding, errors) dla x w self))


klasa _ResultMixinBytes(object):
    """Standard approach to decoding parsed results z bytes to str"""
    __slots__ = ()

    def decode(self, encoding='ascii', errors='strict'):
        zwróć self._decoded_counterpart(*(x.decode(encoding, errors) dla x w self))


klasa _NetlocResultMixinBase(object):
    """Shared methods dla the parsed result objects containing a netloc element"""
    __slots__ = ()

    @property
    def username(self):
        zwróć self._userinfo[0]

    @property
    def dalejword(self):
        zwróć self._userinfo[1]

    @property
    def hostname(self):
        hostname = self._hostinfo[0]
        jeżeli nie hostname:
            hostname = Nic
        albo_inaczej hostname jest nie Nic:
            hostname = hostname.lower()
        zwróć hostname

    @property
    def port(self):
        port = self._hostinfo[1]
        jeżeli port jest nie Nic:
            port = int(port, 10)
            # Return Nic on an illegal port
            jeżeli nie ( 0 <= port <= 65535):
                zwróć Nic
        zwróć port


klasa _NetlocResultMixinStr(_NetlocResultMixinBase, _ResultMixinStr):
    __slots__ = ()

    @property
    def _userinfo(self):
        netloc = self.netloc
        userinfo, have_info, hostinfo = netloc.rpartition('@')
        jeżeli have_info:
            username, have_password, dalejword = userinfo.partition(':')
            jeżeli nie have_password:
                dalejword = Nic
        inaczej:
            username = dalejword = Nic
        zwróć username, dalejword

    @property
    def _hostinfo(self):
        netloc = self.netloc
        _, _, hostinfo = netloc.rpartition('@')
        _, have_open_br, bracketed = hostinfo.partition('[')
        jeżeli have_open_br:
            hostname, _, port = bracketed.partition(']')
            _, _, port = port.partition(':')
        inaczej:
            hostname, _, port = hostinfo.partition(':')
        jeżeli nie port:
            port = Nic
        zwróć hostname, port


klasa _NetlocResultMixinBytes(_NetlocResultMixinBase, _ResultMixinBytes):
    __slots__ = ()

    @property
    def _userinfo(self):
        netloc = self.netloc
        userinfo, have_info, hostinfo = netloc.rpartition(b'@')
        jeżeli have_info:
            username, have_password, dalejword = userinfo.partition(b':')
            jeżeli nie have_password:
                dalejword = Nic
        inaczej:
            username = dalejword = Nic
        zwróć username, dalejword

    @property
    def _hostinfo(self):
        netloc = self.netloc
        _, _, hostinfo = netloc.rpartition(b'@')
        _, have_open_br, bracketed = hostinfo.partition(b'[')
        jeżeli have_open_br:
            hostname, _, port = bracketed.partition(b']')
            _, _, port = port.partition(b':')
        inaczej:
            hostname, _, port = hostinfo.partition(b':')
        jeżeli nie port:
            port = Nic
        zwróć hostname, port


z collections zaimportuj namedtuple

_DefragResultBase = namedtuple('DefragResult', 'url fragment')
_SplitResultBase = namedtuple('SplitResult', 'scheme netloc path query fragment')
_ParseResultBase = namedtuple('ParseResult', 'scheme netloc path params query fragment')

# For backwards compatibility, alias _NetlocResultMixinStr
# ResultBase jest no longer part of the documented API, but it jest
# retained since deprecating it isn't worth the hassle
ResultBase = _NetlocResultMixinStr

# Structured result objects dla string data
klasa DefragResult(_DefragResultBase, _ResultMixinStr):
    __slots__ = ()
    def geturl(self):
        jeżeli self.fragment:
            zwróć self.url + '#' + self.fragment
        inaczej:
            zwróć self.url

klasa SplitResult(_SplitResultBase, _NetlocResultMixinStr):
    __slots__ = ()
    def geturl(self):
        zwróć urlunsplit(self)

klasa ParseResult(_ParseResultBase, _NetlocResultMixinStr):
    __slots__ = ()
    def geturl(self):
        zwróć urlunparse(self)

# Structured result objects dla bytes data
klasa DefragResultBytes(_DefragResultBase, _ResultMixinBytes):
    __slots__ = ()
    def geturl(self):
        jeżeli self.fragment:
            zwróć self.url + b'#' + self.fragment
        inaczej:
            zwróć self.url

klasa SplitResultBytes(_SplitResultBase, _NetlocResultMixinBytes):
    __slots__ = ()
    def geturl(self):
        zwróć urlunsplit(self)

klasa ParseResultBytes(_ParseResultBase, _NetlocResultMixinBytes):
    __slots__ = ()
    def geturl(self):
        zwróć urlunparse(self)

# Set up the encode/decode result pairs
def _fix_result_transcoding():
    _result_pairs = (
        (DefragResult, DefragResultBytes),
        (SplitResult, SplitResultBytes),
        (ParseResult, ParseResultBytes),
    )
    dla _decoded, _encoded w _result_pairs:
        _decoded._encoded_counterpart = _encoded
        _encoded._decoded_counterpart = _decoded

_fix_result_transcoding()
usuń _fix_result_transcoding

def urlparse(url, scheme='', allow_fragments=Prawda):
    """Parse a URL into 6 components:
    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    Return a 6-tuple: (scheme, netloc, path, params, query, fragment).
    Note that we don't przerwij the components up w smaller bits
    (e.g. netloc jest a single string) oraz we don't expand % escapes."""
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    splitresult = urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment = splitresult
    jeżeli scheme w uses_params oraz ';' w url:
        url, params = _splitparams(url)
    inaczej:
        params = ''
    result = ParseResult(scheme, netloc, url, params, query, fragment)
    zwróć _coerce_result(result)

def _splitparams(url):
    jeżeli '/'  w url:
        i = url.find(';', url.rfind('/'))
        jeżeli i < 0:
            zwróć url, ''
    inaczej:
        i = url.find(';')
    zwróć url[:i], url[i+1:]

def _splitnetloc(url, start=0):
    delim = len(url)   # position of end of domain part of url, default jest end
    dla c w '/?#':    # look dla delimiters; the order jest NOT important
        wdelim = url.find(c, start)        # find first of this delim
        jeżeli wdelim >= 0:                    # jeżeli found
            delim = min(delim, wdelim)     # use earliest delim position
    zwróć url[start:delim], url[delim:]   # zwróć (domain, rest)

def urlsplit(url, scheme='', allow_fragments=Prawda):
    """Parse a URL into 5 components:
    <scheme>://<netloc>/<path>?<query>#<fragment>
    Return a 5-tuple: (scheme, netloc, path, query, fragment).
    Note that we don't przerwij the components up w smaller bits
    (e.g. netloc jest a single string) oraz we don't expand % escapes."""
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    allow_fragments = bool(allow_fragments)
    key = url, scheme, allow_fragments, type(url), type(scheme)
    cached = _parse_cache.get(key, Nic)
    jeżeli cached:
        zwróć _coerce_result(cached)
    jeżeli len(_parse_cache) >= MAX_CACHE_SIZE: # avoid runaway growth
        clear_cache()
    netloc = query = fragment = ''
    i = url.find(':')
    jeżeli i > 0:
        jeżeli url[:i] == 'http': # optimize the common case
            scheme = url[:i].lower()
            url = url[i+1:]
            jeżeli url[:2] == '//':
                netloc, url = _splitnetloc(url, 2)
                jeżeli (('[' w netloc oraz ']' nie w netloc) albo
                        (']' w netloc oraz '[' nie w netloc)):
                    podnieś ValueError("Invalid IPv6 URL")
            jeżeli allow_fragments oraz '#' w url:
                url, fragment = url.split('#', 1)
            jeżeli '?' w url:
                url, query = url.split('?', 1)
            v = SplitResult(scheme, netloc, url, query, fragment)
            _parse_cache[key] = v
            zwróć _coerce_result(v)
        dla c w url[:i]:
            jeżeli c nie w scheme_chars:
                przerwij
        inaczej:
            # make sure "url" jest nie actually a port number (in which case
            # "scheme" jest really part of the path)
            rest = url[i+1:]
            jeżeli nie rest albo any(c nie w '0123456789' dla c w rest):
                # nie a port number
                scheme, url = url[:i].lower(), rest

    jeżeli url[:2] == '//':
        netloc, url = _splitnetloc(url, 2)
        jeżeli (('[' w netloc oraz ']' nie w netloc) albo
                (']' w netloc oraz '[' nie w netloc)):
            podnieś ValueError("Invalid IPv6 URL")
    jeżeli allow_fragments oraz '#' w url:
        url, fragment = url.split('#', 1)
    jeżeli '?' w url:
        url, query = url.split('?', 1)
    v = SplitResult(scheme, netloc, url, query, fragment)
    _parse_cache[key] = v
    zwróć _coerce_result(v)

def urlunparse(components):
    """Put a parsed URL back together again.  This may result w a
    slightly different, but equivalent URL, jeżeli the URL that was parsed
    originally had redundant delimiters, e.g. a ? przy an empty query
    (the draft states that these are equivalent)."""
    scheme, netloc, url, params, query, fragment, _coerce_result = (
                                                  _coerce_args(*components))
    jeżeli params:
        url = "%s;%s" % (url, params)
    zwróć _coerce_result(urlunsplit((scheme, netloc, url, query, fragment)))

def urlunsplit(components):
    """Combine the elements of a tuple jako returned by urlsplit() into a
    complete URL jako a string. The data argument can be any five-item iterable.
    This may result w a slightly different, but equivalent URL, jeżeli the URL that
    was parsed originally had unnecessary delimiters (dla example, a ? przy an
    empty query; the RFC states that these are equivalent)."""
    scheme, netloc, url, query, fragment, _coerce_result = (
                                          _coerce_args(*components))
    jeżeli netloc albo (scheme oraz scheme w uses_netloc oraz url[:2] != '//'):
        jeżeli url oraz url[:1] != '/': url = '/' + url
        url = '//' + (netloc albo '') + url
    jeżeli scheme:
        url = scheme + ':' + url
    jeżeli query:
        url = url + '?' + query
    jeżeli fragment:
        url = url + '#' + fragment
    zwróć _coerce_result(url)

def urljoin(base, url, allow_fragments=Prawda):
    """Join a base URL oraz a possibly relative URL to form an absolute
    interpretation of the latter."""
    jeżeli nie base:
        zwróć url
    jeżeli nie url:
        zwróć base

    base, url, _coerce_result = _coerce_args(base, url)
    bscheme, bnetloc, bpath, bparams, bquery, bfragment = \
            urlparse(base, '', allow_fragments)
    scheme, netloc, path, params, query, fragment = \
            urlparse(url, bscheme, allow_fragments)

    jeżeli scheme != bscheme albo scheme nie w uses_relative:
        zwróć _coerce_result(url)
    jeżeli scheme w uses_netloc:
        jeżeli netloc:
            zwróć _coerce_result(urlunparse((scheme, netloc, path,
                                              params, query, fragment)))
        netloc = bnetloc

    jeżeli nie path oraz nie params:
        path = bpath
        params = bparams
        jeżeli nie query:
            query = bquery
        zwróć _coerce_result(urlunparse((scheme, netloc, path,
                                          params, query, fragment)))

    base_parts = bpath.split('/')
    jeżeli base_parts[-1] != '':
        # the last item jest nie a directory, so will nie be taken into account
        # w resolving the relative path
        usuń base_parts[-1]

    # dla rfc3986, ignore all base path should the first character be root.
    jeżeli path[:1] == '/':
        segments = path.split('/')
    inaczej:
        segments = base_parts + path.split('/')
        # filter out elements that would cause redundant slashes on re-joining
        # the resolved_path
        segments[1:-1] = filter(Nic, segments[1:-1])

    resolved_path = []

    dla seg w segments:
        jeżeli seg == '..':
            spróbuj:
                resolved_path.pop()
            wyjąwszy IndexError:
                # ignore any .. segments that would otherwise cause an IndexError
                # when popped z resolved_path jeżeli resolving dla rfc3986
                dalej
        albo_inaczej seg == '.':
            kontynuuj
        inaczej:
            resolved_path.append(seg)

    jeżeli segments[-1] w ('.', '..'):
        # do some post-processing here. jeżeli the last segment was a relative dir,
        # then we need to append the trailing '/'
        resolved_path.append('')

    zwróć _coerce_result(urlunparse((scheme, netloc, '/'.join(
        resolved_path) albo '/', params, query, fragment)))


def urldefrag(url):
    """Removes any existing fragment z URL.

    Returns a tuple of the defragmented URL oraz the fragment.  If
    the URL contained no fragments, the second element jest the
    empty string.
    """
    url, _coerce_result = _coerce_args(url)
    jeżeli '#' w url:
        s, n, p, a, q, frag = urlparse(url)
        defrag = urlunparse((s, n, p, a, q, ''))
    inaczej:
        frag = ''
        defrag = url
    zwróć _coerce_result(DefragResult(defrag, frag))

_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = Nic

def unquote_to_bytes(string):
    """unquote_to_bytes('abc%20def') -> b'abc def'."""
    # Note: strings are encoded jako UTF-8. This jest only an issue jeżeli it contains
    # unescaped non-ASCII characters, which URIs should not.
    jeżeli nie string:
        # Is it a string-like object?
        string.split
        zwróć b''
    jeżeli isinstance(string, str):
        string = string.encode('utf-8')
    bits = string.split(b'%')
    jeżeli len(bits) == 1:
        zwróć string
    res = [bits[0]]
    append = res.append
    # Delay the initialization of the table to nie waste memory
    # jeżeli the function jest never called
    global _hextobyte
    jeżeli _hextobyte jest Nic:
        _hextobyte = {(a + b).encode(): bytes([int(a + b, 16)])
                      dla a w _hexdig dla b w _hexdig}
    dla item w bits[1:]:
        spróbuj:
            append(_hextobyte[item[:2]])
            append(item[2:])
        wyjąwszy KeyError:
            append(b'%')
            append(item)
    zwróć b''.join(res)

_asciire = re.compile('([\x00-\x7f]+)')

def unquote(string, encoding='utf-8', errors='replace'):
    """Replace %xx escapes by their single-character equivalent. The optional
    encoding oraz errors parameters specify how to decode percent-encoded
    sequences into Unicode characters, jako accepted by the bytes.decode()
    method.
    By default, percent-encoded sequences are decoded przy UTF-8, oraz invalid
    sequences are replaced by a placeholder character.

    unquote('abc%20def') -> 'abc def'.
    """
    jeżeli '%' nie w string:
        string.split
        zwróć string
    jeżeli encoding jest Nic:
        encoding = 'utf-8'
    jeżeli errors jest Nic:
        errors = 'replace'
    bits = _asciire.split(string)
    res = [bits[0]]
    append = res.append
    dla i w range(1, len(bits), 2):
        append(unquote_to_bytes(bits[i]).decode(encoding, errors))
        append(bits[i + 1])
    zwróć ''.join(res)

def parse_qs(qs, keep_blank_values=Nieprawda, strict_parsing=Nieprawda,
             encoding='utf-8', errors='replace'):
    """Parse a query given jako a string argument.

        Arguments:

        qs: percent-encoded query string to be parsed

        keep_blank_values: flag indicating whether blank values w
            percent-encoded queries should be treated jako blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored oraz treated jako jeżeli they were
            nie included.

        strict_parsing: flag indicating what to do przy parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors podnieś a ValueError exception.

        encoding oraz errors: specify how to decode percent-encoded sequences
            into Unicode characters, jako accepted by the bytes.decode() method.
    """
    parsed_result = {}
    pairs = parse_qsl(qs, keep_blank_values, strict_parsing,
                      encoding=encoding, errors=errors)
    dla name, value w pairs:
        jeżeli name w parsed_result:
            parsed_result[name].append(value)
        inaczej:
            parsed_result[name] = [value]
    zwróć parsed_result

def parse_qsl(qs, keep_blank_values=Nieprawda, strict_parsing=Nieprawda,
              encoding='utf-8', errors='replace'):
    """Parse a query given jako a string argument.

    Arguments:

    qs: percent-encoded query string to be parsed

    keep_blank_values: flag indicating whether blank values w
        percent-encoded queries should be treated jako blank strings.  A
        true value indicates that blanks should be retained jako blank
        strings.  The default false value indicates that blank values
        are to be ignored oraz treated jako jeżeli they were  nie included.

    strict_parsing: flag indicating what to do przy parsing errors. If
        false (the default), errors are silently ignored. If true,
        errors podnieś a ValueError exception.

    encoding oraz errors: specify how to decode percent-encoded sequences
        into Unicode characters, jako accepted by the bytes.decode() method.

    Returns a list, jako G-d intended.
    """
    qs, _coerce_result = _coerce_args(qs)
    pairs = [s2 dla s1 w qs.split('&') dla s2 w s1.split(';')]
    r = []
    dla name_value w pairs:
        jeżeli nie name_value oraz nie strict_parsing:
            kontynuuj
        nv = name_value.split('=', 1)
        jeżeli len(nv) != 2:
            jeżeli strict_parsing:
                podnieś ValueError("bad query field: %r" % (name_value,))
            # Handle case of a control-name przy no equal sign
            jeżeli keep_blank_values:
                nv.append('')
            inaczej:
                kontynuuj
        jeżeli len(nv[1]) albo keep_blank_values:
            name = nv[0].replace('+', ' ')
            name = unquote(name, encoding=encoding, errors=errors)
            name = _coerce_result(name)
            value = nv[1].replace('+', ' ')
            value = unquote(value, encoding=encoding, errors=errors)
            value = _coerce_result(value)
            r.append((name, value))
    zwróć r

def unquote_plus(string, encoding='utf-8', errors='replace'):
    """Like unquote(), but also replace plus signs by spaces, jako required for
    unquoting HTML form values.

    unquote_plus('%7e/abc+def') -> '~/abc def'
    """
    string = string.replace('+', ' ')
    zwróć unquote(string, encoding, errors)

_ALWAYS_SAFE = frozenset(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                         b'abcdefghijklmnopqrstuvwxyz'
                         b'0123456789'
                         b'_.-')
_ALWAYS_SAFE_BYTES = bytes(_ALWAYS_SAFE)
_safe_quoters = {}

klasa Quoter(collections.defaultdict):
    """A mapping z bytes (in range(0,256)) to strings.

    String values are percent-encoded byte values, unless the key < 128, oraz
    w the "safe" set (either the specified safe set, albo default set).
    """
    # Keeps a cache internally, using defaultdict, dla efficiency (lookups
    # of cached keys don't call Python code at all).
    def __init__(self, safe):
        """safe: bytes object."""
        self.safe = _ALWAYS_SAFE.union(safe)

    def __repr__(self):
        # Without this, will just display jako a defaultdict
        zwróć "<%s %r>" % (self.__class__.__name__, dict(self))

    def __missing__(self, b):
        # Handle a cache miss. Store quoted string w cache oraz return.
        res = chr(b) jeżeli b w self.safe inaczej '%{:02X}'.format(b)
        self[b] = res
        zwróć res

def quote(string, safe='/', encoding=Nic, errors=Nic):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted.

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters.

    reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                  "$" | ","

    Each of these characters jest reserved w some component of a URL,
    but nie necessarily w all of them.

    By default, the quote function jest intended dla quoting the path
    section of a URL.  Thus, it will nie encode '/'.  This character
    jest reserved, but w typical usage the quote function jest being
    called on a path where the existing slash characters are used as
    reserved characters.

    string oraz safe may be either str albo bytes objects. encoding oraz errors
    must nie be specified jeżeli string jest a bytes object.

    The optional encoding oraz errors parameters specify how to deal with
    non-ASCII characters, jako accepted by the str.encode method.
    By default, encoding='utf-8' (characters are encoded przy UTF-8), oraz
    errors='strict' (unsupported characters podnieś a UnicodeEncodeError).
    """
    jeżeli isinstance(string, str):
        jeżeli nie string:
            zwróć string
        jeżeli encoding jest Nic:
            encoding = 'utf-8'
        jeżeli errors jest Nic:
            errors = 'strict'
        string = string.encode(encoding, errors)
    inaczej:
        jeżeli encoding jest nie Nic:
            podnieś TypeError("quote() doesn't support 'encoding' dla bytes")
        jeżeli errors jest nie Nic:
            podnieś TypeError("quote() doesn't support 'errors' dla bytes")
    zwróć quote_from_bytes(string, safe)

def quote_plus(string, safe='', encoding=Nic, errors=Nic):
    """Like quote(), but also replace ' ' przy '+', jako required dla quoting
    HTML form values. Plus signs w the original string are escaped unless
    they are included w safe. It also does nie have safe default to '/'.
    """
    # Check jeżeli ' ' w string, where string may either be a str albo bytes.  If
    # there are no spaces, the regular quote will produce the right answer.
    jeżeli ((isinstance(string, str) oraz ' ' nie w string) albo
        (isinstance(string, bytes) oraz b' ' nie w string)):
        zwróć quote(string, safe, encoding, errors)
    jeżeli isinstance(safe, str):
        space = ' '
    inaczej:
        space = b' '
    string = quote(string, safe + space, encoding, errors)
    zwróć string.replace(' ', '+')

def quote_from_bytes(bs, safe='/'):
    """Like quote(), but accepts a bytes object rather than a str, oraz does
    nie perform string-to-bytes encoding.  It always returns an ASCII string.
    quote_from_bytes(b'abc def\x3f') -> 'abc%20def%3f'
    """
    jeżeli nie isinstance(bs, (bytes, bytearray)):
        podnieś TypeError("quote_from_bytes() expected bytes")
    jeżeli nie bs:
        zwróć ''
    jeżeli isinstance(safe, str):
        # Normalize 'safe' by converting to bytes oraz removing non-ASCII chars
        safe = safe.encode('ascii', 'ignore')
    inaczej:
        safe = bytes([c dla c w safe jeżeli c < 128])
    jeżeli nie bs.rstrip(_ALWAYS_SAFE_BYTES + safe):
        zwróć bs.decode()
    spróbuj:
        quoter = _safe_quoters[safe]
    wyjąwszy KeyError:
        _safe_quoters[safe] = quoter = Quoter(safe).__getitem__
    zwróć ''.join([quoter(char) dla char w bs])

def urlencode(query, doseq=Nieprawda, safe='', encoding=Nic, errors=Nic,
              quote_via=quote_plus):
    """Encode a dict albo sequence of two-element tuples into a URL query string.

    If any values w the query arg are sequences oraz doseq jest true, each
    sequence element jest converted to a separate parameter.

    If the query arg jest a sequence of two-element tuples, the order of the
    parameters w the output will match the order of parameters w the
    input.

    The components of a query arg may each be either a string albo a bytes type.

    The safe, encoding, oraz errors parameters are dalejed down to the function
    specified by quote_via (encoding oraz errors only jeżeli a component jest a str).
    """

    jeżeli hasattr(query, "items"):
        query = query.items()
    inaczej:
        # It's a bother at times that strings oraz string-like objects are
        # sequences.
        spróbuj:
            # non-sequence items should nie work przy len()
            # non-empty strings will fail this
            jeżeli len(query) oraz nie isinstance(query[0], tuple):
                podnieś TypeError
            # Zero-length sequences of all types will get here oraz succeed,
            # but that's a minor nit.  Since the original implementation
            # allowed empty dicts that type of behavior probably should be
            # preserved dla consistency
        wyjąwszy TypeError:
            ty, va, tb = sys.exc_info()
            podnieś TypeError("not a valid non-string sequence "
                            "or mapping object").with_traceback(tb)

    l = []
    jeżeli nie doseq:
        dla k, v w query:
            jeżeli isinstance(k, bytes):
                k = quote_via(k, safe)
            inaczej:
                k = quote_via(str(k), safe, encoding, errors)

            jeżeli isinstance(v, bytes):
                v = quote_via(v, safe)
            inaczej:
                v = quote_via(str(v), safe, encoding, errors)
            l.append(k + '=' + v)
    inaczej:
        dla k, v w query:
            jeżeli isinstance(k, bytes):
                k = quote_via(k, safe)
            inaczej:
                k = quote_via(str(k), safe, encoding, errors)

            jeżeli isinstance(v, bytes):
                v = quote_via(v, safe)
                l.append(k + '=' + v)
            albo_inaczej isinstance(v, str):
                v = quote_via(v, safe, encoding, errors)
                l.append(k + '=' + v)
            inaczej:
                spróbuj:
                    # Is this a sufficient test dla sequence-ness?
                    x = len(v)
                wyjąwszy TypeError:
                    # nie a sequence
                    v = quote_via(str(v), safe, encoding, errors)
                    l.append(k + '=' + v)
                inaczej:
                    # loop over the sequence
                    dla elt w v:
                        jeżeli isinstance(elt, bytes):
                            elt = quote_via(elt, safe)
                        inaczej:
                            elt = quote_via(str(elt), safe, encoding, errors)
                        l.append(k + '=' + elt)
    zwróć '&'.join(l)

# Utilities to parse URLs (most of these zwróć Nic dla missing parts):
# unwrap('<URL:type://host/path>') --> 'type://host/path'
# splittype('type:opaquestring') --> 'type', 'opaquestring'
# splithost('//host[:port]/path') --> 'host[:port]', '/path'
# splituser('user[:passwd]@host[:port]') --> 'user[:passwd]', 'host[:port]'
# splitpasswd('user:passwd') -> 'user', 'passwd'
# splitport('host:port') --> 'host', 'port'
# splitquery('/path?query') --> '/path', 'query'
# splittag('/path#tag') --> '/path', 'tag'
# splitattr('/path;attr1=value1;attr2=value2;...') ->
#   '/path', ['attr1=value1', 'attr2=value2', ...]
# splitvalue('attr=value') --> 'attr', 'value'
# urllib.parse.unquote('abc%20def') -> 'abc def'
# quote('abc def') -> 'abc%20def')

def to_bytes(url):
    """to_bytes(u"URL") --> 'URL'."""
    # Most URL schemes require ASCII. If that changes, the conversion
    # can be relaxed.
    # XXX get rid of to_bytes()
    jeżeli isinstance(url, str):
        spróbuj:
            url = url.encode("ASCII").decode()
        wyjąwszy UnicodeError:
            podnieś UnicodeError("URL " + repr(url) +
                               " contains non-ASCII characters")
    zwróć url

def unwrap(url):
    """unwrap('<URL:type://host/path>') --> 'type://host/path'."""
    url = str(url).strip()
    jeżeli url[:1] == '<' oraz url[-1:] == '>':
        url = url[1:-1].strip()
    jeżeli url[:4] == 'URL:': url = url[4:].strip()
    zwróć url

_typeprog = Nic
def splittype(url):
    """splittype('type:opaquestring') --> 'type', 'opaquestring'."""
    global _typeprog
    jeżeli _typeprog jest Nic:
        _typeprog = re.compile('([^/:]+):(.*)', re.DOTALL)

    match = _typeprog.match(url)
    jeżeli match:
        scheme, data = match.groups()
        zwróć scheme.lower(), data
    zwróć Nic, url

_hostprog = Nic
def splithost(url):
    """splithost('//host[:port]/path') --> 'host[:port]', '/path'."""
    global _hostprog
    jeżeli _hostprog jest Nic:
        _hostprog = re.compile('//([^/?]*)(.*)', re.DOTALL)

    match = _hostprog.match(url)
    jeżeli match:
        host_port, path = match.groups()
        jeżeli path oraz path[0] != '/':
            path = '/' + path
        zwróć host_port, path
    zwróć Nic, url

def splituser(host):
    """splituser('user[:passwd]@host[:port]') --> 'user[:passwd]', 'host[:port]'."""
    user, delim, host = host.rpartition('@')
    zwróć (user jeżeli delim inaczej Nic), host

def splitpasswd(user):
    """splitpasswd('user:passwd') -> 'user', 'passwd'."""
    user, delim, dalejwd = user.partition(':')
    zwróć user, (passwd jeżeli delim inaczej Nic)

# splittag('/path#tag') --> '/path', 'tag'
_portprog = Nic
def splitport(host):
    """splitport('host:port') --> 'host', 'port'."""
    global _portprog
    jeżeli _portprog jest Nic:
        _portprog = re.compile('(.*):([0-9]*)$', re.DOTALL)

    match = _portprog.match(host)
    jeżeli match:
        host, port = match.groups()
        jeżeli port:
            zwróć host, port
    zwróć host, Nic

def splitnport(host, defport=-1):
    """Split host oraz port, returning numeric port.
    Return given default port jeżeli no ':' found; defaults to -1.
    Return numerical port jeżeli a valid number are found after ':'.
    Return Nic jeżeli ':' but nie a valid number."""
    host, delim, port = host.rpartition(':')
    jeżeli nie delim:
        host = port
    albo_inaczej port:
        spróbuj:
            nport = int(port)
        wyjąwszy ValueError:
            nport = Nic
        zwróć host, nport
    zwróć host, defport

def splitquery(url):
    """splitquery('/path?query') --> '/path', 'query'."""
    path, delim, query = url.rpartition('?')
    jeżeli delim:
        zwróć path, query
    zwróć url, Nic

def splittag(url):
    """splittag('/path#tag') --> '/path', 'tag'."""
    path, delim, tag = url.rpartition('#')
    jeżeli delim:
        zwróć path, tag
    zwróć url, Nic

def splitattr(url):
    """splitattr('/path;attr1=value1;attr2=value2;...') ->
        '/path', ['attr1=value1', 'attr2=value2', ...]."""
    words = url.split(';')
    zwróć words[0], words[1:]

def splitvalue(attr):
    """splitvalue('attr=value') --> 'attr', 'value'."""
    attr, delim, value = attr.partition('=')
    zwróć attr, (value jeżeli delim inaczej Nic)
