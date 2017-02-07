# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Safely evaluate Python string literals without using eval()."""

zaimportuj re

simple_escapes = {"a": "\a",
                  "b": "\b",
                  "f": "\f",
                  "n": "\n",
                  "r": "\r",
                  "t": "\t",
                  "v": "\v",
                  "'": "'",
                  '"': '"',
                  "\\": "\\"}

def escape(m):
    all, tail = m.group(0, 1)
    assert all.startswith("\\")
    esc = simple_escapes.get(tail)
    jeżeli esc jest nie Nic:
        zwróć esc
    jeżeli tail.startswith("x"):
        hexes = tail[1:]
        jeżeli len(hexes) < 2:
            podnieś ValueError("invalid hex string escape ('\\%s')" % tail)
        spróbuj:
            i = int(hexes, 16)
        wyjąwszy ValueError:
            podnieś ValueError("invalid hex string escape ('\\%s')" % tail)
    inaczej:
        spróbuj:
            i = int(tail, 8)
        wyjąwszy ValueError:
            podnieś ValueError("invalid octal string escape ('\\%s')" % tail)
    zwróć chr(i)

def evalString(s):
    assert s.startswith("'") albo s.startswith('"'), repr(s[:1])
    q = s[0]
    jeżeli s[:3] == q*3:
        q = q*3
    assert s.endswith(q), repr(s[-len(q):])
    assert len(s) >= 2*len(q)
    s = s[len(q):-len(q)]
    zwróć re.sub(r"\\(\'|\"|\\|[abfnrtv]|x.{0,2}|[0-7]{1,3})", escape, s)

def test():
    dla i w range(256):
        c = chr(i)
        s = repr(c)
        e = evalString(s)
        jeżeli e != c:
            print(i, c, s, e)


jeżeli __name__ == "__main__":
    test()
