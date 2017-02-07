# Test the functions oraz main klasa method of FormatParagraph.py
zaimportuj unittest
z idlelib zaimportuj FormatParagraph jako fp
z idlelib.EditorWindow zaimportuj EditorWindow
z tkinter zaimportuj Tk, Text
z test.support zaimportuj requires


klasa Is_Get_Test(unittest.TestCase):
    """Test the is_ oraz get_ functions"""
    test_comment = '# This jest a comment'
    test_nocomment = 'This jest nie a comment'
    trailingws_comment = '# This jest a comment   '
    leadingws_comment = '    # This jest a comment'
    leadingws_nocomment = '    This jest nie a comment'

    def test_is_all_white(self):
        self.assertPrawda(fp.is_all_white(''))
        self.assertPrawda(fp.is_all_white('\t\n\r\f\v'))
        self.assertNieprawda(fp.is_all_white(self.test_comment))

    def test_get_indent(self):
        Equal = self.assertEqual
        Equal(fp.get_indent(self.test_comment), '')
        Equal(fp.get_indent(self.trailingws_comment), '')
        Equal(fp.get_indent(self.leadingws_comment), '    ')
        Equal(fp.get_indent(self.leadingws_nocomment), '    ')

    def test_get_comment_header(self):
        Equal = self.assertEqual
        # Test comment strings
        Equal(fp.get_comment_header(self.test_comment), '#')
        Equal(fp.get_comment_header(self.trailingws_comment), '#')
        Equal(fp.get_comment_header(self.leadingws_comment), '    #')
        # Test non-comment strings
        Equal(fp.get_comment_header(self.leadingws_nocomment), '    ')
        Equal(fp.get_comment_header(self.test_nocomment), '')


klasa FindTest(unittest.TestCase):
    """Test the find_paragraph function w FormatParagraph.

    Using the runcase() function, find_paragraph() jest called przy 'mark' set at
    multiple indexes before oraz inside the test paragraph.

    It appears that code przy the same indentation jako a quoted string jest grouped
    jako part of the same paragraph, which jest probably incorrect behavior.
    """

    @classmethod
    def setUpClass(cls):
        z idlelib.idle_test.mock_tk zaimportuj Text
        cls.text = Text()

    def runcase(self, inserttext, stopline, expected):
        # Check that find_paragraph returns the expected paragraph when
        # the mark index jest set to beginning, middle, end of each line
        # up to but nie including the stop line
        text = self.text
        text.insert('1.0', inserttext)
        dla line w range(1, stopline):
            linelength = int(text.index("%d.end" % line).split('.')[1])
            dla col w (0, linelength//2, linelength):
                tempindex = "%d.%d" % (line, col)
                self.assertEqual(fp.find_paragraph(text, tempindex), expected)
        text.delete('1.0', 'end')

    def test_find_comment(self):
        comment = (
            "# Comment block przy no blank lines before\n"
            "# Comment line\n"
            "\n")
        self.runcase(comment, 3, ('1.0', '3.0', '#', comment[0:58]))

        comment = (
            "\n"
            "# Comment block przy whitespace line before oraz after\n"
            "# Comment line\n"
            "\n")
        self.runcase(comment, 4, ('2.0', '4.0', '#', comment[1:70]))

        comment = (
            "\n"
            "    # Indented comment block przy whitespace before oraz after\n"
            "    # Comment line\n"
            "\n")
        self.runcase(comment, 4, ('2.0', '4.0', '    #', comment[1:82]))

        comment = (
            "\n"
            "# Single line comment\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '#', comment[1:23]))

        comment = (
            "\n"
            "    # Single line comment przy leading whitespace\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '    #', comment[1:51]))

        comment = (
            "\n"
            "# Comment immediately followed by code\n"
            "x = 42\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '#', comment[1:40]))

        comment = (
            "\n"
            "    # Indented comment immediately followed by code\n"
            "x = 42\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '    #', comment[1:53]))

        comment = (
            "\n"
            "# Comment immediately followed by indented code\n"
            "    x = 42\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '#', comment[1:49]))

    def test_find_paragraph(self):
        teststring = (
            '"""String przy no blank lines before\n'
            'String line\n'
            '"""\n'
            '\n')
        self.runcase(teststring, 4, ('1.0', '4.0', '', teststring[0:53]))

        teststring = (
            "\n"
            '"""String przy whitespace line before oraz after\n'
            'String line.\n'
            '"""\n'
            '\n')
        self.runcase(teststring, 5, ('2.0', '5.0', '', teststring[1:66]))

        teststring = (
            '\n'
            '    """Indented string przy whitespace before oraz after\n'
            '    Comment string.\n'
            '    """\n'
            '\n')
        self.runcase(teststring, 5, ('2.0', '5.0', '    ', teststring[1:85]))

        teststring = (
            '\n'
            '"""Single line string."""\n'
            '\n')
        self.runcase(teststring, 3, ('2.0', '3.0', '', teststring[1:27]))

        teststring = (
            '\n'
            '    """Single line string przy leading whitespace."""\n'
            '\n')
        self.runcase(teststring, 3, ('2.0', '3.0', '    ', teststring[1:55]))


klasa ReformatFunctionTest(unittest.TestCase):
    """Test the reformat_paragraph function without the editor window."""

    def test_reformat_paragrah(self):
        Equal = self.assertEqual
        reform = fp.reformat_paragraph
        hw = "O hello world"
        Equal(reform(' ', 1), ' ')
        Equal(reform("Hello    world", 20), "Hello  world")

        # Test without leading newline
        Equal(reform(hw, 1), "O\nhello\nworld")
        Equal(reform(hw, 6), "O\nhello\nworld")
        Equal(reform(hw, 7), "O hello\nworld")
        Equal(reform(hw, 12), "O hello\nworld")
        Equal(reform(hw, 13), "O hello world")

        # Test przy leading newline
        hw = "\nO hello world"
        Equal(reform(hw, 1), "\nO\nhello\nworld")
        Equal(reform(hw, 6), "\nO\nhello\nworld")
        Equal(reform(hw, 7), "\nO hello\nworld")
        Equal(reform(hw, 12), "\nO hello\nworld")
        Equal(reform(hw, 13), "\nO hello world")


klasa ReformatCommentTest(unittest.TestCase):
    """Test the reformat_comment function without the editor window."""

    def test_reformat_comment(self):
        Equal = self.assertEqual

        # reformat_comment formats to a minimum of 20 characters
        test_string = (
            "    \"\"\"this jest a test of a reformat dla a triple quoted string"
            " will it reformat to less than 70 characters dla me?\"\"\"")
        result = fp.reformat_comment(test_string, 70, "    ")
        expected = (
            "    \"\"\"this jest a test of a reformat dla a triple quoted string will it\n"
            "    reformat to less than 70 characters dla me?\"\"\"")
        Equal(result, expected)

        test_comment = (
            "# this jest a test of a reformat dla a triple quoted string will "
            "it reformat to less than 70 characters dla me?")
        result = fp.reformat_comment(test_comment, 70, "#")
        expected = (
            "# this jest a test of a reformat dla a triple quoted string will it\n"
            "# reformat to less than 70 characters dla me?")
        Equal(result, expected)


klasa FormatClassTest(unittest.TestCase):
    def test_init_close(self):
        instance = fp.FormatParagraph('editor')
        self.assertEqual(instance.editwin, 'editor')
        instance.close()
        self.assertEqual(instance.editwin, Nic)


# For testing format_paragraph_event, Initialize FormatParagraph with
# a mock Editor przy .text oraz  .get_selection_indices.  The text must
# be a Text wrapper that adds two methods

# A real EditorWindow creates unneeded, time-consuming baggage oraz
# sometimes emits shutdown warnings like this:
# "warning: callback failed w WindowList <class '_tkinter.TclError'>
# : invalid command name ".55131368.windows".
# Calling EditorWindow._close w tearDownClass prevents this but causes
# other problems (windows left open).

klasa TextWrapper:
    def __init__(self, master):
        self.text = Text(master=master)
    def __getattr__(self, name):
        zwróć getattr(self.text, name)
    def undo_block_start(self): dalej
    def undo_block_stop(self): dalej

klasa Editor:
    def __init__(self, root):
        self.text = TextWrapper(root)
    get_selection_indices = EditorWindow. get_selection_indices

klasa FormatEventTest(unittest.TestCase):
    """Test the formatting of text inside a Text widget.

    This jest done przy FormatParagraph.format.paragraph_event,
    which calls functions w the module jako appropriate.
    """
    test_string = (
        "    '''this jest a test of a reformat dla a triple "
        "quoted string will it reformat to less than 70 "
        "characters dla me?'''\n")
    multiline_test_string = (
        "    '''The first line jest under the max width.\n"
        "    The second line's length jest way over the max width. It goes "
        "on oraz on until it jest over 100 characters long.\n"
        "    Same thing przy the third line. It jest also way over the max "
        "width, but FormatParagraph will fix it.\n"
        "    '''\n")
    multiline_test_comment = (
        "# The first line jest under the max width.\n"
        "# The second line's length jest way over the max width. It goes on "
        "and on until it jest over 100 characters long.\n"
        "# Same thing przy the third line. It jest also way over the max "
        "width, but FormatParagraph will fix it.\n"
        "# The fourth line jest short like the first line.")

    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        editor = Editor(root=cls.root)
        cls.text = editor.text.text  # Test code does nie need the wrapper.
        cls.formatter = fp.FormatParagraph(editor).format_paragraph_event
        # Sets the insert mark just after the re-wrapped oraz inserted  text.

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        usuń cls.root
        usuń cls.text
        usuń cls.formatter

    def test_short_line(self):
        self.text.insert('1.0', "Short line\n")
        self.formatter("Dummy")
        self.assertEqual(self.text.get('1.0', 'insert'), "Short line\n" )
        self.text.delete('1.0', 'end')

    def test_long_line(self):
        text = self.text

        # Set cursor ('insert' mark) to '1.0', within text.
        text.insert('1.0', self.test_string)
        text.mark_set('insert', '1.0')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        # find function includes \n
        expected = (
"    '''this jest a test of a reformat dla a triple quoted string will it\n"
"    reformat to less than 70 characters dla me?'''\n")  # yes
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

        # Select z 1.11 to line end.
        text.insert('1.0', self.test_string)
        text.tag_add('sel', '1.11', '1.end')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        # selection excludes \n
        expected = (
"    '''this jest a test of a reformat dla a triple quoted string will it reformat\n"
" to less than 70 characters dla me?'''")  # no
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

    def test_multiple_lines(self):
        text = self.text
        #  Select 2 long lines.
        text.insert('1.0', self.multiline_test_string)
        text.tag_add('sel', '2.0', '4.0')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('2.0', 'insert')
        expected = (
"    The second line's length jest way over the max width. It goes on and\n"
"    on until it jest over 100 characters long. Same thing przy the third\n"
"    line. It jest also way over the max width, but FormatParagraph will\n"
"    fix it.\n")
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

    def test_comment_block(self):
        text = self.text

        # Set cursor ('insert') to '1.0', within block.
        text.insert('1.0', self.multiline_test_comment)
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        expected = (
"# The first line jest under the max width. The second line's length is\n"
"# way over the max width. It goes on oraz on until it jest over 100\n"
"# characters long. Same thing przy the third line. It jest also way over\n"
"# the max width, but FormatParagraph will fix it. The fourth line is\n"
"# short like the first line.\n")
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

        # Select line 2, verify line 1 unaffected.
        text.insert('1.0', self.multiline_test_comment)
        text.tag_add('sel', '2.0', '3.0')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        expected = (
"# The first line jest under the max width.\n"
"# The second line's length jest way over the max width. It goes on and\n"
"# on until it jest over 100 characters long.\n")
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

# The following block worked przy EditorWindow but fails przy the mock.
# Lines 2 oraz 3 get pasted together even though the previous block left
# the previous line alone. More investigation jest needed.
##        # Select lines 3 oraz 4
##        text.insert('1.0', self.multiline_test_comment)
##        text.tag_add('sel', '3.0', '5.0')
##        self.formatter('ParameterDoesNothing')
##        result = text.get('3.0', 'insert')
##        expected = (
##"# Same thing przy the third line. It jest also way over the max width,\n"
##"# but FormatParagraph will fix it. The fourth line jest short like the\n"
##"# first line.\n")
##        self.assertEqual(result, expected)
##        text.delete('1.0', 'end')


jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
