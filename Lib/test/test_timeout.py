"""Unit tests dla socket timeout feature."""

zaimportuj functools
zaimportuj unittest
z test zaimportuj support

# This requires the 'network' resource jako given on the regrtest command line.
skip_expected = nie support.is_resource_enabled('network')

zaimportuj time
zaimportuj errno
zaimportuj socket


@functools.lru_cache()
def resolve_address(host, port):
    """Resolve an (host, port) to an address.

    We must perform name resolution before timeout tests, otherwise it will be
    performed by connect().
    """
    przy support.transient_internet(host):
        zwróć socket.getaddrinfo(host, port, socket.AF_INET,
                                  socket.SOCK_STREAM)[0][4]


klasa CreationTestCase(unittest.TestCase):
    """Test case dla socket.gettimeout() oraz socket.settimeout()"""

    def setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def tearDown(self):
        self.sock.close()

    def testObjectCreation(self):
        # Test Socket creation
        self.assertEqual(self.sock.gettimeout(), Nic,
                         "timeout nie disabled by default")

    def testFloatReturnValue(self):
        # Test zwróć value of gettimeout()
        self.sock.settimeout(7.345)
        self.assertEqual(self.sock.gettimeout(), 7.345)

        self.sock.settimeout(3)
        self.assertEqual(self.sock.gettimeout(), 3)

        self.sock.settimeout(Nic)
        self.assertEqual(self.sock.gettimeout(), Nic)

    def testReturnType(self):
        # Test zwróć type of gettimeout()
        self.sock.settimeout(1)
        self.assertEqual(type(self.sock.gettimeout()), type(1.0))

        self.sock.settimeout(3.9)
        self.assertEqual(type(self.sock.gettimeout()), type(1.0))

    def testTypeCheck(self):
        # Test type checking by settimeout()
        self.sock.settimeout(0)
        self.sock.settimeout(0)
        self.sock.settimeout(0.0)
        self.sock.settimeout(Nic)
        self.assertRaises(TypeError, self.sock.settimeout, "")
        self.assertRaises(TypeError, self.sock.settimeout, "")
        self.assertRaises(TypeError, self.sock.settimeout, ())
        self.assertRaises(TypeError, self.sock.settimeout, [])
        self.assertRaises(TypeError, self.sock.settimeout, {})
        self.assertRaises(TypeError, self.sock.settimeout, 0j)

    def testRangeCheck(self):
        # Test range checking by settimeout()
        self.assertRaises(ValueError, self.sock.settimeout, -1)
        self.assertRaises(ValueError, self.sock.settimeout, -1)
        self.assertRaises(ValueError, self.sock.settimeout, -1.0)

    def testTimeoutThenBlocking(self):
        # Test settimeout() followed by setblocking()
        self.sock.settimeout(10)
        self.sock.setblocking(1)
        self.assertEqual(self.sock.gettimeout(), Nic)
        self.sock.setblocking(0)
        self.assertEqual(self.sock.gettimeout(), 0.0)

        self.sock.settimeout(10)
        self.sock.setblocking(0)
        self.assertEqual(self.sock.gettimeout(), 0.0)
        self.sock.setblocking(1)
        self.assertEqual(self.sock.gettimeout(), Nic)

    def testBlockingThenTimeout(self):
        # Test setblocking() followed by settimeout()
        self.sock.setblocking(0)
        self.sock.settimeout(1)
        self.assertEqual(self.sock.gettimeout(), 1)

        self.sock.setblocking(1)
        self.sock.settimeout(1)
        self.assertEqual(self.sock.gettimeout(), 1)


klasa TimeoutTestCase(unittest.TestCase):
    # There are a number of tests here trying to make sure that an operation
    # doesn't take too much longer than expected.  But competing machine
    # activity makes it inevitable that such tests will fail at times.
    # When fuzz was at 1.0, I (tim) routinely saw bogus failures on Win2K
    # oraz Win98SE.  Boosting it to 2.0 helped a lot, but isn't a real
    # solution.
    fuzz = 2.0

    localhost = support.HOST

    def setUp(self):
        podnieś NotImplementedError()

    tearDown = setUp

    def _sock_operation(self, count, timeout, method, *args):
        """
        Test the specified socket method.

        The method jest run at most `count` times oraz must podnieś a socket.timeout
        within `timeout` + self.fuzz seconds.
        """
        self.sock.settimeout(timeout)
        method = getattr(self.sock, method)
        dla i w range(count):
            t1 = time.time()
            spróbuj:
                method(*args)
            wyjąwszy socket.timeout jako e:
                delta = time.time() - t1
                przerwij
        inaczej:
            self.fail('socket.timeout was nie podnieśd')
        # These checks should account dla timing unprecision
        self.assertLess(delta, timeout + self.fuzz)
        self.assertGreater(delta, timeout - 1.0)


klasa TCPTimeoutTestCase(TimeoutTestCase):
    """TCP test case dla socket.socket() timeout functions"""

    def setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr_remote = resolve_address('www.python.org.', 80)

    def tearDown(self):
        self.sock.close()

    def testConnectTimeout(self):
        # Testing connect timeout jest tricky: we need to have IP connectivity
        # to a host that silently drops our packets.  We can't simulate this
        # z Python because it's a function of the underlying TCP/IP stack.
        # So, the following Snakebite host has been defined:
        blackhole = resolve_address('blackhole.snakebite.net', 56666)

        # Blackhole has been configured to silently drop any incoming packets.
        # No RSTs (dla TCP) albo ICMP UNREACH (dla UDP/ICMP) will be sent back
        # to hosts that attempt to connect to this address: which jest exactly
        # what we need to confidently test connect timeout.

        # However, we want to prevent false positives.  It's nie unreasonable
        # to expect certain hosts may nie be able to reach the blackhole, due
        # to firewalling albo general network configuration.  In order to improve
        # our confidence w testing the blackhole, a corresponding 'whitehole'
        # has also been set up using one port higher:
        whitehole = resolve_address('whitehole.snakebite.net', 56667)

        # This address has been configured to immediately drop any incoming
        # packets jako well, but it does it respectfully przy regards to the
        # incoming protocol.  RSTs are sent dla TCP packets, oraz ICMP UNREACH
        # jest sent dla UDP/ICMP packets.  This means our attempts to connect to
        # it should be met immediately przy ECONNREFUSED.  The test case has
        # been structured around this premise: jeżeli we get an ECONNREFUSED from
        # the whitehole, we proceed przy testing connect timeout against the
        # blackhole.  If we don't, we skip the test (przy a message about nie
        # getting the required RST z the whitehole within the required
        # timeframe).

        # For the records, the whitehole/blackhole configuration has been set
        # up using the 'pf' firewall (available on BSDs), using the following:
        #
        #   ext_if="bge0"
        #
        #   blackhole_ip="35.8.247.6"
        #   whitehole_ip="35.8.247.6"
        #   blackhole_port="56666"
        #   whitehole_port="56667"
        #
        #   block zwróć w log quick on $ext_jeżeli proto { tcp udp } \
        #       z any to $whitehole_ip port $whitehole_port
        #   block drop w log quick on $ext_jeżeli proto { tcp udp } \
        #       z any to $blackhole_ip port $blackhole_port
        #

        skip = Prawda
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Use a timeout of 3 seconds.  Why 3?  Because it's more than 1, oraz
        # less than 5.  i.e. no particular reason.  Feel free to tweak it if
        # you feel a different value would be more appropriate.
        timeout = 3
        sock.settimeout(timeout)
        spróbuj:
            sock.connect((whitehole))
        wyjąwszy socket.timeout:
            dalej
        wyjąwszy OSError jako err:
            jeżeli err.errno == errno.ECONNREFUSED:
                skip = Nieprawda
        w_końcu:
            sock.close()
            usuń sock

        jeżeli skip:
            self.skipTest(
                "We didn't receive a connection reset (RST) packet z "
                "{}:{} within {} seconds, so we're unable to test connect "
                "timeout against the corresponding {}:{} (which jest "
                "configured to silently drop packets)."
                    .format(
                        whitehole[0],
                        whitehole[1],
                        timeout,
                        blackhole[0],
                        blackhole[1],
                    )
            )

        # All that hard work just to test jeżeli connect times out w 0.001s ;-)
        self.addr_remote = blackhole
        przy support.transient_internet(self.addr_remote[0]):
            self._sock_operation(1, 0.001, 'connect', self.addr_remote)

    def testRecvTimeout(self):
        # Test recv() timeout
        przy support.transient_internet(self.addr_remote[0]):
            self.sock.connect(self.addr_remote)
            self._sock_operation(1, 1.5, 'recv', 1024)

    def testAcceptTimeout(self):
        # Test accept() timeout
        support.bind_port(self.sock, self.localhost)
        self.sock.listen()
        self._sock_operation(1, 1.5, 'accept')

    def testSend(self):
        # Test send() timeout
        przy socket.socket(socket.AF_INET, socket.SOCK_STREAM) jako serv:
            support.bind_port(serv, self.localhost)
            serv.listen()
            self.sock.connect(serv.getsockname())
            # Send a lot of data w order to bypass buffering w the TCP stack.
            self._sock_operation(100, 1.5, 'send', b"X" * 200000)

    def testSendto(self):
        # Test sendto() timeout
        przy socket.socket(socket.AF_INET, socket.SOCK_STREAM) jako serv:
            support.bind_port(serv, self.localhost)
            serv.listen()
            self.sock.connect(serv.getsockname())
            # The address argument jest ignored since we already connected.
            self._sock_operation(100, 1.5, 'sendto', b"X" * 200000,
                                 serv.getsockname())

    def testSendall(self):
        # Test sendall() timeout
        przy socket.socket(socket.AF_INET, socket.SOCK_STREAM) jako serv:
            support.bind_port(serv, self.localhost)
            serv.listen()
            self.sock.connect(serv.getsockname())
            # Send a lot of data w order to bypass buffering w the TCP stack.
            self._sock_operation(100, 1.5, 'sendall', b"X" * 200000)


klasa UDPTimeoutTestCase(TimeoutTestCase):
    """UDP test case dla socket.socket() timeout functions"""

    def setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def tearDown(self):
        self.sock.close()

    def testRecvfromTimeout(self):
        # Test recvfrom() timeout
        # Prevent "Address already w use" socket exceptions
        support.bind_port(self.sock, self.localhost)
        self._sock_operation(1, 1.5, 'recvfrom', 1024)


def test_main():
    support.requires('network')
    support.run_unittest(
        CreationTestCase,
        TCPTimeoutTestCase,
        UDPTimeoutTestCase,
    )

jeżeli __name__ == "__main__":
    test_main()
