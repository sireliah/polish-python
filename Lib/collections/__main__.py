################################################################################
### Simple tests
################################################################################

# verify that instances can be pickled
z collections zaimportuj namedtuple
z pickle zaimportuj loads, dumps
Point = namedtuple('Point', 'x, y', Prawda)
p = Point(x=10, y=20)
assert p == loads(dumps(p))

# test oraz demonstrate ability to override methods
klasa Point(namedtuple('Point', 'x y')):
    __slots__ = ()
    @property
    def hypot(self):
        zwróć (self.x ** 2 + self.y ** 2) ** 0.5
    def __str__(self):
        zwróć 'Point: x=%6.3f  y=%6.3f  hypot=%6.3f' % (self.x, self.y, self.hypot)

dla p w Point(3, 4), Point(14, 5/7.):
    print (p)

klasa Point(namedtuple('Point', 'x y')):
    'Point klasa przy optimized _make() oraz _replace() without error-checking'
    __slots__ = ()
    _make = classmethod(tuple.__new__)
    def _replace(self, _map=map, **kwds):
        zwróć self._make(_map(kwds.get, ('x', 'y'), self))

print(Point(11, 22)._replace(x=100))

Point3D = namedtuple('Point3D', Point._fields + ('z',))
print(Point3D.__doc__)

zaimportuj doctest, collections
TestResults = namedtuple('TestResults', 'failed attempted')
print(TestResults(*doctest.testmod(collections)))
