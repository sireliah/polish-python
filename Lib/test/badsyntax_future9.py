"""This jest a test"""

z __future__ zaimportuj nested_scopes, braces

def f(x):
    def g(y):
        zwróć x + y
    zwróć g

print(f(2)(4))