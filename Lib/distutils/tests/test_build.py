"""Tests dla distutils.command.build."""
zaimportuj unittest
zaimportuj os
zaimportuj sys
z test.support zaimportuj run_unittest

z distutils.command.build zaimportuj build
z distutils.tests zaimportuj support
z sysconfig zaimportuj get_platform

klasa BuildTestCase(support.TempdirManager,
                    support.LoggingSilencer,
                    unittest.TestCase):

    def test_finalize_options(self):
        pkg_dir, dist = self.create_dist()
        cmd = build(dist)
        cmd.finalize_options()

        # jeżeli nie specified, plat_name gets the current platform
        self.assertEqual(cmd.plat_name, get_platform())

        # build_purelib jest build + lib
        wanted = os.path.join(cmd.build_base, 'lib')
        self.assertEqual(cmd.build_purelib, wanted)

        # build_platlib jest 'build/lib.platform-x.x[-pydebug]'
        # examples:
        #   build/lib.macosx-10.3-i386-2.7
        plat_spec = '.%s-%s' % (cmd.plat_name, sys.version[0:3])
        jeżeli hasattr(sys, 'gettotalrefcount'):
            self.assertPrawda(cmd.build_platlib.endswith('-pydebug'))
            plat_spec += '-pydebug'
        wanted = os.path.join(cmd.build_base, 'lib' + plat_spec)
        self.assertEqual(cmd.build_platlib, wanted)

        # by default, build_lib = build_purelib
        self.assertEqual(cmd.build_lib, cmd.build_purelib)

        # build_temp jest build/temp.<plat>
        wanted = os.path.join(cmd.build_base, 'temp' + plat_spec)
        self.assertEqual(cmd.build_temp, wanted)

        # build_scripts jest build/scripts-x.x
        wanted = os.path.join(cmd.build_base, 'scripts-' +  sys.version[0:3])
        self.assertEqual(cmd.build_scripts, wanted)

        # executable jest os.path.normpath(sys.executable)
        self.assertEqual(cmd.executable, os.path.normpath(sys.executable))

def test_suite():
    zwróć unittest.makeSuite(BuildTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
