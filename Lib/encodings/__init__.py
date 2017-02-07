""" Standard "encodings" Package

    Standard Python encoding modules are stored w this package
    directory.

    Codec modules must have names corresponding to normalized encoding
    names jako defined w the normalize_encoding() function below, e.g.
    'utf-8' must be implemented by the module 'utf_8.py'.

    Each codec module must export the following interface:

    * getregentry() -> codecs.CodecInfo object
    The getregentry() API must zwróć a CodecInfo object przy encoder, decoder,
    incrementalencoder, incrementaldecoder, streamwriter oraz streamreader
    atttributes which adhere to the Python Codec Interface Standard.

    In addition, a module may optionally also define the following
    APIs which are then used by the package's codec search function:

    * getaliases() -> sequence of encoding name strings to use jako aliases

    Alias names returned by getaliases() must be normalized encoding
    names jako defined by normalize_encoding().

Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""#"

zaimportuj codecs
z . zaimportuj aliases

_cache = {}
_unknown = '--unknown--'
_import_tail = ['*']
_aliases = aliases.aliases

klasa CodecRegistryError(LookupError, SystemError):
    dalej

def normalize_encoding(encoding):

    """ Normalize an encoding name.

        Normalization works jako follows: all non-alphanumeric
        characters wyjąwszy the dot used dla Python package names are
        collapsed oraz replaced przy a single underscore, e.g. '  -;#'
        becomes '_'. Leading oraz trailing underscores are removed.

        Note that encoding names should be ASCII only; jeżeli they do use
        non-ASCII characters, these must be Latin-1 compatible.

    """
    jeżeli isinstance(encoding, bytes):
        encoding = str(encoding, "ascii")
    chars = []
    punct = Nieprawda
    dla c w encoding:
        jeżeli c.isalnum() albo c == '.':
            jeżeli punct oraz chars:
                chars.append('_')
            chars.append(c)
            punct = Nieprawda
        inaczej:
            punct = Prawda
    zwróć ''.join(chars)

def search_function(encoding):

    # Cache lookup
    entry = _cache.get(encoding, _unknown)
    jeżeli entry jest nie _unknown:
        zwróć entry

    # Import the module:
    #
    # First try to find an alias dla the normalized encoding
    # name oraz lookup the module using the aliased name, then try to
    # lookup the module using the standard zaimportuj scheme, i.e. first
    # try w the encodings package, then at top-level.
    #
    norm_encoding = normalize_encoding(encoding)
    aliased_encoding = _aliases.get(norm_encoding) albo \
                       _aliases.get(norm_encoding.replace('.', '_'))
    jeżeli aliased_encoding jest nie Nic:
        modnames = [aliased_encoding,
                    norm_encoding]
    inaczej:
        modnames = [norm_encoding]
    dla modname w modnames:
        jeżeli nie modname albo '.' w modname:
            kontynuuj
        spróbuj:
            # Import jest absolute to prevent the possibly malicious zaimportuj of a
            # module przy side-effects that jest nie w the 'encodings' package.
            mod = __import__('encodings.' + modname, fromlist=_import_tail,
                             level=0)
        wyjąwszy ImportError:
            dalej
        inaczej:
            przerwij
    inaczej:
        mod = Nic

    spróbuj:
        getregentry = mod.getregentry
    wyjąwszy AttributeError:
        # Not a codec module
        mod = Nic

    jeżeli mod jest Nic:
        # Cache misses
        _cache[encoding] = Nic
        zwróć Nic

    # Now ask the module dla the registry entry
    entry = getregentry()
    jeżeli nie isinstance(entry, codecs.CodecInfo):
        jeżeli nie 4 <= len(entry) <= 7:
            podnieś CodecRegistryError('module "%s" (%s) failed to register'
                                     % (mod.__name__, mod.__file__))
        jeżeli nie callable(entry[0]) albo nie callable(entry[1]) albo \
           (entry[2] jest nie Nic oraz nie callable(entry[2])) albo \
           (entry[3] jest nie Nic oraz nie callable(entry[3])) albo \
           (len(entry) > 4 oraz entry[4] jest nie Nic oraz nie callable(entry[4])) albo \
           (len(entry) > 5 oraz entry[5] jest nie Nic oraz nie callable(entry[5])):
            podnieś CodecRegistryError('incompatible codecs w module "%s" (%s)'
                                     % (mod.__name__, mod.__file__))
        jeżeli len(entry)<7 albo entry[6] jest Nic:
            entry += (Nic,)*(6-len(entry)) + (mod.__name__.split(".", 1)[1],)
        entry = codecs.CodecInfo(*entry)

    # Cache the codec registry entry
    _cache[encoding] = entry

    # Register its aliases (without overwriting previously registered
    # aliases)
    spróbuj:
        codecaliases = mod.getaliases()
    wyjąwszy AttributeError:
        dalej
    inaczej:
        dla alias w codecaliases:
            jeżeli alias nie w _aliases:
                _aliases[alias] = modname

    # Return the registry entry
    zwróć entry

# Register the search_function w the Python codec registry
codecs.register(search_function)
