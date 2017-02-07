
# Various microbenchmarks comparing unicode oraz byte string performance
# Please keep this file both 2.x oraz 3.x compatible!

zaimportuj timeit
zaimportuj itertools
zaimportuj operator
zaimportuj re
zaimportuj sys
zaimportuj datetime
zaimportuj optparse

VERSION = '2.0'

def p(*args):
    sys.stdout.write(' '.join(str(s) dla s w args) + '\n')

jeżeli sys.version_info >= (3,):
    BYTES = bytes_from_str = lambda x: x.encode('ascii')
    UNICODE = unicode_from_str = lambda x: x
inaczej:
    BYTES = bytes_from_str = lambda x: x
    UNICODE = unicode_from_str = lambda x: x.decode('ascii')

klasa UnsupportedType(TypeError):
    dalej


p('stringbench v%s' % VERSION)
p(sys.version)
p(datetime.datetime.now())

REPEAT = 1
REPEAT = 3
#REPEAT = 7

jeżeli __name__ != "__main__":
    podnieś SystemExit("Must run jako main program")

parser = optparse.OptionParser()
parser.add_option("-R", "--skip-re", dest="skip_re",
                  action="store_true",
                  help="skip regular expression tests")
parser.add_option("-8", "--8-bit", dest="bytes_only",
                  action="store_true",
                  help="only do 8-bit string benchmarks")
parser.add_option("-u", "--unicode", dest="unicode_only",
                  action="store_true",
                  help="only do Unicode string benchmarks")


_RANGE_1000 = list(range(1000))
_RANGE_100 = list(range(100))
_RANGE_10 = list(range(10))

dups = {}
def bench(s, group, repeat_count):
    def blah(f):
        jeżeli f.__name__ w dups:
            podnieś AssertionError("Multiple functions przy same name: %r" %
                                 (f.__name__,))
        dups[f.__name__] = 1
        f.comment = s
        f.is_bench = Prawda
        f.group = group
        f.repeat_count = repeat_count
        zwróć f
    zwróć blah

def uses_re(f):
    f.uses_re = Prawda

####### 'in' comparisons

@bench('"A" w "A"*1000', "early match, single character", 1000)
def in_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    dla x w _RANGE_1000:
        s2 w s1

@bench('"B" w "A"*1000', "no match, single character", 1000)
def in_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    dla x w _RANGE_1000:
        s2 w s1


@bench('"AB" w "AB"*1000', "early match, two characters", 1000)
def in_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    dla x w _RANGE_1000:
        s2 w s1

@bench('"BC" w "AB"*1000', "no match, two characters", 1000)
def in_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    dla x w _RANGE_1000:
        s2 w s1

@bench('"BC" w ("AB"*300+"C")', "late match, two characters", 1000)
def in_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    dla x w _RANGE_1000:
        s2 w s1

@bench('s="ABC"*33; (s+"E") w ((s+"D")*300+s+"E")',
       "late match, 100 characters", 100)
def in_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*300 + m+e
    s2 = m+e
    dla x w _RANGE_100:
        s2 w s1

# Try przy regex
@uses_re
@bench('s="ABC"*33; re.compile(s+"D").search((s+"D")*300+s+"E")',
       "late match, 100 characters", 100)
def re_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*300 + m+e
    s2 = m+e
    pat = re.compile(s2)
    search = pat.search
    dla x w _RANGE_100:
        search(s1)


#### same tests jako 'in' but use 'find'

@bench('("A"*1000).find("A")', "early match, single character", 1000)
def find_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_find = s1.find
    dla x w _RANGE_1000:
        s1_find(s2)

@bench('("A"*1000).find("B")', "no match, single character", 1000)
def find_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_find = s1.find
    dla x w _RANGE_1000:
        s1_find(s2)


@bench('("AB"*1000).find("AB")', "early match, two characters", 1000)
def find_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_find = s1.find
    dla x w _RANGE_1000:
        s1_find(s2)

@bench('("AB"*1000).find("BC")', "no match, two characters", 1000)
def find_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_find = s1.find
    dla x w _RANGE_1000:
        s1_find(s2)

@bench('("AB"*1000).find("CA")', "no match, two characters", 1000)
def find_test_no_match_two_character_bis(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("CA")
    s1_find = s1.find
    dla x w _RANGE_1000:
        s1_find(s2)

@bench('("AB"*300+"C").find("BC")', "late match, two characters", 1000)
def find_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    s1_find = s1.find
    dla x w _RANGE_1000:
        s1_find(s2)

@bench('("AB"*300+"CA").find("CA")', "late match, two characters", 1000)
def find_test_slow_match_two_characters_bis(STR):
    s1 = STR("AB" * 300+"CA")
    s2 = STR("CA")
    s1_find = s1.find
    dla x w _RANGE_1000:
        s1_find(s2)

@bench('s="ABC"*33; ((s+"D")*500+s+"E").find(s+"E")',
       "late match, 100 characters", 100)
def find_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + m+e
    s2 = m+e
    s1_find = s1.find
    dla x w _RANGE_100:
        s1_find(s2)

@bench('s="ABC"*33; ((s+"D")*500+"E"+s).find("E"+s)',
       "late match, 100 characters", 100)
def find_test_slow_match_100_characters_bis(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + e+m
    s2 = e+m
    s1_find = s1.find
    dla x w _RANGE_100:
        s1_find(s2)


#### Same tests dla 'rfind'

@bench('("A"*1000).rfind("A")', "early match, single character", 1000)
def rfind_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_rfind = s1.rfind
    dla x w _RANGE_1000:
        s1_rfind(s2)

@bench('("A"*1000).rfind("B")', "no match, single character", 1000)
def rfind_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_rfind = s1.rfind
    dla x w _RANGE_1000:
        s1_rfind(s2)


@bench('("AB"*1000).rfind("AB")', "early match, two characters", 1000)
def rfind_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_rfind = s1.rfind
    dla x w _RANGE_1000:
        s1_rfind(s2)

@bench('("AB"*1000).rfind("BC")', "no match, two characters", 1000)
def rfind_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_rfind = s1.rfind
    dla x w _RANGE_1000:
        s1_rfind(s2)

@bench('("AB"*1000).rfind("CA")', "no match, two characters", 1000)
def rfind_test_no_match_two_character_bis(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("CA")
    s1_rfind = s1.rfind
    dla x w _RANGE_1000:
        s1_rfind(s2)

@bench('("C"+"AB"*300).rfind("CA")', "late match, two characters", 1000)
def rfind_test_slow_match_two_characters(STR):
    s1 = STR("C" + "AB" * 300)
    s2 = STR("CA")
    s1_rfind = s1.rfind
    dla x w _RANGE_1000:
        s1_rfind(s2)

@bench('("BC"+"AB"*300).rfind("BC")', "late match, two characters", 1000)
def rfind_test_slow_match_two_characters_bis(STR):
    s1 = STR("BC" + "AB" * 300)
    s2 = STR("BC")
    s1_rfind = s1.rfind
    dla x w _RANGE_1000:
        s1_rfind(s2)

@bench('s="ABC"*33; ("E"+s+("D"+s)*500).rfind("E"+s)',
       "late match, 100 characters", 100)
def rfind_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = e+m + (d+m)*500
    s2 = e+m
    s1_rfind = s1.rfind
    dla x w _RANGE_100:
        s1_rfind(s2)

@bench('s="ABC"*33; (s+"E"+("D"+s)*500).rfind(s+"E")',
       "late match, 100 characters", 100)
def rfind_test_slow_match_100_characters_bis(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = m+e + (d+m)*500
    s2 = m+e
    s1_rfind = s1.rfind
    dla x w _RANGE_100:
        s1_rfind(s2)


#### Now przy index.
# Skip the ones which fail because that would include exception overhead.

@bench('("A"*1000).index("A")', "early match, single character", 1000)
def index_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_index = s1.index
    dla x w _RANGE_1000:
        s1_index(s2)

@bench('("AB"*1000).index("AB")', "early match, two characters", 1000)
def index_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_index = s1.index
    dla x w _RANGE_1000:
        s1_index(s2)

@bench('("AB"*300+"C").index("BC")', "late match, two characters", 1000)
def index_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    s1_index = s1.index
    dla x w _RANGE_1000:
        s1_index(s2)

@bench('s="ABC"*33; ((s+"D")*500+s+"E").index(s+"E")',
       "late match, 100 characters", 100)
def index_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + m+e
    s2 = m+e
    s1_index = s1.index
    dla x w _RANGE_100:
        s1_index(s2)


#### Same dla rindex

@bench('("A"*1000).rindex("A")', "early match, single character", 1000)
def rindex_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_rindex = s1.rindex
    dla x w _RANGE_1000:
        s1_rindex(s2)

@bench('("AB"*1000).rindex("AB")', "early match, two characters", 1000)
def rindex_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_rindex = s1.rindex
    dla x w _RANGE_1000:
        s1_rindex(s2)

@bench('("C"+"AB"*300).rindex("CA")', "late match, two characters", 1000)
def rindex_test_slow_match_two_characters(STR):
    s1 = STR("C" + "AB" * 300)
    s2 = STR("CA")
    s1_rindex = s1.rindex
    dla x w _RANGE_1000:
        s1_rindex(s2)

@bench('s="ABC"*33; ("E"+s+("D"+s)*500).rindex("E"+s)',
       "late match, 100 characters", 100)
def rindex_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = e + m + (d+m)*500
    s2 = e + m
    s1_rindex = s1.rindex
    dla x w _RANGE_100:
        s1_rindex(s2)


#### Same dla partition

@bench('("A"*1000).partition("A")', "early match, single character", 1000)
def partition_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_partition = s1.partition
    dla x w _RANGE_1000:
        s1_partition(s2)

@bench('("A"*1000).partition("B")', "no match, single character", 1000)
def partition_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_partition = s1.partition
    dla x w _RANGE_1000:
        s1_partition(s2)


@bench('("AB"*1000).partition("AB")', "early match, two characters", 1000)
def partition_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_partition = s1.partition
    dla x w _RANGE_1000:
        s1_partition(s2)

@bench('("AB"*1000).partition("BC")', "no match, two characters", 1000)
def partition_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_partition = s1.partition
    dla x w _RANGE_1000:
        s1_partition(s2)

@bench('("AB"*300+"C").partition("BC")', "late match, two characters", 1000)
def partition_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    s1_partition = s1.partition
    dla x w _RANGE_1000:
        s1_partition(s2)

@bench('s="ABC"*33; ((s+"D")*500+s+"E").partition(s+"E")',
       "late match, 100 characters", 100)
def partition_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + m+e
    s2 = m+e
    s1_partition = s1.partition
    dla x w _RANGE_100:
        s1_partition(s2)


#### Same dla rpartition

@bench('("A"*1000).rpartition("A")', "early match, single character", 1000)
def rpartition_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_rpartition = s1.rpartition
    dla x w _RANGE_1000:
        s1_rpartition(s2)

@bench('("A"*1000).rpartition("B")', "no match, single character", 1000)
def rpartition_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_rpartition = s1.rpartition
    dla x w _RANGE_1000:
        s1_rpartition(s2)


@bench('("AB"*1000).rpartition("AB")', "early match, two characters", 1000)
def rpartition_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_rpartition = s1.rpartition
    dla x w _RANGE_1000:
        s1_rpartition(s2)

@bench('("AB"*1000).rpartition("BC")', "no match, two characters", 1000)
def rpartition_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_rpartition = s1.rpartition
    dla x w _RANGE_1000:
        s1_rpartition(s2)

@bench('("C"+"AB"*300).rpartition("CA")', "late match, two characters", 1000)
def rpartition_test_slow_match_two_characters(STR):
    s1 = STR("C" + "AB" * 300)
    s2 = STR("CA")
    s1_rpartition = s1.rpartition
    dla x w _RANGE_1000:
        s1_rpartition(s2)

@bench('s="ABC"*33; ("E"+s+("D"+s)*500).rpartition("E"+s)',
       "late match, 100 characters", 100)
def rpartition_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = e + m + (d+m)*500
    s2 = e + m
    s1_rpartition = s1.rpartition
    dla x w _RANGE_100:
        s1_rpartition(s2)


#### Same dla split(s, 1)

@bench('("A"*1000).split("A", 1)', "early match, single character", 1000)
def split_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_split = s1.split
    dla x w _RANGE_1000:
        s1_split(s2, 1)

@bench('("A"*1000).split("B", 1)', "no match, single character", 1000)
def split_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_split = s1.split
    dla x w _RANGE_1000:
        s1_split(s2, 1)


@bench('("AB"*1000).split("AB", 1)', "early match, two characters", 1000)
def split_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_split = s1.split
    dla x w _RANGE_1000:
        s1_split(s2, 1)

@bench('("AB"*1000).split("BC", 1)', "no match, two characters", 1000)
def split_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_split = s1.split
    dla x w _RANGE_1000:
        s1_split(s2, 1)

@bench('("AB"*300+"C").split("BC", 1)', "late match, two characters", 1000)
def split_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    s1_split = s1.split
    dla x w _RANGE_1000:
        s1_split(s2, 1)

@bench('s="ABC"*33; ((s+"D")*500+s+"E").split(s+"E", 1)',
       "late match, 100 characters", 100)
def split_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + m+e
    s2 = m+e
    s1_split = s1.split
    dla x w _RANGE_100:
        s1_split(s2, 1)


#### Same dla rsplit(s, 1)

@bench('("A"*1000).rsplit("A", 1)', "early match, single character", 1000)
def rsplit_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_rsplit = s1.rsplit
    dla x w _RANGE_1000:
        s1_rsplit(s2, 1)

@bench('("A"*1000).rsplit("B", 1)', "no match, single character", 1000)
def rsplit_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_rsplit = s1.rsplit
    dla x w _RANGE_1000:
        s1_rsplit(s2, 1)


@bench('("AB"*1000).rsplit("AB", 1)', "early match, two characters", 1000)
def rsplit_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_rsplit = s1.rsplit
    dla x w _RANGE_1000:
        s1_rsplit(s2, 1)

@bench('("AB"*1000).rsplit("BC", 1)', "no match, two characters", 1000)
def rsplit_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_rsplit = s1.rsplit
    dla x w _RANGE_1000:
        s1_rsplit(s2, 1)

@bench('("C"+"AB"*300).rsplit("CA", 1)', "late match, two characters", 1000)
def rsplit_test_slow_match_two_characters(STR):
    s1 = STR("C" + "AB" * 300)
    s2 = STR("CA")
    s1_rsplit = s1.rsplit
    dla x w _RANGE_1000:
        s1_rsplit(s2, 1)

@bench('s="ABC"*33; ("E"+s+("D"+s)*500).rsplit("E"+s, 1)',
       "late match, 100 characters", 100)
def rsplit_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = e + m + (d+m)*500
    s2 = e + m
    s1_rsplit = s1.rsplit
    dla x w _RANGE_100:
        s1_rsplit(s2, 1)


#### Benchmark the operator-based methods

@bench('"A"*10', "repeat 1 character 10 times", 1000)
def repeat_single_10_times(STR):
    s = STR("A")
    dla x w _RANGE_1000:
        s * 10

@bench('"A"*1000', "repeat 1 character 1000 times", 1000)
def repeat_single_1000_times(STR):
    s = STR("A")
    dla x w _RANGE_1000:
        s * 1000

@bench('"ABCDE"*10', "repeat 5 characters 10 times", 1000)
def repeat_5_10_times(STR):
    s = STR("ABCDE")
    dla x w _RANGE_1000:
        s * 10

@bench('"ABCDE"*1000', "repeat 5 characters 1000 times", 1000)
def repeat_5_1000_times(STR):
    s = STR("ABCDE")
    dla x w _RANGE_1000:
        s * 1000

# + dla concat

@bench('"Andrew"+"Dalke"', "concat two strings", 1000)
def concat_two_strings(STR):
    s1 = STR("Andrew")
    s2 = STR("Dalke")
    dla x w _RANGE_1000:
        s1+s2

@bench('s1+s2+s3+s4+...+s20', "concat 20 strings of words length 4 to 15",
       1000)
def concat_many_strings(STR):
    s1=STR('TIXSGYNREDCVBHJ')
    s2=STR('PUMTLXBZVDO')
    s3=STR('FVZNJ')
    s4=STR('OGDXUW')
    s5=STR('WEIMRNCOYVGHKB')
    s6=STR('FCQTNMXPUZH')
    s7=STR('TICZJYRLBNVUEAK')
    s8=STR('REYB')
    s9=STR('PWUOQ')
    s10=STR('EQHCMKBS')
    s11=STR('AEVDFOH')
    s12=STR('IFHVD')
    s13=STR('JGTCNLXWOHQ')
    s14=STR('ITSKEPYLROZAWXF')
    s15=STR('THEK')
    s16=STR('GHPZFBUYCKMNJIT')
    s17=STR('JMUZ')
    s18=STR('WLZQMTB')
    s19=STR('KPADCBW')
    s20=STR('TNJHZQAGBU')
    dla x w _RANGE_1000:
        (s1 + s2+ s3+ s4+ s5+ s6+ s7+ s8+ s9+s10+
         s11+s12+s13+s14+s15+s16+s17+s18+s19+s20)


#### Benchmark join

def get_bytes_uzyskajing_seq(STR, arg):
    jeżeli STR jest BYTES oraz sys.version_info >= (3,):
        podnieś UnsupportedType
    zwróć STR(arg)

@bench('"A".join("")',
       "join empty string, przy 1 character sep", 100)
def join_empty_single(STR):
    sep = STR("A")
    s2 = get_bytes_uzyskajing_seq(STR, "")
    sep_join = sep.join
    dla x w _RANGE_100:
        sep_join(s2)

@bench('"ABCDE".join("")',
       "join empty string, przy 5 character sep", 100)
def join_empty_5(STR):
    sep = STR("ABCDE")
    s2 = get_bytes_uzyskajing_seq(STR, "")
    sep_join = sep.join
    dla x w _RANGE_100:
        sep_join(s2)

@bench('"A".join("ABC..Z")',
       "join string przy 26 characters, przy 1 character sep", 1000)
def join_alphabet_single(STR):
    sep = STR("A")
    s2 = get_bytes_uzyskajing_seq(STR, "ABCDEFGHIJKLMnOPQRSTUVWXYZ")
    sep_join = sep.join
    dla x w _RANGE_1000:
        sep_join(s2)

@bench('"ABCDE".join("ABC..Z")',
       "join string przy 26 characters, przy 5 character sep", 1000)
def join_alphabet_5(STR):
    sep = STR("ABCDE")
    s2 = get_bytes_uzyskajing_seq(STR, "ABCDEFGHIJKLMnOPQRSTUVWXYZ")
    sep_join = sep.join
    dla x w _RANGE_1000:
        sep_join(s2)

@bench('"A".join(list("ABC..Z"))',
       "join list of 26 characters, przy 1 character sep", 1000)
def join_alphabet_list_single(STR):
    sep = STR("A")
    s2 = [STR(x) dla x w "ABCDEFGHIJKLMnOPQRSTUVWXYZ"]
    sep_join = sep.join
    dla x w _RANGE_1000:
        sep_join(s2)

@bench('"ABCDE".join(list("ABC..Z"))',
       "join list of 26 characters, przy 5 character sep", 1000)
def join_alphabet_list_five(STR):
    sep = STR("ABCDE")
    s2 = [STR(x) dla x w "ABCDEFGHIJKLMnOPQRSTUVWXYZ"]
    sep_join = sep.join
    dla x w _RANGE_1000:
        sep_join(s2)

@bench('"A".join(["Bob"]*100))',
       "join list of 100 words, przy 1 character sep", 1000)
def join_100_words_single(STR):
    sep = STR("A")
    s2 = [STR("Bob")]*100
    sep_join = sep.join
    dla x w _RANGE_1000:
        sep_join(s2)

@bench('"ABCDE".join(["Bob"]*100))',
       "join list of 100 words, przy 5 character sep", 1000)
def join_100_words_5(STR):
    sep = STR("ABCDE")
    s2 = [STR("Bob")]*100
    sep_join = sep.join
    dla x w _RANGE_1000:
        sep_join(s2)

#### split tests

@bench('("Here are some words. "*2).split()', "split whitespace (small)", 1000)
def whitespace_split(STR):
    s = STR("Here are some words. "*2)
    s_split = s.split
    dla x w _RANGE_1000:
        s_split()

@bench('("Here are some words. "*2).rsplit()', "split whitespace (small)", 1000)
def whitespace_rsplit(STR):
    s = STR("Here are some words. "*2)
    s_rsplit = s.rsplit
    dla x w _RANGE_1000:
        s_rsplit()

@bench('("Here are some words. "*2).split(Nic, 1)',
       "split 1 whitespace", 1000)
def whitespace_split_1(STR):
    s = STR("Here are some words. "*2)
    s_split = s.split
    N = Nic
    dla x w _RANGE_1000:
        s_split(N, 1)

@bench('("Here are some words. "*2).rsplit(Nic, 1)',
       "split 1 whitespace", 1000)
def whitespace_rsplit_1(STR):
    s = STR("Here are some words. "*2)
    s_rsplit = s.rsplit
    N = Nic
    dla x w _RANGE_1000:
        s_rsplit(N, 1)

@bench('("Here are some words. "*2).partition(" ")',
       "split 1 whitespace", 1000)
def whitespace_partition(STR):
    sep = STR(" ")
    s = STR("Here are some words. "*2)
    s_partition = s.partition
    dla x w _RANGE_1000:
        s_partition(sep)

@bench('("Here are some words. "*2).rpartition(" ")',
       "split 1 whitespace", 1000)
def whitespace_rpartition(STR):
    sep = STR(" ")
    s = STR("Here are some words. "*2)
    s_rpartition = s.rpartition
    dla x w _RANGE_1000:
        s_rpartition(sep)

human_text = """\
Python jest a dynamic object-oriented programming language that can be
used dla many kinds of software development. It offers strong support
dla integration przy other languages oraz tools, comes przy extensive
standard libraries, oraz can be learned w a few days. Many Python
programmers report substantial productivity gains oraz feel the language
encourages the development of higher quality, more maintainable code.

Python runs on Windows, Linux/Unix, Mac OS X, Amiga, Palm
Handhelds, oraz Nokia mobile phones. Python has also been ported to the
Java oraz .NET virtual machines.

Python jest distributed under an OSI-approved open source license that
makes it free to use, even dla commercial products.
"""*25
human_text_bytes = bytes_from_str(human_text)
human_text_unicode = unicode_from_str(human_text)
def _get_human_text(STR):
    jeżeli STR jest UNICODE:
        zwróć human_text_unicode
    jeżeli STR jest BYTES:
        zwróć human_text_bytes
    podnieś AssertionError

@bench('human_text.split()', "split whitespace (huge)", 10)
def whitespace_split_huge(STR):
    s = _get_human_text(STR)
    s_split = s.split
    dla x w _RANGE_10:
        s_split()

@bench('human_text.rsplit()', "split whitespace (huge)", 10)
def whitespace_rsplit_huge(STR):
    s = _get_human_text(STR)
    s_rsplit = s.rsplit
    dla x w _RANGE_10:
        s_rsplit()



@bench('"this\\nis\\na\\ntest\\n".split("\\n")', "split newlines", 1000)
def newlines_split(STR):
    s = STR("this\nis\na\ntest\n")
    s_split = s.split
    nl = STR("\n")
    dla x w _RANGE_1000:
        s_split(nl)


@bench('"this\\nis\\na\\ntest\\n".rsplit("\\n")', "split newlines", 1000)
def newlines_rsplit(STR):
    s = STR("this\nis\na\ntest\n")
    s_rsplit = s.rsplit
    nl = STR("\n")
    dla x w _RANGE_1000:
        s_rsplit(nl)

@bench('"this\\nis\\na\\ntest\\n".splitlines()', "split newlines", 1000)
def newlines_splitlines(STR):
    s = STR("this\nis\na\ntest\n")
    s_splitlines = s.splitlines
    dla x w _RANGE_1000:
        s_splitlines()

## split text przy 2000 newlines

def _make_2000_lines():
    zaimportuj random
    r = random.Random(100)
    chars = list(map(chr, range(32, 128)))
    i = 0
    dopóki i < len(chars):
        chars[i] = " "
        i += r.randrange(9)
    s = "".join(chars)
    s = s*4
    words = []
    dla i w range(2000):
        start = r.randrange(96)
        n = r.randint(5, 65)
        words.append(s[start:start+n])
    zwróć "\n".join(words)+"\n"

_text_with_2000_lines = _make_2000_lines()
_text_with_2000_lines_bytes = bytes_from_str(_text_with_2000_lines)
_text_with_2000_lines_unicode = unicode_from_str(_text_with_2000_lines)
def _get_2000_lines(STR):
    jeżeli STR jest UNICODE:
        zwróć _text_with_2000_lines_unicode
    jeżeli STR jest BYTES:
        zwróć _text_with_2000_lines_bytes
    podnieś AssertionError


@bench('"...text...".split("\\n")', "split 2000 newlines", 10)
def newlines_split_2000(STR):
    s = _get_2000_lines(STR)
    s_split = s.split
    nl = STR("\n")
    dla x w _RANGE_10:
        s_split(nl)

@bench('"...text...".rsplit("\\n")', "split 2000 newlines", 10)
def newlines_rsplit_2000(STR):
    s = _get_2000_lines(STR)
    s_rsplit = s.rsplit
    nl = STR("\n")
    dla x w _RANGE_10:
        s_rsplit(nl)

@bench('"...text...".splitlines()', "split 2000 newlines", 10)
def newlines_splitlines_2000(STR):
    s = _get_2000_lines(STR)
    s_splitlines = s.splitlines
    dla x w _RANGE_10:
        s_splitlines()


## split text on "--" characters
@bench(
    '"this--is--a--test--of--the--emergency--broadcast--system".split("--")',
    "split on multicharacter separator (small)", 1000)
def split_multichar_sep_small(STR):
    s = STR("this--is--a--test--of--the--emergency--broadcast--system")
    s_split = s.split
    pat = STR("--")
    dla x w _RANGE_1000:
        s_split(pat)
@bench(
    '"this--is--a--test--of--the--emergency--broadcast--system".rsplit("--")',
    "split on multicharacter separator (small)", 1000)
def rsplit_multichar_sep_small(STR):
    s = STR("this--is--a--test--of--the--emergency--broadcast--system")
    s_rsplit = s.rsplit
    pat = STR("--")
    dla x w _RANGE_1000:
        s_rsplit(pat)

## split dna text on "ACTAT" characters
@bench('dna.split("ACTAT")',
       "split on multicharacter separator (dna)", 10)
def split_multichar_sep_dna(STR):
    s = _get_dna(STR)
    s_split = s.split
    pat = STR("ACTAT")
    dla x w _RANGE_10:
        s_split(pat)

@bench('dna.rsplit("ACTAT")',
       "split on multicharacter separator (dna)", 10)
def rsplit_multichar_sep_dna(STR):
    s = _get_dna(STR)
    s_rsplit = s.rsplit
    pat = STR("ACTAT")
    dla x w _RANGE_10:
        s_rsplit(pat)



## split przy limits

GFF3_example = "\t".join([
    "I", "Genomic_canonical", "region", "357208", "396183", ".", "+", ".",
    "ID=Sequence:R119;note=Clone R119%3B Genbank AF063007;Name=R119"])

@bench('GFF3_example.split("\\t")', "tab split", 1000)
def tab_split_no_limit(STR):
    sep = STR("\t")
    s = STR(GFF3_example)
    s_split = s.split
    dla x w _RANGE_1000:
        s_split(sep)

@bench('GFF3_example.split("\\t", 8)', "tab split", 1000)
def tab_split_limit(STR):
    sep = STR("\t")
    s = STR(GFF3_example)
    s_split = s.split
    dla x w _RANGE_1000:
        s_split(sep, 8)

@bench('GFF3_example.rsplit("\\t")', "tab split", 1000)
def tab_rsplit_no_limit(STR):
    sep = STR("\t")
    s = STR(GFF3_example)
    s_rsplit = s.rsplit
    dla x w _RANGE_1000:
        s_rsplit(sep)

@bench('GFF3_example.rsplit("\\t", 8)', "tab split", 1000)
def tab_rsplit_limit(STR):
    sep = STR("\t")
    s = STR(GFF3_example)
    s_rsplit = s.rsplit
    dla x w _RANGE_1000:
        s_rsplit(sep, 8)

#### Count characters

@bench('...text.with.2000.newlines.count("\\n")',
       "count newlines", 10)
def count_newlines(STR):
    s = _get_2000_lines(STR)
    s_count = s.count
    nl = STR("\n")
    dla x w _RANGE_10:
        s_count(nl)

# Orchid sequences concatenated, z Biopython
_dna = """
CGTAACAAGGTTTCCGTAGGTGAACCTGCGGAAGGATCATTGTTGAGATCACATAATAATTGATCGGGTT
AATCTGGAGGATCTGTTTACTTTGGTCACCCATGAGCATTTGCTGTTGAAGTGACCTAGAATTGCCATCG
AGCCTCCTTGGGAGCTTTCTTGTTGGCGAGATCTAAACCCTTGCCCGGCGCAGTTTTGCTCCAAGTCGTT
TGACACATAATTGGTGAAGGGGGTGGCATCCTTCCCTGACCCTCCCCCAACTATTTTTTTAACAACTCTC
AGCAACGGAGACTCAGTCTTCGGCAAATGCGATAAATGGTGTGAATTGCAGAATCCCGTGCACCATCGAG
TCTTTGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCACGCCTGCCTGGGCATTGCGAGTCATAT
CTCTCCCTTAACGAGGCTGTCCATACATACTGTTCAGCCGGTGCGGATGTGAGTTTGGCCCCTTGTTCTT
TGGTACGGGGGGTCTAAGAGCTGCATGGGCTTTTGATGGTCCTAAATACGGCAAGAGGTGGACGAACTAT
GCTACAACAAAATTGTTGTGCAGAGGCCCCGGGTTGTCGTATTAGATGGGCCACCGTAATCTGAAGACCC
TTTTGAACCCCATTGGAGGCCCATCAACCCATGATCAGTTGATGGCCATTTGGTTGCGACCCCAGGTCAG
GTGAGCAACAGCTGTCGTAACAAGGTTTCCGTAGGGTGAACTGCGGAAGGATCATTGTTGAGATCACATA
ATAATTGATCGAGTTAATCTGGAGGATCTGTTTACTTGGGTCACCCATGGGCATTTGCTGTTGAAGTGAC
CTAGATTTGCCATCGAGCCTCCTTGGGAGCATCCTTGTTGGCGATATCTAAACCCTCAATTTTTCCCCCA
ATCAAATTACACAAAATTGGTGGAGGGGGTGGCATTCTTCCCTTACCCTCCCCCAAATATTTTTTTAACA
ACTCTCAGCAACGGATATCTCAGCTCTTGCATCGATGAAGAACCCACCGAAATGCGATAAATGGTGTGAA
TTGCAGAATCCCGTGAACCATCGAGTCTTTGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCACG
CCTGCCTGGGCATTGCGAGTCATATCTCTCCCTTAACGAGGCTGTCCATACATACTGTTCAGCCGGTGCG
GATGTGAGTTTGGCCCCTTGTTCTTTGGTACGGGGGGTCTAAGAGATGCATGGGCTTTTGATGGTCCTAA
ATACGGCAAGAGGTGGACGAACTATGCTACAACAAAATTGTTGTGCAAAGGCCCCGGGTTGTCGTATAAG
ATGGGCCACCGATATCTGAAGACCCTTTTGGACCCCATTGGAGCCCATCAACCCATGTCAGTTGATGGCC
ATTCGTAACAAGGTTTCCGTAGGTGAACCTGCGGAAGGATCATTGTTGAGATCACATAATAATTGATCGA
GTTAATCTGGAGGATCTGTTTACTTGGGTCACCCATGGGCATTTGCTGTTGAAGTGACCTAGATTTGCCA
TCGAGCCTCCTTGGGAGCTTTCTTGTTGGCGATATCTAAACCCTTGCCCGGCAGAGTTTTGGGAATCCCG
TGAACCATCGAGTCTTTGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCACGCCTGCCTGGGCAT
TGCGAGTCATATCTCTCCCTTAACGAGGCTGTCCATACACACCTGTTCAGCCGGTGCGGATGTGAGTTTG
GCCCCTTGTTCTTTGGTACGGGGGGTCTAAGAGCTGCATGGGCTTTTGATGGTCCTAAATACGGCAAGAG
GTGGACGAACTATGCTACAACAAAATTGTTGTGCAAAGGCCCCGGGTTGTCGTATTAGATGGGCCACCAT
AATCTGAAGACCCTTTTGAACCCCATTGGAGGCCCATCAACCCATGATCAGTTGATGGCCATTTGGTTGC
GACCCAGTCAGGTGAGGGTAGGTGAACCTGCGGAAGGATCATTGTTGAGATCACATAATAATTGATCGAG
TTAATCTGGAGGATCTGTTTACTTTGGTCACCCATGGGCATTTGCTGTTGAAGTGACCTAGATTTGCCAT
CGAGCCTCCTTGGGAGCTTTCTTGTTGGCGAGATCTAAACCCTTGCCCGGCGGAGTTTGGCGCCAAGTCA
TATGACACATAATTGGTGAAGGGGGTGGCATCCTGCCCTGACCCTCCCCAAATTATTTTTTTAACAACTC
TCAGCAACGGATATCTCGGCTCTTGCATCGATGAAGAACGCAGCGAAATGCGATAAATGGTGTGAATTGC
AGAATCCCGTGAACCATCGAGTCTTTGGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCACGCCT
GCCTGGGCATTGGGAATCATATCTCTCCCCTAACGAGGCTATCCAAACATACTGTTCATCCGGTGCGGAT
GTGAGTTTGGCCCCTTGTTCTTTGGTACCGGGGGTCTAAGAGCTGCATGGGCATTTGATGGTCCTCAAAA
CGGCAAGAGGTGGACGAACTATGCCACAACAAAATTGTTGTCCCAAGGCCCCGGGTTGTCGTATTAGATG
GGCCACCGTAACCTGAAGACCCTTTTGAACCCCATTGGAGGCCCATCAACCCATGATCAGTTGATGACCA
TTTGTTGCGACCCCAGTCAGCTGAGCAACCCGCTGAGTGGAAGGTCATTGCCGATATCACATAATAATTG
ATCGAGTTAATCTGGAGGATCTGTTTACTTGGTCACCCATGAGCATTTGCTGTTGAAGTGACCTAGATTT
GCCATCGAGCCTCCTTGGGAGTTTTCTTGTTGGCGAGATCTAAACCCTTGCCCGGCGGAGTTGTGCGCCA
AGTCATATGACACATAATTGGTGAAGGGGGTGGCATCCTGCCCTGACCCTCCCCAAATTATTTTTTTAAC
AACTCTCAGCAACGGATATCTCGGCTCTTGCATCGATGAAGAACGCAGCGAAATGCGATAAATGGTGTGA
ATTGCAGAATCCCGTGAACCATCGAGTCTTTGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCAC
GCCTGCCTGGGCATTGCGAGTCATATCTCTCCCTTAACGAGGCTGTCCATACATACTGTTCATCCGGTGC
GGATGTGAGTTTGGCCCCTTGTTCTTTGGTACGGGGGGTCTAAGAGCTGCATGGGCATTTGATGGTCCTC
AAAACGGCAAGAGGTGGACGAACTATGCTACAACCAAATTGTTGTCCCAAGGCCCCGGGTTGTCGTATTA
GATGGGCCACCGTAACCTGAAGACCCTTTTGAACCCCATTGGAGGCCCATCAACCCATGATCAGTTGATG
ACCATGTGTTGCGACCCCAGTCAGCTGAGCAACGCGCTGAGCGTAACAAGGTTTCCGTAGGTGGACCTCC
GGGAGGATCATTGTTGAGATCACATAATAATTGATCGAGGTAATCTGGAGGATCTGCATATTTTGGTCAC
"""
_dna = "".join(_dna.splitlines())
_dna = _dna * 25
_dna_bytes = bytes_from_str(_dna)
_dna_unicode = unicode_from_str(_dna)

def _get_dna(STR):
    jeżeli STR jest UNICODE:
        zwróć _dna_unicode
    jeżeli STR jest BYTES:
        zwróć _dna_bytes
    podnieś AssertionError

@bench('dna.count("AACT")', "count AACT substrings w DNA example", 10)
def count_aact(STR):
    seq = _get_dna(STR)
    seq_count = seq.count
    needle = STR("AACT")
    dla x w _RANGE_10:
        seq_count(needle)

##### startsprzy oraz endswith

@bench('"Andrew".startswith("A")', 'startsprzy single character', 1000)
def startswith_single(STR):
    s1 = STR("Andrew")
    s2 = STR("A")
    s1_startswith = s1.startswith
    dla x w _RANGE_1000:
        s1_startswith(s2)

@bench('"Andrew".startswith("Andrew")', 'startsprzy multiple characters',
       1000)
def startswith_multiple(STR):
    s1 = STR("Andrew")
    s2 = STR("Andrew")
    s1_startswith = s1.startswith
    dla x w _RANGE_1000:
        s1_startswith(s2)

@bench('"Andrew".startswith("Anders")',
       'startsprzy multiple characters - not!', 1000)
def startswith_multiple_not(STR):
    s1 = STR("Andrew")
    s2 = STR("Anders")
    s1_startswith = s1.startswith
    dla x w _RANGE_1000:
        s1_startswith(s2)


# endswith

@bench('"Andrew".endswith("w")', 'endsprzy single character', 1000)
def endswith_single(STR):
    s1 = STR("Andrew")
    s2 = STR("w")
    s1_endswith = s1.endswith
    dla x w _RANGE_1000:
        s1_endswith(s2)

@bench('"Andrew".endswith("Andrew")', 'endsprzy multiple characters', 1000)
def endswith_multiple(STR):
    s1 = STR("Andrew")
    s2 = STR("Andrew")
    s1_endswith = s1.endswith
    dla x w _RANGE_1000:
        s1_endswith(s2)

@bench('"Andrew".endswith("Anders")',
       'endsprzy multiple characters - not!', 1000)
def endswith_multiple_not(STR):
    s1 = STR("Andrew")
    s2 = STR("Anders")
    s1_endswith = s1.endswith
    dla x w _RANGE_1000:
        s1_endswith(s2)

#### Strip

@bench('"Hello!\\n".strip()', 'strip terminal newline', 1000)
def terminal_newline_strip_right(STR):
    s = STR("Hello!\n")
    s_strip = s.strip
    dla x w _RANGE_1000:
        s_strip()

@bench('"Hello!\\n".rstrip()', 'strip terminal newline', 1000)
def terminal_newline_rstrip(STR):
    s = STR("Hello!\n")
    s_rstrip = s.rstrip
    dla x w _RANGE_1000:
        s_rstrip()

@bench('"\\nHello!".strip()', 'strip terminal newline', 1000)
def terminal_newline_strip_left(STR):
    s = STR("\nHello!")
    s_strip = s.strip
    dla x w _RANGE_1000:
        s_strip()

@bench('"\\nHello!\\n".strip()', 'strip terminal newline', 1000)
def terminal_newline_strip_both(STR):
    s = STR("\nHello!\n")
    s_strip = s.strip
    dla x w _RANGE_1000:
        s_strip()

@bench('"\\nHello!".rstrip()', 'strip terminal newline', 1000)
def terminal_newline_lstrip(STR):
    s = STR("\nHello!")
    s_lstrip = s.lstrip
    dla x w _RANGE_1000:
        s_lstrip()

@bench('s="Hello!\\n"; s[:-1] jeżeli s[-1]=="\\n" inaczej s',
       'strip terminal newline', 1000)
def terminal_newline_if_inaczej(STR):
    s = STR("Hello!\n")
    NL = STR("\n")
    dla x w _RANGE_1000:
        s[:-1] jeżeli (s[-1] == NL) inaczej s


# Strip multiple spaces albo tabs

@bench('"Hello\\t   \\t".strip()', 'strip terminal spaces oraz tabs', 1000)
def terminal_space_strip(STR):
    s = STR("Hello\t   \t!")
    s_strip = s.strip
    dla x w _RANGE_1000:
        s_strip()

@bench('"Hello\\t   \\t".rstrip()', 'strip terminal spaces oraz tabs', 1000)
def terminal_space_rstrip(STR):
    s = STR("Hello!\t   \t")
    s_rstrip = s.rstrip
    dla x w _RANGE_1000:
        s_rstrip()

@bench('"\\t   \\tHello".rstrip()', 'strip terminal spaces oraz tabs', 1000)
def terminal_space_lstrip(STR):
    s = STR("\t   \tHello!")
    s_lstrip = s.lstrip
    dla x w _RANGE_1000:
        s_lstrip()


#### replace
@bench('"This jest a test".replace(" ", "\\t")', 'replace single character',
       1000)
def replace_single_character(STR):
    s = STR("This jest a test!")
    from_str = STR(" ")
    to_str = STR("\t")
    s_replace = s.replace
    dla x w _RANGE_1000:
        s_replace(from_str, to_str)

@uses_re
@bench('re.sub(" ", "\\t", "This jest a test"', 'replace single character',
       1000)
def replace_single_character_re(STR):
    s = STR("This jest a test!")
    pat = re.compile(STR(" "))
    to_str = STR("\t")
    pat_sub = pat.sub
    dla x w _RANGE_1000:
        pat_sub(to_str, s)

@bench('"...text.with.2000.lines...replace("\\n", " ")',
       'replace single character, big string', 10)
def replace_single_character_big(STR):
    s = _get_2000_lines(STR)
    from_str = STR("\n")
    to_str = STR(" ")
    s_replace = s.replace
    dla x w _RANGE_10:
        s_replace(from_str, to_str)

@uses_re
@bench('re.sub("\\n", " ", "...text.with.2000.lines...")',
       'replace single character, big string', 10)
def replace_single_character_big_re(STR):
    s = _get_2000_lines(STR)
    pat = re.compile(STR("\n"))
    to_str = STR(" ")
    pat_sub = pat.sub
    dla x w _RANGE_10:
        pat_sub(to_str, s)


@bench('dna.replace("ATC", "ATT")',
       'replace multiple characters, dna', 10)
def replace_multiple_characters_dna(STR):
    seq = _get_dna(STR)
    from_str = STR("ATC")
    to_str = STR("ATT")
    seq_replace = seq.replace
    dla x w _RANGE_10:
        seq_replace(from_str, to_str)

# This increases the character count
@bench('"...text.with.2000.newlines...replace("\\n", "\\r\\n")',
       'replace oraz expand multiple characters, big string', 10)
def replace_multiple_character_big(STR):
    s = _get_2000_lines(STR)
    from_str = STR("\n")
    to_str = STR("\r\n")
    s_replace = s.replace
    dla x w _RANGE_10:
        s_replace(from_str, to_str)


# This decreases the character count
@bench('"When shall we three meet again?".replace("ee", "")',
       'replace/remove multiple characters', 1000)
def replace_multiple_character_remove(STR):
    s = STR("When shall we three meet again?")
    from_str = STR("ee")
    to_str = STR("")
    s_replace = s.replace
    dla x w _RANGE_1000:
        s_replace(from_str, to_str)


big_s = "A" + ("Z"*128*1024)
big_s_bytes = bytes_from_str(big_s)
big_s_unicode = unicode_from_str(big_s)
def _get_big_s(STR):
    jeżeli STR jest UNICODE: zwróć big_s_unicode
    jeżeli STR jest BYTES: zwróć big_s_bytes
    podnieś AssertionError

# The older replace implementation counted all matches w
# the string even when it only needed to make one replacement.
@bench('("A" + ("Z"*128*1024)).replace("A", "BB", 1)',
       'quick replace single character match', 10)
def quick_replace_single_match(STR):
    s = _get_big_s(STR)
    from_str = STR("A")
    to_str = STR("BB")
    s_replace = s.replace
    dla x w _RANGE_10:
        s_replace(from_str, to_str, 1)

@bench('("A" + ("Z"*128*1024)).replace("AZZ", "BBZZ", 1)',
       'quick replace multiple character match', 10)
def quick_replace_multiple_match(STR):
    s = _get_big_s(STR)
    from_str = STR("AZZ")
    to_str = STR("BBZZ")
    s_replace = s.replace
    dla x w _RANGE_10:
        s_replace(from_str, to_str, 1)


####

# CCP does a lot of this, dla internationalisation of ingame messages.
_format = "The %(thing)s jest %(place)s the %(location)s."
_format_dict = { "thing":"THING", "place":"PLACE", "location":"LOCATION", }
_format_bytes = bytes_from_str(_format)
_format_unicode = unicode_from_str(_format)
_format_dict_bytes = dict((bytes_from_str(k), bytes_from_str(v)) dla (k,v) w _format_dict.items())
_format_dict_unicode = dict((unicode_from_str(k), unicode_from_str(v)) dla (k,v) w _format_dict.items())

def _get_format(STR):
    jeżeli STR jest UNICODE:
        zwróć _format_unicode
    jeżeli STR jest BYTES:
        jeżeli sys.version_info >= (3,):
            podnieś UnsupportedType
        zwróć _format_bytes
    podnieś AssertionError

def _get_format_dict(STR):
    jeżeli STR jest UNICODE:
        zwróć _format_dict_unicode
    jeżeli STR jest BYTES:
        jeżeli sys.version_info >= (3,):
            podnieś UnsupportedType
        zwróć _format_dict_bytes
    podnieś AssertionError

# Formatting.
@bench('"The %(k1)s jest %(k2)s the %(k3)s."%{"k1":"x","k2":"y","k3":"z",}',
       'formatting a string type przy a dict', 1000)
def format_with_dict(STR):
    s = _get_format(STR)
    d = _get_format_dict(STR)
    dla x w _RANGE_1000:
        s % d


#### Upper- oraz lower- case conversion

@bench('("Where w the world jest Carmen San Deigo?"*10).lower()',
       "case conversion -- rare", 1000)
def lower_conversion_rare(STR):
    s = STR("Where w the world jest Carmen San Deigo?"*10)
    s_lower = s.lower
    dla x w _RANGE_1000:
        s_lower()

@bench('("WHERE IN THE WORLD IS CARMEN SAN DEIGO?"*10).lower()',
       "case conversion -- dense", 1000)
def lower_conversion_dense(STR):
    s = STR("WHERE IN THE WORLD IS CARMEN SAN DEIGO?"*10)
    s_lower = s.lower
    dla x w _RANGE_1000:
        s_lower()


@bench('("wHERE IN THE WORLD IS cARMEN sAN dEIGO?"*10).upper()',
       "case conversion -- rare", 1000)
def upper_conversion_rare(STR):
    s = STR("Where w the world jest Carmen San Deigo?"*10)
    s_upper = s.upper
    dla x w _RANGE_1000:
        s_upper()

@bench('("where w the world jest carmen san deigo?"*10).upper()',
       "case conversion -- dense", 1000)
def upper_conversion_dense(STR):
    s = STR("where w the world jest carmen san deigo?"*10)
    s_upper = s.upper
    dla x w _RANGE_1000:
        s_upper()


# end of benchmarks

#################

klasa BenchTimer(timeit.Timer):
    def best(self, repeat=1):
        dla i w range(1, 10):
            number = 10**i
            x = self.timeit(number)
            jeżeli x > 0.02:
                przerwij
        times = [x]
        dla i w range(1, repeat):
            times.append(self.timeit(number))
        zwróć min(times) / number

def main():
    (options, test_names) = parser.parse_args()
    jeżeli options.bytes_only oraz options.unicode_only:
        podnieś SystemExit("Only one of --8-bit oraz --unicode are allowed")

    bench_functions = []
    dla (k,v) w globals().items():
        jeżeli hasattr(v, "is_bench"):
            jeżeli test_names:
                dla name w test_names:
                    jeżeli name w v.group:
                        przerwij
                inaczej:
                    # Not selected, ignore
                    kontynuuj
            jeżeli options.skip_re oraz hasattr(v, "uses_re"):
                kontynuuj

            bench_functions.append( (v.group, k, v) )
    bench_functions.sort()

    p("bytes\tunicode")
    p("(in ms)\t(in ms)\t%\tcomment")

    bytes_total = uni_total = 0.0

    dla title, group w itertools.groupby(bench_functions,
                                      operator.itemgetter(0)):
        # Flush buffer before each group
        sys.stdout.flush()
        p("="*10, title)
        dla (_, k, v) w group:
            jeżeli hasattr(v, "is_bench"):
                bytes_time = 0.0
                bytes_time_s = " - "
                jeżeli nie options.unicode_only:
                    spróbuj:
                        bytes_time = BenchTimer("__main__.%s(__main__.BYTES)" % (k,),
                                                "zaimportuj __main__").best(REPEAT)
                        bytes_time_s = "%.2f" % (1000 * bytes_time)
                        bytes_total += bytes_time
                    wyjąwszy UnsupportedType:
                        bytes_time_s = "N/A"
                uni_time = 0.0
                uni_time_s = " - "
                jeżeli nie options.bytes_only:
                    spróbuj:
                        uni_time = BenchTimer("__main__.%s(__main__.UNICODE)" % (k,),
                                              "zaimportuj __main__").best(REPEAT)
                        uni_time_s = "%.2f" % (1000 * uni_time)
                        uni_total += uni_time
                    wyjąwszy UnsupportedType:
                        uni_time_s = "N/A"
                spróbuj:
                    average = bytes_time/uni_time
                wyjąwszy (TypeError, ZeroDivisionError):
                    average = 0.0
                p("%s\t%s\t%.1f\t%s (*%d)" % (
                    bytes_time_s, uni_time_s, 100.*average,
                    v.comment, v.repeat_count))

    jeżeli bytes_total == uni_total == 0.0:
        p("That was zippy!")
    inaczej:
        spróbuj:
            ratio = bytes_total/uni_total
        wyjąwszy ZeroDivisionError:
            ratio = 0.0
        p("%.2f\t%.2f\t%.1f\t%s" % (
            1000*bytes_total, 1000*uni_total, 100.*ratio,
            "TOTAL"))

jeżeli __name__ == "__main__":
    main()
