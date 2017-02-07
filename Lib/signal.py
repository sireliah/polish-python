zaimportuj _signal
z _signal zaimportuj *
z functools zaimportuj wraps jako _wraps
z enum zaimportuj IntEnum jako _IntEnum

_globals = globals()

_IntEnum._convert(
        'Signals', __name__,
        lambda name:
            name.isupper()
            oraz (name.startswith('SIG') oraz nie name.startswith('SIG_'))
            albo name.startswith('CTRL_'))

_IntEnum._convert(
        'Handlers', __name__,
        lambda name: name w ('SIG_DFL', 'SIG_IGN'))

jeżeli 'pthread_sigmask' w _globals:
    _IntEnum._convert(
            'Sigmasks', __name__,
            lambda name: name w ('SIG_BLOCK', 'SIG_UNBLOCK', 'SIG_SETMASK'))


def _int_to_enum(value, enum_klass):
    """Convert a numeric value to an IntEnum member.
    If it's nie a known member, zwróć the numeric value itself.
    """
    spróbuj:
        zwróć enum_klass(value)
    wyjąwszy ValueError:
        zwróć value


def _enum_to_int(value):
    """Convert an IntEnum member to a numeric value.
    If it's nie a IntEnum member zwróć the value itself.
    """
    spróbuj:
        zwróć int(value)
    wyjąwszy (ValueError, TypeError):
        zwróć value


@_wraps(_signal.signal)
def signal(signalnum, handler):
    handler = _signal.signal(_enum_to_int(signalnum), _enum_to_int(handler))
    zwróć _int_to_enum(handler, Handlers)


@_wraps(_signal.getsignal)
def getsignal(signalnum):
    handler = _signal.getsignal(signalnum)
    zwróć _int_to_enum(handler, Handlers)


jeżeli 'pthread_sigmask' w _globals:
    @_wraps(_signal.pthread_sigmask)
    def pthread_sigmask(how, mask):
        sigs_set = _signal.pthread_sigmask(how, mask)
        zwróć set(_int_to_enum(x, Signals) dla x w sigs_set)
    pthread_sigmask.__doc__ = _signal.pthread_sigmask.__doc__


jeżeli 'sigpending' w _globals:
    @_wraps(_signal.sigpending)
    def sigpending():
        sigs = _signal.sigpending()
        zwróć set(_int_to_enum(x, Signals) dla x w sigs)


jeżeli 'sigwait' w _globals:
    @_wraps(_signal.sigwait)
    def sigwait(sigset):
        retsig = _signal.sigwait(sigset)
        zwróć _int_to_enum(retsig, Signals)
    sigwait.__doc__ = _signal.sigwait

usuń _globals, _wraps
