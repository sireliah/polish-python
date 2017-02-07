"""Test cases dla test_pyclbr.py"""

def f(): dalej

klasa Other(object):
    @classmethod
    def foo(c): dalej

    def om(self): dalej

klasa B (object):
    def bm(self): dalej

klasa C (B):
    foo = Other().foo
    om = Other.om

    d = 10

    # XXX: This causes test_pyclbr.py to fail, but only because the
    #      introspection-based is_method() code w the test can't
    #      distinguish between this oraz a genuine method function like m().
    #      The pyclbr.py module gets this right jako it parses the text.
    #
    #f = f

    def m(self): dalej

    @staticmethod
    def sm(self): dalej

    @classmethod
    def cm(self): dalej
