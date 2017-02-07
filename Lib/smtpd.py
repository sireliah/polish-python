#! /usr/bin/env python3
"""An RFC 5321 smtp proxy przy optional RFC 1870 oraz RFC 6531 extensions.

Usage: %(program)s [options] [localhost:localport [remotehost:remoteport]]

Options:

    --nosetuid
    -n
        This program generally tries to setuid `nobody', unless this flag jest
        set.  The setuid call will fail jeżeli this program jest nie run jako root (in
        which case, use this flag).

    --version
    -V
        Print the version number oraz exit.

    --class classname
    -c classname
        Use `classname' jako the concrete SMTP proxy class.  Uses `PureProxy' by
        default.

    --size limit
    -s limit
        Restrict the total size of the incoming message to "limit" number of
        bytes via the RFC 1870 SIZE extension.  Defaults to 33554432 bytes.

    --smtputf8
    -u
        Enable the SMTPUTF8 extension oraz behave jako an RFC 6531 smtp proxy.

    --debug
    -d
        Turn on debugging prints.

    --help
    -h
        Print this message oraz exit.

Version: %(__version__)s

If localhost jest nie given then `localhost' jest used, oraz jeżeli localport jest nie
given then 8025 jest used.  If remotehost jest nie given then `localhost' jest used,
and jeżeli remoteport jest nie given, then 25 jest used.
"""

# Overview:
#
# This file implements the minimal SMTP protocol jako defined w RFC 5321.  It
# has a hierarchy of classes which implement the backend functionality dla the
# smtpd.  A number of classes are provided:
#
#   SMTPServer - the base klasa dla the backend.  Raises NotImplementedError
#   jeżeli you try to use it.
#
#   DebuggingServer - simply prints each message it receives on stdout.
#
#   PureProxy - Proxies all messages to a real smtpd which does final
#   delivery.  One known problem przy this klasa jest that it doesn't handle
#   SMTP errors z the backend server at all.  This should be fixed
#   (contributions are welcome!).
#
#   MailmanProxy - An experimental hack to work przy GNU Mailman
#   <www.list.org>.  Using this server jako your real incoming smtpd, your
#   mailhost will automatically recognize oraz accept mail destined to Mailman
#   lists when those lists are created.  Every message nie destined dla a list
#   gets forwarded to a real backend smtpd, jako przy PureProxy.  Again, errors
#   are nie handled correctly yet.
#
#
# Author: Barry Warsaw <barry@python.org>
#
# TODO:
#
# - support mailbox delivery
# - alias files
# - Handle more ESMTP extensions
# - handle error codes z the backend smtpd

zaimportuj sys
zaimportuj os
zaimportuj errno
zaimportuj getopt
zaimportuj time
zaimportuj socket
zaimportuj asyncore
zaimportuj asynchat
zaimportuj collections
z warnings zaimportuj warn
z email._header_value_parser zaimportuj get_addr_spec, get_angle_addr

__all__ = ["SMTPServer","DebuggingServer","PureProxy","MailmanProxy"]

program = sys.argv[0]
__version__ = 'Python SMTP proxy version 0.3'


klasa Devnull:
    def write(self, msg): dalej
    def flush(self): dalej


DEBUGSTREAM = Devnull()
NEWLINE = '\n'
COMMASPACE = ', '
DATA_SIZE_DEFAULT = 33554432


def usage(code, msg=''):
    print(__doc__ % globals(), file=sys.stderr)
    jeżeli msg:
        print(msg, file=sys.stderr)
    sys.exit(code)


klasa SMTPChannel(asynchat.async_chat):
    COMMAND = 0
    DATA = 1

    command_size_limit = 512
    command_size_limits = collections.defaultdict(lambda x=command_size_limit: x)

    @property
    def max_command_size_limit(self):
        spróbuj:
            zwróć max(self.command_size_limits.values())
        wyjąwszy ValueError:
            zwróć self.command_size_limit

    def __init__(self, server, conn, addr, data_size_limit=DATA_SIZE_DEFAULT,
                 map=Nic, enable_SMTPUTF8=Nieprawda, decode_data=Nic):
        asynchat.async_chat.__init__(self, conn, map=map)
        self.smtp_server = server
        self.conn = conn
        self.addr = addr
        self.data_size_limit = data_size_limit
        self.enable_SMTPUTF8 = enable_SMTPUTF8
        jeżeli enable_SMTPUTF8:
            jeżeli decode_data:
                ValueError("decode_data oraz enable_SMTPUTF8 cannot be set to"
                           " Prawda at the same time")
            decode_data = Nieprawda
        jeżeli decode_data jest Nic:
            warn("The decode_data default of Prawda will change to Nieprawda w 3.6;"
                 " specify an explicit value dla this keyword",
                 DeprecationWarning, 2)
            decode_data = Prawda
        self._decode_data = decode_data
        jeżeli decode_data:
            self._emptystring = ''
            self._linesep = '\r\n'
            self._dotsep = '.'
            self._newline = NEWLINE
        inaczej:
            self._emptystring = b''
            self._linesep = b'\r\n'
            self._dotsep = ord(b'.')
            self._newline = b'\n'
        self._set_rset_state()
        self.seen_greeting = ''
        self.extended_smtp = Nieprawda
        self.command_size_limits.clear()
        self.fqdn = socket.getfqdn()
        spróbuj:
            self.peer = conn.getpeername()
        wyjąwszy OSError jako err:
            # a race condition  may occur jeżeli the other end jest closing
            # before we can get the peername
            self.close()
            jeżeli err.args[0] != errno.ENOTCONN:
                podnieś
            zwróć
        print('Peer:', repr(self.peer), file=DEBUGSTREAM)
        self.push('220 %s %s' % (self.fqdn, __version__))

    def _set_post_data_state(self):
        """Reset state variables to their post-DATA state."""
        self.smtp_state = self.COMMAND
        self.mailz = Nic
        self.rcpttos = []
        self.require_SMTPUTF8 = Nieprawda
        self.num_bytes = 0
        self.set_terminator(b'\r\n')

    def _set_rset_state(self):
        """Reset all state variables wyjąwszy the greeting."""
        self._set_post_data_state()
        self.received_data = ''
        self.received_lines = []


    # properties dla backwards-compatibility
    @property
    def __server(self):
        warn("Access to __server attribute on SMTPChannel jest deprecated, "
            "use 'smtp_server' instead", DeprecationWarning, 2)
        zwróć self.smtp_server
    @__server.setter
    def __server(self, value):
        warn("Setting __server attribute on SMTPChannel jest deprecated, "
            "set 'smtp_server' instead", DeprecationWarning, 2)
        self.smtp_server = value

    @property
    def __line(self):
        warn("Access to __line attribute on SMTPChannel jest deprecated, "
            "use 'received_lines' instead", DeprecationWarning, 2)
        zwróć self.received_lines
    @__line.setter
    def __line(self, value):
        warn("Setting __line attribute on SMTPChannel jest deprecated, "
            "set 'received_lines' instead", DeprecationWarning, 2)
        self.received_lines = value

    @property
    def __state(self):
        warn("Access to __state attribute on SMTPChannel jest deprecated, "
            "use 'smtp_state' instead", DeprecationWarning, 2)
        zwróć self.smtp_state
    @__state.setter
    def __state(self, value):
        warn("Setting __state attribute on SMTPChannel jest deprecated, "
            "set 'smtp_state' instead", DeprecationWarning, 2)
        self.smtp_state = value

    @property
    def __greeting(self):
        warn("Access to __greeting attribute on SMTPChannel jest deprecated, "
            "use 'seen_greeting' instead", DeprecationWarning, 2)
        zwróć self.seen_greeting
    @__greeting.setter
    def __greeting(self, value):
        warn("Setting __greeting attribute on SMTPChannel jest deprecated, "
            "set 'seen_greeting' instead", DeprecationWarning, 2)
        self.seen_greeting = value

    @property
    def __mailfrom(self):
        warn("Access to __mailz attribute on SMTPChannel jest deprecated, "
            "use 'mailfrom' instead", DeprecationWarning, 2)
        zwróć self.mailfrom
    @__mailfrom.setter
    def __mailfrom(self, value):
        warn("Setting __mailz attribute on SMTPChannel jest deprecated, "
            "set 'mailfrom' instead", DeprecationWarning, 2)
        self.mailz = value

    @property
    def __rcpttos(self):
        warn("Access to __rcpttos attribute on SMTPChannel jest deprecated, "
            "use 'rcpttos' instead", DeprecationWarning, 2)
        zwróć self.rcpttos
    @__rcpttos.setter
    def __rcpttos(self, value):
        warn("Setting __rcpttos attribute on SMTPChannel jest deprecated, "
            "set 'rcpttos' instead", DeprecationWarning, 2)
        self.rcpttos = value

    @property
    def __data(self):
        warn("Access to __data attribute on SMTPChannel jest deprecated, "
            "use 'received_data' instead", DeprecationWarning, 2)
        zwróć self.received_data
    @__data.setter
    def __data(self, value):
        warn("Setting __data attribute on SMTPChannel jest deprecated, "
            "set 'received_data' instead", DeprecationWarning, 2)
        self.received_data = value

    @property
    def __fqdn(self):
        warn("Access to __fqdn attribute on SMTPChannel jest deprecated, "
            "use 'fqdn' instead", DeprecationWarning, 2)
        zwróć self.fqdn
    @__fqdn.setter
    def __fqdn(self, value):
        warn("Setting __fqdn attribute on SMTPChannel jest deprecated, "
            "set 'fqdn' instead", DeprecationWarning, 2)
        self.fqdn = value

    @property
    def __peer(self):
        warn("Access to __peer attribute on SMTPChannel jest deprecated, "
            "use 'peer' instead", DeprecationWarning, 2)
        zwróć self.peer
    @__peer.setter
    def __peer(self, value):
        warn("Setting __peer attribute on SMTPChannel jest deprecated, "
            "set 'peer' instead", DeprecationWarning, 2)
        self.peer = value

    @property
    def __conn(self):
        warn("Access to __conn attribute on SMTPChannel jest deprecated, "
            "use 'conn' instead", DeprecationWarning, 2)
        zwróć self.conn
    @__conn.setter
    def __conn(self, value):
        warn("Setting __conn attribute on SMTPChannel jest deprecated, "
            "set 'conn' instead", DeprecationWarning, 2)
        self.conn = value

    @property
    def __addr(self):
        warn("Access to __addr attribute on SMTPChannel jest deprecated, "
            "use 'addr' instead", DeprecationWarning, 2)
        zwróć self.addr
    @__addr.setter
    def __addr(self, value):
        warn("Setting __addr attribute on SMTPChannel jest deprecated, "
            "set 'addr' instead", DeprecationWarning, 2)
        self.addr = value

    # Overrides base klasa dla convenience.
    def push(self, msg):
        asynchat.async_chat.push(self, bytes(
            msg + '\r\n', 'utf-8' jeżeli self.require_SMTPUTF8 inaczej 'ascii'))

    # Implementation of base klasa abstract method
    def collect_incoming_data(self, data):
        limit = Nic
        jeżeli self.smtp_state == self.COMMAND:
            limit = self.max_command_size_limit
        albo_inaczej self.smtp_state == self.DATA:
            limit = self.data_size_limit
        jeżeli limit oraz self.num_bytes > limit:
            zwróć
        albo_inaczej limit:
            self.num_bytes += len(data)
        jeżeli self._decode_data:
            self.received_lines.append(str(data, 'utf-8'))
        inaczej:
            self.received_lines.append(data)

    # Implementation of base klasa abstract method
    def found_terminator(self):
        line = self._emptystring.join(self.received_lines)
        print('Data:', repr(line), file=DEBUGSTREAM)
        self.received_lines = []
        jeżeli self.smtp_state == self.COMMAND:
            sz, self.num_bytes = self.num_bytes, 0
            jeżeli nie line:
                self.push('500 Error: bad syntax')
                zwróć
            jeżeli nie self._decode_data:
                line = str(line, 'utf-8')
            i = line.find(' ')
            jeżeli i < 0:
                command = line.upper()
                arg = Nic
            inaczej:
                command = line[:i].upper()
                arg = line[i+1:].strip()
            max_sz = (self.command_size_limits[command]
                        jeżeli self.extended_smtp inaczej self.command_size_limit)
            jeżeli sz > max_sz:
                self.push('500 Error: line too long')
                zwróć
            method = getattr(self, 'smtp_' + command, Nic)
            jeżeli nie method:
                self.push('500 Error: command "%s" nie recognized' % command)
                zwróć
            method(arg)
            zwróć
        inaczej:
            jeżeli self.smtp_state != self.DATA:
                self.push('451 Internal confusion')
                self.num_bytes = 0
                zwróć
            jeżeli self.data_size_limit oraz self.num_bytes > self.data_size_limit:
                self.push('552 Error: Too much mail data')
                self.num_bytes = 0
                zwróć
            # Remove extraneous carriage returns oraz de-transparency according
            # to RFC 5321, Section 4.5.2.
            data = []
            dla text w line.split(self._linesep):
                jeżeli text oraz text[0] == self._dotsep:
                    data.append(text[1:])
                inaczej:
                    data.append(text)
            self.received_data = self._newline.join(data)
            args = (self.peer, self.mailfrom, self.rcpttos, self.received_data)
            kwargs = {}
            jeżeli nie self._decode_data:
                kwargs = {
                    'mail_options': self.mail_options,
                    'rcpt_options': self.rcpt_options,
                }
            status = self.smtp_server.process_message(*args, **kwargs)
            self._set_post_data_state()
            jeżeli nie status:
                self.push('250 OK')
            inaczej:
                self.push(status)

    # SMTP oraz ESMTP commands
    def smtp_HELO(self, arg):
        jeżeli nie arg:
            self.push('501 Syntax: HELO hostname')
            zwróć
        # See issue #21783 dla a discussion of this behavior.
        jeżeli self.seen_greeting:
            self.push('503 Duplicate HELO/EHLO')
            zwróć
        self._set_rset_state()
        self.seen_greeting = arg
        self.push('250 %s' % self.fqdn)

    def smtp_EHLO(self, arg):
        jeżeli nie arg:
            self.push('501 Syntax: EHLO hostname')
            zwróć
        # See issue #21783 dla a discussion of this behavior.
        jeżeli self.seen_greeting:
            self.push('503 Duplicate HELO/EHLO')
            zwróć
        self._set_rset_state()
        self.seen_greeting = arg
        self.extended_smtp = Prawda
        self.push('250-%s' % self.fqdn)
        jeżeli self.data_size_limit:
            self.push('250-SIZE %s' % self.data_size_limit)
            self.command_size_limits['MAIL'] += 26
        jeżeli nie self._decode_data:
            self.push('250-8BITMIME')
        jeżeli self.enable_SMTPUTF8:
            self.push('250-SMTPUTF8')
            self.command_size_limits['MAIL'] += 10
        self.push('250 HELP')

    def smtp_NOOP(self, arg):
        jeżeli arg:
            self.push('501 Syntax: NOOP')
        inaczej:
            self.push('250 OK')

    def smtp_QUIT(self, arg):
        # args jest ignored
        self.push('221 Bye')
        self.close_when_done()

    def _strip_command_keyword(self, keyword, arg):
        keylen = len(keyword)
        jeżeli arg[:keylen].upper() == keyword:
            zwróć arg[keylen:].strip()
        zwróć ''

    def _getaddr(self, arg):
        jeżeli nie arg:
            zwróć '', ''
        jeżeli arg.lstrip().startswith('<'):
            address, rest = get_angle_addr(arg)
        inaczej:
            address, rest = get_addr_spec(arg)
        jeżeli nie address:
            zwróć address, rest
        zwróć address.addr_spec, rest

    def _getparams(self, params):
        # Return params jako dictionary. Return Nic jeżeli nie all parameters
        # appear to be syntactically valid according to RFC 1869.
        result = {}
        dla param w params:
            param, eq, value = param.partition('=')
            jeżeli nie param.isalnum() albo eq oraz nie value:
                zwróć Nic
            result[param] = value jeżeli eq inaczej Prawda
        zwróć result

    def smtp_HELP(self, arg):
        jeżeli arg:
            extended = ' [SP <mail-parameters>]'
            lc_arg = arg.upper()
            jeżeli lc_arg == 'EHLO':
                self.push('250 Syntax: EHLO hostname')
            albo_inaczej lc_arg == 'HELO':
                self.push('250 Syntax: HELO hostname')
            albo_inaczej lc_arg == 'MAIL':
                msg = '250 Syntax: MAIL FROM: <address>'
                jeżeli self.extended_smtp:
                    msg += extended
                self.push(msg)
            albo_inaczej lc_arg == 'RCPT':
                msg = '250 Syntax: RCPT TO: <address>'
                jeżeli self.extended_smtp:
                    msg += extended
                self.push(msg)
            albo_inaczej lc_arg == 'DATA':
                self.push('250 Syntax: DATA')
            albo_inaczej lc_arg == 'RSET':
                self.push('250 Syntax: RSET')
            albo_inaczej lc_arg == 'NOOP':
                self.push('250 Syntax: NOOP')
            albo_inaczej lc_arg == 'QUIT':
                self.push('250 Syntax: QUIT')
            albo_inaczej lc_arg == 'VRFY':
                self.push('250 Syntax: VRFY <address>')
            inaczej:
                self.push('501 Supported commands: EHLO HELO MAIL RCPT '
                          'DATA RSET NOOP QUIT VRFY')
        inaczej:
            self.push('250 Supported commands: EHLO HELO MAIL RCPT DATA '
                      'RSET NOOP QUIT VRFY')

    def smtp_VRFY(self, arg):
        jeżeli arg:
            address, params = self._getaddr(arg)
            jeżeli address:
                self.push('252 Cannot VRFY user, but will accept message '
                          'and attempt delivery')
            inaczej:
                self.push('502 Could nie VRFY %s' % arg)
        inaczej:
            self.push('501 Syntax: VRFY <address>')

    def smtp_MAIL(self, arg):
        jeżeli nie self.seen_greeting:
            self.push('503 Error: send HELO first')
            zwróć
        print('===> MAIL', arg, file=DEBUGSTREAM)
        syntaxerr = '501 Syntax: MAIL FROM: <address>'
        jeżeli self.extended_smtp:
            syntaxerr += ' [SP <mail-parameters>]'
        jeżeli arg jest Nic:
            self.push(syntaxerr)
            zwróć
        arg = self._strip_command_keyword('FROM:', arg)
        address, params = self._getaddr(arg)
        jeżeli nie address:
            self.push(syntaxerr)
            zwróć
        jeżeli nie self.extended_smtp oraz params:
            self.push(syntaxerr)
            zwróć
        jeżeli self.mailfrom:
            self.push('503 Error: nested MAIL command')
            zwróć
        self.mail_options = params.upper().split()
        params = self._getparams(self.mail_options)
        jeżeli params jest Nic:
            self.push(syntaxerr)
            zwróć
        jeżeli nie self._decode_data:
            body = params.pop('BODY', '7BIT')
            jeżeli body nie w ['7BIT', '8BITMIME']:
                self.push('501 Error: BODY can only be one of 7BIT, 8BITMIME')
                zwróć
        jeżeli self.enable_SMTPUTF8:
            smtputf8 = params.pop('SMTPUTF8', Nieprawda)
            jeżeli smtputf8 jest Prawda:
                self.require_SMTPUTF8 = Prawda
            albo_inaczej smtputf8 jest nie Nieprawda:
                self.push('501 Error: SMTPUTF8 takes no arguments')
                zwróć
        size = params.pop('SIZE', Nic)
        jeżeli size:
            jeżeli nie size.isdigit():
                self.push(syntaxerr)
                zwróć
            albo_inaczej self.data_size_limit oraz int(size) > self.data_size_limit:
                self.push('552 Error: message size exceeds fixed maximum message size')
                zwróć
        jeżeli len(params.keys()) > 0:
            self.push('555 MAIL FROM parameters nie recognized albo nie implemented')
            zwróć
        self.mailz = address
        print('sender:', self.mailfrom, file=DEBUGSTREAM)
        self.push('250 OK')

    def smtp_RCPT(self, arg):
        jeżeli nie self.seen_greeting:
            self.push('503 Error: send HELO first');
            zwróć
        print('===> RCPT', arg, file=DEBUGSTREAM)
        jeżeli nie self.mailfrom:
            self.push('503 Error: need MAIL command')
            zwróć
        syntaxerr = '501 Syntax: RCPT TO: <address>'
        jeżeli self.extended_smtp:
            syntaxerr += ' [SP <mail-parameters>]'
        jeżeli arg jest Nic:
            self.push(syntaxerr)
            zwróć
        arg = self._strip_command_keyword('TO:', arg)
        address, params = self._getaddr(arg)
        jeżeli nie address:
            self.push(syntaxerr)
            zwróć
        jeżeli nie self.extended_smtp oraz params:
            self.push(syntaxerr)
            zwróć
        self.rcpt_options = params.upper().split()
        params = self._getparams(self.rcpt_options)
        jeżeli params jest Nic:
            self.push(syntaxerr)
            zwróć
        # XXX currently there are no options we recognize.
        jeżeli len(params.keys()) > 0:
            self.push('555 RCPT TO parameters nie recognized albo nie implemented')
            zwróć
        self.rcpttos.append(address)
        print('recips:', self.rcpttos, file=DEBUGSTREAM)
        self.push('250 OK')

    def smtp_RSET(self, arg):
        jeżeli arg:
            self.push('501 Syntax: RSET')
            zwróć
        self._set_rset_state()
        self.push('250 OK')

    def smtp_DATA(self, arg):
        jeżeli nie self.seen_greeting:
            self.push('503 Error: send HELO first');
            zwróć
        jeżeli nie self.rcpttos:
            self.push('503 Error: need RCPT command')
            zwróć
        jeżeli arg:
            self.push('501 Syntax: DATA')
            zwróć
        self.smtp_state = self.DATA
        self.set_terminator(b'\r\n.\r\n')
        self.push('354 End data przy <CR><LF>.<CR><LF>')

    # Commands that have nie been implemented
    def smtp_EXPN(self, arg):
        self.push('502 EXPN nie implemented')


klasa SMTPServer(asyncore.dispatcher):
    # SMTPChannel klasa to use dla managing client connections
    channel_class = SMTPChannel

    def __init__(self, localaddr, remoteaddr,
                 data_size_limit=DATA_SIZE_DEFAULT, map=Nic,
                 enable_SMTPUTF8=Nieprawda, decode_data=Nic):
        self._localaddr = localaddr
        self._remoteaddr = remoteaddr
        self.data_size_limit = data_size_limit
        self.enable_SMTPUTF8 = enable_SMTPUTF8
        jeżeli enable_SMTPUTF8:
            jeżeli decode_data:
                podnieś ValueError("The decode_data oraz enable_SMTPUTF8"
                                 " parameters cannot be set to Prawda at the"
                                 " same time.")
            decode_data = Nieprawda
        jeżeli decode_data jest Nic:
            warn("The decode_data default of Prawda will change to Nieprawda w 3.6;"
                 " specify an explicit value dla this keyword",
                 DeprecationWarning, 2)
            decode_data = Prawda
        self._decode_data = decode_data
        asyncore.dispatcher.__init__(self, map=map)
        spróbuj:
            gai_results = socket.getaddrinfo(*localaddr,
                                             type=socket.SOCK_STREAM)
            self.create_socket(gai_results[0][0], gai_results[0][1])
            # try to re-use a server port jeżeli possible
            self.set_reuse_addr()
            self.bind(localaddr)
            self.listen(5)
        wyjąwszy:
            self.close()
            podnieś
        inaczej:
            print('%s started at %s\n\tLocal addr: %s\n\tRemote addr:%s' % (
                self.__class__.__name__, time.ctime(time.time()),
                localaddr, remoteaddr), file=DEBUGSTREAM)

    def handle_accepted(self, conn, addr):
        print('Incoming connection z %s' % repr(addr), file=DEBUGSTREAM)
        channel = self.channel_class(self,
                                     conn,
                                     addr,
                                     self.data_size_limit,
                                     self._map,
                                     self.enable_SMTPUTF8,
                                     self._decode_data)

    # API dla "doing something useful przy the message"
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """Override this abstract method to handle messages z the client.

        peer jest a tuple containing (ipaddr, port) of the client that made the
        socket connection to our smtp port.

        mailz jest the raw address the client claims the message jest coming
        from.

        rcpttos jest a list of raw addresses the client wishes to deliver the
        message to.

        data jest a string containing the entire full text of the message,
        headers (jeżeli supplied) oraz all.  It has been `de-transparencied'
        according to RFC 821, Section 4.5.2.  In other words, a line
        containing a `.' followed by other text has had the leading dot
        removed.

        kwargs jest a dictionary containing additional information. It jest empty
        unless decode_data=Nieprawda albo enable_SMTPUTF8=Prawda was given jako init
        parameter, w which case ut will contain the following keys:
            'mail_options': list of parameters to the mail command.  All
                            elements are uppercase strings.  Example:
                            ['BODY=8BITMIME', 'SMTPUTF8'].
            'rcpt_options': same, dla the rcpt command.

        This function should zwróć Nic dla a normal `250 Ok' response;
        otherwise, it should zwróć the desired response string w RFC 821
        format.

        """
        podnieś NotImplementedError


klasa DebuggingServer(SMTPServer):

    def _print_message_content(self, peer, data):
        inheaders = 1
        lines = data.splitlines()
        dla line w lines:
            # headers first
            jeżeli inheaders oraz nie line:
                peerheader = 'X-Peer: ' + peer[0]
                jeżeli nie isinstance(data, str):
                    # decoded_data=false; make header match other binary output
                    peerheader = repr(peerheader.encode('utf-8'))
                print(peerheader)
                inheaders = 0
            jeżeli nie isinstance(data, str):
                # Avoid spurious 'str on bytes instance' warning.
                line = repr(line)
            print(line)

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print('---------- MESSAGE FOLLOWS ----------')
        jeżeli kwargs:
            jeżeli kwargs.get('mail_options'):
                print('mail options: %s' % kwargs['mail_options'])
            jeżeli kwargs.get('rcpt_options'):
                print('rcpt options: %s\n' % kwargs['rcpt_options'])
        self._print_message_content(peer, data)
        print('------------ END MESSAGE ------------')


klasa PureProxy(SMTPServer):
    def __init__(self, *args, **kwargs):
        jeżeli 'enable_SMTPUTF8' w kwargs oraz kwargs['enable_SMTPUTF8']:
            podnieś ValueError("PureProxy does nie support SMTPUTF8.")
        super(PureProxy, self).__init__(*args, **kwargs)

    def process_message(self, peer, mailfrom, rcpttos, data):
        lines = data.split('\n')
        # Look dla the last header
        i = 0
        dla line w lines:
            jeżeli nie line:
                przerwij
            i += 1
        lines.insert(i, 'X-Peer: %s' % peer[0])
        data = NEWLINE.join(lines)
        refused = self._deliver(mailfrom, rcpttos, data)
        # TBD: what to do przy refused addresses?
        print('we got some refusals:', refused, file=DEBUGSTREAM)

    def _deliver(self, mailfrom, rcpttos, data):
        zaimportuj smtplib
        refused = {}
        spróbuj:
            s = smtplib.SMTP()
            s.connect(self._remoteaddr[0], self._remoteaddr[1])
            spróbuj:
                refused = s.sendmail(mailfrom, rcpttos, data)
            w_końcu:
                s.quit()
        wyjąwszy smtplib.SMTPRecipientsRefused jako e:
            print('got SMTPRecipientsRefused', file=DEBUGSTREAM)
            refused = e.recipients
        wyjąwszy (OSError, smtplib.SMTPException) jako e:
            print('got', e.__class__, file=DEBUGSTREAM)
            # All recipients were refused.  If the exception had an associated
            # error code, use it.  Otherwise,fake it przy a non-triggering
            # exception code.
            errcode = getattr(e, 'smtp_code', -1)
            errmsg = getattr(e, 'smtp_error', 'ignore')
            dla r w rcpttos:
                refused[r] = (errcode, errmsg)
        zwróć refused


klasa MailmanProxy(PureProxy):
    def __init__(self, *args, **kwargs):
        jeżeli 'enable_SMTPUTF8' w kwargs oraz kwargs['enable_SMTPUTF8']:
            podnieś ValueError("MailmanProxy does nie support SMTPUTF8.")
        super(PureProxy, self).__init__(*args, **kwargs)

    def process_message(self, peer, mailfrom, rcpttos, data):
        z io zaimportuj StringIO
        z Mailman zaimportuj Utils
        z Mailman zaimportuj Message
        z Mailman zaimportuj MailList
        # If the message jest to a Mailman mailing list, then we'll invoke the
        # Mailman script directly, without going through the real smtpd.
        # Otherwise we'll forward it to the local proxy dla disposition.
        listnames = []
        dla rcpt w rcpttos:
            local = rcpt.lower().split('@')[0]
            # We allow the following variations on the theme
            #   listname
            #   listname-admin
            #   listname-owner
            #   listname-request
            #   listname-join
            #   listname-leave
            parts = local.split('-')
            jeżeli len(parts) > 2:
                kontynuuj
            listname = parts[0]
            jeżeli len(parts) == 2:
                command = parts[1]
            inaczej:
                command = ''
            jeżeli nie Utils.list_exists(listname) albo command nie w (
                    '', 'admin', 'owner', 'request', 'join', 'leave'):
                kontynuuj
            listnames.append((rcpt, listname, command))
        # Remove all list recipients z rcpttos oraz forward what we're nie
        # going to take care of ourselves.  Linear removal should be fine
        # since we don't expect a large number of recipients.
        dla rcpt, listname, command w listnames:
            rcpttos.remove(rcpt)
        # If there's any non-list destined recipients left,
        print('forwarding recips:', ' '.join(rcpttos), file=DEBUGSTREAM)
        jeżeli rcpttos:
            refused = self._deliver(mailfrom, rcpttos, data)
            # TBD: what to do przy refused addresses?
            print('we got refusals:', refused, file=DEBUGSTREAM)
        # Now deliver directly to the list commands
        mlists = {}
        s = StringIO(data)
        msg = Message.Message(s)
        # These headers are required dla the proper execution of Mailman.  All
        # MTAs w existence seem to add these jeżeli the original message doesn't
        # have them.
        jeżeli nie msg.get('from'):
            msg['From'] = mailfrom
        jeżeli nie msg.get('date'):
            msg['Date'] = time.ctime(time.time())
        dla rcpt, listname, command w listnames:
            print('sending message to', rcpt, file=DEBUGSTREAM)
            mlist = mlists.get(listname)
            jeżeli nie mlist:
                mlist = MailList.MailList(listname, lock=0)
                mlists[listname] = mlist
            # dispatch on the type of command
            jeżeli command == '':
                # post
                msg.Enqueue(mlist, tolist=1)
            albo_inaczej command == 'admin':
                msg.Enqueue(mlist, toadmin=1)
            albo_inaczej command == 'owner':
                msg.Enqueue(mlist, toowner=1)
            albo_inaczej command == 'request':
                msg.Enqueue(mlist, torequest=1)
            albo_inaczej command w ('join', 'leave'):
                # TBD: this jest a hack!
                jeżeli command == 'join':
                    msg['Subject'] = 'subscribe'
                inaczej:
                    msg['Subject'] = 'unsubscribe'
                msg.Enqueue(mlist, torequest=1)


klasa Options:
    setuid = Prawda
    classname = 'PureProxy'
    size_limit = Nic
    enable_SMTPUTF8 = Nieprawda


def parseargs():
    global DEBUGSTREAM
    spróbuj:
        opts, args = getopt.getopt(
            sys.argv[1:], 'nVhc:s:du',
            ['class=', 'nosetuid', 'version', 'help', 'size=', 'debug',
             'smtputf8'])
    wyjąwszy getopt.error jako e:
        usage(1, e)

    options = Options()
    dla opt, arg w opts:
        jeżeli opt w ('-h', '--help'):
            usage(0)
        albo_inaczej opt w ('-V', '--version'):
            print(__version__)
            sys.exit(0)
        albo_inaczej opt w ('-n', '--nosetuid'):
            options.setuid = Nieprawda
        albo_inaczej opt w ('-c', '--class'):
            options.classname = arg
        albo_inaczej opt w ('-d', '--debug'):
            DEBUGSTREAM = sys.stderr
        albo_inaczej opt w ('-u', '--smtputf8'):
            options.enable_SMTPUTF8 = Prawda
        albo_inaczej opt w ('-s', '--size'):
            spróbuj:
                int_size = int(arg)
                options.size_limit = int_size
            wyjąwszy:
                print('Invalid size: ' + arg, file=sys.stderr)
                sys.exit(1)

    # parse the rest of the arguments
    jeżeli len(args) < 1:
        localspec = 'localhost:8025'
        remotespec = 'localhost:25'
    albo_inaczej len(args) < 2:
        localspec = args[0]
        remotespec = 'localhost:25'
    albo_inaczej len(args) < 3:
        localspec = args[0]
        remotespec = args[1]
    inaczej:
        usage(1, 'Invalid arguments: %s' % COMMASPACE.join(args))

    # split into host/port pairs
    i = localspec.find(':')
    jeżeli i < 0:
        usage(1, 'Bad local spec: %s' % localspec)
    options.localhost = localspec[:i]
    spróbuj:
        options.localport = int(localspec[i+1:])
    wyjąwszy ValueError:
        usage(1, 'Bad local port: %s' % localspec)
    i = remotespec.find(':')
    jeżeli i < 0:
        usage(1, 'Bad remote spec: %s' % remotespec)
    options.remotehost = remotespec[:i]
    spróbuj:
        options.remoteport = int(remotespec[i+1:])
    wyjąwszy ValueError:
        usage(1, 'Bad remote port: %s' % remotespec)
    zwróć options


jeżeli __name__ == '__main__':
    options = parseargs()
    # Become nobody
    classname = options.classname
    jeżeli "." w classname:
        lastdot = classname.rfind(".")
        mod = __import__(classname[:lastdot], globals(), locals(), [""])
        classname = classname[lastdot+1:]
    inaczej:
        zaimportuj __main__ jako mod
    class_ = getattr(mod, classname)
    proxy = class_((options.localhost, options.localport),
                   (options.remotehost, options.remoteport),
                   options.size_limit, enable_SMTPUTF8=options.enable_SMTPUTF8)
    jeżeli options.setuid:
        spróbuj:
            zaimportuj pwd
        wyjąwszy ImportError:
            print('Cannot zaimportuj module "pwd"; try running przy -n option.', file=sys.stderr)
            sys.exit(1)
        nobody = pwd.getpwnam('nobody')[2]
        spróbuj:
            os.setuid(nobody)
        wyjąwszy PermissionError:
            print('Cannot setuid "nobody"; try running przy -n option.', file=sys.stderr)
            sys.exit(1)
    spróbuj:
        asyncore.loop()
    wyjąwszy KeyboardInterrupt:
        dalej
