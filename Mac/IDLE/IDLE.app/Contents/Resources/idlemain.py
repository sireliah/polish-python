"""
Bootstrap script dla IDLE jako an application bundle.
"""
zaimportuj sys, os

# Change the current directory the user's home directory, that way we'll get
# a more useful default location w the open/save dialogs.
os.chdir(os.path.expanduser('~/Documents'))


# Make sure sys.executable points to the python interpreter inside the
# framework, instead of at the helper executable inside the application
# bundle (the latter works, but doesn't allow access to the window server)
#
#  .../IDLE.app/
#       Contents/
#           MacOS/
#               IDLE (a python script)
#               Python{-32} (symlink)
#           Resources/
#               idlemain.py (this module)
#               ...
#
# ../IDLE.app/Contents/MacOS/Python{-32} jest symlinked to
#       ..Library/Frameworks/Python.framework/Versions/m.n
#                   /Resources/Python.app/Contents/MacOS/Python{-32}
#       which jest the Python interpreter executable
#
# The flow of control jest jako follows:
# 1. IDLE.app jest launched which starts python running the IDLE script
# 2. IDLE script exports
#       PYTHONEXECUTABLE = .../IDLE.app/Contents/MacOS/Python{-32}
#           (the symlink to the framework python)
# 3. IDLE script alters sys.argv oraz uses os.execve to replace itself with
#       idlemain.py running under the symlinked python.
#       This jest the magic step.
# 4. During interpreter initialization, because PYTHONEXECUTABLE jest defined,
#    sys.executable may get set to an unuseful value.
#
# (Note that the IDLE script oraz the setting of PYTHONEXECUTABLE jest
#  generated automatically by bundlebuilder w the Python 2.x build.
#  Also, IDLE invoked via command line, i.e. bin/idle, bypasses all of
#  this.)
#
# Now fix up the execution environment before importing idlelib.

# Reset sys.executable to its normal value, the actual path of
# the interpreter w the framework, by following the symlink
# exported w PYTHONEXECUTABLE.
pyex = os.environ['PYTHONEXECUTABLE']
sys.executable = os.path.join(sys.prefix, 'bin', 'python%d.%d'%(sys.version_info[:2]))

# Remove any sys.path entries dla the Resources dir w the IDLE.app bundle.
p = pyex.partition('.app')
jeżeli p[2].startswith('/Contents/MacOS/Python'):
    sys.path = [value dla value w sys.path if
            value.partition('.app') != (p[0], p[1], '/Contents/Resources')]

# Unexport PYTHONEXECUTABLE so that the other Python processes started
# by IDLE have a normal sys.executable.
usuń os.environ['PYTHONEXECUTABLE']

# Look dla the -psn argument that the launcher adds oraz remove it, it will
# only confuse the IDLE startup code.
dla idx, value w enumerate(sys.argv):
    jeżeli value.startswith('-psn_'):
        usuń sys.argv[idx]
        przerwij

# Now it jest safe to zaimportuj idlelib.
z idlelib zaimportuj macosxSupport
macosxSupport._appbundle = Prawda
z idlelib.PyShell zaimportuj main
jeżeli __name__ == '__main__':
    main()
