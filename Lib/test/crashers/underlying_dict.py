zaimportuj gc

thingy = object()
klasa A(object):
    def f(self):
        zwróć 1
    x = thingy

r = gc.get_referrers(thingy)
jeżeli "__module__" w r[0]:
    dct = r[0]
inaczej:
    dct = r[1]

a = A()
dla i w range(10):
    a.f()
dct["f"] = lambda self: 2

print(a.f()) # should print 1
