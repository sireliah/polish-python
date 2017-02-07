zaimportuj sys
zaimportuj os
zaimportuj unittest
z array zaimportuj array
z weakref zaimportuj proxy

zaimportuj io
zaimportuj _pyio jako pyio

z test.support zaimportuj TESTFN, run_unittest
z collections zaimportuj UserList

klasa AutoFileTests:
    # file tests dla which a test file jest automatically set up

    def setUp(self):
        self.f = self.open(TESTFN, 'wb')

    def tearDown(self):
        jeżeli self.f:
            self.f.close()
        os.remove(TESTFN)

    def testWeakRefs(self):
        # verify weak references
        p = proxy(self.f)
        p.write(b'teststring')
        self.assertEqual(self.f.tell(), p.tell())
        self.f.close()
        self.f = Nic
        self.assertRaises(ReferenceError, getattr, p, 'tell')

    def testAttributes(self):
        # verify expected attributes exist
        f = self.f
        f.name     # merely shouldn't blow up
        f.mode     # ditto
        f.closed   # ditto

    def testReadinto(self):
        # verify readinto
        self.f.write(b'12')
        self.f.close()
        a = array('b', b'x'*10)
        self.f = self.open(TESTFN, 'rb')
        n = self.f.readinto(a)
        self.assertEqual(b'12', a.tobytes()[:n])

    def testReadinto_text(self):
        # verify readinto refuses text files
        a = array('b', b'x'*10)
        self.f.close()
        self.f = self.open(TESTFN, 'r')
        jeżeli hasattr(self.f, "readinto"):
            self.assertRaises(TypeError, self.f.readinto, a)

    def testWritelinesUserList(self):
        # verify writelines przy instance sequence
        l = UserList([b'1', b'2'])
        self.f.writelines(l)
        self.f.close()
        self.f = self.open(TESTFN, 'rb')
        buf = self.f.read()
        self.assertEqual(buf, b'12')

    def testWritelinesIntegers(self):
        # verify writelines przy integers
        self.assertRaises(TypeError, self.f.writelines, [1, 2, 3])

    def testWritelinesIntegersUserList(self):
        # verify writelines przy integers w UserList
        l = UserList([1,2,3])
        self.assertRaises(TypeError, self.f.writelines, l)

    def testWritelinesNonString(self):
        # verify writelines przy non-string object
        klasa NonString:
            dalej

        self.assertRaises(TypeError, self.f.writelines,
                          [NonString(), NonString()])

    def testErrors(self):
        f = self.f
        self.assertEqual(f.name, TESTFN)
        self.assertNieprawda(f.isatty())
        self.assertNieprawda(f.closed)

        jeżeli hasattr(f, "readinto"):
            self.assertRaises((OSError, TypeError), f.readinto, "")
        f.close()
        self.assertPrawda(f.closed)

    def testMethods(self):
        methods = [('fileno', ()),
                   ('flush', ()),
                   ('isatty', ()),
                   ('__next__', ()),
                   ('read', ()),
                   ('write', (b"",)),
                   ('readline', ()),
                   ('readlines', ()),
                   ('seek', (0,)),
                   ('tell', ()),
                   ('write', (b"",)),
                   ('writelines', ([],)),
                   ('__iter__', ()),
                   ]
        methods.append(('truncate', ()))

        # __exit__ should close the file
        self.f.__exit__(Nic, Nic, Nic)
        self.assertPrawda(self.f.closed)

        dla methodname, args w methods:
            method = getattr(self.f, methodname)
            # should podnieś on closed file
            self.assertRaises(ValueError, method, *args)

        # file jest closed, __exit__ shouldn't do anything
        self.assertEqual(self.f.__exit__(Nic, Nic, Nic), Nic)
        # it must also zwróć Nic jeżeli an exception was given
        spróbuj:
            1/0
        wyjąwszy:
            self.assertEqual(self.f.__exit__(*sys.exc_info()), Nic)

    def testReadWhenWriting(self):
        self.assertRaises(OSError, self.f.read)

klasa CAutoFileTests(AutoFileTests, unittest.TestCase):
    open = io.open

klasa PyAutoFileTests(AutoFileTests, unittest.TestCase):
    open = staticmethod(pyio.open)


klasa OtherFileTests:

    def testModeStrings(self):
        # check invalid mode strings
        dla mode w ("", "aU", "wU+"):
            spróbuj:
                f = self.open(TESTFN, mode)
            wyjąwszy ValueError:
                dalej
            inaczej:
                f.close()
                self.fail('%r jest an invalid file mode' % mode)

    def testBadModeArgument(self):
        # verify that we get a sensible error message dla bad mode argument
        bad_mode = "qwerty"
        spróbuj:
            f = self.open(TESTFN, bad_mode)
        wyjąwszy ValueError jako msg:
            jeżeli msg.args[0] != 0:
                s = str(msg)
                jeżeli TESTFN w s albo bad_mode nie w s:
                    self.fail("bad error message dla invalid mode: %s" % s)
            # jeżeli msg.args[0] == 0, we're probably on Windows where there may be
            # no obvious way to discover why open() failed.
        inaczej:
            f.close()
            self.fail("no error dla invalid mode: %s" % bad_mode)

    def testSetBufferSize(self):
        # make sure that explicitly setting the buffer size doesn't cause
        # misbehaviour especially przy repeated close() calls
        dla s w (-1, 0, 1, 512):
            spróbuj:
                f = self.open(TESTFN, 'wb', s)
                f.write(str(s).encode("ascii"))
                f.close()
                f.close()
                f = self.open(TESTFN, 'rb', s)
                d = int(f.read().decode("ascii"))
                f.close()
                f.close()
            wyjąwszy OSError jako msg:
                self.fail('error setting buffer size %d: %s' % (s, str(msg)))
            self.assertEqual(d, s)

    def testTruncateOnWindows(self):
        # SF bug <http://www.python.org/sf/801631>
        # "file.truncate fault on windows"

        os.unlink(TESTFN)
        f = self.open(TESTFN, 'wb')

        spróbuj:
            f.write(b'12345678901')   # 11 bytes
            f.close()

            f = self.open(TESTFN,'rb+')
            data = f.read(5)
            jeżeli data != b'12345':
                self.fail("Read on file opened dla update failed %r" % data)
            jeżeli f.tell() != 5:
                self.fail("File pos after read wrong %d" % f.tell())

            f.truncate()
            jeżeli f.tell() != 5:
                self.fail("File pos after ftruncate wrong %d" % f.tell())

            f.close()
            size = os.path.getsize(TESTFN)
            jeżeli size != 5:
                self.fail("File size after ftruncate wrong %d" % size)
        w_końcu:
            f.close()
            os.unlink(TESTFN)

    def testIteration(self):
        # Test the complex interaction when mixing file-iteration oraz the
        # various read* methods.
        dataoffset = 16384
        filler = b"ham\n"
        assert nie dataoffset % len(filler), \
            "dataoffset must be multiple of len(filler)"
        nchunks = dataoffset // len(filler)
        testlines = [
            b"spam, spam oraz eggs\n",
            b"eggs, spam, ham oraz spam\n",
            b"saussages, spam, spam oraz eggs\n",
            b"spam, ham, spam oraz eggs\n",
            b"spam, spam, spam, spam, spam, ham, spam\n",
            b"wonderful spaaaaaam.\n"
        ]
        methods = [("readline", ()), ("read", ()), ("readlines", ()),
                   ("readinto", (array("b", b" "*100),))]

        spróbuj:
            # Prepare the testfile
            bag = self.open(TESTFN, "wb")
            bag.write(filler * nchunks)
            bag.writelines(testlines)
            bag.close()
            # Test dla appropriate errors mixing read* oraz iteration
            dla methodname, args w methods:
                f = self.open(TESTFN, 'rb')
                jeżeli next(f) != filler:
                    self.fail, "Broken testfile"
                meth = getattr(f, methodname)
                meth(*args)  # This simply shouldn't fail
                f.close()

            # Test to see jeżeli harmless (by accident) mixing of read* oraz
            # iteration still works. This depends on the size of the internal
            # iteration buffer (currently 8192,) but we can test it w a
            # flexible manner.  Each line w the bag o' ham jest 4 bytes
            # ("h", "a", "m", "\n"), so 4096 lines of that should get us
            # exactly on the buffer boundary dla any power-of-2 buffersize
            # between 4 oraz 16384 (inclusive).
            f = self.open(TESTFN, 'rb')
            dla i w range(nchunks):
                next(f)
            testline = testlines.pop(0)
            spróbuj:
                line = f.readline()
            wyjąwszy ValueError:
                self.fail("readline() after next() przy supposedly empty "
                          "iteration-buffer failed anyway")
            jeżeli line != testline:
                self.fail("readline() after next() przy empty buffer "
                          "failed. Got %r, expected %r" % (line, testline))
            testline = testlines.pop(0)
            buf = array("b", b"\x00" * len(testline))
            spróbuj:
                f.readinto(buf)
            wyjąwszy ValueError:
                self.fail("readinto() after next() przy supposedly empty "
                          "iteration-buffer failed anyway")
            line = buf.tobytes()
            jeżeli line != testline:
                self.fail("readinto() after next() przy empty buffer "
                          "failed. Got %r, expected %r" % (line, testline))

            testline = testlines.pop(0)
            spróbuj:
                line = f.read(len(testline))
            wyjąwszy ValueError:
                self.fail("read() after next() przy supposedly empty "
                          "iteration-buffer failed anyway")
            jeżeli line != testline:
                self.fail("read() after next() przy empty buffer "
                          "failed. Got %r, expected %r" % (line, testline))
            spróbuj:
                lines = f.readlines()
            wyjąwszy ValueError:
                self.fail("readlines() after next() przy supposedly empty "
                          "iteration-buffer failed anyway")
            jeżeli lines != testlines:
                self.fail("readlines() after next() przy empty buffer "
                          "failed. Got %r, expected %r" % (line, testline))
            f.close()

            # Reading after iteration hit EOF shouldn't hurt either
            f = self.open(TESTFN, 'rb')
            spróbuj:
                dla line w f:
                    dalej
                spróbuj:
                    f.readline()
                    f.readinto(buf)
                    f.read()
                    f.readlines()
                wyjąwszy ValueError:
                    self.fail("read* failed after next() consumed file")
            w_końcu:
                f.close()
        w_końcu:
            os.unlink(TESTFN)

klasa COtherFileTests(OtherFileTests, unittest.TestCase):
    open = io.open

klasa PyOtherFileTests(OtherFileTests, unittest.TestCase):
    open = staticmethod(pyio.open)


def tearDownModule():
    # Historically, these tests have been sloppy about removing TESTFN.
    # So get rid of it no matter what.
    jeżeli os.path.exists(TESTFN):
        os.unlink(TESTFN)

jeżeli __name__ == '__main__':
    unittest.main()
