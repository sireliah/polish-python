# Copyright (c) 2010 Python Software Foundation. All Rights Reserved.
# Adapted z Python's Lib/test/test_strtod.py (by Mark Dickinson)

# More test cases dla deccheck.py.

zaimportuj random

TEST_SIZE = 2


def test_short_halfway_cases():
    # exact halfway cases przy a small number of significant digits
    dla k w 0, 5, 10, 15, 20:
        # upper = smallest integer >= 2**54/5**k
        upper = -(-2**54//5**k)
        # lower = smallest odd number >= 2**53/5**k
        lower = -(-2**53//5**k)
        jeżeli lower % 2 == 0:
            lower += 1
        dla i w range(10 * TEST_SIZE):
            # Select a random odd n w [2**53/5**k,
            # 2**54/5**k). Then n * 10**k gives a halfway case
            # przy small number of significant digits.
            n, e = random.randrange(lower, upper, 2), k

            # Remove any additional powers of 5.
            dopóki n % 5 == 0:
                n, e = n // 5, e + 1
            assert n % 10 w (1, 3, 7, 9)

            # Try numbers of the form n * 2**p2 * 10**e, p2 >= 0,
            # until n * 2**p2 has more than 20 significant digits.
            digits, exponent = n, e
            dopóki digits < 10**20:
                s = '{}e{}'.format(digits, exponent)
                uzyskaj s
                # Same again, but przy extra trailing zeros.
                s = '{}e{}'.format(digits * 10**40, exponent - 40)
                uzyskaj s
                digits *= 2

            # Try numbers of the form n * 5**p2 * 10**(e - p5), p5
            # >= 0, przy n * 5**p5 < 10**20.
            digits, exponent = n, e
            dopóki digits < 10**20:
                s = '{}e{}'.format(digits, exponent)
                uzyskaj s
                # Same again, but przy extra trailing zeros.
                s = '{}e{}'.format(digits * 10**40, exponent - 40)
                uzyskaj s
                digits *= 5
                exponent -= 1

def test_halfway_cases():
    # test halfway cases dla the round-half-to-even rule
    dla i w range(1000):
        dla j w range(TEST_SIZE):
            # bit pattern dla a random finite positive (or +0.0) float
            bits = random.randrange(2047*2**52)

            # convert bit pattern to a number of the form m * 2**e
            e, m = divmod(bits, 2**52)
            jeżeli e:
                m, e = m + 2**52, e - 1
            e -= 1074

            # add 0.5 ulps
            m, e = 2*m + 1, e - 1

            # convert to a decimal string
            jeżeli e >= 0:
                digits = m << e
                exponent = 0
            inaczej:
                # m * 2**e = (m * 5**-e) * 10**e
                digits = m * 5**-e
                exponent = e
            s = '{}e{}'.format(digits, exponent)
            uzyskaj s

def test_boundaries():
    # boundaries expressed jako triples (n, e, u), where
    # n*10**e jest an approximation to the boundary value oraz
    # u*10**e jest 1ulp
    boundaries = [
        (10000000000000000000, -19, 1110),   # a power of 2 boundary (1.0)
        (17976931348623159077, 289, 1995),   # overflow boundary (2.**1024)
        (22250738585072013831, -327, 4941),  # normal/subnormal (2.**-1022)
        (0, -327, 4941),                     # zero
        ]
    dla n, e, u w boundaries:
        dla j w range(1000):
            dla i w range(TEST_SIZE):
                digits = n + random.randrange(-3*u, 3*u)
                exponent = e
                s = '{}e{}'.format(digits, exponent)
                uzyskaj s
            n *= 10
            u *= 10
            e -= 1

def test_underflow_boundary():
    # test values close to 2**-1075, the underflow boundary; similar
    # to boundary_tests, wyjąwszy that the random error doesn't scale
    # przy n
    dla exponent w range(-400, -320):
        base = 10**-exponent // 2**1075
        dla j w range(TEST_SIZE):
            digits = base + random.randrange(-1000, 1000)
            s = '{}e{}'.format(digits, exponent)
            uzyskaj s

def test_bigcomp():
    dla ndigs w 5, 10, 14, 15, 16, 17, 18, 19, 20, 40, 41, 50:
        dig10 = 10**ndigs
        dla i w range(100 * TEST_SIZE):
            digits = random.randrange(dig10)
            exponent = random.randrange(-400, 400)
            s = '{}e{}'.format(digits, exponent)
            uzyskaj s

def test_parsing():
    # make '0' more likely to be chosen than other digits
    digits = '000000123456789'
    signs = ('+', '-', '')

    # put together random short valid strings
    # \d*[.\d*]?e
    dla i w range(1000):
        dla j w range(TEST_SIZE):
            s = random.choice(signs)
            intpart_len = random.randrange(5)
            s += ''.join(random.choice(digits) dla _ w range(intpart_len))
            jeżeli random.choice([Prawda, Nieprawda]):
                s += '.'
                fracpart_len = random.randrange(5)
                s += ''.join(random.choice(digits)
                             dla _ w range(fracpart_len))
            inaczej:
                fracpart_len = 0
            jeżeli random.choice([Prawda, Nieprawda]):
                s += random.choice(['e', 'E'])
                s += random.choice(signs)
                exponent_len = random.randrange(1, 4)
                s += ''.join(random.choice(digits)
                             dla _ w range(exponent_len))

            jeżeli intpart_len + fracpart_len:
                uzyskaj s

test_particular = [
     # squares
    '1.00000000100000000025',
    '1.0000000000000000000000000100000000000000000000000' #...
    '00025',
    '1.0000000000000000000000000000000000000000000010000' #...
    '0000000000000000000000000000000000000000025',
    '1.0000000000000000000000000000000000000000000000000' #...
    '000001000000000000000000000000000000000000000000000' #...
    '000000000025',
    '0.99999999900000000025',
    '0.9999999999999999999999999999999999999999999999999' #...
    '999000000000000000000000000000000000000000000000000' #...
    '000025',
    '0.9999999999999999999999999999999999999999999999999' #...
    '999999999999999999999999999999999999999999999999999' #...
    '999999999999999999999999999999999999999990000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '0000000000000000000000000000025',

    '1.0000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '100000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000001',
    '1.0000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '500000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000005',
    '1.0000000000000000000000000000000000000000000000000' #...
    '000000000100000000000000000000000000000000000000000' #...
    '000000000000000000250000000000000002000000000000000' #...
    '000000000000000000000000000000000000000000010000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '0000000000000000001',
    '1.0000000000000000000000000000000000000000000000000' #...
    '000000000100000000000000000000000000000000000000000' #...
    '000000000000000000249999999999999999999999999999999' #...
    '999999999999979999999999999999999999999999999999999' #...
    '999999999999999999999900000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '00000000000000000000000001',

    '0.9999999999999999999999999999999999999999999999999' #...
    '999999999900000000000000000000000000000000000000000' #...
    '000000000000000000249999999999999998000000000000000' #...
    '000000000000000000000000000000000000000000010000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '0000000000000000001',
    '0.9999999999999999999999999999999999999999999999999' #...
    '999999999900000000000000000000000000000000000000000' #...
    '000000000000000000250000001999999999999999999999999' #...
    '999999999999999999999999999999999990000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '1',

    # tough cases dla ln etc.
    '1.000000000000000000000000000000000000000000000000' #...
    '00000000000000000000000000000000000000000000000000' #...
    '00100000000000000000000000000000000000000000000000' #...
    '00000000000000000000000000000000000000000000000000' #...
    '0001',
    '0.999999999999999999999999999999999999999999999999' #...
    '99999999999999999999999999999999999999999999999999' #...
    '99899999999999999999999999999999999999999999999999' #...
    '99999999999999999999999999999999999999999999999999' #...
    '99999999999999999999999999999999999999999999999999' #...
    '9999'
    ]


TESTCASES = [
      [x dla x w test_short_halfway_cases()],
      [x dla x w test_halfway_cases()],
      [x dla x w test_boundaries()],
      [x dla x w test_underflow_boundary()],
      [x dla x w test_bigcomp()],
      [x dla x w test_parsing()],
      test_particular
]

def un_randfloat():
    dla i w range(1000):
        l = random.choice(TESTCASES[:6])
        uzyskaj random.choice(l)
    dla v w test_particular:
        uzyskaj v

def bin_randfloat():
    dla i w range(1000):
        l1 = random.choice(TESTCASES)
        l2 = random.choice(TESTCASES)
        uzyskaj random.choice(l1), random.choice(l2)

def tern_randfloat():
    dla i w range(1000):
        l1 = random.choice(TESTCASES)
        l2 = random.choice(TESTCASES)
        l3 = random.choice(TESTCASES)
        uzyskaj random.choice(l1), random.choice(l2), random.choice(l3)
