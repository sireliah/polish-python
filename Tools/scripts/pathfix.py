#!/usr/bin/env python3

# Change the #! line occurring w Python scripts.  The new interpreter
# pathname must be given przy a -i option.
#
# Command line arguments are files albo directories to be processed.
# Directories are searched recursively dla files whose name looks
# like a python module.
# Symbolic links are always ignored (wyjąwszy jako explicit directory
# arguments).  Of course, the original file jest kept jako a back-up
# (przy a "~" attached to its name).
#
# Undoubtedly you can do this using find oraz sed albo perl, but this jest
# a nice example of Python code that recurses down a directory tree
# oraz uses regular expressions.  Also note several subtleties like
# preserving the file's mode oraz avoiding to even write a temp file
# when no changes are needed dla a file.
#
# NB: by changing only the function fixfile() you can turn this
# into a program dla a different change to Python programs...

zaimportuj sys
zaimportuj re
zaimportuj os
z stat zaimportuj *
zaimportuj getopt

err = sys.stderr.write
dbg = err
rep = sys.stdout.write

new_interpreter = Nic
preserve_timestamps = Nieprawda

def main():
    global new_interpreter
    global preserve_timestamps
    usage = ('usage: %s -i /interpreter -p file-or-directory ...\n' %
             sys.argv[0])
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'i:p')
    wyjąwszy getopt.error jako msg:
        err(str(msg) + '\n')
        err(usage)
        sys.exit(2)
    dla o, a w opts:
        jeżeli o == '-i':
            new_interpreter = a.encode()
        jeżeli o == '-p':
            preserve_timestamps = Prawda
    jeżeli nie new_interpreter albo nie new_interpreter.startswith(b'/') albo \
           nie args:
        err('-i option albo file-or-directory missing\n')
        err(usage)
        sys.exit(2)
    bad = 0
    dla arg w args:
        jeżeli os.path.isdir(arg):
            jeżeli recursedown(arg): bad = 1
        albo_inaczej os.path.islink(arg):
            err(arg + ': will nie process symbolic links\n')
            bad = 1
        inaczej:
            jeżeli fix(arg): bad = 1
    sys.exit(bad)

ispythonprog = re.compile('^[a-zA-Z0-9_]+\.py$')
def ispython(name):
    zwróć bool(ispythonprog.match(name))

def recursedown(dirname):
    dbg('recursedown(%r)\n' % (dirname,))
    bad = 0
    spróbuj:
        names = os.listdir(dirname)
    wyjąwszy OSError jako msg:
        err('%s: cannot list directory: %r\n' % (dirname, msg))
        zwróć 1
    names.sort()
    subdirs = []
    dla name w names:
        jeżeli name w (os.curdir, os.pardir): kontynuuj
        fullname = os.path.join(dirname, name)
        jeżeli os.path.islink(fullname): dalej
        albo_inaczej os.path.isdir(fullname):
            subdirs.append(fullname)
        albo_inaczej ispython(name):
            jeżeli fix(fullname): bad = 1
    dla fullname w subdirs:
        jeżeli recursedown(fullname): bad = 1
    zwróć bad

def fix(filename):
##  dbg('fix(%r)\n' % (filename,))
    spróbuj:
        f = open(filename, 'rb')
    wyjąwszy IOError jako msg:
        err('%s: cannot open: %r\n' % (filename, msg))
        zwróć 1
    line = f.readline()
    fixed = fixline(line)
    jeżeli line == fixed:
        rep(filename+': no change\n')
        f.close()
        zwróć
    head, tail = os.path.split(filename)
    tempname = os.path.join(head, '@' + tail)
    spróbuj:
        g = open(tempname, 'wb')
    wyjąwszy IOError jako msg:
        f.close()
        err('%s: cannot create: %r\n' % (tempname, msg))
        zwróć 1
    rep(filename + ': updating\n')
    g.write(fixed)
    BUFSIZE = 8*1024
    dopóki 1:
        buf = f.read(BUFSIZE)
        jeżeli nie buf: przerwij
        g.write(buf)
    g.close()
    f.close()

    # Finishing touch -- move files

    mtime = Nic
    atime = Nic
    # First copy the file's mode to the temp file
    spróbuj:
        statbuf = os.stat(filename)
        mtime = statbuf.st_mtime
        atime = statbuf.st_atime
        os.chmod(tempname, statbuf[ST_MODE] & 0o7777)
    wyjąwszy OSError jako msg:
        err('%s: warning: chmod failed (%r)\n' % (tempname, msg))
    # Then make a backup of the original file jako filename~
    spróbuj:
        os.rename(filename, filename + '~')
    wyjąwszy OSError jako msg:
        err('%s: warning: backup failed (%r)\n' % (filename, msg))
    # Now move the temp file to the original file
    spróbuj:
        os.rename(tempname, filename)
    wyjąwszy OSError jako msg:
        err('%s: rename failed (%r)\n' % (filename, msg))
        zwróć 1
    jeżeli preserve_timestamps:
        jeżeli atime oraz mtime:
            spróbuj:
                os.utime(filename, (atime, mtime))
            wyjąwszy OSError jako msg:
                err('%s: reset of timestamp failed (%r)\n' % (filename, msg))
                zwróć 1
    # Return success
    zwróć 0

def fixline(line):
    jeżeli nie line.startswith(b'#!'):
        zwróć line
    jeżeli b"python" nie w line:
        zwróć line
    zwróć b'#! ' + new_interpreter + b'\n'

jeżeli __name__ == '__main__':
    main()
