##  Module statistics.py
##
##  Copyright (c) 2013 Steven D'Aprano <steve+python@pearwood.info>.
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may nie use this file wyjąwszy w compliance przy the License.
##  You may obtain a copy of the License at
##
##  http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law albo agreed to w writing, software
##  distributed under the License jest distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express albo implied.
##  See the License dla the specific language governing permissions oraz
##  limitations under the License.


"""
Basic statistics module.

This module provides functions dla calculating statistics of data, including
averages, variance, oraz standard deviation.

Calculating averages
--------------------

==================  =============================================
Function            Description
==================  =============================================
mean                Arithmetic mean (average) of data.
median              Median (middle value) of data.
median_low          Low median of data.
median_high         High median of data.
median_grouped      Median, albo 50th percentile, of grouped data.
mode                Mode (most common value) of data.
==================  =============================================

Calculate the arithmetic mean ("the average") of data:

>>> mean([-1.0, 2.5, 3.25, 5.75])
2.625


Calculate the standard median of discrete data:

>>> median([2, 3, 4, 5])
3.5


Calculate the median, albo 50th percentile, of data grouped into klasa intervals
centred on the data values provided. E.g. jeżeli your data points are rounded to
the nearest whole number:

>>> median_grouped([2, 2, 3, 3, 3, 4])  #doctest: +ELLIPSIS
2.8333333333...

This should be interpreted w this way: you have two data points w the class
interval 1.5-2.5, three data points w the klasa interval 2.5-3.5, oraz one w
the klasa interval 3.5-4.5. The median of these data points jest 2.8333...


Calculating variability albo spread
---------------------------------

==================  =============================================
Function            Description
==================  =============================================
pvariance           Population variance of data.
variance            Sample variance of data.
pstdev              Population standard deviation of data.
stdev               Sample standard deviation of data.
==================  =============================================

Calculate the standard deviation of sample data:

>>> stdev([2.5, 3.25, 5.5, 11.25, 11.75])  #doctest: +ELLIPSIS
4.38961843444...

If you have previously calculated the mean, you can dalej it jako the optional
second argument to the four "spread" functions to avoid recalculating it:

>>> data = [1, 2, 2, 4, 4, 4, 5, 6]
>>> mu = mean(data)
>>> pvariance(data, mu)
2.5


Exceptions
----------

A single exception jest defined: StatisticsError jest a subclass of ValueError.

"""

__all__ = [ 'StatisticsError',
            'pstdev', 'pvariance', 'stdev', 'variance',
            'median',  'median_low', 'median_high', 'median_grouped',
            'mean', 'mode',
          ]


zaimportuj collections
zaimportuj math

z fractions zaimportuj Fraction
z decimal zaimportuj Decimal


# === Exceptions ===

klasa StatisticsError(ValueError):
    dalej


# === Private utilities ===

def _sum(data, start=0):
    """_sum(data [, start]) -> value

    Return a high-precision sum of the given numeric data. If optional
    argument ``start`` jest given, it jest added to the total. If ``data`` jest
    empty, ``start`` (defaulting to 0) jest returned.


    Examples
    --------

    >>> _sum([3, 2.25, 4.5, -0.5, 1.0], 0.75)
    11.0

    Some sources of round-off error will be avoided:

    >>> _sum([1e50, 1, -1e50] * 1000)  # Built-in sum returns zero.
    1000.0

    Fractions oraz Decimals are also supported:

    >>> z fractions zaimportuj Fraction jako F
    >>> _sum([F(2, 3), F(7, 5), F(1, 4), F(5, 6)])
    Fraction(63, 20)

    >>> z decimal zaimportuj Decimal jako D
    >>> data = [D("0.1375"), D("0.2108"), D("0.3061"), D("0.0419")]
    >>> _sum(data)
    Decimal('0.6963')

    Mixed types are currently treated jako an error, wyjąwszy that int jest
    allowed.
    """
    # We fail jako soon jako we reach a value that jest nie an int albo the type of
    # the first value which jest nie an int. E.g. _sum([int, int, float, int])
    # jest okay, but sum([int, int, float, Fraction]) jest not.
    allowed_types = {int, type(start)}
    n, d = _exact_ratio(start)
    partials = {d: n}  # map {denominator: sum of numerators}
    # Micro-optimizations.
    exact_ratio = _exact_ratio
    partials_get = partials.get
    # Add numerators dla each denominator.
    dla x w data:
        _check_type(type(x), allowed_types)
        n, d = exact_ratio(x)
        partials[d] = partials_get(d, 0) + n
    # Find the expected result type. If allowed_types has only one item, it
    # will be int; jeżeli it has two, use the one which isn't int.
    assert len(allowed_types) w (1, 2)
    jeżeli len(allowed_types) == 1:
        assert allowed_types.pop() jest int
        T = int
    inaczej:
        T = (allowed_types - {int}).pop()
    jeżeli Nic w partials:
        assert issubclass(T, (float, Decimal))
        assert nie math.isfinite(partials[Nic])
        zwróć T(partials[Nic])
    total = Fraction()
    dla d, n w sorted(partials.items()):
        total += Fraction(n, d)
    jeżeli issubclass(T, int):
        assert total.denominator == 1
        zwróć T(total.numerator)
    jeżeli issubclass(T, Decimal):
        zwróć T(total.numerator)/total.denominator
    zwróć T(total)


def _check_type(T, allowed):
    jeżeli T nie w allowed:
        jeżeli len(allowed) == 1:
            allowed.add(T)
        inaczej:
            types = ', '.join([t.__name__ dla t w allowed] + [T.__name__])
            podnieś TypeError("unsupported mixed types: %s" % types)


def _exact_ratio(x):
    """Convert Real number x exactly to (numerator, denominator) pair.

    >>> _exact_ratio(0.25)
    (1, 4)

    x jest expected to be an int, Fraction, Decimal albo float.
    """
    spróbuj:
        spróbuj:
            # int, Fraction
            zwróć (x.numerator, x.denominator)
        wyjąwszy AttributeError:
            # float
            spróbuj:
                zwróć x.as_integer_ratio()
            wyjąwszy AttributeError:
                # Decimal
                spróbuj:
                    zwróć _decimal_to_ratio(x)
                wyjąwszy AttributeError:
                    msg = "can't convert type '{}' to numerator/denominator"
                    podnieś TypeError(msg.format(type(x).__name__)) z Nic
    wyjąwszy (OverflowError, ValueError):
        # INF albo NAN
        jeżeli __debug__:
            # Decimal signalling NANs cannot be converted to float :-(
            jeżeli isinstance(x, Decimal):
                assert nie x.is_finite()
            inaczej:
                assert nie math.isfinite(x)
        zwróć (x, Nic)


# FIXME This jest faster than Fraction.from_decimal, but still too slow.
def _decimal_to_ratio(d):
    """Convert Decimal d to exact integer ratio (numerator, denominator).

    >>> z decimal zaimportuj Decimal
    >>> _decimal_to_ratio(Decimal("2.6"))
    (26, 10)

    """
    sign, digits, exp = d.as_tuple()
    jeżeli exp w ('F', 'n', 'N'):  # INF, NAN, sNAN
        assert nie d.is_finite()
        podnieś ValueError
    num = 0
    dla digit w digits:
        num = num*10 + digit
    jeżeli exp < 0:
        den = 10**-exp
    inaczej:
        num *= 10**exp
        den = 1
    jeżeli sign:
        num = -num
    zwróć (num, den)


def _counts(data):
    # Generate a table of sorted (value, frequency) pairs.
    table = collections.Counter(iter(data)).most_common()
    jeżeli nie table:
        zwróć table
    # Extract the values przy the highest frequency.
    maxfreq = table[0][1]
    dla i w range(1, len(table)):
        jeżeli table[i][1] != maxfreq:
            table = table[:i]
            przerwij
    zwróć table


# === Measures of central tendency (averages) ===

def mean(data):
    """Return the sample arithmetic mean of data.

    >>> mean([1, 2, 3, 4, 4])
    2.8

    >>> z fractions zaimportuj Fraction jako F
    >>> mean([F(3, 7), F(1, 21), F(5, 3), F(1, 3)])
    Fraction(13, 21)

    >>> z decimal zaimportuj Decimal jako D
    >>> mean([D("0.5"), D("0.75"), D("0.625"), D("0.375")])
    Decimal('0.5625')

    If ``data`` jest empty, StatisticsError will be podnieśd.
    """
    jeżeli iter(data) jest data:
        data = list(data)
    n = len(data)
    jeżeli n < 1:
        podnieś StatisticsError('mean requires at least one data point')
    zwróć _sum(data)/n


# FIXME: investigate ways to calculate medians without sorting? Quickselect?
def median(data):
    """Return the median (middle value) of numeric data.

    When the number of data points jest odd, zwróć the middle data point.
    When the number of data points jest even, the median jest interpolated by
    taking the average of the two middle values:

    >>> median([1, 3, 5])
    3
    >>> median([1, 3, 5, 7])
    4.0

    """
    data = sorted(data)
    n = len(data)
    jeżeli n == 0:
        podnieś StatisticsError("no median dla empty data")
    jeżeli n%2 == 1:
        zwróć data[n//2]
    inaczej:
        i = n//2
        zwróć (data[i - 1] + data[i])/2


def median_low(data):
    """Return the low median of numeric data.

    When the number of data points jest odd, the middle value jest returned.
    When it jest even, the smaller of the two middle values jest returned.

    >>> median_low([1, 3, 5])
    3
    >>> median_low([1, 3, 5, 7])
    3

    """
    data = sorted(data)
    n = len(data)
    jeżeli n == 0:
        podnieś StatisticsError("no median dla empty data")
    jeżeli n%2 == 1:
        zwróć data[n//2]
    inaczej:
        zwróć data[n//2 - 1]


def median_high(data):
    """Return the high median of data.

    When the number of data points jest odd, the middle value jest returned.
    When it jest even, the larger of the two middle values jest returned.

    >>> median_high([1, 3, 5])
    3
    >>> median_high([1, 3, 5, 7])
    5

    """
    data = sorted(data)
    n = len(data)
    jeżeli n == 0:
        podnieś StatisticsError("no median dla empty data")
    zwróć data[n//2]


def median_grouped(data, interval=1):
    """"Return the 50th percentile (median) of grouped continuous data.

    >>> median_grouped([1, 2, 2, 3, 4, 4, 4, 4, 4, 5])
    3.7
    >>> median_grouped([52, 52, 53, 54])
    52.5

    This calculates the median jako the 50th percentile, oraz should be
    used when your data jest continuous oraz grouped. In the above example,
    the values 1, 2, 3, etc. actually represent the midpoint of classes
    0.5-1.5, 1.5-2.5, 2.5-3.5, etc. The middle value falls somewhere w
    klasa 3.5-4.5, oraz interpolation jest used to estimate it.

    Optional argument ``interval`` represents the klasa interval, oraz
    defaults to 1. Changing the klasa interval naturally will change the
    interpolated 50th percentile value:

    >>> median_grouped([1, 3, 3, 5, 7], interval=1)
    3.25
    >>> median_grouped([1, 3, 3, 5, 7], interval=2)
    3.5

    This function does nie check whether the data points are at least
    ``interval`` apart.
    """
    data = sorted(data)
    n = len(data)
    jeżeli n == 0:
        podnieś StatisticsError("no median dla empty data")
    albo_inaczej n == 1:
        zwróć data[0]
    # Find the value at the midpoint. Remember this corresponds to the
    # centre of the klasa interval.
    x = data[n//2]
    dla obj w (x, interval):
        jeżeli isinstance(obj, (str, bytes)):
            podnieś TypeError('expected number but got %r' % obj)
    spróbuj:
        L = x - interval/2  # The lower limit of the median interval.
    wyjąwszy TypeError:
        # Mixed type. For now we just coerce to float.
        L = float(x) - float(interval)/2
    cf = data.index(x)  # Number of values below the median interval.
    # FIXME The following line could be more efficient dla big lists.
    f = data.count(x)  # Number of data points w the median interval.
    zwróć L + interval*(n/2 - cf)/f


def mode(data):
    """Return the most common data point z discrete albo nominal data.

    ``mode`` assumes discrete data, oraz returns a single value. This jest the
    standard treatment of the mode jako commonly taught w schools:

    >>> mode([1, 1, 2, 3, 3, 3, 3, 4])
    3

    This also works przy nominal (non-numeric) data:

    >>> mode(["red", "blue", "blue", "red", "green", "red", "red"])
    'red'

    If there jest nie exactly one most common value, ``mode`` will podnieś
    StatisticsError.
    """
    # Generate a table of sorted (value, frequency) pairs.
    table = _counts(data)
    jeżeli len(table) == 1:
        zwróć table[0][0]
    albo_inaczej table:
        podnieś StatisticsError(
                'no unique mode; found %d equally common values' % len(table)
                )
    inaczej:
        podnieś StatisticsError('no mode dla empty data')


# === Measures of spread ===

# See http://mathworld.wolfram.com/Variance.html
#     http://mathworld.wolfram.com/SampleVariance.html
#     http://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
#
# Under no circumstances use the so-called "computational formula for
# variance", jako that jest only suitable dla hand calculations przy a small
# amount of low-precision data. It has terrible numeric properties.
#
# See a comparison of three computational methods here:
# http://www.johndcook.com/blog/2008/09/26/comparing-three-methods-of-computing-standard-deviation/

def _ss(data, c=Nic):
    """Return sum of square deviations of sequence data.

    If ``c`` jest Nic, the mean jest calculated w one dalej, oraz the deviations
    z the mean are calculated w a second dalej. Otherwise, deviations are
    calculated z ``c`` jako given. Use the second case przy care, jako it can
    lead to garbage results.
    """
    jeżeli c jest Nic:
        c = mean(data)
    ss = _sum((x-c)**2 dla x w data)
    # The following sum should mathematically equal zero, but due to rounding
    # error may not.
    ss -= _sum((x-c) dla x w data)**2/len(data)
    assert nie ss < 0, 'negative sum of square deviations: %f' % ss
    zwróć ss


def variance(data, xbar=Nic):
    """Return the sample variance of data.

    data should be an iterable of Real-valued numbers, przy at least two
    values. The optional argument xbar, jeżeli given, should be the mean of
    the data. If it jest missing albo Nic, the mean jest automatically calculated.

    Use this function when your data jest a sample z a population. To
    calculate the variance z the entire population, see ``pvariance``.

    Examples:

    >>> data = [2.75, 1.75, 1.25, 0.25, 0.5, 1.25, 3.5]
    >>> variance(data)
    1.3720238095238095

    If you have already calculated the mean of your data, you can dalej it as
    the optional second argument ``xbar`` to avoid recalculating it:

    >>> m = mean(data)
    >>> variance(data, m)
    1.3720238095238095

    This function does nie check that ``xbar`` jest actually the mean of
    ``data``. Giving arbitrary values dla ``xbar`` may lead to invalid albo
    impossible results.

    Decimals oraz Fractions are supported:

    >>> z decimal zaimportuj Decimal jako D
    >>> variance([D("27.5"), D("30.25"), D("30.25"), D("34.5"), D("41.75")])
    Decimal('31.01875')

    >>> z fractions zaimportuj Fraction jako F
    >>> variance([F(1, 6), F(1, 2), F(5, 3)])
    Fraction(67, 108)

    """
    jeżeli iter(data) jest data:
        data = list(data)
    n = len(data)
    jeżeli n < 2:
        podnieś StatisticsError('variance requires at least two data points')
    ss = _ss(data, xbar)
    zwróć ss/(n-1)


def pvariance(data, mu=Nic):
    """Return the population variance of ``data``.

    data should be an iterable of Real-valued numbers, przy at least one
    value. The optional argument mu, jeżeli given, should be the mean of
    the data. If it jest missing albo Nic, the mean jest automatically calculated.

    Use this function to calculate the variance z the entire population.
    To estimate the variance z a sample, the ``variance`` function jest
    usually a better choice.

    Examples:

    >>> data = [0.0, 0.25, 0.25, 1.25, 1.5, 1.75, 2.75, 3.25]
    >>> pvariance(data)
    1.25

    If you have already calculated the mean of the data, you can dalej it as
    the optional second argument to avoid recalculating it:

    >>> mu = mean(data)
    >>> pvariance(data, mu)
    1.25

    This function does nie check that ``mu`` jest actually the mean of ``data``.
    Giving arbitrary values dla ``mu`` may lead to invalid albo impossible
    results.

    Decimals oraz Fractions are supported:

    >>> z decimal zaimportuj Decimal jako D
    >>> pvariance([D("27.5"), D("30.25"), D("30.25"), D("34.5"), D("41.75")])
    Decimal('24.815')

    >>> z fractions zaimportuj Fraction jako F
    >>> pvariance([F(1, 4), F(5, 4), F(1, 2)])
    Fraction(13, 72)

    """
    jeżeli iter(data) jest data:
        data = list(data)
    n = len(data)
    jeżeli n < 1:
        podnieś StatisticsError('pvariance requires at least one data point')
    ss = _ss(data, mu)
    zwróć ss/n


def stdev(data, xbar=Nic):
    """Return the square root of the sample variance.

    See ``variance`` dla arguments oraz other details.

    >>> stdev([1.5, 2.5, 2.5, 2.75, 3.25, 4.75])
    1.0810874155219827

    """
    var = variance(data, xbar)
    spróbuj:
        zwróć var.sqrt()
    wyjąwszy AttributeError:
        zwróć math.sqrt(var)


def pstdev(data, mu=Nic):
    """Return the square root of the population variance.

    See ``pvariance`` dla arguments oraz other details.

    >>> pstdev([1.5, 2.5, 2.5, 2.75, 3.25, 4.75])
    0.986893273527251

    """
    var = pvariance(data, mu)
    spróbuj:
        zwróć var.sqrt()
    wyjąwszy AttributeError:
        zwróć math.sqrt(var)
