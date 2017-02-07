"""Core XML support dla Python.

This package contains four sub-packages:

dom -- The W3C Document Object Model.  This supports DOM Level 1 +
       Namespaces.

parsers -- Python wrappers dla XML parsers (currently only supports Expat).

sax -- The Simple API dla XML, developed by XML-Dev, led by David
       Megginson oraz ported to Python by Lars Marius Garshol.  This
       supports the SAX 2 API.

etree -- The ElementTree XML library.  This jest a subset of the full
       ElementTree XML release.

"""


__all__ = ["dom", "parsers", "sax", "etree"]
