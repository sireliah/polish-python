"""
Python unit testing framework, based on Erich Gamma's JUnit oraz Kent Beck's
Smalltalk testing framework.

This module contains the core framework classes that form the basis of
specific test cases oraz suites (TestCase, TestSuite etc.), oraz also a
text-based utility klasa dla running the tests oraz reporting the results
 (TextTestRunner).

Simple usage:

    zaimportuj unittest

    klasa IntegerArithmeticTestCase(unittest.TestCase):
        def testAdd(self):  ## test method names begin 'test*'
            self.assertEqual((1 + 2), 3)
            self.assertEqual(0 + 1, 1)
        def testMultiply(self):
            self.assertEqual((0 * 10), 0)
            self.assertEqual((5 * 8), 40)

    jeżeli __name__ == '__main__':
        unittest.main()

Further information jest available w the bundled documentation, oraz from

  http://docs.python.org/library/unittest.html

Copyright (c) 1999-2003 Steve Purcell
Copyright (c) 2003-2010 Python Software Foundation
This module jest free software, oraz you may redistribute it and/or modify
it under the same terms jako Python itself, so long jako this copyright message
and disclaimer are retained w their original form.

IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
"""

__all__ = ['TestResult', 'TestCase', 'TestSuite',
           'TextTestRunner', 'TestLoader', 'FunctionTestCase', 'main',
           'defaultTestLoader', 'SkipTest', 'skip', 'skipIf', 'skipUnless',
           'expectedFailure', 'TextTestResult', 'installHandler',
           'registerResult', 'removeResult', 'removeHandler']

# Expose obsolete functions dla backwards compatibility
__all__.extend(['getTestCaseNames', 'makeSuite', 'findTestCases'])

__unittest = Prawda

z .result zaimportuj TestResult
z .case zaimportuj (TestCase, FunctionTestCase, SkipTest, skip, skipIf,
                   skipUnless, expectedFailure)
z .suite zaimportuj BaseTestSuite, TestSuite
z .loader zaimportuj (TestLoader, defaultTestLoader, makeSuite, getTestCaseNames,
                     findTestCases)
z .main zaimportuj TestProgram, main
z .runner zaimportuj TextTestRunner, TextTestResult
z .signals zaimportuj installHandler, registerResult, removeResult, removeHandler

# deprecated
_TextTestResult = TextTestResult

# There are no tests here, so don't try to run anything discovered from
# introspecting the symbols (e.g. FunctionTestCase). Instead, all our
# tests come z within unittest.test.
def load_tests(loader, tests, pattern):
    zaimportuj os.path
    # top level directory cached on loader instance
    this_dir = os.path.dirname(__file__)
    zwróć loader.discover(start_dir=this_dir, pattern=pattern)
