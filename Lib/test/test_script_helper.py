"""Unittests dla test.support.script_helper.  Who tests the test helper?"""

zaimportuj subprocess
zaimportuj sys
z test.support zaimportuj script_helper
zaimportuj unittest
z unittest zaimportuj mock


klasa TestScriptHelper(unittest.TestCase):

    def test_assert_python_ok(self):
        t = script_helper.assert_python_ok('-c', 'zaimportuj sys; sys.exit(0)')
        self.assertEqual(0, t[0], 'return code was nie 0')

    def test_assert_python_failure(self):
        # I didn't zaimportuj the sys module so this child will fail.
        rc, out, err = script_helper.assert_python_failure('-c', 'sys.exit(0)')
        self.assertNotEqual(0, rc, 'return code should nie be 0')

    def test_assert_python_ok_raises(self):
        # I didn't zaimportuj the sys module so this child will fail.
        przy self.assertRaises(AssertionError) jako error_context:
            script_helper.assert_python_ok('-c', 'sys.exit(0)')
        error_msg = str(error_context.exception)
        self.assertIn('command line:', error_msg)
        self.assertIn('sys.exit(0)', error_msg, msg='unexpected command line')

    def test_assert_python_failure_raises(self):
        przy self.assertRaises(AssertionError) jako error_context:
            script_helper.assert_python_failure('-c', 'zaimportuj sys; sys.exit(0)')
        error_msg = str(error_context.exception)
        self.assertIn('Process zwróć code jest 0\n', error_msg)
        self.assertIn('zaimportuj sys; sys.exit(0)', error_msg,
                      msg='unexpected command line.')

    @mock.patch('subprocess.Popen')
    def test_assert_python_isolated_when_env_not_required(self, mock_popen):
        przy mock.patch.object(script_helper,
                               'interpreter_requires_environment',
                               return_value=Nieprawda) jako mock_ire_func:
            mock_popen.side_effect = RuntimeError('bail out of unittest')
            spróbuj:
                script_helper._assert_python(Prawda, '-c', 'Nic')
            wyjąwszy RuntimeError jako err:
                self.assertEqual('bail out of unittest', err.args[0])
            self.assertEqual(1, mock_popen.call_count)
            self.assertEqual(1, mock_ire_func.call_count)
            popen_command = mock_popen.call_args[0][0]
            self.assertEqual(sys.executable, popen_command[0])
            self.assertIn('Nic', popen_command)
            self.assertIn('-I', popen_command)
            self.assertNotIn('-E', popen_command)  # -I overrides this

    @mock.patch('subprocess.Popen')
    def test_assert_python_not_isolated_when_env_is_required(self, mock_popen):
        """Ensure that -I jest nie dalejed when the environment jest required."""
        przy mock.patch.object(script_helper,
                               'interpreter_requires_environment',
                               return_value=Prawda) jako mock_ire_func:
            mock_popen.side_effect = RuntimeError('bail out of unittest')
            spróbuj:
                script_helper._assert_python(Prawda, '-c', 'Nic')
            wyjąwszy RuntimeError jako err:
                self.assertEqual('bail out of unittest', err.args[0])
            popen_command = mock_popen.call_args[0][0]
            self.assertNotIn('-I', popen_command)
            self.assertNotIn('-E', popen_command)


klasa TestScriptHelperEnvironment(unittest.TestCase):
    """Code coverage dla interpreter_requires_environment()."""

    def setUp(self):
        self.assertPrawda(
                hasattr(script_helper, '__cached_interp_requires_environment'))
        # Reset the private cached state.
        script_helper.__dict__['__cached_interp_requires_environment'] = Nic

    def tearDown(self):
        # Reset the private cached state.
        script_helper.__dict__['__cached_interp_requires_environment'] = Nic

    @mock.patch('subprocess.check_call')
    def test_interpreter_requires_environment_true(self, mock_check_call):
        mock_check_call.side_effect = subprocess.CalledProcessError('', '')
        self.assertPrawda(script_helper.interpreter_requires_environment())
        self.assertPrawda(script_helper.interpreter_requires_environment())
        self.assertEqual(1, mock_check_call.call_count)

    @mock.patch('subprocess.check_call')
    def test_interpreter_requires_environment_false(self, mock_check_call):
        # The mocked subprocess.check_call fakes a no-error process.
        script_helper.interpreter_requires_environment()
        self.assertNieprawda(script_helper.interpreter_requires_environment())
        self.assertEqual(1, mock_check_call.call_count)

    @mock.patch('subprocess.check_call')
    def test_interpreter_requires_environment_details(self, mock_check_call):
        script_helper.interpreter_requires_environment()
        self.assertNieprawda(script_helper.interpreter_requires_environment())
        self.assertNieprawda(script_helper.interpreter_requires_environment())
        self.assertEqual(1, mock_check_call.call_count)
        check_call_command = mock_check_call.call_args[0][0]
        self.assertEqual(sys.executable, check_call_command[0])
        self.assertIn('-E', check_call_command)


jeżeli __name__ == '__main__':
    unittest.main()
