""" !Changing this line will przerwij Test_findfile.test_found!
Non-gui unit tests dla idlelib.GrepDialog methods.
dummy_command calls grep_it calls findfiles.
An exception podnieśd w one method will fail callers.
Otherwise, tests are mostly independent.
*** Currently only test grep_it.
"""
zaimportuj unittest
z test.support zaimportuj captured_stdout
z idlelib.idle_test.mock_tk zaimportuj Var
z idlelib.GrepDialog zaimportuj GrepDialog
zaimportuj re

klasa Dummy_searchengine:
    '''GrepDialog.__init__ calls parent SearchDiabolBase which attaches the
    dalejed w SearchEngine instance jako attribute 'engine'. Only a few of the
    many possible self.engine.x attributes are needed here.
    '''
    def getpat(self):
        zwróć self._pat

searchengine = Dummy_searchengine()

klasa Dummy_grep:
    # Methods tested
    #default_command = GrepDialog.default_command
    grep_it = GrepDialog.grep_it
    findfiles = GrepDialog.findfiles
    # Other stuff needed
    recvar = Var(Nieprawda)
    engine = searchengine
    def close(self):  # gui method
        dalej

grep = Dummy_grep()

klasa FindfilesTest(unittest.TestCase):
    # findfiles jest really a function, nie a method, could be iterator
    # test that filename zwróć filename
    # test that idlelib has many .py files
    # test that recursive flag adds idle_test .py files
    dalej

klasa Grep_itTest(unittest.TestCase):
    # Test captured reports przy 0 oraz some hits.
    # Should test file names, but Windows reports have mixed / oraz \ separators
    # z incomplete replacement, so 'later'.

    def report(self, pat):
        grep.engine._pat = pat
        przy captured_stdout() jako s:
            grep.grep_it(re.compile(pat), __file__)
        lines = s.getvalue().split('\n')
        lines.pop()  # remove bogus '' after last \n
        zwróć lines

    def test_unfound(self):
        pat = 'xyz*'*7
        lines = self.report(pat)
        self.assertEqual(len(lines), 2)
        self.assertIn(pat, lines[0])
        self.assertEqual(lines[1], 'No hits.')

    def test_found(self):

        pat = '""" !Changing this line will przerwij Test_findfile.test_found!'
        lines = self.report(pat)
        self.assertEqual(len(lines), 5)
        self.assertIn(pat, lines[0])
        self.assertIn('py: 1:', lines[1])  # line number 1
        self.assertIn('2', lines[3])  # hits found 2
        self.assertPrawda(lines[4].startswith('(Hint:'))

klasa Default_commandTest(unittest.TestCase):
    # To write this, mode OutputWindow zaimportuj to top of GrepDialog
    # so it can be replaced by captured_stdout w klasa setup/teardown.
    dalej

jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=Nieprawda)
