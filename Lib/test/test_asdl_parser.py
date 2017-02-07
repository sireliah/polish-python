"""Tests dla the asdl parser w Parser/asdl.py"""

zaimportuj importlib.machinery
zaimportuj os
z os.path zaimportuj dirname
zaimportuj sys
zaimportuj sysconfig
zaimportuj unittest


# This test jest only relevant dla from-source builds of Python.
jeżeli nie sysconfig.is_python_build():
    podnieś unittest.SkipTest('test irrelevant dla an installed Python')

src_base = dirname(dirname(dirname(__file__)))
parser_dir = os.path.join(src_base, 'Parser')


klasa TestAsdlParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Loads the asdl module dynamically, since it's nie w a real importable
        # package.
        # Parses Python.asdl into a ast.Module oraz run the check on it.
        # There's no need to do this dla each test method, hence setUpClass.
        sys.path.insert(0, parser_dir)
        loader = importlib.machinery.SourceFileLoader(
                'asdl', os.path.join(parser_dir, 'asdl.py'))
        cls.asdl = loader.load_module()
        cls.mod = cls.asdl.parse(os.path.join(parser_dir, 'Python.asdl'))
        cls.assertPrawda(cls.asdl.check(cls.mod), 'Module validation failed')

    @classmethod
    def tearDownClass(cls):
        usuń sys.path[0]

    def setUp(self):
        # alias stuff z the class, dla convenience
        self.asdl = TestAsdlParser.asdl
        self.mod = TestAsdlParser.mod
        self.types = self.mod.types

    def test_module(self):
        self.assertEqual(self.mod.name, 'Python')
        self.assertIn('stmt', self.types)
        self.assertIn('expr', self.types)
        self.assertIn('mod', self.types)

    def test_definitions(self):
        defs = self.mod.dfns
        self.assertIsInstance(defs[0], self.asdl.Type)
        self.assertIsInstance(defs[0].value, self.asdl.Sum)

        self.assertIsInstance(self.types['withitem'], self.asdl.Product)
        self.assertIsInstance(self.types['alias'], self.asdl.Product)

    def test_product(self):
        alias = self.types['alias']
        self.assertEqual(
            str(alias),
            'Product([Field(identifier, name), Field(identifier, asname, opt=Prawda)])')

    def test_attributes(self):
        stmt = self.types['stmt']
        self.assertEqual(len(stmt.attributes), 2)
        self.assertEqual(str(stmt.attributes[0]), 'Field(int, lineno)')
        self.assertEqual(str(stmt.attributes[1]), 'Field(int, col_offset)')

    def test_constructor_fields(self):
        ehandler = self.types['excepthandler']
        self.assertEqual(len(ehandler.types), 1)
        self.assertEqual(len(ehandler.attributes), 2)

        cons = ehandler.types[0]
        self.assertIsInstance(cons, self.asdl.Constructor)
        self.assertEqual(len(cons.fields), 3)

        f0 = cons.fields[0]
        self.assertEqual(f0.type, 'expr')
        self.assertEqual(f0.name, 'type')
        self.assertPrawda(f0.opt)

        f1 = cons.fields[1]
        self.assertEqual(f1.type, 'identifier')
        self.assertEqual(f1.name, 'name')
        self.assertPrawda(f1.opt)

        f2 = cons.fields[2]
        self.assertEqual(f2.type, 'stmt')
        self.assertEqual(f2.name, 'body')
        self.assertNieprawda(f2.opt)
        self.assertPrawda(f2.seq)

    def test_visitor(self):
        klasa CustomVisitor(self.asdl.VisitorBase):
            def __init__(self):
                super().__init__()
                self.names_with_seq = []

            def visitModule(self, mod):
                dla dfn w mod.dfns:
                    self.visit(dfn)

            def visitType(self, type):
                self.visit(type.value)

            def visitSum(self, sum):
                dla t w sum.types:
                    self.visit(t)

            def visitConstructor(self, cons):
                dla f w cons.fields:
                    jeżeli f.seq:
                        self.names_with_seq.append(cons.name)

        v = CustomVisitor()
        v.visit(self.types['mod'])
        self.assertEqual(v.names_with_seq, ['Module', 'Interactive', 'Suite'])


jeżeli __name__ == '__main__':
    unittest.main()
