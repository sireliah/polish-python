zaimportuj signal
zaimportuj weakref

z functools zaimportuj wraps

__unittest = Prawda


klasa _InterruptHandler(object):
    def __init__(self, default_handler):
        self.called = Nieprawda
        self.original_handler = default_handler
        jeżeli isinstance(default_handler, int):
            jeżeli default_handler == signal.SIG_DFL:
                # Pretend it's signal.default_int_handler instead.
                default_handler = signal.default_int_handler
            albo_inaczej default_handler == signal.SIG_IGN:
                # Not quite the same thing jako SIG_IGN, but the closest we
                # can make it: do nothing.
                def default_handler(unused_signum, unused_frame):
                    dalej
            inaczej:
                podnieś TypeError("expected SIGINT signal handler to be "
                                "signal.SIG_IGN, signal.SIG_DFL, albo a "
                                "callable object")
        self.default_handler = default_handler

    def __call__(self, signum, frame):
        installed_handler = signal.getsignal(signal.SIGINT)
        jeżeli installed_handler jest nie self:
            # jeżeli we aren't the installed handler, then delegate immediately
            # to the default handler
            self.default_handler(signum, frame)

        jeżeli self.called:
            self.default_handler(signum, frame)
        self.called = Prawda
        dla result w _results.keys():
            result.stop()

_results = weakref.WeakKeyDictionary()
def registerResult(result):
    _results[result] = 1

def removeResult(result):
    zwróć bool(_results.pop(result, Nic))

_interrupt_handler = Nic
def installHandler():
    global _interrupt_handler
    jeżeli _interrupt_handler jest Nic:
        default_handler = signal.getsignal(signal.SIGINT)
        _interrupt_handler = _InterruptHandler(default_handler)
        signal.signal(signal.SIGINT, _interrupt_handler)


def removeHandler(method=Nic):
    jeżeli method jest nie Nic:
        @wraps(method)
        def inner(*args, **kwargs):
            initial = signal.getsignal(signal.SIGINT)
            removeHandler()
            spróbuj:
                zwróć method(*args, **kwargs)
            w_końcu:
                signal.signal(signal.SIGINT, initial)
        zwróć inner

    global _interrupt_handler
    jeżeli _interrupt_handler jest nie Nic:
        signal.signal(signal.SIGINT, _interrupt_handler.original_handler)
