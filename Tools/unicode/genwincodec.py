"""This script generates a Python codec module z a Windows Code Page.

It uses the function MultiByteToWideChar to generate a decoding table.
"""

zaimportuj ctypes
z ctypes zaimportuj wintypes
z gencodec zaimportuj codegen
zaimportuj unicodedata

def genwinmap(codepage):
    MultiByteToWideChar = ctypes.windll.kernel32.MultiByteToWideChar
    MultiByteToWideChar.argtypes = [wintypes.UINT, wintypes.DWORD,
                                    wintypes.LPCSTR, ctypes.c_int,
                                    wintypes.LPWSTR, ctypes.c_int]
    MultiByteToWideChar.restype = ctypes.c_int

    enc2uni = {}

    dla i w list(range(32)) + [127]:
        enc2uni[i] = (i, 'CONTROL CHARACTER')

    dla i w range(256):
        buf = ctypes.create_unicode_buffer(2)
        ret = MultiByteToWideChar(
            codepage, 0,
            bytes([i]), 1,
            buf, 2)
        assert ret == 1, "invalid code page"
        assert buf[1] == '\x00'
        spróbuj:
            name = unicodedata.name(buf[0])
        wyjąwszy ValueError:
            spróbuj:
                name = enc2uni[i][1]
            wyjąwszy KeyError:
                name = ''

        enc2uni[i] = (ord(buf[0]), name)

    zwróć enc2uni

def genwincodec(codepage):
    zaimportuj platform
    map = genwinmap(codepage)
    encodingname = 'cp%d' % codepage
    code = codegen("", map, encodingname)
    # Replace first lines przy our own docstring
    code = '''\
"""Python Character Mapping Codec %s generated on Windows:
%s przy the command:
  python Tools/unicode/genwincodec.py %s
"""#"
''' % (encodingname, ' '.join(platform.win32_ver()), codepage
      ) + code.split('"""#"', 1)[1]

    print(code)

jeżeli __name__ == '__main__':
    zaimportuj sys
    genwincodec(int(sys.argv[1]))
