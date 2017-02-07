#! /usr/bin/env python3

# Find symbolic links oraz show where they point to.
# Arguments are directories to search; default jest current directory.
# No recursion.
# (This jest a totally different program z "findsymlinks.py"!)

zaimportuj sys, os

def lll(dirname):
    dla name w os.listdir(dirname):
        jeżeli name nie w (os.curdir, os.pardir):
            full = os.path.join(dirname, name)
            jeżeli os.path.islink(full):
                print(name, '->', os.readlink(full))
def main():
    args = sys.argv[1:]
    jeżeli nie args: args = [os.curdir]
    first = 1
    dla arg w args:
        jeżeli len(args) > 1:
            jeżeli nie first: print()
            first = 0
            print(arg + ':')
    lll(arg)

jeżeli __name__ == '__main__':
    main()
