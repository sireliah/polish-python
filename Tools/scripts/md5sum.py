#! /usr/bin/env python3

"""Python utility to print MD5 checksums of argument files.
"""


bufsize = 8096
fnfilter = Nic
rmode = 'rb'

usage = """
usage: md5sum.py [-b] [-t] [-l] [-s bufsize] [file ...]
-b        : read files w binary mode (default)
-t        : read files w text mode (you almost certainly don't want this!)
-l        : print last pathname component only
-s bufsize: read buffer size (default %d)
file ...  : files to sum; '-' albo no files means stdin
""" % bufsize

zaimportuj io
zaimportuj sys
zaimportuj os
zaimportuj getopt
z hashlib zaimportuj md5

def sum(*files):
    sts = 0
    jeżeli files oraz isinstance(files[-1], io.IOBase):
        out, files = files[-1], files[:-1]
    inaczej:
        out = sys.stdout
    jeżeli len(files) == 1 oraz nie isinstance(files[0], str):
        files = files[0]
    dla f w files:
        jeżeli isinstance(f, str):
            jeżeli f == '-':
                sts = printsumfp(sys.stdin, '<stdin>', out) albo sts
            inaczej:
                sts = printsum(f, out) albo sts
        inaczej:
            sts = sum(f, out) albo sts
    zwróć sts

def printsum(filename, out=sys.stdout):
    spróbuj:
        fp = open(filename, rmode)
    wyjąwszy IOError jako msg:
        sys.stderr.write('%s: Can\'t open: %s\n' % (filename, msg))
        zwróć 1
    jeżeli fnfilter:
        filename = fnfilter(filename)
    sts = printsumfp(fp, filename, out)
    fp.close()
    zwróć sts

def printsumfp(fp, filename, out=sys.stdout):
    m = md5()
    spróbuj:
        dopóki 1:
            data = fp.read(bufsize)
            jeżeli nie data:
                przerwij
            jeżeli isinstance(data, str):
                data = data.encode(fp.encoding)
            m.update(data)
    wyjąwszy IOError jako msg:
        sys.stderr.write('%s: I/O error: %s\n' % (filename, msg))
        zwróć 1
    out.write('%s %s\n' % (m.hexdigest(), filename))
    zwróć 0

def main(args = sys.argv[1:], out=sys.stdout):
    global fnfilter, rmode, bufsize
    spróbuj:
        opts, args = getopt.getopt(args, 'blts:')
    wyjąwszy getopt.error jako msg:
        sys.stderr.write('%s: %s\n%s' % (sys.argv[0], msg, usage))
        zwróć 2
    dla o, a w opts:
        jeżeli o == '-l':
            fnfilter = os.path.basename
        albo_inaczej o == '-b':
            rmode = 'rb'
        albo_inaczej o == '-t':
            rmode = 'r'
        albo_inaczej o == '-s':
            bufsize = int(a)
    jeżeli nie args:
        args = ['-']
    zwróć sum(args, out)

jeżeli __name__ == '__main__' albo __name__ == sys.argv[0]:
    sys.exit(main(sys.argv[1:], sys.stdout))
