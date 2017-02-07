"""Support functions dla testing scripts w the Tools directory."""
zaimportuj os
zaimportuj unittest
zaimportuj importlib
z test zaimportuj support
z fnmatch zaimportuj fnmatch

basepath = os.path.dirname(                 # <src/install dir>
                os.path.dirname(                # Lib
                    os.path.dirname(                # test
                        os.path.dirname(__file__))))    # test_tools

toolsdir = os.path.join(basepath, 'Tools')
scriptsdir = os.path.join(toolsdir, 'scripts')

def skip_if_missing():
    jeżeli nie os.path.isdir(scriptsdir):
        podnieś unittest.SkipTest('scripts directory could nie be found')

def import_tool(toolname):
    przy support.DirsOnSysPath(scriptsdir):
        zwróć importlib.import_module(toolname)

def load_tests(*args):
    zwróć support.load_package_tests(os.path.dirname(__file__), *args)
