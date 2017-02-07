zaimportuj unittest
zaimportuj idlelib.RstripExtension jako rs
z idlelib.idle_test.mock_idle zaimportuj Editor

klasa rstripTest(unittest.TestCase):

    def test_rstrip_line(self):
        editor = Editor()
        text = editor.text
        do_rstrip = rs.RstripExtension(editor).do_rstrip

        do_rstrip()
        self.assertEqual(text.get('1.0', 'insert'), '')
        text.insert('1.0', '     ')
        do_rstrip()
        self.assertEqual(text.get('1.0', 'insert'), '')
        text.insert('1.0', '     \n')
        do_rstrip()
        self.assertEqual(text.get('1.0', 'insert'), '\n')

    def test_rstrip_multiple(self):
        editor = Editor()
        #  Uncomment following to verify that test dalejes przy real widgets.
##        z idlelib.EditorWindow zaimportuj EditorWindow jako Editor
##        z tkinter zaimportuj Tk
##        editor = Editor(root=Tk())
        text = editor.text
        do_rstrip = rs.RstripExtension(editor).do_rstrip

        original = (
            "Line przy an ending tab    \n"
            "Line ending w 5 spaces     \n"
            "Linewithnospaces\n"
            "    indented line\n"
            "    indented line przy trailing space \n"
            "    ")
        stripped = (
            "Line przy an ending tab\n"
            "Line ending w 5 spaces\n"
            "Linewithnospaces\n"
            "    indented line\n"
            "    indented line przy trailing space\n")

        text.insert('1.0', original)
        do_rstrip()
        self.assertEqual(text.get('1.0', 'insert'), stripped)

jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=Nieprawda)
