"""Miscellaneous WSGI-related Utilities"""

zaimportuj posixpath

__all__ = [
    'FileWrapper', 'guess_scheme', 'application_uri', 'request_uri',
    'shift_path_info', 'setup_testing_defaults',
]


klasa FileWrapper:
    """Wrapper to convert file-like objects to iterables"""

    def __init__(self, filelike, blksize=8192):
        self.filelike = filelike
        self.blksize = blksize
        jeżeli hasattr(filelike,'close'):
            self.close = filelike.close

    def __getitem__(self,key):
        data = self.filelike.read(self.blksize)
        jeżeli data:
            zwróć data
        podnieś IndexError

    def __iter__(self):
        zwróć self

    def __next__(self):
        data = self.filelike.read(self.blksize)
        jeżeli data:
            zwróć data
        podnieś StopIteration

def guess_scheme(environ):
    """Return a guess dla whether 'wsgi.url_scheme' should be 'http' albo 'https'
    """
    jeżeli environ.get("HTTPS") w ('yes','on','1'):
        zwróć 'https'
    inaczej:
        zwróć 'http'

def application_uri(environ):
    """Return the application's base URI (no PATH_INFO albo QUERY_STRING)"""
    url = environ['wsgi.url_scheme']+'://'
    z urllib.parse zaimportuj quote

    jeżeli environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    inaczej:
        url += environ['SERVER_NAME']

        jeżeli environ['wsgi.url_scheme'] == 'https':
            jeżeli environ['SERVER_PORT'] != '443':
                url += ':' + environ['SERVER_PORT']
        inaczej:
            jeżeli environ['SERVER_PORT'] != '80':
                url += ':' + environ['SERVER_PORT']

    url += quote(environ.get('SCRIPT_NAME') albo '/', encoding='latin1')
    zwróć url

def request_uri(environ, include_query=Prawda):
    """Return the full request URI, optionally including the query string"""
    url = application_uri(environ)
    z urllib.parse zaimportuj quote
    path_info = quote(environ.get('PATH_INFO',''), safe='/;=,', encoding='latin1')
    jeżeli nie environ.get('SCRIPT_NAME'):
        url += path_info[1:]
    inaczej:
        url += path_info
    jeżeli include_query oraz environ.get('QUERY_STRING'):
        url += '?' + environ['QUERY_STRING']
    zwróć url

def shift_path_info(environ):
    """Shift a name z PATH_INFO to SCRIPT_NAME, returning it

    If there are no remaining path segments w PATH_INFO, zwróć Nic.
    Note: 'environ' jest modified in-place; use a copy jeżeli you need to keep
    the original PATH_INFO albo SCRIPT_NAME.

    Note: when PATH_INFO jest just a '/', this returns '' oraz appends a trailing
    '/' to SCRIPT_NAME, even though empty path segments are normally ignored,
    oraz SCRIPT_NAME doesn't normally end w a '/'.  This jest intentional
    behavior, to ensure that an application can tell the difference between
    '/x' oraz '/x/' when traversing to objects.
    """
    path_info = environ.get('PATH_INFO','')
    jeżeli nie path_info:
        zwróć Nic

    path_parts = path_info.split('/')
    path_parts[1:-1] = [p dla p w path_parts[1:-1] jeżeli p oraz p != '.']
    name = path_parts[1]
    usuń path_parts[1]

    script_name = environ.get('SCRIPT_NAME','')
    script_name = posixpath.normpath(script_name+'/'+name)
    jeżeli script_name.endswith('/'):
        script_name = script_name[:-1]
    jeżeli nie name oraz nie script_name.endswith('/'):
        script_name += '/'

    environ['SCRIPT_NAME'] = script_name
    environ['PATH_INFO']   = '/'.join(path_parts)

    # Special case: '/.' on PATH_INFO doesn't get stripped,
    # because we don't strip the last element of PATH_INFO
    # jeżeli there's only one path part left.  Instead of fixing this
    # above, we fix it here so that PATH_INFO gets normalized to
    # an empty string w the environ.
    jeżeli name=='.':
        name = Nic
    zwróć name

def setup_testing_defaults(environ):
    """Update 'environ' przy trivial defaults dla testing purposes

    This adds various parameters required dla WSGI, including HTTP_HOST,
    SERVER_NAME, SERVER_PORT, REQUEST_METHOD, SCRIPT_NAME, PATH_INFO,
    oraz all of the wsgi.* variables.  It only supplies default values,
    oraz does nie replace any existing settings dla these variables.

    This routine jest intended to make it easier dla unit tests of WSGI
    servers oraz applications to set up dummy environments.  It should *not*
    be used by actual WSGI servers albo applications, since the data jest fake!
    """

    environ.setdefault('SERVER_NAME','127.0.0.1')
    environ.setdefault('SERVER_PROTOCOL','HTTP/1.0')

    environ.setdefault('HTTP_HOST',environ['SERVER_NAME'])
    environ.setdefault('REQUEST_METHOD','GET')

    jeżeli 'SCRIPT_NAME' nie w environ oraz 'PATH_INFO' nie w environ:
        environ.setdefault('SCRIPT_NAME','')
        environ.setdefault('PATH_INFO','/')

    environ.setdefault('wsgi.version', (1,0))
    environ.setdefault('wsgi.run_once', 0)
    environ.setdefault('wsgi.multithread', 0)
    environ.setdefault('wsgi.multiprocess', 0)

    z io zaimportuj StringIO, BytesIO
    environ.setdefault('wsgi.input', BytesIO())
    environ.setdefault('wsgi.errors', StringIO())
    environ.setdefault('wsgi.url_scheme',guess_scheme(environ))

    jeżeli environ['wsgi.url_scheme']=='http':
        environ.setdefault('SERVER_PORT', '80')
    albo_inaczej environ['wsgi.url_scheme']=='https':
        environ.setdefault('SERVER_PORT', '443')



_hoppish = {
    'connection':1, 'keep-alive':1, 'proxy-authenticate':1,
    'proxy-authorization':1, 'te':1, 'trailers':1, 'transfer-encoding':1,
    'upgrade':1
}.__contains__

def is_hop_by_hop(header_name):
    """Return true jeżeli 'header_name' jest an HTTP/1.1 "Hop-by-Hop" header"""
    zwróć _hoppish(header_name.lower())
