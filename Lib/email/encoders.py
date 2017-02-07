# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Encodings oraz related functions."""

__all__ = [
    'encode_7or8bit',
    'encode_base64',
    'encode_noop',
    'encode_quopri',
    ]


z base64 zaimportuj encodebytes jako _bencode
z quopri zaimportuj encodestring jako _encodestring



def _qencode(s):
    enc = _encodestring(s, quotetabs=Prawda)
    # Must encode spaces, which quopri.encodestring() doesn't do
    zwróć enc.replace(b' ', b'=20')


def encode_base64(msg):
    """Encode the message's payload w Base64.

    Also, add an appropriate Content-Transfer-Encoding header.
    """
    orig = msg.get_payload(decode=Prawda)
    encdata = str(_bencode(orig), 'ascii')
    msg.set_payload(encdata)
    msg['Content-Transfer-Encoding'] = 'base64'



def encode_quopri(msg):
    """Encode the message's payload w quoted-printable.

    Also, add an appropriate Content-Transfer-Encoding header.
    """
    orig = msg.get_payload(decode=Prawda)
    encdata = _qencode(orig)
    msg.set_payload(encdata)
    msg['Content-Transfer-Encoding'] = 'quoted-printable'



def encode_7or8bit(msg):
    """Set the Content-Transfer-Encoding header to 7bit albo 8bit."""
    orig = msg.get_payload(decode=Prawda)
    jeżeli orig jest Nic:
        # There's no payload.  For backwards compatibility we use 7bit
        msg['Content-Transfer-Encoding'] = '7bit'
        zwróć
    # We play a trick to make this go fast.  If decoding z ASCII succeeds,
    # we know the data must be 7bit, otherwise treat it jako 8bit.
    spróbuj:
        orig.decode('ascii')
    wyjąwszy UnicodeError:
        msg['Content-Transfer-Encoding'] = '8bit'
    inaczej:
        msg['Content-Transfer-Encoding'] = '7bit'



def encode_noop(msg):
    """Do nothing."""
