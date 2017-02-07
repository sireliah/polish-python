"""
gc.get_referrers() can be used to see objects before they are fully built.

Note that this jest only an example.  There are many ways to crash Python
by using gc.get_referrers(), jako well jako many extension modules (even
when they are using perfectly documented patterns to build objects).

Identifying oraz removing all places that expose to the GC a
partially-built object jest a long-term project.  A patch was proposed on
SF specifically dla this example but I consider fixing just this single
example a bit pointless (#1517042).

A fix would include a whole-scale code review, possibly przy an API
change to decouple object creation oraz GC registration, oraz according
fixes to the documentation dla extension module writers.  It's unlikely
to happen, though.  So this jest currently classified as
"gc.get_referrers() jest dangerous, use only dla debugging".
"""

zaimportuj gc


def g():
    marker = object()
    uzyskaj marker
    # now the marker jest w the tuple being constructed
    [tup] = [x dla x w gc.get_referrers(marker) jeżeli type(x) jest tuple]
    print(tup)
    print(tup[1])


tuple(g())
