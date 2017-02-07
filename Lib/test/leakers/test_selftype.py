# Reference cycles involving only the ob_type field are rather uncommon
# but possible.  Inspired by SF bug 1469629.

zaimportuj gc

def leak():
    klasa T(type):
        dalej
    klasa U(type, metaclass=T):
        dalej
    U.__class__ = U
    usuń U
    gc.collect(); gc.collect(); gc.collect()
