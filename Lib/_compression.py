"""Internal classes used by the gzip, lzma oraz bz2 modules"""

zaimportuj io


BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE  # Compressed data read chunk size


klasa BaseStream(io.BufferedIOBase):
    """Mode-checking helper functions."""

    def _check_not_closed(self):
        jeżeli self.closed:
            podnieś ValueError("I/O operation on closed file")

    def _check_can_read(self):
        jeżeli nie self.readable():
            podnieś io.UnsupportedOperation("File nie open dla reading")

    def _check_can_write(self):
        jeżeli nie self.writable():
            podnieś io.UnsupportedOperation("File nie open dla writing")

    def _check_can_seek(self):
        jeżeli nie self.readable():
            podnieś io.UnsupportedOperation("Seeking jest only supported "
                                          "on files open dla reading")
        jeżeli nie self.seekable():
            podnieś io.UnsupportedOperation("The underlying file object "
                                          "does nie support seeking")


klasa DecompressReader(io.RawIOBase):
    """Adapts the decompressor API to a RawIOBase reader API"""

    def readable(self):
        zwróć Prawda

    def __init__(self, fp, decomp_factory, trailing_error=(), **decomp_args):
        self._fp = fp
        self._eof = Nieprawda
        self._pos = 0  # Current offset w decompressed stream

        # Set to size of decompressed stream once it jest known, dla SEEK_END
        self._size = -1

        # Save the decompressor factory oraz arguments.
        # If the file contains multiple compressed streams, each
        # stream will need a separate decompressor object. A new decompressor
        # object jest also needed when implementing a backwards seek().
        self._decomp_factory = decomp_factory
        self._decomp_args = decomp_args
        self._decompressor = self._decomp_factory(**self._decomp_args)

        # Exception klasa to catch z decompressor signifying invalid
        # trailing data to ignore
        self._trailing_error = trailing_error

    def close(self):
        self._decompressor = Nic
        zwróć super().close()

    def seekable(self):
        zwróć self._fp.seekable()

    def readinto(self, b):
        przy memoryview(b) jako view, view.cast("B") jako byte_view:
            data = self.read(len(byte_view))
            byte_view[:len(data)] = data
        zwróć len(data)

    def read(self, size=-1):
        jeżeli size < 0:
            zwróć self.readall()

        jeżeli nie size albo self._eof:
            zwróć b""
        data = Nic  # Default jeżeli EOF jest encountered
        # Depending on the input data, our call to the decompressor may nie
        # zwróć any data. In this case, try again after reading another block.
        dopóki Prawda:
            jeżeli self._decompressor.eof:
                rawblock = (self._decompressor.unused_data albo
                            self._fp.read(BUFFER_SIZE))
                jeżeli nie rawblock:
                    przerwij
                # Continue to next stream.
                self._decompressor = self._decomp_factory(
                    **self._decomp_args)
                spróbuj:
                    data = self._decompressor.decompress(rawblock, size)
                wyjąwszy self._trailing_error:
                    # Trailing data isn't a valid compressed stream; ignore it.
                    przerwij
            inaczej:
                jeżeli self._decompressor.needs_input:
                    rawblock = self._fp.read(BUFFER_SIZE)
                    jeżeli nie rawblock:
                        podnieś EOFError("Compressed file ended before the "
                                       "end-of-stream marker was reached")
                inaczej:
                    rawblock = b""
                data = self._decompressor.decompress(rawblock, size)
            jeżeli data:
                przerwij
        jeżeli nie data:
            self._eof = Prawda
            self._size = self._pos
            zwróć b""
        self._pos += len(data)
        zwróć data

    # Rewind the file to the beginning of the data stream.
    def _rewind(self):
        self._fp.seek(0)
        self._eof = Nieprawda
        self._pos = 0
        self._decompressor = self._decomp_factory(**self._decomp_args)

    def seek(self, offset, whence=io.SEEK_SET):
        # Recalculate offset jako an absolute file position.
        jeżeli whence == io.SEEK_SET:
            dalej
        albo_inaczej whence == io.SEEK_CUR:
            offset = self._pos + offset
        albo_inaczej whence == io.SEEK_END:
            # Seeking relative to EOF - we need to know the file's size.
            jeżeli self._size < 0:
                dopóki self.read(io.DEFAULT_BUFFER_SIZE):
                    dalej
            offset = self._size + offset
        inaczej:
            podnieś ValueError("Invalid value dla whence: {}".format(whence))

        # Make it so that offset jest the number of bytes to skip forward.
        jeżeli offset < self._pos:
            self._rewind()
        inaczej:
            offset -= self._pos

        # Read oraz discard data until we reach the desired position.
        dopóki offset > 0:
            data = self.read(min(io.DEFAULT_BUFFER_SIZE, offset))
            jeżeli nie data:
                przerwij
            offset -= len(data)

        zwróć self._pos

    def tell(self):
        """Return the current file position."""
        zwróć self._pos
