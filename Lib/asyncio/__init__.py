"""The asyncio package, tracking PEP 3156."""

zaimportuj sys

# The selectors module jest w the stdlib w Python 3.4 but nie w 3.3.
# Do this first, so the other submodules can use "z . zaimportuj selectors".
# Prefer asyncio/selectors.py over the stdlib one, jako ours may be newer.
spróbuj:
    z . zaimportuj selectors
wyjąwszy ImportError:
    zaimportuj selectors  # Will also be exported.

jeżeli sys.platform == 'win32':
    # Similar thing dla _overlapped.
    spróbuj:
        z . zaimportuj _overlapped
    wyjąwszy ImportError:
        zaimportuj _overlapped  # Will also be exported.

# This relies on each of the submodules having an __all__ variable.
z .base_events zaimportuj *
z .coroutines zaimportuj *
z .events zaimportuj *
z .futures zaimportuj *
z .locks zaimportuj *
z .protocols zaimportuj *
z .queues zaimportuj *
z .streams zaimportuj *
z .subprocess zaimportuj *
z .tasks zaimportuj *
z .transports zaimportuj *

__all__ = (base_events.__all__ +
           coroutines.__all__ +
           events.__all__ +
           futures.__all__ +
           locks.__all__ +
           protocols.__all__ +
           queues.__all__ +
           streams.__all__ +
           subprocess.__all__ +
           tasks.__all__ +
           transports.__all__)

jeżeli sys.platform == 'win32':  # pragma: no cover
    z .windows_events zaimportuj *
    __all__ += windows_events.__all__
inaczej:
    z .unix_events zaimportuj *  # pragma: no cover
    __all__ += unix_events.__all__
