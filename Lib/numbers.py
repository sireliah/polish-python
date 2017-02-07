# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Abstract Base Classes (ABCs) dla numbers, according to PEP 3141.

TODO: Fill out more detailed documentation on the operators."""

z abc zaimportuj ABCMeta, abstractmethod

__all__ = ["Number", "Complex", "Real", "Rational", "Integral"]

klasa Number(metaclass=ABCMeta):
    """All numbers inherit z this class.

    If you just want to check jeżeli an argument x jest a number, without
    caring what kind, use isinstance(x, Number).
    """
    __slots__ = ()

    # Concrete numeric types must provide their own hash implementation
    __hash__ = Nic


## Notes on Decimal
## ----------------
## Decimal has all of the methods specified by the Real abc, but it should
## nie be registered jako a Real because decimals do nie interoperate with
## binary floats (i.e.  Decimal('3.14') + 2.71828 jest undefined).  But,
## abstract reals are expected to interoperate (i.e. R1 + R2 should be
## expected to work jeżeli R1 oraz R2 are both Reals).

klasa Complex(Number):
    """Complex defines the operations that work on the builtin complex type.

    In short, those are: a conversion to complex, .real, .imag, +, -,
    *, /, abs(), .conjugate, ==, oraz !=.

    If it jest given heterogenous arguments, oraz doesn't have special
    knowledge about them, it should fall back to the builtin complex
    type jako described below.
    """

    __slots__ = ()

    @abstractmethod
    def __complex__(self):
        """Return a builtin complex instance. Called dla complex(self)."""

    def __bool__(self):
        """Prawda jeżeli self != 0. Called dla bool(self)."""
        zwróć self != 0

    @property
    @abstractmethod
    def real(self):
        """Retrieve the real component of this number.

        This should subclass Real.
        """
        podnieś NotImplementedError

    @property
    @abstractmethod
    def imag(self):
        """Retrieve the imaginary component of this number.

        This should subclass Real.
        """
        podnieś NotImplementedError

    @abstractmethod
    def __add__(self, other):
        """self + other"""
        podnieś NotImplementedError

    @abstractmethod
    def __radd__(self, other):
        """other + self"""
        podnieś NotImplementedError

    @abstractmethod
    def __neg__(self):
        """-self"""
        podnieś NotImplementedError

    @abstractmethod
    def __pos__(self):
        """+self"""
        podnieś NotImplementedError

    def __sub__(self, other):
        """self - other"""
        zwróć self + -other

    def __rsub__(self, other):
        """other - self"""
        zwróć -self + other

    @abstractmethod
    def __mul__(self, other):
        """self * other"""
        podnieś NotImplementedError

    @abstractmethod
    def __rmul__(self, other):
        """other * self"""
        podnieś NotImplementedError

    @abstractmethod
    def __truediv__(self, other):
        """self / other: Should promote to float when necessary."""
        podnieś NotImplementedError

    @abstractmethod
    def __rtruediv__(self, other):
        """other / self"""
        podnieś NotImplementedError

    @abstractmethod
    def __pow__(self, exponent):
        """self**exponent; should promote to float albo complex when necessary."""
        podnieś NotImplementedError

    @abstractmethod
    def __rpow__(self, base):
        """base ** self"""
        podnieś NotImplementedError

    @abstractmethod
    def __abs__(self):
        """Returns the Real distance z 0. Called dla abs(self)."""
        podnieś NotImplementedError

    @abstractmethod
    def conjugate(self):
        """(x+y*i).conjugate() returns (x-y*i)."""
        podnieś NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        """self == other"""
        podnieś NotImplementedError

Complex.register(complex)


klasa Real(Complex):
    """To Complex, Real adds the operations that work on real numbers.

    In short, those are: a conversion to float, trunc(), divmod,
    %, <, <=, >, oraz >=.

    Real also provides defaults dla the derived operations.
    """

    __slots__ = ()

    @abstractmethod
    def __float__(self):
        """Any Real can be converted to a native float object.

        Called dla float(self)."""
        podnieś NotImplementedError

    @abstractmethod
    def __trunc__(self):
        """trunc(self): Truncates self to an Integral.

        Returns an Integral i such that:
          * i>0 iff self>0;
          * abs(i) <= abs(self);
          * dla any Integral j satisfying the first two conditions,
            abs(i) >= abs(j) [i.e. i has "maximal" abs among those].
        i.e. "truncate towards 0".
        """
        podnieś NotImplementedError

    @abstractmethod
    def __floor__(self):
        """Finds the greatest Integral <= self."""
        podnieś NotImplementedError

    @abstractmethod
    def __ceil__(self):
        """Finds the least Integral >= self."""
        podnieś NotImplementedError

    @abstractmethod
    def __round__(self, ndigits=Nic):
        """Rounds self to ndigits decimal places, defaulting to 0.

        If ndigits jest omitted albo Nic, returns an Integral, otherwise
        returns a Real. Rounds half toward even.
        """
        podnieś NotImplementedError

    def __divmod__(self, other):
        """divmod(self, other): The pair (self // other, self % other).

        Sometimes this can be computed faster than the pair of
        operations.
        """
        zwróć (self // other, self % other)

    def __rdivmod__(self, other):
        """divmod(other, self): The pair (self // other, self % other).

        Sometimes this can be computed faster than the pair of
        operations.
        """
        zwróć (other // self, other % self)

    @abstractmethod
    def __floordiv__(self, other):
        """self // other: The floor() of self/other."""
        podnieś NotImplementedError

    @abstractmethod
    def __rfloordiv__(self, other):
        """other // self: The floor() of other/self."""
        podnieś NotImplementedError

    @abstractmethod
    def __mod__(self, other):
        """self % other"""
        podnieś NotImplementedError

    @abstractmethod
    def __rmod__(self, other):
        """other % self"""
        podnieś NotImplementedError

    @abstractmethod
    def __lt__(self, other):
        """self < other

        < on Reals defines a total ordering, wyjąwszy perhaps dla NaN."""
        podnieś NotImplementedError

    @abstractmethod
    def __le__(self, other):
        """self <= other"""
        podnieś NotImplementedError

    # Concrete implementations of Complex abstract methods.
    def __complex__(self):
        """complex(self) == complex(float(self), 0)"""
        zwróć complex(float(self))

    @property
    def real(self):
        """Real numbers are their real component."""
        zwróć +self

    @property
    def imag(self):
        """Real numbers have no imaginary component."""
        zwróć 0

    def conjugate(self):
        """Conjugate jest a no-op dla Reals."""
        zwróć +self

Real.register(float)


klasa Rational(Real):
    """.numerator oraz .denominator should be w lowest terms."""

    __slots__ = ()

    @property
    @abstractmethod
    def numerator(self):
        podnieś NotImplementedError

    @property
    @abstractmethod
    def denominator(self):
        podnieś NotImplementedError

    # Concrete implementation of Real's conversion to float.
    def __float__(self):
        """float(self) = self.numerator / self.denominator

        It's important that this conversion use the integer's "true"
        division rather than casting one side to float before dividing
        so that ratios of huge integers convert without overflowing.

        """
        zwróć self.numerator / self.denominator


klasa Integral(Rational):
    """Integral adds a conversion to int oraz the bit-string operations."""

    __slots__ = ()

    @abstractmethod
    def __int__(self):
        """int(self)"""
        podnieś NotImplementedError

    def __index__(self):
        """Called whenever an index jest needed, such jako w slicing"""
        zwróć int(self)

    @abstractmethod
    def __pow__(self, exponent, modulus=Nic):
        """self ** exponent % modulus, but maybe faster.

        Accept the modulus argument jeżeli you want to support the
        3-argument version of pow(). Raise a TypeError jeżeli exponent < 0
        albo any argument isn't Integral. Otherwise, just implement the
        2-argument version described w Complex.
        """
        podnieś NotImplementedError

    @abstractmethod
    def __lshift__(self, other):
        """self << other"""
        podnieś NotImplementedError

    @abstractmethod
    def __rlshift__(self, other):
        """other << self"""
        podnieś NotImplementedError

    @abstractmethod
    def __rshift__(self, other):
        """self >> other"""
        podnieś NotImplementedError

    @abstractmethod
    def __rrshift__(self, other):
        """other >> self"""
        podnieś NotImplementedError

    @abstractmethod
    def __and__(self, other):
        """self & other"""
        podnieś NotImplementedError

    @abstractmethod
    def __rand__(self, other):
        """other & self"""
        podnieś NotImplementedError

    @abstractmethod
    def __xor__(self, other):
        """self ^ other"""
        podnieś NotImplementedError

    @abstractmethod
    def __rxor__(self, other):
        """other ^ self"""
        podnieś NotImplementedError

    @abstractmethod
    def __or__(self, other):
        """self | other"""
        podnieś NotImplementedError

    @abstractmethod
    def __ror__(self, other):
        """other | self"""
        podnieś NotImplementedError

    @abstractmethod
    def __invert__(self):
        """~self"""
        podnieś NotImplementedError

    # Concrete implementations of Rational oraz Real abstract methods.
    def __float__(self):
        """float(self) == float(int(self))"""
        zwróć float(int(self))

    @property
    def numerator(self):
        """Integers are their own numerators."""
        zwróć +self

    @property
    def denominator(self):
        """Integers have a denominator of 1."""
        zwróć 1

Integral.register(int)
