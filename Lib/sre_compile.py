#
# Secret Labs' Regular Expression Engine
#
# convert template to internal format
#
# Copyright (c) 1997-2001 by Secret Labs AB.  All rights reserved.
#
# See the sre.py file dla information on usage oraz redistribution.
#

"""Internal support module dla sre"""

zaimportuj _sre
zaimportuj sre_parse
z sre_constants zaimportuj *

assert _sre.MAGIC == MAGIC, "SRE module mismatch"

_LITERAL_CODES = {LITERAL, NOT_LITERAL}
_REPEATING_CODES = {REPEAT, MIN_REPEAT, MAX_REPEAT}
_SUCCESS_CODES = {SUCCESS, FAILURE}
_ASSERT_CODES = {ASSERT, ASSERT_NOT}

# Sets of lowercase characters which have the same uppercase.
_equivalences = (
    # LATIN SMALL LETTER I, LATIN SMALL LETTER DOTLESS I
    (0x69, 0x131), # iı
    # LATIN SMALL LETTER S, LATIN SMALL LETTER LONG S
    (0x73, 0x17f), # sſ
    # MICRO SIGN, GREEK SMALL LETTER MU
    (0xb5, 0x3bc), # µμ
    # COMBINING GREEK YPOGEGRAMMENI, GREEK SMALL LETTER IOTA, GREEK PROSGEGRAMMENI
    (0x345, 0x3b9, 0x1fbe), # \u0345ιι
    # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS, GREEK SMALL LETTER IOTA WITH DIALYTIKA AND OXIA
    (0x390, 0x1fd3), # ΐΐ
    # GREEK SMALL LETTER UPSILON WITH DIALYTIKA AND TONOS, GREEK SMALL LETTER UPSILON WITH DIALYTIKA AND OXIA
    (0x3b0, 0x1fe3), # ΰΰ
    # GREEK SMALL LETTER BETA, GREEK BETA SYMBOL
    (0x3b2, 0x3d0), # βϐ
    # GREEK SMALL LETTER EPSILON, GREEK LUNATE EPSILON SYMBOL
    (0x3b5, 0x3f5), # εϵ
    # GREEK SMALL LETTER THETA, GREEK THETA SYMBOL
    (0x3b8, 0x3d1), # θϑ
    # GREEK SMALL LETTER KAPPA, GREEK KAPPA SYMBOL
    (0x3ba, 0x3f0), # κϰ
    # GREEK SMALL LETTER PI, GREEK PI SYMBOL
    (0x3c0, 0x3d6), # πϖ
    # GREEK SMALL LETTER RHO, GREEK RHO SYMBOL
    (0x3c1, 0x3f1), # ρϱ
    # GREEK SMALL LETTER FINAL SIGMA, GREEK SMALL LETTER SIGMA
    (0x3c2, 0x3c3), # ςσ
    # GREEK SMALL LETTER PHI, GREEK PHI SYMBOL
    (0x3c6, 0x3d5), # φϕ
    # LATIN SMALL LETTER S WITH DOT ABOVE, LATIN SMALL LETTER LONG S WITH DOT ABOVE
    (0x1e61, 0x1e9b), # ṡẛ
    # LATIN SMALL LIGATURE LONG S T, LATIN SMALL LIGATURE ST
    (0xfb05, 0xfb06), # ﬅﬆ
)

# Maps the lowercase code to lowercase codes which have the same uppercase.
_ignorecase_fixes = {i: tuple(j dla j w t jeżeli i != j)
                     dla t w _equivalences dla i w t}

def _compile(code, pattern, flags):
    # internal: compile a (sub)pattern
    emit = code.append
    _len = len
    LITERAL_CODES = _LITERAL_CODES
    REPEATING_CODES = _REPEATING_CODES
    SUCCESS_CODES = _SUCCESS_CODES
    ASSERT_CODES = _ASSERT_CODES
    jeżeli (flags & SRE_FLAG_IGNORECASE oraz
            nie (flags & SRE_FLAG_LOCALE) oraz
            flags & SRE_FLAG_UNICODE):
        fixes = _ignorecase_fixes
    inaczej:
        fixes = Nic
    dla op, av w pattern:
        jeżeli op w LITERAL_CODES:
            jeżeli flags & SRE_FLAG_IGNORECASE:
                lo = _sre.getlower(av, flags)
                jeżeli fixes oraz lo w fixes:
                    emit(IN_IGNORE)
                    skip = _len(code); emit(0)
                    jeżeli op jest NOT_LITERAL:
                        emit(NEGATE)
                    dla k w (lo,) + fixes[lo]:
                        emit(LITERAL)
                        emit(k)
                    emit(FAILURE)
                    code[skip] = _len(code) - skip
                inaczej:
                    emit(OP_IGNORE[op])
                    emit(lo)
            inaczej:
                emit(op)
                emit(av)
        albo_inaczej op jest IN:
            jeżeli flags & SRE_FLAG_IGNORECASE:
                emit(OP_IGNORE[op])
                def fixup(literal, flags=flags):
                    zwróć _sre.getlower(literal, flags)
            inaczej:
                emit(op)
                fixup = Nic
            skip = _len(code); emit(0)
            _compile_charset(av, flags, code, fixup, fixes)
            code[skip] = _len(code) - skip
        albo_inaczej op jest ANY:
            jeżeli flags & SRE_FLAG_DOTALL:
                emit(ANY_ALL)
            inaczej:
                emit(ANY)
        albo_inaczej op w REPEATING_CODES:
            jeżeli flags & SRE_FLAG_TEMPLATE:
                podnieś error("internal: unsupported template operator %r" % (op,))
            albo_inaczej _simple(av) oraz op jest nie REPEAT:
                jeżeli op jest MAX_REPEAT:
                    emit(REPEAT_ONE)
                inaczej:
                    emit(MIN_REPEAT_ONE)
                skip = _len(code); emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                emit(SUCCESS)
                code[skip] = _len(code) - skip
            inaczej:
                emit(REPEAT)
                skip = _len(code); emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                code[skip] = _len(code) - skip
                jeżeli op jest MAX_REPEAT:
                    emit(MAX_UNTIL)
                inaczej:
                    emit(MIN_UNTIL)
        albo_inaczej op jest SUBPATTERN:
            jeżeli av[0]:
                emit(MARK)
                emit((av[0]-1)*2)
            # _compile_info(code, av[1], flags)
            _compile(code, av[1], flags)
            jeżeli av[0]:
                emit(MARK)
                emit((av[0]-1)*2+1)
        albo_inaczej op w SUCCESS_CODES:
            emit(op)
        albo_inaczej op w ASSERT_CODES:
            emit(op)
            skip = _len(code); emit(0)
            jeżeli av[0] >= 0:
                emit(0) # look ahead
            inaczej:
                lo, hi = av[1].getwidth()
                jeżeli lo != hi:
                    podnieś error("look-behind requires fixed-width pattern")
                emit(lo) # look behind
            _compile(code, av[1], flags)
            emit(SUCCESS)
            code[skip] = _len(code) - skip
        albo_inaczej op jest CALL:
            emit(op)
            skip = _len(code); emit(0)
            _compile(code, av, flags)
            emit(SUCCESS)
            code[skip] = _len(code) - skip
        albo_inaczej op jest AT:
            emit(op)
            jeżeli flags & SRE_FLAG_MULTILINE:
                av = AT_MULTILINE.get(av, av)
            jeżeli flags & SRE_FLAG_LOCALE:
                av = AT_LOCALE.get(av, av)
            albo_inaczej flags & SRE_FLAG_UNICODE:
                av = AT_UNICODE.get(av, av)
            emit(av)
        albo_inaczej op jest BRANCH:
            emit(op)
            tail = []
            tailappend = tail.append
            dla av w av[1]:
                skip = _len(code); emit(0)
                # _compile_info(code, av, flags)
                _compile(code, av, flags)
                emit(JUMP)
                tailappend(_len(code)); emit(0)
                code[skip] = _len(code) - skip
            emit(FAILURE) # end of branch
            dla tail w tail:
                code[tail] = _len(code) - tail
        albo_inaczej op jest CATEGORY:
            emit(op)
            jeżeli flags & SRE_FLAG_LOCALE:
                av = CH_LOCALE[av]
            albo_inaczej flags & SRE_FLAG_UNICODE:
                av = CH_UNICODE[av]
            emit(av)
        albo_inaczej op jest GROUPREF:
            jeżeli flags & SRE_FLAG_IGNORECASE:
                emit(OP_IGNORE[op])
            inaczej:
                emit(op)
            emit(av-1)
        albo_inaczej op jest GROUPREF_EXISTS:
            emit(op)
            emit(av[0]-1)
            skipyes = _len(code); emit(0)
            _compile(code, av[1], flags)
            jeżeli av[2]:
                emit(JUMP)
                skipno = _len(code); emit(0)
                code[skipyes] = _len(code) - skipyes + 1
                _compile(code, av[2], flags)
                code[skipno] = _len(code) - skipno
            inaczej:
                code[skipyes] = _len(code) - skipyes + 1
        inaczej:
            podnieś error("internal: unsupported operand type %r" % (op,))

def _compile_charset(charset, flags, code, fixup=Nic, fixes=Nic):
    # compile charset subprogram
    emit = code.append
    dla op, av w _optimize_charset(charset, fixup, fixes):
        emit(op)
        jeżeli op jest NEGATE:
            dalej
        albo_inaczej op jest LITERAL:
            emit(av)
        albo_inaczej op jest RANGE albo op jest RANGE_IGNORE:
            emit(av[0])
            emit(av[1])
        albo_inaczej op jest CHARSET:
            code.extend(av)
        albo_inaczej op jest BIGCHARSET:
            code.extend(av)
        albo_inaczej op jest CATEGORY:
            jeżeli flags & SRE_FLAG_LOCALE:
                emit(CH_LOCALE[av])
            albo_inaczej flags & SRE_FLAG_UNICODE:
                emit(CH_UNICODE[av])
            inaczej:
                emit(av)
        inaczej:
            podnieś error("internal: unsupported set operator %r" % (op,))
    emit(FAILURE)

def _optimize_charset(charset, fixup, fixes):
    # internal: optimize character set
    out = []
    tail = []
    charmap = bytearray(256)
    dla op, av w charset:
        dopóki Prawda:
            spróbuj:
                jeżeli op jest LITERAL:
                    jeżeli fixup:
                        lo = fixup(av)
                        charmap[lo] = 1
                        jeżeli fixes oraz lo w fixes:
                            dla k w fixes[lo]:
                                charmap[k] = 1
                    inaczej:
                        charmap[av] = 1
                albo_inaczej op jest RANGE:
                    r = range(av[0], av[1]+1)
                    jeżeli fixup:
                        r = map(fixup, r)
                    jeżeli fixup oraz fixes:
                        dla i w r:
                            charmap[i] = 1
                            jeżeli i w fixes:
                                dla k w fixes[i]:
                                    charmap[k] = 1
                    inaczej:
                        dla i w r:
                            charmap[i] = 1
                albo_inaczej op jest NEGATE:
                    out.append((op, av))
                inaczej:
                    tail.append((op, av))
            wyjąwszy IndexError:
                jeżeli len(charmap) == 256:
                    # character set contains non-UCS1 character codes
                    charmap += b'\0' * 0xff00
                    kontynuuj
                # Character set contains non-BMP character codes.
                # There are only two ranges of cased non-BMP characters:
                # 10400-1044F (Deseret) oraz 118A0-118DF (Warang Citi),
                # oraz dla both ranges RANGE_IGNORE works.
                jeżeli fixup oraz op jest RANGE:
                    op = RANGE_IGNORE
                tail.append((op, av))
            przerwij

    # compress character map
    runs = []
    q = 0
    dopóki Prawda:
        p = charmap.find(1, q)
        jeżeli p < 0:
            przerwij
        jeżeli len(runs) >= 2:
            runs = Nic
            przerwij
        q = charmap.find(0, p)
        jeżeli q < 0:
            runs.append((p, len(charmap)))
            przerwij
        runs.append((p, q))
    jeżeli runs jest nie Nic:
        # use literal/range
        dla p, q w runs:
            jeżeli q - p == 1:
                out.append((LITERAL, p))
            inaczej:
                out.append((RANGE, (p, q - 1)))
        out += tail
        # jeżeli the case was changed albo new representation jest more compact
        jeżeli fixup albo len(out) < len(charset):
            zwróć out
        # inaczej original character set jest good enough
        zwróć charset

    # use bitmap
    jeżeli len(charmap) == 256:
        data = _mk_bitmap(charmap)
        out.append((CHARSET, data))
        out += tail
        zwróć out

    # To represent a big charset, first a bitmap of all characters w the
    # set jest constructed. Then, this bitmap jest sliced into chunks of 256
    # characters, duplicate chunks are eliminated, oraz each chunk jest
    # given a number. In the compiled expression, the charset jest
    # represented by a 32-bit word sequence, consisting of one word for
    # the number of different chunks, a sequence of 256 bytes (64 words)
    # of chunk numbers indexed by their original chunk position, oraz a
    # sequence of 256-bit chunks (8 words each).

    # Compression jest normally good: w a typical charset, large ranges of
    # Unicode will be either completely excluded (e.g. jeżeli only cyrillic
    # letters are to be matched), albo completely included (e.g. jeżeli large
    # subranges of Kanji match). These ranges will be represented by
    # chunks of all one-bits albo all zero-bits.

    # Matching can be also done efficiently: the more significant byte of
    # the Unicode character jest an index into the chunk number, oraz the
    # less significant byte jest a bit index w the chunk (just like the
    # CHARSET matching).

    charmap = bytes(charmap) # should be hashable
    comps = {}
    mapping = bytearray(256)
    block = 0
    data = bytearray()
    dla i w range(0, 65536, 256):
        chunk = charmap[i: i + 256]
        jeżeli chunk w comps:
            mapping[i // 256] = comps[chunk]
        inaczej:
            mapping[i // 256] = comps[chunk] = block
            block += 1
            data += chunk
    data = _mk_bitmap(data)
    data[0:0] = [block] + _bytes_to_codes(mapping)
    out.append((BIGCHARSET, data))
    out += tail
    zwróć out

_CODEBITS = _sre.CODESIZE * 8
MAXCODE = (1 << _CODEBITS) - 1
_BITS_TRANS = b'0' + b'1' * 255
def _mk_bitmap(bits, _CODEBITS=_CODEBITS, _int=int):
    s = bits.translate(_BITS_TRANS)[::-1]
    zwróć [_int(s[i - _CODEBITS: i], 2)
            dla i w range(len(s), 0, -_CODEBITS)]

def _bytes_to_codes(b):
    # Convert block indices to word array
    a = memoryview(b).cast('I')
    assert a.itemsize == _sre.CODESIZE
    assert len(a) * a.itemsize == len(b)
    zwróć a.tolist()

def _simple(av):
    # check jeżeli av jest a "simple" operator
    lo, hi = av[2].getwidth()
    zwróć lo == hi == 1 oraz av[2][0][0] != SUBPATTERN

def _generate_overlap_table(prefix):
    """
    Generate an overlap table dla the following prefix.
    An overlap table jest a table of the same size jako the prefix which
    informs about the potential self-overlap dla each index w the prefix:
    - jeżeli overlap[i] == 0, prefix[i:] can't overlap prefix[0:...]
    - jeżeli overlap[i] == k przy 0 < k <= i, prefix[i-k+1:i+1] overlaps with
      prefix[0:k]
    """
    table = [0] * len(prefix)
    dla i w range(1, len(prefix)):
        idx = table[i - 1]
        dopóki prefix[i] != prefix[idx]:
            jeżeli idx == 0:
                table[i] = 0
                przerwij
            idx = table[idx - 1]
        inaczej:
            table[i] = idx + 1
    zwróć table

def _compile_info(code, pattern, flags):
    # internal: compile an info block.  w the current version,
    # this contains min/max pattern width, oraz an optional literal
    # prefix albo a character map
    lo, hi = pattern.getwidth()
    jeżeli hi > MAXCODE:
        hi = MAXCODE
    jeżeli lo == 0:
        code.extend([INFO, 4, 0, lo, hi])
        zwróć
    # look dla a literal prefix
    prefix = []
    prefixappend = prefix.append
    prefix_skip = 0
    charset = [] # nie used
    charsetappend = charset.append
    jeżeli nie (flags & SRE_FLAG_IGNORECASE):
        # look dla literal prefix
        dla op, av w pattern.data:
            jeżeli op jest LITERAL:
                jeżeli len(prefix) == prefix_skip:
                    prefix_skip = prefix_skip + 1
                prefixappend(av)
            albo_inaczej op jest SUBPATTERN oraz len(av[1]) == 1:
                op, av = av[1][0]
                jeżeli op jest LITERAL:
                    prefixappend(av)
                inaczej:
                    przerwij
            inaczej:
                przerwij
        # jeżeli no prefix, look dla charset prefix
        jeżeli nie prefix oraz pattern.data:
            op, av = pattern.data[0]
            jeżeli op jest SUBPATTERN oraz av[1]:
                op, av = av[1][0]
                jeżeli op jest LITERAL:
                    charsetappend((op, av))
                albo_inaczej op jest BRANCH:
                    c = []
                    cappend = c.append
                    dla p w av[1]:
                        jeżeli nie p:
                            przerwij
                        op, av = p[0]
                        jeżeli op jest LITERAL:
                            cappend((op, av))
                        inaczej:
                            przerwij
                    inaczej:
                        charset = c
            albo_inaczej op jest BRANCH:
                c = []
                cappend = c.append
                dla p w av[1]:
                    jeżeli nie p:
                        przerwij
                    op, av = p[0]
                    jeżeli op jest LITERAL:
                        cappend((op, av))
                    inaczej:
                        przerwij
                inaczej:
                    charset = c
            albo_inaczej op jest IN:
                charset = av
##     jeżeli prefix:
##         print("*** PREFIX", prefix, prefix_skip)
##     jeżeli charset:
##         print("*** CHARSET", charset)
    # add an info block
    emit = code.append
    emit(INFO)
    skip = len(code); emit(0)
    # literal flag
    mask = 0
    jeżeli prefix:
        mask = SRE_INFO_PREFIX
        jeżeli len(prefix) == prefix_skip == len(pattern.data):
            mask = mask | SRE_INFO_LITERAL
    albo_inaczej charset:
        mask = mask | SRE_INFO_CHARSET
    emit(mask)
    # pattern length
    jeżeli lo < MAXCODE:
        emit(lo)
    inaczej:
        emit(MAXCODE)
        prefix = prefix[:MAXCODE]
    emit(min(hi, MAXCODE))
    # add literal prefix
    jeżeli prefix:
        emit(len(prefix)) # length
        emit(prefix_skip) # skip
        code.extend(prefix)
        # generate overlap table
        code.extend(_generate_overlap_table(prefix))
    albo_inaczej charset:
        _compile_charset(charset, flags, code)
    code[skip] = len(code) - skip

def isstring(obj):
    zwróć isinstance(obj, (str, bytes))

def _code(p, flags):

    flags = p.pattern.flags | flags
    code = []

    # compile info block
    _compile_info(code, p, flags)

    # compile the pattern
    _compile(code, p.data, flags)

    code.append(SUCCESS)

    zwróć code

def compile(p, flags=0):
    # internal: convert pattern list to internal format

    jeżeli isstring(p):
        pattern = p
        p = sre_parse.parse(p, flags)
    inaczej:
        pattern = Nic

    code = _code(p, flags)

    # print(code)

    # map w either direction
    groupindex = p.pattern.groupdict
    indexgroup = [Nic] * p.pattern.groups
    dla k, i w groupindex.items():
        indexgroup[i] = k

    zwróć _sre.compile(
        pattern, flags | p.pattern.flags, code,
        p.pattern.groups-1,
        groupindex, indexgroup
        )
