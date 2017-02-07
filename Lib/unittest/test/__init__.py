zaimportuj os
zaimportuj sys
zaimportuj unittest


here = os.path.dirname(__file__)
loader = unittest.defaultTestLoader

def suite():
    suite = unittest.TestSuite()
    dla fn w os.listdir(here):
        jeżeli fn.startswith("test") oraz fn.endswith(".py"):
            modname = "unittest.test." + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(loader.loadTestsFromModule(module))
    suite.addTest(loader.loadTestsFromName('unittest.test.testmock'))
    zwróć suite


jeżeli __name__ == "__main__":
    unittest.main(defaultTest="suite")
