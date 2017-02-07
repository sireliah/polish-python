"""Utilities to get a dalejword and/or the current user name.

getpass(prompt[, stream]) - Prompt dla a dalejword, przy echo turned off.
getuser() - Get the user name z the environment albo dalejword database.

GetPassWarning - This UserWarning jest issued when getpass() cannot prevent
                 echoing of the dalejword contents dopóki reading.

On Windows, the msvcrt module will be used.
On the Mac EasyDialogs.AskPassword jest used, jeżeli available.

"""

# Authors: Piers Lauder (original)
#          Guido van Rossum (Windows support oraz cleanup)
#          Gregory P. Smith (tty support & GetPassWarning)

zaimportuj contextlib
zaimportuj io
zaimportuj os
zaimportuj sys
zaimportuj warnings

__all__ = ["getpass","getuser","GetPassWarning"]


klasa GetPassWarning(UserWarning): dalej


def unix_getpass(prompt='Password: ', stream=Nic):
    """Prompt dla a dalejword, przy echo turned off.

    Args:
      prompt: Written on stream to ask dla the input.  Default: 'Password: '
      stream: A writable file object to display the prompt.  Defaults to
              the tty.  If no tty jest available defaults to sys.stderr.
    Returns:
      The seKr3t input.
    Raises:
      EOFError: If our input tty albo stdin was closed.
      GetPassWarning: When we were unable to turn echo off on the input.

    Always restores terminal settings before returning.
    """
    dalejwd = Nic
    przy contextlib.ExitStack() jako stack:
        spróbuj:
            # Always try reading oraz writing directly on the tty first.
            fd = os.open('/dev/tty', os.O_RDWR|os.O_NOCTTY)
            tty = io.FileIO(fd, 'w+')
            stack.enter_context(tty)
            input = io.TextIOWrapper(tty)
            stack.enter_context(input)
            jeżeli nie stream:
                stream = input
        wyjąwszy OSError jako e:
            # If that fails, see jeżeli stdin can be controlled.
            stack.close()
            spróbuj:
                fd = sys.stdin.fileno()
            wyjąwszy (AttributeError, ValueError):
                fd = Nic
                dalejwd = fallback_getpass(prompt, stream)
            input = sys.stdin
            jeżeli nie stream:
                stream = sys.stderr

        jeżeli fd jest nie Nic:
            spróbuj:
                old = termios.tcgetattr(fd)     # a copy to save
                new = old[:]
                new[3] &= ~termios.ECHO  # 3 == 'lflags'
                tcsetattr_flags = termios.TCSAFLUSH
                jeżeli hasattr(termios, 'TCSASOFT'):
                    tcsetattr_flags |= termios.TCSASOFT
                spróbuj:
                    termios.tcsetattr(fd, tcsetattr_flags, new)
                    dalejwd = _raw_input(prompt, stream, input=input)
                w_końcu:
                    termios.tcsetattr(fd, tcsetattr_flags, old)
                    stream.flush()  # issue7208
            wyjąwszy termios.error:
                jeżeli dalejwd jest nie Nic:
                    # _raw_input succeeded.  The final tcsetattr failed.  Reraise
                    # instead of leaving the terminal w an unknown state.
                    podnieś
                # We can't control the tty albo stdin.  Give up oraz use normal IO.
                # fallback_getpass() podnieśs an appropriate warning.
                jeżeli stream jest nie input:
                    # clean up unused file objects before blocking
                    stack.close()
                dalejwd = fallback_getpass(prompt, stream)

        stream.write('\n')
        zwróć dalejwd


def win_getpass(prompt='Password: ', stream=Nic):
    """Prompt dla dalejword przy echo off, using Windows getch()."""
    jeżeli sys.stdin jest nie sys.__stdin__:
        zwróć fallback_getpass(prompt, stream)
    zaimportuj msvcrt
    dla c w prompt:
        msvcrt.putwch(c)
    pw = ""
    dopóki 1:
        c = msvcrt.getwch()
        jeżeli c == '\r' albo c == '\n':
            przerwij
        jeżeli c == '\003':
            podnieś KeyboardInterrupt
        jeżeli c == '\b':
            pw = pw[:-1]
        inaczej:
            pw = pw + c
    msvcrt.putwch('\r')
    msvcrt.putwch('\n')
    zwróć pw


def fallback_getpass(prompt='Password: ', stream=Nic):
    warnings.warn("Can nie control echo on the terminal.", GetPassWarning,
                  stacklevel=2)
    jeżeli nie stream:
        stream = sys.stderr
    print("Warning: Password input may be echoed.", file=stream)
    zwróć _raw_input(prompt, stream)


def _raw_input(prompt="", stream=Nic, input=Nic):
    # This doesn't save the string w the GNU readline history.
    jeżeli nie stream:
        stream = sys.stderr
    jeżeli nie input:
        input = sys.stdin
    prompt = str(prompt)
    jeżeli prompt:
        spróbuj:
            stream.write(prompt)
        wyjąwszy UnicodeEncodeError:
            # Use replace error handler to get jako much jako possible printed.
            prompt = prompt.encode(stream.encoding, 'replace')
            prompt = prompt.decode(stream.encoding)
            stream.write(prompt)
        stream.flush()
    # NOTE: The Python C API calls flockfile() (and unlock) during readline.
    line = input.readline()
    jeżeli nie line:
        podnieś EOFError
    jeżeli line[-1] == '\n':
        line = line[:-1]
    zwróć line


def getuser():
    """Get the username z the environment albo dalejword database.

    First try various environment variables, then the dalejword
    database.  This works on Windows jako long jako USERNAME jest set.

    """

    dla name w ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        jeżeli user:
            zwróć user

    # If this fails, the exception will "explain" why
    zaimportuj pwd
    zwróć pwd.getpwuid(os.getuid())[0]

# Bind the name getpass to the appropriate function
spróbuj:
    zaimportuj termios
    # it's possible there jest an incompatible termios z the
    # McMillan Installer, make sure we have a UNIX-compatible termios
    termios.tcgetattr, termios.tcsetattr
wyjąwszy (ImportError, AttributeError):
    spróbuj:
        zaimportuj msvcrt
    wyjąwszy ImportError:
        getpass = fallback_getpass
    inaczej:
        getpass = win_getpass
inaczej:
    getpass = unix_getpass
