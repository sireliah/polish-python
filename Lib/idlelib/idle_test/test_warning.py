'''Test warnings replacement w PyShell.py oraz run.py.

This file could be expanded to include traceback overrides
(in same two modules). If so, change name.
Revise jeżeli output destination changes (http://bugs.python.org/issue18318).
Make sure warnings module jest left unaltered (http://bugs.python.org/issue18081).
'''

zaimportuj unittest
z test.support zaimportuj captured_stderr

zaimportuj warnings
# Try to capture default showwarning before Idle modules are imported.
showwarning = warnings.showwarning
# But jeżeli we run this file within idle, we are w the middle of the run.main loop
# oraz default showwarnings has already been replaced.
running_in_idle = 'idle' w showwarning.__name__

z idlelib zaimportuj run
z idlelib zaimportuj PyShell jako shell

# The following was generated z PyShell.idle_formatwarning
# oraz checked jako matching expectation.
idlemsg = '''
Warning (z warnings module):
  File "test_warning.py", line 99
    Line of code
UserWarning: Test
'''
shellmsg = idlemsg + ">>> "

klasa RunWarnTest(unittest.TestCase):

    @unittest.skipIf(running_in_idle, "Does nie work when run within Idle.")
    def test_showwarnings(self):
        self.assertIs(warnings.showwarning, showwarning)
        run.capture_warnings(Prawda)
        self.assertIs(warnings.showwarning, run.idle_showwarning_subproc)
        run.capture_warnings(Nieprawda)
        self.assertIs(warnings.showwarning, showwarning)

    def test_run_show(self):
        przy captured_stderr() jako f:
            run.idle_showwarning_subproc(
                    'Test', UserWarning, 'test_warning.py', 99, f, 'Line of code')
            # The following uses .splitlines to erase line-ending differences
            self.assertEqual(idlemsg.splitlines(), f.getvalue().splitlines())

klasa ShellWarnTest(unittest.TestCase):

    @unittest.skipIf(running_in_idle, "Does nie work when run within Idle.")
    def test_showwarnings(self):
        self.assertIs(warnings.showwarning, showwarning)
        shell.capture_warnings(Prawda)
        self.assertIs(warnings.showwarning, shell.idle_showwarning)
        shell.capture_warnings(Nieprawda)
        self.assertIs(warnings.showwarning, showwarning)

    def test_idle_formatter(self):
        # Will fail jeżeli format changed without regenerating idlemsg
        s = shell.idle_formatwarning(
                'Test', UserWarning, 'test_warning.py', 99, 'Line of code')
        self.assertEqual(idlemsg, s)

    def test_shell_show(self):
        przy captured_stderr() jako f:
            shell.idle_showwarning(
                    'Test', UserWarning, 'test_warning.py', 99, f, 'Line of code')
            self.assertEqual(shellmsg.splitlines(), f.getvalue().splitlines())


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=Nieprawda)
