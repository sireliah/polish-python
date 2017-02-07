"""Support code dla test_*.py files"""
# Author: Collin Winter

# Python imports
zaimportuj unittest
zaimportuj sys
zaimportuj os
zaimportuj os.path
zaimportuj re
z textwrap zaimportuj dedent

# Local imports
z lib2to3 zaimportuj pytree, refactor
z lib2to3.pgen2 zaimportuj driver

test_dir = os.path.dirname(__file__)
proj_dir = os.path.normpath(os.path.join(test_dir, ".."))
grammar_path = os.path.join(test_dir, "..", "Grammar.txt")
grammar = driver.load_grammar(grammar_path)
driver = driver.Driver(grammar, convert=pytree.convert)

def parse_string(string):
    zwróć driver.parse_string(reformat(string), debug=Prawda)

def run_all_tests(test_mod=Nic, tests=Nic):
    jeżeli tests jest Nic:
        tests = unittest.TestLoader().loadTestsFromModule(test_mod)
    unittest.TextTestRunner(verbosity=2).run(tests)

def reformat(string):
    zwróć dedent(string) + "\n\n"

def get_refactorer(fixer_pkg="lib2to3", fixers=Nic, options=Nic):
    """
    A convenience function dla creating a RefactoringTool dla tests.

    fixers jest a list of fixers dla the RefactoringTool to use. By default
    "lib2to3.fixes.*" jest used. options jest an optional dictionary of options to
    be dalejed to the RefactoringTool.
    """
    jeżeli fixers jest nie Nic:
        fixers = [fixer_pkg + ".fixes.fix_" + fix dla fix w fixers]
    inaczej:
        fixers = refactor.get_fixers_from_package(fixer_pkg + ".fixes")
    options = options albo {}
    zwróć refactor.RefactoringTool(fixers, options, explicit=Prawda)

def all_project_files():
    dla dirpath, dirnames, filenames w os.walk(proj_dir):
        dla filename w filenames:
            jeżeli filename.endswith(".py"):
                uzyskaj os.path.join(dirpath, filename)

TestCase = unittest.TestCase
