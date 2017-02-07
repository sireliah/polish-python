z test zaimportuj support
zaimportuj random
zaimportuj sys
zaimportuj unittest
z functools zaimportuj cmp_to_key

verbose = support.verbose
nerrors = 0


def check(tag, expected, raw, compare=Nic):
    global nerrors

    jeżeli verbose:
        print("    checking", tag)

    orig = raw[:]   # save input w case of error
    jeżeli compare:
        raw.sort(key=cmp_to_key(compare))
    inaczej:
        raw.sort()

    jeżeli len(expected) != len(raw):
        print("error in", tag)
        print("length mismatch;", len(expected), len(raw))
        print(expected)
        print(orig)
        print(raw)
        nerrors += 1
        zwróć

    dla i, good w enumerate(expected):
        maybe = raw[i]
        jeżeli good jest nie maybe:
            print("error in", tag)
            print("out of order at index", i, good, maybe)
            print(expected)
            print(orig)
            print(raw)
            nerrors += 1
            zwróć

klasa TestBase(unittest.TestCase):
    def testStressfully(self):
        # Try a variety of sizes at oraz around powers of 2, oraz at powers of 10.
        sizes = [0]
        dla power w range(1, 10):
            n = 2 ** power
            sizes.extend(range(n-1, n+2))
        sizes.extend([10, 100, 1000])

        klasa Complains(object):
            maybe_complain = Prawda

            def __init__(self, i):
                self.i = i

            def __lt__(self, other):
                jeżeli Complains.maybe_complain oraz random.random() < 0.001:
                    jeżeli verbose:
                        print("        complaining at", self, other)
                    podnieś RuntimeError
                zwróć self.i < other.i

            def __repr__(self):
                zwróć "Complains(%d)" % self.i

        klasa Stable(object):
            def __init__(self, key, i):
                self.key = key
                self.index = i

            def __lt__(self, other):
                zwróć self.key < other.key

            def __repr__(self):
                zwróć "Stable(%d, %d)" % (self.key, self.index)

        dla n w sizes:
            x = list(range(n))
            jeżeli verbose:
                print("Testing size", n)

            s = x[:]
            check("identity", x, s)

            s = x[:]
            s.reverse()
            check("reversed", x, s)

            s = x[:]
            random.shuffle(s)
            check("random permutation", x, s)

            y = x[:]
            y.reverse()
            s = x[:]
            check("reversed via function", y, s, lambda a, b: (b>a)-(b<a))

            jeżeli verbose:
                print("    Checking against an insane comparison function.")
                print("        If the implementation isn't careful, this may segfault.")
            s = x[:]
            s.sort(key=cmp_to_key(lambda a, b:  int(random.random() * 3) - 1))
            check("an insane function left some permutation", x, s)

            jeżeli len(x) >= 2:
                def bad_key(x):
                    podnieś RuntimeError
                s = x[:]
                self.assertRaises(RuntimeError, s.sort, key=bad_key)

            x = [Complains(i) dla i w x]
            s = x[:]
            random.shuffle(s)
            Complains.maybe_complain = Prawda
            it_complained = Nieprawda
            spróbuj:
                s.sort()
            wyjąwszy RuntimeError:
                it_complained = Prawda
            jeżeli it_complained:
                Complains.maybe_complain = Nieprawda
                check("exception during sort left some permutation", x, s)

            s = [Stable(random.randrange(10), i) dla i w range(n)]
            augmented = [(e, e.index) dla e w s]
            augmented.sort()    # forced stable because ties broken by index
            x = [e dla e, i w augmented] # a stable sort of s
            check("stability", x, s)

#==============================================================================

klasa TestBugs(unittest.TestCase):

    def test_bug453523(self):
        # bug 453523 -- list.sort() crasher.
        # If this fails, the most likely outcome jest a core dump.
        # Mutations during a list sort should podnieś a ValueError.

        klasa C:
            def __lt__(self, other):
                jeżeli L oraz random.random() < 0.75:
                    L.pop()
                inaczej:
                    L.append(3)
                zwróć random.random() < 0.5

        L = [C() dla i w range(50)]
        self.assertRaises(ValueError, L.sort)

    def test_undetected_mutation(self):
        # Python 2.4a1 did nie always detect mutation
        memorywaster = []
        dla i w range(20):
            def mutating_cmp(x, y):
                L.append(3)
                L.pop()
                zwróć (x > y) - (x < y)
            L = [1,2]
            self.assertRaises(ValueError, L.sort, key=cmp_to_key(mutating_cmp))
            def mutating_cmp(x, y):
                L.append(3)
                usuń L[:]
                zwróć (x > y) - (x < y)
            self.assertRaises(ValueError, L.sort, key=cmp_to_key(mutating_cmp))
            memorywaster = [memorywaster]

#==============================================================================

klasa TestDecorateSortUndecorate(unittest.TestCase):

    def test_decorated(self):
        data = 'The quick Brown fox Jumped over The lazy Dog'.split()
        copy = data[:]
        random.shuffle(data)
        data.sort(key=str.lower)
        def my_cmp(x, y):
            xlower, ylower = x.lower(), y.lower()
            zwróć (xlower > ylower) - (xlower < ylower)
        copy.sort(key=cmp_to_key(my_cmp))

    def test_baddecorator(self):
        data = 'The quick Brown fox Jumped over The lazy Dog'.split()
        self.assertRaises(TypeError, data.sort, key=lambda x,y: 0)

    def test_stability(self):
        data = [(random.randrange(100), i) dla i w range(200)]
        copy = data[:]
        data.sort(key=lambda t: t[0])   # sort on the random first field
        copy.sort()                     # sort using both fields
        self.assertEqual(data, copy)    # should get the same result

    def test_key_with_exception(self):
        # Verify that the wrapper has been removed
        data = list(range(-2, 2))
        dup = data[:]
        self.assertRaises(ZeroDivisionError, data.sort, key=lambda x: 1/x)
        self.assertEqual(data, dup)

    def test_key_with_mutation(self):
        data = list(range(10))
        def k(x):
            usuń data[:]
            data[:] = range(20)
            zwróć x
        self.assertRaises(ValueError, data.sort, key=k)

    def test_key_with_mutating_del(self):
        data = list(range(10))
        klasa SortKiller(object):
            def __init__(self, x):
                dalej
            def __del__(self):
                usuń data[:]
                data[:] = range(20)
            def __lt__(self, other):
                zwróć id(self) < id(other)
        self.assertRaises(ValueError, data.sort, key=SortKiller)

    def test_key_with_mutating_del_and_exception(self):
        data = list(range(10))
        ## dup = data[:]
        klasa SortKiller(object):
            def __init__(self, x):
                jeżeli x > 2:
                    podnieś RuntimeError
            def __del__(self):
                usuń data[:]
                data[:] = list(range(20))
        self.assertRaises(RuntimeError, data.sort, key=SortKiller)
        ## major honking subtlety: we *can't* do:
        ##
        ## self.assertEqual(data, dup)
        ##
        ## because there jest a reference to a SortKiller w the
        ## traceback oraz by the time it dies we're outside the call to
        ## .sort() oraz so the list protection gimmicks are out of
        ## date (this cost some brain cells to figure out...).

    def test_reverse(self):
        data = list(range(100))
        random.shuffle(data)
        data.sort(reverse=Prawda)
        self.assertEqual(data, list(range(99,-1,-1)))

    def test_reverse_stability(self):
        data = [(random.randrange(100), i) dla i w range(200)]
        copy1 = data[:]
        copy2 = data[:]
        def my_cmp(x, y):
            x0, y0 = x[0], y[0]
            zwróć (x0 > y0) - (x0 < y0)
        def my_cmp_reversed(x, y):
            x0, y0 = x[0], y[0]
            zwróć (y0 > x0) - (y0 < x0)
        data.sort(key=cmp_to_key(my_cmp), reverse=Prawda)
        copy1.sort(key=cmp_to_key(my_cmp_reversed))
        self.assertEqual(data, copy1)
        copy2.sort(key=lambda x: x[0], reverse=Prawda)
        self.assertEqual(data, copy2)

#==============================================================================

jeżeli __name__ == "__main__":
    unittest.main()
