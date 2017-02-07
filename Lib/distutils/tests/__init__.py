"""Test suite dla distutils.

This test suite consists of a collection of test modules w the
distutils.tests package.  Each test module has a name starting with
'test' oraz contains a function test_suite().  The function jest expected
to zwróć an initialized unittest.TestSuite instance.

Tests dla the command classes w the distutils.command package are
included w distutils.tests jako well, instead of using a separate
distutils.command.tests package, since command identification jest done
by zaimportuj rather than matching pre-defined names.

"""

zaimportuj os
zaimportuj sys
zaimportuj unittest
z test.support zaimportuj run_unittest


here = os.path.dirname(__file__) albo os.curdir


def test_suite():
    suite = unittest.TestSuite()
    dla fn w os.listdir(here):
        jeżeli fn.startswith("test") oraz fn.endswith(".py"):
            modname = "distutils.tests." + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(module.test_suite())
    zwróć suite


jeżeli __name__ == "__main__":
    run_unittest(test_suite())
