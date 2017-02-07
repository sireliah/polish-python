# Copyright (c) 2001-2006 Twisted Matrix Laboratories.
#
# Permission jest hereby granted, free of charge, to any person obtaining
# a copy of this software oraz associated documentation files (the
# "Software"), to deal w the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, oraz to
# permit persons to whom the Software jest furnished to do so, subject to
# the following conditions:
#
# The above copyright notice oraz this permission notice shall be
# included w all copies albo substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
Tests dla epoll wrapper.
"""
zaimportuj errno
zaimportuj os
zaimportuj select
zaimportuj socket
zaimportuj time
zaimportuj unittest

z test zaimportuj support
jeżeli nie hasattr(select, "epoll"):
    podnieś unittest.SkipTest("test works only on Linux 2.6")

spróbuj:
    select.epoll()
wyjąwszy OSError jako e:
    jeżeli e.errno == errno.ENOSYS:
        podnieś unittest.SkipTest("kernel doesn't support epoll()")
    podnieś

klasa TestEPoll(unittest.TestCase):

    def setUp(self):
        self.serverSocket = socket.socket()
        self.serverSocket.bind(('127.0.0.1', 0))
        self.serverSocket.listen()
        self.connections = [self.serverSocket]

    def tearDown(self):
        dla skt w self.connections:
            skt.close()

    def _connected_pair(self):
        client = socket.socket()
        client.setblocking(Nieprawda)
        spróbuj:
            client.connect(('127.0.0.1', self.serverSocket.getsockname()[1]))
        wyjąwszy OSError jako e:
            self.assertEqual(e.args[0], errno.EINPROGRESS)
        inaczej:
            podnieś AssertionError("Connect should have podnieśd EINPROGRESS")
        server, addr = self.serverSocket.accept()

        self.connections.extend((client, server))
        zwróć client, server

    def test_create(self):
        spróbuj:
            ep = select.epoll(16)
        wyjąwszy OSError jako e:
            podnieś AssertionError(str(e))
        self.assertPrawda(ep.fileno() > 0, ep.fileno())
        self.assertPrawda(nie ep.closed)
        ep.close()
        self.assertPrawda(ep.closed)
        self.assertRaises(ValueError, ep.fileno)
        jeżeli hasattr(select, "EPOLL_CLOEXEC"):
            select.epoll(select.EPOLL_CLOEXEC).close()
            self.assertRaises(OSError, select.epoll, flags=12356)

    def test_badcreate(self):
        self.assertRaises(TypeError, select.epoll, 1, 2, 3)
        self.assertRaises(TypeError, select.epoll, 'foo')
        self.assertRaises(TypeError, select.epoll, Nic)
        self.assertRaises(TypeError, select.epoll, ())
        self.assertRaises(TypeError, select.epoll, ['foo'])
        self.assertRaises(TypeError, select.epoll, {})

    def test_context_manager(self):
        przy select.epoll(16) jako ep:
            self.assertGreater(ep.fileno(), 0)
            self.assertNieprawda(ep.closed)
        self.assertPrawda(ep.closed)
        self.assertRaises(ValueError, ep.fileno)

    def test_add(self):
        server, client = self._connected_pair()

        ep = select.epoll(2)
        spróbuj:
            ep.register(server.fileno(), select.EPOLLIN | select.EPOLLOUT)
            ep.register(client.fileno(), select.EPOLLIN | select.EPOLLOUT)
        w_końcu:
            ep.close()

        # adding by object w/ fileno works, too.
        ep = select.epoll(2)
        spróbuj:
            ep.register(server, select.EPOLLIN | select.EPOLLOUT)
            ep.register(client, select.EPOLLIN | select.EPOLLOUT)
        w_końcu:
            ep.close()

        ep = select.epoll(2)
        spróbuj:
            # TypeError: argument must be an int, albo have a fileno() method.
            self.assertRaises(TypeError, ep.register, object(),
                select.EPOLLIN | select.EPOLLOUT)
            self.assertRaises(TypeError, ep.register, Nic,
                select.EPOLLIN | select.EPOLLOUT)
            # ValueError: file descriptor cannot be a negative integer (-1)
            self.assertRaises(ValueError, ep.register, -1,
                select.EPOLLIN | select.EPOLLOUT)
            # OSError: [Errno 9] Bad file descriptor
            self.assertRaises(OSError, ep.register, 10000,
                select.EPOLLIN | select.EPOLLOUT)
            # registering twice also podnieśs an exception
            ep.register(server, select.EPOLLIN | select.EPOLLOUT)
            self.assertRaises(OSError, ep.register, server,
                select.EPOLLIN | select.EPOLLOUT)
        w_końcu:
            ep.close()

    def test_fromfd(self):
        server, client = self._connected_pair()

        ep = select.epoll(2)
        ep2 = select.epoll.fromfd(ep.fileno())

        ep2.register(server.fileno(), select.EPOLLIN | select.EPOLLOUT)
        ep2.register(client.fileno(), select.EPOLLIN | select.EPOLLOUT)

        events = ep.poll(1, 4)
        events2 = ep2.poll(0.9, 4)
        self.assertEqual(len(events), 2)
        self.assertEqual(len(events2), 2)

        ep.close()
        spróbuj:
            ep2.poll(1, 4)
        wyjąwszy OSError jako e:
            self.assertEqual(e.args[0], errno.EBADF, e)
        inaczej:
            self.fail("epoll on closed fd didn't podnieś EBADF")

    def test_control_and_wait(self):
        client, server = self._connected_pair()

        ep = select.epoll(16)
        ep.register(server.fileno(),
                   select.EPOLLIN | select.EPOLLOUT | select.EPOLLET)
        ep.register(client.fileno(),
                   select.EPOLLIN | select.EPOLLOUT | select.EPOLLET)

        now = time.monotonic()
        events = ep.poll(1, 4)
        then = time.monotonic()
        self.assertNieprawda(then - now > 0.1, then - now)

        events.sort()
        expected = [(client.fileno(), select.EPOLLOUT),
                    (server.fileno(), select.EPOLLOUT)]
        expected.sort()

        self.assertEqual(events, expected)

        events = ep.poll(timeout=2.1, maxevents=4)
        self.assertNieprawda(events)

        client.send(b"Hello!")
        server.send(b"world!!!")

        now = time.monotonic()
        events = ep.poll(1, 4)
        then = time.monotonic()
        self.assertNieprawda(then - now > 0.01)

        events.sort()
        expected = [(client.fileno(), select.EPOLLIN | select.EPOLLOUT),
                    (server.fileno(), select.EPOLLIN | select.EPOLLOUT)]
        expected.sort()

        self.assertEqual(events, expected)

        ep.unregister(client.fileno())
        ep.modify(server.fileno(), select.EPOLLOUT)
        now = time.monotonic()
        events = ep.poll(1, 4)
        then = time.monotonic()
        self.assertNieprawda(then - now > 0.01)

        expected = [(server.fileno(), select.EPOLLOUT)]
        self.assertEqual(events, expected)

    def test_errors(self):
        self.assertRaises(ValueError, select.epoll, -2)
        self.assertRaises(ValueError, select.epoll().register, -1,
                          select.EPOLLIN)

    def test_unregister_closed(self):
        server, client = self._connected_pair()
        fd = server.fileno()
        ep = select.epoll(16)
        ep.register(server)

        now = time.monotonic()
        events = ep.poll(1, 4)
        then = time.monotonic()
        self.assertNieprawda(then - now > 0.01)

        server.close()
        ep.unregister(fd)

    def test_close(self):
        open_file = open(__file__, "rb")
        self.addCleanup(open_file.close)
        fd = open_file.fileno()
        epoll = select.epoll()

        # test fileno() method oraz closed attribute
        self.assertIsInstance(epoll.fileno(), int)
        self.assertNieprawda(epoll.closed)

        # test close()
        epoll.close()
        self.assertPrawda(epoll.closed)
        self.assertRaises(ValueError, epoll.fileno)

        # close() can be called more than once
        epoll.close()

        # operations must fail przy ValueError("I/O operation on closed ...")
        self.assertRaises(ValueError, epoll.modify, fd, select.EPOLLIN)
        self.assertRaises(ValueError, epoll.poll, 1.0)
        self.assertRaises(ValueError, epoll.register, fd, select.EPOLLIN)
        self.assertRaises(ValueError, epoll.unregister, fd)

    def test_fd_non_inheritable(self):
        epoll = select.epoll()
        self.addCleanup(epoll.close)
        self.assertEqual(os.get_inheritable(epoll.fileno()), Nieprawda)


jeżeli __name__ == "__main__":
    unittest.main()
