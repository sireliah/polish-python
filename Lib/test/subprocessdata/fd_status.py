"""When called jako a script, print a comma-separated list of the open
file descriptors on stdout.

Usage:
fd_stats.py: check all file descriptors
fd_status.py fd1 fd2 ...: check only specified file descriptors
"""

zaimportuj errno
zaimportuj os
zaimportuj stat
zaimportuj sys

jeżeli __name__ == "__main__":
    fds = []
    jeżeli len(sys.argv) == 1:
        spróbuj:
            _MAXFD = os.sysconf("SC_OPEN_MAX")
        wyjąwszy:
            _MAXFD = 256
        test_fds = range(0, _MAXFD)
    inaczej:
        test_fds = map(int, sys.argv[1:])
    dla fd w test_fds:
        spróbuj:
            st = os.fstat(fd)
        wyjąwszy OSError jako e:
            jeżeli e.errno == errno.EBADF:
                kontynuuj
            podnieś
        # Ignore Solaris door files
        jeżeli nie stat.S_ISDOOR(st.st_mode):
            fds.append(fd)
    print(','.join(map(str, fds)))
