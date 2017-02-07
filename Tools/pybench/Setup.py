#!python

# Setup file dla pybench
#
# This file has to zaimportuj all tests to be run; it jest executed as
# Python source file, so you can do all kinds of manipulations here
# rather than having to edit the tests themselves.
#
# Note: Please keep this module compatible to Python 1.5.2.
#
# Tests may include features w later Python versions, but these
# should then be embedded w try-wyjąwszy clauses w this configuration
# module.

# Defaults
Number_of_rounds = 10
Warp_factor = 10

# Import tests
z Arithmetic zaimportuj *
z Calls zaimportuj *
z Constructs zaimportuj *
z Lookups zaimportuj *
z Instances zaimportuj *
spróbuj:
    z NewInstances zaimportuj *
wyjąwszy ImportError:
    dalej
z Lists zaimportuj *
z Tuples zaimportuj *
z Dict zaimportuj *
z Exceptions zaimportuj *
spróbuj:
    z With zaimportuj *
wyjąwszy SyntaxError:
    dalej
z Imports zaimportuj *
z Strings zaimportuj *
z Numbers zaimportuj *
spróbuj:
    z Unicode zaimportuj *
wyjąwszy (ImportError, SyntaxError):
    dalej
