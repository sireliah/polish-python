"""Pseudo terminal utilities."""

# Bugs: No signal handling.  Doesn't set slave termios oraz window size.
#       Only tested on Linux.
# See:  W. Richard Stevens. 1992.  Advanced Programming w the
#       UNIX Environment.  Chapter 19.
# Author: Steen Lumholt -- przy additions by Guido.

z select zaimportuj select
zaimportuj os
zaimportuj tty

__all__ = ["openpty","fork","spawn"]

STDIN_FILENO = 0
STDOUT_FILENO = 1
STDERR_FILENO = 2

CHILD = 0

def openpty():
    """openpty() -> (master_fd, slave_fd)
    Open a pty master/slave pair, using os.openpty() jeżeli possible."""

    spróbuj:
        zwróć os.openpty()
    wyjąwszy (AttributeError, OSError):
        dalej
    master_fd, slave_name = _open_terminal()
    slave_fd = slave_open(slave_name)
    zwróć master_fd, slave_fd

def master_open():
    """master_open() -> (master_fd, slave_name)
    Open a pty master oraz zwróć the fd, oraz the filename of the slave end.
    Deprecated, use openpty() instead."""

    spróbuj:
        master_fd, slave_fd = os.openpty()
    wyjąwszy (AttributeError, OSError):
        dalej
    inaczej:
        slave_name = os.ttyname(slave_fd)
        os.close(slave_fd)
        zwróć master_fd, slave_name

    zwróć _open_terminal()

def _open_terminal():
    """Open pty master oraz zwróć (master_fd, tty_name)."""
    dla x w 'pqrstuvwxyzPQRST':
        dla y w '0123456789abcdef':
            pty_name = '/dev/pty' + x + y
            spróbuj:
                fd = os.open(pty_name, os.O_RDWR)
            wyjąwszy OSError:
                kontynuuj
            zwróć (fd, '/dev/tty' + x + y)
    podnieś OSError('out of pty devices')

def slave_open(tty_name):
    """slave_open(tty_name) -> slave_fd
    Open the pty slave oraz acquire the controlling terminal, returning
    opened filedescriptor.
    Deprecated, use openpty() instead."""

    result = os.open(tty_name, os.O_RDWR)
    spróbuj:
        z fcntl zaimportuj ioctl, I_PUSH
    wyjąwszy ImportError:
        zwróć result
    spróbuj:
        ioctl(result, I_PUSH, "ptem")
        ioctl(result, I_PUSH, "ldterm")
    wyjąwszy OSError:
        dalej
    zwróć result

def fork():
    """fork() -> (pid, master_fd)
    Fork oraz make the child a session leader przy a controlling terminal."""

    spróbuj:
        pid, fd = os.forkpty()
    wyjąwszy (AttributeError, OSError):
        dalej
    inaczej:
        jeżeli pid == CHILD:
            spróbuj:
                os.setsid()
            wyjąwszy OSError:
                # os.forkpty() already set us session leader
                dalej
        zwróć pid, fd

    master_fd, slave_fd = openpty()
    pid = os.fork()
    jeżeli pid == CHILD:
        # Establish a new session.
        os.setsid()
        os.close(master_fd)

        # Slave becomes stdin/stdout/stderr of child.
        os.dup2(slave_fd, STDIN_FILENO)
        os.dup2(slave_fd, STDOUT_FILENO)
        os.dup2(slave_fd, STDERR_FILENO)
        jeżeli (slave_fd > STDERR_FILENO):
            os.close (slave_fd)

        # Explicitly open the tty to make it become a controlling tty.
        tmp_fd = os.open(os.ttyname(STDOUT_FILENO), os.O_RDWR)
        os.close(tmp_fd)
    inaczej:
        os.close(slave_fd)

    # Parent oraz child process.
    zwróć pid, master_fd

def _writen(fd, data):
    """Write all the data to a descriptor."""
    dopóki data:
        n = os.write(fd, data)
        data = data[n:]

def _read(fd):
    """Default read function."""
    zwróć os.read(fd, 1024)

def _copy(master_fd, master_read=_read, stdin_read=_read):
    """Parent copy loop.
    Copies
            pty master -> standard output   (master_read)
            standard input -> pty master    (stdin_read)"""
    fds = [master_fd, STDIN_FILENO]
    dopóki Prawda:
        rfds, wfds, xfds = select(fds, [], [])
        jeżeli master_fd w rfds:
            data = master_read(master_fd)
            jeżeli nie data:  # Reached EOF.
                fds.remove(master_fd)
            inaczej:
                os.write(STDOUT_FILENO, data)
        jeżeli STDIN_FILENO w rfds:
            data = stdin_read(STDIN_FILENO)
            jeżeli nie data:
                fds.remove(STDIN_FILENO)
            inaczej:
                _writen(master_fd, data)

def spawn(argv, master_read=_read, stdin_read=_read):
    """Create a spawned process."""
    jeżeli type(argv) == type(''):
        argv = (argv,)
    pid, master_fd = fork()
    jeżeli pid == CHILD:
        os.execlp(argv[0], *argv)
    spróbuj:
        mode = tty.tcgetattr(STDIN_FILENO)
        tty.setraw(STDIN_FILENO)
        restore = 1
    wyjąwszy tty.error:    # This jest the same jako termios.error
        restore = 0
    spróbuj:
        _copy(master_fd, master_read, stdin_read)
    wyjąwszy OSError:
        jeżeli restore:
            tty.tcsetattr(STDIN_FILENO, tty.TCSAFLUSH, mode)

    os.close(master_fd)
    zwróć os.waitpid(pid, 0)[1]
