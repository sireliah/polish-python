#! /usr/bin/env python3
# Check that all ".pyc" files exist oraz are up-to-date
# Uses module 'os'

zaimportuj sys
zaimportuj os
z stat zaimportuj ST_MTIME
zaimportuj importlib.util

# PEP 3147 compatibility (PYC Repository Directories)
cache_from_source = (importlib.util.cache_from_source jeżeli sys.implementation.cache_tag
                     inaczej lambda path: path + 'c')


def main():
    jeżeli len(sys.argv) > 1:
        verbose = (sys.argv[1] == '-v')
        silent = (sys.argv[1] == '-s')
    inaczej:
        verbose = silent = Nieprawda
    MAGIC = importlib.util.MAGIC_NUMBER
    jeżeli nie silent:
        print('Using MAGIC word', repr(MAGIC))
    dla dirname w sys.path:
        spróbuj:
            names = os.listdir(dirname)
        wyjąwszy OSError:
            print('Cannot list directory', repr(dirname))
            kontynuuj
        jeżeli nie silent:
            print('Checking ', repr(dirname), '...')
        dla name w sorted(names):
            jeżeli name.endswith('.py'):
                name = os.path.join(dirname, name)
                spróbuj:
                    st = os.stat(name)
                wyjąwszy OSError:
                    print('Cannot stat', repr(name))
                    kontynuuj
                jeżeli verbose:
                    print('Check', repr(name), '...')
                name_c = cache_from_source(name)
                spróbuj:
                    przy open(name_c, 'rb') jako f:
                        magic_str = f.read(4)
                        mtime_str = f.read(4)
                wyjąwszy IOError:
                    print('Cannot open', repr(name_c))
                    kontynuuj
                jeżeli magic_str != MAGIC:
                    print('Bad MAGIC word w ".pyc" file', end=' ')
                    print(repr(name_c))
                    kontynuuj
                mtime = get_long(mtime_str)
                jeżeli mtime w {0, -1}:
                    print('Bad ".pyc" file', repr(name_c))
                albo_inaczej mtime != st[ST_MTIME]:
                    print('Out-of-date ".pyc" file', end=' ')
                    print(repr(name_c))


def get_long(s):
    jeżeli len(s) != 4:
        zwróć -1
    zwróć s[0] + (s[1] << 8) + (s[2] << 16) + (s[3] << 24)


jeżeli __name__ == '__main__':
    main()
