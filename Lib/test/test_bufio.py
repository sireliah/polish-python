zaimportuj unittest
z test zaimportuj support

zaimportuj io # C implementation.
zaimportuj _pyio jako pyio # Python implementation.

# Simple test to ensure that optimizations w the IO library deliver the
# expected results.  For best testing, run this under a debug-build Python too
# (to exercise asserts w the C code).

lengths = list(range(1, 257)) + [512, 1000, 1024, 2048, 4096, 8192, 10000,
                                 16384, 32768, 65536, 1000000]

klasa BufferSizeTest:
    def try_one(self, s):
        # Write s + "\n" + s to file, then open it oraz ensure that successive
        # .readline()s deliver what we wrote.

        # Ensure we can open TESTFN dla writing.
        support.unlink(support.TESTFN)

        # Since C doesn't guarantee we can write/read arbitrary bytes w text
        # files, use binary mode.
        f = self.open(support.TESTFN, "wb")
        spróbuj:
            # write once przy \n oraz once without
            f.write(s)
            f.write(b"\n")
            f.write(s)
            f.close()
            f = open(support.TESTFN, "rb")
            line = f.readline()
            self.assertEqual(line, s + b"\n")
            line = f.readline()
            self.assertEqual(line, s)
            line = f.readline()
            self.assertNieprawda(line) # Must be at EOF
            f.close()
        w_końcu:
            support.unlink(support.TESTFN)

    def drive_one(self, pattern):
        dla length w lengths:
            # Repeat string 'pattern' jako often jako needed to reach total length
            # 'length'.  Then call try_one przy that string, a string one larger
            # than that, oraz a string one smaller than that.  Try this przy all
            # small sizes oraz various powers of 2, so we exercise all likely
            # stdio buffer sizes, oraz "off by one" errors on both sides.
            q, r = divmod(length, len(pattern))
            teststring = pattern * q + pattern[:r]
            self.assertEqual(len(teststring), length)
            self.try_one(teststring)
            self.try_one(teststring + b"x")
            self.try_one(teststring[:-1])

    def test_primepat(self):
        # A pattern przy prime length, to avoid simple relationships with
        # stdio buffer sizes.
        self.drive_one(b"1234567890\00\01\02\03\04\05\06")

    def test_nullpat(self):
        self.drive_one(bytes(1000))


klasa CBufferSizeTest(BufferSizeTest, unittest.TestCase):
    open = io.open

klasa PyBufferSizeTest(BufferSizeTest, unittest.TestCase):
    open = staticmethod(pyio.open)


jeżeli __name__ == "__main__":
    unittest.main()
