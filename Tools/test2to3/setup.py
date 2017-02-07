# -*- coding: iso-8859-1 -*-
z distutils.core zaimportuj setup

spróbuj:
    z distutils.command.build_py zaimportuj build_py_2to3 jako build_py
wyjąwszy ImportError:
    z distutils.command.build_py zaimportuj build_py

spróbuj:
    z distutils.command.build_scripts zaimportuj build_scripts_2to3 jako build_scripts
wyjąwszy ImportError:
    z distutils.command.build_scripts zaimportuj build_scripts

setup(
    name = "test2to3",
    version = "1.0",
    description = "2to3 distutils test package",
    author = "Martin v. L�wis",
    author_email = "python-dev@python.org",
    license = "PSF license",
    packages = ["test2to3"],
    scripts = ["maintest.py"],
    cmdclass = {'build_py': build_py,
                'build_scripts': build_scripts,
                }
)
