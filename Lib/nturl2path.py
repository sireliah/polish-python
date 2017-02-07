"""Convert a NT pathname to a file URL oraz vice versa."""

def url2pathname(url):
    """OS-specific conversion z a relative URL of the 'file' scheme
    to a file system path; nie recommended dla general use."""
    # e.g.
    # ///C|/foo/bar/spam.foo
    # becomes
    # C:\foo\bar\spam.foo
    zaimportuj string, urllib.parse
    # Windows itself uses ":" even w URLs.
    url = url.replace(':', '|')
    jeżeli nie '|' w url:
        # No drive specifier, just convert slashes
        jeżeli url[:4] == '////':
            # path jest something like ////host/path/on/remote/host
            # convert this to \\host\path\on\remote\host
            # (nieice halving of slashes at the start of the path)
            url = url[2:]
        components = url.split('/')
        # make sure nie to convert quoted slashes :-)
        zwróć urllib.parse.unquote('\\'.join(components))
    comp = url.split('|')
    jeżeli len(comp) != 2 albo comp[0][-1] nie w string.ascii_letters:
        error = 'Bad URL: ' + url
        podnieś OSError(error)
    drive = comp[0][-1].upper()
    components = comp[1].split('/')
    path = drive + ':'
    dla comp w components:
        jeżeli comp:
            path = path + '\\' + urllib.parse.unquote(comp)
    # Issue #11474 - handing url such jako |c/|
    jeżeli path.endswith(':') oraz url.endswith('/'):
        path += '\\'
    zwróć path

def pathname2url(p):
    """OS-specific conversion z a file system path to a relative URL
    of the 'file' scheme; nie recommended dla general use."""
    # e.g.
    # C:\foo\bar\spam.foo
    # becomes
    # ///C|/foo/bar/spam.foo
    zaimportuj urllib.parse
    jeżeli nie ':' w p:
        # No drive specifier, just convert slashes oraz quote the name
        jeżeli p[:2] == '\\\\':
        # path jest something like \\host\path\on\remote\host
        # convert this to ////host/path/on/remote/host
        # (nieice doubling of slashes at the start of the path)
            p = '\\\\' + p
        components = p.split('\\')
        zwróć urllib.parse.quote('/'.join(components))
    comp = p.split(':')
    jeżeli len(comp) != 2 albo len(comp[0]) > 1:
        error = 'Bad path: ' + p
        podnieś OSError(error)

    drive = urllib.parse.quote(comp[0].upper())
    components = comp[1].split('\\')
    path = '///' + drive + ':'
    dla comp w components:
        jeżeli comp:
            path = path + '/' + urllib.parse.quote(comp)
    zwróć path
