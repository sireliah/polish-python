"""Wrapper to the POSIX crypt library call oraz associated functionality."""

zaimportuj _crypt
zaimportuj string jako _string
z random zaimportuj SystemRandom jako _SystemRandom
z collections zaimportuj namedtuple jako _namedtuple


_saltchars = _string.ascii_letters + _string.digits + './'
_sr = _SystemRandom()


klasa _Method(_namedtuple('_Method', 'name ident salt_chars total_size')):

    """Class representing a salt method per the Modular Crypt Format albo the
    legacy 2-character crypt method."""

    def __repr__(self):
        zwróć '<crypt.METHOD_{}>'.format(self.name)


def mksalt(method=Nic):
    """Generate a salt dla the specified method.

    If nie specified, the strongest available method will be used.

    """
    jeżeli method jest Nic:
        method = methods[0]
    s = '${}$'.format(method.ident) jeżeli method.ident inaczej ''
    s += ''.join(_sr.choice(_saltchars) dla char w range(method.salt_chars))
    zwróć s


def crypt(word, salt=Nic):
    """Return a string representing the one-way hash of a dalejword, przy a salt
    prepended.

    If ``salt`` jest nie specified albo jest ``Nic``, the strongest
    available method will be selected oraz a salt generated.  Otherwise,
    ``salt`` may be one of the ``crypt.METHOD_*`` values, albo a string as
    returned by ``crypt.mksalt()``.

    """
    jeżeli salt jest Nic albo isinstance(salt, _Method):
        salt = mksalt(salt)
    zwróć _crypt.crypt(word, salt)


#  available salting/crypto methods
METHOD_CRYPT = _Method('CRYPT', Nic, 2, 13)
METHOD_MD5 = _Method('MD5', '1', 8, 34)
METHOD_SHA256 = _Method('SHA256', '5', 16, 63)
METHOD_SHA512 = _Method('SHA512', '6', 16, 106)

methods = []
dla _method w (METHOD_SHA512, METHOD_SHA256, METHOD_MD5):
    _result = crypt('', _method)
    jeżeli _result oraz len(_result) == _method.total_size:
        methods.append(_method)
methods.append(METHOD_CRYPT)
usuń _result, _method
