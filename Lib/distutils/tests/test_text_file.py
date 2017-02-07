"""Tests dla distutils.text_file."""
zaimportuj os
zaimportuj unittest
z distutils.text_file zaimportuj TextFile
z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest

TEST_DATA = """# test file

line 3 \\
# intervening comment
  continues on next line
"""

klasa TextFileTestCase(support.TempdirManager, unittest.TestCase):

    def test_class(self):
        # old tests moved z text_file.__main__
        # so they are really called by the buildbots

        # result 1: no fancy options
        result1 = ['# test file\n', '\n', 'line 3 \\\n',
                   '# intervening comment\n',
                   '  continues on next line\n']

        # result 2: just strip comments
        result2 = ["\n",
                   "line 3 \\\n",
                   "  continues on next line\n"]

        # result 3: just strip blank lines
        result3 = ["# test file\n",
                   "line 3 \\\n",
                   "# intervening comment\n",
                   "  continues on next line\n"]

        # result 4: default, strip comments, blank lines,
        # oraz trailing whitespace
        result4 = ["line 3 \\",
                   "  continues on next line"]

        # result 5: strip comments oraz blanks, plus join lines (but don't
        # "collapse" joined lines
        result5 = ["line 3   continues on next line"]

        # result 6: strip comments oraz blanks, plus join lines (and
        # "collapse" joined lines
        result6 = ["line 3 continues on next line"]

        def test_input(count, description, file, expected_result):
            result = file.readlines()
            self.assertEqual(result, expected_result)

        tmpdir = self.mkdtemp()
        filename = os.path.join(tmpdir, "test.txt")
        out_file = open(filename, "w")
        spróbuj:
            out_file.write(TEST_DATA)
        w_końcu:
            out_file.close()

        in_file = TextFile(filename, strip_comments=0, skip_blanks=0,
                           lstrip_ws=0, rstrip_ws=0)
        spróbuj:
            test_input(1, "no processing", in_file, result1)
        w_końcu:
            in_file.close()

        in_file = TextFile(filename, strip_comments=1, skip_blanks=0,
                           lstrip_ws=0, rstrip_ws=0)
        spróbuj:
            test_input(2, "strip comments", in_file, result2)
        w_końcu:
            in_file.close()

        in_file = TextFile(filename, strip_comments=0, skip_blanks=1,
                           lstrip_ws=0, rstrip_ws=0)
        spróbuj:
            test_input(3, "strip blanks", in_file, result3)
        w_końcu:
            in_file.close()

        in_file = TextFile(filename)
        spróbuj:
            test_input(4, "default processing", in_file, result4)
        w_końcu:
            in_file.close()

        in_file = TextFile(filename, strip_comments=1, skip_blanks=1,
                           join_lines=1, rstrip_ws=1)
        spróbuj:
            test_input(5, "join lines without collapsing", in_file, result5)
        w_końcu:
            in_file.close()

        in_file = TextFile(filename, strip_comments=1, skip_blanks=1,
                           join_lines=1, rstrip_ws=1, collapse_join=1)
        spróbuj:
            test_input(6, "join lines przy collapsing", in_file, result6)
        w_końcu:
            in_file.close()

def test_suite():
    zwróć unittest.makeSuite(TextFileTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
