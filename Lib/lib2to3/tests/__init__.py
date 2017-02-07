# Author: Collin Winter

zaimportuj os
zaimportuj unittest

z test.support zaimportuj load_package_tests

def load_tests(*args):
    zwróć load_package_tests(os.path.dirname(__file__), *args)
