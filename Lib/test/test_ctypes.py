zaimportuj unittest
z test.support zaimportuj import_module

ctypes_test = import_module('ctypes.test')

load_tests = ctypes_test.load_tests

jeżeli __name__ == "__main__":
    unittest.main()
