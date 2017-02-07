#! /usr/bin/env python3

# linktree
#
# Make a copy of a directory tree przy symbolic links to all files w the
# original tree.
# All symbolic links go to a special symbolic link at the top, so you
# can easily fix things jeżeli the original source tree moves.
# See also "mkreal".
#
# usage: mklinks oldtree newtree

zaimportuj sys, os

LINK = '.LINK' # Name of special symlink at the top.

debug = 0

def main():
    jeżeli nie 3 <= len(sys.argv) <= 4:
        print('usage:', sys.argv[0], 'oldtree newtree [linkto]')
        zwróć 2
    oldtree, newtree = sys.argv[1], sys.argv[2]
    jeżeli len(sys.argv) > 3:
        link = sys.argv[3]
        link_may_fail = 1
    inaczej:
        link = LINK
        link_may_fail = 0
    jeżeli nie os.path.isdir(oldtree):
        print(oldtree + ': nie a directory')
        zwróć 1
    spróbuj:
        os.mkdir(newtree, 0o777)
    wyjąwszy OSError jako msg:
        print(newtree + ': cannot mkdir:', msg)
        zwróć 1
    linkname = os.path.join(newtree, link)
    spróbuj:
        os.symlink(os.path.join(os.pardir, oldtree), linkname)
    wyjąwszy OSError jako msg:
        jeżeli nie link_may_fail:
            print(linkname + ': cannot symlink:', msg)
            zwróć 1
        inaczej:
            print(linkname + ': warning: cannot symlink:', msg)
    linknames(oldtree, newtree, link)
    zwróć 0

def linknames(old, new, link):
    jeżeli debug: print('linknames', (old, new, link))
    spróbuj:
        names = os.listdir(old)
    wyjąwszy OSError jako msg:
        print(old + ': warning: cannot listdir:', msg)
        zwróć
    dla name w names:
        jeżeli name nie w (os.curdir, os.pardir):
            oldname = os.path.join(old, name)
            linkname = os.path.join(link, name)
            newname = os.path.join(new, name)
            jeżeli debug > 1: print(oldname, newname, linkname)
            jeżeli os.path.isdir(oldname) oraz \
               nie os.path.islink(oldname):
                spróbuj:
                    os.mkdir(newname, 0o777)
                    ok = 1
                wyjąwszy:
                    print(newname + \
                          ': warning: cannot mkdir:', msg)
                    ok = 0
                jeżeli ok:
                    linkname = os.path.join(os.pardir,
                                            linkname)
                    linknames(oldname, newname, linkname)
            inaczej:
                os.symlink(linkname, newname)

jeżeli __name__ == '__main__':
    sys.exit(main())
