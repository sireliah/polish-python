"""IMAP4 client.

Based on RFC 2060.

Public class:           IMAP4
Public variable:        Debug
Public functions:       Internaldate2tuple
                        Int2AP
                        ParseFlags
                        Time2Internaldate
"""

# Author: Piers Lauder <piers@cs.su.oz.au> December 1997.
#
# Authentication code contributed by Donn Cave <donn@u.washington.edu> June 1998.
# String method conversion by ESR, February 2001.
# GET/SETACL contributed by Anthony Baxter <anthony@interlink.com.au> April 2001.
# IMAP4_SSL contributed by Tino Lange <Tino.Lange@isg.de> March 2002.
# GET/SETQUOTA contributed by Andreas Zeidler <az@kreativkombinat.de> June 2002.
# PROXYAUTH contributed by Rick Holbert <holbert.13@osu.edu> November 2002.
# GET/SETANNOTATION contributed by Tomas Lindroos <skitta@abo.fi> June 2005.

__version__ = "2.58"

zaimportuj binascii, errno, random, re, socket, subprocess, sys, time, calendar
z datetime zaimportuj datetime, timezone, timedelta
z io zaimportuj DEFAULT_BUFFER_SIZE

spróbuj:
    zaimportuj ssl
    HAVE_SSL = Prawda
wyjąwszy ImportError:
    HAVE_SSL = Nieprawda

__all__ = ["IMAP4", "IMAP4_stream", "Internaldate2tuple",
           "Int2AP", "ParseFlags", "Time2Internaldate"]

#       Globals

CRLF = b'\r\n'
Debug = 0
IMAP4_PORT = 143
IMAP4_SSL_PORT = 993
AllowedVersions = ('IMAP4REV1', 'IMAP4')        # Most recent first

# Maximal line length when calling readline(). This jest to prevent
# reading arbitrary length lines. RFC 3501 oraz 2060 (IMAP 4rev1)
# don't specify a line length. RFC 2683 suggests limiting client
# command lines to 1000 octets oraz that servers should be prepared
# to accept command lines up to 8000 octets, so we used to use 10K here.
# In the modern world (eg: gmail) the response to, dla example, a
# search command can be quite large, so we now use 1M.
_MAXLINE = 1000000


#       Commands

Commands = {
        # name            valid states
        'APPEND':       ('AUTH', 'SELECTED'),
        'AUTHENTICATE': ('NONAUTH',),
        'CAPABILITY':   ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'),
        'CHECK':        ('SELECTED',),
        'CLOSE':        ('SELECTED',),
        'COPY':         ('SELECTED',),
        'CREATE':       ('AUTH', 'SELECTED'),
        'DELETE':       ('AUTH', 'SELECTED'),
        'DELETEACL':    ('AUTH', 'SELECTED'),
        'ENABLE':       ('AUTH', ),
        'EXAMINE':      ('AUTH', 'SELECTED'),
        'EXPUNGE':      ('SELECTED',),
        'FETCH':        ('SELECTED',),
        'GETACL':       ('AUTH', 'SELECTED'),
        'GETANNOTATION':('AUTH', 'SELECTED'),
        'GETQUOTA':     ('AUTH', 'SELECTED'),
        'GETQUOTAROOT': ('AUTH', 'SELECTED'),
        'MYRIGHTS':     ('AUTH', 'SELECTED'),
        'LIST':         ('AUTH', 'SELECTED'),
        'LOGIN':        ('NONAUTH',),
        'LOGOUT':       ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'),
        'LSUB':         ('AUTH', 'SELECTED'),
        'NAMESPACE':    ('AUTH', 'SELECTED'),
        'NOOP':         ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'),
        'PARTIAL':      ('SELECTED',),                                  # NB: obsolete
        'PROXYAUTH':    ('AUTH',),
        'RENAME':       ('AUTH', 'SELECTED'),
        'SEARCH':       ('SELECTED',),
        'SELECT':       ('AUTH', 'SELECTED'),
        'SETACL':       ('AUTH', 'SELECTED'),
        'SETANNOTATION':('AUTH', 'SELECTED'),
        'SETQUOTA':     ('AUTH', 'SELECTED'),
        'SORT':         ('SELECTED',),
        'STARTTLS':     ('NONAUTH',),
        'STATUS':       ('AUTH', 'SELECTED'),
        'STORE':        ('SELECTED',),
        'SUBSCRIBE':    ('AUTH', 'SELECTED'),
        'THREAD':       ('SELECTED',),
        'UID':          ('SELECTED',),
        'UNSUBSCRIBE':  ('AUTH', 'SELECTED'),
        }

#       Patterns to match server responses

Continuation = re.compile(br'\+( (?P<data>.*))?')
Flags = re.compile(br'.*FLAGS \((?P<flags>[^\)]*)\)')
InternalDate = re.compile(br'.*INTERNALDATE "'
        br'(?P<day>[ 0123][0-9])-(?P<mon>[A-Z][a-z][a-z])-(?P<year>[0-9][0-9][0-9][0-9])'
        br' (?P<hour>[0-9][0-9]):(?P<min>[0-9][0-9]):(?P<sec>[0-9][0-9])'
        br' (?P<zonen>[-+])(?P<zoneh>[0-9][0-9])(?P<zonem>[0-9][0-9])'
        br'"')
# Literal jest no longer used; kept dla backward compatibility.
Literal = re.compile(br'.*{(?P<size>\d+)}$', re.ASCII)
MapCRLF = re.compile(br'\r\n|\r|\n')
Response_code = re.compile(br'\[(?P<type>[A-Z-]+)( (?P<data>[^\]]*))?\]')
Untagged_response = re.compile(br'\* (?P<type>[A-Z-]+)( (?P<data>.*))?')
# Untagged_status jest no longer used; kept dla backward compatibility
Untagged_status = re.compile(
    br'\* (?P<data>\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?', re.ASCII)
# We compile these w _mode_xxx.
_Literal = br'.*{(?P<size>\d+)}$'
_Untagged_status = br'\* (?P<data>\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?'



klasa IMAP4:

    """IMAP4 client class.

    Instantiate with: IMAP4([host[, port]])

            host - host's name (default: localhost);
            port - port number (default: standard IMAP4 port).

    All IMAP4rev1 commands are supported by methods of the same
    name (in lower-case).

    All arguments to commands are converted to strings, wyjąwszy for
    AUTHENTICATE, oraz the last argument to APPEND which jest dalejed as
    an IMAP4 literal.  If necessary (the string contains any
    non-printing characters albo white-space oraz isn't enclosed with
    either parentheses albo double quotes) each string jest quoted.
    However, the 'password' argument to the LOGIN command jest always
    quoted.  If you want to avoid having an argument string quoted
    (eg: the 'flags' argument to STORE) then enclose the string w
    parentheses (eg: "(\Deleted)").

    Each command returns a tuple: (type, [data, ...]) where 'type'
    jest usually 'OK' albo 'NO', oraz 'data' jest either the text z the
    tagged response, albo untagged results z command. Each 'data'
    jest either a string, albo a tuple. If a tuple, then the first part
    jest the header of the response, oraz the second part contains
    the data (ie: 'literal' value).

    Errors podnieś the exception klasa <instance>.error("<reason>").
    IMAP4 server errors podnieś <instance>.abort("<reason>"),
    which jest a sub-class of 'error'. Mailbox status changes
    z READ-WRITE to READ-ONLY podnieś the exception class
    <instance>.readonly("<reason>"), which jest a sub-class of 'abort'.

    "error" exceptions imply a program error.
    "abort" exceptions imply the connection should be reset, oraz
            the command re-tried.
    "readonly" exceptions imply the command should be re-tried.

    Note: to use this module, you must read the RFCs pertaining to the
    IMAP4 protocol, jako the semantics of the arguments to each IMAP4
    command are left to the invoker, nie to mention the results. Also,
    most IMAP servers implement a sub-set of the commands available here.
    """

    klasa error(Exception): dalej    # Logical errors - debug required
    klasa abort(error): dalej        # Service errors - close oraz retry
    klasa readonly(abort): dalej     # Mailbox status changed to READ-ONLY

    def __init__(self, host='', port=IMAP4_PORT):
        self.debug = Debug
        self.state = 'LOGOUT'
        self.literal = Nic             # A literal argument to a command
        self.tagged_commands = {}       # Tagged commands awaiting response
        self.untagged_responses = {}    # {typ: [data, ...], ...}
        self.continuation_response = '' # Last continuation response
        self.is_readonly = Nieprawda        # READ-ONLY desired state
        self.tagnum = 0
        self._tls_established = Nieprawda
        self._mode_ascii()

        # Open socket to server.

        self.open(host, port)

        spróbuj:
            self._connect()
        wyjąwszy Exception:
            spróbuj:
                self.shutdown()
            wyjąwszy OSError:
                dalej
            podnieś

    def _mode_ascii(self):
        self.utf8_enabled = Nieprawda
        self._encoding = 'ascii'
        self.Literal = re.compile(_Literal, re.ASCII)
        self.Untagged_status = re.compile(_Untagged_status, re.ASCII)


    def _mode_utf8(self):
        self.utf8_enabled = Prawda
        self._encoding = 'utf-8'
        self.Literal = re.compile(_Literal)
        self.Untagged_status = re.compile(_Untagged_status)


    def _connect(self):
        # Create unique tag dla this session,
        # oraz compile tagged response matcher.

        self.tagpre = Int2AP(random.randint(4096, 65535))
        self.tagre = re.compile(br'(?P<tag>'
                        + self.tagpre
                        + br'\d+) (?P<type>[A-Z]+) (?P<data>.*)', re.ASCII)

        # Get server welcome message,
        # request oraz store CAPABILITY response.

        jeżeli __debug__:
            self._cmd_log_len = 10
            self._cmd_log_idx = 0
            self._cmd_log = {}           # Last `_cmd_log_len' interactions
            jeżeli self.debug >= 1:
                self._mesg('imaplib version %s' % __version__)
                self._mesg('new IMAP4 connection, tag=%s' % self.tagpre)

        self.welcome = self._get_response()
        jeżeli 'PREAUTH' w self.untagged_responses:
            self.state = 'AUTH'
        albo_inaczej 'OK' w self.untagged_responses:
            self.state = 'NONAUTH'
        inaczej:
            podnieś self.error(self.welcome)

        self._get_capabilities()
        jeżeli __debug__:
            jeżeli self.debug >= 3:
                self._mesg('CAPABILITIES: %r' % (self.capabilities,))

        dla version w AllowedVersions:
            jeżeli nie version w self.capabilities:
                kontynuuj
            self.PROTOCOL_VERSION = version
            zwróć

        podnieś self.error('server nie IMAP4 compliant')


    def __getattr__(self, attr):
        #       Allow UPPERCASE variants of IMAP4 command methods.
        jeżeli attr w Commands:
            zwróć getattr(self, attr.lower())
        podnieś AttributeError("Unknown IMAP4 command: '%s'" % attr)

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        spróbuj:
            self.logout()
        wyjąwszy OSError:
            dalej


    #       Overridable methods


    def _create_socket(self):
        zwróć socket.create_connection((self.host, self.port))

    def open(self, host = '', port = IMAP4_PORT):
        """Setup connection to remote server on "host:port"
            (default: localhost:standard IMAP4 port).
        This connection will be used by the routines:
            read, readline, send, shutdown.
        """
        self.host = host
        self.port = port
        self.sock = self._create_socket()
        self.file = self.sock.makefile('rb')


    def read(self, size):
        """Read 'size' bytes z remote."""
        zwróć self.file.read(size)


    def readline(self):
        """Read line z remote."""
        line = self.file.readline(_MAXLINE + 1)
        jeżeli len(line) > _MAXLINE:
            podnieś self.error("got more than %d bytes" % _MAXLINE)
        zwróć line


    def send(self, data):
        """Send data to remote."""
        self.sock.sendall(data)


    def shutdown(self):
        """Close I/O established w "open"."""
        self.file.close()
        spróbuj:
            self.sock.shutdown(socket.SHUT_RDWR)
        wyjąwszy OSError jako e:
            # The server might already have closed the connection
            jeżeli e.errno != errno.ENOTCONN:
                podnieś
        w_końcu:
            self.sock.close()


    def socket(self):
        """Return socket instance used to connect to IMAP4 server.

        socket = <instance>.socket()
        """
        zwróć self.sock



    #       Utility methods


    def recent(self):
        """Return most recent 'RECENT' responses jeżeli any exist,
        inaczej prompt server dla an update using the 'NOOP' command.

        (typ, [data]) = <instance>.recent()

        'data' jest Nic jeżeli no new messages,
        inaczej list of RECENT responses, most recent last.
        """
        name = 'RECENT'
        typ, dat = self._untagged_response('OK', [Nic], name)
        jeżeli dat[-1]:
            zwróć typ, dat
        typ, dat = self.noop()  # Prod server dla response
        zwróć self._untagged_response(typ, dat, name)


    def response(self, code):
        """Return data dla response 'code' jeżeli received, albo Nic.

        Old value dla response 'code' jest cleared.

        (code, [data]) = <instance>.response(code)
        """
        zwróć self._untagged_response(code, [Nic], code.upper())



    #       IMAP4 commands


    def append(self, mailbox, flags, date_time, message):
        """Append message to named mailbox.

        (typ, [data]) = <instance>.append(mailbox, flags, date_time, message)

                All args wyjąwszy `message' can be Nic.
        """
        name = 'APPEND'
        jeżeli nie mailbox:
            mailbox = 'INBOX'
        jeżeli flags:
            jeżeli (flags[0],flags[-1]) != ('(',')'):
                flags = '(%s)' % flags
        inaczej:
            flags = Nic
        jeżeli date_time:
            date_time = Time2Internaldate(date_time)
        inaczej:
            date_time = Nic
        literal = MapCRLF.sub(CRLF, message)
        jeżeli self.utf8_enabled:
            literal = b'UTF8 (' + literal + b')'
        self.literal = literal
        zwróć self._simple_command(name, mailbox, flags, date_time)


    def authenticate(self, mechanism, authobject):
        """Authenticate command - requires response processing.

        'mechanism' specifies which authentication mechanism jest to
        be used - it must appear w <instance>.capabilities w the
        form AUTH=<mechanism>.

        'authobject' must be a callable object:

                data = authobject(response)

        It will be called to process server continuation responses; the
        response argument it jest dalejed will be a bytes.  It should zwróć bytes
        data that will be base64 encoded oraz sent to the server.  It should
        zwróć Nic jeżeli the client abort response '*' should be sent instead.
        """
        mech = mechanism.upper()
        # XXX: shouldn't this code be removed, nie commented out?
        #cap = 'AUTH=%s' % mech
        #jeżeli nie cap w self.capabilities:       # Let the server decide!
        #    podnieś self.error("Server doesn't allow %s authentication." % mech)
        self.literal = _Authenticator(authobject).process
        typ, dat = self._simple_command('AUTHENTICATE', mech)
        jeżeli typ != 'OK':
            podnieś self.error(dat[-1])
        self.state = 'AUTH'
        zwróć typ, dat


    def capability(self):
        """(typ, [data]) = <instance>.capability()
        Fetch capabilities list z server."""

        name = 'CAPABILITY'
        typ, dat = self._simple_command(name)
        zwróć self._untagged_response(typ, dat, name)


    def check(self):
        """Checkpoint mailbox on server.

        (typ, [data]) = <instance>.check()
        """
        zwróć self._simple_command('CHECK')


    def close(self):
        """Close currently selected mailbox.

        Deleted messages are removed z writable mailbox.
        This jest the recommended command before 'LOGOUT'.

        (typ, [data]) = <instance>.close()
        """
        spróbuj:
            typ, dat = self._simple_command('CLOSE')
        w_końcu:
            self.state = 'AUTH'
        zwróć typ, dat


    def copy(self, message_set, new_mailbox):
        """Copy 'message_set' messages onto end of 'new_mailbox'.

        (typ, [data]) = <instance>.copy(message_set, new_mailbox)
        """
        zwróć self._simple_command('COPY', message_set, new_mailbox)


    def create(self, mailbox):
        """Create new mailbox.

        (typ, [data]) = <instance>.create(mailbox)
        """
        zwróć self._simple_command('CREATE', mailbox)


    def delete(self, mailbox):
        """Delete old mailbox.

        (typ, [data]) = <instance>.delete(mailbox)
        """
        zwróć self._simple_command('DELETE', mailbox)

    def deleteacl(self, mailbox, who):
        """Delete the ACLs (remove any rights) set dla who on mailbox.

        (typ, [data]) = <instance>.deleteacl(mailbox, who)
        """
        zwróć self._simple_command('DELETEACL', mailbox, who)

    def enable(self, capability):
        """Send an RFC5161 enable string to the server.

        (typ, [data]) = <intance>.enable(capability)
        """
        jeżeli 'ENABLE' nie w self.capabilities:
            podnieś IMAP4.error("Server does nie support ENABLE")
        typ, data = self._simple_command('ENABLE', capability)
        jeżeli typ == 'OK' oraz 'UTF8=ACCEPT' w capability.upper():
            self._mode_utf8()
        zwróć typ, data

    def expunge(self):
        """Permanently remove deleted items z selected mailbox.

        Generates 'EXPUNGE' response dla each deleted message.

        (typ, [data]) = <instance>.expunge()

        'data' jest list of 'EXPUNGE'd message numbers w order received.
        """
        name = 'EXPUNGE'
        typ, dat = self._simple_command(name)
        zwróć self._untagged_response(typ, dat, name)


    def fetch(self, message_set, message_parts):
        """Fetch (parts of) messages.

        (typ, [data, ...]) = <instance>.fetch(message_set, message_parts)

        'message_parts' should be a string of selected parts
        enclosed w parentheses, eg: "(UID BODY[TEXT])".

        'data' are tuples of message part envelope oraz data.
        """
        name = 'FETCH'
        typ, dat = self._simple_command(name, message_set, message_parts)
        zwróć self._untagged_response(typ, dat, name)


    def getacl(self, mailbox):
        """Get the ACLs dla a mailbox.

        (typ, [data]) = <instance>.getacl(mailbox)
        """
        typ, dat = self._simple_command('GETACL', mailbox)
        zwróć self._untagged_response(typ, dat, 'ACL')


    def getannotation(self, mailbox, entry, attribute):
        """(typ, [data]) = <instance>.getannotation(mailbox, entry, attribute)
        Retrieve ANNOTATIONs."""

        typ, dat = self._simple_command('GETANNOTATION', mailbox, entry, attribute)
        zwróć self._untagged_response(typ, dat, 'ANNOTATION')


    def getquota(self, root):
        """Get the quota root's resource usage oraz limits.

        Part of the IMAP4 QUOTA extension defined w rfc2087.

        (typ, [data]) = <instance>.getquota(root)
        """
        typ, dat = self._simple_command('GETQUOTA', root)
        zwróć self._untagged_response(typ, dat, 'QUOTA')


    def getquotaroot(self, mailbox):
        """Get the list of quota roots dla the named mailbox.

        (typ, [[QUOTAROOT responses...], [QUOTA responses]]) = <instance>.getquotaroot(mailbox)
        """
        typ, dat = self._simple_command('GETQUOTAROOT', mailbox)
        typ, quota = self._untagged_response(typ, dat, 'QUOTA')
        typ, quotaroot = self._untagged_response(typ, dat, 'QUOTAROOT')
        zwróć typ, [quotaroot, quota]


    def list(self, directory='""', pattern='*'):
        """List mailbox names w directory matching pattern.

        (typ, [data]) = <instance>.list(directory='""', pattern='*')

        'data' jest list of LIST responses.
        """
        name = 'LIST'
        typ, dat = self._simple_command(name, directory, pattern)
        zwróć self._untagged_response(typ, dat, name)


    def login(self, user, dalejword):
        """Identify client using plaintext dalejword.

        (typ, [data]) = <instance>.login(user, dalejword)

        NB: 'password' will be quoted.
        """
        typ, dat = self._simple_command('LOGIN', user, self._quote(password))
        jeżeli typ != 'OK':
            podnieś self.error(dat[-1])
        self.state = 'AUTH'
        zwróć typ, dat


    def login_cram_md5(self, user, dalejword):
        """ Force use of CRAM-MD5 authentication.

        (typ, [data]) = <instance>.login_cram_md5(user, dalejword)
        """
        self.user, self.password = user, dalejword
        zwróć self.authenticate('CRAM-MD5', self._CRAM_MD5_AUTH)


    def _CRAM_MD5_AUTH(self, challenge):
        """ Authobject to use przy CRAM-MD5 authentication. """
        zaimportuj hmac
        pwd = (self.password.encode('utf-8') jeżeli isinstance(self.password, str)
                                             inaczej self.password)
        zwróć self.user + " " + hmac.HMAC(pwd, challenge, 'md5').hexdigest()


    def logout(self):
        """Shutdown connection to server.

        (typ, [data]) = <instance>.logout()

        Returns server 'BYE' response.
        """
        self.state = 'LOGOUT'
        spróbuj: typ, dat = self._simple_command('LOGOUT')
        wyjąwszy: typ, dat = 'NO', ['%s: %s' % sys.exc_info()[:2]]
        self.shutdown()
        jeżeli 'BYE' w self.untagged_responses:
            zwróć 'BYE', self.untagged_responses['BYE']
        zwróć typ, dat


    def lsub(self, directory='""', pattern='*'):
        """List 'subscribed' mailbox names w directory matching pattern.

        (typ, [data, ...]) = <instance>.lsub(directory='""', pattern='*')

        'data' are tuples of message part envelope oraz data.
        """
        name = 'LSUB'
        typ, dat = self._simple_command(name, directory, pattern)
        zwróć self._untagged_response(typ, dat, name)

    def myrights(self, mailbox):
        """Show my ACLs dla a mailbox (i.e. the rights that I have on mailbox).

        (typ, [data]) = <instance>.myrights(mailbox)
        """
        typ,dat = self._simple_command('MYRIGHTS', mailbox)
        zwróć self._untagged_response(typ, dat, 'MYRIGHTS')

    def namespace(self):
        """ Returns IMAP namespaces ala rfc2342

        (typ, [data, ...]) = <instance>.namespace()
        """
        name = 'NAMESPACE'
        typ, dat = self._simple_command(name)
        zwróć self._untagged_response(typ, dat, name)


    def noop(self):
        """Send NOOP command.

        (typ, [data]) = <instance>.noop()
        """
        jeżeli __debug__:
            jeżeli self.debug >= 3:
                self._dump_ur(self.untagged_responses)
        zwróć self._simple_command('NOOP')


    def partial(self, message_num, message_part, start, length):
        """Fetch truncated part of a message.

        (typ, [data, ...]) = <instance>.partial(message_num, message_part, start, length)

        'data' jest tuple of message part envelope oraz data.
        """
        name = 'PARTIAL'
        typ, dat = self._simple_command(name, message_num, message_part, start, length)
        zwróć self._untagged_response(typ, dat, 'FETCH')


    def proxyauth(self, user):
        """Assume authentication jako "user".

        Allows an authorised administrator to proxy into any user's
        mailbox.

        (typ, [data]) = <instance>.proxyauth(user)
        """

        name = 'PROXYAUTH'
        zwróć self._simple_command('PROXYAUTH', user)


    def rename(self, oldmailbox, newmailbox):
        """Rename old mailbox name to new.

        (typ, [data]) = <instance>.rename(oldmailbox, newmailbox)
        """
        zwróć self._simple_command('RENAME', oldmailbox, newmailbox)


    def search(self, charset, *criteria):
        """Search mailbox dla matching messages.

        (typ, [data]) = <instance>.search(charset, criterion, ...)

        'data' jest space separated list of matching message numbers.
        If UTF8 jest enabled, charset MUST be Nic.
        """
        name = 'SEARCH'
        jeżeli charset:
            jeżeli self.utf8_enabled:
                podnieś IMAP4.error("Non-Nic charset nie valid w UTF8 mode")
            typ, dat = self._simple_command(name, 'CHARSET', charset, *criteria)
        inaczej:
            typ, dat = self._simple_command(name, *criteria)
        zwróć self._untagged_response(typ, dat, name)


    def select(self, mailbox='INBOX', readonly=Nieprawda):
        """Select a mailbox.

        Flush all untagged responses.

        (typ, [data]) = <instance>.select(mailbox='INBOX', readonly=Nieprawda)

        'data' jest count of messages w mailbox ('EXISTS' response).

        Mandated responses are ('FLAGS', 'EXISTS', 'RECENT', 'UIDVALIDITY'), so
        other responses should be obtained via <instance>.response('FLAGS') etc.
        """
        self.untagged_responses = {}    # Flush old responses.
        self.is_readonly = readonly
        jeżeli readonly:
            name = 'EXAMINE'
        inaczej:
            name = 'SELECT'
        typ, dat = self._simple_command(name, mailbox)
        jeżeli typ != 'OK':
            self.state = 'AUTH'     # Might have been 'SELECTED'
            zwróć typ, dat
        self.state = 'SELECTED'
        jeżeli 'READ-ONLY' w self.untagged_responses \
                oraz nie readonly:
            jeżeli __debug__:
                jeżeli self.debug >= 1:
                    self._dump_ur(self.untagged_responses)
            podnieś self.readonly('%s jest nie writable' % mailbox)
        zwróć typ, self.untagged_responses.get('EXISTS', [Nic])


    def setacl(self, mailbox, who, what):
        """Set a mailbox acl.

        (typ, [data]) = <instance>.setacl(mailbox, who, what)
        """
        zwróć self._simple_command('SETACL', mailbox, who, what)


    def setannotation(self, *args):
        """(typ, [data]) = <instance>.setannotation(mailbox[, entry, attribute]+)
        Set ANNOTATIONs."""

        typ, dat = self._simple_command('SETANNOTATION', *args)
        zwróć self._untagged_response(typ, dat, 'ANNOTATION')


    def setquota(self, root, limits):
        """Set the quota root's resource limits.

        (typ, [data]) = <instance>.setquota(root, limits)
        """
        typ, dat = self._simple_command('SETQUOTA', root, limits)
        zwróć self._untagged_response(typ, dat, 'QUOTA')


    def sort(self, sort_criteria, charset, *search_criteria):
        """IMAP4rev1 extension SORT command.

        (typ, [data]) = <instance>.sort(sort_criteria, charset, search_criteria, ...)
        """
        name = 'SORT'
        #jeżeli nie name w self.capabilities:      # Let the server decide!
        #       podnieś self.error('unimplemented extension command: %s' % name)
        jeżeli (sort_criteria[0],sort_criteria[-1]) != ('(',')'):
            sort_criteria = '(%s)' % sort_criteria
        typ, dat = self._simple_command(name, sort_criteria, charset, *search_criteria)
        zwróć self._untagged_response(typ, dat, name)


    def starttls(self, ssl_context=Nic):
        name = 'STARTTLS'
        jeżeli nie HAVE_SSL:
            podnieś self.error('SSL support missing')
        jeżeli self._tls_established:
            podnieś self.abort('TLS session already established')
        jeżeli name nie w self.capabilities:
            podnieś self.abort('TLS nie supported by server')
        # Generate a default SSL context jeżeli none was dalejed.
        jeżeli ssl_context jest Nic:
            ssl_context = ssl._create_stdlib_context()
        typ, dat = self._simple_command(name)
        jeżeli typ == 'OK':
            self.sock = ssl_context.wrap_socket(self.sock,
                                                server_hostname=self.host)
            self.file = self.sock.makefile('rb')
            self._tls_established = Prawda
            self._get_capabilities()
        inaczej:
            podnieś self.error("Couldn't establish TLS session")
        zwróć self._untagged_response(typ, dat, name)


    def status(self, mailbox, names):
        """Request named status conditions dla mailbox.

        (typ, [data]) = <instance>.status(mailbox, names)
        """
        name = 'STATUS'
        #jeżeli self.PROTOCOL_VERSION == 'IMAP4':   # Let the server decide!
        #    podnieś self.error('%s unimplemented w IMAP4 (obtain IMAP4rev1 server, albo re-code)' % name)
        typ, dat = self._simple_command(name, mailbox, names)
        zwróć self._untagged_response(typ, dat, name)


    def store(self, message_set, command, flags):
        """Alters flag dispositions dla messages w mailbox.

        (typ, [data]) = <instance>.store(message_set, command, flags)
        """
        jeżeli (flags[0],flags[-1]) != ('(',')'):
            flags = '(%s)' % flags  # Avoid quoting the flags
        typ, dat = self._simple_command('STORE', message_set, command, flags)
        zwróć self._untagged_response(typ, dat, 'FETCH')


    def subscribe(self, mailbox):
        """Subscribe to new mailbox.

        (typ, [data]) = <instance>.subscribe(mailbox)
        """
        zwróć self._simple_command('SUBSCRIBE', mailbox)


    def thread(self, threading_algorithm, charset, *search_criteria):
        """IMAPrev1 extension THREAD command.

        (type, [data]) = <instance>.thread(threading_algorithm, charset, search_criteria, ...)
        """
        name = 'THREAD'
        typ, dat = self._simple_command(name, threading_algorithm, charset, *search_criteria)
        zwróć self._untagged_response(typ, dat, name)


    def uid(self, command, *args):
        """Execute "command arg ..." przy messages identified by UID,
                rather than message number.

        (typ, [data]) = <instance>.uid(command, arg1, arg2, ...)

        Returns response appropriate to 'command'.
        """
        command = command.upper()
        jeżeli nie command w Commands:
            podnieś self.error("Unknown IMAP4 UID command: %s" % command)
        jeżeli self.state nie w Commands[command]:
            podnieś self.error("command %s illegal w state %s, "
                             "only allowed w states %s" %
                             (command, self.state,
                              ', '.join(Commands[command])))
        name = 'UID'
        typ, dat = self._simple_command(name, command, *args)
        jeżeli command w ('SEARCH', 'SORT', 'THREAD'):
            name = command
        inaczej:
            name = 'FETCH'
        zwróć self._untagged_response(typ, dat, name)


    def unsubscribe(self, mailbox):
        """Unsubscribe z old mailbox.

        (typ, [data]) = <instance>.unsubscribe(mailbox)
        """
        zwróć self._simple_command('UNSUBSCRIBE', mailbox)


    def xatom(self, name, *args):
        """Allow simple extension commands
                notified by server w CAPABILITY response.

        Assumes command jest legal w current state.

        (typ, [data]) = <instance>.xatom(name, arg, ...)

        Returns response appropriate to extension command `name'.
        """
        name = name.upper()
        #jeżeli nie name w self.capabilities:      # Let the server decide!
        #    podnieś self.error('unknown extension command: %s' % name)
        jeżeli nie name w Commands:
            Commands[name] = (self.state,)
        zwróć self._simple_command(name, *args)



    #       Private methods


    def _append_untagged(self, typ, dat):
        jeżeli dat jest Nic:
            dat = b''
        ur = self.untagged_responses
        jeżeli __debug__:
            jeżeli self.debug >= 5:
                self._mesg('untagged_responses[%s] %s += ["%r"]' %
                        (typ, len(ur.get(typ,'')), dat))
        jeżeli typ w ur:
            ur[typ].append(dat)
        inaczej:
            ur[typ] = [dat]


    def _check_bye(self):
        bye = self.untagged_responses.get('BYE')
        jeżeli bye:
            podnieś self.abort(bye[-1].decode(self._encoding, 'replace'))


    def _command(self, name, *args):

        jeżeli self.state nie w Commands[name]:
            self.literal = Nic
            podnieś self.error("command %s illegal w state %s, "
                             "only allowed w states %s" %
                             (name, self.state,
                              ', '.join(Commands[name])))

        dla typ w ('OK', 'NO', 'BAD'):
            jeżeli typ w self.untagged_responses:
                usuń self.untagged_responses[typ]

        jeżeli 'READ-ONLY' w self.untagged_responses \
        oraz nie self.is_readonly:
            podnieś self.readonly('mailbox status changed to READ-ONLY')

        tag = self._new_tag()
        name = bytes(name, self._encoding)
        data = tag + b' ' + name
        dla arg w args:
            jeżeli arg jest Nic: kontynuuj
            jeżeli isinstance(arg, str):
                arg = bytes(arg, self._encoding)
            data = data + b' ' + arg

        literal = self.literal
        jeżeli literal jest nie Nic:
            self.literal = Nic
            jeżeli type(literal) jest type(self._command):
                literator = literal
            inaczej:
                literator = Nic
                data = data + bytes(' {%s}' % len(literal), self._encoding)

        jeżeli __debug__:
            jeżeli self.debug >= 4:
                self._mesg('> %r' % data)
            inaczej:
                self._log('> %r' % data)

        spróbuj:
            self.send(data + CRLF)
        wyjąwszy OSError jako val:
            podnieś self.abort('socket error: %s' % val)

        jeżeli literal jest Nic:
            zwróć tag

        dopóki 1:
            # Wait dla continuation response

            dopóki self._get_response():
                jeżeli self.tagged_commands[tag]:   # BAD/NO?
                    zwróć tag

            # Send literal

            jeżeli literator:
                literal = literator(self.continuation_response)

            jeżeli __debug__:
                jeżeli self.debug >= 4:
                    self._mesg('write literal size %s' % len(literal))

            spróbuj:
                self.send(literal)
                self.send(CRLF)
            wyjąwszy OSError jako val:
                podnieś self.abort('socket error: %s' % val)

            jeżeli nie literator:
                przerwij

        zwróć tag


    def _command_complete(self, name, tag):
        # BYE jest expected after LOGOUT
        jeżeli name != 'LOGOUT':
            self._check_bye()
        spróbuj:
            typ, data = self._get_tagged_response(tag)
        wyjąwszy self.abort jako val:
            podnieś self.abort('command: %s => %s' % (name, val))
        wyjąwszy self.error jako val:
            podnieś self.error('command: %s => %s' % (name, val))
        jeżeli name != 'LOGOUT':
            self._check_bye()
        jeżeli typ == 'BAD':
            podnieś self.error('%s command error: %s %s' % (name, typ, data))
        zwróć typ, data


    def _get_capabilities(self):
        typ, dat = self.capability()
        jeżeli dat == [Nic]:
            podnieś self.error('no CAPABILITY response z server')
        dat = str(dat[-1], self._encoding)
        dat = dat.upper()
        self.capabilities = tuple(dat.split())


    def _get_response(self):

        # Read response oraz store.
        #
        # Returns Nic dla continuation responses,
        # otherwise first response line received.

        resp = self._get_line()

        # Command completion response?

        jeżeli self._match(self.tagre, resp):
            tag = self.mo.group('tag')
            jeżeli nie tag w self.tagged_commands:
                podnieś self.abort('unexpected tagged response: %r' % resp)

            typ = self.mo.group('type')
            typ = str(typ, self._encoding)
            dat = self.mo.group('data')
            self.tagged_commands[tag] = (typ, [dat])
        inaczej:
            dat2 = Nic

            # '*' (untagged) responses?

            jeżeli nie self._match(Untagged_response, resp):
                jeżeli self._match(self.Untagged_status, resp):
                    dat2 = self.mo.group('data2')

            jeżeli self.mo jest Nic:
                # Only other possibility jest '+' (continuation) response...

                jeżeli self._match(Continuation, resp):
                    self.continuation_response = self.mo.group('data')
                    zwróć Nic     # NB: indicates continuation

                podnieś self.abort("unexpected response: %r" % resp)

            typ = self.mo.group('type')
            typ = str(typ, self._encoding)
            dat = self.mo.group('data')
            jeżeli dat jest Nic: dat = b''        # Null untagged response
            jeżeli dat2: dat = dat + b' ' + dat2

            # Is there a literal to come?

            dopóki self._match(self.Literal, dat):

                # Read literal direct z connection.

                size = int(self.mo.group('size'))
                jeżeli __debug__:
                    jeżeli self.debug >= 4:
                        self._mesg('read literal size %s' % size)
                data = self.read(size)

                # Store response przy literal jako tuple

                self._append_untagged(typ, (dat, data))

                # Read trailer - possibly containing another literal

                dat = self._get_line()

            self._append_untagged(typ, dat)

        # Bracketed response information?

        jeżeli typ w ('OK', 'NO', 'BAD') oraz self._match(Response_code, dat):
            typ = self.mo.group('type')
            typ = str(typ, self._encoding)
            self._append_untagged(typ, self.mo.group('data'))

        jeżeli __debug__:
            jeżeli self.debug >= 1 oraz typ w ('NO', 'BAD', 'BYE'):
                self._mesg('%s response: %r' % (typ, dat))

        zwróć resp


    def _get_tagged_response(self, tag):

        dopóki 1:
            result = self.tagged_commands[tag]
            jeżeli result jest nie Nic:
                usuń self.tagged_commands[tag]
                zwróć result

            # If we've seen a BYE at this point, the socket will be
            # closed, so report the BYE now.

            self._check_bye()

            # Some have reported "unexpected response" exceptions.
            # Note that ignoring them here causes loops.
            # Instead, send me details of the unexpected response oraz
            # I'll update the code w `_get_response()'.

            spróbuj:
                self._get_response()
            wyjąwszy self.abort jako val:
                jeżeli __debug__:
                    jeżeli self.debug >= 1:
                        self.print_log()
                podnieś


    def _get_line(self):

        line = self.readline()
        jeżeli nie line:
            podnieś self.abort('socket error: EOF')

        # Protocol mandates all lines terminated by CRLF
        jeżeli nie line.endswith(b'\r\n'):
            podnieś self.abort('socket error: unterminated line: %r' % line)

        line = line[:-2]
        jeżeli __debug__:
            jeżeli self.debug >= 4:
                self._mesg('< %r' % line)
            inaczej:
                self._log('< %r' % line)
        zwróć line


    def _match(self, cre, s):

        # Run compiled regular expression match method on 's'.
        # Save result, zwróć success.

        self.mo = cre.match(s)
        jeżeli __debug__:
            jeżeli self.mo jest nie Nic oraz self.debug >= 5:
                self._mesg("\tmatched r'%r' => %r" % (cre.pattern, self.mo.groups()))
        zwróć self.mo jest nie Nic


    def _new_tag(self):

        tag = self.tagpre + bytes(str(self.tagnum), self._encoding)
        self.tagnum = self.tagnum + 1
        self.tagged_commands[tag] = Nic
        zwróć tag


    def _quote(self, arg):

        arg = arg.replace('\\', '\\\\')
        arg = arg.replace('"', '\\"')

        zwróć '"' + arg + '"'


    def _simple_command(self, name, *args):

        zwróć self._command_complete(name, self._command(name, *args))


    def _untagged_response(self, typ, dat, name):
        jeżeli typ == 'NO':
            zwróć typ, dat
        jeżeli nie name w self.untagged_responses:
            zwróć typ, [Nic]
        data = self.untagged_responses.pop(name)
        jeżeli __debug__:
            jeżeli self.debug >= 5:
                self._mesg('untagged_responses[%s] => %s' % (name, data))
        zwróć typ, data


    jeżeli __debug__:

        def _mesg(self, s, secs=Nic):
            jeżeli secs jest Nic:
                secs = time.time()
            tm = time.strftime('%M:%S', time.localtime(secs))
            sys.stderr.write('  %s.%02d %s\n' % (tm, (secs*100)%100, s))
            sys.stderr.flush()

        def _dump_ur(self, dict):
            # Dump untagged responses (in `dict').
            l = dict.items()
            jeżeli nie l: zwróć
            t = '\n\t\t'
            l = map(lambda x:'%s: "%s"' % (x[0], x[1][0] oraz '" "'.join(x[1]) albo ''), l)
            self._mesg('untagged responses dump:%s%s' % (t, t.join(l)))

        def _log(self, line):
            # Keep log of last `_cmd_log_len' interactions dla debugging.
            self._cmd_log[self._cmd_log_idx] = (line, time.time())
            self._cmd_log_idx += 1
            jeżeli self._cmd_log_idx >= self._cmd_log_len:
                self._cmd_log_idx = 0

        def print_log(self):
            self._mesg('last %d IMAP4 interactions:' % len(self._cmd_log))
            i, n = self._cmd_log_idx, self._cmd_log_len
            dopóki n:
                spróbuj:
                    self._mesg(*self._cmd_log[i])
                wyjąwszy:
                    dalej
                i += 1
                jeżeli i >= self._cmd_log_len:
                    i = 0
                n -= 1


jeżeli HAVE_SSL:

    klasa IMAP4_SSL(IMAP4):

        """IMAP4 client klasa over SSL connection

        Instantiate with: IMAP4_SSL([host[, port[, keyfile[, certfile[, ssl_context]]]]])

                host - host's name (default: localhost);
                port - port number (default: standard IMAP4 SSL port);
                keyfile - PEM formatted file that contains your private key (default: Nic);
                certfile - PEM formatted certificate chain file (default: Nic);
                ssl_context - a SSLContext object that contains your certificate chain
                              oraz private key (default: Nic)
                Note: jeżeli ssl_context jest provided, then parameters keyfile albo
                certfile should nie be set otherwise ValueError jest podnieśd.

        dla more documentation see the docstring of the parent klasa IMAP4.
        """


        def __init__(self, host='', port=IMAP4_SSL_PORT, keyfile=Nic,
                     certfile=Nic, ssl_context=Nic):
            jeżeli ssl_context jest nie Nic oraz keyfile jest nie Nic:
                podnieś ValueError("ssl_context oraz keyfile arguments are mutually "
                                 "exclusive")
            jeżeli ssl_context jest nie Nic oraz certfile jest nie Nic:
                podnieś ValueError("ssl_context oraz certfile arguments are mutually "
                                 "exclusive")

            self.keyfile = keyfile
            self.certfile = certfile
            jeżeli ssl_context jest Nic:
                ssl_context = ssl._create_stdlib_context(certfile=certfile,
                                                         keyfile=keyfile)
            self.ssl_context = ssl_context
            IMAP4.__init__(self, host, port)

        def _create_socket(self):
            sock = IMAP4._create_socket(self)
            zwróć self.ssl_context.wrap_socket(sock,
                                                server_hostname=self.host)

        def open(self, host='', port=IMAP4_SSL_PORT):
            """Setup connection to remote server on "host:port".
                (default: localhost:standard IMAP4 SSL port).
            This connection will be used by the routines:
                read, readline, send, shutdown.
            """
            IMAP4.open(self, host, port)

    __all__.append("IMAP4_SSL")


klasa IMAP4_stream(IMAP4):

    """IMAP4 client klasa over a stream

    Instantiate with: IMAP4_stream(command)

            "command" - a string that can be dalejed to subprocess.Popen()

    dla more documentation see the docstring of the parent klasa IMAP4.
    """


    def __init__(self, command):
        self.command = command
        IMAP4.__init__(self)


    def open(self, host = Nic, port = Nic):
        """Setup a stream connection.
        This connection will be used by the routines:
            read, readline, send, shutdown.
        """
        self.host = Nic        # For compatibility przy parent class
        self.port = Nic
        self.sock = Nic
        self.file = Nic
        self.process = subprocess.Popen(self.command,
            bufsize=DEFAULT_BUFFER_SIZE,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            shell=Prawda, close_fds=Prawda)
        self.writefile = self.process.stdin
        self.readfile = self.process.stdout

    def read(self, size):
        """Read 'size' bytes z remote."""
        zwróć self.readfile.read(size)


    def readline(self):
        """Read line z remote."""
        zwróć self.readfile.readline()


    def send(self, data):
        """Send data to remote."""
        self.writefile.write(data)
        self.writefile.flush()


    def shutdown(self):
        """Close I/O established w "open"."""
        self.readfile.close()
        self.writefile.close()
        self.process.wait()



klasa _Authenticator:

    """Private klasa to provide en/decoding
            dla base64-based authentication conversation.
    """

    def __init__(self, mechinst):
        self.mech = mechinst    # Callable object to provide/process data

    def process(self, data):
        ret = self.mech(self.decode(data))
        jeżeli ret jest Nic:
            zwróć b'*'     # Abort conversation
        zwróć self.encode(ret)

    def encode(self, inp):
        #
        #  Invoke binascii.b2a_base64 iteratively with
        #  short even length buffers, strip the trailing
        #  line feed z the result oraz append.  "Even"
        #  means a number that factors to both 6 oraz 8,
        #  so when it gets to the end of the 8-bit input
        #  there's no partial 6-bit output.
        #
        oup = b''
        jeżeli isinstance(inp, str):
            inp = inp.encode('utf-8')
        dopóki inp:
            jeżeli len(inp) > 48:
                t = inp[:48]
                inp = inp[48:]
            inaczej:
                t = inp
                inp = b''
            e = binascii.b2a_base64(t)
            jeżeli e:
                oup = oup + e[:-1]
        zwróć oup

    def decode(self, inp):
        jeżeli nie inp:
            zwróć b''
        zwróć binascii.a2b_base64(inp)

Months = ' Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')
Mon2num = {s.encode():n+1 dla n, s w enumerate(Months[1:])}

def Internaldate2tuple(resp):
    """Parse an IMAP4 INTERNALDATE string.

    Return corresponding local time.  The zwróć value jest a
    time.struct_time tuple albo Nic jeżeli the string has wrong format.
    """

    mo = InternalDate.match(resp)
    jeżeli nie mo:
        zwróć Nic

    mon = Mon2num[mo.group('mon')]
    zonen = mo.group('zonen')

    day = int(mo.group('day'))
    year = int(mo.group('year'))
    hour = int(mo.group('hour'))
    min = int(mo.group('min'))
    sec = int(mo.group('sec'))
    zoneh = int(mo.group('zoneh'))
    zonem = int(mo.group('zonem'))

    # INTERNALDATE timezone must be subtracted to get UT

    zone = (zoneh*60 + zonem)*60
    jeżeli zonen == b'-':
        zone = -zone

    tt = (year, mon, day, hour, min, sec, -1, -1, -1)
    utc = calendar.timegm(tt) - zone

    zwróć time.localtime(utc)



def Int2AP(num):

    """Convert integer to A-P string representation."""

    val = b''; AP = b'ABCDEFGHIJKLMNOP'
    num = int(abs(num))
    dopóki num:
        num, mod = divmod(num, 16)
        val = AP[mod:mod+1] + val
    zwróć val



def ParseFlags(resp):

    """Convert IMAP4 flags response to python tuple."""

    mo = Flags.match(resp)
    jeżeli nie mo:
        zwróć ()

    zwróć tuple(mo.group('flags').split())


def Time2Internaldate(date_time):

    """Convert date_time to IMAP4 INTERNALDATE representation.

    Return string w form: '"DD-Mmm-YYYY HH:MM:SS +HHMM"'.  The
    date_time argument can be a number (int albo float) representing
    seconds since epoch (as returned by time.time()), a 9-tuple
    representing local time, an instance of time.struct_time (as
    returned by time.localtime()), an aware datetime instance albo a
    double-quoted string.  In the last case, it jest assumed to already
    be w the correct format.
    """
    jeżeli isinstance(date_time, (int, float)):
        dt = datetime.fromtimestamp(date_time,
                                    timezone.utc).astimezone()
    albo_inaczej isinstance(date_time, tuple):
        spróbuj:
            gmtoff = date_time.tm_gmtoff
        wyjąwszy AttributeError:
            jeżeli time.daylight:
                dst = date_time[8]
                jeżeli dst == -1:
                    dst = time.localtime(time.mktime(date_time))[8]
                gmtoff = -(time.timezone, time.altzone)[dst]
            inaczej:
                gmtoff = -time.timezone
        delta = timedelta(seconds=gmtoff)
        dt = datetime(*date_time[:6], tzinfo=timezone(delta))
    albo_inaczej isinstance(date_time, datetime):
        jeżeli date_time.tzinfo jest Nic:
            podnieś ValueError("date_time must be aware")
        dt = date_time
    albo_inaczej isinstance(date_time, str) oraz (date_time[0],date_time[-1]) == ('"','"'):
        zwróć date_time        # Assume w correct format
    inaczej:
        podnieś ValueError("date_time nie of a known type")
    fmt = '"%d-{}-%Y %H:%M:%S %z"'.format(Months[dt.month])
    zwróć dt.strftime(fmt)



jeżeli __name__ == '__main__':

    # To test: invoke either jako 'python imaplib.py [IMAP4_server_hostname]'
    # albo 'python imaplib.py -s "rsh IMAP4_server_hostname exec /etc/rimapd"'
    # to test the IMAP4_stream class

    zaimportuj getopt, getpass

    spróbuj:
        optlist, args = getopt.getopt(sys.argv[1:], 'd:s:')
    wyjąwszy getopt.error jako val:
        optlist, args = (), ()

    stream_command = Nic
    dla opt,val w optlist:
        jeżeli opt == '-d':
            Debug = int(val)
        albo_inaczej opt == '-s':
            stream_command = val
            jeżeli nie args: args = (stream_command,)

    jeżeli nie args: args = ('',)

    host = args[0]

    USER = getpass.getuser()
    PASSWD = getpass.getpass("IMAP dalejword dla %s on %s: " % (USER, host albo "localhost"))

    test_mesg = 'From: %(user)s@localhost%(lf)sSubject: IMAP4 test%(lf)s%(lf)sdata...%(lf)s' % {'user':USER, 'lf':'\n'}
    test_seq1 = (
    ('login', (USER, PASSWD)),
    ('create', ('/tmp/xxx 1',)),
    ('rename', ('/tmp/xxx 1', '/tmp/yyy')),
    ('CREATE', ('/tmp/yyz 2',)),
    ('append', ('/tmp/yyz 2', Nic, Nic, test_mesg)),
    ('list', ('/tmp', 'yy*')),
    ('select', ('/tmp/yyz 2',)),
    ('search', (Nic, 'SUBJECT', 'test')),
    ('fetch', ('1', '(FLAGS INTERNALDATE RFC822)')),
    ('store', ('1', 'FLAGS', '(\Deleted)')),
    ('namespace', ()),
    ('expunge', ()),
    ('recent', ()),
    ('close', ()),
    )

    test_seq2 = (
    ('select', ()),
    ('response',('UIDVALIDITY',)),
    ('uid', ('SEARCH', 'ALL')),
    ('response', ('EXISTS',)),
    ('append', (Nic, Nic, Nic, test_mesg)),
    ('recent', ()),
    ('logout', ()),
    )

    def run(cmd, args):
        M._mesg('%s %s' % (cmd, args))
        typ, dat = getattr(M, cmd)(*args)
        M._mesg('%s => %s %s' % (cmd, typ, dat))
        jeżeli typ == 'NO': podnieś dat[0]
        zwróć dat

    spróbuj:
        jeżeli stream_command:
            M = IMAP4_stream(stream_command)
        inaczej:
            M = IMAP4(host)
        jeżeli M.state == 'AUTH':
            test_seq1 = test_seq1[1:]   # Login nie needed
        M._mesg('PROTOCOL_VERSION = %s' % M.PROTOCOL_VERSION)
        M._mesg('CAPABILITIES = %r' % (M.capabilities,))

        dla cmd,args w test_seq1:
            run(cmd, args)

        dla ml w run('list', ('/tmp/', 'yy%')):
            mo = re.match(r'.*"([^"]+)"$', ml)
            jeżeli mo: path = mo.group(1)
            inaczej: path = ml.split()[-1]
            run('delete', (path,))

        dla cmd,args w test_seq2:
            dat = run(cmd, args)

            jeżeli (cmd,args) != ('uid', ('SEARCH', 'ALL')):
                kontynuuj

            uid = dat[-1].split()
            jeżeli nie uid: kontynuuj
            run('uid', ('FETCH', '%s' % uid[-1],
                    '(FLAGS INTERNALDATE RFC822.SIZE RFC822.HEADER RFC822.TEXT)'))

        print('\nAll tests OK.')

    wyjąwszy:
        print('\nTests failed.')

        jeżeli nie Debug:
            print('''
If you would like to see debugging output,
spróbuj: %s -d5
''' % sys.argv[0])

        podnieś
