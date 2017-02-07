zaimportuj os, string

codecs = {
    'cn': ('gb2312', 'gbk', 'gb18030', 'hz'),
    'tw': ('big5', 'cp950'),
    'hk': ('big5hkscs',),
    'jp': ('cp932', 'shift_jis', 'euc_jp', 'euc_jisx0213', 'shift_jisx0213',
           'euc_jis_2004', 'shift_jis_2004'),
    'kr': ('cp949', 'euc_kr', 'johab'),
    'iso2022': ('iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2',
                'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
                'iso2022_kr'),
}

TEMPLATE = string.Template("""\
#
# $encoding.py: Python Unicode Codec dla $ENCODING
#
# Written by Hye-Shik Chang <perky@FreeBSD.org>
#

zaimportuj _codecs_$owner, codecs
zaimportuj _multibytecodec jako mbc

codec = _codecs_$owner.getcodec('$encoding')

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
        name='$encoding',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
""")

def gencodecs(prefix):
    dla loc, encodings w codecs.items():
        dla enc w encodings:
            code = TEMPLATE.substitute(ENCODING=enc.upper(),
                                       encoding=enc.lower(),
                                       owner=loc)
            codecpath = os.path.join(prefix, enc + '.py')
            open(codecpath, 'w').write(code)

jeżeli __name__ == '__main__':
    zaimportuj sys
    gencodecs(sys.argv[1])
