zaimportuj os
zaimportuj sys
zaimportuj unittest


here = os.path.dirname(__file__)
loader = unittest.defaultTestLoader

def load_tests(*args):
    suite = unittest.TestSuite()
    dla fn w os.listdir(here):
        jeżeli fn.startswith("test") oraz fn.endswith(".py"):
            modname = "unittest.test.testmock." + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(loader.loadTestsFromModule(module))
    zwróć suite
