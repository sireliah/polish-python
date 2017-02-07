#! /usr/bin/env python3

# Print the product of age oraz size of each file, w suitable units.
#
# Usage: byteyears [ -a | -m | -c ] file ...
#
# Options -[amc] select atime, mtime (default) albo ctime jako age.

zaimportuj sys, os, time
z stat zaimportuj *

def main():

    # Use lstat() to stat files jeżeli it exists, inaczej stat()
    spróbuj:
        statfunc = os.lstat
    wyjąwszy AttributeError:
        statfunc = os.stat

    # Parse options
    jeżeli sys.argv[1] == '-m':
        itime = ST_MTIME
        usuń sys.argv[1]
    albo_inaczej sys.argv[1] == '-c':
        itime = ST_CTIME
        usuń sys.argv[1]
    albo_inaczej sys.argv[1] == '-a':
        itime = ST_CTIME
        usuń sys.argv[1]
    inaczej:
        itime = ST_MTIME

    secs_per_year = 365.0 * 24.0 * 3600.0   # Scale factor
    now = time.time()                       # Current time, dla age computations
    status = 0                              # Exit status, set to 1 on errors

    # Compute max file name length
    maxlen = 1
    dla filename w sys.argv[1:]:
        maxlen = max(maxlen, len(filename))

    # Process each argument w turn
    dla filename w sys.argv[1:]:
        spróbuj:
            st = statfunc(filename)
        wyjąwszy OSError jako msg:
            sys.stderr.write("can't stat %r: %r\n" % (filename, msg))
            status = 1
            st = ()
        jeżeli st:
            anytime = st[itime]
            size = st[ST_SIZE]
            age = now - anytime
            byteyears = float(size) * float(age) / secs_per_year
            print(filename.ljust(maxlen), end=' ')
            print(repr(int(byteyears)).rjust(8))

    sys.exit(status)

jeżeli __name__ == '__main__':
    main()
