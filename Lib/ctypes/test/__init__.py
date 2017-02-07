zaimportuj os
zaimportuj unittest
z test zaimportuj support

# skip tests jeżeli _ctypes was nie built
ctypes = support.import_module('ctypes')
ctypes_symbols = dir(ctypes)

def need_symbol(name):
    zwróć unittest.skipUnless(name w ctypes_symbols,
                               '{!r} jest required'.format(name))

def load_tests(*args):
    zwróć support.load_package_tests(os.path.dirname(__file__), *args)
