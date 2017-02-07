zaimportuj pipes
zaimportuj os
zaimportuj string
zaimportuj unittest
z test.support zaimportuj TESTFN, run_unittest, unlink, reap_children

jeżeli os.name != 'posix':
    podnieś unittest.SkipTest('pipes module only works on posix')

TESTFN2 = TESTFN + "2"

# tr a-z A-Z jest nie portable, so make the ranges explicit
s_command = 'tr %s %s' % (string.ascii_lowercase, string.ascii_uppercase)

klasa SimplePipeTests(unittest.TestCase):
    def tearDown(self):
        dla f w (TESTFN, TESTFN2):
            unlink(f)

    def testSimplePipe1(self):
        t = pipes.Template()
        t.append(s_command, pipes.STDIN_STDOUT)
        f = t.open(TESTFN, 'w')
        f.write('hello world #1')
        f.close()
        przy open(TESTFN) jako f:
            self.assertEqual(f.read(), 'HELLO WORLD #1')

    def testSimplePipe2(self):
        przy open(TESTFN, 'w') jako f:
            f.write('hello world #2')
        t = pipes.Template()
        t.append(s_command + ' < $IN > $OUT', pipes.FILEIN_FILEOUT)
        t.copy(TESTFN, TESTFN2)
        przy open(TESTFN2) jako f:
            self.assertEqual(f.read(), 'HELLO WORLD #2')

    def testSimplePipe3(self):
        przy open(TESTFN, 'w') jako f:
            f.write('hello world #2')
        t = pipes.Template()
        t.append(s_command + ' < $IN', pipes.FILEIN_STDOUT)
        f = t.open(TESTFN, 'r')
        spróbuj:
            self.assertEqual(f.read(), 'HELLO WORLD #2')
        w_końcu:
            f.close()

    def testEmptyPipeline1(self):
        # copy through empty pipe
        d = 'empty pipeline test COPY'
        przy open(TESTFN, 'w') jako f:
            f.write(d)
        przy open(TESTFN2, 'w') jako f:
            f.write('')
        t=pipes.Template()
        t.copy(TESTFN, TESTFN2)
        przy open(TESTFN2) jako f:
            self.assertEqual(f.read(), d)

    def testEmptyPipeline2(self):
        # read through empty pipe
        d = 'empty pipeline test READ'
        przy open(TESTFN, 'w') jako f:
            f.write(d)
        t=pipes.Template()
        f = t.open(TESTFN, 'r')
        spróbuj:
            self.assertEqual(f.read(), d)
        w_końcu:
            f.close()

    def testEmptyPipeline3(self):
        # write through empty pipe
        d = 'empty pipeline test WRITE'
        t = pipes.Template()
        przy t.open(TESTFN, 'w') jako f:
            f.write(d)
        przy open(TESTFN) jako f:
            self.assertEqual(f.read(), d)

    def testRepr(self):
        t = pipes.Template()
        self.assertEqual(repr(t), "<Template instance, steps=[]>")
        t.append('tr a-z A-Z', pipes.STDIN_STDOUT)
        self.assertEqual(repr(t),
                    "<Template instance, steps=[('tr a-z A-Z', '--')]>")

    def testSetDebug(self):
        t = pipes.Template()
        t.debug(Nieprawda)
        self.assertEqual(t.debugging, Nieprawda)
        t.debug(Prawda)
        self.assertEqual(t.debugging, Prawda)

    def testReadOpenSink(self):
        # check calling open('r') on a pipe ending with
        # a sink podnieśs ValueError
        t = pipes.Template()
        t.append('boguscmd', pipes.SINK)
        self.assertRaises(ValueError, t.open, 'bogusfile', 'r')

    def testWriteOpenSource(self):
        # check calling open('w') on a pipe ending with
        # a source podnieśs ValueError
        t = pipes.Template()
        t.prepend('boguscmd', pipes.SOURCE)
        self.assertRaises(ValueError, t.open, 'bogusfile', 'w')

    def testBadAppendOptions(self):
        t = pipes.Template()

        # try a non-string command
        self.assertRaises(TypeError, t.append, 7, pipes.STDIN_STDOUT)

        # try a type that isn't recognized
        self.assertRaises(ValueError, t.append, 'boguscmd', 'xx')

        # shouldn't be able to append a source
        self.assertRaises(ValueError, t.append, 'boguscmd', pipes.SOURCE)

        # check appending two sinks
        t = pipes.Template()
        t.append('boguscmd', pipes.SINK)
        self.assertRaises(ValueError, t.append, 'boguscmd', pipes.SINK)

        # command needing file input but przy no $IN
        t = pipes.Template()
        self.assertRaises(ValueError, t.append, 'boguscmd $OUT',
                           pipes.FILEIN_FILEOUT)
        t = pipes.Template()
        self.assertRaises(ValueError, t.append, 'boguscmd',
                           pipes.FILEIN_STDOUT)

        # command needing file output but przy no $OUT
        t = pipes.Template()
        self.assertRaises(ValueError, t.append, 'boguscmd $IN',
                           pipes.FILEIN_FILEOUT)
        t = pipes.Template()
        self.assertRaises(ValueError, t.append, 'boguscmd',
                           pipes.STDIN_FILEOUT)


    def testBadPrependOptions(self):
        t = pipes.Template()

        # try a non-string command
        self.assertRaises(TypeError, t.prepend, 7, pipes.STDIN_STDOUT)

        # try a type that isn't recognized
        self.assertRaises(ValueError, t.prepend, 'tr a-z A-Z', 'xx')

        # shouldn't be able to prepend a sink
        self.assertRaises(ValueError, t.prepend, 'boguscmd', pipes.SINK)

        # check prepending two sources
        t = pipes.Template()
        t.prepend('boguscmd', pipes.SOURCE)
        self.assertRaises(ValueError, t.prepend, 'boguscmd', pipes.SOURCE)

        # command needing file input but przy no $IN
        t = pipes.Template()
        self.assertRaises(ValueError, t.prepend, 'boguscmd $OUT',
                           pipes.FILEIN_FILEOUT)
        t = pipes.Template()
        self.assertRaises(ValueError, t.prepend, 'boguscmd',
                           pipes.FILEIN_STDOUT)

        # command needing file output but przy no $OUT
        t = pipes.Template()
        self.assertRaises(ValueError, t.prepend, 'boguscmd $IN',
                           pipes.FILEIN_FILEOUT)
        t = pipes.Template()
        self.assertRaises(ValueError, t.prepend, 'boguscmd',
                           pipes.STDIN_FILEOUT)

    def testBadOpenMode(self):
        t = pipes.Template()
        self.assertRaises(ValueError, t.open, 'bogusfile', 'x')

    def testClone(self):
        t = pipes.Template()
        t.append('tr a-z A-Z', pipes.STDIN_STDOUT)

        u = t.clone()
        self.assertNotEqual(id(t), id(u))
        self.assertEqual(t.steps, u.steps)
        self.assertNotEqual(id(t.steps), id(u.steps))
        self.assertEqual(t.debugging, u.debugging)

def test_main():
    run_unittest(SimplePipeTests)
    reap_children()

jeżeli __name__ == "__main__":
    test_main()
