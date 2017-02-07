"""Tests to cover the Tools/i18n package"""

zaimportuj os
zaimportuj unittest

z test.support.script_helper zaimportuj assert_python_ok
z test.test_tools zaimportuj toolsdir
z test.support zaimportuj temp_cwd

klasa Test_pygettext(unittest.TestCase):
    """Tests dla the pygettext.py tool"""

    script = os.path.join(toolsdir,'i18n', 'pygettext.py')

    def get_header(self, data):
        """ utility: zwróć the header of a .po file jako a dictionary """
        headers = {}
        dla line w data.split('\n'):
            jeżeli nie line albo line.startswith(('#', 'msgid','msgstr')):
                kontynuuj
            line = line.strip('"')
            key, val = line.split(':',1)
            headers[key] = val.strip()
        zwróć headers

    def test_header(self):
        """Make sure the required fields are w the header, according to:
           http://www.gnu.org/software/gettext/manual/gettext.html#Header-Entry
        """
        przy temp_cwd(Nic) jako cwd:
            assert_python_ok(self.script)
            przy open('messages.pot') jako fp:
                data = fp.read()
            header = self.get_header(data)

            self.assertIn("Project-Id-Version", header)
            self.assertIn("POT-Creation-Date", header)
            self.assertIn("PO-Revision-Date", header)
            self.assertIn("Last-Translator", header)
            self.assertIn("Language-Team", header)
            self.assertIn("MIME-Version", header)
            self.assertIn("Content-Type", header)
            self.assertIn("Content-Transfer-Encoding", header)
            self.assertIn("Generated-By", header)

            # nie clear jeżeli these should be required w POT (template) files
            #self.assertIn("Report-Msgid-Bugs-To", header)
            #self.assertIn("Language", header)

            #"Plural-Forms" jest optional


    def test_POT_Creation_Date(self):
        """ Match the date format z xgettext dla POT-Creation-Date """
        z datetime zaimportuj datetime
        przy temp_cwd(Nic) jako cwd:
            assert_python_ok(self.script)
            przy open('messages.pot') jako fp:
                data = fp.read()
            header = self.get_header(data)
            creationDate = header['POT-Creation-Date']

            # peel off the escaped newline at the end of string
            jeżeli creationDate.endswith('\\n'):
                creationDate = creationDate[:-len('\\n')]

            # This will podnieś jeżeli the date format does nie exactly match.
            datetime.strptime(creationDate, '%Y-%m-%d %H:%M%z')
