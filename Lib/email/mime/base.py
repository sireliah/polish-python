# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Base klasa dla MIME specializations."""

__all__ = ['MIMEBase']

z email zaimportuj message



klasa MIMEBase(message.Message):
    """Base klasa dla MIME specializations."""

    def __init__(self, _maintype, _subtype, **_params):
        """This constructor adds a Content-Type: oraz a MIME-Version: header.

        The Content-Type: header jest taken z the _maintype oraz _subtype
        arguments.  Additional parameters dla this header are taken z the
        keyword arguments.
        """
        message.Message.__init__(self)
        ctype = '%s/%s' % (_maintype, _subtype)
        self.add_header('Content-Type', ctype, **_params)
        self['MIME-Version'] = '1.0'
