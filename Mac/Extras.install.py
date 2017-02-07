"""Recursively copy a directory but skip undesired files oraz
directories (CVS, backup files, pyc files, etc)"""

zaimportuj sys
zaimportuj os
zaimportuj shutil

verbose = 1
debug = 0

def isclean(name):
    jeżeli name == 'CVS': zwróć 0
    jeżeli name == '.cvsignore': zwróć 0
    jeżeli name == '.DS_store': zwróć 0
    jeżeli name == '.svn': zwróć 0
    jeżeli name.endswith('~'): zwróć 0
    jeżeli name.endswith('.BAK'): zwróć 0
    jeżeli name.endswith('.pyc'): zwróć 0
    jeżeli name.endswith('.pyo'): zwróć 0
    jeżeli name.endswith('.orig'): zwróć 0
    zwróć 1

def copycleandir(src, dst):
    dla cursrc, dirs, files w os.walk(src):
        assert cursrc.startswith(src)
        curdst = dst + cursrc[len(src):]
        jeżeli verbose:
            print("mkdir", curdst)
        jeżeli nie debug:
            jeżeli nie os.path.exists(curdst):
                os.makedirs(curdst)
        dla fn w files:
            jeżeli isclean(fn):
                jeżeli verbose:
                    print("copy", os.path.join(cursrc, fn), os.path.join(curdst, fn))
                jeżeli nie debug:
                    shutil.copy2(os.path.join(cursrc, fn), os.path.join(curdst, fn))
            inaczej:
                jeżeli verbose:
                    print("skipfile", os.path.join(cursrc, fn))
        dla i w range(len(dirs)-1, -1, -1):
            jeżeli nie isclean(dirs[i]):
                jeżeli verbose:
                    print("skipdir", os.path.join(cursrc, dirs[i]))
                usuń dirs[i]

def main():
    jeżeli len(sys.argv) != 3:
        sys.stderr.write("Usage: %s srcdir dstdir\n" % sys.argv[0])
        sys.exit(1)
    copycleandir(sys.argv[1], sys.argv[2])

jeżeli __name__ == '__main__':
    main()
