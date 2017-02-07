"""An FTP client klasa oraz some helper functions.

Based on RFC 959: File Transfer Protocol (FTP), by J. Postel oraz J. Reynolds

Example:

>>> z ftplib zaimportuj FTP
>>> ftp = FTP('ftp.python.org') # connect to host, default port
>>> ftp.login() # default, i.e.: user anonymous, dalejwd anonymous@
'230 Guest login ok, access restrictions apply.'
>>> ftp.retrlines('LIST') # list directory contents
total 9
drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 .
drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 ..
drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 bin
drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 etc
d-wxrwxr-x   2 ftp      wheel        1024 Sep  5 13:43 incoming
drwxr-xr-x   2 root     wheel        1024 Nov 17  1993 lib
drwxr-xr-x   6 1094     wheel        1024 Sep 13 19:07 pub
drwxr-xr-x   3 root     wheel        1024 Jan  3  1994 usr
-rw-r--r--   1 root     root          312 Aug  1  1994 welcome.msg
'226 Transfer complete.'
>>> ftp.quit()
'221 Goodbye.'
>>>

A nice test that reveals some of the network dialogue would be:
python ftplib.py -d localhost -l -p -l
"""

#
# Changes oraz improvements suggested by Steve Majewski.
# Modified by Jack to work on the mac.
# Modified by Siebren to support docstrings oraz PASV.
# Modified by Phil Schwartz to add storbinary oraz storlines callbacks.
# Modified by Giampaolo Rodola' to add TLS support.
#

zaimportuj os
zaimportuj sys
zaimportuj socket
zaimportuj warnings
z socket zaimportuj _GLOBAL_DEFAULT_TIMEOUT

__all__ = ["FTP"]

# Magic number z <socket.h>
MSG_OOB = 0x1                           # Process data out of band


# The standard FTP server control port
FTP_PORT = 21
# The sizehint parameter dalejed to readline() calls
MAXLINE = 8192


# Exception podnieśd when an error albo invalid response jest received
klasa Error(Exception): dalej
klasa error_reply(Error): dalej          # unexpected [123]xx reply
klasa error_temp(Error): dalej           # 4xx errors
klasa error_perm(Error): dalej           # 5xx errors
klasa error_proto(Error): dalej          # response does nie begin przy [1-5]


# All exceptions (hopefully) that may be podnieśd here oraz that aren't
# (always) programming errors on our side
all_errors = (Error, OSError, EOFError)


# Line terminators (we always output CRLF, but accept any of CRLF, CR, LF)
CRLF = '\r\n'
B_CRLF = b'\r\n'

# The klasa itself
klasa FTP:

    '''An FTP client class.

    To create a connection, call the klasa using these arguments:
            host, user, dalejwd, acct, timeout

    The first four arguments are all strings, oraz have default value ''.
    timeout must be numeric oraz defaults to Nic jeżeli nie dalejed,
    meaning that no timeout will be set on any ftp socket(s)
    If a timeout jest dalejed, then this jest now the default timeout dla all ftp
    socket operations dla this instance.

    Then use self.connect() przy optional host oraz port argument.

    To download a file, use ftp.retrlines('RETR ' + filename),
    albo ftp.retrbinary() przy slightly different arguments.
    To upload a file, use ftp.storlines() albo ftp.storbinary(),
    which have an open file jako argument (see their definitions
    below dla details).
    The download/upload functions first issue appropriate TYPE
    oraz PORT albo PASV commands.
    '''

    debugging = 0
    host = ''
    port = FTP_PORT
    maxline = MAXLINE
    sock = Nic
    file = Nic
    welcome = Nic
    dalejiveserver = 1
    encoding = "latin-1"

    # Initialization method (called by klasa instantiation).
    # Initialize host to localhost, port to standard ftp port
    # Optional arguments are host (dla connect()),
    # oraz user, dalejwd, acct (dla login())
    def __init__(self, host='', user='', dalejwd='', acct='',
                 timeout=_GLOBAL_DEFAULT_TIMEOUT, source_address=Nic):
        self.source_address = source_address
        self.timeout = timeout
        jeżeli host:
            self.connect(host)
            jeżeli user:
                self.login(user, dalejwd, acct)

    def __enter__(self):
        zwróć self

    # Context management protocol: try to quit() jeżeli active
    def __exit__(self, *args):
        jeżeli self.sock jest nie Nic:
            spróbuj:
                self.quit()
            wyjąwszy (OSError, EOFError):
                dalej
            w_końcu:
                jeżeli self.sock jest nie Nic:
                    self.close()

    def connect(self, host='', port=0, timeout=-999, source_address=Nic):
        '''Connect to host.  Arguments are:
         - host: hostname to connect to (string, default previous host)
         - port: port to connect to (integer, default previous port)
         - timeout: the timeout to set against the ftp socket(s)
         - source_address: a 2-tuple (host, port) dla the socket to bind
           to jako its source address before connecting.
        '''
        jeżeli host != '':
            self.host = host
        jeżeli port > 0:
            self.port = port
        jeżeli timeout != -999:
            self.timeout = timeout
        jeżeli source_address jest nie Nic:
            self.source_address = source_address
        self.sock = socket.create_connection((self.host, self.port), self.timeout,
                                             source_address=self.source_address)
        self.af = self.sock.family
        self.file = self.sock.makefile('r', encoding=self.encoding)
        self.welcome = self.getresp()
        zwróć self.welcome

    def getwelcome(self):
        '''Get the welcome message z the server.
        (this jest read oraz squirreled away by connect())'''
        jeżeli self.debugging:
            print('*welcome*', self.sanitize(self.welcome))
        zwróć self.welcome

    def set_debuglevel(self, level):
        '''Set the debugging level.
        The required argument level means:
        0: no debugging output (default)
        1: print commands oraz responses but nie body text etc.
        2: also print raw lines read oraz sent before stripping CR/LF'''
        self.debugging = level
    debug = set_debuglevel

    def set_pasv(self, val):
        '''Use dalejive albo active mode dla data transfers.
        With a false argument, use the normal PORT mode,
        With a true argument, use the PASV command.'''
        self.passiveserver = val

    # Internal: "sanitize" a string dla printing
    def sanitize(self, s):
        jeżeli s[:5] w {'pass ', 'PASS '}:
            i = len(s.rstrip('\r\n'))
            s = s[:5] + '*'*(i-5) + s[i:]
        zwróć repr(s)

    # Internal: send one line to the server, appending CRLF
    def putline(self, line):
        line = line + CRLF
        jeżeli self.debugging > 1:
            print('*put*', self.sanitize(line))
        self.sock.sendall(line.encode(self.encoding))

    # Internal: send one command to the server (through putline())
    def putcmd(self, line):
        jeżeli self.debugging: print('*cmd*', self.sanitize(line))
        self.putline(line)

    # Internal: zwróć one line z the server, stripping CRLF.
    # Raise EOFError jeżeli the connection jest closed
    def getline(self):
        line = self.file.readline(self.maxline + 1)
        jeżeli len(line) > self.maxline:
            podnieś Error("got more than %d bytes" % self.maxline)
        jeżeli self.debugging > 1:
            print('*get*', self.sanitize(line))
        jeżeli nie line:
            podnieś EOFError
        jeżeli line[-2:] == CRLF:
            line = line[:-2]
        albo_inaczej line[-1:] w CRLF:
            line = line[:-1]
        zwróć line

    # Internal: get a response z the server, which may possibly
    # consist of multiple lines.  Return a single string przy no
    # trailing CRLF.  If the response consists of multiple lines,
    # these are separated by '\n' characters w the string
    def getmultiline(self):
        line = self.getline()
        jeżeli line[3:4] == '-':
            code = line[:3]
            dopóki 1:
                nextline = self.getline()
                line = line + ('\n' + nextline)
                jeżeli nextline[:3] == code oraz \
                        nextline[3:4] != '-':
                    przerwij
        zwróć line

    # Internal: get a response z the server.
    # Raise various errors jeżeli the response indicates an error
    def getresp(self):
        resp = self.getmultiline()
        jeżeli self.debugging:
            print('*resp*', self.sanitize(resp))
        self.lastresp = resp[:3]
        c = resp[:1]
        jeżeli c w {'1', '2', '3'}:
            zwróć resp
        jeżeli c == '4':
            podnieś error_temp(resp)
        jeżeli c == '5':
            podnieś error_perm(resp)
        podnieś error_proto(resp)

    def voidresp(self):
        """Expect a response beginning przy '2'."""
        resp = self.getresp()
        jeżeli resp[:1] != '2':
            podnieś error_reply(resp)
        zwróć resp

    def abort(self):
        '''Abort a file transfer.  Uses out-of-band data.
        This does nie follow the procedure z the RFC to send Telnet
        IP oraz Synch; that doesn't seem to work przy the servers I've
        tried.  Instead, just send the ABOR command jako OOB data.'''
        line = b'ABOR' + B_CRLF
        jeżeli self.debugging > 1:
            print('*put urgent*', self.sanitize(line))
        self.sock.sendall(line, MSG_OOB)
        resp = self.getmultiline()
        jeżeli resp[:3] nie w {'426', '225', '226'}:
            podnieś error_proto(resp)
        zwróć resp

    def sendcmd(self, cmd):
        '''Send a command oraz zwróć the response.'''
        self.putcmd(cmd)
        zwróć self.getresp()

    def voidcmd(self, cmd):
        """Send a command oraz expect a response beginning przy '2'."""
        self.putcmd(cmd)
        zwróć self.voidresp()

    def sendport(self, host, port):
        '''Send a PORT command przy the current host oraz the given
        port number.
        '''
        hbytes = host.split('.')
        pbytes = [repr(port//256), repr(port%256)]
        bytes = hbytes + pbytes
        cmd = 'PORT ' + ','.join(bytes)
        zwróć self.voidcmd(cmd)

    def sendeprt(self, host, port):
        '''Send a EPRT command przy the current host oraz the given port number.'''
        af = 0
        jeżeli self.af == socket.AF_INET:
            af = 1
        jeżeli self.af == socket.AF_INET6:
            af = 2
        jeżeli af == 0:
            podnieś error_proto('unsupported address family')
        fields = ['', repr(af), host, repr(port), '']
        cmd = 'EPRT ' + '|'.join(fields)
        zwróć self.voidcmd(cmd)

    def makeport(self):
        '''Create a new socket oraz send a PORT command dla it.'''
        err = Nic
        sock = Nic
        dla res w socket.getaddrinfo(Nic, 0, self.af, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            af, socktype, proto, canonname, sa = res
            spróbuj:
                sock = socket.socket(af, socktype, proto)
                sock.bind(sa)
            wyjąwszy OSError jako _:
                err = _
                jeżeli sock:
                    sock.close()
                sock = Nic
                kontynuuj
            przerwij
        jeżeli sock jest Nic:
            jeżeli err jest nie Nic:
                podnieś err
            inaczej:
                podnieś OSError("getaddrinfo returns an empty list")
        sock.listen(1)
        port = sock.getsockname()[1] # Get proper port
        host = self.sock.getsockname()[0] # Get proper host
        jeżeli self.af == socket.AF_INET:
            resp = self.sendport(host, port)
        inaczej:
            resp = self.sendeprt(host, port)
        jeżeli self.timeout jest nie _GLOBAL_DEFAULT_TIMEOUT:
            sock.settimeout(self.timeout)
        zwróć sock

    def makepasv(self):
        jeżeli self.af == socket.AF_INET:
            host, port = parse227(self.sendcmd('PASV'))
        inaczej:
            host, port = parse229(self.sendcmd('EPSV'), self.sock.getpeername())
        zwróć host, port

    def ntransfercmd(self, cmd, rest=Nic):
        """Initiate a transfer over the data connection.

        If the transfer jest active, send a port command oraz the
        transfer command, oraz accept the connection.  If the server jest
        dalejive, send a pasv command, connect to it, oraz start the
        transfer command.  Either way, zwróć the socket dla the
        connection oraz the expected size of the transfer.  The
        expected size may be Nic jeżeli it could nie be determined.

        Optional `rest' argument can be a string that jest sent jako the
        argument to a REST command.  This jest essentially a server
        marker used to tell the server to skip over any data up to the
        given marker.
        """
        size = Nic
        jeżeli self.passiveserver:
            host, port = self.makepasv()
            conn = socket.create_connection((host, port), self.timeout,
                                            source_address=self.source_address)
            spróbuj:
                jeżeli rest jest nie Nic:
                    self.sendcmd("REST %s" % rest)
                resp = self.sendcmd(cmd)
                # Some servers apparently send a 200 reply to
                # a LIST albo STOR command, before the 150 reply
                # (and way before the 226 reply). This seems to
                # be w violation of the protocol (which only allows
                # 1xx albo error messages dla LIST), so we just discard
                # this response.
                jeżeli resp[0] == '2':
                    resp = self.getresp()
                jeżeli resp[0] != '1':
                    podnieś error_reply(resp)
            wyjąwszy:
                conn.close()
                podnieś
        inaczej:
            przy self.makeport() jako sock:
                jeżeli rest jest nie Nic:
                    self.sendcmd("REST %s" % rest)
                resp = self.sendcmd(cmd)
                # See above.
                jeżeli resp[0] == '2':
                    resp = self.getresp()
                jeżeli resp[0] != '1':
                    podnieś error_reply(resp)
                conn, sockaddr = sock.accept()
                jeżeli self.timeout jest nie _GLOBAL_DEFAULT_TIMEOUT:
                    conn.settimeout(self.timeout)
        jeżeli resp[:3] == '150':
            # this jest conditional w case we received a 125
            size = parse150(resp)
        zwróć conn, size

    def transfercmd(self, cmd, rest=Nic):
        """Like ntransfercmd() but returns only the socket."""
        zwróć self.ntransfercmd(cmd, rest)[0]

    def login(self, user = '', dalejwd = '', acct = ''):
        '''Login, default anonymous.'''
        jeżeli nie user:
            user = 'anonymous'
        jeżeli nie dalejwd:
            dalejwd = ''
        jeżeli nie acct:
            acct = ''
        jeżeli user == 'anonymous' oraz dalejwd w {'', '-'}:
            # If there jest no anonymous ftp dalejword specified
            # then we'll just use anonymous@
            # We don't send any other thing because:
            # - We want to remain anonymous
            # - We want to stop SPAM
            # - We don't want to let ftp sites to discriminate by the user,
            #   host albo country.
            dalejwd = dalejwd + 'anonymous@'
        resp = self.sendcmd('USER ' + user)
        jeżeli resp[0] == '3':
            resp = self.sendcmd('PASS ' + dalejwd)
        jeżeli resp[0] == '3':
            resp = self.sendcmd('ACCT ' + acct)
        jeżeli resp[0] != '2':
            podnieś error_reply(resp)
        zwróć resp

    def retrbinary(self, cmd, callback, blocksize=8192, rest=Nic):
        """Retrieve data w binary mode.  A new port jest created dla you.

        Args:
          cmd: A RETR command.
          callback: A single parameter callable to be called on each
                    block of data read.
          blocksize: The maximum number of bytes to read z the
                     socket at one time.  [default: 8192]
          rest: Passed to transfercmd().  [default: Nic]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE I')
        przy self.transfercmd(cmd, rest) jako conn:
            dopóki 1:
                data = conn.recv(blocksize)
                jeżeli nie data:
                    przerwij
                callback(data)
            # shutdown ssl layer
            jeżeli _SSLSocket jest nie Nic oraz isinstance(conn, _SSLSocket):
                conn.unwrap()
        zwróć self.voidresp()

    def retrlines(self, cmd, callback = Nic):
        """Retrieve data w line mode.  A new port jest created dla you.

        Args:
          cmd: A RETR, LIST, albo NLST command.
          callback: An optional single parameter callable that jest called
                    dla each line przy the trailing CRLF stripped.
                    [default: print_line()]

        Returns:
          The response code.
        """
        jeżeli callback jest Nic:
            callback = print_line
        resp = self.sendcmd('TYPE A')
        przy self.transfercmd(cmd) jako conn, \
                 conn.makefile('r', encoding=self.encoding) jako fp:
            dopóki 1:
                line = fp.readline(self.maxline + 1)
                jeżeli len(line) > self.maxline:
                    podnieś Error("got more than %d bytes" % self.maxline)
                jeżeli self.debugging > 2:
                    print('*retr*', repr(line))
                jeżeli nie line:
                    przerwij
                jeżeli line[-2:] == CRLF:
                    line = line[:-2]
                albo_inaczej line[-1:] == '\n':
                    line = line[:-1]
                callback(line)
            # shutdown ssl layer
            jeżeli _SSLSocket jest nie Nic oraz isinstance(conn, _SSLSocket):
                conn.unwrap()
        zwróć self.voidresp()

    def storbinary(self, cmd, fp, blocksize=8192, callback=Nic, rest=Nic):
        """Store a file w binary mode.  A new port jest created dla you.

        Args:
          cmd: A STOR command.
          fp: A file-like object przy a read(num_bytes) method.
          blocksize: The maximum data size to read z fp oraz send over
                     the connection at once.  [default: 8192]
          callback: An optional single parameter callable that jest called on
                    each block of data after it jest sent.  [default: Nic]
          rest: Passed to transfercmd().  [default: Nic]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE I')
        przy self.transfercmd(cmd, rest) jako conn:
            dopóki 1:
                buf = fp.read(blocksize)
                jeżeli nie buf:
                    przerwij
                conn.sendall(buf)
                jeżeli callback:
                    callback(buf)
            # shutdown ssl layer
            jeżeli _SSLSocket jest nie Nic oraz isinstance(conn, _SSLSocket):
                conn.unwrap()
        zwróć self.voidresp()

    def storlines(self, cmd, fp, callback=Nic):
        """Store a file w line mode.  A new port jest created dla you.

        Args:
          cmd: A STOR command.
          fp: A file-like object przy a readline() method.
          callback: An optional single parameter callable that jest called on
                    each line after it jest sent.  [default: Nic]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE A')
        przy self.transfercmd(cmd) jako conn:
            dopóki 1:
                buf = fp.readline(self.maxline + 1)
                jeżeli len(buf) > self.maxline:
                    podnieś Error("got more than %d bytes" % self.maxline)
                jeżeli nie buf:
                    przerwij
                jeżeli buf[-2:] != B_CRLF:
                    jeżeli buf[-1] w B_CRLF: buf = buf[:-1]
                    buf = buf + B_CRLF
                conn.sendall(buf)
                jeżeli callback:
                    callback(buf)
            # shutdown ssl layer
            jeżeli _SSLSocket jest nie Nic oraz isinstance(conn, _SSLSocket):
                conn.unwrap()
        zwróć self.voidresp()

    def acct(self, dalejword):
        '''Send new account name.'''
        cmd = 'ACCT ' + dalejword
        zwróć self.voidcmd(cmd)

    def nlst(self, *args):
        '''Return a list of files w a given directory (default the current).'''
        cmd = 'NLST'
        dla arg w args:
            cmd = cmd + (' ' + arg)
        files = []
        self.retrlines(cmd, files.append)
        zwróć files

    def dir(self, *args):
        '''List a directory w long form.
        By default list current directory to stdout.
        Optional last argument jest callback function; all
        non-empty arguments before it are concatenated to the
        LIST command.  (This *should* only be used dla a pathname.)'''
        cmd = 'LIST'
        func = Nic
        jeżeli args[-1:] oraz type(args[-1]) != type(''):
            args, func = args[:-1], args[-1]
        dla arg w args:
            jeżeli arg:
                cmd = cmd + (' ' + arg)
        self.retrlines(cmd, func)

    def mlsd(self, path="", facts=[]):
        '''List a directory w a standardized format by using MLSD
        command (RFC-3659). If path jest omitted the current directory
        jest assumed. "facts" jest a list of strings representing the type
        of information desired (e.g. ["type", "size", "perm"]).

        Return a generator object uzyskajing a tuple of two elements
        dla every file found w path.
        First element jest the file name, the second one jest a dictionary
        including a variable number of "facts" depending on the server
        oraz whether "facts" argument has been provided.
        '''
        jeżeli facts:
            self.sendcmd("OPTS MLST " + ";".join(facts) + ";")
        jeżeli path:
            cmd = "MLSD %s" % path
        inaczej:
            cmd = "MLSD"
        lines = []
        self.retrlines(cmd, lines.append)
        dla line w lines:
            facts_found, _, name = line.rstrip(CRLF).partition(' ')
            entry = {}
            dla fact w facts_found[:-1].split(";"):
                key, _, value = fact.partition("=")
                entry[key.lower()] = value
            uzyskaj (name, entry)

    def rename(self, fromname, toname):
        '''Rename a file.'''
        resp = self.sendcmd('RNFR ' + fromname)
        jeżeli resp[0] != '3':
            podnieś error_reply(resp)
        zwróć self.voidcmd('RNTO ' + toname)

    def delete(self, filename):
        '''Delete a file.'''
        resp = self.sendcmd('DELE ' + filename)
        jeżeli resp[:3] w {'250', '200'}:
            zwróć resp
        inaczej:
            podnieś error_reply(resp)

    def cwd(self, dirname):
        '''Change to a directory.'''
        jeżeli dirname == '..':
            spróbuj:
                zwróć self.voidcmd('CDUP')
            wyjąwszy error_perm jako msg:
                jeżeli msg.args[0][:3] != '500':
                    podnieś
        albo_inaczej dirname == '':
            dirname = '.'  # does nothing, but could zwróć error
        cmd = 'CWD ' + dirname
        zwróć self.voidcmd(cmd)

    def size(self, filename):
        '''Retrieve the size of a file.'''
        # The SIZE command jest defined w RFC-3659
        resp = self.sendcmd('SIZE ' + filename)
        jeżeli resp[:3] == '213':
            s = resp[3:].strip()
            zwróć int(s)

    def mkd(self, dirname):
        '''Make a directory, zwróć its full pathname.'''
        resp = self.voidcmd('MKD ' + dirname)
        # fix around non-compliant implementations such jako IIS shipped
        # przy Windows server 2003
        jeżeli nie resp.startswith('257'):
            zwróć ''
        zwróć parse257(resp)

    def rmd(self, dirname):
        '''Remove a directory.'''
        zwróć self.voidcmd('RMD ' + dirname)

    def pwd(self):
        '''Return current working directory.'''
        resp = self.voidcmd('PWD')
        # fix around non-compliant implementations such jako IIS shipped
        # przy Windows server 2003
        jeżeli nie resp.startswith('257'):
            zwróć ''
        zwróć parse257(resp)

    def quit(self):
        '''Quit, oraz close the connection.'''
        resp = self.voidcmd('QUIT')
        self.close()
        zwróć resp

    def close(self):
        '''Close the connection without assuming anything about it.'''
        spróbuj:
            file = self.file
            self.file = Nic
            jeżeli file jest nie Nic:
                file.close()
        w_końcu:
            sock = self.sock
            self.sock = Nic
            jeżeli sock jest nie Nic:
                sock.close()

spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    _SSLSocket = Nic
inaczej:
    _SSLSocket = ssl.SSLSocket

    klasa FTP_TLS(FTP):
        '''A FTP subclass which adds TLS support to FTP jako described
        w RFC-4217.

        Connect jako usual to port 21 implicitly securing the FTP control
        connection before authenticating.

        Securing the data connection requires user to explicitly ask
        dla it by calling prot_p() method.

        Usage example:
        >>> z ftplib zaimportuj FTP_TLS
        >>> ftps = FTP_TLS('ftp.python.org')
        >>> ftps.login()  # login anonymously previously securing control channel
        '230 Guest login ok, access restrictions apply.'
        >>> ftps.prot_p()  # switch to secure data connection
        '200 Protection level set to P'
        >>> ftps.retrlines('LIST')  # list directory content securely
        total 9
        drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 .
        drwxr-xr-x   8 root     wheel        1024 Jan  3  1994 ..
        drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 bin
        drwxr-xr-x   2 root     wheel        1024 Jan  3  1994 etc
        d-wxrwxr-x   2 ftp      wheel        1024 Sep  5 13:43 incoming
        drwxr-xr-x   2 root     wheel        1024 Nov 17  1993 lib
        drwxr-xr-x   6 1094     wheel        1024 Sep 13 19:07 pub
        drwxr-xr-x   3 root     wheel        1024 Jan  3  1994 usr
        -rw-r--r--   1 root     root          312 Aug  1  1994 welcome.msg
        '226 Transfer complete.'
        >>> ftps.quit()
        '221 Goodbye.'
        >>>
        '''
        ssl_version = ssl.PROTOCOL_SSLv23

        def __init__(self, host='', user='', dalejwd='', acct='', keyfile=Nic,
                     certfile=Nic, context=Nic,
                     timeout=_GLOBAL_DEFAULT_TIMEOUT, source_address=Nic):
            jeżeli context jest nie Nic oraz keyfile jest nie Nic:
                podnieś ValueError("context oraz keyfile arguments are mutually "
                                 "exclusive")
            jeżeli context jest nie Nic oraz certfile jest nie Nic:
                podnieś ValueError("context oraz certfile arguments are mutually "
                                 "exclusive")
            self.keyfile = keyfile
            self.certfile = certfile
            jeżeli context jest Nic:
                context = ssl._create_stdlib_context(self.ssl_version,
                                                     certfile=certfile,
                                                     keyfile=keyfile)
            self.context = context
            self._prot_p = Nieprawda
            FTP.__init__(self, host, user, dalejwd, acct, timeout, source_address)

        def login(self, user='', dalejwd='', acct='', secure=Prawda):
            jeżeli secure oraz nie isinstance(self.sock, ssl.SSLSocket):
                self.auth()
            zwróć FTP.login(self, user, dalejwd, acct)

        def auth(self):
            '''Set up secure control connection by using TLS/SSL.'''
            jeżeli isinstance(self.sock, ssl.SSLSocket):
                podnieś ValueError("Already using TLS")
            jeżeli self.ssl_version >= ssl.PROTOCOL_SSLv23:
                resp = self.voidcmd('AUTH TLS')
            inaczej:
                resp = self.voidcmd('AUTH SSL')
            self.sock = self.context.wrap_socket(self.sock,
                                                 server_hostname=self.host)
            self.file = self.sock.makefile(mode='r', encoding=self.encoding)
            zwróć resp

        def ccc(self):
            '''Switch back to a clear-text control connection.'''
            jeżeli nie isinstance(self.sock, ssl.SSLSocket):
                podnieś ValueError("not using TLS")
            resp = self.voidcmd('CCC')
            self.sock = self.sock.unwrap()
            zwróć resp

        def prot_p(self):
            '''Set up secure data connection.'''
            # PROT defines whether albo nie the data channel jest to be protected.
            # Though RFC-2228 defines four possible protection levels,
            # RFC-4217 only recommends two, Clear oraz Private.
            # Clear (PROT C) means that no security jest to be used on the
            # data-channel, Private (PROT P) means that the data-channel
            # should be protected by TLS.
            # PBSZ command MUST still be issued, but must have a parameter of
            # '0' to indicate that no buffering jest taking place oraz the data
            # connection should nie be encapsulated.
            self.voidcmd('PBSZ 0')
            resp = self.voidcmd('PROT P')
            self._prot_p = Prawda
            zwróć resp

        def prot_c(self):
            '''Set up clear text data connection.'''
            resp = self.voidcmd('PROT C')
            self._prot_p = Nieprawda
            zwróć resp

        # --- Overridden FTP methods

        def ntransfercmd(self, cmd, rest=Nic):
            conn, size = FTP.ntransfercmd(self, cmd, rest)
            jeżeli self._prot_p:
                conn = self.context.wrap_socket(conn,
                                                server_hostname=self.host)
            zwróć conn, size

        def abort(self):
            # overridden jako we can't dalej MSG_OOB flag to sendall()
            line = b'ABOR' + B_CRLF
            self.sock.sendall(line)
            resp = self.getmultiline()
            jeżeli resp[:3] nie w {'426', '225', '226'}:
                podnieś error_proto(resp)
            zwróć resp

    __all__.append('FTP_TLS')
    all_errors = (Error, OSError, EOFError, ssl.SSLError)


_150_re = Nic

def parse150(resp):
    '''Parse the '150' response dla a RETR request.
    Returns the expected transfer size albo Nic; size jest nie guaranteed to
    be present w the 150 message.
    '''
    jeżeli resp[:3] != '150':
        podnieś error_reply(resp)
    global _150_re
    jeżeli _150_re jest Nic:
        zaimportuj re
        _150_re = re.compile(
            "150 .* \((\d+) bytes\)", re.IGNORECASE | re.ASCII)
    m = _150_re.match(resp)
    jeżeli nie m:
        zwróć Nic
    zwróć int(m.group(1))


_227_re = Nic

def parse227(resp):
    '''Parse the '227' response dla a PASV request.
    Raises error_proto jeżeli it does nie contain '(h1,h2,h3,h4,p1,p2)'
    Return ('host.addr.as.numbers', port#) tuple.'''

    jeżeli resp[:3] != '227':
        podnieś error_reply(resp)
    global _227_re
    jeżeli _227_re jest Nic:
        zaimportuj re
        _227_re = re.compile(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', re.ASCII)
    m = _227_re.search(resp)
    jeżeli nie m:
        podnieś error_proto(resp)
    numbers = m.groups()
    host = '.'.join(numbers[:4])
    port = (int(numbers[4]) << 8) + int(numbers[5])
    zwróć host, port


def parse229(resp, peer):
    '''Parse the '229' response dla a EPSV request.
    Raises error_proto jeżeli it does nie contain '(|||port|)'
    Return ('host.addr.as.numbers', port#) tuple.'''

    jeżeli resp[:3] != '229':
        podnieś error_reply(resp)
    left = resp.find('(')
    jeżeli left < 0: podnieś error_proto(resp)
    right = resp.find(')', left + 1)
    jeżeli right < 0:
        podnieś error_proto(resp) # should contain '(|||port|)'
    jeżeli resp[left + 1] != resp[right - 1]:
        podnieś error_proto(resp)
    parts = resp[left + 1:right].split(resp[left+1])
    jeżeli len(parts) != 5:
        podnieś error_proto(resp)
    host = peer[0]
    port = int(parts[3])
    zwróć host, port


def parse257(resp):
    '''Parse the '257' response dla a MKD albo PWD request.
    This jest a response to a MKD albo PWD request: a directory name.
    Returns the directoryname w the 257 reply.'''

    jeżeli resp[:3] != '257':
        podnieś error_reply(resp)
    jeżeli resp[3:5] != ' "':
        zwróć '' # Not compliant to RFC 959, but UNIX ftpd does this
    dirname = ''
    i = 5
    n = len(resp)
    dopóki i < n:
        c = resp[i]
        i = i+1
        jeżeli c == '"':
            jeżeli i >= n albo resp[i] != '"':
                przerwij
            i = i+1
        dirname = dirname + c
    zwróć dirname


def print_line(line):
    '''Default retrlines callback to print a line.'''
    print(line)


def ftpcp(source, sourcename, target, targetname = '', type = 'I'):
    '''Copy file z one FTP-instance to another.'''
    jeżeli nie targetname:
        targetname = sourcename
    type = 'TYPE ' + type
    source.voidcmd(type)
    target.voidcmd(type)
    sourcehost, sourceport = parse227(source.sendcmd('PASV'))
    target.sendport(sourcehost, sourceport)
    # RFC 959: the user must "listen" [...] BEFORE sending the
    # transfer request.
    # So: STOR before RETR, because here the target jest a "user".
    treply = target.sendcmd('STOR ' + targetname)
    jeżeli treply[:3] nie w {'125', '150'}:
        podnieś error_proto  # RFC 959
    sreply = source.sendcmd('RETR ' + sourcename)
    jeżeli sreply[:3] nie w {'125', '150'}:
        podnieś error_proto  # RFC 959
    source.voidresp()
    target.voidresp()


def test():
    '''Test program.
    Usage: ftp [-d] [-r[file]] host [-l[dir]] [-d[dir]] [-p] [file] ...

    -d dir
    -l list
    -p dalejword
    '''

    jeżeli len(sys.argv) < 2:
        print(test.__doc__)
        sys.exit(0)

    zaimportuj netrc

    debugging = 0
    rcfile = Nic
    dopóki sys.argv[1] == '-d':
        debugging = debugging+1
        usuń sys.argv[1]
    jeżeli sys.argv[1][:2] == '-r':
        # get name of alternate ~/.netrc file:
        rcfile = sys.argv[1][2:]
        usuń sys.argv[1]
    host = sys.argv[1]
    ftp = FTP(host)
    ftp.set_debuglevel(debugging)
    userid = dalejwd = acct = ''
    spróbuj:
        netrcobj = netrc.netrc(rcfile)
    wyjąwszy OSError:
        jeżeli rcfile jest nie Nic:
            sys.stderr.write("Could nie open account file"
                             " -- using anonymous login.")
    inaczej:
        spróbuj:
            userid, acct, dalejwd = netrcobj.authenticators(host)
        wyjąwszy KeyError:
            # no account dla host
            sys.stderr.write(
                    "No account -- using anonymous login.")
    ftp.login(userid, dalejwd, acct)
    dla file w sys.argv[2:]:
        jeżeli file[:2] == '-l':
            ftp.dir(file[2:])
        albo_inaczej file[:2] == '-d':
            cmd = 'CWD'
            jeżeli file[2:]: cmd = cmd + ' ' + file[2:]
            resp = ftp.sendcmd(cmd)
        albo_inaczej file == '-p':
            ftp.set_pasv(nie ftp.passiveserver)
        inaczej:
            ftp.retrbinary('RETR ' + file, \
                           sys.stdout.write, 1024)
    ftp.quit()


jeżeli __name__ == '__main__':
    test()
