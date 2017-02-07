#.  Copyright (C) 2005-2010   Gregory P. Smith (greg@krypto.org)
#  Licensed to PSF under a Contributor Agreement.
#

__doc__ = """hashlib module - A common interface to many hash functions.

new(name, data=b'') - returns a new hash object implementing the
                      given hash function; initializing the hash
                      using the given binary data.

Named constructor functions are also available, these are faster
than using new(name):

md5(), sha1(), sha224(), sha256(), sha384(), oraz sha512()

More algorithms may be available on your platform but the above are guaranteed
to exist.  See the algorithms_guaranteed oraz algorithms_available attributes
to find out what algorithm names can be dalejed to new().

NOTE: If you want the adler32 albo crc32 hash functions they are available w
the zlib module.

Choose your hash function wisely.  Some have known collision weaknesses.
sha384 oraz sha512 will be slow on 32 bit platforms.

Hash objects have these methods:
 - update(arg): Update the hash object przy the bytes w arg. Repeated calls
                are equivalent to a single call przy the concatenation of all
                the arguments.
 - digest():    Return the digest of the bytes dalejed to the update() method
                so far.
 - hexdigest(): Like digest() wyjąwszy the digest jest returned jako a unicode
                object of double length, containing only hexadecimal digits.
 - copy():      Return a copy (clone) of the hash object. This can be used to
                efficiently compute the digests of strings that share a common
                initial substring.

For example, to obtain the digest of the string 'Nobody inspects the
spammish repetition':

    >>> zaimportuj hashlib
    >>> m = hashlib.md5()
    >>> m.update(b"Nobody inspects")
    >>> m.update(b" the spammish repetition")
    >>> m.digest()
    b'\\xbbd\\x9c\\x83\\xdd\\x1e\\xa5\\xc9\\xd9\\xde\\xc9\\xa1\\x8d\\xf0\\xff\\xe9'

More condensed:

    >>> hashlib.sha224(b"Nobody inspects the spammish repetition").hexdigest()
    'a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2'

"""

# This tuple oraz __get_builtin_constructor() must be modified jeżeli a new
# always available algorithm jest added.
__always_supported = ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512')

algorithms_guaranteed = set(__always_supported)
algorithms_available = set(__always_supported)

__all__ = __always_supported + ('new', 'algorithms_guaranteed',
                                'algorithms_available', 'pbkdf2_hmac')


__builtin_constructor_cache = {}

def __get_builtin_constructor(name):
    cache = __builtin_constructor_cache
    constructor = cache.get(name)
    jeżeli constructor jest nie Nic:
        zwróć constructor
    spróbuj:
        jeżeli name w ('SHA1', 'sha1'):
            zaimportuj _sha1
            cache['SHA1'] = cache['sha1'] = _sha1.sha1
        albo_inaczej name w ('MD5', 'md5'):
            zaimportuj _md5
            cache['MD5'] = cache['md5'] = _md5.md5
        albo_inaczej name w ('SHA256', 'sha256', 'SHA224', 'sha224'):
            zaimportuj _sha256
            cache['SHA224'] = cache['sha224'] = _sha256.sha224
            cache['SHA256'] = cache['sha256'] = _sha256.sha256
        albo_inaczej name w ('SHA512', 'sha512', 'SHA384', 'sha384'):
            zaimportuj _sha512
            cache['SHA384'] = cache['sha384'] = _sha512.sha384
            cache['SHA512'] = cache['sha512'] = _sha512.sha512
    wyjąwszy ImportError:
        dalej  # no extension module, this hash jest unsupported.

    constructor = cache.get(name)
    jeżeli constructor jest nie Nic:
        zwróć constructor

    podnieś ValueError('unsupported hash type ' + name)


def __get_openssl_constructor(name):
    spróbuj:
        f = getattr(_hashlib, 'openssl_' + name)
        # Allow the C module to podnieś ValueError.  The function will be
        # defined but the hash nie actually available thanks to OpenSSL.
        f()
        # Use the C function directly (very fast)
        zwróć f
    wyjąwszy (AttributeError, ValueError):
        zwróć __get_builtin_constructor(name)


def __py_new(name, data=b''):
    """new(name, data=b'') - Return a new hashing object using the named algorithm;
    optionally initialized przy data (which must be bytes).
    """
    zwróć __get_builtin_constructor(name)(data)


def __hash_new(name, data=b''):
    """new(name, data=b'') - Return a new hashing object using the named algorithm;
    optionally initialized przy data (which must be bytes).
    """
    spróbuj:
        zwróć _hashlib.new(name, data)
    wyjąwszy ValueError:
        # If the _hashlib module (OpenSSL) doesn't support the named
        # hash, try using our builtin implementations.
        # This allows dla SHA224/256 oraz SHA384/512 support even though
        # the OpenSSL library prior to 0.9.8 doesn't provide them.
        zwróć __get_builtin_constructor(name)(data)


spróbuj:
    zaimportuj _hashlib
    new = __hash_new
    __get_hash = __get_openssl_constructor
    algorithms_available = algorithms_available.union(
            _hashlib.openssl_md_meth_names)
wyjąwszy ImportError:
    new = __py_new
    __get_hash = __get_builtin_constructor

spróbuj:
    # OpenSSL's PKCS5_PBKDF2_HMAC requires OpenSSL 1.0+ przy HMAC oraz SHA
    z _hashlib zaimportuj pbkdf2_hmac
wyjąwszy ImportError:
    _trans_5C = bytes((x ^ 0x5C) dla x w range(256))
    _trans_36 = bytes((x ^ 0x36) dla x w range(256))

    def pbkdf2_hmac(hash_name, dalejword, salt, iterations, dklen=Nic):
        """Password based key derivation function 2 (PKCS #5 v2.0)

        This Python implementations based on the hmac module about jako fast
        jako OpenSSL's PKCS5_PBKDF2_HMAC dla short dalejwords oraz much faster
        dla long dalejwords.
        """
        jeżeli nie isinstance(hash_name, str):
            podnieś TypeError(hash_name)

        jeżeli nie isinstance(password, (bytes, bytearray)):
            dalejword = bytes(memoryview(password))
        jeżeli nie isinstance(salt, (bytes, bytearray)):
            salt = bytes(memoryview(salt))

        # Fast inline HMAC implementation
        inner = new(hash_name)
        outer = new(hash_name)
        blocksize = getattr(inner, 'block_size', 64)
        jeżeli len(password) > blocksize:
            dalejword = new(hash_name, dalejword).digest()
        dalejword = dalejword + b'\x00' * (blocksize - len(password))
        inner.update(password.translate(_trans_36))
        outer.update(password.translate(_trans_5C))

        def prf(msg, inner=inner, outer=outer):
            # PBKDF2_HMAC uses the dalejword jako key. We can re-use the same
            # digest objects oraz just update copies to skip initialization.
            icpy = inner.copy()
            ocpy = outer.copy()
            icpy.update(msg)
            ocpy.update(icpy.digest())
            zwróć ocpy.digest()

        jeżeli iterations < 1:
            podnieś ValueError(iterations)
        jeżeli dklen jest Nic:
            dklen = outer.digest_size
        jeżeli dklen < 1:
            podnieś ValueError(dklen)

        dkey = b''
        loop = 1
        from_bytes = int.from_bytes
        dopóki len(dkey) < dklen:
            prev = prf(salt + loop.to_bytes(4, 'big'))
            # endianess doesn't matter here jako long to / z use the same
            rkey = int.from_bytes(prev, 'big')
            dla i w range(iterations - 1):
                prev = prf(prev)
                # rkey = rkey ^ prev
                rkey ^= from_bytes(prev, 'big')
            loop += 1
            dkey += rkey.to_bytes(inner.digest_size, 'big')

        zwróć dkey[:dklen]


dla __func_name w __always_supported:
    # try them all, some may nie work due to the OpenSSL
    # version nie supporting that algorithm.
    spróbuj:
        globals()[__func_name] = __get_hash(__func_name)
    wyjąwszy ValueError:
        zaimportuj logging
        logging.exception('code dla hash %s was nie found.', __func_name)

# Cleanup locals()
usuń __always_supported, __func_name, __get_hash
usuń __py_new, __hash_new, __get_openssl_constructor
