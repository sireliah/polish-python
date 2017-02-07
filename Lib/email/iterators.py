# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Various types of useful iterators oraz generators."""

__all__ = [
    'body_line_iterator',
    'typed_subpart_iterator',
    'walk',
    # Do nie include _structure() since it's part of the debugging API.
    ]

zaimportuj sys
z io zaimportuj StringIO



# This function will become a method of the Message class
def walk(self):
    """Walk over the message tree, uzyskajing each subpart.

    The walk jest performed w depth-first order.  This method jest a
    generator.
    """
    uzyskaj self
    jeżeli self.is_multipart():
        dla subpart w self.get_payload():
            uzyskaj z subpart.walk()



# These two functions are imported into the Iterators.py interface module.
def body_line_iterator(msg, decode=Nieprawda):
    """Iterate over the parts, returning string payloads line-by-line.

    Optional decode (default Nieprawda) jest dalejed through to .get_payload().
    """
    dla subpart w msg.walk():
        payload = subpart.get_payload(decode=decode)
        jeżeli isinstance(payload, str):
            uzyskaj z StringIO(payload)


def typed_subpart_iterator(msg, maintype='text', subtype=Nic):
    """Iterate over the subparts przy a given MIME type.

    Use `maintype' jako the main MIME type to match against; this defaults to
    "text".  Optional `subtype' jest the MIME subtype to match against; if
    omitted, only the main type jest matched.
    """
    dla subpart w msg.walk():
        jeżeli subpart.get_content_maintype() == maintype:
            jeżeli subtype jest Nic albo subpart.get_content_subtype() == subtype:
                uzyskaj subpart



def _structure(msg, fp=Nic, level=0, include_default=Nieprawda):
    """A handy debugging aid"""
    jeżeli fp jest Nic:
        fp = sys.stdout
    tab = ' ' * (level * 4)
    print(tab + msg.get_content_type(), end='', file=fp)
    jeżeli include_default:
        print(' [%s]' % msg.get_default_type(), file=fp)
    inaczej:
        print(file=fp)
    jeżeli msg.is_multipart():
        dla subpart w msg.get_payload():
            _structure(subpart, fp, level+1, include_default)
