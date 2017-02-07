r"""TELNET client class.

Based on RFC 854: TELNET Protocol Specification, by J. Postel oraz
J. Reynolds

Example:

>>> z telnetlib zaimportuj Telnet
>>> tn = Telnet('www.python.org', 79)   # connect to finger port
>>> tn.write(b'guido\r\n')
>>> print(tn.read_all())
Login       Name               TTY         Idle    When    Where
guido    Guido van Rossum      pts/2        <Dec  2 11:10> snag.cnri.reston..

>>>

Note that read_all() won't read until eof -- it just reads some data
-- but it guarantees to read at least one byte unless EOF jest hit.

It jest possible to dalej a Telnet object to a selector w order to wait until
more data jest available.  Note that w this case, read_eager() may zwróć b''
even jeżeli there was data on the socket, because the protocol negotiation may have
eaten the data.  This jest why EOFError jest needed w some cases to distinguish
between "no data" oraz "connection closed" (since the socket also appears ready
dla reading when it jest closed).

To do:
- option negotiation
- timeout should be intrinsic to the connection object instead of an
  option on one of the read calls only

"""


# Imported modules
zaimportuj sys
zaimportuj socket
zaimportuj selectors
z time zaimportuj monotonic jako _time

__all__ = ["Telnet"]

# Tunable parameters
DEBUGLEVEL = 0

# Telnet protocol defaults
TELNET_PORT = 23

# Telnet protocol characters (don't change)
IAC  = bytes([255]) # "Interpret As Command"
DONT = bytes([254])
DO   = bytes([253])
WONT = bytes([252])
WILL = bytes([251])
theNULL = bytes([0])

SE  = bytes([240])  # Subnegotiation End
NOP = bytes([241])  # No Operation
DM  = bytes([242])  # Data Mark
BRK = bytes([243])  # Break
IP  = bytes([244])  # Interrupt process
AO  = bytes([245])  # Abort output
AYT = bytes([246])  # Are You There
EC  = bytes([247])  # Erase Character
EL  = bytes([248])  # Erase Line
GA  = bytes([249])  # Go Ahead
SB =  bytes([250])  # Subnegotiation Begin


# Telnet protocol options code (don't change)
# These ones all come z arpa/telnet.h
BINARY = bytes([0]) # 8-bit data path
ECHO = bytes([1]) # echo
RCP = bytes([2]) # prepare to reconnect
SGA = bytes([3]) # suppress go ahead
NAMS = bytes([4]) # approximate message size
STATUS = bytes([5]) # give status
TM = bytes([6]) # timing mark
RCTE = bytes([7]) # remote controlled transmission oraz echo
NAOL = bytes([8]) # negotiate about output line width
NAOP = bytes([9]) # negotiate about output page size
NAOCRD = bytes([10]) # negotiate about CR disposition
NAOHTS = bytes([11]) # negotiate about horizontal tabstops
NAOHTD = bytes([12]) # negotiate about horizontal tab disposition
NAOFFD = bytes([13]) # negotiate about formfeed disposition
NAOVTS = bytes([14]) # negotiate about vertical tab stops
NAOVTD = bytes([15]) # negotiate about vertical tab disposition
NAOLFD = bytes([16]) # negotiate about output LF disposition
XASCII = bytes([17]) # extended ascii character set
LOGOUT = bytes([18]) # force logout
BM = bytes([19]) # byte macro
DET = bytes([20]) # data entry terminal
SUPDUP = bytes([21]) # supdup protocol
SUPDUPOUTPUT = bytes([22]) # supdup output
SNDLOC = bytes([23]) # send location
TTYPE = bytes([24]) # terminal type
EOR = bytes([25]) # end albo record
TUID = bytes([26]) # TACACS user identification
OUTMRK = bytes([27]) # output marking
TTYLOC = bytes([28]) # terminal location number
VT3270REGIME = bytes([29]) # 3270 regime
X3PAD = bytes([30]) # X.3 PAD
NAWS = bytes([31]) # window size
TSPEED = bytes([32]) # terminal speed
LFLOW = bytes([33]) # remote flow control
LINEMODE = bytes([34]) # Linemode option
XDISPLOC = bytes([35]) # X Display Location
OLD_ENVIRON = bytes([36]) # Old - Environment variables
AUTHENTICATION = bytes([37]) # Authenticate
ENCRYPT = bytes([38]) # Encryption option
NEW_ENVIRON = bytes([39]) # New - Environment variables
# the following ones come from
# http://www.iana.org/assignments/telnet-options
# Unfortunately, that document does nie assign identifiers
# to all of them, so we are making them up
TN3270E = bytes([40]) # TN3270E
XAUTH = bytes([41]) # XAUTH
CHARSET = bytes([42]) # CHARSET
RSP = bytes([43]) # Telnet Remote Serial Port
COM_PORT_OPTION = bytes([44]) # Com Port Control Option
SUPPRESS_LOCAL_ECHO = bytes([45]) # Telnet Suppress Local Echo
TLS = bytes([46]) # Telnet Start TLS
KERMIT = bytes([47]) # KERMIT
SEND_URL = bytes([48]) # SEND-URL
FORWARD_X = bytes([49]) # FORWARD_X
PRAGMA_LOGON = bytes([138]) # TELOPT PRAGMA LOGON
SSPI_LOGON = bytes([139]) # TELOPT SSPI LOGON
PRAGMA_HEARTBEAT = bytes([140]) # TELOPT PRAGMA HEARTBEAT
EXOPL = bytes([255]) # Extended-Options-List
NOOPT = bytes([0])


# poll/select have the advantage of nie requiring any extra file descriptor,
# contrarily to epoll/kqueue (also, they require a single syscall).
jeżeli hasattr(selectors, 'PollSelector'):
    _TelnetSelector = selectors.PollSelector
inaczej:
    _TelnetSelector = selectors.SelectSelector


klasa Telnet:

    """Telnet interface class.

    An instance of this klasa represents a connection to a telnet
    server.  The instance jest initially nie connected; the open()
    method must be used to establish a connection.  Alternatively, the
    host name oraz optional port number can be dalejed to the
    constructor, too.

    Don't try to reopen an already connected instance.

    This klasa has many read_*() methods.  Note that some of them
    podnieś EOFError when the end of the connection jest read, because
    they can zwróć an empty string dla other reasons.  See the
    individual doc strings.

    read_until(expected, [timeout])
        Read until the expected string has been seen, albo a timeout jest
        hit (default jest no timeout); may block.

    read_all()
        Read all data until EOF; may block.

    read_some()
        Read at least one byte albo EOF; may block.

    read_very_eager()
        Read all data available already queued albo on the socket,
        without blocking.

    read_eager()
        Read either data already queued albo some data available on the
        socket, without blocking.

    read_lazy()
        Read all data w the raw queue (processing it first), without
        doing any socket I/O.

    read_very_lazy()
        Reads all data w the cooked queue, without doing any socket
        I/O.

    read_sb_data()
        Reads available data between SB ... SE sequence. Don't block.

    set_option_negotiation_callback(callback)
        Each time a telnet option jest read on the input flow, this callback
        (jeżeli set) jest called przy the following parameters :
        callback(telnet socket, command, option)
            option will be chr(0) when there jest no option.
        No other action jest done afterwards by telnetlib.

    """

    def __init__(self, host=Nic, port=0,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Constructor.

        When called without arguments, create an unconnected instance.
        With a hostname argument, it connects the instance; port number
        oraz timeout are optional.
        """
        self.debuglevel = DEBUGLEVEL
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = Nic
        self.rawq = b''
        self.irawq = 0
        self.cookedq = b''
        self.eof = 0
        self.iacseq = b'' # Buffer dla IAC sequence.
        self.sb = 0 # flag dla SB oraz SE sequence.
        self.sbdataq = b''
        self.option_callback = Nic
        jeżeli host jest nie Nic:
            self.open(host, port, timeout)

    def open(self, host, port=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Connect to a host.

        The optional second argument jest the port number, which
        defaults to the standard telnet port (23).

        Don't try to reopen an already connected instance.
        """
        self.eof = 0
        jeżeli nie port:
            port = TELNET_PORT
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = socket.create_connection((host, port), timeout)

    def __del__(self):
        """Destructor -- close the connection."""
        self.close()

    def msg(self, msg, *args):
        """Print a debug message, when the debug level jest > 0.

        If extra arguments are present, they are substituted w the
        message using the standard string formatting operator.

        """
        jeżeli self.debuglevel > 0:
            print('Telnet(%s,%s):' % (self.host, self.port), end=' ')
            jeżeli args:
                print(msg % args)
            inaczej:
                print(msg)

    def set_debuglevel(self, debuglevel):
        """Set the debug level.

        The higher it is, the more debug output you get (on sys.stdout).

        """
        self.debuglevel = debuglevel

    def close(self):
        """Close the connection."""
        sock = self.sock
        self.sock = Nic
        self.eof = Prawda
        self.iacseq = b''
        self.sb = 0
        jeżeli sock:
            sock.close()

    def get_socket(self):
        """Return the socket object used internally."""
        zwróć self.sock

    def fileno(self):
        """Return the fileno() of the socket object used internally."""
        zwróć self.sock.fileno()

    def write(self, buffer):
        """Write a string to the socket, doubling any IAC characters.

        Can block jeżeli the connection jest blocked.  May podnieś
        OSError jeżeli the connection jest closed.

        """
        jeżeli IAC w buffer:
            buffer = buffer.replace(IAC, IAC+IAC)
        self.msg("send %r", buffer)
        self.sock.sendall(buffer)

    def read_until(self, match, timeout=Nic):
        """Read until a given string jest encountered albo until timeout.

        When no match jest found, zwróć whatever jest available instead,
        possibly the empty string.  Raise EOFError jeżeli the connection
        jest closed oraz no cooked data jest available.

        """
        n = len(match)
        self.process_rawq()
        i = self.cookedq.find(match)
        jeżeli i >= 0:
            i = i+n
            buf = self.cookedq[:i]
            self.cookedq = self.cookedq[i:]
            zwróć buf
        jeżeli timeout jest nie Nic:
            deadline = _time() + timeout
        przy _TelnetSelector() jako selector:
            selector.register(self, selectors.EVENT_READ)
            dopóki nie self.eof:
                jeżeli selector.select(timeout):
                    i = max(0, len(self.cookedq)-n)
                    self.fill_rawq()
                    self.process_rawq()
                    i = self.cookedq.find(match, i)
                    jeżeli i >= 0:
                        i = i+n
                        buf = self.cookedq[:i]
                        self.cookedq = self.cookedq[i:]
                        zwróć buf
                jeżeli timeout jest nie Nic:
                    timeout = deadline - _time()
                    jeżeli timeout < 0:
                        przerwij
        zwróć self.read_very_lazy()

    def read_all(self):
        """Read all data until EOF; block until connection closed."""
        self.process_rawq()
        dopóki nie self.eof:
            self.fill_rawq()
            self.process_rawq()
        buf = self.cookedq
        self.cookedq = b''
        zwróć buf

    def read_some(self):
        """Read at least one byte of cooked data unless EOF jest hit.

        Return b'' jeżeli EOF jest hit.  Block jeżeli no data jest immediately
        available.

        """
        self.process_rawq()
        dopóki nie self.cookedq oraz nie self.eof:
            self.fill_rawq()
            self.process_rawq()
        buf = self.cookedq
        self.cookedq = b''
        zwróć buf

    def read_very_eager(self):
        """Read everything that's possible without blocking w I/O (eager).

        Raise EOFError jeżeli connection closed oraz no cooked data
        available.  Return b'' jeżeli no cooked data available otherwise.
        Don't block unless w the midst of an IAC sequence.

        """
        self.process_rawq()
        dopóki nie self.eof oraz self.sock_avail():
            self.fill_rawq()
            self.process_rawq()
        zwróć self.read_very_lazy()

    def read_eager(self):
        """Read readily available data.

        Raise EOFError jeżeli connection closed oraz no cooked data
        available.  Return b'' jeżeli no cooked data available otherwise.
        Don't block unless w the midst of an IAC sequence.

        """
        self.process_rawq()
        dopóki nie self.cookedq oraz nie self.eof oraz self.sock_avail():
            self.fill_rawq()
            self.process_rawq()
        zwróć self.read_very_lazy()

    def read_lazy(self):
        """Process oraz zwróć data that's already w the queues (lazy).

        Raise EOFError jeżeli connection closed oraz no data available.
        Return b'' jeżeli no cooked data available otherwise.  Don't block
        unless w the midst of an IAC sequence.

        """
        self.process_rawq()
        zwróć self.read_very_lazy()

    def read_very_lazy(self):
        """Return any data available w the cooked queue (very lazy).

        Raise EOFError jeżeli connection closed oraz no data available.
        Return b'' jeżeli no cooked data available otherwise.  Don't block.

        """
        buf = self.cookedq
        self.cookedq = b''
        jeżeli nie buf oraz self.eof oraz nie self.rawq:
            podnieś EOFError('telnet connection closed')
        zwróć buf

    def read_sb_data(self):
        """Return any data available w the SB ... SE queue.

        Return b'' jeżeli no SB ... SE available. Should only be called
        after seeing a SB albo SE command. When a new SB command jest
        found, old unread SB data will be discarded. Don't block.

        """
        buf = self.sbdataq
        self.sbdataq = b''
        zwróć buf

    def set_option_negotiation_callback(self, callback):
        """Provide a callback function called after each receipt of a telnet option."""
        self.option_callback = callback

    def process_rawq(self):
        """Transfer z raw queue to cooked queue.

        Set self.eof when connection jest closed.  Don't block unless w
        the midst of an IAC sequence.

        """
        buf = [b'', b'']
        spróbuj:
            dopóki self.rawq:
                c = self.rawq_getchar()
                jeżeli nie self.iacseq:
                    jeżeli c == theNULL:
                        kontynuuj
                    jeżeli c == b"\021":
                        kontynuuj
                    jeżeli c != IAC:
                        buf[self.sb] = buf[self.sb] + c
                        kontynuuj
                    inaczej:
                        self.iacseq += c
                albo_inaczej len(self.iacseq) == 1:
                    # 'IAC: IAC CMD [OPTION only dla WILL/WONT/DO/DONT]'
                    jeżeli c w (DO, DONT, WILL, WONT):
                        self.iacseq += c
                        kontynuuj

                    self.iacseq = b''
                    jeżeli c == IAC:
                        buf[self.sb] = buf[self.sb] + c
                    inaczej:
                        jeżeli c == SB: # SB ... SE start.
                            self.sb = 1
                            self.sbdataq = b''
                        albo_inaczej c == SE:
                            self.sb = 0
                            self.sbdataq = self.sbdataq + buf[1]
                            buf[1] = b''
                        jeżeli self.option_callback:
                            # Callback jest supposed to look into
                            # the sbdataq
                            self.option_callback(self.sock, c, NOOPT)
                        inaczej:
                            # We can't offer automatic processing of
                            # suboptions. Alas, we should nie get any
                            # unless we did a WILL/DO before.
                            self.msg('IAC %d nie recognized' % ord(c))
                albo_inaczej len(self.iacseq) == 2:
                    cmd = self.iacseq[1:2]
                    self.iacseq = b''
                    opt = c
                    jeżeli cmd w (DO, DONT):
                        self.msg('IAC %s %d',
                            cmd == DO oraz 'DO' albo 'DONT', ord(opt))
                        jeżeli self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        inaczej:
                            self.sock.sendall(IAC + WONT + opt)
                    albo_inaczej cmd w (WILL, WONT):
                        self.msg('IAC %s %d',
                            cmd == WILL oraz 'WILL' albo 'WONT', ord(opt))
                        jeżeli self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        inaczej:
                            self.sock.sendall(IAC + DONT + opt)
        wyjąwszy EOFError: # podnieśd by self.rawq_getchar()
            self.iacseq = b'' # Reset on EOF
            self.sb = 0
            dalej
        self.cookedq = self.cookedq + buf[0]
        self.sbdataq = self.sbdataq + buf[1]

    def rawq_getchar(self):
        """Get next char z raw queue.

        Block jeżeli no data jest immediately available.  Raise EOFError
        when connection jest closed.

        """
        jeżeli nie self.rawq:
            self.fill_rawq()
            jeżeli self.eof:
                podnieś EOFError
        c = self.rawq[self.irawq:self.irawq+1]
        self.irawq = self.irawq + 1
        jeżeli self.irawq >= len(self.rawq):
            self.rawq = b''
            self.irawq = 0
        zwróć c

    def fill_rawq(self):
        """Fill raw queue z exactly one recv() system call.

        Block jeżeli no data jest immediately available.  Set self.eof when
        connection jest closed.

        """
        jeżeli self.irawq >= len(self.rawq):
            self.rawq = b''
            self.irawq = 0
        # The buffer size should be fairly small so jako to avoid quadratic
        # behavior w process_rawq() above
        buf = self.sock.recv(50)
        self.msg("recv %r", buf)
        self.eof = (nie buf)
        self.rawq = self.rawq + buf

    def sock_avail(self):
        """Test whether data jest available on the socket."""
        przy _TelnetSelector() jako selector:
            selector.register(self, selectors.EVENT_READ)
            zwróć bool(selector.select(0))

    def interact(self):
        """Interaction function, emulates a very dumb telnet client."""
        jeżeli sys.platform == "win32":
            self.mt_interact()
            zwróć
        przy _TelnetSelector() jako selector:
            selector.register(self, selectors.EVENT_READ)
            selector.register(sys.stdin, selectors.EVENT_READ)

            dopóki Prawda:
                dla key, events w selector.select():
                    jeżeli key.fileobj jest self:
                        spróbuj:
                            text = self.read_eager()
                        wyjąwszy EOFError:
                            print('*** Connection closed by remote host ***')
                            zwróć
                        jeżeli text:
                            sys.stdout.write(text.decode('ascii'))
                            sys.stdout.flush()
                    albo_inaczej key.fileobj jest sys.stdin:
                        line = sys.stdin.readline().encode('ascii')
                        jeżeli nie line:
                            zwróć
                        self.write(line)

    def mt_interact(self):
        """Multithreaded version of interact()."""
        zaimportuj _thread
        _thread.start_new_thread(self.listener, ())
        dopóki 1:
            line = sys.stdin.readline()
            jeżeli nie line:
                przerwij
            self.write(line.encode('ascii'))

    def listener(self):
        """Helper dla mt_interact() -- this executes w the other thread."""
        dopóki 1:
            spróbuj:
                data = self.read_eager()
            wyjąwszy EOFError:
                print('*** Connection closed by remote host ***')
                zwróć
            jeżeli data:
                sys.stdout.write(data.decode('ascii'))
            inaczej:
                sys.stdout.flush()

    def expect(self, list, timeout=Nic):
        """Read until one z a list of a regular expressions matches.

        The first argument jest a list of regular expressions, either
        compiled (re.RegexObject instances) albo uncompiled (strings).
        The optional second argument jest a timeout, w seconds; default
        jest no timeout.

        Return a tuple of three items: the index w the list of the
        first regular expression that matches; the match object
        returned; oraz the text read up till oraz including the match.

        If EOF jest read oraz no text was read, podnieś EOFError.
        Otherwise, when nothing matches, zwróć (-1, Nic, text) where
        text jest the text received so far (may be the empty string jeżeli a
        timeout happened).

        If a regular expression ends przy a greedy match (e.g. '.*')
        albo jeżeli more than one expression can match the same input, the
        results are undeterministic, oraz may depend on the I/O timing.

        """
        re = Nic
        list = list[:]
        indices = range(len(list))
        dla i w indices:
            jeżeli nie hasattr(list[i], "search"):
                jeżeli nie re: zaimportuj re
                list[i] = re.compile(list[i])
        jeżeli timeout jest nie Nic:
            deadline = _time() + timeout
        przy _TelnetSelector() jako selector:
            selector.register(self, selectors.EVENT_READ)
            dopóki nie self.eof:
                self.process_rawq()
                dla i w indices:
                    m = list[i].search(self.cookedq)
                    jeżeli m:
                        e = m.end()
                        text = self.cookedq[:e]
                        self.cookedq = self.cookedq[e:]
                        zwróć (i, m, text)
                jeżeli timeout jest nie Nic:
                    ready = selector.select(timeout)
                    timeout = deadline - _time()
                    jeżeli nie ready:
                        jeżeli timeout < 0:
                            przerwij
                        inaczej:
                            kontynuuj
                self.fill_rawq()
        text = self.read_very_lazy()
        jeżeli nie text oraz self.eof:
            podnieś EOFError
        zwróć (-1, Nic, text)


def test():
    """Test program dla telnetlib.

    Usage: python telnetlib.py [-d] ... [host [port]]

    Default host jest localhost; default port jest 23.

    """
    debuglevel = 0
    dopóki sys.argv[1:] oraz sys.argv[1] == '-d':
        debuglevel = debuglevel+1
        usuń sys.argv[1]
    host = 'localhost'
    jeżeli sys.argv[1:]:
        host = sys.argv[1]
    port = 0
    jeżeli sys.argv[2:]:
        portstr = sys.argv[2]
        spróbuj:
            port = int(portstr)
        wyjąwszy ValueError:
            port = socket.getservbyname(portstr, 'tcp')
    tn = Telnet()
    tn.set_debuglevel(debuglevel)
    tn.open(host, port, timeout=0.5)
    tn.interact()
    tn.close()

jeżeli __name__ == '__main__':
    test()
