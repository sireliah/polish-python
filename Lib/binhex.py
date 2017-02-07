"""Macintosh binhex compression/decompression.

easy interface:
binhex(inputfilename, outputfilename)
hexbin(inputfilename, outputfilename)
"""

#
# Jack Jansen, CWI, August 1995.
#
# The module jest supposed to be jako compatible jako possible. Especially the
# easy interface should work "as expected" on any platform.
# XXXX Note: currently, textfiles appear w mac-form on all platforms.
# We seem to lack a simple character-translate w python.
# (we should probably use ISO-Latin-1 on all but the mac platform).
# XXXX The simple routines are too simple: they expect to hold the complete
# files in-core. Should be fixed.
# XXXX It would be nice to handle AppleDouble format on unix
# (dla servers serving macs).
# XXXX I don't understand what happens when you get 0x90 times the same byte on
# input. The resulting code (xx 90 90) would appear to be interpreted jako an
# escaped *value* of 0x90. All coders I've seen appear to ignore this nicety...
#
zaimportuj io
zaimportuj os
zaimportuj struct
zaimportuj binascii

__all__ = ["binhex","hexbin","Error"]

klasa Error(Exception):
    dalej

# States (what have we written)
_DID_HEADER = 0
_DID_DATA = 1

# Various constants
REASONABLY_LARGE = 32768  # Minimal amount we dalej the rle-coder
LINELEN = 64
RUNCHAR = b"\x90"

#
# This code jest no longer byte-order dependent


klasa FInfo:
    def __init__(self):
        self.Type = '????'
        self.Creator = '????'
        self.Flags = 0

def getfileinfo(name):
    finfo = FInfo()
    przy io.open(name, 'rb') jako fp:
        # Quick check dla textfile
        data = fp.read(512)
        jeżeli 0 nie w data:
            finfo.Type = 'TEXT'
        fp.seek(0, 2)
        dsize = fp.tell()
    dir, file = os.path.split(name)
    file = file.replace(':', '-', 1)
    zwróć file, finfo, dsize, 0

klasa openrsrc:
    def __init__(self, *args):
        dalej

    def read(self, *args):
        zwróć b''

    def write(self, *args):
        dalej

    def close(self):
        dalej

klasa _Hqxcoderengine:
    """Write data to the coder w 3-byte chunks"""

    def __init__(self, ofp):
        self.ofp = ofp
        self.data = b''
        self.hqxdata = b''
        self.linelen = LINELEN - 1

    def write(self, data):
        self.data = self.data + data
        datalen = len(self.data)
        todo = (datalen // 3) * 3
        data = self.data[:todo]
        self.data = self.data[todo:]
        jeżeli nie data:
            zwróć
        self.hqxdata = self.hqxdata + binascii.b2a_hqx(data)
        self._flush(0)

    def _flush(self, force):
        first = 0
        dopóki first <= len(self.hqxdata) - self.linelen:
            last = first + self.linelen
            self.ofp.write(self.hqxdata[first:last] + b'\n')
            self.linelen = LINELEN
            first = last
        self.hqxdata = self.hqxdata[first:]
        jeżeli force:
            self.ofp.write(self.hqxdata + b':\n')

    def close(self):
        jeżeli self.data:
            self.hqxdata = self.hqxdata + binascii.b2a_hqx(self.data)
        self._flush(1)
        self.ofp.close()
        usuń self.ofp

klasa _Rlecoderengine:
    """Write data to the RLE-coder w suitably large chunks"""

    def __init__(self, ofp):
        self.ofp = ofp
        self.data = b''

    def write(self, data):
        self.data = self.data + data
        jeżeli len(self.data) < REASONABLY_LARGE:
            zwróć
        rledata = binascii.rlecode_hqx(self.data)
        self.ofp.write(rledata)
        self.data = b''

    def close(self):
        jeżeli self.data:
            rledata = binascii.rlecode_hqx(self.data)
            self.ofp.write(rledata)
        self.ofp.close()
        usuń self.ofp

klasa BinHex:
    def __init__(self, name_finfo_dlen_rlen, ofp):
        name, finfo, dlen, rlen = name_finfo_dlen_rlen
        close_on_error = Nieprawda
        jeżeli isinstance(ofp, str):
            ofname = ofp
            ofp = io.open(ofname, 'wb')
            close_on_error = Prawda
        spróbuj:
            ofp.write(b'(This file must be converted przy BinHex 4.0)\r\r:')
            hqxer = _Hqxcoderengine(ofp)
            self.ofp = _Rlecoderengine(hqxer)
            self.crc = 0
            jeżeli finfo jest Nic:
                finfo = FInfo()
            self.dlen = dlen
            self.rlen = rlen
            self._writeinfo(name, finfo)
            self.state = _DID_HEADER
        wyjąwszy:
            jeżeli close_on_error:
                ofp.close()
            podnieś

    def _writeinfo(self, name, finfo):
        nl = len(name)
        jeżeli nl > 63:
            podnieś Error('Filename too long')
        d = bytes([nl]) + name.encode("latin-1") + b'\0'
        tp, cr = finfo.Type, finfo.Creator
        jeżeli isinstance(tp, str):
            tp = tp.encode("latin-1")
        jeżeli isinstance(cr, str):
            cr = cr.encode("latin-1")
        d2 = tp + cr

        # Force all structs to be packed przy big-endian
        d3 = struct.pack('>h', finfo.Flags)
        d4 = struct.pack('>ii', self.dlen, self.rlen)
        info = d + d2 + d3 + d4
        self._write(info)
        self._writecrc()

    def _write(self, data):
        self.crc = binascii.crc_hqx(data, self.crc)
        self.ofp.write(data)

    def _writecrc(self):
        # XXXX Should this be here??
        # self.crc = binascii.crc_hqx('\0\0', self.crc)
        jeżeli self.crc < 0:
            fmt = '>h'
        inaczej:
            fmt = '>H'
        self.ofp.write(struct.pack(fmt, self.crc))
        self.crc = 0

    def write(self, data):
        jeżeli self.state != _DID_HEADER:
            podnieś Error('Writing data at the wrong time')
        self.dlen = self.dlen - len(data)
        self._write(data)

    def close_data(self):
        jeżeli self.dlen != 0:
            podnieś Error('Incorrect data size, diff=%r' % (self.rlen,))
        self._writecrc()
        self.state = _DID_DATA

    def write_rsrc(self, data):
        jeżeli self.state < _DID_DATA:
            self.close_data()
        jeżeli self.state != _DID_DATA:
            podnieś Error('Writing resource data at the wrong time')
        self.rlen = self.rlen - len(data)
        self._write(data)

    def close(self):
        jeżeli self.state jest Nic:
            zwróć
        spróbuj:
            jeżeli self.state < _DID_DATA:
                self.close_data()
            jeżeli self.state != _DID_DATA:
                podnieś Error('Close at the wrong time')
            jeżeli self.rlen != 0:
                podnieś Error("Incorrect resource-datasize, diff=%r" % (self.rlen,))
            self._writecrc()
        w_końcu:
            self.state = Nic
            ofp = self.ofp
            usuń self.ofp
            ofp.close()

def binhex(inp, out):
    """binhex(infilename, outfilename): create binhex-encoded copy of a file"""
    finfo = getfileinfo(inp)
    ofp = BinHex(finfo, out)

    przy io.open(inp, 'rb') jako ifp:
        # XXXX Do textfile translation on non-mac systems
        dopóki Prawda:
            d = ifp.read(128000)
            jeżeli nie d: przerwij
            ofp.write(d)
        ofp.close_data()

    ifp = openrsrc(inp, 'rb')
    dopóki Prawda:
        d = ifp.read(128000)
        jeżeli nie d: przerwij
        ofp.write_rsrc(d)
    ofp.close()
    ifp.close()

klasa _Hqxdecoderengine:
    """Read data via the decoder w 4-byte chunks"""

    def __init__(self, ifp):
        self.ifp = ifp
        self.eof = 0

    def read(self, totalwtd):
        """Read at least wtd bytes (or until EOF)"""
        decdata = b''
        wtd = totalwtd
        #
        # The loop here jest convoluted, since we don't really now how
        # much to decode: there may be newlines w the incoming data.
        dopóki wtd > 0:
            jeżeli self.eof: zwróć decdata
            wtd = ((wtd + 2) // 3) * 4
            data = self.ifp.read(wtd)
            #
            # Next problem: there may nie be a complete number of
            # bytes w what we dalej to a2b. Solve by yet another
            # loop.
            #
            dopóki Prawda:
                spróbuj:
                    decdatacur, self.eof = binascii.a2b_hqx(data)
                    przerwij
                wyjąwszy binascii.Incomplete:
                    dalej
                newdata = self.ifp.read(1)
                jeżeli nie newdata:
                    podnieś Error('Premature EOF on binhex file')
                data = data + newdata
            decdata = decdata + decdatacur
            wtd = totalwtd - len(decdata)
            jeżeli nie decdata oraz nie self.eof:
                podnieś Error('Premature EOF on binhex file')
        zwróć decdata

    def close(self):
        self.ifp.close()

klasa _Rledecoderengine:
    """Read data via the RLE-coder"""

    def __init__(self, ifp):
        self.ifp = ifp
        self.pre_buffer = b''
        self.post_buffer = b''
        self.eof = 0

    def read(self, wtd):
        jeżeli wtd > len(self.post_buffer):
            self._fill(wtd - len(self.post_buffer))
        rv = self.post_buffer[:wtd]
        self.post_buffer = self.post_buffer[wtd:]
        zwróć rv

    def _fill(self, wtd):
        self.pre_buffer = self.pre_buffer + self.ifp.read(wtd + 4)
        jeżeli self.ifp.eof:
            self.post_buffer = self.post_buffer + \
                binascii.rledecode_hqx(self.pre_buffer)
            self.pre_buffer = b''
            zwróć

        #
        # Obfuscated code ahead. We have to take care that we don't
        # end up przy an orphaned RUNCHAR later on. So, we keep a couple
        # of bytes w the buffer, depending on what the end of
        # the buffer looks like:
        # '\220\0\220' - Keep 3 bytes: repeated \220 (escaped jako \220\0)
        # '?\220' - Keep 2 bytes: repeated something-inaczej
        # '\220\0' - Escaped \220: Keep 2 bytes.
        # '?\220?' - Complete repeat sequence: decode all
        # otherwise: keep 1 byte.
        #
        mark = len(self.pre_buffer)
        jeżeli self.pre_buffer[-3:] == RUNCHAR + b'\0' + RUNCHAR:
            mark = mark - 3
        albo_inaczej self.pre_buffer[-1:] == RUNCHAR:
            mark = mark - 2
        albo_inaczej self.pre_buffer[-2:] == RUNCHAR + b'\0':
            mark = mark - 2
        albo_inaczej self.pre_buffer[-2:-1] == RUNCHAR:
            dalej # Decode all
        inaczej:
            mark = mark - 1

        self.post_buffer = self.post_buffer + \
            binascii.rledecode_hqx(self.pre_buffer[:mark])
        self.pre_buffer = self.pre_buffer[mark:]

    def close(self):
        self.ifp.close()

klasa HexBin:
    def __init__(self, ifp):
        jeżeli isinstance(ifp, str):
            ifp = io.open(ifp, 'rb')
        #
        # Find initial colon.
        #
        dopóki Prawda:
            ch = ifp.read(1)
            jeżeli nie ch:
                podnieś Error("No binhex data found")
            # Cater dla \r\n terminated lines (which show up jako \n\r, hence
            # all lines start przy \r)
            jeżeli ch == b'\r':
                kontynuuj
            jeżeli ch == b':':
                przerwij

        hqxifp = _Hqxdecoderengine(ifp)
        self.ifp = _Rledecoderengine(hqxifp)
        self.crc = 0
        self._readheader()

    def _read(self, len):
        data = self.ifp.read(len)
        self.crc = binascii.crc_hqx(data, self.crc)
        zwróć data

    def _checkcrc(self):
        filecrc = struct.unpack('>h', self.ifp.read(2))[0] & 0xffff
        #self.crc = binascii.crc_hqx('\0\0', self.crc)
        # XXXX Is this needed??
        self.crc = self.crc & 0xffff
        jeżeli filecrc != self.crc:
            podnieś Error('CRC error, computed %x, read %x'
                        % (self.crc, filecrc))
        self.crc = 0

    def _readheader(self):
        len = self._read(1)
        fname = self._read(ord(len))
        rest = self._read(1 + 4 + 4 + 2 + 4 + 4)
        self._checkcrc()

        type = rest[1:5]
        creator = rest[5:9]
        flags = struct.unpack('>h', rest[9:11])[0]
        self.dlen = struct.unpack('>l', rest[11:15])[0]
        self.rlen = struct.unpack('>l', rest[15:19])[0]

        self.FName = fname
        self.FInfo = FInfo()
        self.FInfo.Creator = creator
        self.FInfo.Type = type
        self.FInfo.Flags = flags

        self.state = _DID_HEADER

    def read(self, *n):
        jeżeli self.state != _DID_HEADER:
            podnieś Error('Read data at wrong time')
        jeżeli n:
            n = n[0]
            n = min(n, self.dlen)
        inaczej:
            n = self.dlen
        rv = b''
        dopóki len(rv) < n:
            rv = rv + self._read(n-len(rv))
        self.dlen = self.dlen - n
        zwróć rv

    def close_data(self):
        jeżeli self.state != _DID_HEADER:
            podnieś Error('close_data at wrong time')
        jeżeli self.dlen:
            dummy = self._read(self.dlen)
        self._checkcrc()
        self.state = _DID_DATA

    def read_rsrc(self, *n):
        jeżeli self.state == _DID_HEADER:
            self.close_data()
        jeżeli self.state != _DID_DATA:
            podnieś Error('Read resource data at wrong time')
        jeżeli n:
            n = n[0]
            n = min(n, self.rlen)
        inaczej:
            n = self.rlen
        self.rlen = self.rlen - n
        zwróć self._read(n)

    def close(self):
        jeżeli self.state jest Nic:
            zwróć
        spróbuj:
            jeżeli self.rlen:
                dummy = self.read_rsrc(self.rlen)
            self._checkcrc()
        w_końcu:
            self.state = Nic
            self.ifp.close()

def hexbin(inp, out):
    """hexbin(infilename, outfilename) - Decode binhexed file"""
    ifp = HexBin(inp)
    finfo = ifp.FInfo
    jeżeli nie out:
        out = ifp.FName

    przy io.open(out, 'wb') jako ofp:
        # XXXX Do translation on non-mac systems
        dopóki Prawda:
            d = ifp.read(128000)
            jeżeli nie d: przerwij
            ofp.write(d)
    ifp.close_data()

    d = ifp.read_rsrc(128000)
    jeżeli d:
        ofp = openrsrc(out, 'wb')
        ofp.write(d)
        dopóki Prawda:
            d = ifp.read_rsrc(128000)
            jeżeli nie d: przerwij
            ofp.write(d)
        ofp.close()

    ifp.close()
