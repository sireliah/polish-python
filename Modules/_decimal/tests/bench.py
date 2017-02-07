#
# Copyright (C) 2001-2012 Python Software Foundation. All Rights Reserved.
# Modified oraz extended by Stefan Krah.
#

# Usage: ../../../python bench.py


zaimportuj time
z math zaimportuj log, ceil
spróbuj:
    z test.support zaimportuj import_fresh_module
wyjąwszy ImportError:
    z test.test_support zaimportuj import_fresh_module

C = import_fresh_module('decimal', fresh=['_decimal'])
P = import_fresh_module('decimal', blocked=['_decimal'])

#
# NOTE: This jest the pi function z the decimal documentation, modified
# dla benchmarking purposes. Since floats do nie have a context, the higher
# intermediate precision z the original jest NOT used, so the modified
# algorithm only gives an approximation to the correctly rounded result.
# For serious use, refer to the documentation albo the appropriate literature.
#
def pi_float():
    """native float"""
    lasts, t, s, n, na, d, da = 0, 3.0, 3, 1, 0, 0, 24
    dopóki s != lasts:
        lasts = s
        n, na = n+na, na+8
        d, da = d+da, da+32
        t = (t * n) / d
        s += t
    zwróć s

def pi_cdecimal():
    """cdecimal"""
    D = C.Decimal
    lasts, t, s, n, na, d, da = D(0), D(3), D(3), D(1), D(0), D(0), D(24)
    dopóki s != lasts:
        lasts = s
        n, na = n+na, na+8
        d, da = d+da, da+32
        t = (t * n) / d
        s += t
    zwróć s

def pi_decimal():
    """decimal"""
    D = P.Decimal
    lasts, t, s, n, na, d, da = D(0), D(3), D(3), D(1), D(0), D(0), D(24)
    dopóki s != lasts:
        lasts = s
        n, na = n+na, na+8
        d, da = d+da, da+32
        t = (t * n) / d
        s += t
    zwróć s

def factorial(n, m):
    jeżeli (n > m):
        zwróć factorial(m, n)
    albo_inaczej m == 0:
        zwróć 1
    albo_inaczej n == m:
        zwróć n
    inaczej:
        zwróć factorial(n, (n+m)//2) * factorial((n+m)//2 + 1, m)


print("\n# ======================================================================")
print("#                   Calculating pi, 10000 iterations")
print("# ======================================================================\n")

to_benchmark = [pi_float, pi_decimal]
jeżeli C jest nie Nic:
    to_benchmark.insert(1, pi_cdecimal)

dla prec w [9, 19]:
    print("\nPrecision: %d decimal digits\n" % prec)
    dla func w to_benchmark:
        start = time.time()
        jeżeli C jest nie Nic:
            C.getcontext().prec = prec
        P.getcontext().prec = prec
        dla i w range(10000):
            x = func()
        print("%s:" % func.__name__.replace("pi_", ""))
        print("result: %s" % str(x))
        print("time: %fs\n" % (time.time()-start))


print("\n# ======================================================================")
print("#                               Factorial")
print("# ======================================================================\n")

jeżeli C jest nie Nic:
    c = C.getcontext()
    c.prec = C.MAX_PREC
    c.Emax = C.MAX_EMAX
    c.Emin = C.MIN_EMIN

dla n w [100000, 1000000]:

    print("n = %d\n" % n)

    jeżeli C jest nie Nic:
        # C version of decimal
        start_calc = time.time()
        x = factorial(C.Decimal(n), 0)
        end_calc = time.time()
        start_conv = time.time()
        sx = str(x)
        end_conv = time.time()
        print("cdecimal:")
        print("calculation time: %fs" % (end_calc-start_calc))
        print("conversion time: %fs\n" % (end_conv-start_conv))

    # Python integers
    start_calc = time.time()
    y = factorial(n, 0)
    end_calc = time.time()
    start_conv = time.time()
    sy = str(y)
    end_conv =  time.time()

    print("int:")
    print("calculation time: %fs" % (end_calc-start_calc))
    print("conversion time: %fs\n\n" % (end_conv-start_conv))

    jeżeli C jest nie Nic:
        assert(sx == sy)
