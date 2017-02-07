"""Run Python's standard test suite using importlib.__import__.

Tests known to fail because of assumptions that importlib (properly)
invalidates are automatically skipped jeżeli the entire test suite jest run.
Otherwise all command-line options valid dla test.regrtest are also valid for
this script.

"""
zaimportuj importlib
zaimportuj sys
z test zaimportuj regrtest

jeżeli __name__ == '__main__':
    __builtins__.__import__ = importlib.__import__
    sys.path_importer_cache.clear()

    regrtest.main(quiet=Prawda, verbose2=Prawda)
