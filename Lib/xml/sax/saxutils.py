"""\
A library of useful helper classes to the SAX classes, dla the
convenience of application oraz driver writers.
"""

zaimportuj os, urllib.parse, urllib.request
zaimportuj io
zaimportuj codecs
z . zaimportuj handler
z . zaimportuj xmlreader

def __dict_replace(s, d):
    """Replace substrings of a string using a dictionary."""
    dla key, value w d.items():
        s = s.replace(key, value)
    zwróć s

def escape(data, entities={}):
    """Escape &, <, oraz > w a string of data.

    You can escape other strings of data by dalejing a dictionary as
    the optional entities parameter.  The keys oraz values must all be
    strings; each key will be replaced przy its corresponding value.
    """

    # must do ampersand first
    data = data.replace("&", "&amp;")
    data = data.replace(">", "&gt;")
    data = data.replace("<", "&lt;")
    jeżeli entities:
        data = __dict_replace(data, entities)
    zwróć data

def unescape(data, entities={}):
    """Unescape &amp;, &lt;, oraz &gt; w a string of data.

    You can unescape other strings of data by dalejing a dictionary as
    the optional entities parameter.  The keys oraz values must all be
    strings; each key will be replaced przy its corresponding value.
    """
    data = data.replace("&lt;", "<")
    data = data.replace("&gt;", ">")
    jeżeli entities:
        data = __dict_replace(data, entities)
    # must do ampersand last
    zwróć data.replace("&amp;", "&")

def quoteattr(data, entities={}):
    """Escape oraz quote an attribute value.

    Escape &, <, oraz > w a string of data, then quote it dla use as
    an attribute value.  The \" character will be escaped jako well, if
    necessary.

    You can escape other strings of data by dalejing a dictionary as
    the optional entities parameter.  The keys oraz values must all be
    strings; each key will be replaced przy its corresponding value.
    """
    entities = entities.copy()
    entities.update({'\n': '&#10;', '\r': '&#13;', '\t':'&#9;'})
    data = escape(data, entities)
    jeżeli '"' w data:
        jeżeli "'" w data:
            data = '"%s"' % data.replace('"', "&quot;")
        inaczej:
            data = "'%s'" % data
    inaczej:
        data = '"%s"' % data
    zwróć data


def _gettextwriter(out, encoding):
    jeżeli out jest Nic:
        zaimportuj sys
        zwróć sys.stdout

    jeżeli isinstance(out, io.TextIOBase):
        # use a text writer jako jest
        zwróć out

    jeżeli isinstance(out, (codecs.StreamWriter, codecs.StreamReaderWriter)):
        # use a codecs stream writer jako jest
        zwróć out

    # wrap a binary writer przy TextIOWrapper
    jeżeli isinstance(out, io.RawIOBase):
        # Keep the original file open when the TextIOWrapper jest
        # destroyed
        klasa _wrapper:
            __class__ = out.__class__
            def __getattr__(self, name):
                zwróć getattr(out, name)
        buffer = _wrapper()
        buffer.close = lambda: Nic
    inaczej:
        # This jest to handle dalejed objects that aren't w the
        # IOBase hierarchy, but just have a write method
        buffer = io.BufferedIOBase()
        buffer.writable = lambda: Prawda
        buffer.write = out.write
        spróbuj:
            # TextIOWrapper uses this methods to determine
            # jeżeli BOM (dla UTF-16, etc) should be added
            buffer.seekable = out.seekable
            buffer.tell = out.tell
        wyjąwszy AttributeError:
            dalej
    zwróć io.TextIOWrapper(buffer, encoding=encoding,
                            errors='xmlcharrefreplace',
                            newline='\n',
                            write_through=Prawda)

klasa XMLGenerator(handler.ContentHandler):

    def __init__(self, out=Nic, encoding="iso-8859-1", short_empty_elements=Nieprawda):
        handler.ContentHandler.__init__(self)
        out = _gettextwriter(out, encoding)
        self._write = out.write
        self._flush = out.flush
        self._ns_contexts = [{}] # contains uri -> prefix dicts
        self._current_context = self._ns_contexts[-1]
        self._undeclared_ns_maps = []
        self._encoding = encoding
        self._short_empty_elements = short_empty_elements
        self._pending_start_element = Nieprawda

    def _qname(self, name):
        """Builds a qualified name z a (ns_url, localname) pair"""
        jeżeli name[0]:
            # Per http://www.w3.org/XML/1998/namespace, The 'xml' prefix jest
            # bound by definition to http://www.w3.org/XML/1998/namespace.  It
            # does nie need to be declared oraz will nie usually be found w
            # self._current_context.
            jeżeli 'http://www.w3.org/XML/1998/namespace' == name[0]:
                zwróć 'xml:' + name[1]
            # The name jest w a non-empty namespace
            prefix = self._current_context[name[0]]
            jeżeli prefix:
                # If it jest nie the default namespace, prepend the prefix
                zwróć prefix + ":" + name[1]
        # Return the unqualified name
        zwróć name[1]

    def _finish_pending_start_element(self,endElement=Nieprawda):
        jeżeli self._pending_start_element:
            self._write('>')
            self._pending_start_element = Nieprawda

    # ContentHandler methods

    def startDocument(self):
        self._write('<?xml version="1.0" encoding="%s"?>\n' %
                        self._encoding)

    def endDocument(self):
        self._flush()

    def startPrefixMapping(self, prefix, uri):
        self._ns_contexts.append(self._current_context.copy())
        self._current_context[uri] = prefix
        self._undeclared_ns_maps.append((prefix, uri))

    def endPrefixMapping(self, prefix):
        self._current_context = self._ns_contexts[-1]
        usuń self._ns_contexts[-1]

    def startElement(self, name, attrs):
        self._finish_pending_start_element()
        self._write('<' + name)
        dla (name, value) w attrs.items():
            self._write(' %s=%s' % (name, quoteattr(value)))
        jeżeli self._short_empty_elements:
            self._pending_start_element = Prawda
        inaczej:
            self._write(">")

    def endElement(self, name):
        jeżeli self._pending_start_element:
            self._write('/>')
            self._pending_start_element = Nieprawda
        inaczej:
            self._write('</%s>' % name)

    def startElementNS(self, name, qname, attrs):
        self._finish_pending_start_element()
        self._write('<' + self._qname(name))

        dla prefix, uri w self._undeclared_ns_maps:
            jeżeli prefix:
                self._write(' xmlns:%s="%s"' % (prefix, uri))
            inaczej:
                self._write(' xmlns="%s"' % uri)
        self._undeclared_ns_maps = []

        dla (name, value) w attrs.items():
            self._write(' %s=%s' % (self._qname(name), quoteattr(value)))
        jeżeli self._short_empty_elements:
            self._pending_start_element = Prawda
        inaczej:
            self._write(">")

    def endElementNS(self, name, qname):
        jeżeli self._pending_start_element:
            self._write('/>')
            self._pending_start_element = Nieprawda
        inaczej:
            self._write('</%s>' % self._qname(name))

    def characters(self, content):
        jeżeli content:
            self._finish_pending_start_element()
            jeżeli nie isinstance(content, str):
                content = str(content, self._encoding)
            self._write(escape(content))

    def ignorableWhitespace(self, content):
        jeżeli content:
            self._finish_pending_start_element()
            jeżeli nie isinstance(content, str):
                content = str(content, self._encoding)
            self._write(content)

    def processingInstruction(self, target, data):
        self._finish_pending_start_element()
        self._write('<?%s %s?>' % (target, data))


klasa XMLFilterBase(xmlreader.XMLReader):
    """This klasa jest designed to sit between an XMLReader oraz the
    client application's event handlers.  By default, it does nothing
    but dalej requests up to the reader oraz events on to the handlers
    unmodified, but subclasses can override specific methods to modify
    the event stream albo the configuration requests jako they dalej
    through."""

    def __init__(self, parent = Nic):
        xmlreader.XMLReader.__init__(self)
        self._parent = parent

    # ErrorHandler methods

    def error(self, exception):
        self._err_handler.error(exception)

    def fatalError(self, exception):
        self._err_handler.fatalError(exception)

    def warning(self, exception):
        self._err_handler.warning(exception)

    # ContentHandler methods

    def setDocumentLocator(self, locator):
        self._cont_handler.setDocumentLocator(locator)

    def startDocument(self):
        self._cont_handler.startDocument()

    def endDocument(self):
        self._cont_handler.endDocument()

    def startPrefixMapping(self, prefix, uri):
        self._cont_handler.startPrefixMapping(prefix, uri)

    def endPrefixMapping(self, prefix):
        self._cont_handler.endPrefixMapping(prefix)

    def startElement(self, name, attrs):
        self._cont_handler.startElement(name, attrs)

    def endElement(self, name):
        self._cont_handler.endElement(name)

    def startElementNS(self, name, qname, attrs):
        self._cont_handler.startElementNS(name, qname, attrs)

    def endElementNS(self, name, qname):
        self._cont_handler.endElementNS(name, qname)

    def characters(self, content):
        self._cont_handler.characters(content)

    def ignorableWhitespace(self, chars):
        self._cont_handler.ignorableWhitespace(chars)

    def processingInstruction(self, target, data):
        self._cont_handler.processingInstruction(target, data)

    def skippedEntity(self, name):
        self._cont_handler.skippedEntity(name)

    # DTDHandler methods

    def notationDecl(self, name, publicId, systemId):
        self._dtd_handler.notationDecl(name, publicId, systemId)

    def unparsedEntityDecl(self, name, publicId, systemId, ndata):
        self._dtd_handler.unparsedEntityDecl(name, publicId, systemId, ndata)

    # EntityResolver methods

    def resolveEntity(self, publicId, systemId):
        zwróć self._ent_handler.resolveEntity(publicId, systemId)

    # XMLReader methods

    def parse(self, source):
        self._parent.setContentHandler(self)
        self._parent.setErrorHandler(self)
        self._parent.setEntityResolver(self)
        self._parent.setDTDHandler(self)
        self._parent.parse(source)

    def setLocale(self, locale):
        self._parent.setLocale(locale)

    def getFeature(self, name):
        zwróć self._parent.getFeature(name)

    def setFeature(self, name, state):
        self._parent.setFeature(name, state)

    def getProperty(self, name):
        zwróć self._parent.getProperty(name)

    def setProperty(self, name, value):
        self._parent.setProperty(name, value)

    # XMLFilter methods

    def getParent(self):
        zwróć self._parent

    def setParent(self, parent):
        self._parent = parent

# --- Utility functions

def prepare_input_source(source, base=""):
    """This function takes an InputSource oraz an optional base URL oraz
    returns a fully resolved InputSource object ready dla reading."""

    jeżeli isinstance(source, str):
        source = xmlreader.InputSource(source)
    albo_inaczej hasattr(source, "read"):
        f = source
        source = xmlreader.InputSource()
        jeżeli isinstance(f.read(0), str):
            source.setCharacterStream(f)
        inaczej:
            source.setByteStream(f)
        jeżeli hasattr(f, "name") oraz isinstance(f.name, str):
            source.setSystemId(f.name)

    jeżeli source.getCharacterStream() jest Nic oraz source.getByteStream() jest Nic:
        sysid = source.getSystemId()
        basehead = os.path.dirname(os.path.normpath(base))
        sysidfilename = os.path.join(basehead, sysid)
        jeżeli os.path.isfile(sysidfilename):
            source.setSystemId(sysidfilename)
            f = open(sysidfilename, "rb")
        inaczej:
            source.setSystemId(urllib.parse.urljoin(base, sysid))
            f = urllib.request.urlopen(source.getSystemId())

        source.setByteStream(f)

    zwróć source
