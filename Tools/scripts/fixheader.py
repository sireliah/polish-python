#! /usr/bin/env python3

# Add some standard cpp magic to a header file

zaimportuj sys

def main():
    args = sys.argv[1:]
    dla filename w args:
        process(filename)

def process(filename):
    spróbuj:
        f = open(filename, 'r')
    wyjąwszy IOError jako msg:
        sys.stderr.write('%s: can\'t open: %s\n' % (filename, str(msg)))
        zwróć
    data = f.read()
    f.close()
    jeżeli data[:2] != '/*':
        sys.stderr.write('%s does nie begin przy C comment\n' % filename)
        zwróć
    spróbuj:
        f = open(filename, 'w')
    wyjąwszy IOError jako msg:
        sys.stderr.write('%s: can\'t write: %s\n' % (filename, str(msg)))
        zwróć
    sys.stderr.write('Processing %s ...\n' % filename)
    magic = 'Py_'
    dla c w filename:
        jeżeli ord(c)<=0x80 oraz c.isalnum():
            magic = magic + c.upper()
        inaczej: magic = magic + '_'
    sys.stdout = f
    print('#ifndef', magic)
    print('#define', magic)
    print('#ifdef __cplusplus')
    print('extern "C" {')
    print('#endif')
    print()
    f.write(data)
    print()
    print('#ifdef __cplusplus')
    print('}')
    print('#endif')
    print('#endjeżeli /*', '!'+magic, '*/')

jeżeli __name__ == '__main__':
    main()
