# Helper script dla test_tempfile.py.  argv[2] jest the number of a file
# descriptor which should _not_ be open.  Check this by attempting to
# write to it -- jeżeli we succeed, something jest wrong.

zaimportuj sys
zaimportuj os
z test.support zaimportuj SuppressCrashReport

przy SuppressCrashReport():
    verbose = (sys.argv[1] == 'v')
    spróbuj:
        fd = int(sys.argv[2])

        spróbuj:
            os.write(fd, b"blat")
        wyjąwszy OSError:
            # Success -- could nie write to fd.
            sys.exit(0)
        inaczej:
            jeżeli verbose:
                sys.stderr.write("fd %d jest open w child" % fd)
            sys.exit(1)

    wyjąwszy Exception:
        jeżeli verbose:
            podnieś
        sys.exit(1)
