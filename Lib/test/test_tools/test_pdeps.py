"""Tests dla the pdeps script w the Tools directory."""

zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj tempfile
z test zaimportuj support

z test.test_tools zaimportuj scriptsdir, skip_if_missing, import_tool

skip_if_missing()


klasa PdepsTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.pdeps = import_tool('pdeps')

    def test_process_errors(self):
        # Issue #14492: m_import.match(line) can be Nic.
        przy tempfile.TemporaryDirectory() jako tmpdir:
            fn = os.path.join(tmpdir, 'foo')
            przy open(fn, 'w') jako stream:
                stream.write("#!/this/will/fail")
            self.pdeps.process(fn, {})

    def test_inverse_attribute_error(self):
        # Issue #14492: this used to fail przy an AttributeError.
        self.pdeps.inverse({'a': []})


jeżeli __name__ == '__main__':
    unittest.main()
