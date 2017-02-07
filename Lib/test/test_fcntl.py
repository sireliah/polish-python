"""Test program dla the fcntl C module.
"""
zaimportuj platform
zaimportuj os
zaimportuj struct
zaimportuj sys
zaimportuj unittest
z test.support zaimportuj (verbose, TESTFN, unlink, run_unittest, import_module,
                          cpython_only)

# Skip test jeżeli no fcntl module.
fcntl = import_module('fcntl')


# TODO - Write tests dla flock() oraz lockf().

def get_lockdata():
    spróbuj:
        os.O_LARGEFILE
    wyjąwszy AttributeError:
        start_len = "ll"
    inaczej:
        start_len = "qq"

    jeżeli (sys.platform.startswith(('netbsd', 'freebsd', 'openbsd', 'bsdos'))
        albo sys.platform == 'darwin'):
        jeżeli struct.calcsize('l') == 8:
            off_t = 'l'
            pid_t = 'i'
        inaczej:
            off_t = 'lxxxx'
            pid_t = 'l'
        lockdata = struct.pack(off_t + off_t + pid_t + 'hh', 0, 0, 0,
                               fcntl.F_WRLCK, 0)
    albo_inaczej sys.platform.startswith('gnukfreebsd'):
        lockdata = struct.pack('qqihhi', 0, 0, 0, fcntl.F_WRLCK, 0, 0)
    albo_inaczej sys.platform w ['aix3', 'aix4', 'hp-uxB', 'unixware7']:
        lockdata = struct.pack('hhlllii', fcntl.F_WRLCK, 0, 0, 0, 0, 0, 0)
    inaczej:
        lockdata = struct.pack('hh'+start_len+'hh', fcntl.F_WRLCK, 0, 0, 0, 0, 0)
    jeżeli lockdata:
        jeżeli verbose:
            print('struct.pack: ', repr(lockdata))
    zwróć lockdata

lockdata = get_lockdata()

klasa BadFile:
    def __init__(self, fn):
        self.fn = fn
    def fileno(self):
        zwróć self.fn

klasa TestFcntl(unittest.TestCase):

    def setUp(self):
        self.f = Nic

    def tearDown(self):
        jeżeli self.f oraz nie self.f.closed:
            self.f.close()
        unlink(TESTFN)

    def test_fcntl_fileno(self):
        # the example z the library docs
        self.f = open(TESTFN, 'wb')
        rv = fcntl.fcntl(self.f.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        jeżeli verbose:
            print('Status z fcntl przy O_NONBLOCK: ', rv)
        rv = fcntl.fcntl(self.f.fileno(), fcntl.F_SETLKW, lockdata)
        jeżeli verbose:
            print('String z fcntl przy F_SETLKW: ', repr(rv))
        self.f.close()

    def test_fcntl_file_descriptor(self):
        # again, but dalej the file rather than numeric descriptor
        self.f = open(TESTFN, 'wb')
        rv = fcntl.fcntl(self.f, fcntl.F_SETFL, os.O_NONBLOCK)
        jeżeli verbose:
            print('Status z fcntl przy O_NONBLOCK: ', rv)
        rv = fcntl.fcntl(self.f, fcntl.F_SETLKW, lockdata)
        jeżeli verbose:
            print('String z fcntl przy F_SETLKW: ', repr(rv))
        self.f.close()

    def test_fcntl_bad_file(self):
        przy self.assertRaises(ValueError):
            fcntl.fcntl(-1, fcntl.F_SETFL, os.O_NONBLOCK)
        przy self.assertRaises(ValueError):
            fcntl.fcntl(BadFile(-1), fcntl.F_SETFL, os.O_NONBLOCK)
        przy self.assertRaises(TypeError):
            fcntl.fcntl('spam', fcntl.F_SETFL, os.O_NONBLOCK)
        przy self.assertRaises(TypeError):
            fcntl.fcntl(BadFile('spam'), fcntl.F_SETFL, os.O_NONBLOCK)

    @cpython_only
    def test_fcntl_bad_file_overflow(self):
        z _testcapi zaimportuj INT_MAX, INT_MIN
        # Issue 15989
        przy self.assertRaises(OverflowError):
            fcntl.fcntl(INT_MAX + 1, fcntl.F_SETFL, os.O_NONBLOCK)
        przy self.assertRaises(OverflowError):
            fcntl.fcntl(BadFile(INT_MAX + 1), fcntl.F_SETFL, os.O_NONBLOCK)
        przy self.assertRaises(OverflowError):
            fcntl.fcntl(INT_MIN - 1, fcntl.F_SETFL, os.O_NONBLOCK)
        przy self.assertRaises(OverflowError):
            fcntl.fcntl(BadFile(INT_MIN - 1), fcntl.F_SETFL, os.O_NONBLOCK)

    @unittest.skipIf(
        platform.machine().startswith('arm') oraz platform.system() == 'Linux',
        "ARM Linux returns EINVAL dla F_NOTIFY DN_MULTISHOT")
    def test_fcntl_64_bit(self):
        # Issue #1309352: fcntl shouldn't fail when the third arg fits w a
        # C 'long' but nie w a C 'int'.
        spróbuj:
            cmd = fcntl.F_NOTIFY
            # This flag jest larger than 2**31 w 64-bit builds
            flags = fcntl.DN_MULTISHOT
        wyjąwszy AttributeError:
            self.skipTest("F_NOTIFY albo DN_MULTISHOT unavailable")
        fd = os.open(os.path.dirname(os.path.abspath(TESTFN)), os.O_RDONLY)
        spróbuj:
            fcntl.fcntl(fd, cmd, flags)
        w_końcu:
            os.close(fd)

    def test_flock(self):
        # Solaris needs readable file dla shared lock
        self.f = open(TESTFN, 'wb+')
        fileno = self.f.fileno()
        fcntl.flock(fileno, fcntl.LOCK_SH)
        fcntl.flock(fileno, fcntl.LOCK_UN)
        fcntl.flock(self.f, fcntl.LOCK_SH | fcntl.LOCK_NB)
        fcntl.flock(self.f, fcntl.LOCK_UN)
        fcntl.flock(fileno, fcntl.LOCK_EX)
        fcntl.flock(fileno, fcntl.LOCK_UN)

        self.assertRaises(ValueError, fcntl.flock, -1, fcntl.LOCK_SH)
        self.assertRaises(TypeError, fcntl.flock, 'spam', fcntl.LOCK_SH)

    @cpython_only
    def test_flock_overflow(self):
        zaimportuj _testcapi
        self.assertRaises(OverflowError, fcntl.flock, _testcapi.INT_MAX+1,
                          fcntl.LOCK_SH)


def test_main():
    run_unittest(TestFcntl)

jeżeli __name__ == '__main__':
    test_main()
