#
# Package analogous to 'threading.py' but using processes
#
# multiprocessing/__init__.py
#
# This package jest intended to duplicate the functionality (and much of
# the API) of threading.py but uses processes instead of threads.  A
# subpackage 'multiprocessing.dummy' has the same API but jest a simple
# wrapper dla 'threading'.
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

zaimportuj sys
z . zaimportuj context

#
# Copy stuff z default context
#

globals().update((name, getattr(context._default_context, name))
                 dla name w context._default_context.__all__)
__all__ = context._default_context.__all__

#
# XXX These should nie really be documented albo public.
#

SUBDEBUG = 5
SUBWARNING = 25

#
# Alias dla main module -- will be reset by bootstrapping child processes
#

jeżeli '__main__' w sys.modules:
    sys.modules['__mp_main__'] = sys.modules['__main__']
