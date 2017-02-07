#!/usr/bin/env python3
#-------------------------------------------------------------------
# tarfile.py
#-------------------------------------------------------------------
# Copyright (C) 2002 Lars Gustaebel <lars@gustaebel.de>
# All rights reserved.
#
# Permission  jest  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  oraz associated documentation
# files  (the  "Software"),  to   deal  w  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  oraz to  permit  persons  to  whom the
# Software  jest  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice oraz this  permission notice shall  be
# included w all copies albo substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
# OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
# NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
# HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
# WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
"""Read z oraz write to tar format archives.
"""

version     = "0.9.0"
__author__  = "Lars Gust\u00e4bel (lars@gustaebel.de)"
__date__    = "$Date: 2011-02-25 17:42:01 +0200 (Fri, 25 Feb 2011) $"
__cvsid__   = "$Id: tarfile.py 88586 2011-02-25 15:42:01Z marc-andre.lemburg $"
__credits__ = "Gustavo Niemeyer, Niels Gust\u00e4bel, Richard Townsend."

#---------
# Imports
#---------
z builtins zaimportuj open jako bltn_open
zaimportuj sys
zaimportuj os
zaimportuj io
zaimportuj shutil
zaimportuj stat
zaimportuj time
zaimportuj struct
zaimportuj copy
zaimportuj re

spróbuj:
    zaimportuj grp, pwd
wyjąwszy ImportError:
    grp = pwd = Nic

# os.symlink on Windows prior to 6.0 podnieśs NotImplementedError
symlink_exception = (AttributeError, NotImplementedError)
spróbuj:
    # OSError (winerror=1314) will be podnieśd jeżeli the caller does nie hold the
    # SeCreateSymbolicLinkPrivilege privilege
    symlink_exception += (OSError,)
wyjąwszy NameError:
    dalej

# z tarfile zaimportuj *
__all__ = ["TarFile", "TarInfo", "is_tarfile", "TarError"]

#---------------------------------------------------------
# tar constants
#---------------------------------------------------------
NUL = b"\0"                     # the null character
BLOCKSIZE = 512                 # length of processing blocks
RECORDSIZE = BLOCKSIZE * 20     # length of records
GNU_MAGIC = b"ustar  \0"        # magic gnu tar string
POSIX_MAGIC = b"ustar\x0000"    # magic posix tar string

LENGTH_NAME = 100               # maximum length of a filename
LENGTH_LINK = 100               # maximum length of a linkname
LENGTH_PREFIX = 155             # maximum length of the prefix field

REGTYPE = b"0"                  # regular file
AREGTYPE = b"\0"                # regular file
LNKTYPE = b"1"                  # link (inside tarfile)
SYMTYPE = b"2"                  # symbolic link
CHRTYPE = b"3"                  # character special device
BLKTYPE = b"4"                  # block special device
DIRTYPE = b"5"                  # directory
FIFOTYPE = b"6"                 # fifo special device
CONTTYPE = b"7"                 # contiguous file

GNUTYPE_LONGNAME = b"L"         # GNU tar longname
GNUTYPE_LONGLINK = b"K"         # GNU tar longlink
GNUTYPE_SPARSE = b"S"           # GNU tar sparse file

XHDTYPE = b"x"                  # POSIX.1-2001 extended header
XGLTYPE = b"g"                  # POSIX.1-2001 global header
SOLARIS_XHDTYPE = b"X"          # Solaris extended header

USTAR_FORMAT = 0                # POSIX.1-1988 (ustar) format
GNU_FORMAT = 1                  # GNU tar format
PAX_FORMAT = 2                  # POSIX.1-2001 (pax) format
DEFAULT_FORMAT = GNU_FORMAT

#---------------------------------------------------------
# tarfile constants
#---------------------------------------------------------
# File types that tarfile supports:
SUPPORTED_TYPES = (REGTYPE, AREGTYPE, LNKTYPE,
                   SYMTYPE, DIRTYPE, FIFOTYPE,
                   CONTTYPE, CHRTYPE, BLKTYPE,
                   GNUTYPE_LONGNAME, GNUTYPE_LONGLINK,
                   GNUTYPE_SPARSE)

# File types that will be treated jako a regular file.
REGULAR_TYPES = (REGTYPE, AREGTYPE,
                 CONTTYPE, GNUTYPE_SPARSE)

# File types that are part of the GNU tar format.
GNU_TYPES = (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK,
             GNUTYPE_SPARSE)

# Fields z a pax header that override a TarInfo attribute.
PAX_FIELDS = ("path", "linkpath", "size", "mtime",
              "uid", "gid", "uname", "gname")

# Fields z a pax header that are affected by hdrcharset.
PAX_NAME_FIELDS = {"path", "linkpath", "uname", "gname"}

# Fields w a pax header that are numbers, all other fields
# are treated jako strings.
PAX_NUMBER_FIELDS = {
    "atime": float,
    "ctime": float,
    "mtime": float,
    "uid": int,
    "gid": int,
    "size": int
}

#---------------------------------------------------------
# initialization
#---------------------------------------------------------
jeżeli os.name w ("nt", "ce"):
    ENCODING = "utf-8"
inaczej:
    ENCODING = sys.getfilesystemencoding()

#---------------------------------------------------------
# Some useful functions
#---------------------------------------------------------

def stn(s, length, encoding, errors):
    """Convert a string to a null-terminated bytes object.
    """
    s = s.encode(encoding, errors)
    zwróć s[:length] + (length - len(s)) * NUL

def nts(s, encoding, errors):
    """Convert a null-terminated bytes object to a string.
    """
    p = s.find(b"\0")
    jeżeli p != -1:
        s = s[:p]
    zwróć s.decode(encoding, errors)

def nti(s):
    """Convert a number field to a python number.
    """
    # There are two possible encodings dla a number field, see
    # itn() below.
    jeżeli s[0] w (0o200, 0o377):
        n = 0
        dla i w range(len(s) - 1):
            n <<= 8
            n += s[i + 1]
        jeżeli s[0] == 0o377:
            n = -(256 ** (len(s) - 1) - n)
    inaczej:
        spróbuj:
            s = nts(s, "ascii", "strict")
            n = int(s.strip() albo "0", 8)
        wyjąwszy ValueError:
            podnieś InvalidHeaderError("invalid header")
    zwróć n

def itn(n, digits=8, format=DEFAULT_FORMAT):
    """Convert a python number to a number field.
    """
    # POSIX 1003.1-1988 requires numbers to be encoded jako a string of
    # octal digits followed by a null-byte, this allows values up to
    # (8**(digits-1))-1. GNU tar allows storing numbers greater than
    # that jeżeli necessary. A leading 0o200 albo 0o377 byte indicate this
    # particular encoding, the following digits-1 bytes are a big-endian
    # base-256 representation. This allows values up to (256**(digits-1))-1.
    # A 0o200 byte indicates a positive number, a 0o377 byte a negative
    # number.
    jeżeli 0 <= n < 8 ** (digits - 1):
        s = bytes("%0*o" % (digits - 1, int(n)), "ascii") + NUL
    albo_inaczej format == GNU_FORMAT oraz -256 ** (digits - 1) <= n < 256 ** (digits - 1):
        jeżeli n >= 0:
            s = bytearray([0o200])
        inaczej:
            s = bytearray([0o377])
            n = 256 ** digits + n

        dla i w range(digits - 1):
            s.insert(1, n & 0o377)
            n >>= 8
    inaczej:
        podnieś ValueError("overflow w number field")

    zwróć s

def calc_chksums(buf):
    """Calculate the checksum dla a member's header by summing up all
       characters wyjąwszy dla the chksum field which jest treated jako if
       it was filled przy spaces. According to the GNU tar sources,
       some tars (Sun oraz NeXT) calculate chksum przy signed char,
       which will be different jeżeli there are chars w the buffer with
       the high bit set. So we calculate two checksums, unsigned oraz
       signed.
    """
    unsigned_chksum = 256 + sum(struct.unpack_from("148B8x356B", buf))
    signed_chksum = 256 + sum(struct.unpack_from("148b8x356b", buf))
    zwróć unsigned_chksum, signed_chksum

def copyfileobj(src, dst, length=Nic, exception=OSError):
    """Copy length bytes z fileobj src to fileobj dst.
       If length jest Nic, copy the entire content.
    """
    jeżeli length == 0:
        zwróć
    jeżeli length jest Nic:
        shutil.copyfileobj(src, dst)
        zwróć

    BUFSIZE = 16 * 1024
    blocks, remainder = divmod(length, BUFSIZE)
    dla b w range(blocks):
        buf = src.read(BUFSIZE)
        jeżeli len(buf) < BUFSIZE:
            podnieś exception("unexpected end of data")
        dst.write(buf)

    jeżeli remainder != 0:
        buf = src.read(remainder)
        jeżeli len(buf) < remainder:
            podnieś exception("unexpected end of data")
        dst.write(buf)
    zwróć

def filemode(mode):
    """Deprecated w this location; use stat.filemode."""
    zaimportuj warnings
    warnings.warn("deprecated w favor of stat.filemode",
                  DeprecationWarning, 2)
    zwróć stat.filemode(mode)

def _safe_print(s):
    encoding = getattr(sys.stdout, 'encoding', Nic)
    jeżeli encoding jest nie Nic:
        s = s.encode(encoding, 'backslashreplace').decode(encoding)
    print(s, end=' ')


klasa TarError(Exception):
    """Base exception."""
    dalej
klasa ExtractError(TarError):
    """General exception dla extract errors."""
    dalej
klasa ReadError(TarError):
    """Exception dla unreadable tar archives."""
    dalej
klasa CompressionError(TarError):
    """Exception dla unavailable compression methods."""
    dalej
klasa StreamError(TarError):
    """Exception dla unsupported operations on stream-like TarFiles."""
    dalej
klasa HeaderError(TarError):
    """Base exception dla header errors."""
    dalej
klasa EmptyHeaderError(HeaderError):
    """Exception dla empty headers."""
    dalej
klasa TruncatedHeaderError(HeaderError):
    """Exception dla truncated headers."""
    dalej
klasa EOFHeaderError(HeaderError):
    """Exception dla end of file headers."""
    dalej
klasa InvalidHeaderError(HeaderError):
    """Exception dla invalid headers."""
    dalej
klasa SubsequentHeaderError(HeaderError):
    """Exception dla missing oraz invalid extended headers."""
    dalej

#---------------------------
# internal stream interface
#---------------------------
klasa _LowLevelFile:
    """Low-level file object. Supports reading oraz writing.
       It jest used instead of a regular file object dla streaming
       access.
    """

    def __init__(self, name, mode):
        mode = {
            "r": os.O_RDONLY,
            "w": os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        }[mode]
        jeżeli hasattr(os, "O_BINARY"):
            mode |= os.O_BINARY
        self.fd = os.open(name, mode, 0o666)

    def close(self):
        os.close(self.fd)

    def read(self, size):
        zwróć os.read(self.fd, size)

    def write(self, s):
        os.write(self.fd, s)

klasa _Stream:
    """Class that serves jako an adapter between TarFile oraz
       a stream-like object.  The stream-like object only
       needs to have a read() albo write() method oraz jest accessed
       blockwise.  Use of gzip albo bzip2 compression jest possible.
       A stream-like object could be dla example: sys.stdin,
       sys.stdout, a socket, a tape device etc.

       _Stream jest intended to be used only internally.
    """

    def __init__(self, name, mode, comptype, fileobj, bufsize):
        """Construct a _Stream object.
        """
        self._extfileobj = Prawda
        jeżeli fileobj jest Nic:
            fileobj = _LowLevelFile(name, mode)
            self._extfileobj = Nieprawda

        jeżeli comptype == '*':
            # Enable transparent compression detection dla the
            # stream interface
            fileobj = _StreamProxy(fileobj)
            comptype = fileobj.getcomptype()

        self.name     = name albo ""
        self.mode     = mode
        self.comptype = comptype
        self.fileobj  = fileobj
        self.bufsize  = bufsize
        self.buf      = b""
        self.pos      = 0
        self.closed   = Nieprawda

        spróbuj:
            jeżeli comptype == "gz":
                spróbuj:
                    zaimportuj zlib
                wyjąwszy ImportError:
                    podnieś CompressionError("zlib module jest nie available")
                self.zlib = zlib
                self.crc = zlib.crc32(b"")
                jeżeli mode == "r":
                    self._init_read_gz()
                    self.exception = zlib.error
                inaczej:
                    self._init_write_gz()

            albo_inaczej comptype == "bz2":
                spróbuj:
                    zaimportuj bz2
                wyjąwszy ImportError:
                    podnieś CompressionError("bz2 module jest nie available")
                jeżeli mode == "r":
                    self.dbuf = b""
                    self.cmp = bz2.BZ2Decompressor()
                    self.exception = OSError
                inaczej:
                    self.cmp = bz2.BZ2Compressor()

            albo_inaczej comptype == "xz":
                spróbuj:
                    zaimportuj lzma
                wyjąwszy ImportError:
                    podnieś CompressionError("lzma module jest nie available")
                jeżeli mode == "r":
                    self.dbuf = b""
                    self.cmp = lzma.LZMADecompressor()
                    self.exception = lzma.LZMAError
                inaczej:
                    self.cmp = lzma.LZMACompressor()

            albo_inaczej comptype != "tar":
                podnieś CompressionError("unknown compression type %r" % comptype)

        wyjąwszy:
            jeżeli nie self._extfileobj:
                self.fileobj.close()
            self.closed = Prawda
            podnieś

    def __del__(self):
        jeżeli hasattr(self, "closed") oraz nie self.closed:
            self.close()

    def _init_write_gz(self):
        """Initialize dla writing przy gzip compression.
        """
        self.cmp = self.zlib.compressobj(9, self.zlib.DEFLATED,
                                            -self.zlib.MAX_WBITS,
                                            self.zlib.DEF_MEM_LEVEL,
                                            0)
        timestamp = struct.pack("<L", int(time.time()))
        self.__write(b"\037\213\010\010" + timestamp + b"\002\377")
        jeżeli self.name.endswith(".gz"):
            self.name = self.name[:-3]
        # RFC1952 says we must use ISO-8859-1 dla the FNAME field.
        self.__write(self.name.encode("iso-8859-1", "replace") + NUL)

    def write(self, s):
        """Write string s to the stream.
        """
        jeżeli self.comptype == "gz":
            self.crc = self.zlib.crc32(s, self.crc)
        self.pos += len(s)
        jeżeli self.comptype != "tar":
            s = self.cmp.compress(s)
        self.__write(s)

    def __write(self, s):
        """Write string s to the stream jeżeli a whole new block
           jest ready to be written.
        """
        self.buf += s
        dopóki len(self.buf) > self.bufsize:
            self.fileobj.write(self.buf[:self.bufsize])
            self.buf = self.buf[self.bufsize:]

    def close(self):
        """Close the _Stream object. No operation should be
           done on it afterwards.
        """
        jeżeli self.closed:
            zwróć

        self.closed = Prawda
        spróbuj:
            jeżeli self.mode == "w" oraz self.comptype != "tar":
                self.buf += self.cmp.flush()

            jeżeli self.mode == "w" oraz self.buf:
                self.fileobj.write(self.buf)
                self.buf = b""
                jeżeli self.comptype == "gz":
                    # The native zlib crc jest an unsigned 32-bit integer, but
                    # the Python wrapper implicitly casts that to a signed C
                    # long.  So, on a 32-bit box self.crc may "look negative",
                    # dopóki the same crc on a 64-bit box may "look positive".
                    # To avoid irksome warnings z the `struct` module, force
                    # it to look positive on all boxes.
                    self.fileobj.write(struct.pack("<L", self.crc & 0xffffffff))
                    self.fileobj.write(struct.pack("<L", self.pos & 0xffffFFFF))
        w_końcu:
            jeżeli nie self._extfileobj:
                self.fileobj.close()

    def _init_read_gz(self):
        """Initialize dla reading a gzip compressed fileobj.
        """
        self.cmp = self.zlib.decompressobj(-self.zlib.MAX_WBITS)
        self.dbuf = b""

        # taken z gzip.GzipFile przy some alterations
        jeżeli self.__read(2) != b"\037\213":
            podnieś ReadError("not a gzip file")
        jeżeli self.__read(1) != b"\010":
            podnieś CompressionError("unsupported compression method")

        flag = ord(self.__read(1))
        self.__read(6)

        jeżeli flag & 4:
            xlen = ord(self.__read(1)) + 256 * ord(self.__read(1))
            self.read(xlen)
        jeżeli flag & 8:
            dopóki Prawda:
                s = self.__read(1)
                jeżeli nie s albo s == NUL:
                    przerwij
        jeżeli flag & 16:
            dopóki Prawda:
                s = self.__read(1)
                jeżeli nie s albo s == NUL:
                    przerwij
        jeżeli flag & 2:
            self.__read(2)

    def tell(self):
        """Return the stream's file pointer position.
        """
        zwróć self.pos

    def seek(self, pos=0):
        """Set the stream's file pointer to pos. Negative seeking
           jest forbidden.
        """
        jeżeli pos - self.pos >= 0:
            blocks, remainder = divmod(pos - self.pos, self.bufsize)
            dla i w range(blocks):
                self.read(self.bufsize)
            self.read(remainder)
        inaczej:
            podnieś StreamError("seeking backwards jest nie allowed")
        zwróć self.pos

    def read(self, size=Nic):
        """Return the next size number of bytes z the stream.
           If size jest nie defined, zwróć all bytes of the stream
           up to EOF.
        """
        jeżeli size jest Nic:
            t = []
            dopóki Prawda:
                buf = self._read(self.bufsize)
                jeżeli nie buf:
                    przerwij
                t.append(buf)
            buf = "".join(t)
        inaczej:
            buf = self._read(size)
        self.pos += len(buf)
        zwróć buf

    def _read(self, size):
        """Return size bytes z the stream.
        """
        jeżeli self.comptype == "tar":
            zwróć self.__read(size)

        c = len(self.dbuf)
        dopóki c < size:
            buf = self.__read(self.bufsize)
            jeżeli nie buf:
                przerwij
            spróbuj:
                buf = self.cmp.decompress(buf)
            wyjąwszy self.exception:
                podnieś ReadError("invalid compressed data")
            self.dbuf += buf
            c += len(buf)
        buf = self.dbuf[:size]
        self.dbuf = self.dbuf[size:]
        zwróć buf

    def __read(self, size):
        """Return size bytes z stream. If internal buffer jest empty,
           read another block z the stream.
        """
        c = len(self.buf)
        dopóki c < size:
            buf = self.fileobj.read(self.bufsize)
            jeżeli nie buf:
                przerwij
            self.buf += buf
            c += len(buf)
        buf = self.buf[:size]
        self.buf = self.buf[size:]
        zwróć buf
# klasa _Stream

klasa _StreamProxy(object):
    """Small proxy klasa that enables transparent compression
       detection dla the Stream interface (mode 'r|*').
    """

    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.buf = self.fileobj.read(BLOCKSIZE)

    def read(self, size):
        self.read = self.fileobj.read
        zwróć self.buf

    def getcomptype(self):
        jeżeli self.buf.startswith(b"\x1f\x8b\x08"):
            zwróć "gz"
        albo_inaczej self.buf[0:3] == b"BZh" oraz self.buf[4:10] == b"1AY&SY":
            zwróć "bz2"
        albo_inaczej self.buf.startswith((b"\x5d\x00\x00\x80", b"\xfd7zXZ")):
            zwróć "xz"
        inaczej:
            zwróć "tar"

    def close(self):
        self.fileobj.close()
# klasa StreamProxy

#------------------------
# Extraction file object
#------------------------
klasa _FileInFile(object):
    """A thin wrapper around an existing file object that
       provides a part of its data jako an individual file
       object.
    """

    def __init__(self, fileobj, offset, size, blockinfo=Nic):
        self.fileobj = fileobj
        self.offset = offset
        self.size = size
        self.position = 0
        self.name = getattr(fileobj, "name", Nic)
        self.closed = Nieprawda

        jeżeli blockinfo jest Nic:
            blockinfo = [(0, size)]

        # Construct a map przy data oraz zero blocks.
        self.map_index = 0
        self.map = []
        lastpos = 0
        realpos = self.offset
        dla offset, size w blockinfo:
            jeżeli offset > lastpos:
                self.map.append((Nieprawda, lastpos, offset, Nic))
            self.map.append((Prawda, offset, offset + size, realpos))
            realpos += size
            lastpos = offset + size
        jeżeli lastpos < self.size:
            self.map.append((Nieprawda, lastpos, self.size, Nic))

    def flush(self):
        dalej

    def readable(self):
        zwróć Prawda

    def writable(self):
        zwróć Nieprawda

    def seekable(self):
        zwróć self.fileobj.seekable()

    def tell(self):
        """Return the current file position.
        """
        zwróć self.position

    def seek(self, position, whence=io.SEEK_SET):
        """Seek to a position w the file.
        """
        jeżeli whence == io.SEEK_SET:
            self.position = min(max(position, 0), self.size)
        albo_inaczej whence == io.SEEK_CUR:
            jeżeli position < 0:
                self.position = max(self.position + position, 0)
            inaczej:
                self.position = min(self.position + position, self.size)
        albo_inaczej whence == io.SEEK_END:
            self.position = max(min(self.size + position, self.size), 0)
        inaczej:
            podnieś ValueError("Invalid argument")
        zwróć self.position

    def read(self, size=Nic):
        """Read data z the file.
        """
        jeżeli size jest Nic:
            size = self.size - self.position
        inaczej:
            size = min(size, self.size - self.position)

        buf = b""
        dopóki size > 0:
            dopóki Prawda:
                data, start, stop, offset = self.map[self.map_index]
                jeżeli start <= self.position < stop:
                    przerwij
                inaczej:
                    self.map_index += 1
                    jeżeli self.map_index == len(self.map):
                        self.map_index = 0
            length = min(size, stop - self.position)
            jeżeli data:
                self.fileobj.seek(offset + (self.position - start))
                b = self.fileobj.read(length)
                jeżeli len(b) != length:
                    podnieś ReadError("unexpected end of data")
                buf += b
            inaczej:
                buf += NUL * length
            size -= length
            self.position += length
        zwróć buf

    def readinto(self, b):
        buf = self.read(len(b))
        b[:len(buf)] = buf
        zwróć len(buf)

    def close(self):
        self.closed = Prawda
#class _FileInFile

klasa ExFileObject(io.BufferedReader):

    def __init__(self, tarfile, tarinfo):
        fileobj = _FileInFile(tarfile.fileobj, tarinfo.offset_data,
                tarinfo.size, tarinfo.sparse)
        super().__init__(fileobj)
#class ExFileObject

#------------------
# Exported Classes
#------------------
klasa TarInfo(object):
    """Informational klasa which holds the details about an
       archive member given by a tar header block.
       TarInfo objects are returned by TarFile.getmember(),
       TarFile.getmembers() oraz TarFile.gettarinfo() oraz are
       usually created internally.
    """

    __slots__ = ("name", "mode", "uid", "gid", "size", "mtime",
                 "chksum", "type", "linkname", "uname", "gname",
                 "devmajor", "devminor",
                 "offset", "offset_data", "pax_headers", "sparse",
                 "tarfile", "_sparse_structs", "_link_target")

    def __init__(self, name=""):
        """Construct a TarInfo object. name jest the optional name
           of the member.
        """
        self.name = name        # member name
        self.mode = 0o644       # file permissions
        self.uid = 0            # user id
        self.gid = 0            # group id
        self.size = 0           # file size
        self.mtime = 0          # modification time
        self.chksum = 0         # header checksum
        self.type = REGTYPE     # member type
        self.linkname = ""      # link name
        self.uname = ""         # user name
        self.gname = ""         # group name
        self.devmajor = 0       # device major number
        self.devminor = 0       # device minor number

        self.offset = 0         # the tar header starts here
        self.offset_data = 0    # the file's data starts here

        self.sparse = Nic      # sparse member information
        self.pax_headers = {}   # pax header information

    # In pax headers the "name" oraz "linkname" field are called
    # "path" oraz "linkpath".
    def _getpath(self):
        zwróć self.name
    def _setpath(self, name):
        self.name = name
    path = property(_getpath, _setpath)

    def _getlinkpath(self):
        zwróć self.linkname
    def _setlinkpath(self, linkname):
        self.linkname = linkname
    linkpath = property(_getlinkpath, _setlinkpath)

    def __repr__(self):
        zwróć "<%s %r at %#x>" % (self.__class__.__name__,self.name,id(self))

    def get_info(self):
        """Return the TarInfo's attributes jako a dictionary.
        """
        info = {
            "name":     self.name,
            "mode":     self.mode & 0o7777,
            "uid":      self.uid,
            "gid":      self.gid,
            "size":     self.size,
            "mtime":    self.mtime,
            "chksum":   self.chksum,
            "type":     self.type,
            "linkname": self.linkname,
            "uname":    self.uname,
            "gname":    self.gname,
            "devmajor": self.devmajor,
            "devminor": self.devminor
        }

        jeżeli info["type"] == DIRTYPE oraz nie info["name"].endswith("/"):
            info["name"] += "/"

        zwróć info

    def tobuf(self, format=DEFAULT_FORMAT, encoding=ENCODING, errors="surrogateescape"):
        """Return a tar header jako a string of 512 byte blocks.
        """
        info = self.get_info()

        jeżeli format == USTAR_FORMAT:
            zwróć self.create_ustar_header(info, encoding, errors)
        albo_inaczej format == GNU_FORMAT:
            zwróć self.create_gnu_header(info, encoding, errors)
        albo_inaczej format == PAX_FORMAT:
            zwróć self.create_pax_header(info, encoding)
        inaczej:
            podnieś ValueError("invalid format")

    def create_ustar_header(self, info, encoding, errors):
        """Return the object jako a ustar header block.
        """
        info["magic"] = POSIX_MAGIC

        jeżeli len(info["linkname"]) > LENGTH_LINK:
            podnieś ValueError("linkname jest too long")

        jeżeli len(info["name"]) > LENGTH_NAME:
            info["prefix"], info["name"] = self._posix_split_name(info["name"])

        zwróć self._create_header(info, USTAR_FORMAT, encoding, errors)

    def create_gnu_header(self, info, encoding, errors):
        """Return the object jako a GNU header block sequence.
        """
        info["magic"] = GNU_MAGIC

        buf = b""
        jeżeli len(info["linkname"]) > LENGTH_LINK:
            buf += self._create_gnu_long_header(info["linkname"], GNUTYPE_LONGLINK, encoding, errors)

        jeżeli len(info["name"]) > LENGTH_NAME:
            buf += self._create_gnu_long_header(info["name"], GNUTYPE_LONGNAME, encoding, errors)

        zwróć buf + self._create_header(info, GNU_FORMAT, encoding, errors)

    def create_pax_header(self, info, encoding):
        """Return the object jako a ustar header block. If it cannot be
           represented this way, prepend a pax extended header sequence
           przy supplement information.
        """
        info["magic"] = POSIX_MAGIC
        pax_headers = self.pax_headers.copy()

        # Test string fields dla values that exceed the field length albo cannot
        # be represented w ASCII encoding.
        dla name, hname, length w (
                ("name", "path", LENGTH_NAME), ("linkname", "linkpath", LENGTH_LINK),
                ("uname", "uname", 32), ("gname", "gname", 32)):

            jeżeli hname w pax_headers:
                # The pax header has priority.
                kontynuuj

            # Try to encode the string jako ASCII.
            spróbuj:
                info[name].encode("ascii", "strict")
            wyjąwszy UnicodeEncodeError:
                pax_headers[hname] = info[name]
                kontynuuj

            jeżeli len(info[name]) > length:
                pax_headers[hname] = info[name]

        # Test number fields dla values that exceed the field limit albo values
        # that like to be stored jako float.
        dla name, digits w (("uid", 8), ("gid", 8), ("size", 12), ("mtime", 12)):
            jeżeli name w pax_headers:
                # The pax header has priority. Avoid overflow.
                info[name] = 0
                kontynuuj

            val = info[name]
            jeżeli nie 0 <= val < 8 ** (digits - 1) albo isinstance(val, float):
                pax_headers[name] = str(val)
                info[name] = 0

        # Create a pax extended header jeżeli necessary.
        jeżeli pax_headers:
            buf = self._create_pax_generic_header(pax_headers, XHDTYPE, encoding)
        inaczej:
            buf = b""

        zwróć buf + self._create_header(info, USTAR_FORMAT, "ascii", "replace")

    @classmethod
    def create_pax_global_header(cls, pax_headers):
        """Return the object jako a pax global header block sequence.
        """
        zwróć cls._create_pax_generic_header(pax_headers, XGLTYPE, "utf-8")

    def _posix_split_name(self, name):
        """Split a name longer than 100 chars into a prefix
           oraz a name part.
        """
        prefix = name[:LENGTH_PREFIX + 1]
        dopóki prefix oraz prefix[-1] != "/":
            prefix = prefix[:-1]

        name = name[len(prefix):]
        prefix = prefix[:-1]

        jeżeli nie prefix albo len(name) > LENGTH_NAME:
            podnieś ValueError("name jest too long")
        zwróć prefix, name

    @staticmethod
    def _create_header(info, format, encoding, errors):
        """Return a header block. info jest a dictionary przy file
           information, format must be one of the *_FORMAT constants.
        """
        parts = [
            stn(info.get("name", ""), 100, encoding, errors),
            itn(info.get("mode", 0) & 0o7777, 8, format),
            itn(info.get("uid", 0), 8, format),
            itn(info.get("gid", 0), 8, format),
            itn(info.get("size", 0), 12, format),
            itn(info.get("mtime", 0), 12, format),
            b"        ", # checksum field
            info.get("type", REGTYPE),
            stn(info.get("linkname", ""), 100, encoding, errors),
            info.get("magic", POSIX_MAGIC),
            stn(info.get("uname", ""), 32, encoding, errors),
            stn(info.get("gname", ""), 32, encoding, errors),
            itn(info.get("devmajor", 0), 8, format),
            itn(info.get("devminor", 0), 8, format),
            stn(info.get("prefix", ""), 155, encoding, errors)
        ]

        buf = struct.pack("%ds" % BLOCKSIZE, b"".join(parts))
        chksum = calc_chksums(buf[-BLOCKSIZE:])[0]
        buf = buf[:-364] + bytes("%06o\0" % chksum, "ascii") + buf[-357:]
        zwróć buf

    @staticmethod
    def _create_payload(payload):
        """Return the string payload filled przy zero bytes
           up to the next 512 byte border.
        """
        blocks, remainder = divmod(len(payload), BLOCKSIZE)
        jeżeli remainder > 0:
            payload += (BLOCKSIZE - remainder) * NUL
        zwróć payload

    @classmethod
    def _create_gnu_long_header(cls, name, type, encoding, errors):
        """Return a GNUTYPE_LONGNAME albo GNUTYPE_LONGLINK sequence
           dla name.
        """
        name = name.encode(encoding, errors) + NUL

        info = {}
        info["name"] = "././@LongLink"
        info["type"] = type
        info["size"] = len(name)
        info["magic"] = GNU_MAGIC

        # create extended header + name blocks.
        zwróć cls._create_header(info, USTAR_FORMAT, encoding, errors) + \
                cls._create_payload(name)

    @classmethod
    def _create_pax_generic_header(cls, pax_headers, type, encoding):
        """Return a POSIX.1-2008 extended albo global header sequence
           that contains a list of keyword, value pairs. The values
           must be strings.
        """
        # Check jeżeli one of the fields contains surrogate characters oraz thereby
        # forces hdrcharset=BINARY, see _proc_pax() dla more information.
        binary = Nieprawda
        dla keyword, value w pax_headers.items():
            spróbuj:
                value.encode("utf-8", "strict")
            wyjąwszy UnicodeEncodeError:
                binary = Prawda
                przerwij

        records = b""
        jeżeli binary:
            # Put the hdrcharset field at the beginning of the header.
            records += b"21 hdrcharset=BINARY\n"

        dla keyword, value w pax_headers.items():
            keyword = keyword.encode("utf-8")
            jeżeli binary:
                # Try to restore the original byte representation of `value'.
                # Needless to say, that the encoding must match the string.
                value = value.encode(encoding, "surrogateescape")
            inaczej:
                value = value.encode("utf-8")

            l = len(keyword) + len(value) + 3   # ' ' + '=' + '\n'
            n = p = 0
            dopóki Prawda:
                n = l + len(str(p))
                jeżeli n == p:
                    przerwij
                p = n
            records += bytes(str(p), "ascii") + b" " + keyword + b"=" + value + b"\n"

        # We use a hardcoded "././@PaxHeader" name like star does
        # instead of the one that POSIX recommends.
        info = {}
        info["name"] = "././@PaxHeader"
        info["type"] = type
        info["size"] = len(records)
        info["magic"] = POSIX_MAGIC

        # Create pax header + record blocks.
        zwróć cls._create_header(info, USTAR_FORMAT, "ascii", "replace") + \
                cls._create_payload(records)

    @classmethod
    def frombuf(cls, buf, encoding, errors):
        """Construct a TarInfo object z a 512 byte bytes object.
        """
        jeżeli len(buf) == 0:
            podnieś EmptyHeaderError("empty header")
        jeżeli len(buf) != BLOCKSIZE:
            podnieś TruncatedHeaderError("truncated header")
        jeżeli buf.count(NUL) == BLOCKSIZE:
            podnieś EOFHeaderError("end of file header")

        chksum = nti(buf[148:156])
        jeżeli chksum nie w calc_chksums(buf):
            podnieś InvalidHeaderError("bad checksum")

        obj = cls()
        obj.name = nts(buf[0:100], encoding, errors)
        obj.mode = nti(buf[100:108])
        obj.uid = nti(buf[108:116])
        obj.gid = nti(buf[116:124])
        obj.size = nti(buf[124:136])
        obj.mtime = nti(buf[136:148])
        obj.chksum = chksum
        obj.type = buf[156:157]
        obj.linkname = nts(buf[157:257], encoding, errors)
        obj.uname = nts(buf[265:297], encoding, errors)
        obj.gname = nts(buf[297:329], encoding, errors)
        obj.devmajor = nti(buf[329:337])
        obj.devminor = nti(buf[337:345])
        prefix = nts(buf[345:500], encoding, errors)

        # Old V7 tar format represents a directory jako a regular
        # file przy a trailing slash.
        jeżeli obj.type == AREGTYPE oraz obj.name.endswith("/"):
            obj.type = DIRTYPE

        # The old GNU sparse format occupies some of the unused
        # space w the buffer dla up to 4 sparse structures.
        # Save the them dla later processing w _proc_sparse().
        jeżeli obj.type == GNUTYPE_SPARSE:
            pos = 386
            structs = []
            dla i w range(4):
                spróbuj:
                    offset = nti(buf[pos:pos + 12])
                    numbytes = nti(buf[pos + 12:pos + 24])
                wyjąwszy ValueError:
                    przerwij
                structs.append((offset, numbytes))
                pos += 24
            isextended = bool(buf[482])
            origsize = nti(buf[483:495])
            obj._sparse_structs = (structs, isextended, origsize)

        # Remove redundant slashes z directories.
        jeżeli obj.isdir():
            obj.name = obj.name.rstrip("/")

        # Reconstruct a ustar longname.
        jeżeli prefix oraz obj.type nie w GNU_TYPES:
            obj.name = prefix + "/" + obj.name
        zwróć obj

    @classmethod
    def fromtarfile(cls, tarfile):
        """Return the next TarInfo object z TarFile object
           tarfile.
        """
        buf = tarfile.fileobj.read(BLOCKSIZE)
        obj = cls.frombuf(buf, tarfile.encoding, tarfile.errors)
        obj.offset = tarfile.fileobj.tell() - BLOCKSIZE
        zwróć obj._proc_member(tarfile)

    #--------------------------------------------------------------------------
    # The following are methods that are called depending on the type of a
    # member. The entry point jest _proc_member() which can be overridden w a
    # subclass to add custom _proc_*() methods. A _proc_*() method MUST
    # implement the following
    # operations:
    # 1. Set self.offset_data to the position where the data blocks begin,
    #    jeżeli there jest data that follows.
    # 2. Set tarfile.offset to the position where the next member's header will
    #    begin.
    # 3. Return self albo another valid TarInfo object.
    def _proc_member(self, tarfile):
        """Choose the right processing method depending on
           the type oraz call it.
        """
        jeżeli self.type w (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK):
            zwróć self._proc_gnulong(tarfile)
        albo_inaczej self.type == GNUTYPE_SPARSE:
            zwróć self._proc_sparse(tarfile)
        albo_inaczej self.type w (XHDTYPE, XGLTYPE, SOLARIS_XHDTYPE):
            zwróć self._proc_pax(tarfile)
        inaczej:
            zwróć self._proc_builtin(tarfile)

    def _proc_builtin(self, tarfile):
        """Process a builtin type albo an unknown type which
           will be treated jako a regular file.
        """
        self.offset_data = tarfile.fileobj.tell()
        offset = self.offset_data
        jeżeli self.isreg() albo self.type nie w SUPPORTED_TYPES:
            # Skip the following data blocks.
            offset += self._block(self.size)
        tarfile.offset = offset

        # Patch the TarInfo object przy saved global
        # header information.
        self._apply_pax_info(tarfile.pax_headers, tarfile.encoding, tarfile.errors)

        zwróć self

    def _proc_gnulong(self, tarfile):
        """Process the blocks that hold a GNU longname
           albo longlink member.
        """
        buf = tarfile.fileobj.read(self._block(self.size))

        # Fetch the next header oraz process it.
        spróbuj:
            next = self.fromtarfile(tarfile)
        wyjąwszy HeaderError:
            podnieś SubsequentHeaderError("missing albo bad subsequent header")

        # Patch the TarInfo object z the next header with
        # the longname information.
        next.offset = self.offset
        jeżeli self.type == GNUTYPE_LONGNAME:
            next.name = nts(buf, tarfile.encoding, tarfile.errors)
        albo_inaczej self.type == GNUTYPE_LONGLINK:
            next.linkname = nts(buf, tarfile.encoding, tarfile.errors)

        zwróć next

    def _proc_sparse(self, tarfile):
        """Process a GNU sparse header plus extra headers.
        """
        # We already collected some sparse structures w frombuf().
        structs, isextended, origsize = self._sparse_structs
        usuń self._sparse_structs

        # Collect sparse structures z extended header blocks.
        dopóki isextended:
            buf = tarfile.fileobj.read(BLOCKSIZE)
            pos = 0
            dla i w range(21):
                spróbuj:
                    offset = nti(buf[pos:pos + 12])
                    numbytes = nti(buf[pos + 12:pos + 24])
                wyjąwszy ValueError:
                    przerwij
                jeżeli offset oraz numbytes:
                    structs.append((offset, numbytes))
                pos += 24
            isextended = bool(buf[504])
        self.sparse = structs

        self.offset_data = tarfile.fileobj.tell()
        tarfile.offset = self.offset_data + self._block(self.size)
        self.size = origsize
        zwróć self

    def _proc_pax(self, tarfile):
        """Process an extended albo global header jako described w
           POSIX.1-2008.
        """
        # Read the header information.
        buf = tarfile.fileobj.read(self._block(self.size))

        # A pax header stores supplemental information dla either
        # the following file (extended) albo all following files
        # (global).
        jeżeli self.type == XGLTYPE:
            pax_headers = tarfile.pax_headers
        inaczej:
            pax_headers = tarfile.pax_headers.copy()

        # Check jeżeli the pax header contains a hdrcharset field. This tells us
        # the encoding of the path, linkpath, uname oraz gname fields. Normally,
        # these fields are UTF-8 encoded but since POSIX.1-2008 tar
        # implementations are allowed to store them jako raw binary strings if
        # the translation to UTF-8 fails.
        match = re.search(br"\d+ hdrcharset=([^\n]+)\n", buf)
        jeżeli match jest nie Nic:
            pax_headers["hdrcharset"] = match.group(1).decode("utf-8")

        # For the time being, we don't care about anything other than "BINARY".
        # The only other value that jest currently allowed by the standard jest
        # "ISO-IR 10646 2000 UTF-8" w other words UTF-8.
        hdrcharset = pax_headers.get("hdrcharset")
        jeżeli hdrcharset == "BINARY":
            encoding = tarfile.encoding
        inaczej:
            encoding = "utf-8"

        # Parse pax header information. A record looks like that:
        # "%d %s=%s\n" % (length, keyword, value). length jest the size
        # of the complete record including the length field itself oraz
        # the newline. keyword oraz value are both UTF-8 encoded strings.
        regex = re.compile(br"(\d+) ([^=]+)=")
        pos = 0
        dopóki Prawda:
            match = regex.match(buf, pos)
            jeżeli nie match:
                przerwij

            length, keyword = match.groups()
            length = int(length)
            value = buf[match.end(2) + 1:match.start(1) + length - 1]

            # Normally, we could just use "utf-8" jako the encoding oraz "strict"
            # jako the error handler, but we better nie take the risk. For
            # example, GNU tar <= 1.23 jest known to store filenames it cannot
            # translate to UTF-8 jako raw strings (unfortunately without a
            # hdrcharset=BINARY header).
            # We first try the strict standard encoding, oraz jeżeli that fails we
            # fall back on the user's encoding oraz error handler.
            keyword = self._decode_pax_field(keyword, "utf-8", "utf-8",
                    tarfile.errors)
            jeżeli keyword w PAX_NAME_FIELDS:
                value = self._decode_pax_field(value, encoding, tarfile.encoding,
                        tarfile.errors)
            inaczej:
                value = self._decode_pax_field(value, "utf-8", "utf-8",
                        tarfile.errors)

            pax_headers[keyword] = value
            pos += length

        # Fetch the next header.
        spróbuj:
            next = self.fromtarfile(tarfile)
        wyjąwszy HeaderError:
            podnieś SubsequentHeaderError("missing albo bad subsequent header")

        # Process GNU sparse information.
        jeżeli "GNU.sparse.map" w pax_headers:
            # GNU extended sparse format version 0.1.
            self._proc_gnusparse_01(next, pax_headers)

        albo_inaczej "GNU.sparse.size" w pax_headers:
            # GNU extended sparse format version 0.0.
            self._proc_gnusparse_00(next, pax_headers, buf)

        albo_inaczej pax_headers.get("GNU.sparse.major") == "1" oraz pax_headers.get("GNU.sparse.minor") == "0":
            # GNU extended sparse format version 1.0.
            self._proc_gnusparse_10(next, pax_headers, tarfile)

        jeżeli self.type w (XHDTYPE, SOLARIS_XHDTYPE):
            # Patch the TarInfo object przy the extended header info.
            next._apply_pax_info(pax_headers, tarfile.encoding, tarfile.errors)
            next.offset = self.offset

            jeżeli "size" w pax_headers:
                # If the extended header replaces the size field,
                # we need to recalculate the offset where the next
                # header starts.
                offset = next.offset_data
                jeżeli next.isreg() albo next.type nie w SUPPORTED_TYPES:
                    offset += next._block(next.size)
                tarfile.offset = offset

        zwróć next

    def _proc_gnusparse_00(self, next, pax_headers, buf):
        """Process a GNU tar extended sparse header, version 0.0.
        """
        offsets = []
        dla match w re.finditer(br"\d+ GNU.sparse.offset=(\d+)\n", buf):
            offsets.append(int(match.group(1)))
        numbytes = []
        dla match w re.finditer(br"\d+ GNU.sparse.numbytes=(\d+)\n", buf):
            numbytes.append(int(match.group(1)))
        next.sparse = list(zip(offsets, numbytes))

    def _proc_gnusparse_01(self, next, pax_headers):
        """Process a GNU tar extended sparse header, version 0.1.
        """
        sparse = [int(x) dla x w pax_headers["GNU.sparse.map"].split(",")]
        next.sparse = list(zip(sparse[::2], sparse[1::2]))

    def _proc_gnusparse_10(self, next, pax_headers, tarfile):
        """Process a GNU tar extended sparse header, version 1.0.
        """
        fields = Nic
        sparse = []
        buf = tarfile.fileobj.read(BLOCKSIZE)
        fields, buf = buf.split(b"\n", 1)
        fields = int(fields)
        dopóki len(sparse) < fields * 2:
            jeżeli b"\n" nie w buf:
                buf += tarfile.fileobj.read(BLOCKSIZE)
            number, buf = buf.split(b"\n", 1)
            sparse.append(int(number))
        next.offset_data = tarfile.fileobj.tell()
        next.sparse = list(zip(sparse[::2], sparse[1::2]))

    def _apply_pax_info(self, pax_headers, encoding, errors):
        """Replace fields przy supplemental information z a previous
           pax extended albo global header.
        """
        dla keyword, value w pax_headers.items():
            jeżeli keyword == "GNU.sparse.name":
                setattr(self, "path", value)
            albo_inaczej keyword == "GNU.sparse.size":
                setattr(self, "size", int(value))
            albo_inaczej keyword == "GNU.sparse.realsize":
                setattr(self, "size", int(value))
            albo_inaczej keyword w PAX_FIELDS:
                jeżeli keyword w PAX_NUMBER_FIELDS:
                    spróbuj:
                        value = PAX_NUMBER_FIELDS[keyword](value)
                    wyjąwszy ValueError:
                        value = 0
                jeżeli keyword == "path":
                    value = value.rstrip("/")
                setattr(self, keyword, value)

        self.pax_headers = pax_headers.copy()

    def _decode_pax_field(self, value, encoding, fallback_encoding, fallback_errors):
        """Decode a single field z a pax record.
        """
        spróbuj:
            zwróć value.decode(encoding, "strict")
        wyjąwszy UnicodeDecodeError:
            zwróć value.decode(fallback_encoding, fallback_errors)

    def _block(self, count):
        """Round up a byte count by BLOCKSIZE oraz zwróć it,
           e.g. _block(834) => 1024.
        """
        blocks, remainder = divmod(count, BLOCKSIZE)
        jeżeli remainder:
            blocks += 1
        zwróć blocks * BLOCKSIZE

    def isreg(self):
        zwróć self.type w REGULAR_TYPES
    def isfile(self):
        zwróć self.isreg()
    def isdir(self):
        zwróć self.type == DIRTYPE
    def issym(self):
        zwróć self.type == SYMTYPE
    def islnk(self):
        zwróć self.type == LNKTYPE
    def ischr(self):
        zwróć self.type == CHRTYPE
    def isblk(self):
        zwróć self.type == BLKTYPE
    def isfifo(self):
        zwróć self.type == FIFOTYPE
    def issparse(self):
        zwróć self.sparse jest nie Nic
    def isdev(self):
        zwróć self.type w (CHRTYPE, BLKTYPE, FIFOTYPE)
# klasa TarInfo

klasa TarFile(object):
    """The TarFile Class provides an interface to tar archives.
    """

    debug = 0                   # May be set z 0 (no msgs) to 3 (all msgs)

    dereference = Nieprawda         # If true, add content of linked file to the
                                # tar file, inaczej the link.

    ignore_zeros = Nieprawda        # If true, skips empty albo invalid blocks oraz
                                # continues processing.

    errorlevel = 1              # If 0, fatal errors only appear w debug
                                # messages (jeżeli debug >= 0). If > 0, errors
                                # are dalejed to the caller jako exceptions.

    format = DEFAULT_FORMAT     # The format to use when creating an archive.

    encoding = ENCODING         # Encoding dla 8-bit character strings.

    errors = Nic               # Error handler dla unicode conversion.

    tarinfo = TarInfo           # The default TarInfo klasa to use.

    fileobject = ExFileObject   # The file-object dla extractfile().

    def __init__(self, name=Nic, mode="r", fileobj=Nic, format=Nic,
            tarinfo=Nic, dereference=Nic, ignore_zeros=Nic, encoding=Nic,
            errors="surrogateescape", pax_headers=Nic, debug=Nic, errorlevel=Nic):
        """Open an (uncompressed) tar archive `name'. `mode' jest either 'r' to
           read z an existing archive, 'a' to append data to an existing
           file albo 'w' to create a new file overwriting an existing one. `mode'
           defaults to 'r'.
           If `fileobj' jest given, it jest used dla reading albo writing data. If it
           can be determined, `mode' jest overridden by `fileobj's mode.
           `fileobj' jest nie closed, when TarFile jest closed.
        """
        modes = {"r": "rb", "a": "r+b", "w": "wb", "x": "xb"}
        jeżeli mode nie w modes:
            podnieś ValueError("mode must be 'r', 'a', 'w' albo 'x'")
        self.mode = mode
        self._mode = modes[mode]

        jeżeli nie fileobj:
            jeżeli self.mode == "a" oraz nie os.path.exists(name):
                # Create nonexistent files w append mode.
                self.mode = "w"
                self._mode = "wb"
            fileobj = bltn_open(name, self._mode)
            self._extfileobj = Nieprawda
        inaczej:
            jeżeli (name jest Nic oraz hasattr(fileobj, "name") oraz
                isinstance(fileobj.name, (str, bytes))):
                name = fileobj.name
            jeżeli hasattr(fileobj, "mode"):
                self._mode = fileobj.mode
            self._extfileobj = Prawda
        self.name = os.path.abspath(name) jeżeli name inaczej Nic
        self.fileobj = fileobj

        # Init attributes.
        jeżeli format jest nie Nic:
            self.format = format
        jeżeli tarinfo jest nie Nic:
            self.tarinfo = tarinfo
        jeżeli dereference jest nie Nic:
            self.dereference = dereference
        jeżeli ignore_zeros jest nie Nic:
            self.ignore_zeros = ignore_zeros
        jeżeli encoding jest nie Nic:
            self.encoding = encoding
        self.errors = errors

        jeżeli pax_headers jest nie Nic oraz self.format == PAX_FORMAT:
            self.pax_headers = pax_headers
        inaczej:
            self.pax_headers = {}

        jeżeli debug jest nie Nic:
            self.debug = debug
        jeżeli errorlevel jest nie Nic:
            self.errorlevel = errorlevel

        # Init datastructures.
        self.closed = Nieprawda
        self.members = []       # list of members jako TarInfo objects
        self._loaded = Nieprawda    # flag jeżeli all members have been read
        self.offset = self.fileobj.tell()
                                # current position w the archive file
        self.inodes = {}        # dictionary caching the inodes of
                                # archive members already added

        spróbuj:
            jeżeli self.mode == "r":
                self.firstmember = Nic
                self.firstmember = self.next()

            jeżeli self.mode == "a":
                # Move to the end of the archive,
                # before the first empty block.
                dopóki Prawda:
                    self.fileobj.seek(self.offset)
                    spróbuj:
                        tarinfo = self.tarinfo.fromtarfile(self)
                        self.members.append(tarinfo)
                    wyjąwszy EOFHeaderError:
                        self.fileobj.seek(self.offset)
                        przerwij
                    wyjąwszy HeaderError jako e:
                        podnieś ReadError(str(e))

            jeżeli self.mode w ("a", "w", "x"):
                self._loaded = Prawda

                jeżeli self.pax_headers:
                    buf = self.tarinfo.create_pax_global_header(self.pax_headers.copy())
                    self.fileobj.write(buf)
                    self.offset += len(buf)
        wyjąwszy:
            jeżeli nie self._extfileobj:
                self.fileobj.close()
            self.closed = Prawda
            podnieś

    #--------------------------------------------------------------------------
    # Below are the classmethods which act jako alternate constructors to the
    # TarFile class. The open() method jest the only one that jest needed for
    # public use; it jest the "super"-constructor oraz jest able to select an
    # adequate "sub"-constructor dla a particular compression using the mapping
    # z OPEN_METH.
    #
    # This concept allows one to subclass TarFile without losing the comfort of
    # the super-constructor. A sub-constructor jest registered oraz made available
    # by adding it to the mapping w OPEN_METH.

    @classmethod
    def open(cls, name=Nic, mode="r", fileobj=Nic, bufsize=RECORDSIZE, **kwargs):
        """Open a tar archive dla reading, writing albo appending. Return
           an appropriate TarFile class.

           mode:
           'r' albo 'r:*' open dla reading przy transparent compression
           'r:'         open dla reading exclusively uncompressed
           'r:gz'       open dla reading przy gzip compression
           'r:bz2'      open dla reading przy bzip2 compression
           'r:xz'       open dla reading przy lzma compression
           'a' albo 'a:'  open dla appending, creating the file jeżeli necessary
           'w' albo 'w:'  open dla writing without compression
           'w:gz'       open dla writing przy gzip compression
           'w:bz2'      open dla writing przy bzip2 compression
           'w:xz'       open dla writing przy lzma compression

           'x' albo 'x:'  create a tarfile exclusively without compression, podnieś
                        an exception jeżeli the file jest already created
           'x:gz'       create an gzip compressed tarfile, podnieś an exception
                        jeżeli the file jest already created
           'x:bz2'      create an bzip2 compressed tarfile, podnieś an exception
                        jeżeli the file jest already created
           'x:xz'       create an lzma compressed tarfile, podnieś an exception
                        jeżeli the file jest already created

           'r|*'        open a stream of tar blocks przy transparent compression
           'r|'         open an uncompressed stream of tar blocks dla reading
           'r|gz'       open a gzip compressed stream of tar blocks
           'r|bz2'      open a bzip2 compressed stream of tar blocks
           'r|xz'       open an lzma compressed stream of tar blocks
           'w|'         open an uncompressed stream dla writing
           'w|gz'       open a gzip compressed stream dla writing
           'w|bz2'      open a bzip2 compressed stream dla writing
           'w|xz'       open an lzma compressed stream dla writing
        """

        jeżeli nie name oraz nie fileobj:
            podnieś ValueError("nothing to open")

        jeżeli mode w ("r", "r:*"):
            # Find out which *open() jest appropriate dla opening the file.
            dla comptype w cls.OPEN_METH:
                func = getattr(cls, cls.OPEN_METH[comptype])
                jeżeli fileobj jest nie Nic:
                    saved_pos = fileobj.tell()
                spróbuj:
                    zwróć func(name, "r", fileobj, **kwargs)
                wyjąwszy (ReadError, CompressionError) jako e:
                    jeżeli fileobj jest nie Nic:
                        fileobj.seek(saved_pos)
                    kontynuuj
            podnieś ReadError("file could nie be opened successfully")

        albo_inaczej ":" w mode:
            filemode, comptype = mode.split(":", 1)
            filemode = filemode albo "r"
            comptype = comptype albo "tar"

            # Select the *open() function according to
            # given compression.
            jeżeli comptype w cls.OPEN_METH:
                func = getattr(cls, cls.OPEN_METH[comptype])
            inaczej:
                podnieś CompressionError("unknown compression type %r" % comptype)
            zwróć func(name, filemode, fileobj, **kwargs)

        albo_inaczej "|" w mode:
            filemode, comptype = mode.split("|", 1)
            filemode = filemode albo "r"
            comptype = comptype albo "tar"

            jeżeli filemode nie w ("r", "w"):
                podnieś ValueError("mode must be 'r' albo 'w'")

            stream = _Stream(name, filemode, comptype, fileobj, bufsize)
            spróbuj:
                t = cls(name, filemode, stream, **kwargs)
            wyjąwszy:
                stream.close()
                podnieś
            t._extfileobj = Nieprawda
            zwróć t

        albo_inaczej mode w ("a", "w", "x"):
            zwróć cls.taropen(name, mode, fileobj, **kwargs)

        podnieś ValueError("undiscernible mode")

    @classmethod
    def taropen(cls, name, mode="r", fileobj=Nic, **kwargs):
        """Open uncompressed tar archive name dla reading albo writing.
        """
        jeżeli mode nie w ("r", "a", "w", "x"):
            podnieś ValueError("mode must be 'r', 'a', 'w' albo 'x'")
        zwróć cls(name, mode, fileobj, **kwargs)

    @classmethod
    def gzopen(cls, name, mode="r", fileobj=Nic, compresslevel=9, **kwargs):
        """Open gzip compressed tar archive name dla reading albo writing.
           Appending jest nie allowed.
        """
        jeżeli mode nie w ("r", "w", "x"):
            podnieś ValueError("mode must be 'r', 'w' albo 'x'")

        spróbuj:
            zaimportuj gzip
            gzip.GzipFile
        wyjąwszy (ImportError, AttributeError):
            podnieś CompressionError("gzip module jest nie available")

        spróbuj:
            fileobj = gzip.GzipFile(name, mode + "b", compresslevel, fileobj)
        wyjąwszy OSError:
            jeżeli fileobj jest nie Nic oraz mode == 'r':
                podnieś ReadError("not a gzip file")
            podnieś

        spróbuj:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        wyjąwszy OSError:
            fileobj.close()
            jeżeli mode == 'r':
                podnieś ReadError("not a gzip file")
            podnieś
        wyjąwszy:
            fileobj.close()
            podnieś
        t._extfileobj = Nieprawda
        zwróć t

    @classmethod
    def bz2open(cls, name, mode="r", fileobj=Nic, compresslevel=9, **kwargs):
        """Open bzip2 compressed tar archive name dla reading albo writing.
           Appending jest nie allowed.
        """
        jeżeli mode nie w ("r", "w", "x"):
            podnieś ValueError("mode must be 'r', 'w' albo 'x'")

        spróbuj:
            zaimportuj bz2
        wyjąwszy ImportError:
            podnieś CompressionError("bz2 module jest nie available")

        fileobj = bz2.BZ2File(fileobj albo name, mode,
                              compresslevel=compresslevel)

        spróbuj:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        wyjąwszy (OSError, EOFError):
            fileobj.close()
            jeżeli mode == 'r':
                podnieś ReadError("not a bzip2 file")
            podnieś
        wyjąwszy:
            fileobj.close()
            podnieś
        t._extfileobj = Nieprawda
        zwróć t

    @classmethod
    def xzopen(cls, name, mode="r", fileobj=Nic, preset=Nic, **kwargs):
        """Open lzma compressed tar archive name dla reading albo writing.
           Appending jest nie allowed.
        """
        jeżeli mode nie w ("r", "w", "x"):
            podnieś ValueError("mode must be 'r', 'w' albo 'x'")

        spróbuj:
            zaimportuj lzma
        wyjąwszy ImportError:
            podnieś CompressionError("lzma module jest nie available")

        fileobj = lzma.LZMAFile(fileobj albo name, mode, preset=preset)

        spróbuj:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        wyjąwszy (lzma.LZMAError, EOFError):
            fileobj.close()
            jeżeli mode == 'r':
                podnieś ReadError("not an lzma file")
            podnieś
        wyjąwszy:
            fileobj.close()
            podnieś
        t._extfileobj = Nieprawda
        zwróć t

    # All *open() methods are registered here.
    OPEN_METH = {
        "tar": "taropen",   # uncompressed tar
        "gz":  "gzopen",    # gzip compressed tar
        "bz2": "bz2open",   # bzip2 compressed tar
        "xz":  "xzopen"     # lzma compressed tar
    }

    #--------------------------------------------------------------------------
    # The public methods which TarFile provides:

    def close(self):
        """Close the TarFile. In write-mode, two finishing zero blocks are
           appended to the archive.
        """
        jeżeli self.closed:
            zwróć

        self.closed = Prawda
        spróbuj:
            jeżeli self.mode w ("a", "w", "x"):
                self.fileobj.write(NUL * (BLOCKSIZE * 2))
                self.offset += (BLOCKSIZE * 2)
                # fill up the end przy zero-blocks
                # (like option -b20 dla tar does)
                blocks, remainder = divmod(self.offset, RECORDSIZE)
                jeżeli remainder > 0:
                    self.fileobj.write(NUL * (RECORDSIZE - remainder))
        w_końcu:
            jeżeli nie self._extfileobj:
                self.fileobj.close()

    def getmember(self, name):
        """Return a TarInfo object dla member `name'. If `name' can nie be
           found w the archive, KeyError jest podnieśd. If a member occurs more
           than once w the archive, its last occurrence jest assumed to be the
           most up-to-date version.
        """
        tarinfo = self._getmember(name)
        jeżeli tarinfo jest Nic:
            podnieś KeyError("filename %r nie found" % name)
        zwróć tarinfo

    def getmembers(self):
        """Return the members of the archive jako a list of TarInfo objects. The
           list has the same order jako the members w the archive.
        """
        self._check()
        jeżeli nie self._loaded:    # jeżeli we want to obtain a list of
            self._load()        # all members, we first have to
                                # scan the whole archive.
        zwróć self.members

    def getnames(self):
        """Return the members of the archive jako a list of their names. It has
           the same order jako the list returned by getmembers().
        """
        zwróć [tarinfo.name dla tarinfo w self.getmembers()]

    def gettarinfo(self, name=Nic, arcname=Nic, fileobj=Nic):
        """Create a TarInfo object dla either the file `name' albo the file
           object `fileobj' (using os.fstat on its file descriptor). You can
           modify some of the TarInfo's attributes before you add it using
           addfile(). If given, `arcname' specifies an alternative name dla the
           file w the archive.
        """
        self._check("awx")

        # When fileobj jest given, replace name by
        # fileobj's real name.
        jeżeli fileobj jest nie Nic:
            name = fileobj.name

        # Building the name of the member w the archive.
        # Backward slashes are converted to forward slashes,
        # Absolute paths are turned to relative paths.
        jeżeli arcname jest Nic:
            arcname = name
        drv, arcname = os.path.splitdrive(arcname)
        arcname = arcname.replace(os.sep, "/")
        arcname = arcname.lstrip("/")

        # Now, fill the TarInfo object with
        # information specific dla the file.
        tarinfo = self.tarinfo()
        tarinfo.tarfile = self

        # Use os.stat albo os.lstat, depending on platform
        # oraz jeżeli symlinks shall be resolved.
        jeżeli fileobj jest Nic:
            jeżeli hasattr(os, "lstat") oraz nie self.dereference:
                statres = os.lstat(name)
            inaczej:
                statres = os.stat(name)
        inaczej:
            statres = os.fstat(fileobj.fileno())
        linkname = ""

        stmd = statres.st_mode
        jeżeli stat.S_ISREG(stmd):
            inode = (statres.st_ino, statres.st_dev)
            jeżeli nie self.dereference oraz statres.st_nlink > 1 oraz \
                    inode w self.inodes oraz arcname != self.inodes[inode]:
                # Is it a hardlink to an already
                # archived file?
                type = LNKTYPE
                linkname = self.inodes[inode]
            inaczej:
                # The inode jest added only jeżeli its valid.
                # For win32 it jest always 0.
                type = REGTYPE
                jeżeli inode[0]:
                    self.inodes[inode] = arcname
        albo_inaczej stat.S_ISDIR(stmd):
            type = DIRTYPE
        albo_inaczej stat.S_ISFIFO(stmd):
            type = FIFOTYPE
        albo_inaczej stat.S_ISLNK(stmd):
            type = SYMTYPE
            linkname = os.readlink(name)
        albo_inaczej stat.S_ISCHR(stmd):
            type = CHRTYPE
        albo_inaczej stat.S_ISBLK(stmd):
            type = BLKTYPE
        inaczej:
            zwróć Nic

        # Fill the TarInfo object przy all
        # information we can get.
        tarinfo.name = arcname
        tarinfo.mode = stmd
        tarinfo.uid = statres.st_uid
        tarinfo.gid = statres.st_gid
        jeżeli type == REGTYPE:
            tarinfo.size = statres.st_size
        inaczej:
            tarinfo.size = 0
        tarinfo.mtime = statres.st_mtime
        tarinfo.type = type
        tarinfo.linkname = linkname
        jeżeli pwd:
            spróbuj:
                tarinfo.uname = pwd.getpwuid(tarinfo.uid)[0]
            wyjąwszy KeyError:
                dalej
        jeżeli grp:
            spróbuj:
                tarinfo.gname = grp.getgrgid(tarinfo.gid)[0]
            wyjąwszy KeyError:
                dalej

        jeżeli type w (CHRTYPE, BLKTYPE):
            jeżeli hasattr(os, "major") oraz hasattr(os, "minor"):
                tarinfo.devmajor = os.major(statres.st_rdev)
                tarinfo.devminor = os.minor(statres.st_rdev)
        zwróć tarinfo

    def list(self, verbose=Prawda, *, members=Nic):
        """Print a table of contents to sys.stdout. If `verbose' jest Nieprawda, only
           the names of the members are printed. If it jest Prawda, an `ls -l'-like
           output jest produced. `members' jest optional oraz must be a subset of the
           list returned by getmembers().
        """
        self._check()

        jeżeli members jest Nic:
            members = self
        dla tarinfo w members:
            jeżeli verbose:
                _safe_print(stat.filemode(tarinfo.mode))
                _safe_print("%s/%s" % (tarinfo.uname albo tarinfo.uid,
                                       tarinfo.gname albo tarinfo.gid))
                jeżeli tarinfo.ischr() albo tarinfo.isblk():
                    _safe_print("%10s" %
                            ("%d,%d" % (tarinfo.devmajor, tarinfo.devminor)))
                inaczej:
                    _safe_print("%10d" % tarinfo.size)
                _safe_print("%d-%02d-%02d %02d:%02d:%02d" \
                            % time.localtime(tarinfo.mtime)[:6])

            _safe_print(tarinfo.name + ("/" jeżeli tarinfo.isdir() inaczej ""))

            jeżeli verbose:
                jeżeli tarinfo.issym():
                    _safe_print("-> " + tarinfo.linkname)
                jeżeli tarinfo.islnk():
                    _safe_print("link to " + tarinfo.linkname)
            print()

    def add(self, name, arcname=Nic, recursive=Prawda, exclude=Nic, *, filter=Nic):
        """Add the file `name' to the archive. `name' may be any type of file
           (directory, fifo, symbolic link, etc.). If given, `arcname'
           specifies an alternative name dla the file w the archive.
           Directories are added recursively by default. This can be avoided by
           setting `recursive' to Nieprawda. `exclude' jest a function that should
           zwróć Prawda dla each filename to be excluded. `filter' jest a function
           that expects a TarInfo object argument oraz returns the changed
           TarInfo object, jeżeli it returns Nic the TarInfo object will be
           excluded z the archive.
        """
        self._check("awx")

        jeżeli arcname jest Nic:
            arcname = name

        # Exclude pathnames.
        jeżeli exclude jest nie Nic:
            zaimportuj warnings
            warnings.warn("use the filter argument instead",
                    DeprecationWarning, 2)
            jeżeli exclude(name):
                self._dbg(2, "tarfile: Excluded %r" % name)
                zwróć

        # Skip jeżeli somebody tries to archive the archive...
        jeżeli self.name jest nie Nic oraz os.path.abspath(name) == self.name:
            self._dbg(2, "tarfile: Skipped %r" % name)
            zwróć

        self._dbg(1, name)

        # Create a TarInfo object z the file.
        tarinfo = self.gettarinfo(name, arcname)

        jeżeli tarinfo jest Nic:
            self._dbg(1, "tarfile: Unsupported type %r" % name)
            zwróć

        # Change albo exclude the TarInfo object.
        jeżeli filter jest nie Nic:
            tarinfo = filter(tarinfo)
            jeżeli tarinfo jest Nic:
                self._dbg(2, "tarfile: Excluded %r" % name)
                zwróć

        # Append the tar header oraz data to the archive.
        jeżeli tarinfo.isreg():
            przy bltn_open(name, "rb") jako f:
                self.addfile(tarinfo, f)

        albo_inaczej tarinfo.isdir():
            self.addfile(tarinfo)
            jeżeli recursive:
                dla f w os.listdir(name):
                    self.add(os.path.join(name, f), os.path.join(arcname, f),
                            recursive, exclude, filter=filter)

        inaczej:
            self.addfile(tarinfo)

    def addfile(self, tarinfo, fileobj=Nic):
        """Add the TarInfo object `tarinfo' to the archive. If `fileobj' jest
           given, tarinfo.size bytes are read z it oraz added to the archive.
           You can create TarInfo objects using gettarinfo().
           On Windows platforms, `fileobj' should always be opened przy mode
           'rb' to avoid irritation about the file size.
        """
        self._check("awx")

        tarinfo = copy.copy(tarinfo)

        buf = tarinfo.tobuf(self.format, self.encoding, self.errors)
        self.fileobj.write(buf)
        self.offset += len(buf)

        # If there's data to follow, append it.
        jeżeli fileobj jest nie Nic:
            copyfileobj(fileobj, self.fileobj, tarinfo.size)
            blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
            jeżeli remainder > 0:
                self.fileobj.write(NUL * (BLOCKSIZE - remainder))
                blocks += 1
            self.offset += blocks * BLOCKSIZE

        self.members.append(tarinfo)

    def extractall(self, path=".", members=Nic, *, numeric_owner=Nieprawda):
        """Extract all members z the archive to the current working
           directory oraz set owner, modification time oraz permissions on
           directories afterwards. `path' specifies a different directory
           to extract to. `members' jest optional oraz must be a subset of the
           list returned by getmembers(). If `numeric_owner` jest Prawda, only
           the numbers dla user/group names are used oraz nie the names.
        """
        directories = []

        jeżeli members jest Nic:
            members = self

        dla tarinfo w members:
            jeżeli tarinfo.isdir():
                # Extract directories przy a safe mode.
                directories.append(tarinfo)
                tarinfo = copy.copy(tarinfo)
                tarinfo.mode = 0o700
            # Do nie set_attrs directories, jako we will do that further down
            self.extract(tarinfo, path, set_attrs=nie tarinfo.isdir(),
                         numeric_owner=numeric_owner)

        # Reverse sort directories.
        directories.sort(key=lambda a: a.name)
        directories.reverse()

        # Set correct owner, mtime oraz filemode on directories.
        dla tarinfo w directories:
            dirpath = os.path.join(path, tarinfo.name)
            spróbuj:
                self.chown(tarinfo, dirpath, numeric_owner=numeric_owner)
                self.utime(tarinfo, dirpath)
                self.chmod(tarinfo, dirpath)
            wyjąwszy ExtractError jako e:
                jeżeli self.errorlevel > 1:
                    podnieś
                inaczej:
                    self._dbg(1, "tarfile: %s" % e)

    def extract(self, member, path="", set_attrs=Prawda, *, numeric_owner=Nieprawda):
        """Extract a member z the archive to the current working directory,
           using its full name. Its file information jest extracted jako accurately
           jako possible. `member' may be a filename albo a TarInfo object. You can
           specify a different directory using `path'. File attributes (owner,
           mtime, mode) are set unless `set_attrs' jest Nieprawda. If `numeric_owner`
           jest Prawda, only the numbers dla user/group names are used oraz nie
           the names.
        """
        self._check("r")

        jeżeli isinstance(member, str):
            tarinfo = self.getmember(member)
        inaczej:
            tarinfo = member

        # Prepare the link target dla makelink().
        jeżeli tarinfo.islnk():
            tarinfo._link_target = os.path.join(path, tarinfo.linkname)

        spróbuj:
            self._extract_member(tarinfo, os.path.join(path, tarinfo.name),
                                 set_attrs=set_attrs,
                                 numeric_owner=numeric_owner)
        wyjąwszy OSError jako e:
            jeżeli self.errorlevel > 0:
                podnieś
            inaczej:
                jeżeli e.filename jest Nic:
                    self._dbg(1, "tarfile: %s" % e.strerror)
                inaczej:
                    self._dbg(1, "tarfile: %s %r" % (e.strerror, e.filename))
        wyjąwszy ExtractError jako e:
            jeżeli self.errorlevel > 1:
                podnieś
            inaczej:
                self._dbg(1, "tarfile: %s" % e)

    def extractfile(self, member):
        """Extract a member z the archive jako a file object. `member' may be
           a filename albo a TarInfo object. If `member' jest a regular file albo a
           link, an io.BufferedReader object jest returned. Otherwise, Nic jest
           returned.
        """
        self._check("r")

        jeżeli isinstance(member, str):
            tarinfo = self.getmember(member)
        inaczej:
            tarinfo = member

        jeżeli tarinfo.isreg() albo tarinfo.type nie w SUPPORTED_TYPES:
            # Members przy unknown types are treated jako regular files.
            zwróć self.fileobject(self, tarinfo)

        albo_inaczej tarinfo.islnk() albo tarinfo.issym():
            jeżeli isinstance(self.fileobj, _Stream):
                # A small but ugly workaround dla the case that someone tries
                # to extract a (sym)link jako a file-object z a non-seekable
                # stream of tar blocks.
                podnieś StreamError("cannot extract (sym)link jako file object")
            inaczej:
                # A (sym)link's file object jest its target's file object.
                zwróć self.extractfile(self._find_link_target(tarinfo))
        inaczej:
            # If there's no data associated przy the member (directory, chrdev,
            # blkdev, etc.), zwróć Nic instead of a file object.
            zwróć Nic

    def _extract_member(self, tarinfo, targetpath, set_attrs=Prawda,
                        numeric_owner=Nieprawda):
        """Extract the TarInfo object tarinfo to a physical
           file called targetpath.
        """
        # Fetch the TarInfo object dla the given name
        # oraz build the destination pathname, replacing
        # forward slashes to platform specific separators.
        targetpath = targetpath.rstrip("/")
        targetpath = targetpath.replace("/", os.sep)

        # Create all upper directories.
        upperdirs = os.path.dirname(targetpath)
        jeżeli upperdirs oraz nie os.path.exists(upperdirs):
            # Create directories that are nie part of the archive with
            # default permissions.
            os.makedirs(upperdirs)

        jeżeli tarinfo.islnk() albo tarinfo.issym():
            self._dbg(1, "%s -> %s" % (tarinfo.name, tarinfo.linkname))
        inaczej:
            self._dbg(1, tarinfo.name)

        jeżeli tarinfo.isreg():
            self.makefile(tarinfo, targetpath)
        albo_inaczej tarinfo.isdir():
            self.makedir(tarinfo, targetpath)
        albo_inaczej tarinfo.isfifo():
            self.makefifo(tarinfo, targetpath)
        albo_inaczej tarinfo.ischr() albo tarinfo.isblk():
            self.makedev(tarinfo, targetpath)
        albo_inaczej tarinfo.islnk() albo tarinfo.issym():
            self.makelink(tarinfo, targetpath)
        albo_inaczej tarinfo.type nie w SUPPORTED_TYPES:
            self.makeunknown(tarinfo, targetpath)
        inaczej:
            self.makefile(tarinfo, targetpath)

        jeżeli set_attrs:
            self.chown(tarinfo, targetpath, numeric_owner)
            jeżeli nie tarinfo.issym():
                self.chmod(tarinfo, targetpath)
                self.utime(tarinfo, targetpath)

    #--------------------------------------------------------------------------
    # Below are the different file methods. They are called via
    # _extract_member() when extract() jest called. They can be replaced w a
    # subclass to implement other functionality.

    def makedir(self, tarinfo, targetpath):
        """Make a directory called targetpath.
        """
        spróbuj:
            # Use a safe mode dla the directory, the real mode jest set
            # later w _extract_member().
            os.mkdir(targetpath, 0o700)
        wyjąwszy FileExistsError:
            dalej

    def makefile(self, tarinfo, targetpath):
        """Make a file called targetpath.
        """
        source = self.fileobj
        source.seek(tarinfo.offset_data)
        przy bltn_open(targetpath, "wb") jako target:
            jeżeli tarinfo.sparse jest nie Nic:
                dla offset, size w tarinfo.sparse:
                    target.seek(offset)
                    copyfileobj(source, target, size, ReadError)
            inaczej:
                copyfileobj(source, target, tarinfo.size, ReadError)
            target.seek(tarinfo.size)
            target.truncate()

    def makeunknown(self, tarinfo, targetpath):
        """Make a file z a TarInfo object przy an unknown type
           at targetpath.
        """
        self.makefile(tarinfo, targetpath)
        self._dbg(1, "tarfile: Unknown file type %r, " \
                     "extracted jako regular file." % tarinfo.type)

    def makefifo(self, tarinfo, targetpath):
        """Make a fifo called targetpath.
        """
        jeżeli hasattr(os, "mkfifo"):
            os.mkfifo(targetpath)
        inaczej:
            podnieś ExtractError("fifo nie supported by system")

    def makedev(self, tarinfo, targetpath):
        """Make a character albo block device called targetpath.
        """
        jeżeli nie hasattr(os, "mknod") albo nie hasattr(os, "makedev"):
            podnieś ExtractError("special devices nie supported by system")

        mode = tarinfo.mode
        jeżeli tarinfo.isblk():
            mode |= stat.S_IFBLK
        inaczej:
            mode |= stat.S_IFCHR

        os.mknod(targetpath, mode,
                 os.makedev(tarinfo.devmajor, tarinfo.devminor))

    def makelink(self, tarinfo, targetpath):
        """Make a (symbolic) link called targetpath. If it cannot be created
          (platform limitation), we try to make a copy of the referenced file
          instead of a link.
        """
        spróbuj:
            # For systems that support symbolic oraz hard links.
            jeżeli tarinfo.issym():
                os.symlink(tarinfo.linkname, targetpath)
            inaczej:
                # See extract().
                jeżeli os.path.exists(tarinfo._link_target):
                    os.link(tarinfo._link_target, targetpath)
                inaczej:
                    self._extract_member(self._find_link_target(tarinfo),
                                         targetpath)
        wyjąwszy symlink_exception:
            spróbuj:
                self._extract_member(self._find_link_target(tarinfo),
                                     targetpath)
            wyjąwszy KeyError:
                podnieś ExtractError("unable to resolve link inside archive")

    def chown(self, tarinfo, targetpath, numeric_owner):
        """Set owner of targetpath according to tarinfo. If numeric_owner
           jest Prawda, use .gid/.uid instead of .gname/.uname.
        """
        jeżeli pwd oraz hasattr(os, "geteuid") oraz os.geteuid() == 0:
            # We have to be root to do so.
            jeżeli numeric_owner:
                g = tarinfo.gid
                u = tarinfo.uid
            inaczej:
                spróbuj:
                    g = grp.getgrnam(tarinfo.gname)[2]
                wyjąwszy KeyError:
                    g = tarinfo.gid
                spróbuj:
                    u = pwd.getpwnam(tarinfo.uname)[2]
                wyjąwszy KeyError:
                    u = tarinfo.uid
            spróbuj:
                jeżeli tarinfo.issym() oraz hasattr(os, "lchown"):
                    os.lchown(targetpath, u, g)
                inaczej:
                    os.chown(targetpath, u, g)
            wyjąwszy OSError jako e:
                podnieś ExtractError("could nie change owner")

    def chmod(self, tarinfo, targetpath):
        """Set file permissions of targetpath according to tarinfo.
        """
        jeżeli hasattr(os, 'chmod'):
            spróbuj:
                os.chmod(targetpath, tarinfo.mode)
            wyjąwszy OSError jako e:
                podnieś ExtractError("could nie change mode")

    def utime(self, tarinfo, targetpath):
        """Set modification time of targetpath according to tarinfo.
        """
        jeżeli nie hasattr(os, 'utime'):
            zwróć
        spróbuj:
            os.utime(targetpath, (tarinfo.mtime, tarinfo.mtime))
        wyjąwszy OSError jako e:
            podnieś ExtractError("could nie change modification time")

    #--------------------------------------------------------------------------
    def next(self):
        """Return the next member of the archive jako a TarInfo object, when
           TarFile jest opened dla reading. Return Nic jeżeli there jest no more
           available.
        """
        self._check("ra")
        jeżeli self.firstmember jest nie Nic:
            m = self.firstmember
            self.firstmember = Nic
            zwróć m

        # Advance the file pointer.
        jeżeli self.offset != self.fileobj.tell():
            self.fileobj.seek(self.offset - 1)
            jeżeli nie self.fileobj.read(1):
                podnieś ReadError("unexpected end of data")

        # Read the next block.
        tarinfo = Nic
        dopóki Prawda:
            spróbuj:
                tarinfo = self.tarinfo.fromtarfile(self)
            wyjąwszy EOFHeaderError jako e:
                jeżeli self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    kontynuuj
            wyjąwszy InvalidHeaderError jako e:
                jeżeli self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    kontynuuj
                albo_inaczej self.offset == 0:
                    podnieś ReadError(str(e))
            wyjąwszy EmptyHeaderError:
                jeżeli self.offset == 0:
                    podnieś ReadError("empty file")
            wyjąwszy TruncatedHeaderError jako e:
                jeżeli self.offset == 0:
                    podnieś ReadError(str(e))
            wyjąwszy SubsequentHeaderError jako e:
                podnieś ReadError(str(e))
            przerwij

        jeżeli tarinfo jest nie Nic:
            self.members.append(tarinfo)
        inaczej:
            self._loaded = Prawda

        zwróć tarinfo

    #--------------------------------------------------------------------------
    # Little helper methods:

    def _getmember(self, name, tarinfo=Nic, normalize=Nieprawda):
        """Find an archive member by name z bottom to top.
           If tarinfo jest given, it jest used jako the starting point.
        """
        # Ensure that all members have been loaded.
        members = self.getmembers()

        # Limit the member search list up to tarinfo.
        jeżeli tarinfo jest nie Nic:
            members = members[:members.index(tarinfo)]

        jeżeli normalize:
            name = os.path.normpath(name)

        dla member w reversed(members):
            jeżeli normalize:
                member_name = os.path.normpath(member.name)
            inaczej:
                member_name = member.name

            jeżeli name == member_name:
                zwróć member

    def _load(self):
        """Read through the entire archive file oraz look dla readable
           members.
        """
        dopóki Prawda:
            tarinfo = self.next()
            jeżeli tarinfo jest Nic:
                przerwij
        self._loaded = Prawda

    def _check(self, mode=Nic):
        """Check jeżeli TarFile jest still open, oraz jeżeli the operation's mode
           corresponds to TarFile's mode.
        """
        jeżeli self.closed:
            podnieś OSError("%s jest closed" % self.__class__.__name__)
        jeżeli mode jest nie Nic oraz self.mode nie w mode:
            podnieś OSError("bad operation dla mode %r" % self.mode)

    def _find_link_target(self, tarinfo):
        """Find the target member of a symlink albo hardlink member w the
           archive.
        """
        jeżeli tarinfo.issym():
            # Always search the entire archive.
            linkname = "/".join(filter(Nic, (os.path.dirname(tarinfo.name), tarinfo.linkname)))
            limit = Nic
        inaczej:
            # Search the archive before the link, because a hard link jest
            # just a reference to an already archived file.
            linkname = tarinfo.linkname
            limit = tarinfo

        member = self._getmember(linkname, tarinfo=limit, normalize=Prawda)
        jeżeli member jest Nic:
            podnieś KeyError("linkname %r nie found" % linkname)
        zwróć member

    def __iter__(self):
        """Provide an iterator object.
        """
        jeżeli self._loaded:
            zwróć iter(self.members)
        inaczej:
            zwróć TarIter(self)

    def _dbg(self, level, msg):
        """Write debugging output to sys.stderr.
        """
        jeżeli level <= self.debug:
            print(msg, file=sys.stderr)

    def __enter__(self):
        self._check()
        zwróć self

    def __exit__(self, type, value, traceback):
        jeżeli type jest Nic:
            self.close()
        inaczej:
            # An exception occurred. We must nie call close() because
            # it would try to write end-of-archive blocks oraz padding.
            jeżeli nie self._extfileobj:
                self.fileobj.close()
            self.closed = Prawda
# klasa TarFile

klasa TarIter:
    """Iterator Class.

       dla tarinfo w TarFile(...):
           suite...
    """

    def __init__(self, tarfile):
        """Construct a TarIter object.
        """
        self.tarfile = tarfile
        self.index = 0
    def __iter__(self):
        """Return iterator object.
        """
        zwróć self
    def __next__(self):
        """Return the next item using TarFile's next() method.
           When all members have been read, set TarFile jako _loaded.
        """
        # Fix dla SF #1100429: Under rare circumstances it can
        # happen that getmembers() jest called during iteration,
        # which will cause TarIter to stop prematurely.

        jeżeli self.index == 0 oraz self.tarfile.firstmember jest nie Nic:
            tarinfo = self.tarfile.next()
        albo_inaczej self.index < len(self.tarfile.members):
            tarinfo = self.tarfile.members[self.index]
        albo_inaczej nie self.tarfile._loaded:
            tarinfo = self.tarfile.next()
            jeżeli nie tarinfo:
                self.tarfile._loaded = Prawda
                podnieś StopIteration
        inaczej:
            podnieś StopIteration
        self.index += 1
        zwróć tarinfo

#--------------------
# exported functions
#--------------------
def is_tarfile(name):
    """Return Prawda jeżeli name points to a tar archive that we
       are able to handle, inaczej zwróć Nieprawda.
    """
    spróbuj:
        t = open(name)
        t.close()
        zwróć Prawda
    wyjąwszy TarError:
        zwróć Nieprawda

open = TarFile.open


def main():
    zaimportuj argparse

    description = 'A simple command line interface dla tarfile module.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--verbose', action='store_true', default=Nieprawda,
                        help='Verbose output')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--list', metavar='<tarfile>',
                       help='Show listing of a tarfile')
    group.add_argument('-e', '--extract', nargs='+',
                       metavar=('<tarfile>', '<output_dir>'),
                       help='Extract tarfile into target dir')
    group.add_argument('-c', '--create', nargs='+',
                       metavar=('<name>', '<file>'),
                       help='Create tarfile z sources')
    group.add_argument('-t', '--test', metavar='<tarfile>',
                       help='Test jeżeli a tarfile jest valid')
    args = parser.parse_args()

    jeżeli args.test:
        src = args.test
        jeżeli is_tarfile(src):
            przy open(src, 'r') jako tar:
                tar.getmembers()
                print(tar.getmembers(), file=sys.stderr)
            jeżeli args.verbose:
                print('{!r} jest a tar archive.'.format(src))
        inaczej:
            parser.exit(1, '{!r} jest nie a tar archive.\n'.format(src))

    albo_inaczej args.list:
        src = args.list
        jeżeli is_tarfile(src):
            przy TarFile.open(src, 'r:*') jako tf:
                tf.list(verbose=args.verbose)
        inaczej:
            parser.exit(1, '{!r} jest nie a tar archive.\n'.format(src))

    albo_inaczej args.extract:
        jeżeli len(args.extract) == 1:
            src = args.extract[0]
            curdir = os.curdir
        albo_inaczej len(args.extract) == 2:
            src, curdir = args.extract
        inaczej:
            parser.exit(1, parser.format_help())

        jeżeli is_tarfile(src):
            przy TarFile.open(src, 'r:*') jako tf:
                tf.extractall(path=curdir)
            jeżeli args.verbose:
                jeżeli curdir == '.':
                    msg = '{!r} file jest extracted.'.format(src)
                inaczej:
                    msg = ('{!r} file jest extracted '
                           'into {!r} directory.').format(src, curdir)
                print(msg)
        inaczej:
            parser.exit(1, '{!r} jest nie a tar archive.\n'.format(src))

    albo_inaczej args.create:
        tar_name = args.create.pop(0)
        _, ext = os.path.splitext(tar_name)
        compressions = {
            # gz
            '.gz': 'gz',
            '.tgz': 'gz',
            # xz
            '.xz': 'xz',
            '.txz': 'xz',
            # bz2
            '.bz2': 'bz2',
            '.tbz': 'bz2',
            '.tbz2': 'bz2',
            '.tb2': 'bz2',
        }
        tar_mode = 'w:' + compressions[ext] jeżeli ext w compressions inaczej 'w'
        tar_files = args.create

        przy TarFile.open(tar_name, tar_mode) jako tf:
            dla file_name w tar_files:
                tf.add(file_name)

        jeżeli args.verbose:
            print('{!r} file created.'.format(tar_name))

    inaczej:
        parser.exit(1, parser.format_help())

jeżeli __name__ == '__main__':
    main()
