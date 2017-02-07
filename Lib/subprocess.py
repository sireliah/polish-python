# subprocess - Subprocesses przy accessible I/O streams
#
# For more information about this module, see PEP 324.
#
# Copyright (c) 2003-2005 by Peter Astrand <astrand@lysator.liu.se>
#
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/2.4/license dla licensing details.

r"""subprocess - Subprocesses przy accessible I/O streams

This module allows you to spawn processes, connect to their
input/output/error pipes, oraz obtain their zwróć codes.  This module
intends to replace several older modules oraz functions:

os.system
os.spawn*

Information about how the subprocess module can be used to replace these
modules oraz functions can be found below.



Using the subprocess module
===========================
This module defines one klasa called Popen:

klasa Popen(args, bufsize=-1, executable=Nic,
            stdin=Nic, stdout=Nic, stderr=Nic,
            preexec_fn=Nic, close_fds=Prawda, shell=Nieprawda,
            cwd=Nic, env=Nic, universal_newlines=Nieprawda,
            startupinfo=Nic, creationflags=0,
            restore_signals=Prawda, start_new_session=Nieprawda, dalej_fds=()):


Arguments are:

args should be a string, albo a sequence of program arguments.  The
program to execute jest normally the first item w the args sequence albo
string, but can be explicitly set by using the executable argument.

On POSIX, przy shell=Nieprawda (default): In this case, the Popen class
uses os.execvp() to execute the child program.  args should normally
be a sequence.  A string will be treated jako a sequence przy the string
as the only item (the program to execute).

On POSIX, przy shell=Prawda: If args jest a string, it specifies the
command string to execute through the shell.  If args jest a sequence,
the first item specifies the command string, oraz any additional items
will be treated jako additional shell arguments.

On Windows: the Popen klasa uses CreateProcess() to execute the child
program, which operates on strings.  If args jest a sequence, it will be
converted to a string using the list2cmdline method.  Please note that
not all MS Windows applications interpret the command line the same
way: The list2cmdline jest designed dla applications using the same
rules jako the MS C runtime.

bufsize will be supplied jako the corresponding argument to the io.open()
function when creating the stdin/stdout/stderr pipe file objects:
0 means unbuffered (read & write are one system call oraz can zwróć short),
1 means line buffered, any other positive value means use a buffer of
approximately that size.  A negative bufsize, the default, means the system
default of io.DEFAULT_BUFFER_SIZE will be used.

stdin, stdout oraz stderr specify the executed programs' standard
input, standard output oraz standard error file handles, respectively.
Valid values are PIPE, an existing file descriptor (a positive
integer), an existing file object, oraz Nic.  PIPE indicates that a
new pipe to the child should be created.  With Nic, no redirection
will occur; the child's file handles will be inherited z the
parent.  Additionally, stderr can be STDOUT, which indicates that the
stderr data z the applications should be captured into the same
file handle jako dla stdout.

On POSIX, jeżeli preexec_fn jest set to a callable object, this object will be
called w the child process just before the child jest executed.  The use
of preexec_fn jest nie thread safe, using it w the presence of threads
could lead to a deadlock w the child process before the new executable
is executed.

If close_fds jest true, all file descriptors wyjąwszy 0, 1 oraz 2 will be
closed before the child process jest executed.  The default dla close_fds
varies by platform:  Always true on POSIX.  Prawda when stdin/stdout/stderr
are Nic on Windows, false otherwise.

pass_fds jest an optional sequence of file descriptors to keep open between the
parent oraz child.  Providing any dalej_fds implicitly sets close_fds to true.

jeżeli shell jest true, the specified command will be executed through the
shell.

If cwd jest nie Nic, the current directory will be changed to cwd
before the child jest executed.

On POSIX, jeżeli restore_signals jest Prawda all signals that Python sets to
SIG_IGN are restored to SIG_DFL w the child process before the exec.
Currently this includes the SIGPIPE, SIGXFZ oraz SIGXFSZ signals.  This
parameter does nothing on Windows.

On POSIX, jeżeli start_new_session jest Prawda, the setsid() system call will be made
in the child process prior to executing the command.

If env jest nie Nic, it defines the environment variables dla the new
process.

If universal_newlines jest Nieprawda, the file objects stdin, stdout oraz stderr
are opened jako binary files, oraz no line ending conversion jest done.

If universal_newlines jest Prawda, the file objects stdout oraz stderr are
opened jako a text file, but lines may be terminated by any of '\n',
the Unix end-of-line convention, '\r', the old Macintosh convention albo
'\r\n', the Windows convention.  All of these external representations
are seen jako '\n' by the Python program.  Also, the newlines attribute
of the file objects stdout, stdin oraz stderr are nie updated by the
communicate() method.

In either case, the process being communicated przy should start up
expecting to receive bytes on its standard input oraz decode them with
the same encoding they are sent in.

The startupinfo oraz creationflags, jeżeli given, will be dalejed to the
underlying CreateProcess() function.  They can specify things such as
appearance of the main window oraz priority dla the new process.
(Windows only)


This module also defines some shortcut functions:

call(*popenargs, **kwargs):
    Run command przy arguments.  Wait dla command to complete, then
    zwróć the returncode attribute.

    The arguments are the same jako dla the Popen constructor.  Example:

    >>> retcode = subprocess.call(["ls", "-l"])

check_call(*popenargs, **kwargs):
    Run command przy arguments.  Wait dla command to complete.  If the
    exit code was zero then return, otherwise podnieś
    CalledProcessError.  The CalledProcessError object will have the
    zwróć code w the returncode attribute.

    The arguments are the same jako dla the Popen constructor.  Example:

    >>> subprocess.check_call(["ls", "-l"])
    0

getstatusoutput(cmd):
    Return (status, output) of executing cmd w a shell.

    Execute the string 'cmd' w a shell przy 'check_output' oraz
    zwróć a 2-tuple (status, output). Universal newlines mode jest used,
    meaning that the result przy be decoded to a string.

    A trailing newline jest stripped z the output.
    The exit status dla the command can be interpreted
    according to the rules dla the function 'wait'.  Example:

    >>> subprocess.getstatusoutput('ls /bin/ls')
    (0, '/bin/ls')
    >>> subprocess.getstatusoutput('cat /bin/junk')
    (256, 'cat: /bin/junk: No such file albo directory')
    >>> subprocess.getstatusoutput('/bin/junk')
    (256, 'sh: /bin/junk: nie found')

getoutput(cmd):
    Return output (stdout albo stderr) of executing cmd w a shell.

    Like getstatusoutput(), wyjąwszy the exit status jest ignored oraz the zwróć
    value jest a string containing the command's output.  Example:

    >>> subprocess.getoutput('ls /bin/ls')
    '/bin/ls'

check_output(*popenargs, **kwargs):
    Run command przy arguments oraz zwróć its output.

    If the exit code was non-zero it podnieśs a CalledProcessError.  The
    CalledProcessError object will have the zwróć code w the returncode
    attribute oraz output w the output attribute.

    The arguments are the same jako dla the Popen constructor.  Example:

    >>> output = subprocess.check_output(["ls", "-l", "/dev/null"])

    There jest an additional optional argument, "input", allowing you to
    dalej a string to the subprocess's stdin.  If you use this argument
    you may nie also use the Popen constructor's "stdin" argument.

    If universal_newlines jest set to Prawda, the "input" argument must
    be a string rather than bytes, oraz the zwróć value will be a string.

Exceptions
----------
Exceptions podnieśd w the child process, before the new program has
started to execute, will be re-raised w the parent.  Additionally,
the exception object will have one extra attribute called
'child_traceback', which jest a string containing traceback information
z the child's point of view.

The most common exception podnieśd jest OSError.  This occurs, for
example, when trying to execute a non-existent file.  Applications
should prepare dla OSErrors.

A ValueError will be podnieśd jeżeli Popen jest called przy invalid arguments.

Exceptions defined within this module inherit z SubprocessError.
check_call() oraz check_output() will podnieś CalledProcessError jeżeli the
called process returns a non-zero zwróć code.  TimeoutExpired
be podnieśd jeżeli a timeout was specified oraz expired.


Security
--------
Unlike some other popen functions, this implementation will never call
/bin/sh implicitly.  This means that all characters, including shell
metacharacters, can safely be dalejed to child processes.


Popen objects
=============
Instances of the Popen klasa have the following methods:

poll()
    Check jeżeli child process has terminated.  Returns returncode
    attribute.

wait()
    Wait dla child process to terminate.  Returns returncode attribute.

communicate(input=Nic)
    Interact przy process: Send data to stdin.  Read data z stdout
    oraz stderr, until end-of-file jest reached.  Wait dla process to
    terminate.  The optional input argument should be data to be
    sent to the child process, albo Nic, jeżeli no data should be sent to
    the child. If the Popen instance was constructed przy universal_newlines
    set to Prawda, the input argument should be a string oraz will be encoded
    using the preferred system encoding (see locale.getpreferredencoding);
    jeżeli universal_newlines jest Nieprawda, the input argument should be a
    byte string.

    communicate() returns a tuple (stdout, stderr).

    Note: The data read jest buffered w memory, so do nie use this
    method jeżeli the data size jest large albo unlimited.

The following attributes are also available:

stdin
    If the stdin argument jest PIPE, this attribute jest a file object
    that provides input to the child process.  Otherwise, it jest Nic.

stdout
    If the stdout argument jest PIPE, this attribute jest a file object
    that provides output z the child process.  Otherwise, it jest
    Nic.

stderr
    If the stderr argument jest PIPE, this attribute jest file object that
    provides error output z the child process.  Otherwise, it jest
    Nic.

pid
    The process ID of the child process.

returncode
    The child zwróć code.  A Nic value indicates that the process
    hasn't terminated yet.  A negative value -N indicates that the
    child was terminated by signal N (POSIX only).


Replacing older functions przy the subprocess module
====================================================
In this section, "a ==> b" means that b can be used jako a replacement
dla a.

Note: All functions w this section fail (more albo less) silently if
the executed program cannot be found; this module podnieśs an OSError
exception.

In the following examples, we assume that the subprocess module jest
imported przy "z subprocess zaimportuj *".


Replacing /bin/sh shell backquote
---------------------------------
output=`mycmd myarg`
==>
output = Popen(["mycmd", "myarg"], stdout=PIPE).communicate()[0]


Replacing shell pipe line
-------------------------
output=`dmesg | grep hda`
==>
p1 = Popen(["dmesg"], stdout=PIPE)
p2 = Popen(["grep", "hda"], stdin=p1.stdout, stdout=PIPE)
output = p2.communicate()[0]


Replacing os.system()
---------------------
sts = os.system("mycmd" + " myarg")
==>
p = Popen("mycmd" + " myarg", shell=Prawda)
pid, sts = os.waitpid(p.pid, 0)

Note:

* Calling the program through the shell jest usually nie required.

* It's easier to look at the returncode attribute than the
  exitstatus.

A more real-world example would look like this:

spróbuj:
    retcode = call("mycmd" + " myarg", shell=Prawda)
    jeżeli retcode < 0:
        print("Child was terminated by signal", -retcode, file=sys.stderr)
    inaczej:
        print("Child returned", retcode, file=sys.stderr)
wyjąwszy OSError jako e:
    print("Execution failed:", e, file=sys.stderr)


Replacing os.spawn*
-------------------
P_NOWAIT example:

pid = os.spawnlp(os.P_NOWAIT, "/bin/mycmd", "mycmd", "myarg")
==>
pid = Popen(["/bin/mycmd", "myarg"]).pid


P_WAIT example:

retcode = os.spawnlp(os.P_WAIT, "/bin/mycmd", "mycmd", "myarg")
==>
retcode = call(["/bin/mycmd", "myarg"])


Vector example:

os.spawnvp(os.P_NOWAIT, path, args)
==>
Popen([path] + args[1:])


Environment example:

os.spawnlpe(os.P_NOWAIT, "/bin/mycmd", "mycmd", "myarg", env)
==>
Popen(["/bin/mycmd", "myarg"], env={"PATH": "/usr/bin"})
"""

zaimportuj sys
_mswindows = (sys.platform == "win32")

zaimportuj io
zaimportuj os
zaimportuj time
zaimportuj signal
zaimportuj builtins
zaimportuj warnings
zaimportuj errno
z time zaimportuj monotonic jako _time

# Exception classes used by this module.
klasa SubprocessError(Exception): dalej


klasa CalledProcessError(SubprocessError):
    """This exception jest podnieśd when a process run by check_call() albo
    check_output() returns a non-zero exit status.
    The exit status will be stored w the returncode attribute;
    check_output() will also store the output w the output attribute.
    """
    def __init__(self, returncode, cmd, output=Nic, stderr=Nic):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr

    def __str__(self):
        zwróć "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)

    @property
    def stdout(self):
        """Alias dla output attribute, to match stderr"""
        zwróć self.output

    @stdout.setter
    def stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout jest a transparent alias dla .output
        self.output = value


klasa TimeoutExpired(SubprocessError):
    """This exception jest podnieśd when the timeout expires dopóki waiting dla a
    child process.
    """
    def __init__(self, cmd, timeout, output=Nic, stderr=Nic):
        self.cmd = cmd
        self.timeout = timeout
        self.output = output
        self.stderr = stderr

    def __str__(self):
        zwróć ("Command '%s' timed out after %s seconds" %
                (self.cmd, self.timeout))

    @property
    def stdout(self):
        zwróć self.output

    @stdout.setter
    def stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout jest a transparent alias dla .output
        self.output = value


jeżeli _mswindows:
    zaimportuj threading
    zaimportuj msvcrt
    zaimportuj _winapi
    klasa STARTUPINFO:
        dwFlags = 0
        hStdInput = Nic
        hStdOutput = Nic
        hStdError = Nic
        wShowWindow = 0
inaczej:
    zaimportuj _posixsubprocess
    zaimportuj select
    zaimportuj selectors
    spróbuj:
        zaimportuj threading
    wyjąwszy ImportError:
        zaimportuj dummy_threading jako threading

    # When select albo poll has indicated that the file jest writable,
    # we can write up to _PIPE_BUF bytes without risk of blocking.
    # POSIX defines PIPE_BUF jako >= 512.
    _PIPE_BUF = getattr(select, 'PIPE_BUF', 512)

    # poll/select have the advantage of nie requiring any extra file
    # descriptor, contrarily to epoll/kqueue (also, they require a single
    # syscall).
    jeżeli hasattr(selectors, 'PollSelector'):
        _PopenSelector = selectors.PollSelector
    inaczej:
        _PopenSelector = selectors.SelectSelector


__all__ = ["Popen", "PIPE", "STDOUT", "call", "check_call", "getstatusoutput",
           "getoutput", "check_output", "run", "CalledProcessError", "DEVNULL",
           "SubprocessError", "TimeoutExpired", "CompletedProcess"]
           # NOTE: We intentionally exclude list2cmdline jako it jest
           # considered an internal implementation detail.  issue10838.

jeżeli _mswindows:
    z _winapi zaimportuj (CREATE_NEW_CONSOLE, CREATE_NEW_PROCESS_GROUP,
                         STD_INPUT_HANDLE, STD_OUTPUT_HANDLE,
                         STD_ERROR_HANDLE, SW_HIDE,
                         STARTF_USESTDHANDLES, STARTF_USESHOWWINDOW)

    __all__.extend(["CREATE_NEW_CONSOLE", "CREATE_NEW_PROCESS_GROUP",
                    "STD_INPUT_HANDLE", "STD_OUTPUT_HANDLE",
                    "STD_ERROR_HANDLE", "SW_HIDE",
                    "STARTF_USESTDHANDLES", "STARTF_USESHOWWINDOW"])

    klasa Handle(int):
        closed = Nieprawda

        def Close(self, CloseHandle=_winapi.CloseHandle):
            jeżeli nie self.closed:
                self.closed = Prawda
                CloseHandle(self)

        def Detach(self):
            jeżeli nie self.closed:
                self.closed = Prawda
                zwróć int(self)
            podnieś ValueError("already closed")

        def __repr__(self):
            zwróć "%s(%d)" % (self.__class__.__name__, int(self))

        __del__ = Close
        __str__ = __repr__


# This lists holds Popen instances dla which the underlying process had nie
# exited at the time its __del__ method got called: those processes are wait()ed
# dla synchronously z _cleanup() when a new Popen object jest created, to avoid
# zombie processes.
_active = []

def _cleanup():
    dla inst w _active[:]:
        res = inst._internal_poll(_deadstate=sys.maxsize)
        jeżeli res jest nie Nic:
            spróbuj:
                _active.remove(inst)
            wyjąwszy ValueError:
                # This can happen jeżeli two threads create a new Popen instance.
                # It's harmless that it was already removed, so ignore.
                dalej

PIPE = -1
STDOUT = -2
DEVNULL = -3


# XXX This function jest only used by multiprocessing oraz the test suite,
# but it's here so that it can be imported when Python jest compiled without
# threads.

def _args_from_interpreter_flags():
    """Return a list of command-line arguments reproducing the current
    settings w sys.flags oraz sys.warnoptions."""
    flag_opt_map = {
        'debug': 'd',
        # 'inspect': 'i',
        # 'interactive': 'i',
        'optimize': 'O',
        'dont_write_bytecode': 'B',
        'no_user_site': 's',
        'no_site': 'S',
        'ignore_environment': 'E',
        'verbose': 'v',
        'bytes_warning': 'b',
        'quiet': 'q',
        'hash_randomization': 'R',
    }
    args = []
    dla flag, opt w flag_opt_map.items():
        v = getattr(sys.flags, flag)
        jeżeli v > 0:
            jeżeli flag == 'hash_randomization':
                v = 1 # Handle specification of an exact seed
            args.append('-' + opt * v)
    dla opt w sys.warnoptions:
        args.append('-W' + opt)
    zwróć args


def call(*popenargs, timeout=Nic, **kwargs):
    """Run command przy arguments.  Wait dla command to complete albo
    timeout, then zwróć the returncode attribute.

    The arguments are the same jako dla the Popen constructor.  Example:

    retcode = call(["ls", "-l"])
    """
    przy Popen(*popenargs, **kwargs) jako p:
        spróbuj:
            zwróć p.wait(timeout=timeout)
        wyjąwszy:
            p.kill()
            p.wait()
            podnieś


def check_call(*popenargs, **kwargs):
    """Run command przy arguments.  Wait dla command to complete.  If
    the exit code was zero then return, otherwise podnieś
    CalledProcessError.  The CalledProcessError object will have the
    zwróć code w the returncode attribute.

    The arguments are the same jako dla the call function.  Example:

    check_call(["ls", "-l"])
    """
    retcode = call(*popenargs, **kwargs)
    jeżeli retcode:
        cmd = kwargs.get("args")
        jeżeli cmd jest Nic:
            cmd = popenargs[0]
        podnieś CalledProcessError(retcode, cmd)
    zwróć 0


def check_output(*popenargs, timeout=Nic, **kwargs):
    r"""Run command przy arguments oraz zwróć its output.

    If the exit code was non-zero it podnieśs a CalledProcessError.  The
    CalledProcessError object will have the zwróć code w the returncode
    attribute oraz output w the output attribute.

    The arguments are the same jako dla the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    b'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument jest nie allowed jako it jest used internally.
    To capture standard error w the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    b'ls: non_existent_file: No such file albo directory\n'

    There jest an additional optional argument, "input", allowing you to
    dalej a string to the subprocess's stdin.  If you use this argument
    you may nie also use the Popen constructor's "stdin" argument, as
    it too will be used internally.  Example:

    >>> check_output(["sed", "-e", "s/foo/bar/"],
    ...              input=b"when w the course of fooman events\n")
    b'when w the course of barman events\n'

    If universal_newlines=Prawda jest dalejed, the "input" argument must be a
    string oraz the zwróć value will be a string rather than bytes.
    """
    jeżeli 'stdout' w kwargs:
        podnieś ValueError('stdout argument nie allowed, it will be overridden.')

    jeżeli 'input' w kwargs oraz kwargs['input'] jest Nic:
        # Explicitly dalejing input=Nic was previously equivalent to dalejing an
        # empty string. That jest maintained here dla backwards compatibility.
        kwargs['input'] = '' jeżeli kwargs.get('universal_newlines', Nieprawda) inaczej b''

    zwróć run(*popenargs, stdout=PIPE, timeout=timeout, check=Prawda,
               **kwargs).stdout


klasa CompletedProcess(object):
    """A process that has finished running.

    This jest returned by run().

    Attributes:
      args: The list albo str args dalejed to run().
      returncode: The exit code of the process, negative dla signals.
      stdout: The standard output (Nic jeżeli nie captured).
      stderr: The standard error (Nic jeżeli nie captured).
    """
    def __init__(self, args, returncode, stdout=Nic, stderr=Nic):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self):
        args = ['args={!r}'.format(self.args),
                'returncode={!r}'.format(self.returncode)]
        jeżeli self.stdout jest nie Nic:
            args.append('stdout={!r}'.format(self.stdout))
        jeżeli self.stderr jest nie Nic:
            args.append('stderr={!r}'.format(self.stderr))
        zwróć "{}({})".format(type(self).__name__, ', '.join(args))

    def check_returncode(self):
        """Raise CalledProcessError jeżeli the exit code jest non-zero."""
        jeżeli self.returncode:
            podnieś CalledProcessError(self.returncode, self.args, self.stdout,
                                     self.stderr)


def run(*popenargs, input=Nic, timeout=Nic, check=Nieprawda, **kwargs):
    """Run command przy arguments oraz zwróć a CompletedProcess instance.

    The returned instance will have attributes args, returncode, stdout oraz
    stderr. By default, stdout oraz stderr are nie captured, oraz those attributes
    will be Nic. Pass stdout=PIPE and/or stderr=PIPE w order to capture them.

    If check jest Prawda oraz the exit code was non-zero, it podnieśs a
    CalledProcessError. The CalledProcessError object will have the zwróć code
    w the returncode attribute, oraz output & stderr attributes jeżeli those streams
    were captured.

    If timeout jest given, oraz the process takes too long, a TimeoutExpired
    exception will be podnieśd.

    There jest an optional argument "input", allowing you to
    dalej a string to the subprocess's stdin.  If you use this argument
    you may nie also use the Popen constructor's "stdin" argument, as
    it will be used internally.

    The other arguments are the same jako dla the Popen constructor.

    If universal_newlines=Prawda jest dalejed, the "input" argument must be a
    string oraz stdout/stderr w the returned object will be strings rather than
    bytes.
    """
    jeżeli input jest nie Nic:
        jeżeli 'stdin' w kwargs:
            podnieś ValueError('stdin oraz input arguments may nie both be used.')
        kwargs['stdin'] = PIPE

    przy Popen(*popenargs, **kwargs) jako process:
        spróbuj:
            stdout, stderr = process.communicate(input, timeout=timeout)
        wyjąwszy TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            podnieś TimeoutExpired(process.args, timeout, output=stdout,
                                 stderr=stderr)
        wyjąwszy:
            process.kill()
            process.wait()
            podnieś
        retcode = process.poll()
        jeżeli check oraz retcode:
            podnieś CalledProcessError(retcode, process.args,
                                     output=stdout, stderr=stderr)
    zwróć CompletedProcess(process.args, retcode, stdout, stderr)


def list2cmdline(seq):
    """
    Translate a sequence of arguments into a command line
    string, using the same rules jako the MS C runtime:

    1) Arguments are delimited by white space, which jest either a
       space albo a tab.

    2) A string surrounded by double quotation marks jest
       interpreted jako a single argument, regardless of white space
       contained within.  A quoted string can be embedded w an
       argument.

    3) A double quotation mark preceded by a backslash jest
       interpreted jako a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes jest interpreted jako a literal
       backslash.  If the number of backslashes jest odd, the last
       backslash escapes the next double quotation mark as
       described w rule 3.
    """

    # See
    # http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    # albo search http://msdn.microsoft.com for
    # "Parsing C++ Command-Line Arguments"
    result = []
    needquote = Nieprawda
    dla arg w seq:
        bs_buf = []

        # Add a space to separate this argument z the others
        jeżeli result:
            result.append(' ')

        needquote = (" " w arg) albo ("\t" w arg) albo nie arg
        jeżeli needquote:
            result.append('"')

        dla c w arg:
            jeżeli c == '\\':
                # Don't know jeżeli we need to double yet.
                bs_buf.append(c)
            albo_inaczej c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            inaczej:
                # Normal char
                jeżeli bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, jeżeli any.
        jeżeli bs_buf:
            result.extend(bs_buf)

        jeżeli needquote:
            result.extend(bs_buf)
            result.append('"')

    zwróć ''.join(result)


# Various tools dla executing commands oraz looking at their output oraz status.
#

def getstatusoutput(cmd):
    """    Return (status, output) of executing cmd w a shell.

    Execute the string 'cmd' w a shell przy 'check_output' oraz
    zwróć a 2-tuple (status, output). Universal newlines mode jest used,
    meaning that the result przy be decoded to a string.

    A trailing newline jest stripped z the output.
    The exit status dla the command can be interpreted
    according to the rules dla the function 'wait'. Example:

    >>> zaimportuj subprocess
    >>> subprocess.getstatusoutput('ls /bin/ls')
    (0, '/bin/ls')
    >>> subprocess.getstatusoutput('cat /bin/junk')
    (256, 'cat: /bin/junk: No such file albo directory')
    >>> subprocess.getstatusoutput('/bin/junk')
    (256, 'sh: /bin/junk: nie found')
    """
    spróbuj:
        data = check_output(cmd, shell=Prawda, universal_newlines=Prawda, stderr=STDOUT)
        status = 0
    wyjąwszy CalledProcessError jako ex:
        data = ex.output
        status = ex.returncode
    jeżeli data[-1:] == '\n':
        data = data[:-1]
    zwróć status, data

def getoutput(cmd):
    """Return output (stdout albo stderr) of executing cmd w a shell.

    Like getstatusoutput(), wyjąwszy the exit status jest ignored oraz the zwróć
    value jest a string containing the command's output.  Example:

    >>> zaimportuj subprocess
    >>> subprocess.getoutput('ls /bin/ls')
    '/bin/ls'
    """
    zwróć getstatusoutput(cmd)[1]


_PLATFORM_DEFAULT_CLOSE_FDS = object()


klasa Popen(object):

    _child_created = Nieprawda  # Set here since __del__ checks it

    def __init__(self, args, bufsize=-1, executable=Nic,
                 stdin=Nic, stdout=Nic, stderr=Nic,
                 preexec_fn=Nic, close_fds=_PLATFORM_DEFAULT_CLOSE_FDS,
                 shell=Nieprawda, cwd=Nic, env=Nic, universal_newlines=Nieprawda,
                 startupinfo=Nic, creationflags=0,
                 restore_signals=Prawda, start_new_session=Nieprawda,
                 dalej_fds=()):
        """Create new Popen instance."""
        _cleanup()
        # Held dopóki anything jest calling waitpid before returncode has been
        # updated to prevent clobbering returncode jeżeli wait() albo poll() are
        # called z multiple threads at once.  After acquiring the lock,
        # code must re-check self.returncode to see jeżeli another thread just
        # finished a waitpid() call.
        self._waitpid_lock = threading.Lock()

        self._input = Nic
        self._communication_started = Nieprawda
        jeżeli bufsize jest Nic:
            bufsize = -1  # Restore default
        jeżeli nie isinstance(bufsize, int):
            podnieś TypeError("bufsize must be an integer")

        jeżeli _mswindows:
            jeżeli preexec_fn jest nie Nic:
                podnieś ValueError("preexec_fn jest nie supported on Windows "
                                 "platforms")
            any_stdio_set = (stdin jest nie Nic albo stdout jest nie Nic albo
                             stderr jest nie Nic)
            jeżeli close_fds jest _PLATFORM_DEFAULT_CLOSE_FDS:
                jeżeli any_stdio_set:
                    close_fds = Nieprawda
                inaczej:
                    close_fds = Prawda
            albo_inaczej close_fds oraz any_stdio_set:
                podnieś ValueError(
                        "close_fds jest nie supported on Windows platforms"
                        " jeżeli you redirect stdin/stdout/stderr")
        inaczej:
            # POSIX
            jeżeli close_fds jest _PLATFORM_DEFAULT_CLOSE_FDS:
                close_fds = Prawda
            jeżeli dalej_fds oraz nie close_fds:
                warnings.warn("pass_fds overriding close_fds.", RuntimeWarning)
                close_fds = Prawda
            jeżeli startupinfo jest nie Nic:
                podnieś ValueError("startupinfo jest only supported on Windows "
                                 "platforms")
            jeżeli creationflags != 0:
                podnieś ValueError("creationflags jest only supported on Windows "
                                 "platforms")

        self.args = args
        self.stdin = Nic
        self.stdout = Nic
        self.stderr = Nic
        self.pid = Nic
        self.returncode = Nic
        self.universal_newlines = universal_newlines

        # Input oraz output objects. The general principle jest like
        # this:
        #
        # Parent                   Child
        # ------                   -----
        # p2cwrite   ---stdin--->  p2cread
        # c2pread    <--stdout---  c2pwrite
        # errread    <--stderr---  errwrite
        #
        # On POSIX, the child objects are file descriptors.  On
        # Windows, these are Windows file handles.  The parent objects
        # are file descriptors on both platforms.  The parent objects
        # are -1 when nie using PIPEs. The child objects are -1
        # when nie redirecting.

        (p2cread, p2cwrite,
         c2pread, c2pwrite,
         errread, errwrite) = self._get_handles(stdin, stdout, stderr)

        # We wrap OS handles *before* launching the child, otherwise a
        # quickly terminating child could make our fds unwrappable
        # (see #8458).

        jeżeli _mswindows:
            jeżeli p2cwrite != -1:
                p2cwrite = msvcrt.open_osfhandle(p2cwrite.Detach(), 0)
            jeżeli c2pread != -1:
                c2pread = msvcrt.open_osfhandle(c2pread.Detach(), 0)
            jeżeli errread != -1:
                errread = msvcrt.open_osfhandle(errread.Detach(), 0)

        jeżeli p2cwrite != -1:
            self.stdin = io.open(p2cwrite, 'wb', bufsize)
            jeżeli universal_newlines:
                self.stdin = io.TextIOWrapper(self.stdin, write_through=Prawda,
                                              line_buffering=(bufsize == 1))
        jeżeli c2pread != -1:
            self.stdout = io.open(c2pread, 'rb', bufsize)
            jeżeli universal_newlines:
                self.stdout = io.TextIOWrapper(self.stdout)
        jeżeli errread != -1:
            self.stderr = io.open(errread, 'rb', bufsize)
            jeżeli universal_newlines:
                self.stderr = io.TextIOWrapper(self.stderr)

        self._closed_child_pipe_fds = Nieprawda
        spróbuj:
            self._execute_child(args, executable, preexec_fn, close_fds,
                                dalej_fds, cwd, env,
                                startupinfo, creationflags, shell,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite,
                                restore_signals, start_new_session)
        wyjąwszy:
            # Cleanup jeżeli the child failed starting.
            dla f w filter(Nic, (self.stdin, self.stdout, self.stderr)):
                spróbuj:
                    f.close()
                wyjąwszy OSError:
                    dalej  # Ignore EBADF albo other errors.

            jeżeli nie self._closed_child_pipe_fds:
                to_close = []
                jeżeli stdin == PIPE:
                    to_close.append(p2cread)
                jeżeli stdout == PIPE:
                    to_close.append(c2pwrite)
                jeżeli stderr == PIPE:
                    to_close.append(errwrite)
                jeżeli hasattr(self, '_devnull'):
                    to_close.append(self._devnull)
                dla fd w to_close:
                    spróbuj:
                        os.close(fd)
                    wyjąwszy OSError:
                        dalej

            podnieś


    def _translate_newlines(self, data, encoding):
        data = data.decode(encoding)
        zwróć data.replace("\r\n", "\n").replace("\r", "\n")

    def __enter__(self):
        zwróć self

    def __exit__(self, type, value, traceback):
        jeżeli self.stdout:
            self.stdout.close()
        jeżeli self.stderr:
            self.stderr.close()
        spróbuj:  # Flushing a BufferedWriter may podnieś an error
            jeżeli self.stdin:
                self.stdin.close()
        w_końcu:
            # Wait dla the process to terminate, to avoid zombies.
            self.wait()

    def __del__(self, _maxsize=sys.maxsize):
        jeżeli nie self._child_created:
            # We didn't get to successfully create a child process.
            zwróć
        # In case the child hasn't been waited on, check jeżeli it's done.
        self._internal_poll(_deadstate=_maxsize)
        jeżeli self.returncode jest Nic oraz _active jest nie Nic:
            # Child jest still running, keep us alive until we can wait on it.
            _active.append(self)

    def _get_devnull(self):
        jeżeli nie hasattr(self, '_devnull'):
            self._devnull = os.open(os.devnull, os.O_RDWR)
        zwróć self._devnull

    def _stdin_write(self, input):
        jeżeli input:
            spróbuj:
                self.stdin.write(input)
            wyjąwszy BrokenPipeError:
                # communicate() must ignore broken pipe error
                dalej
            wyjąwszy OSError jako e:
                jeżeli e.errno == errno.EINVAL oraz self.poll() jest nie Nic:
                    # Issue #19612: On Windows, stdin.write() fails przy EINVAL
                    # jeżeli the process already exited before the write
                    dalej
                inaczej:
                    podnieś
        self.stdin.close()

    def communicate(self, input=Nic, timeout=Nic):
        """Interact przy process: Send data to stdin.  Read data from
        stdout oraz stderr, until end-of-file jest reached.  Wait for
        process to terminate.

        The optional "input" argument should be data to be sent to the
        child process (jeżeli self.universal_newlines jest Prawda, this should
        be a string; jeżeli it jest Nieprawda, "input" should be bytes), albo
        Nic, jeżeli no data should be sent to the child.

        communicate() returns a tuple (stdout, stderr).  These will be
        bytes or, jeżeli self.universal_newlines was Prawda, a string.
        """

        jeżeli self._communication_started oraz input:
            podnieś ValueError("Cannot send input after starting communication")

        # Optimization: If we are nie worried about timeouts, we haven't
        # started communicating, oraz we have one albo zero pipes, using select()
        # albo threads jest unnecessary.
        jeżeli (timeout jest Nic oraz nie self._communication_started oraz
            [self.stdin, self.stdout, self.stderr].count(Nic) >= 2):
            stdout = Nic
            stderr = Nic
            jeżeli self.stdin:
                self._stdin_write(input)
            albo_inaczej self.stdout:
                stdout = self.stdout.read()
                self.stdout.close()
            albo_inaczej self.stderr:
                stderr = self.stderr.read()
                self.stderr.close()
            self.wait()
        inaczej:
            jeżeli timeout jest nie Nic:
                endtime = _time() + timeout
            inaczej:
                endtime = Nic

            spróbuj:
                stdout, stderr = self._communicate(input, endtime, timeout)
            w_końcu:
                self._communication_started = Prawda

            sts = self.wait(timeout=self._remaining_time(endtime))

        zwróć (stdout, stderr)


    def poll(self):
        zwróć self._internal_poll()


    def _remaining_time(self, endtime):
        """Convenience dla _communicate when computing timeouts."""
        jeżeli endtime jest Nic:
            zwróć Nic
        inaczej:
            zwróć endtime - _time()


    def _check_timeout(self, endtime, orig_timeout):
        """Convenience dla checking jeżeli a timeout has expired."""
        jeżeli endtime jest Nic:
            zwróć
        jeżeli _time() > endtime:
            podnieś TimeoutExpired(self.args, orig_timeout)


    jeżeli _mswindows:
        #
        # Windows methods
        #
        def _get_handles(self, stdin, stdout, stderr):
            """Construct oraz zwróć tuple przy IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            jeżeli stdin jest Nic oraz stdout jest Nic oraz stderr jest Nic:
                zwróć (-1, -1, -1, -1, -1, -1)

            p2cread, p2cwrite = -1, -1
            c2pread, c2pwrite = -1, -1
            errread, errwrite = -1, -1

            jeżeli stdin jest Nic:
                p2cread = _winapi.GetStdHandle(_winapi.STD_INPUT_HANDLE)
                jeżeli p2cread jest Nic:
                    p2cread, _ = _winapi.CreatePipe(Nic, 0)
                    p2cread = Handle(p2cread)
                    _winapi.CloseHandle(_)
            albo_inaczej stdin == PIPE:
                p2cread, p2cwrite = _winapi.CreatePipe(Nic, 0)
                p2cread, p2cwrite = Handle(p2cread), Handle(p2cwrite)
            albo_inaczej stdin == DEVNULL:
                p2cread = msvcrt.get_osfhandle(self._get_devnull())
            albo_inaczej isinstance(stdin, int):
                p2cread = msvcrt.get_osfhandle(stdin)
            inaczej:
                # Assuming file-like object
                p2cread = msvcrt.get_osfhandle(stdin.fileno())
            p2cread = self._make_inheritable(p2cread)

            jeżeli stdout jest Nic:
                c2pwrite = _winapi.GetStdHandle(_winapi.STD_OUTPUT_HANDLE)
                jeżeli c2pwrite jest Nic:
                    _, c2pwrite = _winapi.CreatePipe(Nic, 0)
                    c2pwrite = Handle(c2pwrite)
                    _winapi.CloseHandle(_)
            albo_inaczej stdout == PIPE:
                c2pread, c2pwrite = _winapi.CreatePipe(Nic, 0)
                c2pread, c2pwrite = Handle(c2pread), Handle(c2pwrite)
            albo_inaczej stdout == DEVNULL:
                c2pwrite = msvcrt.get_osfhandle(self._get_devnull())
            albo_inaczej isinstance(stdout, int):
                c2pwrite = msvcrt.get_osfhandle(stdout)
            inaczej:
                # Assuming file-like object
                c2pwrite = msvcrt.get_osfhandle(stdout.fileno())
            c2pwrite = self._make_inheritable(c2pwrite)

            jeżeli stderr jest Nic:
                errwrite = _winapi.GetStdHandle(_winapi.STD_ERROR_HANDLE)
                jeżeli errwrite jest Nic:
                    _, errwrite = _winapi.CreatePipe(Nic, 0)
                    errwrite = Handle(errwrite)
                    _winapi.CloseHandle(_)
            albo_inaczej stderr == PIPE:
                errread, errwrite = _winapi.CreatePipe(Nic, 0)
                errread, errwrite = Handle(errread), Handle(errwrite)
            albo_inaczej stderr == STDOUT:
                errwrite = c2pwrite
            albo_inaczej stderr == DEVNULL:
                errwrite = msvcrt.get_osfhandle(self._get_devnull())
            albo_inaczej isinstance(stderr, int):
                errwrite = msvcrt.get_osfhandle(stderr)
            inaczej:
                # Assuming file-like object
                errwrite = msvcrt.get_osfhandle(stderr.fileno())
            errwrite = self._make_inheritable(errwrite)

            zwróć (p2cread, p2cwrite,
                    c2pread, c2pwrite,
                    errread, errwrite)


        def _make_inheritable(self, handle):
            """Return a duplicate of handle, which jest inheritable"""
            h = _winapi.DuplicateHandle(
                _winapi.GetCurrentProcess(), handle,
                _winapi.GetCurrentProcess(), 0, 1,
                _winapi.DUPLICATE_SAME_ACCESS)
            zwróć Handle(h)


        def _execute_child(self, args, executable, preexec_fn, close_fds,
                           dalej_fds, cwd, env,
                           startupinfo, creationflags, shell,
                           p2cread, p2cwrite,
                           c2pread, c2pwrite,
                           errread, errwrite,
                           unused_restore_signals, unused_start_new_session):
            """Execute program (MS Windows version)"""

            assert nie dalej_fds, "pass_fds nie supported on Windows."

            jeżeli nie isinstance(args, str):
                args = list2cmdline(args)

            # Process startup details
            jeżeli startupinfo jest Nic:
                startupinfo = STARTUPINFO()
            jeżeli -1 nie w (p2cread, c2pwrite, errwrite):
                startupinfo.dwFlags |= _winapi.STARTF_USESTDHANDLES
                startupinfo.hStdInput = p2cread
                startupinfo.hStdOutput = c2pwrite
                startupinfo.hStdError = errwrite

            jeżeli shell:
                startupinfo.dwFlags |= _winapi.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = _winapi.SW_HIDE
                comspec = os.environ.get("COMSPEC", "cmd.exe")
                args = '{} /c "{}"'.format (comspec, args)

            # Start the process
            spróbuj:
                hp, ht, pid, tid = _winapi.CreateProcess(executable, args,
                                         # no special security
                                         Nic, Nic,
                                         int(nie close_fds),
                                         creationflags,
                                         env,
                                         cwd,
                                         startupinfo)
            w_końcu:
                # Child jest launched. Close the parent's copy of those pipe
                # handles that only the child should have open.  You need
                # to make sure that no handles to the write end of the
                # output pipe are maintained w this process albo inaczej the
                # pipe will nie close when the child process exits oraz the
                # ReadFile will hang.
                jeżeli p2cread != -1:
                    p2cread.Close()
                jeżeli c2pwrite != -1:
                    c2pwrite.Close()
                jeżeli errwrite != -1:
                    errwrite.Close()
                jeżeli hasattr(self, '_devnull'):
                    os.close(self._devnull)

            # Retain the process handle, but close the thread handle
            self._child_created = Prawda
            self._handle = Handle(hp)
            self.pid = pid
            _winapi.CloseHandle(ht)

        def _internal_poll(self, _deadstate=Nic,
                _WaitForSingleObject=_winapi.WaitForSingleObject,
                _WAIT_OBJECT_0=_winapi.WAIT_OBJECT_0,
                _GetExitCodeProcess=_winapi.GetExitCodeProcess):
            """Check jeżeli child process has terminated.  Returns returncode
            attribute.

            This method jest called by __del__, so it can only refer to objects
            w its local scope.

            """
            jeżeli self.returncode jest Nic:
                jeżeli _WaitForSingleObject(self._handle, 0) == _WAIT_OBJECT_0:
                    self.returncode = _GetExitCodeProcess(self._handle)
            zwróć self.returncode


        def wait(self, timeout=Nic, endtime=Nic):
            """Wait dla child process to terminate.  Returns returncode
            attribute."""
            jeżeli endtime jest nie Nic:
                timeout = self._remaining_time(endtime)
            jeżeli timeout jest Nic:
                timeout_millis = _winapi.INFINITE
            inaczej:
                timeout_millis = int(timeout * 1000)
            jeżeli self.returncode jest Nic:
                result = _winapi.WaitForSingleObject(self._handle,
                                                    timeout_millis)
                jeżeli result == _winapi.WAIT_TIMEOUT:
                    podnieś TimeoutExpired(self.args, timeout)
                self.returncode = _winapi.GetExitCodeProcess(self._handle)
            zwróć self.returncode


        def _readerthread(self, fh, buffer):
            buffer.append(fh.read())
            fh.close()


        def _communicate(self, input, endtime, orig_timeout):
            # Start reader threads feeding into a list hanging off of this
            # object, unless they've already been started.
            jeżeli self.stdout oraz nie hasattr(self, "_stdout_buff"):
                self._stdout_buff = []
                self.stdout_thread = \
                        threading.Thread(target=self._readerthread,
                                         args=(self.stdout, self._stdout_buff))
                self.stdout_thread.daemon = Prawda
                self.stdout_thread.start()
            jeżeli self.stderr oraz nie hasattr(self, "_stderr_buff"):
                self._stderr_buff = []
                self.stderr_thread = \
                        threading.Thread(target=self._readerthread,
                                         args=(self.stderr, self._stderr_buff))
                self.stderr_thread.daemon = Prawda
                self.stderr_thread.start()

            jeżeli self.stdin:
                self._stdin_write(input)

            # Wait dla the reader threads, albo time out.  If we time out, the
            # threads remain reading oraz the fds left open w case the user
            # calls communicate again.
            jeżeli self.stdout jest nie Nic:
                self.stdout_thread.join(self._remaining_time(endtime))
                jeżeli self.stdout_thread.is_alive():
                    podnieś TimeoutExpired(self.args, orig_timeout)
            jeżeli self.stderr jest nie Nic:
                self.stderr_thread.join(self._remaining_time(endtime))
                jeżeli self.stderr_thread.is_alive():
                    podnieś TimeoutExpired(self.args, orig_timeout)

            # Collect the output z oraz close both pipes, now that we know
            # both have been read successfully.
            stdout = Nic
            stderr = Nic
            jeżeli self.stdout:
                stdout = self._stdout_buff
                self.stdout.close()
            jeżeli self.stderr:
                stderr = self._stderr_buff
                self.stderr.close()

            # All data exchanged.  Translate lists into strings.
            jeżeli stdout jest nie Nic:
                stdout = stdout[0]
            jeżeli stderr jest nie Nic:
                stderr = stderr[0]

            zwróć (stdout, stderr)

        def send_signal(self, sig):
            """Send a signal to the process
            """
            jeżeli sig == signal.SIGTERM:
                self.terminate()
            albo_inaczej sig == signal.CTRL_C_EVENT:
                os.kill(self.pid, signal.CTRL_C_EVENT)
            albo_inaczej sig == signal.CTRL_BREAK_EVENT:
                os.kill(self.pid, signal.CTRL_BREAK_EVENT)
            inaczej:
                podnieś ValueError("Unsupported signal: {}".format(sig))

        def terminate(self):
            """Terminates the process
            """
            spróbuj:
                _winapi.TerminateProcess(self._handle, 1)
            wyjąwszy PermissionError:
                # ERROR_ACCESS_DENIED (winerror 5) jest received when the
                # process already died.
                rc = _winapi.GetExitCodeProcess(self._handle)
                jeżeli rc == _winapi.STILL_ACTIVE:
                    podnieś
                self.returncode = rc

        kill = terminate

    inaczej:
        #
        # POSIX methods
        #
        def _get_handles(self, stdin, stdout, stderr):
            """Construct oraz zwróć tuple przy IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            p2cread, p2cwrite = -1, -1
            c2pread, c2pwrite = -1, -1
            errread, errwrite = -1, -1

            jeżeli stdin jest Nic:
                dalej
            albo_inaczej stdin == PIPE:
                p2cread, p2cwrite = os.pipe()
            albo_inaczej stdin == DEVNULL:
                p2cread = self._get_devnull()
            albo_inaczej isinstance(stdin, int):
                p2cread = stdin
            inaczej:
                # Assuming file-like object
                p2cread = stdin.fileno()

            jeżeli stdout jest Nic:
                dalej
            albo_inaczej stdout == PIPE:
                c2pread, c2pwrite = os.pipe()
            albo_inaczej stdout == DEVNULL:
                c2pwrite = self._get_devnull()
            albo_inaczej isinstance(stdout, int):
                c2pwrite = stdout
            inaczej:
                # Assuming file-like object
                c2pwrite = stdout.fileno()

            jeżeli stderr jest Nic:
                dalej
            albo_inaczej stderr == PIPE:
                errread, errwrite = os.pipe()
            albo_inaczej stderr == STDOUT:
                errwrite = c2pwrite
            albo_inaczej stderr == DEVNULL:
                errwrite = self._get_devnull()
            albo_inaczej isinstance(stderr, int):
                errwrite = stderr
            inaczej:
                # Assuming file-like object
                errwrite = stderr.fileno()

            zwróć (p2cread, p2cwrite,
                    c2pread, c2pwrite,
                    errread, errwrite)


        def _execute_child(self, args, executable, preexec_fn, close_fds,
                           dalej_fds, cwd, env,
                           startupinfo, creationflags, shell,
                           p2cread, p2cwrite,
                           c2pread, c2pwrite,
                           errread, errwrite,
                           restore_signals, start_new_session):
            """Execute program (POSIX version)"""

            jeżeli isinstance(args, (str, bytes)):
                args = [args]
            inaczej:
                args = list(args)

            jeżeli shell:
                args = ["/bin/sh", "-c"] + args
                jeżeli executable:
                    args[0] = executable

            jeżeli executable jest Nic:
                executable = args[0]
            orig_executable = executable

            # For transferring possible exec failure z child to parent.
            # Data format: "exception name:hex errno:description"
            # Pickle jest nie used; it jest complex oraz involves memory allocation.
            errpipe_read, errpipe_write = os.pipe()
            # errpipe_write must nie be w the standard io 0, 1, albo 2 fd range.
            low_fds_to_close = []
            dopóki errpipe_write < 3:
                low_fds_to_close.append(errpipe_write)
                errpipe_write = os.dup(errpipe_write)
            dla low_fd w low_fds_to_close:
                os.close(low_fd)
            spróbuj:
                spróbuj:
                    # We must avoid complex work that could involve
                    # malloc albo free w the child process to avoid
                    # potential deadlocks, thus we do all this here.
                    # oraz dalej it to fork_exec()

                    jeżeli env jest nie Nic:
                        env_list = [os.fsencode(k) + b'=' + os.fsencode(v)
                                    dla k, v w env.items()]
                    inaczej:
                        env_list = Nic  # Use execv instead of execve.
                    executable = os.fsencode(executable)
                    jeżeli os.path.dirname(executable):
                        executable_list = (executable,)
                    inaczej:
                        # This matches the behavior of os._execvpe().
                        executable_list = tuple(
                            os.path.join(os.fsencode(dir), executable)
                            dla dir w os.get_exec_path(env))
                    fds_to_keep = set(pass_fds)
                    fds_to_keep.add(errpipe_write)
                    self.pid = _posixsubprocess.fork_exec(
                            args, executable_list,
                            close_fds, sorted(fds_to_keep), cwd, env_list,
                            p2cread, p2cwrite, c2pread, c2pwrite,
                            errread, errwrite,
                            errpipe_read, errpipe_write,
                            restore_signals, start_new_session, preexec_fn)
                    self._child_created = Prawda
                w_końcu:
                    # be sure the FD jest closed no matter what
                    os.close(errpipe_write)

                # self._devnull jest nie always defined.
                devnull_fd = getattr(self, '_devnull', Nic)
                jeżeli p2cread != -1 oraz p2cwrite != -1 oraz p2cread != devnull_fd:
                    os.close(p2cread)
                jeżeli c2pwrite != -1 oraz c2pread != -1 oraz c2pwrite != devnull_fd:
                    os.close(c2pwrite)
                jeżeli errwrite != -1 oraz errread != -1 oraz errwrite != devnull_fd:
                    os.close(errwrite)
                jeżeli devnull_fd jest nie Nic:
                    os.close(devnull_fd)
                # Prevent a double close of these fds z __init__ on error.
                self._closed_child_pipe_fds = Prawda

                # Wait dla exec to fail albo succeed; possibly raising an
                # exception (limited w size)
                errpipe_data = bytearray()
                dopóki Prawda:
                    part = os.read(errpipe_read, 50000)
                    errpipe_data += part
                    jeżeli nie part albo len(errpipe_data) > 50000:
                        przerwij
            w_końcu:
                # be sure the FD jest closed no matter what
                os.close(errpipe_read)

            jeżeli errpipe_data:
                spróbuj:
                    os.waitpid(self.pid, 0)
                wyjąwszy ChildProcessError:
                    dalej
                spróbuj:
                    exception_name, hex_errno, err_msg = (
                            errpipe_data.split(b':', 2))
                wyjąwszy ValueError:
                    exception_name = b'SubprocessError'
                    hex_errno = b'0'
                    err_msg = (b'Bad exception data z child: ' +
                               repr(errpipe_data))
                child_exception_type = getattr(
                        builtins, exception_name.decode('ascii'),
                        SubprocessError)
                err_msg = err_msg.decode(errors="surrogatepass")
                jeżeli issubclass(child_exception_type, OSError) oraz hex_errno:
                    errno_num = int(hex_errno, 16)
                    child_exec_never_called = (err_msg == "noexec")
                    jeżeli child_exec_never_called:
                        err_msg = ""
                    jeżeli errno_num != 0:
                        err_msg = os.strerror(errno_num)
                        jeżeli errno_num == errno.ENOENT:
                            jeżeli child_exec_never_called:
                                # The error must be z chdir(cwd).
                                err_msg += ': ' + repr(cwd)
                            inaczej:
                                err_msg += ': ' + repr(orig_executable)
                    podnieś child_exception_type(errno_num, err_msg)
                podnieś child_exception_type(err_msg)


        def _handle_exitstatus(self, sts, _WIFSIGNALED=os.WIFSIGNALED,
                _WTERMSIG=os.WTERMSIG, _WIFEXITED=os.WIFEXITED,
                _WEXITSTATUS=os.WEXITSTATUS):
            """All callers to this function MUST hold self._waitpid_lock."""
            # This method jest called (indirectly) by __del__, so it cannot
            # refer to anything outside of its local scope.
            jeżeli _WIFSIGNALED(sts):
                self.returncode = -_WTERMSIG(sts)
            albo_inaczej _WIFEXITED(sts):
                self.returncode = _WEXITSTATUS(sts)
            inaczej:
                # Should never happen
                podnieś SubprocessError("Unknown child exit status!")


        def _internal_poll(self, _deadstate=Nic, _waitpid=os.waitpid,
                _WNOHANG=os.WNOHANG, _ECHILD=errno.ECHILD):
            """Check jeżeli child process has terminated.  Returns returncode
            attribute.

            This method jest called by __del__, so it cannot reference anything
            outside of the local scope (nor can any methods it calls).

            """
            jeżeli self.returncode jest Nic:
                jeżeli nie self._waitpid_lock.acquire(Nieprawda):
                    # Something inaczej jest busy calling waitpid.  Don't allow two
                    # at once.  We know nothing yet.
                    zwróć Nic
                spróbuj:
                    jeżeli self.returncode jest nie Nic:
                        zwróć self.returncode  # Another thread waited.
                    pid, sts = _waitpid(self.pid, _WNOHANG)
                    jeżeli pid == self.pid:
                        self._handle_exitstatus(sts)
                wyjąwszy OSError jako e:
                    jeżeli _deadstate jest nie Nic:
                        self.returncode = _deadstate
                    albo_inaczej e.errno == _ECHILD:
                        # This happens jeżeli SIGCLD jest set to be ignored albo
                        # waiting dla child processes has otherwise been
                        # disabled dla our process.  This child jest dead, we
                        # can't get the status.
                        # http://bugs.python.org/issue15756
                        self.returncode = 0
                w_końcu:
                    self._waitpid_lock.release()
            zwróć self.returncode


        def _try_wait(self, wait_flags):
            """All callers to this function MUST hold self._waitpid_lock."""
            spróbuj:
                (pid, sts) = os.waitpid(self.pid, wait_flags)
            wyjąwszy ChildProcessError:
                # This happens jeżeli SIGCLD jest set to be ignored albo waiting
                # dla child processes has otherwise been disabled dla our
                # process.  This child jest dead, we can't get the status.
                pid = self.pid
                sts = 0
            zwróć (pid, sts)


        def wait(self, timeout=Nic, endtime=Nic):
            """Wait dla child process to terminate.  Returns returncode
            attribute."""
            jeżeli self.returncode jest nie Nic:
                zwróć self.returncode

            # endtime jest preferred to timeout.  timeout jest only used for
            # printing.
            jeżeli endtime jest nie Nic albo timeout jest nie Nic:
                jeżeli endtime jest Nic:
                    endtime = _time() + timeout
                albo_inaczej timeout jest Nic:
                    timeout = self._remaining_time(endtime)

            jeżeli endtime jest nie Nic:
                # Enter a busy loop jeżeli we have a timeout.  This busy loop was
                # cribbed z Lib/threading.py w Thread.wait() at r71065.
                delay = 0.0005 # 500 us -> initial delay of 1 ms
                dopóki Prawda:
                    jeżeli self._waitpid_lock.acquire(Nieprawda):
                        spróbuj:
                            jeżeli self.returncode jest nie Nic:
                                przerwij  # Another thread waited.
                            (pid, sts) = self._try_wait(os.WNOHANG)
                            assert pid == self.pid albo pid == 0
                            jeżeli pid == self.pid:
                                self._handle_exitstatus(sts)
                                przerwij
                        w_końcu:
                            self._waitpid_lock.release()
                    remaining = self._remaining_time(endtime)
                    jeżeli remaining <= 0:
                        podnieś TimeoutExpired(self.args, timeout)
                    delay = min(delay * 2, remaining, .05)
                    time.sleep(delay)
            inaczej:
                dopóki self.returncode jest Nic:
                    przy self._waitpid_lock:
                        jeżeli self.returncode jest nie Nic:
                            przerwij  # Another thread waited.
                        (pid, sts) = self._try_wait(0)
                        # Check the pid oraz loop jako waitpid has been known to
                        # zwróć 0 even without WNOHANG w odd situations.
                        # http://bugs.python.org/issue14396.
                        jeżeli pid == self.pid:
                            self._handle_exitstatus(sts)
            zwróć self.returncode


        def _communicate(self, input, endtime, orig_timeout):
            jeżeli self.stdin oraz nie self._communication_started:
                # Flush stdio buffer.  This might block, jeżeli the user has
                # been writing to .stdin w an uncontrolled fashion.
                self.stdin.flush()
                jeżeli nie input:
                    self.stdin.close()

            stdout = Nic
            stderr = Nic

            # Only create this mapping jeżeli we haven't already.
            jeżeli nie self._communication_started:
                self._fileobj2output = {}
                jeżeli self.stdout:
                    self._fileobj2output[self.stdout] = []
                jeżeli self.stderr:
                    self._fileobj2output[self.stderr] = []

            jeżeli self.stdout:
                stdout = self._fileobj2output[self.stdout]
            jeżeli self.stderr:
                stderr = self._fileobj2output[self.stderr]

            self._save_input(input)

            jeżeli self._input:
                input_view = memoryview(self._input)

            przy _PopenSelector() jako selector:
                jeżeli self.stdin oraz input:
                    selector.register(self.stdin, selectors.EVENT_WRITE)
                jeżeli self.stdout:
                    selector.register(self.stdout, selectors.EVENT_READ)
                jeżeli self.stderr:
                    selector.register(self.stderr, selectors.EVENT_READ)

                dopóki selector.get_map():
                    timeout = self._remaining_time(endtime)
                    jeżeli timeout jest nie Nic oraz timeout < 0:
                        podnieś TimeoutExpired(self.args, orig_timeout)

                    ready = selector.select(timeout)
                    self._check_timeout(endtime, orig_timeout)

                    # XXX Rewrite these to use non-blocking I/O on the file
                    # objects; they are no longer using C stdio!

                    dla key, events w ready:
                        jeżeli key.fileobj jest self.stdin:
                            chunk = input_view[self._input_offset :
                                               self._input_offset + _PIPE_BUF]
                            spróbuj:
                                self._input_offset += os.write(key.fd, chunk)
                            wyjąwszy BrokenPipeError:
                                selector.unregister(key.fileobj)
                                key.fileobj.close()
                            inaczej:
                                jeżeli self._input_offset >= len(self._input):
                                    selector.unregister(key.fileobj)
                                    key.fileobj.close()
                        albo_inaczej key.fileobj w (self.stdout, self.stderr):
                            data = os.read(key.fd, 32768)
                            jeżeli nie data:
                                selector.unregister(key.fileobj)
                                key.fileobj.close()
                            self._fileobj2output[key.fileobj].append(data)

            self.wait(timeout=self._remaining_time(endtime))

            # All data exchanged.  Translate lists into strings.
            jeżeli stdout jest nie Nic:
                stdout = b''.join(stdout)
            jeżeli stderr jest nie Nic:
                stderr = b''.join(stderr)

            # Translate newlines, jeżeli requested.
            # This also turns bytes into strings.
            jeżeli self.universal_newlines:
                jeżeli stdout jest nie Nic:
                    stdout = self._translate_newlines(stdout,
                                                      self.stdout.encoding)
                jeżeli stderr jest nie Nic:
                    stderr = self._translate_newlines(stderr,
                                                      self.stderr.encoding)

            zwróć (stdout, stderr)


        def _save_input(self, input):
            # This method jest called z the _communicate_with_*() methods
            # so that jeżeli we time out dopóki communicating, we can kontynuuj
            # sending input jeżeli we retry.
            jeżeli self.stdin oraz self._input jest Nic:
                self._input_offset = 0
                self._input = input
                jeżeli self.universal_newlines oraz input jest nie Nic:
                    self._input = self._input.encode(self.stdin.encoding)


        def send_signal(self, sig):
            """Send a signal to the process
            """
            os.kill(self.pid, sig)

        def terminate(self):
            """Terminate the process przy SIGTERM
            """
            self.send_signal(signal.SIGTERM)

        def kill(self):
            """Kill the process przy SIGKILL
            """
            self.send_signal(signal.SIGKILL)
