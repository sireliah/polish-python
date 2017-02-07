zaimportuj errno
zaimportuj os
zaimportuj random
zaimportuj selectors
zaimportuj signal
zaimportuj socket
zaimportuj sys
z test zaimportuj support
z time zaimportuj sleep
zaimportuj unittest
zaimportuj unittest.mock
z time zaimportuj monotonic jako time
spróbuj:
    zaimportuj resource
wyjąwszy ImportError:
    resource = Nic


jeżeli hasattr(socket, 'socketpair'):
    socketpair = socket.socketpair
inaczej:
    def socketpair(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
        przy socket.socket(family, type, proto) jako l:
            l.bind((support.HOST, 0))
            l.listen()
            c = socket.socket(family, type, proto)
            spróbuj:
                c.connect(l.getsockname())
                caddr = c.getsockname()
                dopóki Prawda:
                    a, addr = l.accept()
                    # check that we've got the correct client
                    jeżeli addr == caddr:
                        zwróć c, a
                    a.close()
            wyjąwszy OSError:
                c.close()
                podnieś


def find_ready_matching(ready, flag):
    match = []
    dla key, events w ready:
        jeżeli events & flag:
            match.append(key.fileobj)
    zwróć match


klasa BaseSelectorTestCase(unittest.TestCase):

    def make_socketpair(self):
        rd, wr = socketpair()
        self.addCleanup(rd.close)
        self.addCleanup(wr.close)
        zwróć rd, wr

    def test_register(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        key = s.register(rd, selectors.EVENT_READ, "data")
        self.assertIsInstance(key, selectors.SelectorKey)
        self.assertEqual(key.fileobj, rd)
        self.assertEqual(key.fd, rd.fileno())
        self.assertEqual(key.events, selectors.EVENT_READ)
        self.assertEqual(key.data, "data")

        # register an unknown event
        self.assertRaises(ValueError, s.register, 0, 999999)

        # register an invalid FD
        self.assertRaises(ValueError, s.register, -10, selectors.EVENT_READ)

        # register twice
        self.assertRaises(KeyError, s.register, rd, selectors.EVENT_READ)

        # register the same FD, but przy a different object
        self.assertRaises(KeyError, s.register, rd.fileno(),
                          selectors.EVENT_READ)

    def test_unregister(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        s.register(rd, selectors.EVENT_READ)
        s.unregister(rd)

        # unregister an unknown file obj
        self.assertRaises(KeyError, s.unregister, 999999)

        # unregister twice
        self.assertRaises(KeyError, s.unregister, rd)

    def test_unregister_after_fd_close(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)
        rd, wr = self.make_socketpair()
        r, w = rd.fileno(), wr.fileno()
        s.register(r, selectors.EVENT_READ)
        s.register(w, selectors.EVENT_WRITE)
        rd.close()
        wr.close()
        s.unregister(r)
        s.unregister(w)

    @unittest.skipUnless(os.name == 'posix', "requires posix")
    def test_unregister_after_fd_close_and_reuse(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)
        rd, wr = self.make_socketpair()
        r, w = rd.fileno(), wr.fileno()
        s.register(r, selectors.EVENT_READ)
        s.register(w, selectors.EVENT_WRITE)
        rd2, wr2 = self.make_socketpair()
        rd.close()
        wr.close()
        os.dup2(rd2.fileno(), r)
        os.dup2(wr2.fileno(), w)
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        s.unregister(r)
        s.unregister(w)

    def test_unregister_after_socket_close(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)
        rd, wr = self.make_socketpair()
        s.register(rd, selectors.EVENT_READ)
        s.register(wr, selectors.EVENT_WRITE)
        rd.close()
        wr.close()
        s.unregister(rd)
        s.unregister(wr)

    def test_modify(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        key = s.register(rd, selectors.EVENT_READ)

        # modify events
        key2 = s.modify(rd, selectors.EVENT_WRITE)
        self.assertNotEqual(key.events, key2.events)
        self.assertEqual(key2, s.get_key(rd))

        s.unregister(rd)

        # modify data
        d1 = object()
        d2 = object()

        key = s.register(rd, selectors.EVENT_READ, d1)
        key2 = s.modify(rd, selectors.EVENT_READ, d2)
        self.assertEqual(key.events, key2.events)
        self.assertNotEqual(key.data, key2.data)
        self.assertEqual(key2, s.get_key(rd))
        self.assertEqual(key2.data, d2)

        # modify unknown file obj
        self.assertRaises(KeyError, s.modify, 999999, selectors.EVENT_READ)

        # modify use a shortcut
        d3 = object()
        s.register = unittest.mock.Mock()
        s.unregister = unittest.mock.Mock()

        s.modify(rd, selectors.EVENT_READ, d3)
        self.assertNieprawda(s.register.called)
        self.assertNieprawda(s.unregister.called)

    def test_close(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        mapping = s.get_map()
        rd, wr = self.make_socketpair()

        s.register(rd, selectors.EVENT_READ)
        s.register(wr, selectors.EVENT_WRITE)

        s.close()
        self.assertRaises(RuntimeError, s.get_key, rd)
        self.assertRaises(RuntimeError, s.get_key, wr)
        self.assertRaises(KeyError, mapping.__getitem__, rd)
        self.assertRaises(KeyError, mapping.__getitem__, wr)

    def test_get_key(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        key = s.register(rd, selectors.EVENT_READ, "data")
        self.assertEqual(key, s.get_key(rd))

        # unknown file obj
        self.assertRaises(KeyError, s.get_key, 999999)

    def test_get_map(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        keys = s.get_map()
        self.assertNieprawda(keys)
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])
        key = s.register(rd, selectors.EVENT_READ, "data")
        self.assertIn(rd, keys)
        self.assertEqual(key, keys[rd])
        self.assertEqual(len(keys), 1)
        self.assertEqual(list(keys), [rd.fileno()])
        self.assertEqual(list(keys.values()), [key])

        # unknown file obj
        przy self.assertRaises(KeyError):
            keys[999999]

        # Read-only mapping
        przy self.assertRaises(TypeError):
            usuń keys[rd]

    def test_select(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        s.register(rd, selectors.EVENT_READ)
        wr_key = s.register(wr, selectors.EVENT_WRITE)

        result = s.select()
        dla key, events w result:
            self.assertPrawda(isinstance(key, selectors.SelectorKey))
            self.assertPrawda(events)
            self.assertNieprawda(events & ~(selectors.EVENT_READ |
                                        selectors.EVENT_WRITE))

        self.assertEqual([(wr_key, selectors.EVENT_WRITE)], result)

    def test_context_manager(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        przy s jako sel:
            sel.register(rd, selectors.EVENT_READ)
            sel.register(wr, selectors.EVENT_WRITE)

        self.assertRaises(RuntimeError, s.get_key, rd)
        self.assertRaises(RuntimeError, s.get_key, wr)

    def test_fileno(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        jeżeli hasattr(s, 'fileno'):
            fd = s.fileno()
            self.assertPrawda(isinstance(fd, int))
            self.assertGreaterEqual(fd, 0)

    def test_selector(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        NUM_SOCKETS = 12
        MSG = b" This jest a test."
        MSG_LEN = len(MSG)
        readers = []
        writers = []
        r2w = {}
        w2r = {}

        dla i w range(NUM_SOCKETS):
            rd, wr = self.make_socketpair()
            s.register(rd, selectors.EVENT_READ)
            s.register(wr, selectors.EVENT_WRITE)
            readers.append(rd)
            writers.append(wr)
            r2w[rd] = wr
            w2r[wr] = rd

        bufs = []

        dopóki writers:
            ready = s.select()
            ready_writers = find_ready_matching(ready, selectors.EVENT_WRITE)
            jeżeli nie ready_writers:
                self.fail("no sockets ready dla writing")
            wr = random.choice(ready_writers)
            wr.send(MSG)

            dla i w range(10):
                ready = s.select()
                ready_readers = find_ready_matching(ready,
                                                    selectors.EVENT_READ)
                jeżeli ready_readers:
                    przerwij
                # there might be a delay between the write to the write end oraz
                # the read end jest reported ready
                sleep(0.1)
            inaczej:
                self.fail("no sockets ready dla reading")
            self.assertEqual([w2r[wr]], ready_readers)
            rd = ready_readers[0]
            buf = rd.recv(MSG_LEN)
            self.assertEqual(len(buf), MSG_LEN)
            bufs.append(buf)
            s.unregister(r2w[rd])
            s.unregister(rd)
            writers.remove(r2w[rd])

        self.assertEqual(bufs, [MSG] * NUM_SOCKETS)

    @unittest.skipIf(sys.platform == 'win32',
                     'select.select() cannot be used przy empty fd sets')
    def test_empty_select(self):
        # Issue #23009: Make sure EpollSelector.select() works when no FD jest
        # registered.
        s = self.SELECTOR()
        self.addCleanup(s.close)
        self.assertEqual(s.select(timeout=0), [])

    def test_timeout(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        s.register(wr, selectors.EVENT_WRITE)
        t = time()
        self.assertEqual(1, len(s.select(0)))
        self.assertEqual(1, len(s.select(-1)))
        self.assertLess(time() - t, 0.5)

        s.unregister(wr)
        s.register(rd, selectors.EVENT_READ)
        t = time()
        self.assertNieprawda(s.select(0))
        self.assertNieprawda(s.select(-1))
        self.assertLess(time() - t, 0.5)

        t0 = time()
        self.assertNieprawda(s.select(1))
        t1 = time()
        dt = t1 - t0
        # Tolerate 2.0 seconds dla very slow buildbots
        self.assertPrawda(0.8 <= dt <= 2.0, dt)

    @unittest.skipUnless(hasattr(signal, "alarm"),
                         "signal.alarm() required dla this test")
    def test_select_interrupt_exc(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        klasa InterruptSelect(Exception):
            dalej

        def handler(*args):
            podnieś InterruptSelect

        orig_alrm_handler = signal.signal(signal.SIGALRM, handler)
        self.addCleanup(signal.signal, signal.SIGALRM, orig_alrm_handler)
        self.addCleanup(signal.alarm, 0)

        signal.alarm(1)

        s.register(rd, selectors.EVENT_READ)
        t = time()
        # select() jest interrupted by a signal which podnieśs an exception
        przy self.assertRaises(InterruptSelect):
            s.select(30)
        # select() was interrupted before the timeout of 30 seconds
        self.assertLess(time() - t, 5.0)

    @unittest.skipUnless(hasattr(signal, "alarm"),
                         "signal.alarm() required dla this test")
    def test_select_interrupt_noraise(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        orig_alrm_handler = signal.signal(signal.SIGALRM, lambda *args: Nic)
        self.addCleanup(signal.signal, signal.SIGALRM, orig_alrm_handler)
        self.addCleanup(signal.alarm, 0)

        signal.alarm(1)

        s.register(rd, selectors.EVENT_READ)
        t = time()
        # select() jest interrupted by a signal, but the signal handler doesn't
        # podnieś an exception, so select() should by retries przy a recomputed
        # timeout
        self.assertNieprawda(s.select(1.5))
        self.assertGreaterEqual(time() - t, 1.0)


klasa ScalableSelectorMixIn:

    # see issue #18963 dla why it's skipped on older OS X versions
    @support.requires_mac_ver(10, 5)
    @unittest.skipUnless(resource, "Test needs resource module")
    def test_above_fd_setsize(self):
        # A scalable implementation should have no problem przy more than
        # FD_SETSIZE file descriptors. Since we don't know the value, we just
        # try to set the soft RLIMIT_NOFILE to the hard RLIMIT_NOFILE ceiling.
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        spróbuj:
            resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
            self.addCleanup(resource.setrlimit, resource.RLIMIT_NOFILE,
                            (soft, hard))
            NUM_FDS = min(hard, 2**16)
        wyjąwszy (OSError, ValueError):
            NUM_FDS = soft

        # guard dla already allocated FDs (stdin, stdout...)
        NUM_FDS -= 32

        s = self.SELECTOR()
        self.addCleanup(s.close)

        dla i w range(NUM_FDS // 2):
            spróbuj:
                rd, wr = self.make_socketpair()
            wyjąwszy OSError:
                # too many FDs, skip - note that we should only catch EMFILE
                # here, but apparently *BSD oraz Solaris can fail upon connect()
                # albo bind() przy EADDRNOTAVAIL, so let's be safe
                self.skipTest("FD limit reached")

            spróbuj:
                s.register(rd, selectors.EVENT_READ)
                s.register(wr, selectors.EVENT_WRITE)
            wyjąwszy OSError jako e:
                jeżeli e.errno == errno.ENOSPC:
                    # this can be podnieśd by epoll jeżeli we go over
                    # fs.epoll.max_user_watches sysctl
                    self.skipTest("FD limit reached")
                podnieś

        self.assertEqual(NUM_FDS // 2, len(s.select()))


klasa DefaultSelectorTestCase(BaseSelectorTestCase):

    SELECTOR = selectors.DefaultSelector


klasa SelectSelectorTestCase(BaseSelectorTestCase):

    SELECTOR = selectors.SelectSelector


@unittest.skipUnless(hasattr(selectors, 'PollSelector'),
                     "Test needs selectors.PollSelector")
klasa PollSelectorTestCase(BaseSelectorTestCase, ScalableSelectorMixIn):

    SELECTOR = getattr(selectors, 'PollSelector', Nic)


@unittest.skipUnless(hasattr(selectors, 'EpollSelector'),
                     "Test needs selectors.EpollSelector")
klasa EpollSelectorTestCase(BaseSelectorTestCase, ScalableSelectorMixIn):

    SELECTOR = getattr(selectors, 'EpollSelector', Nic)


@unittest.skipUnless(hasattr(selectors, 'KqueueSelector'),
                     "Test needs selectors.KqueueSelector)")
klasa KqueueSelectorTestCase(BaseSelectorTestCase, ScalableSelectorMixIn):

    SELECTOR = getattr(selectors, 'KqueueSelector', Nic)


@unittest.skipUnless(hasattr(selectors, 'DevpollSelector'),
                     "Test needs selectors.DevpollSelector")
klasa DevpollSelectorTestCase(BaseSelectorTestCase, ScalableSelectorMixIn):

    SELECTOR = getattr(selectors, 'DevpollSelector', Nic)



def test_main():
    tests = [DefaultSelectorTestCase, SelectSelectorTestCase,
             PollSelectorTestCase, EpollSelectorTestCase,
             KqueueSelectorTestCase, DevpollSelectorTestCase]
    support.run_unittest(*tests)
    support.reap_children()


jeżeli __name__ == "__main__":
    test_main()
