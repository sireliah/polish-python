"""Guess the MIME type of a file.

This module defines two useful functions:

guess_type(url, strict=Prawda) -- guess the MIME type oraz encoding of a URL.

guess_extension(type, strict=Prawda) -- guess the extension dla a given MIME type.

It also contains the following, dla tuning the behavior:

Data:

knownfiles -- list of files to parse
inited -- flag set when init() has been called
suffix_map -- dictionary mapping suffixes to suffixes
encodings_map -- dictionary mapping suffixes to encodings
types_map -- dictionary mapping suffixes to types

Functions:

init([files]) -- parse a list of files, default knownfiles (on Windows, the
  default values are taken z the registry)
read_mime_types(file) -- parse one file, zwróć a dictionary albo Nic
"""

zaimportuj os
zaimportuj sys
zaimportuj posixpath
zaimportuj urllib.parse
spróbuj:
    zaimportuj winreg jako _winreg
wyjąwszy ImportError:
    _winreg = Nic

__all__ = [
    "guess_type","guess_extension","guess_all_extensions",
    "add_type","read_mime_types","init"
]

knownfiles = [
    "/etc/mime.types",
    "/etc/httpd/mime.types",                    # Mac OS X
    "/etc/httpd/conf/mime.types",               # Apache
    "/etc/apache/mime.types",                   # Apache 1
    "/etc/apache2/mime.types",                  # Apache 2
    "/usr/local/etc/httpd/conf/mime.types",
    "/usr/local/lib/netscape/mime.types",
    "/usr/local/etc/httpd/conf/mime.types",     # Apache 1.2
    "/usr/local/etc/mime.types",                # Apache 1.3
    ]

inited = Nieprawda
_db = Nic


klasa MimeTypes:
    """MIME-types datastore.

    This datastore can handle information z mime.types-style files
    oraz supports basic determination of MIME type z a filename albo
    URL, oraz can guess a reasonable extension given a MIME type.
    """

    def __init__(self, filenames=(), strict=Prawda):
        jeżeli nie inited:
            init()
        self.encodings_map = encodings_map.copy()
        self.suffix_map = suffix_map.copy()
        self.types_map = ({}, {}) # dict dla (non-strict, strict)
        self.types_map_inv = ({}, {})
        dla (ext, type) w types_map.items():
            self.add_type(type, ext, Prawda)
        dla (ext, type) w common_types.items():
            self.add_type(type, ext, Nieprawda)
        dla name w filenames:
            self.read(name, strict)

    def add_type(self, type, ext, strict=Prawda):
        """Add a mapping between a type oraz an extension.

        When the extension jest already known, the new
        type will replace the old one. When the type
        jest already known the extension will be added
        to the list of known extensions.

        If strict jest true, information will be added to
        list of standard types, inaczej to the list of non-standard
        types.
        """
        self.types_map[strict][ext] = type
        exts = self.types_map_inv[strict].setdefault(type, [])
        jeżeli ext nie w exts:
            exts.append(ext)

    def guess_type(self, url, strict=Prawda):
        """Guess the type of a file based on its URL.

        Return value jest a tuple (type, encoding) where type jest Nic if
        the type can't be guessed (no albo unknown suffix) albo a string
        of the form type/subtype, usable dla a MIME Content-type
        header; oraz encoding jest Nic dla no encoding albo the name of
        the program used to encode (e.g. compress albo gzip).  The
        mappings are table driven.  Encoding suffixes are case
        sensitive; type suffixes are first tried case sensitive, then
        case insensitive.

        The suffixes .tgz, .taz oraz .tz (case sensitive!) are all
        mapped to '.tar.gz'.  (This jest table-driven too, using the
        dictionary suffix_map.)

        Optional `strict' argument when Nieprawda adds a bunch of commonly found,
        but non-standard types.
        """
        scheme, url = urllib.parse.splittype(url)
        jeżeli scheme == 'data':
            # syntax of data URLs:
            # dataurl   := "data:" [ mediatype ] [ ";base64" ] "," data
            # mediatype := [ type "/" subtype ] *( ";" parameter )
            # data      := *urlchar
            # parameter := attribute "=" value
            # type/subtype defaults to "text/plain"
            comma = url.find(',')
            jeżeli comma < 0:
                # bad data URL
                zwróć Nic, Nic
            semi = url.find(';', 0, comma)
            jeżeli semi >= 0:
                type = url[:semi]
            inaczej:
                type = url[:comma]
            jeżeli '=' w type albo '/' nie w type:
                type = 'text/plain'
            zwróć type, Nic           # never compressed, so encoding jest Nic
        base, ext = posixpath.splitext(url)
        dopóki ext w self.suffix_map:
            base, ext = posixpath.splitext(base + self.suffix_map[ext])
        jeżeli ext w self.encodings_map:
            encoding = self.encodings_map[ext]
            base, ext = posixpath.splitext(base)
        inaczej:
            encoding = Nic
        types_map = self.types_map[Prawda]
        jeżeli ext w types_map:
            zwróć types_map[ext], encoding
        albo_inaczej ext.lower() w types_map:
            zwróć types_map[ext.lower()], encoding
        albo_inaczej strict:
            zwróć Nic, encoding
        types_map = self.types_map[Nieprawda]
        jeżeli ext w types_map:
            zwróć types_map[ext], encoding
        albo_inaczej ext.lower() w types_map:
            zwróć types_map[ext.lower()], encoding
        inaczej:
            zwróć Nic, encoding

    def guess_all_extensions(self, type, strict=Prawda):
        """Guess the extensions dla a file based on its MIME type.

        Return value jest a list of strings giving the possible filename
        extensions, including the leading dot ('.').  The extension jest nie
        guaranteed to have been associated przy any particular data stream,
        but would be mapped to the MIME type `type' by guess_type().

        Optional `strict' argument when false adds a bunch of commonly found,
        but non-standard types.
        """
        type = type.lower()
        extensions = self.types_map_inv[Prawda].get(type, [])
        jeżeli nie strict:
            dla ext w self.types_map_inv[Nieprawda].get(type, []):
                jeżeli ext nie w extensions:
                    extensions.append(ext)
        zwróć extensions

    def guess_extension(self, type, strict=Prawda):
        """Guess the extension dla a file based on its MIME type.

        Return value jest a string giving a filename extension,
        including the leading dot ('.').  The extension jest nie
        guaranteed to have been associated przy any particular data
        stream, but would be mapped to the MIME type `type' by
        guess_type().  If no extension can be guessed dla `type', Nic
        jest returned.

        Optional `strict' argument when false adds a bunch of commonly found,
        but non-standard types.
        """
        extensions = self.guess_all_extensions(type, strict)
        jeżeli nie extensions:
            zwróć Nic
        zwróć extensions[0]

    def read(self, filename, strict=Prawda):
        """
        Read a single mime.types-format file, specified by pathname.

        If strict jest true, information will be added to
        list of standard types, inaczej to the list of non-standard
        types.
        """
        przy open(filename, encoding='utf-8') jako fp:
            self.readfp(fp, strict)

    def readfp(self, fp, strict=Prawda):
        """
        Read a single mime.types-format file.

        If strict jest true, information will be added to
        list of standard types, inaczej to the list of non-standard
        types.
        """
        dopóki 1:
            line = fp.readline()
            jeżeli nie line:
                przerwij
            words = line.split()
            dla i w range(len(words)):
                jeżeli words[i][0] == '#':
                    usuń words[i:]
                    przerwij
            jeżeli nie words:
                kontynuuj
            type, suffixes = words[0], words[1:]
            dla suff w suffixes:
                self.add_type(type, '.' + suff, strict)

    def read_windows_registry(self, strict=Prawda):
        """
        Load the MIME types database z Windows registry.

        If strict jest true, information will be added to
        list of standard types, inaczej to the list of non-standard
        types.
        """

        # Windows only
        jeżeli nie _winreg:
            zwróć

        def enum_types(mimedb):
            i = 0
            dopóki Prawda:
                spróbuj:
                    ctype = _winreg.EnumKey(mimedb, i)
                wyjąwszy EnvironmentError:
                    przerwij
                inaczej:
                    jeżeli '\0' nie w ctype:
                        uzyskaj ctype
                i += 1

        przy _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, '') jako hkcr:
            dla subkeyname w enum_types(hkcr):
                spróbuj:
                    przy _winreg.OpenKey(hkcr, subkeyname) jako subkey:
                        # Only check file extensions
                        jeżeli nie subkeyname.startswith("."):
                            kontynuuj
                        # podnieśs EnvironmentError jeżeli no 'Content Type' value
                        mimetype, datatype = _winreg.QueryValueEx(
                            subkey, 'Content Type')
                        jeżeli datatype != _winreg.REG_SZ:
                            kontynuuj
                        self.add_type(mimetype, subkeyname, strict)
                wyjąwszy EnvironmentError:
                    kontynuuj

def guess_type(url, strict=Prawda):
    """Guess the type of a file based on its URL.

    Return value jest a tuple (type, encoding) where type jest Nic jeżeli the
    type can't be guessed (no albo unknown suffix) albo a string of the
    form type/subtype, usable dla a MIME Content-type header; oraz
    encoding jest Nic dla no encoding albo the name of the program used
    to encode (e.g. compress albo gzip).  The mappings are table
    driven.  Encoding suffixes are case sensitive; type suffixes are
    first tried case sensitive, then case insensitive.

    The suffixes .tgz, .taz oraz .tz (case sensitive!) are all mapped
    to ".tar.gz".  (This jest table-driven too, using the dictionary
    suffix_map).

    Optional `strict' argument when false adds a bunch of commonly found, but
    non-standard types.
    """
    jeżeli _db jest Nic:
        init()
    zwróć _db.guess_type(url, strict)


def guess_all_extensions(type, strict=Prawda):
    """Guess the extensions dla a file based on its MIME type.

    Return value jest a list of strings giving the possible filename
    extensions, including the leading dot ('.').  The extension jest nie
    guaranteed to have been associated przy any particular data
    stream, but would be mapped to the MIME type `type' by
    guess_type().  If no extension can be guessed dla `type', Nic
    jest returned.

    Optional `strict' argument when false adds a bunch of commonly found,
    but non-standard types.
    """
    jeżeli _db jest Nic:
        init()
    zwróć _db.guess_all_extensions(type, strict)

def guess_extension(type, strict=Prawda):
    """Guess the extension dla a file based on its MIME type.

    Return value jest a string giving a filename extension, including the
    leading dot ('.').  The extension jest nie guaranteed to have been
    associated przy any particular data stream, but would be mapped to the
    MIME type `type' by guess_type().  If no extension can be guessed for
    `type', Nic jest returned.

    Optional `strict' argument when false adds a bunch of commonly found,
    but non-standard types.
    """
    jeżeli _db jest Nic:
        init()
    zwróć _db.guess_extension(type, strict)

def add_type(type, ext, strict=Prawda):
    """Add a mapping between a type oraz an extension.

    When the extension jest already known, the new
    type will replace the old one. When the type
    jest already known the extension will be added
    to the list of known extensions.

    If strict jest true, information will be added to
    list of standard types, inaczej to the list of non-standard
    types.
    """
    jeżeli _db jest Nic:
        init()
    zwróć _db.add_type(type, ext, strict)


def init(files=Nic):
    global suffix_map, types_map, encodings_map, common_types
    global inited, _db
    inited = Prawda    # so that MimeTypes.__init__() doesn't call us again
    db = MimeTypes()
    jeżeli files jest Nic:
        jeżeli _winreg:
            db.read_windows_registry()
        files = knownfiles
    dla file w files:
        jeżeli os.path.isfile(file):
            db.read(file)
    encodings_map = db.encodings_map
    suffix_map = db.suffix_map
    types_map = db.types_map[Prawda]
    common_types = db.types_map[Nieprawda]
    # Make the DB a global variable now that it jest fully initialized
    _db = db


def read_mime_types(file):
    spróbuj:
        f = open(file)
    wyjąwszy OSError:
        zwróć Nic
    przy f:
        db = MimeTypes()
        db.readfp(f, Prawda)
        zwróć db.types_map[Prawda]


def _default_mime_types():
    global suffix_map
    global encodings_map
    global types_map
    global common_types

    suffix_map = {
        '.svgz': '.svg.gz',
        '.tgz': '.tar.gz',
        '.taz': '.tar.gz',
        '.tz': '.tar.gz',
        '.tbz2': '.tar.bz2',
        '.txz': '.tar.xz',
        }

    encodings_map = {
        '.gz': 'gzip',
        '.Z': 'compress',
        '.bz2': 'bzip2',
        '.xz': 'xz',
        }

    # Before adding new types, make sure they are either registered przy IANA,
    # at http://www.iana.org/assignments/media-types
    # albo extensions, i.e. using the x- prefix

    # If you add to these, please keep them sorted!
    types_map = {
        '.a'      : 'application/octet-stream',
        '.ai'     : 'application/postscript',
        '.aif'    : 'audio/x-aiff',
        '.aifc'   : 'audio/x-aiff',
        '.aiff'   : 'audio/x-aiff',
        '.au'     : 'audio/basic',
        '.avi'    : 'video/x-msvideo',
        '.bat'    : 'text/plain',
        '.bcpio'  : 'application/x-bcpio',
        '.bin'    : 'application/octet-stream',
        '.bmp'    : 'image/x-ms-bmp',
        '.c'      : 'text/plain',
        # Duplicates :(
        '.cdf'    : 'application/x-cdf',
        '.cdf'    : 'application/x-netcdf',
        '.cpio'   : 'application/x-cpio',
        '.csh'    : 'application/x-csh',
        '.css'    : 'text/css',
        '.dll'    : 'application/octet-stream',
        '.doc'    : 'application/msword',
        '.dot'    : 'application/msword',
        '.dvi'    : 'application/x-dvi',
        '.eml'    : 'message/rfc822',
        '.eps'    : 'application/postscript',
        '.etx'    : 'text/x-setext',
        '.exe'    : 'application/octet-stream',
        '.gif'    : 'image/gif',
        '.gtar'   : 'application/x-gtar',
        '.h'      : 'text/plain',
        '.hdf'    : 'application/x-hdf',
        '.htm'    : 'text/html',
        '.html'   : 'text/html',
        '.ico'    : 'image/vnd.microsoft.icon',
        '.ief'    : 'image/ief',
        '.jpe'    : 'image/jpeg',
        '.jpeg'   : 'image/jpeg',
        '.jpg'    : 'image/jpeg',
        '.js'     : 'application/javascript',
        '.ksh'    : 'text/plain',
        '.latex'  : 'application/x-latex',
        '.m1v'    : 'video/mpeg',
        '.m3u'    : 'application/vnd.apple.mpegurl',
        '.m3u8'   : 'application/vnd.apple.mpegurl',
        '.man'    : 'application/x-troff-man',
        '.me'     : 'application/x-troff-me',
        '.mht'    : 'message/rfc822',
        '.mhtml'  : 'message/rfc822',
        '.mif'    : 'application/x-mif',
        '.mov'    : 'video/quicktime',
        '.movie'  : 'video/x-sgi-movie',
        '.mp2'    : 'audio/mpeg',
        '.mp3'    : 'audio/mpeg',
        '.mp4'    : 'video/mp4',
        '.mpa'    : 'video/mpeg',
        '.mpe'    : 'video/mpeg',
        '.mpeg'   : 'video/mpeg',
        '.mpg'    : 'video/mpeg',
        '.ms'     : 'application/x-troff-ms',
        '.nc'     : 'application/x-netcdf',
        '.nws'    : 'message/rfc822',
        '.o'      : 'application/octet-stream',
        '.obj'    : 'application/octet-stream',
        '.oda'    : 'application/oda',
        '.p12'    : 'application/x-pkcs12',
        '.p7c'    : 'application/pkcs7-mime',
        '.pbm'    : 'image/x-portable-bitmap',
        '.pdf'    : 'application/pdf',
        '.pfx'    : 'application/x-pkcs12',
        '.pgm'    : 'image/x-portable-graymap',
        '.pl'     : 'text/plain',
        '.png'    : 'image/png',
        '.pnm'    : 'image/x-portable-anymap',
        '.pot'    : 'application/vnd.ms-powerpoint',
        '.ppa'    : 'application/vnd.ms-powerpoint',
        '.ppm'    : 'image/x-portable-pixmap',
        '.pps'    : 'application/vnd.ms-powerpoint',
        '.ppt'    : 'application/vnd.ms-powerpoint',
        '.ps'     : 'application/postscript',
        '.pwz'    : 'application/vnd.ms-powerpoint',
        '.py'     : 'text/x-python',
        '.pyc'    : 'application/x-python-code',
        '.pyo'    : 'application/x-python-code',
        '.qt'     : 'video/quicktime',
        '.ra'     : 'audio/x-pn-realaudio',
        '.ram'    : 'application/x-pn-realaudio',
        '.ras'    : 'image/x-cmu-raster',
        '.rdf'    : 'application/xml',
        '.rgb'    : 'image/x-rgb',
        '.roff'   : 'application/x-troff',
        '.rtx'    : 'text/richtext',
        '.sgm'    : 'text/x-sgml',
        '.sgml'   : 'text/x-sgml',
        '.sh'     : 'application/x-sh',
        '.shar'   : 'application/x-shar',
        '.snd'    : 'audio/basic',
        '.so'     : 'application/octet-stream',
        '.src'    : 'application/x-wais-source',
        '.sv4cpio': 'application/x-sv4cpio',
        '.sv4crc' : 'application/x-sv4crc',
        '.svg'    : 'image/svg+xml',
        '.swf'    : 'application/x-shockwave-flash',
        '.t'      : 'application/x-troff',
        '.tar'    : 'application/x-tar',
        '.tcl'    : 'application/x-tcl',
        '.tex'    : 'application/x-tex',
        '.texi'   : 'application/x-texinfo',
        '.texinfo': 'application/x-texinfo',
        '.tif'    : 'image/tiff',
        '.tiff'   : 'image/tiff',
        '.tr'     : 'application/x-troff',
        '.tsv'    : 'text/tab-separated-values',
        '.txt'    : 'text/plain',
        '.ustar'  : 'application/x-ustar',
        '.vcf'    : 'text/x-vcard',
        '.wav'    : 'audio/x-wav',
        '.wiz'    : 'application/msword',
        '.wsdl'   : 'application/xml',
        '.xbm'    : 'image/x-xbitmap',
        '.xlb'    : 'application/vnd.ms-excel',
        # Duplicates :(
        '.xls'    : 'application/excel',
        '.xls'    : 'application/vnd.ms-excel',
        '.xml'    : 'text/xml',
        '.xpdl'   : 'application/xml',
        '.xpm'    : 'image/x-xpixmap',
        '.xsl'    : 'application/xml',
        '.xwd'    : 'image/x-xwindowdump',
        '.zip'    : 'application/zip',
        }

    # These are non-standard types, commonly found w the wild.  They will
    # only match jeżeli strict=0 flag jest given to the API methods.

    # Please sort these too
    common_types = {
        '.jpg' : 'image/jpg',
        '.mid' : 'audio/midi',
        '.midi': 'audio/midi',
        '.pct' : 'image/pict',
        '.pic' : 'image/pict',
        '.pict': 'image/pict',
        '.rtf' : 'application/rtf',
        '.xul' : 'text/xul'
        }


_default_mime_types()


jeżeli __name__ == '__main__':
    zaimportuj getopt

    USAGE = """\
Usage: mimetypes.py [options] type

Options:
    --help / -h       -- print this message oraz exit
    --lenient / -l    -- additionally search of some common, but non-standard
                         types.
    --extension / -e  -- guess extension instead of type

More than one type argument may be given.
"""

    def usage(code, msg=''):
        print(USAGE)
        jeżeli msg: print(msg)
        sys.exit(code)

    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'hle',
                                   ['help', 'lenient', 'extension'])
    wyjąwszy getopt.error jako msg:
        usage(1, msg)

    strict = 1
    extension = 0
    dla opt, arg w opts:
        jeżeli opt w ('-h', '--help'):
            usage(0)
        albo_inaczej opt w ('-l', '--lenient'):
            strict = 0
        albo_inaczej opt w ('-e', '--extension'):
            extension = 1
    dla gtype w args:
        jeżeli extension:
            guess = guess_extension(gtype, strict)
            jeżeli nie guess: print("I don't know anything about type", gtype)
            inaczej: print(guess)
        inaczej:
            guess, encoding = guess_type(gtype, strict)
            jeżeli nie guess: print("I don't know anything about type", gtype)
            inaczej: print('type:', guess, 'encoding:', encoding)
