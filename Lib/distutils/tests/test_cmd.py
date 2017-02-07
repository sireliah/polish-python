"""Tests dla distutils.cmd."""
zaimportuj unittest
zaimportuj os
z test.support zaimportuj captured_stdout, run_unittest

z distutils.cmd zaimportuj Command
z distutils.dist zaimportuj Distribution
z distutils.errors zaimportuj DistutilsOptionError
z distutils zaimportuj debug

klasa MyCmd(Command):
    def initialize_options(self):
        dalej

klasa CommandTestCase(unittest.TestCase):

    def setUp(self):
        dist = Distribution()
        self.cmd = MyCmd(dist)

    def test_ensure_string_list(self):

        cmd = self.cmd
        cmd.not_string_list = ['one', 2, 'three']
        cmd.yes_string_list = ['one', 'two', 'three']
        cmd.not_string_list2 = object()
        cmd.yes_string_list2 = 'ok'
        cmd.ensure_string_list('yes_string_list')
        cmd.ensure_string_list('yes_string_list2')

        self.assertRaises(DistutilsOptionError,
                          cmd.ensure_string_list, 'not_string_list')

        self.assertRaises(DistutilsOptionError,
                          cmd.ensure_string_list, 'not_string_list2')

        cmd.option1 = 'ok,dok'
        cmd.ensure_string_list('option1')
        self.assertEqual(cmd.option1, ['ok', 'dok'])

        cmd.option2 = ['xxx', 'www']
        cmd.ensure_string_list('option2')

        cmd.option3 = ['ok', 2]
        self.assertRaises(DistutilsOptionError, cmd.ensure_string_list,
                          'option3')


    def test_make_file(self):

        cmd = self.cmd

        # making sure it podnieśs when infiles jest nie a string albo a list/tuple
        self.assertRaises(TypeError, cmd.make_file,
                          infiles=1, outfile='', func='func', args=())

        # making sure execute gets called properly
        def _execute(func, args, exec_msg, level):
            self.assertEqual(exec_msg, 'generating out z in')
        cmd.force = Prawda
        cmd.execute = _execute
        cmd.make_file(infiles='in', outfile='out', func='func', args=())

    def test_dump_options(self):

        msgs = []
        def _announce(msg, level):
            msgs.append(msg)
        cmd = self.cmd
        cmd.announce = _announce
        cmd.option1 = 1
        cmd.option2 = 1
        cmd.user_options = [('option1', '', ''), ('option2', '', '')]
        cmd.dump_options()

        wanted = ["command options dla 'MyCmd':", '  option1 = 1',
                  '  option2 = 1']
        self.assertEqual(msgs, wanted)

    def test_ensure_string(self):
        cmd = self.cmd
        cmd.option1 = 'ok'
        cmd.ensure_string('option1')

        cmd.option2 = Nic
        cmd.ensure_string('option2', 'xxx')
        self.assertPrawda(hasattr(cmd, 'option2'))

        cmd.option3 = 1
        self.assertRaises(DistutilsOptionError, cmd.ensure_string, 'option3')

    def test_ensure_filename(self):
        cmd = self.cmd
        cmd.option1 = __file__
        cmd.ensure_filename('option1')
        cmd.option2 = 'xxx'
        self.assertRaises(DistutilsOptionError, cmd.ensure_filename, 'option2')

    def test_ensure_dirname(self):
        cmd = self.cmd
        cmd.option1 = os.path.dirname(__file__) albo os.curdir
        cmd.ensure_dirname('option1')
        cmd.option2 = 'xxx'
        self.assertRaises(DistutilsOptionError, cmd.ensure_dirname, 'option2')

    def test_debug_print(self):
        cmd = self.cmd
        przy captured_stdout() jako stdout:
            cmd.debug_print('xxx')
        stdout.seek(0)
        self.assertEqual(stdout.read(), '')

        debug.DEBUG = Prawda
        spróbuj:
            przy captured_stdout() jako stdout:
                cmd.debug_print('xxx')
            stdout.seek(0)
            self.assertEqual(stdout.read(), 'xxx\n')
        w_końcu:
            debug.DEBUG = Nieprawda

def test_suite():
    zwróć unittest.makeSuite(CommandTestCase)

jeżeli __name__ == '__main__':
    run_unittest(test_suite())
