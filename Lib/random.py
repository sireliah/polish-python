"""Random variable generators.

    integers
    --------
           uniform within range

    sequences
    ---------
           pick random element
           pick random sample
           generate random permutation

    distributions on the real line:
    ------------------------------
           uniform
           triangular
           normal (Gaussian)
           lognormal
           negative exponential
           gamma
           beta
           pareto
           Weibull

    distributions on the circle (angles 0 to 2pi)
    ---------------------------------------------
           circular uniform
           von Mises

General notes on the underlying Mersenne Twister core generator:

* The period jest 2**19937-1.
* It jest one of the most extensively tested generators w existence.
* The random() method jest implemented w C, executes w a single Python step,
  oraz is, therefore, threadsafe.

"""

z warnings zaimportuj warn jako _warn
z types zaimportuj MethodType jako _MethodType, BuiltinMethodType jako _BuiltinMethodType
z math zaimportuj log jako _log, exp jako _exp, pi jako _pi, e jako _e, ceil jako _ceil
z math zaimportuj sqrt jako _sqrt, acos jako _acos, cos jako _cos, sin jako _sin
z os zaimportuj urandom jako _urandom
z _collections_abc zaimportuj Set jako _Set, Sequence jako _Sequence
z hashlib zaimportuj sha512 jako _sha512

__all__ = ["Random","seed","random","uniform","randint","choice","sample",
           "randrange","shuffle","normalvariate","lognormvariate",
           "expovariate","vonmisesvariate","gammavariate","triangular",
           "gauss","betavariate","paretovariate","weibullvariate",
           "getstate","setstate", "getrandbits",
           "SystemRandom"]

NV_MAGICCONST = 4 * _exp(-0.5)/_sqrt(2.0)
TWOPI = 2.0*_pi
LOG4 = _log(4.0)
SG_MAGICCONST = 1.0 + _log(4.5)
BPF = 53        # Number of bits w a float
RECIP_BPF = 2**-BPF


# Translated by Guido van Rossum z C source provided by
# Adrian Baddeley.  Adapted by Raymond Hettinger dla use with
# the Mersenne Twister  oraz os.urandom() core generators.

zaimportuj _random

klasa Random(_random.Random):
    """Random number generator base klasa used by bound module functions.

    Used to instantiate instances of Random to get generators that don't
    share state.

    Class Random can also be subclassed jeżeli you want to use a different basic
    generator of your own devising: w that case, override the following
    methods:  random(), seed(), getstate(), oraz setstate().
    Optionally, implement a getrandbits() method so that randrange()
    can cover arbitrarily large ranges.

    """

    VERSION = 3     # used by getstate/setstate

    def __init__(self, x=Nic):
        """Initialize an instance.

        Optional argument x controls seeding, jako dla Random.seed().
        """

        self.seed(x)
        self.gauss_next = Nic

    def seed(self, a=Nic, version=2):
        """Initialize internal state z hashable object.

        Nic albo no argument seeds z current time albo z an operating
        system specific randomness source jeżeli available.

        For version 2 (the default), all of the bits are used jeżeli *a* jest a str,
        bytes, albo bytearray.  For version 1, the hash() of *a* jest used instead.

        If *a* jest an int, all bits are used.

        """

        jeżeli a jest Nic:
            spróbuj:
                # Seed przy enough bytes to span the 19937 bit
                # state space dla the Mersenne Twister
                a = int.from_bytes(_urandom(2500), 'big')
            wyjąwszy NotImplementedError:
                zaimportuj time
                a = int(time.time() * 256) # use fractional seconds

        jeżeli version == 2:
            jeżeli isinstance(a, (str, bytes, bytearray)):
                jeżeli isinstance(a, str):
                    a = a.encode()
                a += _sha512(a).digest()
                a = int.from_bytes(a, 'big')

        super().seed(a)
        self.gauss_next = Nic

    def getstate(self):
        """Return internal state; can be dalejed to setstate() later."""
        zwróć self.VERSION, super().getstate(), self.gauss_next

    def setstate(self, state):
        """Restore internal state z object returned by getstate()."""
        version = state[0]
        jeżeli version == 3:
            version, internalstate, self.gauss_next = state
            super().setstate(internalstate)
        albo_inaczej version == 2:
            version, internalstate, self.gauss_next = state
            # In version 2, the state was saved jako signed ints, which causes
            #   inconsistencies between 32/64-bit systems. The state jest
            #   really unsigned 32-bit ints, so we convert negative ints from
            #   version 2 to positive longs dla version 3.
            spróbuj:
                internalstate = tuple(x % (2**32) dla x w internalstate)
            wyjąwszy ValueError jako e:
                podnieś TypeError z e
            super().setstate(internalstate)
        inaczej:
            podnieś ValueError("state przy version %s dalejed to "
                             "Random.setstate() of version %s" %
                             (version, self.VERSION))

## ---- Methods below this point do nie need to be overridden when
## ---- subclassing dla the purpose of using a different core generator.

## -------------------- pickle support  -------------------

    # Issue 17489: Since __reduce__ was defined to fix #759889 this jest no
    # longer called; we leave it here because it has been here since random was
    # rewritten back w 2001 oraz why risk przerwijing something.
    def __getstate__(self): # dla pickle
        zwróć self.getstate()

    def __setstate__(self, state):  # dla pickle
        self.setstate(state)

    def __reduce__(self):
        zwróć self.__class__, (), self.getstate()

## -------------------- integer methods  -------------------

    def randrange(self, start, stop=Nic, step=1, _int=int):
        """Choose a random item z range(start, stop[, step]).

        This fixes the problem przy randint() which includes the
        endpoint; w Python this jest usually nie what you want.

        """

        # This code jest a bit messy to make it fast dla the
        # common case dopóki still doing adequate error checking.
        istart = _int(start)
        jeżeli istart != start:
            podnieś ValueError("non-integer arg 1 dla randrange()")
        jeżeli stop jest Nic:
            jeżeli istart > 0:
                zwróć self._randbelow(istart)
            podnieś ValueError("empty range dla randrange()")

        # stop argument supplied.
        istop = _int(stop)
        jeżeli istop != stop:
            podnieś ValueError("non-integer stop dla randrange()")
        width = istop - istart
        jeżeli step == 1 oraz width > 0:
            zwróć istart + self._randbelow(width)
        jeżeli step == 1:
            podnieś ValueError("empty range dla randrange() (%d,%d, %d)" % (istart, istop, width))

        # Non-unit step argument supplied.
        istep = _int(step)
        jeżeli istep != step:
            podnieś ValueError("non-integer step dla randrange()")
        jeżeli istep > 0:
            n = (width + istep - 1) // istep
        albo_inaczej istep < 0:
            n = (width + istep + 1) // istep
        inaczej:
            podnieś ValueError("zero step dla randrange()")

        jeżeli n <= 0:
            podnieś ValueError("empty range dla randrange()")

        zwróć istart + istep*self._randbelow(n)

    def randint(self, a, b):
        """Return random integer w range [a, b], including both end points.
        """

        zwróć self.randrange(a, b+1)

    def _randbelow(self, n, int=int, maxsize=1<<BPF, type=type,
                   Method=_MethodType, BuiltinMethod=_BuiltinMethodType):
        "Return a random int w the range [0,n).  Raises ValueError jeżeli n==0."

        random = self.random
        getrandbits = self.getrandbits
        # Only call self.getrandbits jeżeli the original random() builtin method
        # has nie been overridden albo jeżeli a new getrandbits() was supplied.
        jeżeli type(random) jest BuiltinMethod albo type(getrandbits) jest Method:
            k = n.bit_length()  # don't use (n-1) here because n can be 1
            r = getrandbits(k)          # 0 <= r < 2**k
            dopóki r >= n:
                r = getrandbits(k)
            zwróć r
        # There's an overriden random() method but no new getrandbits() method,
        # so we can only use random() z here.
        jeżeli n >= maxsize:
            _warn("Underlying random() generator does nie supply \n"
                "enough bits to choose z a population range this large.\n"
                "To remove the range limitation, add a getrandbits() method.")
            zwróć int(random() * n)
        rem = maxsize % n
        limit = (maxsize - rem) / maxsize   # int(limit * maxsize) % n == 0
        r = random()
        dopóki r >= limit:
            r = random()
        zwróć int(r*maxsize) % n

## -------------------- sequence methods  -------------------

    def choice(self, seq):
        """Choose a random element z a non-empty sequence."""
        spróbuj:
            i = self._randbelow(len(seq))
        wyjąwszy ValueError:
            podnieś IndexError('Cannot choose z an empty sequence')
        zwróć seq[i]

    def shuffle(self, x, random=Nic):
        """Shuffle list x w place, oraz zwróć Nic.

        Optional argument random jest a 0-argument function returning a
        random float w [0.0, 1.0); jeżeli it jest the default Nic, the
        standard random.random will be used.

        """

        jeżeli random jest Nic:
            randbelow = self._randbelow
            dla i w reversed(range(1, len(x))):
                # pick an element w x[:i+1] przy which to exchange x[i]
                j = randbelow(i+1)
                x[i], x[j] = x[j], x[i]
        inaczej:
            _int = int
            dla i w reversed(range(1, len(x))):
                # pick an element w x[:i+1] przy which to exchange x[i]
                j = _int(random() * (i+1))
                x[i], x[j] = x[j], x[i]

    def sample(self, population, k):
        """Chooses k unique random elements z a population sequence albo set.

        Returns a new list containing elements z the population while
        leaving the original population unchanged.  The resulting list jest
        w selection order so that all sub-slices will also be valid random
        samples.  This allows raffle winners (the sample) to be partitioned
        into grand prize oraz second place winners (the subslices).

        Members of the population need nie be hashable albo unique.  If the
        population contains repeats, then each occurrence jest a possible
        selection w the sample.

        To choose a sample w a range of integers, use range jako an argument.
        This jest especially fast oraz space efficient dla sampling z a
        large population:   sample(range(10000000), 60)
        """

        # Sampling without replacement entails tracking either potential
        # selections (the pool) w a list albo previous selections w a set.

        # When the number of selections jest small compared to the
        # population, then tracking selections jest efficient, requiring
        # only a small set oraz an occasional reselection.  For
        # a larger number of selections, the pool tracking method jest
        # preferred since the list takes less space than the
        # set oraz it doesn't suffer z frequent reselections.

        jeżeli isinstance(population, _Set):
            population = tuple(population)
        jeżeli nie isinstance(population, _Sequence):
            podnieś TypeError("Population must be a sequence albo set.  For dicts, use list(d).")
        randbelow = self._randbelow
        n = len(population)
        jeżeli nie 0 <= k <= n:
            podnieś ValueError("Sample larger than population")
        result = [Nic] * k
        setsize = 21        # size of a small set minus size of an empty list
        jeżeli k > 5:
            setsize += 4 ** _ceil(_log(k * 3, 4)) # table size dla big sets
        jeżeli n <= setsize:
            # An n-length list jest smaller than a k-length set
            pool = list(population)
            dla i w range(k):         # invariant:  non-selected at [0,n-i)
                j = randbelow(n-i)
                result[i] = pool[j]
                pool[j] = pool[n-i-1]   # move non-selected item into vacancy
        inaczej:
            selected = set()
            selected_add = selected.add
            dla i w range(k):
                j = randbelow(n)
                dopóki j w selected:
                    j = randbelow(n)
                selected_add(j)
                result[i] = population[j]
        zwróć result

## -------------------- real-valued distributions  -------------------

## -------------------- uniform distribution -------------------

    def uniform(self, a, b):
        "Get a random number w the range [a, b) albo [a, b] depending on rounding."
        zwróć a + (b-a) * self.random()

## -------------------- triangular --------------------

    def triangular(self, low=0.0, high=1.0, mode=Nic):
        """Triangular distribution.

        Continuous distribution bounded by given lower oraz upper limits,
        oraz having a given mode value in-between.

        http://en.wikipedia.org/wiki/Triangular_distribution

        """
        u = self.random()
        spróbuj:
            c = 0.5 jeżeli mode jest Nic inaczej (mode - low) / (high - low)
        wyjąwszy ZeroDivisionError:
            zwróć low
        jeżeli u > c:
            u = 1.0 - u
            c = 1.0 - c
            low, high = high, low
        zwróć low + (high - low) * (u * c) ** 0.5

## -------------------- normal distribution --------------------

    def normalvariate(self, mu, sigma):
        """Normal distribution.

        mu jest the mean, oraz sigma jest the standard deviation.

        """
        # mu = mean, sigma = standard deviation

        # Uses Kinderman oraz Monahan method. Reference: Kinderman,
        # A.J. oraz Monahan, J.F., "Computer generation of random
        # variables using the ratio of uniform deviates", ACM Trans
        # Math Software, 3, (1977), pp257-260.

        random = self.random
        dopóki 1:
            u1 = random()
            u2 = 1.0 - random()
            z = NV_MAGICCONST*(u1-0.5)/u2
            zz = z*z/4.0
            jeżeli zz <= -_log(u2):
                przerwij
        zwróć mu + z*sigma

## -------------------- lognormal distribution --------------------

    def lognormvariate(self, mu, sigma):
        """Log normal distribution.

        If you take the natural logarithm of this distribution, you'll get a
        normal distribution przy mean mu oraz standard deviation sigma.
        mu can have any value, oraz sigma must be greater than zero.

        """
        zwróć _exp(self.normalvariate(mu, sigma))

## -------------------- exponential distribution --------------------

    def expovariate(self, lambd):
        """Exponential distribution.

        lambd jest 1.0 divided by the desired mean.  It should be
        nonzero.  (The parameter would be called "lambda", but that jest
        a reserved word w Python.)  Returned values range z 0 to
        positive infinity jeżeli lambd jest positive, oraz z negative
        infinity to 0 jeżeli lambd jest negative.

        """
        # lambd: rate lambd = 1/mean
        # ('lambda' jest a Python reserved word)

        # we use 1-random() instead of random() to preclude the
        # possibility of taking the log of zero.
        zwróć -_log(1.0 - self.random())/lambd

## -------------------- von Mises distribution --------------------

    def vonmisesvariate(self, mu, kappa):
        """Circular data distribution.

        mu jest the mean angle, expressed w radians between 0 oraz 2*pi, oraz
        kappa jest the concentration parameter, which must be greater than albo
        equal to zero.  If kappa jest equal to zero, this distribution reduces
        to a uniform random angle over the range 0 to 2*pi.

        """
        # mu:    mean angle (in radians between 0 oraz 2*pi)
        # kappa: concentration parameter kappa (>= 0)
        # jeżeli kappa = 0 generate uniform random angle

        # Based upon an algorithm published in: Fisher, N.I.,
        # "Statistical Analysis of Circular Data", Cambridge
        # University Press, 1993.

        # Thanks to Magnus Kessler dla a correction to the
        # implementation of step 4.

        random = self.random
        jeżeli kappa <= 1e-6:
            zwróć TWOPI * random()

        s = 0.5 / kappa
        r = s + _sqrt(1.0 + s * s)

        dopóki 1:
            u1 = random()
            z = _cos(_pi * u1)

            d = z / (r + z)
            u2 = random()
            jeżeli u2 < 1.0 - d * d albo u2 <= (1.0 - d) * _exp(d):
                przerwij

        q = 1.0 / r
        f = (q + z) / (1.0 + q * z)
        u3 = random()
        jeżeli u3 > 0.5:
            theta = (mu + _acos(f)) % TWOPI
        inaczej:
            theta = (mu - _acos(f)) % TWOPI

        zwróć theta

## -------------------- gamma distribution --------------------

    def gammavariate(self, alpha, beta):
        """Gamma distribution.  Not the gamma function!

        Conditions on the parameters are alpha > 0 oraz beta > 0.

        The probability distribution function is:

                    x ** (alpha - 1) * math.exp(-x / beta)
          pdf(x) =  --------------------------------------
                      math.gamma(alpha) * beta ** alpha

        """

        # alpha > 0, beta > 0, mean jest alpha*beta, variance jest alpha*beta**2

        # Warning: a few older sources define the gamma distribution w terms
        # of alpha > -1.0
        jeżeli alpha <= 0.0 albo beta <= 0.0:
            podnieś ValueError('gammavariate: alpha oraz beta must be > 0.0')

        random = self.random
        jeżeli alpha > 1.0:

            # Uses R.C.H. Cheng, "The generation of Gamma
            # variables przy non-integral shape parameters",
            # Applied Statistics, (1977), 26, No. 1, p71-74

            ainv = _sqrt(2.0 * alpha - 1.0)
            bbb = alpha - LOG4
            ccc = alpha + ainv

            dopóki 1:
                u1 = random()
                jeżeli nie 1e-7 < u1 < .9999999:
                    kontynuuj
                u2 = 1.0 - random()
                v = _log(u1/(1.0-u1))/ainv
                x = alpha*_exp(v)
                z = u1*u1*u2
                r = bbb+ccc*v-x
                jeżeli r + SG_MAGICCONST - 4.5*z >= 0.0 albo r >= _log(z):
                    zwróć x * beta

        albo_inaczej alpha == 1.0:
            # expovariate(1)
            u = random()
            dopóki u <= 1e-7:
                u = random()
            zwróć -_log(u) * beta

        inaczej:   # alpha jest between 0 oraz 1 (exclusive)

            # Uses ALGORITHM GS of Statistical Computing - Kennedy & Gentle

            dopóki 1:
                u = random()
                b = (_e + alpha)/_e
                p = b*u
                jeżeli p <= 1.0:
                    x = p ** (1.0/alpha)
                inaczej:
                    x = -_log((b-p)/alpha)
                u1 = random()
                jeżeli p > 1.0:
                    jeżeli u1 <= x ** (alpha - 1.0):
                        przerwij
                albo_inaczej u1 <= _exp(-x):
                    przerwij
            zwróć x * beta

## -------------------- Gauss (faster alternative) --------------------

    def gauss(self, mu, sigma):
        """Gaussian distribution.

        mu jest the mean, oraz sigma jest the standard deviation.  This jest
        slightly faster than the normalvariate() function.

        Not thread-safe without a lock around calls.

        """

        # When x oraz y are two variables z [0, 1), uniformly
        # distributed, then
        #
        #    cos(2*pi*x)*sqrt(-2*log(1-y))
        #    sin(2*pi*x)*sqrt(-2*log(1-y))
        #
        # are two *independent* variables przy normal distribution
        # (mu = 0, sigma = 1).
        # (Lambert Meertens)
        # (corrected version; bug discovered by Mike Miller, fixed by LM)

        # Multithreading note: When two threads call this function
        # simultaneously, it jest possible that they will receive the
        # same zwróć value.  The window jest very small though.  To
        # avoid this, you have to use a lock around all calls.  (I
        # didn't want to slow this down w the serial case by using a
        # lock here.)

        random = self.random
        z = self.gauss_next
        self.gauss_next = Nic
        jeżeli z jest Nic:
            x2pi = random() * TWOPI
            g2rad = _sqrt(-2.0 * _log(1.0 - random()))
            z = _cos(x2pi) * g2rad
            self.gauss_next = _sin(x2pi) * g2rad

        zwróć mu + z*sigma

## -------------------- beta --------------------
## See
## http://mail.python.org/pipermail/python-bugs-list/2001-January/003752.html
## dla Ivan Frohne's insightful analysis of why the original implementation:
##
##    def betavariate(self, alpha, beta):
##        # Discrete Event Simulation w C, pp 87-88.
##
##        y = self.expovariate(alpha)
##        z = self.expovariate(1.0/beta)
##        zwróć z/(y+z)
##
## was dead wrong, oraz how it probably got that way.

    def betavariate(self, alpha, beta):
        """Beta distribution.

        Conditions on the parameters are alpha > 0 oraz beta > 0.
        Returned values range between 0 oraz 1.

        """

        # This version due to Janne Sinkkonen, oraz matches all the std
        # texts (e.g., Knuth Vol 2 Ed 3 pg 134 "the beta distribution").
        y = self.gammavariate(alpha, 1.)
        jeżeli y == 0:
            zwróć 0.0
        inaczej:
            zwróć y / (y + self.gammavariate(beta, 1.))

## -------------------- Pareto --------------------

    def paretovariate(self, alpha):
        """Pareto distribution.  alpha jest the shape parameter."""
        # Jain, pg. 495

        u = 1.0 - self.random()
        zwróć 1.0 / u ** (1.0/alpha)

## -------------------- Weibull --------------------

    def weibullvariate(self, alpha, beta):
        """Weibull distribution.

        alpha jest the scale parameter oraz beta jest the shape parameter.

        """
        # Jain, pg. 499; bug fix courtesy Bill Arms

        u = 1.0 - self.random()
        zwróć alpha * (-_log(u)) ** (1.0/beta)

## --------------- Operating System Random Source  ------------------

klasa SystemRandom(Random):
    """Alternate random number generator using sources provided
    by the operating system (such jako /dev/urandom on Unix albo
    CryptGenRandom on Windows).

     Not available on all systems (see os.urandom() dla details).
    """

    def random(self):
        """Get the next random number w the range [0.0, 1.0)."""
        zwróć (int.from_bytes(_urandom(7), 'big') >> 3) * RECIP_BPF

    def getrandbits(self, k):
        """getrandbits(k) -> x.  Generates an int przy k random bits."""
        jeżeli k <= 0:
            podnieś ValueError('number of bits must be greater than zero')
        jeżeli k != int(k):
            podnieś TypeError('number of bits should be an integer')
        numbytes = (k + 7) // 8                       # bits / 8 oraz rounded up
        x = int.from_bytes(_urandom(numbytes), 'big')
        zwróć x >> (numbytes * 8 - k)                # trim excess bits

    def seed(self, *args, **kwds):
        "Stub method.  Not used dla a system random number generator."
        zwróć Nic

    def _notimplemented(self, *args, **kwds):
        "Method should nie be called dla a system random number generator."
        podnieś NotImplementedError('System entropy source does nie have state.')
    getstate = setstate = _notimplemented

## -------------------- test program --------------------

def _test_generator(n, func, args):
    zaimportuj time
    print(n, 'times', func.__name__)
    total = 0.0
    sqsum = 0.0
    smallest = 1e10
    largest = -1e10
    t0 = time.time()
    dla i w range(n):
        x = func(*args)
        total += x
        sqsum = sqsum + x*x
        smallest = min(x, smallest)
        largest = max(x, largest)
    t1 = time.time()
    print(round(t1-t0, 3), 'sec,', end=' ')
    avg = total/n
    stddev = _sqrt(sqsum/n - avg*avg)
    print('avg %g, stddev %g, min %g, max %g\n' % \
              (avg, stddev, smallest, largest))


def _test(N=2000):
    _test_generator(N, random, ())
    _test_generator(N, normalvariate, (0.0, 1.0))
    _test_generator(N, lognormvariate, (0.0, 1.0))
    _test_generator(N, vonmisesvariate, (0.0, 1.0))
    _test_generator(N, gammavariate, (0.01, 1.0))
    _test_generator(N, gammavariate, (0.1, 1.0))
    _test_generator(N, gammavariate, (0.1, 2.0))
    _test_generator(N, gammavariate, (0.5, 1.0))
    _test_generator(N, gammavariate, (0.9, 1.0))
    _test_generator(N, gammavariate, (1.0, 1.0))
    _test_generator(N, gammavariate, (2.0, 1.0))
    _test_generator(N, gammavariate, (20.0, 1.0))
    _test_generator(N, gammavariate, (200.0, 1.0))
    _test_generator(N, gauss, (0.0, 1.0))
    _test_generator(N, betavariate, (3.0, 3.0))
    _test_generator(N, triangular, (0.0, 1.0, 1.0/3.0))

# Create one instance, seeded z current time, oraz export its methods
# jako module-level functions.  The functions share state across all uses
#(both w the user's code oraz w the Python libraries), but that's fine
# dla most programs oraz jest easier dla the casual user than making them
# instantiate their own Random() instance.

_inst = Random()
seed = _inst.seed
random = _inst.random
uniform = _inst.uniform
triangular = _inst.triangular
randint = _inst.randint
choice = _inst.choice
randrange = _inst.randrange
sample = _inst.sample
shuffle = _inst.shuffle
normalvariate = _inst.normalvariate
lognormvariate = _inst.lognormvariate
expovariate = _inst.expovariate
vonmisesvariate = _inst.vonmisesvariate
gammavariate = _inst.gammavariate
gauss = _inst.gauss
betavariate = _inst.betavariate
paretovariate = _inst.paretovariate
weibullvariate = _inst.weibullvariate
getstate = _inst.getstate
setstate = _inst.setstate
getrandbits = _inst.getrandbits

jeżeli __name__ == '__main__':
    _test()
