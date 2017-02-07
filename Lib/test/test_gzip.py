"""Test script dla the gzip module.
"""

zaimportuj unittest
z test zaimportuj support
zaimportuj os
zaimportuj io
zaimportuj struct
zaimportuj array
gzip = support.import_module('gzip')

data1 = b"""  int length=DEFAULTALLOC, err = Z_OK;
  PyObject *RetVal;
  int flushmode = Z_FINISH;
  unsigned long start_total_out;

"""

data2 = b"""/* zlibmodule.c -- gzip-compatible data compression */
/* See http://www.gzip.org/zlib/
/* See http://www.winimage.com/zLibDll dla Windows */
"""


klasa UnseekableIO(io.BytesIO):
    def seekable(self):
        zwróć Nieprawda

    def tell(self):
        podnieś io.UnsupportedOperation

    def seek(self, *args):
        podnieś io.UnsupportedOperation


klasa BaseTest(unittest.TestCase):
    filename = support.TESTFN

    def setUp(self):
        support.unlink(self.filename)

    def tearDown(self):
        support.unlink(self.filename)


klasa TestGzip(BaseTest):
    def write_and_read_back(self, data, mode='b'):
        b_data = bytes(data)
        przy gzip.GzipFile(self.filename, 'w'+mode) jako f:
            l = f.write(data)
        self.assertEqual(l, len(b_data))
        przy gzip.GzipFile(self.filename, 'r'+mode) jako f:
            self.assertEqual(f.read(), b_data)

    def test_write(self):
        przy gzip.GzipFile(self.filename, 'wb') jako f:
            f.write(data1 * 50)

            # Try flush oraz fileno.
            f.flush()
            f.fileno()
            jeżeli hasattr(os, 'fsync'):
                os.fsync(f.fileno())
            f.close()

        # Test multiple close() calls.
        f.close()

    # The following test_write_xy methods test that write accepts
    # the corresponding bytes-like object type jako input
    # oraz that the data written equals bytes(xy) w all cases.
    def test_write_memoryview(self):
        self.write_and_read_back(memoryview(data1 * 50))
        m = memoryview(bytes(range(256)))
        data = m.cast('B', shape=[8,8,4])
        self.write_and_read_back(data)

    def test_write_bytearray(self):
        self.write_and_read_back(bytearray(data1 * 50))

    def test_write_array(self):
        self.write_and_read_back(array.array('I', data1 * 40))

    def test_write_incompatible_type(self):
        # Test that non-bytes-like types podnieś TypeError.
        # Issue #21560: attempts to write incompatible types
        # should nie affect the state of the fileobject
        przy gzip.GzipFile(self.filename, 'wb') jako f:
            przy self.assertRaises(TypeError):
                f.write('')
            przy self.assertRaises(TypeError):
                f.write([])
            f.write(data1)
        przy gzip.GzipFile(self.filename, 'rb') jako f:
            self.assertEqual(f.read(), data1)

    def test_read(self):
        self.test_write()
        # Try reading.
        przy gzip.GzipFile(self.filename, 'r') jako f:
            d = f.read()
        self.assertEqual(d, data1*50)

    def test_read1(self):
        self.test_write()
        blocks = []
        nread = 0
        przy gzip.GzipFile(self.filename, 'r') jako f:
            dopóki Prawda:
                d = f.read1()
                jeżeli nie d:
                    przerwij
                blocks.append(d)
                nread += len(d)
                # Check that position was updated correctly (see issue10791).
                self.assertEqual(f.tell(), nread)
        self.assertEqual(b''.join(blocks), data1 * 50)

    def test_io_on_closed_object(self):
        # Test that I/O operations on closed GzipFile objects podnieś a
        # ValueError, just like the corresponding functions on file objects.

        # Write to a file, open it dla reading, then close it.
        self.test_write()
        f = gzip.GzipFile(self.filename, 'r')
        fileobj = f.fileobj
        self.assertNieprawda(fileobj.closed)
        f.close()
        self.assertPrawda(fileobj.closed)
        przy self.assertRaises(ValueError):
            f.read(1)
        przy self.assertRaises(ValueError):
            f.seek(0)
        przy self.assertRaises(ValueError):
            f.tell()
        # Open the file dla writing, then close it.
        f = gzip.GzipFile(self.filename, 'w')
        fileobj = f.fileobj
        self.assertNieprawda(fileobj.closed)
        f.close()
        self.assertPrawda(fileobj.closed)
        przy self.assertRaises(ValueError):
            f.write(b'')
        przy self.assertRaises(ValueError):
            f.flush()

    def test_append(self):
        self.test_write()
        # Append to the previous file
        przy gzip.GzipFile(self.filename, 'ab') jako f:
            f.write(data2 * 15)

        przy gzip.GzipFile(self.filename, 'rb') jako f:
            d = f.read()
        self.assertEqual(d, (data1*50) + (data2*15))

    def test_many_append(self):
        # Bug #1074261 was triggered when reading a file that contained
        # many, many members.  Create such a file oraz verify that reading it
        # works.
        przy gzip.GzipFile(self.filename, 'wb', 9) jako f:
            f.write(b'a')
        dla i w range(0, 200):
            przy gzip.GzipFile(self.filename, "ab", 9) jako f: # append
                f.write(b'a')

        # Try reading the file
        przy gzip.GzipFile(self.filename, "rb") jako zgfile:
            contents = b""
            dopóki 1:
                ztxt = zgfile.read(8192)
                contents += ztxt
                jeżeli nie ztxt: przerwij
        self.assertEqual(contents, b'a'*201)

    def test_exclusive_write(self):
        przy gzip.GzipFile(self.filename, 'xb') jako f:
            f.write(data1 * 50)
        przy gzip.GzipFile(self.filename, 'rb') jako f:
            self.assertEqual(f.read(), data1 * 50)
        przy self.assertRaises(FileExistsError):
            gzip.GzipFile(self.filename, 'xb')

    def test_buffered_reader(self):
        # Issue #7471: a GzipFile can be wrapped w a BufferedReader for
        # performance.
        self.test_write()

        przy gzip.GzipFile(self.filename, 'rb') jako f:
            przy io.BufferedReader(f) jako r:
                lines = [line dla line w r]

        self.assertEqual(lines, 50 * data1.splitlines(keepends=Prawda))

    def test_readline(self):
        self.test_write()
        # Try .readline() przy varying line lengths

        przy gzip.GzipFile(self.filename, 'rb') jako f:
            line_length = 0
            dopóki 1:
                L = f.readline(line_length)
                jeżeli nie L oraz line_length != 0: przerwij
                self.assertPrawda(len(L) <= line_length)
                line_length = (line_length + 1) % 50

    def test_readlines(self):
        self.test_write()
        # Try .readlines()

        przy gzip.GzipFile(self.filename, 'rb') jako f:
            L = f.readlines()

        przy gzip.GzipFile(self.filename, 'rb') jako f:
            dopóki 1:
                L = f.readlines(150)
                jeżeli L == []: przerwij

    def test_seek_read(self):
        self.test_write()
        # Try seek, read test

        przy gzip.GzipFile(self.filename) jako f:
            dopóki 1:
                oldpos = f.tell()
                line1 = f.readline()
                jeżeli nie line1: przerwij
                newpos = f.tell()
                f.seek(oldpos)  # negative seek
                jeżeli len(line1)>10:
                    amount = 10
                inaczej:
                    amount = len(line1)
                line2 = f.read(amount)
                self.assertEqual(line1[:amount], line2)
                f.seek(newpos)  # positive seek

    def test_seek_whence(self):
        self.test_write()
        # Try seek(whence=1), read test

        przy gzip.GzipFile(self.filename) jako f:
            f.read(10)
            f.seek(10, whence=1)
            y = f.read(10)
        self.assertEqual(y, data1[20:30])

    def test_seek_write(self):
        # Try seek, write test
        przy gzip.GzipFile(self.filename, 'w') jako f:
            dla pos w range(0, 256, 16):
                f.seek(pos)
                f.write(b'GZ\n')

    def test_mode(self):
        self.test_write()
        przy gzip.GzipFile(self.filename, 'r') jako f:
            self.assertEqual(f.myfileobj.mode, 'rb')
        support.unlink(self.filename)
        przy gzip.GzipFile(self.filename, 'x') jako f:
            self.assertEqual(f.myfileobj.mode, 'xb')

    def test_1647484(self):
        dla mode w ('wb', 'rb'):
            przy gzip.GzipFile(self.filename, mode) jako f:
                self.assertPrawda(hasattr(f, "name"))
                self.assertEqual(f.name, self.filename)

    def test_paddedfile_getattr(self):
        self.test_write()
        przy gzip.GzipFile(self.filename, 'rb') jako f:
            self.assertPrawda(hasattr(f.fileobj, "name"))
            self.assertEqual(f.fileobj.name, self.filename)

    def test_mtime(self):
        mtime = 123456789
        przy gzip.GzipFile(self.filename, 'w', mtime = mtime) jako fWrite:
            fWrite.write(data1)
        przy gzip.GzipFile(self.filename) jako fRead:
            self.assertPrawda(hasattr(fRead, 'mtime'))
            self.assertIsNic(fRead.mtime)
            dataRead = fRead.read()
            self.assertEqual(dataRead, data1)
            self.assertEqual(fRead.mtime, mtime)

    def test_metadata(self):
        mtime = 123456789

        przy gzip.GzipFile(self.filename, 'w', mtime = mtime) jako fWrite:
            fWrite.write(data1)

        przy open(self.filename, 'rb') jako fRead:
            # see RFC 1952: http://www.faqs.org/rfcs/rfc1952.html

            idBytes = fRead.read(2)
            self.assertEqual(idBytes, b'\x1f\x8b') # gzip ID

            cmByte = fRead.read(1)
            self.assertEqual(cmByte, b'\x08') # deflate

            flagsByte = fRead.read(1)
            self.assertEqual(flagsByte, b'\x08') # only the FNAME flag jest set

            mtimeBytes = fRead.read(4)
            self.assertEqual(mtimeBytes, struct.pack('<i', mtime)) # little-endian

            xflByte = fRead.read(1)
            self.assertEqual(xflByte, b'\x02') # maximum compression

            osByte = fRead.read(1)
            self.assertEqual(osByte, b'\xff') # OS "unknown" (OS-independent)

            # Since the FNAME flag jest set, the zero-terminated filename follows.
            # RFC 1952 specifies that this jest the name of the input file, jeżeli any.
            # However, the gzip module defaults to storing the name of the output
            # file w this field.
            expected = self.filename.encode('Latin-1') + b'\x00'
            nameBytes = fRead.read(len(expected))
            self.assertEqual(nameBytes, expected)

            # Since no other flags were set, the header ends here.
            # Rather than process the compressed data, let's seek to the trailer.
            fRead.seek(os.stat(self.filename).st_size - 8)

            crc32Bytes = fRead.read(4) # CRC32 of uncompressed data [data1]
            self.assertEqual(crc32Bytes, b'\xaf\xd7d\x83')

            isizeBytes = fRead.read(4)
            self.assertEqual(isizeBytes, struct.pack('<i', len(data1)))

    def test_with_open(self):
        # GzipFile supports the context management protocol
        przy gzip.GzipFile(self.filename, "wb") jako f:
            f.write(b"xxx")
        f = gzip.GzipFile(self.filename, "rb")
        f.close()
        spróbuj:
            przy f:
                dalej
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("__enter__ on a closed file didn't podnieś an exception")
        spróbuj:
            przy gzip.GzipFile(self.filename, "wb") jako f:
                1/0
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            self.fail("1/0 didn't podnieś an exception")

    def test_zero_padded_file(self):
        przy gzip.GzipFile(self.filename, "wb") jako f:
            f.write(data1 * 50)

        # Pad the file przy zeroes
        przy open(self.filename, "ab") jako f:
            f.write(b"\x00" * 50)

        przy gzip.GzipFile(self.filename, "rb") jako f:
            d = f.read()
            self.assertEqual(d, data1 * 50, "Incorrect data w file")

    def test_non_seekable_file(self):
        uncompressed = data1 * 50
        buf = UnseekableIO()
        przy gzip.GzipFile(fileobj=buf, mode="wb") jako f:
            f.write(uncompressed)
        compressed = buf.getvalue()
        buf = UnseekableIO(compressed)
        przy gzip.GzipFile(fileobj=buf, mode="rb") jako f:
            self.assertEqual(f.read(), uncompressed)

    def test_peek(self):
        uncompressed = data1 * 200
        przy gzip.GzipFile(self.filename, "wb") jako f:
            f.write(uncompressed)

        def sizes():
            dopóki Prawda:
                dla n w range(5, 50, 10):
                    uzyskaj n

        przy gzip.GzipFile(self.filename, "rb") jako f:
            f.max_read_chunk = 33
            nread = 0
            dla n w sizes():
                s = f.peek(n)
                jeżeli s == b'':
                    przerwij
                self.assertEqual(f.read(len(s)), s)
                nread += len(s)
            self.assertEqual(f.read(100), b'')
            self.assertEqual(nread, len(uncompressed))

    def test_textio_readlines(self):
        # Issue #10791: TextIOWrapper.readlines() fails when wrapping GzipFile.
        lines = (data1 * 50).decode("ascii").splitlines(keepends=Prawda)
        self.test_write()
        przy gzip.GzipFile(self.filename, 'r') jako f:
            przy io.TextIOWrapper(f, encoding="ascii") jako t:
                self.assertEqual(t.readlines(), lines)

    def test_fileobj_from_fdopen(self):
        # Issue #13781: Opening a GzipFile dla writing fails when using a
        # fileobj created przy os.fdopen().
        fd = os.open(self.filename, os.O_WRONLY | os.O_CREAT)
        przy os.fdopen(fd, "wb") jako f:
            przy gzip.GzipFile(fileobj=f, mode="w") jako g:
                dalej

    def test_bytes_filename(self):
        str_filename = self.filename
        spróbuj:
            bytes_filename = str_filename.encode("ascii")
        wyjąwszy UnicodeEncodeError:
            self.skipTest("Temporary file name needs to be ASCII")
        przy gzip.GzipFile(bytes_filename, "wb") jako f:
            f.write(data1 * 50)
        przy gzip.GzipFile(bytes_filename, "rb") jako f:
            self.assertEqual(f.read(), data1 * 50)
        # Sanity check that we are actually operating on the right file.
        przy gzip.GzipFile(str_filename, "rb") jako f:
            self.assertEqual(f.read(), data1 * 50)

    def test_decompress_limited(self):
        """Decompressed data buffering should be limited"""
        bomb = gzip.compress(bytes(int(2e6)), compresslevel=9)
        self.assertLess(len(bomb), io.DEFAULT_BUFFER_SIZE)

        bomb = io.BytesIO(bomb)
        decomp = gzip.GzipFile(fileobj=bomb)
        self.assertEqual(bytes(1), decomp.read(1))
        max_decomp = 1 + io.DEFAULT_BUFFER_SIZE
        self.assertLessEqual(decomp._buffer.raw.tell(), max_decomp,
            "Excessive amount of data was decompressed")

    # Testing compress/decompress shortcut functions

    def test_compress(self):
        dla data w [data1, data2]:
            dla args w [(), (1,), (6,), (9,)]:
                datac = gzip.compress(data, *args)
                self.assertEqual(type(datac), bytes)
                przy gzip.GzipFile(fileobj=io.BytesIO(datac), mode="rb") jako f:
                    self.assertEqual(f.read(), data)

    def test_decompress(self):
        dla data w (data1, data2):
            buf = io.BytesIO()
            przy gzip.GzipFile(fileobj=buf, mode="wb") jako f:
                f.write(data)
            self.assertEqual(gzip.decompress(buf.getvalue()), data)
            # Roundtrip przy compress
            datac = gzip.compress(data)
            self.assertEqual(gzip.decompress(datac), data)

    def test_read_truncated(self):
        data = data1*50
        # Drop the CRC (4 bytes) oraz file size (4 bytes).
        truncated = gzip.compress(data)[:-8]
        przy gzip.GzipFile(fileobj=io.BytesIO(truncated)) jako f:
            self.assertRaises(EOFError, f.read)
        przy gzip.GzipFile(fileobj=io.BytesIO(truncated)) jako f:
            self.assertEqual(f.read(len(data)), data)
            self.assertRaises(EOFError, f.read, 1)
        # Incomplete 10-byte header.
        dla i w range(2, 10):
            przy gzip.GzipFile(fileobj=io.BytesIO(truncated[:i])) jako f:
                self.assertRaises(EOFError, f.read, 1)

    def test_read_with_extra(self):
        # Gzip data przy an extra field
        gzdata = (b'\x1f\x8b\x08\x04\xb2\x17cQ\x02\xff'
                  b'\x05\x00Extra'
                  b'\x0bI-.\x01\x002\xd1Mx\x04\x00\x00\x00')
        przy gzip.GzipFile(fileobj=io.BytesIO(gzdata)) jako f:
            self.assertEqual(f.read(), b'Test')

    def test_prepend_error(self):
        # See issue #20875
        przy gzip.open(self.filename, "wb") jako f:
            f.write(data1)
        przy gzip.open(self.filename, "rb") jako f:
            f._buffer.raw._fp.prepend()

klasa TestOpen(BaseTest):
    def test_binary_modes(self):
        uncompressed = data1 * 50

        przy gzip.open(self.filename, "wb") jako f:
            f.write(uncompressed)
        przy open(self.filename, "rb") jako f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed)

        przy gzip.open(self.filename, "rb") jako f:
            self.assertEqual(f.read(), uncompressed)

        przy gzip.open(self.filename, "ab") jako f:
            f.write(uncompressed)
        przy open(self.filename, "rb") jako f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed * 2)

        przy self.assertRaises(FileExistsError):
            gzip.open(self.filename, "xb")
        support.unlink(self.filename)
        przy gzip.open(self.filename, "xb") jako f:
            f.write(uncompressed)
        przy open(self.filename, "rb") jako f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed)

    def test_implicit_binary_modes(self):
        # Test implicit binary modes (no "b" albo "t" w mode string).
        uncompressed = data1 * 50

        przy gzip.open(self.filename, "w") jako f:
            f.write(uncompressed)
        przy open(self.filename, "rb") jako f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed)

        przy gzip.open(self.filename, "r") jako f:
            self.assertEqual(f.read(), uncompressed)

        przy gzip.open(self.filename, "a") jako f:
            f.write(uncompressed)
        przy open(self.filename, "rb") jako f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed * 2)

        przy self.assertRaises(FileExistsError):
            gzip.open(self.filename, "x")
        support.unlink(self.filename)
        przy gzip.open(self.filename, "x") jako f:
            f.write(uncompressed)
        przy open(self.filename, "rb") jako f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed)

    def test_text_modes(self):
        uncompressed = data1.decode("ascii") * 50
        uncompressed_raw = uncompressed.replace("\n", os.linesep)
        przy gzip.open(self.filename, "wt") jako f:
            f.write(uncompressed)
        przy open(self.filename, "rb") jako f:
            file_data = gzip.decompress(f.read()).decode("ascii")
            self.assertEqual(file_data, uncompressed_raw)
        przy gzip.open(self.filename, "rt") jako f:
            self.assertEqual(f.read(), uncompressed)
        przy gzip.open(self.filename, "at") jako f:
            f.write(uncompressed)
        przy open(self.filename, "rb") jako f:
            file_data = gzip.decompress(f.read()).decode("ascii")
            self.assertEqual(file_data, uncompressed_raw * 2)

    def test_fileobj(self):
        uncompressed_bytes = data1 * 50
        uncompressed_str = uncompressed_bytes.decode("ascii")
        compressed = gzip.compress(uncompressed_bytes)
        przy gzip.open(io.BytesIO(compressed), "r") jako f:
            self.assertEqual(f.read(), uncompressed_bytes)
        przy gzip.open(io.BytesIO(compressed), "rb") jako f:
            self.assertEqual(f.read(), uncompressed_bytes)
        przy gzip.open(io.BytesIO(compressed), "rt") jako f:
            self.assertEqual(f.read(), uncompressed_str)

    def test_bad_params(self):
        # Test invalid parameter combinations.
        przy self.assertRaises(TypeError):
            gzip.open(123.456)
        przy self.assertRaises(ValueError):
            gzip.open(self.filename, "wbt")
        przy self.assertRaises(ValueError):
            gzip.open(self.filename, "xbt")
        przy self.assertRaises(ValueError):
            gzip.open(self.filename, "rb", encoding="utf-8")
        przy self.assertRaises(ValueError):
            gzip.open(self.filename, "rb", errors="ignore")
        przy self.assertRaises(ValueError):
            gzip.open(self.filename, "rb", newline="\n")

    def test_encoding(self):
        # Test non-default encoding.
        uncompressed = data1.decode("ascii") * 50
        uncompressed_raw = uncompressed.replace("\n", os.linesep)
        przy gzip.open(self.filename, "wt", encoding="utf-16") jako f:
            f.write(uncompressed)
        przy open(self.filename, "rb") jako f:
            file_data = gzip.decompress(f.read()).decode("utf-16")
            self.assertEqual(file_data, uncompressed_raw)
        przy gzip.open(self.filename, "rt", encoding="utf-16") jako f:
            self.assertEqual(f.read(), uncompressed)

    def test_encoding_error_handler(self):
        # Test przy non-default encoding error handler.
        przy gzip.open(self.filename, "wb") jako f:
            f.write(b"foo\xffbar")
        przy gzip.open(self.filename, "rt", encoding="ascii", errors="ignore") \
                jako f:
            self.assertEqual(f.read(), "foobar")

    def test_newline(self):
        # Test przy explicit newline (universal newline mode disabled).
        uncompressed = data1.decode("ascii") * 50
        przy gzip.open(self.filename, "wt", newline="\n") jako f:
            f.write(uncompressed)
        przy gzip.open(self.filename, "rt", newline="\r") jako f:
            self.assertEqual(f.readlines(), [uncompressed])

def test_main(verbose=Nic):
    support.run_unittest(TestGzip, TestOpen)

jeżeli __name__ == "__main__":
    test_main(verbose=Prawda)
