"""
Read oraz write ZIP files.

XXX references to utf-8 need further investigation.
"""
zaimportuj io
zaimportuj os
zaimportuj re
zaimportuj importlib.util
zaimportuj sys
zaimportuj time
zaimportuj stat
zaimportuj shutil
zaimportuj struct
zaimportuj binascii
zaimportuj threading


spróbuj:
    zaimportuj zlib # We may need its compression method
    crc32 = zlib.crc32
wyjąwszy ImportError:
    zlib = Nic
    crc32 = binascii.crc32

spróbuj:
    zaimportuj bz2 # We may need its compression method
wyjąwszy ImportError:
    bz2 = Nic

spróbuj:
    zaimportuj lzma # We may need its compression method
wyjąwszy ImportError:
    lzma = Nic

__all__ = ["BadZipFile", "BadZipfile", "error",
           "ZIP_STORED", "ZIP_DEFLATED", "ZIP_BZIP2", "ZIP_LZMA",
           "is_zipfile", "ZipInfo", "ZipFile", "PyZipFile", "LargeZipFile"]

klasa BadZipFile(Exception):
    dalej


klasa LargeZipFile(Exception):
    """
    Raised when writing a zipfile, the zipfile requires ZIP64 extensions
    oraz those extensions are disabled.
    """

error = BadZipfile = BadZipFile      # Pre-3.2 compatibility names


ZIP64_LIMIT = (1 << 31) - 1
ZIP_FILECOUNT_LIMIT = (1 << 16) - 1
ZIP_MAX_COMMENT = (1 << 16) - 1

# constants dla Zip file compression methods
ZIP_STORED = 0
ZIP_DEFLATED = 8
ZIP_BZIP2 = 12
ZIP_LZMA = 14
# Other ZIP compression methods nie supported

DEFAULT_VERSION = 20
ZIP64_VERSION = 45
BZIP2_VERSION = 46
LZMA_VERSION = 63
# we recognize (but nie necessarily support) all features up to that version
MAX_EXTRACT_VERSION = 63

# Below are some formats oraz associated data dla reading/writing headers using
# the struct module.  The names oraz structures of headers/records are those used
# w the PKWARE description of the ZIP file format:
#     http://www.pkware.com/documents/casestudies/APPNOTE.TXT
# (URL valid jako of January 2008)

# The "end of central directory" structure, magic number, size, oraz indices
# (section V.I w the format document)
structEndArchive = b"<4s4H2LH"
stringEndArchive = b"PK\005\006"
sizeEndCentDir = struct.calcsize(structEndArchive)

_ECD_SIGNATURE = 0
_ECD_DISK_NUMBER = 1
_ECD_DISK_START = 2
_ECD_ENTRIES_THIS_DISK = 3
_ECD_ENTRIES_TOTAL = 4
_ECD_SIZE = 5
_ECD_OFFSET = 6
_ECD_COMMENT_SIZE = 7
# These last two indices are nie part of the structure jako defined w the
# spec, but they are used internally by this module jako a convenience
_ECD_COMMENT = 8
_ECD_LOCATION = 9

# The "central directory" structure, magic number, size, oraz indices
# of entries w the structure (section V.F w the format document)
structCentralDir = "<4s4B4HL2L5H2L"
stringCentralDir = b"PK\001\002"
sizeCentralDir = struct.calcsize(structCentralDir)

# indexes of entries w the central directory structure
_CD_SIGNATURE = 0
_CD_CREATE_VERSION = 1
_CD_CREATE_SYSTEM = 2
_CD_EXTRACT_VERSION = 3
_CD_EXTRACT_SYSTEM = 4
_CD_FLAG_BITS = 5
_CD_COMPRESS_TYPE = 6
_CD_TIME = 7
_CD_DATE = 8
_CD_CRC = 9
_CD_COMPRESSED_SIZE = 10
_CD_UNCOMPRESSED_SIZE = 11
_CD_FILENAME_LENGTH = 12
_CD_EXTRA_FIELD_LENGTH = 13
_CD_COMMENT_LENGTH = 14
_CD_DISK_NUMBER_START = 15
_CD_INTERNAL_FILE_ATTRIBUTES = 16
_CD_EXTERNAL_FILE_ATTRIBUTES = 17
_CD_LOCAL_HEADER_OFFSET = 18

# The "local file header" structure, magic number, size, oraz indices
# (section V.A w the format document)
structFileHeader = "<4s2B4HL2L2H"
stringFileHeader = b"PK\003\004"
sizeFileHeader = struct.calcsize(structFileHeader)

_FH_SIGNATURE = 0
_FH_EXTRACT_VERSION = 1
_FH_EXTRACT_SYSTEM = 2
_FH_GENERAL_PURPOSE_FLAG_BITS = 3
_FH_COMPRESSION_METHOD = 4
_FH_LAST_MOD_TIME = 5
_FH_LAST_MOD_DATE = 6
_FH_CRC = 7
_FH_COMPRESSED_SIZE = 8
_FH_UNCOMPRESSED_SIZE = 9
_FH_FILENAME_LENGTH = 10
_FH_EXTRA_FIELD_LENGTH = 11

# The "Zip64 end of central directory locator" structure, magic number, oraz size
structEndArchive64Locator = "<4sLQL"
stringEndArchive64Locator = b"PK\x06\x07"
sizeEndCentDir64Locator = struct.calcsize(structEndArchive64Locator)

# The "Zip64 end of central directory" record, magic number, size, oraz indices
# (section V.G w the format document)
structEndArchive64 = "<4sQ2H2L4Q"
stringEndArchive64 = b"PK\x06\x06"
sizeEndCentDir64 = struct.calcsize(structEndArchive64)

_CD64_SIGNATURE = 0
_CD64_DIRECTORY_RECSIZE = 1
_CD64_CREATE_VERSION = 2
_CD64_EXTRACT_VERSION = 3
_CD64_DISK_NUMBER = 4
_CD64_DISK_NUMBER_START = 5
_CD64_NUMBER_ENTRIES_THIS_DISK = 6
_CD64_NUMBER_ENTRIES_TOTAL = 7
_CD64_DIRECTORY_SIZE = 8
_CD64_OFFSET_START_CENTDIR = 9

def _check_zipfile(fp):
    spróbuj:
        jeżeli _EndRecData(fp):
            zwróć Prawda         # file has correct magic number
    wyjąwszy OSError:
        dalej
    zwróć Nieprawda

def is_zipfile(filename):
    """Quickly see jeżeli a file jest a ZIP file by checking the magic number.

    The filename argument may be a file albo file-like object too.
    """
    result = Nieprawda
    spróbuj:
        jeżeli hasattr(filename, "read"):
            result = _check_zipfile(fp=filename)
        inaczej:
            przy open(filename, "rb") jako fp:
                result = _check_zipfile(fp)
    wyjąwszy OSError:
        dalej
    zwróć result

def _EndRecData64(fpin, offset, endrec):
    """
    Read the ZIP64 end-of-archive records oraz use that to update endrec
    """
    spróbuj:
        fpin.seek(offset - sizeEndCentDir64Locator, 2)
    wyjąwszy OSError:
        # If the seek fails, the file jest nie large enough to contain a ZIP64
        # end-of-archive record, so just zwróć the end record we were given.
        zwróć endrec

    data = fpin.read(sizeEndCentDir64Locator)
    jeżeli len(data) != sizeEndCentDir64Locator:
        zwróć endrec
    sig, diskno, reloff, disks = struct.unpack(structEndArchive64Locator, data)
    jeżeli sig != stringEndArchive64Locator:
        zwróć endrec

    jeżeli diskno != 0 albo disks != 1:
        podnieś BadZipFile("zipfiles that span multiple disks are nie supported")

    # Assume no 'zip64 extensible data'
    fpin.seek(offset - sizeEndCentDir64Locator - sizeEndCentDir64, 2)
    data = fpin.read(sizeEndCentDir64)
    jeżeli len(data) != sizeEndCentDir64:
        zwróć endrec
    sig, sz, create_version, read_version, disk_num, disk_dir, \
        dircount, dircount2, dirsize, diroffset = \
        struct.unpack(structEndArchive64, data)
    jeżeli sig != stringEndArchive64:
        zwróć endrec

    # Update the original endrec using data z the ZIP64 record
    endrec[_ECD_SIGNATURE] = sig
    endrec[_ECD_DISK_NUMBER] = disk_num
    endrec[_ECD_DISK_START] = disk_dir
    endrec[_ECD_ENTRIES_THIS_DISK] = dircount
    endrec[_ECD_ENTRIES_TOTAL] = dircount2
    endrec[_ECD_SIZE] = dirsize
    endrec[_ECD_OFFSET] = diroffset
    zwróć endrec


def _EndRecData(fpin):
    """Return data z the "End of Central Directory" record, albo Nic.

    The data jest a list of the nine items w the ZIP "End of central dir"
    record followed by a tenth item, the file seek offset of this record."""

    # Determine file size
    fpin.seek(0, 2)
    filesize = fpin.tell()

    # Check to see jeżeli this jest ZIP file przy no archive comment (the
    # "end of central directory" structure should be the last item w the
    # file jeżeli this jest the case).
    spróbuj:
        fpin.seek(-sizeEndCentDir, 2)
    wyjąwszy OSError:
        zwróć Nic
    data = fpin.read()
    jeżeli (len(data) == sizeEndCentDir oraz
        data[0:4] == stringEndArchive oraz
        data[-2:] == b"\000\000"):
        # the signature jest correct oraz there's no comment, unpack structure
        endrec = struct.unpack(structEndArchive, data)
        endrec=list(endrec)

        # Append a blank comment oraz record start offset
        endrec.append(b"")
        endrec.append(filesize - sizeEndCentDir)

        # Try to read the "Zip64 end of central directory" structure
        zwróć _EndRecData64(fpin, -sizeEndCentDir, endrec)

    # Either this jest nie a ZIP file, albo it jest a ZIP file przy an archive
    # comment.  Search the end of the file dla the "end of central directory"
    # record signature. The comment jest the last item w the ZIP file oraz may be
    # up to 64K long.  It jest assumed that the "end of central directory" magic
    # number does nie appear w the comment.
    maxCommentStart = max(filesize - (1 << 16) - sizeEndCentDir, 0)
    fpin.seek(maxCommentStart, 0)
    data = fpin.read()
    start = data.rfind(stringEndArchive)
    jeżeli start >= 0:
        # found the magic number; attempt to unpack oraz interpret
        recData = data[start:start+sizeEndCentDir]
        jeżeli len(recData) != sizeEndCentDir:
            # Zip file jest corrupted.
            zwróć Nic
        endrec = list(struct.unpack(structEndArchive, recData))
        commentSize = endrec[_ECD_COMMENT_SIZE] #as claimed by the zip file
        comment = data[start+sizeEndCentDir:start+sizeEndCentDir+commentSize]
        endrec.append(comment)
        endrec.append(maxCommentStart + start)

        # Try to read the "Zip64 end of central directory" structure
        zwróć _EndRecData64(fpin, maxCommentStart + start - filesize,
                             endrec)

    # Unable to find a valid end of central directory structure
    zwróć Nic


klasa ZipInfo (object):
    """Class przy attributes describing each file w the ZIP archive."""

    __slots__ = (
        'orig_filename',
        'filename',
        'date_time',
        'compress_type',
        'comment',
        'extra',
        'create_system',
        'create_version',
        'extract_version',
        'reserved',
        'flag_bits',
        'volume',
        'internal_attr',
        'external_attr',
        'header_offset',
        'CRC',
        'compress_size',
        'file_size',
        '_raw_time',
    )

    def __init__(self, filename="NoName", date_time=(1980,1,1,0,0,0)):
        self.orig_filename = filename   # Original file name w archive

        # Terminate the file name at the first null byte.  Null bytes w file
        # names are used jako tricks by viruses w archives.
        null_byte = filename.find(chr(0))
        jeżeli null_byte >= 0:
            filename = filename[0:null_byte]
        # This jest used to ensure paths w generated ZIP files always use
        # forward slashes jako the directory separator, jako required by the
        # ZIP format specification.
        jeżeli os.sep != "/" oraz os.sep w filename:
            filename = filename.replace(os.sep, "/")

        self.filename = filename        # Normalized file name
        self.date_time = date_time      # year, month, day, hour, min, sec

        jeżeli date_time[0] < 1980:
            podnieś ValueError('ZIP does nie support timestamps before 1980')

        # Standard values:
        self.compress_type = ZIP_STORED # Type of compression dla the file
        self.comment = b""              # Comment dla each file
        self.extra = b""                # ZIP extra data
        jeżeli sys.platform == 'win32':
            self.create_system = 0          # System which created ZIP archive
        inaczej:
            # Assume everything inaczej jest unix-y
            self.create_system = 3          # System which created ZIP archive
        self.create_version = DEFAULT_VERSION  # Version which created ZIP archive
        self.extract_version = DEFAULT_VERSION # Version needed to extract archive
        self.reserved = 0               # Must be zero
        self.flag_bits = 0              # ZIP flag bits
        self.volume = 0                 # Volume number of file header
        self.internal_attr = 0          # Internal attributes
        self.external_attr = 0          # External file attributes
        # Other attributes are set by klasa ZipFile:
        # header_offset         Byte offset to the file header
        # CRC                   CRC-32 of the uncompressed file
        # compress_size         Size of the compressed file
        # file_size             Size of the uncompressed file

    def __repr__(self):
        result = ['<%s filename=%r' % (self.__class__.__name__, self.filename)]
        jeżeli self.compress_type != ZIP_STORED:
            result.append(' compress_type=%s' %
                          compressor_names.get(self.compress_type,
                                               self.compress_type))
        hi = self.external_attr >> 16
        lo = self.external_attr & 0xFFFF
        jeżeli hi:
            result.append(' filemode=%r' % stat.filemode(hi))
        jeżeli lo:
            result.append(' external_attr=%#x' % lo)
        isdir = self.filename[-1:] == '/'
        jeżeli nie isdir albo self.file_size:
            result.append(' file_size=%r' % self.file_size)
        jeżeli ((nie isdir albo self.compress_size) oraz
            (self.compress_type != ZIP_STORED albo
             self.file_size != self.compress_size)):
            result.append(' compress_size=%r' % self.compress_size)
        result.append('>')
        zwróć ''.join(result)

    def FileHeader(self, zip64=Nic):
        """Return the per-file header jako a string."""
        dt = self.date_time
        dosdate = (dt[0] - 1980) << 9 | dt[1] << 5 | dt[2]
        dostime = dt[3] << 11 | dt[4] << 5 | (dt[5] // 2)
        jeżeli self.flag_bits & 0x08:
            # Set these to zero because we write them after the file data
            CRC = compress_size = file_size = 0
        inaczej:
            CRC = self.CRC
            compress_size = self.compress_size
            file_size = self.file_size

        extra = self.extra

        min_version = 0
        jeżeli zip64 jest Nic:
            zip64 = file_size > ZIP64_LIMIT albo compress_size > ZIP64_LIMIT
        jeżeli zip64:
            fmt = '<HHQQ'
            extra = extra + struct.pack(fmt,
                                        1, struct.calcsize(fmt)-4, file_size, compress_size)
        jeżeli file_size > ZIP64_LIMIT albo compress_size > ZIP64_LIMIT:
            jeżeli nie zip64:
                podnieś LargeZipFile("Filesize would require ZIP64 extensions")
            # File jest larger than what fits into a 4 byte integer,
            # fall back to the ZIP64 extension
            file_size = 0xffffffff
            compress_size = 0xffffffff
            min_version = ZIP64_VERSION

        jeżeli self.compress_type == ZIP_BZIP2:
            min_version = max(BZIP2_VERSION, min_version)
        albo_inaczej self.compress_type == ZIP_LZMA:
            min_version = max(LZMA_VERSION, min_version)

        self.extract_version = max(min_version, self.extract_version)
        self.create_version = max(min_version, self.create_version)
        filename, flag_bits = self._encodeFilenameFlags()
        header = struct.pack(structFileHeader, stringFileHeader,
                             self.extract_version, self.reserved, flag_bits,
                             self.compress_type, dostime, dosdate, CRC,
                             compress_size, file_size,
                             len(filename), len(extra))
        zwróć header + filename + extra

    def _encodeFilenameFlags(self):
        spróbuj:
            zwróć self.filename.encode('ascii'), self.flag_bits
        wyjąwszy UnicodeEncodeError:
            zwróć self.filename.encode('utf-8'), self.flag_bits | 0x800

    def _decodeExtra(self):
        # Try to decode the extra field.
        extra = self.extra
        unpack = struct.unpack
        dopóki len(extra) >= 4:
            tp, ln = unpack('<HH', extra[:4])
            jeżeli tp == 1:
                jeżeli ln >= 24:
                    counts = unpack('<QQQ', extra[4:28])
                albo_inaczej ln == 16:
                    counts = unpack('<QQ', extra[4:20])
                albo_inaczej ln == 8:
                    counts = unpack('<Q', extra[4:12])
                albo_inaczej ln == 0:
                    counts = ()
                inaczej:
                    podnieś RuntimeError("Corrupt extra field %s"%(ln,))

                idx = 0

                # ZIP64 extension (large files and/or large archives)
                jeżeli self.file_size w (0xffffffffffffffff, 0xffffffff):
                    self.file_size = counts[idx]
                    idx += 1

                jeżeli self.compress_size == 0xFFFFFFFF:
                    self.compress_size = counts[idx]
                    idx += 1

                jeżeli self.header_offset == 0xffffffff:
                    old = self.header_offset
                    self.header_offset = counts[idx]
                    idx+=1

            extra = extra[ln+4:]


klasa _ZipDecrypter:
    """Class to handle decryption of files stored within a ZIP archive.

    ZIP supports a dalejword-based form of encryption. Even though known
    plaintext attacks have been found against it, it jest still useful
    to be able to get data out of such a file.

    Usage:
        zd = _ZipDecrypter(mypwd)
        plain_char = zd(cypher_char)
        plain_text = map(zd, cypher_text)
    """

    def _GenerateCRCTable():
        """Generate a CRC-32 table.

        ZIP encryption uses the CRC32 one-byte primitive dla scrambling some
        internal keys. We noticed that a direct implementation jest faster than
        relying on binascii.crc32().
        """
        poly = 0xedb88320
        table = [0] * 256
        dla i w range(256):
            crc = i
            dla j w range(8):
                jeżeli crc & 1:
                    crc = ((crc >> 1) & 0x7FFFFFFF) ^ poly
                inaczej:
                    crc = ((crc >> 1) & 0x7FFFFFFF)
            table[i] = crc
        zwróć table
    crctable = Nic

    def _crc32(self, ch, crc):
        """Compute the CRC32 primitive on one byte."""
        zwróć ((crc >> 8) & 0xffffff) ^ self.crctable[(crc ^ ch) & 0xff]

    def __init__(self, pwd):
        jeżeli _ZipDecrypter.crctable jest Nic:
            _ZipDecrypter.crctable = _ZipDecrypter._GenerateCRCTable()
        self.key0 = 305419896
        self.key1 = 591751049
        self.key2 = 878082192
        dla p w pwd:
            self._UpdateKeys(p)

    def _UpdateKeys(self, c):
        self.key0 = self._crc32(c, self.key0)
        self.key1 = (self.key1 + (self.key0 & 255)) & 4294967295
        self.key1 = (self.key1 * 134775813 + 1) & 4294967295
        self.key2 = self._crc32((self.key1 >> 24) & 255, self.key2)

    def __call__(self, c):
        """Decrypt a single character."""
        assert isinstance(c, int)
        k = self.key2 | 2
        c = c ^ (((k * (k^1)) >> 8) & 255)
        self._UpdateKeys(c)
        zwróć c


klasa LZMACompressor:

    def __init__(self):
        self._comp = Nic

    def _init(self):
        props = lzma._encode_filter_properties({'id': lzma.FILTER_LZMA1})
        self._comp = lzma.LZMACompressor(lzma.FORMAT_RAW, filters=[
            lzma._decode_filter_properties(lzma.FILTER_LZMA1, props)
        ])
        zwróć struct.pack('<BBH', 9, 4, len(props)) + props

    def compress(self, data):
        jeżeli self._comp jest Nic:
            zwróć self._init() + self._comp.compress(data)
        zwróć self._comp.compress(data)

    def flush(self):
        jeżeli self._comp jest Nic:
            zwróć self._init() + self._comp.flush()
        zwróć self._comp.flush()


klasa LZMADecompressor:

    def __init__(self):
        self._decomp = Nic
        self._unconsumed = b''
        self.eof = Nieprawda

    def decompress(self, data):
        jeżeli self._decomp jest Nic:
            self._unconsumed += data
            jeżeli len(self._unconsumed) <= 4:
                zwróć b''
            psize, = struct.unpack('<H', self._unconsumed[2:4])
            jeżeli len(self._unconsumed) <= 4 + psize:
                zwróć b''

            self._decomp = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[
                lzma._decode_filter_properties(lzma.FILTER_LZMA1,
                                               self._unconsumed[4:4 + psize])
            ])
            data = self._unconsumed[4 + psize:]
            usuń self._unconsumed

        result = self._decomp.decompress(data)
        self.eof = self._decomp.eof
        zwróć result


compressor_names = {
    0: 'store',
    1: 'shrink',
    2: 'reduce',
    3: 'reduce',
    4: 'reduce',
    5: 'reduce',
    6: 'implode',
    7: 'tokenize',
    8: 'deflate',
    9: 'deflate64',
    10: 'implode',
    12: 'bzip2',
    14: 'lzma',
    18: 'terse',
    19: 'lz77',
    97: 'wavpack',
    98: 'ppmd',
}

def _check_compression(compression):
    jeżeli compression == ZIP_STORED:
        dalej
    albo_inaczej compression == ZIP_DEFLATED:
        jeżeli nie zlib:
            podnieś RuntimeError(
                "Compression requires the (missing) zlib module")
    albo_inaczej compression == ZIP_BZIP2:
        jeżeli nie bz2:
            podnieś RuntimeError(
                "Compression requires the (missing) bz2 module")
    albo_inaczej compression == ZIP_LZMA:
        jeżeli nie lzma:
            podnieś RuntimeError(
                "Compression requires the (missing) lzma module")
    inaczej:
        podnieś RuntimeError("That compression method jest nie supported")


def _get_compressor(compress_type):
    jeżeli compress_type == ZIP_DEFLATED:
        zwróć zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                zlib.DEFLATED, -15)
    albo_inaczej compress_type == ZIP_BZIP2:
        zwróć bz2.BZ2Compressor()
    albo_inaczej compress_type == ZIP_LZMA:
        zwróć LZMACompressor()
    inaczej:
        zwróć Nic


def _get_decompressor(compress_type):
    jeżeli compress_type == ZIP_STORED:
        zwróć Nic
    albo_inaczej compress_type == ZIP_DEFLATED:
        zwróć zlib.decompressobj(-15)
    albo_inaczej compress_type == ZIP_BZIP2:
        zwróć bz2.BZ2Decompressor()
    albo_inaczej compress_type == ZIP_LZMA:
        zwróć LZMADecompressor()
    inaczej:
        descr = compressor_names.get(compress_type)
        jeżeli descr:
            podnieś NotImplementedError("compression type %d (%s)" % (compress_type, descr))
        inaczej:
            podnieś NotImplementedError("compression type %d" % (compress_type,))


klasa _SharedFile:
    def __init__(self, file, pos, close, lock):
        self._file = file
        self._pos = pos
        self._close = close
        self._lock = lock

    def read(self, n=-1):
        przy self._lock:
            self._file.seek(self._pos)
            data = self._file.read(n)
            self._pos = self._file.tell()
            zwróć data

    def close(self):
        jeżeli self._file jest nie Nic:
            fileobj = self._file
            self._file = Nic
            self._close(fileobj)

# Provide the tell method dla unseekable stream
klasa _Tellable:
    def __init__(self, fp):
        self.fp = fp
        self.offset = 0

    def write(self, data):
        n = self.fp.write(data)
        self.offset += n
        zwróć n

    def tell(self):
        zwróć self.offset

    def flush(self):
        self.fp.flush()

    def close(self):
        self.fp.close()


klasa ZipExtFile(io.BufferedIOBase):
    """File-like object dla reading an archive member.
       Is returned by ZipFile.open().
    """

    # Max size supported by decompressor.
    MAX_N = 1 << 31 - 1

    # Read z compressed files w 4k blocks.
    MIN_READ_SIZE = 4096

    # Search dla universal newlines albo line chunks.
    PATTERN = re.compile(br'^(?P<chunk>[^\r\n]+)|(?P<newline>\n|\r\n?)')

    def __init__(self, fileobj, mode, zipinfo, decrypter=Nic,
                 close_fileobj=Nieprawda):
        self._fileobj = fileobj
        self._decrypter = decrypter
        self._close_fileobj = close_fileobj

        self._compress_type = zipinfo.compress_type
        self._compress_left = zipinfo.compress_size
        self._left = zipinfo.file_size

        self._decompressor = _get_decompressor(self._compress_type)

        self._eof = Nieprawda
        self._readbuffer = b''
        self._offset = 0

        self._universal = 'U' w mode
        self.newlines = Nic

        # Adjust read size dla encrypted files since the first 12 bytes
        # are dla the encryption/password information.
        jeżeli self._decrypter jest nie Nic:
            self._compress_left -= 12

        self.mode = mode
        self.name = zipinfo.filename

        jeżeli hasattr(zipinfo, 'CRC'):
            self._expected_crc = zipinfo.CRC
            self._running_crc = crc32(b'') & 0xffffffff
        inaczej:
            self._expected_crc = Nic

    def __repr__(self):
        result = ['<%s.%s' % (self.__class__.__module__,
                              self.__class__.__qualname__)]
        jeżeli nie self.closed:
            result.append(' name=%r mode=%r' % (self.name, self.mode))
            jeżeli self._compress_type != ZIP_STORED:
                result.append(' compress_type=%s' %
                              compressor_names.get(self._compress_type,
                                                   self._compress_type))
        inaczej:
            result.append(' [closed]')
        result.append('>')
        zwróć ''.join(result)

    def readline(self, limit=-1):
        """Read oraz zwróć a line z the stream.

        If limit jest specified, at most limit bytes will be read.
        """

        jeżeli nie self._universal oraz limit < 0:
            # Shortcut common case - newline found w buffer.
            i = self._readbuffer.find(b'\n', self._offset) + 1
            jeżeli i > 0:
                line = self._readbuffer[self._offset: i]
                self._offset = i
                zwróć line

        jeżeli nie self._universal:
            zwróć io.BufferedIOBase.readline(self, limit)

        line = b''
        dopóki limit < 0 albo len(line) < limit:
            readahead = self.peek(2)
            jeżeli readahead == b'':
                zwróć line

            #
            # Search dla universal newlines albo line chunks.
            #
            # The pattern returns either a line chunk albo a newline, but nie
            # both. Combined przy peek(2), we are assured that the sequence
            # '\r\n' jest always retrieved completely oraz never split into
            # separate newlines - '\r', '\n' due to coincidental readaheads.
            #
            match = self.PATTERN.search(readahead)
            newline = match.group('newline')
            jeżeli newline jest nie Nic:
                jeżeli self.newlines jest Nic:
                    self.newlines = []
                jeżeli newline nie w self.newlines:
                    self.newlines.append(newline)
                self._offset += len(newline)
                zwróć line + b'\n'

            chunk = match.group('chunk')
            jeżeli limit >= 0:
                chunk = chunk[: limit - len(line)]

            self._offset += len(chunk)
            line += chunk

        zwróć line

    def peek(self, n=1):
        """Returns buffered bytes without advancing the position."""
        jeżeli n > len(self._readbuffer) - self._offset:
            chunk = self.read(n)
            jeżeli len(chunk) > self._offset:
                self._readbuffer = chunk + self._readbuffer[self._offset:]
                self._offset = 0
            inaczej:
                self._offset -= len(chunk)

        # Return up to 512 bytes to reduce allocation overhead dla tight loops.
        zwróć self._readbuffer[self._offset: self._offset + 512]

    def readable(self):
        zwróć Prawda

    def read(self, n=-1):
        """Read oraz zwróć up to n bytes.
        If the argument jest omitted, Nic, albo negative, data jest read oraz returned until EOF jest reached..
        """
        jeżeli n jest Nic albo n < 0:
            buf = self._readbuffer[self._offset:]
            self._readbuffer = b''
            self._offset = 0
            dopóki nie self._eof:
                buf += self._read1(self.MAX_N)
            zwróć buf

        end = n + self._offset
        jeżeli end < len(self._readbuffer):
            buf = self._readbuffer[self._offset:end]
            self._offset = end
            zwróć buf

        n = end - len(self._readbuffer)
        buf = self._readbuffer[self._offset:]
        self._readbuffer = b''
        self._offset = 0
        dopóki n > 0 oraz nie self._eof:
            data = self._read1(n)
            jeżeli n < len(data):
                self._readbuffer = data
                self._offset = n
                buf += data[:n]
                przerwij
            buf += data
            n -= len(data)
        zwróć buf

    def _update_crc(self, newdata):
        # Update the CRC using the given data.
        jeżeli self._expected_crc jest Nic:
            # No need to compute the CRC jeżeli we don't have a reference value
            zwróć
        self._running_crc = crc32(newdata, self._running_crc) & 0xffffffff
        # Check the CRC jeżeli we're at the end of the file
        jeżeli self._eof oraz self._running_crc != self._expected_crc:
            podnieś BadZipFile("Bad CRC-32 dla file %r" % self.name)

    def read1(self, n):
        """Read up to n bytes przy at most one read() system call."""

        jeżeli n jest Nic albo n < 0:
            buf = self._readbuffer[self._offset:]
            self._readbuffer = b''
            self._offset = 0
            dopóki nie self._eof:
                data = self._read1(self.MAX_N)
                jeżeli data:
                    buf += data
                    przerwij
            zwróć buf

        end = n + self._offset
        jeżeli end < len(self._readbuffer):
            buf = self._readbuffer[self._offset:end]
            self._offset = end
            zwróć buf

        n = end - len(self._readbuffer)
        buf = self._readbuffer[self._offset:]
        self._readbuffer = b''
        self._offset = 0
        jeżeli n > 0:
            dopóki nie self._eof:
                data = self._read1(n)
                jeżeli n < len(data):
                    self._readbuffer = data
                    self._offset = n
                    buf += data[:n]
                    przerwij
                jeżeli data:
                    buf += data
                    przerwij
        zwróć buf

    def _read1(self, n):
        # Read up to n compressed bytes przy at most one read() system call,
        # decrypt oraz decompress them.
        jeżeli self._eof albo n <= 0:
            zwróć b''

        # Read z file.
        jeżeli self._compress_type == ZIP_DEFLATED:
            ## Handle unconsumed data.
            data = self._decompressor.unconsumed_tail
            jeżeli n > len(data):
                data += self._read2(n - len(data))
        inaczej:
            data = self._read2(n)

        jeżeli self._compress_type == ZIP_STORED:
            self._eof = self._compress_left <= 0
        albo_inaczej self._compress_type == ZIP_DEFLATED:
            n = max(n, self.MIN_READ_SIZE)
            data = self._decompressor.decompress(data, n)
            self._eof = (self._decompressor.eof albo
                         self._compress_left <= 0 oraz
                         nie self._decompressor.unconsumed_tail)
            jeżeli self._eof:
                data += self._decompressor.flush()
        inaczej:
            data = self._decompressor.decompress(data)
            self._eof = self._decompressor.eof albo self._compress_left <= 0

        data = data[:self._left]
        self._left -= len(data)
        jeżeli self._left <= 0:
            self._eof = Prawda
        self._update_crc(data)
        zwróć data

    def _read2(self, n):
        jeżeli self._compress_left <= 0:
            zwróć b''

        n = max(n, self.MIN_READ_SIZE)
        n = min(n, self._compress_left)

        data = self._fileobj.read(n)
        self._compress_left -= len(data)
        jeżeli nie data:
            podnieś EOFError

        jeżeli self._decrypter jest nie Nic:
            data = bytes(map(self._decrypter, data))
        zwróć data

    def close(self):
        spróbuj:
            jeżeli self._close_fileobj:
                self._fileobj.close()
        w_końcu:
            super().close()


klasa ZipFile:
    """ Class przy methods to open, read, write, close, list zip files.

    z = ZipFile(file, mode="r", compression=ZIP_STORED, allowZip64=Prawda)

    file: Either the path to the file, albo a file-like object.
          If it jest a path, the file will be opened oraz closed by ZipFile.
    mode: The mode can be either read 'r', write 'w', exclusive create 'x',
          albo append 'a'.
    compression: ZIP_STORED (no compression), ZIP_DEFLATED (requires zlib),
                 ZIP_BZIP2 (requires bz2) albo ZIP_LZMA (requires lzma).
    allowZip64: jeżeli Prawda ZipFile will create files przy ZIP64 extensions when
                needed, otherwise it will podnieś an exception when this would
                be necessary.

    """

    fp = Nic                   # Set here since __del__ checks it
    _windows_illegal_name_trans_table = Nic

    def __init__(self, file, mode="r", compression=ZIP_STORED, allowZip64=Prawda):
        """Open the ZIP file przy mode read 'r', write 'w', exclusive create 'x',
        albo append 'a'."""
        jeżeli mode nie w ('r', 'w', 'x', 'a'):
            podnieś RuntimeError("ZipFile requires mode 'r', 'w', 'x', albo 'a'")

        _check_compression(compression)

        self._allowZip64 = allowZip64
        self._didModify = Nieprawda
        self.debug = 0  # Level of printing: 0 through 3
        self.NameToInfo = {}    # Find file info given name
        self.filelist = []      # List of ZipInfo instances dla archive
        self.compression = compression  # Method of compression
        self.mode = mode
        self.pwd = Nic
        self._comment = b''

        # Check jeżeli we were dalejed a file-like object
        jeżeli isinstance(file, str):
            # No, it's a filename
            self._filePassed = 0
            self.filename = file
            modeDict = {'r' : 'rb', 'w': 'w+b', 'x': 'x+b', 'a' : 'r+b',
                        'r+b': 'w+b', 'w+b': 'wb', 'x+b': 'xb'}
            filemode = modeDict[mode]
            dopóki Prawda:
                spróbuj:
                    self.fp = io.open(file, filemode)
                wyjąwszy OSError:
                    jeżeli filemode w modeDict:
                        filemode = modeDict[filemode]
                        kontynuuj
                    podnieś
                przerwij
        inaczej:
            self._filePassed = 1
            self.fp = file
            self.filename = getattr(file, 'name', Nic)
        self._fileRefCnt = 1
        self._lock = threading.RLock()
        self._seekable = Prawda

        spróbuj:
            jeżeli mode == 'r':
                self._RealGetContents()
            albo_inaczej mode w ('w', 'x'):
                # set the modified flag so central directory gets written
                # even jeżeli no files are added to the archive
                self._didModify = Prawda
                spróbuj:
                    self.start_dir = self.fp.tell()
                wyjąwszy (AttributeError, OSError):
                    self.fp = _Tellable(self.fp)
                    self.start_dir = 0
                    self._seekable = Nieprawda
                inaczej:
                    # Some file-like objects can provide tell() but nie seek()
                    spróbuj:
                        self.fp.seek(self.start_dir)
                    wyjąwszy (AttributeError, OSError):
                        self._seekable = Nieprawda
            albo_inaczej mode == 'a':
                spróbuj:
                    # See jeżeli file jest a zip file
                    self._RealGetContents()
                    # seek to start of directory oraz overwrite
                    self.fp.seek(self.start_dir)
                wyjąwszy BadZipFile:
                    # file jest nie a zip file, just append
                    self.fp.seek(0, 2)

                    # set the modified flag so central directory gets written
                    # even jeżeli no files are added to the archive
                    self._didModify = Prawda
                    self.start_dir = self.fp.tell()
            inaczej:
                podnieś RuntimeError("Mode must be 'r', 'w', 'x', albo 'a'")
        wyjąwszy:
            fp = self.fp
            self.fp = Nic
            self._fpclose(fp)
            podnieś

    def __enter__(self):
        zwróć self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        result = ['<%s.%s' % (self.__class__.__module__,
                              self.__class__.__qualname__)]
        jeżeli self.fp jest nie Nic:
            jeżeli self._filePassed:
                result.append(' file=%r' % self.fp)
            albo_inaczej self.filename jest nie Nic:
                result.append(' filename=%r' % self.filename)
            result.append(' mode=%r' % self.mode)
        inaczej:
            result.append(' [closed]')
        result.append('>')
        zwróć ''.join(result)

    def _RealGetContents(self):
        """Read w the table of contents dla the ZIP file."""
        fp = self.fp
        spróbuj:
            endrec = _EndRecData(fp)
        wyjąwszy OSError:
            podnieś BadZipFile("File jest nie a zip file")
        jeżeli nie endrec:
            podnieś BadZipFile("File jest nie a zip file")
        jeżeli self.debug > 1:
            print(endrec)
        size_cd = endrec[_ECD_SIZE]             # bytes w central directory
        offset_cd = endrec[_ECD_OFFSET]         # offset of central directory
        self._comment = endrec[_ECD_COMMENT]    # archive comment

        # "concat" jest zero, unless zip was concatenated to another file
        concat = endrec[_ECD_LOCATION] - size_cd - offset_cd
        jeżeli endrec[_ECD_SIGNATURE] == stringEndArchive64:
            # If Zip64 extension structures are present, account dla them
            concat -= (sizeEndCentDir64 + sizeEndCentDir64Locator)

        jeżeli self.debug > 2:
            inferred = concat + offset_cd
            print("given, inferred, offset", offset_cd, inferred, concat)
        # self.start_dir:  Position of start of central directory
        self.start_dir = offset_cd + concat
        fp.seek(self.start_dir, 0)
        data = fp.read(size_cd)
        fp = io.BytesIO(data)
        total = 0
        dopóki total < size_cd:
            centdir = fp.read(sizeCentralDir)
            jeżeli len(centdir) != sizeCentralDir:
                podnieś BadZipFile("Truncated central directory")
            centdir = struct.unpack(structCentralDir, centdir)
            jeżeli centdir[_CD_SIGNATURE] != stringCentralDir:
                podnieś BadZipFile("Bad magic number dla central directory")
            jeżeli self.debug > 2:
                print(centdir)
            filename = fp.read(centdir[_CD_FILENAME_LENGTH])
            flags = centdir[5]
            jeżeli flags & 0x800:
                # UTF-8 file names extension
                filename = filename.decode('utf-8')
            inaczej:
                # Historical ZIP filename encoding
                filename = filename.decode('cp437')
            # Create ZipInfo instance to store file information
            x = ZipInfo(filename)
            x.extra = fp.read(centdir[_CD_EXTRA_FIELD_LENGTH])
            x.comment = fp.read(centdir[_CD_COMMENT_LENGTH])
            x.header_offset = centdir[_CD_LOCAL_HEADER_OFFSET]
            (x.create_version, x.create_system, x.extract_version, x.reserved,
             x.flag_bits, x.compress_type, t, d,
             x.CRC, x.compress_size, x.file_size) = centdir[1:12]
            jeżeli x.extract_version > MAX_EXTRACT_VERSION:
                podnieś NotImplementedError("zip file version %.1f" %
                                          (x.extract_version / 10))
            x.volume, x.internal_attr, x.external_attr = centdir[15:18]
            # Convert date/time code to (year, month, day, hour, min, sec)
            x._raw_time = t
            x.date_time = ( (d>>9)+1980, (d>>5)&0xF, d&0x1F,
                            t>>11, (t>>5)&0x3F, (t&0x1F) * 2 )

            x._decodeExtra()
            x.header_offset = x.header_offset + concat
            self.filelist.append(x)
            self.NameToInfo[x.filename] = x

            # update total bytes read z central directory
            total = (total + sizeCentralDir + centdir[_CD_FILENAME_LENGTH]
                     + centdir[_CD_EXTRA_FIELD_LENGTH]
                     + centdir[_CD_COMMENT_LENGTH])

            jeżeli self.debug > 2:
                print("total", total)


    def namelist(self):
        """Return a list of file names w the archive."""
        zwróć [data.filename dla data w self.filelist]

    def infolist(self):
        """Return a list of klasa ZipInfo instances dla files w the
        archive."""
        zwróć self.filelist

    def printdir(self, file=Nic):
        """Print a table of contents dla the zip file."""
        print("%-46s %19s %12s" % ("File Name", "Modified    ", "Size"),
              file=file)
        dla zinfo w self.filelist:
            date = "%d-%02d-%02d %02d:%02d:%02d" % zinfo.date_time[:6]
            print("%-46s %s %12d" % (zinfo.filename, date, zinfo.file_size),
                  file=file)

    def testzip(self):
        """Read all the files oraz check the CRC."""
        chunk_size = 2 ** 20
        dla zinfo w self.filelist:
            spróbuj:
                # Read by chunks, to avoid an OverflowError albo a
                # MemoryError przy very large embedded files.
                przy self.open(zinfo.filename, "r") jako f:
                    dopóki f.read(chunk_size):     # Check CRC-32
                        dalej
            wyjąwszy BadZipFile:
                zwróć zinfo.filename

    def getinfo(self, name):
        """Return the instance of ZipInfo given 'name'."""
        info = self.NameToInfo.get(name)
        jeżeli info jest Nic:
            podnieś KeyError(
                'There jest no item named %r w the archive' % name)

        zwróć info

    def setpassword(self, pwd):
        """Set default dalejword dla encrypted files."""
        jeżeli pwd oraz nie isinstance(pwd, bytes):
            podnieś TypeError("pwd: expected bytes, got %s" % type(pwd))
        jeżeli pwd:
            self.pwd = pwd
        inaczej:
            self.pwd = Nic

    @property
    def comment(self):
        """The comment text associated przy the ZIP file."""
        zwróć self._comment

    @comment.setter
    def comment(self, comment):
        jeżeli nie isinstance(comment, bytes):
            podnieś TypeError("comment: expected bytes, got %s" % type(comment))
        # check dla valid comment length
        jeżeli len(comment) > ZIP_MAX_COMMENT:
            zaimportuj warnings
            warnings.warn('Archive comment jest too long; truncating to %d bytes'
                          % ZIP_MAX_COMMENT, stacklevel=2)
            comment = comment[:ZIP_MAX_COMMENT]
        self._comment = comment
        self._didModify = Prawda

    def read(self, name, pwd=Nic):
        """Return file bytes (as a string) dla name."""
        przy self.open(name, "r", pwd) jako fp:
            zwróć fp.read()

    def open(self, name, mode="r", pwd=Nic):
        """Return file-like object dla 'name'."""
        jeżeli mode nie w ("r", "U", "rU"):
            podnieś RuntimeError('open() requires mode "r", "U", albo "rU"')
        jeżeli 'U' w mode:
            zaimportuj warnings
            warnings.warn("'U' mode jest deprecated",
                          DeprecationWarning, 2)
        jeżeli pwd oraz nie isinstance(pwd, bytes):
            podnieś TypeError("pwd: expected bytes, got %s" % type(pwd))
        jeżeli nie self.fp:
            podnieś RuntimeError(
                "Attempt to read ZIP archive that was already closed")

        # Make sure we have an info object
        jeżeli isinstance(name, ZipInfo):
            # 'name' jest already an info object
            zinfo = name
        inaczej:
            # Get info object dla name
            zinfo = self.getinfo(name)

        self._fileRefCnt += 1
        zef_file = _SharedFile(self.fp, zinfo.header_offset, self._fpclose, self._lock)
        spróbuj:
            # Skip the file header:
            fheader = zef_file.read(sizeFileHeader)
            jeżeli len(fheader) != sizeFileHeader:
                podnieś BadZipFile("Truncated file header")
            fheader = struct.unpack(structFileHeader, fheader)
            jeżeli fheader[_FH_SIGNATURE] != stringFileHeader:
                podnieś BadZipFile("Bad magic number dla file header")

            fname = zef_file.read(fheader[_FH_FILENAME_LENGTH])
            jeżeli fheader[_FH_EXTRA_FIELD_LENGTH]:
                zef_file.read(fheader[_FH_EXTRA_FIELD_LENGTH])

            jeżeli zinfo.flag_bits & 0x20:
                # Zip 2.7: compressed patched data
                podnieś NotImplementedError("compressed patched data (flag bit 5)")

            jeżeli zinfo.flag_bits & 0x40:
                # strong encryption
                podnieś NotImplementedError("strong encryption (flag bit 6)")

            jeżeli zinfo.flag_bits & 0x800:
                # UTF-8 filename
                fname_str = fname.decode("utf-8")
            inaczej:
                fname_str = fname.decode("cp437")

            jeżeli fname_str != zinfo.orig_filename:
                podnieś BadZipFile(
                    'File name w directory %r oraz header %r differ.'
                    % (zinfo.orig_filename, fname))

            # check dla encrypted flag & handle dalejword
            is_encrypted = zinfo.flag_bits & 0x1
            zd = Nic
            jeżeli is_encrypted:
                jeżeli nie pwd:
                    pwd = self.pwd
                jeżeli nie pwd:
                    podnieś RuntimeError("File %s jest encrypted, dalejword "
                                       "required dla extraction" % name)

                zd = _ZipDecrypter(pwd)
                # The first 12 bytes w the cypher stream jest an encryption header
                #  used to strengthen the algorithm. The first 11 bytes are
                #  completely random, dopóki the 12th contains the MSB of the CRC,
                #  albo the MSB of the file time depending on the header type
                #  oraz jest used to check the correctness of the dalejword.
                header = zef_file.read(12)
                h = list(map(zd, header[0:12]))
                jeżeli zinfo.flag_bits & 0x8:
                    # compare against the file type z extended local headers
                    check_byte = (zinfo._raw_time >> 8) & 0xff
                inaczej:
                    # compare against the CRC otherwise
                    check_byte = (zinfo.CRC >> 24) & 0xff
                jeżeli h[11] != check_byte:
                    podnieś RuntimeError("Bad dalejword dla file", name)

            zwróć ZipExtFile(zef_file, mode, zinfo, zd, Prawda)
        wyjąwszy:
            zef_file.close()
            podnieś

    def extract(self, member, path=Nic, pwd=Nic):
        """Extract a member z the archive to the current working directory,
           using its full name. Its file information jest extracted jako accurately
           jako possible. `member' may be a filename albo a ZipInfo object. You can
           specify a different directory using `path'.
        """
        jeżeli nie isinstance(member, ZipInfo):
            member = self.getinfo(member)

        jeżeli path jest Nic:
            path = os.getcwd()

        zwróć self._extract_member(member, path, pwd)

    def extractall(self, path=Nic, members=Nic, pwd=Nic):
        """Extract all members z the archive to the current working
           directory. `path' specifies a different directory to extract to.
           `members' jest optional oraz must be a subset of the list returned
           by namelist().
        """
        jeżeli members jest Nic:
            members = self.namelist()

        dla zipinfo w members:
            self.extract(zipinfo, path, pwd)

    @classmethod
    def _sanitize_windows_name(cls, arcname, pathsep):
        """Replace bad characters oraz remove trailing dots z parts."""
        table = cls._windows_illegal_name_trans_table
        jeżeli nie table:
            illegal = ':<>|"?*'
            table = str.maketrans(illegal, '_' * len(illegal))
            cls._windows_illegal_name_trans_table = table
        arcname = arcname.translate(table)
        # remove trailing dots
        arcname = (x.rstrip('.') dla x w arcname.split(pathsep))
        # rejoin, removing empty parts.
        arcname = pathsep.join(x dla x w arcname jeżeli x)
        zwróć arcname

    def _extract_member(self, member, targetpath, pwd):
        """Extract the ZipInfo object 'member' to a physical
           file on the path targetpath.
        """
        # build the destination pathname, replacing
        # forward slashes to platform specific separators.
        arcname = member.filename.replace('/', os.path.sep)

        jeżeli os.path.altsep:
            arcname = arcname.replace(os.path.altsep, os.path.sep)
        # interpret absolute pathname jako relative, remove drive letter albo
        # UNC path, redundant separators, "." oraz ".." components.
        arcname = os.path.splitdrive(arcname)[1]
        invalid_path_parts = ('', os.path.curdir, os.path.pardir)
        arcname = os.path.sep.join(x dla x w arcname.split(os.path.sep)
                                   jeżeli x nie w invalid_path_parts)
        jeżeli os.path.sep == '\\':
            # filter illegal characters on Windows
            arcname = self._sanitize_windows_name(arcname, os.path.sep)

        targetpath = os.path.join(targetpath, arcname)
        targetpath = os.path.normpath(targetpath)

        # Create all upper directories jeżeli necessary.
        upperdirs = os.path.dirname(targetpath)
        jeżeli upperdirs oraz nie os.path.exists(upperdirs):
            os.makedirs(upperdirs)

        jeżeli member.filename[-1] == '/':
            jeżeli nie os.path.isdir(targetpath):
                os.mkdir(targetpath)
            zwróć targetpath

        przy self.open(member, pwd=pwd) jako source, \
             open(targetpath, "wb") jako target:
            shutil.copyfileobj(source, target)

        zwróć targetpath

    def _writecheck(self, zinfo):
        """Check dla errors before writing a file to the archive."""
        jeżeli zinfo.filename w self.NameToInfo:
            zaimportuj warnings
            warnings.warn('Duplicate name: %r' % zinfo.filename, stacklevel=3)
        jeżeli self.mode nie w ('w', 'x', 'a'):
            podnieś RuntimeError("write() requires mode 'w', 'x', albo 'a'")
        jeżeli nie self.fp:
            podnieś RuntimeError(
                "Attempt to write ZIP archive that was already closed")
        _check_compression(zinfo.compress_type)
        jeżeli nie self._allowZip64:
            requires_zip64 = Nic
            jeżeli len(self.filelist) >= ZIP_FILECOUNT_LIMIT:
                requires_zip64 = "Files count"
            albo_inaczej zinfo.file_size > ZIP64_LIMIT:
                requires_zip64 = "Filesize"
            albo_inaczej zinfo.header_offset > ZIP64_LIMIT:
                requires_zip64 = "Zipfile size"
            jeżeli requires_zip64:
                podnieś LargeZipFile(requires_zip64 +
                                   " would require ZIP64 extensions")

    def write(self, filename, arcname=Nic, compress_type=Nic):
        """Put the bytes z filename into the archive under the name
        arcname."""
        jeżeli nie self.fp:
            podnieś RuntimeError(
                "Attempt to write to ZIP archive that was already closed")

        st = os.stat(filename)
        isdir = stat.S_ISDIR(st.st_mode)
        mtime = time.localtime(st.st_mtime)
        date_time = mtime[0:6]
        # Create ZipInfo instance to store file information
        jeżeli arcname jest Nic:
            arcname = filename
        arcname = os.path.normpath(os.path.splitdrive(arcname)[1])
        dopóki arcname[0] w (os.sep, os.altsep):
            arcname = arcname[1:]
        jeżeli isdir:
            arcname += '/'
        zinfo = ZipInfo(arcname, date_time)
        zinfo.external_attr = (st[0] & 0xFFFF) << 16      # Unix attributes
        jeżeli compress_type jest Nic:
            zinfo.compress_type = self.compression
        inaczej:
            zinfo.compress_type = compress_type

        zinfo.file_size = st.st_size
        zinfo.flag_bits = 0x00
        przy self._lock:
            jeżeli self._seekable:
                self.fp.seek(self.start_dir)
            zinfo.header_offset = self.fp.tell()    # Start of header bytes
            jeżeli zinfo.compress_type == ZIP_LZMA:
                # Compressed data includes an end-of-stream (EOS) marker
                zinfo.flag_bits |= 0x02

            self._writecheck(zinfo)
            self._didModify = Prawda

            jeżeli isdir:
                zinfo.file_size = 0
                zinfo.compress_size = 0
                zinfo.CRC = 0
                zinfo.external_attr |= 0x10  # MS-DOS directory flag
                self.filelist.append(zinfo)
                self.NameToInfo[zinfo.filename] = zinfo
                self.fp.write(zinfo.FileHeader(Nieprawda))
                self.start_dir = self.fp.tell()
                zwróć

            cmpr = _get_compressor(zinfo.compress_type)
            jeżeli nie self._seekable:
                zinfo.flag_bits |= 0x08
            przy open(filename, "rb") jako fp:
                # Must overwrite CRC oraz sizes przy correct data later
                zinfo.CRC = CRC = 0
                zinfo.compress_size = compress_size = 0
                # Compressed size can be larger than uncompressed size
                zip64 = self._allowZip64 oraz \
                    zinfo.file_size * 1.05 > ZIP64_LIMIT
                self.fp.write(zinfo.FileHeader(zip64))
                file_size = 0
                dopóki 1:
                    buf = fp.read(1024 * 8)
                    jeżeli nie buf:
                        przerwij
                    file_size = file_size + len(buf)
                    CRC = crc32(buf, CRC) & 0xffffffff
                    jeżeli cmpr:
                        buf = cmpr.compress(buf)
                        compress_size = compress_size + len(buf)
                    self.fp.write(buf)
            jeżeli cmpr:
                buf = cmpr.flush()
                compress_size = compress_size + len(buf)
                self.fp.write(buf)
                zinfo.compress_size = compress_size
            inaczej:
                zinfo.compress_size = file_size
            zinfo.CRC = CRC
            zinfo.file_size = file_size
            jeżeli zinfo.flag_bits & 0x08:
                # Write CRC oraz file sizes after the file data
                fmt = '<LQQ' jeżeli zip64 inaczej '<LLL'
                self.fp.write(struct.pack(fmt, zinfo.CRC, zinfo.compress_size,
                                          zinfo.file_size))
                self.start_dir = self.fp.tell()
            inaczej:
                jeżeli nie zip64 oraz self._allowZip64:
                    jeżeli file_size > ZIP64_LIMIT:
                        podnieś RuntimeError('File size has increased during compressing')
                    jeżeli compress_size > ZIP64_LIMIT:
                        podnieś RuntimeError('Compressed size larger than uncompressed size')
                # Seek backwards oraz write file header (which will now include
                # correct CRC oraz file sizes)
                self.start_dir = self.fp.tell() # Preserve current position w file
                self.fp.seek(zinfo.header_offset)
                self.fp.write(zinfo.FileHeader(zip64))
                self.fp.seek(self.start_dir)
            self.filelist.append(zinfo)
            self.NameToInfo[zinfo.filename] = zinfo

    def writestr(self, zinfo_or_arcname, data, compress_type=Nic):
        """Write a file into the archive.  The contents jest 'data', which
        may be either a 'str' albo a 'bytes' instance; jeżeli it jest a 'str',
        it jest encoded jako UTF-8 first.
        'zinfo_or_arcname' jest either a ZipInfo instance albo
        the name of the file w the archive."""
        jeżeli isinstance(data, str):
            data = data.encode("utf-8")
        jeżeli nie isinstance(zinfo_or_arcname, ZipInfo):
            zinfo = ZipInfo(filename=zinfo_or_arcname,
                            date_time=time.localtime(time.time())[:6])
            zinfo.compress_type = self.compression
            jeżeli zinfo.filename[-1] == '/':
                zinfo.external_attr = 0o40775 << 16   # drwxrwxr-x
                zinfo.external_attr |= 0x10           # MS-DOS directory flag
            inaczej:
                zinfo.external_attr = 0o600 << 16     # ?rw-------
        inaczej:
            zinfo = zinfo_or_arcname

        jeżeli nie self.fp:
            podnieś RuntimeError(
                "Attempt to write to ZIP archive that was already closed")

        zinfo.file_size = len(data)            # Uncompressed size
        przy self._lock:
            jeżeli self._seekable:
                self.fp.seek(self.start_dir)
            zinfo.header_offset = self.fp.tell()    # Start of header data
            jeżeli compress_type jest nie Nic:
                zinfo.compress_type = compress_type
            zinfo.header_offset = self.fp.tell()    # Start of header data
            jeżeli compress_type jest nie Nic:
                zinfo.compress_type = compress_type
            jeżeli zinfo.compress_type == ZIP_LZMA:
                # Compressed data includes an end-of-stream (EOS) marker
                zinfo.flag_bits |= 0x02

            self._writecheck(zinfo)
            self._didModify = Prawda
            zinfo.CRC = crc32(data) & 0xffffffff       # CRC-32 checksum
            co = _get_compressor(zinfo.compress_type)
            jeżeli co:
                data = co.compress(data) + co.flush()
                zinfo.compress_size = len(data)    # Compressed size
            inaczej:
                zinfo.compress_size = zinfo.file_size
            zip64 = zinfo.file_size > ZIP64_LIMIT albo \
                zinfo.compress_size > ZIP64_LIMIT
            jeżeli zip64 oraz nie self._allowZip64:
                podnieś LargeZipFile("Filesize would require ZIP64 extensions")
            self.fp.write(zinfo.FileHeader(zip64))
            self.fp.write(data)
            jeżeli zinfo.flag_bits & 0x08:
                # Write CRC oraz file sizes after the file data
                fmt = '<LQQ' jeżeli zip64 inaczej '<LLL'
                self.fp.write(struct.pack(fmt, zinfo.CRC, zinfo.compress_size,
                                          zinfo.file_size))
            self.fp.flush()
            self.start_dir = self.fp.tell()
            self.filelist.append(zinfo)
            self.NameToInfo[zinfo.filename] = zinfo

    def __del__(self):
        """Call the "close()" method w case the user forgot."""
        self.close()

    def close(self):
        """Close the file, oraz dla mode 'w', 'x' oraz 'a' write the ending
        records."""
        jeżeli self.fp jest Nic:
            zwróć

        spróbuj:
            jeżeli self.mode w ('w', 'x', 'a') oraz self._didModify: # write ending records
                przy self._lock:
                    jeżeli self._seekable:
                        self.fp.seek(self.start_dir)
                    self._write_end_record()
        w_końcu:
            fp = self.fp
            self.fp = Nic
            self._fpclose(fp)

    def _write_end_record(self):
        dla zinfo w self.filelist:         # write central directory
            dt = zinfo.date_time
            dosdate = (dt[0] - 1980) << 9 | dt[1] << 5 | dt[2]
            dostime = dt[3] << 11 | dt[4] << 5 | (dt[5] // 2)
            extra = []
            jeżeli zinfo.file_size > ZIP64_LIMIT \
               albo zinfo.compress_size > ZIP64_LIMIT:
                extra.append(zinfo.file_size)
                extra.append(zinfo.compress_size)
                file_size = 0xffffffff
                compress_size = 0xffffffff
            inaczej:
                file_size = zinfo.file_size
                compress_size = zinfo.compress_size

            jeżeli zinfo.header_offset > ZIP64_LIMIT:
                extra.append(zinfo.header_offset)
                header_offset = 0xffffffff
            inaczej:
                header_offset = zinfo.header_offset

            extra_data = zinfo.extra
            min_version = 0
            jeżeli extra:
                # Append a ZIP64 field to the extra's
                extra_data = struct.pack(
                    '<HH' + 'Q'*len(extra),
                    1, 8*len(extra), *extra) + extra_data

                min_version = ZIP64_VERSION

            jeżeli zinfo.compress_type == ZIP_BZIP2:
                min_version = max(BZIP2_VERSION, min_version)
            albo_inaczej zinfo.compress_type == ZIP_LZMA:
                min_version = max(LZMA_VERSION, min_version)

            extract_version = max(min_version, zinfo.extract_version)
            create_version = max(min_version, zinfo.create_version)
            spróbuj:
                filename, flag_bits = zinfo._encodeFilenameFlags()
                centdir = struct.pack(structCentralDir,
                                      stringCentralDir, create_version,
                                      zinfo.create_system, extract_version, zinfo.reserved,
                                      flag_bits, zinfo.compress_type, dostime, dosdate,
                                      zinfo.CRC, compress_size, file_size,
                                      len(filename), len(extra_data), len(zinfo.comment),
                                      0, zinfo.internal_attr, zinfo.external_attr,
                                      header_offset)
            wyjąwszy DeprecationWarning:
                print((structCentralDir, stringCentralDir, create_version,
                       zinfo.create_system, extract_version, zinfo.reserved,
                       zinfo.flag_bits, zinfo.compress_type, dostime, dosdate,
                       zinfo.CRC, compress_size, file_size,
                       len(zinfo.filename), len(extra_data), len(zinfo.comment),
                       0, zinfo.internal_attr, zinfo.external_attr,
                       header_offset), file=sys.stderr)
                podnieś
            self.fp.write(centdir)
            self.fp.write(filename)
            self.fp.write(extra_data)
            self.fp.write(zinfo.comment)

        pos2 = self.fp.tell()
        # Write end-of-zip-archive record
        centDirCount = len(self.filelist)
        centDirSize = pos2 - self.start_dir
        centDirOffset = self.start_dir
        requires_zip64 = Nic
        jeżeli centDirCount > ZIP_FILECOUNT_LIMIT:
            requires_zip64 = "Files count"
        albo_inaczej centDirOffset > ZIP64_LIMIT:
            requires_zip64 = "Central directory offset"
        albo_inaczej centDirSize > ZIP64_LIMIT:
            requires_zip64 = "Central directory size"
        jeżeli requires_zip64:
            # Need to write the ZIP64 end-of-archive records
            jeżeli nie self._allowZip64:
                podnieś LargeZipFile(requires_zip64 +
                                   " would require ZIP64 extensions")
            zip64endrec = struct.pack(
                structEndArchive64, stringEndArchive64,
                44, 45, 45, 0, 0, centDirCount, centDirCount,
                centDirSize, centDirOffset)
            self.fp.write(zip64endrec)

            zip64locrec = struct.pack(
                structEndArchive64Locator,
                stringEndArchive64Locator, 0, pos2, 1)
            self.fp.write(zip64locrec)
            centDirCount = min(centDirCount, 0xFFFF)
            centDirSize = min(centDirSize, 0xFFFFFFFF)
            centDirOffset = min(centDirOffset, 0xFFFFFFFF)

        endrec = struct.pack(structEndArchive, stringEndArchive,
                             0, 0, centDirCount, centDirCount,
                             centDirSize, centDirOffset, len(self._comment))
        self.fp.write(endrec)
        self.fp.write(self._comment)
        self.fp.flush()

    def _fpclose(self, fp):
        assert self._fileRefCnt > 0
        self._fileRefCnt -= 1
        jeżeli nie self._fileRefCnt oraz nie self._filePassed:
            fp.close()


klasa PyZipFile(ZipFile):
    """Class to create ZIP archives przy Python library files oraz packages."""

    def __init__(self, file, mode="r", compression=ZIP_STORED,
                 allowZip64=Prawda, optimize=-1):
        ZipFile.__init__(self, file, mode=mode, compression=compression,
                         allowZip64=allowZip64)
        self._optimize = optimize

    def writepy(self, pathname, basename="", filterfunc=Nic):
        """Add all files z "pathname" to the ZIP archive.

        If pathname jest a package directory, search the directory oraz
        all package subdirectories recursively dla all *.py oraz enter
        the modules into the archive.  If pathname jest a plain
        directory, listdir *.py oraz enter all modules.  Else, pathname
        must be a Python *.py file oraz the module will be put into the
        archive.  Added modules are always module.pyc.
        This method will compile the module.py into module.pyc if
        necessary.
        If filterfunc(pathname) jest given, it jest called przy every argument.
        When it jest Nieprawda, the file albo directory jest skipped.
        """
        jeżeli filterfunc oraz nie filterfunc(pathname):
            jeżeli self.debug:
                label = 'path' jeżeli os.path.isdir(pathname) inaczej 'file'
                print('%s "%s" skipped by filterfunc' % (label, pathname))
            zwróć
        dir, name = os.path.split(pathname)
        jeżeli os.path.isdir(pathname):
            initname = os.path.join(pathname, "__init__.py")
            jeżeli os.path.isfile(initname):
                # This jest a package directory, add it
                jeżeli basename:
                    basename = "%s/%s" % (basename, name)
                inaczej:
                    basename = name
                jeżeli self.debug:
                    print("Adding package in", pathname, "as", basename)
                fname, arcname = self._get_codename(initname[0:-3], basename)
                jeżeli self.debug:
                    print("Adding", arcname)
                self.write(fname, arcname)
                dirlist = os.listdir(pathname)
                dirlist.remove("__init__.py")
                # Add all *.py files oraz package subdirectories
                dla filename w dirlist:
                    path = os.path.join(pathname, filename)
                    root, ext = os.path.splitext(filename)
                    jeżeli os.path.isdir(path):
                        jeżeli os.path.isfile(os.path.join(path, "__init__.py")):
                            # This jest a package directory, add it
                            self.writepy(path, basename,
                                         filterfunc=filterfunc)  # Recursive call
                    albo_inaczej ext == ".py":
                        jeżeli filterfunc oraz nie filterfunc(path):
                            jeżeli self.debug:
                                print('file "%s" skipped by filterfunc' % path)
                            kontynuuj
                        fname, arcname = self._get_codename(path[0:-3],
                                                            basename)
                        jeżeli self.debug:
                            print("Adding", arcname)
                        self.write(fname, arcname)
            inaczej:
                # This jest NOT a package directory, add its files at top level
                jeżeli self.debug:
                    print("Adding files z directory", pathname)
                dla filename w os.listdir(pathname):
                    path = os.path.join(pathname, filename)
                    root, ext = os.path.splitext(filename)
                    jeżeli ext == ".py":
                        jeżeli filterfunc oraz nie filterfunc(path):
                            jeżeli self.debug:
                                print('file "%s" skipped by filterfunc' % path)
                            kontynuuj
                        fname, arcname = self._get_codename(path[0:-3],
                                                            basename)
                        jeżeli self.debug:
                            print("Adding", arcname)
                        self.write(fname, arcname)
        inaczej:
            jeżeli pathname[-3:] != ".py":
                podnieś RuntimeError(
                    'Files added przy writepy() must end przy ".py"')
            fname, arcname = self._get_codename(pathname[0:-3], basename)
            jeżeli self.debug:
                print("Adding file", arcname)
            self.write(fname, arcname)

    def _get_codename(self, pathname, basename):
        """Return (filename, archivename) dla the path.

        Given a module name path, zwróć the correct file path oraz
        archive name, compiling jeżeli necessary.  For example, given
        /python/lib/string, zwróć (/python/lib/string.pyc, string).
        """
        def _compile(file, optimize=-1):
            zaimportuj py_compile
            jeżeli self.debug:
                print("Compiling", file)
            spróbuj:
                py_compile.compile(file, doraise=Prawda, optimize=optimize)
            wyjąwszy py_compile.PyCompileError jako err:
                print(err.msg)
                zwróć Nieprawda
            zwróć Prawda

        file_py  = pathname + ".py"
        file_pyc = pathname + ".pyc"
        pycache_opt0 = importlib.util.cache_from_source(file_py, optimization='')
        pycache_opt1 = importlib.util.cache_from_source(file_py, optimization=1)
        pycache_opt2 = importlib.util.cache_from_source(file_py, optimization=2)
        jeżeli self._optimize == -1:
            # legacy mode: use whatever file jest present
            jeżeli (os.path.isfile(file_pyc) oraz
                  os.stat(file_pyc).st_mtime >= os.stat(file_py).st_mtime):
                # Use .pyc file.
                arcname = fname = file_pyc
            albo_inaczej (os.path.isfile(pycache_opt0) oraz
                  os.stat(pycache_opt0).st_mtime >= os.stat(file_py).st_mtime):
                # Use the __pycache__/*.pyc file, but write it to the legacy pyc
                # file name w the archive.
                fname = pycache_opt0
                arcname = file_pyc
            albo_inaczej (os.path.isfile(pycache_opt1) oraz
                  os.stat(pycache_opt1).st_mtime >= os.stat(file_py).st_mtime):
                # Use the __pycache__/*.pyc file, but write it to the legacy pyc
                # file name w the archive.
                fname = pycache_opt1
                arcname = file_pyc
            albo_inaczej (os.path.isfile(pycache_opt2) oraz
                  os.stat(pycache_opt2).st_mtime >= os.stat(file_py).st_mtime):
                # Use the __pycache__/*.pyc file, but write it to the legacy pyc
                # file name w the archive.
                fname = pycache_opt2
                arcname = file_pyc
            inaczej:
                # Compile py into PEP 3147 pyc file.
                jeżeli _compile(file_py):
                    jeżeli sys.flags.optimize == 0:
                        fname = pycache_opt0
                    albo_inaczej sys.flags.optimize == 1:
                        fname = pycache_opt1
                    inaczej:
                        fname = pycache_opt2
                    arcname = file_pyc
                inaczej:
                    fname = arcname = file_py
        inaczej:
            # new mode: use given optimization level
            jeżeli self._optimize == 0:
                fname = pycache_opt0
                arcname = file_pyc
            inaczej:
                arcname = file_pyc
                jeżeli self._optimize == 1:
                    fname = pycache_opt1
                albo_inaczej self._optimize == 2:
                    fname = pycache_opt2
                inaczej:
                    msg = "invalid value dla 'optimize': {!r}".format(self._optimize)
                    podnieś ValueError(msg)
            jeżeli nie (os.path.isfile(fname) oraz
                    os.stat(fname).st_mtime >= os.stat(file_py).st_mtime):
                jeżeli nie _compile(file_py, optimize=self._optimize):
                    fname = arcname = file_py
        archivename = os.path.split(arcname)[1]
        jeżeli basename:
            archivename = "%s/%s" % (basename, archivename)
        zwróć (fname, archivename)


def main(args = Nic):
    zaimportuj textwrap
    USAGE=textwrap.dedent("""\
        Usage:
            zipfile.py -l zipfile.zip        # Show listing of a zipfile
            zipfile.py -t zipfile.zip        # Test jeżeli a zipfile jest valid
            zipfile.py -e zipfile.zip target # Extract zipfile into target dir
            zipfile.py -c zipfile.zip src ... # Create zipfile z sources
        """)
    jeżeli args jest Nic:
        args = sys.argv[1:]

    jeżeli nie args albo args[0] nie w ('-l', '-c', '-e', '-t'):
        print(USAGE)
        sys.exit(1)

    jeżeli args[0] == '-l':
        jeżeli len(args) != 2:
            print(USAGE)
            sys.exit(1)
        przy ZipFile(args[1], 'r') jako zf:
            zf.printdir()

    albo_inaczej args[0] == '-t':
        jeżeli len(args) != 2:
            print(USAGE)
            sys.exit(1)
        przy ZipFile(args[1], 'r') jako zf:
            badfile = zf.testzip()
        jeżeli badfile:
            print("The following enclosed file jest corrupted: {!r}".format(badfile))
        print("Done testing")

    albo_inaczej args[0] == '-e':
        jeżeli len(args) != 3:
            print(USAGE)
            sys.exit(1)

        przy ZipFile(args[1], 'r') jako zf:
            zf.extractall(args[2])

    albo_inaczej args[0] == '-c':
        jeżeli len(args) < 3:
            print(USAGE)
            sys.exit(1)

        def addToZip(zf, path, zippath):
            jeżeli os.path.isfile(path):
                zf.write(path, zippath, ZIP_DEFLATED)
            albo_inaczej os.path.isdir(path):
                jeżeli zippath:
                    zf.write(path, zippath)
                dla nm w os.listdir(path):
                    addToZip(zf,
                             os.path.join(path, nm), os.path.join(zippath, nm))
            # inaczej: ignore

        przy ZipFile(args[1], 'w') jako zf:
            dla path w args[2:]:
                zippath = os.path.basename(path)
                jeżeli nie zippath:
                    zippath = os.path.basename(os.path.dirname(path))
                jeżeli zippath w ('', os.curdir, os.pardir):
                    zippath = ''
                addToZip(zf, path, zippath)

jeżeli __name__ == "__main__":
    main()
