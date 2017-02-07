z unittest zaimportuj mock
zaimportuj os
zaimportuj platform
zaimportuj subprocess
zaimportuj sys
zaimportuj tempfile
zaimportuj unittest
zaimportuj warnings

z test zaimportuj support

klasa PlatformTest(unittest.TestCase):
    def test_architecture(self):
        res = platform.architecture()

    @support.skip_unless_symlink
    def test_architecture_via_symlink(self): # issue3762
        # On Windows, the EXE needs to know where pythonXY.dll jest at so we have
        # to add the directory to the path.
        jeżeli sys.platform == "win32":
            os.environ["Path"] = "{};{}".format(
                os.path.dirname(sys.executable), os.environ["Path"])

        def get(python):
            cmd = [python, '-c',
                'zaimportuj platform; print(platform.architecture())']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            zwróć p.communicate()
        real = os.path.realpath(sys.executable)
        link = os.path.abspath(support.TESTFN)
        os.symlink(real, link)
        spróbuj:
            self.assertEqual(get(real), get(link))
        w_końcu:
            os.remove(link)

    def test_platform(self):
        dla aliased w (Nieprawda, Prawda):
            dla terse w (Nieprawda, Prawda):
                res = platform.platform(aliased, terse)

    def test_system(self):
        res = platform.system()

    def test_node(self):
        res = platform.node()

    def test_release(self):
        res = platform.release()

    def test_version(self):
        res = platform.version()

    def test_machine(self):
        res = platform.machine()

    def test_processor(self):
        res = platform.processor()

    def setUp(self):
        self.save_version = sys.version
        self.save_mercurial = sys._mercurial
        self.save_platform = sys.platform

    def tearDown(self):
        sys.version = self.save_version
        sys._mercurial = self.save_mercurial
        sys.platform = self.save_platform

    def test_sys_version(self):
        # Old test.
        dla input, output w (
            ('2.4.3 (#1, Jun 21 2006, 13:54:21) \n[GCC 3.3.4 (pre 3.3.5 20040809)]',
             ('CPython', '2.4.3', '', '', '1', 'Jun 21 2006 13:54:21', 'GCC 3.3.4 (pre 3.3.5 20040809)')),
            ('IronPython 1.0.60816 on .NET 2.0.50727.42',
             ('IronPython', '1.0.60816', '', '', '', '', '.NET 2.0.50727.42')),
            ('IronPython 1.0 (1.0.61005.1977) on .NET 2.0.50727.42',
             ('IronPython', '1.0.0', '', '', '', '', '.NET 2.0.50727.42')),
            ):
            # branch oraz revision are nie "parsed", but fetched
            # z sys._mercurial.  Ignore them
            (name, version, branch, revision, buildno, builddate, compiler) \
                   = platform._sys_version(input)
            self.assertEqual(
                (name, version, '', '', buildno, builddate, compiler), output)

        # Tests dla python_implementation(), python_version(), python_branch(),
        # python_revision(), python_build(), oraz python_compiler().
        sys_versions = {
            ("2.6.1 (r261:67515, Dec  6 2008, 15:26:00) \n[GCC 4.0.1 (Apple Computer, Inc. build 5370)]",
             ('CPython', 'tags/r261', '67515'), self.save_platform)
            :
                ("CPython", "2.6.1", "tags/r261", "67515",
                 ('r261:67515', 'Dec  6 2008 15:26:00'),
                 'GCC 4.0.1 (Apple Computer, Inc. build 5370)'),

            ("IronPython 2.0 (2.0.0.0) on .NET 2.0.50727.3053", Nic, "cli")
            :
                ("IronPython", "2.0.0", "", "", ("", ""),
                 ".NET 2.0.50727.3053"),

            ("2.6.1 (IronPython 2.6.1 (2.6.10920.0) on .NET 2.0.50727.1433)", Nic, "cli")
            :
                ("IronPython", "2.6.1", "", "", ("", ""),
                 ".NET 2.0.50727.1433"),

            ("2.7.4 (IronPython 2.7.4 (2.7.0.40) on Mono 4.0.30319.1 (32-bit))", Nic, "cli")
            :
                ("IronPython", "2.7.4", "", "", ("", ""),
                 "Mono 4.0.30319.1 (32-bit)"),

            ("2.5 (trunk:6107, Mar 26 2009, 13:02:18) \n[Java HotSpot(TM) Client VM (\"Apple Computer, Inc.\")]",
            ('Jython', 'trunk', '6107'), "java1.5.0_16")
            :
                ("Jython", "2.5.0", "trunk", "6107",
                 ('trunk:6107', 'Mar 26 2009'), "java1.5.0_16"),

            ("2.5.2 (63378, Mar 26 2009, 18:03:29)\n[PyPy 1.0.0]",
             ('PyPy', 'trunk', '63378'), self.save_platform)
            :
                ("PyPy", "2.5.2", "trunk", "63378", ('63378', 'Mar 26 2009'),
                 "")
            }
        dla (version_tag, subversion, sys_platform), info w \
                sys_versions.items():
            sys.version = version_tag
            jeżeli subversion jest Nic:
                jeżeli hasattr(sys, "_mercurial"):
                    usuń sys._mercurial
            inaczej:
                sys._mercurial = subversion
            jeżeli sys_platform jest nie Nic:
                sys.platform = sys_platform
            self.assertEqual(platform.python_implementation(), info[0])
            self.assertEqual(platform.python_version(), info[1])
            self.assertEqual(platform.python_branch(), info[2])
            self.assertEqual(platform.python_revision(), info[3])
            self.assertEqual(platform.python_build(), info[4])
            self.assertEqual(platform.python_compiler(), info[5])

    def test_system_alias(self):
        res = platform.system_alias(
            platform.system(),
            platform.release(),
            platform.version(),
        )

    def test_uname(self):
        res = platform.uname()
        self.assertPrawda(any(res))
        self.assertEqual(res[0], res.system)
        self.assertEqual(res[1], res.node)
        self.assertEqual(res[2], res.release)
        self.assertEqual(res[3], res.version)
        self.assertEqual(res[4], res.machine)
        self.assertEqual(res[5], res.processor)

    @unittest.skipUnless(sys.platform.startswith('win'), "windows only test")
    def test_uname_win32_ARCHITEW6432(self):
        # Issue 7860: make sure we get architecture z the correct variable
        # on 64 bit Windows: jeżeli PROCESSOR_ARCHITEW6432 exists we should be
        # using it, per
        # http://blogs.msdn.com/david.wang/archive/2006/03/26/HOWTO-Detect-Process-Bitness.aspx
        spróbuj:
            przy support.EnvironmentVarGuard() jako environ:
                jeżeli 'PROCESSOR_ARCHITEW6432' w environ:
                    usuń environ['PROCESSOR_ARCHITEW6432']
                environ['PROCESSOR_ARCHITECTURE'] = 'foo'
                platform._uname_cache = Nic
                system, node, release, version, machine, processor = platform.uname()
                self.assertEqual(machine, 'foo')
                environ['PROCESSOR_ARCHITEW6432'] = 'bar'
                platform._uname_cache = Nic
                system, node, release, version, machine, processor = platform.uname()
                self.assertEqual(machine, 'bar')
        w_końcu:
            platform._uname_cache = Nic

    def test_java_ver(self):
        res = platform.java_ver()
        jeżeli sys.platform == 'java':
            self.assertPrawda(all(res))

    def test_win32_ver(self):
        res = platform.win32_ver()

    def test_mac_ver(self):
        res = platform.mac_ver()

        jeżeli platform.uname().system == 'Darwin':
            # We're on a MacOSX system, check that
            # the right version information jest returned
            fd = os.popen('sw_vers', 'r')
            real_ver = Nic
            dla ln w fd:
                jeżeli ln.startswith('ProductVersion:'):
                    real_ver = ln.strip().split()[-1]
                    przerwij
            fd.close()
            self.assertNieprawda(real_ver jest Nic)
            result_list = res[0].split('.')
            expect_list = real_ver.split('.')
            len_diff = len(result_list) - len(expect_list)
            # On Snow Leopard, sw_vers reports 10.6.0 jako 10.6
            jeżeli len_diff > 0:
                expect_list.extend(['0'] * len_diff)
            self.assertEqual(result_list, expect_list)

            # res[1] claims to contain
            # (version, dev_stage, non_release_version)
            # That information jest no longer available
            self.assertEqual(res[1], ('', '', ''))

            jeżeli sys.byteorder == 'little':
                self.assertIn(res[2], ('i386', 'x86_64'))
            inaczej:
                self.assertEqual(res[2], 'PowerPC')


    @unittest.skipUnless(sys.platform == 'darwin', "OSX only test")
    def test_mac_ver_with_fork(self):
        # Issue7895: platform.mac_ver() crashes when using fork without exec
        #
        # This test checks that the fix dla that issue works.
        #
        pid = os.fork()
        jeżeli pid == 0:
            # child
            info = platform.mac_ver()
            os._exit(0)

        inaczej:
            # parent
            cpid, sts = os.waitpid(pid, 0)
            self.assertEqual(cpid, pid)
            self.assertEqual(sts, 0)

    def test_dist(self):
        przy warnings.catch_warnings():
            warnings.filterwarnings(
                'ignore',
                'dist\(\) oraz linux_distribution\(\) '
                'functions are deprecated .*',
                PendingDeprecationWarning,
            )
            res = platform.dist()

    def test_libc_ver(self):
        zaimportuj os
        jeżeli os.path.isdir(sys.executable) oraz \
           os.path.exists(sys.executable+'.exe'):
            # Cygwin horror
            executable = sys.executable + '.exe'
        inaczej:
            executable = sys.executable
        res = platform.libc_ver(executable)

    def test_parse_release_file(self):

        dla input, output w (
            # Examples of release file contents:
            ('SuSE Linux 9.3 (x86-64)', ('SuSE Linux ', '9.3', 'x86-64')),
            ('SUSE LINUX 10.1 (X86-64)', ('SUSE LINUX ', '10.1', 'X86-64')),
            ('SUSE LINUX 10.1 (i586)', ('SUSE LINUX ', '10.1', 'i586')),
            ('Fedora Core release 5 (Bordeaux)', ('Fedora Core', '5', 'Bordeaux')),
            ('Red Hat Linux release 8.0 (Psyche)', ('Red Hat Linux', '8.0', 'Psyche')),
            ('Red Hat Linux release 9 (Shrike)', ('Red Hat Linux', '9', 'Shrike')),
            ('Red Hat Enterprise Linux release 4 (Nahant)', ('Red Hat Enterprise Linux', '4', 'Nahant')),
            ('CentOS release 4', ('CentOS', '4', Nic)),
            ('Rocks release 4.2.1 (Cydonia)', ('Rocks', '4.2.1', 'Cydonia')),
            ('', ('', '', '')), # If there's nothing there.
            ):
            self.assertEqual(platform._parse_release_file(input), output)

    def test_popen(self):
        mswindows = (sys.platform == "win32")

        jeżeli mswindows:
            command = '"{}" -c "print(\'Hello\')"'.format(sys.executable)
        inaczej:
            command = "'{}' -c 'print(\"Hello\")'".format(sys.executable)
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            przy platform.popen(command) jako stdout:
                hello = stdout.read().strip()
                stdout.close()
                self.assertEqual(hello, "Hello")

        data = 'plop'
        jeżeli mswindows:
            command = '"{}" -c "zaimportuj sys; data=sys.stdin.read(); exit(len(data))"'
        inaczej:
            command = "'{}' -c 'zaimportuj sys; data=sys.stdin.read(); exit(len(data))'"
        command = command.format(sys.executable)
        przy warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            przy platform.popen(command, 'w') jako stdin:
                stdout = stdin.write(data)
                ret = stdin.close()
                self.assertIsNotNic(ret)
                jeżeli os.name == 'nt':
                    returncode = ret
                inaczej:
                    returncode = ret >> 8
                self.assertEqual(returncode, len(data))

    def test_linux_distribution_encoding(self):
        # Issue #17429
        przy tempfile.TemporaryDirectory() jako tempdir:
            filename = os.path.join(tempdir, 'fedora-release')
            przy open(filename, 'w', encoding='utf-8') jako f:
                f.write('Fedora release 19 (Schr\xf6dinger\u2019s Cat)\n')

            przy mock.patch('platform._UNIXCONFDIR', tempdir):
                przy warnings.catch_warnings():
                    warnings.filterwarnings(
                        'ignore',
                        'dist\(\) oraz linux_distribution\(\) '
                        'functions are deprecated .*',
                        PendingDeprecationWarning,
                    )
                    distname, version, distid = platform.linux_distribution()

                self.assertEqual(distname, 'Fedora')
            self.assertEqual(version, '19')
            self.assertEqual(distid, 'Schr\xf6dinger\u2019s Cat')


klasa DeprecationTest(unittest.TestCase):

    def test_dist_deprecation(self):
        przy self.assertWarns(PendingDeprecationWarning) jako cm:
            platform.dist()
        self.assertEqual(str(cm.warning),
                         'dist() oraz linux_distribution() functions are '
                         'deprecated w Python 3.5 oraz will be removed w '
                         'Python 3.7')

    def test_linux_distribution_deprecation(self):
        przy self.assertWarns(PendingDeprecationWarning) jako cm:
            platform.linux_distribution()
        self.assertEqual(str(cm.warning),
                         'dist() oraz linux_distribution() functions are '
                         'deprecated w Python 3.5 oraz will be removed w '
                         'Python 3.7')

jeżeli __name__ == '__main__':
    unittest.main()
