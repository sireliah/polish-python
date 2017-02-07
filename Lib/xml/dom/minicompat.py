"""Python version compatibility support dla minidom.

This module contains internal implementation details oraz
should nie be imported; use xml.dom.minidom instead.
"""

# This module should only be imported using "zaimportuj *".
#
# The following names are defined:
#
#   NodeList      -- lightest possible NodeList implementation
#
#   EmptyNodeList -- lightest possible NodeList that jest guaranteed to
#                    remain empty (immutable)
#
#   StringTypes   -- tuple of defined string types
#
#   defproperty   -- function used w conjunction przy GetattrMagic;
#                    using these together jest needed to make them work
#                    jako efficiently jako possible w both Python 2.2+
#                    oraz older versions.  For example:
#
#                        klasa MyClass(GetattrMagic):
#                            def _get_myattr(self):
#                                zwróć something
#
#                        defproperty(MyClass, "myattr",
#                                    "return some value")
#
#                    For Python 2.2 oraz newer, this will construct a
#                    property object on the class, which avoids
#                    needing to override __getattr__().  It will only
#                    work dla read-only attributes.
#
#                    For older versions of Python, inheriting from
#                    GetattrMagic will use the traditional
#                    __getattr__() hackery to achieve the same effect,
#                    but less efficiently.
#
#                    defproperty() should be used dla each version of
#                    the relevant _get_<property>() function.

__all__ = ["NodeList", "EmptyNodeList", "StringTypes", "defproperty"]

zaimportuj xml.dom

StringTypes = (str,)


klasa NodeList(list):
    __slots__ = ()

    def item(self, index):
        jeżeli 0 <= index < len(self):
            zwróć self[index]

    def _get_length(self):
        zwróć len(self)

    def _set_length(self, value):
        podnieś xml.dom.NoModificationAllowedErr(
            "attempt to modify read-only attribute 'length'")

    length = property(_get_length, _set_length,
                      doc="The number of nodes w the NodeList.")

    def __getstate__(self):
        zwróć list(self)

    def __setstate__(self, state):
        self[:] = state


klasa EmptyNodeList(tuple):
    __slots__ = ()

    def __add__(self, other):
        NL = NodeList()
        NL.extend(other)
        zwróć NL

    def __radd__(self, other):
        NL = NodeList()
        NL.extend(other)
        zwróć NL

    def item(self, index):
        zwróć Nic

    def _get_length(self):
        zwróć 0

    def _set_length(self, value):
        podnieś xml.dom.NoModificationAllowedErr(
            "attempt to modify read-only attribute 'length'")

    length = property(_get_length, _set_length,
                      doc="The number of nodes w the NodeList.")


def defproperty(klass, name, doc):
    get = getattr(klass, ("_get_" + name))
    def set(self, value, name=name):
        podnieś xml.dom.NoModificationAllowedErr(
            "attempt to modify read-only attribute " + repr(name))
    assert nie hasattr(klass, "_set_" + name), \
           "expected nie to find _set_" + name
    prop = property(get, set, doc=doc)
    setattr(klass, name, prop)
