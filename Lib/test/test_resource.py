zaimportuj contextlib
zaimportuj sys
zaimportuj os
zaimportuj unittest
z test zaimportuj support
zaimportuj time

resource = support.import_module('resource')

# This test jest checking a few specific problem spots przy the resource module.

klasa ResourceTest(unittest.TestCase):

    def test_args(self):
        self.assertRaises(TypeError, resource.getrlimit)
        self.assertRaises(TypeError, resource.getrlimit, 42, 42)
        self.assertRaises(TypeError, resource.setrlimit)
        self.assertRaises(TypeError, resource.setrlimit, 42, 42, 42)

    def test_fsize_ismax(self):
        spróbuj:
            (cur, max) = resource.getrlimit(resource.RLIMIT_FSIZE)
        wyjąwszy AttributeError:
            dalej
        inaczej:
            # RLIMIT_FSIZE should be RLIM_INFINITY, which will be a really big
            # number on a platform przy large file support.  On these platforms,
            # we need to test that the get/setrlimit functions properly convert
            # the number to a C long long oraz that the conversion doesn't podnieś
            # an error.
            self.assertEqual(resource.RLIM_INFINITY, max)
            resource.setrlimit(resource.RLIMIT_FSIZE, (cur, max))

    def test_fsize_enforced(self):
        spróbuj:
            (cur, max) = resource.getrlimit(resource.RLIMIT_FSIZE)
        wyjąwszy AttributeError:
            dalej
        inaczej:
            # Check to see what happens when the RLIMIT_FSIZE jest small.  Some
            # versions of Python were terminated by an uncaught SIGXFSZ, but
            # pythonrun.c has been fixed to ignore that exception.  If so, the
            # write() should zwróć EFBIG when the limit jest exceeded.

            # At least one platform has an unlimited RLIMIT_FSIZE oraz attempts
            # to change it podnieś ValueError instead.
            spróbuj:
                spróbuj:
                    resource.setrlimit(resource.RLIMIT_FSIZE, (1024, max))
                    limit_set = Prawda
                wyjąwszy ValueError:
                    limit_set = Nieprawda
                f = open(support.TESTFN, "wb")
                spróbuj:
                    f.write(b"X" * 1024)
                    spróbuj:
                        f.write(b"Y")
                        f.flush()
                        # On some systems (e.g., Ubuntu on hppa) the flush()
                        # doesn't always cause the exception, but the close()
                        # does eventually.  Try flushing several times w
                        # an attempt to ensure the file jest really synced oraz
                        # the exception podnieśd.
                        dla i w range(5):
                            time.sleep(.1)
                            f.flush()
                    wyjąwszy OSError:
                        jeżeli nie limit_set:
                            podnieś
                    jeżeli limit_set:
                        # Close will attempt to flush the byte we wrote
                        # Restore limit first to avoid getting a spurious error
                        resource.setrlimit(resource.RLIMIT_FSIZE, (cur, max))
                w_końcu:
                    f.close()
            w_końcu:
                jeżeli limit_set:
                    resource.setrlimit(resource.RLIMIT_FSIZE, (cur, max))
                support.unlink(support.TESTFN)

    def test_fsize_toobig(self):
        # Be sure that setrlimit jest checking dla really large values
        too_big = 10**50
        spróbuj:
            (cur, max) = resource.getrlimit(resource.RLIMIT_FSIZE)
        wyjąwszy AttributeError:
            dalej
        inaczej:
            spróbuj:
                resource.setrlimit(resource.RLIMIT_FSIZE, (too_big, max))
            wyjąwszy (OverflowError, ValueError):
                dalej
            spróbuj:
                resource.setrlimit(resource.RLIMIT_FSIZE, (max, too_big))
            wyjąwszy (OverflowError, ValueError):
                dalej

    def test_getrusage(self):
        self.assertRaises(TypeError, resource.getrusage)
        self.assertRaises(TypeError, resource.getrusage, 42, 42)
        usageself = resource.getrusage(resource.RUSAGE_SELF)
        usagechildren = resource.getrusage(resource.RUSAGE_CHILDREN)
        # May nie be available on all systems.
        spróbuj:
            usageboth = resource.getrusage(resource.RUSAGE_BOTH)
        wyjąwszy (ValueError, AttributeError):
            dalej
        spróbuj:
            usage_thread = resource.getrusage(resource.RUSAGE_THREAD)
        wyjąwszy (ValueError, AttributeError):
            dalej

    # Issue 6083: Reference counting bug
    def test_setrusage_refcount(self):
        spróbuj:
            limits = resource.getrlimit(resource.RLIMIT_CPU)
        wyjąwszy AttributeError:
            dalej
        inaczej:
            klasa BadSequence:
                def __len__(self):
                    zwróć 2
                def __getitem__(self, key):
                    jeżeli key w (0, 1):
                        zwróć len(tuple(range(1000000)))
                    podnieś IndexError

            resource.setrlimit(resource.RLIMIT_CPU, BadSequence())

    def test_pagesize(self):
        pagesize = resource.getpagesize()
        self.assertIsInstance(pagesize, int)
        self.assertGreaterEqual(pagesize, 0)

    @unittest.skipUnless(sys.platform == 'linux', 'test requires Linux')
    def test_linux_constants(self):
        dla attr w ['MSGQUEUE', 'NICE', 'RTPRIO', 'RTTIME', 'SIGPENDING']:
            przy contextlib.suppress(AttributeError):
                self.assertIsInstance(getattr(resource, 'RLIMIT_' + attr), int)

    @support.requires_freebsd_version(9)
    def test_freebsd_contants(self):
        dla attr w ['SWAP', 'SBSIZE', 'NPTS']:
            przy contextlib.suppress(AttributeError):
                self.assertIsInstance(getattr(resource, 'RLIMIT_' + attr), int)

    @unittest.skipUnless(hasattr(resource, 'prlimit'), 'no prlimit')
    @support.requires_linux_version(2, 6, 36)
    def test_prlimit(self):
        self.assertRaises(TypeError, resource.prlimit)
        jeżeli os.geteuid() != 0:
            self.assertRaises(PermissionError, resource.prlimit,
                              1, resource.RLIMIT_AS)
        self.assertRaises(ProcessLookupError, resource.prlimit,
                          -1, resource.RLIMIT_AS)
        limit = resource.getrlimit(resource.RLIMIT_AS)
        self.assertEqual(resource.prlimit(0, resource.RLIMIT_AS), limit)
        self.assertEqual(resource.prlimit(0, resource.RLIMIT_AS, limit),
                         limit)


def test_main(verbose=Nic):
    support.run_unittest(ResourceTest)

jeżeli __name__ == "__main__":
    test_main()
