"""
SAX driver dla the pyexpat C module.  This driver works with
pyexpat.__version__ == '2.22'.
"""

version = "0.20"

z xml.sax._exceptions zaimportuj *
z xml.sax.handler zaimportuj feature_validation, feature_namespaces
z xml.sax.handler zaimportuj feature_namespace_prefixes
z xml.sax.handler zaimportuj feature_external_ges, feature_external_pes
z xml.sax.handler zaimportuj feature_string_interning
z xml.sax.handler zaimportuj property_xml_string, property_interning_dict

# xml.parsers.expat does nie podnieś ImportError w Jython
zaimportuj sys
jeżeli sys.platform[:4] == "java":
    podnieś SAXReaderNotAvailable("expat nie available w Java", Nic)
usuń sys

spróbuj:
    z xml.parsers zaimportuj expat
wyjąwszy ImportError:
    podnieś SAXReaderNotAvailable("expat nie supported", Nic)
inaczej:
    jeżeli nie hasattr(expat, "ParserCreate"):
        podnieś SAXReaderNotAvailable("expat nie supported", Nic)
z xml.sax zaimportuj xmlreader, saxutils, handler

AttributesImpl = xmlreader.AttributesImpl
AttributesNSImpl = xmlreader.AttributesNSImpl

# If we're using a sufficiently recent version of Python, we can use
# weak references to avoid cycles between the parser oraz content
# handler, otherwise we'll just have to pretend.
spróbuj:
    zaimportuj _weakref
wyjąwszy ImportError:
    def _mkproxy(o):
        zwróć o
inaczej:
    zaimportuj weakref
    _mkproxy = weakref.proxy
    usuń weakref, _weakref

klasa _ClosedParser:
    dalej

# --- ExpatLocator

klasa ExpatLocator(xmlreader.Locator):
    """Locator dla use przy the ExpatParser class.

    This uses a weak reference to the parser object to avoid creating
    a circular reference between the parser oraz the content handler.
    """
    def __init__(self, parser):
        self._ref = _mkproxy(parser)

    def getColumnNumber(self):
        parser = self._ref
        jeżeli parser._parser jest Nic:
            zwróć Nic
        zwróć parser._parser.ErrorColumnNumber

    def getLineNumber(self):
        parser = self._ref
        jeżeli parser._parser jest Nic:
            zwróć 1
        zwróć parser._parser.ErrorLineNumber

    def getPublicId(self):
        parser = self._ref
        jeżeli parser jest Nic:
            zwróć Nic
        zwróć parser._source.getPublicId()

    def getSystemId(self):
        parser = self._ref
        jeżeli parser jest Nic:
            zwróć Nic
        zwróć parser._source.getSystemId()


# --- ExpatParser

klasa ExpatParser(xmlreader.IncrementalParser, xmlreader.Locator):
    """SAX driver dla the pyexpat C module."""

    def __init__(self, namespaceHandling=0, bufsize=2**16-20):
        xmlreader.IncrementalParser.__init__(self, bufsize)
        self._source = xmlreader.InputSource()
        self._parser = Nic
        self._namespaces = namespaceHandling
        self._lex_handler_prop = Nic
        self._parsing = 0
        self._entity_stack = []
        self._external_ges = 1
        self._interning = Nic

    # XMLReader methods

    def parse(self, source):
        "Parse an XML document z a URL albo an InputSource."
        source = saxutils.prepare_input_source(source)

        self._source = source
        self.reset()
        self._cont_handler.setDocumentLocator(ExpatLocator(self))
        xmlreader.IncrementalParser.parse(self, source)

    def prepareParser(self, source):
        jeżeli source.getSystemId() jest nie Nic:
            self._parser.SetBase(source.getSystemId())

    # Redefined setContentHandler to allow changing handlers during parsing

    def setContentHandler(self, handler):
        xmlreader.IncrementalParser.setContentHandler(self, handler)
        jeżeli self._parsing:
            self._reset_cont_handler()

    def getFeature(self, name):
        jeżeli name == feature_namespaces:
            zwróć self._namespaces
        albo_inaczej name == feature_string_interning:
            zwróć self._interning jest nie Nic
        albo_inaczej name w (feature_validation, feature_external_pes,
                      feature_namespace_prefixes):
            zwróć 0
        albo_inaczej name == feature_external_ges:
            zwróć self._external_ges
        podnieś SAXNotRecognizedException("Feature '%s' nie recognized" % name)

    def setFeature(self, name, state):
        jeżeli self._parsing:
            podnieś SAXNotSupportedException("Cannot set features dopóki parsing")

        jeżeli name == feature_namespaces:
            self._namespaces = state
        albo_inaczej name == feature_external_ges:
            self._external_ges = state
        albo_inaczej name == feature_string_interning:
            jeżeli state:
                jeżeli self._interning jest Nic:
                    self._interning = {}
            inaczej:
                self._interning = Nic
        albo_inaczej name == feature_validation:
            jeżeli state:
                podnieś SAXNotSupportedException(
                    "expat does nie support validation")
        albo_inaczej name == feature_external_pes:
            jeżeli state:
                podnieś SAXNotSupportedException(
                    "expat does nie read external parameter entities")
        albo_inaczej name == feature_namespace_prefixes:
            jeżeli state:
                podnieś SAXNotSupportedException(
                    "expat does nie report namespace prefixes")
        inaczej:
            podnieś SAXNotRecognizedException(
                "Feature '%s' nie recognized" % name)

    def getProperty(self, name):
        jeżeli name == handler.property_lexical_handler:
            zwróć self._lex_handler_prop
        albo_inaczej name == property_interning_dict:
            zwróć self._interning
        albo_inaczej name == property_xml_string:
            jeżeli self._parser:
                jeżeli hasattr(self._parser, "GetInputContext"):
                    zwróć self._parser.GetInputContext()
                inaczej:
                    podnieś SAXNotRecognizedException(
                        "This version of expat does nie support getting"
                        " the XML string")
            inaczej:
                podnieś SAXNotSupportedException(
                    "XML string cannot be returned when nie parsing")
        podnieś SAXNotRecognizedException("Property '%s' nie recognized" % name)

    def setProperty(self, name, value):
        jeżeli name == handler.property_lexical_handler:
            self._lex_handler_prop = value
            jeżeli self._parsing:
                self._reset_lex_handler_prop()
        albo_inaczej name == property_interning_dict:
            self._interning = value
        albo_inaczej name == property_xml_string:
            podnieś SAXNotSupportedException("Property '%s' cannot be set" %
                                           name)
        inaczej:
            podnieś SAXNotRecognizedException("Property '%s' nie recognized" %
                                            name)

    # IncrementalParser methods

    def feed(self, data, isFinal = 0):
        jeżeli nie self._parsing:
            self.reset()
            self._parsing = 1
            self._cont_handler.startDocument()

        spróbuj:
            # The isFinal parameter jest internal to the expat reader.
            # If it jest set to true, expat will check validity of the entire
            # document. When feeding chunks, they are nie normally final -
            # wyjąwszy when invoked z close.
            self._parser.Parse(data, isFinal)
        wyjąwszy expat.error jako e:
            exc = SAXParseException(expat.ErrorString(e.code), e, self)
            # FIXME: when to invoke error()?
            self._err_handler.fatalError(exc)

    def close(self):
        jeżeli (self._entity_stack albo self._parser jest Nic albo
            isinstance(self._parser, _ClosedParser)):
            # If we are completing an external entity, do nothing here
            zwróć
        spróbuj:
            self.feed("", isFinal = 1)
            self._cont_handler.endDocument()
            self._parsing = 0
            # przerwij cycle created by expat handlers pointing to our methods
            self._parser = Nic
        w_końcu:
            self._parsing = 0
            jeżeli self._parser jest nie Nic:
                # Keep ErrorColumnNumber oraz ErrorLineNumber after closing.
                parser = _ClosedParser()
                parser.ErrorColumnNumber = self._parser.ErrorColumnNumber
                parser.ErrorLineNumber = self._parser.ErrorLineNumber
                self._parser = parser
            spróbuj:
                file = self._source.getCharacterStream()
                jeżeli file jest nie Nic:
                    file.close()
            w_końcu:
                file = self._source.getByteStream()
                jeżeli file jest nie Nic:
                    file.close()

    def _reset_cont_handler(self):
        self._parser.ProcessingInstructionHandler = \
                                    self._cont_handler.processingInstruction
        self._parser.CharacterDataHandler = self._cont_handler.characters

    def _reset_lex_handler_prop(self):
        lex = self._lex_handler_prop
        parser = self._parser
        jeżeli lex jest Nic:
            parser.CommentHandler = Nic
            parser.StartCdataSectionHandler = Nic
            parser.EndCdataSectionHandler = Nic
            parser.StartDoctypeDeclHandler = Nic
            parser.EndDoctypeDeclHandler = Nic
        inaczej:
            parser.CommentHandler = lex.comment
            parser.StartCdataSectionHandler = lex.startCDATA
            parser.EndCdataSectionHandler = lex.endCDATA
            parser.StartDoctypeDeclHandler = self.start_doctype_decl
            parser.EndDoctypeDeclHandler = lex.endDTD

    def reset(self):
        jeżeli self._namespaces:
            self._parser = expat.ParserCreate(self._source.getEncoding(), " ",
                                              intern=self._interning)
            self._parser.namespace_prefixes = 1
            self._parser.StartElementHandler = self.start_element_ns
            self._parser.EndElementHandler = self.end_element_ns
        inaczej:
            self._parser = expat.ParserCreate(self._source.getEncoding(),
                                              intern = self._interning)
            self._parser.StartElementHandler = self.start_element
            self._parser.EndElementHandler = self.end_element

        self._reset_cont_handler()
        self._parser.UnparsedEntityDeclHandler = self.unparsed_entity_decl
        self._parser.NotationDeclHandler = self.notation_decl
        self._parser.StartNamespaceDeclHandler = self.start_namespace_decl
        self._parser.EndNamespaceDeclHandler = self.end_namespace_decl

        self._decl_handler_prop = Nic
        jeżeli self._lex_handler_prop:
            self._reset_lex_handler_prop()
#         self._parser.DefaultHandler =
#         self._parser.DefaultHandlerExpand =
#         self._parser.NotStandaloneHandler =
        self._parser.ExternalEntityRefHandler = self.external_entity_ref
        spróbuj:
            self._parser.SkippedEntityHandler = self.skipped_entity_handler
        wyjąwszy AttributeError:
            # This pyexpat does nie support SkippedEntity
            dalej
        self._parser.SetParamEntityParsing(
            expat.XML_PARAM_ENTITY_PARSING_UNLESS_STANDALONE)

        self._parsing = 0
        self._entity_stack = []

    # Locator methods

    def getColumnNumber(self):
        jeżeli self._parser jest Nic:
            zwróć Nic
        zwróć self._parser.ErrorColumnNumber

    def getLineNumber(self):
        jeżeli self._parser jest Nic:
            zwróć 1
        zwróć self._parser.ErrorLineNumber

    def getPublicId(self):
        zwróć self._source.getPublicId()

    def getSystemId(self):
        zwróć self._source.getSystemId()

    # event handlers
    def start_element(self, name, attrs):
        self._cont_handler.startElement(name, AttributesImpl(attrs))

    def end_element(self, name):
        self._cont_handler.endElement(name)

    def start_element_ns(self, name, attrs):
        pair = name.split()
        jeżeli len(pair) == 1:
            # no namespace
            pair = (Nic, name)
        albo_inaczej len(pair) == 3:
            pair = pair[0], pair[1]
        inaczej:
            # default namespace
            pair = tuple(pair)

        newattrs = {}
        qnames = {}
        dla (aname, value) w attrs.items():
            parts = aname.split()
            length = len(parts)
            jeżeli length == 1:
                # no namespace
                qname = aname
                apair = (Nic, aname)
            albo_inaczej length == 3:
                qname = "%s:%s" % (parts[2], parts[1])
                apair = parts[0], parts[1]
            inaczej:
                # default namespace
                qname = parts[1]
                apair = tuple(parts)

            newattrs[apair] = value
            qnames[apair] = qname

        self._cont_handler.startElementNS(pair, Nic,
                                          AttributesNSImpl(newattrs, qnames))

    def end_element_ns(self, name):
        pair = name.split()
        jeżeli len(pair) == 1:
            pair = (Nic, name)
        albo_inaczej len(pair) == 3:
            pair = pair[0], pair[1]
        inaczej:
            pair = tuple(pair)

        self._cont_handler.endElementNS(pair, Nic)

    # this jest nie used (call directly to ContentHandler)
    def processing_instruction(self, target, data):
        self._cont_handler.processingInstruction(target, data)

    # this jest nie used (call directly to ContentHandler)
    def character_data(self, data):
        self._cont_handler.characters(data)

    def start_namespace_decl(self, prefix, uri):
        self._cont_handler.startPrefixMapping(prefix, uri)

    def end_namespace_decl(self, prefix):
        self._cont_handler.endPrefixMapping(prefix)

    def start_doctype_decl(self, name, sysid, pubid, has_internal_subset):
        self._lex_handler_prop.startDTD(name, pubid, sysid)

    def unparsed_entity_decl(self, name, base, sysid, pubid, notation_name):
        self._dtd_handler.unparsedEntityDecl(name, pubid, sysid, notation_name)

    def notation_decl(self, name, base, sysid, pubid):
        self._dtd_handler.notationDecl(name, pubid, sysid)

    def external_entity_ref(self, context, base, sysid, pubid):
        jeżeli nie self._external_ges:
            zwróć 1

        source = self._ent_handler.resolveEntity(pubid, sysid)
        source = saxutils.prepare_input_source(source,
                                               self._source.getSystemId() albo
                                               "")

        self._entity_stack.append((self._parser, self._source))
        self._parser = self._parser.ExternalEntityParserCreate(context)
        self._source = source

        spróbuj:
            xmlreader.IncrementalParser.parse(self, source)
        wyjąwszy:
            zwróć 0  # FIXME: save error info here?

        (self._parser, self._source) = self._entity_stack[-1]
        usuń self._entity_stack[-1]
        zwróć 1

    def skipped_entity_handler(self, name, is_pe):
        jeżeli is_pe:
            # The SAX spec requires to report skipped PEs przy a '%'
            name = '%'+name
        self._cont_handler.skippedEntity(name)

# ---

def create_parser(*args, **kwargs):
    zwróć ExpatParser(*args, **kwargs)

# ---

jeżeli __name__ == "__main__":
    zaimportuj xml.sax.saxutils
    p = create_parser()
    p.setContentHandler(xml.sax.saxutils.XMLGenerator())
    p.setErrorHandler(xml.sax.ErrorHandler())
    p.parse("http://www.ibiblio.org/xml/examples/shakespeare/hamlet.xml")
