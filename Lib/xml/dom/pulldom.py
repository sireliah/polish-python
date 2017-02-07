zaimportuj xml.sax
zaimportuj xml.sax.handler

START_ELEMENT = "START_ELEMENT"
END_ELEMENT = "END_ELEMENT"
COMMENT = "COMMENT"
START_DOCUMENT = "START_DOCUMENT"
END_DOCUMENT = "END_DOCUMENT"
PROCESSING_INSTRUCTION = "PROCESSING_INSTRUCTION"
IGNORABLE_WHITESPACE = "IGNORABLE_WHITESPACE"
CHARACTERS = "CHARACTERS"

klasa PullDOM(xml.sax.ContentHandler):
    _locator = Nic
    document = Nic

    def __init__(self, documentFactory=Nic):
        z xml.dom zaimportuj XML_NAMESPACE
        self.documentFactory = documentFactory
        self.firstEvent = [Nic, Nic]
        self.lastEvent = self.firstEvent
        self.elementStack = []
        self.push = self.elementStack.append
        spróbuj:
            self.pop = self.elementStack.pop
        wyjąwszy AttributeError:
            # use class' pop instead
            dalej
        self._ns_contexts = [{XML_NAMESPACE:'xml'}] # contains uri -> prefix dicts
        self._current_context = self._ns_contexts[-1]
        self.pending_events = []

    def pop(self):
        result = self.elementStack[-1]
        usuń self.elementStack[-1]
        zwróć result

    def setDocumentLocator(self, locator):
        self._locator = locator

    def startPrefixMapping(self, prefix, uri):
        jeżeli nie hasattr(self, '_xmlns_attrs'):
            self._xmlns_attrs = []
        self._xmlns_attrs.append((prefix albo 'xmlns', uri))
        self._ns_contexts.append(self._current_context.copy())
        self._current_context[uri] = prefix albo Nic

    def endPrefixMapping(self, prefix):
        self._current_context = self._ns_contexts.pop()

    def startElementNS(self, name, tagName , attrs):
        # Retrieve xml namespace declaration attributes.
        xmlns_uri = 'http://www.w3.org/2000/xmlns/'
        xmlns_attrs = getattr(self, '_xmlns_attrs', Nic)
        jeżeli xmlns_attrs jest nie Nic:
            dla aname, value w xmlns_attrs:
                attrs._attrs[(xmlns_uri, aname)] = value
            self._xmlns_attrs = []
        uri, localname = name
        jeżeli uri:
            # When using namespaces, the reader may albo may nie
            # provide us przy the original name. If not, create
            # *a* valid tagName z the current context.
            jeżeli tagName jest Nic:
                prefix = self._current_context[uri]
                jeżeli prefix:
                    tagName = prefix + ":" + localname
                inaczej:
                    tagName = localname
            jeżeli self.document:
                node = self.document.createElementNS(uri, tagName)
            inaczej:
                node = self.buildDocument(uri, tagName)
        inaczej:
            # When the tagname jest nie prefixed, it just appears as
            # localname
            jeżeli self.document:
                node = self.document.createElement(localname)
            inaczej:
                node = self.buildDocument(Nic, localname)

        dla aname,value w attrs.items():
            a_uri, a_localname = aname
            jeżeli a_uri == xmlns_uri:
                jeżeli a_localname == 'xmlns':
                    qname = a_localname
                inaczej:
                    qname = 'xmlns:' + a_localname
                attr = self.document.createAttributeNS(a_uri, qname)
                node.setAttributeNodeNS(attr)
            albo_inaczej a_uri:
                prefix = self._current_context[a_uri]
                jeżeli prefix:
                    qname = prefix + ":" + a_localname
                inaczej:
                    qname = a_localname
                attr = self.document.createAttributeNS(a_uri, qname)
                node.setAttributeNodeNS(attr)
            inaczej:
                attr = self.document.createAttribute(a_localname)
                node.setAttributeNode(attr)
            attr.value = value

        self.lastEvent[1] = [(START_ELEMENT, node), Nic]
        self.lastEvent = self.lastEvent[1]
        self.push(node)

    def endElementNS(self, name, tagName):
        self.lastEvent[1] = [(END_ELEMENT, self.pop()), Nic]
        self.lastEvent = self.lastEvent[1]

    def startElement(self, name, attrs):
        jeżeli self.document:
            node = self.document.createElement(name)
        inaczej:
            node = self.buildDocument(Nic, name)

        dla aname,value w attrs.items():
            attr = self.document.createAttribute(aname)
            attr.value = value
            node.setAttributeNode(attr)

        self.lastEvent[1] = [(START_ELEMENT, node), Nic]
        self.lastEvent = self.lastEvent[1]
        self.push(node)

    def endElement(self, name):
        self.lastEvent[1] = [(END_ELEMENT, self.pop()), Nic]
        self.lastEvent = self.lastEvent[1]

    def comment(self, s):
        jeżeli self.document:
            node = self.document.createComment(s)
            self.lastEvent[1] = [(COMMENT, node), Nic]
            self.lastEvent = self.lastEvent[1]
        inaczej:
            event = [(COMMENT, s), Nic]
            self.pending_events.append(event)

    def processingInstruction(self, target, data):
        jeżeli self.document:
            node = self.document.createProcessingInstruction(target, data)
            self.lastEvent[1] = [(PROCESSING_INSTRUCTION, node), Nic]
            self.lastEvent = self.lastEvent[1]
        inaczej:
            event = [(PROCESSING_INSTRUCTION, target, data), Nic]
            self.pending_events.append(event)

    def ignorableWhitespace(self, chars):
        node = self.document.createTextNode(chars)
        self.lastEvent[1] = [(IGNORABLE_WHITESPACE, node), Nic]
        self.lastEvent = self.lastEvent[1]

    def characters(self, chars):
        node = self.document.createTextNode(chars)
        self.lastEvent[1] = [(CHARACTERS, node), Nic]
        self.lastEvent = self.lastEvent[1]

    def startDocument(self):
        jeżeli self.documentFactory jest Nic:
            zaimportuj xml.dom.minidom
            self.documentFactory = xml.dom.minidom.Document.implementation

    def buildDocument(self, uri, tagname):
        # Can't do that w startDocument, since we need the tagname
        # XXX: obtain DocumentType
        node = self.documentFactory.createDocument(uri, tagname, Nic)
        self.document = node
        self.lastEvent[1] = [(START_DOCUMENT, node), Nic]
        self.lastEvent = self.lastEvent[1]
        self.push(node)
        # Put everything we have seen so far into the document
        dla e w self.pending_events:
            jeżeli e[0][0] == PROCESSING_INSTRUCTION:
                _,target,data = e[0]
                n = self.document.createProcessingInstruction(target, data)
                e[0] = (PROCESSING_INSTRUCTION, n)
            albo_inaczej e[0][0] == COMMENT:
                n = self.document.createComment(e[0][1])
                e[0] = (COMMENT, n)
            inaczej:
                podnieś AssertionError("Unknown pending event ",e[0][0])
            self.lastEvent[1] = e
            self.lastEvent = e
        self.pending_events = Nic
        zwróć node.firstChild

    def endDocument(self):
        self.lastEvent[1] = [(END_DOCUMENT, self.document), Nic]
        self.pop()

    def clear(self):
        "clear(): Explicitly release parsing structures"
        self.document = Nic

klasa ErrorHandler:
    def warning(self, exception):
        print(exception)
    def error(self, exception):
        podnieś exception
    def fatalError(self, exception):
        podnieś exception

klasa DOMEventStream:
    def __init__(self, stream, parser, bufsize):
        self.stream = stream
        self.parser = parser
        self.bufsize = bufsize
        jeżeli nie hasattr(self.parser, 'feed'):
            self.getEvent = self._slurp
        self.reset()

    def reset(self):
        self.pulldom = PullDOM()
        # This content handler relies on namespace support
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 1)
        self.parser.setContentHandler(self.pulldom)

    def __getitem__(self, pos):
        rc = self.getEvent()
        jeżeli rc:
            zwróć rc
        podnieś IndexError

    def __next__(self):
        rc = self.getEvent()
        jeżeli rc:
            zwróć rc
        podnieś StopIteration

    def __iter__(self):
        zwróć self

    def expandNode(self, node):
        event = self.getEvent()
        parents = [node]
        dopóki event:
            token, cur_node = event
            jeżeli cur_node jest node:
                zwróć
            jeżeli token != END_ELEMENT:
                parents[-1].appendChild(cur_node)
            jeżeli token == START_ELEMENT:
                parents.append(cur_node)
            albo_inaczej token == END_ELEMENT:
                usuń parents[-1]
            event = self.getEvent()

    def getEvent(self):
        # use IncrementalParser interface, so we get the desired
        # pull effect
        jeżeli nie self.pulldom.firstEvent[1]:
            self.pulldom.lastEvent = self.pulldom.firstEvent
        dopóki nie self.pulldom.firstEvent[1]:
            buf = self.stream.read(self.bufsize)
            jeżeli nie buf:
                self.parser.close()
                zwróć Nic
            self.parser.feed(buf)
        rc = self.pulldom.firstEvent[1][0]
        self.pulldom.firstEvent[1] = self.pulldom.firstEvent[1][1]
        zwróć rc

    def _slurp(self):
        """ Fallback replacement dla getEvent() using the
            standard SAX2 interface, which means we slurp the
            SAX events into memory (no performance gain, but
            we are compatible to all SAX parsers).
        """
        self.parser.parse(self.stream)
        self.getEvent = self._emit
        zwróć self._emit()

    def _emit(self):
        """ Fallback replacement dla getEvent() that emits
            the events that _slurp() read previously.
        """
        rc = self.pulldom.firstEvent[1][0]
        self.pulldom.firstEvent[1] = self.pulldom.firstEvent[1][1]
        zwróć rc

    def clear(self):
        """clear(): Explicitly release parsing objects"""
        self.pulldom.clear()
        usuń self.pulldom
        self.parser = Nic
        self.stream = Nic

klasa SAX2DOM(PullDOM):

    def startElementNS(self, name, tagName , attrs):
        PullDOM.startElementNS(self, name, tagName, attrs)
        curNode = self.elementStack[-1]
        parentNode = self.elementStack[-2]
        parentNode.appendChild(curNode)

    def startElement(self, name, attrs):
        PullDOM.startElement(self, name, attrs)
        curNode = self.elementStack[-1]
        parentNode = self.elementStack[-2]
        parentNode.appendChild(curNode)

    def processingInstruction(self, target, data):
        PullDOM.processingInstruction(self, target, data)
        node = self.lastEvent[0][1]
        parentNode = self.elementStack[-1]
        parentNode.appendChild(node)

    def ignorableWhitespace(self, chars):
        PullDOM.ignorableWhitespace(self, chars)
        node = self.lastEvent[0][1]
        parentNode = self.elementStack[-1]
        parentNode.appendChild(node)

    def characters(self, chars):
        PullDOM.characters(self, chars)
        node = self.lastEvent[0][1]
        parentNode = self.elementStack[-1]
        parentNode.appendChild(node)


default_bufsize = (2 ** 14) - 20

def parse(stream_or_string, parser=Nic, bufsize=Nic):
    jeżeli bufsize jest Nic:
        bufsize = default_bufsize
    jeżeli isinstance(stream_or_string, str):
        stream = open(stream_or_string, 'rb')
    inaczej:
        stream = stream_or_string
    jeżeli nie parser:
        parser = xml.sax.make_parser()
    zwróć DOMEventStream(stream, parser, bufsize)

def parseString(string, parser=Nic):
    z io zaimportuj StringIO

    bufsize = len(string)
    buf = StringIO(string)
    jeżeli nie parser:
        parser = xml.sax.make_parser()
    zwróć DOMEventStream(buf, parser, bufsize)
