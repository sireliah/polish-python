# Test case dla the select.devpoll() function

# Initial tests are copied jako jest z "test_poll.py"

zaimportuj os
zaimportuj random
zaimportuj select
zaimportuj sys
zaimportuj unittest
z test.support zaimportuj TESTFN, run_unittest, cpython_only

jeżeli nie hasattr(select, 'devpoll') :
    podnieś unittest.SkipTest('test works only on Solaris OS family')


def find_ready_matching(ready, flag):
    match = []
    dla fd, mode w ready:
        jeżeli mode & flag:
            match.append(fd)
    zwróć match

klasa DevPollTests(unittest.TestCase):

    def test_devpoll1(self):
        # Basic functional test of poll object
        # Create a bunch of pipe oraz test that poll works przy them.

        p = select.devpoll()

        NUM_PIPES = 12
        MSG = b" This jest a test."
        MSG_LEN = len(MSG)
        readers = []
        writers = []
        r2w = {}
        w2r = {}

        dla i w range(NUM_PIPES):
            rd, wr = os.pipe()
            p.register(rd)
            p.modify(rd, select.POLLIN)
            p.register(wr, select.POLLOUT)
            readers.append(rd)
            writers.append(wr)
            r2w[rd] = wr
            w2r[wr] = rd

        bufs = []

        dopóki writers:
            ready = p.poll()
            ready_writers = find_ready_matching(ready, select.POLLOUT)
            jeżeli nie ready_writers:
                self.fail("no pipes ready dla writing")
            wr = random.choice(ready_writers)
            os.write(wr, MSG)

            ready = p.poll()
            ready_readers = find_ready_matching(ready, select.POLLIN)
            jeżeli nie ready_readers:
                self.fail("no pipes ready dla reading")
            self.assertEqual([w2r[wr]], ready_readers)
            rd = ready_readers[0]
            buf = os.read(rd, MSG_LEN)
            self.assertEqual(len(buf), MSG_LEN)
            bufs.append(buf)
            os.close(r2w[rd]) ; os.close(rd)
            p.unregister(r2w[rd])
            p.unregister(rd)
            writers.remove(r2w[rd])

        self.assertEqual(bufs, [MSG] * NUM_PIPES)

    def test_timeout_overflow(self):
        pollster = select.devpoll()
        w, r = os.pipe()
        pollster.register(w)

        pollster.poll(-1)
        self.assertRaises(OverflowError, pollster.poll, -2)
        self.assertRaises(OverflowError, pollster.poll, -1 << 31)
        self.assertRaises(OverflowError, pollster.poll, -1 << 64)

        pollster.poll(0)
        pollster.poll(1)
        pollster.poll(1 << 30)
        self.assertRaises(OverflowError, pollster.poll, 1 << 31)
        self.assertRaises(OverflowError, pollster.poll, 1 << 63)
        self.assertRaises(OverflowError, pollster.poll, 1 << 64)

    def test_close(self):
        open_file = open(__file__, "rb")
        self.addCleanup(open_file.close)
        fd = open_file.fileno()
        devpoll = select.devpoll()

        # test fileno() method oraz closed attribute
        self.assertIsInstance(devpoll.fileno(), int)
        self.assertNieprawda(devpoll.closed)

        # test close()
        devpoll.close()
        self.assertPrawda(devpoll.closed)
        self.assertRaises(ValueError, devpoll.fileno)

        # close() can be called more than once
        devpoll.close()

        # operations must fail przy ValueError("I/O operation on closed ...")
        self.assertRaises(ValueError, devpoll.modify, fd, select.POLLIN)
        self.assertRaises(ValueError, devpoll.poll)
        self.assertRaises(ValueError, devpoll.register, fd, fd, select.POLLIN)
        self.assertRaises(ValueError, devpoll.unregister, fd)

    def test_fd_non_inheritable(self):
        devpoll = select.devpoll()
        self.addCleanup(devpoll.close)
        self.assertEqual(os.get_inheritable(devpoll.fileno()), Nieprawda)

    def test_events_mask_overflow(self):
        pollster = select.devpoll()
        w, r = os.pipe()
        pollster.register(w)
        # Issue #17919
        self.assertRaises(OverflowError, pollster.register, 0, -1)
        self.assertRaises(OverflowError, pollster.register, 0, 1 << 64)
        self.assertRaises(OverflowError, pollster.modify, 1, -1)
        self.assertRaises(OverflowError, pollster.modify, 1, 1 << 64)

    @cpython_only
    def test_events_mask_overflow_c_limits(self):
        z _testcapi zaimportuj USHRT_MAX
        pollster = select.devpoll()
        w, r = os.pipe()
        pollster.register(w)
        # Issue #17919
        self.assertRaises(OverflowError, pollster.register, 0, USHRT_MAX + 1)
        self.assertRaises(OverflowError, pollster.modify, 1, USHRT_MAX + 1)


def test_main():
    run_unittest(DevPollTests)

jeżeli __name__ == '__main__':
    test_main()
