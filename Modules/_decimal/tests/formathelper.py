#
# Copyright (c) 2008-2012 Stefan Krah. All rights reserved.
#
# Redistribution oraz use w source oraz binary forms, przy albo without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions oraz the following disclaimer.
#
# 2. Redistributions w binary form must reproduce the above copyright
#    notice, this list of conditions oraz the following disclaimer w the
#    documentation and/or other materials provided przy the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


# Generate PEP-3101 format strings.


zaimportuj os, sys, locale, random
zaimportuj platform, subprocess
z test.support zaimportuj import_fresh_module
z distutils.spawn zaimportuj find_executable

C = import_fresh_module('decimal', fresh=['_decimal'])
P = import_fresh_module('decimal', blocked=['_decimal'])


windows_lang_strings = [
  "chinese", "chinese-simplified", "chinese-traditional", "czech", "danish",
  "dutch", "belgian", "english", "australian", "canadian", "english-nz",
  "english-uk", "english-us", "finnish", "french", "french-belgian",
  "french-canadian", "french-swiss", "german", "german-austrian",
  "german-swiss", "greek", "hungarian", "icelandic", "italian", "italian-swiss",
  "japanese", "korean", "norwegian", "norwegian-bokmal", "norwegian-nynorsk",
  "polish", "portuguese", "portuguese-brazil", "russian", "slovak", "spanish",
  "spanish-mexican", "spanish-modern", "swedish", "turkish",
]

preferred_encoding = {
  'cs_CZ': 'ISO8859-2',
  'cs_CZ.iso88592': 'ISO8859-2',
  'czech': 'ISO8859-2',
  'eesti': 'ISO8859-1',
  'estonian': 'ISO8859-1',
  'et_EE': 'ISO8859-15',
  'et_EE.ISO-8859-15': 'ISO8859-15',
  'et_EE.iso885915': 'ISO8859-15',
  'et_EE.iso88591': 'ISO8859-1',
  'fi_FI.iso88591': 'ISO8859-1',
  'fi_FI': 'ISO8859-15',
  'fi_FI@euro': 'ISO8859-15',
  'fi_FI.iso885915@euro': 'ISO8859-15',
  'finnish': 'ISO8859-1',
  'lv_LV': 'ISO8859-13',
  'lv_LV.iso885913': 'ISO8859-13',
  'nb_NO': 'ISO8859-1',
  'nb_NO.iso88591': 'ISO8859-1',
  'bokmal': 'ISO8859-1',
  'nn_NO': 'ISO8859-1',
  'nn_NO.iso88591': 'ISO8859-1',
  'no_NO': 'ISO8859-1',
  'norwegian': 'ISO8859-1',
  'nynorsk': 'ISO8859-1',
  'ru_RU': 'ISO8859-5',
  'ru_RU.iso88595': 'ISO8859-5',
  'russian': 'ISO8859-5',
  'ru_RU.KOI8-R': 'KOI8-R',
  'ru_RU.koi8r': 'KOI8-R',
  'ru_RU.CP1251': 'CP1251',
  'ru_RU.cp1251': 'CP1251',
  'sk_SK': 'ISO8859-2',
  'sk_SK.iso88592': 'ISO8859-2',
  'slovak': 'ISO8859-2',
  'sv_FI': 'ISO8859-1',
  'sv_FI.iso88591': 'ISO8859-1',
  'sv_FI@euro': 'ISO8859-15',
  'sv_FI.iso885915@euro': 'ISO8859-15',
  'uk_UA': 'KOI8-U',
  'uk_UA.koi8u': 'KOI8-U'
}

integers = [
  "",
  "1",
  "12",
  "123",
  "1234",
  "12345",
  "123456",
  "1234567",
  "12345678",
  "123456789",
  "1234567890",
  "12345678901",
  "123456789012",
  "1234567890123",
  "12345678901234",
  "123456789012345",
  "1234567890123456",
  "12345678901234567",
  "123456789012345678",
  "1234567890123456789",
  "12345678901234567890",
  "123456789012345678901",
  "1234567890123456789012",
]

numbers = [
  "0", "-0", "+0",
  "0.0", "-0.0", "+0.0",
  "0e0", "-0e0", "+0e0",
  ".0", "-.0",
  ".1", "-.1",
  "1.1", "-1.1",
  "1e1", "-1e1"
]

# Get the list of available locales.
jeżeli platform.system() == 'Windows':
    locale_list = windows_lang_strings
inaczej:
    locale_list = ['C']
    jeżeli os.path.isfile("/var/lib/locales/supported.d/local"):
        # On Ubuntu, `locale -a` gives the wrong case dla some locales,
        # so we get the correct names directly:
        przy open("/var/lib/locales/supported.d/local") jako f:
            locale_list = [loc.split()[0] dla loc w f.readlines() \
                           jeżeli nie loc.startswith('#')]
    albo_inaczej find_executable('locale'):
        locale_list = subprocess.Popen(["locale", "-a"],
                          stdout=subprocess.PIPE).communicate()[0]
        spróbuj:
            locale_list = locale_list.decode()
        wyjąwszy UnicodeDecodeError:
            # Some distributions insist on using latin-1 characters
            # w their locale names.
            locale_list = locale_list.decode('latin-1')
        locale_list = locale_list.split('\n')
spróbuj:
    locale_list.remove('')
wyjąwszy ValueError:
    dalej

# Debian
jeżeli os.path.isfile("/etc/locale.alias"):
    przy open("/etc/locale.alias") jako f:
        dopóki 1:
            spróbuj:
                line = f.readline()
            wyjąwszy UnicodeDecodeError:
                kontynuuj
            jeżeli line == "":
                przerwij
            jeżeli line.startswith('#'):
                kontynuuj
            x = line.split()
            jeżeli len(x) == 2:
                jeżeli x[0] w locale_list:
                    locale_list.remove(x[0])

# FreeBSD
jeżeli platform.system() == 'FreeBSD':
    # http://www.freebsd.org/cgi/query-pr.cgi?pr=142173
    # en_GB.US-ASCII has 163 jako the currency symbol.
    dla loc w ['it_CH.ISO8859-1', 'it_CH.ISO8859-15', 'it_CH.UTF-8',
                'it_IT.ISO8859-1', 'it_IT.ISO8859-15', 'it_IT.UTF-8',
                'sl_SI.ISO8859-2', 'sl_SI.UTF-8',
                'en_GB.US-ASCII']:
        spróbuj:
            locale_list.remove(loc)
        wyjąwszy ValueError:
            dalej

# Print a testcase w the format of the IBM tests (dla runtest.c):
def get_preferred_encoding():
    loc = locale.setlocale(locale.LC_CTYPE)
    jeżeli loc w preferred_encoding:
        zwróć preferred_encoding[loc]
    inaczej:
        zwróć locale.getpreferredencoding()

def printit(testno, s, fmt, encoding=Nic):
    jeżeli nie encoding:
        encoding = get_preferred_encoding()
    spróbuj:
        result = format(P.Decimal(s), fmt)
        fmt = str(fmt.encode(encoding))[2:-1]
        result = str(result.encode(encoding))[2:-1]
        jeżeli "'" w result:
            sys.stdout.write("xfmt%d  format  %s  '%s'  ->  \"%s\"\n"
                             % (testno, s, fmt, result))
        inaczej:
            sys.stdout.write("xfmt%d  format  %s  '%s'  ->  '%s'\n"
                             % (testno, s, fmt, result))
    wyjąwszy Exception jako err:
        sys.stderr.write("%s  %s  %s\n" % (err, s, fmt))


# Check jeżeli an integer can be converted to a valid fill character.
def check_fillchar(i):
    spróbuj:
        c = chr(i)
        c.encode('utf-8').decode()
        format(P.Decimal(0), c + '<19g')
        zwróć c
    wyjąwszy:
        zwróć Nic

# Generate all unicode characters that are accepted as
# fill characters by decimal.py.
def all_fillchars():
    dla i w range(0, 0x110002):
        c = check_fillchar(i)
        jeżeli c: uzyskaj c

# Return random fill character.
def rand_fillchar():
    dopóki 1:
        i = random.randrange(0, 0x110002)
        c = check_fillchar(i)
        jeżeli c: zwróć c

# Generate random format strings
# [[fill]align][sign][#][0][width][.precision][type]
def rand_format(fill, typespec='EeGgFfn%'):
    active = sorted(random.sample(range(7), random.randrange(8)))
    have_align = 0
    s = ''
    dla elem w active:
        jeżeli elem == 0: # fill+align
            s += fill
            s += random.choice('<>=^')
            have_align = 1
        albo_inaczej elem == 1: # sign
            s += random.choice('+- ')
        albo_inaczej elem == 2 oraz nie have_align: # zeropad
            s += '0'
        albo_inaczej elem == 3: # width
            s += str(random.randrange(1, 100))
        albo_inaczej elem == 4: # thousands separator
            s += ','
        albo_inaczej elem == 5: # prec
            s += '.'
            s += str(random.randrange(100))
        albo_inaczej elem == 6:
            jeżeli 4 w active: c = typespec.replace('n', '')
            inaczej: c = typespec
            s += random.choice(c)
    zwróć s

# Partially brute force all possible format strings containing a thousands
# separator. Fall back to random where the runtime would become excessive.
# [[fill]align][sign][#][0][width][,][.precision][type]
def all_format_sep():
    dla align w ('', '<', '>', '=', '^'):
        dla fill w ('', 'x'):
            jeżeli align == '': fill = ''
            dla sign w ('', '+', '-', ' '):
                dla zeropad w ('', '0'):
                    jeżeli align != '': zeropad = ''
                    dla width w ['']+[str(y) dla y w range(1, 15)]+['101']:
                        dla prec w ['']+['.'+str(y) dla y w range(15)]:
                            # dla type w ('', 'E', 'e', 'G', 'g', 'F', 'f', '%'):
                            type = random.choice(('', 'E', 'e', 'G', 'g', 'F', 'f', '%'))
                            uzyskaj ''.join((fill, align, sign, zeropad, width, ',', prec, type))

# Partially brute force all possible format strings przy an 'n' specifier.
# [[fill]align][sign][#][0][width][,][.precision][type]
def all_format_loc():
    dla align w ('', '<', '>', '=', '^'):
        dla fill w ('', 'x'):
            jeżeli align == '': fill = ''
            dla sign w ('', '+', '-', ' '):
                dla zeropad w ('', '0'):
                    jeżeli align != '': zeropad = ''
                    dla width w ['']+[str(y) dla y w range(1, 20)]+['101']:
                        dla prec w ['']+['.'+str(y) dla y w range(1, 20)]:
                            uzyskaj ''.join((fill, align, sign, zeropad, width, prec, 'n'))

# Generate random format strings przy a unicode fill character
# [[fill]align][sign][#][0][width][,][.precision][type]
def randfill(fill):
    active = sorted(random.sample(range(5), random.randrange(6)))
    s = ''
    s += str(fill)
    s += random.choice('<>=^')
    dla elem w active:
        jeżeli elem == 0: # sign
            s += random.choice('+- ')
        albo_inaczej elem == 1: # width
            s += str(random.randrange(1, 100))
        albo_inaczej elem == 2: # thousands separator
            s += ','
        albo_inaczej elem == 3: # prec
            s += '.'
            s += str(random.randrange(100))
        albo_inaczej elem == 4:
            jeżeli 2 w active: c = 'EeGgFf%'
            inaczej: c = 'EeGgFfn%'
            s += random.choice(c)
    zwróć s

# Generate random format strings przy random locale setting
# [[fill]align][sign][#][0][width][,][.precision][type]
def rand_locale():
    spróbuj:
        loc = random.choice(locale_list)
        locale.setlocale(locale.LC_ALL, loc)
    wyjąwszy locale.Error jako err:
        dalej
    active = sorted(random.sample(range(5), random.randrange(6)))
    s = ''
    have_align = 0
    dla elem w active:
        jeżeli elem == 0: # fill+align
            s += chr(random.randrange(32, 128))
            s += random.choice('<>=^')
            have_align = 1
        albo_inaczej elem == 1: # sign
            s += random.choice('+- ')
        albo_inaczej elem == 2 oraz nie have_align: # zeropad
            s += '0'
        albo_inaczej elem == 3: # width
            s += str(random.randrange(1, 100))
        albo_inaczej elem == 4: # prec
            s += '.'
            s += str(random.randrange(100))
    s += 'n'
    zwróć s
