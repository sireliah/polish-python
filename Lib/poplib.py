"""A POP3 client class.

Based on the J. Myers POP3 draft, Jan. 96
"""

# Author: David Ascher <david_ascher@brown.edu>
#         [heavily stealing z nntplib.py]
# Updated: Piers Lauder <piers@cs.su.oz.au> [Jul '97]
# String method conversion oraz test jig improvements by ESR, February 2001.
# Added the POP3_SSL class. Methods loosely based on IMAP_SSL. Hector Urtubia <urtubia@mrbook.org> Aug 2003

# Example (see the test function at the end of this file)

# Imports

zaimportuj errno
zaimportuj re
zaimportuj socket

spróbuj:
    zaimportuj ssl
    HAVE_SSL = Prawda
wyjąwszy ImportError:
    HAVE_SSL = Nieprawda

__all__ = ["POP3","error_proto"]

# Exception podnieśd when an error albo invalid response jest received:

klasa error_proto(Exception): dalej

# Standard Port
POP3_PORT = 110

# POP SSL PORT
POP3_SSL_PORT = 995

# Line terminators (we always output CRLF, but accept any of CRLF, LFCR, LF)
CR = b'\r'
LF = b'\n'
CRLF = CR+LF

# maximal line length when calling readline(). This jest to prevent
# reading arbitrary length lines. RFC 1939 limits POP3 line length to
# 512 characters, including CRLF. We have selected 2048 just to be on
# the safe side.
_MAXLINE = 2048


klasa POP3:

    """This klasa supports both the minimal oraz optional command sets.
    Arguments can be strings albo integers (where appropriate)
    (e.g.: retr(1) oraz retr('1') both work equally well.

    Minimal Command Set:
            USER name               user(name)
            PASS string             dalej_(string)
            STAT                    stat()
            LIST [msg]              list(msg = Nic)
            RETR msg                retr(msg)
            DELE msg                dele(msg)
            NOOP                    noop()
            RSET                    rset()
            QUIT                    quit()

    Optional Commands (some servers support these):
            RPOP name               rpop(name)
            APOP name digest        apop(name, digest)
            TOP msg n               top(msg, n)
            UIDL [msg]              uidl(msg = Nic)
            CAPA                    capa()
            STLS                    stls()
            UTF8                    utf8()

    Raises one exception: 'error_proto'.

    Instantiate with:
            POP3(hostname, port=110)

    NB:     the POP protocol locks the mailbox z user
            authorization until QUIT, so be sure to get in, suck
            the messages, oraz quit, each time you access the
            mailbox.

            POP jest a line-based protocol, which means large mail
            messages consume lots of python cycles reading them
            line-by-line.

            If it's available on your mail server, use IMAP4
            instead, it doesn't suffer z the two problems
            above.
    """

    encoding = 'UTF-8'

    def __init__(self, host, port=POP3_PORT,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self._tls_established = Nieprawda
        self.sock = self._create_socket(timeout)
        self.file = self.sock.makefile('rb')
        self._debugging = 0
        self.welcome = self._getresp()

    def _create_socket(self, timeout):
        zwróć socket.create_connection((self.host, self.port), timeout)

    def _putline(self, line):
        jeżeli self._debugging > 1: print('*put*', repr(line))
        self.sock.sendall(line + CRLF)


    # Internal: send one command to the server (through _putline())

    def _putcmd(self, line):
        jeżeli self._debugging: print('*cmd*', repr(line))
        line = bytes(line, self.encoding)
        self._putline(line)


    # Internal: zwróć one line z the server, stripping CRLF.
    # This jest where all the CPU time of this module jest consumed.
    # Raise error_proto('-ERR EOF') jeżeli the connection jest closed.

    def _getline(self):
        line = self.file.readline(_MAXLINE + 1)
        jeżeli len(line) > _MAXLINE:
            podnieś error_proto('line too long')

        jeżeli self._debugging > 1: print('*get*', repr(line))
        jeżeli nie line: podnieś error_proto('-ERR EOF')
        octets = len(line)
        # server can send any combination of CR & LF
        # however, 'readline()' returns lines ending w LF
        # so only possibilities are ...LF, ...CRLF, CR...LF
        jeżeli line[-2:] == CRLF:
            zwróć line[:-2], octets
        jeżeli line[:1] == CR:
            zwróć line[1:-1], octets
        zwróć line[:-1], octets


    # Internal: get a response z the server.
    # Raise 'error_proto' jeżeli the response doesn't start przy '+'.

    def _getresp(self):
        resp, o = self._getline()
        jeżeli self._debugging > 1: print('*resp*', repr(resp))
        jeżeli nie resp.startswith(b'+'):
            podnieś error_proto(resp)
        zwróć resp


    # Internal: get a response plus following text z the server.

    def _getlongresp(self):
        resp = self._getresp()
        list = []; octets = 0
        line, o = self._getline()
        dopóki line != b'.':
            jeżeli line.startswith(b'..'):
                o = o-1
                line = line[1:]
            octets = octets + o
            list.append(line)
            line, o = self._getline()
        zwróć resp, list, octets


    # Internal: send a command oraz get the response

    def _shortcmd(self, line):
        self._putcmd(line)
        zwróć self._getresp()


    # Internal: send a command oraz get the response plus following text

    def _longcmd(self, line):
        self._putcmd(line)
        zwróć self._getlongresp()


    # These can be useful:

    def getwelcome(self):
        zwróć self.welcome


    def set_debuglevel(self, level):
        self._debugging = level


    # Here are all the POP commands:

    def user(self, user):
        """Send user name, zwróć response

        (should indicate dalejword required).
        """
        zwróć self._shortcmd('USER %s' % user)


    def dalej_(self, pswd):
        """Send dalejword, zwróć response

        (response includes message count, mailbox size).

        NB: mailbox jest locked by server z here to 'quit()'
        """
        zwróć self._shortcmd('PASS %s' % pswd)


    def stat(self):
        """Get mailbox status.

        Result jest tuple of 2 ints (message count, mailbox size)
        """
        retval = self._shortcmd('STAT')
        rets = retval.split()
        jeżeli self._debugging: print('*stat*', repr(rets))
        numMessages = int(rets[1])
        sizeMessages = int(rets[2])
        zwróć (numMessages, sizeMessages)


    def list(self, which=Nic):
        """Request listing, zwróć result.

        Result without a message number argument jest w form
        ['response', ['mesg_num octets', ...], octets].

        Result when a message number argument jest given jest a
        single response: the "scan listing" dla that message.
        """
        jeżeli which jest nie Nic:
            zwróć self._shortcmd('LIST %s' % which)
        zwróć self._longcmd('LIST')


    def retr(self, which):
        """Retrieve whole message number 'which'.

        Result jest w form ['response', ['line', ...], octets].
        """
        zwróć self._longcmd('RETR %s' % which)


    def dele(self, which):
        """Delete message number 'which'.

        Result jest 'response'.
        """
        zwróć self._shortcmd('DELE %s' % which)


    def noop(self):
        """Does nothing.

        One supposes the response indicates the server jest alive.
        """
        zwróć self._shortcmd('NOOP')


    def rset(self):
        """Unmark all messages marked dla deletion."""
        zwróć self._shortcmd('RSET')


    def quit(self):
        """Signoff: commit changes on server, unlock mailbox, close connection."""
        resp = self._shortcmd('QUIT')
        self.close()
        zwróć resp

    def close(self):
        """Close the connection without assuming anything about it."""
        spróbuj:
            file = self.file
            self.file = Nic
            jeżeli file jest nie Nic:
                file.close()
        w_końcu:
            sock = self.sock
            self.sock = Nic
            jeżeli sock jest nie Nic:
                spróbuj:
                    sock.shutdown(socket.SHUT_RDWR)
                wyjąwszy OSError jako e:
                    # The server might already have closed the connection
                    jeżeli e.errno != errno.ENOTCONN:
                        podnieś
                w_końcu:
                    sock.close()

    #__del__ = quit


    # optional commands:

    def rpop(self, user):
        """Not sure what this does."""
        zwróć self._shortcmd('RPOP %s' % user)


    timestamp = re.compile(br'\+OK.*(<[^>]+>)')

    def apop(self, user, dalejword):
        """Authorisation

        - only possible jeżeli server has supplied a timestamp w initial greeting.

        Args:
                user     - mailbox user;
                dalejword - mailbox dalejword.

        NB: mailbox jest locked by server z here to 'quit()'
        """
        secret = bytes(password, self.encoding)
        m = self.timestamp.match(self.welcome)
        jeżeli nie m:
            podnieś error_proto('-ERR APOP nie supported by server')
        zaimportuj hashlib
        digest = m.group(1)+secret
        digest = hashlib.md5(digest).hexdigest()
        zwróć self._shortcmd('APOP %s %s' % (user, digest))


    def top(self, which, howmuch):
        """Retrieve message header of message number 'which'
        oraz first 'howmuch' lines of message body.

        Result jest w form ['response', ['line', ...], octets].
        """
        zwróć self._longcmd('TOP %s %s' % (which, howmuch))


    def uidl(self, which=Nic):
        """Return message digest (unique id) list.

        If 'which', result contains unique id dla that message
        w the form 'response mesgnum uid', otherwise result jest
        the list ['response', ['mesgnum uid', ...], octets]
        """
        jeżeli which jest nie Nic:
            zwróć self._shortcmd('UIDL %s' % which)
        zwróć self._longcmd('UIDL')


    def utf8(self):
        """Try to enter UTF-8 mode (see RFC 6856). Returns server response.
        """
        zwróć self._shortcmd('UTF8')


    def capa(self):
        """Return server capabilities (RFC 2449) jako a dictionary
        >>> c=poplib.POP3('localhost')
        >>> c.capa()
        {'IMPLEMENTATION': ['Cyrus', 'POP3', 'server', 'v2.2.12'],
         'TOP': [], 'LOGIN-DELAY': ['0'], 'AUTH-RESP-CODE': [],
         'EXPIRE': ['NEVER'], 'USER': [], 'STLS': [], 'PIPELINING': [],
         'UIDL': [], 'RESP-CODES': []}
        >>>

        Really, according to RFC 2449, the cyrus folks should avoid
        having the implementation split into multiple arguments...
        """
        def _parsecap(line):
            lst = line.decode('ascii').split()
            zwróć lst[0], lst[1:]

        caps = {}
        spróbuj:
            resp = self._longcmd('CAPA')
            rawcaps = resp[1]
            dla capline w rawcaps:
                capnm, capargs = _parsecap(capline)
                caps[capnm] = capargs
        wyjąwszy error_proto jako _err:
            podnieś error_proto('-ERR CAPA nie supported by server')
        zwróć caps


    def stls(self, context=Nic):
        """Start a TLS session on the active connection jako specified w RFC 2595.

                context - a ssl.SSLContext
        """
        jeżeli nie HAVE_SSL:
            podnieś error_proto('-ERR TLS support missing')
        jeżeli self._tls_established:
            podnieś error_proto('-ERR TLS session already established')
        caps = self.capa()
        jeżeli nie 'STLS' w caps:
            podnieś error_proto('-ERR STLS nie supported by server')
        jeżeli context jest Nic:
            context = ssl._create_stdlib_context()
        resp = self._shortcmd('STLS')
        self.sock = context.wrap_socket(self.sock,
                                        server_hostname=self.host)
        self.file = self.sock.makefile('rb')
        self._tls_established = Prawda
        zwróć resp


jeżeli HAVE_SSL:

    klasa POP3_SSL(POP3):
        """POP3 client klasa over SSL connection

        Instantiate with: POP3_SSL(hostname, port=995, keyfile=Nic, certfile=Nic,
                                   context=Nic)

               hostname - the hostname of the pop3 over ssl server
               port - port number
               keyfile - PEM formatted file that contains your private key
               certfile - PEM formatted certificate chain file
               context - a ssl.SSLContext

        See the methods of the parent klasa POP3 dla more documentation.
        """

        def __init__(self, host, port=POP3_SSL_PORT, keyfile=Nic, certfile=Nic,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT, context=Nic):
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
            POP3.__init__(self, host, port, timeout)

        def _create_socket(self, timeout):
            sock = POP3._create_socket(self, timeout)
            sock = self.context.wrap_socket(sock,
                                            server_hostname=self.host)
            zwróć sock

        def stls(self, keyfile=Nic, certfile=Nic, context=Nic):
            """The method unconditionally podnieśs an exception since the
            STLS command doesn't make any sense on an already established
            SSL/TLS session.
            """
            podnieś error_proto('-ERR TLS session already established')

    __all__.append("POP3_SSL")

jeżeli __name__ == "__main__":
    zaimportuj sys
    a = POP3(sys.argv[1])
    print(a.getwelcome())
    a.user(sys.argv[2])
    a.pass_(sys.argv[3])
    a.list()
    (numMsgs, totalSize) = a.stat()
    dla i w range(1, numMsgs + 1):
        (header, msg, octets) = a.retr(i)
        print("Message %d:" % i)
        dla line w msg:
            print('   ' + line)
        print('-----------------------')
    a.quit()
