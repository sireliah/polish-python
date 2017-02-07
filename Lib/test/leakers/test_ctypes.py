
# Taken z Lib/ctypes/test/test_keeprefs.py, PointerToStructure.test().

z ctypes zaimportuj Structure, c_int, POINTER
zaimportuj gc

def leak_inner():
    klasa POINT(Structure):
        _fields_ = [("x", c_int)]
    klasa RECT(Structure):
        _fields_ = [("a", POINTER(POINT))]

def leak():
    leak_inner()
    gc.collect()
