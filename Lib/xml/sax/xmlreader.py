"""An XML Reader jest the SAX 2 name dla an XML parser. XML Parsers
should be based on this code. """

z . zaimportuj handler

z ._exceptions zaimportuj SAXNotSupportedException, SAXNotRecognizedException


# ===== XMLREADER =====

klasa XMLReader:
    """Interface dla reading an XML document using callbacks.

    XMLReader jest the interface that an XML parser's SAX2 driver must
    implement. This interface allows an application to set oraz query
    features oraz properties w the parser, to register event handlers
    dla document processing, oraz to initiate a document parse.

    All SAX interfaces are assumed to be synchronous: the parse
    methods must nie zwróć until parsing jest complete, oraz readers
    must wait dla an event-handler callback to zwróć before reporting
    the next event."""

    def __init__(self):
        self._cont_handler = handler.ContentHandler()
        self._dtd_handler = handler.DTDHandler()
        self._ent_handler = handler.EntityResolver()
        self._err_handler = handler.ErrorHandler()

    def parse(self, source):
        "Parse an XML document z a system identifier albo an InputSource."
        podnieś NotImplementedError("This method must be implemented!")

    def getContentHandler(self):
        "Returns the current ContentHandler."
        zwróć self._cont_handler

    def setContentHandler(self, handler):
        "Registers a new object to receive document content events."
        self._cont_handler = handler

    def getDTDHandler(self):
        "Returns the current DTD handler."
        zwróć self._dtd_handler

    def setDTDHandler(self, handler):
        "Register an object to receive basic DTD-related events."
        self._dtd_handler = handler

    def getEntityResolver(self):
        "Returns the current EntityResolver."
        zwróć self._ent_handler

    def setEntityResolver(self, resolver):
        "Register an object to resolve external entities."
        self._ent_handler = resolver

    def getErrorHandler(self):
        "Returns the current ErrorHandler."
        zwróć self._err_handler

    def setErrorHandler(self, handler):
        "Register an object to receive error-message events."
        self._err_handler = handler

    def setLocale(self, locale):
        """Allow an application to set the locale dla errors oraz warnings.

        SAX parsers are nie required to provide localization dla errors
        oraz warnings; jeżeli they cannot support the requested locale,
        however, they must podnieś a SAX exception. Applications may
        request a locale change w the middle of a parse."""
        podnieś SAXNotSupportedException("Locale support nie implemented")

    def getFeature(self, name):
        "Looks up oraz returns the state of a SAX2 feature."
        podnieś SAXNotRecognizedException("Feature '%s' nie recognized" % name)

    def setFeature(self, name, state):
        "Sets the state of a SAX2 feature."
        podnieś SAXNotRecognizedException("Feature '%s' nie recognized" % name)

    def getProperty(self, name):
        "Looks up oraz returns the value of a SAX2 property."
        podnieś SAXNotRecognizedException("Property '%s' nie recognized" % name)

    def setProperty(self, name, value):
        "Sets the value of a SAX2 property."
        podnieś SAXNotRecognizedException("Property '%s' nie recognized" % name)

klasa IncrementalParser(XMLReader):
    """This interface adds three extra methods to the XMLReader
    interface that allow XML parsers to support incremental
    parsing. Support dla this interface jest optional, since nie all
    underlying XML parsers support this functionality.

    When the parser jest instantiated it jest ready to begin accepting
    data z the feed method immediately. After parsing has been
    finished przy a call to close the reset method must be called to
    make the parser ready to accept new data, either z feed albo
    using the parse method.

    Note that these methods must _not_ be called during parsing, that
    is, after parse has been called oraz before it returns.

    By default, the klasa also implements the parse method of the XMLReader
    interface using the feed, close oraz reset methods of the
    IncrementalParser interface jako a convenience to SAX 2.0 driver
    writers."""

    def __init__(self, bufsize=2**16):
        self._bufsize = bufsize
        XMLReader.__init__(self)

    def parse(self, source):
        z . zaimportuj saxutils
        source = saxutils.prepare_input_source(source)

        self.prepareParser(source)
        file = source.getCharacterStream()
        jeżeli file jest Nic:
            file = source.getByteStream()
        buffer = file.read(self._bufsize)
        dopóki buffer:
            self.feed(buffer)
            buffer = file.read(self._bufsize)
        self.close()

    def feed(self, data):
        """This method gives the raw XML data w the data parameter to
        the parser oraz makes it parse the data, emitting the
        corresponding events. It jest allowed dla XML constructs to be
        split across several calls to feed.

        feed may podnieś SAXException."""
        podnieś NotImplementedError("This method must be implemented!")

    def prepareParser(self, source):
        """This method jest called by the parse implementation to allow
        the SAX 2.0 driver to prepare itself dla parsing."""
        podnieś NotImplementedError("prepareParser must be overridden!")

    def close(self):
        """This method jest called when the entire XML document has been
        dalejed to the parser through the feed method, to notify the
        parser that there are no more data. This allows the parser to
        do the final checks on the document oraz empty the internal
        data buffer.

        The parser will nie be ready to parse another document until
        the reset method has been called.

        close may podnieś SAXException."""
        podnieś NotImplementedError("This method must be implemented!")

    def reset(self):
        """This method jest called after close has been called to reset
        the parser so that it jest ready to parse new documents. The
        results of calling parse albo feed after close without calling
        reset are undefined."""
        podnieś NotImplementedError("This method must be implemented!")

# ===== LOCATOR =====

klasa Locator:
    """Interface dla associating a SAX event przy a document
    location. A locator object will zwróć valid results only during
    calls to DocumentHandler methods; at any other time, the
    results are unpredictable."""

    def getColumnNumber(self):
        "Return the column number where the current event ends."
        zwróć -1

    def getLineNumber(self):
        "Return the line number where the current event ends."
        zwróć -1

    def getPublicId(self):
        "Return the public identifier dla the current event."
        zwróć Nic

    def getSystemId(self):
        "Return the system identifier dla the current event."
        zwróć Nic

# ===== INPUTSOURCE =====

klasa InputSource:
    """Encapsulation of the information needed by the XMLReader to
    read entities.

    This klasa may include information about the public identifier,
    system identifier, byte stream (possibly przy character encoding
    information) and/or the character stream of an entity.

    Applications will create objects of this klasa dla use w the
    XMLReader.parse method oraz dla returning from
    EntityResolver.resolveEntity.

    An InputSource belongs to the application, the XMLReader jest nie
    allowed to modify InputSource objects dalejed to it z the
    application, although it may make copies oraz modify those."""

    def __init__(self, system_id = Nic):
        self.__system_id = system_id
        self.__public_id = Nic
        self.__encoding  = Nic
        self.__bytefile  = Nic
        self.__charfile  = Nic

    def setPublicId(self, public_id):
        "Sets the public identifier of this InputSource."
        self.__public_id = public_id

    def getPublicId(self):
        "Returns the public identifier of this InputSource."
        zwróć self.__public_id

    def setSystemId(self, system_id):
        "Sets the system identifier of this InputSource."
        self.__system_id = system_id

    def getSystemId(self):
        "Returns the system identifier of this InputSource."
        zwróć self.__system_id

    def setEncoding(self, encoding):
        """Sets the character encoding of this InputSource.

        The encoding must be a string acceptable dla an XML encoding
        declaration (see section 4.3.3 of the XML recommendation).

        The encoding attribute of the InputSource jest ignored jeżeli the
        InputSource also contains a character stream."""
        self.__encoding = encoding

    def getEncoding(self):
        "Get the character encoding of this InputSource."
        zwróć self.__encoding

    def setByteStream(self, bytefile):
        """Set the byte stream (a Python file-like object which does
        nie perform byte-to-character conversion) dla this input
        source.

        The SAX parser will ignore this jeżeli there jest also a character
        stream specified, but it will use a byte stream w preference
        to opening a URI connection itself.

        If the application knows the character encoding of the byte
        stream, it should set it przy the setEncoding method."""
        self.__bytefile = bytefile

    def getByteStream(self):
        """Get the byte stream dla this input source.

        The getEncoding method will zwróć the character encoding for
        this byte stream, albo Nic jeżeli unknown."""
        zwróć self.__bytefile

    def setCharacterStream(self, charfile):
        """Set the character stream dla this input source. (The stream
        must be a Python 2.0 Unicode-wrapped file-like that performs
        conversion to Unicode strings.)

        If there jest a character stream specified, the SAX parser will
        ignore any byte stream oraz will nie attempt to open a URI
        connection to the system identifier."""
        self.__charfile = charfile

    def getCharacterStream(self):
        "Get the character stream dla this input source."
        zwróć self.__charfile

# ===== ATTRIBUTESIMPL =====

klasa AttributesImpl:

    def __init__(self, attrs):
        """Non-NS-aware implementation.

        attrs should be of the form {name : value}."""
        self._attrs = attrs

    def getLength(self):
        zwróć len(self._attrs)

    def getType(self, name):
        zwróć "CDATA"

    def getValue(self, name):
        zwróć self._attrs[name]

    def getValueByQName(self, name):
        zwróć self._attrs[name]

    def getNameByQName(self, name):
        jeżeli name nie w self._attrs:
            podnieś KeyError(name)
        zwróć name

    def getQNameByName(self, name):
        jeżeli name nie w self._attrs:
            podnieś KeyError(name)
        zwróć name

    def getNames(self):
        zwróć list(self._attrs.keys())

    def getQNames(self):
        zwróć list(self._attrs.keys())

    def __len__(self):
        zwróć len(self._attrs)

    def __getitem__(self, name):
        zwróć self._attrs[name]

    def keys(self):
        zwróć list(self._attrs.keys())

    def __contains__(self, name):
        zwróć name w self._attrs

    def get(self, name, alternative=Nic):
        zwróć self._attrs.get(name, alternative)

    def copy(self):
        zwróć self.__class__(self._attrs)

    def items(self):
        zwróć list(self._attrs.items())

    def values(self):
        zwróć list(self._attrs.values())

# ===== ATTRIBUTESNSIMPL =====

klasa AttributesNSImpl(AttributesImpl):

    def __init__(self, attrs, qnames):
        """NS-aware implementation.

        attrs should be of the form {(ns_uri, lname): value, ...}.
        qnames of the form {(ns_uri, lname): qname, ...}."""
        self._attrs = attrs
        self._qnames = qnames

    def getValueByQName(self, name):
        dla (nsname, qname) w self._qnames.items():
            jeżeli qname == name:
                zwróć self._attrs[nsname]

        podnieś KeyError(name)

    def getNameByQName(self, name):
        dla (nsname, qname) w self._qnames.items():
            jeżeli qname == name:
                zwróć nsname

        podnieś KeyError(name)

    def getQNameByName(self, name):
        zwróć self._qnames[name]

    def getQNames(self):
        zwróć list(self._qnames.values())

    def copy(self):
        zwróć self.__class__(self._attrs, self._qnames)


def _test():
    XMLReader()
    IncrementalParser()
    Locator()

jeżeli __name__ == "__main__":
    _test()
