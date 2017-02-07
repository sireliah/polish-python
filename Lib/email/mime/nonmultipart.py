# Copyright (C) 2002-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Base klasa dla MIME type messages that are nie multipart."""

__all__ = ['MIMENonMultipart']

z email zaimportuj errors
z email.mime.base zaimportuj MIMEBase



klasa MIMENonMultipart(MIMEBase):
    """Base klasa dla MIME non-multipart type messages."""

    def attach(self, payload):
        # The public API prohibits attaching multiple subparts to MIMEBase
        # derived subtypes since none of them are, by definition, of content
        # type multipart/*
        podnieś errors.MultipartConversionError(
            'Cannot attach additional subparts to non-multipart/*')
