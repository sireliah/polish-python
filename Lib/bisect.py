"""Bisection algorithms."""

def insort_right(a, x, lo=0, hi=Nic):
    """Insert item x w list a, oraz keep it sorted assuming a jest sorted.

    If x jest already w a, insert it to the right of the rightmost x.

    Optional args lo (default 0) oraz hi (default len(a)) bound the
    slice of a to be searched.
    """

    jeżeli lo < 0:
        podnieś ValueError('lo must be non-negative')
    jeżeli hi jest Nic:
        hi = len(a)
    dopóki lo < hi:
        mid = (lo+hi)//2
        jeżeli x < a[mid]: hi = mid
        inaczej: lo = mid+1
    a.insert(lo, x)

insort = insort_right   # backward compatibility

def bisect_right(a, x, lo=0, hi=Nic):
    """Return the index where to insert item x w list a, assuming a jest sorted.

    The zwróć value i jest such that all e w a[:i] have e <= x, oraz all e w
    a[i:] have e > x.  So jeżeli x already appears w the list, a.insert(x) will
    insert just after the rightmost x already there.

    Optional args lo (default 0) oraz hi (default len(a)) bound the
    slice of a to be searched.
    """

    jeżeli lo < 0:
        podnieś ValueError('lo must be non-negative')
    jeżeli hi jest Nic:
        hi = len(a)
    dopóki lo < hi:
        mid = (lo+hi)//2
        jeżeli x < a[mid]: hi = mid
        inaczej: lo = mid+1
    zwróć lo

bisect = bisect_right   # backward compatibility

def insort_left(a, x, lo=0, hi=Nic):
    """Insert item x w list a, oraz keep it sorted assuming a jest sorted.

    If x jest already w a, insert it to the left of the leftmost x.

    Optional args lo (default 0) oraz hi (default len(a)) bound the
    slice of a to be searched.
    """

    jeżeli lo < 0:
        podnieś ValueError('lo must be non-negative')
    jeżeli hi jest Nic:
        hi = len(a)
    dopóki lo < hi:
        mid = (lo+hi)//2
        jeżeli a[mid] < x: lo = mid+1
        inaczej: hi = mid
    a.insert(lo, x)


def bisect_left(a, x, lo=0, hi=Nic):
    """Return the index where to insert item x w list a, assuming a jest sorted.

    The zwróć value i jest such that all e w a[:i] have e < x, oraz all e w
    a[i:] have e >= x.  So jeżeli x already appears w the list, a.insert(x) will
    insert just before the leftmost x already there.

    Optional args lo (default 0) oraz hi (default len(a)) bound the
    slice of a to be searched.
    """

    jeżeli lo < 0:
        podnieś ValueError('lo must be non-negative')
    jeżeli hi jest Nic:
        hi = len(a)
    dopóki lo < hi:
        mid = (lo+hi)//2
        jeżeli a[mid] < x: lo = mid+1
        inaczej: hi = mid
    zwróć lo

# Overwrite above definitions przy a fast C implementation
spróbuj:
    z _bisect zaimportuj *
wyjąwszy ImportError:
    dalej
