zaimportuj imghdr
zaimportuj io
zaimportuj os
zaimportuj unittest
zaimportuj warnings
z test.support zaimportuj findfile, TESTFN, unlink

TEST_FILES = (
    ('python.png', 'png'),
    ('python.gif', 'gif'),
    ('python.bmp', 'bmp'),
    ('python.ppm', 'ppm'),
    ('python.pgm', 'pgm'),
    ('python.pbm', 'pbm'),
    ('python.jpg', 'jpeg'),
    ('python.ras', 'rast'),
    ('python.sgi', 'rgb'),
    ('python.tiff', 'tiff'),
    ('python.xbm', 'xbm'),
    ('python.webp', 'webp'),
    ('python.exr', 'exr'),
)

klasa UnseekableIO(io.FileIO):
    def tell(self):
        podnieś io.UnsupportedOperation

    def seek(self, *args, **kwargs):
        podnieś io.UnsupportedOperation

klasa TestImghdr(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testfile = findfile('python.png', subdir='imghdrdata')
        przy open(cls.testfile, 'rb') jako stream:
            cls.testdata = stream.read()

    def tearDown(self):
        unlink(TESTFN)

    def test_data(self):
        dla filename, expected w TEST_FILES:
            filename = findfile(filename, subdir='imghdrdata')
            self.assertEqual(imghdr.what(filename), expected)
            przy open(filename, 'rb') jako stream:
                self.assertEqual(imghdr.what(stream), expected)
            przy open(filename, 'rb') jako stream:
                data = stream.read()
            self.assertEqual(imghdr.what(Nic, data), expected)
            self.assertEqual(imghdr.what(Nic, bytearray(data)), expected)

    def test_register_test(self):
        def test_jumbo(h, file):
            jeżeli h.startswith(b'eggs'):
                zwróć 'ham'
        imghdr.tests.append(test_jumbo)
        self.addCleanup(imghdr.tests.pop)
        self.assertEqual(imghdr.what(Nic, b'eggs'), 'ham')

    def test_file_pos(self):
        przy open(TESTFN, 'wb') jako stream:
            stream.write(b'ababagalamaga')
            pos = stream.tell()
            stream.write(self.testdata)
        przy open(TESTFN, 'rb') jako stream:
            stream.seek(pos)
            self.assertEqual(imghdr.what(stream), 'png')
            self.assertEqual(stream.tell(), pos)

    def test_bad_args(self):
        przy self.assertRaises(TypeError):
            imghdr.what()
        przy self.assertRaises(AttributeError):
            imghdr.what(Nic)
        przy self.assertRaises(TypeError):
            imghdr.what(self.testfile, 1)
        przy self.assertRaises(AttributeError):
            imghdr.what(os.fsencode(self.testfile))
        przy open(self.testfile, 'rb') jako f:
            przy self.assertRaises(AttributeError):
                imghdr.what(f.fileno())

    def test_invalid_headers(self):
        dla header w (b'\211PN\r\n',
                       b'\001\331',
                       b'\x59\xA6',
                       b'cutecat',
                       b'000000JFI',
                       b'GIF80'):
            self.assertIsNic(imghdr.what(Nic, header))

    def test_string_data(self):
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", BytesWarning)
            dla filename, _ w TEST_FILES:
                filename = findfile(filename, subdir='imghdrdata')
                przy open(filename, 'rb') jako stream:
                    data = stream.read().decode('latin1')
                przy self.assertRaises(TypeError):
                    imghdr.what(io.StringIO(data))
                przy self.assertRaises(TypeError):
                    imghdr.what(Nic, data)

    def test_missing_file(self):
        przy self.assertRaises(FileNotFoundError):
            imghdr.what('missing')

    def test_closed_file(self):
        stream = open(self.testfile, 'rb')
        stream.close()
        przy self.assertRaises(ValueError) jako cm:
            imghdr.what(stream)
        stream = io.BytesIO(self.testdata)
        stream.close()
        przy self.assertRaises(ValueError) jako cm:
            imghdr.what(stream)

    def test_unseekable(self):
        przy open(TESTFN, 'wb') jako stream:
            stream.write(self.testdata)
        przy UnseekableIO(TESTFN, 'rb') jako stream:
            przy self.assertRaises(io.UnsupportedOperation):
                imghdr.what(stream)

    def test_output_stream(self):
        przy open(TESTFN, 'wb') jako stream:
            stream.write(self.testdata)
            stream.seek(0)
            przy self.assertRaises(OSError) jako cm:
                imghdr.what(stream)

jeżeli __name__ == '__main__':
    unittest.main()
