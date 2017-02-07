# Copyright (C) 2001-2007 Python Software Foundation
# Author: Barry Warsaw, Thomas Wouters, Anthony Baxter
# Contact: email-sig@python.org

"""A parser of RFC 2822 oraz MIME email messages."""

__all__ = ['Parser', 'HeaderParser', 'BytesParser', 'BytesHeaderParser',
           'FeedParser', 'BytesFeedParser']

z io zaimportuj StringIO, TextIOWrapper

z email.feedparser zaimportuj FeedParser, BytesFeedParser
z email._policybase zaimportuj compat32



klasa Parser:
    def __init__(self, _class=Nic, *, policy=compat32):
        """Parser of RFC 2822 oraz MIME email messages.

        Creates an in-memory object tree representing the email message, which
        can then be manipulated oraz turned over to a Generator to zwróć the
        textual representation of the message.

        The string must be formatted jako a block of RFC 2822 headers oraz header
        continuation lines, optionally preceeded by a `Unix-from' header.  The
        header block jest terminated either by the end of the string albo by a
        blank line.

        _class jest the klasa to instantiate dla new message objects when they
        must be created.  This klasa must have a constructor that can take
        zero arguments.  Default jest Message.Message.

        The policy keyword specifies a policy object that controls a number of
        aspects of the parser's operation.  The default policy maintains
        backward compatibility.

        """
        self._class = _class
        self.policy = policy

    def parse(self, fp, headersonly=Nieprawda):
        """Create a message structure z the data w a file.

        Reads all the data z the file oraz returns the root of the message
        structure.  Optional headersonly jest a flag specifying whether to stop
        parsing after reading the headers albo not.  The default jest Nieprawda,
        meaning it parses the entire contents of the file.
        """
        feedparser = FeedParser(self._class, policy=self.policy)
        jeżeli headersonly:
            feedparser._set_headersonly()
        dopóki Prawda:
            data = fp.read(8192)
            jeżeli nie data:
                przerwij
            feedparser.feed(data)
        zwróć feedparser.close()

    def parsestr(self, text, headersonly=Nieprawda):
        """Create a message structure z a string.

        Returns the root of the message structure.  Optional headersonly jest a
        flag specifying whether to stop parsing after reading the headers albo
        not.  The default jest Nieprawda, meaning it parses the entire contents of
        the file.
        """
        zwróć self.parse(StringIO(text), headersonly=headersonly)



klasa HeaderParser(Parser):
    def parse(self, fp, headersonly=Prawda):
        zwróć Parser.parse(self, fp, Prawda)

    def parsestr(self, text, headersonly=Prawda):
        zwróć Parser.parsestr(self, text, Prawda)


klasa BytesParser:

    def __init__(self, *args, **kw):
        """Parser of binary RFC 2822 oraz MIME email messages.

        Creates an in-memory object tree representing the email message, which
        can then be manipulated oraz turned over to a Generator to zwróć the
        textual representation of the message.

        The input must be formatted jako a block of RFC 2822 headers oraz header
        continuation lines, optionally preceeded by a `Unix-from' header.  The
        header block jest terminated either by the end of the input albo by a
        blank line.

        _class jest the klasa to instantiate dla new message objects when they
        must be created.  This klasa must have a constructor that can take
        zero arguments.  Default jest Message.Message.
        """
        self.parser = Parser(*args, **kw)

    def parse(self, fp, headersonly=Nieprawda):
        """Create a message structure z the data w a binary file.

        Reads all the data z the file oraz returns the root of the message
        structure.  Optional headersonly jest a flag specifying whether to stop
        parsing after reading the headers albo not.  The default jest Nieprawda,
        meaning it parses the entire contents of the file.
        """
        fp = TextIOWrapper(fp, encoding='ascii', errors='surrogateescape')
        spróbuj:
            zwróć self.parser.parse(fp, headersonly)
        w_końcu:
            fp.detach()


    def parsebytes(self, text, headersonly=Nieprawda):
        """Create a message structure z a byte string.

        Returns the root of the message structure.  Optional headersonly jest a
        flag specifying whether to stop parsing after reading the headers albo
        not.  The default jest Nieprawda, meaning it parses the entire contents of
        the file.
        """
        text = text.decode('ASCII', errors='surrogateescape')
        zwróć self.parser.parsestr(text, headersonly)


klasa BytesHeaderParser(BytesParser):
    def parse(self, fp, headersonly=Prawda):
        zwróć BytesParser.parse(self, fp, headersonly=Prawda)

    def parsebytes(self, text, headersonly=Prawda):
        zwróć BytesParser.parsebytes(self, text, headersonly=Prawda)
