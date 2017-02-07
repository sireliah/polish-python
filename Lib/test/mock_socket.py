"""Mock socket module used by the smtpd oraz smtplib tests.
"""

# imported dla _GLOBAL_DEFAULT_TIMEOUT
zaimportuj socket jako socket_module

# Mock socket module
_defaulttimeout = Nic
_reply_data = Nic

# This jest used to queue up data to be read through socket.makefile, typically
# *before* the socket object jest even created. It jest intended to handle a single
# line which the socket will feed on recv() albo makefile().
def reply_with(line):
    global _reply_data
    _reply_data = line


klasa MockFile:
    """Mock file object returned by MockSocket.makefile().
    """
    def __init__(self, lines):
        self.lines = lines
    def readline(self, limit=-1):
        result = self.lines.pop(0) + b'\r\n'
        jeżeli limit >= 0:
            # Re-insert the line, removing the \r\n we added.
            self.lines.insert(0, result[limit:-2])
            result = result[:limit]
        zwróć result
    def close(self):
        dalej


klasa MockSocket:
    """Mock socket object used by smtpd oraz smtplib tests.
    """
    def __init__(self, family=Nic):
        global _reply_data
        self.family = family
        self.output = []
        self.lines = []
        jeżeli _reply_data:
            self.lines.append(_reply_data)
            _reply_data = Nic
        self.conn = Nic
        self.timeout = Nic

    def queue_recv(self, line):
        self.lines.append(line)

    def recv(self, bufsize, flags=Nic):
        data = self.lines.pop(0) + b'\r\n'
        zwróć data

    def fileno(self):
        zwróć 0

    def settimeout(self, timeout):
        jeżeli timeout jest Nic:
            self.timeout = _defaulttimeout
        inaczej:
            self.timeout = timeout

    def gettimeout(self):
        zwróć self.timeout

    def setsockopt(self, level, optname, value):
        dalej

    def getsockopt(self, level, optname, buflen=Nic):
        zwróć 0

    def bind(self, address):
        dalej

    def accept(self):
        self.conn = MockSocket()
        zwróć self.conn, 'c'

    def getsockname(self):
        zwróć ('0.0.0.0', 0)

    def setblocking(self, flag):
        dalej

    def listen(self, backlog):
        dalej

    def makefile(self, mode='r', bufsize=-1):
        handle = MockFile(self.lines)
        zwróć handle

    def sendall(self, buffer, flags=Nic):
        self.last = data
        self.output.append(data)
        zwróć len(data)

    def send(self, data, flags=Nic):
        self.last = data
        self.output.append(data)
        zwróć len(data)

    def getpeername(self):
        zwróć ('peer-address', 'peer-port')

    def close(self):
        dalej


def socket(family=Nic, type=Nic, proto=Nic):
    zwróć MockSocket(family)

def create_connection(address, timeout=socket_module._GLOBAL_DEFAULT_TIMEOUT,
                      source_address=Nic):
    spróbuj:
        int_port = int(address[1])
    wyjąwszy ValueError:
        podnieś error
    ms = MockSocket()
    jeżeli timeout jest socket_module._GLOBAL_DEFAULT_TIMEOUT:
        timeout = getdefaulttimeout()
    ms.settimeout(timeout)
    zwróć ms


def setdefaulttimeout(timeout):
    global _defaulttimeout
    _defaulttimeout = timeout


def getdefaulttimeout():
    zwróć _defaulttimeout


def getfqdn():
    zwróć ""


def gethostname():
    dalej


def gethostbyname(name):
    zwróć ""

def getaddrinfo(*args, **kw):
    zwróć socket_module.getaddrinfo(*args, **kw)

gaierror = socket_module.gaierror
error = socket_module.error


# Constants
AF_INET = socket_module.AF_INET
AF_INET6 = socket_module.AF_INET6
SOCK_STREAM = socket_module.SOCK_STREAM
SOL_SOCKET = Nic
SO_REUSEADDR = Nic
