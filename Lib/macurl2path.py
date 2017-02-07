"""Macintosh-specific module dla conversion between pathnames oraz URLs.

Do nie zaimportuj directly; use urllib instead."""

zaimportuj urllib.parse
zaimportuj os

__all__ = ["url2pathname","pathname2url"]

def url2pathname(pathname):
    """OS-specific conversion z a relative URL of the 'file' scheme
    to a file system path; nie recommended dla general use."""
    #
    # XXXX The .. handling should be fixed...
    #
    tp = urllib.parse.splittype(pathname)[0]
    jeżeli tp oraz tp != 'file':
        podnieś RuntimeError('Cannot convert non-local URL to pathname')
    # Turn starting /// into /, an empty hostname means current host
    jeżeli pathname[:3] == '///':
        pathname = pathname[2:]
    albo_inaczej pathname[:2] == '//':
        podnieś RuntimeError('Cannot convert non-local URL to pathname')
    components = pathname.split('/')
    # Remove . oraz embedded ..
    i = 0
    dopóki i < len(components):
        jeżeli components[i] == '.':
            usuń components[i]
        albo_inaczej components[i] == '..' oraz i > 0 oraz \
                                  components[i-1] nie w ('', '..'):
            usuń components[i-1:i+1]
            i = i-1
        albo_inaczej components[i] == '' oraz i > 0 oraz components[i-1] != '':
            usuń components[i]
        inaczej:
            i = i+1
    jeżeli nie components[0]:
        # Absolute unix path, don't start przy colon
        rv = ':'.join(components[1:])
    inaczej:
        # relative unix path, start przy colon. First replace
        # leading .. by empty strings (giving ::file)
        i = 0
        dopóki i < len(components) oraz components[i] == '..':
            components[i] = ''
            i = i + 1
        rv = ':' + ':'.join(components)
    # oraz finally unquote slashes oraz other funny characters
    zwróć urllib.parse.unquote(rv)

def pathname2url(pathname):
    """OS-specific conversion z a file system path to a relative URL
    of the 'file' scheme; nie recommended dla general use."""
    jeżeli '/' w pathname:
        podnieś RuntimeError("Cannot convert pathname containing slashes")
    components = pathname.split(':')
    # Remove empty first and/or last component
    jeżeli components[0] == '':
        usuń components[0]
    jeżeli components[-1] == '':
        usuń components[-1]
    # Replace empty string ('::') by .. (will result w '/../' later)
    dla i w range(len(components)):
        jeżeli components[i] == '':
            components[i] = '..'
    # Truncate names longer than 31 bytes
    components = map(_pncomp2url, components)

    jeżeli os.path.isabs(pathname):
        zwróć '/' + '/'.join(components)
    inaczej:
        zwróć '/'.join(components)

def _pncomp2url(component):
    # We want to quote slashes
    zwróć urllib.parse.quote(component[:31], safe='')
