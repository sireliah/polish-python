zaimportuj unittest
z test zaimportuj support

zaimportuj errno
zaimportuj io
zaimportuj itertools
zaimportuj socket
zaimportuj select
zaimportuj tempfile
zaimportuj time
zaimportuj traceback
zaimportuj queue
zaimportuj sys
zaimportuj os
zaimportuj array
zaimportuj platform
zaimportuj contextlib
z weakref zaimportuj proxy
zaimportuj signal
zaimportuj math
zaimportuj pickle
zaimportuj struct
zaimportuj random
zaimportuj string
spróbuj:
    zaimportuj multiprocessing
wyjąwszy ImportError:
    multiprocessing = Nieprawda
spróbuj:
    zaimportuj fcntl
wyjąwszy ImportError:
    fcntl = Nic

HOST = support.HOST
MSG = 'Michael Gilfix was here\u1234\r\n'.encode('utf-8') ## test unicode string oraz carriage zwróć

spróbuj:
    zaimportuj _thread jako thread
    zaimportuj threading
wyjąwszy ImportError:
    thread = Nic
    threading = Nic
spróbuj:
    zaimportuj _socket
wyjąwszy ImportError:
    _socket = Nic


def _have_socket_can():
    """Check whether CAN sockets are supported on this host."""
    spróbuj:
        s = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    wyjąwszy (AttributeError, OSError):
        zwróć Nieprawda
    inaczej:
        s.close()
    zwróć Prawda

def _have_socket_rds():
    """Check whether RDS sockets are supported on this host."""
    spróbuj:
        s = socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0)
    wyjąwszy (AttributeError, OSError):
        zwróć Nieprawda
    inaczej:
        s.close()
    zwróć Prawda

HAVE_SOCKET_CAN = _have_socket_can()

HAVE_SOCKET_RDS = _have_socket_rds()

# Size w bytes of the int type
SIZEOF_INT = array.array("i").itemsize

klasa SocketTCPTest(unittest.TestCase):

    def setUp(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = support.bind_port(self.serv)
        self.serv.listen()

    def tearDown(self):
        self.serv.close()
        self.serv = Nic

klasa SocketUDPTest(unittest.TestCase):

    def setUp(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = support.bind_port(self.serv)

    def tearDown(self):
        self.serv.close()
        self.serv = Nic

klasa ThreadSafeCleanupTestCase(unittest.TestCase):
    """Subclass of unittest.TestCase przy thread-safe cleanup methods.

    This subclass protects the addCleanup() oraz doCleanups() methods
    przy a recursive lock.
    """

    jeżeli threading:
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._cleanup_lock = threading.RLock()

        def addCleanup(self, *args, **kwargs):
            przy self._cleanup_lock:
                zwróć super().addCleanup(*args, **kwargs)

        def doCleanups(self, *args, **kwargs):
            przy self._cleanup_lock:
                zwróć super().doCleanups(*args, **kwargs)

klasa SocketCANTest(unittest.TestCase):

    """To be able to run this test, a `vcan0` CAN interface can be created with
    the following commands:
    # modprobe vcan
    # ip link add dev vcan0 type vcan
    # ifconfig vcan0 up
    """
    interface = 'vcan0'
    bufsize = 128

    """The CAN frame structure jest defined w <linux/can.h>:

    struct can_frame {
        canid_t can_id;  /* 32 bit CAN_ID + EFF/RTR/ERR flags */
        __u8    can_dlc; /* data length code: 0 .. 8 */
        __u8    data[8] __attribute__((aligned(8)));
    };
    """
    can_frame_fmt = "=IB3x8s"
    can_frame_size = struct.calcsize(can_frame_fmt)

    """The Broadcast Management Command frame structure jest defined
    w <linux/can/bcm.h>:

    struct bcm_msg_head {
        __u32 opcode;
        __u32 flags;
        __u32 count;
        struct timeval ival1, ival2;
        canid_t can_id;
        __u32 nframes;
        struct can_frame frames[0];
    }

    `bcm_msg_head` must be 8 bytes aligned because of the `frames` member (see
    `struct can_frame` definition). Must use native nie standard types dla packing.
    """
    bcm_cmd_msg_fmt = "@3I4l2I"
    bcm_cmd_msg_fmt += "x" * (struct.calcsize(bcm_cmd_msg_fmt) % 8)

    def setUp(self):
        self.s = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.addCleanup(self.s.close)
        spróbuj:
            self.s.bind((self.interface,))
        wyjąwszy OSError:
            self.skipTest('network interface `%s` does nie exist' %
                           self.interface)


klasa SocketRDSTest(unittest.TestCase):

    """To be able to run this test, the `rds` kernel module must be loaded:
    # modprobe rds
    """
    bufsize = 8192

    def setUp(self):
        self.serv = socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0)
        self.addCleanup(self.serv.close)
        spróbuj:
            self.port = support.bind_port(self.serv)
        wyjąwszy OSError:
            self.skipTest('unable to bind RDS socket')


klasa ThreadableTest:
    """Threadable Test class

    The ThreadableTest klasa makes it easy to create a threaded
    client/server pair z an existing unit test. To create a
    new threaded klasa z an existing unit test, use multiple
    inheritance:

        klasa NewClass (OldClass, ThreadableTest):
            dalej

    This klasa defines two new fixture functions przy obvious
    purposes dla overriding:

        clientSetUp ()
        clientTearDown ()

    Any new test functions within the klasa must then define
    tests w pairs, where the test name jest preceeded przy a
    '_' to indicate the client portion of the test. Ex:

        def testFoo(self):
            # Server portion

        def _testFoo(self):
            # Client portion

    Any exceptions podnieśd by the clients during their tests
    are caught oraz transferred to the main thread to alert
    the testing framework.

    Note, the server setup function cannot call any blocking
    functions that rely on the client thread during setup,
    unless serverExplicitReady() jest called just before
    the blocking call (such jako w setting up a client/server
    connection oraz performing the accept() w setUp().
    """

    def __init__(self):
        # Swap the true setup function
        self.__setUp = self.setUp
        self.__tearDown = self.tearDown
        self.setUp = self._setUp
        self.tearDown = self._tearDown

    def serverExplicitReady(self):
        """This method allows the server to explicitly indicate that
        it wants the client thread to proceed. This jest useful jeżeli the
        server jest about to execute a blocking routine that jest
        dependent upon the client thread during its setup routine."""
        self.server_ready.set()

    def _setUp(self):
        self.server_ready = threading.Event()
        self.client_ready = threading.Event()
        self.done = threading.Event()
        self.queue = queue.Queue(1)
        self.server_crashed = Nieprawda

        # Do some munging to start the client test.
        methodname = self.id()
        i = methodname.rfind('.')
        methodname = methodname[i+1:]
        test_method = getattr(self, '_' + methodname)
        self.client_thread = thread.start_new_thread(
            self.clientRun, (test_method,))

        spróbuj:
            self.__setUp()
        wyjąwszy:
            self.server_crashed = Prawda
            podnieś
        w_końcu:
            self.server_ready.set()
        self.client_ready.wait()

    def _tearDown(self):
        self.__tearDown()
        self.done.wait()

        jeżeli self.queue.qsize():
            exc = self.queue.get()
            podnieś exc

    def clientRun(self, test_func):
        self.server_ready.wait()
        self.clientSetUp()
        self.client_ready.set()
        jeżeli self.server_crashed:
            self.clientTearDown()
            zwróć
        jeżeli nie hasattr(test_func, '__call__'):
            podnieś TypeError("test_func must be a callable function")
        spróbuj:
            test_func()
        wyjąwszy BaseException jako e:
            self.queue.put(e)
        w_końcu:
            self.clientTearDown()

    def clientSetUp(self):
        podnieś NotImplementedError("clientSetUp must be implemented.")

    def clientTearDown(self):
        self.done.set()
        thread.exit()

klasa ThreadedTCPSocketTest(SocketTCPTest, ThreadableTest):

    def __init__(self, methodName='runTest'):
        SocketTCPTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    def clientSetUp(self):
        self.cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def clientTearDown(self):
        self.cli.close()
        self.cli = Nic
        ThreadableTest.clientTearDown(self)

klasa ThreadedUDPSocketTest(SocketUDPTest, ThreadableTest):

    def __init__(self, methodName='runTest'):
        SocketUDPTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    def clientSetUp(self):
        self.cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def clientTearDown(self):
        self.cli.close()
        self.cli = Nic
        ThreadableTest.clientTearDown(self)

klasa ThreadedCANSocketTest(SocketCANTest, ThreadableTest):

    def __init__(self, methodName='runTest'):
        SocketCANTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    def clientSetUp(self):
        self.cli = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        spróbuj:
            self.cli.bind((self.interface,))
        wyjąwszy OSError:
            # skipTest should nie be called here, oraz will be called w the
            # server instead
            dalej

    def clientTearDown(self):
        self.cli.close()
        self.cli = Nic
        ThreadableTest.clientTearDown(self)

klasa ThreadedRDSSocketTest(SocketRDSTest, ThreadableTest):

    def __init__(self, methodName='runTest'):
        SocketRDSTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    def clientSetUp(self):
        self.cli = socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0)
        spróbuj:
            # RDS sockets must be bound explicitly to send albo receive data
            self.cli.bind((HOST, 0))
            self.cli_addr = self.cli.getsockname()
        wyjąwszy OSError:
            # skipTest should nie be called here, oraz will be called w the
            # server instead
            dalej

    def clientTearDown(self):
        self.cli.close()
        self.cli = Nic
        ThreadableTest.clientTearDown(self)

klasa SocketConnectedTest(ThreadedTCPSocketTest):
    """Socket tests dla client-server connection.

    self.cli_conn jest a client socket connected to the server.  The
    setUp() method guarantees that it jest connected to the server.
    """

    def __init__(self, methodName='runTest'):
        ThreadedTCPSocketTest.__init__(self, methodName=methodName)

    def setUp(self):
        ThreadedTCPSocketTest.setUp(self)
        # Indicate explicitly we're ready dla the client thread to
        # proceed oraz then perform the blocking call to accept
        self.serverExplicitReady()
        conn, addr = self.serv.accept()
        self.cli_conn = conn

    def tearDown(self):
        self.cli_conn.close()
        self.cli_conn = Nic
        ThreadedTCPSocketTest.tearDown(self)

    def clientSetUp(self):
        ThreadedTCPSocketTest.clientSetUp(self)
        self.cli.connect((HOST, self.port))
        self.serv_conn = self.cli

    def clientTearDown(self):
        self.serv_conn.close()
        self.serv_conn = Nic
        ThreadedTCPSocketTest.clientTearDown(self)

klasa SocketPairTest(unittest.TestCase, ThreadableTest):

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    def setUp(self):
        self.serv, self.cli = socket.socketpair()

    def tearDown(self):
        self.serv.close()
        self.serv = Nic

    def clientSetUp(self):
        dalej

    def clientTearDown(self):
        self.cli.close()
        self.cli = Nic
        ThreadableTest.clientTearDown(self)


# The following classes are used by the sendmsg()/recvmsg() tests.
# Combining, dla instance, ConnectedStreamTestMixin oraz TCPTestBase
# gives a drop-in replacement dla SocketConnectedTest, but different
# address families can be used, oraz the attributes serv_addr oraz
# cli_addr will be set to the addresses of the endpoints.

klasa SocketTestBase(unittest.TestCase):
    """A base klasa dla socket tests.

    Subclasses must provide methods newSocket() to zwróć a new socket
    oraz bindSock(sock) to bind it to an unused address.

    Creates a socket self.serv oraz sets self.serv_addr to its address.
    """

    def setUp(self):
        self.serv = self.newSocket()
        self.bindServer()

    def bindServer(self):
        """Bind server socket oraz set self.serv_addr to its address."""
        self.bindSock(self.serv)
        self.serv_addr = self.serv.getsockname()

    def tearDown(self):
        self.serv.close()
        self.serv = Nic


klasa SocketListeningTestMixin(SocketTestBase):
    """Mixin to listen on the server socket."""

    def setUp(self):
        super().setUp()
        self.serv.listen()


klasa ThreadedSocketTestMixin(ThreadSafeCleanupTestCase, SocketTestBase,
                              ThreadableTest):
    """Mixin to add client socket oraz allow client/server tests.

    Client socket jest self.cli oraz its address jest self.cli_addr.  See
    ThreadableTest dla usage information.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ThreadableTest.__init__(self)

    def clientSetUp(self):
        self.cli = self.newClientSocket()
        self.bindClient()

    def newClientSocket(self):
        """Return a new socket dla use jako client."""
        zwróć self.newSocket()

    def bindClient(self):
        """Bind client socket oraz set self.cli_addr to its address."""
        self.bindSock(self.cli)
        self.cli_addr = self.cli.getsockname()

    def clientTearDown(self):
        self.cli.close()
        self.cli = Nic
        ThreadableTest.clientTearDown(self)


klasa ConnectedStreamTestMixin(SocketListeningTestMixin,
                               ThreadedSocketTestMixin):
    """Mixin to allow client/server stream tests przy connected client.

    Server's socket representing connection to client jest self.cli_conn
    oraz client's connection to server jest self.serv_conn.  (Based on
    SocketConnectedTest.)
    """

    def setUp(self):
        super().setUp()
        # Indicate explicitly we're ready dla the client thread to
        # proceed oraz then perform the blocking call to accept
        self.serverExplicitReady()
        conn, addr = self.serv.accept()
        self.cli_conn = conn

    def tearDown(self):
        self.cli_conn.close()
        self.cli_conn = Nic
        super().tearDown()

    def clientSetUp(self):
        super().clientSetUp()
        self.cli.connect(self.serv_addr)
        self.serv_conn = self.cli

    def clientTearDown(self):
        self.serv_conn.close()
        self.serv_conn = Nic
        super().clientTearDown()


klasa UnixSocketTestBase(SocketTestBase):
    """Base klasa dla Unix-domain socket tests."""

    # This klasa jest used dla file descriptor dalejing tests, so we
    # create the sockets w a private directory so that other users
    # can't send anything that might be problematic dla a privileged
    # user running the tests.

    def setUp(self):
        self.dir_path = tempfile.mkdtemp()
        self.addCleanup(os.rmdir, self.dir_path)
        super().setUp()

    def bindSock(self, sock):
        path = tempfile.mktemp(dir=self.dir_path)
        sock.bind(path)
        self.addCleanup(support.unlink, path)

klasa UnixStreamBase(UnixSocketTestBase):
    """Base klasa dla Unix-domain SOCK_STREAM tests."""

    def newSocket(self):
        zwróć socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)


klasa InetTestBase(SocketTestBase):
    """Base klasa dla IPv4 socket tests."""

    host = HOST

    def setUp(self):
        super().setUp()
        self.port = self.serv_addr[1]

    def bindSock(self, sock):
        support.bind_port(sock, host=self.host)

klasa TCPTestBase(InetTestBase):
    """Base klasa dla TCP-over-IPv4 tests."""

    def newSocket(self):
        zwróć socket.socket(socket.AF_INET, socket.SOCK_STREAM)

klasa UDPTestBase(InetTestBase):
    """Base klasa dla UDP-over-IPv4 tests."""

    def newSocket(self):
        zwróć socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

klasa SCTPStreamBase(InetTestBase):
    """Base klasa dla SCTP tests w one-to-one (SOCK_STREAM) mode."""

    def newSocket(self):
        zwróć socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                             socket.IPPROTO_SCTP)


klasa Inet6TestBase(InetTestBase):
    """Base klasa dla IPv6 socket tests."""

    host = support.HOSTv6

klasa UDP6TestBase(Inet6TestBase):
    """Base klasa dla UDP-over-IPv6 tests."""

    def newSocket(self):
        zwróć socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)


# Test-skipping decorators dla use przy ThreadableTest.

def skipWithClientIf(condition, reason):
    """Skip decorated test jeżeli condition jest true, add client_skip decorator.

    If the decorated object jest nie a class, sets its attribute
    "client_skip" to a decorator which will zwróć an empty function
    jeżeli the test jest to be skipped, albo the original function jeżeli it jest
    not.  This can be used to avoid running the client part of a
    skipped test when using ThreadableTest.
    """
    def client_pass(*args, **kwargs):
        dalej
    def skipdec(obj):
        retval = unittest.skip(reason)(obj)
        jeżeli nie isinstance(obj, type):
            retval.client_skip = lambda f: client_pass
        zwróć retval
    def noskipdec(obj):
        jeżeli nie (isinstance(obj, type) albo hasattr(obj, "client_skip")):
            obj.client_skip = lambda f: f
        zwróć obj
    zwróć skipdec jeżeli condition inaczej noskipdec


def requireAttrs(obj, *attributes):
    """Skip decorated test jeżeli obj jest missing any of the given attributes.

    Sets client_skip attribute jako skipWithClientIf() does.
    """
    missing = [name dla name w attributes jeżeli nie hasattr(obj, name)]
    zwróć skipWithClientIf(
        missing, "don't have " + ", ".join(name dla name w missing))


def requireSocket(*args):
    """Skip decorated test jeżeli a socket cannot be created przy given arguments.

    When an argument jest given jako a string, will use the value of that
    attribute of the socket module, albo skip the test jeżeli it doesn't
    exist.  Sets client_skip attribute jako skipWithClientIf() does.
    """
    err = Nic
    missing = [obj dla obj w args if
               isinstance(obj, str) oraz nie hasattr(socket, obj)]
    jeżeli missing:
        err = "don't have " + ", ".join(name dla name w missing)
    inaczej:
        callargs = [getattr(socket, obj) jeżeli isinstance(obj, str) inaczej obj
                    dla obj w args]
        spróbuj:
            s = socket.socket(*callargs)
        wyjąwszy OSError jako e:
            # XXX: check errno?
            err = str(e)
        inaczej:
            s.close()
    zwróć skipWithClientIf(
        err jest nie Nic,
        "can't create socket({0}): {1}".format(
            ", ".join(str(o) dla o w args), err))


#######################################################################
## Begin Tests

klasa GeneralModuleTests(unittest.TestCase):

    def test_SocketType_is_socketobject(self):
        zaimportuj _socket
        self.assertPrawda(socket.SocketType jest _socket.socket)
        s = socket.socket()
        self.assertIsInstance(s, socket.SocketType)
        s.close()

    def test_repr(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        przy s:
            self.assertIn('fd=%i' % s.fileno(), repr(s))
            self.assertIn('family=%s' % socket.AF_INET, repr(s))
            self.assertIn('type=%s' % socket.SOCK_STREAM, repr(s))
            self.assertIn('proto=0', repr(s))
            self.assertNotIn('raddr', repr(s))
            s.bind(('127.0.0.1', 0))
            self.assertIn('laddr', repr(s))
            self.assertIn(str(s.getsockname()), repr(s))
        self.assertIn('[closed]', repr(s))
        self.assertNotIn('laddr', repr(s))

    @unittest.skipUnless(_socket jest nie Nic, 'need _socket module')
    def test_csocket_repr(self):
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        spróbuj:
            expected = ('<socket object, fd=%s, family=%s, type=%s, proto=%s>'
                        % (s.fileno(), s.family, s.type, s.proto))
            self.assertEqual(repr(s), expected)
        w_końcu:
            s.close()
        expected = ('<socket object, fd=-1, family=%s, type=%s, proto=%s>'
                    % (s.family, s.type, s.proto))
        self.assertEqual(repr(s), expected)

    def test_weakref(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p = proxy(s)
        self.assertEqual(p.fileno(), s.fileno())
        s.close()
        s = Nic
        spróbuj:
            p.fileno()
        wyjąwszy ReferenceError:
            dalej
        inaczej:
            self.fail('Socket proxy still exists')

    def testSocketError(self):
        # Testing socket module exceptions
        msg = "Error raising socket exception (%s)."
        przy self.assertRaises(OSError, msg=msg % 'OSError'):
            podnieś OSError
        przy self.assertRaises(OSError, msg=msg % 'socket.herror'):
            podnieś socket.herror
        przy self.assertRaises(OSError, msg=msg % 'socket.gaierror'):
            podnieś socket.gaierror

    def testSendtoErrors(self):
        # Testing that sendto doesn't masks failures. See #10169.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(s.close)
        s.bind(('', 0))
        sockname = s.getsockname()
        # 2 args
        przy self.assertRaises(TypeError) jako cm:
            s.sendto('\u2620', sockname)
        self.assertEqual(str(cm.exception),
                         "a bytes-like object jest required, nie 'str'")
        przy self.assertRaises(TypeError) jako cm:
            s.sendto(5j, sockname)
        self.assertEqual(str(cm.exception),
                         "a bytes-like object jest required, nie 'complex'")
        przy self.assertRaises(TypeError) jako cm:
            s.sendto(b'foo', Nic)
        self.assertIn('not NicType',str(cm.exception))
        # 3 args
        przy self.assertRaises(TypeError) jako cm:
            s.sendto('\u2620', 0, sockname)
        self.assertEqual(str(cm.exception),
                         "a bytes-like object jest required, nie 'str'")
        przy self.assertRaises(TypeError) jako cm:
            s.sendto(5j, 0, sockname)
        self.assertEqual(str(cm.exception),
                         "a bytes-like object jest required, nie 'complex'")
        przy self.assertRaises(TypeError) jako cm:
            s.sendto(b'foo', 0, Nic)
        self.assertIn('not NicType', str(cm.exception))
        przy self.assertRaises(TypeError) jako cm:
            s.sendto(b'foo', 'bar', sockname)
        self.assertIn('an integer jest required', str(cm.exception))
        przy self.assertRaises(TypeError) jako cm:
            s.sendto(b'foo', Nic, Nic)
        self.assertIn('an integer jest required', str(cm.exception))
        # wrong number of args
        przy self.assertRaises(TypeError) jako cm:
            s.sendto(b'foo')
        self.assertIn('(1 given)', str(cm.exception))
        przy self.assertRaises(TypeError) jako cm:
            s.sendto(b'foo', 0, sockname, 4)
        self.assertIn('(4 given)', str(cm.exception))

    def testCrucialConstants(self):
        # Testing dla mission critical constants
        socket.AF_INET
        socket.SOCK_STREAM
        socket.SOCK_DGRAM
        socket.SOCK_RAW
        socket.SOCK_RDM
        socket.SOCK_SEQPACKET
        socket.SOL_SOCKET
        socket.SO_REUSEADDR

    def testHostnameRes(self):
        # Testing hostname resolution mechanisms
        hostname = socket.gethostname()
        spróbuj:
            ip = socket.gethostbyname(hostname)
        wyjąwszy OSError:
            # Probably name lookup wasn't set up right; skip this test
            self.skipTest('name lookup failure')
        self.assertPrawda(ip.find('.') >= 0, "Error resolving host to ip.")
        spróbuj:
            hname, aliases, ipaddrs = socket.gethostbyaddr(ip)
        wyjąwszy OSError:
            # Probably a similar problem jako above; skip this test
            self.skipTest('name lookup failure')
        all_host_names = [hostname, hname] + aliases
        fqhn = socket.getfqdn(ip)
        jeżeli nie fqhn w all_host_names:
            self.fail("Error testing host resolution mechanisms. (fqdn: %s, all: %s)" % (fqhn, repr(all_host_names)))

    def test_host_resolution(self):
        dla addr w ['0.1.1.~1', '1+.1.1.1', '::1q', '::1::2',
                     '1:1:1:1:1:1:1:1:1']:
            self.assertRaises(OSError, socket.gethostbyname, addr)
            self.assertRaises(OSError, socket.gethostbyaddr, addr)

        dla addr w [support.HOST, '10.0.0.1', '255.255.255.255']:
            self.assertEqual(socket.gethostbyname(addr), addr)

        # we don't test support.HOSTv6 because there's a chance it doesn't have
        # a matching name entry (e.g. 'ip6-localhost')
        dla host w [support.HOST]:
            self.assertIn(host, socket.gethostbyaddr(host)[2])

    @unittest.skipUnless(hasattr(socket, 'sethostname'), "test needs socket.sethostname()")
    @unittest.skipUnless(hasattr(socket, 'gethostname'), "test needs socket.gethostname()")
    def test_sethostname(self):
        oldhn = socket.gethostname()
        spróbuj:
            socket.sethostname('new')
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.EPERM:
                self.skipTest("test should be run jako root")
            inaczej:
                podnieś
        spróbuj:
            # running test jako root!
            self.assertEqual(socket.gethostname(), 'new')
            # Should work przy bytes objects too
            socket.sethostname(b'bar')
            self.assertEqual(socket.gethostname(), 'bar')
        w_końcu:
            socket.sethostname(oldhn)

    @unittest.skipUnless(hasattr(socket, 'if_nameindex'),
                         'socket.if_nameindex() nie available.')
    def testInterfaceNameIndex(self):
        interfaces = socket.if_nameindex()
        dla index, name w interfaces:
            self.assertIsInstance(index, int)
            self.assertIsInstance(name, str)
            # interface indices are non-zero integers
            self.assertGreater(index, 0)
            _index = socket.if_nametoindex(name)
            self.assertIsInstance(_index, int)
            self.assertEqual(index, _index)
            _name = socket.if_indextoname(index)
            self.assertIsInstance(_name, str)
            self.assertEqual(name, _name)

    @unittest.skipUnless(hasattr(socket, 'if_nameindex'),
                         'socket.if_nameindex() nie available.')
    def testInvalidInterfaceNameIndex(self):
        # test nonexistent interface index/name
        self.assertRaises(OSError, socket.if_indextoname, 0)
        self.assertRaises(OSError, socket.if_nametoindex, '_DEADBEEF')
        # test przy invalid values
        self.assertRaises(TypeError, socket.if_nametoindex, 0)
        self.assertRaises(TypeError, socket.if_indextoname, '_DEADBEEF')

    @unittest.skipUnless(hasattr(sys, 'getrefcount'),
                         'test needs sys.getrefcount()')
    def testRefCountGetNameInfo(self):
        # Testing reference count dla getnameinfo
        spróbuj:
            # On some versions, this loses a reference
            orig = sys.getrefcount(__name__)
            socket.getnameinfo(__name__,0)
        wyjąwszy TypeError:
            jeżeli sys.getrefcount(__name__) != orig:
                self.fail("socket.getnameinfo loses a reference")

    def testInterpreterCrash(self):
        # Making sure getnameinfo doesn't crash the interpreter
        spróbuj:
            # On some versions, this crashes the interpreter.
            socket.getnameinfo(('x', 0, 0, 0), 0)
        wyjąwszy OSError:
            dalej

    def testNtoH(self):
        # This just checks that htons etc. are their own inverse,
        # when looking at the lower 16 albo 32 bits.
        sizes = {socket.htonl: 32, socket.ntohl: 32,
                 socket.htons: 16, socket.ntohs: 16}
        dla func, size w sizes.items():
            mask = (1<<size) - 1
            dla i w (0, 1, 0xffff, ~0xffff, 2, 0x01234567, 0x76543210):
                self.assertEqual(i & mask, func(func(i&mask)) & mask)

            swapped = func(mask)
            self.assertEqual(swapped & mask, mask)
            self.assertRaises(OverflowError, func, 1<<34)

    def testNtoHErrors(self):
        good_values = [ 1, 2, 3, 1, 2, 3 ]
        bad_values = [ -1, -2, -3, -1, -2, -3 ]
        dla k w good_values:
            socket.ntohl(k)
            socket.ntohs(k)
            socket.htonl(k)
            socket.htons(k)
        dla k w bad_values:
            self.assertRaises(OverflowError, socket.ntohl, k)
            self.assertRaises(OverflowError, socket.ntohs, k)
            self.assertRaises(OverflowError, socket.htonl, k)
            self.assertRaises(OverflowError, socket.htons, k)

    def testGetServBy(self):
        eq = self.assertEqual
        # Find one service that exists, then check all the related interfaces.
        # I've ordered this by protocols that have both a tcp oraz udp
        # protocol, at least dla modern Linuxes.
        jeżeli (sys.platform.startswith(('freebsd', 'netbsd', 'gnukfreebsd'))
            albo sys.platform w ('linux', 'darwin')):
            # avoid the 'echo' service on this platform, jako there jest an
            # assumption przerwijing non-standard port/protocol entry
            services = ('daytime', 'qotd', 'domain')
        inaczej:
            services = ('echo', 'daytime', 'domain')
        dla service w services:
            spróbuj:
                port = socket.getservbyname(service, 'tcp')
                przerwij
            wyjąwszy OSError:
                dalej
        inaczej:
            podnieś OSError
        # Try same call przy optional protocol omitted
        port2 = socket.getservbyname(service)
        eq(port, port2)
        # Try udp, but don't barf jeżeli it doesn't exist
        spróbuj:
            udpport = socket.getservbyname(service, 'udp')
        wyjąwszy OSError:
            udpport = Nic
        inaczej:
            eq(udpport, port)
        # Now make sure the lookup by port returns the same service name
        eq(socket.getservbyport(port2), service)
        eq(socket.getservbyport(port, 'tcp'), service)
        jeżeli udpport jest nie Nic:
            eq(socket.getservbyport(udpport, 'udp'), service)
        # Make sure getservbyport does nie accept out of range ports.
        self.assertRaises(OverflowError, socket.getservbyport, -1)
        self.assertRaises(OverflowError, socket.getservbyport, 65536)

    def testDefaultTimeout(self):
        # Testing default timeout
        # The default timeout should initially be Nic
        self.assertEqual(socket.getdefaulttimeout(), Nic)
        s = socket.socket()
        self.assertEqual(s.gettimeout(), Nic)
        s.close()

        # Set the default timeout to 10, oraz see jeżeli it propagates
        socket.setdefaulttimeout(10)
        self.assertEqual(socket.getdefaulttimeout(), 10)
        s = socket.socket()
        self.assertEqual(s.gettimeout(), 10)
        s.close()

        # Reset the default timeout to Nic, oraz see jeżeli it propagates
        socket.setdefaulttimeout(Nic)
        self.assertEqual(socket.getdefaulttimeout(), Nic)
        s = socket.socket()
        self.assertEqual(s.gettimeout(), Nic)
        s.close()

        # Check that setting it to an invalid value podnieśs ValueError
        self.assertRaises(ValueError, socket.setdefaulttimeout, -1)

        # Check that setting it to an invalid type podnieśs TypeError
        self.assertRaises(TypeError, socket.setdefaulttimeout, "spam")

    @unittest.skipUnless(hasattr(socket, 'inet_aton'),
                         'test needs socket.inet_aton()')
    def testIPv4_inet_aton_fourbytes(self):
        # Test that issue1008086 oraz issue767150 are fixed.
        # It must zwróć 4 bytes.
        self.assertEqual(b'\x00'*4, socket.inet_aton('0.0.0.0'))
        self.assertEqual(b'\xff'*4, socket.inet_aton('255.255.255.255'))

    @unittest.skipUnless(hasattr(socket, 'inet_pton'),
                         'test needs socket.inet_pton()')
    def testIPv4toString(self):
        z socket zaimportuj inet_aton jako f, inet_pton, AF_INET
        g = lambda a: inet_pton(AF_INET, a)

        assertInvalid = lambda func,a: self.assertRaises(
            (OSError, ValueError), func, a
        )

        self.assertEqual(b'\x00\x00\x00\x00', f('0.0.0.0'))
        self.assertEqual(b'\xff\x00\xff\x00', f('255.0.255.0'))
        self.assertEqual(b'\xaa\xaa\xaa\xaa', f('170.170.170.170'))
        self.assertEqual(b'\x01\x02\x03\x04', f('1.2.3.4'))
        self.assertEqual(b'\xff\xff\xff\xff', f('255.255.255.255'))
        assertInvalid(f, '0.0.0.')
        assertInvalid(f, '300.0.0.0')
        assertInvalid(f, 'a.0.0.0')
        assertInvalid(f, '1.2.3.4.5')
        assertInvalid(f, '::1')

        self.assertEqual(b'\x00\x00\x00\x00', g('0.0.0.0'))
        self.assertEqual(b'\xff\x00\xff\x00', g('255.0.255.0'))
        self.assertEqual(b'\xaa\xaa\xaa\xaa', g('170.170.170.170'))
        self.assertEqual(b'\xff\xff\xff\xff', g('255.255.255.255'))
        assertInvalid(g, '0.0.0.')
        assertInvalid(g, '300.0.0.0')
        assertInvalid(g, 'a.0.0.0')
        assertInvalid(g, '1.2.3.4.5')
        assertInvalid(g, '::1')

    @unittest.skipUnless(hasattr(socket, 'inet_pton'),
                         'test needs socket.inet_pton()')
    def testIPv6toString(self):
        spróbuj:
            z socket zaimportuj inet_pton, AF_INET6, has_ipv6
            jeżeli nie has_ipv6:
                self.skipTest('IPv6 nie available')
        wyjąwszy ImportError:
            self.skipTest('could nie zaimportuj needed symbols z socket')

        jeżeli sys.platform == "win32":
            spróbuj:
                inet_pton(AF_INET6, '::')
            wyjąwszy OSError jako e:
                jeżeli e.winerror == 10022:
                    self.skipTest('IPv6 might nie be supported')

        f = lambda a: inet_pton(AF_INET6, a)
        assertInvalid = lambda a: self.assertRaises(
            (OSError, ValueError), f, a
        )

        self.assertEqual(b'\x00' * 16, f('::'))
        self.assertEqual(b'\x00' * 16, f('0::0'))
        self.assertEqual(b'\x00\x01' + b'\x00' * 14, f('1::'))
        self.assertEqual(
            b'\x45\xef\x76\xcb\x00\x1a\x56\xef\xaf\xeb\x0b\xac\x19\x24\xae\xae',
            f('45ef:76cb:1a:56ef:afeb:bac:1924:aeae')
        )
        self.assertEqual(
            b'\xad\x42\x0a\xbc' + b'\x00' * 4 + b'\x01\x27\x00\x00\x02\x54\x00\x02',
            f('ad42:abc::127:0:254:2')
        )
        self.assertEqual(b'\x00\x12\x00\x0a' + b'\x00' * 12, f('12:a::'))
        assertInvalid('0x20::')
        assertInvalid(':::')
        assertInvalid('::0::')
        assertInvalid('1::abc::')
        assertInvalid('1::abc::def')
        assertInvalid('1:2:3:4:5:6:')
        assertInvalid('1:2:3:4:5:6')
        assertInvalid('1:2:3:4:5:6:7:8:')
        assertInvalid('1:2:3:4:5:6:7:8:0')

        self.assertEqual(b'\x00' * 12 + b'\xfe\x2a\x17\x40',
            f('::254.42.23.64')
        )
        self.assertEqual(
            b'\x00\x42' + b'\x00' * 8 + b'\xa2\x9b\xfe\x2a\x17\x40',
            f('42::a29b:254.42.23.64')
        )
        self.assertEqual(
            b'\x00\x42\xa8\xb9\x00\x00\x00\x02\xff\xff\xa2\x9b\xfe\x2a\x17\x40',
            f('42:a8b9:0:2:ffff:a29b:254.42.23.64')
        )
        assertInvalid('255.254.253.252')
        assertInvalid('1::260.2.3.0')
        assertInvalid('1::0.be.e.0')
        assertInvalid('1:2:3:4:5:6:7:1.2.3.4')
        assertInvalid('::1.2.3.4:0')
        assertInvalid('0.100.200.0:3:4:5:6:7:8')

    @unittest.skipUnless(hasattr(socket, 'inet_ntop'),
                         'test needs socket.inet_ntop()')
    def testStringToIPv4(self):
        z socket zaimportuj inet_ntoa jako f, inet_ntop, AF_INET
        g = lambda a: inet_ntop(AF_INET, a)
        assertInvalid = lambda func,a: self.assertRaises(
            (OSError, ValueError), func, a
        )

        self.assertEqual('1.0.1.0', f(b'\x01\x00\x01\x00'))
        self.assertEqual('170.85.170.85', f(b'\xaa\x55\xaa\x55'))
        self.assertEqual('255.255.255.255', f(b'\xff\xff\xff\xff'))
        self.assertEqual('1.2.3.4', f(b'\x01\x02\x03\x04'))
        assertInvalid(f, b'\x00' * 3)
        assertInvalid(f, b'\x00' * 5)
        assertInvalid(f, b'\x00' * 16)
        self.assertEqual('170.85.170.85', f(bytearray(b'\xaa\x55\xaa\x55')))

        self.assertEqual('1.0.1.0', g(b'\x01\x00\x01\x00'))
        self.assertEqual('170.85.170.85', g(b'\xaa\x55\xaa\x55'))
        self.assertEqual('255.255.255.255', g(b'\xff\xff\xff\xff'))
        assertInvalid(g, b'\x00' * 3)
        assertInvalid(g, b'\x00' * 5)
        assertInvalid(g, b'\x00' * 16)
        self.assertEqual('170.85.170.85', g(bytearray(b'\xaa\x55\xaa\x55')))

    @unittest.skipUnless(hasattr(socket, 'inet_ntop'),
                         'test needs socket.inet_ntop()')
    def testStringToIPv6(self):
        spróbuj:
            z socket zaimportuj inet_ntop, AF_INET6, has_ipv6
            jeżeli nie has_ipv6:
                self.skipTest('IPv6 nie available')
        wyjąwszy ImportError:
            self.skipTest('could nie zaimportuj needed symbols z socket')

        jeżeli sys.platform == "win32":
            spróbuj:
                inet_ntop(AF_INET6, b'\x00' * 16)
            wyjąwszy OSError jako e:
                jeżeli e.winerror == 10022:
                    self.skipTest('IPv6 might nie be supported')

        f = lambda a: inet_ntop(AF_INET6, a)
        assertInvalid = lambda a: self.assertRaises(
            (OSError, ValueError), f, a
        )

        self.assertEqual('::', f(b'\x00' * 16))
        self.assertEqual('::1', f(b'\x00' * 15 + b'\x01'))
        self.assertEqual(
            'aef:b01:506:1001:ffff:9997:55:170',
            f(b'\x0a\xef\x0b\x01\x05\x06\x10\x01\xff\xff\x99\x97\x00\x55\x01\x70')
        )
        self.assertEqual('::1', f(bytearray(b'\x00' * 15 + b'\x01')))

        assertInvalid(b'\x12' * 15)
        assertInvalid(b'\x12' * 17)
        assertInvalid(b'\x12' * 4)

    # XXX The following don't test module-level functionality...

    def testSockName(self):
        # Testing getsockname()
        port = support.find_unused_port()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        sock.bind(("0.0.0.0", port))
        name = sock.getsockname()
        # XXX(nnorwitz): http://tinyurl.com/os5jz seems to indicate
        # it reasonable to get the host's addr w addition to 0.0.0.0.
        # At least dla eCos.  This jest required dla the S/390 to dalej.
        spróbuj:
            my_ip_addr = socket.gethostbyname(socket.gethostname())
        wyjąwszy OSError:
            # Probably name lookup wasn't set up right; skip this test
            self.skipTest('name lookup failure')
        self.assertIn(name[0], ("0.0.0.0", my_ip_addr), '%s invalid' % name[0])
        self.assertEqual(name[1], port)

    def testGetSockOpt(self):
        # Testing getsockopt()
        # We know a socket should start without reuse==0
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        reuse = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        self.assertNieprawda(reuse != 0, "initial mode jest reuse")

    def testSetSockOpt(self):
        # Testing setsockopt()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        reuse = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        self.assertNieprawda(reuse == 0, "failed to set reuse mode")

    def testSendAfterClose(self):
        # testing send() after close() przy timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.close()
        self.assertRaises(OSError, sock.send, b"spam")

    def testNewAttributes(self):
        # testing .family, .type oraz .protocol

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.assertEqual(sock.family, socket.AF_INET)
        jeżeli hasattr(socket, 'SOCK_CLOEXEC'):
            self.assertIn(sock.type,
                          (socket.SOCK_STREAM | socket.SOCK_CLOEXEC,
                           socket.SOCK_STREAM))
        inaczej:
            self.assertEqual(sock.type, socket.SOCK_STREAM)
        self.assertEqual(sock.proto, 0)
        sock.close()

    def test_getsockaddrarg(self):
        sock = socket.socket()
        self.addCleanup(sock.close)
        port = support.find_unused_port()
        big_port = port + 65536
        neg_port = port - 65536
        self.assertRaises(OverflowError, sock.bind, (HOST, big_port))
        self.assertRaises(OverflowError, sock.bind, (HOST, neg_port))
        # Since find_unused_port() jest inherently subject to race conditions, we
        # call it a couple times jeżeli necessary.
        dla i w itertools.count():
            port = support.find_unused_port()
            spróbuj:
                sock.bind((HOST, port))
            wyjąwszy OSError jako e:
                jeżeli e.errno != errno.EADDRINUSE albo i == 5:
                    podnieś
            inaczej:
                przerwij

    @unittest.skipUnless(os.name == "nt", "Windows specific")
    def test_sock_ioctl(self):
        self.assertPrawda(hasattr(socket.socket, 'ioctl'))
        self.assertPrawda(hasattr(socket, 'SIO_RCVALL'))
        self.assertPrawda(hasattr(socket, 'RCVALL_ON'))
        self.assertPrawda(hasattr(socket, 'RCVALL_OFF'))
        self.assertPrawda(hasattr(socket, 'SIO_KEEPALIVE_VALS'))
        s = socket.socket()
        self.addCleanup(s.close)
        self.assertRaises(ValueError, s.ioctl, -1, Nic)
        s.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 100, 100))

    def testGetaddrinfo(self):
        spróbuj:
            socket.getaddrinfo('localhost', 80)
        wyjąwszy socket.gaierror jako err:
            jeżeli err.errno == socket.EAI_SERVICE:
                # see http://bugs.python.org/issue1282647
                self.skipTest("buggy libc version")
            podnieś
        # len of every sequence jest supposed to be == 5
        dla info w socket.getaddrinfo(HOST, Nic):
            self.assertEqual(len(info), 5)
        # host can be a domain name, a string representation of an
        # IPv4/v6 address albo Nic
        socket.getaddrinfo('localhost', 80)
        socket.getaddrinfo('127.0.0.1', 80)
        socket.getaddrinfo(Nic, 80)
        jeżeli support.IPV6_ENABLED:
            socket.getaddrinfo('::1', 80)
        # port can be a string service name such jako "http", a numeric
        # port number albo Nic
        socket.getaddrinfo(HOST, "http")
        socket.getaddrinfo(HOST, 80)
        socket.getaddrinfo(HOST, Nic)
        # test family oraz socktype filters
        infos = socket.getaddrinfo(HOST, 80, socket.AF_INET, socket.SOCK_STREAM)
        dla family, type, _, _, _ w infos:
            self.assertEqual(family, socket.AF_INET)
            self.assertEqual(str(family), 'AddressFamily.AF_INET')
            self.assertEqual(type, socket.SOCK_STREAM)
            self.assertEqual(str(type), 'SocketKind.SOCK_STREAM')
        infos = socket.getaddrinfo(HOST, Nic, 0, socket.SOCK_STREAM)
        dla _, socktype, _, _, _ w infos:
            self.assertEqual(socktype, socket.SOCK_STREAM)
        # test proto oraz flags arguments
        socket.getaddrinfo(HOST, Nic, 0, 0, socket.SOL_TCP)
        socket.getaddrinfo(HOST, Nic, 0, 0, 0, socket.AI_PASSIVE)
        # a server willing to support both IPv4 oraz IPv6 will
        # usually do this
        socket.getaddrinfo(Nic, 0, socket.AF_UNSPEC, socket.SOCK_STREAM, 0,
                           socket.AI_PASSIVE)
        # test keyword arguments
        a = socket.getaddrinfo(HOST, Nic)
        b = socket.getaddrinfo(host=HOST, port=Nic)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(HOST, Nic, socket.AF_INET)
        b = socket.getaddrinfo(HOST, Nic, family=socket.AF_INET)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(HOST, Nic, 0, socket.SOCK_STREAM)
        b = socket.getaddrinfo(HOST, Nic, type=socket.SOCK_STREAM)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(HOST, Nic, 0, 0, socket.SOL_TCP)
        b = socket.getaddrinfo(HOST, Nic, proto=socket.SOL_TCP)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(HOST, Nic, 0, 0, 0, socket.AI_PASSIVE)
        b = socket.getaddrinfo(HOST, Nic, flags=socket.AI_PASSIVE)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(Nic, 0, socket.AF_UNSPEC, socket.SOCK_STREAM, 0,
                               socket.AI_PASSIVE)
        b = socket.getaddrinfo(host=Nic, port=0, family=socket.AF_UNSPEC,
                               type=socket.SOCK_STREAM, proto=0,
                               flags=socket.AI_PASSIVE)
        self.assertEqual(a, b)
        # Issue #6697.
        self.assertRaises(UnicodeEncodeError, socket.getaddrinfo, 'localhost', '\uD800')

        # Issue 17269: test workaround dla OS X platform bug segfault
        jeżeli hasattr(socket, 'AI_NUMERICSERV'):
            spróbuj:
                # The arguments here are undefined oraz the call may succeed
                # albo fail.  All we care here jest that it doesn't segfault.
                socket.getaddrinfo("localhost", Nic, 0, 0, 0,
                                   socket.AI_NUMERICSERV)
            wyjąwszy socket.gaierror:
                dalej

    def test_getnameinfo(self):
        # only IP addresses are allowed
        self.assertRaises(OSError, socket.getnameinfo, ('mail.python.org',0), 0)

    @unittest.skipUnless(support.is_resource_enabled('network'),
                         'network jest nie enabled')
    def test_idna(self):
        # Check dla internet access before running test (issue #12804).
        spróbuj:
            socket.gethostbyname('python.org')
        wyjąwszy socket.gaierror jako e:
            jeżeli e.errno == socket.EAI_NODATA:
                self.skipTest('internet access required dla this test')
        # these should all be successful
        domain = 'испытание.pythontest.net'
        socket.gethostbyname(domain)
        socket.gethostbyname_ex(domain)
        socket.getaddrinfo(domain,0,socket.AF_UNSPEC,socket.SOCK_STREAM)
        # this may nie work jeżeli the forward lookup choses the IPv6 address, jako that doesn't
        # have a reverse entry yet
        # socket.gethostbyaddr('испытание.python.org')

    def check_sendall_interrupted(self, with_timeout):
        # socketpair() jest nie stricly required, but it makes things easier.
        jeżeli nie hasattr(signal, 'alarm') albo nie hasattr(socket, 'socketpair'):
            self.skipTest("signal.alarm oraz socket.socketpair required dla this test")
        # Our signal handlers clobber the C errno by calling a math function
        # przy an invalid domain value.
        def ok_handler(*args):
            self.assertRaises(ValueError, math.acosh, 0)
        def raising_handler(*args):
            self.assertRaises(ValueError, math.acosh, 0)
            1 // 0
        c, s = socket.socketpair()
        old_alarm = signal.signal(signal.SIGALRM, raising_handler)
        spróbuj:
            jeżeli with_timeout:
                # Just above the one second minimum dla signal.alarm
                c.settimeout(1.5)
            przy self.assertRaises(ZeroDivisionError):
                signal.alarm(1)
                c.sendall(b"x" * support.SOCK_MAX_SIZE)
            jeżeli with_timeout:
                signal.signal(signal.SIGALRM, ok_handler)
                signal.alarm(1)
                self.assertRaises(socket.timeout, c.sendall,
                                  b"x" * support.SOCK_MAX_SIZE)
        w_końcu:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_alarm)
            c.close()
            s.close()

    def test_sendall_interrupted(self):
        self.check_sendall_interrupted(Nieprawda)

    def test_sendall_interrupted_with_timeout(self):
        self.check_sendall_interrupted(Prawda)

    def test_dealloc_warn(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        r = repr(sock)
        przy self.assertWarns(ResourceWarning) jako cm:
            sock = Nic
            support.gc_collect()
        self.assertIn(r, str(cm.warning.args[0]))
        # An open socket file object gets dereferenced after the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        f = sock.makefile('rb')
        r = repr(sock)
        sock = Nic
        support.gc_collect()
        przy self.assertWarns(ResourceWarning):
            f = Nic
            support.gc_collect()

    def test_name_closed_socketio(self):
        przy socket.socket(socket.AF_INET, socket.SOCK_STREAM) jako sock:
            fp = sock.makefile("rb")
            fp.close()
            self.assertEqual(repr(fp), "<_io.BufferedReader name=-1>")

    def test_unusable_closed_socketio(self):
        przy socket.socket() jako sock:
            fp = sock.makefile("rb", buffering=0)
            self.assertPrawda(fp.readable())
            self.assertNieprawda(fp.writable())
            self.assertNieprawda(fp.seekable())
            fp.close()
            self.assertRaises(ValueError, fp.readable)
            self.assertRaises(ValueError, fp.writable)
            self.assertRaises(ValueError, fp.seekable)

    def test_pickle(self):
        sock = socket.socket()
        przy sock:
            dla protocol w range(pickle.HIGHEST_PROTOCOL + 1):
                self.assertRaises(TypeError, pickle.dumps, sock, protocol)
        dla protocol w range(pickle.HIGHEST_PROTOCOL + 1):
            family = pickle.loads(pickle.dumps(socket.AF_INET, protocol))
            self.assertEqual(family, socket.AF_INET)
            type = pickle.loads(pickle.dumps(socket.SOCK_STREAM, protocol))
            self.assertEqual(type, socket.SOCK_STREAM)

    def test_listen_backlog(self):
        dla backlog w 0, -1:
            przy socket.socket(socket.AF_INET, socket.SOCK_STREAM) jako srv:
                srv.bind((HOST, 0))
                srv.listen(backlog)

        przy socket.socket(socket.AF_INET, socket.SOCK_STREAM) jako srv:
            srv.bind((HOST, 0))
            srv.listen()

    @support.cpython_only
    def test_listen_backlog_overflow(self):
        # Issue 15989
        zaimportuj _testcapi
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind((HOST, 0))
        self.assertRaises(OverflowError, srv.listen, _testcapi.INT_MAX + 1)
        srv.close()

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required dla this test.')
    def test_flowinfo(self):
        self.assertRaises(OverflowError, socket.getnameinfo,
                          (support.HOSTv6, 0, 0xffffffff), 0)
        przy socket.socket(socket.AF_INET6, socket.SOCK_STREAM) jako s:
            self.assertRaises(OverflowError, s.bind, (support.HOSTv6, 0, -10))

    def test_str_for_enums(self):
        # Make sure that the AF_* oraz SOCK_* constants have enum-like string
        # reprs.
        przy socket.socket(socket.AF_INET, socket.SOCK_STREAM) jako s:
            self.assertEqual(str(s.family), 'AddressFamily.AF_INET')
            self.assertEqual(str(s.type), 'SocketKind.SOCK_STREAM')

    @unittest.skipIf(os.name == 'nt', 'Will nie work on Windows')
    def test_uknown_socket_family_repr(self):
        # Test that when created przy a family that's nie one of the known
        # AF_*/SOCK_* constants, socket.family just returns the number.
        #
        # To do this we fool socket.socket into believing it already has an
        # open fd because on this path it doesn't actually verify the family oraz
        # type oraz populates the socket object.
        #
        # On Windows this trick won't work, so the test jest skipped.
        fd, _ = tempfile.mkstemp()
        przy socket.socket(family=42424, type=13331, fileno=fd) jako s:
            self.assertEqual(s.family, 42424)
            self.assertEqual(s.type, 13331)

@unittest.skipUnless(HAVE_SOCKET_CAN, 'SocketCan required dla this test.')
klasa BasicCANTest(unittest.TestCase):

    def testCrucialConstants(self):
        socket.AF_CAN
        socket.PF_CAN
        socket.CAN_RAW

    @unittest.skipUnless(hasattr(socket, "CAN_BCM"),
                         'socket.CAN_BCM required dla this test.')
    def testBCMConstants(self):
        socket.CAN_BCM

        # opcodes
        socket.CAN_BCM_TX_SETUP     # create (cyclic) transmission task
        socket.CAN_BCM_TX_DELETE    # remove (cyclic) transmission task
        socket.CAN_BCM_TX_READ      # read properties of (cyclic) transmission task
        socket.CAN_BCM_TX_SEND      # send one CAN frame
        socket.CAN_BCM_RX_SETUP     # create RX content filter subscription
        socket.CAN_BCM_RX_DELETE    # remove RX content filter subscription
        socket.CAN_BCM_RX_READ      # read properties of RX content filter subscription
        socket.CAN_BCM_TX_STATUS    # reply to TX_READ request
        socket.CAN_BCM_TX_EXPIRED   # notification on performed transmissions (count=0)
        socket.CAN_BCM_RX_STATUS    # reply to RX_READ request
        socket.CAN_BCM_RX_TIMEOUT   # cyclic message jest absent
        socket.CAN_BCM_RX_CHANGED   # updated CAN frame (detected content change)

    def testCreateSocket(self):
        przy socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) jako s:
            dalej

    @unittest.skipUnless(hasattr(socket, "CAN_BCM"),
                         'socket.CAN_BCM required dla this test.')
    def testCreateBCMSocket(self):
        przy socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_BCM) jako s:
            dalej

    def testBindAny(self):
        przy socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) jako s:
            s.bind(('', ))

    def testTooLongInterfaceName(self):
        # most systems limit IFNAMSIZ to 16, take 1024 to be sure
        przy socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) jako s:
            self.assertRaisesRegex(OSError, 'interface name too long',
                                   s.bind, ('x' * 1024,))

    @unittest.skipUnless(hasattr(socket, "CAN_RAW_LOOPBACK"),
                         'socket.CAN_RAW_LOOPBACK required dla this test.')
    def testLoopback(self):
        przy socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) jako s:
            dla loopback w (0, 1):
                s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_LOOPBACK,
                             loopback)
                self.assertEqual(loopback,
                    s.getsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_LOOPBACK))

    @unittest.skipUnless(hasattr(socket, "CAN_RAW_FILTER"),
                         'socket.CAN_RAW_FILTER required dla this test.')
    def testFilter(self):
        can_id, can_mask = 0x200, 0x700
        can_filter = struct.pack("=II", can_id, can_mask)
        przy socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) jako s:
            s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, can_filter)
            self.assertEqual(can_filter,
                    s.getsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, 8))
            s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, bytearray(can_filter))


@unittest.skipUnless(HAVE_SOCKET_CAN, 'SocketCan required dla this test.')
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa CANTest(ThreadedCANSocketTest):

    def __init__(self, methodName='runTest'):
        ThreadedCANSocketTest.__init__(self, methodName=methodName)

    @classmethod
    def build_can_frame(cls, can_id, data):
        """Build a CAN frame."""
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        zwróć struct.pack(cls.can_frame_fmt, can_id, can_dlc, data)

    @classmethod
    def dissect_can_frame(cls, frame):
        """Dissect a CAN frame."""
        can_id, can_dlc, data = struct.unpack(cls.can_frame_fmt, frame)
        zwróć (can_id, can_dlc, data[:can_dlc])

    def testSendFrame(self):
        cf, addr = self.s.recvfrom(self.bufsize)
        self.assertEqual(self.cf, cf)
        self.assertEqual(addr[0], self.interface)
        self.assertEqual(addr[1], socket.AF_CAN)

    def _testSendFrame(self):
        self.cf = self.build_can_frame(0x00, b'\x01\x02\x03\x04\x05')
        self.cli.send(self.cf)

    def testSendMaxFrame(self):
        cf, addr = self.s.recvfrom(self.bufsize)
        self.assertEqual(self.cf, cf)

    def _testSendMaxFrame(self):
        self.cf = self.build_can_frame(0x00, b'\x07' * 8)
        self.cli.send(self.cf)

    def testSendMultiFrames(self):
        cf, addr = self.s.recvfrom(self.bufsize)
        self.assertEqual(self.cf1, cf)

        cf, addr = self.s.recvfrom(self.bufsize)
        self.assertEqual(self.cf2, cf)

    def _testSendMultiFrames(self):
        self.cf1 = self.build_can_frame(0x07, b'\x44\x33\x22\x11')
        self.cli.send(self.cf1)

        self.cf2 = self.build_can_frame(0x12, b'\x99\x22\x33')
        self.cli.send(self.cf2)

    @unittest.skipUnless(hasattr(socket, "CAN_BCM"),
                         'socket.CAN_BCM required dla this test.')
    def _testBCM(self):
        cf, addr = self.cli.recvfrom(self.bufsize)
        self.assertEqual(self.cf, cf)
        can_id, can_dlc, data = self.dissect_can_frame(cf)
        self.assertEqual(self.can_id, can_id)
        self.assertEqual(self.data, data)

    @unittest.skipUnless(hasattr(socket, "CAN_BCM"),
                         'socket.CAN_BCM required dla this test.')
    def testBCM(self):
        bcm = socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_BCM)
        self.addCleanup(bcm.close)
        bcm.connect((self.interface,))
        self.can_id = 0x123
        self.data = bytes([0xc0, 0xff, 0xee])
        self.cf = self.build_can_frame(self.can_id, self.data)
        opcode = socket.CAN_BCM_TX_SEND
        flags = 0
        count = 0
        ival1_seconds = ival1_usec = ival2_seconds = ival2_usec = 0
        bcm_can_id = 0x0222
        nframes = 1
        assert len(self.cf) == 16
        header = struct.pack(self.bcm_cmd_msg_fmt,
                    opcode,
                    flags,
                    count,
                    ival1_seconds,
                    ival1_usec,
                    ival2_seconds,
                    ival2_usec,
                    bcm_can_id,
                    nframes,
                    )
        header_plus_frame = header + self.cf
        bytes_sent = bcm.send(header_plus_frame)
        self.assertEqual(bytes_sent, len(header_plus_frame))


@unittest.skipUnless(HAVE_SOCKET_RDS, 'RDS sockets required dla this test.')
klasa BasicRDSTest(unittest.TestCase):

    def testCrucialConstants(self):
        socket.AF_RDS
        socket.PF_RDS

    def testCreateSocket(self):
        przy socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0) jako s:
            dalej

    def testSocketBufferSize(self):
        bufsize = 16384
        przy socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0) jako s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufsize)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, bufsize)


@unittest.skipUnless(HAVE_SOCKET_RDS, 'RDS sockets required dla this test.')
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RDSTest(ThreadedRDSSocketTest):

    def __init__(self, methodName='runTest'):
        ThreadedRDSSocketTest.__init__(self, methodName=methodName)

    def setUp(self):
        super().setUp()
        self.evt = threading.Event()

    def testSendAndRecv(self):
        data, addr = self.serv.recvfrom(self.bufsize)
        self.assertEqual(self.data, data)
        self.assertEqual(self.cli_addr, addr)

    def _testSendAndRecv(self):
        self.data = b'spam'
        self.cli.sendto(self.data, 0, (HOST, self.port))

    def testPeek(self):
        data, addr = self.serv.recvfrom(self.bufsize, socket.MSG_PEEK)
        self.assertEqual(self.data, data)
        data, addr = self.serv.recvfrom(self.bufsize)
        self.assertEqual(self.data, data)

    def _testPeek(self):
        self.data = b'spam'
        self.cli.sendto(self.data, 0, (HOST, self.port))

    @requireAttrs(socket.socket, 'recvmsg')
    def testSendAndRecvMsg(self):
        data, ancdata, msg_flags, addr = self.serv.recvmsg(self.bufsize)
        self.assertEqual(self.data, data)

    @requireAttrs(socket.socket, 'sendmsg')
    def _testSendAndRecvMsg(self):
        self.data = b'hello ' * 10
        self.cli.sendmsg([self.data], (), 0, (HOST, self.port))

    def testSendAndRecvMulti(self):
        data, addr = self.serv.recvfrom(self.bufsize)
        self.assertEqual(self.data1, data)

        data, addr = self.serv.recvfrom(self.bufsize)
        self.assertEqual(self.data2, data)

    def _testSendAndRecvMulti(self):
        self.data1 = b'bacon'
        self.cli.sendto(self.data1, 0, (HOST, self.port))

        self.data2 = b'egg'
        self.cli.sendto(self.data2, 0, (HOST, self.port))

    def testSelect(self):
        r, w, x = select.select([self.serv], [], [], 3.0)
        self.assertIn(self.serv, r)
        data, addr = self.serv.recvfrom(self.bufsize)
        self.assertEqual(self.data, data)

    def _testSelect(self):
        self.data = b'select'
        self.cli.sendto(self.data, 0, (HOST, self.port))

    def testCongestion(self):
        # wait until the sender jest done
        self.evt.wait()

    def _testCongestion(self):
        # test the behavior w case of congestion
        self.data = b'fill'
        self.cli.setblocking(Nieprawda)
        spróbuj:
            # try to lower the receiver's socket buffer size
            self.cli.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16384)
        wyjąwszy OSError:
            dalej
        przy self.assertRaises(OSError) jako cm:
            spróbuj:
                # fill the receiver's socket buffer
                dopóki Prawda:
                    self.cli.sendto(self.data, 0, (HOST, self.port))
            w_końcu:
                # signal the receiver we're done
                self.evt.set()
        # sendto() should have failed przy ENOBUFS
        self.assertEqual(cm.exception.errno, errno.ENOBUFS)
        # oraz we should have received a congestion notification through poll
        r, w, x = select.select([self.serv], [], [], 3.0)
        self.assertIn(self.serv, r)


@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa BasicTCPTest(SocketConnectedTest):

    def __init__(self, methodName='runTest'):
        SocketConnectedTest.__init__(self, methodName=methodName)

    def testRecv(self):
        # Testing large receive over TCP
        msg = self.cli_conn.recv(1024)
        self.assertEqual(msg, MSG)

    def _testRecv(self):
        self.serv_conn.send(MSG)

    def testOverFlowRecv(self):
        # Testing receive w chunks over TCP
        seg1 = self.cli_conn.recv(len(MSG) - 3)
        seg2 = self.cli_conn.recv(1024)
        msg = seg1 + seg2
        self.assertEqual(msg, MSG)

    def _testOverFlowRecv(self):
        self.serv_conn.send(MSG)

    def testRecvFrom(self):
        # Testing large recvfrom() over TCP
        msg, addr = self.cli_conn.recvfrom(1024)
        self.assertEqual(msg, MSG)

    def _testRecvFrom(self):
        self.serv_conn.send(MSG)

    def testOverFlowRecvFrom(self):
        # Testing recvfrom() w chunks over TCP
        seg1, addr = self.cli_conn.recvfrom(len(MSG)-3)
        seg2, addr = self.cli_conn.recvfrom(1024)
        msg = seg1 + seg2
        self.assertEqual(msg, MSG)

    def _testOverFlowRecvFrom(self):
        self.serv_conn.send(MSG)

    def testSendAll(self):
        # Testing sendall() przy a 2048 byte string over TCP
        msg = b''
        dopóki 1:
            read = self.cli_conn.recv(1024)
            jeżeli nie read:
                przerwij
            msg += read
        self.assertEqual(msg, b'f' * 2048)

    def _testSendAll(self):
        big_chunk = b'f' * 2048
        self.serv_conn.sendall(big_chunk)

    def testFromFd(self):
        # Testing fromfd()
        fd = self.cli_conn.fileno()
        sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        self.assertIsInstance(sock, socket.socket)
        msg = sock.recv(1024)
        self.assertEqual(msg, MSG)

    def _testFromFd(self):
        self.serv_conn.send(MSG)

    def testDup(self):
        # Testing dup()
        sock = self.cli_conn.dup()
        self.addCleanup(sock.close)
        msg = sock.recv(1024)
        self.assertEqual(msg, MSG)

    def _testDup(self):
        self.serv_conn.send(MSG)

    def testShutdown(self):
        # Testing shutdown()
        msg = self.cli_conn.recv(1024)
        self.assertEqual(msg, MSG)
        # wait dla _testShutdown to finish: on OS X, when the server
        # closes the connection the client also becomes disconnected,
        # oraz the client's shutdown call will fail. (Issue #4397.)
        self.done.wait()

    def _testShutdown(self):
        self.serv_conn.send(MSG)
        self.serv_conn.shutdown(2)

    testShutdown_overflow = support.cpython_only(testShutdown)

    @support.cpython_only
    def _testShutdown_overflow(self):
        zaimportuj _testcapi
        self.serv_conn.send(MSG)
        # Issue 15989
        self.assertRaises(OverflowError, self.serv_conn.shutdown,
                          _testcapi.INT_MAX + 1)
        self.assertRaises(OverflowError, self.serv_conn.shutdown,
                          2 + (_testcapi.UINT_MAX + 1))
        self.serv_conn.shutdown(2)

    def testDetach(self):
        # Testing detach()
        fileno = self.cli_conn.fileno()
        f = self.cli_conn.detach()
        self.assertEqual(f, fileno)
        # cli_conn cannot be used anymore...
        self.assertPrawda(self.cli_conn._closed)
        self.assertRaises(OSError, self.cli_conn.recv, 1024)
        self.cli_conn.close()
        # ...but we can create another socket using the (still open)
        # file descriptor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=f)
        self.addCleanup(sock.close)
        msg = sock.recv(1024)
        self.assertEqual(msg, MSG)

    def _testDetach(self):
        self.serv_conn.send(MSG)

@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa BasicUDPTest(ThreadedUDPSocketTest):

    def __init__(self, methodName='runTest'):
        ThreadedUDPSocketTest.__init__(self, methodName=methodName)

    def testSendtoAndRecv(self):
        # Testing sendto() oraz Recv() over UDP
        msg = self.serv.recv(len(MSG))
        self.assertEqual(msg, MSG)

    def _testSendtoAndRecv(self):
        self.cli.sendto(MSG, 0, (HOST, self.port))

    def testRecvFrom(self):
        # Testing recvfrom() over UDP
        msg, addr = self.serv.recvfrom(len(MSG))
        self.assertEqual(msg, MSG)

    def _testRecvFrom(self):
        self.cli.sendto(MSG, 0, (HOST, self.port))

    def testRecvFromNegative(self):
        # Negative lengths dalejed to recvz should give ValueError.
        self.assertRaises(ValueError, self.serv.recvfrom, -1)

    def _testRecvFromNegative(self):
        self.cli.sendto(MSG, 0, (HOST, self.port))

# Tests dla the sendmsg()/recvmsg() interface.  Where possible, the
# same test code jest used przy different families oraz types of socket
# (e.g. stream, datagram), oraz tests using recvmsg() are repeated
# using recvmsg_into().
#
# The generic test classes such jako SendmsgTests oraz
# RecvmsgGenericTests inherit z SendrecvmsgBase oraz expect to be
# supplied przy sockets cli_sock oraz serv_sock representing the
# client's oraz the server's end of the connection respectively, oraz
# attributes cli_addr oraz serv_addr holding their (numeric where
# appropriate) addresses.
#
# The final concrete test classes combine these przy subclasses of
# SocketTestBase which set up client oraz server sockets of a specific
# type, oraz przy subclasses of SendrecvmsgBase such as
# SendrecvmsgDgramBase oraz SendrecvmsgConnectedBase which map these
# sockets to cli_sock oraz serv_sock oraz override the methods oraz
# attributes of SendrecvmsgBase to fill w destination addresses if
# needed when sending, check dla specific flags w msg_flags, etc.
#
# RecvmsgIntoMixin provides a version of doRecvmsg() implemented using
# recvmsg_into().

# XXX: like the other datagram (UDP) tests w this module, the code
# here assumes that datagram delivery on the local machine will be
# reliable.

klasa SendrecvmsgBase(ThreadSafeCleanupTestCase):
    # Base klasa dla sendmsg()/recvmsg() tests.

    # Time w seconds to wait before considering a test failed, albo
    # Nic dla no timeout.  Not all tests actually set a timeout.
    fail_timeout = 3.0

    def setUp(self):
        self.misc_event = threading.Event()
        super().setUp()

    def sendToServer(self, msg):
        # Send msg to the server.
        zwróć self.cli_sock.send(msg)

    # Tuple of alternative default arguments dla sendmsg() when called
    # via sendmsgToServer() (e.g. to include a destination address).
    sendmsg_to_server_defaults = ()

    def sendmsgToServer(self, *args):
        # Call sendmsg() on self.cli_sock przy the given arguments,
        # filling w any arguments which are nie supplied przy the
        # corresponding items of self.sendmsg_to_server_defaults, if
        # any.
        zwróć self.cli_sock.sendmsg(
            *(args + self.sendmsg_to_server_defaults[len(args):]))

    def doRecvmsg(self, sock, bufsize, *args):
        # Call recvmsg() on sock przy given arguments oraz zwróć its
        # result.  Should be used dla tests which can use either
        # recvmsg() albo recvmsg_into() - RecvmsgIntoMixin overrides
        # this method przy one which emulates it using recvmsg_into(),
        # thus allowing the same test to be used dla both methods.
        result = sock.recvmsg(bufsize, *args)
        self.registerRecvmsgResult(result)
        zwróć result

    def registerRecvmsgResult(self, result):
        # Called by doRecvmsg() przy the zwróć value of recvmsg() albo
        # recvmsg_into().  Can be overridden to arrange cleanup based
        # on the returned ancillary data, dla instance.
        dalej

    def checkRecvmsgAddress(self, addr1, addr2):
        # Called to compare the received address przy the address of
        # the peer.
        self.assertEqual(addr1, addr2)

    # Flags that are normally unset w msg_flags
    msg_flags_common_unset = 0
    dla name w ("MSG_CTRUNC", "MSG_OOB"):
        msg_flags_common_unset |= getattr(socket, name, 0)

    # Flags that are normally set
    msg_flags_common_set = 0

    # Flags set when a complete record has been received (e.g. MSG_EOR
    # dla SCTP)
    msg_flags_eor_indicator = 0

    # Flags set when a complete record has nie been received
    # (e.g. MSG_TRUNC dla datagram sockets)
    msg_flags_non_eor_indicator = 0

    def checkFlags(self, flags, eor=Nic, checkset=0, checkunset=0, ignore=0):
        # Method to check the value of msg_flags returned by recvmsg[_into]().
        #
        # Checks that all bits w msg_flags_common_set attribute are
        # set w "flags" oraz all bits w msg_flags_common_unset are
        # unset.
        #
        # The "eor" argument specifies whether the flags should
        # indicate that a full record (or datagram) has been received.
        # If "eor" jest Nic, no checks are done; otherwise, checks
        # that:
        #
        #  * jeżeli "eor" jest true, all bits w msg_flags_eor_indicator are
        #    set oraz all bits w msg_flags_non_eor_indicator are unset
        #
        #  * jeżeli "eor" jest false, all bits w msg_flags_non_eor_indicator
        #    are set oraz all bits w msg_flags_eor_indicator are unset
        #
        # If "checkset" and/or "checkunset" are supplied, they require
        # the given bits to be set albo unset respectively, overriding
        # what the attributes require dla those bits.
        #
        # If any bits are set w "ignore", they will nie be checked,
        # regardless of the other inputs.
        #
        # Will podnieś Exception jeżeli the inputs require a bit to be both
        # set oraz unset, oraz it jest nie ignored.

        defaultset = self.msg_flags_common_set
        defaultunset = self.msg_flags_common_unset

        jeżeli eor:
            defaultset |= self.msg_flags_eor_indicator
            defaultunset |= self.msg_flags_non_eor_indicator
        albo_inaczej eor jest nie Nic:
            defaultset |= self.msg_flags_non_eor_indicator
            defaultunset |= self.msg_flags_eor_indicator

        # Function arguments override defaults
        defaultset &= ~checkunset
        defaultunset &= ~checkset

        # Merge arguments przy remaining defaults, oraz check dla conflicts
        checkset |= defaultset
        checkunset |= defaultunset
        inboth = checkset & checkunset & ~ignore
        jeżeli inboth:
            podnieś Exception("contradictory set, unset requirements dla flags "
                            "{0:#x}".format(inboth))

        # Compare przy given msg_flags value
        mask = (checkset | checkunset) & ~ignore
        self.assertEqual(flags & mask, checkset & mask)


klasa RecvmsgIntoMixin(SendrecvmsgBase):
    # Mixin to implement doRecvmsg() using recvmsg_into().

    def doRecvmsg(self, sock, bufsize, *args):
        buf = bytearray(bufsize)
        result = sock.recvmsg_into([buf], *args)
        self.registerRecvmsgResult(result)
        self.assertGreaterEqual(result[0], 0)
        self.assertLessEqual(result[0], bufsize)
        zwróć (bytes(buf[:result[0]]),) + result[1:]


klasa SendrecvmsgDgramFlagsBase(SendrecvmsgBase):
    # Defines flags to be checked w msg_flags dla datagram sockets.

    @property
    def msg_flags_non_eor_indicator(self):
        zwróć super().msg_flags_non_eor_indicator | socket.MSG_TRUNC


klasa SendrecvmsgSCTPFlagsBase(SendrecvmsgBase):
    # Defines flags to be checked w msg_flags dla SCTP sockets.

    @property
    def msg_flags_eor_indicator(self):
        zwróć super().msg_flags_eor_indicator | socket.MSG_EOR


klasa SendrecvmsgConnectionlessBase(SendrecvmsgBase):
    # Base klasa dla tests on connectionless-mode sockets.  Users must
    # supply sockets on attributes cli oraz serv to be mapped to
    # cli_sock oraz serv_sock respectively.

    @property
    def serv_sock(self):
        zwróć self.serv

    @property
    def cli_sock(self):
        zwróć self.cli

    @property
    def sendmsg_to_server_defaults(self):
        zwróć ([], [], 0, self.serv_addr)

    def sendToServer(self, msg):
        zwróć self.cli_sock.sendto(msg, self.serv_addr)


klasa SendrecvmsgConnectedBase(SendrecvmsgBase):
    # Base klasa dla tests on connected sockets.  Users must supply
    # sockets on attributes serv_conn oraz cli_conn (representing the
    # connections *to* the server oraz the client), to be mapped to
    # cli_sock oraz serv_sock respectively.

    @property
    def serv_sock(self):
        zwróć self.cli_conn

    @property
    def cli_sock(self):
        zwróć self.serv_conn

    def checkRecvmsgAddress(self, addr1, addr2):
        # Address jest currently "unspecified" dla a connected socket,
        # so we don't examine it
        dalej


klasa SendrecvmsgServerTimeoutBase(SendrecvmsgBase):
    # Base klasa to set a timeout on server's socket.

    def setUp(self):
        super().setUp()
        self.serv_sock.settimeout(self.fail_timeout)


klasa SendmsgTests(SendrecvmsgServerTimeoutBase):
    # Tests dla sendmsg() which can use any socket type oraz do nie
    # involve recvmsg() albo recvmsg_into().

    def testSendmsg(self):
        # Send a simple message przy sendmsg().
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    def _testSendmsg(self):
        self.assertEqual(self.sendmsgToServer([MSG]), len(MSG))

    def testSendmsgDataGenerator(self):
        # Send z buffer obtained z a generator (nie a sequence).
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    def _testSendmsgDataGenerator(self):
        self.assertEqual(self.sendmsgToServer((o dla o w [MSG])),
                         len(MSG))

    def testSendmsgAncillaryGenerator(self):
        # Gather (empty) ancillary data z a generator.
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    def _testSendmsgAncillaryGenerator(self):
        self.assertEqual(self.sendmsgToServer([MSG], (o dla o w [])),
                         len(MSG))

    def testSendmsgArray(self):
        # Send data z an array instead of the usual bytes object.
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    def _testSendmsgArray(self):
        self.assertEqual(self.sendmsgToServer([array.array("B", MSG)]),
                         len(MSG))

    def testSendmsgGather(self):
        # Send message data z more than one buffer (gather write).
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    def _testSendmsgGather(self):
        self.assertEqual(self.sendmsgToServer([MSG[:3], MSG[3:]]), len(MSG))

    def testSendmsgBadArgs(self):
        # Check that sendmsg() rejects invalid arguments.
        self.assertEqual(self.serv_sock.recv(1000), b"done")

    def _testSendmsgBadArgs(self):
        self.assertRaises(TypeError, self.cli_sock.sendmsg)
        self.assertRaises(TypeError, self.sendmsgToServer,
                          b"not w an iterable")
        self.assertRaises(TypeError, self.sendmsgToServer,
                          object())
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [object()])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG, object()])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], object())
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [], object())
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [], 0, object())
        self.sendToServer(b"done")

    def testSendmsgBadCmsg(self):
        # Check that invalid ancillary data items are rejected.
        self.assertEqual(self.serv_sock.recv(1000), b"done")

    def _testSendmsgBadCmsg(self):
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [object()])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(object(), 0, b"data")])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, object(), b"data")])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, 0, object())])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, 0)])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, 0, b"data", 42)])
        self.sendToServer(b"done")

    @requireAttrs(socket, "CMSG_SPACE")
    def testSendmsgBadMultiCmsg(self):
        # Check that invalid ancillary data items are rejected when
        # more than one item jest present.
        self.assertEqual(self.serv_sock.recv(1000), b"done")

    @testSendmsgBadMultiCmsg.client_skip
    def _testSendmsgBadMultiCmsg(self):
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [0, 0, b""])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, 0, b""), object()])
        self.sendToServer(b"done")

    def testSendmsgExcessCmsgReject(self):
        # Check that sendmsg() rejects excess ancillary data items
        # when the number that can be sent jest limited.
        self.assertEqual(self.serv_sock.recv(1000), b"done")

    def _testSendmsgExcessCmsgReject(self):
        jeżeli nie hasattr(socket, "CMSG_SPACE"):
            # Can only send one item
            przy self.assertRaises(OSError) jako cm:
                self.sendmsgToServer([MSG], [(0, 0, b""), (0, 0, b"")])
            self.assertIsNic(cm.exception.errno)
        self.sendToServer(b"done")

    def testSendmsgAfterClose(self):
        # Check that sendmsg() fails on a closed socket.
        dalej

    def _testSendmsgAfterClose(self):
        self.cli_sock.close()
        self.assertRaises(OSError, self.sendmsgToServer, [MSG])


klasa SendmsgStreamTests(SendmsgTests):
    # Tests dla sendmsg() which require a stream socket oraz do nie
    # involve recvmsg() albo recvmsg_into().

    def testSendmsgExplicitNicAddr(self):
        # Check that peer address can be specified jako Nic.
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    def _testSendmsgExplicitNicAddr(self):
        self.assertEqual(self.sendmsgToServer([MSG], [], 0, Nic), len(MSG))

    def testSendmsgTimeout(self):
        # Check that timeout works przy sendmsg().
        self.assertEqual(self.serv_sock.recv(512), b"a"*512)
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))

    def _testSendmsgTimeout(self):
        spróbuj:
            self.cli_sock.settimeout(0.03)
            przy self.assertRaises(socket.timeout):
                dopóki Prawda:
                    self.sendmsgToServer([b"a"*512])
        w_końcu:
            self.misc_event.set()

    # XXX: would be nice to have more tests dla sendmsg flags argument.

    # Linux supports MSG_DONTWAIT when sending, but w general, it
    # only works when receiving.  Could add other platforms jeżeli they
    # support it too.
    @skipWithClientIf(sys.platform nie w {"linux"},
                      "MSG_DONTWAIT nie known to work on this platform when "
                      "sending")
    def testSendmsgDontWait(self):
        # Check that MSG_DONTWAIT w flags causes non-blocking behaviour.
        self.assertEqual(self.serv_sock.recv(512), b"a"*512)
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))

    @testSendmsgDontWait.client_skip
    def _testSendmsgDontWait(self):
        spróbuj:
            przy self.assertRaises(OSError) jako cm:
                dopóki Prawda:
                    self.sendmsgToServer([b"a"*512], [], socket.MSG_DONTWAIT)
            self.assertIn(cm.exception.errno,
                          (errno.EAGAIN, errno.EWOULDBLOCK))
        w_końcu:
            self.misc_event.set()


klasa SendmsgConnectionlessTests(SendmsgTests):
    # Tests dla sendmsg() which require a connectionless-mode
    # (e.g. datagram) socket, oraz do nie involve recvmsg() albo
    # recvmsg_into().

    def testSendmsgNoDestAddr(self):
        # Check that sendmsg() fails when no destination address jest
        # given dla unconnected socket.
        dalej

    def _testSendmsgNoDestAddr(self):
        self.assertRaises(OSError, self.cli_sock.sendmsg,
                          [MSG])
        self.assertRaises(OSError, self.cli_sock.sendmsg,
                          [MSG], [], 0, Nic)


klasa RecvmsgGenericTests(SendrecvmsgBase):
    # Tests dla recvmsg() which can also be emulated using
    # recvmsg_into(), oraz can use any socket type.

    def testRecvmsg(self):
        # Receive a simple message przy recvmsg[_into]().
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, len(MSG))
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsg(self):
        self.sendToServer(MSG)

    def testRecvmsgExplicitDefaults(self):
        # Test recvmsg[_into]() przy default arguments provided explicitly.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 0, 0)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsgExplicitDefaults(self):
        self.sendToServer(MSG)

    def testRecvmsgShorter(self):
        # Receive a message smaller than buffer.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG) + 42)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsgShorter(self):
        self.sendToServer(MSG)

    # FreeBSD < 8 doesn't always set the MSG_TRUNC flag when a truncated
    # datagram jest received (issue #13001).
    @support.requires_freebsd_version(8)
    def testRecvmsgTrunc(self):
        # Receive part of message, check dla truncation indicators.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG) - 3)
        self.assertEqual(msg, MSG[:-3])
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Nieprawda)

    @support.requires_freebsd_version(8)
    def _testRecvmsgTrunc(self):
        self.sendToServer(MSG)

    def testRecvmsgShortAncillaryBuf(self):
        # Test ancillary data buffer too small to hold any ancillary data.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 1)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsgShortAncillaryBuf(self):
        self.sendToServer(MSG)

    def testRecvmsgLongAncillaryBuf(self):
        # Test large ancillary data buffer.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 10240)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsgLongAncillaryBuf(self):
        self.sendToServer(MSG)

    def testRecvmsgAfterClose(self):
        # Check that recvmsg[_into]() fails on a closed socket.
        self.serv_sock.close()
        self.assertRaises(OSError, self.doRecvmsg, self.serv_sock, 1024)

    def _testRecvmsgAfterClose(self):
        dalej

    def testRecvmsgTimeout(self):
        # Check that timeout works.
        spróbuj:
            self.serv_sock.settimeout(0.03)
            self.assertRaises(socket.timeout,
                              self.doRecvmsg, self.serv_sock, len(MSG))
        w_końcu:
            self.misc_event.set()

    def _testRecvmsgTimeout(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))

    @requireAttrs(socket, "MSG_PEEK")
    def testRecvmsgPeek(self):
        # Check that MSG_PEEK w flags enables examination of pending
        # data without consuming it.

        # Receive part of data przy MSG_PEEK.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG) - 3, 0,
                                                   socket.MSG_PEEK)
        self.assertEqual(msg, MSG[:-3])
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        # Ignoring MSG_TRUNC here (so this test jest the same dla stream
        # oraz datagram sockets).  Some wording w POSIX seems to
        # suggest that it needn't be set when peeking, but that may
        # just be a slip.
        self.checkFlags(flags, eor=Nieprawda,
                        ignore=getattr(socket, "MSG_TRUNC", 0))

        # Receive all data przy MSG_PEEK.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 0,
                                                   socket.MSG_PEEK)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

        # Check that the same data can still be received normally.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, len(MSG))
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    @testRecvmsgPeek.client_skip
    def _testRecvmsgPeek(self):
        self.sendToServer(MSG)

    @requireAttrs(socket.socket, "sendmsg")
    def testRecvmsgFromSendmsg(self):
        # Test receiving przy recvmsg[_into]() when message jest sent
        # using sendmsg().
        self.serv_sock.settimeout(self.fail_timeout)
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, len(MSG))
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    @testRecvmsgFromSendmsg.client_skip
    def _testRecvmsgFromSendmsg(self):
        self.assertEqual(self.sendmsgToServer([MSG[:3], MSG[3:]]), len(MSG))


klasa RecvmsgGenericStreamTests(RecvmsgGenericTests):
    # Tests which require a stream socket oraz can use either recvmsg()
    # albo recvmsg_into().

    def testRecvmsgEOF(self):
        # Receive end-of-stream indicator (b"", peer socket closed).
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, 1024)
        self.assertEqual(msg, b"")
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Nic) # Might nie have end-of-record marker

    def _testRecvmsgEOF(self):
        self.cli_sock.close()

    def testRecvmsgOverflow(self):
        # Receive a message w more than one chunk.
        seg1, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                    len(MSG) - 3)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Nieprawda)

        seg2, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, 1024)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

        msg = seg1 + seg2
        self.assertEqual(msg, MSG)

    def _testRecvmsgOverflow(self):
        self.sendToServer(MSG)


klasa RecvmsgTests(RecvmsgGenericTests):
    # Tests dla recvmsg() which can use any socket type.

    def testRecvmsgBadArgs(self):
        # Check that recvmsg() rejects invalid arguments.
        self.assertRaises(TypeError, self.serv_sock.recvmsg)
        self.assertRaises(ValueError, self.serv_sock.recvmsg,
                          -1, 0, 0)
        self.assertRaises(ValueError, self.serv_sock.recvmsg,
                          len(MSG), -1, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg,
                          [bytearray(10)], 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg,
                          object(), 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg,
                          len(MSG), object(), 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg,
                          len(MSG), 0, object())

        msg, ancdata, flags, addr = self.serv_sock.recvmsg(len(MSG), 0, 0)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsgBadArgs(self):
        self.sendToServer(MSG)


klasa RecvmsgIntoTests(RecvmsgIntoMixin, RecvmsgGenericTests):
    # Tests dla recvmsg_into() which can use any socket type.

    def testRecvmsgIntoBadArgs(self):
        # Check that recvmsg_into() rejects invalid arguments.
        buf = bytearray(len(MSG))
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          len(MSG), 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          buf, 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [object()], 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [b"I'm nie writable"], 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [buf, object()], 0, 0)
        self.assertRaises(ValueError, self.serv_sock.recvmsg_into,
                          [buf], -1, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [buf], object(), 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [buf], 0, object())

        nbytes, ancdata, flags, addr = self.serv_sock.recvmsg_into([buf], 0, 0)
        self.assertEqual(nbytes, len(MSG))
        self.assertEqual(buf, bytearray(MSG))
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsgIntoBadArgs(self):
        self.sendToServer(MSG)

    def testRecvmsgIntoGenerator(self):
        # Receive into buffer obtained z a generator (nie a sequence).
        buf = bytearray(len(MSG))
        nbytes, ancdata, flags, addr = self.serv_sock.recvmsg_into(
            (o dla o w [buf]))
        self.assertEqual(nbytes, len(MSG))
        self.assertEqual(buf, bytearray(MSG))
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsgIntoGenerator(self):
        self.sendToServer(MSG)

    def testRecvmsgIntoArray(self):
        # Receive into an array rather than the usual bytearray.
        buf = array.array("B", [0] * len(MSG))
        nbytes, ancdata, flags, addr = self.serv_sock.recvmsg_into([buf])
        self.assertEqual(nbytes, len(MSG))
        self.assertEqual(buf.tobytes(), MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsgIntoArray(self):
        self.sendToServer(MSG)

    def testRecvmsgIntoScatter(self):
        # Receive into multiple buffers (scatter write).
        b1 = bytearray(b"----")
        b2 = bytearray(b"0123456789")
        b3 = bytearray(b"--------------")
        nbytes, ancdata, flags, addr = self.serv_sock.recvmsg_into(
            [b1, memoryview(b2)[2:9], b3])
        self.assertEqual(nbytes, len(b"Mary had a little lamb"))
        self.assertEqual(b1, bytearray(b"Mary"))
        self.assertEqual(b2, bytearray(b"01 had a 9"))
        self.assertEqual(b3, bytearray(b"little lamb---"))
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda)

    def _testRecvmsgIntoScatter(self):
        self.sendToServer(b"Mary had a little lamb")


klasa CmsgMacroTests(unittest.TestCase):
    # Test the functions CMSG_LEN() oraz CMSG_SPACE().  Tests
    # assumptions used by sendmsg() oraz recvmsg[_into](), which share
    # code przy these functions.

    # Match the definition w socketmodule.c
    spróbuj:
        zaimportuj _testcapi
    wyjąwszy ImportError:
        socklen_t_limit = 0x7fffffff
    inaczej:
        socklen_t_limit = min(0x7fffffff, _testcapi.INT_MAX)

    @requireAttrs(socket, "CMSG_LEN")
    def testCMSG_LEN(self):
        # Test CMSG_LEN() przy various valid oraz invalid values,
        # checking the assumptions used by recvmsg() oraz sendmsg().
        toobig = self.socklen_t_limit - socket.CMSG_LEN(0) + 1
        values = list(range(257)) + list(range(toobig - 257, toobig))

        # struct cmsghdr has at least three members, two of which are ints
        self.assertGreater(socket.CMSG_LEN(0), array.array("i").itemsize * 2)
        dla n w values:
            ret = socket.CMSG_LEN(n)
            # This jest how recvmsg() calculates the data size
            self.assertEqual(ret - socket.CMSG_LEN(0), n)
            self.assertLessEqual(ret, self.socklen_t_limit)

        self.assertRaises(OverflowError, socket.CMSG_LEN, -1)
        # sendmsg() shares code przy these functions, oraz requires
        # that it reject values over the limit.
        self.assertRaises(OverflowError, socket.CMSG_LEN, toobig)
        self.assertRaises(OverflowError, socket.CMSG_LEN, sys.maxsize)

    @requireAttrs(socket, "CMSG_SPACE")
    def testCMSG_SPACE(self):
        # Test CMSG_SPACE() przy various valid oraz invalid values,
        # checking the assumptions used by sendmsg().
        toobig = self.socklen_t_limit - socket.CMSG_SPACE(1) + 1
        values = list(range(257)) + list(range(toobig - 257, toobig))

        last = socket.CMSG_SPACE(0)
        # struct cmsghdr has at least three members, two of which are ints
        self.assertGreater(last, array.array("i").itemsize * 2)
        dla n w values:
            ret = socket.CMSG_SPACE(n)
            self.assertGreaterEqual(ret, last)
            self.assertGreaterEqual(ret, socket.CMSG_LEN(n))
            self.assertGreaterEqual(ret, n + socket.CMSG_LEN(0))
            self.assertLessEqual(ret, self.socklen_t_limit)
            last = ret

        self.assertRaises(OverflowError, socket.CMSG_SPACE, -1)
        # sendmsg() shares code przy these functions, oraz requires
        # that it reject values over the limit.
        self.assertRaises(OverflowError, socket.CMSG_SPACE, toobig)
        self.assertRaises(OverflowError, socket.CMSG_SPACE, sys.maxsize)


klasa SCMRightsTest(SendrecvmsgServerTimeoutBase):
    # Tests dla file descriptor dalejing on Unix-domain sockets.

    # Invalid file descriptor value that's unlikely to evaluate to a
    # real FD even jeżeli one of its bytes jest replaced przy a different
    # value (which shouldn't actually happen).
    badfd = -0x5555

    def newFDs(self, n):
        # Return a list of n file descriptors dla newly-created files
        # containing their list indices jako ASCII numbers.
        fds = []
        dla i w range(n):
            fd, path = tempfile.mkstemp()
            self.addCleanup(os.unlink, path)
            self.addCleanup(os.close, fd)
            os.write(fd, str(i).encode())
            fds.append(fd)
        zwróć fds

    def checkFDs(self, fds):
        # Check that the file descriptors w the given list contain
        # their correct list indices jako ASCII numbers.
        dla n, fd w enumerate(fds):
            os.lseek(fd, 0, os.SEEK_SET)
            self.assertEqual(os.read(fd, 1024), str(n).encode())

    def registerRecvmsgResult(self, result):
        self.addCleanup(self.closeRecvmsgFDs, result)

    def closeRecvmsgFDs(self, recvmsg_result):
        # Close all file descriptors specified w the ancillary data
        # of the given zwróć value z recvmsg() albo recvmsg_into().
        dla cmsg_level, cmsg_type, cmsg_data w recvmsg_result[1]:
            jeżeli (cmsg_level == socket.SOL_SOCKET oraz
                    cmsg_type == socket.SCM_RIGHTS):
                fds = array.array("i")
                fds.frombytes(cmsg_data[:
                        len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
                dla fd w fds:
                    os.close(fd)

    def createAndSendFDs(self, n):
        # Send n new file descriptors created by newFDs() to the
        # server, przy the constant MSG jako the non-ancillary data.
        self.assertEqual(
            self.sendmsgToServer([MSG],
                                 [(socket.SOL_SOCKET,
                                   socket.SCM_RIGHTS,
                                   array.array("i", self.newFDs(n)))]),
            len(MSG))

    def checkRecvmsgFDs(self, numfds, result, maxcmsgs=1, ignoreflags=0):
        # Check that constant MSG was received przy numfds file
        # descriptors w a maximum of maxcmsgs control messages (which
        # must contain only complete integers).  By default, check
        # that MSG_CTRUNC jest unset, but ignore any flags w
        # ignoreflags.
        msg, ancdata, flags, addr = result
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Prawda, checkunset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

        self.assertIsInstance(ancdata, list)
        self.assertLessEqual(len(ancdata), maxcmsgs)
        fds = array.array("i")
        dla item w ancdata:
            self.assertIsInstance(item, tuple)
            cmsg_level, cmsg_type, cmsg_data = item
            self.assertEqual(cmsg_level, socket.SOL_SOCKET)
            self.assertEqual(cmsg_type, socket.SCM_RIGHTS)
            self.assertIsInstance(cmsg_data, bytes)
            self.assertEqual(len(cmsg_data) % SIZEOF_INT, 0)
            fds.frombytes(cmsg_data)

        self.assertEqual(len(fds), numfds)
        self.checkFDs(fds)

    def testFDPassSimple(self):
        # Pass a single FD (array read z bytes object).
        self.checkRecvmsgFDs(1, self.doRecvmsg(self.serv_sock,
                                               len(MSG), 10240))

    def _testFDPassSimple(self):
        self.assertEqual(
            self.sendmsgToServer(
                [MSG],
                [(socket.SOL_SOCKET,
                  socket.SCM_RIGHTS,
                  array.array("i", self.newFDs(1)).tobytes())]),
            len(MSG))

    def testMultipleFDPass(self):
        # Pass multiple FDs w a single array.
        self.checkRecvmsgFDs(4, self.doRecvmsg(self.serv_sock,
                                               len(MSG), 10240))

    def _testMultipleFDPass(self):
        self.createAndSendFDs(4)

    @requireAttrs(socket, "CMSG_SPACE")
    def testFDPassCMSG_SPACE(self):
        # Test using CMSG_SPACE() to calculate ancillary buffer size.
        self.checkRecvmsgFDs(
            4, self.doRecvmsg(self.serv_sock, len(MSG),
                              socket.CMSG_SPACE(4 * SIZEOF_INT)))

    @testFDPassCMSG_SPACE.client_skip
    def _testFDPassCMSG_SPACE(self):
        self.createAndSendFDs(4)

    def testFDPassCMSG_LEN(self):
        # Test using CMSG_LEN() to calculate ancillary buffer size.
        self.checkRecvmsgFDs(1,
                             self.doRecvmsg(self.serv_sock, len(MSG),
                                            socket.CMSG_LEN(4 * SIZEOF_INT)),
                             # RFC 3542 says implementations may set
                             # MSG_CTRUNC jeżeli there isn't enough space
                             # dla trailing padding.
                             ignoreflags=socket.MSG_CTRUNC)

    def _testFDPassCMSG_LEN(self):
        self.createAndSendFDs(1)

    @unittest.skipIf(sys.platform == "darwin", "skipping, see issue #12958")
    @unittest.skipIf(sys.platform.startswith("aix"), "skipping, see issue #22397")
    @requireAttrs(socket, "CMSG_SPACE")
    def testFDPassSeparate(self):
        # Pass two FDs w two separate arrays.  Arrays may be combined
        # into a single control message by the OS.
        self.checkRecvmsgFDs(2,
                             self.doRecvmsg(self.serv_sock, len(MSG), 10240),
                             maxcmsgs=2)

    @testFDPassSeparate.client_skip
    @unittest.skipIf(sys.platform == "darwin", "skipping, see issue #12958")
    @unittest.skipIf(sys.platform.startswith("aix"), "skipping, see issue #22397")
    def _testFDPassSeparate(self):
        fd0, fd1 = self.newFDs(2)
        self.assertEqual(
            self.sendmsgToServer([MSG], [(socket.SOL_SOCKET,
                                          socket.SCM_RIGHTS,
                                          array.array("i", [fd0])),
                                         (socket.SOL_SOCKET,
                                          socket.SCM_RIGHTS,
                                          array.array("i", [fd1]))]),
            len(MSG))

    @unittest.skipIf(sys.platform == "darwin", "skipping, see issue #12958")
    @unittest.skipIf(sys.platform.startswith("aix"), "skipping, see issue #22397")
    @requireAttrs(socket, "CMSG_SPACE")
    def testFDPassSeparateMinSpace(self):
        # Pass two FDs w two separate arrays, receiving them into the
        # minimum space dla two arrays.
        self.checkRecvmsgFDs(2,
                             self.doRecvmsg(self.serv_sock, len(MSG),
                                            socket.CMSG_SPACE(SIZEOF_INT) +
                                            socket.CMSG_LEN(SIZEOF_INT)),
                             maxcmsgs=2, ignoreflags=socket.MSG_CTRUNC)

    @testFDPassSeparateMinSpace.client_skip
    @unittest.skipIf(sys.platform == "darwin", "skipping, see issue #12958")
    @unittest.skipIf(sys.platform.startswith("aix"), "skipping, see issue #22397")
    def _testFDPassSeparateMinSpace(self):
        fd0, fd1 = self.newFDs(2)
        self.assertEqual(
            self.sendmsgToServer([MSG], [(socket.SOL_SOCKET,
                                          socket.SCM_RIGHTS,
                                          array.array("i", [fd0])),
                                         (socket.SOL_SOCKET,
                                          socket.SCM_RIGHTS,
                                          array.array("i", [fd1]))]),
            len(MSG))

    def sendAncillaryIfPossible(self, msg, ancdata):
        # Try to send msg oraz ancdata to server, but jeżeli the system
        # call fails, just send msg przy no ancillary data.
        spróbuj:
            nbytes = self.sendmsgToServer([msg], ancdata)
        wyjąwszy OSError jako e:
            # Check that it was the system call that failed
            self.assertIsInstance(e.errno, int)
            nbytes = self.sendmsgToServer([msg])
        self.assertEqual(nbytes, len(msg))

    def testFDPassEmpty(self):
        # Try to dalej an empty FD array.  Can receive either no array
        # albo an empty array.
        self.checkRecvmsgFDs(0, self.doRecvmsg(self.serv_sock,
                                               len(MSG), 10240),
                             ignoreflags=socket.MSG_CTRUNC)

    def _testFDPassEmpty(self):
        self.sendAncillaryIfPossible(MSG, [(socket.SOL_SOCKET,
                                            socket.SCM_RIGHTS,
                                            b"")])

    def testFDPassPartialInt(self):
        # Try to dalej a truncated FD array.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 10240)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Prawda, ignore=socket.MSG_CTRUNC)
        self.assertLessEqual(len(ancdata), 1)
        dla cmsg_level, cmsg_type, cmsg_data w ancdata:
            self.assertEqual(cmsg_level, socket.SOL_SOCKET)
            self.assertEqual(cmsg_type, socket.SCM_RIGHTS)
            self.assertLess(len(cmsg_data), SIZEOF_INT)

    def _testFDPassPartialInt(self):
        self.sendAncillaryIfPossible(
            MSG,
            [(socket.SOL_SOCKET,
              socket.SCM_RIGHTS,
              array.array("i", [self.badfd]).tobytes()[:-1])])

    @requireAttrs(socket, "CMSG_SPACE")
    def testFDPassPartialIntInMiddle(self):
        # Try to dalej two FD arrays, the first of which jest truncated.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 10240)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Prawda, ignore=socket.MSG_CTRUNC)
        self.assertLessEqual(len(ancdata), 2)
        fds = array.array("i")
        # Arrays may have been combined w a single control message
        dla cmsg_level, cmsg_type, cmsg_data w ancdata:
            self.assertEqual(cmsg_level, socket.SOL_SOCKET)
            self.assertEqual(cmsg_type, socket.SCM_RIGHTS)
            fds.frombytes(cmsg_data[:
                    len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
        self.assertLessEqual(len(fds), 2)
        self.checkFDs(fds)

    @testFDPassPartialIntInMiddle.client_skip
    def _testFDPassPartialIntInMiddle(self):
        fd0, fd1 = self.newFDs(2)
        self.sendAncillaryIfPossible(
            MSG,
            [(socket.SOL_SOCKET,
              socket.SCM_RIGHTS,
              array.array("i", [fd0, self.badfd]).tobytes()[:-1]),
             (socket.SOL_SOCKET,
              socket.SCM_RIGHTS,
              array.array("i", [fd1]))])

    def checkTruncatedHeader(self, result, ignoreflags=0):
        # Check that no ancillary data items are returned when data jest
        # truncated inside the cmsghdr structure.
        msg, ancdata, flags, addr = result
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda, checkset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

    def testCmsgTruncNoBufSize(self):
        # Check that no ancillary data jest received when no buffer size
        # jest specified.
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG)),
                                  # BSD seems to set MSG_CTRUNC only
                                  # jeżeli an item has been partially
                                  # received.
                                  ignoreflags=socket.MSG_CTRUNC)

    def _testCmsgTruncNoBufSize(self):
        self.createAndSendFDs(1)

    def testCmsgTrunc0(self):
        # Check that no ancillary data jest received when buffer size jest 0.
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG), 0),
                                  ignoreflags=socket.MSG_CTRUNC)

    def _testCmsgTrunc0(self):
        self.createAndSendFDs(1)

    # Check that no ancillary data jest returned dla various non-zero
    # (but still too small) buffer sizes.

    def testCmsgTrunc1(self):
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG), 1))

    def _testCmsgTrunc1(self):
        self.createAndSendFDs(1)

    def testCmsgTrunc2Int(self):
        # The cmsghdr structure has at least three members, two of
        # which are ints, so we still shouldn't see any ancillary
        # data.
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG),
                                                 SIZEOF_INT * 2))

    def _testCmsgTrunc2Int(self):
        self.createAndSendFDs(1)

    def testCmsgTruncLen0Minus1(self):
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG),
                                                 socket.CMSG_LEN(0) - 1))

    def _testCmsgTruncLen0Minus1(self):
        self.createAndSendFDs(1)

    # The following tests try to truncate the control message w the
    # middle of the FD array.

    def checkTruncatedArray(self, ancbuf, maxdata, mindata=0):
        # Check that file descriptor data jest truncated to between
        # mindata oraz maxdata bytes when received przy buffer size
        # ancbuf, oraz that any complete file descriptor numbers are
        # valid.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), ancbuf)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Prawda, checkset=socket.MSG_CTRUNC)

        jeżeli mindata == 0 oraz ancdata == []:
            zwróć
        self.assertEqual(len(ancdata), 1)
        cmsg_level, cmsg_type, cmsg_data = ancdata[0]
        self.assertEqual(cmsg_level, socket.SOL_SOCKET)
        self.assertEqual(cmsg_type, socket.SCM_RIGHTS)
        self.assertGreaterEqual(len(cmsg_data), mindata)
        self.assertLessEqual(len(cmsg_data), maxdata)
        fds = array.array("i")
        fds.frombytes(cmsg_data[:
                len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
        self.checkFDs(fds)

    def testCmsgTruncLen0(self):
        self.checkTruncatedArray(ancbuf=socket.CMSG_LEN(0), maxdata=0)

    def _testCmsgTruncLen0(self):
        self.createAndSendFDs(1)

    def testCmsgTruncLen0Plus1(self):
        self.checkTruncatedArray(ancbuf=socket.CMSG_LEN(0) + 1, maxdata=1)

    def _testCmsgTruncLen0Plus1(self):
        self.createAndSendFDs(2)

    def testCmsgTruncLen1(self):
        self.checkTruncatedArray(ancbuf=socket.CMSG_LEN(SIZEOF_INT),
                                 maxdata=SIZEOF_INT)

    def _testCmsgTruncLen1(self):
        self.createAndSendFDs(2)

    def testCmsgTruncLen2Minus1(self):
        self.checkTruncatedArray(ancbuf=socket.CMSG_LEN(2 * SIZEOF_INT) - 1,
                                 maxdata=(2 * SIZEOF_INT) - 1)

    def _testCmsgTruncLen2Minus1(self):
        self.createAndSendFDs(2)


klasa RFC3542AncillaryTest(SendrecvmsgServerTimeoutBase):
    # Test sendmsg() oraz recvmsg[_into]() using the ancillary data
    # features of the RFC 3542 Advanced Sockets API dla IPv6.
    # Currently we can only handle certain data items (e.g. traffic
    # class, hop limit, MTU discovery oraz fragmentation settings)
    # without resorting to unportable means such jako the struct module,
    # but the tests here are aimed at testing the ancillary data
    # handling w sendmsg() oraz recvmsg() rather than the IPv6 API
    # itself.

    # Test value to use when setting hop limit of packet
    hop_limit = 2

    # Test value to use when setting traffic klasa of packet.
    # -1 means "use kernel default".
    traffic_class = -1

    def ancillaryMapping(self, ancdata):
        # Given ancillary data list ancdata, zwróć a mapping from
        # pairs (cmsg_level, cmsg_type) to corresponding cmsg_data.
        # Check that no (level, type) pair appears more than once.
        d = {}
        dla cmsg_level, cmsg_type, cmsg_data w ancdata:
            self.assertNotIn((cmsg_level, cmsg_type), d)
            d[(cmsg_level, cmsg_type)] = cmsg_data
        zwróć d

    def checkHopLimit(self, ancbufsize, maxhop=255, ignoreflags=0):
        # Receive hop limit into ancbufsize bytes of ancillary data
        # space.  Check that data jest MSG, ancillary data jest nie
        # truncated (but ignore any flags w ignoreflags), oraz hop
        # limit jest between 0 oraz maxhop inclusive.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), ancbufsize)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Prawda, checkunset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

        self.assertEqual(len(ancdata), 1)
        self.assertIsInstance(ancdata[0], tuple)
        cmsg_level, cmsg_type, cmsg_data = ancdata[0]
        self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
        self.assertEqual(cmsg_type, socket.IPV6_HOPLIMIT)
        self.assertIsInstance(cmsg_data, bytes)
        self.assertEqual(len(cmsg_data), SIZEOF_INT)
        a = array.array("i")
        a.frombytes(cmsg_data)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], maxhop)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    def testRecvHopLimit(self):
        # Test receiving the packet hop limit jako ancillary data.
        self.checkHopLimit(ancbufsize=10240)

    @testRecvHopLimit.client_skip
    def _testRecvHopLimit(self):
        # Need to wait until server has asked to receive ancillary
        # data, jako implementations are nie required to buffer it
        # otherwise.
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    def testRecvHopLimitCMSG_SPACE(self):
        # Test receiving hop limit, using CMSG_SPACE to calculate buffer size.
        self.checkHopLimit(ancbufsize=socket.CMSG_SPACE(SIZEOF_INT))

    @testRecvHopLimitCMSG_SPACE.client_skip
    def _testRecvHopLimitCMSG_SPACE(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    # Could test receiving into buffer sized using CMSG_LEN, but RFC
    # 3542 says portable applications must provide space dla trailing
    # padding.  Implementations may set MSG_CTRUNC jeżeli there isn't
    # enough space dla the padding.

    @requireAttrs(socket.socket, "sendmsg")
    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    def testSetHopLimit(self):
        # Test setting hop limit on outgoing packet oraz receiving it
        # at the other end.
        self.checkHopLimit(ancbufsize=10240, maxhop=self.hop_limit)

    @testSetHopLimit.client_skip
    def _testSetHopLimit(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.assertEqual(
            self.sendmsgToServer([MSG],
                                 [(socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT,
                                   array.array("i", [self.hop_limit]))]),
            len(MSG))

    def checkTrafficClassAndHopLimit(self, ancbufsize, maxhop=255,
                                     ignoreflags=0):
        # Receive traffic klasa oraz hop limit into ancbufsize bytes of
        # ancillary data space.  Check that data jest MSG, ancillary
        # data jest nie truncated (but ignore any flags w ignoreflags),
        # oraz traffic klasa oraz hop limit are w range (hop limit no
        # more than maxhop).
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVTCLASS, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), ancbufsize)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Prawda, checkunset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)
        self.assertEqual(len(ancdata), 2)
        ancmap = self.ancillaryMapping(ancdata)

        tcdata = ancmap[(socket.IPPROTO_IPV6, socket.IPV6_TCLASS)]
        self.assertEqual(len(tcdata), SIZEOF_INT)
        a = array.array("i")
        a.frombytes(tcdata)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], 255)

        hldata = ancmap[(socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT)]
        self.assertEqual(len(hldata), SIZEOF_INT)
        a = array.array("i")
        a.frombytes(hldata)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], maxhop)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    def testRecvTrafficClassAndHopLimit(self):
        # Test receiving traffic klasa oraz hop limit jako ancillary data.
        self.checkTrafficClassAndHopLimit(ancbufsize=10240)

    @testRecvTrafficClassAndHopLimit.client_skip
    def _testRecvTrafficClassAndHopLimit(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    def testRecvTrafficClassAndHopLimitCMSG_SPACE(self):
        # Test receiving traffic klasa oraz hop limit, using
        # CMSG_SPACE() to calculate buffer size.
        self.checkTrafficClassAndHopLimit(
            ancbufsize=socket.CMSG_SPACE(SIZEOF_INT) * 2)

    @testRecvTrafficClassAndHopLimitCMSG_SPACE.client_skip
    def _testRecvTrafficClassAndHopLimitCMSG_SPACE(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket.socket, "sendmsg")
    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    def testSetTrafficClassAndHopLimit(self):
        # Test setting traffic klasa oraz hop limit on outgoing packet,
        # oraz receiving them at the other end.
        self.checkTrafficClassAndHopLimit(ancbufsize=10240,
                                          maxhop=self.hop_limit)

    @testSetTrafficClassAndHopLimit.client_skip
    def _testSetTrafficClassAndHopLimit(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.assertEqual(
            self.sendmsgToServer([MSG],
                                 [(socket.IPPROTO_IPV6, socket.IPV6_TCLASS,
                                   array.array("i", [self.traffic_class])),
                                  (socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT,
                                   array.array("i", [self.hop_limit]))]),
            len(MSG))

    @requireAttrs(socket.socket, "sendmsg")
    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    def testOddCmsgSize(self):
        # Try to send ancillary data przy first item one byte too
        # long.  Fall back to sending przy correct size jeżeli this fails,
        # oraz check that second item was handled correctly.
        self.checkTrafficClassAndHopLimit(ancbufsize=10240,
                                          maxhop=self.hop_limit)

    @testOddCmsgSize.client_skip
    def _testOddCmsgSize(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        spróbuj:
            nbytes = self.sendmsgToServer(
                [MSG],
                [(socket.IPPROTO_IPV6, socket.IPV6_TCLASS,
                  array.array("i", [self.traffic_class]).tobytes() + b"\x00"),
                 (socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT,
                  array.array("i", [self.hop_limit]))])
        wyjąwszy OSError jako e:
            self.assertIsInstance(e.errno, int)
            nbytes = self.sendmsgToServer(
                [MSG],
                [(socket.IPPROTO_IPV6, socket.IPV6_TCLASS,
                  array.array("i", [self.traffic_class])),
                 (socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT,
                  array.array("i", [self.hop_limit]))])
            self.assertEqual(nbytes, len(MSG))

    # Tests dla proper handling of truncated ancillary data

    def checkHopLimitTruncatedHeader(self, ancbufsize, ignoreflags=0):
        # Receive hop limit into ancbufsize bytes of ancillary data
        # space, which should be too small to contain the ancillary
        # data header (jeżeli ancbufsize jest Nic, dalej no second argument
        # to recvmsg()).  Check that data jest MSG, MSG_CTRUNC jest set
        # (unless included w ignoreflags), oraz no ancillary data jest
        # returned.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.misc_event.set()
        args = () jeżeli ancbufsize jest Nic inaczej (ancbufsize,)
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), *args)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Prawda, checkset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    def testCmsgTruncNoBufSize(self):
        # Check that no ancillary data jest received when no ancillary
        # buffer size jest provided.
        self.checkHopLimitTruncatedHeader(ancbufsize=Nic,
                                          # BSD seems to set
                                          # MSG_CTRUNC only jeżeli an item
                                          # has been partially
                                          # received.
                                          ignoreflags=socket.MSG_CTRUNC)

    @testCmsgTruncNoBufSize.client_skip
    def _testCmsgTruncNoBufSize(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    def testSingleCmsgTrunc0(self):
        # Check that no ancillary data jest received when ancillary
        # buffer size jest zero.
        self.checkHopLimitTruncatedHeader(ancbufsize=0,
                                          ignoreflags=socket.MSG_CTRUNC)

    @testSingleCmsgTrunc0.client_skip
    def _testSingleCmsgTrunc0(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    # Check that no ancillary data jest returned dla various non-zero
    # (but still too small) buffer sizes.

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    def testSingleCmsgTrunc1(self):
        self.checkHopLimitTruncatedHeader(ancbufsize=1)

    @testSingleCmsgTrunc1.client_skip
    def _testSingleCmsgTrunc1(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    def testSingleCmsgTrunc2Int(self):
        self.checkHopLimitTruncatedHeader(ancbufsize=2 * SIZEOF_INT)

    @testSingleCmsgTrunc2Int.client_skip
    def _testSingleCmsgTrunc2Int(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    def testSingleCmsgTruncLen0Minus1(self):
        self.checkHopLimitTruncatedHeader(ancbufsize=socket.CMSG_LEN(0) - 1)

    @testSingleCmsgTruncLen0Minus1.client_skip
    def _testSingleCmsgTruncLen0Minus1(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    def testSingleCmsgTruncInData(self):
        # Test truncation of a control message inside its associated
        # data.  The message may be returned przy its data truncated,
        # albo nie returned at all.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(
            self.serv_sock, len(MSG), socket.CMSG_LEN(SIZEOF_INT) - 1)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Prawda, checkset=socket.MSG_CTRUNC)

        self.assertLessEqual(len(ancdata), 1)
        jeżeli ancdata:
            cmsg_level, cmsg_type, cmsg_data = ancdata[0]
            self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
            self.assertEqual(cmsg_type, socket.IPV6_HOPLIMIT)
            self.assertLess(len(cmsg_data), SIZEOF_INT)

    @testSingleCmsgTruncInData.client_skip
    def _testSingleCmsgTruncInData(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    def checkTruncatedSecondHeader(self, ancbufsize, ignoreflags=0):
        # Receive traffic klasa oraz hop limit into ancbufsize bytes of
        # ancillary data space, which should be large enough to
        # contain the first item, but too small to contain the header
        # of the second.  Check that data jest MSG, MSG_CTRUNC jest set
        # (unless included w ignoreflags), oraz only one ancillary
        # data item jest returned.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVTCLASS, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), ancbufsize)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Prawda, checkset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

        self.assertEqual(len(ancdata), 1)
        cmsg_level, cmsg_type, cmsg_data = ancdata[0]
        self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
        self.assertIn(cmsg_type, {socket.IPV6_TCLASS, socket.IPV6_HOPLIMIT})
        self.assertEqual(len(cmsg_data), SIZEOF_INT)
        a = array.array("i")
        a.frombytes(cmsg_data)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], 255)

    # Try the above test przy various buffer sizes.

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    def testSecondCmsgTrunc0(self):
        self.checkTruncatedSecondHeader(socket.CMSG_SPACE(SIZEOF_INT),
                                        ignoreflags=socket.MSG_CTRUNC)

    @testSecondCmsgTrunc0.client_skip
    def _testSecondCmsgTrunc0(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    def testSecondCmsgTrunc1(self):
        self.checkTruncatedSecondHeader(socket.CMSG_SPACE(SIZEOF_INT) + 1)

    @testSecondCmsgTrunc1.client_skip
    def _testSecondCmsgTrunc1(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    def testSecondCmsgTrunc2Int(self):
        self.checkTruncatedSecondHeader(socket.CMSG_SPACE(SIZEOF_INT) +
                                        2 * SIZEOF_INT)

    @testSecondCmsgTrunc2Int.client_skip
    def _testSecondCmsgTrunc2Int(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    def testSecondCmsgTruncLen0Minus1(self):
        self.checkTruncatedSecondHeader(socket.CMSG_SPACE(SIZEOF_INT) +
                                        socket.CMSG_LEN(0) - 1)

    @testSecondCmsgTruncLen0Minus1.client_skip
    def _testSecondCmsgTruncLen0Minus1(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    def testSecomdCmsgTruncInData(self):
        # Test truncation of the second of two control messages inside
        # its associated data.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVTCLASS, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(
            self.serv_sock, len(MSG),
            socket.CMSG_SPACE(SIZEOF_INT) + socket.CMSG_LEN(SIZEOF_INT) - 1)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Prawda, checkset=socket.MSG_CTRUNC)

        cmsg_types = {socket.IPV6_TCLASS, socket.IPV6_HOPLIMIT}

        cmsg_level, cmsg_type, cmsg_data = ancdata.pop(0)
        self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
        cmsg_types.remove(cmsg_type)
        self.assertEqual(len(cmsg_data), SIZEOF_INT)
        a = array.array("i")
        a.frombytes(cmsg_data)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], 255)

        jeżeli ancdata:
            cmsg_level, cmsg_type, cmsg_data = ancdata.pop(0)
            self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
            cmsg_types.remove(cmsg_type)
            self.assertLess(len(cmsg_data), SIZEOF_INT)

        self.assertEqual(ancdata, [])

    @testSecomdCmsgTruncInData.client_skip
    def _testSecomdCmsgTruncInData(self):
        self.assertPrawda(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)


# Derive concrete test classes dla different socket types.

klasa SendrecvmsgUDPTestBase(SendrecvmsgDgramFlagsBase,
                             SendrecvmsgConnectionlessBase,
                             ThreadedSocketTestMixin, UDPTestBase):
    dalej

@requireAttrs(socket.socket, "sendmsg")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa SendmsgUDPTest(SendmsgConnectionlessTests, SendrecvmsgUDPTestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgUDPTest(RecvmsgTests, SendrecvmsgUDPTestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg_into")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgIntoUDPTest(RecvmsgIntoTests, SendrecvmsgUDPTestBase):
    dalej


klasa SendrecvmsgUDP6TestBase(SendrecvmsgDgramFlagsBase,
                              SendrecvmsgConnectionlessBase,
                              ThreadedSocketTestMixin, UDP6TestBase):

    def checkRecvmsgAddress(self, addr1, addr2):
        # Called to compare the received address przy the address of
        # the peer, ignoring scope ID
        self.assertEqual(addr1[:-1], addr2[:-1])

@requireAttrs(socket.socket, "sendmsg")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required dla this test.')
@requireSocket("AF_INET6", "SOCK_DGRAM")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa SendmsgUDP6Test(SendmsgConnectionlessTests, SendrecvmsgUDP6TestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required dla this test.')
@requireSocket("AF_INET6", "SOCK_DGRAM")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgUDP6Test(RecvmsgTests, SendrecvmsgUDP6TestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg_into")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required dla this test.')
@requireSocket("AF_INET6", "SOCK_DGRAM")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgIntoUDP6Test(RecvmsgIntoTests, SendrecvmsgUDP6TestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required dla this test.')
@requireAttrs(socket, "IPPROTO_IPV6")
@requireSocket("AF_INET6", "SOCK_DGRAM")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgRFC3542AncillaryUDP6Test(RFC3542AncillaryTest,
                                      SendrecvmsgUDP6TestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg_into")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required dla this test.')
@requireAttrs(socket, "IPPROTO_IPV6")
@requireSocket("AF_INET6", "SOCK_DGRAM")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgIntoRFC3542AncillaryUDP6Test(RecvmsgIntoMixin,
                                          RFC3542AncillaryTest,
                                          SendrecvmsgUDP6TestBase):
    dalej


klasa SendrecvmsgTCPTestBase(SendrecvmsgConnectedBase,
                             ConnectedStreamTestMixin, TCPTestBase):
    dalej

@requireAttrs(socket.socket, "sendmsg")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa SendmsgTCPTest(SendmsgStreamTests, SendrecvmsgTCPTestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgTCPTest(RecvmsgTests, RecvmsgGenericStreamTests,
                     SendrecvmsgTCPTestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg_into")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgIntoTCPTest(RecvmsgIntoTests, RecvmsgGenericStreamTests,
                         SendrecvmsgTCPTestBase):
    dalej


klasa SendrecvmsgSCTPStreamTestBase(SendrecvmsgSCTPFlagsBase,
                                    SendrecvmsgConnectedBase,
                                    ConnectedStreamTestMixin, SCTPStreamBase):
    dalej

@requireAttrs(socket.socket, "sendmsg")
@requireSocket("AF_INET", "SOCK_STREAM", "IPPROTO_SCTP")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa SendmsgSCTPStreamTest(SendmsgStreamTests, SendrecvmsgSCTPStreamTestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg")
@requireSocket("AF_INET", "SOCK_STREAM", "IPPROTO_SCTP")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgSCTPStreamTest(RecvmsgTests, RecvmsgGenericStreamTests,
                            SendrecvmsgSCTPStreamTestBase):

    def testRecvmsgEOF(self):
        spróbuj:
            super(RecvmsgSCTPStreamTest, self).testRecvmsgEOF()
        wyjąwszy OSError jako e:
            jeżeli e.errno != errno.ENOTCONN:
                podnieś
            self.skipTest("sporadic ENOTCONN (kernel issue?) - see issue #13876")

@requireAttrs(socket.socket, "recvmsg_into")
@requireSocket("AF_INET", "SOCK_STREAM", "IPPROTO_SCTP")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgIntoSCTPStreamTest(RecvmsgIntoTests, RecvmsgGenericStreamTests,
                                SendrecvmsgSCTPStreamTestBase):

    def testRecvmsgEOF(self):
        spróbuj:
            super(RecvmsgIntoSCTPStreamTest, self).testRecvmsgEOF()
        wyjąwszy OSError jako e:
            jeżeli e.errno != errno.ENOTCONN:
                podnieś
            self.skipTest("sporadic ENOTCONN (kernel issue?) - see issue #13876")


klasa SendrecvmsgUnixStreamTestBase(SendrecvmsgConnectedBase,
                                    ConnectedStreamTestMixin, UnixStreamBase):
    dalej

@requireAttrs(socket.socket, "sendmsg")
@requireAttrs(socket, "AF_UNIX")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa SendmsgUnixStreamTest(SendmsgStreamTests, SendrecvmsgUnixStreamTestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg")
@requireAttrs(socket, "AF_UNIX")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgUnixStreamTest(RecvmsgTests, RecvmsgGenericStreamTests,
                            SendrecvmsgUnixStreamTestBase):
    dalej

@requireAttrs(socket.socket, "recvmsg_into")
@requireAttrs(socket, "AF_UNIX")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgIntoUnixStreamTest(RecvmsgIntoTests, RecvmsgGenericStreamTests,
                                SendrecvmsgUnixStreamTestBase):
    dalej

@requireAttrs(socket.socket, "sendmsg", "recvmsg")
@requireAttrs(socket, "AF_UNIX", "SOL_SOCKET", "SCM_RIGHTS")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgSCMRightsStreamTest(SCMRightsTest, SendrecvmsgUnixStreamTestBase):
    dalej

@requireAttrs(socket.socket, "sendmsg", "recvmsg_into")
@requireAttrs(socket, "AF_UNIX", "SOL_SOCKET", "SCM_RIGHTS")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa RecvmsgIntoSCMRightsStreamTest(RecvmsgIntoMixin, SCMRightsTest,
                                     SendrecvmsgUnixStreamTestBase):
    dalej


# Test interrupting the interruptible send/receive methods przy a
# signal when a timeout jest set.  These tests avoid having multiple
# threads alive during the test so that the OS cannot deliver the
# signal to the wrong one.

klasa InterruptedTimeoutBase(unittest.TestCase):
    # Base klasa dla interrupted send/receive tests.  Installs an
    # empty handler dla SIGALRM oraz removes it on teardown, along with
    # any scheduled alarms.

    def setUp(self):
        super().setUp()
        orig_alrm_handler = signal.signal(signal.SIGALRM,
                                          lambda signum, frame: 1 / 0)
        self.addCleanup(signal.signal, signal.SIGALRM, orig_alrm_handler)
        self.addCleanup(self.setAlarm, 0)

    # Timeout dla socket operations
    timeout = 4.0

    # Provide setAlarm() method to schedule delivery of SIGALRM after
    # given number of seconds, albo cancel it jeżeli zero, oraz an
    # appropriate time value to use.  Use setitimer() jeżeli available.
    jeżeli hasattr(signal, "setitimer"):
        alarm_time = 0.05

        def setAlarm(self, seconds):
            signal.setitimer(signal.ITIMER_REAL, seconds)
    inaczej:
        # Old systems may deliver the alarm up to one second early
        alarm_time = 2

        def setAlarm(self, seconds):
            signal.alarm(seconds)


# Require siginterrupt() w order to ensure that system calls are
# interrupted by default.
@requireAttrs(signal, "siginterrupt")
@unittest.skipUnless(hasattr(signal, "alarm") albo hasattr(signal, "setitimer"),
                     "Don't have signal.alarm albo signal.setitimer")
klasa InterruptedRecvTimeoutTest(InterruptedTimeoutBase, UDPTestBase):
    # Test interrupting the recv*() methods przy signals when a
    # timeout jest set.

    def setUp(self):
        super().setUp()
        self.serv.settimeout(self.timeout)

    def checkInterruptedRecv(self, func, *args, **kwargs):
        # Check that func(*args, **kwargs) podnieśs
        # errno of EINTR when interrupted by a signal.
        self.setAlarm(self.alarm_time)
        przy self.assertRaises(ZeroDivisionError) jako cm:
            func(*args, **kwargs)

    def testInterruptedRecvTimeout(self):
        self.checkInterruptedRecv(self.serv.recv, 1024)

    def testInterruptedRecvIntoTimeout(self):
        self.checkInterruptedRecv(self.serv.recv_into, bytearray(1024))

    def testInterruptedRecvfromTimeout(self):
        self.checkInterruptedRecv(self.serv.recvfrom, 1024)

    def testInterruptedRecvfromIntoTimeout(self):
        self.checkInterruptedRecv(self.serv.recvfrom_into, bytearray(1024))

    @requireAttrs(socket.socket, "recvmsg")
    def testInterruptedRecvmsgTimeout(self):
        self.checkInterruptedRecv(self.serv.recvmsg, 1024)

    @requireAttrs(socket.socket, "recvmsg_into")
    def testInterruptedRecvmsgIntoTimeout(self):
        self.checkInterruptedRecv(self.serv.recvmsg_into, [bytearray(1024)])


# Require siginterrupt() w order to ensure that system calls are
# interrupted by default.
@requireAttrs(signal, "siginterrupt")
@unittest.skipUnless(hasattr(signal, "alarm") albo hasattr(signal, "setitimer"),
                     "Don't have signal.alarm albo signal.setitimer")
@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa InterruptedSendTimeoutTest(InterruptedTimeoutBase,
                                 ThreadSafeCleanupTestCase,
                                 SocketListeningTestMixin, TCPTestBase):
    # Test interrupting the interruptible send*() methods przy signals
    # when a timeout jest set.

    def setUp(self):
        super().setUp()
        self.serv_conn = self.newSocket()
        self.addCleanup(self.serv_conn.close)
        # Use a thread to complete the connection, but wait dla it to
        # terminate before running the test, so that there jest only one
        # thread to accept the signal.
        cli_thread = threading.Thread(target=self.doConnect)
        cli_thread.start()
        self.cli_conn, addr = self.serv.accept()
        self.addCleanup(self.cli_conn.close)
        cli_thread.join()
        self.serv_conn.settimeout(self.timeout)

    def doConnect(self):
        self.serv_conn.connect(self.serv_addr)

    def checkInterruptedSend(self, func, *args, **kwargs):
        # Check that func(*args, **kwargs), run w a loop, podnieśs
        # OSError przy an errno of EINTR when interrupted by a
        # signal.
        przy self.assertRaises(ZeroDivisionError) jako cm:
            dopóki Prawda:
                self.setAlarm(self.alarm_time)
                func(*args, **kwargs)

    # Issue #12958: The following tests have problems on OS X prior to 10.7
    @support.requires_mac_ver(10, 7)
    def testInterruptedSendTimeout(self):
        self.checkInterruptedSend(self.serv_conn.send, b"a"*512)

    @support.requires_mac_ver(10, 7)
    def testInterruptedSendtoTimeout(self):
        # Passing an actual address here jako Python's wrapper for
        # sendto() doesn't allow dalejing a zero-length one; POSIX
        # requires that the address jest ignored since the socket jest
        # connection-mode, however.
        self.checkInterruptedSend(self.serv_conn.sendto, b"a"*512,
                                  self.serv_addr)

    @support.requires_mac_ver(10, 7)
    @requireAttrs(socket.socket, "sendmsg")
    def testInterruptedSendmsgTimeout(self):
        self.checkInterruptedSend(self.serv_conn.sendmsg, [b"a"*512])


@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa TCPCloserTest(ThreadedTCPSocketTest):

    def testClose(self):
        conn, addr = self.serv.accept()
        conn.close()

        sd = self.cli
        read, write, err = select.select([sd], [], [], 1.0)
        self.assertEqual(read, [sd])
        self.assertEqual(sd.recv(1), b'')

        # Calling close() many times should be safe.
        conn.close()
        conn.close()

    def _testClose(self):
        self.cli.connect((HOST, self.port))
        time.sleep(1.0)

@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa BasicSocketPairTest(SocketPairTest):

    def __init__(self, methodName='runTest'):
        SocketPairTest.__init__(self, methodName=methodName)

    def _check_defaults(self, sock):
        self.assertIsInstance(sock, socket.socket)
        jeżeli hasattr(socket, 'AF_UNIX'):
            self.assertEqual(sock.family, socket.AF_UNIX)
        inaczej:
            self.assertEqual(sock.family, socket.AF_INET)
        self.assertEqual(sock.type, socket.SOCK_STREAM)
        self.assertEqual(sock.proto, 0)

    def _testDefaults(self):
        self._check_defaults(self.cli)

    def testDefaults(self):
        self._check_defaults(self.serv)

    def testRecv(self):
        msg = self.serv.recv(1024)
        self.assertEqual(msg, MSG)

    def _testRecv(self):
        self.cli.send(MSG)

    def testSend(self):
        self.serv.send(MSG)

    def _testSend(self):
        msg = self.cli.recv(1024)
        self.assertEqual(msg, MSG)

@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa NonBlockingTCPTests(ThreadedTCPSocketTest):

    def __init__(self, methodName='runTest'):
        ThreadedTCPSocketTest.__init__(self, methodName=methodName)

    def testSetBlocking(self):
        # Testing whether set blocking works
        self.serv.setblocking(Prawda)
        self.assertIsNic(self.serv.gettimeout())
        self.serv.setblocking(Nieprawda)
        self.assertEqual(self.serv.gettimeout(), 0.0)
        start = time.time()
        spróbuj:
            self.serv.accept()
        wyjąwszy OSError:
            dalej
        end = time.time()
        self.assertPrawda((end - start) < 1.0, "Error setting non-blocking mode.")

    def _testSetBlocking(self):
        dalej

    @support.cpython_only
    def testSetBlocking_overflow(self):
        # Issue 15989
        zaimportuj _testcapi
        jeżeli _testcapi.UINT_MAX >= _testcapi.ULONG_MAX:
            self.skipTest('needs UINT_MAX < ULONG_MAX')
        self.serv.setblocking(Nieprawda)
        self.assertEqual(self.serv.gettimeout(), 0.0)
        self.serv.setblocking(_testcapi.UINT_MAX + 1)
        self.assertIsNic(self.serv.gettimeout())

    _testSetBlocking_overflow = support.cpython_only(_testSetBlocking)

    @unittest.skipUnless(hasattr(socket, 'SOCK_NONBLOCK'),
                         'test needs socket.SOCK_NONBLOCK')
    @support.requires_linux_version(2, 6, 28)
    def testInitNonBlocking(self):
        # reinit server socket
        self.serv.close()
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM |
                                                  socket.SOCK_NONBLOCK)
        self.port = support.bind_port(self.serv)
        self.serv.listen()
        # actual testing
        start = time.time()
        spróbuj:
            self.serv.accept()
        wyjąwszy OSError:
            dalej
        end = time.time()
        self.assertPrawda((end - start) < 1.0, "Error creating przy non-blocking mode.")

    def _testInitNonBlocking(self):
        dalej

    def testInheritFlags(self):
        # Issue #7995: when calling accept() on a listening socket przy a
        # timeout, the resulting socket should nie be non-blocking.
        self.serv.settimeout(10)
        spróbuj:
            conn, addr = self.serv.accept()
            message = conn.recv(len(MSG))
        w_końcu:
            conn.close()
            self.serv.settimeout(Nic)

    def _testInheritFlags(self):
        time.sleep(0.1)
        self.cli.connect((HOST, self.port))
        time.sleep(0.5)
        self.cli.send(MSG)

    def testAccept(self):
        # Testing non-blocking accept
        self.serv.setblocking(0)
        spróbuj:
            conn, addr = self.serv.accept()
        wyjąwszy OSError:
            dalej
        inaczej:
            self.fail("Error trying to do non-blocking accept.")
        read, write, err = select.select([self.serv], [], [])
        jeżeli self.serv w read:
            conn, addr = self.serv.accept()
            conn.close()
        inaczej:
            self.fail("Error trying to do accept after select.")

    def _testAccept(self):
        time.sleep(0.1)
        self.cli.connect((HOST, self.port))

    def testConnect(self):
        # Testing non-blocking connect
        conn, addr = self.serv.accept()
        conn.close()

    def _testConnect(self):
        self.cli.settimeout(10)
        self.cli.connect((HOST, self.port))

    def testRecv(self):
        # Testing non-blocking recv
        conn, addr = self.serv.accept()
        conn.setblocking(0)
        spróbuj:
            msg = conn.recv(len(MSG))
        wyjąwszy OSError:
            dalej
        inaczej:
            self.fail("Error trying to do non-blocking recv.")
        read, write, err = select.select([conn], [], [])
        jeżeli conn w read:
            msg = conn.recv(len(MSG))
            conn.close()
            self.assertEqual(msg, MSG)
        inaczej:
            self.fail("Error during select call to non-blocking socket.")

    def _testRecv(self):
        self.cli.connect((HOST, self.port))
        time.sleep(0.1)
        self.cli.send(MSG)

@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa FileObjectClassTestCase(SocketConnectedTest):
    """Unit tests dla the object returned by socket.makefile()

    self.read_file jest the io object returned by makefile() on
    the client connection.  You can read z this file to
    get output z the server.

    self.write_file jest the io object returned by makefile() on the
    server connection.  You can write to this file to send output
    to the client.
    """

    bufsize = -1 # Use default buffer size
    encoding = 'utf-8'
    errors = 'strict'
    newline = Nic

    read_mode = 'rb'
    read_msg = MSG
    write_mode = 'wb'
    write_msg = MSG

    def __init__(self, methodName='runTest'):
        SocketConnectedTest.__init__(self, methodName=methodName)

    def setUp(self):
        self.evt1, self.evt2, self.serv_finished, self.cli_finished = [
            threading.Event() dla i w range(4)]
        SocketConnectedTest.setUp(self)
        self.read_file = self.cli_conn.makefile(
            self.read_mode, self.bufsize,
            encoding = self.encoding,
            errors = self.errors,
            newline = self.newline)

    def tearDown(self):
        self.serv_finished.set()
        self.read_file.close()
        self.assertPrawda(self.read_file.closed)
        self.read_file = Nic
        SocketConnectedTest.tearDown(self)

    def clientSetUp(self):
        SocketConnectedTest.clientSetUp(self)
        self.write_file = self.serv_conn.makefile(
            self.write_mode, self.bufsize,
            encoding = self.encoding,
            errors = self.errors,
            newline = self.newline)

    def clientTearDown(self):
        self.cli_finished.set()
        self.write_file.close()
        self.assertPrawda(self.write_file.closed)
        self.write_file = Nic
        SocketConnectedTest.clientTearDown(self)

    def testReadAfterTimeout(self):
        # Issue #7322: A file object must disallow further reads
        # after a timeout has occurred.
        self.cli_conn.settimeout(1)
        self.read_file.read(3)
        # First read podnieśs a timeout
        self.assertRaises(socket.timeout, self.read_file.read, 1)
        # Second read jest disallowed
        przy self.assertRaises(OSError) jako ctx:
            self.read_file.read(1)
        self.assertIn("cannot read z timed out object", str(ctx.exception))

    def _testReadAfterTimeout(self):
        self.write_file.write(self.write_msg[0:3])
        self.write_file.flush()
        self.serv_finished.wait()

    def testSmallRead(self):
        # Performing small file read test
        first_seg = self.read_file.read(len(self.read_msg)-3)
        second_seg = self.read_file.read(3)
        msg = first_seg + second_seg
        self.assertEqual(msg, self.read_msg)

    def _testSmallRead(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    def testFullRead(self):
        # read until EOF
        msg = self.read_file.read()
        self.assertEqual(msg, self.read_msg)

    def _testFullRead(self):
        self.write_file.write(self.write_msg)
        self.write_file.close()

    def testUnbufferedRead(self):
        # Performing unbuffered file read test
        buf = type(self.read_msg)()
        dopóki 1:
            char = self.read_file.read(1)
            jeżeli nie char:
                przerwij
            buf += char
        self.assertEqual(buf, self.read_msg)

    def _testUnbufferedRead(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    def testReadline(self):
        # Performing file readline test
        line = self.read_file.readline()
        self.assertEqual(line, self.read_msg)

    def _testReadline(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    def testCloseAfterMakefile(self):
        # The file returned by makefile should keep the socket open.
        self.cli_conn.close()
        # read until EOF
        msg = self.read_file.read()
        self.assertEqual(msg, self.read_msg)

    def _testCloseAfterMakefile(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    def testMakefileAfterMakefileClose(self):
        self.read_file.close()
        msg = self.cli_conn.recv(len(MSG))
        jeżeli isinstance(self.read_msg, str):
            msg = msg.decode()
        self.assertEqual(msg, self.read_msg)

    def _testMakefileAfterMakefileClose(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    def testClosedAttr(self):
        self.assertPrawda(nie self.read_file.closed)

    def _testClosedAttr(self):
        self.assertPrawda(nie self.write_file.closed)

    def testAttributes(self):
        self.assertEqual(self.read_file.mode, self.read_mode)
        self.assertEqual(self.read_file.name, self.cli_conn.fileno())

    def _testAttributes(self):
        self.assertEqual(self.write_file.mode, self.write_mode)
        self.assertEqual(self.write_file.name, self.serv_conn.fileno())

    def testRealClose(self):
        self.read_file.close()
        self.assertRaises(ValueError, self.read_file.fileno)
        self.cli_conn.close()
        self.assertRaises(OSError, self.cli_conn.getsockname)

    def _testRealClose(self):
        dalej


klasa UnbufferedFileObjectClassTestCase(FileObjectClassTestCase):

    """Repeat the tests z FileObjectClassTestCase przy bufsize==0.

    In this case (and w this case only), it should be possible to
    create a file object, read a line z it, create another file
    object, read another line z it, without loss of data w the
    first file object's buffer.  Note that http.client relies on this
    when reading multiple requests z the same socket."""

    bufsize = 0 # Use unbuffered mode

    def testUnbufferedReadline(self):
        # Read a line, create a new file object, read another line przy it
        line = self.read_file.readline() # first line
        self.assertEqual(line, b"A. " + self.write_msg) # first line
        self.read_file = self.cli_conn.makefile('rb', 0)
        line = self.read_file.readline() # second line
        self.assertEqual(line, b"B. " + self.write_msg) # second line

    def _testUnbufferedReadline(self):
        self.write_file.write(b"A. " + self.write_msg)
        self.write_file.write(b"B. " + self.write_msg)
        self.write_file.flush()

    def testMakefileClose(self):
        # The file returned by makefile should keep the socket open...
        self.cli_conn.close()
        msg = self.cli_conn.recv(1024)
        self.assertEqual(msg, self.read_msg)
        # ...until the file jest itself closed
        self.read_file.close()
        self.assertRaises(OSError, self.cli_conn.recv, 1024)

    def _testMakefileClose(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    def testMakefileCloseSocketDestroy(self):
        refcount_before = sys.getrefcount(self.cli_conn)
        self.read_file.close()
        refcount_after = sys.getrefcount(self.cli_conn)
        self.assertEqual(refcount_before - 1, refcount_after)

    def _testMakefileCloseSocketDestroy(self):
        dalej

    # Non-blocking ops
    # NOTE: to set `read_file` jako non-blocking, we must call
    # `cli_conn.setblocking` oraz vice-versa (see setUp / clientSetUp).

    def testSmallReadNonBlocking(self):
        self.cli_conn.setblocking(Nieprawda)
        self.assertEqual(self.read_file.readinto(bytearray(10)), Nic)
        self.assertEqual(self.read_file.read(len(self.read_msg) - 3), Nic)
        self.evt1.set()
        self.evt2.wait(1.0)
        first_seg = self.read_file.read(len(self.read_msg) - 3)
        jeżeli first_seg jest Nic:
            # Data nie arrived (can happen under Windows), wait a bit
            time.sleep(0.5)
            first_seg = self.read_file.read(len(self.read_msg) - 3)
        buf = bytearray(10)
        n = self.read_file.readinto(buf)
        self.assertEqual(n, 3)
        msg = first_seg + buf[:n]
        self.assertEqual(msg, self.read_msg)
        self.assertEqual(self.read_file.readinto(bytearray(16)), Nic)
        self.assertEqual(self.read_file.read(1), Nic)

    def _testSmallReadNonBlocking(self):
        self.evt1.wait(1.0)
        self.write_file.write(self.write_msg)
        self.write_file.flush()
        self.evt2.set()
        # Avoid cloding the socket before the server test has finished,
        # otherwise system recv() will zwróć 0 instead of EWOULDBLOCK.
        self.serv_finished.wait(5.0)

    def testWriteNonBlocking(self):
        self.cli_finished.wait(5.0)
        # The client thread can't skip directly - the SkipTest exception
        # would appear jako a failure.
        jeżeli self.serv_skipped:
            self.skipTest(self.serv_skipped)

    def _testWriteNonBlocking(self):
        self.serv_skipped = Nic
        self.serv_conn.setblocking(Nieprawda)
        # Try to saturate the socket buffer pipe przy repeated large writes.
        BIG = b"x" * support.SOCK_MAX_SIZE
        LIMIT = 10
        # The first write() succeeds since a chunk of data can be buffered
        n = self.write_file.write(BIG)
        self.assertGreater(n, 0)
        dla i w range(LIMIT):
            n = self.write_file.write(BIG)
            jeżeli n jest Nic:
                # Succeeded
                przerwij
            self.assertGreater(n, 0)
        inaczej:
            # Let us know that this test didn't manage to establish
            # the expected conditions. This jest nie a failure w itself but,
            # jeżeli it happens repeatedly, the test should be fixed.
            self.serv_skipped = "failed to saturate the socket buffer"


klasa LineBufferedFileObjectClassTestCase(FileObjectClassTestCase):

    bufsize = 1 # Default-buffered dla reading; line-buffered dla writing


klasa SmallBufferedFileObjectClassTestCase(FileObjectClassTestCase):

    bufsize = 2 # Exercise the buffering code


klasa UnicodeReadFileObjectClassTestCase(FileObjectClassTestCase):
    """Tests dla socket.makefile() w text mode (rather than binary)"""

    read_mode = 'r'
    read_msg = MSG.decode('utf-8')
    write_mode = 'wb'
    write_msg = MSG
    newline = ''


klasa UnicodeWriteFileObjectClassTestCase(FileObjectClassTestCase):
    """Tests dla socket.makefile() w text mode (rather than binary)"""

    read_mode = 'rb'
    read_msg = MSG
    write_mode = 'w'
    write_msg = MSG.decode('utf-8')
    newline = ''


klasa UnicodeReadWriteFileObjectClassTestCase(FileObjectClassTestCase):
    """Tests dla socket.makefile() w text mode (rather than binary)"""

    read_mode = 'r'
    read_msg = MSG.decode('utf-8')
    write_mode = 'w'
    write_msg = MSG.decode('utf-8')
    newline = ''


klasa NetworkConnectionTest(object):
    """Prove network connection."""

    def clientSetUp(self):
        # We're inherited below by BasicTCPTest2, which also inherits
        # BasicTCPTest, which defines self.port referenced below.
        self.cli = socket.create_connection((HOST, self.port))
        self.serv_conn = self.cli

klasa BasicTCPTest2(NetworkConnectionTest, BasicTCPTest):
    """Tests that NetworkConnection does nie przerwij existing TCP functionality.
    """

klasa NetworkConnectionNoServer(unittest.TestCase):

    klasa MockSocket(socket.socket):
        def connect(self, *args):
            podnieś socket.timeout('timed out')

    @contextlib.contextmanager
    def mocked_socket_module(self):
        """Return a socket which times out on connect"""
        old_socket = socket.socket
        socket.socket = self.MockSocket
        spróbuj:
            uzyskaj
        w_końcu:
            socket.socket = old_socket

    def test_connect(self):
        port = support.find_unused_port()
        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(cli.close)
        przy self.assertRaises(OSError) jako cm:
            cli.connect((HOST, port))
        self.assertEqual(cm.exception.errno, errno.ECONNREFUSED)

    def test_create_connection(self):
        # Issue #9792: errors podnieśd by create_connection() should have
        # a proper errno attribute.
        port = support.find_unused_port()
        przy self.assertRaises(OSError) jako cm:
            socket.create_connection((HOST, port))

        # Issue #16257: create_connection() calls getaddrinfo() against
        # 'localhost'.  This may result w an IPV6 addr being returned
        # jako well jako an IPV4 one:
        #   >>> socket.getaddrinfo('localhost', port, 0, SOCK_STREAM)
        #   >>> [(2,  2, 0, '', ('127.0.0.1', 41230)),
        #        (26, 2, 0, '', ('::1', 41230, 0, 0))]
        #
        # create_connection() enumerates through all the addresses returned
        # oraz jeżeli it doesn't successfully bind to any of them, it propagates
        # the last exception it encountered.
        #
        # On Solaris, ENETUNREACH jest returned w this circumstance instead
        # of ECONNREFUSED.  So, jeżeli that errno exists, add it to our list of
        # expected errnos.
        expected_errnos = [ errno.ECONNREFUSED, ]
        jeżeli hasattr(errno, 'ENETUNREACH'):
            expected_errnos.append(errno.ENETUNREACH)

        self.assertIn(cm.exception.errno, expected_errnos)

    def test_create_connection_timeout(self):
        # Issue #9792: create_connection() should nie recast timeout errors
        # jako generic socket errors.
        przy self.mocked_socket_module():
            przy self.assertRaises(socket.timeout):
                socket.create_connection((HOST, 1234))


@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa NetworkConnectionAttributesTest(SocketTCPTest, ThreadableTest):

    def __init__(self, methodName='runTest'):
        SocketTCPTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    def clientSetUp(self):
        self.source_port = support.find_unused_port()

    def clientTearDown(self):
        self.cli.close()
        self.cli = Nic
        ThreadableTest.clientTearDown(self)

    def _justAccept(self):
        conn, addr = self.serv.accept()
        conn.close()

    testFamily = _justAccept
    def _testFamily(self):
        self.cli = socket.create_connection((HOST, self.port), timeout=30)
        self.addCleanup(self.cli.close)
        self.assertEqual(self.cli.family, 2)

    testSourceAddress = _justAccept
    def _testSourceAddress(self):
        self.cli = socket.create_connection((HOST, self.port), timeout=30,
                source_address=('', self.source_port))
        self.addCleanup(self.cli.close)
        self.assertEqual(self.cli.getsockname()[1], self.source_port)
        # The port number being used jest sufficient to show that the bind()
        # call happened.

    testTimeoutDefault = _justAccept
    def _testTimeoutDefault(self):
        # dalejing no explicit timeout uses socket's global default
        self.assertPrawda(socket.getdefaulttimeout() jest Nic)
        socket.setdefaulttimeout(42)
        spróbuj:
            self.cli = socket.create_connection((HOST, self.port))
            self.addCleanup(self.cli.close)
        w_końcu:
            socket.setdefaulttimeout(Nic)
        self.assertEqual(self.cli.gettimeout(), 42)

    testTimeoutNic = _justAccept
    def _testTimeoutNic(self):
        # Nic timeout means the same jako sock.settimeout(Nic)
        self.assertPrawda(socket.getdefaulttimeout() jest Nic)
        socket.setdefaulttimeout(30)
        spróbuj:
            self.cli = socket.create_connection((HOST, self.port), timeout=Nic)
            self.addCleanup(self.cli.close)
        w_końcu:
            socket.setdefaulttimeout(Nic)
        self.assertEqual(self.cli.gettimeout(), Nic)

    testTimeoutValueNamed = _justAccept
    def _testTimeoutValueNamed(self):
        self.cli = socket.create_connection((HOST, self.port), timeout=30)
        self.assertEqual(self.cli.gettimeout(), 30)

    testTimeoutValueNonamed = _justAccept
    def _testTimeoutValueNonamed(self):
        self.cli = socket.create_connection((HOST, self.port), 30)
        self.addCleanup(self.cli.close)
        self.assertEqual(self.cli.gettimeout(), 30)

@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa NetworkConnectionBehaviourTest(SocketTCPTest, ThreadableTest):

    def __init__(self, methodName='runTest'):
        SocketTCPTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    def clientSetUp(self):
        dalej

    def clientTearDown(self):
        self.cli.close()
        self.cli = Nic
        ThreadableTest.clientTearDown(self)

    def testInsideTimeout(self):
        conn, addr = self.serv.accept()
        self.addCleanup(conn.close)
        time.sleep(3)
        conn.send(b"done!")
    testOutsideTimeout = testInsideTimeout

    def _testInsideTimeout(self):
        self.cli = sock = socket.create_connection((HOST, self.port))
        data = sock.recv(5)
        self.assertEqual(data, b"done!")

    def _testOutsideTimeout(self):
        self.cli = sock = socket.create_connection((HOST, self.port), timeout=1)
        self.assertRaises(socket.timeout, lambda: sock.recv(5))


klasa TCPTimeoutTest(SocketTCPTest):

    def testTCPTimeout(self):
        def podnieś_timeout(*args, **kwargs):
            self.serv.settimeout(1.0)
            self.serv.accept()
        self.assertRaises(socket.timeout, podnieś_timeout,
                              "Error generating a timeout exception (TCP)")

    def testTimeoutZero(self):
        ok = Nieprawda
        spróbuj:
            self.serv.settimeout(0.0)
            foo = self.serv.accept()
        wyjąwszy socket.timeout:
            self.fail("caught timeout instead of error (TCP)")
        wyjąwszy OSError:
            ok = Prawda
        wyjąwszy:
            self.fail("caught unexpected exception (TCP)")
        jeżeli nie ok:
            self.fail("accept() returned success when we did nie expect it")

    @unittest.skipUnless(hasattr(signal, 'alarm'),
                         'test needs signal.alarm()')
    def testInterruptedTimeout(self):
        # XXX I don't know how to do this test on MSWindows albo any other
        # plaform that doesn't support signal.alarm() albo os.kill(), though
        # the bug should have existed on all platforms.
        self.serv.settimeout(5.0)   # must be longer than alarm
        klasa Alarm(Exception):
            dalej
        def alarm_handler(signal, frame):
            podnieś Alarm
        old_alarm = signal.signal(signal.SIGALRM, alarm_handler)
        spróbuj:
            signal.alarm(2)    # POSIX allows alarm to be up to 1 second early
            spróbuj:
                foo = self.serv.accept()
            wyjąwszy socket.timeout:
                self.fail("caught timeout instead of Alarm")
            wyjąwszy Alarm:
                dalej
            wyjąwszy:
                self.fail("caught other exception instead of Alarm:"
                          " %s(%s):\n%s" %
                          (sys.exc_info()[:2] + (traceback.format_exc(),)))
            inaczej:
                self.fail("nothing caught")
            w_końcu:
                signal.alarm(0)         # shut off alarm
        wyjąwszy Alarm:
            self.fail("got Alarm w wrong place")
        w_końcu:
            # no alarm can be pending.  Safe to restore old handler.
            signal.signal(signal.SIGALRM, old_alarm)

klasa UDPTimeoutTest(SocketUDPTest):

    def testUDPTimeout(self):
        def podnieś_timeout(*args, **kwargs):
            self.serv.settimeout(1.0)
            self.serv.recv(1024)
        self.assertRaises(socket.timeout, podnieś_timeout,
                              "Error generating a timeout exception (UDP)")

    def testTimeoutZero(self):
        ok = Nieprawda
        spróbuj:
            self.serv.settimeout(0.0)
            foo = self.serv.recv(1024)
        wyjąwszy socket.timeout:
            self.fail("caught timeout instead of error (UDP)")
        wyjąwszy OSError:
            ok = Prawda
        wyjąwszy:
            self.fail("caught unexpected exception (UDP)")
        jeżeli nie ok:
            self.fail("recv() returned success when we did nie expect it")

klasa TestExceptions(unittest.TestCase):

    def testExceptionTree(self):
        self.assertPrawda(issubclass(OSError, Exception))
        self.assertPrawda(issubclass(socket.herror, OSError))
        self.assertPrawda(issubclass(socket.gaierror, OSError))
        self.assertPrawda(issubclass(socket.timeout, OSError))

@unittest.skipUnless(sys.platform == 'linux', 'Linux specific test')
klasa TestLinuxAbstractNamespace(unittest.TestCase):

    UNIX_PATH_MAX = 108

    def testLinuxAbstractNamespace(self):
        address = b"\x00python-test-hello\x00\xff"
        przy socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) jako s1:
            s1.bind(address)
            s1.listen()
            przy socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) jako s2:
                s2.connect(s1.getsockname())
                przy s1.accept()[0] jako s3:
                    self.assertEqual(s1.getsockname(), address)
                    self.assertEqual(s2.getpeername(), address)

    def testMaxName(self):
        address = b"\x00" + b"h" * (self.UNIX_PATH_MAX - 1)
        przy socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) jako s:
            s.bind(address)
            self.assertEqual(s.getsockname(), address)

    def testNameOverflow(self):
        address = "\x00" + "h" * self.UNIX_PATH_MAX
        przy socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) jako s:
            self.assertRaises(OSError, s.bind, address)

    def testStrName(self):
        # Check that an abstract name can be dalejed jako a string.
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        spróbuj:
            s.bind("\x00python\x00test\x00")
            self.assertEqual(s.getsockname(), b"\x00python\x00test\x00")
        w_końcu:
            s.close()

    def testBytearrayName(self):
        # Check that an abstract name can be dalejed jako a bytearray.
        przy socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) jako s:
            s.bind(bytearray(b"\x00python\x00test\x00"))
            self.assertEqual(s.getsockname(), b"\x00python\x00test\x00")

@unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'test needs socket.AF_UNIX')
klasa TestUnixDomain(unittest.TestCase):

    def setUp(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def tearDown(self):
        self.sock.close()

    def encoded(self, path):
        # Return the given path encoded w the file system encoding,
        # albo skip the test jeżeli this jest nie possible.
        spróbuj:
            zwróć os.fsencode(path)
        wyjąwszy UnicodeEncodeError:
            self.skipTest(
                "Pathname {0!a} cannot be represented w file "
                "system encoding {1!r}".format(
                    path, sys.getfilesystemencoding()))

    def bind(self, sock, path):
        # Bind the socket
        spróbuj:
            sock.bind(path)
        wyjąwszy OSError jako e:
            jeżeli str(e) == "AF_UNIX path too long":
                self.skipTest(
                    "Pathname {0!a} jest too long to serve jako a AF_UNIX path"
                    .format(path))
            inaczej:
                podnieś

    def testStrAddr(self):
        # Test binding to oraz retrieving a normal string pathname.
        path = os.path.abspath(support.TESTFN)
        self.bind(self.sock, path)
        self.addCleanup(support.unlink, path)
        self.assertEqual(self.sock.getsockname(), path)

    def testBytesAddr(self):
        # Test binding to a bytes pathname.
        path = os.path.abspath(support.TESTFN)
        self.bind(self.sock, self.encoded(path))
        self.addCleanup(support.unlink, path)
        self.assertEqual(self.sock.getsockname(), path)

    def testSurrogateescapeBind(self):
        # Test binding to a valid non-ASCII pathname, przy the
        # non-ASCII bytes supplied using surrogateescape encoding.
        path = os.path.abspath(support.TESTFN_UNICODE)
        b = self.encoded(path)
        self.bind(self.sock, b.decode("ascii", "surrogateescape"))
        self.addCleanup(support.unlink, path)
        self.assertEqual(self.sock.getsockname(), path)

    def testUnencodableAddr(self):
        # Test binding to a pathname that cannot be encoded w the
        # file system encoding.
        jeżeli support.TESTFN_UNENCODABLE jest Nic:
            self.skipTest("No unencodable filename available")
        path = os.path.abspath(support.TESTFN_UNENCODABLE)
        self.bind(self.sock, path)
        self.addCleanup(support.unlink, path)
        self.assertEqual(self.sock.getsockname(), path)

@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa BufferIOTest(SocketConnectedTest):
    """
    Test the buffer versions of socket.recv() oraz socket.send().
    """
    def __init__(self, methodName='runTest'):
        SocketConnectedTest.__init__(self, methodName=methodName)

    def testRecvIntoArray(self):
        buf = bytearray(1024)
        nbytes = self.cli_conn.recv_into(buf)
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    def _testRecvIntoArray(self):
        buf = bytes(MSG)
        self.serv_conn.send(buf)

    def testRecvIntoBytearray(self):
        buf = bytearray(1024)
        nbytes = self.cli_conn.recv_into(buf)
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    _testRecvIntoBytearray = _testRecvIntoArray

    def testRecvIntoMemoryview(self):
        buf = bytearray(1024)
        nbytes = self.cli_conn.recv_into(memoryview(buf))
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    _testRecvIntoMemoryview = _testRecvIntoArray

    def testRecvFromIntoArray(self):
        buf = bytearray(1024)
        nbytes, addr = self.cli_conn.recvfrom_into(buf)
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    def _testRecvFromIntoArray(self):
        buf = bytes(MSG)
        self.serv_conn.send(buf)

    def testRecvFromIntoBytearray(self):
        buf = bytearray(1024)
        nbytes, addr = self.cli_conn.recvfrom_into(buf)
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    _testRecvFromIntoBytearray = _testRecvFromIntoArray

    def testRecvFromIntoMemoryview(self):
        buf = bytearray(1024)
        nbytes, addr = self.cli_conn.recvfrom_into(memoryview(buf))
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    _testRecvFromIntoMemoryview = _testRecvFromIntoArray

    def testRecvFromIntoSmallBuffer(self):
        # See issue #20246.
        buf = bytearray(8)
        self.assertRaises(ValueError, self.cli_conn.recvfrom_into, buf, 1024)

    def _testRecvFromIntoSmallBuffer(self):
        self.serv_conn.send(MSG)

    def testRecvFromIntoEmptyBuffer(self):
        buf = bytearray()
        self.cli_conn.recvfrom_into(buf)
        self.cli_conn.recvfrom_into(buf, 0)

    _testRecvFromIntoEmptyBuffer = _testRecvFromIntoArray


TIPC_STYPE = 2000
TIPC_LOWER = 200
TIPC_UPPER = 210

def isTipcAvailable():
    """Check jeżeli the TIPC module jest loaded

    The TIPC module jest nie loaded automatically on Ubuntu oraz probably
    other Linux distros.
    """
    jeżeli nie hasattr(socket, "AF_TIPC"):
        zwróć Nieprawda
    jeżeli nie os.path.isfile("/proc/modules"):
        zwróć Nieprawda
    przy open("/proc/modules") jako f:
        dla line w f:
            jeżeli line.startswith("tipc "):
                zwróć Prawda
    zwróć Nieprawda

@unittest.skipUnless(isTipcAvailable(),
                     "TIPC module jest nie loaded, please 'sudo modprobe tipc'")
klasa TIPCTest(unittest.TestCase):
    def testRDM(self):
        srv = socket.socket(socket.AF_TIPC, socket.SOCK_RDM)
        cli = socket.socket(socket.AF_TIPC, socket.SOCK_RDM)
        self.addCleanup(srv.close)
        self.addCleanup(cli.close)

        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srvaddr = (socket.TIPC_ADDR_NAMESEQ, TIPC_STYPE,
                TIPC_LOWER, TIPC_UPPER)
        srv.bind(srvaddr)

        sendaddr = (socket.TIPC_ADDR_NAME, TIPC_STYPE,
                TIPC_LOWER + int((TIPC_UPPER - TIPC_LOWER) / 2), 0)
        cli.sendto(MSG, sendaddr)

        msg, recvaddr = srv.recvfrom(1024)

        self.assertEqual(cli.getsockname(), recvaddr)
        self.assertEqual(msg, MSG)


@unittest.skipUnless(isTipcAvailable(),
                     "TIPC module jest nie loaded, please 'sudo modprobe tipc'")
klasa TIPCThreadableTest(unittest.TestCase, ThreadableTest):
    def __init__(self, methodName = 'runTest'):
        unittest.TestCase.__init__(self, methodName = methodName)
        ThreadableTest.__init__(self)

    def setUp(self):
        self.srv = socket.socket(socket.AF_TIPC, socket.SOCK_STREAM)
        self.addCleanup(self.srv.close)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srvaddr = (socket.TIPC_ADDR_NAMESEQ, TIPC_STYPE,
                TIPC_LOWER, TIPC_UPPER)
        self.srv.bind(srvaddr)
        self.srv.listen()
        self.serverExplicitReady()
        self.conn, self.connaddr = self.srv.accept()
        self.addCleanup(self.conn.close)

    def clientSetUp(self):
        # The jest a hittable race between serverExplicitReady() oraz the
        # accept() call; sleep a little dopóki to avoid it, otherwise
        # we could get an exception
        time.sleep(0.1)
        self.cli = socket.socket(socket.AF_TIPC, socket.SOCK_STREAM)
        self.addCleanup(self.cli.close)
        addr = (socket.TIPC_ADDR_NAME, TIPC_STYPE,
                TIPC_LOWER + int((TIPC_UPPER - TIPC_LOWER) / 2), 0)
        self.cli.connect(addr)
        self.cliaddr = self.cli.getsockname()

    def testStream(self):
        msg = self.conn.recv(1024)
        self.assertEqual(msg, MSG)
        self.assertEqual(self.cliaddr, self.connaddr)

    def _testStream(self):
        self.cli.send(MSG)
        self.cli.close()


@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa ContextManagersTest(ThreadedTCPSocketTest):

    def _testSocketClass(self):
        # base test
        przy socket.socket() jako sock:
            self.assertNieprawda(sock._closed)
        self.assertPrawda(sock._closed)
        # close inside przy block
        przy socket.socket() jako sock:
            sock.close()
        self.assertPrawda(sock._closed)
        # exception inside przy block
        przy socket.socket() jako sock:
            self.assertRaises(OSError, sock.sendall, b'foo')
        self.assertPrawda(sock._closed)

    def testCreateConnectionBase(self):
        conn, addr = self.serv.accept()
        self.addCleanup(conn.close)
        data = conn.recv(1024)
        conn.sendall(data)

    def _testCreateConnectionBase(self):
        address = self.serv.getsockname()
        przy socket.create_connection(address) jako sock:
            self.assertNieprawda(sock._closed)
            sock.sendall(b'foo')
            self.assertEqual(sock.recv(1024), b'foo')
        self.assertPrawda(sock._closed)

    def testCreateConnectionClose(self):
        conn, addr = self.serv.accept()
        self.addCleanup(conn.close)
        data = conn.recv(1024)
        conn.sendall(data)

    def _testCreateConnectionClose(self):
        address = self.serv.getsockname()
        przy socket.create_connection(address) jako sock:
            sock.close()
        self.assertPrawda(sock._closed)
        self.assertRaises(OSError, sock.sendall, b'foo')


klasa InheritanceTest(unittest.TestCase):
    @unittest.skipUnless(hasattr(socket, "SOCK_CLOEXEC"),
                         "SOCK_CLOEXEC nie defined")
    @support.requires_linux_version(2, 6, 28)
    def test_SOCK_CLOEXEC(self):
        przy socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM | socket.SOCK_CLOEXEC) jako s:
            self.assertPrawda(s.type & socket.SOCK_CLOEXEC)
            self.assertNieprawda(s.get_inheritable())

    def test_default_inheritable(self):
        sock = socket.socket()
        przy sock:
            self.assertEqual(sock.get_inheritable(), Nieprawda)

    def test_dup(self):
        sock = socket.socket()
        przy sock:
            newsock = sock.dup()
            sock.close()
            przy newsock:
                self.assertEqual(newsock.get_inheritable(), Nieprawda)

    def test_set_inheritable(self):
        sock = socket.socket()
        przy sock:
            sock.set_inheritable(Prawda)
            self.assertEqual(sock.get_inheritable(), Prawda)

            sock.set_inheritable(Nieprawda)
            self.assertEqual(sock.get_inheritable(), Nieprawda)

    @unittest.skipIf(fcntl jest Nic, "need fcntl")
    def test_get_inheritable_cloexec(self):
        sock = socket.socket()
        przy sock:
            fd = sock.fileno()
            self.assertEqual(sock.get_inheritable(), Nieprawda)

            # clear FD_CLOEXEC flag
            flags = fcntl.fcntl(fd, fcntl.F_GETFD)
            flags &= ~fcntl.FD_CLOEXEC
            fcntl.fcntl(fd, fcntl.F_SETFD, flags)

            self.assertEqual(sock.get_inheritable(), Prawda)

    @unittest.skipIf(fcntl jest Nic, "need fcntl")
    def test_set_inheritable_cloexec(self):
        sock = socket.socket()
        przy sock:
            fd = sock.fileno()
            self.assertEqual(fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC,
                             fcntl.FD_CLOEXEC)

            sock.set_inheritable(Prawda)
            self.assertEqual(fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC,
                             0)


    @unittest.skipUnless(hasattr(socket, "socketpair"),
                         "need socket.socketpair()")
    def test_socketpair(self):
        s1, s2 = socket.socketpair()
        self.addCleanup(s1.close)
        self.addCleanup(s2.close)
        self.assertEqual(s1.get_inheritable(), Nieprawda)
        self.assertEqual(s2.get_inheritable(), Nieprawda)


@unittest.skipUnless(hasattr(socket, "SOCK_NONBLOCK"),
                     "SOCK_NONBLOCK nie defined")
klasa NonblockConstantTest(unittest.TestCase):
    def checkNonblock(self, s, nonblock=Prawda, timeout=0.0):
        jeżeli nonblock:
            self.assertPrawda(s.type & socket.SOCK_NONBLOCK)
            self.assertEqual(s.gettimeout(), timeout)
        inaczej:
            self.assertNieprawda(s.type & socket.SOCK_NONBLOCK)
            self.assertEqual(s.gettimeout(), Nic)

    @support.requires_linux_version(2, 6, 28)
    def test_SOCK_NONBLOCK(self):
        # a lot of it seems silly oraz redundant, but I wanted to test that
        # changing back oraz forth worked ok
        przy socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM | socket.SOCK_NONBLOCK) jako s:
            self.checkNonblock(s)
            s.setblocking(1)
            self.checkNonblock(s, Nieprawda)
            s.setblocking(0)
            self.checkNonblock(s)
            s.settimeout(Nic)
            self.checkNonblock(s, Nieprawda)
            s.settimeout(2.0)
            self.checkNonblock(s, timeout=2.0)
            s.setblocking(1)
            self.checkNonblock(s, Nieprawda)
        # defaulttimeout
        t = socket.getdefaulttimeout()
        socket.setdefaulttimeout(0.0)
        przy socket.socket() jako s:
            self.checkNonblock(s)
        socket.setdefaulttimeout(Nic)
        przy socket.socket() jako s:
            self.checkNonblock(s, Nieprawda)
        socket.setdefaulttimeout(2.0)
        przy socket.socket() jako s:
            self.checkNonblock(s, timeout=2.0)
        socket.setdefaulttimeout(Nic)
        przy socket.socket() jako s:
            self.checkNonblock(s, Nieprawda)
        socket.setdefaulttimeout(t)


@unittest.skipUnless(os.name == "nt", "Windows specific")
@unittest.skipUnless(multiprocessing, "need multiprocessing")
klasa TestSocketSharing(SocketTCPTest):
    # This must be classmethod oraz nie staticmethod albo multiprocessing
    # won't be able to bootstrap it.
    @classmethod
    def remoteProcessServer(cls, q):
        # Recreate socket z shared data
        sdata = q.get()
        message = q.get()

        s = socket.fromshare(sdata)
        s2, c = s.accept()

        # Send the message
        s2.sendall(message)
        s2.close()
        s.close()

    def testShare(self):
        # Transfer the listening server socket to another process
        # oraz service it z there.

        # Create process:
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=self.remoteProcessServer, args=(q,))
        p.start()

        # Get the shared socket data
        data = self.serv.share(p.pid)

        # Pass the shared socket to the other process
        addr = self.serv.getsockname()
        self.serv.close()
        q.put(data)

        # The data that the server will send us
        message = b"slapmahfro"
        q.put(message)

        # Connect
        s = socket.create_connection(addr)
        #  listen dla the data
        m = []
        dopóki Prawda:
            data = s.recv(100)
            jeżeli nie data:
                przerwij
            m.append(data)
        s.close()
        received = b"".join(m)
        self.assertEqual(received, message)
        p.join()

    def testShareLength(self):
        data = self.serv.share(os.getpid())
        self.assertRaises(ValueError, socket.fromshare, data[:-1])
        self.assertRaises(ValueError, socket.fromshare, data+b"foo")

    def compareSockets(self, org, other):
        # socket sharing jest expected to work only dla blocking socket
        # since the internal python timout value isn't transfered.
        self.assertEqual(org.gettimeout(), Nic)
        self.assertEqual(org.gettimeout(), other.gettimeout())

        self.assertEqual(org.family, other.family)
        self.assertEqual(org.type, other.type)
        # If the user specified "0" dla proto, then
        # internally windows will have picked the correct value.
        # Python introspection on the socket however will still zwróć
        # 0.  For the shared socket, the python value jest recreated
        # z the actual value, so it may nie compare correctly.
        jeżeli org.proto != 0:
            self.assertEqual(org.proto, other.proto)

    def testShareLocal(self):
        data = self.serv.share(os.getpid())
        s = socket.fromshare(data)
        spróbuj:
            self.compareSockets(self.serv, s)
        w_końcu:
            s.close()

    def testTypes(self):
        families = [socket.AF_INET, socket.AF_INET6]
        types = [socket.SOCK_STREAM, socket.SOCK_DGRAM]
        dla f w families:
            dla t w types:
                spróbuj:
                    source = socket.socket(f, t)
                wyjąwszy OSError:
                    continue # This combination jest nie supported
                spróbuj:
                    data = source.share(os.getpid())
                    shared = socket.fromshare(data)
                    spróbuj:
                        self.compareSockets(source, shared)
                    w_końcu:
                        shared.close()
                w_końcu:
                    source.close()


@unittest.skipUnless(thread, 'Threading required dla this test.')
klasa SendfileUsingSendTest(ThreadedTCPSocketTest):
    """
    Test the send() implementation of socket.sendfile().
    """

    FILESIZE = (10 * 1024 * 1024)  # 10MB
    BUFSIZE = 8192
    FILEDATA = b""
    TIMEOUT = 2

    @classmethod
    def setUpClass(cls):
        def chunks(total, step):
            assert total >= step
            dopóki total > step:
                uzyskaj step
                total -= step
            jeżeli total:
                uzyskaj total

        chunk = b"".join([random.choice(string.ascii_letters).encode()
                          dla i w range(cls.BUFSIZE)])
        przy open(support.TESTFN, 'wb') jako f:
            dla csize w chunks(cls.FILESIZE, cls.BUFSIZE):
                f.write(chunk)
        przy open(support.TESTFN, 'rb') jako f:
            cls.FILEDATA = f.read()
            assert len(cls.FILEDATA) == cls.FILESIZE

    @classmethod
    def tearDownClass(cls):
        support.unlink(support.TESTFN)

    def accept_conn(self):
        self.serv.settimeout(self.TIMEOUT)
        conn, addr = self.serv.accept()
        conn.settimeout(self.TIMEOUT)
        self.addCleanup(conn.close)
        zwróć conn

    def recv_data(self, conn):
        received = []
        dopóki Prawda:
            chunk = conn.recv(self.BUFSIZE)
            jeżeli nie chunk:
                przerwij
            received.append(chunk)
        zwróć b''.join(received)

    def meth_from_sock(self, sock):
        # Depending on the mixin klasa being run zwróć either send()
        # albo sendfile() method implementation.
        zwróć getattr(sock, "_sendfile_use_send")

    # regular file

    def _testRegularFile(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        przy socket.create_connection(address) jako sock, file jako file:
            meth = self.meth_from_sock(sock)
            sent = meth(file)
            self.assertEqual(sent, self.FILESIZE)
            self.assertEqual(file.tell(), self.FILESIZE)

    def testRegularFile(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), self.FILESIZE)
        self.assertEqual(data, self.FILEDATA)

    # non regular file

    def _testNonRegularFile(self):
        address = self.serv.getsockname()
        file = io.BytesIO(self.FILEDATA)
        przy socket.create_connection(address) jako sock, file jako file:
            sent = sock.sendfile(file)
            self.assertEqual(sent, self.FILESIZE)
            self.assertEqual(file.tell(), self.FILESIZE)
            self.assertRaises(socket._GiveupOnSendfile,
                              sock._sendfile_use_sendfile, file)

    def testNonRegularFile(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), self.FILESIZE)
        self.assertEqual(data, self.FILEDATA)

    # empty file

    def _testEmptyFileSend(self):
        address = self.serv.getsockname()
        filename = support.TESTFN + "2"
        przy open(filename, 'wb'):
            self.addCleanup(support.unlink, filename)
        file = open(filename, 'rb')
        przy socket.create_connection(address) jako sock, file jako file:
            meth = self.meth_from_sock(sock)
            sent = meth(file)
            self.assertEqual(sent, 0)
            self.assertEqual(file.tell(), 0)

    def testEmptyFileSend(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(data, b"")

    # offset

    def _testOffset(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        przy socket.create_connection(address) jako sock, file jako file:
            meth = self.meth_from_sock(sock)
            sent = meth(file, offset=5000)
            self.assertEqual(sent, self.FILESIZE - 5000)
            self.assertEqual(file.tell(), self.FILESIZE)

    def testOffset(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), self.FILESIZE - 5000)
        self.assertEqual(data, self.FILEDATA[5000:])

    # count

    def _testCount(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        przy socket.create_connection(address, timeout=2) jako sock, file jako file:
            count = 5000007
            meth = self.meth_from_sock(sock)
            sent = meth(file, count=count)
            self.assertEqual(sent, count)
            self.assertEqual(file.tell(), count)

    def testCount(self):
        count = 5000007
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), count)
        self.assertEqual(data, self.FILEDATA[:count])

    # count small

    def _testCountSmall(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        przy socket.create_connection(address, timeout=2) jako sock, file jako file:
            count = 1
            meth = self.meth_from_sock(sock)
            sent = meth(file, count=count)
            self.assertEqual(sent, count)
            self.assertEqual(file.tell(), count)

    def testCountSmall(self):
        count = 1
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), count)
        self.assertEqual(data, self.FILEDATA[:count])

    # count + offset

    def _testCountWithOffset(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        przy socket.create_connection(address, timeout=2) jako sock, file jako file:
            count = 100007
            meth = self.meth_from_sock(sock)
            sent = meth(file, offset=2007, count=count)
            self.assertEqual(sent, count)
            self.assertEqual(file.tell(), count + 2007)

    def testCountWithOffset(self):
        count = 100007
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), count)
        self.assertEqual(data, self.FILEDATA[2007:count+2007])

    # non blocking sockets are nie supposed to work

    def _testNonBlocking(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        przy socket.create_connection(address) jako sock, file jako file:
            sock.setblocking(Nieprawda)
            meth = self.meth_from_sock(sock)
            self.assertRaises(ValueError, meth, file)
            self.assertRaises(ValueError, sock.sendfile, file)

    def testNonBlocking(self):
        conn = self.accept_conn()
        jeżeli conn.recv(8192):
            self.fail('was nie supposed to receive any data')

    # timeout (non-triggered)

    def _testWithTimeout(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        przy socket.create_connection(address, timeout=2) jako sock, file jako file:
            meth = self.meth_from_sock(sock)
            sent = meth(file)
            self.assertEqual(sent, self.FILESIZE)

    def testWithTimeout(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), self.FILESIZE)
        self.assertEqual(data, self.FILEDATA)

    # timeout (triggered)

    def _testWithTimeoutTriggeredSend(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        przy socket.create_connection(address, timeout=0.01) jako sock, \
                file jako file:
            meth = self.meth_from_sock(sock)
            self.assertRaises(socket.timeout, meth, file)

    def testWithTimeoutTriggeredSend(self):
        conn = self.accept_conn()
        conn.recv(88192)

    # errors

    def _test_errors(self):
        dalej

    def test_errors(self):
        przy open(support.TESTFN, 'rb') jako file:
            przy socket.socket(type=socket.SOCK_DGRAM) jako s:
                meth = self.meth_from_sock(s)
                self.assertRaisesRegex(
                    ValueError, "SOCK_STREAM", meth, file)
        przy open(support.TESTFN, 'rt') jako file:
            przy socket.socket() jako s:
                meth = self.meth_from_sock(s)
                self.assertRaisesRegex(
                    ValueError, "binary mode", meth, file)
        przy open(support.TESTFN, 'rb') jako file:
            przy socket.socket() jako s:
                meth = self.meth_from_sock(s)
                self.assertRaisesRegex(TypeError, "positive integer",
                                       meth, file, count='2')
                self.assertRaisesRegex(TypeError, "positive integer",
                                       meth, file, count=0.1)
                self.assertRaisesRegex(ValueError, "positive integer",
                                       meth, file, count=0)
                self.assertRaisesRegex(ValueError, "positive integer",
                                       meth, file, count=-1)


@unittest.skipUnless(thread, 'Threading required dla this test.')
@unittest.skipUnless(hasattr(os, "sendfile"),
                     'os.sendfile() required dla this test.')
klasa SendfileUsingSendfileTest(SendfileUsingSendTest):
    """
    Test the sendfile() implementation of socket.sendfile().
    """
    def meth_from_sock(self, sock):
        zwróć getattr(sock, "_sendfile_use_sendfile")


def test_main():
    tests = [GeneralModuleTests, BasicTCPTest, TCPCloserTest, TCPTimeoutTest,
             TestExceptions, BufferIOTest, BasicTCPTest2, BasicUDPTest, UDPTimeoutTest ]

    tests.extend([
        NonBlockingTCPTests,
        FileObjectClassTestCase,
        UnbufferedFileObjectClassTestCase,
        LineBufferedFileObjectClassTestCase,
        SmallBufferedFileObjectClassTestCase,
        UnicodeReadFileObjectClassTestCase,
        UnicodeWriteFileObjectClassTestCase,
        UnicodeReadWriteFileObjectClassTestCase,
        NetworkConnectionNoServer,
        NetworkConnectionAttributesTest,
        NetworkConnectionBehaviourTest,
        ContextManagersTest,
        InheritanceTest,
        NonblockConstantTest
    ])
    tests.append(BasicSocketPairTest)
    tests.append(TestUnixDomain)
    tests.append(TestLinuxAbstractNamespace)
    tests.extend([TIPCTest, TIPCThreadableTest])
    tests.extend([BasicCANTest, CANTest])
    tests.extend([BasicRDSTest, RDSTest])
    tests.extend([
        CmsgMacroTests,
        SendmsgUDPTest,
        RecvmsgUDPTest,
        RecvmsgIntoUDPTest,
        SendmsgUDP6Test,
        RecvmsgUDP6Test,
        RecvmsgRFC3542AncillaryUDP6Test,
        RecvmsgIntoRFC3542AncillaryUDP6Test,
        RecvmsgIntoUDP6Test,
        SendmsgTCPTest,
        RecvmsgTCPTest,
        RecvmsgIntoTCPTest,
        SendmsgSCTPStreamTest,
        RecvmsgSCTPStreamTest,
        RecvmsgIntoSCTPStreamTest,
        SendmsgUnixStreamTest,
        RecvmsgUnixStreamTest,
        RecvmsgIntoUnixStreamTest,
        RecvmsgSCMRightsStreamTest,
        RecvmsgIntoSCMRightsStreamTest,
        # These are slow when setitimer() jest nie available
        InterruptedRecvTimeoutTest,
        InterruptedSendTimeoutTest,
        TestSocketSharing,
        SendfileUsingSendTest,
        SendfileUsingSendfileTest,
    ])

    thread_info = support.threading_setup()
    support.run_unittest(*tests)
    support.threading_cleanup(*thread_info)

jeżeli __name__ == "__main__":
    test_main()
