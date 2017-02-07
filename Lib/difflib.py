"""
Module difflib -- helpers dla computing deltas between objects.

Function get_close_matches(word, possibilities, n=3, cutoff=0.6):
    Use SequenceMatcher to zwróć list of the best "good enough" matches.

Function context_diff(a, b):
    For two lists of strings, zwróć a delta w context diff format.

Function ndiff(a, b):
    Return a delta: the difference between `a` oraz `b` (lists of strings).

Function restore(delta, which):
    Return one of the two sequences that generated an ndiff delta.

Function unified_diff(a, b):
    For two lists of strings, zwróć a delta w unified diff format.

Class SequenceMatcher:
    A flexible klasa dla comparing pairs of sequences of any type.

Class Differ:
    For producing human-readable deltas z sequences of lines of text.

Class HtmlDiff:
    For producing HTML side by side comparison przy change highlights.
"""

__all__ = ['get_close_matches', 'ndiff', 'restore', 'SequenceMatcher',
           'Differ','IS_CHARACTER_JUNK', 'IS_LINE_JUNK', 'context_diff',
           'unified_diff', 'diff_bytes', 'HtmlDiff', 'Match']

z heapq zaimportuj nlargest jako _nlargest
z collections zaimportuj namedtuple jako _namedtuple

Match = _namedtuple('Match', 'a b size')

def _calculate_ratio(matches, length):
    jeżeli length:
        zwróć 2.0 * matches / length
    zwróć 1.0

klasa SequenceMatcher:

    """
    SequenceMatcher jest a flexible klasa dla comparing pairs of sequences of
    any type, so long jako the sequence elements are hashable.  The basic
    algorithm predates, oraz jest a little fancier than, an algorithm
    published w the late 1980's by Ratcliff oraz Obershelp under the
    hyperbolic name "gestalt pattern matching".  The basic idea jest to find
    the longest contiguous matching subsequence that contains no "junk"
    elements (R-O doesn't address junk).  The same idea jest then applied
    recursively to the pieces of the sequences to the left oraz to the right
    of the matching subsequence.  This does nie uzyskaj minimal edit
    sequences, but does tend to uzyskaj matches that "look right" to people.

    SequenceMatcher tries to compute a "human-friendly diff" between two
    sequences.  Unlike e.g. UNIX(tm) diff, the fundamental notion jest the
    longest *contiguous* & junk-free matching subsequence.  That's what
    catches peoples' eyes.  The Windows(tm) windiff has another interesting
    notion, pairing up elements that appear uniquely w each sequence.
    That, oraz the method here, appear to uzyskaj more intuitive difference
    reports than does diff.  This method appears to be the least vulnerable
    to synching up on blocks of "junk lines", though (like blank lines w
    ordinary text files, albo maybe "<P>" lines w HTML files).  That may be
    because this jest the only method of the 3 that has a *concept* of
    "junk" <wink>.

    Example, comparing two strings, oraz considering blanks to be "junk":

    >>> s = SequenceMatcher(lambda x: x == " ",
    ...                     "private Thread currentThread;",
    ...                     "private volatile Thread currentThread;")
    >>>

    .ratio() returns a float w [0, 1], measuring the "similarity" of the
    sequences.  As a rule of thumb, a .ratio() value over 0.6 means the
    sequences are close matches:

    >>> print(round(s.ratio(), 3))
    0.866
    >>>

    If you're only interested w where the sequences match,
    .get_matching_blocks() jest handy:

    >>> dla block w s.get_matching_blocks():
    ...     print("a[%d] oraz b[%d] match dla %d elements" % block)
    a[0] oraz b[0] match dla 8 elements
    a[8] oraz b[17] match dla 21 elements
    a[29] oraz b[38] match dla 0 elements

    Note that the last tuple returned by .get_matching_blocks() jest always a
    dummy, (len(a), len(b), 0), oraz this jest the only case w which the last
    tuple element (number of elements matched) jest 0.

    If you want to know how to change the first sequence into the second,
    use .get_opcodes():

    >>> dla opcode w s.get_opcodes():
    ...     print("%6s a[%d:%d] b[%d:%d]" % opcode)
     equal a[0:8] b[0:8]
    insert a[8:8] b[8:17]
     equal a[8:29] b[17:38]

    See the Differ klasa dla a fancy human-friendly file differencer, which
    uses SequenceMatcher both to compare sequences of lines, oraz to compare
    sequences of characters within similar (near-matching) lines.

    See also function get_close_matches() w this module, which shows how
    simple code building on SequenceMatcher can be used to do useful work.

    Timing:  Basic R-O jest cubic time worst case oraz quadratic time expected
    case.  SequenceMatcher jest quadratic time dla the worst case oraz has
    expected-case behavior dependent w a complicated way on how many
    elements the sequences have w common; best case time jest linear.

    Methods:

    __init__(isjunk=Nic, a='', b='')
        Construct a SequenceMatcher.

    set_seqs(a, b)
        Set the two sequences to be compared.

    set_seq1(a)
        Set the first sequence to be compared.

    set_seq2(b)
        Set the second sequence to be compared.

    find_longest_match(alo, ahi, blo, bhi)
        Find longest matching block w a[alo:ahi] oraz b[blo:bhi].

    get_matching_blocks()
        Return list of triples describing matching subsequences.

    get_opcodes()
        Return list of 5-tuples describing how to turn a into b.

    ratio()
        Return a measure of the sequences' similarity (float w [0,1]).

    quick_ratio()
        Return an upper bound on .ratio() relatively quickly.

    real_quick_ratio()
        Return an upper bound on ratio() very quickly.
    """

    def __init__(self, isjunk=Nic, a='', b='', autojunk=Prawda):
        """Construct a SequenceMatcher.

        Optional arg isjunk jest Nic (the default), albo a one-argument
        function that takes a sequence element oraz returns true iff the
        element jest junk.  Nic jest equivalent to dalejing "lambda x: 0", i.e.
        no elements are considered to be junk.  For example, dalej
            lambda x: x w " \\t"
        jeżeli you're comparing lines jako sequences of characters, oraz don't
        want to synch up on blanks albo hard tabs.

        Optional arg a jest the first of two sequences to be compared.  By
        default, an empty string.  The elements of a must be hashable.  See
        also .set_seqs() oraz .set_seq1().

        Optional arg b jest the second of two sequences to be compared.  By
        default, an empty string.  The elements of b must be hashable. See
        also .set_seqs() oraz .set_seq2().

        Optional arg autojunk should be set to Nieprawda to disable the
        "automatic junk heuristic" that treats popular elements jako junk
        (see module documentation dla more information).
        """

        # Members:
        # a
        #      first sequence
        # b
        #      second sequence; differences are computed jako "what do
        #      we need to do to 'a' to change it into 'b'?"
        # b2j
        #      dla x w b, b2j[x] jest a list of the indices (into b)
        #      at which x appears; junk oraz popular elements do nie appear
        # fullbcount
        #      dla x w b, fullbcount[x] == the number of times x
        #      appears w b; only materialized jeżeli really needed (used
        #      only dla computing quick_ratio())
        # matching_blocks
        #      a list of (i, j, k) triples, where a[i:i+k] == b[j:j+k];
        #      ascending & non-overlapping w i oraz w j; terminated by
        #      a dummy (len(a), len(b), 0) sentinel
        # opcodes
        #      a list of (tag, i1, i2, j1, j2) tuples, where tag jest
        #      one of
        #          'replace'   a[i1:i2] should be replaced by b[j1:j2]
        #          'delete'    a[i1:i2] should be deleted
        #          'insert'    b[j1:j2] should be inserted
        #          'equal'     a[i1:i2] == b[j1:j2]
        # isjunk
        #      a user-supplied function taking a sequence element oraz
        #      returning true iff the element jest "junk" -- this has
        #      subtle but helpful effects on the algorithm, which I'll
        #      get around to writing up someday <0.9 wink>.
        #      DON'T USE!  Only __chain_b uses this.  Use "in self.bjunk".
        # bjunk
        #      the items w b dla which isjunk jest Prawda.
        # bpopular
        #      nonjunk items w b treated jako junk by the heuristic (jeżeli used).

        self.isjunk = isjunk
        self.a = self.b = Nic
        self.autojunk = autojunk
        self.set_seqs(a, b)

    def set_seqs(self, a, b):
        """Set the two sequences to be compared.

        >>> s = SequenceMatcher()
        >>> s.set_seqs("abcd", "bcde")
        >>> s.ratio()
        0.75
        """

        self.set_seq1(a)
        self.set_seq2(b)

    def set_seq1(self, a):
        """Set the first sequence to be compared.

        The second sequence to be compared jest nie changed.

        >>> s = SequenceMatcher(Nic, "abcd", "bcde")
        >>> s.ratio()
        0.75
        >>> s.set_seq1("bcde")
        >>> s.ratio()
        1.0
        >>>

        SequenceMatcher computes oraz caches detailed information about the
        second sequence, so jeżeli you want to compare one sequence S against
        many sequences, use .set_seq2(S) once oraz call .set_seq1(x)
        repeatedly dla each of the other sequences.

        See also set_seqs() oraz set_seq2().
        """

        jeżeli a jest self.a:
            zwróć
        self.a = a
        self.matching_blocks = self.opcodes = Nic

    def set_seq2(self, b):
        """Set the second sequence to be compared.

        The first sequence to be compared jest nie changed.

        >>> s = SequenceMatcher(Nic, "abcd", "bcde")
        >>> s.ratio()
        0.75
        >>> s.set_seq2("abcd")
        >>> s.ratio()
        1.0
        >>>

        SequenceMatcher computes oraz caches detailed information about the
        second sequence, so jeżeli you want to compare one sequence S against
        many sequences, use .set_seq2(S) once oraz call .set_seq1(x)
        repeatedly dla each of the other sequences.

        See also set_seqs() oraz set_seq1().
        """

        jeżeli b jest self.b:
            zwróć
        self.b = b
        self.matching_blocks = self.opcodes = Nic
        self.fullbcount = Nic
        self.__chain_b()

    # For each element x w b, set b2j[x] to a list of the indices w
    # b where x appears; the indices are w increasing order; note that
    # the number of times x appears w b jest len(b2j[x]) ...
    # when self.isjunk jest defined, junk elements don't show up w this
    # map at all, which stops the central find_longest_match method
    # z starting any matching block at a junk element ...
    # b2j also does nie contain entries dla "popular" elements, meaning
    # elements that account dla more than 1 + 1% of the total elements, oraz
    # when the sequence jest reasonably large (>= 200 elements); this can
    # be viewed jako an adaptive notion of semi-junk, oraz uzyskajs an enormous
    # speedup when, e.g., comparing program files przy hundreds of
    # instances of "return NULL;" ...
    # note that this jest only called when b changes; so dla cross-product
    # kinds of matches, it's best to call set_seq2 once, then set_seq1
    # repeatedly

    def __chain_b(self):
        # Because isjunk jest a user-defined (nie C) function, oraz we test
        # dla junk a LOT, it's important to minimize the number of calls.
        # Before the tricks described here, __chain_b was by far the most
        # time-consuming routine w the whole module!  If anyone sees
        # Jim Roskind, thank him again dla profile.py -- I never would
        # have guessed that.
        # The first trick jest to build b2j ignoring the possibility
        # of junk.  I.e., we don't call isjunk at all yet.  Throwing
        # out the junk later jest much cheaper than building b2j "right"
        # z the start.
        b = self.b
        self.b2j = b2j = {}

        dla i, elt w enumerate(b):
            indices = b2j.setdefault(elt, [])
            indices.append(i)

        # Purge junk elements
        self.bjunk = junk = set()
        isjunk = self.isjunk
        jeżeli isjunk:
            dla elt w b2j.keys():
                jeżeli isjunk(elt):
                    junk.add(elt)
            dla elt w junk: # separate loop avoids separate list of keys
                usuń b2j[elt]

        # Purge popular elements that are nie junk
        self.bpopular = popular = set()
        n = len(b)
        jeżeli self.autojunk oraz n >= 200:
            ntest = n // 100 + 1
            dla elt, idxs w b2j.items():
                jeżeli len(idxs) > ntest:
                    popular.add(elt)
            dla elt w popular: # ditto; jako fast dla 1% deletion
                usuń b2j[elt]

    def find_longest_match(self, alo, ahi, blo, bhi):
        """Find longest matching block w a[alo:ahi] oraz b[blo:bhi].

        If isjunk jest nie defined:

        Return (i,j,k) such that a[i:i+k] jest equal to b[j:j+k], where
            alo <= i <= i+k <= ahi
            blo <= j <= j+k <= bhi
        oraz dla all (i',j',k') meeting those conditions,
            k >= k'
            i <= i'
            oraz jeżeli i == i', j <= j'

        In other words, of all maximal matching blocks, zwróć one that
        starts earliest w a, oraz of all those maximal matching blocks that
        start earliest w a, zwróć the one that starts earliest w b.

        >>> s = SequenceMatcher(Nic, " abcd", "abcd abcd")
        >>> s.find_longest_match(0, 5, 0, 9)
        Match(a=0, b=4, size=5)

        If isjunk jest defined, first the longest matching block jest
        determined jako above, but przy the additional restriction that no
        junk element appears w the block.  Then that block jest extended as
        far jako possible by matching (only) junk elements on both sides.  So
        the resulting block never matches on junk wyjąwszy jako identical junk
        happens to be adjacent to an "interesting" match.

        Here's the same example jako before, but considering blanks to be
        junk.  That prevents " abcd" z matching the " abcd" at the tail
        end of the second sequence directly.  Instead only the "abcd" can
        match, oraz matches the leftmost "abcd" w the second sequence:

        >>> s = SequenceMatcher(lambda x: x==" ", " abcd", "abcd abcd")
        >>> s.find_longest_match(0, 5, 0, 9)
        Match(a=1, b=0, size=4)

        If no blocks match, zwróć (alo, blo, 0).

        >>> s = SequenceMatcher(Nic, "ab", "c")
        >>> s.find_longest_match(0, 2, 0, 1)
        Match(a=0, b=0, size=0)
        """

        # CAUTION:  stripping common prefix albo suffix would be incorrect.
        # E.g.,
        #    ab
        #    acab
        # Longest matching block jest "ab", but jeżeli common prefix jest
        # stripped, it's "a" (tied przy "b").  UNIX(tm) diff does so
        # strip, so ends up claiming that ab jest changed to acab by
        # inserting "ca" w the middle.  That's minimal but unintuitive:
        # "it's obvious" that someone inserted "ac" at the front.
        # Windiff ends up at the same place jako diff, but by pairing up
        # the unique 'b's oraz then matching the first two 'a's.

        a, b, b2j, isbjunk = self.a, self.b, self.b2j, self.bjunk.__contains__
        besti, bestj, bestsize = alo, blo, 0
        # find longest junk-free match
        # during an iteration of the loop, j2len[j] = length of longest
        # junk-free match ending przy a[i-1] oraz b[j]
        j2len = {}
        nothing = []
        dla i w range(alo, ahi):
            # look at all instances of a[i] w b; note that because
            # b2j has no junk keys, the loop jest skipped jeżeli a[i] jest junk
            j2lenget = j2len.get
            newj2len = {}
            dla j w b2j.get(a[i], nothing):
                # a[i] matches b[j]
                jeżeli j < blo:
                    kontynuuj
                jeżeli j >= bhi:
                    przerwij
                k = newj2len[j] = j2lenget(j-1, 0) + 1
                jeżeli k > bestsize:
                    besti, bestj, bestsize = i-k+1, j-k+1, k
            j2len = newj2len

        # Extend the best by non-junk elements on each end.  In particular,
        # "popular" non-junk elements aren't w b2j, which greatly speeds
        # the inner loop above, but also means "the best" match so far
        # doesn't contain any junk *or* popular non-junk elements.
        dopóki besti > alo oraz bestj > blo oraz \
              nie isbjunk(b[bestj-1]) oraz \
              a[besti-1] == b[bestj-1]:
            besti, bestj, bestsize = besti-1, bestj-1, bestsize+1
        dopóki besti+bestsize < ahi oraz bestj+bestsize < bhi oraz \
              nie isbjunk(b[bestj+bestsize]) oraz \
              a[besti+bestsize] == b[bestj+bestsize]:
            bestsize += 1

        # Now that we have a wholly interesting match (albeit possibly
        # empty!), we may jako well suck up the matching junk on each
        # side of it too.  Can't think of a good reason nie to, oraz it
        # saves post-processing the (possibly considerable) expense of
        # figuring out what to do przy it.  In the case of an empty
        # interesting match, this jest clearly the right thing to do,
        # because no other kind of match jest possible w the regions.
        dopóki besti > alo oraz bestj > blo oraz \
              isbjunk(b[bestj-1]) oraz \
              a[besti-1] == b[bestj-1]:
            besti, bestj, bestsize = besti-1, bestj-1, bestsize+1
        dopóki besti+bestsize < ahi oraz bestj+bestsize < bhi oraz \
              isbjunk(b[bestj+bestsize]) oraz \
              a[besti+bestsize] == b[bestj+bestsize]:
            bestsize = bestsize + 1

        zwróć Match(besti, bestj, bestsize)

    def get_matching_blocks(self):
        """Return list of triples describing matching subsequences.

        Each triple jest of the form (i, j, n), oraz means that
        a[i:i+n] == b[j:j+n].  The triples are monotonically increasing w
        i oraz w j.  New w Python 2.5, it's also guaranteed that if
        (i, j, n) oraz (i', j', n') are adjacent triples w the list, oraz
        the second jest nie the last triple w the list, then i+n != i' albo
        j+n != j'.  IOW, adjacent triples never describe adjacent equal
        blocks.

        The last triple jest a dummy, (len(a), len(b), 0), oraz jest the only
        triple przy n==0.

        >>> s = SequenceMatcher(Nic, "abxcd", "abcd")
        >>> list(s.get_matching_blocks())
        [Match(a=0, b=0, size=2), Match(a=3, b=2, size=2), Match(a=5, b=4, size=0)]
        """

        jeżeli self.matching_blocks jest nie Nic:
            zwróć self.matching_blocks
        la, lb = len(self.a), len(self.b)

        # This jest most naturally expressed jako a recursive algorithm, but
        # at least one user bumped into extreme use cases that exceeded
        # the recursion limit on their box.  So, now we maintain a list
        # ('queue`) of blocks we still need to look at, oraz append partial
        # results to `matching_blocks` w a loop; the matches are sorted
        # at the end.
        queue = [(0, la, 0, lb)]
        matching_blocks = []
        dopóki queue:
            alo, ahi, blo, bhi = queue.pop()
            i, j, k = x = self.find_longest_match(alo, ahi, blo, bhi)
            # a[alo:i] vs b[blo:j] unknown
            # a[i:i+k] same jako b[j:j+k]
            # a[i+k:ahi] vs b[j+k:bhi] unknown
            jeżeli k:   # jeżeli k jest 0, there was no matching block
                matching_blocks.append(x)
                jeżeli alo < i oraz blo < j:
                    queue.append((alo, i, blo, j))
                jeżeli i+k < ahi oraz j+k < bhi:
                    queue.append((i+k, ahi, j+k, bhi))
        matching_blocks.sort()

        # It's possible that we have adjacent equal blocks w the
        # matching_blocks list now.  Starting przy 2.5, this code was added
        # to collapse them.
        i1 = j1 = k1 = 0
        non_adjacent = []
        dla i2, j2, k2 w matching_blocks:
            # Is this block adjacent to i1, j1, k1?
            jeżeli i1 + k1 == i2 oraz j1 + k1 == j2:
                # Yes, so collapse them -- this just increases the length of
                # the first block by the length of the second, oraz the first
                # block so lengthened remains the block to compare against.
                k1 += k2
            inaczej:
                # Not adjacent.  Remember the first block (k1==0 means it's
                # the dummy we started with), oraz make the second block the
                # new block to compare against.
                jeżeli k1:
                    non_adjacent.append((i1, j1, k1))
                i1, j1, k1 = i2, j2, k2
        jeżeli k1:
            non_adjacent.append((i1, j1, k1))

        non_adjacent.append( (la, lb, 0) )
        self.matching_blocks = list(map(Match._make, non_adjacent))
        zwróć self.matching_blocks

    def get_opcodes(self):
        """Return list of 5-tuples describing how to turn a into b.

        Each tuple jest of the form (tag, i1, i2, j1, j2).  The first tuple
        has i1 == j1 == 0, oraz remaining tuples have i1 == the i2 z the
        tuple preceding it, oraz likewise dla j1 == the previous j2.

        The tags are strings, przy these meanings:

        'replace':  a[i1:i2] should be replaced by b[j1:j2]
        'delete':   a[i1:i2] should be deleted.
                    Note that j1==j2 w this case.
        'insert':   b[j1:j2] should be inserted at a[i1:i1].
                    Note that i1==i2 w this case.
        'equal':    a[i1:i2] == b[j1:j2]

        >>> a = "qabxcd"
        >>> b = "abycdf"
        >>> s = SequenceMatcher(Nic, a, b)
        >>> dla tag, i1, i2, j1, j2 w s.get_opcodes():
        ...    print(("%7s a[%d:%d] (%s) b[%d:%d] (%s)" %
        ...           (tag, i1, i2, a[i1:i2], j1, j2, b[j1:j2])))
         delete a[0:1] (q) b[0:0] ()
          equal a[1:3] (ab) b[0:2] (ab)
        replace a[3:4] (x) b[2:3] (y)
          equal a[4:6] (cd) b[3:5] (cd)
         insert a[6:6] () b[5:6] (f)
        """

        jeżeli self.opcodes jest nie Nic:
            zwróć self.opcodes
        i = j = 0
        self.opcodes = answer = []
        dla ai, bj, size w self.get_matching_blocks():
            # invariant:  we've pumped out correct diffs to change
            # a[:i] into b[:j], oraz the next matching block jest
            # a[ai:ai+size] == b[bj:bj+size].  So we need to pump
            # out a diff to change a[i:ai] into b[j:bj], pump out
            # the matching block, oraz move (i,j) beyond the match
            tag = ''
            jeżeli i < ai oraz j < bj:
                tag = 'replace'
            albo_inaczej i < ai:
                tag = 'delete'
            albo_inaczej j < bj:
                tag = 'insert'
            jeżeli tag:
                answer.append( (tag, i, ai, j, bj) )
            i, j = ai+size, bj+size
            # the list of matching blocks jest terminated by a
            # sentinel przy size 0
            jeżeli size:
                answer.append( ('equal', ai, i, bj, j) )
        zwróć answer

    def get_grouped_opcodes(self, n=3):
        """ Isolate change clusters by eliminating ranges przy no changes.

        Return a generator of groups przy up to n lines of context.
        Each group jest w the same format jako returned by get_opcodes().

        >>> z pprint zaimportuj pprint
        >>> a = list(map(str, range(1,40)))
        >>> b = a[:]
        >>> b[8:8] = ['i']     # Make an insertion
        >>> b[20] += 'x'       # Make a replacement
        >>> b[23:28] = []      # Make a deletion
        >>> b[30] += 'y'       # Make another replacement
        >>> pprint(list(SequenceMatcher(Nic,a,b).get_grouped_opcodes()))
        [[('equal', 5, 8, 5, 8), ('insert', 8, 8, 8, 9), ('equal', 8, 11, 9, 12)],
         [('equal', 16, 19, 17, 20),
          ('replace', 19, 20, 20, 21),
          ('equal', 20, 22, 21, 23),
          ('delete', 22, 27, 23, 23),
          ('equal', 27, 30, 23, 26)],
         [('equal', 31, 34, 27, 30),
          ('replace', 34, 35, 30, 31),
          ('equal', 35, 38, 31, 34)]]
        """

        codes = self.get_opcodes()
        jeżeli nie codes:
            codes = [("equal", 0, 1, 0, 1)]
        # Fixup leading oraz trailing groups jeżeli they show no changes.
        jeżeli codes[0][0] == 'equal':
            tag, i1, i2, j1, j2 = codes[0]
            codes[0] = tag, max(i1, i2-n), i2, max(j1, j2-n), j2
        jeżeli codes[-1][0] == 'equal':
            tag, i1, i2, j1, j2 = codes[-1]
            codes[-1] = tag, i1, min(i2, i1+n), j1, min(j2, j1+n)

        nn = n + n
        group = []
        dla tag, i1, i2, j1, j2 w codes:
            # End the current group oraz start a new one whenever
            # there jest a large range przy no changes.
            jeżeli tag == 'equal' oraz i2-i1 > nn:
                group.append((tag, i1, min(i2, i1+n), j1, min(j2, j1+n)))
                uzyskaj group
                group = []
                i1, j1 = max(i1, i2-n), max(j1, j2-n)
            group.append((tag, i1, i2, j1 ,j2))
        jeżeli group oraz nie (len(group)==1 oraz group[0][0] == 'equal'):
            uzyskaj group

    def ratio(self):
        """Return a measure of the sequences' similarity (float w [0,1]).

        Where T jest the total number of elements w both sequences, oraz
        M jest the number of matches, this jest 2.0*M / T.
        Note that this jest 1 jeżeli the sequences are identical, oraz 0 if
        they have nothing w common.

        .ratio() jest expensive to compute jeżeli you haven't already computed
        .get_matching_blocks() albo .get_opcodes(), w which case you may
        want to try .quick_ratio() albo .real_quick_ratio() first to get an
        upper bound.

        >>> s = SequenceMatcher(Nic, "abcd", "bcde")
        >>> s.ratio()
        0.75
        >>> s.quick_ratio()
        0.75
        >>> s.real_quick_ratio()
        1.0
        """

        matches = sum(triple[-1] dla triple w self.get_matching_blocks())
        zwróć _calculate_ratio(matches, len(self.a) + len(self.b))

    def quick_ratio(self):
        """Return an upper bound on ratio() relatively quickly.

        This isn't defined beyond that it jest an upper bound on .ratio(), oraz
        jest faster to compute.
        """

        # viewing a oraz b jako multisets, set matches to the cardinality
        # of their intersection; this counts the number of matches
        # without regard to order, so jest clearly an upper bound
        jeżeli self.fullbcount jest Nic:
            self.fullbcount = fullbcount = {}
            dla elt w self.b:
                fullbcount[elt] = fullbcount.get(elt, 0) + 1
        fullbcount = self.fullbcount
        # avail[x] jest the number of times x appears w 'b' less the
        # number of times we've seen it w 'a' so far ... kinda
        avail = {}
        availhas, matches = avail.__contains__, 0
        dla elt w self.a:
            jeżeli availhas(elt):
                numb = avail[elt]
            inaczej:
                numb = fullbcount.get(elt, 0)
            avail[elt] = numb - 1
            jeżeli numb > 0:
                matches = matches + 1
        zwróć _calculate_ratio(matches, len(self.a) + len(self.b))

    def real_quick_ratio(self):
        """Return an upper bound on ratio() very quickly.

        This isn't defined beyond that it jest an upper bound on .ratio(), oraz
        jest faster to compute than either .ratio() albo .quick_ratio().
        """

        la, lb = len(self.a), len(self.b)
        # can't have more matches than the number of elements w the
        # shorter sequence
        zwróć _calculate_ratio(min(la, lb), la + lb)

def get_close_matches(word, possibilities, n=3, cutoff=0.6):
    """Use SequenceMatcher to zwróć list of the best "good enough" matches.

    word jest a sequence dla which close matches are desired (typically a
    string).

    possibilities jest a list of sequences against which to match word
    (typically a list of strings).

    Optional arg n (default 3) jest the maximum number of close matches to
    return.  n must be > 0.

    Optional arg cutoff (default 0.6) jest a float w [0, 1].  Possibilities
    that don't score at least that similar to word are ignored.

    The best (no more than n) matches among the possibilities are returned
    w a list, sorted by similarity score, most similar first.

    >>> get_close_matches("appel", ["ape", "apple", "peach", "puppy"])
    ['apple', 'ape']
    >>> zaimportuj keyword jako _keyword
    >>> get_close_matches("wheel", _keyword.kwlist)
    ['while']
    >>> get_close_matches("Apple", _keyword.kwlist)
    []
    >>> get_close_matches("accept", _keyword.kwlist)
    ['except']
    """

    jeżeli nie n >  0:
        podnieś ValueError("n must be > 0: %r" % (n,))
    jeżeli nie 0.0 <= cutoff <= 1.0:
        podnieś ValueError("cutoff must be w [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = SequenceMatcher()
    s.set_seq2(word)
    dla x w possibilities:
        s.set_seq1(x)
        jeżeli s.real_quick_ratio() >= cutoff oraz \
           s.quick_ratio() >= cutoff oraz \
           s.ratio() >= cutoff:
            result.append((s.ratio(), x))

    # Move the best scorers to head of list
    result = _nlargest(n, result)
    # Strip scores dla the best n matches
    zwróć [x dla score, x w result]

def _count_leading(line, ch):
    """
    Return number of `ch` characters at the start of `line`.

    Example:

    >>> _count_leading('   abc', ' ')
    3
    """

    i, n = 0, len(line)
    dopóki i < n oraz line[i] == ch:
        i += 1
    zwróć i

klasa Differ:
    r"""
    Differ jest a klasa dla comparing sequences of lines of text, oraz
    producing human-readable differences albo deltas.  Differ uses
    SequenceMatcher both to compare sequences of lines, oraz to compare
    sequences of characters within similar (near-matching) lines.

    Each line of a Differ delta begins przy a two-letter code:

        '- '    line unique to sequence 1
        '+ '    line unique to sequence 2
        '  '    line common to both sequences
        '? '    line nie present w either input sequence

    Lines beginning przy '? ' attempt to guide the eye to intraline
    differences, oraz were nie present w either input sequence.  These lines
    can be confusing jeżeli the sequences contain tab characters.

    Note that Differ makes no claim to produce a *minimal* diff.  To the
    contrary, minimal diffs are often counter-intuitive, because they synch
    up anywhere possible, sometimes accidental matches 100 pages apart.
    Restricting synch points to contiguous matches preserves some notion of
    locality, at the occasional cost of producing a longer diff.

    Example: Comparing two texts.

    First we set up the texts, sequences of individual single-line strings
    ending przy newlines (such sequences can also be obtained z the
    `readlines()` method of file-like objects):

    >>> text1 = '''  1. Beautiful jest better than ugly.
    ...   2. Explicit jest better than implicit.
    ...   3. Simple jest better than complex.
    ...   4. Complex jest better than complicated.
    ... '''.splitlines(keepends=Prawda)
    >>> len(text1)
    4
    >>> text1[0][-1]
    '\n'
    >>> text2 = '''  1. Beautiful jest better than ugly.
    ...   3.   Simple jest better than complex.
    ...   4. Complicated jest better than complex.
    ...   5. Flat jest better than nested.
    ... '''.splitlines(keepends=Prawda)

    Next we instantiate a Differ object:

    >>> d = Differ()

    Note that when instantiating a Differ object we may dalej functions to
    filter out line oraz character 'junk'.  See Differ.__init__ dla details.

    Finally, we compare the two:

    >>> result = list(d.compare(text1, text2))

    'result' jest a list of strings, so let's pretty-print it:

    >>> z pprint zaimportuj pprint jako _pprint
    >>> _pprint(result)
    ['    1. Beautiful jest better than ugly.\n',
     '-   2. Explicit jest better than implicit.\n',
     '-   3. Simple jest better than complex.\n',
     '+   3.   Simple jest better than complex.\n',
     '?     ++\n',
     '-   4. Complex jest better than complicated.\n',
     '?            ^                     ---- ^\n',
     '+   4. Complicated jest better than complex.\n',
     '?           ++++ ^                      ^\n',
     '+   5. Flat jest better than nested.\n']

    As a single multi-line string it looks like this:

    >>> print(''.join(result), end="")
        1. Beautiful jest better than ugly.
    -   2. Explicit jest better than implicit.
    -   3. Simple jest better than complex.
    +   3.   Simple jest better than complex.
    ?     ++
    -   4. Complex jest better than complicated.
    ?            ^                     ---- ^
    +   4. Complicated jest better than complex.
    ?           ++++ ^                      ^
    +   5. Flat jest better than nested.

    Methods:

    __init__(linejunk=Nic, charjunk=Nic)
        Construct a text differencer, przy optional filters.

    compare(a, b)
        Compare two sequences of lines; generate the resulting delta.
    """

    def __init__(self, linejunk=Nic, charjunk=Nic):
        """
        Construct a text differencer, przy optional filters.

        The two optional keyword parameters are dla filter functions:

        - `linejunk`: A function that should accept a single string argument,
          oraz zwróć true iff the string jest junk. The module-level function
          `IS_LINE_JUNK` may be used to filter out lines without visible
          characters, wyjąwszy dla at most one splat ('#').  It jest recommended
          to leave linejunk Nic; the underlying SequenceMatcher klasa has
          an adaptive notion of "noise" lines that's better than any static
          definition the author has ever been able to craft.

        - `charjunk`: A function that should accept a string of length 1. The
          module-level function `IS_CHARACTER_JUNK` may be used to filter out
          whitespace characters (a blank albo tab; **note**: bad idea to include
          newline w this!).  Use of IS_CHARACTER_JUNK jest recommended.
        """

        self.linejunk = linejunk
        self.charjunk = charjunk

    def compare(self, a, b):
        r"""
        Compare two sequences of lines; generate the resulting delta.

        Each sequence must contain individual single-line strings ending with
        newlines. Such sequences can be obtained z the `readlines()` method
        of file-like objects.  The delta generated also consists of newline-
        terminated strings, ready to be printed as-is via the writeline()
        method of a file-like object.

        Example:

        >>> print(''.join(Differ().compare('one\ntwo\nthree\n'.splitlines(Prawda),
        ...                                'ore\ntree\nemu\n'.splitlines(Prawda))),
        ...       end="")
        - one
        ?  ^
        + ore
        ?  ^
        - two
        - three
        ?  -
        + tree
        + emu
        """

        cruncher = SequenceMatcher(self.linejunk, a, b)
        dla tag, alo, ahi, blo, bhi w cruncher.get_opcodes():
            jeżeli tag == 'replace':
                g = self._fancy_replace(a, alo, ahi, b, blo, bhi)
            albo_inaczej tag == 'delete':
                g = self._dump('-', a, alo, ahi)
            albo_inaczej tag == 'insert':
                g = self._dump('+', b, blo, bhi)
            albo_inaczej tag == 'equal':
                g = self._dump(' ', a, alo, ahi)
            inaczej:
                podnieś ValueError('unknown tag %r' % (tag,))

            uzyskaj z g

    def _dump(self, tag, x, lo, hi):
        """Generate comparison results dla a same-tagged range."""
        dla i w range(lo, hi):
            uzyskaj '%s %s' % (tag, x[i])

    def _plain_replace(self, a, alo, ahi, b, blo, bhi):
        assert alo < ahi oraz blo < bhi
        # dump the shorter block first -- reduces the burden on short-term
        # memory jeżeli the blocks are of very different sizes
        jeżeli bhi - blo < ahi - alo:
            first  = self._dump('+', b, blo, bhi)
            second = self._dump('-', a, alo, ahi)
        inaczej:
            first  = self._dump('-', a, alo, ahi)
            second = self._dump('+', b, blo, bhi)

        dla g w first, second:
            uzyskaj z g

    def _fancy_replace(self, a, alo, ahi, b, blo, bhi):
        r"""
        When replacing one block of lines przy another, search the blocks
        dla *similar* lines; the best-matching pair (jeżeli any) jest used jako a
        synch point, oraz intraline difference marking jest done on the
        similar pair. Lots of work, but often worth it.

        Example:

        >>> d = Differ()
        >>> results = d._fancy_replace(['abcDefghiJkl\n'], 0, 1,
        ...                            ['abcdefGhijkl\n'], 0, 1)
        >>> print(''.join(results), end="")
        - abcDefghiJkl
        ?    ^  ^  ^
        + abcdefGhijkl
        ?    ^  ^  ^
        """

        # don't synch up unless the lines have a similarity score of at
        # least cutoff; best_ratio tracks the best score seen so far
        best_ratio, cutoff = 0.74, 0.75
        cruncher = SequenceMatcher(self.charjunk)
        eqi, eqj = Nic, Nic   # 1st indices of equal lines (jeżeli any)

        # search dla the pair that matches best without being identical
        # (identical lines must be junk lines, & we don't want to synch up
        # on junk -- unless we have to)
        dla j w range(blo, bhi):
            bj = b[j]
            cruncher.set_seq2(bj)
            dla i w range(alo, ahi):
                ai = a[i]
                jeżeli ai == bj:
                    jeżeli eqi jest Nic:
                        eqi, eqj = i, j
                    kontynuuj
                cruncher.set_seq1(ai)
                # computing similarity jest expensive, so use the quick
                # upper bounds first -- have seen this speed up messy
                # compares by a factor of 3.
                # note that ratio() jest only expensive to compute the first
                # time it's called on a sequence pair; the expensive part
                # of the computation jest cached by cruncher
                jeżeli cruncher.real_quick_ratio() > best_ratio oraz \
                      cruncher.quick_ratio() > best_ratio oraz \
                      cruncher.ratio() > best_ratio:
                    best_ratio, best_i, best_j = cruncher.ratio(), i, j
        jeżeli best_ratio < cutoff:
            # no non-identical "pretty close" pair
            jeżeli eqi jest Nic:
                # no identical pair either -- treat it jako a straight replace
                uzyskaj z self._plain_replace(a, alo, ahi, b, blo, bhi)
                zwróć
            # no close pair, but an identical pair -- synch up on that
            best_i, best_j, best_ratio = eqi, eqj, 1.0
        inaczej:
            # there's a close pair, so forget the identical pair (jeżeli any)
            eqi = Nic

        # a[best_i] very similar to b[best_j]; eqi jest Nic iff they're nie
        # identical

        # pump out diffs z before the synch point
        uzyskaj z self._fancy_helper(a, alo, best_i, b, blo, best_j)

        # do intraline marking on the synch pair
        aelt, belt = a[best_i], b[best_j]
        jeżeli eqi jest Nic:
            # pump out a '-', '?', '+', '?' quad dla the synched lines
            atags = btags = ""
            cruncher.set_seqs(aelt, belt)
            dla tag, ai1, ai2, bj1, bj2 w cruncher.get_opcodes():
                la, lb = ai2 - ai1, bj2 - bj1
                jeżeli tag == 'replace':
                    atags += '^' * la
                    btags += '^' * lb
                albo_inaczej tag == 'delete':
                    atags += '-' * la
                albo_inaczej tag == 'insert':
                    btags += '+' * lb
                albo_inaczej tag == 'equal':
                    atags += ' ' * la
                    btags += ' ' * lb
                inaczej:
                    podnieś ValueError('unknown tag %r' % (tag,))
            uzyskaj z self._qformat(aelt, belt, atags, btags)
        inaczej:
            # the synch pair jest identical
            uzyskaj '  ' + aelt

        # pump out diffs z after the synch point
        uzyskaj z self._fancy_helper(a, best_i+1, ahi, b, best_j+1, bhi)

    def _fancy_helper(self, a, alo, ahi, b, blo, bhi):
        g = []
        jeżeli alo < ahi:
            jeżeli blo < bhi:
                g = self._fancy_replace(a, alo, ahi, b, blo, bhi)
            inaczej:
                g = self._dump('-', a, alo, ahi)
        albo_inaczej blo < bhi:
            g = self._dump('+', b, blo, bhi)

        uzyskaj z g

    def _qformat(self, aline, bline, atags, btags):
        r"""
        Format "?" output oraz deal przy leading tabs.

        Example:

        >>> d = Differ()
        >>> results = d._qformat('\tabcDefghiJkl\n', '\tabcdefGhijkl\n',
        ...                      '  ^ ^  ^      ', '  ^ ^  ^      ')
        >>> dla line w results: print(repr(line))
        ...
        '- \tabcDefghiJkl\n'
        '? \t ^ ^  ^\n'
        '+ \tabcdefGhijkl\n'
        '? \t ^ ^  ^\n'
        """

        # Can hurt, but will probably help most of the time.
        common = min(_count_leading(aline, "\t"),
                     _count_leading(bline, "\t"))
        common = min(common, _count_leading(atags[:common], " "))
        common = min(common, _count_leading(btags[:common], " "))
        atags = atags[common:].rstrip()
        btags = btags[common:].rstrip()

        uzyskaj "- " + aline
        jeżeli atags:
            uzyskaj "? %s%s\n" % ("\t" * common, atags)

        uzyskaj "+ " + bline
        jeżeli btags:
            uzyskaj "? %s%s\n" % ("\t" * common, btags)

# With respect to junk, an earlier version of ndiff simply refused to
# *start* a match przy a junk element.  The result was cases like this:
#     before: private Thread currentThread;
#     after:  private volatile Thread currentThread;
# If you consider whitespace to be junk, the longest contiguous match
# nie starting przy junk jest "e Thread currentThread".  So ndiff reported
# that "e volatil" was inserted between the 't' oraz the 'e' w "private".
# While an accurate view, to people that's absurd.  The current version
# looks dla matching blocks that are entirely junk-free, then extends the
# longest one of those jako far jako possible but only przy matching junk.
# So now "currentThread" jest matched, then extended to suck up the
# preceding blank; then "private" jest matched, oraz extended to suck up the
# following blank; then "Thread" jest matched; oraz finally ndiff reports
# that "volatile " was inserted before "Thread".  The only quibble
# remaining jest that perhaps it was really the case that " volatile"
# was inserted after "private".  I can live przy that <wink>.

zaimportuj re

def IS_LINE_JUNK(line, pat=re.compile(r"\s*#?\s*$").match):
    r"""
    Return 1 dla ignorable line: iff `line` jest blank albo contains a single '#'.

    Examples:

    >>> IS_LINE_JUNK('\n')
    Prawda
    >>> IS_LINE_JUNK('  #   \n')
    Prawda
    >>> IS_LINE_JUNK('hello\n')
    Nieprawda
    """

    zwróć pat(line) jest nie Nic

def IS_CHARACTER_JUNK(ch, ws=" \t"):
    r"""
    Return 1 dla ignorable character: iff `ch` jest a space albo tab.

    Examples:

    >>> IS_CHARACTER_JUNK(' ')
    Prawda
    >>> IS_CHARACTER_JUNK('\t')
    Prawda
    >>> IS_CHARACTER_JUNK('\n')
    Nieprawda
    >>> IS_CHARACTER_JUNK('x')
    Nieprawda
    """

    zwróć ch w ws


########################################################################
###  Unified Diff
########################################################################

def _format_range_unified(start, stop):
    'Convert range to the "ed" format'
    # Per the diff spec at http://www.unix.org/single_unix_specification/
    beginning = start + 1     # lines start numbering przy one
    length = stop - start
    jeżeli length == 1:
        zwróć '{}'.format(beginning)
    jeżeli nie length:
        beginning -= 1        # empty ranges begin at line just before the range
    zwróć '{},{}'.format(beginning, length)

def unified_diff(a, b, fromfile='', tofile='', fromfiledate='',
                 tofiledate='', n=3, lineterm='\n'):
    r"""
    Compare two sequences of lines; generate the delta jako a unified diff.

    Unified diffs are a compact way of showing line changes oraz a few
    lines of context.  The number of context lines jest set by 'n' which
    defaults to three.

    By default, the diff control lines (those przy ---, +++, albo @@) are
    created przy a trailing newline.  This jest helpful so that inputs
    created z file.readlines() result w diffs that are suitable for
    file.writelines() since both the inputs oraz outputs have trailing
    newlines.

    For inputs that do nie have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The unidiff format normally has a header dla filenames oraz modification
    times.  Any albo all of these may be specified using strings for
    'fromfile', 'tofile', 'fromfiledate', oraz 'tofiledate'.
    The modification times are normally expressed w the ISO 8601 format.

    Example:

    >>> dla line w unified_diff('one two three four'.split(),
    ...             'zero one tree four'.split(), 'Original', 'Current',
    ...             '2005-01-26 23:30:50', '2010-04-02 10:20:52',
    ...             lineterm=''):
    ...     print(line)                 # doctest: +NORMALIZE_WHITESPACE
    --- Original        2005-01-26 23:30:50
    +++ Current         2010-04-02 10:20:52
    @@ -1,4 +1,4 @@
    +zero
     one
    -two
    -three
    +tree
     four
    """

    _check_types(a, b, fromfile, tofile, fromfiledate, tofiledate, lineterm)
    started = Nieprawda
    dla group w SequenceMatcher(Nic,a,b).get_grouped_opcodes(n):
        jeżeli nie started:
            started = Prawda
            fromdate = '\t{}'.format(fromfiledate) jeżeli fromfiledate inaczej ''
            todate = '\t{}'.format(tofiledate) jeżeli tofiledate inaczej ''
            uzyskaj '--- {}{}{}'.format(fromfile, fromdate, lineterm)
            uzyskaj '+++ {}{}{}'.format(tofile, todate, lineterm)

        first, last = group[0], group[-1]
        file1_range = _format_range_unified(first[1], last[2])
        file2_range = _format_range_unified(first[3], last[4])
        uzyskaj '@@ -{} +{} @@{}'.format(file1_range, file2_range, lineterm)

        dla tag, i1, i2, j1, j2 w group:
            jeżeli tag == 'equal':
                dla line w a[i1:i2]:
                    uzyskaj ' ' + line
                kontynuuj
            jeżeli tag w {'replace', 'delete'}:
                dla line w a[i1:i2]:
                    uzyskaj '-' + line
            jeżeli tag w {'replace', 'insert'}:
                dla line w b[j1:j2]:
                    uzyskaj '+' + line


########################################################################
###  Context Diff
########################################################################

def _format_range_context(start, stop):
    'Convert range to the "ed" format'
    # Per the diff spec at http://www.unix.org/single_unix_specification/
    beginning = start + 1     # lines start numbering przy one
    length = stop - start
    jeżeli nie length:
        beginning -= 1        # empty ranges begin at line just before the range
    jeżeli length <= 1:
        zwróć '{}'.format(beginning)
    zwróć '{},{}'.format(beginning, beginning + length - 1)

# See http://www.unix.org/single_unix_specification/
def context_diff(a, b, fromfile='', tofile='',
                 fromfiledate='', tofiledate='', n=3, lineterm='\n'):
    r"""
    Compare two sequences of lines; generate the delta jako a context diff.

    Context diffs are a compact way of showing line changes oraz a few
    lines of context.  The number of context lines jest set by 'n' which
    defaults to three.

    By default, the diff control lines (those przy *** albo ---) are
    created przy a trailing newline.  This jest helpful so that inputs
    created z file.readlines() result w diffs that are suitable for
    file.writelines() since both the inputs oraz outputs have trailing
    newlines.

    For inputs that do nie have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The context diff format normally has a header dla filenames oraz
    modification times.  Any albo all of these may be specified using
    strings dla 'fromfile', 'tofile', 'fromfiledate', oraz 'tofiledate'.
    The modification times are normally expressed w the ISO 8601 format.
    If nie specified, the strings default to blanks.

    Example:

    >>> print(''.join(context_diff('one\ntwo\nthree\nfour\n'.splitlines(Prawda),
    ...       'zero\none\ntree\nfour\n'.splitlines(Prawda), 'Original', 'Current')),
    ...       end="")
    *** Original
    --- Current
    ***************
    *** 1,4 ****
      one
    ! two
    ! three
      four
    --- 1,4 ----
    + zero
      one
    ! tree
      four
    """

    _check_types(a, b, fromfile, tofile, fromfiledate, tofiledate, lineterm)
    prefix = dict(insert='+ ', delete='- ', replace='! ', equal='  ')
    started = Nieprawda
    dla group w SequenceMatcher(Nic,a,b).get_grouped_opcodes(n):
        jeżeli nie started:
            started = Prawda
            fromdate = '\t{}'.format(fromfiledate) jeżeli fromfiledate inaczej ''
            todate = '\t{}'.format(tofiledate) jeżeli tofiledate inaczej ''
            uzyskaj '*** {}{}{}'.format(fromfile, fromdate, lineterm)
            uzyskaj '--- {}{}{}'.format(tofile, todate, lineterm)

        first, last = group[0], group[-1]
        uzyskaj '***************' + lineterm

        file1_range = _format_range_context(first[1], last[2])
        uzyskaj '*** {} ****{}'.format(file1_range, lineterm)

        jeżeli any(tag w {'replace', 'delete'} dla tag, _, _, _, _ w group):
            dla tag, i1, i2, _, _ w group:
                jeżeli tag != 'insert':
                    dla line w a[i1:i2]:
                        uzyskaj prefix[tag] + line

        file2_range = _format_range_context(first[3], last[4])
        uzyskaj '--- {} ----{}'.format(file2_range, lineterm)

        jeżeli any(tag w {'replace', 'insert'} dla tag, _, _, _, _ w group):
            dla tag, _, _, j1, j2 w group:
                jeżeli tag != 'delete':
                    dla line w b[j1:j2]:
                        uzyskaj prefix[tag] + line

def _check_types(a, b, *args):
    # Checking types jest weird, but the alternative jest garbled output when
    # someone dalejes mixed bytes oraz str to {unified,context}_diff(). E.g.
    # without this check, dalejing filenames jako bytes results w output like
    #   --- b'oldfile.txt'
    #   +++ b'newfile.txt'
    # because of how str.format() incorporates bytes objects.
    jeżeli a oraz nie isinstance(a[0], str):
        podnieś TypeError('lines to compare must be str, nie %s (%r)' %
                        (type(a[0]).__name__, a[0]))
    jeżeli b oraz nie isinstance(b[0], str):
        podnieś TypeError('lines to compare must be str, nie %s (%r)' %
                        (type(b[0]).__name__, b[0]))
    dla arg w args:
        jeżeli nie isinstance(arg, str):
            podnieś TypeError('all arguments must be str, not: %r' % (arg,))

def diff_bytes(dfunc, a, b, fromfile=b'', tofile=b'',
               fromfiledate=b'', tofiledate=b'', n=3, lineterm=b'\n'):
    r"""
    Compare `a` oraz `b`, two sequences of lines represented jako bytes rather
    than str. This jest a wrapper dla `dfunc`, which jest typically either
    unified_diff() albo context_diff(). Inputs are losslessly converted to
    strings so that `dfunc` only has to worry about strings, oraz encoded
    back to bytes on return. This jest necessary to compare files with
    unknown albo inconsistent encoding. All other inputs (wyjąwszy `n`) must be
    bytes rather than str.
    """
    def decode(s):
        spróbuj:
            zwróć s.decode('ascii', 'surrogateescape')
        wyjąwszy AttributeError jako err:
            msg = ('all arguments must be bytes, nie %s (%r)' %
                   (type(s).__name__, s))
            podnieś TypeError(msg) z err
    a = list(map(decode, a))
    b = list(map(decode, b))
    fromfile = decode(fromfile)
    tofile = decode(tofile)
    fromfiledate = decode(fromfiledate)
    tofiledate = decode(tofiledate)
    lineterm = decode(lineterm)

    lines = dfunc(a, b, fromfile, tofile, fromfiledate, tofiledate, n, lineterm)
    dla line w lines:
        uzyskaj line.encode('ascii', 'surrogateescape')

def ndiff(a, b, linejunk=Nic, charjunk=IS_CHARACTER_JUNK):
    r"""
    Compare `a` oraz `b` (lists of strings); zwróć a `Differ`-style delta.

    Optional keyword parameters `linejunk` oraz `charjunk` are dla filter
    functions, albo can be Nic:

    - linejunk: A function that should accept a single string argument oraz
      zwróć true iff the string jest junk.  The default jest Nic, oraz jest
      recommended; the underlying SequenceMatcher klasa has an adaptive
      notion of "noise" lines.

    - charjunk: A function that accepts a character (string of length
      1), oraz returns true iff the character jest junk. The default jest
      the module-level function IS_CHARACTER_JUNK, which filters out
      whitespace characters (a blank albo tab; note: it's a bad idea to
      include newline w this!).

    Tools/scripts/ndiff.py jest a command-line front-end to this function.

    Example:

    >>> diff = ndiff('one\ntwo\nthree\n'.splitlines(keepends=Prawda),
    ...              'ore\ntree\nemu\n'.splitlines(keepends=Prawda))
    >>> print(''.join(diff), end="")
    - one
    ?  ^
    + ore
    ?  ^
    - two
    - three
    ?  -
    + tree
    + emu
    """
    zwróć Differ(linejunk, charjunk).compare(a, b)

def _mdiff(fromlines, tolines, context=Nic, linejunk=Nic,
           charjunk=IS_CHARACTER_JUNK):
    r"""Returns generator uzyskajing marked up from/to side by side differences.

    Arguments:
    fromlines -- list of text lines to compared to tolines
    tolines -- list of text lines to be compared to fromlines
    context -- number of context lines to display on each side of difference,
               jeżeli Nic, all from/to text lines will be generated.
    linejunk -- dalejed on to ndiff (see ndiff documentation)
    charjunk -- dalejed on to ndiff (see ndiff documentation)

    This function returns an iterator which returns a tuple:
    (z line tuple, to line tuple, boolean flag)

    from/to line tuple -- (line num, line text)
        line num -- integer albo Nic (to indicate a context separation)
        line text -- original line text przy following markers inserted:
            '\0+' -- marks start of added text
            '\0-' -- marks start of deleted text
            '\0^' -- marks start of changed text
            '\1' -- marks end of added/deleted/changed text

    boolean flag -- Nic indicates context separation, Prawda indicates
        either "from" albo "to" line contains a change, otherwise Nieprawda.

    This function/iterator was originally developed to generate side by side
    file difference dla making HTML pages (see HtmlDiff klasa dla example
    usage).

    Note, this function utilizes the ndiff function to generate the side by
    side difference markup.  Optional ndiff arguments may be dalejed to this
    function oraz they w turn will be dalejed to ndiff.
    """
    zaimportuj re

    # regular expression dla finding intraline change indices
    change_re = re.compile('(\++|\-+|\^+)')

    # create the difference iterator to generate the differences
    diff_lines_iterator = ndiff(fromlines,tolines,linejunk,charjunk)

    def _make_line(lines, format_key, side, num_lines=[0,0]):
        """Returns line of text przy user's change markup oraz line formatting.

        lines -- list of lines z the ndiff generator to produce a line of
                 text from.  When producing the line of text to return, the
                 lines used are removed z this list.
        format_key -- '+' zwróć first line w list przy "add" markup around
                          the entire line.
                      '-' zwróć first line w list przy "delete" markup around
                          the entire line.
                      '?' zwróć first line w list przy add/delete/change
                          intraline markup (indices obtained z second line)
                      Nic zwróć first line w list przy no markup
        side -- indice into the num_lines list (0=from,1=to)
        num_lines -- from/to current line number.  This jest NOT intended to be a
                     dalejed parameter.  It jest present jako a keyword argument to
                     maintain memory of the current line numbers between calls
                     of this function.

        Note, this function jest purposefully nie defined at the module scope so
        that data it needs z its parent function (within whose context it
        jest defined) does nie need to be of module scope.
        """
        num_lines[side] += 1
        # Handle case where no user markup jest to be added, just zwróć line of
        # text przy user's line format to allow dla usage of the line number.
        jeżeli format_key jest Nic:
            zwróć (num_lines[side],lines.pop(0)[2:])
        # Handle case of intraline changes
        jeżeli format_key == '?':
            text, markers = lines.pop(0), lines.pop(0)
            # find intraline changes (store change type oraz indices w tuples)
            sub_info = []
            def record_sub_info(match_object,sub_info=sub_info):
                sub_info.append([match_object.group(1)[0],match_object.span()])
                zwróć match_object.group(1)
            change_re.sub(record_sub_info,markers)
            # process each tuple inserting our special marks that won't be
            # noticed by an xml/html escaper.
            dla key,(begin,end) w reversed(sub_info):
                text = text[0:begin]+'\0'+key+text[begin:end]+'\1'+text[end:]
            text = text[2:]
        # Handle case of add/delete entire line
        inaczej:
            text = lines.pop(0)[2:]
            # jeżeli line of text jest just a newline, insert a space so there jest
            # something dla the user to highlight oraz see.
            jeżeli nie text:
                text = ' '
            # insert marks that won't be noticed by an xml/html escaper.
            text = '\0' + format_key + text + '\1'
        # Return line of text, first allow user's line formatter to do its
        # thing (such jako adding the line number) then replace the special
        # marks przy what the user's change markup.
        zwróć (num_lines[side],text)

    def _line_iterator():
        """Yields from/to lines of text przy a change indication.

        This function jest an iterator.  It itself pulls lines z a
        differencing iterator, processes them oraz uzyskajs them.  When it can
        it uzyskajs both a "from" oraz a "to" line, otherwise it will uzyskaj one
        albo the other.  In addition to uzyskajing the lines of from/to text, a
        boolean flag jest uzyskajed to indicate jeżeli the text line(s) have
        differences w them.

        Note, this function jest purposefully nie defined at the module scope so
        that data it needs z its parent function (within whose context it
        jest defined) does nie need to be of module scope.
        """
        lines = []
        num_blanks_pending, num_blanks_to_uzyskaj = 0, 0
        dopóki Prawda:
            # Load up next 4 lines so we can look ahead, create strings which
            # are a concatenation of the first character of each of the 4 lines
            # so we can do some very readable comparisons.
            dopóki len(lines) < 4:
                lines.append(next(diff_lines_iterator, 'X'))
            s = ''.join([line[0] dla line w lines])
            jeżeli s.startswith('X'):
                # When no more lines, pump out any remaining blank lines so the
                # corresponding add/delete lines get a matching blank line so
                # all line pairs get uzyskajed at the next level.
                num_blanks_to_uzyskaj = num_blanks_pending
            albo_inaczej s.startswith('-?+?'):
                # simple intraline change
                uzyskaj _make_line(lines,'?',0), _make_line(lines,'?',1), Prawda
                kontynuuj
            albo_inaczej s.startswith('--++'):
                # w delete block, add block coming: we do NOT want to get
                # caught up on blank lines yet, just process the delete line
                num_blanks_pending -= 1
                uzyskaj _make_line(lines,'-',0), Nic, Prawda
                kontynuuj
            albo_inaczej s.startswith(('--?+', '--+', '- ')):
                # w delete block oraz see a intraline change albo unchanged line
                # coming: uzyskaj the delete line oraz then blanks
                from_line,to_line = _make_line(lines,'-',0), Nic
                num_blanks_to_uzyskaj,num_blanks_pending = num_blanks_pending-1,0
            albo_inaczej s.startswith('-+?'):
                # intraline change
                uzyskaj _make_line(lines,Nic,0), _make_line(lines,'?',1), Prawda
                kontynuuj
            albo_inaczej s.startswith('-?+'):
                # intraline change
                uzyskaj _make_line(lines,'?',0), _make_line(lines,Nic,1), Prawda
                kontynuuj
            albo_inaczej s.startswith('-'):
                # delete FROM line
                num_blanks_pending -= 1
                uzyskaj _make_line(lines,'-',0), Nic, Prawda
                kontynuuj
            albo_inaczej s.startswith('+--'):
                # w add block, delete block coming: we do NOT want to get
                # caught up on blank lines yet, just process the add line
                num_blanks_pending += 1
                uzyskaj Nic, _make_line(lines,'+',1), Prawda
                kontynuuj
            albo_inaczej s.startswith(('+ ', '+-')):
                # will be leaving an add block: uzyskaj blanks then add line
                from_line, to_line = Nic, _make_line(lines,'+',1)
                num_blanks_to_uzyskaj,num_blanks_pending = num_blanks_pending+1,0
            albo_inaczej s.startswith('+'):
                # inside an add block, uzyskaj the add line
                num_blanks_pending += 1
                uzyskaj Nic, _make_line(lines,'+',1), Prawda
                kontynuuj
            albo_inaczej s.startswith(' '):
                # unchanged text, uzyskaj it to both sides
                uzyskaj _make_line(lines[:],Nic,0),_make_line(lines,Nic,1),Nieprawda
                kontynuuj
            # Catch up on the blank lines so when we uzyskaj the next from/to
            # pair, they are lined up.
            while(num_blanks_to_uzyskaj < 0):
                num_blanks_to_uzyskaj += 1
                uzyskaj Nic,('','\n'),Prawda
            while(num_blanks_to_uzyskaj > 0):
                num_blanks_to_uzyskaj -= 1
                uzyskaj ('','\n'),Nic,Prawda
            jeżeli s.startswith('X'):
                zwróć
            inaczej:
                uzyskaj from_line,to_line,Prawda

    def _line_pair_iterator():
        """Yields from/to lines of text przy a change indication.

        This function jest an iterator.  It itself pulls lines z the line
        iterator.  Its difference z that iterator jest that this function
        always uzyskajs a pair of from/to text lines (przy the change
        indication).  If necessary it will collect single from/to lines
        until it has a matching pair from/to pair to uzyskaj.

        Note, this function jest purposefully nie defined at the module scope so
        that data it needs z its parent function (within whose context it
        jest defined) does nie need to be of module scope.
        """
        line_iterator = _line_iterator()
        fromlines,tolines=[],[]
        dopóki Prawda:
            # Collecting lines of text until we have a from/to pair
            dopóki (len(fromlines)==0 albo len(tolines)==0):
                spróbuj:
                    from_line, to_line, found_diff = next(line_iterator)
                wyjąwszy StopIteration:
                    zwróć
                jeżeli from_line jest nie Nic:
                    fromlines.append((from_line,found_diff))
                jeżeli to_line jest nie Nic:
                    tolines.append((to_line,found_diff))
            # Once we have a pair, remove them z the collection oraz uzyskaj it
            from_line, fromDiff = fromlines.pop(0)
            to_line, to_diff = tolines.pop(0)
            uzyskaj (from_line,to_line,fromDiff albo to_diff)

    # Handle case where user does nie want context differencing, just uzyskaj
    # them up without doing anything inaczej przy them.
    line_pair_iterator = _line_pair_iterator()
    jeżeli context jest Nic:
        uzyskaj z line_pair_iterator
    # Handle case where user wants context differencing.  We must do some
    # storage of lines until we know dla sure that they are to be uzyskajed.
    inaczej:
        context += 1
        lines_to_write = 0
        dopóki Prawda:
            # Store lines up until we find a difference, note use of a
            # circular queue because we only need to keep around what
            # we need dla context.
            index, contextLines = 0, [Nic]*(context)
            found_diff = Nieprawda
            while(found_diff jest Nieprawda):
                spróbuj:
                    from_line, to_line, found_diff = next(line_pair_iterator)
                wyjąwszy StopIteration:
                    zwróć
                i = index % context
                contextLines[i] = (from_line, to_line, found_diff)
                index += 1
            # Yield lines that we have collected so far, but first uzyskaj
            # the user's separator.
            jeżeli index > context:
                uzyskaj Nic, Nic, Nic
                lines_to_write = context
            inaczej:
                lines_to_write = index
                index = 0
            while(lines_to_write):
                i = index % context
                index += 1
                uzyskaj contextLines[i]
                lines_to_write -= 1
            # Now uzyskaj the context lines after the change
            lines_to_write = context-1
            while(lines_to_write):
                from_line, to_line, found_diff = next(line_pair_iterator)
                # If another change within the context, extend the context
                jeżeli found_diff:
                    lines_to_write = context-1
                inaczej:
                    lines_to_write -= 1
                uzyskaj from_line, to_line, found_diff


_file_template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html>

<head>
    <meta http-equiv="Content-Type"
          content="text/html; charset=%(charset)s" />
    <title></title>
    <style type="text/css">%(styles)s
    </style>
</head>

<body>
    %(table)s%(legend)s
</body>

</html>"""

_styles = """
        table.diff {font-family:Courier; border:medium;}
        .diff_header {background-color:#e0e0e0}
        td.diff_header {text-align:right}
        .diff_next {background-color:#c0c0c0}
        .diff_add {background-color:#aaffaa}
        .diff_chg {background-color:#ffff77}
        .diff_sub {background-color:#ffaaaa}"""

_table_template = """
    <table class="diff" id="difflib_chg_%(prefix)s_top"
           cellspacing="0" cellpadding="0" rules="groups" >
        <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>
        <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>
        %(header_row)s
        <tbody>
%(data_rows)s        </tbody>
    </table>"""

_legend = """
    <table class="diff" summary="Legends">
        <tr> <th colspan="2"> Legends </th> </tr>
        <tr> <td> <table border="" summary="Colors">
                      <tr><th> Colors </th> </tr>
                      <tr><td class="diff_add">&nbsp;Added&nbsp;</td></tr>
                      <tr><td class="diff_chg">Changed</td> </tr>
                      <tr><td class="diff_sub">Deleted</td> </tr>
                  </table></td>
             <td> <table border="" summary="Links">
                      <tr><th colspan="2"> Links </th> </tr>
                      <tr><td>(f)irst change</td> </tr>
                      <tr><td>(n)ext change</td> </tr>
                      <tr><td>(t)op</td> </tr>
                  </table></td> </tr>
    </table>"""

klasa HtmlDiff(object):
    """For producing HTML side by side comparison przy change highlights.

    This klasa can be used to create an HTML table (or a complete HTML file
    containing the table) showing a side by side, line by line comparison
    of text przy inter-line oraz intra-line change highlights.  The table can
    be generated w either full albo contextual difference mode.

    The following methods are provided dla HTML generation:

    make_table -- generates HTML dla a single side by side table
    make_file -- generates complete HTML file przy a single side by side table

    See tools/scripts/diff.py dla an example usage of this class.
    """

    _file_template = _file_template
    _styles = _styles
    _table_template = _table_template
    _legend = _legend
    _default_prefix = 0

    def __init__(self,tabsize=8,wrapcolumn=Nic,linejunk=Nic,
                 charjunk=IS_CHARACTER_JUNK):
        """HtmlDiff instance initializer

        Arguments:
        tabsize -- tab stop spacing, defaults to 8.
        wrapcolumn -- column number where lines are broken oraz wrapped,
            defaults to Nic where lines are nie wrapped.
        linejunk,charjunk -- keyword arguments dalejed into ndiff() (used by
            HtmlDiff() to generate the side by side HTML differences).  See
            ndiff() documentation dla argument default values oraz descriptions.
        """
        self._tabsize = tabsize
        self._wrapcolumn = wrapcolumn
        self._linejunk = linejunk
        self._charjunk = charjunk

    def make_file(self, fromlines, tolines, fromdesc='', todesc='',
                  context=Nieprawda, numlines=5, *, charset='utf-8'):
        """Returns HTML file of side by side comparison przy change highlights

        Arguments:
        fromlines -- list of "from" lines
        tolines -- list of "to" lines
        fromdesc -- "from" file column header string
        todesc -- "to" file column header string
        context -- set to Prawda dla contextual differences (defaults to Nieprawda
            which shows full differences).
        numlines -- number of context lines.  When context jest set Prawda,
            controls number of lines displayed before oraz after the change.
            When context jest Nieprawda, controls the number of lines to place
            the "next" link anchors before the next change (so click of
            "next" link jumps to just before the change).
        charset -- charset of the HTML document
        """

        zwróć (self._file_template % dict(
            styles=self._styles,
            legend=self._legend,
            table=self.make_table(fromlines, tolines, fromdesc, todesc,
                                  context=context, numlines=numlines),
            charset=charset
        )).encode(charset, 'xmlcharrefreplace').decode(charset)

    def _tab_newline_replace(self,fromlines,tolines):
        """Returns from/to line lists przy tabs expanded oraz newlines removed.

        Instead of tab characters being replaced by the number of spaces
        needed to fill w to the next tab stop, this function will fill
        the space przy tab characters.  This jest done so that the difference
        algorithms can identify changes w a file when tabs are replaced by
        spaces oraz vice versa.  At the end of the HTML generation, the tab
        characters will be replaced przy a nonbreakable space.
        """
        def expand_tabs(line):
            # hide real spaces
            line = line.replace(' ','\0')
            # expand tabs into spaces
            line = line.expandtabs(self._tabsize)
            # replace spaces z expanded tabs back into tab characters
            # (we'll replace them przy markup after we do differencing)
            line = line.replace(' ','\t')
            zwróć line.replace('\0',' ').rstrip('\n')
        fromlines = [expand_tabs(line) dla line w fromlines]
        tolines = [expand_tabs(line) dla line w tolines]
        zwróć fromlines,tolines

    def _split_line(self,data_list,line_num,text):
        """Builds list of text lines by splitting text lines at wrap point

        This function will determine jeżeli the input text line needs to be
        wrapped (split) into separate lines.  If so, the first wrap point
        will be determined oraz the first line appended to the output
        text line list.  This function jest used recursively to handle
        the second part of the split line to further split it.
        """
        # jeżeli blank line albo context separator, just add it to the output list
        jeżeli nie line_num:
            data_list.append((line_num,text))
            zwróć

        # jeżeli line text doesn't need wrapping, just add it to the output list
        size = len(text)
        max = self._wrapcolumn
        jeżeli (size <= max) albo ((size -(text.count('\0')*3)) <= max):
            data_list.append((line_num,text))
            zwróć

        # scan text looking dla the wrap point, keeping track jeżeli the wrap
        # point jest inside markers
        i = 0
        n = 0
        mark = ''
        dopóki n < max oraz i < size:
            jeżeli text[i] == '\0':
                i += 1
                mark = text[i]
                i += 1
            albo_inaczej text[i] == '\1':
                i += 1
                mark = ''
            inaczej:
                i += 1
                n += 1

        # wrap point jest inside text, przerwij it up into separate lines
        line1 = text[:i]
        line2 = text[i:]

        # jeżeli wrap point jest inside markers, place end marker at end of first
        # line oraz start marker at beginning of second line because each
        # line will have its own table tag markup around it.
        jeżeli mark:
            line1 = line1 + '\1'
            line2 = '\0' + mark + line2

        # tack on first line onto the output list
        data_list.append((line_num,line1))

        # use this routine again to wrap the remaining text
        self._split_line(data_list,'>',line2)

    def _line_wrapper(self,diffs):
        """Returns iterator that splits (wraps) mdiff text lines"""

        # pull from/to data oraz flags z mdiff iterator
        dla fromdata,todata,flag w diffs:
            # check dla context separators oraz dalej them through
            jeżeli flag jest Nic:
                uzyskaj fromdata,todata,flag
                kontynuuj
            (fromline,fromtext),(toline,totext) = fromdata,todata
            # dla each from/to line split it at the wrap column to form
            # list of text lines.
            fromlist,tolist = [],[]
            self._split_line(fromlist,fromline,fromtext)
            self._split_line(tolist,toline,totext)
            # uzyskaj from/to line w pairs inserting blank lines as
            # necessary when one side has more wrapped lines
            dopóki fromlist albo tolist:
                jeżeli fromlist:
                    fromdata = fromlist.pop(0)
                inaczej:
                    fromdata = ('',' ')
                jeżeli tolist:
                    todata = tolist.pop(0)
                inaczej:
                    todata = ('',' ')
                uzyskaj fromdata,todata,flag

    def _collect_lines(self,diffs):
        """Collects mdiff output into separate lists

        Before storing the mdiff from/to data into a list, it jest converted
        into a single line of text przy HTML markup.
        """

        fromlist,tolist,flaglist = [],[],[]
        # pull from/to data oraz flags z mdiff style iterator
        dla fromdata,todata,flag w diffs:
            spróbuj:
                # store HTML markup of the lines into the lists
                fromlist.append(self._format_line(0,flag,*fromdata))
                tolist.append(self._format_line(1,flag,*todata))
            wyjąwszy TypeError:
                # exceptions occur dla lines where context separators go
                fromlist.append(Nic)
                tolist.append(Nic)
            flaglist.append(flag)
        zwróć fromlist,tolist,flaglist

    def _format_line(self,side,flag,linenum,text):
        """Returns HTML markup of "from" / "to" text lines

        side -- 0 albo 1 indicating "from" albo "to" text
        flag -- indicates jeżeli difference on line
        linenum -- line number (used dla line number column)
        text -- line text to be marked up
        """
        spróbuj:
            linenum = '%d' % linenum
            id = ' id="%s%s"' % (self._prefix[side],linenum)
        wyjąwszy TypeError:
            # handle blank lines where linenum jest '>' albo ''
            id = ''
        # replace those things that would get confused przy HTML symbols
        text=text.replace("&","&amp;").replace(">","&gt;").replace("<","&lt;")

        # make space non-breakable so they don't get compressed albo line wrapped
        text = text.replace(' ','&nbsp;').rstrip()

        zwróć '<td class="diff_header"%s>%s</td><td nowrap="nowrap">%s</td>' \
               % (id,linenum,text)

    def _make_prefix(self):
        """Create unique anchor prefixes"""

        # Generate a unique anchor prefix so multiple tables
        # can exist on the same HTML page without conflicts.
        fromprefix = "from%d_" % HtmlDiff._default_prefix
        toprefix = "to%d_" % HtmlDiff._default_prefix
        HtmlDiff._default_prefix += 1
        # store prefixes so line format method has access
        self._prefix = [fromprefix,toprefix]

    def _convert_flags(self,fromlist,tolist,flaglist,context,numlines):
        """Makes list of "next" links"""

        # all anchor names will be generated using the unique "to" prefix
        toprefix = self._prefix[1]

        # process change flags, generating middle column of next anchors/links
        next_id = ['']*len(flaglist)
        next_href = ['']*len(flaglist)
        num_chg, in_change = 0, Nieprawda
        last = 0
        dla i,flag w enumerate(flaglist):
            jeżeli flag:
                jeżeli nie in_change:
                    in_change = Prawda
                    last = i
                    # at the beginning of a change, drop an anchor a few lines
                    # (the context lines) before the change dla the previous
                    # link
                    i = max([0,i-numlines])
                    next_id[i] = ' id="difflib_chg_%s_%d"' % (toprefix,num_chg)
                    # at the beginning of a change, drop a link to the next
                    # change
                    num_chg += 1
                    next_href[last] = '<a href="#difflib_chg_%s_%d">n</a>' % (
                         toprefix,num_chg)
            inaczej:
                in_change = Nieprawda
        # check dla cases where there jest no content to avoid exceptions
        jeżeli nie flaglist:
            flaglist = [Nieprawda]
            next_id = ['']
            next_href = ['']
            last = 0
            jeżeli context:
                fromlist = ['<td></td><td>&nbsp;No Differences Found&nbsp;</td>']
                tolist = fromlist
            inaczej:
                fromlist = tolist = ['<td></td><td>&nbsp;Empty File&nbsp;</td>']
        # jeżeli nie a change on first line, drop a link
        jeżeli nie flaglist[0]:
            next_href[0] = '<a href="#difflib_chg_%s_0">f</a>' % toprefix
        # redo the last link to link to the top
        next_href[last] = '<a href="#difflib_chg_%s_top">t</a>' % (toprefix)

        zwróć fromlist,tolist,flaglist,next_href,next_id

    def make_table(self,fromlines,tolines,fromdesc='',todesc='',context=Nieprawda,
                   numlines=5):
        """Returns HTML table of side by side comparison przy change highlights

        Arguments:
        fromlines -- list of "from" lines
        tolines -- list of "to" lines
        fromdesc -- "from" file column header string
        todesc -- "to" file column header string
        context -- set to Prawda dla contextual differences (defaults to Nieprawda
            which shows full differences).
        numlines -- number of context lines.  When context jest set Prawda,
            controls number of lines displayed before oraz after the change.
            When context jest Nieprawda, controls the number of lines to place
            the "next" link anchors before the next change (so click of
            "next" link jumps to just before the change).
        """

        # make unique anchor prefixes so that multiple tables may exist
        # on the same page without conflict.
        self._make_prefix()

        # change tabs to spaces before it gets more difficult after we insert
        # markup
        fromlines,tolines = self._tab_newline_replace(fromlines,tolines)

        # create diffs iterator which generates side by side from/to data
        jeżeli context:
            context_lines = numlines
        inaczej:
            context_lines = Nic
        diffs = _mdiff(fromlines,tolines,context_lines,linejunk=self._linejunk,
                      charjunk=self._charjunk)

        # set up iterator to wrap lines that exceed desired width
        jeżeli self._wrapcolumn:
            diffs = self._line_wrapper(diffs)

        # collect up from/to lines oraz flags into lists (also format the lines)
        fromlist,tolist,flaglist = self._collect_lines(diffs)

        # process change flags, generating middle column of next anchors/links
        fromlist,tolist,flaglist,next_href,next_id = self._convert_flags(
            fromlist,tolist,flaglist,context,numlines)

        s = []
        fmt = '            <tr><td class="diff_next"%s>%s</td>%s' + \
              '<td class="diff_next">%s</td>%s</tr>\n'
        dla i w range(len(flaglist)):
            jeżeli flaglist[i] jest Nic:
                # mdiff uzyskajs Nic on separator lines skip the bogus ones
                # generated dla the first line
                jeżeli i > 0:
                    s.append('        </tbody>        \n        <tbody>\n')
            inaczej:
                s.append( fmt % (next_id[i],next_href[i],fromlist[i],
                                           next_href[i],tolist[i]))
        jeżeli fromdesc albo todesc:
            header_row = '<thead><tr>%s%s%s%s</tr></thead>' % (
                '<th class="diff_next"><br /></th>',
                '<th colspan="2" class="diff_header">%s</th>' % fromdesc,
                '<th class="diff_next"><br /></th>',
                '<th colspan="2" class="diff_header">%s</th>' % todesc)
        inaczej:
            header_row = ''

        table = self._table_template % dict(
            data_rows=''.join(s),
            header_row=header_row,
            prefix=self._prefix[1])

        zwróć table.replace('\0+','<span class="diff_add">'). \
                     replace('\0-','<span class="diff_sub">'). \
                     replace('\0^','<span class="diff_chg">'). \
                     replace('\1','</span>'). \
                     replace('\t','&nbsp;')

usuń re

def restore(delta, which):
    r"""
    Generate one of the two sequences that generated a delta.

    Given a `delta` produced by `Differ.compare()` albo `ndiff()`, extract
    lines originating z file 1 albo 2 (parameter `which`), stripping off line
    prefixes.

    Examples:

    >>> diff = ndiff('one\ntwo\nthree\n'.splitlines(keepends=Prawda),
    ...              'ore\ntree\nemu\n'.splitlines(keepends=Prawda))
    >>> diff = list(diff)
    >>> print(''.join(restore(diff, 1)), end="")
    one
    two
    three
    >>> print(''.join(restore(diff, 2)), end="")
    ore
    tree
    emu
    """
    spróbuj:
        tag = {1: "- ", 2: "+ "}[int(which)]
    wyjąwszy KeyError:
        podnieś ValueError('unknown delta choice (must be 1 albo 2): %r'
                           % which)
    prefixes = ("  ", tag)
    dla line w delta:
        jeżeli line[:2] w prefixes:
            uzyskaj line[2:]

def _test():
    zaimportuj doctest, difflib
    zwróć doctest.testmod(difflib)

jeżeli __name__ == "__main__":
    _test()
