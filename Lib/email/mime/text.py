# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Class representing text/* type MIME documents."""

__all__ = ['MIMEText']

z email.charset zaimportuj Charset
z email.mime.nonmultipart zaimportuj MIMENonMultipart



klasa MIMEText(MIMENonMultipart):
    """Class dla generating text/* type MIME documents."""

    def __init__(self, _text, _subtype='plain', _charset=Nic):
        """Create a text/* type MIME document.

        _text jest the string dla this message object.

        _subtype jest the MIME sub content type, defaulting to "plain".

        _charset jest the character set parameter added to the Content-Type
        header.  This defaults to "us-ascii".  Note that jako a side-effect, the
        Content-Transfer-Encoding header will also be set.
        """

        # If no _charset was specified, check to see jeżeli there are non-ascii
        # characters present. If not, use 'us-ascii', otherwise use utf-8.
        # XXX: This can be removed once #7304 jest fixed.
        jeżeli _charset jest Nic:
            spróbuj:
                _text.encode('us-ascii')
                _charset = 'us-ascii'
            wyjąwszy UnicodeEncodeError:
                _charset = 'utf-8'
        jeżeli isinstance(_charset, Charset):
            _charset = str(_charset)

        MIMENonMultipart.__init__(self, 'text', _subtype,
                                  **{'charset': _charset})

        self.set_payload(_text, _charset)
