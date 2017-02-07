# xml.etree test dla cElementTree
zaimportuj sys, struct
z test zaimportuj support
z test.support zaimportuj import_fresh_module
zaimportuj types
zaimportuj unittest

cET = import_fresh_module('xml.etree.ElementTree',
                          fresh=['_elementtree'])
cET_alias = import_fresh_module('xml.etree.cElementTree',
                                fresh=['_elementtree', 'xml.etree'])


klasa MiscTests(unittest.TestCase):
    # Issue #8651.
    @support.bigmemtest(size=support._2G + 100, memuse=1, dry_run=Nieprawda)
    def test_length_overflow(self, size):
        data = b'x' * size
        parser = cET.XMLParser()
        spróbuj:
            self.assertRaises(OverflowError, parser.feed, data)
        w_końcu:
            data = Nic


@unittest.skipUnless(cET, 'requires _elementtree')
klasa TestAliasWorking(unittest.TestCase):
    # Test that the cET alias module jest alive
    def test_alias_working(self):
        e = cET_alias.Element('foo')
        self.assertEqual(e.tag, 'foo')


@unittest.skipUnless(cET, 'requires _elementtree')
@support.cpython_only
klasa TestAcceleratorImported(unittest.TestCase):
    # Test that the C accelerator was imported, jako expected
    def test_correct_import_cET(self):
        # SubElement jest a function so it retains _elementtree jako its module.
        self.assertEqual(cET.SubElement.__module__, '_elementtree')

    def test_correct_import_cET_alias(self):
        self.assertEqual(cET_alias.SubElement.__module__, '_elementtree')

    def test_parser_comes_from_C(self):
        # The type of methods defined w Python code jest types.FunctionType,
        # dopóki the type of methods defined inside _elementtree jest
        # <class 'wrapper_descriptor'>
        self.assertNotIsInstance(cET.Element.__init__, types.FunctionType)


@unittest.skipUnless(cET, 'requires _elementtree')
@support.cpython_only
klasa SizeofTest(unittest.TestCase):
    def setUp(self):
        self.elementsize = support.calcobjsize('5P')
        # extra
        self.extra = struct.calcsize('PnnP4P')

    check_sizeof = support.check_sizeof

    def test_element(self):
        e = cET.Element('a')
        self.check_sizeof(e, self.elementsize)

    def test_element_with_attrib(self):
        e = cET.Element('a', href='about:')
        self.check_sizeof(e, self.elementsize + self.extra)

    def test_element_with_children(self):
        e = cET.Element('a')
        dla i w range(5):
            cET.SubElement(e, 'span')
        # should have space dla 8 children now
        self.check_sizeof(e, self.elementsize + self.extra +
                             struct.calcsize('8P'))

def test_main():
    z test zaimportuj test_xml_etree, test_xml_etree_c

    # Run the tests specific to the C implementation
    support.run_unittest(
        MiscTests,
        TestAliasWorking,
        TestAcceleratorImported,
        SizeofTest,
        )

    # Run the same test suite jako the Python module
    test_xml_etree.test_main(module=cET)


jeżeli __name__ == '__main__':
    test_main()
