# Test iterators.

zaimportuj sys
zaimportuj unittest
z test.support zaimportuj run_unittest, TESTFN, unlink, cpython_only
zaimportuj pickle
zaimportuj collections.abc

# Test result of triple loop (too big to inline)
TRIPLETS = [(0, 0, 0), (0, 0, 1), (0, 0, 2),
            (0, 1, 0), (0, 1, 1), (0, 1, 2),
            (0, 2, 0), (0, 2, 1), (0, 2, 2),

            (1, 0, 0), (1, 0, 1), (1, 0, 2),
            (1, 1, 0), (1, 1, 1), (1, 1, 2),
            (1, 2, 0), (1, 2, 1), (1, 2, 2),

            (2, 0, 0), (2, 0, 1), (2, 0, 2),
            (2, 1, 0), (2, 1, 1), (2, 1, 2),
            (2, 2, 0), (2, 2, 1), (2, 2, 2)]

# Helper classes

klasa BasicIterClass:
    def __init__(self, n):
        self.n = n
        self.i = 0
    def __next__(self):
        res = self.i
        jeżeli res >= self.n:
            podnieś StopIteration
        self.i = res + 1
        zwróć res
    def __iter__(self):
        zwróć self

klasa IteratingSequenceClass:
    def __init__(self, n):
        self.n = n
    def __iter__(self):
        zwróć BasicIterClass(self.n)

klasa SequenceClass:
    def __init__(self, n):
        self.n = n
    def __getitem__(self, i):
        jeżeli 0 <= i < self.n:
            zwróć i
        inaczej:
            podnieś IndexError

klasa UnlimitedSequenceClass:
    def __getitem__(self, i):
        zwróć i

# Main test suite

klasa TestCase(unittest.TestCase):

    # Helper to check that an iterator returns a given sequence
    def check_iterator(self, it, seq, pickle=Prawda):
        jeżeli pickle:
            self.check_pickle(it, seq)
        res = []
        dopóki 1:
            spróbuj:
                val = next(it)
            wyjąwszy StopIteration:
                przerwij
            res.append(val)
        self.assertEqual(res, seq)

    # Helper to check that a dla loop generates a given sequence
    def check_for_loop(self, expr, seq, pickle=Prawda):
        jeżeli pickle:
            self.check_pickle(iter(expr), seq)
        res = []
        dla val w expr:
            res.append(val)
        self.assertEqual(res, seq)

    # Helper to check picklability
    def check_pickle(self, itorg, seq):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            # Cannot assert type equality because dict iterators unpickle jako list
            # iterators.
            # self.assertEqual(type(itorg), type(it))
            self.assertPrawda(isinstance(it, collections.abc.Iterator))
            self.assertEqual(list(it), seq)

            it = pickle.loads(d)
            spróbuj:
                next(it)
            wyjąwszy StopIteration:
                kontynuuj
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(list(it), seq[1:])

    # Test basic use of iter() function
    def test_iter_basic(self):
        self.check_iterator(iter(range(10)), list(range(10)))

    # Test that iter(iter(x)) jest the same jako iter(x)
    def test_iter_idempotency(self):
        seq = list(range(10))
        it = iter(seq)
        it2 = iter(it)
        self.assertPrawda(it jest it2)

    # Test that dla loops over iterators work
    def test_iter_for_loop(self):
        self.check_for_loop(iter(range(10)), list(range(10)))

    # Test several independent iterators over the same list
    def test_iter_independence(self):
        seq = range(3)
        res = []
        dla i w iter(seq):
            dla j w iter(seq):
                dla k w iter(seq):
                    res.append((i, j, k))
        self.assertEqual(res, TRIPLETS)

    # Test triple list comprehension using iterators
    def test_nested_comprehensions_iter(self):
        seq = range(3)
        res = [(i, j, k)
               dla i w iter(seq) dla j w iter(seq) dla k w iter(seq)]
        self.assertEqual(res, TRIPLETS)

    # Test triple list comprehension without iterators
    def test_nested_comprehensions_for(self):
        seq = range(3)
        res = [(i, j, k) dla i w seq dla j w seq dla k w seq]
        self.assertEqual(res, TRIPLETS)

    # Test a klasa przy __iter__ w a dla loop
    def test_iter_class_for(self):
        self.check_for_loop(IteratingSequenceClass(10), list(range(10)))

    # Test a klasa przy __iter__ przy explicit iter()
    def test_iter_class_iter(self):
        self.check_iterator(iter(IteratingSequenceClass(10)), list(range(10)))

    # Test dla loop on a sequence klasa without __iter__
    def test_seq_class_for(self):
        self.check_for_loop(SequenceClass(10), list(range(10)))

    # Test iter() on a sequence klasa without __iter__
    def test_seq_class_iter(self):
        self.check_iterator(iter(SequenceClass(10)), list(range(10)))

    # Test a new_style klasa przy __iter__ but no next() method
    def test_new_style_iter_class(self):
        klasa IterClass(object):
            def __iter__(self):
                zwróć self
        self.assertRaises(TypeError, iter, IterClass())

    # Test two-argument iter() przy callable instance
    def test_iter_callable(self):
        klasa C:
            def __init__(self):
                self.i = 0
            def __call__(self):
                i = self.i
                self.i = i + 1
                jeżeli i > 100:
                    podnieś IndexError # Emergency stop
                zwróć i
        self.check_iterator(iter(C(), 10), list(range(10)), pickle=Nieprawda)

    # Test two-argument iter() przy function
    def test_iter_function(self):
        def spam(state=[0]):
            i = state[0]
            state[0] = i+1
            zwróć i
        self.check_iterator(iter(spam, 10), list(range(10)), pickle=Nieprawda)

    # Test two-argument iter() przy function that podnieśs StopIteration
    def test_iter_function_stop(self):
        def spam(state=[0]):
            i = state[0]
            jeżeli i == 10:
                podnieś StopIteration
            state[0] = i+1
            zwróć i
        self.check_iterator(iter(spam, 20), list(range(10)), pickle=Nieprawda)

    # Test exception propagation through function iterator
    def test_exception_function(self):
        def spam(state=[0]):
            i = state[0]
            state[0] = i+1
            jeżeli i == 10:
                podnieś RuntimeError
            zwróć i
        res = []
        spróbuj:
            dla x w iter(spam, 20):
                res.append(x)
        wyjąwszy RuntimeError:
            self.assertEqual(res, list(range(10)))
        inaczej:
            self.fail("should have podnieśd RuntimeError")

    # Test exception propagation through sequence iterator
    def test_exception_sequence(self):
        klasa MySequenceClass(SequenceClass):
            def __getitem__(self, i):
                jeżeli i == 10:
                    podnieś RuntimeError
                zwróć SequenceClass.__getitem__(self, i)
        res = []
        spróbuj:
            dla x w MySequenceClass(20):
                res.append(x)
        wyjąwszy RuntimeError:
            self.assertEqual(res, list(range(10)))
        inaczej:
            self.fail("should have podnieśd RuntimeError")

    # Test dla StopIteration z __getitem__
    def test_stop_sequence(self):
        klasa MySequenceClass(SequenceClass):
            def __getitem__(self, i):
                jeżeli i == 10:
                    podnieś StopIteration
                zwróć SequenceClass.__getitem__(self, i)
        self.check_for_loop(MySequenceClass(20), list(range(10)), pickle=Nieprawda)

    # Test a big range
    def test_iter_big_range(self):
        self.check_for_loop(iter(range(10000)), list(range(10000)))

    # Test an empty list
    def test_iter_empty(self):
        self.check_for_loop(iter([]), [])

    # Test a tuple
    def test_iter_tuple(self):
        self.check_for_loop(iter((0,1,2,3,4,5,6,7,8,9)), list(range(10)))

    # Test a range
    def test_iter_range(self):
        self.check_for_loop(iter(range(10)), list(range(10)))

    # Test a string
    def test_iter_string(self):
        self.check_for_loop(iter("abcde"), ["a", "b", "c", "d", "e"])

    # Test a directory
    def test_iter_dict(self):
        dict = {}
        dla i w range(10):
            dict[i] = Nic
        self.check_for_loop(dict, list(dict.keys()))

    # Test a file
    def test_iter_file(self):
        f = open(TESTFN, "w")
        spróbuj:
            dla i w range(5):
                f.write("%d\n" % i)
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            self.check_for_loop(f, ["0\n", "1\n", "2\n", "3\n", "4\n"], pickle=Nieprawda)
            self.check_for_loop(f, [], pickle=Nieprawda)
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

    # Test list()'s use of iterators.
    def test_builtin_list(self):
        self.assertEqual(list(SequenceClass(5)), list(range(5)))
        self.assertEqual(list(SequenceClass(0)), [])
        self.assertEqual(list(()), [])

        d = {"one": 1, "two": 2, "three": 3}
        self.assertEqual(list(d), list(d.keys()))

        self.assertRaises(TypeError, list, list)
        self.assertRaises(TypeError, list, 42)

        f = open(TESTFN, "w")
        spróbuj:
            dla i w range(5):
                f.write("%d\n" % i)
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            self.assertEqual(list(f), ["0\n", "1\n", "2\n", "3\n", "4\n"])
            f.seek(0, 0)
            self.assertEqual(list(f),
                             ["0\n", "1\n", "2\n", "3\n", "4\n"])
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

    # Test tuples()'s use of iterators.
    def test_builtin_tuple(self):
        self.assertEqual(tuple(SequenceClass(5)), (0, 1, 2, 3, 4))
        self.assertEqual(tuple(SequenceClass(0)), ())
        self.assertEqual(tuple([]), ())
        self.assertEqual(tuple(()), ())
        self.assertEqual(tuple("abc"), ("a", "b", "c"))

        d = {"one": 1, "two": 2, "three": 3}
        self.assertEqual(tuple(d), tuple(d.keys()))

        self.assertRaises(TypeError, tuple, list)
        self.assertRaises(TypeError, tuple, 42)

        f = open(TESTFN, "w")
        spróbuj:
            dla i w range(5):
                f.write("%d\n" % i)
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            self.assertEqual(tuple(f), ("0\n", "1\n", "2\n", "3\n", "4\n"))
            f.seek(0, 0)
            self.assertEqual(tuple(f),
                             ("0\n", "1\n", "2\n", "3\n", "4\n"))
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

    # Test filter()'s use of iterators.
    def test_builtin_filter(self):
        self.assertEqual(list(filter(Nic, SequenceClass(5))),
                         list(range(1, 5)))
        self.assertEqual(list(filter(Nic, SequenceClass(0))), [])
        self.assertEqual(list(filter(Nic, ())), [])
        self.assertEqual(list(filter(Nic, "abc")), ["a", "b", "c"])

        d = {"one": 1, "two": 2, "three": 3}
        self.assertEqual(list(filter(Nic, d)), list(d.keys()))

        self.assertRaises(TypeError, filter, Nic, list)
        self.assertRaises(TypeError, filter, Nic, 42)

        klasa Boolean:
            def __init__(self, truth):
                self.truth = truth
            def __bool__(self):
                zwróć self.truth
        bPrawda = Boolean(Prawda)
        bNieprawda = Boolean(Nieprawda)

        klasa Seq:
            def __init__(self, *args):
                self.vals = args
            def __iter__(self):
                klasa SeqIter:
                    def __init__(self, vals):
                        self.vals = vals
                        self.i = 0
                    def __iter__(self):
                        zwróć self
                    def __next__(self):
                        i = self.i
                        self.i = i + 1
                        jeżeli i < len(self.vals):
                            zwróć self.vals[i]
                        inaczej:
                            podnieś StopIteration
                zwróć SeqIter(self.vals)

        seq = Seq(*([bPrawda, bNieprawda] * 25))
        self.assertEqual(list(filter(lambda x: nie x, seq)), [bNieprawda]*25)
        self.assertEqual(list(filter(lambda x: nie x, iter(seq))), [bNieprawda]*25)

    # Test max() oraz min()'s use of iterators.
    def test_builtin_max_min(self):
        self.assertEqual(max(SequenceClass(5)), 4)
        self.assertEqual(min(SequenceClass(5)), 0)
        self.assertEqual(max(8, -1), 8)
        self.assertEqual(min(8, -1), -1)

        d = {"one": 1, "two": 2, "three": 3}
        self.assertEqual(max(d), "two")
        self.assertEqual(min(d), "one")
        self.assertEqual(max(d.values()), 3)
        self.assertEqual(min(iter(d.values())), 1)

        f = open(TESTFN, "w")
        spróbuj:
            f.write("medium line\n")
            f.write("xtra large line\n")
            f.write("itty-bitty line\n")
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            self.assertEqual(min(f), "itty-bitty line\n")
            f.seek(0, 0)
            self.assertEqual(max(f), "xtra large line\n")
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

    # Test map()'s use of iterators.
    def test_builtin_map(self):
        self.assertEqual(list(map(lambda x: x+1, SequenceClass(5))),
                         list(range(1, 6)))

        d = {"one": 1, "two": 2, "three": 3}
        self.assertEqual(list(map(lambda k, d=d: (k, d[k]), d)),
                         list(d.items()))
        dkeys = list(d.keys())
        expected = [(i < len(d) oraz dkeys[i] albo Nic,
                     i,
                     i < len(d) oraz dkeys[i] albo Nic)
                    dla i w range(3)]

        f = open(TESTFN, "w")
        spróbuj:
            dla i w range(10):
                f.write("xy" * i + "\n") # line i has len 2*i+1
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            self.assertEqual(list(map(len, f)), list(range(1, 21, 2)))
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

    # Test zip()'s use of iterators.
    def test_builtin_zip(self):
        self.assertEqual(list(zip()), [])
        self.assertEqual(list(zip(*[])), [])
        self.assertEqual(list(zip(*[(1, 2), 'ab'])), [(1, 'a'), (2, 'b')])

        self.assertRaises(TypeError, zip, Nic)
        self.assertRaises(TypeError, zip, range(10), 42)
        self.assertRaises(TypeError, zip, range(10), zip)

        self.assertEqual(list(zip(IteratingSequenceClass(3))),
                         [(0,), (1,), (2,)])
        self.assertEqual(list(zip(SequenceClass(3))),
                         [(0,), (1,), (2,)])

        d = {"one": 1, "two": 2, "three": 3}
        self.assertEqual(list(d.items()), list(zip(d, d.values())))

        # Generate all ints starting at constructor arg.
        klasa IntsFrom:
            def __init__(self, start):
                self.i = start

            def __iter__(self):
                zwróć self

            def __next__(self):
                i = self.i
                self.i = i+1
                zwróć i

        f = open(TESTFN, "w")
        spróbuj:
            f.write("a\n" "bbb\n" "cc\n")
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            self.assertEqual(list(zip(IntsFrom(0), f, IntsFrom(-100))),
                             [(0, "a\n", -100),
                              (1, "bbb\n", -99),
                              (2, "cc\n", -98)])
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

        self.assertEqual(list(zip(range(5))), [(i,) dla i w range(5)])

        # Classes that lie about their lengths.
        klasa NoGuessLen5:
            def __getitem__(self, i):
                jeżeli i >= 5:
                    podnieś IndexError
                zwróć i

        klasa Guess3Len5(NoGuessLen5):
            def __len__(self):
                zwróć 3

        klasa Guess30Len5(NoGuessLen5):
            def __len__(self):
                zwróć 30

        def lzip(*args):
            zwróć list(zip(*args))

        self.assertEqual(len(Guess3Len5()), 3)
        self.assertEqual(len(Guess30Len5()), 30)
        self.assertEqual(lzip(NoGuessLen5()), lzip(range(5)))
        self.assertEqual(lzip(Guess3Len5()), lzip(range(5)))
        self.assertEqual(lzip(Guess30Len5()), lzip(range(5)))

        expected = [(i, i) dla i w range(5)]
        dla x w NoGuessLen5(), Guess3Len5(), Guess30Len5():
            dla y w NoGuessLen5(), Guess3Len5(), Guess30Len5():
                self.assertEqual(lzip(x, y), expected)

    def test_unicode_join_endcase(self):

        # This klasa inserts a Unicode object into its argument's natural
        # iteration, w the 3rd position.
        klasa OhPhooey:
            def __init__(self, seq):
                self.it = iter(seq)
                self.i = 0

            def __iter__(self):
                zwróć self

            def __next__(self):
                i = self.i
                self.i = i+1
                jeżeli i == 2:
                    zwróć "fooled you!"
                zwróć next(self.it)

        f = open(TESTFN, "w")
        spróbuj:
            f.write("a\n" + "b\n" + "c\n")
        w_końcu:
            f.close()

        f = open(TESTFN, "r")
        # Nasty:  string.join(s) can't know whether unicode.join() jest needed
        # until it's seen all of s's elements.  But w this case, f's
        # iterator cannot be restarted.  So what we're testing here jest
        # whether string.join() can manage to remember everything it's seen
        # oraz dalej that on to unicode.join().
        spróbuj:
            got = " - ".join(OhPhooey(f))
            self.assertEqual(got, "a\n - b\n - fooled you! - c\n")
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

    # Test iterators przy 'x w y' oraz 'x nie w y'.
    def test_in_and_not_in(self):
        dla sc5 w IteratingSequenceClass(5), SequenceClass(5):
            dla i w range(5):
                self.assertIn(i, sc5)
            dla i w "abc", -1, 5, 42.42, (3, 4), [], {1: 1}, 3-12j, sc5:
                self.assertNotIn(i, sc5)

        self.assertRaises(TypeError, lambda: 3 w 12)
        self.assertRaises(TypeError, lambda: 3 nie w map)

        d = {"one": 1, "two": 2, "three": 3, 1j: 2j}
        dla k w d:
            self.assertIn(k, d)
            self.assertNotIn(k, d.values())
        dla v w d.values():
            self.assertIn(v, d.values())
            self.assertNotIn(v, d)
        dla k, v w d.items():
            self.assertIn((k, v), d.items())
            self.assertNotIn((v, k), d.items())

        f = open(TESTFN, "w")
        spróbuj:
            f.write("a\n" "b\n" "c\n")
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            dla chunk w "abc":
                f.seek(0, 0)
                self.assertNotIn(chunk, f)
                f.seek(0, 0)
                self.assertIn((chunk + "\n"), f)
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

    # Test iterators przy operator.countOf (PySequence_Count).
    def test_countOf(self):
        z operator zaimportuj countOf
        self.assertEqual(countOf([1,2,2,3,2,5], 2), 3)
        self.assertEqual(countOf((1,2,2,3,2,5), 2), 3)
        self.assertEqual(countOf("122325", "2"), 3)
        self.assertEqual(countOf("122325", "6"), 0)

        self.assertRaises(TypeError, countOf, 42, 1)
        self.assertRaises(TypeError, countOf, countOf, countOf)

        d = {"one": 3, "two": 3, "three": 3, 1j: 2j}
        dla k w d:
            self.assertEqual(countOf(d, k), 1)
        self.assertEqual(countOf(d.values(), 3), 3)
        self.assertEqual(countOf(d.values(), 2j), 1)
        self.assertEqual(countOf(d.values(), 1j), 0)

        f = open(TESTFN, "w")
        spróbuj:
            f.write("a\n" "b\n" "c\n" "b\n")
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            dla letter, count w ("a", 1), ("b", 2), ("c", 1), ("d", 0):
                f.seek(0, 0)
                self.assertEqual(countOf(f, letter + "\n"), count)
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

    # Test iterators przy operator.indexOf (PySequence_Index).
    def test_indexOf(self):
        z operator zaimportuj indexOf
        self.assertEqual(indexOf([1,2,2,3,2,5], 1), 0)
        self.assertEqual(indexOf((1,2,2,3,2,5), 2), 1)
        self.assertEqual(indexOf((1,2,2,3,2,5), 3), 3)
        self.assertEqual(indexOf((1,2,2,3,2,5), 5), 5)
        self.assertRaises(ValueError, indexOf, (1,2,2,3,2,5), 0)
        self.assertRaises(ValueError, indexOf, (1,2,2,3,2,5), 6)

        self.assertEqual(indexOf("122325", "2"), 1)
        self.assertEqual(indexOf("122325", "5"), 5)
        self.assertRaises(ValueError, indexOf, "122325", "6")

        self.assertRaises(TypeError, indexOf, 42, 1)
        self.assertRaises(TypeError, indexOf, indexOf, indexOf)

        f = open(TESTFN, "w")
        spróbuj:
            f.write("a\n" "b\n" "c\n" "d\n" "e\n")
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            fiter = iter(f)
            self.assertEqual(indexOf(fiter, "b\n"), 1)
            self.assertEqual(indexOf(fiter, "d\n"), 1)
            self.assertEqual(indexOf(fiter, "e\n"), 0)
            self.assertRaises(ValueError, indexOf, fiter, "a\n")
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

        iclass = IteratingSequenceClass(3)
        dla i w range(3):
            self.assertEqual(indexOf(iclass, i), i)
        self.assertRaises(ValueError, indexOf, iclass, -1)

    # Test iterators przy file.writelines().
    def test_writelines(self):
        f = open(TESTFN, "w")

        spróbuj:
            self.assertRaises(TypeError, f.writelines, Nic)
            self.assertRaises(TypeError, f.writelines, 42)

            f.writelines(["1\n", "2\n"])
            f.writelines(("3\n", "4\n"))
            f.writelines({'5\n': Nic})
            f.writelines({})

            # Try a big chunk too.
            klasa Iterator:
                def __init__(self, start, finish):
                    self.start = start
                    self.finish = finish
                    self.i = self.start

                def __next__(self):
                    jeżeli self.i >= self.finish:
                        podnieś StopIteration
                    result = str(self.i) + '\n'
                    self.i += 1
                    zwróć result

                def __iter__(self):
                    zwróć self

            klasa Whatever:
                def __init__(self, start, finish):
                    self.start = start
                    self.finish = finish

                def __iter__(self):
                    zwróć Iterator(self.start, self.finish)

            f.writelines(Whatever(6, 6+2000))
            f.close()

            f = open(TESTFN)
            expected = [str(i) + "\n" dla i w range(1, 2006)]
            self.assertEqual(list(f), expected)

        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej


    # Test iterators on RHS of unpacking assignments.
    def test_unpack_iter(self):
        a, b = 1, 2
        self.assertEqual((a, b), (1, 2))

        a, b, c = IteratingSequenceClass(3)
        self.assertEqual((a, b, c), (0, 1, 2))

        spróbuj:    # too many values
            a, b = IteratingSequenceClass(3)
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("should have podnieśd ValueError")

        spróbuj:    # nie enough values
            a, b, c = IteratingSequenceClass(2)
        wyjąwszy ValueError:
            dalej
        inaczej:
            self.fail("should have podnieśd ValueError")

        spróbuj:    # nie iterable
            a, b, c = len
        wyjąwszy TypeError:
            dalej
        inaczej:
            self.fail("should have podnieśd TypeError")

        a, b, c = {1: 42, 2: 42, 3: 42}.values()
        self.assertEqual((a, b, c), (42, 42, 42))

        f = open(TESTFN, "w")
        lines = ("a\n", "bb\n", "ccc\n")
        spróbuj:
            dla line w lines:
                f.write(line)
        w_końcu:
            f.close()
        f = open(TESTFN, "r")
        spróbuj:
            a, b, c = f
            self.assertEqual((a, b, c), lines)
        w_końcu:
            f.close()
            spróbuj:
                unlink(TESTFN)
            wyjąwszy OSError:
                dalej

        (a, b), (c,) = IteratingSequenceClass(2), {42: 24}
        self.assertEqual((a, b, c), (0, 1, 42))


    @cpython_only
    def test_ref_counting_behavior(self):
        klasa C(object):
            count = 0
            def __new__(cls):
                cls.count += 1
                zwróć object.__new__(cls)
            def __del__(self):
                cls = self.__class__
                assert cls.count > 0
                cls.count -= 1
        x = C()
        self.assertEqual(C.count, 1)
        usuń x
        self.assertEqual(C.count, 0)
        l = [C(), C(), C()]
        self.assertEqual(C.count, 3)
        spróbuj:
            a, b = iter(l)
        wyjąwszy ValueError:
            dalej
        usuń l
        self.assertEqual(C.count, 0)


    # Make sure StopIteration jest a "sink state".
    # This tests various things that weren't sink states w Python 2.2.1,
    # plus various things that always were fine.

    def test_sinkstate_list(self):
        # This used to fail
        a = list(range(5))
        b = iter(a)
        self.assertEqual(list(b), list(range(5)))
        a.extend(range(5, 10))
        self.assertEqual(list(b), [])

    def test_sinkstate_tuple(self):
        a = (0, 1, 2, 3, 4)
        b = iter(a)
        self.assertEqual(list(b), list(range(5)))
        self.assertEqual(list(b), [])

    def test_sinkstate_string(self):
        a = "abcde"
        b = iter(a)
        self.assertEqual(list(b), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual(list(b), [])

    def test_sinkstate_sequence(self):
        # This used to fail
        a = SequenceClass(5)
        b = iter(a)
        self.assertEqual(list(b), list(range(5)))
        a.n = 10
        self.assertEqual(list(b), [])

    def test_sinkstate_callable(self):
        # This used to fail
        def spam(state=[0]):
            i = state[0]
            state[0] = i+1
            jeżeli i == 10:
                podnieś AssertionError("shouldn't have gotten this far")
            zwróć i
        b = iter(spam, 5)
        self.assertEqual(list(b), list(range(5)))
        self.assertEqual(list(b), [])

    def test_sinkstate_dict(self):
        # XXX For a more thorough test, see towards the end of:
        # http://mail.python.org/pipermail/python-dev/2002-July/026512.html
        a = {1:1, 2:2, 0:0, 4:4, 3:3}
        dla b w iter(a), a.keys(), a.items(), a.values():
            b = iter(a)
            self.assertEqual(len(list(b)), 5)
            self.assertEqual(list(b), [])

    def test_sinkstate_uzyskaj(self):
        def gen():
            dla i w range(5):
                uzyskaj i
        b = gen()
        self.assertEqual(list(b), list(range(5)))
        self.assertEqual(list(b), [])

    def test_sinkstate_range(self):
        a = range(5)
        b = iter(a)
        self.assertEqual(list(b), list(range(5)))
        self.assertEqual(list(b), [])

    def test_sinkstate_enumerate(self):
        a = range(5)
        e = enumerate(a)
        b = iter(e)
        self.assertEqual(list(b), list(zip(range(5), range(5))))
        self.assertEqual(list(b), [])

    def test_3720(self):
        # Avoid a crash, when an iterator deletes its next() method.
        klasa BadIterator(object):
            def __iter__(self):
                zwróć self
            def __next__(self):
                usuń BadIterator.__next__
                zwróć 1

        spróbuj:
            dla i w BadIterator() :
                dalej
        wyjąwszy TypeError:
            dalej

    def test_extending_list_with_iterator_does_not_segfault(self):
        # The code to extend a list przy an iterator has a fair
        # amount of nontrivial logic w terms of guessing how
        # much memory to allocate w advance, "stealing" refs,
        # oraz then shrinking at the end.  This jest a basic smoke
        # test dla that scenario.
        def gen():
            dla i w range(500):
                uzyskaj i
        lst = [0] * 500
        dla i w range(240):
            lst.pop(0)
        lst.extend(gen())
        self.assertEqual(len(lst), 760)

    @cpython_only
    def test_iter_overflow(self):
        # Test dla the issue 22939
        it = iter(UnlimitedSequenceClass())
        # Manually set `it_index` to PY_SSIZE_T_MAX-2 without a loop
        it.__setstate__(sys.maxsize - 2)
        self.assertEqual(next(it), sys.maxsize - 2)
        self.assertEqual(next(it), sys.maxsize - 1)
        przy self.assertRaises(OverflowError):
            next(it)
        # Check that Overflow error jest always podnieśd
        przy self.assertRaises(OverflowError):
            next(it)

    def test_iter_neg_setstate(self):
        it = iter(UnlimitedSequenceClass())
        it.__setstate__(-42)
        self.assertEqual(next(it), 0)
        self.assertEqual(next(it), 1)


def test_main():
    run_unittest(TestCase)


jeżeli __name__ == "__main__":
    test_main()
