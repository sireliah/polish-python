zaimportuj unittest.test

z test zaimportuj support


def test_main():
    # used by regrtest
    support.run_unittest(unittest.test.suite())
    support.reap_children()

def load_tests(*_):
    # used by unittest
    zwróć unittest.test.suite()

jeżeli __name__ == "__main__":
    test_main()
