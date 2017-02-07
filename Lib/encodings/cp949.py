#
# cp949.py: Python Unicode Codec dla CP949
#
# Written by Hye-Shik Chang <perky@FreeBSD.org>
#

zaimportuj _codecs_kr, codecs
zaimportuj _multibytecodec jako mbc

codec = _codecs_kr.getcodec('cp949')

klasa Codec(codecs.Codec):
    encode = codec.encode
    decode = codec.decode

klasa IncrementalEncoder(mbc.MultibyteIncrementalEncoder,
                         codecs.IncrementalEncoder):
    codec = codec

klasa IncrementalDecoder(mbc.MultibyteIncrementalDecoder,
                         codecs.IncrementalDecoder):
    codec = codec

klasa StreamReader(Codec, mbc.MultibyteStreamReader, codecs.StreamReader):
    codec = codec

klasa StreamWriter(Codec, mbc.MultibyteStreamWriter, codecs.StreamWriter):
    codec = codec

def getregentry():
    zwróć codecs.CodecInfo(
        name='cp949',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
