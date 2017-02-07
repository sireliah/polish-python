"""Simple implementation of the Level 1 DOM.

Namespaces oraz other minor Level 2 features are also supported.

parse("foo.xml")

parseString("<foo><bar/></foo>")

Todo:
=====
 * convenience methods dla getting elements oraz text.
 * more testing
 * bring some of the writer oraz linearizer code into conformance przy this
        interface
 * SAX 2 namespaces
"""

zaimportuj io
zaimportuj xml.dom

z xml.dom zaimportuj EMPTY_NAMESPACE, EMPTY_PREFIX, XMLNS_NAMESPACE, domreg
z xml.dom.minicompat zaimportuj *
z xml.dom.xmlbuilder zaimportuj DOMImplementationLS, DocumentLS

# This jest used by the ID-cache invalidation checks; the list isn't
# actually complete, since the nodes being checked will never be the
# DOCUMENT_NODE albo DOCUMENT_FRAGMENT_NODE.  (The node being checked jest
# the node being added albo removed, nie the node being modified.)
#
_nodeTypes_with_children = (xml.dom.Node.ELEMENT_NODE,
                            xml.dom.Node.ENTITY_REFERENCE_NODE)


klasa Node(xml.dom.Node):
    namespaceURI = Nic # this jest non-null only dla elements oraz attributes
    parentNode = Nic
    ownerDocument = Nic
    nextSibling = Nic
    previousSibling = Nic

    prefix = EMPTY_PREFIX # non-null only dla NS elements oraz attributes

    def __bool__(self):
        zwróć Prawda

    def toxml(self, encoding=Nic):
        zwróć self.toprettyxml("", "", encoding)

    def toprettyxml(self, indent="\t", newl="\n", encoding=Nic):
        jeżeli encoding jest Nic:
            writer = io.StringIO()
        inaczej:
            writer = io.TextIOWrapper(io.BytesIO(),
                                      encoding=encoding,
                                      errors="xmlcharrefreplace",
                                      newline='\n')
        jeżeli self.nodeType == Node.DOCUMENT_NODE:
            # Can dalej encoding only to document, to put it into XML header
            self.writexml(writer, "", indent, newl, encoding)
        inaczej:
            self.writexml(writer, "", indent, newl)
        jeżeli encoding jest Nic:
            zwróć writer.getvalue()
        inaczej:
            zwróć writer.detach().getvalue()

    def hasChildNodes(self):
        zwróć bool(self.childNodes)

    def _get_childNodes(self):
        zwróć self.childNodes

    def _get_firstChild(self):
        jeżeli self.childNodes:
            zwróć self.childNodes[0]

    def _get_lastChild(self):
        jeżeli self.childNodes:
            zwróć self.childNodes[-1]

    def insertBefore(self, newChild, refChild):
        jeżeli newChild.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            dla c w tuple(newChild.childNodes):
                self.insertBefore(c, refChild)
            ### The DOM does nie clearly specify what to zwróć w this case
            zwróć newChild
        jeżeli newChild.nodeType nie w self._child_node_types:
            podnieś xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(newChild), repr(self)))
        jeżeli newChild.parentNode jest nie Nic:
            newChild.parentNode.removeChild(newChild)
        jeżeli refChild jest Nic:
            self.appendChild(newChild)
        inaczej:
            spróbuj:
                index = self.childNodes.index(refChild)
            wyjąwszy ValueError:
                podnieś xml.dom.NotFoundErr()
            jeżeli newChild.nodeType w _nodeTypes_with_children:
                _clear_id_cache(self)
            self.childNodes.insert(index, newChild)
            newChild.nextSibling = refChild
            refChild.previousSibling = newChild
            jeżeli index:
                node = self.childNodes[index-1]
                node.nextSibling = newChild
                newChild.previousSibling = node
            inaczej:
                newChild.previousSibling = Nic
            newChild.parentNode = self
        zwróć newChild

    def appendChild(self, node):
        jeżeli node.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            dla c w tuple(node.childNodes):
                self.appendChild(c)
            ### The DOM does nie clearly specify what to zwróć w this case
            zwróć node
        jeżeli node.nodeType nie w self._child_node_types:
            podnieś xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(node), repr(self)))
        albo_inaczej node.nodeType w _nodeTypes_with_children:
            _clear_id_cache(self)
        jeżeli node.parentNode jest nie Nic:
            node.parentNode.removeChild(node)
        _append_child(self, node)
        node.nextSibling = Nic
        zwróć node

    def replaceChild(self, newChild, oldChild):
        jeżeli newChild.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            refChild = oldChild.nextSibling
            self.removeChild(oldChild)
            zwróć self.insertBefore(newChild, refChild)
        jeżeli newChild.nodeType nie w self._child_node_types:
            podnieś xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(newChild), repr(self)))
        jeżeli newChild jest oldChild:
            zwróć
        jeżeli newChild.parentNode jest nie Nic:
            newChild.parentNode.removeChild(newChild)
        spróbuj:
            index = self.childNodes.index(oldChild)
        wyjąwszy ValueError:
            podnieś xml.dom.NotFoundErr()
        self.childNodes[index] = newChild
        newChild.parentNode = self
        oldChild.parentNode = Nic
        jeżeli (newChild.nodeType w _nodeTypes_with_children
            albo oldChild.nodeType w _nodeTypes_with_children):
            _clear_id_cache(self)
        newChild.nextSibling = oldChild.nextSibling
        newChild.previousSibling = oldChild.previousSibling
        oldChild.nextSibling = Nic
        oldChild.previousSibling = Nic
        jeżeli newChild.previousSibling:
            newChild.previousSibling.nextSibling = newChild
        jeżeli newChild.nextSibling:
            newChild.nextSibling.previousSibling = newChild
        zwróć oldChild

    def removeChild(self, oldChild):
        spróbuj:
            self.childNodes.remove(oldChild)
        wyjąwszy ValueError:
            podnieś xml.dom.NotFoundErr()
        jeżeli oldChild.nextSibling jest nie Nic:
            oldChild.nextSibling.previousSibling = oldChild.previousSibling
        jeżeli oldChild.previousSibling jest nie Nic:
            oldChild.previousSibling.nextSibling = oldChild.nextSibling
        oldChild.nextSibling = oldChild.previousSibling = Nic
        jeżeli oldChild.nodeType w _nodeTypes_with_children:
            _clear_id_cache(self)

        oldChild.parentNode = Nic
        zwróć oldChild

    def normalize(self):
        L = []
        dla child w self.childNodes:
            jeżeli child.nodeType == Node.TEXT_NODE:
                jeżeli nie child.data:
                    # empty text node; discard
                    jeżeli L:
                        L[-1].nextSibling = child.nextSibling
                    jeżeli child.nextSibling:
                        child.nextSibling.previousSibling = child.previousSibling
                    child.unlink()
                albo_inaczej L oraz L[-1].nodeType == child.nodeType:
                    # collapse text node
                    node = L[-1]
                    node.data = node.data + child.data
                    node.nextSibling = child.nextSibling
                    jeżeli child.nextSibling:
                        child.nextSibling.previousSibling = node
                    child.unlink()
                inaczej:
                    L.append(child)
            inaczej:
                L.append(child)
                jeżeli child.nodeType == Node.ELEMENT_NODE:
                    child.normalize()
        self.childNodes[:] = L

    def cloneNode(self, deep):
        zwróć _clone_node(self, deep, self.ownerDocument albo self)

    def isSupported(self, feature, version):
        zwróć self.ownerDocument.implementation.hasFeature(feature, version)

    def _get_localName(self):
        # Overridden w Element oraz Attr where localName can be Non-Null
        zwróć Nic

    # Node interfaces z Level 3 (WD 9 April 2002)

    def isSameNode(self, other):
        zwróć self jest other

    def getInterface(self, feature):
        jeżeli self.isSupported(feature, Nic):
            zwróć self
        inaczej:
            zwróć Nic

    # The "user data" functions use a dictionary that jest only present
    # jeżeli some user data has been set, so be careful nie to assume it
    # exists.

    def getUserData(self, key):
        spróbuj:
            zwróć self._user_data[key][0]
        wyjąwszy (AttributeError, KeyError):
            zwróć Nic

    def setUserData(self, key, data, handler):
        old = Nic
        spróbuj:
            d = self._user_data
        wyjąwszy AttributeError:
            d = {}
            self._user_data = d
        jeżeli key w d:
            old = d[key][0]
        jeżeli data jest Nic:
            # ignore handlers dalejed dla Nic
            handler = Nic
            jeżeli old jest nie Nic:
                usuń d[key]
        inaczej:
            d[key] = (data, handler)
        zwróć old

    def _call_user_data_handler(self, operation, src, dst):
        jeżeli hasattr(self, "_user_data"):
            dla key, (data, handler) w list(self._user_data.items()):
                jeżeli handler jest nie Nic:
                    handler.handle(operation, key, data, src, dst)

    # minidom-specific API:

    def unlink(self):
        self.parentNode = self.ownerDocument = Nic
        jeżeli self.childNodes:
            dla child w self.childNodes:
                child.unlink()
            self.childNodes = NodeList()
        self.previousSibling = Nic
        self.nextSibling = Nic

    # A Node jest its own context manager, to ensure that an unlink() call occurs.
    # This jest similar to how a file object works.
    def __enter__(self):
        zwróć self

    def __exit__(self, et, ev, tb):
        self.unlink()

defproperty(Node, "firstChild", doc="First child node, albo Nic.")
defproperty(Node, "lastChild",  doc="Last child node, albo Nic.")
defproperty(Node, "localName",  doc="Namespace-local name of this node.")


def _append_child(self, node):
    # fast path przy less checks; usable by DOM builders jeżeli careful
    childNodes = self.childNodes
    jeżeli childNodes:
        last = childNodes[-1]
        node.previousSibling = last
        last.nextSibling = node
    childNodes.append(node)
    node.parentNode = self

def _in_document(node):
    # zwróć Prawda iff node jest part of a document tree
    dopóki node jest nie Nic:
        jeżeli node.nodeType == Node.DOCUMENT_NODE:
            zwróć Prawda
        node = node.parentNode
    zwróć Nieprawda

def _write_data(writer, data):
    "Writes datachars to writer."
    jeżeli data:
        data = data.replace("&", "&amp;").replace("<", "&lt;"). \
                    replace("\"", "&quot;").replace(">", "&gt;")
        writer.write(data)

def _get_elements_by_tagName_helper(parent, name, rc):
    dla node w parent.childNodes:
        jeżeli node.nodeType == Node.ELEMENT_NODE oraz \
            (name == "*" albo node.tagName == name):
            rc.append(node)
        _get_elements_by_tagName_helper(node, name, rc)
    zwróć rc

def _get_elements_by_tagName_ns_helper(parent, nsURI, localName, rc):
    dla node w parent.childNodes:
        jeżeli node.nodeType == Node.ELEMENT_NODE:
            jeżeli ((localName == "*" albo node.localName == localName) oraz
                (nsURI == "*" albo node.namespaceURI == nsURI)):
                rc.append(node)
            _get_elements_by_tagName_ns_helper(node, nsURI, localName, rc)
    zwróć rc

klasa DocumentFragment(Node):
    nodeType = Node.DOCUMENT_FRAGMENT_NODE
    nodeName = "#document-fragment"
    nodeValue = Nic
    attributes = Nic
    parentNode = Nic
    _child_node_types = (Node.ELEMENT_NODE,
                         Node.TEXT_NODE,
                         Node.CDATA_SECTION_NODE,
                         Node.ENTITY_REFERENCE_NODE,
                         Node.PROCESSING_INSTRUCTION_NODE,
                         Node.COMMENT_NODE,
                         Node.NOTATION_NODE)

    def __init__(self):
        self.childNodes = NodeList()


klasa Attr(Node):
    __slots__=('_name', '_value', 'namespaceURI',
               '_prefix', 'childNodes', '_localName', 'ownerDocument', 'ownerElement')
    nodeType = Node.ATTRIBUTE_NODE
    attributes = Nic
    specified = Nieprawda
    _is_id = Nieprawda

    _child_node_types = (Node.TEXT_NODE, Node.ENTITY_REFERENCE_NODE)

    def __init__(self, qName, namespaceURI=EMPTY_NAMESPACE, localName=Nic,
                 prefix=Nic):
        self.ownerElement = Nic
        self._name = qName
        self.namespaceURI = namespaceURI
        self._prefix = prefix
        self.childNodes = NodeList()

        # Add the single child node that represents the value of the attr
        self.childNodes.append(Text())

        # nodeValue oraz value are set inaczejwhere

    def _get_localName(self):
        spróbuj:
            zwróć self._localName
        wyjąwszy AttributeError:
            zwróć self.nodeName.split(":", 1)[-1]

    def _get_specified(self):
        zwróć self.specified

    def _get_name(self):
        zwróć self._name

    def _set_name(self, value):
        self._name = value
        jeżeli self.ownerElement jest nie Nic:
            _clear_id_cache(self.ownerElement)

    nodeName = name = property(_get_name, _set_name)

    def _get_value(self):
        zwróć self._value

    def _set_value(self, value):
        self._value = value
        self.childNodes[0].data = value
        jeżeli self.ownerElement jest nie Nic:
            _clear_id_cache(self.ownerElement)
        self.childNodes[0].data = value

    nodeValue = value = property(_get_value, _set_value)

    def _get_prefix(self):
        zwróć self._prefix

    def _set_prefix(self, prefix):
        nsuri = self.namespaceURI
        jeżeli prefix == "xmlns":
            jeżeli nsuri oraz nsuri != XMLNS_NAMESPACE:
                podnieś xml.dom.NamespaceErr(
                    "illegal use of 'xmlns' prefix dla the wrong namespace")
        self._prefix = prefix
        jeżeli prefix jest Nic:
            newName = self.localName
        inaczej:
            newName = "%s:%s" % (prefix, self.localName)
        jeżeli self.ownerElement:
            _clear_id_cache(self.ownerElement)
        self.name = newName

    prefix = property(_get_prefix, _set_prefix)

    def unlink(self):
        # This implementation does nie call the base implementation
        # since most of that jest nie needed, oraz the expense of the
        # method call jest nie warranted.  We duplicate the removal of
        # children, but that's all we needed z the base class.
        elem = self.ownerElement
        jeżeli elem jest nie Nic:
            usuń elem._attrs[self.nodeName]
            usuń elem._attrsNS[(self.namespaceURI, self.localName)]
            jeżeli self._is_id:
                self._is_id = Nieprawda
                elem._magic_id_nodes -= 1
                self.ownerDocument._magic_id_count -= 1
        dla child w self.childNodes:
            child.unlink()
        usuń self.childNodes[:]

    def _get_isId(self):
        jeżeli self._is_id:
            zwróć Prawda
        doc = self.ownerDocument
        elem = self.ownerElement
        jeżeli doc jest Nic albo elem jest Nic:
            zwróć Nieprawda

        info = doc._get_elem_info(elem)
        jeżeli info jest Nic:
            zwróć Nieprawda
        jeżeli self.namespaceURI:
            zwróć info.isIdNS(self.namespaceURI, self.localName)
        inaczej:
            zwróć info.isId(self.nodeName)

    def _get_schemaType(self):
        doc = self.ownerDocument
        elem = self.ownerElement
        jeżeli doc jest Nic albo elem jest Nic:
            zwróć _no_type

        info = doc._get_elem_info(elem)
        jeżeli info jest Nic:
            zwróć _no_type
        jeżeli self.namespaceURI:
            zwróć info.getAttributeTypeNS(self.namespaceURI, self.localName)
        inaczej:
            zwróć info.getAttributeType(self.nodeName)

defproperty(Attr, "isId",       doc="Prawda jeżeli this attribute jest an ID.")
defproperty(Attr, "localName",  doc="Namespace-local name of this attribute.")
defproperty(Attr, "schemaType", doc="Schema type dla this attribute.")


klasa NamedNodeMap(object):
    """The attribute list jest a transient interface to the underlying
    dictionaries.  Mutations here will change the underlying element's
    dictionary.

    Ordering jest imposed artificially oraz does nie reflect the order of
    attributes jako found w an input document.
    """

    __slots__ = ('_attrs', '_attrsNS', '_ownerElement')

    def __init__(self, attrs, attrsNS, ownerElement):
        self._attrs = attrs
        self._attrsNS = attrsNS
        self._ownerElement = ownerElement

    def _get_length(self):
        zwróć len(self._attrs)

    def item(self, index):
        spróbuj:
            zwróć self[list(self._attrs.keys())[index]]
        wyjąwszy IndexError:
            zwróć Nic

    def items(self):
        L = []
        dla node w self._attrs.values():
            L.append((node.nodeName, node.value))
        zwróć L

    def itemsNS(self):
        L = []
        dla node w self._attrs.values():
            L.append(((node.namespaceURI, node.localName), node.value))
        zwróć L

    def __contains__(self, key):
        jeżeli isinstance(key, str):
            zwróć key w self._attrs
        inaczej:
            zwróć key w self._attrsNS

    def keys(self):
        zwróć self._attrs.keys()

    def keysNS(self):
        zwróć self._attrsNS.keys()

    def values(self):
        zwróć self._attrs.values()

    def get(self, name, value=Nic):
        zwróć self._attrs.get(name, value)

    __len__ = _get_length

    def _cmp(self, other):
        jeżeli self._attrs jest getattr(other, "_attrs", Nic):
            zwróć 0
        inaczej:
            zwróć (id(self) > id(other)) - (id(self) < id(other))

    def __eq__(self, other):
        zwróć self._cmp(other) == 0

    def __ge__(self, other):
        zwróć self._cmp(other) >= 0

    def __gt__(self, other):
        zwróć self._cmp(other) > 0

    def __le__(self, other):
        zwróć self._cmp(other) <= 0

    def __lt__(self, other):
        zwróć self._cmp(other) < 0

    def __getitem__(self, attname_or_tuple):
        jeżeli isinstance(attname_or_tuple, tuple):
            zwróć self._attrsNS[attname_or_tuple]
        inaczej:
            zwróć self._attrs[attname_or_tuple]

    # same jako set
    def __setitem__(self, attname, value):
        jeżeli isinstance(value, str):
            spróbuj:
                node = self._attrs[attname]
            wyjąwszy KeyError:
                node = Attr(attname)
                node.ownerDocument = self._ownerElement.ownerDocument
                self.setNamedItem(node)
            node.value = value
        inaczej:
            jeżeli nie isinstance(value, Attr):
                podnieś TypeError("value must be a string albo Attr object")
            node = value
            self.setNamedItem(node)

    def getNamedItem(self, name):
        spróbuj:
            zwróć self._attrs[name]
        wyjąwszy KeyError:
            zwróć Nic

    def getNamedItemNS(self, namespaceURI, localName):
        spróbuj:
            zwróć self._attrsNS[(namespaceURI, localName)]
        wyjąwszy KeyError:
            zwróć Nic

    def removeNamedItem(self, name):
        n = self.getNamedItem(name)
        jeżeli n jest nie Nic:
            _clear_id_cache(self._ownerElement)
            usuń self._attrs[n.nodeName]
            usuń self._attrsNS[(n.namespaceURI, n.localName)]
            jeżeli hasattr(n, 'ownerElement'):
                n.ownerElement = Nic
            zwróć n
        inaczej:
            podnieś xml.dom.NotFoundErr()

    def removeNamedItemNS(self, namespaceURI, localName):
        n = self.getNamedItemNS(namespaceURI, localName)
        jeżeli n jest nie Nic:
            _clear_id_cache(self._ownerElement)
            usuń self._attrsNS[(n.namespaceURI, n.localName)]
            usuń self._attrs[n.nodeName]
            jeżeli hasattr(n, 'ownerElement'):
                n.ownerElement = Nic
            zwróć n
        inaczej:
            podnieś xml.dom.NotFoundErr()

    def setNamedItem(self, node):
        jeżeli nie isinstance(node, Attr):
            podnieś xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(node), repr(self)))
        old = self._attrs.get(node.name)
        jeżeli old:
            old.unlink()
        self._attrs[node.name] = node
        self._attrsNS[(node.namespaceURI, node.localName)] = node
        node.ownerElement = self._ownerElement
        _clear_id_cache(node.ownerElement)
        zwróć old

    def setNamedItemNS(self, node):
        zwróć self.setNamedItem(node)

    def __delitem__(self, attname_or_tuple):
        node = self[attname_or_tuple]
        _clear_id_cache(node.ownerElement)
        node.unlink()

    def __getstate__(self):
        zwróć self._attrs, self._attrsNS, self._ownerElement

    def __setstate__(self, state):
        self._attrs, self._attrsNS, self._ownerElement = state

defproperty(NamedNodeMap, "length",
            doc="Number of nodes w the NamedNodeMap.")

AttributeList = NamedNodeMap


klasa TypeInfo(object):
    __slots__ = 'namespace', 'name'

    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

    def __repr__(self):
        jeżeli self.namespace:
            zwróć "<%s %r (z %r)>" % (self.__class__.__name__, self.name,
                                          self.namespace)
        inaczej:
            zwróć "<%s %r>" % (self.__class__.__name__, self.name)

    def _get_name(self):
        zwróć self.name

    def _get_namespace(self):
        zwróć self.namespace

_no_type = TypeInfo(Nic, Nic)

klasa Element(Node):
    __slots__=('ownerDocument', 'parentNode', 'tagName', 'nodeName', 'prefix',
               'namespaceURI', '_localName', 'childNodes', '_attrs', '_attrsNS',
               'nextSibling', 'previousSibling')
    nodeType = Node.ELEMENT_NODE
    nodeValue = Nic
    schemaType = _no_type

    _magic_id_nodes = 0

    _child_node_types = (Node.ELEMENT_NODE,
                         Node.PROCESSING_INSTRUCTION_NODE,
                         Node.COMMENT_NODE,
                         Node.TEXT_NODE,
                         Node.CDATA_SECTION_NODE,
                         Node.ENTITY_REFERENCE_NODE)

    def __init__(self, tagName, namespaceURI=EMPTY_NAMESPACE, prefix=Nic,
                 localName=Nic):
        self.parentNode = Nic
        self.tagName = self.nodeName = tagName
        self.prefix = prefix
        self.namespaceURI = namespaceURI
        self.childNodes = NodeList()
        self.nextSibling = self.previousSibling = Nic

        # Attribute dictionaries are lazily created
        # attributes are double-indexed:
        #    tagName -> Attribute
        #    URI,localName -> Attribute
        # w the future: consider lazy generation
        # of attribute objects this jest too tricky
        # dla now because of headaches with
        # namespaces.
        self._attrs = Nic
        self._attrsNS = Nic

    def _ensure_attributes(self):
        jeżeli self._attrs jest Nic:
            self._attrs = {}
            self._attrsNS = {}

    def _get_localName(self):
        spróbuj:
            zwróć self._localName
        wyjąwszy AttributeError:
            zwróć self.tagName.split(":", 1)[-1]

    def _get_tagName(self):
        zwróć self.tagName

    def unlink(self):
        jeżeli self._attrs jest nie Nic:
            dla attr w list(self._attrs.values()):
                attr.unlink()
        self._attrs = Nic
        self._attrsNS = Nic
        Node.unlink(self)

    def getAttribute(self, attname):
        jeżeli self._attrs jest Nic:
            zwróć ""
        spróbuj:
            zwróć self._attrs[attname].value
        wyjąwszy KeyError:
            zwróć ""

    def getAttributeNS(self, namespaceURI, localName):
        jeżeli self._attrsNS jest Nic:
            zwróć ""
        spróbuj:
            zwróć self._attrsNS[(namespaceURI, localName)].value
        wyjąwszy KeyError:
            zwróć ""

    def setAttribute(self, attname, value):
        attr = self.getAttributeNode(attname)
        jeżeli attr jest Nic:
            attr = Attr(attname)
            attr.value = value # also sets nodeValue
            attr.ownerDocument = self.ownerDocument
            self.setAttributeNode(attr)
        albo_inaczej value != attr.value:
            attr.value = value
            jeżeli attr.isId:
                _clear_id_cache(self)

    def setAttributeNS(self, namespaceURI, qualifiedName, value):
        prefix, localname = _nssplit(qualifiedName)
        attr = self.getAttributeNodeNS(namespaceURI, localname)
        jeżeli attr jest Nic:
            attr = Attr(qualifiedName, namespaceURI, localname, prefix)
            attr.value = value
            attr.ownerDocument = self.ownerDocument
            self.setAttributeNode(attr)
        inaczej:
            jeżeli value != attr.value:
                attr.value = value
                jeżeli attr.isId:
                    _clear_id_cache(self)
            jeżeli attr.prefix != prefix:
                attr.prefix = prefix
                attr.nodeName = qualifiedName

    def getAttributeNode(self, attrname):
        jeżeli self._attrs jest Nic:
            zwróć Nic
        zwróć self._attrs.get(attrname)

    def getAttributeNodeNS(self, namespaceURI, localName):
        jeżeli self._attrsNS jest Nic:
            zwróć Nic
        zwróć self._attrsNS.get((namespaceURI, localName))

    def setAttributeNode(self, attr):
        jeżeli attr.ownerElement nie w (Nic, self):
            podnieś xml.dom.InuseAttributeErr("attribute node already owned")
        self._ensure_attributes()
        old1 = self._attrs.get(attr.name, Nic)
        jeżeli old1 jest nie Nic:
            self.removeAttributeNode(old1)
        old2 = self._attrsNS.get((attr.namespaceURI, attr.localName), Nic)
        jeżeli old2 jest nie Nic oraz old2 jest nie old1:
            self.removeAttributeNode(old2)
        _set_attribute_node(self, attr)

        jeżeli old1 jest nie attr:
            # It might have already been part of this node, w which case
            # it doesn't represent a change, oraz should nie be returned.
            zwróć old1
        jeżeli old2 jest nie attr:
            zwróć old2

    setAttributeNodeNS = setAttributeNode

    def removeAttribute(self, name):
        jeżeli self._attrsNS jest Nic:
            podnieś xml.dom.NotFoundErr()
        spróbuj:
            attr = self._attrs[name]
        wyjąwszy KeyError:
            podnieś xml.dom.NotFoundErr()
        self.removeAttributeNode(attr)

    def removeAttributeNS(self, namespaceURI, localName):
        jeżeli self._attrsNS jest Nic:
            podnieś xml.dom.NotFoundErr()
        spróbuj:
            attr = self._attrsNS[(namespaceURI, localName)]
        wyjąwszy KeyError:
            podnieś xml.dom.NotFoundErr()
        self.removeAttributeNode(attr)

    def removeAttributeNode(self, node):
        jeżeli node jest Nic:
            podnieś xml.dom.NotFoundErr()
        spróbuj:
            self._attrs[node.name]
        wyjąwszy KeyError:
            podnieś xml.dom.NotFoundErr()
        _clear_id_cache(self)
        node.unlink()
        # Restore this since the node jest still useful oraz otherwise
        # unlinked
        node.ownerDocument = self.ownerDocument

    removeAttributeNodeNS = removeAttributeNode

    def hasAttribute(self, name):
        jeżeli self._attrs jest Nic:
            zwróć Nieprawda
        zwróć name w self._attrs

    def hasAttributeNS(self, namespaceURI, localName):
        jeżeli self._attrsNS jest Nic:
            zwróć Nieprawda
        zwróć (namespaceURI, localName) w self._attrsNS

    def getElementsByTagName(self, name):
        zwróć _get_elements_by_tagName_helper(self, name, NodeList())

    def getElementsByTagNameNS(self, namespaceURI, localName):
        zwróć _get_elements_by_tagName_ns_helper(
            self, namespaceURI, localName, NodeList())

    def __repr__(self):
        zwróć "<DOM Element: %s at %#x>" % (self.tagName, id(self))

    def writexml(self, writer, indent="", addindent="", newl=""):
        # indent = current indentation
        # addindent = indentation to add to higher levels
        # newl = newline string
        writer.write(indent+"<" + self.tagName)

        attrs = self._get_attributes()
        a_names = sorted(attrs.keys())

        dla a_name w a_names:
            writer.write(" %s=\"" % a_name)
            _write_data(writer, attrs[a_name].value)
            writer.write("\"")
        jeżeli self.childNodes:
            writer.write(">")
            jeżeli (len(self.childNodes) == 1 oraz
                self.childNodes[0].nodeType == Node.TEXT_NODE):
                self.childNodes[0].writexml(writer, '', '', '')
            inaczej:
                writer.write(newl)
                dla node w self.childNodes:
                    node.writexml(writer, indent+addindent, addindent, newl)
                writer.write(indent)
            writer.write("</%s>%s" % (self.tagName, newl))
        inaczej:
            writer.write("/>%s"%(newl))

    def _get_attributes(self):
        self._ensure_attributes()
        zwróć NamedNodeMap(self._attrs, self._attrsNS, self)

    def hasAttributes(self):
        jeżeli self._attrs:
            zwróć Prawda
        inaczej:
            zwróć Nieprawda

    # DOM Level 3 attributes, based on the 22 Oct 2002 draft

    def setIdAttribute(self, name):
        idAttr = self.getAttributeNode(name)
        self.setIdAttributeNode(idAttr)

    def setIdAttributeNS(self, namespaceURI, localName):
        idAttr = self.getAttributeNodeNS(namespaceURI, localName)
        self.setIdAttributeNode(idAttr)

    def setIdAttributeNode(self, idAttr):
        jeżeli idAttr jest Nic albo nie self.isSameNode(idAttr.ownerElement):
            podnieś xml.dom.NotFoundErr()
        jeżeli _get_containing_entref(self) jest nie Nic:
            podnieś xml.dom.NoModificationAllowedErr()
        jeżeli nie idAttr._is_id:
            idAttr._is_id = Prawda
            self._magic_id_nodes += 1
            self.ownerDocument._magic_id_count += 1
            _clear_id_cache(self)

defproperty(Element, "attributes",
            doc="NamedNodeMap of attributes on the element.")
defproperty(Element, "localName",
            doc="Namespace-local name of this element.")


def _set_attribute_node(element, attr):
    _clear_id_cache(element)
    element._ensure_attributes()
    element._attrs[attr.name] = attr
    element._attrsNS[(attr.namespaceURI, attr.localName)] = attr

    # This creates a circular reference, but Element.unlink()
    # przerwijs the cycle since the references to the attribute
    # dictionaries are tossed.
    attr.ownerElement = element

klasa Childless:
    """Mixin that makes childless-ness easy to implement oraz avoids
    the complexity of the Node methods that deal przy children.
    """
    __slots__ = ()

    attributes = Nic
    childNodes = EmptyNodeList()
    firstChild = Nic
    lastChild = Nic

    def _get_firstChild(self):
        zwróć Nic

    def _get_lastChild(self):
        zwróć Nic

    def appendChild(self, node):
        podnieś xml.dom.HierarchyRequestErr(
            self.nodeName + " nodes cannot have children")

    def hasChildNodes(self):
        zwróć Nieprawda

    def insertBefore(self, newChild, refChild):
        podnieś xml.dom.HierarchyRequestErr(
            self.nodeName + " nodes do nie have children")

    def removeChild(self, oldChild):
        podnieś xml.dom.NotFoundErr(
            self.nodeName + " nodes do nie have children")

    def normalize(self):
        # For childless nodes, normalize() has nothing to do.
        dalej

    def replaceChild(self, newChild, oldChild):
        podnieś xml.dom.HierarchyRequestErr(
            self.nodeName + " nodes do nie have children")


klasa ProcessingInstruction(Childless, Node):
    nodeType = Node.PROCESSING_INSTRUCTION_NODE
    __slots__ = ('target', 'data')

    def __init__(self, target, data):
        self.target = target
        self.data = data

    # nodeValue jest an alias dla data
    def _get_nodeValue(self):
        zwróć self.data
    def _set_nodeValue(self, value):
        self.data = value
    nodeValue = property(_get_nodeValue, _set_nodeValue)

    # nodeName jest an alias dla target
    def _get_nodeName(self):
        zwróć self.target
    def _set_nodeName(self, value):
        self.target = value
    nodeName = property(_get_nodeName, _set_nodeName)

    def writexml(self, writer, indent="", addindent="", newl=""):
        writer.write("%s<?%s %s?>%s" % (indent,self.target, self.data, newl))


klasa CharacterData(Childless, Node):
    __slots__=('_data', 'ownerDocument','parentNode', 'previousSibling', 'nextSibling')

    def __init__(self):
        self.ownerDocument = self.parentNode = Nic
        self.previousSibling = self.nextSibling = Nic
        self._data = ''
        Node.__init__(self)

    def _get_length(self):
        zwróć len(self.data)
    __len__ = _get_length

    def _get_data(self):
        zwróć self._data
    def _set_data(self, data):
        self._data = data

    data = nodeValue = property(_get_data, _set_data)

    def __repr__(self):
        data = self.data
        jeżeli len(data) > 10:
            dotdotdot = "..."
        inaczej:
            dotdotdot = ""
        zwróć '<DOM %s node "%r%s">' % (
            self.__class__.__name__, data[0:10], dotdotdot)

    def substringData(self, offset, count):
        jeżeli offset < 0:
            podnieś xml.dom.IndexSizeErr("offset cannot be negative")
        jeżeli offset >= len(self.data):
            podnieś xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        jeżeli count < 0:
            podnieś xml.dom.IndexSizeErr("count cannot be negative")
        zwróć self.data[offset:offset+count]

    def appendData(self, arg):
        self.data = self.data + arg

    def insertData(self, offset, arg):
        jeżeli offset < 0:
            podnieś xml.dom.IndexSizeErr("offset cannot be negative")
        jeżeli offset >= len(self.data):
            podnieś xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        jeżeli arg:
            self.data = "%s%s%s" % (
                self.data[:offset], arg, self.data[offset:])

    def deleteData(self, offset, count):
        jeżeli offset < 0:
            podnieś xml.dom.IndexSizeErr("offset cannot be negative")
        jeżeli offset >= len(self.data):
            podnieś xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        jeżeli count < 0:
            podnieś xml.dom.IndexSizeErr("count cannot be negative")
        jeżeli count:
            self.data = self.data[:offset] + self.data[offset+count:]

    def replaceData(self, offset, count, arg):
        jeżeli offset < 0:
            podnieś xml.dom.IndexSizeErr("offset cannot be negative")
        jeżeli offset >= len(self.data):
            podnieś xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        jeżeli count < 0:
            podnieś xml.dom.IndexSizeErr("count cannot be negative")
        jeżeli count:
            self.data = "%s%s%s" % (
                self.data[:offset], arg, self.data[offset+count:])

defproperty(CharacterData, "length", doc="Length of the string data.")


klasa Text(CharacterData):
    __slots__ = ()

    nodeType = Node.TEXT_NODE
    nodeName = "#text"
    attributes = Nic

    def splitText(self, offset):
        jeżeli offset < 0 albo offset > len(self.data):
            podnieś xml.dom.IndexSizeErr("illegal offset value")
        newText = self.__class__()
        newText.data = self.data[offset:]
        newText.ownerDocument = self.ownerDocument
        next = self.nextSibling
        jeżeli self.parentNode oraz self w self.parentNode.childNodes:
            jeżeli next jest Nic:
                self.parentNode.appendChild(newText)
            inaczej:
                self.parentNode.insertBefore(newText, next)
        self.data = self.data[:offset]
        zwróć newText

    def writexml(self, writer, indent="", addindent="", newl=""):
        _write_data(writer, "%s%s%s" % (indent, self.data, newl))

    # DOM Level 3 (WD 9 April 2002)

    def _get_wholeText(self):
        L = [self.data]
        n = self.previousSibling
        dopóki n jest nie Nic:
            jeżeli n.nodeType w (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                L.insert(0, n.data)
                n = n.previousSibling
            inaczej:
                przerwij
        n = self.nextSibling
        dopóki n jest nie Nic:
            jeżeli n.nodeType w (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                L.append(n.data)
                n = n.nextSibling
            inaczej:
                przerwij
        zwróć ''.join(L)

    def replaceWholeText(self, content):
        # XXX This needs to be seriously changed jeżeli minidom ever
        # supports EntityReference nodes.
        parent = self.parentNode
        n = self.previousSibling
        dopóki n jest nie Nic:
            jeżeli n.nodeType w (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                next = n.previousSibling
                parent.removeChild(n)
                n = next
            inaczej:
                przerwij
        n = self.nextSibling
        jeżeli nie content:
            parent.removeChild(self)
        dopóki n jest nie Nic:
            jeżeli n.nodeType w (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                next = n.nextSibling
                parent.removeChild(n)
                n = next
            inaczej:
                przerwij
        jeżeli content:
            self.data = content
            zwróć self
        inaczej:
            zwróć Nic

    def _get_isWhitespaceInElementContent(self):
        jeżeli self.data.strip():
            zwróć Nieprawda
        elem = _get_containing_element(self)
        jeżeli elem jest Nic:
            zwróć Nieprawda
        info = self.ownerDocument._get_elem_info(elem)
        jeżeli info jest Nic:
            zwróć Nieprawda
        inaczej:
            zwróć info.isElementContent()

defproperty(Text, "isWhitespaceInElementContent",
            doc="Prawda iff this text node contains only whitespace"
                " oraz jest w element content.")
defproperty(Text, "wholeText",
            doc="The text of all logically-adjacent text nodes.")


def _get_containing_element(node):
    c = node.parentNode
    dopóki c jest nie Nic:
        jeżeli c.nodeType == Node.ELEMENT_NODE:
            zwróć c
        c = c.parentNode
    zwróć Nic

def _get_containing_entref(node):
    c = node.parentNode
    dopóki c jest nie Nic:
        jeżeli c.nodeType == Node.ENTITY_REFERENCE_NODE:
            zwróć c
        c = c.parentNode
    zwróć Nic


klasa Comment(CharacterData):
    nodeType = Node.COMMENT_NODE
    nodeName = "#comment"

    def __init__(self, data):
        CharacterData.__init__(self)
        self._data = data

    def writexml(self, writer, indent="", addindent="", newl=""):
        jeżeli "--" w self.data:
            podnieś ValueError("'--' jest nie allowed w a comment node")
        writer.write("%s<!--%s-->%s" % (indent, self.data, newl))


klasa CDATASection(Text):
    __slots__ = ()

    nodeType = Node.CDATA_SECTION_NODE
    nodeName = "#cdata-section"

    def writexml(self, writer, indent="", addindent="", newl=""):
        jeżeli self.data.find("]]>") >= 0:
            podnieś ValueError("']]>' nie allowed w a CDATA section")
        writer.write("<![CDATA[%s]]>" % self.data)


klasa ReadOnlySequentialNamedNodeMap(object):
    __slots__ = '_seq',

    def __init__(self, seq=()):
        # seq should be a list albo tuple
        self._seq = seq

    def __len__(self):
        zwróć len(self._seq)

    def _get_length(self):
        zwróć len(self._seq)

    def getNamedItem(self, name):
        dla n w self._seq:
            jeżeli n.nodeName == name:
                zwróć n

    def getNamedItemNS(self, namespaceURI, localName):
        dla n w self._seq:
            jeżeli n.namespaceURI == namespaceURI oraz n.localName == localName:
                zwróć n

    def __getitem__(self, name_or_tuple):
        jeżeli isinstance(name_or_tuple, tuple):
            node = self.getNamedItemNS(*name_or_tuple)
        inaczej:
            node = self.getNamedItem(name_or_tuple)
        jeżeli node jest Nic:
            podnieś KeyError(name_or_tuple)
        zwróć node

    def item(self, index):
        jeżeli index < 0:
            zwróć Nic
        spróbuj:
            zwróć self._seq[index]
        wyjąwszy IndexError:
            zwróć Nic

    def removeNamedItem(self, name):
        podnieś xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance jest read-only")

    def removeNamedItemNS(self, namespaceURI, localName):
        podnieś xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance jest read-only")

    def setNamedItem(self, node):
        podnieś xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance jest read-only")

    def setNamedItemNS(self, node):
        podnieś xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance jest read-only")

    def __getstate__(self):
        zwróć [self._seq]

    def __setstate__(self, state):
        self._seq = state[0]

defproperty(ReadOnlySequentialNamedNodeMap, "length",
            doc="Number of entries w the NamedNodeMap.")


klasa Identified:
    """Mix-in klasa that supports the publicId oraz systemId attributes."""

    __slots__ = 'publicId', 'systemId'

    def _identified_mixin_init(self, publicId, systemId):
        self.publicId = publicId
        self.systemId = systemId

    def _get_publicId(self):
        zwróć self.publicId

    def _get_systemId(self):
        zwróć self.systemId

klasa DocumentType(Identified, Childless, Node):
    nodeType = Node.DOCUMENT_TYPE_NODE
    nodeValue = Nic
    name = Nic
    publicId = Nic
    systemId = Nic
    internalSubset = Nic

    def __init__(self, qualifiedName):
        self.entities = ReadOnlySequentialNamedNodeMap()
        self.notations = ReadOnlySequentialNamedNodeMap()
        jeżeli qualifiedName:
            prefix, localname = _nssplit(qualifiedName)
            self.name = localname
        self.nodeName = self.name

    def _get_internalSubset(self):
        zwróć self.internalSubset

    def cloneNode(self, deep):
        jeżeli self.ownerDocument jest Nic:
            # it's ok
            clone = DocumentType(Nic)
            clone.name = self.name
            clone.nodeName = self.name
            operation = xml.dom.UserDataHandler.NODE_CLONED
            jeżeli deep:
                clone.entities._seq = []
                clone.notations._seq = []
                dla n w self.notations._seq:
                    notation = Notation(n.nodeName, n.publicId, n.systemId)
                    clone.notations._seq.append(nieation)
                    n._call_user_data_handler(operation, n, notation)
                dla e w self.entities._seq:
                    entity = Entity(e.nodeName, e.publicId, e.systemId,
                                    e.notationName)
                    entity.actualEncoding = e.actualEncoding
                    entity.encoding = e.encoding
                    entity.version = e.version
                    clone.entities._seq.append(entity)
                    e._call_user_data_handler(operation, n, entity)
            self._call_user_data_handler(operation, self, clone)
            zwróć clone
        inaczej:
            zwróć Nic

    def writexml(self, writer, indent="", addindent="", newl=""):
        writer.write("<!DOCTYPE ")
        writer.write(self.name)
        jeżeli self.publicId:
            writer.write("%s  PUBLIC '%s'%s  '%s'"
                         % (newl, self.publicId, newl, self.systemId))
        albo_inaczej self.systemId:
            writer.write("%s  SYSTEM '%s'" % (newl, self.systemId))
        jeżeli self.internalSubset jest nie Nic:
            writer.write(" [")
            writer.write(self.internalSubset)
            writer.write("]")
        writer.write(">"+newl)

klasa Entity(Identified, Node):
    attributes = Nic
    nodeType = Node.ENTITY_NODE
    nodeValue = Nic

    actualEncoding = Nic
    encoding = Nic
    version = Nic

    def __init__(self, name, publicId, systemId, notation):
        self.nodeName = name
        self.notationName = notation
        self.childNodes = NodeList()
        self._identified_mixin_init(publicId, systemId)

    def _get_actualEncoding(self):
        zwróć self.actualEncoding

    def _get_encoding(self):
        zwróć self.encoding

    def _get_version(self):
        zwróć self.version

    def appendChild(self, newChild):
        podnieś xml.dom.HierarchyRequestErr(
            "cannot append children to an entity node")

    def insertBefore(self, newChild, refChild):
        podnieś xml.dom.HierarchyRequestErr(
            "cannot insert children below an entity node")

    def removeChild(self, oldChild):
        podnieś xml.dom.HierarchyRequestErr(
            "cannot remove children z an entity node")

    def replaceChild(self, newChild, oldChild):
        podnieś xml.dom.HierarchyRequestErr(
            "cannot replace children of an entity node")

klasa Notation(Identified, Childless, Node):
    nodeType = Node.NOTATION_NODE
    nodeValue = Nic

    def __init__(self, name, publicId, systemId):
        self.nodeName = name
        self._identified_mixin_init(publicId, systemId)


klasa DOMImplementation(DOMImplementationLS):
    _features = [("core", "1.0"),
                 ("core", "2.0"),
                 ("core", Nic),
                 ("xml", "1.0"),
                 ("xml", "2.0"),
                 ("xml", Nic),
                 ("ls-load", "3.0"),
                 ("ls-load", Nic),
                 ]

    def hasFeature(self, feature, version):
        jeżeli version == "":
            version = Nic
        zwróć (feature.lower(), version) w self._features

    def createDocument(self, namespaceURI, qualifiedName, doctype):
        jeżeli doctype oraz doctype.parentNode jest nie Nic:
            podnieś xml.dom.WrongDocumentErr(
                "doctype object owned by another DOM tree")
        doc = self._create_document()

        add_root_element = nie (namespaceURI jest Nic
                                oraz qualifiedName jest Nic
                                oraz doctype jest Nic)

        jeżeli nie qualifiedName oraz add_root_element:
            # The spec jest unclear what to podnieś here; SyntaxErr
            # would be the other obvious candidate. Since Xerces podnieśs
            # InvalidCharacterErr, oraz since SyntaxErr jest nie listed
            # dla createDocument, that seems to be the better choice.
            # XXX: need to check dla illegal characters here oraz w
            # createElement.

            # DOM Level III clears this up when talking about the zwróć value
            # of this function.  If namespaceURI, qName oraz DocType are
            # Null the document jest returned without a document element
            # Otherwise jeżeli doctype albo namespaceURI are nie Nic
            # Then we go back to the above problem
            podnieś xml.dom.InvalidCharacterErr("Element przy no name")

        jeżeli add_root_element:
            prefix, localname = _nssplit(qualifiedName)
            jeżeli prefix == "xml" \
               oraz namespaceURI != "http://www.w3.org/XML/1998/namespace":
                podnieś xml.dom.NamespaceErr("illegal use of 'xml' prefix")
            jeżeli prefix oraz nie namespaceURI:
                podnieś xml.dom.NamespaceErr(
                    "illegal use of prefix without namespaces")
            element = doc.createElementNS(namespaceURI, qualifiedName)
            jeżeli doctype:
                doc.appendChild(doctype)
            doc.appendChild(element)

        jeżeli doctype:
            doctype.parentNode = doctype.ownerDocument = doc

        doc.doctype = doctype
        doc.implementation = self
        zwróć doc

    def createDocumentType(self, qualifiedName, publicId, systemId):
        doctype = DocumentType(qualifiedName)
        doctype.publicId = publicId
        doctype.systemId = systemId
        zwróć doctype

    # DOM Level 3 (WD 9 April 2002)

    def getInterface(self, feature):
        jeżeli self.hasFeature(feature, Nic):
            zwróć self
        inaczej:
            zwróć Nic

    # internal
    def _create_document(self):
        zwróć Document()

klasa ElementInfo(object):
    """Object that represents content-mousuń information dla an element.

    This implementation jest nie expected to be used w practice; DOM
    builders should provide implementations which do the right thing
    using information available to it.

    """

    __slots__ = 'tagName',

    def __init__(self, name):
        self.tagName = name

    def getAttributeType(self, aname):
        zwróć _no_type

    def getAttributeTypeNS(self, namespaceURI, localName):
        zwróć _no_type

    def isElementContent(self):
        zwróć Nieprawda

    def isEmpty(self):
        """Returns true iff this element jest declared to have an EMPTY
        content model."""
        zwróć Nieprawda

    def isId(self, aname):
        """Returns true iff the named attribute jest a DTD-style ID."""
        zwróć Nieprawda

    def isIdNS(self, namespaceURI, localName):
        """Returns true iff the identified attribute jest a DTD-style ID."""
        zwróć Nieprawda

    def __getstate__(self):
        zwróć self.tagName

    def __setstate__(self, state):
        self.tagName = state

def _clear_id_cache(node):
    jeżeli node.nodeType == Node.DOCUMENT_NODE:
        node._id_cache.clear()
        node._id_search_stack = Nic
    albo_inaczej _in_document(node):
        node.ownerDocument._id_cache.clear()
        node.ownerDocument._id_search_stack= Nic

klasa Document(Node, DocumentLS):
    __slots__ = ('_elem_info', 'doctype',
                 '_id_search_stack', 'childNodes', '_id_cache')
    _child_node_types = (Node.ELEMENT_NODE, Node.PROCESSING_INSTRUCTION_NODE,
                         Node.COMMENT_NODE, Node.DOCUMENT_TYPE_NODE)

    implementation = DOMImplementation()
    nodeType = Node.DOCUMENT_NODE
    nodeName = "#document"
    nodeValue = Nic
    attributes = Nic
    parentNode = Nic
    previousSibling = nextSibling = Nic


    # Document attributes z Level 3 (WD 9 April 2002)

    actualEncoding = Nic
    encoding = Nic
    standalone = Nic
    version = Nic
    strictErrorChecking = Nieprawda
    errorHandler = Nic
    documentURI = Nic

    _magic_id_count = 0

    def __init__(self):
        self.doctype = Nic
        self.childNodes = NodeList()
        # mapping of (namespaceURI, localName) -> ElementInfo
        #        oraz tagName -> ElementInfo
        self._elem_info = {}
        self._id_cache = {}
        self._id_search_stack = Nic

    def _get_elem_info(self, element):
        jeżeli element.namespaceURI:
            key = element.namespaceURI, element.localName
        inaczej:
            key = element.tagName
        zwróć self._elem_info.get(key)

    def _get_actualEncoding(self):
        zwróć self.actualEncoding

    def _get_doctype(self):
        zwróć self.doctype

    def _get_documentURI(self):
        zwróć self.documentURI

    def _get_encoding(self):
        zwróć self.encoding

    def _get_errorHandler(self):
        zwróć self.errorHandler

    def _get_standalone(self):
        zwróć self.standalone

    def _get_strictErrorChecking(self):
        zwróć self.strictErrorChecking

    def _get_version(self):
        zwróć self.version

    def appendChild(self, node):
        jeżeli node.nodeType nie w self._child_node_types:
            podnieś xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(node), repr(self)))
        jeżeli node.parentNode jest nie Nic:
            # This needs to be done before the next test since this
            # may *be* the document element, w which case it should
            # end up re-ordered to the end.
            node.parentNode.removeChild(node)

        jeżeli node.nodeType == Node.ELEMENT_NODE \
           oraz self._get_documentElement():
            podnieś xml.dom.HierarchyRequestErr(
                "two document elements disallowed")
        zwróć Node.appendChild(self, node)

    def removeChild(self, oldChild):
        spróbuj:
            self.childNodes.remove(oldChild)
        wyjąwszy ValueError:
            podnieś xml.dom.NotFoundErr()
        oldChild.nextSibling = oldChild.previousSibling = Nic
        oldChild.parentNode = Nic
        jeżeli self.documentElement jest oldChild:
            self.documentElement = Nic

        zwróć oldChild

    def _get_documentElement(self):
        dla node w self.childNodes:
            jeżeli node.nodeType == Node.ELEMENT_NODE:
                zwróć node

    def unlink(self):
        jeżeli self.doctype jest nie Nic:
            self.doctype.unlink()
            self.doctype = Nic
        Node.unlink(self)

    def cloneNode(self, deep):
        jeżeli nie deep:
            zwróć Nic
        clone = self.implementation.createDocument(Nic, Nic, Nic)
        clone.encoding = self.encoding
        clone.standalone = self.standalone
        clone.version = self.version
        dla n w self.childNodes:
            childclone = _clone_node(n, deep, clone)
            assert childclone.ownerDocument.isSameNode(clone)
            clone.childNodes.append(childclone)
            jeżeli childclone.nodeType == Node.DOCUMENT_NODE:
                assert clone.documentElement jest Nic
            albo_inaczej childclone.nodeType == Node.DOCUMENT_TYPE_NODE:
                assert clone.doctype jest Nic
                clone.doctype = childclone
            childclone.parentNode = clone
        self._call_user_data_handler(xml.dom.UserDataHandler.NODE_CLONED,
                                     self, clone)
        zwróć clone

    def createDocumentFragment(self):
        d = DocumentFragment()
        d.ownerDocument = self
        zwróć d

    def createElement(self, tagName):
        e = Element(tagName)
        e.ownerDocument = self
        zwróć e

    def createTextNode(self, data):
        jeżeli nie isinstance(data, str):
            podnieś TypeError("node contents must be a string")
        t = Text()
        t.data = data
        t.ownerDocument = self
        zwróć t

    def createCDATASection(self, data):
        jeżeli nie isinstance(data, str):
            podnieś TypeError("node contents must be a string")
        c = CDATASection()
        c.data = data
        c.ownerDocument = self
        zwróć c

    def createComment(self, data):
        c = Comment(data)
        c.ownerDocument = self
        zwróć c

    def createProcessingInstruction(self, target, data):
        p = ProcessingInstruction(target, data)
        p.ownerDocument = self
        zwróć p

    def createAttribute(self, qName):
        a = Attr(qName)
        a.ownerDocument = self
        a.value = ""
        zwróć a

    def createElementNS(self, namespaceURI, qualifiedName):
        prefix, localName = _nssplit(qualifiedName)
        e = Element(qualifiedName, namespaceURI, prefix)
        e.ownerDocument = self
        zwróć e

    def createAttributeNS(self, namespaceURI, qualifiedName):
        prefix, localName = _nssplit(qualifiedName)
        a = Attr(qualifiedName, namespaceURI, localName, prefix)
        a.ownerDocument = self
        a.value = ""
        zwróć a

    # A couple of implementation-specific helpers to create node types
    # nie supported by the W3C DOM specs:

    def _create_entity(self, name, publicId, systemId, notationName):
        e = Entity(name, publicId, systemId, notationName)
        e.ownerDocument = self
        zwróć e

    def _create_notation(self, name, publicId, systemId):
        n = Notation(name, publicId, systemId)
        n.ownerDocument = self
        zwróć n

    def getElementById(self, id):
        jeżeli id w self._id_cache:
            zwróć self._id_cache[id]
        jeżeli nie (self._elem_info albo self._magic_id_count):
            zwróć Nic

        stack = self._id_search_stack
        jeżeli stack jest Nic:
            # we never searched before, albo the cache has been cleared
            stack = [self.documentElement]
            self._id_search_stack = stack
        albo_inaczej nie stack:
            # Previous search was completed oraz cache jest still valid;
            # no matching node.
            zwróć Nic

        result = Nic
        dopóki stack:
            node = stack.pop()
            # add child elements to stack dla continued searching
            stack.extend([child dla child w node.childNodes
                          jeżeli child.nodeType w _nodeTypes_with_children])
            # check this node
            info = self._get_elem_info(node)
            jeżeli info:
                # We have to process all ID attributes before
                # returning w order to get all the attributes set to
                # be IDs using Element.setIdAttribute*().
                dla attr w node.attributes.values():
                    jeżeli attr.namespaceURI:
                        jeżeli info.isIdNS(attr.namespaceURI, attr.localName):
                            self._id_cache[attr.value] = node
                            jeżeli attr.value == id:
                                result = node
                            albo_inaczej nie node._magic_id_nodes:
                                przerwij
                    albo_inaczej info.isId(attr.name):
                        self._id_cache[attr.value] = node
                        jeżeli attr.value == id:
                            result = node
                        albo_inaczej nie node._magic_id_nodes:
                            przerwij
                    albo_inaczej attr._is_id:
                        self._id_cache[attr.value] = node
                        jeżeli attr.value == id:
                            result = node
                        albo_inaczej node._magic_id_nodes == 1:
                            przerwij
            albo_inaczej node._magic_id_nodes:
                dla attr w node.attributes.values():
                    jeżeli attr._is_id:
                        self._id_cache[attr.value] = node
                        jeżeli attr.value == id:
                            result = node
            jeżeli result jest nie Nic:
                przerwij
        zwróć result

    def getElementsByTagName(self, name):
        zwróć _get_elements_by_tagName_helper(self, name, NodeList())

    def getElementsByTagNameNS(self, namespaceURI, localName):
        zwróć _get_elements_by_tagName_ns_helper(
            self, namespaceURI, localName, NodeList())

    def isSupported(self, feature, version):
        zwróć self.implementation.hasFeature(feature, version)

    def importNode(self, node, deep):
        jeżeli node.nodeType == Node.DOCUMENT_NODE:
            podnieś xml.dom.NotSupportedErr("cannot zaimportuj document nodes")
        albo_inaczej node.nodeType == Node.DOCUMENT_TYPE_NODE:
            podnieś xml.dom.NotSupportedErr("cannot zaimportuj document type nodes")
        zwróć _clone_node(node, deep, self)

    def writexml(self, writer, indent="", addindent="", newl="", encoding=Nic):
        jeżeli encoding jest Nic:
            writer.write('<?xml version="1.0" ?>'+newl)
        inaczej:
            writer.write('<?xml version="1.0" encoding="%s"?>%s' % (
                encoding, newl))
        dla node w self.childNodes:
            node.writexml(writer, indent, addindent, newl)

    # DOM Level 3 (WD 9 April 2002)

    def renameNode(self, n, namespaceURI, name):
        jeżeli n.ownerDocument jest nie self:
            podnieś xml.dom.WrongDocumentErr(
                "cannot rename nodes z other documents;\n"
                "expected %s,\nfound %s" % (self, n.ownerDocument))
        jeżeli n.nodeType nie w (Node.ELEMENT_NODE, Node.ATTRIBUTE_NODE):
            podnieś xml.dom.NotSupportedErr(
                "renameNode() only applies to element oraz attribute nodes")
        jeżeli namespaceURI != EMPTY_NAMESPACE:
            jeżeli ':' w name:
                prefix, localName = name.split(':', 1)
                jeżeli (  prefix == "xmlns"
                      oraz namespaceURI != xml.dom.XMLNS_NAMESPACE):
                    podnieś xml.dom.NamespaceErr(
                        "illegal use of 'xmlns' prefix")
            inaczej:
                jeżeli (  name == "xmlns"
                      oraz namespaceURI != xml.dom.XMLNS_NAMESPACE
                      oraz n.nodeType == Node.ATTRIBUTE_NODE):
                    podnieś xml.dom.NamespaceErr(
                        "illegal use of the 'xmlns' attribute")
                prefix = Nic
                localName = name
        inaczej:
            prefix = Nic
            localName = Nic
        jeżeli n.nodeType == Node.ATTRIBUTE_NODE:
            element = n.ownerElement
            jeżeli element jest nie Nic:
                is_id = n._is_id
                element.removeAttributeNode(n)
        inaczej:
            element = Nic
        n.prefix = prefix
        n._localName = localName
        n.namespaceURI = namespaceURI
        n.nodeName = name
        jeżeli n.nodeType == Node.ELEMENT_NODE:
            n.tagName = name
        inaczej:
            # attribute node
            n.name = name
            jeżeli element jest nie Nic:
                element.setAttributeNode(n)
                jeżeli is_id:
                    element.setIdAttributeNode(n)
        # It's nie clear z a semantic perspective whether we should
        # call the user data handlers dla the NODE_RENAMED event since
        # we're re-using the existing node.  The draft spec has been
        # interpreted jako meaning "no, don't call the handler unless a
        # new node jest created."
        zwróć n

defproperty(Document, "documentElement",
            doc="Top-level element of this document.")


def _clone_node(node, deep, newOwnerDocument):
    """
    Clone a node oraz give it the new owner document.
    Called by Node.cloneNode oraz Document.importNode
    """
    jeżeli node.ownerDocument.isSameNode(newOwnerDocument):
        operation = xml.dom.UserDataHandler.NODE_CLONED
    inaczej:
        operation = xml.dom.UserDataHandler.NODE_IMPORTED
    jeżeli node.nodeType == Node.ELEMENT_NODE:
        clone = newOwnerDocument.createElementNS(node.namespaceURI,
                                                 node.nodeName)
        dla attr w node.attributes.values():
            clone.setAttributeNS(attr.namespaceURI, attr.nodeName, attr.value)
            a = clone.getAttributeNodeNS(attr.namespaceURI, attr.localName)
            a.specified = attr.specified

        jeżeli deep:
            dla child w node.childNodes:
                c = _clone_node(child, deep, newOwnerDocument)
                clone.appendChild(c)

    albo_inaczej node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
        clone = newOwnerDocument.createDocumentFragment()
        jeżeli deep:
            dla child w node.childNodes:
                c = _clone_node(child, deep, newOwnerDocument)
                clone.appendChild(c)

    albo_inaczej node.nodeType == Node.TEXT_NODE:
        clone = newOwnerDocument.createTextNode(node.data)
    albo_inaczej node.nodeType == Node.CDATA_SECTION_NODE:
        clone = newOwnerDocument.createCDATASection(node.data)
    albo_inaczej node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
        clone = newOwnerDocument.createProcessingInstruction(node.target,
                                                             node.data)
    albo_inaczej node.nodeType == Node.COMMENT_NODE:
        clone = newOwnerDocument.createComment(node.data)
    albo_inaczej node.nodeType == Node.ATTRIBUTE_NODE:
        clone = newOwnerDocument.createAttributeNS(node.namespaceURI,
                                                   node.nodeName)
        clone.specified = Prawda
        clone.value = node.value
    albo_inaczej node.nodeType == Node.DOCUMENT_TYPE_NODE:
        assert node.ownerDocument jest nie newOwnerDocument
        operation = xml.dom.UserDataHandler.NODE_IMPORTED
        clone = newOwnerDocument.implementation.createDocumentType(
            node.name, node.publicId, node.systemId)
        clone.ownerDocument = newOwnerDocument
        jeżeli deep:
            clone.entities._seq = []
            clone.notations._seq = []
            dla n w node.notations._seq:
                notation = Notation(n.nodeName, n.publicId, n.systemId)
                notation.ownerDocument = newOwnerDocument
                clone.notations._seq.append(nieation)
                jeżeli hasattr(n, '_call_user_data_handler'):
                    n._call_user_data_handler(operation, n, notation)
            dla e w node.entities._seq:
                entity = Entity(e.nodeName, e.publicId, e.systemId,
                                e.notationName)
                entity.actualEncoding = e.actualEncoding
                entity.encoding = e.encoding
                entity.version = e.version
                entity.ownerDocument = newOwnerDocument
                clone.entities._seq.append(entity)
                jeżeli hasattr(e, '_call_user_data_handler'):
                    e._call_user_data_handler(operation, n, entity)
    inaczej:
        # Note the cloning of Document oraz DocumentType nodes jest
        # implementation specific.  minidom handles those cases
        # directly w the cloneNode() methods.
        podnieś xml.dom.NotSupportedErr("Cannot clone node %s" % repr(node))

    # Check dla _call_user_data_handler() since this could conceivably
    # used przy other DOM implementations (one of the FourThought
    # DOMs, perhaps?).
    jeżeli hasattr(node, '_call_user_data_handler'):
        node._call_user_data_handler(operation, node, clone)
    zwróć clone


def _nssplit(qualifiedName):
    fields = qualifiedName.split(':', 1)
    jeżeli len(fields) == 2:
        zwróć fields
    inaczej:
        zwróć (Nic, fields[0])


def _do_pulldom_parse(func, args, kwargs):
    events = func(*args, **kwargs)
    toktype, rootNode = events.getEvent()
    events.expandNode(rootNode)
    events.clear()
    zwróć rootNode

def parse(file, parser=Nic, bufsize=Nic):
    """Parse a file into a DOM by filename albo file object."""
    jeżeli parser jest Nic oraz nie bufsize:
        z xml.dom zaimportuj expatbuilder
        zwróć expatbuilder.parse(file)
    inaczej:
        z xml.dom zaimportuj pulldom
        zwróć _do_pulldom_parse(pulldom.parse, (file,),
            {'parser': parser, 'bufsize': bufsize})

def parseString(string, parser=Nic):
    """Parse a file into a DOM z a string."""
    jeżeli parser jest Nic:
        z xml.dom zaimportuj expatbuilder
        zwróć expatbuilder.parseString(string)
    inaczej:
        z xml.dom zaimportuj pulldom
        zwróć _do_pulldom_parse(pulldom.parseString, (string,),
                                 {'parser': parser})

def getDOMImplementation(features=Nic):
    jeżeli features:
        jeżeli isinstance(features, str):
            features = domreg._parse_feature_string(features)
        dla f, v w features:
            jeżeli nie Document.implementation.hasFeature(f, v):
                zwróć Nic
    zwróć Document.implementation
