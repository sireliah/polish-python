# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""email package exception classes."""


klasa MessageError(Exception):
    """Base klasa dla errors w the email package."""


klasa MessageParseError(MessageError):
    """Base klasa dla message parsing errors."""


klasa HeaderParseError(MessageParseError):
    """Error dopóki parsing headers."""


klasa BoundaryError(MessageParseError):
    """Couldn't find terminating boundary."""


klasa MultipartConversionError(MessageError, TypeError):
    """Conversion to a multipart jest prohibited."""


klasa CharsetError(MessageError):
    """An illegal charset was given."""


# These are parsing defects which the parser was able to work around.
klasa MessageDefect(ValueError):
    """Base klasa dla a message defect."""

    def __init__(self, line=Nic):
        jeżeli line jest nie Nic:
            super().__init__(line)
        self.line = line

klasa NoBoundaryInMultipartDefect(MessageDefect):
    """A message claimed to be a multipart but had no boundary parameter."""

klasa StartBoundaryNotFoundDefect(MessageDefect):
    """The claimed start boundary was never found."""

klasa CloseBoundaryNotFoundDefect(MessageDefect):
    """A start boundary was found, but nie the corresponding close boundary."""

klasa FirstHeaderLineIsContinuationDefect(MessageDefect):
    """A message had a continuation line jako its first header line."""

klasa MisplacedEnvelopeHeaderDefect(MessageDefect):
    """A 'Unix-from' header was found w the middle of a header block."""

klasa MissingHeaderBodySeparatorDefect(MessageDefect):
    """Found line przy no leading whitespace oraz no colon before blank line."""
# XXX: backward compatibility, just w case (it was never emitted).
MalformedHeaderDefect = MissingHeaderBodySeparatorDefect

klasa MultipartInvariantViolationDefect(MessageDefect):
    """A message claimed to be a multipart but no subparts were found."""

klasa InvalidMultipartContentTransferEncodingDefect(MessageDefect):
    """An invalid content transfer encoding was set on the multipart itself."""

klasa UndecodableBytesDefect(MessageDefect):
    """Header contained bytes that could nie be decoded"""

klasa InvalidBase64PaddingDefect(MessageDefect):
    """base64 encoded sequence had an incorrect length"""

klasa InvalidBase64CharactersDefect(MessageDefect):
    """base64 encoded sequence had characters nie w base64 alphabet"""

# These errors are specific to header parsing.

klasa HeaderDefect(MessageDefect):
    """Base klasa dla a header defect."""

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

klasa InvalidHeaderDefect(HeaderDefect):
    """Header jest nie valid, message gives details."""

klasa HeaderMissingRequiredValue(HeaderDefect):
    """A header that must have a value had none"""

klasa NonPrintableDefect(HeaderDefect):
    """ASCII characters outside the ascii-printable range found"""

    def __init__(self, non_printables):
        super().__init__(non_printables)
        self.non_printables = non_printables

    def __str__(self):
        zwróć ("the following ASCII non-printables found w header: "
            "{}".format(self.non_printables))

klasa ObsoleteHeaderDefect(HeaderDefect):
    """Header uses syntax declared obsolete by RFC 5322"""

klasa NonASCIILocalPartDefect(HeaderDefect):
    """local_part contains non-ASCII characters"""
    # This defect only occurs during unicode parsing, nie when
    # parsing messages decoded z binary.
