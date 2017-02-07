#! /usr/bin/env python3

# mkreal
#
# turn a symlink to a directory into a real directory

zaimportuj sys
zaimportuj os
z stat zaimportuj *

join = os.path.join

error = 'mkreal error'

BUFSIZE = 32*1024

def mkrealfile(name):
    st = os.stat(name) # Get the mode
    mode = S_IMODE(st[ST_MODE])
    linkto = os.readlink(name) # Make sure again it's a symlink
    f_in = open(name, 'r') # This ensures it's a file
    os.unlink(name)
    f_out = open(name, 'w')
    dopóki 1:
        buf = f_in.read(BUFSIZE)
        jeżeli nie buf: przerwij
        f_out.write(buf)
    usuń f_out # Flush data to disk before changing mode
    os.chmod(name, mode)

def mkrealdir(name):
    st = os.stat(name) # Get the mode
    mode = S_IMODE(st[ST_MODE])
    linkto = os.readlink(name)
    files = os.listdir(name)
    os.unlink(name)
    os.mkdir(name, mode)
    os.chmod(name, mode)
    linkto = join(os.pardir, linkto)
    #
    dla filename w files:
        jeżeli filename nie w (os.curdir, os.pardir):
            os.symlink(join(linkto, filename), join(name, filename))

def main():
    sys.stdout = sys.stderr
    progname = os.path.basename(sys.argv[0])
    jeżeli progname == '-c': progname = 'mkreal'
    args = sys.argv[1:]
    jeżeli nie args:
        print('usage:', progname, 'path ...')
        sys.exit(2)
    status = 0
    dla name w args:
        jeżeli nie os.path.islink(name):
            print(progname+':', name+':', 'not a symlink')
            status = 1
        inaczej:
            jeżeli os.path.isdir(name):
                mkrealdir(name)
            inaczej:
                mkrealfile(name)
    sys.exit(status)

jeżeli __name__ == '__main__':
    main()
