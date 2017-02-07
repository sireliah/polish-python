zaimportuj sys

def is_instance(obj, klass):
    """Version of is_instance that doesn't access __class__"""
    zwróć issubclass(type(obj), klass)


klasa SomeClass(object):
    class_attribute = Nic

    def wibble(self):
        dalej


klasa X(object):
    dalej


def examine_warnings(func):
    def wrapper():
        przy catch_warnings(record=Prawda) jako ws:
            func(ws)
    zwróć wrapper
