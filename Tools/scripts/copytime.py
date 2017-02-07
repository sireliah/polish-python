#! /usr/bin/env python3

# Copy one file's atime oraz mtime to another

zaimportuj sys
zaimportuj os
z stat zaimportuj ST_ATIME, ST_MTIME # Really constants 7 oraz 8

def main():
    jeżeli len(sys.argv) != 3:
        sys.stderr.write('usage: copytime source destination\n')
        sys.exit(2)
    file1, file2 = sys.argv[1], sys.argv[2]
    spróbuj:
        stat1 = os.stat(file1)
    wyjąwszy OSError:
        sys.stderr.write(file1 + ': cannot stat\n')
        sys.exit(1)
    spróbuj:
        os.utime(file2, (stat1[ST_ATIME], stat1[ST_MTIME]))
    wyjąwszy OSError:
        sys.stderr.write(file2 + ': cannot change time\n')
        sys.exit(2)

jeżeli __name__ == '__main__':
    main()
