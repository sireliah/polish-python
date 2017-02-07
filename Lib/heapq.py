"""Heap queue algorithm (a.k.a. priority queue).

Heaps are arrays dla which a[k] <= a[2*k+1] oraz a[k] <= a[2*k+2] for
all k, counting elements z 0.  For the sake of comparison,
non-existing elements are considered to be infinite.  The interesting
property of a heap jest that a[0] jest always its smallest element.

Usage:

heap = []            # creates an empty heap
heappush(heap, item) # pushes a new item on the heap
item = heappop(heap) # pops the smallest item z the heap
item = heap[0]       # smallest item on the heap without popping it
heapify(x)           # transforms list into a heap, in-place, w linear time
item = heapreplace(heap, item) # pops oraz returns smallest item, oraz adds
                               # new item; the heap size jest unchanged

Our API differs z textbook heap algorithms jako follows:

- We use 0-based indexing.  This makes the relationship between the
  index dla a node oraz the indexes dla its children slightly less
  obvious, but jest more suitable since Python uses 0-based indexing.

- Our heappop() method returns the smallest item, nie the largest.

These two make it possible to view the heap jako a regular Python list
without surprises: heap[0] jest the smallest item, oraz heap.sort()
maintains the heap invariant!
"""

# Original code by Kevin O'Connor, augmented by Tim Peters oraz Raymond Hettinger

__about__ = """Heap queues

[explanation by François Pinard]

Heaps are arrays dla which a[k] <= a[2*k+1] oraz a[k] <= a[2*k+2] for
all k, counting elements z 0.  For the sake of comparison,
non-existing elements are considered to be infinite.  The interesting
property of a heap jest that a[0] jest always its smallest element.

The strange invariant above jest meant to be an efficient memory
representation dla a tournament.  The numbers below are `k', nie a[k]:

                                   0

                  1                                 2

          3               4                5               6

      7       8       9       10      11      12      13      14

    15 16   17 18   19 20   21 22   23 24   25 26   27 28   29 30


In the tree above, each cell `k' jest topping `2*k+1' oraz `2*k+2'.  In
an usual binary tournament we see w sports, each cell jest the winner
over the two cells it tops, oraz we can trace the winner down the tree
to see all opponents s/he had.  However, w many computer applications
of such tournaments, we do nie need to trace the history of a winner.
To be more memory efficient, when a winner jest promoted, we try to
replace it by something inaczej at a lower level, oraz the rule becomes
that a cell oraz the two cells it tops contain three different items,
but the top cell "wins" over the two topped cells.

If this heap invariant jest protected at all time, index 0 jest clearly
the overall winner.  The simplest algorithmic way to remove it oraz
find the "next" winner jest to move some loser (let's say cell 30 w the
diagram above) into the 0 position, oraz then percolate this new 0 down
the tree, exchanging values, until the invariant jest re-established.
This jest clearly logarithmic on the total number of items w the tree.
By iterating over all items, you get an O(n ln n) sort.

A nice feature of this sort jest that you can efficiently insert new
items dopóki the sort jest going on, provided that the inserted items are
not "better" than the last 0'th element you extracted.  This jest
especially useful w simulation contexts, where the tree holds all
incoming events, oraz the "win" condition means the smallest scheduled
time.  When an event schedule other events dla execution, they are
scheduled into the future, so they can easily go into the heap.  So, a
heap jest a good structure dla implementing schedulers (this jest what I
used dla my MIDI sequencer :-).

Various structures dla implementing schedulers have been extensively
studied, oraz heaps are good dla this, jako they are reasonably speedy,
the speed jest almost constant, oraz the worst case jest nie much different
than the average case.  However, there are other representations which
are more efficient overall, yet the worst cases might be terrible.

Heaps are also very useful w big disk sorts.  You most probably all
know that a big sort implies producing "runs" (which are pre-sorted
sequences, which size jest usually related to the amount of CPU memory),
followed by a merging dalejes dla these runs, which merging jest often
very cleverly organised[1].  It jest very important that the initial
sort produces the longest runs possible.  Tournaments are a good way
to that.  If, using all the memory available to hold a tournament, you
replace oraz percolate items that happen to fit the current run, you'll
produce runs which are twice the size of the memory dla random input,
and much better dla input fuzzily ordered.

Moreover, jeżeli you output the 0'th item on disk oraz get an input which
may nie fit w the current tournament (because the value "wins" over
the last output value), it cannot fit w the heap, so the size of the
heap decreases.  The freed memory could be cleverly reused immediately
dla progressively building a second heap, which grows at exactly the
same rate the first heap jest melting.  When the first heap completely
vanishes, you switch heaps oraz start a new run.  Clever oraz quite
effective!

In a word, heaps are useful memory structures to know.  I use them w
a few applications, oraz I think it jest good to keep a `heap' module
around. :-)

--------------------
[1] The disk balancing algorithms which are current, nowadays, are
more annoying than clever, oraz this jest a consequence of the seeking
capabilities of the disks.  On devices which cannot seek, like big
tape drives, the story was quite different, oraz one had to be very
clever to ensure (far w advance) that each tape movement will be the
most effective possible (that is, will best participate at
"progressing" the merge).  Some tapes were even able to read
backwards, oraz this was also used to avoid the rewinding time.
Believe me, real good tape sorts were quite spectacular to watch!
From all times, sorting has always been a Great Art! :-)
"""

__all__ = ['heappush', 'heappop', 'heapify', 'heapreplace', 'merge',
           'nlargest', 'nsmallest', 'heappushpop']

def heappush(heap, item):
    """Push item onto heap, maintaining the heap invariant."""
    heap.append(item)
    _siftdown(heap, 0, len(heap)-1)

def heappop(heap):
    """Pop the smallest item off the heap, maintaining the heap invariant."""
    lastelt = heap.pop()    # podnieśs appropriate IndexError jeżeli heap jest empty
    jeżeli heap:
        returnitem = heap[0]
        heap[0] = lastelt
        _siftup(heap, 0)
        zwróć returnitem
    zwróć lastelt

def heapreplace(heap, item):
    """Pop oraz zwróć the current smallest value, oraz add the new item.

    This jest more efficient than heappop() followed by heappush(), oraz can be
    more appropriate when using a fixed-size heap.  Note that the value
    returned may be larger than item!  That constrains reasonable uses of
    this routine unless written jako part of a conditional replacement:

        jeżeli item > heap[0]:
            item = heapreplace(heap, item)
    """
    returnitem = heap[0]    # podnieśs appropriate IndexError jeżeli heap jest empty
    heap[0] = item
    _siftup(heap, 0)
    zwróć returnitem

def heappushpop(heap, item):
    """Fast version of a heappush followed by a heappop."""
    jeżeli heap oraz heap[0] < item:
        item, heap[0] = heap[0], item
        _siftup(heap, 0)
    zwróć item

def heapify(x):
    """Transform list into a heap, in-place, w O(len(x)) time."""
    n = len(x)
    # Transform bottom-up.  The largest index there's any point to looking at
    # jest the largest przy a child index in-range, so must have 2*i + 1 < n,
    # albo i < (n-1)/2.  If n jest even = 2*j, this jest (2*j-1)/2 = j-1/2 so
    # j-1 jest the largest, which jest n//2 - 1.  If n jest odd = 2*j+1, this jest
    # (2*j+1-1)/2 = j so j-1 jest the largest, oraz that's again n//2-1.
    dla i w reversed(range(n//2)):
        _siftup(x, i)

def _heappop_max(heap):
    """Maxheap version of a heappop."""
    lastelt = heap.pop()    # podnieśs appropriate IndexError jeżeli heap jest empty
    jeżeli heap:
        returnitem = heap[0]
        heap[0] = lastelt
        _siftup_max(heap, 0)
        zwróć returnitem
    zwróć lastelt

def _heapreplace_max(heap, item):
    """Maxheap version of a heappop followed by a heappush."""
    returnitem = heap[0]    # podnieśs appropriate IndexError jeżeli heap jest empty
    heap[0] = item
    _siftup_max(heap, 0)
    zwróć returnitem

def _heapify_max(x):
    """Transform list into a maxheap, in-place, w O(len(x)) time."""
    n = len(x)
    dla i w reversed(range(n//2)):
        _siftup_max(x, i)

# 'heap' jest a heap at all indices >= startpos, wyjąwszy possibly dla pos.  pos
# jest the index of a leaf przy a possibly out-of-order value.  Restore the
# heap invariant.
def _siftdown(heap, startpos, pos):
    newitem = heap[pos]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    dopóki pos > startpos:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        jeżeli newitem < parent:
            heap[pos] = parent
            pos = parentpos
            kontynuuj
        przerwij
    heap[pos] = newitem

# The child indices of heap index pos are already heaps, oraz we want to make
# a heap at index pos too.  We do this by bubbling the smaller child of
# pos up (and so on przy that child's children, etc) until hitting a leaf,
# then using _siftdown to move the oddball originally at index pos into place.
#
# We *could* przerwij out of the loop jako soon jako we find a pos where newitem <=
# both its children, but turns out that's nie a good idea, oraz despite that
# many books write the algorithm that way.  During a heap pop, the last array
# element jest sifted in, oraz that tends to be large, so that comparing it
# against values starting z the root usually doesn't pay (= usually doesn't
# get us out of the loop early).  See Knuth, Volume 3, where this jest
# explained oraz quantified w an exercise.
#
# Cutting the # of comparisons jest important, since these routines have no
# way to extract "the priority" z an array element, so that intelligence
# jest likely to be hiding w custom comparison methods, albo w array elements
# storing (priority, record) tuples.  Comparisons are thus potentially
# expensive.
#
# On random arrays of length 1000, making this change cut the number of
# comparisons made by heapify() a little, oraz those made by exhaustive
# heappop() a lot, w accord przy theory.  Here are typical results z 3
# runs (3 just to demonstrate how small the variance is):
#
# Compares needed by heapify     Compares needed by 1000 heappops
# --------------------------     --------------------------------
# 1837 cut to 1663               14996 cut to 8680
# 1855 cut to 1659               14966 cut to 8678
# 1847 cut to 1660               15024 cut to 8703
#
# Building the heap by using heappush() 1000 times instead required
# 2198, 2148, oraz 2219 compares:  heapify() jest more efficient, when
# you can use it.
#
# The total compares needed by list.sort() on the same lists were 8627,
# 8627, oraz 8632 (this should be compared to the sum of heapify() oraz
# heappop() compares):  list.sort() jest (unsurprisingly!) more efficient
# dla sorting.

def _siftup(heap, pos):
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    # Bubble up the smaller child until hitting a leaf.
    childpos = 2*pos + 1    # leftmost child position
    dopóki childpos < endpos:
        # Set childpos to index of smaller child.
        rightpos = childpos + 1
        jeżeli rightpos < endpos oraz nie heap[childpos] < heap[rightpos]:
            childpos = rightpos
        # Move the smaller child up.
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2*pos + 1
    # The leaf at pos jest empty now.  Put newitem there, oraz bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = newitem
    _siftdown(heap, startpos, pos)

def _siftdown_max(heap, startpos, pos):
    'Maxheap variant of _siftdown'
    newitem = heap[pos]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    dopóki pos > startpos:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        jeżeli parent < newitem:
            heap[pos] = parent
            pos = parentpos
            kontynuuj
        przerwij
    heap[pos] = newitem

def _siftup_max(heap, pos):
    'Maxheap variant of _siftup'
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    # Bubble up the larger child until hitting a leaf.
    childpos = 2*pos + 1    # leftmost child position
    dopóki childpos < endpos:
        # Set childpos to index of larger child.
        rightpos = childpos + 1
        jeżeli rightpos < endpos oraz nie heap[rightpos] < heap[childpos]:
            childpos = rightpos
        # Move the larger child up.
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2*pos + 1
    # The leaf at pos jest empty now.  Put newitem there, oraz bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = newitem
    _siftdown_max(heap, startpos, pos)

def merge(*iterables, key=Nic, reverse=Nieprawda):
    '''Merge multiple sorted inputs into a single sorted output.

    Similar to sorted(itertools.chain(*iterables)) but returns a generator,
    does nie pull the data into memory all at once, oraz assumes that each of
    the input streams jest already sorted (smallest to largest).

    >>> list(merge([1,3,5,7], [0,2,4,8], [5,10,15,20], [], [25]))
    [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]

    If *key* jest nie Nic, applies a key function to each element to determine
    its sort order.

    >>> list(merge(['dog', 'horse'], ['cat', 'fish', 'kangaroo'], key=len))
    ['dog', 'cat', 'fish', 'horse', 'kangaroo']

    '''

    h = []
    h_append = h.append

    jeżeli reverse:
        _heapify = _heapify_max
        _heappop = _heappop_max
        _heapreplace = _heapreplace_max
        direction = -1
    inaczej:
        _heapify = heapify
        _heappop = heappop
        _heapreplace = heapreplace
        direction = 1

    jeżeli key jest Nic:
        dla order, it w enumerate(map(iter, iterables)):
            spróbuj:
                next = it.__next__
                h_append([next(), order * direction, next])
            wyjąwszy StopIteration:
                dalej
        _heapify(h)
        dopóki len(h) > 1:
            spróbuj:
                dopóki Prawda:
                    value, order, next = s = h[0]
                    uzyskaj value
                    s[0] = next()           # podnieśs StopIteration when exhausted
                    _heapreplace(h, s)      # restore heap condition
            wyjąwszy StopIteration:
                _heappop(h)                 # remove empty iterator
        jeżeli h:
            # fast case when only a single iterator remains
            value, order, next = h[0]
            uzyskaj value
            uzyskaj z next.__self__
        zwróć

    dla order, it w enumerate(map(iter, iterables)):
        spróbuj:
            next = it.__next__
            value = next()
            h_append([key(value), order * direction, value, next])
        wyjąwszy StopIteration:
            dalej
    _heapify(h)
    dopóki len(h) > 1:
        spróbuj:
            dopóki Prawda:
                key_value, order, value, next = s = h[0]
                uzyskaj value
                value = next()
                s[0] = key(value)
                s[2] = value
                _heapreplace(h, s)
        wyjąwszy StopIteration:
            _heappop(h)
    jeżeli h:
        key_value, order, value, next = h[0]
        uzyskaj value
        uzyskaj z next.__self__


# Algorithm notes dla nlargest() oraz nsmallest()
# ==============================================
#
# Make a single dalej over the data dopóki keeping the k most extreme values
# w a heap.  Memory consumption jest limited to keeping k values w a list.
#
# Measured performance dla random inputs:
#
#                                   number of comparisons
#    n inputs     k-extreme values  (average of 5 trials)   % more than min()
# -------------   ----------------  ---------------------   -----------------
#      1,000           100                  3,317               231.7%
#     10,000           100                 14,046                40.5%
#    100,000           100                105,749                 5.7%
#  1,000,000           100              1,007,751                 0.8%
# 10,000,000           100             10,009,401                 0.1%
#
# Theoretical number of comparisons dla k smallest of n random inputs:
#
# Step   Comparisons                  Action
# ----   --------------------------   ---------------------------
#  1     1.66 * k                     heapify the first k-inputs
#  2     n - k                        compare remaining elements to top of heap
#  3     k * (1 + lg2(k)) * ln(n/k)   replace the topmost value on the heap
#  4     k * lg2(k) - (k/2)           final sort of the k most extreme values
#
# Combining oraz simplifying dla a rough estimate gives:
#
#        comparisons = n + k * (log(k, 2) * log(n/k) + log(k, 2) + log(n/k))
#
# Computing the number of comparisons dla step 3:
# -----------------------------------------------
# * For the i-th new value z the iterable, the probability of being w the
#   k most extreme values jest k/i.  For example, the probability of the 101st
#   value seen being w the 100 most extreme values jest 100/101.
# * If the value jest a new extreme value, the cost of inserting it into the
#   heap jest 1 + log(k, 2).
# * The probability times the cost gives:
#            (k/i) * (1 + log(k, 2))
# * Summing across the remaining n-k elements gives:
#            sum((k/i) * (1 + log(k, 2)) dla i w range(k+1, n+1))
# * This reduces to:
#            (H(n) - H(k)) * k * (1 + log(k, 2))
# * Where H(n) jest the n-th harmonic number estimated by:
#            gamma = 0.5772156649
#            H(n) = log(n, e) + gamma + 1 / (2 * n)
#   http://en.wikipedia.org/wiki/Harmonic_series_(mathematics)#Rate_of_divergence
# * Substituting the H(n) formula:
#            comparisons = k * (1 + log(k, 2)) * (log(n/k, e) + (1/n - 1/k) / 2)
#
# Worst-case dla step 3:
# ----------------------
# In the worst case, the input data jest reversed sorted so that every new element
# must be inserted w the heap:
#
#             comparisons = 1.66 * k + log(k, 2) * (n - k)
#
# Alternative Algorithms
# ----------------------
# Other algorithms were nie used because they:
# 1) Took much more auxiliary memory,
# 2) Made multiple dalejes over the data.
# 3) Made more comparisons w common cases (small k, large n, semi-random input).
# See the more detailed comparison of approach at:
# http://code.activestate.com/recipes/577573-compare-algorithms-for-heapqsmallest

def nsmallest(n, iterable, key=Nic):
    """Find the n smallest elements w a dataset.

    Equivalent to:  sorted(iterable, key=key)[:n]
    """

    # Short-cut dla n==1 jest to use min()
    jeżeli n == 1:
        it = iter(iterable)
        sentinel = object()
        jeżeli key jest Nic:
            result = min(it, default=sentinel)
        inaczej:
            result = min(it, default=sentinel, key=key)
        zwróć [] jeżeli result jest sentinel inaczej [result]

    # When n>=size, it's faster to use sorted()
    spróbuj:
        size = len(iterable)
    wyjąwszy (TypeError, AttributeError):
        dalej
    inaczej:
        jeżeli n >= size:
            zwróć sorted(iterable, key=key)[:n]

    # When key jest none, use simpler decoration
    jeżeli key jest Nic:
        it = iter(iterable)
        # put the range(n) first so that zip() doesn't
        # consume one too many elements z the iterator
        result = [(elem, i) dla i, elem w zip(range(n), it)]
        jeżeli nie result:
            zwróć result
        _heapify_max(result)
        top = result[0][0]
        order = n
        _heapreplace = _heapreplace_max
        dla elem w it:
            jeżeli elem < top:
                _heapreplace(result, (elem, order))
                top = result[0][0]
                order += 1
        result.sort()
        zwróć [r[0] dla r w result]

    # General case, slowest method
    it = iter(iterable)
    result = [(key(elem), i, elem) dla i, elem w zip(range(n), it)]
    jeżeli nie result:
        zwróć result
    _heapify_max(result)
    top = result[0][0]
    order = n
    _heapreplace = _heapreplace_max
    dla elem w it:
        k = key(elem)
        jeżeli k < top:
            _heapreplace(result, (k, order, elem))
            top = result[0][0]
            order += 1
    result.sort()
    zwróć [r[2] dla r w result]

def nlargest(n, iterable, key=Nic):
    """Find the n largest elements w a dataset.

    Equivalent to:  sorted(iterable, key=key, reverse=Prawda)[:n]
    """

    # Short-cut dla n==1 jest to use max()
    jeżeli n == 1:
        it = iter(iterable)
        sentinel = object()
        jeżeli key jest Nic:
            result = max(it, default=sentinel)
        inaczej:
            result = max(it, default=sentinel, key=key)
        zwróć [] jeżeli result jest sentinel inaczej [result]

    # When n>=size, it's faster to use sorted()
    spróbuj:
        size = len(iterable)
    wyjąwszy (TypeError, AttributeError):
        dalej
    inaczej:
        jeżeli n >= size:
            zwróć sorted(iterable, key=key, reverse=Prawda)[:n]

    # When key jest none, use simpler decoration
    jeżeli key jest Nic:
        it = iter(iterable)
        result = [(elem, i) dla i, elem w zip(range(0, -n, -1), it)]
        jeżeli nie result:
            zwróć result
        heapify(result)
        top = result[0][0]
        order = -n
        _heapreplace = heapreplace
        dla elem w it:
            jeżeli top < elem:
                _heapreplace(result, (elem, order))
                top = result[0][0]
                order -= 1
        result.sort(reverse=Prawda)
        zwróć [r[0] dla r w result]

    # General case, slowest method
    it = iter(iterable)
    result = [(key(elem), i, elem) dla i, elem w zip(range(0, -n, -1), it)]
    jeżeli nie result:
        zwróć result
    heapify(result)
    top = result[0][0]
    order = -n
    _heapreplace = heapreplace
    dla elem w it:
        k = key(elem)
        jeżeli top < k:
            _heapreplace(result, (k, order, elem))
            top = result[0][0]
            order -= 1
    result.sort(reverse=Prawda)
    zwróć [r[2] dla r w result]

# If available, use C implementation
spróbuj:
    z _heapq zaimportuj *
wyjąwszy ImportError:
    dalej
spróbuj:
    z _heapq zaimportuj _heapreplace_max
wyjąwszy ImportError:
    dalej
spróbuj:
    z _heapq zaimportuj _heapify_max
wyjąwszy ImportError:
    dalej
spróbuj:
    z _heapq zaimportuj _heappop_max
wyjąwszy ImportError:
    dalej


jeżeli __name__ == "__main__":

    zaimportuj doctest
    print(doctest.testmod())
