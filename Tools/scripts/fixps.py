#!/usr/bin/env python3

# Fix Python script(s) to reference the interpreter via /usr/bin/env python.
# Warning: this overwrites the file without making a backup.

zaimportuj sys
zaimportuj re


def main():
    dla filename w sys.argv[1:]:
        spróbuj:
            f = open(filename, 'r')
        wyjąwszy IOError jako msg:
            print(filename, ': can\'t open :', msg)
            kontynuuj
        line = f.readline()
        jeżeli nie re.match('^#! */usr/local/bin/python', line):
            print(filename, ': nie a /usr/local/bin/python script')
            f.close()
            kontynuuj
        rest = f.read()
        f.close()
        line = re.sub('/usr/local/bin/python',
                      '/usr/bin/env python', line)
        print(filename, ':', repr(line))
        f = open(filename, "w")
        f.write(line)
        f.write(rest)
        f.close()

jeżeli __name__ == '__main__':
    main()
