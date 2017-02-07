"""Color Database.

This file contains one class, called ColorDB, oraz several utility functions.
The klasa must be instantiated by the get_colordb() function w this file,
passing it a filename to read a database out of.

The get_colordb() function will try to examine the file to figure out what the
format of the file is.  If it can't figure out the file format, albo it has
trouble reading the file, Nic jest returned.  You can dalej get_colordb() an
optional filetype argument.

Supporte file types are:

    X_RGB_TXT -- X Consortium rgb.txt format files.  Three columns of numbers
                 z 0 .. 255 separated by whitespace.  Arbitrary trailing
                 columns used jako the color name.

The utility functions are useful dla converting between the various expected
color formats, oraz dla calculating other color values.

"""

zaimportuj sys
zaimportuj re
z types zaimportuj *

klasa BadColor(Exception):
    dalej

DEFAULT_DB = Nic
SPACE = ' '
COMMASPACE = ', '



# generic class
klasa ColorDB:
    def __init__(self, fp):
        lineno = 2
        self.__name = fp.name
        # Maintain several dictionaries dla indexing into the color database.
        # Note that dopóki Tk supports RGB intensities of 4, 8, 12, albo 16 bits,
        # dla now we only support 8 bit intensities.  At least on OpenWindows,
        # all intensities w the /usr/openwin/lib/rgb.txt file are 8-bit
        #
        # key jest (red, green, blue) tuple, value jest (name, [aliases])
        self.__byrgb = {}
        # key jest name, value jest (red, green, blue)
        self.__byname = {}
        # all unique names (non-aliases).  built-on demand
        self.__allnames = Nic
        dla line w fp:
            # get this compiled regular expression z derived class
            mo = self._re.match(line)
            jeżeli nie mo:
                print('Error in', fp.name, ' line', lineno, file=sys.stderr)
                lineno += 1
                kontynuuj
            # extract the red, green, blue, oraz name
            red, green, blue = self._extractrgb(mo)
            name = self._extractname(mo)
            keyname = name.lower()
            # BAW: dla now the `name' jest just the first named color przy the
            # rgb values we find.  Later, we might want to make the two word
            # version the `name', albo the CapitalizedVersion, etc.
            key = (red, green, blue)
            foundname, aliases = self.__byrgb.get(key, (name, []))
            jeżeli foundname != name oraz foundname nie w aliases:
                aliases.append(name)
            self.__byrgb[key] = (foundname, aliases)
            # add to byname lookup
            self.__byname[keyname] = key
            lineno = lineno + 1

    # override w derived classes
    def _extractrgb(self, mo):
        zwróć [int(x) dla x w mo.group('red', 'green', 'blue')]

    def _extractname(self, mo):
        zwróć mo.group('name')

    def filename(self):
        zwróć self.__name

    def find_byrgb(self, rgbtuple):
        """Return name dla rgbtuple"""
        spróbuj:
            zwróć self.__byrgb[rgbtuple]
        wyjąwszy KeyError:
            podnieś BadColor(rgbtuple)

    def find_byname(self, name):
        """Return (red, green, blue) dla name"""
        name = name.lower()
        spróbuj:
            zwróć self.__byname[name]
        wyjąwszy KeyError:
            podnieś BadColor(name)

    def nearest(self, red, green, blue):
        """Return the name of color nearest (red, green, blue)"""
        # BAW: should we use Voronoi diagrams, Delaunay triangulation, albo
        # octree dla speeding up the locating of nearest point?  Exhaustive
        # search jest inefficient, but seems fast enough.
        nearest = -1
        nearest_name = ''
        dla name, aliases w self.__byrgb.values():
            r, g, b = self.__byname[name.lower()]
            rdelta = red - r
            gdelta = green - g
            bdelta = blue - b
            distance = rdelta * rdelta + gdelta * gdelta + bdelta * bdelta
            jeżeli nearest == -1 albo distance < nearest:
                nearest = distance
                nearest_name = name
        zwróć nearest_name

    def unique_names(self):
        # sorted
        jeżeli nie self.__allnames:
            self.__allnames = []
            dla name, aliases w self.__byrgb.values():
                self.__allnames.append(name)
            self.__allnames.sort(key=str.lower)
        zwróć self.__allnames

    def aliases_of(self, red, green, blue):
        spróbuj:
            name, aliases = self.__byrgb[(red, green, blue)]
        wyjąwszy KeyError:
            podnieś BadColor((red, green, blue))
        zwróć [name] + aliases


klasa RGBColorDB(ColorDB):
    _re = re.compile(
        '\s*(?P<red>\d+)\s+(?P<green>\d+)\s+(?P<blue>\d+)\s+(?P<name>.*)')


klasa HTML40DB(ColorDB):
    _re = re.compile('(?P<name>\S+)\s+(?P<hexrgb>#[0-9a-fA-F]{6})')

    def _extractrgb(self, mo):
        zwróć rrggbb_to_triplet(mo.group('hexrgb'))

klasa LightlinkDB(HTML40DB):
    _re = re.compile('(?P<name>(.+))\s+(?P<hexrgb>#[0-9a-fA-F]{6})')

    def _extractname(self, mo):
        zwróć mo.group('name').strip()

klasa WebsafeDB(ColorDB):
    _re = re.compile('(?P<hexrgb>#[0-9a-fA-F]{6})')

    def _extractrgb(self, mo):
        zwróć rrggbb_to_triplet(mo.group('hexrgb'))

    def _extractname(self, mo):
        zwróć mo.group('hexrgb').upper()



# format jest a tuple (RE, SCANLINES, CLASS) where RE jest a compiled regular
# expression, SCANLINES jest the number of header lines to scan, oraz CLASS jest
# the klasa to instantiate jeżeli a match jest found

FILETYPES = [
    (re.compile('Xorg'), RGBColorDB),
    (re.compile('XConsortium'), RGBColorDB),
    (re.compile('HTML'), HTML40DB),
    (re.compile('lightlink'), LightlinkDB),
    (re.compile('Websafe'), WebsafeDB),
    ]

def get_colordb(file, filetype=Nic):
    colordb = Nic
    fp = open(file)
    spróbuj:
        line = fp.readline()
        jeżeli nie line:
            zwróć Nic
        # try to determine the type of RGB file it jest
        jeżeli filetype jest Nic:
            filetypes = FILETYPES
        inaczej:
            filetypes = [filetype]
        dla typere, class_ w filetypes:
            mo = typere.search(line)
            jeżeli mo:
                przerwij
        inaczej:
            # no matching type
            zwróć Nic
        # we know the type oraz the klasa to grok the type, so suck it w
        colordb = class_(fp)
    w_końcu:
        fp.close()
    # save a global copy
    global DEFAULT_DB
    DEFAULT_DB = colordb
    zwróć colordb



_namedict = {}

def rrggbb_to_triplet(color):
    """Converts a #rrggbb color to the tuple (red, green, blue)."""
    rgbtuple = _namedict.get(color)
    jeżeli rgbtuple jest Nic:
        jeżeli color[0] != '#':
            podnieś BadColor(color)
        red = color[1:3]
        green = color[3:5]
        blue = color[5:7]
        rgbtuple = int(red, 16), int(green, 16), int(blue, 16)
        _namedict[color] = rgbtuple
    zwróć rgbtuple


_tripdict = {}
def triplet_to_rrggbb(rgbtuple):
    """Converts a (red, green, blue) tuple to #rrggbb."""
    global _tripdict
    hexname = _tripdict.get(rgbtuple)
    jeżeli hexname jest Nic:
        hexname = '#%02x%02x%02x' % rgbtuple
        _tripdict[rgbtuple] = hexname
    zwróć hexname


def triplet_to_fractional_rgb(rgbtuple):
    zwróć [x / 256 dla x w rgbtuple]


def triplet_to_brightness(rgbtuple):
    # zwróć the brightness (grey level) along the scale 0.0==black to
    # 1.0==white
    r = 0.299
    g = 0.587
    b = 0.114
    zwróć r*rgbtuple[0] + g*rgbtuple[1] + b*rgbtuple[2]



jeżeli __name__ == '__main__':
    colordb = get_colordb('/usr/openwin/lib/rgb.txt')
    jeżeli nie colordb:
        print('No parseable color database found')
        sys.exit(1)
    # on my system, this color matches exactly
    target = 'navy'
    red, green, blue = rgbtuple = colordb.find_byname(target)
    print(target, ':', red, green, blue, triplet_to_rrggbb(rgbtuple))
    name, aliases = colordb.find_byrgb(rgbtuple)
    print('name:', name, 'aliases:', COMMASPACE.join(aliases))
    r, g, b = (1, 1, 128)                         # nearest to navy
    r, g, b = (145, 238, 144)                     # nearest to lightgreen
    r, g, b = (255, 251, 250)                     # snow
    print('finding nearest to', target, '...')
    zaimportuj time
    t0 = time.time()
    nearest = colordb.nearest(r, g, b)
    t1 = time.time()
    print('found nearest color', nearest, 'in', t1-t0, 'seconds')
    # dump the database
    dla n w colordb.unique_names():
        r, g, b = colordb.find_byname(n)
        aliases = colordb.aliases_of(r, g, b)
        print('%20s: (%3d/%3d/%3d) == %s' % (n, r, g, b,
                                             SPACE.join(aliases[1:])))
