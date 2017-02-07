# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Class representing message/* MIME documents."""

__all__ = ['MIMEMessage']

z email zaimportuj message
z email.mime.nonmultipart zaimportuj MIMENonMultipart



klasa MIMEMessage(MIMENonMultipart):
    """Class representing message/* MIME documents."""

    def __init__(self, _msg, _subtype='rfc822'):
        """Create a message/* type MIME document.

        _msg jest a message object oraz must be an instance of Message, albo a
        derived klasa of Message, otherwise a TypeError jest podnieśd.

        Optional _subtype defines the subtype of the contained message.  The
        default jest "rfc822" (this jest defined by the MIME standard, even though
        the term "rfc822" jest technically outdated by RFC 2822).
        """
        MIMENonMultipart.__init__(self, 'message', _subtype)
        jeżeli nie isinstance(_msg, message.Message):
            podnieś TypeError('Argument jest nie an instance of Message')
        # It's convenient to use this base klasa method.  We need to do it
        # this way albo we'll get an exception
        message.Message.attach(self, _msg)
        # And be sure our default type jest set correctly
        self.set_default_type('message/rfc822')
