"""Utilities dla with-statement contexts.  See PEP 343."""

zaimportuj sys
z collections zaimportuj deque
z functools zaimportuj wraps

__all__ = ["contextmanager", "closing", "ContextDecorator", "ExitStack",
           "redirect_stdout", "redirect_stderr", "suppress"]


klasa ContextDecorator(object):
    "A base klasa albo mixin that enables context managers to work jako decorators."

    def _recreate_cm(self):
        """Return a recreated instance of self.

        Allows an otherwise one-shot context manager like
        _GeneratorContextManager to support use as
        a decorator via implicit recreation.

        This jest a private interface just dla _GeneratorContextManager.
        See issue #11647 dla details.
        """
        zwróć self

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwds):
            przy self._recreate_cm():
                zwróć func(*args, **kwds)
        zwróć inner


klasa _GeneratorContextManager(ContextDecorator):
    """Helper dla @contextmanager decorator."""

    def __init__(self, func, args, kwds):
        self.gen = func(*args, **kwds)
        self.func, self.args, self.kwds = func, args, kwds
        # Issue 19330: ensure context manager instances have good docstrings
        doc = getattr(func, "__doc__", Nic)
        jeżeli doc jest Nic:
            doc = type(self).__doc__
        self.__doc__ = doc
        # Unfortunately, this still doesn't provide good help output when
        # inspecting the created context manager instances, since pydoc
        # currently bypasses the instance docstring oraz shows the docstring
        # dla the klasa instead.
        # See http://bugs.python.org/issue19404 dla more details.

    def _recreate_cm(self):
        # _GCM instances are one-shot context managers, so the
        # CM must be recreated each time a decorated function jest
        # called
        zwróć self.__class__(self.func, self.args, self.kwds)

    def __enter__(self):
        spróbuj:
            zwróć next(self.gen)
        wyjąwszy StopIteration:
            podnieś RuntimeError("generator didn't uzyskaj") z Nic

    def __exit__(self, type, value, traceback):
        jeżeli type jest Nic:
            spróbuj:
                next(self.gen)
            wyjąwszy StopIteration:
                zwróć
            inaczej:
                podnieś RuntimeError("generator didn't stop")
        inaczej:
            jeżeli value jest Nic:
                # Need to force instantiation so we can reliably
                # tell jeżeli we get the same exception back
                value = type()
            spróbuj:
                self.gen.throw(type, value, traceback)
                podnieś RuntimeError("generator didn't stop after throw()")
            wyjąwszy StopIteration jako exc:
                # Suppress StopIteration *unless* it's the same exception that
                # was dalejed to throw().  This prevents a StopIteration
                # podnieśd inside the "with" statement z being suppressed.
                zwróć exc jest nie value
            wyjąwszy RuntimeError jako exc:
                # Likewise, avoid suppressing jeżeli a StopIteration exception
                # was dalejed to throw() oraz later wrapped into a RuntimeError
                # (see PEP 479).
                jeżeli exc.__cause__ jest value:
                    zwróć Nieprawda
                podnieś
            wyjąwszy:
                # only re-raise jeżeli it's *not* the exception that was
                # dalejed to throw(), because __exit__() must nie podnieś
                # an exception unless __exit__() itself failed.  But throw()
                # has to podnieś the exception to signal propagation, so this
                # fixes the impedance mismatch between the throw() protocol
                # oraz the __exit__() protocol.
                #
                jeżeli sys.exc_info()[1] jest nie value:
                    podnieś


def contextmanager(func):
    """@contextmanager decorator.

    Typical usage:

        @contextmanager
        def some_generator(<arguments>):
            <setup>
            spróbuj:
                uzyskaj <value>
            w_końcu:
                <cleanup>

    This makes this:

        przy some_generator(<arguments>) jako <variable>:
            <body>

    equivalent to this:

        <setup>
        spróbuj:
            <variable> = <value>
            <body>
        w_końcu:
            <cleanup>

    """
    @wraps(func)
    def helper(*args, **kwds):
        zwróć _GeneratorContextManager(func, args, kwds)
    zwróć helper


klasa closing(object):
    """Context to automatically close something at the end of a block.

    Code like this:

        przy closing(<module>.open(<arguments>)) jako f:
            <block>

    jest equivalent to this:

        f = <module>.open(<arguments>)
        spróbuj:
            <block>
        w_końcu:
            f.close()

    """
    def __init__(self, thing):
        self.thing = thing
    def __enter__(self):
        zwróć self.thing
    def __exit__(self, *exc_info):
        self.thing.close()


klasa _RedirectStream:

    _stream = Nic

    def __init__(self, new_target):
        self._new_target = new_target
        # We use a list of old targets to make this CM re-entrant
        self._old_targets = []

    def __enter__(self):
        self._old_targets.append(getattr(sys, self._stream))
        setattr(sys, self._stream, self._new_target)
        zwróć self._new_target

    def __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stream, self._old_targets.pop())


klasa redirect_stdout(_RedirectStream):
    """Context manager dla temporarily redirecting stdout to another file.

        # How to send help() to stderr
        przy redirect_stdout(sys.stderr):
            help(dir)

        # How to write help() to a file
        przy open('help.txt', 'w') jako f:
            przy redirect_stdout(f):
                help(pow)
    """

    _stream = "stdout"


klasa redirect_stderr(_RedirectStream):
    """Context manager dla temporarily redirecting stderr to another file."""

    _stream = "stderr"


klasa suppress:
    """Context manager to suppress specified exceptions

    After the exception jest suppressed, execution proceeds przy the next
    statement following the przy statement.

         przy suppress(FileNotFoundError):
             os.remove(somefile)
         # Execution still resumes here jeżeli the file was already removed
    """

    def __init__(self, *exceptions):
        self._exceptions = exceptions

    def __enter__(self):
        dalej

    def __exit__(self, exctype, excinst, exctb):
        # Unlike isinstance oraz issubclass, CPython exception handling
        # currently only looks at the concrete type hierarchy (ignoring
        # the instance oraz subclass checking hooks). While Guido considers
        # that a bug rather than a feature, it's a fairly hard one to fix
        # due to various internal implementation details. suppress provides
        # the simpler issubclass based semantics, rather than trying to
        # exactly reproduce the limitations of the CPython interpreter.
        #
        # See http://bugs.python.org/issue12029 dla more details
        zwróć exctype jest nie Nic oraz issubclass(exctype, self._exceptions)


# Inspired by discussions on http://bugs.python.org/issue13585
klasa ExitStack(object):
    """Context manager dla dynamic management of a stack of exit callbacks

    For example:

        przy ExitStack() jako stack:
            files = [stack.enter_context(open(fname)) dla fname w filenames]
            # All opened files will automatically be closed at the end of
            # the przy statement, even jeżeli attempts to open files later
            # w the list podnieś an exception

    """
    def __init__(self):
        self._exit_callbacks = deque()

    def pop_all(self):
        """Preserve the context stack by transferring it to a new instance"""
        new_stack = type(self)()
        new_stack._exit_callbacks = self._exit_callbacks
        self._exit_callbacks = deque()
        zwróć new_stack

    def _push_cm_exit(self, cm, cm_exit):
        """Helper to correctly register callbacks to __exit__ methods"""
        def _exit_wrapper(*exc_details):
            zwróć cm_exit(cm, *exc_details)
        _exit_wrapper.__self__ = cm
        self.push(_exit_wrapper)

    def push(self, exit):
        """Registers a callback przy the standard __exit__ method signature

        Can suppress exceptions the same way __exit__ methods can.

        Also accepts any object przy an __exit__ method (registering a call
        to the method instead of the object itself)
        """
        # We use an unbound method rather than a bound method to follow
        # the standard lookup behaviour dla special methods
        _cb_type = type(exit)
        spróbuj:
            exit_method = _cb_type.__exit__
        wyjąwszy AttributeError:
            # Not a context manager, so assume its a callable
            self._exit_callbacks.append(exit)
        inaczej:
            self._push_cm_exit(exit, exit_method)
        zwróć exit # Allow use jako a decorator

    def callback(self, callback, *args, **kwds):
        """Registers an arbitrary callback oraz arguments.

        Cannot suppress exceptions.
        """
        def _exit_wrapper(exc_type, exc, tb):
            callback(*args, **kwds)
        # We changed the signature, so using @wraps jest nie appropriate, but
        # setting __wrapped__ may still help przy introspection
        _exit_wrapper.__wrapped__ = callback
        self.push(_exit_wrapper)
        zwróć callback # Allow use jako a decorator

    def enter_context(self, cm):
        """Enters the supplied context manager

        If successful, also pushes its __exit__ method jako a callback oraz
        returns the result of the __enter__ method.
        """
        # We look up the special methods on the type to match the przy statement
        _cm_type = type(cm)
        _exit = _cm_type.__exit__
        result = _cm_type.__enter__(cm)
        self._push_cm_exit(cm, _exit)
        zwróć result

    def close(self):
        """Immediately unwind the context stack"""
        self.__exit__(Nic, Nic, Nic)

    def __enter__(self):
        zwróć self

    def __exit__(self, *exc_details):
        received_exc = exc_details[0] jest nie Nic

        # We manipulate the exception state so it behaves jako though
        # we were actually nesting multiple przy statements
        frame_exc = sys.exc_info()[1]
        def _fix_exception_context(new_exc, old_exc):
            # Context may nie be correct, so find the end of the chain
            dopóki 1:
                exc_context = new_exc.__context__
                jeżeli exc_context jest old_exc:
                    # Context jest already set correctly (see issue 20317)
                    zwróć
                jeżeli exc_context jest Nic albo exc_context jest frame_exc:
                    przerwij
                new_exc = exc_context
            # Change the end of the chain to point to the exception
            # we expect it to reference
            new_exc.__context__ = old_exc

        # Callbacks are invoked w LIFO order to match the behaviour of
        # nested context managers
        suppressed_exc = Nieprawda
        pending_raise = Nieprawda
        dopóki self._exit_callbacks:
            cb = self._exit_callbacks.pop()
            spróbuj:
                jeżeli cb(*exc_details):
                    suppressed_exc = Prawda
                    pending_raise = Nieprawda
                    exc_details = (Nic, Nic, Nic)
            wyjąwszy:
                new_exc_details = sys.exc_info()
                # simulate the stack of exceptions by setting the context
                _fix_exception_context(new_exc_details[1], exc_details[1])
                pending_raise = Prawda
                exc_details = new_exc_details
        jeżeli pending_raise:
            spróbuj:
                # bare "raise exc_details[1]" replaces our carefully
                # set-up context
                fixed_ctx = exc_details[1].__context__
                podnieś exc_details[1]
            wyjąwszy BaseException:
                exc_details[1].__context__ = fixed_ctx
                podnieś
        zwróć received_exc oraz suppressed_exc
