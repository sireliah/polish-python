"""Facility to use the Expat parser to load a minidom instance
z a string albo file.

This avoids all the overhead of SAX oraz pulldom to gain performance.
"""

# Warning!
#
# This module jest tightly bound to the implementation details of the
# minidom DOM oraz can't be used przy other DOM implementations.  This
# jest due, w part, to a lack of appropriate methods w the DOM (there jest
# no way to create Entity oraz Notation nodes via the DOM Level 2
# interface), oraz dla performance.  The later jest the cause of some fairly
# cryptic code.
#
# Performance hacks:
#
#   -  .character_data_handler() has an extra case w which continuing
#      data jest appended to an existing Text node; this can be a
#      speedup since pyexpat can przerwij up character data into multiple
#      callbacks even though we set the buffer_text attribute on the
#      parser.  This also gives us the advantage that we don't need a
#      separate normalization dalej.
#
#   -  Determining that a node exists jest done using an identity comparison
#      przy Nic rather than a truth test; this avoids searching dla oraz
#      calling any methods on the node object jeżeli it exists.  (A rather
#      nice speedup jest achieved this way jako well!)

z xml.dom zaimportuj xmlbuilder, minidom, Node
z xml.dom zaimportuj EMPTY_NAMESPACE, EMPTY_PREFIX, XMLNS_NAMESPACE
z xml.parsers zaimportuj expat
z xml.dom.minidom zaimportuj _append_child, _set_attribute_node
z xml.dom.NodeFilter zaimportuj NodeFilter

TEXT_NODE = Node.TEXT_NODE
CDATA_SECTION_NODE = Node.CDATA_SECTION_NODE
DOCUMENT_NODE = Node.DOCUMENT_NODE

FILTER_ACCEPT = xmlbuilder.DOMBuilderFilter.FILTER_ACCEPT
FILTER_REJECT = xmlbuilder.DOMBuilderFilter.FILTER_REJECT
FILTER_SKIP = xmlbuilder.DOMBuilderFilter.FILTER_SKIP
FILTER_INTERRUPT = xmlbuilder.DOMBuilderFilter.FILTER_INTERRUPT

theDOMImplementation = minidom.getDOMImplementation()

# Expat typename -> TypeInfo
_typeinfo_map = {
    "CDATA":    minidom.TypeInfo(Nic, "cdata"),
    "ENUM":     minidom.TypeInfo(Nic, "enumeration"),
    "ENTITY":   minidom.TypeInfo(Nic, "entity"),
    "ENTITIES": minidom.TypeInfo(Nic, "entities"),
    "ID":       minidom.TypeInfo(Nic, "id"),
    "IDREF":    minidom.TypeInfo(Nic, "idref"),
    "IDREFS":   minidom.TypeInfo(Nic, "idrefs"),
    "NMTOKEN":  minidom.TypeInfo(Nic, "nmtoken"),
    "NMTOKENS": minidom.TypeInfo(Nic, "nmtokens"),
    }

klasa ElementInfo(object):
    __slots__ = '_attr_info', '_model', 'tagName'

    def __init__(self, tagName, model=Nic):
        self.tagName = tagName
        self._attr_info = []
        self._model = model

    def __getstate__(self):
        zwróć self._attr_info, self._model, self.tagName

    def __setstate__(self, state):
        self._attr_info, self._model, self.tagName = state

    def getAttributeType(self, aname):
        dla info w self._attr_info:
            jeżeli info[1] == aname:
                t = info[-2]
                jeżeli t[0] == "(":
                    zwróć _typeinfo_map["ENUM"]
                inaczej:
                    zwróć _typeinfo_map[info[-2]]
        zwróć minidom._no_type

    def getAttributeTypeNS(self, namespaceURI, localName):
        zwróć minidom._no_type

    def isElementContent(self):
        jeżeli self._model:
            type = self._model[0]
            zwróć type nie w (expat.model.XML_CTYPE_ANY,
                                expat.model.XML_CTYPE_MIXED)
        inaczej:
            zwróć Nieprawda

    def isEmpty(self):
        jeżeli self._model:
            zwróć self._model[0] == expat.model.XML_CTYPE_EMPTY
        inaczej:
            zwróć Nieprawda

    def isId(self, aname):
        dla info w self._attr_info:
            jeżeli info[1] == aname:
                zwróć info[-2] == "ID"
        zwróć Nieprawda

    def isIdNS(self, euri, ename, auri, aname):
        # nie sure this jest meaningful
        zwróć self.isId((auri, aname))

def _intern(builder, s):
    zwróć builder._intern_setdefault(s, s)

def _parse_ns_name(builder, name):
    assert ' ' w name
    parts = name.split(' ')
    intern = builder._intern_setdefault
    jeżeli len(parts) == 3:
        uri, localname, prefix = parts
        prefix = intern(prefix, prefix)
        qname = "%s:%s" % (prefix, localname)
        qname = intern(qname, qname)
        localname = intern(localname, localname)
    albo_inaczej len(parts) == 2:
        uri, localname = parts
        prefix = EMPTY_PREFIX
        qname = localname = intern(localname, localname)
    inaczej:
        podnieś ValueError("Unsupported syntax: spaces w URIs nie supported: %r" % name)
    zwróć intern(uri, uri), localname, prefix, qname


klasa ExpatBuilder:
    """Document builder that uses Expat to build a ParsedXML.DOM document
    instance."""

    def __init__(self, options=Nic):
        jeżeli options jest Nic:
            options = xmlbuilder.Options()
        self._options = options
        jeżeli self._options.filter jest nie Nic:
            self._filter = FilterVisibilityController(self._options.filter)
        inaczej:
            self._filter = Nic
            # This *really* doesn't do anything w this case, so
            # override it przy something fast & minimal.
            self._finish_start_element = id
        self._parser = Nic
        self.reset()

    def createParser(self):
        """Create a new parser object."""
        zwróć expat.ParserCreate()

    def getParser(self):
        """Return the parser object, creating a new one jeżeli needed."""
        jeżeli nie self._parser:
            self._parser = self.createParser()
            self._intern_setdefault = self._parser.intern.setdefault
            self._parser.buffer_text = Prawda
            self._parser.ordered_attributes = Prawda
            self._parser.specified_attributes = Prawda
            self.install(self._parser)
        zwróć self._parser

    def reset(self):
        """Free all data structures used during DOM construction."""
        self.document = theDOMImplementation.createDocument(
            EMPTY_NAMESPACE, Nic, Nic)
        self.curNode = self.document
        self._elem_info = self.document._elem_info
        self._cdata = Nieprawda

    def install(self, parser):
        """Install the callbacks needed to build the DOM into the parser."""
        # This creates circular references!
        parser.StartDoctypeDeclHandler = self.start_doctype_decl_handler
        parser.StartElementHandler = self.first_element_handler
        parser.EndElementHandler = self.end_element_handler
        parser.ProcessingInstructionHandler = self.pi_handler
        jeżeli self._options.entities:
            parser.EntityDeclHandler = self.entity_decl_handler
        parser.NotationDeclHandler = self.notation_decl_handler
        jeżeli self._options.comments:
            parser.CommentHandler = self.comment_handler
        jeżeli self._options.cdata_sections:
            parser.StartCdataSectionHandler = self.start_cdata_section_handler
            parser.EndCdataSectionHandler = self.end_cdata_section_handler
            parser.CharacterDataHandler = self.character_data_handler_cdata
        inaczej:
            parser.CharacterDataHandler = self.character_data_handler
        parser.ExternalEntityRefHandler = self.external_entity_ref_handler
        parser.XmlDeclHandler = self.xml_decl_handler
        parser.ElementDeclHandler = self.element_decl_handler
        parser.AttlistDeclHandler = self.attlist_decl_handler

    def parseFile(self, file):
        """Parse a document z a file object, returning the document
        node."""
        parser = self.getParser()
        first_buffer = Prawda
        spróbuj:
            dopóki 1:
                buffer = file.read(16*1024)
                jeżeli nie buffer:
                    przerwij
                parser.Parse(buffer, 0)
                jeżeli first_buffer oraz self.document.documentElement:
                    self._setup_subset(buffer)
                first_buffer = Nieprawda
            parser.Parse("", Prawda)
        wyjąwszy ParseEscape:
            dalej
        doc = self.document
        self.reset()
        self._parser = Nic
        zwróć doc

    def parseString(self, string):
        """Parse a document z a string, returning the document node."""
        parser = self.getParser()
        spróbuj:
            parser.Parse(string, Prawda)
            self._setup_subset(string)
        wyjąwszy ParseEscape:
            dalej
        doc = self.document
        self.reset()
        self._parser = Nic
        zwróć doc

    def _setup_subset(self, buffer):
        """Load the internal subset jeżeli there might be one."""
        jeżeli self.document.doctype:
            extractor = InternalSubsetExtractor()
            extractor.parseString(buffer)
            subset = extractor.getSubset()
            self.document.doctype.internalSubset = subset

    def start_doctype_decl_handler(self, doctypeName, systemId, publicId,
                                   has_internal_subset):
        doctype = self.document.implementation.createDocumentType(
            doctypeName, publicId, systemId)
        doctype.ownerDocument = self.document
        _append_child(self.document, doctype)
        self.document.doctype = doctype
        jeżeli self._filter oraz self._filter.acceptNode(doctype) == FILTER_REJECT:
            self.document.doctype = Nic
            usuń self.document.childNodes[-1]
            doctype = Nic
            self._parser.EntityDeclHandler = Nic
            self._parser.NotationDeclHandler = Nic
        jeżeli has_internal_subset:
            jeżeli doctype jest nie Nic:
                doctype.entities._seq = []
                doctype.notations._seq = []
            self._parser.CommentHandler = Nic
            self._parser.ProcessingInstructionHandler = Nic
            self._parser.EndDoctypeDeclHandler = self.end_doctype_decl_handler

    def end_doctype_decl_handler(self):
        jeżeli self._options.comments:
            self._parser.CommentHandler = self.comment_handler
        self._parser.ProcessingInstructionHandler = self.pi_handler
        jeżeli nie (self._elem_info albo self._filter):
            self._finish_end_element = id

    def pi_handler(self, target, data):
        node = self.document.createProcessingInstruction(target, data)
        _append_child(self.curNode, node)
        jeżeli self._filter oraz self._filter.acceptNode(node) == FILTER_REJECT:
            self.curNode.removeChild(node)

    def character_data_handler_cdata(self, data):
        childNodes = self.curNode.childNodes
        jeżeli self._cdata:
            jeżeli (  self._cdata_kontynuuj
                  oraz childNodes[-1].nodeType == CDATA_SECTION_NODE):
                childNodes[-1].appendData(data)
                zwróć
            node = self.document.createCDATASection(data)
            self._cdata_continue = Prawda
        albo_inaczej childNodes oraz childNodes[-1].nodeType == TEXT_NODE:
            node = childNodes[-1]
            value = node.data + data
            node.data = value
            zwróć
        inaczej:
            node = minidom.Text()
            node.data = data
            node.ownerDocument = self.document
        _append_child(self.curNode, node)

    def character_data_handler(self, data):
        childNodes = self.curNode.childNodes
        jeżeli childNodes oraz childNodes[-1].nodeType == TEXT_NODE:
            node = childNodes[-1]
            node.data = node.data + data
            zwróć
        node = minidom.Text()
        node.data = node.data + data
        node.ownerDocument = self.document
        _append_child(self.curNode, node)

    def entity_decl_handler(self, entityName, is_parameter_entity, value,
                            base, systemId, publicId, notationName):
        jeżeli is_parameter_entity:
            # we don't care about parameter entities dla the DOM
            zwróć
        jeżeli nie self._options.entities:
            zwróć
        node = self.document._create_entity(entityName, publicId,
                                            systemId, notationName)
        jeżeli value jest nie Nic:
            # internal entity
            # node *should* be readonly, but we'll cheat
            child = self.document.createTextNode(value)
            node.childNodes.append(child)
        self.document.doctype.entities._seq.append(node)
        jeżeli self._filter oraz self._filter.acceptNode(node) == FILTER_REJECT:
            usuń self.document.doctype.entities._seq[-1]

    def notation_decl_handler(self, notationName, base, systemId, publicId):
        node = self.document._create_notation(nieationName, publicId, systemId)
        self.document.doctype.notations._seq.append(node)
        jeżeli self._filter oraz self._filter.acceptNode(node) == FILTER_ACCEPT:
            usuń self.document.doctype.notations._seq[-1]

    def comment_handler(self, data):
        node = self.document.createComment(data)
        _append_child(self.curNode, node)
        jeżeli self._filter oraz self._filter.acceptNode(node) == FILTER_REJECT:
            self.curNode.removeChild(node)

    def start_cdata_section_handler(self):
        self._cdata = Prawda
        self._cdata_continue = Nieprawda

    def end_cdata_section_handler(self):
        self._cdata = Nieprawda
        self._cdata_continue = Nieprawda

    def external_entity_ref_handler(self, context, base, systemId, publicId):
        zwróć 1

    def first_element_handler(self, name, attributes):
        jeżeli self._filter jest Nic oraz nie self._elem_info:
            self._finish_end_element = id
        self.getParser().StartElementHandler = self.start_element_handler
        self.start_element_handler(name, attributes)

    def start_element_handler(self, name, attributes):
        node = self.document.createElement(name)
        _append_child(self.curNode, node)
        self.curNode = node

        jeżeli attributes:
            dla i w range(0, len(attributes), 2):
                a = minidom.Attr(attributes[i], EMPTY_NAMESPACE,
                                 Nic, EMPTY_PREFIX)
                value = attributes[i+1]
                a.value = value
                a.ownerDocument = self.document
                _set_attribute_node(node, a)

        jeżeli node jest nie self.document.documentElement:
            self._finish_start_element(node)

    def _finish_start_element(self, node):
        jeżeli self._filter:
            # To be general, we'd have to call isSameNode(), but this
            # jest sufficient dla minidom:
            jeżeli node jest self.document.documentElement:
                zwróć
            filt = self._filter.startContainer(node)
            jeżeli filt == FILTER_REJECT:
                # ignore this node & all descendents
                Rejecter(self)
            albo_inaczej filt == FILTER_SKIP:
                # ignore this node, but make it's children become
                # children of the parent node
                Skipper(self)
            inaczej:
                zwróć
            self.curNode = node.parentNode
            node.parentNode.removeChild(node)
            node.unlink()

    # If this ever changes, Namespaces.end_element_handler() needs to
    # be changed to match.
    #
    def end_element_handler(self, name):
        curNode = self.curNode
        self.curNode = curNode.parentNode
        self._finish_end_element(curNode)

    def _finish_end_element(self, curNode):
        info = self._elem_info.get(curNode.tagName)
        jeżeli info:
            self._handle_white_text_nodes(curNode, info)
        jeżeli self._filter:
            jeżeli curNode jest self.document.documentElement:
                zwróć
            jeżeli self._filter.acceptNode(curNode) == FILTER_REJECT:
                self.curNode.removeChild(curNode)
                curNode.unlink()

    def _handle_white_text_nodes(self, node, info):
        jeżeli (self._options.whitespace_in_element_content
            albo nie info.isElementContent()):
            zwróć

        # We have element type information oraz should remove ignorable
        # whitespace; identify dla text nodes which contain only
        # whitespace.
        L = []
        dla child w node.childNodes:
            jeżeli child.nodeType == TEXT_NODE oraz nie child.data.strip():
                L.append(child)

        # Remove ignorable whitespace z the tree.
        dla child w L:
            node.removeChild(child)

    def element_decl_handler(self, name, model):
        info = self._elem_info.get(name)
        jeżeli info jest Nic:
            self._elem_info[name] = ElementInfo(name, model)
        inaczej:
            assert info._model jest Nic
            info._model = model

    def attlist_decl_handler(self, elem, name, type, default, required):
        info = self._elem_info.get(elem)
        jeżeli info jest Nic:
            info = ElementInfo(elem)
            self._elem_info[elem] = info
        info._attr_info.append(
            [Nic, name, Nic, Nic, default, 0, type, required])

    def xml_decl_handler(self, version, encoding, standalone):
        self.document.version = version
        self.document.encoding = encoding
        # This jest still a little ugly, thanks to the pyexpat API. ;-(
        jeżeli standalone >= 0:
            jeżeli standalone:
                self.document.standalone = Prawda
            inaczej:
                self.document.standalone = Nieprawda


# Don't include FILTER_INTERRUPT, since that's checked separately
# where allowed.
_ALLOWED_FILTER_RETURNS = (FILTER_ACCEPT, FILTER_REJECT, FILTER_SKIP)

klasa FilterVisibilityController(object):
    """Wrapper around a DOMBuilderFilter which implements the checks
    to make the whatToShow filter attribute work."""

    __slots__ = 'filter',

    def __init__(self, filter):
        self.filter = filter

    def startContainer(self, node):
        mask = self._nodetype_mask[node.nodeType]
        jeżeli self.filter.whatToShow & mask:
            val = self.filter.startContainer(node)
            jeżeli val == FILTER_INTERRUPT:
                podnieś ParseEscape
            jeżeli val nie w _ALLOWED_FILTER_RETURNS:
                podnieś ValueError(
                      "startContainer() returned illegal value: " + repr(val))
            zwróć val
        inaczej:
            zwróć FILTER_ACCEPT

    def acceptNode(self, node):
        mask = self._nodetype_mask[node.nodeType]
        jeżeli self.filter.whatToShow & mask:
            val = self.filter.acceptNode(node)
            jeżeli val == FILTER_INTERRUPT:
                podnieś ParseEscape
            jeżeli val == FILTER_SKIP:
                # move all child nodes to the parent, oraz remove this node
                parent = node.parentNode
                dla child w node.childNodes[:]:
                    parent.appendChild(child)
                # node jest handled by the caller
                zwróć FILTER_REJECT
            jeżeli val nie w _ALLOWED_FILTER_RETURNS:
                podnieś ValueError(
                      "acceptNode() returned illegal value: " + repr(val))
            zwróć val
        inaczej:
            zwróć FILTER_ACCEPT

    _nodetype_mask = {
        Node.ELEMENT_NODE:                NodeFilter.SHOW_ELEMENT,
        Node.ATTRIBUTE_NODE:              NodeFilter.SHOW_ATTRIBUTE,
        Node.TEXT_NODE:                   NodeFilter.SHOW_TEXT,
        Node.CDATA_SECTION_NODE:          NodeFilter.SHOW_CDATA_SECTION,
        Node.ENTITY_REFERENCE_NODE:       NodeFilter.SHOW_ENTITY_REFERENCE,
        Node.ENTITY_NODE:                 NodeFilter.SHOW_ENTITY,
        Node.PROCESSING_INSTRUCTION_NODE: NodeFilter.SHOW_PROCESSING_INSTRUCTION,
        Node.COMMENT_NODE:                NodeFilter.SHOW_COMMENT,
        Node.DOCUMENT_NODE:               NodeFilter.SHOW_DOCUMENT,
        Node.DOCUMENT_TYPE_NODE:          NodeFilter.SHOW_DOCUMENT_TYPE,
        Node.DOCUMENT_FRAGMENT_NODE:      NodeFilter.SHOW_DOCUMENT_FRAGMENT,
        Node.NOTATION_NODE:               NodeFilter.SHOW_NOTATION,
        }


klasa FilterCrutch(object):
    __slots__ = '_builder', '_level', '_old_start', '_old_end'

    def __init__(self, builder):
        self._level = 0
        self._builder = builder
        parser = builder._parser
        self._old_start = parser.StartElementHandler
        self._old_end = parser.EndElementHandler
        parser.StartElementHandler = self.start_element_handler
        parser.EndElementHandler = self.end_element_handler

klasa Rejecter(FilterCrutch):
    __slots__ = ()

    def __init__(self, builder):
        FilterCrutch.__init__(self, builder)
        parser = builder._parser
        dla name w ("ProcessingInstructionHandler",
                     "CommentHandler",
                     "CharacterDataHandler",
                     "StartCdataSectionHandler",
                     "EndCdataSectionHandler",
                     "ExternalEntityRefHandler",
                     ):
            setattr(parser, name, Nic)

    def start_element_handler(self, *args):
        self._level = self._level + 1

    def end_element_handler(self, *args):
        jeżeli self._level == 0:
            # restore the old handlers
            parser = self._builder._parser
            self._builder.install(parser)
            parser.StartElementHandler = self._old_start
            parser.EndElementHandler = self._old_end
        inaczej:
            self._level = self._level - 1

klasa Skipper(FilterCrutch):
    __slots__ = ()

    def start_element_handler(self, *args):
        node = self._builder.curNode
        self._old_start(*args)
        jeżeli self._builder.curNode jest nie node:
            self._level = self._level + 1

    def end_element_handler(self, *args):
        jeżeli self._level == 0:
            # We're popping back out of the node we're skipping, so we
            # shouldn't need to do anything but reset the handlers.
            self._builder._parser.StartElementHandler = self._old_start
            self._builder._parser.EndElementHandler = self._old_end
            self._builder = Nic
        inaczej:
            self._level = self._level - 1
            self._old_end(*args)


# framework document used by the fragment builder.
# Takes a string dla the doctype, subset string, oraz namespace attrs string.

_FRAGMENT_BUILDER_INTERNAL_SYSTEM_ID = \
    "http://xml.python.org/entities/fragment-builder/internal"

_FRAGMENT_BUILDER_TEMPLATE = (
    '''\
<!DOCTYPE wrapper
  %%s [
  <!ENTITY fragment-builder-internal
    SYSTEM "%s">
%%s
]>
<wrapper %%s
>&fragment-builder-internal;</wrapper>'''
    % _FRAGMENT_BUILDER_INTERNAL_SYSTEM_ID)


klasa FragmentBuilder(ExpatBuilder):
    """Builder which constructs document fragments given XML source
    text oraz a context node.

    The context node jest expected to provide information about the
    namespace declarations which are w scope at the start of the
    fragment.
    """

    def __init__(self, context, options=Nic):
        jeżeli context.nodeType == DOCUMENT_NODE:
            self.originalDocument = context
            self.context = context
        inaczej:
            self.originalDocument = context.ownerDocument
            self.context = context
        ExpatBuilder.__init__(self, options)

    def reset(self):
        ExpatBuilder.reset(self)
        self.fragment = Nic

    def parseFile(self, file):
        """Parse a document fragment z a file object, returning the
        fragment node."""
        zwróć self.parseString(file.read())

    def parseString(self, string):
        """Parse a document fragment z a string, returning the
        fragment node."""
        self._source = string
        parser = self.getParser()
        doctype = self.originalDocument.doctype
        ident = ""
        jeżeli doctype:
            subset = doctype.internalSubset albo self._getDeclarations()
            jeżeli doctype.publicId:
                ident = ('PUBLIC "%s" "%s"'
                         % (doctype.publicId, doctype.systemId))
            albo_inaczej doctype.systemId:
                ident = 'SYSTEM "%s"' % doctype.systemId
        inaczej:
            subset = ""
        nsattrs = self._getNSattrs() # get ns decls z node's ancestors
        document = _FRAGMENT_BUILDER_TEMPLATE % (ident, subset, nsattrs)
        spróbuj:
            parser.Parse(document, 1)
        wyjąwszy:
            self.reset()
            podnieś
        fragment = self.fragment
        self.reset()
##         self._parser = Nic
        zwróć fragment

    def _getDeclarations(self):
        """Re-create the internal subset z the DocumentType node.

        This jest only needed jeżeli we don't already have the
        internalSubset jako a string.
        """
        doctype = self.context.ownerDocument.doctype
        s = ""
        jeżeli doctype:
            dla i w range(doctype.notations.length):
                notation = doctype.notations.item(i)
                jeżeli s:
                    s = s + "\n  "
                s = "%s<!NOTATION %s" % (s, notation.nodeName)
                jeżeli notation.publicId:
                    s = '%s PUBLIC "%s"\n             "%s">' \
                        % (s, notation.publicId, notation.systemId)
                inaczej:
                    s = '%s SYSTEM "%s">' % (s, notation.systemId)
            dla i w range(doctype.entities.length):
                entity = doctype.entities.item(i)
                jeżeli s:
                    s = s + "\n  "
                s = "%s<!ENTITY %s" % (s, entity.nodeName)
                jeżeli entity.publicId:
                    s = '%s PUBLIC "%s"\n             "%s"' \
                        % (s, entity.publicId, entity.systemId)
                albo_inaczej entity.systemId:
                    s = '%s SYSTEM "%s"' % (s, entity.systemId)
                inaczej:
                    s = '%s "%s"' % (s, entity.firstChild.data)
                jeżeli entity.notationName:
                    s = "%s NOTATION %s" % (s, entity.notationName)
                s = s + ">"
        zwróć s

    def _getNSattrs(self):
        zwróć ""

    def external_entity_ref_handler(self, context, base, systemId, publicId):
        jeżeli systemId == _FRAGMENT_BUILDER_INTERNAL_SYSTEM_ID:
            # this entref jest the one that we made to put the subtree
            # in; all of our given input jest parsed w here.
            old_document = self.document
            old_cur_node = self.curNode
            parser = self._parser.ExternalEntityParserCreate(context)
            # put the real document back, parse into the fragment to zwróć
            self.document = self.originalDocument
            self.fragment = self.document.createDocumentFragment()
            self.curNode = self.fragment
            spróbuj:
                parser.Parse(self._source, 1)
            w_końcu:
                self.curNode = old_cur_node
                self.document = old_document
                self._source = Nic
            zwróć -1
        inaczej:
            zwróć ExpatBuilder.external_entity_ref_handler(
                self, context, base, systemId, publicId)


klasa Namespaces:
    """Mix-in klasa dla builders; adds support dla namespaces."""

    def _initNamespaces(self):
        # list of (prefix, uri) ns declarations.  Namespace attrs are
        # constructed z this oraz added to the element's attrs.
        self._ns_ordered_prefixes = []

    def createParser(self):
        """Create a new namespace-handling parser."""
        parser = expat.ParserCreate(namespace_separator=" ")
        parser.namespace_prefixes = Prawda
        zwróć parser

    def install(self, parser):
        """Insert the namespace-handlers onto the parser."""
        ExpatBuilder.install(self, parser)
        jeżeli self._options.namespace_declarations:
            parser.StartNamespaceDeclHandler = (
                self.start_namespace_decl_handler)

    def start_namespace_decl_handler(self, prefix, uri):
        """Push this namespace declaration on our storage."""
        self._ns_ordered_prefixes.append((prefix, uri))

    def start_element_handler(self, name, attributes):
        jeżeli ' ' w name:
            uri, localname, prefix, qname = _parse_ns_name(self, name)
        inaczej:
            uri = EMPTY_NAMESPACE
            qname = name
            localname = Nic
            prefix = EMPTY_PREFIX
        node = minidom.Element(qname, uri, prefix, localname)
        node.ownerDocument = self.document
        _append_child(self.curNode, node)
        self.curNode = node

        jeżeli self._ns_ordered_prefixes:
            dla prefix, uri w self._ns_ordered_prefixes:
                jeżeli prefix:
                    a = minidom.Attr(_intern(self, 'xmlns:' + prefix),
                                     XMLNS_NAMESPACE, prefix, "xmlns")
                inaczej:
                    a = minidom.Attr("xmlns", XMLNS_NAMESPACE,
                                     "xmlns", EMPTY_PREFIX)
                a.value = uri
                a.ownerDocument = self.document
                _set_attribute_node(node, a)
            usuń self._ns_ordered_prefixes[:]

        jeżeli attributes:
            node._ensure_attributes()
            _attrs = node._attrs
            _attrsNS = node._attrsNS
            dla i w range(0, len(attributes), 2):
                aname = attributes[i]
                value = attributes[i+1]
                jeżeli ' ' w aname:
                    uri, localname, prefix, qname = _parse_ns_name(self, aname)
                    a = minidom.Attr(qname, uri, localname, prefix)
                    _attrs[qname] = a
                    _attrsNS[(uri, localname)] = a
                inaczej:
                    a = minidom.Attr(aname, EMPTY_NAMESPACE,
                                     aname, EMPTY_PREFIX)
                    _attrs[aname] = a
                    _attrsNS[(EMPTY_NAMESPACE, aname)] = a
                a.ownerDocument = self.document
                a.value = value
                a.ownerElement = node

    jeżeli __debug__:
        # This only adds some asserts to the original
        # end_element_handler(), so we only define this when -O jest nie
        # used.  If changing one, be sure to check the other to see if
        # it needs to be changed jako well.
        #
        def end_element_handler(self, name):
            curNode = self.curNode
            jeżeli ' ' w name:
                uri, localname, prefix, qname = _parse_ns_name(self, name)
                assert (curNode.namespaceURI == uri
                        oraz curNode.localName == localname
                        oraz curNode.prefix == prefix), \
                        "element stack messed up! (namespace)"
            inaczej:
                assert curNode.nodeName == name, \
                       "element stack messed up - bad nodeName"
                assert curNode.namespaceURI == EMPTY_NAMESPACE, \
                       "element stack messed up - bad namespaceURI"
            self.curNode = curNode.parentNode
            self._finish_end_element(curNode)


klasa ExpatBuilderNS(Namespaces, ExpatBuilder):
    """Document builder that supports namespaces."""

    def reset(self):
        ExpatBuilder.reset(self)
        self._initNamespaces()


klasa FragmentBuilderNS(Namespaces, FragmentBuilder):
    """Fragment builder that supports namespaces."""

    def reset(self):
        FragmentBuilder.reset(self)
        self._initNamespaces()

    def _getNSattrs(self):
        """Return string of namespace attributes z this element oraz
        ancestors."""
        # XXX This needs to be re-written to walk the ancestors of the
        # context to build up the namespace information from
        # declarations, elements, oraz attributes found w context.
        # Otherwise we have to store a bunch more data on the DOM
        # (though that *might* be more reliable -- nie clear).
        attrs = ""
        context = self.context
        L = []
        dopóki context:
            jeżeli hasattr(context, '_ns_prefix_uri'):
                dla prefix, uri w context._ns_prefix_uri.items():
                    # add every new NS decl z context to L oraz attrs string
                    jeżeli prefix w L:
                        kontynuuj
                    L.append(prefix)
                    jeżeli prefix:
                        declname = "xmlns:" + prefix
                    inaczej:
                        declname = "xmlns"
                    jeżeli attrs:
                        attrs = "%s\n    %s='%s'" % (attrs, declname, uri)
                    inaczej:
                        attrs = " %s='%s'" % (declname, uri)
            context = context.parentNode
        zwróć attrs


klasa ParseEscape(Exception):
    """Exception podnieśd to short-circuit parsing w InternalSubsetExtractor."""
    dalej

klasa InternalSubsetExtractor(ExpatBuilder):
    """XML processor which can rip out the internal document type subset."""

    subset = Nic

    def getSubset(self):
        """Return the internal subset jako a string."""
        zwróć self.subset

    def parseFile(self, file):
        spróbuj:
            ExpatBuilder.parseFile(self, file)
        wyjąwszy ParseEscape:
            dalej

    def parseString(self, string):
        spróbuj:
            ExpatBuilder.parseString(self, string)
        wyjąwszy ParseEscape:
            dalej

    def install(self, parser):
        parser.StartDoctypeDeclHandler = self.start_doctype_decl_handler
        parser.StartElementHandler = self.start_element_handler

    def start_doctype_decl_handler(self, name, publicId, systemId,
                                   has_internal_subset):
        jeżeli has_internal_subset:
            parser = self.getParser()
            self.subset = []
            parser.DefaultHandler = self.subset.append
            parser.EndDoctypeDeclHandler = self.end_doctype_decl_handler
        inaczej:
            podnieś ParseEscape()

    def end_doctype_decl_handler(self):
        s = ''.join(self.subset).replace('\r\n', '\n').replace('\r', '\n')
        self.subset = s
        podnieś ParseEscape()

    def start_element_handler(self, name, attrs):
        podnieś ParseEscape()


def parse(file, namespaces=Prawda):
    """Parse a document, returning the resulting Document node.

    'file' may be either a file name albo an open file object.
    """
    jeżeli namespaces:
        builder = ExpatBuilderNS()
    inaczej:
        builder = ExpatBuilder()

    jeżeli isinstance(file, str):
        przy open(file, 'rb') jako fp:
            result = builder.parseFile(fp)
    inaczej:
        result = builder.parseFile(file)
    zwróć result


def parseString(string, namespaces=Prawda):
    """Parse a document z a string, returning the resulting
    Document node.
    """
    jeżeli namespaces:
        builder = ExpatBuilderNS()
    inaczej:
        builder = ExpatBuilder()
    zwróć builder.parseString(string)


def parseFragment(file, context, namespaces=Prawda):
    """Parse a fragment of a document, given the context z which it
    was originally extracted.  context should be the parent of the
    node(s) which are w the fragment.

    'file' may be either a file name albo an open file object.
    """
    jeżeli namespaces:
        builder = FragmentBuilderNS(context)
    inaczej:
        builder = FragmentBuilder(context)

    jeżeli isinstance(file, str):
        przy open(file, 'rb') jako fp:
            result = builder.parseFile(fp)
    inaczej:
        result = builder.parseFile(file)
    zwróć result


def parseFragmentString(string, context, namespaces=Prawda):
    """Parse a fragment of a document z a string, given the context
    z which it was originally extracted.  context should be the
    parent of the node(s) which are w the fragment.
    """
    jeżeli namespaces:
        builder = FragmentBuilderNS(context)
    inaczej:
        builder = FragmentBuilder(context)
    zwróć builder.parseString(string)


def makeBuilder(options):
    """Create a builder based on an Options object."""
    jeżeli options.namespaces:
        zwróć ExpatBuilderNS(options)
    inaczej:
        zwróć ExpatBuilder(options)
