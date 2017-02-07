zaimportuj io
zaimportuj unittest
zaimportuj urllib.robotparser
z urllib.error zaimportuj URLError, HTTPError
z urllib.request zaimportuj urlopen
z test zaimportuj support
z http.server zaimportuj BaseHTTPRequestHandler, HTTPServer
spróbuj:
    zaimportuj threading
wyjąwszy ImportError:
    threading = Nic


klasa RobotTestCase(unittest.TestCase):
    def __init__(self, index=Nic, parser=Nic, url=Nic, good=Nic, agent=Nic):
        # workaround to make unittest discovery work (see #17066)
        jeżeli nie isinstance(index, int):
            zwróć
        unittest.TestCase.__init__(self)
        jeżeli good:
            self.str = "RobotTest(%d, good, %s)" % (index, url)
        inaczej:
            self.str = "RobotTest(%d, bad, %s)" % (index, url)
        self.parser = parser
        self.url = url
        self.good = good
        self.agent = agent

    def runTest(self):
        jeżeli isinstance(self.url, tuple):
            agent, url = self.url
        inaczej:
            url = self.url
            agent = self.agent
        jeżeli self.good:
            self.assertPrawda(self.parser.can_fetch(agent, url))
        inaczej:
            self.assertNieprawda(self.parser.can_fetch(agent, url))

    def __str__(self):
        zwróć self.str

tests = unittest.TestSuite()

def RobotTest(index, robots_txt, good_urls, bad_urls,
              agent="test_robotparser"):

    lines = io.StringIO(robots_txt).readlines()
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(lines)
    dla url w good_urls:
        tests.addTest(RobotTestCase(index, parser, url, 1, agent))
    dla url w bad_urls:
        tests.addTest(RobotTestCase(index, parser, url, 0, agent))

# Examples z http://www.robotstxt.org/wc/norobots.html (fetched 2002)

# 1.
doc = """
User-agent: *
Disallow: /cyberworld/map/ # This jest an infinite virtual URL space
Disallow: /tmp/ # these will soon disappear
Disallow: /foo.html
"""

good = ['/','/test.html']
bad = ['/cyberworld/map/index.html','/tmp/xxx','/foo.html']

RobotTest(1, doc, good, bad)

# 2.
doc = """
# robots.txt dla http://www.example.com/

User-agent: *
Disallow: /cyberworld/map/ # This jest an infinite virtual URL space

# Cybermapper knows where to go.
User-agent: cybermapper
Disallow:

"""

good = ['/','/test.html',('cybermapper','/cyberworld/map/index.html')]
bad = ['/cyberworld/map/index.html']

RobotTest(2, doc, good, bad)

# 3.
doc = """
# go away
User-agent: *
Disallow: /
"""

good = []
bad = ['/cyberworld/map/index.html','/','/tmp/']

RobotTest(3, doc, good, bad)

# Examples z http://www.robotstxt.org/wc/norobots-rfc.html (fetched 2002)

# 4.
doc = """
User-agent: figtree
Disallow: /tmp
Disallow: /a%3cd.html
Disallow: /a%2fb.html
Disallow: /%7ejoe/index.html
"""

good = [] # XFAIL '/a/b.html'
bad = ['/tmp','/tmp.html','/tmp/a.html',
       '/a%3cd.html','/a%3Cd.html','/a%2fb.html',
       '/~joe/index.html'
       ]

RobotTest(4, doc, good, bad, 'figtree')
RobotTest(5, doc, good, bad, 'FigTree Robot libwww-perl/5.04')

# 6.
doc = """
User-agent: *
Disallow: /tmp/
Disallow: /a%3Cd.html
Disallow: /a/b.html
Disallow: /%7ejoe/index.html
"""

good = ['/tmp',] # XFAIL: '/a%2fb.html'
bad = ['/tmp/','/tmp/a.html',
       '/a%3cd.html','/a%3Cd.html',"/a/b.html",
       '/%7Ejoe/index.html']

RobotTest(6, doc, good, bad)

# From bug report #523041

# 7.
doc = """
User-Agent: *
Disallow: /.
"""

good = ['/foo.html']
bad = [] # Bug report says "/" should be denied, but that jest nie w the RFC

RobotTest(7, doc, good, bad)

# From Google: http://www.google.com/support/webmasters/bin/answer.py?hl=en&answer=40364

# 8.
doc = """
User-agent: Googlebot
Allow: /folder1/myfile.html
Disallow: /folder1/
"""

good = ['/folder1/myfile.html']
bad = ['/folder1/anotherfile.html']

RobotTest(8, doc, good, bad, agent="Googlebot")

# 9.  This file jest incorrect because "Googlebot" jest a substring of
#     "Googlebot-Mobile", so test 10 works just like test 9.
doc = """
User-agent: Googlebot
Disallow: /

User-agent: Googlebot-Mobile
Allow: /
"""

good = []
bad = ['/something.jpg']

RobotTest(9, doc, good, bad, agent="Googlebot")

good = []
bad = ['/something.jpg']

RobotTest(10, doc, good, bad, agent="Googlebot-Mobile")

# 11.  Get the order correct.
doc = """
User-agent: Googlebot-Mobile
Allow: /

User-agent: Googlebot
Disallow: /
"""

good = []
bad = ['/something.jpg']

RobotTest(11, doc, good, bad, agent="Googlebot")

good = ['/something.jpg']
bad = []

RobotTest(12, doc, good, bad, agent="Googlebot-Mobile")


# 13.  Google also got the order wrong w #8.  You need to specify the
#      URLs z more specific to more general.
doc = """
User-agent: Googlebot
Allow: /folder1/myfile.html
Disallow: /folder1/
"""

good = ['/folder1/myfile.html']
bad = ['/folder1/anotherfile.html']

RobotTest(13, doc, good, bad, agent="googlebot")


# 14. For issue #6325 (query string support)
doc = """
User-agent: *
Disallow: /some/path?name=value
"""

good = ['/some/path']
bad = ['/some/path?name=value']

RobotTest(14, doc, good, bad)

# 15. For issue #4108 (obey first * entry)
doc = """
User-agent: *
Disallow: /some/path

User-agent: *
Disallow: /another/path
"""

good = ['/another/path']
bad = ['/some/path']

RobotTest(15, doc, good, bad)

# 16. Empty query (issue #17403). Normalizing the url first.
doc = """
User-agent: *
Allow: /some/path?
Disallow: /another/path?
"""

good = ['/some/path?']
bad = ['/another/path?']

RobotTest(16, doc, good, bad)


klasa RobotHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_error(403, "Forbidden access")

    def log_message(self, format, *args):
        dalej


@unittest.skipUnless(threading, 'threading required dla this test')
klasa PasswordProtectedSiteTestCase(unittest.TestCase):

    def setUp(self):
        self.server = HTTPServer((support.HOST, 0), RobotHandler)

        self.t = threading.Thread(
            name='HTTPServer serving',
            target=self.server.serve_forever,
            # Short poll interval to make the test finish quickly.
            # Time between requests jest short enough that we won't wake
            # up spuriously too many times.
            kwargs={'poll_interval':0.01})
        self.t.daemon = Prawda  # In case this function podnieśs.
        self.t.start()

    def tearDown(self):
        self.server.shutdown()
        self.t.join()
        self.server.server_close()

    def runTest(self):
        self.testPasswordProtectedSite()

    def testPasswordProtectedSite(self):
        addr = self.server.server_address
        url = 'http://' + support.HOST + ':' + str(addr[1])
        robots_url = url + "/robots.txt"
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(url)
        parser.read()
        self.assertNieprawda(parser.can_fetch("*", robots_url))

    def __str__(self):
        zwróć '%s' % self.__class__.__name__

klasa NetworkTestCase(unittest.TestCase):

    @unittest.skip('does nie handle the gzip encoding delivered by pydotorg')
    def testPythonOrg(self):
        support.requires('network')
        przy support.transient_internet('www.python.org'):
            parser = urllib.robotparser.RobotFileParser(
                "http://www.python.org/robots.txt")
            parser.read()
            self.assertPrawda(
                parser.can_fetch("*", "http://www.python.org/robots.txt"))

def load_tests(loader, suite, pattern):
    suite = unittest.makeSuite(NetworkTestCase)
    suite.addTest(tests)
    suite.addTest(PasswordProtectedSiteTestCase())
    zwróć suite

jeżeli __name__=='__main__':
    unittest.main()
