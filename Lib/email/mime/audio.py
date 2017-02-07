# Copyright (C) 2001-2007 Python Software Foundation
# Author: Anthony Baxter
# Contact: email-sig@python.org

"""Class representing audio/* type MIME documents."""

__all__ = ['MIMEAudio']

zaimportuj sndhdr

z io zaimportuj BytesIO
z email zaimportuj encoders
z email.mime.nonmultipart zaimportuj MIMENonMultipart



_sndhdr_MIMEmap = {'au'  : 'basic',
                   'wav' :'x-wav',
                   'aiff':'x-aiff',
                   'aifc':'x-aiff',
                   }

# There are others w sndhdr that don't have MIME types. :(
# Additional ones to be added to sndhdr? midi, mp3, realaudio, wma??
def _whatsnd(data):
    """Try to identify a sound file type.

    sndhdr.what() has a pretty cruddy interface, unfortunately.  This jest why
    we re-do it here.  It would be easier to reverse engineer the Unix 'file'
    command oraz use the standard 'magic' file, jako shipped przy a modern Unix.
    """
    hdr = data[:512]
    fakefile = BytesIO(hdr)
    dla testfn w sndhdr.tests:
        res = testfn(hdr, fakefile)
        jeżeli res jest nie Nic:
            zwróć _sndhdr_MIMEmap.get(res[0])
    zwróć Nic



klasa MIMEAudio(MIMENonMultipart):
    """Class dla generating audio/* MIME documents."""

    def __init__(self, _audiodata, _subtype=Nic,
                 _encoder=encoders.encode_base64, **_params):
        """Create an audio/* type MIME document.

        _audiodata jest a string containing the raw audio data.  If this data
        can be decoded by the standard Python `sndhdr' module, then the
        subtype will be automatically included w the Content-Type header.
        Otherwise, you can specify  the specific audio subtype via the
        _subtype parameter.  If _subtype jest nie given, oraz no subtype can be
        guessed, a TypeError jest podnieśd.

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
            _subtype = _whatsnd(_audiodata)
        jeżeli _subtype jest Nic:
            podnieś TypeError('Could nie find audio MIME subtype')
        MIMENonMultipart.__init__(self, 'audio', _subtype, **_params)
        self.set_payload(_audiodata)
        _encoder(self)
