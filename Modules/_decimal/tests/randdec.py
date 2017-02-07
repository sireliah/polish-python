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


# Generate test cases dla deccheck.py.


#
# Grammar z http://speleotrove.com/decimal/daconvs.html
#
# sign           ::=  '+' | '-'
# digit          ::=  '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' |
#                     '8' | '9'
# indicator      ::=  'e' | 'E'
# digits         ::=  digit [digit]...
# decimal-part   ::=  digits '.' [digits] | ['.'] digits
# exponent-part  ::=  indicator [sign] digits
# infinity       ::=  'Infinity' | 'Inf'
# nan            ::=  'NaN' [digits] | 'sNaN' [digits]
# numeric-value  ::=  decimal-part [exponent-part] | infinity
# numeric-string ::=  [sign] numeric-value | [sign] nan
#


z random zaimportuj randrange, sample
z fractions zaimportuj Fraction
z randfloat zaimportuj un_randfloat, bin_randfloat, tern_randfloat


def sign():
    jeżeli randrange(2):
        jeżeli randrange(2): zwróć '+'
        zwróć ''
    zwróć '-'

def indicator():
    zwróć "eE"[randrange(2)]

def digits(maxprec):
    jeżeli maxprec == 0: zwróć ''
    zwróć str(randrange(10**maxprec))

def dot():
    jeżeli randrange(2): zwróć '.'
    zwróć ''

def decimal_part(maxprec):
    jeżeli randrange(100) > 60: # integers
        zwróć digits(maxprec)
    jeżeli randrange(2):
        intlen = randrange(1, maxprec+1)
        fraclen = maxprec-intlen
        intpart = digits(intlen)
        fracpart = digits(fraclen)
        zwróć ''.join((intpart, '.', fracpart))
    inaczej:
        zwróć ''.join((dot(), digits(maxprec)))

def expdigits(maxexp):
    zwróć str(randrange(maxexp))

def exponent_part(maxexp):
    zwróć ''.join((indicator(), sign(), expdigits(maxexp)))

def infinity():
    jeżeli randrange(2): zwróć 'Infinity'
    zwróć 'Inf'

def nan():
    d = ''
    jeżeli randrange(2):
        d = digits(randrange(99))
    jeżeli randrange(2):
        zwróć ''.join(('NaN', d))
    inaczej:
        zwróć ''.join(('sNaN', d))

def numeric_value(maxprec, maxexp):
    jeżeli randrange(100) > 90:
        zwróć infinity()
    exp_part = ''
    jeżeli randrange(100) > 60:
        exp_part = exponent_part(maxexp)
    zwróć ''.join((decimal_part(maxprec), exp_part))

def numeric_string(maxprec, maxexp):
    jeżeli randrange(100) > 95:
        zwróć ''.join((sign(), nan()))
    inaczej:
        zwróć ''.join((sign(), numeric_value(maxprec, maxexp)))

def randdec(maxprec, maxexp):
    zwróć numeric_string(maxprec, maxexp)

def rand_adjexp(maxprec, maxadjexp):
    d = digits(maxprec)
    maxexp = maxadjexp-len(d)+1
    jeżeli maxexp == 0: maxexp = 1
    exp = str(randrange(maxexp-2*(abs(maxexp)), maxexp))
    zwróć ''.join((sign(), d, 'E', exp))


def ndigits(n):
    jeżeli n < 1: zwróć 0
    zwróć randrange(10**(n-1), 10**n)

def randtuple(maxprec, maxexp):
    n = randrange(100)
    sign = randrange(2)
    coeff = ndigits(maxprec)
    jeżeli n >= 95:
        coeff = ()
        exp = 'F'
    albo_inaczej n >= 85:
        coeff = tuple(map(int, str(ndigits(maxprec))))
        exp = "nN"[randrange(2)]
    inaczej:
        coeff = tuple(map(int, str(ndigits(maxprec))))
        exp = randrange(-maxexp, maxexp)
    zwróć (sign, coeff, exp)

def from_triple(sign, coeff, exp):
    zwróć ''.join((str(sign*coeff), indicator(), str(exp)))


# Close to 10**n
def un_close_to_pow10(prec, maxexp, itr=Nic):
    jeżeli itr jest Nic:
        lst = range(prec+30)
    inaczej:
        lst = sample(range(prec+30), itr)
    nines = [10**n - 1 dla n w lst]
    pow10 = [10**n dla n w lst]
    dla coeff w nines:
        uzyskaj coeff
        uzyskaj -coeff
        uzyskaj from_triple(1, coeff, randrange(2*maxexp))
        uzyskaj from_triple(-1, coeff, randrange(2*maxexp))
    dla coeff w pow10:
        uzyskaj coeff
        uzyskaj -coeff

# Close to 10**n
def bin_close_to_pow10(prec, maxexp, itr=Nic):
    jeżeli itr jest Nic:
        lst = range(prec+30)
    inaczej:
        lst = sample(range(prec+30), itr)
    nines = [10**n - 1 dla n w lst]
    pow10 = [10**n dla n w lst]
    dla coeff w nines:
        uzyskaj coeff, 1
        uzyskaj -coeff, -1
        uzyskaj 1, coeff
        uzyskaj -1, -coeff
        uzyskaj from_triple(1, coeff, randrange(2*maxexp)), 1
        uzyskaj from_triple(-1, coeff, randrange(2*maxexp)), -1
        uzyskaj 1, from_triple(1, coeff, -randrange(2*maxexp))
        uzyskaj -1, from_triple(-1, coeff, -randrange(2*maxexp))
    dla coeff w pow10:
        uzyskaj coeff, -1
        uzyskaj -coeff, 1
        uzyskaj 1, -coeff
        uzyskaj -coeff, 1

# Close to 1:
def close_to_one_greater(prec, emax, emin):
    rprec = 10**prec
    zwróć ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec))))

def close_to_one_less(prec, emax, emin):
    rprec = 10**prec
    zwróć ''.join(("0.9", '9'*randrange(prec),
                   str(randrange(rprec))))

# Close to 0:
def close_to_zero_greater(prec, emax, emin):
    rprec = 10**prec
    zwróć ''.join(("0.", '0'*randrange(prec),
                   str(randrange(rprec))))

def close_to_zero_less(prec, emax, emin):
    rprec = 10**prec
    zwróć ''.join(("-0.", '0'*randrange(prec),
                   str(randrange(rprec))))

# Close to emax:
def close_to_emax_less(prec, emax, emin):
    rprec = 10**prec
    zwróć ''.join(("9.", '9'*randrange(prec),
                   str(randrange(rprec)), "E", str(emax)))

def close_to_emax_greater(prec, emax, emin):
    rprec = 10**prec
    zwróć ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec)), "E", str(emax+1)))

# Close to emin:
def close_to_emin_greater(prec, emax, emin):
    rprec = 10**prec
    zwróć ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec)), "E", str(emin)))

def close_to_emin_less(prec, emax, emin):
    rprec = 10**prec
    zwróć ''.join(("9.", '9'*randrange(prec),
                   str(randrange(rprec)), "E", str(emin-1)))

# Close to etiny:
def close_to_etiny_greater(prec, emax, emin):
    rprec = 10**prec
    etiny = emin - (prec - 1)
    zwróć ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec)), "E", str(etiny)))

def close_to_etiny_less(prec, emax, emin):
    rprec = 10**prec
    etiny = emin - (prec - 1)
    zwróć ''.join(("9.", '9'*randrange(prec),
                   str(randrange(rprec)), "E", str(etiny-1)))


def close_to_min_etiny_greater(prec, max_prec, min_emin):
    rprec = 10**prec
    etiny = min_emin - (max_prec - 1)
    zwróć ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec)), "E", str(etiny)))

def close_to_min_etiny_less(prec, max_prec, min_emin):
    rprec = 10**prec
    etiny = min_emin - (max_prec - 1)
    zwróć ''.join(("9.", '9'*randrange(prec),
                   str(randrange(rprec)), "E", str(etiny-1)))


close_funcs = [
  close_to_one_greater, close_to_one_less, close_to_zero_greater,
  close_to_zero_less, close_to_emax_less, close_to_emax_greater,
  close_to_emin_greater, close_to_emin_less, close_to_etiny_greater,
  close_to_etiny_less, close_to_min_etiny_greater, close_to_min_etiny_less
]


def un_close_numbers(prec, emax, emin, itr=Nic):
    jeżeli itr jest Nic:
        itr = 1000
    dla _ w range(itr):
        dla func w close_funcs:
            uzyskaj func(prec, emax, emin)

def bin_close_numbers(prec, emax, emin, itr=Nic):
    jeżeli itr jest Nic:
        itr = 1000
    dla _ w range(itr):
        dla func1 w close_funcs:
            dla func2 w close_funcs:
                uzyskaj func1(prec, emax, emin), func2(prec, emax, emin)
        dla func w close_funcs:
            uzyskaj randdec(prec, emax), func(prec, emax, emin)
            uzyskaj func(prec, emax, emin), randdec(prec, emax)

def tern_close_numbers(prec, emax, emin, itr):
    jeżeli itr jest Nic:
        itr = 1000
    dla _ w range(itr):
        dla func1 w close_funcs:
            dla func2 w close_funcs:
                dla func3 w close_funcs:
                    uzyskaj (func1(prec, emax, emin), func2(prec, emax, emin),
                           func3(prec, emax, emin))
        dla func w close_funcs:
            uzyskaj (randdec(prec, emax), func(prec, emax, emin),
                   func(prec, emax, emin))
            uzyskaj (func(prec, emax, emin), randdec(prec, emax),
                   func(prec, emax, emin))
            uzyskaj (func(prec, emax, emin), func(prec, emax, emin),
                   randdec(prec, emax))
        dla func w close_funcs:
            uzyskaj (randdec(prec, emax), randdec(prec, emax),
                   func(prec, emax, emin))
            uzyskaj (randdec(prec, emax), func(prec, emax, emin),
                   randdec(prec, emax))
            uzyskaj (func(prec, emax, emin), randdec(prec, emax),
                   randdec(prec, emax))


# If itr == Nic, test all digit lengths up to prec + 30
def un_incr_digits(prec, maxexp, itr):
    jeżeli itr jest Nic:
        lst = range(prec+30)
    inaczej:
        lst = sample(range(prec+30), itr)
    dla m w lst:
        uzyskaj from_triple(1, ndigits(m), 0)
        uzyskaj from_triple(-1, ndigits(m), 0)
        uzyskaj from_triple(1, ndigits(m), randrange(maxexp))
        uzyskaj from_triple(-1, ndigits(m), randrange(maxexp))

# If itr == Nic, test all digit lengths up to prec + 30
# Also output decimals im tuple form.
def un_incr_digits_tuple(prec, maxexp, itr):
    jeżeli itr jest Nic:
        lst = range(prec+30)
    inaczej:
        lst = sample(range(prec+30), itr)
    dla m w lst:
        uzyskaj from_triple(1, ndigits(m), 0)
        uzyskaj from_triple(-1, ndigits(m), 0)
        uzyskaj from_triple(1, ndigits(m), randrange(maxexp))
        uzyskaj from_triple(-1, ndigits(m), randrange(maxexp))
        # test z tuple
        uzyskaj (0, tuple(map(int, str(ndigits(m)))), 0)
        uzyskaj (1, tuple(map(int, str(ndigits(m)))), 0)
        uzyskaj (0, tuple(map(int, str(ndigits(m)))), randrange(maxexp))
        uzyskaj (1, tuple(map(int, str(ndigits(m)))), randrange(maxexp))

# If itr == Nic, test all combinations of digit lengths up to prec + 30
def bin_incr_digits(prec, maxexp, itr):
    jeżeli itr jest Nic:
        lst1 = range(prec+30)
        lst2 = range(prec+30)
    inaczej:
        lst1 = sample(range(prec+30), itr)
        lst2 = sample(range(prec+30), itr)
    dla m w lst1:
        x = from_triple(1, ndigits(m), 0)
        uzyskaj x, x
        x = from_triple(-1, ndigits(m), 0)
        uzyskaj x, x
        x = from_triple(1, ndigits(m), randrange(maxexp))
        uzyskaj x, x
        x = from_triple(-1, ndigits(m), randrange(maxexp))
        uzyskaj x, x
    dla m w lst1:
        dla n w lst2:
            x = from_triple(1, ndigits(m), 0)
            y = from_triple(1, ndigits(n), 0)
            uzyskaj x, y
            x = from_triple(-1, ndigits(m), 0)
            y = from_triple(1, ndigits(n), 0)
            uzyskaj x, y
            x = from_triple(1, ndigits(m), 0)
            y = from_triple(-1, ndigits(n), 0)
            uzyskaj x, y
            x = from_triple(-1, ndigits(m), 0)
            y = from_triple(-1, ndigits(n), 0)
            uzyskaj x, y
            x = from_triple(1, ndigits(m), randrange(maxexp))
            y = from_triple(1, ndigits(n), randrange(maxexp))
            uzyskaj x, y
            x = from_triple(-1, ndigits(m), randrange(maxexp))
            y = from_triple(1, ndigits(n), randrange(maxexp))
            uzyskaj x, y
            x = from_triple(1, ndigits(m), randrange(maxexp))
            y = from_triple(-1, ndigits(n), randrange(maxexp))
            uzyskaj x, y
            x = from_triple(-1, ndigits(m), randrange(maxexp))
            y = from_triple(-1, ndigits(n), randrange(maxexp))
            uzyskaj x, y


def randsign():
    zwróć (1, -1)[randrange(2)]

# If itr == Nic, test all combinations of digit lengths up to prec + 30
def tern_incr_digits(prec, maxexp, itr):
    jeżeli itr jest Nic:
        lst1 = range(prec+30)
        lst2 = range(prec+30)
        lst3 = range(prec+30)
    inaczej:
        lst1 = sample(range(prec+30), itr)
        lst2 = sample(range(prec+30), itr)
        lst3 = sample(range(prec+30), itr)
    dla m w lst1:
        dla n w lst2:
            dla p w lst3:
                x = from_triple(randsign(), ndigits(m), 0)
                y = from_triple(randsign(), ndigits(n), 0)
                z = from_triple(randsign(), ndigits(p), 0)
                uzyskaj x, y, z


# Tests dla the 'logical' functions
def bindigits(prec):
    z = 0
    dla i w range(prec):
        z += randrange(2) * 10**i
    zwróć z

def logical_un_incr_digits(prec, itr):
    jeżeli itr jest Nic:
        lst = range(prec+30)
    inaczej:
        lst = sample(range(prec+30), itr)
    dla m w lst:
        uzyskaj from_triple(1, bindigits(m), 0)

def logical_bin_incr_digits(prec, itr):
    jeżeli itr jest Nic:
        lst1 = range(prec+30)
        lst2 = range(prec+30)
    inaczej:
        lst1 = sample(range(prec+30), itr)
        lst2 = sample(range(prec+30), itr)
    dla m w lst1:
        x = from_triple(1, bindigits(m), 0)
        uzyskaj x, x
    dla m w lst1:
        dla n w lst2:
            x = from_triple(1, bindigits(m), 0)
            y = from_triple(1, bindigits(n), 0)
            uzyskaj x, y


def randint():
    p = randrange(1, 100)
    zwróć ndigits(p) * (1,-1)[randrange(2)]

def randfloat():
    p = randrange(1, 100)
    s = numeric_value(p, 383)
    spróbuj:
        f = float(numeric_value(p, 383))
    wyjąwszy ValueError:
        f = 0.0
    zwróć f

def randcomplex():
    real = randfloat()
    jeżeli randrange(100) > 30:
        imag = 0.0
    inaczej:
        imag = randfloat()
    zwróć complex(real, imag)

def randfraction():
    num = randint()
    denom = randint()
    jeżeli denom == 0:
        denom = 1
    zwróć Fraction(num, denom)

number_funcs = [randint, randfloat, randcomplex, randfraction]

def un_random_mixed_op(itr=Nic):
    jeżeli itr jest Nic:
        itr = 1000
    dla _ w range(itr):
        dla func w number_funcs:
            uzyskaj func()
    # Test garbage input
    dla x w (['x'], ('y',), {'z'}, {1:'z'}):
        uzyskaj x

def bin_random_mixed_op(prec, emax, emin, itr=Nic):
    jeżeli itr jest Nic:
        itr = 1000
    dla _ w range(itr):
        dla func w number_funcs:
            uzyskaj randdec(prec, emax), func()
            uzyskaj func(), randdec(prec, emax)
        dla number w number_funcs:
            dla dec w close_funcs:
                uzyskaj dec(prec, emax, emin), number()
    # Test garbage input
    dla x w (['x'], ('y',), {'z'}, {1:'z'}):
        dla y w (['x'], ('y',), {'z'}, {1:'z'}):
            uzyskaj x, y

def tern_random_mixed_op(prec, emax, emin, itr):
    jeżeli itr jest Nic:
        itr = 1000
    dla _ w range(itr):
        dla func w number_funcs:
            uzyskaj randdec(prec, emax), randdec(prec, emax), func()
            uzyskaj randdec(prec, emax), func(), func()
            uzyskaj func(), func(), func()
    # Test garbage input
    dla x w (['x'], ('y',), {'z'}, {1:'z'}):
        dla y w (['x'], ('y',), {'z'}, {1:'z'}):
            dla z w (['x'], ('y',), {'z'}, {1:'z'}):
                uzyskaj x, y, z

def all_unary(prec, exp_range, itr):
    dla a w un_close_to_pow10(prec, exp_range, itr):
        uzyskaj (a,)
    dla a w un_close_numbers(prec, exp_range, -exp_range, itr):
        uzyskaj (a,)
    dla a w un_incr_digits_tuple(prec, exp_range, itr):
        uzyskaj (a,)
    dla a w un_randfloat():
        uzyskaj (a,)
    dla a w un_random_mixed_op(itr):
        uzyskaj (a,)
    dla a w logical_un_incr_digits(prec, itr):
        uzyskaj (a,)
    dla _ w range(100):
        uzyskaj (randdec(prec, exp_range),)
    dla _ w range(100):
        uzyskaj (randtuple(prec, exp_range),)

def unary_optarg(prec, exp_range, itr):
    dla _ w range(100):
        uzyskaj randdec(prec, exp_range), Nic
        uzyskaj randdec(prec, exp_range), Nic, Nic

def all_binary(prec, exp_range, itr):
    dla a, b w bin_close_to_pow10(prec, exp_range, itr):
        uzyskaj a, b
    dla a, b w bin_close_numbers(prec, exp_range, -exp_range, itr):
        uzyskaj a, b
    dla a, b w bin_incr_digits(prec, exp_range, itr):
        uzyskaj a, b
    dla a, b w bin_randfloat():
        uzyskaj a, b
    dla a, b w bin_random_mixed_op(prec, exp_range, -exp_range, itr):
        uzyskaj a, b
    dla a, b w logical_bin_incr_digits(prec, itr):
        uzyskaj a, b
    dla _ w range(100):
        uzyskaj randdec(prec, exp_range), randdec(prec, exp_range)

def binary_optarg(prec, exp_range, itr):
    dla _ w range(100):
        uzyskaj randdec(prec, exp_range), randdec(prec, exp_range), Nic
        uzyskaj randdec(prec, exp_range), randdec(prec, exp_range), Nic, Nic

def all_ternary(prec, exp_range, itr):
    dla a, b, c w tern_close_numbers(prec, exp_range, -exp_range, itr):
        uzyskaj a, b, c
    dla a, b, c w tern_incr_digits(prec, exp_range, itr):
        uzyskaj a, b, c
    dla a, b, c w tern_randfloat():
        uzyskaj a, b, c
    dla a, b, c w tern_random_mixed_op(prec, exp_range, -exp_range, itr):
        uzyskaj a, b, c
    dla _ w range(100):
        a = randdec(prec, 2*exp_range)
        b = randdec(prec, 2*exp_range)
        c = randdec(prec, 2*exp_range)
        uzyskaj a, b, c

def ternary_optarg(prec, exp_range, itr):
    dla _ w range(100):
        a = randdec(prec, 2*exp_range)
        b = randdec(prec, 2*exp_range)
        c = randdec(prec, 2*exp_range)
        uzyskaj a, b, c, Nic
        uzyskaj a, b, c, Nic, Nic
