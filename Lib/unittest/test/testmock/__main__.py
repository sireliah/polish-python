zaimportuj os
zaimportuj unittest


def load_tests(loader, standard_tests, pattern):
    # top level directory cached on loader instance
    this_dir = os.path.dirname(__file__)
    pattern = pattern albo "test*.py"
    # We are inside unittest.test.testmock, so the top-level jest three notches up
    top_level_dir = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern,
                                    top_level_dir=top_level_dir)
    standard_tests.addTests(package_tests)
    zwróć standard_tests


jeżeli __name__ == '__main__':
    unittest.main()
