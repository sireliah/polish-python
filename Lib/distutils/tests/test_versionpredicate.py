"""Tests harness dla distutils.versionpredicate.

"""

zaimportuj distutils.versionpredicate
zaimportuj doctest
z test.support zaimportuj run_unittest

def test_suite():
    zwróć doctest.DocTestSuite(distutils.versionpredicate)

jeżeli __name__ == '__main__':
    run_unittest(test_suite())
