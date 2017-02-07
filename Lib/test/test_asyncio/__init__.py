zaimportuj os
z test.support zaimportuj load_package_tests, import_module

# Skip tests jeżeli we don't have threading.
import_module('threading')
# Skip tests jeżeli we don't have concurrent.futures.
import_module('concurrent.futures')

def load_tests(*args):
    zwróć load_package_tests(os.path.dirname(__file__), *args)
