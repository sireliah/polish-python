# line 1
'A module docstring.'

zaimportuj sys, inspect
# line 5

# line 7
def spam(a, b, c, d=3, e=4, f=5, *g, **h):
    eggs(b + d, c + f)

# line 11
def eggs(x, y):
    "A docstring."
    global fr, st
    fr = inspect.currentframe()
    st = inspect.stack()
    p = x
    q = y / 0

# line 20
klasa StupidGit:
    """A longer,

    indented

    docstring."""
# line 27

    def abuse(self, a, b, c):
        """Another

\tdocstring

        containing

\ttabs
\t
        """
        self.argue(a, b, c)
# line 40
    def argue(self, a, b, c):
        spróbuj:
            spam(a, b, c)
        wyjąwszy:
            self.ex = sys.exc_info()
            self.tr = inspect.trace()

    def contradiction(self):
        'The automatic gainsaying.'
        dalej

# line 48
klasa MalodorousPervert(StupidGit):
    def abuse(self, a, b, c):
        dalej
    def contradiction(self):
        dalej

Tit = MalodorousPervert

klasa ParrotDroppings:
    dalej

klasa FesteringGob(MalodorousPervert, ParrotDroppings):
    def abuse(self, a, b, c):
        dalej
    def contradiction(self):
        dalej

async def lobbest(grenade):
    dalej
