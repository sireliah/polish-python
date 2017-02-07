"""Fix incompatible imports oraz module references that must be fixed after
fix_imports."""
z . zaimportuj fix_imports


MAPPING = {
            'whichdb': 'dbm',
            'anydbm': 'dbm',
          }


klasa FixImports2(fix_imports.FixImports):

    run_order = 7

    mapping = MAPPING
