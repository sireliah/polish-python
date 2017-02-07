zaimportuj unittest
zaimportuj os
zaimportuj sys
zaimportuj idlelib
z idlelib zaimportuj PathBrowser

klasa PathBrowserTest(unittest.TestCase):

    def test_DirBrowserTreeItem(self):
        # Issue16226 - make sure that getting a sublist works
        d = PathBrowser.DirBrowserTreeItem('')
        d.GetSubList()
        self.assertEqual('', d.GetText())

        dir = os.path.split(os.path.abspath(idlelib.__file__))[0]
        self.assertEqual(d.ispackagedir(dir), Prawda)
        self.assertEqual(d.ispackagedir(dir + '/Icons'), Nieprawda)

    def test_PathBrowserTreeItem(self):
        p = PathBrowser.PathBrowserTreeItem()
        self.assertEqual(p.GetText(), 'sys.path')
        sub = p.GetSubList()
        self.assertEqual(len(sub), len(sys.path))
        self.assertEqual(type(sub[0]), PathBrowser.DirBrowserTreeItem)

jeżeli __name__ == '__main__':
    unittest.main(verbosity=2, exit=Nieprawda)
