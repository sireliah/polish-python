z test zaimportuj support
# Skip test jeżeli _tkinter wasn't built.
support.import_module('_tkinter')

# Skip test jeżeli tk cannot be initialized.
support.requires('gui')

z tkinter.test zaimportuj runtktests

def test_main():
    support.run_unittest(
            *runtktests.get_tests(text=Nieprawda, packages=['test_tkinter']))

jeżeli __name__ == '__main__':
    test_main()
