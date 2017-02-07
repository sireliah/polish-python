"""The machinery of importlib: finders, loaders, hooks, etc."""

zaimportuj _imp

z ._bootstrap zaimportuj ModuleSpec
z ._bootstrap zaimportuj BuiltinImporter
z ._bootstrap zaimportuj FrozenImporter
z ._bootstrap_external zaimportuj (SOURCE_SUFFIXES, DEBUG_BYTECODE_SUFFIXES,
                     OPTIMIZED_BYTECODE_SUFFIXES, BYTECODE_SUFFIXES,
                     EXTENSION_SUFFIXES)
z ._bootstrap_external zaimportuj WindowsRegistryFinder
z ._bootstrap_external zaimportuj PathFinder
z ._bootstrap_external zaimportuj FileFinder
z ._bootstrap_external zaimportuj SourceFileLoader
z ._bootstrap_external zaimportuj SourcelessFileLoader
z ._bootstrap_external zaimportuj ExtensionFileLoader


def all_suffixes():
    """Returns a list of all recognized module suffixes dla this process"""
    zwróć SOURCE_SUFFIXES + BYTECODE_SUFFIXES + EXTENSION_SUFFIXES
