#
# Copyright (c) 2008-2012 Stefan Krah. All rights reserved.
#
# Redistribution oraz use w source oraz binary forms, przy albo without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions oraz the following disclaimer.
#
# 2. Redistributions w binary form must reproduce the above copyright
#    notice, this list of conditions oraz the following disclaimer w the
#    documentation and/or other materials provided przy the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

#
# Usage: python deccheck.py [--short|--medium|--long|--all]
#

zaimportuj sys, random
z copy zaimportuj copy
z collections zaimportuj defaultdict
z test.support zaimportuj import_fresh_module
z randdec zaimportuj randfloat, all_unary, all_binary, all_ternary
z randdec zaimportuj unary_optarg, binary_optarg, ternary_optarg
z formathelper zaimportuj rand_format, rand_locale
z _pydecimal zaimportuj _dec_from_triple

C = import_fresh_module('decimal', fresh=['_decimal'])
P = import_fresh_module('decimal', blocked=['_decimal'])
EXIT_STATUS = 0


# Contains all categories of Decimal methods.
Functions = {
    # Plain unary:
    'unary': (
        '__abs__', '__bool__', '__ceil__', '__complex__', '__copy__',
        '__floor__', '__float__', '__hash__', '__int__', '__neg__',
        '__pos__', '__reduce__', '__repr__', '__str__', '__trunc__',
        'adjusted', 'as_tuple', 'canonical', 'conjugate', 'copy_abs',
        'copy_negate', 'is_canonical', 'is_finite', 'is_infinite',
        'is_nan', 'is_qnan', 'is_signed', 'is_snan', 'is_zero', 'radix'
    ),
    # Unary przy optional context:
    'unary_ctx': (
        'exp', 'is_normal', 'is_subnormal', 'ln', 'log10', 'logb',
        'logical_invert', 'next_minus', 'next_plus', 'normalize',
        'number_class', 'sqrt', 'to_eng_string'
    ),
    # Unary przy optional rounding mode oraz context:
    'unary_rnd_ctx': ('to_integral', 'to_integral_exact', 'to_integral_value'),
    # Plain binary:
    'binary': (
        '__add__', '__divmod__', '__eq__', '__floordiv__', '__ge__', '__gt__',
        '__le__', '__lt__', '__mod__', '__mul__', '__ne__', '__pow__',
        '__radd__', '__rdivmod__', '__rfloordiv__', '__rmod__', '__rmul__',
        '__rpow__', '__rsub__', '__rtruediv__', '__sub__', '__truediv__',
        'compare_total', 'compare_total_mag', 'copy_sign', 'quantize',
        'same_quantum'
    ),
    # Binary przy optional context:
    'binary_ctx': (
        'compare', 'compare_signal', 'logical_and', 'logical_or', 'logical_xor',
        'max', 'max_mag', 'min', 'min_mag', 'next_toward', 'remainder_near',
        'rotate', 'scaleb', 'shift'
    ),
    # Plain ternary:
    'ternary': ('__pow__',),
    # Ternary przy optional context:
    'ternary_ctx': ('fma',),
    # Special:
    'special': ('__format__', '__reduce_ex__', '__round__', 'from_float',
                'quantize'),
    # Properties:
    'property': ('real', 'imag')
}

# Contains all categories of Context methods. The n-ary classification
# applies to the number of Decimal arguments.
ContextFunctions = {
    # Plain nullary:
    'nullary': ('context.__hash__', 'context.__reduce__', 'context.radix'),
    # Plain unary:
    'unary': ('context.abs', 'context.canonical', 'context.copy_abs',
              'context.copy_decimal', 'context.copy_negate',
              'context.create_decimal', 'context.exp', 'context.is_canonical',
              'context.is_finite', 'context.is_infinite', 'context.is_nan',
              'context.is_normal', 'context.is_qnan', 'context.is_signed',
              'context.is_snan', 'context.is_subnormal', 'context.is_zero',
              'context.ln', 'context.log10', 'context.logb',
              'context.logical_invert', 'context.minus', 'context.next_minus',
              'context.next_plus', 'context.normalize', 'context.number_class',
              'context.plus', 'context.sqrt', 'context.to_eng_string',
              'context.to_integral', 'context.to_integral_exact',
              'context.to_integral_value', 'context.to_sci_string'
    ),
    # Plain binary:
    'binary': ('context.add', 'context.compare', 'context.compare_signal',
               'context.compare_total', 'context.compare_total_mag',
               'context.copy_sign', 'context.divide', 'context.divide_int',
               'context.divmod', 'context.logical_and', 'context.logical_or',
               'context.logical_xor', 'context.max', 'context.max_mag',
               'context.min', 'context.min_mag', 'context.multiply',
               'context.next_toward', 'context.power', 'context.quantize',
               'context.remainder', 'context.remainder_near', 'context.rotate',
               'context.same_quantum', 'context.scaleb', 'context.shift',
               'context.subtract'
    ),
    # Plain ternary:
    'ternary': ('context.fma', 'context.power'),
    # Special:
    'special': ('context.__reduce_ex__', 'context.create_decimal_from_float')
}

# Functions that require a restricted exponent range dla reasonable runtimes.
UnaryRestricted = [
  '__ceil__', '__floor__', '__int__', '__trunc__',
  'to_integral', 'to_integral_value'
]

BinaryRestricted = ['__round__']

TernaryRestricted = ['__pow__', 'context.power']


# ======================================================================
#                            Unified Context
# ======================================================================

# Translate symbols.
CondMap = {
        C.Clamped:             P.Clamped,
        C.ConversionSyntax:    P.ConversionSyntax,
        C.DivisionByZero:      P.DivisionByZero,
        C.DivisionImpossible:  P.InvalidOperation,
        C.DivisionUndefined:   P.DivisionUndefined,
        C.Inexact:             P.Inexact,
        C.InvalidContext:      P.InvalidContext,
        C.InvalidOperation:    P.InvalidOperation,
        C.Overflow:            P.Overflow,
        C.Rounded:             P.Rounded,
        C.Subnormal:           P.Subnormal,
        C.Underflow:           P.Underflow,
        C.FloatOperation:      P.FloatOperation,
}

RoundModes = [C.ROUND_UP, C.ROUND_DOWN, C.ROUND_CEILING, C.ROUND_FLOOR,
              C.ROUND_HALF_UP, C.ROUND_HALF_DOWN, C.ROUND_HALF_EVEN,
              C.ROUND_05UP]


klasa Context(object):
    """Provides a convenient way of syncing the C oraz P contexts"""

    __slots__ = ['c', 'p']

    def __init__(self, c_ctx=Nic, p_ctx=Nic):
        """Initialization jest z the C context"""
        self.c = C.getcontext() jeżeli c_ctx jest Nic inaczej c_ctx
        self.p = P.getcontext() jeżeli p_ctx jest Nic inaczej p_ctx
        self.p.prec = self.c.prec
        self.p.Emin = self.c.Emin
        self.p.Emax = self.c.Emax
        self.p.rounding = self.c.rounding
        self.p.capitals = self.c.capitals
        self.settraps([sig dla sig w self.c.traps jeżeli self.c.traps[sig]])
        self.setstatus([sig dla sig w self.c.flags jeżeli self.c.flags[sig]])
        self.p.clamp = self.c.clamp

    def __str__(self):
        zwróć str(self.c) + '\n' + str(self.p)

    def getprec(self):
        assert(self.c.prec == self.p.prec)
        zwróć self.c.prec

    def setprec(self, val):
        self.c.prec = val
        self.p.prec = val

    def getemin(self):
        assert(self.c.Emin == self.p.Emin)
        zwróć self.c.Emin

    def setemin(self, val):
        self.c.Emin = val
        self.p.Emin = val

    def getemax(self):
        assert(self.c.Emax == self.p.Emax)
        zwróć self.c.Emax

    def setemax(self, val):
        self.c.Emax = val
        self.p.Emax = val

    def getround(self):
        assert(self.c.rounding == self.p.rounding)
        zwróć self.c.rounding

    def setround(self, val):
        self.c.rounding = val
        self.p.rounding = val

    def getcapitals(self):
        assert(self.c.capitals == self.p.capitals)
        zwróć self.c.capitals

    def setcapitals(self, val):
        self.c.capitals = val
        self.p.capitals = val

    def getclamp(self):
        assert(self.c.clamp == self.p.clamp)
        zwróć self.c.clamp

    def setclamp(self, val):
        self.c.clamp = val
        self.p.clamp = val

    prec = property(getprec, setprec)
    Emin = property(getemin, setemin)
    Emax = property(getemax, setemax)
    rounding = property(getround, setround)
    clamp = property(getclamp, setclamp)
    capitals = property(getcapitals, setcapitals)

    def clear_traps(self):
        self.c.clear_traps()
        dla trap w self.p.traps:
            self.p.traps[trap] = Nieprawda

    def clear_status(self):
        self.c.clear_flags()
        self.p.clear_flags()

    def settraps(self, lst):
        """lst: C signal list"""
        self.clear_traps()
        dla signal w lst:
            self.c.traps[signal] = Prawda
            self.p.traps[CondMap[signal]] = Prawda

    def setstatus(self, lst):
        """lst: C signal list"""
        self.clear_status()
        dla signal w lst:
            self.c.flags[signal] = Prawda
            self.p.flags[CondMap[signal]] = Prawda

    def assert_eq_status(self):
        """assert equality of C oraz P status"""
        dla signal w self.c.flags:
            jeżeli self.c.flags[signal] == (nie self.p.flags[CondMap[signal]]):
                zwróć Nieprawda
        zwróć Prawda


# We don't want exceptions so that we can compare the status flags.
context = Context()
context.Emin = C.MIN_EMIN
context.Emax = C.MAX_EMAX
context.clear_traps()

# When creating decimals, _decimal jest ultimately limited by the maximum
# context values. We emulate this restriction dla decimal.py.
maxcontext = P.Context(
    prec=C.MAX_PREC,
    Emin=C.MIN_EMIN,
    Emax=C.MAX_EMAX,
    rounding=P.ROUND_HALF_UP,
    capitals=1
)
maxcontext.clamp = 0

def RestrictedDecimal(value):
    maxcontext.traps = copy(context.p.traps)
    maxcontext.clear_flags()
    jeżeli isinstance(value, str):
        value = value.strip()
    dec = maxcontext.create_decimal(value)
    jeżeli maxcontext.flags[P.Inexact] albo \
       maxcontext.flags[P.Rounded] albo \
       maxcontext.flags[P.Clamped] albo \
       maxcontext.flags[P.InvalidOperation]:
        zwróć context.p._raise_error(P.InvalidOperation)
    jeżeli maxcontext.flags[P.FloatOperation]:
        context.p.flags[P.FloatOperation] = Prawda
    zwróć dec


# ======================================================================
#      TestSet: Organize data oraz events during a single test case
# ======================================================================

klasa RestrictedList(list):
    """List that can only be modified by appending items."""
    def __getattribute__(self, name):
        jeżeli name != 'append':
            podnieś AttributeError("unsupported operation")
        zwróć list.__getattribute__(self, name)
    def unsupported(self, *_):
        podnieś AttributeError("unsupported operation")
    __add__ = __delattr__ = __delitem__ = __iadd__ = __imul__ = unsupported
    __mul__ = __reversed__ = __rmul__ = __setattr__ = __setitem__ = unsupported

klasa TestSet(object):
    """A TestSet contains the original input operands, converted operands,
       Python exceptions that occurred either during conversion albo during
       execution of the actual function, oraz the final results.

       For safety, most attributes are lists that only support the append
       operation.

       If a function name jest prefixed przy 'context.', the corresponding
       context method jest called.
    """
    def __init__(self, funcname, operands):
        jeżeli funcname.startswith("context."):
            self.funcname = funcname.replace("context.", "")
            self.contextfunc = Prawda
        inaczej:
            self.funcname = funcname
            self.contextfunc = Nieprawda
        self.op = operands               # raw operand tuple
        self.context = context           # context used dla the operation
        self.cop = RestrictedList()      # converted C.Decimal operands
        self.cex = RestrictedList()      # Python exceptions dla C.Decimal
        self.cresults = RestrictedList() # C.Decimal results
        self.pop = RestrictedList()      # converted P.Decimal operands
        self.pex = RestrictedList()      # Python exceptions dla P.Decimal
        self.presults = RestrictedList() # P.Decimal results


# ======================================================================
#                SkipHandler: skip known discrepancies
# ======================================================================

klasa SkipHandler:
    """Handle known discrepancies between decimal.py oraz _decimal.so.
       These are either ULP differences w the power function albo
       extremely minor issues."""

    def __init__(self):
        self.ulpdiff = 0
        self.powmod_zeros = 0
        self.maxctx = P.Context(Emax=10**18, Emin=-10**18)

    def default(self, t):
        zwróć Nieprawda
    __ge__ =  __gt__ = __le__ = __lt__ = __ne__ = __eq__ = default
    __reduce__ = __format__ = __repr__ = __str__ = default

    def harrison_ulp(self, dec):
        """ftp://ftp.inria.fr/INRIA/publication/publi-pdf/RR/RR-5504.pdf"""
        a = dec.next_plus()
        b = dec.next_minus()
        zwróć abs(a - b)

    def standard_ulp(self, dec, prec):
        zwróć _dec_from_triple(0, '1', dec._exp+len(dec._int)-prec)

    def rounding_direction(self, x, mode):
        """Determine the effective direction of the rounding when
           the exact result x jest rounded according to mode.
           Return -1 dla downwards, 0 dla undirected, 1 dla upwards,
           2 dla ROUND_05UP."""
        cmp = 1 jeżeli x.compare_total(P.Decimal("+0")) >= 0 inaczej -1

        jeżeli mode w (P.ROUND_HALF_EVEN, P.ROUND_HALF_UP, P.ROUND_HALF_DOWN):
            zwróć 0
        albo_inaczej mode == P.ROUND_CEILING:
            zwróć 1
        albo_inaczej mode == P.ROUND_FLOOR:
            zwróć -1
        albo_inaczej mode == P.ROUND_UP:
            zwróć cmp
        albo_inaczej mode == P.ROUND_DOWN:
            zwróć -cmp
        albo_inaczej mode == P.ROUND_05UP:
            zwróć 2
        inaczej:
            podnieś ValueError("Unexpected rounding mode: %s" % mode)

    def check_ulpdiff(self, exact, rounded):
        # current precision
        p = context.p.prec

        # Convert infinities to the largest representable number + 1.
        x = exact
        jeżeli exact.is_infinite():
            x = _dec_from_triple(exact._sign, '10', context.p.Emax)
        y = rounded
        jeżeli rounded.is_infinite():
            y = _dec_from_triple(rounded._sign, '10', context.p.Emax)

        # err = (rounded - exact) / ulp(rounded)
        self.maxctx.prec = p * 2
        t = self.maxctx.subtract(y, x)
        jeżeli context.c.flags[C.Clamped] albo \
           context.c.flags[C.Underflow]:
            # The standard ulp does nie work w Underflow territory.
            ulp = self.harrison_ulp(y)
        inaczej:
            ulp = self.standard_ulp(y, p)
        # Error w ulps.
        err = self.maxctx.divide(t, ulp)

        dir = self.rounding_direction(x, context.p.rounding)
        jeżeli dir == 0:
            jeżeli P.Decimal("-0.6") < err < P.Decimal("0.6"):
                zwróć Prawda
        albo_inaczej dir == 1: # directed, upwards
            jeżeli P.Decimal("-0.1") < err < P.Decimal("1.1"):
                zwróć Prawda
        albo_inaczej dir == -1: # directed, downwards
            jeżeli P.Decimal("-1.1") < err < P.Decimal("0.1"):
                zwróć Prawda
        inaczej: # ROUND_05UP
            jeżeli P.Decimal("-1.1") < err < P.Decimal("1.1"):
                zwróć Prawda

        print("ulp: %s  error: %s  exact: %s  c_rounded: %s"
              % (ulp, err, exact, rounded))
        zwróć Nieprawda

    def bin_resolve_ulp(self, t):
        """Check jeżeli results of _decimal's power function are within the
           allowed ulp ranges."""
        # NaNs are beyond repair.
        jeżeli t.rc.is_nan() albo t.rp.is_nan():
            zwróć Nieprawda

        # "exact" result, double precision, half_even
        self.maxctx.prec = context.p.prec * 2

        op1, op2 = t.pop[0], t.pop[1]
        jeżeli t.contextfunc:
            exact = getattr(self.maxctx, t.funcname)(op1, op2)
        inaczej:
            exact = getattr(op1, t.funcname)(op2, context=self.maxctx)

        # _decimal's rounded result
        rounded = P.Decimal(t.cresults[0])

        self.ulpdiff += 1
        zwróć self.check_ulpdiff(exact, rounded)

    ############################ Correct rounding #############################
    def resolve_underflow(self, t):
        """In extremely rare cases where the infinite precision result jest just
           below etiny, cdecimal does nie set Subnormal/Underflow. Example:

           setcontext(Context(prec=21, rounding=ROUND_UP, Emin=-55, Emax=85))
           Decimal("1.00000000000000000000000000000000000000000000000"
                   "0000000100000000000000000000000000000000000000000"
                   "0000000000000025").ln()
        """
        jeżeli t.cresults != t.presults:
            zwróć Nieprawda # Results must be identical.
        jeżeli context.c.flags[C.Rounded] oraz \
           context.c.flags[C.Inexact] oraz \
           context.p.flags[P.Rounded] oraz \
           context.p.flags[P.Inexact]:
            zwróć Prawda # Subnormal/Underflow may be missing.
        zwróć Nieprawda

    def exp(self, t):
        """Resolve Underflow albo ULP difference."""
        zwróć self.resolve_underflow(t)

    def log10(self, t):
        """Resolve Underflow albo ULP difference."""
        zwróć self.resolve_underflow(t)

    def ln(self, t):
        """Resolve Underflow albo ULP difference."""
        zwróć self.resolve_underflow(t)

    def __pow__(self, t):
        """Always calls the resolve function. C.Decimal does nie have correct
           rounding dla the power function."""
        jeżeli context.c.flags[C.Rounded] oraz \
           context.c.flags[C.Inexact] oraz \
           context.p.flags[P.Rounded] oraz \
           context.p.flags[P.Inexact]:
            zwróć self.bin_resolve_ulp(t)
        inaczej:
            zwróć Nieprawda
    power = __rpow__ = __pow__

    ############################## Technicalities #############################
    def __float__(self, t):
        """NaN comparison w the verify() function obviously gives an
           incorrect answer:  nan == nan -> Nieprawda"""
        jeżeli t.cop[0].is_nan() oraz t.pop[0].is_nan():
            zwróć Prawda
        zwróć Nieprawda
    __complex__ = __float__

    def __radd__(self, t):
        """decimal.py gives precedence to the first NaN; this jest
           nie important, jako __radd__ will nie be called for
           two decimal arguments."""
        jeżeli t.rc.is_nan() oraz t.rp.is_nan():
            zwróć Prawda
        zwróć Nieprawda
    __rmul__ = __radd__

    ################################ Various ##################################
    def __round__(self, t):
        """Exception: Decimal('1').__round__(-100000000000000000000000000)
           Should it really be InvalidOperation?"""
        jeżeli t.rc jest Nic oraz t.rp.is_nan():
            zwróć Prawda
        zwróć Nieprawda

shandler = SkipHandler()
def skip_error(t):
    zwróć getattr(shandler, t.funcname, shandler.default)(t)


# ======================================================================
#                      Handling verification errors
# ======================================================================

klasa VerifyError(Exception):
    """Verification failed."""
    dalej

def function_as_string(t):
    jeżeli t.contextfunc:
        cargs = t.cop
        pargs = t.pop
        cfunc = "c_func: %s(" % t.funcname
        pfunc = "p_func: %s(" % t.funcname
    inaczej:
        cself, cargs = t.cop[0], t.cop[1:]
        pself, pargs = t.pop[0], t.pop[1:]
        cfunc = "c_func: %s.%s(" % (repr(cself), t.funcname)
        pfunc = "p_func: %s.%s(" % (repr(pself), t.funcname)

    err = cfunc
    dla arg w cargs:
        err += "%s, " % repr(arg)
    err = err.rstrip(", ")
    err += ")\n"

    err += pfunc
    dla arg w pargs:
        err += "%s, " % repr(arg)
    err = err.rstrip(", ")
    err += ")"

    zwróć err

def podnieś_error(t):
    global EXIT_STATUS

    jeżeli skip_error(t):
        zwróć
    EXIT_STATUS = 1

    err = "Error w %s:\n\n" % t.funcname
    err += "input operands: %s\n\n" % (t.op,)
    err += function_as_string(t)
    err += "\n\nc_result: %s\np_result: %s\n\n" % (t.cresults, t.presults)
    err += "c_exceptions: %s\np_exceptions: %s\n\n" % (t.cex, t.pex)
    err += "%s\n\n" % str(t.context)

    podnieś VerifyError(err)


# ======================================================================
#                        Main testing functions
#
#  The procedure jest always (t jest the TestSet):
#
#   convert(t) -> Initialize the TestSet jako necessary.
#
#                 Return 0 dla early abortion (e.g. jeżeli a TypeError
#                 occurs during conversion, there jest nothing to test).
#
#                 Return 1 dla continuing przy the test case.
#
#   callfuncs(t) -> Call the relevant function dla each implementation
#                   oraz record the results w the TestSet.
#
#   verify(t) -> Verify the results. If verification fails, details
#                are printed to stdout.
# ======================================================================

def convert(t, convstr=Prawda):
    """ t jest the testset. At this stage the testset contains a tuple of
        operands t.op of various types. For decimal methods the first
        operand (self) jest always converted to Decimal. If 'convstr' jest
        true, string operands are converted jako well.

        Context operands are of type deccheck.Context, rounding mode
        operands are given jako a tuple (C.rounding, P.rounding).

        Other types (float, int, etc.) are left unchanged.
    """
    dla i, op w enumerate(t.op):

        context.clear_status()

        jeżeli op w RoundModes:
            t.cop.append(op)
            t.pop.append(op)

        albo_inaczej nie t.contextfunc oraz i == 0 albo \
             convstr oraz isinstance(op, str):
            spróbuj:
                c = C.Decimal(op)
                cex = Nic
            wyjąwszy (TypeError, ValueError, OverflowError) jako e:
                c = Nic
                cex = e.__class__

            spróbuj:
                p = RestrictedDecimal(op)
                pex = Nic
            wyjąwszy (TypeError, ValueError, OverflowError) jako e:
                p = Nic
                pex = e.__class__

            t.cop.append(c)
            t.cex.append(cex)
            t.pop.append(p)
            t.pex.append(pex)

            jeżeli cex jest pex:
                jeżeli str(c) != str(p) albo nie context.assert_eq_status():
                    podnieś_error(t)
                jeżeli cex oraz pex:
                    # nothing to test
                    zwróć 0
            inaczej:
                podnieś_error(t)

        albo_inaczej isinstance(op, Context):
            t.context = op
            t.cop.append(op.c)
            t.pop.append(op.p)

        inaczej:
            t.cop.append(op)
            t.pop.append(op)

    zwróć 1

def callfuncs(t):
    """ t jest the testset. At this stage the testset contains operand lists
        t.cop oraz t.pop dla the C oraz Python versions of decimal.
        For Decimal methods, the first operands are of type C.Decimal oraz
        P.Decimal respectively. The remaining operands can have various types.
        For Context methods, all operands can have any type.

        t.rc oraz t.rp are the results of the operation.
    """
    context.clear_status()

    spróbuj:
        jeżeli t.contextfunc:
            cargs = t.cop
            t.rc = getattr(context.c, t.funcname)(*cargs)
        inaczej:
            cself = t.cop[0]
            cargs = t.cop[1:]
            t.rc = getattr(cself, t.funcname)(*cargs)
        t.cex.append(Nic)
    wyjąwszy (TypeError, ValueError, OverflowError, MemoryError) jako e:
        t.rc = Nic
        t.cex.append(e.__class__)

    spróbuj:
        jeżeli t.contextfunc:
            pargs = t.pop
            t.rp = getattr(context.p, t.funcname)(*pargs)
        inaczej:
            pself = t.pop[0]
            pargs = t.pop[1:]
            t.rp = getattr(pself, t.funcname)(*pargs)
        t.pex.append(Nic)
    wyjąwszy (TypeError, ValueError, OverflowError, MemoryError) jako e:
        t.rp = Nic
        t.pex.append(e.__class__)

def verify(t, stat):
    """ t jest the testset. At this stage the testset contains the following
        tuples:

            t.op: original operands
            t.cop: C.Decimal operands (see convert dla details)
            t.pop: P.Decimal operands (see convert dla details)
            t.rc: C result
            t.rp: Python result

        t.rc oraz t.rp can have various types.
    """
    t.cresults.append(str(t.rc))
    t.presults.append(str(t.rp))
    jeżeli isinstance(t.rc, C.Decimal) oraz isinstance(t.rp, P.Decimal):
        # General case: both results are Decimals.
        t.cresults.append(t.rc.to_eng_string())
        t.cresults.append(t.rc.as_tuple())
        t.cresults.append(str(t.rc.imag))
        t.cresults.append(str(t.rc.real))
        t.presults.append(t.rp.to_eng_string())
        t.presults.append(t.rp.as_tuple())
        t.presults.append(str(t.rp.imag))
        t.presults.append(str(t.rp.real))

        nc = t.rc.number_class().lstrip('+-s')
        stat[nc] += 1
    inaczej:
        # Results z e.g. __divmod__ can only be compared jako strings.
        jeżeli nie isinstance(t.rc, tuple) oraz nie isinstance(t.rp, tuple):
            jeżeli t.rc != t.rp:
                podnieś_error(t)
        stat[type(t.rc).__name__] += 1

    # The zwróć value lists must be equal.
    jeżeli t.cresults != t.presults:
        podnieś_error(t)
    # The Python exception lists (TypeError, etc.) must be equal.
    jeżeli t.cex != t.pex:
        podnieś_error(t)
    # The context flags must be equal.
    jeżeli nie t.context.assert_eq_status():
        podnieś_error(t)


# ======================================================================
#                           Main test loops
#
#  test_method(method, testspecs, testfunc) ->
#
#     Loop through various context settings. The degree of
#     thoroughness jest determined by 'testspec'. For each
#     setting, call 'testfunc'. Generally, 'testfunc' itself
#     a loop, iterating through many test cases generated
#     by the functions w randdec.py.
#
#  test_n-ary(method, prec, exp_range, restricted_range, itr, stat) ->
#
#     'test_unary', 'test_binary' oraz 'test_ternary' are the
#     main test functions dalejed to 'test_method'. They deal
#     przy the regular cases. The thoroughness of testing jest
#     determined by 'itr'.
#
#     'prec', 'exp_range' oraz 'restricted_range' are dalejed
#     to the test-generating functions oraz limit the generated
#     values. In some cases, dla reasonable run times a
#     maximum exponent of 9999 jest required.
#
#     The 'stat' parameter jest dalejed down to the 'verify'
#     function, which records statistics dla the result values.
# ======================================================================

def log(fmt, args=Nic):
    jeżeli args:
        sys.stdout.write(''.join((fmt, '\n')) % args)
    inaczej:
        sys.stdout.write(''.join((str(fmt), '\n')))
    sys.stdout.flush()

def test_method(method, testspecs, testfunc):
    """Iterate a test function through many context settings."""
    log("testing %s ...", method)
    stat = defaultdict(int)
    dla spec w testspecs:
        jeżeli 'samples' w spec:
            spec['prec'] = sorted(random.sample(range(1, 101),
                                  spec['samples']))
        dla prec w spec['prec']:
            context.prec = prec
            dla expts w spec['expts']:
                emin, emax = expts
                jeżeli emin == 'rand':
                    context.Emin = random.randrange(-1000, 0)
                    context.Emax = random.randrange(prec, 1000)
                inaczej:
                    context.Emin, context.Emax = emin, emax
                jeżeli prec > context.Emax: kontynuuj
                log("    prec: %d  emin: %d  emax: %d",
                    (context.prec, context.Emin, context.Emax))
                restr_range = 9999 jeżeli context.Emax > 9999 inaczej context.Emax+99
                dla rounding w RoundModes:
                    context.rounding = rounding
                    context.capitals = random.randrange(2)
                    jeżeli spec['clamp'] == 'rand':
                        context.clamp = random.randrange(2)
                    inaczej:
                        context.clamp = spec['clamp']
                    exprange = context.c.Emax
                    testfunc(method, prec, exprange, restr_range,
                             spec['iter'], stat)
    log("    result types: %s" % sorted([t dla t w stat.items()]))

def test_unary(method, prec, exp_range, restricted_range, itr, stat):
    """Iterate a unary function through many test cases."""
    jeżeli method w UnaryRestricted:
        exp_range = restricted_range
    dla op w all_unary(prec, exp_range, itr):
        t = TestSet(method, op)
        spróbuj:
            jeżeli nie convert(t):
                kontynuuj
            callfuncs(t)
            verify(t, stat)
        wyjąwszy VerifyError jako err:
            log(err)

    jeżeli nie method.startswith('__'):
        dla op w unary_optarg(prec, exp_range, itr):
            t = TestSet(method, op)
            spróbuj:
                jeżeli nie convert(t):
                    kontynuuj
                callfuncs(t)
                verify(t, stat)
            wyjąwszy VerifyError jako err:
                log(err)

def test_binary(method, prec, exp_range, restricted_range, itr, stat):
    """Iterate a binary function through many test cases."""
    jeżeli method w BinaryRestricted:
        exp_range = restricted_range
    dla op w all_binary(prec, exp_range, itr):
        t = TestSet(method, op)
        spróbuj:
            jeżeli nie convert(t):
                kontynuuj
            callfuncs(t)
            verify(t, stat)
        wyjąwszy VerifyError jako err:
            log(err)

    jeżeli nie method.startswith('__'):
        dla op w binary_optarg(prec, exp_range, itr):
            t = TestSet(method, op)
            spróbuj:
                jeżeli nie convert(t):
                    kontynuuj
                callfuncs(t)
                verify(t, stat)
            wyjąwszy VerifyError jako err:
                log(err)

def test_ternary(method, prec, exp_range, restricted_range, itr, stat):
    """Iterate a ternary function through many test cases."""
    jeżeli method w TernaryRestricted:
        exp_range = restricted_range
    dla op w all_ternary(prec, exp_range, itr):
        t = TestSet(method, op)
        spróbuj:
            jeżeli nie convert(t):
                kontynuuj
            callfuncs(t)
            verify(t, stat)
        wyjąwszy VerifyError jako err:
            log(err)

    jeżeli nie method.startswith('__'):
        dla op w ternary_optarg(prec, exp_range, itr):
            t = TestSet(method, op)
            spróbuj:
                jeżeli nie convert(t):
                    kontynuuj
                callfuncs(t)
                verify(t, stat)
            wyjąwszy VerifyError jako err:
                log(err)

def test_format(method, prec, exp_range, restricted_range, itr, stat):
    """Iterate the __format__ method through many test cases."""
    dla op w all_unary(prec, exp_range, itr):
        fmt1 = rand_format(chr(random.randrange(0, 128)), 'EeGgn')
        fmt2 = rand_locale()
        dla fmt w (fmt1, fmt2):
            fmtop = (op[0], fmt)
            t = TestSet(method, fmtop)
            spróbuj:
                jeżeli nie convert(t, convstr=Nieprawda):
                    kontynuuj
                callfuncs(t)
                verify(t, stat)
            wyjąwszy VerifyError jako err:
                log(err)
    dla op w all_unary(prec, 9999, itr):
        fmt1 = rand_format(chr(random.randrange(0, 128)), 'Ff%')
        fmt2 = rand_locale()
        dla fmt w (fmt1, fmt2):
            fmtop = (op[0], fmt)
            t = TestSet(method, fmtop)
            spróbuj:
                jeżeli nie convert(t, convstr=Nieprawda):
                    kontynuuj
                callfuncs(t)
                verify(t, stat)
            wyjąwszy VerifyError jako err:
                log(err)

def test_round(method, prec, exprange, restricted_range, itr, stat):
    """Iterate the __round__ method through many test cases."""
    dla op w all_unary(prec, 9999, itr):
        n = random.randrange(10)
        roundop = (op[0], n)
        t = TestSet(method, roundop)
        spróbuj:
            jeżeli nie convert(t):
                kontynuuj
            callfuncs(t)
            verify(t, stat)
        wyjąwszy VerifyError jako err:
            log(err)

def test_from_float(method, prec, exprange, restricted_range, itr, stat):
    """Iterate the __float__ method through many test cases."""
    dla rounding w RoundModes:
        context.rounding = rounding
        dla i w range(1000):
            f = randfloat()
            op = (f,) jeżeli method.startswith("context.") inaczej ("sNaN", f)
            t = TestSet(method, op)
            spróbuj:
                jeżeli nie convert(t):
                    kontynuuj
                callfuncs(t)
                verify(t, stat)
            wyjąwszy VerifyError jako err:
                log(err)

def randcontext(exprange):
    c = Context(C.Context(), P.Context())
    c.Emax = random.randrange(1, exprange+1)
    c.Emin = random.randrange(-exprange, 0)
    maxprec = 100 jeżeli c.Emax >= 100 inaczej c.Emax
    c.prec = random.randrange(1, maxprec+1)
    c.clamp = random.randrange(2)
    c.clear_traps()
    zwróć c

def test_quantize_api(method, prec, exprange, restricted_range, itr, stat):
    """Iterate the 'quantize' method through many test cases, using
       the optional arguments."""
    dla op w all_binary(prec, restricted_range, itr):
        dla rounding w RoundModes:
            c = randcontext(exprange)
            quantizeop = (op[0], op[1], rounding, c)
            t = TestSet(method, quantizeop)
            spróbuj:
                jeżeli nie convert(t):
                    kontynuuj
                callfuncs(t)
                verify(t, stat)
            wyjąwszy VerifyError jako err:
                log(err)


def check_untested(funcdict, c_cls, p_cls):
    """Determine untested, C-only oraz Python-only attributes.
       Uncomment print lines dla debugging."""
    c_attr = set(dir(c_cls))
    p_attr = set(dir(p_cls))
    intersect = c_attr & p_attr

    funcdict['c_only'] = tuple(sorted(c_attr-intersect))
    funcdict['p_only'] = tuple(sorted(p_attr-intersect))

    tested = set()
    dla lst w funcdict.values():
        dla v w lst:
            v = v.replace("context.", "") jeżeli c_cls == C.Context inaczej v
            tested.add(v)

    funcdict['untested'] = tuple(sorted(intersect-tested))

    #dla key w ('untested', 'c_only', 'p_only'):
    #    s = 'Context' jeżeli c_cls == C.Context inaczej 'Decimal'
    #    print("\n%s %s:\n%s" % (s, key, funcdict[key]))


jeżeli __name__ == '__main__':

    zaimportuj time

    randseed = int(time.time())
    random.seed(randseed)

    # Set up the testspecs list. A testspec jest simply a dictionary
    # that determines the amount of different contexts that 'test_method'
    # will generate.
    base_expts = [(C.MIN_EMIN, C.MAX_EMAX)]
    jeżeli C.MAX_EMAX == 999999999999999999:
        base_expts.append((-999999999, 999999999))

    # Basic contexts.
    base = {
        'expts': base_expts,
        'prec': [],
        'clamp': 'rand',
        'iter': Nic,
        'samples': Nic,
    }
    # Contexts przy small values dla prec, emin, emax.
    small = {
        'prec': [1, 2, 3, 4, 5],
        'expts': [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5)],
        'clamp': 'rand',
        'iter': Nic
    }
    # IEEE interchange format.
    ieee = [
        # DECIMAL32
        {'prec': [7], 'expts': [(-95, 96)], 'clamp': 1, 'iter': Nic},
        # DECIMAL64
        {'prec': [16], 'expts': [(-383, 384)], 'clamp': 1, 'iter': Nic},
        # DECIMAL128
        {'prec': [34], 'expts': [(-6143, 6144)], 'clamp': 1, 'iter': Nic}
    ]

    jeżeli '--medium' w sys.argv:
        base['expts'].append(('rand', 'rand'))
        # 5 random precisions
        base['samples'] = 5
        testspecs = [small] + ieee + [base]
    jeżeli '--long' w sys.argv:
        base['expts'].append(('rand', 'rand'))
        # 10 random precisions
        base['samples'] = 10
        testspecs = [small] + ieee + [base]
    albo_inaczej '--all' w sys.argv:
        base['expts'].append(('rand', 'rand'))
        # All precisions w [1, 100]
        base['samples'] = 100
        testspecs = [small] + ieee + [base]
    inaczej: # --short
        rand_ieee = random.choice(ieee)
        base['iter'] = small['iter'] = rand_ieee['iter'] = 1
        # 1 random precision oraz exponent pair
        base['samples'] = 1
        base['expts'] = [random.choice(base_expts)]
        # 1 random precision oraz exponent pair
        prec = random.randrange(1, 6)
        small['prec'] = [prec]
        small['expts'] = [(-prec, prec)]
        testspecs = [small, rand_ieee, base]

    check_untested(Functions, C.Decimal, P.Decimal)
    check_untested(ContextFunctions, C.Context, P.Context)


    log("\n\nRandom seed: %d\n\n", randseed)

    # Decimal methods:
    dla method w Functions['unary'] + Functions['unary_ctx'] + \
                  Functions['unary_rnd_ctx']:
        test_method(method, testspecs, test_unary)

    dla method w Functions['binary'] + Functions['binary_ctx']:
        test_method(method, testspecs, test_binary)

    dla method w Functions['ternary'] + Functions['ternary_ctx']:
        test_method(method, testspecs, test_ternary)

    test_method('__format__', testspecs, test_format)
    test_method('__round__', testspecs, test_round)
    test_method('from_float', testspecs, test_from_float)
    test_method('quantize', testspecs, test_quantize_api)

    # Context methods:
    dla method w ContextFunctions['unary']:
        test_method(method, testspecs, test_unary)

    dla method w ContextFunctions['binary']:
        test_method(method, testspecs, test_binary)

    dla method w ContextFunctions['ternary']:
        test_method(method, testspecs, test_ternary)

    test_method('context.create_decimal_from_float', testspecs, test_from_float)


    sys.exit(EXIT_STATUS)
