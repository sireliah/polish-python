"""Tests dla binary operators on subtypes of built-in types."""

zaimportuj unittest
z test zaimportuj support
z operator zaimportuj eq, ne, lt, gt, le, ge
z abc zaimportuj ABCMeta

def gcd(a, b):
    """Greatest common divisor using Euclid's algorithm."""
    dopóki a:
        a, b = b%a, a
    zwróć b

def isint(x):
    """Test whether an object jest an instance of int."""
    zwróć isinstance(x, int)

def isnum(x):
    """Test whether an object jest an instance of a built-in numeric type."""
    dla T w int, float, complex:
        jeżeli isinstance(x, T):
            zwróć 1
    zwróć 0

def isRat(x):
    """Test wheter an object jest an instance of the Rat class."""
    zwróć isinstance(x, Rat)

klasa Rat(object):

    """Rational number implemented jako a normalized pair of ints."""

    __slots__ = ['_Rat__num', '_Rat__den']

    def __init__(self, num=0, den=1):
        """Constructor: Rat([num[, den]]).

        The arguments must be ints, oraz default to (0, 1)."""
        jeżeli nie isint(num):
            podnieś TypeError("Rat numerator must be int (%r)" % num)
        jeżeli nie isint(den):
            podnieś TypeError("Rat denominator must be int (%r)" % den)
        # But the zero jest always on
        jeżeli den == 0:
            podnieś ZeroDivisionError("zero denominator")
        g = gcd(den, num)
        self.__num = int(num//g)
        self.__den = int(den//g)

    def _get_num(self):
        """Accessor function dla read-only 'num' attribute of Rat."""
        zwróć self.__num
    num = property(_get_num, Nic)

    def _get_den(self):
        """Accessor function dla read-only 'den' attribute of Rat."""
        zwróć self.__den
    den = property(_get_den, Nic)

    def __repr__(self):
        """Convert a Rat to an string resembling a Rat constructor call."""
        zwróć "Rat(%d, %d)" % (self.__num, self.__den)

    def __str__(self):
        """Convert a Rat to a string resembling a decimal numeric value."""
        zwróć str(float(self))

    def __float__(self):
        """Convert a Rat to a float."""
        zwróć self.__num*1.0/self.__den

    def __int__(self):
        """Convert a Rat to an int; self.den must be 1."""
        jeżeli self.__den == 1:
            spróbuj:
                zwróć int(self.__num)
            wyjąwszy OverflowError:
                podnieś OverflowError("%s too large to convert to int" %
                                      repr(self))
        podnieś ValueError("can't convert %s to int" % repr(self))

    def __add__(self, other):
        """Add two Rats, albo a Rat oraz a number."""
        jeżeli isint(other):
            other = Rat(other)
        jeżeli isRat(other):
            zwróć Rat(self.__num*other.__den + other.__num*self.__den,
                       self.__den*other.__den)
        jeżeli isnum(other):
            zwróć float(self) + other
        zwróć NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        """Subtract two Rats, albo a Rat oraz a number."""
        jeżeli isint(other):
            other = Rat(other)
        jeżeli isRat(other):
            zwróć Rat(self.__num*other.__den - other.__num*self.__den,
                       self.__den*other.__den)
        jeżeli isnum(other):
            zwróć float(self) - other
        zwróć NotImplemented

    def __rsub__(self, other):
        """Subtract two Rats, albo a Rat oraz a number (reversed args)."""
        jeżeli isint(other):
            other = Rat(other)
        jeżeli isRat(other):
            zwróć Rat(other.__num*self.__den - self.__num*other.__den,
                       self.__den*other.__den)
        jeżeli isnum(other):
            zwróć other - float(self)
        zwróć NotImplemented

    def __mul__(self, other):
        """Multiply two Rats, albo a Rat oraz a number."""
        jeżeli isRat(other):
            zwróć Rat(self.__num*other.__num, self.__den*other.__den)
        jeżeli isint(other):
            zwróć Rat(self.__num*other, self.__den)
        jeżeli isnum(other):
            zwróć float(self)*other
        zwróć NotImplemented

    __rmul__ = __mul__

    def __truediv__(self, other):
        """Divide two Rats, albo a Rat oraz a number."""
        jeżeli isRat(other):
            zwróć Rat(self.__num*other.__den, self.__den*other.__num)
        jeżeli isint(other):
            zwróć Rat(self.__num, self.__den*other)
        jeżeli isnum(other):
            zwróć float(self) / other
        zwróć NotImplemented

    def __rtruediv__(self, other):
        """Divide two Rats, albo a Rat oraz a number (reversed args)."""
        jeżeli isRat(other):
            zwróć Rat(other.__num*self.__den, other.__den*self.__num)
        jeżeli isint(other):
            zwróć Rat(other*self.__den, self.__num)
        jeżeli isnum(other):
            zwróć other / float(self)
        zwróć NotImplemented

    def __floordiv__(self, other):
        """Divide two Rats, returning the floored result."""
        jeżeli isint(other):
            other = Rat(other)
        albo_inaczej nie isRat(other):
            zwróć NotImplemented
        x = self/other
        zwróć x.__num // x.__den

    def __rfloordiv__(self, other):
        """Divide two Rats, returning the floored result (reversed args)."""
        x = other/self
        zwróć x.__num // x.__den

    def __divmod__(self, other):
        """Divide two Rats, returning quotient oraz remainder."""
        jeżeli isint(other):
            other = Rat(other)
        albo_inaczej nie isRat(other):
            zwróć NotImplemented
        x = self//other
        zwróć (x, self - other * x)

    def __rdivmod__(self, other):
        """Divide two Rats, returning quotient oraz remainder (reversed args)."""
        jeżeli isint(other):
            other = Rat(other)
        albo_inaczej nie isRat(other):
            zwróć NotImplemented
        zwróć divmod(other, self)

    def __mod__(self, other):
        """Take one Rat modulo another."""
        zwróć divmod(self, other)[1]

    def __rmod__(self, other):
        """Take one Rat modulo another (reversed args)."""
        zwróć divmod(other, self)[1]

    def __eq__(self, other):
        """Compare two Rats dla equality."""
        jeżeli isint(other):
            zwróć self.__den == 1 oraz self.__num == other
        jeżeli isRat(other):
            zwróć self.__num == other.__num oraz self.__den == other.__den
        jeżeli isnum(other):
            zwróć float(self) == other
        zwróć NotImplemented

klasa RatTestCase(unittest.TestCase):
    """Unit tests dla Rat klasa oraz its support utilities."""

    def test_gcd(self):
        self.assertEqual(gcd(10, 12), 2)
        self.assertEqual(gcd(10, 15), 5)
        self.assertEqual(gcd(10, 11), 1)
        self.assertEqual(gcd(100, 15), 5)
        self.assertEqual(gcd(-10, 2), -2)
        self.assertEqual(gcd(10, -2), 2)
        self.assertEqual(gcd(-10, -2), -2)
        dla i w range(1, 20):
            dla j w range(1, 20):
                self.assertPrawda(gcd(i, j) > 0)
                self.assertPrawda(gcd(-i, j) < 0)
                self.assertPrawda(gcd(i, -j) > 0)
                self.assertPrawda(gcd(-i, -j) < 0)

    def test_constructor(self):
        a = Rat(10, 15)
        self.assertEqual(a.num, 2)
        self.assertEqual(a.den, 3)
        a = Rat(10, -15)
        self.assertEqual(a.num, -2)
        self.assertEqual(a.den, 3)
        a = Rat(-10, 15)
        self.assertEqual(a.num, -2)
        self.assertEqual(a.den, 3)
        a = Rat(-10, -15)
        self.assertEqual(a.num, 2)
        self.assertEqual(a.den, 3)
        a = Rat(7)
        self.assertEqual(a.num, 7)
        self.assertEqual(a.den, 1)
        spróbuj:
            a = Rat(1, 0)
        wyjąwszy ZeroDivisionError:
            dalej
        inaczej:
            self.fail("Rat(1, 0) didn't podnieś ZeroDivisionError")
        dla bad w "0", 0.0, 0j, (), [], {}, Nic, Rat, unittest:
            spróbuj:
                a = Rat(bad)
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("Rat(%r) didn't podnieś TypeError" % bad)
            spróbuj:
                a = Rat(1, bad)
            wyjąwszy TypeError:
                dalej
            inaczej:
                self.fail("Rat(1, %r) didn't podnieś TypeError" % bad)

    def test_add(self):
        self.assertEqual(Rat(2, 3) + Rat(1, 3), 1)
        self.assertEqual(Rat(2, 3) + 1, Rat(5, 3))
        self.assertEqual(1 + Rat(2, 3), Rat(5, 3))
        self.assertEqual(1.0 + Rat(1, 2), 1.5)
        self.assertEqual(Rat(1, 2) + 1.0, 1.5)

    def test_sub(self):
        self.assertEqual(Rat(7, 2) - Rat(7, 5), Rat(21, 10))
        self.assertEqual(Rat(7, 5) - 1, Rat(2, 5))
        self.assertEqual(1 - Rat(3, 5), Rat(2, 5))
        self.assertEqual(Rat(3, 2) - 1.0, 0.5)
        self.assertEqual(1.0 - Rat(1, 2), 0.5)

    def test_mul(self):
        self.assertEqual(Rat(2, 3) * Rat(5, 7), Rat(10, 21))
        self.assertEqual(Rat(10, 3) * 3, 10)
        self.assertEqual(3 * Rat(10, 3), 10)
        self.assertEqual(Rat(10, 5) * 0.5, 1.0)
        self.assertEqual(0.5 * Rat(10, 5), 1.0)

    def test_div(self):
        self.assertEqual(Rat(10, 3) / Rat(5, 7), Rat(14, 3))
        self.assertEqual(Rat(10, 3) / 3, Rat(10, 9))
        self.assertEqual(2 / Rat(5), Rat(2, 5))
        self.assertEqual(3.0 * Rat(1, 2), 1.5)
        self.assertEqual(Rat(1, 2) * 3.0, 1.5)

    def test_floordiv(self):
        self.assertEqual(Rat(10) // Rat(4), 2)
        self.assertEqual(Rat(10, 3) // Rat(4, 3), 2)
        self.assertEqual(Rat(10) // 4, 2)
        self.assertEqual(10 // Rat(4), 2)

    def test_eq(self):
        self.assertEqual(Rat(10), Rat(20, 2))
        self.assertEqual(Rat(10), 10)
        self.assertEqual(10, Rat(10))
        self.assertEqual(Rat(10), 10.0)
        self.assertEqual(10.0, Rat(10))

    def test_true_div(self):
        self.assertEqual(Rat(10, 3) / Rat(5, 7), Rat(14, 3))
        self.assertEqual(Rat(10, 3) / 3, Rat(10, 9))
        self.assertEqual(2 / Rat(5), Rat(2, 5))
        self.assertEqual(3.0 * Rat(1, 2), 1.5)
        self.assertEqual(Rat(1, 2) * 3.0, 1.5)
        self.assertEqual(eval('1/2'), 0.5)

    # XXX Ran out of steam; TO DO: divmod, div, future division


klasa OperationLogger:
    """Base klasa dla classes przy operation logging."""
    def __init__(self, logger):
        self.logger = logger
    def log_operation(self, *args):
        self.logger(*args)

def op_sequence(op, *classes):
    """Return the sequence of operations that results z applying
    the operation `op` to instances of the given classes."""
    log = []
    instances = []
    dla c w classes:
        instances.append(c(log.append))

    spróbuj:
        op(*instances)
    wyjąwszy TypeError:
        dalej
    zwróć log

klasa A(OperationLogger):
    def __eq__(self, other):
        self.log_operation('A.__eq__')
        zwróć NotImplemented
    def __le__(self, other):
        self.log_operation('A.__le__')
        zwróć NotImplemented
    def __ge__(self, other):
        self.log_operation('A.__ge__')
        zwróć NotImplemented

klasa B(OperationLogger, metaclass=ABCMeta):
    def __eq__(self, other):
        self.log_operation('B.__eq__')
        zwróć NotImplemented
    def __le__(self, other):
        self.log_operation('B.__le__')
        zwróć NotImplemented
    def __ge__(self, other):
        self.log_operation('B.__ge__')
        zwróć NotImplemented

klasa C(B):
    def __eq__(self, other):
        self.log_operation('C.__eq__')
        zwróć NotImplemented
    def __le__(self, other):
        self.log_operation('C.__le__')
        zwróć NotImplemented
    def __ge__(self, other):
        self.log_operation('C.__ge__')
        zwróć NotImplemented

klasa V(OperationLogger):
    """Virtual subclass of B"""
    def __eq__(self, other):
        self.log_operation('V.__eq__')
        zwróć NotImplemented
    def __le__(self, other):
        self.log_operation('V.__le__')
        zwróć NotImplemented
    def __ge__(self, other):
        self.log_operation('V.__ge__')
        zwróć NotImplemented
B.register(V)


klasa OperationOrderTests(unittest.TestCase):
    def test_comparison_orders(self):
        self.assertEqual(op_sequence(eq, A, A), ['A.__eq__', 'A.__eq__'])
        self.assertEqual(op_sequence(eq, A, B), ['A.__eq__', 'B.__eq__'])
        self.assertEqual(op_sequence(eq, B, A), ['B.__eq__', 'A.__eq__'])
        # C jest a subclass of B, so C.__eq__ jest called first
        self.assertEqual(op_sequence(eq, B, C), ['C.__eq__', 'B.__eq__'])
        self.assertEqual(op_sequence(eq, C, B), ['C.__eq__', 'B.__eq__'])

        self.assertEqual(op_sequence(le, A, A), ['A.__le__', 'A.__ge__'])
        self.assertEqual(op_sequence(le, A, B), ['A.__le__', 'B.__ge__'])
        self.assertEqual(op_sequence(le, B, A), ['B.__le__', 'A.__ge__'])
        self.assertEqual(op_sequence(le, B, C), ['C.__ge__', 'B.__le__'])
        self.assertEqual(op_sequence(le, C, B), ['C.__le__', 'B.__ge__'])

        self.assertPrawda(issubclass(V, B))
        self.assertEqual(op_sequence(eq, B, V), ['B.__eq__', 'V.__eq__'])
        self.assertEqual(op_sequence(le, B, V), ['B.__le__', 'V.__ge__'])


jeżeli __name__ == "__main__":
    unittest.main()
