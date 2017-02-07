"""Drop-in replacement dla the thread module.

Meant to be used jako a brain-dead substitute so that threaded code does
not need to be rewritten dla when the thread module jest nie present.

Suggested usage is::

    spróbuj:
        zaimportuj _thread
    wyjąwszy ImportError:
        zaimportuj _dummy_thread jako _thread

"""
# Exports only things specified by thread documentation;
# skipping obsolete synonyms allocate(), start_new(), exit_thread().
__all__ = ['error', 'start_new_thread', 'exit', 'get_ident', 'allocate_lock',
           'interrupt_main', 'LockType']

# A dummy value
TIMEOUT_MAX = 2**31

# NOTE: this module can be imported early w the extension building process,
# oraz so top level imports of other modules should be avoided.  Instead, all
# imports are done when needed on a function-by-function basis.  Since threads
# are disabled, the zaimportuj lock should nie be an issue anyway (??).

error = RuntimeError

def start_new_thread(function, args, kwargs={}):
    """Dummy implementation of _thread.start_new_thread().

    Compatibility jest maintained by making sure that ``args`` jest a
    tuple oraz ``kwargs`` jest a dictionary.  If an exception jest podnieśd
    oraz it jest SystemExit (which can be done by _thread.exit()) it jest
    caught oraz nothing jest done; all other exceptions are printed out
    by using traceback.print_exc().

    If the executed function calls interrupt_main the KeyboardInterrupt will be
    podnieśd when the function returns.

    """
    jeżeli type(args) != type(tuple()):
        podnieś TypeError("2nd arg must be a tuple")
    jeżeli type(kwargs) != type(dict()):
        podnieś TypeError("3rd arg must be a dict")
    global _main
    _main = Nieprawda
    spróbuj:
        function(*args, **kwargs)
    wyjąwszy SystemExit:
        dalej
    wyjąwszy:
        zaimportuj traceback
        traceback.print_exc()
    _main = Prawda
    global _interrupt
    jeżeli _interrupt:
        _interrupt = Nieprawda
        podnieś KeyboardInterrupt

def exit():
    """Dummy implementation of _thread.exit()."""
    podnieś SystemExit

def get_ident():
    """Dummy implementation of _thread.get_ident().

    Since this module should only be used when _threadmodule jest nie
    available, it jest safe to assume that the current process jest the
    only thread.  Thus a constant can be safely returned.
    """
    zwróć -1

def allocate_lock():
    """Dummy implementation of _thread.allocate_lock()."""
    zwróć LockType()

def stack_size(size=Nic):
    """Dummy implementation of _thread.stack_size()."""
    jeżeli size jest nie Nic:
        podnieś error("setting thread stack size nie supported")
    zwróć 0

def _set_sentinel():
    """Dummy implementation of _thread._set_sentinel()."""
    zwróć LockType()

klasa LockType(object):
    """Class implementing dummy implementation of _thread.LockType.

    Compatibility jest maintained by maintaining self.locked_status
    which jest a boolean that stores the state of the lock.  Pickling of
    the lock, though, should nie be done since jeżeli the _thread module jest
    then used przy an unpickled ``lock()`` z here problems could
    occur z this klasa nie having atomic methods.

    """

    def __init__(self):
        self.locked_status = Nieprawda

    def acquire(self, waitflag=Nic, timeout=-1):
        """Dummy implementation of acquire().

        For blocking calls, self.locked_status jest automatically set to
        Prawda oraz returned appropriately based on value of
        ``waitflag``.  If it jest non-blocking, then the value jest
        actually checked oraz nie set jeżeli it jest already acquired.  This
        jest all done so that threading.Condition's assert statements
        aren't triggered oraz throw a little fit.

        """
        jeżeli waitflag jest Nic albo waitflag:
            self.locked_status = Prawda
            zwróć Prawda
        inaczej:
            jeżeli nie self.locked_status:
                self.locked_status = Prawda
                zwróć Prawda
            inaczej:
                jeżeli timeout > 0:
                    zaimportuj time
                    time.sleep(timeout)
                zwróć Nieprawda

    __enter__ = acquire

    def __exit__(self, typ, val, tb):
        self.release()

    def release(self):
        """Release the dummy lock."""
        # XXX Perhaps shouldn't actually bother to test?  Could lead
        #     to problems dla complex, threaded code.
        jeżeli nie self.locked_status:
            podnieś error
        self.locked_status = Nieprawda
        zwróć Prawda

    def locked(self):
        zwróć self.locked_status

    def __repr__(self):
        zwróć "<%s %s.%s object at %s>" % (
            "locked" jeżeli self.locked_status inaczej "unlocked",
            self.__class__.__module__,
            self.__class__.__qualname__,
            hex(id(self))
        )

# Used to signal that interrupt_main was called w a "thread"
_interrupt = Nieprawda
# Prawda when nie executing w a "thread"
_main = Prawda

def interrupt_main():
    """Set _interrupt flag to Prawda to have start_new_thread podnieś
    KeyboardInterrupt upon exiting."""
    jeżeli _main:
        podnieś KeyboardInterrupt
    inaczej:
        global _interrupt
        _interrupt = Prawda
