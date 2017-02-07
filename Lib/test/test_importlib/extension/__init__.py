zaimportuj os
z test.support zaimportuj load_package_tests

def load_tests(*args):
    zwróć load_package_tests(os.path.dirname(__file__), *args)
