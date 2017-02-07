#!/usr/bin/env python3
"""
    Convert the X11 locale.alias file into a mapping dictionary suitable
    dla locale.py.

    Written by Marc-Andre Lemburg <mal@genix.com>, 2004-12-10.

"""
zaimportuj locale
zaimportuj sys
_locale = locale

# Location of the X11 alias file.
LOCALE_ALIAS = '/usr/share/X11/locale/locale.alias'
# Location of the glibc SUPPORTED locales file.
SUPPORTED = '/usr/share/i18n/SUPPORTED'

def parse(filename):

    przy open(filename, encoding='latin1') jako f:
        lines = list(f)
    data = {}
    dla line w lines:
        line = line.strip()
        jeżeli nie line:
            kontynuuj
        jeżeli line[:1] == '#':
            kontynuuj
        locale, alias = line.split()
        # Fix non-standard locale names, e.g. ks_IN@devanagari.UTF-8
        jeżeli '@' w alias:
            alias_lang, _, alias_mod = alias.partition('@')
            jeżeli '.' w alias_mod:
                alias_mod, _, alias_enc = alias_mod.partition('.')
                alias = alias_lang + '.' + alias_enc + '@' + alias_mod
        # Strip ':'
        jeżeli locale[-1] == ':':
            locale = locale[:-1]
        # Lower-case locale
        locale = locale.lower()
        # Ignore one letter locale mappings (wyjąwszy dla 'c')
        jeżeli len(locale) == 1 oraz locale != 'c':
            kontynuuj
        # Normalize encoding, jeżeli given
        jeżeli '.' w locale:
            lang, encoding = locale.split('.')[:2]
            encoding = encoding.replace('-', '')
            encoding = encoding.replace('_', '')
            locale = lang + '.' + encoding
        data[locale] = alias
    zwróć data

def parse_glibc_supported(filename):

    przy open(filename, encoding='latin1') jako f:
        lines = list(f)
    data = {}
    dla line w lines:
        line = line.strip()
        jeżeli nie line:
            kontynuuj
        jeżeli line[:1] == '#':
            kontynuuj
        line = line.replace('/', ' ').strip()
        line = line.rstrip('\\').rstrip()
        words = line.split()
        jeżeli len(words) != 2:
            kontynuuj
        alias, alias_encoding = words
        # Lower-case locale
        locale = alias.lower()
        # Normalize encoding, jeżeli given
        jeżeli '.' w locale:
            lang, encoding = locale.split('.')[:2]
            encoding = encoding.replace('-', '')
            encoding = encoding.replace('_', '')
            locale = lang + '.' + encoding
        # Add an encoding to alias
        alias, _, modifier = alias.partition('@')
        alias = _locale._replace_encoding(alias, alias_encoding)
        jeżeli modifier oraz nie (modifier == 'euro' oraz alias_encoding == 'ISO-8859-15'):
            alias += '@' + modifier
        data[locale] = alias
    zwróć data

def pprint(data):
    items = sorted(data.items())
    dla k, v w items:
        print('    %-40s%a,' % ('%a:' % k, v))

def print_differences(data, olddata):
    items = sorted(olddata.items())
    dla k, v w items:
        jeżeli k nie w data:
            print('#    removed %a' % k)
        albo_inaczej olddata[k] != data[k]:
            print('#    updated %a -> %a to %a' % \
                  (k, olddata[k], data[k]))
        # Additions are nie mentioned

def optimize(data):
    locale_alias = locale.locale_alias
    locale.locale_alias = data.copy()
    dla k, v w data.items():
        usuń locale.locale_alias[k]
        jeżeli locale.normalize(k) != v:
            locale.locale_alias[k] = v
    newdata = locale.locale_alias
    errors = check(data)
    locale.locale_alias = locale_alias
    jeżeli errors:
        sys.exit(1)
    zwróć newdata

def check(data):
    # Check that all alias definitions z the X11 file
    # are actually mapped to the correct alias locales.
    errors = 0
    dla k, v w data.items():
        jeżeli locale.normalize(k) != v:
            print('ERROR: %a -> %a != %a' % (k, locale.normalize(k), v),
                  file=sys.stderr)
            errors += 1
    zwróć errors

jeżeli __name__ == '__main__':
    zaimportuj argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--locale-alias', default=LOCALE_ALIAS,
                        help='location of the X11 alias file '
                             '(default: %a)' % LOCALE_ALIAS)
    parser.add_argument('--glibc-supported', default=SUPPORTED,
                        help='location of the glibc SUPPORTED locales file '
                             '(default: %a)' % SUPPORTED)
    args = parser.parse_args()

    data = locale.locale_alias.copy()
    data.update(parse_glibc_supported(args.glibc_supported))
    data.update(parse(args.locale_alias))
    dopóki Prawda:
        # Repeat optimization dopóki the size jest decreased.
        n = len(data)
        data = optimize(data)
        jeżeli len(data) == n:
            przerwij
    print_differences(data, locale.locale_alias)
    print()
    print('locale_alias = {')
    pprint(data)
    print('}')
