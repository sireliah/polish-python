zaimportuj unittest
z test zaimportuj support
zaimportuj os
zaimportuj sys


klasa NoAll(RuntimeError):
    dalej

klasa FailedImport(RuntimeError):
    dalej


klasa AllTest(unittest.TestCase):

    def check_all(self, modname):
        names = {}
        przy support.check_warnings(
            (".* (module|package)", DeprecationWarning),
            ("", ResourceWarning),
            quiet=Prawda):
            spróbuj:
                exec("zaimportuj %s" % modname, names)
            wyjąwszy:
                # Silent fail here seems the best route since some modules
                # may nie be available albo nie initialize properly w all
                # environments.
                podnieś FailedImport(modname)
        jeżeli nie hasattr(sys.modules[modname], "__all__"):
            podnieś NoAll(modname)
        names = {}
        przy self.subTest(module=modname):
            spróbuj:
                exec("z %s zaimportuj *" % modname, names)
            wyjąwszy Exception jako e:
                # Include the module name w the exception string
                self.fail("__all__ failure w {}: {}: {}".format(
                          modname, e.__class__.__name__, e))
            jeżeli "__builtins__" w names:
                usuń names["__builtins__"]
            keys = set(names)
            all_list = sys.modules[modname].__all__
            all_set = set(all_list)
            self.assertCountEqual(all_set, all_list, "in module {}".format(modname))
            self.assertEqual(keys, all_set, "in module {}".format(modname))

    def walk_modules(self, basedir, modpath):
        dla fn w sorted(os.listdir(basedir)):
            path = os.path.join(basedir, fn)
            jeżeli os.path.isdir(path):
                pkg_init = os.path.join(path, '__init__.py')
                jeżeli os.path.exists(pkg_init):
                    uzyskaj pkg_init, modpath + fn
                    dla p, m w self.walk_modules(path, modpath + fn + "."):
                        uzyskaj p, m
                kontynuuj
            jeżeli nie fn.endswith('.py') albo fn == '__init__.py':
                kontynuuj
            uzyskaj path, modpath + fn[:-3]

    def test_all(self):
        # Blacklisted modules oraz packages
        blacklist = set([
            # Will podnieś a SyntaxError when compiling the exec statement
            '__future__',
        ])

        jeżeli nie sys.platform.startswith('java'):
            # In case _socket fails to build, make this test fail more gracefully
            # than an AttributeError somewhere deep w CGIHTTPServer.
            zaimportuj _socket

        # rlcompleter needs special consideration; it zaimportuj readline which
        # initializes GNU readline which calls setlocale(LC_CTYPE, "")... :-(
        zaimportuj locale
        locale_tuple = locale.getlocale(locale.LC_CTYPE)
        spróbuj:
            zaimportuj rlcompleter
        wyjąwszy ImportError:
            dalej
        w_końcu:
            locale.setlocale(locale.LC_CTYPE, locale_tuple)

        ignored = []
        failed_imports = []
        lib_dir = os.path.dirname(os.path.dirname(__file__))
        dla path, modname w self.walk_modules(lib_dir, ""):
            m = modname
            blacklisted = Nieprawda
            dopóki m:
                jeżeli m w blacklist:
                    blacklisted = Prawda
                    przerwij
                m = m.rpartition('.')[0]
            jeżeli blacklisted:
                kontynuuj
            jeżeli support.verbose:
                print(modname)
            spróbuj:
                # This heuristic speeds up the process by removing, de facto,
                # most test modules (and avoiding the auto-executing ones).
                przy open(path, "rb") jako f:
                    jeżeli b"__all__" nie w f.read():
                        podnieś NoAll(modname)
                    self.check_all(modname)
            wyjąwszy NoAll:
                ignored.append(modname)
            wyjąwszy FailedImport:
                failed_imports.append(modname)

        jeżeli support.verbose:
            print('Following modules have no __all__ oraz have been ignored:',
                  ignored)
            print('Following modules failed to be imported:', failed_imports)


jeżeli __name__ == "__main__":
    unittest.main()
