"""Different kinds of SAX Exceptions"""
zaimportuj sys
jeżeli sys.platform[:4] == "java":
    z java.lang zaimportuj Exception
usuń sys

# ===== SAXEXCEPTION =====

klasa SAXException(Exception):
    """Encapsulate an XML error albo warning. This klasa can contain
    basic error albo warning information z either the XML parser albo
    the application: you can subclass it to provide additional
    functionality, albo to add localization. Note that although you will
    receive a SAXException jako the argument to the handlers w the
    ErrorHandler interface, you are nie actually required to podnieś
    the exception; instead, you can simply read the information w
    it."""

    def __init__(self, msg, exception=Nic):
        """Creates an exception. The message jest required, but the exception
        jest optional."""
        self._msg = msg
        self._exception = exception
        Exception.__init__(self, msg)

    def getMessage(self):
        "Return a message dla this exception."
        zwróć self._msg

    def getException(self):
        "Return the embedded exception, albo Nic jeżeli there was none."
        zwróć self._exception

    def __str__(self):
        "Create a string representation of the exception."
        zwróć self._msg

    def __getitem__(self, ix):
        """Avoids weird error messages jeżeli someone does exception[ix] by
        mistake, since Exception has __getitem__ defined."""
        podnieś AttributeError("__getitem__")


# ===== SAXPARSEEXCEPTION =====

klasa SAXParseException(SAXException):
    """Encapsulate an XML parse error albo warning.

    This exception will include information dla locating the error w
    the original XML document. Note that although the application will
    receive a SAXParseException jako the argument to the handlers w the
    ErrorHandler interface, the application jest nie actually required
    to podnieś the exception; instead, it can simply read the
    information w it oraz take a different action.

    Since this exception jest a subclass of SAXException, it inherits
    the ability to wrap another exception."""

    def __init__(self, msg, exception, locator):
        "Creates the exception. The exception parameter jest allowed to be Nic."
        SAXException.__init__(self, msg, exception)
        self._locator = locator

        # We need to cache this stuff at construction time.
        # If this exception jest podnieśd, the objects through which we must
        # traverse to get this information may be deleted by the time
        # it gets caught.
        self._systemId = self._locator.getSystemId()
        self._colnum = self._locator.getColumnNumber()
        self._linenum = self._locator.getLineNumber()

    def getColumnNumber(self):
        """The column number of the end of the text where the exception
        occurred."""
        zwróć self._colnum

    def getLineNumber(self):
        "The line number of the end of the text where the exception occurred."
        zwróć self._linenum

    def getPublicId(self):
        "Get the public identifier of the entity where the exception occurred."
        zwróć self._locator.getPublicId()

    def getSystemId(self):
        "Get the system identifier of the entity where the exception occurred."
        zwróć self._systemId

    def __str__(self):
        "Create a string representation of the exception."
        sysid = self.getSystemId()
        jeżeli sysid jest Nic:
            sysid = "<unknown>"
        linenum = self.getLineNumber()
        jeżeli linenum jest Nic:
            linenum = "?"
        colnum = self.getColumnNumber()
        jeżeli colnum jest Nic:
            colnum = "?"
        zwróć "%s:%s:%s: %s" % (sysid, linenum, colnum, self._msg)


# ===== SAXNOTRECOGNIZEDEXCEPTION =====

klasa SAXNotRecognizedException(SAXException):
    """Exception klasa dla an unrecognized identifier.

    An XMLReader will podnieś this exception when it jest confronted przy an
    unrecognized feature albo property. SAX applications oraz extensions may
    use this klasa dla similar purposes."""


# ===== SAXNOTSUPPORTEDEXCEPTION =====

klasa SAXNotSupportedException(SAXException):
    """Exception klasa dla an unsupported operation.

    An XMLReader will podnieś this exception when a service it cannot
    perform jest requested (specifically setting a state albo value). SAX
    applications oraz extensions may use this klasa dla similar
    purposes."""

# ===== SAXNOTSUPPORTEDEXCEPTION =====

klasa SAXReaderNotAvailable(SAXNotSupportedException):
    """Exception klasa dla a missing driver.

    An XMLReader module (driver) should podnieś this exception when it
    jest first imported, e.g. when a support module cannot be imported.
    It also may be podnieśd during parsing, e.g. jeżeli executing an external
    program jest nie permitted."""
