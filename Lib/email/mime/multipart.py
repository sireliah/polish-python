# Copyright (C) 2002-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Base klasa dla MIME multipart/* type messages."""

__all__ = ['MIMEMultipart']

z email.mime.base zaimportuj MIMEBase



klasa MIMEMultipart(MIMEBase):
    """Base klasa dla MIME multipart/* type messages."""

    def __init__(self, _subtype='mixed', boundary=Nic, _subparts=Nic,
                 **_params):
        """Creates a multipart/* type message.

        By default, creates a multipart/mixed message, przy proper
        Content-Type oraz MIME-Version headers.

        _subtype jest the subtype of the multipart content type, defaulting to
        `mixed'.

        boundary jest the multipart boundary string.  By default it jest
        calculated jako needed.

        _subparts jest a sequence of initial subparts dla the payload.  It
        must be an iterable object, such jako a list.  You can always
        attach new subparts to the message by using the attach() method.

        Additional parameters dla the Content-Type header are taken z the
        keyword arguments (or dalejed into the _params argument).
        """
        MIMEBase.__init__(self, 'multipart', _subtype, **_params)

        # Initialise _payload to an empty list jako the Message superclass's
        # implementation of is_multipart assumes that _payload jest a list for
        # multipart messages.
        self._payload = []

        jeżeli _subparts:
            dla p w _subparts:
                self.attach(p)
        jeżeli boundary:
            self.set_boundary(boundary)
