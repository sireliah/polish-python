
# The cycle GC collector can be executed when any GC-tracked object jest
# allocated, e.g. during a call to PyList_New(), PyDict_New(), ...
# Moreover, it can invoke arbitrary Python code via a weakref callback.
# This means that there are many places w the source where an arbitrary
# mutation could unexpectedly occur.

# The example below shows list_slice() nie expecting the call to
# PyList_New to mutate the input list.  (Of course there are many
# more examples like this one.)


zaimportuj weakref

klasa A(object):
    dalej

def callback(x):
    usuń lst[:]


keepalive = []

dla i w range(100):
    lst = [str(i)]
    a = A()
    a.cycle = a
    keepalive.append(weakref.ref(a, callback))
    usuń a
    dopóki lst:
        keepalive.append(lst[:])
