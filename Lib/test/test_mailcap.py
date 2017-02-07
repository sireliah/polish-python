zaimportuj mailcap
zaimportuj os
zaimportuj shutil
zaimportuj test.support
zaimportuj unittest

# Location of mailcap file
MAILCAPFILE = test.support.findfile("mailcap.txt")

# Dict to act jako mock mailcap entry dla this test
# The keys oraz values should match the contents of MAILCAPFILE
MAILCAPDICT = {
    'application/x-movie':
        [{'compose': 'moviemaker %s',
          'x11-bitmap': '"/usr/lib/Zmail/bitmaps/movie.xbm"',
          'description': '"Movie"',
          'view': 'movieplayer %s'}],
    'application/*':
        [{'copiousoutput': '',
          'view': 'echo "This jest \\"%t\\" but        jest 50 \\% Greek to me" \\; cat %s'}],
    'audio/basic':
        [{'edit': 'audiocompose %s',
          'compose': 'audiocompose %s',
          'description': '"An audio fragment"',
          'view': 'showaudio %s'}],
    'video/mpeg':
        [{'view': 'mpeg_play %s'}],
    'application/postscript':
        [{'needsterminal': '', 'view': 'ps-to-terminal %s'},
         {'compose': 'idraw %s', 'view': 'ps-to-terminal %s'}],
    'application/x-dvi':
        [{'view': 'xdvi %s'}],
    'message/external-body':
        [{'composetyped': 'extcompose %s',
          'description': '"A reference to data stored w an external location"',
          'needsterminal': '',
          'view': 'showexternal %s %{access-type} %{name} %{site}     %{directory} %{mode} %{server}'}],
    'text/richtext':
        [{'test': 'test "`echo     %{charset} | tr \'[A-Z]\' \'[a-z]\'`"  = iso-8859-8',
          'copiousoutput': '',
          'view': 'shownonascii iso-8859-8 -e richtext -p %s'}],
    'image/x-xwindowdump':
        [{'view': 'display %s'}],
    'audio/*':
        [{'view': '/usr/local/bin/showaudio %t'}],
    'video/*':
        [{'view': 'animate %s'}],
    'application/frame':
        [{'print': '"cat %s | lp"', 'view': 'showframe %s'}],
    'image/rgb':
        [{'view': 'display %s'}]
}


klasa HelperFunctionTest(unittest.TestCase):

    def test_listmailcapfiles(self):
        # The zwróć value dla listmailcapfiles() will vary by system.
        # So verify that listmailcapfiles() returns a list of strings that jest of
        # non-zero length.
        mcfiles = mailcap.listmailcapfiles()
        self.assertIsInstance(mcfiles, list)
        dla m w mcfiles:
            self.assertIsInstance(m, str)
        przy test.support.EnvironmentVarGuard() jako env:
            # According to RFC 1524, jeżeli MAILCAPS env variable exists, use that
            # oraz only that.
            jeżeli "MAILCAPS" w env:
                env_mailcaps = env["MAILCAPS"].split(os.pathsep)
            inaczej:
                env_mailcaps = ["/testdir1/.mailcap", "/testdir2/mailcap"]
                env["MAILCAPS"] = os.pathsep.join(env_mailcaps)
                mcfiles = mailcap.listmailcapfiles()
        self.assertEqual(env_mailcaps, mcfiles)

    def test_readmailcapfile(self):
        # Test readmailcapfile() using test file. It should match MAILCAPDICT.
        przy open(MAILCAPFILE, 'r') jako mcf:
            d = mailcap.readmailcapfile(mcf)
        self.assertDictEqual(d, MAILCAPDICT)

    def test_lookup(self):
        # Test without key
        expected = [{'view': 'mpeg_play %s'}, {'view': 'animate %s'}]
        actual = mailcap.lookup(MAILCAPDICT, 'video/mpeg')
        self.assertListEqual(expected, actual)

        # Test przy key
        key = 'compose'
        expected = [{'edit': 'audiocompose %s',
                     'compose': 'audiocompose %s',
                     'description': '"An audio fragment"',
                     'view': 'showaudio %s'}]
        actual = mailcap.lookup(MAILCAPDICT, 'audio/basic', key)
        self.assertListEqual(expected, actual)

    def test_subst(self):
        plist = ['id=1', 'number=2', 'total=3']
        # test case: ([field, MIMEtype, filename, plist=[]], <expected string>)
        test_cases = [
            (["", "audio/*", "foo.txt"], ""),
            (["echo foo", "audio/*", "foo.txt"], "echo foo"),
            (["echo %s", "audio/*", "foo.txt"], "echo foo.txt"),
            (["echo %t", "audio/*", "foo.txt"], "echo audio/*"),
            (["echo \%t", "audio/*", "foo.txt"], "echo %t"),
            (["echo foo", "audio/*", "foo.txt", plist], "echo foo"),
            (["echo %{total}", "audio/*", "foo.txt", plist], "echo 3")
        ]
        dla tc w test_cases:
            self.assertEqual(mailcap.subst(*tc[0]), tc[1])


klasa GetcapsTest(unittest.TestCase):

    def test_mock_getcaps(self):
        # Test mailcap.getcaps() using mock mailcap file w this dir.
        # Temporarily override any existing system mailcap file by pointing the
        # MAILCAPS environment variable to our mock file.
        przy test.support.EnvironmentVarGuard() jako env:
            env["MAILCAPS"] = MAILCAPFILE
            caps = mailcap.getcaps()
            self.assertDictEqual(caps, MAILCAPDICT)

    def test_system_mailcap(self):
        # Test mailcap.getcaps() przy mailcap file(s) on system, jeżeli any.
        caps = mailcap.getcaps()
        self.assertIsInstance(caps, dict)
        mailcapfiles = mailcap.listmailcapfiles()
        existingmcfiles = [mcf dla mcf w mailcapfiles jeżeli os.path.exists(mcf)]
        jeżeli existingmcfiles:
            # At least 1 mailcap file exists, so test that.
            dla (k, v) w caps.items():
                self.assertIsInstance(k, str)
                self.assertIsInstance(v, list)
                dla e w v:
                    self.assertIsInstance(e, dict)
        inaczej:
            # No mailcap files on system. getcaps() should zwróć empty dict.
            self.assertEqual({}, caps)


klasa FindmatchTest(unittest.TestCase):

    def test_findmatch(self):

        # default findmatch arguments
        c = MAILCAPDICT
        fname = "foo.txt"
        plist = ["access-type=default", "name=john", "site=python.org",
                 "directory=/tmp", "mode=foo", "server=bar"]
        audio_basic_entry = {
            'edit': 'audiocompose %s',
            'compose': 'audiocompose %s',
            'description': '"An audio fragment"',
            'view': 'showaudio %s'
        }
        audio_entry = {"view": "/usr/local/bin/showaudio %t"}
        video_entry = {'view': 'animate %s'}
        message_entry = {
            'composetyped': 'extcompose %s',
            'description': '"A reference to data stored w an external location"', 'needsterminal': '',
            'view': 'showexternal %s %{access-type} %{name} %{site}     %{directory} %{mode} %{server}'
        }

        # test case: (findmatch args, findmatch keyword args, expected output)
        #   positional args: caps, MIMEtype
        #   keyword args: key="view", filename="/dev/null", plist=[]
        #   output: (command line, mailcap entry)
        cases = [
            ([{}, "video/mpeg"], {}, (Nic, Nic)),
            ([c, "foo/bar"], {}, (Nic, Nic)),
            ([c, "video/mpeg"], {}, ('mpeg_play /dev/null', {'view': 'mpeg_play %s'})),
            ([c, "audio/basic", "edit"], {}, ("audiocompose /dev/null", audio_basic_entry)),
            ([c, "audio/basic", "compose"], {}, ("audiocompose /dev/null", audio_basic_entry)),
            ([c, "audio/basic", "description"], {}, ('"An audio fragment"', audio_basic_entry)),
            ([c, "audio/basic", "foobar"], {}, (Nic, Nic)),
            ([c, "video/*"], {"filename": fname}, ("animate %s" % fname, video_entry)),
            ([c, "audio/basic", "compose"],
             {"filename": fname},
             ("audiocompose %s" % fname, audio_basic_entry)),
            ([c, "audio/basic"],
             {"key": "description", "filename": fname},
             ('"An audio fragment"', audio_basic_entry)),
            ([c, "audio/*"],
             {"filename": fname},
             ("/usr/local/bin/showaudio audio/*", audio_entry)),
            ([c, "message/external-body"],
             {"plist": plist},
             ("showexternal /dev/null default john python.org     /tmp foo bar", message_entry))
        ]
        self._run_cases(cases)

    @unittest.skipUnless(os.name == "posix", "Requires 'test' command on system")
    def test_test(self):
        # findmatch() will automatically check any "test" conditions oraz skip
        # the entry jeżeli the check fails.
        caps = {"test/pass": [{"test": "test 1 -eq 1"}],
                "test/fail": [{"test": "test 1 -eq 0"}]}
        # test case: (findmatch args, findmatch keyword args, expected output)
        #   positional args: caps, MIMEtype, key ("test")
        #   keyword args: N/A
        #   output: (command line, mailcap entry)
        cases = [
            # findmatch will zwróć the mailcap entry dla test/pass because it evaluates to true
            ([caps, "test/pass", "test"], {}, ("test 1 -eq 1", {"test": "test 1 -eq 1"})),
            # findmatch will zwróć Nic because test/fail evaluates to false
            ([caps, "test/fail", "test"], {}, (Nic, Nic))
        ]
        self._run_cases(cases)

    def _run_cases(self, cases):
        dla c w cases:
            self.assertEqual(mailcap.findmatch(*c[0], **c[1]), c[2])


jeżeli __name__ == '__main__':
    unittest.main()
