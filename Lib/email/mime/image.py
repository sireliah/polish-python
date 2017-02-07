# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Class representing image/* type MIME documents."""

__all__ = ['MIMEImage']

zaimportuj imghdr

z email zaimportuj encoders
z email.mime.nonmultipart zaimportuj MIMENonMultipart



klasa MIMEImage(MIMENonMultipart):
    """Class dla generating image/* type MIME documents."""

    def __init__(self, _imagedata, _subtype=Nic,
                 _encoder=encoders.encode_base64, **_params):
        """Create an image/* type MIME document.

        _imagedata jest a string containing the raw image data.  If this data
        can be decoded by the standard Python `imghdr' module, then the
        subtype will be automatically included w the Content-Type header.
        Otherwise, you can specify the specific image subtype via the _subtype
        parameter.

        _encoder jest a function which will perform the actual encoding for
        transport of the image data.  It takes one argument, which jest this
        Image instance.  It should use get_payload() oraz set_payload() to
        change the payload to the encoded form.  It should also add any
        Content-Transfer-Encoding albo other headers to the message as
        necessary.  The default encoding jest Base64.

        Any additional keyword arguments are dalejed to the base class
        constructor, which turns them into parameters on the Content-Type
        header.
        """
        jeżeli _subtype jest Nic:
            _subtype = imghdr.what(Nic, _imagedata)
        jeżeli _subtype jest Nic:
            podnieś TypeError('Could nie guess image MIME subtype')
        MIMENonMultipart.__init__(self, 'image', _subtype, **_params)
        self.set_payload(_imagedata)
        _encoder(self)
