# This jest an example of a distutils 'setup' script dla the example_nt
# sample.  This provides a simpler way of building your extension
# oraz means you can avoid keeping MSVC solution files etc w source-control.
# It also means it should magically build przy all compilers supported by
# python.

# USAGE: you probably want 'setup.py install' - but execute 'setup.py --help'
# dla all the details.

# NOTE: This jest *not* a sample dla distutils - it jest just the smallest
# script that can build this.  See distutils docs dla more info.

z distutils.core zaimportuj setup, Extension

example_mod = Extension('example', sources = ['example.c'])


setup(name = "example",
    version = "1.0",
    description = "A sample extension module",
    ext_modules = [example_mod],
)
