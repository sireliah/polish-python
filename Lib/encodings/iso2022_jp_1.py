#
# iso2022_jp_1.py: Python Unicode Codec dla ISO2022_JP_1
#
# Written by Hye-Shik Chang <perky@FreeBSD.org>
#

zaimportuj _codecs_iso2022, codecs
zaimportuj _multibytecodec jako mbc

codec = _codecs_iso2022.getcodec('iso2022_jp_1')

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
        name='iso2022_jp_1',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
