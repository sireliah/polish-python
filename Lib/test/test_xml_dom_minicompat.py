# Tests dla xml.dom.minicompat

zaimportuj pickle
zaimportuj unittest

zaimportuj xml.dom
z xml.dom.minicompat zaimportuj *


klasa EmptyNodeListTestCase(unittest.TestCase):
    """Tests dla the EmptyNodeList class."""

    def test_emptynodelist_item(self):
        # Test item access on an EmptyNodeList.
        node_list = EmptyNodeList()

        self.assertIsNic(node_list.item(0))
        self.assertIsNic(node_list.item(-1)) # invalid item

        przy self.assertRaises(IndexError):
            node_list[0]
        przy self.assertRaises(IndexError):
            node_list[-1]

    def test_emptynodelist_length(self):
        node_list = EmptyNodeList()
        # Reading
        self.assertEqual(node_list.length, 0)
        # Writing
        przy self.assertRaises(xml.dom.NoModificationAllowedErr):
            node_list.length = 111

    def test_emptynodelist___add__(self):
        node_list = EmptyNodeList() + NodeList()
        self.assertEqual(node_list, NodeList())

    def test_emptynodelist___radd__(self):
        node_list = [1,2] + EmptyNodeList()
        self.assertEqual(node_list, [1,2])


klasa NodeListTestCase(unittest.TestCase):
    """Tests dla the NodeList class."""

    def test_nodelist_item(self):
        # Test items access on a NodeList.
        # First, use an empty NodeList.
        node_list = NodeList()

        self.assertIsNic(node_list.item(0))
        self.assertIsNic(node_list.item(-1))

        przy self.assertRaises(IndexError):
            node_list[0]
        przy self.assertRaises(IndexError):
            node_list[-1]

        # Now, use a NodeList przy items.
        node_list.append(111)
        node_list.append(999)

        self.assertEqual(node_list.item(0), 111)
        self.assertIsNic(node_list.item(-1)) # invalid item

        self.assertEqual(node_list[0], 111)
        self.assertEqual(node_list[-1], 999)

    def test_nodelist_length(self):
        node_list = NodeList([1, 2])
        # Reading
        self.assertEqual(node_list.length, 2)
        # Writing
        przy self.assertRaises(xml.dom.NoModificationAllowedErr):
            node_list.length = 111

    def test_nodelist___add__(self):
        node_list = NodeList([3, 4]) + [1, 2]
        self.assertEqual(node_list, NodeList([3, 4, 1, 2]))

    def test_nodelist___radd__(self):
        node_list = [1, 2] + NodeList([3, 4])
        self.assertEqual(node_list, NodeList([1, 2, 3, 4]))

    def test_nodelist_pickle_roundtrip(self):
        # Test pickling oraz unpickling of a NodeList.

        dla proto w range(pickle.HIGHEST_PROTOCOL + 1):
            # Empty NodeList.
            node_list = NodeList()
            pickled = pickle.dumps(node_list, proto)
            unpickled = pickle.loads(pickled)
            self.assertEqual(unpickled, node_list)

            # Non-empty NodeList.
            node_list.append(1)
            node_list.append(2)
            pickled = pickle.dumps(node_list, proto)
            unpickled = pickle.loads(pickled)
            self.assertEqual(unpickled, node_list)

jeżeli __name__ == '__main__':
    unittest.main()
