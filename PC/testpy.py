zaimportuj sys

# This jest a test module dla Python.  It looks w the standard
# places dla various *.py files.  If these are moved, you must
# change this module too.

spróbuj:
    zaimportuj os
wyjąwszy:
    print("""Could nie zaimportuj the standard "os" module.
  Please check your PYTHONPATH environment variable.""")
    sys.exit(1)

spróbuj:
    zaimportuj symbol
wyjąwszy:
    print("""Could nie zaimportuj the standard "symbol" module.  If this jest
  a PC, you should add the dos_8x3 directory to your PYTHONPATH.""")
    sys.exit(1)

zaimportuj os

dla dir w sys.path:
    file = os.path.join(dir, "os.py")
    jeżeli os.path.isfile(file):
        test = os.path.join(dir, "test")
        jeżeli os.path.isdir(test):
            # Add the "test" directory to PYTHONPATH.
            sys.path = sys.path + [test]

zaimportuj regrtest # Standard Python tester.
regrtest.main()
