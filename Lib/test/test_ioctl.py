zaimportuj array
zaimportuj unittest
z test.support zaimportuj import_module, get_attribute
zaimportuj os, struct
fcntl = import_module('fcntl')
termios = import_module('termios')
get_attribute(termios, 'TIOCGPGRP') #Can't run tests without this feature

spróbuj:
    tty = open("/dev/tty", "rb")
wyjąwszy OSError:
    podnieś unittest.SkipTest("Unable to open /dev/tty")
inaczej:
    # Skip jeżeli another process jest w foreground
    r = fcntl.ioctl(tty, termios.TIOCGPGRP, "    ")
    tty.close()
    rpgrp = struct.unpack("i", r)[0]
    jeżeli rpgrp nie w (os.getpgrp(), os.getsid(0)):
        podnieś unittest.SkipTest("Neither the process group nor the session "
                                "are attached to /dev/tty")
    usuń tty, r, rpgrp

spróbuj:
    zaimportuj pty
wyjąwszy ImportError:
    pty = Nic

klasa IoctlTests(unittest.TestCase):
    def test_ioctl(self):
        # If this process has been put into the background, TIOCGPGRP returns
        # the session ID instead of the process group id.
        ids = (os.getpgrp(), os.getsid(0))
        przy open("/dev/tty", "rb") jako tty:
            r = fcntl.ioctl(tty, termios.TIOCGPGRP, "    ")
            rpgrp = struct.unpack("i", r)[0]
            self.assertIn(rpgrp, ids)

    def _check_ioctl_mutate_len(self, nbytes=Nic):
        buf = array.array('i')
        intsize = buf.itemsize
        ids = (os.getpgrp(), os.getsid(0))
        # A fill value unlikely to be w `ids`
        fill = -12345
        jeżeli nbytes jest nie Nic:
            # Extend the buffer so that it jest exactly `nbytes` bytes long
            buf.extend([fill] * (nbytes // intsize))
            self.assertEqual(len(buf) * intsize, nbytes)   # sanity check
        inaczej:
            buf.append(fill)
        przy open("/dev/tty", "rb") jako tty:
            r = fcntl.ioctl(tty, termios.TIOCGPGRP, buf, 1)
        rpgrp = buf[0]
        self.assertEqual(r, 0)
        self.assertIn(rpgrp, ids)

    def test_ioctl_mutate(self):
        self._check_ioctl_mutate_len()

    def test_ioctl_mutate_1024(self):
        # Issue #9758: a mutable buffer of exactly 1024 bytes wouldn't be
        # copied back after the system call.
        self._check_ioctl_mutate_len(1024)

    def test_ioctl_mutate_2048(self):
        # Test przy a larger buffer, just dla the record.
        self._check_ioctl_mutate_len(2048)

    def test_ioctl_signed_unsigned_code_param(self):
        jeżeli nie pty:
            podnieś unittest.SkipTest('pty module required')
        mfd, sfd = pty.openpty()
        spróbuj:
            jeżeli termios.TIOCSWINSZ < 0:
                set_winsz_opcode_maybe_neg = termios.TIOCSWINSZ
                set_winsz_opcode_pos = termios.TIOCSWINSZ & 0xffffffff
            inaczej:
                set_winsz_opcode_pos = termios.TIOCSWINSZ
                set_winsz_opcode_maybe_neg, = struct.unpack("i",
                        struct.pack("I", termios.TIOCSWINSZ))

            our_winsz = struct.pack("HHHH",80,25,0,0)
            # test both przy a positive oraz potentially negative ioctl code
            new_winsz = fcntl.ioctl(mfd, set_winsz_opcode_pos, our_winsz)
            new_winsz = fcntl.ioctl(mfd, set_winsz_opcode_maybe_neg, our_winsz)
        w_końcu:
            os.close(mfd)
            os.close(sfd)


jeżeli __name__ == "__main__":
    unittest.main()
