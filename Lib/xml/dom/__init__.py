"""W3C Document Object Mousuń implementation dla Python.

The Python mapping of the Document Object Mousuń jest documented w the
Python Library Reference w the section on the xml.dom package.

This package contains the following modules:

minidom -- A simple implementation of the Level 1 DOM przy namespace
           support added (based on the Level 2 specification) oraz other
           minor Level 2 functionality.

pulldom -- DOM builder supporting on-demand tree-building dla selected
           subtrees of the document.

"""


klasa Node:
    """Class giving the NodeType constants."""
    __slots__ = ()

    # DOM implementations may use this jako a base klasa dla their own
    # Node implementations.  If they don't, the constants defined here
    # should still be used jako the canonical definitions jako they match
    # the values given w the W3C recommendation.  Client code can
    # safely refer to these values w all tests of Node.nodeType
    # values.

    ELEMENT_NODE                = 1
    ATTRIBUTE_NODE              = 2
    TEXT_NODE                   = 3
    CDATA_SECTION_NODE          = 4
    ENTITY_REFERENCE_NODE       = 5
    ENTITY_NODE                 = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE                = 8
    DOCUMENT_NODE               = 9
    DOCUMENT_TYPE_NODE          = 10
    DOCUMENT_FRAGMENT_NODE      = 11
    NOTATION_NODE               = 12


#ExceptionCode
INDEX_SIZE_ERR                 = 1
DOMSTRING_SIZE_ERR             = 2
HIERARCHY_REQUEST_ERR          = 3
WRONG_DOCUMENT_ERR             = 4
INVALID_CHARACTER_ERR          = 5
NO_DATA_ALLOWED_ERR            = 6
NO_MODIFICATION_ALLOWED_ERR    = 7
NOT_FOUND_ERR                  = 8
NOT_SUPPORTED_ERR              = 9
INUSE_ATTRIBUTE_ERR            = 10
INVALID_STATE_ERR              = 11
SYNTAX_ERR                     = 12
INVALID_MODIFICATION_ERR       = 13
NAMESPACE_ERR                  = 14
INVALID_ACCESS_ERR             = 15
VALIDATION_ERR                 = 16


klasa DOMException(Exception):
    """Abstract base klasa dla DOM exceptions.
    Exceptions przy specific codes are specializations of this class."""

    def __init__(self, *args, **kw):
        jeżeli self.__class__ jest DOMException:
            podnieś RuntimeError(
                "DOMException should nie be instantiated directly")
        Exception.__init__(self, *args, **kw)

    def _get_code(self):
        zwróć self.code


klasa IndexSizeErr(DOMException):
    code = INDEX_SIZE_ERR

klasa DomstringSizeErr(DOMException):
    code = DOMSTRING_SIZE_ERR

klasa HierarchyRequestErr(DOMException):
    code = HIERARCHY_REQUEST_ERR

klasa WrongDocumentErr(DOMException):
    code = WRONG_DOCUMENT_ERR

klasa InvalidCharacterErr(DOMException):
    code = INVALID_CHARACTER_ERR

klasa NoDataAllowedErr(DOMException):
    code = NO_DATA_ALLOWED_ERR

klasa NoModificationAllowedErr(DOMException):
    code = NO_MODIFICATION_ALLOWED_ERR

klasa NotFoundErr(DOMException):
    code = NOT_FOUND_ERR

klasa NotSupportedErr(DOMException):
    code = NOT_SUPPORTED_ERR

klasa InuseAttributeErr(DOMException):
    code = INUSE_ATTRIBUTE_ERR

klasa InvalidStateErr(DOMException):
    code = INVALID_STATE_ERR

klasa SyntaxErr(DOMException):
    code = SYNTAX_ERR

klasa InvalidModificationErr(DOMException):
    code = INVALID_MODIFICATION_ERR

klasa NamespaceErr(DOMException):
    code = NAMESPACE_ERR

klasa InvalidAccessErr(DOMException):
    code = INVALID_ACCESS_ERR

klasa ValidationErr(DOMException):
    code = VALIDATION_ERR

klasa UserDataHandler:
    """Class giving the operation constants dla UserDataHandler.handle()."""

    # Based on DOM Level 3 (WD 9 April 2002)

    NODE_CLONED   = 1
    NODE_IMPORTED = 2
    NODE_DELETED  = 3
    NODE_RENAMED  = 4

XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
XMLNS_NAMESPACE = "http://www.w3.org/2000/xmlns/"
XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
EMPTY_NAMESPACE = Nic
EMPTY_PREFIX = Nic

z .domreg zaimportuj getDOMImplementation, registerDOMImplementation
