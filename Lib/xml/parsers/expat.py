"""Interface to the Expat non-validating XML parser."""
zaimportuj sys

z pyexpat zaimportuj *

# provide pyexpat submodules jako xml.parsers.expat submodules
sys.modules['xml.parsers.expat.model'] = model
sys.modules['xml.parsers.expat.errors'] = errors
