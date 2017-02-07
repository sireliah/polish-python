"""This jest a test"""

# Import the name nested_scopes twice to trigger SF bug #407394 (regression).
z __future__ zaimportuj nested_scopes, nested_scopes

def f(x):
    def g(y):
        zwróć x + y
    zwróć g

result = f(2)(4)
