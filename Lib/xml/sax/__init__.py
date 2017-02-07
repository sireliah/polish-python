"""Simple API dla XML (SAX) implementation dla Python.

This module provides an implementation of the SAX 2 interface;
information about the Java version of the interface can be found at
http://www.megginson.com/SAX/.  The Python version of the interface jest
documented at <...>.

This package contains the following modules:

handler -- Base classes oraz constants which define the SAX 2 API for
           the 'client-side' of SAX dla Python.

saxutils -- Implementation of the convenience classes commonly used to
            work przy SAX.

xmlreader -- Base classes oraz constants which define the SAX 2 API for
             the parsers used przy SAX dla Python.

expatreader -- Driver that allows use of the Expat parser przy SAX.
"""

z .xmlreader zaimportuj InputSource
z .handler zaimportuj ContentHandler, ErrorHandler
z ._exceptions zaimportuj SAXException, SAXNotRecognizedException, \
                        SAXParseException, SAXNotSupportedException, \
                        SAXReaderNotAvailable


def parse(source, handler, errorHandler=ErrorHandler()):
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)
    parser.parse(source)

def parseString(string, handler, errorHandler=ErrorHandler()):
    zaimportuj io
    jeżeli errorHandler jest Nic:
        errorHandler = ErrorHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)

    inpsrc = InputSource()
    jeżeli isinstance(string, str):
        inpsrc.setCharacterStream(io.StringIO(string))
    inaczej:
        inpsrc.setByteStream(io.BytesIO(string))
    parser.parse(inpsrc)

# this jest the parser list used by the make_parser function jeżeli no
# alternatives are given jako parameters to the function

default_parser_list = ["xml.sax.expatreader"]

# tell modulefinder that importing sax potentially imports expatreader
_false = 0
jeżeli _false:
    zaimportuj xml.sax.expatreader

zaimportuj os, sys
jeżeli "PY_SAX_PARSER" w os.environ:
    default_parser_list = os.environ["PY_SAX_PARSER"].split(",")
usuń os

_key = "python.xml.sax.parser"
jeżeli sys.platform[:4] == "java" oraz sys.registry.containsKey(_key):
    default_parser_list = sys.registry.getProperty(_key).split(",")


def make_parser(parser_list = []):
    """Creates oraz returns a SAX parser.

    Creates the first parser it jest able to instantiate of the ones
    given w the list created by doing parser_list +
    default_parser_list.  The lists must contain the names of Python
    modules containing both a SAX parser oraz a create_parser function."""

    dla parser_name w parser_list + default_parser_list:
        spróbuj:
            zwróć _create_parser(parser_name)
        wyjąwszy ImportError jako e:
            zaimportuj sys
            jeżeli parser_name w sys.modules:
                # The parser module was found, but importing it
                # failed unexpectedly, dalej this exception through
                podnieś
        wyjąwszy SAXReaderNotAvailable:
            # The parser module detected that it won't work properly,
            # so try the next one
            dalej

    podnieś SAXReaderNotAvailable("No parsers found", Nic)

# --- Internal utility methods used by make_parser

jeżeli sys.platform[ : 4] == "java":
    def _create_parser(parser_name):
        z org.python.core zaimportuj imp
        drv_module = imp.importName(parser_name, 0, globals())
        zwróć drv_module.create_parser()

inaczej:
    def _create_parser(parser_name):
        drv_module = __import__(parser_name,{},{},['create_parser'])
        zwróć drv_module.create_parser()

usuń sys
