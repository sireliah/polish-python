zaimportuj io
zaimportuj socket
zaimportuj datetime
zaimportuj textwrap
zaimportuj unittest
zaimportuj functools
zaimportuj contextlib
z test zaimportuj support
z nntplib zaimportuj NNTP, GroupInfo
zaimportuj nntplib
z unittest.mock zaimportuj patch
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    ssl = Nic

TIMEOUT = 30

# TODO:
# - test the `file` arg to more commands
# - test error conditions
# - test auth oraz `usenetrc`


klasa NetworkedNNTPTestsMixin:

    def test_welcome(self):
        welcome = self.server.getwelcome()
        self.assertEqual(str, type(welcome))

    def test_help(self):
        resp, lines = self.server.help()
        self.assertPrawda(resp.startswith("100 "), resp)
        dla line w lines:
            self.assertEqual(str, type(line))

    def test_list(self):
        resp, groups = self.server.list()
        jeżeli len(groups) > 0:
            self.assertEqual(GroupInfo, type(groups[0]))
            self.assertEqual(str, type(groups[0].group))

    def test_list_active(self):
        resp, groups = self.server.list(self.GROUP_PAT)
        jeżeli len(groups) > 0:
            self.assertEqual(GroupInfo, type(groups[0]))
            self.assertEqual(str, type(groups[0].group))

    def test_unknown_command(self):
        przy self.assertRaises(nntplib.NNTPPermanentError) jako cm:
            self.server._shortcmd("XYZZY")
        resp = cm.exception.response
        self.assertPrawda(resp.startswith("500 "), resp)

    def test_newgroups(self):
        # gmane gets a constant influx of new groups.  In order nie to stress
        # the server too much, we choose a recent date w the past.
        dt = datetime.date.today() - datetime.timedelta(days=7)
        resp, groups = self.server.newgroups(dt)
        jeżeli len(groups) > 0:
            self.assertIsInstance(groups[0], GroupInfo)
            self.assertIsInstance(groups[0].group, str)

    def test_description(self):
        def _check_desc(desc):
            # Sanity checks
            self.assertIsInstance(desc, str)
            self.assertNotIn(self.GROUP_NAME, desc)
        desc = self.server.description(self.GROUP_NAME)
        _check_desc(desc)
        # Another sanity check
        self.assertIn("Python", desc)
        # With a pattern
        desc = self.server.description(self.GROUP_PAT)
        _check_desc(desc)
        # Shouldn't exist
        desc = self.server.description("zk.brrtt.baz")
        self.assertEqual(desc, '')

    def test_descriptions(self):
        resp, descs = self.server.descriptions(self.GROUP_PAT)
        # 215 dla LIST NEWSGROUPS, 282 dla XGTITLE
        self.assertPrawda(
            resp.startswith("215 ") albo resp.startswith("282 "), resp)
        self.assertIsInstance(descs, dict)
        desc = descs[self.GROUP_NAME]
        self.assertEqual(desc, self.server.description(self.GROUP_NAME))

    def test_group(self):
        result = self.server.group(self.GROUP_NAME)
        self.assertEqual(5, len(result))
        resp, count, first, last, group = result
        self.assertEqual(group, self.GROUP_NAME)
        self.assertIsInstance(count, int)
        self.assertIsInstance(first, int)
        self.assertIsInstance(last, int)
        self.assertLessEqual(first, last)
        self.assertPrawda(resp.startswith("211 "), resp)

    def test_date(self):
        resp, date = self.server.date()
        self.assertIsInstance(date, datetime.datetime)
        # Sanity check
        self.assertGreaterEqual(date.year, 1995)
        self.assertLessEqual(date.year, 2030)

    def _check_art_dict(self, art_dict):
        # Some sanity checks dla a field dictionary returned by OVER / XOVER
        self.assertIsInstance(art_dict, dict)
        # NNTP has 7 mandatory fields
        self.assertGreaterEqual(art_dict.keys(),
            {"subject", "from", "date", "message-id",
             "references", ":bytes", ":lines"}
            )
        dla v w art_dict.values():
            self.assertIsInstance(v, (str, type(Nic)))

    def test_xover(self):
        resp, count, first, last, name = self.server.group(self.GROUP_NAME)
        resp, lines = self.server.xover(last - 5, last)
        jeżeli len(lines) == 0:
            self.skipTest("no articles retrieved")
        # The 'last' article jest nie necessarily part of the output (cancelled?)
        art_num, art_dict = lines[0]
        self.assertGreaterEqual(art_num, last - 5)
        self.assertLessEqual(art_num, last)
        self._check_art_dict(art_dict)

    def test_over(self):
        resp, count, first, last, name = self.server.group(self.GROUP_NAME)
        start = last - 10
        # The "start-" article range form
        resp, lines = self.server.over((start, Nic))
        art_num, art_dict = lines[0]
        self._check_art_dict(art_dict)
        # The "start-end" article range form
        resp, lines = self.server.over((start, last))
        art_num, art_dict = lines[-1]
        # The 'last' article jest nie necessarily part of the output (cancelled?)
        self.assertGreaterEqual(art_num, start)
        self.assertLessEqual(art_num, last)
        self._check_art_dict(art_dict)
        # XXX The "message_id" form jest unsupported by gmane
        # 503 Overview by message-ID unsupported

    def test_xhdr(self):
        resp, count, first, last, name = self.server.group(self.GROUP_NAME)
        resp, lines = self.server.xhdr('subject', last)
        dla line w lines:
            self.assertEqual(str, type(line[1]))

    def check_article_resp(self, resp, article, art_num=Nic):
        self.assertIsInstance(article, nntplib.ArticleInfo)
        jeżeli art_num jest nie Nic:
            self.assertEqual(article.number, art_num)
        dla line w article.lines:
            self.assertIsInstance(line, bytes)
        # XXX this could exceptionally happen...
        self.assertNotIn(article.lines[-1], (b".", b".\n", b".\r\n"))

    def test_article_head_body(self):
        resp, count, first, last, name = self.server.group(self.GROUP_NAME)
        # Try to find an available article
        dla art_num w (last, first, last - 1):
            spróbuj:
                resp, head = self.server.head(art_num)
            wyjąwszy nntplib.NNTPTemporaryError jako e:
                jeżeli nie e.response.startswith("423 "):
                    podnieś
                # "423 No such article" => choose another one
                kontynuuj
            przerwij
        inaczej:
            self.skipTest("could nie find a suitable article number")
        self.assertPrawda(resp.startswith("221 "), resp)
        self.check_article_resp(resp, head, art_num)
        resp, body = self.server.body(art_num)
        self.assertPrawda(resp.startswith("222 "), resp)
        self.check_article_resp(resp, body, art_num)
        resp, article = self.server.article(art_num)
        self.assertPrawda(resp.startswith("220 "), resp)
        self.check_article_resp(resp, article, art_num)
        # Tolerate running the tests z behind a NNTP virus checker
        blacklist = lambda line: line.startswith(b'X-Antivirus')
        filtered_head_lines = [line dla line w head.lines
                               jeżeli nie blacklist(line)]
        filtered_lines = [line dla line w article.lines
                          jeżeli nie blacklist(line)]
        self.assertEqual(filtered_lines, filtered_head_lines + [b''] + body.lines)

    def test_capabilities(self):
        # The server under test implements NNTP version 2 oraz has a
        # couple of well-known capabilities. Just sanity check that we
        # got them.
        def _check_caps(caps):
            caps_list = caps['LIST']
            self.assertIsInstance(caps_list, (list, tuple))
            self.assertIn('OVERVIEW.FMT', caps_list)
        self.assertGreaterEqual(self.server.nntp_version, 2)
        _check_caps(self.server.getcapabilities())
        # This re-emits the command
        resp, caps = self.server.capabilities()
        _check_caps(caps)

    @unittest.skipUnless(ssl, 'requires SSL support')
    def test_starttls(self):
        file = self.server.file
        sock = self.server.sock
        spróbuj:
            self.server.starttls()
        wyjąwszy nntplib.NNTPPermanentError:
            self.skipTest("STARTTLS nie supported by server.")
        inaczej:
            # Check that the socket oraz internal pseudo-file really were
            # changed.
            self.assertNotEqual(file, self.server.file)
            self.assertNotEqual(sock, self.server.sock)
            # Check that the new socket really jest an SSL one
            self.assertIsInstance(self.server.sock, ssl.SSLSocket)
            # Check that trying starttls when it's already active fails.
            self.assertRaises(ValueError, self.server.starttls)

    def test_zlogin(self):
        # This test must be the penultimate because further commands will be
        # refused.
        baduser = "notarealuser"
        badpw = "notarealpassword"
        # Check that bogus credentials cause failure
        self.assertRaises(nntplib.NNTPError, self.server.login,
                          user=baduser, dalejword=badpw, usenetrc=Nieprawda)
        # FIXME: We should check that correct credentials succeed, but that
        # would require valid details dla some server somewhere to be w the
        # test suite, I think. Gmane jest anonymous, at least jako used dla the
        # other tests.

    def test_zzquit(self):
        # This test must be called last, hence the name
        cls = type(self)
        spróbuj:
            self.server.quit()
        w_końcu:
            cls.server = Nic

    @classmethod
    def wrap_methods(cls):
        # Wrap all methods w a transient_internet() exception catcher
        # XXX put a generic version w test.support?
        def wrap_meth(meth):
            @functools.wraps(meth)
            def wrapped(self):
                przy support.transient_internet(self.NNTP_HOST):
                    meth(self)
            zwróć wrapped
        dla name w dir(cls):
            jeżeli nie name.startswith('test_'):
                kontynuuj
            meth = getattr(cls, name)
            jeżeli nie callable(meth):
                kontynuuj
            # Need to use a closure so that meth remains bound to its current
            # value
            setattr(cls, name, wrap_meth(meth))

    def test_with_statement(self):
        def is_connected():
            jeżeli nie hasattr(server, 'file'):
                zwróć Nieprawda
            spróbuj:
                server.help()
            wyjąwszy (OSError, EOFError):
                zwróć Nieprawda
            zwróć Prawda

        przy self.NNTP_CLASS(self.NNTP_HOST, timeout=TIMEOUT, usenetrc=Nieprawda) jako server:
            self.assertPrawda(is_connected())
            self.assertPrawda(server.help())
        self.assertNieprawda(is_connected())

        przy self.NNTP_CLASS(self.NNTP_HOST, timeout=TIMEOUT, usenetrc=Nieprawda) jako server:
            server.quit()
        self.assertNieprawda(is_connected())


NetworkedNNTPTestsMixin.wrap_methods()


klasa NetworkedNNTPTests(NetworkedNNTPTestsMixin, unittest.TestCase):
    # This server supports STARTTLS (gmane doesn't)
    NNTP_HOST = 'news.trigofacile.com'
    GROUP_NAME = 'fr.comp.lang.python'
    GROUP_PAT = 'fr.comp.lang.*'

    NNTP_CLASS = NNTP

    @classmethod
    def setUpClass(cls):
        support.requires("network")
        przy support.transient_internet(cls.NNTP_HOST):
            cls.server = cls.NNTP_CLASS(cls.NNTP_HOST, timeout=TIMEOUT, usenetrc=Nieprawda)

    @classmethod
    def tearDownClass(cls):
        jeżeli cls.server jest nie Nic:
            cls.server.quit()

@unittest.skipUnless(ssl, 'requires SSL support')
klasa NetworkedNNTP_SSLTests(NetworkedNNTPTests):

    # Technical limits dla this public NNTP server (see http://www.aioe.org):
    # "Only two concurrent connections per IP address are allowed oraz
    # 400 connections per day are accepted z each IP address."

    NNTP_HOST = 'nntp.aioe.org'
    GROUP_NAME = 'comp.lang.python'
    GROUP_PAT = 'comp.lang.*'

    NNTP_CLASS = getattr(nntplib, 'NNTP_SSL', Nic)

    # Disabled jako it produces too much data
    test_list = Nic

    # Disabled jako the connection will already be encrypted.
    test_starttls = Nic


#
# Non-networked tests using a local server (or something mocking it).
#

klasa _NNTPServerIO(io.RawIOBase):
    """A raw IO object allowing NNTP commands to be received oraz processed
    by a handler.  The handler can push responses which can then be read
    z the IO object."""

    def __init__(self, handler):
        io.RawIOBase.__init__(self)
        # The channel z the client
        self.c2s = io.BytesIO()
        # The channel to the client
        self.s2c = io.BytesIO()
        self.handler = handler
        self.handler.start(self.c2s.readline, self.push_data)

    def readable(self):
        zwróć Prawda

    def writable(self):
        zwróć Prawda

    def push_data(self, data):
        """Push (buffer) some data to send to the client."""
        pos = self.s2c.tell()
        self.s2c.seek(0, 2)
        self.s2c.write(data)
        self.s2c.seek(pos)

    def write(self, b):
        """The client sends us some data"""
        pos = self.c2s.tell()
        self.c2s.write(b)
        self.c2s.seek(pos)
        self.handler.process_pending()
        zwróć len(b)

    def readinto(self, buf):
        """The client wants to read a response"""
        self.handler.process_pending()
        b = self.s2c.read(len(buf))
        n = len(b)
        buf[:n] = b
        zwróć n


def make_mock_file(handler):
    sio = _NNTPServerIO(handler)
    # Using BufferedRWPair instead of BufferedRandom ensures the file
    # isn't seekable.
    file = io.BufferedRWPair(sio, sio)
    zwróć (sio, file)


klasa MockedNNTPTestsMixin:
    # Override w derived classes
    handler_class = Nic

    def setUp(self):
        super().setUp()
        self.make_server()

    def tearDown(self):
        super().tearDown()
        usuń self.server

    def make_server(self, *args, **kwargs):
        self.handler = self.handler_class()
        self.sio, file = make_mock_file(self.handler)
        self.server = nntplib._NNTPBase(file, 'test.server', *args, **kwargs)
        zwróć self.server


klasa MockedNNTPWithReaderModeMixin(MockedNNTPTestsMixin):
    def setUp(self):
        super().setUp()
        self.make_server(readermode=Prawda)


klasa NNTPv1Handler:
    """A handler dla RFC 977"""

    welcome = "200 NNTP mock server"

    def start(self, readline, push_data):
        self.in_body = Nieprawda
        self.allow_posting = Prawda
        self._readline = readline
        self._push_data = push_data
        self._logged_in = Nieprawda
        self._user_sent = Nieprawda
        # Our welcome
        self.handle_welcome()

    def _decode(self, data):
        zwróć str(data, "utf-8", "surrogateescape")

    def process_pending(self):
        jeżeli self.in_body:
            dopóki Prawda:
                line = self._readline()
                jeżeli nie line:
                    zwróć
                self.body.append(line)
                jeżeli line == b".\r\n":
                    przerwij
            spróbuj:
                meth, tokens = self.body_callback
                meth(*tokens, body=self.body)
            w_końcu:
                self.body_callback = Nic
                self.body = Nic
                self.in_body = Nieprawda
        dopóki Prawda:
            line = self._decode(self._readline())
            jeżeli nie line:
                zwróć
            jeżeli nie line.endswith("\r\n"):
                podnieś ValueError("line doesn't end przy \\r\\n: {!r}".format(line))
            line = line[:-2]
            cmd, *tokens = line.split()
            #meth = getattr(self.handler, "handle_" + cmd.upper(), Nic)
            meth = getattr(self, "handle_" + cmd.upper(), Nic)
            jeżeli meth jest Nic:
                self.handle_unknown()
            inaczej:
                spróbuj:
                    meth(*tokens)
                wyjąwszy Exception jako e:
                    podnieś ValueError("command failed: {!r}".format(line)) z e
                inaczej:
                    jeżeli self.in_body:
                        self.body_callback = meth, tokens
                        self.body = []

    def expect_body(self):
        """Flag that the client jest expected to post a request body"""
        self.in_body = Prawda

    def push_data(self, data):
        """Push some binary data"""
        self._push_data(data)

    def push_lit(self, lit):
        """Push a string literal"""
        lit = textwrap.dedent(lit)
        lit = "\r\n".join(lit.splitlines()) + "\r\n"
        lit = lit.encode('utf-8')
        self.push_data(lit)

    def handle_unknown(self):
        self.push_lit("500 What?")

    def handle_welcome(self):
        self.push_lit(self.welcome)

    def handle_QUIT(self):
        self.push_lit("205 Bye!")

    def handle_DATE(self):
        self.push_lit("111 20100914001155")

    def handle_GROUP(self, group):
        jeżeli group == "fr.comp.lang.python":
            self.push_lit("211 486 761 1265 fr.comp.lang.python")
        inaczej:
            self.push_lit("411 No such group {}".format(group))

    def handle_HELP(self):
        self.push_lit("""\
            100 Legal commands
              authinfo user Name|pass Password|generic <prog> <args>
              date
              help
            Report problems to <root@example.org>
            .""")

    def handle_STAT(self, message_spec=Nic):
        jeżeli message_spec jest Nic:
            self.push_lit("412 No newsgroup selected")
        albo_inaczej message_spec == "3000234":
            self.push_lit("223 3000234 <45223423@example.com>")
        albo_inaczej message_spec == "<45223423@example.com>":
            self.push_lit("223 0 <45223423@example.com>")
        inaczej:
            self.push_lit("430 No Such Article Found")

    def handle_NEXT(self):
        self.push_lit("223 3000237 <668929@example.org> retrieved")

    def handle_LAST(self):
        self.push_lit("223 3000234 <45223423@example.com> retrieved")

    def handle_LIST(self, action=Nic, param=Nic):
        jeżeli action jest Nic:
            self.push_lit("""\
                215 Newsgroups w form "group high low flags".
                comp.lang.python 0000052340 0000002828 y
                comp.lang.python.announce 0000001153 0000000993 m
                free.it.comp.lang.python 0000000002 0000000002 y
                fr.comp.lang.python 0000001254 0000000760 y
                free.it.comp.lang.python.learner 0000000000 0000000001 y
                tw.bbs.comp.lang.python 0000000304 0000000304 y
                .""")
        albo_inaczej action == "ACTIVE":
            jeżeli param == "*distutils*":
                self.push_lit("""\
                    215 Newsgroups w form "group high low flags"
                    gmane.comp.python.distutils.devel 0000014104 0000000001 m
                    gmane.comp.python.distutils.cvs 0000000000 0000000001 m
                    .""")
            inaczej:
                self.push_lit("""\
                    215 Newsgroups w form "group high low flags"
                    .""")
        albo_inaczej action == "OVERVIEW.FMT":
            self.push_lit("""\
                215 Order of fields w overview database.
                Subject:
                From:
                Date:
                Message-ID:
                References:
                Bytes:
                Lines:
                Xref:full
                .""")
        albo_inaczej action == "NEWSGROUPS":
            assert param jest nie Nic
            jeżeli param == "comp.lang.python":
                self.push_lit("""\
                    215 Descriptions w form "group description".
                    comp.lang.python\tThe Python computer language.
                    .""")
            albo_inaczej param == "comp.lang.python*":
                self.push_lit("""\
                    215 Descriptions w form "group description".
                    comp.lang.python.announce\tAnnouncements about the Python language. (Moderated)
                    comp.lang.python\tThe Python computer language.
                    .""")
            inaczej:
                self.push_lit("""\
                    215 Descriptions w form "group description".
                    .""")
        inaczej:
            self.push_lit('501 Unknown LIST keyword')

    def handle_NEWNEWS(self, group, date_str, time_str):
        # We hard code different zwróć messages depending on dalejed
        # argument oraz date syntax.
        jeżeli (group == "comp.lang.python" oraz date_str == "20100913"
            oraz time_str == "082004"):
            # Date was dalejed w RFC 3977 format (NNTP "v2")
            self.push_lit("""\
                230 list of newsarticles (NNTP v2) created after Mon Sep 13 08:20:04 2010 follows
                <a4929a40-6328-491a-aaaf-cb79ed7309a2@q2g2000vbk.googlegroups.com>
                <f30c0419-f549-4218-848f-d7d0131da931@y3g2000vbm.googlegroups.com>
                .""")
        albo_inaczej (group == "comp.lang.python" oraz date_str == "100913"
            oraz time_str == "082004"):
            # Date was dalejed w RFC 977 format (NNTP "v1")
            self.push_lit("""\
                230 list of newsarticles (NNTP v1) created after Mon Sep 13 08:20:04 2010 follows
                <a4929a40-6328-491a-aaaf-cb79ed7309a2@q2g2000vbk.googlegroups.com>
                <f30c0419-f549-4218-848f-d7d0131da931@y3g2000vbm.googlegroups.com>
                .""")
        albo_inaczej (group == 'comp.lang.python' oraz
              date_str w ('20100101', '100101') oraz
              time_str == '090000'):
            self.push_lit('too long line' * 3000 +
                          '\n.')
        inaczej:
            self.push_lit("""\
                230 An empty list of newsarticles follows
                .""")
        # (Note dla experiments: many servers disable NEWNEWS.
        #  As of this writing, sicinfo3.epfl.ch doesn't.)

    def handle_XOVER(self, message_spec):
        jeżeli message_spec == "57-59":
            self.push_lit(
                "224 Overview information dla 57-58 follows\n"
                "57\tRe: ANN: New Plone book przy strong Python (and Zope) themes throughout"
                    "\tDoug Hellmann <doug.hellmann-Re5JQEeQqe8AvxtiuMwx3w@public.gmane.org>"
                    "\tSat, 19 Jun 2010 18:04:08 -0400"
                    "\t<4FD05F05-F98B-44DC-8111-C6009C925F0C@gmail.com>"
                    "\t<hvalf7$ort$1@dough.gmane.org>\t7103\t16"
                    "\tXref: news.gmane.org gmane.comp.python.authors:57"
                    "\n"
                "58\tLooking dla a few good bloggers"
                    "\tDoug Hellmann <doug.hellmann-Re5JQEeQqe8AvxtiuMwx3w@public.gmane.org>"
                    "\tThu, 22 Jul 2010 09:14:14 -0400"
                    "\t<A29863FA-F388-40C3-AA25-0FD06B09B5BF@gmail.com>"
                    "\t\t6683\t16"
                    "\t"
                    "\n"
                # An UTF-8 overview line z fr.comp.lang.python
                "59\tRe: Message d'erreur incompréhensible (par moi)"
                    "\tEric Brunel <eric.brunel@pragmadev.nospam.com>"
                    "\tWed, 15 Sep 2010 18:09:15 +0200"
                    "\t<eric.brunel-2B8B56.18091515092010@news.wanadoo.fr>"
                    "\t<4c90ec87$0$32425$ba4acef3@reader.news.orange.fr>\t1641\t27"
                    "\tXref: saria.nerim.net fr.comp.lang.python:1265"
                    "\n"
                ".\n")
        inaczej:
            self.push_lit("""\
                224 No articles
                .""")

    def handle_POST(self, *, body=Nic):
        jeżeli body jest Nic:
            jeżeli self.allow_posting:
                self.push_lit("340 Input article; end przy <CR-LF>.<CR-LF>")
                self.expect_body()
            inaczej:
                self.push_lit("440 Posting nie permitted")
        inaczej:
            assert self.allow_posting
            self.push_lit("240 Article received OK")
            self.posted_body = body

    def handle_IHAVE(self, message_id, *, body=Nic):
        jeżeli body jest Nic:
            jeżeli (self.allow_posting oraz
                message_id == "<i.am.an.article.you.will.want@example.com>"):
                self.push_lit("335 Send it; end przy <CR-LF>.<CR-LF>")
                self.expect_body()
            inaczej:
                self.push_lit("435 Article nie wanted")
        inaczej:
            assert self.allow_posting
            self.push_lit("235 Article transferred OK")
            self.posted_body = body

    sample_head = """\
        From: "Demo User" <nobody@example.net>
        Subject: I am just a test article
        Content-Type: text/plain; charset=UTF-8; format=flowed
        Message-ID: <i.am.an.article.you.will.want@example.com>"""

    sample_body = """\
        This jest just a test article.
        ..Here jest a dot-starting line.

        -- Signed by Andr\xe9."""

    sample_article = sample_head + "\n\n" + sample_body

    def handle_ARTICLE(self, message_spec=Nic):
        jeżeli message_spec jest Nic:
            self.push_lit("220 3000237 <45223423@example.com>")
        albo_inaczej message_spec == "<45223423@example.com>":
            self.push_lit("220 0 <45223423@example.com>")
        albo_inaczej message_spec == "3000234":
            self.push_lit("220 3000234 <45223423@example.com>")
        inaczej:
            self.push_lit("430 No Such Article Found")
            zwróć
        self.push_lit(self.sample_article)
        self.push_lit(".")

    def handle_HEAD(self, message_spec=Nic):
        jeżeli message_spec jest Nic:
            self.push_lit("221 3000237 <45223423@example.com>")
        albo_inaczej message_spec == "<45223423@example.com>":
            self.push_lit("221 0 <45223423@example.com>")
        albo_inaczej message_spec == "3000234":
            self.push_lit("221 3000234 <45223423@example.com>")
        inaczej:
            self.push_lit("430 No Such Article Found")
            zwróć
        self.push_lit(self.sample_head)
        self.push_lit(".")

    def handle_BODY(self, message_spec=Nic):
        jeżeli message_spec jest Nic:
            self.push_lit("222 3000237 <45223423@example.com>")
        albo_inaczej message_spec == "<45223423@example.com>":
            self.push_lit("222 0 <45223423@example.com>")
        albo_inaczej message_spec == "3000234":
            self.push_lit("222 3000234 <45223423@example.com>")
        inaczej:
            self.push_lit("430 No Such Article Found")
            zwróć
        self.push_lit(self.sample_body)
        self.push_lit(".")

    def handle_AUTHINFO(self, cred_type, data):
        jeżeli self._logged_in:
            self.push_lit('502 Already Logged In')
        albo_inaczej cred_type == 'user':
            jeżeli self._user_sent:
                self.push_lit('482 User Credential Already Sent')
            inaczej:
                self.push_lit('381 Password Required')
                self._user_sent = Prawda
        albo_inaczej cred_type == 'pass':
            self.push_lit('281 Login Successful')
            self._logged_in = Prawda
        inaczej:
            podnieś Exception('Unknown cred type {}'.format(cred_type))


klasa NNTPv2Handler(NNTPv1Handler):
    """A handler dla RFC 3977 (NNTP "v2")"""

    def handle_CAPABILITIES(self):
        fmt = """\
            101 Capability list:
            VERSION 2 3
            IMPLEMENTATION INN 2.5.1{}
            HDR
            LIST ACTIVE ACTIVE.TIMES DISTRIB.PATS HEADERS NEWSGROUPS OVERVIEW.FMT
            OVER
            POST
            READER
            ."""

        jeżeli nie self._logged_in:
            self.push_lit(fmt.format('\n            AUTHINFO USER'))
        inaczej:
            self.push_lit(fmt.format(''))

    def handle_MODE(self, _):
        podnieś Exception('MODE READER sent despite READER has been advertised')

    def handle_OVER(self, message_spec=Nic):
        zwróć self.handle_XOVER(message_spec)


klasa CapsAfterLoginNNTPv2Handler(NNTPv2Handler):
    """A handler that allows CAPABILITIES only after login"""

    def handle_CAPABILITIES(self):
        jeżeli nie self._logged_in:
            self.push_lit('480 You must log in.')
        inaczej:
            super().handle_CAPABILITIES()


klasa ModeSwitchingNNTPv2Handler(NNTPv2Handler):
    """A server that starts w transit mode"""

    def __init__(self):
        self._switched = Nieprawda

    def handle_CAPABILITIES(self):
        fmt = """\
            101 Capability list:
            VERSION 2 3
            IMPLEMENTATION INN 2.5.1
            HDR
            LIST ACTIVE ACTIVE.TIMES DISTRIB.PATS HEADERS NEWSGROUPS OVERVIEW.FMT
            OVER
            POST
            {}READER
            ."""
        jeżeli self._switched:
            self.push_lit(fmt.format(''))
        inaczej:
            self.push_lit(fmt.format('MODE-'))

    def handle_MODE(self, what):
        assert nie self._switched oraz what == 'reader'
        self._switched = Prawda
        self.push_lit('200 Posting allowed')


klasa NNTPv1v2TestsMixin:

    def setUp(self):
        super().setUp()

    def test_welcome(self):
        self.assertEqual(self.server.welcome, self.handler.welcome)

    def test_authinfo(self):
        jeżeli self.nntp_version == 2:
            self.assertIn('AUTHINFO', self.server._caps)
        self.server.login('testuser', 'testpw')
        # jeżeli AUTHINFO jest gone z _caps we also know that getcapabilities()
        # has been called after login jako it should
        self.assertNotIn('AUTHINFO', self.server._caps)

    def test_date(self):
        resp, date = self.server.date()
        self.assertEqual(resp, "111 20100914001155")
        self.assertEqual(date, datetime.datetime(2010, 9, 14, 0, 11, 55))

    def test_quit(self):
        self.assertNieprawda(self.sio.closed)
        resp = self.server.quit()
        self.assertEqual(resp, "205 Bye!")
        self.assertPrawda(self.sio.closed)

    def test_help(self):
        resp, help = self.server.help()
        self.assertEqual(resp, "100 Legal commands")
        self.assertEqual(help, [
            '  authinfo user Name|pass Password|generic <prog> <args>',
            '  date',
            '  help',
            'Report problems to <root@example.org>',
        ])

    def test_list(self):
        resp, groups = self.server.list()
        self.assertEqual(len(groups), 6)
        g = groups[1]
        self.assertEqual(g,
            GroupInfo("comp.lang.python.announce", "0000001153",
                      "0000000993", "m"))
        resp, groups = self.server.list("*distutils*")
        self.assertEqual(len(groups), 2)
        g = groups[0]
        self.assertEqual(g,
            GroupInfo("gmane.comp.python.distutils.devel", "0000014104",
                      "0000000001", "m"))

    def test_stat(self):
        resp, art_num, message_id = self.server.stat(3000234)
        self.assertEqual(resp, "223 3000234 <45223423@example.com>")
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")
        resp, art_num, message_id = self.server.stat("<45223423@example.com>")
        self.assertEqual(resp, "223 0 <45223423@example.com>")
        self.assertEqual(art_num, 0)
        self.assertEqual(message_id, "<45223423@example.com>")
        przy self.assertRaises(nntplib.NNTPTemporaryError) jako cm:
            self.server.stat("<non.existent.id>")
        self.assertEqual(cm.exception.response, "430 No Such Article Found")
        przy self.assertRaises(nntplib.NNTPTemporaryError) jako cm:
            self.server.stat()
        self.assertEqual(cm.exception.response, "412 No newsgroup selected")

    def test_next(self):
        resp, art_num, message_id = self.server.next()
        self.assertEqual(resp, "223 3000237 <668929@example.org> retrieved")
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<668929@example.org>")

    def test_last(self):
        resp, art_num, message_id = self.server.last()
        self.assertEqual(resp, "223 3000234 <45223423@example.com> retrieved")
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")

    def test_description(self):
        desc = self.server.description("comp.lang.python")
        self.assertEqual(desc, "The Python computer language.")
        desc = self.server.description("comp.lang.pythonx")
        self.assertEqual(desc, "")

    def test_descriptions(self):
        resp, groups = self.server.descriptions("comp.lang.python")
        self.assertEqual(resp, '215 Descriptions w form "group description".')
        self.assertEqual(groups, {
            "comp.lang.python": "The Python computer language.",
            })
        resp, groups = self.server.descriptions("comp.lang.python*")
        self.assertEqual(groups, {
            "comp.lang.python": "The Python computer language.",
            "comp.lang.python.announce": "Announcements about the Python language. (Moderated)",
            })
        resp, groups = self.server.descriptions("comp.lang.pythonx")
        self.assertEqual(groups, {})

    def test_group(self):
        resp, count, first, last, group = self.server.group("fr.comp.lang.python")
        self.assertPrawda(resp.startswith("211 "), resp)
        self.assertEqual(first, 761)
        self.assertEqual(last, 1265)
        self.assertEqual(count, 486)
        self.assertEqual(group, "fr.comp.lang.python")
        przy self.assertRaises(nntplib.NNTPTemporaryError) jako cm:
            self.server.group("comp.lang.python.devel")
        exc = cm.exception
        self.assertPrawda(exc.response.startswith("411 No such group"),
                        exc.response)

    def test_newnews(self):
        # NEWNEWS comp.lang.python [20]100913 082004
        dt = datetime.datetime(2010, 9, 13, 8, 20, 4)
        resp, ids = self.server.newnews("comp.lang.python", dt)
        expected = (
            "230 list of newsarticles (NNTP v{0}) "
            "created after Mon Sep 13 08:20:04 2010 follows"
            ).format(self.nntp_version)
        self.assertEqual(resp, expected)
        self.assertEqual(ids, [
            "<a4929a40-6328-491a-aaaf-cb79ed7309a2@q2g2000vbk.googlegroups.com>",
            "<f30c0419-f549-4218-848f-d7d0131da931@y3g2000vbm.googlegroups.com>",
            ])
        # NEWNEWS fr.comp.lang.python [20]100913 082004
        dt = datetime.datetime(2010, 9, 13, 8, 20, 4)
        resp, ids = self.server.newnews("fr.comp.lang.python", dt)
        self.assertEqual(resp, "230 An empty list of newsarticles follows")
        self.assertEqual(ids, [])

    def _check_article_body(self, lines):
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[-1].decode('utf-8'), "-- Signed by André.")
        self.assertEqual(lines[-2], b"")
        self.assertEqual(lines[-3], b".Here jest a dot-starting line.")
        self.assertEqual(lines[-4], b"This jest just a test article.")

    def _check_article_head(self, lines):
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], b'From: "Demo User" <nobody@example.net>')
        self.assertEqual(lines[3], b"Message-ID: <i.am.an.article.you.will.want@example.com>")

    def _check_article_data(self, lines):
        self.assertEqual(len(lines), 9)
        self._check_article_head(lines[:4])
        self._check_article_body(lines[-4:])
        self.assertEqual(lines[4], b"")

    def test_article(self):
        # ARTICLE
        resp, info = self.server.article()
        self.assertEqual(resp, "220 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_data(lines)
        # ARTICLE num
        resp, info = self.server.article(3000234)
        self.assertEqual(resp, "220 3000234 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_data(lines)
        # ARTICLE id
        resp, info = self.server.article("<45223423@example.com>")
        self.assertEqual(resp, "220 0 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 0)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_data(lines)
        # Non-existent id
        przy self.assertRaises(nntplib.NNTPTemporaryError) jako cm:
            self.server.article("<non-existent@example.com>")
        self.assertEqual(cm.exception.response, "430 No Such Article Found")

    def test_article_file(self):
        # With a "file" argument
        f = io.BytesIO()
        resp, info = self.server.article(file=f)
        self.assertEqual(resp, "220 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self.assertEqual(lines, [])
        data = f.getvalue()
        self.assertPrawda(data.startswith(
            b'From: "Demo User" <nobody@example.net>\r\n'
            b'Subject: I am just a test article\r\n'
            ), ascii(data))
        self.assertPrawda(data.endswith(
            b'This jest just a test article.\r\n'
            b'.Here jest a dot-starting line.\r\n'
            b'\r\n'
            b'-- Signed by Andr\xc3\xa9.\r\n'
            ), ascii(data))

    def test_head(self):
        # HEAD
        resp, info = self.server.head()
        self.assertEqual(resp, "221 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_head(lines)
        # HEAD num
        resp, info = self.server.head(3000234)
        self.assertEqual(resp, "221 3000234 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_head(lines)
        # HEAD id
        resp, info = self.server.head("<45223423@example.com>")
        self.assertEqual(resp, "221 0 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 0)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_head(lines)
        # Non-existent id
        przy self.assertRaises(nntplib.NNTPTemporaryError) jako cm:
            self.server.head("<non-existent@example.com>")
        self.assertEqual(cm.exception.response, "430 No Such Article Found")

    def test_head_file(self):
        f = io.BytesIO()
        resp, info = self.server.head(file=f)
        self.assertEqual(resp, "221 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self.assertEqual(lines, [])
        data = f.getvalue()
        self.assertPrawda(data.startswith(
            b'From: "Demo User" <nobody@example.net>\r\n'
            b'Subject: I am just a test article\r\n'
            ), ascii(data))
        self.assertNieprawda(data.endswith(
            b'This jest just a test article.\r\n'
            b'.Here jest a dot-starting line.\r\n'
            b'\r\n'
            b'-- Signed by Andr\xc3\xa9.\r\n'
            ), ascii(data))

    def test_body(self):
        # BODY
        resp, info = self.server.body()
        self.assertEqual(resp, "222 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_body(lines)
        # BODY num
        resp, info = self.server.body(3000234)
        self.assertEqual(resp, "222 3000234 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_body(lines)
        # BODY id
        resp, info = self.server.body("<45223423@example.com>")
        self.assertEqual(resp, "222 0 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 0)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_body(lines)
        # Non-existent id
        przy self.assertRaises(nntplib.NNTPTemporaryError) jako cm:
            self.server.body("<non-existent@example.com>")
        self.assertEqual(cm.exception.response, "430 No Such Article Found")

    def test_body_file(self):
        f = io.BytesIO()
        resp, info = self.server.body(file=f)
        self.assertEqual(resp, "222 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self.assertEqual(lines, [])
        data = f.getvalue()
        self.assertNieprawda(data.startswith(
            b'From: "Demo User" <nobody@example.net>\r\n'
            b'Subject: I am just a test article\r\n'
            ), ascii(data))
        self.assertPrawda(data.endswith(
            b'This jest just a test article.\r\n'
            b'.Here jest a dot-starting line.\r\n'
            b'\r\n'
            b'-- Signed by Andr\xc3\xa9.\r\n'
            ), ascii(data))

    def check_over_xover_resp(self, resp, overviews):
        self.assertPrawda(resp.startswith("224 "), resp)
        self.assertEqual(len(overviews), 3)
        art_num, over = overviews[0]
        self.assertEqual(art_num, 57)
        self.assertEqual(over, {
            "from": "Doug Hellmann <doug.hellmann-Re5JQEeQqe8AvxtiuMwx3w@public.gmane.org>",
            "subject": "Re: ANN: New Plone book przy strong Python (and Zope) themes throughout",
            "date": "Sat, 19 Jun 2010 18:04:08 -0400",
            "message-id": "<4FD05F05-F98B-44DC-8111-C6009C925F0C@gmail.com>",
            "references": "<hvalf7$ort$1@dough.gmane.org>",
            ":bytes": "7103",
            ":lines": "16",
            "xref": "news.gmane.org gmane.comp.python.authors:57"
            })
        art_num, over = overviews[1]
        self.assertEqual(over["xref"], Nic)
        art_num, over = overviews[2]
        self.assertEqual(over["subject"],
                         "Re: Message d'erreur incompréhensible (par moi)")

    def test_xover(self):
        resp, overviews = self.server.xover(57, 59)
        self.check_over_xover_resp(resp, overviews)

    def test_over(self):
        # In NNTP "v1", this will fallback on XOVER
        resp, overviews = self.server.over((57, 59))
        self.check_over_xover_resp(resp, overviews)

    sample_post = (
        b'From: "Demo User" <nobody@example.net>\r\n'
        b'Subject: I am just a test article\r\n'
        b'Content-Type: text/plain; charset=UTF-8; format=flowed\r\n'
        b'Message-ID: <i.am.an.article.you.will.want@example.com>\r\n'
        b'\r\n'
        b'This jest just a test article.\r\n'
        b'.Here jest a dot-starting line.\r\n'
        b'\r\n'
        b'-- Signed by Andr\xc3\xa9.\r\n'
    )

    def _check_posted_body(self):
        # Check the raw body jako received by the server
        lines = self.handler.posted_body
        # One additional line dla the "." terminator
        self.assertEqual(len(lines), 10)
        self.assertEqual(lines[-1], b'.\r\n')
        self.assertEqual(lines[-2], b'-- Signed by Andr\xc3\xa9.\r\n')
        self.assertEqual(lines[-3], b'\r\n')
        self.assertEqual(lines[-4], b'..Here jest a dot-starting line.\r\n')
        self.assertEqual(lines[0], b'From: "Demo User" <nobody@example.net>\r\n')

    def _check_post_ihave_sub(self, func, *args, file_factory):
        # First the prepared post przy CRLF endings
        post = self.sample_post
        func_args = args + (file_factory(post),)
        self.handler.posted_body = Nic
        resp = func(*func_args)
        self._check_posted_body()
        # Then the same post przy "normal" line endings - they should be
        # converted by NNTP.post oraz NNTP.ihave.
        post = self.sample_post.replace(b"\r\n", b"\n")
        func_args = args + (file_factory(post),)
        self.handler.posted_body = Nic
        resp = func(*func_args)
        self._check_posted_body()
        zwróć resp

    def check_post_ihave(self, func, success_resp, *args):
        # With a bytes object
        resp = self._check_post_ihave_sub(func, *args, file_factory=bytes)
        self.assertEqual(resp, success_resp)
        # With a bytearray object
        resp = self._check_post_ihave_sub(func, *args, file_factory=bytearray)
        self.assertEqual(resp, success_resp)
        # With a file object
        resp = self._check_post_ihave_sub(func, *args, file_factory=io.BytesIO)
        self.assertEqual(resp, success_resp)
        # With an iterable of terminated lines
        def iterlines(b):
            zwróć iter(b.splitlines(keepends=Prawda))
        resp = self._check_post_ihave_sub(func, *args, file_factory=iterlines)
        self.assertEqual(resp, success_resp)
        # With an iterable of non-terminated lines
        def iterlines(b):
            zwróć iter(b.splitlines(keepends=Nieprawda))
        resp = self._check_post_ihave_sub(func, *args, file_factory=iterlines)
        self.assertEqual(resp, success_resp)

    def test_post(self):
        self.check_post_ihave(self.server.post, "240 Article received OK")
        self.handler.allow_posting = Nieprawda
        przy self.assertRaises(nntplib.NNTPTemporaryError) jako cm:
            self.server.post(self.sample_post)
        self.assertEqual(cm.exception.response,
                         "440 Posting nie permitted")

    def test_ihave(self):
        self.check_post_ihave(self.server.ihave, "235 Article transferred OK",
                              "<i.am.an.article.you.will.want@example.com>")
        przy self.assertRaises(nntplib.NNTPTemporaryError) jako cm:
            self.server.ihave("<another.message.id>", self.sample_post)
        self.assertEqual(cm.exception.response,
                         "435 Article nie wanted")

    def test_too_long_lines(self):
        dt = datetime.datetime(2010, 1, 1, 9, 0, 0)
        self.assertRaises(nntplib.NNTPDataError,
                          self.server.newnews, "comp.lang.python", dt)


klasa NNTPv1Tests(NNTPv1v2TestsMixin, MockedNNTPTestsMixin, unittest.TestCase):
    """Tests an NNTP v1 server (no capabilities)."""

    nntp_version = 1
    handler_class = NNTPv1Handler

    def test_caps(self):
        caps = self.server.getcapabilities()
        self.assertEqual(caps, {})
        self.assertEqual(self.server.nntp_version, 1)
        self.assertEqual(self.server.nntp_implementation, Nic)


klasa NNTPv2Tests(NNTPv1v2TestsMixin, MockedNNTPTestsMixin, unittest.TestCase):
    """Tests an NNTP v2 server (przy capabilities)."""

    nntp_version = 2
    handler_class = NNTPv2Handler

    def test_caps(self):
        caps = self.server.getcapabilities()
        self.assertEqual(caps, {
            'VERSION': ['2', '3'],
            'IMPLEMENTATION': ['INN', '2.5.1'],
            'AUTHINFO': ['USER'],
            'HDR': [],
            'LIST': ['ACTIVE', 'ACTIVE.TIMES', 'DISTRIB.PATS',
                     'HEADERS', 'NEWSGROUPS', 'OVERVIEW.FMT'],
            'OVER': [],
            'POST': [],
            'READER': [],
            })
        self.assertEqual(self.server.nntp_version, 3)
        self.assertEqual(self.server.nntp_implementation, 'INN 2.5.1')


klasa CapsAfterLoginNNTPv2Tests(MockedNNTPTestsMixin, unittest.TestCase):
    """Tests a probably NNTP v2 server przy capabilities only after login."""

    nntp_version = 2
    handler_class = CapsAfterLoginNNTPv2Handler

    def test_caps_only_after_login(self):
        self.assertEqual(self.server._caps, {})
        self.server.login('testuser', 'testpw')
        self.assertIn('VERSION', self.server._caps)


klasa SendReaderNNTPv2Tests(MockedNNTPWithReaderModeMixin,
        unittest.TestCase):
    """Same tests jako dla v2 but we tell NTTP to send MODE READER to a server
    that isn't w READER mode by default."""

    nntp_version = 2
    handler_class = ModeSwitchingNNTPv2Handler

    def test_we_are_in_reader_mode_after_connect(self):
        self.assertIn('READER', self.server._caps)


klasa MiscTests(unittest.TestCase):

    def test_decode_header(self):
        def gives(a, b):
            self.assertEqual(nntplib.decode_header(a), b)
        gives("" , "")
        gives("a plain header", "a plain header")
        gives(" przy extra  spaces ", " przy extra  spaces ")
        gives("=?ISO-8859-15?Q?D=E9buter_en_Python?=", "Débuter en Python")
        gives("=?utf-8?q?Re=3A_=5Bsqlite=5D_probl=C3=A8me_avec_ORDER_BY_sur_des_cha?="
              " =?utf-8?q?=C3=AEnes_de_caract=C3=A8res_accentu=C3=A9es?=",
              "Re: [sqlite] problème avec ORDER BY sur des chaînes de caractères accentuées")
        gives("Re: =?UTF-8?B?cHJvYmzDqG1lIGRlIG1hdHJpY2U=?=",
              "Re: problème de matrice")
        # A natively utf-8 header (found w the real world!)
        gives("Re: Message d'erreur incompréhensible (par moi)",
              "Re: Message d'erreur incompréhensible (par moi)")

    def test_parse_overview_fmt(self):
        # The minimal (default) response
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", ":bytes", ":lines"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "from", "date", "message-id", "references",
             ":bytes", ":lines"])
        # The minimal response using alternative names
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", "Bytes:", "Lines:"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "from", "date", "message-id", "references",
             ":bytes", ":lines"])
        # Variations w casing
        lines = ["subject:", "FROM:", "DaTe:", "message-ID:",
                 "References:", "BYTES:", "Lines:"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "from", "date", "message-id", "references",
             ":bytes", ":lines"])
        # First example z RFC 3977
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", ":bytes", ":lines", "Xref:full",
                 "Distribution:full"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "from", "date", "message-id", "references",
             ":bytes", ":lines", "xref", "distribution"])
        # Second example z RFC 3977
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", "Bytes:", "Lines:", "Xref:FULL",
                 "Distribution:FULL"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "from", "date", "message-id", "references",
             ":bytes", ":lines", "xref", "distribution"])
        # A classic response z INN
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", "Bytes:", "Lines:", "Xref:full"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "from", "date", "message-id", "references",
             ":bytes", ":lines", "xref"])

    def test_parse_overview(self):
        fmt = nntplib._DEFAULT_OVERVIEW_FMT + ["xref"]
        # First example z RFC 3977
        lines = [
            '3000234\tI am just a test article\t"Demo User" '
            '<nobody@example.com>\t6 Oct 1998 04:38:40 -0500\t'
            '<45223423@example.com>\t<45454@example.net>\t1234\t'
            '17\tXref: news.example.com misc.test:3000363',
        ]
        overview = nntplib._parse_overview(lines, fmt)
        (art_num, fields), = overview
        self.assertEqual(art_num, 3000234)
        self.assertEqual(fields, {
            'subject': 'I am just a test article',
            'from': '"Demo User" <nobody@example.com>',
            'date': '6 Oct 1998 04:38:40 -0500',
            'message-id': '<45223423@example.com>',
            'references': '<45454@example.net>',
            ':bytes': '1234',
            ':lines': '17',
            'xref': 'news.example.com misc.test:3000363',
        })
        # Second example; here the "Xref" field jest totally absent (including
        # the header name) oraz comes out jako Nic
        lines = [
            '3000234\tI am just a test article\t"Demo User" '
            '<nobody@example.com>\t6 Oct 1998 04:38:40 -0500\t'
            '<45223423@example.com>\t<45454@example.net>\t1234\t'
            '17\t\t',
        ]
        overview = nntplib._parse_overview(lines, fmt)
        (art_num, fields), = overview
        self.assertEqual(fields['xref'], Nic)
        # Third example; the "Xref" jest an empty string, dopóki "references"
        # jest a single space.
        lines = [
            '3000234\tI am just a test article\t"Demo User" '
            '<nobody@example.com>\t6 Oct 1998 04:38:40 -0500\t'
            '<45223423@example.com>\t \t1234\t'
            '17\tXref: \t',
        ]
        overview = nntplib._parse_overview(lines, fmt)
        (art_num, fields), = overview
        self.assertEqual(fields['references'], ' ')
        self.assertEqual(fields['xref'], '')

    def test_parse_datetime(self):
        def gives(a, b, *c):
            self.assertEqual(nntplib._parse_datetime(a, b),
                             datetime.datetime(*c))
        # Output of DATE command
        gives("19990623135624", Nic, 1999, 6, 23, 13, 56, 24)
        # Variations
        gives("19990623", "135624", 1999, 6, 23, 13, 56, 24)
        gives("990623", "135624", 1999, 6, 23, 13, 56, 24)
        gives("090623", "135624", 2009, 6, 23, 13, 56, 24)

    def test_unparse_datetime(self):
        # Test non-legacy mode
        # 1) przy a datetime
        def gives(y, M, d, h, m, s, date_str, time_str):
            dt = datetime.datetime(y, M, d, h, m, s)
            self.assertEqual(nntplib._unparse_datetime(dt),
                             (date_str, time_str))
            self.assertEqual(nntplib._unparse_datetime(dt, Nieprawda),
                             (date_str, time_str))
        gives(1999, 6, 23, 13, 56, 24, "19990623", "135624")
        gives(2000, 6, 23, 13, 56, 24, "20000623", "135624")
        gives(2010, 6, 5, 1, 2, 3, "20100605", "010203")
        # 2) przy a date
        def gives(y, M, d, date_str, time_str):
            dt = datetime.date(y, M, d)
            self.assertEqual(nntplib._unparse_datetime(dt),
                             (date_str, time_str))
            self.assertEqual(nntplib._unparse_datetime(dt, Nieprawda),
                             (date_str, time_str))
        gives(1999, 6, 23, "19990623", "000000")
        gives(2000, 6, 23, "20000623", "000000")
        gives(2010, 6, 5, "20100605", "000000")

    def test_unparse_datetime_legacy(self):
        # Test legacy mode (RFC 977)
        # 1) przy a datetime
        def gives(y, M, d, h, m, s, date_str, time_str):
            dt = datetime.datetime(y, M, d, h, m, s)
            self.assertEqual(nntplib._unparse_datetime(dt, Prawda),
                             (date_str, time_str))
        gives(1999, 6, 23, 13, 56, 24, "990623", "135624")
        gives(2000, 6, 23, 13, 56, 24, "000623", "135624")
        gives(2010, 6, 5, 1, 2, 3, "100605", "010203")
        # 2) przy a date
        def gives(y, M, d, date_str, time_str):
            dt = datetime.date(y, M, d)
            self.assertEqual(nntplib._unparse_datetime(dt, Prawda),
                             (date_str, time_str))
        gives(1999, 6, 23, "990623", "000000")
        gives(2000, 6, 23, "000623", "000000")
        gives(2010, 6, 5, "100605", "000000")

    @unittest.skipUnless(ssl, 'requires SSL support')
    def test_ssl_support(self):
        self.assertPrawda(hasattr(nntplib, 'NNTP_SSL'))


klasa PublicAPITests(unittest.TestCase):
    """Ensures that the correct values are exposed w the public API."""

    def test_module_all_attribute(self):
        self.assertPrawda(hasattr(nntplib, '__all__'))
        target_api = ['NNTP', 'NNTPError', 'NNTPReplyError',
                      'NNTPTemporaryError', 'NNTPPermanentError',
                      'NNTPProtocolError', 'NNTPDataError', 'decode_header']
        jeżeli ssl jest nie Nic:
            target_api.append('NNTP_SSL')
        self.assertEqual(set(nntplib.__all__), set(target_api))

klasa MockSocketTests(unittest.TestCase):
    """Tests involving a mock socket object

    Used where the _NNTPServerIO file object jest nie enough."""

    nntp_class = nntplib.NNTP

    def check_constructor_error_conditions(
            self, handler_class,
            expected_error_type, expected_error_msg,
            login=Nic, dalejword=Nic):

        klasa mock_socket_module:
            def create_connection(address, timeout):
                zwróć MockSocket()

        klasa MockSocket:
            def close(self):
                nonlocal socket_closed
                socket_closed = Prawda

            def makefile(socket, mode):
                handler = handler_class()
                _, file = make_mock_file(handler)
                files.append(file)
                zwróć file

        socket_closed = Nieprawda
        files = []
        przy patch('nntplib.socket', mock_socket_module), \
             self.assertRaisesRegex(expected_error_type, expected_error_msg):
            self.nntp_class('dummy', user=login, dalejword=password)
        self.assertPrawda(socket_closed)
        dla f w files:
            self.assertPrawda(f.closed)

    def test_bad_welcome(self):
        #Test a bad welcome message
        klasa Handler(NNTPv1Handler):
            welcome = 'Bad Welcome'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPProtocolError, Handler.welcome)

    def test_service_temporarily_unavailable(self):
        #Test service temporarily unavailable
        klasa Handler(NNTPv1Handler):
            welcome = '400 Service temporarily unavilable'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPTemporaryError, Handler.welcome)

    def test_service_permanently_unavailable(self):
        #Test service permanently unavailable
        klasa Handler(NNTPv1Handler):
            welcome = '502 Service permanently unavilable'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPPermanentError, Handler.welcome)

    def test_bad_capabilities(self):
        #Test a bad capabilities response
        klasa Handler(NNTPv1Handler):
            def handle_CAPABILITIES(self):
                self.push_lit(capabilities_response)
        capabilities_response = '201 bad capability'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPReplyError, capabilities_response)

    def test_login_aborted(self):
        #Test a bad authinfo response
        login = 't@e.com'
        dalejword = 'python'
        klasa Handler(NNTPv1Handler):
            def handle_AUTHINFO(self, *args):
                self.push_lit(authinfo_response)
        authinfo_response = '503 Mechanism nie recognized'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPPermanentError, authinfo_response,
            login, dalejword)

klasa bypass_context:
    """Bypass encryption oraz actual SSL module"""
    def wrap_socket(sock, **args):
        zwróć sock

@unittest.skipUnless(ssl, 'requires SSL support')
klasa MockSslTests(MockSocketTests):
    @staticmethod
    def nntp_class(*pos, **kw):
        zwróć nntplib.NNTP_SSL(*pos, ssl_context=bypass_context, **kw)


jeżeli __name__ == "__main__":
    unittest.main()
