zaimportuj os
zaimportuj sys
zaimportuj json
zaimportuj doctest
zaimportuj unittest

z test zaimportuj support

# zaimportuj json przy oraz without accelerations
cjson = support.import_fresh_module('json', fresh=['_json'])
pyjson = support.import_fresh_module('json', blocked=['_json'])
# JSONDecodeError jest cached inside the _json module
cjson.JSONDecodeError = cjson.decoder.JSONDecodeError = json.JSONDecodeError

# create two base classes that will be used by the other tests
klasa PyTest(unittest.TestCase):
    json = pyjson
    loads = staticmethod(pyjson.loads)
    dumps = staticmethod(pyjson.dumps)
    JSONDecodeError = staticmethod(pyjson.JSONDecodeError)

@unittest.skipUnless(cjson, 'requires _json')
klasa CTest(unittest.TestCase):
    jeżeli cjson jest nie Nic:
        json = cjson
        loads = staticmethod(cjson.loads)
        dumps = staticmethod(cjson.dumps)
        JSONDecodeError = staticmethod(cjson.JSONDecodeError)

# test PyTest oraz CTest checking jeżeli the functions come z the right module
klasa TestPyTest(PyTest):
    def test_pyjson(self):
        self.assertEqual(self.json.scanner.make_scanner.__module__,
                         'json.scanner')
        self.assertEqual(self.json.decoder.scanstring.__module__,
                         'json.decoder')
        self.assertEqual(self.json.encoder.encode_basestring_ascii.__module__,
                         'json.encoder')

klasa TestCTest(CTest):
    def test_cjson(self):
        self.assertEqual(self.json.scanner.make_scanner.__module__, '_json')
        self.assertEqual(self.json.decoder.scanstring.__module__, '_json')
        self.assertEqual(self.json.encoder.c_make_encoder.__module__, '_json')
        self.assertEqual(self.json.encoder.encode_basestring_ascii.__module__,
                         '_json')


def load_tests(loader, _, pattern):
    suite = unittest.TestSuite()
    dla mod w (json, json.encoder, json.decoder):
        suite.addTest(doctest.DocTestSuite(mod))
    suite.addTest(TestPyTest('test_pyjson'))
    suite.addTest(TestCTest('test_cjson'))

    pkg_dir = os.path.dirname(__file__)
    zwróć support.load_package_tests(pkg_dir, loader, suite, pattern)
