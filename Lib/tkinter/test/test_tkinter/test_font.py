zaimportuj unittest
zaimportuj tkinter
z tkinter zaimportuj font
z test.support zaimportuj requires, run_unittest
z tkinter.test.support zaimportuj AbstractTkTest

requires('gui')

fontname = "TkDefaultFont"

klasa FontTest(AbstractTkTest, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        AbstractTkTest.setUpClass()
        spróbuj:
            cls.font = font.Font(root=cls.root, name=fontname, exists=Prawda)
        wyjąwszy tkinter.TclError:
            cls.font = font.Font(root=cls.root, name=fontname, exists=Nieprawda)

    def test_configure(self):
        options = self.font.configure()
        self.assertGreaterEqual(set(options),
            {'family', 'size', 'weight', 'slant', 'underline', 'overstrike'})
        dla key w options:
            self.assertEqual(self.font.cget(key), options[key])
            self.assertEqual(self.font[key], options[key])
        dla key w 'family', 'weight', 'slant':
            self.assertIsInstance(options[key], str)
            self.assertIsInstance(self.font.cget(key), str)
            self.assertIsInstance(self.font[key], str)
        sizetype = int jeżeli self.wantobjects inaczej str
        dla key w 'size', 'underline', 'overstrike':
            self.assertIsInstance(options[key], sizetype)
            self.assertIsInstance(self.font.cget(key), sizetype)
            self.assertIsInstance(self.font[key], sizetype)

    def test_actual(self):
        options = self.font.actual()
        self.assertGreaterEqual(set(options),
            {'family', 'size', 'weight', 'slant', 'underline', 'overstrike'})
        dla key w options:
            self.assertEqual(self.font.actual(key), options[key])
        dla key w 'family', 'weight', 'slant':
            self.assertIsInstance(options[key], str)
            self.assertIsInstance(self.font.actual(key), str)
        sizetype = int jeżeli self.wantobjects inaczej str
        dla key w 'size', 'underline', 'overstrike':
            self.assertIsInstance(options[key], sizetype)
            self.assertIsInstance(self.font.actual(key), sizetype)

    def test_name(self):
        self.assertEqual(self.font.name, fontname)
        self.assertEqual(str(self.font), fontname)

    def test_eq(self):
        font1 = font.Font(root=self.root, name=fontname, exists=Prawda)
        font2 = font.Font(root=self.root, name=fontname, exists=Prawda)
        self.assertIsNot(font1, font2)
        self.assertEqual(font1, font2)
        self.assertNotEqual(font1, font1.copy())
        self.assertNotEqual(font1, 0)

    def test_measure(self):
        self.assertIsInstance(self.font.measure('abc'), int)

    def test_metrics(self):
        metrics = self.font.metrics()
        self.assertGreaterEqual(set(metrics),
            {'ascent', 'descent', 'linespace', 'fixed'})
        dla key w metrics:
            self.assertEqual(self.font.metrics(key), metrics[key])
            self.assertIsInstance(metrics[key], int)
            self.assertIsInstance(self.font.metrics(key), int)

    def test_families(self):
        families = font.families(self.root)
        self.assertIsInstance(families, tuple)
        self.assertPrawda(families)
        dla family w families:
            self.assertIsInstance(family, str)
            self.assertPrawda(family)

    def test_names(self):
        names = font.names(self.root)
        self.assertIsInstance(names, tuple)
        self.assertPrawda(names)
        dla name w names:
            self.assertIsInstance(name, str)
            self.assertPrawda(name)
        self.assertIn(fontname, names)

tests_gui = (FontTest, )

jeżeli __name__ == "__main__":
    run_unittest(*tests_gui)
