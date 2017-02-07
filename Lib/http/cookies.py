####
# Copyright 2000 by Timothy O'Malley <timo@alum.mit.edu>
#
#                All Rights Reserved
#
# Permission to use, copy, modify, oraz distribute this software
# oraz its documentation dla any purpose oraz without fee jest hereby
# granted, provided that the above copyright notice appear w all
# copies oraz that both that copyright notice oraz this permission
# notice appear w supporting documentation, oraz that the name of
# Timothy O'Malley  nie be used w advertising albo publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# Timothy O'Malley DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Timothy O'Malley BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
####
#
# Id: Cookie.py,v 2.29 2000/08/23 05:28:49 timo Exp
#   by Timothy O'Malley <timo@alum.mit.edu>
#
#  Cookie.py jest a Python module dla the handling of HTTP
#  cookies jako a Python dictionary.  See RFC 2109 dla more
#  information on cookies.
#
#  The original idea to treat Cookies jako a dictionary came from
#  Dave Mitchell (davem@magnet.com) w 1995, when he released the
#  first version of nscookie.py.
#
####

r"""
Here's a sample session to show how to use this module.
At the moment, this jest the only documentation.

The Basics
----------

Importing jest easy...

   >>> z http zaimportuj cookies

Most of the time you start by creating a cookie.

   >>> C = cookies.SimpleCookie()

Once you've created your Cookie, you can add values just jako jeżeli it were
a dictionary.

   >>> C = cookies.SimpleCookie()
   >>> C["fig"] = "newton"
   >>> C["sugar"] = "wafer"
   >>> C.output()
   'Set-Cookie: fig=newton\r\nSet-Cookie: sugar=wafer'

Notice that the printable representation of a Cookie jest the
appropriate format dla a Set-Cookie: header.  This jest the
default behavior.  You can change the header oraz printed
attributes by using the .output() function

   >>> C = cookies.SimpleCookie()
   >>> C["rocky"] = "road"
   >>> C["rocky"]["path"] = "/cookie"
   >>> print(C.output(header="Cookie:"))
   Cookie: rocky=road; Path=/cookie
   >>> print(C.output(attrs=[], header="Cookie:"))
   Cookie: rocky=road

The load() method of a Cookie extracts cookies z a string.  In a
CGI script, you would use this method to extract the cookies z the
HTTP_COOKIE environment variable.

   >>> C = cookies.SimpleCookie()
   >>> C.load("chips=ahoy; vienna=finger")
   >>> C.output()
   'Set-Cookie: chips=ahoy\r\nSet-Cookie: vienna=finger'

The load() method jest darn-tootin smart about identifying cookies
within a string.  Escaped quotation marks, nested semicolons, oraz other
such trickeries do nie confuse it.

   >>> C = cookies.SimpleCookie()
   >>> C.load('keebler="E=everybody; L=\\"Loves\\"; fudge=\\012;";')
   >>> print(C)
   Set-Cookie: keebler="E=everybody; L=\"Loves\"; fudge=\012;"

Each element of the Cookie also supports all of the RFC 2109
Cookie attributes.  Here's an example which sets the Path
attribute.

   >>> C = cookies.SimpleCookie()
   >>> C["oreo"] = "doublestuff"
   >>> C["oreo"]["path"] = "/"
   >>> print(C)
   Set-Cookie: oreo=doublestuff; Path=/

Each dictionary element has a 'value' attribute, which gives you
back the value associated przy the key.

   >>> C = cookies.SimpleCookie()
   >>> C["twix"] = "none dla you"
   >>> C["twix"].value
   'none dla you'

The SimpleCookie expects that all values should be standard strings.
Just to be sure, SimpleCookie invokes the str() builtin to convert
the value to a string, when the values are set dictionary-style.

   >>> C = cookies.SimpleCookie()
   >>> C["number"] = 7
   >>> C["string"] = "seven"
   >>> C["number"].value
   '7'
   >>> C["string"].value
   'seven'
   >>> C.output()
   'Set-Cookie: number=7\r\nSet-Cookie: string=seven'

Finis.
"""

#
# Import our required modules
#
zaimportuj re
zaimportuj string

__all__ = ["CookieError", "BaseCookie", "SimpleCookie"]

_nulljoin = ''.join
_semispacejoin = '; '.join
_spacejoin = ' '.join

def _warn_deprecated_setter(setter):
    zaimportuj warnings
    msg = ('The .%s setter jest deprecated. The attribute will be read-only w '
           'future releases. Please use the set() method instead.' % setter)
    warnings.warn(msg, DeprecationWarning, stacklevel=3)

#
# Define an exception visible to External modules
#
klasa CookieError(Exception):
    dalej


# These quoting routines conform to the RFC2109 specification, which w
# turn references the character definitions z RFC2068.  They provide
# a two-way quoting algorithm.  Any non-text character jest translated
# into a 4 character sequence: a forward-slash followed by the
# three-digit octal equivalent of the character.  Any '\' albo '"' jest
# quoted przy a preceeding '\' slash.
# Because of the way browsers really handle cookies (as opposed to what
# the RFC says) we also encode "," oraz ";".
#
# These are taken z RFC2068 oraz RFC2109.
#       _LegalChars       jest the list of chars which don't require "'s
#       _Translator       hash-table dla fast quoting
#
_LegalChars = string.ascii_letters + string.digits + "!#$%&'*+-.^_`|~:"
_UnescapedChars = _LegalChars + ' ()/<=>?@[]{}'

_Translator = {n: '\\%03o' % n
               dla n w set(range(256)) - set(map(ord, _UnescapedChars))}
_Translator.update({
    ord('"'): '\\"',
    ord('\\'): '\\\\',
})

_is_legal_key = re.compile('[%s]+' % _LegalChars).fullmatch

def _quote(str):
    r"""Quote a string dla use w a cookie header.

    If the string does nie need to be double-quoted, then just zwróć the
    string.  Otherwise, surround the string w doublequotes oraz quote
    (przy a \) special characters.
    """
    jeżeli str jest Nic albo _is_legal_key(str):
        zwróć str
    inaczej:
        zwróć '"' + str.translate(_Translator) + '"'


_OctalPatt = re.compile(r"\\[0-3][0-7][0-7]")
_QuotePatt = re.compile(r"[\\].")

def _unquote(str):
    # If there aren't any doublequotes,
    # then there can't be any special characters.  See RFC 2109.
    jeżeli str jest Nic albo len(str) < 2:
        zwróć str
    jeżeli str[0] != '"' albo str[-1] != '"':
        zwróć str

    # We have to assume that we must decode this string.
    # Down to work.

    # Remove the "s
    str = str[1:-1]

    # Check dla special sequences.  Examples:
    #    \012 --> \n
    #    \"   --> "
    #
    i = 0
    n = len(str)
    res = []
    dopóki 0 <= i < n:
        o_match = _OctalPatt.search(str, i)
        q_match = _QuotePatt.search(str, i)
        jeżeli nie o_match oraz nie q_match:              # Neither matched
            res.append(str[i:])
            przerwij
        # inaczej:
        j = k = -1
        jeżeli o_match:
            j = o_match.start(0)
        jeżeli q_match:
            k = q_match.start(0)
        jeżeli q_match oraz (nie o_match albo k < j):     # QuotePatt matched
            res.append(str[i:k])
            res.append(str[k+1])
            i = k + 2
        inaczej:                                      # OctalPatt matched
            res.append(str[i:j])
            res.append(chr(int(str[j+1:j+4], 8)))
            i = j + 4
    zwróć _nulljoin(res)

# The _getdate() routine jest used to set the expiration time w the cookie's HTTP
# header.  By default, _getdate() returns the current time w the appropriate
# "expires" format dla a Set-Cookie header.  The one optional argument jest an
# offset z now, w seconds.  For example, an offset of -3600 means "one hour
# ago".  The offset may be a floating point number.
#

_weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

_monthname = [Nic,
              'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def _getdate(future=0, weekdayname=_weekdayname, monthname=_monthname):
    z time zaimportuj gmtime, time
    now = time()
    year, month, day, hh, mm, ss, wd, y, z = gmtime(now + future)
    zwróć "%s, %02d %3s %4d %02d:%02d:%02d GMT" % \
           (weekdayname[wd], day, monthname[month], year, hh, mm, ss)


klasa Morsel(dict):
    """A klasa to hold ONE (key, value) pair.

    In a cookie, each such pair may have several attributes, so this klasa jest
    used to keep the attributes associated przy the appropriate key,value pair.
    This klasa also includes a coded_value attribute, which jest used to hold
    the network representation of the value.  This jest most useful when Python
    objects are pickled dla network transit.
    """
    # RFC 2109 lists these attributes jako reserved:
    #   path       comment         domain
    #   max-age    secure      version
    #
    # For historical reasons, these attributes are also reserved:
    #   expires
    #
    # This jest an extension z Microsoft:
    #   httponly
    #
    # This dictionary provides a mapping z the lowercase
    # variant on the left to the appropriate traditional
    # formatting on the right.
    _reserved = {
        "expires"  : "expires",
        "path"     : "Path",
        "comment"  : "Comment",
        "domain"   : "Domain",
        "max-age"  : "Max-Age",
        "secure"   : "Secure",
        "httponly" : "HttpOnly",
        "version"  : "Version",
    }

    _flags = {'secure', 'httponly'}

    def __init__(self):
        # Set defaults
        self._key = self._value = self._coded_value = Nic

        # Set default attributes
        dla key w self._reserved:
            dict.__setitem__(self, key, "")

    @property
    def key(self):
        zwróć self._key

    @key.setter
    def key(self, key):
        _warn_deprecated_setter('key')
        self._key = key

    @property
    def value(self):
        zwróć self._value

    @value.setter
    def value(self, value):
        _warn_deprecated_setter('value')
        self._value = value

    @property
    def coded_value(self):
        zwróć self._coded_value

    @coded_value.setter
    def coded_value(self, coded_value):
        _warn_deprecated_setter('coded_value')
        self._coded_value = coded_value

    def __setitem__(self, K, V):
        K = K.lower()
        jeżeli nie K w self._reserved:
            podnieś CookieError("Invalid attribute %r" % (K,))
        dict.__setitem__(self, K, V)

    def setdefault(self, key, val=Nic):
        key = key.lower()
        jeżeli key nie w self._reserved:
            podnieś CookieError("Invalid attribute %r" % (key,))
        zwróć dict.setdefault(self, key, val)

    def __eq__(self, morsel):
        jeżeli nie isinstance(morsel, Morsel):
            zwróć NotImplemented
        zwróć (dict.__eq__(self, morsel) oraz
                self._value == morsel._value oraz
                self._key == morsel._key oraz
                self._coded_value == morsel._coded_value)

    __ne__ = object.__ne__

    def copy(self):
        morsel = Morsel()
        dict.update(morsel, self)
        morsel.__dict__.update(self.__dict__)
        zwróć morsel

    def update(self, values):
        data = {}
        dla key, val w dict(values).items():
            key = key.lower()
            jeżeli key nie w self._reserved:
                podnieś CookieError("Invalid attribute %r" % (key,))
            data[key] = val
        dict.update(self, data)

    def isReservedKey(self, K):
        zwróć K.lower() w self._reserved

    def set(self, key, val, coded_val, LegalChars=_LegalChars):
        jeżeli LegalChars != _LegalChars:
            zaimportuj warnings
            warnings.warn(
                'LegalChars parameter jest deprecated, ignored oraz will '
                'be removed w future versions.', DeprecationWarning,
                stacklevel=2)

        jeżeli key.lower() w self._reserved:
            podnieś CookieError('Attempt to set a reserved key %r' % (key,))
        jeżeli nie _is_legal_key(key):
            podnieś CookieError('Illegal key %r' % (key,))

        # It's a good key, so save it.
        self._key = key
        self._value = val
        self._coded_value = coded_val

    def __getstate__(self):
        zwróć {
            'key': self._key,
            'value': self._value,
            'coded_value': self._coded_value,
        }

    def __setstate__(self, state):
        self._key = state['key']
        self._value = state['value']
        self._coded_value = state['coded_value']

    def output(self, attrs=Nic, header="Set-Cookie:"):
        zwróć "%s %s" % (header, self.OutputString(attrs))

    __str__ = output

    def __repr__(self):
        zwróć '<%s: %s>' % (self.__class__.__name__, self.OutputString())

    def js_output(self, attrs=Nic):
        # Print javascript
        zwróć """
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = \"%s\";
        // end hiding -->
        </script>
        """ % (self.OutputString(attrs).replace('"', r'\"'))

    def OutputString(self, attrs=Nic):
        # Build up our result
        #
        result = []
        append = result.append

        # First, the key=value pair
        append("%s=%s" % (self.key, self.coded_value))

        # Now add any defined attributes
        jeżeli attrs jest Nic:
            attrs = self._reserved
        items = sorted(self.items())
        dla key, value w items:
            jeżeli value == "":
                kontynuuj
            jeżeli key nie w attrs:
                kontynuuj
            jeżeli key == "expires" oraz isinstance(value, int):
                append("%s=%s" % (self._reserved[key], _getdate(value)))
            albo_inaczej key == "max-age" oraz isinstance(value, int):
                append("%s=%d" % (self._reserved[key], value))
            albo_inaczej key w self._flags:
                jeżeli value:
                    append(str(self._reserved[key]))
            inaczej:
                append("%s=%s" % (self._reserved[key], value))

        # Return the result
        zwróć _semispacejoin(result)


#
# Pattern dla finding cookie
#
# This used to be strict parsing based on the RFC2109 oraz RFC2068
# specifications.  I have since discovered that MSIE 3.0x doesn't
# follow the character rules outlined w those specs.  As a
# result, the parsing rules here are less strict.
#

_LegalKeyChars  = r"\w\d!#%&'~_`><@,:/\$\*\+\-\.\^\|\)\(\?\}\{\="
_LegalValueChars = _LegalKeyChars + '\[\]'
_CookiePattern = re.compile(r"""
    (?x)                           # This jest a verbose pattern
    \s*                            # Optional whitespace at start of cookie
    (?P<key>                       # Start of group 'key'
    [""" + _LegalKeyChars + r"""]+?   # Any word of at least one letter
    )                              # End of group 'key'
    (                              # Optional group: there may nie be a value.
    \s*=\s*                          # Equal Sign
    (?P<val>                         # Start of group 'val'
    "(?:[^\\"]|\\.)*"                  # Any doublequoted string
    |                                  # albo
    \w{3},\s[\w\d\s-]{9,11}\s[\d:]{8}\sGMT  # Special case dla "expires" attr
    |                                  # albo
    [""" + _LegalValueChars + r"""]*      # Any word albo empty string
    )                                # End of group 'val'
    )?                             # End of optional value group
    \s*                            # Any number of spaces.
    (\s+|;|$)                      # Ending either at space, semicolon, albo EOS.
    """, re.ASCII)                 # May be removed jeżeli safe.


# At long last, here jest the cookie class.  Using this klasa jest almost just like
# using a dictionary.  See this module's docstring dla example usage.
#
klasa BaseCookie(dict):
    """A container klasa dla a set of Morsels."""

    def value_decode(self, val):
        """real_value, coded_value = value_decode(STRING)
        Called prior to setting a cookie's value z the network
        representation.  The VALUE jest the value read z HTTP
        header.
        Override this function to modify the behavior of cookies.
        """
        zwróć val, val

    def value_encode(self, val):
        """real_value, coded_value = value_encode(VALUE)
        Called prior to setting a cookie's value z the dictionary
        representation.  The VALUE jest the value being assigned.
        Override this function to modify the behavior of cookies.
        """
        strval = str(val)
        zwróć strval, strval

    def __init__(self, input=Nic):
        jeżeli input:
            self.load(input)

    def __set(self, key, real_value, coded_value):
        """Private method dla setting a cookie's value"""
        M = self.get(key, Morsel())
        M.set(key, real_value, coded_value)
        dict.__setitem__(self, key, M)

    def __setitem__(self, key, value):
        """Dictionary style assignment."""
        jeżeli isinstance(value, Morsel):
            # allow assignment of constructed Morsels (e.g. dla pickling)
            dict.__setitem__(self, key, value)
        inaczej:
            rval, cval = self.value_encode(value)
            self.__set(key, rval, cval)

    def output(self, attrs=Nic, header="Set-Cookie:", sep="\015\012"):
        """Return a string suitable dla HTTP."""
        result = []
        items = sorted(self.items())
        dla key, value w items:
            result.append(value.output(attrs, header))
        zwróć sep.join(result)

    __str__ = output

    def __repr__(self):
        l = []
        items = sorted(self.items())
        dla key, value w items:
            l.append('%s=%s' % (key, repr(value.value)))
        zwróć '<%s: %s>' % (self.__class__.__name__, _spacejoin(l))

    def js_output(self, attrs=Nic):
        """Return a string suitable dla JavaScript."""
        result = []
        items = sorted(self.items())
        dla key, value w items:
            result.append(value.js_output(attrs))
        zwróć _nulljoin(result)

    def load(self, rawdata):
        """Load cookies z a string (presumably HTTP_COOKIE) albo
        z a dictionary.  Loading cookies z a dictionary 'd'
        jest equivalent to calling:
            map(Cookie.__setitem__, d.keys(), d.values())
        """
        jeżeli isinstance(rawdata, str):
            self.__parse_string(rawdata)
        inaczej:
            # self.update() wouldn't call our custom __setitem__
            dla key, value w rawdata.items():
                self[key] = value
        zwróć

    def __parse_string(self, str, patt=_CookiePattern):
        i = 0                 # Our starting point
        n = len(str)          # Length of string
        parsed_items = []     # Parsed (type, key, value) triples
        morsel_seen = Nieprawda   # A key=value pair was previously encountered

        TYPE_ATTRIBUTE = 1
        TYPE_KEYVALUE = 2

        # We first parse the whole cookie string oraz reject it jeżeli it's
        # syntactically invalid (this helps avoid some classes of injection
        # attacks).
        dopóki 0 <= i < n:
            # Start looking dla a cookie
            match = patt.match(str, i)
            jeżeli nie match:
                # No more cookies
                przerwij

            key, value = match.group("key"), match.group("val")
            i = match.end(0)

            jeżeli key[0] == "$":
                jeżeli nie morsel_seen:
                    # We ignore attributes which pertain to the cookie
                    # mechanism jako a whole, such jako "$Version".
                    # See RFC 2965. (Does anyone care?)
                    kontynuuj
                parsed_items.append((TYPE_ATTRIBUTE, key[1:], value))
            albo_inaczej key.lower() w Morsel._reserved:
                jeżeli nie morsel_seen:
                    # Invalid cookie string
                    zwróć
                jeżeli value jest Nic:
                    jeżeli key.lower() w Morsel._flags:
                        parsed_items.append((TYPE_ATTRIBUTE, key, Prawda))
                    inaczej:
                        # Invalid cookie string
                        zwróć
                inaczej:
                    parsed_items.append((TYPE_ATTRIBUTE, key, _unquote(value)))
            albo_inaczej value jest nie Nic:
                parsed_items.append((TYPE_KEYVALUE, key, self.value_decode(value)))
                morsel_seen = Prawda
            inaczej:
                # Invalid cookie string
                zwróć

        # The cookie string jest valid, apply it.
        M = Nic         # current morsel
        dla tp, key, value w parsed_items:
            jeżeli tp == TYPE_ATTRIBUTE:
                assert M jest nie Nic
                M[key] = value
            inaczej:
                assert tp == TYPE_KEYVALUE
                rval, cval = value
                self.__set(key, rval, cval)
                M = self[key]


klasa SimpleCookie(BaseCookie):
    """
    SimpleCookie supports strings jako cookie values.  When setting
    the value using the dictionary assignment notation, SimpleCookie
    calls the builtin str() to convert the value to a string.  Values
    received z HTTP are kept jako strings.
    """
    def value_decode(self, val):
        zwróć _unquote(val), val

    def value_encode(self, val):
        strval = str(val)
        zwróć strval, _quote(strval)
