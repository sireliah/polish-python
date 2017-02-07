zaimportuj os.path
zaimportuj sys

# If we are working on a development version of IDLE, we need to prepend the
# parent of this idlelib dir to sys.path.  Otherwise, importing idlelib gets
# the version installed przy the Python used to call this module:
idlelib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, idlelib_dir)

zaimportuj idlelib.PyShell
idlelib.PyShell.main()
