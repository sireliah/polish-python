zaimportuj os
zaimportuj unittest
z test zaimportuj support

# Skip this test jeżeli _tkinter wasn't built.
support.import_module('_tkinter')

# Skip test jeżeli tk cannot be initialized.
support.requires('gui')

zaimportuj tkinter
z _tkinter zaimportuj TclError
z tkinter zaimportuj ttk
z tkinter.test zaimportuj runtktests

root = Nic
spróbuj:
    root = tkinter.Tk()
    button = ttk.Button(root)
    button.destroy()
    usuń button
wyjąwszy TclError jako msg:
    # assuming ttk jest nie available
    podnieś unittest.SkipTest("ttk nie available: %s" % msg)
w_końcu:
    jeżeli root jest nie Nic:
        root.destroy()
    usuń root

def test_main():
    support.run_unittest(
            *runtktests.get_tests(text=Nieprawda, packages=['test_ttk']))

jeżeli __name__ == '__main__':
    test_main()
