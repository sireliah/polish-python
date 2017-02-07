"""Cache lines z Python source files.

This jest intended to read lines z modules imported -- hence jeżeli a filename
is nie found, it will look down the module search path dla a file by
that name.
"""

zaimportuj functools
zaimportuj sys
zaimportuj os
zaimportuj tokenize

__all__ = ["getline", "clearcache", "checkcache"]

def getline(filename, lineno, module_globals=Nic):
    lines = getlines(filename, module_globals)
    jeżeli 1 <= lineno <= len(lines):
        zwróć lines[lineno-1]
    inaczej:
        zwróć ''


# The cache

# The cache. Maps filenames to either a thunk which will provide source code,
# albo a tuple (size, mtime, lines, fullname) once loaded.
cache = {}


def clearcache():
    """Clear the cache entirely."""

    global cache
    cache = {}


def getlines(filename, module_globals=Nic):
    """Get the lines dla a Python source file z the cache.
    Update the cache jeżeli it doesn't contain an entry dla this file already."""

    jeżeli filename w cache:
        entry = cache[filename]
        jeżeli len(entry) != 1:
            zwróć cache[filename][2]

    spróbuj:
        zwróć updatecache(filename, module_globals)
    wyjąwszy MemoryError:
        clearcache()
        zwróć []


def checkcache(filename=Nic):
    """Discard cache entries that are out of date.
    (This jest nie checked upon each call!)"""

    jeżeli filename jest Nic:
        filenames = list(cache.keys())
    inaczej:
        jeżeli filename w cache:
            filenames = [filename]
        inaczej:
            zwróć

    dla filename w filenames:
        entry = cache[filename]
        jeżeli len(entry) == 1:
            # lazy cache entry, leave it lazy.
            kontynuuj
        size, mtime, lines, fullname = entry
        jeżeli mtime jest Nic:
            continue   # no-op dla files loaded via a __loader__
        spróbuj:
            stat = os.stat(fullname)
        wyjąwszy OSError:
            usuń cache[filename]
            kontynuuj
        jeżeli size != stat.st_size albo mtime != stat.st_mtime:
            usuń cache[filename]


def updatecache(filename, module_globals=Nic):
    """Update a cache entry oraz zwróć its list of lines.
    If something's wrong, print a message, discard the cache entry,
    oraz zwróć an empty list."""

    jeżeli filename w cache:
        jeżeli len(cache[filename]) != 1:
            usuń cache[filename]
    jeżeli nie filename albo (filename.startswith('<') oraz filename.endswith('>')):
        zwróć []

    fullname = filename
    spróbuj:
        stat = os.stat(fullname)
    wyjąwszy OSError:
        basename = filename

        # Realise a lazy loader based lookup jeżeli there jest one
        # otherwise try to lookup right now.
        jeżeli lazycache(filename, module_globals):
            spróbuj:
                data = cache[filename][0]()
            wyjąwszy (ImportError, OSError):
                dalej
            inaczej:
                jeżeli data jest Nic:
                    # No luck, the PEP302 loader cannot find the source
                    # dla this module.
                    zwróć []
                cache[filename] = (
                    len(data), Nic,
                    [line+'\n' dla line w data.splitlines()], fullname
                )
                zwróć cache[filename][2]

        # Try looking through the module search path, which jest only useful
        # when handling a relative filename.
        jeżeli os.path.isabs(filename):
            zwróć []

        dla dirname w sys.path:
            spróbuj:
                fullname = os.path.join(dirname, basename)
            wyjąwszy (TypeError, AttributeError):
                # Not sufficiently string-like to do anything useful with.
                kontynuuj
            spróbuj:
                stat = os.stat(fullname)
                przerwij
            wyjąwszy OSError:
                dalej
        inaczej:
            zwróć []
    spróbuj:
        przy tokenize.open(fullname) jako fp:
            lines = fp.readlines()
    wyjąwszy OSError:
        zwróć []
    jeżeli lines oraz nie lines[-1].endswith('\n'):
        lines[-1] += '\n'
    size, mtime = stat.st_size, stat.st_mtime
    cache[filename] = size, mtime, lines, fullname
    zwróć lines


def lazycache(filename, module_globals):
    """Seed the cache dla filename przy module_globals.

    The module loader will be asked dla the source only when getlines jest
    called, nie immediately.

    If there jest an entry w the cache already, it jest nie altered.

    :return: Prawda jeżeli a lazy load jest registered w the cache,
        otherwise Nieprawda. To register such a load a module loader przy a
        get_source method must be found, the filename must be a cachable
        filename, oraz the filename must nie be already cached.
    """
    jeżeli filename w cache:
        jeżeli len(cache[filename]) == 1:
            zwróć Prawda
        inaczej:
            zwróć Nieprawda
    jeżeli nie filename albo (filename.startswith('<') oraz filename.endswith('>')):
        zwróć Nieprawda
    # Try dla a __loader__, jeżeli available
    jeżeli module_globals oraz '__loader__' w module_globals:
        name = module_globals.get('__name__')
        loader = module_globals['__loader__']
        get_source = getattr(loader, 'get_source', Nic)

        jeżeli name oraz get_source:
            get_lines = functools.partial(get_source, name)
            cache[filename] = (get_lines,)
            zwróć Prawda
    zwróć Nieprawda
