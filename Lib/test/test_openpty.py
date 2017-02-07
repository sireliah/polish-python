# Test to see jeżeli openpty works. (But don't worry jeżeli it isn't available.)

zaimportuj os, unittest

jeżeli nie hasattr(os, "openpty"):
    podnieś unittest.SkipTest("os.openpty() nie available.")


klasa OpenptyTest(unittest.TestCase):
    def test(self):
        master, slave = os.openpty()
        self.addCleanup(os.close, master)
        self.addCleanup(os.close, slave)
        jeżeli nie os.isatty(slave):
            self.fail("Slave-end of pty jest nie a terminal.")

        os.write(slave, b'Ping!')
        self.assertEqual(os.read(master, 1024), b'Ping!')

jeżeli __name__ == '__main__':
    unittest.main()
