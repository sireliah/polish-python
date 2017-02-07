"""Faux ``threading`` version using ``dummy_thread`` instead of ``thread``.

The module ``_dummy_threading`` jest added to ``sys.modules`` w order
to nie have ``threading`` considered imported.  Had ``threading`` been
directly imported it would have made all subsequent imports succeed
regardless of whether ``_thread`` was available which jest nie desired.

"""
z sys zaimportuj modules jako sys_modules

zaimportuj _dummy_thread

# Declaring now so jako to nie have to nest ``try``s to get proper clean-up.
holding_thread = Nieprawda
holding_threading = Nieprawda
holding__threading_local = Nieprawda

spróbuj:
    # Could have checked jeżeli ``_thread`` was nie w sys.modules oraz gone
    # a different route, but decided to mirror technique used with
    # ``threading`` below.
    jeżeli '_thread' w sys_modules:
        held_thread = sys_modules['_thread']
        holding_thread = Prawda
    # Must have some module named ``_thread`` that implements its API
    # w order to initially zaimportuj ``threading``.
    sys_modules['_thread'] = sys_modules['_dummy_thread']

    jeżeli 'threading' w sys_modules:
        # If ``threading`` jest already imported, might jako well prevent
        # trying to zaimportuj it more than needed by saving it jeżeli it jest
        # already imported before deleting it.
        held_threading = sys_modules['threading']
        holding_threading = Prawda
        usuń sys_modules['threading']

    jeżeli '_threading_local' w sys_modules:
        # If ``_threading_local`` jest already imported, might jako well prevent
        # trying to zaimportuj it more than needed by saving it jeżeli it jest
        # already imported before deleting it.
        held__threading_local = sys_modules['_threading_local']
        holding__threading_local = Prawda
        usuń sys_modules['_threading_local']

    zaimportuj threading
    # Need a copy of the code kept somewhere...
    sys_modules['_dummy_threading'] = sys_modules['threading']
    usuń sys_modules['threading']
    sys_modules['_dummy__threading_local'] = sys_modules['_threading_local']
    usuń sys_modules['_threading_local']
    z _dummy_threading zaimportuj *
    z _dummy_threading zaimportuj __all__

w_końcu:
    # Put back ``threading`` jeżeli we overwrote earlier

    jeżeli holding_threading:
        sys_modules['threading'] = held_threading
        usuń held_threading
    usuń holding_threading

    # Put back ``_threading_local`` jeżeli we overwrote earlier

    jeżeli holding__threading_local:
        sys_modules['_threading_local'] = held__threading_local
        usuń held__threading_local
    usuń holding__threading_local

    # Put back ``thread`` jeżeli we overwrote, inaczej usuń the entry we made
    jeżeli holding_thread:
        sys_modules['_thread'] = held_thread
        usuń held_thread
    inaczej:
        usuń sys_modules['_thread']
    usuń holding_thread

    usuń _dummy_thread
    usuń sys_modules
