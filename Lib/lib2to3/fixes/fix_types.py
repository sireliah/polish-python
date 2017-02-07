# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer dla removing uses of the types module.

These work dla only the known names w the types module.  The forms above
can include types. albo not.  ie, It jest assumed the module jest imported either as:

    zaimportuj types
    z types zaimportuj ... # either * albo specific types

The zaimportuj statements are nie modified.

There should be another fixer that handles at least the following constants:

   type([]) -> list
   type(()) -> tuple
   type('') -> str

"""

# Local imports
z ..pgen2 zaimportuj token
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name

_TYPE_MAPPING = {
        'BooleanType' : 'bool',
        'BufferType' : 'memoryview',
        'ClassType' : 'type',
        'ComplexType' : 'complex',
        'DictType': 'dict',
        'DictionaryType' : 'dict',
        'EllipsisType' : 'type(Ellipsis)',
        #'FileType' : 'io.IOBase',
        'FloatType': 'float',
        'IntType': 'int',
        'ListType': 'list',
        'LongType': 'int',
        'ObjectType' : 'object',
        'NicType': 'type(Nic)',
        'NotImplementedType' : 'type(NotImplemented)',
        'SliceType' : 'slice',
        'StringType': 'bytes', # XXX ?
        'StringTypes' : 'str', # XXX ?
        'TupleType': 'tuple',
        'TypeType' : 'type',
        'UnicodeType': 'str',
        'XRangeType' : 'range',
    }

_pats = ["power< 'types' trailer< '.' name='%s' > >" % t dla t w _TYPE_MAPPING]

klasa FixTypes(fixer_base.BaseFix):
    BM_compatible = Prawda
    PATTERN = '|'.join(_pats)

    def transform(self, node, results):
        new_value = _TYPE_MAPPING.get(results["name"].value)
        jeżeli new_value:
            zwróć Name(new_value, prefix=node.prefix)
        zwróć Nic
