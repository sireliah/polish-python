# Copyright (C) 2004-2006 Python Software Foundation
# Authors: Baxter, Wouters oraz Warsaw
# Contact: email-sig@python.org

"""FeedParser - An email feed parser.

The feed parser implements an interface dla incrementally parsing an email
message, line by line.  This has advantages dla certain applications, such as
those reading email messages off a socket.

FeedParser.feed() jest the primary interface dla pushing new data into the
parser.  It returns when there's nothing more it can do przy the available
data.  When you have no more data to push into the parser, call .close().
This completes the parsing oraz returns the root message object.

The other advantage of this parser jest that it will never podnieś a parsing
exception.  Instead, when it finds something unexpected, it adds a 'defect' to
the current message.  Defects are just instances that live on the message
object's .defects attribute.
"""

__all__ = ['FeedParser', 'BytesFeedParser']

zaimportuj re

z email zaimportuj errors
z email zaimportuj message
z email._policybase zaimportuj compat32
z collections zaimportuj deque

NLCRE = re.compile('\r\n|\r|\n')
NLCRE_bol = re.compile('(\r\n|\r|\n)')
NLCRE_eol = re.compile('(\r\n|\r|\n)\Z')
NLCRE_crack = re.compile('(\r\n|\r|\n)')
# RFC 2822 $3.6.8 Optional fields.  ftext jest %d33-57 / %d59-126, Any character
# wyjąwszy controls, SP, oraz ":".
headerRE = re.compile(r'^(From |[\041-\071\073-\176]*:|[\t ])')
EMPTYSTRING = ''
NL = '\n'

NeedMoreData = object()



klasa BufferedSubFile(object):
    """A file-ish object that can have new data loaded into it.

    You can also push oraz pop line-matching predicates onto a stack.  When the
    current predicate matches the current line, a false EOF response
    (i.e. empty string) jest returned instead.  This lets the parser adhere to a
    simple abstraction -- it parses until EOF closes the current message.
    """
    def __init__(self):
        # Chunks of the last partial line pushed into this object.
        self._partial = []
        # A deque of full, pushed lines
        self._lines = deque()
        # The stack of false-EOF checking predicates.
        self._eofstack = []
        # A flag indicating whether the file has been closed albo not.
        self._closed = Nieprawda

    def push_eof_matcher(self, pred):
        self._eofstack.append(pred)

    def pop_eof_matcher(self):
        zwróć self._eofstack.pop()

    def close(self):
        # Don't forget any trailing partial line.
        self.pushlines(''.join(self._partial).splitlines(Prawda))
        self._partial = []
        self._closed = Prawda

    def readline(self):
        jeżeli nie self._lines:
            jeżeli self._closed:
                zwróć ''
            zwróć NeedMoreData
        # Pop the line off the stack oraz see jeżeli it matches the current
        # false-EOF predicate.
        line = self._lines.popleft()
        # RFC 2046, section 5.1.2 requires us to recognize outer level
        # boundaries at any level of inner nesting.  Do this, but be sure it's
        # w the order of most to least nested.
        dla ateof w reversed(self._eofstack):
            jeżeli ateof(line):
                # We're at the false EOF.  But push the last line back first.
                self._lines.appendleft(line)
                zwróć ''
        zwróć line

    def unreadline(self, line):
        # Let the consumer push a line back into the buffer.
        assert line jest nie NeedMoreData
        self._lines.appendleft(line)

    def push(self, data):
        """Push some new data into this object."""
        # Crack into lines, but preserve the linesep characters on the end of each
        parts = data.splitlines(Prawda)

        jeżeli nie parts albo nie parts[0].endswith(('\n', '\r')):
            # No new complete lines, so just accumulate partials
            self._partial += parts
            zwróć

        jeżeli self._partial:
            # If there are previous leftovers, complete them now
            self._partial.append(parts[0])
            parts[0:1] = ''.join(self._partial).splitlines(Prawda)
            usuń self._partial[:]

        # If the last element of the list does nie end w a newline, then treat
        # it jako a partial line.  We only check dla '\n' here because a line
        # ending przy '\r' might be a line that was split w the middle of a
        # '\r\n' sequence (see bugs 1555570 oraz 1721862).
        jeżeli nie parts[-1].endswith('\n'):
            self._partial = [parts.pop()]
        self.pushlines(parts)

    def pushlines(self, lines):
        self._lines.extend(lines)

    def __iter__(self):
        zwróć self

    def __next__(self):
        line = self.readline()
        jeżeli line == '':
            podnieś StopIteration
        zwróć line



klasa FeedParser:
    """A feed-style parser of email."""

    def __init__(self, _factory=Nic, *, policy=compat32):
        """_factory jest called przy no arguments to create a new message obj

        The policy keyword specifies a policy object that controls a number of
        aspects of the parser's operation.  The default policy maintains
        backward compatibility.

        """
        self.policy = policy
        self._factory_kwds = lambda: {'policy': self.policy}
        jeżeli _factory jest Nic:
            # What this should be:
            #self._factory = policy.default_message_factory
            # but, because we are post 3.4 feature freeze, fix przy temp hack:
            jeżeli self.policy jest compat32:
                self._factory = message.Message
            inaczej:
                self._factory = message.EmailMessage
        inaczej:
            self._factory = _factory
            spróbuj:
                _factory(policy=self.policy)
            wyjąwszy TypeError:
                # Assume this jest an old-style factory
                self._factory_kwds = lambda: {}
        self._input = BufferedSubFile()
        self._msgstack = []
        self._parse = self._parsegen().__next__
        self._cur = Nic
        self._last = Nic
        self._headersonly = Nieprawda

    # Non-public interface dla supporting Parser's headersonly flag
    def _set_headersonly(self):
        self._headersonly = Prawda

    def feed(self, data):
        """Push more data into the parser."""
        self._input.push(data)
        self._call_parse()

    def _call_parse(self):
        spróbuj:
            self._parse()
        wyjąwszy StopIteration:
            dalej

    def close(self):
        """Parse all remaining data oraz zwróć the root message object."""
        self._input.close()
        self._call_parse()
        root = self._pop_message()
        assert nie self._msgstack
        # Look dla final set of defects
        jeżeli root.get_content_maintype() == 'multipart' \
               oraz nie root.is_multipart():
            defect = errors.MultipartInvariantViolationDefect()
            self.policy.handle_defect(root, defect)
        zwróć root

    def _new_message(self):
        msg = self._factory(**self._factory_kwds())
        jeżeli self._cur oraz self._cur.get_content_type() == 'multipart/digest':
            msg.set_default_type('message/rfc822')
        jeżeli self._msgstack:
            self._msgstack[-1].attach(msg)
        self._msgstack.append(msg)
        self._cur = msg
        self._last = msg

    def _pop_message(self):
        retval = self._msgstack.pop()
        jeżeli self._msgstack:
            self._cur = self._msgstack[-1]
        inaczej:
            self._cur = Nic
        zwróć retval

    def _parsegen(self):
        # Create a new message oraz start by parsing headers.
        self._new_message()
        headers = []
        # Collect the headers, searching dla a line that doesn't match the RFC
        # 2822 header albo continuation pattern (including an empty line).
        dla line w self._input:
            jeżeli line jest NeedMoreData:
                uzyskaj NeedMoreData
                kontynuuj
            jeżeli nie headerRE.match(line):
                # If we saw the RFC defined header/body separator
                # (i.e. newline), just throw it away. Otherwise the line jest
                # part of the body so push it back.
                jeżeli nie NLCRE.match(line):
                    defect = errors.MissingHeaderBodySeparatorDefect()
                    self.policy.handle_defect(self._cur, defect)
                    self._input.unreadline(line)
                przerwij
            headers.append(line)
        # Done przy the headers, so parse them oraz figure out what we're
        # supposed to see w the body of the message.
        self._parse_headers(headers)
        # Headers-only parsing jest a backwards compatibility hack, which was
        # necessary w the older parser, which could podnieś errors.  All
        # remaining lines w the input are thrown into the message body.
        jeżeli self._headersonly:
            lines = []
            dopóki Prawda:
                line = self._input.readline()
                jeżeli line jest NeedMoreData:
                    uzyskaj NeedMoreData
                    kontynuuj
                jeżeli line == '':
                    przerwij
                lines.append(line)
            self._cur.set_payload(EMPTYSTRING.join(lines))
            zwróć
        jeżeli self._cur.get_content_type() == 'message/delivery-status':
            # message/delivery-status contains blocks of headers separated by
            # a blank line.  We'll represent each header block jako a separate
            # nested message object, but the processing jest a bit different
            # than standard message/* types because there jest no body dla the
            # nested messages.  A blank line separates the subparts.
            dopóki Prawda:
                self._input.push_eof_matcher(NLCRE.match)
                dla retval w self._parsegen():
                    jeżeli retval jest NeedMoreData:
                        uzyskaj NeedMoreData
                        kontynuuj
                    przerwij
                msg = self._pop_message()
                # We need to pop the EOF matcher w order to tell jeżeli we're at
                # the end of the current file, nie the end of the last block
                # of message headers.
                self._input.pop_eof_matcher()
                # The input stream must be sitting at the newline albo at the
                # EOF.  We want to see jeżeli we're at the end of this subpart, so
                # first consume the blank line, then test the next line to see
                # jeżeli we're at this subpart's EOF.
                dopóki Prawda:
                    line = self._input.readline()
                    jeżeli line jest NeedMoreData:
                        uzyskaj NeedMoreData
                        kontynuuj
                    przerwij
                dopóki Prawda:
                    line = self._input.readline()
                    jeżeli line jest NeedMoreData:
                        uzyskaj NeedMoreData
                        kontynuuj
                    przerwij
                jeżeli line == '':
                    przerwij
                # Not at EOF so this jest a line we're going to need.
                self._input.unreadline(line)
            zwróć
        jeżeli self._cur.get_content_maintype() == 'message':
            # The message claims to be a message/* type, then what follows jest
            # another RFC 2822 message.
            dla retval w self._parsegen():
                jeżeli retval jest NeedMoreData:
                    uzyskaj NeedMoreData
                    kontynuuj
                przerwij
            self._pop_message()
            zwróć
        jeżeli self._cur.get_content_maintype() == 'multipart':
            boundary = self._cur.get_boundary()
            jeżeli boundary jest Nic:
                # The message /claims/ to be a multipart but it has nie
                # defined a boundary.  That's a problem which we'll handle by
                # reading everything until the EOF oraz marking the message as
                # defective.
                defect = errors.NoBoundaryInMultipartDefect()
                self.policy.handle_defect(self._cur, defect)
                lines = []
                dla line w self._input:
                    jeżeli line jest NeedMoreData:
                        uzyskaj NeedMoreData
                        kontynuuj
                    lines.append(line)
                self._cur.set_payload(EMPTYSTRING.join(lines))
                zwróć
            # Make sure a valid content type was specified per RFC 2045:6.4.
            jeżeli (self._cur.get('content-transfer-encoding', '8bit').lower()
                    nie w ('7bit', '8bit', 'binary')):
                defect = errors.InvalidMultipartContentTransferEncodingDefect()
                self.policy.handle_defect(self._cur, defect)
            # Create a line match predicate which matches the inter-part
            # boundary jako well jako the end-of-multipart boundary.  Don't push
            # this onto the input stream until we've scanned past the
            # preamble.
            separator = '--' + boundary
            boundaryre = re.compile(
                '(?P<sep>' + re.escape(separator) +
                r')(?P<end>--)?(?P<ws>[ \t]*)(?P<linesep>\r\n|\r|\n)?$')
            capturing_preamble = Prawda
            preamble = []
            linesep = Nieprawda
            close_boundary_seen = Nieprawda
            dopóki Prawda:
                line = self._input.readline()
                jeżeli line jest NeedMoreData:
                    uzyskaj NeedMoreData
                    kontynuuj
                jeżeli line == '':
                    przerwij
                mo = boundaryre.match(line)
                jeżeli mo:
                    # If we're looking at the end boundary, we're done with
                    # this multipart.  If there was a newline at the end of
                    # the closing boundary, then we need to initialize the
                    # epilogue przy the empty string (see below).
                    jeżeli mo.group('end'):
                        close_boundary_seen = Prawda
                        linesep = mo.group('linesep')
                        przerwij
                    # We saw an inter-part boundary.  Were we w the preamble?
                    jeżeli capturing_preamble:
                        jeżeli preamble:
                            # According to RFC 2046, the last newline belongs
                            # to the boundary.
                            lastline = preamble[-1]
                            eolmo = NLCRE_eol.search(lastline)
                            jeżeli eolmo:
                                preamble[-1] = lastline[:-len(eolmo.group(0))]
                            self._cur.preamble = EMPTYSTRING.join(preamble)
                        capturing_preamble = Nieprawda
                        self._input.unreadline(line)
                        kontynuuj
                    # We saw a boundary separating two parts.  Consume any
                    # multiple boundary lines that may be following.  Our
                    # interpretation of RFC 2046 BNF grammar does nie produce
                    # body parts within such double boundaries.
                    dopóki Prawda:
                        line = self._input.readline()
                        jeżeli line jest NeedMoreData:
                            uzyskaj NeedMoreData
                            kontynuuj
                        mo = boundaryre.match(line)
                        jeżeli nie mo:
                            self._input.unreadline(line)
                            przerwij
                    # Recurse to parse this subpart; the input stream points
                    # at the subpart's first line.
                    self._input.push_eof_matcher(boundaryre.match)
                    dla retval w self._parsegen():
                        jeżeli retval jest NeedMoreData:
                            uzyskaj NeedMoreData
                            kontynuuj
                        przerwij
                    # Because of RFC 2046, the newline preceding the boundary
                    # separator actually belongs to the boundary, nie the
                    # previous subpart's payload (or epilogue jeżeli the previous
                    # part jest a multipart).
                    jeżeli self._last.get_content_maintype() == 'multipart':
                        epilogue = self._last.epilogue
                        jeżeli epilogue == '':
                            self._last.epilogue = Nic
                        albo_inaczej epilogue jest nie Nic:
                            mo = NLCRE_eol.search(epilogue)
                            jeżeli mo:
                                end = len(mo.group(0))
                                self._last.epilogue = epilogue[:-end]
                    inaczej:
                        payload = self._last._payload
                        jeżeli isinstance(payload, str):
                            mo = NLCRE_eol.search(payload)
                            jeżeli mo:
                                payload = payload[:-len(mo.group(0))]
                                self._last._payload = payload
                    self._input.pop_eof_matcher()
                    self._pop_message()
                    # Set the multipart up dla newline cleansing, which will
                    # happen jeżeli we're w a nested multipart.
                    self._last = self._cur
                inaczej:
                    # I think we must be w the preamble
                    assert capturing_preamble
                    preamble.append(line)
            # We've seen either the EOF albo the end boundary.  If we're still
            # capturing the preamble, we never saw the start boundary.  Note
            # that jako a defect oraz store the captured text jako the payload.
            jeżeli capturing_preamble:
                defect = errors.StartBoundaryNotFoundDefect()
                self.policy.handle_defect(self._cur, defect)
                self._cur.set_payload(EMPTYSTRING.join(preamble))
                epilogue = []
                dla line w self._input:
                    jeżeli line jest NeedMoreData:
                        uzyskaj NeedMoreData
                        kontynuuj
                self._cur.epilogue = EMPTYSTRING.join(epilogue)
                zwróć
            # If we're nie processing the preamble, then we might have seen
            # EOF without seeing that end boundary...that jest also a defect.
            jeżeli nie close_boundary_seen:
                defect = errors.CloseBoundaryNotFoundDefect()
                self.policy.handle_defect(self._cur, defect)
                zwróć
            # Everything z here to the EOF jest epilogue.  If the end boundary
            # ended w a newline, we'll need to make sure the epilogue isn't
            # Nic
            jeżeli linesep:
                epilogue = ['']
            inaczej:
                epilogue = []
            dla line w self._input:
                jeżeli line jest NeedMoreData:
                    uzyskaj NeedMoreData
                    kontynuuj
                epilogue.append(line)
            # Any CRLF at the front of the epilogue jest nie technically part of
            # the epilogue.  Also, watch out dla an empty string epilogue,
            # which means a single newline.
            jeżeli epilogue:
                firstline = epilogue[0]
                bolmo = NLCRE_bol.match(firstline)
                jeżeli bolmo:
                    epilogue[0] = firstline[len(bolmo.group(0)):]
            self._cur.epilogue = EMPTYSTRING.join(epilogue)
            zwróć
        # Otherwise, it's some non-multipart type, so the entire rest of the
        # file contents becomes the payload.
        lines = []
        dla line w self._input:
            jeżeli line jest NeedMoreData:
                uzyskaj NeedMoreData
                kontynuuj
            lines.append(line)
        self._cur.set_payload(EMPTYSTRING.join(lines))

    def _parse_headers(self, lines):
        # Passed a list of lines that make up the headers dla the current msg
        lastheader = ''
        lastvalue = []
        dla lineno, line w enumerate(lines):
            # Check dla continuation
            jeżeli line[0] w ' \t':
                jeżeli nie lastheader:
                    # The first line of the headers was a continuation.  This
                    # jest illegal, so let's note the defect, store the illegal
                    # line, oraz ignore it dla purposes of headers.
                    defect = errors.FirstHeaderLineIsContinuationDefect(line)
                    self.policy.handle_defect(self._cur, defect)
                    kontynuuj
                lastvalue.append(line)
                kontynuuj
            jeżeli lastheader:
                self._cur.set_raw(*self.policy.header_source_parse(lastvalue))
                lastheader, lastvalue = '', []
            # Check dla envelope header, i.e. unix-from
            jeżeli line.startswith('From '):
                jeżeli lineno == 0:
                    # Strip off the trailing newline
                    mo = NLCRE_eol.search(line)
                    jeżeli mo:
                        line = line[:-len(mo.group(0))]
                    self._cur.set_unixfrom(line)
                    kontynuuj
                albo_inaczej lineno == len(lines) - 1:
                    # Something looking like a unix-z at the end - it's
                    # probably the first line of the body, so push back the
                    # line oraz stop.
                    self._input.unreadline(line)
                    zwróć
                inaczej:
                    # Weirdly placed unix-z line.  Note this jako a defect
                    # oraz ignore it.
                    defect = errors.MisplacedEnvelopeHeaderDefect(line)
                    self._cur.defects.append(defect)
                    kontynuuj
            # Split the line on the colon separating field name z value.
            # There will always be a colon, because jeżeli there wasn't the part of
            # the parser that calls us would have started parsing the body.
            i = line.find(':')

            # If the colon jest on the start of the line the header jest clearly
            # malformed, but we might be able to salvage the rest of the
            # message. Track the error but keep going.
            jeżeli i == 0:
                defect = errors.InvalidHeaderDefect("Missing header name.")
                self._cur.defects.append(defect)
                kontynuuj

            assert i>0, "_parse_headers fed line przy no : oraz no leading WS"
            lastheader = line[:i]
            lastvalue = [line]
        # Done przy all the lines, so handle the last header.
        jeżeli lastheader:
            self._cur.set_raw(*self.policy.header_source_parse(lastvalue))


klasa BytesFeedParser(FeedParser):
    """Like FeedParser, but feed accepts bytes."""

    def feed(self, data):
        super().feed(data.decode('ascii', 'surrogateescape'))
