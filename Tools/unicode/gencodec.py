""" Unicode Mapping Parser oraz Codec Generator.

This script parses Unicode mapping files jako available z the Unicode
site (ftp://ftp.unicode.org/Public/MAPPINGS/) oraz creates Python codec
modules z them. The codecs use the standard character mapping codec
to actually apply the mapping.

Synopsis: gencodec.py dir codec_prefix

All files w dir are scanned oraz those producing non-empty mappings
will be written to <codec_prefix><mapname>.py przy <mapname> being the
first part of the map's filename ('a' w a.b.c.txt) converted to
lowercase przy hyphens replaced by underscores.

The tool also writes marshalled versions of the mapping tables to the
same location (przy .mapping extension).

Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.
(c) Copyright Guido van Rossum, 2000.

Table generation:
(c) Copyright Marc-Andre Lemburg, 2005.
    Licensed to PSF under a Contributor Agreement.

"""#"

zaimportuj re, os, marshal, codecs

# Maximum allowed size of charmap tables
MAX_TABLE_SIZE = 8192

# Standard undefined Unicode code point
UNI_UNDEFINED = chr(0xFFFE)

# Placeholder dla a missing code point
MISSING_CODE = -1

mapRE = re.compile('((?:0x[0-9a-fA-F]+\+?)+)'
                   '\s+'
                   '((?:(?:0x[0-9a-fA-Z]+|<[A-Za-z]+>)\+?)*)'
                   '\s*'
                   '(#.+)?')

def parsecodes(codes, len=len, range=range):

    """ Converts code combinations to either a single code integer
        albo a tuple of integers.

        meta-codes (in angular brackets, e.g. <LR> oraz <RL>) are
        ignored.

        Empty codes albo illegal ones are returned jako Nic.

    """
    jeżeli nie codes:
        zwróć MISSING_CODE
    l = codes.split('+')
    jeżeli len(l) == 1:
        zwróć int(l[0],16)
    dla i w range(len(l)):
        spróbuj:
            l[i] = int(l[i],16)
        wyjąwszy ValueError:
            l[i] = MISSING_CODE
    l = [x dla x w l jeżeli x != MISSING_CODE]
    jeżeli len(l) == 1:
        zwróć l[0]
    inaczej:
        zwróć tuple(l)

def readmap(filename):

    f = open(filename,'r')
    lines = f.readlines()
    f.close()
    enc2uni = {}
    identity = []
    unmapped = list(range(256))

    # UTC mapping tables per convention don't include the identity
    # mappings dla code points 0x00 - 0x1F oraz 0x7F, unless these are
    # explicitly mapped to different characters albo undefined
    dla i w list(range(32)) + [127]:
        identity.append(i)
        unmapped.remove(i)
        enc2uni[i] = (i, 'CONTROL CHARACTER')

    dla line w lines:
        line = line.strip()
        jeżeli nie line albo line[0] == '#':
            kontynuuj
        m = mapRE.match(line)
        jeżeli nie m:
            #print '* nie matched: %s' % repr(line)
            kontynuuj
        enc,uni,comment = m.groups()
        enc = parsecodes(enc)
        uni = parsecodes(uni)
        jeżeli comment jest Nic:
            comment = ''
        inaczej:
            comment = comment[1:].strip()
        jeżeli nie isinstance(enc, tuple) oraz enc < 256:
            jeżeli enc w unmapped:
                unmapped.remove(enc)
            jeżeli enc == uni:
                identity.append(enc)
            enc2uni[enc] = (uni,comment)
        inaczej:
            enc2uni[enc] = (uni,comment)

    # If there are more identity-mapped entries than unmapped entries,
    # it pays to generate an identity dictionary first, oraz add explicit
    # mappings to Nic dla the rest
    jeżeli len(identity) >= len(unmapped):
        dla enc w unmapped:
            enc2uni[enc] = (MISSING_CODE, "")
        enc2uni['IDENTITY'] = 256

    zwróć enc2uni

def hexrepr(t, precision=4):

    jeżeli t jest Nic:
        zwróć 'Nic'
    spróbuj:
        len(t)
    wyjąwszy TypeError:
        zwróć '0x%0*X' % (precision, t)
    spróbuj:
        zwróć '(' + ', '.join(['0x%0*X' % (precision, item)
                                dla item w t]) + ')'
    wyjąwszy TypeError jako why:
        print('* failed to convert %r: %s' % (t, why))
        podnieś

def python_mapdef_code(varname, map, comments=1, precisions=(2, 4)):

    l = []
    append = l.append
    jeżeli "IDENTITY" w map:
        append("%s = codecs.make_identity_dict(range(%d))" %
               (varname, map["IDENTITY"]))
        append("%s.update({" % varname)
        splits = 1
        usuń map["IDENTITY"]
        identity = 1
    inaczej:
        append("%s = {" % varname)
        splits = 0
        identity = 0

    mappings = sorted(map.items())
    i = 0
    key_precision, value_precision = precisions
    dla mapkey, mapvalue w mappings:
        mapcomment = ''
        jeżeli isinstance(mapkey, tuple):
            (mapkey, mapcomment) = mapkey
        jeżeli isinstance(mapvalue, tuple):
            (mapvalue, mapcomment) = mapvalue
        jeżeli mapkey jest Nic:
            kontynuuj
        jeżeli (identity oraz
            mapkey == mapvalue oraz
            mapkey < 256):
            # No need to include identity mappings, since these
            # are already set dla the first 256 code points.
            kontynuuj
        key = hexrepr(mapkey, key_precision)
        value = hexrepr(mapvalue, value_precision)
        jeżeli mapcomment oraz comments:
            append('    %s: %s,\t#  %s' % (key, value, mapcomment))
        inaczej:
            append('    %s: %s,' % (key, value))
        i += 1
        jeżeli i == 4096:
            # Split the definition into parts to that the Python
            # parser doesn't dump core
            jeżeli splits == 0:
                append('}')
            inaczej:
                append('})')
            append('%s.update({' % varname)
            i = 0
            splits = splits + 1
    jeżeli splits == 0:
        append('}')
    inaczej:
        append('})')

    zwróć l

def python_tabledef_code(varname, map, comments=1, key_precision=2):

    l = []
    append = l.append
    append('%s = (' % varname)

    # Analyze map oraz create table dict
    mappings = sorted(map.items())
    table = {}
    maxkey = 255
    jeżeli 'IDENTITY' w map:
        dla key w range(256):
            table[key] = (key, '')
        usuń map['IDENTITY']
    dla mapkey, mapvalue w mappings:
        mapcomment = ''
        jeżeli isinstance(mapkey, tuple):
            (mapkey, mapcomment) = mapkey
        jeżeli isinstance(mapvalue, tuple):
            (mapvalue, mapcomment) = mapvalue
        jeżeli mapkey == MISSING_CODE:
            kontynuuj
        table[mapkey] = (mapvalue, mapcomment)
        jeżeli mapkey > maxkey:
            maxkey = mapkey
    jeżeli maxkey > MAX_TABLE_SIZE:
        # Table too large
        zwróć Nic

    # Create table code
    maxchar = 0
    dla key w range(maxkey + 1):
        jeżeli key nie w table:
            mapvalue = MISSING_CODE
            mapcomment = 'UNDEFINED'
        inaczej:
            mapvalue, mapcomment = table[key]
        jeżeli mapvalue == MISSING_CODE:
            mapchar = UNI_UNDEFINED
        inaczej:
            jeżeli isinstance(mapvalue, tuple):
                # 1-n mappings nie supported
                zwróć Nic
            inaczej:
                mapchar = chr(mapvalue)
        maxchar = max(maxchar, ord(mapchar))
        jeżeli mapcomment oraz comments:
            append('    %a \t#  %s -> %s' % (mapchar,
                                            hexrepr(key, key_precision),
                                            mapcomment))
        inaczej:
            append('    %a' % mapchar)

    jeżeli maxchar < 256:
        append('    %a \t## Widen to UCS2 dla optimization' % UNI_UNDEFINED)
    append(')')
    zwróć l

def codegen(name, map, encodingname, comments=1):

    """ Returns Python source dla the given map.

        Comments are included w the source, jeżeli comments jest true (default).

    """
    # Generate code
    decoding_map_code = python_mapdef_code(
        'decoding_map',
        map,
        comments=comments)
    decoding_table_code = python_tabledef_code(
        'decoding_table',
        map,
        comments=comments)
    encoding_map_code = python_mapdef_code(
        'encoding_map',
        codecs.make_encoding_map(map),
        comments=comments,
        precisions=(4, 2))

    jeżeli decoding_table_code:
        suffix = 'table'
    inaczej:
        suffix = 'map'

    l = [
        '''\
""" Python Character Mapping Codec %s generated z '%s' przy gencodec.py.

"""#"

zaimportuj codecs

### Codec APIs

klasa Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        zwróć codecs.charmap_encode(input, errors, encoding_%s)

    def decode(self, input, errors='strict'):
        zwróć codecs.charmap_decode(input, errors, decoding_%s)
''' % (encodingname, name, suffix, suffix)]
    l.append('''\
klasa IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=Nieprawda):
        zwróć codecs.charmap_encode(input, self.errors, encoding_%s)[0]

klasa IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=Nieprawda):
        zwróć codecs.charmap_decode(input, self.errors, decoding_%s)[0]''' %
        (suffix, suffix))

    l.append('''
klasa StreamWriter(Codec, codecs.StreamWriter):
    dalej

klasa StreamReader(Codec, codecs.StreamReader):
    dalej

### encodings module API

def getregentry():
    zwróć codecs.CodecInfo(
        name=%r,
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
''' % encodingname.replace('_', '-'))

    # Add decoding table albo map (przy preference to the table)
    jeżeli nie decoding_table_code:
        l.append('''
### Decoding Map
''')
        l.extend(decoding_map_code)
    inaczej:
        l.append('''
### Decoding Table
''')
        l.extend(decoding_table_code)

    # Add encoding map
    jeżeli decoding_table_code:
        l.append('''
### Encoding table
encoding_table = codecs.charmap_build(decoding_table)
''')
    inaczej:
        l.append('''
### Encoding Map
''')
        l.extend(encoding_map_code)

    # Final new-line
    l.append('')

    zwróć '\n'.join(l).expandtabs()

def pymap(name,map,pyfile,encodingname,comments=1):

    code = codegen(name,map,encodingname,comments)
    f = open(pyfile,'w')
    f.write(code)
    f.close()

def marshalmap(name,map,marshalfile):

    d = {}
    dla e,(u,c) w map.items():
        d[e] = (u,c)
    f = open(marshalfile,'wb')
    marshal.dump(d,f)
    f.close()

def convertdir(dir, dirprefix='', nameprefix='', comments=1):

    mapnames = os.listdir(dir)
    dla mapname w mapnames:
        mappathname = os.path.join(dir, mapname)
        jeżeli nie os.path.isfile(mappathname):
            kontynuuj
        name = os.path.split(mapname)[1]
        name = name.replace('-','_')
        name = name.split('.')[0]
        name = name.lower()
        name = nameprefix + name
        codefile = name + '.py'
        marshalfile = name + '.mapping'
        print('converting %s to %s oraz %s' % (mapname,
                                              dirprefix + codefile,
                                              dirprefix + marshalfile))
        spróbuj:
            map = readmap(os.path.join(dir,mapname))
            jeżeli nie map:
                print('* map jest empty; skipping')
            inaczej:
                pymap(mappathname, map, dirprefix + codefile,name,comments)
                marshalmap(mappathname, map, dirprefix + marshalfile)
        wyjąwszy ValueError jako why:
            print('* conversion failed: %s' % why)
            podnieś

def rewritepythondir(dir, dirprefix='', comments=1):

    mapnames = os.listdir(dir)
    dla mapname w mapnames:
        jeżeli nie mapname.endswith('.mapping'):
            kontynuuj
        name = mapname[:-len('.mapping')]
        codefile = name + '.py'
        print('converting %s to %s' % (mapname,
                                       dirprefix + codefile))
        spróbuj:
            map = marshal.load(open(os.path.join(dir,mapname),
                               'rb'))
            jeżeli nie map:
                print('* map jest empty; skipping')
            inaczej:
                pymap(mapname, map, dirprefix + codefile,name,comments)
        wyjąwszy ValueError jako why:
            print('* conversion failed: %s' % why)

jeżeli __name__ == '__main__':

    zaimportuj sys
    jeżeli 1:
        convertdir(*sys.argv[1:])
    inaczej:
        rewritepythondir(*sys.argv[1:])
