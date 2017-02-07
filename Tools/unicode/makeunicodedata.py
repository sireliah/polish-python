#
# (re)generate unicode property oraz type databases
#
# this script converts a unicode 3.2 database file to
# Modules/unicodedata_db.h, Modules/unicodename_db.h,
# oraz Objects/unicodetype_db.h
#
# history:
# 2000-09-24 fl   created (based on bits oraz pieces z unidb)
# 2000-09-25 fl   merged tim's splitbin fixes, separate decomposition table
# 2000-09-25 fl   added character type table
# 2000-09-26 fl   added LINEBREAK, DECIMAL, oraz DIGIT flags/fields (2.0)
# 2000-11-03 fl   expand first/last ranges
# 2001-01-19 fl   added character name tables (2.1)
# 2001-01-21 fl   added decomp compression; dynamic phrasebook threshold
# 2002-09-11 wd   use string methods
# 2002-10-18 mvl  update to Unicode 3.2
# 2002-10-22 mvl  generate NFC tables
# 2002-11-24 mvl  expand all ranges, sort names version-independently
# 2002-11-25 mvl  add UNIDATA_VERSION
# 2004-05-29 perky add east asian width information
# 2006-03-10 mvl  update to Unicode 4.1; add UCD 3.2 delta
# 2008-06-11 gb   add PRINTABLE_MASK dla Atsuo Ishimoto's ascii() patch
# 2011-10-21 ezio add support dla name aliases oraz named sequences
# 2012-01    benjamin add full case mappings
#
# written by Fredrik Lundh (fredrik@pythonware.com)
#

zaimportuj os
zaimportuj sys
zaimportuj zipfile

z textwrap zaimportuj dedent

SCRIPT = sys.argv[0]
VERSION = "3.2"

# The Unicode Database
# --------------------
# When changing UCD version please update
#   * Doc/library/stdtypes.rst, oraz
#   * Doc/library/unicodedata.rst
#   * Doc/reference/lexical_analysis.rst (two occurrences)
UNIDATA_VERSION = "8.0.0"
UNICODE_DATA = "UnicodeData%s.txt"
COMPOSITION_EXCLUSIONS = "CompositionExclusions%s.txt"
EASTASIAN_WIDTH = "EastAsianWidth%s.txt"
UNIHAN = "Unihan%s.zip"
DERIVED_CORE_PROPERTIES = "DerivedCoreProperties%s.txt"
DERIVEDNORMALIZATION_PROPS = "DerivedNormalizationProps%s.txt"
LINE_BREAK = "LineBreak%s.txt"
NAME_ALIASES = "NameAliases%s.txt"
NAMED_SEQUENCES = "NamedSequences%s.txt"
SPECIAL_CASING = "SpecialCasing%s.txt"
CASE_FOLDING = "CaseFolding%s.txt"

# Private Use Areas -- w planes 1, 15, 16
PUA_1 = range(0xE000, 0xF900)
PUA_15 = range(0xF0000, 0xFFFFE)
PUA_16 = range(0x100000, 0x10FFFE)

# we use this ranges of PUA_15 to store name aliases oraz named sequences
NAME_ALIASES_START = 0xF0000
NAMED_SEQUENCES_START = 0xF0200

old_versions = ["3.2.0"]

CATEGORY_NAMES = [ "Cn", "Lu", "Ll", "Lt", "Mn", "Mc", "Me", "Nd",
    "Nl", "No", "Zs", "Zl", "Zp", "Cc", "Cf", "Cs", "Co", "Cn", "Lm",
    "Lo", "Pc", "Pd", "Ps", "Pe", "Pi", "Pf", "Po", "Sm", "Sc", "Sk",
    "So" ]

BIDIRECTIONAL_NAMES = [ "", "L", "LRE", "LRO", "R", "AL", "RLE", "RLO",
    "PDF", "EN", "ES", "ET", "AN", "CS", "NSM", "BN", "B", "S", "WS",
    "ON", "LRI", "RLI", "FSI", "PDI" ]

EASTASIANWIDTH_NAMES = [ "F", "H", "W", "Na", "A", "N" ]

MANDATORY_LINE_BREAKS = [ "BK", "CR", "LF", "NL" ]

# note: should match definitions w Objects/unicodectype.c
ALPHA_MASK = 0x01
DECIMAL_MASK = 0x02
DIGIT_MASK = 0x04
LOWER_MASK = 0x08
LINEBREAK_MASK = 0x10
SPACE_MASK = 0x20
TITLE_MASK = 0x40
UPPER_MASK = 0x80
XID_START_MASK = 0x100
XID_CONTINUE_MASK = 0x200
PRINTABLE_MASK = 0x400
NUMERIC_MASK = 0x800
CASE_IGNORABLE_MASK = 0x1000
CASED_MASK = 0x2000
EXTENDED_CASE_MASK = 0x4000

# these ranges need to match unicodedata.c:is_unified_ideograph
cjk_ranges = [
    ('3400', '4DB5'),
    ('4E00', '9FD5'),
    ('20000', '2A6D6'),
    ('2A700', '2B734'),
    ('2B740', '2B81D'),
    ('2B820', '2CEA1'),
]

def maketables(trace=0):

    print("--- Reading", UNICODE_DATA % "", "...")

    version = ""
    unicode = UnicodeData(UNIDATA_VERSION)

    print(len(list(filter(Nic, unicode.table))), "characters")

    dla version w old_versions:
        print("--- Reading", UNICODE_DATA % ("-"+version), "...")
        old_unicode = UnicodeData(version, cjk_check=Nieprawda)
        print(len(list(filter(Nic, old_unicode.table))), "characters")
        merge_old_version(version, unicode, old_unicode)

    makeunicodename(unicode, trace)
    makeunicodedata(unicode, trace)
    makeunicodetype(unicode, trace)

# --------------------------------------------------------------------
# unicode character properties

def makeunicodedata(unicode, trace):

    dummy = (0, 0, 0, 0, 0, 0)
    table = [dummy]
    cache = {0: dummy}
    index = [0] * len(unicode.chars)

    FILE = "Modules/unicodedata_db.h"

    print("--- Preparing", FILE, "...")

    # 1) database properties

    dla char w unicode.chars:
        record = unicode.table[char]
        jeżeli record:
            # extract database properties
            category = CATEGORY_NAMES.index(record[2])
            combining = int(record[3])
            bidirectional = BIDIRECTIONAL_NAMES.index(record[4])
            mirrored = record[9] == "Y"
            eastasianwidth = EASTASIANWIDTH_NAMES.index(record[15])
            normalizationquickcheck = record[17]
            item = (
                category, combining, bidirectional, mirrored, eastasianwidth,
                normalizationquickcheck
                )
            # add entry to index oraz item tables
            i = cache.get(item)
            jeżeli i jest Nic:
                cache[item] = i = len(table)
                table.append(item)
            index[char] = i

    # 2) decomposition data

    decomp_data = [0]
    decomp_prefix = [""]
    decomp_index = [0] * len(unicode.chars)
    decomp_size = 0

    comp_pairs = []
    comp_first = [Nic] * len(unicode.chars)
    comp_last = [Nic] * len(unicode.chars)

    dla char w unicode.chars:
        record = unicode.table[char]
        jeżeli record:
            jeżeli record[5]:
                decomp = record[5].split()
                jeżeli len(decomp) > 19:
                    podnieś Exception("character %x has a decomposition too large dla nfd_nfkd" % char)
                # prefix
                jeżeli decomp[0][0] == "<":
                    prefix = decomp.pop(0)
                inaczej:
                    prefix = ""
                spróbuj:
                    i = decomp_prefix.index(prefix)
                wyjąwszy ValueError:
                    i = len(decomp_prefix)
                    decomp_prefix.append(prefix)
                prefix = i
                assert prefix < 256
                # content
                decomp = [prefix + (len(decomp)<<8)] + [int(s, 16) dla s w decomp]
                # Collect NFC pairs
                jeżeli nie prefix oraz len(decomp) == 3 oraz \
                   char nie w unicode.exclusions oraz \
                   unicode.table[decomp[1]][3] == "0":
                    p, l, r = decomp
                    comp_first[l] = 1
                    comp_last[r] = 1
                    comp_pairs.append((l,r,char))
                spróbuj:
                    i = decomp_data.index(decomp)
                wyjąwszy ValueError:
                    i = len(decomp_data)
                    decomp_data.extend(decomp)
                    decomp_size = decomp_size + len(decomp) * 2
            inaczej:
                i = 0
            decomp_index[char] = i

    f = l = 0
    comp_first_ranges = []
    comp_last_ranges = []
    prev_f = prev_l = Nic
    dla i w unicode.chars:
        jeżeli comp_first[i] jest nie Nic:
            comp_first[i] = f
            f += 1
            jeżeli prev_f jest Nic:
                prev_f = (i,i)
            albo_inaczej prev_f[1]+1 == i:
                prev_f = prev_f[0],i
            inaczej:
                comp_first_ranges.append(prev_f)
                prev_f = (i,i)
        jeżeli comp_last[i] jest nie Nic:
            comp_last[i] = l
            l += 1
            jeżeli prev_l jest Nic:
                prev_l = (i,i)
            albo_inaczej prev_l[1]+1 == i:
                prev_l = prev_l[0],i
            inaczej:
                comp_last_ranges.append(prev_l)
                prev_l = (i,i)
    comp_first_ranges.append(prev_f)
    comp_last_ranges.append(prev_l)
    total_first = f
    total_last = l

    comp_data = [0]*(total_first*total_last)
    dla f,l,char w comp_pairs:
        f = comp_first[f]
        l = comp_last[l]
        comp_data[f*total_last+l] = char

    print(len(table), "unique properties")
    print(len(decomp_prefix), "unique decomposition prefixes")
    print(len(decomp_data), "unique decomposition entries:", end=' ')
    print(decomp_size, "bytes")
    print(total_first, "first characters w NFC")
    print(total_last, "last characters w NFC")
    print(len(comp_pairs), "NFC pairs")

    print("--- Writing", FILE, "...")

    fp = open(FILE, "w")
    print("/* this file was generated by %s %s */" % (SCRIPT, VERSION), file=fp)
    print(file=fp)
    print('#define UNIDATA_VERSION "%s"' % UNIDATA_VERSION, file=fp)
    print("/* a list of unique database records */", file=fp)
    print("const _PyUnicode_DatabaseRecord _PyUnicode_Database_Records[] = {", file=fp)
    dla item w table:
        print("    {%d, %d, %d, %d, %d, %d}," % item, file=fp)
    print("};", file=fp)
    print(file=fp)

    print("/* Reindexing of NFC first characters. */", file=fp)
    print("#define TOTAL_FIRST",total_first, file=fp)
    print("#define TOTAL_LAST",total_last, file=fp)
    print("struct reindex{int start;short count,index;};", file=fp)
    print("static struct reindex nfc_first[] = {", file=fp)
    dla start,end w comp_first_ranges:
        print("  { %d, %d, %d}," % (start,end-start,comp_first[start]), file=fp)
    print("  {0,0,0}", file=fp)
    print("};\n", file=fp)
    print("static struct reindex nfc_last[] = {", file=fp)
    dla start,end w comp_last_ranges:
        print("  { %d, %d, %d}," % (start,end-start,comp_last[start]), file=fp)
    print("  {0,0,0}", file=fp)
    print("};\n", file=fp)

    # FIXME: <fl> the following tables could be made static, oraz
    # the support code moved into unicodedatabase.c

    print("/* string literals */", file=fp)
    print("const char *_PyUnicode_CategoryNames[] = {", file=fp)
    dla name w CATEGORY_NAMES:
        print("    \"%s\"," % name, file=fp)
    print("    NULL", file=fp)
    print("};", file=fp)

    print("const char *_PyUnicode_BidirectionalNames[] = {", file=fp)
    dla name w BIDIRECTIONAL_NAMES:
        print("    \"%s\"," % name, file=fp)
    print("    NULL", file=fp)
    print("};", file=fp)

    print("const char *_PyUnicode_EastAsianWidthNames[] = {", file=fp)
    dla name w EASTASIANWIDTH_NAMES:
        print("    \"%s\"," % name, file=fp)
    print("    NULL", file=fp)
    print("};", file=fp)

    print("static const char *decomp_prefix[] = {", file=fp)
    dla name w decomp_prefix:
        print("    \"%s\"," % name, file=fp)
    print("    NULL", file=fp)
    print("};", file=fp)

    # split record index table
    index1, index2, shift = splitbins(index, trace)

    print("/* index tables dla the database records */", file=fp)
    print("#define SHIFT", shift, file=fp)
    Array("index1", index1).dump(fp, trace)
    Array("index2", index2).dump(fp, trace)

    # split decomposition index table
    index1, index2, shift = splitbins(decomp_index, trace)

    print("/* decomposition data */", file=fp)
    Array("decomp_data", decomp_data).dump(fp, trace)

    print("/* index tables dla the decomposition data */", file=fp)
    print("#define DECOMP_SHIFT", shift, file=fp)
    Array("decomp_index1", index1).dump(fp, trace)
    Array("decomp_index2", index2).dump(fp, trace)

    index, index2, shift = splitbins(comp_data, trace)
    print("/* NFC pairs */", file=fp)
    print("#define COMP_SHIFT", shift, file=fp)
    Array("comp_index", index).dump(fp, trace)
    Array("comp_data", index2).dump(fp, trace)

    # Generate delta tables dla old versions
    dla version, table, normalization w unicode.changed:
        cversion = version.replace(".","_")
        records = [table[0]]
        cache = {table[0]:0}
        index = [0] * len(table)
        dla i, record w enumerate(table):
            spróbuj:
                index[i] = cache[record]
            wyjąwszy KeyError:
                index[i] = cache[record] = len(records)
                records.append(record)
        index1, index2, shift = splitbins(index, trace)
        print("static const change_record change_records_%s[] = {" % cversion, file=fp)
        dla record w records:
            print("\t{ %s }," % ", ".join(map(str,record)), file=fp)
        print("};", file=fp)
        Array("changes_%s_index" % cversion, index1).dump(fp, trace)
        Array("changes_%s_data" % cversion, index2).dump(fp, trace)
        print("static const change_record* get_change_%s(Py_UCS4 n)" % cversion, file=fp)
        print("{", file=fp)
        print("\tint index;", file=fp)
        print("\tjeżeli (n >= 0x110000) index = 0;", file=fp)
        print("\tinaczej {", file=fp)
        print("\t\tindex = changes_%s_index[n>>%d];" % (cversion, shift), file=fp)
        print("\t\tindex = changes_%s_data[(index<<%d)+(n & %d)];" % \
              (cversion, shift, ((1<<shift)-1)), file=fp)
        print("\t}", file=fp)
        print("\treturn change_records_%s+index;" % cversion, file=fp)
        print("}\n", file=fp)
        print("static Py_UCS4 normalization_%s(Py_UCS4 n)" % cversion, file=fp)
        print("{", file=fp)
        print("\tswitch(n) {", file=fp)
        dla k, v w normalization:
            print("\tcase %s: zwróć 0x%s;" % (hex(k), v), file=fp)
        print("\tdefault: zwróć 0;", file=fp)
        print("\t}\n}\n", file=fp)

    fp.close()

# --------------------------------------------------------------------
# unicode character type tables

def makeunicodetype(unicode, trace):

    FILE = "Objects/unicodetype_db.h"

    print("--- Preparing", FILE, "...")

    # extract unicode types
    dummy = (0, 0, 0, 0, 0, 0)
    table = [dummy]
    cache = {0: dummy}
    index = [0] * len(unicode.chars)
    numeric = {}
    spaces = []
    linebreaks = []
    extra_casing = []

    dla char w unicode.chars:
        record = unicode.table[char]
        jeżeli record:
            # extract database properties
            category = record[2]
            bidirectional = record[4]
            properties = record[16]
            flags = 0
            delta = Prawda
            jeżeli category w ["Lm", "Lt", "Lu", "Ll", "Lo"]:
                flags |= ALPHA_MASK
            jeżeli "Lowercase" w properties:
                flags |= LOWER_MASK
            jeżeli 'Line_Break' w properties albo bidirectional == "B":
                flags |= LINEBREAK_MASK
                linebreaks.append(char)
            jeżeli category == "Zs" albo bidirectional w ("WS", "B", "S"):
                flags |= SPACE_MASK
                spaces.append(char)
            jeżeli category == "Lt":
                flags |= TITLE_MASK
            jeżeli "Uppercase" w properties:
                flags |= UPPER_MASK
            jeżeli char == ord(" ") albo category[0] nie w ("C", "Z"):
                flags |= PRINTABLE_MASK
            jeżeli "XID_Start" w properties:
                flags |= XID_START_MASK
            jeżeli "XID_Continue" w properties:
                flags |= XID_CONTINUE_MASK
            jeżeli "Cased" w properties:
                flags |= CASED_MASK
            jeżeli "Case_Ignorable" w properties:
                flags |= CASE_IGNORABLE_MASK
            sc = unicode.special_casing.get(char)
            cf = unicode.case_folding.get(char, [char])
            jeżeli record[12]:
                upper = int(record[12], 16)
            inaczej:
                upper = char
            jeżeli record[13]:
                lower = int(record[13], 16)
            inaczej:
                lower = char
            jeżeli record[14]:
                title = int(record[14], 16)
            inaczej:
                title = upper
            jeżeli sc jest Nic oraz cf != [lower]:
                sc = ([lower], [title], [upper])
            jeżeli sc jest Nic:
                jeżeli upper == lower == title:
                    upper = lower = title = 0
                inaczej:
                    upper = upper - char
                    lower = lower - char
                    title = title - char
                    assert (abs(upper) <= 2147483647 oraz
                            abs(lower) <= 2147483647 oraz
                            abs(title) <= 2147483647)
            inaczej:
                # This happens either when some character maps to more than one
                # character w uppercase, lowercase, albo titlecase albo the
                # casefolded version of the character jest different z the
                # lowercase. The extra characters are stored w a different
                # array.
                flags |= EXTENDED_CASE_MASK
                lower = len(extra_casing) | (len(sc[0]) << 24)
                extra_casing.extend(sc[0])
                jeżeli cf != sc[0]:
                    lower |= len(cf) << 20
                    extra_casing.extend(cf)
                upper = len(extra_casing) | (len(sc[2]) << 24)
                extra_casing.extend(sc[2])
                # Title jest probably equal to upper.
                jeżeli sc[1] == sc[2]:
                    title = upper
                inaczej:
                    title = len(extra_casing) | (len(sc[1]) << 24)
                    extra_casing.extend(sc[1])
            # decimal digit, integer digit
            decimal = 0
            jeżeli record[6]:
                flags |= DECIMAL_MASK
                decimal = int(record[6])
            digit = 0
            jeżeli record[7]:
                flags |= DIGIT_MASK
                digit = int(record[7])
            jeżeli record[8]:
                flags |= NUMERIC_MASK
                numeric.setdefault(record[8], []).append(char)
            item = (
                upper, lower, title, decimal, digit, flags
                )
            # add entry to index oraz item tables
            i = cache.get(item)
            jeżeli i jest Nic:
                cache[item] = i = len(table)
                table.append(item)
            index[char] = i

    print(len(table), "unique character type entries")
    print(sum(map(len, numeric.values())), "numeric code points")
    print(len(spaces), "whitespace code points")
    print(len(linebreaks), "linebreak code points")
    print(len(extra_casing), "extended case array")

    print("--- Writing", FILE, "...")

    fp = open(FILE, "w")
    print("/* this file was generated by %s %s */" % (SCRIPT, VERSION), file=fp)
    print(file=fp)
    print("/* a list of unique character type descriptors */", file=fp)
    print("const _PyUnicode_TypeRecord _PyUnicode_TypeRecords[] = {", file=fp)
    dla item w table:
        print("    {%d, %d, %d, %d, %d, %d}," % item, file=fp)
    print("};", file=fp)
    print(file=fp)

    print("/* extended case mappings */", file=fp)
    print(file=fp)
    print("const Py_UCS4 _PyUnicode_ExtendedCase[] = {", file=fp)
    dla c w extra_casing:
        print("    %d," % c, file=fp)
    print("};", file=fp)
    print(file=fp)

    # split decomposition index table
    index1, index2, shift = splitbins(index, trace)

    print("/* type indexes */", file=fp)
    print("#define SHIFT", shift, file=fp)
    Array("index1", index1).dump(fp, trace)
    Array("index2", index2).dump(fp, trace)

    # Generate code dla _PyUnicode_ToNumeric()
    numeric_items = sorted(numeric.items())
    print('/* Returns the numeric value jako double dla Unicode characters', file=fp)
    print(' * having this property, -1.0 otherwise.', file=fp)
    print(' */', file=fp)
    print('double _PyUnicode_ToNumeric(Py_UCS4 ch)', file=fp)
    print('{', file=fp)
    print('    switch (ch) {', file=fp)
    dla value, codepoints w numeric_items:
        # Turn text into float literals
        parts = value.split('/')
        parts = [repr(float(part)) dla part w parts]
        value = '/'.join(parts)

        codepoints.sort()
        dla codepoint w codepoints:
            print('    case 0x%04X:' % (codepoint,), file=fp)
        print('        zwróć (double) %s;' % (value,), file=fp)
    print('    }', file=fp)
    print('    zwróć -1.0;', file=fp)
    print('}', file=fp)
    print(file=fp)

    # Generate code dla _PyUnicode_IsWhitespace()
    print("/* Returns 1 dla Unicode characters having the bidirectional", file=fp)
    print(" * type 'WS', 'B' albo 'S' albo the category 'Zs', 0 otherwise.", file=fp)
    print(" */", file=fp)
    print('int _PyUnicode_IsWhitespace(const Py_UCS4 ch)', file=fp)
    print('{', file=fp)
    print('    switch (ch) {', file=fp)

    dla codepoint w sorted(spaces):
        print('    case 0x%04X:' % (codepoint,), file=fp)
    print('        zwróć 1;', file=fp)

    print('    }', file=fp)
    print('    zwróć 0;', file=fp)
    print('}', file=fp)
    print(file=fp)

    # Generate code dla _PyUnicode_IsLinebreak()
    print("/* Returns 1 dla Unicode characters having the line przerwij", file=fp)
    print(" * property 'BK', 'CR', 'LF' albo 'NL' albo having bidirectional", file=fp)
    print(" * type 'B', 0 otherwise.", file=fp)
    print(" */", file=fp)
    print('int _PyUnicode_IsLinebreak(const Py_UCS4 ch)', file=fp)
    print('{', file=fp)
    print('    switch (ch) {', file=fp)
    dla codepoint w sorted(linebreaks):
        print('    case 0x%04X:' % (codepoint,), file=fp)
    print('        zwróć 1;', file=fp)

    print('    }', file=fp)
    print('    zwróć 0;', file=fp)
    print('}', file=fp)
    print(file=fp)

    fp.close()

# --------------------------------------------------------------------
# unicode name database

def makeunicodename(unicode, trace):

    FILE = "Modules/unicodename_db.h"

    print("--- Preparing", FILE, "...")

    # collect names
    names = [Nic] * len(unicode.chars)

    dla char w unicode.chars:
        record = unicode.table[char]
        jeżeli record:
            name = record[1].strip()
            jeżeli name oraz name[0] != "<":
                names[char] = name + chr(0)

    print(len(list(n dla n w names jeżeli n jest nie Nic)), "distinct names")

    # collect unique words z names (niee that we differ between
    # words inside a sentence, oraz words ending a sentence.  the
    # latter includes the trailing null byte.

    words = {}
    n = b = 0
    dla char w unicode.chars:
        name = names[char]
        jeżeli name:
            w = name.split()
            b = b + len(name)
            n = n + len(w)
            dla w w w:
                l = words.get(w)
                jeżeli l:
                    l.append(Nic)
                inaczej:
                    words[w] = [len(words)]

    print(n, "words w text;", b, "bytes")

    wordlist = list(words.items())

    # sort on falling frequency, then by name
    def word_key(a):
        aword, alist = a
        zwróć -len(alist), aword
    wordlist.sort(key=word_key)

    # figure out how many phrasebook escapes we need
    escapes = 0
    dopóki escapes * 256 < len(wordlist):
        escapes = escapes + 1
    print(escapes, "escapes")

    short = 256 - escapes

    assert short > 0

    print(short, "short indexes w lexicon")

    # statistics
    n = 0
    dla i w range(short):
        n = n + len(wordlist[i][1])
    print(n, "short indexes w phrasebook")

    # pick the most commonly used words, oraz sort the rest on falling
    # length (to maximize overlap)

    wordlist, wordtail = wordlist[:short], wordlist[short:]
    wordtail.sort(key=lambda a: a[0], reverse=Prawda)
    wordlist.extend(wordtail)

    # generate lexicon z words

    lexicon_offset = [0]
    lexicon = ""
    words = {}

    # build a lexicon string
    offset = 0
    dla w, x w wordlist:
        # encoding: bit 7 indicates last character w word (chr(128)
        # indicates the last character w an entire string)
        ww = w[:-1] + chr(ord(w[-1])+128)
        # reuse string tails, when possible
        o = lexicon.find(ww)
        jeżeli o < 0:
            o = offset
            lexicon = lexicon + ww
            offset = offset + len(w)
        words[w] = len(lexicon_offset)
        lexicon_offset.append(o)

    lexicon = list(map(ord, lexicon))

    # generate phrasebook z names oraz lexicon
    phrasebook = [0]
    phrasebook_offset = [0] * len(unicode.chars)
    dla char w unicode.chars:
        name = names[char]
        jeżeli name:
            w = name.split()
            phrasebook_offset[char] = len(phrasebook)
            dla w w w:
                i = words[w]
                jeżeli i < short:
                    phrasebook.append(i)
                inaczej:
                    # store jako two bytes
                    phrasebook.append((i>>8) + short)
                    phrasebook.append(i&255)

    assert getsize(phrasebook) == 1

    #
    # unicode name hash table

    # extract names
    data = []
    dla char w unicode.chars:
        record = unicode.table[char]
        jeżeli record:
            name = record[1].strip()
            jeżeli name oraz name[0] != "<":
                data.append((name, char))

    # the magic number 47 was chosen to minimize the number of
    # collisions on the current data set.  jeżeli you like, change it
    # oraz see what happens...

    codehash = Hash("code", data, 47)

    print("--- Writing", FILE, "...")

    fp = open(FILE, "w")
    print("/* this file was generated by %s %s */" % (SCRIPT, VERSION), file=fp)
    print(file=fp)
    print("#define NAME_MAXLEN", 256, file=fp)
    print(file=fp)
    print("/* lexicon */", file=fp)
    Array("lexicon", lexicon).dump(fp, trace)
    Array("lexicon_offset", lexicon_offset).dump(fp, trace)

    # split decomposition index table
    offset1, offset2, shift = splitbins(phrasebook_offset, trace)

    print("/* code->name phrasebook */", file=fp)
    print("#define phrasebook_shift", shift, file=fp)
    print("#define phrasebook_short", short, file=fp)

    Array("phrasebook", phrasebook).dump(fp, trace)
    Array("phrasebook_offset1", offset1).dump(fp, trace)
    Array("phrasebook_offset2", offset2).dump(fp, trace)

    print("/* name->code dictionary */", file=fp)
    codehash.dump(fp, trace)

    print(file=fp)
    print('static const unsigned int aliases_start = %#x;' %
          NAME_ALIASES_START, file=fp)
    print('static const unsigned int aliases_end = %#x;' %
          (NAME_ALIASES_START + len(unicode.aliases)), file=fp)

    print('static const unsigned int name_aliases[] = {', file=fp)
    dla name, codepoint w unicode.aliases:
        print('    0x%04X,' % codepoint, file=fp)
    print('};', file=fp)

    # In Unicode 6.0.0, the sequences contain at most 4 BMP chars,
    # so we are using Py_UCS2 seq[4].  This needs to be updated jeżeli longer
    # sequences albo sequences przy non-BMP chars are added.
    # unicodedata_lookup should be adapted too.
    print(dedent("""
        typedef struct NamedSequence {
            int seqlen;
            Py_UCS2 seq[4];
        } named_sequence;
        """), file=fp)

    print('static const unsigned int named_sequences_start = %#x;' %
          NAMED_SEQUENCES_START, file=fp)
    print('static const unsigned int named_sequences_end = %#x;' %
          (NAMED_SEQUENCES_START + len(unicode.named_sequences)), file=fp)

    print('static const named_sequence named_sequences[] = {', file=fp)
    dla name, sequence w unicode.named_sequences:
        seq_str = ', '.join('0x%04X' % cp dla cp w sequence)
        print('    {%d, {%s}},' % (len(sequence), seq_str), file=fp)
    print('};', file=fp)

    fp.close()


def merge_old_version(version, new, old):
    # Changes to exclusion file nie implemented yet
    jeżeli old.exclusions != new.exclusions:
        podnieś NotImplementedError("exclusions differ")

    # In these change records, 0xFF means "no change"
    bidir_changes = [0xFF]*0x110000
    category_changes = [0xFF]*0x110000
    decimal_changes = [0xFF]*0x110000
    mirrored_changes = [0xFF]*0x110000
    # In numeric data, 0 means "no change",
    # -1 means "did nie have a numeric value
    numeric_changes = [0] * 0x110000
    # normalization_changes jest a list of key-value pairs
    normalization_changes = []
    dla i w range(0x110000):
        jeżeli new.table[i] jest Nic:
            # Characters unassigned w the new version ought to
            # be unassigned w the old one
            assert old.table[i] jest Nic
            kontynuuj
        # check characters unassigned w the old version
        jeżeli old.table[i] jest Nic:
            # category 0 jest "unassigned"
            category_changes[i] = 0
            kontynuuj
        # check characters that differ
        jeżeli old.table[i] != new.table[i]:
            dla k w range(len(old.table[i])):
                jeżeli old.table[i][k] != new.table[i][k]:
                    value = old.table[i][k]
                    jeżeli k == 1 oraz i w PUA_15:
                        # the name jest nie set w the old.table, but w the
                        # new.table we are using it dla aliases oraz named seq
                        assert value == ''
                    albo_inaczej k == 2:
                        #print "CATEGORY",hex(i), old.table[i][k], new.table[i][k]
                        category_changes[i] = CATEGORY_NAMES.index(value)
                    albo_inaczej k == 4:
                        #print "BIDIR",hex(i), old.table[i][k], new.table[i][k]
                        bidir_changes[i] = BIDIRECTIONAL_NAMES.index(value)
                    albo_inaczej k == 5:
                        #print "DECOMP",hex(i), old.table[i][k], new.table[i][k]
                        # We assume that all normalization changes are w 1:1 mappings
                        assert " " nie w value
                        normalization_changes.append((i, value))
                    albo_inaczej k == 6:
                        #print "DECIMAL",hex(i), old.table[i][k], new.table[i][k]
                        # we only support changes where the old value jest a single digit
                        assert value w "0123456789"
                        decimal_changes[i] = int(value)
                    albo_inaczej k == 8:
                        # print "NUMERIC",hex(i), `old.table[i][k]`, new.table[i][k]
                        # Since 0 encodes "no change", the old value jest better nie 0
                        jeżeli nie value:
                            numeric_changes[i] = -1
                        inaczej:
                            numeric_changes[i] = float(value)
                            assert numeric_changes[i] nie w (0, -1)
                    albo_inaczej k == 9:
                        jeżeli value == 'Y':
                            mirrored_changes[i] = '1'
                        inaczej:
                            mirrored_changes[i] = '0'
                    albo_inaczej k == 11:
                        # change to ISO comment, ignore
                        dalej
                    albo_inaczej k == 12:
                        # change to simple uppercase mapping; ignore
                        dalej
                    albo_inaczej k == 13:
                        # change to simple lowercase mapping; ignore
                        dalej
                    albo_inaczej k == 14:
                        # change to simple titlecase mapping; ignore
                        dalej
                    albo_inaczej k == 16:
                        # derived property changes; nie yet
                        dalej
                    albo_inaczej k == 17:
                        # normalization quickchecks are nie performed
                        # dla older versions
                        dalej
                    inaczej:
                        klasa Difference(Exception):pass
                        podnieś Difference(hex(i), k, old.table[i], new.table[i])
    new.changed.append((version, list(zip(bidir_changes, category_changes,
                                     decimal_changes, mirrored_changes,
                                     numeric_changes)),
                        normalization_changes))

def open_data(template, version):
    local = template % ('-'+version,)
    jeżeli nie os.path.exists(local):
        zaimportuj urllib.request
        jeżeli version == '3.2.0':
            # irregular url structure
            url = 'http://www.unicode.org/Public/3.2-Update/' + local
        inaczej:
            url = ('http://www.unicode.org/Public/%s/ucd/'+template) % (version, '')
        urllib.request.urlretrieve(url, filename=local)
    jeżeli local.endswith('.txt'):
        zwróć open(local, encoding='utf-8')
    inaczej:
        # Unihan.zip
        zwróć open(local, 'rb')

# --------------------------------------------------------------------
# the following support code jest taken z the unidb utilities
# Copyright (c) 1999-2000 by Secret Labs AB

# load a unicode-data file z disk

klasa UnicodeData:
    # Record structure:
    # [ID, name, category, combining, bidi, decomp,  (6)
    #  decimal, digit, numeric, bidi-mirrored, Unicode-1-name, (11)
    #  ISO-comment, uppercase, lowercase, titlecase, ea-width, (16)
    #  derived-props] (17)

    def __init__(self, version,
                 linebreakprops=Nieprawda,
                 expand=1,
                 cjk_check=Prawda):
        self.changed = []
        table = [Nic] * 0x110000
        przy open_data(UNICODE_DATA, version) jako file:
            dopóki 1:
                s = file.readline()
                jeżeli nie s:
                    przerwij
                s = s.strip().split(";")
                char = int(s[0], 16)
                table[char] = s

        cjk_ranges_found = []

        # expand first-last ranges
        jeżeli expand:
            field = Nic
            dla i w range(0, 0x110000):
                s = table[i]
                jeżeli s:
                    jeżeli s[1][-6:] == "First>":
                        s[1] = ""
                        field = s
                    albo_inaczej s[1][-5:] == "Last>":
                        jeżeli s[1].startswith("<CJK Ideograph"):
                            cjk_ranges_found.append((field[0],
                                                     s[0]))
                        s[1] = ""
                        field = Nic
                albo_inaczej field:
                    f2 = field[:]
                    f2[0] = "%X" % i
                    table[i] = f2
            jeżeli cjk_check oraz cjk_ranges != cjk_ranges_found:
                podnieś ValueError("CJK ranges deviate: have %r" % cjk_ranges_found)

        # public attributes
        self.filename = UNICODE_DATA % ''
        self.table = table
        self.chars = list(range(0x110000)) # unicode 3.2

        # check dla name aliases oraz named sequences, see #12753
        # aliases oraz named sequences are nie w 3.2.0
        jeżeli version != '3.2.0':
            self.aliases = []
            # store aliases w the Private Use Area 15, w range U+F0000..U+F00FF,
            # w order to take advantage of the compression oraz lookup
            # algorithms used dla the other characters
            pua_index = NAME_ALIASES_START
            przy open_data(NAME_ALIASES, version) jako file:
                dla s w file:
                    s = s.strip()
                    jeżeli nie s albo s.startswith('#'):
                        kontynuuj
                    char, name, abbrev = s.split(';')
                    char = int(char, 16)
                    self.aliases.append((name, char))
                    # also store the name w the PUA 1
                    self.table[pua_index][1] = name
                    pua_index += 1
            assert pua_index - NAME_ALIASES_START == len(self.aliases)

            self.named_sequences = []
            # store named sequences w the PUA 1, w range U+F0100..,
            # w order to take advantage of the compression oraz lookup
            # algorithms used dla the other characters.

            assert pua_index < NAMED_SEQUENCES_START
            pua_index = NAMED_SEQUENCES_START
            przy open_data(NAMED_SEQUENCES, version) jako file:
                dla s w file:
                    s = s.strip()
                    jeżeli nie s albo s.startswith('#'):
                        kontynuuj
                    name, chars = s.split(';')
                    chars = tuple(int(char, 16) dla char w chars.split())
                    # check that the structure defined w makeunicodename jest OK
                    assert 2 <= len(chars) <= 4, "change the Py_UCS2 array size"
                    assert all(c <= 0xFFFF dla c w chars), ("use Py_UCS4 w "
                        "the NamedSequence struct oraz w unicodedata_lookup")
                    self.named_sequences.append((name, chars))
                    # also store these w the PUA 1
                    self.table[pua_index][1] = name
                    pua_index += 1
            assert pua_index - NAMED_SEQUENCES_START == len(self.named_sequences)

        self.exclusions = {}
        przy open_data(COMPOSITION_EXCLUSIONS, version) jako file:
            dla s w file:
                s = s.strip()
                jeżeli nie s:
                    kontynuuj
                jeżeli s[0] == '#':
                    kontynuuj
                char = int(s.split()[0],16)
                self.exclusions[char] = 1

        widths = [Nic] * 0x110000
        przy open_data(EASTASIAN_WIDTH, version) jako file:
            dla s w file:
                s = s.strip()
                jeżeli nie s:
                    kontynuuj
                jeżeli s[0] == '#':
                    kontynuuj
                s = s.split()[0].split(';')
                jeżeli '..' w s[0]:
                    first, last = [int(c, 16) dla c w s[0].split('..')]
                    chars = list(range(first, last+1))
                inaczej:
                    chars = [int(s[0], 16)]
                dla char w chars:
                    widths[char] = s[1]

        dla i w range(0, 0x110000):
            jeżeli table[i] jest nie Nic:
                table[i].append(widths[i])

        dla i w range(0, 0x110000):
            jeżeli table[i] jest nie Nic:
                table[i].append(set())

        przy open_data(DERIVED_CORE_PROPERTIES, version) jako file:
            dla s w file:
                s = s.split('#', 1)[0].strip()
                jeżeli nie s:
                    kontynuuj

                r, p = s.split(";")
                r = r.strip()
                p = p.strip()
                jeżeli ".." w r:
                    first, last = [int(c, 16) dla c w r.split('..')]
                    chars = list(range(first, last+1))
                inaczej:
                    chars = [int(r, 16)]
                dla char w chars:
                    jeżeli table[char]:
                        # Some properties (e.g. Default_Ignorable_Code_Point)
                        # apply to unassigned code points; ignore them
                        table[char][-1].add(p)

        przy open_data(LINE_BREAK, version) jako file:
            dla s w file:
                s = s.partition('#')[0]
                s = [i.strip() dla i w s.split(';')]
                jeżeli len(s) < 2 albo s[1] nie w MANDATORY_LINE_BREAKS:
                    kontynuuj
                jeżeli '..' nie w s[0]:
                    first = last = int(s[0], 16)
                inaczej:
                    first, last = [int(c, 16) dla c w s[0].split('..')]
                dla char w range(first, last+1):
                    table[char][-1].add('Line_Break')

        # We only want the quickcheck properties
        # Format: NF?_QC; Y(es)/N(o)/M(aybe)
        # Yes jest the default, hence only N oraz M occur
        # In 3.2.0, the format was different (NF?_NO)
        # The parsing will incorrectly determine these as
        # "yes", however, unicodedata.c will nie perform quickchecks
        # dla older versions, oraz no delta records will be created.
        quickchecks = [0] * 0x110000
        qc_order = 'NFD_QC NFKD_QC NFC_QC NFKC_QC'.split()
        przy open_data(DERIVEDNORMALIZATION_PROPS, version) jako file:
            dla s w file:
                jeżeli '#' w s:
                    s = s[:s.index('#')]
                s = [i.strip() dla i w s.split(';')]
                jeżeli len(s) < 2 albo s[1] nie w qc_order:
                    kontynuuj
                quickcheck = 'MN'.index(s[2]) + 1 # Maybe albo No
                quickcheck_shift = qc_order.index(s[1])*2
                quickcheck <<= quickcheck_shift
                jeżeli '..' nie w s[0]:
                    first = last = int(s[0], 16)
                inaczej:
                    first, last = [int(c, 16) dla c w s[0].split('..')]
                dla char w range(first, last+1):
                    assert nie (quickchecks[char]>>quickcheck_shift)&3
                    quickchecks[char] |= quickcheck
        dla i w range(0, 0x110000):
            jeżeli table[i] jest nie Nic:
                table[i].append(quickchecks[i])

        przy open_data(UNIHAN, version) jako file:
            zip = zipfile.ZipFile(file)
            jeżeli version == '3.2.0':
                data = zip.open('Unihan-3.2.0.txt').read()
            inaczej:
                data = zip.open('Unihan_NumericValues.txt').read()
        dla line w data.decode("utf-8").splitlines():
            jeżeli nie line.startswith('U+'):
                kontynuuj
            code, tag, value = line.split(Nic, 3)[:3]
            jeżeli tag nie w ('kAccountingNumeric', 'kPrimaryNumeric',
                           'kOtherNumeric'):
                kontynuuj
            value = value.strip().replace(',', '')
            i = int(code[2:], 16)
            # Patch the numeric field
            jeżeli table[i] jest nie Nic:
                table[i][8] = value
        sc = self.special_casing = {}
        przy open_data(SPECIAL_CASING, version) jako file:
            dla s w file:
                s = s[:-1].split('#', 1)[0]
                jeżeli nie s:
                    kontynuuj
                data = s.split("; ")
                jeżeli data[4]:
                    # We ignore all conditionals (since they depend on
                    # languages) wyjąwszy dla one, which jest hardcoded. See
                    # handle_capital_sigma w unicodeobject.c.
                    kontynuuj
                c = int(data[0], 16)
                lower = [int(char, 16) dla char w data[1].split()]
                title = [int(char, 16) dla char w data[2].split()]
                upper = [int(char, 16) dla char w data[3].split()]
                sc[c] = (lower, title, upper)
        cf = self.case_folding = {}
        jeżeli version != '3.2.0':
            przy open_data(CASE_FOLDING, version) jako file:
                dla s w file:
                    s = s[:-1].split('#', 1)[0]
                    jeżeli nie s:
                        kontynuuj
                    data = s.split("; ")
                    jeżeli data[1] w "CF":
                        c = int(data[0], 16)
                        cf[c] = [int(char, 16) dla char w data[2].split()]

    def uselatin1(self):
        # restrict character range to ISO Latin 1
        self.chars = list(range(256))

# hash table tools

# this jest a straight-forward reimplementation of Python's built-in
# dictionary type, using a static data structure, oraz a custom string
# hash algorithm.

def myhash(s, magic):
    h = 0
    dla c w map(ord, s.upper()):
        h = (h * magic) + c
        ix = h & 0xff000000
        jeżeli ix:
            h = (h ^ ((ix>>24) & 0xff)) & 0x00ffffff
    zwróć h

SIZES = [
    (4,3), (8,3), (16,3), (32,5), (64,3), (128,3), (256,29), (512,17),
    (1024,9), (2048,5), (4096,83), (8192,27), (16384,43), (32768,3),
    (65536,45), (131072,9), (262144,39), (524288,39), (1048576,9),
    (2097152,5), (4194304,3), (8388608,33), (16777216,27)
]

klasa Hash:
    def __init__(self, name, data, magic):
        # turn a (key, value) list into a static hash table structure

        # determine table size
        dla size, poly w SIZES:
            jeżeli size > len(data):
                poly = size + poly
                przerwij
        inaczej:
            podnieś AssertionError("ran out of polynomials")

        print(size, "slots w hash table")

        table = [Nic] * size

        mask = size-1

        n = 0

        hash = myhash

        # initialize hash table
        dla key, value w data:
            h = hash(key, magic)
            i = (~h) & mask
            v = table[i]
            jeżeli v jest Nic:
                table[i] = value
                kontynuuj
            incr = (h ^ (h >> 3)) & mask;
            jeżeli nie incr:
                incr = mask
            dopóki 1:
                n = n + 1
                i = (i + incr) & mask
                v = table[i]
                jeżeli v jest Nic:
                    table[i] = value
                    przerwij
                incr = incr << 1
                jeżeli incr > mask:
                    incr = incr ^ poly

        print(n, "collisions")
        self.collisions = n

        dla i w range(len(table)):
            jeżeli table[i] jest Nic:
                table[i] = 0

        self.data = Array(name + "_hash", table)
        self.magic = magic
        self.name = name
        self.size = size
        self.poly = poly

    def dump(self, file, trace):
        # write data to file, jako a C array
        self.data.dump(file, trace)
        file.write("#define %s_magic %d\n" % (self.name, self.magic))
        file.write("#define %s_size %d\n" % (self.name, self.size))
        file.write("#define %s_poly %d\n" % (self.name, self.poly))

# stuff to deal przy arrays of unsigned integers

klasa Array:

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def dump(self, file, trace=0):
        # write data to file, jako a C array
        size = getsize(self.data)
        jeżeli trace:
            print(self.name+":", size*len(self.data), "bytes", file=sys.stderr)
        file.write("static ")
        jeżeli size == 1:
            file.write("unsigned char")
        albo_inaczej size == 2:
            file.write("unsigned short")
        inaczej:
            file.write("unsigned int")
        file.write(" " + self.name + "[] = {\n")
        jeżeli self.data:
            s = "    "
            dla item w self.data:
                i = str(item) + ", "
                jeżeli len(s) + len(i) > 78:
                    file.write(s + "\n")
                    s = "    " + i
                inaczej:
                    s = s + i
            jeżeli s.strip():
                file.write(s + "\n")
        file.write("};\n\n")

def getsize(data):
    # zwróć smallest possible integer size dla the given array
    maxdata = max(data)
    jeżeli maxdata < 256:
        zwróć 1
    albo_inaczej maxdata < 65536:
        zwróć 2
    inaczej:
        zwróć 4

def splitbins(t, trace=0):
    """t, trace=0 -> (t1, t2, shift).  Split a table to save space.

    t jest a sequence of ints.  This function can be useful to save space if
    many of the ints are the same.  t1 oraz t2 are lists of ints, oraz shift
    jest an int, chosen to minimize the combined size of t1 oraz t2 (in C
    code), oraz where dla each i w range(len(t)),
        t[i] == t2[(t1[i >> shift] << shift) + (i & mask)]
    where mask jest a bitmask isolating the last "shift" bits.

    If optional arg trace jest non-zero (default zero), progress info
    jest printed to sys.stderr.  The higher the value, the more info
    you'll get.
    """

    jeżeli trace:
        def dump(t1, t2, shift, bytes):
            print("%d+%d bins at shift %d; %d bytes" % (
                len(t1), len(t2), shift, bytes), file=sys.stderr)
        print("Size of original table:", len(t)*getsize(t), \
                            "bytes", file=sys.stderr)
    n = len(t)-1    # last valid index
    maxshift = 0    # the most we can shift n oraz still have something left
    jeżeli n > 0:
        dopóki n >> 1:
            n >>= 1
            maxshift += 1
    usuń n
    bytes = sys.maxsize  # smallest total size so far
    t = tuple(t)    # so slices can be dict keys
    dla shift w range(maxshift + 1):
        t1 = []
        t2 = []
        size = 2**shift
        bincache = {}
        dla i w range(0, len(t), size):
            bin = t[i:i+size]
            index = bincache.get(bin)
            jeżeli index jest Nic:
                index = len(t2)
                bincache[bin] = index
                t2.extend(bin)
            t1.append(index >> shift)
        # determine memory size
        b = len(t1)*getsize(t1) + len(t2)*getsize(t2)
        jeżeli trace > 1:
            dump(t1, t2, shift, b)
        jeżeli b < bytes:
            best = t1, t2, shift
            bytes = b
    t1, t2, shift = best
    jeżeli trace:
        print("Best:", end=' ', file=sys.stderr)
        dump(t1, t2, shift, bytes)
    jeżeli __debug__:
        # exhaustively verify that the decomposition jest correct
        mask = ~((~0) << shift) # i.e., low-bit mask of shift bits
        dla i w range(len(t)):
            assert t[i] == t2[(t1[i >> shift] << shift) + (i & mask)]
    zwróć best

jeżeli __name__ == "__main__":
    maketables(1)
