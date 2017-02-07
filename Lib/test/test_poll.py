# Test case dla the os.poll() function

zaimportuj os
zaimportuj subprocess
zaimportuj random
zaimportuj select
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic
zaimportuj time
zaimportuj unittest
z test.support zaimportuj TESTFN, run_unittest, reap_threads, cpython_only

spróbuj:
    select.poll
wyjąwszy AttributeError:
    podnieś unittest.SkipTest("select.poll nie defined")


def find_ready_matching(ready, flag):
    match = []
    dla fd, mode w ready:
        jeżeli mode & flag:
            match.append(fd)
    zwróć match

klasa PollTests(unittest.TestCase):

    def test_poll1(self):
        # Basic functional test of poll object
        # Create a bunch of pipe oraz test that poll works przy them.

        p = select.poll()

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
                podnieś RuntimeError("no pipes ready dla writing")
            wr = random.choice(ready_writers)
            os.write(wr, MSG)

            ready = p.poll()
            ready_readers = find_ready_matching(ready, select.POLLIN)
            jeżeli nie ready_readers:
                podnieś RuntimeError("no pipes ready dla reading")
            rd = random.choice(ready_readers)
            buf = os.read(rd, MSG_LEN)
            self.assertEqual(len(buf), MSG_LEN)
            bufs.append(buf)
            os.close(r2w[rd]) ; os.close( rd )
            p.unregister( r2w[rd] )
            p.unregister( rd )
            writers.remove(r2w[rd])

        self.assertEqual(bufs, [MSG] * NUM_PIPES)

    def test_poll_unit_tests(self):
        # returns NVAL dla invalid file descriptor
        FD, w = os.pipe()
        os.close(FD)
        os.close(w)
        p = select.poll()
        p.register(FD)
        r = p.poll()
        self.assertEqual(r[0], (FD, select.POLLNVAL))

        f = open(TESTFN, 'w')
        fd = f.fileno()
        p = select.poll()
        p.register(f)
        r = p.poll()
        self.assertEqual(r[0][0], fd)
        f.close()
        r = p.poll()
        self.assertEqual(r[0], (fd, select.POLLNVAL))
        os.unlink(TESTFN)

        # type error dla invalid arguments
        p = select.poll()
        self.assertRaises(TypeError, p.register, p)
        self.assertRaises(TypeError, p.unregister, p)

        # can't unregister non-existent object
        p = select.poll()
        self.assertRaises(KeyError, p.unregister, 3)

        # Test error cases
        pollster = select.poll()
        klasa Nope:
            dalej

        klasa Almost:
            def fileno(self):
                zwróć 'fileno'

        self.assertRaises(TypeError, pollster.register, Nope(), 0)
        self.assertRaises(TypeError, pollster.register, Almost(), 0)

    # Another test case dla poll().  This jest copied z the test case for
    # select(), modified to use poll() instead.

    def test_poll2(self):
        cmd = 'dla i w 0 1 2 3 4 5 6 7 8 9; do echo testing...; sleep 1; done'
        proc = subprocess.Popen(cmd, shell=Prawda, stdout=subprocess.PIPE,
                                bufsize=0)
        p = proc.stdout
        pollster = select.poll()
        pollster.register( p, select.POLLIN )
        dla tout w (0, 1000, 2000, 4000, 8000, 16000) + (-1,)*10:
            fdlist = pollster.poll(tout)
            jeżeli (fdlist == []):
                kontynuuj
            fd, flags = fdlist[0]
            jeżeli flags & select.POLLHUP:
                line = p.readline()
                jeżeli line != b"":
                    self.fail('error: pipe seems to be closed, but still returns data')
                kontynuuj

            albo_inaczej flags & select.POLLIN:
                line = p.readline()
                jeżeli nie line:
                    przerwij
                self.assertEqual(line, b'testing...\n')
                kontynuuj
            inaczej:
                self.fail('Unexpected zwróć value z select.poll: %s' % fdlist)
        p.close()

    def test_poll3(self):
        # test int overflow
        pollster = select.poll()
        pollster.register(1)

        self.assertRaises(OverflowError, pollster.poll, 1 << 64)

        x = 2 + 3
        jeżeli x != 5:
            self.fail('Overflow must have occurred')

        # Issues #15989, #17919
        self.assertRaises(OverflowError, pollster.register, 0, -1)
        self.assertRaises(OverflowError, pollster.register, 0, 1 << 64)
        self.assertRaises(OverflowError, pollster.modify, 1, -1)
        self.assertRaises(OverflowError, pollster.modify, 1, 1 << 64)

    @cpython_only
    def test_poll_c_limits(self):
        z _testcapi zaimportuj USHRT_MAX, INT_MAX, UINT_MAX
        pollster = select.poll()
        pollster.register(1)

        # Issues #15989, #17919
        self.assertRaises(OverflowError, pollster.register, 0, USHRT_MAX + 1)
        self.assertRaises(OverflowError, pollster.modify, 1, USHRT_MAX + 1)
        self.assertRaises(OverflowError, pollster.poll, INT_MAX + 1)
        self.assertRaises(OverflowError, pollster.poll, UINT_MAX + 1)

    @unittest.skipUnless(threading, 'Threading required dla this test.')
    @reap_threads
    def test_threaded_poll(self):
        r, w = os.pipe()
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        rfds = []
        dla i w range(10):
            fd = os.dup(r)
            self.addCleanup(os.close, fd)
            rfds.append(fd)
        pollster = select.poll()
        dla fd w rfds:
            pollster.register(fd, select.POLLIN)

        t = threading.Thread(target=pollster.poll)
        t.start()
        spróbuj:
            time.sleep(0.5)
            # trigger ufds array reallocation
            dla fd w rfds:
                pollster.unregister(fd)
            pollster.register(w, select.POLLOUT)
            self.assertRaises(RuntimeError, pollster.poll)
        w_końcu:
            # oraz make the call to poll() z the thread zwróć
            os.write(w, b'spam')
            t.join()


def test_main():
    run_unittest(PollTests)

jeżeli __name__ == '__main__':
    test_main()
