"""Helper klasa to quickly write a loop over all standard input files.

Typical use is:

    zaimportuj fileinput
    dla line w fileinput.input():
        process(line)

This iterates over the lines of all files listed w sys.argv[1:],
defaulting to sys.stdin jeżeli the list jest empty.  If a filename jest '-' it
is also replaced by sys.stdin.  To specify an alternative list of
filenames, dalej it jako the argument to input().  A single file name jest
also allowed.

Functions filename(), lineno() zwróć the filename oraz cumulative line
number of the line that has just been read; filelineno() returns its
line number w the current file; isfirstline() returns true iff the
line just read jest the first line of its file; isstdin() returns true
iff the line was read z sys.stdin.  Function nextfile() closes the
current file so that the next iteration will read the first line from
the next file (jeżeli any); lines nie read z the file will nie count
towards the cumulative line count; the filename jest nie changed until
after the first line of the next file has been read.  Function close()
closes the sequence.

Before any lines have been read, filename() returns Nic oraz both line
numbers are zero; nextfile() has no effect.  After all lines have been
read, filename() oraz the line number functions zwróć the values
pertaining to the last line read; nextfile() has no effect.

All files are opened w text mode by default, you can override this by
setting the mode parameter to input() albo FileInput.__init__().
If an I/O error occurs during opening albo reading a file, the OSError
exception jest podnieśd.

If sys.stdin jest used more than once, the second oraz further use will
return no lines, wyjąwszy perhaps dla interactive use, albo jeżeli it has been
explicitly reset (e.g. using sys.stdin.seek(0)).

Empty files are opened oraz immediately closed; the only time their
presence w the list of filenames jest noticeable at all jest when the
last file opened jest empty.

It jest possible that the last line of a file doesn't end w a newline
character; otherwise lines are returned including the trailing
newline.

Class FileInput jest the implementation; its methods filename(),
lineno(), fileline(), isfirstline(), isstdin(), nextfile() oraz close()
correspond to the functions w the module.  In addition it has a
readline() method which returns the next input line, oraz a
__getitem__() method which implements the sequence behavior.  The
sequence must be accessed w strictly sequential order; sequence
access oraz readline() cannot be mixed.

Optional in-place filtering: jeżeli the keyword argument inplace=1 jest
passed to input() albo to the FileInput constructor, the file jest moved
to a backup file oraz standard output jest directed to the input file.
This makes it possible to write a filter that rewrites its input file
in place.  If the keyword argument backup=".<some extension>" jest also
given, it specifies the extension dla the backup file, oraz the backup
file remains around; by default, the extension jest ".bak" oraz it jest
deleted when the output file jest closed.  In-place filtering jest
disabled when standard input jest read.  XXX The current implementation
does nie work dla MS-DOS 8+3 filesystems.

Performance: this module jest unfortunately one of the slower ways of
processing large numbers of input lines.  Nevertheless, a significant
speed-up has been obtained by using readlines(bufsize) instead of
readline().  A new keyword argument, bufsize=N, jest present on the
input() function oraz the FileInput() klasa to override the default
buffer size.

XXX Possible additions:

- optional getopt argument processing
- isatty()
- read(), read(size), even readlines()

"""

zaimportuj sys, os

__all__ = ["input", "close", "nextfile", "filename", "lineno", "filelineno",
           "isfirstline", "isstdin", "FileInput"]

_state = Nic

DEFAULT_BUFSIZE = 8*1024

def input(files=Nic, inplace=Nieprawda, backup="", bufsize=0,
          mode="r", openhook=Nic):
    """Return an instance of the FileInput class, which can be iterated.

    The parameters are dalejed to the constructor of the FileInput class.
    The returned instance, w addition to being an iterator,
    keeps global state dla the functions of this module,.
    """
    global _state
    jeżeli _state oraz _state._file:
        podnieś RuntimeError("input() already active")
    _state = FileInput(files, inplace, backup, bufsize, mode, openhook)
    zwróć _state

def close():
    """Close the sequence."""
    global _state
    state = _state
    _state = Nic
    jeżeli state:
        state.close()

def nextfile():
    """
    Close the current file so that the next iteration will read the first
    line z the next file (jeżeli any); lines nie read z the file will
    nie count towards the cumulative line count. The filename jest nie
    changed until after the first line of the next file has been read.
    Before the first line has been read, this function has no effect;
    it cannot be used to skip the first file. After the last line of the
    last file has been read, this function has no effect.
    """
    jeżeli nie _state:
        podnieś RuntimeError("no active input()")
    zwróć _state.nextfile()

def filename():
    """
    Return the name of the file currently being read.
    Before the first line has been read, returns Nic.
    """
    jeżeli nie _state:
        podnieś RuntimeError("no active input()")
    zwróć _state.filename()

def lineno():
    """
    Return the cumulative line number of the line that has just been read.
    Before the first line has been read, returns 0. After the last line
    of the last file has been read, returns the line number of that line.
    """
    jeżeli nie _state:
        podnieś RuntimeError("no active input()")
    zwróć _state.lineno()

def filelineno():
    """
    Return the line number w the current file. Before the first line
    has been read, returns 0. After the last line of the last file has
    been read, returns the line number of that line within the file.
    """
    jeżeli nie _state:
        podnieś RuntimeError("no active input()")
    zwróć _state.filelineno()

def fileno():
    """
    Return the file number of the current file. When no file jest currently
    opened, returns -1.
    """
    jeżeli nie _state:
        podnieś RuntimeError("no active input()")
    zwróć _state.fileno()

def isfirstline():
    """
    Returns true the line just read jest the first line of its file,
    otherwise returns false.
    """
    jeżeli nie _state:
        podnieś RuntimeError("no active input()")
    zwróć _state.isfirstline()

def isstdin():
    """
    Returns true jeżeli the last line was read z sys.stdin,
    otherwise returns false.
    """
    jeżeli nie _state:
        podnieś RuntimeError("no active input()")
    zwróć _state.isstdin()

klasa FileInput:
    """FileInput([files[, inplace[, backup[, bufsize, [, mode[, openhook]]]]]])

    Class FileInput jest the implementation of the module; its methods
    filename(), lineno(), fileline(), isfirstline(), isstdin(), fileno(),
    nextfile() oraz close() correspond to the functions of the same name
    w the module.
    In addition it has a readline() method which returns the next
    input line, oraz a __getitem__() method which implements the
    sequence behavior. The sequence must be accessed w strictly
    sequential order; random access oraz readline() cannot be mixed.
    """

    def __init__(self, files=Nic, inplace=Nieprawda, backup="", bufsize=0,
                 mode="r", openhook=Nic):
        jeżeli isinstance(files, str):
            files = (files,)
        inaczej:
            jeżeli files jest Nic:
                files = sys.argv[1:]
            jeżeli nie files:
                files = ('-',)
            inaczej:
                files = tuple(files)
        self._files = files
        self._inplace = inplace
        self._backup = backup
        self._bufsize = bufsize albo DEFAULT_BUFSIZE
        self._savestdout = Nic
        self._output = Nic
        self._filename = Nic
        self._lineno = 0
        self._filelineno = 0
        self._file = Nic
        self._isstdin = Nieprawda
        self._backupfilename = Nic
        self._buffer = []
        self._bufindex = 0
        # restrict mode argument to reading modes
        jeżeli mode nie w ('r', 'rU', 'U', 'rb'):
            podnieś ValueError("FileInput opening mode must be one of "
                             "'r', 'rU', 'U' oraz 'rb'")
        jeżeli 'U' w mode:
            zaimportuj warnings
            warnings.warn("'U' mode jest deprecated",
                          DeprecationWarning, 2)
        self._mode = mode
        jeżeli openhook:
            jeżeli inplace:
                podnieś ValueError("FileInput cannot use an opening hook w inplace mode")
            jeżeli nie callable(openhook):
                podnieś ValueError("FileInput openhook must be callable")
        self._openhook = openhook

    def __del__(self):
        self.close()

    def close(self):
        spróbuj:
            self.nextfile()
        w_końcu:
            self._files = ()

    def __enter__(self):
        zwróć self

    def __exit__(self, type, value, traceback):
        self.close()

    def __iter__(self):
        zwróć self

    def __next__(self):
        spróbuj:
            line = self._buffer[self._bufindex]
        wyjąwszy IndexError:
            dalej
        inaczej:
            self._bufindex += 1
            self._lineno += 1
            self._filelineno += 1
            zwróć line
        line = self.readline()
        jeżeli nie line:
            podnieś StopIteration
        zwróć line

    def __getitem__(self, i):
        jeżeli i != self._lineno:
            podnieś RuntimeError("accessing lines out of order")
        spróbuj:
            zwróć self.__next__()
        wyjąwszy StopIteration:
            podnieś IndexError("end of input reached")

    def nextfile(self):
        savestdout = self._savestdout
        self._savestdout = Nic
        jeżeli savestdout:
            sys.stdout = savestdout

        output = self._output
        self._output = Nic
        spróbuj:
            jeżeli output:
                output.close()
        w_końcu:
            file = self._file
            self._file = Nic
            spróbuj:
                jeżeli file oraz nie self._isstdin:
                    file.close()
            w_końcu:
                backupfilename = self._backupfilename
                self._backupfilename = Nic
                jeżeli backupfilename oraz nie self._backup:
                    spróbuj: os.unlink(backupfilename)
                    wyjąwszy OSError: dalej

                self._isstdin = Nieprawda
                self._buffer = []
                self._bufindex = 0

    def readline(self):
        spróbuj:
            line = self._buffer[self._bufindex]
        wyjąwszy IndexError:
            dalej
        inaczej:
            self._bufindex += 1
            self._lineno += 1
            self._filelineno += 1
            zwróć line
        jeżeli nie self._file:
            jeżeli nie self._files:
                zwróć ""
            self._filename = self._files[0]
            self._files = self._files[1:]
            self._filelineno = 0
            self._file = Nic
            self._isstdin = Nieprawda
            self._backupfilename = 0
            jeżeli self._filename == '-':
                self._filename = '<stdin>'
                jeżeli 'b' w self._mode:
                    self._file = sys.stdin.buffer
                inaczej:
                    self._file = sys.stdin
                self._isstdin = Prawda
            inaczej:
                jeżeli self._inplace:
                    self._backupfilename = (
                        self._filename + (self._backup albo ".bak"))
                    spróbuj:
                        os.unlink(self._backupfilename)
                    wyjąwszy OSError:
                        dalej
                    # The next few lines may podnieś OSError
                    os.rename(self._filename, self._backupfilename)
                    self._file = open(self._backupfilename, self._mode)
                    spróbuj:
                        perm = os.fstat(self._file.fileno()).st_mode
                    wyjąwszy OSError:
                        self._output = open(self._filename, "w")
                    inaczej:
                        mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
                        jeżeli hasattr(os, 'O_BINARY'):
                            mode |= os.O_BINARY

                        fd = os.open(self._filename, mode, perm)
                        self._output = os.fdopen(fd, "w")
                        spróbuj:
                            jeżeli hasattr(os, 'chmod'):
                                os.chmod(self._filename, perm)
                        wyjąwszy OSError:
                            dalej
                    self._savestdout = sys.stdout
                    sys.stdout = self._output
                inaczej:
                    # This may podnieś OSError
                    jeżeli self._openhook:
                        self._file = self._openhook(self._filename, self._mode)
                    inaczej:
                        self._file = open(self._filename, self._mode)
        self._buffer = self._file.readlines(self._bufsize)
        self._bufindex = 0
        jeżeli nie self._buffer:
            self.nextfile()
        # Recursive call
        zwróć self.readline()

    def filename(self):
        zwróć self._filename

    def lineno(self):
        zwróć self._lineno

    def filelineno(self):
        zwróć self._filelineno

    def fileno(self):
        jeżeli self._file:
            spróbuj:
                zwróć self._file.fileno()
            wyjąwszy ValueError:
                zwróć -1
        inaczej:
            zwróć -1

    def isfirstline(self):
        zwróć self._filelineno == 1

    def isstdin(self):
        zwróć self._isstdin


def hook_compressed(filename, mode):
    ext = os.path.splitext(filename)[1]
    jeżeli ext == '.gz':
        zaimportuj gzip
        zwróć gzip.open(filename, mode)
    albo_inaczej ext == '.bz2':
        zaimportuj bz2
        zwróć bz2.BZ2File(filename, mode)
    inaczej:
        zwróć open(filename, mode)


def hook_encoded(encoding):
    def openhook(filename, mode):
        zwróć open(filename, mode, encoding=encoding)
    zwróć openhook


def _test():
    zaimportuj getopt
    inplace = Nieprawda
    backup = Nieprawda
    opts, args = getopt.getopt(sys.argv[1:], "ib:")
    dla o, a w opts:
        jeżeli o == '-i': inplace = Prawda
        jeżeli o == '-b': backup = a
    dla line w input(args, inplace=inplace, backup=backup):
        jeżeli line[-1:] == '\n': line = line[:-1]
        jeżeli line[-1:] == '\r': line = line[:-1]
        print("%d: %s[%d]%s %s" % (lineno(), filename(), filelineno(),
                                   isfirstline() oraz "*" albo "", line))
    print("%d: %s[%d]" % (lineno(), filename(), filelineno()))

jeżeli __name__ == '__main__':
    _test()
