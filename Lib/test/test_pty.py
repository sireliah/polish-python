z test.support zaimportuj verbose, import_module, reap_children

# Skip these tests jeżeli termios jest nie available
import_module('termios')

zaimportuj errno
zaimportuj pty
zaimportuj os
zaimportuj sys
zaimportuj select
zaimportuj signal
zaimportuj socket
zaimportuj unittest

TEST_STRING_1 = b"I wish to buy a fish license.\n"
TEST_STRING_2 = b"For my pet fish, Eric.\n"

jeżeli verbose:
    def debug(msg):
        print(msg)
inaczej:
    def debug(msg):
        dalej


def normalize_output(data):
    # Some operating systems do conversions on newline.  We could possibly
    # fix that by doing the appropriate termios.tcsetattr()s.  I couldn't
    # figure out the right combo on Tru64 oraz I don't have an IRIX box.
    # So just normalize the output oraz doc the problem O/Ses by allowing
    # certain combinations dla some platforms, but avoid allowing other
    # differences (like extra whitespace, trailing garbage, etc.)

    # This jest about the best we can do without getting some feedback
    # z someone more knowledgable.

    # OSF/1 (Tru64) apparently turns \n into \r\r\n.
    jeżeli data.endswith(b'\r\r\n'):
        zwróć data.replace(b'\r\r\n', b'\n')

    # IRIX apparently turns \n into \r\n.
    jeżeli data.endswith(b'\r\n'):
        zwróć data.replace(b'\r\n', b'\n')

    zwróć data


# Marginal testing of pty suite. Cannot do extensive 'do albo fail' testing
# because pty code jest nie too portable.
# XXX(nnorwitz):  these tests leak fds when there jest an error.
klasa PtyTest(unittest.TestCase):
    def setUp(self):
        # isatty() oraz close() can hang on some platforms.  Set an alarm
        # before running the test to make sure we don't hang forever.
        self.old_alarm = signal.signal(signal.SIGALRM, self.handle_sig)
        signal.alarm(10)

    def tearDown(self):
        # remove alarm, restore old alarm handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, self.old_alarm)

    def handle_sig(self, sig, frame):
        self.fail("isatty hung")

    def test_basic(self):
        spróbuj:
            debug("Calling master_open()")
            master_fd, slave_name = pty.master_open()
            debug("Got master_fd '%d', slave_name '%s'" %
                  (master_fd, slave_name))
            debug("Calling slave_open(%r)" % (slave_name,))
            slave_fd = pty.slave_open(slave_name)
            debug("Got slave_fd '%d'" % slave_fd)
        wyjąwszy OSError:
            # " An optional feature could nie be imported " ... ?
            podnieś unittest.SkipTest("Pseudo-terminals (seemingly) nie functional.")

        self.assertPrawda(os.isatty(slave_fd), 'slave_fd jest nie a tty')

        # Solaris requires reading the fd before anything jest returned.
        # My guess jest that since we open oraz close the slave fd
        # w master_open(), we need to read the EOF.

        # Ensure the fd jest non-blocking w case there's nothing to read.
        blocking = os.get_blocking(master_fd)
        spróbuj:
            os.set_blocking(master_fd, Nieprawda)
            spróbuj:
                s1 = os.read(master_fd, 1024)
                self.assertEqual(b'', s1)
            wyjąwszy OSError jako e:
                jeżeli e.errno != errno.EAGAIN:
                    podnieś
        w_końcu:
            # Restore the original flags.
            os.set_blocking(master_fd, blocking)

        debug("Writing to slave_fd")
        os.write(slave_fd, TEST_STRING_1)
        s1 = os.read(master_fd, 1024)
        self.assertEqual(b'I wish to buy a fish license.\n',
                         normalize_output(s1))

        debug("Writing chunked output")
        os.write(slave_fd, TEST_STRING_2[:5])
        os.write(slave_fd, TEST_STRING_2[5:])
        s2 = os.read(master_fd, 1024)
        self.assertEqual(b'For my pet fish, Eric.\n', normalize_output(s2))

        os.close(slave_fd)
        os.close(master_fd)


    def test_fork(self):
        debug("calling pty.fork()")
        pid, master_fd = pty.fork()
        jeżeli pid == pty.CHILD:
            # stdout should be connected to a tty.
            jeżeli nie os.isatty(1):
                debug("Child's fd 1 jest nie a tty?!")
                os._exit(3)

            # After pty.fork(), the child should already be a session leader.
            # (on those systems that have that concept.)
            debug("In child, calling os.setsid()")
            spróbuj:
                os.setsid()
            wyjąwszy OSError:
                # Good, we already were session leader
                debug("Good: OSError was podnieśd.")
                dalej
            wyjąwszy AttributeError:
                # Have pty, but nie setsid()?
                debug("No setsid() available?")
                dalej
            wyjąwszy:
                # We don't want this error to propagate, escaping the call to
                # os._exit() oraz causing very peculiar behavior w the calling
                # regrtest.py !
                # Note: could add traceback printing here.
                debug("An unexpected error was podnieśd.")
                os._exit(1)
            inaczej:
                debug("os.setsid() succeeded! (bad!)")
                os._exit(2)
            os._exit(4)
        inaczej:
            debug("Waiting dla child (%d) to finish." % pid)
            # In verbose mode, we have to consume the debug output z the
            # child albo the child will block, causing this test to hang w the
            # parent's waitpid() call.  The child blocks after a
            # platform-dependent amount of data jest written to its fd.  On
            # Linux 2.6, it's 4000 bytes oraz the child won't block, but on OS
            # X even the small writes w the child above will block it.  Also
            # on Linux, the read() will podnieś an OSError (input/output error)
            # when it tries to read past the end of the buffer but the child's
            # already exited, so catch oraz discard those exceptions.  It's nie
            # worth checking dla EIO.
            dopóki Prawda:
                spróbuj:
                    data = os.read(master_fd, 80)
                wyjąwszy OSError:
                    przerwij
                jeżeli nie data:
                    przerwij
                sys.stdout.write(str(data.replace(b'\r\n', b'\n'),
                                     encoding='ascii'))

            ##line = os.read(master_fd, 80)
            ##lines = line.replace('\r\n', '\n').split('\n')
            ##jeżeli Nieprawda oraz lines != ['In child, calling os.setsid()',
            ##             'Good: OSError was podnieśd.', '']:
            ##    podnieś TestFailed("Unexpected output z child: %r" % line)

            (pid, status) = os.waitpid(pid, 0)
            res = status >> 8
            debug("Child (%d) exited przy status %d (%d)." % (pid, res, status))
            jeżeli res == 1:
                self.fail("Child podnieśd an unexpected exception w os.setsid()")
            albo_inaczej res == 2:
                self.fail("pty.fork() failed to make child a session leader.")
            albo_inaczej res == 3:
                self.fail("Child spawned by pty.fork() did nie have a tty jako stdout")
            albo_inaczej res != 4:
                self.fail("pty.fork() failed dla unknown reasons.")

            ##debug("Reading z master_fd now that the child has exited")
            ##spróbuj:
            ##    s1 = os.read(master_fd, 1024)
            ##wyjąwszy OSError:
            ##    dalej
            ##inaczej:
            ##    podnieś TestFailed("Read z master_fd did nie podnieś exception")

        os.close(master_fd)

        # pty.fork() dalejed.


klasa SmallPtyTests(unittest.TestCase):
    """These tests don't spawn children albo hang."""

    def setUp(self):
        self.orig_stdin_fileno = pty.STDIN_FILENO
        self.orig_stdout_fileno = pty.STDOUT_FILENO
        self.orig_pty_select = pty.select
        self.fds = []  # A list of file descriptors to close.
        self.files = []
        self.select_rfds_lengths = []
        self.select_rfds_results = []

    def tearDown(self):
        pty.STDIN_FILENO = self.orig_stdin_fileno
        pty.STDOUT_FILENO = self.orig_stdout_fileno
        pty.select = self.orig_pty_select
        dla file w self.files:
            spróbuj:
                file.close()
            wyjąwszy OSError:
                dalej
        dla fd w self.fds:
            spróbuj:
                os.close(fd)
            wyjąwszy OSError:
                dalej

    def _pipe(self):
        pipe_fds = os.pipe()
        self.fds.extend(pipe_fds)
        zwróć pipe_fds

    def _socketpair(self):
        socketpair = socket.socketpair()
        self.files.extend(socketpair)
        zwróć socketpair

    def _mock_select(self, rfds, wfds, xfds):
        # This will podnieś IndexError when no more expected calls exist.
        self.assertEqual(self.select_rfds_lengths.pop(0), len(rfds))
        zwróć self.select_rfds_results.pop(0), [], []

    def test__copy_to_each(self):
        """Test the normal data case on both master_fd oraz stdin."""
        read_from_stdout_fd, mock_stdout_fd = self._pipe()
        pty.STDOUT_FILENO = mock_stdout_fd
        mock_stdin_fd, write_to_stdin_fd = self._pipe()
        pty.STDIN_FILENO = mock_stdin_fd
        socketpair = self._socketpair()
        masters = [s.fileno() dla s w socketpair]

        # Feed data.  Smaller than PIPEBUF.  These writes will nie block.
        os.write(masters[1], b'z master')
        os.write(write_to_stdin_fd, b'z stdin')

        # Expect two select calls, the last one will cause IndexError
        pty.select = self._mock_select
        self.select_rfds_lengths.append(2)
        self.select_rfds_results.append([mock_stdin_fd, masters[0]])
        self.select_rfds_lengths.append(2)

        przy self.assertRaises(IndexError):
            pty._copy(masters[0])

        # Test that the right data went to the right places.
        rfds = select.select([read_from_stdout_fd, masters[1]], [], [], 0)[0]
        self.assertEqual([read_from_stdout_fd, masters[1]], rfds)
        self.assertEqual(os.read(read_from_stdout_fd, 20), b'z master')
        self.assertEqual(os.read(masters[1], 20), b'z stdin')

    def test__copy_eof_on_all(self):
        """Test the empty read EOF case on both master_fd oraz stdin."""
        read_from_stdout_fd, mock_stdout_fd = self._pipe()
        pty.STDOUT_FILENO = mock_stdout_fd
        mock_stdin_fd, write_to_stdin_fd = self._pipe()
        pty.STDIN_FILENO = mock_stdin_fd
        socketpair = self._socketpair()
        masters = [s.fileno() dla s w socketpair]

        os.close(masters[1])
        socketpair[1].close()
        os.close(write_to_stdin_fd)

        # Expect two select calls, the last one will cause IndexError
        pty.select = self._mock_select
        self.select_rfds_lengths.append(2)
        self.select_rfds_results.append([mock_stdin_fd, masters[0]])
        # We expect that both fds were removed z the fds list jako they
        # both encountered an EOF before the second select call.
        self.select_rfds_lengths.append(0)

        przy self.assertRaises(IndexError):
            pty._copy(masters[0])


def tearDownModule():
    reap_children()

jeżeli __name__ == "__main__":
    unittest.main()
