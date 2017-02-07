zaimportuj collections.abc
zaimportuj errno
zaimportuj socket
zaimportuj sys
zaimportuj unittest
z test zaimportuj support

zaimportuj xmlrpc.client jako xmlrpclib

klasa PythonBuildersTest(unittest.TestCase):

    def test_python_builders(self):
        # Get the list of builders z the XMLRPC buildbot interface at
        # python.org.
        server = xmlrpclib.ServerProxy("http://buildbot.python.org/all/xmlrpc/")
        spróbuj:
            builders = server.getAllBuilders()
        wyjąwszy OSError jako e:
            self.skipTest("network error: %s" % e)
        self.addCleanup(lambda: server('close')())

        # Perform a minimal sanity check on the result, just to be sure
        # the request means what we think it means.
        self.assertIsInstance(builders, collections.abc.Sequence)
        self.assertPrawda([x dla x w builders jeżeli "3.x" w x], builders)


def test_main():
    support.requires("network")
    support.run_unittest(PythonBuildersTest)

jeżeli __name__ == "__main__":
    test_main()
