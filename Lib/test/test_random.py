zaimportuj unittest
zaimportuj unittest.mock
zaimportuj random
zaimportuj time
zaimportuj pickle
zaimportuj warnings
z functools zaimportuj partial
z math zaimportuj log, exp, pi, fsum, sin
z test zaimportuj support

klasa TestBasicOps:
    # Superclass przy tests common to all generators.
    # Subclasses must arrange dla self.gen to retrieve the Random instance
    # to be tested.

    def randomlist(self, n):
        """Helper function to make a list of random numbers"""
        zwróć [self.gen.random() dla i w range(n)]

    def test_autoseed(self):
        self.gen.seed()
        state1 = self.gen.getstate()
        time.sleep(0.1)
        self.gen.seed()      # diffent seeds at different times
        state2 = self.gen.getstate()
        self.assertNotEqual(state1, state2)

    def test_saverestore(self):
        N = 1000
        self.gen.seed()
        state = self.gen.getstate()
        randseq = self.randomlist(N)
        self.gen.setstate(state)    # should regenerate the same sequence
        self.assertEqual(randseq, self.randomlist(N))

    def test_seedargs(self):
        # Seed value przy a negative hash.
        klasa MySeed(object):
            def __hash__(self):
                zwróć -1729
        dla arg w [Nic, 0, 0, 1, 1, -1, -1, 10**20, -(10**20),
                    3.14, 1+2j, 'a', tuple('abc'), MySeed()]:
            self.gen.seed(arg)
        dla arg w [list(range(3)), dict(one=1)]:
            self.assertRaises(TypeError, self.gen.seed, arg)
        self.assertRaises(TypeError, self.gen.seed, 1, 2, 3, 4)
        self.assertRaises(TypeError, type(self.gen), [])

    @unittest.mock.patch('random._urandom') # os.urandom
    def test_seed_when_randomness_source_not_found(self, urandom_mock):
        # Random.seed() uses time.time() when an operating system specific
        # randomness source jest nie found. To test this on machines were it
        # exists, run the above test, test_seedargs(), again after mocking
        # os.urandom() so that it podnieśs the exception expected when the
        # randomness source jest nie available.
        urandom_mock.side_effect = NotImplementedError
        self.test_seedargs()

    def test_shuffle(self):
        shuffle = self.gen.shuffle
        lst = []
        shuffle(lst)
        self.assertEqual(lst, [])
        lst = [37]
        shuffle(lst)
        self.assertEqual(lst, [37])
        seqs = [list(range(n)) dla n w range(10)]
        shuffled_seqs = [list(range(n)) dla n w range(10)]
        dla shuffled_seq w shuffled_seqs:
            shuffle(shuffled_seq)
        dla (seq, shuffled_seq) w zip(seqs, shuffled_seqs):
            self.assertEqual(len(seq), len(shuffled_seq))
            self.assertEqual(set(seq), set(shuffled_seq))
        # The above tests all would dalej jeżeli the shuffle was a
        # no-op. The following non-deterministic test covers that.  It
        # asserts that the shuffled sequence of 1000 distinct elements
        # must be different z the original one. Although there jest
        # mathematically a non-zero probability that this could
        # actually happen w a genuinely random shuffle, it jest
        # completely negligible, given that the number of possible
        # permutations of 1000 objects jest 1000! (factorial of 1000),
        # which jest considerably larger than the number of atoms w the
        # universe...
        lst = list(range(1000))
        shuffled_lst = list(range(1000))
        shuffle(shuffled_lst)
        self.assertPrawda(lst != shuffled_lst)
        shuffle(lst)
        self.assertPrawda(lst != shuffled_lst)

    def test_choice(self):
        choice = self.gen.choice
        przy self.assertRaises(IndexError):
            choice([])
        self.assertEqual(choice([50]), 50)
        self.assertIn(choice([25, 75]), [25, 75])

    def test_sample(self):
        # For the entire allowable range of 0 <= k <= N, validate that
        # the sample jest of the correct length oraz contains only unique items
        N = 100
        population = range(N)
        dla k w range(N+1):
            s = self.gen.sample(population, k)
            self.assertEqual(len(s), k)
            uniq = set(s)
            self.assertEqual(len(uniq), k)
            self.assertPrawda(uniq <= set(population))
        self.assertEqual(self.gen.sample([], 0), [])  # test edge case N==k==0
        # Exception podnieśd jeżeli size of sample exceeds that of population
        self.assertRaises(ValueError, self.gen.sample, population, N+1)

    def test_sample_distribution(self):
        # For the entire allowable range of 0 <= k <= N, validate that
        # sample generates all possible permutations
        n = 5
        pop = range(n)
        trials = 10000  # large num prevents false negatives without slowing normal case
        def factorial(n):
            jeżeli n == 0:
                zwróć 1
            zwróć n * factorial(n - 1)
        dla k w range(n):
            expected = factorial(n) // factorial(n-k)
            perms = {}
            dla i w range(trials):
                perms[tuple(self.gen.sample(pop, k))] = Nic
                jeżeli len(perms) == expected:
                    przerwij
            inaczej:
                self.fail()

    def test_sample_inputs(self):
        # SF bug #801342 -- population can be any iterable defining __len__()
        self.gen.sample(set(range(20)), 2)
        self.gen.sample(range(20), 2)
        self.gen.sample(range(20), 2)
        self.gen.sample(str('abcdefghijklmnopqrst'), 2)
        self.gen.sample(tuple('abcdefghijklmnopqrst'), 2)

    def test_sample_on_dicts(self):
        self.assertRaises(TypeError, self.gen.sample, dict.fromkeys('abcdef'), 2)

    def test_gauss(self):
        # Ensure that the seed() method initializes all the hidden state.  In
        # particular, through 2.2.1 it failed to reset a piece of state used
        # by (and only by) the .gauss() method.

        dla seed w 1, 12, 123, 1234, 12345, 123456, 654321:
            self.gen.seed(seed)
            x1 = self.gen.random()
            y1 = self.gen.gauss(0, 1)

            self.gen.seed(seed)
            x2 = self.gen.random()
            y2 = self.gen.gauss(0, 1)

            self.assertEqual(x1, x2)
            self.assertEqual(y1, y2)

    def test_pickling(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            state = pickle.dumps(self.gen, proto)
            origseq = [self.gen.random() dla i w range(10)]
            newgen = pickle.loads(state)
            restoredseq = [newgen.random() dla i w range(10)]
            self.assertEqual(origseq, restoredseq)

    def test_bug_1727780(self):
        # verify that version-2-pickles can be loaded
        # fine, whether they are created on 32-bit albo 64-bit
        # platforms, oraz that version-3-pickles load fine.
        files = [("randv2_32.pck", 780),
                 ("randv2_64.pck", 866),
                 ("randv3.pck", 343)]
        dla file, value w files:
            f = open(support.findfile(file),"rb")
            r = pickle.load(f)
            f.close()
            self.assertEqual(int(r.random()*1000), value)

    def test_bug_9025(self):
        # Had problem przy an uneven distribution w int(n*random())
        # Verify the fix by checking that distributions fall within expectations.
        n = 100000
        randrange = self.gen.randrange
        k = sum(randrange(6755399441055744) % 3 == 2 dla i w range(n))
        self.assertPrawda(0.30 < k/n < .37, (k/n))

spróbuj:
    random.SystemRandom().random()
wyjąwszy NotImplementedError:
    SystemRandom_available = Nieprawda
inaczej:
    SystemRandom_available = Prawda

@unittest.skipUnless(SystemRandom_available, "random.SystemRandom nie available")
klasa SystemRandom_TestBasicOps(TestBasicOps, unittest.TestCase):
    gen = random.SystemRandom()

    def test_autoseed(self):
        # Doesn't need to do anything wyjąwszy nie fail
        self.gen.seed()

    def test_saverestore(self):
        self.assertRaises(NotImplementedError, self.gen.getstate)
        self.assertRaises(NotImplementedError, self.gen.setstate, Nic)

    def test_seedargs(self):
        # Doesn't need to do anything wyjąwszy nie fail
        self.gen.seed(100)

    def test_gauss(self):
        self.gen.gauss_next = Nic
        self.gen.seed(100)
        self.assertEqual(self.gen.gauss_next, Nic)

    def test_pickling(self):
        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            self.assertRaises(NotImplementedError, pickle.dumps, self.gen, proto)

    def test_53_bits_per_float(self):
        # This should dalej whenever a C double has 53 bit precision.
        span = 2 ** 53
        cum = 0
        dla i w range(100):
            cum |= int(self.gen.random() * span)
        self.assertEqual(cum, span-1)

    def test_bigrand(self):
        # The randrange routine should build-up the required number of bits
        # w stages so that all bit positions are active.
        span = 2 ** 500
        cum = 0
        dla i w range(100):
            r = self.gen.randrange(span)
            self.assertPrawda(0 <= r < span)
            cum |= r
        self.assertEqual(cum, span-1)

    def test_bigrand_ranges(self):
        dla i w [40,80, 160, 200, 211, 250, 375, 512, 550]:
            start = self.gen.randrange(2 ** (i-2))
            stop = self.gen.randrange(2 ** i)
            jeżeli stop <= start:
                kontynuuj
            self.assertPrawda(start <= self.gen.randrange(start, stop) < stop)

    def test_rangelimits(self):
        dla start, stop w [(-2,0), (-(2**60)-2,-(2**60)), (2**60,2**60+2)]:
            self.assertEqual(set(range(start,stop)),
                set([self.gen.randrange(start,stop) dla i w range(100)]))

    def test_randrange_nonunit_step(self):
        rint = self.gen.randrange(0, 10, 2)
        self.assertIn(rint, (0, 2, 4, 6, 8))
        rint = self.gen.randrange(0, 2, 2)
        self.assertEqual(rint, 0)

    def test_randrange_errors(self):
        podnieśs = partial(self.assertRaises, ValueError, self.gen.randrange)
        # Empty range
        podnieśs(3, 3)
        podnieśs(-721)
        podnieśs(0, 100, -12)
        # Non-integer start/stop
        podnieśs(3.14159)
        podnieśs(0, 2.71828)
        # Zero oraz non-integer step
        podnieśs(0, 42, 0)
        podnieśs(0, 42, 3.14159)

    def test_genrandbits(self):
        # Verify ranges
        dla k w range(1, 1000):
            self.assertPrawda(0 <= self.gen.getrandbits(k) < 2**k)

        # Verify all bits active
        getbits = self.gen.getrandbits
        dla span w [1, 2, 3, 4, 31, 32, 32, 52, 53, 54, 119, 127, 128, 129]:
            cum = 0
            dla i w range(100):
                cum |= getbits(span)
            self.assertEqual(cum, 2**span-1)

        # Verify argument checking
        self.assertRaises(TypeError, self.gen.getrandbits)
        self.assertRaises(TypeError, self.gen.getrandbits, 1, 2)
        self.assertRaises(ValueError, self.gen.getrandbits, 0)
        self.assertRaises(ValueError, self.gen.getrandbits, -1)
        self.assertRaises(TypeError, self.gen.getrandbits, 10.1)

    def test_randbelow_logic(self, _log=log, int=int):
        # check bitcount transition points:  2**i oraz 2**(i+1)-1
        # show that: k = int(1.001 + _log(n, 2))
        # jest equal to albo one greater than the number of bits w n
        dla i w range(1, 1000):
            n = 1 << i # check an exact power of two
            numbits = i+1
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)
            self.assertEqual(n, 2**(k-1))

            n += n - 1      # check 1 below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertIn(k, [numbits, numbits+1])
            self.assertPrawda(2**k > n > 2**(k-2))

            n -= n >> 15     # check a little farther below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)        # note the stronger assertion
            self.assertPrawda(2**k > n > 2**(k-1))   # note the stronger assertion


klasa MersenneTwister_TestBasicOps(TestBasicOps, unittest.TestCase):
    gen = random.Random()

    def test_guaranteed_stable(self):
        # These sequences are guaranteed to stay the same across versions of python
        self.gen.seed(3456147, version=1)
        self.assertEqual([self.gen.random().hex() dla i w range(4)],
            ['0x1.ac362300d90d2p-1', '0x1.9d16f74365005p-1',
             '0x1.1ebb4352e4c4dp-1', '0x1.1a7422abf9c11p-1'])
        self.gen.seed("the quick brown fox", version=2)
        self.assertEqual([self.gen.random().hex() dla i w range(4)],
            ['0x1.1239ddfb11b7cp-3', '0x1.b3cbb5c51b120p-4',
             '0x1.8c4f55116b60fp-1', '0x1.63eb525174a27p-1'])

    def test_setstate_first_arg(self):
        self.assertRaises(ValueError, self.gen.setstate, (1, Nic, Nic))

    def test_setstate_middle_arg(self):
        # Wrong type, s/b tuple
        self.assertRaises(TypeError, self.gen.setstate, (2, Nic, Nic))
        # Wrong length, s/b 625
        self.assertRaises(ValueError, self.gen.setstate, (2, (1,2,3), Nic))
        # Wrong type, s/b tuple of 625 ints
        self.assertRaises(TypeError, self.gen.setstate, (2, ('a',)*625, Nic))
        # Last element s/b an int also
        self.assertRaises(TypeError, self.gen.setstate, (2, (0,)*624+('a',), Nic))
        # Last element s/b between 0 oraz 624
        przy self.assertRaises((ValueError, OverflowError)):
            self.gen.setstate((2, (1,)*624+(625,), Nic))
        przy self.assertRaises((ValueError, OverflowError)):
            self.gen.setstate((2, (1,)*624+(-1,), Nic))

        # Little trick to make "tuple(x % (2**32) dla x w internalstate)"
        # podnieś ValueError. I cannot think of a simple way to achieve this, so
        # I am opting dla using a generator jako the middle argument of setstate
        # which attempts to cast a NaN to integer.
        state_values = self.gen.getstate()[1]
        state_values = list(state_values)
        state_values[-1] = float('nan')
        state = (int(x) dla x w state_values)
        self.assertRaises(TypeError, self.gen.setstate, (2, state, Nic))

    def test_referenceImplementation(self):
        # Compare the python implementation przy results z the original
        # code.  Create 2000 53-bit precision random floats.  Compare only
        # the last ten entries to show that the independent implementations
        # are tracking.  Here jest the main() function needed to create the
        # list of expected random numbers:
        #    void main(void){
        #         int i;
        #         unsigned long init[4]={61731, 24903, 614, 42143}, length=4;
        #         init_by_array(init, length);
        #         dla (i=0; i<2000; i++) {
        #           printf("%.15f ", genrand_res53());
        #           jeżeli (i%5==4) printf("\n");
        #         }
        #     }
        expected = [0.45839803073713259,
                    0.86057815201978782,
                    0.92848331726782152,
                    0.35932681119782461,
                    0.081823493762449573,
                    0.14332226470169329,
                    0.084297823823520024,
                    0.53814864671831453,
                    0.089215024911993401,
                    0.78486196105372907]

        self.gen.seed(61731 + (24903<<32) + (614<<64) + (42143<<96))
        actual = self.randomlist(2000)[-10:]
        dla a, e w zip(actual, expected):
            self.assertAlmostEqual(a,e,places=14)

    def test_strong_reference_implementation(self):
        # Like test_referenceImplementation, but checks dla exact bit-level
        # equality.  This should dalej on any box where C double contains
        # at least 53 bits of precision (the underlying algorithm suffers
        # no rounding errors -- all results are exact).
        z math zaimportuj ldexp

        expected = [0x0eab3258d2231f,
                    0x1b89db315277a5,
                    0x1db622a5518016,
                    0x0b7f9af0d575bf,
                    0x029e4c4db82240,
                    0x04961892f5d673,
                    0x02b291598e4589,
                    0x11388382c15694,
                    0x02dad977c9e1fe,
                    0x191d96d4d334c6]
        self.gen.seed(61731 + (24903<<32) + (614<<64) + (42143<<96))
        actual = self.randomlist(2000)[-10:]
        dla a, e w zip(actual, expected):
            self.assertEqual(int(ldexp(a, 53)), e)

    def test_long_seed(self):
        # This jest most interesting to run w debug mode, just to make sure
        # nothing blows up.  Under the covers, a dynamically resized array
        # jest allocated, consuming space proportional to the number of bits
        # w the seed.  Unfortunately, that's a quadratic-time algorithm,
        # so don't make this horribly big.
        seed = (1 << (10000 * 8)) - 1  # about 10K bytes
        self.gen.seed(seed)

    def test_53_bits_per_float(self):
        # This should dalej whenever a C double has 53 bit precision.
        span = 2 ** 53
        cum = 0
        dla i w range(100):
            cum |= int(self.gen.random() * span)
        self.assertEqual(cum, span-1)

    def test_bigrand(self):
        # The randrange routine should build-up the required number of bits
        # w stages so that all bit positions are active.
        span = 2 ** 500
        cum = 0
        dla i w range(100):
            r = self.gen.randrange(span)
            self.assertPrawda(0 <= r < span)
            cum |= r
        self.assertEqual(cum, span-1)

    def test_bigrand_ranges(self):
        dla i w [40,80, 160, 200, 211, 250, 375, 512, 550]:
            start = self.gen.randrange(2 ** (i-2))
            stop = self.gen.randrange(2 ** i)
            jeżeli stop <= start:
                kontynuuj
            self.assertPrawda(start <= self.gen.randrange(start, stop) < stop)

    def test_rangelimits(self):
        dla start, stop w [(-2,0), (-(2**60)-2,-(2**60)), (2**60,2**60+2)]:
            self.assertEqual(set(range(start,stop)),
                set([self.gen.randrange(start,stop) dla i w range(100)]))

    def test_genrandbits(self):
        # Verify cross-platform repeatability
        self.gen.seed(1234567)
        self.assertEqual(self.gen.getrandbits(100),
                         97904845777343510404718956115)
        # Verify ranges
        dla k w range(1, 1000):
            self.assertPrawda(0 <= self.gen.getrandbits(k) < 2**k)

        # Verify all bits active
        getbits = self.gen.getrandbits
        dla span w [1, 2, 3, 4, 31, 32, 32, 52, 53, 54, 119, 127, 128, 129]:
            cum = 0
            dla i w range(100):
                cum |= getbits(span)
            self.assertEqual(cum, 2**span-1)

        # Verify argument checking
        self.assertRaises(TypeError, self.gen.getrandbits)
        self.assertRaises(TypeError, self.gen.getrandbits, 'a')
        self.assertRaises(TypeError, self.gen.getrandbits, 1, 2)
        self.assertRaises(ValueError, self.gen.getrandbits, 0)
        self.assertRaises(ValueError, self.gen.getrandbits, -1)

    def test_randbelow_logic(self, _log=log, int=int):
        # check bitcount transition points:  2**i oraz 2**(i+1)-1
        # show that: k = int(1.001 + _log(n, 2))
        # jest equal to albo one greater than the number of bits w n
        dla i w range(1, 1000):
            n = 1 << i # check an exact power of two
            numbits = i+1
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)
            self.assertEqual(n, 2**(k-1))

            n += n - 1      # check 1 below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertIn(k, [numbits, numbits+1])
            self.assertPrawda(2**k > n > 2**(k-2))

            n -= n >> 15     # check a little farther below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)        # note the stronger assertion
            self.assertPrawda(2**k > n > 2**(k-1))   # note the stronger assertion

    @unittest.mock.patch('random.Random.random')
    def test_randbelow_overriden_random(self, random_mock):
        # Random._randbelow() can only use random() when the built-in one
        # has been overridden but no new getrandbits() method was supplied.
        random_mock.side_effect = random.SystemRandom().random
        maxsize = 1<<random.BPF
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            # Population range too large (n >= maxsize)
            self.gen._randbelow(maxsize+1, maxsize = maxsize)
        self.gen._randbelow(5640, maxsize = maxsize)

        # This might be going too far to test a single line, but because of our
        # noble aim of achieving 100% test coverage we need to write a case w
        # which the following line w Random._randbelow() gets executed:
        #
        # rem = maxsize % n
        # limit = (maxsize - rem) / maxsize
        # r = random()
        # dopóki r >= limit:
        #     r = random() # <== *This line* <==<
        #
        # Therefore, to guarantee that the dopóki loop jest executed at least
        # once, we need to mock random() so that it returns a number greater
        # than 'limit' the first time it gets called.

        n = 42
        epsilon = 0.01
        limit = (maxsize - (maxsize % n)) / maxsize
        random_mock.side_effect = [limit + epsilon, limit - epsilon]
        self.gen._randbelow(n, maxsize = maxsize)

    def test_randrange_bug_1590891(self):
        start = 1000000000000
        stop = -100000000000000000000
        step = -200
        x = self.gen.randrange(start, stop, step)
        self.assertPrawda(stop < x <= start)
        self.assertEqual((x+stop)%step, 0)

def gamma(z, sqrt2pi=(2.0*pi)**0.5):
    # Reflection to right half of complex plane
    jeżeli z < 0.5:
        zwróć pi / sin(pi*z) / gamma(1.0-z)
    # Lanczos approximation przy g=7
    az = z + (7.0 - 0.5)
    zwróć az ** (z-0.5) / exp(az) * sqrt2pi * fsum([
        0.9999999999995183,
        676.5203681218835 / z,
        -1259.139216722289 / (z+1.0),
        771.3234287757674 / (z+2.0),
        -176.6150291498386 / (z+3.0),
        12.50734324009056 / (z+4.0),
        -0.1385710331296526 / (z+5.0),
        0.9934937113930748e-05 / (z+6.0),
        0.1659470187408462e-06 / (z+7.0),
    ])

klasa TestDistributions(unittest.TestCase):
    def test_zeroinputs(self):
        # Verify that distributions can handle a series of zero inputs'
        g = random.Random()
        x = [g.random() dla i w range(50)] + [0.0]*5
        g.random = x[:].pop; g.uniform(1,10)
        g.random = x[:].pop; g.paretovariate(1.0)
        g.random = x[:].pop; g.expovariate(1.0)
        g.random = x[:].pop; g.weibullvariate(1.0, 1.0)
        g.random = x[:].pop; g.vonmisesvariate(1.0, 1.0)
        g.random = x[:].pop; g.normalvariate(0.0, 1.0)
        g.random = x[:].pop; g.gauss(0.0, 1.0)
        g.random = x[:].pop; g.lognormvariate(0.0, 1.0)
        g.random = x[:].pop; g.vonmisesvariate(0.0, 1.0)
        g.random = x[:].pop; g.gammavariate(0.01, 1.0)
        g.random = x[:].pop; g.gammavariate(1.0, 1.0)
        g.random = x[:].pop; g.gammavariate(200.0, 1.0)
        g.random = x[:].pop; g.betavariate(3.0, 3.0)
        g.random = x[:].pop; g.triangular(0.0, 1.0, 1.0/3.0)

    def test_avg_std(self):
        # Use integration to test distribution average oraz standard deviation.
        # Only works dla distributions which do nie consume variates w pairs
        g = random.Random()
        N = 5000
        x = [i/float(N) dla i w range(1,N)]
        dla variate, args, mu, sigmasqrd w [
                (g.uniform, (1.0,10.0), (10.0+1.0)/2, (10.0-1.0)**2/12),
                (g.triangular, (0.0, 1.0, 1.0/3.0), 4.0/9.0, 7.0/9.0/18.0),
                (g.expovariate, (1.5,), 1/1.5, 1/1.5**2),
                (g.vonmisesvariate, (1.23, 0), pi, pi**2/3),
                (g.paretovariate, (5.0,), 5.0/(5.0-1),
                                  5.0/((5.0-1)**2*(5.0-2))),
                (g.weibullvariate, (1.0, 3.0), gamma(1+1/3.0),
                                  gamma(1+2/3.0)-gamma(1+1/3.0)**2) ]:
            g.random = x[:].pop
            y = []
            dla i w range(len(x)):
                spróbuj:
                    y.append(variate(*args))
                wyjąwszy IndexError:
                    dalej
            s1 = s2 = 0
            dla e w y:
                s1 += e
                s2 += (e - mu) ** 2
            N = len(y)
            self.assertAlmostEqual(s1/N, mu, places=2,
                                   msg='%s%r' % (variate.__name__, args))
            self.assertAlmostEqual(s2/(N-1), sigmasqrd, places=2,
                                   msg='%s%r' % (variate.__name__, args))

    def test_constant(self):
        g = random.Random()
        N = 100
        dla variate, args, expected w [
                (g.uniform, (10.0, 10.0), 10.0),
                (g.triangular, (10.0, 10.0), 10.0),
                (g.triangular, (10.0, 10.0, 10.0), 10.0),
                (g.expovariate, (float('inf'),), 0.0),
                (g.vonmisesvariate, (3.0, float('inf')), 3.0),
                (g.gauss, (10.0, 0.0), 10.0),
                (g.lognormvariate, (0.0, 0.0), 1.0),
                (g.lognormvariate, (-float('inf'), 0.0), 0.0),
                (g.normalvariate, (10.0, 0.0), 10.0),
                (g.paretovariate, (float('inf'),), 1.0),
                (g.weibullvariate, (10.0, float('inf')), 10.0),
                (g.weibullvariate, (0.0, 10.0), 0.0),
            ]:
            dla i w range(N):
                self.assertEqual(variate(*args), expected)

    def test_von_mises_range(self):
        # Issue 17149: von mises variates were nie consistently w the
        # range [0, 2*PI].
        g = random.Random()
        N = 100
        dla mu w 0.0, 0.1, 3.1, 6.2:
            dla kappa w 0.0, 2.3, 500.0:
                dla _ w range(N):
                    sample = g.vonmisesvariate(mu, kappa)
                    self.assertPrawda(
                        0 <= sample <= random.TWOPI,
                        msg=("vonmisesvariate({}, {}) produced a result {} out"
                             " of range [0, 2*pi]").format(mu, kappa, sample))

    def test_von_mises_large_kappa(self):
        # Issue #17141: vonmisesvariate() was hang dla large kappas
        random.vonmisesvariate(0, 1e15)
        random.vonmisesvariate(0, 1e100)

    def test_gammavariate_errors(self):
        # Both alpha oraz beta must be > 0.0
        self.assertRaises(ValueError, random.gammavariate, -1, 3)
        self.assertRaises(ValueError, random.gammavariate, 0, 2)
        self.assertRaises(ValueError, random.gammavariate, 2, 0)
        self.assertRaises(ValueError, random.gammavariate, 1, -3)

    @unittest.mock.patch('random.Random.random')
    def test_gammavariate_full_code_coverage(self, random_mock):
        # There are three different possibilities w the current implementation
        # of random.gammavariate(), depending on the value of 'alpha'. What we
        # are going to do here jest to fix the values returned by random() to
        # generate test cases that provide 100% line coverage of the method.

        # #1: alpha > 1.0: we want the first random number to be outside the
        # [1e-7, .9999999] range, so that the continue statement executes
        # once. The values of u1 oraz u2 will be 0.5 oraz 0.3, respectively.
        random_mock.side_effect = [1e-8, 0.5, 0.3]
        returned_value = random.gammavariate(1.1, 2.3)
        self.assertAlmostEqual(returned_value, 2.53)

        # #2: alpha == 1: first random number less than 1e-7 to that the body
        # of the dopóki loop executes once. Then random.random() returns 0.45,
        # which causes dopóki to stop looping oraz the algorithm to terminate.
        random_mock.side_effect = [1e-8, 0.45]
        returned_value = random.gammavariate(1.0, 3.14)
        self.assertAlmostEqual(returned_value, 2.507314166123803)

        # #3: 0 < alpha < 1. This jest the most complex region of code to cover,
        # jako there are multiple if-inaczej statements. Let's take a look at the
        # source code, oraz determine the values that we need accordingly:
        #
        # dopóki 1:
        #     u = random()
        #     b = (_e + alpha)/_e
        #     p = b*u
        #     jeżeli p <= 1.0: # <=== (A)
        #         x = p ** (1.0/alpha)
        #     inaczej: # <=== (B)
        #         x = -_log((b-p)/alpha)
        #     u1 = random()
        #     jeżeli p > 1.0: # <=== (C)
        #         jeżeli u1 <= x ** (alpha - 1.0): # <=== (D)
        #             przerwij
        #     albo_inaczej u1 <= _exp(-x): # <=== (E)
        #         przerwij
        # zwróć x * beta
        #
        # First, we want (A) to be Prawda. For that we need that:
        # b*random() <= 1.0
        # r1 = random() <= 1.0 / b
        #
        # We now get to the second if-inaczej branch, oraz here, since p <= 1.0,
        # (C) jest Nieprawda oraz we take the albo_inaczej branch, (E). For it to be Prawda,
        # so that the przerwij jest executed, we need that:
        # r2 = random() <= _exp(-x)
        # r2 <= _exp(-(p ** (1.0/alpha)))
        # r2 <= _exp(-((b*r1) ** (1.0/alpha)))

        _e = random._e
        _exp = random._exp
        _log = random._log
        alpha = 0.35
        beta = 1.45
        b = (_e + alpha)/_e
        epsilon = 0.01

        r1 = 0.8859296441566 # 1.0 / b
        r2 = 0.3678794411714 # _exp(-((b*r1) ** (1.0/alpha)))

        # These four "random" values result w the following trace:
        # (A) Prawda, (E) Nieprawda --> [next iteration of while]
        # (A) Prawda, (E) Prawda --> [dopóki loop przerwijs]
        random_mock.side_effect = [r1, r2 + epsilon, r1, r2]
        returned_value = random.gammavariate(alpha, beta)
        self.assertAlmostEqual(returned_value, 1.4499999999997544)

        # Let's now make (A) be Nieprawda. If this jest the case, when we get to the
        # second if-inaczej 'p' jest greater than 1, so (C) evaluates to Prawda. We
        # now encounter a second jeżeli statement, (D), which w order to execute
        # must satisfy the following condition:
        # r2 <= x ** (alpha - 1.0)
        # r2 <= (-_log((b-p)/alpha)) ** (alpha - 1.0)
        # r2 <= (-_log((b-(b*r1))/alpha)) ** (alpha - 1.0)
        r1 = 0.8959296441566 # (1.0 / b) + epsilon -- so that (A) jest Nieprawda
        r2 = 0.9445400408898141

        # And these four values result w the following trace:
        # (B) oraz (C) Prawda, (D) Nieprawda --> [next iteration of while]
        # (B) oraz (C) Prawda, (D) Prawda [dopóki loop przerwijs]
        random_mock.side_effect = [r1, r2 + epsilon, r1, r2]
        returned_value = random.gammavariate(alpha, beta)
        self.assertAlmostEqual(returned_value, 1.5830349561760781)

    @unittest.mock.patch('random.Random.gammavariate')
    def test_betavariate_return_zero(self, gammavariate_mock):
        # betavariate() returns zero when the Gamma distribution
        # that it uses internally returns this same value.
        gammavariate_mock.return_value = 0.0
        self.assertEqual(0.0, random.betavariate(2.71828, 3.14159))

klasa TestModule(unittest.TestCase):
    def testMagicConstants(self):
        self.assertAlmostEqual(random.NV_MAGICCONST, 1.71552776992141)
        self.assertAlmostEqual(random.TWOPI, 6.28318530718)
        self.assertAlmostEqual(random.LOG4, 1.38629436111989)
        self.assertAlmostEqual(random.SG_MAGICCONST, 2.50407739677627)

    def test__all__(self):
        # tests validity but nie completeness of the __all__ list
        self.assertPrawda(set(random.__all__) <= set(dir(random)))

    def test_random_subclass_with_kwargs(self):
        # SF bug #1486663 -- this used to erroneously podnieś a TypeError
        klasa Subclass(random.Random):
            def __init__(self, newarg=Nic):
                random.Random.__init__(self)
        Subclass(newarg=1)


jeżeli __name__ == "__main__":
    unittest.main()
