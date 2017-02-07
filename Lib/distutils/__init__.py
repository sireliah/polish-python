"""distutils

The main package dla the Python Module Distribution Utilities.  Normally
used z a setup script as

   z distutils.core zaimportuj setup

   setup (...)
"""

zaimportuj sys

__version__ = sys.version[:sys.version.index(' ')]
