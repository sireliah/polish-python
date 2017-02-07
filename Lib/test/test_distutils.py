"""Tests dla distutils.

The tests dla distutils are defined w the distutils.tests package;
the test_suite() function there returns a test suite that's ready to
be run.
"""

zaimportuj distutils.tests
zaimportuj test.support


def test_main():
    test.support.run_unittest(distutils.tests.test_suite())
    test.support.reap_children()


jeżeli __name__ == "__main__":
    test_main()
