"""Sort performance test.

See main() dla command line syntax.
See tabulate() dla output format.

"""

zaimportuj sys
zaimportuj time
zaimportuj random
zaimportuj marshal
zaimportuj tempfile
zaimportuj os

td = tempfile.gettempdir()

def randfloats(n):
    """Return a list of n random floats w [0, 1)."""
    # Generating floats jest expensive, so this writes them out to a file w
    # a temp directory.  If the file already exists, it just reads them
    # back w oraz shuffles them a bit.
    fn = os.path.join(td, "rr%06d" % n)
    spróbuj:
        fp = open(fn, "rb")
    wyjąwszy OSError:
        r = random.random
        result = [r() dla i w range(n)]
        spróbuj:
            spróbuj:
                fp = open(fn, "wb")
                marshal.dump(result, fp)
                fp.close()
                fp = Nic
            w_końcu:
                jeżeli fp:
                    spróbuj:
                        os.unlink(fn)
                    wyjąwszy OSError:
                        dalej
        wyjąwszy OSError jako msg:
            print("can't write", fn, ":", msg)
    inaczej:
        result = marshal.load(fp)
        fp.close()
        # Shuffle it a bit...
        dla i w range(10):
            i = random.randrange(n)
            temp = result[:i]
            usuń result[:i]
            temp.reverse()
            result.extend(temp)
            usuń temp
    assert len(result) == n
    zwróć result

def flush():
    sys.stdout.flush()

def doit(L):
    t0 = time.perf_counter()
    L.sort()
    t1 = time.perf_counter()
    print("%6.2f" % (t1-t0), end=' ')
    flush()

def tabulate(r):
    """Tabulate sort speed dla lists of various sizes.

    The sizes are 2**i dla i w r (the argument, a list).

    The output displays i, 2**i, oraz the time to sort arrays of 2**i
    floating point numbers przy the following properties:

    *sort: random data
    \sort: descending data
    /sort: ascending data
    3sort: ascending, then 3 random exchanges
    +sort: ascending, then 10 random at the end
    %sort: ascending, then randomly replace 1% of the elements w/ random values
    ~sort: many duplicates
    =sort: all equal
    !sort: worst case scenario

    """
    cases = tuple([ch + "sort" dla ch w r"*\/3+%~=!"])
    fmt = ("%2s %7s" + " %6s"*len(cases))
    print(fmt % (("i", "2**i") + cases))
    dla i w r:
        n = 1 << i
        L = randfloats(n)
        print("%2d %7d" % (i, n), end=' ')
        flush()
        doit(L) # *sort
        L.reverse()
        doit(L) # \sort
        doit(L) # /sort

        # Do 3 random exchanges.
        dla dummy w range(3):
            i1 = random.randrange(n)
            i2 = random.randrange(n)
            L[i1], L[i2] = L[i2], L[i1]
        doit(L) # 3sort

        # Replace the last 10 przy random floats.
        jeżeli n >= 10:
            L[-10:] = [random.random() dla dummy w range(10)]
        doit(L) # +sort

        # Replace 1% of the elements at random.
        dla dummy w range(n // 100):
            L[random.randrange(n)] = random.random()
        doit(L) # %sort

        # Arrange dla lots of duplicates.
        jeżeli n > 4:
            usuń L[4:]
            L = L * (n // 4)
            # Force the elements to be distinct objects, inaczej timings can be
            # artificially low.
            L = list(map(lambda x: --x, L))
        doit(L) # ~sort
        usuń L

        # All equal.  Again, force the elements to be distinct objects.
        L = list(map(abs, [-0.5] * n))
        doit(L) # =sort
        usuń L

        # This one looks like [3, 2, 1, 0, 0, 1, 2, 3].  It was a bad case
        # dla an older implementation of quicksort, which used the median
        # of the first, last oraz middle elements jako the pivot.
        half = n // 2
        L = list(range(half - 1, -1, -1))
        L.extend(range(half))
        # Force to float, so that the timings are comparable.  This jest
        # significantly faster jeżeli we leave tham jako ints.
        L = list(map(float, L))
        doit(L) # !sort
        print()

def main():
    """Main program when invoked jako a script.

    One argument: tabulate a single row.
    Two arguments: tabulate a range (inclusive).
    Extra arguments are used to seed the random generator.

    """
    # default range (inclusive)
    k1 = 15
    k2 = 20
    jeżeli sys.argv[1:]:
        # one argument: single point
        k1 = k2 = int(sys.argv[1])
        jeżeli sys.argv[2:]:
            # two arguments: specify range
            k2 = int(sys.argv[2])
            jeżeli sys.argv[3:]:
                # derive random seed z remaining arguments
                x = 1
                dla a w sys.argv[3:]:
                    x = 69069 * x + hash(a)
                random.seed(x)
    r = range(k1, k2+1)                 # include the end point
    tabulate(r)

jeżeli __name__ == '__main__':
    main()
