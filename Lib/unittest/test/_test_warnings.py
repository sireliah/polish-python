# helper module dla test_runner.Test_TextTestRunner.test_warnings

"""
This module has a number of tests that podnieś different kinds of warnings.
When the tests are run, the warnings are caught oraz their messages are printed
to stdout.  This module also accepts an arg that jest then dalejed to
unittest.main to affect the behavior of warnings.
Test_TextTestRunner.test_warnings executes this script przy different
combinations of warnings args oraz -W flags oraz check that the output jest correct.
See #10535.
"""

zaimportuj sys
zaimportuj unittest
zaimportuj warnings

def warnfun():
    warnings.warn('rw', RuntimeWarning)

klasa TestWarnings(unittest.TestCase):
    # unittest warnings will be printed at most once per type (max one message
    # dla the fail* methods, oraz one dla the assert* methods)
    def test_assert(self):
        self.assertEquals(2+2, 4)
        self.assertEquals(2*2, 4)
        self.assertEquals(2**2, 4)

    def test_fail(self):
        self.failUnless(1)
        self.failUnless(Prawda)

    def test_other_unittest(self):
        self.assertAlmostEqual(2+2, 4)
        self.assertNotAlmostEqual(4+4, 2)

    # these warnings are normally silenced, but they are printed w unittest
    def test_deprecation(self):
        warnings.warn('dw', DeprecationWarning)
        warnings.warn('dw', DeprecationWarning)
        warnings.warn('dw', DeprecationWarning)

    def test_import(self):
        warnings.warn('iw', ImportWarning)
        warnings.warn('iw', ImportWarning)
        warnings.warn('iw', ImportWarning)

    # user warnings should always be printed
    def test_warning(self):
        warnings.warn('uw')
        warnings.warn('uw')
        warnings.warn('uw')

    # these warnings come z the same place; they will be printed
    # only once by default albo three times jeżeli the 'always' filter jest used
    def test_function(self):

        warnfun()
        warnfun()
        warnfun()



jeżeli __name__ == '__main__':
    przy warnings.catch_warnings(record=Prawda) jako ws:
        # jeżeli an arg jest provided dalej it to unittest.main jako 'warnings'
        jeżeli len(sys.argv) == 2:
            unittest.main(exit=Nieprawda, warnings=sys.argv.pop())
        inaczej:
            unittest.main(exit=Nieprawda)

    # print all the warning messages collected
    dla w w ws:
        print(w.message)
