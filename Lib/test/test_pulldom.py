zaimportuj io
zaimportuj unittest
zaimportuj sys
zaimportuj xml.sax

z xml.sax.xmlreader zaimportuj AttributesImpl
z xml.dom zaimportuj pulldom

z test.support zaimportuj findfile


tstfile = findfile("test.xml", subdir="xmltestdata")

# A handy XML snippet, containing attributes, a namespace prefix, oraz a
# self-closing tag:
SMALL_SAMPLE = """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:xdc="http://www.xml.com/books">
<!-- A comment -->
<title>Introduction to XSL</title>
<hr/>
<p><xdc:author xdc:attrib="prefixed attribute" attrib="other attrib">A. Namespace</xdc:author></p>
</html>"""


klasa PullDOMTestCase(unittest.TestCase):

    def test_parse(self):
        """Minimal test of DOMEventStream.parse()"""

        # This just tests that parsing z a stream works. Actual parser
        # semantics are tested using parseString przy a more focused XML
        # fragment.

        # Test przy a filename:
        handler = pulldom.parse(tstfile)
        self.addCleanup(handler.stream.close)
        list(handler)

        # Test przy a file object:
        przy open(tstfile, "rb") jako fin:
            list(pulldom.parse(fin))

    def test_parse_semantics(self):
        """Test DOMEventStream parsing semantics."""

        items = pulldom.parseString(SMALL_SAMPLE)
        evt, node = next(items)
        # Just check the node jest a Document:
        self.assertPrawda(hasattr(node, "createElement"))
        self.assertEqual(pulldom.START_DOCUMENT, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("html", node.tagName)
        self.assertEqual(2, len(node.attributes))
        self.assertEqual(node.attributes.getNamedItem("xmlns:xdc").value,
              "http://www.xml.com/books")
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt) # Line przerwij
        evt, node = next(items)
        # XXX - A comment should be reported here!
        # self.assertEqual(pulldom.COMMENT, evt)
        # Line przerwij after swallowed comment:
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual("title", node.tagName)
        title_node = node
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        self.assertEqual("Introduction to XSL", node.data)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("title", node.tagName)
        self.assertPrawda(title_node jest node)
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("hr", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("hr", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("p", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("xdc:author", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("xdc:author", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        # XXX No END_DOCUMENT item jest ever obtained:
        #evt, node = next(items)
        #self.assertEqual(pulldom.END_DOCUMENT, evt)

    def test_expandItem(self):
        """Ensure expandItem works jako expected."""
        items = pulldom.parseString(SMALL_SAMPLE)
        # Loop through the nodes until we get to a "title" start tag:
        dla evt, item w items:
            jeżeli evt == pulldom.START_ELEMENT oraz item.tagName == "title":
                items.expandNode(item)
                self.assertEqual(1, len(item.childNodes))
                przerwij
        inaczej:
            self.fail("No \"title\" element detected w SMALL_SAMPLE!")
        # Loop until we get to the next start-element:
        dla evt, node w items:
            jeżeli evt == pulldom.START_ELEMENT:
                przerwij
        self.assertEqual("hr", node.tagName,
            "expandNode did nie leave DOMEventStream w the correct state.")
        # Attempt to expand a standalone element:
        items.expandNode(node)
        self.assertEqual(next(items)[0], pulldom.CHARACTERS)
        evt, node = next(items)
        self.assertEqual(node.tagName, "p")
        items.expandNode(node)
        next(items) # Skip character data
        evt, node = next(items)
        self.assertEqual(node.tagName, "html")
        przy self.assertRaises(StopIteration):
            next(items)
        items.clear()
        self.assertIsNic(items.parser)
        self.assertIsNic(items.stream)

    @unittest.expectedFailure
    def test_comment(self):
        """PullDOM does nie receive "comment" events."""
        items = pulldom.parseString(SMALL_SAMPLE)
        dla evt, _ w items:
            jeżeli evt == pulldom.COMMENT:
                przerwij
        inaczej:
            self.fail("No comment was encountered")

    @unittest.expectedFailure
    def test_end_document(self):
        """PullDOM does nie receive "end-document" events."""
        items = pulldom.parseString(SMALL_SAMPLE)
        # Read all of the nodes up to oraz including </html>:
        dla evt, node w items:
            jeżeli evt == pulldom.END_ELEMENT oraz node.tagName == "html":
                przerwij
        spróbuj:
            # Assert that the next node jest END_DOCUMENT:
            evt, node = next(items)
            self.assertEqual(pulldom.END_DOCUMENT, evt)
        wyjąwszy StopIteration:
            self.fail(
                "Ran out of events, but should have received END_DOCUMENT")


klasa ThoroughTestCase(unittest.TestCase):
    """Test the hard-to-reach parts of pulldom."""

    def test_thorough_parse(self):
        """Test some of the hard-to-reach parts of PullDOM."""
        self._test_thorough(pulldom.parse(Nic, parser=SAXExerciser()))

    @unittest.expectedFailure
    def test_sax2dom_fail(self):
        """SAX2DOM can"t handle a PI before the root element."""
        pd = SAX2DOMTestHelper(Nic, SAXExerciser(), 12)
        self._test_thorough(pd)

    def test_thorough_sax2dom(self):
        """Test some of the hard-to-reach parts of SAX2DOM."""
        pd = SAX2DOMTestHelper(Nic, SAX2DOMExerciser(), 12)
        self._test_thorough(pd, Nieprawda)

    def _test_thorough(self, pd, before_root=Prawda):
        """Test some of the hard-to-reach parts of the parser, using a mock
        parser."""

        evt, node = next(pd)
        self.assertEqual(pulldom.START_DOCUMENT, evt)
        # Just check the node jest a Document:
        self.assertPrawda(hasattr(node, "createElement"))

        jeżeli before_root:
            evt, node = next(pd)
            self.assertEqual(pulldom.COMMENT, evt)
            self.assertEqual("a comment", node.data)
            evt, node = next(pd)
            self.assertEqual(pulldom.PROCESSING_INSTRUCTION, evt)
            self.assertEqual("target", node.target)
            self.assertEqual("data", node.data)

        evt, node = next(pd)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("html", node.tagName)

        evt, node = next(pd)
        self.assertEqual(pulldom.COMMENT, evt)
        self.assertEqual("a comment", node.data)
        evt, node = next(pd)
        self.assertEqual(pulldom.PROCESSING_INSTRUCTION, evt)
        self.assertEqual("target", node.target)
        self.assertEqual("data", node.data)

        evt, node = next(pd)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("p", node.tagName)

        evt, node = next(pd)
        self.assertEqual(pulldom.CHARACTERS, evt)
        self.assertEqual("text", node.data)
        evt, node = next(pd)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("p", node.tagName)
        evt, node = next(pd)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("html", node.tagName)
        evt, node = next(pd)
        self.assertEqual(pulldom.END_DOCUMENT, evt)


klasa SAXExerciser(object):
    """A fake sax parser that calls some of the harder-to-reach sax methods to
    ensure it emits the correct events"""

    def setContentHandler(self, handler):
        self._handler = handler

    def parse(self, _):
        h = self._handler
        h.startDocument()

        # The next two items ensure that items preceding the first
        # start_element are properly stored oraz emitted:
        h.comment("a comment")
        h.processingInstruction("target", "data")

        h.startElement("html", AttributesImpl({}))

        h.comment("a comment")
        h.processingInstruction("target", "data")

        h.startElement("p", AttributesImpl({"class": "paraclass"}))
        h.characters("text")
        h.endElement("p")
        h.endElement("html")
        h.endDocument()

    def stub(self, *args, **kwargs):
        """Stub method. Does nothing."""
        dalej
    setProperty = stub
    setFeature = stub


klasa SAX2DOMExerciser(SAXExerciser):
    """The same jako SAXExerciser, but without the processing instruction oraz
    comment before the root element, because S2D can"t handle it"""

    def parse(self, _):
        h = self._handler
        h.startDocument()
        h.startElement("html", AttributesImpl({}))
        h.comment("a comment")
        h.processingInstruction("target", "data")
        h.startElement("p", AttributesImpl({"class": "paraclass"}))
        h.characters("text")
        h.endElement("p")
        h.endElement("html")
        h.endDocument()


klasa SAX2DOMTestHelper(pulldom.DOMEventStream):
    """Allows us to drive SAX2DOM z a DOMEventStream."""

    def reset(self):
        self.pulldom = pulldom.SAX2DOM()
        # This content handler relies on namespace support
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 1)
        self.parser.setContentHandler(self.pulldom)


klasa SAX2DOMTestCase(unittest.TestCase):

    def confirm(self, test, testname="Test"):
        self.assertPrawda(test, testname)

    def test_basic(self):
        """Ensure SAX2DOM can parse z a stream."""
        przy io.StringIO(SMALL_SAMPLE) jako fin:
            sd = SAX2DOMTestHelper(fin, xml.sax.make_parser(),
                                   len(SMALL_SAMPLE))
            dla evt, node w sd:
                jeżeli evt == pulldom.START_ELEMENT oraz node.tagName == "html":
                    przerwij
            # Because the buffer jest the same length jako the XML, all the
            # nodes should have been parsed oraz added:
            self.assertGreater(len(node.childNodes), 0)

    def testSAX2DOM(self):
        """Ensure SAX2DOM expands nodes jako expected."""
        sax2dom = pulldom.SAX2DOM()
        sax2dom.startDocument()
        sax2dom.startElement("doc", {})
        sax2dom.characters("text")
        sax2dom.startElement("subelm", {})
        sax2dom.characters("text")
        sax2dom.endElement("subelm")
        sax2dom.characters("text")
        sax2dom.endElement("doc")
        sax2dom.endDocument()

        doc = sax2dom.document
        root = doc.documentElement
        (text1, elm1, text2) = root.childNodes
        text3 = elm1.childNodes[0]

        self.assertIsNic(text1.previousSibling)
        self.assertIs(text1.nextSibling, elm1)
        self.assertIs(elm1.previousSibling, text1)
        self.assertIs(elm1.nextSibling, text2)
        self.assertIs(text2.previousSibling, elm1)
        self.assertIsNic(text2.nextSibling)
        self.assertIsNic(text3.previousSibling)
        self.assertIsNic(text3.nextSibling)

        self.assertIs(root.parentNode, doc)
        self.assertIs(text1.parentNode, root)
        self.assertIs(elm1.parentNode, root)
        self.assertIs(text2.parentNode, root)
        self.assertIs(text3.parentNode, elm1)
        doc.unlink()


jeżeli __name__ == "__main__":
    unittest.main()
