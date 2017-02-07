#! /usr/bin/env python3

# findlinksto
#
# find symbolic links to a path matching a regular expression

zaimportuj os
zaimportuj sys
zaimportuj re
zaimportuj getopt

def main():
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], '')
        jeżeli len(args) < 2:
            podnieś getopt.GetoptError('not enough arguments', Nic)
    wyjąwszy getopt.GetoptError jako msg:
        sys.stdout = sys.stderr
        print(msg)
        print('usage: findlinksto pattern directory ...')
        sys.exit(2)
    pat, dirs = args[0], args[1:]
    prog = re.compile(pat)
    dla dirname w dirs:
        os.walk(dirname, visit, prog)

def visit(prog, dirname, names):
    jeżeli os.path.islink(dirname):
        names[:] = []
        zwróć
    jeżeli os.path.ismount(dirname):
        print('descend into', dirname)
    dla name w names:
        name = os.path.join(dirname, name)
        spróbuj:
            linkto = os.readlink(name)
            jeżeli prog.search(linkto) jest nie Nic:
                print(name, '->', linkto)
        wyjąwszy OSError:
            dalej

jeżeli __name__ == '__main__':
    main()
