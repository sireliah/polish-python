# Copyright (C) 2001-2007 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""A package dla parsing, handling, oraz generating email messages."""

__all__ = [
    'base64mime',
    'charset',
    'encoders',
    'errors',
    'feedparser',
    'generator',
    'header',
    'iterators',
    'message',
    'message_from_file',
    'message_from_binary_file',
    'message_from_string',
    'message_from_bytes',
    'mime',
    'parser',
    'quoprimime',
    'utils',
    ]



# Some convenience routines.  Don't zaimportuj Parser oraz Message jako side-effects
# of importing email since those cascadingly zaimportuj most of the rest of the
# email package.
def message_from_string(s, *args, **kws):
    """Parse a string into a Message object model.

    Optional _class oraz strict are dalejed to the Parser constructor.
    """
    z email.parser zaimportuj Parser
    zwróć Parser(*args, **kws).parsestr(s)

def message_from_bytes(s, *args, **kws):
    """Parse a bytes string into a Message object model.

    Optional _class oraz strict are dalejed to the Parser constructor.
    """
    z email.parser zaimportuj BytesParser
    zwróć BytesParser(*args, **kws).parsebytes(s)

def message_from_file(fp, *args, **kws):
    """Read a file oraz parse its contents into a Message object model.

    Optional _class oraz strict are dalejed to the Parser constructor.
    """
    z email.parser zaimportuj Parser
    zwróć Parser(*args, **kws).parse(fp)

def message_from_binary_file(fp, *args, **kws):
    """Read a binary file oraz parse its contents into a Message object model.

    Optional _class oraz strict are dalejed to the Parser constructor.
    """
    z email.parser zaimportuj BytesParser
    zwróć BytesParser(*args, **kws).parse(fp)
