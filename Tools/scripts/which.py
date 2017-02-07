#! /usr/bin/env python3

# Variant of "which".
# On stderr, near oraz total misses are reported.
# '-l<flags>' argument adds ls -l<flags> of each file found.

zaimportuj sys
jeżeli sys.path[0] w (".", ""): usuń sys.path[0]

zaimportuj sys, os
z stat zaimportuj *

def msg(str):
    sys.stderr.write(str + '\n')

def main():
    pathlist = os.environ['PATH'].split(os.pathsep)

    sts = 0
    longlist = ''

    jeżeli sys.argv[1:] oraz sys.argv[1][:2] == '-l':
        longlist = sys.argv[1]
        usuń sys.argv[1]

    dla prog w sys.argv[1:]:
        ident = ()
        dla dir w pathlist:
            filename = os.path.join(dir, prog)
            spróbuj:
                st = os.stat(filename)
            wyjąwszy OSError:
                kontynuuj
            jeżeli nie S_ISREG(st[ST_MODE]):
                msg(filename + ': nie a disk file')
            inaczej:
                mode = S_IMODE(st[ST_MODE])
                jeżeli mode & 0o111:
                    jeżeli nie ident:
                        print(filename)
                        ident = st[:3]
                    inaczej:
                        jeżeli st[:3] == ident:
                            s = 'same as: '
                        inaczej:
                            s = 'also: '
                        msg(s + filename)
                inaczej:
                    msg(filename + ': nie executable')
            jeżeli longlist:
                sts = os.system('ls ' + longlist + ' ' + filename)
                jeżeli sts: msg('"ls -l" exit status: ' + repr(sts))
        jeżeli nie ident:
            msg(prog + ': nie found')
            sts = 1

    sys.exit(sts)

jeżeli __name__ == '__main__':
    main()
