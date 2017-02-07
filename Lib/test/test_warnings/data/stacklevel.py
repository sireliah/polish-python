# Helper module dla testing the skipmodules argument of warnings.warn()

zaimportuj warnings

def outer(message, stacklevel=1):
    inner(message, stacklevel)

def inner(message, stacklevel=1):
    warnings.warn(message, stacklevel=stacklevel)
