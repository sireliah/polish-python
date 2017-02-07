"""Basic tests dla os.popen()

  Particularly useful dla platforms that fake popen.
"""

zaimportuj unittest
z test zaimportuj support
zaimportuj os, sys

# Test that command-lines get down jako we expect.
# To do this we execute:
#    python -c "zaimportuj sys;print(sys.argv)" {rest_of_commandline}
# This results w Python being spawned oraz printing the sys.argv list.
# We can then eval() the result of this, oraz see what each argv was.
python = sys.executable
jeżeli ' ' w python:
    python = '"' + python + '"'     # quote embedded space dla cmdline

klasa PopenTest(unittest.TestCase):

    def _do_test_commandline(self, cmdline, expected):
        cmd = '%s -c "zaimportuj sys; print(sys.argv)" %s'
        cmd = cmd % (python, cmdline)
        przy os.popen(cmd) jako p:
            data = p.read()
        got = eval(data)[1:] # strip off argv[0]
        self.assertEqual(got, expected)

    def test_popen(self):
        self.assertRaises(TypeError, os.popen)
        self._do_test_commandline(
            "foo bar",
            ["foo", "bar"]
        )
        self._do_test_commandline(
            'foo "spam oraz eggs" "silly walk"',
            ["foo", "spam oraz eggs", "silly walk"]
        )
        self._do_test_commandline(
            'foo "a \\"quoted\\" arg" bar',
            ["foo", 'a "quoted" arg', "bar"]
        )
        support.reap_children()

    def test_return_code(self):
        self.assertEqual(os.popen("exit 0").close(), Nic)
        jeżeli os.name == 'nt':
            self.assertEqual(os.popen("exit 42").close(), 42)
        inaczej:
            self.assertEqual(os.popen("exit 42").close(), 42 << 8)

    def test_contextmanager(self):
        przy os.popen("echo hello") jako f:
            self.assertEqual(f.read(), "hello\n")

    def test_iterating(self):
        przy os.popen("echo hello") jako f:
            self.assertEqual(list(f), ["hello\n"])

jeżeli __name__ == "__main__":
    unittest.main()
