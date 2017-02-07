#
# The ndarray object z _testbuffer.c jest a complete implementation of
# a PEP-3118 buffer provider. It jest independent z NumPy's ndarray
# oraz the tests don't require NumPy.
#
# If NumPy jest present, some tests check both ndarray implementations
# against each other.
#
# Most ndarray tests also check that memoryview(ndarray) behaves w
# the same way jako the original. Thus, a substantial part of the
# memoryview tests jest now w this module.
#

zaimportuj contextlib
zaimportuj unittest
z test zaimportuj support
z itertools zaimportuj permutations, product
z random zaimportuj randrange, sample, choice
z sysconfig zaimportuj get_config_var
zaimportuj warnings
zaimportuj sys, array, io
z decimal zaimportuj Decimal
z fractions zaimportuj Fraction

spróbuj:
    z _testbuffer zaimportuj *
wyjąwszy ImportError:
    ndarray = Nic

spróbuj:
    zaimportuj struct
wyjąwszy ImportError:
    struct = Nic

spróbuj:
    zaimportuj ctypes
wyjąwszy ImportError:
    ctypes = Nic

spróbuj:
    przy warnings.catch_warnings():
        z numpy zaimportuj ndarray jako numpy_array
wyjąwszy ImportError:
    numpy_array = Nic


SHORT_TEST = Prawda


# ======================================================================
#                    Random lists by format specifier
# ======================================================================

# Native format chars oraz their ranges.
NATIVE = {
    '?':0, 'c':0, 'b':0, 'B':0,
    'h':0, 'H':0, 'i':0, 'I':0,
    'l':0, 'L':0, 'n':0, 'N':0,
    'f':0, 'd':0, 'P':0
}

# NumPy does nie have 'n' albo 'N':
jeżeli numpy_array:
    usuń NATIVE['n']
    usuń NATIVE['N']

jeżeli struct:
    spróbuj:
        # Add "qQ" jeżeli present w native mode.
        struct.pack('Q', 2**64-1)
        NATIVE['q'] = 0
        NATIVE['Q'] = 0
    wyjąwszy struct.error:
        dalej

# Standard format chars oraz their ranges.
STANDARD = {
    '?':(0, 2),            'c':(0, 1<<8),
    'b':(-(1<<7), 1<<7),   'B':(0, 1<<8),
    'h':(-(1<<15), 1<<15), 'H':(0, 1<<16),
    'i':(-(1<<31), 1<<31), 'I':(0, 1<<32),
    'l':(-(1<<31), 1<<31), 'L':(0, 1<<32),
    'q':(-(1<<63), 1<<63), 'Q':(0, 1<<64),
    'f':(-(1<<63), 1<<63), 'd':(-(1<<1023), 1<<1023)
}

def native_type_range(fmt):
    """Return range of a native type."""
    jeżeli fmt == 'c':
        lh = (0, 256)
    albo_inaczej fmt == '?':
        lh = (0, 2)
    albo_inaczej fmt == 'f':
        lh = (-(1<<63), 1<<63)
    albo_inaczej fmt == 'd':
        lh = (-(1<<1023), 1<<1023)
    inaczej:
        dla exp w (128, 127, 64, 63, 32, 31, 16, 15, 8, 7):
            spróbuj:
                struct.pack(fmt, (1<<exp)-1)
                przerwij
            wyjąwszy struct.error:
                dalej
        lh = (-(1<<exp), 1<<exp) jeżeli exp & 1 inaczej (0, 1<<exp)
    zwróć lh

fmtdict = {
    '':NATIVE,
    '@':NATIVE,
    '<':STANDARD,
    '>':STANDARD,
    '=':STANDARD,
    '!':STANDARD
}

jeżeli struct:
    dla fmt w fmtdict['@']:
        fmtdict['@'][fmt] = native_type_range(fmt)

MEMORYVIEW = NATIVE.copy()
ARRAY = NATIVE.copy()
dla k w NATIVE:
    jeżeli nie k w "bBhHiIlLfd":
        usuń ARRAY[k]

BYTEFMT = NATIVE.copy()
dla k w NATIVE:
    jeżeli nie k w "Bbc":
        usuń BYTEFMT[k]

fmtdict['m']  = MEMORYVIEW
fmtdict['@m'] = MEMORYVIEW
fmtdict['a']  = ARRAY
fmtdict['b']  = BYTEFMT
fmtdict['@b']  = BYTEFMT

# Capabilities of the test objects:
MODE = 0
MULT = 1
cap = {         # format chars                  # multiplier
  'ndarray':    (['', '@', '<', '>', '=', '!'], ['', '1', '2', '3']),
  'array':      (['a'],                         ['']),
  'numpy':      ([''],                          ['']),
  'memoryview': (['@m', 'm'],                   ['']),
  'bytefmt':    (['@b', 'b'],                   ['']),
}

def randrange_fmt(mode, char, obj):
    """Return random item dla a type specified by a mode oraz a single
       format character."""
    x = randrange(*fmtdict[mode][char])
    jeżeli char == 'c':
        x = bytes([x])
        jeżeli obj == 'numpy' oraz x == b'\x00':
            # http://projects.scipy.org/numpy/ticket/1925
            x = b'\x01'
    jeżeli char == '?':
        x = bool(x)
    jeżeli char == 'f' albo char == 'd':
        x = struct.pack(char, x)
        x = struct.unpack(char, x)[0]
    zwróć x

def gen_item(fmt, obj):
    """Return single random item."""
    mode, chars = fmt.split('#')
    x = []
    dla c w chars:
        x.append(randrange_fmt(mode, c, obj))
    zwróć x[0] jeżeli len(x) == 1 inaczej tuple(x)

def gen_items(n, fmt, obj):
    """Return a list of random items (or a scalar)."""
    jeżeli n == 0:
        zwróć gen_item(fmt, obj)
    lst = [0] * n
    dla i w range(n):
        lst[i] = gen_item(fmt, obj)
    zwróć lst

def struct_items(n, obj):
    mode = choice(cap[obj][MODE])
    xfmt = mode + '#'
    fmt = mode.strip('amb')
    nmemb = randrange(2, 10) # number of struct members
    dla _ w range(nmemb):
        char = choice(tuple(fmtdict[mode]))
        multiplier = choice(cap[obj][MULT])
        xfmt += (char * int(multiplier jeżeli multiplier inaczej 1))
        fmt += (multiplier + char)
    items = gen_items(n, xfmt, obj)
    item = gen_item(xfmt, obj)
    zwróć fmt, items, item

def randitems(n, obj='ndarray', mode=Nic, char=Nic):
    """Return random format, items, item."""
    jeżeli mode jest Nic:
        mode = choice(cap[obj][MODE])
    jeżeli char jest Nic:
        char = choice(tuple(fmtdict[mode]))
    multiplier = choice(cap[obj][MULT])
    fmt = mode + '#' + char * int(multiplier jeżeli multiplier inaczej 1)
    items = gen_items(n, fmt, obj)
    item = gen_item(fmt, obj)
    fmt = mode.strip('amb') + multiplier + char
    zwróć fmt, items, item

def iter_mode(n, obj='ndarray'):
    """Iterate through supported mode/char combinations."""
    dla mode w cap[obj][MODE]:
        dla char w fmtdict[mode]:
            uzyskaj randitems(n, obj, mode, char)

def iter_format(nitems, testobj='ndarray'):
    """Yield (format, items, item) dla all possible modes oraz format
       characters plus one random compound format string."""
    dla t w iter_mode(nitems, testobj):
        uzyskaj t
    jeżeli testobj != 'ndarray':
        zwróć
    uzyskaj struct_items(nitems, testobj)


def is_byte_format(fmt):
    zwróć 'c' w fmt albo 'b' w fmt albo 'B' w fmt

def is_memoryview_format(fmt):
    """format suitable dla memoryview"""
    x = len(fmt)
    zwróć ((x == 1 albo (x == 2 oraz fmt[0] == '@')) oraz
            fmt[x-1] w MEMORYVIEW)

NON_BYTE_FORMAT = [c dla c w fmtdict['@'] jeżeli nie is_byte_format(c)]


# ======================================================================
#       Multi-dimensional tolist(), slicing oraz slice assignments
# ======================================================================

def atomp(lst):
    """Tuple items (representing structs) are regarded jako atoms."""
    zwróć nie isinstance(lst, list)

def listp(lst):
    zwróć isinstance(lst, list)

def prod(lst):
    """Product of list elements."""
    jeżeli len(lst) == 0:
        zwróć 0
    x = lst[0]
    dla v w lst[1:]:
        x *= v
    zwróć x

def strides_from_shape(ndim, shape, itemsize, layout):
    """Calculate strides of a contiguous array. Layout jest 'C' albo
       'F' (Fortran)."""
    jeżeli ndim == 0:
        zwróć ()
    jeżeli layout == 'C':
        strides = list(shape[1:]) + [itemsize]
        dla i w range(ndim-2, -1, -1):
            strides[i] *= strides[i+1]
    inaczej:
        strides = [itemsize] + list(shape[:-1])
        dla i w range(1, ndim):
            strides[i] *= strides[i-1]
    zwróć strides

def _ca(items, s):
    """Convert flat item list to the nested list representation of a
       multidimensional C array przy shape 's'."""
    jeżeli atomp(items):
        zwróć items
    jeżeli len(s) == 0:
        zwróć items[0]
    lst = [0] * s[0]
    stride = len(items) // s[0] jeżeli s[0] inaczej 0
    dla i w range(s[0]):
        start = i*stride
        lst[i] = _ca(items[start:start+stride], s[1:])
    zwróć lst

def _fa(items, s):
    """Convert flat item list to the nested list representation of a
       multidimensional Fortran array przy shape 's'."""
    jeżeli atomp(items):
        zwróć items
    jeżeli len(s) == 0:
        zwróć items[0]
    lst = [0] * s[0]
    stride = s[0]
    dla i w range(s[0]):
        lst[i] = _fa(items[i::stride], s[1:])
    zwróć lst

def carray(items, shape):
    jeżeli listp(items) oraz nie 0 w shape oraz prod(shape) != len(items):
        podnieś ValueError("prod(shape) != len(items)")
    zwróć _ca(items, shape)

def farray(items, shape):
    jeżeli listp(items) oraz nie 0 w shape oraz prod(shape) != len(items):
        podnieś ValueError("prod(shape) != len(items)")
    zwróć _fa(items, shape)

def indices(shape):
    """Generate all possible tuples of indices."""
    iterables = [range(v) dla v w shape]
    zwróć product(*iterables)

def getindex(ndim, ind, strides):
    """Convert multi-dimensional index to the position w the flat list."""
    ret = 0
    dla i w range(ndim):
        ret += strides[i] * ind[i]
    zwróć ret

def transpose(src, shape):
    """Transpose flat item list that jest regarded jako a multi-dimensional
       matrix defined by shape: dest...[k][j][i] = src[i][j][k]...  """
    jeżeli nie shape:
        zwróć src
    ndim = len(shape)
    sstrides = strides_from_shape(ndim, shape, 1, 'C')
    dstrides = strides_from_shape(ndim, shape[::-1], 1, 'C')
    dest = [0] * len(src)
    dla ind w indices(shape):
        fr = getindex(ndim, ind, sstrides)
        to = getindex(ndim, ind[::-1], dstrides)
        dest[to] = src[fr]
    zwróć dest

def _flatten(lst):
    """flatten list"""
    jeżeli lst == []:
        zwróć lst
    jeżeli atomp(lst):
        zwróć [lst]
    zwróć _flatten(lst[0]) + _flatten(lst[1:])

def flatten(lst):
    """flatten list albo zwróć scalar"""
    jeżeli atomp(lst): # scalar
        zwróć lst
    zwróć _flatten(lst)

def slice_shape(lst, slices):
    """Get the shape of lst after slicing: slices jest a list of slice
       objects."""
    jeżeli atomp(lst):
        zwróć []
    zwróć [len(lst[slices[0]])] + slice_shape(lst[0], slices[1:])

def multislice(lst, slices):
    """Multi-dimensional slicing: slices jest a list of slice objects."""
    jeżeli atomp(lst):
        zwróć lst
    zwróć [multislice(sublst, slices[1:]) dla sublst w lst[slices[0]]]

def m_assign(llst, rlst, lslices, rslices):
    """Multi-dimensional slice assignment: llst oraz rlst are the operands,
       lslices oraz rslices are lists of slice objects. llst oraz rlst must
       have the same structure.

       For a two-dimensional example, this jest nie implemented w Python:

         llst[0:3:2, 0:3:2] = rlst[1:3:1, 1:3:1]

       Instead we write:

         lslices = [slice(0,3,2), slice(0,3,2)]
         rslices = [slice(1,3,1), slice(1,3,1)]
         multislice_assign(llst, rlst, lslices, rslices)
    """
    jeżeli atomp(rlst):
        zwróć rlst
    rlst = [m_assign(l, r, lslices[1:], rslices[1:])
            dla l, r w zip(llst[lslices[0]], rlst[rslices[0]])]
    llst[lslices[0]] = rlst
    zwróć llst

def cmp_structure(llst, rlst, lslices, rslices):
    """Compare the structure of llst[lslices] oraz rlst[rslices]."""
    lshape = slice_shape(llst, lslices)
    rshape = slice_shape(rlst, rslices)
    jeżeli (len(lshape) != len(rshape)):
        zwróć -1
    dla i w range(len(lshape)):
        jeżeli lshape[i] != rshape[i]:
            zwróć -1
        jeżeli lshape[i] == 0:
            zwróć 0
    zwróć 0

def multislice_assign(llst, rlst, lslices, rslices):
    """Return llst after assigning: llst[lslices] = rlst[rslices]"""
    jeżeli cmp_structure(llst, rlst, lslices, rslices) < 0:
        podnieś ValueError("lvalue oraz rvalue have different structures")
    zwróć m_assign(llst, rlst, lslices, rslices)


# ======================================================================
#                          Random structures
# ======================================================================

#
# PEP-3118 jest very permissive przy respect to the contents of a
# Py_buffer. In particular:
#
#   - shape can be zero
#   - strides can be any integer, including zero
#   - offset can point to any location w the underlying
#     memory block, provided that it jest a multiple of
#     itemsize.
#
# The functions w this section test oraz verify random structures
# w full generality. A structure jest valid iff it fits w the
# underlying memory block.
#
# The structure 't' (short dla 'tuple') jest fully defined by:
#
#   t = (memlen, itemsize, ndim, shape, strides, offset)
#

def verify_structure(memlen, itemsize, ndim, shape, strides, offset):
    """Verify that the parameters represent a valid array within
       the bounds of the allocated memory:
           char *mem: start of the physical memory block
           memlen: length of the physical memory block
           offset: (char *)buf - mem
    """
    jeżeli offset % itemsize:
        zwróć Nieprawda
    jeżeli offset < 0 albo offset+itemsize > memlen:
        zwróć Nieprawda
    jeżeli any(v % itemsize dla v w strides):
        zwróć Nieprawda

    jeżeli ndim <= 0:
        zwróć ndim == 0 oraz nie shape oraz nie strides
    jeżeli 0 w shape:
        zwróć Prawda

    imin = sum(strides[j]*(shape[j]-1) dla j w range(ndim)
               jeżeli strides[j] <= 0)
    imax = sum(strides[j]*(shape[j]-1) dla j w range(ndim)
               jeżeli strides[j] > 0)

    zwróć 0 <= offset+imin oraz offset+imax+itemsize <= memlen

def get_item(lst, indices):
    dla i w indices:
        lst = lst[i]
    zwróć lst

def memory_index(indices, t):
    """Location of an item w the underlying memory."""
    memlen, itemsize, ndim, shape, strides, offset = t
    p = offset
    dla i w range(ndim):
        p += strides[i]*indices[i]
    zwróć p

def is_overlapping(t):
    """The structure 't' jest overlapping jeżeli at least one memory location
       jest visited twice dopóki iterating through all possible tuples of
       indices."""
    memlen, itemsize, ndim, shape, strides, offset = t
    visited = 1<<memlen
    dla ind w indices(shape):
        i = memory_index(ind, t)
        bit = 1<<i
        jeżeli visited & bit:
            zwróć Prawda
        visited |= bit
    zwróć Nieprawda

def rand_structure(itemsize, valid, maxdim=5, maxshape=16, shape=()):
    """Return random structure:
           (memlen, itemsize, ndim, shape, strides, offset)
       If 'valid' jest true, the returned structure jest valid, otherwise invalid.
       If 'shape' jest given, use that instead of creating a random shape.
    """
    jeżeli nie shape:
        ndim = randrange(maxdim+1)
        jeżeli (ndim == 0):
            jeżeli valid:
                zwróć itemsize, itemsize, ndim, (), (), 0
            inaczej:
                nitems = randrange(1, 16+1)
                memlen = nitems * itemsize
                offset = -itemsize jeżeli randrange(2) == 0 inaczej memlen
                zwróć memlen, itemsize, ndim, (), (), offset

        minshape = 2
        n = randrange(100)
        jeżeli n >= 95 oraz valid:
            minshape = 0
        albo_inaczej n >= 90:
            minshape = 1
        shape = [0] * ndim

        dla i w range(ndim):
            shape[i] = randrange(minshape, maxshape+1)
    inaczej:
        ndim = len(shape)

    maxstride = 5
    n = randrange(100)
    zero_stride = Prawda jeżeli n >= 95 oraz n & 1 inaczej Nieprawda

    strides = [0] * ndim
    strides[ndim-1] = itemsize * randrange(-maxstride, maxstride+1)
    jeżeli nie zero_stride oraz strides[ndim-1] == 0:
        strides[ndim-1] = itemsize

    dla i w range(ndim-2, -1, -1):
        maxstride *= shape[i+1] jeżeli shape[i+1] inaczej 1
        jeżeli zero_stride:
            strides[i] = itemsize * randrange(-maxstride, maxstride+1)
        inaczej:
            strides[i] = ((1,-1)[randrange(2)] *
                          itemsize * randrange(1, maxstride+1))

    imin = imax = 0
    jeżeli nie 0 w shape:
        imin = sum(strides[j]*(shape[j]-1) dla j w range(ndim)
                   jeżeli strides[j] <= 0)
        imax = sum(strides[j]*(shape[j]-1) dla j w range(ndim)
                   jeżeli strides[j] > 0)

    nitems = imax - imin
    jeżeli valid:
        offset = -imin * itemsize
        memlen = offset + (imax+1) * itemsize
    inaczej:
        memlen = (-imin + imax) * itemsize
        offset = -imin-itemsize jeżeli randrange(2) == 0 inaczej memlen
    zwróć memlen, itemsize, ndim, shape, strides, offset

def randslice_from_slicelen(slicelen, listlen):
    """Create a random slice of len slicelen that fits into listlen."""
    maxstart = listlen - slicelen
    start = randrange(maxstart+1)
    maxstep = (listlen - start) // slicelen jeżeli slicelen inaczej 1
    step = randrange(1, maxstep+1)
    stop = start + slicelen * step
    s = slice(start, stop, step)
    _, _, _, control = slice_indices(s, listlen)
    jeżeli control != slicelen:
        podnieś RuntimeError
    zwróć s

def randslice_from_shape(ndim, shape):
    """Create two sets of slices dla an array x przy shape 'shape'
       such that shapeof(x[lslices]) == shapeof(x[rslices])."""
    lslices = [0] * ndim
    rslices = [0] * ndim
    dla n w range(ndim):
        l = shape[n]
        slicelen = randrange(1, l+1) jeżeli l > 0 inaczej 0
        lslices[n] = randslice_from_slicelen(slicelen, l)
        rslices[n] = randslice_from_slicelen(slicelen, l)
    zwróć tuple(lslices), tuple(rslices)

def rand_aligned_slices(maxdim=5, maxshape=16):
    """Create (lshape, rshape, tuple(lslices), tuple(rslices)) such that
       shapeof(x[lslices]) == shapeof(y[rslices]), where x jest an array
       przy shape 'lshape' oraz y jest an array przy shape 'rshape'."""
    ndim = randrange(1, maxdim+1)
    minshape = 2
    n = randrange(100)
    jeżeli n >= 95:
        minshape = 0
    albo_inaczej n >= 90:
        minshape = 1
    all_random = Prawda jeżeli randrange(100) >= 80 inaczej Nieprawda
    lshape = [0]*ndim; rshape = [0]*ndim
    lslices = [0]*ndim; rslices = [0]*ndim

    dla n w range(ndim):
        small = randrange(minshape, maxshape+1)
        big = randrange(minshape, maxshape+1)
        jeżeli big < small:
            big, small = small, big

        # Create a slice that fits the smaller value.
        jeżeli all_random:
            start = randrange(-small, small+1)
            stop = randrange(-small, small+1)
            step = (1,-1)[randrange(2)] * randrange(1, small+2)
            s_small = slice(start, stop, step)
            _, _, _, slicelen = slice_indices(s_small, small)
        inaczej:
            slicelen = randrange(1, small+1) jeżeli small > 0 inaczej 0
            s_small = randslice_from_slicelen(slicelen, small)

        # Create a slice of the same length dla the bigger value.
        s_big = randslice_from_slicelen(slicelen, big)
        jeżeli randrange(2) == 0:
            rshape[n], lshape[n] = big, small
            rslices[n], lslices[n] = s_big, s_small
        inaczej:
            rshape[n], lshape[n] = small, big
            rslices[n], lslices[n] = s_small, s_big

    zwróć lshape, rshape, tuple(lslices), tuple(rslices)

def randitems_from_structure(fmt, t):
    """Return a list of random items dla structure 't' przy format
       'fmtchar'."""
    memlen, itemsize, _, _, _, _ = t
    zwróć gen_items(memlen//itemsize, '#'+fmt, 'numpy')

def ndarray_from_structure(items, fmt, t, flags=0):
    """Return ndarray z the tuple returned by rand_structure()"""
    memlen, itemsize, ndim, shape, strides, offset = t
    zwróć ndarray(items, shape=shape, strides=strides, format=fmt,
                   offset=offset, flags=ND_WRITABLE|flags)

def numpy_array_from_structure(items, fmt, t):
    """Return numpy_array z the tuple returned by rand_structure()"""
    memlen, itemsize, ndim, shape, strides, offset = t
    buf = bytearray(memlen)
    dla j, v w enumerate(items):
        struct.pack_into(fmt, buf, j*itemsize, v)
    zwróć numpy_array(buffer=buf, shape=shape, strides=strides,
                       dtype=fmt, offset=offset)


# ======================================================================
#                          memoryview casts
# ======================================================================

def cast_items(exporter, fmt, itemsize, shape=Nic):
    """Interpret the raw memory of 'exporter' jako a list of items with
       size 'itemsize'. If shape=Nic, the new structure jest assumed to
       be 1-D przy n * itemsize = bytelen. If shape jest given, the usual
       constraint dla contiguous arrays prod(shape) * itemsize = bytelen
       applies. On success, zwróć (items, shape). If the constraints
       cannot be met, zwróć (Nic, Nic). If a chunk of bytes jest interpreted
       jako NaN jako a result of float conversion, zwróć ('nan', Nic)."""
    bytelen = exporter.nbytes
    jeżeli shape:
        jeżeli prod(shape) * itemsize != bytelen:
            zwróć Nic, shape
    albo_inaczej shape == []:
        jeżeli exporter.ndim == 0 albo itemsize != bytelen:
            zwróć Nic, shape
    inaczej:
        n, r = divmod(bytelen, itemsize)
        shape = [n]
        jeżeli r != 0:
            zwróć Nic, shape

    mem = exporter.tobytes()
    byteitems = [mem[i:i+itemsize] dla i w range(0, len(mem), itemsize)]

    items = []
    dla v w byteitems:
        item = struct.unpack(fmt, v)[0]
        jeżeli item != item:
            zwróć 'nan', shape
        items.append(item)

    zwróć (items, shape) jeżeli shape != [] inaczej (items[0], shape)

def gencastshapes():
    """Generate shapes to test casting."""
    dla n w range(32):
        uzyskaj [n]
    ndim = randrange(4, 6)
    minshape = 1 jeżeli randrange(100) > 80 inaczej 2
    uzyskaj [randrange(minshape, 5) dla _ w range(ndim)]
    ndim = randrange(2, 4)
    minshape = 1 jeżeli randrange(100) > 80 inaczej 2
    uzyskaj [randrange(minshape, 5) dla _ w range(ndim)]


# ======================================================================
#                              Actual tests
# ======================================================================

def genslices(n):
    """Generate all possible slices dla a single dimension."""
    zwróć product(range(-n, n+1), range(-n, n+1), range(-n, n+1))

def genslices_ndim(ndim, shape):
    """Generate all possible slice tuples dla 'shape'."""
    iterables = [genslices(shape[n]) dla n w range(ndim)]
    zwróć product(*iterables)

def rslice(n, allow_empty=Nieprawda):
    """Generate random slice dla a single dimension of length n.
       If zero=Prawda, the slices may be empty, otherwise they will
       be non-empty."""
    minlen = 0 jeżeli allow_empty albo n == 0 inaczej 1
    slicelen = randrange(minlen, n+1)
    zwróć randslice_from_slicelen(slicelen, n)

def rslices(n, allow_empty=Nieprawda):
    """Generate random slices dla a single dimension."""
    dla _ w range(5):
        uzyskaj rslice(n, allow_empty)

def rslices_ndim(ndim, shape, iterations=5):
    """Generate random slice tuples dla 'shape'."""
    # non-empty slices
    dla _ w range(iterations):
        uzyskaj tuple(rslice(shape[n]) dla n w range(ndim))
    # possibly empty slices
    dla _ w range(iterations):
        uzyskaj tuple(rslice(shape[n], allow_empty=Prawda) dla n w range(ndim))
    # invalid slices
    uzyskaj tuple(slice(0,1,0) dla _ w range(ndim))

def rpermutation(iterable, r=Nic):
    pool = tuple(iterable)
    r = len(pool) jeżeli r jest Nic inaczej r
    uzyskaj tuple(sample(pool, r))

def ndarray_print(nd):
    """Print ndarray dla debugging."""
    spróbuj:
        x = nd.tolist()
    wyjąwszy (TypeError, NotImplementedError):
        x = nd.tobytes()
    jeżeli isinstance(nd, ndarray):
        offset = nd.offset
        flags = nd.flags
    inaczej:
        offset = 'unknown'
        flags = 'unknown'
    print("ndarray(%s, shape=%s, strides=%s, suboffsets=%s, offset=%s, "
          "format='%s', itemsize=%s, flags=%s)" %
          (x, nd.shape, nd.strides, nd.suboffsets, offset,
           nd.format, nd.itemsize, flags))
    sys.stdout.flush()


ITERATIONS = 100
MAXDIM = 5
MAXSHAPE = 10

jeżeli SHORT_TEST:
    ITERATIONS = 10
    MAXDIM = 3
    MAXSHAPE = 4
    genslices = rslices
    genslices_ndim = rslices_ndim
    permutations = rpermutation


@unittest.skipUnless(struct, 'struct module required dla this test.')
@unittest.skipUnless(ndarray, 'ndarray object required dla this test')
klasa TestBufferProtocol(unittest.TestCase):

    def setUp(self):
        # The suboffsets tests need sizeof(void *).
        self.sizeof_void_p = get_sizeof_void_p()

    def verify(self, result, obj=-1,
                     itemsize={1}, fmt=-1, readonly={1},
                     ndim={1}, shape=-1, strides=-1,
                     lst=-1, sliced=Nieprawda, cast=Nieprawda):
        # Verify buffer contents against expected values. Default values
        # are deliberately initialized to invalid types.
        jeżeli shape:
            expected_len = prod(shape)*itemsize
        inaczej:
            jeżeli nie fmt: # array has been implicitly cast to unsigned bytes
                expected_len = len(lst)
            inaczej: # ndim = 0
                expected_len = itemsize

        # Reconstruct suboffsets z strides. Support dla slicing
        # could be added, but jest currently only needed dla test_getbuf().
        suboffsets = ()
        jeżeli result.suboffsets:
            self.assertGreater(ndim, 0)

            suboffset0 = 0
            dla n w range(1, ndim):
                jeżeli shape[n] == 0:
                    przerwij
                jeżeli strides[n] <= 0:
                    suboffset0 += -strides[n] * (shape[n]-1)

            suboffsets = [suboffset0] + [-1 dla v w range(ndim-1)]

            # Not correct jeżeli slicing has occurred w the first dimension.
            stride0 = self.sizeof_void_p
            jeżeli strides[0] < 0:
                stride0 = -stride0
            strides = [stride0] + list(strides[1:])

        self.assertIs(result.obj, obj)
        self.assertEqual(result.nbytes, expected_len)
        self.assertEqual(result.itemsize, itemsize)
        self.assertEqual(result.format, fmt)
        self.assertEqual(result.readonly, readonly)
        self.assertEqual(result.ndim, ndim)
        self.assertEqual(result.shape, tuple(shape))
        jeżeli nie (sliced oraz suboffsets):
            self.assertEqual(result.strides, tuple(strides))
        self.assertEqual(result.suboffsets, tuple(suboffsets))

        jeżeli isinstance(result, ndarray) albo is_memoryview_format(fmt):
            rep = result.tolist() jeżeli fmt inaczej result.tobytes()
            self.assertEqual(rep, lst)

        jeżeli nie fmt: # array has been cast to unsigned bytes,
            zwróć  # the remaining tests won't work.

        # PyBuffer_GetPointer() jest the definition how to access an item.
        # If PyBuffer_GetPointer(indices) jest correct dla all possible
        # combinations of indices, the buffer jest correct.
        #
        # Also test tobytes() against the flattened 'lst', przy all items
        # packed to bytes.
        jeżeli nie cast: # casts chop up 'lst' w different ways
            b = bytearray()
            buf_err = Nic
            dla ind w indices(shape):
                spróbuj:
                    item1 = get_pointer(result, ind)
                    item2 = get_item(lst, ind)
                    jeżeli isinstance(item2, tuple):
                        x = struct.pack(fmt, *item2)
                    inaczej:
                        x = struct.pack(fmt, item2)
                    b.extend(x)
                wyjąwszy BufferError:
                    buf_err = Prawda # re-exporter does nie provide full buffer
                    przerwij
                self.assertEqual(item1, item2)

            jeżeli nie buf_err:
                # test tobytes()
                self.assertEqual(result.tobytes(), b)

                # lst := expected multi-dimensional logical representation
                # flatten(lst) := elements w C-order
                ff = fmt jeżeli fmt inaczej 'B'
                flattened = flatten(lst)

                # Rules dla 'A': jeżeli the array jest already contiguous, zwróć
                # the array unaltered. Otherwise, zwróć a contiguous 'C'
                # representation.
                dla order w ['C', 'F', 'A']:
                    expected = result
                    jeżeli order == 'F':
                        jeżeli nie is_contiguous(result, 'A') albo \
                           is_contiguous(result, 'C'):
                            # For constructing the ndarray, convert the
                            # flattened logical representation to Fortran order.
                            trans = transpose(flattened, shape)
                            expected = ndarray(trans, shape=shape, format=ff,
                                               flags=ND_FORTRAN)
                    inaczej: # 'C', 'A'
                        jeżeli nie is_contiguous(result, 'A') albo \
                           is_contiguous(result, 'F') oraz order == 'C':
                            # The flattened list jest already w C-order.
                            expected = ndarray(flattened, shape=shape, format=ff)

                    contig = get_contiguous(result, PyBUF_READ, order)
                    self.assertEqual(contig.tobytes(), b)
                    self.assertPrawda(cmp_contig(contig, expected))

                    jeżeli ndim == 0:
                        kontynuuj

                    nmemb = len(flattened)
                    ro = 0 jeżeli readonly inaczej ND_WRITABLE

                    ### See comment w test_py_buffer_to_contiguous dla an
                    ### explanation why these tests are valid.

                    # To 'C'
                    contig = py_buffer_to_contiguous(result, 'C', PyBUF_FULL_RO)
                    self.assertEqual(len(contig), nmemb * itemsize)
                    initlst = [struct.unpack_from(fmt, contig, n*itemsize)
                               dla n w range(nmemb)]
                    jeżeli len(initlst[0]) == 1:
                        initlst = [v[0] dla v w initlst]

                    y = ndarray(initlst, shape=shape, flags=ro, format=fmt)
                    self.assertEqual(memoryview(y), memoryview(result))

                    # To 'F'
                    contig = py_buffer_to_contiguous(result, 'F', PyBUF_FULL_RO)
                    self.assertEqual(len(contig), nmemb * itemsize)
                    initlst = [struct.unpack_from(fmt, contig, n*itemsize)
                               dla n w range(nmemb)]
                    jeżeli len(initlst[0]) == 1:
                        initlst = [v[0] dla v w initlst]

                    y = ndarray(initlst, shape=shape, flags=ro|ND_FORTRAN,
                                format=fmt)
                    self.assertEqual(memoryview(y), memoryview(result))

                    # To 'A'
                    contig = py_buffer_to_contiguous(result, 'A', PyBUF_FULL_RO)
                    self.assertEqual(len(contig), nmemb * itemsize)
                    initlst = [struct.unpack_from(fmt, contig, n*itemsize)
                               dla n w range(nmemb)]
                    jeżeli len(initlst[0]) == 1:
                        initlst = [v[0] dla v w initlst]

                    f = ND_FORTRAN jeżeli is_contiguous(result, 'F') inaczej 0
                    y = ndarray(initlst, shape=shape, flags=f|ro, format=fmt)
                    self.assertEqual(memoryview(y), memoryview(result))

        jeżeli is_memoryview_format(fmt):
            spróbuj:
                m = memoryview(result)
            wyjąwszy BufferError: # re-exporter does nie provide full information
                zwróć
            ex = result.obj jeżeli isinstance(result, memoryview) inaczej result
            self.assertIs(m.obj, ex)
            self.assertEqual(m.nbytes, expected_len)
            self.assertEqual(m.itemsize, itemsize)
            self.assertEqual(m.format, fmt)
            self.assertEqual(m.readonly, readonly)
            self.assertEqual(m.ndim, ndim)
            self.assertEqual(m.shape, tuple(shape))
            jeżeli nie (sliced oraz suboffsets):
                self.assertEqual(m.strides, tuple(strides))
            self.assertEqual(m.suboffsets, tuple(suboffsets))

            n = 1 jeżeli ndim == 0 inaczej len(lst)
            self.assertEqual(len(m), n)

            rep = result.tolist() jeżeli fmt inaczej result.tobytes()
            self.assertEqual(rep, lst)
            self.assertEqual(m, result)

    def verify_getbuf(self, orig_ex, ex, req, sliced=Nieprawda):
        def simple_fmt(ex):
            zwróć ex.format == '' albo ex.format == 'B'
        def match(req, flag):
            zwróć ((req&flag) == flag)

        jeżeli (# writable request to read-only exporter
            (ex.readonly oraz match(req, PyBUF_WRITABLE)) albo
            # cannot match explicit contiguity request
            (match(req, PyBUF_C_CONTIGUOUS) oraz nie ex.c_contiguous) albo
            (match(req, PyBUF_F_CONTIGUOUS) oraz nie ex.f_contiguous) albo
            (match(req, PyBUF_ANY_CONTIGUOUS) oraz nie ex.contiguous) albo
            # buffer needs suboffsets
            (nie match(req, PyBUF_INDIRECT) oraz ex.suboffsets) albo
            # buffer without strides must be C-contiguous
            (nie match(req, PyBUF_STRIDES) oraz nie ex.c_contiguous) albo
            # PyBUF_SIMPLE|PyBUF_FORMAT oraz PyBUF_WRITABLE|PyBUF_FORMAT
            (nie match(req, PyBUF_ND) oraz match(req, PyBUF_FORMAT))):

            self.assertRaises(BufferError, ndarray, ex, getbuf=req)
            zwróć

        jeżeli isinstance(ex, ndarray) albo is_memoryview_format(ex.format):
            lst = ex.tolist()
        inaczej:
            nd = ndarray(ex, getbuf=PyBUF_FULL_RO)
            lst = nd.tolist()

        # The consumer may have requested default values albo a NULL format.
        ro = 0 jeżeli match(req, PyBUF_WRITABLE) inaczej ex.readonly
        fmt = ex.format
        itemsize = ex.itemsize
        ndim = ex.ndim
        jeżeli nie match(req, PyBUF_FORMAT):
            # itemsize refers to the original itemsize before the cast.
            # The equality product(shape) * itemsize = len still holds.
            # The equality calcsize(format) = itemsize does _not_ hold.
            fmt = ''
            lst = orig_ex.tobytes() # Issue 12834
        jeżeli nie match(req, PyBUF_ND):
            ndim = 1
        shape = orig_ex.shape jeżeli match(req, PyBUF_ND) inaczej ()
        strides = orig_ex.strides jeżeli match(req, PyBUF_STRIDES) inaczej ()

        nd = ndarray(ex, getbuf=req)
        self.verify(nd, obj=ex,
                    itemsize=itemsize, fmt=fmt, readonly=ro,
                    ndim=ndim, shape=shape, strides=strides,
                    lst=lst, sliced=sliced)

    def test_ndarray_getbuf(self):
        requests = (
            # distinct flags
            PyBUF_INDIRECT, PyBUF_STRIDES, PyBUF_ND, PyBUF_SIMPLE,
            PyBUF_C_CONTIGUOUS, PyBUF_F_CONTIGUOUS, PyBUF_ANY_CONTIGUOUS,
            # compound requests
            PyBUF_FULL, PyBUF_FULL_RO,
            PyBUF_RECORDS, PyBUF_RECORDS_RO,
            PyBUF_STRIDED, PyBUF_STRIDED_RO,
            PyBUF_CONTIG, PyBUF_CONTIG_RO,
        )
        # items oraz format
        items_fmt = (
            ([Prawda jeżeli x % 2 inaczej Nieprawda dla x w range(12)], '?'),
            ([1,2,3,4,5,6,7,8,9,10,11,12], 'b'),
            ([1,2,3,4,5,6,7,8,9,10,11,12], 'B'),
            ([(2**31-x) jeżeli x % 2 inaczej (-2**31+x) dla x w range(12)], 'l')
        )
        # shape, strides, offset
        structure = (
            ([], [], 0),
            ([1,3,1], [], 0),
            ([12], [], 0),
            ([12], [-1], 11),
            ([6], [2], 0),
            ([6], [-2], 11),
            ([3, 4], [], 0),
            ([3, 4], [-4, -1], 11),
            ([2, 2], [4, 1], 4),
            ([2, 2], [-4, -1], 8)
        )
        # ndarray creation flags
        ndflags = (
            0, ND_WRITABLE, ND_FORTRAN, ND_FORTRAN|ND_WRITABLE,
            ND_PIL, ND_PIL|ND_WRITABLE
        )
        # flags that can actually be used jako flags
        real_flags = (0, PyBUF_WRITABLE, PyBUF_FORMAT,
                      PyBUF_WRITABLE|PyBUF_FORMAT)

        dla items, fmt w items_fmt:
            itemsize = struct.calcsize(fmt)
            dla shape, strides, offset w structure:
                strides = [v * itemsize dla v w strides]
                offset *= itemsize
                dla flags w ndflags:

                    jeżeli strides oraz (flags&ND_FORTRAN):
                        kontynuuj
                    jeżeli nie shape oraz (flags&ND_PIL):
                        kontynuuj

                    _items = items jeżeli shape inaczej items[0]
                    ex1 = ndarray(_items, format=fmt, flags=flags,
                                  shape=shape, strides=strides, offset=offset)
                    ex2 = ex1[::-2] jeżeli shape inaczej Nic

                    m1 = memoryview(ex1)
                    jeżeli ex2:
                        m2 = memoryview(ex2)
                    jeżeli ex1.ndim == 0 albo (ex1.ndim == 1 oraz shape oraz strides):
                        self.assertEqual(m1, ex1)
                    jeżeli ex2 oraz ex2.ndim == 1 oraz shape oraz strides:
                        self.assertEqual(m2, ex2)

                    dla req w requests:
                        dla bits w real_flags:
                            self.verify_getbuf(ex1, ex1, req|bits)
                            self.verify_getbuf(ex1, m1, req|bits)
                            jeżeli ex2:
                                self.verify_getbuf(ex2, ex2, req|bits,
                                                   sliced=Prawda)
                                self.verify_getbuf(ex2, m2, req|bits,
                                                   sliced=Prawda)

        items = [1,2,3,4,5,6,7,8,9,10,11,12]

        # ND_GETBUF_FAIL
        ex = ndarray(items, shape=[12], flags=ND_GETBUF_FAIL)
        self.assertRaises(BufferError, ndarray, ex)

        # Request complex structure z a simple exporter. In this
        # particular case the test object jest nie PEP-3118 compliant.
        base = ndarray([9], [1])
        ex = ndarray(base, getbuf=PyBUF_SIMPLE)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_WRITABLE)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_ND)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_STRIDES)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_C_CONTIGUOUS)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_F_CONTIGUOUS)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_ANY_CONTIGUOUS)
        nd = ndarray(ex, getbuf=PyBUF_SIMPLE)

        # Issue #22445: New precise contiguity definition.
        dla shape w [1,12,1], [7,0,7]:
            dla order w 0, ND_FORTRAN:
                ex = ndarray(items, shape=shape, flags=order|ND_WRITABLE)
                self.assertPrawda(is_contiguous(ex, 'F'))
                self.assertPrawda(is_contiguous(ex, 'C'))

                dla flags w requests:
                    nd = ndarray(ex, getbuf=flags)
                    self.assertPrawda(is_contiguous(nd, 'F'))
                    self.assertPrawda(is_contiguous(nd, 'C'))

    def test_ndarray_exceptions(self):
        nd = ndarray([9], [1])
        ndm = ndarray([9], [1], flags=ND_VAREXPORT)

        # Initialization of a new ndarray albo mutation of an existing array.
        dla c w (ndarray, nd.push, ndm.push):
            # Invalid types.
            self.assertRaises(TypeError, c, {1,2,3})
            self.assertRaises(TypeError, c, [1,2,'3'])
            self.assertRaises(TypeError, c, [1,2,(3,4)])
            self.assertRaises(TypeError, c, [1,2,3], shape={3})
            self.assertRaises(TypeError, c, [1,2,3], shape=[3], strides={1})
            self.assertRaises(TypeError, c, [1,2,3], shape=[3], offset=[])
            self.assertRaises(TypeError, c, [1], shape=[1], format={})
            self.assertRaises(TypeError, c, [1], shape=[1], flags={})
            self.assertRaises(TypeError, c, [1], shape=[1], getbuf={})

            # ND_FORTRAN flag jest only valid without strides.
            self.assertRaises(TypeError, c, [1], shape=[1], strides=[1],
                              flags=ND_FORTRAN)

            # ND_PIL flag jest only valid przy ndim > 0.
            self.assertRaises(TypeError, c, [1], shape=[], flags=ND_PIL)

            # Invalid items.
            self.assertRaises(ValueError, c, [], shape=[1])
            self.assertRaises(ValueError, c, ['XXX'], shape=[1], format="L")
            # Invalid combination of items oraz format.
            self.assertRaises(struct.error, c, [1000], shape=[1], format="B")
            self.assertRaises(ValueError, c, [1,(2,3)], shape=[2], format="B")
            self.assertRaises(ValueError, c, [1,2,3], shape=[3], format="QL")

            # Invalid ndim.
            n = ND_MAX_NDIM+1
            self.assertRaises(ValueError, c, [1]*n, shape=[1]*n)

            # Invalid shape.
            self.assertRaises(ValueError, c, [1], shape=[-1])
            self.assertRaises(ValueError, c, [1,2,3], shape=['3'])
            self.assertRaises(OverflowError, c, [1], shape=[2**128])
            # prod(shape) * itemsize != len(items)
            self.assertRaises(ValueError, c, [1,2,3,4,5], shape=[2,2], offset=3)

            # Invalid strides.
            self.assertRaises(ValueError, c, [1,2,3], shape=[3], strides=['1'])
            self.assertRaises(OverflowError, c, [1], shape=[1],
                              strides=[2**128])

            # Invalid combination of strides oraz shape.
            self.assertRaises(ValueError, c, [1,2], shape=[2,1], strides=[1])
            # Invalid combination of strides oraz format.
            self.assertRaises(ValueError, c, [1,2,3,4], shape=[2], strides=[3],
                              format="L")

            # Invalid offset.
            self.assertRaises(ValueError, c, [1,2,3], shape=[3], offset=4)
            self.assertRaises(ValueError, c, [1,2,3], shape=[1], offset=3,
                              format="L")

            # Invalid format.
            self.assertRaises(ValueError, c, [1,2,3], shape=[3], format="")
            self.assertRaises(struct.error, c, [(1,2,3)], shape=[1],
                              format="@#$")

            # Striding out of the memory bounds.
            items = [1,2,3,4,5,6,7,8,9,10]
            self.assertRaises(ValueError, c, items, shape=[2,3],
                              strides=[-3, -2], offset=5)

            # Constructing consumer: format argument invalid.
            self.assertRaises(TypeError, c, bytearray(), format="Q")

            # Constructing original base object: getbuf argument invalid.
            self.assertRaises(TypeError, c, [1], shape=[1], getbuf=PyBUF_FULL)

            # Shape argument jest mandatory dla original base objects.
            self.assertRaises(TypeError, c, [1])


        # PyBUF_WRITABLE request to read-only provider.
        self.assertRaises(BufferError, ndarray, b'123', getbuf=PyBUF_WRITABLE)

        # ND_VAREXPORT can only be specified during construction.
        nd = ndarray([9], [1], flags=ND_VAREXPORT)
        self.assertRaises(ValueError, nd.push, [1], [1], flags=ND_VAREXPORT)

        # Invalid operation dla consumers: push/pop
        nd = ndarray(b'123')
        self.assertRaises(BufferError, nd.push, [1], [1])
        self.assertRaises(BufferError, nd.pop)

        # ND_VAREXPORT nie set: push/pop fail przy exported buffers
        nd = ndarray([9], [1])
        nd.push([1], [1])
        m = memoryview(nd)
        self.assertRaises(BufferError, nd.push, [1], [1])
        self.assertRaises(BufferError, nd.pop)
        m.release()
        nd.pop()

        # Single remaining buffer: pop fails
        self.assertRaises(BufferError, nd.pop)
        usuń nd

        # get_pointer()
        self.assertRaises(TypeError, get_pointer, {}, [1,2,3])
        self.assertRaises(TypeError, get_pointer, b'123', {})

        nd = ndarray(list(range(100)), shape=[1]*100)
        self.assertRaises(ValueError, get_pointer, nd, [5])

        nd = ndarray(list(range(12)), shape=[3,4])
        self.assertRaises(ValueError, get_pointer, nd, [2,3,4])
        self.assertRaises(ValueError, get_pointer, nd, [3,3])
        self.assertRaises(ValueError, get_pointer, nd, [-3,3])
        self.assertRaises(OverflowError, get_pointer, nd, [1<<64,3])

        # tolist() needs format
        ex = ndarray([1,2,3], shape=[3], format='L')
        nd = ndarray(ex, getbuf=PyBUF_SIMPLE)
        self.assertRaises(ValueError, nd.tolist)

        # memoryview_from_buffer()
        ex1 = ndarray([1,2,3], shape=[3], format='L')
        ex2 = ndarray(ex1)
        nd = ndarray(ex2)
        self.assertRaises(TypeError, nd.memoryview_from_buffer)

        nd = ndarray([(1,)*200], shape=[1], format='L'*200)
        self.assertRaises(TypeError, nd.memoryview_from_buffer)

        n = ND_MAX_NDIM
        nd = ndarray(list(range(n)), shape=[1]*n)
        self.assertRaises(ValueError, nd.memoryview_from_buffer)

        # get_contiguous()
        nd = ndarray([1], shape=[1])
        self.assertRaises(TypeError, get_contiguous, 1, 2, 3, 4, 5)
        self.assertRaises(TypeError, get_contiguous, nd, "xyz", 'C')
        self.assertRaises(OverflowError, get_contiguous, nd, 2**64, 'C')
        self.assertRaises(TypeError, get_contiguous, nd, PyBUF_READ, 961)
        self.assertRaises(UnicodeEncodeError, get_contiguous, nd, PyBUF_READ,
                          '\u2007')
        self.assertRaises(ValueError, get_contiguous, nd, PyBUF_READ, 'Z')
        self.assertRaises(ValueError, get_contiguous, nd, 255, 'A')

        # cmp_contig()
        nd = ndarray([1], shape=[1])
        self.assertRaises(TypeError, cmp_contig, 1, 2, 3, 4, 5)
        self.assertRaises(TypeError, cmp_contig, {}, nd)
        self.assertRaises(TypeError, cmp_contig, nd, {})

        # is_contiguous()
        nd = ndarray([1], shape=[1])
        self.assertRaises(TypeError, is_contiguous, 1, 2, 3, 4, 5)
        self.assertRaises(TypeError, is_contiguous, {}, 'A')
        self.assertRaises(TypeError, is_contiguous, nd, 201)

    def test_ndarray_linked_list(self):
        dla perm w permutations(range(5)):
            m = [0]*5
            nd = ndarray([1,2,3], shape=[3], flags=ND_VAREXPORT)
            m[0] = memoryview(nd)

            dla i w range(1, 5):
                nd.push([1,2,3], shape=[3])
                m[i] = memoryview(nd)

            dla i w range(5):
                m[perm[i]].release()

            self.assertRaises(BufferError, nd.pop)
            usuń nd

    def test_ndarray_format_scalar(self):
        # ndim = 0: scalar
        dla fmt, scalar, _ w iter_format(0):
            itemsize = struct.calcsize(fmt)
            nd = ndarray(scalar, shape=(), format=fmt)
            self.verify(nd, obj=Nic,
                        itemsize=itemsize, fmt=fmt, readonly=1,
                        ndim=0, shape=(), strides=(),
                        lst=scalar)

    def test_ndarray_format_shape(self):
        # ndim = 1, shape = [n]
        nitems =  randrange(1, 10)
        dla fmt, items, _ w iter_format(nitems):
            itemsize = struct.calcsize(fmt)
            dla flags w (0, ND_PIL):
                nd = ndarray(items, shape=[nitems], format=fmt, flags=flags)
                self.verify(nd, obj=Nic,
                            itemsize=itemsize, fmt=fmt, readonly=1,
                            ndim=1, shape=(nitems,), strides=(itemsize,),
                            lst=items)

    def test_ndarray_format_strides(self):
        # ndim = 1, strides
        nitems = randrange(1, 30)
        dla fmt, items, _ w iter_format(nitems):
            itemsize = struct.calcsize(fmt)
            dla step w range(-5, 5):
                jeżeli step == 0:
                    kontynuuj

                shape = [len(items[::step])]
                strides = [step*itemsize]
                offset = itemsize*(nitems-1) jeżeli step < 0 inaczej 0

                dla flags w (0, ND_PIL):
                    nd = ndarray(items, shape=shape, strides=strides,
                                 format=fmt, offset=offset, flags=flags)
                    self.verify(nd, obj=Nic,
                                itemsize=itemsize, fmt=fmt, readonly=1,
                                ndim=1, shape=shape, strides=strides,
                                lst=items[::step])

    def test_ndarray_fortran(self):
        items = [1,2,3,4,5,6,7,8,9,10,11,12]
        ex = ndarray(items, shape=(3, 4), strides=(1, 3))
        nd = ndarray(ex, getbuf=PyBUF_F_CONTIGUOUS|PyBUF_FORMAT)
        self.assertEqual(nd.tolist(), farray(items, (3, 4)))

    def test_ndarray_multidim(self):
        dla ndim w range(5):
            shape_t = [randrange(2, 10) dla _ w range(ndim)]
            nitems = prod(shape_t)
            dla shape w permutations(shape_t):

                fmt, items, _ = randitems(nitems)
                itemsize = struct.calcsize(fmt)

                dla flags w (0, ND_PIL):
                    jeżeli ndim == 0 oraz flags == ND_PIL:
                        kontynuuj

                    # C array
                    nd = ndarray(items, shape=shape, format=fmt, flags=flags)

                    strides = strides_from_shape(ndim, shape, itemsize, 'C')
                    lst = carray(items, shape)
                    self.verify(nd, obj=Nic,
                                itemsize=itemsize, fmt=fmt, readonly=1,
                                ndim=ndim, shape=shape, strides=strides,
                                lst=lst)

                    jeżeli is_memoryview_format(fmt):
                        # memoryview: reconstruct strides
                        ex = ndarray(items, shape=shape, format=fmt)
                        nd = ndarray(ex, getbuf=PyBUF_CONTIG_RO|PyBUF_FORMAT)
                        self.assertPrawda(nd.strides == ())
                        mv = nd.memoryview_from_buffer()
                        self.verify(mv, obj=Nic,
                                    itemsize=itemsize, fmt=fmt, readonly=1,
                                    ndim=ndim, shape=shape, strides=strides,
                                    lst=lst)

                    # Fortran array
                    nd = ndarray(items, shape=shape, format=fmt,
                                 flags=flags|ND_FORTRAN)

                    strides = strides_from_shape(ndim, shape, itemsize, 'F')
                    lst = farray(items, shape)
                    self.verify(nd, obj=Nic,
                                itemsize=itemsize, fmt=fmt, readonly=1,
                                ndim=ndim, shape=shape, strides=strides,
                                lst=lst)

    def test_ndarray_index_invalid(self):
        # nie writable
        nd = ndarray([1], shape=[1])
        self.assertRaises(TypeError, nd.__setitem__, 1, 8)
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(TypeError, mv.__setitem__, 1, 8)

        # cannot be deleted
        nd = ndarray([1], shape=[1], flags=ND_WRITABLE)
        self.assertRaises(TypeError, nd.__delitem__, 1)
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(TypeError, mv.__delitem__, 1)

        # overflow
        nd = ndarray([1], shape=[1], flags=ND_WRITABLE)
        self.assertRaises(OverflowError, nd.__getitem__, 1<<64)
        self.assertRaises(OverflowError, nd.__setitem__, 1<<64, 8)
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(IndexError, mv.__getitem__, 1<<64)
        self.assertRaises(IndexError, mv.__setitem__, 1<<64, 8)

        # format
        items = [1,2,3,4,5,6,7,8]
        nd = ndarray(items, shape=[len(items)], format="B", flags=ND_WRITABLE)
        self.assertRaises(struct.error, nd.__setitem__, 2, 300)
        self.assertRaises(ValueError, nd.__setitem__, 1, (100, 200))
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(ValueError, mv.__setitem__, 2, 300)
        self.assertRaises(TypeError, mv.__setitem__, 1, (100, 200))

        items = [(1,2), (3,4), (5,6)]
        nd = ndarray(items, shape=[len(items)], format="LQ", flags=ND_WRITABLE)
        self.assertRaises(ValueError, nd.__setitem__, 2, 300)
        self.assertRaises(struct.error, nd.__setitem__, 1, (b'\x001', 200))

    def test_ndarray_index_scalar(self):
        # scalar
        nd = ndarray(1, shape=(), flags=ND_WRITABLE)
        mv = memoryview(nd)
        self.assertEqual(mv, nd)

        x = nd[()];  self.assertEqual(x, 1)
        x = nd[...]; self.assertEqual(x.tolist(), nd.tolist())

        x = mv[()];  self.assertEqual(x, 1)
        x = mv[...]; self.assertEqual(x.tolist(), nd.tolist())

        self.assertRaises(TypeError, nd.__getitem__, 0)
        self.assertRaises(TypeError, mv.__getitem__, 0)
        self.assertRaises(TypeError, nd.__setitem__, 0, 8)
        self.assertRaises(TypeError, mv.__setitem__, 0, 8)

        self.assertEqual(nd.tolist(), 1)
        self.assertEqual(mv.tolist(), 1)

        nd[()] = 9; self.assertEqual(nd.tolist(), 9)
        mv[()] = 9; self.assertEqual(mv.tolist(), 9)

        nd[...] = 5; self.assertEqual(nd.tolist(), 5)
        mv[...] = 5; self.assertEqual(mv.tolist(), 5)

    def test_ndarray_index_null_strides(self):
        ex = ndarray(list(range(2*4)), shape=[2, 4], flags=ND_WRITABLE)
        nd = ndarray(ex, getbuf=PyBUF_CONTIG)

        # Sub-views are only possible dla full exporters.
        self.assertRaises(BufferError, nd.__getitem__, 1)
        # Same dla slices.
        self.assertRaises(BufferError, nd.__getitem__, slice(3,5,1))

    def test_ndarray_index_getitem_single(self):
        # getitem
        dla fmt, items, _ w iter_format(5):
            nd = ndarray(items, shape=[5], format=fmt)
            dla i w range(-5, 5):
                self.assertEqual(nd[i], items[i])

            self.assertRaises(IndexError, nd.__getitem__, -6)
            self.assertRaises(IndexError, nd.__getitem__, 5)

            jeżeli is_memoryview_format(fmt):
                mv = memoryview(nd)
                self.assertEqual(mv, nd)
                dla i w range(-5, 5):
                    self.assertEqual(mv[i], items[i])

                self.assertRaises(IndexError, mv.__getitem__, -6)
                self.assertRaises(IndexError, mv.__getitem__, 5)

        # getitem przy null strides
        dla fmt, items, _ w iter_format(5):
            ex = ndarray(items, shape=[5], flags=ND_WRITABLE, format=fmt)
            nd = ndarray(ex, getbuf=PyBUF_CONTIG|PyBUF_FORMAT)

            dla i w range(-5, 5):
                self.assertEqual(nd[i], items[i])

            jeżeli is_memoryview_format(fmt):
                mv = nd.memoryview_from_buffer()
                self.assertIs(mv.__eq__(nd), NotImplemented)
                dla i w range(-5, 5):
                    self.assertEqual(mv[i], items[i])

        # getitem przy null format
        items = [1,2,3,4,5]
        ex = ndarray(items, shape=[5])
        nd = ndarray(ex, getbuf=PyBUF_CONTIG_RO)
        dla i w range(-5, 5):
            self.assertEqual(nd[i], items[i])

        # getitem przy null shape/strides/format
        items = [1,2,3,4,5]
        ex = ndarray(items, shape=[5])
        nd = ndarray(ex, getbuf=PyBUF_SIMPLE)

        dla i w range(-5, 5):
            self.assertEqual(nd[i], items[i])

    def test_ndarray_index_setitem_single(self):
        # assign single value
        dla fmt, items, single_item w iter_format(5):
            nd = ndarray(items, shape=[5], format=fmt, flags=ND_WRITABLE)
            dla i w range(5):
                items[i] = single_item
                nd[i] = single_item
            self.assertEqual(nd.tolist(), items)

            self.assertRaises(IndexError, nd.__setitem__, -6, single_item)
            self.assertRaises(IndexError, nd.__setitem__, 5, single_item)

            jeżeli nie is_memoryview_format(fmt):
                kontynuuj

            nd = ndarray(items, shape=[5], format=fmt, flags=ND_WRITABLE)
            mv = memoryview(nd)
            self.assertEqual(mv, nd)
            dla i w range(5):
                items[i] = single_item
                mv[i] = single_item
            self.assertEqual(mv.tolist(), items)

            self.assertRaises(IndexError, mv.__setitem__, -6, single_item)
            self.assertRaises(IndexError, mv.__setitem__, 5, single_item)


        # assign single value: lobject = robject
        dla fmt, items, single_item w iter_format(5):
            nd = ndarray(items, shape=[5], format=fmt, flags=ND_WRITABLE)
            dla i w range(-5, 4):
                items[i] = items[i+1]
                nd[i] = nd[i+1]
            self.assertEqual(nd.tolist(), items)

            jeżeli nie is_memoryview_format(fmt):
                kontynuuj

            nd = ndarray(items, shape=[5], format=fmt, flags=ND_WRITABLE)
            mv = memoryview(nd)
            self.assertEqual(mv, nd)
            dla i w range(-5, 4):
                items[i] = items[i+1]
                mv[i] = mv[i+1]
            self.assertEqual(mv.tolist(), items)

    def test_ndarray_index_getitem_multidim(self):
        shape_t = (2, 3, 5)
        nitems = prod(shape_t)
        dla shape w permutations(shape_t):

            fmt, items, _ = randitems(nitems)

            dla flags w (0, ND_PIL):
                # C array
                nd = ndarray(items, shape=shape, format=fmt, flags=flags)
                lst = carray(items, shape)

                dla i w range(-shape[0], shape[0]):
                    self.assertEqual(lst[i], nd[i].tolist())
                    dla j w range(-shape[1], shape[1]):
                        self.assertEqual(lst[i][j], nd[i][j].tolist())
                        dla k w range(-shape[2], shape[2]):
                            self.assertEqual(lst[i][j][k], nd[i][j][k])

                # Fortran array
                nd = ndarray(items, shape=shape, format=fmt,
                             flags=flags|ND_FORTRAN)
                lst = farray(items, shape)

                dla i w range(-shape[0], shape[0]):
                    self.assertEqual(lst[i], nd[i].tolist())
                    dla j w range(-shape[1], shape[1]):
                        self.assertEqual(lst[i][j], nd[i][j].tolist())
                        dla k w range(shape[2], shape[2]):
                            self.assertEqual(lst[i][j][k], nd[i][j][k])

    def test_ndarray_sequence(self):
        nd = ndarray(1, shape=())
        self.assertRaises(TypeError, eval, "1 w nd", locals())
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(TypeError, eval, "1 w mv", locals())

        dla fmt, items, _ w iter_format(5):
            nd = ndarray(items, shape=[5], format=fmt)
            dla i, v w enumerate(nd):
                self.assertEqual(v, items[i])
                self.assertPrawda(v w nd)

            jeżeli is_memoryview_format(fmt):
                mv = memoryview(nd)
                dla i, v w enumerate(mv):
                    self.assertEqual(v, items[i])
                    self.assertPrawda(v w mv)

    def test_ndarray_slice_invalid(self):
        items = [1,2,3,4,5,6,7,8]

        # rvalue jest nie an exporter
        xl = ndarray(items, shape=[8], flags=ND_WRITABLE)
        ml = memoryview(xl)
        self.assertRaises(TypeError, xl.__setitem__, slice(0,8,1), items)
        self.assertRaises(TypeError, ml.__setitem__, slice(0,8,1), items)

        # rvalue jest nie a full exporter
        xl = ndarray(items, shape=[8], flags=ND_WRITABLE)
        ex = ndarray(items, shape=[8], flags=ND_WRITABLE)
        xr = ndarray(ex, getbuf=PyBUF_ND)
        self.assertRaises(BufferError, xl.__setitem__, slice(0,8,1), xr)

        # zero step
        nd = ndarray(items, shape=[8], format="L", flags=ND_WRITABLE)
        mv = memoryview(nd)
        self.assertRaises(ValueError, nd.__getitem__, slice(0,1,0))
        self.assertRaises(ValueError, mv.__getitem__, slice(0,1,0))

        nd = ndarray(items, shape=[2,4], format="L", flags=ND_WRITABLE)
        mv = memoryview(nd)

        self.assertRaises(ValueError, nd.__getitem__,
                          (slice(0,1,1), slice(0,1,0)))
        self.assertRaises(ValueError, nd.__getitem__,
                          (slice(0,1,0), slice(0,1,1)))
        self.assertRaises(TypeError, nd.__getitem__, "@%$")
        self.assertRaises(TypeError, nd.__getitem__, ("@%$", slice(0,1,1)))
        self.assertRaises(TypeError, nd.__getitem__, (slice(0,1,1), {}))

        # memoryview: nie implemented
        self.assertRaises(NotImplementedError, mv.__getitem__,
                          (slice(0,1,1), slice(0,1,0)))
        self.assertRaises(TypeError, mv.__getitem__, "@%$")

        # differing format
        xl = ndarray(items, shape=[8], format="B", flags=ND_WRITABLE)
        xr = ndarray(items, shape=[8], format="b")
        ml = memoryview(xl)
        mr = memoryview(xr)
        self.assertRaises(ValueError, xl.__setitem__, slice(0,1,1), xr[7:8])
        self.assertEqual(xl.tolist(), items)
        self.assertRaises(ValueError, ml.__setitem__, slice(0,1,1), mr[7:8])
        self.assertEqual(ml.tolist(), items)

        # differing itemsize
        xl = ndarray(items, shape=[8], format="B", flags=ND_WRITABLE)
        yr = ndarray(items, shape=[8], format="L")
        ml = memoryview(xl)
        mr = memoryview(xr)
        self.assertRaises(ValueError, xl.__setitem__, slice(0,1,1), xr[7:8])
        self.assertEqual(xl.tolist(), items)
        self.assertRaises(ValueError, ml.__setitem__, slice(0,1,1), mr[7:8])
        self.assertEqual(ml.tolist(), items)

        # differing ndim
        xl = ndarray(items, shape=[2, 4], format="b", flags=ND_WRITABLE)
        xr = ndarray(items, shape=[8], format="b")
        ml = memoryview(xl)
        mr = memoryview(xr)
        self.assertRaises(ValueError, xl.__setitem__, slice(0,1,1), xr[7:8])
        self.assertEqual(xl.tolist(), [[1,2,3,4], [5,6,7,8]])
        self.assertRaises(NotImplementedError, ml.__setitem__, slice(0,1,1),
                          mr[7:8])

        # differing shape
        xl = ndarray(items, shape=[8], format="b", flags=ND_WRITABLE)
        xr = ndarray(items, shape=[8], format="b")
        ml = memoryview(xl)
        mr = memoryview(xr)
        self.assertRaises(ValueError, xl.__setitem__, slice(0,2,1), xr[7:8])
        self.assertEqual(xl.tolist(), items)
        self.assertRaises(ValueError, ml.__setitem__, slice(0,2,1), mr[7:8])
        self.assertEqual(ml.tolist(), items)

        # _testbuffer.c module functions
        self.assertRaises(TypeError, slice_indices, slice(0,1,2), {})
        self.assertRaises(TypeError, slice_indices, "###########", 1)
        self.assertRaises(ValueError, slice_indices, slice(0,1,0), 4)

        x = ndarray(items, shape=[8], format="b", flags=ND_PIL)
        self.assertRaises(TypeError, x.add_suboffsets)

        ex = ndarray(items, shape=[8], format="B")
        x = ndarray(ex, getbuf=PyBUF_SIMPLE)
        self.assertRaises(TypeError, x.add_suboffsets)

    def test_ndarray_slice_zero_shape(self):
        items = [1,2,3,4,5,6,7,8,9,10,11,12]

        x = ndarray(items, shape=[12], format="L", flags=ND_WRITABLE)
        y = ndarray(items, shape=[12], format="L")
        x[4:4] = y[9:9]
        self.assertEqual(x.tolist(), items)

        ml = memoryview(x)
        mr = memoryview(y)
        self.assertEqual(ml, x)
        self.assertEqual(ml, y)
        ml[4:4] = mr[9:9]
        self.assertEqual(ml.tolist(), items)

        x = ndarray(items, shape=[3, 4], format="L", flags=ND_WRITABLE)
        y = ndarray(items, shape=[4, 3], format="L")
        x[1:2, 2:2] = y[1:2, 3:3]
        self.assertEqual(x.tolist(), carray(items, [3, 4]))

    def test_ndarray_slice_multidim(self):
        shape_t = (2, 3, 5)
        ndim = len(shape_t)
        nitems = prod(shape_t)
        dla shape w permutations(shape_t):

            fmt, items, _ = randitems(nitems)
            itemsize = struct.calcsize(fmt)

            dla flags w (0, ND_PIL):
                nd = ndarray(items, shape=shape, format=fmt, flags=flags)
                lst = carray(items, shape)

                dla slices w rslices_ndim(ndim, shape):

                    listerr = Nic
                    spróbuj:
                        sliced = multislice(lst, slices)
                    wyjąwszy Exception jako e:
                        listerr = e.__class__

                    nderr = Nic
                    spróbuj:
                        ndsliced = nd[slices]
                    wyjąwszy Exception jako e:
                        nderr = e.__class__

                    jeżeli nderr albo listerr:
                        self.assertIs(nderr, listerr)
                    inaczej:
                        self.assertEqual(ndsliced.tolist(), sliced)

    def test_ndarray_slice_redundant_suboffsets(self):
        shape_t = (2, 3, 5, 2)
        ndim = len(shape_t)
        nitems = prod(shape_t)
        dla shape w permutations(shape_t):

            fmt, items, _ = randitems(nitems)
            itemsize = struct.calcsize(fmt)

            nd = ndarray(items, shape=shape, format=fmt)
            nd.add_suboffsets()
            ex = ndarray(items, shape=shape, format=fmt)
            ex.add_suboffsets()
            mv = memoryview(ex)
            lst = carray(items, shape)

            dla slices w rslices_ndim(ndim, shape):

                listerr = Nic
                spróbuj:
                    sliced = multislice(lst, slices)
                wyjąwszy Exception jako e:
                    listerr = e.__class__

                nderr = Nic
                spróbuj:
                    ndsliced = nd[slices]
                wyjąwszy Exception jako e:
                    nderr = e.__class__

                jeżeli nderr albo listerr:
                    self.assertIs(nderr, listerr)
                inaczej:
                    self.assertEqual(ndsliced.tolist(), sliced)

    def test_ndarray_slice_assign_single(self):
        dla fmt, items, _ w iter_format(5):
            dla lslice w genslices(5):
                dla rslice w genslices(5):
                    dla flags w (0, ND_PIL):

                        f = flags|ND_WRITABLE
                        nd = ndarray(items, shape=[5], format=fmt, flags=f)
                        ex = ndarray(items, shape=[5], format=fmt, flags=f)
                        mv = memoryview(ex)

                        lsterr = Nic
                        diff_structure = Nic
                        lst = items[:]
                        spróbuj:
                            lval = lst[lslice]
                            rval = lst[rslice]
                            lst[lslice] = lst[rslice]
                            diff_structure = len(lval) != len(rval)
                        wyjąwszy Exception jako e:
                            lsterr = e.__class__

                        nderr = Nic
                        spróbuj:
                            nd[lslice] = nd[rslice]
                        wyjąwszy Exception jako e:
                            nderr = e.__class__

                        jeżeli diff_structure: # ndarray cannot change shape
                            self.assertIs(nderr, ValueError)
                        inaczej:
                            self.assertEqual(nd.tolist(), lst)
                            self.assertIs(nderr, lsterr)

                        jeżeli nie is_memoryview_format(fmt):
                            kontynuuj

                        mverr = Nic
                        spróbuj:
                            mv[lslice] = mv[rslice]
                        wyjąwszy Exception jako e:
                            mverr = e.__class__

                        jeżeli diff_structure: # memoryview cannot change shape
                            self.assertIs(mverr, ValueError)
                        inaczej:
                            self.assertEqual(mv.tolist(), lst)
                            self.assertEqual(mv, nd)
                            self.assertIs(mverr, lsterr)
                            self.verify(mv, obj=ex,
                              itemsize=nd.itemsize, fmt=fmt, readonly=0,
                              ndim=nd.ndim, shape=nd.shape, strides=nd.strides,
                              lst=nd.tolist())

    def test_ndarray_slice_assign_multidim(self):
        shape_t = (2, 3, 5)
        ndim = len(shape_t)
        nitems = prod(shape_t)
        dla shape w permutations(shape_t):

            fmt, items, _ = randitems(nitems)

            dla flags w (0, ND_PIL):
                dla _ w range(ITERATIONS):
                    lslices, rslices = randslice_from_shape(ndim, shape)

                    nd = ndarray(items, shape=shape, format=fmt,
                                 flags=flags|ND_WRITABLE)
                    lst = carray(items, shape)

                    listerr = Nic
                    spróbuj:
                        result = multislice_assign(lst, lst, lslices, rslices)
                    wyjąwszy Exception jako e:
                        listerr = e.__class__

                    nderr = Nic
                    spróbuj:
                        nd[lslices] = nd[rslices]
                    wyjąwszy Exception jako e:
                        nderr = e.__class__

                    jeżeli nderr albo listerr:
                        self.assertIs(nderr, listerr)
                    inaczej:
                        self.assertEqual(nd.tolist(), result)

    def test_ndarray_random(self):
        # construction of valid arrays
        dla _ w range(ITERATIONS):
            dla fmt w fmtdict['@']:
                itemsize = struct.calcsize(fmt)

                t = rand_structure(itemsize, Prawda, maxdim=MAXDIM,
                                   maxshape=MAXSHAPE)
                self.assertPrawda(verify_structure(*t))
                items = randitems_from_structure(fmt, t)

                x = ndarray_from_structure(items, fmt, t)
                xlist = x.tolist()

                mv = memoryview(x)
                jeżeli is_memoryview_format(fmt):
                    mvlist = mv.tolist()
                    self.assertEqual(mvlist, xlist)

                jeżeli t[2] > 0:
                    # ndim > 0: test against suboffsets representation.
                    y = ndarray_from_structure(items, fmt, t, flags=ND_PIL)
                    ylist = y.tolist()
                    self.assertEqual(xlist, ylist)

                    mv = memoryview(y)
                    jeżeli is_memoryview_format(fmt):
                        self.assertEqual(mv, y)
                        mvlist = mv.tolist()
                        self.assertEqual(mvlist, ylist)

                jeżeli numpy_array:
                    shape = t[3]
                    jeżeli 0 w shape:
                        continue # http://projects.scipy.org/numpy/ticket/1910
                    z = numpy_array_from_structure(items, fmt, t)
                    self.verify(x, obj=Nic,
                                itemsize=z.itemsize, fmt=fmt, readonly=0,
                                ndim=z.ndim, shape=z.shape, strides=z.strides,
                                lst=z.tolist())

    def test_ndarray_random_invalid(self):
        # exceptions during construction of invalid arrays
        dla _ w range(ITERATIONS):
            dla fmt w fmtdict['@']:
                itemsize = struct.calcsize(fmt)

                t = rand_structure(itemsize, Nieprawda, maxdim=MAXDIM,
                                   maxshape=MAXSHAPE)
                self.assertNieprawda(verify_structure(*t))
                items = randitems_from_structure(fmt, t)

                nderr = Nieprawda
                spróbuj:
                    x = ndarray_from_structure(items, fmt, t)
                wyjąwszy Exception jako e:
                    nderr = e.__class__
                self.assertPrawda(nderr)

                jeżeli numpy_array:
                    numpy_err = Nieprawda
                    spróbuj:
                        y = numpy_array_from_structure(items, fmt, t)
                    wyjąwszy Exception jako e:
                        numpy_err = e.__class__

                    jeżeli 0: # http://projects.scipy.org/numpy/ticket/1910
                        self.assertPrawda(numpy_err)

    def test_ndarray_random_slice_assign(self):
        # valid slice assignments
        dla _ w range(ITERATIONS):
            dla fmt w fmtdict['@']:
                itemsize = struct.calcsize(fmt)

                lshape, rshape, lslices, rslices = \
                    rand_aligned_slices(maxdim=MAXDIM, maxshape=MAXSHAPE)
                tl = rand_structure(itemsize, Prawda, shape=lshape)
                tr = rand_structure(itemsize, Prawda, shape=rshape)
                self.assertPrawda(verify_structure(*tl))
                self.assertPrawda(verify_structure(*tr))
                litems = randitems_from_structure(fmt, tl)
                ritems = randitems_from_structure(fmt, tr)

                xl = ndarray_from_structure(litems, fmt, tl)
                xr = ndarray_from_structure(ritems, fmt, tr)
                xl[lslices] = xr[rslices]
                xllist = xl.tolist()
                xrlist = xr.tolist()

                ml = memoryview(xl)
                mr = memoryview(xr)
                self.assertEqual(ml.tolist(), xllist)
                self.assertEqual(mr.tolist(), xrlist)

                jeżeli tl[2] > 0 oraz tr[2] > 0:
                    # ndim > 0: test against suboffsets representation.
                    yl = ndarray_from_structure(litems, fmt, tl, flags=ND_PIL)
                    yr = ndarray_from_structure(ritems, fmt, tr, flags=ND_PIL)
                    yl[lslices] = yr[rslices]
                    yllist = yl.tolist()
                    yrlist = yr.tolist()
                    self.assertEqual(xllist, yllist)
                    self.assertEqual(xrlist, yrlist)

                    ml = memoryview(yl)
                    mr = memoryview(yr)
                    self.assertEqual(ml.tolist(), yllist)
                    self.assertEqual(mr.tolist(), yrlist)

                jeżeli numpy_array:
                    jeżeli 0 w lshape albo 0 w rshape:
                        continue # http://projects.scipy.org/numpy/ticket/1910

                    zl = numpy_array_from_structure(litems, fmt, tl)
                    zr = numpy_array_from_structure(ritems, fmt, tr)
                    zl[lslices] = zr[rslices]

                    jeżeli nie is_overlapping(tl) oraz nie is_overlapping(tr):
                        # Slice assignment of overlapping structures
                        # jest undefined w NumPy.
                        self.verify(xl, obj=Nic,
                                    itemsize=zl.itemsize, fmt=fmt, readonly=0,
                                    ndim=zl.ndim, shape=zl.shape,
                                    strides=zl.strides, lst=zl.tolist())

                    self.verify(xr, obj=Nic,
                                itemsize=zr.itemsize, fmt=fmt, readonly=0,
                                ndim=zr.ndim, shape=zr.shape,
                                strides=zr.strides, lst=zr.tolist())

    def test_ndarray_re_export(self):
        items = [1,2,3,4,5,6,7,8,9,10,11,12]

        nd = ndarray(items, shape=[3,4], flags=ND_PIL)
        ex = ndarray(nd)

        self.assertPrawda(ex.flags & ND_PIL)
        self.assertIs(ex.obj, nd)
        self.assertEqual(ex.suboffsets, (0, -1))
        self.assertNieprawda(ex.c_contiguous)
        self.assertNieprawda(ex.f_contiguous)
        self.assertNieprawda(ex.contiguous)

    def test_ndarray_zero_shape(self):
        # zeros w shape
        dla flags w (0, ND_PIL):
            nd = ndarray([1,2,3], shape=[0], flags=flags)
            mv = memoryview(nd)
            self.assertEqual(mv, nd)
            self.assertEqual(nd.tolist(), [])
            self.assertEqual(mv.tolist(), [])

            nd = ndarray([1,2,3], shape=[0,3,3], flags=flags)
            self.assertEqual(nd.tolist(), [])

            nd = ndarray([1,2,3], shape=[3,0,3], flags=flags)
            self.assertEqual(nd.tolist(), [[], [], []])

            nd = ndarray([1,2,3], shape=[3,3,0], flags=flags)
            self.assertEqual(nd.tolist(),
                             [[[], [], []], [[], [], []], [[], [], []]])

    def test_ndarray_zero_strides(self):
        # zero strides
        dla flags w (0, ND_PIL):
            nd = ndarray([1], shape=[5], strides=[0], flags=flags)
            mv = memoryview(nd)
            self.assertEqual(mv, nd)
            self.assertEqual(nd.tolist(), [1, 1, 1, 1, 1])
            self.assertEqual(mv.tolist(), [1, 1, 1, 1, 1])

    def test_ndarray_offset(self):
        nd = ndarray(list(range(20)), shape=[3], offset=7)
        self.assertEqual(nd.offset, 7)
        self.assertEqual(nd.tolist(), [7,8,9])

    def test_ndarray_memoryview_from_buffer(self):
        dla flags w (0, ND_PIL):
            nd = ndarray(list(range(3)), shape=[3], flags=flags)
            m = nd.memoryview_from_buffer()
            self.assertEqual(m, nd)

    def test_ndarray_get_pointer(self):
        dla flags w (0, ND_PIL):
            nd = ndarray(list(range(3)), shape=[3], flags=flags)
            dla i w range(3):
                self.assertEqual(nd[i], get_pointer(nd, [i]))

    def test_ndarray_tolist_null_strides(self):
        ex = ndarray(list(range(20)), shape=[2,2,5])

        nd = ndarray(ex, getbuf=PyBUF_ND|PyBUF_FORMAT)
        self.assertEqual(nd.tolist(), ex.tolist())

        m = memoryview(ex)
        self.assertEqual(m.tolist(), ex.tolist())

    def test_ndarray_cmp_contig(self):

        self.assertNieprawda(cmp_contig(b"123", b"456"))

        x = ndarray(list(range(12)), shape=[3,4])
        y = ndarray(list(range(12)), shape=[4,3])
        self.assertNieprawda(cmp_contig(x, y))

        x = ndarray([1], shape=[1], format="B")
        self.assertPrawda(cmp_contig(x, b'\x01'))
        self.assertPrawda(cmp_contig(b'\x01', x))

    def test_ndarray_hash(self):

        a = array.array('L', [1,2,3])
        nd = ndarray(a)
        self.assertRaises(ValueError, hash, nd)

        # one-dimensional
        b = bytes(list(range(12)))

        nd = ndarray(list(range(12)), shape=[12])
        self.assertEqual(hash(nd), hash(b))

        # C-contiguous
        nd = ndarray(list(range(12)), shape=[3,4])
        self.assertEqual(hash(nd), hash(b))

        nd = ndarray(list(range(12)), shape=[3,2,2])
        self.assertEqual(hash(nd), hash(b))

        # Fortran contiguous
        b = bytes(transpose(list(range(12)), shape=[4,3]))
        nd = ndarray(list(range(12)), shape=[3,4], flags=ND_FORTRAN)
        self.assertEqual(hash(nd), hash(b))

        b = bytes(transpose(list(range(12)), shape=[2,3,2]))
        nd = ndarray(list(range(12)), shape=[2,3,2], flags=ND_FORTRAN)
        self.assertEqual(hash(nd), hash(b))

        # suboffsets
        b = bytes(list(range(12)))
        nd = ndarray(list(range(12)), shape=[2,2,3], flags=ND_PIL)
        self.assertEqual(hash(nd), hash(b))

        # non-byte formats
        nd = ndarray(list(range(12)), shape=[2,2,3], format='L')
        self.assertEqual(hash(nd), hash(nd.tobytes()))

    def test_py_buffer_to_contiguous(self):

        # The requests are used w _testbuffer.c:py_buffer_to_contiguous
        # to generate buffers without full information dla testing.
        requests = (
            # distinct flags
            PyBUF_INDIRECT, PyBUF_STRIDES, PyBUF_ND, PyBUF_SIMPLE,
            # compound requests
            PyBUF_FULL, PyBUF_FULL_RO,
            PyBUF_RECORDS, PyBUF_RECORDS_RO,
            PyBUF_STRIDED, PyBUF_STRIDED_RO,
            PyBUF_CONTIG, PyBUF_CONTIG_RO,
        )

        # no buffer interface
        self.assertRaises(TypeError, py_buffer_to_contiguous, {}, 'F',
                          PyBUF_FULL_RO)

        # scalar, read-only request
        nd = ndarray(9, shape=(), format="L", flags=ND_WRITABLE)
        dla order w ['C', 'F', 'A']:
            dla request w requests:
                b = py_buffer_to_contiguous(nd, order, request)
                self.assertEqual(b, nd.tobytes())

        # zeros w shape
        nd = ndarray([1], shape=[0], format="L", flags=ND_WRITABLE)
        dla order w ['C', 'F', 'A']:
            dla request w requests:
                b = py_buffer_to_contiguous(nd, order, request)
                self.assertEqual(b, b'')

        nd = ndarray(list(range(8)), shape=[2, 0, 7], format="L",
                     flags=ND_WRITABLE)
        dla order w ['C', 'F', 'A']:
            dla request w requests:
                b = py_buffer_to_contiguous(nd, order, request)
                self.assertEqual(b, b'')

        ### One-dimensional arrays are trivial, since Fortran oraz C order
        ### are the same.

        # one-dimensional
        dla f w [0, ND_FORTRAN]:
            nd = ndarray([1], shape=[1], format="h", flags=f|ND_WRITABLE)
            ndbytes = nd.tobytes()
            dla order w ['C', 'F', 'A']:
                dla request w requests:
                    b = py_buffer_to_contiguous(nd, order, request)
                    self.assertEqual(b, ndbytes)

            nd = ndarray([1, 2, 3], shape=[3], format="b", flags=f|ND_WRITABLE)
            ndbytes = nd.tobytes()
            dla order w ['C', 'F', 'A']:
                dla request w requests:
                    b = py_buffer_to_contiguous(nd, order, request)
                    self.assertEqual(b, ndbytes)

        # one-dimensional, non-contiguous input
        nd = ndarray([1, 2, 3], shape=[2], strides=[2], flags=ND_WRITABLE)
        ndbytes = nd.tobytes()
        dla order w ['C', 'F', 'A']:
            dla request w [PyBUF_STRIDES, PyBUF_FULL]:
                b = py_buffer_to_contiguous(nd, order, request)
                self.assertEqual(b, ndbytes)

        nd = nd[::-1]
        ndbytes = nd.tobytes()
        dla order w ['C', 'F', 'A']:
            dla request w requests:
                spróbuj:
                    b = py_buffer_to_contiguous(nd, order, request)
                wyjąwszy BufferError:
                    kontynuuj
                self.assertEqual(b, ndbytes)

        ###
        ### Multi-dimensional arrays:
        ###
        ### The goal here jest to preserve the logical representation of the
        ### input array but change the physical representation jeżeli necessary.
        ###
        ### _testbuffer example:
        ### ====================
        ###
        ###    C input array:
        ###    --------------
        ###       >>> nd = ndarray(list(range(12)), shape=[3, 4])
        ###       >>> nd.tolist()
        ###       [[0, 1, 2, 3],
        ###        [4, 5, 6, 7],
        ###        [8, 9, 10, 11]]
        ###
        ###    Fortran output:
        ###    ---------------
        ###       >>> py_buffer_to_contiguous(nd, 'F', PyBUF_FULL_RO)
        ###       >>> b'\x00\x04\x08\x01\x05\t\x02\x06\n\x03\x07\x0b'
        ###
        ###    The zwróć value corresponds to this input list for
        ###    _testbuffer's ndarray:
        ###       >>> nd = ndarray([0,4,8,1,5,9,2,6,10,3,7,11], shape=[3,4],
        ###                        flags=ND_FORTRAN)
        ###       >>> nd.tolist()
        ###       [[0, 1, 2, 3],
        ###        [4, 5, 6, 7],
        ###        [8, 9, 10, 11]]
        ###
        ###    The logical array jest the same, but the values w memory are now
        ###    w Fortran order.
        ###
        ### NumPy example:
        ### ==============
        ###    _testbuffer's ndarray takes lists to initialize the memory.
        ###    Here's the same sequence w NumPy:
        ###
        ###    C input:
        ###    --------
        ###       >>> nd = ndarray(buffer=bytearray(list(range(12))),
        ###                        shape=[3, 4], dtype='B')
        ###       >>> nd
        ###       array([[ 0,  1,  2,  3],
        ###              [ 4,  5,  6,  7],
        ###              [ 8,  9, 10, 11]], dtype=uint8)
        ###
        ###    Fortran output:
        ###    ---------------
        ###       >>> fortran_buf = nd.tostring(order='F')
        ###       >>> fortran_buf
        ###       b'\x00\x04\x08\x01\x05\t\x02\x06\n\x03\x07\x0b'
        ###
        ###       >>> nd = ndarray(buffer=fortran_buf, shape=[3, 4],
        ###                        dtype='B', order='F')
        ###
        ###       >>> nd
        ###       array([[ 0,  1,  2,  3],
        ###              [ 4,  5,  6,  7],
        ###              [ 8,  9, 10, 11]], dtype=uint8)
        ###

        # multi-dimensional, contiguous input
        lst = list(range(12))
        dla f w [0, ND_FORTRAN]:
            nd = ndarray(lst, shape=[3, 4], flags=f|ND_WRITABLE)
            jeżeli numpy_array:
                na = numpy_array(buffer=bytearray(lst),
                                 shape=[3, 4], dtype='B',
                                 order='C' jeżeli f == 0 inaczej 'F')

            # 'C' request
            jeżeli f == ND_FORTRAN: # 'F' to 'C'
                x = ndarray(transpose(lst, [4, 3]), shape=[3, 4],
                            flags=ND_WRITABLE)
                expected = x.tobytes()
            inaczej:
                expected = nd.tobytes()
            dla request w requests:
                spróbuj:
                    b = py_buffer_to_contiguous(nd, 'C', request)
                wyjąwszy BufferError:
                    kontynuuj

                self.assertEqual(b, expected)

                # Check that output can be used jako the basis dla constructing
                # a C array that jest logically identical to the input array.
                y = ndarray([v dla v w b], shape=[3, 4], flags=ND_WRITABLE)
                self.assertEqual(memoryview(y), memoryview(nd))

                jeżeli numpy_array:
                    self.assertEqual(b, na.tostring(order='C'))

            # 'F' request
            jeżeli f == 0: # 'C' to 'F'
                x = ndarray(transpose(lst, [3, 4]), shape=[4, 3],
                            flags=ND_WRITABLE)
            inaczej:
                x = ndarray(lst, shape=[3, 4], flags=ND_WRITABLE)
            expected = x.tobytes()
            dla request w [PyBUF_FULL, PyBUF_FULL_RO, PyBUF_INDIRECT,
                            PyBUF_STRIDES, PyBUF_ND]:
                spróbuj:
                    b = py_buffer_to_contiguous(nd, 'F', request)
                wyjąwszy BufferError:
                    kontynuuj
                self.assertEqual(b, expected)

                # Check that output can be used jako the basis dla constructing
                # a Fortran array that jest logically identical to the input array.
                y = ndarray([v dla v w b], shape=[3, 4], flags=ND_FORTRAN|ND_WRITABLE)
                self.assertEqual(memoryview(y), memoryview(nd))

                jeżeli numpy_array:
                    self.assertEqual(b, na.tostring(order='F'))

            # 'A' request
            jeżeli f == ND_FORTRAN:
                x = ndarray(lst, shape=[3, 4], flags=ND_WRITABLE)
                expected = x.tobytes()
            inaczej:
                expected = nd.tobytes()
            dla request w [PyBUF_FULL, PyBUF_FULL_RO, PyBUF_INDIRECT,
                            PyBUF_STRIDES, PyBUF_ND]:
                spróbuj:
                    b = py_buffer_to_contiguous(nd, 'A', request)
                wyjąwszy BufferError:
                    kontynuuj

                self.assertEqual(b, expected)

                # Check that output can be used jako the basis dla constructing
                # an array przy order=f that jest logically identical to the input
                # array.
                y = ndarray([v dla v w b], shape=[3, 4], flags=f|ND_WRITABLE)
                self.assertEqual(memoryview(y), memoryview(nd))

                jeżeli numpy_array:
                    self.assertEqual(b, na.tostring(order='A'))

        # multi-dimensional, non-contiguous input
        nd = ndarray(list(range(12)), shape=[3, 4], flags=ND_WRITABLE|ND_PIL)

        # 'C'
        b = py_buffer_to_contiguous(nd, 'C', PyBUF_FULL_RO)
        self.assertEqual(b, nd.tobytes())
        y = ndarray([v dla v w b], shape=[3, 4], flags=ND_WRITABLE)
        self.assertEqual(memoryview(y), memoryview(nd))

        # 'F'
        b = py_buffer_to_contiguous(nd, 'F', PyBUF_FULL_RO)
        x = ndarray(transpose(lst, [3, 4]), shape=[4, 3], flags=ND_WRITABLE)
        self.assertEqual(b, x.tobytes())
        y = ndarray([v dla v w b], shape=[3, 4], flags=ND_FORTRAN|ND_WRITABLE)
        self.assertEqual(memoryview(y), memoryview(nd))

        # 'A'
        b = py_buffer_to_contiguous(nd, 'A', PyBUF_FULL_RO)
        self.assertEqual(b, nd.tobytes())
        y = ndarray([v dla v w b], shape=[3, 4], flags=ND_WRITABLE)
        self.assertEqual(memoryview(y), memoryview(nd))

    def test_memoryview_construction(self):

        items_shape = [(9, []), ([1,2,3], [3]), (list(range(2*3*5)), [2,3,5])]

        # NumPy style, C-contiguous:
        dla items, shape w items_shape:

            # From PEP-3118 compliant exporter:
            ex = ndarray(items, shape=shape)
            m = memoryview(ex)
            self.assertPrawda(m.c_contiguous)
            self.assertPrawda(m.contiguous)

            ndim = len(shape)
            strides = strides_from_shape(ndim, shape, 1, 'C')
            lst = carray(items, shape)

            self.verify(m, obj=ex,
                        itemsize=1, fmt='B', readonly=1,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

            # From memoryview:
            m2 = memoryview(m)
            self.verify(m2, obj=ex,
                        itemsize=1, fmt='B', readonly=1,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

            # PyMemoryView_FromBuffer(): no strides
            nd = ndarray(ex, getbuf=PyBUF_CONTIG_RO|PyBUF_FORMAT)
            self.assertEqual(nd.strides, ())
            m = nd.memoryview_from_buffer()
            self.verify(m, obj=Nic,
                        itemsize=1, fmt='B', readonly=1,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

            # PyMemoryView_FromBuffer(): no format, shape, strides
            nd = ndarray(ex, getbuf=PyBUF_SIMPLE)
            self.assertEqual(nd.format, '')
            self.assertEqual(nd.shape, ())
            self.assertEqual(nd.strides, ())
            m = nd.memoryview_from_buffer()

            lst = [items] jeżeli ndim == 0 inaczej items
            self.verify(m, obj=Nic,
                        itemsize=1, fmt='B', readonly=1,
                        ndim=1, shape=[ex.nbytes], strides=(1,),
                        lst=lst)

        # NumPy style, Fortran contiguous:
        dla items, shape w items_shape:

            # From PEP-3118 compliant exporter:
            ex = ndarray(items, shape=shape, flags=ND_FORTRAN)
            m = memoryview(ex)
            self.assertPrawda(m.f_contiguous)
            self.assertPrawda(m.contiguous)

            ndim = len(shape)
            strides = strides_from_shape(ndim, shape, 1, 'F')
            lst = farray(items, shape)

            self.verify(m, obj=ex,
                        itemsize=1, fmt='B', readonly=1,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

            # From memoryview:
            m2 = memoryview(m)
            self.verify(m2, obj=ex,
                        itemsize=1, fmt='B', readonly=1,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

        # PIL style:
        dla items, shape w items_shape[1:]:

            # From PEP-3118 compliant exporter:
            ex = ndarray(items, shape=shape, flags=ND_PIL)
            m = memoryview(ex)

            ndim = len(shape)
            lst = carray(items, shape)

            self.verify(m, obj=ex,
                        itemsize=1, fmt='B', readonly=1,
                        ndim=ndim, shape=shape, strides=ex.strides,
                        lst=lst)

            # From memoryview:
            m2 = memoryview(m)
            self.verify(m2, obj=ex,
                        itemsize=1, fmt='B', readonly=1,
                        ndim=ndim, shape=shape, strides=ex.strides,
                        lst=lst)

        # Invalid number of arguments:
        self.assertRaises(TypeError, memoryview, b'9', 'x')
        # Not a buffer provider:
        self.assertRaises(TypeError, memoryview, {})
        # Non-compliant buffer provider:
        ex = ndarray([1,2,3], shape=[3])
        nd = ndarray(ex, getbuf=PyBUF_SIMPLE)
        self.assertRaises(BufferError, memoryview, nd)
        nd = ndarray(ex, getbuf=PyBUF_CONTIG_RO|PyBUF_FORMAT)
        self.assertRaises(BufferError, memoryview, nd)

        # ndim > 64
        nd = ndarray([1]*128, shape=[1]*128, format='L')
        self.assertRaises(ValueError, memoryview, nd)
        self.assertRaises(ValueError, nd.memoryview_from_buffer)
        self.assertRaises(ValueError, get_contiguous, nd, PyBUF_READ, 'C')
        self.assertRaises(ValueError, get_contiguous, nd, PyBUF_READ, 'F')
        self.assertRaises(ValueError, get_contiguous, nd[::-1], PyBUF_READ, 'C')

    def test_memoryview_cast_zero_shape(self):
        # Casts are undefined jeżeli buffer jest multidimensional oraz shape
        # contains zeros. These arrays are regarded jako C-contiguous by
        # Numpy oraz PyBuffer_GetContiguous(), so they are nie caught by
        # the test dla C-contiguity w memory_cast().
        items = [1,2,3]
        dla shape w ([0,3,3], [3,0,3], [0,3,3]):
            ex = ndarray(items, shape=shape)
            self.assertPrawda(ex.c_contiguous)
            msrc = memoryview(ex)
            self.assertRaises(TypeError, msrc.cast, 'c')
        # Monodimensional empty view can be cast (issue #19014).
        dla fmt, _, _ w iter_format(1, 'memoryview'):
            msrc = memoryview(b'')
            m = msrc.cast(fmt)
            self.assertEqual(m.tobytes(), b'')
            self.assertEqual(m.tolist(), [])

    check_sizeof = support.check_sizeof

    def test_memoryview_sizeof(self):
        check = self.check_sizeof
        vsize = support.calcvobjsize
        base_struct = 'Pnin 2P2n2i5P P'
        per_dim = '3n'

        items = list(range(8))
        check(memoryview(b''), vsize(base_struct + 1 * per_dim))
        a = ndarray(items, shape=[2, 4], format="b")
        check(memoryview(a), vsize(base_struct + 2 * per_dim))
        a = ndarray(items, shape=[2, 2, 2], format="b")
        check(memoryview(a), vsize(base_struct + 3 * per_dim))

    def test_memoryview_struct_module(self):

        klasa INT(object):
            def __init__(self, val):
                self.val = val
            def __int__(self):
                zwróć self.val

        klasa IDX(object):
            def __init__(self, val):
                self.val = val
            def __index__(self):
                zwróć self.val

        def f(): zwróć 7

        values = [INT(9), IDX(9),
                  2.2+3j, Decimal("-21.1"), 12.2, Fraction(5, 2),
                  [1,2,3], {4,5,6}, {7:8}, (), (9,),
                  Prawda, Nieprawda, Nic, NotImplemented,
                  b'a', b'abc', bytearray(b'a'), bytearray(b'abc'),
                  'a', 'abc', r'a', r'abc',
                  f, lambda x: x]

        dla fmt, items, item w iter_format(10, 'memoryview'):
            ex = ndarray(items, shape=[10], format=fmt, flags=ND_WRITABLE)
            nd = ndarray(items, shape=[10], format=fmt, flags=ND_WRITABLE)
            m = memoryview(ex)

            struct.pack_into(fmt, nd, 0, item)
            m[0] = item
            self.assertEqual(m[0], nd[0])

            itemsize = struct.calcsize(fmt)
            jeżeli 'P' w fmt:
                kontynuuj

            dla v w values:
                struct_err = Nic
                spróbuj:
                    struct.pack_into(fmt, nd, itemsize, v)
                wyjąwszy struct.error:
                    struct_err = struct.error

                mv_err = Nic
                spróbuj:
                    m[1] = v
                wyjąwszy (TypeError, ValueError) jako e:
                    mv_err = e.__class__

                jeżeli struct_err albo mv_err:
                    self.assertIsNot(struct_err, Nic)
                    self.assertIsNot(mv_err, Nic)
                inaczej:
                    self.assertEqual(m[1], nd[1])

    def test_memoryview_cast_zero_strides(self):
        # Casts are undefined jeżeli strides contains zeros. These arrays are
        # (sometimes!) regarded jako C-contiguous by Numpy, but nie by
        # PyBuffer_GetContiguous().
        ex = ndarray([1,2,3], shape=[3], strides=[0])
        self.assertNieprawda(ex.c_contiguous)
        msrc = memoryview(ex)
        self.assertRaises(TypeError, msrc.cast, 'c')

    def test_memoryview_cast_invalid(self):
        # invalid format
        dla sfmt w NON_BYTE_FORMAT:
            sformat = '@' + sfmt jeżeli randrange(2) inaczej sfmt
            ssize = struct.calcsize(sformat)
            dla dfmt w NON_BYTE_FORMAT:
                dformat = '@' + dfmt jeżeli randrange(2) inaczej dfmt
                dsize = struct.calcsize(dformat)
                ex = ndarray(list(range(32)), shape=[32//ssize], format=sformat)
                msrc = memoryview(ex)
                self.assertRaises(TypeError, msrc.cast, dfmt, [32//dsize])

        dla sfmt, sitems, _ w iter_format(1):
            ex = ndarray(sitems, shape=[1], format=sfmt)
            msrc = memoryview(ex)
            dla dfmt, _, _ w iter_format(1):
                jeżeli nie is_memoryview_format(dfmt):
                    self.assertRaises(ValueError, msrc.cast, dfmt,
                                      [32//dsize])
                inaczej:
                    jeżeli nie is_byte_format(sfmt) oraz nie is_byte_format(dfmt):
                        self.assertRaises(TypeError, msrc.cast, dfmt,
                                          [32//dsize])

        # invalid shape
        size_h = struct.calcsize('h')
        size_d = struct.calcsize('d')
        ex = ndarray(list(range(2*2*size_d)), shape=[2,2,size_d], format='h')
        msrc = memoryview(ex)
        self.assertRaises(TypeError, msrc.cast, shape=[2,2,size_h], format='d')

        ex = ndarray(list(range(120)), shape=[1,2,3,4,5])
        m = memoryview(ex)

        # incorrect number of args
        self.assertRaises(TypeError, m.cast)
        self.assertRaises(TypeError, m.cast, 1, 2, 3)

        # incorrect dest format type
        self.assertRaises(TypeError, m.cast, {})

        # incorrect dest format
        self.assertRaises(ValueError, m.cast, "X")
        self.assertRaises(ValueError, m.cast, "@X")
        self.assertRaises(ValueError, m.cast, "@XY")

        # dest format nie implemented
        self.assertRaises(ValueError, m.cast, "=B")
        self.assertRaises(ValueError, m.cast, "!L")
        self.assertRaises(ValueError, m.cast, "<P")
        self.assertRaises(ValueError, m.cast, ">l")
        self.assertRaises(ValueError, m.cast, "BI")
        self.assertRaises(ValueError, m.cast, "xBI")

        # src format nie implemented
        ex = ndarray([(1,2), (3,4)], shape=[2], format="II")
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.__getitem__, 0)
        self.assertRaises(NotImplementedError, m.__setitem__, 0, 8)
        self.assertRaises(NotImplementedError, m.tolist)

        # incorrect shape type
        ex = ndarray(list(range(120)), shape=[1,2,3,4,5])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.cast, "B", shape={})

        # incorrect shape elements
        ex = ndarray(list(range(120)), shape=[2*3*4*5])
        m = memoryview(ex)
        self.assertRaises(OverflowError, m.cast, "B", shape=[2**64])
        self.assertRaises(ValueError, m.cast, "B", shape=[-1])
        self.assertRaises(ValueError, m.cast, "B", shape=[2,3,4,5,6,7,-1])
        self.assertRaises(ValueError, m.cast, "B", shape=[2,3,4,5,6,7,0])
        self.assertRaises(TypeError, m.cast, "B", shape=[2,3,4,5,6,7,'x'])

        # N-D -> N-D cast
        ex = ndarray(list([9 dla _ w range(3*5*7*11)]), shape=[3,5,7,11])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.cast, "I", shape=[2,3,4,5])

        # cast przy ndim > 64
        nd = ndarray(list(range(128)), shape=[128], format='I')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.cast, 'I', [1]*128)

        # view->len nie a multiple of itemsize
        ex = ndarray(list([9 dla _ w range(3*5*7*11)]), shape=[3*5*7*11])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.cast, "I", shape=[2,3,4,5])

        # product(shape) * itemsize != buffer size
        ex = ndarray(list([9 dla _ w range(3*5*7*11)]), shape=[3*5*7*11])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.cast, "B", shape=[2,3,4,5])

        # product(shape) * itemsize overflow
        nd = ndarray(list(range(128)), shape=[128], format='I')
        m1 = memoryview(nd)
        nd = ndarray(list(range(128)), shape=[128], format='B')
        m2 = memoryview(nd)
        jeżeli sys.maxsize == 2**63-1:
            self.assertRaises(TypeError, m1.cast, 'B',
                              [7, 7, 73, 127, 337, 92737, 649657])
            self.assertRaises(ValueError, m1.cast, 'B',
                              [2**20, 2**20, 2**10, 2**10, 2**3])
            self.assertRaises(ValueError, m2.cast, 'I',
                              [2**20, 2**20, 2**10, 2**10, 2**1])
        inaczej:
            self.assertRaises(TypeError, m1.cast, 'B',
                              [1, 2147483647])
            self.assertRaises(ValueError, m1.cast, 'B',
                              [2**10, 2**10, 2**5, 2**5, 2**1])
            self.assertRaises(ValueError, m2.cast, 'I',
                              [2**10, 2**10, 2**5, 2**3, 2**1])

    def test_memoryview_cast(self):
        bytespec = (
          ('B', lambda ex: list(ex.tobytes())),
          ('b', lambda ex: [x-256 jeżeli x > 127 inaczej x dla x w list(ex.tobytes())]),
          ('c', lambda ex: [bytes(chr(x), 'latin-1') dla x w list(ex.tobytes())]),
        )

        def iter_roundtrip(ex, m, items, fmt):
            srcsize = struct.calcsize(fmt)
            dla bytefmt, to_bytelist w bytespec:

                m2 = m.cast(bytefmt)
                lst = to_bytelist(ex)
                self.verify(m2, obj=ex,
                            itemsize=1, fmt=bytefmt, readonly=0,
                            ndim=1, shape=[31*srcsize], strides=(1,),
                            lst=lst, cast=Prawda)

                m3 = m2.cast(fmt)
                self.assertEqual(m3, ex)
                lst = ex.tolist()
                self.verify(m3, obj=ex,
                            itemsize=srcsize, fmt=fmt, readonly=0,
                            ndim=1, shape=[31], strides=(srcsize,),
                            lst=lst, cast=Prawda)

        # cast z ndim = 0 to ndim = 1
        srcsize = struct.calcsize('I')
        ex = ndarray(9, shape=[], format='I')
        destitems, destshape = cast_items(ex, 'B', 1)
        m = memoryview(ex)
        m2 = m.cast('B')
        self.verify(m2, obj=ex,
                    itemsize=1, fmt='B', readonly=1,
                    ndim=1, shape=destshape, strides=(1,),
                    lst=destitems, cast=Prawda)

        # cast z ndim = 1 to ndim = 0
        destsize = struct.calcsize('I')
        ex = ndarray([9]*destsize, shape=[destsize], format='B')
        destitems, destshape = cast_items(ex, 'I', destsize, shape=[])
        m = memoryview(ex)
        m2 = m.cast('I', shape=[])
        self.verify(m2, obj=ex,
                    itemsize=destsize, fmt='I', readonly=1,
                    ndim=0, shape=(), strides=(),
                    lst=destitems, cast=Prawda)

        # array.array: roundtrip to/z bytes
        dla fmt, items, _ w iter_format(31, 'array'):
            ex = array.array(fmt, items)
            m = memoryview(ex)
            iter_roundtrip(ex, m, items, fmt)

        # ndarray: roundtrip to/z bytes
        dla fmt, items, _ w iter_format(31, 'memoryview'):
            ex = ndarray(items, shape=[31], format=fmt, flags=ND_WRITABLE)
            m = memoryview(ex)
            iter_roundtrip(ex, m, items, fmt)

    def test_memoryview_cast_1D_ND(self):
        # Cast between C-contiguous buffers. At least one buffer must
        # be 1D, at least one format must be 'c', 'b' albo 'B'.
        dla _tshape w gencastshapes():
            dla char w fmtdict['@']:
                tfmt = ('', '@')[randrange(2)] + char
                tsize = struct.calcsize(tfmt)
                n = prod(_tshape) * tsize
                obj = 'memoryview' jeżeli is_byte_format(tfmt) inaczej 'bytefmt'
                dla fmt, items, _ w iter_format(n, obj):
                    size = struct.calcsize(fmt)
                    shape = [n] jeżeli n > 0 inaczej []
                    tshape = _tshape + [size]

                    ex = ndarray(items, shape=shape, format=fmt)
                    m = memoryview(ex)

                    titems, tshape = cast_items(ex, tfmt, tsize, shape=tshape)

                    jeżeli titems jest Nic:
                        self.assertRaises(TypeError, m.cast, tfmt, tshape)
                        kontynuuj
                    jeżeli titems == 'nan':
                        continue # NaNs w lists are a recipe dla trouble.

                    # 1D -> ND
                    nd = ndarray(titems, shape=tshape, format=tfmt)

                    m2 = m.cast(tfmt, shape=tshape)
                    ndim = len(tshape)
                    strides = nd.strides
                    lst = nd.tolist()
                    self.verify(m2, obj=ex,
                                itemsize=tsize, fmt=tfmt, readonly=1,
                                ndim=ndim, shape=tshape, strides=strides,
                                lst=lst, cast=Prawda)

                    # ND -> 1D
                    m3 = m2.cast(fmt)
                    m4 = m2.cast(fmt, shape=shape)
                    ndim = len(shape)
                    strides = ex.strides
                    lst = ex.tolist()

                    self.verify(m3, obj=ex,
                                itemsize=size, fmt=fmt, readonly=1,
                                ndim=ndim, shape=shape, strides=strides,
                                lst=lst, cast=Prawda)

                    self.verify(m4, obj=ex,
                                itemsize=size, fmt=fmt, readonly=1,
                                ndim=ndim, shape=shape, strides=strides,
                                lst=lst, cast=Prawda)

        jeżeli ctypes:
            # format: "T{>l:x:>d:y:}"
            klasa BEPoint(ctypes.BigEndianStructure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_double)]
            point = BEPoint(100, 200.1)
            m1 = memoryview(point)
            m2 = m1.cast('B')
            self.assertEqual(m2.obj, point)
            self.assertEqual(m2.itemsize, 1)
            self.assertEqual(m2.readonly, 0)
            self.assertEqual(m2.ndim, 1)
            self.assertEqual(m2.shape, (m2.nbytes,))
            self.assertEqual(m2.strides, (1,))
            self.assertEqual(m2.suboffsets, ())

            x = ctypes.c_double(1.2)
            m1 = memoryview(x)
            m2 = m1.cast('c')
            self.assertEqual(m2.obj, x)
            self.assertEqual(m2.itemsize, 1)
            self.assertEqual(m2.readonly, 0)
            self.assertEqual(m2.ndim, 1)
            self.assertEqual(m2.shape, (m2.nbytes,))
            self.assertEqual(m2.strides, (1,))
            self.assertEqual(m2.suboffsets, ())

    def test_memoryview_tolist(self):

        # Most tolist() tests are w self.verify() etc.

        a = array.array('h', list(range(-6, 6)))
        m = memoryview(a)
        self.assertEqual(m, a)
        self.assertEqual(m.tolist(), a.tolist())

        a = a[2::3]
        m = m[2::3]
        self.assertEqual(m, a)
        self.assertEqual(m.tolist(), a.tolist())

        ex = ndarray(list(range(2*3*5*7*11)), shape=[11,2,7,3,5], format='L')
        m = memoryview(ex)
        self.assertEqual(m.tolist(), ex.tolist())

        ex = ndarray([(2, 5), (7, 11)], shape=[2], format='lh')
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.tolist)

        ex = ndarray([b'12345'], shape=[1], format="s")
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.tolist)

        ex = ndarray([b"a",b"b",b"c",b"d",b"e",b"f"], shape=[2,3], format='s')
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.tolist)

    def test_memoryview_repr(self):
        m = memoryview(bytearray(9))
        r = m.__repr__()
        self.assertPrawda(r.startswith("<memory"))

        m.release()
        r = m.__repr__()
        self.assertPrawda(r.startswith("<released"))

    def test_memoryview_sequence(self):

        dla fmt w ('d', 'f'):
            inf = float(3e400)
            ex = array.array(fmt, [1.0, inf, 3.0])
            m = memoryview(ex)
            self.assertIn(1.0, m)
            self.assertIn(5e700, m)
            self.assertIn(3.0, m)

        ex = ndarray(9.0, [], format='f')
        m = memoryview(ex)
        self.assertRaises(TypeError, eval, "9.0 w m", locals())

    @contextlib.contextmanager
    def assert_out_of_bounds_error(self, dim):
        przy self.assertRaises(IndexError) jako cm:
            uzyskaj
        self.assertEqual(str(cm.exception),
                         "index out of bounds on dimension %d" % (dim,))

    def test_memoryview_index(self):

        # ndim = 0
        ex = ndarray(12.5, shape=[], format='d')
        m = memoryview(ex)
        self.assertEqual(m[()], 12.5)
        self.assertEqual(m[...], m)
        self.assertEqual(m[...], ex)
        self.assertRaises(TypeError, m.__getitem__, 0)

        ex = ndarray((1,2,3), shape=[], format='iii')
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.__getitem__, ())

        # range
        ex = ndarray(list(range(7)), shape=[7], flags=ND_WRITABLE)
        m = memoryview(ex)

        self.assertRaises(IndexError, m.__getitem__, 2**64)
        self.assertRaises(TypeError, m.__getitem__, 2.0)
        self.assertRaises(TypeError, m.__getitem__, 0.0)

        # out of bounds
        self.assertRaises(IndexError, m.__getitem__, -8)
        self.assertRaises(IndexError, m.__getitem__, 8)

        # multi-dimensional
        ex = ndarray(list(range(12)), shape=[3,4], flags=ND_WRITABLE)
        m = memoryview(ex)

        self.assertEqual(m[0, 0], 0)
        self.assertEqual(m[2, 0], 8)
        self.assertEqual(m[2, 3], 11)
        self.assertEqual(m[-1, -1], 11)
        self.assertEqual(m[-3, -4], 0)

        # out of bounds
        dla index w (3, -4):
            przy self.assert_out_of_bounds_error(dim=1):
                m[index, 0]
        dla index w (4, -5):
            przy self.assert_out_of_bounds_error(dim=2):
                m[0, index]
        self.assertRaises(IndexError, m.__getitem__, (2**64, 0))
        self.assertRaises(IndexError, m.__getitem__, (0, 2**64))

        self.assertRaises(TypeError, m.__getitem__, (0, 0, 0))
        self.assertRaises(TypeError, m.__getitem__, (0.0, 0.0))

        # Not implemented: multidimensional sub-views
        self.assertRaises(NotImplementedError, m.__getitem__, ())
        self.assertRaises(NotImplementedError, m.__getitem__, 0)

    def test_memoryview_assign(self):

        # ndim = 0
        ex = ndarray(12.5, shape=[], format='f', flags=ND_WRITABLE)
        m = memoryview(ex)
        m[()] = 22.5
        self.assertEqual(m[()], 22.5)
        m[...] = 23.5
        self.assertEqual(m[()], 23.5)
        self.assertRaises(TypeError, m.__setitem__, 0, 24.7)

        # read-only
        ex = ndarray(list(range(7)), shape=[7])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.__setitem__, 2, 10)

        # range
        ex = ndarray(list(range(7)), shape=[7], flags=ND_WRITABLE)
        m = memoryview(ex)

        self.assertRaises(IndexError, m.__setitem__, 2**64, 9)
        self.assertRaises(TypeError, m.__setitem__, 2.0, 10)
        self.assertRaises(TypeError, m.__setitem__, 0.0, 11)

        # out of bounds
        self.assertRaises(IndexError, m.__setitem__, -8, 20)
        self.assertRaises(IndexError, m.__setitem__, 8, 25)

        # pack_single() success:
        dla fmt w fmtdict['@']:
            jeżeli fmt == 'c' albo fmt == '?':
                kontynuuj
            ex = ndarray([1,2,3], shape=[3], format=fmt, flags=ND_WRITABLE)
            m = memoryview(ex)
            i = randrange(-3, 3)
            m[i] = 8
            self.assertEqual(m[i], 8)
            self.assertEqual(m[i], ex[i])

        ex = ndarray([b'1', b'2', b'3'], shape=[3], format='c',
                     flags=ND_WRITABLE)
        m = memoryview(ex)
        m[2] = b'9'
        self.assertEqual(m[2], b'9')

        ex = ndarray([Prawda, Nieprawda, Prawda], shape=[3], format='?',
                     flags=ND_WRITABLE)
        m = memoryview(ex)
        m[1] = Prawda
        self.assertEqual(m[1], Prawda)

        # pack_single() exceptions:
        nd = ndarray([b'x'], shape=[1], format='c', flags=ND_WRITABLE)
        m = memoryview(nd)
        self.assertRaises(TypeError, m.__setitem__, 0, 100)

        ex = ndarray(list(range(120)), shape=[1,2,3,4,5], flags=ND_WRITABLE)
        m1 = memoryview(ex)

        dla fmt, _range w fmtdict['@'].items():
            jeżeli (fmt == '?'): # PyObject_IsPrawda() accepts anything
                kontynuuj
            jeżeli fmt == 'c': # special case tested above
                kontynuuj
            m2 = m1.cast(fmt)
            lo, hi = _range
            jeżeli fmt == 'd' albo fmt == 'f':
                lo, hi = -2**1024, 2**1024
            jeżeli fmt != 'P': # PyLong_AsVoidPtr() accepts negative numbers
                self.assertRaises(ValueError, m2.__setitem__, 0, lo-1)
                self.assertRaises(TypeError, m2.__setitem__, 0, "xyz")
            self.assertRaises(ValueError, m2.__setitem__, 0, hi)

        # invalid item
        m2 = m1.cast('c')
        self.assertRaises(ValueError, m2.__setitem__, 0, b'\xff\xff')

        # format nie implemented
        ex = ndarray(list(range(1)), shape=[1], format="xL", flags=ND_WRITABLE)
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.__setitem__, 0, 1)

        ex = ndarray([b'12345'], shape=[1], format="s", flags=ND_WRITABLE)
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.__setitem__, 0, 1)

        # multi-dimensional
        ex = ndarray(list(range(12)), shape=[3,4], flags=ND_WRITABLE)
        m = memoryview(ex)
        m[0,1] = 42
        self.assertEqual(ex[0][1], 42)
        m[-1,-1] = 43
        self.assertEqual(ex[2][3], 43)
        # errors
        dla index w (3, -4):
            przy self.assert_out_of_bounds_error(dim=1):
                m[index, 0] = 0
        dla index w (4, -5):
            przy self.assert_out_of_bounds_error(dim=2):
                m[0, index] = 0
        self.assertRaises(IndexError, m.__setitem__, (2**64, 0), 0)
        self.assertRaises(IndexError, m.__setitem__, (0, 2**64), 0)

        self.assertRaises(TypeError, m.__setitem__, (0, 0, 0), 0)
        self.assertRaises(TypeError, m.__setitem__, (0.0, 0.0), 0)

        # Not implemented: multidimensional sub-views
        self.assertRaises(NotImplementedError, m.__setitem__, 0, [2, 3])

    def test_memoryview_slice(self):

        ex = ndarray(list(range(12)), shape=[12], flags=ND_WRITABLE)
        m = memoryview(ex)

        # zero step
        self.assertRaises(ValueError, m.__getitem__, slice(0,2,0))
        self.assertRaises(ValueError, m.__setitem__, slice(0,2,0),
                          bytearray([1,2]))

        # 0-dim slicing (identity function)
        self.assertRaises(NotImplementedError, m.__getitem__, ())

        # multidimensional slices
        ex = ndarray(list(range(12)), shape=[12], flags=ND_WRITABLE)
        m = memoryview(ex)

        self.assertRaises(NotImplementedError, m.__getitem__,
                          (slice(0,2,1), slice(0,2,1)))
        self.assertRaises(NotImplementedError, m.__setitem__,
                          (slice(0,2,1), slice(0,2,1)), bytearray([1,2]))

        # invalid slice tuple
        self.assertRaises(TypeError, m.__getitem__, (slice(0,2,1), {}))
        self.assertRaises(TypeError, m.__setitem__, (slice(0,2,1), {}),
                          bytearray([1,2]))

        # rvalue jest nie an exporter
        self.assertRaises(TypeError, m.__setitem__, slice(0,1,1), [1])

        # non-contiguous slice assignment
        dla flags w (0, ND_PIL):
            ex1 = ndarray(list(range(12)), shape=[12], strides=[-1], offset=11,
                          flags=ND_WRITABLE|flags)
            ex2 = ndarray(list(range(24)), shape=[12], strides=[2], flags=flags)
            m1 = memoryview(ex1)
            m2 = memoryview(ex2)

            ex1[2:5] = ex1[2:5]
            m1[2:5] = m2[2:5]

            self.assertEqual(m1, ex1)
            self.assertEqual(m2, ex2)

            ex1[1:3][::-1] = ex2[0:2][::1]
            m1[1:3][::-1] = m2[0:2][::1]

            self.assertEqual(m1, ex1)
            self.assertEqual(m2, ex2)

            ex1[4:1:-2][::-1] = ex1[1:4:2][::1]
            m1[4:1:-2][::-1] = m1[1:4:2][::1]

            self.assertEqual(m1, ex1)
            self.assertEqual(m2, ex2)

    def test_memoryview_array(self):

        def cmptest(testcase, a, b, m, singleitem):
            dla i, _ w enumerate(a):
                ai = a[i]
                mi = m[i]
                testcase.assertEqual(ai, mi)
                a[i] = singleitem
                jeżeli singleitem != ai:
                    testcase.assertNotEqual(a, m)
                    testcase.assertNotEqual(a, b)
                inaczej:
                    testcase.assertEqual(a, m)
                    testcase.assertEqual(a, b)
                m[i] = singleitem
                testcase.assertEqual(a, m)
                testcase.assertEqual(b, m)
                a[i] = ai
                m[i] = mi

        dla n w range(1, 5):
            dla fmt, items, singleitem w iter_format(n, 'array'):
                dla lslice w genslices(n):
                    dla rslice w genslices(n):

                        a = array.array(fmt, items)
                        b = array.array(fmt, items)
                        m = memoryview(b)

                        self.assertEqual(m, a)
                        self.assertEqual(m.tolist(), a.tolist())
                        self.assertEqual(m.tobytes(), a.tobytes())
                        self.assertEqual(len(m), len(a))

                        cmptest(self, a, b, m, singleitem)

                        array_err = Nic
                        have_resize = Nic
                        spróbuj:
                            al = a[lslice]
                            ar = a[rslice]
                            a[lslice] = a[rslice]
                            have_resize = len(al) != len(ar)
                        wyjąwszy Exception jako e:
                            array_err = e.__class__

                        m_err = Nic
                        spróbuj:
                            m[lslice] = m[rslice]
                        wyjąwszy Exception jako e:
                            m_err = e.__class__

                        jeżeli have_resize: # memoryview cannot change shape
                            self.assertIs(m_err, ValueError)
                        albo_inaczej m_err albo array_err:
                            self.assertIs(m_err, array_err)
                        inaczej:
                            self.assertEqual(m, a)
                            self.assertEqual(m.tolist(), a.tolist())
                            self.assertEqual(m.tobytes(), a.tobytes())
                            cmptest(self, a, b, m, singleitem)

    def test_memoryview_compare_special_cases(self):

        a = array.array('L', [1, 2, 3])
        b = array.array('L', [1, 2, 7])

        # Ordering comparisons podnieś:
        v = memoryview(a)
        w = memoryview(b)
        dla attr w ('__lt__', '__le__', '__gt__', '__ge__'):
            self.assertIs(getattr(v, attr)(w), NotImplemented)
            self.assertIs(getattr(a, attr)(v), NotImplemented)

        # Released views compare equal to themselves:
        v = memoryview(a)
        v.release()
        self.assertEqual(v, v)
        self.assertNotEqual(v, a)
        self.assertNotEqual(a, v)

        v = memoryview(a)
        w = memoryview(a)
        w.release()
        self.assertNotEqual(v, w)
        self.assertNotEqual(w, v)

        # Operand does nie implement the buffer protocol:
        v = memoryview(a)
        self.assertNotEqual(v, [1, 2, 3])

        # NaNs
        nd = ndarray([(0, 0)], shape=[1], format='l x d x', flags=ND_WRITABLE)
        nd[0] = (-1, float('nan'))
        self.assertNotEqual(memoryview(nd), nd)

        # Depends on issue #15625: the struct module does nie understand 'u'.
        a = array.array('u', 'xyz')
        v = memoryview(a)
        self.assertNotEqual(a, v)
        self.assertNotEqual(v, a)

        # Some ctypes format strings are unknown to the struct module.
        jeżeli ctypes:
            # format: "T{>l:x:>l:y:}"
            klasa BEPoint(ctypes.BigEndianStructure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            point = BEPoint(100, 200)
            a = memoryview(point)
            b = memoryview(point)
            self.assertNotEqual(a, b)
            self.assertNotEqual(a, point)
            self.assertNotEqual(point, a)
            self.assertRaises(NotImplementedError, a.tolist)

    def test_memoryview_compare_ndim_zero(self):

        nd1 = ndarray(1729, shape=[], format='@L')
        nd2 = ndarray(1729, shape=[], format='L', flags=ND_WRITABLE)
        v = memoryview(nd1)
        w = memoryview(nd2)
        self.assertEqual(v, w)
        self.assertEqual(w, v)
        self.assertEqual(v, nd2)
        self.assertEqual(nd2, v)
        self.assertEqual(w, nd1)
        self.assertEqual(nd1, w)

        self.assertNieprawda(v.__ne__(w))
        self.assertNieprawda(w.__ne__(v))

        w[()] = 1728
        self.assertNotEqual(v, w)
        self.assertNotEqual(w, v)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(nd2, v)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(nd1, w)

        self.assertNieprawda(v.__eq__(w))
        self.assertNieprawda(w.__eq__(v))

        nd = ndarray(list(range(12)), shape=[12], flags=ND_WRITABLE|ND_PIL)
        ex = ndarray(list(range(12)), shape=[12], flags=ND_WRITABLE|ND_PIL)
        m = memoryview(ex)

        self.assertEqual(m, nd)
        m[9] = 100
        self.assertNotEqual(m, nd)

        # struct module: equal
        nd1 = ndarray((1729, 1.2, b'12345'), shape=[], format='Lf5s')
        nd2 = ndarray((1729, 1.2, b'12345'), shape=[], format='hf5s',
                      flags=ND_WRITABLE)
        v = memoryview(nd1)
        w = memoryview(nd2)
        self.assertEqual(v, w)
        self.assertEqual(w, v)
        self.assertEqual(v, nd2)
        self.assertEqual(nd2, v)
        self.assertEqual(w, nd1)
        self.assertEqual(nd1, w)

        # struct module: nie equal
        nd1 = ndarray((1729, 1.2, b'12345'), shape=[], format='Lf5s')
        nd2 = ndarray((-1729, 1.2, b'12345'), shape=[], format='hf5s',
                      flags=ND_WRITABLE)
        v = memoryview(nd1)
        w = memoryview(nd2)
        self.assertNotEqual(v, w)
        self.assertNotEqual(w, v)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(nd2, v)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(nd1, w)
        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)

    def test_memoryview_compare_ndim_one(self):

        # contiguous
        nd1 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='@h')
        nd2 = ndarray([-529, 576, -625, 676, 729], shape=[5], format='@h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # contiguous, struct module
        nd1 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='<i')
        nd2 = ndarray([-529, 576, -625, 676, 729], shape=[5], format='>h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # non-contiguous
        nd1 = ndarray([-529, -625, -729], shape=[3], format='@h')
        nd2 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='@h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd2[::2])
        self.assertEqual(w[::2], nd1)
        self.assertEqual(v, w[::2])
        self.assertEqual(v[::-1], w[::-2])

        # non-contiguous, struct module
        nd1 = ndarray([-529, -625, -729], shape=[3], format='!h')
        nd2 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='<l')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd2[::2])
        self.assertEqual(w[::2], nd1)
        self.assertEqual(v, w[::2])
        self.assertEqual(v[::-1], w[::-2])

        # non-contiguous, suboffsets
        nd1 = ndarray([-529, -625, -729], shape=[3], format='@h')
        nd2 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='@h',
                      flags=ND_PIL)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd2[::2])
        self.assertEqual(w[::2], nd1)
        self.assertEqual(v, w[::2])
        self.assertEqual(v[::-1], w[::-2])

        # non-contiguous, suboffsets, struct module
        nd1 = ndarray([-529, -625, -729], shape=[3], format='h  0c')
        nd2 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='>  h',
                      flags=ND_PIL)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd2[::2])
        self.assertEqual(w[::2], nd1)
        self.assertEqual(v, w[::2])
        self.assertEqual(v[::-1], w[::-2])

    def test_memoryview_compare_zero_shape(self):

        # zeros w shape
        nd1 = ndarray([900, 961], shape=[0], format='@h')
        nd2 = ndarray([-900, -961], shape=[0], format='@h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # zeros w shape, struct module
        nd1 = ndarray([900, 961], shape=[0], format='= h0c')
        nd2 = ndarray([-900, -961], shape=[0], format='@   i')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    def test_memoryview_compare_zero_strides(self):

        # zero strides
        nd1 = ndarray([900, 900, 900, 900], shape=[4], format='@L')
        nd2 = ndarray([900], shape=[4], strides=[0], format='L')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # zero strides, struct module
        nd1 = ndarray([(900, 900)]*4, shape=[4], format='@ Li')
        nd2 = ndarray([(900, 900)], shape=[4], strides=[0], format='!L  h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    def test_memoryview_compare_random_formats(self):

        # random single character native formats
        n = 10
        dla char w fmtdict['@m']:
            fmt, items, singleitem = randitems(n, 'memoryview', '@', char)
            dla flags w (0, ND_PIL):
                nd = ndarray(items, shape=[n], format=fmt, flags=flags)
                m = memoryview(nd)
                self.assertEqual(m, nd)

                nd = nd[::-3]
                m = memoryview(nd)
                self.assertEqual(m, nd)

        # random formats
        n = 10
        dla _ w range(100):
            fmt, items, singleitem = randitems(n)
            dla flags w (0, ND_PIL):
                nd = ndarray(items, shape=[n], format=fmt, flags=flags)
                m = memoryview(nd)
                self.assertEqual(m, nd)

                nd = nd[::-3]
                m = memoryview(nd)
                self.assertEqual(m, nd)

    def test_memoryview_compare_multidim_c(self):

        # C-contiguous, different values
        nd1 = ndarray(list(range(-15, 15)), shape=[3, 2, 5], format='@h')
        nd2 = ndarray(list(range(0, 30)), shape=[3, 2, 5], format='@h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # C-contiguous, different values, struct module
        nd1 = ndarray([(0, 1, 2)]*30, shape=[3, 2, 5], format='=f q xxL')
        nd2 = ndarray([(-1.2, 1, 2)]*30, shape=[3, 2, 5], format='< f 2Q')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # C-contiguous, different shape
        nd1 = ndarray(list(range(30)), shape=[2, 3, 5], format='L')
        nd2 = ndarray(list(range(30)), shape=[3, 2, 5], format='L')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # C-contiguous, different shape, struct module
        nd1 = ndarray([(0, 1, 2)]*21, shape=[3, 7], format='! b B xL')
        nd2 = ndarray([(0, 1, 2)]*21, shape=[7, 3], format='= Qx l xxL')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # C-contiguous, different format, struct module
        nd1 = ndarray(list(range(30)), shape=[2, 3, 5], format='L')
        nd2 = ndarray(list(range(30)), shape=[2, 3, 5], format='l')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    def test_memoryview_compare_multidim_fortran(self):

        # Fortran-contiguous, different values
        nd1 = ndarray(list(range(-15, 15)), shape=[5, 2, 3], format='@h',
                      flags=ND_FORTRAN)
        nd2 = ndarray(list(range(0, 30)), shape=[5, 2, 3], format='@h',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # Fortran-contiguous, different values, struct module
        nd1 = ndarray([(2**64-1, -1)]*6, shape=[2, 3], format='=Qq',
                      flags=ND_FORTRAN)
        nd2 = ndarray([(-1, 2**64-1)]*6, shape=[2, 3], format='=qQ',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # Fortran-contiguous, different shape
        nd1 = ndarray(list(range(-15, 15)), shape=[2, 3, 5], format='l',
                      flags=ND_FORTRAN)
        nd2 = ndarray(list(range(-15, 15)), shape=[3, 2, 5], format='l',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # Fortran-contiguous, different shape, struct module
        nd1 = ndarray(list(range(-15, 15)), shape=[2, 3, 5], format='0ll',
                      flags=ND_FORTRAN)
        nd2 = ndarray(list(range(-15, 15)), shape=[3, 2, 5], format='l',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # Fortran-contiguous, different format, struct module
        nd1 = ndarray(list(range(30)), shape=[5, 2, 3], format='@h',
                      flags=ND_FORTRAN)
        nd2 = ndarray(list(range(30)), shape=[5, 2, 3], format='@b',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    def test_memoryview_compare_multidim_mixed(self):

        # mixed C/Fortran contiguous
        lst1 = list(range(-15, 15))
        lst2 = transpose(lst1, [3, 2, 5])
        nd1 = ndarray(lst1, shape=[3, 2, 5], format='@l')
        nd2 = ndarray(lst2, shape=[3, 2, 5], format='l', flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, w)

        # mixed C/Fortran contiguous, struct module
        lst1 = [(-3.3, -22, b'x')]*30
        lst1[5] = (-2.2, -22, b'x')
        lst2 = transpose(lst1, [3, 2, 5])
        nd1 = ndarray(lst1, shape=[3, 2, 5], format='d b c')
        nd2 = ndarray(lst2, shape=[3, 2, 5], format='d h c', flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, w)

        # different values, non-contiguous
        ex1 = ndarray(list(range(40)), shape=[5, 8], format='@I')
        nd1 = ex1[3:1:-1, ::-2]
        ex2 = ndarray(list(range(40)), shape=[5, 8], format='I')
        nd2 = ex2[1:3:1, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # same values, non-contiguous, struct module
        ex1 = ndarray([(2**31-1, -2**31)]*22, shape=[11, 2], format='=ii')
        nd1 = ex1[3:1:-1, ::-2]
        ex2 = ndarray([(2**31-1, -2**31)]*22, shape=[11, 2], format='>ii')
        nd2 = ex2[1:3:1, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # different shape
        ex1 = ndarray(list(range(30)), shape=[2, 3, 5], format='b')
        nd1 = ex1[1:3:, ::-2]
        nd2 = ndarray(list(range(30)), shape=[3, 2, 5], format='b')
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # different shape, struct module
        ex1 = ndarray(list(range(30)), shape=[2, 3, 5], format='B')
        nd1 = ex1[1:3:, ::-2]
        nd2 = ndarray(list(range(30)), shape=[3, 2, 5], format='b')
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # different format, struct module
        ex1 = ndarray([(2, b'123')]*30, shape=[5, 3, 2], format='b3s')
        nd1 = ex1[1:3:, ::-2]
        nd2 = ndarray([(2, b'123')]*30, shape=[5, 3, 2], format='i3s')
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

    def test_memoryview_compare_multidim_zero_shape(self):

        # zeros w shape
        nd1 = ndarray(list(range(30)), shape=[0, 3, 2], format='i')
        nd2 = ndarray(list(range(30)), shape=[5, 0, 2], format='@i')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # zeros w shape, struct module
        nd1 = ndarray(list(range(30)), shape=[0, 3, 2], format='i')
        nd2 = ndarray(list(range(30)), shape=[5, 0, 2], format='@i')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

    def test_memoryview_compare_multidim_zero_strides(self):

        # zero strides
        nd1 = ndarray([900]*80, shape=[4, 5, 4], format='@L')
        nd2 = ndarray([900], shape=[4, 5, 4], strides=[0, 0, 0], format='L')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)
        self.assertEqual(v.tolist(), w.tolist())

        # zero strides, struct module
        nd1 = ndarray([(1, 2)]*10, shape=[2, 5], format='=lQ')
        nd2 = ndarray([(1, 2)], shape=[2, 5], strides=[0, 0], format='<lQ')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    def test_memoryview_compare_multidim_suboffsets(self):

        # suboffsets
        ex1 = ndarray(list(range(40)), shape=[5, 8], format='@I')
        nd1 = ex1[3:1:-1, ::-2]
        ex2 = ndarray(list(range(40)), shape=[5, 8], format='I', flags=ND_PIL)
        nd2 = ex2[1:3:1, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # suboffsets, struct module
        ex1 = ndarray([(2**64-1, -1)]*40, shape=[5, 8], format='=Qq',
                      flags=ND_WRITABLE)
        ex1[2][7] = (1, -2)
        nd1 = ex1[3:1:-1, ::-2]

        ex2 = ndarray([(2**64-1, -1)]*40, shape=[5, 8], format='>Qq',
                      flags=ND_PIL|ND_WRITABLE)
        ex2[2][7] = (1, -2)
        nd2 = ex2[1:3:1, ::-2]

        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # suboffsets, different shape
        ex1 = ndarray(list(range(30)), shape=[2, 3, 5], format='b',
                      flags=ND_PIL)
        nd1 = ex1[1:3:, ::-2]
        nd2 = ndarray(list(range(30)), shape=[3, 2, 5], format='b')
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # suboffsets, different shape, struct module
        ex1 = ndarray([(2**8-1, -1)]*40, shape=[2, 3, 5], format='Bb',
                      flags=ND_PIL|ND_WRITABLE)
        nd1 = ex1[1:2:, ::-2]

        ex2 = ndarray([(2**8-1, -1)]*40, shape=[3, 2, 5], format='Bb')
        nd2 = ex2[1:2:, ::-2]

        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # suboffsets, different format
        ex1 = ndarray(list(range(30)), shape=[5, 3, 2], format='i', flags=ND_PIL)
        nd1 = ex1[1:3:, ::-2]
        ex2 = ndarray(list(range(30)), shape=[5, 3, 2], format='@I', flags=ND_PIL)
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # suboffsets, different format, struct module
        ex1 = ndarray([(b'hello', b'', 1)]*27, shape=[3, 3, 3], format='5s0sP',
                      flags=ND_PIL|ND_WRITABLE)
        ex1[1][2][2] = (b'sushi', b'', 1)
        nd1 = ex1[1:3:, ::-2]

        ex2 = ndarray([(b'hello', b'', 1)]*27, shape=[3, 3, 3], format='5s0sP',
                      flags=ND_PIL|ND_WRITABLE)
        ex1[1][2][2] = (b'sushi', b'', 1)
        nd2 = ex2[1:3:, ::-2]

        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # initialize mixed C/Fortran + suboffsets
        lst1 = list(range(-15, 15))
        lst2 = transpose(lst1, [3, 2, 5])
        nd1 = ndarray(lst1, shape=[3, 2, 5], format='@l', flags=ND_PIL)
        nd2 = ndarray(lst2, shape=[3, 2, 5], format='l', flags=ND_FORTRAN|ND_PIL)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, w)

        # initialize mixed C/Fortran + suboffsets, struct module
        lst1 = [(b'sashimi', b'sliced', 20.05)]*30
        lst1[11] = (b'ramen', b'spicy', 9.45)
        lst2 = transpose(lst1, [3, 2, 5])

        nd1 = ndarray(lst1, shape=[3, 2, 5], format='< 10p 9p d', flags=ND_PIL)
        nd2 = ndarray(lst2, shape=[3, 2, 5], format='> 10p 9p d',
                      flags=ND_FORTRAN|ND_PIL)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, w)

    def test_memoryview_compare_not_equal(self):

        # items nie equal
        dla byteorder w ['=', '<', '>', '!']:
            x = ndarray([2**63]*120, shape=[3,5,2,2,2], format=byteorder+'Q')
            y = ndarray([2**63]*120, shape=[3,5,2,2,2], format=byteorder+'Q',
                        flags=ND_WRITABLE|ND_FORTRAN)
            y[2][3][1][1][1] = 1
            a = memoryview(x)
            b = memoryview(y)
            self.assertEqual(a, x)
            self.assertEqual(b, y)
            self.assertNotEqual(a, b)
            self.assertNotEqual(a, y)
            self.assertNotEqual(b, x)

            x = ndarray([(2**63, 2**31, 2**15)]*120, shape=[3,5,2,2,2],
                        format=byteorder+'QLH')
            y = ndarray([(2**63, 2**31, 2**15)]*120, shape=[3,5,2,2,2],
                        format=byteorder+'QLH', flags=ND_WRITABLE|ND_FORTRAN)
            y[2][3][1][1][1] = (1, 1, 1)
            a = memoryview(x)
            b = memoryview(y)
            self.assertEqual(a, x)
            self.assertEqual(b, y)
            self.assertNotEqual(a, b)
            self.assertNotEqual(a, y)
            self.assertNotEqual(b, x)

    def test_memoryview_check_released(self):

        a = array.array('d', [1.1, 2.2, 3.3])

        m = memoryview(a)
        m.release()

        # PyMemoryView_FromObject()
        self.assertRaises(ValueError, memoryview, m)
        # memoryview.cast()
        self.assertRaises(ValueError, m.cast, 'c')
        # getbuffer()
        self.assertRaises(ValueError, ndarray, m)
        # memoryview.tolist()
        self.assertRaises(ValueError, m.tolist)
        # memoryview.tobytes()
        self.assertRaises(ValueError, m.tobytes)
        # sequence
        self.assertRaises(ValueError, eval, "1.0 w m", locals())
        # subscript
        self.assertRaises(ValueError, m.__getitem__, 0)
        # assignment
        self.assertRaises(ValueError, m.__setitem__, 0, 1)

        dla attr w ('obj', 'nbytes', 'readonly', 'itemsize', 'format', 'ndim',
                     'shape', 'strides', 'suboffsets', 'c_contiguous',
                     'f_contiguous', 'contiguous'):
            self.assertRaises(ValueError, m.__getattribute__, attr)

        # richcompare
        b = array.array('d', [1.1, 2.2, 3.3])
        m1 = memoryview(a)
        m2 = memoryview(b)

        self.assertEqual(m1, m2)
        m1.release()
        self.assertNotEqual(m1, m2)
        self.assertNotEqual(m1, a)
        self.assertEqual(m1, m1)

    def test_memoryview_tobytes(self):
        # Many implicit tests are already w self.verify().

        t = (-529, 576, -625, 676, -729)

        nd = ndarray(t, shape=[5], format='@h')
        m = memoryview(nd)
        self.assertEqual(m, nd)
        self.assertEqual(m.tobytes(), nd.tobytes())

        nd = ndarray([t], shape=[1], format='>hQiLl')
        m = memoryview(nd)
        self.assertEqual(m, nd)
        self.assertEqual(m.tobytes(), nd.tobytes())

        nd = ndarray([t dla _ w range(12)], shape=[2,2,3], format='=hQiLl')
        m = memoryview(nd)
        self.assertEqual(m, nd)
        self.assertEqual(m.tobytes(), nd.tobytes())

        nd = ndarray([t dla _ w range(120)], shape=[5,2,2,3,2],
                     format='<hQiLl')
        m = memoryview(nd)
        self.assertEqual(m, nd)
        self.assertEqual(m.tobytes(), nd.tobytes())

        # Unknown formats are handled: tobytes() purely depends on itemsize.
        jeżeli ctypes:
            # format: "T{>l:x:>l:y:}"
            klasa BEPoint(ctypes.BigEndianStructure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            point = BEPoint(100, 200)
            a = memoryview(point)
            self.assertEqual(a.tobytes(), bytes(point))

    def test_memoryview_get_contiguous(self):
        # Many implicit tests are already w self.verify().

        # no buffer interface
        self.assertRaises(TypeError, get_contiguous, {}, PyBUF_READ, 'F')

        # writable request to read-only object
        self.assertRaises(BufferError, get_contiguous, b'x', PyBUF_WRITE, 'C')

        # writable request to non-contiguous object
        nd = ndarray([1, 2, 3], shape=[2], strides=[2])
        self.assertRaises(BufferError, get_contiguous, nd, PyBUF_WRITE, 'A')

        # scalar, read-only request z read-only exporter
        nd = ndarray(9, shape=(), format="L")
        dla order w ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(m, nd)
            self.assertEqual(m[()], 9)

        # scalar, read-only request z writable exporter
        nd = ndarray(9, shape=(), format="L", flags=ND_WRITABLE)
        dla order w ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(m, nd)
            self.assertEqual(m[()], 9)

        # scalar, writable request
        dla order w ['C', 'F', 'A']:
            nd[()] = 9
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(m, nd)
            self.assertEqual(m[()], 9)

            m[()] = 10
            self.assertEqual(m[()], 10)
            self.assertEqual(nd[()], 10)

        # zeros w shape
        nd = ndarray([1], shape=[0], format="L", flags=ND_WRITABLE)
        dla order w ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertRaises(IndexError, m.__getitem__, 0)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), [])

        nd = ndarray(list(range(8)), shape=[2, 0, 7], format="L",
                     flags=ND_WRITABLE)
        dla order w ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(ndarray(m).tolist(), [[], []])

        # one-dimensional
        nd = ndarray([1], shape=[1], format="h", flags=ND_WRITABLE)
        dla order w ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), nd.tolist())

        nd = ndarray([1, 2, 3], shape=[3], format="b", flags=ND_WRITABLE)
        dla order w ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), nd.tolist())

        # one-dimensional, non-contiguous
        nd = ndarray([1, 2, 3], shape=[2], strides=[2], flags=ND_WRITABLE)
        dla order w ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), nd.tolist())
            self.assertRaises(TypeError, m.__setitem__, 1, 20)
            self.assertEqual(m[1], 3)
            self.assertEqual(nd[1], 3)

        nd = nd[::-1]
        dla order w ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), nd.tolist())
            self.assertRaises(TypeError, m.__setitem__, 1, 20)
            self.assertEqual(m[1], 1)
            self.assertEqual(nd[1], 1)

        # multi-dimensional, contiguous input
        nd = ndarray(list(range(12)), shape=[3, 4], flags=ND_WRITABLE)
        dla order w ['C', 'A']:
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(ndarray(m).tolist(), nd.tolist())

        self.assertRaises(BufferError, get_contiguous, nd, PyBUF_WRITE, 'F')
        m = get_contiguous(nd, PyBUF_READ, order)
        self.assertEqual(ndarray(m).tolist(), nd.tolist())

        nd = ndarray(list(range(12)), shape=[3, 4],
                     flags=ND_WRITABLE|ND_FORTRAN)
        dla order w ['F', 'A']:
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(ndarray(m).tolist(), nd.tolist())

        self.assertRaises(BufferError, get_contiguous, nd, PyBUF_WRITE, 'C')
        m = get_contiguous(nd, PyBUF_READ, order)
        self.assertEqual(ndarray(m).tolist(), nd.tolist())

        # multi-dimensional, non-contiguous input
        nd = ndarray(list(range(12)), shape=[3, 4], flags=ND_WRITABLE|ND_PIL)
        dla order w ['C', 'F', 'A']:
            self.assertRaises(BufferError, get_contiguous, nd, PyBUF_WRITE,
                              order)
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(ndarray(m).tolist(), nd.tolist())

        # flags
        nd = ndarray([1,2,3,4,5], shape=[3], strides=[2])
        m = get_contiguous(nd, PyBUF_READ, 'C')
        self.assertPrawda(m.c_contiguous)

    def test_memoryview_serializing(self):

        # C-contiguous
        size = struct.calcsize('i')
        a = array.array('i', [1,2,3,4,5])
        m = memoryview(a)
        buf = io.BytesIO(m)
        b = bytearray(5*size)
        buf.readinto(b)
        self.assertEqual(m.tobytes(), b)

        # C-contiguous, multi-dimensional
        size = struct.calcsize('L')
        nd = ndarray(list(range(12)), shape=[2,3,2], format="L")
        m = memoryview(nd)
        buf = io.BytesIO(m)
        b = bytearray(2*3*2*size)
        buf.readinto(b)
        self.assertEqual(m.tobytes(), b)

        # Fortran contiguous, multi-dimensional
        #size = struct.calcsize('L')
        #nd = ndarray(list(range(12)), shape=[2,3,2], format="L",
        #             flags=ND_FORTRAN)
        #m = memoryview(nd)
        #buf = io.BytesIO(m)
        #b = bytearray(2*3*2*size)
        #buf.readinto(b)
        #self.assertEqual(m.tobytes(), b)

    def test_memoryview_hash(self):

        # bytes exporter
        b = bytes(list(range(12)))
        m = memoryview(b)
        self.assertEqual(hash(b), hash(m))

        # C-contiguous
        mc = m.cast('c', shape=[3,4])
        self.assertEqual(hash(mc), hash(b))

        # non-contiguous
        mx = m[::-2]
        b = bytes(list(range(12))[::-2])
        self.assertEqual(hash(mx), hash(b))

        # Fortran contiguous
        nd = ndarray(list(range(30)), shape=[3,2,5], flags=ND_FORTRAN)
        m = memoryview(nd)
        self.assertEqual(hash(m), hash(nd))

        # multi-dimensional slice
        nd = ndarray(list(range(30)), shape=[3,2,5])
        x = nd[::2, ::, ::-1]
        m = memoryview(x)
        self.assertEqual(hash(m), hash(x))

        # multi-dimensional slice przy suboffsets
        nd = ndarray(list(range(30)), shape=[2,5,3], flags=ND_PIL)
        x = nd[::2, ::, ::-1]
        m = memoryview(x)
        self.assertEqual(hash(m), hash(x))

        # equality-hash invariant
        x = ndarray(list(range(12)), shape=[12], format='B')
        a = memoryview(x)

        y = ndarray(list(range(12)), shape=[12], format='b')
        b = memoryview(y)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

        # non-byte formats
        nd = ndarray(list(range(12)), shape=[2,2,3], format='L')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.__hash__)

        nd = ndarray(list(range(-6, 6)), shape=[2,2,3], format='h')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.__hash__)

        nd = ndarray(list(range(12)), shape=[2,2,3], format='= L')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.__hash__)

        nd = ndarray(list(range(-6, 6)), shape=[2,2,3], format='< h')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.__hash__)

    def test_memoryview_release(self):

        # Create re-exporter z getbuffer(memoryview), then release the view.
        a = bytearray([1,2,3])
        m = memoryview(a)
        nd = ndarray(m) # re-exporter
        self.assertRaises(BufferError, m.release)
        usuń nd
        m.release()

        a = bytearray([1,2,3])
        m = memoryview(a)
        nd1 = ndarray(m, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        nd2 = ndarray(nd1, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        self.assertIs(nd2.obj, m)
        self.assertRaises(BufferError, m.release)
        usuń nd1, nd2
        m.release()

        # chained views
        a = bytearray([1,2,3])
        m1 = memoryview(a)
        m2 = memoryview(m1)
        nd = ndarray(m2) # re-exporter
        m1.release()
        self.assertRaises(BufferError, m2.release)
        usuń nd
        m2.release()

        a = bytearray([1,2,3])
        m1 = memoryview(a)
        m2 = memoryview(m1)
        nd1 = ndarray(m2, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        nd2 = ndarray(nd1, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        self.assertIs(nd2.obj, m2)
        m1.release()
        self.assertRaises(BufferError, m2.release)
        usuń nd1, nd2
        m2.release()

        # Allow changing layout dopóki buffers are exported.
        nd = ndarray([1,2,3], shape=[3], flags=ND_VAREXPORT)
        m1 = memoryview(nd)

        nd.push([4,5,6,7,8], shape=[5]) # mutate nd
        m2 = memoryview(nd)

        x = memoryview(m1)
        self.assertEqual(x.tolist(), m1.tolist())

        y = memoryview(m2)
        self.assertEqual(y.tolist(), m2.tolist())
        self.assertEqual(y.tolist(), nd.tolist())
        m2.release()
        y.release()

        nd.pop() # pop the current view
        self.assertEqual(x.tolist(), nd.tolist())

        usuń nd
        m1.release()
        x.release()

        # If multiple memoryviews share the same managed buffer, implicit
        # release() w the context manager's __exit__() method should still
        # work.
        def catch22(b):
            przy memoryview(b) jako m2:
                dalej

        x = bytearray(b'123')
        przy memoryview(x) jako m1:
            catch22(m1)
            self.assertEqual(m1[0], ord(b'1'))

        x = ndarray(list(range(12)), shape=[2,2,3], format='l')
        y = ndarray(x, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        z = ndarray(y, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        self.assertIs(z.obj, x)
        przy memoryview(z) jako m:
            catch22(m)
            self.assertEqual(m[0:1].tolist(), [[[0, 1, 2], [3, 4, 5]]])

        # Test garbage collection.
        dla flags w (0, ND_REDIRECT):
            x = bytearray(b'123')
            przy memoryview(x) jako m1:
                usuń x
                y = ndarray(m1, getbuf=PyBUF_FULL_RO, flags=flags)
                przy memoryview(y) jako m2:
                    usuń y
                    z = ndarray(m2, getbuf=PyBUF_FULL_RO, flags=flags)
                    przy memoryview(z) jako m3:
                        usuń z
                        catch22(m3)
                        catch22(m2)
                        catch22(m1)
                        self.assertEqual(m1[0], ord(b'1'))
                        self.assertEqual(m2[1], ord(b'2'))
                        self.assertEqual(m3[2], ord(b'3'))
                        usuń m3
                    usuń m2
                usuń m1

            x = bytearray(b'123')
            przy memoryview(x) jako m1:
                usuń x
                y = ndarray(m1, getbuf=PyBUF_FULL_RO, flags=flags)
                przy memoryview(y) jako m2:
                    usuń y
                    z = ndarray(m2, getbuf=PyBUF_FULL_RO, flags=flags)
                    przy memoryview(z) jako m3:
                        usuń z
                        catch22(m1)
                        catch22(m2)
                        catch22(m3)
                        self.assertEqual(m1[0], ord(b'1'))
                        self.assertEqual(m2[1], ord(b'2'))
                        self.assertEqual(m3[2], ord(b'3'))
                        usuń m1, m2, m3

        # memoryview.release() fails jeżeli the view has exported buffers.
        x = bytearray(b'123')
        przy self.assertRaises(BufferError):
            przy memoryview(x) jako m:
                ex = ndarray(m)
                m[0] == ord(b'1')

    def test_memoryview_redirect(self):

        nd = ndarray([1.0 * x dla x w range(12)], shape=[12], format='d')
        a = array.array('d', [1.0 * x dla x w range(12)])

        dla x w (nd, a):
            y = ndarray(x, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
            z = ndarray(y, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
            m = memoryview(z)

            self.assertIs(y.obj, x)
            self.assertIs(z.obj, x)
            self.assertIs(m.obj, x)

            self.assertEqual(m, x)
            self.assertEqual(m, y)
            self.assertEqual(m, z)

            self.assertEqual(m[1:3], x[1:3])
            self.assertEqual(m[1:3], y[1:3])
            self.assertEqual(m[1:3], z[1:3])
            usuń y, z
            self.assertEqual(m[1:3], x[1:3])

    def test_memoryview_from_static_exporter(self):

        fmt = 'B'
        lst = [0,1,2,3,4,5,6,7,8,9,10,11]

        # exceptions
        self.assertRaises(TypeError, staticarray, 1, 2, 3)

        # view.obj==x
        x = staticarray()
        y = memoryview(x)
        self.verify(y, obj=x,
                    itemsize=1, fmt=fmt, readonly=1,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        dla i w range(12):
            self.assertEqual(y[i], i)
        usuń x
        usuń y

        x = staticarray()
        y = memoryview(x)
        usuń y
        usuń x

        x = staticarray()
        y = ndarray(x, getbuf=PyBUF_FULL_RO)
        z = ndarray(y, getbuf=PyBUF_FULL_RO)
        m = memoryview(z)
        self.assertIs(y.obj, x)
        self.assertIs(m.obj, z)
        self.verify(m, obj=z,
                    itemsize=1, fmt=fmt, readonly=1,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        usuń x, y, z, m

        x = staticarray()
        y = ndarray(x, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        z = ndarray(y, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        m = memoryview(z)
        self.assertIs(y.obj, x)
        self.assertIs(z.obj, x)
        self.assertIs(m.obj, x)
        self.verify(m, obj=x,
                    itemsize=1, fmt=fmt, readonly=1,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        usuń x, y, z, m

        # view.obj==NULL
        x = staticarray(legacy_mode=Prawda)
        y = memoryview(x)
        self.verify(y, obj=Nic,
                    itemsize=1, fmt=fmt, readonly=1,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        dla i w range(12):
            self.assertEqual(y[i], i)
        usuń x
        usuń y

        x = staticarray(legacy_mode=Prawda)
        y = memoryview(x)
        usuń y
        usuń x

        x = staticarray(legacy_mode=Prawda)
        y = ndarray(x, getbuf=PyBUF_FULL_RO)
        z = ndarray(y, getbuf=PyBUF_FULL_RO)
        m = memoryview(z)
        self.assertIs(y.obj, Nic)
        self.assertIs(m.obj, z)
        self.verify(m, obj=z,
                    itemsize=1, fmt=fmt, readonly=1,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        usuń x, y, z, m

        x = staticarray(legacy_mode=Prawda)
        y = ndarray(x, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        z = ndarray(y, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        m = memoryview(z)
        # Clearly setting view.obj==NULL jest inferior, since it
        # messes up the redirection chain:
        self.assertIs(y.obj, Nic)
        self.assertIs(z.obj, y)
        self.assertIs(m.obj, y)
        self.verify(m, obj=y,
                    itemsize=1, fmt=fmt, readonly=1,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        usuń x, y, z, m

    def test_memoryview_getbuffer_undefined(self):

        # getbufferproc does nie adhere to the new documentation
        nd = ndarray([1,2,3], [3], flags=ND_GETBUF_FAIL|ND_GETBUF_UNDEFINED)
        self.assertRaises(BufferError, memoryview, nd)

    def test_issue_7385(self):
        x = ndarray([1,2,3], shape=[3], flags=ND_GETBUF_FAIL)
        self.assertRaises(BufferError, memoryview, x)


jeżeli __name__ == "__main__":
    unittest.main()
