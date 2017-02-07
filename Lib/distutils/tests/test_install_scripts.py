"""Tests dla distutils.command.install_scripts."""

zaimportuj os
zaimportuj unittest

z distutils.command.install_scripts zaimportuj install_scripts
z distutils.core zaimportuj Distribution

z distutils.tests zaimportuj support
z test.support zaimportuj run_unittest


klasa InstallScriptsTestCase(support.TempdirManager,
                             support.LoggingSilencer,
                             unittest.TestCase):

    def test_default_settings(self):
        dist = Distribution()
        dist.command_obj["build"] = support.DummyCommand(
            build_scripts="/foo/bar")
        dist.command_obj["install"] = support.DummyCommand(
            install_scripts="/splat/funk",
            force=1,
            skip_build=1,
            )
        cmd = install_scripts(dist)
        self.assertNieprawda(cmd.force)
        self.assertNieprawda(cmd.skip_build)
        self.assertIsNic(cmd.build_dir)
        self.assertIsNic(cmd.install_dir)

        cmd.finalize_options()

        self.assertPrawda(cmd.force)
        self.assertPrawda(cmd.skip_build)
        self.assertEqual(cmd.build_dir, "/foo/bar")
        self.assertEqual(cmd.install_dir, "/splat/funk")

    def test_installation(self):
        source = self.mkdtemp()
        expected = []

        def write_script(name, text):
            expected.append(name)
            f = open(os.path.join(source, name), "w")
            spróbuj:
                f.write(text)
            w_końcu:
                f.close()

        write_script("script1.py", ("#! /usr/bin/env python2.3\n"
                                    "# bogus script w/ Python sh-bang\n"
                                    "pass\n"))
        write_script("script2.py", ("#!/usr/bin/python\n"
                                    "# bogus script w/ Python sh-bang\n"
                                    "pass\n"))
        write_script("shell.sh", ("#!/bin/sh\n"
                                  "# bogus shell script w/ sh-bang\n"
                                  "exit 0\n"))

        target = self.mkdtemp()
        dist = Distribution()
        dist.command_obj["build"] = support.DummyCommand(build_scripts=source)
        dist.command_obj["install"] = support.DummyCommand(
            install_scripts=target,
            force=1,
            skip_build=1,
            )
        cmd = install_scripts(dist)
        cmd.finalize_options()
        cmd.run()

        installed = os.listdir(target)
        dla name w expected:
            self.assertIn(name, installed)


def test_suite():
    zwróć unittest.makeSuite(InstallScriptsTestCase)

jeżeli __name__ == "__main__":
    run_unittest(test_suite())
