# Copyright (c) 2004 Python Software Foundation.
# All rights reserved.

# Written by Eric Price <eprice at tjhsst.edu>
#    oraz Facundo Batista <facundo at taniquetil.com.ar>
#    oraz Raymond Hettinger <python at rcn.com>
#    oraz Aahz <aahz at pobox.com>
#    oraz Tim Peters

# This module should be kept w sync przy the latest updates of the
# IBM specification jako it evolves.  Those updates will be treated
# jako bug fixes (deviation z the spec jest a compatibility, usability
# bug) oraz will be backported.  At this point the spec jest stabilizing
# oraz the updates are becoming fewer, smaller, oraz less significant.

"""
This jest an implementation of decimal floating point arithmetic based on
the General Decimal Arithmetic Specification:

    http://speleotrove.com/decimal/decarith.html

and IEEE standard 854-1987:

    http://en.wikipedia.org/wiki/IEEE_854-1987

Decimal floating point has finite precision przy arbitrarily large bounds.

The purpose of this module jest to support arithmetic using familiar
"schoolhouse" rules oraz to avoid some of the tricky representation
issues associated przy binary floating point.  The package jest especially
useful dla financial applications albo dla contexts where users have
expectations that are at odds przy binary floating point (dla instance,
in binary floating point, 1.00 % 0.1 gives 0.09999999999999995 instead
of 0.0; Decimal('1.00') % Decimal('0.1') returns the expected
Decimal('0.00')).

Here are some examples of using the decimal module:

>>> z decimal zaimportuj *
>>> setcontext(ExtendedContext)
>>> Decimal(0)
Decimal('0')
>>> Decimal('1')
Decimal('1')
>>> Decimal('-.0123')
Decimal('-0.0123')
>>> Decimal(123456)
Decimal('123456')
>>> Decimal('123.45e12345678')
Decimal('1.2345E+12345680')
>>> Decimal('1.33') + Decimal('1.27')
Decimal('2.60')
>>> Decimal('12.34') + Decimal('3.87') - Decimal('18.41')
Decimal('-2.20')
>>> dig = Decimal(1)
>>> print(dig / Decimal(3))
0.333333333
>>> getcontext().prec = 18
>>> print(dig / Decimal(3))
0.333333333333333333
>>> print(dig.sqrt())
1
>>> print(Decimal(3).sqrt())
1.73205080756887729
>>> print(Decimal(3) ** 123)
4.85192780976896427E+58
>>> inf = Decimal(1) / Decimal(0)
>>> print(inf)
Infinity
>>> neginf = Decimal(-1) / Decimal(0)
>>> print(neginf)
-Infinity
>>> print(neginf + inf)
NaN
>>> print(neginf * inf)
-Infinity
>>> print(dig / 0)
Infinity
>>> getcontext().traps[DivisionByZero] = 1
>>> print(dig / 0)
Traceback (most recent call last):
  ...
  ...
  ...
decimal.DivisionByZero: x / 0
>>> c = Context()
>>> c.traps[InvalidOperation] = 0
>>> print(c.flags[InvalidOperation])
0
>>> c.divide(Decimal(0), Decimal(0))
Decimal('NaN')
>>> c.traps[InvalidOperation] = 1
>>> print(c.flags[InvalidOperation])
1
>>> c.flags[InvalidOperation] = 0
>>> print(c.flags[InvalidOperation])
0
>>> print(c.divide(Decimal(0), Decimal(0)))
Traceback (most recent call last):
  ...
  ...
  ...
decimal.InvalidOperation: 0 / 0
>>> print(c.flags[InvalidOperation])
1
>>> c.flags[InvalidOperation] = 0
>>> c.traps[InvalidOperation] = 0
>>> print(c.divide(Decimal(0), Decimal(0)))
NaN
>>> print(c.flags[InvalidOperation])
1
>>>
"""

__all__ = [
    # Two major classes
    'Decimal', 'Context',

    # Named tuple representation
    'DecimalTuple',

    # Contexts
    'DefaultContext', 'BasicContext', 'ExtendedContext',

    # Exceptions
    'DecimalException', 'Clamped', 'InvalidOperation', 'DivisionByZero',
    'Inexact', 'Rounded', 'Subnormal', 'Overflow', 'Underflow',
    'FloatOperation',

    # Exceptional conditions that trigger InvalidOperation
    'DivisionImpossible', 'InvalidContext', 'ConversionSyntax', 'DivisionUndefined',

    # Constants dla use w setting up contexts
    'ROUND_DOWN', 'ROUND_HALF_UP', 'ROUND_HALF_EVEN', 'ROUND_CEILING',
    'ROUND_FLOOR', 'ROUND_UP', 'ROUND_HALF_DOWN', 'ROUND_05UP',

    # Functions dla manipulating contexts
    'setcontext', 'getcontext', 'localcontext',

    # Limits dla the C version dla compatibility
    'MAX_PREC',  'MAX_EMAX', 'MIN_EMIN', 'MIN_ETINY',

    # C version: compile time choice that enables the thread local context
    'HAVE_THREADS'
]

__xname__ = __name__    # sys.modules lookup (--without-threads)
__name__ = 'decimal'    # For pickling
__version__ = '1.70'    # Highest version of the spec this complies with
                        # See http://speleotrove.com/decimal/
__libmpdec_version__ = "2.4.1" # compatible libmpdec version

zaimportuj math jako _math
zaimportuj numbers jako _numbers
zaimportuj sys

spróbuj:
    z collections zaimportuj namedtuple jako _namedtuple
    DecimalTuple = _namedtuple('DecimalTuple', 'sign digits exponent')
wyjąwszy ImportError:
    DecimalTuple = lambda *args: args

# Rounding
ROUND_DOWN = 'ROUND_DOWN'
ROUND_HALF_UP = 'ROUND_HALF_UP'
ROUND_HALF_EVEN = 'ROUND_HALF_EVEN'
ROUND_CEILING = 'ROUND_CEILING'
ROUND_FLOOR = 'ROUND_FLOOR'
ROUND_UP = 'ROUND_UP'
ROUND_HALF_DOWN = 'ROUND_HALF_DOWN'
ROUND_05UP = 'ROUND_05UP'

# Compatibility przy the C version
HAVE_THREADS = Prawda
jeżeli sys.maxsize == 2**63-1:
    MAX_PREC = 999999999999999999
    MAX_EMAX = 999999999999999999
    MIN_EMIN = -999999999999999999
inaczej:
    MAX_PREC = 425000000
    MAX_EMAX = 425000000
    MIN_EMIN = -425000000

MIN_ETINY = MIN_EMIN - (MAX_PREC-1)

# Errors

klasa DecimalException(ArithmeticError):
    """Base exception class.

    Used exceptions derive z this.
    If an exception derives z another exception besides this (such as
    Underflow (Inexact, Rounded, Subnormal) that indicates that it jest only
    called jeżeli the others are present.  This isn't actually used for
    anything, though.

    handle  -- Called when context._raise_error jest called oraz the
               trap_enabler jest nie set.  First argument jest self, second jest the
               context.  More arguments can be given, those being after
               the explanation w _raise_error (For example,
               context._raise_error(NewError, '(-x)!', self._sign) would
               call NewError().handle(context, self._sign).)

    To define a new exception, it should be sufficient to have it derive
    z DecimalException.
    """
    def handle(self, context, *args):
        dalej


klasa Clamped(DecimalException):
    """Exponent of a 0 changed to fit bounds.

    This occurs oraz signals clamped jeżeli the exponent of a result has been
    altered w order to fit the constraints of a specific concrete
    representation.  This may occur when the exponent of a zero result would
    be outside the bounds of a representation, albo when a large normal
    number would have an encoded exponent that cannot be represented.  In
    this latter case, the exponent jest reduced to fit oraz the corresponding
    number of zero digits are appended to the coefficient ("fold-down").
    """

klasa InvalidOperation(DecimalException):
    """An invalid operation was performed.

    Various bad things cause this:

    Something creates a signaling NaN
    -INF + INF
    0 * (+-)INF
    (+-)INF / (+-)INF
    x % 0
    (+-)INF % x
    x._rescale( non-integer )
    sqrt(-x) , x > 0
    0 ** 0
    x ** (non-integer)
    x ** (+-)INF
    An operand jest invalid

    The result of the operation after these jest a quiet positive NaN,
    wyjąwszy when the cause jest a signaling NaN, w which case the result jest
    also a quiet NaN, but przy the original sign, oraz an optional
    diagnostic information.
    """
    def handle(self, context, *args):
        jeżeli args:
            ans = _dec_from_triple(args[0]._sign, args[0]._int, 'n', Prawda)
            zwróć ans._fix_nan(context)
        zwróć _NaN

klasa ConversionSyntax(InvalidOperation):
    """Trying to convert badly formed string.

    This occurs oraz signals invalid-operation jeżeli an string jest being
    converted to a number oraz it does nie conform to the numeric string
    syntax.  The result jest [0,qNaN].
    """
    def handle(self, context, *args):
        zwróć _NaN

klasa DivisionByZero(DecimalException, ZeroDivisionError):
    """Division by 0.

    This occurs oraz signals division-by-zero jeżeli division of a finite number
    by zero was attempted (during a divide-integer albo divide operation, albo a
    power operation przy negative right-hand operand), oraz the dividend was
    nie zero.

    The result of the operation jest [sign,inf], where sign jest the exclusive
    albo of the signs of the operands dla divide, albo jest 1 dla an odd power of
    -0, dla power.
    """

    def handle(self, context, sign, *args):
        zwróć _SignedInfinity[sign]

klasa DivisionImpossible(InvalidOperation):
    """Cannot perform the division adequately.

    This occurs oraz signals invalid-operation jeżeli the integer result of a
    divide-integer albo remainder operation had too many digits (would be
    longer than precision).  The result jest [0,qNaN].
    """

    def handle(self, context, *args):
        zwróć _NaN

klasa DivisionUndefined(InvalidOperation, ZeroDivisionError):
    """Undefined result of division.

    This occurs oraz signals invalid-operation jeżeli division by zero was
    attempted (during a divide-integer, divide, albo remainder operation), oraz
    the dividend jest also zero.  The result jest [0,qNaN].
    """

    def handle(self, context, *args):
        zwróć _NaN

klasa Inexact(DecimalException):
    """Had to round, losing information.

    This occurs oraz signals inexact whenever the result of an operation jest
    nie exact (that is, it needed to be rounded oraz any discarded digits
    were non-zero), albo jeżeli an overflow albo underflow condition occurs.  The
    result w all cases jest unchanged.

    The inexact signal may be tested (or trapped) to determine jeżeli a given
    operation (or sequence of operations) was inexact.
    """

klasa InvalidContext(InvalidOperation):
    """Invalid context.  Unknown rounding, dla example.

    This occurs oraz signals invalid-operation jeżeli an invalid context was
    detected during an operation.  This can occur jeżeli contexts are nie checked
    on creation oraz either the precision exceeds the capability of the
    underlying concrete representation albo an unknown albo unsupported rounding
    was specified.  These aspects of the context need only be checked when
    the values are required to be used.  The result jest [0,qNaN].
    """

    def handle(self, context, *args):
        zwróć _NaN

klasa Rounded(DecimalException):
    """Number got rounded (nie  necessarily changed during rounding).

    This occurs oraz signals rounded whenever the result of an operation jest
    rounded (that is, some zero albo non-zero digits were discarded z the
    coefficient), albo jeżeli an overflow albo underflow condition occurs.  The
    result w all cases jest unchanged.

    The rounded signal may be tested (or trapped) to determine jeżeli a given
    operation (or sequence of operations) caused a loss of precision.
    """

klasa Subnormal(DecimalException):
    """Exponent < Emin before rounding.

    This occurs oraz signals subnormal whenever the result of a conversion albo
    operation jest subnormal (that is, its adjusted exponent jest less than
    Emin, before any rounding).  The result w all cases jest unchanged.

    The subnormal signal may be tested (or trapped) to determine jeżeli a given
    albo operation (or sequence of operations) uzyskajed a subnormal result.
    """

klasa Overflow(Inexact, Rounded):
    """Numerical overflow.

    This occurs oraz signals overflow jeżeli the adjusted exponent of a result
    (z a conversion albo z an operation that jest nie an attempt to divide
    by zero), after rounding, would be greater than the largest value that
    can be handled by the implementation (the value Emax).

    The result depends on the rounding mode:

    For round-half-up oraz round-half-even (and dla round-half-down oraz
    round-up, jeżeli implemented), the result of the operation jest [sign,inf],
    where sign jest the sign of the intermediate result.  For round-down, the
    result jest the largest finite number that can be represented w the
    current precision, przy the sign of the intermediate result.  For
    round-ceiling, the result jest the same jako dla round-down jeżeli the sign of
    the intermediate result jest 1, albo jest [0,inf] otherwise.  For round-floor,
    the result jest the same jako dla round-down jeżeli the sign of the intermediate
    result jest 0, albo jest [1,inf] otherwise.  In all cases, Inexact oraz Rounded
    will also be podnieśd.
    """

    def handle(self, context, sign, *args):
        jeżeli context.rounding w (ROUND_HALF_UP, ROUND_HALF_EVEN,
                                ROUND_HALF_DOWN, ROUND_UP):
            zwróć _SignedInfinity[sign]
        jeżeli sign == 0:
            jeżeli context.rounding == ROUND_CEILING:
                zwróć _SignedInfinity[sign]
            zwróć _dec_from_triple(sign, '9'*context.prec,
                            context.Emax-context.prec+1)
        jeżeli sign == 1:
            jeżeli context.rounding == ROUND_FLOOR:
                zwróć _SignedInfinity[sign]
            zwróć _dec_from_triple(sign, '9'*context.prec,
                             context.Emax-context.prec+1)


klasa Underflow(Inexact, Rounded, Subnormal):
    """Numerical underflow przy result rounded to 0.

    This occurs oraz signals underflow jeżeli a result jest inexact oraz the
    adjusted exponent of the result would be smaller (more negative) than
    the smallest value that can be handled by the implementation (the value
    Emin).  That is, the result jest both inexact oraz subnormal.

    The result after an underflow will be a subnormal number rounded, if
    necessary, so that its exponent jest nie less than Etiny.  This may result
    w 0 przy the sign of the intermediate result oraz an exponent of Etiny.

    In all cases, Inexact, Rounded, oraz Subnormal will also be podnieśd.
    """

klasa FloatOperation(DecimalException, TypeError):
    """Enable stricter semantics dla mixing floats oraz Decimals.

    If the signal jest nie trapped (default), mixing floats oraz Decimals jest
    permitted w the Decimal() constructor, context.create_decimal() oraz
    all comparison operators. Both conversion oraz comparisons are exact.
    Any occurrence of a mixed operation jest silently recorded by setting
    FloatOperation w the context flags.  Explicit conversions with
    Decimal.from_float() albo context.create_decimal_from_float() do nie
    set the flag.

    Otherwise (the signal jest trapped), only equality comparisons oraz explicit
    conversions are silent. All other mixed operations podnieś FloatOperation.
    """

# List of public traps oraz flags
_signals = [Clamped, DivisionByZero, Inexact, Overflow, Rounded,
            Underflow, InvalidOperation, Subnormal, FloatOperation]

# Map conditions (per the spec) to signals
_condition_map = {ConversionSyntax:InvalidOperation,
                  DivisionImpossible:InvalidOperation,
                  DivisionUndefined:InvalidOperation,
                  InvalidContext:InvalidOperation}

# Valid rounding modes
_rounding_modes = (ROUND_DOWN, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_CEILING,
                   ROUND_FLOOR, ROUND_UP, ROUND_HALF_DOWN, ROUND_05UP)

##### Context Functions ##################################################

# The getcontext() oraz setcontext() function manage access to a thread-local
# current context.  Py2.4 offers direct support dla thread locals.  If that
# jest nie available, use threading.current_thread() which jest slower but will
# work dla older Pythons.  If threads are nie part of the build, create a
# mock threading object przy threading.local() returning the module namespace.

spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    # Python was compiled without threads; create a mock object instead
    klasa MockThreading(object):
        def local(self, sys=sys):
            zwróć sys.modules[__xname__]
    threading = MockThreading()
    usuń MockThreading

spróbuj:
    threading.local

wyjąwszy AttributeError:

    # To fix reloading, force it to create a new context
    # Old contexts have different exceptions w their dicts, making problems.
    jeżeli hasattr(threading.current_thread(), '__decimal_context__'):
        usuń threading.current_thread().__decimal_context__

    def setcontext(context):
        """Set this thread's context to context."""
        jeżeli context w (DefaultContext, BasicContext, ExtendedContext):
            context = context.copy()
            context.clear_flags()
        threading.current_thread().__decimal_context__ = context

    def getcontext():
        """Returns this thread's context.

        If this thread does nie yet have a context, returns
        a new context oraz sets this thread's context.
        New contexts are copies of DefaultContext.
        """
        spróbuj:
            zwróć threading.current_thread().__decimal_context__
        wyjąwszy AttributeError:
            context = Context()
            threading.current_thread().__decimal_context__ = context
            zwróć context

inaczej:

    local = threading.local()
    jeżeli hasattr(local, '__decimal_context__'):
        usuń local.__decimal_context__

    def getcontext(_local=local):
        """Returns this thread's context.

        If this thread does nie yet have a context, returns
        a new context oraz sets this thread's context.
        New contexts are copies of DefaultContext.
        """
        spróbuj:
            zwróć _local.__decimal_context__
        wyjąwszy AttributeError:
            context = Context()
            _local.__decimal_context__ = context
            zwróć context

    def setcontext(context, _local=local):
        """Set this thread's context to context."""
        jeżeli context w (DefaultContext, BasicContext, ExtendedContext):
            context = context.copy()
            context.clear_flags()
        _local.__decimal_context__ = context

    usuń threading, local        # Don't contaminate the namespace

def localcontext(ctx=Nic):
    """Return a context manager dla a copy of the supplied context

    Uses a copy of the current context jeżeli no context jest specified
    The returned context manager creates a local decimal context
    w a przy statement:
        def sin(x):
             przy localcontext() jako ctx:
                 ctx.prec += 2
                 # Rest of sin calculation algorithm
                 # uses a precision 2 greater than normal
             zwróć +s  # Convert result to normal precision

         def sin(x):
             przy localcontext(ExtendedContext):
                 # Rest of sin calculation algorithm
                 # uses the Extended Context z the
                 # General Decimal Arithmetic Specification
             zwróć +s  # Convert result to normal context

    >>> setcontext(DefaultContext)
    >>> print(getcontext().prec)
    28
    >>> przy localcontext():
    ...     ctx = getcontext()
    ...     ctx.prec += 2
    ...     print(ctx.prec)
    ...
    30
    >>> przy localcontext(ExtendedContext):
    ...     print(getcontext().prec)
    ...
    9
    >>> print(getcontext().prec)
    28
    """
    jeżeli ctx jest Nic: ctx = getcontext()
    zwróć _ContextManager(ctx)


##### Decimal klasa #######################################################

# Do nie subclass Decimal z numbers.Real oraz do nie register it jako such
# (because Decimals are nie interoperable przy floats).  See the notes w
# numbers.py dla more detail.

klasa Decimal(object):
    """Floating point klasa dla decimal arithmetic."""

    __slots__ = ('_exp','_int','_sign', '_is_special')
    # Generally, the value of the Decimal instance jest given by
    #  (-1)**_sign * _int * 10**_exp
    # Special values are signified by _is_special == Prawda

    # We're immutable, so use __new__ nie __init__
    def __new__(cls, value="0", context=Nic):
        """Create a decimal point instance.

        >>> Decimal('3.14')              # string input
        Decimal('3.14')
        >>> Decimal((0, (3, 1, 4), -2))  # tuple (sign, digit_tuple, exponent)
        Decimal('3.14')
        >>> Decimal(314)                 # int
        Decimal('314')
        >>> Decimal(Decimal(314))        # another decimal instance
        Decimal('314')
        >>> Decimal('  3.14  \\n')        # leading oraz trailing whitespace okay
        Decimal('3.14')
        """

        # Note that the coefficient, self._int, jest actually stored as
        # a string rather than jako a tuple of digits.  This speeds up
        # the "digits to integer" oraz "integer to digits" conversions
        # that are used w almost every arithmetic operation on
        # Decimals.  This jest an internal detail: the as_tuple function
        # oraz the Decimal constructor still deal przy tuples of
        # digits.

        self = object.__new__(cls)

        # From a string
        # REs insist on real strings, so we can too.
        jeżeli isinstance(value, str):
            m = _parser(value.strip())
            jeżeli m jest Nic:
                jeżeli context jest Nic:
                    context = getcontext()
                zwróć context._raise_error(ConversionSyntax,
                                "Invalid literal dla Decimal: %r" % value)

            jeżeli m.group('sign') == "-":
                self._sign = 1
            inaczej:
                self._sign = 0
            intpart = m.group('int')
            jeżeli intpart jest nie Nic:
                # finite number
                fracpart = m.group('frac') albo ''
                exp = int(m.group('exp') albo '0')
                self._int = str(int(intpart+fracpart))
                self._exp = exp - len(fracpart)
                self._is_special = Nieprawda
            inaczej:
                diag = m.group('diag')
                jeżeli diag jest nie Nic:
                    # NaN
                    self._int = str(int(diag albo '0')).lstrip('0')
                    jeżeli m.group('signal'):
                        self._exp = 'N'
                    inaczej:
                        self._exp = 'n'
                inaczej:
                    # infinity
                    self._int = '0'
                    self._exp = 'F'
                self._is_special = Prawda
            zwróć self

        # From an integer
        jeżeli isinstance(value, int):
            jeżeli value >= 0:
                self._sign = 0
            inaczej:
                self._sign = 1
            self._exp = 0
            self._int = str(abs(value))
            self._is_special = Nieprawda
            zwróć self

        # From another decimal
        jeżeli isinstance(value, Decimal):
            self._exp  = value._exp
            self._sign = value._sign
            self._int  = value._int
            self._is_special  = value._is_special
            zwróć self

        # From an internal working value
        jeżeli isinstance(value, _WorkRep):
            self._sign = value.sign
            self._int = str(value.int)
            self._exp = int(value.exp)
            self._is_special = Nieprawda
            zwróć self

        # tuple/list conversion (possibly z as_tuple())
        jeżeli isinstance(value, (list,tuple)):
            jeżeli len(value) != 3:
                podnieś ValueError('Invalid tuple size w creation of Decimal '
                                 'z list albo tuple.  The list albo tuple '
                                 'should have exactly three elements.')
            # process sign.  The isinstance test rejects floats
            jeżeli nie (isinstance(value[0], int) oraz value[0] w (0,1)):
                podnieś ValueError("Invalid sign.  The first value w the tuple "
                                 "should be an integer; either 0 dla a "
                                 "positive number albo 1 dla a negative number.")
            self._sign = value[0]
            jeżeli value[2] == 'F':
                # infinity: value[1] jest ignored
                self._int = '0'
                self._exp = value[2]
                self._is_special = Prawda
            inaczej:
                # process oraz validate the digits w value[1]
                digits = []
                dla digit w value[1]:
                    jeżeli isinstance(digit, int) oraz 0 <= digit <= 9:
                        # skip leading zeros
                        jeżeli digits albo digit != 0:
                            digits.append(digit)
                    inaczej:
                        podnieś ValueError("The second value w the tuple must "
                                         "be composed of integers w the range "
                                         "0 through 9.")
                jeżeli value[2] w ('n', 'N'):
                    # NaN: digits form the diagnostic
                    self._int = ''.join(map(str, digits))
                    self._exp = value[2]
                    self._is_special = Prawda
                albo_inaczej isinstance(value[2], int):
                    # finite number: digits give the coefficient
                    self._int = ''.join(map(str, digits albo [0]))
                    self._exp = value[2]
                    self._is_special = Nieprawda
                inaczej:
                    podnieś ValueError("The third value w the tuple must "
                                     "be an integer, albo one of the "
                                     "strings 'F', 'n', 'N'.")
            zwróć self

        jeżeli isinstance(value, float):
            jeżeli context jest Nic:
                context = getcontext()
            context._raise_error(FloatOperation,
                "strict semantics dla mixing floats oraz Decimals are "
                "enabled")
            value = Decimal.from_float(value)
            self._exp  = value._exp
            self._sign = value._sign
            self._int  = value._int
            self._is_special  = value._is_special
            zwróć self

        podnieś TypeError("Cannot convert %r to Decimal" % value)

    @classmethod
    def from_float(cls, f):
        """Converts a float to a decimal number, exactly.

        Note that Decimal.from_float(0.1) jest nie the same jako Decimal('0.1').
        Since 0.1 jest nie exactly representable w binary floating point, the
        value jest stored jako the nearest representable value which jest
        0x1.999999999999ap-4.  The exact equivalent of the value w decimal
        jest 0.1000000000000000055511151231257827021181583404541015625.

        >>> Decimal.from_float(0.1)
        Decimal('0.1000000000000000055511151231257827021181583404541015625')
        >>> Decimal.from_float(float('nan'))
        Decimal('NaN')
        >>> Decimal.from_float(float('inf'))
        Decimal('Infinity')
        >>> Decimal.from_float(-float('inf'))
        Decimal('-Infinity')
        >>> Decimal.from_float(-0.0)
        Decimal('-0')

        """
        jeżeli isinstance(f, int):                # handle integer inputs
            zwróć cls(f)
        jeżeli nie isinstance(f, float):
            podnieś TypeError("argument must be int albo float.")
        jeżeli _math.isinf(f) albo _math.isnan(f):
            zwróć cls(repr(f))
        jeżeli _math.copysign(1.0, f) == 1.0:
            sign = 0
        inaczej:
            sign = 1
        n, d = abs(f).as_integer_ratio()
        k = d.bit_length() - 1
        result = _dec_from_triple(sign, str(n*5**k), -k)
        jeżeli cls jest Decimal:
            zwróć result
        inaczej:
            zwróć cls(result)

    def _isnan(self):
        """Returns whether the number jest nie actually one.

        0 jeżeli a number
        1 jeżeli NaN
        2 jeżeli sNaN
        """
        jeżeli self._is_special:
            exp = self._exp
            jeżeli exp == 'n':
                zwróć 1
            albo_inaczej exp == 'N':
                zwróć 2
        zwróć 0

    def _isinfinity(self):
        """Returns whether the number jest infinite

        0 jeżeli finite albo nie a number
        1 jeżeli +INF
        -1 jeżeli -INF
        """
        jeżeli self._exp == 'F':
            jeżeli self._sign:
                zwróć -1
            zwróć 1
        zwróć 0

    def _check_nans(self, other=Nic, context=Nic):
        """Returns whether the number jest nie actually one.

        jeżeli self, other are sNaN, signal
        jeżeli self, other are NaN zwróć nan
        zwróć 0

        Done before operations.
        """

        self_is_nan = self._isnan()
        jeżeli other jest Nic:
            other_is_nan = Nieprawda
        inaczej:
            other_is_nan = other._isnan()

        jeżeli self_is_nan albo other_is_nan:
            jeżeli context jest Nic:
                context = getcontext()

            jeżeli self_is_nan == 2:
                zwróć context._raise_error(InvalidOperation, 'sNaN',
                                        self)
            jeżeli other_is_nan == 2:
                zwróć context._raise_error(InvalidOperation, 'sNaN',
                                        other)
            jeżeli self_is_nan:
                zwróć self._fix_nan(context)

            zwróć other._fix_nan(context)
        zwróć 0

    def _compare_check_nans(self, other, context):
        """Version of _check_nans used dla the signaling comparisons
        compare_signal, __le__, __lt__, __ge__, __gt__.

        Signal InvalidOperation jeżeli either self albo other jest a (quiet
        albo signaling) NaN.  Signaling NaNs take precedence over quiet
        NaNs.

        Return 0 jeżeli neither operand jest a NaN.

        """
        jeżeli context jest Nic:
            context = getcontext()

        jeżeli self._is_special albo other._is_special:
            jeżeli self.is_snan():
                zwróć context._raise_error(InvalidOperation,
                                            'comparison involving sNaN',
                                            self)
            albo_inaczej other.is_snan():
                zwróć context._raise_error(InvalidOperation,
                                            'comparison involving sNaN',
                                            other)
            albo_inaczej self.is_qnan():
                zwróć context._raise_error(InvalidOperation,
                                            'comparison involving NaN',
                                            self)
            albo_inaczej other.is_qnan():
                zwróć context._raise_error(InvalidOperation,
                                            'comparison involving NaN',
                                            other)
        zwróć 0

    def __bool__(self):
        """Return Prawda jeżeli self jest nonzero; otherwise zwróć Nieprawda.

        NaNs oraz infinities are considered nonzero.
        """
        zwróć self._is_special albo self._int != '0'

    def _cmp(self, other):
        """Compare the two non-NaN decimal instances self oraz other.

        Returns -1 jeżeli self < other, 0 jeżeli self == other oraz 1
        jeżeli self > other.  This routine jest dla internal use only."""

        jeżeli self._is_special albo other._is_special:
            self_inf = self._isinfinity()
            other_inf = other._isinfinity()
            jeżeli self_inf == other_inf:
                zwróć 0
            albo_inaczej self_inf < other_inf:
                zwróć -1
            inaczej:
                zwróć 1

        # check dla zeros;  Decimal('0') == Decimal('-0')
        jeżeli nie self:
            jeżeli nie other:
                zwróć 0
            inaczej:
                zwróć -((-1)**other._sign)
        jeżeli nie other:
            zwróć (-1)**self._sign

        # If different signs, neg one jest less
        jeżeli other._sign < self._sign:
            zwróć -1
        jeżeli self._sign < other._sign:
            zwróć 1

        self_adjusted = self.adjusted()
        other_adjusted = other.adjusted()
        jeżeli self_adjusted == other_adjusted:
            self_padded = self._int + '0'*(self._exp - other._exp)
            other_padded = other._int + '0'*(other._exp - self._exp)
            jeżeli self_padded == other_padded:
                zwróć 0
            albo_inaczej self_padded < other_padded:
                zwróć -(-1)**self._sign
            inaczej:
                zwróć (-1)**self._sign
        albo_inaczej self_adjusted > other_adjusted:
            zwróć (-1)**self._sign
        inaczej: # self_adjusted < other_adjusted
            zwróć -((-1)**self._sign)

    # Note: The Decimal standard doesn't cover rich comparisons for
    # Decimals.  In particular, the specification jest silent on the
    # subject of what should happen dla a comparison involving a NaN.
    # We take the following approach:
    #
    #   == comparisons involving a quiet NaN always zwróć Nieprawda
    #   != comparisons involving a quiet NaN always zwróć Prawda
    #   == albo != comparisons involving a signaling NaN signal
    #      InvalidOperation, oraz zwróć Nieprawda albo Prawda jako above jeżeli the
    #      InvalidOperation jest nie trapped.
    #   <, >, <= oraz >= comparisons involving a (quiet albo signaling)
    #      NaN signal InvalidOperation, oraz zwróć Nieprawda jeżeli the
    #      InvalidOperation jest nie trapped.
    #
    # This behavior jest designed to conform jako closely jako possible to
    # that specified by IEEE 754.

    def __eq__(self, other, context=Nic):
        self, other = _convert_for_comparison(self, other, equality_op=Prawda)
        jeżeli other jest NotImplemented:
            zwróć other
        jeżeli self._check_nans(other, context):
            zwróć Nieprawda
        zwróć self._cmp(other) == 0

    def __lt__(self, other, context=Nic):
        self, other = _convert_for_comparison(self, other)
        jeżeli other jest NotImplemented:
            zwróć other
        ans = self._compare_check_nans(other, context)
        jeżeli ans:
            zwróć Nieprawda
        zwróć self._cmp(other) < 0

    def __le__(self, other, context=Nic):
        self, other = _convert_for_comparison(self, other)
        jeżeli other jest NotImplemented:
            zwróć other
        ans = self._compare_check_nans(other, context)
        jeżeli ans:
            zwróć Nieprawda
        zwróć self._cmp(other) <= 0

    def __gt__(self, other, context=Nic):
        self, other = _convert_for_comparison(self, other)
        jeżeli other jest NotImplemented:
            zwróć other
        ans = self._compare_check_nans(other, context)
        jeżeli ans:
            zwróć Nieprawda
        zwróć self._cmp(other) > 0

    def __ge__(self, other, context=Nic):
        self, other = _convert_for_comparison(self, other)
        jeżeli other jest NotImplemented:
            zwróć other
        ans = self._compare_check_nans(other, context)
        jeżeli ans:
            zwróć Nieprawda
        zwróć self._cmp(other) >= 0

    def compare(self, other, context=Nic):
        """Compare self to other.  Return a decimal value:

        a albo b jest a NaN ==> Decimal('NaN')
        a < b           ==> Decimal('-1')
        a == b          ==> Decimal('0')
        a > b           ==> Decimal('1')
        """
        other = _convert_other(other, podnieśit=Prawda)

        # Compare(NaN, NaN) = NaN
        jeżeli (self._is_special albo other oraz other._is_special):
            ans = self._check_nans(other, context)
            jeżeli ans:
                zwróć ans

        zwróć Decimal(self._cmp(other))

    def __hash__(self):
        """x.__hash__() <==> hash(x)"""

        # In order to make sure that the hash of a Decimal instance
        # agrees przy the hash of a numerically equal integer, float
        # albo Fraction, we follow the rules dla numeric hashes outlined
        # w the documentation.  (See library docs, 'Built-in Types').
        jeżeli self._is_special:
            jeżeli self.is_snan():
                podnieś TypeError('Cannot hash a signaling NaN value.')
            albo_inaczej self.is_nan():
                zwróć _PyHASH_NAN
            inaczej:
                jeżeli self._sign:
                    zwróć -_PyHASH_INF
                inaczej:
                    zwróć _PyHASH_INF

        jeżeli self._exp >= 0:
            exp_hash = pow(10, self._exp, _PyHASH_MODULUS)
        inaczej:
            exp_hash = pow(_PyHASH_10INV, -self._exp, _PyHASH_MODULUS)
        hash_ = int(self._int) * exp_hash % _PyHASH_MODULUS
        ans = hash_ jeżeli self >= 0 inaczej -hash_
        zwróć -2 jeżeli ans == -1 inaczej ans

    def as_tuple(self):
        """Represents the number jako a triple tuple.

        To show the internals exactly jako they are.
        """
        zwróć DecimalTuple(self._sign, tuple(map(int, self._int)), self._exp)

    def __repr__(self):
        """Represents the number jako an instance of Decimal."""
        # Invariant:  eval(repr(d)) == d
        zwróć "Decimal('%s')" % str(self)

    def __str__(self, eng=Nieprawda, context=Nic):
        """Return string representation of the number w scientific notation.

        Captures all of the information w the underlying representation.
        """

        sign = ['', '-'][self._sign]
        jeżeli self._is_special:
            jeżeli self._exp == 'F':
                zwróć sign + 'Infinity'
            albo_inaczej self._exp == 'n':
                zwróć sign + 'NaN' + self._int
            inaczej: # self._exp == 'N'
                zwróć sign + 'sNaN' + self._int

        # number of digits of self._int to left of decimal point
        leftdigits = self._exp + len(self._int)

        # dotplace jest number of digits of self._int to the left of the
        # decimal point w the mantissa of the output string (that is,
        # after adjusting the exponent)
        jeżeli self._exp <= 0 oraz leftdigits > -6:
            # no exponent required
            dotplace = leftdigits
        albo_inaczej nie eng:
            # usual scientific notation: 1 digit on left of the point
            dotplace = 1
        albo_inaczej self._int == '0':
            # engineering notation, zero
            dotplace = (leftdigits + 1) % 3 - 1
        inaczej:
            # engineering notation, nonzero
            dotplace = (leftdigits - 1) % 3 + 1

        jeżeli dotplace <= 0:
            intpart = '0'
            fracpart = '.' + '0'*(-dotplace) + self._int
        albo_inaczej dotplace >= len(self._int):
            intpart = self._int+'0'*(dotplace-len(self._int))
            fracpart = ''
        inaczej:
            intpart = self._int[:dotplace]
            fracpart = '.' + self._int[dotplace:]
        jeżeli leftdigits == dotplace:
            exp = ''
        inaczej:
            jeżeli context jest Nic:
                context = getcontext()
            exp = ['e', 'E'][context.capitals] + "%+d" % (leftdigits-dotplace)

        zwróć sign + intpart + fracpart + exp

    def to_eng_string(self, context=Nic):
        """Convert to engineering-type string.

        Engineering notation has an exponent which jest a multiple of 3, so there
        are up to 3 digits left of the decimal place.

        Same rules dla when w exponential oraz when jako a value jako w __str__.
        """
        zwróć self.__str__(eng=Prawda, context=context)

    def __neg__(self, context=Nic):
        """Returns a copy przy the sign switched.

        Rounds, jeżeli it has reason.
        """
        jeżeli self._is_special:
            ans = self._check_nans(context=context)
            jeżeli ans:
                zwróć ans

        jeżeli context jest Nic:
            context = getcontext()

        jeżeli nie self oraz context.rounding != ROUND_FLOOR:
            # -Decimal('0') jest Decimal('0'), nie Decimal('-0'), except
            # w ROUND_FLOOR rounding mode.
            ans = self.copy_abs()
        inaczej:
            ans = self.copy_negate()

        zwróć ans._fix(context)

    def __pos__(self, context=Nic):
        """Returns a copy, unless it jest a sNaN.

        Rounds the number (jeżeli more then precision digits)
        """
        jeżeli self._is_special:
            ans = self._check_nans(context=context)
            jeżeli ans:
                zwróć ans

        jeżeli context jest Nic:
            context = getcontext()

        jeżeli nie self oraz context.rounding != ROUND_FLOOR:
            # + (-0) = 0, wyjąwszy w ROUND_FLOOR rounding mode.
            ans = self.copy_abs()
        inaczej:
            ans = Decimal(self)

        zwróć ans._fix(context)

    def __abs__(self, round=Prawda, context=Nic):
        """Returns the absolute value of self.

        If the keyword argument 'round' jest false, do nie round.  The
        expression self.__abs__(round=Nieprawda) jest equivalent to
        self.copy_abs().
        """
        jeżeli nie round:
            zwróć self.copy_abs()

        jeżeli self._is_special:
            ans = self._check_nans(context=context)
            jeżeli ans:
                zwróć ans

        jeżeli self._sign:
            ans = self.__neg__(context=context)
        inaczej:
            ans = self.__pos__(context=context)

        zwróć ans

    def __add__(self, other, context=Nic):
        """Returns self + other.

        -INF + INF (or the reverse) cause InvalidOperation errors.
        """
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other

        jeżeli context jest Nic:
            context = getcontext()

        jeżeli self._is_special albo other._is_special:
            ans = self._check_nans(other, context)
            jeżeli ans:
                zwróć ans

            jeżeli self._isinfinity():
                # If both INF, same sign => same jako both, opposite => error.
                jeżeli self._sign != other._sign oraz other._isinfinity():
                    zwróć context._raise_error(InvalidOperation, '-INF + INF')
                zwróć Decimal(self)
            jeżeli other._isinfinity():
                zwróć Decimal(other)  # Can't both be infinity here

        exp = min(self._exp, other._exp)
        negativezero = 0
        jeżeli context.rounding == ROUND_FLOOR oraz self._sign != other._sign:
            # If the answer jest 0, the sign should be negative, w this case.
            negativezero = 1

        jeżeli nie self oraz nie other:
            sign = min(self._sign, other._sign)
            jeżeli negativezero:
                sign = 1
            ans = _dec_from_triple(sign, '0', exp)
            ans = ans._fix(context)
            zwróć ans
        jeżeli nie self:
            exp = max(exp, other._exp - context.prec-1)
            ans = other._rescale(exp, context.rounding)
            ans = ans._fix(context)
            zwróć ans
        jeżeli nie other:
            exp = max(exp, self._exp - context.prec-1)
            ans = self._rescale(exp, context.rounding)
            ans = ans._fix(context)
            zwróć ans

        op1 = _WorkRep(self)
        op2 = _WorkRep(other)
        op1, op2 = _normalize(op1, op2, context.prec)

        result = _WorkRep()
        jeżeli op1.sign != op2.sign:
            # Equal oraz opposite
            jeżeli op1.int == op2.int:
                ans = _dec_from_triple(negativezero, '0', exp)
                ans = ans._fix(context)
                zwróć ans
            jeżeli op1.int < op2.int:
                op1, op2 = op2, op1
                # OK, now abs(op1) > abs(op2)
            jeżeli op1.sign == 1:
                result.sign = 1
                op1.sign, op2.sign = op2.sign, op1.sign
            inaczej:
                result.sign = 0
                # So we know the sign, oraz op1 > 0.
        albo_inaczej op1.sign == 1:
            result.sign = 1
            op1.sign, op2.sign = (0, 0)
        inaczej:
            result.sign = 0
        # Now, op1 > abs(op2) > 0

        jeżeli op2.sign == 0:
            result.int = op1.int + op2.int
        inaczej:
            result.int = op1.int - op2.int

        result.exp = op1.exp
        ans = Decimal(result)
        ans = ans._fix(context)
        zwróć ans

    __radd__ = __add__

    def __sub__(self, other, context=Nic):
        """Return self - other"""
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other

        jeżeli self._is_special albo other._is_special:
            ans = self._check_nans(other, context=context)
            jeżeli ans:
                zwróć ans

        # self - other jest computed jako self + other.copy_negate()
        zwróć self.__add__(other.copy_negate(), context=context)

    def __rsub__(self, other, context=Nic):
        """Return other - self"""
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other

        zwróć other.__sub__(self, context=context)

    def __mul__(self, other, context=Nic):
        """Return self * other.

        (+-) INF * 0 (or its reverse) podnieś InvalidOperation.
        """
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other

        jeżeli context jest Nic:
            context = getcontext()

        resultsign = self._sign ^ other._sign

        jeżeli self._is_special albo other._is_special:
            ans = self._check_nans(other, context)
            jeżeli ans:
                zwróć ans

            jeżeli self._isinfinity():
                jeżeli nie other:
                    zwróć context._raise_error(InvalidOperation, '(+-)INF * 0')
                zwróć _SignedInfinity[resultsign]

            jeżeli other._isinfinity():
                jeżeli nie self:
                    zwróć context._raise_error(InvalidOperation, '0 * (+-)INF')
                zwróć _SignedInfinity[resultsign]

        resultexp = self._exp + other._exp

        # Special case dla multiplying by zero
        jeżeli nie self albo nie other:
            ans = _dec_from_triple(resultsign, '0', resultexp)
            # Fixing w case the exponent jest out of bounds
            ans = ans._fix(context)
            zwróć ans

        # Special case dla multiplying by power of 10
        jeżeli self._int == '1':
            ans = _dec_from_triple(resultsign, other._int, resultexp)
            ans = ans._fix(context)
            zwróć ans
        jeżeli other._int == '1':
            ans = _dec_from_triple(resultsign, self._int, resultexp)
            ans = ans._fix(context)
            zwróć ans

        op1 = _WorkRep(self)
        op2 = _WorkRep(other)

        ans = _dec_from_triple(resultsign, str(op1.int * op2.int), resultexp)
        ans = ans._fix(context)

        zwróć ans
    __rmul__ = __mul__

    def __truediv__(self, other, context=Nic):
        """Return self / other."""
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć NotImplemented

        jeżeli context jest Nic:
            context = getcontext()

        sign = self._sign ^ other._sign

        jeżeli self._is_special albo other._is_special:
            ans = self._check_nans(other, context)
            jeżeli ans:
                zwróć ans

            jeżeli self._isinfinity() oraz other._isinfinity():
                zwróć context._raise_error(InvalidOperation, '(+-)INF/(+-)INF')

            jeżeli self._isinfinity():
                zwróć _SignedInfinity[sign]

            jeżeli other._isinfinity():
                context._raise_error(Clamped, 'Division by infinity')
                zwróć _dec_from_triple(sign, '0', context.Etiny())

        # Special cases dla zeroes
        jeżeli nie other:
            jeżeli nie self:
                zwróć context._raise_error(DivisionUndefined, '0 / 0')
            zwróć context._raise_error(DivisionByZero, 'x / 0', sign)

        jeżeli nie self:
            exp = self._exp - other._exp
            coeff = 0
        inaczej:
            # OK, so neither = 0, INF albo NaN
            shift = len(other._int) - len(self._int) + context.prec + 1
            exp = self._exp - other._exp - shift
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            jeżeli shift >= 0:
                coeff, remainder = divmod(op1.int * 10**shift, op2.int)
            inaczej:
                coeff, remainder = divmod(op1.int, op2.int * 10**-shift)
            jeżeli remainder:
                # result jest nie exact; adjust to ensure correct rounding
                jeżeli coeff % 5 == 0:
                    coeff += 1
            inaczej:
                # result jest exact; get jako close to ideal exponent jako possible
                ideal_exp = self._exp - other._exp
                dopóki exp < ideal_exp oraz coeff % 10 == 0:
                    coeff //= 10
                    exp += 1

        ans = _dec_from_triple(sign, str(coeff), exp)
        zwróć ans._fix(context)

    def _divide(self, other, context):
        """Return (self // other, self % other), to context.prec precision.

        Assumes that neither self nor other jest a NaN, that self jest nie
        infinite oraz that other jest nonzero.
        """
        sign = self._sign ^ other._sign
        jeżeli other._isinfinity():
            ideal_exp = self._exp
        inaczej:
            ideal_exp = min(self._exp, other._exp)

        expdiff = self.adjusted() - other.adjusted()
        jeżeli nie self albo other._isinfinity() albo expdiff <= -2:
            zwróć (_dec_from_triple(sign, '0', 0),
                    self._rescale(ideal_exp, context.rounding))
        jeżeli expdiff <= context.prec:
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            jeżeli op1.exp >= op2.exp:
                op1.int *= 10**(op1.exp - op2.exp)
            inaczej:
                op2.int *= 10**(op2.exp - op1.exp)
            q, r = divmod(op1.int, op2.int)
            jeżeli q < 10**context.prec:
                zwróć (_dec_from_triple(sign, str(q), 0),
                        _dec_from_triple(self._sign, str(r), ideal_exp))

        # Here the quotient jest too large to be representable
        ans = context._raise_error(DivisionImpossible,
                                   'quotient too large w //, % albo divmod')
        zwróć ans, ans

    def __rtruediv__(self, other, context=Nic):
        """Swaps self/other oraz returns __truediv__."""
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other
        zwróć other.__truediv__(self, context=context)

    def __divmod__(self, other, context=Nic):
        """
        Return (self // other, self % other)
        """
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other

        jeżeli context jest Nic:
            context = getcontext()

        ans = self._check_nans(other, context)
        jeżeli ans:
            zwróć (ans, ans)

        sign = self._sign ^ other._sign
        jeżeli self._isinfinity():
            jeżeli other._isinfinity():
                ans = context._raise_error(InvalidOperation, 'divmod(INF, INF)')
                zwróć ans, ans
            inaczej:
                zwróć (_SignedInfinity[sign],
                        context._raise_error(InvalidOperation, 'INF % x'))

        jeżeli nie other:
            jeżeli nie self:
                ans = context._raise_error(DivisionUndefined, 'divmod(0, 0)')
                zwróć ans, ans
            inaczej:
                zwróć (context._raise_error(DivisionByZero, 'x // 0', sign),
                        context._raise_error(InvalidOperation, 'x % 0'))

        quotient, remainder = self._divide(other, context)
        remainder = remainder._fix(context)
        zwróć quotient, remainder

    def __rdivmod__(self, other, context=Nic):
        """Swaps self/other oraz returns __divmod__."""
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other
        zwróć other.__divmod__(self, context=context)

    def __mod__(self, other, context=Nic):
        """
        self % other
        """
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other

        jeżeli context jest Nic:
            context = getcontext()

        ans = self._check_nans(other, context)
        jeżeli ans:
            zwróć ans

        jeżeli self._isinfinity():
            zwróć context._raise_error(InvalidOperation, 'INF % x')
        albo_inaczej nie other:
            jeżeli self:
                zwróć context._raise_error(InvalidOperation, 'x % 0')
            inaczej:
                zwróć context._raise_error(DivisionUndefined, '0 % 0')

        remainder = self._divide(other, context)[1]
        remainder = remainder._fix(context)
        zwróć remainder

    def __rmod__(self, other, context=Nic):
        """Swaps self/other oraz returns __mod__."""
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other
        zwróć other.__mod__(self, context=context)

    def remainder_near(self, other, context=Nic):
        """
        Remainder nearest to 0-  abs(remainder-near) <= other/2
        """
        jeżeli context jest Nic:
            context = getcontext()

        other = _convert_other(other, podnieśit=Prawda)

        ans = self._check_nans(other, context)
        jeżeli ans:
            zwróć ans

        # self == +/-infinity -> InvalidOperation
        jeżeli self._isinfinity():
            zwróć context._raise_error(InvalidOperation,
                                        'remainder_near(infinity, x)')

        # other == 0 -> either InvalidOperation albo DivisionUndefined
        jeżeli nie other:
            jeżeli self:
                zwróć context._raise_error(InvalidOperation,
                                            'remainder_near(x, 0)')
            inaczej:
                zwróć context._raise_error(DivisionUndefined,
                                            'remainder_near(0, 0)')

        # other = +/-infinity -> remainder = self
        jeżeli other._isinfinity():
            ans = Decimal(self)
            zwróć ans._fix(context)

        # self = 0 -> remainder = self, przy ideal exponent
        ideal_exponent = min(self._exp, other._exp)
        jeżeli nie self:
            ans = _dec_from_triple(self._sign, '0', ideal_exponent)
            zwróć ans._fix(context)

        # catch most cases of large albo small quotient
        expdiff = self.adjusted() - other.adjusted()
        jeżeli expdiff >= context.prec + 1:
            # expdiff >= prec+1 => abs(self/other) > 10**prec
            zwróć context._raise_error(DivisionImpossible)
        jeżeli expdiff <= -2:
            # expdiff <= -2 => abs(self/other) < 0.1
            ans = self._rescale(ideal_exponent, context.rounding)
            zwróć ans._fix(context)

        # adjust both arguments to have the same exponent, then divide
        op1 = _WorkRep(self)
        op2 = _WorkRep(other)
        jeżeli op1.exp >= op2.exp:
            op1.int *= 10**(op1.exp - op2.exp)
        inaczej:
            op2.int *= 10**(op2.exp - op1.exp)
        q, r = divmod(op1.int, op2.int)
        # remainder jest r*10**ideal_exponent; other jest +/-op2.int *
        # 10**ideal_exponent.   Apply correction to ensure that
        # abs(remainder) <= abs(other)/2
        jeżeli 2*r + (q&1) > op2.int:
            r -= op2.int
            q += 1

        jeżeli q >= 10**context.prec:
            zwróć context._raise_error(DivisionImpossible)

        # result has same sign jako self unless r jest negative
        sign = self._sign
        jeżeli r < 0:
            sign = 1-sign
            r = -r

        ans = _dec_from_triple(sign, str(r), ideal_exponent)
        zwróć ans._fix(context)

    def __floordiv__(self, other, context=Nic):
        """self // other"""
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other

        jeżeli context jest Nic:
            context = getcontext()

        ans = self._check_nans(other, context)
        jeżeli ans:
            zwróć ans

        jeżeli self._isinfinity():
            jeżeli other._isinfinity():
                zwróć context._raise_error(InvalidOperation, 'INF // INF')
            inaczej:
                zwróć _SignedInfinity[self._sign ^ other._sign]

        jeżeli nie other:
            jeżeli self:
                zwróć context._raise_error(DivisionByZero, 'x // 0',
                                            self._sign ^ other._sign)
            inaczej:
                zwróć context._raise_error(DivisionUndefined, '0 // 0')

        zwróć self._divide(other, context)[0]

    def __rfloordiv__(self, other, context=Nic):
        """Swaps self/other oraz returns __floordiv__."""
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other
        zwróć other.__floordiv__(self, context=context)

    def __float__(self):
        """Float representation."""
        jeżeli self._isnan():
            jeżeli self.is_snan():
                podnieś ValueError("Cannot convert signaling NaN to float")
            s = "-nan" jeżeli self._sign inaczej "nan"
        inaczej:
            s = str(self)
        zwróć float(s)

    def __int__(self):
        """Converts self to an int, truncating jeżeli necessary."""
        jeżeli self._is_special:
            jeżeli self._isnan():
                podnieś ValueError("Cannot convert NaN to integer")
            albo_inaczej self._isinfinity():
                podnieś OverflowError("Cannot convert infinity to integer")
        s = (-1)**self._sign
        jeżeli self._exp >= 0:
            zwróć s*int(self._int)*10**self._exp
        inaczej:
            zwróć s*int(self._int[:self._exp] albo '0')

    __trunc__ = __int__

    def real(self):
        zwróć self
    real = property(real)

    def imag(self):
        zwróć Decimal(0)
    imag = property(imag)

    def conjugate(self):
        zwróć self

    def __complex__(self):
        zwróć complex(float(self))

    def _fix_nan(self, context):
        """Decapitate the payload of a NaN to fit the context"""
        payload = self._int

        # maximum length of payload jest precision jeżeli clamp=0,
        # precision-1 jeżeli clamp=1.
        max_payload_len = context.prec - context.clamp
        jeżeli len(payload) > max_payload_len:
            payload = payload[len(payload)-max_payload_len:].lstrip('0')
            zwróć _dec_from_triple(self._sign, payload, self._exp, Prawda)
        zwróć Decimal(self)

    def _fix(self, context):
        """Round jeżeli it jest necessary to keep self within prec precision.

        Rounds oraz fixes the exponent.  Does nie podnieś on a sNaN.

        Arguments:
        self - Decimal instance
        context - context used.
        """

        jeżeli self._is_special:
            jeżeli self._isnan():
                # decapitate payload jeżeli necessary
                zwróć self._fix_nan(context)
            inaczej:
                # self jest +/-Infinity; zwróć unaltered
                zwróć Decimal(self)

        # jeżeli self jest zero then exponent should be between Etiny oraz
        # Emax jeżeli clamp==0, oraz between Etiny oraz Etop jeżeli clamp==1.
        Etiny = context.Etiny()
        Etop = context.Etop()
        jeżeli nie self:
            exp_max = [context.Emax, Etop][context.clamp]
            new_exp = min(max(self._exp, Etiny), exp_max)
            jeżeli new_exp != self._exp:
                context._raise_error(Clamped)
                zwróć _dec_from_triple(self._sign, '0', new_exp)
            inaczej:
                zwróć Decimal(self)

        # exp_min jest the smallest allowable exponent of the result,
        # equal to max(self.adjusted()-context.prec+1, Etiny)
        exp_min = len(self._int) + self._exp - context.prec
        jeżeli exp_min > Etop:
            # overflow: exp_min > Etop iff self.adjusted() > Emax
            ans = context._raise_error(Overflow, 'above Emax', self._sign)
            context._raise_error(Inexact)
            context._raise_error(Rounded)
            zwróć ans

        self_is_subnormal = exp_min < Etiny
        jeżeli self_is_subnormal:
            exp_min = Etiny

        # round jeżeli self has too many digits
        jeżeli self._exp < exp_min:
            digits = len(self._int) + self._exp - exp_min
            jeżeli digits < 0:
                self = _dec_from_triple(self._sign, '1', exp_min-1)
                digits = 0
            rounding_method = self._pick_rounding_function[context.rounding]
            changed = rounding_method(self, digits)
            coeff = self._int[:digits] albo '0'
            jeżeli changed > 0:
                coeff = str(int(coeff)+1)
                jeżeli len(coeff) > context.prec:
                    coeff = coeff[:-1]
                    exp_min += 1

            # check whether the rounding pushed the exponent out of range
            jeżeli exp_min > Etop:
                ans = context._raise_error(Overflow, 'above Emax', self._sign)
            inaczej:
                ans = _dec_from_triple(self._sign, coeff, exp_min)

            # podnieś the appropriate signals, taking care to respect
            # the precedence described w the specification
            jeżeli changed oraz self_is_subnormal:
                context._raise_error(Underflow)
            jeżeli self_is_subnormal:
                context._raise_error(Subnormal)
            jeżeli changed:
                context._raise_error(Inexact)
            context._raise_error(Rounded)
            jeżeli nie ans:
                # podnieś Clamped on underflow to 0
                context._raise_error(Clamped)
            zwróć ans

        jeżeli self_is_subnormal:
            context._raise_error(Subnormal)

        # fold down jeżeli clamp == 1 oraz self has too few digits
        jeżeli context.clamp == 1 oraz self._exp > Etop:
            context._raise_error(Clamped)
            self_padded = self._int + '0'*(self._exp - Etop)
            zwróć _dec_from_triple(self._sign, self_padded, Etop)

        # here self was representable to begin with; zwróć unchanged
        zwróć Decimal(self)

    # dla each of the rounding functions below:
    #   self jest a finite, nonzero Decimal
    #   prec jest an integer satisfying 0 <= prec < len(self._int)
    #
    # each function returns either -1, 0, albo 1, jako follows:
    #   1 indicates that self should be rounded up (away z zero)
    #   0 indicates that self should be truncated, oraz that all the
    #     digits to be truncated are zeros (so the value jest unchanged)
    #  -1 indicates that there are nonzero digits to be truncated

    def _round_down(self, prec):
        """Also known jako round-towards-0, truncate."""
        jeżeli _all_zeros(self._int, prec):
            zwróć 0
        inaczej:
            zwróć -1

    def _round_up(self, prec):
        """Rounds away z 0."""
        zwróć -self._round_down(prec)

    def _round_half_up(self, prec):
        """Rounds 5 up (away z 0)"""
        jeżeli self._int[prec] w '56789':
            zwróć 1
        albo_inaczej _all_zeros(self._int, prec):
            zwróć 0
        inaczej:
            zwróć -1

    def _round_half_down(self, prec):
        """Round 5 down"""
        jeżeli _exact_half(self._int, prec):
            zwróć -1
        inaczej:
            zwróć self._round_half_up(prec)

    def _round_half_even(self, prec):
        """Round 5 to even, rest to nearest."""
        jeżeli _exact_half(self._int, prec) oraz \
                (prec == 0 albo self._int[prec-1] w '02468'):
            zwróć -1
        inaczej:
            zwróć self._round_half_up(prec)

    def _round_ceiling(self, prec):
        """Rounds up (nie away z 0 jeżeli negative.)"""
        jeżeli self._sign:
            zwróć self._round_down(prec)
        inaczej:
            zwróć -self._round_down(prec)

    def _round_floor(self, prec):
        """Rounds down (nie towards 0 jeżeli negative)"""
        jeżeli nie self._sign:
            zwróć self._round_down(prec)
        inaczej:
            zwróć -self._round_down(prec)

    def _round_05up(self, prec):
        """Round down unless digit prec-1 jest 0 albo 5."""
        jeżeli prec oraz self._int[prec-1] nie w '05':
            zwróć self._round_down(prec)
        inaczej:
            zwróć -self._round_down(prec)

    _pick_rounding_function = dict(
        ROUND_DOWN = _round_down,
        ROUND_UP = _round_up,
        ROUND_HALF_UP = _round_half_up,
        ROUND_HALF_DOWN = _round_half_down,
        ROUND_HALF_EVEN = _round_half_even,
        ROUND_CEILING = _round_ceiling,
        ROUND_FLOOR = _round_floor,
        ROUND_05UP = _round_05up,
    )

    def __round__(self, n=Nic):
        """Round self to the nearest integer, albo to a given precision.

        If only one argument jest supplied, round a finite Decimal
        instance self to the nearest integer.  If self jest infinite albo
        a NaN then a Python exception jest podnieśd.  If self jest finite
        oraz lies exactly halfway between two integers then it jest
        rounded to the integer przy even last digit.

        >>> round(Decimal('123.456'))
        123
        >>> round(Decimal('-456.789'))
        -457
        >>> round(Decimal('-3.0'))
        -3
        >>> round(Decimal('2.5'))
        2
        >>> round(Decimal('3.5'))
        4
        >>> round(Decimal('Inf'))
        Traceback (most recent call last):
          ...
        OverflowError: cannot round an infinity
        >>> round(Decimal('NaN'))
        Traceback (most recent call last):
          ...
        ValueError: cannot round a NaN

        If a second argument n jest supplied, self jest rounded to n
        decimal places using the rounding mode dla the current
        context.

        For an integer n, round(self, -n) jest exactly equivalent to
        self.quantize(Decimal('1En')).

        >>> round(Decimal('123.456'), 0)
        Decimal('123')
        >>> round(Decimal('123.456'), 2)
        Decimal('123.46')
        >>> round(Decimal('123.456'), -2)
        Decimal('1E+2')
        >>> round(Decimal('-Infinity'), 37)
        Decimal('NaN')
        >>> round(Decimal('sNaN123'), 0)
        Decimal('NaN123')

        """
        jeżeli n jest nie Nic:
            # two-argument form: use the equivalent quantize call
            jeżeli nie isinstance(n, int):
                podnieś TypeError('Second argument to round should be integral')
            exp = _dec_from_triple(0, '1', -n)
            zwróć self.quantize(exp)

        # one-argument form
        jeżeli self._is_special:
            jeżeli self.is_nan():
                podnieś ValueError("cannot round a NaN")
            inaczej:
                podnieś OverflowError("cannot round an infinity")
        zwróć int(self._rescale(0, ROUND_HALF_EVEN))

    def __floor__(self):
        """Return the floor of self, jako an integer.

        For a finite Decimal instance self, zwróć the greatest
        integer n such that n <= self.  If self jest infinite albo a NaN
        then a Python exception jest podnieśd.

        """
        jeżeli self._is_special:
            jeżeli self.is_nan():
                podnieś ValueError("cannot round a NaN")
            inaczej:
                podnieś OverflowError("cannot round an infinity")
        zwróć int(self._rescale(0, ROUND_FLOOR))

    def __ceil__(self):
        """Return the ceiling of self, jako an integer.

        For a finite Decimal instance self, zwróć the least integer n
        such that n >= self.  If self jest infinite albo a NaN then a
        Python exception jest podnieśd.

        """
        jeżeli self._is_special:
            jeżeli self.is_nan():
                podnieś ValueError("cannot round a NaN")
            inaczej:
                podnieś OverflowError("cannot round an infinity")
        zwróć int(self._rescale(0, ROUND_CEILING))

    def fma(self, other, third, context=Nic):
        """Fused multiply-add.

        Returns self*other+third przy no rounding of the intermediate
        product self*other.

        self oraz other are multiplied together, przy no rounding of
        the result.  The third operand jest then added to the result,
        oraz a single final rounding jest performed.
        """

        other = _convert_other(other, podnieśit=Prawda)
        third = _convert_other(third, podnieśit=Prawda)

        # compute product; podnieś InvalidOperation jeżeli either operand jest
        # a signaling NaN albo jeżeli the product jest zero times infinity.
        jeżeli self._is_special albo other._is_special:
            jeżeli context jest Nic:
                context = getcontext()
            jeżeli self._exp == 'N':
                zwróć context._raise_error(InvalidOperation, 'sNaN', self)
            jeżeli other._exp == 'N':
                zwróć context._raise_error(InvalidOperation, 'sNaN', other)
            jeżeli self._exp == 'n':
                product = self
            albo_inaczej other._exp == 'n':
                product = other
            albo_inaczej self._exp == 'F':
                jeżeli nie other:
                    zwróć context._raise_error(InvalidOperation,
                                                'INF * 0 w fma')
                product = _SignedInfinity[self._sign ^ other._sign]
            albo_inaczej other._exp == 'F':
                jeżeli nie self:
                    zwróć context._raise_error(InvalidOperation,
                                                '0 * INF w fma')
                product = _SignedInfinity[self._sign ^ other._sign]
        inaczej:
            product = _dec_from_triple(self._sign ^ other._sign,
                                       str(int(self._int) * int(other._int)),
                                       self._exp + other._exp)

        zwróć product.__add__(third, context)

    def _power_modulo(self, other, modulo, context=Nic):
        """Three argument version of __pow__"""

        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other
        modulo = _convert_other(modulo)
        jeżeli modulo jest NotImplemented:
            zwróć modulo

        jeżeli context jest Nic:
            context = getcontext()

        # deal przy NaNs: jeżeli there are any sNaNs then first one wins,
        # (i.e. behaviour dla NaNs jest identical to that of fma)
        self_is_nan = self._isnan()
        other_is_nan = other._isnan()
        modulo_is_nan = modulo._isnan()
        jeżeli self_is_nan albo other_is_nan albo modulo_is_nan:
            jeżeli self_is_nan == 2:
                zwróć context._raise_error(InvalidOperation, 'sNaN',
                                        self)
            jeżeli other_is_nan == 2:
                zwróć context._raise_error(InvalidOperation, 'sNaN',
                                        other)
            jeżeli modulo_is_nan == 2:
                zwróć context._raise_error(InvalidOperation, 'sNaN',
                                        modulo)
            jeżeli self_is_nan:
                zwróć self._fix_nan(context)
            jeżeli other_is_nan:
                zwróć other._fix_nan(context)
            zwróć modulo._fix_nan(context)

        # check inputs: we apply same restrictions jako Python's pow()
        jeżeli nie (self._isinteger() oraz
                other._isinteger() oraz
                modulo._isinteger()):
            zwróć context._raise_error(InvalidOperation,
                                        'pow() 3rd argument nie allowed '
                                        'unless all arguments are integers')
        jeżeli other < 0:
            zwróć context._raise_error(InvalidOperation,
                                        'pow() 2nd argument cannot be '
                                        'negative when 3rd argument specified')
        jeżeli nie modulo:
            zwróć context._raise_error(InvalidOperation,
                                        'pow() 3rd argument cannot be 0')

        # additional restriction dla decimal: the modulus must be less
        # than 10**prec w absolute value
        jeżeli modulo.adjusted() >= context.prec:
            zwróć context._raise_error(InvalidOperation,
                                        'insufficient precision: pow() 3rd '
                                        'argument must nie have more than '
                                        'precision digits')

        # define 0**0 == NaN, dla consistency przy two-argument pow
        # (even though it hurts!)
        jeżeli nie other oraz nie self:
            zwróć context._raise_error(InvalidOperation,
                                        'at least one of pow() 1st argument '
                                        'and 2nd argument must be nonzero ;'
                                        '0**0 jest nie defined')

        # compute sign of result
        jeżeli other._iseven():
            sign = 0
        inaczej:
            sign = self._sign

        # convert modulo to a Python integer, oraz self oraz other to
        # Decimal integers (i.e. force their exponents to be >= 0)
        modulo = abs(int(modulo))
        base = _WorkRep(self.to_integral_value())
        exponent = _WorkRep(other.to_integral_value())

        # compute result using integer pow()
        base = (base.int % modulo * pow(10, base.exp, modulo)) % modulo
        dla i w range(exponent.exp):
            base = pow(base, 10, modulo)
        base = pow(base, exponent.int, modulo)

        zwróć _dec_from_triple(sign, str(base), 0)

    def _power_exact(self, other, p):
        """Attempt to compute self**other exactly.

        Given Decimals self oraz other oraz an integer p, attempt to
        compute an exact result dla the power self**other, przy p
        digits of precision.  Return Nic jeżeli self**other jest nie
        exactly representable w p digits.

        Assumes that elimination of special cases has already been
        performed: self oraz other must both be nonspecial; self must
        be positive oraz nie numerically equal to 1; other must be
        nonzero.  For efficiency, other._exp should nie be too large,
        so that 10**abs(other._exp) jest a feasible calculation."""

        # In the comments below, we write x dla the value of self oraz y dla the
        # value of other.  Write x = xc*10**xe oraz abs(y) = yc*10**ye, przy xc
        # oraz yc positive integers nie divisible by 10.

        # The main purpose of this method jest to identify the *failure*
        # of x**y to be exactly representable przy jako little effort as
        # possible.  So we look dla cheap oraz easy tests that
        # eliminate the possibility of x**y being exact.  Only jeżeli all
        # these tests are dalejed do we go on to actually compute x**y.

        # Here's the main idea.  Express y jako a rational number m/n, przy m oraz
        # n relatively prime oraz n>0.  Then dla x**y to be exactly
        # representable (at *any* precision), xc must be the nth power of a
        # positive integer oraz xe must be divisible by n.  If y jest negative
        # then additionally xc must be a power of either 2 albo 5, hence a power
        # of 2**n albo 5**n.
        #
        # There's a limit to how small |y| can be: jeżeli y=m/n jako above
        # then:
        #
        #  (1) jeżeli xc != 1 then dla the result to be representable we
        #      need xc**(1/n) >= 2, oraz hence also xc**|y| >= 2.  So
        #      jeżeli |y| <= 1/nbits(xc) then xc < 2**nbits(xc) <=
        #      2**(1/|y|), hence xc**|y| < 2 oraz the result jest nie
        #      representable.
        #
        #  (2) jeżeli xe != 0, |xe|*(1/n) >= 1, so |xe|*|y| >= 1.  Hence if
        #      |y| < 1/|xe| then the result jest nie representable.
        #
        # Note that since x jest nie equal to 1, at least one of (1) oraz
        # (2) must apply.  Now |y| < 1/nbits(xc) iff |yc|*nbits(xc) <
        # 10**-ye iff len(str(|yc|*nbits(xc)) <= -ye.
        #
        # There's also a limit to how large y can be, at least jeżeli it's
        # positive: the normalized result will have coefficient xc**y,
        # so jeżeli it's representable then xc**y < 10**p, oraz y <
        # p/log10(xc).  Hence jeżeli y*log10(xc) >= p then the result jest
        # nie exactly representable.

        # jeżeli len(str(abs(yc*xe)) <= -ye then abs(yc*xe) < 10**-ye,
        # so |y| < 1/xe oraz the result jest nie representable.
        # Similarly, len(str(abs(yc)*xc_bits)) <= -ye implies |y|
        # < 1/nbits(xc).

        x = _WorkRep(self)
        xc, xe = x.int, x.exp
        dopóki xc % 10 == 0:
            xc //= 10
            xe += 1

        y = _WorkRep(other)
        yc, ye = y.int, y.exp
        dopóki yc % 10 == 0:
            yc //= 10
            ye += 1

        # case where xc == 1: result jest 10**(xe*y), przy xe*y
        # required to be an integer
        jeżeli xc == 1:
            xe *= yc
            # result jest now 10**(xe * 10**ye);  xe * 10**ye must be integral
            dopóki xe % 10 == 0:
                xe //= 10
                ye += 1
            jeżeli ye < 0:
                zwróć Nic
            exponent = xe * 10**ye
            jeżeli y.sign == 1:
                exponent = -exponent
            # jeżeli other jest a nonnegative integer, use ideal exponent
            jeżeli other._isinteger() oraz other._sign == 0:
                ideal_exponent = self._exp*int(other)
                zeros = min(exponent-ideal_exponent, p-1)
            inaczej:
                zeros = 0
            zwróć _dec_from_triple(0, '1' + '0'*zeros, exponent-zeros)

        # case where y jest negative: xc must be either a power
        # of 2 albo a power of 5.
        jeżeli y.sign == 1:
            last_digit = xc % 10
            jeżeli last_digit w (2,4,6,8):
                # quick test dla power of 2
                jeżeli xc & -xc != xc:
                    zwróć Nic
                # now xc jest a power of 2; e jest its exponent
                e = _nbits(xc)-1

                # We now have:
                #
                #   x = 2**e * 10**xe, e > 0, oraz y < 0.
                #
                # The exact result is:
                #
                #   x**y = 5**(-e*y) * 10**(e*y + xe*y)
                #
                # provided that both e*y oraz xe*y are integers.  Note that if
                # 5**(-e*y) >= 10**p, then the result can't be expressed
                # exactly przy p digits of precision.
                #
                # Using the above, we can guard against large values of ye.
                # 93/65 jest an upper bound dla log(10)/log(5), so if
                #
                #   ye >= len(str(93*p//65))
                #
                # then
                #
                #   -e*y >= -y >= 10**ye > 93*p/65 > p*log(10)/log(5),
                #
                # so 5**(-e*y) >= 10**p, oraz the coefficient of the result
                # can't be expressed w p digits.

                # emax >= largest e such that 5**e < 10**p.
                emax = p*93//65
                jeżeli ye >= len(str(emax)):
                    zwróć Nic

                # Find -e*y oraz -xe*y; both must be integers
                e = _decimal_lshift_exact(e * yc, ye)
                xe = _decimal_lshift_exact(xe * yc, ye)
                jeżeli e jest Nic albo xe jest Nic:
                    zwróć Nic

                jeżeli e > emax:
                    zwróć Nic
                xc = 5**e

            albo_inaczej last_digit == 5:
                # e >= log_5(xc) jeżeli xc jest a power of 5; we have
                # equality all the way up to xc=5**2658
                e = _nbits(xc)*28//65
                xc, remainder = divmod(5**e, xc)
                jeżeli remainder:
                    zwróć Nic
                dopóki xc % 5 == 0:
                    xc //= 5
                    e -= 1

                # Guard against large values of ye, using the same logic jako w
                # the 'xc jest a power of 2' branch.  10/3 jest an upper bound for
                # log(10)/log(2).
                emax = p*10//3
                jeżeli ye >= len(str(emax)):
                    zwróć Nic

                e = _decimal_lshift_exact(e * yc, ye)
                xe = _decimal_lshift_exact(xe * yc, ye)
                jeżeli e jest Nic albo xe jest Nic:
                    zwróć Nic

                jeżeli e > emax:
                    zwróć Nic
                xc = 2**e
            inaczej:
                zwróć Nic

            jeżeli xc >= 10**p:
                zwróć Nic
            xe = -e-xe
            zwróć _dec_from_triple(0, str(xc), xe)

        # now y jest positive; find m oraz n such that y = m/n
        jeżeli ye >= 0:
            m, n = yc*10**ye, 1
        inaczej:
            jeżeli xe != 0 oraz len(str(abs(yc*xe))) <= -ye:
                zwróć Nic
            xc_bits = _nbits(xc)
            jeżeli xc != 1 oraz len(str(abs(yc)*xc_bits)) <= -ye:
                zwróć Nic
            m, n = yc, 10**(-ye)
            dopóki m % 2 == n % 2 == 0:
                m //= 2
                n //= 2
            dopóki m % 5 == n % 5 == 0:
                m //= 5
                n //= 5

        # compute nth root of xc*10**xe
        jeżeli n > 1:
            # jeżeli 1 < xc < 2**n then xc isn't an nth power
            jeżeli xc != 1 oraz xc_bits <= n:
                zwróć Nic

            xe, rem = divmod(xe, n)
            jeżeli rem != 0:
                zwróć Nic

            # compute nth root of xc using Newton's method
            a = 1 << -(-_nbits(xc)//n) # initial estimate
            dopóki Prawda:
                q, r = divmod(xc, a**(n-1))
                jeżeli a <= q:
                    przerwij
                inaczej:
                    a = (a*(n-1) + q)//n
            jeżeli nie (a == q oraz r == 0):
                zwróć Nic
            xc = a

        # now xc*10**xe jest the nth root of the original xc*10**xe
        # compute mth power of xc*10**xe

        # jeżeli m > p*100//_log10_lb(xc) then m > p/log10(xc), hence xc**m >
        # 10**p oraz the result jest nie representable.
        jeżeli xc > 1 oraz m > p*100//_log10_lb(xc):
            zwróć Nic
        xc = xc**m
        xe *= m
        jeżeli xc > 10**p:
            zwróć Nic

        # by this point the result *is* exactly representable
        # adjust the exponent to get jako close jako possible to the ideal
        # exponent, jeżeli necessary
        str_xc = str(xc)
        jeżeli other._isinteger() oraz other._sign == 0:
            ideal_exponent = self._exp*int(other)
            zeros = min(xe-ideal_exponent, p-len(str_xc))
        inaczej:
            zeros = 0
        zwróć _dec_from_triple(0, str_xc+'0'*zeros, xe-zeros)

    def __pow__(self, other, modulo=Nic, context=Nic):
        """Return self ** other [ % modulo].

        With two arguments, compute self**other.

        With three arguments, compute (self**other) % modulo.  For the
        three argument form, the following restrictions on the
        arguments hold:

         - all three arguments must be integral
         - other must be nonnegative
         - either self albo other (or both) must be nonzero
         - modulo must be nonzero oraz must have at most p digits,
           where p jest the context precision.

        If any of these restrictions jest violated the InvalidOperation
        flag jest podnieśd.

        The result of pow(self, other, modulo) jest identical to the
        result that would be obtained by computing (self**other) %
        modulo przy unbounded precision, but jest computed more
        efficiently.  It jest always exact.
        """

        jeżeli modulo jest nie Nic:
            zwróć self._power_modulo(other, modulo, context)

        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other

        jeżeli context jest Nic:
            context = getcontext()

        # either argument jest a NaN => result jest NaN
        ans = self._check_nans(other, context)
        jeżeli ans:
            zwróć ans

        # 0**0 = NaN (!), x**0 = 1 dla nonzero x (including +/-Infinity)
        jeżeli nie other:
            jeżeli nie self:
                zwróć context._raise_error(InvalidOperation, '0 ** 0')
            inaczej:
                zwróć _One

        # result has sign 1 iff self._sign jest 1 oraz other jest an odd integer
        result_sign = 0
        jeżeli self._sign == 1:
            jeżeli other._isinteger():
                jeżeli nie other._iseven():
                    result_sign = 1
            inaczej:
                # -ve**noninteger = NaN
                # (-0)**noninteger = 0**noninteger
                jeżeli self:
                    zwróć context._raise_error(InvalidOperation,
                        'x ** y przy x negative oraz y nie an integer')
            # negate self, without doing any unwanted rounding
            self = self.copy_negate()

        # 0**(+ve albo Inf)= 0; 0**(-ve albo -Inf) = Infinity
        jeżeli nie self:
            jeżeli other._sign == 0:
                zwróć _dec_from_triple(result_sign, '0', 0)
            inaczej:
                zwróć _SignedInfinity[result_sign]

        # Inf**(+ve albo Inf) = Inf; Inf**(-ve albo -Inf) = 0
        jeżeli self._isinfinity():
            jeżeli other._sign == 0:
                zwróć _SignedInfinity[result_sign]
            inaczej:
                zwróć _dec_from_triple(result_sign, '0', 0)

        # 1**other = 1, but the choice of exponent oraz the flags
        # depend on the exponent of self, oraz on whether other jest a
        # positive integer, a negative integer, albo neither
        jeżeli self == _One:
            jeżeli other._isinteger():
                # exp = max(self._exp*max(int(other), 0),
                # 1-context.prec) but evaluating int(other) directly
                # jest dangerous until we know other jest small (other
                # could be 1e999999999)
                jeżeli other._sign == 1:
                    multiplier = 0
                albo_inaczej other > context.prec:
                    multiplier = context.prec
                inaczej:
                    multiplier = int(other)

                exp = self._exp * multiplier
                jeżeli exp < 1-context.prec:
                    exp = 1-context.prec
                    context._raise_error(Rounded)
            inaczej:
                context._raise_error(Inexact)
                context._raise_error(Rounded)
                exp = 1-context.prec

            zwróć _dec_from_triple(result_sign, '1'+'0'*-exp, exp)

        # compute adjusted exponent of self
        self_adj = self.adjusted()

        # self ** infinity jest infinity jeżeli self > 1, 0 jeżeli self < 1
        # self ** -infinity jest infinity jeżeli self < 1, 0 jeżeli self > 1
        jeżeli other._isinfinity():
            jeżeli (other._sign == 0) == (self_adj < 0):
                zwróć _dec_from_triple(result_sign, '0', 0)
            inaczej:
                zwróć _SignedInfinity[result_sign]

        # z here on, the result always goes through the call
        # to _fix at the end of this function.
        ans = Nic
        exact = Nieprawda

        # crude test to catch cases of extreme overflow/underflow.  If
        # log10(self)*other >= 10**bound oraz bound >= len(str(Emax))
        # then 10**bound >= 10**len(str(Emax)) >= Emax+1 oraz hence
        # self**other >= 10**(Emax+1), so overflow occurs.  The test
        # dla underflow jest similar.
        bound = self._log10_exp_bound() + other.adjusted()
        jeżeli (self_adj >= 0) == (other._sign == 0):
            # self > 1 oraz other +ve, albo self < 1 oraz other -ve
            # possibility of overflow
            jeżeli bound >= len(str(context.Emax)):
                ans = _dec_from_triple(result_sign, '1', context.Emax+1)
        inaczej:
            # self > 1 oraz other -ve, albo self < 1 oraz other +ve
            # possibility of underflow to 0
            Etiny = context.Etiny()
            jeżeli bound >= len(str(-Etiny)):
                ans = _dec_from_triple(result_sign, '1', Etiny-1)

        # try dla an exact result przy precision +1
        jeżeli ans jest Nic:
            ans = self._power_exact(other, context.prec + 1)
            jeżeli ans jest nie Nic:
                jeżeli result_sign == 1:
                    ans = _dec_from_triple(1, ans._int, ans._exp)
                exact = Prawda

        # usual case: inexact result, x**y computed directly jako exp(y*log(x))
        jeżeli ans jest Nic:
            p = context.prec
            x = _WorkRep(self)
            xc, xe = x.int, x.exp
            y = _WorkRep(other)
            yc, ye = y.int, y.exp
            jeżeli y.sign == 1:
                yc = -yc

            # compute correctly rounded result:  start przy precision +3,
            # then increase precision until result jest unambiguously roundable
            extra = 3
            dopóki Prawda:
                coeff, exp = _dpower(xc, xe, yc, ye, p+extra)
                jeżeli coeff % (5*10**(len(str(coeff))-p-1)):
                    przerwij
                extra += 3

            ans = _dec_from_triple(result_sign, str(coeff), exp)

        # unlike exp, ln oraz log10, the power function respects the
        # rounding mode; no need to switch to ROUND_HALF_EVEN here

        # There's a difficulty here when 'other' jest nie an integer oraz
        # the result jest exact.  In this case, the specification
        # requires that the Inexact flag be podnieśd (in spite of
        # exactness), but since the result jest exact _fix won't do this
        # dla us.  (Correspondingly, the Underflow signal should also
        # be podnieśd dla subnormal results.)  We can't directly podnieś
        # these signals either before albo after calling _fix, since
        # that would violate the precedence dla signals.  So we wrap
        # the ._fix call w a temporary context, oraz reraise
        # afterwards.
        jeżeli exact oraz nie other._isinteger():
            # pad przy zeros up to length context.prec+1 jeżeli necessary; this
            # ensures that the Rounded signal will be podnieśd.
            jeżeli len(ans._int) <= context.prec:
                expdiff = context.prec + 1 - len(ans._int)
                ans = _dec_from_triple(ans._sign, ans._int+'0'*expdiff,
                                       ans._exp-expdiff)

            # create a copy of the current context, przy cleared flags/traps
            newcontext = context.copy()
            newcontext.clear_flags()
            dla exception w _signals:
                newcontext.traps[exception] = 0

            # round w the new context
            ans = ans._fix(newcontext)

            # podnieś Inexact, oraz jeżeli necessary, Underflow
            newcontext._raise_error(Inexact)
            jeżeli newcontext.flags[Subnormal]:
                newcontext._raise_error(Underflow)

            # propagate signals to the original context; _fix could
            # have podnieśd any of Overflow, Underflow, Subnormal,
            # Inexact, Rounded, Clamped.  Overflow needs the correct
            # arguments.  Note that the order of the exceptions jest
            # important here.
            jeżeli newcontext.flags[Overflow]:
                context._raise_error(Overflow, 'above Emax', ans._sign)
            dla exception w Underflow, Subnormal, Inexact, Rounded, Clamped:
                jeżeli newcontext.flags[exception]:
                    context._raise_error(exception)

        inaczej:
            ans = ans._fix(context)

        zwróć ans

    def __rpow__(self, other, context=Nic):
        """Swaps self/other oraz returns __pow__."""
        other = _convert_other(other)
        jeżeli other jest NotImplemented:
            zwróć other
        zwróć other.__pow__(self, context=context)

    def normalize(self, context=Nic):
        """Normalize- strip trailing 0s, change anything equal to 0 to 0e0"""

        jeżeli context jest Nic:
            context = getcontext()

        jeżeli self._is_special:
            ans = self._check_nans(context=context)
            jeżeli ans:
                zwróć ans

        dup = self._fix(context)
        jeżeli dup._isinfinity():
            zwróć dup

        jeżeli nie dup:
            zwróć _dec_from_triple(dup._sign, '0', 0)
        exp_max = [context.Emax, context.Etop()][context.clamp]
        end = len(dup._int)
        exp = dup._exp
        dopóki dup._int[end-1] == '0' oraz exp < exp_max:
            exp += 1
            end -= 1
        zwróć _dec_from_triple(dup._sign, dup._int[:end], exp)

    def quantize(self, exp, rounding=Nic, context=Nic):
        """Quantize self so its exponent jest the same jako that of exp.

        Similar to self._rescale(exp._exp) but przy error checking.
        """
        exp = _convert_other(exp, podnieśit=Prawda)

        jeżeli context jest Nic:
            context = getcontext()
        jeżeli rounding jest Nic:
            rounding = context.rounding

        jeżeli self._is_special albo exp._is_special:
            ans = self._check_nans(exp, context)
            jeżeli ans:
                zwróć ans

            jeżeli exp._isinfinity() albo self._isinfinity():
                jeżeli exp._isinfinity() oraz self._isinfinity():
                    zwróć Decimal(self)  # jeżeli both are inf, it jest OK
                zwróć context._raise_error(InvalidOperation,
                                        'quantize przy one INF')

        # exp._exp should be between Etiny oraz Emax
        jeżeli nie (context.Etiny() <= exp._exp <= context.Emax):
            zwróć context._raise_error(InvalidOperation,
                   'target exponent out of bounds w quantize')

        jeżeli nie self:
            ans = _dec_from_triple(self._sign, '0', exp._exp)
            zwróć ans._fix(context)

        self_adjusted = self.adjusted()
        jeżeli self_adjusted > context.Emax:
            zwróć context._raise_error(InvalidOperation,
                                        'exponent of quantize result too large dla current context')
        jeżeli self_adjusted - exp._exp + 1 > context.prec:
            zwróć context._raise_error(InvalidOperation,
                                        'quantize result has too many digits dla current context')

        ans = self._rescale(exp._exp, rounding)
        jeżeli ans.adjusted() > context.Emax:
            zwróć context._raise_error(InvalidOperation,
                                        'exponent of quantize result too large dla current context')
        jeżeli len(ans._int) > context.prec:
            zwróć context._raise_error(InvalidOperation,
                                        'quantize result has too many digits dla current context')

        # podnieś appropriate flags
        jeżeli ans oraz ans.adjusted() < context.Emin:
            context._raise_error(Subnormal)
        jeżeli ans._exp > self._exp:
            jeżeli ans != self:
                context._raise_error(Inexact)
            context._raise_error(Rounded)

        # call to fix takes care of any necessary folddown, oraz
        # signals Clamped jeżeli necessary
        ans = ans._fix(context)
        zwróć ans

    def same_quantum(self, other, context=Nic):
        """Return Prawda jeżeli self oraz other have the same exponent; otherwise
        zwróć Nieprawda.

        If either operand jest a special value, the following rules are used:
           * zwróć Prawda jeżeli both operands are infinities
           * zwróć Prawda jeżeli both operands are NaNs
           * otherwise, zwróć Nieprawda.
        """
        other = _convert_other(other, podnieśit=Prawda)
        jeżeli self._is_special albo other._is_special:
            zwróć (self.is_nan() oraz other.is_nan() albo
                    self.is_infinite() oraz other.is_infinite())
        zwróć self._exp == other._exp

    def _rescale(self, exp, rounding):
        """Rescale self so that the exponent jest exp, either by padding przy zeros
        albo by truncating digits, using the given rounding mode.

        Specials are returned without change.  This operation jest
        quiet: it podnieśs no flags, oraz uses no information z the
        context.

        exp = exp to scale to (an integer)
        rounding = rounding mode
        """
        jeżeli self._is_special:
            zwróć Decimal(self)
        jeżeli nie self:
            zwróć _dec_from_triple(self._sign, '0', exp)

        jeżeli self._exp >= exp:
            # pad answer przy zeros jeżeli necessary
            zwróć _dec_from_triple(self._sign,
                                        self._int + '0'*(self._exp - exp), exp)

        # too many digits; round oraz lose data.  If self.adjusted() <
        # exp-1, replace self by 10**(exp-1) before rounding
        digits = len(self._int) + self._exp - exp
        jeżeli digits < 0:
            self = _dec_from_triple(self._sign, '1', exp-1)
            digits = 0
        this_function = self._pick_rounding_function[rounding]
        changed = this_function(self, digits)
        coeff = self._int[:digits] albo '0'
        jeżeli changed == 1:
            coeff = str(int(coeff)+1)
        zwróć _dec_from_triple(self._sign, coeff, exp)

    def _round(self, places, rounding):
        """Round a nonzero, nonspecial Decimal to a fixed number of
        significant figures, using the given rounding mode.

        Infinities, NaNs oraz zeros are returned unaltered.

        This operation jest quiet: it podnieśs no flags, oraz uses no
        information z the context.

        """
        jeżeli places <= 0:
            podnieś ValueError("argument should be at least 1 w _round")
        jeżeli self._is_special albo nie self:
            zwróć Decimal(self)
        ans = self._rescale(self.adjusted()+1-places, rounding)
        # it can happen that the rescale alters the adjusted exponent;
        # dla example when rounding 99.97 to 3 significant figures.
        # When this happens we end up przy an extra 0 at the end of
        # the number; a second rescale fixes this.
        jeżeli ans.adjusted() != self.adjusted():
            ans = ans._rescale(ans.adjusted()+1-places, rounding)
        zwróć ans

    def to_integral_exact(self, rounding=Nic, context=Nic):
        """Rounds to a nearby integer.

        If no rounding mode jest specified, take the rounding mode from
        the context.  This method podnieśs the Rounded oraz Inexact flags
        when appropriate.

        See also: to_integral_value, which does exactly the same as
        this method wyjąwszy that it doesn't podnieś Inexact albo Rounded.
        """
        jeżeli self._is_special:
            ans = self._check_nans(context=context)
            jeżeli ans:
                zwróć ans
            zwróć Decimal(self)
        jeżeli self._exp >= 0:
            zwróć Decimal(self)
        jeżeli nie self:
            zwróć _dec_from_triple(self._sign, '0', 0)
        jeżeli context jest Nic:
            context = getcontext()
        jeżeli rounding jest Nic:
            rounding = context.rounding
        ans = self._rescale(0, rounding)
        jeżeli ans != self:
            context._raise_error(Inexact)
        context._raise_error(Rounded)
        zwróć ans

    def to_integral_value(self, rounding=Nic, context=Nic):
        """Rounds to the nearest integer, without raising inexact, rounded."""
        jeżeli context jest Nic:
            context = getcontext()
        jeżeli rounding jest Nic:
            rounding = context.rounding
        jeżeli self._is_special:
            ans = self._check_nans(context=context)
            jeżeli ans:
                zwróć ans
            zwróć Decimal(self)
        jeżeli self._exp >= 0:
            zwróć Decimal(self)
        inaczej:
            zwróć self._rescale(0, rounding)

    # the method name changed, but we provide also the old one, dla compatibility
    to_integral = to_integral_value

    def sqrt(self, context=Nic):
        """Return the square root of self."""
        jeżeli context jest Nic:
            context = getcontext()

        jeżeli self._is_special:
            ans = self._check_nans(context=context)
            jeżeli ans:
                zwróć ans

            jeżeli self._isinfinity() oraz self._sign == 0:
                zwróć Decimal(self)

        jeżeli nie self:
            # exponent = self._exp // 2.  sqrt(-0) = -0
            ans = _dec_from_triple(self._sign, '0', self._exp // 2)
            zwróć ans._fix(context)

        jeżeli self._sign == 1:
            zwróć context._raise_error(InvalidOperation, 'sqrt(-x), x > 0')

        # At this point self represents a positive number.  Let p be
        # the desired precision oraz express self w the form c*100**e
        # przy c a positive real number oraz e an integer, c oraz e
        # being chosen so that 100**(p-1) <= c < 100**p.  Then the
        # (exact) square root of self jest sqrt(c)*10**e, oraz 10**(p-1)
        # <= sqrt(c) < 10**p, so the closest representable Decimal at
        # precision p jest n*10**e where n = round_half_even(sqrt(c)),
        # the closest integer to sqrt(c) przy the even integer chosen
        # w the case of a tie.
        #
        # To ensure correct rounding w all cases, we use the
        # following trick: we compute the square root to an extra
        # place (precision p+1 instead of precision p), rounding down.
        # Then, jeżeli the result jest inexact oraz its last digit jest 0 albo 5,
        # we increase the last digit to 1 albo 6 respectively; jeżeli it's
        # exact we leave the last digit alone.  Now the final round to
        # p places (or fewer w the case of underflow) will round
        # correctly oraz podnieś the appropriate flags.

        # use an extra digit of precision
        prec = context.prec+1

        # write argument w the form c*100**e where e = self._exp//2
        # jest the 'ideal' exponent, to be used jeżeli the square root jest
        # exactly representable.  l jest the number of 'digits' of c w
        # base 100, so that 100**(l-1) <= c < 100**l.
        op = _WorkRep(self)
        e = op.exp >> 1
        jeżeli op.exp & 1:
            c = op.int * 10
            l = (len(self._int) >> 1) + 1
        inaczej:
            c = op.int
            l = len(self._int)+1 >> 1

        # rescale so that c has exactly prec base 100 'digits'
        shift = prec-l
        jeżeli shift >= 0:
            c *= 100**shift
            exact = Prawda
        inaczej:
            c, remainder = divmod(c, 100**-shift)
            exact = nie remainder
        e -= shift

        # find n = floor(sqrt(c)) using Newton's method
        n = 10**prec
        dopóki Prawda:
            q = c//n
            jeżeli n <= q:
                przerwij
            inaczej:
                n = n + q >> 1
        exact = exact oraz n*n == c

        jeżeli exact:
            # result jest exact; rescale to use ideal exponent e
            jeżeli shift >= 0:
                # assert n % 10**shift == 0
                n //= 10**shift
            inaczej:
                n *= 10**-shift
            e += shift
        inaczej:
            # result jest nie exact; fix last digit jako described above
            jeżeli n % 5 == 0:
                n += 1

        ans = _dec_from_triple(0, str(n), e)

        # round, oraz fit to current context
        context = context._shallow_copy()
        rounding = context._set_rounding(ROUND_HALF_EVEN)
        ans = ans._fix(context)
        context.rounding = rounding

        zwróć ans

    def max(self, other, context=Nic):
        """Returns the larger value.

        Like max(self, other) wyjąwszy jeżeli one jest nie a number, returns
        NaN (and signals jeżeli one jest sNaN).  Also rounds.
        """
        other = _convert_other(other, podnieśit=Prawda)

        jeżeli context jest Nic:
            context = getcontext()

        jeżeli self._is_special albo other._is_special:
            # If one operand jest a quiet NaN oraz the other jest number, then the
            # number jest always returned
            sn = self._isnan()
            on = other._isnan()
            jeżeli sn albo on:
                jeżeli on == 1 oraz sn == 0:
                    zwróć self._fix(context)
                jeżeli sn == 1 oraz on == 0:
                    zwróć other._fix(context)
                zwróć self._check_nans(other, context)

        c = self._cmp(other)
        jeżeli c == 0:
            # If both operands are finite oraz equal w numerical value
            # then an ordering jest applied:
            #
            # If the signs differ then max returns the operand przy the
            # positive sign oraz min returns the operand przy the negative sign
            #
            # If the signs are the same then the exponent jest used to select
            # the result.  This jest exactly the ordering used w compare_total.
            c = self.compare_total(other)

        jeżeli c == -1:
            ans = other
        inaczej:
            ans = self

        zwróć ans._fix(context)

    def min(self, other, context=Nic):
        """Returns the smaller value.

        Like min(self, other) wyjąwszy jeżeli one jest nie a number, returns
        NaN (and signals jeżeli one jest sNaN).  Also rounds.
        """
        other = _convert_other(other, podnieśit=Prawda)

        jeżeli context jest Nic:
            context = getcontext()

        jeżeli self._is_special albo other._is_special:
            # If one operand jest a quiet NaN oraz the other jest number, then the
            # number jest always returned
            sn = self._isnan()
            on = other._isnan()
            jeżeli sn albo on:
                jeżeli on == 1 oraz sn == 0:
                    zwróć self._fix(context)
                jeżeli sn == 1 oraz on == 0:
                    zwróć other._fix(context)
                zwróć self._check_nans(other, context)

        c = self._cmp(other)
        jeżeli c == 0:
            c = self.compare_total(other)

        jeżeli c == -1:
            ans = self
        inaczej:
            ans = other

        zwróć ans._fix(context)

    def _isinteger(self):
        """Returns whether self jest an integer"""
        jeżeli self._is_special:
            zwróć Nieprawda
        jeżeli self._exp >= 0:
            zwróć Prawda
        rest = self._int[self._exp:]
        zwróć rest == '0'*len(rest)

    def _iseven(self):
        """Returns Prawda jeżeli self jest even.  Assumes self jest an integer."""
        jeżeli nie self albo self._exp > 0:
            zwróć Prawda
        zwróć self._int[-1+self._exp] w '02468'

    def adjusted(self):
        """Return the adjusted exponent of self"""
        spróbuj:
            zwróć self._exp + len(self._int) - 1
        # If NaN albo Infinity, self._exp jest string
        wyjąwszy TypeError:
            zwróć 0

    def canonical(self):
        """Returns the same Decimal object.

        As we do nie have different encodings dla the same number, the
        received object already jest w its canonical form.
        """
        zwróć self

    def compare_signal(self, other, context=Nic):
        """Compares self to the other operand numerically.

        It's pretty much like compare(), but all NaNs signal, przy signaling
        NaNs taking precedence over quiet NaNs.
        """
        other = _convert_other(other, podnieśit = Prawda)
        ans = self._compare_check_nans(other, context)
        jeżeli ans:
            zwróć ans
        zwróć self.compare(other, context=context)

    def compare_total(self, other, context=Nic):
        """Compares self to other using the abstract representations.

        This jest nie like the standard compare, which use their numerical
        value. Note that a total ordering jest defined dla all possible abstract
        representations.
        """
        other = _convert_other(other, podnieśit=Prawda)

        # jeżeli one jest negative oraz the other jest positive, it's easy
        jeżeli self._sign oraz nie other._sign:
            zwróć _NegativeOne
        jeżeli nie self._sign oraz other._sign:
            zwróć _One
        sign = self._sign

        # let's handle both NaN types
        self_nan = self._isnan()
        other_nan = other._isnan()
        jeżeli self_nan albo other_nan:
            jeżeli self_nan == other_nan:
                # compare payloads jako though they're integers
                self_key = len(self._int), self._int
                other_key = len(other._int), other._int
                jeżeli self_key < other_key:
                    jeżeli sign:
                        zwróć _One
                    inaczej:
                        zwróć _NegativeOne
                jeżeli self_key > other_key:
                    jeżeli sign:
                        zwróć _NegativeOne
                    inaczej:
                        zwróć _One
                zwróć _Zero

            jeżeli sign:
                jeżeli self_nan == 1:
                    zwróć _NegativeOne
                jeżeli other_nan == 1:
                    zwróć _One
                jeżeli self_nan == 2:
                    zwróć _NegativeOne
                jeżeli other_nan == 2:
                    zwróć _One
            inaczej:
                jeżeli self_nan == 1:
                    zwróć _One
                jeżeli other_nan == 1:
                    zwróć _NegativeOne
                jeżeli self_nan == 2:
                    zwróć _One
                jeżeli other_nan == 2:
                    zwróć _NegativeOne

        jeżeli self < other:
            zwróć _NegativeOne
        jeżeli self > other:
            zwróć _One

        jeżeli self._exp < other._exp:
            jeżeli sign:
                zwróć _One
            inaczej:
                zwróć _NegativeOne
        jeżeli self._exp > other._exp:
            jeżeli sign:
                zwróć _NegativeOne
            inaczej:
                zwróć _One
        zwróć _Zero


    def compare_total_mag(self, other, context=Nic):
        """Compares self to other using abstract repr., ignoring sign.

        Like compare_total, but przy operand's sign ignored oraz assumed to be 0.
        """
        other = _convert_other(other, podnieśit=Prawda)

        s = self.copy_abs()
        o = other.copy_abs()
        zwróć s.compare_total(o)

    def copy_abs(self):
        """Returns a copy przy the sign set to 0. """
        zwróć _dec_from_triple(0, self._int, self._exp, self._is_special)

    def copy_negate(self):
        """Returns a copy przy the sign inverted."""
        jeżeli self._sign:
            zwróć _dec_from_triple(0, self._int, self._exp, self._is_special)
        inaczej:
            zwróć _dec_from_triple(1, self._int, self._exp, self._is_special)

    def copy_sign(self, other, context=Nic):
        """Returns self przy the sign of other."""
        other = _convert_other(other, podnieśit=Prawda)
        zwróć _dec_from_triple(other._sign, self._int,
                                self._exp, self._is_special)

    def exp(self, context=Nic):
        """Returns e ** self."""

        jeżeli context jest Nic:
            context = getcontext()

        # exp(NaN) = NaN
        ans = self._check_nans(context=context)
        jeżeli ans:
            zwróć ans

        # exp(-Infinity) = 0
        jeżeli self._isinfinity() == -1:
            zwróć _Zero

        # exp(0) = 1
        jeżeli nie self:
            zwróć _One

        # exp(Infinity) = Infinity
        jeżeli self._isinfinity() == 1:
            zwróć Decimal(self)

        # the result jest now guaranteed to be inexact (the true
        # mathematical result jest transcendental). There's no need to
        # podnieś Rounded oraz Inexact here---they'll always be podnieśd as
        # a result of the call to _fix.
        p = context.prec
        adj = self.adjusted()

        # we only need to do any computation dla quite a small range
        # of adjusted exponents---dla example, -29 <= adj <= 10 for
        # the default context.  For smaller exponent the result jest
        # indistinguishable z 1 at the given precision, dopóki for
        # larger exponent the result either overflows albo underflows.
        jeżeli self._sign == 0 oraz adj > len(str((context.Emax+1)*3)):
            # overflow
            ans = _dec_from_triple(0, '1', context.Emax+1)
        albo_inaczej self._sign == 1 oraz adj > len(str((-context.Etiny()+1)*3)):
            # underflow to 0
            ans = _dec_from_triple(0, '1', context.Etiny()-1)
        albo_inaczej self._sign == 0 oraz adj < -p:
            # p+1 digits; final round will podnieś correct flags
            ans = _dec_from_triple(0, '1' + '0'*(p-1) + '1', -p)
        albo_inaczej self._sign == 1 oraz adj < -p-1:
            # p+1 digits; final round will podnieś correct flags
            ans = _dec_from_triple(0, '9'*(p+1), -p-1)
        # general case
        inaczej:
            op = _WorkRep(self)
            c, e = op.int, op.exp
            jeżeli op.sign == 1:
                c = -c

            # compute correctly rounded result: increase precision by
            # 3 digits at a time until we get an unambiguously
            # roundable result
            extra = 3
            dopóki Prawda:
                coeff, exp = _dexp(c, e, p+extra)
                jeżeli coeff % (5*10**(len(str(coeff))-p-1)):
                    przerwij
                extra += 3

            ans = _dec_from_triple(0, str(coeff), exp)

        # at this stage, ans should round correctly przy *any*
        # rounding mode, nie just przy ROUND_HALF_EVEN
        context = context._shallow_copy()
        rounding = context._set_rounding(ROUND_HALF_EVEN)
        ans = ans._fix(context)
        context.rounding = rounding

        zwróć ans

    def is_canonical(self):
        """Return Prawda jeżeli self jest canonical; otherwise zwróć Nieprawda.

        Currently, the encoding of a Decimal instance jest always
        canonical, so this method returns Prawda dla any Decimal.
        """
        zwróć Prawda

    def is_finite(self):
        """Return Prawda jeżeli self jest finite; otherwise zwróć Nieprawda.

        A Decimal instance jest considered finite jeżeli it jest neither
        infinite nor a NaN.
        """
        zwróć nie self._is_special

    def is_infinite(self):
        """Return Prawda jeżeli self jest infinite; otherwise zwróć Nieprawda."""
        zwróć self._exp == 'F'

    def is_nan(self):
        """Return Prawda jeżeli self jest a qNaN albo sNaN; otherwise zwróć Nieprawda."""
        zwróć self._exp w ('n', 'N')

    def is_normal(self, context=Nic):
        """Return Prawda jeżeli self jest a normal number; otherwise zwróć Nieprawda."""
        jeżeli self._is_special albo nie self:
            zwróć Nieprawda
        jeżeli context jest Nic:
            context = getcontext()
        zwróć context.Emin <= self.adjusted()

    def is_qnan(self):
        """Return Prawda jeżeli self jest a quiet NaN; otherwise zwróć Nieprawda."""
        zwróć self._exp == 'n'

    def is_signed(self):
        """Return Prawda jeżeli self jest negative; otherwise zwróć Nieprawda."""
        zwróć self._sign == 1

    def is_snan(self):
        """Return Prawda jeżeli self jest a signaling NaN; otherwise zwróć Nieprawda."""
        zwróć self._exp == 'N'

    def is_subnormal(self, context=Nic):
        """Return Prawda jeżeli self jest subnormal; otherwise zwróć Nieprawda."""
        jeżeli self._is_special albo nie self:
            zwróć Nieprawda
        jeżeli context jest Nic:
            context = getcontext()
        zwróć self.adjusted() < context.Emin

    def is_zero(self):
        """Return Prawda jeżeli self jest a zero; otherwise zwróć Nieprawda."""
        zwróć nie self._is_special oraz self._int == '0'

    def _ln_exp_bound(self):
        """Compute a lower bound dla the adjusted exponent of self.ln().
        In other words, compute r such that self.ln() >= 10**r.  Assumes
        that self jest finite oraz positive oraz that self != 1.
        """

        # dla 0.1 <= x <= 10 we use the inequalities 1-1/x <= ln(x) <= x-1
        adj = self._exp + len(self._int) - 1
        jeżeli adj >= 1:
            # argument >= 10; we use 23/10 = 2.3 jako a lower bound dla ln(10)
            zwróć len(str(adj*23//10)) - 1
        jeżeli adj <= -2:
            # argument <= 0.1
            zwróć len(str((-1-adj)*23//10)) - 1
        op = _WorkRep(self)
        c, e = op.int, op.exp
        jeżeli adj == 0:
            # 1 < self < 10
            num = str(c-10**-e)
            den = str(c)
            zwróć len(num) - len(den) - (num < den)
        # adj == -1, 0.1 <= self < 1
        zwróć e + len(str(10**-e - c)) - 1


    def ln(self, context=Nic):
        """Returns the natural (base e) logarithm of self."""

        jeżeli context jest Nic:
            context = getcontext()

        # ln(NaN) = NaN
        ans = self._check_nans(context=context)
        jeżeli ans:
            zwróć ans

        # ln(0.0) == -Infinity
        jeżeli nie self:
            zwróć _NegativeInfinity

        # ln(Infinity) = Infinity
        jeżeli self._isinfinity() == 1:
            zwróć _Infinity

        # ln(1.0) == 0.0
        jeżeli self == _One:
            zwróć _Zero

        # ln(negative) podnieśs InvalidOperation
        jeżeli self._sign == 1:
            zwróć context._raise_error(InvalidOperation,
                                        'ln of a negative value')

        # result jest irrational, so necessarily inexact
        op = _WorkRep(self)
        c, e = op.int, op.exp
        p = context.prec

        # correctly rounded result: repeatedly increase precision by 3
        # until we get an unambiguously roundable result
        places = p - self._ln_exp_bound() + 2 # at least p+3 places
        dopóki Prawda:
            coeff = _dlog(c, e, places)
            # assert len(str(abs(coeff)))-p >= 1
            jeżeli coeff % (5*10**(len(str(abs(coeff)))-p-1)):
                przerwij
            places += 3
        ans = _dec_from_triple(int(coeff<0), str(abs(coeff)), -places)

        context = context._shallow_copy()
        rounding = context._set_rounding(ROUND_HALF_EVEN)
        ans = ans._fix(context)
        context.rounding = rounding
        zwróć ans

    def _log10_exp_bound(self):
        """Compute a lower bound dla the adjusted exponent of self.log10().
        In other words, find r such that self.log10() >= 10**r.
        Assumes that self jest finite oraz positive oraz that self != 1.
        """

        # For x >= 10 albo x < 0.1 we only need a bound on the integer
        # part of log10(self), oraz this comes directly z the
        # exponent of x.  For 0.1 <= x <= 10 we use the inequalities
        # 1-1/x <= log(x) <= x-1. If x > 1 we have |log10(x)| >
        # (1-1/x)/2.31 > 0.  If x < 1 then |log10(x)| > (1-x)/2.31 > 0

        adj = self._exp + len(self._int) - 1
        jeżeli adj >= 1:
            # self >= 10
            zwróć len(str(adj))-1
        jeżeli adj <= -2:
            # self < 0.1
            zwróć len(str(-1-adj))-1
        op = _WorkRep(self)
        c, e = op.int, op.exp
        jeżeli adj == 0:
            # 1 < self < 10
            num = str(c-10**-e)
            den = str(231*c)
            zwróć len(num) - len(den) - (num < den) + 2
        # adj == -1, 0.1 <= self < 1
        num = str(10**-e-c)
        zwróć len(num) + e - (num < "231") - 1

    def log10(self, context=Nic):
        """Returns the base 10 logarithm of self."""

        jeżeli context jest Nic:
            context = getcontext()

        # log10(NaN) = NaN
        ans = self._check_nans(context=context)
        jeżeli ans:
            zwróć ans

        # log10(0.0) == -Infinity
        jeżeli nie self:
            zwróć _NegativeInfinity

        # log10(Infinity) = Infinity
        jeżeli self._isinfinity() == 1:
            zwróć _Infinity

        # log10(negative albo -Infinity) podnieśs InvalidOperation
        jeżeli self._sign == 1:
            zwróć context._raise_error(InvalidOperation,
                                        'log10 of a negative value')

        # log10(10**n) = n
        jeżeli self._int[0] == '1' oraz self._int[1:] == '0'*(len(self._int) - 1):
            # answer may need rounding
            ans = Decimal(self._exp + len(self._int) - 1)
        inaczej:
            # result jest irrational, so necessarily inexact
            op = _WorkRep(self)
            c, e = op.int, op.exp
            p = context.prec

            # correctly rounded result: repeatedly increase precision
            # until result jest unambiguously roundable
            places = p-self._log10_exp_bound()+2
            dopóki Prawda:
                coeff = _dlog10(c, e, places)
                # assert len(str(abs(coeff)))-p >= 1
                jeżeli coeff % (5*10**(len(str(abs(coeff)))-p-1)):
                    przerwij
                places += 3
            ans = _dec_from_triple(int(coeff<0), str(abs(coeff)), -places)

        context = context._shallow_copy()
        rounding = context._set_rounding(ROUND_HALF_EVEN)
        ans = ans._fix(context)
        context.rounding = rounding
        zwróć ans

    def logb(self, context=Nic):
        """ Returns the exponent of the magnitude of self's MSD.

        The result jest the integer which jest the exponent of the magnitude
        of the most significant digit of self (as though it were truncated
        to a single digit dopóki maintaining the value of that digit oraz
        without limiting the resulting exponent).
        """
        # logb(NaN) = NaN
        ans = self._check_nans(context=context)
        jeżeli ans:
            zwróć ans

        jeżeli context jest Nic:
            context = getcontext()

        # logb(+/-Inf) = +Inf
        jeżeli self._isinfinity():
            zwróć _Infinity

        # logb(0) = -Inf, DivisionByZero
        jeżeli nie self:
            zwróć context._raise_error(DivisionByZero, 'logb(0)', 1)

        # otherwise, simply zwróć the adjusted exponent of self, jako a
        # Decimal.  Note that no attempt jest made to fit the result
        # into the current context.
        ans = Decimal(self.adjusted())
        zwróć ans._fix(context)

    def _islogical(self):
        """Return Prawda jeżeli self jest a logical operand.

        For being logical, it must be a finite number przy a sign of 0,
        an exponent of 0, oraz a coefficient whose digits must all be
        either 0 albo 1.
        """
        jeżeli self._sign != 0 albo self._exp != 0:
            zwróć Nieprawda
        dla dig w self._int:
            jeżeli dig nie w '01':
                zwróć Nieprawda
        zwróć Prawda

    def _fill_logical(self, context, opa, opb):
        djeżeli = context.prec - len(opa)
        jeżeli djeżeli > 0:
            opa = '0'*djeżeli + opa
        albo_inaczej djeżeli < 0:
            opa = opa[-context.prec:]
        djeżeli = context.prec - len(opb)
        jeżeli djeżeli > 0:
            opb = '0'*djeżeli + opb
        albo_inaczej djeżeli < 0:
            opb = opb[-context.prec:]
        zwróć opa, opb

    def logical_and(self, other, context=Nic):
        """Applies an 'and' operation between self oraz other's digits."""
        jeżeli context jest Nic:
            context = getcontext()

        other = _convert_other(other, podnieśit=Prawda)

        jeżeli nie self._islogical() albo nie other._islogical():
            zwróć context._raise_error(InvalidOperation)

        # fill to context.prec
        (opa, opb) = self._fill_logical(context, self._int, other._int)

        # make the operation, oraz clean starting zeroes
        result = "".join([str(int(a)&int(b)) dla a,b w zip(opa,opb)])
        zwróć _dec_from_triple(0, result.lstrip('0') albo '0', 0)

    def logical_invert(self, context=Nic):
        """Invert all its digits."""
        jeżeli context jest Nic:
            context = getcontext()
        zwróć self.logical_xor(_dec_from_triple(0,'1'*context.prec,0),
                                context)

    def logical_or(self, other, context=Nic):
        """Applies an 'or' operation between self oraz other's digits."""
        jeżeli context jest Nic:
            context = getcontext()

        other = _convert_other(other, podnieśit=Prawda)

        jeżeli nie self._islogical() albo nie other._islogical():
            zwróć context._raise_error(InvalidOperation)

        # fill to context.prec
        (opa, opb) = self._fill_logical(context, self._int, other._int)

        # make the operation, oraz clean starting zeroes
        result = "".join([str(int(a)|int(b)) dla a,b w zip(opa,opb)])
        zwróć _dec_from_triple(0, result.lstrip('0') albo '0', 0)

    def logical_xor(self, other, context=Nic):
        """Applies an 'xor' operation between self oraz other's digits."""
        jeżeli context jest Nic:
            context = getcontext()

        other = _convert_other(other, podnieśit=Prawda)

        jeżeli nie self._islogical() albo nie other._islogical():
            zwróć context._raise_error(InvalidOperation)

        # fill to context.prec
        (opa, opb) = self._fill_logical(context, self._int, other._int)

        # make the operation, oraz clean starting zeroes
        result = "".join([str(int(a)^int(b)) dla a,b w zip(opa,opb)])
        zwróć _dec_from_triple(0, result.lstrip('0') albo '0', 0)

    def max_mag(self, other, context=Nic):
        """Compares the values numerically przy their sign ignored."""
        other = _convert_other(other, podnieśit=Prawda)

        jeżeli context jest Nic:
            context = getcontext()

        jeżeli self._is_special albo other._is_special:
            # If one operand jest a quiet NaN oraz the other jest number, then the
            # number jest always returned
            sn = self._isnan()
            on = other._isnan()
            jeżeli sn albo on:
                jeżeli on == 1 oraz sn == 0:
                    zwróć self._fix(context)
                jeżeli sn == 1 oraz on == 0:
                    zwróć other._fix(context)
                zwróć self._check_nans(other, context)

        c = self.copy_abs()._cmp(other.copy_abs())
        jeżeli c == 0:
            c = self.compare_total(other)

        jeżeli c == -1:
            ans = other
        inaczej:
            ans = self

        zwróć ans._fix(context)

    def min_mag(self, other, context=Nic):
        """Compares the values numerically przy their sign ignored."""
        other = _convert_other(other, podnieśit=Prawda)

        jeżeli context jest Nic:
            context = getcontext()

        jeżeli self._is_special albo other._is_special:
            # If one operand jest a quiet NaN oraz the other jest number, then the
            # number jest always returned
            sn = self._isnan()
            on = other._isnan()
            jeżeli sn albo on:
                jeżeli on == 1 oraz sn == 0:
                    zwróć self._fix(context)
                jeżeli sn == 1 oraz on == 0:
                    zwróć other._fix(context)
                zwróć self._check_nans(other, context)

        c = self.copy_abs()._cmp(other.copy_abs())
        jeżeli c == 0:
            c = self.compare_total(other)

        jeżeli c == -1:
            ans = self
        inaczej:
            ans = other

        zwróć ans._fix(context)

    def next_minus(self, context=Nic):
        """Returns the largest representable number smaller than itself."""
        jeżeli context jest Nic:
            context = getcontext()

        ans = self._check_nans(context=context)
        jeżeli ans:
            zwróć ans

        jeżeli self._isinfinity() == -1:
            zwróć _NegativeInfinity
        jeżeli self._isinfinity() == 1:
            zwróć _dec_from_triple(0, '9'*context.prec, context.Etop())

        context = context.copy()
        context._set_rounding(ROUND_FLOOR)
        context._ignore_all_flags()
        new_self = self._fix(context)
        jeżeli new_self != self:
            zwróć new_self
        zwróć self.__sub__(_dec_from_triple(0, '1', context.Etiny()-1),
                            context)

    def next_plus(self, context=Nic):
        """Returns the smallest representable number larger than itself."""
        jeżeli context jest Nic:
            context = getcontext()

        ans = self._check_nans(context=context)
        jeżeli ans:
            zwróć ans

        jeżeli self._isinfinity() == 1:
            zwróć _Infinity
        jeżeli self._isinfinity() == -1:
            zwróć _dec_from_triple(1, '9'*context.prec, context.Etop())

        context = context.copy()
        context._set_rounding(ROUND_CEILING)
        context._ignore_all_flags()
        new_self = self._fix(context)
        jeżeli new_self != self:
            zwróć new_self
        zwróć self.__add__(_dec_from_triple(0, '1', context.Etiny()-1),
                            context)

    def next_toward(self, other, context=Nic):
        """Returns the number closest to self, w the direction towards other.

        The result jest the closest representable number to self
        (excluding self) that jest w the direction towards other,
        unless both have the same value.  If the two operands are
        numerically equal, then the result jest a copy of self przy the
        sign set to be the same jako the sign of other.
        """
        other = _convert_other(other, podnieśit=Prawda)

        jeżeli context jest Nic:
            context = getcontext()

        ans = self._check_nans(other, context)
        jeżeli ans:
            zwróć ans

        comparison = self._cmp(other)
        jeżeli comparison == 0:
            zwróć self.copy_sign(other)

        jeżeli comparison == -1:
            ans = self.next_plus(context)
        inaczej: # comparison == 1
            ans = self.next_minus(context)

        # decide which flags to podnieś using value of ans
        jeżeli ans._isinfinity():
            context._raise_error(Overflow,
                                 'Infinite result z next_toward',
                                 ans._sign)
            context._raise_error(Inexact)
            context._raise_error(Rounded)
        albo_inaczej ans.adjusted() < context.Emin:
            context._raise_error(Underflow)
            context._raise_error(Subnormal)
            context._raise_error(Inexact)
            context._raise_error(Rounded)
            # jeżeli precision == 1 then we don't podnieś Clamped dla a
            # result 0E-Etiny.
            jeżeli nie ans:
                context._raise_error(Clamped)

        zwróć ans

    def number_class(self, context=Nic):
        """Returns an indication of the klasa of self.

        The klasa jest one of the following strings:
          sNaN
          NaN
          -Infinity
          -Normal
          -Subnormal
          -Zero
          +Zero
          +Subnormal
          +Normal
          +Infinity
        """
        jeżeli self.is_snan():
            zwróć "sNaN"
        jeżeli self.is_qnan():
            zwróć "NaN"
        inf = self._isinfinity()
        jeżeli inf == 1:
            zwróć "+Infinity"
        jeżeli inf == -1:
            zwróć "-Infinity"
        jeżeli self.is_zero():
            jeżeli self._sign:
                zwróć "-Zero"
            inaczej:
                zwróć "+Zero"
        jeżeli context jest Nic:
            context = getcontext()
        jeżeli self.is_subnormal(context=context):
            jeżeli self._sign:
                zwróć "-Subnormal"
            inaczej:
                zwróć "+Subnormal"
        # just a normal, regular, boring number, :)
        jeżeli self._sign:
            zwróć "-Normal"
        inaczej:
            zwróć "+Normal"

    def radix(self):
        """Just returns 10, jako this jest Decimal, :)"""
        zwróć Decimal(10)

    def rotate(self, other, context=Nic):
        """Returns a rotated copy of self, value-of-other times."""
        jeżeli context jest Nic:
            context = getcontext()

        other = _convert_other(other, podnieśit=Prawda)

        ans = self._check_nans(other, context)
        jeżeli ans:
            zwróć ans

        jeżeli other._exp != 0:
            zwróć context._raise_error(InvalidOperation)
        jeżeli nie (-context.prec <= int(other) <= context.prec):
            zwróć context._raise_error(InvalidOperation)

        jeżeli self._isinfinity():
            zwróć Decimal(self)

        # get values, pad jeżeli necessary
        torot = int(other)
        rotdig = self._int
        topad = context.prec - len(rotdig)
        jeżeli topad > 0:
            rotdig = '0'*topad + rotdig
        albo_inaczej topad < 0:
            rotdig = rotdig[-topad:]

        # let's rotate!
        rotated = rotdig[torot:] + rotdig[:torot]
        zwróć _dec_from_triple(self._sign,
                                rotated.lstrip('0') albo '0', self._exp)

    def scaleb(self, other, context=Nic):
        """Returns self operand after adding the second value to its exp."""
        jeżeli context jest Nic:
            context = getcontext()

        other = _convert_other(other, podnieśit=Prawda)

        ans = self._check_nans(other, context)
        jeżeli ans:
            zwróć ans

        jeżeli other._exp != 0:
            zwróć context._raise_error(InvalidOperation)
        liminf = -2 * (context.Emax + context.prec)
        limsup =  2 * (context.Emax + context.prec)
        jeżeli nie (liminf <= int(other) <= limsup):
            zwróć context._raise_error(InvalidOperation)

        jeżeli self._isinfinity():
            zwróć Decimal(self)

        d = _dec_from_triple(self._sign, self._int, self._exp + int(other))
        d = d._fix(context)
        zwróć d

    def shift(self, other, context=Nic):
        """Returns a shifted copy of self, value-of-other times."""
        jeżeli context jest Nic:
            context = getcontext()

        other = _convert_other(other, podnieśit=Prawda)

        ans = self._check_nans(other, context)
        jeżeli ans:
            zwróć ans

        jeżeli other._exp != 0:
            zwróć context._raise_error(InvalidOperation)
        jeżeli nie (-context.prec <= int(other) <= context.prec):
            zwróć context._raise_error(InvalidOperation)

        jeżeli self._isinfinity():
            zwróć Decimal(self)

        # get values, pad jeżeli necessary
        torot = int(other)
        rotdig = self._int
        topad = context.prec - len(rotdig)
        jeżeli topad > 0:
            rotdig = '0'*topad + rotdig
        albo_inaczej topad < 0:
            rotdig = rotdig[-topad:]

        # let's shift!
        jeżeli torot < 0:
            shifted = rotdig[:torot]
        inaczej:
            shifted = rotdig + '0'*torot
            shifted = shifted[-context.prec:]

        zwróć _dec_from_triple(self._sign,
                                    shifted.lstrip('0') albo '0', self._exp)

    # Support dla pickling, copy, oraz deepcopy
    def __reduce__(self):
        zwróć (self.__class__, (str(self),))

    def __copy__(self):
        jeżeli type(self) jest Decimal:
            zwróć self     # I'm immutable; therefore I am my own clone
        zwróć self.__class__(str(self))

    def __deepcopy__(self, memo):
        jeżeli type(self) jest Decimal:
            zwróć self     # My components are also immutable
        zwróć self.__class__(str(self))

    # PEP 3101 support.  the _localeconv keyword argument should be
    # considered private: it's provided dla ease of testing only.
    def __format__(self, specifier, context=Nic, _localeconv=Nic):
        """Format a Decimal instance according to the given specifier.

        The specifier should be a standard format specifier, przy the
        form described w PEP 3101.  Formatting types 'e', 'E', 'f',
        'F', 'g', 'G', 'n' oraz '%' are supported.  If the formatting
        type jest omitted it defaults to 'g' albo 'G', depending on the
        value of context.capitals.
        """

        # Note: PEP 3101 says that jeżeli the type jest nie present then
        # there should be at least one digit after the decimal point.
        # We take the liberty of ignoring this requirement for
        # Decimal---it's presumably there to make sure that
        # format(float, '') behaves similarly to str(float).
        jeżeli context jest Nic:
            context = getcontext()

        spec = _parse_format_specifier(specifier, _localeconv=_localeconv)

        # special values don't care about the type albo precision
        jeżeli self._is_special:
            sign = _format_sign(self._sign, spec)
            body = str(self.copy_abs())
            jeżeli spec['type'] == '%':
                body += '%'
            zwróć _format_align(sign, body, spec)

        # a type of Nic defaults to 'g' albo 'G', depending on context
        jeżeli spec['type'] jest Nic:
            spec['type'] = ['g', 'G'][context.capitals]

        # jeżeli type jest '%', adjust exponent of self accordingly
        jeżeli spec['type'] == '%':
            self = _dec_from_triple(self._sign, self._int, self._exp+2)

        # round jeżeli necessary, taking rounding mode z the context
        rounding = context.rounding
        precision = spec['precision']
        jeżeli precision jest nie Nic:
            jeżeli spec['type'] w 'eE':
                self = self._round(precision+1, rounding)
            albo_inaczej spec['type'] w 'fF%':
                self = self._rescale(-precision, rounding)
            albo_inaczej spec['type'] w 'gG' oraz len(self._int) > precision:
                self = self._round(precision, rounding)
        # special case: zeros przy a positive exponent can't be
        # represented w fixed point; rescale them to 0e0.
        jeżeli nie self oraz self._exp > 0 oraz spec['type'] w 'fF%':
            self = self._rescale(0, rounding)

        # figure out placement of the decimal point
        leftdigits = self._exp + len(self._int)
        jeżeli spec['type'] w 'eE':
            jeżeli nie self oraz precision jest nie Nic:
                dotplace = 1 - precision
            inaczej:
                dotplace = 1
        albo_inaczej spec['type'] w 'fF%':
            dotplace = leftdigits
        albo_inaczej spec['type'] w 'gG':
            jeżeli self._exp <= 0 oraz leftdigits > -6:
                dotplace = leftdigits
            inaczej:
                dotplace = 1

        # find digits before oraz after decimal point, oraz get exponent
        jeżeli dotplace < 0:
            intpart = '0'
            fracpart = '0'*(-dotplace) + self._int
        albo_inaczej dotplace > len(self._int):
            intpart = self._int + '0'*(dotplace-len(self._int))
            fracpart = ''
        inaczej:
            intpart = self._int[:dotplace] albo '0'
            fracpart = self._int[dotplace:]
        exp = leftdigits-dotplace

        # done przy the decimal-specific stuff;  hand over the rest
        # of the formatting to the _format_number function
        zwróć _format_number(self._sign, intpart, fracpart, exp, spec)

def _dec_from_triple(sign, coefficient, exponent, special=Nieprawda):
    """Create a decimal instance directly, without any validation,
    normalization (e.g. removal of leading zeros) albo argument
    conversion.

    This function jest dla *internal use only*.
    """

    self = object.__new__(Decimal)
    self._sign = sign
    self._int = coefficient
    self._exp = exponent
    self._is_special = special

    zwróć self

# Register Decimal jako a kind of Number (an abstract base class).
# However, do nie register it jako Real (because Decimals are nie
# interoperable przy floats).
_numbers.Number.register(Decimal)


##### Context klasa #######################################################

klasa _ContextManager(object):
    """Context manager klasa to support localcontext().

      Sets a copy of the supplied context w __enter__() oraz restores
      the previous decimal context w __exit__()
    """
    def __init__(self, new_context):
        self.new_context = new_context.copy()
    def __enter__(self):
        self.saved_context = getcontext()
        setcontext(self.new_context)
        zwróć self.new_context
    def __exit__(self, t, v, tb):
        setcontext(self.saved_context)

klasa Context(object):
    """Contains the context dla a Decimal instance.

    Contains:
    prec - precision (dla use w rounding, division, square roots..)
    rounding - rounding type (how you round)
    traps - If traps[exception] = 1, then the exception jest
                    podnieśd when it jest caused.  Otherwise, a value jest
                    substituted in.
    flags  - When an exception jest caused, flags[exception] jest set.
             (Whether albo nie the trap_enabler jest set)
             Should be reset by user of Decimal instance.
    Emin -   Minimum exponent
    Emax -   Maximum exponent
    capitals -      If 1, 1*10^1 jest printed jako 1E+1.
                    If 0, printed jako 1e1
    clamp -  If 1, change exponents jeżeli too high (Default 0)
    """

    def __init__(self, prec=Nic, rounding=Nic, Emin=Nic, Emax=Nic,
                       capitals=Nic, clamp=Nic, flags=Nic, traps=Nic,
                       _ignored_flags=Nic):
        # Set defaults; dla everything wyjąwszy flags oraz _ignored_flags,
        # inherit z DefaultContext.
        spróbuj:
            dc = DefaultContext
        wyjąwszy NameError:
            dalej

        self.prec = prec jeżeli prec jest nie Nic inaczej dc.prec
        self.rounding = rounding jeżeli rounding jest nie Nic inaczej dc.rounding
        self.Emin = Emin jeżeli Emin jest nie Nic inaczej dc.Emin
        self.Emax = Emax jeżeli Emax jest nie Nic inaczej dc.Emax
        self.capitals = capitals jeżeli capitals jest nie Nic inaczej dc.capitals
        self.clamp = clamp jeżeli clamp jest nie Nic inaczej dc.clamp

        jeżeli _ignored_flags jest Nic:
            self._ignored_flags = []
        inaczej:
            self._ignored_flags = _ignored_flags

        jeżeli traps jest Nic:
            self.traps = dc.traps.copy()
        albo_inaczej nie isinstance(traps, dict):
            self.traps = dict((s, int(s w traps)) dla s w _signals + traps)
        inaczej:
            self.traps = traps

        jeżeli flags jest Nic:
            self.flags = dict.fromkeys(_signals, 0)
        albo_inaczej nie isinstance(flags, dict):
            self.flags = dict((s, int(s w flags)) dla s w _signals + flags)
        inaczej:
            self.flags = flags

    def _set_integer_check(self, name, value, vmin, vmax):
        jeżeli nie isinstance(value, int):
            podnieś TypeError("%s must be an integer" % name)
        jeżeli vmin == '-inf':
            jeżeli value > vmax:
                podnieś ValueError("%s must be w [%s, %d]. got: %s" % (name, vmin, vmax, value))
        albo_inaczej vmax == 'inf':
            jeżeli value < vmin:
                podnieś ValueError("%s must be w [%d, %s]. got: %s" % (name, vmin, vmax, value))
        inaczej:
            jeżeli value < vmin albo value > vmax:
                podnieś ValueError("%s must be w [%d, %d]. got %s" % (name, vmin, vmax, value))
        zwróć object.__setattr__(self, name, value)

    def _set_signal_dict(self, name, d):
        jeżeli nie isinstance(d, dict):
            podnieś TypeError("%s must be a signal dict" % d)
        dla key w d:
            jeżeli nie key w _signals:
                podnieś KeyError("%s jest nie a valid signal dict" % d)
        dla key w _signals:
            jeżeli nie key w d:
                podnieś KeyError("%s jest nie a valid signal dict" % d)
        zwróć object.__setattr__(self, name, d)

    def __setattr__(self, name, value):
        jeżeli name == 'prec':
            zwróć self._set_integer_check(name, value, 1, 'inf')
        albo_inaczej name == 'Emin':
            zwróć self._set_integer_check(name, value, '-inf', 0)
        albo_inaczej name == 'Emax':
            zwróć self._set_integer_check(name, value, 0, 'inf')
        albo_inaczej name == 'capitals':
            zwróć self._set_integer_check(name, value, 0, 1)
        albo_inaczej name == 'clamp':
            zwróć self._set_integer_check(name, value, 0, 1)
        albo_inaczej name == 'rounding':
            jeżeli nie value w _rounding_modes:
                # podnieś TypeError even dla strings to have consistency
                # among various implementations.
                podnieś TypeError("%s: invalid rounding mode" % value)
            zwróć object.__setattr__(self, name, value)
        albo_inaczej name == 'flags' albo name == 'traps':
            zwróć self._set_signal_dict(name, value)
        albo_inaczej name == '_ignored_flags':
            zwróć object.__setattr__(self, name, value)
        inaczej:
            podnieś AttributeError(
                "'decimal.Context' object has no attribute '%s'" % name)

    def __delattr__(self, name):
        podnieś AttributeError("%s cannot be deleted" % name)

    # Support dla pickling, copy, oraz deepcopy
    def __reduce__(self):
        flags = [sig dla sig, v w self.flags.items() jeżeli v]
        traps = [sig dla sig, v w self.traps.items() jeżeli v]
        zwróć (self.__class__,
                (self.prec, self.rounding, self.Emin, self.Emax,
                 self.capitals, self.clamp, flags, traps))

    def __repr__(self):
        """Show the current context."""
        s = []
        s.append('Context(prec=%(prec)d, rounding=%(rounding)s, '
                 'Emin=%(Emin)d, Emax=%(Emax)d, capitals=%(capitals)d, '
                 'clamp=%(clamp)d'
                 % vars(self))
        names = [f.__name__ dla f, v w self.flags.items() jeżeli v]
        s.append('flags=[' + ', '.join(names) + ']')
        names = [t.__name__ dla t, v w self.traps.items() jeżeli v]
        s.append('traps=[' + ', '.join(names) + ']')
        zwróć ', '.join(s) + ')'

    def clear_flags(self):
        """Reset all flags to zero"""
        dla flag w self.flags:
            self.flags[flag] = 0

    def clear_traps(self):
        """Reset all traps to zero"""
        dla flag w self.traps:
            self.traps[flag] = 0

    def _shallow_copy(self):
        """Returns a shallow copy z self."""
        nc = Context(self.prec, self.rounding, self.Emin, self.Emax,
                     self.capitals, self.clamp, self.flags, self.traps,
                     self._ignored_flags)
        zwróć nc

    def copy(self):
        """Returns a deep copy z self."""
        nc = Context(self.prec, self.rounding, self.Emin, self.Emax,
                     self.capitals, self.clamp,
                     self.flags.copy(), self.traps.copy(),
                     self._ignored_flags)
        zwróć nc
    __copy__ = copy

    def _raise_error(self, condition, explanation = Nic, *args):
        """Handles an error

        If the flag jest w _ignored_flags, returns the default response.
        Otherwise, it sets the flag, then, jeżeli the corresponding
        trap_enabler jest set, it reraises the exception.  Otherwise, it returns
        the default value after setting the flag.
        """
        error = _condition_map.get(condition, condition)
        jeżeli error w self._ignored_flags:
            # Don't touch the flag
            zwróć error().handle(self, *args)

        self.flags[error] = 1
        jeżeli nie self.traps[error]:
            # The errors define how to handle themselves.
            zwróć condition().handle(self, *args)

        # Errors should only be risked on copies of the context
        # self._ignored_flags = []
        podnieś error(explanation)

    def _ignore_all_flags(self):
        """Ignore all flags, jeżeli they are podnieśd"""
        zwróć self._ignore_flags(*_signals)

    def _ignore_flags(self, *flags):
        """Ignore the flags, jeżeli they are podnieśd"""
        # Do nie mutate-- This way, copies of a context leave the original
        # alone.
        self._ignored_flags = (self._ignored_flags + list(flags))
        zwróć list(flags)

    def _regard_flags(self, *flags):
        """Stop ignoring the flags, jeżeli they are podnieśd"""
        jeżeli flags oraz isinstance(flags[0], (tuple,list)):
            flags = flags[0]
        dla flag w flags:
            self._ignored_flags.remove(flag)

    # We inherit object.__hash__, so we must deny this explicitly
    __hash__ = Nic

    def Etiny(self):
        """Returns Etiny (= Emin - prec + 1)"""
        zwróć int(self.Emin - self.prec + 1)

    def Etop(self):
        """Returns maximum exponent (= Emax - prec + 1)"""
        zwróć int(self.Emax - self.prec + 1)

    def _set_rounding(self, type):
        """Sets the rounding type.

        Sets the rounding type, oraz returns the current (previous)
        rounding type.  Often used like:

        context = context.copy()
        # so you don't change the calling context
        # jeżeli an error occurs w the middle.
        rounding = context._set_rounding(ROUND_UP)
        val = self.__sub__(other, context=context)
        context._set_rounding(rounding)

        This will make it round up dla that operation.
        """
        rounding = self.rounding
        self.rounding= type
        zwróć rounding

    def create_decimal(self, num='0'):
        """Creates a new Decimal instance but using self jako context.

        This method implements the to-number operation of the
        IBM Decimal specification."""

        jeżeli isinstance(num, str) oraz num != num.strip():
            zwróć self._raise_error(ConversionSyntax,
                                     "no trailing albo leading whitespace jest "
                                     "permitted.")

        d = Decimal(num, context=self)
        jeżeli d._isnan() oraz len(d._int) > self.prec - self.clamp:
            zwróć self._raise_error(ConversionSyntax,
                                     "diagnostic info too long w NaN")
        zwróć d._fix(self)

    def create_decimal_from_float(self, f):
        """Creates a new Decimal instance z a float but rounding using self
        jako the context.

        >>> context = Context(prec=5, rounding=ROUND_DOWN)
        >>> context.create_decimal_from_float(3.1415926535897932)
        Decimal('3.1415')
        >>> context = Context(prec=5, traps=[Inexact])
        >>> context.create_decimal_from_float(3.1415926535897932)
        Traceback (most recent call last):
            ...
        decimal.Inexact

        """
        d = Decimal.from_float(f)       # An exact conversion
        zwróć d._fix(self)             # Apply the context rounding

    # Methods
    def abs(self, a):
        """Returns the absolute value of the operand.

        If the operand jest negative, the result jest the same jako using the minus
        operation on the operand.  Otherwise, the result jest the same jako using
        the plus operation on the operand.

        >>> ExtendedContext.abs(Decimal('2.1'))
        Decimal('2.1')
        >>> ExtendedContext.abs(Decimal('-100'))
        Decimal('100')
        >>> ExtendedContext.abs(Decimal('101.5'))
        Decimal('101.5')
        >>> ExtendedContext.abs(Decimal('-101.5'))
        Decimal('101.5')
        >>> ExtendedContext.abs(-1)
        Decimal('1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.__abs__(context=self)

    def add(self, a, b):
        """Return the sum of the two operands.

        >>> ExtendedContext.add(Decimal('12'), Decimal('7.00'))
        Decimal('19.00')
        >>> ExtendedContext.add(Decimal('1E+2'), Decimal('1.01E+4'))
        Decimal('1.02E+4')
        >>> ExtendedContext.add(1, Decimal(2))
        Decimal('3')
        >>> ExtendedContext.add(Decimal(8), 5)
        Decimal('13')
        >>> ExtendedContext.add(5, 5)
        Decimal('10')
        """
        a = _convert_other(a, podnieśit=Prawda)
        r = a.__add__(b, context=self)
        jeżeli r jest NotImplemented:
            podnieś TypeError("Unable to convert %s to Decimal" % b)
        inaczej:
            zwróć r

    def _apply(self, a):
        zwróć str(a._fix(self))

    def canonical(self, a):
        """Returns the same Decimal object.

        As we do nie have different encodings dla the same number, the
        received object already jest w its canonical form.

        >>> ExtendedContext.canonical(Decimal('2.50'))
        Decimal('2.50')
        """
        jeżeli nie isinstance(a, Decimal):
            podnieś TypeError("canonical requires a Decimal jako an argument.")
        zwróć a.canonical()

    def compare(self, a, b):
        """Compares values numerically.

        If the signs of the operands differ, a value representing each operand
        ('-1' jeżeli the operand jest less than zero, '0' jeżeli the operand jest zero albo
        negative zero, albo '1' jeżeli the operand jest greater than zero) jest used w
        place of that operand dla the comparison instead of the actual
        operand.

        The comparison jest then effected by subtracting the second operand from
        the first oraz then returning a value according to the result of the
        subtraction: '-1' jeżeli the result jest less than zero, '0' jeżeli the result jest
        zero albo negative zero, albo '1' jeżeli the result jest greater than zero.

        >>> ExtendedContext.compare(Decimal('2.1'), Decimal('3'))
        Decimal('-1')
        >>> ExtendedContext.compare(Decimal('2.1'), Decimal('2.1'))
        Decimal('0')
        >>> ExtendedContext.compare(Decimal('2.1'), Decimal('2.10'))
        Decimal('0')
        >>> ExtendedContext.compare(Decimal('3'), Decimal('2.1'))
        Decimal('1')
        >>> ExtendedContext.compare(Decimal('2.1'), Decimal('-3'))
        Decimal('1')
        >>> ExtendedContext.compare(Decimal('-3'), Decimal('2.1'))
        Decimal('-1')
        >>> ExtendedContext.compare(1, 2)
        Decimal('-1')
        >>> ExtendedContext.compare(Decimal(1), 2)
        Decimal('-1')
        >>> ExtendedContext.compare(1, Decimal(2))
        Decimal('-1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.compare(b, context=self)

    def compare_signal(self, a, b):
        """Compares the values of the two operands numerically.

        It's pretty much like compare(), but all NaNs signal, przy signaling
        NaNs taking precedence over quiet NaNs.

        >>> c = ExtendedContext
        >>> c.compare_signal(Decimal('2.1'), Decimal('3'))
        Decimal('-1')
        >>> c.compare_signal(Decimal('2.1'), Decimal('2.1'))
        Decimal('0')
        >>> c.flags[InvalidOperation] = 0
        >>> print(c.flags[InvalidOperation])
        0
        >>> c.compare_signal(Decimal('NaN'), Decimal('2.1'))
        Decimal('NaN')
        >>> print(c.flags[InvalidOperation])
        1
        >>> c.flags[InvalidOperation] = 0
        >>> print(c.flags[InvalidOperation])
        0
        >>> c.compare_signal(Decimal('sNaN'), Decimal('2.1'))
        Decimal('NaN')
        >>> print(c.flags[InvalidOperation])
        1
        >>> c.compare_signal(-1, 2)
        Decimal('-1')
        >>> c.compare_signal(Decimal(-1), 2)
        Decimal('-1')
        >>> c.compare_signal(-1, Decimal(2))
        Decimal('-1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.compare_signal(b, context=self)

    def compare_total(self, a, b):
        """Compares two operands using their abstract representation.

        This jest nie like the standard compare, which use their numerical
        value. Note that a total ordering jest defined dla all possible abstract
        representations.

        >>> ExtendedContext.compare_total(Decimal('12.73'), Decimal('127.9'))
        Decimal('-1')
        >>> ExtendedContext.compare_total(Decimal('-127'),  Decimal('12'))
        Decimal('-1')
        >>> ExtendedContext.compare_total(Decimal('12.30'), Decimal('12.3'))
        Decimal('-1')
        >>> ExtendedContext.compare_total(Decimal('12.30'), Decimal('12.30'))
        Decimal('0')
        >>> ExtendedContext.compare_total(Decimal('12.3'),  Decimal('12.300'))
        Decimal('1')
        >>> ExtendedContext.compare_total(Decimal('12.3'),  Decimal('NaN'))
        Decimal('-1')
        >>> ExtendedContext.compare_total(1, 2)
        Decimal('-1')
        >>> ExtendedContext.compare_total(Decimal(1), 2)
        Decimal('-1')
        >>> ExtendedContext.compare_total(1, Decimal(2))
        Decimal('-1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.compare_total(b)

    def compare_total_mag(self, a, b):
        """Compares two operands using their abstract representation ignoring sign.

        Like compare_total, but przy operand's sign ignored oraz assumed to be 0.
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.compare_total_mag(b)

    def copy_abs(self, a):
        """Returns a copy of the operand przy the sign set to 0.

        >>> ExtendedContext.copy_abs(Decimal('2.1'))
        Decimal('2.1')
        >>> ExtendedContext.copy_abs(Decimal('-100'))
        Decimal('100')
        >>> ExtendedContext.copy_abs(-1)
        Decimal('1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.copy_abs()

    def copy_decimal(self, a):
        """Returns a copy of the decimal object.

        >>> ExtendedContext.copy_decimal(Decimal('2.1'))
        Decimal('2.1')
        >>> ExtendedContext.copy_decimal(Decimal('-1.00'))
        Decimal('-1.00')
        >>> ExtendedContext.copy_decimal(1)
        Decimal('1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć Decimal(a)

    def copy_negate(self, a):
        """Returns a copy of the operand przy the sign inverted.

        >>> ExtendedContext.copy_negate(Decimal('101.5'))
        Decimal('-101.5')
        >>> ExtendedContext.copy_negate(Decimal('-101.5'))
        Decimal('101.5')
        >>> ExtendedContext.copy_negate(1)
        Decimal('-1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.copy_negate()

    def copy_sign(self, a, b):
        """Copies the second operand's sign to the first one.

        In detail, it returns a copy of the first operand przy the sign
        equal to the sign of the second operand.

        >>> ExtendedContext.copy_sign(Decimal( '1.50'), Decimal('7.33'))
        Decimal('1.50')
        >>> ExtendedContext.copy_sign(Decimal('-1.50'), Decimal('7.33'))
        Decimal('1.50')
        >>> ExtendedContext.copy_sign(Decimal( '1.50'), Decimal('-7.33'))
        Decimal('-1.50')
        >>> ExtendedContext.copy_sign(Decimal('-1.50'), Decimal('-7.33'))
        Decimal('-1.50')
        >>> ExtendedContext.copy_sign(1, -2)
        Decimal('-1')
        >>> ExtendedContext.copy_sign(Decimal(1), -2)
        Decimal('-1')
        >>> ExtendedContext.copy_sign(1, Decimal(-2))
        Decimal('-1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.copy_sign(b)

    def divide(self, a, b):
        """Decimal division w a specified context.

        >>> ExtendedContext.divide(Decimal('1'), Decimal('3'))
        Decimal('0.333333333')
        >>> ExtendedContext.divide(Decimal('2'), Decimal('3'))
        Decimal('0.666666667')
        >>> ExtendedContext.divide(Decimal('5'), Decimal('2'))
        Decimal('2.5')
        >>> ExtendedContext.divide(Decimal('1'), Decimal('10'))
        Decimal('0.1')
        >>> ExtendedContext.divide(Decimal('12'), Decimal('12'))
        Decimal('1')
        >>> ExtendedContext.divide(Decimal('8.00'), Decimal('2'))
        Decimal('4.00')
        >>> ExtendedContext.divide(Decimal('2.400'), Decimal('2.0'))
        Decimal('1.20')
        >>> ExtendedContext.divide(Decimal('1000'), Decimal('100'))
        Decimal('10')
        >>> ExtendedContext.divide(Decimal('1000'), Decimal('1'))
        Decimal('1000')
        >>> ExtendedContext.divide(Decimal('2.40E+6'), Decimal('2'))
        Decimal('1.20E+6')
        >>> ExtendedContext.divide(5, 5)
        Decimal('1')
        >>> ExtendedContext.divide(Decimal(5), 5)
        Decimal('1')
        >>> ExtendedContext.divide(5, Decimal(5))
        Decimal('1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        r = a.__truediv__(b, context=self)
        jeżeli r jest NotImplemented:
            podnieś TypeError("Unable to convert %s to Decimal" % b)
        inaczej:
            zwróć r

    def divide_int(self, a, b):
        """Divides two numbers oraz returns the integer part of the result.

        >>> ExtendedContext.divide_int(Decimal('2'), Decimal('3'))
        Decimal('0')
        >>> ExtendedContext.divide_int(Decimal('10'), Decimal('3'))
        Decimal('3')
        >>> ExtendedContext.divide_int(Decimal('1'), Decimal('0.3'))
        Decimal('3')
        >>> ExtendedContext.divide_int(10, 3)
        Decimal('3')
        >>> ExtendedContext.divide_int(Decimal(10), 3)
        Decimal('3')
        >>> ExtendedContext.divide_int(10, Decimal(3))
        Decimal('3')
        """
        a = _convert_other(a, podnieśit=Prawda)
        r = a.__floordiv__(b, context=self)
        jeżeli r jest NotImplemented:
            podnieś TypeError("Unable to convert %s to Decimal" % b)
        inaczej:
            zwróć r

    def divmod(self, a, b):
        """Return (a // b, a % b).

        >>> ExtendedContext.divmod(Decimal(8), Decimal(3))
        (Decimal('2'), Decimal('2'))
        >>> ExtendedContext.divmod(Decimal(8), Decimal(4))
        (Decimal('2'), Decimal('0'))
        >>> ExtendedContext.divmod(8, 4)
        (Decimal('2'), Decimal('0'))
        >>> ExtendedContext.divmod(Decimal(8), 4)
        (Decimal('2'), Decimal('0'))
        >>> ExtendedContext.divmod(8, Decimal(4))
        (Decimal('2'), Decimal('0'))
        """
        a = _convert_other(a, podnieśit=Prawda)
        r = a.__divmod__(b, context=self)
        jeżeli r jest NotImplemented:
            podnieś TypeError("Unable to convert %s to Decimal" % b)
        inaczej:
            zwróć r

    def exp(self, a):
        """Returns e ** a.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.exp(Decimal('-Infinity'))
        Decimal('0')
        >>> c.exp(Decimal('-1'))
        Decimal('0.367879441')
        >>> c.exp(Decimal('0'))
        Decimal('1')
        >>> c.exp(Decimal('1'))
        Decimal('2.71828183')
        >>> c.exp(Decimal('0.693147181'))
        Decimal('2.00000000')
        >>> c.exp(Decimal('+Infinity'))
        Decimal('Infinity')
        >>> c.exp(10)
        Decimal('22026.4658')
        """
        a =_convert_other(a, podnieśit=Prawda)
        zwróć a.exp(context=self)

    def fma(self, a, b, c):
        """Returns a multiplied by b, plus c.

        The first two operands are multiplied together, using multiply,
        the third operand jest then added to the result of that
        multiplication, using add, all przy only one final rounding.

        >>> ExtendedContext.fma(Decimal('3'), Decimal('5'), Decimal('7'))
        Decimal('22')
        >>> ExtendedContext.fma(Decimal('3'), Decimal('-5'), Decimal('7'))
        Decimal('-8')
        >>> ExtendedContext.fma(Decimal('888565290'), Decimal('1557.96930'), Decimal('-86087.7578'))
        Decimal('1.38435736E+12')
        >>> ExtendedContext.fma(1, 3, 4)
        Decimal('7')
        >>> ExtendedContext.fma(1, Decimal(3), 4)
        Decimal('7')
        >>> ExtendedContext.fma(1, 3, Decimal(4))
        Decimal('7')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.fma(b, c, context=self)

    def is_canonical(self, a):
        """Return Prawda jeżeli the operand jest canonical; otherwise zwróć Nieprawda.

        Currently, the encoding of a Decimal instance jest always
        canonical, so this method returns Prawda dla any Decimal.

        >>> ExtendedContext.is_canonical(Decimal('2.50'))
        Prawda
        """
        jeżeli nie isinstance(a, Decimal):
            podnieś TypeError("is_canonical requires a Decimal jako an argument.")
        zwróć a.is_canonical()

    def is_finite(self, a):
        """Return Prawda jeżeli the operand jest finite; otherwise zwróć Nieprawda.

        A Decimal instance jest considered finite jeżeli it jest neither
        infinite nor a NaN.

        >>> ExtendedContext.is_finite(Decimal('2.50'))
        Prawda
        >>> ExtendedContext.is_finite(Decimal('-0.3'))
        Prawda
        >>> ExtendedContext.is_finite(Decimal('0'))
        Prawda
        >>> ExtendedContext.is_finite(Decimal('Inf'))
        Nieprawda
        >>> ExtendedContext.is_finite(Decimal('NaN'))
        Nieprawda
        >>> ExtendedContext.is_finite(1)
        Prawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.is_finite()

    def is_infinite(self, a):
        """Return Prawda jeżeli the operand jest infinite; otherwise zwróć Nieprawda.

        >>> ExtendedContext.is_infinite(Decimal('2.50'))
        Nieprawda
        >>> ExtendedContext.is_infinite(Decimal('-Inf'))
        Prawda
        >>> ExtendedContext.is_infinite(Decimal('NaN'))
        Nieprawda
        >>> ExtendedContext.is_infinite(1)
        Nieprawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.is_infinite()

    def is_nan(self, a):
        """Return Prawda jeżeli the operand jest a qNaN albo sNaN;
        otherwise zwróć Nieprawda.

        >>> ExtendedContext.is_nan(Decimal('2.50'))
        Nieprawda
        >>> ExtendedContext.is_nan(Decimal('NaN'))
        Prawda
        >>> ExtendedContext.is_nan(Decimal('-sNaN'))
        Prawda
        >>> ExtendedContext.is_nan(1)
        Nieprawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.is_nan()

    def is_normal(self, a):
        """Return Prawda jeżeli the operand jest a normal number;
        otherwise zwróć Nieprawda.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.is_normal(Decimal('2.50'))
        Prawda
        >>> c.is_normal(Decimal('0.1E-999'))
        Nieprawda
        >>> c.is_normal(Decimal('0.00'))
        Nieprawda
        >>> c.is_normal(Decimal('-Inf'))
        Nieprawda
        >>> c.is_normal(Decimal('NaN'))
        Nieprawda
        >>> c.is_normal(1)
        Prawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.is_normal(context=self)

    def is_qnan(self, a):
        """Return Prawda jeżeli the operand jest a quiet NaN; otherwise zwróć Nieprawda.

        >>> ExtendedContext.is_qnan(Decimal('2.50'))
        Nieprawda
        >>> ExtendedContext.is_qnan(Decimal('NaN'))
        Prawda
        >>> ExtendedContext.is_qnan(Decimal('sNaN'))
        Nieprawda
        >>> ExtendedContext.is_qnan(1)
        Nieprawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.is_qnan()

    def is_signed(self, a):
        """Return Prawda jeżeli the operand jest negative; otherwise zwróć Nieprawda.

        >>> ExtendedContext.is_signed(Decimal('2.50'))
        Nieprawda
        >>> ExtendedContext.is_signed(Decimal('-12'))
        Prawda
        >>> ExtendedContext.is_signed(Decimal('-0'))
        Prawda
        >>> ExtendedContext.is_signed(8)
        Nieprawda
        >>> ExtendedContext.is_signed(-8)
        Prawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.is_signed()

    def is_snan(self, a):
        """Return Prawda jeżeli the operand jest a signaling NaN;
        otherwise zwróć Nieprawda.

        >>> ExtendedContext.is_snan(Decimal('2.50'))
        Nieprawda
        >>> ExtendedContext.is_snan(Decimal('NaN'))
        Nieprawda
        >>> ExtendedContext.is_snan(Decimal('sNaN'))
        Prawda
        >>> ExtendedContext.is_snan(1)
        Nieprawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.is_snan()

    def is_subnormal(self, a):
        """Return Prawda jeżeli the operand jest subnormal; otherwise zwróć Nieprawda.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.is_subnormal(Decimal('2.50'))
        Nieprawda
        >>> c.is_subnormal(Decimal('0.1E-999'))
        Prawda
        >>> c.is_subnormal(Decimal('0.00'))
        Nieprawda
        >>> c.is_subnormal(Decimal('-Inf'))
        Nieprawda
        >>> c.is_subnormal(Decimal('NaN'))
        Nieprawda
        >>> c.is_subnormal(1)
        Nieprawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.is_subnormal(context=self)

    def is_zero(self, a):
        """Return Prawda jeżeli the operand jest a zero; otherwise zwróć Nieprawda.

        >>> ExtendedContext.is_zero(Decimal('0'))
        Prawda
        >>> ExtendedContext.is_zero(Decimal('2.50'))
        Nieprawda
        >>> ExtendedContext.is_zero(Decimal('-0E+2'))
        Prawda
        >>> ExtendedContext.is_zero(1)
        Nieprawda
        >>> ExtendedContext.is_zero(0)
        Prawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.is_zero()

    def ln(self, a):
        """Returns the natural (base e) logarithm of the operand.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.ln(Decimal('0'))
        Decimal('-Infinity')
        >>> c.ln(Decimal('1.000'))
        Decimal('0')
        >>> c.ln(Decimal('2.71828183'))
        Decimal('1.00000000')
        >>> c.ln(Decimal('10'))
        Decimal('2.30258509')
        >>> c.ln(Decimal('+Infinity'))
        Decimal('Infinity')
        >>> c.ln(1)
        Decimal('0')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.ln(context=self)

    def log10(self, a):
        """Returns the base 10 logarithm of the operand.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.log10(Decimal('0'))
        Decimal('-Infinity')
        >>> c.log10(Decimal('0.001'))
        Decimal('-3')
        >>> c.log10(Decimal('1.000'))
        Decimal('0')
        >>> c.log10(Decimal('2'))
        Decimal('0.301029996')
        >>> c.log10(Decimal('10'))
        Decimal('1')
        >>> c.log10(Decimal('70'))
        Decimal('1.84509804')
        >>> c.log10(Decimal('+Infinity'))
        Decimal('Infinity')
        >>> c.log10(0)
        Decimal('-Infinity')
        >>> c.log10(1)
        Decimal('0')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.log10(context=self)

    def logb(self, a):
        """ Returns the exponent of the magnitude of the operand's MSD.

        The result jest the integer which jest the exponent of the magnitude
        of the most significant digit of the operand (as though the
        operand were truncated to a single digit dopóki maintaining the
        value of that digit oraz without limiting the resulting exponent).

        >>> ExtendedContext.logb(Decimal('250'))
        Decimal('2')
        >>> ExtendedContext.logb(Decimal('2.50'))
        Decimal('0')
        >>> ExtendedContext.logb(Decimal('0.03'))
        Decimal('-2')
        >>> ExtendedContext.logb(Decimal('0'))
        Decimal('-Infinity')
        >>> ExtendedContext.logb(1)
        Decimal('0')
        >>> ExtendedContext.logb(10)
        Decimal('1')
        >>> ExtendedContext.logb(100)
        Decimal('2')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.logb(context=self)

    def logical_and(self, a, b):
        """Applies the logical operation 'and' between each operand's digits.

        The operands must be both logical numbers.

        >>> ExtendedContext.logical_and(Decimal('0'), Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.logical_and(Decimal('0'), Decimal('1'))
        Decimal('0')
        >>> ExtendedContext.logical_and(Decimal('1'), Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.logical_and(Decimal('1'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.logical_and(Decimal('1100'), Decimal('1010'))
        Decimal('1000')
        >>> ExtendedContext.logical_and(Decimal('1111'), Decimal('10'))
        Decimal('10')
        >>> ExtendedContext.logical_and(110, 1101)
        Decimal('100')
        >>> ExtendedContext.logical_and(Decimal(110), 1101)
        Decimal('100')
        >>> ExtendedContext.logical_and(110, Decimal(1101))
        Decimal('100')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.logical_and(b, context=self)

    def logical_invert(self, a):
        """Invert all the digits w the operand.

        The operand must be a logical number.

        >>> ExtendedContext.logical_invert(Decimal('0'))
        Decimal('111111111')
        >>> ExtendedContext.logical_invert(Decimal('1'))
        Decimal('111111110')
        >>> ExtendedContext.logical_invert(Decimal('111111111'))
        Decimal('0')
        >>> ExtendedContext.logical_invert(Decimal('101010101'))
        Decimal('10101010')
        >>> ExtendedContext.logical_invert(1101)
        Decimal('111110010')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.logical_invert(context=self)

    def logical_or(self, a, b):
        """Applies the logical operation 'or' between each operand's digits.

        The operands must be both logical numbers.

        >>> ExtendedContext.logical_or(Decimal('0'), Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.logical_or(Decimal('0'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.logical_or(Decimal('1'), Decimal('0'))
        Decimal('1')
        >>> ExtendedContext.logical_or(Decimal('1'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.logical_or(Decimal('1100'), Decimal('1010'))
        Decimal('1110')
        >>> ExtendedContext.logical_or(Decimal('1110'), Decimal('10'))
        Decimal('1110')
        >>> ExtendedContext.logical_or(110, 1101)
        Decimal('1111')
        >>> ExtendedContext.logical_or(Decimal(110), 1101)
        Decimal('1111')
        >>> ExtendedContext.logical_or(110, Decimal(1101))
        Decimal('1111')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.logical_or(b, context=self)

    def logical_xor(self, a, b):
        """Applies the logical operation 'xor' between each operand's digits.

        The operands must be both logical numbers.

        >>> ExtendedContext.logical_xor(Decimal('0'), Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.logical_xor(Decimal('0'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.logical_xor(Decimal('1'), Decimal('0'))
        Decimal('1')
        >>> ExtendedContext.logical_xor(Decimal('1'), Decimal('1'))
        Decimal('0')
        >>> ExtendedContext.logical_xor(Decimal('1100'), Decimal('1010'))
        Decimal('110')
        >>> ExtendedContext.logical_xor(Decimal('1111'), Decimal('10'))
        Decimal('1101')
        >>> ExtendedContext.logical_xor(110, 1101)
        Decimal('1011')
        >>> ExtendedContext.logical_xor(Decimal(110), 1101)
        Decimal('1011')
        >>> ExtendedContext.logical_xor(110, Decimal(1101))
        Decimal('1011')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.logical_xor(b, context=self)

    def max(self, a, b):
        """max compares two values numerically oraz returns the maximum.

        If either operand jest a NaN then the general rules apply.
        Otherwise, the operands are compared jako though by the compare
        operation.  If they are numerically equal then the left-hand operand
        jest chosen jako the result.  Otherwise the maximum (closer to positive
        infinity) of the two operands jest chosen jako the result.

        >>> ExtendedContext.max(Decimal('3'), Decimal('2'))
        Decimal('3')
        >>> ExtendedContext.max(Decimal('-10'), Decimal('3'))
        Decimal('3')
        >>> ExtendedContext.max(Decimal('1.0'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.max(Decimal('7'), Decimal('NaN'))
        Decimal('7')
        >>> ExtendedContext.max(1, 2)
        Decimal('2')
        >>> ExtendedContext.max(Decimal(1), 2)
        Decimal('2')
        >>> ExtendedContext.max(1, Decimal(2))
        Decimal('2')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.max(b, context=self)

    def max_mag(self, a, b):
        """Compares the values numerically przy their sign ignored.

        >>> ExtendedContext.max_mag(Decimal('7'), Decimal('NaN'))
        Decimal('7')
        >>> ExtendedContext.max_mag(Decimal('7'), Decimal('-10'))
        Decimal('-10')
        >>> ExtendedContext.max_mag(1, -2)
        Decimal('-2')
        >>> ExtendedContext.max_mag(Decimal(1), -2)
        Decimal('-2')
        >>> ExtendedContext.max_mag(1, Decimal(-2))
        Decimal('-2')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.max_mag(b, context=self)

    def min(self, a, b):
        """min compares two values numerically oraz returns the minimum.

        If either operand jest a NaN then the general rules apply.
        Otherwise, the operands are compared jako though by the compare
        operation.  If they are numerically equal then the left-hand operand
        jest chosen jako the result.  Otherwise the minimum (closer to negative
        infinity) of the two operands jest chosen jako the result.

        >>> ExtendedContext.min(Decimal('3'), Decimal('2'))
        Decimal('2')
        >>> ExtendedContext.min(Decimal('-10'), Decimal('3'))
        Decimal('-10')
        >>> ExtendedContext.min(Decimal('1.0'), Decimal('1'))
        Decimal('1.0')
        >>> ExtendedContext.min(Decimal('7'), Decimal('NaN'))
        Decimal('7')
        >>> ExtendedContext.min(1, 2)
        Decimal('1')
        >>> ExtendedContext.min(Decimal(1), 2)
        Decimal('1')
        >>> ExtendedContext.min(1, Decimal(29))
        Decimal('1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.min(b, context=self)

    def min_mag(self, a, b):
        """Compares the values numerically przy their sign ignored.

        >>> ExtendedContext.min_mag(Decimal('3'), Decimal('-2'))
        Decimal('-2')
        >>> ExtendedContext.min_mag(Decimal('-3'), Decimal('NaN'))
        Decimal('-3')
        >>> ExtendedContext.min_mag(1, -2)
        Decimal('1')
        >>> ExtendedContext.min_mag(Decimal(1), -2)
        Decimal('1')
        >>> ExtendedContext.min_mag(1, Decimal(-2))
        Decimal('1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.min_mag(b, context=self)

    def minus(self, a):
        """Minus corresponds to unary prefix minus w Python.

        The operation jest evaluated using the same rules jako subtract; the
        operation minus(a) jest calculated jako subtract('0', a) where the '0'
        has the same exponent jako the operand.

        >>> ExtendedContext.minus(Decimal('1.3'))
        Decimal('-1.3')
        >>> ExtendedContext.minus(Decimal('-1.3'))
        Decimal('1.3')
        >>> ExtendedContext.minus(1)
        Decimal('-1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.__neg__(context=self)

    def multiply(self, a, b):
        """multiply multiplies two operands.

        If either operand jest a special value then the general rules apply.
        Otherwise, the operands are multiplied together
        ('long multiplication'), resulting w a number which may be jako long as
        the sum of the lengths of the two operands.

        >>> ExtendedContext.multiply(Decimal('1.20'), Decimal('3'))
        Decimal('3.60')
        >>> ExtendedContext.multiply(Decimal('7'), Decimal('3'))
        Decimal('21')
        >>> ExtendedContext.multiply(Decimal('0.9'), Decimal('0.8'))
        Decimal('0.72')
        >>> ExtendedContext.multiply(Decimal('0.9'), Decimal('-0'))
        Decimal('-0.0')
        >>> ExtendedContext.multiply(Decimal('654321'), Decimal('654321'))
        Decimal('4.28135971E+11')
        >>> ExtendedContext.multiply(7, 7)
        Decimal('49')
        >>> ExtendedContext.multiply(Decimal(7), 7)
        Decimal('49')
        >>> ExtendedContext.multiply(7, Decimal(7))
        Decimal('49')
        """
        a = _convert_other(a, podnieśit=Prawda)
        r = a.__mul__(b, context=self)
        jeżeli r jest NotImplemented:
            podnieś TypeError("Unable to convert %s to Decimal" % b)
        inaczej:
            zwróć r

    def next_minus(self, a):
        """Returns the largest representable number smaller than a.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> ExtendedContext.next_minus(Decimal('1'))
        Decimal('0.999999999')
        >>> c.next_minus(Decimal('1E-1007'))
        Decimal('0E-1007')
        >>> ExtendedContext.next_minus(Decimal('-1.00000003'))
        Decimal('-1.00000004')
        >>> c.next_minus(Decimal('Infinity'))
        Decimal('9.99999999E+999')
        >>> c.next_minus(1)
        Decimal('0.999999999')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.next_minus(context=self)

    def next_plus(self, a):
        """Returns the smallest representable number larger than a.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> ExtendedContext.next_plus(Decimal('1'))
        Decimal('1.00000001')
        >>> c.next_plus(Decimal('-1E-1007'))
        Decimal('-0E-1007')
        >>> ExtendedContext.next_plus(Decimal('-1.00000003'))
        Decimal('-1.00000002')
        >>> c.next_plus(Decimal('-Infinity'))
        Decimal('-9.99999999E+999')
        >>> c.next_plus(1)
        Decimal('1.00000001')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.next_plus(context=self)

    def next_toward(self, a, b):
        """Returns the number closest to a, w direction towards b.

        The result jest the closest representable number z the first
        operand (but nie the first operand) that jest w the direction
        towards the second operand, unless the operands have the same
        value.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.next_toward(Decimal('1'), Decimal('2'))
        Decimal('1.00000001')
        >>> c.next_toward(Decimal('-1E-1007'), Decimal('1'))
        Decimal('-0E-1007')
        >>> c.next_toward(Decimal('-1.00000003'), Decimal('0'))
        Decimal('-1.00000002')
        >>> c.next_toward(Decimal('1'), Decimal('0'))
        Decimal('0.999999999')
        >>> c.next_toward(Decimal('1E-1007'), Decimal('-100'))
        Decimal('0E-1007')
        >>> c.next_toward(Decimal('-1.00000003'), Decimal('-10'))
        Decimal('-1.00000004')
        >>> c.next_toward(Decimal('0.00'), Decimal('-0.0000'))
        Decimal('-0.00')
        >>> c.next_toward(0, 1)
        Decimal('1E-1007')
        >>> c.next_toward(Decimal(0), 1)
        Decimal('1E-1007')
        >>> c.next_toward(0, Decimal(1))
        Decimal('1E-1007')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.next_toward(b, context=self)

    def normalize(self, a):
        """normalize reduces an operand to its simplest form.

        Essentially a plus operation przy all trailing zeros removed z the
        result.

        >>> ExtendedContext.normalize(Decimal('2.1'))
        Decimal('2.1')
        >>> ExtendedContext.normalize(Decimal('-2.0'))
        Decimal('-2')
        >>> ExtendedContext.normalize(Decimal('1.200'))
        Decimal('1.2')
        >>> ExtendedContext.normalize(Decimal('-120'))
        Decimal('-1.2E+2')
        >>> ExtendedContext.normalize(Decimal('120.00'))
        Decimal('1.2E+2')
        >>> ExtendedContext.normalize(Decimal('0.00'))
        Decimal('0')
        >>> ExtendedContext.normalize(6)
        Decimal('6')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.normalize(context=self)

    def number_class(self, a):
        """Returns an indication of the klasa of the operand.

        The klasa jest one of the following strings:
          -sNaN
          -NaN
          -Infinity
          -Normal
          -Subnormal
          -Zero
          +Zero
          +Subnormal
          +Normal
          +Infinity

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.number_class(Decimal('Infinity'))
        '+Infinity'
        >>> c.number_class(Decimal('1E-10'))
        '+Normal'
        >>> c.number_class(Decimal('2.50'))
        '+Normal'
        >>> c.number_class(Decimal('0.1E-999'))
        '+Subnormal'
        >>> c.number_class(Decimal('0'))
        '+Zero'
        >>> c.number_class(Decimal('-0'))
        '-Zero'
        >>> c.number_class(Decimal('-0.1E-999'))
        '-Subnormal'
        >>> c.number_class(Decimal('-1E-10'))
        '-Normal'
        >>> c.number_class(Decimal('-2.50'))
        '-Normal'
        >>> c.number_class(Decimal('-Infinity'))
        '-Infinity'
        >>> c.number_class(Decimal('NaN'))
        'NaN'
        >>> c.number_class(Decimal('-NaN'))
        'NaN'
        >>> c.number_class(Decimal('sNaN'))
        'sNaN'
        >>> c.number_class(123)
        '+Normal'
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.number_class(context=self)

    def plus(self, a):
        """Plus corresponds to unary prefix plus w Python.

        The operation jest evaluated using the same rules jako add; the
        operation plus(a) jest calculated jako add('0', a) where the '0'
        has the same exponent jako the operand.

        >>> ExtendedContext.plus(Decimal('1.3'))
        Decimal('1.3')
        >>> ExtendedContext.plus(Decimal('-1.3'))
        Decimal('-1.3')
        >>> ExtendedContext.plus(-1)
        Decimal('-1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.__pos__(context=self)

    def power(self, a, b, modulo=Nic):
        """Raises a to the power of b, to modulo jeżeli given.

        With two arguments, compute a**b.  If a jest negative then b
        must be integral.  The result will be inexact unless b jest
        integral oraz the result jest finite oraz can be expressed exactly
        w 'precision' digits.

        With three arguments, compute (a**b) % modulo.  For the
        three argument form, the following restrictions on the
        arguments hold:

         - all three arguments must be integral
         - b must be nonnegative
         - at least one of a albo b must be nonzero
         - modulo must be nonzero oraz have at most 'precision' digits

        The result of pow(a, b, modulo) jest identical to the result
        that would be obtained by computing (a**b) % modulo with
        unbounded precision, but jest computed more efficiently.  It jest
        always exact.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.power(Decimal('2'), Decimal('3'))
        Decimal('8')
        >>> c.power(Decimal('-2'), Decimal('3'))
        Decimal('-8')
        >>> c.power(Decimal('2'), Decimal('-3'))
        Decimal('0.125')
        >>> c.power(Decimal('1.7'), Decimal('8'))
        Decimal('69.7575744')
        >>> c.power(Decimal('10'), Decimal('0.301029996'))
        Decimal('2.00000000')
        >>> c.power(Decimal('Infinity'), Decimal('-1'))
        Decimal('0')
        >>> c.power(Decimal('Infinity'), Decimal('0'))
        Decimal('1')
        >>> c.power(Decimal('Infinity'), Decimal('1'))
        Decimal('Infinity')
        >>> c.power(Decimal('-Infinity'), Decimal('-1'))
        Decimal('-0')
        >>> c.power(Decimal('-Infinity'), Decimal('0'))
        Decimal('1')
        >>> c.power(Decimal('-Infinity'), Decimal('1'))
        Decimal('-Infinity')
        >>> c.power(Decimal('-Infinity'), Decimal('2'))
        Decimal('Infinity')
        >>> c.power(Decimal('0'), Decimal('0'))
        Decimal('NaN')

        >>> c.power(Decimal('3'), Decimal('7'), Decimal('16'))
        Decimal('11')
        >>> c.power(Decimal('-3'), Decimal('7'), Decimal('16'))
        Decimal('-11')
        >>> c.power(Decimal('-3'), Decimal('8'), Decimal('16'))
        Decimal('1')
        >>> c.power(Decimal('3'), Decimal('7'), Decimal('-16'))
        Decimal('11')
        >>> c.power(Decimal('23E12345'), Decimal('67E189'), Decimal('123456789'))
        Decimal('11729830')
        >>> c.power(Decimal('-0'), Decimal('17'), Decimal('1729'))
        Decimal('-0')
        >>> c.power(Decimal('-23'), Decimal('0'), Decimal('65537'))
        Decimal('1')
        >>> ExtendedContext.power(7, 7)
        Decimal('823543')
        >>> ExtendedContext.power(Decimal(7), 7)
        Decimal('823543')
        >>> ExtendedContext.power(7, Decimal(7), 2)
        Decimal('1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        r = a.__pow__(b, modulo, context=self)
        jeżeli r jest NotImplemented:
            podnieś TypeError("Unable to convert %s to Decimal" % b)
        inaczej:
            zwróć r

    def quantize(self, a, b):
        """Returns a value equal to 'a' (rounded), having the exponent of 'b'.

        The coefficient of the result jest derived z that of the left-hand
        operand.  It may be rounded using the current rounding setting (jeżeli the
        exponent jest being increased), multiplied by a positive power of ten (if
        the exponent jest being decreased), albo jest unchanged (jeżeli the exponent jest
        already equal to that of the right-hand operand).

        Unlike other operations, jeżeli the length of the coefficient after the
        quantize operation would be greater than precision then an Invalid
        operation condition jest podnieśd.  This guarantees that, unless there jest
        an error condition, the exponent of the result of a quantize jest always
        equal to that of the right-hand operand.

        Also unlike other operations, quantize will never podnieś Underflow, even
        jeżeli the result jest subnormal oraz inexact.

        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('0.001'))
        Decimal('2.170')
        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('0.01'))
        Decimal('2.17')
        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('0.1'))
        Decimal('2.2')
        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('1e+0'))
        Decimal('2')
        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('1e+1'))
        Decimal('0E+1')
        >>> ExtendedContext.quantize(Decimal('-Inf'), Decimal('Infinity'))
        Decimal('-Infinity')
        >>> ExtendedContext.quantize(Decimal('2'), Decimal('Infinity'))
        Decimal('NaN')
        >>> ExtendedContext.quantize(Decimal('-0.1'), Decimal('1'))
        Decimal('-0')
        >>> ExtendedContext.quantize(Decimal('-0'), Decimal('1e+5'))
        Decimal('-0E+5')
        >>> ExtendedContext.quantize(Decimal('+35236450.6'), Decimal('1e-2'))
        Decimal('NaN')
        >>> ExtendedContext.quantize(Decimal('-35236450.6'), Decimal('1e-2'))
        Decimal('NaN')
        >>> ExtendedContext.quantize(Decimal('217'), Decimal('1e-1'))
        Decimal('217.0')
        >>> ExtendedContext.quantize(Decimal('217'), Decimal('1e-0'))
        Decimal('217')
        >>> ExtendedContext.quantize(Decimal('217'), Decimal('1e+1'))
        Decimal('2.2E+2')
        >>> ExtendedContext.quantize(Decimal('217'), Decimal('1e+2'))
        Decimal('2E+2')
        >>> ExtendedContext.quantize(1, 2)
        Decimal('1')
        >>> ExtendedContext.quantize(Decimal(1), 2)
        Decimal('1')
        >>> ExtendedContext.quantize(1, Decimal(2))
        Decimal('1')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.quantize(b, context=self)

    def radix(self):
        """Just returns 10, jako this jest Decimal, :)

        >>> ExtendedContext.radix()
        Decimal('10')
        """
        zwróć Decimal(10)

    def remainder(self, a, b):
        """Returns the remainder z integer division.

        The result jest the residue of the dividend after the operation of
        calculating integer division jako described dla divide-integer, rounded
        to precision digits jeżeli necessary.  The sign of the result, if
        non-zero, jest the same jako that of the original dividend.

        This operation will fail under the same conditions jako integer division
        (that is, jeżeli integer division on the same two operands would fail, the
        remainder cannot be calculated).

        >>> ExtendedContext.remainder(Decimal('2.1'), Decimal('3'))
        Decimal('2.1')
        >>> ExtendedContext.remainder(Decimal('10'), Decimal('3'))
        Decimal('1')
        >>> ExtendedContext.remainder(Decimal('-10'), Decimal('3'))
        Decimal('-1')
        >>> ExtendedContext.remainder(Decimal('10.2'), Decimal('1'))
        Decimal('0.2')
        >>> ExtendedContext.remainder(Decimal('10'), Decimal('0.3'))
        Decimal('0.1')
        >>> ExtendedContext.remainder(Decimal('3.6'), Decimal('1.3'))
        Decimal('1.0')
        >>> ExtendedContext.remainder(22, 6)
        Decimal('4')
        >>> ExtendedContext.remainder(Decimal(22), 6)
        Decimal('4')
        >>> ExtendedContext.remainder(22, Decimal(6))
        Decimal('4')
        """
        a = _convert_other(a, podnieśit=Prawda)
        r = a.__mod__(b, context=self)
        jeżeli r jest NotImplemented:
            podnieś TypeError("Unable to convert %s to Decimal" % b)
        inaczej:
            zwróć r

    def remainder_near(self, a, b):
        """Returns to be "a - b * n", where n jest the integer nearest the exact
        value of "x / b" (jeżeli two integers are equally near then the even one
        jest chosen).  If the result jest equal to 0 then its sign will be the
        sign of a.

        This operation will fail under the same conditions jako integer division
        (that is, jeżeli integer division on the same two operands would fail, the
        remainder cannot be calculated).

        >>> ExtendedContext.remainder_near(Decimal('2.1'), Decimal('3'))
        Decimal('-0.9')
        >>> ExtendedContext.remainder_near(Decimal('10'), Decimal('6'))
        Decimal('-2')
        >>> ExtendedContext.remainder_near(Decimal('10'), Decimal('3'))
        Decimal('1')
        >>> ExtendedContext.remainder_near(Decimal('-10'), Decimal('3'))
        Decimal('-1')
        >>> ExtendedContext.remainder_near(Decimal('10.2'), Decimal('1'))
        Decimal('0.2')
        >>> ExtendedContext.remainder_near(Decimal('10'), Decimal('0.3'))
        Decimal('0.1')
        >>> ExtendedContext.remainder_near(Decimal('3.6'), Decimal('1.3'))
        Decimal('-0.3')
        >>> ExtendedContext.remainder_near(3, 11)
        Decimal('3')
        >>> ExtendedContext.remainder_near(Decimal(3), 11)
        Decimal('3')
        >>> ExtendedContext.remainder_near(3, Decimal(11))
        Decimal('3')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.remainder_near(b, context=self)

    def rotate(self, a, b):
        """Returns a rotated copy of a, b times.

        The coefficient of the result jest a rotated copy of the digits w
        the coefficient of the first operand.  The number of places of
        rotation jest taken z the absolute value of the second operand,
        przy the rotation being to the left jeżeli the second operand jest
        positive albo to the right otherwise.

        >>> ExtendedContext.rotate(Decimal('34'), Decimal('8'))
        Decimal('400000003')
        >>> ExtendedContext.rotate(Decimal('12'), Decimal('9'))
        Decimal('12')
        >>> ExtendedContext.rotate(Decimal('123456789'), Decimal('-2'))
        Decimal('891234567')
        >>> ExtendedContext.rotate(Decimal('123456789'), Decimal('0'))
        Decimal('123456789')
        >>> ExtendedContext.rotate(Decimal('123456789'), Decimal('+2'))
        Decimal('345678912')
        >>> ExtendedContext.rotate(1333333, 1)
        Decimal('13333330')
        >>> ExtendedContext.rotate(Decimal(1333333), 1)
        Decimal('13333330')
        >>> ExtendedContext.rotate(1333333, Decimal(1))
        Decimal('13333330')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.rotate(b, context=self)

    def same_quantum(self, a, b):
        """Returns Prawda jeżeli the two operands have the same exponent.

        The result jest never affected by either the sign albo the coefficient of
        either operand.

        >>> ExtendedContext.same_quantum(Decimal('2.17'), Decimal('0.001'))
        Nieprawda
        >>> ExtendedContext.same_quantum(Decimal('2.17'), Decimal('0.01'))
        Prawda
        >>> ExtendedContext.same_quantum(Decimal('2.17'), Decimal('1'))
        Nieprawda
        >>> ExtendedContext.same_quantum(Decimal('Inf'), Decimal('-Inf'))
        Prawda
        >>> ExtendedContext.same_quantum(10000, -1)
        Prawda
        >>> ExtendedContext.same_quantum(Decimal(10000), -1)
        Prawda
        >>> ExtendedContext.same_quantum(10000, Decimal(-1))
        Prawda
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.same_quantum(b)

    def scaleb (self, a, b):
        """Returns the first operand after adding the second value its exp.

        >>> ExtendedContext.scaleb(Decimal('7.50'), Decimal('-2'))
        Decimal('0.0750')
        >>> ExtendedContext.scaleb(Decimal('7.50'), Decimal('0'))
        Decimal('7.50')
        >>> ExtendedContext.scaleb(Decimal('7.50'), Decimal('3'))
        Decimal('7.50E+3')
        >>> ExtendedContext.scaleb(1, 4)
        Decimal('1E+4')
        >>> ExtendedContext.scaleb(Decimal(1), 4)
        Decimal('1E+4')
        >>> ExtendedContext.scaleb(1, Decimal(4))
        Decimal('1E+4')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.scaleb(b, context=self)

    def shift(self, a, b):
        """Returns a shifted copy of a, b times.

        The coefficient of the result jest a shifted copy of the digits
        w the coefficient of the first operand.  The number of places
        to shift jest taken z the absolute value of the second operand,
        przy the shift being to the left jeżeli the second operand jest
        positive albo to the right otherwise.  Digits shifted into the
        coefficient are zeros.

        >>> ExtendedContext.shift(Decimal('34'), Decimal('8'))
        Decimal('400000000')
        >>> ExtendedContext.shift(Decimal('12'), Decimal('9'))
        Decimal('0')
        >>> ExtendedContext.shift(Decimal('123456789'), Decimal('-2'))
        Decimal('1234567')
        >>> ExtendedContext.shift(Decimal('123456789'), Decimal('0'))
        Decimal('123456789')
        >>> ExtendedContext.shift(Decimal('123456789'), Decimal('+2'))
        Decimal('345678900')
        >>> ExtendedContext.shift(88888888, 2)
        Decimal('888888800')
        >>> ExtendedContext.shift(Decimal(88888888), 2)
        Decimal('888888800')
        >>> ExtendedContext.shift(88888888, Decimal(2))
        Decimal('888888800')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.shift(b, context=self)

    def sqrt(self, a):
        """Square root of a non-negative number to context precision.

        If the result must be inexact, it jest rounded using the round-half-even
        algorithm.

        >>> ExtendedContext.sqrt(Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.sqrt(Decimal('-0'))
        Decimal('-0')
        >>> ExtendedContext.sqrt(Decimal('0.39'))
        Decimal('0.624499800')
        >>> ExtendedContext.sqrt(Decimal('100'))
        Decimal('10')
        >>> ExtendedContext.sqrt(Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.sqrt(Decimal('1.0'))
        Decimal('1.0')
        >>> ExtendedContext.sqrt(Decimal('1.00'))
        Decimal('1.0')
        >>> ExtendedContext.sqrt(Decimal('7'))
        Decimal('2.64575131')
        >>> ExtendedContext.sqrt(Decimal('10'))
        Decimal('3.16227766')
        >>> ExtendedContext.sqrt(2)
        Decimal('1.41421356')
        >>> ExtendedContext.prec
        9
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.sqrt(context=self)

    def subtract(self, a, b):
        """Return the difference between the two operands.

        >>> ExtendedContext.subtract(Decimal('1.3'), Decimal('1.07'))
        Decimal('0.23')
        >>> ExtendedContext.subtract(Decimal('1.3'), Decimal('1.30'))
        Decimal('0.00')
        >>> ExtendedContext.subtract(Decimal('1.3'), Decimal('2.07'))
        Decimal('-0.77')
        >>> ExtendedContext.subtract(8, 5)
        Decimal('3')
        >>> ExtendedContext.subtract(Decimal(8), 5)
        Decimal('3')
        >>> ExtendedContext.subtract(8, Decimal(5))
        Decimal('3')
        """
        a = _convert_other(a, podnieśit=Prawda)
        r = a.__sub__(b, context=self)
        jeżeli r jest NotImplemented:
            podnieś TypeError("Unable to convert %s to Decimal" % b)
        inaczej:
            zwróć r

    def to_eng_string(self, a):
        """Converts a number to a string, using scientific notation.

        The operation jest nie affected by the context.
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.to_eng_string(context=self)

    def to_sci_string(self, a):
        """Converts a number to a string, using scientific notation.

        The operation jest nie affected by the context.
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.__str__(context=self)

    def to_integral_exact(self, a):
        """Rounds to an integer.

        When the operand has a negative exponent, the result jest the same
        jako using the quantize() operation using the given operand jako the
        left-hand-operand, 1E+0 jako the right-hand-operand, oraz the precision
        of the operand jako the precision setting; Inexact oraz Rounded flags
        are allowed w this operation.  The rounding mode jest taken z the
        context.

        >>> ExtendedContext.to_integral_exact(Decimal('2.1'))
        Decimal('2')
        >>> ExtendedContext.to_integral_exact(Decimal('100'))
        Decimal('100')
        >>> ExtendedContext.to_integral_exact(Decimal('100.0'))
        Decimal('100')
        >>> ExtendedContext.to_integral_exact(Decimal('101.5'))
        Decimal('102')
        >>> ExtendedContext.to_integral_exact(Decimal('-101.5'))
        Decimal('-102')
        >>> ExtendedContext.to_integral_exact(Decimal('10E+5'))
        Decimal('1.0E+6')
        >>> ExtendedContext.to_integral_exact(Decimal('7.89E+77'))
        Decimal('7.89E+77')
        >>> ExtendedContext.to_integral_exact(Decimal('-Inf'))
        Decimal('-Infinity')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.to_integral_exact(context=self)

    def to_integral_value(self, a):
        """Rounds to an integer.

        When the operand has a negative exponent, the result jest the same
        jako using the quantize() operation using the given operand jako the
        left-hand-operand, 1E+0 jako the right-hand-operand, oraz the precision
        of the operand jako the precision setting, wyjąwszy that no flags will
        be set.  The rounding mode jest taken z the context.

        >>> ExtendedContext.to_integral_value(Decimal('2.1'))
        Decimal('2')
        >>> ExtendedContext.to_integral_value(Decimal('100'))
        Decimal('100')
        >>> ExtendedContext.to_integral_value(Decimal('100.0'))
        Decimal('100')
        >>> ExtendedContext.to_integral_value(Decimal('101.5'))
        Decimal('102')
        >>> ExtendedContext.to_integral_value(Decimal('-101.5'))
        Decimal('-102')
        >>> ExtendedContext.to_integral_value(Decimal('10E+5'))
        Decimal('1.0E+6')
        >>> ExtendedContext.to_integral_value(Decimal('7.89E+77'))
        Decimal('7.89E+77')
        >>> ExtendedContext.to_integral_value(Decimal('-Inf'))
        Decimal('-Infinity')
        """
        a = _convert_other(a, podnieśit=Prawda)
        zwróć a.to_integral_value(context=self)

    # the method name changed, but we provide also the old one, dla compatibility
    to_integral = to_integral_value

klasa _WorkRep(object):
    __slots__ = ('sign','int','exp')
    # sign: 0 albo 1
    # int:  int
    # exp:  Nic, int, albo string

    def __init__(self, value=Nic):
        jeżeli value jest Nic:
            self.sign = Nic
            self.int = 0
            self.exp = Nic
        albo_inaczej isinstance(value, Decimal):
            self.sign = value._sign
            self.int = int(value._int)
            self.exp = value._exp
        inaczej:
            # assert isinstance(value, tuple)
            self.sign = value[0]
            self.int = value[1]
            self.exp = value[2]

    def __repr__(self):
        zwróć "(%r, %r, %r)" % (self.sign, self.int, self.exp)

    __str__ = __repr__



def _normalize(op1, op2, prec = 0):
    """Normalizes op1, op2 to have the same exp oraz length of coefficient.

    Done during addition.
    """
    jeżeli op1.exp < op2.exp:
        tmp = op2
        other = op1
    inaczej:
        tmp = op1
        other = op2

    # Let exp = min(tmp.exp - 1, tmp.adjusted() - precision - 1).
    # Then adding 10**exp to tmp has the same effect (after rounding)
    # jako adding any positive quantity smaller than 10**exp; similarly
    # dla subtraction.  So jeżeli other jest smaller than 10**exp we replace
    # it przy 10**exp.  This avoids tmp.exp - other.exp getting too large.
    tmp_len = len(str(tmp.int))
    other_len = len(str(other.int))
    exp = tmp.exp + min(-1, tmp_len - prec - 2)
    jeżeli other_len + other.exp - 1 < exp:
        other.int = 1
        other.exp = exp

    tmp.int *= 10 ** (tmp.exp - other.exp)
    tmp.exp = other.exp
    zwróć op1, op2

##### Integer arithmetic functions used by ln, log10, exp oraz __pow__ #####

_nbits = int.bit_length

def _decimal_lshift_exact(n, e):
    """ Given integers n oraz e, zwróć n * 10**e jeżeli it's an integer, inaczej Nic.

    The computation jest designed to avoid computing large powers of 10
    unnecessarily.

    >>> _decimal_lshift_exact(3, 4)
    30000
    >>> _decimal_lshift_exact(300, -999999999)  # returns Nic

    """
    jeżeli n == 0:
        zwróć 0
    albo_inaczej e >= 0:
        zwróć n * 10**e
    inaczej:
        # val_n = largest power of 10 dividing n.
        str_n = str(abs(n))
        val_n = len(str_n) - len(str_n.rstrip('0'))
        zwróć Nic jeżeli val_n < -e inaczej n // 10**-e

def _sqrt_nearest(n, a):
    """Closest integer to the square root of the positive integer n.  a jest
    an initial approximation to the square root.  Any positive integer
    will do dla a, but the closer a jest to the square root of n the
    faster convergence will be.

    """
    jeżeli n <= 0 albo a <= 0:
        podnieś ValueError("Both arguments to _sqrt_nearest should be positive.")

    b=0
    dopóki a != b:
        b, a = a, a--n//a>>1
    zwróć a

def _rshift_nearest(x, shift):
    """Given an integer x oraz a nonnegative integer shift, zwróć closest
    integer to x / 2**shift; use round-to-even w case of a tie.

    """
    b, q = 1 << shift, x >> shift
    zwróć q + (2*(x & (b-1)) + (q&1) > b)

def _div_nearest(a, b):
    """Closest integer to a/b, a oraz b positive integers; rounds to even
    w the case of a tie.

    """
    q, r = divmod(a, b)
    zwróć q + (2*r + (q&1) > b)

def _ilog(x, M, L = 8):
    """Integer approximation to M*log(x/M), przy absolute error boundable
    w terms only of x/M.

    Given positive integers x oraz M, zwróć an integer approximation to
    M * log(x/M).  For L = 8 oraz 0.1 <= x/M <= 10 the difference
    between the approximation oraz the exact result jest at most 22.  For
    L = 8 oraz 1.0 <= x/M <= 10.0 the difference jest at most 15.  In
    both cases these are upper bounds on the error; it will usually be
    much smaller."""

    # The basic algorithm jest the following: let log1p be the function
    # log1p(x) = log(1+x).  Then log(x/M) = log1p((x-M)/M).  We use
    # the reduction
    #
    #    log1p(y) = 2*log1p(y/(1+sqrt(1+y)))
    #
    # repeatedly until the argument to log1p jest small (< 2**-L w
    # absolute value).  For small y we can use the Taylor series
    # expansion
    #
    #    log1p(y) ~ y - y**2/2 + y**3/3 - ... - (-y)**T/T
    #
    # truncating at T such that y**T jest small enough.  The whole
    # computation jest carried out w a form of fixed-point arithmetic,
    # przy a real number z being represented by an integer
    # approximation to z*M.  To avoid loss of precision, the y below
    # jest actually an integer approximation to 2**R*y*M, where R jest the
    # number of reductions performed so far.

    y = x-M
    # argument reduction; R = number of reductions performed
    R = 0
    dopóki (R <= L oraz abs(y) << L-R >= M albo
           R > L oraz abs(y) >> R-L >= M):
        y = _div_nearest((M*y) << 1,
                         M + _sqrt_nearest(M*(M+_rshift_nearest(y, R)), M))
        R += 1

    # Taylor series przy T terms
    T = -int(-10*len(str(M))//(3*L))
    yshift = _rshift_nearest(y, R)
    w = _div_nearest(M, T)
    dla k w range(T-1, 0, -1):
        w = _div_nearest(M, k) - _div_nearest(yshift*w, M)

    zwróć _div_nearest(w*y, M)

def _dlog10(c, e, p):
    """Given integers c, e oraz p przy c > 0, p >= 0, compute an integer
    approximation to 10**p * log10(c*10**e), przy an absolute error of
    at most 1.  Assumes that c*10**e jest nie exactly 1."""

    # increase precision by 2; compensate dla this by dividing
    # final result by 100
    p += 2

    # write c*10**e jako d*10**f przy either:
    #   f >= 0 oraz 1 <= d <= 10, albo
    #   f <= 0 oraz 0.1 <= d <= 1.
    # Thus dla c*10**e close to 1, f = 0
    l = len(str(c))
    f = e+l - (e+l >= 1)

    jeżeli p > 0:
        M = 10**p
        k = e+p-f
        jeżeli k >= 0:
            c *= 10**k
        inaczej:
            c = _div_nearest(c, 10**-k)

        log_d = _ilog(c, M) # error < 5 + 22 = 27
        log_10 = _log10_digits(p) # error < 1
        log_d = _div_nearest(log_d*M, log_10)
        log_tenpower = f*M # exact
    inaczej:
        log_d = 0  # error < 2.31
        log_tenpower = _div_nearest(f, 10**-p) # error < 0.5

    zwróć _div_nearest(log_tenpower+log_d, 100)

def _dlog(c, e, p):
    """Given integers c, e oraz p przy c > 0, compute an integer
    approximation to 10**p * log(c*10**e), przy an absolute error of
    at most 1.  Assumes that c*10**e jest nie exactly 1."""

    # Increase precision by 2. The precision increase jest compensated
    # dla at the end przy a division by 100.
    p += 2

    # rewrite c*10**e jako d*10**f przy either f >= 0 oraz 1 <= d <= 10,
    # albo f <= 0 oraz 0.1 <= d <= 1.  Then we can compute 10**p * log(c*10**e)
    # jako 10**p * log(d) + 10**p*f * log(10).
    l = len(str(c))
    f = e+l - (e+l >= 1)

    # compute approximation to 10**p*log(d), przy error < 27
    jeżeli p > 0:
        k = e+p-f
        jeżeli k >= 0:
            c *= 10**k
        inaczej:
            c = _div_nearest(c, 10**-k)  # error of <= 0.5 w c

        # _ilog magnifies existing error w c by a factor of at most 10
        log_d = _ilog(c, 10**p) # error < 5 + 22 = 27
    inaczej:
        # p <= 0: just approximate the whole thing by 0; error < 2.31
        log_d = 0

    # compute approximation to f*10**p*log(10), przy error < 11.
    jeżeli f:
        extra = len(str(abs(f)))-1
        jeżeli p + extra >= 0:
            # error w f * _log10_digits(p+extra) < |f| * 1 = |f|
            # after division, error < |f|/10**extra + 0.5 < 10 + 0.5 < 11
            f_log_ten = _div_nearest(f*_log10_digits(p+extra), 10**extra)
        inaczej:
            f_log_ten = 0
    inaczej:
        f_log_ten = 0

    # error w sum < 11+27 = 38; error after division < 0.38 + 0.5 < 1
    zwróć _div_nearest(f_log_ten + log_d, 100)

klasa _Log10Memoize(object):
    """Class to compute, store, oraz allow retrieval of, digits of the
    constant log(10) = 2.302585....  This constant jest needed by
    Decimal.ln, Decimal.log10, Decimal.exp oraz Decimal.__pow__."""
    def __init__(self):
        self.digits = "23025850929940456840179914546843642076011014886"

    def getdigits(self, p):
        """Given an integer p >= 0, zwróć floor(10**p)*log(10).

        For example, self.getdigits(3) returns 2302.
        """
        # digits are stored jako a string, dla quick conversion to
        # integer w the case that we've already computed enough
        # digits; the stored digits should always be correct
        # (truncated, nie rounded to nearest).
        jeżeli p < 0:
            podnieś ValueError("p should be nonnegative")

        jeżeli p >= len(self.digits):
            # compute p+3, p+6, p+9, ... digits; continue until at
            # least one of the extra digits jest nonzero
            extra = 3
            dopóki Prawda:
                # compute p+extra digits, correct to within 1ulp
                M = 10**(p+extra+2)
                digits = str(_div_nearest(_ilog(10*M, M), 100))
                jeżeli digits[-extra:] != '0'*extra:
                    przerwij
                extra += 3
            # keep all reliable digits so far; remove trailing zeros
            # oraz next nonzero digit
            self.digits = digits.rstrip('0')[:-1]
        zwróć int(self.digits[:p+1])

_log10_digits = _Log10Memoize().getdigits

def _iexp(x, M, L=8):
    """Given integers x oraz M, M > 0, such that x/M jest small w absolute
    value, compute an integer approximation to M*exp(x/M).  For 0 <=
    x/M <= 2.4, the absolute error w the result jest bounded by 60 (and
    jest usually much smaller)."""

    # Algorithm: to compute exp(z) dla a real number z, first divide z
    # by a suitable power R of 2 so that |z/2**R| < 2**-L.  Then
    # compute expm1(z/2**R) = exp(z/2**R) - 1 using the usual Taylor
    # series
    #
    #     expm1(x) = x + x**2/2! + x**3/3! + ...
    #
    # Now use the identity
    #
    #     expm1(2x) = expm1(x)*(expm1(x)+2)
    #
    # R times to compute the sequence expm1(z/2**R),
    # expm1(z/2**(R-1)), ... , exp(z/2), exp(z).

    # Find R such that x/2**R/M <= 2**-L
    R = _nbits((x<<L)//M)

    # Taylor series.  (2**L)**T > M
    T = -int(-10*len(str(M))//(3*L))
    y = _div_nearest(x, T)
    Mshift = M<<R
    dla i w range(T-1, 0, -1):
        y = _div_nearest(x*(Mshift + y), Mshift * i)

    # Expansion
    dla k w range(R-1, -1, -1):
        Mshift = M<<(k+2)
        y = _div_nearest(y*(y+Mshift), Mshift)

    zwróć M+y

def _dexp(c, e, p):
    """Compute an approximation to exp(c*10**e), przy p decimal places of
    precision.

    Returns integers d, f such that:

      10**(p-1) <= d <= 10**p, oraz
      (d-1)*10**f < exp(c*10**e) < (d+1)*10**f

    In other words, d*10**f jest an approximation to exp(c*10**e) przy p
    digits of precision, oraz przy an error w d of at most 1.  This jest
    almost, but nie quite, the same jako the error being < 1ulp: when d
    = 10**(p-1) the error could be up to 10 ulp."""

    # we'll call iexp przy M = 10**(p+2), giving p+3 digits of precision
    p += 2

    # compute log(10) przy extra precision = adjusted exponent of c*10**e
    extra = max(0, e + len(str(c)) - 1)
    q = p + extra

    # compute quotient c*10**e/(log(10)) = c*10**(e+q)/(log(10)*10**q),
    # rounding down
    shift = e+q
    jeżeli shift >= 0:
        cshift = c*10**shift
    inaczej:
        cshift = c//10**-shift
    quot, rem = divmod(cshift, _log10_digits(q))

    # reduce remainder back to original precision
    rem = _div_nearest(rem, 10**extra)

    # error w result of _iexp < 120;  error after division < 0.62
    zwróć _div_nearest(_iexp(rem, 10**p), 1000), quot - p + 3

def _dpower(xc, xe, yc, ye, p):
    """Given integers xc, xe, yc oraz ye representing Decimals x = xc*10**xe oraz
    y = yc*10**ye, compute x**y.  Returns a pair of integers (c, e) such that:

      10**(p-1) <= c <= 10**p, oraz
      (c-1)*10**e < x**y < (c+1)*10**e

    w other words, c*10**e jest an approximation to x**y przy p digits
    of precision, oraz przy an error w c of at most 1.  (This jest
    almost, but nie quite, the same jako the error being < 1ulp: when c
    == 10**(p-1) we can only guarantee error < 10ulp.)

    We assume that: x jest positive oraz nie equal to 1, oraz y jest nonzero.
    """

    # Find b such that 10**(b-1) <= |y| <= 10**b
    b = len(str(abs(yc))) + ye

    # log(x) = lxc*10**(-p-b-1), to p+b+1 places after the decimal point
    lxc = _dlog(xc, xe, p+b+1)

    # compute product y*log(x) = yc*lxc*10**(-p-b-1+ye) = pc*10**(-p-1)
    shift = ye-b
    jeżeli shift >= 0:
        pc = lxc*yc*10**shift
    inaczej:
        pc = _div_nearest(lxc*yc, 10**-shift)

    jeżeli pc == 0:
        # we prefer a result that isn't exactly 1; this makes it
        # easier to compute a correctly rounded result w __pow__
        jeżeli ((len(str(xc)) + xe >= 1) == (yc > 0)): # jeżeli x**y > 1:
            coeff, exp = 10**(p-1)+1, 1-p
        inaczej:
            coeff, exp = 10**p-1, -p
    inaczej:
        coeff, exp = _dexp(pc, -(p+1), p+1)
        coeff = _div_nearest(coeff, 10)
        exp += 1

    zwróć coeff, exp

def _log10_lb(c, correction = {
        '1': 100, '2': 70, '3': 53, '4': 40, '5': 31,
        '6': 23, '7': 16, '8': 10, '9': 5}):
    """Compute a lower bound dla 100*log10(c) dla a positive integer c."""
    jeżeli c <= 0:
        podnieś ValueError("The argument to _log10_lb should be nonnegative.")
    str_c = str(c)
    zwróć 100*len(str_c) - correction[str_c[0]]

##### Helper Functions ####################################################

def _convert_other(other, podnieśit=Nieprawda, allow_float=Nieprawda):
    """Convert other to Decimal.

    Verifies that it's ok to use w an implicit construction.
    If allow_float jest true, allow conversion z float;  this
    jest used w the comparison methods (__eq__ oraz friends).

    """
    jeżeli isinstance(other, Decimal):
        zwróć other
    jeżeli isinstance(other, int):
        zwróć Decimal(other)
    jeżeli allow_float oraz isinstance(other, float):
        zwróć Decimal.from_float(other)

    jeżeli podnieśit:
        podnieś TypeError("Unable to convert %s to Decimal" % other)
    zwróć NotImplemented

def _convert_for_comparison(self, other, equality_op=Nieprawda):
    """Given a Decimal instance self oraz a Python object other, zwróć
    a pair (s, o) of Decimal instances such that "s op o" jest
    equivalent to "self op other" dla any of the 6 comparison
    operators "op".

    """
    jeżeli isinstance(other, Decimal):
        zwróć self, other

    # Comparison przy a Rational instance (also includes integers):
    # self op n/d <=> self*d op n (dla n oraz d integers, d positive).
    # A NaN albo infinity can be left unchanged without affecting the
    # comparison result.
    jeżeli isinstance(other, _numbers.Rational):
        jeżeli nie self._is_special:
            self = _dec_from_triple(self._sign,
                                    str(int(self._int) * other.denominator),
                                    self._exp)
        zwróć self, Decimal(other.numerator)

    # Comparisons przy float oraz complex types.  == oraz != comparisons
    # przy complex numbers should succeed, returning either Prawda albo Nieprawda
    # jako appropriate.  Other comparisons zwróć NotImplemented.
    jeżeli equality_op oraz isinstance(other, _numbers.Complex) oraz other.imag == 0:
        other = other.real
    jeżeli isinstance(other, float):
        context = getcontext()
        jeżeli equality_op:
            context.flags[FloatOperation] = 1
        inaczej:
            context._raise_error(FloatOperation,
                "strict semantics dla mixing floats oraz Decimals are enabled")
        zwróć self, Decimal.from_float(other)
    zwróć NotImplemented, NotImplemented


##### Setup Specific Contexts ############################################

# The default context prototype used by Context()
# Is mutable, so that new contexts can have different default values

DefaultContext = Context(
        prec=28, rounding=ROUND_HALF_EVEN,
        traps=[DivisionByZero, Overflow, InvalidOperation],
        flags=[],
        Emax=999999,
        Emin=-999999,
        capitals=1,
        clamp=0
)

# Pre-made alternate contexts offered by the specification
# Don't change these; the user should be able to select these
# contexts oraz be able to reproduce results z other implementations
# of the spec.

BasicContext = Context(
        prec=9, rounding=ROUND_HALF_UP,
        traps=[DivisionByZero, Overflow, InvalidOperation, Clamped, Underflow],
        flags=[],
)

ExtendedContext = Context(
        prec=9, rounding=ROUND_HALF_EVEN,
        traps=[],
        flags=[],
)


##### crud dla parsing strings #############################################
#
# Regular expression used dla parsing numeric strings.  Additional
# comments:
#
# 1. Uncomment the two '\s*' lines to allow leading and/or trailing
# whitespace.  But note that the specification disallows whitespace w
# a numeric string.
#
# 2. For finite numbers (nie infinities oraz NaNs) the body of the
# number between the optional sign oraz the optional exponent must have
# at least one decimal digit, possibly after the decimal point.  The
# lookahead expression '(?=\d|\.\d)' checks this.

zaimportuj re
_parser = re.compile(r"""        # A numeric string consists of:
#    \s*
    (?P<sign>[-+])?              # an optional sign, followed by either...
    (
        (?=\d|\.\d)              # ...a number (przy at least one digit)
        (?P<int>\d*)             # having a (possibly empty) integer part
        (\.(?P<frac>\d*))?       # followed by an optional fractional part
        (E(?P<exp>[-+]?\d+))?    # followed by an optional exponent, or...
    |
        Inf(inity)?              # ...an infinity, or...
    |
        (?P<signal>s)?           # ...an (optionally signaling)
        NaN                      # NaN
        (?P<diag>\d*)            # przy (possibly empty) diagnostic info.
    )
#    \s*
    \Z
""", re.VERBOSE | re.IGNORECASE).match

_all_zeros = re.compile('0*$').match
_exact_half = re.compile('50*$').match

##### PEP3101 support functions ##############################################
# The functions w this section have little to do przy the Decimal
# class, oraz could potentially be reused albo adapted dla other pure
# Python numeric classes that want to implement __format__
#
# A format specifier dla Decimal looks like:
#
#   [[fill]align][sign][#][0][minimumwidth][,][.precision][type]

_parse_format_specifier_regex = re.compile(r"""\A
(?:
   (?P<fill>.)?
   (?P<align>[<>=^])
)?
(?P<sign>[-+ ])?
(?P<alt>\#)?
(?P<zeropad>0)?
(?P<minimumwidth>(?!0)\d+)?
(?P<thousands_sep>,)?
(?:\.(?P<precision>0|(?!0)\d+))?
(?P<type>[eEfFgGn%])?
\Z
""", re.VERBOSE|re.DOTALL)

usuń re

# The locale module jest only needed dla the 'n' format specifier.  The
# rest of the PEP 3101 code functions quite happily without it, so we
# don't care too much jeżeli locale isn't present.
spróbuj:
    zaimportuj locale jako _locale
wyjąwszy ImportError:
    dalej

def _parse_format_specifier(format_spec, _localeconv=Nic):
    """Parse oraz validate a format specifier.

    Turns a standard numeric format specifier into a dict, przy the
    following entries:

      fill: fill character to pad field to minimum width
      align: alignment type, either '<', '>', '=' albo '^'
      sign: either '+', '-' albo ' '
      minimumwidth: nonnegative integer giving minimum width
      zeropad: boolean, indicating whether to pad przy zeros
      thousands_sep: string to use jako thousands separator, albo ''
      grouping: grouping dla thousands separators, w format
        used by localeconv
      decimal_point: string to use dla decimal point
      precision: nonnegative integer giving precision, albo Nic
      type: one of the characters 'eEfFgG%', albo Nic

    """
    m = _parse_format_specifier_regex.match(format_spec)
    jeżeli m jest Nic:
        podnieś ValueError("Invalid format specifier: " + format_spec)

    # get the dictionary
    format_dict = m.groupdict()

    # zeropad; defaults dla fill oraz alignment.  If zero padding
    # jest requested, the fill oraz align fields should be absent.
    fill = format_dict['fill']
    align = format_dict['align']
    format_dict['zeropad'] = (format_dict['zeropad'] jest nie Nic)
    jeżeli format_dict['zeropad']:
        jeżeli fill jest nie Nic:
            podnieś ValueError("Fill character conflicts przy '0'"
                             " w format specifier: " + format_spec)
        jeżeli align jest nie Nic:
            podnieś ValueError("Alignment conflicts przy '0' w "
                             "format specifier: " + format_spec)
    format_dict['fill'] = fill albo ' '
    # PEP 3101 originally specified that the default alignment should
    # be left;  it was later agreed that right-aligned makes more sense
    # dla numeric types.  See http://bugs.python.org/issue6857.
    format_dict['align'] = align albo '>'

    # default sign handling: '-' dla negative, '' dla positive
    jeżeli format_dict['sign'] jest Nic:
        format_dict['sign'] = '-'

    # minimumwidth defaults to 0; precision remains Nic jeżeli nie given
    format_dict['minimumwidth'] = int(format_dict['minimumwidth'] albo '0')
    jeżeli format_dict['precision'] jest nie Nic:
        format_dict['precision'] = int(format_dict['precision'])

    # jeżeli format type jest 'g' albo 'G' then a precision of 0 makes little
    # sense; convert it to 1.  Same jeżeli format type jest unspecified.
    jeżeli format_dict['precision'] == 0:
        jeżeli format_dict['type'] jest Nic albo format_dict['type'] w 'gGn':
            format_dict['precision'] = 1

    # determine thousands separator, grouping, oraz decimal separator, oraz
    # add appropriate entries to format_dict
    jeżeli format_dict['type'] == 'n':
        # apart z separators, 'n' behaves just like 'g'
        format_dict['type'] = 'g'
        jeżeli _localeconv jest Nic:
            _localeconv = _locale.localeconv()
        jeżeli format_dict['thousands_sep'] jest nie Nic:
            podnieś ValueError("Explicit thousands separator conflicts przy "
                             "'n' type w format specifier: " + format_spec)
        format_dict['thousands_sep'] = _localeconv['thousands_sep']
        format_dict['grouping'] = _localeconv['grouping']
        format_dict['decimal_point'] = _localeconv['decimal_point']
    inaczej:
        jeżeli format_dict['thousands_sep'] jest Nic:
            format_dict['thousands_sep'] = ''
        format_dict['grouping'] = [3, 0]
        format_dict['decimal_point'] = '.'

    zwróć format_dict

def _format_align(sign, body, spec):
    """Given an unpadded, non-aligned numeric string 'body' oraz sign
    string 'sign', add padding oraz alignment conforming to the given
    format specifier dictionary 'spec' (as produced by
    parse_format_specifier).

    """
    # how much extra space do we have to play with?
    minimumwidth = spec['minimumwidth']
    fill = spec['fill']
    padding = fill*(minimumwidth - len(sign) - len(body))

    align = spec['align']
    jeżeli align == '<':
        result = sign + body + padding
    albo_inaczej align == '>':
        result = padding + sign + body
    albo_inaczej align == '=':
        result = sign + padding + body
    albo_inaczej align == '^':
        half = len(padding)//2
        result = padding[:half] + sign + body + padding[half:]
    inaczej:
        podnieś ValueError('Unrecognised alignment field')

    zwróć result

def _group_lengths(grouping):
    """Convert a localeconv-style grouping into a (possibly infinite)
    iterable of integers representing group lengths.

    """
    # The result z localeconv()['grouping'], oraz the input to this
    # function, should be a list of integers w one of the
    # following three forms:
    #
    #   (1) an empty list, albo
    #   (2) nonempty list of positive integers + [0]
    #   (3) list of positive integers + [locale.CHAR_MAX], albo

    z itertools zaimportuj chain, repeat
    jeżeli nie grouping:
        zwróć []
    albo_inaczej grouping[-1] == 0 oraz len(grouping) >= 2:
        zwróć chain(grouping[:-1], repeat(grouping[-2]))
    albo_inaczej grouping[-1] == _locale.CHAR_MAX:
        zwróć grouping[:-1]
    inaczej:
        podnieś ValueError('unrecognised format dla grouping')

def _insert_thousands_sep(digits, spec, min_width=1):
    """Insert thousands separators into a digit string.

    spec jest a dictionary whose keys should include 'thousands_sep' oraz
    'grouping'; typically it's the result of parsing the format
    specifier using _parse_format_specifier.

    The min_width keyword argument gives the minimum length of the
    result, which will be padded on the left przy zeros jeżeli necessary.

    If necessary, the zero padding adds an extra '0' on the left to
    avoid a leading thousands separator.  For example, inserting
    commas every three digits w '123456', przy min_width=8, gives
    '0,123,456', even though that has length 9.

    """

    sep = spec['thousands_sep']
    grouping = spec['grouping']

    groups = []
    dla l w _group_lengths(grouping):
        jeżeli l <= 0:
            podnieś ValueError("group length should be positive")
        # max(..., 1) forces at least 1 digit to the left of a separator
        l = min(max(len(digits), min_width, 1), l)
        groups.append('0'*(l - len(digits)) + digits[-l:])
        digits = digits[:-l]
        min_width -= l
        jeżeli nie digits oraz min_width <= 0:
            przerwij
        min_width -= len(sep)
    inaczej:
        l = max(len(digits), min_width, 1)
        groups.append('0'*(l - len(digits)) + digits[-l:])
    zwróć sep.join(reversed(groups))

def _format_sign(is_negative, spec):
    """Determine sign character."""

    jeżeli is_negative:
        zwróć '-'
    albo_inaczej spec['sign'] w ' +':
        zwróć spec['sign']
    inaczej:
        zwróć ''

def _format_number(is_negative, intpart, fracpart, exp, spec):
    """Format a number, given the following data:

    is_negative: true jeżeli the number jest negative, inaczej false
    intpart: string of digits that must appear before the decimal point
    fracpart: string of digits that must come after the point
    exp: exponent, jako an integer
    spec: dictionary resulting z parsing the format specifier

    This function uses the information w spec to:
      insert separators (decimal separator oraz thousands separators)
      format the sign
      format the exponent
      add trailing '%' dla the '%' type
      zero-pad jeżeli necessary
      fill oraz align jeżeli necessary
    """

    sign = _format_sign(is_negative, spec)

    jeżeli fracpart albo spec['alt']:
        fracpart = spec['decimal_point'] + fracpart

    jeżeli exp != 0 albo spec['type'] w 'eE':
        echar = {'E': 'E', 'e': 'e', 'G': 'E', 'g': 'e'}[spec['type']]
        fracpart += "{0}{1:+}".format(echar, exp)
    jeżeli spec['type'] == '%':
        fracpart += '%'

    jeżeli spec['zeropad']:
        min_width = spec['minimumwidth'] - len(fracpart) - len(sign)
    inaczej:
        min_width = 0
    intpart = _insert_thousands_sep(intpart, spec, min_width)

    zwróć _format_align(sign, intpart+fracpart, spec)


##### Useful Constants (internal use only) ################################

# Reusable defaults
_Infinity = Decimal('Inf')
_NegativeInfinity = Decimal('-Inf')
_NaN = Decimal('NaN')
_Zero = Decimal(0)
_One = Decimal(1)
_NegativeOne = Decimal(-1)

# _SignedInfinity[sign] jest infinity w/ that sign
_SignedInfinity = (_Infinity, _NegativeInfinity)

# Constants related to the hash implementation;  hash(x) jest based
# on the reduction of x modulo _PyHASH_MODULUS
_PyHASH_MODULUS = sys.hash_info.modulus
# hash values to use dla positive oraz negative infinities, oraz nans
_PyHASH_INF = sys.hash_info.inf
_PyHASH_NAN = sys.hash_info.nan

# _PyHASH_10INV jest the inverse of 10 modulo the prime _PyHASH_MODULUS
_PyHASH_10INV = pow(10, _PyHASH_MODULUS - 2, _PyHASH_MODULUS)
usuń sys
