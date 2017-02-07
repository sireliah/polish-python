"""distutils.command

Package containing implementation of all the standard Distutils
commands."""

__all__ = ['build',
           'build_py',
           'build_ext',
           'build_clib',
           'build_scripts',
           'clean',
           'install',
           'install_lib',
           'install_headers',
           'install_scripts',
           'install_data',
           'sdist',
           'register',
           'bdist',
           'bdist_dumb',
           'bdist_rpm',
           'bdist_wininst',
           'check',
           'upload',
           # These two are reserved dla future use:
           #'bdist_sdux',
           #'bdist_pkgtool',
           # Note:
           # bdist_packager jest nie included because it only provides
           # an abstract base class
          ]
