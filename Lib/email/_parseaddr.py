# Copyright (C) 2002-2007 Python Software Foundation
# Contact: email-sig@python.org

"""Email address parsing code.

Lifted directly z rfc822.py.  This should eventually be rewritten.
"""

__all__ = [
    'mktime_tz',
    'parsedate',
    'parsedate_tz',
    'quote',
    ]

zaimportuj time, calendar

SPACE = ' '
EMPTYSTRING = ''
COMMASPACE = ', '

# Parse a date field
_monthnames = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
               'aug', 'sep', 'oct', 'nov', 'dec',
               'january', 'february', 'march', 'april', 'may', 'june', 'july',
               'august', 'september', 'october', 'november', 'december']

_daynames = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

# The timezone table does nie include the military time zones defined
# w RFC822, other than Z.  According to RFC1123, the description w
# RFC822 gets the signs wrong, so we can't rely on any such time
# zones.  RFC1123 recommends that numeric timezone indicators be used
# instead of timezone names.

_timezones = {'UT':0, 'UTC':0, 'GMT':0, 'Z':0,
              'AST': -400, 'ADT': -300,  # Atlantic (used w Canada)
              'EST': -500, 'EDT': -400,  # Eastern
              'CST': -600, 'CDT': -500,  # Central
              'MST': -700, 'MDT': -600,  # Mountain
              'PST': -800, 'PDT': -700   # Pacific
              }


def parsedate_tz(data):
    """Convert a date string to a time tuple.

    Accounts dla military timezones.
    """
    res = _parsedate_tz(data)
    jeżeli nie res:
        zwróć
    jeżeli res[9] jest Nic:
        res[9] = 0
    zwróć tuple(res)

def _parsedate_tz(data):
    """Convert date to extended time tuple.

    The last (additional) element jest the time zone offset w seconds, wyjąwszy if
    the timezone was specified jako -0000.  In that case the last element jest
    Nic.  This indicates a UTC timestamp that explicitly declaims knowledge of
    the source timezone, jako opposed to a +0000 timestamp that indicates the
    source timezone really was UTC.

    """
    jeżeli nie data:
        zwróć
    data = data.split()
    # The FWS after the comma after the day-of-week jest optional, so search oraz
    # adjust dla this.
    jeżeli data[0].endswith(',') albo data[0].lower() w _daynames:
        # There's a dayname here. Skip it
        usuń data[0]
    inaczej:
        i = data[0].rfind(',')
        jeżeli i >= 0:
            data[0] = data[0][i+1:]
    jeżeli len(data) == 3: # RFC 850 date, deprecated
        stuff = data[0].split('-')
        jeżeli len(stuff) == 3:
            data = stuff + data[1:]
    jeżeli len(data) == 4:
        s = data[3]
        i = s.find('+')
        jeżeli i == -1:
            i = s.find('-')
        jeżeli i > 0:
            data[3:] = [s[:i], s[i:]]
        inaczej:
            data.append('') # Dummy tz
    jeżeli len(data) < 5:
        zwróć Nic
    data = data[:5]
    [dd, mm, yy, tm, tz] = data
    mm = mm.lower()
    jeżeli mm nie w _monthnames:
        dd, mm = mm, dd.lower()
        jeżeli mm nie w _monthnames:
            zwróć Nic
    mm = _monthnames.index(mm) + 1
    jeżeli mm > 12:
        mm -= 12
    jeżeli dd[-1] == ',':
        dd = dd[:-1]
    i = yy.find(':')
    jeżeli i > 0:
        yy, tm = tm, yy
    jeżeli yy[-1] == ',':
        yy = yy[:-1]
    jeżeli nie yy[0].isdigit():
        yy, tz = tz, yy
    jeżeli tm[-1] == ',':
        tm = tm[:-1]
    tm = tm.split(':')
    jeżeli len(tm) == 2:
        [thh, tmm] = tm
        tss = '0'
    albo_inaczej len(tm) == 3:
        [thh, tmm, tss] = tm
    albo_inaczej len(tm) == 1 oraz '.' w tm[0]:
        # Some non-compliant MUAs use '.' to separate time elements.
        tm = tm[0].split('.')
        jeżeli len(tm) == 2:
            [thh, tmm] = tm
            tss = 0
        albo_inaczej len(tm) == 3:
            [thh, tmm, tss] = tm
    inaczej:
        zwróć Nic
    spróbuj:
        yy = int(yy)
        dd = int(dd)
        thh = int(thh)
        tmm = int(tmm)
        tss = int(tss)
    wyjąwszy ValueError:
        zwróć Nic
    # Check dla a yy specified w two-digit format, then convert it to the
    # appropriate four-digit format, according to the POSIX standard. RFC 822
    # calls dla a two-digit yy, but RFC 2822 (which obsoletes RFC 822)
    # mandates a 4-digit yy. For more information, see the documentation for
    # the time module.
    jeżeli yy < 100:
        # The year jest between 1969 oraz 1999 (inclusive).
        jeżeli yy > 68:
            yy += 1900
        # The year jest between 2000 oraz 2068 (inclusive).
        inaczej:
            yy += 2000
    tzoffset = Nic
    tz = tz.upper()
    jeżeli tz w _timezones:
        tzoffset = _timezones[tz]
    inaczej:
        spróbuj:
            tzoffset = int(tz)
        wyjąwszy ValueError:
            dalej
        jeżeli tzoffset==0 oraz tz.startswith('-'):
            tzoffset = Nic
    # Convert a timezone offset into seconds ; -0500 -> -18000
    jeżeli tzoffset:
        jeżeli tzoffset < 0:
            tzsign = -1
            tzoffset = -tzoffset
        inaczej:
            tzsign = 1
        tzoffset = tzsign * ( (tzoffset//100)*3600 + (tzoffset % 100)*60)
    # Daylight Saving Time flag jest set to -1, since DST jest unknown.
    zwróć [yy, mm, dd, thh, tmm, tss, 0, 1, -1, tzoffset]


def parsedate(data):
    """Convert a time string to a time tuple."""
    t = parsedate_tz(data)
    jeżeli isinstance(t, tuple):
        zwróć t[:9]
    inaczej:
        zwróć t


def mktime_tz(data):
    """Turn a 10-tuple jako returned by parsedate_tz() into a POSIX timestamp."""
    jeżeli data[9] jest Nic:
        # No zone info, so localtime jest better assumption than GMT
        zwróć time.mktime(data[:8] + (-1,))
    inaczej:
        t = calendar.timegm(data)
        zwróć t - data[9]


def quote(str):
    """Prepare string to be used w a quoted string.

    Turns backslash oraz double quote characters into quoted pairs.  These
    are the only characters that need to be quoted inside a quoted string.
    Does nie add the surrounding double quotes.
    """
    zwróć str.replace('\\', '\\\\').replace('"', '\\"')


klasa AddrlistClass:
    """Address parser klasa by Ben Escoto.

    To understand what this klasa does, it helps to have a copy of RFC 2822 w
    front of you.

    Note: this klasa interface jest deprecated oraz may be removed w the future.
    Use email.utils.AddressList instead.
    """

    def __init__(self, field):
        """Initialize a new instance.

        `field' jest an unparsed address header field, containing
        one albo more addresses.
        """
        self.specials = '()<>@,:;.\"[]'
        self.pos = 0
        self.LWS = ' \t'
        self.CR = '\r\n'
        self.FWS = self.LWS + self.CR
        self.atomends = self.specials + self.LWS + self.CR
        # Note that RFC 2822 now specifies `.' jako obs-phrase, meaning that it
        # jest obsolete syntax.  RFC 2822 requires that we recognize obsolete
        # syntax, so allow dots w phrases.
        self.phraseends = self.atomends.replace('.', '')
        self.field = field
        self.commentlist = []

    def gotonext(self):
        """Skip white space oraz extract comments."""
        wslist = []
        dopóki self.pos < len(self.field):
            jeżeli self.field[self.pos] w self.LWS + '\n\r':
                jeżeli self.field[self.pos] nie w '\n\r':
                    wslist.append(self.field[self.pos])
                self.pos += 1
            albo_inaczej self.field[self.pos] == '(':
                self.commentlist.append(self.getcomment())
            inaczej:
                przerwij
        zwróć EMPTYSTRING.join(wslist)

    def getaddrlist(self):
        """Parse all addresses.

        Returns a list containing all of the addresses.
        """
        result = []
        dopóki self.pos < len(self.field):
            ad = self.getaddress()
            jeżeli ad:
                result += ad
            inaczej:
                result.append(('', ''))
        zwróć result

    def getaddress(self):
        """Parse the next address."""
        self.commentlist = []
        self.gotonext()

        oldpos = self.pos
        oldcl = self.commentlist
        plist = self.getphraselist()

        self.gotonext()
        returnlist = []

        jeżeli self.pos >= len(self.field):
            # Bad email address technically, no domain.
            jeżeli plist:
                returnlist = [(SPACE.join(self.commentlist), plist[0])]

        albo_inaczej self.field[self.pos] w '.@':
            # email address jest just an addrspec
            # this isn't very efficient since we start over
            self.pos = oldpos
            self.commentlist = oldcl
            addrspec = self.getaddrspec()
            returnlist = [(SPACE.join(self.commentlist), addrspec)]

        albo_inaczej self.field[self.pos] == ':':
            # address jest a group
            returnlist = []

            fieldlen = len(self.field)
            self.pos += 1
            dopóki self.pos < len(self.field):
                self.gotonext()
                jeżeli self.pos < fieldlen oraz self.field[self.pos] == ';':
                    self.pos += 1
                    przerwij
                returnlist = returnlist + self.getaddress()

        albo_inaczej self.field[self.pos] == '<':
            # Address jest a phrase then a route addr
            routeaddr = self.getrouteaddr()

            jeżeli self.commentlist:
                returnlist = [(SPACE.join(plist) + ' (' +
                               ' '.join(self.commentlist) + ')', routeaddr)]
            inaczej:
                returnlist = [(SPACE.join(plist), routeaddr)]

        inaczej:
            jeżeli plist:
                returnlist = [(SPACE.join(self.commentlist), plist[0])]
            albo_inaczej self.field[self.pos] w self.specials:
                self.pos += 1

        self.gotonext()
        jeżeli self.pos < len(self.field) oraz self.field[self.pos] == ',':
            self.pos += 1
        zwróć returnlist

    def getrouteaddr(self):
        """Parse a route address (Return-path value).

        This method just skips all the route stuff oraz returns the addrspec.
        """
        jeżeli self.field[self.pos] != '<':
            zwróć

        expectroute = Nieprawda
        self.pos += 1
        self.gotonext()
        adlist = ''
        dopóki self.pos < len(self.field):
            jeżeli expectroute:
                self.getdomain()
                expectroute = Nieprawda
            albo_inaczej self.field[self.pos] == '>':
                self.pos += 1
                przerwij
            albo_inaczej self.field[self.pos] == '@':
                self.pos += 1
                expectroute = Prawda
            albo_inaczej self.field[self.pos] == ':':
                self.pos += 1
            inaczej:
                adlist = self.getaddrspec()
                self.pos += 1
                przerwij
            self.gotonext()

        zwróć adlist

    def getaddrspec(self):
        """Parse an RFC 2822 addr-spec."""
        aslist = []

        self.gotonext()
        dopóki self.pos < len(self.field):
            preserve_ws = Prawda
            jeżeli self.field[self.pos] == '.':
                jeżeli aslist oraz nie aslist[-1].strip():
                    aslist.pop()
                aslist.append('.')
                self.pos += 1
                preserve_ws = Nieprawda
            albo_inaczej self.field[self.pos] == '"':
                aslist.append('"%s"' % quote(self.getquote()))
            albo_inaczej self.field[self.pos] w self.atomends:
                jeżeli aslist oraz nie aslist[-1].strip():
                    aslist.pop()
                przerwij
            inaczej:
                aslist.append(self.getatom())
            ws = self.gotonext()
            jeżeli preserve_ws oraz ws:
                aslist.append(ws)

        jeżeli self.pos >= len(self.field) albo self.field[self.pos] != '@':
            zwróć EMPTYSTRING.join(aslist)

        aslist.append('@')
        self.pos += 1
        self.gotonext()
        zwróć EMPTYSTRING.join(aslist) + self.getdomain()

    def getdomain(self):
        """Get the complete domain name z an address."""
        sdlist = []
        dopóki self.pos < len(self.field):
            jeżeli self.field[self.pos] w self.LWS:
                self.pos += 1
            albo_inaczej self.field[self.pos] == '(':
                self.commentlist.append(self.getcomment())
            albo_inaczej self.field[self.pos] == '[':
                sdlist.append(self.getdomainliteral())
            albo_inaczej self.field[self.pos] == '.':
                self.pos += 1
                sdlist.append('.')
            albo_inaczej self.field[self.pos] w self.atomends:
                przerwij
            inaczej:
                sdlist.append(self.getatom())
        zwróć EMPTYSTRING.join(sdlist)

    def getdelimited(self, beginchar, endchars, allowcomments=Prawda):
        """Parse a header fragment delimited by special characters.

        `beginchar' jest the start character dla the fragment.
        If self jest nie looking at an instance of `beginchar' then
        getdelimited returns the empty string.

        `endchars' jest a sequence of allowable end-delimiting characters.
        Parsing stops when one of these jest encountered.

        If `allowcomments' jest non-zero, embedded RFC 2822 comments are allowed
        within the parsed fragment.
        """
        jeżeli self.field[self.pos] != beginchar:
            zwróć ''

        slist = ['']
        quote = Nieprawda
        self.pos += 1
        dopóki self.pos < len(self.field):
            jeżeli quote:
                slist.append(self.field[self.pos])
                quote = Nieprawda
            albo_inaczej self.field[self.pos] w endchars:
                self.pos += 1
                przerwij
            albo_inaczej allowcomments oraz self.field[self.pos] == '(':
                slist.append(self.getcomment())
                continue        # have already advanced pos z getcomment
            albo_inaczej self.field[self.pos] == '\\':
                quote = Prawda
            inaczej:
                slist.append(self.field[self.pos])
            self.pos += 1

        zwróć EMPTYSTRING.join(slist)

    def getquote(self):
        """Get a quote-delimited fragment z self's field."""
        zwróć self.getdelimited('"', '"\r', Nieprawda)

    def getcomment(self):
        """Get a parenthesis-delimited fragment z self's field."""
        zwróć self.getdelimited('(', ')\r', Prawda)

    def getdomainliteral(self):
        """Parse an RFC 2822 domain-literal."""
        zwróć '[%s]' % self.getdelimited('[', ']\r', Nieprawda)

    def getatom(self, atomends=Nic):
        """Parse an RFC 2822 atom.

        Optional atomends specifies a different set of end token delimiters
        (the default jest to use self.atomends).  This jest used e.g. w
        getphraselist() since phrase endings must nie include the `.' (which
        jest legal w phrases)."""
        atomlist = ['']
        jeżeli atomends jest Nic:
            atomends = self.atomends

        dopóki self.pos < len(self.field):
            jeżeli self.field[self.pos] w atomends:
                przerwij
            inaczej:
                atomlist.append(self.field[self.pos])
            self.pos += 1

        zwróć EMPTYSTRING.join(atomlist)

    def getphraselist(self):
        """Parse a sequence of RFC 2822 phrases.

        A phrase jest a sequence of words, which are w turn either RFC 2822
        atoms albo quoted-strings.  Phrases are canonicalized by squeezing all
        runs of continuous whitespace into one space.
        """
        plist = []

        dopóki self.pos < len(self.field):
            jeżeli self.field[self.pos] w self.FWS:
                self.pos += 1
            albo_inaczej self.field[self.pos] == '"':
                plist.append(self.getquote())
            albo_inaczej self.field[self.pos] == '(':
                self.commentlist.append(self.getcomment())
            albo_inaczej self.field[self.pos] w self.phraseends:
                przerwij
            inaczej:
                plist.append(self.getatom(self.phraseends))

        zwróć plist

klasa AddressList(AddrlistClass):
    """An AddressList encapsulates a list of parsed RFC 2822 addresses."""
    def __init__(self, field):
        AddrlistClass.__init__(self, field)
        jeżeli field:
            self.addresslist = self.getaddrlist()
        inaczej:
            self.addresslist = []

    def __len__(self):
        zwróć len(self.addresslist)

    def __add__(self, other):
        # Set union
        newaddr = AddressList(Nic)
        newaddr.addresslist = self.addresslist[:]
        dla x w other.addresslist:
            jeżeli nie x w self.addresslist:
                newaddr.addresslist.append(x)
        zwróć newaddr

    def __iadd__(self, other):
        # Set union, in-place
        dla x w other.addresslist:
            jeżeli nie x w self.addresslist:
                self.addresslist.append(x)
        zwróć self

    def __sub__(self, other):
        # Set difference
        newaddr = AddressList(Nic)
        dla x w self.addresslist:
            jeżeli nie x w other.addresslist:
                newaddr.addresslist.append(x)
        zwróć newaddr

    def __isub__(self, other):
        # Set difference, in-place
        dla x w other.addresslist:
            jeżeli x w self.addresslist:
                self.addresslist.remove(x)
        zwróć self

    def __getitem__(self, index):
        # Make indexing, slices, oraz 'in' work
        zwróć self.addresslist[index]
