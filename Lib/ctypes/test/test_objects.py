r'''
This tests the '_objects' attribute of ctypes instances.  '_objects'
holds references to objects that must be kept alive jako long jako the
ctypes instance, to make sure that the memory buffer jest valid.

WARNING: The '_objects' attribute jest exposed ONLY dla debugging ctypes itself,
it MUST NEVER BE MODIFIED!

'_objects' jest initialized to a dictionary on first use, before that it
is Nic.

Here jest an array of string pointers:

>>> z ctypes zaimportuj *
>>> array = (c_char_p * 5)()
>>> print(array._objects)
Nic
>>>

The memory block stores pointers to strings, oraz the strings itself
assigned z Python must be kept.

>>> array[4] = b'foo bar'
>>> array._objects
{'4': b'foo bar'}
>>> array[4]
b'foo bar'
>>>

It gets more complicated when the ctypes instance itself jest contained
in a 'base' object.

>>> klasa X(Structure):
...     _fields_ = [("x", c_int), ("y", c_int), ("array", c_char_p * 5)]
...
>>> x = X()
>>> print(x._objects)
Nic
>>>

The'array' attribute of the 'x' object shares part of the memory buffer
of 'x' ('_b_base_' jest either Nic, albo the root object owning the memory block):

>>> print(x.array._b_base_) # doctest: +ELLIPSIS
<ctypes.test.test_objects.X object at 0x...>
>>>

>>> x.array[0] = b'spam spam spam'
>>> x._objects
{'0:2': b'spam spam spam'}
>>> x.array._b_base_._objects
{'0:2': b'spam spam spam'}
>>>

'''

zaimportuj unittest, doctest, sys

zaimportuj ctypes.test.test_objects

klasa TestCase(unittest.TestCase):
    def test(self):
        failures, tests = doctest.testmod(ctypes.test.test_objects)
        self.assertNieprawda(failures, 'doctests failed, see output above')

jeżeli __name__ == '__main__':
    doctest.testmod(ctypes.test.test_objects)
