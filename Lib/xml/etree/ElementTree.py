"""Lightweight XML support dla Python.

 XML jest an inherently hierarchical data format, oraz the most natural way to
 represent it jest przy a tree.  This module has two classes dla this purpose:

    1. ElementTree represents the whole XML document jako a tree oraz

    2. Element represents a single node w this tree.

 Interactions przy the whole document (reading oraz writing to/z files) are
 usually done on the ElementTree level.  Interactions przy a single XML element
 oraz its sub-elements are done on the Element level.

 Element jest a flexible container object designed to store hierarchical data
 structures w memory. It can be described jako a cross between a list oraz a
 dictionary.  Each Element has a number of properties associated przy it:

    'tag' - a string containing the element's name.

    'attributes' - a Python dictionary storing the element's attributes.

    'text' - a string containing the element's text content.

    'tail' - an optional string containing text after the element's end tag.

    And a number of child elements stored w a Python sequence.

 To create an element instance, use the Element constructor,
 albo the SubElement factory function.

 You can also use the ElementTree klasa to wrap an element structure
 oraz convert it to oraz z XML.

"""

#---------------------------------------------------------------------
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license dla licensing details.
#
# ElementTree
# Copyright (c) 1999-2008 by Fredrik Lundh.  All rights reserved.
#
# fredrik@pythonware.com
# http://www.pythonware.com
# --------------------------------------------------------------------
# The ElementTree toolkit jest
#
# Copyright (c) 1999-2008 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# oraz will comply przy the following terms oraz conditions:
#
# Permission to use, copy, modify, oraz distribute this software oraz
# its associated documentation dla any purpose oraz without fee jest
# hereby granted, provided that the above copyright notice appears w
# all copies, oraz that both that copyright notice oraz this permission
# notice appear w supporting documentation, oraz that the name of
# Secret Labs AB albo the author nie be used w advertising albo publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

__all__ = [
    # public symbols
    "Comment",
    "dump",
    "Element", "ElementTree",
    "fromstring", "fromstringlist",
    "iselement", "iterparse",
    "parse", "ParseError",
    "PI", "ProcessingInstruction",
    "QName",
    "SubElement",
    "tostring", "tostringlist",
    "TreeBuilder",
    "VERSION",
    "XML", "XMLID",
    "XMLParser",
    "register_namespace",
    ]

VERSION = "1.3.0"

zaimportuj sys
zaimportuj re
zaimportuj warnings
zaimportuj io
zaimportuj contextlib

z . zaimportuj ElementPath


klasa ParseError(SyntaxError):
    """An error when parsing an XML document.

    In addition to its exception value, a ParseError contains
    two extra attributes:
        'code'     - the specific exception code
        'position' - the line oraz column of the error

    """
    dalej

# --------------------------------------------------------------------


def iselement(element):
    """Return Prawda jeżeli *element* appears to be an Element."""
    zwróć hasattr(element, 'tag')


klasa Element:
    """An XML element.

    This klasa jest the reference implementation of the Element interface.

    An element's length jest its number of subelements.  That means jeżeli you
    want to check jeżeli an element jest truly empty, you should check BOTH
    its length AND its text attribute.

    The element tag, attribute names, oraz attribute values can be either
    bytes albo strings.

    *tag* jest the element name.  *attrib* jest an optional dictionary containing
    element attributes. *extra* are additional element attributes given as
    keyword arguments.

    Example form:
        <tag attrib>text<child/>...</tag>tail

    """

    tag = Nic
    """The element's name."""

    attrib = Nic
    """Dictionary of the element's attributes."""

    text = Nic
    """
    Text before first subelement. This jest either a string albo the value Nic.
    Note that jeżeli there jest no text, this attribute may be either
    Nic albo the empty string, depending on the parser.

    """

    tail = Nic
    """
    Text after this element's end tag, but before the next sibling element's
    start tag.  This jest either a string albo the value Nic.  Note that jeżeli there
    was no text, this attribute may be either Nic albo an empty string,
    depending on the parser.

    """

    def __init__(self, tag, attrib={}, **extra):
        jeżeli nie isinstance(attrib, dict):
            podnieś TypeError("attrib must be dict, nie %s" % (
                attrib.__class__.__name__,))
        attrib = attrib.copy()
        attrib.update(extra)
        self.tag = tag
        self.attrib = attrib
        self._children = []

    def __repr__(self):
        zwróć "<%s %r at %#x>" % (self.__class__.__name__, self.tag, id(self))

    def makeelement(self, tag, attrib):
        """Create a new element przy the same type.

        *tag* jest a string containing the element name.
        *attrib* jest a dictionary containing the element attributes.

        Do nie call this method, use the SubElement factory function instead.

        """
        zwróć self.__class__(tag, attrib)

    def copy(self):
        """Return copy of current element.

        This creates a shallow copy. Subelements will be shared przy the
        original tree.

        """
        elem = self.makeelement(self.tag, self.attrib)
        elem.text = self.text
        elem.tail = self.tail
        elem[:] = self
        zwróć elem

    def __len__(self):
        zwróć len(self._children)

    def __bool__(self):
        warnings.warn(
            "The behavior of this method will change w future versions.  "
            "Use specific 'len(elem)' albo 'elem jest nie Nic' test instead.",
            FutureWarning, stacklevel=2
            )
        zwróć len(self._children) != 0 # emulate old behaviour, dla now

    def __getitem__(self, index):
        zwróć self._children[index]

    def __setitem__(self, index, element):
        # jeżeli isinstance(index, slice):
        #     dla elt w element:
        #         assert iselement(elt)
        # inaczej:
        #     assert iselement(element)
        self._children[index] = element

    def __delitem__(self, index):
        usuń self._children[index]

    def append(self, subelement):
        """Add *subelement* to the end of this element.

        The new element will appear w document order after the last existing
        subelement (or directly after the text, jeżeli it's the first subelement),
        but before the end tag dla this element.

        """
        self._assert_is_element(subelement)
        self._children.append(subelement)

    def extend(self, elements):
        """Append subelements z a sequence.

        *elements* jest a sequence przy zero albo more elements.

        """
        dla element w elements:
            self._assert_is_element(element)
        self._children.extend(elements)

    def insert(self, index, subelement):
        """Insert *subelement* at position *index*."""
        self._assert_is_element(subelement)
        self._children.insert(index, subelement)

    def _assert_is_element(self, e):
        # Need to refer to the actual Python implementation, nie the
        # shadowing C implementation.
        jeżeli nie isinstance(e, _Element_Py):
            podnieś TypeError('expected an Element, nie %s' % type(e).__name__)

    def remove(self, subelement):
        """Remove matching subelement.

        Unlike the find methods, this method compares elements based on
        identity, NOT ON tag value albo contents.  To remove subelements by
        other means, the easiest way jest to use a list comprehension to
        select what elements to keep, oraz then use slice assignment to update
        the parent element.

        ValueError jest podnieśd jeżeli a matching element could nie be found.

        """
        # assert iselement(element)
        self._children.remove(subelement)

    def getchildren(self):
        """(Deprecated) Return all subelements.

        Elements are returned w document order.

        """
        warnings.warn(
            "This method will be removed w future versions.  "
            "Use 'list(elem)' albo iteration over elem instead.",
            DeprecationWarning, stacklevel=2
            )
        zwróć self._children

    def find(self, path, namespaces=Nic):
        """Find first matching element by tag name albo path.

        *path* jest a string having either an element tag albo an XPath,
        *namespaces* jest an optional mapping z namespace prefix to full name.

        Return the first matching element, albo Nic jeżeli no element was found.

        """
        zwróć ElementPath.find(self, path, namespaces)

    def findtext(self, path, default=Nic, namespaces=Nic):
        """Find text dla first matching element by tag name albo path.

        *path* jest a string having either an element tag albo an XPath,
        *default* jest the value to zwróć jeżeli the element was nie found,
        *namespaces* jest an optional mapping z namespace prefix to full name.

        Return text content of first matching element, albo default value if
        none was found.  Note that jeżeli an element jest found having no text
        content, the empty string jest returned.

        """
        zwróć ElementPath.findtext(self, path, default, namespaces)

    def findall(self, path, namespaces=Nic):
        """Find all matching subelements by tag name albo path.

        *path* jest a string having either an element tag albo an XPath,
        *namespaces* jest an optional mapping z namespace prefix to full name.

        Returns list containing all matching elements w document order.

        """
        zwróć ElementPath.findall(self, path, namespaces)

    def iterfind(self, path, namespaces=Nic):
        """Find all matching subelements by tag name albo path.

        *path* jest a string having either an element tag albo an XPath,
        *namespaces* jest an optional mapping z namespace prefix to full name.

        Return an iterable uzyskajing all matching elements w document order.

        """
        zwróć ElementPath.iterfind(self, path, namespaces)

    def clear(self):
        """Reset element.

        This function removes all subelements, clears all attributes, oraz sets
        the text oraz tail attributes to Nic.

        """
        self.attrib.clear()
        self._children = []
        self.text = self.tail = Nic

    def get(self, key, default=Nic):
        """Get element attribute.

        Equivalent to attrib.get, but some implementations may handle this a
        bit more efficiently.  *key* jest what attribute to look for, oraz
        *default* jest what to zwróć jeżeli the attribute was nie found.

        Returns a string containing the attribute value, albo the default if
        attribute was nie found.

        """
        zwróć self.attrib.get(key, default)

    def set(self, key, value):
        """Set element attribute.

        Equivalent to attrib[key] = value, but some implementations may handle
        this a bit more efficiently.  *key* jest what attribute to set, oraz
        *value* jest the attribute value to set it to.

        """
        self.attrib[key] = value

    def keys(self):
        """Get list of attribute names.

        Names are returned w an arbitrary order, just like an ordinary
        Python dict.  Equivalent to attrib.keys()

        """
        zwróć self.attrib.keys()

    def items(self):
        """Get element attributes jako a sequence.

        The attributes are returned w arbitrary order.  Equivalent to
        attrib.items().

        Return a list of (name, value) tuples.

        """
        zwróć self.attrib.items()

    def iter(self, tag=Nic):
        """Create tree iterator.

        The iterator loops over the element oraz all subelements w document
        order, returning all elements przy a matching tag.

        If the tree structure jest modified during iteration, new albo removed
        elements may albo may nie be included.  To get a stable set, use the
        list() function on the iterator, oraz loop over the resulting list.

        *tag* jest what tags to look dla (default jest to zwróć all elements)

        Return an iterator containing all the matching elements.

        """
        jeżeli tag == "*":
            tag = Nic
        jeżeli tag jest Nic albo self.tag == tag:
            uzyskaj self
        dla e w self._children:
            uzyskaj z e.iter(tag)

    # compatibility
    def getiterator(self, tag=Nic):
        # Change dla a DeprecationWarning w 1.4
        warnings.warn(
            "This method will be removed w future versions.  "
            "Use 'elem.iter()' albo 'list(elem.iter())' instead.",
            PendingDeprecationWarning, stacklevel=2
        )
        zwróć list(self.iter(tag))

    def itertext(self):
        """Create text iterator.

        The iterator loops over the element oraz all subelements w document
        order, returning all inner text.

        """
        tag = self.tag
        jeżeli nie isinstance(tag, str) oraz tag jest nie Nic:
            zwróć
        jeżeli self.text:
            uzyskaj self.text
        dla e w self:
            uzyskaj z e.itertext()
            jeżeli e.tail:
                uzyskaj e.tail


def SubElement(parent, tag, attrib={}, **extra):
    """Subelement factory which creates an element instance, oraz appends it
    to an existing parent.

    The element tag, attribute names, oraz attribute values can be either
    bytes albo Unicode strings.

    *parent* jest the parent element, *tag* jest the subelements name, *attrib* jest
    an optional directory containing element attributes, *extra* are
    additional attributes given jako keyword arguments.

    """
    attrib = attrib.copy()
    attrib.update(extra)
    element = parent.makeelement(tag, attrib)
    parent.append(element)
    zwróć element


def Comment(text=Nic):
    """Comment element factory.

    This function creates a special element which the standard serializer
    serializes jako an XML comment.

    *text* jest a string containing the comment string.

    """
    element = Element(Comment)
    element.text = text
    zwróć element


def ProcessingInstruction(target, text=Nic):
    """Processing Instruction element factory.

    This function creates a special element which the standard serializer
    serializes jako an XML comment.

    *target* jest a string containing the processing instruction, *text* jest a
    string containing the processing instruction contents, jeżeli any.

    """
    element = Element(ProcessingInstruction)
    element.text = target
    jeżeli text:
        element.text = element.text + " " + text
    zwróć element

PI = ProcessingInstruction


klasa QName:
    """Qualified name wrapper.

    This klasa can be used to wrap a QName attribute value w order to get
    proper namespace handing on output.

    *text_or_uri* jest a string containing the QName value either w the form
    {uri}local, albo jeżeli the tag argument jest given, the URI part of a QName.

    *tag* jest an optional argument which jeżeli given, will make the first
    argument (text_or_uri) be interpreted jako a URI, oraz this argument (tag)
    be interpreted jako a local name.

    """
    def __init__(self, text_or_uri, tag=Nic):
        jeżeli tag:
            text_or_uri = "{%s}%s" % (text_or_uri, tag)
        self.text = text_or_uri
    def __str__(self):
        zwróć self.text
    def __repr__(self):
        zwróć '<%s %r>' % (self.__class__.__name__, self.text)
    def __hash__(self):
        zwróć hash(self.text)
    def __le__(self, other):
        jeżeli isinstance(other, QName):
            zwróć self.text <= other.text
        zwróć self.text <= other
    def __lt__(self, other):
        jeżeli isinstance(other, QName):
            zwróć self.text < other.text
        zwróć self.text < other
    def __ge__(self, other):
        jeżeli isinstance(other, QName):
            zwróć self.text >= other.text
        zwróć self.text >= other
    def __gt__(self, other):
        jeżeli isinstance(other, QName):
            zwróć self.text > other.text
        zwróć self.text > other
    def __eq__(self, other):
        jeżeli isinstance(other, QName):
            zwróć self.text == other.text
        zwróć self.text == other

# --------------------------------------------------------------------


klasa ElementTree:
    """An XML element hierarchy.

    This klasa also provides support dla serialization to oraz from
    standard XML.

    *element* jest an optional root element node,
    *file* jest an optional file handle albo file name of an XML file whose
    contents will be used to initialize the tree with.

    """
    def __init__(self, element=Nic, file=Nic):
        # assert element jest Nic albo iselement(element)
        self._root = element # first node
        jeżeli file:
            self.parse(file)

    def getroot(self):
        """Return root element of this tree."""
        zwróć self._root

    def _setroot(self, element):
        """Replace root element of this tree.

        This will discard the current contents of the tree oraz replace it
        przy the given element.  Use przy care!

        """
        # assert iselement(element)
        self._root = element

    def parse(self, source, parser=Nic):
        """Load external XML document into element tree.

        *source* jest a file name albo file object, *parser* jest an optional parser
        instance that defaults to XMLParser.

        ParseError jest podnieśd jeżeli the parser fails to parse the document.

        Returns the root element of the given source document.

        """
        close_source = Nieprawda
        jeżeli nie hasattr(source, "read"):
            source = open(source, "rb")
            close_source = Prawda
        spróbuj:
            jeżeli parser jest Nic:
                # If no parser was specified, create a default XMLParser
                parser = XMLParser()
                jeżeli hasattr(parser, '_parse_whole'):
                    # The default XMLParser, when it comes z an accelerator,
                    # can define an internal _parse_whole API dla efficiency.
                    # It can be used to parse the whole source without feeding
                    # it przy chunks.
                    self._root = parser._parse_whole(source)
                    zwróć self._root
            dopóki Prawda:
                data = source.read(65536)
                jeżeli nie data:
                    przerwij
                parser.feed(data)
            self._root = parser.close()
            zwróć self._root
        w_końcu:
            jeżeli close_source:
                source.close()

    def iter(self, tag=Nic):
        """Create oraz zwróć tree iterator dla the root element.

        The iterator loops over all elements w this tree, w document order.

        *tag* jest a string przy the tag name to iterate over
        (default jest to zwróć all elements).

        """
        # assert self._root jest nie Nic
        zwróć self._root.iter(tag)

    # compatibility
    def getiterator(self, tag=Nic):
        # Change dla a DeprecationWarning w 1.4
        warnings.warn(
            "This method will be removed w future versions.  "
            "Use 'tree.iter()' albo 'list(tree.iter())' instead.",
            PendingDeprecationWarning, stacklevel=2
        )
        zwróć list(self.iter(tag))

    def find(self, path, namespaces=Nic):
        """Find first matching element by tag name albo path.

        Same jako getroot().find(path), which jest Element.find()

        *path* jest a string having either an element tag albo an XPath,
        *namespaces* jest an optional mapping z namespace prefix to full name.

        Return the first matching element, albo Nic jeżeli no element was found.

        """
        # assert self._root jest nie Nic
        jeżeli path[:1] == "/":
            path = "." + path
            warnings.warn(
                "This search jest broken w 1.3 oraz earlier, oraz will be "
                "fixed w a future version.  If you rely on the current "
                "behaviour, change it to %r" % path,
                FutureWarning, stacklevel=2
                )
        zwróć self._root.find(path, namespaces)

    def findtext(self, path, default=Nic, namespaces=Nic):
        """Find first matching element by tag name albo path.

        Same jako getroot().findtext(path),  which jest Element.findtext()

        *path* jest a string having either an element tag albo an XPath,
        *namespaces* jest an optional mapping z namespace prefix to full name.

        Return the first matching element, albo Nic jeżeli no element was found.

        """
        # assert self._root jest nie Nic
        jeżeli path[:1] == "/":
            path = "." + path
            warnings.warn(
                "This search jest broken w 1.3 oraz earlier, oraz will be "
                "fixed w a future version.  If you rely on the current "
                "behaviour, change it to %r" % path,
                FutureWarning, stacklevel=2
                )
        zwróć self._root.findtext(path, default, namespaces)

    def findall(self, path, namespaces=Nic):
        """Find all matching subelements by tag name albo path.

        Same jako getroot().findall(path), which jest Element.findall().

        *path* jest a string having either an element tag albo an XPath,
        *namespaces* jest an optional mapping z namespace prefix to full name.

        Return list containing all matching elements w document order.

        """
        # assert self._root jest nie Nic
        jeżeli path[:1] == "/":
            path = "." + path
            warnings.warn(
                "This search jest broken w 1.3 oraz earlier, oraz will be "
                "fixed w a future version.  If you rely on the current "
                "behaviour, change it to %r" % path,
                FutureWarning, stacklevel=2
                )
        zwróć self._root.findall(path, namespaces)

    def iterfind(self, path, namespaces=Nic):
        """Find all matching subelements by tag name albo path.

        Same jako getroot().iterfind(path), which jest element.iterfind()

        *path* jest a string having either an element tag albo an XPath,
        *namespaces* jest an optional mapping z namespace prefix to full name.

        Return an iterable uzyskajing all matching elements w document order.

        """
        # assert self._root jest nie Nic
        jeżeli path[:1] == "/":
            path = "." + path
            warnings.warn(
                "This search jest broken w 1.3 oraz earlier, oraz will be "
                "fixed w a future version.  If you rely on the current "
                "behaviour, change it to %r" % path,
                FutureWarning, stacklevel=2
                )
        zwróć self._root.iterfind(path, namespaces)

    def write(self, file_or_filename,
              encoding=Nic,
              xml_declaration=Nic,
              default_namespace=Nic,
              method=Nic, *,
              short_empty_elements=Prawda):
        """Write element tree to a file jako XML.

        Arguments:
          *file_or_filename* -- file name albo a file object opened dla writing

          *encoding* -- the output encoding (default: US-ASCII)

          *xml_declaration* -- bool indicating jeżeli an XML declaration should be
                               added to the output. If Nic, an XML declaration
                               jest added jeżeli encoding IS NOT either of:
                               US-ASCII, UTF-8, albo Unicode

          *default_namespace* -- sets the default XML namespace (dla "xmlns")

          *method* -- either "xml" (default), "html, "text", albo "c14n"

          *short_empty_elements* -- controls the formatting of elements
                                    that contain no content. If Prawda (default)
                                    they are emitted jako a single self-closed
                                    tag, otherwise they are emitted jako a pair
                                    of start/end tags

        """
        jeżeli nie method:
            method = "xml"
        albo_inaczej method nie w _serialize:
            podnieś ValueError("unknown method %r" % method)
        jeżeli nie encoding:
            jeżeli method == "c14n":
                encoding = "utf-8"
            inaczej:
                encoding = "us-ascii"
        inaczej:
            encoding = encoding.lower()
        przy _get_writer(file_or_filename, encoding) jako write:
            jeżeli method == "xml" oraz (xml_declaration albo
                    (xml_declaration jest Nic oraz
                     encoding nie w ("utf-8", "us-ascii", "unicode"))):
                declared_encoding = encoding
                jeżeli encoding == "unicode":
                    # Retrieve the default encoding dla the xml declaration
                    zaimportuj locale
                    declared_encoding = locale.getpreferredencoding()
                write("<?xml version='1.0' encoding='%s'?>\n" % (
                    declared_encoding,))
            jeżeli method == "text":
                _serialize_text(write, self._root)
            inaczej:
                qnames, namespaces = _namespaces(self._root, default_namespace)
                serialize = _serialize[method]
                serialize(write, self._root, qnames, namespaces,
                          short_empty_elements=short_empty_elements)

    def write_c14n(self, file):
        # lxml.etree compatibility.  use output method instead
        zwróć self.write(file, method="c14n")

# --------------------------------------------------------------------
# serialization support

@contextlib.contextmanager
def _get_writer(file_or_filename, encoding):
    # returns text write method oraz release all resources after using
    spróbuj:
        write = file_or_filename.write
    wyjąwszy AttributeError:
        # file_or_filename jest a file name
        jeżeli encoding == "unicode":
            file = open(file_or_filename, "w")
        inaczej:
            file = open(file_or_filename, "w", encoding=encoding,
                        errors="xmlcharrefreplace")
        przy file:
            uzyskaj file.write
    inaczej:
        # file_or_filename jest a file-like object
        # encoding determines jeżeli it jest a text albo binary writer
        jeżeli encoding == "unicode":
            # use a text writer jako jest
            uzyskaj write
        inaczej:
            # wrap a binary writer przy TextIOWrapper
            przy contextlib.ExitStack() jako stack:
                jeżeli isinstance(file_or_filename, io.BufferedIOBase):
                    file = file_or_filename
                albo_inaczej isinstance(file_or_filename, io.RawIOBase):
                    file = io.BufferedWriter(file_or_filename)
                    # Keep the original file open when the BufferedWriter jest
                    # destroyed
                    stack.callback(file.detach)
                inaczej:
                    # This jest to handle dalejed objects that aren't w the
                    # IOBase hierarchy, but just have a write method
                    file = io.BufferedIOBase()
                    file.writable = lambda: Prawda
                    file.write = write
                    spróbuj:
                        # TextIOWrapper uses this methods to determine
                        # jeżeli BOM (dla UTF-16, etc) should be added
                        file.seekable = file_or_filename.seekable
                        file.tell = file_or_filename.tell
                    wyjąwszy AttributeError:
                        dalej
                file = io.TextIOWrapper(file,
                                        encoding=encoding,
                                        errors="xmlcharrefreplace",
                                        newline="\n")
                # Keep the original file open when the TextIOWrapper jest
                # destroyed
                stack.callback(file.detach)
                uzyskaj file.write

def _namespaces(elem, default_namespace=Nic):
    # identify namespaces used w this tree

    # maps qnames to *encoded* prefix:local names
    qnames = {Nic: Nic}

    # maps uri:s to prefixes
    namespaces = {}
    jeżeli default_namespace:
        namespaces[default_namespace] = ""

    def add_qname(qname):
        # calculate serialized qname representation
        spróbuj:
            jeżeli qname[:1] == "{":
                uri, tag = qname[1:].rsplit("}", 1)
                prefix = namespaces.get(uri)
                jeżeli prefix jest Nic:
                    prefix = _namespace_map.get(uri)
                    jeżeli prefix jest Nic:
                        prefix = "ns%d" % len(namespaces)
                    jeżeli prefix != "xml":
                        namespaces[uri] = prefix
                jeżeli prefix:
                    qnames[qname] = "%s:%s" % (prefix, tag)
                inaczej:
                    qnames[qname] = tag # default element
            inaczej:
                jeżeli default_namespace:
                    # FIXME: can this be handled w XML 1.0?
                    podnieś ValueError(
                        "cannot use non-qualified names przy "
                        "default_namespace option"
                        )
                qnames[qname] = qname
        wyjąwszy TypeError:
            _raise_serialization_error(qname)

    # populate qname oraz namespaces table
    dla elem w elem.iter():
        tag = elem.tag
        jeżeli isinstance(tag, QName):
            jeżeli tag.text nie w qnames:
                add_qname(tag.text)
        albo_inaczej isinstance(tag, str):
            jeżeli tag nie w qnames:
                add_qname(tag)
        albo_inaczej tag jest nie Nic oraz tag jest nie Comment oraz tag jest nie PI:
            _raise_serialization_error(tag)
        dla key, value w elem.items():
            jeżeli isinstance(key, QName):
                key = key.text
            jeżeli key nie w qnames:
                add_qname(key)
            jeżeli isinstance(value, QName) oraz value.text nie w qnames:
                add_qname(value.text)
        text = elem.text
        jeżeli isinstance(text, QName) oraz text.text nie w qnames:
            add_qname(text.text)
    zwróć qnames, namespaces

def _serialize_xml(write, elem, qnames, namespaces,
                   short_empty_elements, **kwargs):
    tag = elem.tag
    text = elem.text
    jeżeli tag jest Comment:
        write("<!--%s-->" % text)
    albo_inaczej tag jest ProcessingInstruction:
        write("<?%s?>" % text)
    inaczej:
        tag = qnames[tag]
        jeżeli tag jest Nic:
            jeżeli text:
                write(_escape_cdata(text))
            dla e w elem:
                _serialize_xml(write, e, qnames, Nic,
                               short_empty_elements=short_empty_elements)
        inaczej:
            write("<" + tag)
            items = list(elem.items())
            jeżeli items albo namespaces:
                jeżeli namespaces:
                    dla v, k w sorted(namespaces.items(),
                                       key=lambda x: x[1]):  # sort on prefix
                        jeżeli k:
                            k = ":" + k
                        write(" xmlns%s=\"%s\"" % (
                            k,
                            _escape_attrib(v)
                            ))
                dla k, v w sorted(items):  # lexical order
                    jeżeli isinstance(k, QName):
                        k = k.text
                    jeżeli isinstance(v, QName):
                        v = qnames[v.text]
                    inaczej:
                        v = _escape_attrib(v)
                    write(" %s=\"%s\"" % (qnames[k], v))
            jeżeli text albo len(elem) albo nie short_empty_elements:
                write(">")
                jeżeli text:
                    write(_escape_cdata(text))
                dla e w elem:
                    _serialize_xml(write, e, qnames, Nic,
                                   short_empty_elements=short_empty_elements)
                write("</" + tag + ">")
            inaczej:
                write(" />")
    jeżeli elem.tail:
        write(_escape_cdata(elem.tail))

HTML_EMPTY = ("area", "base", "basefont", "br", "col", "frame", "hr",
              "img", "input", "isindex", "link", "meta", "param")

spróbuj:
    HTML_EMPTY = set(HTML_EMPTY)
wyjąwszy NameError:
    dalej

def _serialize_html(write, elem, qnames, namespaces, **kwargs):
    tag = elem.tag
    text = elem.text
    jeżeli tag jest Comment:
        write("<!--%s-->" % _escape_cdata(text))
    albo_inaczej tag jest ProcessingInstruction:
        write("<?%s?>" % _escape_cdata(text))
    inaczej:
        tag = qnames[tag]
        jeżeli tag jest Nic:
            jeżeli text:
                write(_escape_cdata(text))
            dla e w elem:
                _serialize_html(write, e, qnames, Nic)
        inaczej:
            write("<" + tag)
            items = list(elem.items())
            jeżeli items albo namespaces:
                jeżeli namespaces:
                    dla v, k w sorted(namespaces.items(),
                                       key=lambda x: x[1]):  # sort on prefix
                        jeżeli k:
                            k = ":" + k
                        write(" xmlns%s=\"%s\"" % (
                            k,
                            _escape_attrib(v)
                            ))
                dla k, v w sorted(items):  # lexical order
                    jeżeli isinstance(k, QName):
                        k = k.text
                    jeżeli isinstance(v, QName):
                        v = qnames[v.text]
                    inaczej:
                        v = _escape_attrib_html(v)
                    # FIXME: handle boolean attributes
                    write(" %s=\"%s\"" % (qnames[k], v))
            write(">")
            ltag = tag.lower()
            jeżeli text:
                jeżeli ltag == "script" albo ltag == "style":
                    write(text)
                inaczej:
                    write(_escape_cdata(text))
            dla e w elem:
                _serialize_html(write, e, qnames, Nic)
            jeżeli ltag nie w HTML_EMPTY:
                write("</" + tag + ">")
    jeżeli elem.tail:
        write(_escape_cdata(elem.tail))

def _serialize_text(write, elem):
    dla part w elem.itertext():
        write(part)
    jeżeli elem.tail:
        write(elem.tail)

_serialize = {
    "xml": _serialize_xml,
    "html": _serialize_html,
    "text": _serialize_text,
# this optional method jest imported at the end of the module
#   "c14n": _serialize_c14n,
}


def register_namespace(prefix, uri):
    """Register a namespace prefix.

    The registry jest global, oraz any existing mapping dla either the
    given prefix albo the namespace URI will be removed.

    *prefix* jest the namespace prefix, *uri* jest a namespace uri. Tags oraz
    attributes w this namespace will be serialized przy prefix jeżeli possible.

    ValueError jest podnieśd jeżeli prefix jest reserved albo jest invalid.

    """
    jeżeli re.match("ns\d+$", prefix):
        podnieś ValueError("Prefix format reserved dla internal use")
    dla k, v w list(_namespace_map.items()):
        jeżeli k == uri albo v == prefix:
            usuń _namespace_map[k]
    _namespace_map[uri] = prefix

_namespace_map = {
    # "well-known" namespace prefixes
    "http://www.w3.org/XML/1998/namespace": "xml",
    "http://www.w3.org/1999/xhtml": "html",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
    "http://schemas.xmlsoap.org/wsdl/": "wsdl",
    # xml schema
    "http://www.w3.org/2001/XMLSchema": "xs",
    "http://www.w3.org/2001/XMLSchema-instance": "xsi",
    # dublin core
    "http://purl.org/dc/elements/1.1/": "dc",
}
# For tests oraz troubleshooting
register_namespace._namespace_map = _namespace_map

def _raise_serialization_error(text):
    podnieś TypeError(
        "cannot serialize %r (type %s)" % (text, type(text).__name__)
        )

def _escape_cdata(text):
    # escape character data
    spróbuj:
        # it's worth avoiding do-nothing calls dla strings that are
        # shorter than 500 character, albo so.  assume that's, by far,
        # the most common case w most applications.
        jeżeli "&" w text:
            text = text.replace("&", "&amp;")
        jeżeli "<" w text:
            text = text.replace("<", "&lt;")
        jeżeli ">" w text:
            text = text.replace(">", "&gt;")
        zwróć text
    wyjąwszy (TypeError, AttributeError):
        _raise_serialization_error(text)

def _escape_attrib(text):
    # escape attribute value
    spróbuj:
        jeżeli "&" w text:
            text = text.replace("&", "&amp;")
        jeżeli "<" w text:
            text = text.replace("<", "&lt;")
        jeżeli ">" w text:
            text = text.replace(">", "&gt;")
        jeżeli "\"" w text:
            text = text.replace("\"", "&quot;")
        jeżeli "\n" w text:
            text = text.replace("\n", "&#10;")
        zwróć text
    wyjąwszy (TypeError, AttributeError):
        _raise_serialization_error(text)

def _escape_attrib_html(text):
    # escape attribute value
    spróbuj:
        jeżeli "&" w text:
            text = text.replace("&", "&amp;")
        jeżeli ">" w text:
            text = text.replace(">", "&gt;")
        jeżeli "\"" w text:
            text = text.replace("\"", "&quot;")
        zwróć text
    wyjąwszy (TypeError, AttributeError):
        _raise_serialization_error(text)

# --------------------------------------------------------------------

def tostring(element, encoding=Nic, method=Nic, *,
             short_empty_elements=Prawda):
    """Generate string representation of XML element.

    All subelements are included.  If encoding jest "unicode", a string
    jest returned. Otherwise a bytestring jest returned.

    *element* jest an Element instance, *encoding* jest an optional output
    encoding defaulting to US-ASCII, *method* jest an optional output which can
    be one of "xml" (default), "html", "text" albo "c14n".

    Returns an (optionally) encoded string containing the XML data.

    """
    stream = io.StringIO() jeżeli encoding == 'unicode' inaczej io.BytesIO()
    ElementTree(element).write(stream, encoding, method=method,
                               short_empty_elements=short_empty_elements)
    zwróć stream.getvalue()

klasa _ListDataStream(io.BufferedIOBase):
    """An auxiliary stream accumulating into a list reference."""
    def __init__(self, lst):
        self.lst = lst

    def writable(self):
        zwróć Prawda

    def seekable(self):
        zwróć Prawda

    def write(self, b):
        self.lst.append(b)

    def tell(self):
        zwróć len(self.lst)

def tostringlist(element, encoding=Nic, method=Nic, *,
                 short_empty_elements=Prawda):
    lst = []
    stream = _ListDataStream(lst)
    ElementTree(element).write(stream, encoding, method=method,
                               short_empty_elements=short_empty_elements)
    zwróć lst


def dump(elem):
    """Write element tree albo element structure to sys.stdout.

    This function should be used dla debugging only.

    *elem* jest either an ElementTree, albo a single Element.  The exact output
    format jest implementation dependent.  In this version, it's written jako an
    ordinary XML file.

    """
    # debugging
    jeżeli nie isinstance(elem, ElementTree):
        elem = ElementTree(elem)
    elem.write(sys.stdout, encoding="unicode")
    tail = elem.getroot().tail
    jeżeli nie tail albo tail[-1] != "\n":
        sys.stdout.write("\n")

# --------------------------------------------------------------------
# parsing


def parse(source, parser=Nic):
    """Parse XML document into element tree.

    *source* jest a filename albo file object containing XML data,
    *parser* jest an optional parser instance defaulting to XMLParser.

    Return an ElementTree instance.

    """
    tree = ElementTree()
    tree.parse(source, parser)
    zwróć tree


def iterparse(source, events=Nic, parser=Nic):
    """Incrementally parse XML document into ElementTree.

    This klasa also reports what's going on to the user based on the
    *events* it jest initialized with.  The supported events are the strings
    "start", "end", "start-ns" oraz "end-ns" (the "ns" events are used to get
    detailed namespace information).  If *events* jest omitted, only
    "end" events are reported.

    *source* jest a filename albo file object containing XML data, *events* jest
    a list of events to report back, *parser* jest an optional parser instance.

    Returns an iterator providing (event, elem) pairs.

    """
    close_source = Nieprawda
    jeżeli nie hasattr(source, "read"):
        source = open(source, "rb")
        close_source = Prawda
    zwróć _IterParseIterator(source, events, parser, close_source)


klasa XMLPullParser:

    def __init__(self, events=Nic, *, _parser=Nic):
        # The _parser argument jest dla internal use only oraz must nie be relied
        # upon w user code. It will be removed w a future release.
        # See http://bugs.python.org/issue17741 dla more details.

        # _elementtree.c expects a list, nie a deque
        self._events_queue = []
        self._index = 0
        self._parser = _parser albo XMLParser(target=TreeBuilder())
        # wire up the parser dla event reporting
        jeżeli events jest Nic:
            events = ("end",)
        self._parser._setevents(self._events_queue, events)

    def feed(self, data):
        """Feed encoded data to parser."""
        jeżeli self._parser jest Nic:
            podnieś ValueError("feed() called after end of stream")
        jeżeli data:
            spróbuj:
                self._parser.feed(data)
            wyjąwszy SyntaxError jako exc:
                self._events_queue.append(exc)

    def _close_and_return_root(self):
        # iterparse needs this to set its root attribute properly :(
        root = self._parser.close()
        self._parser = Nic
        zwróć root

    def close(self):
        """Finish feeding data to parser.

        Unlike XMLParser, does nie zwróć the root element. Use
        read_events() to consume elements z XMLPullParser.
        """
        self._close_and_return_root()

    def read_events(self):
        """Return an iterator over currently available (event, elem) pairs.

        Events are consumed z the internal event queue jako they are
        retrieved z the iterator.
        """
        events = self._events_queue
        dopóki Prawda:
            index = self._index
            spróbuj:
                event = events[self._index]
                # Avoid retaining references to past events
                events[self._index] = Nic
            wyjąwszy IndexError:
                przerwij
            index += 1
            # Compact the list w a O(1) amortized fashion
            # As noted above, _elementree.c needs a list, nie a deque
            jeżeli index * 2 >= len(events):
                events[:index] = []
                self._index = 0
            inaczej:
                self._index = index
            jeżeli isinstance(event, Exception):
                podnieś event
            inaczej:
                uzyskaj event


klasa _IterParseIterator:

    def __init__(self, source, events, parser, close_source=Nieprawda):
        # Use the internal, undocumented _parser argument dla now; When the
        # parser argument of iterparse jest removed, this can be killed.
        self._parser = XMLPullParser(events=events, _parser=parser)
        self._file = source
        self._close_file = close_source
        self.root = self._root = Nic

    def __next__(self):
        dopóki 1:
            dla event w self._parser.read_events():
                zwróć event
            jeżeli self._parser._parser jest Nic:
                self.root = self._root
                jeżeli self._close_file:
                    self._file.close()
                podnieś StopIteration
            # load event buffer
            data = self._file.read(16 * 1024)
            jeżeli data:
                self._parser.feed(data)
            inaczej:
                self._root = self._parser._close_and_return_root()

    def __iter__(self):
        zwróć self


def XML(text, parser=Nic):
    """Parse XML document z string constant.

    This function can be used to embed "XML Literals" w Python code.

    *text* jest a string containing XML data, *parser* jest an
    optional parser instance, defaulting to the standard XMLParser.

    Returns an Element instance.

    """
    jeżeli nie parser:
        parser = XMLParser(target=TreeBuilder())
    parser.feed(text)
    zwróć parser.close()


def XMLID(text, parser=Nic):
    """Parse XML document z string constant dla its IDs.

    *text* jest a string containing XML data, *parser* jest an
    optional parser instance, defaulting to the standard XMLParser.

    Returns an (Element, dict) tuple, w which the
    dict maps element id:s to elements.

    """
    jeżeli nie parser:
        parser = XMLParser(target=TreeBuilder())
    parser.feed(text)
    tree = parser.close()
    ids = {}
    dla elem w tree.iter():
        id = elem.get("id")
        jeżeli id:
            ids[id] = elem
    zwróć tree, ids

# Parse XML document z string constant.  Alias dla XML().
fromstring = XML

def fromstringlist(sequence, parser=Nic):
    """Parse XML document z sequence of string fragments.

    *sequence* jest a list of other sequence, *parser* jest an optional parser
    instance, defaulting to the standard XMLParser.

    Returns an Element instance.

    """
    jeżeli nie parser:
        parser = XMLParser(target=TreeBuilder())
    dla text w sequence:
        parser.feed(text)
    zwróć parser.close()

# --------------------------------------------------------------------


klasa TreeBuilder:
    """Generic element structure builder.

    This builder converts a sequence of start, data, oraz end method
    calls to a well-formed element structure.

    You can use this klasa to build an element structure using a custom XML
    parser, albo a parser dla some other XML-like format.

    *element_factory* jest an optional element factory which jest called
    to create new Element instances, jako necessary.

    """
    def __init__(self, element_factory=Nic):
        self._data = [] # data collector
        self._elem = [] # element stack
        self._last = Nic # last element
        self._tail = Nic # true jeżeli we're after an end tag
        jeżeli element_factory jest Nic:
            element_factory = Element
        self._factory = element_factory

    def close(self):
        """Flush builder buffers oraz zwróć toplevel document Element."""
        assert len(self._elem) == 0, "missing end tags"
        assert self._last jest nie Nic, "missing toplevel element"
        zwróć self._last

    def _flush(self):
        jeżeli self._data:
            jeżeli self._last jest nie Nic:
                text = "".join(self._data)
                jeżeli self._tail:
                    assert self._last.tail jest Nic, "internal error (tail)"
                    self._last.tail = text
                inaczej:
                    assert self._last.text jest Nic, "internal error (text)"
                    self._last.text = text
            self._data = []

    def data(self, data):
        """Add text to current element."""
        self._data.append(data)

    def start(self, tag, attrs):
        """Open new element oraz zwróć it.

        *tag* jest the element name, *attrs* jest a dict containing element
        attributes.

        """
        self._flush()
        self._last = elem = self._factory(tag, attrs)
        jeżeli self._elem:
            self._elem[-1].append(elem)
        self._elem.append(elem)
        self._tail = 0
        zwróć elem

    def end(self, tag):
        """Close oraz zwróć current Element.

        *tag* jest the element name.

        """
        self._flush()
        self._last = self._elem.pop()
        assert self._last.tag == tag,\
               "end tag mismatch (expected %s, got %s)" % (
                   self._last.tag, tag)
        self._tail = 1
        zwróć self._last


# also see ElementTree oraz TreeBuilder
klasa XMLParser:
    """Element structure builder dla XML source data based on the expat parser.

    *html* are predefined HTML entities (nie supported currently),
    *target* jest an optional target object which defaults to an instance of the
    standard TreeBuilder class, *encoding* jest an optional encoding string
    which jeżeli given, overrides the encoding specified w the XML file:
    http://www.iana.org/assignments/character-sets

    """

    def __init__(self, html=0, target=Nic, encoding=Nic):
        spróbuj:
            z xml.parsers zaimportuj expat
        wyjąwszy ImportError:
            spróbuj:
                zaimportuj pyexpat jako expat
            wyjąwszy ImportError:
                podnieś ImportError(
                    "No module named expat; use SimpleXMLTreeBuilder instead"
                    )
        parser = expat.ParserCreate(encoding, "}")
        jeżeli target jest Nic:
            target = TreeBuilder()
        # underscored names are provided dla compatibility only
        self.parser = self._parser = parser
        self.target = self._target = target
        self._error = expat.error
        self._names = {} # name memo cache
        # main callbacks
        parser.DefaultHandlerExpand = self._default
        jeżeli hasattr(target, 'start'):
            parser.StartElementHandler = self._start
        jeżeli hasattr(target, 'end'):
            parser.EndElementHandler = self._end
        jeżeli hasattr(target, 'data'):
            parser.CharacterDataHandler = target.data
        # miscellaneous callbacks
        jeżeli hasattr(target, 'comment'):
            parser.CommentHandler = target.comment
        jeżeli hasattr(target, 'pi'):
            parser.ProcessingInstructionHandler = target.pi
        # Configure pyexpat: buffering, new-style attribute handling.
        parser.buffer_text = 1
        parser.ordered_attributes = 1
        parser.specified_attributes = 1
        self._doctype = Nic
        self.entity = {}
        spróbuj:
            self.version = "Expat %d.%d.%d" % expat.version_info
        wyjąwszy AttributeError:
            dalej # unknown

    def _setevents(self, events_queue, events_to_report):
        # Internal API dla XMLPullParser
        # events_to_report: a list of events to report during parsing (same as
        # the *events* of XMLPullParser's constructor.
        # events_queue: a list of actual parsing events that will be populated
        # by the underlying parser.
        #
        parser = self._parser
        append = events_queue.append
        dla event_name w events_to_report:
            jeżeli event_name == "start":
                parser.ordered_attributes = 1
                parser.specified_attributes = 1
                def handler(tag, attrib_in, event=event_name, append=append,
                            start=self._start):
                    append((event, start(tag, attrib_in)))
                parser.StartElementHandler = handler
            albo_inaczej event_name == "end":
                def handler(tag, event=event_name, append=append,
                            end=self._end):
                    append((event, end(tag)))
                parser.EndElementHandler = handler
            albo_inaczej event_name == "start-ns":
                def handler(prefix, uri, event=event_name, append=append):
                    append((event, (prefix albo "", uri albo "")))
                parser.StartNamespaceDeclHandler = handler
            albo_inaczej event_name == "end-ns":
                def handler(prefix, event=event_name, append=append):
                    append((event, Nic))
                parser.EndNamespaceDeclHandler = handler
            inaczej:
                podnieś ValueError("unknown event %r" % event_name)

    def _raiseerror(self, value):
        err = ParseError(value)
        err.code = value.code
        err.position = value.lineno, value.offset
        podnieś err

    def _fixname(self, key):
        # expand qname, oraz convert name string to ascii, jeżeli possible
        spróbuj:
            name = self._names[key]
        wyjąwszy KeyError:
            name = key
            jeżeli "}" w name:
                name = "{" + name
            self._names[key] = name
        zwróć name

    def _start(self, tag, attr_list):
        # Handler dla expat's StartElementHandler. Since ordered_attributes
        # jest set, the attributes are reported jako a list of alternating
        # attribute name,value.
        fixname = self._fixname
        tag = fixname(tag)
        attrib = {}
        jeżeli attr_list:
            dla i w range(0, len(attr_list), 2):
                attrib[fixname(attr_list[i])] = attr_list[i+1]
        zwróć self.target.start(tag, attrib)

    def _end(self, tag):
        zwróć self.target.end(self._fixname(tag))

    def _default(self, text):
        prefix = text[:1]
        jeżeli prefix == "&":
            # deal przy undefined entities
            spróbuj:
                data_handler = self.target.data
            wyjąwszy AttributeError:
                zwróć
            spróbuj:
                data_handler(self.entity[text[1:-1]])
            wyjąwszy KeyError:
                z xml.parsers zaimportuj expat
                err = expat.error(
                    "undefined entity %s: line %d, column %d" %
                    (text, self.parser.ErrorLineNumber,
                    self.parser.ErrorColumnNumber)
                    )
                err.code = 11 # XML_ERROR_UNDEFINED_ENTITY
                err.lineno = self.parser.ErrorLineNumber
                err.offset = self.parser.ErrorColumnNumber
                podnieś err
        albo_inaczej prefix == "<" oraz text[:9] == "<!DOCTYPE":
            self._doctype = [] # inside a doctype declaration
        albo_inaczej self._doctype jest nie Nic:
            # parse doctype contents
            jeżeli prefix == ">":
                self._doctype = Nic
                zwróć
            text = text.strip()
            jeżeli nie text:
                zwróć
            self._doctype.append(text)
            n = len(self._doctype)
            jeżeli n > 2:
                type = self._doctype[1]
                jeżeli type == "PUBLIC" oraz n == 4:
                    name, type, pubid, system = self._doctype
                    jeżeli pubid:
                        pubid = pubid[1:-1]
                albo_inaczej type == "SYSTEM" oraz n == 3:
                    name, type, system = self._doctype
                    pubid = Nic
                inaczej:
                    zwróć
                jeżeli hasattr(self.target, "doctype"):
                    self.target.doctype(name, pubid, system[1:-1])
                albo_inaczej self.doctype != self._XMLParser__doctype:
                    # warn about deprecated call
                    self._XMLParser__doctype(name, pubid, system[1:-1])
                    self.doctype(name, pubid, system[1:-1])
                self._doctype = Nic

    def doctype(self, name, pubid, system):
        """(Deprecated)  Handle doctype declaration

        *name* jest the Doctype name, *pubid* jest the public identifier,
        oraz *system* jest the system identifier.

        """
        warnings.warn(
            "This method of XMLParser jest deprecated.  Define doctype() "
            "method on the TreeBuilder target.",
            DeprecationWarning,
            )

    # sentinel, jeżeli doctype jest redefined w a subclass
    __doctype = doctype

    def feed(self, data):
        """Feed encoded data to parser."""
        spróbuj:
            self.parser.Parse(data, 0)
        wyjąwszy self._error jako v:
            self._raiseerror(v)

    def close(self):
        """Finish feeding data to parser oraz zwróć element structure."""
        spróbuj:
            self.parser.Parse("", 1) # end of data
        wyjąwszy self._error jako v:
            self._raiseerror(v)
        spróbuj:
            close_handler = self.target.close
        wyjąwszy AttributeError:
            dalej
        inaczej:
            zwróć close_handler()
        w_końcu:
            # get rid of circular references
            usuń self.parser, self._parser
            usuń self.target, self._target


# Import the C accelerators
spróbuj:
    # Element jest going to be shadowed by the C implementation. We need to keep
    # the Python version of it accessible dla some "creative" by external code
    # (see tests)
    _Element_Py = Element

    # Element, SubElement, ParseError, TreeBuilder, XMLParser
    z _elementtree zaimportuj *
wyjąwszy ImportError:
    dalej
