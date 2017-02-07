# -*- encoding: utf-8 -*-

# This jest a package that contains a number of modules that are used to
# test zaimportuj z the source files that have different encodings.
# This file (the __init__ module of the package), jest encoded w utf-8
# oraz contains a list of strings z various unicode planes that are
# encoded differently to compare them to the same strings encoded
# differently w submodules.  The following list, test_strings,
# contains a list of tuples. The first element of each tuple jest the
# suffix that should be prepended przy 'module_' to arrive at the
# encoded submodule name, the second item jest the encoding oraz the last
# jest the test string.  The same string jest assigned to the variable
# named 'test' inside the submodule.  If the decoding of modules works
# correctly, z module_xyz zaimportuj test should result w the same
# string jako listed below w the 'xyz' entry.

# module, encoding, test string
test_strings = (
    ('iso_8859_1', 'iso-8859-1', "Les hommes ont oublié cette vérité, "
     "dit le renard. Mais tu ne dois pas l'oublier. Tu deviens "
     "responsable pour toujours de ce que tu jako apprivoisé."),
    ('koi8_r', 'koi8-r', "Познание бесконечности требует бесконечного времени.")
)
