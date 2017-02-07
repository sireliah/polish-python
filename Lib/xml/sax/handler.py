"""
This module contains the core classes of version 2.0 of SAX dla Python.
This file provides only default classes przy absolutely minimum
functionality, z which drivers oraz applications can be subclassed.

Many of these classes are empty oraz are included only jako documentation
of the interfaces.

$Id$
"""

version = '2.0beta'

#============================================================================
#
# HANDLER INTERFACES
#
#============================================================================

# ===== ERRORHANDLER =====

klasa ErrorHandler:
    """Basic interface dla SAX error handlers.

    If you create an object that implements this interface, then
    register the object przy your XMLReader, the parser will call the
    methods w your object to report all warnings oraz errors. There
    are three levels of errors available: warnings, (possibly)
    recoverable errors, oraz unrecoverable errors. All methods take a
    SAXParseException jako the only parameter."""

    def error(self, exception):
        "Handle a recoverable error."
        podnieś exception

    def fatalError(self, exception):
        "Handle a non-recoverable error."
        podnieś exception

    def warning(self, exception):
        "Handle a warning."
        print(exception)


# ===== CONTENTHANDLER =====

klasa ContentHandler:
    """Interface dla receiving logical document content events.

    This jest the main callback interface w SAX, oraz the one most
    important to applications. The order of events w this interface
    mirrors the order of the information w the document."""

    def __init__(self):
        self._locator = Nic

    def setDocumentLocator(self, locator):
        """Called by the parser to give the application a locator for
        locating the origin of document events.

        SAX parsers are strongly encouraged (though nie absolutely
        required) to supply a locator: jeżeli it does so, it must supply
        the locator to the application by invoking this method before
        invoking any of the other methods w the DocumentHandler
        interface.

        The locator allows the application to determine the end
        position of any document-related event, even jeżeli the parser jest
        nie reporting an error. Typically, the application will use
        this information dla reporting its own errors (such as
        character content that does nie match an application's
        business rules). The information returned by the locator jest
        probably nie sufficient dla use przy a search engine.

        Note that the locator will zwróć correct information only
        during the invocation of the events w this interface. The
        application should nie attempt to use it at any other time."""
        self._locator = locator

    def startDocument(self):
        """Receive notification of the beginning of a document.

        The SAX parser will invoke this method only once, before any
        other methods w this interface albo w DTDHandler (wyjąwszy for
        setDocumentLocator)."""

    def endDocument(self):
        """Receive notification of the end of a document.

        The SAX parser will invoke this method only once, oraz it will
        be the last method invoked during the parse. The parser shall
        nie invoke this method until it has either abandoned parsing
        (because of an unrecoverable error) albo reached the end of
        input."""

    def startPrefixMapping(self, prefix, uri):
        """Begin the scope of a prefix-URI Namespace mapping.

        The information z this event jest nie necessary dla normal
        Namespace processing: the SAX XML reader will automatically
        replace prefixes dla element oraz attribute names when the
        http://xml.org/sax/features/namespaces feature jest true (the
        default).

        There are cases, however, when applications need to use
        prefixes w character data albo w attribute values, where they
        cannot safely be expanded automatically; the
        start/endPrefixMapping event supplies the information to the
        application to expand prefixes w those contexts itself, if
        necessary.

        Note that start/endPrefixMapping events are nie guaranteed to
        be properly nested relative to each-other: all
        startPrefixMapping events will occur before the corresponding
        startElement event, oraz all endPrefixMapping events will occur
        after the corresponding endElement event, but their order jest
        nie guaranteed."""

    def endPrefixMapping(self, prefix):
        """End the scope of a prefix-URI mapping.

        See startPrefixMapping dla details. This event will always
        occur after the corresponding endElement event, but the order
        of endPrefixMapping events jest nie otherwise guaranteed."""

    def startElement(self, name, attrs):
        """Signals the start of an element w non-namespace mode.

        The name parameter contains the raw XML 1.0 name of the
        element type jako a string oraz the attrs parameter holds an
        instance of the Attributes klasa containing the attributes of
        the element."""

    def endElement(self, name):
        """Signals the end of an element w non-namespace mode.

        The name parameter contains the name of the element type, just
        jako przy the startElement event."""

    def startElementNS(self, name, qname, attrs):
        """Signals the start of an element w namespace mode.

        The name parameter contains the name of the element type jako a
        (uri, localname) tuple, the qname parameter the raw XML 1.0
        name used w the source document, oraz the attrs parameter
        holds an instance of the Attributes klasa containing the
        attributes of the element.

        The uri part of the name tuple jest Nic dla elements which have
        no namespace."""

    def endElementNS(self, name, qname):
        """Signals the end of an element w namespace mode.

        The name parameter contains the name of the element type, just
        jako przy the startElementNS event."""

    def characters(self, content):
        """Receive notification of character data.

        The Parser will call this method to report each chunk of
        character data. SAX parsers may zwróć all contiguous
        character data w a single chunk, albo they may split it into
        several chunks; however, all of the characters w any single
        event must come z the same external entity so that the
        Locator provides useful information."""

    def ignorableWhitespace(self, whitespace):
        """Receive notification of ignorable whitespace w element content.

        Validating Parsers must use this method to report each chunk
        of ignorable whitespace (see the W3C XML 1.0 recommendation,
        section 2.10): non-validating parsers may also use this method
        jeżeli they are capable of parsing oraz using content models.

        SAX parsers may zwróć all contiguous whitespace w a single
        chunk, albo they may split it into several chunks; however, all
        of the characters w any single event must come z the same
        external entity, so that the Locator provides useful
        information."""

    def processingInstruction(self, target, data):
        """Receive notification of a processing instruction.

        The Parser will invoke this method once dla each processing
        instruction found: note that processing instructions may occur
        before albo after the main document element.

        A SAX parser should never report an XML declaration (XML 1.0,
        section 2.8) albo a text declaration (XML 1.0, section 4.3.1)
        using this method."""

    def skippedEntity(self, name):
        """Receive notification of a skipped entity.

        The Parser will invoke this method once dla each entity
        skipped. Non-validating processors may skip entities jeżeli they
        have nie seen the declarations (because, dla example, the
        entity was declared w an external DTD subset). All processors
        may skip external entities, depending on the values of the
        http://xml.org/sax/features/external-general-entities oraz the
        http://xml.org/sax/features/external-parameter-entities
        properties."""


# ===== DTDHandler =====

klasa DTDHandler:
    """Handle DTD events.

    This interface specifies only those DTD events required dla basic
    parsing (unparsed entities oraz attributes)."""

    def notationDecl(self, name, publicId, systemId):
        "Handle a notation declaration event."

    def unparsedEntityDecl(self, name, publicId, systemId, ndata):
        "Handle an unparsed entity declaration event."


# ===== ENTITYRESOLVER =====

klasa EntityResolver:
    """Basic interface dla resolving entities. If you create an object
    implementing this interface, then register the object przy your
    Parser, the parser will call the method w your object to
    resolve all external entities. Note that DefaultHandler implements
    this interface przy the default behaviour."""

    def resolveEntity(self, publicId, systemId):
        """Resolve the system identifier of an entity oraz zwróć either
        the system identifier to read z jako a string, albo an InputSource
        to read from."""
        zwróć systemId


#============================================================================
#
# CORE FEATURES
#
#============================================================================

feature_namespaces = "http://xml.org/sax/features/namespaces"
# true: Perform Namespace processing (default).
# false: Optionally do nie perform Namespace processing
#        (implies namespace-prefixes).
# access: (parsing) read-only; (nie parsing) read/write

feature_namespace_prefixes = "http://xml.org/sax/features/namespace-prefixes"
# true: Report the original prefixed names oraz attributes used dla Namespace
#       declarations.
# false: Do nie report attributes used dla Namespace declarations, oraz
#        optionally do nie report original prefixed names (default).
# access: (parsing) read-only; (nie parsing) read/write

feature_string_interning = "http://xml.org/sax/features/string-interning"
# true: All element names, prefixes, attribute names, Namespace URIs, oraz
#       local names are interned using the built-in intern function.
# false: Names are nie necessarily interned, although they may be (default).
# access: (parsing) read-only; (nie parsing) read/write

feature_validation = "http://xml.org/sax/features/validation"
# true: Report all validation errors (implies external-general-entities oraz
#       external-parameter-entities).
# false: Do nie report validation errors.
# access: (parsing) read-only; (nie parsing) read/write

feature_external_ges = "http://xml.org/sax/features/external-general-entities"
# true: Include all external general (text) entities.
# false: Do nie include external general entities.
# access: (parsing) read-only; (nie parsing) read/write

feature_external_pes = "http://xml.org/sax/features/external-parameter-entities"
# true: Include all external parameter entities, including the external
#       DTD subset.
# false: Do nie include any external parameter entities, even the external
#        DTD subset.
# access: (parsing) read-only; (nie parsing) read/write

all_features = [feature_namespaces,
                feature_namespace_prefixes,
                feature_string_interning,
                feature_validation,
                feature_external_ges,
                feature_external_pes]


#============================================================================
#
# CORE PROPERTIES
#
#============================================================================

property_lexical_handler = "http://xml.org/sax/properties/lexical-handler"
# data type: xml.sax.sax2lib.LexicalHandler
# description: An optional extension handler dla lexical events like comments.
# access: read/write

property_declaration_handler = "http://xml.org/sax/properties/declaration-handler"
# data type: xml.sax.sax2lib.DeclHandler
# description: An optional extension handler dla DTD-related events other
#              than notations oraz unparsed entities.
# access: read/write

property_dom_node = "http://xml.org/sax/properties/dom-node"
# data type: org.w3c.dom.Node
# description: When parsing, the current DOM node being visited jeżeli this jest
#              a DOM iterator; when nie parsing, the root DOM node for
#              iteration.
# access: (parsing) read-only; (nie parsing) read/write

property_xml_string = "http://xml.org/sax/properties/xml-string"
# data type: String
# description: The literal string of characters that was the source for
#              the current event.
# access: read-only

property_encoding = "http://www.python.org/sax/properties/encoding"
# data type: String
# description: The name of the encoding to assume dla input data.
# access: write: set the encoding, e.g. established by a higher-level
#                protocol. May change during parsing (e.g. after
#                processing a META tag)
#         read:  zwróć the current encoding (possibly established through
#                auto-detection.
# initial value: UTF-8
#

property_interning_dict = "http://www.python.org/sax/properties/interning-dict"
# data type: Dictionary
# description: The dictionary used to intern common strings w the document
# access: write: Request that the parser uses a specific dictionary, to
#                allow interning across different documents
#         read:  zwróć the current interning dictionary, albo Nic
#

all_properties = [property_lexical_handler,
                  property_dom_node,
                  property_declaration_handler,
                  property_xml_string,
                  property_encoding,
                  property_interning_dict]
