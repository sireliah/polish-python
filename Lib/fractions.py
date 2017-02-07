# Originally contributed by Sjoerd Mullender.
# Significantly modified by Jeffrey Yasskin <jyasskin at gmail.com>.

"""Fraction, infinite-precision, real numbers."""

z decimal zaimportuj Decimal
zaimportuj math
zaimportuj numbers
zaimportuj operator
zaimportuj re
zaimportuj sys

__all__ = ['Fraction', 'gcd']



def gcd(a, b):
    """Calculate the Greatest Common Divisor of a oraz b.

    Unless b==0, the result will have the same sign jako b (so that when
    b jest divided by it, the result comes out positive).
    """
    zaimportuj warnings
    warnings.warn('fractions.gcd() jest deprecated. Use math.gcd() instead.',
                  DeprecationWarning, 2)
    jeżeli type(a) jest int jest type(b):
        jeżeli (b albo a) < 0:
            zwróć -math.gcd(a, b)
        zwróć math.gcd(a, b)
    zwróć _gcd(a, b)

def _gcd(a, b):
    # Supports non-integers dla backward compatibility.
    dopóki b:
        a, b = b, a%b
    zwróć a

# Constants related to the hash implementation;  hash(x) jest based
# on the reduction of x modulo the prime _PyHASH_MODULUS.
_PyHASH_MODULUS = sys.hash_info.modulus
# Value to be used dla rationals that reduce to infinity modulo
# _PyHASH_MODULUS.
_PyHASH_INF = sys.hash_info.inf

_RATIONAL_FORMAT = re.compile(r"""
    \A\s*                      # optional whitespace at the start, then
    (?P<sign>[-+]?)            # an optional sign, then
    (?=\d|\.\d)                # lookahead dla digit albo .digit
    (?P<num>\d*)               # numerator (possibly empty)
    (?:                        # followed by
       (?:/(?P<denom>\d+))?    # an optional denominator
    |                          # albo
       (?:\.(?P<decimal>\d*))? # an optional fractional part
       (?:E(?P<exp>[-+]?\d+))? # oraz optional exponent
    )
    \s*\Z                      # oraz optional whitespace to finish
""", re.VERBOSE | re.IGNORECASE)


klasa Fraction(numbers.Rational):
    """This klasa implements rational numbers.

    In the two-argument form of the constructor, Fraction(8, 6) will
    produce a rational number equivalent to 4/3. Both arguments must
    be Rational. The numerator defaults to 0 oraz the denominator
    defaults to 1 so that Fraction(3) == 3 oraz Fraction() == 0.

    Fractions can also be constructed from:

      - numeric strings similar to those accepted by the
        float constructor (dla example, '-2.3' albo '1e10')

      - strings of the form '123/456'

      - float oraz Decimal instances

      - other Rational instances (including integers)

    """

    __slots__ = ('_numerator', '_denominator')

    # We're immutable, so use __new__ nie __init__
    def __new__(cls, numerator=0, denominator=Nic, _normalize=Prawda):
        """Constructs a Rational.

        Takes a string like '3/2' albo '1.5', another Rational instance, a
        numerator/denominator pair, albo a float.

        Examples
        --------

        >>> Fraction(10, -8)
        Fraction(-5, 4)
        >>> Fraction(Fraction(1, 7), 5)
        Fraction(1, 35)
        >>> Fraction(Fraction(1, 7), Fraction(2, 3))
        Fraction(3, 14)
        >>> Fraction('314')
        Fraction(314, 1)
        >>> Fraction('-35/4')
        Fraction(-35, 4)
        >>> Fraction('3.1415') # conversion z numeric string
        Fraction(6283, 2000)
        >>> Fraction('-47e-2') # string may include a decimal exponent
        Fraction(-47, 100)
        >>> Fraction(1.47)  # direct construction z float (exact conversion)
        Fraction(6620291452234629, 4503599627370496)
        >>> Fraction(2.25)
        Fraction(9, 4)
        >>> Fraction(Decimal('1.47'))
        Fraction(147, 100)

        """
        self = super(Fraction, cls).__new__(cls)

        jeżeli denominator jest Nic:
            jeżeli type(numerator) jest int:
                self._numerator = numerator
                self._denominator = 1
                zwróć self

            albo_inaczej isinstance(numerator, numbers.Rational):
                self._numerator = numerator.numerator
                self._denominator = numerator.denominator
                zwróć self

            albo_inaczej isinstance(numerator, float):
                # Exact conversion z float
                value = Fraction.from_float(numerator)
                self._numerator = value._numerator
                self._denominator = value._denominator
                zwróć self

            albo_inaczej isinstance(numerator, Decimal):
                value = Fraction.from_decimal(numerator)
                self._numerator = value._numerator
                self._denominator = value._denominator
                zwróć self

            albo_inaczej isinstance(numerator, str):
                # Handle construction z strings.
                m = _RATIONAL_FORMAT.match(numerator)
                jeżeli m jest Nic:
                    podnieś ValueError('Invalid literal dla Fraction: %r' %
                                     numerator)
                numerator = int(m.group('num') albo '0')
                denom = m.group('denom')
                jeżeli denom:
                    denominator = int(denom)
                inaczej:
                    denominator = 1
                    decimal = m.group('decimal')
                    jeżeli decimal:
                        scale = 10**len(decimal)
                        numerator = numerator * scale + int(decimal)
                        denominator *= scale
                    exp = m.group('exp')
                    jeżeli exp:
                        exp = int(exp)
                        jeżeli exp >= 0:
                            numerator *= 10**exp
                        inaczej:
                            denominator *= 10**-exp
                jeżeli m.group('sign') == '-':
                    numerator = -numerator

            inaczej:
                podnieś TypeError("argument should be a string "
                                "or a Rational instance")

        albo_inaczej type(numerator) jest int jest type(denominator):
            dalej # *very* normal case

        albo_inaczej (isinstance(numerator, numbers.Rational) oraz
            isinstance(denominator, numbers.Rational)):
            numerator, denominator = (
                numerator.numerator * denominator.denominator,
                denominator.numerator * numerator.denominator
                )
        inaczej:
            podnieś TypeError("both arguments should be "
                            "Rational instances")

        jeżeli denominator == 0:
            podnieś ZeroDivisionError('Fraction(%s, 0)' % numerator)
        jeżeli _normalize:
            jeżeli type(numerator) jest int jest type(denominator):
                # *very* normal case
                g = math.gcd(numerator, denominator)
                jeżeli denominator < 0:
                    g = -g
            inaczej:
                g = _gcd(numerator, denominator)
            numerator //= g
            denominator //= g
        self._numerator = numerator
        self._denominator = denominator
        zwróć self

    @classmethod
    def from_float(cls, f):
        """Converts a finite float to a rational number, exactly.

        Beware that Fraction.from_float(0.3) != Fraction(3, 10).

        """
        jeżeli isinstance(f, numbers.Integral):
            zwróć cls(f)
        albo_inaczej nie isinstance(f, float):
            podnieś TypeError("%s.from_float() only takes floats, nie %r (%s)" %
                            (cls.__name__, f, type(f).__name__))
        jeżeli math.isnan(f):
            podnieś ValueError("Cannot convert %r to %s." % (f, cls.__name__))
        jeżeli math.isinf(f):
            podnieś OverflowError("Cannot convert %r to %s." % (f, cls.__name__))
        zwróć cls(*f.as_integer_ratio())

    @classmethod
    def from_decimal(cls, dec):
        """Converts a finite Decimal instance to a rational number, exactly."""
        z decimal zaimportuj Decimal
        jeżeli isinstance(dec, numbers.Integral):
            dec = Decimal(int(dec))
        albo_inaczej nie isinstance(dec, Decimal):
            podnieś TypeError(
                "%s.from_decimal() only takes Decimals, nie %r (%s)" %
                (cls.__name__, dec, type(dec).__name__))
        jeżeli dec.is_infinite():
            podnieś OverflowError(
                "Cannot convert %s to %s." % (dec, cls.__name__))
        jeżeli dec.is_nan():
            podnieś ValueError("Cannot convert %s to %s." % (dec, cls.__name__))
        sign, digits, exp = dec.as_tuple()
        digits = int(''.join(map(str, digits)))
        jeżeli sign:
            digits = -digits
        jeżeli exp >= 0:
            zwróć cls(digits * 10 ** exp)
        inaczej:
            zwróć cls(digits, 10 ** -exp)

    def limit_denominator(self, max_denominator=1000000):
        """Closest Fraction to self przy denominator at most max_denominator.

        >>> Fraction('3.141592653589793').limit_denominator(10)
        Fraction(22, 7)
        >>> Fraction('3.141592653589793').limit_denominator(100)
        Fraction(311, 99)
        >>> Fraction(4321, 8765).limit_denominator(10000)
        Fraction(4321, 8765)

        """
        # Algorithm notes: For any real number x, define a *best upper
        # approximation* to x to be a rational number p/q such that:
        #
        #   (1) p/q >= x, oraz
        #   (2) jeżeli p/q > r/s >= x then s > q, dla any rational r/s.
        #
        # Define *best lower approximation* similarly.  Then it can be
        # proved that a rational number jest a best upper albo lower
        # approximation to x if, oraz only if, it jest a convergent albo
        # semiconvergent of the (unique shortest) continued fraction
        # associated to x.
        #
        # To find a best rational approximation przy denominator <= M,
        # we find the best upper oraz lower approximations with
        # denominator <= M oraz take whichever of these jest closer to x.
        # In the event of a tie, the bound przy smaller denominator jest
        # chosen.  If both denominators are equal (which can happen
        # only when max_denominator == 1 oraz self jest midway between
        # two integers) the lower bound---i.e., the floor of self, jest
        # taken.

        jeżeli max_denominator < 1:
            podnieś ValueError("max_denominator should be at least 1")
        jeżeli self._denominator <= max_denominator:
            zwróć Fraction(self)

        p0, q0, p1, q1 = 0, 1, 1, 0
        n, d = self._numerator, self._denominator
        dopóki Prawda:
            a = n//d
            q2 = q0+a*q1
            jeżeli q2 > max_denominator:
                przerwij
            p0, q0, p1, q1 = p1, q1, p0+a*p1, q2
            n, d = d, n-a*d

        k = (max_denominator-q0)//q1
        bound1 = Fraction(p0+k*p1, q0+k*q1)
        bound2 = Fraction(p1, q1)
        jeżeli abs(bound2 - self) <= abs(bound1-self):
            zwróć bound2
        inaczej:
            zwróć bound1

    @property
    def numerator(a):
        zwróć a._numerator

    @property
    def denominator(a):
        zwróć a._denominator

    def __repr__(self):
        """repr(self)"""
        zwróć '%s(%s, %s)' % (self.__class__.__name__,
                               self._numerator, self._denominator)

    def __str__(self):
        """str(self)"""
        jeżeli self._denominator == 1:
            zwróć str(self._numerator)
        inaczej:
            zwróć '%s/%s' % (self._numerator, self._denominator)

    def _operator_fallbacks(monomorphic_operator, fallback_operator):
        """Generates forward oraz reverse operators given a purely-rational
        operator oraz a function z the operator module.

        Use this like:
        __op__, __rop__ = _operator_fallbacks(just_rational_op, operator.op)

        In general, we want to implement the arithmetic operations so
        that mixed-mode operations either call an implementation whose
        author knew about the types of both arguments, albo convert both
        to the nearest built w type oraz do the operation there. In
        Fraction, that means that we define __add__ oraz __radd__ as:

            def __add__(self, other):
                # Both types have numerators/denominator attributes,
                # so do the operation directly
                jeżeli isinstance(other, (int, Fraction)):
                    zwróć Fraction(self.numerator * other.denominator +
                                    other.numerator * self.denominator,
                                    self.denominator * other.denominator)
                # float oraz complex don't have those operations, but we
                # know about those types, so special case them.
                albo_inaczej isinstance(other, float):
                    zwróć float(self) + other
                albo_inaczej isinstance(other, complex):
                    zwróć complex(self) + other
                # Let the other type take over.
                zwróć NotImplemented

            def __radd__(self, other):
                # radd handles more types than add because there's
                # nothing left to fall back to.
                jeżeli isinstance(other, numbers.Rational):
                    zwróć Fraction(self.numerator * other.denominator +
                                    other.numerator * self.denominator,
                                    self.denominator * other.denominator)
                albo_inaczej isinstance(other, Real):
                    zwróć float(other) + float(self)
                albo_inaczej isinstance(other, Complex):
                    zwróć complex(other) + complex(self)
                zwróć NotImplemented


        There are 5 different cases dla a mixed-type addition on
        Fraction. I'll refer to all of the above code that doesn't
        refer to Fraction, float, albo complex jako "boilerplate". 'r'
        will be an instance of Fraction, which jest a subtype of
        Rational (r : Fraction <: Rational), oraz b : B <:
        Complex. The first three involve 'r + b':

            1. If B <: Fraction, int, float, albo complex, we handle
               that specially, oraz all jest well.
            2. If Fraction falls back to the boilerplate code, oraz it
               were to zwróć a value z __add__, we'd miss the
               possibility that B defines a more intelligent __radd__,
               so the boilerplate should zwróć NotImplemented from
               __add__. In particular, we don't handle Rational
               here, even though we could get an exact answer, w case
               the other type wants to do something special.
            3. If B <: Fraction, Python tries B.__radd__ before
               Fraction.__add__. This jest ok, because it was
               implemented przy knowledge of Fraction, so it can
               handle those instances before delegating to Real albo
               Complex.

        The next two situations describe 'b + r'. We assume that b
        didn't know about Fraction w its implementation, oraz that it
        uses similar boilerplate code:

            4. If B <: Rational, then __radd_ converts both to the
               builtin rational type (hey look, that's us) oraz
               proceeds.
            5. Otherwise, __radd__ tries to find the nearest common
               base ABC, oraz fall back to its builtin type. Since this
               klasa doesn't subclass a concrete type, there's no
               implementation to fall back to, so we need to try as
               hard jako possible to zwróć an actual value, albo the user
               will get a TypeError.

        """
        def forward(a, b):
            jeżeli isinstance(b, (int, Fraction)):
                zwróć monomorphic_operator(a, b)
            albo_inaczej isinstance(b, float):
                zwróć fallback_operator(float(a), b)
            albo_inaczej isinstance(b, complex):
                zwróć fallback_operator(complex(a), b)
            inaczej:
                zwróć NotImplemented
        forward.__name__ = '__' + fallback_operator.__name__ + '__'
        forward.__doc__ = monomorphic_operator.__doc__

        def reverse(b, a):
            jeżeli isinstance(a, numbers.Rational):
                # Includes ints.
                zwróć monomorphic_operator(a, b)
            albo_inaczej isinstance(a, numbers.Real):
                zwróć fallback_operator(float(a), float(b))
            albo_inaczej isinstance(a, numbers.Complex):
                zwróć fallback_operator(complex(a), complex(b))
            inaczej:
                zwróć NotImplemented
        reverse.__name__ = '__r' + fallback_operator.__name__ + '__'
        reverse.__doc__ = monomorphic_operator.__doc__

        zwróć forward, reverse

    def _add(a, b):
        """a + b"""
        da, db = a.denominator, b.denominator
        zwróć Fraction(a.numerator * db + b.numerator * da,
                        da * db)

    __add__, __radd__ = _operator_fallbacks(_add, operator.add)

    def _sub(a, b):
        """a - b"""
        da, db = a.denominator, b.denominator
        zwróć Fraction(a.numerator * db - b.numerator * da,
                        da * db)

    __sub__, __rsub__ = _operator_fallbacks(_sub, operator.sub)

    def _mul(a, b):
        """a * b"""
        zwróć Fraction(a.numerator * b.numerator, a.denominator * b.denominator)

    __mul__, __rmul__ = _operator_fallbacks(_mul, operator.mul)

    def _div(a, b):
        """a / b"""
        zwróć Fraction(a.numerator * b.denominator,
                        a.denominator * b.numerator)

    __truediv__, __rtruediv__ = _operator_fallbacks(_div, operator.truediv)

    def __floordiv__(a, b):
        """a // b"""
        zwróć math.floor(a / b)

    def __rfloordiv__(b, a):
        """a // b"""
        zwróć math.floor(a / b)

    def __mod__(a, b):
        """a % b"""
        div = a // b
        zwróć a - b * div

    def __rmod__(b, a):
        """a % b"""
        div = a // b
        zwróć a - b * div

    def __pow__(a, b):
        """a ** b

        If b jest nie an integer, the result will be a float albo complex
        since roots are generally irrational. If b jest an integer, the
        result will be rational.

        """
        jeżeli isinstance(b, numbers.Rational):
            jeżeli b.denominator == 1:
                power = b.numerator
                jeżeli power >= 0:
                    zwróć Fraction(a._numerator ** power,
                                    a._denominator ** power,
                                    _normalize=Nieprawda)
                inaczej:
                    zwróć Fraction(a._denominator ** -power,
                                    a._numerator ** -power,
                                    _normalize=Nieprawda)
            inaczej:
                # A fractional power will generally produce an
                # irrational number.
                zwróć float(a) ** float(b)
        inaczej:
            zwróć float(a) ** b

    def __rpow__(b, a):
        """a ** b"""
        jeżeli b._denominator == 1 oraz b._numerator >= 0:
            # If a jest an int, keep it that way jeżeli possible.
            zwróć a ** b._numerator

        jeżeli isinstance(a, numbers.Rational):
            zwróć Fraction(a.numerator, a.denominator) ** b

        jeżeli b._denominator == 1:
            zwróć a ** b._numerator

        zwróć a ** float(b)

    def __pos__(a):
        """+a: Coerces a subclass instance to Fraction"""
        zwróć Fraction(a._numerator, a._denominator, _normalize=Nieprawda)

    def __neg__(a):
        """-a"""
        zwróć Fraction(-a._numerator, a._denominator, _normalize=Nieprawda)

    def __abs__(a):
        """abs(a)"""
        zwróć Fraction(abs(a._numerator), a._denominator, _normalize=Nieprawda)

    def __trunc__(a):
        """trunc(a)"""
        jeżeli a._numerator < 0:
            zwróć -(-a._numerator // a._denominator)
        inaczej:
            zwróć a._numerator // a._denominator

    def __floor__(a):
        """Will be math.floor(a) w 3.0."""
        zwróć a.numerator // a.denominator

    def __ceil__(a):
        """Will be math.ceil(a) w 3.0."""
        # The negations cleverly convince floordiv to zwróć the ceiling.
        zwróć -(-a.numerator // a.denominator)

    def __round__(self, ndigits=Nic):
        """Will be round(self, ndigits) w 3.0.

        Rounds half toward even.
        """
        jeżeli ndigits jest Nic:
            floor, remainder = divmod(self.numerator, self.denominator)
            jeżeli remainder * 2 < self.denominator:
                zwróć floor
            albo_inaczej remainder * 2 > self.denominator:
                zwróć floor + 1
            # Deal przy the half case:
            albo_inaczej floor % 2 == 0:
                zwróć floor
            inaczej:
                zwróć floor + 1
        shift = 10**abs(ndigits)
        # See _operator_fallbacks.forward to check that the results of
        # these operations will always be Fraction oraz therefore have
        # round().
        jeżeli ndigits > 0:
            zwróć Fraction(round(self * shift), shift)
        inaczej:
            zwróć Fraction(round(self / shift) * shift)

    def __hash__(self):
        """hash(self)"""

        # XXX since this method jest expensive, consider caching the result

        # In order to make sure that the hash of a Fraction agrees
        # przy the hash of a numerically equal integer, float albo
        # Decimal instance, we follow the rules dla numeric hashes
        # outlined w the documentation.  (See library docs, 'Built-in
        # Types').

        # dinv jest the inverse of self._denominator modulo the prime
        # _PyHASH_MODULUS, albo 0 jeżeli self._denominator jest divisible by
        # _PyHASH_MODULUS.
        dinv = pow(self._denominator, _PyHASH_MODULUS - 2, _PyHASH_MODULUS)
        jeżeli nie dinv:
            hash_ = _PyHASH_INF
        inaczej:
            hash_ = abs(self._numerator) * dinv % _PyHASH_MODULUS
        result = hash_ jeżeli self >= 0 inaczej -hash_
        zwróć -2 jeżeli result == -1 inaczej result

    def __eq__(a, b):
        """a == b"""
        jeżeli type(b) jest int:
            zwróć a._numerator == b oraz a._denominator == 1
        jeżeli isinstance(b, numbers.Rational):
            zwróć (a._numerator == b.numerator oraz
                    a._denominator == b.denominator)
        jeżeli isinstance(b, numbers.Complex) oraz b.imag == 0:
            b = b.real
        jeżeli isinstance(b, float):
            jeżeli math.isnan(b) albo math.isinf(b):
                # comparisons przy an infinity albo nan should behave w
                # the same way dla any finite a, so treat a jako zero.
                zwróć 0.0 == b
            inaczej:
                zwróć a == a.from_float(b)
        inaczej:
            # Since a doesn't know how to compare przy b, let's give b
            # a chance to compare itself przy a.
            zwróć NotImplemented

    def _richcmp(self, other, op):
        """Helper dla comparison operators, dla internal use only.

        Implement comparison between a Rational instance `self`, oraz
        either another Rational instance albo a float `other`.  If
        `other` jest nie a Rational instance albo a float, zwróć
        NotImplemented. `op` should be one of the six standard
        comparison operators.

        """
        # convert other to a Rational instance where reasonable.
        jeżeli isinstance(other, numbers.Rational):
            zwróć op(self._numerator * other.denominator,
                      self._denominator * other.numerator)
        jeżeli isinstance(other, float):
            jeżeli math.isnan(other) albo math.isinf(other):
                zwróć op(0.0, other)
            inaczej:
                zwróć op(self, self.from_float(other))
        inaczej:
            zwróć NotImplemented

    def __lt__(a, b):
        """a < b"""
        zwróć a._richcmp(b, operator.lt)

    def __gt__(a, b):
        """a > b"""
        zwróć a._richcmp(b, operator.gt)

    def __le__(a, b):
        """a <= b"""
        zwróć a._richcmp(b, operator.le)

    def __ge__(a, b):
        """a >= b"""
        zwróć a._richcmp(b, operator.ge)

    def __bool__(a):
        """a != 0"""
        zwróć a._numerator != 0

    # support dla pickling, copy, oraz deepcopy

    def __reduce__(self):
        zwróć (self.__class__, (str(self),))

    def __copy__(self):
        jeżeli type(self) == Fraction:
            zwróć self     # I'm immutable; therefore I am my own clone
        zwróć self.__class__(self._numerator, self._denominator)

    def __deepcopy__(self, memo):
        jeżeli type(self) == Fraction:
            zwróć self     # My components are also immutable
        zwróć self.__class__(self._numerator, self._denominator)
