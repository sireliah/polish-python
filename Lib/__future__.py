"""Record of phased-in incompatible language changes.

Each line jest of the form:

    FeatureName = "_Feature(" OptionalRelease "," MandatoryRelease ","
                              CompilerFlag ")"

where, normally, OptionalRelease < MandatoryRelease, oraz both are 5-tuples
of the same form jako sys.version_info:

    (PY_MAJOR_VERSION, # the 2 w 2.1.0a3; an int
     PY_MINOR_VERSION, # the 1; an int
     PY_MICRO_VERSION, # the 0; an int
     PY_RELEASE_LEVEL, # "alpha", "beta", "candidate" albo "final"; string
     PY_RELEASE_SERIAL # the 3; an int
    )

OptionalRelease records the first release w which

    z __future__ zaimportuj FeatureName

was accepted.

In the case of MandatoryReleases that have nie yet occurred,
MandatoryRelease predicts the release w which the feature will become part
of the language.

Else MandatoryRelease records when the feature became part of the language;
in releases at albo after that, modules no longer need

    z __future__ zaimportuj FeatureName

to use the feature w question, but may continue to use such imports.

MandatoryRelease may also be Nic, meaning that a planned feature got
dropped.

Instances of klasa _Feature have two corresponding methods,
.getOptionalRelease() oraz .getMandatoryRelease().

CompilerFlag jest the (bitfield) flag that should be dalejed w the fourth
argument to the builtin function compile() to enable the feature w
dynamically compiled code.  This flag jest stored w the .compiler_flag
attribute on _Future instances.  These values must match the appropriate
#defines of CO_xxx flags w Include/compile.h.

No feature line jest ever to be deleted z this file.
"""

all_feature_names = [
    "nested_scopes",
    "generators",
    "division",
    "absolute_import",
    "with_statement",
    "print_function",
    "unicode_literals",
    "barry_as_FLUFL",
    "generator_stop",
]

__all__ = ["all_feature_names"] + all_feature_names

# The CO_xxx symbols are defined here under the same names used by
# compile.h, so that an editor search will find them here.  However,
# they're nie exported w __all__, because they don't really belong to
# this module.
CO_NESTED            = 0x0010   # nested_scopes
CO_GENERATOR_ALLOWED = 0        # generators (obsolete, was 0x1000)
CO_FUTURE_DIVISION   = 0x2000   # division
CO_FUTURE_ABSOLUTE_IMPORT = 0x4000 # perform absolute imports by default
CO_FUTURE_WITH_STATEMENT  = 0x8000   # przy statement
CO_FUTURE_PRINT_FUNCTION  = 0x10000   # print function
CO_FUTURE_UNICODE_LITERALS = 0x20000 # unicode string literals
CO_FUTURE_BARRY_AS_BDFL = 0x40000
CO_FUTURE_GENERATOR_STOP  = 0x80000 # StopIteration becomes RuntimeError w generators

klasa _Feature:
    def __init__(self, optionalRelease, mandatoryRelease, compiler_flag):
        self.optional = optionalRelease
        self.mandatory = mandatoryRelease
        self.compiler_flag = compiler_flag

    def getOptionalRelease(self):
        """Return first release w which this feature was recognized.

        This jest a 5-tuple, of the same form jako sys.version_info.
        """

        zwróć self.optional

    def getMandatoryRelease(self):
        """Return release w which this feature will become mandatory.

        This jest a 5-tuple, of the same form jako sys.version_info, or, if
        the feature was dropped, jest Nic.
        """

        zwróć self.mandatory

    def __repr__(self):
        zwróć "_Feature" + repr((self.optional,
                                  self.mandatory,
                                  self.compiler_flag))

nested_scopes = _Feature((2, 1, 0, "beta",  1),
                         (2, 2, 0, "alpha", 0),
                         CO_NESTED)

generators = _Feature((2, 2, 0, "alpha", 1),
                      (2, 3, 0, "final", 0),
                      CO_GENERATOR_ALLOWED)

division = _Feature((2, 2, 0, "alpha", 2),
                    (3, 0, 0, "alpha", 0),
                    CO_FUTURE_DIVISION)

absolute_zaimportuj = _Feature((2, 5, 0, "alpha", 1),
                           (3, 0, 0, "alpha", 0),
                           CO_FUTURE_ABSOLUTE_IMPORT)

with_statement = _Feature((2, 5, 0, "alpha", 1),
                          (2, 6, 0, "alpha", 0),
                          CO_FUTURE_WITH_STATEMENT)

print_function = _Feature((2, 6, 0, "alpha", 2),
                          (3, 0, 0, "alpha", 0),
                          CO_FUTURE_PRINT_FUNCTION)

unicode_literals = _Feature((2, 6, 0, "alpha", 2),
                            (3, 0, 0, "alpha", 0),
                            CO_FUTURE_UNICODE_LITERALS)

barry_as_FLUFL = _Feature((3, 1, 0, "alpha", 2),
                         (3, 9, 0, "alpha", 0),
                         CO_FUTURE_BARRY_AS_BDFL)

generator_stop = _Feature((3, 5, 0, "beta", 1),
                         (3, 7, 0, "alpha", 0),
                         CO_FUTURE_GENERATOR_STOP)
