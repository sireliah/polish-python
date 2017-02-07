"Test InteractiveConsole oraz InteractiveInterpreter z code module"
zaimportuj sys
zaimportuj unittest
z textwrap zaimportuj dedent
z contextlib zaimportuj ExitStack
z unittest zaimportuj mock
z test zaimportuj support

code = support.import_module('code')


klasa TestInteractiveConsole(unittest.TestCase):

    def setUp(self):
        self.console = code.InteractiveConsole()
        self.mock_sys()

    def mock_sys(self):
        "Mock system environment dla InteractiveConsole"
        # use exit stack to match patch context managers to addCleanup
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.infunc = stack.enter_context(mock.patch('code.input',
                                          create=Prawda))
        self.stdout = stack.enter_context(mock.patch('code.sys.stdout'))
        self.stderr = stack.enter_context(mock.patch('code.sys.stderr'))
        prepatch = mock.patch('code.sys', wraps=code.sys, spec=code.sys)
        self.sysmod = stack.enter_context(prepatch)
        jeżeli sys.excepthook jest sys.__excepthook__:
            self.sysmod.excepthook = self.sysmod.__excepthook__

    def test_ps1(self):
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact()
        self.assertEqual(self.sysmod.ps1, '>>> ')

    def test_ps2(self):
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact()
        self.assertEqual(self.sysmod.ps2, '... ')

    def test_console_stderr(self):
        self.infunc.side_effect = ["'antioch'", "", EOFError('Finished')]
        self.console.interact()
        dla call w list(self.stdout.method_calls):
            jeżeli 'antioch' w ''.join(call[1]):
                przerwij
        inaczej:
            podnieś AssertionError("no console stdout")

    def test_syntax_error(self):
        self.infunc.side_effect = ["undefined", EOFError('Finished')]
        self.console.interact()
        dla call w self.stderr.method_calls:
            jeżeli 'NameError' w ''.join(call[1]):
                przerwij
        inaczej:
            podnieś AssertionError("No syntax error z console")

    def test_sysexcepthook(self):
        self.infunc.side_effect = ["raise ValueError('')",
                                    EOFError('Finished')]
        hook = mock.Mock()
        self.sysmod.excepthook = hook
        self.console.interact()
        self.assertPrawda(hook.called)

    def test_banner(self):
        # przy banner
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact(banner='Foo')
        self.assertEqual(len(self.stderr.method_calls), 2)
        banner_call = self.stderr.method_calls[0]
        self.assertEqual(banner_call, ['write', ('Foo\n',), {}])

        # no banner
        self.stderr.reset_mock()
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact(banner='')
        self.assertEqual(len(self.stderr.method_calls), 1)

    def test_cause_tb(self):
        self.infunc.side_effect = ["raise ValueError('') z AttributeError",
                                    EOFError('Finished')]
        self.console.interact()
        output = ''.join(''.join(call[1]) dla call w self.stderr.method_calls)
        expected = dedent("""
        AttributeError

        The above exception was the direct cause of the following exception:

        Traceback (most recent call last):
          File "<console>", line 1, w <module>
        ValueError
        """)
        self.assertIn(expected, output)

    def test_context_tb(self):
        self.infunc.side_effect = ["spróbuj: ham\nwyjąwszy: eggs\n",
                                    EOFError('Finished')]
        self.console.interact()
        output = ''.join(''.join(call[1]) dla call w self.stderr.method_calls)
        expected = dedent("""
        Traceback (most recent call last):
          File "<console>", line 1, w <module>
        NameError: name 'ham' jest nie defined

        During handling of the above exception, another exception occurred:

        Traceback (most recent call last):
          File "<console>", line 2, w <module>
        NameError: name 'eggs' jest nie defined
        """)
        self.assertIn(expected, output)


jeżeli __name__ == "__main__":
    unittest.main()
