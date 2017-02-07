"""HMAC (Keyed-Hashing dla Message Authentication) Python module.

Implements the HMAC algorithm jako described by RFC 2104.
"""

zaimportuj warnings jako _warnings
z _operator zaimportuj _compare_digest jako compare_digest
zaimportuj hashlib jako _hashlib

trans_5C = bytes((x ^ 0x5C) dla x w range(256))
trans_36 = bytes((x ^ 0x36) dla x w range(256))

# The size of the digests returned by HMAC depends on the underlying
# hashing module used.  Use digest_size z the instance of HMAC instead.
digest_size = Nic



klasa HMAC:
    """RFC 2104 HMAC class.  Also complies przy RFC 4231.

    This supports the API dla Cryptographic Hash Functions (PEP 247).
    """
    blocksize = 64  # 512-bit HMAC; can be changed w subclasses.

    def __init__(self, key, msg = Nic, digestmod = Nic):
        """Create a new HMAC object.

        key:       key dla the keyed hash object.
        msg:       Initial input dla the hash, jeżeli provided.
        digestmod: A module supporting PEP 247.  *OR*
                   A hashlib constructor returning a new hash object. *OR*
                   A hash name suitable dla hashlib.new().
                   Defaults to hashlib.md5.
                   Implicit default to hashlib.md5 jest deprecated oraz will be
                   removed w Python 3.6.

        Note: key oraz msg must be a bytes albo bytearray objects.
        """

        jeżeli nie isinstance(key, (bytes, bytearray)):
            podnieś TypeError("key: expected bytes albo bytearray, but got %r" % type(key).__name__)

        jeżeli digestmod jest Nic:
            _warnings.warn("HMAC() without an explicit digestmod argument "
                           "is deprecated.", PendingDeprecationWarning, 2)
            digestmod = _hashlib.md5

        jeżeli callable(digestmod):
            self.digest_cons = digestmod
        albo_inaczej isinstance(digestmod, str):
            self.digest_cons = lambda d=b'': _hashlib.new(digestmod, d)
        inaczej:
            self.digest_cons = lambda d=b'': digestmod.new(d)

        self.outer = self.digest_cons()
        self.inner = self.digest_cons()
        self.digest_size = self.inner.digest_size

        jeżeli hasattr(self.inner, 'block_size'):
            blocksize = self.inner.block_size
            jeżeli blocksize < 16:
                _warnings.warn('block_size of %d seems too small; using our '
                               'default of %d.' % (blocksize, self.blocksize),
                               RuntimeWarning, 2)
                blocksize = self.blocksize
        inaczej:
            _warnings.warn('No block_size attribute on given digest object; '
                           'Assuming %d.' % (self.blocksize),
                           RuntimeWarning, 2)
            blocksize = self.blocksize

        # self.blocksize jest the default blocksize. self.block_size jest
        # effective block size jako well jako the public API attribute.
        self.block_size = blocksize

        jeżeli len(key) > blocksize:
            key = self.digest_cons(key).digest()

        key = key + bytes(blocksize - len(key))
        self.outer.update(key.translate(trans_5C))
        self.inner.update(key.translate(trans_36))
        jeżeli msg jest nie Nic:
            self.update(msg)

    @property
    def name(self):
        zwróć "hmac-" + self.inner.name

    def update(self, msg):
        """Update this hashing object przy the string msg.
        """
        self.inner.update(msg)

    def copy(self):
        """Return a separate copy of this hashing object.

        An update to this copy won't affect the original object.
        """
        # Call __new__ directly to avoid the expensive __init__.
        other = self.__class__.__new__(self.__class__)
        other.digest_cons = self.digest_cons
        other.digest_size = self.digest_size
        other.inner = self.inner.copy()
        other.outer = self.outer.copy()
        zwróć other

    def _current(self):
        """Return a hash object dla the current state.

        To be used only internally przy digest() oraz hexdigest().
        """
        h = self.outer.copy()
        h.update(self.inner.digest())
        zwróć h

    def digest(self):
        """Return the hash value of this hashing object.

        This returns a string containing 8-bit data.  The object jest
        nie altered w any way by this function; you can kontynuuj
        updating the object after calling this function.
        """
        h = self._current()
        zwróć h.digest()

    def hexdigest(self):
        """Like digest(), but returns a string of hexadecimal digits instead.
        """
        h = self._current()
        zwróć h.hexdigest()

def new(key, msg = Nic, digestmod = Nic):
    """Create a new hashing object oraz zwróć it.

    key: The starting key dla the hash.
    msg: jeżeli available, will immediately be hashed into the object's starting
    state.

    You can now feed arbitrary strings into the object using its update()
    method, oraz can ask dla the hash value at any time by calling its digest()
    method.
    """
    zwróć HMAC(key, msg, digestmod)
