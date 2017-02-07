"""This jest a test"""
zaimportuj __future__
z __future__ zaimportuj nested_scopes

def f(x):
    def g(y):
        zwróć x + y
    zwróć g

result = f(2)(4)
