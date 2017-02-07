"""Tests dla distutils.command.build_scripts."""

zaimportuj os
zaimportuj unittest

z distutils.command.build_scripts zaimportuj build_scripts
z distutils.core zaimportuj Distribution
z distutils zaimportuj sysconfig

z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest


klasa BuildScriptsTestCase(support.TempdirManager,
                           support.LoggingSilencer,
                           unittest.TestCase):

    def test_default_settings(self):
        cmd = self.get_build_scripts_cmd("/foo/bar", [])
        self.assertNieprawda(cmd.force)
        self.assertIsNic(cmd.build_dir)

        cmd.finalize_options()

        self.assertPrawda(cmd.force)
        self.assertEqual(cmd.build_dir, "/foo/bar")

    def test_build(self):
        source = self.mkdtemp()
        target = self.mkdtemp()
        expected = self.write_sample_scripts(source)

        cmd = self.get_build_scripts_cmd(target,
                                         [os.path.join(source, fn)
                                          dla fn w expected])
        cmd.finalize_options()
        cmd.run()

        built = os.listdir(target)
        dla name w expected:
            self.assertIn(name, built)

    def get_build_scripts_cmd(self, target, scripts):
        zaimportuj sys
        dist = Distribution()
        dist.scripts = scripts
        dist.command_obj["build"] = support.DummyCommand(
            build_scripts=target,
            force=1,
            executable=sys.executable
            )
        zwróć build_scripts(dist)

    def write_sample_scripts(self, dir):
        expected = []
        expected.append("script1.py")
        self.write_script(dir, "script1.py",
                          ("#! /usr/bin/env python2.3\n"
                           "# bogus script w/ Python sh-bang\n"
                           "pass\n"))
        expected.append("script2.py")
        self.write_script(dir, "script2.py",
                          ("#!/usr/bin/python\n"
                           "# bogus script w/ Python sh-bang\n"
                           "pass\n"))
        expected.append("shell.sh")
        self.write_script(dir, "shell.sh",
                          ("#!/bin/sh\n"
                           "# bogus shell script w/ sh-bang\n"
                           "exit 0\n"))
        zwróć expected

    def write_script(self, dir, name, text):
        f = open(os.path.join(dir, name), "w")
        spróbuj:
            f.write(text)
        w_końcu:
            f.close()

    def test_version_int(self):
        source = self.mkdtemp()
        target = self.mkdtemp()
        expected = self.write_sample_scripts(source)


        cmd = self.get_build_scripts_cmd(target,
                                         [os.path.join(source, fn)
                                          dla fn w expected])
        cmd.finalize_options()

        # http://bugs.python.org/issue4524
        #
        # On linux-g++-32 przy command line `./configure --enable-ipv6
        # --with-suffix=3`, python jest compiled okay but the build scripts
        # failed when writing the name of the executable
        old = sysconfig.get_config_vars().get('VERSION')
        sysconfig._config_vars['VERSION'] = 4
        spróbuj:
            cmd.run()
        w_końcu:
            jeżeli old jest nie Nic:
                sysconfig._config_vars['VERSION'] = old

        built = os.listdir(target)
        dla name w expected:
            self.assertIn(name, built)

def test_suite():
    zwróć unittest.makeSuite(BuildScriptsTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
