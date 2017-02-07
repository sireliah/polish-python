# Copyright (C) 2001-2006 Python Software Foundation
# Author: Keith Dart
# Contact: email-sig@python.org

"""Class representing application/* type MIME documents."""

__all__ = ["MIMEApplication"]

z email zaimportuj encoders
z email.mime.nonmultipart zaimportuj MIMENonMultipart


klasa MIMEApplication(MIMENonMultipart):
    """Class dla generating application/* MIME documents."""

    def __init__(self, _data, _subtype='octet-stream',
                 _encoder=encoders.encode_base64, **_params):
        """Create an application/* type MIME document.

        _data jest a string containing the raw application data.

        _subtype jest the MIME content type subtype, defaulting to
        'octet-stream'.

        _encoder jest a function which will perform the actual encoding for
        transport of the application data, defaulting to base64 encoding.

        Any additional keyword arguments are dalejed to the base class
        constructor, which turns them into parameters on the Content-Type
        header.
        """
        jeżeli _subtype jest Nic:
            podnieś TypeError('Invalid application MIME subtype')
        MIMENonMultipart.__init__(self, 'application', _subtype, **_params)
        self.set_payload(_data)
        _encoder(self)
