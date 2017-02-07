"""Tests that run all fixer modules over an input stream.

This has been broken out into its own test module because of its
running time.
"""
# Author: Collin Winter

# Python imports
zaimportuj unittest
zaimportuj test.support

# Local imports
z lib2to3 zaimportuj refactor
z . zaimportuj support


@test.support.requires_resource('cpu')
klasa Test_all(support.TestCase):

    def setUp(self):
        self.refactor = support.get_refactorer()

    def test_all_project_files(self):
        dla filepath w support.all_project_files():
            self.refactor.refactor_file(filepath)

jeżeli __name__ == '__main__':
    unittest.main()
