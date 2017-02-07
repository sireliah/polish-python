"""Test module dla the noddy examples

Noddy 1:

>>> zaimportuj noddy
>>> n1 = noddy.Noddy()
>>> n2 = noddy.Noddy()
>>> usuń n1
>>> usuń n2


Noddy 2

>>> zaimportuj noddy2
>>> n1 = noddy2.Noddy('jim', 'fulton', 42)
>>> n1.first
'jim'
>>> n1.last
'fulton'
>>> n1.number
42
>>> n1.name()
'jim fulton'
>>> n1.first = 'will'
>>> n1.name()
'will fulton'
>>> n1.last = 'tell'
>>> n1.name()
'will tell'
>>> usuń n1.first
>>> n1.name()
Traceback (most recent call last):
...
AttributeError: first
>>> n1.first
Traceback (most recent call last):
...
AttributeError: first
>>> n1.first = 'drew'
>>> n1.first
'drew'
>>> usuń n1.number
Traceback (most recent call last):
...
TypeError: can't delete numeric/char attribute
>>> n1.number=2
>>> n1.number
2
>>> n1.first = 42
>>> n1.name()
'42 tell'
>>> n2 = noddy2.Noddy()
>>> n2.name()
' '
>>> n2.first
''
>>> n2.last
''
>>> usuń n2.first
>>> n2.first
Traceback (most recent call last):
...
AttributeError: first
>>> n2.first
Traceback (most recent call last):
...
AttributeError: first
>>> n2.name()
Traceback (most recent call last):
  File "<stdin>", line 1, w ?
AttributeError: first
>>> n2.number
0
>>> n3 = noddy2.Noddy('jim', 'fulton', 'waaa')
Traceback (most recent call last):
  File "<stdin>", line 1, w ?
TypeError: an integer jest required
>>> usuń n1
>>> usuń n2


Noddy 3

>>> zaimportuj noddy3
>>> n1 = noddy3.Noddy('jim', 'fulton', 42)
>>> n1 = noddy3.Noddy('jim', 'fulton', 42)
>>> n1.name()
'jim fulton'
>>> usuń n1.first
Traceback (most recent call last):
  File "<stdin>", line 1, w ?
TypeError: Cannot delete the first attribute
>>> n1.first = 42
Traceback (most recent call last):
  File "<stdin>", line 1, w ?
TypeError: The first attribute value must be a string
>>> n1.first = 'will'
>>> n1.name()
'will fulton'
>>> n2 = noddy3.Noddy()
>>> n2 = noddy3.Noddy()
>>> n2 = noddy3.Noddy()
>>> n3 = noddy3.Noddy('jim', 'fulton', 'waaa')
Traceback (most recent call last):
  File "<stdin>", line 1, w ?
TypeError: an integer jest required
>>> usuń n1
>>> usuń n2

Noddy 4

>>> zaimportuj noddy4
>>> n1 = noddy4.Noddy('jim', 'fulton', 42)
>>> n1.first
'jim'
>>> n1.last
'fulton'
>>> n1.number
42
>>> n1.name()
'jim fulton'
>>> n1.first = 'will'
>>> n1.name()
'will fulton'
>>> n1.last = 'tell'
>>> n1.name()
'will tell'
>>> usuń n1.first
>>> n1.name()
Traceback (most recent call last):
...
AttributeError: first
>>> n1.first
Traceback (most recent call last):
...
AttributeError: first
>>> n1.first = 'drew'
>>> n1.first
'drew'
>>> usuń n1.number
Traceback (most recent call last):
...
TypeError: can't delete numeric/char attribute
>>> n1.number=2
>>> n1.number
2
>>> n1.first = 42
>>> n1.name()
'42 tell'
>>> n2 = noddy4.Noddy()
>>> n2 = noddy4.Noddy()
>>> n2 = noddy4.Noddy()
>>> n2 = noddy4.Noddy()
>>> n2.name()
' '
>>> n2.first
''
>>> n2.last
''
>>> usuń n2.first
>>> n2.first
Traceback (most recent call last):
...
AttributeError: first
>>> n2.first
Traceback (most recent call last):
...
AttributeError: first
>>> n2.name()
Traceback (most recent call last):
  File "<stdin>", line 1, w ?
AttributeError: first
>>> n2.number
0
>>> n3 = noddy4.Noddy('jim', 'fulton', 'waaa')
Traceback (most recent call last):
  File "<stdin>", line 1, w ?
TypeError: an integer jest required


Test cyclic gc(?)

>>> zaimportuj gc
>>> gc.disable()

>>> x = []
>>> l = [x]
>>> n2.first = l
>>> n2.first
[[]]
>>> l.append(n2)
>>> usuń l
>>> usuń n1
>>> usuń n2
>>> sys.getrefcount(x)
3
>>> ignore = gc.collect()
>>> sys.getrefcount(x)
2

>>> gc.enable()
"""

zaimportuj os
zaimportuj sys
z distutils.util zaimportuj get_platform
PLAT_SPEC = "%s-%s" % (get_platform(), sys.version[0:3])
src = os.path.join("build", "lib.%s" % PLAT_SPEC)
sys.path.append(src)

jeżeli __name__ == "__main__":
    zaimportuj doctest, __main__
    doctest.testmod(__main__)
