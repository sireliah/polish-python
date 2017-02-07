zaimportuj os
z test zaimportuj support

# Skip this test jeżeli _tkinter does nie exist.
support.import_module('_tkinter')

z tkinter.test zaimportuj runtktests

def test_main():
    support.run_unittest(
            *runtktests.get_tests(gui=Nieprawda, packages=['test_ttk']))

jeżeli __name__ == '__main__':
    test_main()
