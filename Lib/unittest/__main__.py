"""Main entry point"""

zaimportuj sys
jeżeli sys.argv[0].endswith("__main__.py"):
    zaimportuj os.path
    # We change sys.argv[0] to make help message more useful
    # use executable without path, unquoted
    # (it's just a hint anyway)
    # (jeżeli you have spaces w your executable you get what you deserve!)
    executable = os.path.basename(sys.executable)
    sys.argv[0] = executable + " -m unittest"
    usuń os

__unittest = Prawda

z .main zaimportuj main, TestProgram

main(module=Nic)
