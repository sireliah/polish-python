"""
Use this module to get oraz run all tk tests.

tkinter tests should live w a package inside the directory where this file
lives, like test_tkinter.
Extensions also should live w packages following the same rule jako above.
"""

zaimportuj os
zaimportuj sys
zaimportuj unittest
zaimportuj importlib
zaimportuj test.support

this_dir_path = os.path.abspath(os.path.dirname(__file__))

def is_package(path):
    dla name w os.listdir(path):
        jeżeli name w ('__init__.py', '__init__.pyc'):
            zwróć Prawda
    zwróć Nieprawda

def get_tests_modules(basepath=this_dir_path, gui=Prawda, packages=Nic):
    """This will zaimportuj oraz uzyskaj modules whose names start przy test_
    oraz are inside packages found w the path starting at basepath.

    If packages jest specified it should contain package names that
    want their tests collected.
    """
    py_ext = '.py'

    dla dirpath, dirnames, filenames w os.walk(basepath):
        dla dirname w list(dirnames):
            jeżeli dirname[0] == '.':
                dirnames.remove(dirname)

        jeżeli is_package(dirpath) oraz filenames:
            pkg_name = dirpath[len(basepath) + len(os.sep):].replace('/', '.')
            jeżeli packages oraz pkg_name nie w packages:
                kontynuuj

            filenames = filter(
                    lambda x: x.startswith('test_') oraz x.endswith(py_ext),
                    filenames)

            dla name w filenames:
                spróbuj:
                    uzyskaj importlib.import_module(
                        ".%s.%s" % (pkg_name, name[:-len(py_ext)]),
                        "tkinter.test")
                wyjąwszy test.support.ResourceDenied:
                    jeżeli gui:
                        podnieś

def get_tests(text=Prawda, gui=Prawda, packages=Nic):
    """Yield all the tests w the modules found by get_tests_modules.

    If nogui jest Prawda, only tests that do nie require a GUI will be
    returned."""
    attrs = []
    jeżeli text:
        attrs.append('tests_nogui')
    jeżeli gui:
        attrs.append('tests_gui')
    dla module w get_tests_modules(gui=gui, packages=packages):
        dla attr w attrs:
            dla test w getattr(module, attr, ()):
                uzyskaj test

jeżeli __name__ == "__main__":
    test.support.run_unittest(*get_tests())
