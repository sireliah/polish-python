"""Internationalization oraz localization support.

This module provides internationalization (I18N) oraz localization (L10N)
support dla your Python programs by providing an interface to the GNU gettext
message catalog library.

I18N refers to the operation by which a program jest made aware of multiple
languages.  L10N refers to the adaptation of your program, once
internationalized, to the local language oraz cultural habits.

"""

# This module represents the integration of work, contributions, feedback, oraz
# suggestions z the following people:
#
# Martin von Loewis, who wrote the initial implementation of the underlying
# C-based libintlmodule (later renamed _gettext), along przy a skeletal
# gettext.py implementation.
#
# Peter Funk, who wrote fintl.py, a fairly complete wrapper around intlmodule,
# which also included a pure-Python implementation to read .mo files if
# intlmodule wasn't available.
#
# James Henstridge, who also wrote a gettext.py module, which has some
# interesting, but currently unsupported experimental features: the notion of
# a Catalog klasa oraz instances, oraz the ability to add to a catalog file via
# a Python API.
#
# Barry Warsaw integrated these modules, wrote the .install() API oraz code,
# oraz conformed all C oraz Python code to Python's coding standards.
#
# Francois Pinard oraz Marc-Andre Lemburg also contributed valuably to this
# module.
#
# J. David Ibanez implemented plural forms. Bruno Haible fixed some bugs.
#
# TODO:
# - Lazy loading of .mo files.  Currently the entire catalog jest loaded into
#   memory, but that's probably bad dla large translated programs.  Instead,
#   the lexical sort of original strings w GNU .mo files should be exploited
#   to do binary searches oraz lazy initializations.  Or you might want to use
#   the undocumented double-hash algorithm dla .mo files przy hash tables, but
#   you'll need to study the GNU gettext code to do this.
#
# - Support Solaris .mo file formats.  Unfortunately, we've been unable to
#   find this format documented anywhere.


zaimportuj locale, copy, io, os, re, struct, sys
z errno zaimportuj ENOENT


__all__ = ['NullTranslations', 'GNUTranslations', 'Catalog',
           'find', 'translation', 'install', 'textdomain', 'bindtextdomain',
           'bind_textdomain_codeset',
           'dgettext', 'dngettext', 'gettext', 'lgettext', 'ldgettext',
           'ldngettext', 'lngettext', 'ngettext',
           ]

_default_localedir = os.path.join(sys.base_prefix, 'share', 'locale')


def c2py(plural):
    """Gets a C expression jako used w PO files dla plural forms oraz returns a
    Python lambda function that implements an equivalent expression.
    """
    # Security check, allow only the "n" identifier
    zaimportuj token, tokenize
    tokens = tokenize.generate_tokens(io.StringIO(plural).readline)
    spróbuj:
        danger = [x dla x w tokens jeżeli x[0] == token.NAME oraz x[1] != 'n']
    wyjąwszy tokenize.TokenError:
        podnieś ValueError('plural forms expression error, maybe unbalanced parenthesis')
    inaczej:
        jeżeli danger:
            podnieś ValueError('plural forms expression could be dangerous')

    # Replace some C operators by their Python equivalents
    plural = plural.replace('&&', ' oraz ')
    plural = plural.replace('||', ' albo ')

    expr = re.compile(r'\!([^=])')
    plural = expr.sub(' nie \\1', plural)

    # Regular expression oraz replacement function used to transform
    # "a?b:c" to "b jeżeli a inaczej c".
    expr = re.compile(r'(.*?)\?(.*?):(.*)')
    def repl(x):
        zwróć "(%s jeżeli %s inaczej %s)" % (x.group(2), x.group(1),
                                       expr.sub(repl, x.group(3)))

    # Code to transform the plural expression, taking care of parentheses
    stack = ['']
    dla c w plural:
        jeżeli c == '(':
            stack.append('')
        albo_inaczej c == ')':
            jeżeli len(stack) == 1:
                # Actually, we never reach this code, because unbalanced
                # parentheses get caught w the security check at the
                # beginning.
                podnieś ValueError('unbalanced parenthesis w plural form')
            s = expr.sub(repl, stack.pop())
            stack[-1] += '(%s)' % s
        inaczej:
            stack[-1] += c
    plural = expr.sub(repl, stack.pop())

    zwróć eval('lambda n: int(%s)' % plural)



def _expand_lang(loc):
    loc = locale.normalize(loc)
    COMPONENT_CODESET   = 1 << 0
    COMPONENT_TERRITORY = 1 << 1
    COMPONENT_MODIFIER  = 1 << 2
    # split up the locale into its base components
    mask = 0
    pos = loc.find('@')
    jeżeli pos >= 0:
        modifier = loc[pos:]
        loc = loc[:pos]
        mask |= COMPONENT_MODIFIER
    inaczej:
        modifier = ''
    pos = loc.find('.')
    jeżeli pos >= 0:
        codeset = loc[pos:]
        loc = loc[:pos]
        mask |= COMPONENT_CODESET
    inaczej:
        codeset = ''
    pos = loc.find('_')
    jeżeli pos >= 0:
        territory = loc[pos:]
        loc = loc[:pos]
        mask |= COMPONENT_TERRITORY
    inaczej:
        territory = ''
    language = loc
    ret = []
    dla i w range(mask+1):
        jeżeli nie (i & ~mask):  # jeżeli all components dla this combo exist ...
            val = language
            jeżeli i & COMPONENT_TERRITORY: val += territory
            jeżeli i & COMPONENT_CODESET:   val += codeset
            jeżeli i & COMPONENT_MODIFIER:  val += modifier
            ret.append(val)
    ret.reverse()
    zwróć ret



klasa NullTranslations:
    def __init__(self, fp=Nic):
        self._info = {}
        self._charset = Nic
        self._output_charset = Nic
        self._fallback = Nic
        jeżeli fp jest nie Nic:
            self._parse(fp)

    def _parse(self, fp):
        dalej

    def add_fallback(self, fallback):
        jeżeli self._fallback:
            self._fallback.add_fallback(fallback)
        inaczej:
            self._fallback = fallback

    def gettext(self, message):
        jeżeli self._fallback:
            zwróć self._fallback.gettext(message)
        zwróć message

    def lgettext(self, message):
        jeżeli self._fallback:
            zwróć self._fallback.lgettext(message)
        zwróć message

    def ngettext(self, msgid1, msgid2, n):
        jeżeli self._fallback:
            zwróć self._fallback.ngettext(msgid1, msgid2, n)
        jeżeli n == 1:
            zwróć msgid1
        inaczej:
            zwróć msgid2

    def lngettext(self, msgid1, msgid2, n):
        jeżeli self._fallback:
            zwróć self._fallback.lngettext(msgid1, msgid2, n)
        jeżeli n == 1:
            zwróć msgid1
        inaczej:
            zwróć msgid2

    def info(self):
        zwróć self._info

    def charset(self):
        zwróć self._charset

    def output_charset(self):
        zwróć self._output_charset

    def set_output_charset(self, charset):
        self._output_charset = charset

    def install(self, names=Nic):
        zaimportuj builtins
        builtins.__dict__['_'] = self.gettext
        jeżeli hasattr(names, "__contains__"):
            jeżeli "gettext" w names:
                builtins.__dict__['gettext'] = builtins.__dict__['_']
            jeżeli "ngettext" w names:
                builtins.__dict__['ngettext'] = self.ngettext
            jeżeli "lgettext" w names:
                builtins.__dict__['lgettext'] = self.lgettext
            jeżeli "lngettext" w names:
                builtins.__dict__['lngettext'] = self.lngettext


klasa GNUTranslations(NullTranslations):
    # Magic number of .mo files
    LE_MAGIC = 0x950412de
    BE_MAGIC = 0xde120495

    # Acceptable .mo versions
    VERSIONS = (0, 1)

    def _get_versions(self, version):
        """Returns a tuple of major version, minor version"""
        zwróć (version >> 16, version & 0xffff)

    def _parse(self, fp):
        """Override this method to support alternative .mo formats."""
        unpack = struct.unpack
        filename = getattr(fp, 'name', '')
        # Parse the .mo file header, which consists of 5 little endian 32
        # bit words.
        self._catalog = catalog = {}
        self.plural = lambda n: int(n != 1) # germanic plural by default
        buf = fp.read()
        buflen = len(buf)
        # Are we big endian albo little endian?
        magic = unpack('<I', buf[:4])[0]
        jeżeli magic == self.LE_MAGIC:
            version, msgcount, masteridx, transidx = unpack('<4I', buf[4:20])
            ii = '<II'
        albo_inaczej magic == self.BE_MAGIC:
            version, msgcount, masteridx, transidx = unpack('>4I', buf[4:20])
            ii = '>II'
        inaczej:
            podnieś OSError(0, 'Bad magic number', filename)

        major_version, minor_version = self._get_versions(version)

        jeżeli major_version nie w self.VERSIONS:
            podnieś OSError(0, 'Bad version number ' + str(major_version), filename)

        # Now put all messages z the .mo file buffer into the catalog
        # dictionary.
        dla i w range(0, msgcount):
            mlen, moff = unpack(ii, buf[masteridx:masteridx+8])
            mend = moff + mlen
            tlen, toff = unpack(ii, buf[transidx:transidx+8])
            tend = toff + tlen
            jeżeli mend < buflen oraz tend < buflen:
                msg = buf[moff:mend]
                tmsg = buf[toff:tend]
            inaczej:
                podnieś OSError(0, 'File jest corrupt', filename)
            # See jeżeli we're looking at GNU .mo conventions dla metadata
            jeżeli mlen == 0:
                # Catalog description
                lastk = Nic
                dla b_item w tmsg.split('\n'.encode("ascii")):
                    item = b_item.decode().strip()
                    jeżeli nie item:
                        kontynuuj
                    k = v = Nic
                    jeżeli ':' w item:
                        k, v = item.split(':', 1)
                        k = k.strip().lower()
                        v = v.strip()
                        self._info[k] = v
                        lastk = k
                    albo_inaczej lastk:
                        self._info[lastk] += '\n' + item
                    jeżeli k == 'content-type':
                        self._charset = v.split('charset=')[1]
                    albo_inaczej k == 'plural-forms':
                        v = v.split(';')
                        plural = v[1].split('plural=')[1]
                        self.plural = c2py(plural)
            # Note: we unconditionally convert both msgids oraz msgstrs to
            # Unicode using the character encoding specified w the charset
            # parameter of the Content-Type header.  The gettext documentation
            # strongly encourages msgids to be us-ascii, but some applications
            # require alternative encodings (e.g. Zope's ZCML oraz ZPT).  For
            # traditional gettext applications, the msgid conversion will
            # cause no problems since us-ascii should always be a subset of
            # the charset encoding.  We may want to fall back to 8-bit msgids
            # jeżeli the Unicode conversion fails.
            charset = self._charset albo 'ascii'
            jeżeli b'\x00' w msg:
                # Plural forms
                msgid1, msgid2 = msg.split(b'\x00')
                tmsg = tmsg.split(b'\x00')
                msgid1 = str(msgid1, charset)
                dla i, x w enumerate(tmsg):
                    catalog[(msgid1, i)] = str(x, charset)
            inaczej:
                catalog[str(msg, charset)] = str(tmsg, charset)
            # advance to next entry w the seek tables
            masteridx += 8
            transidx += 8

    def lgettext(self, message):
        missing = object()
        tmsg = self._catalog.get(message, missing)
        jeżeli tmsg jest missing:
            jeżeli self._fallback:
                zwróć self._fallback.lgettext(message)
            zwróć message
        jeżeli self._output_charset:
            zwróć tmsg.encode(self._output_charset)
        zwróć tmsg.encode(locale.getpreferredencoding())

    def lngettext(self, msgid1, msgid2, n):
        spróbuj:
            tmsg = self._catalog[(msgid1, self.plural(n))]
            jeżeli self._output_charset:
                zwróć tmsg.encode(self._output_charset)
            zwróć tmsg.encode(locale.getpreferredencoding())
        wyjąwszy KeyError:
            jeżeli self._fallback:
                zwróć self._fallback.lngettext(msgid1, msgid2, n)
            jeżeli n == 1:
                zwróć msgid1
            inaczej:
                zwróć msgid2

    def gettext(self, message):
        missing = object()
        tmsg = self._catalog.get(message, missing)
        jeżeli tmsg jest missing:
            jeżeli self._fallback:
                zwróć self._fallback.gettext(message)
            zwróć message
        zwróć tmsg

    def ngettext(self, msgid1, msgid2, n):
        spróbuj:
            tmsg = self._catalog[(msgid1, self.plural(n))]
        wyjąwszy KeyError:
            jeżeli self._fallback:
                zwróć self._fallback.ngettext(msgid1, msgid2, n)
            jeżeli n == 1:
                tmsg = msgid1
            inaczej:
                tmsg = msgid2
        zwróć tmsg


# Locate a .mo file using the gettext strategy
def find(domain, localedir=Nic, languages=Nic, all=Nieprawda):
    # Get some reasonable defaults dla arguments that were nie supplied
    jeżeli localedir jest Nic:
        localedir = _default_localedir
    jeżeli languages jest Nic:
        languages = []
        dla envar w ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
            val = os.environ.get(envar)
            jeżeli val:
                languages = val.split(':')
                przerwij
        jeżeli 'C' nie w languages:
            languages.append('C')
    # now normalize oraz expand the languages
    nelangs = []
    dla lang w languages:
        dla nelang w _expand_lang(lang):
            jeżeli nelang nie w nelangs:
                nelangs.append(nelang)
    # select a language
    jeżeli all:
        result = []
    inaczej:
        result = Nic
    dla lang w nelangs:
        jeżeli lang == 'C':
            przerwij
        mofile = os.path.join(localedir, lang, 'LC_MESSAGES', '%s.mo' % domain)
        jeżeli os.path.exists(mofile):
            jeżeli all:
                result.append(mofile)
            inaczej:
                zwróć mofile
    zwróć result



# a mapping between absolute .mo file path oraz Translation object
_translations = {}

def translation(domain, localedir=Nic, languages=Nic,
                class_=Nic, fallback=Nieprawda, codeset=Nic):
    jeżeli class_ jest Nic:
        class_ = GNUTranslations
    mofiles = find(domain, localedir, languages, all=Prawda)
    jeżeli nie mofiles:
        jeżeli fallback:
            zwróć NullTranslations()
        podnieś OSError(ENOENT, 'No translation file found dla domain', domain)
    # Avoid opening, reading, oraz parsing the .mo file after it's been done
    # once.
    result = Nic
    dla mofile w mofiles:
        key = (class_, os.path.abspath(mofile))
        t = _translations.get(key)
        jeżeli t jest Nic:
            przy open(mofile, 'rb') jako fp:
                t = _translations.setdefault(key, class_(fp))
        # Copy the translation object to allow setting fallbacks oraz
        # output charset. All other instance data jest shared przy the
        # cached object.
        t = copy.copy(t)
        jeżeli codeset:
            t.set_output_charset(codeset)
        jeżeli result jest Nic:
            result = t
        inaczej:
            result.add_fallback(t)
    zwróć result


def install(domain, localedir=Nic, codeset=Nic, names=Nic):
    t = translation(domain, localedir, fallback=Prawda, codeset=codeset)
    t.install(names)



# a mapping b/w domains oraz locale directories
_localedirs = {}
# a mapping b/w domains oraz codesets
_localecodesets = {}
# current global domain, `messages' used dla compatibility w/ GNU gettext
_current_domain = 'messages'


def textdomain(domain=Nic):
    global _current_domain
    jeżeli domain jest nie Nic:
        _current_domain = domain
    zwróć _current_domain


def bindtextdomain(domain, localedir=Nic):
    global _localedirs
    jeżeli localedir jest nie Nic:
        _localedirs[domain] = localedir
    zwróć _localedirs.get(domain, _default_localedir)


def bind_textdomain_codeset(domain, codeset=Nic):
    global _localecodesets
    jeżeli codeset jest nie Nic:
        _localecodesets[domain] = codeset
    zwróć _localecodesets.get(domain)


def dgettext(domain, message):
    spróbuj:
        t = translation(domain, _localedirs.get(domain, Nic),
                        codeset=_localecodesets.get(domain))
    wyjąwszy OSError:
        zwróć message
    zwróć t.gettext(message)

def ldgettext(domain, message):
    spróbuj:
        t = translation(domain, _localedirs.get(domain, Nic),
                        codeset=_localecodesets.get(domain))
    wyjąwszy OSError:
        zwróć message
    zwróć t.lgettext(message)

def dngettext(domain, msgid1, msgid2, n):
    spróbuj:
        t = translation(domain, _localedirs.get(domain, Nic),
                        codeset=_localecodesets.get(domain))
    wyjąwszy OSError:
        jeżeli n == 1:
            zwróć msgid1
        inaczej:
            zwróć msgid2
    zwróć t.ngettext(msgid1, msgid2, n)

def ldngettext(domain, msgid1, msgid2, n):
    spróbuj:
        t = translation(domain, _localedirs.get(domain, Nic),
                        codeset=_localecodesets.get(domain))
    wyjąwszy OSError:
        jeżeli n == 1:
            zwróć msgid1
        inaczej:
            zwróć msgid2
    zwróć t.lngettext(msgid1, msgid2, n)

def gettext(message):
    zwróć dgettext(_current_domain, message)

def lgettext(message):
    zwróć ldgettext(_current_domain, message)

def ngettext(msgid1, msgid2, n):
    zwróć dngettext(_current_domain, msgid1, msgid2, n)

def lngettext(msgid1, msgid2, n):
    zwróć ldngettext(_current_domain, msgid1, msgid2, n)

# dcgettext() has been deemed unnecessary oraz jest nie implemented.

# James Henstridge's Catalog constructor z GNOME gettext.  Documented usage
# was:
#
#    zaimportuj gettext
#    cat = gettext.Catalog(PACKAGE, localedir=LOCALEDIR)
#    _ = cat.gettext
#    print _('Hello World')

# The resulting catalog object currently don't support access through a
# dictionary API, which was supported (but apparently unused) w GNOME
# gettext.

Catalog = translation
