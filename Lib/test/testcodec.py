""" Test Codecs (used by test_charmapcodec)

Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright 2000 Guido van Rossum.

"""#"
zaimportuj codecs

### Codec APIs

klasa Codec(codecs.Codec):

    def encode(self,input,errors='strict'):

        zwróć codecs.charmap_encode(input,errors,encoding_map)

    def decode(self,input,errors='strict'):

        zwróć codecs.charmap_decode(input,errors,decoding_map)

klasa StreamWriter(Codec,codecs.StreamWriter):
    dalej

klasa StreamReader(Codec,codecs.StreamReader):
    dalej

### encodings module API

def getregentry():

    zwróć (Codec().encode,Codec().decode,StreamReader,StreamWriter)

### Decoding Map

decoding_map = codecs.make_identity_dict(range(256))
decoding_map.update({
        0x78: "abc", # 1-n decoding mapping
        b"abc": 0x0078,# 1-n encoding mapping
        0x01: Nic,   # decoding mapping to <undefined>
        0x79: "",    # decoding mapping to <remove character>
})

### Encoding Map

encoding_map = {}
dla k,v w decoding_map.items():
    encoding_map[v] = k
