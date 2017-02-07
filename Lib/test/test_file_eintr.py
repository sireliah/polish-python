# Written to test interrupted system calls interfering przy our many buffered
# IO implementations.  http://bugs.python.org/issue12268
#
# It was suggested that this code could be merged into test_io oraz the tests
# made to work using the same method jako the existing signal tests w test_io.
# I was unable to get single process tests using alarm albo setitimer that way
# to reproduce the EINTR problems.  This process based test suite reproduces
# the problems prior to the issue12268 patch reliably on Linux oraz OSX.
#  - gregory.p.smith

zaimportuj os
zaimportuj select
zaimportuj signal
zaimportuj subprocess
zaimportuj sys
zaimportuj time
zaimportuj unittest

# Test zaimportuj all of the things we're about to try testing up front.
zaimportuj _io
zaimportuj _pyio


@unittest.skipUnless(os.name == 'posix', 'tests requires a posix system.')
klasa TestFileIOSignalInterrupt:
    def setUp(self):
        self._process = Nic

    def tearDown(self):
        jeżeli self._process oraz self._process.poll() jest Nic:
            spróbuj:
                self._process.kill()
            wyjąwszy OSError:
                dalej

    def _generate_infile_setup_code(self):
        """Returns the infile = ... line of code dla the reader process.

        subclasseses should override this to test different IO objects.
        """
        zwróć ('zaimportuj %s jako io ;'
                'infile = io.FileIO(sys.stdin.fileno(), "rb")' %
                self.modname)

    def fail_with_process_info(self, why, stdout=b'', stderr=b'',
                               communicate=Prawda):
        """A common way to cleanup oraz fail przy useful debug output.

        Kills the process jeżeli it jest still running, collects remaining output
        oraz fails the test przy an error message including the output.

        Args:
            why: Text to go after "Error z IO process" w the message.
            stdout, stderr: standard output oraz error z the process so
                far to include w the error message.
            communicate: bool, when Prawda we call communicate() on the process
                after killing it to gather additional output.
        """
        jeżeli self._process.poll() jest Nic:
            time.sleep(0.1)  # give it time to finish printing the error.
            spróbuj:
                self._process.terminate()  # Ensure it dies.
            wyjąwszy OSError:
                dalej
        jeżeli communicate:
            stdout_end, stderr_end = self._process.communicate()
            stdout += stdout_end
            stderr += stderr_end
        self.fail('Error z IO process %s:\nSTDOUT:\n%sSTDERR:\n%s\n' %
                  (why, stdout.decode(), stderr.decode()))

    def _test_reading(self, data_to_write, read_and_verify_code):
        """Generic buffered read method test harness to validate EINTR behavior.

        Also validates that Python signal handlers are run during the read.

        Args:
            data_to_write: String to write to the child process dla reading
                before sending it a signal, confirming the signal was handled,
                writing a final newline oraz closing the infile pipe.
            read_and_verify_code: Single "line" of code to read z a file
                object named 'infile' oraz validate the result.  This will be
                executed jako part of a python subprocess fed data_to_write.
        """
        infile_setup_code = self._generate_infile_setup_code()
        # Total pipe IO w this function jest smaller than the minimum posix OS
        # pipe buffer size of 512 bytes.  No writer should block.
        assert len(data_to_write) < 512, 'data_to_write must fit w pipe buf.'

        # Start a subprocess to call our read method dopóki handling a signal.
        self._process = subprocess.Popen(
                [sys.executable, '-u', '-c',
                 'zaimportuj signal, sys ;'
                 'signal.signal(signal.SIGINT, '
                               'lambda s, f: sys.stderr.write("$\\n")) ;'
                 + infile_setup_code + ' ;' +
                 'sys.stderr.write("Worm Sign!\\n") ;'
                 + read_and_verify_code + ' ;' +
                 'infile.close()'
                ],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        # Wait dla the signal handler to be installed.
        worm_sign = self._process.stderr.read(len(b'Worm Sign!\n'))
        jeżeli worm_sign != b'Worm Sign!\n':  # See also, Dune by Frank Herbert.
            self.fail_with_process_info('dopóki awaiting a sign',
                                        stderr=worm_sign)
        self._process.stdin.write(data_to_write)

        signals_sent = 0
        rlist = []
        # We don't know when the read_and_verify_code w our child jest actually
        # executing within the read system call we want to interrupt.  This
        # loop waits dla a bit before sending the first signal to increase
        # the likelihood of that.  Implementations without correct EINTR
        # oraz signal handling usually fail this test.
        dopóki nie rlist:
            rlist, _, _ = select.select([self._process.stderr], (), (), 0.05)
            self._process.send_signal(signal.SIGINT)
            signals_sent += 1
            jeżeli signals_sent > 200:
                self._process.kill()
                self.fail('reader process failed to handle our signals.')
        # This assumes anything unexpected that writes to stderr will also
        # write a newline.  That jest true of the traceback printing code.
        signal_line = self._process.stderr.readline()
        jeżeli signal_line != b'$\n':
            self.fail_with_process_info('dopóki awaiting signal',
                                        stderr=signal_line)

        # We append a newline to our input so that a readline call can
        # end on its own before the EOF jest seen oraz so that we're testing
        # the read call that was interrupted by a signal before the end of
        # the data stream has been reached.
        stdout, stderr = self._process.communicate(input=b'\n')
        jeżeli self._process.returncode:
            self.fail_with_process_info(
                    'exited rc=%d' % self._process.returncode,
                    stdout, stderr, communicate=Nieprawda)
        # PASS!

    # String format dla the read_and_verify_code used by read methods.
    _READING_CODE_TEMPLATE = (
            'got = infile.{read_method_name}() ;'
            'expected = {expected!r} ;'
            'assert got == expected, ('
                    '"{read_method_name} returned wrong data.\\n"'
                    '"got data %r\\nexpected %r" % (got, expected))'
            )

    def test_readline(self):
        """readline() must handle signals oraz nie lose data."""
        self._test_reading(
                data_to_write=b'hello, world!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readline',
                        expected=b'hello, world!\n'))

    def test_readlines(self):
        """readlines() must handle signals oraz nie lose data."""
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readlines',
                        expected=[b'hello\n', b'world!\n']))

    def test_readall(self):
        """readall() must handle signals oraz nie lose data."""
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readall',
                        expected=b'hello\nworld!\n'))
        # read() jest the same thing jako readall().
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='read',
                        expected=b'hello\nworld!\n'))


klasa CTestFileIOSignalInterrupt(TestFileIOSignalInterrupt, unittest.TestCase):
    modname = '_io'

klasa PyTestFileIOSignalInterrupt(TestFileIOSignalInterrupt, unittest.TestCase):
    modname = '_pyio'


klasa TestBufferedIOSignalInterrupt(TestFileIOSignalInterrupt):
    def _generate_infile_setup_code(self):
        """Returns the infile = ... line of code to make a BufferedReader."""
        zwróć ('zaimportuj %s jako io ;infile = io.open(sys.stdin.fileno(), "rb") ;'
                'assert isinstance(infile, io.BufferedReader)' %
                self.modname)

    def test_readall(self):
        """BufferedReader.read() must handle signals oraz nie lose data."""
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='read',
                        expected=b'hello\nworld!\n'))

klasa CTestBufferedIOSignalInterrupt(TestBufferedIOSignalInterrupt, unittest.TestCase):
    modname = '_io'

klasa PyTestBufferedIOSignalInterrupt(TestBufferedIOSignalInterrupt, unittest.TestCase):
    modname = '_pyio'


klasa TestTextIOSignalInterrupt(TestFileIOSignalInterrupt):
    def _generate_infile_setup_code(self):
        """Returns the infile = ... line of code to make a TextIOWrapper."""
        zwróć ('zaimportuj %s jako io ;'
                'infile = io.open(sys.stdin.fileno(), "rt", newline=Nic) ;'
                'assert isinstance(infile, io.TextIOWrapper)' %
                self.modname)

    def test_readline(self):
        """readline() must handle signals oraz nie lose data."""
        self._test_reading(
                data_to_write=b'hello, world!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readline',
                        expected='hello, world!\n'))

    def test_readlines(self):
        """readlines() must handle signals oraz nie lose data."""
        self._test_reading(
                data_to_write=b'hello\r\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readlines',
                        expected=['hello\n', 'world!\n']))

    def test_readall(self):
        """read() must handle signals oraz nie lose data."""
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='read',
                        expected="hello\nworld!\n"))

klasa CTestTextIOSignalInterrupt(TestTextIOSignalInterrupt, unittest.TestCase):
    modname = '_io'

klasa PyTestTextIOSignalInterrupt(TestTextIOSignalInterrupt, unittest.TestCase):
    modname = '_pyio'


jeżeli __name__ == '__main__':
    unittest.main()
