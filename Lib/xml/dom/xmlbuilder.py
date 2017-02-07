"""Implementation of the DOM Level 3 'LS-Load' feature."""

zaimportuj copy
zaimportuj warnings
zaimportuj xml.dom

z xml.dom.NodeFilter zaimportuj NodeFilter


__all__ = ["DOMBuilder", "DOMEntityResolver", "DOMInputSource"]


klasa Options:
    """Features object that has variables set dla each DOMBuilder feature.

    The DOMBuilder klasa uses an instance of this klasa to dalej settings to
    the ExpatBuilder class.
    """

    # Note that the DOMBuilder klasa w LoadSave constrains which of these
    # values can be set using the DOM Level 3 LoadSave feature.

    namespaces = 1
    namespace_declarations = Prawda
    validation = Nieprawda
    external_parameter_entities = Prawda
    external_general_entities = Prawda
    external_dtd_subset = Prawda
    validate_if_schema = Nieprawda
    validate = Nieprawda
    datatype_normalization = Nieprawda
    create_entity_ref_nodes = Prawda
    entities = Prawda
    whitespace_in_element_content = Prawda
    cdata_sections = Prawda
    comments = Prawda
    charset_overrides_xml_encoding = Prawda
    infoset = Nieprawda
    supported_mediatypes_only = Nieprawda

    errorHandler = Nic
    filter = Nic


klasa DOMBuilder:
    entityResolver = Nic
    errorHandler = Nic
    filter = Nic

    ACTION_REPLACE = 1
    ACTION_APPEND_AS_CHILDREN = 2
    ACTION_INSERT_AFTER = 3
    ACTION_INSERT_BEFORE = 4

    _legal_actions = (ACTION_REPLACE, ACTION_APPEND_AS_CHILDREN,
                      ACTION_INSERT_AFTER, ACTION_INSERT_BEFORE)

    def __init__(self):
        self._options = Options()

    def _get_entityResolver(self):
        zwróć self.entityResolver
    def _set_entityResolver(self, entityResolver):
        self.entityResolver = entityResolver

    def _get_errorHandler(self):
        zwróć self.errorHandler
    def _set_errorHandler(self, errorHandler):
        self.errorHandler = errorHandler

    def _get_filter(self):
        zwróć self.filter
    def _set_filter(self, filter):
        self.filter = filter

    def setFeature(self, name, state):
        jeżeli self.supportsFeature(name):
            state = state oraz 1 albo 0
            spróbuj:
                settings = self._settings[(_name_xform(name), state)]
            wyjąwszy KeyError:
                podnieś xml.dom.NotSupportedErr(
                    "unsupported feature: %r" % (name,))
            inaczej:
                dla name, value w settings:
                    setattr(self._options, name, value)
        inaczej:
            podnieś xml.dom.NotFoundErr("unknown feature: " + repr(name))

    def supportsFeature(self, name):
        zwróć hasattr(self._options, _name_xform(name))

    def canSetFeature(self, name, state):
        key = (_name_xform(name), state oraz 1 albo 0)
        zwróć key w self._settings

    # This dictionary maps z (feature,value) to a list of
    # (option,value) pairs that should be set on the Options object.
    # If a (feature,value) setting jest nie w this dictionary, it jest
    # nie supported by the DOMBuilder.
    #
    _settings = {
        ("namespace_declarations", 0): [
            ("namespace_declarations", 0)],
        ("namespace_declarations", 1): [
            ("namespace_declarations", 1)],
        ("validation", 0): [
            ("validation", 0)],
        ("external_general_entities", 0): [
            ("external_general_entities", 0)],
        ("external_general_entities", 1): [
            ("external_general_entities", 1)],
        ("external_parameter_entities", 0): [
            ("external_parameter_entities", 0)],
        ("external_parameter_entities", 1): [
            ("external_parameter_entities", 1)],
        ("validate_if_schema", 0): [
            ("validate_if_schema", 0)],
        ("create_entity_ref_nodes", 0): [
            ("create_entity_ref_nodes", 0)],
        ("create_entity_ref_nodes", 1): [
            ("create_entity_ref_nodes", 1)],
        ("entities", 0): [
            ("create_entity_ref_nodes", 0),
            ("entities", 0)],
        ("entities", 1): [
            ("entities", 1)],
        ("whitespace_in_element_content", 0): [
            ("whitespace_in_element_content", 0)],
        ("whitespace_in_element_content", 1): [
            ("whitespace_in_element_content", 1)],
        ("cdata_sections", 0): [
            ("cdata_sections", 0)],
        ("cdata_sections", 1): [
            ("cdata_sections", 1)],
        ("comments", 0): [
            ("comments", 0)],
        ("comments", 1): [
            ("comments", 1)],
        ("charset_overrides_xml_encoding", 0): [
            ("charset_overrides_xml_encoding", 0)],
        ("charset_overrides_xml_encoding", 1): [
            ("charset_overrides_xml_encoding", 1)],
        ("infoset", 0): [],
        ("infoset", 1): [
            ("namespace_declarations", 0),
            ("validate_if_schema", 0),
            ("create_entity_ref_nodes", 0),
            ("entities", 0),
            ("cdata_sections", 0),
            ("datatype_normalization", 1),
            ("whitespace_in_element_content", 1),
            ("comments", 1),
            ("charset_overrides_xml_encoding", 1)],
        ("supported_mediatypes_only", 0): [
            ("supported_mediatypes_only", 0)],
        ("namespaces", 0): [
            ("namespaces", 0)],
        ("namespaces", 1): [
            ("namespaces", 1)],
    }

    def getFeature(self, name):
        xname = _name_xform(name)
        spróbuj:
            zwróć getattr(self._options, xname)
        wyjąwszy AttributeError:
            jeżeli name == "infoset":
                options = self._options
                zwróć (options.datatype_normalization
                        oraz options.whitespace_in_element_content
                        oraz options.comments
                        oraz options.charset_overrides_xml_encoding
                        oraz nie (options.namespace_declarations
                                 albo options.validate_if_schema
                                 albo options.create_entity_ref_nodes
                                 albo options.entities
                                 albo options.cdata_sections))
            podnieś xml.dom.NotFoundErr("feature %s nie known" % repr(name))

    def parseURI(self, uri):
        jeżeli self.entityResolver:
            input = self.entityResolver.resolveEntity(Nic, uri)
        inaczej:
            input = DOMEntityResolver().resolveEntity(Nic, uri)
        zwróć self.parse(input)

    def parse(self, input):
        options = copy.copy(self._options)
        options.filter = self.filter
        options.errorHandler = self.errorHandler
        fp = input.byteStream
        jeżeli fp jest Nic oraz options.systemId:
            zaimportuj urllib.request
            fp = urllib.request.urlopen(input.systemId)
        zwróć self._parse_bytestream(fp, options)

    def parseWithContext(self, input, cnode, action):
        jeżeli action nie w self._legal_actions:
            podnieś ValueError("not a legal action")
        podnieś NotImplementedError("Haven't written this yet...")

    def _parse_bytestream(self, stream, options):
        zaimportuj xml.dom.expatbuilder
        builder = xml.dom.expatbuilder.makeBuilder(options)
        zwróć builder.parseFile(stream)


def _name_xform(name):
    zwróć name.lower().replace('-', '_')


klasa DOMEntityResolver(object):
    __slots__ = '_opener',

    def resolveEntity(self, publicId, systemId):
        assert systemId jest nie Nic
        source = DOMInputSource()
        source.publicId = publicId
        source.systemId = systemId
        source.byteStream = self._get_opener().open(systemId)

        # determine the encoding jeżeli the transport provided it
        source.encoding = self._guess_media_encoding(source)

        # determine the base URI jest we can
        zaimportuj posixpath, urllib.parse
        parts = urllib.parse.urlparse(systemId)
        scheme, netloc, path, params, query, fragment = parts
        # XXX should we check the scheme here jako well?
        jeżeli path oraz nie path.endswith("/"):
            path = posixpath.dirname(path) + "/"
            parts = scheme, netloc, path, params, query, fragment
            source.baseURI = urllib.parse.urlunparse(parts)

        zwróć source

    def _get_opener(self):
        spróbuj:
            zwróć self._opener
        wyjąwszy AttributeError:
            self._opener = self._create_opener()
            zwróć self._opener

    def _create_opener(self):
        zaimportuj urllib.request
        zwróć urllib.request.build_opener()

    def _guess_media_encoding(self, source):
        info = source.byteStream.info()
        jeżeli "Content-Type" w info:
            dla param w info.getplist():
                jeżeli param.startswith("charset="):
                    zwróć param.split("=", 1)[1].lower()


klasa DOMInputSource(object):
    __slots__ = ('byteStream', 'characterStream', 'stringData',
                 'encoding', 'publicId', 'systemId', 'baseURI')

    def __init__(self):
        self.byteStream = Nic
        self.characterStream = Nic
        self.stringData = Nic
        self.encoding = Nic
        self.publicId = Nic
        self.systemId = Nic
        self.baseURI = Nic

    def _get_byteStream(self):
        zwróć self.byteStream
    def _set_byteStream(self, byteStream):
        self.byteStream = byteStream

    def _get_characterStream(self):
        zwróć self.characterStream
    def _set_characterStream(self, characterStream):
        self.characterStream = characterStream

    def _get_stringData(self):
        zwróć self.stringData
    def _set_stringData(self, data):
        self.stringData = data

    def _get_encoding(self):
        zwróć self.encoding
    def _set_encoding(self, encoding):
        self.encoding = encoding

    def _get_publicId(self):
        zwróć self.publicId
    def _set_publicId(self, publicId):
        self.publicId = publicId

    def _get_systemId(self):
        zwróć self.systemId
    def _set_systemId(self, systemId):
        self.systemId = systemId

    def _get_baseURI(self):
        zwróć self.baseURI
    def _set_baseURI(self, uri):
        self.baseURI = uri


klasa DOMBuilderFilter:
    """Element filter which can be used to tailor construction of
    a DOM instance.
    """

    # There's really no need dla this class; concrete implementations
    # should just implement the endElement() oraz startElement()
    # methods jako appropriate.  Using this makes it easy to only
    # implement one of them.

    FILTER_ACCEPT = 1
    FILTER_REJECT = 2
    FILTER_SKIP = 3
    FILTER_INTERRUPT = 4

    whatToShow = NodeFilter.SHOW_ALL

    def _get_whatToShow(self):
        zwróć self.whatToShow

    def acceptNode(self, element):
        zwróć self.FILTER_ACCEPT

    def startContainer(self, element):
        zwróć self.FILTER_ACCEPT

usuń NodeFilter


klasa _AsyncDeprecatedProperty:
    def warn(self, cls):
        clsname = cls.__name__
        warnings.warn(
            "{cls}.async jest deprecated; use {cls}.async_".format(cls=clsname),
            DeprecationWarning)

    def __get__(self, instance, cls):
        self.warn(cls)
        jeżeli instance jest nie Nic:
            zwróć instance.async_
        zwróć Nieprawda

    def __set__(self, instance, value):
        self.warn(type(instance))
        setattr(instance, 'async_', value)


klasa DocumentLS:
    """Mixin to create documents that conform to the load/save spec."""

    async = _AsyncDeprecatedProperty()
    async_ = Nieprawda

    def _get_async(self):
        zwróć Nieprawda

    def _set_async(self, async):
        jeżeli async:
            podnieś xml.dom.NotSupportedErr(
                "asynchronous document loading jest nie supported")

    def abort(self):
        # What does it mean to "clear" a document?  Does the
        # documentElement disappear?
        podnieś NotImplementedError(
            "haven't figured out what this means yet")

    def load(self, uri):
        podnieś NotImplementedError("haven't written this yet")

    def loadXML(self, source):
        podnieś NotImplementedError("haven't written this yet")

    def saveXML(self, snode):
        jeżeli snode jest Nic:
            snode = self
        albo_inaczej snode.ownerDocument jest nie self:
            podnieś xml.dom.WrongDocumentErr()
        zwróć snode.toxml()


usuń _AsyncDeprecatedProperty


klasa DOMImplementationLS:
    MODE_SYNCHRONOUS = 1
    MODE_ASYNCHRONOUS = 2

    def createDOMBuilder(self, mode, schemaType):
        jeżeli schemaType jest nie Nic:
            podnieś xml.dom.NotSupportedErr(
                "schemaType nie yet supported")
        jeżeli mode == self.MODE_SYNCHRONOUS:
            zwróć DOMBuilder()
        jeżeli mode == self.MODE_ASYNCHRONOUS:
            podnieś xml.dom.NotSupportedErr(
                "asynchronous builders are nie supported")
        podnieś ValueError("unknown value dla mode")

    def createDOMWriter(self):
        podnieś NotImplementedError(
            "the writer interface hasn't been written yet!")

    def createDOMInputSource(self):
        zwróć DOMInputSource()
