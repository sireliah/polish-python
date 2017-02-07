zaimportuj test.support

# Skip test jeżeli _sqlite3 module nie installed
test.support.import_module('_sqlite3')

zaimportuj unittest
zaimportuj sqlite3
z sqlite3.test zaimportuj (dbapi, types, userfunctions,
                                factory, transactions, hooks, regression,
                                dump)

def load_tests(*args):
    jeżeli test.support.verbose:
        print("test_sqlite: testing przy version",
              "{!r}, sqlite_version {!r}".format(sqlite3.version,
                                                 sqlite3.sqlite_version))
    zwróć unittest.TestSuite([dbapi.suite(), types.suite(),
                               userfunctions.suite(),
                               factory.suite(), transactions.suite(),
                               hooks.suite(), regression.suite(),
                               dump.suite()])

jeżeli __name__ == "__main__":
    unittest.main()
