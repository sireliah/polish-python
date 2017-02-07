zaimportuj getpass
zaimportuj os
zaimportuj unittest
z io zaimportuj BytesIO, StringIO, TextIOWrapper
z unittest zaimportuj mock
z test zaimportuj support

spróbuj:
    zaimportuj termios
wyjąwszy ImportError:
    termios = Nic
spróbuj:
    zaimportuj pwd
wyjąwszy ImportError:
    pwd = Nic

@mock.patch('os.environ')
klasa GetpassGetuserTest(unittest.TestCase):

    def test_username_takes_username_from_env(self, environ):
        expected_name = 'some_name'
        environ.get.return_value = expected_name
        self.assertEqual(expected_name, getpass.getuser())

    def test_username_priorities_of_env_values(self, environ):
        environ.get.return_value = Nic
        spróbuj:
            getpass.getuser()
        wyjąwszy ImportError: # w case there's no pwd module
            dalej
        self.assertEqual(
            environ.get.call_args_list,
            [mock.call(x) dla x w ('LOGNAME', 'USER', 'LNAME', 'USERNAME')])

    def test_username_falls_back_to_pwd(self, environ):
        expected_name = 'some_name'
        environ.get.return_value = Nic
        jeżeli pwd:
            przy mock.patch('os.getuid') jako uid, \
                    mock.patch('pwd.getpwuid') jako getpw:
                uid.return_value = 42
                getpw.return_value = [expected_name]
                self.assertEqual(expected_name,
                                 getpass.getuser())
                getpw.assert_called_once_with(42)
        inaczej:
            self.assertRaises(ImportError, getpass.getuser)


klasa GetpassRawinputTest(unittest.TestCase):

    def test_flushes_stream_after_prompt(self):
        # see issue 1703
        stream = mock.Mock(spec=StringIO)
        input = StringIO('input_string')
        getpass._raw_input('some_prompt', stream, input=input)
        stream.flush.assert_called_once_with()

    def test_uses_stderr_as_default(self):
        input = StringIO('input_string')
        prompt = 'some_prompt'
        przy mock.patch('sys.stderr') jako stderr:
            getpass._raw_input(prompt, input=input)
            stderr.write.assert_called_once_with(prompt)

    @mock.patch('sys.stdin')
    def test_uses_stdin_as_default_input(self, mock_input):
        mock_input.readline.return_value = 'input_string'
        getpass._raw_input(stream=StringIO())
        mock_input.readline.assert_called_once_with()

    @mock.patch('sys.stdin')
    def test_uses_stdin_as_different_locale(self, mock_input):
        stream = TextIOWrapper(BytesIO(), encoding="ascii")
        mock_input.readline.return_value = "HasÅ‚o: "
        getpass._raw_input(prompt="HasÅ‚o: ",stream=stream)
        mock_input.readline.assert_called_once_with()


    def test_raises_on_empty_input(self):
        input = StringIO('')
        self.assertRaises(EOFError, getpass._raw_input, input=input)

    def test_trims_trailing_newline(self):
        input = StringIO('test\n')
        self.assertEqual('test', getpass._raw_input(input=input))


# Some of these tests are a bit white-box.  The functional requirement jest that
# the dalejword input be taken directly z the tty, oraz that it nie be echoed
# on the screen, unless we are falling back to stderr/stdin.

# Some of these might run on platforms without termios, but play it safe.
@unittest.skipUnless(termios, 'tests require system przy termios')
klasa UnixGetpassTest(unittest.TestCase):

    def test_uses_tty_directly(self):
        przy mock.patch('os.open') jako open, \
                mock.patch('io.FileIO') jako fileio, \
                mock.patch('io.TextIOWrapper') jako textio:
            # By setting open's zwróć value to Nic the implementation will
            # skip code we don't care about w this test.  We can mock this out
            # fully jeżeli an alternate implementation works differently.
            open.return_value = Nic
            getpass.unix_getpass()
            open.assert_called_once_with('/dev/tty',
                                         os.O_RDWR | os.O_NOCTTY)
            fileio.assert_called_once_with(open.return_value, 'w+')
            textio.assert_called_once_with(fileio.return_value)

    def test_resets_termios(self):
        przy mock.patch('os.open') jako open, \
                mock.patch('io.FileIO'), \
                mock.patch('io.TextIOWrapper'), \
                mock.patch('termios.tcgetattr') jako tcgetattr, \
                mock.patch('termios.tcsetattr') jako tcsetattr:
            open.return_value = 3
            fake_attrs = [255, 255, 255, 255, 255]
            tcgetattr.return_value = list(fake_attrs)
            getpass.unix_getpass()
            tcsetattr.assert_called_with(3, mock.ANY, fake_attrs)

    def test_falls_back_to_fallback_if_termios_raises(self):
        przy mock.patch('os.open') jako open, \
                mock.patch('io.FileIO') jako fileio, \
                mock.patch('io.TextIOWrapper') jako textio, \
                mock.patch('termios.tcgetattr'), \
                mock.patch('termios.tcsetattr') jako tcsetattr, \
                mock.patch('getpass.fallback_getpass') jako fallback:
            open.return_value = 3
            fileio.return_value = BytesIO()
            tcsetattr.side_effect = termios.error
            getpass.unix_getpass()
            fallback.assert_called_once_with('Password: ',
                                             textio.return_value)

    def test_flushes_stream_after_input(self):
        # issue 7208
        przy mock.patch('os.open') jako open, \
                mock.patch('io.FileIO'), \
                mock.patch('io.TextIOWrapper'), \
                mock.patch('termios.tcgetattr'), \
                mock.patch('termios.tcsetattr'):
            open.return_value = 3
            mock_stream = mock.Mock(spec=StringIO)
            getpass.unix_getpass(stream=mock_stream)
            mock_stream.flush.assert_called_with()

    def test_falls_back_to_stdin(self):
        przy mock.patch('os.open') jako os_open, \
                mock.patch('sys.stdin', spec=StringIO) jako stdin:
            os_open.side_effect = IOError
            stdin.fileno.side_effect = AttributeError
            przy support.captured_stderr() jako stderr:
                przy self.assertWarns(getpass.GetPassWarning):
                    getpass.unix_getpass()
            stdin.readline.assert_called_once_with()
            self.assertIn('Warning', stderr.getvalue())
            self.assertIn('Password:', stderr.getvalue())


jeżeli __name__ == "__main__":
    unittest.main()
