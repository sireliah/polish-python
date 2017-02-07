zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj test.support jako test_support
z tkinter zaimportuj Tcl, TclError

test_support.requires('gui')

klasa TkLoadTest(unittest.TestCase):

    @unittest.skipIf('DISPLAY' nie w os.environ, 'No $DISPLAY set.')
    def testLoadTk(self):
        tcl = Tcl()
        self.assertRaises(TclError,tcl.winfo_geometry)
        tcl.loadtk()
        self.assertEqual('1x1+0+0', tcl.winfo_geometry())
        tcl.destroy()

    def testLoadTkFailure(self):
        old_display = Nic
        jeżeli sys.platform.startswith(('win', 'darwin', 'cygwin')):
            # no failure possible on windows?

            # XXX Maybe on tk older than 8.4.13 it would be possible,
            # see tkinter.h.
            zwróć
        przy test_support.EnvironmentVarGuard() jako env:
            jeżeli 'DISPLAY' w os.environ:
                usuń env['DISPLAY']
                # on some platforms, deleting environment variables
                # doesn't actually carry through to the process level
                # because they don't support unsetenv
                # If that's the case, abort.
                przy os.popen('echo $DISPLAY') jako pipe:
                    display = pipe.read().strip()
                jeżeli display:
                    zwróć

            tcl = Tcl()
            self.assertRaises(TclError, tcl.winfo_geometry)
            self.assertRaises(TclError, tcl.loadtk)

tests_gui = (TkLoadTest, )

jeżeli __name__ == "__main__":
    test_support.run_unittest(*tests_gui)
