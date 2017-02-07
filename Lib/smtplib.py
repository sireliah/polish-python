#! /usr/bin/env python3

'''SMTP/ESMTP client class.

This should follow RFC 821 (SMTP), RFC 1869 (ESMTP), RFC 2554 (SMTP
Authentication) oraz RFC 2487 (Secure SMTP over TLS).

Notes:

Please remember, when doing ESMTP, that the names of the SMTP service
extensions are NOT the same thing jako the option keywords dla the RCPT
and MAIL commands!

Example:

  >>> zaimportuj smtplib
  >>> s=smtplib.SMTP("localhost")
  >>> print(s.help())
  This jest Sendmail version 8.8.4
  Topics:
      HELO    EHLO    MAIL    RCPT    DATA
      RSET    NOOP    QUIT    HELP    VRFY
      EXPN    VERB    ETRN    DSN
  For more info use "HELP <topic>".
  To report bugs w the implementation send email to
      sendmail-bugs@sendmail.org.
  For local information send email to Postmaster at your site.
  End of HELP info
  >>> s.putcmd("vrfy","someone@here")
  >>> s.getreply()
  (250, "Somebody OverHere <somebody@here.my.org>")
  >>> s.quit()
'''

# Author: The Dragon De Monsyne <dragondm@integral.org>
# ESMTP support, test code oraz doc fixes added by
#     Eric S. Raymond <esr@thyrsus.com>
# Better RFC 821 compliance (MAIL oraz RCPT, oraz CRLF w data)
#     by Carey Evans <c.evans@clear.net.nz>, dla picky mail servers.
# RFC 2554 (authentication) support by Gerhard Haering <gerhard@bigfoot.de>.
#
# This was modified z the Python 1.5 library HTTP lib.

zaimportuj socket
zaimportuj io
zaimportuj re
zaimportuj email.utils
zaimportuj email.message
zaimportuj email.generator
zaimportuj base64
zaimportuj hmac
zaimportuj copy
zaimportuj datetime
zaimportuj sys
z email.base64mime zaimportuj body_encode jako encode_base64

__all__ = ["SMTPException", "SMTPServerDisconnected", "SMTPResponseException",
           "SMTPSenderRefused", "SMTPRecipientsRefused", "SMTPDataError",
           "SMTPConnectError", "SMTPHeloError", "SMTPAuthenticationError",
           "quoteaddr", "quotedata", "SMTP"]

SMTP_PORT = 25
SMTP_SSL_PORT = 465
CRLF = "\r\n"
bCRLF = b"\r\n"
_MAXLINE = 8192 # more than 8 times larger than RFC 821, 4.5.3

OLDSTYLE_AUTH = re.compile(r"auth=(.*)", re.I)

# Exception classes used by this module.
klasa SMTPException(OSError):
    """Base klasa dla all exceptions podnieśd by this module."""

klasa SMTPNotSupportedError(SMTPException):
    """The command albo option jest nie supported by the SMTP server.

    This exception jest podnieśd when an attempt jest made to run a command albo a
    command przy an option which jest nie supported by the server.
    """

klasa SMTPServerDisconnected(SMTPException):
    """Not connected to any SMTP server.

    This exception jest podnieśd when the server unexpectedly disconnects,
    albo when an attempt jest made to use the SMTP instance before
    connecting it to a server.
    """

klasa SMTPResponseException(SMTPException):
    """Base klasa dla all exceptions that include an SMTP error code.

    These exceptions are generated w some instances when the SMTP
    server returns an error code.  The error code jest stored w the
    `smtp_code' attribute of the error, oraz the `smtp_error' attribute
    jest set to the error message.
    """

    def __init__(self, code, msg):
        self.smtp_code = code
        self.smtp_error = msg
        self.args = (code, msg)

klasa SMTPSenderRefused(SMTPResponseException):
    """Sender address refused.

    In addition to the attributes set by on all SMTPResponseException
    exceptions, this sets `sender' to the string that the SMTP refused.
    """

    def __init__(self, code, msg, sender):
        self.smtp_code = code
        self.smtp_error = msg
        self.sender = sender
        self.args = (code, msg, sender)

klasa SMTPRecipientsRefused(SMTPException):
    """All recipient addresses refused.

    The errors dla each recipient are accessible through the attribute
    'recipients', which jest a dictionary of exactly the same sort as
    SMTP.sendmail() returns.
    """

    def __init__(self, recipients):
        self.recipients = recipients
        self.args = (recipients,)


klasa SMTPDataError(SMTPResponseException):
    """The SMTP server didn't accept the data."""

klasa SMTPConnectError(SMTPResponseException):
    """Error during connection establishment."""

klasa SMTPHeloError(SMTPResponseException):
    """The server refused our HELO reply."""

klasa SMTPAuthenticationError(SMTPResponseException):
    """Authentication error.

    Most probably the server didn't accept the username/password
    combination provided.
    """

def quoteaddr(addrstring):
    """Quote a subset of the email addresses defined by RFC 821.

    Should be able to handle anything email.utils.parseaddr can handle.
    """
    displayname, addr = email.utils.parseaddr(addrstring)
    jeżeli (displayname, addr) == ('', ''):
        # parseaddr couldn't parse it, use it jako jest oraz hope dla the best.
        jeżeli addrstring.strip().startswith('<'):
            zwróć addrstring
        zwróć "<%s>" % addrstring
    zwróć "<%s>" % addr

def _addr_only(addrstring):
    displayname, addr = email.utils.parseaddr(addrstring)
    jeżeli (displayname, addr) == ('', ''):
        # parseaddr couldn't parse it, so use it jako is.
        zwróć addrstring
    zwróć addr

# Legacy method kept dla backward compatibility.
def quotedata(data):
    """Quote data dla email.

    Double leading '.', oraz change Unix newline '\\n', albo Mac '\\r' into
    Internet CRLF end-of-line.
    """
    zwróć re.sub(r'(?m)^\.', '..',
        re.sub(r'(?:\r\n|\n|\r(?!\n))', CRLF, data))

def _quote_periods(bindata):
    zwróć re.sub(br'(?m)^\.', b'..', bindata)

def _fix_eols(data):
    zwróć  re.sub(r'(?:\r\n|\n|\r(?!\n))', CRLF, data)

spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    _have_ssl = Nieprawda
inaczej:
    _have_ssl = Prawda


klasa SMTP:
    """This klasa manages a connection to an SMTP albo ESMTP server.
    SMTP Objects:
        SMTP objects have the following attributes:
            helo_resp
                This jest the message given by the server w response to the
                most recent HELO command.

            ehlo_resp
                This jest the message given by the server w response to the
                most recent EHLO command. This jest usually multiline.

            does_esmtp
                This jest a Prawda value _after you do an EHLO command_, jeżeli the
                server supports ESMTP.

            esmtp_features
                This jest a dictionary, which, jeżeli the server supports ESMTP,
                will _after you do an EHLO command_, contain the names of the
                SMTP service extensions this server supports, oraz their
                parameters (jeżeli any).

                Note, all extension names are mapped to lower case w the
                dictionary.

        See each method's docstrings dla details.  In general, there jest a
        method of the same name to perform each SMTP command.  There jest also a
        method called 'sendmail' that will do an entire mail transaction.
        """
    debuglevel = 0
    file = Nic
    helo_resp = Nic
    ehlo_msg = "ehlo"
    ehlo_resp = Nic
    does_esmtp = 0
    default_port = SMTP_PORT

    def __init__(self, host='', port=0, local_hostname=Nic,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=Nic):
        """Initialize a new instance.

        If specified, `host' jest the name of the remote host to which to
        connect.  If specified, `port' specifies the port to which to connect.
        By default, smtplib.SMTP_PORT jest used.  If a host jest specified the
        connect method jest called, oraz jeżeli it returns anything other than a
        success code an SMTPConnectError jest podnieśd.  If specified,
        `local_hostname` jest used jako the FQDN of the local host w the HELO/EHLO
        command.  Otherwise, the local hostname jest found using
        socket.getfqdn(). The `source_address` parameter takes a 2-tuple (host,
        port) dla the socket to bind to jako its source address before
        connecting. If the host jest '' oraz port jest 0, the OS default behavior
        will be used.

        """
        self._host = host
        self.timeout = timeout
        self.esmtp_features = {}
        self.command_encoding = 'ascii'
        self.source_address = source_address

        jeżeli host:
            (code, msg) = self.connect(host, port)
            jeżeli code != 220:
                podnieś SMTPConnectError(code, msg)
        jeżeli local_hostname jest nie Nic:
            self.local_hostname = local_hostname
        inaczej:
            # RFC 2821 says we should use the fqdn w the EHLO/HELO verb, oraz
            # jeżeli that can't be calculated, that we should use a domain literal
            # instead (essentially an encoded IP address like [A.B.C.D]).
            fqdn = socket.getfqdn()
            jeżeli '.' w fqdn:
                self.local_hostname = fqdn
            inaczej:
                # We can't find an fqdn hostname, so use a domain literal
                addr = '127.0.0.1'
                spróbuj:
                    addr = socket.gethostbyname(socket.gethostname())
                wyjąwszy socket.gaierror:
                    dalej
                self.local_hostname = '[%s]' % addr

    def __enter__(self):
        zwróć self

    def __exit__(self, *args):
        spróbuj:
            code, message = self.docmd("QUIT")
            jeżeli code != 221:
                podnieś SMTPResponseException(code, message)
        wyjąwszy SMTPServerDisconnected:
            dalej
        w_końcu:
            self.close()

    def set_debuglevel(self, debuglevel):
        """Set the debug output level.

        A non-false value results w debug messages dla connection oraz dla all
        messages sent to oraz received z the server.

        """
        self.debuglevel = debuglevel

    def _print_debug(self, *args):
        jeżeli self.debuglevel > 1:
            print(datetime.datetime.now().time(), *args, file=sys.stderr)
        inaczej:
            print(*args, file=sys.stderr)

    def _get_socket(self, host, port, timeout):
        # This makes it simpler dla SMTP_SSL to use the SMTP connect code
        # oraz just alter the socket connection bit.
        jeżeli self.debuglevel > 0:
            self._print_debug('connect: to', (host, port), self.source_address)
        zwróć socket.create_connection((host, port), timeout,
                                        self.source_address)

    def connect(self, host='localhost', port=0, source_address=Nic):
        """Connect to a host on a given port.

        If the hostname ends przy a colon (`:') followed by a number, oraz
        there jest no port specified, that suffix will be stripped off oraz the
        number interpreted jako the port number to use.

        Note: This method jest automatically invoked by __init__, jeżeli a host jest
        specified during instantiation.

        """

        jeżeli source_address:
            self.source_address = source_address

        jeżeli nie port oraz (host.find(':') == host.rfind(':')):
            i = host.rfind(':')
            jeżeli i >= 0:
                host, port = host[:i], host[i + 1:]
                spróbuj:
                    port = int(port)
                wyjąwszy ValueError:
                    podnieś OSError("nonnumeric port")
        jeżeli nie port:
            port = self.default_port
        jeżeli self.debuglevel > 0:
            self._print_debug('connect:', (host, port))
        self.sock = self._get_socket(host, port, self.timeout)
        self.file = Nic
        (code, msg) = self.getreply()
        jeżeli self.debuglevel > 0:
            self._print_debug('connect:', repr(msg))
        zwróć (code, msg)

    def send(self, s):
        """Send `s' to the server."""
        jeżeli self.debuglevel > 0:
            self._print_debug('send:', repr(s))
        jeżeli hasattr(self, 'sock') oraz self.sock:
            jeżeli isinstance(s, str):
                # send jest used by the 'data' command, where command_encoding
                # should nie be used, but 'data' needs to convert the string to
                # binary itself anyway, so that's nie a problem.
                s = s.encode(self.command_encoding)
            spróbuj:
                self.sock.sendall(s)
            wyjąwszy OSError:
                self.close()
                podnieś SMTPServerDisconnected('Server nie connected')
        inaczej:
            podnieś SMTPServerDisconnected('please run connect() first')

    def putcmd(self, cmd, args=""):
        """Send a command to the server."""
        jeżeli args == "":
            str = '%s%s' % (cmd, CRLF)
        inaczej:
            str = '%s %s%s' % (cmd, args, CRLF)
        self.send(str)

    def getreply(self):
        """Get a reply z the server.

        Returns a tuple consisting of:

          - server response code (e.g. '250', albo such, jeżeli all goes well)
            Note: returns -1 jeżeli it can't read response code.

          - server response string corresponding to response code (multiline
            responses are converted to a single, multiline string).

        Raises SMTPServerDisconnected jeżeli end-of-file jest reached.
        """
        resp = []
        jeżeli self.file jest Nic:
            self.file = self.sock.makefile('rb')
        dopóki 1:
            spróbuj:
                line = self.file.readline(_MAXLINE + 1)
            wyjąwszy OSError jako e:
                self.close()
                podnieś SMTPServerDisconnected("Connection unexpectedly closed: "
                                             + str(e))
            jeżeli nie line:
                self.close()
                podnieś SMTPServerDisconnected("Connection unexpectedly closed")
            jeżeli self.debuglevel > 0:
                self._print_debug('reply:', repr(line))
            jeżeli len(line) > _MAXLINE:
                self.close()
                podnieś SMTPResponseException(500, "Line too long.")
            resp.append(line[4:].strip(b' \t\r\n'))
            code = line[:3]
            # Check that the error code jest syntactically correct.
            # Don't attempt to read a continuation line jeżeli it jest broken.
            spróbuj:
                errcode = int(code)
            wyjąwszy ValueError:
                errcode = -1
                przerwij
            # Check jeżeli multiline response.
            jeżeli line[3:4] != b"-":
                przerwij

        errmsg = b"\n".join(resp)
        jeżeli self.debuglevel > 0:
            self._print_debug('reply: retcode (%s); Msg: %a' % (errcode, errmsg))
        zwróć errcode, errmsg

    def docmd(self, cmd, args=""):
        """Send a command, oraz zwróć its response code."""
        self.putcmd(cmd, args)
        zwróć self.getreply()

    # std smtp commands
    def helo(self, name=''):
        """SMTP 'helo' command.
        Hostname to send dla this command defaults to the FQDN of the local
        host.
        """
        self.putcmd("helo", name albo self.local_hostname)
        (code, msg) = self.getreply()
        self.helo_resp = msg
        zwróć (code, msg)

    def ehlo(self, name=''):
        """ SMTP 'ehlo' command.
        Hostname to send dla this command defaults to the FQDN of the local
        host.
        """
        self.esmtp_features = {}
        self.putcmd(self.ehlo_msg, name albo self.local_hostname)
        (code, msg) = self.getreply()
        # According to RFC1869 some (badly written)
        # MTA's will disconnect on an ehlo. Toss an exception if
        # that happens -ddm
        jeżeli code == -1 oraz len(msg) == 0:
            self.close()
            podnieś SMTPServerDisconnected("Server nie connected")
        self.ehlo_resp = msg
        jeżeli code != 250:
            zwróć (code, msg)
        self.does_esmtp = 1
        #parse the ehlo response -ddm
        assert isinstance(self.ehlo_resp, bytes), repr(self.ehlo_resp)
        resp = self.ehlo_resp.decode("latin-1").split('\n')
        usuń resp[0]
        dla each w resp:
            # To be able to communicate przy jako many SMTP servers jako possible,
            # we have to take the old-style auth advertisement into account,
            # because:
            # 1) Else our SMTP feature parser gets confused.
            # 2) There are some servers that only advertise the auth methods we
            #    support using the old style.
            auth_match = OLDSTYLE_AUTH.match(each)
            jeżeli auth_match:
                # This doesn't remove duplicates, but that's no problem
                self.esmtp_features["auth"] = self.esmtp_features.get("auth", "") \
                        + " " + auth_match.groups(0)[0]
                kontynuuj

            # RFC 1869 requires a space between ehlo keyword oraz parameters.
            # It's actually stricter, w that only spaces are allowed between
            # parameters, but were nie going to check dla that here.  Note
            # that the space isn't present jeżeli there are no parameters.
            m = re.match(r'(?P<feature>[A-Za-z0-9][A-Za-z0-9\-]*) ?', each)
            jeżeli m:
                feature = m.group("feature").lower()
                params = m.string[m.end("feature"):].strip()
                jeżeli feature == "auth":
                    self.esmtp_features[feature] = self.esmtp_features.get(feature, "") \
                            + " " + params
                inaczej:
                    self.esmtp_features[feature] = params
        zwróć (code, msg)

    def has_extn(self, opt):
        """Does the server support a given SMTP service extension?"""
        zwróć opt.lower() w self.esmtp_features

    def help(self, args=''):
        """SMTP 'help' command.
        Returns help text z server."""
        self.putcmd("help", args)
        zwróć self.getreply()[1]

    def rset(self):
        """SMTP 'rset' command -- resets session."""
        self.command_encoding = 'ascii'
        zwróć self.docmd("rset")

    def _rset(self):
        """Internal 'rset' command which ignores any SMTPServerDisconnected error.

        Used internally w the library, since the server disconnected error
        should appear to the application when the *next* command jest issued, if
        we are doing an internal "safety" reset.
        """
        spróbuj:
            self.rset()
        wyjąwszy SMTPServerDisconnected:
            dalej

    def noop(self):
        """SMTP 'noop' command -- doesn't do anything :>"""
        zwróć self.docmd("noop")

    def mail(self, sender, options=[]):
        """SMTP 'mail' command -- begins mail xfer session.

        This method may podnieś the following exceptions:

         SMTPNotSupportedError  The options parameter includes 'SMTPUTF8'
                                but the SMTPUTF8 extension jest nie supported by
                                the server.
        """
        optionlist = ''
        jeżeli options oraz self.does_esmtp:
            jeżeli any(x.lower()=='smtputf8' dla x w options):
                jeżeli self.has_extn('smtputf8'):
                    self.command_encoding = 'utf-8'
                inaczej:
                    podnieś SMTPNotSupportedError(
                        'SMTPUTF8 nie supported by server')
            optionlist = ' ' + ' '.join(options)
        self.putcmd("mail", "FROM:%s%s" % (quoteaddr(sender), optionlist))
        zwróć self.getreply()

    def rcpt(self, recip, options=[]):
        """SMTP 'rcpt' command -- indicates 1 recipient dla this mail."""
        optionlist = ''
        jeżeli options oraz self.does_esmtp:
            optionlist = ' ' + ' '.join(options)
        self.putcmd("rcpt", "TO:%s%s" % (quoteaddr(recip), optionlist))
        zwróć self.getreply()

    def data(self, msg):
        """SMTP 'DATA' command -- sends message data to server.

        Automatically quotes lines beginning przy a period per rfc821.
        Raises SMTPDataError jeżeli there jest an unexpected reply to the
        DATA command; the zwróć value z this method jest the final
        response code received when the all data jest sent.  If msg
        jest a string, lone '\\r' oraz '\\n' characters are converted to
        '\\r\\n' characters.  If msg jest bytes, it jest transmitted jako is.
        """
        self.putcmd("data")
        (code, repl) = self.getreply()
        jeżeli self.debuglevel > 0:
            self._print_debug('data:', (code, repl))
        jeżeli code != 354:
            podnieś SMTPDataError(code, repl)
        inaczej:
            jeżeli isinstance(msg, str):
                msg = _fix_eols(msg).encode('ascii')
            q = _quote_periods(msg)
            jeżeli q[-2:] != bCRLF:
                q = q + bCRLF
            q = q + b"." + bCRLF
            self.send(q)
            (code, msg) = self.getreply()
            jeżeli self.debuglevel > 0:
                self._print_debug('data:', (code, msg))
            zwróć (code, msg)

    def verify(self, address):
        """SMTP 'verify' command -- checks dla address validity."""
        self.putcmd("vrfy", _addr_only(address))
        zwróć self.getreply()
    # a.k.a.
    vrfy = verify

    def expn(self, address):
        """SMTP 'expn' command -- expands a mailing list."""
        self.putcmd("expn", _addr_only(address))
        zwróć self.getreply()

    # some useful methods

    def ehlo_or_helo_if_needed(self):
        """Call self.ehlo() and/or self.helo() jeżeli needed.

        If there has been no previous EHLO albo HELO command this session, this
        method tries ESMTP EHLO first.

        This method may podnieś the following exceptions:

         SMTPHeloError            The server didn't reply properly to
                                  the helo greeting.
        """
        jeżeli self.helo_resp jest Nic oraz self.ehlo_resp jest Nic:
            jeżeli nie (200 <= self.ehlo()[0] <= 299):
                (code, resp) = self.helo()
                jeżeli nie (200 <= code <= 299):
                    podnieś SMTPHeloError(code, resp)

    def auth(self, mechanism, authobject, *, initial_response_ok=Prawda):
        """Authentication command - requires response processing.

        'mechanism' specifies which authentication mechanism jest to
        be used - the valid values are those listed w the 'auth'
        element of 'esmtp_features'.

        'authobject' must be a callable object taking a single argument:

                data = authobject(challenge)

        It will be called to process the server's challenge response; the
        challenge argument it jest dalejed will be a bytes.  It should zwróć
        bytes data that will be base64 encoded oraz sent to the server.

        Keyword arguments:
            - initial_response_ok: Allow sending the RFC 4954 initial-response
              to the AUTH command, jeżeli the authentication methods supports it.
        """
        # RFC 4954 allows auth methods to provide an initial response.  Not all
        # methods support it.  By definition, jeżeli they zwróć something other
        # than Nic when challenge jest Nic, then they do.  See issue #15014.
        mechanism = mechanism.upper()
        initial_response = (authobject() jeżeli initial_response_ok inaczej Nic)
        jeżeli initial_response jest nie Nic:
            response = encode_base64(initial_response.encode('ascii'), eol='')
            (code, resp) = self.docmd("AUTH", mechanism + " " + response)
        inaczej:
            (code, resp) = self.docmd("AUTH", mechanism)
            # Server replies przy 334 (challenge) albo 535 (nie supported)
            jeżeli code == 334:
                challenge = base64.decodebytes(resp)
                response = encode_base64(
                    authobject(challenge).encode('ascii'), eol='')
                (code, resp) = self.docmd(response)
        jeżeli code w (235, 503):
            zwróć (code, resp)
        podnieś SMTPAuthenticationError(code, resp)

    def auth_cram_md5(self, challenge=Nic):
        """ Authobject to use przy CRAM-MD5 authentication. Requires self.user
        oraz self.password to be set."""
        # CRAM-MD5 does nie support initial-response.
        jeżeli challenge jest Nic:
            zwróć Nic
        zwróć self.user + " " + hmac.HMAC(
            self.password.encode('ascii'), challenge, 'md5').hexdigest()

    def auth_plain(self, challenge=Nic):
        """ Authobject to use przy PLAIN authentication. Requires self.user oraz
        self.password to be set."""
        zwróć "\0%s\0%s" % (self.user, self.password)

    def auth_login(self, challenge=Nic):
        """ Authobject to use przy LOGIN authentication. Requires self.user oraz
        self.password to be set."""
        (code, resp) = self.docmd(
            encode_base64(self.user.encode('ascii'), eol=''))
        jeżeli code == 334:
            zwróć self.password
        podnieś SMTPAuthenticationError(code, resp)

    def login(self, user, dalejword, *, initial_response_ok=Prawda):
        """Log w on an SMTP server that requires authentication.

        The arguments are:
            - user:         The user name to authenticate with.
            - dalejword:     The dalejword dla the authentication.

        Keyword arguments:
            - initial_response_ok: Allow sending the RFC 4954 initial-response
              to the AUTH command, jeżeli the authentication methods supports it.

        If there has been no previous EHLO albo HELO command this session, this
        method tries ESMTP EHLO first.

        This method will zwróć normally jeżeli the authentication was successful.

        This method may podnieś the following exceptions:

         SMTPHeloError            The server didn't reply properly to
                                  the helo greeting.
         SMTPAuthenticationError  The server didn't accept the username/
                                  dalejword combination.
         SMTPNotSupportedError    The AUTH command jest nie supported by the
                                  server.
         SMTPException            No suitable authentication method was
                                  found.
        """

        self.ehlo_or_helo_if_needed()
        jeżeli nie self.has_extn("auth"):
            podnieś SMTPNotSupportedError(
                "SMTP AUTH extension nie supported by server.")

        # Authentication methods the server claims to support
        advertised_authlist = self.esmtp_features["auth"].split()

        # Authentication methods we can handle w our preferred order:
        preferred_auths = ['CRAM-MD5', 'PLAIN', 'LOGIN']

        # We try the supported authentications w our preferred order, if
        # the server supports them.
        authlist = [auth dla auth w preferred_auths
                    jeżeli auth w advertised_authlist]
        jeżeli nie authlist:
            podnieś SMTPException("No suitable authentication method found.")

        # Some servers advertise authentication methods they don't really
        # support, so jeżeli authentication fails, we continue until we've tried
        # all methods.
        self.user, self.password = user, dalejword
        dla authmethod w authlist:
            method_name = 'auth_' + authmethod.lower().replace('-', '_')
            spróbuj:
                (code, resp) = self.auth(
                    authmethod, getattr(self, method_name),
                    initial_response_ok=initial_response_ok)
                # 235 == 'Authentication successful'
                # 503 == 'Error: already authenticated'
                jeżeli code w (235, 503):
                    zwróć (code, resp)
            wyjąwszy SMTPAuthenticationError jako e:
                last_exception = e

        # We could nie login successfully.  Return result of last attempt.
        podnieś last_exception

    def starttls(self, keyfile=Nic, certfile=Nic, context=Nic):
        """Puts the connection to the SMTP server into TLS mode.

        If there has been no previous EHLO albo HELO command this session, this
        method tries ESMTP EHLO first.

        If the server supports TLS, this will encrypt the rest of the SMTP
        session. If you provide the keyfile oraz certfile parameters,
        the identity of the SMTP server oraz client can be checked. This,
        however, depends on whether the socket module really checks the
        certificates.

        This method may podnieś the following exceptions:

         SMTPHeloError            The server didn't reply properly to
                                  the helo greeting.
        """
        self.ehlo_or_helo_if_needed()
        jeżeli nie self.has_extn("starttls"):
            podnieś SMTPNotSupportedError(
                "STARTTLS extension nie supported by server.")
        (resp, reply) = self.docmd("STARTTLS")
        jeżeli resp == 220:
            jeżeli nie _have_ssl:
                podnieś RuntimeError("No SSL support included w this Python")
            jeżeli context jest nie Nic oraz keyfile jest nie Nic:
                podnieś ValueError("context oraz keyfile arguments are mutually "
                                 "exclusive")
            jeżeli context jest nie Nic oraz certfile jest nie Nic:
                podnieś ValueError("context oraz certfile arguments are mutually "
                                 "exclusive")
            jeżeli context jest Nic:
                context = ssl._create_stdlib_context(certfile=certfile,
                                                     keyfile=keyfile)
            self.sock = context.wrap_socket(self.sock,
                                            server_hostname=self._host)
            self.file = Nic
            # RFC 3207:
            # The client MUST discard any knowledge obtained from
            # the server, such jako the list of SMTP service extensions,
            # which was nie obtained z the TLS negotiation itself.
            self.helo_resp = Nic
            self.ehlo_resp = Nic
            self.esmtp_features = {}
            self.does_esmtp = 0
        zwróć (resp, reply)

    def sendmail(self, from_addr, to_addrs, msg, mail_options=[],
                 rcpt_options=[]):
        """This command performs an entire mail transaction.

        The arguments are:
            - from_addr    : The address sending this mail.
            - to_addrs     : A list of addresses to send this mail to.  A bare
                             string will be treated jako a list przy 1 address.
            - msg          : The message to send.
            - mail_options : List of ESMTP options (such jako 8bitmime) dla the
                             mail command.
            - rcpt_options : List of ESMTP options (such jako DSN commands) for
                             all the rcpt commands.

        msg may be a string containing characters w the ASCII range, albo a byte
        string.  A string jest encoded to bytes using the ascii codec, oraz lone
        \\r oraz \\n characters are converted to \\r\\n characters.

        If there has been no previous EHLO albo HELO command this session, this
        method tries ESMTP EHLO first.  If the server does ESMTP, message size
        oraz each of the specified options will be dalejed to it.  If EHLO
        fails, HELO will be tried oraz ESMTP options suppressed.

        This method will zwróć normally jeżeli the mail jest accepted dla at least
        one recipient.  It returns a dictionary, przy one entry dla each
        recipient that was refused.  Each entry contains a tuple of the SMTP
        error code oraz the accompanying error message sent by the server.

        This method may podnieś the following exceptions:

         SMTPHeloError          The server didn't reply properly to
                                the helo greeting.
         SMTPRecipientsRefused  The server rejected ALL recipients
                                (no mail was sent).
         SMTPSenderRefused      The server didn't accept the from_addr.
         SMTPDataError          The server replied przy an unexpected
                                error code (other than a refusal of
                                a recipient).
         SMTPNotSupportedError  The mail_options parameter includes 'SMTPUTF8'
                                but the SMTPUTF8 extension jest nie supported by
                                the server.

        Note: the connection will be open even after an exception jest podnieśd.

        Example:

         >>> zaimportuj smtplib
         >>> s=smtplib.SMTP("localhost")
         >>> tolist=["one@one.org","two@two.org","three@three.org","four@four.org"]
         >>> msg = '''\\
         ... From: Me@my.org
         ... Subject: testin'...
         ...
         ... This jest a test '''
         >>> s.sendmail("me@my.org",tolist,msg)
         { "three@three.org" : ( 550 ,"User unknown" ) }
         >>> s.quit()

        In the above example, the message was accepted dla delivery to three
        of the four addresses, oraz one was rejected, przy the error code
        550.  If all addresses are accepted, then the method will zwróć an
        empty dictionary.

        """
        self.ehlo_or_helo_if_needed()
        esmtp_opts = []
        jeżeli isinstance(msg, str):
            msg = _fix_eols(msg).encode('ascii')
        jeżeli self.does_esmtp:
            jeżeli self.has_extn('size'):
                esmtp_opts.append("size=%d" % len(msg))
            dla option w mail_options:
                esmtp_opts.append(option)
        (code, resp) = self.mail(from_addr, esmtp_opts)
        jeżeli code != 250:
            jeżeli code == 421:
                self.close()
            inaczej:
                self._rset()
            podnieś SMTPSenderRefused(code, resp, from_addr)
        senderrs = {}
        jeżeli isinstance(to_addrs, str):
            to_addrs = [to_addrs]
        dla each w to_addrs:
            (code, resp) = self.rcpt(each, rcpt_options)
            jeżeli (code != 250) oraz (code != 251):
                senderrs[each] = (code, resp)
            jeżeli code == 421:
                self.close()
                podnieś SMTPRecipientsRefused(senderrs)
        jeżeli len(senderrs) == len(to_addrs):
            # the server refused all our recipients
            self._rset()
            podnieś SMTPRecipientsRefused(senderrs)
        (code, resp) = self.data(msg)
        jeżeli code != 250:
            jeżeli code == 421:
                self.close()
            inaczej:
                self._rset()
            podnieś SMTPDataError(code, resp)
        #jeżeli we got here then somebody got our mail
        zwróć senderrs

    def send_message(self, msg, from_addr=Nic, to_addrs=Nic,
                mail_options=[], rcpt_options={}):
        """Converts message to a bytestring oraz dalejes it to sendmail.

        The arguments are jako dla sendmail, wyjąwszy that msg jest an
        email.message.Message object.  If from_addr jest Nic albo to_addrs jest
        Nic, these arguments are taken z the headers of the Message as
        described w RFC 2822 (a ValueError jest podnieśd jeżeli there jest more than
        one set of 'Resent-' headers).  Regardless of the values of from_addr oraz
        to_addr, any Bcc field (or Resent-Bcc field, when the Message jest a
        resent) of the Message object won't be transmitted.  The Message
        object jest then serialized using email.generator.BytesGenerator oraz
        sendmail jest called to transmit the message.  If the sender albo any of
        the recipient addresses contain non-ASCII oraz the server advertises the
        SMTPUTF8 capability, the policy jest cloned przy utf8 set to Prawda dla the
        serialization, oraz SMTPUTF8 oraz BODY=8BITMIME are asserted on the send.
        If the server does nie support SMTPUTF8, an SMPTNotSupported error jest
        podnieśd.  Otherwise the generator jest called without modifying the
        policy.

        """
        # 'Resent-Date' jest a mandatory field jeżeli the Message jest resent (RFC 2822
        # Section 3.6.6). In such a case, we use the 'Resent-*' fields.  However,
        # jeżeli there jest more than one 'Resent-' block there's no way to
        # unambiguously determine which one jest the most recent w all cases,
        # so rather than guess we podnieś a ValueError w that case.
        #
        # TODO implement heuristics to guess the correct Resent-* block przy an
        # option allowing the user to enable the heuristics.  (It should be
        # possible to guess correctly almost all of the time.)

        self.ehlo_or_helo_if_needed()
        resent = msg.get_all('Resent-Date')
        jeżeli resent jest Nic:
            header_prefix = ''
        albo_inaczej len(resent) == 1:
            header_prefix = 'Resent-'
        inaczej:
            podnieś ValueError("message has more than one 'Resent-' header block")
        jeżeli from_addr jest Nic:
            # Prefer the sender field per RFC 2822:3.6.2.
            from_addr = (msg[header_prefix + 'Sender']
                           jeżeli (header_prefix + 'Sender') w msg
                           inaczej msg[header_prefix + 'From'])
        jeżeli to_addrs jest Nic:
            addr_fields = [f dla f w (msg[header_prefix + 'To'],
                                       msg[header_prefix + 'Bcc'],
                                       msg[header_prefix + 'Cc'])
                           jeżeli f jest nie Nic]
            to_addrs = [a[1] dla a w email.utils.getaddresses(addr_fields)]
        # Make a local copy so we can delete the bcc headers.
        msg_copy = copy.copy(msg)
        usuń msg_copy['Bcc']
        usuń msg_copy['Resent-Bcc']
        international = Nieprawda
        spróbuj:
            ''.join([from_addr, *to_addrs]).encode('ascii')
        wyjąwszy UnicodeEncodeError:
            jeżeli nie self.has_extn('smtputf8'):
                podnieś SMTPNotSupportedError(
                    "One albo more source albo delivery addresses require"
                    " internationalized email support, but the server"
                    " does nie advertise the required SMTPUTF8 capability")
            international = Prawda
        przy io.BytesIO() jako bytesmsg:
            jeżeli international:
                g = email.generator.BytesGenerator(
                    bytesmsg, policy=msg.policy.clone(utf8=Prawda))
                mail_options += ['SMTPUTF8', 'BODY=8BITMIME']
            inaczej:
                g = email.generator.BytesGenerator(bytesmsg)
            g.flatten(msg_copy, linesep='\r\n')
            flatmsg = bytesmsg.getvalue()
        zwróć self.sendmail(from_addr, to_addrs, flatmsg, mail_options,
                             rcpt_options)

    def close(self):
        """Close the connection to the SMTP server."""
        spróbuj:
            file = self.file
            self.file = Nic
            jeżeli file:
                file.close()
        w_końcu:
            sock = self.sock
            self.sock = Nic
            jeżeli sock:
                sock.close()

    def quit(self):
        """Terminate the SMTP session."""
        res = self.docmd("quit")
        # A new EHLO jest required after reconnecting przy connect()
        self.ehlo_resp = self.helo_resp = Nic
        self.esmtp_features = {}
        self.does_esmtp = Nieprawda
        self.close()
        zwróć res

jeżeli _have_ssl:

    klasa SMTP_SSL(SMTP):
        """ This jest a subclass derived z SMTP that connects over an SSL
        encrypted socket (to use this klasa you need a socket module that was
        compiled przy SSL support). If host jest nie specified, '' (the local
        host) jest used. If port jest omitted, the standard SMTP-over-SSL port
        (465) jest used.  local_hostname oraz source_address have the same meaning
        jako they do w the SMTP class.  keyfile oraz certfile are also optional -
        they can contain a PEM formatted private key oraz certificate chain file
        dla the SSL connection. context also optional, can contain a
        SSLContext, oraz jest an alternative to keyfile oraz certfile; If it jest
        specified both keyfile oraz certfile must be Nic.

        """

        default_port = SMTP_SSL_PORT

        def __init__(self, host='', port=0, local_hostname=Nic,
                     keyfile=Nic, certfile=Nic,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     source_address=Nic, context=Nic):
            jeżeli context jest nie Nic oraz keyfile jest nie Nic:
                podnieś ValueError("context oraz keyfile arguments are mutually "
                                 "exclusive")
            jeżeli context jest nie Nic oraz certfile jest nie Nic:
                podnieś ValueError("context oraz certfile arguments are mutually "
                                 "exclusive")
            self.keyfile = keyfile
            self.certfile = certfile
            jeżeli context jest Nic:
                context = ssl._create_stdlib_context(certfile=certfile,
                                                     keyfile=keyfile)
            self.context = context
            SMTP.__init__(self, host, port, local_hostname, timeout,
                    source_address)

        def _get_socket(self, host, port, timeout):
            jeżeli self.debuglevel > 0:
                self._print_debug('connect:', (host, port))
            new_socket = socket.create_connection((host, port), timeout,
                    self.source_address)
            new_socket = self.context.wrap_socket(new_socket,
                                                  server_hostname=self._host)
            zwróć new_socket

    __all__.append("SMTP_SSL")

#
# LMTP extension
#
LMTP_PORT = 2003

klasa LMTP(SMTP):
    """LMTP - Local Mail Transfer Protocol

    The LMTP protocol, which jest very similar to ESMTP, jest heavily based
    on the standard SMTP client. It's common to use Unix sockets for
    LMTP, so our connect() method must support that jako well jako a regular
    host:port server.  local_hostname oraz source_address have the same
    meaning jako they do w the SMTP class.  To specify a Unix socket,
    you must use an absolute path jako the host, starting przy a '/'.

    Authentication jest supported, using the regular SMTP mechanism. When
    using a Unix socket, LMTP generally don't support albo require any
    authentication, but your mileage might vary."""

    ehlo_msg = "lhlo"

    def __init__(self, host='', port=LMTP_PORT, local_hostname=Nic,
            source_address=Nic):
        """Initialize a new instance."""
        SMTP.__init__(self, host, port, local_hostname=local_hostname,
                      source_address=source_address)

    def connect(self, host='localhost', port=0, source_address=Nic):
        """Connect to the LMTP daemon, on either a Unix albo a TCP socket."""
        jeżeli host[0] != '/':
            zwróć SMTP.connect(self, host, port, source_address=source_address)

        # Handle Unix-domain sockets.
        spróbuj:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.file = Nic
            self.sock.connect(host)
        wyjąwszy OSError:
            jeżeli self.debuglevel > 0:
                self._print_debug('connect fail:', host)
            jeżeli self.sock:
                self.sock.close()
            self.sock = Nic
            podnieś
        (code, msg) = self.getreply()
        jeżeli self.debuglevel > 0:
            self._print_debug('connect:', msg)
        zwróć (code, msg)


# Test the sendmail method, which tests most of the others.
# Note: This always sends to localhost.
jeżeli __name__ == '__main__':
    zaimportuj sys

    def prompt(prompt):
        sys.stdout.write(prompt + ": ")
        sys.stdout.flush()
        zwróć sys.stdin.readline().strip()

    fromaddr = prompt("From")
    toaddrs = prompt("To").split(',')
    print("Enter message, end przy ^D:")
    msg = ''
    dopóki 1:
        line = sys.stdin.readline()
        jeżeli nie line:
            przerwij
        msg = msg + line
    print("Message length jest %d" % len(msg))

    server = SMTP('localhost')
    server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
