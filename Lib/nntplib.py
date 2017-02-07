"""An NNTP client klasa based on:
- RFC 977: Network News Transfer Protocol
- RFC 2980: Common NNTP Extensions
- RFC 3977: Network News Transfer Protocol (version 2)

Example:

>>> z nntplib zaimportuj NNTP
>>> s = NNTP('news')
>>> resp, count, first, last, name = s.group('comp.lang.python')
>>> print('Group', name, 'has', count, 'articles, range', first, 'to', last)
Group comp.lang.python has 51 articles, range 5770 to 5821
>>> resp, subs = s.xhdr('subject', '{0}-{1}'.format(first, last))
>>> resp = s.quit()
>>>

Here 'resp' jest the server response line.
Error responses are turned into exceptions.

To post an article z a file:
>>> f = open(filename, 'rb') # file containing article, including header
>>> resp = s.post(f)
>>>

For descriptions of all methods, read the comments w the code below.
Note that all arguments oraz zwróć values representing article numbers
are strings, nie numbers, since they are rarely used dla calculations.
"""

# RFC 977 by Brian Kantor oraz Phil Lapsley.
# xover, xgtitle, xpath, date methods by Kevan Heydon

# Incompatible changes z the 2.x nntplib:
# - all commands are encoded jako UTF-8 data (using the "surrogateescape"
#   error handler), wyjąwszy dla raw message data (POST, IHAVE)
# - all responses are decoded jako UTF-8 data (using the "surrogateescape"
#   error handler), wyjąwszy dla raw message data (ARTICLE, HEAD, BODY)
# - the `file` argument to various methods jest keyword-only
#
# - NNTP.date() returns a datetime object
# - NNTP.newgroups() oraz NNTP.newnews() take a datetime (or date) object,
#   rather than a pair of (date, time) strings.
# - NNTP.newgroups() oraz NNTP.list() zwróć a list of GroupInfo named tuples
# - NNTP.descriptions() returns a dict mapping group names to descriptions
# - NNTP.xover() returns a list of dicts mapping field names (header albo metadata)
#   to field values; each dict representing a message overview.
# - NNTP.article(), NNTP.head() oraz NNTP.body() zwróć a (response, ArticleInfo)
#   tuple.
# - the "internal" methods have been marked private (they now start with
#   an underscore)

# Other changes z the 2.x/3.1 nntplib:
# - automatic querying of capabilities at connect
# - New method NNTP.getcapabilities()
# - New method NNTP.over()
# - New helper function decode_header()
# - NNTP.post() oraz NNTP.ihave() accept file objects, bytes-like objects oraz
#   arbitrary iterables uzyskajing lines.
# - An extensive test suite :-)

# TODO:
# - zwróć structured data (GroupInfo etc.) everywhere
# - support HDR

# Imports
zaimportuj re
zaimportuj socket
zaimportuj collections
zaimportuj datetime
zaimportuj warnings

spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    _have_ssl = Nieprawda
inaczej:
    _have_ssl = Prawda

z email.header zaimportuj decode_header jako _email_decode_header
z socket zaimportuj _GLOBAL_DEFAULT_TIMEOUT

__all__ = ["NNTP",
           "NNTPError", "NNTPReplyError", "NNTPTemporaryError",
           "NNTPPermanentError", "NNTPProtocolError", "NNTPDataError",
           "decode_header",
           ]

# maximal line length when calling readline(). This jest to prevent
# reading arbitrary length lines. RFC 3977 limits NNTP line length to
# 512 characters, including CRLF. We have selected 2048 just to be on
# the safe side.
_MAXLINE = 2048


# Exceptions podnieśd when an error albo invalid response jest received
klasa NNTPError(Exception):
    """Base klasa dla all nntplib exceptions"""
    def __init__(self, *args):
        Exception.__init__(self, *args)
        spróbuj:
            self.response = args[0]
        wyjąwszy IndexError:
            self.response = 'No response given'

klasa NNTPReplyError(NNTPError):
    """Unexpected [123]xx reply"""
    dalej

klasa NNTPTemporaryError(NNTPError):
    """4xx errors"""
    dalej

klasa NNTPPermanentError(NNTPError):
    """5xx errors"""
    dalej

klasa NNTPProtocolError(NNTPError):
    """Response does nie begin przy [1-5]"""
    dalej

klasa NNTPDataError(NNTPError):
    """Error w response data"""
    dalej


# Standard port used by NNTP servers
NNTP_PORT = 119
NNTP_SSL_PORT = 563

# Response numbers that are followed by additional text (e.g. article)
_LONGRESP = {
    '100',   # HELP
    '101',   # CAPABILITIES
    '211',   # LISTGROUP   (also nie multi-line przy GROUP)
    '215',   # LIST
    '220',   # ARTICLE
    '221',   # HEAD, XHDR
    '222',   # BODY
    '224',   # OVER, XOVER
    '225',   # HDR
    '230',   # NEWNEWS
    '231',   # NEWGROUPS
    '282',   # XGTITLE
}

# Default decoded value dla LIST OVERVIEW.FMT jeżeli nie supported
_DEFAULT_OVERVIEW_FMT = [
    "subject", "from", "date", "message-id", "references", ":bytes", ":lines"]

# Alternative names allowed w LIST OVERVIEW.FMT response
_OVERVIEW_FMT_ALTERNATIVES = {
    'bytes': ':bytes',
    'lines': ':lines',
}

# Line terminators (we always output CRLF, but accept any of CRLF, CR, LF)
_CRLF = b'\r\n'

GroupInfo = collections.namedtuple('GroupInfo',
                                   ['group', 'last', 'first', 'flag'])

ArticleInfo = collections.namedtuple('ArticleInfo',
                                     ['number', 'message_id', 'lines'])


# Helper function(s)
def decode_header(header_str):
    """Takes an unicode string representing a munged header value
    oraz decodes it jako a (possibly non-ASCII) readable value."""
    parts = []
    dla v, enc w _email_decode_header(header_str):
        jeżeli isinstance(v, bytes):
            parts.append(v.decode(enc albo 'ascii'))
        inaczej:
            parts.append(v)
    zwróć ''.join(parts)

def _parse_overview_fmt(lines):
    """Parse a list of string representing the response to LIST OVERVIEW.FMT
    oraz zwróć a list of header/metadata names.
    Raises NNTPDataError jeżeli the response jest nie compliant
    (cf. RFC 3977, section 8.4)."""
    fmt = []
    dla line w lines:
        jeżeli line[0] == ':':
            # Metadata name (e.g. ":bytes")
            name, _, suffix = line[1:].partition(':')
            name = ':' + name
        inaczej:
            # Header name (e.g. "Subject:" albo "Xref:full")
            name, _, suffix = line.partition(':')
        name = name.lower()
        name = _OVERVIEW_FMT_ALTERNATIVES.get(name, name)
        # Should we do something przy the suffix?
        fmt.append(name)
    defaults = _DEFAULT_OVERVIEW_FMT
    jeżeli len(fmt) < len(defaults):
        podnieś NNTPDataError("LIST OVERVIEW.FMT response too short")
    jeżeli fmt[:len(defaults)] != defaults:
        podnieś NNTPDataError("LIST OVERVIEW.FMT redefines default fields")
    zwróć fmt

def _parse_overview(lines, fmt, data_process_func=Nic):
    """Parse the response to a OVER albo XOVER command according to the
    overview format `fmt`."""
    n_defaults = len(_DEFAULT_OVERVIEW_FMT)
    overview = []
    dla line w lines:
        fields = {}
        article_number, *tokens = line.split('\t')
        article_number = int(article_number)
        dla i, token w enumerate(tokens):
            jeżeli i >= len(fmt):
                # XXX should we podnieś an error? Some servers might nie
                # support LIST OVERVIEW.FMT oraz still zwróć additional
                # headers.
                kontynuuj
            field_name = fmt[i]
            is_metadata = field_name.startswith(':')
            jeżeli i >= n_defaults oraz nie is_metadata:
                # Non-default header names are included w full w the response
                # (unless the field jest totally empty)
                h = field_name + ": "
                jeżeli token oraz token[:len(h)].lower() != h:
                    podnieś NNTPDataError("OVER/XOVER response doesn't include "
                                        "names of additional headers")
                token = token[len(h):] jeżeli token inaczej Nic
            fields[fmt[i]] = token
        overview.append((article_number, fields))
    zwróć overview

def _parse_datetime(date_str, time_str=Nic):
    """Parse a pair of (date, time) strings, oraz zwróć a datetime object.
    If only the date jest given, it jest assumed to be date oraz time
    concatenated together (e.g. response to the DATE command).
    """
    jeżeli time_str jest Nic:
        time_str = date_str[-6:]
        date_str = date_str[:-6]
    hours = int(time_str[:2])
    minutes = int(time_str[2:4])
    seconds = int(time_str[4:])
    year = int(date_str[:-4])
    month = int(date_str[-4:-2])
    day = int(date_str[-2:])
    # RFC 3977 doesn't say how to interpret 2-char years.  Assume that
    # there are no dates before 1970 on Usenet.
    jeżeli year < 70:
        year += 2000
    albo_inaczej year < 100:
        year += 1900
    zwróć datetime.datetime(year, month, day, hours, minutes, seconds)

def _unparse_datetime(dt, legacy=Nieprawda):
    """Format a date albo datetime object jako a pair of (date, time) strings
    w the format required by the NEWNEWS oraz NEWGROUPS commands.  If a
    date object jest dalejed, the time jest assumed to be midnight (00h00).

    The returned representation depends on the legacy flag:
    * jeżeli legacy jest Nieprawda (the default):
      date has the YYYYMMDD format oraz time the HHMMSS format
    * jeżeli legacy jest Prawda:
      date has the YYMMDD format oraz time the HHMMSS format.
    RFC 3977 compliant servers should understand both formats; therefore,
    legacy jest only needed when talking to old servers.
    """
    jeżeli nie isinstance(dt, datetime.datetime):
        time_str = "000000"
    inaczej:
        time_str = "{0.hour:02d}{0.minute:02d}{0.second:02d}".format(dt)
    y = dt.year
    jeżeli legacy:
        y = y % 100
        date_str = "{0:02d}{1.month:02d}{1.day:02d}".format(y, dt)
    inaczej:
        date_str = "{0:04d}{1.month:02d}{1.day:02d}".format(y, dt)
    zwróć date_str, time_str


jeżeli _have_ssl:

    def _encrypt_on(sock, context, hostname):
        """Wrap a socket w SSL/TLS. Arguments:
        - sock: Socket to wrap
        - context: SSL context to use dla the encrypted connection
        Returns:
        - sock: New, encrypted socket.
        """
        # Generate a default SSL context jeżeli none was dalejed.
        jeżeli context jest Nic:
            context = ssl._create_stdlib_context()
        zwróć context.wrap_socket(sock, server_hostname=hostname)


# The classes themselves
klasa _NNTPBase:
    # UTF-8 jest the character set dla all NNTP commands oraz responses: they
    # are automatically encoded (when sending) oraz decoded (and receiving)
    # by this class.
    # However, some multi-line data blocks can contain arbitrary bytes (for
    # example, latin-1 albo utf-16 data w the body of a message). Commands
    # taking (POST, IHAVE) albo returning (HEAD, BODY, ARTICLE) raw message
    # data will therefore only accept oraz produce bytes objects.
    # Furthermore, since there could be non-compliant servers out there,
    # we use 'surrogateescape' jako the error handler dla fault tolerance
    # oraz easy round-tripping. This could be useful dla some applications
    # (e.g. NNTP gateways).

    encoding = 'utf-8'
    errors = 'surrogateescape'

    def __init__(self, file, host,
                 readermode=Nic, timeout=_GLOBAL_DEFAULT_TIMEOUT):
        """Initialize an instance.  Arguments:
        - file: file-like object (open dla read/write w binary mode)
        - host: hostname of the server
        - readermode: jeżeli true, send 'mode reader' command after
                      connecting.
        - timeout: timeout (in seconds) used dla socket connections

        readermode jest sometimes necessary jeżeli you are connecting to an
        NNTP server on the local machine oraz intend to call
        reader-specific commands, such jako `group'.  If you get
        unexpected NNTPPermanentErrors, you might need to set
        readermode.
        """
        self.host = host
        self.file = file
        self.debugging = 0
        self.welcome = self._getresp()

        # Inquire about capabilities (RFC 3977).
        self._caps = Nic
        self.getcapabilities()

        # 'MODE READER' jest sometimes necessary to enable 'reader' mode.
        # However, the order w which 'MODE READER' oraz 'AUTHINFO' need to
        # arrive differs between some NNTP servers. If _setreadermode() fails
        # przy an authorization failed error, it will set this to Prawda;
        # the login() routine will interpret that jako a request to try again
        # after performing its normal function.
        # Enable only jeżeli we're nie already w READER mode anyway.
        self.readermode_afterauth = Nieprawda
        jeżeli readermode oraz 'READER' nie w self._caps:
            self._setreadermode()
            jeżeli nie self.readermode_afterauth:
                # Capabilities might have changed after MODE READER
                self._caps = Nic
                self.getcapabilities()

        # RFC 4642 2.2.2: Both the client oraz the server MUST know jeżeli there jest
        # a TLS session active.  A client MUST NOT attempt to start a TLS
        # session jeżeli a TLS session jest already active.
        self.tls_on = Nieprawda

        # Log w oraz encryption setup order jest left to subclasses.
        self.authenticated = Nieprawda

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        is_connected = lambda: hasattr(self, "file")
        jeżeli is_connected():
            spróbuj:
                self.quit()
            wyjąwszy (OSError, EOFError):
                dalej
            w_końcu:
                jeżeli is_connected():
                    self._close()

    def getwelcome(self):
        """Get the welcome message z the server
        (this jest read oraz squirreled away by __init__()).
        If the response code jest 200, posting jest allowed;
        jeżeli it 201, posting jest nie allowed."""

        jeżeli self.debugging: print('*welcome*', repr(self.welcome))
        zwróć self.welcome

    def getcapabilities(self):
        """Get the server capabilities, jako read by __init__().
        If the CAPABILITIES command jest nie supported, an empty dict jest
        returned."""
        jeżeli self._caps jest Nic:
            self.nntp_version = 1
            self.nntp_implementation = Nic
            spróbuj:
                resp, caps = self.capabilities()
            wyjąwszy (NNTPPermanentError, NNTPTemporaryError):
                # Server doesn't support capabilities
                self._caps = {}
            inaczej:
                self._caps = caps
                jeżeli 'VERSION' w caps:
                    # The server can advertise several supported versions,
                    # choose the highest.
                    self.nntp_version = max(map(int, caps['VERSION']))
                jeżeli 'IMPLEMENTATION' w caps:
                    self.nntp_implementation = ' '.join(caps['IMPLEMENTATION'])
        zwróć self._caps

    def set_debuglevel(self, level):
        """Set the debugging level.  Argument 'level' means:
        0: no debugging output (default)
        1: print commands oraz responses but nie body text etc.
        2: also print raw lines read oraz sent before stripping CR/LF"""

        self.debugging = level
    debug = set_debuglevel

    def _putline(self, line):
        """Internal: send one line to the server, appending CRLF.
        The `line` must be a bytes-like object."""
        line = line + _CRLF
        jeżeli self.debugging > 1: print('*put*', repr(line))
        self.file.write(line)
        self.file.flush()

    def _putcmd(self, line):
        """Internal: send one command to the server (through _putline()).
        The `line` must be an unicode string."""
        jeżeli self.debugging: print('*cmd*', repr(line))
        line = line.encode(self.encoding, self.errors)
        self._putline(line)

    def _getline(self, strip_crlf=Prawda):
        """Internal: zwróć one line z the server, stripping _CRLF.
        Raise EOFError jeżeli the connection jest closed.
        Returns a bytes object."""
        line = self.file.readline(_MAXLINE +1)
        jeżeli len(line) > _MAXLINE:
            podnieś NNTPDataError('line too long')
        jeżeli self.debugging > 1:
            print('*get*', repr(line))
        jeżeli nie line: podnieś EOFError
        jeżeli strip_crlf:
            jeżeli line[-2:] == _CRLF:
                line = line[:-2]
            albo_inaczej line[-1:] w _CRLF:
                line = line[:-1]
        zwróć line

    def _getresp(self):
        """Internal: get a response z the server.
        Raise various errors jeżeli the response indicates an error.
        Returns an unicode string."""
        resp = self._getline()
        jeżeli self.debugging: print('*resp*', repr(resp))
        resp = resp.decode(self.encoding, self.errors)
        c = resp[:1]
        jeżeli c == '4':
            podnieś NNTPTemporaryError(resp)
        jeżeli c == '5':
            podnieś NNTPPermanentError(resp)
        jeżeli c nie w '123':
            podnieś NNTPProtocolError(resp)
        zwróć resp

    def _getlongresp(self, file=Nic):
        """Internal: get a response plus following text z the server.
        Raise various errors jeżeli the response indicates an error.

        Returns a (response, lines) tuple where `response` jest an unicode
        string oraz `lines` jest a list of bytes objects.
        If `file` jest a file-like object, it must be open w binary mode.
        """

        openedFile = Nic
        spróbuj:
            # If a string was dalejed then open a file przy that name
            jeżeli isinstance(file, (str, bytes)):
                openedFile = file = open(file, "wb")

            resp = self._getresp()
            jeżeli resp[:3] nie w _LONGRESP:
                podnieś NNTPReplyError(resp)

            lines = []
            jeżeli file jest nie Nic:
                # XXX lines = Nic instead?
                terminators = (b'.' + _CRLF, b'.\n')
                dopóki 1:
                    line = self._getline(Nieprawda)
                    jeżeli line w terminators:
                        przerwij
                    jeżeli line.startswith(b'..'):
                        line = line[1:]
                    file.write(line)
            inaczej:
                terminator = b'.'
                dopóki 1:
                    line = self._getline()
                    jeżeli line == terminator:
                        przerwij
                    jeżeli line.startswith(b'..'):
                        line = line[1:]
                    lines.append(line)
        w_końcu:
            # If this method created the file, then it must close it
            jeżeli openedFile:
                openedFile.close()

        zwróć resp, lines

    def _shortcmd(self, line):
        """Internal: send a command oraz get the response.
        Same zwróć value jako _getresp()."""
        self._putcmd(line)
        zwróć self._getresp()

    def _longcmd(self, line, file=Nic):
        """Internal: send a command oraz get the response plus following text.
        Same zwróć value jako _getlongresp()."""
        self._putcmd(line)
        zwróć self._getlongresp(file)

    def _longcmdstring(self, line, file=Nic):
        """Internal: send a command oraz get the response plus following text.
        Same jako _longcmd() oraz _getlongresp(), wyjąwszy that the returned `lines`
        are unicode strings rather than bytes objects.
        """
        self._putcmd(line)
        resp, list = self._getlongresp(file)
        zwróć resp, [line.decode(self.encoding, self.errors)
                      dla line w list]

    def _getoverviewfmt(self):
        """Internal: get the overview format. Queries the server jeżeli nie
        already done, inaczej returns the cached value."""
        spróbuj:
            zwróć self._cachedoverviewfmt
        wyjąwszy AttributeError:
            dalej
        spróbuj:
            resp, lines = self._longcmdstring("LIST OVERVIEW.FMT")
        wyjąwszy NNTPPermanentError:
            # Not supported by server?
            fmt = _DEFAULT_OVERVIEW_FMT[:]
        inaczej:
            fmt = _parse_overview_fmt(lines)
        self._cachedoverviewfmt = fmt
        zwróć fmt

    def _grouplist(self, lines):
        # Parse lines into "group last first flag"
        zwróć [GroupInfo(*line.split()) dla line w lines]

    def capabilities(self):
        """Process a CAPABILITIES command.  Not supported by all servers.
        Return:
        - resp: server response jeżeli successful
        - caps: a dictionary mapping capability names to lists of tokens
        (dla example {'VERSION': ['2'], 'OVER': [], LIST: ['ACTIVE', 'HEADERS'] })
        """
        caps = {}
        resp, lines = self._longcmdstring("CAPABILITIES")
        dla line w lines:
            name, *tokens = line.split()
            caps[name] = tokens
        zwróć resp, caps

    def newgroups(self, date, *, file=Nic):
        """Process a NEWGROUPS command.  Arguments:
        - date: a date albo datetime object
        Return:
        - resp: server response jeżeli successful
        - list: list of newsgroup names
        """
        jeżeli nie isinstance(date, (datetime.date, datetime.date)):
            podnieś TypeError(
                "the date parameter must be a date albo datetime object, "
                "not '{:40}'".format(date.__class__.__name__))
        date_str, time_str = _unparse_datetime(date, self.nntp_version < 2)
        cmd = 'NEWGROUPS {0} {1}'.format(date_str, time_str)
        resp, lines = self._longcmdstring(cmd, file)
        zwróć resp, self._grouplist(lines)

    def newnews(self, group, date, *, file=Nic):
        """Process a NEWNEWS command.  Arguments:
        - group: group name albo '*'
        - date: a date albo datetime object
        Return:
        - resp: server response jeżeli successful
        - list: list of message ids
        """
        jeżeli nie isinstance(date, (datetime.date, datetime.date)):
            podnieś TypeError(
                "the date parameter must be a date albo datetime object, "
                "not '{:40}'".format(date.__class__.__name__))
        date_str, time_str = _unparse_datetime(date, self.nntp_version < 2)
        cmd = 'NEWNEWS {0} {1} {2}'.format(group, date_str, time_str)
        zwróć self._longcmdstring(cmd, file)

    def list(self, group_pattern=Nic, *, file=Nic):
        """Process a LIST albo LIST ACTIVE command. Arguments:
        - group_pattern: a pattern indicating which groups to query
        - file: Filename string albo file object to store the result w
        Returns:
        - resp: server response jeżeli successful
        - list: list of (group, last, first, flag) (strings)
        """
        jeżeli group_pattern jest nie Nic:
            command = 'LIST ACTIVE ' + group_pattern
        inaczej:
            command = 'LIST'
        resp, lines = self._longcmdstring(command, file)
        zwróć resp, self._grouplist(lines)

    def _getdescriptions(self, group_pattern, return_all):
        line_pat = re.compile('^(?P<group>[^ \t]+)[ \t]+(.*)$')
        # Try the more std (acc. to RFC2980) LIST NEWSGROUPS first
        resp, lines = self._longcmdstring('LIST NEWSGROUPS ' + group_pattern)
        jeżeli nie resp.startswith('215'):
            # Now the deprecated XGTITLE.  This either podnieśs an error
            # albo succeeds przy the same output structure jako LIST
            # NEWSGROUPS.
            resp, lines = self._longcmdstring('XGTITLE ' + group_pattern)
        groups = {}
        dla raw_line w lines:
            match = line_pat.search(raw_line.strip())
            jeżeli match:
                name, desc = match.group(1, 2)
                jeżeli nie return_all:
                    zwróć desc
                groups[name] = desc
        jeżeli return_all:
            zwróć resp, groups
        inaczej:
            # Nothing found
            zwróć ''

    def description(self, group):
        """Get a description dla a single group.  If more than one
        group matches ('group' jest a pattern), zwróć the first.  If no
        group matches, zwróć an empty string.

        This elides the response code z the server, since it can
        only be '215' albo '285' (dla xgtitle) anyway.  If the response
        code jest needed, use the 'descriptions' method.

        NOTE: This neither checks dla a wildcard w 'group' nor does
        it check whether the group actually exists."""
        zwróć self._getdescriptions(group, Nieprawda)

    def descriptions(self, group_pattern):
        """Get descriptions dla a range of groups."""
        zwróć self._getdescriptions(group_pattern, Prawda)

    def group(self, name):
        """Process a GROUP command.  Argument:
        - group: the group name
        Returns:
        - resp: server response jeżeli successful
        - count: number of articles
        - first: first article number
        - last: last article number
        - name: the group name
        """
        resp = self._shortcmd('GROUP ' + name)
        jeżeli nie resp.startswith('211'):
            podnieś NNTPReplyError(resp)
        words = resp.split()
        count = first = last = 0
        n = len(words)
        jeżeli n > 1:
            count = words[1]
            jeżeli n > 2:
                first = words[2]
                jeżeli n > 3:
                    last = words[3]
                    jeżeli n > 4:
                        name = words[4].lower()
        zwróć resp, int(count), int(first), int(last), name

    def help(self, *, file=Nic):
        """Process a HELP command. Argument:
        - file: Filename string albo file object to store the result w
        Returns:
        - resp: server response jeżeli successful
        - list: list of strings returned by the server w response to the
                HELP command
        """
        zwróć self._longcmdstring('HELP', file)

    def _statparse(self, resp):
        """Internal: parse the response line of a STAT, NEXT, LAST,
        ARTICLE, HEAD albo BODY command."""
        jeżeli nie resp.startswith('22'):
            podnieś NNTPReplyError(resp)
        words = resp.split()
        art_num = int(words[1])
        message_id = words[2]
        zwróć resp, art_num, message_id

    def _statcmd(self, line):
        """Internal: process a STAT, NEXT albo LAST command."""
        resp = self._shortcmd(line)
        zwróć self._statparse(resp)

    def stat(self, message_spec=Nic):
        """Process a STAT command.  Argument:
        - message_spec: article number albo message id (jeżeli nie specified,
          the current article jest selected)
        Returns:
        - resp: server response jeżeli successful
        - art_num: the article number
        - message_id: the message id
        """
        jeżeli message_spec:
            zwróć self._statcmd('STAT {0}'.format(message_spec))
        inaczej:
            zwróć self._statcmd('STAT')

    def next(self):
        """Process a NEXT command.  No arguments.  Return jako dla STAT."""
        zwróć self._statcmd('NEXT')

    def last(self):
        """Process a LAST command.  No arguments.  Return jako dla STAT."""
        zwróć self._statcmd('LAST')

    def _artcmd(self, line, file=Nic):
        """Internal: process a HEAD, BODY albo ARTICLE command."""
        resp, lines = self._longcmd(line, file)
        resp, art_num, message_id = self._statparse(resp)
        zwróć resp, ArticleInfo(art_num, message_id, lines)

    def head(self, message_spec=Nic, *, file=Nic):
        """Process a HEAD command.  Argument:
        - message_spec: article number albo message id
        - file: filename string albo file object to store the headers w
        Returns:
        - resp: server response jeżeli successful
        - ArticleInfo: (article number, message id, list of header lines)
        """
        jeżeli message_spec jest nie Nic:
            cmd = 'HEAD {0}'.format(message_spec)
        inaczej:
            cmd = 'HEAD'
        zwróć self._artcmd(cmd, file)

    def body(self, message_spec=Nic, *, file=Nic):
        """Process a BODY command.  Argument:
        - message_spec: article number albo message id
        - file: filename string albo file object to store the body w
        Returns:
        - resp: server response jeżeli successful
        - ArticleInfo: (article number, message id, list of body lines)
        """
        jeżeli message_spec jest nie Nic:
            cmd = 'BODY {0}'.format(message_spec)
        inaczej:
            cmd = 'BODY'
        zwróć self._artcmd(cmd, file)

    def article(self, message_spec=Nic, *, file=Nic):
        """Process an ARTICLE command.  Argument:
        - message_spec: article number albo message id
        - file: filename string albo file object to store the article w
        Returns:
        - resp: server response jeżeli successful
        - ArticleInfo: (article number, message id, list of article lines)
        """
        jeżeli message_spec jest nie Nic:
            cmd = 'ARTICLE {0}'.format(message_spec)
        inaczej:
            cmd = 'ARTICLE'
        zwróć self._artcmd(cmd, file)

    def slave(self):
        """Process a SLAVE command.  Returns:
        - resp: server response jeżeli successful
        """
        zwróć self._shortcmd('SLAVE')

    def xhdr(self, hdr, str, *, file=Nic):
        """Process an XHDR command (optional server extension).  Arguments:
        - hdr: the header type (e.g. 'subject')
        - str: an article nr, a message id, albo a range nr1-nr2
        - file: Filename string albo file object to store the result w
        Returns:
        - resp: server response jeżeli successful
        - list: list of (nr, value) strings
        """
        pat = re.compile('^([0-9]+) ?(.*)\n?')
        resp, lines = self._longcmdstring('XHDR {0} {1}'.format(hdr, str), file)
        def remove_number(line):
            m = pat.match(line)
            zwróć m.group(1, 2) jeżeli m inaczej line
        zwróć resp, [remove_number(line) dla line w lines]

    def xover(self, start, end, *, file=Nic):
        """Process an XOVER command (optional server extension) Arguments:
        - start: start of range
        - end: end of range
        - file: Filename string albo file object to store the result w
        Returns:
        - resp: server response jeżeli successful
        - list: list of dicts containing the response fields
        """
        resp, lines = self._longcmdstring('XOVER {0}-{1}'.format(start, end),
                                          file)
        fmt = self._getoverviewfmt()
        zwróć resp, _parse_overview(lines, fmt)

    def over(self, message_spec, *, file=Nic):
        """Process an OVER command.  If the command isn't supported, fall
        back to XOVER. Arguments:
        - message_spec:
            - either a message id, indicating the article to fetch
              information about
            - albo a (start, end) tuple, indicating a range of article numbers;
              jeżeli end jest Nic, information up to the newest message will be
              retrieved
            - albo Nic, indicating the current article number must be used
        - file: Filename string albo file object to store the result w
        Returns:
        - resp: server response jeżeli successful
        - list: list of dicts containing the response fields

        NOTE: the "message id" form isn't supported by XOVER
        """
        cmd = 'OVER' jeżeli 'OVER' w self._caps inaczej 'XOVER'
        jeżeli isinstance(message_spec, (tuple, list)):
            start, end = message_spec
            cmd += ' {0}-{1}'.format(start, end albo '')
        albo_inaczej message_spec jest nie Nic:
            cmd = cmd + ' ' + message_spec
        resp, lines = self._longcmdstring(cmd, file)
        fmt = self._getoverviewfmt()
        zwróć resp, _parse_overview(lines, fmt)

    def xgtitle(self, group, *, file=Nic):
        """Process an XGTITLE command (optional server extension) Arguments:
        - group: group name wildcard (i.e. news.*)
        Returns:
        - resp: server response jeżeli successful
        - list: list of (name,title) strings"""
        warnings.warn("The XGTITLE extension jest nie actively used, "
                      "use descriptions() instead",
                      DeprecationWarning, 2)
        line_pat = re.compile('^([^ \t]+)[ \t]+(.*)$')
        resp, raw_lines = self._longcmdstring('XGTITLE ' + group, file)
        lines = []
        dla raw_line w raw_lines:
            match = line_pat.search(raw_line.strip())
            jeżeli match:
                lines.append(match.group(1, 2))
        zwróć resp, lines

    def xpath(self, id):
        """Process an XPATH command (optional server extension) Arguments:
        - id: Message id of article
        Returns:
        resp: server response jeżeli successful
        path: directory path to article
        """
        warnings.warn("The XPATH extension jest nie actively used",
                      DeprecationWarning, 2)

        resp = self._shortcmd('XPATH {0}'.format(id))
        jeżeli nie resp.startswith('223'):
            podnieś NNTPReplyError(resp)
        spróbuj:
            [resp_num, path] = resp.split()
        wyjąwszy ValueError:
            podnieś NNTPReplyError(resp)
        inaczej:
            zwróć resp, path

    def date(self):
        """Process the DATE command.
        Returns:
        - resp: server response jeżeli successful
        - date: datetime object
        """
        resp = self._shortcmd("DATE")
        jeżeli nie resp.startswith('111'):
            podnieś NNTPReplyError(resp)
        elem = resp.split()
        jeżeli len(elem) != 2:
            podnieś NNTPDataError(resp)
        date = elem[1]
        jeżeli len(date) != 14:
            podnieś NNTPDataError(resp)
        zwróć resp, _parse_datetime(date, Nic)

    def _post(self, command, f):
        resp = self._shortcmd(command)
        # Raises a specific exception jeżeli posting jest nie allowed
        jeżeli nie resp.startswith('3'):
            podnieś NNTPReplyError(resp)
        jeżeli isinstance(f, (bytes, bytearray)):
            f = f.splitlines()
        # We don't use _putline() because:
        # - we don't want additional CRLF jeżeli the file albo iterable jest already
        #   w the right format
        # - we don't want a spurious flush() after each line jest written
        dla line w f:
            jeżeli nie line.endswith(_CRLF):
                line = line.rstrip(b"\r\n") + _CRLF
            jeżeli line.startswith(b'.'):
                line = b'.' + line
            self.file.write(line)
        self.file.write(b".\r\n")
        self.file.flush()
        zwróć self._getresp()

    def post(self, data):
        """Process a POST command.  Arguments:
        - data: bytes object, iterable albo file containing the article
        Returns:
        - resp: server response jeżeli successful"""
        zwróć self._post('POST', data)

    def ihave(self, message_id, data):
        """Process an IHAVE command.  Arguments:
        - message_id: message-id of the article
        - data: file containing the article
        Returns:
        - resp: server response jeżeli successful
        Note that jeżeli the server refuses the article an exception jest podnieśd."""
        zwróć self._post('IHAVE {0}'.format(message_id), data)

    def _close(self):
        self.file.close()
        usuń self.file

    def quit(self):
        """Process a QUIT command oraz close the socket.  Returns:
        - resp: server response jeżeli successful"""
        spróbuj:
            resp = self._shortcmd('QUIT')
        w_końcu:
            self._close()
        zwróć resp

    def login(self, user=Nic, dalejword=Nic, usenetrc=Prawda):
        jeżeli self.authenticated:
            podnieś ValueError("Already logged in.")
        jeżeli nie user oraz nie usenetrc:
            podnieś ValueError(
                "At least one of `user` oraz `usenetrc` must be specified")
        # If no login/password was specified but netrc was requested,
        # try to get them z ~/.netrc
        # Presume that jeżeli .netrc has an entry, NNRP authentication jest required.
        spróbuj:
            jeżeli usenetrc oraz nie user:
                zaimportuj netrc
                credentials = netrc.netrc()
                auth = credentials.authenticators(self.host)
                jeżeli auth:
                    user = auth[0]
                    dalejword = auth[2]
        wyjąwszy OSError:
            dalej
        # Perform NNTP authentication jeżeli needed.
        jeżeli nie user:
            zwróć
        resp = self._shortcmd('authinfo user ' + user)
        jeżeli resp.startswith('381'):
            jeżeli nie dalejword:
                podnieś NNTPReplyError(resp)
            inaczej:
                resp = self._shortcmd('authinfo dalej ' + dalejword)
                jeżeli nie resp.startswith('281'):
                    podnieś NNTPPermanentError(resp)
        # Capabilities might have changed after login
        self._caps = Nic
        self.getcapabilities()
        # Attempt to send mode reader jeżeli it was requested after login.
        # Only do so jeżeli we're nie w reader mode already.
        jeżeli self.readermode_afterauth oraz 'READER' nie w self._caps:
            self._setreadermode()
            # Capabilities might have changed after MODE READER
            self._caps = Nic
            self.getcapabilities()

    def _setreadermode(self):
        spróbuj:
            self.welcome = self._shortcmd('mode reader')
        wyjąwszy NNTPPermanentError:
            # Error 5xx, probably 'not implemented'
            dalej
        wyjąwszy NNTPTemporaryError jako e:
            jeżeli e.response.startswith('480'):
                # Need authorization before 'mode reader'
                self.readermode_afterauth = Prawda
            inaczej:
                podnieś

    jeżeli _have_ssl:
        def starttls(self, context=Nic):
            """Process a STARTTLS command. Arguments:
            - context: SSL context to use dla the encrypted connection
            """
            # Per RFC 4642, STARTTLS MUST NOT be sent after authentication albo if
            # a TLS session already exists.
            jeżeli self.tls_on:
                podnieś ValueError("TLS jest already enabled.")
            jeżeli self.authenticated:
                podnieś ValueError("TLS cannot be started after authentication.")
            resp = self._shortcmd('STARTTLS')
            jeżeli resp.startswith('382'):
                self.file.close()
                self.sock = _encrypt_on(self.sock, context, self.host)
                self.file = self.sock.makefile("rwb")
                self.tls_on = Prawda
                # Capabilities may change after TLS starts up, so ask dla them
                # again.
                self._caps = Nic
                self.getcapabilities()
            inaczej:
                podnieś NNTPError("TLS failed to start.")


klasa NNTP(_NNTPBase):

    def __init__(self, host, port=NNTP_PORT, user=Nic, dalejword=Nic,
                 readermode=Nic, usenetrc=Nieprawda,
                 timeout=_GLOBAL_DEFAULT_TIMEOUT):
        """Initialize an instance.  Arguments:
        - host: hostname to connect to
        - port: port to connect to (default the standard NNTP port)
        - user: username to authenticate with
        - dalejword: dalejword to use przy username
        - readermode: jeżeli true, send 'mode reader' command after
                      connecting.
        - usenetrc: allow loading username oraz dalejword z ~/.netrc file
                    jeżeli nie specified explicitly
        - timeout: timeout (in seconds) used dla socket connections

        readermode jest sometimes necessary jeżeli you are connecting to an
        NNTP server on the local machine oraz intend to call
        reader-specific commands, such jako `group'.  If you get
        unexpected NNTPPermanentErrors, you might need to set
        readermode.
        """
        self.host = host
        self.port = port
        self.sock = socket.create_connection((host, port), timeout)
        file = Nic
        spróbuj:
            file = self.sock.makefile("rwb")
            _NNTPBase.__init__(self, file, host,
                               readermode, timeout)
            jeżeli user albo usenetrc:
                self.login(user, dalejword, usenetrc)
        wyjąwszy:
            jeżeli file:
                file.close()
            self.sock.close()
            podnieś

    def _close(self):
        spróbuj:
            _NNTPBase._close(self)
        w_końcu:
            self.sock.close()


jeżeli _have_ssl:
    klasa NNTP_SSL(_NNTPBase):

        def __init__(self, host, port=NNTP_SSL_PORT,
                    user=Nic, dalejword=Nic, ssl_context=Nic,
                    readermode=Nic, usenetrc=Nieprawda,
                    timeout=_GLOBAL_DEFAULT_TIMEOUT):
            """This works identically to NNTP.__init__, wyjąwszy dla the change
            w default port oraz the `ssl_context` argument dla SSL connections.
            """
            self.sock = socket.create_connection((host, port), timeout)
            file = Nic
            spróbuj:
                self.sock = _encrypt_on(self.sock, ssl_context, host)
                file = self.sock.makefile("rwb")
                _NNTPBase.__init__(self, file, host,
                                   readermode=readermode, timeout=timeout)
                jeżeli user albo usenetrc:
                    self.login(user, dalejword, usenetrc)
            wyjąwszy:
                jeżeli file:
                    file.close()
                self.sock.close()
                podnieś

        def _close(self):
            spróbuj:
                _NNTPBase._close(self)
            w_końcu:
                self.sock.close()

    __all__.append("NNTP_SSL")


# Test retrieval when run jako a script.
jeżeli __name__ == '__main__':
    zaimportuj argparse

    parser = argparse.ArgumentParser(description="""\
        nntplib built-in demo - display the latest articles w a newsgroup""")
    parser.add_argument('-g', '--group', default='gmane.comp.python.general',
                        help='group to fetch messages z (default: %(default)s)')
    parser.add_argument('-s', '--server', default='news.gmane.org',
                        help='NNTP server hostname (default: %(default)s)')
    parser.add_argument('-p', '--port', default=-1, type=int,
                        help='NNTP port number (default: %s / %s)' % (NNTP_PORT, NNTP_SSL_PORT))
    parser.add_argument('-n', '--nb-articles', default=10, type=int,
                        help='number of articles to fetch (default: %(default)s)')
    parser.add_argument('-S', '--ssl', action='store_true', default=Nieprawda,
                        help='use NNTP over SSL')
    args = parser.parse_args()

    port = args.port
    jeżeli nie args.ssl:
        jeżeli port == -1:
            port = NNTP_PORT
        s = NNTP(host=args.server, port=port)
    inaczej:
        jeżeli port == -1:
            port = NNTP_SSL_PORT
        s = NNTP_SSL(host=args.server, port=port)

    caps = s.getcapabilities()
    jeżeli 'STARTTLS' w caps:
        s.starttls()
    resp, count, first, last, name = s.group(args.group)
    print('Group', name, 'has', count, 'articles, range', first, 'to', last)

    def cut(s, lim):
        jeżeli len(s) > lim:
            s = s[:lim - 4] + "..."
        zwróć s

    first = str(int(last) - args.nb_articles + 1)
    resp, overviews = s.xover(first, last)
    dla artnum, over w overviews:
        author = decode_header(over['from']).split('<', 1)[0]
        subject = decode_header(over['subject'])
        lines = int(over[':lines'])
        print("{:7} {:20} {:42} ({})".format(
              artnum, cut(author, 20), cut(subject, 42), lines)
              )

    s.quit()
