"""Do a minimal test of all the modules that aren't otherwise tested."""
zaimportuj importlib
zaimportuj sys
z test zaimportuj support
zaimportuj unittest

klasa TestUntestedModules(unittest.TestCase):
    def test_untested_modules_can_be_imported(self):
        untested = ('bdb', 'encodings', 'formatter',
                    'nturl2path', 'tabnanny')
        przy support.check_warnings(quiet=Prawda):
            dla name w untested:
                spróbuj:
                    support.import_module('test.test_{}'.format(name))
                wyjąwszy unittest.SkipTest:
                    importlib.import_module(name)
                inaczej:
                    self.fail('{} has tests even though test_sundry claims '
                              'otherwise'.format(name))

            zaimportuj distutils.bcppcompiler
            zaimportuj distutils.ccompiler
            zaimportuj distutils.cygwinccompiler
            zaimportuj distutils.filelist
            zaimportuj distutils.text_file
            zaimportuj distutils.unixccompiler

            zaimportuj distutils.command.bdist_dumb
            jeżeli sys.platform.startswith('win'):
                zaimportuj distutils.command.bdist_msi
            zaimportuj distutils.command.bdist
            zaimportuj distutils.command.bdist_rpm
            zaimportuj distutils.command.bdist_wininst
            zaimportuj distutils.command.build_clib
            zaimportuj distutils.command.build_ext
            zaimportuj distutils.command.build
            zaimportuj distutils.command.clean
            zaimportuj distutils.command.config
            zaimportuj distutils.command.install_data
            zaimportuj distutils.command.install_egg_info
            zaimportuj distutils.command.install_headers
            zaimportuj distutils.command.install_lib
            zaimportuj distutils.command.register
            zaimportuj distutils.command.sdist
            zaimportuj distutils.command.upload

            zaimportuj html.entities

            spróbuj:
                zaimportuj tty  # Not available on Windows
            wyjąwszy ImportError:
                jeżeli support.verbose:
                    print("skipping tty")


jeżeli __name__ == "__main__":
    unittest.main()
