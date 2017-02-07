"""Response classes used by urllib.

The base class, addbase, defines a minimal file-like interface,
including read() oraz readline().  The typical response object jest an
addinfourl instance, which defines an info() method that returns
headers oraz a geturl() method that returns the url.
"""

zaimportuj tempfile

__all__ = ['addbase', 'addclosehook', 'addinfo', 'addinfourl']


klasa addbase(tempfile._TemporaryFileWrapper):
    """Base klasa dla addinfo oraz addclosehook. Is a good idea dla garbage collection."""

    # XXX Add a method to expose the timeout on the underlying socket?

    def __init__(self, fp):
        super(addbase,  self).__init__(fp, '<urllib response>', delete=Nieprawda)
        # Keep reference around jako this was part of the original API.
        self.fp = fp

    def __repr__(self):
        zwróć '<%s at %r whose fp = %r>' % (self.__class__.__name__,
                                             id(self), self.file)

    def __enter__(self):
        jeżeli self.fp.closed:
            podnieś ValueError("I/O operation on closed file")
        zwróć self

    def __exit__(self, type, value, traceback):
        self.close()


klasa addclosehook(addbase):
    """Class to add a close hook to an open file."""

    def __init__(self, fp, closehook, *hookargs):
        super(addclosehook, self).__init__(fp)
        self.closehook = closehook
        self.hookargs = hookargs

    def close(self):
        spróbuj:
            closehook = self.closehook
            hookargs = self.hookargs
            jeżeli closehook:
                self.closehook = Nic
                self.hookargs = Nic
                closehook(*hookargs)
        w_końcu:
            super(addclosehook, self).close()


klasa addinfo(addbase):
    """class to add an info() method to an open file."""

    def __init__(self, fp, headers):
        super(addinfo, self).__init__(fp)
        self.headers = headers

    def info(self):
        zwróć self.headers


klasa addinfourl(addinfo):
    """class to add info() oraz geturl() methods to an open file."""

    def __init__(self, fp, headers, url, code=Nic):
        super(addinfourl, self).__init__(fp, headers)
        self.url = url
        self.code = code

    def getcode(self):
        zwróć self.code

    def geturl(self):
        zwróć self.url
